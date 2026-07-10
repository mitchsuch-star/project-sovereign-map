"""EC-6a sandbox toggle — S4, closes Economy Revisit Track 1 (spec §0.6.3).

The Europe campaign ships as an open-ended SANDBOX (EC-6 gate decision,
July 7, 2026): no hard win/lose at turn 60 or at the 0.75 region fraction.
Real victory conditions are owned by the Pre-Ship Victory & Objectives Pass
— do NOT re-enable the disabled victory code (`ECONOMY_REVISIT_SPEC.md` §2).

Pins (the S4 completion definition, spec §0.6.3):
- ENFORCEMENT: `_check_victory_conditions` early-returns game-continues on
  sandbox worlds (every branch: time defeat, time victory, total conquest,
  elimination, army-loss/territory-loss defeats) and `_check_enemy_victory`
  is a no-op. The guard is the FIRST statement, so the hidden FINAL-11 full
  region-scan (GR8 — ×2 per end_turn on 126 provinces) never runs.
- DISPLAY READERS gated with enforcement (never one without the other):
  `dispatch._build_turn_limit_warning` → None; `get_defeat_imminent_state`
  → None ("the campaign ends" would be a false promise); `get_turn_summary`
  omits the countdown keys; `get_action_summary` sends the max_turns=0
  open-ended sentinel and main.gd renders a bare turn number for it.
- AUTO-ADVANCE CONSISTENCY: `end_turn` past turn 60 keeps playing —
  `victory_check.game_over` stays False for the executor/meta_executor
  auto-advance readers.
- SAVE-COMPAT: `max_turns` round-trips untouched; sandbox is derived from
  the persisted `sovereign_map`, so old saves load straight into sandbox
  with no migration (the EC-0 pattern: derive, don't add a field).
- LEGACY worlds (the 19-region test fixture / rollback) keep ALL victory,
  defeat, and countdown behavior unchanged.
"""

import inspect
from pathlib import Path

import pytest

from backend.game_logic.dispatch import _build_turn_limit_warning
from backend.game_logic.turn_manager import TurnManager, get_defeat_imminent_state
from backend.models.world_state import VICTORY_REGION_FRACTION, WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
)

MAIN_GD_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "scripts" / "main.gd"
)


@pytest.fixture
def europe():
    """Bare Europe flag world — sovereign_map='europe', 126 provinces."""
    return WorldState(player_nation="France", sovereign_map="europe")


@pytest.fixture
def legacy():
    """The 19-region legacy fixture world — hard win/lose stays live here."""
    return WorldState(player_nation="France")


@pytest.fixture(scope="module")
def world1805():
    """Read-only module-scoped 1805 campaign — mutating tests copy it."""
    return WorldState.from_scenario(str(SCENARIO_PATH))


def _copy(world):
    """Cheap isolated copy through the serialization seam."""
    return WorldState.from_dict(world.to_dict())


def _give_regions(world, nation, count):
    """Assign the first `count` regions to `nation` (rest untouched) and
    invalidate the per-turn nation/region caches."""
    for i, region in enumerate(world.regions.values()):
        if i >= count:
            break
        region.controller = nation
    world.invalidate_active_nations_cache()


def _give_all_regions(world, nation):
    for region in world.regions.values():
        region.controller = nation
    world.invalidate_active_nations_cache()


# ══════════════════════════ the toggle itself ══════════════════════════


class TestSandboxToggle:
    def test_sandbox_mode_derived_from_sovereign_map(self, europe, legacy):
        assert europe.sandbox_mode is True
        assert legacy.sandbox_mode is False

    def test_1805_campaign_is_sandbox(self, world1805):
        assert world1805.sovereign_map == "europe"
        assert world1805.sandbox_mode is True
        # max_turns itself is untouched — only enforcement/readers are gated.
        assert world1805.max_turns == 60


# ══════════════════════ enforcement — europe sandbox ══════════════════════


class TestSandboxEnforcement:
    def test_no_time_defeat_at_turn_60(self, europe):
        """Pre-S4: turn 60 below the fraction = 'Time expired' DEFEAT."""
        europe.current_turn = europe.max_turns
        result = TurnManager(europe)._check_victory_conditions()
        assert result == {"game_over": False, "result": None, "reason": None}

    def test_no_time_victory_past_60_at_075_fraction(self, europe):
        """Pre-S4: >=0.75 fraction at max_turns = 'Survived' VICTORY."""
        threshold = int(len(europe.regions) * VICTORY_REGION_FRACTION)
        _give_regions(europe, "France", threshold + 5)
        europe.current_turn = europe.max_turns + 1
        result = TurnManager(europe)._check_victory_conditions()
        assert result["game_over"] is False

    def test_no_total_conquest_victory(self, europe):
        """Pre-S4: holding every region = total-conquest VICTORY."""
        _give_all_regions(europe, "France")
        result = TurnManager(europe)._check_victory_conditions()
        assert result["game_over"] is False

    def test_no_army_loss_defeat(self, europe):
        """Pre-S4: no living player marshal = 'All armies destroyed' DEFEAT."""
        for marshal in europe.get_player_marshals():
            marshal.strength = 0
        result = TurnManager(europe)._check_victory_conditions()
        assert result["game_over"] is False

    def test_no_zero_region_defeat(self, europe):
        """Pre-S4: 0 player regions = 'All territory lost' DEFEAT."""
        _give_all_regions(europe, "Austria")
        result = TurnManager(europe)._check_victory_conditions()
        assert result["game_over"] is False

    def test_no_enemy_conquest_victory(self, europe):
        """Pre-S4: an enemy above the fraction = enemy conquest end-screen."""
        threshold = int(len(europe.regions) * VICTORY_REGION_FRACTION)
        _give_regions(europe, "Austria", threshold + 5)
        assert TurnManager(europe)._check_enemy_victory() is None

    def test_1805_no_end_screen_at_turn_60(self, world1805):
        world = _copy(world1805)
        world.current_turn = 60
        tm = TurnManager(world)
        assert tm._check_victory_conditions()["game_over"] is False
        assert tm._check_enemy_victory() is None

    def test_1805_no_end_screen_at_075_fraction(self, world1805):
        world = _copy(world1805)
        threshold = int(len(world.regions) * VICTORY_REGION_FRACTION)
        _give_regions(world, "France", threshold + 5)
        world.current_turn = 61
        result = TurnManager(world)._check_victory_conditions()
        assert result["game_over"] is False
        assert world.game_over is False

    def test_guard_precedes_the_hidden_region_scan(self):
        """The early return must stay the FIRST statement — it is what kills
        the FINAL-11 `regions.values()` scan (GR8) and the region-index reads
        for sandbox worlds. Source-order pin (the S3 pattern)."""
        src = inspect.getsource(TurnManager._check_victory_conditions)
        guard = src.index("sandbox_mode")
        assert guard < src.index("get_player_regions")
        assert guard < src.index("regions.values()")


# ═══════════════════ display readers — europe sandbox ═══════════════════


class TestSandboxDisplayReaders:
    def test_no_turn_limit_warning_at_final_turn(self, europe):
        """remaining == 0 fired the 'FINAL TURN' critical warning pre-S4."""
        europe.current_turn = europe.max_turns
        assert _build_turn_limit_warning(europe, "France") is None

    def test_no_turn_limit_warning_at_five_remaining(self, europe):
        europe.current_turn = europe.max_turns - 4
        assert _build_turn_limit_warning(europe, "France") is None

    def test_no_turn_limit_warning_past_the_old_limit(self, europe):
        europe.current_turn = europe.max_turns + 3
        assert _build_turn_limit_warning(europe, "France") is None

    def test_no_defeat_imminent_warning(self, europe):
        """'If it falls, the campaign ends' is a false promise in sandbox —
        gated at the single source (get_defeat_imminent_state)."""
        # One-region France = the pre-S4 'One Region Remains' trigger.
        _give_all_regions(europe, "Austria")
        first = next(iter(europe.regions.values()))
        first.controller = "France"
        europe.invalidate_active_nations_cache()
        assert get_defeat_imminent_state(europe) is None

    def test_turn_summary_omits_countdown_keys(self, europe):
        europe.current_turn = europe.max_turns  # would read '0 remaining'
        summary = TurnManager(europe).get_turn_summary()
        assert "max_turns" not in summary
        assert "turns_remaining" not in summary
        # The non-countdown payload is intact.
        for key in ("turn", "gold", "regions", "game_over", "victory"):
            assert key in summary

    def test_action_summary_sends_open_ended_sentinel(self, europe):
        summary = europe.get_action_summary()
        assert summary["max_turns"] == 0
        assert isinstance(summary["max_turns"], int)  # Golden Rule 2

    def test_godot_turn_counter_gates_on_sentinel(self):
        """main.gd renders a bare turn number for the max_turns<=0 sentinel
        (never 'N/0' or a stale '61/60'). Source pin, PRE-EC .gd pattern."""
        src = MAIN_GD_PATH.read_text(encoding="utf-8")
        assert "if int(max_turns) <= 0:" in src
        assert "turn_value.text = str(int(current_turn))\n" in src


# ═══════════════════ auto-advance consistency (executor seam) ═══════════════════


class TestAutoAdvanceConsistency:
    def test_end_turn_past_60_keeps_playing(self, europe):
        """executor.py / meta_executor.py read victory_check.game_over on the
        auto-advance path — enforcement and that reader stay consistent."""
        europe.current_turn = europe.max_turns
        result = TurnManager(europe).end_turn(game_state=None)
        assert result["victory_check"]["game_over"] is False
        assert europe.game_over is False
        assert europe.current_turn == europe.max_turns + 1


# ══════════════════════════ save-compat ══════════════════════════


class TestSaveCompat:
    def test_max_turns_round_trips_and_sandbox_survives_load(self, europe):
        europe.current_turn = 60
        restored = WorldState.from_dict(europe.to_dict())
        assert restored.max_turns == 60
        assert restored.sandbox_mode is True
        result = TurnManager(restored)._check_victory_conditions()
        assert result["game_over"] is False

    def test_save_without_max_turns_key_still_boots_sandbox(self, europe):
        """Pre-EC-6a europe saves: derived toggle needs no migration."""
        data = europe.to_dict()
        data.pop("max_turns", None)
        restored = WorldState.from_dict(data)
        assert restored.max_turns == 60
        assert restored.sandbox_mode is True

    def test_legacy_round_trip_stays_hard_mode(self, legacy):
        restored = WorldState.from_dict(legacy.to_dict())
        assert restored.sandbox_mode is False
        assert restored.max_turns == 40


# ═══════════════ legacy control — hard win/lose unchanged ═══════════════


class TestLegacyUnchanged:
    def test_legacy_time_defeat_still_fires(self, legacy):
        legacy.current_turn = legacy.max_turns
        result = TurnManager(legacy)._check_victory_conditions()
        assert result["game_over"] is True
        assert result["result"] == "defeat"
        assert result["reason"] == "Time expired without achieving dominance"

    def test_legacy_time_victory_still_fires(self, legacy):
        threshold = int(len(legacy.regions) * VICTORY_REGION_FRACTION)
        # Above the fraction but below total conquest → the time-victory branch.
        _give_regions(legacy, "France", threshold + 1)
        legacy.current_turn = legacy.max_turns
        result = TurnManager(legacy)._check_victory_conditions()
        assert result["game_over"] is True
        assert result["result"] == "victory"

    def test_legacy_enemy_victory_still_fires(self, legacy):
        threshold = int(len(legacy.regions) * VICTORY_REGION_FRACTION)
        _give_regions(legacy, "Austria", threshold + 1)
        result = TurnManager(legacy)._check_enemy_victory()
        assert result is not None
        assert result["nation"] == "Austria"

    def test_legacy_turn_limit_warning_still_fires(self, legacy):
        legacy.current_turn = legacy.max_turns
        warning = _build_turn_limit_warning(legacy, "France")
        assert warning is not None
        assert warning["severity"] == "critical"

    def test_legacy_defeat_imminent_still_fires(self, legacy):
        living = [m for m in legacy.get_player_marshals() if m.strength > 0]
        for marshal in living[1:]:
            marshal.strength = 0
        state = get_defeat_imminent_state(legacy)
        assert state is not None
        assert state["living_marshal_count"] == 1

    def test_legacy_turn_summary_keeps_countdown(self, legacy):
        legacy.current_turn = 10
        summary = TurnManager(legacy).get_turn_summary()
        assert summary["max_turns"] == 40
        assert summary["turns_remaining"] == 30

    def test_legacy_action_summary_keeps_max_turns(self, legacy):
        assert legacy.get_action_summary()["max_turns"] == 40
