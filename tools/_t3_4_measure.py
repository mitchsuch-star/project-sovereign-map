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
LAST_REFUGE_EXIT = "last_refuge"


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


def crown_grounds() -> dict:
    """T4-3: {province: court} — the provinces the scenario's promotion
    laws rest on (each law's `requires_design` on its court's agenda deck),
    read off the file (no backend import in this parent)."""
    scenario = json.loads((ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
                           / "europe_1805.json").read_text(encoding="utf-8"))
    out = {}
    for court, rows in (scenario.get("reforms") or {}).items():
        for row in rows if isinstance(rows, list) else []:
            design_id = row.get("requires_design") if isinstance(row, dict) else None
            for entry in (scenario.get("agendas") or {}).get(court) or []:
                if design_id and isinstance(entry, dict) and entry.get("id") == design_id:
                    out.update({str(r): str(court) for r in entry.get("regions") or []})
    return out


_CROWN_GROUNDS = crown_grounds()


def census_of(digest: dict) -> dict:
    peaces, letters, signed, evacuations, refuges = [], [], [], [], []
    # T4-3: every change of hands of a province a crown rests on — how near
    # a promotion came (the crown's court taking it starts its six turns).
    grounds = []
    # T4-1 (DYNAMISM_SPEC.md §3c G2): the Alarm's guarantees — a pledge
    # that names the conqueror it answers (`against`) — and every honour.
    alarm_guarantees, honoured = [], []
    seats, promotions, demotions = [], [], []
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
            # T4-2 (DYNAMISM_SPEC.md §3c G5): a court that signed at its
            # last province instead of falling.
            if (event.get("type") == "third_party_peace"
                    and event.get("exit") == LAST_REFUGE_EXIT):
                refuges.append({"turn": int(row.get("turn", 0)),
                                "proposer": str(event.get("proposer") or ""),
                                "accepter": str(event.get("accepter") or ""),
                                "consequence": str(event.get("consequence") or "")})
            # T4-2b (DYNAMISM_SPEC.md §3c "The seat"): a court's seat moved
            # by a treaty, and home again — `province_returned` by outcome.
            if (event.get("type") == "province_returned"
                    and event.get("outcome") in ("court_removed", "court_returned")):
                seats.append({"turn": int(row.get("turn", 0)),
                              "court": str(event.get("nation") or ""),
                              "outcome": str(event.get("outcome") or ""),
                              "seat": str(event.get("region") or ""),
                              "lost": str(event.get("lost") or ""),
                              "holder": str(event.get("target_nation") or "")})
            if (event.get("type") == "region_captured"
                    and str(event.get("region") or "") in _CROWN_GROUNDS):
                grounds.append({"turn": int(row.get("turn", 0)),
                                "region": str(event.get("region") or ""),
                                "crown_of": _CROWN_GROUNDS[str(event.get("region"))],
                                "by": str(event.get("captured_by") or ""),
                                "from": str(event.get("captured_from") or "")})
            # T4-3 (§3c G6): a crown taken, and a crown lost with its grounds.
            if event.get("type") == "rank_promotion":
                promotions.append({"turn": int(row.get("turn", 0)),
                                   "court": str(event.get("nation") or ""),
                                   "law": str(event.get("law") or ""),
                                   "grounds": list(event.get("grounds") or [])})
            if event.get("type") == "law_lapsed" and event.get("reason") == "grounds_lost":
                demotions.append({"turn": int(row.get("turn", 0)),
                                  "court": str(event.get("nation") or ""),
                                  "law": str(event.get("law") or ""),
                                  "grounds": list(event.get("grounds") or [])})
        for prop in row.get("incoming_proposals") or []:
            if prop.get("ptype") == AIM_LETTER:
                letters.append({"turn": int(row.get("turn", 0)),
                                "proposer": str(prop.get("proposer") or "")})
    metrics = derive_metrics(digest)
    return {"aim_peaces": peaces, "aim_letters": letters, "signed_cessions": signed,
            "evacuations": evacuations,
            "last_refuges": refuges,
            "seats": seats,
            "rank_promotions": promotions,
            "grounds_lapses": demotions,
            "crown_grounds": grounds,
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
            "last_refuges": sum(len(c["last_refuges"]) for c in census.values()),
            "seats_removed": sum(1 for c in census.values() for s in c["seats"]
                                 if s["outcome"] == "court_removed"),
            "seats_returned": sum(1 for c in census.values() for s in c["seats"]
                                  if s["outcome"] == "court_returned"),
            "rank_promotions": sum(len(c["rank_promotions"]) for c in census.values()),
            "grounds_lapses": sum(len(c["grounds_lapses"]) for c in census.values()),
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
