**← [Все проекты · All projects](https://github.com/rukazax?tab=repositories)**

# local-llm · Локальный ИИ-сервер на 4× Tesla V100 SXM2

<p align="center">
  <img src="assets/banner.svg" alt="local-llm — 4× Tesla V100 SXM2, 128 GB VRAM" width="100%">
</p>

<p align="center">
  <img alt="GPU" src="https://img.shields.io/badge/GPU-4%C3%97%20V100%20SXM2%2032GB-76b900.svg">
  <img alt="VRAM" src="https://img.shields.io/badge/VRAM-128%20GB%20HBM2%20NVLink-4B6BFB.svg">
  <img alt="engines" src="https://img.shields.io/badge/engines-llama.cpp%20%7C%201Cat--LLM-orange.svg">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-blue.svg">
  <img alt="docs" src="https://img.shields.io/badge/docs-RU%20%7C%20EN-8A2BE2.svg">
</p>

**RU** · [English](#english)

---

## 🧭 Навигация

| Раздел | О чём |
|---|---|
| [О проекте](#-о-проекте) | что это и зачем |
| [Железо](#-железо) | конфигурация 4×V100 = 128 ГБ |
| [Архитектура](#-архитектура) | схема системы |
| [Движки](#-движки) | на чём и как гоняем модели |
| [Модели](#-модели) | сводка + полная база |
| [Скорости](#-скорости) | замеры и оценки |
| [Роадмап](#-роадмап-сборки-и-настройки) | этапы сборки и настройки |
| [Сборка и запуск](docs/ru/07-build-and-launch.md) | пошаговый мануал до первого токена |
| [Перспективы](#-перспективы-и-направления) | где это применять |
| [Выводы](#-выводы) | главное по итогам исследований |
| [Документация](#-документация) | RU/EN файлы базы знаний |
| [Источники](#-источники) | откуда данные |

**Документы базы знаний:**
[Железо](docs/ru/01-hardware.md) · [Роадмап](docs/ru/02-roadmap.md) · [Движки](docs/ru/03-engines.md) · [Модели](docs/ru/04-models.md) · [Исследования](docs/ru/05-research.md) · [Гибрид VRAM+RAM](docs/ru/06-hybrid-mode.md) · [Сборка и запуск](docs/ru/07-build-and-launch.md) — и зеркала на английском в [docs/en](docs/en/).

---

## 💡 О проекте

Это сводная база знаний по сборке **домашнего LLM-сервера на списанных серверных ускорителях**.
Не «обзор для лайков», а рабочий документ: что купить, как собрать, что на этом запускается,
с какой скоростью, чему верить и куда развивать. Всё собрано из глубоких исследований
(RU и зарубежные источники: Хабр, Reddit r/LocalLLaMA, Level1Techs, GitHub-форки, научные работы)
и собственных расчётов под конкретную конфигурацию.

Формула проекта простая: **2017-й железо + 2026-й софт = скорость уровня флагманов за цену хлама** 🎯

---

## 🔧 Железо

| Компонент | Конфигурация | Примечание |
|---|---|---|
| GPU | **4× Tesla V100 SXM2 32GB** на одной несущей плате | Volta, SM70, тензор-ядра FP16, HBM2 |
| Несущая плата | заводской модуль 4×SXM2 + **полный NVLink**, PEX8749 | без NVLink скорость падает ~вдвое |
| Итого VRAM | **128 ГБ HBM2** | однородная конфигурация, TP4 без компромиссов |
| Связь с хостом | **один PCIe 3.0 x16**, питание 2×8-pin до 1200 Вт | NVLink делает GPU↔GPU, хосту хватает одного слота |
| CPU | **2× Xeon E5-2695 v4** — 18C/36T, 120 Вт | 36 ядер под CPU-часть гибрида |
| Материнская плата | **Atermiter X99 Dual X99** (ZX-DU99D4), E-ATX, C612 | 8× DDR4 DIMM, 2× M.2, два x16 |
| Охлаждение | радиаторы/водоблоки + сильный продув | воздух не тянет 4×300 Вт в закрытом корпусе |
| Питание | простой ~250 Вт · нагрузка 900–1100 Вт · пик **1400 Вт** | БП 1600 Вт, отдельная линия |
| RAM хоста | **256 ГБ** DDR4-2400 REG ECC, 8×32 (RDIMM 2Rx4) | второй tier: эксперты MoE в RAM (см. 06); 76,8 ГБ/с на сокет |
| Диск | NVMe 4–8 ГБ/с | скорость загрузки моделей |
| ОС | Ubuntu 24.04+, UEFI, Above 4G Decoding, Re-Size BAR | обязательные пункты BIOS |
| Драйвер | NVIDIA **580.x** — последний с поддержкой Volta | зафиксировать, не гнаться за новыми |

Подробно — в [docs/ru/01-hardware.md](docs/ru/01-hardware.md), пошаговая сборка и запуск —
в [docs/ru/07-build-and-launch.md](docs/ru/07-build-and-launch.md).

---

## 🗺 Архитектура

```mermaid
flowchart LR
    U[Пользователь / DSH-агенты] --> API[OpenAI-совместимый API]
    API --> ENG1[llama.cpp / форки SM70\nGGUF Q4–Q8, MTP]
    API --> ENG2[1Cat-LLM v1.5.3\nNVFP4 + MTP4 / DFlash2]
    ENG1 --> GPU0[4× V100 SXM2 32GB\nTP4 · NVLink 300 ГБ/с]
    ENG2 --> GPU0
    GPU0 --> RAM[(host RAM 256 ГБ\nэксперты MoE · KV offload)]
    MODELS[База моделей:\nобычные · abliterated · derestricted] --> ENG1
    MODELS --> ENG2
```

---

## ⚙️ Движки

| Движок | Статус на Volta | Для чего у нас |
|---|---|---|
| **llama.cpp** (+ форки SM70) | ✅ полная | все GGUF: MoE 30–120B, 72B dense, VL, embeddings |
| **1Cat-LLM** (форк vLLM, v1.5.3) | ✅ флагман | 27B NVFP4 + MTP4/DFlash2 — до **892 ток/с aggregate** |
| **llamacpp-v100 / llama.cpp-v100** (форки) | ✅ оптимизации под SM70 | Flash-Next на 2–6 GPU, MTP, +20% tensor-split |
| Ollama | ❌ выпилил Volta | не используем |
| upstream vLLM | ❌ требует CC ≥ 7.5 | только форки |
| PyTorch | ⚠️ сборки свёрнуты | инференс не на нём; fine-tune — через LoRA-стек |

Ключевой приём скорости — **спекулятивное декодирование MTP**: голова multi-token-prediction
уже внутри GGUF Unsloth, флаг `--spec-type draft-mtp` даёт **+33–39%** декода (65 → 90+ ток/с
на одной карте для 27B). Подробно — [docs/ru/03-engines.md](docs/ru/03-engines.md).

---

## 🧠 Модели

Полная база с умениями, скоростями и доверием — [docs/ru/04-models.md](docs/ru/04-models.md).
Здесь — сводка. Все влезают целиком в 128 ГБ вместе с контекстом.

| Модель | Тип | Размер | Зачем |
|---|---|---|---|
| GLM-4.5-Air-Derestricted | MoE 110B/12B | Q5 · 83.5 ГБ | основная агентская, tool-calling |
| Qwen3.8-27B (NVFP4 + MTP4) | dense | 23.4 ГБ | скоростной агент: 426 ток/с одиночный |
| Huihui-Qwen3.8-27B-abliterated | dense | Q8 · 29 ГБ | универсал без отказов + зрение + 256K |
| Qwen3-Coder-30B-A3B-abliterated | MoE 30B/3B | Q5 · 21 ГБ | код-агент, ~100 ток/с |
| Qwen2.5-72B-Instruct-abliterated | dense | Q6 · 62 ГБ | тяжёлый ризонинг, русский |
| Qwen3-VL-30B-A3B-abliterated | MoE-VL | Q5 · 22 ГБ | зрение: документы, скрины, фото |
| Hermes 4-70B | dense | Q5 · 50 ГБ | SOTA по «отказности», tool calling |
| MiniMax M2.7 | MoE 230B/10B | IQ1_M · 61 ГБ | агент-флагман open-весов (MIT) |
| AliceAI-Foundation-80B-A3B | MoE 80B/3B | Q5 · 57 ГБ | лучший русский MoE |
| Qwen3-Embedding-4B | 4B | Q8 · 4.5 ГБ | RAG-вектора |

---

## 🚀 Скорости

Замеры сообщества на V100 (точные условия — в базе моделей); наши ожидания для 4×32 помечены «оценка».

```
Qwen3.8-27B NVFP4 + MTP4 (1Cat, TP4)   ████████████████████ 426 ток/с одиночный · 892 aggregate
Qwen3.8-27B GGUF + MTP (1 карта)       ████████████░░░░░░░░  65 ток/с @1K · 42 @128K
Qwen3-Coder-30B-A3B Q5 (MoE)           ██████████████████░░  ~100 ток/с (оценка)
Qwen3.8 Flash-Next IQ3E + MTP (2×32)   ████████████████████  122 ток/с @256K контекст (замер)
GLM-4.5-Air Q5 (MoE 110B/12B)          ██████████████░░░░░░  ~45–60 ток/с (оценка)
Qwen2.5-72B Q6 (dense)                 ████████░░░░░░░░░░░░  ~25–35 ток/с (оценка)
DeepSeek V4.1 Flash 2-bit (4×V100)     ███████████████░░░░░   91 ток/с (замер, expert offload)
Prefill до 3400 ток/с на 6×V100-16 (Flash-Next MTP) — чтение 100k промпта ≈ 25–30 сек
```

Важные правила скорости: NVLink обязателен (без него вдвое медленнее), MTP-флаг включать всегда,
KV-кэш в q8_0 — на Volta это ёмкость почти без потери скорости (~2%), лимит 250–300 Вт/карту
теряет мало производительности.

---

## 🛠 Роадмап сборки и настройки

```mermaid
gantt
    title Локальный ИИ-сервер: этапы
    dateFormat X
    axisFormat %s
    section Железо
    Комплектация и проверка лотов      :0, 1
    Стенд: база + водоблоки + контур   :1, 2
    section Софт
    ОС + BIOS + драйвер 580 + CUDA 12.8 :2, 3
    Приёмка: verify-gpus (NVLink, ECC)  :3, 4
    llama.cpp + очередь GGUF            :4, 5
    1Cat-LLM + NVFP4 + замеры           :5, 6
    section Эксплуатация
    API/UI + интеграция с NAS           :6, 7
    Модели в работе + мониторинг        :7, 8
    Апгрейды: RAM 256 + 2-й сокет, NVMe :8, 9
```

Этапы с командами и критериями приёмки — [docs/ru/02-roadmap.md](docs/ru/02-roadmap.md).

---

## 🌱 Перспективы и направления

- **Агентика с приватностью**: DSH-агенты и код-агенты на локальных моделях — данные не покидают дом.
- **RAG-база знаний**: embeddings + 72B/VL ретрив и анализ своих документов.
- **Креатив и RP без фильтров**: abliterated/derestricted 27–70B.
- **Зрение**: разбор сканов, скриншотов, фото (VL-30B). Локальный OCR-конвейер.
- **Картинки и видео на том же железе**: Z-Image Turbo (1024²) и MiniMax H3 видео — через 1Cat-LLM.
- **Обучение своих моделей**: LoRA/QLoRA на 27–70B прямо на этом стенде (FP16 Volta подходит).
- **Мультиинстанс**: 128 ГБ позволяют держать 2–3 модели одновременно (27B + Coder-30B + embeddings).

---

## ✅ Выводы

1. **4×V100 32GB — однородная конфигурация без компромиссов**: TP4 в любом движке, любая модель
   до ~100 ГБ весов влезает целиком. Смешивать 16+32 не нужно — и было бы вредно.
2. **Экосистема Volta сжалась, но жива и целеустремлена**: llama.cpp и 1Cat-LLM целенаправленно
   оптимизируют SM70; Ollama/vLLM/PyTorch ушли. Наш стек подобран правильно.
3. **MTP-спекуляция — главный бесплатный ускоритель**: +33–39% декода флагом. Включать всегда.
4. **Uncensored-модели почти ничего не стоят по качеству** (Heretic-метод измерим и аккуратен),
   но их надо изолировать от инструментов с доступом к системе — принцип «модель без отказов +
   доступ к шеллу = риск».
5. **RAM — это второй tier, а не апгрейд «на вырост»**: 256 ГБ DDR4-2400 (8 каналов) дают
   MoE со 100+ млрд общих параметров ~5–15 ток/с; dense-модели в RAM не гоняем. Драйвер 580 —
   последний для Volta, стек фиксируем. Подробно — [Гибрид VRAM+RAM](docs/ru/06-hybrid-mode.md).
6. **Никакой локальный 27–120B не тягается с облачными флагманами в сложной агентике** —
   но для приватных задач, кода, RAG, зрения и креатива он даёт скорость и контроль,
   которых облако не даст.

---

## 📚 Документация

| RU | EN |
|---|---|
| [Железо](docs/ru/01-hardware.md) | [Hardware](docs/en/01-hardware.md) |
| [Роадмап](docs/ru/02-roadmap.md) | [Roadmap](docs/en/02-roadmap.md) |
| [Движки](docs/ru/03-engines.md) | [Engines](docs/en/03-engines.md) |
| [База моделей](docs/ru/04-models.md) | [Models database](docs/en/04-models.md) |
| [Исследования](docs/ru/05-research.md) | [Research](docs/en/05-research.md) |
| [Гибрид VRAM+RAM](docs/ru/06-hybrid-mode.md) | [Hybrid mode](docs/en/06-hybrid-mode.md) |
| [Сборка и запуск](docs/ru/07-build-and-launch.md) | [Build & launch](docs/en/07-build-and-launch.md) |

## 📖 Источники

Хабр-серия о V100-серверах · Reddit r/LocalLLaMA (V100 Home Lab Bible) · Level1Techs (DIY backplane) ·
Angry Sysadmins · 1Cat-LLM · llamacpp-v100 форки · llamaperf.com · roksblog.de · обзор ULLM-экосистемы (IMC'26) ·
видео Simply Explained, Kiber Kuznitsa, l2oot. Полный список со ссылками — [docs/ru/05-research.md](docs/ru/05-research.md).

## Лицензия

[MIT](LICENSE) © 2026 rukazax

---

## English

Local AI server knowledge base built on **4× Tesla V100 SXM2 32GB = 128 GB VRAM (NVLink TP4)**.
A working document, not a review: what to buy, how to assemble, what runs, how fast, what to trust,
where to grow next. Built from deep research across Russian and international sources
(Habr, r/LocalLLaMA, Level1Techs, SM70 GitHub forks, an IMC'26 paper on uncensored-model ecosystems).

**Project formula: 2017 hardware + 2026 software = flagship-class speed for scrapyard prices.** 🎯

### Hardware

4× V100 SXM2 32GB on a factory 4-module NVLink carrier (full NVLink or you lose ~half the speed)
with a single PCIe 3.0 x16 uplink and 2× 8-pin feeding up to 1200 W; **2× Xeon E5-2695 v4**
(18C/36T, 120 W) on an **Atermiter X99 Dual X99** (E-ATX, C612, 8 DIMMs); 1600 W PSU on a dedicated
line (idle ~250 W, load 900–1100 W, peak ~1400 W); host RAM **256 GB** DDR4-2400 REG ECC
(8× 32 GB RDIMM 2Rx4, 76.8 GB/s per socket) — the second tier where MoE experts live
(see [docs/en/06-hybrid-mode.md](docs/en/06-hybrid-mode.md)); NVMe 4–8 GB/s;
Ubuntu 24.04 with UEFI + Above 4G Decoding + Re-Size BAR, NVIDIA **580.x** — the last Volta driver, frozen.
Step-by-step build and launch: [docs/en/07-build-and-launch.md](docs/en/07-build-and-launch.md).

### Engines

- **llama.cpp** and its SM70 forks — every GGUF: MoE 30–120B, dense 72B, vision, embeddings;
- **1Cat-LLM** (vLLM fork) — 27B NVFP4 with MTP4/DFlash2 speculative decoding, **892 tok/s aggregate**;
- Ollama and upstream vLLM dropped Volta — not used. PyTorch builds are winding down.

### Speed rules

NVLink is mandatory (without it — half the speed). `--spec-type draft-mtp` gives **+33–39% decode**
(the MTP head already ships inside Unsloth GGUFs). KV cache in q8_0 is capacity at ~2% speed cost on Volta.
A 250–300 W per-card limit costs almost no performance.

### Models

Everything below fits fully in 128 GB with context: GLM-4.5-Air-Derestricted Q5 (83.5 GB, main agent),
Qwen3.8-27B NVFP4+MTP4 (speed demon), Huihui-Qwen3.8-27B-abliterated Q8 (universal uncensored with vision
and 256K context), Qwen3-Coder-30B-A3B-abliterated Q5 (~100 tok/s code agent), Qwen2.5-72B-abliterated Q6,
Qwen3-VL-30B-A3B-abliterated Q5 (vision), Hermes 4-70B Q5, MiniMax M2.7 IQ1_M (61 GB, open-weight agentic
flagship), AliceAI-80B-A3B Q5 (best Russian MoE), Qwen3-Embedding-4B Q8 (RAG).
Full database with skills, speeds and trust levels: [docs/en/04-models.md](docs/en/04-models.md).

### Roadmap

Lots check → bench assembly (SXM2 seating, leak test) → OS/BIOS/driver/CUDA → acceptance
(4 GPUs, NVLink links, ECC counters) → llama.cpp + GGUF queue → 1Cat-LLM + NVFP4 + benchmarks →
API/UI + NAS integration → models in production + monitoring → upgrades (second socket + 256 GB RAM, NVMe, optional
2-card “instance B”). Details: [docs/en/02-roadmap.md](docs/en/02-roadmap.md).

### Directions

Private agentics (DSH agents, coding agents), RAG over your own documents, unfiltered creative/RP,
vision (documents, screenshots), image/video generation on the same rig (Z-Image, MiniMax H3 via 1Cat-LLM),
fine-tuning your own models (LoRA/QLoRA on 27–70B), multi-instance serving.

### Conclusions

1. 4×32 GB is a homogeneous no-compromise config: TP4 in any engine, models up to ~100 GB of weights fit whole.
2. The Volta ecosystem shrank but lives with purpose: llama.cpp and 1Cat-LLM target SM70 on purpose.
3. MTP speculation is the main free speedup — always on.
4. Uncensored models cost almost nothing in quality (Heretic is measurable), but keep them away from
   system-level tools: no-refusal model + shell access = risk.
5. RAM is a second tier, not a rainy-day upgrade: 256 GB DDR4-2400 (8 channels) runs MoE with
   100B+ total parameters at ~5–15 tok/s; dense models stay out of RAM. Driver 580 is the last for
   Volta — freeze the stack. Details: [docs/en/06-hybrid-mode.md](docs/en/06-hybrid-mode.md).
6. No local 27–120B beats cloud flagships at hard agentic work — but for private tasks, code, RAG,
   vision and creativity it gives speed and control the cloud cannot.

### License

[MIT](LICENSE) © 2026 rukazax

---

#local-llm #v100 #sxm2 #nvlink #localai #llm #llamacpp #1catvllm #nvfp4 #mtp #uncensored #abliterated #selfhosted #homelab #rag #ai-inference