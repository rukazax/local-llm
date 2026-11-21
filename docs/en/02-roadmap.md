# 02 · Roadmap: build and setup

**EN** · [Русский](../ru/02-roadmap.md) · [← README](../../README.md)

```mermaid
gantt
    title local-llm project stages
    dateFormat X
    axisFormat %s
    section Hardware
    S0. Lots check              :0, 1
    S1. Bench: base, blocks, loop :1, 2
    section Software
    S2. OS + BIOS + driver + CUDA :2, 3
    S3. Acceptance (NVLink, ECC)  :3, 4
    S4. llama.cpp + GGUF queue    :4, 5
    S5. 1Cat-LLM + NVFP4 + bench  :5, 6
    section Operations
    S6. API/UI + NAS integration  :6, 7
    S7. Models in production      :7, 8
    S8. Upgrades (RAM, NVMe, B-rig):8, 9
```

**S0 — Lots check.** Buy 4× V100 SXM2 **32GB** (homogeneous!), a 4-module base with NVLink bridges,
SFF adapters + cables, 4 waterblocks, a 360×45 + 240×30 loop, a 2 kW PSU. Count washers/springs;
haggle (sellers expect 10–20% off). Acceptance: everything present, photos both sides.

**S1 — Bench assembly.** SXM2 seating per spec; X-pattern paste; 5 mm VRM pads; 24 h leak test.
Acceptance: 4 modules visible in lspci, no leaks.

**S2 — OS & stack.** UEFI + Above 4G + ReBAR; driver 580.x (frozen); CUDA 12.8 in PATH;
Python 3.12 + uv. Acceptance: `nvidia-smi -L` lists 4 GPUs.

**S3 — Hardware acceptance.** Run the acceptance script: 4 GPUs, `nvidia-smi nvlink -s` active
links, topo -m; 30-min stress → ECC counters still zero; wall-power 900–1100 W at a 250 W/card cap;
temps < 85 °C. Full checklist: [07-build-and-launch](07-build-and-launch.md).

**S4 — llama.cpp.** Build with `GGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=70`; serve GGUF with
`-ngl all --tensor-split 1,1,1,1 -fa on -ctk q8_0 -ctv q8_0`. Tune in order: offload → quant →
context → KV → FA → batch → speculation. Benchmark with llama-bench (PP and TG separately).

**S5 — 1Cat-LLM.** Run the installer `--check`, then install; target the reference numbers:
27B NVFP4 **425 tok/s single (DFlash2), 1139–1264 aggregate @8×8K** (±15%). DFlash2 for code, MTP4 for prose.

**S6 — Serving layer.** OpenAI-compatible API + token auth, web UI, task routing to the NAS/DSH
agents (code → Coder-30B, agentics → GLM-Air, vision → VL-30B).

**S7 — Operations.** Monitor temps/ECC/watts; the download schedule (01:30–19:00) is already in cron;
every new model goes through llama-bench into the models database.

**S8 — Upgrades.** Second socket + 256 GB RAM first (unlocks Flash Next and hybrid tier 2,
see [06](06-hybrid-mode.md)); NVMe as needed; an optional 2-card
“instance B” when parallel workloads appear; a 192–256 GB platform only when 128 GB is truly not enough.

---
#local-llm #roadmap #setup #v100
