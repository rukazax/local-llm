# Приёмка VoxCPM2 на RTX 2080 Max-Q (8 ГБ)

**RU** · [English](#english)

Дата: 23.11.2026. Стенд: Windows-бокс `192.168.88.20` (RTX 2080 Max-Q, 8 ГБ, Python 3.10.11,
**torch 2.6.0+cu124**, transformers 5.20.2, `transformers.is_torch_available() == True`). Модель:
`openbmb/VoxCPM2` (2B), локальная копия весов 4,7 ГБ, `dtype` в `config.json` переключён
`bfloat16 → float16` (у SM75 нет bf16). Карта перед замером пустая: `nvidia-smi` → 0 МиБ.
Скрипт замера: [`voxcpm2-rtx2080-test-2026-11-23.py`](voxcpm2-rtx2080-test-2026-11-23.py).

> **Первая версия этого отчёта врала, и не по мелочи.** Утром 23.11 здесь стоял RTF 18,8 и вывод
> «для рендера тома не годится». Оба утверждения — артефакт стенда, а не свойство модели. Ниже
> разобрано, что именно было сломано; цифры в таблицах — только после починки.

## Две ошибки окружения, из-за которых первый замер ничего не значил

**1. transformers отказался от PyTorch.** Стояли torch 2.5.1+cu124 и transformers 5.20.2, а
библиотека с версии 5 требует torch ≥ 2.6. При живом `torch.cuda.is_available() == True` она
писала в лог:

```
[transformers] Disabling PyTorch because PyTorch >= 2.6 is required but found 2.5.1+cu124
[transformers] PyTorch was not found.
```

То есть движок работал с наполовину отключённой интеграцией. Лечится одной командой:
`pip install torch==2.6.0+cu124 torchaudio==2.6.0+cu124` (для cp310 на cu124 в индексе PyTorch
есть ровно 2.6.0). Критерий починки — строка `Disabling PyTorch` исчезла, а
`transformers.is_torch_available()` отвечает `True`. Скрипт замера теперь падает с кодом 2, если
это не так: молчаливый деградированный прогон больше не пройдёт.

**2. Карта была занята чужим движком.** XTTS на `:8765` держал 2 759 МиБ из 8 192. С моделью
получалось 7 982 МиБ — 97 % памяти, и Windows начинал вытеснять в общую память. Отсюда
«0,35 токена в секунду» и 100 % утилизации при 1 830 МГц: карта не простаивала, она тонула.
На пустой карте тот же шаг идёт **0,33 с вместо 2,9 с** — в девять раз быстрее.

Побочно это опровергает и промежуточный вывод прошлой версии («узкое место не диффузия»):
на починенном стенде `inference_timesteps` снова влияет, 4 шага против 10 дают ровно те же ~2×.

## Что получилось

| Метрика | Значение | Комментарий |
|---|---|---|
| Загрузка модели | 16,3 с | против 28,2 с на сломанном окружении |
| VRAM после загрузки | 5 064 МБ | карта пустая, никто не мешает |
| VRAM пиковая | 5 456 МБ | из 8 192 МБ — запас 2,7 ГБ, влезает с головой |
| Выход | 48 кГц, моно, s16le | как в карточке |
| **RTF** | **2,12–3,87**, медиана **2,20** | fp16, `inference_timesteps=10` |
| RTF при 4 шагах | **1,16–1,28** | вдвое быстрее, но см. дефект ниже |
| WER (GigaAM int8) | 16,9 % — 10 ошибок на 59 слов | 7 из них — одна фраза с числами |
| Voice Design (RU) | **не работает** | «женский» 107 Гц, «низкий мужской» 150 Гц |
| Voice Design (EN) | работает | «dry female narrator» 222 Гц, «low male» 136 Гц |

Числа по каждой фразе (9 прогонов, `inference_timesteps=10`):

| # | Фраза | Знаков | Синтез, с | Аудио, с | RTF |
|---|---|---|---|---|---|
| 0 | диалог с ремаркой | 69 | 22,93 | 5,92 | 3,87 |
| 1 | вопрос с именем | 24 | 2,46 | 1,12 | 2,20 |
| 2 | восклицание | 22 | 3,12 | 1,44 | 2,17 |
| 3 | системная строка | 45 | 6,11 | 2,88 | 2,12 |
| 4 | числа 21 и 42 | 42 | 11,33 | 4,48 | 2,53 |
| 5 | брань автора | 26 | 3,42 | 1,60 | 2,14 |
| 6 | шёпот | 27 | 5,16 | 1,92 | 2,69 |
| 7 | сухо, дикторски | 36 | 6,46 | 2,40 | 2,69 |
| 8 | бытовая проза | 50 | 7,58 | 3,52 | 2,15 |

Первый прогон (3,87) — прогрев ядер, в медиану его не берём. Остальные восемь укладываются в
2,12–2,69, разброс от длины фразы и от того, сколько кадров модель решила потратить на паузы.

Шаги против качества — одни и те же три фразы:

| Фраза | 4 шага: синтез / аудио / RTF | 10 шагов: синтез / аудио / RTF |
|---|---|---|
| диалог | 4,19 / 3,52 / 1,192 | 13,30 / 5,60 / 2,375 |
| вопрос | 2,05 / 1,76 / 1,163 | 2,89 / 1,28 / 2,257 |
| восклицание | 2,25 / 1,76 / 1,277 | 2,81 / 1,28 / 2,197 |

На диалоге 4 шага выдали 3,52 с вместо 5,60 — и распознавание слышит обрубленный хвост:
«…положил ладонь на **паруч**» вместо «на поручень». Экономия вдвое, но за счёт конца фразы;
для рендера тома это недопустимо, для чернового прослушивания — годится.

## Что это меняет в решении

RTF 2,2 значит: час аудио считается 2 часа 12 минут. Том этой серии (600 тыс. знаков ≈ 14 ч
аудио) — **≈ 31 час** на одной карте; при 4 шагах ≈ 17 ч, но с обрубленными хвостами. Формально
VoxCPM2 том уже тянет — в отличие от «восьми суток» из прошлой версии отчёта.

Но TeraTTSv2 на CPU этого же NAS даёт RTF 0,47, то есть **в 4,7 раза быстрее** и на железе,
которое не занимает карту. Поэтому расклад такой:

- **базовый движок томов — TeraTTSv2** (RTF 0,47, WER 1,8 %, 44,1 кГц, ударения автоматом);
- **VoxCPM2 — кандидат на образцы, трейлеры и 48-кГц тембр**: там счёт идёт на минуты и десятки
  минут аудио, где множитель 2,2 неважен, а качество и голосовой дизайн важнее;
- перепроверка на V100 остаётся: SM70 с честным fp16 и втрое большей памятью может дать другой
  RTF, но из этого замера это не следует.

## Два дефекта, которые от окружения не зависят

**1. Числа читаются по-английски.** Фраза «В отсеке осталось 21 ящик и 42 контейнера» после
починки окружения по-прежнему распознаётся как «отсекиосталось **твентиван** ящик и **форти ту**
контейнера» — при `normalize=True`. Русское «двадцать один» так не переврать, значит это модель,
а не распознаватель. Нужен свой разворачиватель чисел перед синтезом. TeraTTSv2 уже делает это
через `num2words` — переиспользовать, а не писать третий.

**2. Voice Design понимает только английские описания.** Три русских описания дали три разных
тембра, но не те: «сухой женский дикторский» — 107 Гц (мужской регистр), «спокойный низкий
мужской» — 150 Гц. Английские попали с первого раза: «a dry female narrator» — 222 Гц,
«a calm low male voice» — 136 Гц. Практический вывод: описания голоса писать по-английски,
русский — только в реплике.

Для калибровки: медиана основного тона у русских дикторов-мужчин ~110–130 Гц, у женщин
~190–220 Гц; замер грубый (автокорреляция по 40-мс окнам, порог 0,35), поэтому важны не
абсолютные герцы, а порядок: 107 против 222 — это разные голоса, а не погрешность.

## Где модель ошибается по тексту

Шесть фраз из девяти распознаны в ноль ошибок. Остальное:

| Фраза | Что услышали | Вердикт |
|---|---|---|
| числа 21 и 42 | твентиван / форти ту | дефект модели, лечится разворачивателем |
| «сканирование» | «сканирования» | окончание; модель или распознаватель — нужна прослушка |
| «ёшкин кот» | «ошкин кодт» | «ё» под вопросом: других слов с «ё» в наборе нет |

Без фразы с числами WER выходит 6,1 % (3 ошибки на 49 слов), с ней — 16,9 %. Это и есть цена
одного непокрытого класса: числительные встречаются в тексте часто.

## Чего этот замер не доказывает

- **Скорость на V100 не измерена.** SM70 с честным fp16 и втрое большей памятью даст другой RTF,
  но насколько — из этого замера не следует. 2080 Max-Q к тому же мобильная и греется.
- **Качество тембра не оценено.** SIM 81,1 из карточки мы не проверяли: для этого нужен эталонный
  диктор и метрика сходства, а не WER.
- **Один WER — не приговор.** 59 слов мало; цифра отделяет «читает» от «не читает», а не
  сравнивает модели в десятых долях процента.
- **Одновременная работа с XTTS не проверена как сценарий.** RTF 2,2 получен на пустой карте;
  если рядом держать XTTS (2,7 ГБ), синтез замедлится в разы — на этом и погорел первый замер.
  Для рендера тома VoxCPM2 держать одного.

## Как повторить

1. `venv` на Python **3.10** (пакету нужен 3.10–3.12).
2. **torch строго ≥ 2.6** под transformers 5.x:
   `pip install torch==2.6.0+cu124 torchaudio==2.6.0+cu124`. Колесо 2,53 ГБ с этого бокса не
   качается напрямую — качать на NAS и раздавать по HTTP (`python3 -m http.server`).
   Проверка до замера: `transformers.is_torch_available()` → `True`.
3. **Освободить карту.** Остановить XTTS и убедиться, что `nvidia-smi` показывает 0 МиБ, иначе
   получите RTF в девять раз хуже и не заметите. Сторож `shov-win-health.timer` на это время
   выключить, иначе он поднимет движок посреди замера (`rootdo systemctl stop
   shov-win-health.timer`, потом `start`).
4. Веса на бокс — не с HF (оттуда `read operation timed out`), а с NAS по LAN: `hf download
   openbmb/VoxCPM2` в `/srv/apps/models/voxcpm2`, раздача `http.server 8099`, `curl` с бокса;
   4,58 ГБ шли ~13 минут, размер сверен побайтово.
5. `dtype` в `config.json` → `float16` (копия исходника рядом: `config.json-hf-bf16`).

## Файлы

- Скрипт замера: [`voxcpm2-rtx2080-test-2026-11-23.py`](voxcpm2-rtx2080-test-2026-11-23.py)
  (в нём же preflight-гейт на `is_torch_available`)
- Аудио: `C:\tts\voxcpm-out26` на боксе (15 wav, 48 кГц) — временно
- Сравнение с TeraTTSv2: [teratts-cpu-acceptance-2026-11-23](teratts-cpu-acceptance-2026-11-23.md)

---

## English

Date: 23 Nov 2026. Rig: the Windows box at `192.168.88.20` (RTX 2080 Max-Q, 8 GB, Python 3.10.11,
**torch 2.6.0+cu124**, transformers 5.20.2, `transformers.is_torch_available() == True`). Model:
`openbmb/VoxCPM2` (2B), local 4.7 GB copy, `dtype` switched from `bfloat16` to `float16` in
`config.json` (SM75 has no bf16). The card was empty before the run: `nvidia-smi` → 0 MiB.

> **The first version of this report was wrong, and not by a little.** In the morning it carried
> RTF 18.8 and the verdict "unusable for volume rendering". Both were rig artefacts, not model
> properties. What follows are the numbers after the fix.

### Two rig errors that made the first run meaningless

1. **transformers refused PyTorch.** torch 2.5.1+cu124 with transformers 5.20.2: the library requires
   torch ≥ 2.6 since v5 and logged `Disabling PyTorch because PyTorch >= 2.6 is required` while
   `torch.cuda.is_available()` was `True`. Fixed with
   `pip install torch==2.6.0+cu124 torchaudio==2.6.0+cu124`; the test script now exits with code 2
   unless `transformers.is_torch_available()` is `True`, so a degraded run cannot pass silently.
2. **The card was already busy.** XTTS on `:8765` held 2,759 MB of 8,192; with the model it reached
   7,982 MB — 97 % — and Windows started spilling to shared memory. Hence "0.35 tokens/s" at 100 %
   utilisation and 1,830 MHz: the card was drowning, not idling. On an empty card the same step takes
   **0.33 s instead of 2.9 s**. This also refutes the earlier claim that diffusion steps do not
   matter: they do, 4 steps versus 10 give the expected ~2×.

### Results

| Metric | Value | Note |
|---|---|---|
| Model load | 16.3 s | 28.2 s on the broken rig |
| VRAM after load | 5,064 MB | card otherwise empty |
| Peak VRAM | 5,456 MB of 8,192 | 2.7 GB headroom |
| Output | 48 kHz, mono, s16le | as advertised |
| **RTF** | **2.12–3.87**, median **2.20** | fp16, 10 inference steps |
| RTF at 4 steps | **1.16–1.28** | twice as fast, see the tail defect |
| WER (GigaAM int8) | 16.9 % — 10 errors in 59 words | 7 of them in the digits phrase |
| Voice Design (Russian) | **does not work** | "female" 107 Hz, "low male" 150 Hz |
| Voice Design (English) | works | "dry female narrator" 222 Hz, "low male" 136 Hz |

| Phrase | Chars | Synth, s | Audio, s | RTF |
|---|---|---|---|---|
| dialogue with a stage direction | 69 | 22.93 | 5.92 | 3.87 |
| question with a name | 24 | 2.46 | 1.12 | 2.20 |
| exclamation | 22 | 3.12 | 1.44 | 2.17 |
| system line | 45 | 6.11 | 2.88 | 2.12 |
| digits 21 and 42 | 42 | 11.33 | 4.48 | 2.53 |
| profanity | 26 | 3.42 | 1.60 | 2.14 |
| whisper | 27 | 5.16 | 1.92 | 2.69 |
| dry narration | 36 | 6.46 | 2.40 | 2.69 |
| everyday prose | 50 | 7.58 | 3.52 | 2.15 |

The first run (3.87) is kernel warm-up and is excluded from the median. At 4 steps the dialogue
produced 3.52 s instead of 5.60 s and ASR hears a truncated tail ("на паруч" instead of "на
поручень"): half the cost, but a lost ending.

### What this changes

RTF 2.2 means one hour of audio takes 2 h 12 min of compute; a volume of this series (600k
characters ≈ 14 h of audio) is **≈ 31 hours** on one card. So VoxCPM2 *can* render a volume, unlike the "eight days" of the first report. But
TeraTTSv2 on the NAS CPU runs at RTF 0.47 — **4.7× faster** and without occupying a GPU. Therefore:

- **the base engine for volumes stays TeraTTSv2**;
- **VoxCPM2 is a candidate for samples, trailers and 48-kHz timbre**;
- the V100 re-test still stands: Volta may change the RTF, and this run cannot tell.

### Two defects that do not depend on the rig

1. **Digits are read in English.** "21 ящик и 42 контейнера" still comes back as "твентиван … форти
   ту" with `normalize=True`; a Russian numeral expander is required. TeraTTSv2 already does this
   with `num2words` — reuse it.
2. **Voice Design follows English descriptions only.** Russian prompts produced wrong registers
   (107 Hz for "female", 150 Hz for "low male"); English prompts hit the target first try.

Six of nine phrases transcribe with zero errors; without the digits phrase WER is 6.1 %
(3/49). "ёшкин кот" came out as "ошкин кодт" — the only word with "ё" in the set, needs listening.

Not proven by this run: V100 throughput, timbre similarity (SIM 81.1 untested), WER stability on
59 words, and running alongside XTTS — that is exactly what broke the first measurement, so a
VoxCPM2 volume render should own the card.

#local-llm #tts #voxcpm2 #rtx2080 #v100 #audio-books
