"""SF-RR6 (Score Finish residue 5, October 21, 2026): the deltas of the v1.2
re-read beside each archive's frozen record (`docs/SCORE_FINISH_SPEC.md` §4.4
— the corrected readers never rewrite a past mark; `tools/score_reread.py`
writes `checklist_v1_2.json` BESIDE `checklist.json`).

    python tools/_sf_rr6_reread_deltas.py RUN_DIR [RUN_DIR ...] [--md OUT.md]

For each archive: every item whose mark moved (measured / pass), the pillar
readings that moved, and the directional — as recorded, as v1.1 re-read it
(`checklist_v1_1.json`, where the archive has one) and as v1.2 re-reads it.
An item v1.1 had already moved is marked so; the rest are SF-RR6's.
"""
from __future__ import annotations

import argparse
import json
import pathlib


def _mark(item: dict) -> str:
    if not item.get("measured"):
        return "·"
    return "✓" if item.get("pass") else "✗"


def deltas(run_dir: pathlib.Path) -> dict:
    base = json.loads((run_dir / "checklist.json").read_text(encoding="utf-8"))
    rer = json.loads((run_dir / "checklist_v1_2.json").read_text(encoding="utf-8"))
    v11_path = run_dir / "checklist_v1_1.json"
    v11 = json.loads(v11_path.read_text(encoding="utf-8")) if v11_path.exists() else None
    rows, pillars = [], []
    for key, p in rer["pillars"].items():
        was = {i["id"]: i for i in base["pillars"][key]["items"]}
        mid = ({i["id"]: i for i in v11["pillars"][key]["items"]} if v11 else {})
        for item in p["items"]:
            old = was[item["id"]]
            if _mark(old) != _mark(item):
                m11 = _mark(mid[item["id"]]) if item["id"] in mid else "—"
                rows.append({"item": f"{key}.{item['id']}", "recorded": _mark(old),
                             "v1_1": m11, "reread": _mark(item),
                             "whose": ("v1.1's" if m11 == _mark(item) and m11 != "—"
                                       else "SF-RR6"),
                             "why": str(item.get("evidence", ""))[:260]})
        before = base["pillars"][key]["score"]["reading"]
        after = p["score"]["reading"]
        if before != after:
            pillars.append({"pillar": key, "recorded": before, "reread": after})
    return {"run": run_dir.name, "items": rows, "pillars": pillars,
            "directional": {"recorded": base.get("directional"), "reread": rer.get("directional")}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--md", default="")
    args = ap.parse_args()
    out = [deltas(pathlib.Path(r).resolve()) for r in args.runs]
    lines = []
    for d in out:
        dr, dv = d["directional"]["recorded"] or {}, d["directional"]["reread"] or {}
        lines.append(f"### {d['run']} — directional {dr.get('value')} over {dr.get('over')} "
                     f"→ {dv.get('value')} over {dv.get('over')} (v1.2 re-read)")
        lines.append("")
        lines.append("| Item | Recorded | v1.1 re-read | v1.2 re-read | Whose | The v1.2 evidence |")
        lines.append("|---|---|---|---|---|---|")
        for r in d["items"]:
            lines.append(f"| {r['item']} | {r['recorded']} | {r['v1_1']} | {r['reread']} | "
                         f"{r['whose']} | {r['why'].replace('|', '/')} |")
        if not d["items"]:
            lines.append("| — | | | | | no item moved |")
        lines.append("")
        if d["pillars"]:
            lines.append("Pillar readings: " + "; ".join(
                f"{p['pillar']} {p['recorded']} → {p['reread']}" for p in d["pillars"]))
            lines.append("")
    text = "\n".join(lines)
    if args.md:
        pathlib.Path(args.md).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
