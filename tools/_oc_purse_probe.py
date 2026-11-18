"""Row OC, OC-1 — the purse probe (November 18, 2026): the courts' purse on the
ambient board, per seed, for the slice's done-whens.

    * GRD-15  Prussia buys no law it never uses — every law each court
              enacts, with the uses its order-effects had before it (drills
              with room for morale, recruits by arm), and the laws enacted
              unused;
    * GRD-37  a doctrine-cure court reaches its Staff inside forty turns on
              some seed — each court's Staff and cure turns;
    * GRD-21  no court's chest ends a passive run under one turn of upkeep —
              every court's closing chest against `ledger.one_turn_of_upkeep`,
              its lowest chest and the turns it stood under a turn;
    * GRD-29  Britain's cure is never stranded by an edict — her authority
              and the Militia Transfer's turn.

Each seed runs in its own hash-pinned child on the ambient board (forty
turns, the M7 per-turn re-seed — the T8 probe's and the series' idiom), with
the seams the parent's `INK_IRON_SEAMS` holds (`tools/_seams_env.py`). The
uses are counted by wrapping `reforms.note_law_used`, which the shared
executor calls on every recruit and every drill with room for morale whether
or not the row's seam records them. Display only: no game number moves.

    .venv/Scripts/python.exe tools/_oc_purse_probe.py --out FILE [--seeds a,b] [--jobs 4]
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
SEEDS = ("historical", "ulm", "austerlitz", "jena", "marengo",
         "eylau", "friedland", "wagram", "lodi", "rivoli")
DOCTRINE_COURTS = ("Austria", "Prussia", "Russia", "Britain")
TURNS = 40

CHILD = r"""
import sys, random, contextlib, io, json, collections
sys.path.insert(0, {root!r})
from tools._seams_env import apply_from_env
apply_from_env()
import backend.game_logic.reforms as RF
from backend.game_logic import doctrines as DC, ledger as LG, standing as ST
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.game_logic.turn_manager import TurnManager
USES = collections.defaultdict(collections.Counter)
_real = RF.note_law_used
def _counting(world, nation, verb, arm=None, morale_applied=True):
    key = verb if verb != "recruit" else f"recruit:{{arm}}" + ("" if morale_applied else ":void")
    USES[nation][key] += 1
    return _real(world, nation, verb, arm, morale_applied)
RF.note_law_used = _counting
from backend.models.world_state import MAX_ARTILLERY_POOL, MAX_CAVALRY_POOL, MAX_INFANTRY_POOL
CAPS = {{"infantry": MAX_INFANTRY_POOL, "cavalry": MAX_CAVALRY_POOL, "artillery": MAX_ARTILLERY_POOL}}
ENACTED = collections.defaultdict(list)
def _demand(world, n, row, uses):
    # the game's own rule (reforms.law_is_used), read off the counted uses
    # at the moment of enactment — whatever the USED seam records
    staff = DC.staff_law(world, n)
    pools = (getattr(world, "manpower_pools", {{}}) or {{}}).get(n) or {{}}
    for c in row.get("effects") or []:
        if not isinstance(c, dict):
            continue
        t = str(c.get("type") or "")
        if t == "drill_morale":
            if uses.get("drill", 0) > 0:
                return True
        elif t in ("recruit_price", "recruit_morale"):
            arm = str(c.get("arm") or "all")
            for k, v in uses.items():
                parts = k.split(":")
                if parts[0] != "recruit" or v <= 0:
                    continue
                if arm not in ("all", parts[1]):
                    continue
                if t == "recruit_morale" and len(parts) > 2:
                    continue
                return True
        elif t == "manpower_regen":
            pool = str(c.get("pool") or "infantry")
            if int(pools.get(pool, 0) or 0) < CAPS.get(pool, MAX_INFANTRY_POOL):
                return True
        elif t == "cures":
            if staff is not None and RF.is_in_force(staff):
                return True
        else:
            return True
    return False
_real_enact = RF.enact_law
def _enacting(world, nation, row):
    if nation != getattr(world, "player_nation", None):
        uses = dict(USES[nation])
        ENACTED[nation].append({{"id": row.get("id"), "turn": int(getattr(world, "current_turn", 0) or 0),
                                "effects": [c.get("type") for c in (row.get("effects") or []) if isinstance(c, dict)],
                                "uses_before": uses, "used_before": bool(_demand(world, nation, row, uses))}})
    return _real_enact(world, nation, row)
RF.enact_law = _enacting
with contextlib.redirect_stdout(io.StringIO()):
    world = WorldState.from_scenario({scenario!r})
    executor = CommandExecutor()
    tm = TurnManager(world, executor=executor)
    game_state = {{"world": world, "executor": executor}}
player = world.player_nation
courts = sorted(n for n in RF.REFORM_DECKS if n != player and RF.deck(world, n))
rec = {{}}
def _row(n):
    return rec.setdefault(n, {{"laws": [], "staff_turn": None, "cure_turn": None,
                              "min_chest": None, "min_turn": None, "turns_under_keep": 0,
                              "authority": []}})
for turn in range({turns}):
    random.seed(10_000 + turn)
    with contextlib.redirect_stdout(io.StringIO()):
        tm.end_turn(game_state)
    now = int(world.current_turn)
    for n in sorted(set(world.get_active_nations()) - {{player}}):
        r = _row(n)
        chest = int(world.nation_gold.get(n, 0) or 0)
        keep = LG.one_turn_of_upkeep(world, n)
        if r["min_chest"] is None or chest < r["min_chest"]:
            r["min_chest"], r["min_turn"] = chest, now
        if chest < keep:
            r["turns_under_keep"] += 1
        r["chest_final"], r["keep_final"] = chest, keep
        r["at_war_final"] = sorted(world.get_nations_at_war_with(n))
        r["provinces_final"] = len(world.get_nation_regions(n))
        if n in {doctrine!r}:
            if now <= 6:
                r["authority"].append(int(ST.standing_of(world, n)))
            staff = DC.staff_law(world, n)
            if staff is not None and RF.is_in_force(staff) and r["staff_turn"] is None:
                r["staff_turn"] = int(staff.get("enacted_turn"))
            if DC.flaw_cured(world, n) and r["cure_turn"] is None:
                r["cure_turn"] = now
out = {{}}
for n, r in rec.items():
    r["laws"] = ENACTED.get(n, [])
    r["uses"] = dict(USES[n])
    r["unused_laws"] = [l["id"] for l in r["laws"] if not l["used_before"]]
    r["under_keep_final"] = r.get("chest_final", 0) < r.get("keep_final", 0)
    out[n] = r
print("PURSE=" + json.dumps(out, sort_keys=True))
"""


def run(seed: str) -> dict:
    env = dict(os.environ)
    env.update(PYTHONHASHSEED="0", PYTHONPATH=str(ROOT), SOVEREIGN_SEED=seed, LLM_MODE="mock")
    for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING", "PYTHONDONTWRITEBYTECODE"):
        env.pop(k, None)
    code = CHILD.format(root=str(ROOT), turns=TURNS, doctrine=DOCTRINE_COURTS,
                        scenario=str(ROOT / "godot-client" / "project-sovereign" / "assets"
                                     / "maps" / "europe_1805.json"))
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, timeout=3600)
    stdout = proc.stdout.decode("utf-8", errors="replace")
    if proc.returncode != 0:
        raise SystemExit(f"{seed} failed:\n{stdout[-1500:]}\n{proc.stderr.decode('utf-8', 'replace')[-3000:]}")
    line = [ln for ln in stdout.splitlines() if ln.startswith("PURSE=")][-1]
    return json.loads(line[len("PURSE="):])


# The courts whose Staff the S14j economy had put out of reach (GRD-28's own
# words: Prussia and Russia; GRD-37's T0-G probe: every rival but Britain held
# by the chest). Britain reached hers before row OC, so it proves nothing here.
STUCK_COURTS = ("Austria", "Prussia", "Russia")


def summarize(seeds: dict) -> dict:
    staff = {s: {n: r.get("staff_turn") for n, r in courts.items() if n in DOCTRINE_COURTS}
             for s, courts in seeds.items()}
    reached = sorted({(s, n) for s, c in staff.items() for n, t in c.items()
                      if t is not None and 0 < t <= TURNS})
    stuck = [x for x in reached if x[1] in STUCK_COURTS]
    unused = {s: {n: r.get("unused_laws", []) for n, r in c.items() if r.get("unused_laws")}
              for s, c in seeds.items()}
    prussia_unused = {s: c.get("Prussia", {}).get("unused_laws", []) for s, c in seeds.items()}
    under = {s: sorted(n for n, r in c.items() if r.get("under_keep_final")) for s, c in seeds.items()}
    dipped = {s: sorted(n for n, r in c.items() if int(r.get("turns_under_keep", 0) or 0) > 0)
              for s, c in seeds.items()}
    return {
        "staff_turns": staff,
        "doctrine_courts_reaching_their_staff": [list(x) for x in reached],
        "stuck_courts_reaching_their_staff": [list(x) for x in stuck],
        "grd37_met_as_written": bool(reached),
        "grd37_met_for_the_stuck_courts": bool(stuck),
        "unused_laws_by_court": unused,
        "prussia_unused_laws": prussia_unused,
        "grd15_met": not any(prussia_unused.values()),
        "courts_under_a_turn_at_the_close": under,
        "courts_ever_under_a_turn": dipped,
        "grd21_met": not any(under.values()),
        "britain_authority_t1_t6": {s: c.get("Britain", {}).get("authority") for s, c in seeds.items()},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", default=",".join(SEEDS))
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()
    seeds = [s for s in args.seeds.split(",") if s]
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        got = dict(zip(seeds, pool.map(run, seeds)))
    out = {"_note": ("Row OC, OC-1 — the purse probe (tools/_oc_purse_probe.py): forty ambient "
                     "turns per seed, per court the laws enacted with their prior uses, the "
                     "Staff and cure turns, the closing chest against one turn of upkeep, "
                     "the lowest chest, Britain's opening authority."),
           "turns": TURNS, "seams": os.environ.get("INK_IRON_SEAMS", ""),
           "seeds": got, "summary": summarize(got)}
    Path(args.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out["summary"], indent=1))
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
