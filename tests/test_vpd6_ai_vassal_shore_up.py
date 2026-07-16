"""
VP-D6 — Enemy-AI grip-awareness: the P1.6 vassal shore-up rung
(DESIGN_REFINEMENT.md VP-D6; VASSAL_DEEPENING_SPEC.md §8 item 5),
landed July 16, 2026.

A spiralling AI lord steadies its own satellites through the SAME executor
at the SAME prices as the player (Slice-0 nation-neutral substrate): invest
→ cede a province (VS-3's lord-neutral helper) → grant autonomy, in
escalating desperation. Latent at the 1805 boot (no enemy lord holds a
satellite) — live the moment one acquires a vassal.
"""

import pytest

from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState
from backend.game_logic.vassal import (
    AUTONOMY_PUPPET,
    AUTONOMY_SATELLITE,
    INVEST_GOLD_COST,
    TRIBUTE_RATES,
)


def _setup(lord="Austria", vassal="Saxony", loyalty=30, dp=3, gold=2000):
    world = WorldState(player_nation="France")
    world.vassals[vassal] = {
        "lord": lord,
        "loyalty": int(loyalty),
        "autonomy": AUTONOMY_SATELLITE,
        "path": "treaty",
        "created_turn": 1,
        "tribute_rate": TRIBUTE_RATES[AUTONOMY_SATELLITE],
        "carved_from": None,
        "regions": None,
    }
    key = world._make_diplo_key(lord, vassal)
    world.diplomatic_states[key] = "VASSAL"
    world.nation_relations[key] = 0
    world.nation_dp = {lord: dp}
    world.nation_gold[lord] = gold
    world.invalidate_active_nations_cache()
    executor = CommandExecutor()
    ai = EnemyAI(executor)
    return world, ai


class TestRungGating:
    def test_dormant_without_own_satellites(self):
        """France's satellites never trigger Austria's rung."""
        world, ai = _setup(lord="France", loyalty=20)
        world.nation_dp = {"Austria": 3}
        world.nation_gold["Austria"] = 2000
        action = ai._find_vassal_shore_up("Austria", world, 2000, set())
        assert action is None

    def test_dormant_when_satellites_healthy(self):
        world, ai = _setup(loyalty=80)
        action = ai._find_vassal_shore_up("Austria", world, 2000, set())
        assert action is None

    def test_dormant_without_nation_dp(self):
        world, ai = _setup(loyalty=20, dp=0)
        action = ai._find_vassal_shore_up("Austria", world, 2000, set())
        assert action is None

    def test_invest_arm_fires_below_40(self):
        world, ai = _setup(loyalty=35)
        action = ai._find_vassal_shore_up("Austria", world, 2000, set())
        assert action == {"action": "invest_vassal", "target": "Saxony"}

    def test_grant_arm_when_invest_cooling_and_province_spare(self):
        world, ai = _setup(loyalty=25)
        world.vassal_investment_cooldowns["Saxony"] = 2
        # Austria holds the conquered Saxony region (starting controller
        # Saxony) — a homeland-return, the classic Ried-style grant.
        world.regions["Saxony"].controller = "Austria"
        world.invalidate_active_nations_cache()
        action = ai._find_vassal_shore_up("Austria", world, 2000, set())
        assert action is not None
        assert action["action"] == "grant_region_to_vassal"
        assert action["target"] == "Saxony"
        assert action["region"] == "Saxony"

    def test_autonomy_arm_last_resort(self):
        world, ai = _setup(loyalty=20)
        world.vassal_investment_cooldowns["Saxony"] = 2
        # no eligible province → falls through to autonomy-up
        action = ai._find_vassal_shore_up("Austria", world, 2000, set())
        assert action is not None
        assert action["action"] == "change_autonomy"
        assert action["new_level"] == AUTONOMY_SATELLITE + 1

    def test_skip_actions_respected(self):
        world, ai = _setup(loyalty=35)
        action = ai._find_vassal_shore_up(
            "Austria", world, 2000, {"invest_vassal"})
        # invest skipped; loyalty 35 is above the grant (<30) and autonomy
        # (<25) gates → nothing
        assert action is None

    def test_puppet_autonomy_arm_targets_next_level(self):
        world, ai = _setup(loyalty=20)
        world.vassals["Saxony"]["autonomy"] = AUTONOMY_PUPPET
        world.vassal_investment_cooldowns["Saxony"] = 2
        action = ai._find_vassal_shore_up("Austria", world, 2000, set())
        assert action["action"] == "change_autonomy"
        assert action["new_level"] == AUTONOMY_PUPPET + 1


class TestEndToEnd:
    def test_admin_phase_invests_through_shared_executor(self):
        """GR5 proof: the rung executes via the SAME executor, spending the
        AI's own nation_dp/gold, and the satellite steadies."""
        world, ai = _setup(loyalty=30, dp=3, gold=2000)
        game_state = {"world": world}

        results = ai.execute_admin_phase("Austria", world, game_state)

        invested = [r for r in results
                    if r.get("ai_action", {}).get("action") == "invest_vassal"]
        assert invested, [r.get("ai_action") for r in results]
        assert world.vassals["Saxony"]["loyalty"] == 40  # +10
        assert world.nation_dp["Austria"] == 2
        assert world.nation_gold["Austria"] <= 2000 - INVEST_GOLD_COST + 100

    def test_admin_phase_grants_province_with_region_field(self):
        """The command builder carries the structured region pick."""
        world, ai = _setup(loyalty=25, dp=3, gold=2000)
        world.vassal_investment_cooldowns["Saxony"] = 2
        world.regions["Saxony"].controller = "Austria"  # homeland-return
        world.invalidate_active_nations_cache()
        game_state = {"world": world}

        results = ai.execute_admin_phase("Austria", world, game_state)

        granted = [r for r in results
                   if r.get("ai_action", {}).get("action") == "grant_region_to_vassal"]
        assert granted, [r.get("ai_action") for r in results]
        assert world.regions["Saxony"].controller == "Saxony"
        assert "Saxony" in world.vassals["Saxony"].get("granted_regions", [])

    def test_admin_phase_autonomy_arm_executes(self):
        world, ai = _setup(loyalty=20, dp=3, gold=100)  # too poor to invest
        game_state = {"world": world}

        results = ai.execute_admin_phase("Austria", world, game_state)

        changed = [r for r in results
                   if r.get("ai_action", {}).get("action") == "change_autonomy"]
        assert changed, [r.get("ai_action") for r in results]
        assert world.vassals["Saxony"]["autonomy"] == AUTONOMY_SATELLITE + 1

    def test_player_pools_never_touched(self):
        world, ai = _setup(loyalty=30, dp=3, gold=2000)
        player_dp = world.diplomatic_points
        player_gold = world.nation_gold.get("France", 0)
        ai.execute_admin_phase("Austria", world, {"world": world})
        assert world.diplomatic_points == player_dp
        assert world.nation_gold.get("France", 0) == player_gold
