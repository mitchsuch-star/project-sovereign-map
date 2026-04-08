"""Phase 2B+ tests: R81 — Nation Elimination.

0 regions = eliminated. Marshals removed, treaties cleaned, vassals cleaned.
"""

from backend.models.world_state import WorldState
from backend.game_logic.diplomacy import _is_nation_eliminated


def _make_world():
    world = WorldState()
    world.current_turn = 5
    return world


def _set_diplo_state(world, a, b, state):
    key = world._make_diplo_key(a, b)
    world.diplomatic_states[key] = state


class TestR81NationElimination:
    """R81: 0 regions = eliminated — remove marshals automatically."""

    def test_capture_last_region_triggers_elimination(self):
        """Capturing a nation's last region removes all its marshals."""
        world = _make_world()
        # Give Saxony only one region
        for name, region in world.regions.items():
            if region.controller == "Saxony":
                region.controller = "France"  # Take all Saxony regions first
        # Give back one region
        saxony_region = None
        for name, region in world.regions.items():
            if name == "Saxony":
                region.controller = "Saxony"
                saxony_region = name
                break
        if not saxony_region:
            # Just use any region
            for name, region in world.regions.items():
                region.controller = "Saxony"
                saxony_region = name
                break

        # Verify Saxony has marshals
        saxony_marshals = [n for n, m in world.marshals.items() if m.nation == "Saxony"]
        assert len(saxony_marshals) > 0, "Saxony should have marshals initially"

        # Capture last region
        world.capture_region(saxony_region, "France")

        # All Saxony marshals should be removed
        remaining = [n for n, m in world.marshals.items() if m.nation == "Saxony"]
        assert len(remaining) == 0, f"Saxony marshals should be eliminated, found: {remaining}"

    def test_elimination_cleans_treaties_and_states(self):
        """Active treaties removed, diplo states → PEACE on elimination."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "ALLIANCE")
        key = world._make_diplo_key("France", "Saxony")
        world.active_treaties[key] = {
            "nations": ["France", "Saxony"],
            "type": "alliance",
            "clauses": [],
            "turn_signed": 3,
            "harshness": 0,
        }

        # Remove all Saxony regions except one
        for name, region in world.regions.items():
            if region.controller == "Saxony":
                region.controller = "France"
        saxony_region = None
        for name, region in world.regions.items():
            if name == "Saxony":
                region.controller = "Saxony"
                saxony_region = name
                break
        if not saxony_region:
            for name in list(world.regions.keys()):
                world.regions[name].controller = "Saxony"
                saxony_region = name
                break

        world.capture_region(saxony_region, "France")

        # Treaty should be removed
        assert key not in world.active_treaties
        # Diplo state should be PEACE
        assert world.diplomatic_states.get(key) == "PEACE"

    def test_elimination_cancels_orders_targeting_removed(self):
        """Strategic orders targeting removed marshals are cancelled."""
        world = _make_world()
        from backend.models.marshal import StrategicOrder
        # Give a French marshal an order targeting a Saxony marshal
        saxony_marshals = [n for n, m in world.marshals.items() if m.nation == "Saxony"]
        french_marshals = [n for n, m in world.marshals.items() if m.nation == "France"]
        if saxony_marshals and french_marshals:
            target_name = saxony_marshals[0]
            pursuer = french_marshals[0]
            order = StrategicOrder(
                command_type="PURSUE",
                target=target_name,
                target_type="marshal",
                started_turn=1,
                original_command="pursue test",
                path=[],
            )
            world.marshals[pursuer].strategic_order = order

            # Remove all Saxony regions except one, then capture
            for name, region in world.regions.items():
                if region.controller == "Saxony":
                    region.controller = "France"
            for name in list(world.regions.keys()):
                if name == "Saxony":
                    world.regions[name].controller = "Saxony"
                    break
            world.capture_region("Saxony", "France")

            # Order should be cancelled
            assert world.marshals[pursuer].strategic_order is None

    def test_elimination_cleans_vassals(self):
        """Both as-vassal and as-lord vassal relationships are cleaned."""
        world = _make_world()
        # Saxony as vassal of France
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 50, "autonomy": 2}
        # Some nation as vassal of Saxony (unusual but test edge case)
        world.vassals["Bavaria"] = {"lord": "Saxony", "loyalty": 40, "autonomy": 1}

        # Eliminate Saxony
        for name, region in world.regions.items():
            if region.controller == "Saxony":
                region.controller = "France"
        for name in list(world.regions.keys()):
            if name == "Saxony":
                world.regions[name].controller = "Saxony"
                break
        world.capture_region("Saxony", "France")

        assert "Saxony" not in world.vassals
        assert "Bavaria" not in world.vassals

    def test_player_nation_not_auto_eliminated(self):
        """Player losing last region does NOT trigger _eliminate_nation."""
        world = _make_world()
        french_regions = world.get_nation_regions("France")
        french_marshals_before = [n for n, m in world.marshals.items() if m.nation == "France"]

        # Remove all French regions except one
        for name in french_regions[1:]:
            world.regions[name].controller = "Austria"
        last_region = french_regions[0]

        # Enemy captures last French region
        world.capture_region(last_region, "Austria")

        # French marshals should NOT be removed (player elimination = game-over, separate path)
        french_marshals_after = [n for n, m in world.marshals.items() if m.nation == "France"]
        assert len(french_marshals_after) == len(french_marshals_before)

    def test_territory_cede_can_trigger_elimination(self):
        """Treaty ceding all remaining regions triggers elimination."""
        world = _make_world()
        # Get Saxony's regions and leave only one
        for name, region in world.regions.items():
            if region.controller == "Saxony":
                region.controller = "France"
        for name in list(world.regions.keys()):
            if name == "Saxony":
                world.regions[name].controller = "Saxony"
                break

        saxony_marshals = [n for n, m in world.marshals.items() if m.nation == "Saxony"]
        assert len(saxony_marshals) > 0

        # Ratify treaty with territory_cede clause (Saxony cedes territory to France)
        _set_diplo_state(world, "France", "Saxony", "WAR")
        # PL-20 §F: Elimination requires war_score >= 90
        diplo_key = world._make_diplo_key("France", "Saxony")
        if not hasattr(world, 'war_scores'):
            world.war_scores = {}
        world.war_scores[diplo_key] = 95
        proposal = {
            "type": "peace",
            "proposer_nation": "Saxony",
            "target_nation": "France",
            "sweeteners": [
                {"type": "territory_cede", "value": 0, "regions": ["Saxony"]},
            ],
            "demands": [],
            "clauses": [],
        }
        world._ratify_treaty(proposal)

        # Saxony should be eliminated
        remaining = [n for n, m in world.marshals.items() if m.nation == "Saxony"]
        assert len(remaining) == 0

    def test_is_nation_eliminated_simplified(self):
        """_is_nation_eliminated only checks regions."""
        world = _make_world()
        # Saxony has regions → not eliminated
        assert _is_nation_eliminated(world, "Saxony") is False

        # Remove all Saxony regions
        for region in world.regions.values():
            if region.controller == "Saxony":
                region.controller = "France"
        # Even if marshals remain, it should show eliminated (region check only)
        assert _is_nation_eliminated(world, "Saxony") is True

    def test_notification_on_elimination(self):
        """Elimination fires a notification."""
        world = _make_world()
        for name, region in world.regions.items():
            if region.controller == "Saxony":
                region.controller = "France"
        for name in list(world.regions.keys()):
            if name == "Saxony":
                world.regions[name].controller = "Saxony"
                break
        initial_count = len(world.notifications._pending)
        world.capture_region("Saxony", "France")
        assert len(world.notifications._pending) > initial_count

    def test_capture_non_last_region_no_elimination(self):
        """Capturing a region when nation has others doesn't trigger elimination."""
        world = _make_world()
        saxony_regions = world.get_nation_regions("Saxony")
        if len(saxony_regions) < 2:
            # Saxony only has one region in default setup, so give it another
            for name in list(world.regions.keys()):
                if world.regions[name].controller != "Saxony":
                    world.regions[name].controller = "Saxony"
                    break
            saxony_regions = world.get_nation_regions("Saxony")

        marshals_before = len([n for n, m in world.marshals.items() if m.nation == "Saxony"])
        # Capture one region (nation still has others)
        world.capture_region(saxony_regions[0], "France")
        marshals_after = len([n for n, m in world.marshals.items() if m.nation == "Saxony"])
        assert marshals_after == marshals_before
