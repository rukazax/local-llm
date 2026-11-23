import time, json, resource
from transformers import AutoModel

PHRASES = [
 ("dialog",   "Сеня, ты чего замер? Гущин шагнул ближе и положил ладонь на поручень.", "ru_m5", 1.0),
 ("question", "Ветров, ты слышишь меня?", "ru_f1", 1.0),
 ("exclaim",  "Да это же конец всему!", "ru_m5", 1.0),
 ("system",   "Навык Сканирование повышен до второго уровня.", "ru_f1", 1.0),
 ("numbers",  "В отсеке осталось 21 ящик и 42 контейнера.", "ru_m5", 1.0),
 ("swear",    "Ёшкин кот, опять замкнуло.", "ru_m5", 1.0),
 ("whisper",  "Не включай свет, они рядом.", "ru_f1", 1.15),
 ("dry",      "Доклад принят. Продолжайте движение.", "ru_f1", 1.0),
 ("slow",     "Сеня, ты чего замер? Гущин шагнул ближе.", "ru_m5", 1.25),
]

t0 = time.time()
tts = AutoModel.from_pretrained("/srv/apps/models/terattsv2", trust_remote_code=True,
                                provider="CPUExecutionProvider", threads=6)
print(json.dumps({"load_s": round(time.time()-t0, 1)}), flush=True)

for i, (label, txt, voice, ds) in enumerate(PHRASES):
    t = time.time()
    wav = tts.generate_speech(f"<ru>{txt}</ru>", voice=voice, duration_scale=ds)
    el = time.time() - t
    dur = len(wav) / 44100
    path = f"/tmp/teratts/{i:02d}_{label}.wav"
    tts.save_wav(path, wav)
    print(json.dumps({"i": i, "label": label, "chars": len(txt), "synth_s": round(el, 2),
                      "audio_s": round(dur, 2), "rtf": round(el / dur, 3),
                      "voice": voice, "ds": ds}, ensure_ascii=False), flush=True)

print(json.dumps({"maxrss_mb": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)}))
print("normalize:", tts.normalize_text("<ru>В отсеке осталось 21 ящик и 42 контейнера. Сеня, ты чего замер?</ru>"))
