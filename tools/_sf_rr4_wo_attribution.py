"""SF-RR4 (Score Finish residue 3, October 21, 2026 — war, truce and the
standing order; EG-D3's bench) — attribute the re-measured WO slice-10 gated
count (one more link in the chain `tools/_pc_s14p3_wo_attribution.py` → …).

    .venv/Scripts/python.exe tools/_sf_rr4_wo_attribution.py

Runs the slice-10 file's own cooldown probe in hash-pinned children, exactly
as its runner does: on the shipped tree; with the bench held DOWN in the child
(the data lever B of `tools/_sf_rr4_series_arms.py` — the three courts' pools
emptied at the boot); with the backtrack veto held down (J); and with every
seam of the slice held down (the series tool's LEVERS and DATA_LEVERS). The
claim the re-seated pin carries — "with every SF-RR4 seam down S14 part 3's
figure returns" — is what this measures. Writes
tools/_sf_rr4_wo_attribution.json.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _arms():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_sf_rr4_series_arms", ROOT / "tools" / "_sf_rr4_series_arms.py")
    arms = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(arms)
    return arms


def _preamble(keys) -> str:
    arms = _arms()
    lines = []
    for i, key in enumerate(sorted(keys)):
        if key in arms.DATA_LEVERS:
            lines.append(arms.DATA_LEVERS[key])
            continue
        module, name, down = arms.LEVERS[key]
        lines.append(f"import {module} as _M{i}\n_M{i}.{name} = lambda *a, **k: {down}\n")
    return "".join(lines)


def child_env() -> dict:
    env = dict(os.environ)
    env.update(PYTHONHASHSEED="0", PYTHONPATH=str(ROOT),
               SOVEREIGN_SEED="historical", LLM_MODE="mock")
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING",
                "PYTHONDONTWRITEBYTECODE"):
        env.pop(key, None)
    return env


def spawn(down_keys) -> int:
    import tests.test_wo_slice10_enemy_direction_gate as T
    code = _preamble(down_keys) + T._COOLDOWN_PROBE
    proc = subprocess.run([sys.executable, "-c", code], env=child_env(),
                          cwd=str(ROOT), capture_output=True, text=True,
                          encoding="utf-8", errors="replace",
                          timeout=1800)
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    return json.loads(proc.stdout.split("WO10C=")[-1].splitlines()[0])["writes"]


def main() -> int:
    arms = _arms()
    every = tuple(arms.LEVERS) + tuple(arms.DATA_LEVERS)
    out = {"gated_shipped": spawn(()), "gated_bench_down": spawn(("B",)),
           "gated_backtrack_veto_down": spawn(("J",)),
           "gated_every_rr4_seam_down": spawn(every)}
    print(out)
    (ROOT / "tools" / "_sf_rr4_wo_attribution.json").write_text(
        json.dumps(out, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
