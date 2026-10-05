#!/usr/bin/env python
"""THE RE-READ — a committed reading re-read under an amended checklist,
without re-scoring the reading (`docs/SCORE_FINISH_SPEC.md` §4.3, §5, §6.7).

    .venv/Scripts/python.exe -X utf8 tools/score_reread.py --run RUN_DIR \
        --checklist docs/SCORE_CHECKLIST_V1_1.json [--eyes EYES.json] --suffix v1_1

Why a separate tool and not `score_run.py check`:

* `check` rewrites the archive's own `checklist.json` / `scores.json` — the
  record of what the frozen instrument read. A re-read must sit BESIDE it.
* `check` prices every pillar's P1 cap off TODAY's defect ledger. A defect
  fixed after the reading (SFR-D11, SF-RR1 part (i)) would silently uncap its
  pillar — a re-score by the back door, which §5 forbids ("a fix landed after
  a reading is an item flip, never a re-score"). The re-read reads the open
  P1s from the archive's own `census_by_pillar.json`: the ledger AS THE
  READING STOOD.

What it does: every item keeps its archived mark, except
  (1) an item the amended checklist marks `amended` — re-read with the reader
      the item names (`reader`: a probe in `tools/_score_probes.py` or an
      `r_<pillar>_<ID>` in `tools/score_run.py`), on the archive's own arms;
  (2) an EYES item the `--eyes` file marks — the mark replaces the archived
      one (the user's, or the user's delegate's, over the panel's).
Then the frozen rule (§4.4) scores the items, and the result is written to
`RUN_DIR/checklist_<suffix>.json` and `RUN_DIR/scores_<suffix>.json`.
Nothing in the archive is overwritten, and no game state is touched.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import score_run as SR  # noqa: E402


def _resolve_reader(name: str):
    """A probe in `_score_probes` first (wrapped like `check` wraps it), else
    an AUTO reader `r_*` in `score_run`."""
    from tools import _score_probes as P

    if hasattr(P, name):
        return SR._probe(name)
    fn = getattr(SR, name, None)
    if fn is None:
        raise SystemExit(f"no reader named {name!r}")
    return fn


def reread(run_dir: pathlib.Path, checklist: dict, eyes: dict, suffix: str) -> dict:
    base = json.loads((run_dir / "checklist.json").read_text(encoding="utf-8"))
    census_path = run_dir / "census_by_pillar.json"
    census = (json.loads(census_path.read_text(encoding="utf-8"))
              if census_path.exists() else {"pillars": {}})
    arms = None
    ctx = None
    out = {
        "run": str(run_dir),
        "checklist_version": checklist.get("version"),
        "reread_of": "checklist.json",
        "census": "census_by_pillar.json (the ledger as the reading stood)",
        "pillars": {},
    }
    scores = {}
    for pillar in checklist["pillars"]:
        key = pillar["key"]
        archived = {i["id"]: i for i in base["pillars"][key]["items"]}
        items_out = []
        for item in pillar["items"]:
            iid, kind = item["id"], item["kind"]
            kept = dict(archived[iid])
            if kind == "EYES" and f"{key}.{iid}" in eyes:
                mark = eyes[f"{key}.{iid}"]
                res = SR._res(True, bool(mark.get("pass")),
                              str(mark.get("evidence", "")) + " (EYES)")
                items_out.append({"id": iid, "kind": kind, "text": item["text"],
                                  **res, "reread": "eyes"})
                continue
            if item.get("amended"):
                if arms is None:
                    arms = SR.load_arms(run_dir)
                    ctx = {"run_dir": run_dir, "arms": arms}
                    for k, script in (("dl_script", "score_docked_lines.json"),
                                      ("typed_script", "typed_road.json"),
                                      ("hold_script", SR.HOLD_SCRIPT)):
                        p = SR.ROOT / SR.SCRIPTS / script
                        ctx[k] = (json.loads(p.read_text(encoding="utf-8"))
                                  if p.exists() else {})
                fn = _resolve_reader(item["reader"])
                with contextlib.redirect_stdout(io.StringIO()):
                    res = fn(arms, ctx)
                items_out.append({"id": iid, "kind": kind, "text": item["text"],
                                  **res, "reread": item["amended"],
                                  "as_read": {k: kept.get(k) for k in
                                              ("measured", "pass", "evidence")}})
                continue
            kept["text"] = item["text"]
            items_out.append(kept)
        open_p1 = (census.get("pillars", {}).get(key) or {}).get("p1", [])
        sc = SR.pillar_score(items_out, open_p1)
        sc["open_p2"] = (census.get("pillars", {}).get(key) or {}).get("p2", 0)
        sc["target_ceilings"] = pillar["target_ceilings"]
        out["pillars"][key] = {"name": pillar["name"], "items": items_out, "score": sc}
        scores[key] = sc
    out["directional"] = SR.directional(scores)
    (run_dir / f"checklist_{suffix}.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (run_dir / f"scores_{suffix}.json").write_text(
        json.dumps({"directional": out["directional"],
                    "pillars": {k: {"name": out["pillars"][k]["name"], **v}
                                for k, v in scores.items()}},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--checklist", required=True)
    ap.add_argument("--eyes", default="")
    ap.add_argument("--suffix", required=True)
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    run_dir = pathlib.Path(args.run).resolve()
    checklist = json.loads(pathlib.Path(args.checklist).read_text(encoding="utf-8"))
    eyes = (json.loads(pathlib.Path(args.eyes).read_text(encoding="utf-8"))
            if args.eyes else {})
    out = reread(run_dir, checklist, eyes, args.suffix)
    d = out["directional"]
    print(f"re-read {run_dir.name} under {args.checklist}: directional "
          f"{d['value']} over {d['over']}")
    for key, p in out["pillars"].items():
        sc = p["score"]
        flips = [i["id"] for i in p["items"] if i.get("reread")]
        print(f"  {key:18s} {sc['reading']:>12s}  ceilings {sc['ceilings_passed']}/"
              f"{sc['target_ceilings']}  floors {sc['floors_passed']}/2"
              + (f"  re-read: {', '.join(flips)}" if flips else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
