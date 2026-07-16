"""
Vassal Depth Slice 0 — Nation-neutral vassal substrate + VP-D1 garrison wire
(July 16, 2026; docs/VASSAL_DEEPENING_SPEC.md §8 build sequence, Slice 0).

Pins:
  1. invest_in_vassal / change_vassal_autonomy are lord-parameterized (GR5):
     an AI lord acts through the SAME functions, spending its own
     nation_dp / nation_gold — never the player's pools.
  2. change_vassal_autonomy gained a lord gate — pre-fix it had NONE and
     charged the player's DP unconditionally (a live footgun for any AI path).
  3. Coalition threat is player-scoped: AI vassalizations add none; an AI
     lord's rebellion reduces none.
  4. VP-D1: the garrison loyalty lever is WIRED — presence-based flat +2 via
     the single-source lord_garrison_present, symmetric for enemy lords.
  5. The executor honors _acting_nation + structured autonomy levels.
"""

import pytest

from backend.models.marshal import Marshal
from backend.models.world_state import WorldState
from backend.game_logic.vassal import (
    AUTONOMY_AUTONOMOUS,
    AUTONOMY_PUPPET,
    AUTONOMY_SATELLITE,
    GARRISON_LOYALTY_BONUS,
    TRIBUTE_RATES,
    change_vassal_autonomy,
    check_vassal_rebellion,
    create_vassal_conquest,
    create_vassal_treaty,
    invest_in_vassal,
    lord_garrison_present,
    process_vassal_loyalty,
    recovery_hint_for_grip,
)


def make_world():
    return WorldState()


def add_vassal(world, vassal="Saxony", lord="France", loyalty=60,
               autonomy=AUTONOMY_SATELLITE):
    world.vassals[vassal] = {
        "lord": lord,
        "loyalty": int(loyalty),
        "autonomy": int(autonomy),
        "path": "treaty",
        "created_turn": 1,
        "tribute_rate": TRIBUTE_RATES[autonomy],
        "carved_from": None,
        "regions": None,
    }
    key = world._make_diplo_key(lord, vassal)
    world.diplomatic_states[key] = "VASSAL"
    world.nation_relations[key] = 0
    world.invalidate_active_nations_cache()
    return world.vassals[vassal]


# ═══════════════════════════════════════════════════════
# 1. Nation-neutral invest (GR5)
# ═══════════════════════════════════════════════════════

class TestInvestNationNeutral:
    def test_ai_lord_invests_from_its_own_pools(self):
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="Prussia", loyalty=40)
        world.nation_dp = {"Prussia": 3}
        world.nation_gold["Prussia"] = 1000
        player_dp_before = world.diplomatic_points
        player_gold_before = world.nation_gold.get("France", 0)

        result = invest_in_vassal(world, "Saxony", actor="Prussia")

        assert result["success"], result["message"]
        assert world.vassals["Saxony"]["loyalty"] == 50
        assert world.nation_dp["Prussia"] == 2
        assert world.nation_gold["Prussia"] == 800
        # The player's pools are untouched
        assert world.diplomatic_points == player_dp_before
        assert world.nation_gold.get("France", 0) == player_gold_before

    def test_ai_cannot_invest_in_anothers_vassal(self):
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="France", loyalty=40)
        world.nation_dp = {"Prussia": 3}
        world.nation_gold["Prussia"] = 1000

        result = invest_in_vassal(world, "Saxony", actor="Prussia")

        assert not result["success"]
        assert "not your vassal" in result["message"]

    def test_ai_insufficient_nation_dp_refused(self):
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="Prussia", loyalty=40)
        world.nation_dp = {"Prussia": 0}
        world.nation_gold["Prussia"] = 1000

        result = invest_in_vassal(world, "Saxony", actor="Prussia")

        assert not result["success"]
        assert "diplomatic points" in result["message"].lower()
        # No partial spend
        assert world.nation_gold["Prussia"] == 1000

    def test_insufficient_gold_charges_no_dp(self):
        """Gold is checked BEFORE DP is charged — no partial spend."""
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="France", loyalty=40)
        world.diplomatic_points = 3
        world.nation_gold["France"] = 50  # < 200

        result = invest_in_vassal(world, "Saxony")

        assert not result["success"]
        assert world.diplomatic_points == 3

    def test_player_path_unchanged(self):
        """The default (no actor) path is byte-compatible with pre-slice-0."""
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="France", loyalty=40)
        world.diplomatic_points = 2
        world.nation_gold["France"] = 500

        result = invest_in_vassal(world, "Saxony")

        assert result["success"]
        assert world.vassals["Saxony"]["loyalty"] == 50
        assert world.diplomatic_points == 1
        assert world.nation_gold["France"] == 300


# ═══════════════════════════════════════════════════════
# 2. change_vassal_autonomy lord gate + DP split
# ═══════════════════════════════════════════════════════

class TestAutonomyNationNeutral:
    def test_ai_lord_changes_own_vassal_spends_nation_dp(self):
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="Prussia",
                   loyalty=40, autonomy=AUTONOMY_SATELLITE)
        world.nation_dp = {"Prussia": 2}
        player_dp_before = world.diplomatic_points

        result = change_vassal_autonomy(world, "Saxony", AUTONOMY_AUTONOMOUS,
                                        actor="Prussia")

        assert result["success"], result["message"]
        assert world.vassals["Saxony"]["autonomy"] == AUTONOMY_AUTONOMOUS
        assert world.nation_dp["Prussia"] == 1
        assert world.diplomatic_points == player_dp_before

    def test_ai_cannot_change_player_vassal_autonomy(self):
        """Pre-fix: NO lord gate — this call would have succeeded AND drained
        the player's DP. Both are now pinned closed."""
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="France",
                   loyalty=40, autonomy=AUTONOMY_SATELLITE)
        world.nation_dp = {"Prussia": 2}
        player_dp_before = world.diplomatic_points

        result = change_vassal_autonomy(world, "Saxony", AUTONOMY_AUTONOMOUS,
                                        actor="Prussia")

        assert not result["success"]
        assert "not your vassal" in result["message"]
        assert world.diplomatic_points == player_dp_before
        assert world.nation_dp["Prussia"] == 2
        assert world.vassals["Saxony"]["autonomy"] == AUTONOMY_SATELLITE

    def test_player_path_unchanged(self):
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="France",
                   loyalty=40, autonomy=AUTONOMY_SATELLITE)
        world.diplomatic_points = 2

        result = change_vassal_autonomy(world, "Saxony", AUTONOMY_AUTONOMOUS)

        assert result["success"]
        assert world.diplomatic_points == 1
        assert world.vassals["Saxony"]["tribute_rate"] == TRIBUTE_RATES[AUTONOMY_AUTONOMOUS]


# ═══════════════════════════════════════════════════════
# 3. Player-scoped coalition threat
# ═══════════════════════════════════════════════════════

class TestThreatPlayerScoped:
    # The WPS-B power cap is not under test here (Saxony is 62% of Prussia in
    # the legacy fixture); patch it open so the threat guard is what's pinned.
    _CAP_OK = {"allowed": True, "reason": ""}

    def test_ai_treaty_vassalization_adds_no_threat(self):
        from unittest.mock import patch
        world = make_world()
        world.threat_level = 10
        key = world._make_diplo_key("Prussia", "Saxony")
        world.diplomatic_states[key] = "OPEN_BORDERS"

        with patch("backend.game_logic.diplomacy.check_vassalage_power_cap",
                   return_value=self._CAP_OK):
            result = create_vassal_treaty(world, "Prussia", "Saxony")

        assert result["success"], result["message"]
        assert world.threat_level == 10

    def test_player_treaty_vassalization_still_adds_threat(self):
        world = make_world()
        world.threat_level = 10
        key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[key] = "OPEN_BORDERS"

        result = create_vassal_treaty(world, "France", "Saxony")

        assert result["success"], result["message"]
        assert world.threat_level == 15

    def test_ai_conquest_vassalization_adds_no_threat(self):
        from unittest.mock import patch
        world = make_world()
        world.threat_level = 10
        key = world._make_diplo_key("Prussia", "Saxony")
        world.diplomatic_states[key] = "WAR"

        with patch("backend.game_logic.diplomacy.check_vassalage_power_cap",
                   return_value=self._CAP_OK):
            result = create_vassal_conquest(world, "Prussia", "Saxony")

        assert result["success"], result["message"]
        assert world.threat_level == 10

    def test_ai_lord_rebellion_reduces_no_player_threat(self):
        world = make_world()
        world.threat_level = 50
        add_vassal(world, vassal="Saxony", lord="Prussia", loyalty=0)

        check_vassal_rebellion(world)

        assert "Saxony" not in world.vassals
        assert world.threat_level == 50


# ═══════════════════════════════════════════════════════
# 4. VP-D1: wired presence-based garrison lever
# ═══════════════════════════════════════════════════════

class TestGarrisonLeverWired:
    def test_player_marshal_in_vassal_capital_steadies_loyalty(self):
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="France", loyalty=60)
        marshal = next(m for m in world.marshals.values() if m.nation == "France")
        marshal.location = "Dresden"

        process_vassal_loyalty(world)

        # drift(-2) + garrison(+2) = 0
        assert world.vassals["Saxony"]["loyalty"] == 60

    def test_enemy_lord_garrison_symmetric_gr5(self):
        """An AI lord garrisoning ITS vassal's capital earns the same +2."""
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="Prussia", loyalty=60)
        m = Marshal("Blucher", "Dresden", 15000, "aggressive", nation="Prussia")
        world.marshals[m.name] = m

        process_vassal_loyalty(world)

        assert world.vassals["Saxony"]["loyalty"] == 60

    def test_wrong_nation_marshal_gives_nothing(self):
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="France", loyalty=60)
        m = Marshal("Blucher", "Dresden", 15000, "aggressive", nation="Prussia")
        world.marshals[m.name] = m

        process_vassal_loyalty(world)

        # drift(-2) only — a foreign corps is no comfort
        assert world.vassals["Saxony"]["loyalty"] == 58

    def test_predicate_detachment_corner(self):
        """Lord-controlled capital holding a real garrison counts (carved
        vassal whose capital the lord retained)."""
        world = make_world()
        region = world.regions.get("Dresden")
        assert region is not None
        region.controller = "France"
        region.garrison_strength = 5000
        assert lord_garrison_present(world, "France", "Dresden") is True

    def test_predicate_vassal_own_garrison_excluded(self):
        world = make_world()
        region = world.regions.get("Dresden")
        assert region is not None
        region.controller = "Saxony"
        region.garrison_strength = 10000
        assert lord_garrison_present(world, "France", "Dresden") is False

    def test_full_value_in_spiral_band(self):
        """The garrison term is NOT blunted by the VS-R lever multiplier —
        a deed, not a cheap one-shot. Contribution stays +2 even in spiral."""
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="France", loyalty=60)
        marshal = next(m for m in world.marshals.values() if m.nation == "France")
        marshal.location = "Dresden"
        # Force a grip spiral: authority floor + capital lost
        world.authority_tracker.authority = 20
        paris = world.regions.get("Paris")
        if paris is not None:
            paris.controller = "Austria"

        process_vassal_loyalty(world)

        # drift(-2) + garrison(+2) + grip(-2) = -2 (garrison at FULL +2;
        # if it were blunted to 0 the total would be -4)
        assert world.vassals["Saxony"]["loyalty"] == 58

    def test_recovery_hint_readvertises_garrison(self):
        assert "garrison" in recovery_hint_for_grip(80).lower()
        # The spiral copy still does NOT sell the garrison as an arrestor
        assert "garrison" not in recovery_hint_for_grip(10).lower()

    def test_bonus_constant(self):
        assert GARRISON_LOYALTY_BONUS == 2


# ═══════════════════════════════════════════════════════
# 5. Executor honors _acting_nation + structured levels
# ═══════════════════════════════════════════════════════

class TestExecutorActingNation:
    def _executor(self, world):
        from backend.commands.executor import CommandExecutor
        return CommandExecutor(), {"world": world, "debug_mode": True}

    def test_invest_via_executor_with_acting_nation(self):
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="Prussia", loyalty=40)
        world.nation_dp = {"Prussia": 3}
        world.nation_gold["Prussia"] = 1000
        executor, game_state = self._executor(world)

        result = executor._vassal._execute_invest_vassal(
            {"action": "invest_vassal", "target": "Saxony",
             "_acting_nation": "Prussia"},
            game_state,
        )

        assert result["success"], result["message"]
        assert world.nation_dp["Prussia"] == 2

    def test_change_autonomy_structured_level(self):
        """A structured new_level field wins over raw-text parsing."""
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="France",
                   loyalty=40, autonomy=AUTONOMY_SATELLITE)
        world.diplomatic_points = 2
        executor, game_state = self._executor(world)

        result = executor._vassal._execute_change_autonomy(
            {"action": "change_autonomy", "target": "Saxony",
             "new_level": AUTONOMY_AUTONOMOUS},
            game_state,
        )

        assert result["success"], result["message"]
        assert world.vassals["Saxony"]["autonomy"] == AUTONOMY_AUTONOMOUS

    def test_change_autonomy_structured_level_ai_actor(self):
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="Prussia",
                   loyalty=40, autonomy=AUTONOMY_PUPPET)
        world.nation_dp = {"Prussia": 2}
        executor, game_state = self._executor(world)

        result = executor._vassal._execute_change_autonomy(
            {"action": "change_autonomy", "target": "Saxony",
             "new_level": AUTONOMY_SATELLITE, "_acting_nation": "Prussia"},
            game_state,
        )

        assert result["success"], result["message"]
        assert world.nation_dp["Prussia"] == 1
        assert world.vassals["Saxony"]["autonomy"] == AUTONOMY_SATELLITE

    def test_change_autonomy_raw_text_path_still_works(self):
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="France",
                   loyalty=40, autonomy=AUTONOMY_SATELLITE)
        world.diplomatic_points = 2
        executor, game_state = self._executor(world)

        result = executor._vassal._execute_change_autonomy(
            {"action": "change_autonomy", "target": "Saxony",
             "raw_command": "grant Saxony more autonomy"},
            game_state,
        )

        assert result["success"], result["message"]
        assert world.vassals["Saxony"]["autonomy"] == AUTONOMY_AUTONOMOUS
