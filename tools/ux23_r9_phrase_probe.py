"""UX23-R9 phrase probe — offline dev tool, NOT in CI.

    ".venv/Scripts/python.exe" tools/ux23_r9_phrase_probe.py

WHAT IT IS FOR. `tools/audio_envelope_probe.gd` answered the *silence* half of
the capped-cue question: every capped cue is present and loud inside its
window. The half nobody could answer without ears is whether a capped MUSICAL
cue ends on a phrase or is cut mid-figure (row UX23-R9).

This does not replace the ear. What it CAN do is measure the thing a phrase
boundary is made of: a bugle call separates its notes with short gaps and ends
a phrase on a noticeably longer one. So take every gap in the envelope, call
the ones materially longer than the median a phrase boundary, and ask where
each cue's `max_s` sits relative to them.

INPUT. The uncapped renders written by `tools/ux23_r9_audition_render.gd` with
`UX23_R9_FULL=1` — plain 16-bit PCM WAV, which the stdlib `wave` module reads,
which is how this sidesteps the venv's missing mp3/ogg decoder.

WHAT IT FOUND (Aug 31, 2026), and why it changed the row: `to_the_color` has
NO phrase-length gap between 0.70 s and 14.52 s, so no cap under ~15 s can end
it on a phrase and the row's own "move `max_s` to the next phrase boundary"
instruction is unsatisfiable for it. See `docs/REV_FOLLOWUPS.md`.
"""

import array
import math
import statistics
import sys
import wave

# The uncapped renders live beside the capped ones, under Godot's user://.
RENDER_DIR = ("C:/Users/User/AppData/Roaming/Godot/app_userdata/"
              "Ink & Iron/ux23_r9/")

WINDOW_S = 0.02          # envelope resolution
FADE_S = 0.8             # `_fade_stop`'s fade, mirrored from audio_manager.gd
GAP_FRACTION = 0.15      # below 15% of peak reads as "between notes"
PHRASE_MIN_S = 0.25      # a gap this long is a phrase boundary, not a tongue

# cue -> max_s, mirrored from audio_manager.gd's CUES. A literal on purpose:
# this is an instrument and must be pointable at a window whose registry entry
# is wrong.
CAPS = {"reveille": 4.2, "to_the_color": 5.2, "fanfare": 5.2}


def envelope(path):
    """Per-window RMS of the left channel, normalised to full scale."""
    with wave.open(path, "rb") as handle:
        rate, count = handle.getframerate(), handle.getnframes()
        pcm = array.array("h")
        pcm.frombytes(handle.readframes(count))
    step = int(rate * WINDOW_S)
    return [
        math.sqrt(sum(pcm[j] * pcm[j] for j in range(i, i + step * 2, 2)) / step)
        / 32768.0
        for i in range(0, len(pcm) - step * 2, step * 2)
    ]


def gaps(env):
    """[(start_s, end_s)] runs where the envelope sits below the gap floor."""
    floor = max(env) * GAP_FRACTION
    out, start = [], None
    for i, value in enumerate(env):
        if value < floor and start is None:
            start = i
        elif value >= floor and start is not None:
            out.append((start * WINDOW_S, i * WINDOW_S))
            start = None
    return out


def report(cue, cap):
    env = envelope(RENDER_DIR + cue + "_FULL.wav")
    peak = max(env)
    runs = gaps(env)
    median = statistics.median([b - a for a, b in runs]) if runs else 0.0
    threshold = max(PHRASE_MIN_S, median * 2.5)
    phrases = [(a, b) for a, b in runs if (b - a) >= threshold]
    index = int(cap / WINDOW_S)

    print("== %s   cap %.1fs   fade ends %.1fs   file %.1fs =="
          % (cue, cap, cap + FADE_S, len(env) * WINDOW_S))
    print("   envelope at the cap      %.0f%% of peak"
          % (100 * env[index] / peak))
    print("   %d gaps, median %.2fs; %d are phrase-length (>= %.2fs)"
          % (len(runs), median, len(phrases), threshold))
    prior = [g for g in phrases if g[1] <= cap]
    later = [g for g in phrases if g[0] > cap]
    if prior:
        print("   last phrase boundary     %.2fs  (%.2fs of a NEW phrase plays "
              "before the fade starts)" % (prior[-1][1], cap - prior[-1][1]))
    if later:
        nxt = later[0][0]
        inside = "INSIDE the fade" if nxt <= cap + FADE_S else "past the fade"
        print("   next phrase boundary     %.2fs  (%+.2fs from the cap, %s)"
              % (nxt, nxt - cap, inside))
    else:
        print("   next phrase boundary     NONE in the rest of the file")
    print()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for name, seconds in CAPS.items():
        report(name, seconds)
