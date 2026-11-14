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
FPS = 30
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
    # AI scenes from Google Flow override the stock clip when present: footage/flow/<name>/<id>.mp4
    flow_dir = FOOTAGE / "flow" / name
    for s in tl["segments"]:
        f = flow_dir / f"{s['id']}.mp4"
        if f.exists():
            s["clip"] = f"flow/{name}/{s['id']}"
            s["clipStart"] = 0
            if s["scene"] not in ("card",):
                s["scene"] = "footage"
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
    clips = sorted({s["clip"] for s in tl["segments"] if isinstance(s.get("clip"), int)})
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
        if not src.exists():
            continue
        srcs = [src]
        if str(clip).startswith("flow/"):                    # optional 2nd Flow clip: <id>_2.mp4, chained after
            second = src.with_name(f"{src.stem}_2.mp4")
            if second.exists():
                srcs.append(second)
        d = FRAMES / str(clip)
        if d.exists() and any(d.iterdir()):
            newest = max(f.stat().st_mtime for f in srcs)
            if newest <= d.stat().st_mtime:                  # frames are up to date
                continue
            shutil.rmtree(d)                                 # clip was replaced: extract again
        d.mkdir(parents=True, exist_ok=True)
        # soft blur + denoise: makes the cartoon pop and keeps the MP4 small
        vf = ("fps=30,scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,"
              "gblur=sigma=1.4,hqdn3d=3:3:4:4,eq=saturation=1.15:contrast=1.05")
        for f in srcs:
            subprocess.run([ffmpeg(), "-loglevel", "error", "-i", str(f), "-t", str(dur), "-vf", vf, "-q:v", "5",
                            "-start_number", str(len(os.listdir(d)) + 1), str(d / "%05d.jpg")], check=True)
        print(f"  frames for clip {clip}: {len(os.listdir(d))}")


def import_flow(name):
    """Move downloaded Flow clips from footage/flow_inbox/<name>/ to footage/flow/<name>/<id>.mp4.

    A file named after a part id (e.g. stretch.mp4 or stretch_2.mp4) goes to that part. Every other file is matched,
    oldest download first, to the parts in prompt-list order that don't have a clip yet.
    """
    sys.path.insert(0, str(ROOT / "tools"))
    from make_flow_prompts import prompt_list
    ids = [pid for pid, _, _ in prompt_list(name)]
    inbox = FOOTAGE / "flow_inbox" / name
    dest = FOOTAGE / "flow" / name
    inbox.mkdir(parents=True, exist_ok=True)
    dest.mkdir(parents=True, exist_ok=True)
    files = sorted(inbox.glob("*.mp4"), key=lambda f: f.stat().st_mtime)
    if not files:
        print(f"  no .mp4 files in {inbox.relative_to(ROOT)} - download clips from Flow there first")
        return
    moves, by_order = [], []
    for f in files:
        base = f.stem[:-2] if f.stem.endswith("_2") else f.stem
        (moves.append((f, f.stem)) if base in ids else by_order.append(f))
    taken = {stem for _, stem in moves}
    free = [i for i in ids if i not in taken and not (dest / f"{i}.mp4").exists()]
    for f in by_order:
        if not free:
            print(f"  !! {f.name}: every part already has a clip - left in the inbox")
            continue
        moves.append((f, free.pop(0)))
    for f, stem in moves:
        target = dest / f"{stem}.mp4"
        if target.exists():
            target.unlink()
        shutil.move(str(f), str(target))
        shutil.rmtree(FRAMES / "flow" / name / stem.removesuffix("_2"), ignore_errors=True)
        print(f"  {f.name} -> flow/{name}/{target.name}")
    have = sum((dest / f"{i}.mp4").exists() for i in ids)
    left = [i for i in ids if not (dest / f"{i}.mp4").exists()]
    print(f"  {have}/{len(ids)} parts have a Flow clip." + (f" Next to make: {', '.join(left[:5])}" if left else ""))


# ------------------------------------------------------------------ voice
# Kokoro TTS (Apache-2.0: fine for monetized videos). (voice, speed) per language.
VOICE_KOKORO = {"en": ("af_heart", 1.08), "ja": ("jf_alpha", 1.0)}
# Fallbacks only when .tts-venv is missing. Don't publish monetized videos with these (licence unclear / Apple: not allowed).
VOICE_SAY = {"en": ("Samantha", "190"), "ja": ("Kyoko", "200")}
VOICE_EDGE = {"en": "en-US-AnaNeural", "ja": "ja-JP-NanamiNeural"}
TTS_PY = ROOT / ".tts-venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
_kokoro = None


def _kokoro_say(text, lang, out):
    """Ask the long-running Kokoro helper (tools/tts_kokoro.py serve) for one line. False if it failed."""
    global _kokoro
    if _kokoro is None:
        _kokoro = subprocess.Popen([str(TTS_PY), str(ROOT / "tools" / "tts_kokoro.py"), "serve"],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding="utf-8")
    voice, speed = VOICE_KOKORO[lang]
    _kokoro.stdin.write(json.dumps({"text": text, "lang": lang, "voice": voice, "speed": speed,
                                    "out": str(out)}) + "\n")
    _kokoro.stdin.flush()
    ans = _kokoro.stdout.readline().strip()
    if ans != "ok":
        print(f"  !! Kokoro failed on '{text}': {ans}")
    return ans == "ok"


def voice_engine():
    return "kokoro" if TTS_PY.exists() else ("say" if shutil.which("say") else "edge")


def voice_clip(text, lang="en"):
    eng = voice_engine()
    tag = f"kokoro|{'|'.join(map(str, VOICE_KOKORO[lang]))}|" if eng == "kokoro" else ""
    key = hashlib.md5(f"{tag}{lang}|{text}".encode("utf-8")).hexdigest()[:14]
    wav = VOICES / f"{lang}_{key}.wav"
    if not wav.exists():
        VOICES.mkdir(exist_ok=True)
        tmp = VOICES / f"tmp_{key}"
        if eng == "kokoro":
            tmp = tmp.with_suffix(".wav")
            if not _kokoro_say(text, lang, tmp):
                sys.exit("Kokoro voice failed (see above). Fix .tts-venv, or delete it to use the fallback voice.")
        elif shutil.which("say"):                            # macOS built-in voices
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
    if voice_engine() != "kokoro":
        print("  !! WARNING: Kokoro voice not installed (run tools/setup_voice.bat). Using the fallback voice -"
              " don't upload this soundtrack to a monetized channel.")
    import music
    ext, covered = music.build(tl, ROOT / "music" / name, ffmpeg(), Synth.frozen_at)
    if ext is None:
        print(f"  no tracks in music/{name}/ - using the generated music")
    else:
        print(f"  real music on {len(covered)}/{len(tl['segments'])} parts (generated music on the rest)")
    syn = Synth(tl, voice_clip, ext, covered)
    out = AUDIO / f"{name}.m4a"
    AUDIO.mkdir(exist_ok=True)
    syn.render(out, ffmpeg())
    print(f"  soundtrack: {out.name} ({out.stat().st_size / 1e6:.1f} MB)")
    return out


# ------------------------------------------------------------------ video frames
def page_url(name):
    tl = load_timeline(name)
    flow = ",".join(s["id"] for s in tl["segments"] if str(s.get("clip", "")).startswith("flow/"))
    return (ENGINE / "index.html").as_uri() + f"?render=1&w={OUT_W}&tl=../timelines/{name}.js&flow={flow}"


def _clip_frame(seg, local_t):
    clip = seg.get("clip")
    d = FRAMES / str(clip) if clip else None
    if not d or not d.exists():
        return ""
    n = len(os.listdir(d))
    if n == 0:
        return ""
    i = int((local_t + seg.get("clipStart", 0)) * FPS)
    period = max(1, 2 * n - 2)                     # ping-pong loop for short clips
    i %= period
    if i >= n:
        i = period - i
    return "data:image/jpeg;base64," + base64.b64encode((d / f"{i + 1:05d}.jpg").read_bytes()).decode()


def bg_data(tl, t):
    segs = tl["segments"]
    k = len(segs) - 1
    for j, s in enumerate(segs):
        if t < s["start"] + s["dur"]:
            k = j
            break
    seg = segs[k]
    st = t - seg["start"]
    bg = _clip_frame(seg, st)
    bg2 = _clip_frame(segs[k - 1], segs[k - 1]["dur"] + st) if k > 0 and st < 0.6 else ""
    return bg, bg2


def _open(p, name):
    # GPU drawing for the hidden Chrome (default headless Chrome draws in software)
    args = ["--use-angle=d3d11", "--enable-gpu", "--ignore-gpu-blocklist", "--enable-gpu-rasterization",
            "--enable-accelerated-2d-canvas"] if GPU_DRAW else []
    browser = p.chromium.launch(args=args)
    page = browser.new_page(viewport={"width": OUT_W, "height": OUT_H})
    page.goto(page_url(name))
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(600)
    return browser, page


def _grab(page, tl, t):
    bg, bg2 = bg_data(tl, t)
    data = page.evaluate("([t, bg, bg2]) => frameJPEG(t, 0.9, bg, bg2)", [t, bg, bg2])
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


ENC_CPU = ["-c:v", "libx264", "-preset", "medium", "-crf", "28", "-pix_fmt", "yuv420p", "-g", "50"]
# NVIDIA hardware encoder: about 12 MB per minute at CQ 33 (owner target), frees the CPU for drawing frames
ENC_NVENC = ["-c:v", "h264_nvenc", "-preset", "p6", "-tune", "hq", "-rc", "vbr", "-cq", "33", "-b:v", "0",
             "-spatial-aq", "1", "-pix_fmt", "yuv420p", "-g", "50"]
# GPU use can be switched off with WARMUP_GPU=0 (or only one part: WARMUP_GPU_ENC=0 / WARMUP_GPU_DRAW=0)
GPU_ENC = os.environ.get("WARMUP_GPU", "1") != "0" and os.environ.get("WARMUP_GPU_ENC", "1") != "0"
GPU_DRAW = os.environ.get("WARMUP_GPU", "1") != "0" and os.environ.get("WARMUP_GPU_DRAW", "1") != "0"
_nvenc_ok = None


def enc():
    """Video encoder args: NVENC when an NVIDIA GPU is there (checked once), else libx264."""
    global _nvenc_ok
    if GPU_ENC and _nvenc_ok is None:
        r = subprocess.run([ffmpeg(), "-v", "error", "-f", "lavfi", "-i", "color=s=640x360", "-frames:v", "3",
                            "-c:v", "h264_nvenc", "-f", "null", "-"], capture_output=True)
        _nvenc_ok = r.returncode == 0
    return ENC_NVENC if GPU_ENC and _nvenc_ok else ENC_CPU


ENC = ENC_CPU


def _render_part(job):
    from playwright.sync_api import sync_playwright
    name, k, f0, f1 = job
    tl = load_timeline(name)
    out = PARTS / name / f"part{k:02d}.mp4"
    proc = subprocess.Popen([ffmpeg(), "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
                             "-i", "-", *enc(), str(out)], stdin=subprocess.PIPE)
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


CHAPTER_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}


def chapter_ranges(tl):
    """[{ch, title, start, end, first}] - each chapter runs from its card to the next card (last one to the end)."""
    segs = tl["segments"]
    cards = [i for i, s in enumerate(segs) if s["scene"] == "card"]
    out = []
    for n, i in enumerate(cards):
        j = cards[n + 1] if n + 1 < len(cards) else len(segs)
        out.append({"ch": segs[i]["ch"], "title": segs[i]["story"], "start": segs[i]["start"],
                    "end": segs[j]["start"] if j < len(segs) else tl["total"],
                    "first": segs[i + 1] if i + 1 < len(segs) else segs[i]})
    return out


def _card_audio(kind, dur, tl):
    from synth import Synth
    syn = Synth(tl, voice_clip)
    n = int(dur * SR)
    x = np.zeros(n, np.float32)

    def add(t, y, g):
        i = int(t * SR); j = min(n, i + len(y)); x[i:j] += (y[: j - i] * g).astype(np.float32)
    if kind == "intro":
        add(0.0, syn.whoosh(0.5), 0.8)
        add(0.25, voice_clip("Stand up! Let's move!"), 1.3)
        add(dur - 2.0, syn.riser(2.0), 0.8)
    else:
        add(0.0, syn.crash(), 0.6)
        add(0.0, syn.chime(84), 0.8); add(0.25, syn.chime(88), 0.6)
        add(0.4, voice_clip("Great job! Subscribe for more!"), 1.3)
        x[-int(0.6 * SR):] *= np.linspace(1, 0, int(0.6 * SR))
    x = np.tanh(x / max(1e-6, np.abs(x).max()) * 1.2) * 0.85
    return x


def _render_card(name, kind, dur, ch, big, small, top, bg, out):
    from playwright.sync_api import sync_playwright
    tl = load_timeline(name)
    wav = out.with_suffix(".wav")
    a = _card_audio(kind, dur, tl)
    with wave.open(str(wav), "w") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.repeat(a[:, None], 2, 1) * 32767).astype(np.int16).tobytes())
    proc = subprocess.Popen([ffmpeg(), "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
                             "-i", "-", "-i", str(wav), *enc(), "-c:a", "aac", "-b:a", "128k", "-ar", str(SR),
                             "-shortest", str(out)], stdin=subprocess.PIPE)
    with sync_playwright() as p:
        browser, page = _open(p, name)
        for i in range(int(dur * FPS)):
            data = page.evaluate("([k, st, d, ch, big, small, top, bg]) => ytCardJPEG(k, st, d, ch, big, small, top, bg)",
                                 [kind, i / FPS, dur, ch, big, small, top, bg])
            proc.stdin.write(base64.b64decode(data.split(",", 1)[1]))
        browser.close()
    proc.stdin.close()
    proc.wait()
    wav.unlink()


def export_chapters(name, workers=None, only=None):
    """output/youtube/<name>_ch<N>.mp4: 3 s intro card + the chapter + 4 s outro card."""
    tl = load_timeline(name)
    ydir = OUT / "youtube"
    ydir.mkdir(parents=True, exist_ok=True)
    made = []
    for c in chapter_ranges(tl):
        if only and c["ch"] not in only:
            continue
        print(f"\n  chapter {c['ch']}: {c['title']} ({(c['end'] - c['start']) / 60:.1f} min)")
        tmp = ydir / f".tmp_{name}_{c['ch']}"
        tmp.mkdir(exist_ok=True)
        bg = _clip_frame(c["first"], 2.0)
        top = f"CHAPTER {c['ch']}"
        _render_card(name, "intro", 3.0, c["ch"], c["title"], "Stand up! Let's move!", top, bg, tmp / "intro.mp4")
        _render_card(name, "outro", 4.0, c["ch"], "GREAT JOB!", "Subscribe for more!", "", bg, tmp / "outro.mp4")
        body = render_video(name, workers, c["start"], c["end"])
        bd = c["end"] - c["start"]
        out = ydir / f"{name}_ch{c['ch']}.mp4"
        fc = (f"[1:a]afade=t=out:st={bd - 0.5:.2f}:d=0.5[ba];"
              "[0:v][0:a][1:v][ba][2:v][2:a]concat=n=3:v=1:a=1[v][a]")
        subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(tmp / "intro.mp4"), "-i", str(body),
                        "-i", str(tmp / "outro.mp4"), "-filter_complex", fc, "-map", "[v]", "-map", "[a]", *enc(),
                        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)], check=True)
        body.unlink()
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"  -> {out} ({out.stat().st_size / 1e6:.0f} MB)")
        made.append(out)
    return made


def render_video(name, workers=None, t0=0.0, t1=None):
    tl = load_timeline(name)
    total = tl["total"]
    t1 = min(total, t1 or total)
    sample = t0 > 0 or t1 < total
    F0, n = int(t0 * FPS), int((t1 - t0) * FPS)
    workers = workers or max(2, (os.cpu_count() or 4) // 2)
    if enc() is ENC_NVENC and workers > 8:
        # consumer NVIDIA cards only open a limited number of encoders at once (16 fails on an RTX 5070);
        # 8 is as fast as 12 here anyway because drawing frames is the slow part
        print(f"  (GPU encoder: using 8 workers instead of {workers})")
        workers = 8
    (PARTS / name).mkdir(parents=True, exist_ok=True)
    chunk = (n + workers - 1) // workers
    jobs = [(name, k, F0 + k * chunk, F0 + min(n, (k + 1) * chunk)) for k in range(workers)]
    print(f"  rendering {n} frames ({n / FPS / 60:.1f} min) with {workers} workers"
          f" (encoder: {'NVIDIA GPU' if enc() is ENC_NVENC else 'CPU'}, drawing: {'GPU' if GPU_DRAW else 'CPU'})...")
    with ProcessPoolExecutor(workers) as ex:
        parts = list(ex.map(_render_part, jobs))
    lst = PARTS / name / "list.txt"
    lst.write_text("".join(f"file '{pathlib.Path(p).as_posix()}'\n" for p in parts))
    OUT.mkdir(exist_ok=True)
    out = OUT / (f"SAMPLE_{name}_{int(t0)}s-{int(t1)}s.mp4" if sample else f"{tl.get('output', name)}.mp4")
    audio = AUDIO / f"{name}.m4a"
    cmd = [ffmpeg(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst)]
    if audio.exists():
        cmd += ["-ss", str(t0), "-t", str(t1 - t0), "-i", str(audio), "-map", "0:v", "-map", "1:a",
                "-c:a", "aac", "-b:a", "128k", "-af", "afade=in:d=0.3", "-shortest"]
    cmd += ["-c:v", "copy", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    shutil.rmtree(PARTS / name, ignore_errors=True)
    print(f"\n  DONE: {out}  ({out.stat().st_size / 1e6:.0f} MB)")
    return out
