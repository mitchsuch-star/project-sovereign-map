"""PC-F59 / PC-R2 — the austerlitz t24–44 measurement (S13e part 2, October
16, 2026; `docs/audits/PEACE_CONUNDRUM_2026_10_15.md` §43 F59, §46 D).

Part V measured THREE truces in 26 turns on the commanded austerlitz arm
(`--diplomacy accept`): every truce popped the ledger and re-stamped the
war's age at the collapse, so the war cycled truce → collapse → truce. This
tool drives the SAME twenty turns from the same t24 save twice — the rules
DOWN through their seams (the shipped behaviour) and UP — and records how
many truces France signed, how many collapsed, and the war's age as the
AI's own `pair_war_age` read it at the last turn.

    python tools/_pc_s13e2_austerlitz_drive.py --save <t24 save> [--turns 20] [--out JSON]

Writes `tools/_pc_s13e2_austerlitz_truces.json` (committed with the landing
record; `tests/test_pc_rulings.py::TestPCR2::test_k_f59_...` pins it).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRIVER = ROOT / "tools" / "playtest_driver.py"
SCRIPT = ROOT / "tools" / "playtest_scripts" / "commanded_full40.json"

DOWN = [
    "backend.game_logic.diplomacy:truce_keeps_the_ledger=False",
    "backend.game_logic.coalition:truce_holds_exhaustion=False",
    ("backend.game_logic.diplomacy:truce_hope_alive="
     "{'alive': True, 'members': [], 'subsidy': None, 'exhaustion': {}, "
     "'alive_terms': ['league'], 'dead_terms': []}"),
]


def run_arm(name: str, save: Path, turns: int, seams: list, out_root: Path) -> dict:
    out = out_root / name
    cmd = [sys.executable, str(DRIVER), "--name", name, "--seed", "austerlitz",
           "--from-save", str(save), "--script", str(SCRIPT), "--turns", str(turns),
           "--diplomacy", "accept", "--out", str(out)]
    for s in seams:
        cmd += ["--seam", s]
    env = dict(os.environ)
    env["LLM_MODE"] = "mock"
    for k in ("PYTHONIOENCODING", "PYTHONDONTWRITEBYTECODE", "SOVEREIGN_SCENARIO", "SOVEREIGN_MAP"):
        env.pop(k, None)
    proc = subprocess.run(cmd, env=env, cwd=str(ROOT), capture_output=True, timeout=5400)
    if proc.returncode not in (0, 1):
        raise SystemExit(f"{name} failed:\n{proc.stdout.decode('utf-8', 'replace')[-2000:]}\n"
                         f"{proc.stderr.decode('utf-8', 'replace')[-3000:]}")
    digest = out / name / "digest.md"
    text = digest.read_text(encoding="utf-8")
    truces = len(re.findall(r"RAIL armistice_ratified: A truce with Austria", text))
    collapses = len(re.findall(r"armistice between (?:Austria and France|France and Austria) has collapsed", text))
    ripened = len(re.findall(r"armistice between (?:Austria and France|France and Austria) has concluded", text))
    # the last save's own stores: the war's age as the AI reads it
    saves = sorted((out / name / "saves").glob("*.json"))
    age = None
    exhaustion = None
    state = None
    for cand in reversed(saves):
        if cand.name == "autosave.json":
            data = json.loads(cand.read_text(encoding="utf-8"))
            ws = data.get("world_state", data)
            key = "Austria|France"
            state = ws.get("diplomatic_states", {}).get(key)
            start = (ws.get("war_start_turns") or {}).get(key)
            age = (int(ws["current_turn"]) - int(start)) if start is not None else None
            exhaustion = (ws.get("war_exhaustion") or {}).get("Austria")
            break
    return {"name": name, "seams_down": seams, "truces_with_austria": truces,
            "collapses": collapses, "ripened_into_peace": ripened,
            "final_state": state, "war_age_at_end": age, "austria_exhaustion_at_end": exhaustion,
            "digest": str(digest.relative_to(out_root))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", required=True)
    ap.add_argument("--turns", type=int, default=20)
    ap.add_argument("--out", default=str(ROOT / "tools" / "_pc_s13e2_austerlitz_truces.json"))
    ap.add_argument("--work", default="")
    args = ap.parse_args()
    work = Path(args.work) if args.work else Path(tempfile.mkdtemp(prefix="pc_s13e2_aust_"))
    save = Path(args.save)
    before = run_arm("before_rules_down", save, args.turns, DOWN, work)
    after = run_arm("after_rules_up", save, args.turns, [], work)
    record = {"save": save.name, "turns": args.turns, "seed": "austerlitz",
              "script": SCRIPT.name, "diplomacy": "accept",
              "before": before, "after": after, "work": str(work)}
    Path(args.out).write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in record.items() if k in ("before", "after")}, indent=1))
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
