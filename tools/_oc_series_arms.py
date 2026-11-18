"""Row OC — "the rulings built" — the BASELINE_SERIES attribution (November
18, 2026): which of the session's rows moves the ambient forty-turn series
(`tests/test_ai_intent_threat_migration.py --emit-series`, the idle France on
the historical seed). Every seam of the session is wrapped in the child and
its reads COUNTED (an arm whose seam never bites cannot pass for a
byte-identical one). The prior is HEAD's `BASELINE_SERIES` (never the working
tree's), the S14k rig's rule.

Arms: `0` — every row of `tests/_oc_seams.py` down (the tree before the
session: must reproduce the prior byte for byte); `ALL` — the shipped tree
(the re-pin's value); `+<ROW>` — that row alone up, the others down.

    .venv/Scripts/python.exe tools/_oc_series_arms.py [--arms 0,ALL,+USED] [--jobs 5]

Writes tools/_oc_series_arms_final.json (a re-run writes its own via --out).
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tests" / "test_ai_intent_threat_migration.py"
sys.path.insert(0, str(ROOT))
from tests._oc_seams import OC_SEAMS_BY_ROW  # noqa: E402

ROWS = list(OC_SEAMS_BY_ROW)


def _arms() -> dict:
    arms = {"0": set(ROWS), "ALL": set()}
    for row in ROWS:
        arms["+" + row] = set(ROWS) - {row}
    return arms


ARMS = _arms()

CHILD = r"""
import sys, runpy, atexit, collections, importlib
ROWS = {rows!r}
DOWN = set({down!r})
_c = collections.Counter()
def _wrap(module, name, row):
    mod = importlib.import_module(module)
    real = getattr(mod, name)
    def seam():
        _c[f"{{row}}:{{name}}"] += 1
        return False if row in DOWN else real()
    setattr(mod, name, seam)
for row, specs in ROWS.items():
    for spec in specs:
        target = spec.split("=", 1)[0]
        module, name = target.split(":", 1)
        _wrap(module, name, row)
def _dump():
    print("REACH=" + repr(dict(_c)))
atexit.register(_dump)
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""


def run_arm(down: set) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING",
              "PYTHONDONTWRITEBYTECODE", "INK_IRON_SEAMS"):
        env.pop(k, None)
    rows = {r: list(OC_SEAMS_BY_ROW[r]) for r in ROWS}
    code = CHILD.format(rows=rows, down=sorted(down), runner=str(RUNNER))
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, timeout=3600)
    stdout = proc.stdout.decode("utf-8", errors="replace")
    stderr = proc.stderr.decode("utf-8", errors="replace")
    if proc.returncode != 0:
        raise SystemExit(f"arm failed:\n{stdout[-2000:]}\n{stderr[-3000:]}")
    lines = stdout.splitlines()
    payload = json.loads([ln for ln in lines if ln.startswith("PAYLOAD=")][-1][len("PAYLOAD="):])
    counts = [ln for ln in lines if ln.startswith("REACH=")]
    payload["reach"] = ast.literal_eval(counts[-1].split("=", 1)[1]) if counts else None
    return payload


def first_divergence(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return None if len(a) == len(b) else min(len(a), len(b))


def prior_series(git_root: str = str(ROOT)) -> list:
    """HEAD's `BASELINE_SERIES`, read from `git_root` (the repository a frozen
    copy was taken from)."""
    rel = RUNNER.relative_to(ROOT).as_posix()
    text = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=git_root,
                          capture_output=True, check=True).stdout.decode("utf-8")
    m = re.search(r"^BASELINE_SERIES = (\[[^\]]*\])", text, re.M)
    return json.loads(m.group(1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--jobs", type=int, default=5)
    ap.add_argument("--out", default=str(ROOT / "tools" / "_oc_series_arms_final.json"))
    ap.add_argument("--git", default=str(ROOT), help="the repository whose HEAD holds the prior")
    args = ap.parse_args()
    prior = prior_series(args.git)
    names = [x.strip() for x in args.arms.split(",") if x.strip()]
    out = {"prior": prior, "rows": ROWS, "seams_down": {k: sorted(ARMS[k]) for k in names}, "arms": {}}
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = dict(zip(names, pool.map(lambda a: run_arm(ARMS[a]), names)))
    for arm in names:
        payload = results[arm]
        series = payload["series"]
        out["arms"][arm] = {"down": sorted(ARMS[arm]), "series": series,
                            "first_divergence_vs_prior": first_divergence(series, prior),
                            "reach": payload.get("reach")}
        print(f"arm {arm:>9}: divergence vs prior {out['arms'][arm]['first_divergence_vs_prior']}", flush=True)
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
