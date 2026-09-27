"""AAR32-D1 "The favorable line" — the measurement behind the ruling.

The muster's band word ("favorable" / "even" / "unfavorable") is a forecast
of what the resolver will do. This tool asks the resolver: over the REAL 1805
roster (every French marshal against every Austrian, Russian, British and
Prussian commander, authored skills, personalities and abilities), at a set
of target band ratios, how often does the attacker win, stalemate or lose?

It reads the band's own ratio (`objection_v2.inferred_attack_effective_ratio`
with `fold_modifiers=True`) and the ruling's weighing
(`objection_v2.generalship_factor` — the resolver's shock, defense and
expected-roll terms, relative to a 5/5/5 pairing), solves the attacker's
strength for each target against a 30,000 defender on open ground, and
resolves N seeded battles through `CombatResolver.resolve_battle`.

    .venv/Scripts/python.exe tools/_aar32_the_favorable_line.py [--battles 200]

Writes tools/_aar32_the_favorable_line.json (committed with the ruling).
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import io
import json
import os
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(str(ROOT))
os.environ.setdefault("LLM_MODE", "mock")

with contextlib.redirect_stdout(io.StringIO()):
    from backend.models.world_state import WorldState
    from backend.game_logic.combat import CombatResolver
    from backend.commands.objection_v2 import (
        inferred_attack_effective_ratio, generalship_factor)

SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
DEFENDER_STRENGTH = 30000
TARGETS = [0.8, 1.0, 1.2, 1.4, 1.5, 1.6, 1.7, 1.8, 2.0]


def fresh(m, strength):
    c = copy.deepcopy(m)
    c.strength = int(strength)
    c.morale = 100
    c.fortified = False
    c.defense_bonus = 0.0
    c.location = "TestField"
    return c


def folded(a, d):
    return inferred_attack_effective_ratio(a, d, None, fold_modifiers=True)


def solve(am, dm, target, weighed):
    lo, hi = 500.0, 400000.0
    for _ in range(50):
        mid = (lo + hi) / 2
        a, d = fresh(am, mid), fresh(dm, DEFENDER_STRENGTH)
        value = folded(a, d) * (generalship_factor(a, d) if weighed else 1.0)
        if value < target:
            lo = mid
        else:
            hi = mid
    return int(hi)


def outcomes(am, dm, strength, battles):
    w = st = lo = 0
    for seed in range(battles):
        random.seed(seed)
        a, d = fresh(am, strength), fresh(dm, DEFENDER_STRENGTH)
        o = CombatResolver().resolve_battle(a, d, terrain="plains")["outcome"]
        if o in ("attacker_victory", "attacker_tactical_victory"):
            w += 1
        elif o in ("defender_victory", "defender_tactical_victory", "mutual_destruction"):
            lo += 1
        else:
            st += 1
    return 100.0 * w / battles, 100.0 * st / battles, 100.0 * lo / battles


def table(french, enemies, weighed, battles):
    out = {}
    for t in TARGETS:
        rows = []
        for am in french:
            for dm in enemies:
                rows.append(outcomes(am, dm, solve(am, dm, t, weighed), battles))
        wins = [r[0] for r in rows]
        out[str(t)] = {
            "win_mean": round(statistics.mean(wins), 1),
            "win_min": round(min(wins), 1), "win_max": round(max(wins), 1),
            "stalemate_mean": round(statistics.mean(r[1] for r in rows), 1),
            "loss_mean": round(statistics.mean(r[2] for r in rows), 1),
            "pairings": len(rows)}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--battles", type=int, default=200)
    ap.add_argument("--out", default=str(ROOT / "tools" / "_aar32_the_favorable_line.json"))
    args = ap.parse_args()
    with contextlib.redirect_stdout(io.StringIO()):
        world = WorldState.from_scenario(str(SCENARIO))
        french = [m for m in world.marshals.values()
                  if m.nation == "France" and not getattr(m, "is_sovereign", False)]
        enemies = [m for m in world.marshals.values()
                   if m.nation in ("Austria", "Russia", "Britain", "Prussia")]
        by_fold = table(french, enemies, False, args.battles)
        by_weight = table(french, enemies, True, args.battles)
    for label, tab in (("the band's folded ratio", by_fold),
                       ("the folded ratio weighed by generalship", by_weight)):
        print(f"== {label}")
        for t, row in tab.items():
            print(f"  {t:>4}: win {row['win_mean']:5.1f}% ({row['win_min']:.0f}..{row['win_max']:.0f})"
                  f"  stalemate {row['stalemate_mean']:5.1f}%  loss {row['loss_mean']:5.1f}%")
    Path(args.out).write_text(json.dumps(
        {"battles_per_pairing": args.battles, "defender_strength": DEFENDER_STRENGTH,
         "by_folded_ratio": by_fold, "by_weighed_ratio": by_weight}, indent=1),
        encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
