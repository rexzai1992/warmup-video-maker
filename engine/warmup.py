"""Warm-up video maker engine: footage download, soundtrack, frame rendering, MP4 encode.

Used by ../make_video.py. Everything is timed on a 120 BPM grid from a timeline file in ../timelines/,
so the moves, the music, the sound effects and the voice callouts stay on the beat.
"""
import base64, hashlib, json, os, shutil, subprocess, sys, urllib.request, wave, pathlib
from concurrent.futures import ProcessPoolExecutor

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENGINE = ROOT / "engine"
FOOTAGE = ROOT / "footage"
FRAMES = ROOT / ".frames"
PARTS = ROOT / ".parts"
VOICES = ROOT / "voice_cache"
AUDIO = ROOT / "audio"
OUT = ROOT / "output"
FPS = 25
OUT_W, OUT_H = 1280, 720
SR = 44100


# ------------------------------------------------------------------ timeline
def load_timeline(name):
    src = (ROOT / "timelines" / f"{name}.js").read_text(encoding="utf-8")
    body = src[src.index("{"): src.rindex("};") + 1]
    body = "\n".join(l for l in body.splitlines() if not l.strip().startswith(("/*", "//")))
    tl = json.loads(body)
    t = 0.0
    for s in tl["segments"]:
        s["start"] = t
        t += s["dur"]
    tl["total"] = t
    return tl


# ------------------------------------------------------------------ footage
def ffmpeg():
    exe = shutil.which("ffmpeg")
    if not exe:
        sys.exit("ffmpeg not found. Install it and make sure 'ffmpeg' works in a terminal (see README).")
    return exe


def download_footage(tl):
    """Free Mixkit stock clips (Mixkit License: free for commercial use, no attribution needed)."""
    FOOTAGE.mkdir(exist_ok=True)
    clips = sorted({s["clip"] for s in tl["segments"] if s.get("clip")})
    for c in clips:
        f = FOOTAGE / f"{c}.mp4"
        if f.exists() and f.stat().st_size > 10000:
            continue
        for res in ("720", "1080", "360"):
            url = f"https://assets.mixkit.co/videos/{c}/{c}-{res}.mp4"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=120) as r, open(f, "wb") as o:
                    shutil.copyfileobj(r, o)
                print(f"  downloaded clip {c} ({res}p)")
                break
            except Exception:
                continue
        else:
            print(f"  !! could not download clip {c} - that part will use a plain background")


def extract_frames(tl):
    need = {}
    for s in tl["segments"]:
        if s.get("clip"):
            need[s["clip"]] = max(need.get(s["clip"], 0), s.get("clipStart", 0) + s["dur"] + 1)
    for clip, dur in need.items():
        src = FOOTAGE / f"{clip}.mp4"
        d = FRAMES / str(clip)
        if not src.exists() or (d.exists() and any(d.iterdir())):
            continue
        d.mkdir(parents=True, exist_ok=True)
        # soft blur + denoise: makes the cartoon pop and keeps the MP4 small
        vf = ("fps=25,scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,"
              "gblur=sigma=1.4,hqdn3d=3:3:4:4,eq=saturation=1.15:contrast=1.05")
        subprocess.run([ffmpeg(), "-loglevel", "error", "-i", str(src), "-t", str(dur), "-vf", vf,
                        "-q:v", "5", str(d / "%05d.jpg")], check=True)
        print(f"  frames for clip {clip}: {len(os.listdir(d))}")


# ------------------------------------------------------------------ voice
VOICE_SAY = {"en": ("Samantha", "190"), "ja": ("Kyoko", "200")}
VOICE_EDGE = {"en": "en-US-AnaNeural", "ja": "ja-JP-NanamiNeural"}


def voice_clip(text, lang="en"):
    key = hashlib.md5(f"{lang}|{text}".encode("utf-8")).hexdigest()[:14]
    wav = VOICES / f"{lang}_{key}.wav"
    if not wav.exists():
        VOICES.mkdir(exist_ok=True)
        tmp = VOICES / f"tmp_{key}"
        if shutil.which("say"):                              # macOS built-in voices
            v, rate = VOICE_SAY[lang]
            tmp = tmp.with_suffix(".aiff")
            subprocess.run(["say", "-v", v, "-r", rate, "-o", str(tmp), text], check=True)
        else:                                                # Windows/Linux: free Microsoft neural voices
            tmp = tmp.with_suffix(".mp3")
            subprocess.run([sys.executable, "-m", "edge_tts", "--voice", VOICE_EDGE[lang], "--rate", "+8%",
                            "--text", text, "--write-media", str(tmp)], check=True)
        subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(tmp), "-ac", "1", "-ar", str(SR),
                        "-af", "silenceremove=start_periods=1:start_threshold=-45dB", str(wav)], check=True)
        tmp.unlink()
    with wave.open(str(wav)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


# ------------------------------------------------------------------ soundtrack
def build_audio(tl, name):
    from synth import Synth
    syn = Synth(tl, voice_clip)
    out = AUDIO / f"{name}.m4a"
    AUDIO.mkdir(exist_ok=True)
    syn.render(out, ffmpeg())
    print(f"  soundtrack: {out.name} ({out.stat().st_size / 1e6:.1f} MB)")
    return out


# ------------------------------------------------------------------ video frames
def page_url(name):
    return (ENGINE / "index.html").as_uri() + f"?render=1&w={OUT_W}&tl=../timelines/{name}.js"


def bg_data(tl, t):
    seg = tl["segments"][-1]
    for s in tl["segments"]:
        if t < s["start"] + s["dur"]:
            seg = s
            break
    clip = seg.get("clip")
    d = FRAMES / str(clip) if clip else None
    if not d or not d.exists():
        return ""
    n = len(os.listdir(d))
    if n == 0:
        return ""
    i = int((t - seg["start"] + seg.get("clipStart", 0)) * FPS)
    period = max(1, 2 * n - 2)                     # ping-pong loop for short clips
    i %= period
    if i >= n:
        i = period - i
    return "data:image/jpeg;base64," + base64.b64encode((d / f"{i + 1:05d}.jpg").read_bytes()).decode()


def _open(p, name):
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": OUT_W, "height": OUT_H})
    page.goto(page_url(name))
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(600)
    return browser, page


def _grab(page, tl, t):
    data = page.evaluate("([t, bg]) => frameJPEG(t, 0.9, bg)", [t, bg_data(tl, t)])
    return base64.b64decode(data.split(",", 1)[1])


def preview(name, times):
    from playwright.sync_api import sync_playwright
    tl = load_timeline(name)
    download_footage(tl); extract_frames(tl)
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser, page = _open(p, name)
        for t in times:
            f = OUT / f"preview_{name}_{float(t):06.1f}.jpg"
            f.write_bytes(_grab(page, tl, float(t)))
            print("  ", f)
        browser.close()


ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "28", "-pix_fmt", "yuv420p", "-g", "50"]


def _render_part(job):
    from playwright.sync_api import sync_playwright
    name, k, f0, f1 = job
    tl = load_timeline(name)
    out = PARTS / name / f"part{k:02d}.mp4"
    proc = subprocess.Popen([ffmpeg(), "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
                             "-i", "-", *ENC, str(out)], stdin=subprocess.PIPE)
    with sync_playwright() as p:
        browser, page = _open(p, name)
        for i in range(f0, f1):
            proc.stdin.write(_grab(page, tl, i / FPS))
            done = i - f0 + 1
            if done % 250 == 0 or i == f1 - 1:
                print(f"  worker {k}: {100 * done / (f1 - f0):5.1f}%", flush=True)
        browser.close()
    proc.stdin.close()
    proc.wait()
    return str(out)


def render_video(name, workers=None):
    tl = load_timeline(name)
    total = tl["total"]
    n = int(total * FPS)
    workers = workers or max(2, (os.cpu_count() or 4) // 2)
    (PARTS / name).mkdir(parents=True, exist_ok=True)
    chunk = (n + workers - 1) // workers
    jobs = [(name, k, k * chunk, min(n, (k + 1) * chunk)) for k in range(workers)]
    print(f"  rendering {n} frames ({total / 60:.1f} min) with {workers} workers...")
    with ProcessPoolExecutor(workers) as ex:
        parts = list(ex.map(_render_part, jobs))
    lst = PARTS / name / "list.txt"
    lst.write_text("".join(f"file '{pathlib.Path(p).as_posix()}'\n" for p in parts))
    OUT.mkdir(exist_ok=True)
    out = OUT / f"{tl.get('output', name)}.mp4"
    audio = AUDIO / f"{name}.m4a"
    cmd = [ffmpeg(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst)]
    if audio.exists():
        cmd += ["-i", str(audio), "-map", "0:v", "-map", "1:a", "-c:a", "copy", "-shortest"]
    cmd += ["-c:v", "copy", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    shutil.rmtree(PARTS / name, ignore_errors=True)
    print(f"\n  DONE: {out}  ({out.stat().st_size / 1e6:.0f} MB)")
    return out
