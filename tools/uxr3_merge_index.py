"""UXR-3 — merge a re-shoot (or a re-probe) into a whole-manifest record
(Pre-Deploy S12, October 13, 2026).

    .venv/Scripts/python.exe -X utf8 tools/uxr3_merge_index.py index \
        --base <run>/index.json --with <reshoot>/index.json --why "<reason>" --out <merged>/index.json
    .venv/Scripts/python.exe -X utf8 tools/uxr3_merge_index.py probe \
        --base <probe>/probe.json --with <reprobe>/probe.json --why "<reason>" --out <merged>/probe.json

A re-read shoots the whole manifest once, then re-shoots only the scenes a
later fix touched (`iq10_run_captures.py --only …`, one engine), and merges the
re-shot surfaces into a fresh whole-manifest index: every row of the re-shoot
replaces the base's rows of the same surface, at every resolution. The merged
record says which surfaces came from where and why (`reshoot`), and the commit
each was shot on, so nobody has to trust a label. The probe merges the same way,
surface by surface.

S11 did this by hand for the main menu (`docs/audits/uxr3/` records, the
`reshoot` block); this is that step as a tool.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys


def load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def merge_index(base: dict, extra: dict, why: str, extra_path: str) -> dict:
    replaced = sorted({str(r.get("base_id") or r.get("id")) for r in extra.get("rows", [])})
    keep = [r for r in base.get("rows", []) if str(r.get("base_id") or r.get("id")) not in replaced]
    rows = keep + list(extra.get("rows", []))
    order = {str(r.get("id")): i for i, r in enumerate(base.get("rows", []))}
    rows.sort(key=lambda r: order.get(str(r.get("id")), len(order)))
    out = dict(base, rows=rows)
    out["script_errors"] = list(base.get("script_errors") or []) + list(extra.get("script_errors") or [])
    out["exit_code"] = max(int(base.get("exit_code") or 0), int(extra.get("exit_code") or 0))
    out.setdefault("reshoots", [])
    out["reshoots"] = list(out["reshoots"]) + [{
        "source": extra_path, "surfaces": replaced, "why": why,
        "client_commit": extra.get("client_commit", ""), "base_commit": base.get("client_commit", "")}]
    return out


def merge_probe(base: dict, extra: dict, why: str, extra_path: str) -> dict:
    shots = dict(base.get("shots") or {})
    replaced = sorted((extra.get("shots") or {}).keys())
    shots.update(extra.get("shots") or {})
    out = dict(base, shots=shots)
    out["crashes"] = list(base.get("crashes") or []) + list(extra.get("crashes") or [])
    out.setdefault("reprobes", [])
    out["reprobes"] = list(out["reprobes"]) + [{
        "source": extra_path, "surfaces": replaced, "why": why,
        "client_commit": extra.get("client_commit", ""), "base_commit": base.get("client_commit", "")}]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=("index", "probe"))
    ap.add_argument("--base", required=True)
    ap.add_argument("--with", dest="extra", required=True)
    ap.add_argument("--why", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    base, extra = load(pathlib.Path(args.base)), load(pathlib.Path(args.extra))
    fn = merge_index if args.kind == "index" else merge_probe
    out = fn(base, extra, args.why, str(pathlib.Path(args.extra)).replace("\\", "/"))
    path = pathlib.Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    last = out["reshoots" if args.kind == "index" else "reprobes"][-1]
    print(f"merged {len(last['surfaces'])} surface(s) from {last['source']} "
          f"(commit {last['client_commit'] or '?'}) into {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
