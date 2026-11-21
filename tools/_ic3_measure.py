"""Row IC, Session 3 — "on his own": the measure (INDEPENDENT_COMMAND_SPEC.md §13).

The rules were written BEFORE any data (§13): R-ACTS, R-TOGETHER, R-FRIENDS,
R-VARIETY, R-TRUE. This tool plays the shipped 1805 campaign in-process (the
real `/command` road, the mock parser) with THREE BOLD AND TWO CAREFUL MEN ON
THEIR OWN — Ney, Lannes, Murat; Davout, Bernadotte — each given his own
proposal on turn 1 (the count raised to five by a measure-only seam,
`own_order.COUNT_AT_START`), and the player otherwise only ends the turn. Each
seed is a campaign seed (`WorldState.from_scenario(seed=…)`).

Per night it records, BEFORE the turn ends, each man's "Tonight" (the one pure
reading) and whether a bold man had an enemy France sees within two marches;
and AFTER, what each man did (the pass's own rows), every battle a French corps
was attacked in with a man on his own next to it, and whether that man rolled
to arrive (the reinforcement seam, wrapped).

    .venv/Scripts/python.exe tools/_ic3_measure.py [--seeds 30] [--turns 20]
        [--out tools/_ic3_variety_<stamp>.json]

Reported per seed and per man; a miss is said as a miss.
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

MEN = ("Ney", "Lannes", "Murat", "Davout", "Bernadotte")
BOLD = ("Ney", "Lannes", "Murat")
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
SEED_NAMES = ["historical", "austerlitz", "marengo"] + [f"ic3-{n:02d}" for n in range(1, 60)]
VISIBLE = {"attack", "strike", "storm", "besiege", "take", "march", "move_up", "join",
           "look", "probe", "dig_in", "fall_back"}
TOWARD = {"attack", "strike", "storm", "besiege", "take", "march", "move_up", "join", "probe"}


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def one_seed(seed: str, turns: int) -> dict:
    with _quiet():
        import backend.main as M
        from fastapi.testclient import TestClient

        from backend.commands import parse_preview as PP
        from backend.commands.combat_executor import CombatExecutor
        from backend.commands.parser import CommandParser
        from backend.game_logic import own_order as O
        from backend.models.world_state import WorldState
        world = WorldState.from_scenario(str(SCENARIO), seed=seed)
        M._set_active_world(world)
        M.parser = CommandParser(use_real_llm=False)
        PP.invalidate()
    O.COUNT_AT_START = len(MEN)
    rolls: list = []
    real = CombatExecutor._calculate_reinforcements

    def _wrapped(self, primary, defender, battle_region, nation, w, rng=None, attacked=False):
        out = real(self, primary, defender, battle_region, nation, w, rng=rng, attacked=attacked)
        try:
            if nation == w.player_nation and (attacked or getattr(self, "_reinforcing_the_attacked", False)):
                region = w.get_region(battle_region)
                near = set(getattr(region, "adjacent_regions", []) or [])
                rows = out if isinstance(out, list) else (out or {}).get("results", []) if isinstance(out, dict) else []
                tried = {str(r.get("marshal")) for r in rows if isinstance(r, dict)}
                for man in O.men(w):
                    if man.location in near and man.name != getattr(primary, "name", ""):
                        rolls.append({"turn": int(w.current_turn), "man": man.name,
                                      "friend": getattr(primary, "name", ""),
                                      "rolled": man.name in tried,
                                      "hates": int(man.get_relationship(getattr(primary, "name", ""))) <= -2})
        except Exception as exc:          # the measure never breaks the battle
            rolls.append({"error": str(exc)})
        return out

    CombatExecutor._calculate_reinforcements = _wrapped
    nights = []
    try:
        for name in MEN:
            m = world.marshals.get(name)
            if m is None:
                continue
            prop = O.proposal(world, m)
            spec, why = O.spec_from(world, m, prop["task"], prop["target"])
            if spec is not None:
                with _quiet():
                    O.give(world, m, spec, line=prop["line"], own_proposal=True)
        with TestClient(M.app) as client:
            for t in range(turns):
                if getattr(M.world, "game_over", False):
                    break
                w = M.world
                with _quiet():
                    plan = {r["marshal"]: r for r in O.tonight(w)}
                near_foe = {}
                from backend.commands import if_thens as IT
                for name in BOLD:
                    m = w.marshals.get(name)
                    if m is None or not O.on_his_own(m):
                        continue
                    near_foe[name] = any((O._distance(w, m.location, where) or 9) <= 2
                                         for _e, where in IT.seen_enemies(w, m))
                # men within one march of the same seen enemy (R-TOGETHER)
                shared = {}
                for m in O.men(w):
                    for enemy, where in IT.seen_enemies(w, m):
                        if (O._distance(w, m.location, where) or 9) <= 1:
                            shared.setdefault(enemy.name, set()).add(m.name)
                random.seed(f"{seed}:{t}")
                with _quiet():
                    out = client.post("/command", json={"command": "end turn"}).json()
                rows = [r for r in (out.get("strategic_reports") or []) if r.get("own")]
                nights.append({
                    "turn": t + 1,
                    "plan": {n: {"act": r["act"], "line": r["line"], "visible": r["visible"],
                                 "again": r.get("again", False), "with": r.get("with", ""),
                                 "target": r.get("target", "")} for n, r in plan.items()},
                    "did": [{"marshal": r["marshal"], "act": r.get("act"), "said": r.get("said", ""),
                             "message": r.get("message", ""), "target": r.get("target", ""),
                             "battle": bool(r.get("battle_report") or r.get("battle_message"))}
                            for r in rows],
                    "near_foe": near_foe,
                    "shared": {k: sorted(v) for k, v in shared.items() if len(v) >= 2},
                    "on_own": [m.name for m in O.men(M.world)],
                })
    finally:
        CombatExecutor._calculate_reinforcements = real
        O.COUNT_AT_START = 1
    return {"seed": seed, "nights": nights, "rolls": rolls}


def score(runs: list) -> dict:
    per_man = {n: {"nights": 0, "visible": 0, "stays": 0, "kinds": set(), "near": 0, "toward": 0}
               for n in MEN}
    true_bad, alike, alike_n, third, together_nights, together_named, double = [], 0, 0, 0, 0, 0, 0
    friends_battles, friends_rolled = 0, 0
    waits_three, third_acts = 0, []
    per_seed = []
    for run in runs:
        seed_row = {"seed": run["seed"], "nights": len(run["nights"])}
        hist = {n: [] for n in MEN}
        for night in run["nights"]:
            did = {r["marshal"]: r for r in night["did"]}
            plan = night["plan"]
            for name, r in did.items():
                if name not in per_man:
                    continue
                act = str(r.get("act") or "")
                if act == "start":
                    continue
                pm = per_man[name]
                pm["nights"] += 1
                pm["kinds"].add(act)
                again = bool((plan.get(name) or {}).get("again"))
                if act in VISIBLE and not again:
                    pm["visible"] += 1
                if act == "stay" or again:
                    pm["stays"] += 1
                if night["near_foe"].get(name):
                    pm["near"] += 1
                    if act in TOWARD:
                        pm["toward"] += 1
                said = plan.get(name, {})
                if act not in ("stay", "join") and said and r.get("said") and r["said"] != said.get("line"):
                    true_bad.append((run["seed"], night["turn"], name))
                place = r.get("target") or ""
                hist[name].append((act, place))
            acts = [str((did.get(n) or {}).get("act") or "") for n in MEN if n in did]
            acts = [a for a in acts if a and a != "start"]
            if len(acts) >= 3:
                alike_n += 1
                if len(set(acts)) == 1:
                    alike += 1
            for enemy, names in night["shared"].items():
                together_nights += 1
                hits = [n for n in names if (did.get(n) or {}).get("act") in ("attack", "strike")
                        and (did.get(n) or {}).get("target") == enemy]
                if len(hits) >= 2:
                    double += 1
                lines = " ".join(str((plan.get(n) or {}).get("line") or "") for n in names)
                if any(str(other) in lines for other in names) or any(
                        (plan.get(n) or {}).get("act") in ("join", "move_up") for n in names):
                    together_named += 1
        for name, seq in hist.items():
            for i in range(2, len(seq)):
                if seq[i] == seq[i - 1] == seq[i - 2] and seq[i][0] not in ("stay", "join", "attack", "march"):
                    # waiting for your word or recovering is not a choice of
                    # his — the third-night rule reads only what he chose
                    if seq[i][0] in ("asks", "recover"):
                        waits_three += 1
                        continue
                    third += 1
                    third_acts.append(seq[i][0])
        for roll in run["rolls"]:
            if roll.get("error") or roll.get("hates"):
                continue
            friends_battles += 1
            friends_rolled += 1 if roll.get("rolled") else 0
        seed_row["friends"] = {"battles": sum(1 for r in run["rolls"] if not r.get("error")),
                               "rolled": sum(1 for r in run["rolls"] if r.get("rolled"))}
        per_seed.append(seed_row)
    men_out = {}
    for name, pm in per_man.items():
        n = max(1, pm["nights"])
        men_out[name] = {"nights": pm["nights"], "visible_share": round(pm["visible"] / n, 3),
                         "stays_share": round(pm["stays"] / n, 3), "kinds": sorted(pm["kinds"]),
                         "near_foe_nights": pm["near"],
                         "toward_share": round(pm["toward"] / max(1, pm["near"]), 3) if pm["near"] else None}
    r_acts = all(m["visible_share"] >= 0.7 and m["stays_share"] < 0.3 for m in men_out.values()
                 if m["nights"]) and all((men_out[n]["toward_share"] or 1.0) >= 0.5 for n in BOLD)
    return {
        "R-ACTS": {"met": r_acts, "per_man": men_out},
        "R-VARIETY": {"alike_share": round(alike / max(1, alike_n), 3), "alike_nights": alike,
                      "nights_read": alike_n, "third_night_repeats": third,
                      "third_night_acts": sorted(third_acts),
                      "asks_or_recovers_three_nights": waits_three,
                      "every_man_two_kinds": all(len(m["kinds"]) >= 2 for m in men_out.values() if m["nights"]),
                      "met": alike / max(1, alike_n) < 0.40 and third == 0
                      and all(len(m["kinds"]) >= 2 for m in men_out.values() if m["nights"])},
        "R-TOGETHER": {"nights": together_nights, "double_attacks": double,
                       "named_share": round(together_named / max(1, together_nights), 3),
                       "met": double == 0 and (together_nights == 0 or together_named / together_nights >= 0.5)},
        "R-FRIENDS": {"battles_with_a_man_beside": friends_battles,
                      "he_rolled": friends_rolled,
                      "share": round(friends_rolled / max(1, friends_battles), 3)},
        "R-TRUE": {"mismatches": true_bad[:20], "count": len(true_bad), "met": not true_bad},
        "per_seed": per_seed,
    }


BAND = (23, 28)
BAND_ARMS = ("CMD-H", "CMD-A", "CMD-M")
STANDING = {"CMD-H": 26, "CMD-A": 27, "CMD-M": 28}     # _ic2b_after_2026_11_20.json
OWN_ARMS = {"TODAY": [], "N1": ["--own", "1"], "N2S": ["--own", "2", "--own-at-start", "2"],
            "LADDER": ["--own", "3"]}


def band(jobs: int, stamp: str) -> dict:
    """R-BAND (and R-INERT's arm TODAY): the France band on the commanded seeds
    with men on their own in use — as today (no one), one man, two at the
    start, and as many as the laws allow."""
    from concurrent.futures import ThreadPoolExecutor
    from tools import score_run as SR
    run_dir = ROOT / "tools" / "playtest_runs" / f"ic3_band_{stamp}"
    out = {"band": list(BAND), "standing": dict(STANDING), "arms": {}}

    def _one(arm, name):
        arms_dir = run_dir / arm
        arms_dir.mkdir(parents=True, exist_ok=True)
        argv = list(SR.ARMS[name]["argv"]) + OWN_ARMS[arm]
        result = SR._run_driver(ROOT, arms_dir, name, argv)
        rows = []
        digest = arms_dir / name / "digest.jsonl"
        if digest.is_file():
            rows = [json.loads(line) for line in digest.read_text(encoding="utf-8").splitlines()
                    if line.strip()]
        ledgers = [r for r in rows if r.get("kind") == "ledger"]
        own_lines = sum(1 for r in rows if r.get("kind") == "command"
                        and "on your own" in str(r.get("text") or ""))
        return arm, name, {"exit": result["exit"],
                           "provinces": int(ledgers[-1]["provinces"]) if ledgers else None,
                           "own_given": own_lines}

    with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        futs = [pool.submit(_one, arm, name) for arm in OWN_ARMS for name in BAND_ARMS]
        for f in futs:
            arm, name, row = f.result()
            out["arms"].setdefault(arm, {})[name] = row
            print(f"[ic3 band] {arm} {name}: {row}", flush=True)
    for arm, rows in out["arms"].items():
        out["arms"][arm]["_holds"] = all(
            (r.get("provinces") or 0) >= BAND[0] and (r.get("provinces") or 99) <= BAND[1]
            for k, r in rows.items() if not k.startswith("_"))
    today = out["arms"].get("TODAY", {})
    out["r_inert_band_is_standing"] = all(
        (today.get(n) or {}).get("provinces") == STANDING[n] for n in BAND_ARMS)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--turns", type=int, default=20)
    ap.add_argument("--out", default="")
    ap.add_argument("--band", action="store_true", help="the band arms instead of the sweep")
    ap.add_argument("--jobs", type=int, default=3)
    args = ap.parse_args(argv)
    if args.band:
        stamp = time.strftime("%Y_%m_%d")
        result = band(args.jobs, stamp)
        out = pathlib.Path(args.out) if args.out else ROOT / "tools" / f"_ic3_band_{stamp}.json"
        out.write_text(json.dumps(result, indent=1), encoding="utf-8")
        print(json.dumps(result, indent=1))
        return 0
    started = time.time()
    runs = []
    for seed in SEED_NAMES[:args.seeds]:
        t0 = time.time()
        runs.append(one_seed(seed, args.turns))
        print(f"seed {seed}: {len(runs[-1]['nights'])} nights, {time.time() - t0:.0f}s", flush=True)
    result = {"tool": "tools/_ic3_measure.py", "seeds": args.seeds, "turns": args.turns,
              "men": list(MEN), "score": score(runs), "seconds": round(time.time() - started)}
    out = pathlib.Path(args.out) if args.out else ROOT / "tools" / (
        "_ic3_variety_" + time.strftime("%Y_%m_%d") + ".json")
    out.write_text(json.dumps(result, indent=1, default=list), encoding="utf-8")
    print(json.dumps({k: v for k, v in result["score"].items() if k != "per_seed"}, indent=1, default=list))
    print("written", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
