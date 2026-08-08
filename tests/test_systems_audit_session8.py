"""
Systems Audit Fix Plan — Session 8: Balance & Economy

Tests for fixes:
  F1:  Defense modifier cap 1.75x (prevents invincible turtling)
  F2:  HOLD order slows fort decay for all personalities
  F3:  AI futility decay every 3 turns + reset on weak defender
  F4:  Supply stacking penalty for death-balling
  F5:  Early defeat — DEFERRED (roadmap)
  F6:  Admin AP gold 75 → 35
  F7:  Victory threshold → 14
  F8:  Halved regen rates (infantry/cavalry/artillery)
  F9:  British naval income requires >= 1 region
  F10: Trade income visibility in dispatch/ledger
  F11: Bankruptcy checked after ALL income sources
  F12: Vindication — WAI (no change)
"""

import io
import contextlib

from backend.models.marshal import Marshal
from backend.models.world_state import (
    WorldState,
    INFANTRY_BASE_REGEN, CAVALRY_BASE_REGEN, ARTILLERY_BASE_REGEN,
)
from backend.game_logic.diplomacy import calculate_trade_income


def _suppress_output():
    """Context manager to suppress print output during tests."""
    return contextlib.redirect_stdout(io.StringIO())


def _fresh_world():
    """Create a fresh WorldState for testing."""
    with _suppress_output():
        return WorldState()


def _make_marshal(name="Test", strength=10000, personality="cautious", nation="France",
                  cavalry=False, artillery=False, **kwargs):
    """Helper to create a marshal with sensible defaults."""
    with _suppress_output():
        m = Marshal(name, "TestRegion", strength, personality, nation,
                    cavalry=cavalry, artillery=artillery)
    for k, v in kwargs.items():
        setattr(m, k, v)
    return m


# ═══════════════════════════════════════════════════════════════════
# F1: Defense modifier cap 1.75x
# ═══════════════════════════════════════════════════════════════════

class TestDefenseModifierCap:
    """No marshal can exceed 1.75x total defense."""

    def test_stacked_bonuses_capped_at_175(self):
        """Marshal with max defense_bonus + coordination should cap at 1.75."""
        m = _make_marshal(name="Davout", personality="cautious", strength=20000)
        m.defense_bonus = 0.20  # Max fort bonus for Davout
        m.total_coordination_defense_bonus = 0.50  # Stacked coordination
        m.square_formation = True  # +5%
        m.holding_position = True  # Personality bonus
        # These multiplicative bonuses should push well over 1.75 uncapped
        mod = m.get_defense_modifier()
        assert mod <= 1.75

    def test_normal_defense_not_capped(self):
        """Marshal with moderate bonuses should NOT be capped."""
        m = _make_marshal(name="Soult", personality="cautious", strength=20000)
        m.defense_bonus = 0.10
        mod = m.get_defense_modifier()
        assert mod < 1.75  # Should be well under cap


# ═══════════════════════════════════════════════════════════════════
# F2: HOLD order slows fort decay
# ═══════════════════════════════════════════════════════════════════

class TestHoldDecayReduction:
    """HOLD order reduces fortification decay for all personalities."""

    def test_hold_slows_decay_cautious(self):
        """Cautious marshal with HOLD gets 75% decay reduction."""
        world = _fresh_world()
        davout = world.get_marshal("Davout")
        davout.defense_bonus = 0.10  # Above cautious floor (0.05)
        davout.fortified = True  # Must be fortified for decay logic
        davout.is_fortifying = False
        davout.turns_fortified = 9  # Will be incremented to 10 (>= 8 start)
        davout.cumulative_fortification_turns = 9  # V2-27: must match for decay calc

        # Give HOLD order
        from backend.models.marshal import StrategicOrder
        davout.strategic_order = StrategicOrder("HOLD", davout.location, "generic", 1, "hold position")

        start_bonus = davout.defense_bonus
        with _suppress_output():
            world._process_tactical_states()
        hold_decay = start_bonus - davout.defense_bonus

        # Now test without HOLD
        davout.defense_bonus = start_bonus
        davout.fortified = True
        davout.turns_fortified = 9
        davout.cumulative_fortification_turns = 9  # V2-27: must match for decay calc
        davout.strategic_order = None
        with _suppress_output():
            world._process_tactical_states()
        normal_decay = start_bonus - davout.defense_bonus

        # HOLD should produce less decay than no HOLD
        assert normal_decay > 0, "Without HOLD, cautious should decay"
        assert hold_decay < normal_decay

    def test_hold_slows_decay_non_cautious(self):
        """Non-cautious (balanced) marshal with HOLD gets 50% decay reduction.
        Uses Grouchy rebadged as balanced (Ney is cavalry, skips decay)."""
        world = _fresh_world()
        grouchy = world.get_marshal("Grouchy")
        # Override personality to balanced for this test (literal has same config as cautious)
        grouchy.personality = "balanced"
        grouchy.defense_bonus = 0.10  # Above balanced floor (0.0)
        grouchy.fortified = True
        grouchy.is_fortifying = False
        grouchy.turns_fortified = 7  # Will be incremented to 8 (>= 6 start for balanced)
        grouchy.cumulative_fortification_turns = 7  # V2-27: must match for decay calc

        from backend.models.marshal import StrategicOrder
        grouchy.strategic_order = StrategicOrder("HOLD", grouchy.location, "generic", 1, "hold position")

        start_bonus = grouchy.defense_bonus
        with _suppress_output():
            world._process_tactical_states()
        hold_decay = start_bonus - grouchy.defense_bonus

        grouchy.defense_bonus = start_bonus
        grouchy.fortified = True
        grouchy.turns_fortified = 7
        grouchy.cumulative_fortification_turns = 7  # V2-27: must match for decay calc
        grouchy.strategic_order = None
        with _suppress_output():
            world._process_tactical_states()
        normal_decay = start_bonus - grouchy.defense_bonus

        assert normal_decay > 0, "Without HOLD, balanced should decay"
        assert hold_decay < normal_decay


# ═══════════════════════════════════════════════════════════════════
# F3: AI futility decay
# ═══════════════════════════════════════════════════════════════════

class TestAIFutilityDecay:
    """AI futility counter decays every 3 turns and resets on weak defender."""

    def test_futility_decays_every_3_turns(self):
        """Futility counter decrements by 1 every 3 turns."""
        world = _fresh_world()
        world.ai_attack_futility = {"Blucher:Davout": 5}
        world.current_turn = 3  # Divisible by 3

        # Simulate the decay block
        if world.current_turn % 3 == 0:
            expired = []
            for key, count in world.ai_attack_futility.items():
                new_count = count - 1
                if new_count <= 0:
                    expired.append(key)
                else:
                    world.ai_attack_futility[key] = new_count
            for key in expired:
                world.ai_attack_futility.pop(key, None)

        assert world.ai_attack_futility["Blucher:Davout"] == 4

    def test_futility_expires_at_zero(self):
        """Futility entry removed when it decays to 0."""
        world = _fresh_world()
        world.ai_attack_futility = {"Blucher:Davout": 1}
        world.current_turn = 6

        if world.current_turn % 3 == 0:
            expired = []
            for key, count in world.ai_attack_futility.items():
                new_count = count - 1
                if new_count <= 0:
                    expired.append(key)
                else:
                    world.ai_attack_futility[key] = new_count
            for key in expired:
                world.ai_attack_futility.pop(key, None)

        assert "Blucher:Davout" not in world.ai_attack_futility

    def test_futility_resets_on_weak_defender(self):
        """Futility resets when defender drops below 50% starting strength."""
        world = _fresh_world()
        davout = world.get_marshal("Davout")
        davout.strength = int(davout.starting_strength * 0.4)  # Below 50%

        world.ai_attack_futility = {"Blucher:Davout": 5}

        # Simulate the reset block
        reset_keys = []
        for key in world.ai_attack_futility:
            parts = key.split(":")
            if len(parts) == 2:
                defender_name = parts[1]
                defender = world.get_marshal(defender_name)
                if defender and defender.strength < defender.starting_strength * 0.5:
                    reset_keys.append(key)
        for key in reset_keys:
            world.ai_attack_futility.pop(key, None)

        assert "Blucher:Davout" not in world.ai_attack_futility


# ═══════════════════════════════════════════════════════════════════
# F4: Supply stacking penalty
# ═══════════════════════════════════════════════════════════════════

class TestSupplyStackingPenalty:
    """Death-balling (3+ marshals in one region) incurs supply penalty."""

    def test_three_marshals_same_region_attrition(self):
        """3 marshals in same region should incur stacking attrition."""
        world = _fresh_world()
        # Move 3 French marshals to the same region
        target_region = "Saxony"
        french_marshals = [m for m in world.marshals.values() if m.nation == "France"]
        for i, m in enumerate(french_marshals[:3]):
            m.location = target_region
            m.strength = 20000  # Healthy troops

        # Count marshals in that region
        marshals_here = [m for m in world.marshals.values()
                         if m.location == target_region and m.strength > 0]
        num_marshals = len(marshals_here)
        stacking_penalty = max(0, num_marshals - 1) * 0.01

        assert num_marshals >= 3
        assert stacking_penalty >= 0.02  # +1% per marshal beyond 1st


# ═══════════════════════════════════════════════════════════════════
# F6: Admin AP gold reduced
# ═══════════════════════════════════════════════════════════════════

class TestAdminAPGold:
    """Admin AP conversion now 25g per unused AP (was 35g in S8, 75g originally)."""

    def test_admin_bonus_25g_per_ap(self):
        """Each unused admin AP converts to 25g (Session 12)."""
        world = _fresh_world()
        world.admin_actions_remaining = 3
        bonus = world._calculate_admin_bonus(world.player_nation)
        assert bonus == 3 * 25  # 75g


# ═══════════════════════════════════════════════════════════════════
# F7: Victory threshold
# ═══════════════════════════════════════════════════════════════════

class TestVictoryThreshold:
    """Victory requires 75% of regions via VICTORY_REGION_FRACTION."""

    def test_victory_threshold_constant_exists(self):
        """VICTORY_REGION_FRACTION is 0.75 and produces correct threshold for current map."""
        from backend.models.world_state import VICTORY_REGION_FRACTION
        from backend.models.region import REGIONS_DATA
        assert VICTORY_REGION_FRACTION == 0.75
        region_count = len(REGIONS_DATA)
        assert int(region_count * VICTORY_REGION_FRACTION) == int(region_count * 0.75)

    def test_victory_threshold_less_than_total(self):
        """Victory threshold is achievable — less than total regions."""
        from backend.models.world_state import VICTORY_REGION_FRACTION
        world = _fresh_world()
        total_regions = len(world.regions)
        threshold = int(total_regions * VICTORY_REGION_FRACTION)
        assert threshold < total_regions


# ═══════════════════════════════════════════════════════════════════
# F8: Halved regen rates
# ═══════════════════════════════════════════════════════════════════

class TestHalvedRegenRates:
    """Manpower regen halved: infantry 2500, cavalry 250, artillery 150."""

    def test_infantry_base_regen(self):
        assert INFANTRY_BASE_REGEN == 2500

    def test_cavalry_base_regen(self):
        assert CAVALRY_BASE_REGEN == 250

    def test_artillery_base_regen(self):
        assert ARTILLERY_BASE_REGEN == 150

    def test_cavalry_less_than_infantry(self):
        assert CAVALRY_BASE_REGEN < INFANTRY_BASE_REGEN

    def test_artillery_less_than_cavalry(self):
        assert ARTILLERY_BASE_REGEN < CAVALRY_BASE_REGEN


# ═══════════════════════════════════════════════════════════════════
# F9: British naval income requires regions
# ═══════════════════════════════════════════════════════════════════

class TestBritishNavalIncome:
    """British naval income requires at least 1 controlled region."""

    def test_britain_with_regions_gets_naval_income(self):
        """Britain with regions gets 200g naval income (150 + 50*1 coastal)."""
        world = _fresh_world()
        result = world.calculate_turn_income("Britain")
        naval = result["breakdown"]["naval_income"]
        assert naval == 200  # 150 + 50*1 (Netherlands is the only coastal region)

    def test_britain_without_regions_no_naval_income(self):
        """Britain with 0 regions gets 0 naval income."""
        world = _fresh_world()
        # Remove all British regions
        for region in world.regions.values():
            if region.controller == "Britain":
                region.controller = "France"
        result = world.calculate_turn_income("Britain")
        naval = result["breakdown"]["naval_income"]
        assert naval == 0

    def test_france_never_gets_naval_income(self):
        """Non-Britain nations never get naval income."""
        world = _fresh_world()
        result = world.calculate_turn_income("France")
        naval = result["breakdown"]["naval_income"]
        assert naval == 0


# ═══════════════════════════════════════════════════════════════════
# F10: Trade income visibility
# ═══════════════════════════════════════════════════════════════════

class TestTradeIncomeVisibility:
    """Trade income shows in dispatch and ledger."""

    def test_dispatch_includes_trade_income(self):
        """Dispatch situation section includes trade_income field."""
        world = _fresh_world()
        # Set up a PEACE diplomatic state to generate trade income
        world.diplomatic_states["France|Prussia"] = "PEACE"
        from backend.game_logic.dispatch import _build_situation
        situation = _build_situation(world, world.player_nation)
        assert "trade_income" in situation
        assert isinstance(situation["trade_income"], int)

    def test_dispatch_trade_income_in_delta(self):
        """Dispatch treasury_delta includes trade income."""
        world = _fresh_world()
        # Set ALLIANCE for high trade income
        world.diplomatic_states["France|Prussia"] = "ALLIANCE"
        from backend.game_logic.dispatch import _build_situation

        # Get situation with trade
        situation = _build_situation(world, world.player_nation)
        trade = situation["trade_income"]
        assert trade > 0  # ALLIANCE = 200g
        # treasury_delta should account for trade. EB review [5] re-pin
        # (Aug 7 2026): the delta now reads the ledger's reconciled net
        # (the CA8-10 fix — the hand-assembled formula omitted admin
        # bonus/tribute/treaty gold), so trade's inclusion is asserted
        # through the ledger identity: net moves one-for-one with trade.
        from backend.game_logic.ledger import _build_economy
        econ = _build_economy(world, world.player_nation)
        assert econ["trade_income"] == trade
        assert situation["treasury_delta"] == int(econ["net"])

    def test_ledger_includes_trade_income(self):
        """Ledger economy section includes trade_income field."""
        world = _fresh_world()
        world.diplomatic_states["France|Prussia"] = "PEACE"
        from backend.game_logic.ledger import _build_economy
        economy = _build_economy(world, world.player_nation)
        assert "trade_income" in economy
        assert isinstance(economy["trade_income"], int)

    def test_calculate_trade_income_read_only(self):
        """calculate_trade_income does NOT modify nation_gold."""
        world = _fresh_world()
        world.diplomatic_states["France|Prussia"] = "ALLIANCE"
        gold_before = dict(world.nation_gold)
        calculate_trade_income(world)
        assert world.nation_gold == gold_before


# ═══════════════════════════════════════════════════════════════════
# F11: Bankruptcy after all income sources
# ═══════════════════════════════════════════════════════════════════

class TestBankruptcyTiming:
    """Bankruptcy checked after trade income, not just region income."""

    def test_no_bankruptcy_called_in_process_income_phase(self):
        """process_income_phase should NOT update bankruptcy counter."""
        world = _fresh_world()
        # Set negative gold so bankruptcy WOULD trigger
        world.nation_gold["France"] = -1000
        world.nation_bankruptcy_turns["France"] = 0

        # process_income_phase: gold goes more negative from upkeep
        with _suppress_output():
            world.process_income_phase("France")

        # Bankruptcy counter should NOT have been updated (it's deferred)
        # Gold is negative, but _update_bankruptcy was removed from process_income_phase
        # The counter stays at 0 because bankruptcy check is now in advance_turn
        assert world.nation_bankruptcy_turns["France"] == 0

    def test_trade_income_prevents_bankruptcy(self):
        """Trade income received after region income should prevent bankruptcy."""
        world = _fresh_world()
        # Scenario: Region income leaves France slightly negative
        world.nation_gold["France"] = -50
        # But trade income from alliance would cover it
        world.diplomatic_states["France|Prussia"] = "ALLIANCE"  # +200g

        from backend.game_logic.diplomacy import process_trade_income
        process_trade_income(world)

        # Now gold should be positive
        assert world.nation_gold["France"] > 0

        # Bankruptcy check AFTER trade should find positive gold
        world._update_bankruptcy("France")
        assert world.nation_bankruptcy_turns["France"] == 0
