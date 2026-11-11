"""Session G4 — the BASELINE_SERIES attribution for the ten session-G4
seams (DYNAMISM_SPEC.md §7d; November 11, 2026), an arm per seam raised in
the sweep's order, each rule's reach COUNTED in the child (an arm whose seam
never bites cannot pass for a byte-identical one). The prior is HEAD's
`BASELINE_SERIES` (never the working tree's), the S14k rig's rule.

Arms: `0` — the ten seams down, the tree session G3 left (must reproduce
the prior byte for byte); then FORM / WON / LAPSE / REAR / CEILING / ALLY /
GUNS / WAGON / HOUSE, each adding its seam; `ALL` — + KING, the shipped tree (the
re-pin's value, if the series moves).

    .venv/Scripts/python.exe tools/_g4_series_arms.py [--arms 0,FORM,…,ALL] [--jobs 3]

Writes tools/_g4_series_arms_final.json (committed with the landing record;
a re-run writes its OWN record via --out).
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tests" / "test_ai_intent_threat_migration.py"
ORDER = ("FORM", "WON", "LAPSE", "REAR", "CEILING", "ALLY", "GUNS", "WAGON", "HOUSE", "KING")
ARMS = {"0": set(ORDER)}
for _i, _name in enumerate(ORDER[:-1], start=1):
    ARMS[_name] = set(ORDER[_i:])
ARMS["ALL"] = set()

CHILD = r"""
import sys, runpy, atexit, collections
DOWN = set({down!r})
_c = collections.Counter()
_beats = []
from backend.game_logic import formations as FM
from backend.game_logic import agendas as AG
from backend.game_logic import vassal as VS
from backend.game_logic import war_council as WC
from backend.game_logic import recruitment as RC
from backend.game_logic import settlement_third_party as TP
from backend.commands import combat_executor as CE
from backend.game_logic import crowns as CR
def _counted(module, name, key):
    seam = getattr(module, name)
    def _wrapped():
        _c[key.lower() + "_seam_reads"] += 1
        return False if key in DOWN else seam()
    setattr(module, name, _wrapped)
_counted(FM, "a_nation_is_proclaimed_on_what_it_holds", "FORM")
_counted(AG, "an_allys_soil_is_not_won", "WON")
_counted(VS, "a_pact_lapses_at_the_vassalage", "LAPSE")
_counted(WC, "a_backer_is_no_menace", "REAR")
_counted(RC, "a_commission_reads_the_arming_ceiling", "CEILING")
_counted(TP, "the_emperors_ally_takes_no_separate_peace", "ALLY")
_counted(CE, "no_guns_from_a_sanctuary", "GUNS")
_counted(WC, "a_bandwagoner_joins_a_neighbours_war", "WAGON")
_counted(CR, "the_people_drive_out_a_foreign_king", "KING")
from backend.game_logic import diplomacy as DI
_counted(DI, "a_client_joins_no_war_against_a_house_at_peace", "HOUSE")
_keeps = DI.client_keeps_its_peace_with_the_house
def client_keeps_its_peace_with_the_house(world, joiner, aggressor):
    out = _keeps(world, joiner, aggressor)
    if out:
        _bite("house_bites", world, joiner, aggressor)
    return out
DI.client_keeps_its_peace_with_the_house = client_keeps_its_peace_with_the_house
def _turn(world):
    return int(getattr(world, "current_turn", 0) or 0)
def _bite(key, world, *what):
    _c[key] += 1
    if len(_beats) < 80:
        _beats.append([_turn(world), key] + [str(w) for w in what])
_backers = WC.backers_of
def backers_of(world, nation):
    out = _backers(world, nation)
    if out:
        _bite("rear_bites", world, nation, sorted(out))
    return out
WC.backers_of = backers_of
_over = RC.commission_over_the_ceiling
def commission_over_the_ceiling(world, nation, candidate):
    out = _over(world, nation, candidate)
    if out:
        _bite("ceiling_bites", world, nation, candidate.get("name"))
    return out
RC.commission_over_the_ceiling = commission_over_the_ceiling
_stands = TP.ally_stands_by_the_emperor
def ally_stands_by_the_emperor(world, winner, loser):
    out = _stands(world, winner, loser)
    if out:
        _bite("ally_bites", world, winner, loser)
    return out
TP.ally_stands_by_the_emperor = ally_stands_by_the_emperor
_sanct = CE.fires_from_a_sanctuary
def fires_from_a_sanctuary(world, marshal, target_nation):
    out = _sanct(world, marshal, target_nation)
    if out:
        _bite("guns_bites", world, getattr(marshal, "name", ""), out, target_nation)
    return out
CE.fires_from_a_sanctuary = fires_from_a_sanctuary
_reach = WC.bandwagon_in_reach
def bandwagon_in_reach(world, nation, enemy):
    out = _reach(world, nation, enemy)
    if not out:
        _bite("wagon_bites", world, nation, enemy)
    return out
WC.bandwagon_in_reach = bandwagon_in_reach
_decision = VS._vassalage_entry_decision
def _vassalage_entry_decision(world, lord, vassal, other, **k):
    out = _decision(world, lord, vassal, other, **k)
    if out and out[0] == "pact":
        _bite("lapse_bites", world, lord, vassal, other)
    return out
VS._vassalage_entry_decision = _vassalage_entry_decision
_fate = CR.king_at_the_rebellion
def king_at_the_rebellion(world, tag, lord, cause):
    out = _fate(world, tag, lord, cause)
    if out:
        _bite("king_bites", world, tag, lord)
    return out
CR.king_at_the_rebellion = king_at_the_rebellion
_due = FM.proclamation_due
def proclamation_due(world, nation, entry, forms):
    out = _due(world, nation, entry, forms)
    if out:
        _bite("form_proclaims", world, nation, entry.get("id"))
    return out
FM.proclamation_due = proclamation_due
_KEYS = sorted(["%s_seam_reads" % k.lower() for k in {order!r}]
               + ["rear_bites", "ceiling_bites", "ally_bites", "guns_bites", "wagon_bites",
                  "lapse_bites", "king_bites", "form_proclaims", "house_bites"])
def _dump():
    print("REACH=" + repr({{"counts": {{k: int(_c.get(k, 0)) for k in _KEYS}},
                           "beats": _beats}}))
atexit.register(_dump)
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""


def run_arm(down: set) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING",
              "PYTHONDONTWRITEBYTECODE", "INK_IRON_SEAMS"):
        env.pop(k, None)
    code = CHILD.format(down=sorted(down), runner=str(RUNNER), order=list(ORDER))
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, timeout=3600)
    stdout = proc.stdout.decode("utf-8", errors="replace")
    stderr = proc.stderr.decode("utf-8", errors="replace")
    if proc.returncode != 0:
        raise SystemExit(f"arm failed:\n{stdout[-2000:]}\n{stderr[-3000:]}")
    lines = stdout.splitlines()
    payload = json.loads([ln for ln in lines if ln.startswith("PAYLOAD=")][-1][len("PAYLOAD="):])
    counts = [ln for ln in lines if ln.startswith("REACH=")]
    payload["reach"] = ast.literal_eval(counts[-1].split("=", 1)[1]) if counts else None
    return payload


def first_divergence(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return None if len(a) == len(b) else min(len(a), len(b))


def prior_series() -> list:
    """HEAD's `BASELINE_SERIES` — the series before this session, never the
    working tree's (the S14k rig's rule)."""
    rel = RUNNER.relative_to(ROOT).as_posix()
    text = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=str(ROOT),
                          capture_output=True, check=True).stdout.decode("utf-8")
    m = re.search(r"^BASELINE_SERIES = (\[[^\]]*\])", text, re.M)
    return json.loads(m.group(1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--out", default=str(ROOT / "tools" / "_g4_series_arms_final.json"))
    args = ap.parse_args()
    prior = prior_series()
    names = [x.strip() for x in args.arms.split(",") if x.strip()]
    out = {"prior": prior, "seams_down": {k: sorted(ARMS[k]) for k in names},
           "arms": {}}
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = dict(zip(names, pool.map(lambda a: run_arm(ARMS[a]), names)))
    for arm in names:
        payload = results[arm]
        series = payload["series"]
        out["arms"][arm] = {"down": sorted(ARMS[arm]), "series": series,
                            "first_divergence_vs_prior": first_divergence(series, prior),
                            "reach": payload.get("reach")}
        print(f"arm {arm:>10}: divergence vs prior {out['arms'][arm]['first_divergence_vs_prior']}"
              f"  reach {(payload.get('reach') or {}).get('counts')}", flush=True)
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
