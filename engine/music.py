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
TEMPO = 120.0                        # target BPM, set per video with set_bpm() (timeline "bpm")
BEAT = 60 / TEMPO
BAR = 4 * BEAT
PHRASE = 4 * BAR                     # loops are whole 4-bar phrases


def set_bpm(bpm):
    global TEMPO, BEAT, BAR, PHRASE
    TEMPO = float(bpm); BEAT = 60 / TEMPO; BAR = 4 * BEAT; PHRASE = 4 * BAR
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


_rubberband = None


def stretch_filter(ffmpeg, ratio):
    """rubberband (best quality for music, keeps drum hits sharp) when this ffmpeg has it, else atempo."""
    global _rubberband
    if _rubberband is None:
        out = subprocess.run([ffmpeg, "-hide_banner", "-filters"], capture_output=True, text=True).stdout
        _rubberband = " rubberband " in out
    return f"rubberband=tempo={ratio:.6f}:transients=crisp" if _rubberband else _atempo(ratio)


def decode(path, ffmpeg, af=None, sr=SR, ch=2):
    cmd = [ffmpeg, "-v", "error", "-i", str(path)]
    if af:
        cmd += ["-af", af]
    cmd += ["-f", "f32le", "-ac", str(ch), "-ar", str(sr), "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()


def grid_bpm(bpm):
    """Count the song in half, normal or double time. Prefer a version that needs speeding up by at most 1.5x or
    slowing by at most 10% (owner wants fast, punchy music); otherwise the smallest change."""
    cands = (bpm / 2, bpm, bpm * 2)
    ok = [c for c in cands if 0.9 <= TEMPO / c <= 1.5]
    return min(ok or cands, key=lambda x: abs(np.log(TEMPO / x)))


def beat_phase(x, sr=SR):
    """Where the beats sit inside the 0.5 s grid (0..0.5 s), for audio already at 120 BPM.

    Low band (< 200 Hz: kick, bass, snare body) -> envelope rise (attacks) at 1 ms resolution -> phase of the 2 Hz
    component over the whole song. Off-beat hi-hats are filtered out; attacks have almost no detection lag."""
    from scipy.signal import butter, sosfiltfilt
    lo = sosfiltfilt(butter(4, 200, "low", fs=sr, output="sos"), x)
    env = np.abs(lo)
    k = sr // 1000                                            # 1 ms blocks
    env = env[: len(env) // k * k].reshape(-1, k).max(1)
    env = np.convolve(env, np.ones(25) / 25, mode="same")     # 25 ms centred smoothing: removes bass-note ripple
    rise = np.maximum(0, np.diff(env, prepend=env[0]))
    on = rise > 0.25 * rise.max()                              # clear attacks only, not slow swells
    starts = np.nonzero(on & ~np.roll(on, 1))[0]              # first ms of each attack (a kick keeps "rising"
    starts = starts[(starts > 0) & (starts < len(env) - 40)]   # ~100 ms as its pitch falls - only its start counts)
    keep, last = [], -10 ** 9
    for s_ in starts:                                          # one start per hit: ignore re-triggers for 150 ms
        if s_ - last > 150:
            keep.append(s_)
        last = s_ if s_ - last > 150 else last
    starts = np.array(keep, dtype=int)
    w = env[starts + 40] - env[starts]                         # weight = how big the hit is
    t = (starts + 3) * k / sr                                  # block -> seconds (a block is 44 samples, not exactly 1 ms)
    c = np.dot(np.maximum(w, 0), np.exp(-2j * np.pi * t / BEAT))
    return float((-np.angle(c) / (2 * np.pi) % 1) * BEAT)


def drift(x, sr=SR):
    """Beat position change (s) between the first and second half of audio that should be at 120 BPM."""
    h = len(x) // 2
    return ((beat_phase(x[h:], sr) + h / sr) - beat_phase(x[:h], sr) + BEAT / 2) % BEAT - BEAT / 2


def downbeat_phase(y, grid, sr=22050):
    """Which of the 4 beat positions (0-3) in `grid` is beat 1."""
    import librosa
    hop = 512
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
    low = S[freqs < 150].sum(0)
    kick = np.maximum(0, np.diff(low, prepend=low[0]))
    chroma = librosa.feature.chroma_stft(S=S ** 2, sr=sr)
    chroma = librosa.util.normalize(chroma, axis=0)
    # harmony change at each beat: chroma of the beat that starts here vs the beat before
    fr = librosa.time_to_frames(grid, sr=sr, hop_length=hop)
    w = max(1, int(BEAT * sr / hop))
    nov = np.array([np.linalg.norm(chroma[:, f:f + w].mean(1) - chroma[:, max(0, f - w):f].mean(1))
                    if w <= f < chroma.shape[1] - w else 0 for f in fr])
    kk = np.array([kick[max(0, f - 1): f + 2].max() if f + 2 <= len(kick) else 0 for f in fr])
    # compare the 4 positions: per-position means, scaled to their spread; bass drum counts double
    km = np.array([kk[i::4].mean() for i in range(4)])
    nm = np.array([nov[i::4].mean() for i in range(4)])
    rel = lambda a: (a - a.mean()) / (a.mean() + 1e-9)    # relative contrast, so a flat feature adds ~nothing
    return int(np.argmax(2 * rel(km) + rel(nm)))


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
    ratio = TEMPO / grid_bpm(bpm)
    st = decode(path, ffmpeg, af=stretch_filter(ffmpeg, ratio))   # stereo, 120 BPM now
    # fine-tune: beats must sit at the same grid position at the start and the end of the song
    for _ in range(2):
        d = drift(st.mean(1))
        if abs(d) < 0.008 or abs(d) > 0.15:          # good enough / not a steady beat (fix would make it worse)
            break
        ratio *= 1 + d / (len(st) / SR / 2)          # later in the 2nd half = too slow -> speed up a bit
        st = decode(path, ffmpeg, af=stretch_filter(ffmpeg, ratio))
    bpm = TEMPO / ratio if abs(np.log(TEMPO / bpm)) < 0.36 else bpm
    mono = st.mean(1)

    # Beat position inside the 0.5 s grid. The phase of the onset envelope's 2 Hz component (= 120 BPM) over the whole
    # song: even 8th-note hi-hats cancel out at 2 Hz, so this locks onto the kick/snare beats, not the off-beats.
    # Low band only (< 400 Hz: kick, snare body, bass) - off-beat hi-hats would otherwise pull it half a beat.
    y2 = librosa.resample(mono, orig_sr=SR, target_sr=22050)
    phase = beat_phase(mono)

    # downbeat (beat 1 of the bar). Full-band onsets favour the snare on 2 and 4, so use what marks beat 1 instead:
    # the bass drum (low band onsets) and chord changes (chroma novelty), each normalised, summed per beat position.
    grid = np.arange(phase, len(mono) / SR - BEAT, BEAT)
    k = downbeat_phase(y2, grid)
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
    h = hashlib.md5(f"{path.resolve()}|{path.stat().st_mtime}|{path.stat().st_size}|v14|{TEMPO}".encode()).hexdigest()[:16]
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
            print(f"  music {folder.name}/{track.name}: {bpm:.1f} BPM -> {TEMPO:.0f} (x{ratio:.3f}), "
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
