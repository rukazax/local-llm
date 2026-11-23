# 04 · Model database: regular, uncensored, trainable

**EN** · [Русский](../ru/04-models.md) · [← README](../../README.md)

Speeds: community measurements on V100 are marked ✅ **measured**; 4×32 NVLink TP4 figures are
estimates. Every model fits **fully** in 128 GB with context; pairs of small ones co-exist.

## A. Regular (official) models 🏛

The quality benchmark: unmodified weights, maximum intelligence and reliability. For code and
hard agentics prefer these.

| Model | Type | Quant · size | Speed (est/measured) | Skills & purpose | Trust |
|---|---|---|---|---|---|
| **Qwen3.8-27B** (official, Apache 2.0) | dense 27B, hybrid GDN+attention, MTP | UD-Q5/Q8 · 20–29 GB | ✅ 65 tok/s @1K (GGUF+MTP, one card); 425 tok/s NVFP4+DFlash2 (TP4); GGUF Q8 on 4×32 ~50–70 | the new-generation universal: native vision, 256K context, code, agentics, multilingual | ★★★★★ GPQA 89.2, LiveCodeBench 90.3 — first line for critical code |
| **GLM-4.5-Air** (Zhipu) | MoE 110B/12B | Q5 · 83.5 GB | est 45–60 tok/s | the main agent: tool-calling, long context, planning | ★★★★★ Sonnet-class agentics |
| **Qwen2.5-72B-Instruct** | dense 72B | Q6 · 62 GB | est 25–35 tok/s | heavy reasoning, strong Russian | ★★★★☆ |
| **GPT-OSS-120B** (OpenAI, Apache 2.0) | MoE 120B/5.1B | Q4 · ~65 GB | est 50–70 tok/s | reasoning with adjustable effort, browser/code tools | ★★★★☆ |
| **GPT-OSS-20B** | MoE 20B/3.6B | Q5 · ~12 GB | est 100+ tok/s | background instance, quick tasks | ★★★★☆ |
| **Llama-3.3-70B** (Meta) | dense 70B | Q5 · ~50 GB | est 25–35 tok/s | western classic: MMLU 86, HumanEval 88.4; weaker Russian | ★★★★☆ |
| **Qwen3.8-Flash-Next** (177B/3B MoE) | MoE + PLE table | IQ3E · 80 GB (+27–50 GB RAM for PLE) | ✅ 122 tok/s @256K (2×32, MTP) | ultra-long context (256K–1M), fast MoE | ★★★★☆ needs RAM 96+ — enable after the RAM upgrade |
| **Nemotron 3.5 Super 120B / Bolt 74B-A9B** (NVIDIA) | MoE/Mamba hybrid | Q4/IQ2 · 60–25 GB | est 50–80 tok/s | reasoner: GPQA 88.8, BrowseComp 70 | ★★★★☆ |
| **QwQ-32B / DeepSeek-R1-Distill-32B** | dense 32B reasoners | Q5 · ~22 GB | est 60–80 tok/s | math/logic (AIME ~80%) | ★★★★☆ |
| **Step-3.5-Flash** 196B/A11B (Apache 2.0) | MoE | IQ3 · ~85 GB | est 40–55 tok/s | agent + code: SWE-bench 74.4% | ★★★★☆ |
| **Ling-3.0-flash** 124B/A5.1B (MIT) | MoE | Q4 · ~65 GB | est 55–75 tok/s | token-efficient agent | ★★★☆☆ |
| **InternVL3-78B** | dense VLM | Q5 · ~55 GB | est 25–35 tok/s | SOTA open vision (MMMU 72.2) | ★★★★☆ |
| **DeepSeek-OCR / -OCR-2** | 3.3B | Q8 · ~4 GB | 100+ tok/s | OCR specialist: books as pixels | ★★★★☆ |
| **Qwen3-Embedding-4B** | embed 4B | Q8 · 4.5 GB | thousands tok/s | RAG vectors | ★★★★★ |

## B. Uncensored 🕊 (abliterated · Heretic · derestricted)

Methods: **abliteration** removes the refusal direction from weights; **Heretic** is automated
ablation with metrics (dominant since Nov 2025); **derestricted** fine-tunes on refusal-free data
(ArliAI); merges via MergeKit/TIES. IMC'26: ULLMs comply with “harmful” prompts 64% vs 23%;
quality slightly below the original.

| Model | Base | Quant · size | Speed | Purpose | Trust |
|---|---|---|---|---|---|
| **Huihui-Qwen3.8-27B-abliterated** | Qwen3.8-27B | Q8 · 29 GB | ✅ same as original (65 tok/s @1K with MTP) | universal uncensored: gritty fiction, grey-zone tasks, security writeups; vision and 256K preserved | ★★★★☆ the 2026 “best overall” in 27B |
| **Huihui-Qwen3-Coder-30B-A3B-abliterated** | Qwen3-Coder-30B | Q5 · 21 GB | ✅ ~99 tok/s (measured on 2×V100) | fast code agent without preachy refusals | ★★★★☆ |
| **Huihui-Qwen2.5-72B-abliterated** | Qwen2.5-72B | Q6 · 62 GB | est 25–35 tok/s | heavy reasoning + Russian, uncensored | ★★★★☆ |
| **Huihui-Qwen3-VL-30B-A3B-abliterated** | Qwen3-VL-30B | Q5 · 22 GB | est 85–105 tok/s | unfiltered vision: screenshots, documents, photos | ★★★★☆ |
| **Huihui-Qwen3-8B-abliterated-v2** | Qwen3-8B | Q6 · 7 GB | ✅ 100+ tok/s | background instance | ★★★☆☆ |
| **GLM-4.5-Air-Derestricted** (ArliAI) | GLM-4.5-Air | Q5 · 83.5 GB | est 45–60 tok/s | the main agent without safety lectures — a fine-tune, not ablation: closest to the original | ★★★★★ our DSH workhorse |
| **Hermes 4-70B** (Nous) | Llama-3.3-70B | Q5 · 50 GB | est 25–35 tok/s | minimal-refusal official fine-tune: SOTA RefusalBench, hybrid reasoning, tool calling | ★★★★☆ |
| **Gemma-4-27b-uncensored / GLM-4.7-Flash-Heretic** | various | Q4 · 14–18 GB | est 60–90 tok/s | fresh bases with Heretic metrics | ★★★☆☆ |

Trust rule: abliteration ≈ −0–3% quality; Heretic is measurable and gentler; derestricted
fine-tunes are closest to the original. For code and critical math — official weights; for grey
zones and creativity — ablations. Security: a no-refusal model + shell access = risk — keep such
instances isolated from tools.

## C. Creative & RP 🎭

Midnight Miqu Rosso 70B/123B (Llama-3 merges, top RP, unstable facts) · Magnum v4/v5 (Claude-style
prose) · Cydonia / EVA-Llama / NemoMix (12–72B mixes). Download per task — RP models displace the
working set.

## D. Vision 👁

Qwen3-VL-30B-A3B (+abliterated, 22 GB, the workhorse) · InternVL3-78B (55 GB, max quality) ·
DeepSeek-OCR-2 (4 GB, streaming OCR) · Huihui-Qwen3.8-27B-abliterated (29 GB, native vision,
no refusals).

## E. Trainable models 🎓

Fine-tune targets on this rig (LoRA/QLoRA, FP16 Volta): **Qwen3.8-27B** (best foundation: fresh,
MTP, vision), **GLM-4.5-Air** (agent specialization), **Llama-3.3-70B** (western style). 27B QLoRA
fits one card; 70B LoRA fits two. Stack: bitsandbytes (SM70 supported) + axolotl/LLaMA-Factory;
verify Unsloth builds under SM70. Own “uncensored” model: abliteration/Heretic first, then LoRA on
your data — a two-stage pipeline.

## F. Speech and books 🎙

The creative layer has its own document — [09 · Writing and voicing a book](09-books-writing-and-voicing.md).
This section only lists the models and their VRAM cost.

| Job | Model | Size · VRAM | License | Note |
|---|---|---|---|---|
| Voicing, primary | **VoxCPM2** (OpenBMB, 2B) | ~5.6 GB weights · ~8 GB | Apache-2.0 | 48 kHz, Voice Design from a text description; ru SIM 81.1, best in class; ru WER 3.6–5.2 % · card figures, **not verified on our rig** (needs a GPU) |
| Second voice | **Qwen3-TTS-12Hz-1.7B-Base** | ~4.8 GB | Apache-2.0 | ru WER 3.21, but stress marks need RUAccent |
| Stress safety net, CPU fallback | **TeraTTSv2** (ONNX) | CPU · 2.5 GB RAM | OpenRAIL-M + attribution | RUAccent built in, commercial use allowed; ✅ **measured**: RTF 0.47 (0.34–0.67) on CPU, WER 1.8 % with GigaAM, 44.1 kHz |
| RU cloning, experiments only | **F5-TTS_RUSSIAN** | ~4 GB | **CC BY-NC 4.0** | not part of the main build |
| Voicing acceptance (WER) | **whisper-large-v3** | 4.4 GB | MIT | 15.2× real time on V100 |
| Stress marks before synthesis | **ruaccent** | CPU | MIT | homographs 0.82 vs 0.38 for silero |
| Style RAG over the author corpus | **Qwen3-Embedding-4B** | 4.5 GB | Apache-2.0 | already in table A |

The only live speech measurement so far is TeraTTSv2 on CPU (15 GB RAM, no GPU):
[TeraTTSv2 acceptance run](../research/teratts-cpu-acceptance-2026-11-23.md). Every other figure in
the table above comes from model cards, not from us.

**The writer and the editor must be different models.** Prose: Qwen3.8-27B (or its abliterated
variant); editing: Qwen2.5-72B; a "second prose voice": **Hermes 4-70B**, Magnum or Miqu. One model
writing and praising its own text hides the water; swapping the model makes it obvious.

VRAM: 27B Q8 (29 GB) + 72B Q6 (62 GB) + TTS 8 + Whisper 4.4 + embeddings 4.5 ≈ 108 GB — it fits into
128 GB, but context makes it tight. Keep either "writer + editor" or "writer + TTS + Whisper +
embeddings" resident.

## Sphere → model cheat sheet 🗺

| Sphere | First line | Reserve |
|---|---|---|
| Agentics, tool-calling (DSH) | GLM-4.5-Air-Derestricted | MiniMax M2.7, Step-3.5-Flash |
| Code, vibecoding | Qwen3-Coder-30B-A3B-abliterated | Qwen3.8-27B official, R1-Distill |
| Reasoning, math | QwQ-32B / R1-Distill-32B | GPT-OSS-120B, Nemotron Bolt |
| Long documents (100K+) | Qwen3.8-27B (256K) | Flash-Next (after RAM upgrade) |
| Vision/OCR | Qwen3-VL-30B-A3B | InternVL3-78B, DeepSeek-OCR-2 |
| Russian language | AliceAI-80B-A3B | Qwen2.5-72B, GLM-Air |
| Creative/RP unfiltered | Huihui-Qwen3.8-27B-abliterated | Midnight Miqu, Hermes 4-70B |
| RAG vectors | Qwen3-Embedding-4B | — |
| Private all-round chat | Qwen3.8-27B NVFP4+MTP4 (speed) | GLM-Air (quality) |
| Images/video | Z-Image / H3 via 1Cat-LLM | — |

## Honest comparison with flagships ⚖️

Our class (27–120B local) vs cloud flagships of 2026 (GPT-6.2 Astra, Claude Opus 5.x, Gemini 4
Carbon, DeepSeek V4): flagships win hard multi-step agentics, ultra-long context and expert
judgment. Local wins privacy, token cost (zero), queue-free speed, version control and grey zones.
A local rig covers **95% of daily work**; cloud is a targeted reserve. “Local + cloud fallback” is
an architecture, not a compromise.

---
#local-llm #models #uncensored #abliterated #fine-tuning #benchmarks
