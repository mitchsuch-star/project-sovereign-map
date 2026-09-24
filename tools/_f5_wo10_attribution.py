"""F5 — attribute the re-measured WO slice-10 board pins to the F5 levers.

    .venv/Scripts/python.exe tools/_f5_wo10_attribution.py

Runs `tests/test_wo_slice10_enemy_direction_gate.py`'s own ambient and
cooldown probes in hash-pinned children — exactly as its `_spawn` does — with
the file's three gate levers set from the flags AND the two F5 levers set
DOWN, and prints the seams / pairs / series / cooldowns each arm reads. The
claim the pins carry ("with the two F5 levers down in the child the prior
figures return") is what this measures.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

F5_DOWN = (
    "import backend.ai.enemy_ai as _EA_F5\n"
    "_EA_F5.ONE_WALK_IN_PER_CORPS_PER_TURN = False\n"
    "_EA_F5.THE_LITERAL_TAKES_THE_CAUTIOUS_STRENGTH_CHECK = False\n"
)


def spawn(probe: str, flags: str, marker: str, f5_down: bool) -> dict:
    import tests.test_wo_slice10_enemy_direction_gate as T
    env = dict(os.environ)
    env.update(PYTHONHASHSEED="0", PYTHONPATH=str(ROOT),
               SOVEREIGN_SEED="historical", LLM_MODE="mock")
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING"):
        env.pop(key, None)
    code = "import sys\n" + T._LEVER_PRELUDE + (F5_DOWN if f5_down else "") + probe
    proc = subprocess.run([sys.executable, "-c", code, flags], env=env, cwd=str(ROOT),
                          capture_output=True, text=True, timeout=900)
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    return json.loads(proc.stdout.split(marker)[-1].splitlines()[0])


def main() -> int:
    import tests.test_wo_slice10_enemy_direction_gate as T
    for f5_down in (True, False):
        label = "F5 levers DOWN" if f5_down else "shipped"
        ungated = spawn(T._AMBIENT_PROBE, "000", "WO10=", f5_down)
        seams: dict = {}
        for name, _q, _m in ungated["hits"]:
            seams[name] = seams.get(name, 0) + 1
        pairs = Counter((q, m) for _s, q, m in ungated["hits"])
        print(f"[{label}] ungated seams:", seams)
        print(f"[{label}] ungated pairs:", dict(pairs))
        print(f"[{label}] ungated series:", ungated["series"])
        cool_u = spawn(T._COOLDOWN_PROBE, "000", "WO10C=", f5_down)["writes"]
        cool_g = spawn(T._COOLDOWN_PROBE, "111", "WO10C=", f5_down)["writes"]
        print(f"[{label}] cooldowns: ungated {cool_u} gated {cool_g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
