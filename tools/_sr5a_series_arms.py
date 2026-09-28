"""SR-5a "The chest" (Score Mandate Chunk 5, RULED by the user September 28,
2026) — the BASELINE_SERIES attribution, in the tools/_drill_fix_series_arms.py
pattern: each arm run on the recorded ambient board in a child process, the
scenario swapped in the child (the shipped file is never written) and every
slice lever set in the child.

    .venv/Scripts/python.exe tools/_sr5a_series_arms.py [--arms all|0,1,...]

Scenario arms (the ruled balance package lives in europe_1805.json):
    0    the PRE-SLICE scenario (git HEAD~ content, i.e. the file before the
         package) and every slice lever DOWN — must reproduce the recorded
         series byte for byte
    L    the pre-slice scenario, every slice lever UP (AAR-6's admin pool,
         the substitutes' named ground, the ledger's why-notes, IQ1-5-1's
         honest forecast — which the AI's purse test reads — and the card's
         tomorrow's standing) — the levers alone
    B    Britain's half of the package alone (London/East Anglia/Midlands/
         Northumbria/Scotland incomes, trade dominance 450, overseas 1,000)
    F    France's half alone (every homeland province at 75%)
    1    the shipped scenario (both halves), every lever up — the new series

Writes tools/_sr5a_series_arms.json.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tests" / "test_ai_intent_threat_migration.py"
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
SCEN_REL = "godot-client/project-sovereign/assets/maps/europe_1805.json"

BRITAIN_INCOME = {"London": 500, "East Anglia": 300, "Midlands": 300,
                  "Northumbria": 150, "Scotland": 150}
BRITAIN_NAVY = {"trade_dominance": 450, "overseas_income": 1000}

CHILD = r"""
import json, sys, runpy
import backend.commands.executor as EX
import backend.commands.economy_executor as EE
import backend.game_logic.ledger as LG
import backend.game_logic.vassal as VS
import backend.models.world_state as WSM
from backend.models.world_state import WorldState
up = {up!r}
EX.AN_ADMIN_ORDER_ASKS_ONLY_THE_ADMIN_POOL = up
EE.THE_NAMED_GROUND_RECEIVES_THE_SUBSTITUTES = up
LG.THE_BILLS_SAY_WHY_THEY_MOVED = up
WSM.THE_FORECAST_PRICES_TOMORROWS_WAR = up
VS.THE_CARD_READS_TOMORROWS_STANDING = up
_scen = {scen!r}
_orig = WorldState.from_scenario.__func__
def _swap(cls, path, seed=None):
    if str(path).replace("\\", "/").endswith("europe_1805.json"):
        path = _scen
    return _orig(cls, path, seed=seed)
WorldState.from_scenario = classmethod(_swap)
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""


def prior_scenario_text() -> str:
    """The scenario as it stood before this slice (the committed parent)."""
    out = subprocess.run(["git", "show", f"HEAD:{SCEN_REL}"], cwd=str(ROOT),
                         capture_output=True, text=True, encoding="utf-8")
    if out.returncode != 0:
        raise SystemExit(out.stderr)
    data = json.loads(out.stdout)
    if "_economy_balance_comment" in data:
        # Run after the slice landed: the parent is one commit further back.
        out = subprocess.run(["git", "show", f"HEAD~1:{SCEN_REL}"], cwd=str(ROOT),
                             capture_output=True, text=True, encoding="utf-8")
    return out.stdout


def write_variant(name: str, britain: bool, france: bool) -> str:
    base = json.loads(prior_scenario_text())
    shipped = json.loads(SCENARIO.read_text(encoding="utf-8"))
    overrides = base.setdefault("region_overrides", {})
    for prov, fields in (shipped.get("region_overrides") or {}).items():
        inc = fields.get("income_value")
        if inc is None:
            continue
        is_britain = prov in BRITAIN_INCOME
        if (is_britain and britain) or (not is_britain and france):
            overrides.setdefault(prov, {})["income_value"] = inc
    if britain:
        base["navies"]["Britain"].update(BRITAIN_NAVY)
    path = Path(tempfile.gettempdir()) / f"sr5a_arm_{name}.json"
    path.write_text(json.dumps(base), encoding="utf-8")
    return str(path)


def run_arm(scen: str, up: bool) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING"):
        env.pop(key, None)
    code = CHILD.format(runner=str(RUNNER), up=up, scen=scen)
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=3600)
    if proc.returncode != 0:
        raise SystemExit(f"arm failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}")
    lines = proc.stdout.splitlines()
    return json.loads([ln for ln in lines if ln.startswith("PAYLOAD=")][-1][len("PAYLOAD="):])


def _series_in(src: str) -> list:
    start = src.index("BASELINE_SERIES = [")
    end = src.index("]", start)
    return list(ast.literal_eval(src[start + len("BASELINE_SERIES = "):end + 1]))


def recorded_series() -> list:
    """The series recorded BEFORE this slice — read from git, never the
    working copy (which carries SR-5a's own re-record once it is written)."""
    rel = "tests/test_ai_intent_threat_migration.py"
    for rev in ("HEAD", "HEAD~1"):
        out = subprocess.run(["git", "show", f"{rev}:{rel}"], cwd=str(ROOT),
                             capture_output=True, text=True, encoding="utf-8")
        if out.returncode != 0:
            raise SystemExit(out.stderr)
        if 'SR-5a "The chest"' not in out.stdout:
            return _series_in(out.stdout)
    raise SystemExit("no pre-slice BASELINE_SERIES found in HEAD or HEAD~1")


def shipped_series() -> list:
    return _series_in(RUNNER.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="all")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_sr5a_series_arms.json"))
    args = ap.parse_args()
    specs = {
        "0": (write_variant("0", False, False), False),
        "L": (write_variant("L", False, False), True),
        "B": (write_variant("B", True, False), True),
        "F": (write_variant("F", False, True), True),
        "1": (str(SCENARIO), True),
    }
    wanted = list(specs) if args.arms == "all" else args.arms.split(",")
    prior = recorded_series()
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {arm: pool.submit(run_arm, *specs[arm]) for arm in wanted}
        results = {arm: fut.result() for arm, fut in futures.items()}
    shipped = shipped_series()
    for arm in wanted:
        payload = results[arm]
        same = payload["series"] == prior
        diverge = next((i for i, (a, b) in enumerate(zip(payload["series"], prior))
                        if a != b), None)
        print(f"arm {arm}: byte-identical to the PRIOR record = {same}"
              + ("" if same else f" (first divergence at index {diverge})")
              + f"; equals the shipped BASELINE_SERIES = {payload['series'] == shipped}")
        print(f"   series[-5:] = {payload['series'][-5:]}  provinces France = "
              f"{payload['provinces'].get('France')} Britain = "
              f"{payload['provinces'].get('Britain')}")
    Path(args.out).write_text(json.dumps({
        "recorded": prior, "arms": results,
        "arm_specs": {k: {"up": v[1], "scenario": "shipped" if k == "1" else k}
                      for k, v in specs.items()}}, indent=1), encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
