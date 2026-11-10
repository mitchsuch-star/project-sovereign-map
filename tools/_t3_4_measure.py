"""T3-4 the terms — the slice's measure (DYNAMISM_SPEC.md §2 Tier 3; the
Tier-3 gate record AI_INTENT_SPEC.md §13.2 R5; November 9, 2026).

ONE chain over the ten ambient `SWEEP_SEEDS` x 40 turns (each child under
PYTHONHASHSEED=0 via `ai_v_sweep.spawn_run`; THIS PARENT RUNS PLAIN, never
`-X utf8`), writing TWO records from the same digests:

* `--out` — the DY signature record, in `tools/_dy0_baseline.py`'s exact
  shape (per seed the `_variance_signature` and the `story_class`, plus the
  distinct-class count), so the kept-record pins read it like every other;
* `--census` — the terms' own census: per seed the aim peaces (the
  `third_party_peace` events whose `exit` is `aim_held_sue` — both AI–AI
  roads log it), each named (turn, proposer, accepter, consequence), and the
  P8-Aim letters France received (`incoming_proposals` rows of label
  `aim_peace` — the ambient France answers none), plus the debt per seed
  (`derive_metrics`' `captures_outside_aim`).

A control chain sets `INK_IRON_SEAMS` (the children copy the environment —
the AU-2c hook) to hold both T3-4 seams down; it must reproduce the T3-3
final record's signatures byte for byte. The chain runs ALONE: no backend,
test or deck edit lands while it runs.

Usage:
  .venv/Scripts/python.exe tools/_t3_4_measure.py --out FILE --census FILE
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.ai_v_sweep import (  # noqa: E402
    AMBIENT_K,
    SWEEP_SEEDS,
    _variance_signature,
    derive_metrics,
    spawn_run,
    story_class,
    story_class_count,
)

AIM_EXIT = "aim_held_sue"
AIM_LETTER = "aim_peace"


def _signs_provinces(event: dict) -> bool:
    """T3-5: an AI peace whose words name provinces signed over — "X takes
    Y" (the instance road's consequence) or "X keeps Y by treaty" (the pair
    exits' lock)."""
    words = str(event.get("consequence") or "")
    if event.get("exit") == AIM_EXIT:
        return True
    if event.get("exit"):
        # a pair exit's own words ("… takes it on the held line") are no
        # cession; only the lock's sentence is
        return "keeps " in words and "by treaty" in words
    return " takes " in f" {words}"


def census_of(digest: dict) -> dict:
    peaces, letters, signed, evacuations = [], [], [], []
    # T4-1 (DYNAMISM_SPEC.md §3c G2): the Alarm's guarantees — a pledge
    # that names the conqueror it answers (`against`) — and every honour.
    alarm_guarantees, honoured = [], []
    for row in digest.get("turns") or []:
        for event in row.get("events") or []:
            if event.get("type") == "guarantee_pledged" and event.get("against"):
                alarm_guarantees.append({"turn": int(row.get("turn", 0)),
                                         "guarantor": str(event.get("guarantor") or ""),
                                         "protected": str(event.get("protected") or ""),
                                         "against": str(event.get("against") or "")})
            if event.get("type") == "guarantee_honored":
                honoured.append({"turn": int(row.get("turn", 0)),
                                 "guarantor": str(event.get("guarantor") or ""),
                                 "ward": str(event.get("ward") or ""),
                                 "aggressor": str(event.get("aggressor") or "")})
            if (event.get("type") == "third_party_peace"
                    and " evacuates " in str(event.get("consequence") or "")):
                evacuations.append({"turn": int(row.get("turn", 0)),
                                    "proposer": str(event.get("proposer") or ""),
                                    "accepter": str(event.get("accepter") or ""),
                                    "consequence": str(event.get("consequence") or "")})
            if event.get("type") == "third_party_peace" and _signs_provinces(event):
                signed.append({"turn": int(row.get("turn", 0)),
                               "proposer": str(event.get("proposer") or ""),
                               "accepter": str(event.get("accepter") or ""),
                               "exit": str(event.get("exit") or ""),
                               "consequence": str(event.get("consequence") or "")})
            if (event.get("type") == "third_party_peace"
                    and event.get("exit") == AIM_EXIT):
                peaces.append({"turn": int(row.get("turn", 0)),
                               "proposer": str(event.get("proposer") or ""),
                               "accepter": str(event.get("accepter") or ""),
                               "consequence": str(event.get("consequence") or "")})
        for prop in row.get("incoming_proposals") or []:
            if prop.get("ptype") == AIM_LETTER:
                letters.append({"turn": int(row.get("turn", 0)),
                                "proposer": str(prop.get("proposer") or "")})
    metrics = derive_metrics(digest)
    return {"aim_peaces": peaces, "aim_letters": letters, "signed_cessions": signed,
            "evacuations": evacuations,
            "alarm_guarantees": alarm_guarantees,
            "guarantees_honoured": honoured,
            "captures_outside_aim": int(metrics.get("captures_outside_aim", 0) or 0),
            "annexations_outside_aim": int(metrics.get("annexations_outside_aim", 0) or 0),
            "annexations_outside_aim_by_court": dict(
                (digest.get("final") or {}).get("annexations_outside_aim") or {})}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--turns", type=int, default=40)
    ap.add_argument("--out", required=True)
    ap.add_argument("--census", required=True)
    ap.add_argument("--label", default="t3-4",
                    help="the slice the record belongs to (its notes' head)")
    args = ap.parse_args()

    seeds, census = {}, {}
    for seed in SWEEP_SEEDS:
        print(f"[t3-4] {seed}: running {args.turns} ambient turns ...", flush=True)
        digest = spawn_run(seed, AMBIENT_K, args.turns)
        cls = story_class(digest)
        seeds[seed] = {
            "signature": _variance_signature(digest),
            "story_class": [[key, list(map(list, values))
                             if values and isinstance(values[0], tuple)
                             else list(values)]
                            for key, values in cls],
        }
        census[seed] = census_of(digest)
    classes = [json.dumps(seeds[s]["story_class"], sort_keys=True)
               for s in SWEEP_SEEDS]
    count = story_class_count(classes)
    record = {
        "_note": ((f"{args.label.upper()} — " if args.label != "t3-4" else "")
                  + "T3-4 the terms — the DY signature record (DYNAMISM_SPEC.md "
                  "§2 Tier 3; the gate record §13.2 R5) — ten ambient "
                  f"SWEEP_SEEDS x {args.turns} turns at K={AMBIENT_K}; "
                  "written by tools/_t3_4_measure.py (a chain run ALONE) in "
                  "tools/_dy0_baseline.py's shape; pinned by "
                  "tests/test_t3_4_the_terms.py."),
        "turns": int(args.turns),
        "ambient_base": int(AMBIENT_K),
        "story_class_count": int(count),
        "seeds": seeds,
    }
    out = pathlib.Path(args.out)
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")
    census_record = {
        "_note": ("T3-4 the terms — the census (aim peaces by both AI–AI "
                  "roads, P8-Aim letters France received, the debt) per "
                  "seed, from the same digests as the signature record."),
        "turns": int(args.turns),
        "seeds": census,
        "totals": {
            "aim_peaces": sum(len(c["aim_peaces"]) for c in census.values()),
            "aim_letters": sum(len(c["aim_letters"]) for c in census.values()),
            "signed_cessions": sum(len(c["signed_cessions"]) for c in census.values()),
            "evacuations": sum(len(c["evacuations"]) for c in census.values()),
            "alarm_guarantees": sum(len(c["alarm_guarantees"]) for c in census.values()),
            "guarantees_honoured": sum(len(c["guarantees_honoured"])
                                       for c in census.values()),
            "annexations_outside_aim": sum(c["annexations_outside_aim"]
                                           for c in census.values()),
            "captures_outside_aim": sum(c["captures_outside_aim"]
                                        for c in census.values()),
        },
    }
    pathlib.Path(args.census).write_text(
        json.dumps(census_record, indent=1, sort_keys=True) + "\n",
        encoding="utf-8")
    print(f"[t3-4] story_class_count = {count} of {len(SWEEP_SEEDS)}")
    print(f"[t3-4] totals = {census_record['totals']}")
    print(f"[t3-4] written {out} and {args.census}")


if __name__ == "__main__":
    main()
