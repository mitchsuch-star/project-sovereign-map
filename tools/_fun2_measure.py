"""Row FUN, Session FUN-2 — "conquest with a cost" — the measure (November 26,
2026; `docs/GAMEPLAY_REVIEW_2026_11_25.md` §5; `docs/NEXT_SESSION_PROMPT.md`'s
FUN-2 block).

THE RULE, WRITTEN BEFORE THE DATA (the brief's own words, kept here verbatim
before any run):
    (a) a France that erases Austria by turn 20 meets a league on every seed,
        and no member lacks a border or a stake;
    (b) a France that takes only its war aim meets no league by turn 30 on at
        least 7 of 10 seeds.
Read here as:
    (a) on each of the ten ambient seeds, France takes Austria's seven provinces
        through the capture chokepoint (`WorldState.capture_region`), one a turn
        from turn 4 — its seven boot provinces, then whatever else it holds, the
        capital last — a garrison left in each so none rises, its field armies
        beaten on turn 3 first (an Austerlitz: unbeaten, the corps in each
        province retake it the next morning); the rest of Europe
        is played by the computer (the ambient sweep's loop, `ai_v_sweep.run_one`'s
        idiom). PASS on a seed when a league stands against France at some turn
        from the erasure to turn 30, AND every court that entered a league
        against France from turn 4 on (a new league's members, or a court
        joining one that stands) borders France's house or holds a stake at
        that moment. Reported beside it, never gated: whether the league is NEW
        or a court JOINED it by fear (the boot Third Coalition may still stand).
    (b) France takes only its war aim — the boot war's aim the war council
        reads for France beyond its own soil is the enemy capitals (Vienna,
        London, Vilna); the one in reach, Vienna, is taken on turn 6 and held
        with a garrison. PASS on a seed when no league forms against France
        after turn 1 and no court joins one by fear through turn 30. Bar: 7 of 10.
    A missed bar is reported as missed, never moved.

    .venv/Scripts/python.exe tools/_fun2_measure.py [--arms erase,aim] [--seeds ...]
                                                    [--turns 30] [--jobs 4] [--out F]
    .venv/Scripts/python.exe tools/_fun2_measure.py --child --seed S --arm erase --turns 30

Writes tools/_fun2_measure_2026_11_26.json by default.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
AMBIENT_K = 10_000
AUSTRIA = ["Bohemia", "Carniola", "Moravia", "Hungary", "Croatia", "Tyrol", "Vienna"]
ERASE_FROM = 4
AIM_TURN = 6
AIM_PROVINCE = "Vienna"
GARRISON = 3000
SEEDS = ["historical", "ulm", "austerlitz", "jena", "marengo",
         "eylau", "friedland", "wagram", "lodi", "rivoli"]


def _hold(world, name: str) -> None:
    region = world.regions[name]
    region.garrison_strength = GARRISON
    region.garrison_detachment = True


def _script(world, arm: str) -> list:
    """France's scripted captures for this turn (by `world.current_turn`)."""
    turn = int(world.current_turn)
    done = []
    if arm in ("erase", "erase_bare") and turn == ERASE_FROM - 1:
        # An Austerlitz: Austria's field armies are beaten before its land is
        # taken — without it the corps standing in each province simply retake it
        # the next morning (the first two runs, kept in the record's notes).
        for m in [m for m in world.marshals.values() if m.nation == "Austria"]:
            world.destroy_marshal(m, "destroyed", victor="France")
            done.append(f"{m.name} beaten")
    if arm in ("erase", "erase_bare"):
        # Austria's boot provinces first, in order, then whatever else it holds by
        # then (the computer's Austria takes land too) — one a turn from turn 4
        # until it holds none, by turn 20 at the latest; the capital comes last.
        if ERASE_FROM <= turn <= 20:
            held = list(world.get_nation_regions("Austria"))
            order = [n for n in AUSTRIA if n in held] + sorted(n for n in held if n not in AUSTRIA)
            capital = [n for n in order if getattr(world.regions[n], "is_capital", False)]
            order = [n for n in order if n not in capital] + capital
            if order:
                name = order[0]
                world.capture_region(name, "France")
                done.append(name)
                if arm == "erase":
                    _hold(world, name)
    elif arm == "aim" and turn == AIM_TURN:
        if world.regions[AIM_PROVINCE].controller != "France":
            world.capture_region(AIM_PROVINCE, "France")
            done.append(AIM_PROVINCE)
        _hold(world, AIM_PROVINCE)
    return done


def child(seed: str, arm: str, turns: int) -> dict:
    os.environ["SOVEREIGN_SEED"] = seed
    os.environ["LLM_MODE"] = "mock"
    os.environ.pop("SOVEREIGN_SCENARIO", None)
    os.environ.pop("SOVEREIGN_MAP", None)
    sys.path.insert(0, str(ROOT))
    import contextlib
    import io
    import random

    from backend.commands.executor import CommandExecutor
    from backend.game_logic import fear as F
    from backend.game_logic.turn_manager import TurnManager
    from backend.models.world_state import WorldState

    with contextlib.redirect_stdout(io.StringIO()):
        world = WorldState.from_scenario(str(SCENARIO))
        executor = CommandExecutor()
        tm = TurnManager(world, executor=executor)
    game_state = {"world": world, "executor": executor}
    boot_league = dict(world.active_coalition or {})
    boot_id = boot_league.get("id")
    last_members = set(boot_league.get("members") or [])
    last_id = boot_id
    rows = []
    erased_turn = None
    for i in range(turns):
        played = int(world.current_turn)          # the turn this loop plays (1-based)
        taken = _script(world, arm)
        if arm.startswith("erase") and erased_turn is None and not world.get_nation_regions("Austria"):
            erased_turn = played
        random.seed(AMBIENT_K + i)
        with contextlib.redirect_stdout(io.StringIO()):
            tm.end_turn(game_state)
        league = world.active_coalition
        lid = (league or {}).get("id")
        members = set((league or {}).get("members") or []) if league and (
            (league.get("target_nation") or world.player_nation) == world.player_nation) else set()
        entered = sorted(members - last_members) if lid == last_id else sorted(members)
        # a NEW league against France (an eclipse league's members read as none)
        new_league = bool(league and members and lid != boot_id and lid != last_id)
        checks = {c: bool(F.border_or_stake(world, c)) for c in entered}
        fears = {c: int(F.fear_of(world, c)) for c in entered}
        rows.append({
            "turn": played, "taken": taken, "entered_fear": fears,
            "austria": sorted(world.get_nation_regions("Austria")),
            "league": ({"id": lid, "name": league.get("name"), "members": sorted(members),
                        "by_fear": sorted(league.get("by_fear") or [])} if members else None),
            "new_league": new_league, "entered": entered, "border_or_stake": checks,
            "threat": int(world.threat_level),
            "fear": {c: int(v) for c, v in sorted((world.court_grudges or {}).items(),
                                                   key=lambda kv: -kv[1])[:8]},
        })
        last_members, last_id = members, lid
    return {"seed": seed, "arm": arm, "turns": rows, "erased_turn": erased_turn,
            "austria_alive_at_end": bool(world.get_nation_regions("Austria")),
            "france_provinces": len(world.get_nation_regions("France"))}


def verdict(run: dict) -> dict:
    rows = run["turns"]
    arm = run["arm"]
    if arm.startswith("erase"):
        window = [r for r in rows if ERASE_FROM <= r["turn"] <= 30]
        stands = any(r["league"] for r in window if r["turn"] >= (run.get("erased_turn") or 99))
        entered = [(r["turn"], c, ok) for r in window for c, ok in r["border_or_stake"].items()]
        lacking = [(t, c) for t, c, ok in entered if not ok]
        # the stricter reading, REPORTED (never gated): some court entered a league
        # against France past the line of fear (not the boot league standing alone)
        by_fear = [(r["turn"], c) for r in window for c, f in (r.get("entered_fear") or {}).items()
                   if f > 50]
        return {"pass": bool(stands and not lacking and run.get("erased_turn")),
                "league_stands": stands, "lacking": lacking,
                "strict_pass": bool(stands and not lacking and by_fear and run.get("erased_turn")),
                "entered_by_fear": by_fear, "erased_turn": run.get("erased_turn")}
    new = [r["turn"] for r in rows if r["turn"] <= 30 and (r["new_league"] or r["entered"])]
    return {"pass": not new, "new_league_or_join_turns": new}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--child", action="store_true")
    ap.add_argument("--seed", default="historical")
    ap.add_argument("--arm", default="erase")
    ap.add_argument("--arms", default="erase,aim")
    ap.add_argument("--seeds", default=",".join(SEEDS))
    ap.add_argument("--turns", type=int, default=30)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out", default=str(ROOT / "tools" / "_fun2_measure_2026_11_26.json"))
    args = ap.parse_args()
    if args.child:
        if os.environ.get("PYTHONHASHSEED") != "0":
            raise SystemExit("PYTHONHASHSEED must be 0 (spawn me as a subprocess)")
        print("PAYLOAD=" + json.dumps(child(args.seed, args.arm, args.turns)))
        return 0
    seeds = [s for s in args.seeds.split(",") if s]
    arms = [a for a in args.arms.split(",") if a]
    jobs = [(s, a) for a in arms for s in seeds]

    def spawn(job):
        seed, arm = job
        env = dict(os.environ)
        env.update(PYTHONHASHSEED="0", PYTHONPATH=str(ROOT), SOVEREIGN_SEED=seed, LLM_MODE="mock")
        for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING", "INK_IRON_SEAMS"):
            env.pop(k, None)
        proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--child",
                               "--seed", seed, "--arm", arm, "--turns", str(args.turns)],
                              env=env, cwd=str(ROOT), capture_output=True, timeout=3600)
        out = proc.stdout.decode("utf-8", errors="replace")
        if proc.returncode != 0:
            return {"seed": seed, "arm": arm, "error": proc.stderr.decode("utf-8", errors="replace")[-3000:]}
        return json.loads([ln for ln in out.splitlines() if ln.startswith("PAYLOAD=")][-1][8:])

    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        runs = list(pool.map(spawn, jobs))
    record = {"rule": __doc__.split("THE RULE, WRITTEN BEFORE THE DATA")[1].split("    .venv")[0].strip(),
              "turns": args.turns, "runs": {}, "verdicts": {}}
    for run in runs:
        key = f"{run['arm']}:{run['seed']}"
        if "error" in run:
            record["runs"][key] = run
            print(key, "ERROR", run["error"][-400:])
            continue
        record["runs"][key] = run
        record["verdicts"][key] = verdict(run)
        print(f"{key:>22}: {record['verdicts'][key]}")
    for arm in arms:
        passed = sum(1 for s in seeds if record["verdicts"].get(f"{arm}:{s}", {}).get("pass"))
        strict = sum(1 for s in seeds if record["verdicts"].get(f"{arm}:{s}", {}).get("strict_pass"))
        record.setdefault("summary", {})[arm] = {"passed": passed, "of": len(seeds),
                                                 **({"strict_passed": strict} if arm.startswith("erase") else {})}
        print(f"ARM {arm}: {passed} of {len(seeds)} seeds pass"
              + (f" (the stricter reading: {strict})" if arm.startswith("erase") else ""))
    Path(args.out).write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
