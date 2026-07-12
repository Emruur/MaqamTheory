"""Generate all WAV files for the maqam learning site.

Usage:
    python3 tools/generate_audio.py           # write audio/*.wav
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
BEAT = 60.0 / BPM

# Harmonic recipe for the "warm synth" tone: (harmonic number, amplitude).
HARMONICS = [(1, 1.0), (2, 0.42), (3, 0.28), (4, 0.12), (5, 0.08), (6, 0.045)]


def tone(freq: float, dur: float, velocity: float = 1.0) -> np.ndarray:
    """One warm synthesized note: additive harmonics, soft attack, gentle decay."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    # Delayed, subtle vibrato (starts after ~0.25 s).
    vib_depth = 0.0025 * np.clip((t - 0.25) / 0.35, 0, 1)
    inst_freq = freq * (1 + vib_depth * np.sin(2 * np.pi * 5.2 * t))
    phase = 2 * np.pi * np.cumsum(inst_freq) / SR
    sig = np.zeros(n)
    for k, amp in HARMONICS:
        # Higher harmonics decay a bit faster for a rounder sustain.
        sig += amp * np.exp(-t * 0.9 * k) * np.sin(k * phase)
    attack = np.minimum(t / 0.028, 1.0)
    decay = np.exp(-t * 1.4)
    release_len = min(0.06, dur / 4)
    release = np.clip((dur - t) / release_len, 0, 1)
    return velocity * sig * attack * decay * release


def render(events: list[tuple[float | None, float]], gap: float = 0.02,
           tail: float = 0.6) -> np.ndarray:
    """Render (commas, beats) events into one buffer. commas=None is a rest.

    Notes ring slightly past their slot (legato) by rendering each note
    1.6x its nominal length and mixing into a shared buffer.
    """
    total = sum(beats for _, beats in events) * BEAT + tail
    buf = np.zeros(int(total * SR) + SR // 10)
    cursor = 0.0
    for commas, beats in events:
        slot = beats * BEAT
        if commas is not None:
            dur = min(slot * 1.6, slot + 0.5)
            note = tone(md.freq(commas), dur)
            i = int((cursor + gap) * SR)
            note = note[: max(0, len(buf) - i)]
            buf[i:i + len(note)] += note
        cursor += slot
    peak = np.max(np.abs(buf))
    if peak > 0:
        buf *= 0.82 / peak
    return buf


def write_wav(name: str, buf: np.ndarray) -> None:
    OUT.mkdir(exist_ok=True)
    data = (np.clip(buf, -1, 1) * 32767).astype("<i2")
    with wave.open(str(OUT / name), "wb") as w:
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


def generate() -> None:
    files = 0

    def out(name, events):
        nonlocal files
        write_wav(name, render(events))
        files += 1

    for key, m in md.MAKAMLAR.items():
        asc, desc = m["asc"], m["desc"]
        out(f"{key}_scale_asc.wav", scale_events(asc))
        out(f"{key}_scale_desc.wav", scale_events(list(reversed(desc))))
        # Quiz version: continuous up-and-down, slightly brisker.
        updown = asc + list(reversed(desc))[1:]
        out(f"{key}_quiz.wav", [(p, 0.6) for p in updown[:-1]] + [(updown[-1], 1.6)])
        # Genus segments.
        for part in ("lower_genus", "upper_genus"):
            _, genus_name, root = m[part]
            pitches = md.steps_to_scale(root, md.GENUS[genus_name])
            out(f"{key}_{part}.wav", scale_events(pitches))
        out(f"{key}_seyir.wav", m["seyir"])

    # Individual notes, shared across makams, keyed by comma value.
    needed = set()
    for m in md.MAKAMLAR.values():
        needed.update(m["asc"])
        needed.update(m["desc"])
        needed.add(m["yeden"])
    for name, (genus_name, root) in md.GENUS_DEMOS.items():
        needed.update(md.steps_to_scale(root, md.GENUS[genus_name]))
    for commas in sorted(needed):
        write_wav(f"note_{commas}.wav", render([(commas, 1.4)], tail=0.4))
        files += 1

    # Chapter 4: every genus type on the same root (dugah).
    for name, (genus_name, root) in md.GENUS_DEMOS.items():
        pitches = md.steps_to_scale(root, md.GENUS[genus_name])
        out(f"genus_{name}.wav", scale_events(pitches))

    # Chapter 2 demos.
    # The whole tone dugah->buselik split into 9 single-comma steps.
    out("demo_comma_steps.wav",
        [(40 + i, 0.55) for i in range(9)] + [(49, 1.4)])
    # One comma in isolation: A, then A one comma higher, alternating.
    out("demo_one_comma.wav",
        [(40, 1.2), (41, 1.2), (40, 1.2), (41, 1.6)])
    # The four B's between A and B natural: buselik, segah, dik kurdi, kurdi.
    out("demo_b_variants.wav",
        [(40, 0.7), (49, 1.5), (None, 0.5),
         (40, 0.7), (48, 1.5), (None, 0.5),
         (40, 0.7), (45, 1.5), (None, 0.5),
         (40, 0.7), (44, 1.5)])
    # Tanini (9), buyuk mucenneb (8), kucuk mucenneb (5), bakiye (4) from dugah.
    out("demo_intervals.wav",
        [(40, 0.7), (49, 1.3), (None, 0.4),
         (40, 0.7), (48, 1.3), (None, 0.4),
         (40, 0.7), (45, 1.3), (None, 0.4),
         (40, 0.7), (44, 1.3)])
    # Chapter 3: the perde ladder from rast to gerdaniye (main pitches).
    ladder = [31, 40, 44, 45, 48, 49, 53, 57, 62, 66, 67, 71, 75, 79, 84]
    out("demo_perde_ladder.wav", [(p, 0.6) for p in ladder[:-1]] + [(84, 1.6)])
    # 12-TET major scale on G for comparison with Rast (chapter 5).
    tet = [392.0 * 2 ** (s / 12) for s in [0, 2, 4, 5, 7, 9, 11, 12]]
    # Rendered by hand since render() works in commas, not Hz.
    total = (0.75 * 7 + 1.6) * BEAT + 0.6
    buf = np.zeros(int(total * SR) + SR // 10)
    cursor = 0.0
    for i, f in enumerate(tet):
        beats = 1.6 if i == len(tet) - 1 else 0.75
        note = tone(f, min(beats * BEAT * 1.6, beats * BEAT + 0.5))
        j = int((cursor + 0.02) * SR)
        buf[j:j + len(note)] += note
        cursor += beats * BEAT
    buf *= 0.82 / np.max(np.abs(buf))
    write_wav("demo_g_major_12tet.wav", buf)
    files += 1

    print(f"wrote {files} files to {OUT}")


def check() -> None:
    md.check()
    # Verify synthesized fundamental via FFT for a few pitches.
    for commas in (31, 40, 48, 62, 79, 93):
        expected = md.freq(commas)
        sig = tone(expected, 1.0)
        spec = np.abs(np.fft.rfft(sig * np.hanning(len(sig))))
        peak_hz = np.argmax(spec) * SR / len(sig)
        assert abs(peak_hz - expected) < 1.5, (
            f"commas={commas}: FFT peak {peak_hz:.2f} Hz != expected {expected:.2f} Hz")
        print(f"  commas {commas:>3}: expected {expected:8.2f} Hz, "
              f"FFT peak {peak_hz:8.2f} Hz  ok")
    print("generate_audio: synthesis checks passed")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        generate()
