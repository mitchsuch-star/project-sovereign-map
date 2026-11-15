"""Row BA, BA-1 "the battle in acts" — the client walk (Mode C, driven).

Plays the REAL tableau (`battle_diorama.tscn`) through the acts of the
battles `tools/ba1_stage_battles.py` staged, and reads the record
`tools/ba1_acts_walk.gd` writes per frame.

    .venv/Scripts/python.exe tools/ba1_stage_battles.py        # the payloads
    .venv/Scripts/python.exe tools/ba1_acts_walk.py            # the walk
    .venv/Scripts/python.exe tools/ba1_acts_walk.py --only ulm_full
    .venv/Scripts/python.exe tools/ba1_acts_walk.py --scale 2.0 --tag x2

A whole walk writes `docs/audits/ba1_client/walk_record.json` (every shot's
record) and the curated frames `docs/audits/ba1_client/BA1_*.jpg`; every
frame of the run stays in the temp folder the tool names. An `--only` or a
tagged run writes its record beside it and leaves the committed one alone.

The walk FAILS (exit 1) when the engine logged a SCRIPT ERROR, a shot did not
complete, or one of the walk's own claims does not hold. The claims are read
off the engine's record, never off a picture:

  * the acts END where the settled frame stands — every corps at its place
    plus its resting offset, its pips counted, a beaten plinth turned down,
    the dice on the baize, no act still named;
  * a CLICK on the tableau mid-act (a real one, at its centre) gives that
    frame at once, and so does one on the dark margin (BA1-X5); a click on
    the settled tableau changes nothing; 'Final frame only' and Reduce
    motion open on it; Replay then plays the acts;
  * 'Brief always' tells fewer developments than the full form and ends on
    the same table;
  * every act the battle's script carries is told on the table;
  * a corps that marches in starts off its place and unseen; an enemy corps
    comes up DARK, with no name, and is made out when it arrives;
  * a payload from before the acts (an old save's) plays the tableau's first
    sequence and settles with plinths and no dice;
  * BA1-X1: no strength line carries the advance's toll; the toll is told
    under the lead's feet;
  * BA1-X6: when the acts open, every corps' line reads what it BROUGHT and
    no line on the baize says where a corps will end (no arrow, no toll);
    mid-fight the line is running; at the end it reads brought → kept. Its
    siblings: the baize wears no result's cast, no laurel flanks the plate
    and the reserve's dead are not told until the gavel — and then they are;
  * the chrome is whole for the NEXT battle: a click in the tableau's first
    instant, or Esc mid-act and then another battle on the same tableau
    (settled, or one from before the acts), shows the tray opaque, the
    laurels and the cast as the settled frame has them.

`run()` and `check()` are also the suite's driven pin
(tests/test_ba1_the_battle_in_acts.py: headless, the record only, the scene
run eight times faster).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "godot-client" / "project-sovereign"
OUT = ROOT / "docs" / "audits" / "ba1_client"
PAYLOADS = OUT / "payloads"
RUN = Path(tempfile.gettempdir()) / "ba1_acts_walk"
GODOT_DEFAULT = r"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe\Godot_v4.4.1-stable_win64.exe"

ACTS = ("approach", "cannonade", "assault", "crisis", "pursuit")

# The development each scene was staged for, shot at its own moment.
SCENE_BEATS = {
    "ulm_full": [
        {"beat": "arrive", "after": 0.45, "shot": "marching_in"},
        {"beat": "advance", "after": 0.5, "shot": "the_lead_goes_in"},
        {"beat": "dice", "after": 0.3, "shot": "dice_tumbling"},
        {"beat": "break", "after": 0.7, "shot": "the_line_breaks"},
        {"beat": "leave", "after": 0.95, "shot": "driven_back"},
    ],
    "the_capitulation": [{"beat": "break", "after": 0.9, "shot": "taken"}],
    "last_hour": [{"beat": "arrive", "where": {"late": True}, "after": 0.7, "shot": "last_hour"}],
    "the_flank": [{"beat": "flank", "after": 1.2, "shot": "flank"}],
    "enemy_comes": [
        {"beat": "arrive", "where": {"concealed": True}, "after": 0.3, "shot": "coming_up"},
        {"beat": "arrive", "where": {"concealed": True}, "after": 1.6, "shot": "made_out"},
    ],
    "the_day_hangs": [{"beat": "stand", "after": 0.8, "shot": "stand"}],
    "the_guns": [{"beat": "battery", "after": 0.8, "shot": "battery"}],
}

# The frames a whole walk keeps in the repo: (shot id, tag, file stem).
CURATED = [
    ("ulm_full", "opening", "01_ulm_the_two_leads"),
    ("ulm_full", "marching_in", "02_ulm_a_corps_marches_in"),
    ("ulm_full", "the_lead_goes_in", "03_ulm_ney_goes_in_ahead"),
    ("ulm_full", "dice_tumbling", "04_ulm_the_dice"),
    ("ulm_full", "the_line_breaks", "05_ulm_the_line_breaks"),
    ("ulm_full", "driven_back", "06_ulm_driven_back"),
    ("ulm_full", "end", "07_ulm_the_field_at_rest"),
    ("last_hour", "last_hour", "08_the_last_hour"),
    ("the_flank", "flank", "09_the_flank"),
    ("the_guns", "battery", "10_the_guns"),
    ("enemy_comes", "coming_up", "11_an_enemy_corps_comes_up_unseen"),
    ("enemy_comes", "made_out", "12_it_is_made_out"),
    ("the_capitulation", "end", "13_mack_taken"),
    ("the_day_hangs", "end", "14_the_day_hangs"),
    ("defeat_defending", "end", "15_a_defeat_on_the_defence"),
    ("observed_full", "end", "16_another_courts_battle"),
    ("ordinary_brief", "end", "17_an_ordinary_battle_in_brief"),
    ("ulm_full__old_payload", "end", "18_a_battle_from_before_the_acts"),
    ("four_a_side", "end", "19_four_corps_a_side_at_rest"),
]

SOURCES = [
    "godot-client/project-sovereign/scripts/battle_acts.gd",
    "godot-client/project-sovereign/scripts/diorama_plinth.gd",
    "godot-client/project-sovereign/scripts/battle_diorama.gd",
    "backend/game_logic/battle_script.py",
    "tools/ba1_acts_walk.gd",
]


def scene_events(name: str) -> list[dict]:
    return ([{"t": 0.4, "shot": "opening"}]
            + [{"act": act, "after": 0.9, "shot": act} for act in ACTS]
            + list(SCENE_BEATS.get(name, []))
            + [{"end": True, "after": 2.8, "shot": "end"}])


def build_shots(payload_dir: Path, only: list[str], scale: float) -> list[dict]:
    manifest = json.loads((payload_dir / "manifest.json").read_text(encoding="utf-8"))
    shots = []
    for name, row in manifest.items():
        if only and not any(o in name for o in only):
            continue
        payload = str(payload_dir / f"{name}.json")
        shots.append({"id": name, "scene": name, "payload": payload, "mode": "acts",
                      "cinematic": True, "scale": scale, "events": scene_events(name)})
        # the settled frame of the same battle (a second viewing)
        shots.append({"id": f"{name}__settled", "scene": name, "payload": payload,
                      "mode": "acts", "cinematic": False, "scale": scale,
                      "events": [{"t": 0.6, "frames": 4, "shot": "settled"}]})
    if "ulm_full" in manifest and (not only or any(o in "ulm_full" for o in only)):
        ulm = str(payload_dir / "ulm_full.json")
        common = {"scene": "ulm_full", "payload": ulm, "scale": scale}
        shots += [
            # the player's click ON the tableau, mid-act (BA1-X5), then one more
            # on the settled table
            {**common, "id": "ulm_full__skip", "mode": "acts", "cinematic": True,
             "events": [{"t": 2.6, "shot": "before"}, {"t": 2.7, "do": "click"},
                        {"t": 3.3, "shot": "after"}, {"t": 3.4, "do": "click"},
                        {"t": 3.9, "shot": "after_a_second_click"}]},
            # … and on the dark margin round it
            {**common, "id": "ulm_full__skip_margin", "mode": "acts", "cinematic": True,
             "events": [{"t": 2.6, "shot": "before"}, {"t": 2.7, "do": "click_margin"},
                        {"t": 3.3, "shot": "after"}]},
            # Settings -> Battle scenes -> Brief always, on a great battle
            {**common, "id": "ulm_full__brief_always", "mode": "brief", "cinematic": True,
             "events": [{"t": 0.4, "shot": "opening"}, {"end": True, "after": 2.8, "shot": "end"}]},
            # Settings -> Battle scenes -> Final frame only, then Replay
            {**common, "id": "ulm_full__final_only", "mode": "final", "cinematic": True,
             "events": [{"t": 0.6, "shot": "opened"}, {"t": 0.7, "do": "replay"},
                        {"act": "approach", "after": 0.9, "shot": "replaying"},
                        {"end": True, "after": 2.8, "shot": "end"}]},
            # Settings -> Reduce motion: the battle opens as it ended
            {**common, "id": "ulm_full__reduce_motion", "mode": "acts", "cinematic": True,
             "reduce_motion": True, "events": [{"t": 0.6, "shot": "opened"}]},
            # a payload from before the acts (an old save's battle): no script
            {**common, "id": "ulm_full__old_payload", "mode": "acts", "cinematic": True,
             "strip_script": True, "events": [{"t": 1.2, "shot": "playing"},
                                              {"t": 6.5, "shot": "end"}]},
            # a click in the tableau's first instant, while it still fades in: the
            # settled frame stands whole (the tray used to be left part-faded)
            {**common, "id": "ulm_full__skip_at_once", "mode": "acts", "cinematic": True,
             "events": [{"t": 0.06, "shot": "fading_in"}, {"t": 0.08, "do": "click"},
                        {"t": 0.5, "shot": "after"}]},
            # closed mid-act (Esc); the same tableau then shows a battle from before
            # the acts — nothing the interrupted showing held back is missing from it
            {**common, "id": "ulm_full__closed_then_old", "mode": "acts", "cinematic": True,
             "events": [{"t": 2.6, "shot": "before"}, {"t": 2.7, "do": "close"},
                        {"t": 2.9, "do": "reopen", "cinematic": True, "strip_script": True},
                        {"t": 1.2, "shot": "playing"}, {"t": 6.5, "shot": "end"}]},
            # … closed in its first instant, and then opened settled
            {**common, "id": "ulm_full__closed_then_settled", "mode": "acts", "cinematic": True,
             "events": [{"t": 0.06, "shot": "fading_in"}, {"t": 0.08, "do": "close"},
                        {"t": 0.3, "do": "reopen", "cinematic": False},
                        {"t": 0.6, "shot": "seen_again"}]},
        ]
    return shots


def run(shots: list[dict], godot: str, work: Path, *, headless: bool = False,
        time_scale: float = 1.0) -> tuple[dict, list[str]]:
    """Run the harness over `shots`; returns (its result JSON, SCRIPT ERROR lines)."""
    work.mkdir(parents=True, exist_ok=True)
    spec_path, result_path, log_path = work / "spec.json", work / "result.json", work / "engine.log"
    for stale in (result_path, log_path):
        if stale.exists():
            stale.unlink()
    spec_path.write_text(json.dumps({
        "out": str(work), "result": str(result_path), "window": [1600, 900],
        "time_scale": time_scale, "record_only": headless, "shots": shots}, indent=1),
        encoding="utf-8")
    env = dict(os.environ, BA1_SPEC=str(spec_path))
    cmd = [godot, "--audio-driver", "Dummy"]
    cmd += ["--headless"] if headless else ["--windowed", "--resolution", "1600x900",
                                             "--position", "5200,20"]
    cmd += ["--log-file", str(log_path), "--path", str(PROJECT),
            "--script", "../../tools/ba1_acts_walk.gd"]
    budget = 120 + len(shots) * (40.0 / max(time_scale, 0.1) + 4.0)
    subprocess.run(cmd, cwd=str(ROOT), env=env, timeout=budget)
    result = json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else {}
    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    body = log.split("[BA1] BEGIN", 1)[-1]
    errors = [ln.strip() for ln in body.splitlines() if "SCRIPT ERROR" in ln]
    return result, errors


# ── the claims ──────────────────────────────────────────────────────────────

def _frame(res: dict, tag: str) -> dict:
    for row in (res or {}).get("frames") or []:
        if row.get("tag") == tag:
            return row
    return {}


def _at_rest(frame: dict) -> list[str]:
    """Every corps where the settled frame has it."""
    wrong = []
    for c in frame.get("corps") or []:
        if c["x"] != c["home_x"] + c["rest_dx"] or c["alpha_pct"] != 100 or c.get("dark"):
            wrong.append(f"{c['name']} at x={c['x']} a={c['alpha_pct']}% dark={c.get('dark')} "
                         f"(rest {c['home_x'] + c['rest_dx']})")
        if c["face_down"] != (c["status"] in ("routed", "destroyed")):
            wrong.append(f"{c['name']} plinth face_down={c['face_down']} for status {c['status']}")
    return wrong


def _table(frame: dict) -> list:
    return [(c["name"], c["x"], c["y"], c["pips_lost"], c["face_down"])
            for c in frame.get("corps") or []]


def _toll_claims(rid: str, frame: dict, payload: dict) -> list[str]:
    """BA1-X1: the advance's toll is told under the feet, never on the strength line."""
    wrong = []
    labels = frame.get("labels") or []
    for label in labels:
        if label.endswith(" after the advance") and label.count(" → ") >= 2:
            wrong.append(f"{rid}: a strength line still carries the advance's toll ({label!r})")
    for side in ("attacker", "defender"):
        for c in (payload.get(side) or {}).get("contingents") or []:
            if "after_advance" in c and int(c.get("advance_losses", 0) or 0) > 0:
                want = f"→ {int(c['after_advance']):,} after the advance"
                if want not in labels:
                    wrong.append(f"{rid}: {c.get('name')}'s toll {want!r} is not on the table")
    return wrong


def _on_the_table(frame: dict, payload: dict) -> list[dict]:
    """The payload's corps that stand on this table (the rest are in reserve)."""
    names = {c["name"] for c in frame.get("corps") or []}
    return [c for side in ("attacker", "defender")
            for c in (payload.get(side) or {}).get("contingents") or []
            if c.get("name") in names]


def _settled_strength_claims(rid: str, frame: dict, payload: dict) -> list[str]:
    """At rest every corps' line reads what it brought and what it kept."""
    labels = frame.get("labels") or []
    return [f"{rid}: {c.get('name')}'s line "
            f"{int(c.get('committed', 0) or 0):,} → {int(c.get('remaining', 0) or 0):,} is not on the table"
            for c in _on_the_table(frame, payload)
            if f"{int(c.get('committed', 0) or 0):,} → {int(c.get('remaining', 0) or 0):,}" not in labels]


def _opening_strength_claims(rid: str, frame: dict, payload: dict) -> list[str]:
    """BA1-X6: when the acts open, no line says where a corps will end."""
    wrong = [f"{rid}: at the opening a line already tells the end ({m['text']!r})"
             for m in frame.get("marks") or [] if m["kind"] == "text" and "→" in m["text"]]
    labels = frame.get("labels") or []
    wrong += [f"{rid}: at the opening {c.get('name')}'s line is not what he brought "
              f"({int(c.get('committed', 0) or 0):,})"
              for c in _on_the_table(frame, payload)
              if f"{int(c.get('committed', 0) or 0):,}" not in labels]
    # its siblings: the defeat's cast on the baize, the laurels of a triumph,
    # what the corps in reserve lost
    if frame.get("vignette") != NEUTRAL_CAST:
        wrong.append(f"{rid}: at the opening the baize already wears the result's cast "
                     f"({frame.get('vignette')})")
    if frame.get("laurels"):
        wrong.append(f"{rid}: at the opening the laurels already flank the plate")
    wrong += [f"{rid}: at the opening the reserve's dead are already told ({m['text']!r})"
              for m in frame.get("marks") or []
              if m["kind"] == "text" and "in reserve" in m["text"] and "lost" in m["text"]]
    return wrong


NEUTRAL_CAST = "ffffffff"


def _the_end_claims(rid: str, end: dict, settled: dict, payload: dict) -> list[str]:
    """What the opening held back is on the table when the acts end, as the
    settled frame has it — and the staged battles really do carry each."""
    wrong = []
    for key in ("vignette", "laurels"):
        if end.get(key) != settled.get(key):
            wrong.append(f"{rid}: {key} is {end.get(key)!r} at the end and "
                         f"{settled.get(key)!r} on the settled frame")
    register = payload.get("register")
    if (settled.get("laurels", 0) == 2) != (register == "triumph"):
        wrong.append(f"{rid}: {settled.get('laurels')} laurels on a {register!r}")
    if (settled.get("vignette") != NEUTRAL_CAST) != (register == "defeat"):
        wrong.append(f"{rid}: the baize's cast is {settled.get('vignette')!r} on a {register!r}")

    def tails(frame):
        return sorted(m["text"] for m in frame.get("marks") or []
                      if m["kind"] == "text" and "in reserve" in m["text"])
    if tails(end) != tails(settled):
        wrong.append(f"{rid}: the reserve's line is {tails(end)} at the end and "
                     f"{tails(settled)} on the settled frame")
    for side in ("attacker", "defender"):
        dead = int((payload.get(side) or {}).get("reserve_casualties", 0) or 0)
        if dead > 0 and int((payload.get(side) or {}).get("reserve_count", 0) or 0) > 0 \
                and not any(f"{dead:,} lost" in t for t in tails(settled)):
            wrong.append(f"{rid}: the {side}'s reserve lost {dead:,} and the settled frame "
                         f"does not say so ({tails(settled)})")
    return wrong


def _chrome_claims(by_id: dict) -> list[str]:
    """BA1-X6's own leak, and the one the first sequence always had: the tray,
    the laurels and the baize's cast are CHROME (built once), so a showing
    that is cut short — a click in its first instant, Esc mid-act — must not
    leave them as it had them for the battle shown next."""
    settled = _frame(by_id.get("ulm_full__settled"), "settled")
    if not settled:
        return []
    wrong = []

    def whole(frame: dict) -> bool:
        return bool(frame.get("final") and frame.get("visible")
                    and frame.get("tray_alpha_pct") == 100
                    and frame.get("laurels") == settled.get("laurels")
                    and frame.get("vignette") == settled.get("vignette")
                    and _table(frame) == _table(settled))

    def says(frame: dict) -> str:
        return (f"final={frame.get('final')} visible={frame.get('visible')} "
                f"tray={frame.get('tray_alpha_pct')}% laurels={frame.get('laurels')} "
                f"cast={frame.get('vignette')}")

    at_once = by_id.get("ulm_full__skip_at_once")
    if at_once and not whole(_frame(at_once, "after")):
        wrong.append(f"a click in the first instant: not the settled frame ({says(_frame(at_once, 'after'))})")
    again = by_id.get("ulm_full__closed_then_settled")
    if again and not whole(_frame(again, "seen_again")):
        wrong.append("closed in the first instant, then opened settled: not the settled frame "
                     f"({says(_frame(again, 'seen_again'))})")
    old = by_id.get("ulm_full__closed_then_old")
    if old:
        before, playing, end = (_frame(old, tag) for tag in ("before", "playing", "end"))
        if before.get("final") or before.get("laurels"):
            wrong.append(f"closed mid-act: the close did not catch the acts playing ({says(before)})")
        for name, frame in (("playing", playing), ("end", end)):
            if frame.get("laurels") != settled.get("laurels") or frame.get("tray_alpha_pct") != 100 \
                    or not frame.get("visible"):
                wrong.append("closed mid-act, then a battle from before the acts "
                             f"({name}): {says(frame)}")
        if not end.get("final") or end.get("dice_shown"):
            wrong.append(f"closed mid-act, then a battle from before the acts: {says(end)}, "
                         f"dice={end.get('dice_shown')}")
    return wrong


def chrome_overlaps(frame: dict, slack: int = 2) -> list[str]:
    """The plate's furniture — the wax seal, the two laurels of a triumph, Replay and
    Close — standing on one another (the nameplate itself is not counted: the seal
    hangs off its edge by design). BA1-X8 reads the settled frame of a triumph."""
    pieces = {k: v for k, v in (frame.get("chrome") or {}).items() if k != "plate"}
    names = sorted(pieces)
    out = []
    for i, a in enumerate(names):
        ax, ay, aw, ah = pieces[a]
        for b in names[i + 1:]:
            bx, by, bw, bh = pieces[b]
            w = min(ax + aw, bx + bw) - max(ax, bx)
            h = min(ay + ah, by + bh) - max(ay, by)
            if w > slack and h > slack:
                out.append(f"{a} {pieces[a]} over {b} {pieces[b]} ({w}x{h})")
    return out


def pips_lost(committed: int, remaining: int) -> int:
    """`DioramaPlinth.pips_lost`, mirrored: of six pips, the corps' losses as a
    share of what it brought, rounded; any loss costs one, and only a corps
    with nothing left has lost all six."""
    if committed <= 0:
        return 0
    lost = min(max(committed - remaining, 0), committed)
    if lost <= 0:
        return 0
    if remaining <= 0:
        return 6
    # GDScript's round() is half away from zero; Python's is half to even
    return min(max(int(lost / committed * 6 + 0.5), 1), 5)


def _pip_claims(rid: str, frame: dict, payload: dict) -> list[str]:
    wrong = []
    by_name = {c.get("name"): c for side in ("attacker", "defender")
               for c in (payload.get(side) or {}).get("contingents") or []}
    for c in frame.get("corps") or []:
        data = by_name.get(c["name"]) or {}
        want = pips_lost(int(data.get("committed", 0) or 0), int(data.get("remaining", 0) or 0))
        if c["pips_lost"] != want:
            wrong.append(f"{rid}: {c['name']} shows {c['pips_lost']} pips lost, the rule gives "
                         f"{want} ({data.get('committed')} -> {data.get('remaining')})")
    return wrong


def overlaps(frame: dict) -> list[str]:
    """Words on words: two lines of text on the baize, or a line and a
    portrait, that share a row and run into each other. `marks` are the
    words' own extents, not their labels' boxes; a line's extent is its LINE
    box (ascent, descent and leading), and the tableau stacks a name over its
    figures at a pitch tighter than that box — two stacked lines' boxes
    overlap by a third and their glyphs do not — so a pair counts when it
    overlaps by more than HALF the lower of the two heights (BA1-X1's pair,
    two strength lines on one row, overlapped by the whole height)."""
    marks = frame.get("marks") or []
    out = []
    for i, a in enumerate(marks):
        ax, ay, aw, ah = a["rect"]
        for b in marks[i + 1:]:
            if a["kind"] == "portrait" and b["kind"] == "portrait":
                continue
            bx, by, bw, bh = b["rect"]
            w = min(ax + aw, bx + bw) - max(ax, bx)
            h = min(ay + ah, by + bh) - max(ay, by)
            if w > 2 and h > 0.5 * min(ah, bh):
                out.append(f"{a['text']!r} {a['rect']} over {b['text']!r} {b['rect']} ({w}x{h})")
    return out


def off_the_baize(frame: dict, width: int = 948, height: int = 440) -> list[str]:
    """A line of text or a portrait that leaves the stage."""
    out = []
    for m in frame.get("marks") or []:
        x, y, w, h = m["rect"]
        if x < -1 or y < -1 or x + w > width + 1 or y + h > height + 1:
            out.append(f"{m['text']!r} {m['rect']}")
    return out


def check(results: dict, shots: list[dict]) -> list[str]:
    by_id = {r["id"]: r for r in results.get("results") or []}
    spec = {s["id"]: s for s in shots}
    payloads: dict[str, dict] = {}
    for shot in shots:
        if shot["payload"] not in payloads:
            payloads[shot["payload"]] = json.loads(Path(shot["payload"]).read_text(encoding="utf-8"))
    problems = []
    for shot in shots:
        res = by_id.get(shot["id"])
        if not res or not res.get("ok"):
            problems.append(f"{shot['id']}: did not complete "
                            f"({(res or {}).get('error', 'no result')})")
            continue
        for row in res.get("frames") or []:
            if not row.get("saved"):
                problems.append(f"{shot['id']}/{row.get('tag')}: the frame was not saved")

    for rid, shot in spec.items():
        res = by_id.get(rid)
        if "__" in rid or not res:
            continue
        payload = payloads[shot["payload"]]
        script = payload.get("script") or {}
        # The full form names every act the battle has; the brief form tells
        # the head beats, so it names the acts that have one.
        brief = script.get("form") == "brief" or shot.get("mode") == "brief"
        script_acts = [b["act"] for b in script.get("acts") or []
                       if not brief or any(x.get("weight") == "head" for x in b.get("beats") or [])]
        end = _frame(res, "end")
        settled = _frame(by_id.get(f"{rid}__settled"), "settled")
        if not end or not settled:
            problems.append(f"{rid}: no end/settled frame to compare")
            continue
        if not end.get("final"):
            problems.append(f"{rid}: the acts had not ended at the last frame")
        problems += [f"{rid} end: {w}" for w in _at_rest(end)]
        problems += [f"{rid} settled: {w}" for w in _at_rest(settled)]
        if _table(end) != _table(settled):
            problems.append(f"{rid}: the acts end on another table than the settled frame")
        if end.get("dice_shown") != settled.get("dice_shown") or not end.get("dice_shown"):
            problems.append(f"{rid}: the dice are not on both the end and the settled frame")
        if end.get("act"):
            problems.append(f"{rid}: an act is still named after the gavel ({end['act']!r})")
        if not end.get("banner") or end.get("banner") != settled.get("banner"):
            problems.append(f"{rid}: the banner differs ({end.get('banner')!r} / "
                            f"{settled.get('banner')!r})")
        if end.get("told") != settled.get("told"):
            problems.append(f"{rid}: Berthier's verdict differs between the end and the settled frame")
        problems += _toll_claims(rid, end, payload) + _toll_claims(f"{rid} settled", settled, payload)
        problems += _settled_strength_claims(rid, end, payload)
        problems += _settled_strength_claims(f"{rid} settled", settled, payload)
        problems += _opening_strength_claims(rid, _frame(res, "opening"), payload)
        problems += _the_end_claims(rid, end, settled, payload)
        crisis = _frame(res, "crisis")
        if crisis and not crisis.get("read_at_first_sight") \
                and not any(" → " in label for label in crisis.get("labels") or []):
            problems.append(f"{rid}: no strength line is running at the crisis")
        problems += _pip_claims(rid, end, payload)
        # at rest, no line of text stands on another or on a portrait, and
        # none leaves the baize (in motion they may cross: a lead surges)
        for name, frame in (("end", end), ("settled", settled)):
            problems += [f"{rid} {name}: ink over ink — {w}" for w in overlaps(frame)]
            problems += [f"{rid} {name}: off the baize — {w}" for w in off_the_baize(frame)]
            if not frame.get("marks"):
                problems.append(f"{rid} {name}: no marks recorded")
        # every act the script carries is told on the table, and only those
        opening = _frame(res, "opening")
        played = opening.get("played") or []
        told_acts = sorted({p["act"] for p in played if p["captioned"]}, key=ACTS.index)
        if told_acts != script_acts:
            problems.append(f"{rid}: the table tells {told_acts}, the script carries {script_acts}")
        for act in script_acts:
            frame = _frame(res, act)
            if not frame:
                problems.append(f"{rid}: act {act!r} was never shot")
            elif not frame.get("act") or frame.get("final"):
                problems.append(f"{rid}/{act}: no act named on the table ({frame.get('act')!r})")
        if sorted(res.get("missed") or []) != sorted(a for a in ACTS if a not in script_acts):
            problems.append(f"{rid}: missed {res.get('missed')} (acts not in the script: "
                            f"{[a for a in ACTS if a not in script_acts]})")
        # a corps that marches in starts off its place and unseen
        arrives = any(p["kind"] == "arrive" for p in played)
        off = [c["name"] for c in opening.get("corps") or []
               if c["alpha_pct"] < 100 or c["x"] != c["home_x"]]
        if arrives and not off:
            problems.append(f"{rid}: a corps arrives in the script but none stood off its "
                            f"place at the opening")

    if "enemy_comes" in spec:
        # read at the opening (he stands off the field, dark and unnamed) and
        # at the end (made out); the two frames between are the walk's pictures
        opening, end = (_frame(by_id.get("enemy_comes"), t) for t in ("opening", "end"))
        dark = [c["name"] for c in opening.get("corps") or [] if c.get("dark")]
        if len(dark) != 1 or any(c.get("dark") for c in end.get("corps") or []):
            problems.append(f"enemy comes: dark at the opening {dark}, still dark at the end "
                            f"{[c['name'] for c in end.get('corps') or [] if c.get('dark')]}")

    for rid, where in (("ulm_full__skip", "on the tableau"), ("ulm_full__skip_margin", "on the margin")):
        skip = by_id.get(rid)
        if not skip:
            continue
        before, after = _frame(skip, "before"), _frame(skip, "after")
        settled = _frame(by_id.get("ulm_full__settled"), "settled")
        if before.get("final") or not after.get("final"):
            problems.append(f"a click {where}: `_final` did not go false -> true across it")
        if _table(after) != _table(settled):
            problems.append(f"a click {where}: the frame after it is not the settled frame")
        if not after.get("close_shown") or not after.get("replay_shown"):
            problems.append(f"a click {where}: Close and Replay are not shown after it")
        problems += [f"a click {where}, after: {w}" for w in _at_rest(after)]
        again = _frame(skip, "after_a_second_click")
        if again and (not again.get("final") or not again.get("visible")
                      or _table(again) != _table(settled)):
            problems.append("a click on the settled tableau changed it")
    problems += _chrome_claims(by_id)
    brief, full = by_id.get("ulm_full__brief_always"), by_id.get("ulm_full")
    if brief and full:
        nb = len(_frame(brief, "opening").get("played") or [])
        nf = len(_frame(full, "opening").get("played") or [])
        if not (0 < nb < nf):
            problems.append(f"brief always: {nb} developments against the full form's {nf}")
        problems += [f"brief always end: {w}" for w in _at_rest(_frame(brief, "end"))]
        if _table(_frame(brief, "end")) != _table(_frame(full, "end")):
            problems.append("brief always: its end is not the full form's end")
    final_only = by_id.get("ulm_full__final_only")
    if final_only:
        opened, replaying, end = (_frame(final_only, t) for t in ("opened", "replaying", "end"))
        if not opened.get("final") or not opened.get("replay_shown"):
            problems.append("final frame only: the battle did not open settled with Replay shown")
        if replaying.get("final") or not replaying.get("act"):
            problems.append("final frame only: Replay did not play the acts")
        problems += [f"final frame only, replay end: {w}" for w in _at_rest(end)]
        if not end.get("final"):
            problems.append("final frame only: the replayed acts had not ended")
    reduced = by_id.get("ulm_full__reduce_motion")
    if reduced and not _frame(reduced, "opened").get("final"):
        problems.append("reduce motion: the battle did not open settled")
    old = by_id.get("ulm_full__old_payload")
    if old:
        playing, end = _frame(old, "playing"), _frame(old, "end")
        if playing.get("plays") or playing.get("played"):
            problems.append("old payload: a battle without a script played the acts")
        if not end.get("final") or end.get("dice_shown"):
            problems.append("old payload: it did not settle, or it shows dice it never had")
        if any(c["pips_lost"] < 0 for c in end.get("corps") or []):
            problems.append("old payload: a corps has no plinth")
    return problems


# ── the record ──────────────────────────────────────────────────────────────

def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:16]


def _slim(results: dict) -> list:
    """The record without the run's own file names."""
    out = []
    for res in results.get("results") or []:
        frames = [{k: v for k, v in row.items() if k != "png"} for row in res.get("frames") or []]
        out.append({**{k: v for k, v in res.items() if k != "frames"}, "frames": frames})
    return out


def keep_frames(work: Path) -> list[str]:
    from PIL import Image
    kept = []
    for old in OUT.glob("BA1_*.jpg"):
        old.unlink()
    for shot, tag, stem in CURATED:
        src = work / f"{shot}_{tag}.png"
        if not src.exists():
            continue
        dst = OUT / f"BA1_{stem}.jpg"
        Image.open(src).convert("RGB").save(dst, "JPEG", quality=88, optimize=True)
        kept.append(dst.name)
    return kept


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--only", default="")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--tag", default="", help="a tagged run keeps its record apart")
    ap.add_argument("--headless", action="store_true", help="the record only, no frames")
    ap.add_argument("--time-scale", type=float, default=1.0)
    ap.add_argument("--text-size", type=float, default=None,
                    help="Settings -> Text size for every shot (unsaid: the game's own default)")
    ap.add_argument("--godot", default=os.environ.get("IQ10_GODOT", GODOT_DEFAULT))
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # a claim may quote "Ney ◆"
    only = [s.strip() for s in args.only.split(",") if s.strip()]
    shots = build_shots(PAYLOADS, only, args.scale)
    if args.text_size is not None:
        for shot in shots:
            shot["text_size"] = args.text_size
    whole = not only and not args.tag and not args.headless and args.scale == 1.0 \
        and args.time_scale == 1.0 and args.text_size is None
    work = RUN / (args.tag or ("whole" if whole else "part"))
    print(f"{len(shots)} shot(s) at scale {args.scale:g} -> {work}")
    results, errors = run(shots, args.godot, work, headless=args.headless,
                          time_scale=args.time_scale)
    problems = check(results, shots)
    if only:
        problems = [p for p in problems if "no end/settled" not in p]
    record = {
        "date": datetime.date.today().isoformat(), "scale": args.scale,
        "text_size": args.text_size,
        "time_scale": args.time_scale, "headless": bool(args.headless),
        "shots": len(shots), "script_errors": errors, "problems": problems,
        "sources": {name: _sha(ROOT / name) for name in SOURCES},
        "payloads": {p.name: _sha(p) for p in sorted(PAYLOADS.glob("*.json"))},
        "results": _slim(results),
    }
    if whole:
        record["frames_kept"] = keep_frames(work)
        target = OUT / "walk_record.json"
    else:
        target = work / "walk_record.json"
    target.write_text(json.dumps(record, indent=1, ensure_ascii=False), encoding="utf-8")
    for line in errors[:20]:
        print("SCRIPT ERROR:", line)
    for line in problems:
        print("CLAIM:", line)
    done = sum(1 for r in results.get("results") or [] if r.get("ok"))
    print(f"{done}/{len(shots)} shots complete, {len(errors)} script error(s), "
          f"{len(problems)} claim(s) failed; record: {target}")
    return 1 if (errors or problems or done != len(shots)) else 0


if __name__ == "__main__":
    raise SystemExit(main())
