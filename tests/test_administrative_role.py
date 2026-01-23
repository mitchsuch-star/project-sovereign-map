"""
Tests for Administrative Role Redemption System (Phase 3)

Tests cover:
1. Admin role stores troop data correctly
2. Admin role grants bonus action
3. Maximum one admin at a time
4. Dismiss transfers troops to nearby marshal (≤3 regions)
5. Dismiss disbands troops if no ally nearby
6. Dismiss grants +10 authority
7. Last marshal protection (only autonomy available)
8. Bonus action persists across turns
"""

import pytest
from backend.models.world_state import WorldState
from backend.commands.disobedience import DisobedienceSystem
from backend.models.marshal import Marshal
from backend.models.trust import Trust


class TestAdminRoleStoresTroopData:
    """Test that administrative role correctly stores troop data for future restoration."""

    def test_admin_role_stores_strength(self):
        """Admin marshal's strength is stored in administrative_strength."""
        world = WorldState()
        system = DisobedienceSystem()

        # Get Ney and set up redemption scenario
        ney = world.get_marshal("Ney")
        original_strength = ney.strength
        ney.trust = Trust(15)

        # Create redemption event and choose administrative role
        redemption_event = system._create_redemption_event(ney, world)
        result = system.handle_redemption_response(redemption_event, 'administrative_role', world)

        assert result['success'] is True
        assert ney.administrative is True
        assert ney.administrative_strength == original_strength
        assert ney.strength == 0  # Field strength is zeroed

    def test_admin_role_stores_location(self):
        """Admin marshal's location is stored in administrative_location."""
        world = WorldState()
        system = DisobedienceSystem()

        ney = world.get_marshal("Ney")
        original_location = ney.location
        ney.trust = Trust(15)

        redemption_event = system._create_redemption_event(ney, world)
        result = system.handle_redemption_response(redemption_event, 'administrative_role', world)

        assert result['success'] is True
        assert ney.administrative_location == original_location
        assert ney.location is None  # Field location is cleared


class TestAdminRoleGrantsBonusAction:
    """Test that administrative role grants +1 action per turn."""

    def test_admin_role_increments_bonus_actions(self):
        """Choosing administrative role increases world.bonus_actions by 1."""
        world = WorldState()
        system = DisobedienceSystem()

        assert world.bonus_actions == 0

        ney = world.get_marshal("Ney")
        ney.trust = Trust(15)

        redemption_event = system._create_redemption_event(ney, world)
        result = system.handle_redemption_response(redemption_event, 'administrative_role', world)

        assert result['success'] is True
        assert world.bonus_actions == 1

    def test_admin_role_increases_max_actions(self):
        """calculate_max_actions() returns 5 after admin role transfer."""
        world = WorldState()
        system = DisobedienceSystem()

        assert world.calculate_max_actions() == 4

        ney = world.get_marshal("Ney")
        ney.trust = Trust(15)

        redemption_event = system._create_redemption_event(ney, world)
        system.handle_redemption_response(redemption_event, 'administrative_role', world)

        assert world.calculate_max_actions() == 5

    def test_admin_role_result_includes_new_max_actions(self):
        """Result dict includes new_max_actions for frontend display."""
        world = WorldState()
        system = DisobedienceSystem()

        ney = world.get_marshal("Ney")
        ney.trust = Trust(15)

        redemption_event = system._create_redemption_event(ney, world)
        result = system.handle_redemption_response(redemption_event, 'administrative_role', world)

        assert 'new_max_actions' in result
        assert result['new_max_actions'] == 5


class TestAdminRoleMaxOne:
    """Test that maximum one marshal can be in administrative role."""

    def test_admin_role_not_available_if_one_exists(self):
        """Administrative role option not shown if an admin already exists."""
        world = WorldState()
        system = DisobedienceSystem()

        # First, put Ney in admin role
        ney = world.get_marshal("Ney")
        ney.trust = Trust(15)
        redemption_event = system._create_redemption_event(ney, world)
        system.handle_redemption_response(redemption_event, 'administrative_role', world)

        # Verify Ney is in admin
        assert len(world.get_admin_marshals()) == 1

        # Now try to trigger redemption for Davout
        davout = world.get_marshal("Davout")
        davout.trust = Trust(15)

        # Check available options - admin should NOT be available
        options = system._get_available_redemption_options(davout, world)
        option_ids = [opt['id'] for opt in options]

        assert 'grant_autonomy' in option_ids
        assert 'administrative_role' not in option_ids  # Already have one admin
        assert 'dismiss' in option_ids


class TestDismissTransfersTroopsNearby:
    """Test dismiss transfers troops to marshal within 3 regions."""

    def test_dismiss_transfers_to_nearby_marshal(self):
        """Troops transfer to nearest ally within 3 regions."""
        world = WorldState()
        system = DisobedienceSystem()

        ney = world.get_marshal("Ney")
        davout = world.get_marshal("Davout")

        ney_strength = ney.strength
        davout_original_strength = davout.strength
        ney.trust = Trust(15)

        # Ney at Belgium, Davout at Paris - should be within 3 regions
        redemption_event = system._create_redemption_event(ney, world)
        result = system.handle_redemption_response(redemption_event, 'dismiss', world)

        assert result['success'] is True
        assert result['dismissed'] is True
        # Davout should have received Ney's troops
        assert davout.strength == davout_original_strength + ney_strength
        # Ney should be removed from marshals
        assert 'Ney' not in world.marshals


class TestDismissDisbandsTroopsFar:
    """Test dismiss disbands troops if no ally within 3 regions."""

    def test_dismiss_disbands_if_no_nearby_ally(self):
        """Troops disband if all marshals are >3 regions away."""
        world = WorldState()
        system = DisobedienceSystem()

        # Move all other French marshals far away
        davout = world.get_marshal("Davout")
        grouchy = world.get_marshal("Grouchy")

        # Move them to distant regions (more than 3 hops from Belgium)
        davout.location = "Spain"
        grouchy.location = "Italy"

        ney = world.get_marshal("Ney")  # At Belgium
        davout_original_strength = davout.strength
        grouchy_original_strength = grouchy.strength
        ney.trust = Trust(15)

        redemption_event = system._create_redemption_event(ney, world)
        result = system.handle_redemption_response(redemption_event, 'dismiss', world)

        assert result['success'] is True
        # No troops transferred - all marshals too far
        assert davout.strength == davout_original_strength
        assert grouchy.strength == grouchy_original_strength
        # Message should mention dispersed
        assert 'dispersed' in result['message'].lower()


class TestDismissGrantsAuthority:
    """Test dismiss grants +10 authority."""

    def test_dismiss_adds_authority_bonus(self):
        """Dismissing a marshal adds +10 to authority."""
        world = WorldState()
        system = DisobedienceSystem()

        # Start with lower authority to test the increase
        world.authority_tracker.authority = 70
        original_authority = world.authority_tracker.authority

        ney = world.get_marshal("Ney")
        ney.trust = Trust(15)

        redemption_event = system._create_redemption_event(ney, world)
        result = system.handle_redemption_response(redemption_event, 'dismiss', world)

        assert result['success'] is True
        assert 'authority_bonus' in result
        assert result['authority_bonus'] == 10
        assert world.authority_tracker.authority == original_authority + 10

    def test_dismiss_authority_capped_at_100(self):
        """Authority doesn't exceed 100 after dismiss bonus."""
        world = WorldState()
        system = DisobedienceSystem()

        # Set authority near max
        world.authority_tracker.authority = 95

        ney = world.get_marshal("Ney")
        ney.trust = Trust(15)

        redemption_event = system._create_redemption_event(ney, world)
        system.handle_redemption_response(redemption_event, 'dismiss', world)

        assert world.authority_tracker.authority == 100  # Capped, not 105


class TestLastMarshalOnlyAutonomy:
    """Test that last field marshal only sees autonomy option."""

    def test_last_marshal_only_autonomy_available(self):
        """When only 1 field marshal remains, only autonomy is available."""
        world = WorldState()
        system = DisobedienceSystem()

        # Remove all marshals except Ney
        del world.marshals["Davout"]
        del world.marshals["Grouchy"]

        # Verify only 1 field marshal
        assert len(world.get_field_marshals()) == 1

        ney = world.get_marshal("Ney")
        ney.trust = Trust(15)

        options = system._get_available_redemption_options(ney, world)
        option_ids = [opt['id'] for opt in options]

        assert option_ids == ['grant_autonomy']
        assert 'administrative_role' not in option_ids
        assert 'dismiss' not in option_ids

    def test_two_marshals_shows_all_options(self):
        """When 2+ field marshals exist, all options are available."""
        world = WorldState()
        system = DisobedienceSystem()

        # Remove one marshal, keep two
        del world.marshals["Grouchy"]

        # Verify 2 field marshals
        assert len(world.get_field_marshals()) == 2

        ney = world.get_marshal("Ney")
        ney.trust = Trust(15)

        options = system._get_available_redemption_options(ney, world)
        option_ids = [opt['id'] for opt in options]

        assert 'grant_autonomy' in option_ids
        assert 'administrative_role' in option_ids
        assert 'dismiss' in option_ids


class TestBonusActionPersistsAcrossTurns:
    """Test that bonus actions persist across turn advancement."""

    def test_bonus_action_persists_after_advance_turn(self):
        """bonus_actions doesn't reset when turn advances."""
        world = WorldState()
        system = DisobedienceSystem()

        ney = world.get_marshal("Ney")
        ney.trust = Trust(15)

        # Grant admin role
        redemption_event = system._create_redemption_event(ney, world)
        system.handle_redemption_response(redemption_event, 'administrative_role', world)

        assert world.bonus_actions == 1
        assert world.calculate_max_actions() == 5

        # Advance turn
        world.advance_turn()

        # Bonus should persist
        assert world.bonus_actions == 1
        assert world.calculate_max_actions() == 5
        assert world.actions_remaining == 5

    def test_multiple_turns_maintain_bonus(self):
        """Bonus actions remain through multiple turn advances."""
        world = WorldState()
        system = DisobedienceSystem()

        ney = world.get_marshal("Ney")
        ney.trust = Trust(15)

        redemption_event = system._create_redemption_event(ney, world)
        system.handle_redemption_response(redemption_event, 'administrative_role', world)

        # Advance multiple turns
        for _ in range(5):
            world.advance_turn()

        assert world.bonus_actions == 1
        assert world.calculate_max_actions() == 5


class TestFieldAndAdminMarshalHelpers:
    """Test the new get_field_marshals() and get_admin_marshals() helpers."""

    def test_get_field_marshals_excludes_admin(self):
        """get_field_marshals() doesn't include marshals in admin role."""
        world = WorldState()
        system = DisobedienceSystem()

        initial_field = len(world.get_field_marshals())
        assert initial_field == 3  # Ney, Davout, Grouchy

        # Put Ney in admin role
        ney = world.get_marshal("Ney")
        ney.trust = Trust(15)
        redemption_event = system._create_redemption_event(ney, world)
        system.handle_redemption_response(redemption_event, 'administrative_role', world)

        assert len(world.get_field_marshals()) == 2
        field_names = [m.name for m in world.get_field_marshals()]
        assert 'Ney' not in field_names
        assert 'Davout' in field_names
        assert 'Grouchy' in field_names

    def test_get_admin_marshals_includes_admin(self):
        """get_admin_marshals() returns marshals in admin role."""
        world = WorldState()
        system = DisobedienceSystem()

        assert len(world.get_admin_marshals()) == 0

        ney = world.get_marshal("Ney")
        ney.trust = Trust(15)
        redemption_event = system._create_redemption_event(ney, world)
        system.handle_redemption_response(redemption_event, 'administrative_role', world)

        admin_marshals = world.get_admin_marshals()
        assert len(admin_marshals) == 1
        assert admin_marshals[0].name == 'Ney'


class TestFindNearestMarshalWithinRange:
    """Test the find_nearest_marshal_within_range() helper."""

    def test_finds_marshal_within_range(self):
        """Returns marshal within max_distance."""
        world = WorldState()

        # Ney at Belgium, Davout at Paris
        result = world.find_nearest_marshal_within_range(
            from_location="Belgium",
            nation="France",
            max_distance=3,
            exclude_marshal="Ney"
        )

        assert result is not None
        marshal, distance = result
        assert marshal.name in ["Davout", "Grouchy"]
        assert distance <= 3

    def test_returns_none_if_none_in_range(self):
        """Returns None if no marshal within range."""
        world = WorldState()

        # Move all French marshals far away
        world.get_marshal("Davout").location = "Spain"
        world.get_marshal("Grouchy").location = "Italy"

        result = world.find_nearest_marshal_within_range(
            from_location="Belgium",
            nation="France",
            max_distance=1,
            exclude_marshal="Ney"
        )

        assert result is None

    def test_excludes_specified_marshal(self):
        """Doesn't return the excluded marshal even if in range."""
        world = WorldState()

        # Put Davout right next to Ney
        world.get_marshal("Davout").location = "Belgium"

        result = world.find_nearest_marshal_within_range(
            from_location="Belgium",
            nation="France",
            max_distance=0,
            exclude_marshal="Davout"
        )

        # Should find Ney (also at Belgium) or None if Ney excluded too
        if result:
            marshal, _ = result
            assert marshal.name != "Davout"

    def test_excludes_admin_marshals(self):
        """Doesn't return marshals in administrative role."""
        world = WorldState()
        system = DisobedienceSystem()

        # Put Davout in admin
        davout = world.get_marshal("Davout")
        davout.administrative = True
        davout.strength = 0

        result = world.find_nearest_marshal_within_range(
            from_location="Belgium",
            nation="France",
            max_distance=10,
            exclude_marshal="Ney"
        )

        if result:
            marshal, _ = result
            assert marshal.name != "Davout"


class TestDemandObedienceRemoved:
    """Test that demand_obedience is no longer a valid option."""

    def test_demand_obedience_returns_invalid(self):
        """Choosing demand_obedience returns error."""
        world = WorldState()
        system = DisobedienceSystem()

        ney = world.get_marshal("Ney")
        ney.trust = Trust(15)

        redemption_event = system._create_redemption_event(ney, world)
        result = system.handle_redemption_response(redemption_event, 'demand_obedience', world)

        assert result['success'] is False
        assert 'Invalid choice' in result['message']

    def test_demand_obedience_not_in_options(self):
        """demand_obedience is not in available options."""
        world = WorldState()
        system = DisobedienceSystem()

        ney = world.get_marshal("Ney")
        ney.trust = Trust(15)

        options = system._get_available_redemption_options(ney, world)
        option_ids = [opt['id'] for opt in options]

        assert 'demand_obedience' not in option_ids
