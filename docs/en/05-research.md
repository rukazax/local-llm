# 05 · Research: findings and sources

**EN** · [Русский](../ru/05-research.md) · [← README](../../README.md)

## Consolidated findings (all research waves, 2026-11-19)

### Hardware & assembly

No full NVLink → ~half the speed (57 vs ~100 tok/s) — Simply Explained, roksblog. Idle 42 W/module;
a 250–300 W cap costs little (150 W — minimal loss) — Angry Sysadmins, Level1Techs. Above 4G +
ReBAR + UEFI mandatory; x8/x8 bifurcation for single-slot. Peak 1350 W; loop 360×45 + 240×30;
a block handles ~300 W/card — Kiber Kuznitsa, Habr 1084234. No commercial 6-module boards;
DIY inter-board NVLink bridges are unproven — Level1Techs.

### Speeds (measured on V100)

| Setup | Result |
|---|---|
| Qwen3.8-27B NVFP4 + MTP4, 1Cat TP4 4×32 | **892 tok/s aggregate** @8K/8 streams; 426 single; 367 @64K |
| Qwen3.8-27B GGUF Q4_K_M + MTP, 1×32 | 65 tok/s @1K → 42 @128K (stock: 35.95 → 16.49) |
| Flash-Next IQ3E+MTP, 2×32 NVLink | 122 tok/s @256K; tensor split +20% vs layer |
| Flash-Next (6×16GB, wangxso) | prefill 3402 tok/s @200K |
| DeepSeek V4.1 Flash 2-bit, 4×32 + offload | 91 tok/s decode, 2100 prefill |
| qwen3-coder:30b Q4, 2×V100 | 98.8 tok/s |
| MTP flag on consumer GPUs | +33–39% decode |
| KV q8_0 on Volta | ~2% vs f16 — “capacity, not speed” |
| 2×V100-16 no NVLink vs RTX 4090 | 50–52 vs 90 tok/s (27B MTP, 131K) |

### Volta ecosystem

Driver **580.x is the last** for Volta; CUDA 13 dropped Volta; test new kernels before upgrading.
Ollama removed Volta, upstream vLLM needs CC ≥ 7.5, PyTorch builds wound down 09.2026.
1Cat-LLM v1.5.3 (2026-11-14): GGUF support, the reference rig uses **62 GB host RAM**; Z-Image and
MiniMax H3 already run on SM70.

### Uncensored ecosystem (IMC'26 paper, 16k models)

Refusal rate: ULLM 35.6% vs 77.4% regular. Methods: fine-tunes 16%, pure ablation 4.7%, merges 2%,
compression 13.7%, combined 62.5%. Heretic dominates since Nov 2025 (24% of new ULLMs); MergeKit
94% of merges, TIES the top technique. More downloads → lower refusal rates.

### Model key facts

Qwen3.8-27B (08.2026, Apache 2.0): hybrid GDN (3 DeltaNet : 1 attention), MTP, native vision, 256K;
GPQA 89.2, LiveCodeBench 90.3. MiniMax M2.7 230B/A10B MIT: IQ1_M = 60.7 GB — an open-weight agentic
flagship that fits our 128 GB. Hermes 4-70B: SOTA RefusalBench. AliceAI-80B-A3B (Yandex): strongest
Russian MoE. Nemotron Bolt: GPQA 88.83. DeepSeek V4 Flash abliterated: 154 GB Q4 — out of reach
(192 GB class). Abliteration costs ~0 speed (62.0 vs 62.1 tok/s).

## Sources

**RU:** [Habr: LLM server cheaper than RTX 3090](https://habr.com/ru/articles/1084234/),
[one Tesla V100 32GB](https://habr.com/ru/articles/1093584/),
[AI lab for 200k ₽](https://habr.com/ru/articles/1041610/),
[Vibecode on the cheap](https://habr.com/ru/articles/1049052/),
[V100 16GB in an RTX 4090 case](https://habr.com/ru/articles/1039198/).

**EN/forums:** [Angry Sysadmins](https://angrysysadmins.tech/2026/03/grassyloki/cheapish-ai-homelab-on-a-budget-v100s-custom-boards-and-nvlink/),
[Level1Techs DIY backplane](https://forum.level1techs.com/t/designing-an-open-source-budget-4x-v100-sxm2-nvlink-backplane-passive-pcie-vs-pex8749/250801?page=2),
[roksblog: 2×V100 vs RTX 4090](https://www.roksblog.de/can-two-old-tesla-v100s-beat-an-rtx-4090-for-a-fully-local-hermes-agent/),
[llamaperf V100-32GB](https://llamaperf.com/gpu/v100-32gb),
[vramcalculator flags](https://vramcalculator.com/llama-cpp-performance-flags/),
[bswen optimization](https://docs.bswen.com/blog/2026-03-15-llamacpp-optimization-speed/),
[carteakey guide](https://carteakey.dev/blog/local-inference/local-llm-optimization/).

**Forks/engines:** [1Cat-LLM](https://github.com/1CatAI/1Cat-vLLM),
[anyei/llamacpp-v100](https://github.com/anyei/llamacpp-v100),
[wangxso/llama.cpp-v100](https://github.com/wangxso/llama.cpp-v100),
[jusko fork](https://github.com/jackjusko/jusko-llama-volta-qwen3flash),
[sudoingX/qwen38-mtp](https://github.com/sudoingX/qwen38-mtp),
[Flash-Next IQ3E GGUF](https://huggingface.co/pentacoxian-dev/Qwen3.8-Flash-Next-IQ3E-Q8D-MTP-GGUF).

**Science & guides:** [ULLM ecosystem IMC'26](https://www.xiaojingliao.com/uploads/9/7/0/2/97024238/imc2026-lin-ullm.pdf),
[open-weight-models](https://github.com/xigh/open-weight-models),
[FreakyJolly](https://freakyjolly.com/best-uncensored-local-llms/),
[locallyuncensored](https://locallyuncensored.com/blog/abliterated-models-guide.html),
[bestllmfor](https://bestllmfor.com/guides/abliterated-uncensored-local-llms),
[kextcache refusal tests](https://kextcache.com/uncensored-ai-models/).

**Videos:** Simply Explained (gwj2tyKkoUU), Kiber Kuznitsa (Yel0Msi1lTY), l2oot (CUuGClNNjdg),
DIY build (M0CgzCR3uwk).

---
#local-llm #research #sources #benchmarks
