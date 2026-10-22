"""VP-1 "The Emperor's Designs", S14b part 1 (`docs/VP1_DESIGNS_SPEC.md` §7) —
the archived commanded arms re-run on the part's tree, every stream compared
with the S14b head's archive (`docs/audits/score_runs/2026_10_21_rr6x3/`).

    python tools/_vp1_arm_attribution.py --run DIR [--record OUT.json]
        [--baseline DIR --arms FC,...]   (S14b part 2: an arm the archive lacks,
                                          compared with a run of the prior tree)

DIR is a `tools/score_run.py run` of CMD-H, CMD-A, CMD-M, OP, FLD, DL, LAW and
VOLTE on the part's tree. Part 1 ships unarmed — the shipped boot authors no
`imperial_designs` block — so every stream must equal the archive: the GAME
stream (the ledger and the commands, `tools/_sf_rr6_arm_attribution.stream`),
the VIEW stream (battles, the enemy phase) and every other digest record but
the run's own stamps (the tree's SHA, the wall clock). A record that parts is
printed with its turn and both sides, for the landing record to attribute.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "docs" / "audits" / "score_runs" / "2026_10_21_rr6x3"
ARMS = ("CMD-H", "CMD-A", "CMD-M", "OP", "FLD", "DL", "LAW", "VOLTE")
STAMPS = ("sha", "engine", "started", "finished", "elapsed", "wall", "tree", "out")


def _records(arm) -> list:
    out = []
    for r in arm.records:
        out.append({k: v for k, v in r.items() if k not in STAMPS})
    return out


def compare(run_dir: pathlib.Path, baseline: pathlib.Path = ARCHIVE, arms=ARMS) -> dict:
    sys.path.insert(0, str(ROOT))
    from tools import score_run as SR
    from tools._sf_rr6_arm_attribution import first_parting, stream
    archive = SR.load_arms(baseline)
    run = SR.load_arms(run_dir)
    result = {}
    for name in arms:
        if name not in archive or name not in run:
            result[name] = {"missing": True}
            continue
        row = {}
        for which in ("game", "view"):
            p = first_parting(stream(archive[name], which), stream(run[name], which))
            row[which] = "equal" if p is None else f"parts at turn {p[0]}: {p[1]} | {p[2]}"
        a, b = _records(archive[name]), _records(run[name])
        parted = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), None)
        if parted is None and len(a) != len(b):
            parted = min(len(a), len(b))
        row["records"] = ("equal" if parted is None else
                          f"record {parted}: {json.dumps(a[parted] if parted < len(a) else None, default=str)[:300]}"
                          f" | {json.dumps(b[parted] if parted < len(b) else None, default=str)[:300]}")
        row["n_records"] = [len(a), len(b)]
        result[name] = row
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--record", default="")
    ap.add_argument("--baseline", default=str(ARCHIVE))
    ap.add_argument("--arms", default=",".join(ARMS))
    args = ap.parse_args()
    result = compare(pathlib.Path(args.run), pathlib.Path(args.baseline),
                     [a for a in args.arms.split(",") if a])
    for name, row in result.items():
        print(f"{name:6s} " + "  ".join(f"{k}={v}" for k, v in row.items()))
    if args.record:
        pathlib.Path(args.record).write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
