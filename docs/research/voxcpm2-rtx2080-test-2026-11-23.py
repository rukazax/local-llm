"""VoxCPM2 acceptance re-run on a WORKING torch/transformers pairing.

The first run (2026-11-23 morning) measured a broken environment: transformers
5.20.2 disabled torch 2.5.1 ("PyTorch >= 2.6 is required"), so the numbers
described the failure, not the model. This script refuses to run unless
transformers actually sees torch, then repeats the same phrase set plus a
4-vs-10 timestep comparison the broken run could not distinguish.
"""
import os, sys, json, time
import numpy as np, torch, soundfile as sf

import transformers
pre = {
    "event": "preflight",
    "python": sys.version.split()[0],
    "torch": torch.__version__,
    "torch_cuda": torch.cuda.is_available(),
    "transformers": transformers.__version__,
    "transformers_sees_torch": transformers.is_torch_available(),
    "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
}
print(json.dumps(pre), flush=True)
if not pre["transformers_sees_torch"]:
    print(json.dumps({"event": "FAIL", "reason": "transformers still cannot use torch (PyTorch >= 2.6 required); numbers would be meaningless"}), flush=True)
    sys.exit(2)
if not pre["torch_cuda"]:
    print(json.dumps({"event": "FAIL", "reason": "CUDA not available"}), flush=True)
    sys.exit(2)

from voxcpm import VoxCPM

MODEL = r"C:\tts\models\VoxCPM2"
OUT = r"C:\tts\voxcpm-out26"
os.makedirs(OUT, exist_ok=True)
torch.cuda.reset_peak_memory_stats()

t0 = time.time()
m = VoxCPM.from_pretrained(MODEL, load_denoiser=False, device="cuda", optimize=False, local_files_only=True)
load_s = time.time() - t0
sr = int(m.tts_model.sample_rate)
print(json.dumps({"event": "load", "load_s": round(load_s, 1), "sample_rate": sr,
                  "vram_after_load_mb": round(torch.cuda.max_memory_allocated() / 2**20)}), flush=True)

PHRASES = [
 ("dialog",   "Сеня, ты чего замер? Гущин шагнул ближе и положил ладонь на поручень."),
 ("question", "Ветров, ты слышишь меня?"),
 ("exclaim",  "Да это же конец всему!"),
 ("system",   "Навык Сканирование повышен до второго уровня."),
 ("numbers",  "В отсеке осталось 21 ящик и 42 контейнера."),
 ("swear",    "Ёшкин кот, опять замкнуло."),
 ("whisper",  "Не включай свет, они рядом."),
 ("dry",      "Доклад принят. Продолжайте движение."),
 ("story",    "Он открыл шкафчик, достал кружку и налил себе чаю."),
]


def synth(text, steps, tag):
    torch.cuda.reset_peak_memory_stats()
    t = time.time()
    wav = np.asarray(m.generate(text=text, cfg_value=2.0, inference_timesteps=steps, normalize=True))
    el = time.time() - t
    dur = len(wav) / sr
    sf.write(os.path.join(OUT, tag + ".wav"), wav, sr)
    rec = {"event": "synth", "tag": tag, "steps": steps, "chars": len(text),
           "synth_s": round(el, 2), "audio_s": round(dur, 2), "rtf": round(el / dur, 3),
           "s_per_1k_chars": round(el / max(len(text), 1) * 1000, 1),
           "vram_peak_mb": round(torch.cuda.max_memory_allocated() / 2**20)}
    print(json.dumps(rec, ensure_ascii=False), flush=True)
    return rec


main = [synth(text, 10, "t10_%02d_%s" % (i, label)) for i, (label, text) in enumerate(PHRASES)]

for steps in (4, 10):
    for i, (label, text) in enumerate(PHRASES[:3]):
        synth(text, steps, "cmp%d_%02d_%s" % (steps, i, label))

rtfs = sorted(r["rtf"] for r in main)
print(json.dumps({"event": "summary", "rtf_median": round(rtfs[len(rtfs)//2], 3),
                  "rtf_min": min(rtfs), "rtf_max": max(rtfs),
                  "vram_peak_mb": round(torch.cuda.max_memory_allocated() / 2**20)}), flush=True)
print(json.dumps({"event": "done"}), flush=True)
