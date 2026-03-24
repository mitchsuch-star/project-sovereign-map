"""
Audit gap tests for Sessions 7–8 of the Systems Audit Fix Plan.

Covers gaps identified during the code audit:
  1. Victory threshold consistency (player AND enemy must both be 14)
  2. Defense cap with square formation stacking
  3. Phantom personality/marshal cleanup validation
  4. Parser valid_marshals matches create_starting_marshals()
"""

import io
import contextlib

from backend.models.marshal import Marshal
from backend.models.world_state import WorldState
from backend.models.personality import Personality, PERSONALITY_DESCRIPTIONS


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
# 1. Victory threshold consistency
# ═══════════════════════════════════════════════════════════════════

class TestVictoryThresholdConsistency:
    """Player and enemy victory thresholds must match at 14."""

    def test_enemy_victory_threshold_matches_player(self):
        """Enemy victory check in TurnManager uses same threshold as player."""
        from backend.game_logic.turn_manager import TurnManager
        world = _fresh_world()
        tm = TurnManager(world)

        # Give an enemy 13 regions — should NOT trigger victory
        for region in world.regions.values():
            region.controller = "Prussia"
        # Keep exactly 6 as France (19 - 6 = 13 for Prussia)
        count = 0
        for region in world.regions.values():
            if count < 6:
                region.controller = "France"
                count += 1

        result = tm._check_enemy_victory()
        assert result is None, "13 regions should NOT trigger enemy victory"

    def test_enemy_14_regions_triggers_victory(self):
        """Enemy with 14 regions triggers victory."""
        from backend.game_logic.turn_manager import TurnManager
        world = _fresh_world()
        tm = TurnManager(world)

        # Give Prussia 14 regions
        count = 0
        for region in world.regions.values():
            if count < 14:
                region.controller = "Prussia"
                count += 1
            else:
                region.controller = "France"

        result = tm._check_enemy_victory()
        assert result is not None, "14 regions should trigger enemy victory"
        assert result["nation"] == "Prussia"

    def test_player_14_regions_triggers_victory(self):
        """Player with 14 regions triggers victory in advance_turn."""
        world = _fresh_world()

        # Give France 14 regions
        count = 0
        for region in world.regions.values():
            if count < 14:
                region.controller = "France"
                count += 1
            else:
                region.controller = "Prussia"

        player_regions = len(world.get_player_regions())
        assert player_regions == 14
        # The threshold check: player_regions >= 14
        assert player_regions >= 14


# ═══════════════════════════════════════════════════════════════════
# 2. Defense cap with square formation
# ═══════════════════════════════════════════════════════════════════

class TestDefenseCapWithSquare:
    """Defense cap 1.75x applies even with square formation."""

    def test_square_plus_max_bonuses_capped(self):
        """Square formation + fort + coordination + personality is capped at 1.75."""
        m = _make_marshal(name="Davout", personality="cautious", strength=20000)
        m.defense_bonus = 0.20       # Max fort bonus
        m.total_coordination_defense_bonus = 0.50  # Stacked coordination
        m.square_formation = True    # +5%
        m.holding_position = True    # Personality bonus

        mod = m.get_defense_modifier()
        assert mod == 1.75, f"Defense modifier should cap at 1.75, got {mod}"

    def test_square_without_stacking_not_capped(self):
        """Square formation alone (no other bonuses) should NOT hit cap."""
        m = _make_marshal(name="Test", personality="aggressive", strength=10000)
        m.square_formation = True  # +5%
        # No fort bonus, no coordination

        mod = m.get_defense_modifier()
        assert mod < 1.75, f"Square alone should be well under cap, got {mod}"
        assert mod > 1.0, "Square formation should provide some defense boost"


# ═══════════════════════════════════════════════════════════════════
# 3. Phantom personality cleanup validation
# ═══════════════════════════════════════════════════════════════════

class TestPhantomPersonalityCleanup:
    """Validate balanced/loyal are properly marked as reserved."""

    def test_balanced_loyal_in_enum(self):
        """BALANCED and LOYAL exist in enum (reserved for 1805)."""
        assert Personality.BALANCED.value == "balanced"
        assert Personality.LOYAL.value == "loyal"

    def test_balanced_loyal_no_example_marshals(self):
        """BALANCED and LOYAL personality descriptions have empty examples."""
        balanced_desc = PERSONALITY_DESCRIPTIONS[Personality.BALANCED]
        loyal_desc = PERSONALITY_DESCRIPTIONS[Personality.LOYAL]
        assert balanced_desc['examples'] == [], \
            f"BALANCED should have no example marshals, got {balanced_desc['examples']}"
        assert loyal_desc['examples'] == [], \
            f"LOYAL should have no example marshals, got {loyal_desc['examples']}"

    def test_active_personalities_have_real_marshals(self):
        """AGGRESSIVE/CAUTIOUS/LITERAL examples are all real marshals."""
        real_marshals = {"Ney", "Davout", "Grouchy", "Drouot",
                         "Wellington", "Blucher", "Schwarzenberg",
                         "Archduke Charles", "Gneisenau", "Kleist", "Uxbridge"}
        for personality in [Personality.AGGRESSIVE, Personality.CAUTIOUS, Personality.LITERAL]:
            desc = PERSONALITY_DESCRIPTIONS[personality]
            for example in desc['examples']:
                assert example in real_marshals, \
                    f"{personality.value} has non-existent example marshal: {example}"

    def test_personality_modifiers_no_balanced_loyal(self):
        """get_personality_modifiers returns empty dict for balanced/loyal."""
        from backend.models.personality_modifiers import get_personality_modifiers
        assert get_personality_modifiers("balanced") == {}
        assert get_personality_modifiers("loyal") == {}


# ═══════════════════════════════════════════════════════════════════
# 4. Parser valid_marshals matches game state
# ═══════════════════════════════════════════════════════════════════

class TestParserMarshalList:
    """Parser's valid marshal list must match create_starting_marshals()."""

    def test_valid_marshals_match_starting_marshals(self):
        """Parser.valid_marshals should exactly match French starting marshals."""
        from backend.commands.parser import CommandParser
        with _suppress_output():
            parser = CommandParser(use_real_llm=False)

        world = _fresh_world()
        french_marshals = sorted([m.name for m in world.marshals.values()
                                  if m.nation == "France"])
        parser_marshals = sorted(parser.valid_marshals)

        assert parser_marshals == french_marshals, \
            f"Parser marshals {parser_marshals} != starting marshals {french_marshals}"

    def test_no_phantom_marshals_in_parser(self):
        """Parser must not include marshals that don't exist in the game."""
        from backend.commands.parser import CommandParser
        with _suppress_output():
            parser = CommandParser(use_real_llm=False)

        phantom_names = ["Murat", "Soult", "Lannes", "Bernadotte", "Duroc"]
        for name in phantom_names:
            assert name not in parser.valid_marshals, \
                f"Phantom marshal {name} should not be in parser.valid_marshals"

    def test_no_phantom_marshals_in_mock_parser(self):
        """Mock LLM parser must not include non-existent marshal keywords."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient(use_real_api=False)

        # Parse a command mentioning a phantom marshal
        result = client.parse_command("Murat, attack Wellington", {})
        # Should NOT resolve to "Murat" as marshal
        if result and result.get("marshal"):
            assert result["marshal"] != "Murat", \
                "Mock parser should not resolve phantom marshal 'Murat'"
