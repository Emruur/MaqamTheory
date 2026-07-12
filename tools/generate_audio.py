"""Generate all WAV files for the maqam learning site, in three voices.

Usage:
    python3 tools/generate_audio.py           # write audio/*.wav (warm),
                                              # audio/ney/*, audio/pluck/*
    python3 tools/generate_audio.py --check   # verify theory data + synth pitch
"""

import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import makam_data as md

SR = 44100
OUT = Path(__file__).parent.parent / "audio"
BPM = 96

# Three timbres. The "warm" voice lives at audio/ root (site default);
# the others in subdirectories switched by the site-wide voice picker.
VOICES = {
    "warm": {
        "subdir": "",
        "harmonics": [(1, 1.0), (2, 0.42), (3, 0.28), (4, 0.12),
                      (5, 0.08), (6, 0.045)],
        "attack": 0.028, "decay": 1.4, "harm_decay": 0.9,
        "vib_depth": 0.0025, "vib_rate": 5.2, "noise": 0.0,
    },
    "ney": {
        "subdir": "ney",
        "harmonics": [(1, 1.0), (2, 0.14), (3, 0.40), (4, 0.09),
                      (5, 0.17), (6, 0.05), (7, 0.07)],
        "attack": 0.09, "decay": 1.0, "harm_decay": 0.7,
        "vib_depth": 0.0042, "vib_rate": 4.8, "noise": 0.10,
    },
    "pluck": {
        "subdir": "pluck",
        "harmonics": [(1, 1.0), (2, 0.62), (3, 0.45), (4, 0.30),
                      (5, 0.19), (6, 0.12), (7, 0.08), (8, 0.05)],
        "attack": 0.005, "decay": 2.3, "harm_decay": 2.2,
        "vib_depth": 0.0, "vib_rate": 5.0, "noise": 0.0,
    },
}


def bandpass_noise(n: int, f0: float) -> np.ndarray:
    """Breath layer for the ney: noise resonating around a centre frequency."""
    spec = np.fft.rfft(np.random.default_rng(int(f0 * 100)).standard_normal(n))
    freqs = np.fft.rfftfreq(n, 1 / SR)
    resp = 1.0 / (1.0 + ((freqs - f0) / (f0 / 9.0)) ** 2)
    out = np.fft.irfft(spec * resp, n)
    peak = np.max(np.abs(out))
    return out / peak if peak > 0 else out


def tone(freq: float, dur: float, voice: str = "warm",
         velocity: float = 1.0) -> np.ndarray:
    """One synthesized note in the given voice."""
    v = VOICES[voice]
    n = int(dur * SR)
    t = np.arange(n) / SR
    vib = v["vib_depth"] * np.clip((t - 0.25) / 0.35, 0, 1)
    inst_freq = freq * (1 + vib * np.sin(2 * np.pi * v["vib_rate"] * t))
    phase = 2 * np.pi * np.cumsum(inst_freq) / SR
    sig = np.zeros(n)
    for k, amp in v["harmonics"]:
        sig += amp * np.exp(-t * v["harm_decay"] * k) * np.sin(k * phase)
    if v["noise"] > 0:
        sig += v["noise"] * bandpass_noise(n, freq * 2)
    attack = np.minimum(t / v["attack"], 1.0)
    decay = np.exp(-t * v["decay"])
    release_len = min(0.06, dur / 4)
    release = np.clip((dur - t) / release_len, 0, 1)
    return velocity * sig * attack * decay * release


def render(events: list[tuple[float | None, float]], voice: str = "warm",
           gap: float = 0.02, tail: float = 0.6,
           bpm: float = BPM) -> np.ndarray:
    """Render (commas, beats) events into one buffer. commas=None is a rest."""
    beat = 60.0 / bpm
    total = sum(beats for _, beats in events) * beat + tail
    buf = np.zeros(int(total * SR) + SR // 10)
    cursor = 0.0
    for commas, beats in events:
        slot = beats * beat
        if commas is not None:
            dur = min(slot * 1.6, slot + 0.5)
            note = tone(md.freq(commas), dur, voice)
            i = int((cursor + gap) * SR)
            note = note[: max(0, len(buf) - i)]
            buf[i:i + len(note)] += note
        cursor += slot
    peak = np.max(np.abs(buf))
    if peak > 0:
        buf *= 0.82 / peak
    return buf


def write_wav(name: str, buf: np.ndarray, subdir: str = "") -> None:
    d = OUT / subdir if subdir else OUT
    d.mkdir(parents=True, exist_ok=True)
    data = (np.clip(buf, -1, 1) * 32767).astype("<i2")
    with wave.open(str(d / name), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def scale_events(pitches: list[int], hold_ends: bool = True):
    ev = []
    for i, p in enumerate(pitches):
        last = i == len(pitches) - 1
        ev.append((p, 1.6 if (last and hold_ends) else 0.75))
    return ev


def collect_sequences() -> dict[str, dict]:
    """Every sequence on the site: {name: {events, bpm, tail}}."""
    seqs = {}

    def add(name, events, bpm=BPM, tail=0.6):
        seqs[name] = {"events": events, "bpm": bpm, "tail": tail}

    for key, m in md.MAKAMLAR.items():
        asc, desc = m["asc"], m["desc"]
        add(f"{key}_scale_asc", scale_events(asc))
        add(f"{key}_scale_desc", scale_events(list(reversed(desc))))
        updown = asc + list(reversed(desc))[1:]
        add(f"{key}_quiz",
            [(p, 0.6) for p in updown[:-1]] + [(updown[-1], 1.6)])
        for part in ("lower_genus", "upper_genus"):
            _, genus_name, root = m[part]
            add(f"{key}_{part}",
                scale_events(md.steps_to_scale(root, md.GENUS[genus_name])))
        add(f"{key}_seyir", m["seyir"])
        if key in md.SONGS:
            song = md.SONGS[key]
            add(f"song_{key}", song["events"], bpm=song["bpm"], tail=1.0)

    needed = set()
    for m in md.MAKAMLAR.values():
        needed.update(m["asc"])
        needed.update(m["desc"])
        needed.add(m["yeden"])
    for name, (genus_name, root) in md.GENUS_DEMOS.items():
        needed.update(md.steps_to_scale(root, md.GENUS[genus_name]))
    for commas in sorted(needed):
        add(f"note_{commas}", [(commas, 1.4)], tail=0.4)

    for name, (genus_name, root) in md.GENUS_DEMOS.items():
        add(f"genus_{name}",
            scale_events(md.steps_to_scale(root, md.GENUS[genus_name])))

    add("demo_comma_steps", [(40 + i, 0.55) for i in range(9)] + [(49, 1.4)])
    add("demo_one_comma", [(40, 1.2), (41, 1.2), (40, 1.2), (41, 1.6)])
    add("demo_b_variants",
        [(40, 0.7), (49, 1.5), (None, 0.5),
         (40, 0.7), (48, 1.5), (None, 0.5),
         (40, 0.7), (45, 1.5), (None, 0.5),
         (40, 0.7), (44, 1.5)])
    add("demo_intervals",
        [(40, 0.7), (49, 1.3), (None, 0.4),
         (40, 0.7), (48, 1.3), (None, 0.4),
         (40, 0.7), (45, 1.3), (None, 0.4),
         (40, 0.7), (44, 1.3)])
    ladder = [31, 40, 44, 45, 48, 49, 53, 57, 62, 66, 67, 71, 75, 79, 84]
    add("demo_perde_ladder", [(p, 0.6) for p in ladder[:-1]] + [(84, 1.6)])
    return seqs


def render_12tet(voice: str) -> np.ndarray:
    """G major in 12-TET for the Rast comparison (raw Hz, not commas)."""
    tet = [392.0 * 2 ** (s / 12) for s in [0, 2, 4, 5, 7, 9, 11, 12]]
    beat = 60.0 / BPM
    total = (0.75 * 7 + 1.6) * beat + 0.6
    buf = np.zeros(int(total * SR) + SR // 10)
    cursor = 0.0
    for i, f in enumerate(tet):
        beats = 1.6 if i == len(tet) - 1 else 0.75
        note = tone(f, min(beats * beat * 1.6, beats * beat + 0.5), voice)
        j = int((cursor + 0.02) * SR)
        note = note[: max(0, len(buf) - j)]
        buf[j:j + len(note)] += note
        cursor += beats * beat
    buf *= 0.82 / np.max(np.abs(buf))
    return buf


def generate() -> None:
    seqs = collect_sequences()
    for vname, v in VOICES.items():
        count = 0
        for name, s in seqs.items():
            write_wav(f"{name}.wav",
                      render(s["events"], vname, bpm=s["bpm"], tail=s["tail"]),
                      subdir=v["subdir"])
            count += 1
        write_wav("demo_g_major_12tet.wav", render_12tet(vname),
                  subdir=v["subdir"])
        count += 1
        where = v["subdir"] or "."
        print(f"  {vname}: wrote {count} files to audio/{where}")


def check() -> None:
    md.check()
    for vname in VOICES:
        for commas in (31, 40, 48, 62, 79, 93):
            expected = md.freq(commas)
            sig = tone(expected, 1.0, vname)
            spec = np.abs(np.fft.rfft(sig * np.hanning(len(sig))))
            peak_hz = np.argmax(spec) * SR / len(sig)
            assert abs(peak_hz - expected) < 1.5, (
                f"{vname} commas={commas}: FFT peak {peak_hz:.2f} Hz "
                f"!= expected {expected:.2f} Hz")
        print(f"  {vname}: fundamentals verified at 6 pitches")
    print("generate_audio: synthesis checks passed")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        generate()
