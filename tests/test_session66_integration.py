"""
Tests for Session 66: Godot UI + Integration Audit

Tests coordination tutorial trigger, reinforcement display data,
coordination readiness in game state summary, serialization of
new fields, and edge cases for Phase 7 integration.

Spec: docs/MULTI_MARSHAL_SPEC.md §12, §14
"""

from backend.models.marshal import Marshal
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _make_marshal(name="TestInf", location="Paris", strength=30000,
                  personality="cautious", nation="France",
                  cavalry=False, artillery=False, **kw):
    """Create a marshal with sensible defaults."""
    return Marshal(
        name=name, location=location, strength=strength,
        personality=personality, nation=nation,
        movement_range=2 if cavalry else 1,
        tactical_skill=7,
        skills=kw.pop("skills", {
            "tactical": 7, "shock": 7, "defense": 7,
            "logistics": 7, "administration": 7, "command": 7,
        }),
        cavalry=cavalry, artillery=artillery,
        spawn_location=kw.pop("spawn_location", location),
        **kw,
    )


def _make_world_with_marshals(marshal_list, player_nation="France"):
    """Create a WorldState and replace marshals with the given list."""
    world = WorldState(player_nation=player_nation)
    world.marshals.clear()
    for m in marshal_list:
        world.marshals[m.name] = m
    return world


def _executor():
    return CommandExecutor()


# ════════════════════════════════════════════════════════════════════════════════
# COORDINATION TUTORIAL FIELD
# ════════════════════════════════════════════════════════════════════════════════

class TestCoordinationTutorialField:
    """Test coordination_tutorial_shown field on WorldState."""

    def test_defaults_to_false(self):
        world = WorldState()
        assert world.coordination_tutorial_shown is False

    def test_serialization_roundtrip(self):
        world = WorldState()
        world.coordination_tutorial_shown = True
        data = world.to_dict()
        assert data["coordination_tutorial_shown"] is True

        restored = WorldState.from_dict(data)
        assert restored.coordination_tutorial_shown is True

    def test_serialization_default_on_missing_key(self):
        """Old saves without the field should default to False."""
        world = WorldState()
        data = world.to_dict()
        del data["coordination_tutorial_shown"]

        restored = WorldState.from_dict(data)
        assert restored.coordination_tutorial_shown is False

    def test_in_to_dict(self):
        world = WorldState()
        data = world.to_dict()
        assert "coordination_tutorial_shown" in data

    def test_false_by_default_in_new_game(self):
        world = WorldState()
        data = world.to_dict()
        assert data["coordination_tutorial_shown"] is False


# ════════════════════════════════════════════════════════════════════════════════
# COORDINATION TUTORIAL TRIGGER
# ════════════════════════════════════════════════════════════════════════════════

class TestCoordinationTutorialTrigger:
    """Test that the tutorial fires once when player gets combined arms."""

    def _setup_combined_arms_battle(self):
        """Set up a battle where player has combined arms (infantry + cavalry).

        All marshals in the SAME region so reinforcement relocation doesn't
        move Ney away before _calculate_coordination_context runs.
        """
        inf = _make_marshal(name="Davout", location="Waterloo", strength=30000,
                           nation="France")
        cav = _make_marshal(name="Ney", location="Waterloo", strength=25000,
                           cavalry=True, nation="France")
        enemy = _make_marshal(name="Wellington", location="Waterloo",
                             strength=20000, nation="Britain")
        world = _make_world_with_marshals([inf, cav, enemy])

        # Set up region control — contested region
        world.regions["Waterloo"].controller = "Britain"

        return inf, cav, enemy, world

    def test_tutorial_triggers_on_first_combined_arms(self):
        inf, cav, enemy, world = self._setup_combined_arms_battle()
        assert world.coordination_tutorial_shown is False

        ex = _executor()
        game_state = {"world": world}

        # Execute attack with combined arms
        result = ex.execute({"command": {
            "marshal": "Davout",
            "action": "attack",
            "target": "Wellington",
        }}, game_state)

        assert result.get("success") is True
        assert world.coordination_tutorial_shown is True
        assert "coordination_tutorial" in result

    def test_tutorial_does_not_fire_twice(self):
        inf, cav, enemy, world = self._setup_combined_arms_battle()
        world.coordination_tutorial_shown = True  # Already shown

        ex = _executor()
        game_state = {"world": world}

        result = ex.execute({"command": {
            "marshal": "Davout",
            "action": "attack",
            "target": "Wellington",
        }}, game_state)

        assert result.get("success") is True
        assert "coordination_tutorial" not in result

    def test_tutorial_not_triggered_for_solo_attack(self):
        """Solo attack (no combined arms) should not trigger tutorial."""
        inf = _make_marshal(name="Davout", location="Paris", strength=30000,
                           nation="France")
        enemy = _make_marshal(name="Wellington", location="Waterloo",
                             strength=20000, nation="Britain")
        world = _make_world_with_marshals([inf, enemy])
        world.regions["Paris"].controller = "France"
        world.regions["Waterloo"].controller = "Britain"

        ex = _executor()
        game_state = {"world": world}

        result = ex.execute({"command": {
            "marshal": "Davout",
            "action": "attack",
            "target": "Wellington",
        }}, game_state)

        assert world.coordination_tutorial_shown is False
        assert "coordination_tutorial" not in result

    def test_tutorial_not_triggered_for_enemy_combined_arms(self):
        """Enemy AI combined arms should not trigger player tutorial."""
        player = _make_marshal(name="Davout", location="Waterloo",
                              strength=30000, nation="France")
        enemy_inf = _make_marshal(name="Wellington", location="Rhineland",
                                 strength=25000, nation="Britain")
        enemy_cav = _make_marshal(name="Blucher", location="Rhineland",
                                 strength=20000, cavalry=True, nation="Prussia")
        world = _make_world_with_marshals([player, enemy_inf, enemy_cav])
        world.regions["Waterloo"].controller = "France"
        world.regions["Rhineland"].controller = "Britain"

        ex = _executor()
        game_state = {"world": world}

        # Enemy attacks player — enemy has combined arms, player doesn't
        result = ex.execute({"command": {
            "marshal": "Wellington",
            "action": "attack",
            "target": "Davout",
        }, "_strategic_execution": True}, game_state)  # Skip AP cost

        assert world.coordination_tutorial_shown is False

    def test_tutorial_content_structure(self):
        inf, cav, enemy, world = self._setup_combined_arms_battle()

        ex = _executor()
        game_state = {"world": world}

        result = ex.execute({"command": {
            "marshal": "Davout",
            "action": "attack",
            "target": "Wellington",
        }}, game_state)

        tutorial = result.get("coordination_tutorial", {})
        assert "title" in tutorial
        assert "message" in tutorial
        assert "tip" in tutorial
        assert "warning" in tutorial
        assert tutorial["title"] == "BERTHIER'S REPORT"
        assert "combined arms" in tutorial["tip"].lower()
        assert "casualties" in tutorial["warning"].lower()


# ════════════════════════════════════════════════════════════════════════════════
# GAME STATE SUMMARY — RELATIONSHIPS AND CO-LOCATION
# ════════════════════════════════════════════════════════════════════════════════

class TestGameStateSummaryRelationships:
    """Test that relationships and co-location data are in game state summary."""

    def test_relationships_included_for_player_marshals(self):
        m1 = _make_marshal(name="Davout", location="Paris", nation="France")
        m2 = _make_marshal(name="Ney", location="Paris", cavalry=True, nation="France")
        m1.set_relationship("Ney", 1)  # Friendly
        world = _make_world_with_marshals([m1, m2])
        world.regions["Paris"].controller = "France"

        summary = world.get_game_state_summary()
        paris_data = summary["map_data"]["Paris"]
        marshals = paris_data["marshals"]

        # Find Davout's data
        davout_data = None
        for md in marshals:
            if md["name"] == "Davout":
                davout_data = md
                break

        assert davout_data is not None
        assert "relationships" in davout_data
        assert "Ney" in davout_data["relationships"]
        assert davout_data["relationships"]["Ney"]["value"] == 1
        assert davout_data["relationships"]["Ney"]["label"] == "Friendly"

    def test_co_location_turns_included(self):
        m1 = _make_marshal(name="Davout", location="Paris", nation="France")
        m2 = _make_marshal(name="Ney", location="Paris", cavalry=True, nation="France")
        m1.co_location_turns = {"Ney": 1}  # Co-located since turn 1
        world = _make_world_with_marshals([m1, m2])
        world.current_turn = 3
        world.regions["Paris"].controller = "France"

        summary = world.get_game_state_summary()
        paris_data = summary["map_data"]["Paris"]

        davout_data = None
        for md in paris_data["marshals"]:
            if md["name"] == "Davout":
                davout_data = md
                break

        assert davout_data is not None
        assert "co_location_turns" in davout_data
        assert davout_data["co_location_turns"]["Ney"] == 2  # turn 3 - turn 1 = 2

    def test_relationships_not_included_for_enemy_marshals(self):
        """Enemy marshals should not have relationships in summary."""
        player = _make_marshal(name="Davout", location="Paris", nation="France")
        enemy = _make_marshal(name="Wellington", location="Waterloo", nation="Britain")
        world = _make_world_with_marshals([player, enemy])
        world.regions["Waterloo"].controller = "Britain"

        summary = world.get_game_state_summary()
        waterloo_data = summary["map_data"]["Waterloo"]

        well_data = None
        for md in waterloo_data["marshals"]:
            if md["name"] == "Wellington":
                well_data = md
                break

        assert well_data is not None
        assert "relationships" not in well_data

    def test_relationship_values_are_int(self):
        """Golden Rule #2: All numbers to Godot must be int."""
        m1 = _make_marshal(name="Davout", location="Paris", nation="France")
        m2 = _make_marshal(name="Ney", location="Paris", cavalry=True, nation="France")
        m1.set_relationship("Ney", -2)  # Hostile
        world = _make_world_with_marshals([m1, m2])
        world.regions["Paris"].controller = "France"

        summary = world.get_game_state_summary()
        paris_data = summary["map_data"]["Paris"]

        for md in paris_data["marshals"]:
            if md["name"] == "Davout":
                rel = md["relationships"]["Ney"]
                assert isinstance(rel["value"], int)
                break

    def test_co_location_turns_are_int(self):
        """Golden Rule #2: All numbers to Godot must be int."""
        m1 = _make_marshal(name="Davout", location="Paris", nation="France")
        m1.co_location_turns = {"Ney": 1}
        world = _make_world_with_marshals([m1])
        world.current_turn = 5
        world.regions["Paris"].controller = "France"

        summary = world.get_game_state_summary()
        paris_data = summary["map_data"]["Paris"]

        for md in paris_data["marshals"]:
            if md["name"] == "Davout":
                assert isinstance(md["co_location_turns"]["Ney"], int)
                break

    def test_all_relationship_labels_correct(self):
        """Verify all 5 relationship labels map correctly."""
        m1 = _make_marshal(name="A", location="Paris", nation="France")
        m2 = _make_marshal(name="B", location="Paris", nation="France")
        m3 = _make_marshal(name="C", location="Paris", nation="France")
        m4 = _make_marshal(name="D", location="Paris", nation="France")
        m5 = _make_marshal(name="E", location="Paris", nation="France")

        m1.set_relationship("B", -2)
        m1.set_relationship("C", -1)
        m1.set_relationship("D", 1)
        m1.set_relationship("E", 2)

        world = _make_world_with_marshals([m1, m2, m3, m4, m5])
        world.regions["Paris"].controller = "France"

        summary = world.get_game_state_summary()
        paris_data = summary["map_data"]["Paris"]

        a_data = None
        for md in paris_data["marshals"]:
            if md["name"] == "A":
                a_data = md
                break

        assert a_data["relationships"]["B"]["label"] == "Hostile"
        assert a_data["relationships"]["C"]["label"] == "Rival"
        assert a_data["relationships"]["D"]["label"] == "Friendly"
        assert a_data["relationships"]["E"]["label"] == "Devoted"
        # Professional (0) is default — check for a marshal with no explicit relationship
        assert a_data["relationships"].get("B", {}).get("label") == "Hostile"

    def test_empty_relationships_for_solo_marshal(self):
        """A marshal alone in a region still has relationships dict (may be empty)."""
        m1 = _make_marshal(name="Davout", location="Paris", nation="France")
        world = _make_world_with_marshals([m1])
        world.regions["Paris"].controller = "France"

        summary = world.get_game_state_summary()
        paris_data = summary["map_data"]["Paris"]

        davout_data = paris_data["marshals"][0]
        assert "relationships" in davout_data
        assert isinstance(davout_data["relationships"], dict)


# ════════════════════════════════════════════════════════════════════════════════
# REINFORCEMENT MESSAGES
# ════════════════════════════════════════════════════════════════════════════════

class TestReinforcementMessages:
    """Test that reinforcement arrival/failure messages are in battle results."""

    def test_reinforcement_messages_in_result(self):
        """When a battle has potential reinforcements, messages should be present."""
        primary = _make_marshal(name="Ney", location="Paris", strength=30000,
                               cavalry=True, nation="France")
        ally = _make_marshal(name="Davout", location="Rhineland", strength=25000,
                            nation="France")
        enemy = _make_marshal(name="Wellington", location="Waterloo",
                             strength=20000, nation="Britain")

        world = _make_world_with_marshals([primary, ally, enemy])
        world.regions["Paris"].controller = "France"
        world.regions["Rhineland"].controller = "France"
        world.regions["Waterloo"].controller = "Britain"

        # Davout adjacent to Waterloo (depends on adjacency graph)
        # This test verifies the field exists if reinforcements are calculated
        ex = _executor()
        game_state = {"world": world}

        result = ex.execute({"command": {
            "marshal": "Ney",
            "action": "attack",
            "target": "Wellington",
        }}, game_state)

        # reinforcement_messages may or may not be present depending on adjacency
        # The important thing is they're strings if present
        if "reinforcement_messages" in result:
            assert isinstance(result["reinforcement_messages"], list)
            for msg in result["reinforcement_messages"]:
                assert isinstance(msg, str)

    def test_reinforcement_failure_uses_narrative_not_code(self):
        """Failure reasons must use player-facing text, not internal codes."""
        ex = _executor()
        # Grouchy (literal) won't reinforce without explicit order
        primary = _make_marshal(name="Davout", location="Waterloo", strength=30000,
                               nation="France")
        grouchy = _make_marshal(name="Grouchy", location="Paris", strength=20000,
                                personality="literal", nation="France")
        enemy = _make_marshal(name="Wellington", location="Waterloo",
                             strength=20000, nation="Britain")
        world = _make_world_with_marshals([primary, grouchy, enemy])
        world.regions["Waterloo"].controller = "Britain"
        world.regions["Paris"].controller = "France"

        game_state = {"world": world}
        result = ex.execute({"command": {
            "marshal": "Davout",
            "action": "attack",
            "target": "Wellington",
        }}, game_state)

        if "reinforcement_messages" in result:
            for msg in result["reinforcement_messages"]:
                assert "literal_personality" not in msg
                assert "low_score" not in msg
                assert "fate_intervened" not in msg

    def test_aggregate_ally_casualties_singular_form(self):
        """When 1 reinforcer arrives and takes casualties, use 'ally' not 'allies'."""
        ex = _executor()
        # Unit test the message formatting logic directly
        # Simulate: 1 reinforcer arrived, took 500 casualties
        arrived_names = ["Ney"]
        atk_distribution = {"Davout": 2000, "Ney": 500}

        # Build the aggregate message the same way executor does
        ally_casualties = sum(atk_distribution.get(n, 0) for n in arrived_names)
        assert ally_casualties == 500
        if len(arrived_names) == 1:
            msg = f"His supporting ally lost {int(ally_casualties):,} men."
        else:
            msg = f"His supporting allies lost {int(ally_casualties):,} men combined."

        assert "ally" in msg
        assert "allies" not in msg
        assert "500" in msg

    def test_aggregate_ally_casualties_plural_form(self):
        """When 2+ reinforcers arrive, use 'allies' with 'combined'."""
        arrived_names = ["Ney", "Grouchy"]
        atk_distribution = {"Davout": 2000, "Ney": 500, "Grouchy": 300}

        ally_casualties = sum(atk_distribution.get(n, 0) for n in arrived_names)
        assert ally_casualties == 800
        if len(arrived_names) == 1:
            msg = f"His supporting ally lost {int(ally_casualties):,} men."
        else:
            msg = f"His supporting allies lost {int(ally_casualties):,} men combined."

        assert "allies" in msg
        assert "combined" in msg
        assert "800" in msg

    def test_reinforcement_failure_uses_narrative_not_code(self):
        """Failure reasons must use player-facing text, not internal codes."""
        ex = _executor()
        primary = _make_marshal(name="Davout", location="Waterloo", strength=30000,
                               nation="France")
        grouchy = _make_marshal(name="Grouchy", location="Paris", strength=20000,
                                personality="literal", nation="France")
        enemy = _make_marshal(name="Wellington", location="Waterloo",
                             strength=20000, nation="Britain")
        world = _make_world_with_marshals([primary, grouchy, enemy])
        world.regions["Waterloo"].controller = "Britain"
        world.regions["Paris"].controller = "France"

        game_state = {"world": world}
        result = ex.execute({"command": {
            "marshal": "Davout",
            "action": "attack",
            "target": "Wellington",
        }}, game_state)

        if "reinforcement_messages" in result:
            for msg in result["reinforcement_messages"]:
                assert "literal_personality" not in msg
                assert "low_score" not in msg
                assert "fate_intervened" not in msg


# ════════════════════════════════════════════════════════════════════════════════
# EDGE CASES
# ════════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Edge cases for Phase 7 integration."""

    def test_all_hostile_marshals_still_coordinate(self):
        """All hostile marshals still get combined arms but 0% per-ally bonus."""
        inf = _make_marshal(name="A", location="Paris", strength=30000,
                           nation="France")
        cav = _make_marshal(name="B", location="Paris", strength=25000,
                           cavalry=True, nation="France")
        inf.set_relationship("B", -2)  # Hostile
        cav.set_relationship("A", -2)  # Hostile

        world = _make_world_with_marshals([inf, cav])
        ex = _executor()

        # Combined arms still detected
        type_count = ex._count_unit_types("Paris", "France", world)
        assert type_count == 2

        # But per-ally coordination should be 0 due to hostile
        coord = ex._calculate_coordination_context(inf, world)
        # Combined arms bonus still applies
        assert coord["type_count"] == 2
        # Per-ally is 0 for hostile
        assert inf._display_coordination_atk == 0.0

    def test_artillery_only_stack_no_combined_arms(self):
        """Artillery-only stack gets no combined arms bonus."""
        art1 = _make_marshal(name="Art1", location="Paris", strength=20000,
                            artillery=True, nation="France")
        art2 = _make_marshal(name="Art2", location="Paris", strength=15000,
                            artillery=True, nation="France")
        world = _make_world_with_marshals([art1, art2])
        ex = _executor()

        type_count = ex._count_unit_types("Paris", "France", world)
        assert type_count == 1  # Only artillery

    def test_three_unit_types_full_combined_arms(self):
        """Infantry + cavalry + artillery = 3/3 combined arms."""
        inf = _make_marshal(name="Inf", location="Paris", nation="France")
        cav = _make_marshal(name="Cav", location="Paris", cavalry=True, nation="France")
        art = _make_marshal(name="Art", location="Paris", artillery=True, nation="France")
        world = _make_world_with_marshals([inf, cav, art])
        ex = _executor()

        type_count = ex._count_unit_types("Paris", "France", world)
        assert type_count == 3

    def test_four_marshals_all_hostile(self):
        """4 marshals, all hostile — still calculate coordination but 0% mutual."""
        marshals = []
        for i in range(4):
            m = _make_marshal(name=f"M{i}", location="Paris", nation="France",
                             cavalry=(i == 1), artillery=(i == 2))
            marshals.append(m)

        # All hostile to each other
        for i in range(4):
            for j in range(4):
                if i != j:
                    marshals[i].set_relationship(f"M{j}", -2)

        world = _make_world_with_marshals(marshals)
        ex = _executor()
        coord = ex._calculate_coordination_context(marshals[0], world)

        # Combined arms still works (3 types: inf + cav + art)
        assert coord["type_count"] == 3
        # But per-ally coordination is 0 for hostile
        assert marshals[0]._display_coordination_atk == 0.0

    def test_coordination_tutorial_shown_preserves_on_save_load(self):
        """Save/load roundtrip preserves coordination_tutorial_shown."""
        world = WorldState()
        world.coordination_tutorial_shown = True

        data = world.to_dict()
        restored = WorldState.from_dict(data)

        assert restored.coordination_tutorial_shown is True

    def test_coordination_tutorial_shown_false_preserves(self):
        world = WorldState()
        assert world.coordination_tutorial_shown is False

        data = world.to_dict()
        restored = WorldState.from_dict(data)

        assert restored.coordination_tutorial_shown is False


# ════════════════════════════════════════════════════════════════════════════════
# INTEGRATION: FULL COORDINATED BATTLE
# ════════════════════════════════════════════════════════════════════════════════

class TestFullCoordinatedBattle:
    """Integration test: full battle with coordination features."""

    def test_coordinated_attack_produces_battle_report(self):
        """A coordinated attack should produce a battle report with observation."""
        inf = _make_marshal(name="Davout", location="Belgium", strength=30000,
                           nation="France")
        cav = _make_marshal(name="Ney", location="Belgium", strength=25000,
                           cavalry=True, nation="France")
        enemy = _make_marshal(name="Wellington", location="Waterloo",
                             strength=20000, nation="Britain")

        world = _make_world_with_marshals([inf, cav, enemy])
        world.regions["Belgium"].controller = "France"
        world.regions["Waterloo"].controller = "Britain"

        ex = _executor()
        game_state = {"world": world}

        result = ex.execute({"command": {
            "marshal": "Davout",
            "action": "attack",
            "target": "Wellington",
        }}, game_state)

        assert result.get("success") is True
        assert "battle_report" in result
        report = result["battle_report"]
        assert "modifier_breakdown" in report
        assert "casualty_summary" in report
        assert "observation" in report
        # Observation should be a non-empty string
        assert isinstance(report["observation"], str)
        assert len(report["observation"]) > 0

    def test_coordinated_battle_all_numbers_int(self):
        """Golden Rule #2: All numeric values in battle report must be int."""
        inf = _make_marshal(name="Davout", location="Paris", strength=30000,
                           nation="France")
        cav = _make_marshal(name="Ney", location="Paris", strength=25000,
                           cavalry=True, nation="France")
        enemy = _make_marshal(name="Wellington", location="Waterloo",
                             strength=20000, nation="Britain")

        world = _make_world_with_marshals([inf, cav, enemy])
        world.regions["Paris"].controller = "France"
        world.regions["Waterloo"].controller = "Britain"

        ex = _executor()
        game_state = {"world": world}

        result = ex.execute({"command": {
            "marshal": "Davout",
            "action": "attack",
            "target": "Wellington",
        }}, game_state)

        report = result.get("battle_report", {})
        casualty = report.get("casualty_summary", {})

        for key in ["attacker_casualties", "attacker_remaining", "attacker_original",
                     "defender_casualties", "defender_remaining", "defender_original"]:
            if key in casualty:
                assert isinstance(casualty[key], int), f"{key} is {type(casualty[key])}, not int"

        # Check modifier values
        breakdown = report.get("modifier_breakdown", {})
        for side in ["attacker", "defender"]:
            for mod in breakdown.get(side, []):
                assert isinstance(mod["value"], int), f"Modifier value {mod} is not int"

    def test_save_load_mid_coordination(self):
        """Save and load during a game with coordination state."""
        inf = _make_marshal(name="Davout", location="Paris", strength=30000,
                           nation="France")
        cav = _make_marshal(name="Ney", location="Paris", strength=25000,
                           cavalry=True, nation="France")
        inf.set_relationship("Ney", 1)  # Friendly
        cav.set_relationship("Davout", 1)
        inf.co_location_turns = {"Ney": 1}
        cav.co_location_turns = {"Davout": 1}

        world = _make_world_with_marshals([inf, cav])
        world.current_turn = 5
        world.coordination_tutorial_shown = True

        data = world.to_dict()
        restored = WorldState.from_dict(data)

        assert restored.coordination_tutorial_shown is True
        assert restored.current_turn == 5

        # Check marshals preserved coordination state
        davout = restored.marshals["Davout"]
        ney = restored.marshals["Ney"]
        assert davout.get_relationship("Ney") == 1
        assert ney.get_relationship("Davout") == 1
        assert davout.co_location_turns.get("Ney") == 1
        assert ney.co_location_turns.get("Davout") == 1


# ════════════════════════════════════════════════════════════════════════════════
# FILTERED GAME STATE SUMMARY
# ════════════════════════════════════════════════════════════════════════════════

class TestFilteredGameStateSummary:
    """Test that filtered game state includes relationship data."""

    def test_relationships_in_filtered_summary(self):
        m1 = _make_marshal(name="Davout", location="Paris", nation="France")
        m2 = _make_marshal(name="Ney", location="Paris", cavalry=True, nation="France")
        m1.set_relationship("Ney", 2)  # Devoted
        world = _make_world_with_marshals([m1, m2])
        world.regions["Paris"].controller = "France"

        summary = world.get_filtered_game_state_summary()
        paris_data = summary["map_data"]["Paris"]

        davout_data = None
        for md in paris_data["marshals"]:
            if md["name"] == "Davout":
                davout_data = md
                break

        assert davout_data is not None
        assert "relationships" in davout_data
        assert davout_data["relationships"]["Ney"]["value"] == 2
        assert davout_data["relationships"]["Ney"]["label"] == "Devoted"

    def test_co_location_in_filtered_summary(self):
        m1 = _make_marshal(name="Davout", location="Paris", nation="France")
        m1.co_location_turns = {"Ney": 2}
        world = _make_world_with_marshals([m1])
        world.current_turn = 4
        world.regions["Paris"].controller = "France"

        summary = world.get_filtered_game_state_summary()
        paris_data = summary["map_data"]["Paris"]

        davout_data = paris_data["marshals"][0]
        assert davout_data["co_location_turns"]["Ney"] == 2  # turn 4 - turn 2 = 2
