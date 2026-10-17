"""S13e part 3 (Pre-Deploy, October 16, 2026) — attribute the re-measured WO
slice-10 gated count to the peace rulings' twelve seams (PC-R4 / R5 / R6 and
the F-rows; one more link in the chain `tools/_ddb_x3_wo_attribution.py`
→ `tools/_econ_gate_wo_attribution.py` → …).

    .venv/Scripts/python.exe tools/_pc_s13e3_wo_attribution.py

Runs the slice-10 file's own cooldown probe in hash-pinned children, exactly
as its runner does, twice: once on the shipped tree, and once with part 3's
twelve seams set DOWN in the child before the world boots — the same
expressions the Step 7 page's driven pin holds down (`SEAMS_DOWN` in
`tests/test_sf_page_the_front_page_of_the_peace.py`; the source is never
written). The claim the re-seated pin carries — "with part 3's seams down
DDB-X3's figure returns" — is what this measures.
Writes tools/_pc_s13e3_wo_attribution.json.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PART3_SEAMS = {
    "backend.game_logic.settlement_scoring:court_own_pressure",
    "backend.game_logic.settlement_baseline:stake_floor_consults",
    "backend.game_logic.ai_diplomacy:letter_consenting_courts",
    "backend.game_logic.ai_diplomacy:letter_writer_and_score",
    "backend.game_logic.coalition:exhaustion_clock_terms",
    "backend.game_logic.ai_diplomacy:p2_league_gate",
    "backend.game_logic.diplomacy:battle_score_from_records",
    "backend.game_logic.diplomacy:defense_ticking_gain",
    "backend.game_logic.diplomacy:acceptance_reads_the_field",
    "backend.game_logic.naval:posture_blockade_answered",
    "backend.game_logic.settlement_third_party:silent_band_white_peace",
    "backend.game_logic.settlement_helpers:newcomer_joins_the_war",
}


def seams_down_preamble() -> str:
    """The twelve `MODULE:NAME=EXPR` seams as a child preamble: each becomes
    `MODULE.NAME = lambda *a, **k: EXPR`, the driver's own reading."""
    import tests.test_sf_page_the_front_page_of_the_peace as SF
    lines = []
    for spec in SF.SEAMS_DOWN:
        target, expr = spec.split("=", 1)
        if target not in PART3_SEAMS:
            continue
        module, name = target.split(":")
        i = len(lines)
        lines.append(f"import {module} as _M{i}\n_M{i}.{name} = lambda *a, **k: {expr}\n")
    assert len(lines) == len(PART3_SEAMS), len(lines)
    return "".join(lines)


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
    code = (seams_down_preamble() if down else "") + T._COOLDOWN_PROBE
    proc = subprocess.run([sys.executable, "-c", code], env=child_env(),
                          cwd=str(ROOT), capture_output=True, text=True,
                          encoding="utf-8", errors="replace",
                          timeout=1800)
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    return json.loads(proc.stdout.split("WO10C=")[-1].splitlines()[0])["writes"]


def main() -> int:
    out = {"gated_shipped": spawn(False), "gated_part3_seams_down": spawn(True)}
    print(out)
    (ROOT / "tools" / "_pc_s13e3_wo_attribution.json").write_text(
        json.dumps(out, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
