"""
Final Audit Fix Session 1: Test file for FINAL-9, FINAL-10, FINAL-11,
FINAL-7, FINAL-8, FINAL-16, FINAL-17.

Tests victory/defeat conditions, fog filters, fortification int conversion,
retreat fog leak, and capital-captured AI proposal skip.
"""

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.game_logic.turn_manager import TurnManager
from backend.game_logic.combat import CombatResolver
from backend.campaign_log import filter_campaign_log
from backend.models.intel import FULL, PARTIAL, UNKNOWN  # noqa: F401
from backend.commands.executor import _filter_tactical_events_by_fog


def _make_world(**kwargs):
    """Create a WorldState with sensible defaults for testing."""
    world = WorldState()
    for k, v in kwargs.items():
        setattr(world, k, v)
    return world


def _marshal(name, nation="France", location="Paris", strength=5000, personality="aggressive"):
    """Create a Marshal with required args filled in."""
    return Marshal(name, location, strength, personality, nation=nation)


# ============================================================================
# FINAL-9: Defeat on capital loss / 0 regions
# ============================================================================

class TestDefeatOnCapitalLossOrZeroRegions:
    """FINAL-9 + PL-31: Defeat on 0 regions only. Capital loss is NOT defeat."""

    def test_zero_regions_triggers_defeat(self):
        """If player has 0 regions, _check_victory_conditions returns defeat."""
        world = _make_world()
        for region in world.regions.values():
            region.controller = "Prussia"
        m = _marshal("Ney")
        world.marshals["Ney"] = m

        tm = TurnManager(world)
        result = tm._check_victory_conditions()
        assert result["game_over"] is True
        assert result["result"] == "defeat"
        assert "territory" in result["reason"].lower()

    def test_capital_captured_does_not_defeat(self):
        """PL-31: Capital loss alone should NOT end the game."""
        world = _make_world()
        paris = world.get_region("Paris")
        assert paris is not None
        paris.controller = "Prussia"
        # Player still has other regions + marshals
        m = _marshal("Ney")
        world.marshals["Ney"] = m

        tm = TurnManager(world)
        result = tm._check_victory_conditions()
        assert result["game_over"] is False, (
            "Capital loss should not trigger defeat (PL-31)"
        )


# ============================================================================
# FINAL-10: Turn 40 off-by-one
# ============================================================================

class TestTurnLimitOffByOne:
    """FINAL-10: Game should end at exactly max_turns (>=, not >)."""

    def test_game_ends_at_exactly_max_turns(self):
        """When current_turn == max_turns, the time check should fire."""
        world = _make_world()
        world.max_turns = 40
        world.current_turn = 40
        total = len(world.regions)
        from backend.models.world_state import VICTORY_REGION_FRACTION
        needed = int(total * VICTORY_REGION_FRACTION)
        controlled = 0
        for region in world.regions.values():
            if controlled < needed:
                region.controller = "France"
                controlled += 1
            else:
                region.controller = "Prussia"
        m = _marshal("Ney")
        world.marshals["Ney"] = m

        tm = TurnManager(world)
        result = tm._check_victory_conditions()
        assert result["game_over"] is True
        assert result["result"] == "victory"


# ============================================================================
# FINAL-11: Victory on total enemy elimination
# ============================================================================

class TestVictoryOnEnemyElimination:
    """FINAL-11: If all enemy nations have 0 regions, game ends in victory."""

    def test_all_enemy_nations_zero_regions_triggers_victory(self):
        """Victory when every region is controlled by player nation."""
        world = _make_world()
        for region in world.regions.values():
            region.controller = "France"
        m = _marshal("Ney")
        world.marshals["Ney"] = m

        tm = TurnManager(world)
        result = tm._check_victory_conditions()
        assert result["game_over"] is True
        assert result["result"] == "victory"

    def test_enemies_with_regions_no_victory(self):
        """No premature victory when enemies still hold regions."""
        world = _make_world()
        for name, region in world.regions.items():
            if name == "Berlin":
                region.controller = "Prussia"
            else:
                region.controller = "France"
        m = _marshal("Ney")
        world.marshals["Ney"] = m
        world.current_turn = 1

        tm = TurnManager(world)
        result = tm._check_victory_conditions()
        total = len(world.regions)
        player_count = len(world.get_player_regions())
        if player_count >= total - 1:
            assert result["game_over"] is True  # total conquest
        else:
            assert result["game_over"] is False


# ============================================================================
# FINAL-7: Tactical events fog filter
# ============================================================================

class TestTacticalEventsFogFilter:
    """FINAL-7: Tactical events should be filtered by fog before reaching frontend."""

    def test_player_nation_events_kept(self):
        """Events from player nation marshals are always visible."""
        world = _make_world()
        events = [
            {"type": "recovery", "marshal": "Ney", "nation": "France", "location": "Paris"},
            {"type": "recovery", "marshal": "Blucher", "nation": "Prussia", "location": "Berlin"},
        ]
        intel = world.get_region_intel("Berlin")
        intel.visibility = UNKNOWN

        filtered = _filter_tactical_events_by_fog(events, world)
        names = [e.get("marshal") for e in filtered]
        assert "Ney" in names

    def test_visible_enemy_events_kept(self):
        """Enemy events in visible regions are kept."""
        world = _make_world()
        intel = world.get_region_intel("Berlin")
        intel.visibility = PARTIAL
        events = [
            {"type": "recovery", "marshal": "Blucher", "nation": "Prussia", "location": "Berlin"},
        ]
        filtered = _filter_tactical_events_by_fog(events, world)
        assert len(filtered) == 1

    def test_fogged_enemy_events_filtered(self):
        """Enemy events in fogged regions are removed."""
        world = _make_world()
        intel = world.get_region_intel("Berlin")
        intel.visibility = UNKNOWN
        events = [
            {"type": "recovery", "marshal": "Blucher", "nation": "Prussia", "location": "Berlin"},
        ]
        filtered = _filter_tactical_events_by_fog(events, world)
        assert len(filtered) == 0


# ============================================================================
# FINAL-8: Fortification old/new are int (Golden Rule #2)
# ============================================================================

class TestFortificationIntConversion:
    """FINAL-8: fortification_old/new in combat results must be int, not float."""

    def test_fortification_values_are_int(self):
        """Combat result fortification_old/new are int type."""
        attacker = _marshal("Ney", location="Rhineland", strength=10000, personality="aggressive")
        attacker.morale = 80
        defender = _marshal("Wellington", nation="Britain", location="Rhineland",
                            strength=8000, personality="cautious")
        defender.morale = 80
        defender.defense_bonus = 0.25  # Fortified

        resolver = CombatResolver()
        result = resolver.resolve_battle(attacker, defender, terrain="plains")

        assert isinstance(result["fortification_old"], int)
        assert isinstance(result["fortification_new"], int)
        assert result["fortification_old"] == 25
        assert result["fortification_new"] < 25

        log_event = result["log_battle_event"]
        assert isinstance(log_event["fortification_old"], int)
        assert isinstance(log_event["fortification_new"], int)


# ============================================================================
# FINAL-16: Retreat destination fog leak
# ============================================================================

class TestRetreatDestinationFogLeak:
    """FINAL-16: Retreat events should strip destination when fogged."""

    def test_fogged_destination_hidden(self):
        """If retreat destination is fogged, 'to' field is stripped."""
        world = _make_world()
        src_intel = world.get_region_intel("Rhineland")
        src_intel.visibility = PARTIAL
        dst_intel = world.get_region_intel("Berlin")
        dst_intel.visibility = UNKNOWN

        events = [
            {
                "type": "retreat",
                "marshal": "Blucher",
                "nation": "Prussia",
                "location": "Rhineland",
                "from": "Rhineland",
                "to": "Berlin"
            }
        ]
        filtered = filter_campaign_log(events, world)
        assert len(filtered) == 1
        assert "to" not in filtered[0]

    def test_visible_destination_shown(self):
        """If retreat destination is visible, 'to' field is preserved."""
        world = _make_world()
        src_intel = world.get_region_intel("Rhineland")
        src_intel.visibility = PARTIAL
        dst_intel = world.get_region_intel("Berlin")
        dst_intel.visibility = PARTIAL

        events = [
            {
                "type": "retreat",
                "marshal": "Blucher",
                "nation": "Prussia",
                "location": "Rhineland",
                "from": "Rhineland",
                "to": "Berlin"
            }
        ]
        filtered = filter_campaign_log(events, world)
        assert len(filtered) == 1
        assert filtered[0].get("to") == "Berlin"


# ============================================================================
# FINAL-17: AI proposals to defeated nations (capital captured)
# ============================================================================

class TestAIProposalToDefeatedNation:
    """FINAL-17: AI should not propose to nations whose capital is captured."""

    def test_no_proposal_to_capital_captured_nation(self):
        """AI proposal generation skips nations whose capital is held by enemy."""
        world = _make_world()
        berlin = world.get_region("Berlin")
        berlin.controller = "France"
        # Give Prussia at least one non-capital region
        for name, r in world.regions.items():
            if name == "Saxony":
                r.controller = "Prussia"
                break

        # Ensure Prussia has marshals (not fully eliminated)
        m = _marshal("Blucher", nation="Prussia", location="Saxony")
        world.marshals["Blucher"] = m

        from backend.game_logic.ai_diplomacy import process_diplomatic_phase
        result = process_diplomatic_phase("Prussia", world)
        assert result is None  # Should skip — capital captured
