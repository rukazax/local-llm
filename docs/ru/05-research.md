# 05 · Исследования: находки и источники

**RU** · [English](../en/05-research.md) · [← README](../../README.md)

---

## Консолидированные находки (все ресёрчи, 19.11.2026)

### Железо и сборка

| Находка | Источник |
|---|---|
| Без полного NVLink — вдвое медленнее (57 против ~100 ток/с) | Simply Explained (видео), roksblog |
| 42 Вт на модуль в простое; лимит 250–300 Вт почти не теряет скорости; 150 Вт — минимум потерь | Angry Sysadmins, Level1Techs |
| Above 4G + ReBAR + UEFI — обязательны; bifurcation x8/x8 для одного слота | Angry Sysadmins |
| Пик 4 карт — 1350 Вт; СЖО 360×45 + 240×30; водоблок ~300 Вт/карту | Kiber Kuznitsa (видео), Хабр 1084234 |
| Прижим SXM2: винты до упора + 16 центральных на 2 оборота; ECC-счётчики после нагрузки | наша практика + форумные кейсы |
| Альтернативы: Fujitsu CX400M4 (обычно 4×16), Dell C4130/4140 — дешевле, но bespoke-охлаждение | Level1Techs |
| 6-модульных готовых плат нет; DIY-мосты между платами не доказаны | Level1Techs, pigeon-labs |

### Скорости (замеры на V100)

| Конфигурация | Результат |
|---|---|
| Qwen3.8-27B NVFP4 + DFlash2, 1Cat 1.5.4 TP4 4×32 | **1139 ток/с aggregate** @8K/8 потоков; 425 одиночный; 784 @8K/8×64K |
| Qwen3.8-27B GGUF Q4_K_M + MTP, 1×32 | 65 ток/с @1K → 42 @128K (сток: 35.95 → 16.49) |
| Qwen3.8-27B NVFP4, 1×32 | 29.3 ток/с — одиночная карта для NVFP4 не optimized-путь |
| Flash-Next IQ3E+MTP, 2×32 NVLink | 122 ток/с @256K контекста; tensor-split +20% к layer-split |
| Flash-Next (6×16GB, wangxso) | prefill 3402 ток/с @200K |
| DeepSeek V4.1 Flash 2-bit, 4×32 + оффлоад | 91 ток/с декод, 2100 ток/с prefill |
| DeepSeek V4.1 Flash 2-bit, 8×32 @150W | 131 ток/с (1Cat + pipeline-патч) |
| qwen3-coder:30b Q4, 2×V100 (ollama-форк) | 98.8 ток/с |
| Qwen3.8-27B + MTP флаг, consumer GPU | +33–39% декода (sudoingX) |
| KV q8_0 на Volta | ~2% к f16 — «ёмкость, не скорость» |
| 2×V100-16 без NVLink vs RTX 4090 | 50–52 против 90 ток/с (27B MTP, 131K) | 

### Экосистема Volta

- Драйвер **580.x — последний** для Volta; CUDA 13 Volta не поддерживает; ядра Linux новые —
  тестировать перед апгрейдом.
- Ollama выкинул Volta (форки в AUR), upstream vLLM требует CC ≥ 7.5, PyTorch свернул сборки 09.2026.
- 1Cat-vLLM v1.5.4 (21.11.2026): Flash-Next MTP5 + DCP2, стек KV в RAM, 425/1139 ток/с на 4×V100 — [гайд 08](08-1cat-vllm-nvfp4.md).
- 1Cat-LLM v1.5.3 (14.11.2026): 21k коммитов, GGUF-поддержка (переименование в 1Cat-LLM идёт),
  эталонный стенд расходует **62 ГБ host RAM**; Z-Image и MiniMax H3 уже работают на SM70.

### Uncensored-экосистема (научная работа IMC'26, 16k моделей)

- Refusal rate: ULLM **35.6%** против 77.4% у обычных; 62% моделей — комбинированные методы.
- Методы: файнтюн 16%, абляция 4.7% (чистая), мерджи 2%, сжатие 13.7%, комбинации 62.5%.
- **Heretic — доминирующий инструмент с ноября 2025** (24% новых ULLM); MergeKit — 94% мерджей,
  TIES — популярнейшая техника мерджа.
- Больше скачивания = ниже refusal rate: сообщество отбирает рабочие абляции.

### Модели: ключевые факты

- **Qwen3.8-27B** (08.2026, Apache 2.0): гибрид GDN (3 DeltaNet : 1 attention), MTP, нативное
  зрение, 256K; GPQA 89.2, LiveCodeBench v6 90.3 — «плотно к закрытым флагманам».
- **MiniMax M2.7** 230B/A10B, MIT: IQ1_M = 60.7 ГБ — агент-флагман, влезает в наши 128.
- **Hermes 4-70B** (Nous): SOTA RefusalBench, гибридный ризонинг, tool calling.
- **AliceAI-Foundation-80B-A3B** (Yandex, Apache 2.0): сильный русский (WikiWebFacts 86.5).
- **Nemotron 3.5 Bolt 74B-A9B**: GPQA 88.83; «24GB IQ2» билд — 86.43.
- **DeepSeek V4 Flash abliterated**: 154 ГБ Q4 — вне досягаемости (нужно 192 ГБ).
- Аbliteration почти не стоит скорости (62.0 против 62.1 ток/с — замер kextcache).

## Все источники

**RU:** Хабр [«сервер для LLM дешевле RTX 3090»](https://habr.com/ru/articles/1084234/),
[«одна Tesla V100 32 ГБ»](https://habr.com/ru/articles/1093584/),
[«Лаборатория ИИ за 200 000 ₽»](https://habr.com/ru/articles/1041610/),
[«Vibecode по дешевке»](https://habr.com/ru/articles/1049052/),
[«V100 16Gb в корпусе от RTX 4090»](https://habr.com/ru/articles/1039198/).

**EN/форумы:** [Angry Sysadmins](https://angrysysadmins.tech/2026/03/grassyloki/cheapish-ai-homelab-on-a-budget-v100s-custom-boards-and-nvlink/),
[Level1Techs DIY backplane](https://forum.level1techs.com/t/designing-an-open-source-budget-4x-v100-sxm2-nvlink-backplane-passive-pcie-vs-pex8749/250801?page=2),
[roksblog: 2×V100 vs RTX 4090](https://www.roksblog.de/can-two-old-tesla-v100s-beat-an-rtx-4090-for-a-fully-local-hermes-agent/),
[llamaperf V100-32GB](https://llamaperf.com/gpu/v100-32gb),
[vramcalculator: флаги llama.cpp](https://vramcalculator.com/llama-cpp-performance-flags/),
[bswen: оптимизация llama.cpp](https://docs.bswen.com/blog/2026-03-15-llamacpp-optimization-speed/),
[carteakey: локальная оптимизация](https://carteakey.dev/blog/local-inference/local-llm-optimization/).

**Форки/движки:** [1Cat-LLM](https://github.com/1CatAI/1Cat-vLLM),
[anyei/llamacpp-v100](https://github.com/anyei/llamacpp-v100),
[wangxso/llama.cpp-v100](https://github.com/wangxso/llama.cpp-v100),
[jusko-llama-volta-qwen3flash](https://github.com/jackjusko/jusko-llama-volta-qwen3flash),
[sudoingX/qwen38-mtp](https://github.com/sudoingX/qwen38-mtp),
[pentacoxian-dev Flash-Next IQ3E](https://huggingface.co/pentacoxian-dev/Qwen3.8-Flash-Next-IQ3E-Q8D-MTP-GGUF).

**Наука и справочники:** [ULLM ecosystem (IMC'26)](https://www.xiaojingliao.com/uploads/9/7/0/2/97024238/imc2026-lin-ullm.pdf),
[open-weight-models](https://github.com/xigh/open-weight-models),
[FreakyJolly uncensored](https://freakyjolly.com/best-uncensored-local-llms/),
[locallyuncensored guide](https://locallyuncensored.com/blog/abliterated-models-guide.html),
[bestllmfor: abliterated](https://bestllmfor.com/guides/abliterated-uncensored-local-llms),
[kextcache: тесты отказов](https://kextcache.com/uncensored-ai-models/).

**Видео:** Simply Explained (gwj2tyKkoUU), Kiber Kuznitsa (Yel0Msi1lTY), l2oot (CUuGClNNjdg),
DIY-сборка (M0CgzCR3uwk).

**Наша база:** дайджесты в общей памяти DSH (8343bcf0, 8b9482ef, ee7923ee, 9e7cd0af, 8de10650),
[локальный отчёт](../../reports/ai-nas-v100-roadmap-2026-11-19.md) (workspace pc_admin).

---
#local-llm #research #sources #benchmarks
