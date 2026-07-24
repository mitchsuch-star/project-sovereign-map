"""AI-4a steps 1-4 — the threat_by_target additive migration (Stage C).

docs/AI_INTENT_SPEC.md §4.4a: the migration is ADDITIVE, not a rewrite.

  1. `world.threat_by_target: dict[str, int]`; `add_threat`/`reduce_threat`
     gain an optional `target` defaulting to the player. Every existing
     call site keeps its exact behaviour.
  2. `threat_level` is a PROPERTY over the player's slot (the `gold`
     property idiom) — all 73 backend reads and 10 .gd reads unchanged.
  3. `threat_sources_this_turn` entries gain a `target` key; legacy
     entries without one default to the player on read. `from_dict`
     seeds the dict from a legacy scalar; `to_dict` writes both.
  4. THE PIN: a boot world + 40-turn run produce a byte-identical
     `threat_level` series before and after the migration, at fixed
     ambient RNG (per-turn `random.seed(10_000 + turn)`, the M7 idiom),
     `SOVEREIGN_SEED=historical` and `PYTHONHASHSEED=0` (set iteration
     order feeds AI decisions — without the hash pin the ambient sim is
     process-unstable, which is pin 14(c)'s "no campaign replay" clause
     observed in the wild).

Steps 5-6 (producer migration + decay re-key) are Stage D. Until they
land, NO production caller passes a non-player target, and every
non-player slot is structurally 0 — asserted here.

The recorded series below was measured on master @ d1be956 BEFORE the
migration was applied, then re-measured after: byte-identical. Any later
slice that legitimately changes AI-diplomacy behaviour (the Stage C rung
rework does) re-records the constant CONSCIOUSLY with a note beside it.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from backend.game_logic.coalition import add_threat, reduce_threat
from backend.models.world_state import WorldState

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO_ROOT / "godot-client" / "project-sovereign"
                 / "assets" / "maps" / "europe_1805.json")

# Measured on master @ d1be956 (pre-migration), re-measured identical
# post-migration (steps 1-4) — the §4.4a step-4 gate held: the
# migration alone changed NOTHING. Byte-identical baseline of record:
# [85, 86, 84, 82, 80, 77, 74, 71, 68, 65, 62, 59, 46, 43, 40, 45, 42,
#  39, 36, 41, 38, 35, 32, 40, 37, 34, 31, 37, 45, 42, 42, 42, 45, 45,
#  42, 42, 45, 45, 42, 42, 45]
# Then RE-RECORDED CONSCIOUSLY at the Stage C rung rework, same
# session: AI-2's intent-driven rungs (P-Intent before P3, the AI-AI
# design/alignment triggers, the sponsor branch) legitimately change
# what the courts do each turn, which feeds relations, bloc shares and
# the coalition tick. The pin's job from here is to catch UNINTENDED
# drift between slices.
BASELINE_SERIES = [
    85, 86, 84, 82, 80, 77, 74, 71, 68, 65, 62, 59, 46, 43, 40, 48, 53,
    50, 47, 52, 49, 46, 43, 43, 40, 37, 34, 39, 36, 33, 33, 30, 27, 27,
    27, 24, 24, 21, 21, 21, 18,
]


def _run_series_subprocess() -> dict:
    """Run the 40-turn ambient sim in a hash-pinned subprocess."""
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    env.pop("SOVEREIGN_SCENARIO", None)
    env.pop("SOVEREIGN_MAP", None)
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--emit-series"],
        env=env, cwd=str(REPO_ROOT), capture_output=True, text=True,
        timeout=300,
    )
    assert result.returncode == 0, (
        f"series runner failed:\n{result.stdout[-2000:]}\n"
        f"{result.stderr[-2000:]}")
    payload_line = [ln for ln in result.stdout.splitlines()
                    if ln.startswith("PAYLOAD=")][-1]
    return json.loads(payload_line[len("PAYLOAD="):])


class TestStep4SeriesPin:
    """§4.4a step 4 — the byte-identical 40-turn series."""

    @pytest.fixture(scope="class")
    def payload(self):
        return _run_series_subprocess()

    def test_series_matches_recorded_baseline(self, payload):
        assert payload["series"] == BASELINE_SERIES

    def test_no_nonplayer_slot_ever_accrues(self, payload):
        """Steps 5-6 have not landed: every non-player slot is 0 after
        40 ambient turns — no producer passes a target."""
        tbt = payload["threat_by_target"]
        for nation, value in tbt.items():
            if nation != "France":
                assert value == 0, f"{nation} slot accrued {value}"

    def test_scalar_mirrors_player_slot_throughout(self, payload):
        assert payload["scalar_mirror_ok"] is True


class TestStep2Property:
    """threat_level is a view over the player's slot."""

    def test_read_is_player_slot(self):
        world = WorldState(player_nation="France")
        world.threat_by_target["France"] = 37
        assert world.threat_level == 37

    def test_write_is_player_slot(self):
        world = WorldState(player_nation="France")
        world.threat_level = 44
        assert world.threat_by_target["France"] == 44

    def test_missing_slot_reads_zero(self):
        world = WorldState(player_nation="France")
        world.threat_by_target = {}
        assert world.threat_level == 0

    def test_augmented_assignment_works(self):
        world = WorldState(player_nation="France")
        world.threat_level = 10
        world.threat_level += 5
        assert world.threat_level == 15
        assert world.threat_by_target["France"] == 15


class TestStep1TargetParameter:
    """add_threat/reduce_threat optional target, default player."""

    def test_default_target_is_byte_identical_player_arm(self):
        world = WorldState(player_nation="France")
        world.threat_level = 10
        new = add_threat(world, 5, "battle_win")
        assert new == 15
        assert world.threat_level == 15
        entry = world.threat_sources_this_turn[-1]
        assert entry["source"] == "battle_win"
        assert entry["amount"] == 5
        assert entry["target"] == "France"
        assert world.positive_threat_delta_this_turn is True

    def test_explicit_nonplayer_target_writes_its_own_slot(self):
        world = WorldState(player_nation="France")
        world.threat_level = 10
        new = add_threat(world, 7, "battle_win", target="Austria")
        assert new == 7
        assert world.threat_by_target["Austria"] == 7
        assert world.threat_level == 10  # player slot untouched
        entry = world.threat_sources_this_turn[-1]
        assert entry["target"] == "Austria"

    def test_nonplayer_target_does_not_set_player_pressure_flag(self):
        """positive_threat_delta_this_turn backs a FRANCE-threat anti-spam
        gate — a foreign slot rising must not trip it."""
        world = WorldState(player_nation="France")
        world.positive_threat_delta_this_turn = False
        add_threat(world, 7, "battle_win", target="Austria")
        assert world.positive_threat_delta_this_turn is False
        add_threat(world, 3, "battle_win")
        assert world.positive_threat_delta_this_turn is True

    def test_reduce_threat_target_arm(self):
        world = WorldState(player_nation="France")
        world.threat_by_target["Austria"] = 20
        new = reduce_threat(world, 6, "generous_peace", target="Austria")
        assert new == 14
        assert world.threat_by_target["Austria"] == 14
        entry = world.threat_sources_this_turn[-1]
        assert entry["amount"] == -6
        assert entry["target"] == "Austria"

    def test_per_slot_clamp(self):
        world = WorldState(player_nation="France")
        add_threat(world, 250, "capital_capture", target="Austria")
        assert world.threat_by_target["Austria"] == 100
        reduce_threat(world, 250, "generous_peace", target="Austria")
        assert world.threat_by_target["Austria"] == 0

    def test_zero_amount_noop_returns_target_slot(self):
        world = WorldState(player_nation="France")
        world.threat_by_target["Austria"] = 9
        assert add_threat(world, 0, "x", target="Austria") == 9
        assert reduce_threat(world, -3, "x", target="Austria") == 9
        assert world.threat_sources_this_turn == []


class TestStep3Serialization:
    """to_dict writes both; from_dict migrates a legacy scalar."""

    def test_round_trip_preserves_nonplayer_slots(self):
        world = WorldState(player_nation="France")
        world.threat_level = 42
        world.threat_by_target["Austria"] = 17
        restored = WorldState.from_dict(world.to_dict())
        assert restored.threat_level == 42
        assert restored.threat_by_target["Austria"] == 17

    def test_to_dict_writes_both_forms(self):
        world = WorldState(player_nation="France")
        world.threat_level = 33
        data = world.to_dict()
        assert data["threat_level"] == 33
        assert data["threat_by_target"]["France"] == 33

    def test_legacy_scalar_only_save_seeds_player_slot(self):
        world = WorldState(player_nation="France")
        world.threat_level = 55
        data = world.to_dict()
        data.pop("threat_by_target")
        restored = WorldState.from_dict(data)
        assert restored.threat_level == 55
        assert restored.threat_by_target["France"] == 55

    def test_missing_both_reads_zero(self):
        world = WorldState(player_nation="France")
        data = world.to_dict()
        data.pop("threat_by_target")
        data.pop("threat_level")
        restored = WorldState.from_dict(data)
        assert restored.threat_level == 0

    def test_legacy_entry_without_target_survives_round_trip(self):
        """A legacy save's source entries have no target key — they load
        unchanged (readers default to the player at read time)."""
        world = WorldState(player_nation="France")
        world.threat_sources_this_turn = [
            {"source": "battle_win", "amount": 3}]
        restored = WorldState.from_dict(world.to_dict())
        assert restored.threat_sources_this_turn == [
            {"source": "battle_win", "amount": 3}]


def _emit_series() -> None:
    """The subprocess runner (invoked with --emit-series)."""
    import random

    from backend.commands.executor import CommandExecutor
    from backend.game_logic.turn_manager import TurnManager

    world = WorldState.from_scenario(str(SCENARIO_PATH))
    executor = CommandExecutor()
    tm = TurnManager(world, executor=executor)
    game_state = {"world": world, "executor": executor}

    series = [int(world.threat_level)]
    mirror_ok = (world.threat_level
                 == world.threat_by_target.get(world.player_nation, 0))
    for turn in range(40):
        random.seed(10_000 + turn)  # the M7 per-turn re-seed idiom
        tm.end_turn(game_state)
        series.append(int(world.threat_level))
        if (world.threat_level
                != world.threat_by_target.get(world.player_nation, 0)):
            mirror_ok = False
    print("PAYLOAD=" + json.dumps({
        "series": series,
        "threat_by_target": {
            str(k): int(v) for k, v in world.threat_by_target.items()},
        "scalar_mirror_ok": bool(mirror_ok),
    }))


if __name__ == "__main__":
    if "--emit-series" in sys.argv:
        sys.path.insert(0, str(REPO_ROOT))
        _emit_series()
