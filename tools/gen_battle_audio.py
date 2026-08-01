"""Generate the Battle Diorama's drum sting (row BD) — offline dev tool.

The eval memo (BATTLE_DIORAMA_EVAL_2026_07_17.md §3) documented that no
period drum/fife sting exists in the downloaded CC0 packs — the RPG pack's
closest asset is a metal pot. Rather than ship a cooking sound as a military
snare, this synthesizes one: the same own-pipeline route the war-table
pieces took (tools/gen_war_table_pieces.py — deterministic, offline,
self-authored, CC0-clean, NOT in requirements/CI).

Output: godot-client/project-sovereign/assets/audio/battle/drum_sting.wav
    A field snare: a five-stroke crescendo roll into two accent strokes —
    the cadence a court-martial drummer closes on. ~1.5 s, 44.1 kHz mono.

Model: each stroke = a burst of exponentially-decaying filtered noise
(the wires) + a damped 180-330 Hz body tone (the shell). Deterministic
seed so the artifact is reproducible byte-for-byte.

Run:  .venv/Scripts/python.exe tools/gen_battle_audio.py
"""

import wave
from pathlib import Path

import numpy as np

SAMPLE_RATE = 44100
OUT = (Path(__file__).resolve().parent.parent / "godot-client"
       / "project-sovereign" / "assets" / "audio" / "battle"
       / "drum_sting.wav")

rng = np.random.default_rng(1805)  # the campaign year


def _snare_stroke(duration: float, strength: float, snap: float) -> np.ndarray:
    """One snare stroke: noise wires + shell body, exponential decay."""
    n = int(duration * SAMPLE_RATE)
    t = np.arange(n) / SAMPLE_RATE

    # The wires: white noise, band-shaped by differencing (brightens),
    # decaying fast.
    noise = rng.standard_normal(n)
    noise = np.diff(noise, prepend=0.0) * 0.7 + noise * 0.3
    wires = noise * np.exp(-t * (34.0 + 26.0 * snap))

    # The shell: two damped partials around the drum's fundamental.
    shell = (np.sin(2 * np.pi * 184.0 * t) * 0.55
             + np.sin(2 * np.pi * 331.0 * t) * 0.30)
    shell *= np.exp(-t * 46.0)

    # Stick attack transient.
    attack = np.exp(-t * 900.0)

    return strength * (wires * 0.72 + shell * 0.55 + attack * 0.35)


def build_sting() -> np.ndarray:
    total = int(1.55 * SAMPLE_RATE)
    out = np.zeros(total)

    # The crescendo roll: eight grace strokes tightening and swelling.
    t0 = 0.02
    gap = 0.085
    for i in range(8):
        strength = 0.18 + 0.055 * i
        stroke = _snare_stroke(0.16, strength, snap=0.4 + 0.05 * i)
        start = int(t0 * SAMPLE_RATE)
        end = min(start + stroke.size, total)
        out[start:end] += stroke[: end - start]
        gap *= 0.93          # the roll tightens
        t0 += gap

    # The two closing accents — the gavel itself.
    for accent_t, strength in ((t0 + 0.10, 0.95), (t0 + 0.34, 1.15)):
        stroke = _snare_stroke(0.42, strength, snap=1.0)
        start = int(accent_t * SAMPLE_RATE)
        end = min(start + stroke.size, total)
        out[start:end] += stroke[: end - start]

    # A low field-drum boom under the final accent (the regiment's timpani).
    boom_start = int((t0 + 0.34) * SAMPLE_RATE)
    bn = total - boom_start
    bt = np.arange(bn) / SAMPLE_RATE
    boom = np.sin(2 * np.pi * 72.0 * bt) * np.exp(-bt * 9.0) * 0.5
    out[boom_start:] += boom

    # Normalize with headroom, gentle fade-out tail.
    out = out / np.max(np.abs(out)) * 0.82
    fade = np.linspace(1.0, 0.0, int(0.12 * SAMPLE_RATE))
    out[-fade.size:] *= fade
    return out


def main() -> None:
    data = build_sting()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(data, -1.0, 1.0) * 32767).astype("<i2")
    with wave.open(str(OUT), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(pcm.tobytes())
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
