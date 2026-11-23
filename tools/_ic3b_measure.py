"""Row IC, Session 3b — an army's task: the measure.

THE RULES, WRITTEN BEFORE ANY DATA (`docs/NEXT_SESSION_PROMPT.md`, "Row IC,
Session 3b — the plan, decided", November 21, 2026; made exact here before the
first run):

  R-INERT     with no army's task the France band on the three commanded seeds
              reads the standing 26 / 27 / 28 (the arm TODAY of `--band`).
  R-REPORT    (row IC, Session 4b — replaces Session 3b's R-TRUE: the user's
              "He moves at turn start" previews nothing) on 30 seeds x 20 turns
              with ONE army's task: what the report says each man of the army
              did is what happened — a march or a follow it claims ended where
              it says. Met: 0 false lines.
  R-TOGETHER  never two separate attacks: on no night does a follower open a
              battle of his own (a battle whose attacker is a follower); and the
              followers' "Tonight" lines name their commander on at least half
              of the nights they share with him. Met: 0 such battles, share >= 0.5.
  R-BAND      with an army's task (the driver's `--army-task`) the band on the
              three commanded seeds stays inside 23-28.

Reported besides (no bar): how often a follower moved, stood by, joined or
stayed put; how many nights the army had a task; how often the task was given
again after it ended.

The sweep plays the shipped 1805 campaign in-process (the real `/command`
road, the mock parser): the Army of the Rhine (Ney, Davout, Soult) is formed on
turn 1 and kept on its ready task (`army_task.proposal` — its commander's own
idea, or the war goal), given by the line with no `list_first` (the list's own
lines, carried out at once); the player otherwise only ends the turn.

    .venv/Scripts/python.exe tools/_ic3b_measure.py [--seeds 30] [--turns 20]
    .venv/Scripts/python.exe tools/_ic3b_measure.py --band [--jobs 4]
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import pathlib
import random
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
for _k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
    os.environ.pop(_k, None)
os.environ["LLM_MODE"] = "mock"

ARMY = "Army of the Rhine"
MEN = ("Ney", "Davout", "Soult")
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
SEED_NAMES = ["historical", "austerlitz", "marengo"] + [f"ic3b-{n:02d}" for n in range(1, 60)]
BAND = (23, 28)
BAND_ARMS = ("CMD-H", "CMD-A", "CMD-M")
STANDING = {"CMD-H": 26, "CMD-A": 27, "CMD-M": 28}
ARMS = {"TODAY": [], "ARMY": ["--army-task"]}


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def one_seed(seed: str, turns: int) -> dict:
    with _quiet():
        import backend.main as M
        from fastapi.testclient import TestClient

        from backend.commands import army_task as AT
        from backend.commands import parse_preview as PP
        from backend.commands.parser import CommandParser
        from backend.game_logic import armies
        from backend.game_logic import own_order as O
        from backend.models.world_state import WorldState
        world = WorldState.from_scenario(str(SCENARIO), seed=seed)
        M._set_active_world(world)
        M.parser = CommandParser(use_real_llm=False)
        PP.invalidate()
    nights, given = [], 0
    # THE TASK, by the seed's place in the list (set before the first full run,
    # so the army is made to march and to fight, not only to hold): a third of
    # the seeds take Swabia (Mack stands on it), a third chase Mack, a third
    # take the army's own ready task; a task the board refuses (Swabia ours
    # already, Mack out of sight) falls back to the ready task.
    wanted = ("take Swabia", "chase Mack", "")[SEED_NAMES.index(seed) % 3] if seed in SEED_NAMES else ""
    with TestClient(M.app) as client:
        def say(line: str) -> dict:
            with _quiet():
                return client.post("/command", json={"command": line}).json()

        say(f"form the {ARMY} with Ney, Davout and Soult")
        for t in range(turns):
            w = M.world
            if getattr(w, "game_over", False):
                break
            # keep the army on a task: its ready task when it has none, and the
            # same task again while a man of it does not follow yet
            for _try in range(2):
                held = AT.task_of(w, ARMY) if armies.find(w, ARMY) else {}
                have = int(w.actions_remaining or 0)
                if not armies.find(w, ARMY):
                    break
                if not held:
                    if have < 2 or O.count(w) >= O.allowed(w):
                        break
                    ready = str(AT.proposal(w, ARMY).get("line") or "")
                    reply = say(f"{ARMY}, {wanted}") if wanted else {}
                    if not reply.get("success"):
                        if not ready:
                            break
                        reply = say(ready)
                    given += 1 if reply.get("success") else 0
                    if not reply.get("success"):
                        break
                    continue
                lead = w.get_marshal(held["lead"])
                waiting = [n for n in armies.field_members(w, ARMY)
                           if n != held["lead"] and not O.on_his_own(w.get_marshal(n))
                           and AT.following(w, w.get_marshal(n)) is not lead]
                if not waiting or have < 1:
                    break
                if not say(f"{ARMY}, {held['words']}").get("success"):
                    break
            w = M.world
            held = AT.task_of(w, ARMY) if armies.find(w, ARMY) else {}
            # (row IC, Session 4b — "He moves at turn start": nothing is previewed;
            # the army moves as the next turn opens and the report says what it did)
            followers = [m.name for m in AT.followers(w, w.get_marshal(held["lead"]))] if held else []
            log_at = len(getattr(w, "event_log", None) or [])
            random.seed(f"{seed}:{t}")
            with _quiet():
                out = client.post("/command", json={"command": "end turn"}).json()
            rows = [r for r in (out.get("strategic_reports") or []) if r.get("own")]
            w = M.world
            opened = []
            for event in (getattr(w, "event_log", None) or [])[log_at:]:
                if isinstance(event, dict) and str(event.get("attacker") or "") in followers \
                        and "battle" in str(event.get("type") or ""):
                    opened.append({"type": event.get("type"), "attacker": event.get("attacker"),
                                   "turn": event.get("turn")})
            nights.append({
                "turn": t + 1, "lead": (held or {}).get("lead", ""), "task": (held or {}).get("words", ""),
                "followers": followers,
                "did": [{"marshal": r["marshal"], "act": str(r.get("act") or ""),
                         "place": str(r.get("place") or ""), "follows": str(r.get("follows") or ""),
                         "message": str(r.get("message") or ""), "action": str(r.get("action") or ""),
                         "after": str(getattr(w.get_marshal(r["marshal"]), "location", "") or "")}
                        for r in rows if r.get("act")],
                "follower_battles": opened,
            })
    return {"seed": seed, "nights": nights, "given": given}


def score(runs: list) -> dict:
    """Row IC, Session 4b: R-REPORT replaces R-TRUE (nothing is previewed —
    the user's "He moves at turn start"): what the report says each man of the
    army did is what happened; R-TOGETHER as written (no follower opens a
    battle; each follower's line names his commander)."""
    mismatches, lead_nights, follower_nights, named, shared = [], 0, 0, 0, 0
    acts = {"follow": 0, "with": 0, "stand_by": 0, "join": 0, "stay": 0, "start": 0, "halt": 0, "recover": 0}
    lead_acts: dict = {}
    battles = []
    task_nights, per_seed = 0, {}
    moves = {"march", "probe", "fall_back", "move_up", "follow"}
    for run in runs:
        bad_here = 0
        for night in run["nights"]:
            if night["lead"]:
                task_nights += 1
            battles.extend({"seed": run["seed"], **b} for b in night["follower_battles"])
            for row in night["did"]:
                name, act = row["marshal"], row["act"]
                if row["action"] in ("own_done", "own_ended"):
                    continue            # a row of the close (a task done), not of the move
                follower = bool(row["follows"])
                if follower:
                    follower_nights += 1
                    acts[act] = acts.get(act, 0) + 1
                    shared += 1
                    lead = row["follows"]
                    if lead in row["message"] or lead.replace("Massena", "Masséna") in row["message"]:
                        named += 1
                else:
                    lead_nights += 1
                    lead_acts[act] = lead_acts.get(act, 0) + 1
                if "could not" in row["message"]:
                    continue
                if act in moves and row["place"] and row["after"] and row["after"] != row["place"]:
                    bad_here += 1
                    mismatches.append({"seed": run["seed"], "turn": night["turn"], "marshal": name,
                                       "did": {"act": act, "place": row["place"], "after": row["after"],
                                               "message": row["message"][:160]}})
        per_seed[run["seed"]] = {"nights": len(run["nights"]), "given": run["given"],
                                 "mismatches": bad_here}
    share = (named / shared) if shared else 1.0
    return {
        "R-REPORT": {"false": mismatches[:20], "count": len(mismatches),
                     "turns_read": lead_nights + follower_nights, "met": not mismatches},
        "R-TOGETHER": {"follower_battles": battles[:20], "count": len(battles),
                       "shared_turns": shared, "named": named, "share": round(share, 3),
                       "met": not battles and share >= 0.5},
        "reported": {"task_nights": task_nights, "commander_nights": lead_nights,
                     "follower_nights": follower_nights, "commander_acts": lead_acts,
                     "follower_acts": acts},
        "per_seed": per_seed,
    }


def band(jobs: int, stamp: str) -> dict:
    """R-INERT (the arm TODAY) and R-BAND (the arm ARMY) on the commanded seeds."""
    from concurrent.futures import ThreadPoolExecutor
    from tools import score_run as SR
    run_dir = ROOT / "tools" / "playtest_runs" / f"ic3b_band_{stamp}"
    out = {"band": list(BAND), "standing": dict(STANDING), "arms": {}}

    def _one(arm, name):
        arms_dir = run_dir / arm
        arms_dir.mkdir(parents=True, exist_ok=True)
        argv = list(SR.ARMS[name]["argv"]) + ARMS[arm]
        result = SR._run_driver(ROOT, arms_dir, name, argv)
        rows = []
        digest = arms_dir / name / "digest.jsonl"
        if digest.is_file():
            rows = [json.loads(line) for line in digest.read_text(encoding="utf-8").splitlines()
                    if line.strip()]
        ledgers = [r for r in rows if r.get("kind") == "ledger"]
        army_lines = sum(1 for r in rows if r.get("kind") == "command"
                         and str(r.get("text") or "").startswith("Army of the Rhine,"))
        return arm, name, {"exit": result["exit"],
                           "provinces": int(ledgers[-1]["provinces"]) if ledgers else None,
                           "army_task_lines": army_lines}

    with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        futs = [pool.submit(_one, arm, name) for arm in ARMS for name in BAND_ARMS]
        for f in futs:
            arm, name, row = f.result()
            out["arms"].setdefault(arm, {})[name] = row
            print(f"[ic3b band] {arm} {name}: {row}", flush=True)
    for arm, rows in out["arms"].items():
        out["arms"][arm]["_holds"] = all(
            (r.get("provinces") or 0) >= BAND[0] and (r.get("provinces") or 99) <= BAND[1]
            for k, r in rows.items() if not k.startswith("_"))
    today = out["arms"].get("TODAY", {})
    out["R-INERT"] = {"met": all((today.get(n) or {}).get("provinces") == STANDING[n] for n in BAND_ARMS)}
    out["R-BAND"] = {"met": bool(out["arms"].get("ARMY", {}).get("_holds"))}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--turns", type=int, default=20)
    ap.add_argument("--out", default="")
    ap.add_argument("--band", action="store_true", help="the band arms instead of the sweep")
    ap.add_argument("--jobs", type=int, default=3)
    args = ap.parse_args(argv)
    stamp = time.strftime("%Y_%m_%d")
    if args.band:
        result = band(args.jobs, stamp)
        out = pathlib.Path(args.out) if args.out else ROOT / "tools" / f"_ic3b_band_{stamp}.json"
        out.write_text(json.dumps(result, indent=1), encoding="utf-8")
        print(json.dumps(result, indent=1))
        return 0
    started = time.time()
    runs = []
    for seed in SEED_NAMES[:args.seeds]:
        t0 = time.time()
        runs.append(one_seed(seed, args.turns))
        print(f"seed {seed}: {len(runs[-1]['nights'])} nights, {time.time() - t0:.0f}s", flush=True)
    result = {"tool": "tools/_ic3b_measure.py", "seeds": args.seeds, "turns": args.turns,
              "army": ARMY, "men": list(MEN), "score": score(runs),
              "seconds": round(time.time() - started)}
    out = pathlib.Path(args.out) if args.out else ROOT / "tools" / f"_ic3b_sweep_{stamp}.json"
    out.write_text(json.dumps(result, indent=1, default=list), encoding="utf-8")
    print(json.dumps({k: v for k, v in result["score"].items() if k != "per_seed"}, indent=1, default=list))
    print("written", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
