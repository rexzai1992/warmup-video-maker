"""Kokoro TTS helper (Apache-2.0, OK for commercial use). Runs inside .tts-venv (Python 3.10-3.12 + torch).

  .tts-venv/Scripts/python tools/tts_kokoro.py "Jump! Jump!" en out.wav [voice] [speed]
  .tts-venv/Scripts/python tools/tts_kokoro.py serve          # used by engine/warmup.py

serve mode: one JSON job per stdin line {"text","lang","voice","speed","out"}; answers "ok" or "err <msg>" per line,
so the model loads once for the whole soundtrack.
"""
import json, sys, warnings

warnings.filterwarnings("ignore")
import numpy as np
import soundfile as sf
from kokoro import KPipeline

SR = 24000
LANG_CODE = {"en": "a", "ja": "j"}           # a = American English, j = Japanese
DEFAULT_VOICE = {"en": "af_heart", "ja": "jf_alpha"}
_pipes = {}


def synth(text, lang="en", voice=None, speed=1.08, out="out.wav"):
    code = LANG_CODE[lang]
    if code not in _pipes:
        _pipes[code] = KPipeline(lang_code=code, repo_id="hexgrad/Kokoro-82M")
    parts = [a.numpy() if hasattr(a, "numpy") else np.asarray(a)
             for _, _, a in _pipes[code](text, voice=voice or DEFAULT_VOICE[lang], speed=float(speed))]
    sf.write(out, np.concatenate(parts) if parts else np.zeros(SR // 10, np.float32), SR)


def serve():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            j = json.loads(line)
            synth(j["text"], j.get("lang", "en"), j.get("voice"), j.get("speed", 1.08), j["out"])
            print("ok", flush=True)
        except Exception as e:                           # keep serving; caller falls back for this line
            print("err " + str(e).replace("\n", " "), flush=True)


if __name__ == "__main__":
    if sys.argv[1:2] == ["serve"]:
        serve()
    else:
        a = sys.argv[1:]
        synth(a[0], a[1], a[3] if len(a) > 3 else None, a[4] if len(a) > 4 else 1.08, a[2])
