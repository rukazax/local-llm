# 01 · Hardware: configuration and assembly

**EN** · [Русский](../ru/01-hardware.md) · [← README](../../README.md)

## Final configuration

| Component | Choice | Why |
|---|---|---|
| GPU | **4× Tesla V100 SXM2 32GB** | 128 GB HBM2, homogeneous; TP4 without compromise in any engine |
| Carrier | 4-module SXM2 base with **full NVLink** | NVLink 300 GB/s GPU↔GPU; without it — ~half the speed (57 vs ~100 tok/s measured) |
| Host link | PCIe 3.0 x16 → 2× SFF-8654/8664 adapters + cables | x8 per GPU is enough; GPU↔GPU traffic rides NVLink |
| Cooling | waterblocks + 360×45 + 240×30 radiators | air cannot handle 4×300 W; a block dissipates ~300 W per card |
| PSU | 2 kW, dedicated line | idle ~200 W · load 700–800 W · peak 1350 W |
| RAM | **256 GB** DDR4-2400 RDIMM (8×32, two sockets, 8 channels) | the second tier — MoE experts live in RAM, see [hybrid mode](06-hybrid-mode.md); the 1Cat-LLM reference rig consumes ~62 GB host RAM |
| Disk | NVMe 4–8 GB/s | model checkpoints are 20–90 GB |
| OS | Ubuntu 24.04+ | glibc ≥ 2.38, GLIBCXX ≥ 3.4.30 |

## BIOS/UEFI checklist

UEFI boot (CSM off) · **Above 4G Decoding** (cards invisible without it) · **Resizable BAR** ·
bifurcation x8/x8 for a single-slot setup.

## Assembly gotchas

- SXM2 seating: screws down fully, then the 16 central screws exactly **two full turns CCW**;
  after load, check NVLink ECC counters (`nvidia-smi nvlink -e`) — zeros are the goal.
- Washer/spring kits ship incomplete — count per card.
- Waterblocks: X-pattern paste, 5 mm VRM pads, 24-hour leak test before powering GPUs.
- Static-pressure fans (Arctic P12/P8); big slow case fans beat the “lawnmower” whine.
- SXM2 modules idle at ~42 W each — they do not power-save.
- `nvidia-smi -pl 250` barely costs performance and cuts the 1350 W peak to ~1000 W.

## Software stack

NVIDIA **580.x** — the last Volta driver (freeze it, keep a tarball); CUDA 12.8 (CUDA 13 dropped
Volta); Python 3.12 + uv; llama.cpp + SM70 forks; 1Cat-LLM v1.5.3. Details in
[03-engines](03-engines.md).

## Risks

Ollama/upstream vLLM/PyTorch left Volta → build on llama.cpp + 1Cat-LLM; 1Cat stopping → the GGUF
queue is the fallback; V100 prices rising → buy 32GB modules now; NVLink errors under load → ECC
counters after every stress test.

---
#local-llm #v100 #sxm2 #hardware #watercooling
