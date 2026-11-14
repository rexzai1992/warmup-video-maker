"""Original soundtrack generator: music + beat-synced sound effects + voice callouts.

Styles: "pop" (school version) and "japan" (taiko drums, koto plucks, pentatonic melody).
All events sit on the 120 BPM grid so they match the dance moves frame-for-frame.
"""
import subprocess, wave, pathlib
import numpy as np

SR = 44100
BEAT = 0.5   # 120 BPM


# Interactive game layer: impact beats per move (same table as GAME_HITS in engine/index.html)
GAME_HITS = {
    "punch": (1, [(0.25, "hL"), (0.75, "hR")], "whack"),
    "kick": (2, [(0.5, "fL"), (1.5, "fR")], "kick"),
    "run": (1, [(0.0, "fR"), (0.5, "fL")], "stomp"),
    "highknees": (1, [(0.0, "fR"), (0.5, "fL")], "stomp"),
    "hop": (1, [(0.0, "fB")], "stomp"),
    "jump": (2, [(1.0, "hB"), (1.6, "land")], "pop"),
    "tuckjump": (2, [(1.0, "hB"), (1.6, "land")], "pop"),
    "starjump": (1, [(0.5, "hB")], "pop"),
    "frog": (4, [(2.5, "hB"), (3.2, "land")], "pop"),
    "climb": (1, [(0.25, "hL"), (0.75, "hR")], "grab"),
    "squat": (2, [(1.0, "hL"), (1.0, "hR")], "press"),
    "skater": (2, [(0.0, "fB"), (1.0, "fB")], "coin"),
}


def game_hits(tl, s):
    """[(beat, limb, kind)] impacts in a segment, or [] when it has no game."""
    if tl.get("games", True) is False or s.get("game") == "none" or s["scene"] == "card" or s.get("calm"):
        return []
    g = GAME_HITS.get(s["move"])
    if not g:
        return []
    cyc, at, kind = g
    nb = s["dur"] / BEAT - 2
    out = []
    c = 0
    while c * cyc < nb + cyc:
        for o, limb in at:
            hb = c * cyc + o
            if 4 <= hb <= nb:
                out.append((hb, limb, s.get("game", kind)))
        c += 1
    return sorted(out)


class Synth:
    def __init__(self, tl, voice_fn, ext_music=None, covered=()):
        self.tl, self.voice_fn = tl, voice_fn
        self.ext_music, self.covered = ext_music, set(covered)   # real music (N, 2) from music.py + parts it covers
        self.style = tl.get("music", "pop")
        self.segs, self.total = tl["segments"], tl["total"]
        self.N = int((self.total + 2) * SR)
        self.music = np.zeros(self.N, np.float32)
        self.sfx = np.zeros(self.N, np.float32)
        self.voice = np.zeros(self.N, np.float32)
        self.rng = np.random.default_rng(7)

    # ---------------- helpers
    def add(self, buf, t, x, g=1.0):
        i = int(t * SR)
        if 0 <= i < self.N:
            j = min(self.N, i + len(x))
            buf[i:j] += (x[: j - i] * g).astype(np.float32)

    @staticmethod
    def tt(d):
        return np.arange(int(d * SR)) / SR

    def env(self, d, a=0.005, r=None):
        t = self.tt(d)
        return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / ((r or d) / 5))

    @staticmethod
    def midi(n):
        return 440 * 2 ** ((n - 69) / 12)

    def noise(self, d):
        return self.rng.uniform(-1, 1, int(d * SR))

    @staticmethod
    def hp(x):
        return np.diff(x, prepend=0)

    @staticmethod
    def lp(x, k=8):
        return np.convolve(x, np.ones(k) / k, mode="same")

    # ---------------- instruments
    def kick(self):
        t = self.tt(0.4)
        f = 45 + 110 * np.exp(-t * 28)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7.5) + 0.3 * self.noise(0.4) * np.exp(-t * 200)

    def taiko(self, big=True):
        d = 0.9 if big else 0.4
        t = self.tt(d)
        f = 58 + 70 * np.exp(-t * 18)
        body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (4 if big else 9))
        skin = self.lp(self.noise(d), 4) * np.exp(-t * 40)
        return (body * 1.1 + skin * 0.5) * (1 if big else 0.6)

    def ka(self):  # rim click on the taiko
        t = self.tt(0.06)
        return self.hp(self.noise(0.06)) * np.exp(-t * 90) * 0.6 + np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 120) * 0.3

    def snare(self):
        t = self.tt(0.25)
        return 0.6 * self.noise(0.25) * np.exp(-t * 18) + 0.5 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25)

    def clap(self):
        x = np.zeros(int(0.3 * SR))
        for k, off in enumerate([0, 0.012, 0.024]):
            i0 = int(off * SR); m = len(x) - i0
            x[i0:] += self.rng.uniform(-1, 1, m) * np.exp(-np.arange(m) / SR * (60 if k < 2 else 14))
        return self.hp(x) * 0.6

    def hat(self, open_=False):
        d = 0.18 if open_ else 0.05
        return self.hp(self.hp(self.noise(d))) * np.exp(-self.tt(d) * (18 if open_ else 90)) * 0.35

    def tone(self, n, d, harm=(1, .5, .33, .25, .2), dec=None, a=0.005):
        t = self.tt(d)
        y = sum(h * np.sin(2 * np.pi * self.midi(n) * (i + 1) * t) for i, h in enumerate(harm))
        return y * self.env(d, a, dec)

    def bass(self, n, d):
        return self.tone(n, d, (1, .6, .3, .15), dec=d * 1.2, a=0.004) * 0.55

    def pluck(self, n, d):
        return self.tone(n, d, (1, 0, .33, 0, .2, 0, .14), dec=d * 0.9, a=0.002) * 0.22

    def koto(self, n, d=0.7):
        t = self.tt(d)
        f = self.midi(n) * (1 + 0.012 * np.exp(-t * 30))      # tiny pitch drop like a plucked koto string
        ph = 2 * np.pi * np.cumsum(f) / SR
        y = np.sin(ph) + 0.6 * np.sin(2 * ph) + 0.35 * np.sin(3 * ph) + 0.2 * np.sin(5 * ph)
        return y * np.exp(-t * 6) * np.minimum(1, t / 0.002) * 0.2

    def flute(self, n, d):
        t = self.tt(d)
        vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t)
        ph = 2 * np.pi * np.cumsum(self.midi(n) * vib) / SR
        e = np.minimum(1, t / 0.06) * np.minimum(1, (d - t) / 0.08)
        return (np.sin(ph) + 0.15 * np.sin(2 * ph) + 0.04 * self.noise(d)) * e * 0.12

    def pad(self, ns, d):
        t = self.tt(d)
        y = sum(np.sin(2 * np.pi * self.midi(n) * t) + 0.5 * np.sin(2 * np.pi * self.midi(n) * 1.004 * t) for n in ns)
        return y * np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.4) * 0.06

    def crash(self):
        d = 1.6
        return self.hp(self.noise(d)) * np.exp(-self.tt(d) * 3) * 0.35 + np.sin(2 * np.pi * 55 * self.tt(d)) * np.exp(-self.tt(d) * 4) * 0.5

    def gong(self):
        d = 2.5; t = self.tt(d)
        y = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((110, 1), (167, .6), (231, .4), (297, .3)))
        return y * np.exp(-t * 1.6) * np.minimum(1, t / 0.01) * 0.25

    def riser(self, d):
        t = self.tt(d)
        f = 200 + 1800 * (t / d) ** 2
        return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15 + self.hp(self.noise(d)) * 0.25) * (t / d) ** 2

    def whoosh(self, d=0.35):
        t = self.tt(d)
        return self.lp(self.noise(d), 24) * 3 * np.sin(np.pi * t / d) ** 2 * 0.6

    def boing(self, lo=200, hi=600, d=0.3):
        t = self.tt(d)
        f = lo + (hi - lo) * (1 - np.exp(-t * 14)) + 30 * np.sin(2 * np.pi * 18 * t)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * 0.45

    def thud(self):
        t = self.tt(0.2)
        return np.sin(2 * np.pi * (60 + 80 * np.exp(-t * 40)) * t) * np.exp(-t * 18) * 0.6

    def splash(self):
        d = 0.5
        return self.lp(self.noise(d), 3) * np.exp(-self.tt(d) * 7) * 0.5 + self.hp(self.noise(d)) * np.exp(-self.tt(d) * 10) * 0.25

    def pop(self):
        t = self.tt(0.12)
        return np.sin(2 * np.pi * (900 - 2000 * t) * t) * np.exp(-t * 35) * 0.5

    def ribbit(self):
        t = self.tt(0.32)
        am = (np.sin(2 * np.pi * 28 * t) > 0).astype(float)
        return np.sin(2 * np.pi * (180 + 60 * t) * t) * am * np.exp(-t * 6) * 0.45

    def bonk(self):                         # cartoon bonk + little squeak (whack the mouse)
        t = self.tt(0.18)
        body = np.sin(2 * np.pi * np.cumsum(700 * np.exp(-t * 9) + 180) / SR) * np.exp(-t * 22)
        t2 = self.tt(0.09)
        squeak = np.sin(2 * np.pi * np.cumsum(1600 + 900 * t2 / 0.09) / SR) * np.exp(-t2 * 25) * 0.35
        out = body * 0.8 + 0.25 * self.noise(0.18) * np.exp(-t * 80)
        out[: len(squeak)] += squeak
        return out

    def coin(self):                         # two-note coin ding
        a = self.tone(83, 0.07, (1, .3), dec=0.1) * 0.35
        b2 = self.tone(88, 0.35, (1, .3), dec=0.3) * 0.35
        return np.concatenate([a, b2])

    def click(self):
        t = self.tt(0.05)
        return self.hp(self.noise(0.05)) * np.exp(-t * 120) * 0.5 + np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 90) * 0.2

    def boom(self):                         # landing impact (screen shake)
        t = self.tt(0.6)
        low = np.sin(2 * np.pi * np.cumsum(38 + 70 * np.exp(-t * 14)) / SR) * np.exp(-t * 5.5)
        return low * 1.1 + self.lp(self.noise(0.6), 6) * np.exp(-t * 12) * 0.5

    @staticmethod
    def mix(*parts):
        """Sum sounds of different lengths: mix((x, gain), (y, gain), ...)."""
        n = max(len(x) for x, _ in parts)
        out = np.zeros(n)
        for x, g in parts:
            out[: len(x)] += x * g
        return out

    def game_sfx(self, kind, limb):
        if limb == "land":
            return self.boom(), 0.9
        m = self.mix
        return {"whack": (self.bonk(), 0.9),
                "pop": (m((self.pop(), 1.6), (self.clap(), 0.4)), 0.9),
                "stomp": (m((self.splash(), 0.9), (self.thud(), 0.5)), 0.75),
                "kick": (m((self.thud(), 1.0), (self.whoosh(0.3), 0.6)), 0.8),
                "grab": (self.coin(), 0.8), "coin": (self.coin(), 0.8),
                "press": (m((self.beep(76, 0.1), 1.0), (self.click(), 1.0)), 0.8)}.get(kind, (self.pop(), 0.6))

    def beep(self, n=81, d=0.12):
        return self.tone(n, d, (1, .2), dec=d * 2) * 0.35

    def chime(self, n=84):
        return self.tone(n, 0.8, (1, .4, .2), dec=0.6) * 0.3 + self.tone(n + 7, 0.8, (1,), dec=0.6) * 0.15

    def scratch(self):
        d = 0.45; t = self.tt(d)
        f = 900 * np.abs(np.sin(2 * np.pi * 3.2 * t)) + 120
        return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + self.lp(self.noise(d), 3) * 0.3) * np.exp(-t * 3)

    # ---------------- harmony
    PROG_POP = {
        1: [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]],
        2: [[48, 52, 55], [55, 59, 62], [57, 60, 64], [53, 57, 60]],
        3: [[50, 54, 57], [57, 61, 64], [59, 62, 66], [55, 59, 62]],
        4: [[52, 55, 59], [48, 52, 55], [55, 59, 62], [50, 54, 57]],
        5: [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]],
    }
    # Japanese "yo" pentatonic flavour (D E G A B) with open fifths
    PROG_JP = {
        1: [[50, 57, 62], [55, 62, 67], [52, 59, 64], [57, 64, 69]],
        2: [[52, 59, 64], [50, 57, 62], [55, 62, 67], [52, 59, 64]],
        3: [[55, 62, 67], [57, 64, 69], [52, 59, 64], [50, 57, 62]],
        4: [[50, 57, 62], [57, 64, 69], [55, 62, 67], [52, 59, 64]],
        5: [[55, 62, 67, 71], [52, 59, 64, 69], [50, 57, 62, 66], [55, 62, 67, 71]],
    }
    YO = [62, 64, 67, 69, 71, 74, 76, 79]
    MELO = [0, 2, 4, 3, 2, 1, 2, -1, 3, 4, 5, 4, 2, 3, 1, -1]   # -1 = rest
    ARP = [0, 1, 2, 1, 0, 2, 1, 2]

    @staticmethod
    def frozen_at(s, st):
        return s["move"] == "freeze" and st >= 4 and ((st / BEAT) % 8) >= 4

    def music_for(self, s):
        jp = self.style == "japan"
        calm, card = s.get("calm", False), s["scene"] == "card"
        prog = (self.PROG_JP if jp else self.PROG_POP)[s["ch"]]
        add, M = self.add, self.music
        for bi in range(int(round(s["dur"] / BEAT))):
            st = bi * BEAT
            t = s["start"] + st
            if self.frozen_at(s, st + 0.01):
                continue
            gb = int(round(t / BEAT))
            chord = prog[(gb // 4) % 4]
            bib = gb % 4
            root = chord[0] - 24 if chord[0] - 24 >= 26 else chord[0] - 12
            if bib == 0:
                add(M, t, self.pad([n + 12 for n in chord], 4 * BEAT), 1.0 if calm else 0.7)
            if calm:
                if s["id"].startswith("water"):
                    add(M, t, self.taiko(False) if jp else self.kick(), 0.35)
                    add(M, t + BEAT / 2, self.hat(), 0.5)
                for k in range(2):
                    n = chord[self.ARP[(bi * 2 + k) % 8] % len(chord)] + 12
                    add(M, t + k * BEAT / 2, self.koto(n, 0.9) if jp else self.pluck(n, 0.5), 0.7)
                if bib == 0:
                    add(M, t, self.bass(root, 4 * BEAT), 0.5)
                continue
            # drums
            if jp:
                add(M, t, self.taiko(bib in (0, 2)), 0.95)
                add(M, t + BEAT / 2, self.ka(), 0.45)
                if bib == 3:
                    add(M, t + BEAT * 0.75, self.taiko(False), 0.5)
                add(M, t, self.hat(), 0.25); add(M, t + BEAT / 2, self.hat(True), 0.3)
                if bib in (1, 3):
                    add(M, t, self.clap(), 0.3)
            else:
                add(M, t, self.kick(), 0.9)
                if bib in (1, 3):
                    add(M, t, self.snare(), 0.45); add(M, t, self.clap(), 0.35)
                for k in range(2):
                    add(M, t + k * BEAT / 2, self.hat(open_=(k == 1)), 0.45 if k else 0.3)
                if s["ch"] in (3, 4):
                    add(M, t + BEAT / 4, self.hat(), 0.18); add(M, t + 3 * BEAT / 4, self.hat(), 0.18)
            add(M, t, self.bass(root, BEAT / 2), 0.9)
            add(M, t + BEAT / 2, self.bass(root + 12, BEAT / 2), 0.6)
            if not card:
                if jp:
                    for k in range(2):
                        n = chord[self.ARP[(bi * 2 + k) % 8] % len(chord)] + 12
                        add(M, t + k * BEAT / 2, self.koto(n, 0.6), 0.7)
                    m = self.MELO[gb % 16]
                    if m >= 0 and (gb // 16) % 2 == 0:
                        add(M, t, self.flute(self.YO[m] + 12, BEAT * 0.95), 0.9)
                else:
                    for k in range(2):
                        n = chord[self.ARP[(bi * 2 + k) % 8] % len(chord)] + 12
                        add(M, t + k * BEAT / 2, self.pluck(n, 0.3), 0.8)
            if card and st >= s["dur"] - 4 * BEAT:
                for k in range(4):
                    add(M, t + k * BEAT / 4, self.taiko(False) if jp else self.snare(), 0.15 + 0.1 * k)

    def sfx_for(self, s, i):
        add, X = self.add, self.sfx
        st0, dur, mv = s["start"], s["dur"], s["move"]
        nb = int(round(dur / BEAT))
        T = lambda b: st0 + b * BEAT
        jp = self.style == "japan"
        if s["scene"] == "card":
            add(X, st0, self.gong() if jp else self.crash(), 0.9)
        elif i > 0:
            add(X, st0, self.whoosh(0.4), 0.7)
            add(X, st0, self.crash(), 0.3)
        nxt = self.segs[i + 1] if i + 1 < len(self.segs) else None
        if nxt and nxt["scene"] == "card":
            add(X, st0 + dur - 2.0, self.riser(2.0), 0.9)
        if s["scene"] != "card" and s["id"] not in ("intro", "outro") and not s.get("calm"):
            add(X, T(nb - 8), self.beep(88, 0.08), 0.6)
            for b in (nb - 6, nb - 4, nb - 2):
                add(X, T(b), self.beep(81, 0.12), 0.7)
        hits = game_hits(self.tl, s)
        done_pairs = set()
        for hb, limb, kind in hits:
            if (hb, kind) in done_pairs:          # two buttons pressed together = one sound
                continue
            done_pairs.add((hb, kind))
            y, g = self.game_sfx(kind, limb)
            add(X, T(hb), y, g)
        for b in range(nb):
            if hits and mv != "frog":
                continue
            if hits and mv == "frog":              # keep the ribbit, the landing boom replaces the thud
                if b % 4 == 0:
                    add(X, T(b + 1.8), self.ribbit(), 0.8)
                continue
            if mv in ("jump", "tuckjump") and b % 2 == 0:
                add(X, T(b + 0.4), self.boing(220, 700), 0.8)
                add(X, T(b + 1.6), self.splash() if s.get("prop") == "puddles" else self.thud(), 0.8)
            elif mv == "hop":
                add(X, T(b + 0.02), self.boing(300, 520, 0.18), 0.5)
            elif mv == "squat" and b % 2 == 1:
                add(X, T(b - 0.3), self.whoosh(0.6), 0.6)
            elif mv == "starjump":
                add(X, T(b + 0.5), self.clap(), 0.35)
            elif mv in ("run", "highknees"):
                add(X, T(b), self.thud(), 0.25); add(X, T(b + 0.5), self.thud(), 0.25)
            elif mv == "reachside" and b >= 8 and b % 2 == 1:
                add(X, T(b), self.pop(), 0.8)
            elif mv == "frog" and b % 4 == 0:
                add(X, T(b + 1.8), self.ribbit(), 0.8); add(X, T(b + 3.2), self.thud(), 0.7)
            elif mv == "punch":
                if jp and s["id"] == "taiko":
                    add(X, T(b + 0.25), self.taiko(False), 0.6); add(X, T(b + 0.75), self.taiko(False), 0.6)
                else:
                    add(X, T(b + 0.12), self.whoosh(0.18), 0.5); add(X, T(b + 0.62), self.whoosh(0.18), 0.5)
            elif mv == "kick" and b % 2 == 0:
                add(X, T(b + 0.1), self.whoosh(0.3), 0.6); add(X, T(b + 1.1), self.whoosh(0.3), 0.6)
            elif mv == "skater" and b % 2 == 0:
                add(X, T(b + 0.25), self.whoosh(0.35), 0.55); add(X, T(b + 1.25), self.whoosh(0.35), 0.55)
            elif mv == "climb":
                add(X, T(b + 0.25), self.pop(), 0.3)
            elif mv == "balance" and b % 16 == 0 and b > 0:
                add(X, T(b), self.chime(), 0.8)
            elif mv == "freeze" and b >= 8:
                if b % 8 == 4:
                    add(X, T(b), self.scratch(), 0.9)
                elif b % 8 == 0 and b >= 16:
                    add(X, T(b), self.chime(88), 0.7)

    @staticmethod
    def auto_voice(s):
        out = []
        if s["move"] == "freeze":
            hero = s["id"] == "statue"
            light = s.get("prop") == "light"
            for b in range(12, int(s["dur"] / BEAT), 8):
                out.append((b * BEAT, "Statue!" if hero else ("Red light!" if light else "Freeze!")))
                if (b + 4) * BEAT < s["dur"] - 0.5:
                    out.append(((b + 4) * BEAT, "Green light!" if light else "Dance!"))
        if s["move"] == "reachside":
            for b in range(8, 20, 2):
                out.append((b * BEAT, "Left!" if (b % 4) == 0 else "Right!"))
        return out

    def render(self, out, ffmpeg):
        for i, s in enumerate(self.segs):
            if i not in self.covered:
                self.music_for(s)
            self.sfx_for(s, i)
            lines = [(float(a), b, "en") for a, b in s.get("say", [])] + [(a, b, "en") for a, b in self.auto_voice(s)]
            lines += [(float(a), b, "ja") for a, b in s.get("jsay", [])]
            for at, text, lang in lines:
                at = round(at / BEAT) * BEAT          # every callout starts on the beat
                self.add(self.voice, s["start"] + at, self.voice_fn(text, lang), 1.0)
        envv = np.convolve(np.abs(self.voice), np.ones(int(0.15 * SR)) / int(0.15 * SR), mode="same")
        duck = 1 - 0.5 * np.clip(envv * 12, 0, 1)
        mono = self.music * 0.75 * duck + self.sfx * 0.8 + self.voice * 1.25
        mix = np.repeat(mono[:, None], 2, axis=1)
        if self.ext_music is not None:                       # real songs: stereo, ducked a bit more under the voice
            duck2 = 1 - 0.6 * np.clip(envv * 12, 0, 1)
            mix += self.ext_music[: len(mix)] * duck2[:, None]
        end = int(self.total * SR)
        fi, fo = int(0.6 * SR), int(1.5 * SR)
        mix[:fi] *= np.linspace(0, 1, fi)[:, None]
        mix[end - fo:end] *= np.linspace(1, 0, fo)[:, None]
        mix = mix[:end]
        mix = np.tanh(mix / (np.max(np.abs(mix)) * 0.55)) * 0.89
        wav = pathlib.Path(out).with_suffix(".wav")
        with wave.open(str(wav), "w") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((mix * 32767).astype(np.int16).tobytes())
        subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", str(wav), "-ac", "2", "-c:a", "aac", "-b:a", "128k", str(out)], check=True)
        wav.unlink()
