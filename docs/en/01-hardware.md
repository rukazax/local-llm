# 01 · Hardware: configuration and assembly

**EN** · [Русский](../ru/01-hardware.md) · [← README](../../README.md)

## Final configuration

| Component | Choice | Why |
|---|---|---|
| GPU | **4× Tesla V100 SXM2 32GB** on one carrier board | 128 GB HBM2, homogeneous; TP4 without compromise |
| Carrier | factory 4×SXM2 module with **full NVLink**, Broadcom PEX8748 switch | NVLink 300 GB/s GPU↔GPU; **one PCIe 3.0 x16** uplink, **2× 8-pin up to 1200 W**. Without NVLink — ~half the speed (57 vs ~100 tok/s measured) |
| CPU | **2× Intel Xeon E5-2695 v4** — 18C/36T, 2.1–3.3 GHz, 45 MB L3, 120 W, 40 PCIe 3.0 lanes | 36 physical cores for the CPU side of the hybrid and for services; DDR4-2400 controller |
| Motherboard | **Atermiter X99 Dual X99** (ZX-DU99D4 family), E-ATX, C612, 2× LGA2011-3 | 8× DDR4 DIMM = 256 GB, 2× M.2 NVMe, two full-size x16 |
| Cooling | **water loop** (bought 22 Nov): Enermax ELC-NC200RGB 400 ml pump, 9.5/12.7 mm PVC tubing, **24 G1/4 fittings**, leak-guard fitting, **6× ARGB 120 mm**, **2× 360 mm radiators, ТСРП-ХП65-360** (2× 5 885 ₽) + 2× LGA2011-3 tower coolers on the CPUs | air cannot handle 4×300 W in a closed box; the loop covers 240 W of CPU with headroom for GPU blocks |
| PSU | **1600 W**, dedicated line; the module on 2× 8-pin from separate rails | idle ~250 W (V100 never power-saves, ~42 W/card) · load 900–1100 W · peak ~1400 W while a model loads |
| RAM | **256 GB = 8× 32 GB DDR4-2400 REG ECC (RDIMM 2Rx4)** | the second tier — MoE experts live in RAM, see [hybrid mode](06-hybrid-mode.md); 1 DIMM per channel, **76.8 GB/s per socket** |
| Disk | NVMe 4–8 GB/s | model checkpoints are 20–90 GB |
| OS | Ubuntu 24.04+ | glibc ≥ 2.38, GLIBCXX ≥ 3.4.30 |

**How the TP4 set is assembled (status 22 Nov):** either a ready-made 4×SXM2 32GB NVLink module,
or the **4-slot SXM2 NVLink PCB (one kit, bought)** plus **4× V100 SXM2 32GB** — three cards in hand,
the fourth to be bought together with RAM. The **V100 SXM2 16GB cards that come with the carrier are
not used** in this build; the separate V100 32G PCIe card is not part of TP4.

**Why the 16 GB cards do not fit:** TP4 splits weights into four equal shards, so the cards must be
identical — 2×16 + 2×32 puts the smallest shard in every layer and caps you at 64 GB instead of 128 GB.
The pair of 16 GB cards is kept for carrier bring-up (links, BIOS, power before the expensive cards
arrive) and as a spare set.

### Platform memory ceiling

- The E5 v4 controller officially supports **up to 1.5 TB** (with 128 GB 3DS LRDIMMs),
  DDR4-1600/1866/2133/**2400**, 4 channels, 76.8 GB/s per socket
  ([Intel ARK](https://www.intel.com/content/www/us/en/products/sku/91316/intel-xeon-processor-e52695-v4-45m-cache-2-10-ghz/specifications.html)).
- The limit is set by **the board and its BIOS**: 8 slots × **32 GB** = **256 GB**. It does not bring
  up LRDIMM/3DS, so 32 GB per slot is the practical maximum.
- 2666/2933/3200 modules are not "incompatible" — they downclock to 2400 by JEDEC. Paying above
  2400 buys nothing here.

## BIOS/UEFI checklist

UEFI boot (CSM off) · **Above 4G Decoding** (cards invisible without it) · **Re-Size BAR**
(disable and retest P2P if the board misbehaves) · IOMMU on (off if P2P breaks) ·
**Node Interleaving Disabled** (otherwise two-socket NUMA locality is lost) · memory 2400 ·
Restore on AC loss · Secure Boot off · fans Performance.

Full walkthrough from unboxing to the first token — [07-build-and-launch](07-build-and-launch.md).

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
Volta); Python 3.12 + uv; llama.cpp + SM70 forks; 1Cat-vLLM v1.5.4 (see [08](08-1cat-vllm-nvfp4.md)). Details in
[03-engines](03-engines.md).

## Risks

Ollama/upstream vLLM/PyTorch left Volta → build on llama.cpp + 1Cat-LLM; 1Cat stopping → the GGUF
queue is the fallback; V100 prices rising → buy 32GB modules now; NVLink errors under load → ECC
counters after every stress test.

---
#local-llm #v100 #sxm2 #hardware #watercooling
