"""RS-27 (Score Finish Step 3, October 2, 2026) — the volte-face fires on
its own arm, DRIVEN.

Measured first: the bisect the row asked for named Chunk 1's SR-1d (the
league's offer moved t4 → t9, the courting past the window), and the
per-lever attribution on the VOLTE arm read all Step-3 levers DOWN → 0
(the baseline's miss reproduces) and the shipped tree → the beat at turn
21, with RS-3 (`A_FIELD_WIN_HALTS_BEFORE_THE_WORKS`) and the AI's odds gate
(`AI_ATTACKS_OBEY_THE_MUSTER_GATE`) each necessary (either alone down → 0):
the war's course on the arm changed, and the peace now lands where the
courting can reach the floor inside the window. The spec's own
disposition — "pin it firing on its arm or re-script the arm" — is the
first: the arm is unchanged and this pin drives it.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "tools" / "playtest_scripts" / "volte_court_austria.json"


def _drive(tmp_path, *extra):
    env = dict(os.environ, PYTHONHASHSEED="0", LLM_MODE="mock",
               SOVEREIGN_SEED="historical")
    env.pop("PYTHONIOENCODING", None)
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        env.pop(key, None)
    env["INK_IRON_SAVE_DIR"] = str(tmp_path / "saves")
    proc = subprocess.run(
        [sys.executable, str(REPO / "tools" / "playtest_driver.py"),
         "--script", str(SCRIPT), "--turns", "40", "--seed", "historical",
         "--out", str(tmp_path), *extra],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=900, env=env, cwd=str(REPO))
    runs = [p for p in tmp_path.iterdir() if (p / "digest.jsonl").is_file()]
    assert runs, proc.stderr[-2000:]
    rows = [json.loads(line) for line in
            (runs[0] / "digest.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    return rows


def _volte_turns(rows):
    turns = []
    turn = None
    for row in rows:
        if row.get("kind") == "turn" or "turn" in row and row.get("kind") in ("ledger", "enemy_phase"):
            turn = row.get("turn", turn)
        if row.get("kind") == "campaign_log" and row.get("dtype") == "volte_face":
            turns.append(int(row.get("log_turn") or turn or -1))
        elif row.get("kind") == "rail" and row.get("dtype") == "volte_face":
            turns.append(int(turn or -1))
    return turns


class TestTheVolteFaceFiresOnItsArm:
    def test_the_beat_fires_inside_the_window(self, tmp_path):
        rows = _drive(tmp_path)
        turns = _volte_turns(rows)
        assert turns, "the VOLTE arm raised no volte_face beat (RS-27)"
        assert min(t for t in turns if t >= 0) <= 31, turns   # the war ends ~t11; window 20

    def test_with_every_step3_lever_down_the_baselines_miss_reproduces(self, tmp_path):
        """The attribution's arm 0 — the row's own 'cause not isolated' is
        isolated: without Step 3's balance block the beat never fires here."""
        rows = _drive(
            tmp_path,
            "--lever", "backend.commands.combat_executor:A_FIELD_WIN_HALTS_BEFORE_THE_WORKS=0",
            "--lever", "backend.ai.enemy_ai:AI_ATTACKS_OBEY_THE_MUSTER_GATE=0",
            "--lever", "backend.ai.enemy_ai:A_HELD_CORPS_IS_NOT_IDLE=0",
            "--lever", "backend.game_logic.garrison_report:A_SMALL_GARRISON_SURRENDERS=0",
            "--lever", "backend.commands.tactical_executor:ONE_STANCE_RULE_FOR_DRILL=0",
            "--lever", "backend.commands.combat_executor:BLEED_BY_THE_MEN_COMMITTED=0",
            "--lever", "backend.commands.combat_executor:AN_IN_PLACE_CAPTURE_MARCHES_NOWHERE=0",
            "--lever", "backend.game_logic.coalition:THE_ARMED_PEACE=0",
            "--lever", "backend.models.world_state:DISPERSION_IS_NOT_PUNISHED=0",
        )
        assert not _volte_turns(rows)
