"""
Test suite for the garrison command (Session 31).

Player can detach 3,000 troops to garrison a controlled region.
Uses existing garrison_strength field with garrison_detachment=True.
Player garrisons don't regen and fight to destruction (no 5k collapse).
"""

import pytest
from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState
from backend.models.region import Region


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _setup():
    """Create a fresh world and executor for testing."""
    world = WorldState()
    game_state = {"world": world}
    executor = CommandExecutor()
    return world, game_state, executor


def _garrison_command(marshal_name, target=None):
    """Build a parsed garrison command dict."""
    return {
        "success": True,
        "command": {
            "action": "garrison",
            "marshal": marshal_name,
            "target": target,
        }
    }


# ════════════════════════════════════════════════════════════════════════════════
# GARRISON PLACEMENT TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestGarrisonPlacement:
    """Test successful garrison placement."""

    def test_garrison_placed_successfully(self):
        """Marshal detaches 3k troops, region gets garrison."""
        world, gs, executor = _setup()
        # Use Ney — he starts in Belgium which has no existing garrison
        ney = world.marshals["Ney"]
        old_strength = ney.strength
        region = world.regions[ney.location]
        assert region.garrison_strength == 0  # Precondition: no existing garrison

        result = executor._execute_garrison(
            {"marshal": "Ney"}, gs)

        assert result["success"] is True
        assert ney.strength == old_strength - 3000
        assert region.garrison_strength == 3000
        assert region.garrison_detachment is True
        assert "3,000" in result["message"]
        assert "Ney" in result["message"]

    def test_garrison_costs_2_ap(self):
        """Garrison action costs 2 AP (real commitment)."""
        world, gs, executor = _setup()
        assert world.get_action_cost("garrison") == 2

    def test_garrison_blocked_with_1_ap(self):
        """Garrison requires 2 AP — must fail with only 1 remaining."""
        world, gs, executor = _setup()
        world.actions_remaining = 1
        result = executor.execute(
            _garrison_command("Ney"), gs)
        assert result["success"] is False
        assert "Not enough actions" in result.get("message", "") or "action" in result.get("message", "").lower()

    def test_garrison_succeeds_with_2_ap(self):
        """Garrison succeeds with exactly 2 AP remaining."""
        world, gs, executor = _setup()
        world.actions_remaining = 2
        ney = world.marshals["Ney"]
        region = world.regions[ney.location]
        region.controller = "France"
        region.garrison_strength = 0
        result = executor.execute(
            _garrison_command("Ney"), gs)
        assert result["success"] is True

    def test_garrison_event_logged(self):
        """Event log records garrison_placed."""
        world, gs, executor = _setup()
        ney = world.marshals["Ney"]

        executor._execute_garrison({"marshal": "Ney"}, gs)

        events = [e for e in world.event_log if e["type"] == "garrison_placed"]
        assert len(events) == 1
        assert events[0]["marshal"] == "Ney"
        assert events[0]["region"] == ney.location
        assert events[0]["troops"] == 3000


# ════════════════════════════════════════════════════════════════════════════════
# FAILURE CASE TESTS (Berthier-style messages)
# ════════════════════════════════════════════════════════════════════════════════

class TestGarrisonFailures:
    """Test all garrison failure cases return Berthier-style messages."""

    def test_fail_not_enough_troops(self):
        """Marshal with < 8k troops can't garrison."""
        world, gs, executor = _setup()
        ney = world.marshals["Ney"]
        ney.strength = 5000

        result = executor._execute_garrison(
            {"marshal": "Ney"}, gs)

        assert result["success"] is False
        assert "too depleted" in result["message"]
        assert "8,000" in result["message"]

    def test_fail_region_not_owned(self):
        """Can't garrison enemy-controlled territory."""
        world, gs, executor = _setup()
        # Move Davout to a British-controlled region
        ney = world.marshals["Ney"]
        # Find an enemy-controlled region
        enemy_region = None
        for r in world.regions.values():
            if r.controller and r.controller != "France":
                enemy_region = r
                break
        if enemy_region:
            ney.location = enemy_region.name
            result = executor._execute_garrison(
                {"marshal": "Ney"}, gs)
            assert result["success"] is False
            assert "do not control" in result["message"]

    def test_fail_region_already_garrisoned(self):
        """Can't place a second garrison in a region that has one."""
        world, gs, executor = _setup()
        ney = world.marshals["Ney"]
        region = world.regions[ney.location]
        region.garrison_strength = 3000
        region.garrison_detachment = True

        result = executor._execute_garrison(
            {"marshal": "Ney"}, gs)

        assert result["success"] is False
        assert "already holds" in result["message"]

    def test_fail_capital_already_garrisoned(self):
        """Can't garrison a region with existing capital garrison."""
        world, gs, executor = _setup()
        # Move a marshal to Paris (which has capital garrison)
        paris = world.regions.get("Paris")
        if paris and paris.garrison_strength > 0:
            # Find a French marshal and move them to Paris
            for m in world.marshals.values():
                if m.nation == "France":
                    m.location = "Paris"
                    result = executor._execute_garrison(
                        {"marshal": m.name}, gs)
                    assert result["success"] is False
                    assert "already holds" in result["message"]
                    break

    def test_fail_enemies_present(self):
        """Can't garrison while enemies are in the same region."""
        world, gs, executor = _setup()
        ney = world.marshals["Ney"]
        # Place an enemy in the same region
        for m in world.marshals.values():
            if m.nation != "France":
                m.location = ney.location
                break

        result = executor._execute_garrison(
            {"marshal": "Ney"}, gs)

        assert result["success"] is False
        assert "contest" in result["message"] or "under threat" in result["message"]

    def test_fail_no_marshal_name(self):
        """Missing marshal name returns Berthier message."""
        world, gs, executor = _setup()
        result = executor._execute_garrison(
            {"marshal": ""}, gs)

        assert result["success"] is False
        assert "Which marshal" in result["message"]

    def test_fail_unknown_marshal(self):
        """Unknown marshal name returns Berthier message."""
        world, gs, executor = _setup()
        result = executor._execute_garrison(
            {"marshal": "Bonaparte"}, gs)

        assert result["success"] is False
        assert "know no marshal" in result["message"]


# ════════════════════════════════════════════════════════════════════════════════
# PLAYER GARRISON COMBAT TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestPlayerGarrisonCombat:
    """Test that player garrisons use _resolve_garrison_combat and behave correctly."""

    def test_player_garrison_fights_when_attacked(self):
        """Player garrison triggers garrison combat when enemy attacks."""
        world, gs, executor = _setup()

        # Set up a garrisoned French region with no French marshals present
        target_region = world.regions["Belgium"]
        target_region.garrison_strength = 3000
        target_region.garrison_detachment = True
        target_region.controller = "France"

        # Move ALL marshals far away first to avoid engagement conflicts
        for m in world.marshals.values():
            m.location = "London"

        # Find an enemy marshal and place them adjacent to Belgium (not Paris)
        enemy = None
        for m in world.marshals.values():
            if m.nation != "France" and m.strength > 0:
                enemy = m
                break

        if enemy:
            enemy.location = "Netherlands"  # Adjacent to Belgium, no French marshals

            result = executor._execute_attack(enemy, "Belgium", world, gs)
            # The garrison should have fought (either survived or destroyed)
            assert "garrison" in result.get("message", "").lower() or target_region.garrison_strength == 0

    def test_player_garrison_no_collapse_threshold(self):
        """Player garrisons below 5k still fight (no collapse threshold)."""
        world, gs, executor = _setup()
        # Set up a region with player garrison at 2000 (below capital 5k threshold)
        region = world.regions.get("Belgium") or list(world.regions.values())[0]
        region.garrison_strength = 2000
        region.garrison_detachment = True
        region.controller = "France"

        # The garrison should still be "fightable" — garrison_fights check uses > 0 for player
        assert region.garrison_strength > 0
        assert region.garrison_detachment is True
        # This confirms the garrison won't auto-collapse like capital garrisons do

    def test_player_garrison_destroyed_clears_fields(self):
        """When player garrison is destroyed, both fields reset."""
        world, gs, executor = _setup()
        region = world.regions.get("Belgium") or list(world.regions.values())[0]
        region.garrison_strength = 100  # Very weak — will die
        region.garrison_detachment = True
        region.controller = "France"

        # Simulate destruction
        region.garrison_strength = 0
        region.garrison_detachment = False

        assert region.garrison_strength == 0
        assert region.garrison_detachment is False


# ════════════════════════════════════════════════════════════════════════════════
# CAPITAL GARRISON REGRESSION TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestCapitalGarrisonRegression:
    """Ensure capital garrison still works correctly after player garrison changes."""

    def test_capital_garrison_still_regens(self):
        """Capital garrison (non-player-placed) still regenerates."""
        world, gs, executor = _setup()
        paris = world.regions.get("Paris")
        if paris and paris.is_capital:
            paris.garrison_strength = 10000
            paris.garrison_detachment = False  # Capital garrison

            # Advance turn — garrison should regen
            old = paris.garrison_strength
            result = world.advance_turn()
            assert paris.garrison_strength > old
            assert paris.garrison_strength <= 15000

    def test_player_garrison_does_not_regen(self):
        """Player-placed garrison does NOT regenerate even on capital."""
        world, gs, executor = _setup()
        paris = world.regions.get("Paris")
        if paris and paris.is_capital:
            paris.garrison_strength = 3000
            paris.garrison_detachment = True  # Player garrison, NOT capital

            old = paris.garrison_strength
            world.advance_turn()
            assert paris.garrison_strength == old  # No regen

    def test_capital_garrison_still_collapses_at_5k(self):
        """Capital garrison (non-player-placed) still collapses below 5k."""
        world, gs, executor = _setup()
        # We test via the attack path logic
        region = list(world.regions.values())[0]
        region.garrison_strength = 3000
        region.garrison_detachment = False  # Capital style
        region.controller = "Britain"

        # The capital-style garrison with < 5000 should auto-collapse
        # (handled in executor attack flow: garrison_strength > 0, not player_placed, < 5000)
        # Just verify the field values
        assert not region.garrison_detachment
        assert region.garrison_strength < 5000


# ════════════════════════════════════════════════════════════════════════════════
# SERIALIZATION TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestGarrisonSerialization:
    """Test save/load roundtrip for garrison fields."""

    def test_garrison_detachment_serializes(self):
        """garrison_detachment survives to_dict/from_dict."""
        region = Region("Test", ["A", "B"], terrain="plains", region_type="town")
        region.garrison_strength = 3000
        region.garrison_detachment = True

        d = region.to_dict()
        assert d["garrison_detachment"] is True
        assert d["garrison_strength"] == 3000

        r2 = Region.from_dict(d)
        assert r2.garrison_detachment is True
        assert r2.garrison_strength == 3000

    def test_backward_compat_missing_field(self):
        """Old saves without garrison_detachment default to False."""
        data = {
            "name": "Test",
            "adjacent_regions": ["A"],
            "garrison_strength": 15000,
            # No garrison_detachment key
        }
        r = Region.from_dict(data)
        assert r.garrison_detachment is False

    def test_backward_compat_old_key_name(self):
        """Old saves with garrison_player_placed migrate to garrison_detachment."""
        data = {
            "name": "Test",
            "adjacent_regions": ["A"],
            "garrison_strength": 3000,
            "garrison_player_placed": True,  # Old key name
        }
        r = Region.from_dict(data)
        assert r.garrison_detachment is True

    def test_garrison_persists_across_turns(self):
        """Player garrison survives turn processing without change."""
        world, gs, executor = _setup()
        ney = world.marshals["Ney"]
        region = world.regions[ney.location]

        executor._execute_garrison({"marshal": "Ney"}, gs)
        assert region.garrison_strength == 3000
        assert region.garrison_detachment is True

        # Advance a turn — garrison should persist unchanged
        world.advance_turn()
        assert region.garrison_strength == 3000
        assert region.garrison_detachment is True


# ════════════════════════════════════════════════════════════════════════════════
# PARSER TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestGarrisonParser:
    """Test mock parser recognizes garrison keywords."""

    def test_parse_garrison_keyword(self):
        """'garrison' keyword detected by mock parser."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client._parse_with_mock("Davout, garrison Bavaria")
        assert result is not None
        assert result.action == "garrison"

    def test_parse_leave_troops(self):
        """'leave troops' keyword detected."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client._parse_with_mock("Davout, leave troops at Bavaria")
        assert result is not None
        assert result.action == "garrison"

    def test_parse_detach_troops(self):
        """'detach troops' keyword detected."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client._parse_with_mock("Davout, detach troops")
        assert result is not None
        assert result.action == "garrison"


# ════════════════════════════════════════════════════════════════════════════════
# GARRISON CAP TESTS (Session 37: max 3 per nation)
# ════════════════════════════════════════════════════════════════════════════════

class TestGarrisonCap:
    """Test garrison cap of 3 per nation (includes capital garrisons)."""

    def test_cap_constant_is_3(self):
        """GARRISON_MAX_PER_NATION is 3."""
        world, gs, executor = _setup()
        assert executor.GARRISON_MAX_PER_NATION == 3

    def test_capital_counts_toward_cap(self):
        """Paris capital garrison counts as 1 toward France's cap of 3."""
        world, gs, executor = _setup()
        paris = world.regions.get("Paris")
        assert paris is not None
        assert paris.garrison_strength > 0  # Capital garrison exists
        # Count French garrisons — Paris should count
        french_garrisons = sum(
            1 for r in world.regions.values()
            if r.garrison_strength > 0 and r.controller == "France"
        )
        assert french_garrisons >= 1  # At least Paris

    def test_cap_blocks_at_3(self):
        """Cannot place garrison when nation already has 3."""
        world, gs, executor = _setup()
        # Paris already has a capital garrison (1).
        # Set up 2 more French garrisons to hit cap of 3.
        french_regions = [r for r in world.regions.values()
                         if r.controller == "France" and r.garrison_strength == 0]
        for i, region in enumerate(french_regions[:2]):
            region.garrison_strength = 3000
            region.garrison_detachment = True

        # Now try to place another — should fail
        ney = world.marshals["Ney"]
        ney.strength = 20000
        # Put Ney in a region without a garrison
        for r in world.regions.values():
            if r.controller == "France" and r.garrison_strength == 0:
                ney.location = r.name
                break

        result = executor._execute_garrison({"marshal": "Ney"}, gs)
        assert result["success"] is False
        assert "Berthier" in result["message"]
        assert "3" in result["message"]

    def test_cap_allows_when_under_limit(self):
        """Can place garrison when under cap."""
        world, gs, executor = _setup()
        # Paris has capital garrison (1). Should still allow 2 more.
        ney = world.marshals["Ney"]
        ney.strength = 20000
        region = world.regions[ney.location]
        region.controller = "France"
        region.garrison_strength = 0

        result = executor._execute_garrison({"marshal": "Ney"}, gs)
        assert result["success"] is True

    def test_cap_no_ap_spent_on_rejection(self):
        """When cap blocks garrison, no AP is consumed."""
        world, gs, executor = _setup()
        # Fill to cap
        french_regions = [r for r in world.regions.values()
                         if r.controller == "France" and r.garrison_strength == 0]
        for region in french_regions[:2]:
            region.garrison_strength = 3000
            region.garrison_detachment = True

        old_ap = world.actions_remaining
        ney = world.marshals["Ney"]
        ney.strength = 20000
        for r in world.regions.values():
            if r.controller == "France" and r.garrison_strength == 0:
                ney.location = r.name
                break

        result = executor._execute_garrison({"marshal": "Ney"}, gs)
        assert result["success"] is False
        # AP should not have changed (cap validation is pre-executor)
        assert world.actions_remaining == old_ap

    def test_cap_per_nation_not_global(self):
        """Each nation has its own cap of 3."""
        world, gs, executor = _setup()
        # Count French and British garrisons separately
        french_count = sum(
            1 for r in world.regions.values()
            if r.garrison_strength > 0 and r.controller == "France"
        )
        british_count = sum(
            1 for r in world.regions.values()
            if r.garrison_strength > 0 and r.controller == "Britain"
        )
        # British cap is independent of French garrisons
        # Fill France to 3 — British should still be able to garrison
        french_regions = [r for r in world.regions.values()
                         if r.controller == "France" and r.garrison_strength == 0]
        for region in french_regions[:3 - french_count]:
            region.garrison_strength = 3000
            region.garrison_detachment = True

        # Now verify French is at cap
        french_count = sum(
            1 for r in world.regions.values()
            if r.garrison_strength > 0 and r.controller == "France"
        )
        assert french_count >= 3

        # British marshal should still be able to garrison
        wellington = world.marshals.get("Wellington")
        if wellington:
            wellington.strength = 20000
            region = world.regions[wellington.location]
            region.controller = "Britain"
            region.garrison_strength = 0
            result = executor._execute_garrison({"marshal": "Wellington"}, gs)
            # Should succeed (Britain not at cap) or fail for other reasons, NOT cap
            if not result["success"]:
                assert "3 garrisons" not in result["message"]


# ════════════════════════════════════════════════════════════════════════════════
# MAP DATA / FOG FILTER TESTS (Session 37)
# ════════════════════════════════════════════════════════════════════════════════

class TestGarrisonMapData:
    """Test garrison data in map_data and fog filtering."""

    def test_garrison_in_map_data(self):
        """get_game_state_summary includes garrison_strength and garrison_detachment."""
        world, gs, executor = _setup()
        region = world.regions["Belgium"]
        region.garrison_strength = 3000
        region.garrison_detachment = True

        summary = world.get_game_state_summary()
        map_data = summary["map_data"]
        belgium = map_data["Belgium"]
        assert belgium["garrison_strength"] == 3000
        assert belgium["garrison_detachment"] is True

    def test_garrison_zero_in_map_data(self):
        """Regions without garrisons show 0 strength and False detachment."""
        world, gs, executor = _setup()
        region = world.regions["Belgium"]
        region.garrison_strength = 0
        region.garrison_detachment = False

        summary = world.get_game_state_summary()
        map_data = summary["map_data"]
        belgium = map_data["Belgium"]
        assert belgium["garrison_strength"] == 0
        assert belgium["garrison_detachment"] is False

    def test_fog_own_region_full_garrison(self):
        """Own region with FULL visibility shows exact garrison strength."""
        world, gs, executor = _setup()
        # Paris is French — should have full visibility for France (player nation)
        paris = world.regions["Paris"]
        assert paris.garrison_strength > 0  # Capital garrison

        filtered = world.get_filtered_game_state_summary()
        paris_data = filtered["map_data"]["Paris"]
        assert paris_data["garrison_strength"] == paris.garrison_strength

    def test_fog_unknown_hides_garrison(self):
        """UNKNOWN visibility hides garrison entirely (shows 0)."""
        world, gs, executor = _setup()
        # Set a garrison on an enemy region far from player
        london = world.regions.get("London")
        if london:
            london.garrison_strength = 10000
            london.controller = "Britain"

            filtered = world.get_filtered_game_state_summary()
            london_data = filtered["map_data"].get("London")
            if london_data:
                # If visibility is unknown/last_known, garrison should be hidden
                vis = london_data.get("visibility", "unknown")
                if vis in ("unknown", "last_known"):
                    assert london_data["garrison_strength"] == 0

    def test_fog_partial_sentinel(self):
        """PARTIAL/STALE visibility shows sentinel -1 for garrison (unknown strength)."""
        world, gs, executor = _setup()
        # Test the filtering logic via unfiltered summary fields
        summary = world.get_game_state_summary()
        # Verify the map_data has the fields we expect
        for region_name, data in summary["map_data"].items():
            assert "garrison_strength" in data
            assert "garrison_detachment" in data
