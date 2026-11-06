"""AU-4 the courts' flip (docs/AUTHORITY_CURRENCY_SPEC.md §6.8) — the flip's
record beside the review's, on the 59 measured runs: the PARKED tree (AU-4
part 1, the courts' writes down), the courts up as the review MEASURED them
(AU-20 in the tree: the AI's admin step dropped the rung's `currency`, so a
court's Decree at its floors was paid in gold under its reserve bar), and the
FLIP as shipped (AU-20 fixed: the Decree paid in authority). The review
composer's own reading (`tools/_standing_courts_review.py`), its trees renamed;
the courts' Decrees counted by the purse that paid them. Seeded paths, not laws.

    .venv/Scripts/python.exe -X utf8 tools/_standing_courts_flip.py

Writes tools/_standing_courts_flip.json (committed with the landing record).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools._standing_courts_review import compose  # noqa: E402

REVIEW = ROOT / "tools" / "playtest_runs" / "au4_2026_11_05" / "courts_flat"
FLIP = ROOT / "tools" / "playtest_runs" / "au4_flip_2026_11_06"
RENAME = {"shipped": "parked", "flat": "reviewed", "grip": "flipped"}


def _renamed(value):
    if isinstance(value, dict):
        return {RENAME.get(k, k): _renamed(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_renamed(v) for v in value]
    return value


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parked-standing", default=str(FLIP / "parked" / "_standing_final.json"))
    ap.add_argument("--parked-reach", default=str(FLIP / "parked" / "_s14c_sweep_final.json"))
    ap.add_argument("--reviewed-standing", default=str(REVIEW / "standing_courts_flat.json"))
    ap.add_argument("--reviewed-reach", default=str(REVIEW / "reach_courts_flat.json"))
    ap.add_argument("--flipped-standing", default=str(ROOT / "tools" / "_standing_final.json"))
    ap.add_argument("--flipped-reach", default=str(ROOT / "tools" / "_s14c_sweep_final.json"))
    ap.add_argument("--rig", default=str(ROOT / "tools" / "_standing_series_arms_final.json"))
    ap.add_argument("--out", default=str(ROOT / "tools" / "_standing_courts_flip.json"))
    args = ap.parse_args(argv)
    composed = compose(argparse.Namespace(
        shipped_standing=args.parked_standing, flat_standing=args.reviewed_standing,
        grip_standing=args.flipped_standing, shipped_reach=args.parked_reach,
        flat_reach=args.reviewed_reach, grip_reach=args.flipped_reach, rig=args.rig))
    out = _renamed(composed)
    out["_what"] = ("AU-4 the courts' flip (AUTHORITY_CURRENCY_SPEC.md §6.8): the parked tree, the courts up "
                    "as the review measured them (AU-20 in the tree — the courts' Decree at their floors paid "
                    "in gold) and the flip as shipped (AU-20 fixed — paid in authority); per run the player's "
                    "end and each great power's end, the courts' moves by cause, each letter's arrivals, the "
                    "series rig's arms. Seeded paths, not laws.")
    out["court_decrees_in_authority"] = {tree: int((moves or {}).get("edict_decreed", 0))
                                         for tree, moves in out["court_moves_by_cause"].items()}
    Path(args.out).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", args.out)
    print("courts' mean end:", json.dumps(out["courts_mean_end"]))
    print("at or under 30:", json.dumps(out["courts_at_or_under_30"]))
    print("court moves:", json.dumps(out["court_moves_by_cause"]))
    print("court decrees in authority:", json.dumps(out["court_decrees_in_authority"]))
    print("letters:", json.dumps(out["letters"]))
    print("player's end moved on", len(out["player_end_moved"]), "runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
