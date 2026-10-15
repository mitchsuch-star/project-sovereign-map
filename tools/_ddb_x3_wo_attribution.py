"""DDB-X3 (Pre-Deploy S13b part 3, October 15, 2026) — attribute the
re-measured WO slice-10 gated count to the AI's retreat onto an ally's soil
(one more link in the economy gate's chain, `tools/_econ_gate_wo_attribution.py`).

    .venv/Scripts/python.exe tools/_ddb_x3_wo_attribution.py

Runs the slice-10 file's own cooldown probe in hash-pinned children, exactly
as its runner does, twice: once on the shipped tree, and once with DDB-X3's
seam (`enemy_ai.ai_retreat_soil_is_friendly`) set DOWN in the child before
the world boots — own soil only, the pre-slice read (the source is never
written). The claim the re-seated pin carries — "with DDB-X3's seam down the
economy gate's figure returns" — is what this measures.
Writes tools/_ddb_x3_wo_attribution.json.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

X3_DOWN = ("import backend.ai.enemy_ai as _EA\n"
           "_EA.ai_retreat_soil_is_friendly = "
           "lambda world, nation, controller: controller == nation\n")


def child_env() -> dict:
    env = dict(os.environ)
    env.update(PYTHONHASHSEED="0", PYTHONPATH=str(ROOT),
               SOVEREIGN_SEED="historical", LLM_MODE="mock")
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING",
                "PYTHONDONTWRITEBYTECODE"):
        env.pop(key, None)
    return env


def spawn(down: bool) -> int:
    import tests.test_wo_slice10_enemy_direction_gate as T
    code = (X3_DOWN if down else "") + T._COOLDOWN_PROBE
    proc = subprocess.run([sys.executable, "-c", code], env=child_env(),
                          cwd=str(ROOT), capture_output=True, text=True,
                          encoding="utf-8", errors="replace",
                          timeout=1800)
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    return json.loads(proc.stdout.split("WO10C=")[-1].splitlines()[0])["writes"]


def main() -> int:
    out = {"gated_shipped": spawn(False), "gated_x3_down": spawn(True)}
    print(out)
    (ROOT / "tools" / "_ddb_x3_wo_attribution.json").write_text(
        json.dumps(out, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
