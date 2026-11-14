"""Real music (e.g. YouTube Audio Library tracks) locked to the 120 BPM grid.

Put tracks in music/<version>/:  ch1.mp3 ... ch5.mp3 (one per chapter) and calm.mp3 (water breaks + cool-down).
Any of .mp3 .m4a .wav .ogg .flac works. Missing files fall back to the generated synth music for those parts.

Per track: detect tempo + beats (librosa) -> stretch to exactly 120 BPM (ffmpeg atempo, pitch unchanged) ->
find the bar downbeat -> cut a loop of whole 4-bar phrases from the loud part (skips quiet intros and fade-outs)
-> loop it across the chapter so every downbeat lands on the video's bar grid (chapters start on bar lines).
"""
import hashlib, pathlib, subprocess

import numpy as np

SR = 44100
BEAT = 0.5
BAR = 4 * BEAT
PHRASE = 4 * BAR                     # loops are whole 4-bar phrases (8 s)
EXTS = (".mp3", ".m4a", ".wav", ".ogg", ".flac")
TARGET_RMS = 0.12                    # about the synth music level (0.11) so voice + effects keep their balance
CACHE = pathlib.Path(__file__).resolve().parent.parent / ".music_cache"


def find_track(folder, key):
    for ext in EXTS:
        f = pathlib.Path(folder) / f"{key}{ext}"
        if f.exists():
            return f
    return None


def _atempo(ratio):
    """ffmpeg atempo only takes 0.5..2 per filter; chain for anything else."""
    parts = []
    while ratio > 2:
        parts.append(2.0); ratio /= 2
    while ratio < 0.5:
        parts.append(0.5); ratio /= 0.5
    parts.append(ratio)
    return ",".join(f"atempo={r:.6f}" for r in parts)


def decode(path, ffmpeg, af=None, sr=SR, ch=2):
    cmd = [ffmpeg, "-v", "error", "-i", str(path)]
    if af:
        cmd += ["-af", af]
    cmd += ["-f", "f32le", "-ac", str(ch), "-ar", str(sr), "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()


def analyse(path, ffmpeg):
    """(bpm, ratio, loop[n,2]) - the track stretched to 120 BPM, cut to whole phrases starting on a downbeat."""
    import librosa
    y = decode(path, ffmpeg, sr=22050, ch=1)[:, 0]
    tempo, _ = librosa.beat.beat_track(y=y, sr=22050)
    bpm = float(np.atleast_1d(tempo)[0])
    # librosa's tempo is rounded to its analysis grid (e.g. 103.4 for 104): a 0.6% error drifts ~0.3 s per minute.
    # Refine: the tempo whose pulse train best matches the onsets over the whole song (fine 0.005 BPM scan).
    hop = 128
    env = librosa.onset.onset_strength(y=y, sr=22050, hop_length=hop)
    env = env - env.mean()
    tt = np.arange(len(env)) * hop / 22050
    cand = np.arange(bpm * 0.97, bpm * 1.03, 0.005)
    score = [abs(np.dot(env, np.exp(-2j * np.pi * (c / 60) * tt))) for c in cand]
    bpm = float(cand[int(np.argmax(score))])
    while bpm < 90:                                        # half-time feel -> count it double
        bpm *= 2
    while bpm > 150:
        bpm /= 2
    ratio = 120.0 / bpm
    st = decode(path, ffmpeg, af=_atempo(ratio))           # stereo, 120 BPM now
    mono = st.mean(1)

    # beats of the stretched track, then the grid phase (where the beats fall inside 0.5 s)
    y2 = librosa.resample(mono, orig_sr=SR, target_sr=22050)
    env = librosa.onset.onset_strength(y=y2, sr=22050)
    _, bt = librosa.beat.beat_track(onset_envelope=env, sr=22050, start_bpm=120, tightness=400)
    times = librosa.frames_to_time(bt, sr=22050)
    if len(times) < 16:
        raise ValueError("couldn't find a steady beat")
    ang = np.angle(np.mean(np.exp(2j * np.pi * times / BEAT)))
    phase = (ang / (2 * np.pi) % 1) * BEAT                # first beat position in [0, 0.5)

    # downbeat: of the 4 beat positions in a bar, the one with the strongest onsets on average
    grid = np.arange(phase, len(mono) / SR - BEAT, BEAT)
    strength = np.interp(librosa.time_to_frames(grid, sr=22050), np.arange(len(env)), env)
    k = int(np.argmax([strength[i::4].mean() for i in range(4)]))
    bars = grid[k::4]

    # loud part only: bars whose RMS is at least 60% of the typical bar
    rms = np.array([np.sqrt(np.mean(mono[int(b * SR): int((b + BAR) * SR)] ** 2) + 1e-12) for b in bars])
    loud = np.where(rms >= 0.6 * np.median(rms))[0]
    b0, b1 = loud[0], loud[-1] + 1
    nphr = max(1, (b1 - b0) // 4)
    start = int(round(bars[b0] * SR))
    n = int(nphr * PHRASE * SR)
    loop = st[start: start + n]
    if len(loop) < n:
        loop = np.pad(loop, ((0, n - len(loop)), (0, 0)))
    loop *= TARGET_RMS / (np.sqrt(np.mean(loop ** 2)) + 1e-9)
    return bpm, ratio, loop.astype(np.float32)


def load_loop(path, ffmpeg):
    h = hashlib.md5(f"{path.resolve()}|{path.stat().st_mtime}|{path.stat().st_size}|v1".encode()).hexdigest()[:16]
    CACHE.mkdir(exist_ok=True)
    f = CACHE / f"{h}.npz"
    if f.exists():
        z = np.load(f)
        return float(z["bpm"]), float(z["ratio"]), z["loop"]
    bpm, ratio, loop = analyse(path, ffmpeg)
    np.savez(f, bpm=bpm, ratio=ratio, loop=loop)
    return bpm, ratio, loop


def tile(loop, n):
    """Repeat a phrase loop to n samples. Seams sit on a downbeat; a 5 ms dip there avoids clicks."""
    L = len(loop)
    out = np.tile(loop, (-(-n // L), 1))[:n].copy()
    f = int(0.005 * SR)
    w = np.linspace(0, 1, f, dtype=np.float32)[:, None]
    for p in range(L, n - f, L):
        out[p - f: p] *= w[::-1]
        out[p: p + f] *= w
    return out


def spans(tl, folder):
    """Consecutive parts that share a track: [(key, track, start, end, [segment indexes])]."""
    out = []
    for i, s in enumerate(tl["segments"]):
        key = "calm" if s.get("calm") and s["scene"] != "card" else f"ch{s['ch']}"
        if s.get("calm") and s["scene"] == "card":
            key = "calm" if find_track(folder, "calm") else key
        track = find_track(folder, key) or (find_track(folder, f"ch{s['ch']}") if key == "calm" else None)
        if out and out[-1][0] == key:
            out[-1][3] = s["start"] + s["dur"]
            out[-1][4].append(i)
        else:
            out.append([key, track, s["start"], s["start"] + s["dur"], [i]])
    return out


def build(tl, folder, ffmpeg, frozen_at):
    """Stereo music for the whole timeline + the set of segment indexes it covers (the rest uses synth music)."""
    folder = pathlib.Path(folder)
    if not folder.exists() or not any(find_track(folder, k) for k in ["calm"] + [f"ch{i}" for i in range(1, 6)]):
        return None, set()
    N = int((tl["total"] + 2) * SR)
    music = np.zeros((N, 2), np.float32)
    covered = set()
    tail = int(0.35 * SR)
    loops = {}
    for key, track, t0, t1, idx in spans(tl, folder):
        if track is None:
            continue
        if track not in loops:
            bpm, ratio, loop = load_loop(track, ffmpeg)
            loops[track] = loop
            print(f"  music {folder.name}/{track.name}: {bpm:.1f} BPM -> 120 (x{ratio:.3f}), "
                  f"{len(loop) / SR:.0f} s loop")
        i0, n = int(t0 * SR), int((t1 - t0) * SR) + tail
        x = tile(loops[track], n)
        x[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))[:, None]
        x[-tail:] *= np.linspace(1, 0, tail)[:, None]          # short tail under the next part's whoosh
        if key == "calm":
            x *= 0.8
        j = min(N, i0 + n)
        music[i0:j] += x[: j - i0]
        covered.update(idx)

    # FREEZE game: music almost silent on frozen beats (with 20 ms ramps so it doesn't click)
    g = np.ones(N, np.float32)
    for s in tl["segments"]:
        if s["move"] != "freeze":
            continue
        for b in range(int(round(s["dur"] / BEAT))):
            if frozen_at(s, b * BEAT + 0.01):
                a = int((s["start"] + b * BEAT) * SR)
                g[a: a + int(BEAT * SR)] = 0.05
    r = int(0.02 * SR)
    g = np.convolve(g, np.ones(r) / r, mode="same").astype(np.float32)
    music *= g[:, None]
    return music, covered
