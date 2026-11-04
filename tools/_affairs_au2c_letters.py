"""AU-2c "the Bank and the Pope" (docs/AUTHORITY_CURRENCY_SPEC.md §6.4) — the
review record put to the user BEFORE arming (RE's rule: a template without a
measured premise is not armed).

Reads the two chains of `tools/playtest_runs/au2c_2026_11_04/`: the SHIPPED
tree (the letters held out — its records are the committed tool records) and
the ARMED tree (`standing.letters_armed` forced up on every arm: the driver's
`--seam`, `INK_IRON_SEAMS` for the sweep's and the probe's children). Per run:
each letter's premise mornings (the moments trace's affair frames — `true`),
its due mornings (the `due` marks: the premise held for its streak and the
floor allowed it), its arrivals and answers (the reach record), and what it
displaced — every other template's arrivals, shipped against armed — and the
standing's end on both trees. Seeded paths, not laws: a run whose arrivals
moved is attributed by event, never averaged.

    .venv/Scripts/python.exe tools/_affairs_au2c_letters.py \
        --shipped tools/playtest_runs/au2c_2026_11_04/shipped \
        --armed tools/playtest_runs/au2c_2026_11_04/armed \
        --shipped-reach tools/_s14c_sweep_final.json \
        --armed-reach tools/playtest_runs/au2c_2026_11_04/armed/reach_armed.json \
        --shipped-standing tools/_standing_final.json \
        --armed-standing tools/playtest_runs/au2c_2026_11_04/armed/standing_armed.json \
        --out tools/_affairs_au2c_letters.json
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
LETTERS = ("the_bank", "the_popes_ports")
FAMILIES = ("sweep", "commanded", "accept", "reach_aar", "saves", "haiti", "road", "road_accept")


def _template(mid: str) -> str:
    return str(mid or "").split("#", 1)[0]


def traces(root: Path) -> Dict[str, List[Dict[str, Any]]]:
    """{family/arm: the moments trace's mornings} for every run under `root`."""
    out: Dict[str, List[Dict[str, Any]]] = {}
    for meta_path in sorted(root.rglob("arms/*/meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        family = meta_path.parents[2].name
        out[f"{family}/{meta_path.parent.name}"] = list((meta.get("moments_trace") or {}).get("mornings") or [])
    sweep = root / "sweep"
    for path in sorted(sweep.glob("arm*.json")):
        digest = json.loads(path.read_text(encoding="utf-8"))
        out[f"sweep/{path.stem}"] = list(((digest.get("final") or {}).get("moments_trace") or {}).get("mornings") or [])
    return out


def premise_rows(mornings: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    rows = {}
    for letter in LETTERS:
        held = [int(m["turn"]) for m in mornings if letter in ((m.get("affairs") or {}).get("true") or [])]
        due = [int(m["turn"]) for m in mornings
               if any(str(d).split("|", 1)[0] == letter for d in ((m.get("affairs") or {}).get("due") or []))]
        rows[letter] = {"premise_mornings": len(held), "first_held": held[0] if held else None,
                        "due_mornings": len(due), "first_due": due[0] if due else None}
    return rows


def reach_runs(record: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    out = {}
    for family in FAMILIES:
        for arm, row in (record.get(family) or {}).items():
            if isinstance(row, dict) and row.get("measured"):
                out[f"{family}/{arm}"] = row
    return out


def arrivals(row: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Every affair occurrence the run delivered: its answer row (an answer,
    a lapse — `crowded` rows never arrived)."""
    return [a for a in (row.get("answers") or [])
            if "#" in str(a.get("moment") or "") and a.get("kind") in ("answer", "lapse")]


def standing_rows(record: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {f"{r.get('family')}/{r.get('arm')}": r for r in (record.get("rows") or []) if r.get("measured")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shipped", required=True)
    ap.add_argument("--armed", required=True)
    ap.add_argument("--shipped-reach", required=True)
    ap.add_argument("--armed-reach", required=True)
    ap.add_argument("--shipped-standing", required=True)
    ap.add_argument("--armed-standing", required=True)
    ap.add_argument("--out", default=str(ROOT / "tools" / "_affairs_au2c_letters.json"))
    args = ap.parse_args()

    armed_traces = traces(Path(args.armed))
    shipped_reach = reach_runs(json.loads(Path(args.shipped_reach).read_text(encoding="utf-8")))
    armed_reach = reach_runs(json.loads(Path(args.armed_reach).read_text(encoding="utf-8")))
    shipped_st = standing_rows(json.loads(Path(args.shipped_standing).read_text(encoding="utf-8")))
    armed_st = standing_rows(json.loads(Path(args.armed_standing).read_text(encoding="utf-8")))

    runs: Dict[str, Any] = {}
    totals = {letter: Counter() for letter in LETTERS}
    displaced = Counter()
    gained = Counter()
    for key in sorted(set(armed_reach) | set(shipped_reach)):
        a_rows, s_rows = armed_reach.get(key) or {}, shipped_reach.get(key) or {}
        a_arr, s_arr = arrivals(a_rows), arrivals(s_rows)
        prem = premise_rows(armed_traces.get(key) or [])
        row: Dict[str, Any] = {"letters": {}}
        for letter in LETTERS:
            mine = [{"turn": int(a["turn"]), "kind": a["kind"], "answer": a.get("answer")}
                    for a in a_arr if _template(a["moment"]) == letter]
            row["letters"][letter] = {**prem[letter], "arrivals": mine}
            t = totals[letter]
            t["runs_premise"] += 1 if prem[letter]["premise_mornings"] else 0
            t["premise_mornings"] += prem[letter]["premise_mornings"]
            t["runs_due"] += 1 if prem[letter]["due_mornings"] else 0
            t["runs_arrived"] += 1 if mine else 0
            t["arrivals"] += len(mine)
            for arrival in mine:
                t[f"{arrival['kind']}_{arrival['answer']}"] += 1
        # every other template's arrivals, shipped against armed (by template; the turns beside)
        others_s = Counter(_template(a["moment"]) for a in s_arr if _template(a["moment"]) not in LETTERS)
        others_a = Counter(_template(a["moment"]) for a in a_arr if _template(a["moment"]) not in LETTERS)
        moved = {}
        for template in sorted(set(others_s) | set(others_a)):
            if others_s[template] != others_a[template]:
                moved[template] = {"shipped": others_s[template], "armed": others_a[template],
                                   "turns_shipped": [int(a["turn"]) for a in s_arr if _template(a["moment"]) == template],
                                   "turns_armed": [int(a["turn"]) for a in a_arr if _template(a["moment"]) == template]}
                if others_a[template] < others_s[template]:
                    displaced[template] += others_s[template] - others_a[template]
                else:
                    gained[template] += others_a[template] - others_s[template]
        row["others_moved"] = moved
        s_st, a_st = shipped_st.get(key) or {}, armed_st.get(key) or {}
        row["standing"] = {"shipped_end": s_st.get("end"), "armed_end": a_st.get("end"),
                           "shipped_min": s_st.get("min"), "armed_min": a_st.get("min")}
        runs[key] = row

    out = {
        "_what": ("AU-2c — the Bank's Panic and the Pope's Refusal measured UP for the user's review before "
                  "arming (AUTHORITY_CURRENCY_SPEC.md §6.4): per run each letter's premise mornings, due "
                  "mornings, arrivals and answers on the ARMED tree; every other template's arrivals shipped "
                  "against armed; the standing's end on both trees. Seeded paths, not laws."),
        "runs_measured": len(runs),
        "totals": {letter: dict(sorted(totals[letter].items())) for letter in LETTERS},
        "others_displaced": dict(sorted(displaced.items())),
        "others_gained": dict(sorted(gained.items())),
        "runs": runs,
    }
    Path(args.out).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(runs)} runs; totals {json.dumps(out['totals'])}")
    print(f"displaced {dict(displaced)}; gained {dict(gained)}")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
