"""Session UI-5 (November 12, 2026) — the audio's loudness and loop seams, measured.

Nobody listens in a session (docs/MUSIC_SOUND_SPEC.md §0.6, §2a), so the ear is
replaced by measurement. This tool reads every file the AudioManager registry
names (CUES, LOOPS, MUSIC, MUSIC_ONESHOTS, ANTHEMS — parsed straight out of
`audio_manager.gd`) and records, per file:

  * integrated loudness (LUFS, ITU-R BS.1770-4 via pyloudnorm) and the sample
    peak (dBFS) — the trims the registry carries are set from these so the
    music rotations sit within ±1 LU of one target and the cues keep one
    ladder (interface quiet < effects < ceremony);
  * for a LOOP, the seam: the level step and the waveform jump where the file
    wraps (end → start) — a seam over the threshold is re-made as a
    crossfaded loop (`--make-loop`), the head blended into the tail.

The project venv has no audio decoder (and no ffmpeg — §0), so this runs in a
side venv with `soundfile` (libsndfile ≥ 1.1 reads OGG Vorbis and MP3) and
`pyloudnorm`:

    python -m venv audiovenv
    audiovenv/Scripts/python -m pip install soundfile pyloudnorm numpy scipy
    audiovenv/Scripts/python -I tools/ui5_audio_prep.py --measure
    audiovenv/Scripts/python -I tools/ui5_audio_prep.py --make-loop SRC DST --xfade 1.5

`--measure` writes docs/audits/audio_loudness_2026_11_12.json (committed);
`tests/test_ui5_full_measure.py` checks every registry file has a row there.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
CLIENT = REPO / "godot-client" / "project-sovereign"
AUDIO = CLIENT / "assets" / "audio"
MANAGER = CLIENT / "scripts" / "audio_manager.gd"
RECORD = REPO / "docs" / "audits" / "audio_loudness_2026_11_12.json"

# The target a music rotation is trimmed to (after the bus and MUSIC_DB), the
# seam thresholds a loop must pass.
MUSIC_TARGET_LUFS = -23.0
SEAM_LEVEL_STEP_DB = 6.0      # RMS of the last 60 ms vs the first 60 ms
SEAM_JUMP = 0.12              # |last sample − first sample| (full scale = 1)


def registry_files() -> dict:
    """{relative path: [roles]} for every file the registry names."""
    src = MANAGER.read_text(encoding="utf-8")
    roles: dict[str, list] = {}

    def add(rel: str, role: str) -> None:
        roles.setdefault(rel, [])
        if role not in roles[rel]:
            roles[rel].append(role)

    def block(name: str) -> str:
        start = src.index(f"const {name} := {{")
        return src[start:src.index("\n}\n", start)]

    for m in re.finditer(r'^\t"([a-z_0-9]+)": \{(.+)\},?\s*$', block("CUES"), re.M):
        for rel in re.findall(r'"([a-z_0-9]+/[^"]+)"', m.group(2)):
            add(rel, "cue:" + m.group(1))
    for m in re.finditer(r'^\t"([a-z_0-9]+)": \{"file": "([^"]+)"', block("LOOPS"), re.M):
        add(m.group(2), "loop:" + m.group(1))
    music = block("MUSIC")
    for key_m in re.finditer(r'"([a-z]+)": \[(.*?)\]', music, re.S):
        for rel in re.findall(r'"(music/[^"]+)"', key_m.group(2)):
            add(rel, "music:" + key_m.group(1))
    for name in ("MUSIC_ONESHOTS", "ANTHEMS"):
        for key, rel in re.findall(r'"([A-Za-z_]+)": "(music/[^"]+)"', block(name)):
            add(rel, name.lower() + ":" + key)
    return roles


def _mono(data):
    import numpy as np
    return data.mean(axis=1) if data.ndim == 2 else data


def measure_file(path: pathlib.Path) -> dict:
    import numpy as np
    import pyloudnorm as pyln
    import soundfile as sf

    data, rate = sf.read(str(path), always_2d=False)
    if data.size == 0:
        return {"error": "empty"}
    peak = float(np.max(np.abs(data)))
    out = {
        "seconds": round(len(data) / rate, 3),
        "rate": int(rate),
        "channels": 1 if data.ndim == 1 else int(data.shape[1]),
        "peak_dbfs": round(20 * math.log10(peak), 2) if peak > 0 else -120.0,
    }
    meter = pyln.Meter(rate)
    # pyloudnorm needs at least one 400 ms block. A short UI tick is TILED to
    # a second (not padded with silence, which would read the gap, not the
    # tick): its integrated loudness is then the loudness of the sound while
    # it sounds — the burst a player hears.
    block = int(1.0 * rate) + 1
    measured = data
    if len(data) < block:
        reps = int(math.ceil(block / max(1, len(data))))
        measured = np.concatenate([data] * reps)[:block]
    try:
        lufs = float(meter.integrated_loudness(measured))
        out["lufs"] = round(lufs, 2) if math.isfinite(lufs) else -70.0
    except ValueError as exc:
        out["lufs"] = -70.0
        out["lufs_note"] = str(exc)
    return out


def seam(path: pathlib.Path) -> dict:
    import numpy as np
    import soundfile as sf

    data, rate = sf.read(str(path), always_2d=False)
    mono = _mono(data)
    n = max(1, int(0.06 * rate))
    tail, head = mono[-n:], mono[:n]

    def rms(x):
        v = float(np.sqrt(np.mean(np.square(x)))) if len(x) else 0.0
        return 20 * math.log10(v) if v > 1e-6 else -120.0

    step = abs(rms(tail) - rms(head))
    jump = float(abs(mono[-1] - mono[0]))
    out = {"level_step_db": round(step, 2), "jump": round(jump, 4),
           "ok": step <= SEAM_LEVEL_STEP_DB and jump <= SEAM_JUMP}
    if not out["ok"] and jump <= SEAM_JUMP:
        # A rhythmic loop (a clock's tick) starts ON a beat, so its head is loud
        # and its tail the quiet between beats — a level step that is no seam
        # when the gap across the wrap is one beat. Measured, not assumed: the
        # onsets' intervals must be regular and the wrap must match them.
        beat = _rhythm(mono, rate)
        if beat:
            out["rhythm"] = beat
            out["ok"] = beat["wrap_matches"]
    if not out["ok"] and jump <= SEAM_JUMP:
        # An impulsive texture (a fire's crackle, footsteps, a creak) steps 10 dB
        # between ANY two neighbouring 60-ms windows: the wrap is a seam only
        # when it jumps more than the file's own texture does (its 95th
        # percentile step across 200 cuts inside the file).
        inner = _inner_steps(mono, n, rms)
        if inner:
            out["texture_p95_db"] = round(inner, 2)
            out["ok"] = step <= inner
    return out


def _inner_steps(mono, n: int, rms) -> float:
    """The 95th percentile of |RMS(before) - RMS(after)| at 200 cuts inside
    the file (two windows of `n` samples either side of each cut)."""
    import numpy as np
    if len(mono) < 4 * n:
        return 0.0
    cuts = np.linspace(n, len(mono) - n, 202)[1:-1].astype(int)
    steps = [abs(rms(mono[c - n:c]) - rms(mono[c:c + n])) for c in cuts]
    return float(np.percentile(steps, 95))


def _rhythm(mono, rate) -> dict:
    """Onsets (an energy envelope over 35 % of its peak, 0.25 s apart); the
    loop is rhythmic when there are 4+ onsets whose intervals sit within 10 %
    of their median, and the wrap (end - last onset + first onset) is within
    10 % of that median."""
    import numpy as np
    env = np.abs(mono)
    win = max(1, int(0.01 * rate))
    smooth = np.convolve(env, np.ones(win) / win, mode="same")
    thr = float(smooth.max()) * 0.35
    onsets, i, gap = [], 0, int(0.25 * rate)
    while i < len(smooth):
        if smooth[i] > thr:
            onsets.append(i / rate)
            i += gap
        else:
            i += 1
    if len(onsets) < 4:
        return {}
    iv = np.diff(onsets)
    med = float(np.median(iv))
    if med <= 0 or float(np.max(np.abs(iv - med))) > 0.1 * med:
        return {}
    wrap = len(mono) / rate - onsets[-1] + onsets[0]
    return {"onsets": len(onsets), "beat_s": round(med, 3), "wrap_s": round(wrap, 3),
            "wrap_matches": abs(wrap - med) <= 0.1 * med}


def make_loop(src: pathlib.Path, dst: pathlib.Path, xfade: float) -> None:
    """A seamless loop: the last `xfade` seconds crossfade (equal power) into
    the head, and the file is cut so its end meets its own blended start."""
    import numpy as np
    import soundfile as sf

    data, rate = sf.read(str(src), always_2d=True)
    n = int(xfade * rate)
    if len(data) <= 3 * n:
        raise SystemExit(f"{src.name}: too short for a {xfade}s crossfade")
    t = np.linspace(0.0, math.pi / 2, n)[:, None]
    fade_in, fade_out = np.sin(t), np.cos(t)
    head = data[:n] * fade_in + data[-n:] * fade_out
    body = np.concatenate([head, data[n:-n]])
    dst.parent.mkdir(parents=True, exist_ok=True)
    # libsndfile's Vorbis encoder overflows the stack on Windows when handed a
    # long buffer in one call (measured: a 54 s take crashed, a 5 s one wrote);
    # write in blocks.
    with sf.SoundFile(str(dst), "w", samplerate=rate, channels=body.shape[1],
                      format="OGG", subtype="VORBIS") as out:
        for start in range(0, len(body), 8192):
            out.write(body[start:start + 8192])
    print(f"looped {src.name} -> {dst} ({len(body) / rate:.2f}s, xfade {xfade}s)")


def run_measure() -> int:
    roles = registry_files()
    rows = {}
    missing = []
    for rel in sorted(roles):
        path = AUDIO / rel.replace("/", "\\" if sys.platform == "win32" else "/")
        if not path.exists():
            missing.append(rel)
            continue
        row = measure_file(path)
        row["roles"] = roles[rel]
        if any(r.startswith("loop:") for r in roles[rel]):
            row["seam"] = seam(path)
        rows[rel] = row
        flag = ""
        if "seam" in row and not row["seam"]["ok"]:
            flag = "  SEAM " + json.dumps(row["seam"])
        print(f"{rel:52s} {row.get('lufs', 0):7.2f} LUFS  peak {row.get('peak_dbfs', 0):6.2f}"
              f"  {row.get('seconds', 0):7.2f}s{flag}")
    music = [r["lufs"] for rel, r in rows.items()
             if any(x.startswith("music:") for x in r["roles"]) and "lufs" in r]
    record = {
        "tool": "tools/ui5_audio_prep.py --measure",
        "standard": "ITU-R BS.1770-4 integrated loudness (pyloudnorm), sample peak",
        "music_target_lufs": MUSIC_TARGET_LUFS,
        "music_spread_lu": round(max(music) - min(music), 2) if music else 0.0,
        "missing": missing,
        "files": rows,
    }
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n{len(rows)} files measured, {len(missing)} missing -> {RECORD}")
    if missing:
        print("missing:", ", ".join(missing))
    return 0


# ── the ladder (`--apply`) ─────────────────────────────────────────────────
# Every cue and loop file is first normalised to REFERENCE_LUFS by its own
# FILE_TRIM_DB entry (a round-robin's variants then match each other — the
# page turns had spread 10 dB, the book's open sat 16 dB under its close);
# a cue's registry "db" is then its CLASS level against that reference. The
# targets are effective loudness before the bus slider — interface quiet,
# effects louder, ceremonies loudest; the beds well under everything.
REFERENCE_LUFS = -20.0
MUSIC_TARGET = -19.0          # every piece the same, Eroica I (the menu) barely moved
PEAK_CEILING_DBFS = -1.0      # a boost never lifts a file's peak past this
CUE_LADDER = {
    "hover": -42, "tick": -34,
    "click": -27, "toggle": -27, "select": -27, "back": -28, "page_turn": -27, "cloth": -29,
    "latch": -27, "paper_slide": -33,
    "panel_open": -27, "panel_close": -27, "book_open": -27, "book_close": -27,
    "parchment_open": -27, "parchment_close": -28, "door_open": -27, "door_close": -27,
    "letter_open": -27,
    "confirm": -25, "error": -25, "question": -25, "notification": -25, "quill_flick": -26,
    "quill_sign": -25, "wax_seal": -24, "command_ack": -26, "paper_crumple": -25,
    "coins_small": -25, "coin_pour": -25, "door_knock": -24, "gavel": -24, "end_turn": -25,
    "cannon": -20, "cannon_distant": -27, "musket_volley": -22, "musket_shot": -25,
    "cavalry": -22, "whinny": -26, "sword_draw": -23, "march_step": -32, "order_march": -27,
    "spade": -25, "drum_cadence": -25, "hammer": -25, "horse_trot": -25, "boots": -26,
    "drum_sting": -21, "bells_peal": -21, "bell_toll": -22, "ship_bell": -24,
    "notification_high": -25, "notification_critical": -23, "crowd_cheer": -23,
    "distant_drums": -33, "reveille": -24, "mail_call": -24, "first_call": -24,
    "to_the_color": -23, "fanfare": -21, "bugle_to_arms": -23, "bugle_charge": -22,
    "bugle_retreat": -24,
}
LOOP_LADDER = {
    "scribble": -33, "scribble_long": -35, "scribble_verdict": -33, "wind": -38, "sea": -31,
    "creak": -37, "crowd": -35, "march": -31, "march_long": -31, "battle_bed": -31,
    "campfire": -39, "fire": -40, "clock": -46, "birds": -40, "rain": -38, "winter_wind": -36,
}
NIB_TARGET = -38.0
NIB_FILES = ["ui/quill_strokes.ogg", "ui/quill_scribble_loop.ogg"]


def _trim(lufs: float, peak: float, target: float, floor: float, headroom: float = 0.0) -> float:
    """The gain that brings a file to `target`, never lifting its peak past
    the ceiling at the level it PLAYS at: `headroom` is how far under 0 dB
    the registry already sets it (music plays MUSIC_DB = -10 dB under its
    bus, so a quiet quartet may rise 10 dB more than a cue before it nears
    the ceiling — the first --apply held four pieces 1.5-3.5 LU short)."""
    gain = target - lufs
    gain = min(gain, PEAK_CEILING_DBFS + headroom - peak)
    return round(max(floor, gain), 1)


def run_apply() -> int:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    files = record["files"]
    if record.get("missing"):
        print("measure first: missing files", record["missing"])
        return 1
    src = MANAGER.read_text(encoding="utf-8")
    music_db = re.search(r"const MUSIC_DB := (-?[0-9.]+)", src)
    music_headroom = -float(music_db.group(1)) if music_db else 0.0
    file_trims: dict[str, float] = {}
    music_trims: dict[str, float] = {}
    for rel, row in files.items():
        roles = row.get("roles", [])
        lufs, peak = float(row.get("lufs", -70.0)), float(row.get("peak_dbfs", 0.0))
        if any(r.startswith(("music:", "music_oneshots:", "anthems:")) for r in roles):
            music_trims[rel] = _trim(lufs, peak, MUSIC_TARGET, -14.0, music_headroom)
        if any(r.startswith(("cue:", "loop:")) for r in roles) or rel in NIB_FILES:
            file_trims[rel] = _trim(lufs, peak, REFERENCE_LUFS, -24.0)
    for rel in NIB_FILES:
        if rel not in file_trims:
            path = AUDIO / rel
            if path.exists():
                row = measure_file(path)
                file_trims[rel] = _trim(row["lufs"], row["peak_dbfs"], REFERENCE_LUFS, -24.0)

    def set_db(match: re.Match, ladder: dict, default_none=True) -> str:
        name, body = match.group(1), match.group(2)
        if name not in ladder:
            return match.group(0)
        db = round(float(ladder[name]) - REFERENCE_LUFS, 1)
        new_body = re.sub(r'"db": -?[0-9.]+', f'"db": {db}', body, count=1)
        return match.group(0).replace(body, new_body)

    def rewrite_block(text: str, name: str, ladder: dict, pattern: str) -> str:
        start = text.index(f"const {name} := {{")
        end = text.index("\n}\n", start)
        block = text[start:end]
        block = re.sub(pattern, lambda m: set_db(m, ladder), block, flags=re.M)
        return text[:start] + block + text[end:]

    src = rewrite_block(src, "CUES", CUE_LADDER, r'^\t"([a-z_0-9]+)": \{(.+)\},?\s*$')
    src = rewrite_block(src, "LOOPS", LOOP_LADDER, r'^\t"([a-z_0-9]+)": \{("file".+)\},?\s*$')
    src = re.sub(r"const NIB_DB := -?[0-9.]+", f"const NIB_DB := {round(NIB_TARGET - REFERENCE_LUFS, 1)}", src)

    def dict_block(name: str, trims: dict) -> str:
        rows = "".join(f'\t"{k}": {v},\n' for k, v in sorted(trims.items()))
        return f"const {name} := {{\n{rows}}}\n"

    generated = ("# <ui5-trims> generated by tools/ui5_audio_prep.py --apply from\n"
                 "# docs/audits/audio_loudness_2026_11_12.json — do not edit by hand.\n"
                 + dict_block("FILE_TRIM_DB", file_trims) + dict_block("MUSIC_TRIM_DB", music_trims)
                 + "# </ui5-trims>")
    src = re.sub(r"# <ui5-trims>.*?# </ui5-trims>", lambda _m: generated, src, flags=re.S)
    MANAGER.write_text(src, encoding="utf-8", newline="\n")
    record["reference_lufs"] = REFERENCE_LUFS
    record["music_target"] = MUSIC_TARGET
    record["file_trim_db"] = file_trims
    record["music_trim_db"] = music_trims
    record["cue_ladder"] = CUE_LADDER
    record["loop_ladder"] = LOOP_LADDER
    RECORD.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    after = [files[r]["lufs"] + music_trims[r] for r in music_trims if r in files]
    print(f"applied: {len(file_trims)} file trims, {len(music_trims)} music trims; "
          f"music after trims spans {min(after):.2f}..{max(after):.2f} LUFS")
    return 0


# ── the envelopes (`--envelope`) ───────────────────────────────────────────
# The question tools/audio_envelope_probe.gd asks of the August caps (does the
# sound sit INSIDE the window a cue plays?), asked of every capped cue by
# decoding offline (libsndfile) instead of playing through Godot in real time.
ENVELOPE_RECORD = REPO / "docs" / "audits" / "audio_envelope_ui5_2026_11_13.json"
WINDOW_S = 0.05


def run_envelope() -> int:
    import numpy as np
    import soundfile as sf

    src = MANAGER.read_text(encoding="utf-8")
    start = src.index("const CUES := {")
    block = src[start:src.index("\n}\n", start)]
    rows = []
    for m in re.finditer(r'^\t"([a-z_0-9]+)": \{(.+)\},?\s*$', block, re.M):
        cue, spec = m.group(1), m.group(2)
        cap = re.search(r'"max_s":\s*([0-9.]+)', spec)
        if not cap:
            continue
        offset = re.search(r'"start_s":\s*([0-9.]+)', spec)
        for rel in re.findall(r'"([a-z_0-9]+/[^"]+)"', spec):
            path = AUDIO / rel
            if not path.exists():
                rows.append({"cue": cue, "file": rel, "verdict": "missing"})
                continue
            data, rate = sf.read(str(path), always_2d=True)
            mono = data.mean(axis=1)
            n = max(1, int(WINDOW_S * rate))
            frames = len(mono) // n
            env = np.sqrt(np.mean(np.square(mono[:frames * n].reshape(frames, n)), axis=1)) if frames else np.zeros(1)
            peak = float(env.max()) if env.size else 0.0
            s0 = float(offset.group(1)) if offset else 0.0
            c = float(cap.group(1))
            lo, hi = int(s0 / WINDOW_S), int((s0 + c) / WINDOW_S)
            inside = env[lo:hi] if hi > lo else env[:1]
            onset_idx = int(np.argmax(env >= peak * 0.1)) if peak > 0 else 0
            onset = onset_idx * WINDOW_S
            inside_peak = float(inside.max()) if inside.size else 0.0
            ok = peak > 0 and onset < s0 + c * 0.6 and inside_peak >= peak * 0.35
            rows.append({
                "cue": cue, "file": rel, "max_s": c, "start_s": s0,
                "onset_s": round(onset, 2), "peak_in_window_frac": round(inside_peak / peak, 3) if peak else 0.0,
                "verdict": "sound inside the window" if ok else "CHECK: the window misses the sound",
            })
    bad = [r for r in rows if not str(r["verdict"]).startswith("sound inside")]
    ENVELOPE_RECORD.write_text(json.dumps({"tool": "tools/ui5_audio_prep.py --envelope",
                                           "window_s": WINDOW_S, "rows": rows}, indent=1) + "\n",
                               encoding="utf-8")
    for r in rows:
        print(f"{r['cue']:24s} {r['file']:44s} {r['verdict']}  onset {r.get('onset_s', '-')}")
    print(f"\n{len(rows)} capped files, {len(bad)} to check -> {ENVELOPE_RECORD}")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--envelope", action="store_true",
                    help="check every capped cue's sound sits inside its window")
    ap.add_argument("--apply", action="store_true",
                    help="write the trims and the class ladder into audio_manager.gd")
    ap.add_argument("--make-loop", nargs=2, metavar=("SRC", "DST"))
    ap.add_argument("--xfade", type=float, default=1.5)
    args = ap.parse_args()
    if args.make_loop:
        make_loop(pathlib.Path(args.make_loop[0]), pathlib.Path(args.make_loop[1]), args.xfade)
        return 0
    if args.measure:
        return run_measure()
    if args.apply:
        return run_apply()
    if args.envelope:
        return run_envelope()
    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
