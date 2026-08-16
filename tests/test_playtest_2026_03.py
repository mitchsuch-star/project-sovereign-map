"""
Playtest bugfix tests — March 2026 review.

C1: Armistice stranded marshal deadlock
C2: Same-nation self-combat
M1: Raw internal state name in diplomacy message
M2: "recruit infantry at Paris" parse failure
"""
import pytest
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.game_logic.diplomacy import (
    cleanup_war_end, _find_friendly_retreat
)


# ═══════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════

def _make_world():
    world = WorldState()
    world.current_turn = 5
    return world


def _make_game_state(world=None):
    if world is None:
        world = _make_world()
    return {"world": world}


# ═══════════════════════════════════════════════════════════════════════════
# C1: ARMISTICE STRANDED MARSHAL DEADLOCK
# ═══════════════════════════════════════════════════════════════════════════

class TestC1EngagementCheckUsesWarStatus:
    """Engagement check must use is_at_war(), not just nation != nation."""

    def test_non_war_foreign_marshal_does_not_block_attack(self):
        """Marshal from non-warring nation in same region shouldn't block attacks elsewhere."""
        world = _make_world()
        executor = CommandExecutor()

        # Setup: France at war with Britain, armistice with Prussia
        diplo_key_war = "|".join(sorted(["France", "Britain"]))
        diplo_key_peace = "|".join(sorted(["France", "Prussia"]))
        world.diplomatic_states[diplo_key_war] = "WAR"
        world.diplomatic_states[diplo_key_peace] = "ARMISTICE"

        # French marshal in Belgium with a Prussian marshal (armistice, not war)
        ney = world.marshals.get("Ney")
        if ney:
            ney.location = "Belgium"
            ney.strength = 50000

        # Put a Prussian marshal in Belgium too
        gneisenau = world.marshals.get("Gneisenau")
        if gneisenau:
            gneisenau.location = "Belgium"
            gneisenau.strength = 17000

        # Put a British marshal in Waterloo (adjacent, at war)
        wellington = world.marshals.get("Wellington")
        if wellington:
            wellington.location = "Waterloo"
            wellington.strength = 40000

        if not all([ney, gneisenau, wellington]):
            pytest.skip("Required marshals not found")

        # Ney should be able to attack Wellington despite Gneisenau being in Belgium
        game_state = _make_game_state(world)
        result = executor.execute(
            {"action": "attack", "marshal": "Ney", "target": "Wellington"},
            game_state
        )
        # Should NOT get "Cannot attack elsewhere while engaged" error
        assert "engaged" not in result.get("message", "").lower() or result.get("success", False)

    def test_war_foreign_marshal_still_blocks_attack_elsewhere(self):
        """Marshal from warring nation in same region SHOULD block attacks elsewhere."""
        world = _make_world()
        executor = CommandExecutor()

        diplo_key = "|".join(sorted(["France", "Britain"]))
        world.diplomatic_states[diplo_key] = "WAR"

        ney = world.marshals.get("Ney")
        wellington = world.marshals.get("Wellington")
        if not ney or not wellington:
            pytest.skip("Required marshals not found")

        # Both in Belgium — at war
        ney.location = "Belgium"
        ney.strength = 50000
        wellington.location = "Belgium"
        wellington.strength = 40000

        # Try to attack a different region — should be blocked
        game_state = _make_game_state(world)
        result = executor.execute(
            {"action": "attack", "marshal": "Ney", "target": "Waterloo"},
            game_state
        )
        msg = result.get("message", "").lower()
        assert "engaged" in msg or not result.get("success", True)


class TestC1ForceRetreatOnWarEnd:
    """cleanup_war_end() must not strand marshals — and, since WIN-D3, must
    not TELEPORT them either.

    ── CONSCIOUS FLIP, August 16, 2026 (WIN-D3 "The Road Home") ────────────
    Both assertions below used to read "he is no longer on that soil", which
    the March-2026 C1 fix satisfied by relocating him across the map for free
    in complete silence. `_force_retreat_displaced_marshals` is RETIRED
    (WAR_WITHDRAWAL_SPEC §3, gate §7a) and the evacuation corridor replaces
    it: the marshal STAYS, is granted temporary right of transit, and is
    handed a free march order home that the player can see, cancel or
    override. The C1 deadlock these tests were written against is closed more
    directly than before — he can now legally move — and that is what is
    pinned here instead of the teleport.
    """

    def test_war_end_does_not_teleport_the_enemy_off_our_soil(self):
        """The retired teleport moves nobody. (Pin on the retirement itself.)"""
        world = _make_world()

        gneisenau = world.marshals.get("Gneisenau")
        if not gneisenau:
            pytest.skip("Gneisenau not found")

        gneisenau.location = "Belgium"
        gneisenau.strength = 17000

        belgium = world.get_region("Belgium")
        if belgium:
            belgium.controller = "France"

        diplo_key = "|".join(sorted(["France", "Prussia"]))
        world.diplomatic_states[diplo_key] = "ARMISTICE"
        cleanup_war_end(world, diplo_key)

        assert gneisenau.location == "Belgium", (
            "cleanup_war_end must no longer relocate a marshal — the corridor "
            "gives him a road, not a teleport")

    def test_war_end_does_not_teleport_us_off_theirs(self):
        world = _make_world()

        davout = world.marshals.get("Davout")
        if not davout:
            pytest.skip("Davout not found")

        davout.location = "Berlin"
        davout.strength = 30000

        berlin = world.get_region("Berlin")
        if berlin:
            berlin.controller = "Prussia"

        diplo_key = "|".join(sorted(["France", "Prussia"]))
        world.diplomatic_states[diplo_key] = "ARMISTICE"
        cleanup_war_end(world, diplo_key)

        assert davout.location == "Berlin"

    def test_the_corridor_covers_what_the_teleport_used_to(self):
        """The case C1 existed for, taken through the real seam.

        Going through `set_diplomatic_state` (the ONE ending-agnostic
        chokepoint, per PT-J1) rather than `cleanup_war_end`, the marshal
        standing on the ex-enemy's soil gets exactly what the design
        promises: passage, and an order home.
        """
        from backend.game_logic.diplomacy import set_diplomatic_state
        from backend.game_logic.withdrawal import is_road_home_order

        world = _make_world()
        davout = world.marshals.get("Davout")
        if not davout:
            pytest.skip("Davout not found")

        davout.location = "Berlin"
        davout.strength = 30000
        berlin = world.get_region("Berlin")
        if berlin:
            berlin.controller = "Prussia"

        set_diplomatic_state(world, "France", "Prussia", "WAR")
        set_diplomatic_state(world, "France", "Prussia", "ARMISTICE")

        assert davout.location == "Berlin", "he marches, he is not moved"
        assert is_road_home_order(davout.strategic_order), (
            "a marshal on the ex-enemy's soil must be handed the road home")

    def test_force_retreat_cancels_strategic_orders(self):
        """Retreated marshal should have strategic orders cancelled."""
        world = _make_world()

        gneisenau = world.marshals.get("Gneisenau")
        if not gneisenau:
            pytest.skip("Gneisenau not found")

        gneisenau.location = "Belgium"
        gneisenau.strength = 17000

        # Give Gneisenau a strategic order
        from backend.models.marshal import StrategicOrder
        gneisenau.strategic_order = StrategicOrder(
            command_type="PURSUE", target="Ney", target_type="marshal",
            started_turn=3, original_command="pursue Ney"
        )

        belgium = world.get_region("Belgium")
        if belgium:
            belgium.controller = "France"

        diplo_key = "|".join(sorted(["France", "Prussia"]))
        world.diplomatic_states[diplo_key] = "ARMISTICE"
        cleanup_war_end(world, diplo_key)

        assert gneisenau.strategic_order is None

    def test_no_retreat_if_in_own_territory(self):
        """Marshal in own territory shouldn't be forced to retreat."""
        world = _make_world()

        gneisenau = world.marshals.get("Gneisenau")
        if not gneisenau:
            pytest.skip("Gneisenau not found")

        # Gneisenau is Prussian, in Prussian territory — should stay
        gneisenau.location = "Berlin"
        gneisenau.strength = 17000

        berlin = world.get_region("Berlin")
        if berlin:
            berlin.controller = "Prussia"

        original_location = gneisenau.location

        diplo_key = "|".join(sorted(["France", "Prussia"]))
        world.diplomatic_states[diplo_key] = "ARMISTICE"
        cleanup_war_end(world, diplo_key)

        assert gneisenau.location == original_location

    def test_no_retreat_for_uninvolved_nations(self):
        """Marshal from unrelated nation shouldn't be affected."""
        world = _make_world()

        wellington = world.marshals.get("Wellington")
        if not wellington:
            pytest.skip("Wellington not found")

        # Wellington is British, in Belgium (French territory)
        # But armistice is France-Prussia, not France-Britain
        wellington.location = "Belgium"
        wellington.strength = 40000

        belgium = world.get_region("Belgium")
        if belgium:
            belgium.controller = "France"

        original_location = wellington.location

        diplo_key = "|".join(sorted(["France", "Prussia"]))
        world.diplomatic_states[diplo_key] = "ARMISTICE"
        cleanup_war_end(world, diplo_key)

        # Wellington should NOT have been moved — he's British, not Prussian
        assert wellington.location == original_location

    def test_destroyed_marshal_not_retreated(self):
        """Marshal with 0 strength shouldn't be retreated."""
        world = _make_world()

        gneisenau = world.marshals.get("Gneisenau")
        if not gneisenau:
            pytest.skip("Gneisenau not found")

        gneisenau.location = "Belgium"
        gneisenau.strength = 0

        belgium = world.get_region("Belgium")
        if belgium:
            belgium.controller = "France"

        original_location = gneisenau.location

        diplo_key = "|".join(sorted(["France", "Prussia"]))
        world.diplomatic_states[diplo_key] = "ARMISTICE"
        cleanup_war_end(world, diplo_key)

        assert gneisenau.location == original_location


class TestC1FindFriendlyRetreat:
    """BFS retreat finder should locate nearest friendly region."""

    def test_finds_adjacent_friendly(self):
        world = _make_world()
        gneisenau = world.marshals.get("Gneisenau")
        if not gneisenau:
            pytest.skip("Gneisenau not found")

        gneisenau.location = "Belgium"
        gneisenau.strength = 17000

        # Make sure at least one adjacent region to Belgium is Prussian
        berlin = world.get_region("Berlin")
        if berlin:
            berlin.controller = "Prussia"

        result = _find_friendly_retreat(world, gneisenau)
        assert result != ""
        region = world.get_region(result)
        assert region is not None
        assert region.controller == "Prussia"

    def test_bfs_finds_non_adjacent_friendly(self):
        """If no adjacent friendly region, BFS should search further."""
        world = _make_world()
        gneisenau = world.marshals.get("Gneisenau")
        if not gneisenau:
            pytest.skip("Gneisenau not found")

        gneisenau.location = "Belgium"
        gneisenau.strength = 17000

        # Set all regions adjacent to Belgium as French
        belgium = world.get_region("Belgium")
        if belgium:
            for adj_name in belgium.adjacent_regions:
                adj = world.get_region(adj_name)
                if adj:
                    adj.controller = "France"

        # But Berlin is still Prussian (further away)
        berlin = world.get_region("Berlin")
        if berlin:
            berlin.controller = "Prussia"

        result = _find_friendly_retreat(world, gneisenau)
        assert result != ""
        region = world.get_region(result)
        assert region is not None
        assert region.controller == "Prussia"


# ═══════════════════════════════════════════════════════════════════════════
# C2: SAME-NATION SELF-COMBAT
# ═══════════════════════════════════════════════════════════════════════════

class TestC2SameNationCombatGuard:
    """resolve_battle() must reject same-nation combat."""

    def test_same_nation_auto_target_prevented(self):
        """AI auto-target must not select same-nation marshals."""
        world = _make_world()

        # Britain at war with France
        diplo_key = "|".join(sorted(["France", "Britain"]))
        world.diplomatic_states[diplo_key] = "WAR"

        wellington = world.marshals.get("Wellington")
        uxbridge = world.marshals.get("Uxbridge")
        if not wellington or not uxbridge:
            pytest.skip("Wellington/Uxbridge not found")

        # Both British, in same region
        wellington.location = "Belgium"
        wellington.strength = 40000
        uxbridge.location = "Belgium"
        uxbridge.strength = 15000

        # Nation-aware enemy finder must not return same-nation marshals
        result = world._find_nearest_enemy_for_nation("Belgium", "Britain")
        if result:
            enemy, dist = result
            assert enemy.nation != "Britain", (
                f"Auto-target returned same-nation marshal: {enemy.name}"
            )

    def test_different_nation_combat_still_works(self):
        """Normal combat between warring nations should work fine."""
        from backend.game_logic.combat import CombatResolver

        world = _make_world()
        ney = world.marshals.get("Ney")
        wellington = world.marshals.get("Wellington")
        if not ney or not wellington:
            pytest.skip("Ney/Wellington not found")

        diplo_key = "|".join(sorted(["France", "Britain"]))
        world.diplomatic_states[diplo_key] = "WAR"

        ney.location = "Belgium"
        ney.strength = 50000
        wellington.location = "Belgium"
        wellington.strength = 40000

        resolver = CombatResolver()
        result = resolver.resolve_battle(ney, wellington, world)
        assert result.get("outcome") != "cancelled"


class TestC2FindNearestEnemyNationAware:
    """find_nearest_enemy must not return same-nation marshals for AI."""

    def test_player_perspective_find_nearest_enemy(self):
        """find_nearest_enemy should still work for player perspective."""
        world = _make_world()

        diplo_key = "|".join(sorted(["France", "Britain"]))
        world.diplomatic_states[diplo_key] = "WAR"

        wellington = world.marshals.get("Wellington")
        if not wellington:
            pytest.skip("Wellington not found")

        result = world.find_nearest_enemy("Paris")
        # Should find a non-France marshal
        if result:
            enemy, dist = result
            assert enemy.nation != "France"

    def test_nation_aware_find_does_not_return_same_nation(self):
        """_find_nearest_enemy_for_nation must not return same-nation marshals."""
        world = _make_world()

        # Britain at war with France
        diplo_key = "|".join(sorted(["France", "Britain"]))
        world.diplomatic_states[diplo_key] = "WAR"

        result = world._find_nearest_enemy_for_nation("Belgium", "Britain")
        if result:
            enemy, dist = result
            assert enemy.nation != "Britain", (
                f"Nation-aware enemy finder returned same-nation marshal: {enemy.name} ({enemy.nation})"
            )


# ═══════════════════════════════════════════════════════════════════════════
# M1: RAW INTERNAL STATE NAME IN DIPLOMACY MESSAGE
# ═══════════════════════════════════════════════════════════════════════════

class TestM1DiplomaticDisplayNames:
    """Internal state names must be translated to player-facing display names."""

    def test_armistice_losing_displays_as_armistice(self):
        """'armistice_losing' should display as 'Armistice', not 'Armistice Losing'."""
        from backend.game_logic.diplomatic_dialogue import _display_proposal_type
        assert _display_proposal_type("armistice_losing") == "Armistice"

    def test_armistice_winning_displays_as_armistice(self):
        from backend.game_logic.diplomatic_dialogue import _display_proposal_type
        assert _display_proposal_type("armistice_winning") == "Armistice"

    def test_non_aggression_displays_correctly(self):
        from backend.game_logic.diplomatic_dialogue import _display_proposal_type
        assert _display_proposal_type("non_aggression") == "Non-Aggression Pact"

    def test_war_declaration_on_armistice_treaty_uses_display_name(self):
        """War declaration warning should show 'Armistice' not 'Armistice Losing'."""
        world = _make_world()
        executor = CommandExecutor()

        # Set up an armistice_losing treaty with Prussia
        diplo_key = "|".join(sorted(["France", "Prussia"]))
        world.diplomatic_states[diplo_key] = "ARMISTICE"
        world.active_treaties[diplo_key] = {
            "type": "armistice_losing",
            "nations": ["France", "Prussia"],
            "clauses": [],
            "turn_signed": 3,
        }
        # Clear cooldown so war declaration reaches the treaty warning
        world.armistice_cooldowns = {}

        game_state = _make_game_state(world)
        result = executor.execute(
            {"command": {"action": "diplomatic_declare_war",
                         "diplomatic_data": {"target_nation": "Prussia", "action": "diplomatic_declare_war", "war_objective": "conquest"}}},
            game_state
        )
        msg = result.get("message", "")
        # Should say "Armistice" not "Armistice Losing"
        assert "Armistice Losing" not in msg, f"Raw internal name leaked: {msg}"
        assert "Armistice" in msg, f"Display name missing from message: {msg}"
        # Should use "an" not "a" before "Armistice"
        assert "an Armistice" in msg, f"Wrong article: {msg}"


# ═══════════════════════════════════════════════════════════════════════════
# M2: "recruit infantry at Paris" PARSE FAILURE
# ═══════════════════════════════════════════════════════════════════════════

class TestM2RecruitWithoutMarshal:
    """'recruit infantry at Paris' should parse successfully."""

    def test_recruit_infantry_at_location_parses(self):
        """Parser must handle 'recruit [type] at [location]' without marshal name."""
        from backend.commands.parser import CommandParser

        world = _make_world()
        parser = CommandParser()
        result = parser.parse("recruit infantry at Paris", None, world=world)

        assert result.get("success"), f"Parse failed: {result.get('error')}"
        assert result["command"]["action"] == "recruit"
        assert result["command"]["target"] == "Paris"

    def test_recruit_cavalry_at_location_parses(self):
        from backend.commands.parser import CommandParser

        world = _make_world()
        parser = CommandParser()
        result = parser.parse("recruit cavalry at Belgium", None, world=world)

        assert result.get("success"), f"Parse failed: {result.get('error')}"
        assert result["command"]["action"] == "recruit"

    def test_recruit_with_marshal_still_works(self):
        """Original pattern 'Davout recruit at Paris' must still work."""
        from backend.commands.parser import CommandParser

        world = _make_world()
        parser = CommandParser()
        result = parser.parse("Davout recruit at Paris", None, world=world)

        assert result.get("success"), f"Parse failed: {result.get('error')}"
        assert result["command"]["marshal"] == "Davout"
        assert result["command"]["action"] == "recruit"

    def test_troop_type_words_not_treated_as_marshal(self):
        """'infantry', 'cavalry', 'artillery' should not be fuzzy-matched as marshal names."""
        from backend.commands.parser import CommandParser

        world = _make_world()
        parser = CommandParser()

        for troop_word in ["infantry", "cavalry", "artillery"]:
            result = parser.parse(f"recruit {troop_word} at Paris", None, world=world)
            assert result.get("success"), (
                f"'{troop_word}' was treated as a marshal name: {result.get('error')}"
            )


# ═══════════════════════════════════════════════════════════════════════════
# C3: TURN COUNTER SKIP (double advance_turn guard)
# ═══════════════════════════════════════════════════════════════════════════

class TestC3DoubleAdvanceGuard:
    """end_turn() must only advance the turn counter once."""

    def test_advance_turn_increments_by_one(self):
        """Normal advance_turn should increment by exactly 1."""
        world = _make_world()
        world.current_turn = 10

        world.advance_turn()
        assert world.current_turn == 11

    def test_end_turn_produces_sequential_turns(self):
        """Full end_turn cycle should produce sequential turn numbers."""
        from backend.game_logic.turn_manager import TurnManager

        world = _make_world()
        world.current_turn = 2
        executor = CommandExecutor()
        game_state = _make_game_state(world)

        turn_manager = TurnManager(world, executor=executor)
        result = turn_manager.end_turn(game_state)

        assert result["turn_ended"] == 2
        assert result["next_turn"] == 3, (
            f"Turn should advance 2→3, got 2→{result['next_turn']}"
        )
        assert world.current_turn == 3

    def test_multiple_end_turns_are_sequential(self):
        """Multiple end_turn calls should produce strictly sequential turns."""
        from backend.game_logic.turn_manager import TurnManager

        world = _make_world()
        world.current_turn = 1
        executor = CommandExecutor()
        game_state = _make_game_state(world)

        turns_seen = [1]
        for _ in range(5):
            turn_manager = TurnManager(world, executor=executor)
            result = turn_manager.end_turn(game_state)
            turns_seen.append(world.current_turn)

        # Should be strictly sequential: 1, 2, 3, 4, 5, 6
        for i in range(1, len(turns_seen)):
            assert turns_seen[i] == turns_seen[i-1] + 1, (
                f"Turn sequence broken: {turns_seen}"
            )

    def test_end_turn_with_game_over_still_advances_once(self):
        """If victory check fires, turn should still advance exactly once."""
        from backend.game_logic.turn_manager import TurnManager

        world = _make_world()
        world.current_turn = 5
        # Force game over by giving player all regions
        for region in world.regions.values():
            region.controller = "France"

        executor = CommandExecutor()
        game_state = _make_game_state(world)

        turn_manager = TurnManager(world, executor=executor)
        result = turn_manager.end_turn(game_state)

        assert world.current_turn == 6, (
            f"Turn should advance 5→6 (even with game over), got {world.current_turn}"
        )
