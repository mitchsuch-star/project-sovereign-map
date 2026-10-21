"""S14 part 3 (Pre-Deploy, October 20, 2026 — the league's bond, Chaumont) —
attribute the re-measured WO slice-10 gated count to the bond (one more link
in the chain `tools/_pc_s13e3_wo_attribution.py` → `tools/_ddb_x3_wo_attribution.py`
→ …).

    .venv/Scripts/python.exe tools/_pc_s14p3_wo_attribution.py

Runs the slice-10 file's own cooldown probe in hash-pinned children, exactly
as its runner does, three times: on the shipped tree; with the bond's AI mint
held DOWN in the child (`bond.ai_paymaster_binds` → [] — no bond is ever
minted, so every read of one is inert); and with every seam of the part held
down (the series tool's LEVERS, `tools/_pc_s14p3_series_arms.py`). The claim
the re-seated pin carries — "with the bond's mint down S13e part 3's figure
returns" — is what this measures. Writes tools/_pc_s14p3_wo_attribution.json.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _preamble(keys) -> str:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_pc_s14p3_series_arms", ROOT / "tools" / "_pc_s14p3_series_arms.py")
    arms = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(arms)
    lines = []
    for i, key in enumerate(sorted(keys)):
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
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_pc_s14p3_series_arms", ROOT / "tools" / "_pc_s14p3_series_arms.py")
    arms = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(arms)
    out = {"gated_shipped": spawn(()), "gated_bond_mint_down": spawn(("B",)),
           "gated_every_bond_seam_down": spawn(tuple(arms.LEVERS))}
    print(out)
    (ROOT / "tools" / "_pc_s14p3_wo_attribution.json").write_text(
        json.dumps(out, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
