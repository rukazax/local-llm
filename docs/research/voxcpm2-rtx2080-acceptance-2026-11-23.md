# Приёмка VoxCPM2 на RTX 2080 Max-Q (8 ГБ)

**RU** · [English](#english)

Дата: 23.11.2026. Стенд: Windows-бокс `192.168.88.20` (RTX 2080 Max-Q, 8 ГБ, драйвер из
поставки, Python 3.10.11, torch 2.5.1+cu124). Модель: `openbmb/VoxCPM2` (2B), локальная копия
весов 4,7 ГБ, `dtype` в `config.json` переключён `bfloat16 → float16` (у SM75 нет bf16).
Скрипт замера: [`voxcpm2-rtx2080-test-2026-11-23.py`](voxcpm2-rtx2080-test-2026-11-23.py).

Задача была простая: единственная модель речи, которая до сих пор стояла в плане «на веру» —
основной голос озвучки. Проверить, влезает ли она в 8 ГБ и с какой скоростью говорит.

## Что получилось

| Метрика | Значение | Комментарий |
|---|---|---|
| Загрузка модели | 28,2 с | safetensors 4,58 ГБ + AudioVAE |
| VRAM после загрузки | 5 064 МБ | XTTS на `:8765` держал ещё ~2,7 ГБ — вдвоём впритык |
| VRAM пиковая | 5 460 МБ | из 8 192 МБ; запас есть, но третий движок уже не влезет |
| Выход | 48 кГц, моно, s16le | как в карточке, вопросов нет |
| **RTF** | **17,2–20,6**, медиана **18,8** | на 2080 Max-Q, fp16, `inference_timesteps=10` |
| WER (GigaAM int8) | 8,6 % — 8 ошибок на 93 слова | из них настоящих дефектов модели — один |
| Громкость | −15,6 … −30,4 dB mean | разброс большой, нормализовать обязательно |
| Voice Design (RU) | **не работает** | «женский» вышел 107 Гц, «низкий мужской» — 150 Гц |
| Voice Design (EN) | работает | «dry female narrator» — 222 Гц, «low male» — 136 Гц |

Числа по каждой фразе (12 прогонов, из них 3 с русским описанием голоса и 2 с английским):

| # | Фраза | Знаков | Синтез, с | Аудио, с | RTF |
|---|---|---|---|---|---|
| 0 | диалог с ремаркой | 69 | 85,6 | 4,16 | 20,6 |
| 1 | вопрос с именем | 24 | 19,4 | 1,12 | 17,3 |
| 2 | восклицание | 22 | 24,8 | 1,44 | 17,2 |
| 3 | системная строка | 45 | 42,5 | 2,24 | 19,0 |
| 4 | числа 21 и 42 | 42 | 63,3 | 3,36 | 18,8 |
| 5 | брань автора | 26 | 29,2 | 1,60 | 18,2 |
| 6 | шёпот | 27 | 42,1 | 2,24 | 18,8 |
| 7 | сухо, дикторски | 36 | 48,4 | 2,56 | 18,9 |
| 8 | бытовая проза | 50 | 60,1 | 3,20 | 18,8 |
| D1 | описание по-русски, «сухой женский» | — | 94,3 | 5,12 | 18,4 |
| D2 | описание по-русски, «низкий мужской» | — | 110,6 | 5,92 | 18,7 |
| D3 | описание по-русски, «взволнованный» | — | 92,1 | 4,80 | 19,2 |

## Три вещи, которые важнее самих цифр

**1. Скорость делает модель непригодной для рендера тома.** RTF 18,8 значит: час аудио
считается 19 часов. Десятичасовой том — восемь суток на одной карте. Для сравнения, TeraTTSv2
на CPU этого же NAS даёт RTF 0,47, то есть **в 40 раз быстрее на железе, которое вдвое дешевле**.
VoxCPM2 остаётся моделью для образцов, трейлеров и проб Voice Design, но не для озвучки книги.

**2. Числа читаются по-английски.** На фразе «В отсеке осталось 21 ящик и 42 контейнера»
распознавание слышит «твенти ван ящик и форти ту контейнера» — при `normalize=True`. Это не
ошибка распознавателя: русское «двадцать один» так не переврать. Значит, перед синтезом нужен
свой разворачиватель чисел (RUAccent умеет, либо простой числительный конвертер), иначе в
озвучке будут английские числительные.

**3. Voice Design понимает английский, но не русский.** Три русских описания дали три разных
тембра, но не те, что просили: «сухой женский дикторский» — 107 Гц (это мужской регистр),
«спокойный низкий мужской» — 150 Гц (выше «женского»). Английские описания попали в цель с
первого раза: «a dry female narrator» — 222 Гц, «a calm low male voice» — 136 Гц. Практический
вывод: описания голоса писать по-английски, а русский текст — только в реплике.

Для калибровки: медиана основного тона у русских дикторов-мужчин ~110–130 Гц, у женщин
~190–220 Гц; замер грубый (автокорреляция по 40-мс окнам, порог 0,35), поэтому важны не
абсолютные герцы, а порядок: 107 против 222 — это разные голоса, а не погрешность.

## Чего этот замер не доказывает

- **Скорость на V100 не измерена.** SM70 с честным fp16 и втрое большей памятью даст другой RTF,
  но насколько — из этого замера не следует. Карта 2080 Max-Q к тому же мобильная и греется.
- **Качество тембра не оценено.** SIM 81,1 из карточки мы не проверяли: для этого нужен эталонный
  диктор и метрика сходства, а не WER.
- **Причины RTF 18,8 не разобраны.** 2,8–3,0 с на шаг генерации при 10 шагах диффузии — это
  подозрительно много даже для мобильной 2080; возможно, дело в сборке (transformers 5.20.2 при
  torch 2.5.1 сам пишет «PyTorch was not found» и отключает часть интеграций). Прежде чем винить
  архитектуру, стоит перепроверить на чистом окружении с `transformers==4.57.x`.
- **Один WER — не приговор.** 93 слова — мало; цифра годится, чтобы отличить «читает» от
  «не читает», а не чтобы сравнивать модели в десятых долях процента.

## Как ставили (чтобы повторить)

1. `venv` на Python **3.10** (не 3.13: пакету нужен 3.10–3.12).
2. `pip install --index-url https://download.pytorch.org/whl/cu124 torch==2.5.1+cu124` с бокса
   отвечает `Could not find a version that satisfies the requirement` — cu124-индекс с этой
   машины не резолвится. Обошли переиспользованием готового окружения: скопировали `venv_f5`
   (там уже torch 2.5.1+cu124) в `venv-voxcpm`, дальше `pip install voxcpm` видит torch
   установленным и не тянет второй.
3. Веса качали не на боксе (HF оттуда недоступен, `read operation timed out`), а на NAS:
   `hf download openbmb/VoxCPM2` в `/srv/apps/models/voxcpm2`, затем раздача
   `python3 -m http.server 8099` и `curl` с бокса по LAN. 4,58 ГБ шли ~13 минут, размер после
   сверен побайтово с источником.
4. `dtype` в `config.json` заменён на `float16` (копия исходника рядом: `config.json-hf-bf16`).

## Файлы

- Скрипт: [`voxcpm2-rtx2080-test-2026-11-23.py`](voxcpm2-rtx2080-test-2026-11-23.py)
- Аудио: `/tmp/voxout` на NAS (12 wav, 48 кГц) — временно, для прослушивания
- Сравнение с TeraTTSv2: [teratts-cpu-acceptance-2026-11-23](teratts-cpu-acceptance-2026-11-23.md)

---

## English

Date: 23 Nov 2026. Rig: the Windows box at `192.168.88.20` (RTX 2080 Max-Q, 8 GB, Python 3.10.11,
torch 2.5.1+cu124). Model: `openbmb/VoxCPM2` (2B), local 4.7 GB copy, `dtype` switched from
`bfloat16` to `float16` in `config.json` (SM75 has no bf16).

| Metric | Value |
|---|---|
| Model load | 28.2 s |
| VRAM after load | 5,064 MB (XTTS on `:8765` held another ~2.7 GB — tight together) |
| Peak VRAM | 5,460 MB of 8,192 MB |
| Output | 48 kHz, mono, s16le |
| **RTF** | **17.2–20.6**, median **18.8** (fp16, 10 inference steps) |
| WER (GigaAM int8) | 8.6 % — 8 errors in 93 words; one genuine model defect |
| Loudness | −15.6 … −30.4 dB mean — normalise before delivery |
| Voice Design (Russian) | **does not work**: "female" came out at 107 Hz, "low male" at 150 Hz |
| Voice Design (English) | works: "dry female narrator" 222 Hz, "low male" 136 Hz |

Three findings that matter more than the table:

1. **Throughput rules it out for book rendering.** RTF 18.8 means one hour of audio takes 19 hours;
   a ten-hour volume is eight days on one card. TeraTTSv2 on the NAS CPU runs at RTF 0.47 —
   forty times faster on cheaper hardware. VoxCPM2 stays a model for samples, trailers and Voice
   Design probes, not for a full audiobook.
2. **Digits are read in English.** "21 ящик и 42 контейнера" was recognised as "твенти ван … форти
   ту" with `normalize=True`. A Russian numeral expander is required before synthesis.
3. **Voice Design follows English descriptions only.** Russian prompts produced three different
   timbres but not the requested ones; English prompts hit the target first try.

Not proven by this run: V100 throughput, timbre similarity (card figure SIM 81.1 untested), the root
cause of the 18.8 RTF (transformers 5.20.2 with torch 2.5.1 disables part of its PyTorch
integration — retest on `transformers==4.57.x` before blaming the architecture), and WER stability
on a 93-word sample.

#local-llm #tts #voxcpm2 #rtx2080 #v100 #audio-books
