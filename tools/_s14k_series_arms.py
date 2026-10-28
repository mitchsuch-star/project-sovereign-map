"""S14k — the courts take the field: which row moves the ambient series, and
where.

    .venv/Scripts/python.exe tools/_s14k_series_arms.py --rows K1,K2,K3,K4,K5 --out tools/_s14k_p1_series_arms_final.json
    .venv/Scripts/python.exe tools/_s14k_series_arms.py --rows G1,G2,G3 --out tools/_s14k_p2_series_arms_final.json

Each arm is the shipped tree with a set of the slice's SEAMS held down in the
child (the driver's `--seam MODULE:NAME=EXPR` idiom: the seam becomes
`lambda *a, **k: EXPR`), then the `--emit-series` loop of
`tests/test_ai_intent_threat_migration.py`. Arm "0" holds every row down and
must reproduce the series before S14k byte for byte (the prior is read from
HEAD's `BASELINE_SERIES`, never the working tree's); a lettered arm holds ONE
row's seams down; "ALL" holds none (the shipped series). The rows are the ones
`tests/_oct27_seams.py` lists under S14k, so the recorded boards and this rig
hold the same switches — the content rows (K1 the 1805 field corps, K2 the
benches) are held down at the boot by their own seams, never by editing the
scenario. The S14j rig (`tools/_s14j_series_arms.py`) is the template; only
the registry differs.
"""
from __future__ import annotations

import argparse
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
from tests._oct27_seams import S14K_SEAMS_BY_ROW  # noqa: E402


def arms_for(rows: list) -> dict:
    """Arm "0" holds `rows` down (the series before them), one arm per row,
    "ALL" none."""
    return {"0": sorted(rows), "ALL": [], **{row: [row] for row in rows}}


ARMS = arms_for(list(S14K_SEAMS_BY_ROW))

CHILD = r"""
import importlib, runpy, sys
SPECS = {specs!r}
for spec in SPECS:
    target, expr = spec.split("=", 1)
    module_name, attr = target.split(":", 1)
    owner = importlib.import_module(module_name)
    *path, name = attr.split(".")
    for step in path:
        owner = getattr(owner, step)
    assert callable(getattr(owner, name)), spec
    setattr(owner, name, eval("lambda *a, **k: " + expr.strip(), {{}}))
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""


def run_arm(rows: list) -> dict:
    specs = [spec for row in rows for spec in S14K_SEAMS_BY_ROW[row]]
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING", "PYTHONDONTWRITEBYTECODE"):
        env.pop(k, None)
    code = CHILD.format(specs=specs, runner=str(RUNNER))
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, timeout=3600)
    stdout = proc.stdout.decode("utf-8", errors="replace")
    if proc.returncode != 0:
        raise SystemExit(f"arm {rows} failed:\n{stdout[-2000:]}\n"
                         f"{proc.stderr.decode('utf-8', errors='replace')[-3000:]}")
    line = [ln for ln in stdout.splitlines() if ln.startswith("PAYLOAD=")][-1]
    return json.loads(line[len("PAYLOAD="):])


def first_divergence(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return None if len(a) == len(b) else min(len(a), len(b))


def prior_series() -> list:
    rel = RUNNER.relative_to(ROOT).as_posix()
    text = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=str(ROOT),
                          capture_output=True, check=True).stdout.decode("utf-8")
    m = re.search(r"^BASELINE_SERIES = (\[[^\]]*\])", text, re.M)
    return json.loads(m.group(1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", default=",".join(S14K_SEAMS_BY_ROW),
                    help="the rows in play (K1..K5)")
    ap.add_argument("--arms", default="")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    global ARMS
    ARMS = arms_for([r.strip() for r in args.rows.split(",") if r.strip()])
    if not args.arms:
        args.arms = ",".join(ARMS)
    prior = prior_series()
    names = [x.strip() for x in args.arms.split(",") if x.strip()]
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = dict(zip(names, pool.map(lambda a: run_arm(ARMS[a]), names)))
    shipped = results["ALL"]["series"] if "ALL" in results else None
    out = {"prior": prior, "seams_down": {k: ARMS[k] for k in names}, "arms": {}}
    for arm in names:
        series = results[arm]["series"]
        out["arms"][arm] = {"down": ARMS[arm], "series": series,
                            "first_divergence_vs_prior": first_divergence(series, prior),
                            "first_divergence_vs_shipped": (first_divergence(series, shipped)
                                                            if shipped is not None else None)}
        print(f"arm {arm:>5}: divergence vs prior {out['arms'][arm]['first_divergence_vs_prior']}"
              f"  vs shipped {out['arms'][arm]['first_divergence_vs_shipped']}", flush=True)
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
