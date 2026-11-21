# 06 · Hybrid mode: VRAM + CPU/RAM

**RU** · [Русская версия](../ru/06-hybrid-mode.md) · [← README](../../README.md)

---

## What changed (2026-11-20)

Two new inputs reshaped the plan:

- **One 4-slot V100 SXM2 carrier with full NVLink** — 128 GB VRAM as a single homogeneous TP4 pool.
- **The model must be able to use CPU+RAM, not just VRAM** — for the models that do not fit in 128 GB.
- Target host: **2× Xeon E5-2695 v4 (36 threads)** on Atermiter X99 Dual + 8×32 GB DDR4-2400 RDIMM = **256 GB**, eight channels.

## The main conclusion

The hybrid is a **full second tier**, not a workaround: attention and shared experts stay on the GPU,
the heavy MoE experts live in RAM. A 110–235B model runs, paying in speed proportional to DDR4 bandwidth.
The split is simple:

| Mode | Fits | Speed | Use |
|---|---|---|---|
| VRAM-only (TP4, `-sm row`) | up to ~100 GB of weights | 25–100 tok/s | daily work, agents, code |
| Hybrid (`--n-cpu-moe`, `-ot exps=CPU`) | 140–235 GB | 5–25 tok/s | heavy MoE, batches, offline jobs |

## How the hybrid works

Two mechanisms in llama.cpp / ik_llama.cpp, both about MoE:

1. `--n-cpu-moe N` — experts of the first N layers in RAM, attention and shared parts on the GPU.
   Flexible: N is tuned until VRAM sits at 90–95%.
2. `-ot 'exps=CPU'` — all experts in RAM, attention on the GPU. Simpler and more predictable, but slower.

Obligatory companions: `--no-mmap` (otherwise the page cache on 256 GB of RAM thrashes on 200+ GB
models), `-t 36` (not 72 — extra threads hurt across two sockets), `--numa distribute`,
KV cache as `-ctk q8_0 -ctv q8_0`.

## The ceiling arithmetic (why it is slow, and how slow)

Hybrid speed ≈ RAM bandwidth / bytes read per token:

- DDR4-2400, 8 channels: 153.6 GB/s theoretical, **~110 GB/s** in practice.
- A MoE with 22B active parameters at Q4 ≈ 11 GB per token → **~10 tok/s**.
- A MoE with 37B active at Q2 ≈ 9–10 GB per token → **~6–11 tok/s** (quant and GPU share dependent).
- A dense 70B at Q4 ≈ 35 GB per token → **~3 tok/s**: dense models do not belong in RAM, only MoE.

Hence the rule: the hybrid makes sense for MoE with 100+ billion **total** and ≤40 billion **active**
parameters. Anything denser stays in VRAM at a more aggressive quant.

## What breaks on Volta (expectation vs reality)

| Expectation | Reality |
|---|---|
| Q4 speeds up compute | No: SM70 has no INT4/BF16/FP8 tensor paths — Q4 saves memory, dequant runs at FP16 |
| NVFP4 gives native acceleration | Software emulation; the gain comes from MTP and batching only |
| More CPU threads is faster | No: 36 threads is the optimum; 72 falls off a cliff on NUMA |
| Any new engine will do | Ollama and upstream vLLM dropped Volta; PyTorch builds are winding down |

The real accelerators on this board: **MTP speculation (+33–39%)**, batching, `-sm row` with live NVLink,
q8_0 KV instead of f16.

## Models by mode

The full database with licenses, ratings and sources is in `docs/en/04-models.md`; here is only the split.

**Tier 1 — fits entirely in 128 GB:**

| Model | Quant | Size | Estimate |
|---|---|---|---|
| GLM-4.5-Air-Derestricted | Q5 | 83.5 GB | 45–60 tok/s, primary agent |
| Hermes 4-70B | Q5 | 50 GB | 25–35 tok/s, RP/creative + tool-calling |
| Qwen2.5-72B-Instruct-abliterated | Q6 | 62 GB | 25–35 tok/s, heavy Russian reasoning |
| AliceAI-80B-A3B | Q5 | 57 GB | 60–90 tok/s, best Russian MoE |
| Qwen3-Coder-30B-A3B-abliterated | Q5 | 21 GB | ~100 tok/s, code and shell |
| Huihui-Qwen3.8-27B-abliterated | Q8 | 29 GB | 60–90 tok/s, universal + vision + 256K |
| Qwen3-VL-30B-A3B-abliterated | Q5 | 22 GB | 80–100 tok/s, documents and screenshots |
| MiniMax M2.7 | IQ1_M | 61 GB | 15–25 tok/s, open-weight agent (MIT) |
| Qwen3-Embedding-4B | Q8 | 4.5 GB | RAG vectors |

**Tier 2 — through RAM (256 GB):**

| Model | Quant | Size | Estimate |
|---|---|---|---|
| Qwen3-235B-A22B | Q4_K_M | ~140 GB | 8–15 tok/s |
| Qwen3-235B-A22B | IQ2_XXS | ~75 GB | 15–25 tok/s (tight, but in VRAM) |
| GLM-4.5/4.6 355B | Q4 | ~200 GB | 5–10 tok/s |
| DeepSeek V3/R1 671B | IQ2_XXS | ~190 GB | 2–5 tok/s — an experiment, not work |
| Kimi K2 1T | any | 250–280 GB | does not fit even in RAM — cross it out |

## Glossary (so the terms do not blur)

- **Reasoning** — the model thinks before answering: breaks the task into steps, checks itself.
  "Heavy" = thousands of reasoning tokens and tens of seconds before the first word (72B Q6:
  2000 thinking tokens ≈ a minute). Use it surgically: architecture, legal analysis, debugging —
  not every chat message.
- **RP / creative** — roleplay and prose: voice and atmosphere matter, not facts. Code-tuned models
  sound like a manual here.
- **Tool-calling** — the model invokes functions as structure (a JSON object with a name and arguments)
  rather than as text. All agentics rests on it. What to check: JSON validity, argument accuracy,
  correct tool choice, multi-step persistence, parallel calls, no refusals of legitimate commands.

## Security

A no-refusal model + shell/file access + indirect prompt injection = RCE. The mandatory layer:
a dedicated user without sudo, a container with `--cap-drop=ALL`, an egress allow-list, tool-call
logging, HITL on write/exec, no `~/.ssh` or `.env` in the context. Abliteration removes the refusal,
not the knowledge.

## What changes in the other documents

- `01-hardware.md`: RAM 64→128 GB becomes **256 GB** (8×32 DDR4-2400 RDIMM, two sockets) — without it
  tier 2 does not exist.
- `03-engines.md`: **ik_llama.cpp** joins llama.cpp / 1Cat-LLM as the best CPU/CUDA hybrid engine.
- `04-models.md`: unchanged — the models are the same, only the launch mode changes.
- `02-roadmap.md`: the "RAM upgrade" stage becomes "second socket + 256 GB" and moves ahead of tier-2 models.

## Sources

[HuggingFace: MoE offload guide](https://huggingface.co/blog/Doctor-Shotgun/llamacpp-moe-offload-guide),
[powabase: hybrid CPU/GPU inference](https://powabase.ai/blog/run-a-moe-llm-locally-on-your-gpu-connect-it-to-a-baas/),
[ktransformers benchmarks](https://ktransformers.net/en/benchmarks),
[llama.cpp #21112 — 4×V100 measurements](https://github.com/ggml-org/llama.cpp/discussions/21112),
[willitrunai: V100 32GB](https://willitrunai.com/gpus/v100-32gb),
[1Cat-LLM](https://github.com/1CatAI/1Cat-vLLM), [anyei/llamacpp-v100](https://github.com/anyei/llamacpp-v100).

Caveats: the tok/s figures are estimates derived from memory bandwidth, not measurements on our hardware;
the claimed 1139–1264 tok/s aggregate for 1Cat is verifiable only by replication; prices for 4-slot NVLink
carriers in Russia are unconfirmed (Avito sits behind an anti-bot).

---

#local-llm #v100 #hybrid #cpu-offload #moe #llamacpp
