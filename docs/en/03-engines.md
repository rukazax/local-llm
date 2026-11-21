# 03 · Engines: what runs the models

**EN** · [Русский](../ru/03-engines.md) · [← README](../../README.md)

## Stack map for Volta (SM70), 2026

| Stack | Volta | Role here |
|---|---|---|
| **llama.cpp** | ✅ base | all GGUF: MoE, dense, VL, embeddings; TP4/layer split |
| **ik_llama.cpp** | ✅ fork | best CPU/CUDA hybrid: MoE offload to RAM, 10–30% faster than mainline — see [hybrid](06-hybrid-mode.md) |
| **1Cat-vLLM** (ex 1Cat-LLM, **1.5.4**) | ✅ flagship | NVFP4/MXFP4, AWQ, FP8-KV, GGUF (new), MTP4/MTP5/DFlash2 — [guide 08](08-1cat-vllm-nvfp4.md) |
| **llamacpp-v100** (anyei) | ✅ fork | MoE expert cache (+23–38%), MLA tensor mode, lossless q8_0 KV |
| **llama.cpp-v100** (wangxso / 1115714829) | ✅ fork | Flash-Next on 2–6 GPUs: prefill 3402 tok/s @200K on 6×16GB; DFlash2 decode up to 220 tok/s |
| **jusko-llama-volta-qwen3flash** | ✅ fork | Flash-Next serving; FlashAttention barrier fixes; agent-context checkpointing |
| **ReVolta** | ✅ vLLM fork | AWQ Flash-Next: 201 tok/s on 4×V100 without NVLink |
| **Strata** | ✅ | hot-tensor offload to one card + RAM: 60–66 tok/s on a single V100 |
| Ollama / upstream vLLM / PyTorch | ❌/⚠️ | dropped or winding down Volta — not used |

## Speculative decoding — the main free speedup

- **MTP**: the head already ships in Unsloth GGUFs; `--spec-type draft-mtp --spec-draft-n-max 3..5`
  gives **+33–39% decode** (27B: 65 → 90+ tok/s on one card). Draft max 7 is worse than max 5.
- **DFlash2** (7-token drafter, pinned revision `dedf8df6`): better on code — 425 tok/s single, 1139 agg @8×8K on 1.5.4.
- **MTP4** (native head in the NVFP4 checkpoint): better on prose and long context — 281 single, 1264 agg @8×8K on TP4.
- Watch acceptance (~70%); below that, speculation hurts.

## KV cache & context

q8_0 KV on Volta is **capacity at ~2% speed cost** (2× compression); q4_0 is emergency-only
(long-context needle drift). Decode slows with depth: 27B GGUF 65 @1K → 42 @128K.

## Multi-GPU split modes

`layer` (default, low traffic, tolerates uneven VRAM) · `tensor` (both GPUs per layer, ~+20% on
NVLink, needs identical cards) · TP4 in 1Cat/vLLM (homogeneous only) · `--n-cpu-moe N` (expert
offload: half the VRAM for −7…−15% decode).

## Quantization on Volta

GGUF Q5/Q6 (~1–2% loss, our standard) · UD-Q4_K_XL (best quality/size for 27B) · Q8_0 (~FP16) ·
IQ1_M/IQ2 (giants like MiniMax M2.7 only) · AWQ W4A16 (1Cat/ReVolta) · NVFP4/MXFP4 (4-bit weights,
FP16 compute — the 1Cat trick). Hardware FP8/FP4 compute does not exist on Volta — emulation only.

## Fine-tuning on Volta

LoRA/QLoRA with bitsandbytes (SM70 supported): 27B QLoRA on one card, 70B LoRA on two.
axolotl/LLaMA-Factory work on CUDA 12.x; verify Unsloth builds under SM70 before long runs.
Full fine-tune: up to ~30B with sharding on 128 GB; 70B full needs 8 GPUs. A cheap “own uncensored
model” pipeline: abliteration/Heretic first, then LoRA on your data.

## Exotica already working on V100

Z-Image Turbo/Base (1024² images) and MiniMax H3 (1344×768, 107 frames, 24 fps video with audio)
run natively in 1Cat-LLM. DeepSeek V4.1 Flash 552B (2-bit experts): 91 tok/s on 4×V100 with expert
offload.

---
#local-llm #engines #llamacpp #1catllm #mtp #quantization
