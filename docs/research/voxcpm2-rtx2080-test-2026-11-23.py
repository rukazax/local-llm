# Приёмка VoxCPM2 на RTX 2080 Max-Q (8 ГБ): тот же набор фраз, что у TeraTTSv2, плюс 3 варианта Voice Design.
# Запуск на боксе 192.168.88.20 в venv на Python 3.10 (torch 2.5.1+cu124, dtype в config.json переключён bfloat16→float16).

import os, sys, json, time
import numpy as np, torch, soundfile as sf
from voxcpm import VoxCPM

MODEL = r"C:\tts\models\VoxCPM2"
OUT = r"C:\tts\voxcpm-out"
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

for i, (label, text) in enumerate(PHRASES):
    t = time.time()
    wav = np.asarray(m.generate(text=text, cfg_value=2.0, inference_timesteps=10, normalize=True))
    el = time.time() - t
    dur = len(wav) / sr
    sf.write(os.path.join(OUT, f"{i:02d}_{label}.wav"), wav, sr)
    print(json.dumps({"event": "synth", "i": i, "label": label, "chars": len(text),
                      "synth_s": round(el, 2), "audio_s": round(dur, 2),
                      "rtf": round(el / dur, 3),
                      "vram_peak_mb": round(torch.cuda.max_memory_allocated() / 2**20)}, ensure_ascii=False), flush=True)

DESIGN = [
 ("design_dry_female", "сухой женский дикторский голос, нейтральная интонация"),
 ("design_warm_male",  "спокойный низкий мужской голос, лёгкая ирония"),
 ("design_excited",    "взволнованный молодой мужской голос, громко, азартно"),
]
TEXT = "Сеня, ты чего замер? Гущин шагнул ближе и положил ладонь на поручень."
for tag, ctrl in DESIGN:
    t = time.time()
    wav = np.asarray(m.generate(text=f"({ctrl}){TEXT}", cfg_value=2.0, inference_timesteps=10, normalize=True))
    el = time.time() - t
    dur = len(wav) / sr
    sf.write(os.path.join(OUT, tag + ".wav"), wav, sr)
    print(json.dumps({"event": "design", "tag": tag, "control": ctrl,
                      "synth_s": round(el, 2), "audio_s": round(dur, 2), "rtf": round(el / dur, 3),
                      "vram_peak_mb": round(torch.cuda.max_memory_allocated() / 2**20)}, ensure_ascii=False), flush=True)

print(json.dumps({"event": "done", "vram_peak_mb": round(torch.cuda.max_memory_allocated() / 2**20)}), flush=True)
