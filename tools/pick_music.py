"""Check candidate songs and pick the best ones for each chapter.

  1. Download candidates (YouTube Audio Library) anywhere, e.g. Downloads
     python tools/pick_music.py --scan [folder ...]   -> copies new songs (last 3 days) into music/inbox/<version>/
     (or put them in music/inbox/school/ and music/inbox/japan/ yourself)
  2. python tools/pick_music.py            -> table + suggestion
  3. python tools/pick_music.py --apply    -> copies the picks to music/<version>/ch1..ch5 + calm

Good fit = tempo needs little stretching to reach 120 BPM (beats stay natural), long enough, steady beat.
"""
import pathlib, re, shutil, sys, time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
import music  # noqa: E402

EXTS = music.EXTS


def info(f, ffmpeg):
    import librosa
    y = music.decode(f, ffmpeg, sr=22050, ch=1)[:, 0]
    dur = len(y) / 22050
    tempo, _ = librosa.beat.beat_track(y=y, sr=22050)
    bpm = float(np.atleast_1d(tempo)[0])
    hop = 128
    env = librosa.onset.onset_strength(y=y, sr=22050, hop_length=hop)
    tt = np.arange(len(env)) * hop / 22050
    e = env - env.mean()
    cand = np.arange(bpm * 0.97, bpm * 1.03, 0.01)
    sc = [abs(np.dot(e, np.exp(-2j * np.pi * (c / 60) * tt))) for c in cand]
    bpm = float(cand[int(np.argmax(sc))])
    steady = float(max(sc) / (np.abs(e).sum() + 1e-9))      # how strong/regular the pulse is (0..1)
    eff = music.grid_bpm(bpm)
    stretch = 120 / eff - 1
    rms = float(np.sqrt(np.mean(y ** 2)))
    return dict(file=f, dur=dur, bpm=bpm, eff=eff, stretch=stretch, steady=steady, rms=rms,
                energy=float(np.mean(env)))


def score_upbeat(r):
    s = 1.0 - min(1, abs(r["stretch"]) / 0.25)          # 0% stretch best, 25%+ worst
    s += 0.6 * min(1, r["steady"] / 0.15)                # clear beat
    s += 0.4 * min(1, r["energy"] / 1.5)                 # energetic
    s -= 0.5 if r["dur"] < 75 else 0                     # very short = lots of looping
    return s


def pick(version, ffmpeg):
    inbox = ROOT / "music" / "inbox" / version
    files = sorted(f for f in inbox.glob("*") if f.suffix.lower() in EXTS) if inbox.exists() else []
    if not files:
        print(f"[{version}] no songs in {inbox.relative_to(ROOT)}")
        return None
    rows = [info(f, ffmpeg) for f in files]
    print(f"\n[{version}] {len(rows)} songs")
    print(f"  {'song':42s} {'len':>5s} {'BPM':>6s} {'stretch':>8s} {'beat':>5s} {'energy':>6s}")
    for r in sorted(rows, key=lambda r: -r["energy"]):
        print(f"  {r['file'].name[:42]:42s} {r['dur'] / 60:4.1f}m {r['bpm']:6.1f} {r['stretch'] * 100:+7.0f}% "
              f"{r['steady']:5.2f} {r['energy']:6.2f}")
    calm = min(rows, key=lambda r: (r["energy"], -r["dur"]))
    up = sorted([r for r in rows if r is not calm], key=score_upbeat, reverse=True)[:5]
    up.sort(key=lambda r: r["energy"])                    # build up: ch1 medium ... ch4 highest
    order = [up[i] for i in (1, 2, 3, 4, 0) if i < len(up)] if len(up) == 5 else up
    picks = {f"ch{i + 1}": r for i, r in enumerate(order)}
    picks["calm"] = calm
    print("  suggestion:")
    for k, r in picks.items():
        warn = "  (big tempo change)" if abs(r["stretch"]) > 0.2 else ""
        print(f"    {k:5s} <- {r['file'].name}{warn}")
    return picks


JAPAN_WORDS = ("japan", "tokyo", "kyoto", "taiko", "koto", "shamisen", "sakura", "matsuri", "festival", "asia",
               "zen", "ninja", "samurai", "bamboo", "fuji", "geisha", "oriental", "shakuhachi", "kimono", "edo")
RIPPED = re.compile(r"\[[A-Za-z0-9_-]{11}\]")       # "... [dQw4w9WgXcQ].mp3" = ripped from a YouTube video


def scan(folders, days=3):
    """Collect songs downloaded in the last `days` days from the given folders (default: Downloads)
    into music/inbox/<school|japan>/. Japan-sounding names go to japan, the rest to school."""
    since = time.time() - days * 86400
    n = 0
    for folder in folders:
        for f in sorted(pathlib.Path(folder).expanduser().glob("*")):
            if f.suffix.lower() not in EXTS or f.stat().st_mtime < since:
                continue
            if RIPPED.search(f.name):
                print(f"  SKIPPED (ripped from a YouTube video, not safe for a monetized channel): {f.name}")
                continue
            v = "japan" if any(w in f.name.lower() for w in JAPAN_WORDS) else "school"
            dest = ROOT / "music" / "inbox" / v
            dest.mkdir(parents=True, exist_ok=True)
            if not (dest / f.name).exists():
                shutil.copy2(f, dest / f.name)
                n += 1
            print(f"  {v:6s} <- {f.name}")
    print(f"  {n} new song(s) copied into music/inbox/")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ff = shutil.which("ffmpeg") or sys.exit("ffmpeg not found")
    if "--scan" in sys.argv:
        extra = [a for a in sys.argv[sys.argv.index("--scan") + 1:] if not a.startswith("--")]
        scan(extra or [pathlib.Path.home() / "Downloads"])
    for v in ("school", "japan"):
        picks = pick(v, ff)
        if picks and "--apply" in sys.argv:
            dest = ROOT / "music" / v
            for k, r in picks.items():
                for old in dest.glob(f"{k}.*"):
                    old.unlink()
                shutil.copy2(r["file"], dest / f"{k}{r['file'].suffix.lower()}")
            print(f"  copied to music/{v}/ - now run: python make_video.py {v} --new-audio")


if __name__ == "__main__":
    main()
