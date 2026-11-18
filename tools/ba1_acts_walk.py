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
import re
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
    # Row BA, BA-2: the board, the walls, the guns
    "the_reserve": [{"beat": "advance", "after": 0.45, "shot": "the_line_goes_in"}],
    "two_a_side": [{"beat": "advance", "after": 0.45, "shot": "the_line_goes_in"}],
    "our_dispositions": [{"beat": "plan", "after": 0.6, "shot": "plan"}],
    "square_and_horse": [{"beat": "advance", "after": 0.3, "shot": "the_horse"}],
    "assault_held": [{"beat": "storm", "after": 0.7, "until": "column", "limit": 1.2, "shot": "storm"},
                     {"beat": "wall_holds", "after": 0.9, "shot": "the_wall"}],
    "assault_stormed": [{"beat": "storm", "after": 0.7, "until": "column", "limit": 1.2, "shot": "storm"},
                        {"beat": "wall_falls", "after": 0.9, "shot": "the_wall"}],
    "assault_occupied": [{"beat": "wall_falls", "after": 0.9, "shot": "the_wall"}],
    "assault_capitulated": [{"beat": "capitulates", "after": 0.9, "shot": "the_wall"}],
    "assault_on_ours": [{"beat": "storm", "after": 0.7, "until": "column", "limit": 1.2, "shot": "storm"}],
    # (the second reading: this frame was read mid-count) a cannonade counts its toll as
    # the battery fires, over 1.6 s: the shot is taken when the count has ended
    "bombard_link": [{"beat": "battery", "after": 1.9, "shot": "battery"}],
    "bombard_levels": [{"beat": "works", "after": 0.9, "shot": "works"}],
    "bombard_ours": [{"beat": "bystander", "after": 0.6, "shot": "bystander"}],
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
    ("the_reserve", "end", "19_three_seats_and_the_reserve"),
    # Row BA, BA-2: the board, the walls, the guns
    ("the_reserve", "the_line_goes_in", "20_the_order_of_battle_goes_in"),
    ("two_a_side", "end", "21_two_corps_a_side"),
    ("our_dispositions", "plan", "22_our_dispositions_named"),
    ("square_and_horse", "the_horse", "23_the_horse_and_the_square"),
    ("assault_held", "opening", "24_before_the_walls"),
    ("assault_held", "storm", "25_the_storm"),
    ("assault_held", "end", "26_the_walls_hold"),
    ("assault_stormed", "end", "27_the_walls_are_carried"),
    ("assault_capitulated", "end", "28_the_garrison_capitulates"),
    ("assault_on_ours", "end", "29_our_own_walls"),
    ("bombard_link", "battery", "30_the_cannonade_alone"),
    ("bombard_levels", "end", "31_the_works_are_levelled"),
    ("bombard_ours", "bystander", "32_our_own_corps_under_our_guns"),
    ("old_four_seat", "end", "33_an_old_four_seat_battle_keeps_its_file"),
    # Row BA, BA-3: the day's panel at rest (the end of each showing)
    ("day_opens", "end", "34_the_day_opens"),
    ("day_dim_chip", "end", "35_a_chip_is_dim"),
    ("day_word", "end", "36_a_word_and_his_answer"),
    ("day_night", "end", "37_night_falls"),
    ("day_defence", "end", "38_a_defended_day"),
    ("day_follows", "end", "39_a_table_that_follows"),
    ("day_ulm", "end", "40_ulms_thirteen_chips"),
    ("day_guns", "end", "41_the_guns_among_the_groups"),
]

SOURCES = [
    "godot-client/project-sovereign/scripts/battle_acts.gd",
    "godot-client/project-sovereign/scripts/diorama_plinth.gd",
    "godot-client/project-sovereign/scripts/battle_diorama.gd",
    "backend/game_logic/battle_script.py",
    "backend/game_logic/siege_diorama.py",
    "tools/ba1_acts_walk.gd",
    # BA2-X17 (closed with BA-3's walk of record): every source that shapes
    # what the walk shows — the payload's builder, the stage, this walk and
    # the client's shared helpers.
    "backend/game_logic/battle_diorama.py",
    "backend/game_logic/battle_day.py",
    "backend/game_logic/battle_telling.py",
    "tools/ba1_stage_battles.py",
    "tools/ba1_acts_walk.py",
    "godot-client/project-sovereign/scripts/utils.gd",
]

# BA-2: a payload from BEFORE the three-seat cap (BA-1's own four-a-side
# battle, kept as it was staged): four corps a side must still play, as the
# host's file.
OLD_FOUR_SEAT = OUT / "old_four_seat_payload.json"
# (the session's review) the longest line a province gives under the headline — a liberation's
LONG_LINE = ("Naples, the Kingdom of the Two Sicilies' capital, retaken — handed back to "
             "the Kingdom of the Two Sicilies.")
STAGE_MID_X = 474           # the stage's centre line (948 px wide)


def scene_events(name: str) -> list[dict]:
    # K1: a day's table is read at the very gavel too (the panel must not stand there)
    gavel = ([{"end": True, "after": 0.0, "until": "gavel", "limit": 6.0, "shot": "gavel"}]
             if name.startswith("day_") else [])
    return ([{"t": 0.4, "shot": "opening"}]
            + [{"act": act, "after": 0.9, "shot": act} for act in ACTS]
            + list(SCENE_BEATS.get(name, []))
            + gavel
            + [{"end": True, "after": 2.8, "shot": "end"}])


def chip_word(chip: dict, day: dict) -> str:
    """What the client emits on `word_given` for this chip (battle_acts.gd
    `_on_day_chip`): a word chip's `@word:<word>:<enemy>`, else its order."""
    if chip.get("word"):
        return f"@word:{chip['word']}:{day.get('enemy', '')}"
    return str(chip.get("command") or "")


EXIT_KINDS = ("stand", "break_off")
OWN_KINDS = ("press", "guard", "dig_in")
# battle_acts.gd DAY_GROUP_LABEL / DAY_RULE / DAY_CLASH_SCOPE (the second reading)
GROUP_LABEL = {"lead": "Another leads the attack", "bring_up": "Bring up", "cannonade": "The guns, no clash"}
DAY_LIFT = 8                # battle_acts.gd DAY_LIFT: what the panel may take of the gap under the bars
DAY_RULE = ("A word costs points, and he answers it. A line that breaks decides the day; "
            "two silences running, or no point left, and night falls: nothing decided.")
DAY_CLASH_SCOPE = " LOST THIS CLASH"


def chip_box(chip: dict) -> str:
    """Which of the panel's three boxes draws this chip (battle_acts.gd
    `_day_split`): the exits (row E: every "stands", "Break off" / "Fall back",
    "Leave it to <lead>"), the lead's own words (row C: press, the Guard, dig
    in), or a compact group (rows D)."""
    if chip.get("word") or chip.get("kind") in EXIT_KINDS:
        return "exits"
    if chip.get("kind") in OWN_KINDS:
        return "own"
    return "groups"


def day_split(chips: list) -> tuple[list, list, list]:
    """[own indices, groups as (kind, [indices]) by first appearance, exit
    indices] — all IN THE ARRAY'S ORDER (nothing is re-sorted)."""
    own = [i for i, c in enumerate(chips) if chip_box(c) == "own"]
    groups: list = []
    for i, c in enumerate(chips):
        if chip_box(c) != "groups":
            continue
        found = next((g for g in groups if g[0] == c.get("kind")), None)
        if found is None:
            found = (c.get("kind"), [])
            groups.append(found)
        found[1].append(i)
    exits = [i for i, c in enumerate(chips) if chip_box(c) == "exits"]
    return own, groups, exits


def _variant(name: str, payload: dict, label: str) -> str:
    """A payload edited for one claim, written beside the run's own files."""
    folder = RUN / "variants"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}__{label}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return str(path)


def day_shots(name: str, payload_path: str, scale: float) -> list[dict]:
    """BA-3: the presses and the key, on the settled table of a day that awaits
    our word (a lit order chip, a lit word chip, a name chip of a compact group,
    a dim chip, Esc), the chrome's return, the clash's own headline (the day
    taken out of the payload: the banner and the shelf are read against it),
    and — on `day_opens` — the day edited to await HIM (one `@refresh`) and the
    day with no script acts to play (the panel stands at rest)."""
    payload = json.loads(Path(payload_path).read_text(encoding="utf-8"))
    day = payload.get("day") if isinstance(payload.get("day"), dict) else {}
    if not day:
        return []
    chips = day.get("chips") or []
    common = {"scene": name, "payload": payload_path, "mode": "acts", "cinematic": False,
              "scale": scale}
    stripped = {k: v for k, v in payload.items() if k != "day"}
    shots = [{**common, "id": f"{name}__no_day", "payload": _variant(name, stripped, "no_day"),
              "events": [{"t": 0.6, "frames": 4, "shot": "settled"}]}]
    if day.get("follows") and day.get("open") and name == "day_follows":
        # K4: a table that follows goes on by itself 2.5 s after it rests (none under Reduce motion)
        shots.append({**common, "id": f"{name}__goes_on", "events": [
            {"t": 0.6, "frames": 4, "shot": "rest"}, {"t": 4.4, "shot": "later"}]})
        shots.append({**common, "id": f"{name}__stays_reduced", "reduce_motion": True, "events": [
            {"t": 0.6, "frames": 4, "shot": "rest"}, {"t": 4.4, "shot": "later"}]})
        # a Replay cancels the wait: no dismissal during the replay; it restarts at the new rest
        shots.append({**common, "id": f"{name}__replays", "events": [
            {"t": 0.6, "frames": 4, "shot": "rest"}, {"t": 0.7, "do": "replay"},
            {"t": 2.6, "shot": "during"}, {"end": True, "after": 4.5, "shot": "later"}]})
        ordinary_f = Path(payload_path).parent / "ordinary_brief.json"
        if ordinary_f.exists():
            shots.append({**common, "id": f"{name}__then_ordinary", "events": [
                {"t": 0.6, "frames": 4, "shot": "before"},
                {"t": 0.7, "do": "reopen", "cinematic": False, "payload": str(ordinary_f)},
                {"t": 0.6, "frames": 4, "shot": "after"}]})
        # (g) a table that follows asks nothing even when its day awaits him
        him = json.loads(json.dumps(payload))
        him["day"]["awaits"] = "theirs"
        shots.append({**common, "id": f"{name}__follows_awaits_him",
                      "payload": _variant(name, him, "follows_awaits_him"),
                      "events": [{"t": 0.6, "frames": 4, "shot": "settled"}]})
        return shots
    if not (day.get("open") and day.get("awaits") == "ours" and chips and not day.get("pending")
            and not day.get("follows")):
        return shots
    before = {"t": 0.6, "frames": 4, "shot": "before"}

    def pick(want):
        return next((i for i, c in enumerate(chips) if want(c)), None)

    lit_order = pick(lambda c: c.get("ok") and c.get("command") and chip_box(c) == "own")
    lit_group = pick(lambda c: c.get("ok") and c.get("command") and chip_box(c) == "groups")
    lit_word = pick(lambda c: c.get("ok") and c.get("word"))
    dim = pick(lambda c: not c.get("ok"))
    for kind, index in (("press_lit", lit_order), ("press_group", lit_group),
                        ("press_word", lit_word), ("press_dim", dim)):
        if index is None:
            continue
        events = [before, {"t": 0.7, "do": "press_chip", "index": index, "box": chip_box(chips[index]),
                           "shot": "pressed"}]
        if kind == "press_lit":
            events.append({"t": 0.8, "do": "press_chip", "index": index, "box": chip_box(chips[index]),
                           "shot": "pressed_again"})
        shots.append({**common, "id": f"{name}__{kind}", "events": events})
    shots.append({**common, "id": f"{name}__esc", "events": [
        before, {"t": 0.7, "do": "esc", "shot": "after"}]})
    # BA-6 (fewer chips): "+N more" is a toggle — every word of the groups in place, and back
    if any(i not in day_digits(chips) for _k, idx in day_split(chips)[1] for i in idx):
        shots.append({**common, "id": f"{name}__more", "events": [
            before, {"t": 0.7, "do": "press_chip", "meta": "daymore", "box": "groups", "shot": "open"},
            {"t": 0.8, "do": "press_chip", "meta": "daymore", "box": "groups", "shot": "closed"}]})
    # BA-4: the bare digits press the day's chips in fixed slots — a real key
    # each: the lead's own word, a corps of a group, a free word, a slot no
    # chip holds, a locked chip's slot, and a key while the acts still play
    for kind, d in day_digit_shots(chips).items():
        if kind == "digit_playing":
            shots.append({**common, "id": f"{name}__{kind}", "cinematic": True,
                          "events": [{"t": 0.5, "do": "digit", "n": d, "shot": "pressed"}]})
        elif kind in ("digit_empty", "digit_locked"):
            shots.append({**common, "id": f"{name}__{kind}", "events": [
                before, {"t": 0.7, "do": "digit", "n": d, "shot": "pressed"}]})
        else:
            shots.append({**common, "id": f"{name}__{kind}", "events": [
                before, {"t": 0.7, "do": "digit", "n": d, "shot": "pressed"},
                {"t": 0.8, "do": "digit", "n": d, "shot": "pressed_again"}]})
    # the chrome the panel borrowed comes back for the next battle on the same
    # tableau: an ordinary battle (no day) is shown after the day's table
    ordinary = Path(payload_path).parent / "ordinary_brief.json"
    if ordinary.exists():
        shots.append({**common, "id": f"{name}__then_ordinary", "events": [
            before, {"t": 0.7, "do": "reopen", "cinematic": False, "payload": str(ordinary)},
            {"t": 0.6, "frames": 4, "shot": "after"}]})
    if name == "day_opens":
        # BA6-6: the table's marks have their caption line where the table has the room — a day that
        # carries no first-day line has it (that line takes the room once a campaign)
        plain = json.loads(json.dumps(payload))
        plain["day"].pop("first_open", None)
        shots.append({**common, "id": f"{name}__legend", "payload": _variant(name, plain, "legend"),
                      "events": [{"t": 0.6, "frames": 4, "shot": "settled"}]})
        # BA6-3: stakes short enough to stand beside the buttons: the exits' cards keep the tray's floor
        short = json.loads(json.dumps(payload))
        for chip in short["day"].get("chips") or []:
            if chip_box(chip) == "exits":
                chip["does"] = {"stand": "he speaks next", "break_off": "the day ends"}.get(
                    str(chip.get("kind")), "he may press")
        shots.append({**common, "id": f"{name}__beside", "payload": _variant(name, short, "beside"),
                      "events": [{"t": 0.6, "frames": 4, "shot": "settled"}]})
        bare = json.loads(json.dumps(payload))
        bare["day"]["chips"] = []                  # K7: an open day that awaits OUR word, and no chips
        shots.append({**common, "id": f"{name}__no_chips", "payload": _variant(name, bare, "no_chips"),
                      "events": [{"t": 0.6, "frames": 4, "shot": "settled"}]})
        him = json.loads(json.dumps(payload))
        him["day"].update(awaits="theirs", chips=[])
        him_path = _variant(name, him, "awaits_him")
        shots.append({**common, "id": f"{name}__awaits_him", "payload": him_path,
                      "events": [{"t": 0.6, "frames": 4, "shot": "settled"}]})
        shots.append({**common, "id": f"{name}__awaits_him_acts", "payload": him_path,
                      "cinematic": True, "events": [{"t": 0.4, "shot": "opening"},
                                                    {"end": True, "after": 2.8, "shot": "end"}]})
        # … and a click that skips the acts settles the table at once: still one word
        shots.append({**common, "id": f"{name}__awaits_him_skip", "payload": him_path, "cinematic": True,
                      "events": [{"t": 0.4, "shot": "opening"}, {"t": 2.7, "do": "click", "shot": "skipped"},
                                 {"t": 3.6, "shot": "later"}]})
        shots.append({**common, "id": f"{name}__no_script", "strip_script": True, "cinematic": True,
                      "events": [{"t": 1.2, "shot": "playing"}, {"t": 6.5, "shot": "end"}]})
    return shots


def _long_line_payload(payload_dir: Path) -> str:
    """(The session's review) Ulm's tableau as a liberation would carry it — the
    province's own line the longest the game writes (`LONG_LINE`), then what
    told. Derived beside the run from the payload of record, never kept."""
    src = json.loads((payload_dir / "ulm_full.json").read_text(encoding="utf-8"))
    src.update(region_conquered=True, liberated_to="TwoSicilies", liberation_line=LONG_LINE)
    out = RUN / "_derived" / "ulm_full__long_line.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(src, ensure_ascii=False, indent=1), encoding="utf-8")
    return str(out)


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
        shots += day_shots(name, payload, scale)
    if OLD_FOUR_SEAT.exists() and (not only or any(o in "old_four_seat" for o in only)):
        old = str(OLD_FOUR_SEAT)
        shots.append({"id": "old_four_seat", "scene": "old_four_seat", "payload": old,
                      "mode": "acts", "cinematic": True, "scale": scale,
                      "events": scene_events("old_four_seat")})
        shots.append({"id": "old_four_seat__settled", "scene": "old_four_seat", "payload": old,
                      "mode": "acts", "cinematic": False, "scale": scale,
                      "events": [{"t": 0.6, "frames": 4, "shot": "settled"}]})
    if "ulm_full" in manifest and (not only or any(o in "ulm_full" for o in only)):
        ulm = str(payload_dir / "ulm_full.json")
        common = {"scene": "ulm_full", "payload": ulm, "scale": scale}
        # (the session's review) Ulm as a liberation carries it: the line under the headline
        # must fit the baize — whole, short, or with what told on its hover — at every size
        long_line = _long_line_payload(payload_dir)
        for tag, size in (("", None), ("_130", 1.3)):
            shot = {"id": f"ulm_full__long_line{tag}", "scene": "ulm_full", "payload": long_line,
                    "mode": "acts", "cinematic": False, "scale": scale,
                    "events": [{"t": 0.6, "frames": 4, "shot": "settled"}]}
            if size is not None:
                shot["text_size"] = size
            shots.append(shot)
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
            # BA-5 — the acts' speed. Settings -> Battle speed -> twice as fast: the engine's
            # clock is the acts' while they play and is given back at the gavel
            {**common, "id": "ulm_full__speed_x2", "mode": "acts", "cinematic": True, "speed": "x2",
             "events": [{"t": 2.6, "shot": "playing"}, {"end": True, "after": 2.8, "shot": "end"}]},
            # … the table's own switch, pressed mid-act with a REAL click: the acts go on,
            # the clock doubles at once and the setting is kept; a second press gives it back
            {**common, "id": "ulm_full__speed_switch", "mode": "acts", "cinematic": True,
             "events": [{"t": 2.6, "shot": "before"}, {"t": 2.7, "do": "click_speed"},
                        {"t": 3.3, "shot": "faster"}, {"t": 3.4, "do": "click_speed"},
                        {"t": 4.0, "shot": "back"}, {"end": True, "after": 2.8, "shot": "end"}]},
            # … closed mid-act at twice the speed (Esc): the clock is given back with the table
            {**common, "id": "ulm_full__speed_closed", "mode": "acts", "cinematic": True, "speed": "x2",
             "events": [{"t": 2.6, "shot": "playing"}, {"t": 2.7, "do": "close"},
                        {"t": 3.2, "shot": "closed"}]},
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
                lost = f"({int(c['advance_losses']):,} lost on the march)"
                told = [label for label in labels if label.startswith(want)]
                if not told:
                    wrong.append(f"{rid}: {c.get('name')}'s toll {want!r} is not on the table")
                elif not any(lost in label for label in told):
                    # (the review) at the baize's foot, where the second line has no room, the
                    # cost rides the toll's own line: "→ 21,687 after the advance (−307)" —
                    # the toll alone only where even that would leave the baize sideways
                    one = f"{want} (−{int(c['advance_losses']):,})"
                    rects = [m["rect"] for m in frame.get("marks") or []
                             if m.get("kind") == "text" and m.get("text") in (want, one)]
                    room_below = not rects or rects[0][1] + 2 * rects[0][3] <= 441
                    if room_below or not any(label == one for label in told):
                        wrong.append(f"{rid}: (BA5-m) {c.get('name')}'s toll does not say what the march cost "
                                     f"({lost!r}, or on one line {one!r}): {told!r}")
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
              if m["kind"] == "text" and (("in reserve" in m["text"] and "lost" in m["text"])
                                          or RESERVE_DEAD_LINE.fullmatch(m["text"]))]
    return wrong


# BA-2: on a wedge the reserve's dead is a line of its own ("1,127 lost").
RESERVE_DEAD_LINE = re.compile(r"[\d,]+ lost")


def _kind(payload: dict) -> str:
    return str(payload.get("kind") or "battle")


def _beats(payload: dict) -> list[dict]:
    return [b for block in (payload.get("script") or {}).get("acts") or []
            for b in block.get("beats") or []]


def _overlap(a, b, slack: int = 2) -> bool:
    if not a or not b:
        return False
    w = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    h = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    return w > slack and h > slack


def _wall_claims(rid: str, res: dict, end: dict, settled: dict, payload: dict) -> list[str]:
    """BA-2. A garrison assault opens on a WHOLE wall and ends on the one the
    assault left (held, stormed, capitulated) — as the settled frame has it;
    the garrison shows no portrait and no standard; no stormer stands in the
    wall. No other battle has a wall."""
    wrong = []
    opening = _frame(res, "opening")
    if _kind(payload) != "assault":
        wrong += [f"{rid} {name}: a wall ({frame.get('wall')!r}) on a table that is no assault"
                  for name, frame in (("opening", opening), ("end", end), ("settled", settled))
                  if frame.get("wall")]
        return wrong
    fate = payload.get("fate")
    if opening and opening.get("wall") != "whole":
        wrong.append(f"{rid}: at the opening the wall already reads {opening.get('wall')!r}")
    for name, frame in (("end", end), ("settled", settled)):
        if frame.get("wall") != fate:
            wrong.append(f"{rid} {name}: the wall reads {frame.get('wall')!r}, "
                         f"the assault's fate is {fate!r}")
        if frame.get("wall_ladders_pct") and fate == "held":
            wrong.append(f"{rid} {name}: ladders still stand against a wall that held")
        for c in frame.get("corps") or []:
            if not c.get("garrison") and _overlap(c.get("body"), frame.get("wall_rect")):
                wrong.append(f"{rid} {name}: {c['name']} stands in the wall")
    storm = _frame(res, "storm")
    if storm:
        # the storm itself: the ladders up against a wall still whole, and the
        # stormers closed up into columns (their files narrower than their line)
        line = {c["name"]: c.get("files_px", 0) for c in settled.get("corps") or []}
        if storm.get("wall") != "whole" or not storm.get("wall_ladders_pct"):
            wrong.append(f"{rid} storm: the wall reads {storm.get('wall')!r} with ladders at "
                         f"{storm.get('wall_ladders_pct')} %")
        for c in storm.get("corps") or []:
            if not c.get("garrison") and not c.get("files_px", 0) < line.get(c["name"], 0):
                wrong.append(f"{rid} storm: {c['name']} goes in standing in line "
                             f"({c.get('files_px')} px of {line.get(c['name'])}), not in column")
    for name, frame in (("opening", opening), ("end", end), ("settled", settled)):
        keepers = [c for c in frame.get("corps") or [] if c.get("garrison")]
        if frame and len(keepers) != 1:
            wrong.append(f"{rid} {name}: {len(keepers)} garrison blocks on an assault's table")
        for c in keepers:
            if c.get("portrait_shown") or c.get("standard_shown"):
                wrong.append(f"{rid} {name}: the garrison shows a portrait "
                             f"({c.get('portrait_shown')}) or a standard ({c.get('standard_shown')})")
    return wrong


def _works_claims(rid: str, res: dict, end: dict, settled: dict, payload: dict) -> list[str]:
    """BA-2. Field works stand at the strength the battle met them with when
    the acts open, and at what its report says they ended on when they end;
    a rampart nobody is told of is not drawn (a watcher is told of none)."""
    marks: dict = {}
    for beat in _beats(payload):
        who, kind = str(beat.get("actor", "")), beat.get("kind")
        if kind in ("ground", "plan") and int(beat.get("works_pct", 0) or 0) > 0:
            marks.setdefault(who, [int(beat["works_pct"]), int(beat["works_pct"])])
        elif kind == "works":
            marks[who] = [int(beat.get("old", 0) or 0), int(beat.get("new", 0) or 0)]
    wrong = []
    opening = _frame(res, "opening")
    for name, frame, index in (("opening", opening, 0), ("end", end, 1), ("settled", settled, 1)):
        if not frame:
            continue
        shown = frame.get("works") or {}
        on_table = {c["name"] for c in frame.get("corps") or []}
        want = {who: pair[index] for who, pair in marks.items() if who in on_table}
        if shown != want:
            wrong.append(f"{rid} {name}: the works stand at {shown}, the battle's report "
                         f"gives {want}")
    return wrong


WEDGE_TEXT_MAX = 1.15       # BA3-X2: the stations are laid for Text size 100 % and the shipped 115 %


def _board_claims(rid: str, frame: dict, text_size: float = 1.15) -> list[str]:
    """BA-2, the order of battle. Two or three corps on a side lay the wedge:
    the lead nearest the centre line, the near wing below and behind him, the
    far wing above and behind, the two sides mirrored; no line of a corps
    stands on another corps' slab or men. Anything else — a duel, an old
    payload that seats four — keeps the host's file."""
    corps = frame.get("corps") or []
    if not corps:
        return []
    sides = {True: [c for c in corps if c["left"]], False: [c for c in corps if not c["left"]]}
    most = max(len(sides[True]), len(sides[False]))
    want = "wedge" if 2 <= most <= 3 else "file"
    wrong = []
    if frame.get("laid") != want:
        # BA3-X2 (row BA, BA-4): past the text size the stations are laid for
        # the file is the RULED layout (`battle_acts.gd`'s header: measured at
        # 130 %, and two more station sets tried and refused) — the table keeps
        # it with ITS OWN measured reason on record (`laid_why`: which line
        # would stand on what, and by how much), and the walk reads that. Up
        # to that size a wedge that is not laid is a claim, and says the reason.
        why = frame.get("laid_why") or []
        if want == "wedge" and frame.get("laid") == "file" and text_size > WEDGE_TEXT_MAX + 0.001 and why:
            NOTES_SEEN.append(f"{rid}: the file is kept at text {text_size:g} — {why[0]}"
                              + (f" (and {len(why) - 1} more)" if len(why) > 1 else ""))
        else:
            wrong.append(f"{rid}: the table is laid as {frame.get('laid')!r}; "
                         f"{len(sides[True])} against {len(sides[False])} corps lay the {want}"
                         + (f" — the table's own measure: {why[0]}" if why else ""))
    if frame.get("laid") != "wedge":
        return wrong
    for side in sides.values():
        leads = [c for c in side if c.get("role") == "lead"]
        if len(leads) != 1 or not leads[0].get("lead"):
            wrong.append(f"{rid}: a side's centre is not its lead ({[c['name'] for c in leads]})")
            continue
        lead = leads[0]
        for c in side:
            if c is lead:
                continue
            if abs(c["home_x"] - STAGE_MID_X) < abs(lead["home_x"] - STAGE_MID_X) + 100:
                wrong.append(f"{rid}: {c['name']} stands as near the centre as the lead")
            if c.get("role") == "near" and not c["home_y"] > lead["home_y"] + 20:
                wrong.append(f"{rid}: the near wing {c['name']} is not below the lead")
            if c.get("role") == "far" and not c["home_y"] < lead["home_y"] - 100:
                wrong.append(f"{rid}: the far wing {c['name']} is not above the lead")
    for role in ("lead", "near", "far"):
        left = [c for c in sides[True] if c.get("role") == role]
        right = [c for c in sides[False] if c.get("role") == role]
        if left and right and (abs(left[0]["home_x"] + right[0]["home_x"] - 2 * STAGE_MID_X) > 1
                               or left[0]["home_y"] != right[0]["home_y"]):
            wrong.append(f"{rid}: the {role} stations are not mirrored "
                         f"({left[0]['home_x']},{left[0]['home_y']} / "
                         f"{right[0]['home_x']},{right[0]['home_y']})")
    for a in corps:
        for b in corps:
            if a is b:
                continue
            for word in a.get("words") or []:
                if _overlap(word, b.get("body")):
                    wrong.append(f"{rid}: a line of {a['name']}'s {word} stands on "
                                 f"{b['name']}'s men {b.get('body')}")
    return wrong


def _manoeuvre_claims(rid: str, opening: dict, end: dict, settled: dict) -> list[str]:
    """BA-2. A corps comes on in COLUMN and ends in LINE: when the acts open
    its files are closed up, and at the end every man stands where the
    settled frame has him. A garrison and a corps in square do not manoeuvre."""
    wrong = []
    line = {c["name"]: c for c in settled.get("corps") or []}
    for c in end.get("corps") or []:
        if c["name"] in line and c.get("files_px") != line[c["name"]].get("files_px"):
            wrong.append(f"{rid}: at the end {c['name']}'s files span {c.get('files_px')} px, "
                         f"the settled frame's {line[c['name']].get('files_px')}")
    for c in opening.get("corps") or []:
        there = line.get(c["name"]) or {}
        still = c.get("garrison") or c.get("in_square")
        if there.get("files_px", 0) > 20 and not still \
                and not c.get("files_px", 0) < there["files_px"]:
            wrong.append(f"{rid}: at the opening {c['name']} already stands in line "
                         f"({c.get('files_px')} px of {there['files_px']})")
        if still and c.get("files_px") != there.get("files_px"):
            wrong.append(f"{rid}: {c['name']} (a garrison, or in square) is not in its "
                         f"own formation at the opening")
    return wrong


def _standard_claims(rid: str, end: dict, settled: dict) -> list[str]:
    """BA2-X5. Every standard stands at the end of the acts where the settled
    frame has it — the victor's, advanced onto the player's half on a defeat,
    among them."""
    there = {c["name"]: c.get("standard_x") for c in settled.get("corps") or []}
    return [f"{rid}: {c['name']}'s standard stands at {c.get('standard_x')} when the acts end "
            f"and at {there[c['name']]} on the settled frame"
            for c in end.get("corps") or []
            if c["name"] in there and c.get("standard_x") != there[c["name"]]]


SQUARE_SPAN_PX = 74      # a square's stands close up (72 px); a line's span 84


def _square_claims(rid: str, res: dict, end: dict, settled: dict, payload: dict) -> list[str]:
    """BA-2. A corps the script tells in square STANDS in square, from the
    first frame to the last: marked, and its stands closed up on their slab
    (a disposition, not a result). No other corps is formed so."""
    told = set()
    for beat in _beats(payload):
        kind = beat.get("kind")
        if kind in ("ground", "plan") and beat.get("square"):
            told.add(str(beat.get("actor", "")))
        elif kind == "square":
            # the row is the horse's own: the square is the lead it rode at
            side = "defender" if beat.get("side") == "attacker" else "attacker"
            told |= {str(c.get("name", "")) for c in (payload.get(side) or {}).get("contingents") or []
                     if c.get("lead")}
    wrong = []
    for name, frame in (("opening", _frame(res, "opening")), ("end", end), ("settled", settled)):
        for c in frame.get("corps") or []:
            if c["name"] in told:
                if not c.get("in_square"):
                    wrong.append(f"{rid} {name}: {c['name']} is told in square and is not marked so")
                elif c.get("files_px", 0) > SQUARE_SPAN_PX:
                    wrong.append(f"{rid} {name}: {c['name']} is in square and stands in line "
                                 f"({c.get('files_px')} px)")
            elif c.get("in_square"):
                wrong.append(f"{rid} {name}: {c['name']} stands in square and no beat tells it")
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
    # BA-3: a table with a day lends the laurels' room to the day's panel
    # (battle_acts.gd `_show_the_day`), so a triumph's laurels stand only on a
    # table that has no day.
    day_block = payload.get("day") if isinstance(payload.get("day"), dict) else None
    # (a day decided by its clash builds no panel: its laurels stand)
    has_panel = bool(day_block) and (bool(day_block.get("open")) or bool(day_block.get("banner")))
    flank = register == "triumph" and not has_panel
    if (settled.get("laurels", 0) == 2) != flank:
        wrong.append(f"{rid}: {settled.get('laurels')} laurels on a {register!r}"
                     f"{' with a day' if isinstance(payload.get('day'), dict) else ''}")
    if (settled.get("vignette") != NEUTRAL_CAST) != (register == "defeat"):
        wrong.append(f"{rid}: the baize's cast is {settled.get('vignette')!r} on a {register!r}")

    def tails(frame):
        return sorted(m["text"] for m in frame.get("marks") or []
                      if m["kind"] == "text" and "in reserve" in m["text"])
    if tails(end) != tails(settled):
        wrong.append(f"{rid}: the reserve's line is {tails(end)} at the end and "
                     f"{tails(settled)} on the settled frame")
    # (on a wedge the reserve's dead is a line of its own beside the count)
    said = [m["text"] for m in settled.get("marks") or [] if m["kind"] == "text"]
    for side in ("attacker", "defender"):
        dead = int((payload.get(side) or {}).get("reserve_casualties", 0) or 0)
        if dead > 0 and int((payload.get(side) or {}).get("reserve_count", 0) or 0) > 0 \
                and not any(f"{dead:,} lost" in t for t in said):
            wrong.append(f"{rid}: the {side}'s reserve lost {dead:,} and the settled frame "
                         f"does not say so ({tails(settled)})")
    for side in ("attacker", "defender"):
        count = int((payload.get(side) or {}).get("reserve_count", 0) or 0)
        if count > 0 and not any(t.startswith(f"+{count} ") for t in tails(settled)):
            wrong.append(f"{rid}: the {side} keeps {count} corps in reserve and the settled "
                         f"frame does not say so ({tails(settled)})")
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


def _laurel_claims(where: str, frame: dict) -> list[str]:
    """BA1-X8 (closed in BA-5): on a triumph the two laurels flank the BANNER, on the
    baize — one on each side of its words, level with them, clear of every other word
    and portrait there, and of the dice."""
    laurels = frame.get("laurel_ink") or []
    if len(laurels) != 2:
        return []
    problems = []
    banner = frame.get("banner_ink") or []
    left, right = sorted(laurels, key=lambda r: r[0])
    if len(banner) != 4:
        problems.append(f"{where}: (BA1-X8) laurels on a table whose banner is not shown")
    else:
        if not (left[0] + left[2] <= banner[0] and right[0] >= banner[0] + banner[2]):
            problems.append(f"{where}: (BA1-X8) the laurels do not flank the banner's words "
                            f"({left} / {banner} / {right})")
        mid = banner[1] + banner[3] / 2.0
        for rect in (left, right):
            if abs(rect[1] + rect[3] / 2.0 - mid) > 6:
                problems.append(f"{where}: (BA1-X8) a laurel is not level with the banner ({rect} / {banner})")
    for rect in (left, right):
        if rect[0] < 0 or rect[1] < 0 or rect[0] + rect[2] > 948 or rect[1] + rect[3] > 440:
            problems.append(f"{where}: (BA1-X8) a laurel leaves the baize ({rect})")
        for mark in frame.get("marks") or []:
            if mark.get("rect") == banner:
                continue
            if _overlap(rect, mark["rect"], slack=0):
                problems.append(f"{where}: (BA1-X8) a laurel {rect} stands on {mark['text']!r} {mark['rect']}")
        dice = frame.get("dice_rect") or []
        if frame.get("dice_shown") and len(dice) == 4 and _overlap(rect, dice, slack=0):
            problems.append(f"{where}: (BA1-X8) a laurel {rect} stands on the dice {dice}")
    return problems


def _letters(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(text or "").lower())


def _verdict_claims(where: str, frame: dict, payload: dict, *, at_rest: bool) -> list[str]:
    """BA5-D3 — what stands in the verdict's room stands whole. At rest: Berthier's line
    and the enemy's answer fit the room, or the room holds whole paragraphs and an (i)
    whose hover carries EVERY word; only a single paragraph too tall for the room alone
    may scroll. While the acts play: a beat's line too tall for the room is set a step
    smaller before it may scroll."""
    if not frame.get("verdict_visible") or "verdict_h" not in frame:
        return []
    bb = str(frame.get("verdict_bb") or "")
    if not bb:
        return []
    problems = []
    over = int(frame["verdict_h"]) > int(frame["verdict_room"]) + 1
    kept = bb.split("[/hint]")[0] if "[hint=" in bb else bb
    if over and "\n" in kept:
        problems.append(f"{where}: (BA5-d3) the verdict stands behind a scrollbar with more than one "
                        f"paragraph in its room ({frame['verdict_h']} px in {frame['verdict_room']})")
    # a step smaller: the verdict label's own Caption step (the house rule: never a BBCode size; a
    # record from before it carried the size in the text)
    stepped = bb.startswith("[font_size=") or str(frame.get("verdict_step") or "") == "CaptionRich"
    if over and not stepped:
        problems.append(f"{where}: (BA5-d3) a line too tall for the verdict's room was not set a step "
                        f"smaller ({frame['verdict_h']} px in {frame['verdict_room']})")
    if at_rest:
        said = _letters(HINT_RX.search(bb).group(1)) if "[hint=" in bb else _letters(frame.get("told"))
        for key in ("observation", "enemy_voice"):
            words = _letters(payload.get(key))
            if words and words not in said:
                problems.append(f"{where}: (BA5-d3) the verdict "
                                f"{'and its hover drop' if '[hint=' in bb else 'drops'} the {key}")
        if "[hint=" in bb and "[img " not in bb:
            problems.append(f"{where}: (BA5-d3) the verdict folds words into a hover and shows no (i)")
    return problems


GROUND_KINDS = ("plains", "forest", "hills", "mountains", "urban", "river_crossing")


def _ground_claims(where: str, frame: dict, payload: dict) -> list[str]:
    """BA-5 — the ground on the table (the user's tick). The payload's `ground` (the
    province's terrain) is drawn on the felt: the terrain it names, in the stage's own
    order right over the felt (under the lamp, the men and every label), on the
    DEFENDER's half. A payload without one — an old save's, a fleet action's — is a
    bare felt."""
    if "ground" not in frame:
        return []
    want = str(payload.get("ground") or "")
    if want not in GROUND_KINDS or payload.get("naval"):
        want = ""
    got = frame.get("ground") or {}
    if str(got.get("kind") or "") != want:
        return [f"{where}: (BA5-g) the table draws the ground {got.get('kind')!r}; "
                f"the payload's is {want!r}"]
    problems = []
    if want:
        if int(got.get("index", -1)) != 1:
            problems.append(f"{where}: (BA5-g) the ground stands at {got.get('index')} in the stage's "
                            f"order — over the felt and under everything else is 1")
        his_side = 1 if payload.get("player_side") != "defender" else -1
        if int(got.get("dir", 0)) != his_side:
            problems.append(f"{where}: (BA5-g) the ground lies on the attacker's half of the table")
    return problems


def _told_claims(where: str, frame: dict, payload: dict) -> list[str]:
    """BA-5 — a verdict names what told. A payload's `verdict_told` (the server's own
    sentence) stands in the line under the headline at rest, shown: alone, or after the
    table's own line where the province changed hands. A payload without one says no
    such sentence there. (Its place on the baize is every label's: `overlaps`,
    `off_the_baize`.)"""
    told = str(payload.get("verdict_told") or "")
    sub = frame.get("sub_banner") or {}
    if not isinstance(sub, dict):
        return []
    text = str(sub.get("text") or "")
    if told:
        # (the review) where the whole line would leave the baize, what told is said
        # short or rides the line's hover whole — never lost
        cut = told.find(": ")
        short = (told[cut + 2:cut + 3].upper() + told[cut + 3:]) if (told.startswith("Decided") and cut > 0) else ""
        # (the walk of record) where even the province's own line is too wide, its first clause
        # stands and the hover carries the whole line, then what told
        tip = str(sub.get("tip") or "")
        hovered = tip == told or tip.endswith(" " + told)
        said = text == told or text.endswith(" " + told) or (
            hovered and (bool(short) and (text == short or text.endswith(" " + short)) or told not in text))
        if not sub.get("visible") or not said:
            return [f"{where}: (BA5-v) the line under the headline reads {text!r} "
                    f"({'shown' if sub.get('visible') else 'hidden'}); what told is {told!r}"]
        return []
    if re.search(r"\btold\b|\ban even fight\b", text, flags=re.I):
        return [f"{where}: (BA5-v) the line under the headline says what told ({text!r}) on a "
                f"payload that carries none"]
    return []


SPEED_WORDS = {"x1": "Speed ×1", "x2": "Speed ×2"}
TRAY_H = 744                         # battle_diorama.gd TRAY_H (the tray without a day's room)
SPEED_ROOM = [846, 696, 110, 42]     # Close's room in the tray's design pixels (to the tray's floor)


def _long_line_claims(by_id: dict, payloads: dict, spec: dict) -> list[str]:
    """(BA5-w, the session's review) A liberation's line and what told under the headline:
    on the baize and on no other line at the shipped size and at 130 % — what told said
    whole, short, or whole on the line's hover (`_told_claims`), the province's own line
    always."""
    wrong = []
    for rid in ("ulm_full__long_line", "ulm_full__long_line_130"):
        if rid not in spec:
            continue
        frame = _frame(by_id.get(rid), "settled")
        if not frame:
            wrong.append(f"{rid}: (BA5-w) no settled frame")
            continue
        wrong += [f"{rid}: (BA5-w) off the baize — {w}" for w in off_the_baize(frame)]
        wrong += [f"{rid}: (BA5-w) ink over ink — {w}" for w in overlaps(frame)]
        wrong += _told_claims(rid, frame, payloads[spec[rid]["payload"]])
        sub = frame.get("sub_banner") or {}
        text, tip = str(sub.get("text") or ""), str(sub.get("tip") or "")
        head = LONG_LINE.split(" — ", 1)[0] + "."
        if LONG_LINE not in text and not (text.startswith(head) and tip.startswith(LONG_LINE)):
            wrong.append(f"{rid}: (BA5-w) the province's own line is neither under the headline whole nor "
                         f"its first clause there with the whole on the line's hover: {text!r} / {tip!r}")
    return wrong


def _speed_claims(by_id: dict) -> list[str]:
    """BA-5 — the acts' speed (the user's tick, "Speed for the acts"). `clock_pct` is the
    engine's clock against the walk's own (100 = the walk's pace): the acts take it only
    at twice the speed and only while something plays, and give it back at the gavel, at
    a skip and at a close. The table's own switch stands beside the skip hint and nowhere
    else; a press on it is not a click on the table (the acts go on)."""
    problems = []
    for rid, res in by_id.items():
        fast = rid.startswith("ulm_full__speed")
        for row in res.get("frames") or []:
            if "clock_pct" not in row:
                continue
            where = f"{rid}/{row.get('tag')}"
            sw = row.get("speed_switch") or {}
            if bool(sw.get("shown")) != bool(row.get("skip_hint_visible")):
                problems.append(f"{where}: (BA5-s1) the speed switch is "
                                f"{'up' if sw.get('shown') else 'gone'} while the skip hint is "
                                f"{'up' if row.get('skip_hint_visible') else 'gone'}")
            if sw.get("shown"):
                if sw.get("text") != SPEED_WORDS.get(row.get("speed_setting")):
                    problems.append(f"{where}: (BA5-s1) the switch reads {sw.get('text')!r} at "
                                    f"the setting {row.get('speed_setting')!r}")
                # it stands in Close's own room (x 846..956, y 698..738 of the tray), which
                # the table keeps clear of the plate, the seal and the laurels
                rect = sw.get("rect") or []
                # (BA-6) Close's room moves down with the tray's foot while a day's panel asks for room
                room = [SPEED_ROOM[0], SPEED_ROOM[1] + int(row.get("tray_h", TRAY_H) or TRAY_H) - TRAY_H,
                        SPEED_ROOM[2], SPEED_ROOM[3]]
                if len(rect) == 4 and rect[2] > room[2]:
                    # (large type) the switch is wider than Close: it keeps Close's right edge and grows leftward
                    room = [SPEED_ROOM[0] + SPEED_ROOM[2] - rect[2], room[1], rect[2], room[3]]
                if len(rect) != 4 or not _rect_inside(rect, room, slack=3):
                    problems.append(f"{where}: (BA5-s1) the switch stands outside Close's room "
                                    f"({rect}, the room {room})")
                mine = sw.get("window_rect") or []
                for piece, at in (row.get("chrome") or {}).items():
                    if piece in ("close", "replay") or len(mine) != 4:
                        continue
                    if _overlap(mine, at, slack=0):
                        problems.append(f"{where}: (BA5-s1) the switch stands on the {piece} "
                                        f"({mine} against {at})")
            if not fast and int(row.get("clock_pct", 100)) != 100:
                problems.append(f"{where}: (BA5-s1) the clock reads {row.get('clock_pct')}% on a "
                                f"table at its own pace")
            want = 200 if (row.get("speed_setting") == "x2" and sw.get("shown")) else 100
            if fast and int(row.get("clock_pct", 100)) != want:
                problems.append(f"{where}: (BA5-s2) the clock reads {row.get('clock_pct')}%, the "
                                f"table wants {want}% (setting {row.get('speed_setting')!r}, "
                                f"{'playing' if sw.get('shown') else 'at rest'})")
    settled = _frame(by_id.get("ulm_full__settled"), "settled")
    x2 = by_id.get("ulm_full__speed_x2")
    if x2:
        playing, end = _frame(x2, "playing"), _frame(x2, "end")
        if playing.get("final") or int(playing.get("clock_pct", 0)) != 200:
            problems.append("twice as fast: (BA5-s2) the acts are not playing on a doubled clock "
                            f"(final {playing.get('final')}, clock {playing.get('clock_pct')}%)")
        if not end.get("final") or int(end.get("clock_pct", 0)) != 100:
            problems.append("twice as fast: (BA5-s2) the clock was not given back at the gavel "
                            f"(final {end.get('final')}, clock {end.get('clock_pct')}%)")
        if settled and _table(end) != _table(settled):
            problems.append("twice as fast: (BA5-s2) the acts end on another table than the settled frame")
    pressed = by_id.get("ulm_full__speed_switch")
    if pressed:
        before, faster, back, end = (_frame(pressed, t) for t in ("before", "faster", "back", "end"))
        if before.get("speed_setting") != "x1" or int(before.get("clock_pct", 0)) != 100:
            problems.append("the speed switch: (BA5-s3) the table did not open at its own pace")
        if faster.get("final"):
            problems.append("the speed switch: (BA5-s3) a press on it skipped the acts")
        if faster.get("speed_setting") != "x2" or int(faster.get("clock_pct", 0)) != 200:
            problems.append("the speed switch: (BA5-s3) a press did not double the clock and keep "
                            f"the setting ({faster.get('speed_setting')!r}, {faster.get('clock_pct')}%)")
        if back.get("final") or back.get("speed_setting") != "x1" or int(back.get("clock_pct", 0)) != 100:
            problems.append("the speed switch: (BA5-s3) a second press did not give the clock back "
                            f"({back.get('speed_setting')!r}, {back.get('clock_pct')}%, final {back.get('final')})")
        if not end.get("final") or (settled and _table(end) != _table(settled)):
            problems.append("the speed switch: (BA5-s3) the acts did not end on the settled frame")
        if pressed.get("missed"):
            problems.append(f"the speed switch: (BA5-s3) missed {pressed.get('missed')}")
    closed = by_id.get("ulm_full__speed_closed")
    if closed:
        playing, after = _frame(closed, "playing"), _frame(closed, "closed")
        if int(playing.get("clock_pct", 0)) != 200:
            problems.append("closed at twice the speed: (BA5-s4) the acts were not on a doubled clock")
        if after.get("visible") or int(after.get("clock_pct", 0)) != 100:
            problems.append("closed at twice the speed: (BA5-s4) the clock was not given back with "
                            f"the table (visible {after.get('visible')}, clock {after.get('clock_pct')}%)")
    return problems


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


# Client defects the walk's day claims found are listed here, reported to the
# lead session and not fixed in the walk. A known defect is printed as KNOWN and
# does not fail the walk — but it is STRICT: when the scene stops showing it,
# the walk fails until its row is deleted, so a fixed defect cannot stay
# "known". (No defect is known at present.)
KNOWN_PREFIX = "KNOWN-"
KNOWN_DEFECTS: dict = {}
KNOWN_SEEN: list[str] = []

HINT_RX = re.compile(r"\[hint=([^\]]*)\]")
CHIP_HEAD = "[table=1,baseline]"
PIP_RX = re.compile(r"\[img width=\d+ height=\d+ color=#([0-9a-f]{6})\][^\[]*swatch\.png\[/img\]")
PIP_ON = "d9c08c"
URL_RX = re.compile(r"\[url=day:(\d+)\]")
DAY_MORE_KEY = "daymore"    # battle_acts.gd DAY_MORE_KEY: the quiet chip's own link
EXITS_RIGHT_EDGE = 716      # the exits row stands left of Replay (x 726)
EXIT_CARDS_FLOOR = 735      # battle_acts.gd DAY_BOTTOM (738) less DAY_EXIT_FLOOR (3): where the exits' cards end
STAGE_TOP = 52              # the baize begins here: the band above it is the day's head's (BA-5)
# the line under a day's headline: BA-3's, and BA-5's two (an open day, a closed one)
DAY_LINE_HEADS = ("The last clash", "The day so far", "The day:")
DEFAULT_TEXT_SIZE = 1.15


def _plain(text: str) -> str:
    """Words only: lower case, no spaces, no marks (a hover's cleaned text and
    a payload's reason differ in quotes and spacing, never in words)."""
    return re.sub(r"[^a-z0-9]", "", str(text).lower())


def _shown_text(seg: str) -> str:
    """What a chip's BBCode shows: no images, no tags, one space."""
    seg = re.sub(r"\[img[^\]]*\][^\[]*\[/img\]", "", seg)
    seg = re.sub(r"\[/?[a-z_]+(?:[= ][^\]]*)?\]", "", seg)
    return re.sub(r"\s+", " ", seg.replace(" ", " ")).strip()


def _rect_inside(inner, outer, slack: int = 1) -> bool:
    return (inner[0] >= outer[0] - slack and inner[1] >= outer[1] - slack
            and inner[0] + inner[2] <= outer[0] + outer[2] + slack
            and inner[1] + inner[3] <= outer[1] + outer[3] + slack)


def day_digits(chips: list) -> dict:
    """BA-4, the rule of the fixed slots, worked here from the block alone:
    {index into `chips`: digit}. 1 the lead presses (or strikes back), 2 the
    Guard, 3 he digs in; 4 to 6 the first three chips of every other kind, in
    the block's own order; 7 he stands, 8 break off / fall back, 9 leave it
    to him. A slot is one chip's; a kind that is not offered leaves its digit
    unused, and a chip past the sixth has none."""
    own, groups, exits = day_split(chips)
    out, taken = {}, set()
    for i in own:
        digit = {"press": 1, "guard": 2, "dig_in": 3}.get(chips[i].get("kind"))
        if digit and digit not in taken:
            out[i] = digit
            taken.add(digit)
    nxt = 4
    for _kind, idx in groups:
        for i in idx:
            if nxt <= 6:
                out[i] = nxt
                nxt += 1
    for i in exits:
        digit = 9 if chips[i].get("word") == "leave_it" else (7 if chips[i].get("kind") == "stand" else 8)
        if digit not in taken:
            out[i] = digit
            taken.add(digit)
    return out


def day_digit_shots(chips: list) -> dict:
    """BA-4: the digits the walk presses on a day that offers `chips` —
    {shot kind: digit}: the first lit slot of the lead's own words, of the
    groups and of the exits; a slot no chip holds; a locked chip's slot; and
    the lowest lit slot again while the acts still play."""
    by_digit = {d: i for i, d in day_digits(chips).items()}
    lit = sorted(d for d, i in by_digit.items() if chips[i].get("ok"))
    out = {}
    for kind, want in (("digit_own", lambda d: d <= 3), ("digit_group", lambda d: 4 <= d <= 6),
                       ("digit_exit", lambda d: d >= 7)):
        d = next((d for d in lit if want(d)), None)
        if d is not None:
            out[kind] = d
    empty = next((d for d in range(1, 10) if d not in by_digit), None)
    if empty is not None:
        out["digit_empty"] = empty
    locked = next((d for d, i in sorted(by_digit.items()) if not chips[i].get("ok")), None)
    if locked is not None:
        out["digit_locked"] = locked
    if lit:
        out["digit_playing"] = lit[0]
    return out


def _one_chip_claims(where: str, i: int, chip: dict, seg: str, *, name_only: bool,
                     digit: int = 0) -> list[str]:
    """A lit chip is a link (`[url=day:<i>]`) with no lock; a dim chip is the
    disabled pill (the lock, NO link) and carries its reason as its hover. A
    chip written whole carries its label and, when it costs, its price; a name
    chip carries the marshal's name and its hover the full label. BA-4: a chip
    with a digit shows it first ("1 Ney presses · 1", "4 Davout"), and no
    other chip opens with a digit."""
    wrong = []
    price = int(chip.get("price", 0))
    opens = _shown_text(seg)
    if digit and not opens.startswith(f"{digit} "):
        wrong.append(f"{where}: (BA4-d) chip {i} {chip.get('label')!r} holds digit {digit} and reads {opens!r}")
    if not digit and re.match(r"^\d ", opens):
        wrong.append(f"{where}: (BA4-d) chip {i} {chip.get('label')!r} holds no digit and reads {opens!r}")
    if name_only:
        want = str(chip.get("shown") or chip.get("label", "")).replace(" ", " ")
    else:
        bare = str(chip.get("label", "")).replace(" ", " ")
        want = bare if price <= 0 else f"{bare} · {price}"
        if price <= 0 and f"{bare} ·" in seg:
            wrong.append(f"{where}: chip {i} {chip.get('label')!r} is free and carries a price")
    if want not in seg:
        wrong.append(f"{where}: chip {i} {chip.get('label')!r} (price {price}) is not drawn as {want!r}")
    linked, locked = f"[url=day:{i}]" in seg, "lock-simple" in seg
    hints = [_plain(h) for h in HINT_RX.findall(seg)]
    if name_only and not any(_plain(chip.get("label", "")) in h for h in hints):
        wrong.append(f"{where}: name chip {i} does not carry its full label {chip.get('label')!r} as its hover")
    if chip.get("ok"):
        if not linked or locked:
            wrong.append(f"{where}: chip {i} {chip.get('label')!r} is lit and is drawn "
                         f"{'without its link' if not linked else 'with a lock'}")
    else:
        if linked or not locked:
            wrong.append(f"{where}: chip {i} {chip.get('label')!r} is dim and is drawn "
                         f"{'as a link' if linked else 'without its lock'}")
        if chip.get("why") and not any(_plain(chip["why"]) in h for h in hints):
            wrong.append(f"{where}: dim chip {i} {chip.get('label')!r} does not carry its "
                         f"reason {chip.get('why')!r} (hovers: {hints})")
    named = opens[len(f"{digit} "):] if digit and opens.startswith(f"{digit} ") else opens
    if linked and name_only and not named.startswith(str(chip.get("shown") or chip.get("label", ""))):
        wrong.append(f"{where}: (q) the name chip under day:{i} reads {opens!r}, the chip "
                     f"at that index is {chip.get('shown')!r}")
    return wrong


def _day_chip_claims(rid: str, day: dict, src: dict, digits: dict | None = None,
                     built: dict | None = None) -> list[str]:
    """Claims 4, (d), (m) and (q) over the three boxes: row C (the lead's own
    words, full chips), rows D (one line per kind: a plain label once with the
    price, then name-only chips; a kind with ONE chip is written whole), row E
    (the exits). `src` holds each box's BBCode."""
    wrong = []
    chips = day.get("chips") or []
    own, groups, exits = day_split(chips)
    # BA-4: the digits the table gave are the fixed slots' (worked here from
    # the block), and each chip opens with its own
    want_digits = day_digits(chips)
    if digits is not None and {int(k): int(v) for k, v in digits.items()} != want_digits:
        wrong.append(f"{rid}: (BA4-d) the table's digits {dict(sorted((int(k), int(v)) for k, v in digits.items()))} "
                     f"are not the fixed slots' {dict(sorted(want_digits.items()))}")
    seg_own = src["own"].split(CHIP_HEAD)[1:]
    if len(seg_own) != len(own):
        return [f"{rid}: row C draws {len(seg_own)} chip(s), the day offers {len(own)} of its own"]
    for i, seg in zip(own, seg_own):
        wrong += _one_chip_claims(f"{rid} row C", i, chips[i], seg, name_only=False,
                                  digit=want_digits.get(i, 0))
    segs = src["groups"].split(CHIP_HEAD)[1:]       # one run of chips, whether the groups flow inline or by line
    # (BA6-4, fewer chips) the groups show the chips the digits 4-6 reach and ONE quiet "+N more" chip
    # that holds the rest (its hover names them); pressed, every chip stands and the chip reads "show fewer"
    more_open = bool((built or {}).get("more_open"))
    shown_idx = [[i for i in idx if more_open or want_digits.get(i)] for _kind, idx in groups]
    hidden = [i for (_kind, idx), keep in zip(groups, shown_idx) for i in idx if i not in keep]
    n_more = sum(1 for _kind, idx in groups for i in idx if not want_digits.get(i))
    n_more_chip = 1 if n_more > 0 else 0
    if built is not None and int(built.get("more_n") or 0) != n_more:
        wrong.append(f"{rid}: (BA6-4) the table counts {built.get('more_n')} word(s) behind '+N more', "
                     f"the digits leave {n_more}")
    if len(segs) != sum(len(k) for k in shown_idx) + n_more_chip:
        return wrong + [f"{rid}: (BA6-4) rows D draw {len(segs)} chip(s), the day's groups show "
                        f"{sum(len(k) for k in shown_idx)} and {n_more_chip} '+N more'"]
    if n_more_chip:
        more_seg = segs[-1]
        segs = segs[:-1]
        want_more = "show fewer" if more_open else f"+{n_more} more"
        if want_more not in _shown_text(more_seg) or f"[url={DAY_MORE_KEY}]" not in more_seg:
            wrong.append(f"{rid}: (BA6-4) the quiet chip reads {_shown_text(more_seg)!r} / "
                         f"{'linked' if f'[url={DAY_MORE_KEY}]' in more_seg else 'not linked'}, wanted {want_more!r}")
        if not more_open:
            for i in hidden:
                if _plain(chips[i].get("label", "")) not in _hovers(more_seg):
                    wrong.append(f"{rid}: (BA6-4) the '+{n_more} more' hover does not name {chips[i].get('label')!r}")
    said = _shown_text(src["groups"]).replace("\u00a0", " ")     # (a label never breaks inside itself)
    cursor = 0
    taken = 0
    for (kind, full), idx in zip(groups, shown_idx):
        mine = segs[taken: taken + len(idx)]
        taken += len(idx)
        if not idx:
            if GROUP_LABEL.get(kind) and (GROUP_LABEL[kind] + ":") in said:
                wrong.append(f"{rid} rows D: the {kind} group shows a label and no chip")
            continue
        if kind not in GROUP_LABEL:
            # a kind the table has no label for is written whole, chip by chip
            for i, seg in zip(idx, mine):
                wrong += _one_chip_claims(f"{rid} rows D", i, chips[i], seg, name_only=False,
                                          digit=want_digits.get(i, 0))
            continue
        # (the second reading) every kind stands under a label that says what it DOES and
        # its price in points - a kind of one word as a kind of five
        price = int(chips[idx[0]].get("price", 0))
        want = GROUP_LABEL[kind] + (f" · {price} point{'' if price == 1 else 's'}" if price > 0 else "") + ":"
        found = said.find(want, cursor)
        if found < 0:
            wrong.append(f"{rid} rows D: the {kind} group's label {want!r} is not drawn (in order)")
        else:
            cursor = found + len(want)
        for i, seg in zip(idx, mine):
            wrong += _one_chip_claims(f"{rid} rows D", i, chips[i], seg, name_only=True,
                                      digit=want_digits.get(i, 0))
    seg_exit = src["exits"].split(CHIP_HEAD)[1:]
    if len(seg_exit) != len(exits):
        return wrong + [f"{rid}: row E draws {len(seg_exit)} exit(s), the day offers {len(exits)}"]
    for i, seg in zip(exits, seg_exit):
        wrong += _one_chip_claims(f"{rid} row E", i, chips[i], seg, name_only=False,
                                  digit=want_digits.get(i, 0))
    # (m) the chips stand in the block's array order: C, then D, then E
    metas = [int(m) for m in URL_RX.findall(src["own"] + "\n" + src["groups"] + "\n" + src["exits"])]
    if metas != sorted(metas) or len(set(metas)) != len(metas):
        wrong.append(f"{rid}: (m) the chips are not drawn in the block's array order ({metas})")
    return wrong


def _pip_counts(text: str) -> tuple[int, int]:
    cols = PIP_RX.findall(text)
    return len(cols), sum(1 for c in cols if c == PIP_ON)


def _day_head_claims(where: str, day: dict, head: dict, text_size: float = 1.15) -> list[str]:
    """(c) and (e): the pips are drawn from `ours_of` / `theirs_of` (slots) and
    the points left (lit); the head names his temper and his road when the block
    gives them — in the line or in its hover."""
    wrong = []
    src = re.sub(r"\[/?hint[^\]]*\]", "", head.get("source", ""))
    left, _, right = src.partition("against")
    for label, side, of_key, left_key in (("ours", left, "ours_of", "ours"), ("his", right, "theirs_of", "theirs")):
        slots, lit = _pip_counts(side)
        want_slots = int(day.get(of_key) or 0) or max(int(day.get(left_key, 0)), 2)
        if slots != want_slots or lit != int(day.get(left_key, 0)):
            wrong.append(f"{where}: {label} purse is drawn {lit} lit of {slots} slots, the day gives "
                         f"{day.get(left_key)} of {want_slots}")
    # K3 (the second reading: the prefix gave its room to the purses' own words) the head
    # begins with the lead's name and says each purse in words - at the shipped size and
    # under it always; over it the words are the last thing the line gives up
    said = re.sub(r"[\s\ufffc]+", " ", str(head.get("text", "")).replace("\u00a0", " ")).strip()
    lead = str(day.get("lead_shown") or "")
    if lead and not said.startswith(lead):
        wrong.append(f"{where}: (K3) the head does not begin with the lead's name {lead!r}: {said[:50]!r}")
    ours_of = int(day.get("ours_of") or 0) or max(int(day.get("ours", 0)), 2)
    his_of = int(day.get("theirs_of") or 0) or max(int(day.get("theirs", 0)), 2)
    in_words = (f"{int(day.get('ours', 0))} of {ours_of} points", f"{int(day.get('theirs', 0))} of {his_of}")
    if " points" in said and not all(w in said for w in in_words):
        wrong.append(f"{where}: (K3) the head's words are not the day's purses {in_words}: {said[:90]!r}")
    if " points" not in said and text_size <= 1.15:
        wrong.append(f"{where}: (K3) the head does not say the purses in words at text {text_size:g}: {said[:90]!r}")
    temper = str(day.get("his_temper") or "")
    src_all = src + " " + " ".join(HINT_RX.findall(head.get("source", "")))     # the line, and its hover
    if temper and temper not in src_all:
        wrong.append(f"{where}: the head (or its hover) does not name his temper {temper!r}")
    road = day.get("his_road")
    if isinstance(road, bool):
        phrase = "his road is open" if road else "no road behind him"
        if phrase not in src_all:
            wrong.append(f"{where}: the head (or its hover) does not say {phrase!r}")
    return wrong


def _sliced(where: str, ln: dict, what: str) -> list[str]:
    """(j) NOTHING IS SLICED: every text row of a box lies wholly inside the box.
    A box that does not scroll holds all its content; a box that scrolls (the
    groups, cut to whole rows) shows at the top only whole rows and reaches all
    of its content."""
    wrong = []
    box_h = ln["box"][3]
    rows = ln.get("rows") or []
    if ln.get("scroll_active"):
        cut = [r for r in rows if r[0] < box_h < r[1]]
        if cut:
            wrong.append(f"{where}: (j) {what} {ln['text'][:30]!r} is SLICED at its bottom edge "
                         f"({box_h} px): a row {cut[0]} is cut")
        if ln.get("v_max", 0) < ln["content_h"] - 1:
            wrong.append(f"{where}: {what} scrolls but cannot reach all of its content "
                         f"(reach {ln.get('v_max')} of {ln['content_h']})")
    else:
        if ln["content_h"] > box_h + 1 or any(r[1] > box_h + 1 for r in rows):
            wrong.append(f"{where}: (j) {what} {ln['text'][:30]!r} is SLICED: content {ln['content_h']} px "
                         f"in a box of {box_h} px, not scrolling")
    if ln["content_w"] > ln["box"][2] + 1:
        wrong.append(f"{where}: {what} {ln['text'][:30]!r} runs past its box's right edge "
                     f"({ln['content_w']} of {ln['box'][2]} px)")
    return wrong


NOTES_SEEN: list[str] = []      # facts the walk records and does not fail on


def _button_places(where: str, frame: dict, follows: bool) -> list[str]:
    """K4: every table reads Close at x 846 and Replay at x 726; a table that
    FOLLOWS keeps Close's right edge at x 956 and Replay slides left of it."""
    btns = frame.get("buttons") or {}
    if not btns or not frame.get("final"):
        return []
    close, replay = btns["close"], btns["replay"]
    if follows:
        if abs(close[0] + close[2] - 956) > 1 or replay[0] + replay[2] > close[0]:
            return [f"{where}: (K4) on a table that follows Close ends at x {close[0] + close[2]} (956) and "
                    f"Replay at {replay[0] + replay[2]} (left of {close[0]})"]
        NOTES_SEEN.append(f"{where}: follows table: Close x {close[0]}, Replay x {replay[0]}")
        return []
    if close[0] != 846 or replay[0] != 726:
        return [f"{where}: (K4) the buttons stand at Close x {close[0]} / Replay x {replay[0]}, not 846 / 726"]
    foot = int(frame.get("tray_h", TRAY_H) or TRAY_H) - 46         # (BA-6) the foot's own line: the tray's height less 46
    if close[1] != foot or replay[1] != foot:
        return [f"{where}: (BA6-1) the buttons stand at y {close[1]} / {replay[1]}, the tray's foot is y {foot}"]
    return []


def _day_claims(rid: str, res: dict, end: dict, settled: dict, payload: dict, own: dict | None = None) -> list[str]:
    """BA-3, the day's panel. A table with a day builds the panel hidden, holds it
    back while the acts play, shows it at rest in the room of the verdict, the
    name plate and the seal — inside the tray, on no other line of text, clear of
    Replay and Close, nothing sliced; the lead's own words on row C (the Guard
    beside the press), the other words in compact groups, the exits the last
    row; the banner; the shelf. A table without a day builds none."""
    day = payload.get("day") if isinstance(payload.get("day"), dict) else None
    own = own or {}
    own_banner = str(own.get("banner") or "")
    wrong = []
    if day is None:
        for name, frame in (("end", end), ("settled", settled)):
            built = frame.get("day") or {}
            if int(frame.get("tray_h_built", TRAY_H)) != TRAY_H or int(frame.get("day_room", 0)) != 0:
                wrong.append(f"{rid} {name}: (BA6-1) a table with no day has a tray {frame.get('tray_h_built')} high "
                             f"(room {frame.get('day_room')}), not {TRAY_H}")
            if built.get("has"):
                wrong.append(f"{rid} {name}: a day's panel on a table that has no day")
            wrong += _button_places(f"{rid} {name}", frame, False)
            if str((frame.get("sub_banner") or {}).get("text", "")).startswith(DAY_LINE_HEADS):
                wrong.append(f"{rid} {name}: (K11) a table with no day carries a day's morning in the sub-banner")
            if frame.get("close_text") not in (None, "Close"):
                wrong.append(f"{rid} {name}: (K4) a table that does not follow reads {frame.get('close_text')!r} on its primary button")
            if not frame.get("verdict_visible") or not frame.get("plate_visible") \
                    or (frame.get("seal_exists") and not frame.get("seal_visible")):
                wrong.append(f"{rid} {name}: a table without a day lost its verdict "
                             f"({frame.get('verdict_visible')}), plate ({frame.get('plate_visible')}) "
                             f"or seal ({frame.get('seal_visible')})")
        if payload.get("register") in ("triumph", "defeat") and (payload.get("script") or {}).get("acts") \
                and not end.get("scribble_seen"):
            wrong.append(f"{rid}: (K10 control) a battle's verdict was not written with the quill")
        return wrong
    if not day.get("open") and not day.get("banner"):
        # a day decided by its clash builds NO panel: the table stands as on any battle
        for name, frame in (("end", end), ("settled", settled)):
            if (frame.get("day") or {}).get("has"):
                wrong.append(f"{rid} {name}: a day decided by its clash built a panel")
            if not frame.get("verdict_visible") or not frame.get("plate_visible"):
                wrong.append(f"{rid} {name}: a day decided by its clash lost the verdict or the plate")
            sub = frame.get("sub_banner") or {}
            if str(sub.get("text", "")).startswith(DAY_LINE_HEADS):
                wrong.append(f"{rid} {name}: (K11) a decided day carries the day's morning in the sub-banner")
            wrong += _button_places(f"{rid} {name}", frame, False)
        if not end.get("scribble_seen"):
            wrong.append(f"{rid}: (K10) a day decided by its clash lost the verdict's quill")
        return wrong
    rows = [(row.get("tag"), row) for row in res.get("frames") or []] + [("settled (2nd viewing)", settled)]
    offered = bool(day.get("open")) and day.get("awaits") == "ours" and not day.get("pending") \
        and not day.get("follows") and bool(day.get("chips"))
    chips = day.get("chips") or []
    own_chips, groups, exits = day_split(chips)
    text_size = float(res.get("text_size") or DEFAULT_TEXT_SIZE)
    for tag, frame in rows:
        built = frame.get("day") or {}
        where = f"{rid}/{tag}"
        if not built.get("has"):
            wrong.append(f"{where}: the table carries a day and no panel was built")
            continue
        if not frame.get("final"):
            if built.get("visible"):
                wrong.append(f"{where}: the day's panel is on the table while the acts play")
            continue
        if not built.get("visible"):
            wrong.append(f"{where}: the day's panel is not shown at rest")
        else:
            # K1 the panel comes in when the table is final: never with the skip hint, never without Close
            if frame.get("skip_hint_visible") or not frame.get("close_shown"):
                wrong.append(f"{where}: (K1) the panel stands with the skip hint up "
                             f"({frame.get('skip_hint_visible')}) or without Close ({frame.get('close_shown')})")
        wrong += _button_places(where, frame, bool(day.get("follows")))
        # K4 the primary button of a table that FOLLOWS reads "His answer ▸"; any other says "Close"
        want_close = "His answer" if day.get("follows") else "Close"
        if want_close not in str(frame.get("close_text", "")) or (
                not day.get("follows") and frame.get("close_text") != "Close"):
            wrong.append(f"{where}: (K4) the primary button reads {frame.get('close_text')!r} on a table "
                         f"{'that follows' if day.get('follows') else 'that does not follow'}")
        if frame.get("verdict_visible") or frame.get("plate_visible") or frame.get("seal_visible"):
            wrong.append(f"{where}: at rest the verdict ({frame.get('verdict_visible')}), plate "
                         f"({frame.get('plate_visible')}) or seal ({frame.get('seal_visible')}) "
                         f"stands in the panel's room")
        tray = built.get("tray") or [0, 0, 1000, 744]
        prect = built.get("rect") or [0, 0, 0, 0]
        if not _rect_inside(prect, tray):
            wrong.append(f"{where}: the panel {prect} leaves the tray {tray}")
        # (o) the shelf is hidden at rest only when the panel took its room
        # (the second reading: before a word loses what it does the panel may take
        # DAY_LIFT px of the gap under the bars - that is not the shelf's room)
        took_room = prect[1] < int(frame.get("verdict_y", prect[1])) - (DAY_LIFT if built.get("lifted") else 0)
        was_up = bool(own.get("shelf_visible"))
        if own and bool(frame.get("shelf_visible")) != (was_up and not took_room):
            wrong.append(f"{where}: (o) the shelf is {'up' if frame.get('shelf_visible') else 'hidden'} "
                         f"(the clash's own table has it {'up' if was_up else 'down'}) and the panel "
                         f"{'took' if took_room else 'did not take'} its room "
                         f"(panel y {prect[1]}, verdict y {frame.get('verdict_y')})")
        if took_room and not was_up:
            wrong.append(f"{where}: (o) the panel rose above the verdict where there was no shelf to give room")
        # (BA5-t) the lift is said: the panel's top is its plain top, less DAY_LIFT exactly when it lifted
        if "top_plain" in built and prect[1] != int(built["top_plain"]) - (DAY_LIFT if built.get("lifted") else 0):
            wrong.append(f"{where}: (BA5-t) the panel's top is {prect[1]}, its plain top {built['top_plain']}, "
                         f"and the table says lifted={built.get('lifted')}")
        lines = [ln for ln in built.get("lines") or [] if ln.get("text", "").strip()]
        # BA-4: the first day's own line (`first_open`) — on a row of its own
        # above the head where the table has room for it whole, else nowhere
        # on the panel (it rides the head's hover); read apart from the rows
        first_rows = [ln for ln in lines if ln.get("first")]
        lines = [ln for ln in lines if not ln.get("first")]
        wrong += _day_first_claims(where, day, built, first_rows, lines, tray)
        # BA-5: the head (the purses, his temper and road, Berthier's reading) stands in the
        # band above the baize - the tray's own empty 52 px - whatever the panel holds below
        heads = [ln for ln in lines if ln.get("head")]
        if len(heads) != 1 or heads[0] is not lines[0]:
            wrong.append(f"{where}: (BA5-h) the panel draws {len(heads)} head(s), or not first")
        elif heads[0]["box"][1] != 0 or not _rect_inside(heads[0]["ink"], tray) \
                or heads[0]["ink"][1] < prect[1]:
            # (the second reading) the stakes head the decision block: the panel's own first row
            wrong.append(f"{where}: (BA5-h) the head is not the panel's first row "
                         f"(box {heads[0]['box']}, ink {heads[0]['ink']}, panel {prect})")
        wrong += _day_band_claims(where, built, frame, payload, offered, text_size)
        wrong += _day_finish_claims(where, day, built, frame, offered)
        wrong += _day_lever_claims(rid, where, day, built, frame, offered, text_size, lines)
        kinds = {k: [ln for ln in lines if ln.get(k)] for k in ("chips", "groups", "exits")}
        for ln in lines:
            what = ("row C (the lead's own words)" if ln.get("chips") else "rows D (the groups)"
                    if ln.get("groups") else "row E (the exits)" if ln.get("exits") else "a line")
            if not _rect_inside(ln["ink"], tray):
                wrong.append(f"{where}: {what} of the panel {ln['text'][:40]!r} {ln['ink']} leaves the tray")
            wrong += _sliced(where, ln, what)
            if ln.get("scroll_active") and not ln.get("groups"):
                wrong.append(f"{where}: {what} scrolls (only the groups may, by whole rows)")
            for other in built.get("others") or []:
                if _overlap(ln["ink"], other["rect"]):
                    wrong.append(f"{where}: the panel's {ln['text'][:30]!r} {ln['ink']} is on another "
                                 f"line of text {other['text']!r} {other['rect']}")
            for shelf in frame.get("shelf_rects") or []:
                if _overlap(ln["ink"], shelf):
                    wrong.append(f"{where}: the panel's {ln['text'][:30]!r} {ln['ink']} is on the shelf {shelf}")
            for button, brect in (built.get("buttons") or {}).items():
                if _overlap(ln["ink"], brect):
                    wrong.append(f"{where}: the panel's {ln['text'][:30]!r} {ln['ink']} is on the "
                                 f"{button} button {brect}")
        # (p) on Ulm no box scrolls at 1.0 and 1.15; at 1.3 only the groups, by whole rows
        if rid == "day_ulm" and text_size <= 1.15 and any(ln.get("scroll_active") for ln in lines):
            wrong.append(f"{where}: (p) a box scrolls on Ulm at text size {text_size:g}")
        # the last told line is on the panel (or on the head's hover); chips only for a
        # day that awaits us and whose clash no other follows
        told = [t.get("line", "") for t in day.get("told") or [] if t.get("line")]
        said = " ".join(ln["text"] + " " + ln.get("source", "") for ln in lines).replace(" ", " ")
        # (BA-5: on the head's hover the line is the hover's cleaned text - a typographic
        # apostrophe for a straight one - so it is read there by its words)
        hovered = _plain(" ".join(HINT_RX.findall(" ".join(ln.get("source", "") for ln in lines))))
        if told and told[-1] not in said and _plain(told[-1]) not in hovered:
            wrong.append(f"{where}: the day's last told line {told[-1]!r} is not on the panel")
        # (BA5-o, the session's review) a closed day keeps the line that says HOW it ended: on
        # the table, or on the head's hover with the rest of a close the table had no row for
        ends = [t.get("line", "") for t in day.get("told") or [] if t.get("who") == "end" and t.get("line")]
        if not day.get("open") and ends:
            for end_line in ends:
                if end_line not in said and _plain(end_line) not in hovered:
                    wrong.append(f"{where}: (BA5-o) the closing table drops a line of the close "
                                 f"({end_line!r}): on neither the table nor the head's hover")
            # (the re-review) ON the table: the rows' own text, never a hover's — `said` holds
            # each label's source, and the head's hover rides in its [hint=…]
            on_table = " ".join(ln["text"] for ln in lines).replace(" ", " ")
            if ends[0] not in on_table:
                wrong.append(f"{where}: (BA5-o) the line that says how the day ended ({ends[0]!r}) "
                             f"is not on the closing table")
        if lines:
            wrong += _day_head_claims(where, day, lines[0], text_size)
        # K5 on the guns' day: the last told line stands just under the head while the room allows,
        # the groups never scroll
        if rid == "day_guns":
            grp = [ln for ln in lines if ln.get("groups")]
            if grp and grp[0].get("scroll_active"):
                wrong.append(f"{where}: (K5) the groups box scrolls on the day with three groups")
            if built.get("inline") is not None:
                NOTES_SEEN.append(f"{where}: groups inline={built.get('inline')} at text {text_size:g}")
            told_last = [t.get("line", "") for t in day.get("told") or [] if t.get("line")]
            # (BA-4: on the first day of a campaign the first day's own line may
            # take that row for its one showing — the told line is then on the hover)
            if told_last and text_size <= 1.15 and not first_rows:
                # (BA-5: the head stands in the band above the baize - the told line is the
                # panel's own first row)
                # (the second reading: the told line gives way before a word loses what it
                # does - where it HAS a row, the row stands above the words)
                told_rows = [ln for ln in lines if not (ln.get("chips") or ln.get("groups") or ln.get("exits")
                                                        or ln.get("head") or ln.get("rule"))
                             and told_last[-1] in ln["text"].replace("\u00a0", " ")]
                words_top = min([ln["box"][1] for ln in lines
                                 if ln.get("chips") or ln.get("groups") or ln.get("exits")] or [10 ** 6])
                if told_rows and told_rows[0]["box"][1] > words_top:
                    wrong.append(f"{where}: (K5) the last told line stands under the words "
                                 f"(text {text_size:g})")
                NOTES_SEEN.append(f"{where}: the last told line has {'a row' if told_rows else 'the hover'} "
                                  f"at text {text_size:g}")
        if bool(built.get("has_chips")) != (offered and bool(own_chips)) \
                or bool(built.get("has_groups")) != (offered and bool(groups)) \
                or bool(built.get("has_exits")) != offered:
            wrong.append(f"{where}: boxes on the panel C={built.get('has_chips')} D={built.get('has_groups')} "
                         f"E={built.get('has_exits')}; the day offers {len(own_chips)} own, {len(groups)} group "
                         f"kind(s), {len(exits)} exit(s) (open={day.get('open')}, awaits={day.get('awaits')!r}, "
                         f"follows={day.get('follows')})")
        if offered and built.get("has_exits"):
            src = {k: (kinds[key][0]["source"] if kinds[key] else "")
                   for k, key in (("own", "chips"), ("groups", "groups"), ("exits", "exits"))}
            wrong += _day_chip_claims(where, day, src, built.get("digits"), built)
            e_ln = kinds["exits"][0] if kinds["exits"] else None
            # (k) the Guard, when offered, is the second chip of the array, on row C beside the press
            guard = [i for i in own_chips if chips[i].get("kind") == "guard"]
            if guard:
                seg = src["own"].split(CHIP_HEAD)[1:]
                c_ln = kinds["chips"][0] if kinds["chips"] else None
                if guard[0] != 1 or chips[0].get("kind") != "press" or len(seg) < 2 \
                        or "The Guard" not in seg[1]:
                    wrong.append(f"{where}: (k) the Guard is not the second chip of row C beside the press")
                elif c_ln and (len(c_ln.get("rows") or []) != 1 or c_ln["content_w"] > c_ln["box"][2] + 1
                               or not _rect_inside(c_ln["ink"], tray)):
                    wrong.append(f"{where}: (k) row C is not one whole row ({c_ln.get('rows')}, "
                                 f"{c_ln['content_w']} of {c_ln['box'][2]} px): the Guard may be cut")
            # (l) the exits row is the LAST row, whole, left of x 716, clear of Replay and Close
            if e_ln:
                # K2 the exits row stands on the buttons' mid-line (within 1 px) and above the frame's inner line (738)
                btns = built.get("buttons") or {}
                exits_up = bool(built.get("exits_up"))
                if btns and exits_up:
                    # (the second reading) two-line cards beside the buttons, whole, above the
                    # frame's inner line (738)
                    e_bottom = prect[1] + e_ln["box"][1] + e_ln["box"][3]
                    if built.get("exits_row"):
                        # (BA-6) the exits' stakes need the width: a full-width row on the line above the buttons
                        want_bottom = btns["close"][1] - 4
                        if abs(e_bottom - want_bottom) > 2:
                            wrong.append(f"{where}: (BA6-3) the exits' full-width row ends at y {e_bottom}: it stands "
                                         f"on the line above the buttons (y {want_bottom})")
                    else:
                        floor = tray[3] - 6 - 3          # DAY_BOTTOM + room, less DAY_EXIT_FLOOR
                        if abs(e_bottom - floor) > 2:
                            wrong.append(f"{where}: (BA5-e) the exits' cards end at y {e_bottom}: they stand on "
                                         f"the tray's floor ({floor}), beside the buttons")
                elif btns:
                    centre_b = btns["close"][1] + btns["close"][3] / 2.0
                    centre_e = prect[1] + e_ln["box"][1] + e_ln["box"][3] / 2.0
                    clamped = abs(prect[1] + e_ln["box"][1] + e_ln["box"][3] - (tray[3] - 6 - 3)) <= 2   # (BA-6) the floor's own line
                    if abs(centre_e - centre_b) > 1.0 and not clamped:
                        wrong.append(f"{where}: (K2) the exits row's mid-line ({centre_e:.1f}) is not the buttons' "
                                     f"({centre_b:.1f})")
                    if prect[1] + e_ln["box"][1] + e_ln["box"][3] >= tray[3] - 6:
                        wrong.append(f"{where}: (K2) the exits row's bottom reaches the frame's inner line ({tray[3] - 6})")
                bottom = e_ln["box"][1] + e_ln["box"][3]
                others_bottom = max([ln["box"][1] + ln["box"][3] for ln in lines if ln is not e_ln] or [0])
                right_edge = 970 if built.get("exits_row") else EXITS_RIGHT_EDGE
                if bottom < others_bottom or e_ln["ink"][0] + e_ln["ink"][2] > right_edge:
                    wrong.append(f"{where}: (l) the exits row is not the last row or runs past x {right_edge} "
                                 f"(bottom {bottom} / {others_bottom}, ink {e_ln['ink']})")
        if not day.get("open") and "[url=day:" in " ".join(
                ln.get("source", "") for ln in built.get("lines") or []):
            wrong.append(f"{where}: a closed day shows chips")
        # (g) a table that follows shows no chips and gives no word on show
        if frame.get("emitted"):
            wrong.append(f"{where}: the table gave {frame.get('emitted')} on show")
    # K11 the sub-banner carries the day's morning, clear of the dice's room
    if rid in ("day_opens", "day_ulm", "day_defence", "day_night") and day.get("morning"):
        for name, frame in (("end", end), ("settled", settled)):
            sub = frame.get("sub_banner") or {}
            if not sub.get("visible") or sub.get("text") != day.get("morning"):
                wrong.append(f"{rid} {name}: (K11) the sub-banner reads {sub.get('text')!r} "
                             f"({'shown' if sub.get('visible') else 'hidden'}), the day's morning is {day.get('morning')!r}")
            ink, dice = frame.get("sub_ink") or [], frame.get("dice_rect") or []
            if ink and dice:
                over = ink[1] + ink[3] - dice[1]
                if over > 0 and text_size <= 1.15:
                    wrong.append(f"{rid} {name}: (K11) the sub-banner reaches {over} px into the dice's room at text {text_size:g}")
                elif over > 0:
                    NOTES_SEEN.append(f"{rid} {name}: the sub-banner ends {over} px into the dice's room at text {text_size:g}")
                else:
                    NOTES_SEEN.append(f"{rid} {name}: the sub-banner ends {-over} px above the dice at text {text_size:g}")
    # K10 no quill, no fanfare, no bell over a day's own banner
    if str(day.get("banner") or ""):
        for name, frame in (("end", end),):
            if frame.get("scribble_seen") or any("fanfare_erafnaf" in c or "bell_toll_single" in c
                                                  for c in frame.get("cues") or []):
                wrong.append(f"{rid} {name}: (K10) the verdict's quill / fanfare / bell sounded over a day's banner "
                             f"(quill {frame.get('scribble_seen')}, cues {frame.get('cues')})")
    # (n) the banner: the day's own words replace the clash's headline at rest
    banner = str(day.get("banner") or "")
    for name, frame in (("end", end), ("settled", settled)):
        shown = str(frame.get("banner") or "")
        if banner and shown != banner.upper():
            wrong.append(f"{rid} {name}: (n) the headline reads {shown!r}, the day's banner is {banner.upper()!r}")
        elif not banner and own_banner and shown != own_banner:
            wrong.append(f"{rid} {name}: (n) with no banner the headline reads {shown!r}, the clash's own is {own_banner!r}")
        if banner and own_banner and shown == own_banner and own_banner != banner.upper():
            wrong.append(f"{rid} {name}: (n) the clash's own headline stands over a day")
    return wrong


def wrap_does(does: str) -> list[str]:
    """battle_acts.gd `_wrap_does`: an exit's stakes in two lines, cut at a semicolon."""
    parts = does.split("; ")
    if len(parts) < 2:
        return [does]
    cut = -(-len(parts) // 2)
    return ["; ".join(parts[:cut]), "; ".join(parts[cut:])]


def _hovers(seg: str) -> str:
    return " ".join(_plain(h) for h in HINT_RX.findall(seg))


EXIT_TAG_ORDER = ("leave_it", "break_off", "stand")     # battle_acts.gd DAY_TAG_ORDER


def _exit_rank(chip: dict) -> int:
    """An exit's turn to keep its tag beside the buttons (-1: none)."""
    if str(chip.get("word") or "") == "leave_it":
        return 0
    kind = str(chip.get("kind") or "")
    return EXIT_TAG_ORDER.index(kind) if kind in EXIT_TAG_ORDER else -1


def _day_band_claims(where: str, built: dict, frame: dict, payload: dict, offered: bool,
                     text_size: float = 1.15) -> list[str]:
    """Row BA, BA-5, the second reading. (BA5-n) the band above the baize names the battle —
    the plate's own words, whose room the panel takes. (BA5-u) the day's rule stands on a
    table that offers its words: on its own caption line, or in the first day's line (which
    says it in full), or on the head's hover; a table that offers none says none. (BA5-k)
    at rest the two counters say they count this clash."""
    wrong = []
    named = built.get("name") if isinstance(built.get("name"), dict) else None
    battle = str(payload.get("battle_name") or "").strip()
    if battle:
        want = f"{battle.upper()}  ·  TURN {int(payload.get('turn') or 0)}"
        if named is None or not named.get("shown") or named.get("text") != want:
            wrong.append(f"{where}: (BA5-n) the band above the baize reads "
                         f"{(named or {}).get('text')!r} ({'shown' if (named or {}).get('shown') else 'hidden'}), "
                         f"the battle is {want!r}")
        elif named["rect"][1] < 0 or named["rect"][1] + named["rect"][3] > STAGE_TOP:
            wrong.append(f"{where}: (BA5-n) the battle's name does not stand in the band above the baize "
                         f"(rect {named['rect']}, the baize begins at y {STAGE_TOP})")
    elif named is not None:
        wrong.append(f"{where}: (BA5-n) the band names a battle ({named.get('text')!r}) the payload does not")
    lines = [ln for ln in built.get("lines") or [] if ln.get("text", "").strip()]
    rule_rows = [ln for ln in lines if ln.get("rule")]
    first_rows = [ln for ln in lines if ln.get("first")]
    head = next((ln for ln in lines if ln.get("head")), None)
    hover = _plain(" ".join(HINT_RX.findall((head or {}).get("source", ""))))
    if bool(built.get("rule_row")) != bool(rule_rows):
        wrong.append(f"{where}: (BA5-u) the table says its rule has a row ({built.get('rule_row')}) and "
                     f"draws {len(rule_rows)}")
    if offered:
        if rule_rows and _plain(rule_rows[0].get("text", "")) != _plain(DAY_RULE):
            wrong.append(f"{where}: (BA5-u) the rule's line reads {rule_rows[0].get('text')!r}")
        if rule_rows and first_rows:
            wrong.append(f"{where}: (BA5-u) the day's rule and the first day's line both stand (one says the other)")
        if not rule_rows and not first_rows and _plain(DAY_RULE) not in hover:
            wrong.append(f"{where}: (BA5-u) the day's rule is nowhere on a table that offers its words")
    elif rule_rows:
        wrong.append(f"{where}: (BA5-u) a table that offers no word says the day's rule")
    if frame.get("final"):
        caps = [str(pair[0]) for pair in frame.get("counters") or []]
        # (the type is held at the 130 % step above it, so the scoped captions fit as they do there)
        if len(caps) != 2 or not any(cap.endswith(DAY_CLASH_SCOPE) for cap in caps):
            wrong.append(f"{where}: (BA5-k) neither counter says it counts this clash ({caps})")
    return wrong


def _guns_claims(rid: str, res: dict, settled: dict, payload: dict) -> list[str]:
    """Row BA, BA-5, the second reading — figures that agree. (BA5-q) Before an assault the
    guns' toll is counted as the battery fires: on the frame shot at the battery the two
    counters read what the beat says the guns took and cost, and the band's figure of the
    side they fired on reads its muster less that. A cannonade's own table counts its whole
    toll as its battery fires: the frame shot at the battery reads every strength line, both
    counters and the band as the table at rest does. And no table without a day says a
    counter counts "this clash"."""
    wrong = []
    for name, frame in (("end", _frame(res, "end")), ("settled", settled)):
        caps = [str(pair[0]) for pair in (frame or {}).get("counters") or []]
        if not isinstance(payload.get("day"), dict) and any(cap.endswith(DAY_CLASH_SCOPE) for cap in caps):
            wrong.append(f"{rid} {name}: (BA5-k) a table with no day says a counter counts this clash ({caps})")
    frame = _frame(res, "battery")
    battery = [b for act in ((payload.get("script") or {}).get("acts") or [])
               for b in (act.get("beats") or []) if b.get("kind") == "battery"]
    if not frame or frame.get("final") or not battery:
        return wrong
    figures = [str(pair[1]) for pair in frame.get("counters") or []]
    band = [str(fig) for fig in frame.get("band") or []]
    if _kind(payload) == "battle":
        first = battery[0]
        dealt, taken = int(first.get("dealt", 0) or 0), int(first.get("taken", 0) or 0)
        for what, n in (("took", dealt), ("cost", taken)):
            if n > 0 and f"{n:,}" not in figures:
                wrong.append(f"{rid}/battery: (BA5-q) no counter reads what the guns {what} ({n:,}): {figures}")
        target = "defender" if first.get("side") == "attacker" else "attacker"
        before = int((payload.get(target) or {}).get("committed_total", 0) or 0)
        if dealt > 0 and before > 0 and f"{before:,} → {before - dealt:,}" not in band:
            wrong.append(f"{rid}/battery: (BA5-q) the band does not read the guns' toll "
                         f"({before:,} → {before - dealt:,}): {band}")
    else:
        def running(row):
            return sorted(label for label in row.get("labels") or [] if " → " in label)
        rest_figures = [str(pair[1]) for pair in settled.get("counters") or []]
        if running(frame) != running(settled) or figures != rest_figures \
                or band != [str(fig) for fig in settled.get("band") or []]:
            wrong.append(f"{rid}/battery: (BA5-q) a cannonade's count has not ended as its battery fired: "
                         f"{running(frame)} {figures} {band}, at rest {running(settled)} {rest_figures}")
    return wrong


def _day_finish_claims(where: str, day: dict, built: dict, frame: dict, offered: bool) -> list[str]:
    """Row BA, BA-5 - what the table says of a word and of him.
    (BA5-r) the head ends on Berthier's reading where the block carries one, and on none
    where it does not. (BA5-c) the lead's own words are two-line CARDS while the ladder
    left them their second lines: each carries what it does (a locked one, why it is
    locked) on its face; without them the chip's hover says it. (BA5-e) the exits on a
    row of their own say what they do after a dash; level with the buttons they say it
    as far as the row fits left of Replay, in a fixed order (leave it, leave the field,
    stand), and the rest keep it for their hovers. (BA5-l) the ladder's order: the exits give up their row before the
    last word told gives up its own, and the cards keep their second lines longer than
    either. (BA5-p) Close wears the primary look except while the words are offered."""
    wrong = []
    lines = [ln for ln in built.get("lines") or [] if ln.get("text", "").strip()]
    head = next((ln for ln in lines if ln.get("head")), None)
    reading = str((day.get("reading") or {}).get("line") or "") if isinstance(day.get("reading"), dict) else ""
    if head is not None:
        said = str(head.get("text", "")).replace("\u00a0", " ").strip()
        if reading and not said.endswith(reading):
            wrong.append(f"{where}: (BA5-r) the head does not end on Berthier's reading {reading!r}: {said[-60:]!r}")
        if not reading and any(w in said for w in ("he will strike", "he may strike", "he will not strike")):
            wrong.append(f"{where}: (BA5-r) the head carries a reading the block does not: {said[-60:]!r}")
    if frame.get("final") and "close_primary" in frame:
        if bool(frame.get("close_primary")) == bool(offered):
            wrong.append(f"{where}: (BA5-p) Close is {'primary' if frame.get('close_primary') else 'plain'} "
                         f"on a table that {'offers its words' if offered else 'offers none'}")
    if not offered:
        return wrong
    chips = day.get("chips") or []
    own, _groups, exits = day_split(chips)
    box = {key: next((ln for ln in lines if ln.get(key)), None) for key in ("chips", "exits")}
    cards, exits_up, tags = bool(built.get("cards")), bool(built.get("exits_up")), bool(built.get("exit_tags"))
    kept = int(built.get("tags_kept") or 0)
    if box["chips"] is not None:
        segs = box["chips"]["source"].split(CHIP_HEAD)[1:]
        for i, seg in zip(own, segs):
            chip = chips[i]
            does = str(chip.get("does") or "")
            face = _shown_text(seg).replace("\u00a0", " ")
            want = does if (chip.get("ok") or not chip.get("why")) else str(chip.get("why"))
            if cards and want and want not in face:
                wrong.append(f"{where}: (BA5-c) the card of {chip.get('label')!r} does not carry {want!r} on its face: {face!r}")
            if cards and int(chip.get("price", 0)) > 0 and " point" not in face:
                wrong.append(f"{where}: (BA5-c) the card of {chip.get('label')!r} does not say its price in points: {face!r}")
            if not cards and does and does in face:
                wrong.append(f"{where}: (BA5-c) with no cards the chip {chip.get('label')!r} still carries its second line")
            if cards and does and not chip.get("ok") and chip.get("why") and _plain(does) not in _hovers(seg):
                wrong.append(f"{where}: (BA5-c) the locked card of {chip.get('label')!r} says what it would do "
                             f"nowhere (its face says why it is locked; hovers: {_hovers(seg)!r})")
            if not cards and does and _plain(does) not in _hovers(seg):
                wrong.append(f"{where}: (BA5-c) the chip {chip.get('label')!r} says what it does nowhere (hovers: {_hovers(seg)!r})")
    if box["exits"] is not None:
        segs = box["exits"]["source"].split(CHIP_HEAD)[1:]
        for i, seg in zip(exits, segs):
            chip = chips[i]
            does = str(chip.get("does") or "")
            face = _shown_text(seg).replace("\u00a0", " ")
            if not does:
                continue
            on_face = tags or 0 <= _exit_rank(chip) < kept
            # as a card an exit says its price and what it does on its second line (a locked
            # one, why it is locked); as a one-line chip, what it does after a dash
            lit = bool(chip.get("ok")) or not chip.get("why")
            said_as = (("free · " if int(chip.get("price", 0)) <= 0 else "") + does) if tags else f"— {does}"
            if tags and not lit:
                said_as = str(chip.get("why"))
            if tags and lit and built.get("exits_wrapped"):
                # (BA6-3) the stakes wrap at a semicolon: both halves stand, one on each line
                halves = wrap_does(does)
                said_as = ("free · " if int(chip.get("price", 0)) <= 0 else "") + halves[0]
                if len(halves) > 1 and halves[1] not in face:
                    wrong.append(f"{where}: (BA6-3) the exit {chip.get('label')!r} wraps its stakes and the second "
                                 f"line {halves[1]!r} is not on its face: {face!r}")
            if on_face and said_as not in face:
                wrong.append(f"{where}: (BA5-e) the exit {chip.get('label')!r} does not say {said_as!r} on its face: {face!r}")
            if not on_face and (does in face or _plain(does) not in _hovers(seg)):
                wrong.append(f"{where}: (BA5-e) the exit {chip.get('label')!r} carries a tag out of its turn, "
                             f"or says what it does nowhere (face {face!r}, kept {kept})")
    if tags and kept:
        wrong.append(f"{where}: (BA5-e) the exits are cards and count {kept} tag(s) kept as one-line chips")
    if tags != exits_up:
        wrong.append(f"{where}: (BA5-e) the exits say what they do ({tags}) and are cards ({exits_up}): one without the other")
    # (BA5-l) the ladder's order
    told = [t.get("line", "") for t in day.get("told") or [] if t.get("line")]
    told_row = any(told and told[-1] in ln["text"].replace("\u00a0", " ") for ln in lines
                   if not (ln.get("chips") or ln.get("groups") or ln.get("exits") or ln.get("head")
                           or ln.get("first") or ln.get("rule")))
    can_card = any(str(chips[i].get("does") or "") for i in own)
    can_tag = any(str(chips[i].get("does") or "") for i in exits)
    # (BA5-l, the second reading) a word keeps what it does longer than the table keeps its
    # own lines: the exits' cards give way for their width, or after the day's rule, the last
    # word told and the first day's line have; the cards' second lines after the exits' cards
    stood = [name for name, up in (("the day's rule", bool(built.get("rule_row"))),
                                   ("the last word told", told_row),
                                   ("the first day's line", any(ln.get("first") for ln in built.get("lines") or [])))
             if up]
    if can_tag and not exits_up and not built.get("exits_wide") and stood:
        wrong.append(f"{where}: (BA5-l) the exits lost their cards while {', '.join(stood)} still stood")
    if can_card and not cards and (exits_up or stood) and not built.get("cards_wide"):
        wrong.append(f"{where}: (BA5-l) the cards lost their second lines while the exits' cards ({exits_up}) "
                     f"or {', '.join(stood) or 'no line'} still stood")
    return wrong


def what_told(payload: dict) -> str:
    """battle_acts.gd `_what_told`: the cause alone, capitalised, no full stop ('' where none)."""
    line = str(payload.get("verdict_told") or "")
    if not line or line == "<null>":
        line = str((payload.get("day") or {}).get("verdict_told") or "") if isinstance(payload.get("day"), dict) else ""
    line = line.strip()
    if not line or line == "<null>":
        return ""
    if line.startswith("Decided") and ": " in line:
        line = line[line.rindex(": ") + 2:]
    elif line.startswith("Decided") and line.rstrip(".").endswith(", in an even fight"):
        line = "An even fight"
    if line.endswith("."):
        line = line[:-1]
    return line[:1].upper() + line[1:]


def _signed_pct(n: int) -> str:
    return f"+{n}%" if n >= 0 else f"\u2212{abs(n)}%"


def _luck_claims(where: str, frame: dict, payload: dict, text_size: float = 1.0) -> list[str]:
    """(BA6-5) the dice plate's third row sets the luck against what told, in one phrase:
    '<What told>; the dice added +X% to the blow, the day's fortune +Y% to us' — X the roll's
    lands figure against the average throw's 102 %, Y OUR side's fortune; a table whose payload
    names nothing that told keeps the fortune line as it was. Read where the row stands."""
    texts = frame.get("dice_texts") or []
    if not texts:
        return []                      # (an old save's tableau has no dice plate at all)
    roll = next((b for b in _beats(payload) if b.get("kind") == "dice"), None)
    if roll is None:
        return []
    told = what_told(payload)
    attacker_left = str(payload.get("player_side") or "") != "defender"
    key = "fortune_attacker" if attacker_left else "fortune_defender"
    if len(texts) < 3:
        # the third row (the luck) is printed wherever the tray's room holds it: at the sizes the shipped
        # 106 px serves (100 %, 115 %) it must stand; from 120 % the three rows no longer fit the room
        # (a Caption line of 24 px) and the plate keeps two - and the luck takes the SECOND row in its
        # short form (the C12 ruling: the dice's share and the day's fortune, no wider than the lands
        # row it replaces; what told stands on the verdict's line)
        if text_size <= 1.15 + 1e-6:
            return [f"{where}: (BA6-5) the dice plate shows {len(texts)} row(s) ({texts!r}), wanted three"]
        if not told or len(texts) < 2:
            return []
        crit = str(roll.get("critical") or "")
        prefix = "a twelve: " if crit == "success" else ("a two: " if crit == "failure" else "")
        short = (f"{prefix}the dice added {_signed_pct(int(roll.get('swing', 0)) + 100 - 102)} to the blow, "
                 f"the day's fortune {_signed_pct(int(roll.get(key, 0)))} to us")
        if str(texts[1]) != short:
            return [f"{where}: (BA6-5) at Text size {text_size:g} the luck's short row reads {texts[1]!r}, "
                    f"wanted {short!r}"]
        return []
    last = str(texts[2])
    if not told:
        if not last.startswith("the day's fortune in strength:"):
            return [f"{where}: (BA6-5) with nothing told the luck row reads {last!r}"]
        return []
    want = (f"{told}; the dice added {_signed_pct(int(roll.get('swing', 0)) + 100 - 102)} to the blow, "
            f"the day's fortune {_signed_pct(int(roll.get(key, 0)))} to us")
    if last != want:
        return [f"{where}: (BA6-5) the luck row reads {last!r}, wanted {want!r}"]
    return []


def _day_lever_claims(rid: str, where: str, day: dict, built: dict, frame: dict, offered: bool,
                      text_size: float, lines: list) -> list[str]:
    """Row BA, "the levers past 5" (BA-6): (BA6-1) the tray grows by DAY_ROOM while a day's panel
    stands and the panel's floor with it; (BA6-2) the lead's own words are THREE-line cards where
    the ladder left room — the word and its price at the body's size, what it does and what it
    risks at the Caption step, the third line shed before the second (a card without it carries
    its risk on its hover); (BA6-3) the exits' stakes stand on their faces, full width on the line
    above the buttons where they do not fit beside them; (BA6-4) the groups show the chips the
    digits reach and a quiet '+N more'; (BA6-6) the table's marks stand in one caption line
    above the exits, else on the head's hover."""
    wrong = []
    room = int(built.get("room") or 110)
    if not frame.get("final"):
        return wrong
    if int(frame.get("tray_h_built", 0)) != TRAY_H + room or int(frame.get("day_room", 0)) != room \
            or int(frame.get("tray_h", 0)) != TRAY_H + room:
        wrong.append(f"{where}: (BA6-1) the tray is {frame.get('tray_h_built')} high (room {frame.get('day_room')}) "
                     f"while a day's panel stands, wanted {TRAY_H + room}")
    prect = built.get("rect") or [0, 0, 0, 0]
    if prect[1] + prect[3] != TRAY_H + room - 6:
        wrong.append(f"{where}: (BA6-1) the panel's floor is y {prect[1] + prect[3]}, the tray's less its edge "
                     f"is {TRAY_H + room - 6}")
    if not offered or not built.get("visible"):
        return wrong
    chips = day.get("chips") or []
    own, groups, exits = day_split(chips)
    by = {key: next((ln for ln in lines if ln.get(key)), None) for key in ("chips", "groups", "exits")}
    # (BA6-2) three-line cards
    if built.get("risk_lines") and not built.get("cards"):
        wrong.append(f"{where}: (BA6-2) the cards carry a third line and no second")
    if by["chips"] is not None:
        segs = by["chips"]["source"].split(CHIP_HEAD)[1:]
        for i, seg in zip(own, segs):
            chip = chips[i]
            risk = str(chip.get("risk") or "")
            if not risk or not chip.get("ok"):
                continue
            face = _shown_text(seg).replace("\u00a0", " ")
            if built.get("risk_lines"):
                if risk not in face:
                    wrong.append(f"{where}: (BA6-2) the card of {chip.get('label')!r} does not carry what it risks "
                                 f"({risk!r}) on its face: {face!r}")
                head_line = seg.split("\n", 1)[0]
                if "[font_size" in head_line:
                    wrong.append(f"{where}: (BA6-2) the card of {chip.get('label')!r} sets its first line "
                                 f"(the word and its price) in a smaller step")
                if seg.count("[font_size") < 2:
                    wrong.append(f"{where}: (BA6-2) the card of {chip.get('label')!r} has {seg.count('[font_size')} "
                                 f"Caption line(s), wanted 2 (what it does, what it risks)")
            else:
                if risk in face or _plain(risk) not in _hovers(seg):
                    wrong.append(f"{where}: (BA6-2) a card with no third line still carries {risk!r}, or says it "
                                 f"nowhere (hovers: {_hovers(seg)!r})")
    # (BA6-3) the exits' faces say the stakes (BA5-e), beside the buttons or on a row of their own
    # (independent evidence: the box's own measured size and place, the buttons' record and the card lines
    # drawn - never the panel's flags read against each other)
    e_ln = by["exits"]
    if e_ln is not None and built.get("exits_up"):
        btn_top = (built.get("buttons") or {}).get("close", [0, 0, 0, 0])[1]
        e_box_w, e_bottom = e_ln["box"][2], prect[1] + e_ln["box"][1] + e_ln["box"][3]
        if built.get("exits_row"):
            if abs(e_box_w - prect[2]) > 2 or e_bottom > btn_top:
                wrong.append(f"{where}: (BA6-3) the exits' full-width row is {e_box_w} px wide (the panel is "
                             f"{prect[2]}) and ends at y {e_bottom}, the buttons' top is {btn_top}")
        elif e_box_w >= prect[2] - 2:
            wrong.append(f"{where}: (BA6-3) the exits stand beside the buttons in a box {e_box_w} px wide "
                         f"(the panel is {prect[2]}: Replay's room is not kept)")
    if e_ln is not None and built.get("exits_wrapped"):
        two = sum(1 for seg in e_ln["source"].split(CHIP_HEAD)[1:] if seg.count("[font_size") >= 2)
        if not two:
            wrong.append(f"{where}: (BA6-3) the exits wrap their stakes and no card draws two Caption lines")
    if by["exits"] is not None and built.get("exits_wrapped"):
        for i, seg in zip(exits, by["exits"]["source"].split(CHIP_HEAD)[1:]):
            chip = chips[i]
            if chip.get("ok") and len(wrap_does(str(chip.get("does") or ""))) > 1 and seg.count("[font_size") < 2:
                wrong.append(f"{where}: (BA6-3) the exit {chip.get('label')!r} wraps its stakes on "
                             f"{seg.count('[font_size')} Caption line(s), wanted 2")
    if by["exits"] is not None and built.get("exits_up"):
        ink = by["exits"]["ink"]
        if not built.get("exits_row") and ink[0] + ink[2] > EXITS_RIGHT_EDGE:
            wrong.append(f"{where}: (BA6-3) the exits beside the buttons run to x {ink[0] + ink[2]}")
    # (BA6-6) the legend
    leg = next((ln for ln in lines if ln.get("legend")), None)
    head = next((ln for ln in lines if ln.get("head")), None)
    hover = _plain(" ".join(HINT_RX.findall((head or {}).get("source", ""))))
    if built.get("legend_row") != (leg is not None):
        wrong.append(f"{where}: (BA6-6) the table says its legend has a row ({built.get('legend_row')}) and draws "
                     f"{1 if leg else 0}")
    if leg is not None:
        said = _plain(leg.get("text", ""))
        for words in ("eachsideslead", "apointinhand", "apointspent", "keys19saythewords",
                      "acardits" + "price"):
            if words not in said:
                wrong.append(f"{where}: (BA6-6) the legend does not say {words!r}: {leg.get('text')!r}")
        if len(leg.get("rows") or []) != 1 or not leg.get("shown"):
            wrong.append(f"{where}: (BA6-6) the legend is not one shown row ({leg.get('rows')})")
        if by["exits"] is not None and leg["ink"][1] + leg["ink"][3] > by["exits"]["ink"][1]:
            wrong.append(f"{where}: (BA6-6) the legend stands on the exits ({leg['ink']} / {by['exits']['ink']})")
        if leg["ink"][1] < prect[1]:
            wrong.append(f"{where}: (BA6-6) the legend stands above the panel")
    elif "keys1to9saythewords" not in hover and "thekeys1to9saythewords" not in hover:
        wrong.append(f"{where}: (BA6-6) no legend row and none on the head's hover")
    # (BA6-4) the groups: at most the chips the digits reach, plus the quiet chip
    if groups and not built.get("more_open"):
        n_digit = sum(1 for _k, idx in groups for i in idx if day_digits(chips).get(i))
        links = len(URL_RX.findall((by["groups"] or {}).get("source", ""))) if by["groups"] else 0
        if links > 3 or links != n_digit:
            wrong.append(f"{where}: (BA6-4) the groups draw {links} lit chip(s), the digits 4-6 reach {n_digit}")
        total = sum(len(idx) for _k, idx in groups)
        if total > 3 and int(built.get("more_n") or 0) != total - 3:
            wrong.append(f"{where}: (BA6-4) {total} group words and '+N more' counts {built.get('more_n')}")
        if total > 3 and rid in ("day_crowded", "day_guns", "day_ulm") and not built.get("more_n"):
            wrong.append(f"{where}: (BA6-4) no '+N more' on a crowded day")
    return wrong


def _day_first_claims(where: str, day: dict, built: dict, first_rows: list, lines: list,
                      tray: list) -> list[str]:
    """BA-4, the first day's line (the block's `first_open`). Where it has a
    row: ONE row, shown, at the panel's top, whole and inside the tray, the
    head right under it — and no chip scrolls for it (it may take the told
    line's row for its one showing: the last word told is then on the head's
    hover, where the claim on the day's last told line still finds it). Where
    it has none it is on the head's hover, and the table says it showed
    nothing (`first_shown`). A day whose block carries no line shows none."""
    wrong = []
    fo = day.get("first_open") if isinstance(day.get("first_open"), dict) else None
    said = str((fo or {}).get("line") or "")
    shown = str(built.get("first_shown") or "")
    if not said or not day.get("open"):
        if first_rows or shown:
            wrong.append(f"{where}: (BA4-f) a first-open line stands on a table whose block carries none")
        return wrong
    if not first_rows:
        if shown:
            wrong.append(f"{where}: (BA4-f) the table acknowledged {shown!r} and drew no row for it")
        head = lines[0] if lines else {}
        if _plain(said) not in _plain(" ".join(HINT_RX.findall(head.get("source", "")))):
            wrong.append(f"{where}: (BA4-f) the first day's line has no row and is not on the head's hover")
        return wrong
    row = first_rows[0]
    if len(first_rows) != 1 or not row.get("shown"):
        wrong.append(f"{where}: (BA4-f) the first day's line is drawn {len(first_rows)} time(s), "
                     f"shown={row.get('shown')}")
    if _plain(said) != _plain(row.get("text", "")):
        wrong.append(f"{where}: (BA4-f) the row reads {row.get('text')!r}, the block's line is {said!r}")
    head = next((ln for ln in lines if ln.get("head")), None)
    under_head = int(head["box"][3]) if head else 0
    if abs(row["box"][1] - under_head) > 1 or not _rect_inside(row["ink"], tray):
        wrong.append(f"{where}: (BA4-f) the first day's line does not stand right under the head inside the "
                     f"tray (box {row['box']}, the head is {under_head} px tall, ink {row['ink']})")
    wrong += _sliced(where, row, "the first day's line")
    # (BA-5: the head stands in the band above the baize - `(BA5-h)`; the line is the
    # panel's first row and the words follow it)
    if shown != str((fo or {}).get("screen") or ""):
        wrong.append(f"{where}: (BA4-f) the line is on the table and the table acknowledged {shown!r}")
    if any(ln.get("scroll_active") for ln in lines):
        wrong.append(f"{where}: (BA4-f) a box scrolls on a table that gave the first day's line a row")
    return wrong


def _day_press_claims(rid: str, res: dict, day: dict, by_id: dict | None = None) -> list[str]:
    """BA-3 claims 5 and 6, and (h), (i), (n), (o), (q): one press, one word; a dim
    chip sends nothing; a compact group's name chip sends ITS corps' order; Esc
    closes the table with the panel up (no line takes focus); a day that awaits
    HIM asks once; a payload with no acts shows the panel at rest; the ordinary
    battle after a day has its own headline and shelf back."""
    wrong = []
    by_id = by_id or {}
    chips = day.get("chips") or []
    kind = rid.rsplit("__", 1)[-1]
    frame = lambda tag: _frame(res, tag)   # noqa: E731
    before = frame("before")
    if (before.get("emitted") or []) != []:
        wrong.append(f"{rid}: a word was given before any press ({before.get('emitted')})")
    if kind in ("press_lit", "press_word", "press_group"):
        box = {"press_lit": "own", "press_word": "exits", "press_group": "groups"}[kind]
        chip = next((c for c in chips if c.get("ok") and chip_box(c) == box
                     and (c.get("word") or c.get("command"))), None)
        word = chip_word(chip, day) if chip else ""
        pressed = frame("pressed")
        if (pressed.get("emitted") or []) != [word]:
            wrong.append(f"{rid}: one press of {chip.get('label') if chip else '?'!r} gave "
                         f"{pressed.get('emitted')}, wanted exactly [{word!r}]")
        if kind == "press_group" and chip and chip.get("shown") and not word.startswith(chip["shown"]):
            wrong.append(f"{rid}: (q) pressing {chip['shown']!r} sent {word!r}")
        if not (pressed.get("day") or {}).get("latched"):
            wrong.append(f"{rid}: the in-flight latch is not set after the press")
        if "[url=day:" in " ".join(ln.get("source", "") for ln in (pressed.get("day") or {}).get("lines") or []):
            wrong.append(f"{rid}: a chip is still a link after the press (the panel is not inert)")
        again = frame("pressed_again")
        if again and (again.get("emitted") or []) != [word]:
            wrong.append(f"{rid}: a second press before new data gave {again.get('emitted')}, "
                         f"wanted still exactly [{word!r}]")
    elif kind == "beside":
        # BA6-3: short stakes stand BESIDE the buttons (no full-width row), on the tray's floor
        built = frame("settled").get("day") or {}
        e_ln = next((ln for ln in built.get("lines") or [] if ln.get("exits")), None)
        prect = built.get("rect") or [0, 0, 0, 0]
        tray_h = (built.get("tray") or [0, 0, 1000, TRAY_H])[3]
        # (BA1-X4) above Text size 130 % even the short stakes' cards are wider than the room beside
        # the buttons (the panel records it as `exits_wide`), and the designed fallback is the
        # full-width row above them - the same answer the panel gives every longer stake
        size = float(res.get("text_size") or DEFAULT_TEXT_SIZE)
        row_is_the_answer = bool(built.get("exits_row")) and bool(built.get("exits_row_tried")) and size > 1.3
        if not built.get("exits_up") or (built.get("exits_row") and not row_is_the_answer) or e_ln is None:
            wrong.append(f"{rid}: (BA5-e) short stakes did not stand beside the buttons "
                         f"(cards {built.get('exits_up')}, row {built.get('exits_row')})")
        elif not row_is_the_answer and abs(prect[1] + e_ln["box"][1] + e_ln["box"][3] - (tray_h - 6 - 3)) > 2:
            wrong.append(f"{rid}: (BA5-e) the exits' cards beside the buttons end at y "
                         f"{prect[1] + e_ln['box'][1] + e_ln['box'][3]}, the tray's floor is {tray_h - 9}")
    elif kind == "legend":
        # BA6-6: with room (no first-day line) the legend stands whole on its own caption line at the
        # sizes the table has always fitted; at larger type it may ride the head's hover
        built = frame("settled").get("day") or {}
        size = float(res.get("text_size") or DEFAULT_TEXT_SIZE)
        leg = next((ln for ln in built.get("lines") or [] if ln.get("legend")), None)
        if size <= 1.15 and (not built.get("legend_row") or leg is None):
            wrong.append(f"{rid}: (BA6-6) a day with room (no first-day line) has no legend row at text {size:g}")
        elif leg is not None and not leg.get("shown"):
            wrong.append(f"{rid}: (BA6-6) the legend row is not shown")
    elif kind == "more":
        # BA6-4: the quiet chip sends no word; pressed it shows every chip of the groups, pressed again
        # it gives them back — and the digits do not change
        if (frame("open").get("emitted") or []) != [] or (frame("closed").get("emitted") or []) != []:
            wrong.append(f"{rid}: (BA6-4) '+N more' gave a word ({frame('open').get('emitted')})")
        opened, closed = frame("open").get("day") or {}, frame("closed").get("day") or {}
        if not opened.get("more_open") or closed.get("more_open"):
            wrong.append(f"{rid}: (BA6-4) '+N more' did not toggle (open {opened.get('more_open')}, "
                         f"closed again {closed.get('more_open')})")
        _own, groups_now, _exits = day_split(chips)
        total = sum(len(idx) for _k, idx in groups_now)
        for tag, built, want_open in (("open", opened, True), ("closed", closed, False)):
            grp = next((ln for ln in built.get("lines") or [] if ln.get("groups")), {})
            n_links = len(URL_RX.findall(grp.get("source", "")))
            shown = total if want_open else sum(1 for _k, idx in groups_now for i in idx if day_digits(chips).get(i))
            if n_links != shown:
                wrong.append(f"{rid}/{tag}: (BA6-4) the groups draw {n_links} lit chip(s), wanted {shown}")
        if opened.get("digits") != closed.get("digits"):
            wrong.append(f"{rid}: (BA6-4) the digits changed with '+N more'")
        # (BA6-4) the opened box gets the room its words need (the panel is laid again with them),
        # and scrolls only where the ladder could not make that room
        grp_open = next((ln for ln in opened.get("lines") or [] if ln.get("groups")), None)
        if grp_open is not None:
            overflow = grp_open["content_h"] > grp_open["box"][3] + 1
            if overflow and not opened.get("groups_scrolls"):
                wrong.append(f"{rid}: (BA6-4) the opened groups need {grp_open['content_h']} px in a box "
                             f"{grp_open['box'][3]} high and the panel says they do not scroll")
            if overflow and not grp_open.get("scroll_active"):
                wrong.append(f"{rid}: (BA6-4) the opened groups overflow their box and cannot be scrolled to")
            exits_open = next((ln for ln in opened.get("lines") or [] if ln.get("exits")), None)
            if exits_open is not None and grp_open["box"][1] + grp_open["box"][3] > exits_open["box"][1] + 1:
                wrong.append(f"{rid}: (BA6-4) the opened groups run down into the exits' row")
    elif kind == "press_dim":
        pressed = frame("pressed")
        if (pressed.get("emitted") or []) != []:
            wrong.append(f"{rid}: pressing a dim chip gave {pressed.get('emitted')}")
        if (pressed.get("day") or {}).get("latched"):
            wrong.append(f"{rid}: pressing a dim chip set the latch")
    elif kind in ("digit_own", "digit_group", "digit_exit"):
        # BA-4: a bare digit gives its slot's word, once — the chip the fixed
        # slots put under it, never another
        digit = int(day_digit_shots(chips).get(kind) or 0)
        index = {d: i for i, d in day_digits(chips).items()}.get(digit)
        chip = chips[index] if index is not None else None
        word = chip_word(chip, day) if chip else ""
        pressed = frame("pressed")
        if (pressed.get("emitted") or []) != [word] or not word:
            wrong.append(f"{rid}: (BA4-k) digit {digit} gave {pressed.get('emitted')}, its slot holds "
                         f"{chip.get('label') if chip else None!r}: wanted exactly [{word!r}]")
        if not (pressed.get("day") or {}).get("latched"):
            wrong.append(f"{rid}: (BA4-k) the latch is not set after digit {digit}")
        again = frame("pressed_again")
        if again and (again.get("emitted") or []) != [word]:
            wrong.append(f"{rid}: (BA4-k) the same digit a second time gave {again.get('emitted')}, "
                         f"wanted still exactly [{word!r}]")
        if again and int((again.get("day") or {}).get("denied") or 0) < 1:
            wrong.append(f"{rid}: (BA4-k) a digit on a latched table was not denied (the deny cue)")
    elif kind in ("digit_empty", "digit_locked"):
        digit = int(day_digit_shots(chips).get(kind) or 0)
        pressed = frame("pressed")
        if (pressed.get("emitted") or []) != []:
            wrong.append(f"{rid}: (BA4-k) digit {digit} — "
                         f"{'no chip in its slot' if kind == 'digit_empty' else 'a locked chip'} — "
                         f"gave {pressed.get('emitted')}")
        if (pressed.get("day") or {}).get("latched"):
            wrong.append(f"{rid}: (BA4-k) digit {digit} set the latch and gave no word")
        if int((pressed.get("day") or {}).get("denied") or 0) < 1:
            wrong.append(f"{rid}: (BA4-k) digit {digit} was not denied (the deny cue)")
        if pressed.get("visible") is False:
            wrong.append(f"{rid}: (BA4-k) digit {digit} closed the table")
    elif kind == "digit_playing":
        pressed = frame("pressed")
        if (pressed.get("emitted") or []) != []:
            wrong.append(f"{rid}: (BA4-k) a digit while the acts play gave {pressed.get('emitted')}")
        if pressed.get("final"):
            wrong.append(f"{rid}: (BA4-k) a digit while the acts play ended them (it is no skip)")
    elif kind == "then_ordinary":
        after = frame("after")
        built = after.get("day") or {}
        if built.get("has") or built.get("visible"):
            wrong.append(f"{rid}: a day's panel is left on the tableau for a battle with no day")
        if not after.get("final") or not after.get("verdict_visible") or not after.get("plate_visible") \
                or (after.get("seal_exists") and not after.get("seal_visible")):
            wrong.append(f"{rid}: the chrome did not come back for the next battle "
                         f"(verdict {after.get('verdict_visible')}, plate {after.get('plate_visible')}, "
                         f"seal {after.get('seal_visible')})")
        wrong += _button_places(rid, after, False)
        if after.get("close_text") != "Close":
            wrong.append(f"{rid}: (K4) the next table's primary button reads {after.get('close_text')!r}, not 'Close'")
        ref = _frame(by_id.get("ordinary_brief__settled"), "settled")
        if ref:
            if after.get("banner") != ref.get("banner"):
                wrong.append(f"{rid}: (n) the ordinary battle after a day reads {after.get('banner')!r}, "
                             f"its own headline is {ref.get('banner')!r}")
            if after.get("shelf_visible") != ref.get("shelf_visible"):
                wrong.append(f"{rid}: (o) the shelf after a day is {after.get('shelf_visible')}, "
                             f"the ordinary battle's own is {ref.get('shelf_visible')}")
    elif kind == "esc":
        built = before.get("day") or {}
        if not built.get("visible") or not before.get("visible"):
            wrong.append(f"{rid}: Esc was not tried with the panel up")
        if built.get("focus_in_panel") or any(m != 0 for m in built.get("focus_modes") or []):
            wrong.append(f"{rid}: the panel takes keyboard focus (modes {built.get('focus_modes')}, "
                         f"focus in panel {built.get('focus_in_panel')})")
        after = frame("after")
        if after.get("visible") is not False:
            wrong.append(f"{rid}: Esc did not close the table with the panel up")
    elif kind == "no_chips":
        # K7 an open day that awaits OUR word and carries no chips asks the server once
        got = frame("settled").get("emitted") or []
        if got != [f"@refresh:{day.get('enemy', '')}"]:
            wrong.append(f"{rid}: (K7) a day that awaits us with no chips gave {got} on show, wanted exactly "
                         f"one @refresh:{day.get('enemy', '')}")
    elif kind == "goes_on":
        rest, later = frame("rest"), frame("later")
        if "His answer" not in str(rest.get("close_text", "")):
            wrong.append(f"{rid}: (K4) the table that follows does not offer 'His answer' ({rest.get('close_text')!r})")
        if later.get("visible") is not False and int(later.get("dismissed", 0)) < 1:
            wrong.append(f"{rid}: (K4) the table that follows did not go on by itself within 3.8 s of resting")
    elif kind == "replays":
        during, later = frame("during"), frame("later")
        if int(during.get("dismissed", 0)) != 0:
            wrong.append(f"{rid}: (K4) the table was dismissed during the replay")
        if int(later.get("dismissed", 0)) < 1:
            wrong.append(f"{rid}: (K4) after the replay the wait did not restart and carry the table on")
    elif kind == "stays_reduced":
        later = frame("later")
        if later.get("visible") is False or int(later.get("dismissed", 0)) > 0:
            wrong.append(f"{rid}: (K4) under Reduce motion the table that follows went on by itself")
    elif kind == "follows_awaits_him":
        got = frame("settled")
        if got.get("emitted") or (got.get("day") or {}).get("has_chips") or (got.get("day") or {}).get("has_exits"):
            wrong.append(f"{rid}: a table that follows gave {got.get('emitted')} on show (it must ask "
                         f"nothing and offer no chips)")
    elif kind == "awaits_him_skip":
        for tag in ("skipped", "later"):
            got = frame(tag).get("emitted") or []
            if got != [f"@refresh:{day.get('enemy', '')}"]:
                wrong.append(f"{rid}/{tag}: a skipped day that awaits him gave {got}, wanted exactly "
                             f"one @refresh:{day.get('enemy', '')}")
    elif kind in ("awaits_him", "awaits_him_acts"):
        # (h) a table whose day awaits him asks the server exactly once
        last = frame("settled") if kind == "awaits_him" else frame("end")
        got = last.get("emitted") or []
        if got != [f"@refresh:{day.get('enemy', '')}"]:
            wrong.append(f"{rid}: a day that awaits him gave {got} on show, wanted exactly "
                         f"one @refresh:{day.get('enemy', '')}")
        if (last.get("day") or {}).get("has_chips") or (last.get("day") or {}).get("has_exits"):
            wrong.append(f"{rid}: chips on a day that awaits HIM")
    elif kind == "no_script":
        # (i) no acts to play: nothing to hold the panel back for — it stands at rest
        # no acts to play: the host's own first sequence plays; the panel comes in with the table's
        # final state (K1), never before and never missing at rest
        playing = frame("playing")
        if not playing.get("final") and (playing.get("day") or {}).get("visible"):
            wrong.append(f"{rid}/playing: the panel stands while the script-less table still plays")
        got = frame("end")
        built = got.get("day") or {}
        if not (got.get("final") and built.get("has") and built.get("visible")):
            wrong.append(f"{rid}/end: a payload with a day and no script acts does not show the panel at "
                         f"rest (final={got.get('final')}, panel={built.get('has')}/{built.get('visible')})")
    return wrong


def check(results: dict, shots: list[dict]) -> list[str]:
    NOTES_SEEN.clear()
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
        if _kind(payload) == "battle":
            if end.get("dice_shown") != settled.get("dice_shown") or not end.get("dice_shown"):
                problems.append(f"{rid}: the dice are not on both the end and the settled frame")
            # BA5-D6: the throw is read when the dice have landed - mid-tumble the tray shows the
            # dice alone, and the sentence that names the roll has not been read
            for row in res.get("frames") or []:
                if row.get("tag") == "dice_tumbling" and row.get("dice_shown"):
                    if int(row.get("dice_rows_shown", 0)) > 0:
                        problems.append(f"{rid}: (BA5-d6) the tray reads {row.get('dice_rows_shown')} "
                                        f"line(s) while the dice still tumble")
                    if int(row.get("caption_chars", 0)) != 0:
                        problems.append(f"{rid}: (BA5-d6) the throw's sentence is read while the dice tumble")
            for name, frame in (("end", end), ("settled", settled)):
                if frame.get("dice_shown") and int(frame.get("dice_rows_shown", 0)) < 2:
                    problems.append(f"{rid} {name}: (BA5-d6) at rest the tray reads "
                                    f"{frame.get('dice_rows_shown')} line(s) of the throw")
                problems += _luck_claims(f"{rid} {name}", frame, payload,
                                         float(res.get("text_size") or DEFAULT_TEXT_SIZE))
        elif end.get("dice_shown") or settled.get("dice_shown"):
            # BA-2: a wall is not rolled for, and guns throw no dice
            problems.append(f"{rid}: dice on a {_kind(payload)}'s table, which rolled none")
        if end.get("act"):
            problems.append(f"{rid}: an act is still named after the gavel ({end['act']!r})")
        if not end.get("banner") or end.get("banner") != settled.get("banner"):
            problems.append(f"{rid}: the banner differs ({end.get('banner')!r} / "
                            f"{settled.get('banner')!r})")
        # (a table with a day's panel does not write the verdict over the day's own banner — K10 —
        # so the end frame holds no verdict where the settled frame has its text)
        if end.get("told") != settled.get("told") and not (end.get("day") or {}).get("has"):
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
        # BA-2: the wall, the works, the order of battle, column into line
        problems += _wall_claims(rid, res, end, settled, payload)
        problems += _works_claims(rid, res, end, settled, payload)
        problems += _manoeuvre_claims(rid, _frame(res, "opening"), end, settled)
        problems += _square_claims(rid, res, end, settled, payload)
        problems += _standard_claims(rid, end, settled)
        # BA-5: the ground on the table
        problems += _ground_claims(f"{rid} end", end, payload)
        problems += _ground_claims(f"{rid} settled", settled, payload)
        problems += _told_claims(f"{rid} end", end, payload)
        problems += _told_claims(f"{rid} settled", settled, payload)
        problems += _guns_claims(rid, res, settled, payload)
        # BA1-X8: a triumph's laurels flank its banner
        problems += _laurel_claims(f"{rid} end", end)
        problems += _laurel_claims(f"{rid} settled", settled)
        # BA5-D3: the verdict in its room — at rest, and each act's line as it was shot
        problems += _verdict_claims(f"{rid} end", end, payload, at_rest=True)
        problems += _verdict_claims(f"{rid} settled", settled, payload, at_rest=True)
        for row in res.get("frames") or []:
            if row.get("act") and not row.get("final"):
                problems += _verdict_claims(f"{rid}/{row.get('tag')}", row, payload, at_rest=False)
        # BA-3: the day's panel and the room it lends from
        own_frame = _frame(by_id.get(f"{rid}__no_day"), "settled")
        problems += _day_claims(rid, res, end, settled, payload, own_frame)
        # at rest, no line of text stands on another or on a portrait, and
        # none leaves the baize (in motion they may cross: a lead surges)
        for name, frame in (("end", end), ("settled", settled)):
            problems += [f"{rid} {name}: ink over ink — {w}" for w in overlaps(frame)]
            problems += [f"{rid} {name}: off the baize — {w}" for w in off_the_baize(frame)]
            problems += _board_claims(f"{rid} {name}", frame,
                                      float(res.get("text_size") or DEFAULT_TEXT_SIZE))
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

    for rid, shot in spec.items():
        res = by_id.get(rid)
        if res and res.get("ok") and rid.rsplit("__", 1)[-1] in (
                "press_lit", "press_word", "press_group", "press_dim", "esc", "then_ordinary",
                "awaits_him", "awaits_him_acts", "awaits_him_skip", "no_script", "follows_awaits_him",
                "no_chips", "goes_on", "stays_reduced", "replays", "more", "legend", "beside",
                # BA-4: the digits' own shots. They were built and shot and their
                # claims never read — this list did not name them, and the switch-off
                # table said so (three digit cases walked green with the fix off)
                "digit_own", "digit_group", "digit_exit", "digit_empty", "digit_locked",
                "digit_playing"):
            problems += _day_press_claims(rid, res, payloads[shot["payload"]].get("day") or {}, by_id)

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
    problems += _speed_claims(by_id)
    problems += _long_line_claims(by_id, payloads, spec)
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
    # BA-3: the client defects the day's claims found stand apart (KNOWN_DEFECTS)
    KNOWN_SEEN.clear()
    KNOWN_SEEN.extend(p for p in problems if p.startswith(KNOWN_PREFIX))
    problems = [p for p in problems if not p.startswith(KNOWN_PREFIX)]
    for tag, scenes in KNOWN_DEFECTS.items():
        for scene in scenes:
            if scene in spec and by_id.get(scene) and not any(
                    p.startswith(f"{KNOWN_PREFIX}{tag} {scene}") for p in KNOWN_SEEN):
                problems.append(f"known client defect {tag} no longer shows on {scene}: "
                                f"delete its row from KNOWN_DEFECTS")
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
    ap.add_argument("--payloads", default=str(PAYLOADS),
                    help="another folder of staged payloads (never the walk of record)")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # a claim may quote "Ney ◆"
    only = [s.strip() for s in args.only.split(",") if s.strip()]
    payload_dir = Path(args.payloads)
    shots = build_shots(payload_dir, only, args.scale)
    if args.text_size is not None:
        for shot in shots:
            shot["text_size"] = args.text_size
    whole = not only and not args.tag and not args.headless and args.scale == 1.0 \
        and args.time_scale == 1.0 and args.text_size is None and payload_dir == PAYLOADS
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
        "payloads": {p.name: _sha(p) for p in sorted(payload_dir.glob("*.json"))},
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
    for line in KNOWN_SEEN:
        print("KNOWN client defect:", line[len(KNOWN_PREFIX):])
    for line in sorted(set(NOTES_SEEN)):
        print("NOTE:", line)
    for line in problems:
        print("CLAIM:", line)
    done = sum(1 for r in results.get("results") or [] if r.get("ok"))
    print(f"{done}/{len(shots)} shots complete, {len(errors)} script error(s), "
          f"{len(problems)} claim(s) failed; record: {target}")
    return 1 if (errors or problems or done != len(shots)) else 0


if __name__ == "__main__":
    raise SystemExit(main())
