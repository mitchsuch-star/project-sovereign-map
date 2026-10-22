"""S14c part 4 (`docs/EVENTS_SPEC.md` §7, §9 Part 4) — the moments' measurement,
recorded. Composes `tools/_s14c_sweep_final.json` from part 4's runs, every one
carrying the moments' production-time trace (`tools/_moments_trace.py`):

    --sweep DIR         `tools/ai_v_sweep.py --all --out DIR` — arm A (control),
                        arm B (variance), arm C (the ten SWEEP_SEEDS) and the
                        scripted France; the trace rides every run
    --commanded DIR     the archived commanded arms (`tools/score_run.py run`
                        with `--moments-trace` on each driver)
    --accept DIR        CMD-A / CMD-M / CMD-H with `--moment accept --moments-trace`
    --road DIR          `tools/_vp1_road_arms.py --out DIR` (the trace rides
                        every road arm)
    --road-accept DIR   VP1-RH with `--moment accept` (the same tool, its --out)

Each arm keeps the trace's verdict — the ceilings, the floors, shown = applied —
its mornings, and each moment's reach composed from the trace alone (seeded
paths, not laws): "arrived T8, answered accept", "arrived T18, lapsed T19",
"passed T11 (premise)", "crowded out T19", or "pending — the last morning T28".
The record carries the shipped deck's hash: a deck edited after the
measurement reds `tests/test_moments_pacing.py` until it is measured again.

    python tools/_s14c_sweep_record.py --sweep DIR --commanded DIR --accept DIR \\
        --road DIR --road-accept DIR [--out tools/_s14c_sweep_final.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
OUT = ROOT / "tools" / "_s14c_sweep_final.json"


def deck_sha(block: dict) -> str:
    """The shipped block's identity (sorted keys; the record and the pin agree)."""
    return hashlib.sha256(json.dumps(block, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def reach(trace: dict, deck_ids: list) -> dict:
    """Each moment's fate on one arm, read off the trace's own rows."""
    mornings = trace.get("mornings") or []
    applications = trace.get("applications") or []
    last = max([int(m.get("turn", 0)) for m in mornings] or [0])
    out = {}
    for mid in deck_ids:
        arrived = next((int(m["turn"]) for m in mornings if mid in (m.get("delivered") or [])), None)
        passed = next(((int(m["turn"]), m["passed"][mid]) for m in mornings
                       if mid in (m.get("passed") or {})), None)
        answer = next((a for a in applications if a.get("moment") == mid
                       and a.get("kind") in ("answer", "lapse")), None)
        if arrived is not None:
            if answer is None:
                out[mid] = f"arrived T{arrived}, standing at the last morning T{last}"
            elif answer["kind"] == "lapse":
                out[mid] = f"arrived T{arrived}, lapsed T{answer['turn']} (its decline)"
            else:
                out[mid] = f"arrived T{arrived}, answered {answer['answer']} T{answer['turn']}"
        elif passed is not None:
            turn, why = passed
            out[mid] = f"crowded out T{turn} (its receipt)" if why == "crowded" else f"passed T{turn} ({why})"
        else:
            out[mid] = f"pending — the last morning T{last}"
    return out


def row(trace: dict, deck_ids: list, **extra) -> dict:
    judged = trace.get("judged") or {}
    out = {"measured": bool(trace.get("measured")), "mornings": int(judged.get("mornings", 0) or 0),
           "ceiling_breaches": judged.get("ceiling_breaches") or [],
           "floor_breaches": judged.get("floor_breaches") or [],
           "floors": judged.get("floors") or {},
           "shown_equals_applied": bool(judged.get("shown_equals_applied", True)),
           "mismatches": judged.get("mismatches") or [],
           "answers": judged.get("answers") or [],
           "reach": reach(trace, deck_ids),
           "errors": trace.get("errors") or []}
    out.update(extra)
    return out


def _sweep(root: Path, deck_ids: list) -> dict:
    out = {}
    for path in sorted(root.glob("arm*.json")):
        digest = json.loads(path.read_text(encoding="utf-8"))
        trace = (digest.get("final") or {}).get("moments_trace") or {}
        derived = digest.get("derived") or {}
        meta = digest.get("meta") or {}
        out[path.stem] = row(trace, deck_ids, seed=meta.get("seed"), ambient_base=meta.get("ambient_base"),
                             script=meta.get("script"),
                             metrics={"max_per_turn": derived.get("moments_max_per_producing_turn", 0),
                                      "open_max": derived.get("open_letters_max", 0),
                                      "during_foreground": derived.get("letters_during_foreground", 0),
                                      "fire_turns": derived.get("fire_turns", {})})
    return out


def _driver_arms(root: Path, deck_ids: list) -> dict:
    out = {}
    for meta_path in sorted(root.glob("arms/*/meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        trace = meta.get("moments_trace") or {}
        if trace:
            out[meta_path.parent.name] = row(trace, deck_ids, status=meta.get("status"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweep", required=True)
    ap.add_argument("--commanded", required=True)
    ap.add_argument("--accept", required=True)
    ap.add_argument("--road", required=True, help="the road arms' --out directory")
    ap.add_argument("--road-accept", required=True, help="Road I answered: its --out directory")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    block = json.loads(SCENARIO.read_text(encoding="utf-8"))["moments"]
    deck_ids = [e["id"] for e in block["deck"]]
    record = {
        "_part": ("S14c part 4 — the moments over the 10-seed sweep and the arms, each run "
                  "carrying the production-time trace (docs/EVENTS_SPEC.md §7, §17)"),
        "deck_sha": deck_sha(block), "pacing": block.get("pacing") or {}, "deck": deck_ids,
        "sweep": _sweep(Path(args.sweep), deck_ids),
        "commanded": _driver_arms(Path(args.commanded), deck_ids),
        "accept": _driver_arms(Path(args.accept), deck_ids),
        "road": _driver_arms(Path(args.road), deck_ids),
        "road_accept": _driver_arms(Path(args.road_accept), deck_ids),
    }
    Path(args.out).write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for family in ("sweep", "commanded", "accept", "road", "road_accept"):
        rows = record[family]
        print(f"{family:12s} arms {len(rows):2d}  ceiling breaches "
              f"{sum(len(r['ceiling_breaches']) for r in rows.values())}  floor breaches "
              f"{sum(len(r['floor_breaches']) for r in rows.values())}  shown=applied "
              f"{all(r['shown_equals_applied'] for r in rows.values())}")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
