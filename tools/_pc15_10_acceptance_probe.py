"""PC15-10 B5 — the §8 acceptance arm, instrumented (September 27, 2026).

`docs/PETITION_POPUP_REVISIT_SPEC.md` §8 asks five questions of the flagship
arm after the petition revisit: how many blocking petition modals a 24-turn
campaign raises, whether any petition moment is lost in silence, whether an
audience is heard and answered through the same handler as a modal, how many
L1 audiences die unopened (the Q1 re-open observable), and the per-kind table.
The digest answers the first, third and fifth; this probe answers the second
and fourth, which the digest cannot see.

It runs `tools/playtest_driver.py` IN THIS PROCESS (Mode A) with the petition
channel wrapped, so every petition MOMENT the producers make is joined
against its fate:

  * answered   — `handle_petition_response` retired it (a modal OR an
                 audience: the same handler, the same state writes);
  * retired    — `retire_petition` with its receipt (F2);
  * evicted    — a crisis set an audience aside (B1: withdrawn, its latch
                 un-stamped so it returns, one dispatch line says so);
  * withdrawn  — replaced by a re-fire (F6);
  * standing   — still in the slot when the run ends;
  * blocked    — the channel refused it (another card held the slot); for a
                 confrontation the moment is the jealousy FIRE line, which is
                 recorded here with whether the drama cap kept it.

A queued card with none of those is a SILENT LOSS (§8 item 2).

Usage (from the repo root; PYTHONHASHSEED must be set, as the driver needs):
    PYTHONHASHSEED=0 .venv/Scripts/python.exe tools/_pc15_10_acceptance_probe.py \
        OUT.json -- --name b5-flagship-1805 --seed historical --llm mock \
        --script tools/playtest_scripts/flagship_1805.json --turns 24 \
        --objection insist --diplomacy decline --redemption dismiss \
        --petition first_enabled --audience open --declare-war proceed --fresh
Then: .venv/Scripts/python.exe tools/_pc15_10_acceptance_analyze.py \
        docs/audits/playtest_digests/flagship-1805-aug15/digest.jsonl \
        tools/playtest_runs/b5-flagship-1805/digest.jsonl OUT.json
"""
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.game_logic import jealousy as J  # noqa: E402

TRACK = {}          # id(petition) -> record (the object is held, so ids stay unique)
ORDER = []          # every NEW moment's push, in order
FIRE_LINES = []     # (turn, marshal, target, "kept"|"capped") — every player fire line

_orig_push = J._push_petition
_orig_retire = J.retire_petition
_orig_evict = J._evict_audience
_orig_withdraw = J._retire_pending_petition
_orig_answer = J.handle_petition_response
_orig_cap = J._cap_routine_drama


def _level(petition):
    try:
        return int((petition.get("context") or {}).get("escalation_level", 0) or 0)
    except (TypeError, ValueError):
        return 0


def _turn(world):
    return int(getattr(world, "current_turn", 0) or 0)


def push(world, petition):
    new = id(petition) not in TRACK
    status = _orig_push(world, petition)
    if new:     # the per-turn re-push hands the SAME object back (identity)
        TRACK[id(petition)] = {
            "obj": petition, "turn": _turn(world),
            "kind": str(petition.get("kind") or ""),
            "speaker": J._petition_speaker(petition),
            "tier": J.petition_tier(petition), "level": _level(petition),
            "status": status, "fate": None, "fate_turn": None, "opened": False,
        }
        ORDER.append(id(petition))
    return status


def _set(petition, fate, world, overwrite=True):
    rec = TRACK.get(id(petition))
    if rec is not None and (overwrite or rec["fate"] is None):
        rec["fate"], rec["fate_turn"] = fate, _turn(world)


def retire(world, petition, reason):
    clause = _orig_retire(world, petition, reason)
    _set(petition, f"retired:{reason}", world)
    return clause


def evict(world, petition):
    _orig_evict(world, petition)
    _set(petition, "evicted", world)


def withdraw(world, petition):
    _orig_withdraw(world, petition)
    _set(petition, "withdrawn", world, overwrite=False)


def answer(world, choice, executor=None, game_state=None):
    petition = getattr(world, "pending_marshal_petition", None)
    rec = TRACK.get(id(petition)) if petition is not None else None
    if rec is not None:
        rec["opened"] = True
    result = _orig_answer(world, choice, executor=executor, game_state=game_state)
    if (rec is not None and getattr(world, "pending_marshal_petition", None) is not petition
            and rec["fate"] in (None, "withdrawn")):
        rec["fate"], rec["fate_turn"] = f"answered:{choice}", _turn(world)
    return result


def cap(world, events, start):
    before = [(e.get("marshal"), e.get("target")) for e in events[start:]
              if isinstance(e, dict) and e.get("type") == "jealousy_fired"]
    _orig_cap(world, events, start)
    after = {(e.get("marshal"), e.get("target")) for e in events[start:]
             if isinstance(e, dict) and e.get("type") == "jealousy_fired"}
    for pair in before:
        FIRE_LINES.append((_turn(world), pair[0], pair[1],
                           "kept" if pair in after else "capped"))


def main() -> None:
    out_path = sys.argv[1]
    driver_args = sys.argv[sys.argv.index("--") + 1:]
    os.chdir(REPO)
    import tools.playtest_driver as D

    J._push_petition = push
    J.retire_petition = retire
    J._evict_audience = evict
    J._retire_pending_petition = withdraw
    J.handle_petition_response = answer    # main.py imports it at call time
    J._cap_routine_drama = cap

    sys.argv = ["playtest_driver.py", *driver_args]
    code = 0
    try:
        D.main()
    except SystemExit as exc:
        code = exc.code or 0

    import backend.main as M

    standing = getattr(M.world, "pending_marshal_petition", None)
    rows = []
    for key in ORDER:
        rec = TRACK[key]
        fate = rec["fate"]
        if fate is None and rec["obj"] is standing:
            fate = "standing"
        if fate is None and rec["status"] == J.PETITION_BLOCKED:
            fate = "blocked"
        rows.append({k: v for k, v in rec.items() if k != "obj"} | {"fate": fate})
    silent = [r for r in rows if r["status"] == J.PETITION_QUEUED and r["fate"] is None]
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump({"exit": code, "rows": rows, "silent": silent, "fire_lines": FIRE_LINES},
                  fh, indent=1)
    print("exit", code, "moments", len(rows), "silent", len(silent))


if __name__ == "__main__":
    main()
