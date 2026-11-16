# -*- coding: utf-8 -*-
"""Musica de fondo + efectos de sonido para el video ZEUS, 100% sintetizados.
120 BPM, La menor, progresion i-VI-III-VII (Am F C G). 90 s.
Salidas en build/: music.wav, sfx.wav, mix.wav
"""
import json, os
import numpy as np
from scipy import signal
import wave

SR = 44100
DUR = 90.0
N = int(SR * DUR)
BPM = 120
BEAT = 60 / BPM
S16 = BEAT / 4
BAR = BEAT * 4
HERE = os.path.dirname(__file__)
BUILD = os.path.join(HERE, "..", "build")
TL = json.load(open(os.path.join(BUILD, "timeline.json")))
rs = np.random.RandomState(7)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(d):
    return np.arange(int(d * SR)) / SR


def env_adsr(n, a=0.005, d=0.1, s=0.6, r=0.1):
    e = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = min(na, n); e[:na] = np.linspace(0, 1, na)
    nd = min(nd, n - na); e[na:na + nd] = np.linspace(1, s, nd)
    nr = min(nr, n)
    if nr > 0:
        e[n - nr:] *= np.linspace(1, 0, nr)
    return e


def polyblep(ph, dt):
    out = np.zeros_like(ph)
    m = ph < dt
    x = ph[m] / dt; out[m] = x + x - x * x - 1
    m2 = ph > 1 - dt
    x = (ph[m2] - 1) / dt; out[m2] = x * x + x + x + 1
    return out


def saw(freq, n, phase0=0.0):
    dt = freq / SR
    ph = (phase0 + np.cumsum(np.full(n, dt))) % 1.0
    return 2 * ph - 1 - polyblep(ph, dt)


def square(freq, n):
    dt = freq / SR
    ph = np.cumsum(np.full(n, dt)) % 1.0
    s = np.where(ph < 0.5, 1.0, -1.0)
    s += polyblep(ph, dt)
    s -= polyblep((ph + 0.5) % 1.0, dt)
    return s


def lp(x, fc, order=2):
    sos = signal.butter(order, min(fc, SR * 0.45), "low", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def hp(x, fc, order=2):
    sos = signal.butter(order, fc, "high", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def bp(x, f1, f2, order=2):
    sos = signal.butter(order, [f1, min(f2, SR * 0.45)], "band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def sweep_lp(x, fcs, block=512):
    """filtro paso bajo variable en el tiempo (fcs: array de cortes por muestra)"""
    out = np.zeros_like(x); zi = None
    for i in range(0, len(x), block):
        fc = float(np.clip(fcs[min(i, len(fcs) - 1)], 40, SR * 0.45))
        sos = signal.butter(2, fc, "low", fs=SR, output="sos")
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        out[i:i + block], zi = signal.sosfilt(sos, x[i:i + block], zi=zi)
    return out


def reverb_ir(dur=2.2, decay=3.0, seed=1):
    r = np.random.RandomState(seed)
    t = tt(dur)
    ir = r.randn(len(t)) * np.exp(-decay * t)
    ir = lp(ir, 6000)
    ir[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
    return ir / np.sqrt(np.sum(ir ** 2))


IR_L, IR_R = reverb_ir(seed=1), reverb_ir(seed=2)


def reverb(x, wet=0.25):
    l = signal.fftconvolve(x, IR_L)[:len(x)]
    r = signal.fftconvolve(x, IR_R)[:len(x)]
    return np.stack([x + wet * l, x + wet * r])


def place(buf, sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= buf.shape[-1]:
        return
    if sig.ndim == 1:
        sig = np.stack([sig * np.sqrt(0.5 - pan * 0.5) * 1.414, sig * np.sqrt(0.5 + pan * 0.5) * 1.414])
    n = min(sig.shape[1], buf.shape[1] - i)
    buf[:, i:i + n] += gain * sig[:, :n]


# =============================================================== INSTRUMENTOS
def kick(punch=1.0):
    t = tt(0.45)
    f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 7.5)
    s += 0.5 * punch * np.exp(-t * 300) * rs.randn(len(t)) * 0.3
    return np.tanh(s * 1.6) * 0.9


def clap():
    t = tt(0.35)
    n = rs.randn(len(t))
    e = np.zeros(len(t))
    for d in (0.0, 0.011, 0.022):
        e += (t >= d) * np.exp(-(t - d).clip(0) * 180)
    e += (t >= 0.03) * np.exp(-(t - 0.03).clip(0) * 14) * 0.5
    return bp(n * e, 900, 5000) * 0.9


def snare():
    t = tt(0.25)
    s = bp(rs.randn(len(t)), 1500, 9000) * np.exp(-t * 22) * 0.7
    s += np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.5
    return s


def hat(open_=False):
    t = tt(0.3 if open_ else 0.06)
    s = hp(rs.randn(len(t)), 7000) * np.exp(-t * (12 if open_ else 70))
    return s * 0.45


def tom(f0):
    t = tt(0.4)
    f = f0 * (1 + 0.6 * np.exp(-t * 20))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 0.7


def supersaw(m, d, voices=7, detune=0.18, cutoff=3500, a=0.005, r=0.12, s=0.7, dd=0.15):
    n = int(d * SR)
    f = mtof(m)
    out = np.zeros(n)
    for v in range(voices):
        cents = (v - (voices - 1) / 2) / ((voices - 1) / 2) * detune * 100
        out += saw(f * 2 ** (cents / 1200), n, phase0=rs.rand())
    out /= voices ** 0.7
    out = lp(out, cutoff)
    return out * env_adsr(n, a, dd, s, r)


def pluck(m, d=0.22, cutoff0=5000):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = 0.6 * saw(mtof(m), n) + 0.4 * square(mtof(m) * 2, n) * 0.5
    fcs = 300 + cutoff0 * np.exp(-t * 18)
    x = sweep_lp(x, fcs, 256)
    return x * np.exp(-t * 9) * env_adsr(n, 0.002, 0.01, 1, 0.02)


def bass(m, d, cutoff=520):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = 0.7 * saw(mtof(m), n) + 0.6 * np.sin(2 * np.pi * mtof(m) * t)
    x = sweep_lp(x, cutoff + 900 * np.exp(-t * 14), 256)
    return np.tanh(x * 1.4) * env_adsr(n, 0.004, 0.08, 0.8, 0.03)


def lead(m, d):
    n = int(d * SR)
    t = np.arange(n) / SR
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.clip(t * 4, 0, 1)
    f = mtof(m) * vib
    ph = np.cumsum(f / SR) % 1
    x = 2 * ph - 1
    ph2 = np.cumsum(f * 1.006 / SR) % 1
    x = 0.5 * x + 0.5 * (2 * ph2 - 1)
    x = lp(x, 4200)
    return x * env_adsr(n, 0.01, 0.1, 0.75, 0.08)


# =============================================================== ARREGLO
PROG = [  # (acorde voicing, raiz bajo)
    ([57, 60, 64, 69], 33),  # Am
    ([53, 57, 60, 65], 29),  # F
    ([55, 60, 64, 67], 36),  # C
    ([55, 59, 62, 67], 31),  # G
]
NBARS = int(DUR / BAR)

drums = np.zeros((2, N)); bassb = np.zeros((2, N)); synth = np.zeros((2, N)); padb = np.zeros((2, N)); leadb = np.zeros((2, N))
K, CL, SN, HC, HO = kick(), clap(), snare(), hat(False), hat(True)
kick_times = []


def sec(t):
    if t < 6: return "intro"
    if t < 14: return "tension"
    if t < 34: return "dropA"
    if t < 46: return "dropA2"
    if t < 56: return "breakB"
    if t < 66: return "groove"
    if t < 72: return "groove2"
    if t < 76: return "build"
    if t < 88: return "dropB"
    return "outro"


GAPS = [(13.75, 14.0), (75.75, 76.0)]  # silencios antes de los drops


def in_gap(t):
    return any(a <= t < b for a, b in GAPS)


for b in range(NBARS):
    t0 = b * BAR
    chord, root = PROG[b % 4]
    S = sec(t0)
    for s16 in range(16):
        t = t0 + s16 * S16
        if in_gap(t) or t >= 88.0:
            continue
        S = sec(t)
        beat = s16 % 4 == 0
        # ---- bombo
        if S == "intro" and s16 in (0, 8):
            place(drums, lp(K, 900), t, 0.55); kick_times.append(t)
        elif S == "tension" and beat:
            place(drums, lp(K, 600 + (t - 6) * 400), t, 0.75); kick_times.append(t)
        elif S in ("dropA", "dropA2", "groove", "groove2", "dropB") and beat:
            place(drums, K, t, 1.0); kick_times.append(t)
        elif S == "breakB" and s16 in (0, 10):
            place(drums, K, t, 0.9); kick_times.append(t)
        elif S == "build":
            if (t < 74 and beat) or (t >= 74 and s16 % 2 == 0):
                place(drums, K, t, 0.9); kick_times.append(t)
        # ---- clap
        if S in ("dropA", "dropA2", "groove", "groove2", "dropB") and s16 in (4, 12):
            place(drums, CL, t, 0.7)
        if S == "breakB" and s16 == 8:
            place(drums, CL, t, 0.75)
        # ---- hats
        if S in ("tension",) and s16 % 2 == 1:
            place(drums, HC, t, 0.35 + 0.3 * (t - 6) / 8, pan=0.3)
        if S in ("dropA", "dropA2", "groove", "groove2", "dropB", "breakB", "build"):
            place(drums, HC, t, 0.28 if s16 % 2 else 0.18, pan=0.25)
            if s16 % 4 == 2 and S != "breakB":
                place(drums, HO, t, 0.45, pan=-0.2)
        if S == "intro" and s16 % 4 == 2:
            place(drums, HC, t, 0.25, pan=0.3)
        # ---- toms en investigacion
        if S == "groove" and s16 in (13, 14, 15) and b % 2 == 1:
            place(drums, tom(110 - (s16 - 13) * 18), t, 0.6, pan=(s16 - 14) * 0.4)
        # ---- bajo
        if S == "tension" and s16 % 2 == 0:
            place(bassb, bass(root + 12 * (s16 % 4 == 2), S16 * 1.8, 260 + (t - 6) * 60), t, 0.55)
        if S in ("dropA", "dropA2", "groove", "groove2", "dropB", "build"):
            pat = {0: 0, 3: 12, 6: 0, 8: 0, 10: 12, 11: 0, 14: 7}
            if s16 in pat:
                place(bassb, bass(root + pat[s16], S16 * (2.6 if s16 in (0, 8) else 1.6)), t, 0.75)
        if S == "breakB" and s16 in (0, 10):
            place(bassb, bass(root, S16 * 5, 400), t, 0.7)
        # ---- stabs (supersaw)
        if S in ("dropA", "dropA2", "dropB") and s16 in (0, 3, 6, 10, 12):
            for m in chord:
                place(synth, supersaw(m + 12, 0.2, cutoff=4200, r=0.08), t, 0.2, pan=rs.uniform(-.4, .4))
        if S in ("groove", "groove2") and s16 in (2, 6, 10, 14):
            for m in chord[1:]:
                place(synth, supersaw(m + 12, 0.14, cutoff=2600, r=0.06), t, 0.16, pan=(0.5 if s16 % 8 == 2 else -0.5))
        # ---- arpegio pluck
        arp_on = S in ("intro", "tension", "dropA2", "breakB", "groove", "groove2", "build", "dropB")
        if arp_on:
            seq = [chord[0], chord[1], chord[2], chord[3], chord[2] + 12, chord[3], chord[1] + 12, chord[2]]
            m = seq[s16 % 8] + 12
            g = {"intro": 0.22, "tension": 0.25}.get(S, 0.2)
            cut = 1200 + 2500 * min(1, t / 14) if t < 14 else 5000
            place(synth, pluck(m, 0.22, cut), t, g, pan=0.45 if s16 % 2 else -0.45)
    # ---- pad (largo por compas)
    if t0 < 88:
        S0 = sec(t0)
        pg = {"intro": 0.32, "tension": 0.3, "breakB": 0.34, "build": 0.3}.get(S0, 0.22)
        d = BAR if not any(a > t0 and a < t0 + BAR for a, _ in GAPS) else BAR - 0.25
        for m in chord:
            place(padb, supersaw(m, d + 0.15, voices=5, detune=0.12, cutoff=1500 if S0 != "intro" else 900, a=0.25, r=0.35, s=0.8, dd=0.3), t0, pg * 0.6,
                  pan=rs.uniform(-.6, .6))

# ---- melodia principal (drops y final)
MEL = [  # (paso de 8vo, nota, duracion en 8vos) por compas segun acorde
    [(0, 76, 2), (2, 76, 1), (3, 74, 1), (4, 72, 2), (6, 69, 2)],
    [(0, 72, 2), (2, 72, 1), (3, 74, 1), (4, 76, 2), (6, 72, 2)],
    [(0, 79, 2), (2, 76, 2), (4, 74, 1), (5, 72, 3)],
    [(0, 74, 2), (2, 71, 2), (4, 74, 1), (5, 76, 3)],
]
for b in range(NBARS):
    t0 = b * BAR
    if not ((14 <= t0 < 34 and b % 8 >= 4) or (76 <= t0 < 88) or (46 <= t0 < 54)):
        continue
    gain = 0.26 if t0 >= 76 else 0.2
    for st, m, du in MEL[b % 4]:
        t = t0 + st * BEAT / 2
        if in_gap(t): continue
        place(leadb, lead(m, du * BEAT / 2 * 0.95), t, gain, pan=0.0)
        place(leadb, lead(m + 12, du * BEAT / 2 * 0.95), t, gain * 0.25, pan=0.3)

# ---- redobles de tension
for a, b2 in [(12.0, 13.75), (72.0, 75.75)]:
    t = a
    while t < b2:
        p = (t - a) / (b2 - a)
        place(drums, SN, t, 0.25 + 0.5 * p, pan=0)
        step = S16 * 2 if p < 0.5 else (S16 if p < 0.85 else S16 / 2)
        t += step

# ---- sidechain (bombeo) de todo menos la bateria
duck = np.ones(N)
for kt in kick_times:
    i = int(kt * SR); n = int(0.38 * SR)
    seg = 1 - 0.65 * np.exp(-np.arange(n) / SR * 11)
    j = min(N, i + n)
    duck[i:j] = np.minimum(duck[i:j], seg[:j - i])

# envolvente global de filtro para la intro/tension (sube el brillo)
music_tonal = bassb + synth * 1.0 + padb + leadb
music_tonal *= duck
music_tonal = reverb(music_tonal[0], 0.22)[0:1].repeat(2, 0) * 0 + np.stack([
    reverb(music_tonal[0], 0.22)[0], reverb(music_tonal[1], 0.22)[1]])
music = music_tonal + drums
# fade final
fo = int(2.0 * SR)
music[:, N - fo:] *= np.linspace(1, 0, fo) ** 1.5


# =============================================================== EFECTOS
def noise(d):
    return rs.randn(int(d * SR))


def fx_boom():
    t = tt(2.2)
    f = 32 + 70 * np.exp(-t * 6)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    s += lp(noise(2.2), 300) * np.exp(-t * 4) * 0.8
    return np.tanh(s * 1.5)


def fx_whoosh(d=0.6, up=True):
    n = int(d * SR); t = np.arange(n) / SR
    x = noise(d)
    fcs = (300 + 6000 * (t / d) ** 1.5) if up else (6000 - 5700 * (t / d) ** 0.7)
    y = sweep_lp(x, fcs, 256) - sweep_lp(x, fcs * 0.25, 256)
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return y * e * 1.2


def fx_pop(f0=700):
    t = tt(0.09)
    f = f0 * (1 + 1.2 * (t / 0.09))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45) * 0.8


def fx_click():
    t = tt(0.03)
    return (np.sin(2 * np.pi * 2400 * t) * 0.6 + hp(noise(0.03), 3000) * 0.5) * np.exp(-t * 200)


def fx_tick():
    t = tt(0.05)
    return bp(noise(0.05), 2500, 5000) * np.exp(-t * 120) * 1.4 + np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 150) * 0.4


def fx_ding(f=1318.5):
    t = tt(1.2)
    s = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (3 + k * 2)) for k, a in [(1, 1), (1.5, 0.5), (2.0, 0.35), (3.01, 0.15)])
    return s * 0.45 * env_adsr(len(t), 0.002, 0.01, 1, 0.05)


def fx_glitch():
    out = np.zeros(int(0.5 * SR)); r = np.random.RandomState(3); i = 0
    while i < len(out):
        n = int(r.uniform(0.01, 0.05) * SR)
        f = r.choice([80, 200, 400, 1200, 3000])
        seg = square(f, n) * r.uniform(0.2, 0.6) if r.rand() < .6 else rs.randn(n) * 0.4
        seg = np.round(seg * 4) / 4
        out[i:i + n] = seg[:len(out) - i]; i += n
    return out * 0.6


def fx_window(k):
    t = tt(0.13); f = [520, 440, 600, 380][k % 4]
    s = square(f, len(t)) * 0.25 + np.sin(2 * np.pi * f * 2 * t) * 0.3
    return lp(s, 3000) * np.exp(-t * 25)


def fx_stamp():
    t = tt(0.6)
    s = np.sin(2 * np.pi * np.cumsum(60 + 120 * np.exp(-t * 30)) / SR) * np.exp(-t * 9)
    s += bp(noise(0.6), 200, 3000) * np.exp(-t * 25) * 0.9
    return np.tanh(s * 2) * 0.9


def fx_riser(d):
    n = int(d * SR); t = np.arange(n) / SR; p = t / d
    x = noise(d)
    y = sweep_lp(x, 200 + 9000 * p ** 2, 256) - sweep_lp(x, 100 + 3000 * p ** 2, 256)
    tone = saw(1, n) * 0
    f = 110 * 2 ** (p * 3)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * 0.12
    return (y * 0.8 + tone) * p ** 1.6


def fx_lightning():
    d = 2.0; n = int(d * SR); t = np.arange(n) / SR
    x = noise(d)
    crack = hp(x, 1500) * np.exp(-t * 30) * 1.6
    # chisporroteo
    imp = np.zeros(n); r = np.random.RandomState(11)
    for _ in range(140):
        i = int(r.exponential(0.25) * SR)
        if i < n: imp[i] += r.uniform(-1, 1) * np.exp(-i / SR * 3)
    crackle = hp(signal.lfilter([1], [1, -0.6], imp), 2000) * 2.0
    rumble = lp(x, 180) * np.exp(-t * 1.5) * 1.6
    return np.tanh(crack + crackle + rumble)


def fx_shimmer():
    out = np.zeros(int(1.6 * SR))
    for i, m in enumerate([81, 84, 88, 93, 96]):
        t = tt(1.2)
        s = np.sin(2 * np.pi * mtof(m) * t) * np.exp(-t * 4) * 0.25
        j = int(i * 0.06 * SR); out[j:j + len(s)] += s
    return out


def fx_counter(d=2.4):
    out = np.zeros(int(d * SR)); t = 0.0; k = 0
    while t < d:
        p = t / d
        s = fx_pop(900 + 600 * p) * 0.35
        j = int(t * SR); out[j:j + len(s)] += s[:len(out) - j]
        t += 0.045 + 0.12 * p ** 2; k += 1
    return out


def fx_kaching():
    out = np.zeros(int(1.6 * SR))
    ka = bp(noise(0.08), 2000, 8000) * np.exp(-tt(0.08) * 60)
    out[:len(ka)] += ka
    t = tt(1.4)
    bell = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * dcy) * a for f, a, dcy in [(2637, 0.5, 3), (3322, 0.4, 3.5), (4186, 0.3, 4), (5274, 0.2, 5), (1975, 0.3, 2.5)])
    trem = 0.75 + 0.25 * np.sin(2 * np.pi * 28 * t)
    j = int(0.08 * SR); out[j:j + len(t)] += bell * trem * 0.7
    return out


def fx_error():
    out = np.zeros(int(0.45 * SR))
    for i, f in enumerate([330, 250]):
        t = tt(0.18); s = lp(square(f, len(t)), 2000) * 0.35 * env_adsr(len(t), 0.003, 0.05, 0.8, 0.04)
        j = int(i * 0.2 * SR); out[j:j + len(s)] += s
    return out


def fx_sonar():
    t = tt(1.8)
    return np.sin(2 * np.pi * 1250 * t) * np.exp(-t * 3.2) * 0.45 * env_adsr(len(t), 0.004, 0.01, 1, 0.1)


def fx_arp(notes, step=0.08, decay=4, g=0.35):
    out = np.zeros(int((len(notes) * step + 1.3) * SR))
    for i, m in enumerate(notes):
        t = tt(1.2)
        s = (np.sin(2 * np.pi * mtof(m) * t) + 0.3 * np.sin(2 * np.pi * mtof(m) * 2 * t)) * np.exp(-t * decay) * g
        j = int(i * step * SR); out[j:j + len(s)] += s
    return out


def fx_impact():
    return np.tanh(kick() * 1.3 + np.pad(lp(noise(0.4), 2500) * np.exp(-tt(0.4) * 12) * 0.6, (0, len(kick()) - int(0.4 * SR))))


def fx_check(i):
    return fx_arp([76 + i * 2, 83 + i * 2], 0.05, 9, 0.3)


def fx_transition():
    w = fx_whoosh(0.55, True)
    hit = lp(kick(), 400) * 0.5
    out = np.zeros(len(w) + len(hit))
    out[:len(w)] += w; j = int(0.27 * SR); out[j:j + len(hit)] += hit
    return out


sfx = np.zeros((2, N))
riser_d = {11.0: 2.75, 72.0: 3.75}
wcount = 0; ccount = 0
GAIN = dict(boom=0.75, whoosh=0.45, pop=0.35, glitch=0.4, window=0.45, stamp=0.7, riser=0.5, lightning=0.75, shimmer=0.5,
            swoosh_down=0.45, transition=0.55, click=0.5, tick=0.5, ding=0.6, blip=0.4, counter=0.6, kaching=0.65, error=0.6,
            sonar=0.5, found=0.55, impact=0.75, check=0.6, success=0.55)
for name, t in TL["sfx"]:
    pan = 0.0
    if name == "boom": s = fx_boom()
    elif name == "whoosh": s = fx_whoosh(0.6, True); s_off = 0.3
    elif name == "swoosh_down": s = fx_whoosh(0.7, False)
    elif name == "pop": s = fx_pop(600 + rs.randint(0, 500)); pan = rs.uniform(-.5, .5)
    elif name == "glitch": s = fx_glitch()
    elif name == "window": s = fx_window(wcount); pan = rs.uniform(-.6, .6); wcount += 1
    elif name == "stamp": s = fx_stamp()
    elif name == "riser": s = fx_riser(riser_d[t])
    elif name == "lightning": s = fx_lightning()
    elif name == "shimmer": s = fx_shimmer()
    elif name == "transition": s = fx_transition(); t -= 0.27
    elif name == "click": s = fx_click()
    elif name == "tick": s = fx_tick()
    elif name == "ding": s = fx_ding()
    elif name == "blip": s = fx_pop(1300)
    elif name == "counter": s = fx_counter()
    elif name == "kaching": s = fx_kaching()
    elif name == "error": s = fx_error()
    elif name == "sonar": s = fx_sonar()
    elif name == "found": s = fx_arp([81, 85, 88, 93], 0.09, 3.5, 0.3)
    elif name == "impact": s = fx_impact()
    elif name == "check": s = fx_check(ccount); ccount += 1
    elif name == "success": s = fx_arp([72, 76, 79, 84, 88], 0.07, 3.5, 0.3)
    else: continue
    if name == "whoosh": t -= 0.3  # pico del whoosh en el evento
    place(sfx, s, max(0, t), GAIN[name], pan)
sfx = np.stack([reverb(sfx[0], 0.18)[0], reverb(sfx[1], 0.18)[1]])


# =============================================================== MASTER
def norm(x, peak_db=-1.0):
    return x / (np.max(np.abs(x)) + 1e-9) * 10 ** (peak_db / 20)


def soft_limit(x, drive=1.0):
    return np.tanh(x * drive) / np.tanh(drive)


def write(path, x):
    x = np.clip(x, -1, 1)
    data = (x.T * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())


# realce leve de graves y brillo
music = norm(music, -3)
music = soft_limit(music * 1.4, 1.2)
music = norm(music, -1.5)
sfxn = norm(sfx, -1.5)
# mezcla: musica un poco abajo para dejar espacio a la voz
mix = soft_limit(0.62 * music + 0.75 * sfxn, 1.1)
mix = norm(mix, -1.0)
write(os.path.join(BUILD, "music.wav"), music)
write(os.path.join(BUILD, "sfx.wav"), sfxn)
write(os.path.join(BUILD, "mix.wav"), mix)
print("ok")
