"""
N4 War Status Panel — Backend Tests (24 cases per §N4j)

Tests build_active_wars() which produces the active_wars dict
for the HUD + detail popup. Covers: war scoring, fog filtering,
coalition tagging, armistice data, edge cases.
"""

from backend.models.world_state import WorldState
from backend.game_logic.war_status import build_active_wars
from backend.models.intel import FULL, PARTIAL


def make_world():
    """Create a fresh WorldState with all diplomatic states reset to PEACE."""
    world = WorldState(player_nation="France")
    # Clear default wars (Britain/Prussia start at WAR)
    for key in list(world.diplomatic_states.keys()):
        world.diplomatic_states[key] = "PEACE"
    return world


def set_war(world, opponent):
    """Set up a WAR state between France and opponent."""
    diplo_key = world._make_diplo_key("France", opponent)
    world.diplomatic_states[diplo_key] = "WAR"
    world.war_scores[diplo_key] = 0
    world.war_start_turns[diplo_key] = int(world.current_turn)
    world.war_exhaustion[opponent] = 0


def set_armistice(world, opponent, elapsed=0):
    """Set up an ARMISTICE state between France and opponent."""
    diplo_key = world._make_diplo_key("France", opponent)
    world.diplomatic_states[diplo_key] = "ARMISTICE"
    world.armistice_turns[diplo_key] = elapsed


def give_visibility(world, opponent, vis_tier):
    """Give the player visibility of an opponent's marshal locations."""
    for m in world.marshals.values():
        if m.nation == opponent and m.strength > 0:
            intel = world.get_region_intel(m.location)
            intel.visibility = vis_tier
            break


def clear_visibility(world, opponent):
    """Ensure opponent marshals have no visibility (UNKNOWN)."""
    from backend.models.intel import UNKNOWN
    for m in world.marshals.values():
        if m.nation == opponent and m.strength > 0:
            intel = world.get_region_intel(m.location)
            intel.visibility = UNKNOWN


# ======================================================
# Test 1: Empty wars list when no wars or armistices
# ======================================================

class TestNoWars:
    def test_empty_wars_when_no_wars_or_armistices(self):
        """§N4j-1: Returns empty wars list when no active wars or armistices."""
        world = make_world()
        result = build_active_wars(world)
        assert result["wars"] == []
        assert result["coalition"] is None


# ======================================================
# Test 2: Correct opponent, war_score, duration, started_turn
# ======================================================

class TestWarBasics:
    def test_correct_fields_for_active_war(self):
        """§N4j-2: Returns correct opponent, war_score, duration, started_turn."""
        world = make_world()
        world.current_turn = 5
        set_war(world, "Prussia")
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_start_turns[diplo_key] = 2
        world.war_scores[diplo_key] = 15

        result = build_active_wars(world)
        wars = result["wars"]
        assert len(wars) == 1
        w = wars[0]
        assert w["opponent"] == "Prussia"
        assert w["started_turn"] == 2
        assert w["duration"] == 3  # turn 5 - start 2


# ======================================================
# Test 3: War score sign from France's perspective
# ======================================================

class TestWarScorePerspective:
    def test_war_score_positive_when_france_winning(self):
        """§N4j-3: War score sign is from France's perspective (positive = winning)."""
        world = make_world()
        set_war(world, "Britain")
        diplo_key = world._make_diplo_key("France", "Britain")
        # Add battle records where France wins → positive battle score
        world.battle_records[diplo_key] = [
            {"turn": 1, "winner": "France", "attacker": "France",
             "defender": "Britain", "attacker_casualties": 2000,
             "defender_casualties": 3000, "location": "Belgium"},
            {"turn": 2, "winner": "France", "attacker": "France",
             "defender": "Britain", "attacker_casualties": 2000,
             "defender_casualties": 3000, "location": "Netherlands"},
        ]

        result = build_active_wars(world)
        w = [w for w in result["wars"] if w["opponent"] == "Britain"][0]
        assert w["war_score"] > 0  # France's perspective should be positive


# ======================================================
# Test 4: All numbers are int()
# ======================================================

class TestIntWrapping:
    def test_all_numbers_are_int(self):
        """§N4j-4: All numbers are int() (Godot golden rule)."""
        world = make_world()
        set_war(world, "Prussia")
        give_visibility(world, "Prussia", FULL)

        result = build_active_wars(world)
        w = [w for w in result["wars"] if w["opponent"] == "Prussia"][0]
        assert isinstance(w["war_score"], int)
        assert isinstance(w["duration"], int)
        assert isinstance(w["started_turn"], int)
        assert isinstance(w["battles_fought"], int)
        assert isinstance(w["decisive_won"], int)
        for key in w["breakdown"]:
            assert isinstance(w["breakdown"][key], int), f"breakdown[{key}] is not int"
        if w["war_exhaustion"] is not None:
            assert isinstance(w["war_exhaustion"], int)


# ======================================================
# Test 5: Breakdown contains all 4 components
# ======================================================

class TestBreakdown:
    def test_breakdown_contains_four_components(self):
        """§N4j-5: breakdown contains all 4 components that sum to war_score."""
        world = make_world()
        set_war(world, "Prussia")

        result = build_active_wars(world)
        w = [w for w in result["wars"] if w["opponent"] == "Prussia"][0]
        bd = w["breakdown"]
        assert "territory" in bd
        assert "battles" in bd
        assert "decisive" in bd
        assert "capital" in bd


# ======================================================
# Test 6: Trend detection
# ======================================================

class TestTrend:
    def test_trend_rising_when_score_increased(self):
        """§N4j-6: trend is 'rising' when live score > previous + 2."""
        world = make_world()
        set_war(world, "Prussia")
        diplo_key = world._make_diplo_key("France", "Prussia")
        # Add battle records so live score is positive (~6)
        world.battle_records[diplo_key] = [
            {"turn": 1, "winner": "France", "location": "Saxony"},
            {"turn": 2, "winner": "France", "location": "Saxony"},
        ]
        # Previous score was 0 → current 6 > 0 + 2 → rising
        world.previous_war_scores[diplo_key] = 0

        result = build_active_wars(world)
        w = [w for w in result["wars"] if w["opponent"] == "Prussia"][0]
        assert w["trend"] == "rising"

    def test_trend_falling_when_score_decreased(self):
        """§N4j-6: trend is 'falling' when live score < previous - 2."""
        world = make_world()
        set_war(world, "Prussia")
        diplo_key = world._make_diplo_key("France", "Prussia")
        # No battle records → live score ~0. Previous was 20 → falling
        world.previous_war_scores[diplo_key] = 20

        result = build_active_wars(world)
        w = [w for w in result["wars"] if w["opponent"] == "Prussia"][0]
        assert w["trend"] == "falling"

    def test_trend_stable_when_score_unchanged(self):
        """§N4j-6: trend is 'stable' when score change <=2."""
        world = make_world()
        set_war(world, "Prussia")
        diplo_key = world._make_diplo_key("France", "Prussia")
        # No battle records → live score ~0. Previous was 0 → stable
        world.previous_war_scores[diplo_key] = 0

        result = build_active_wars(world)
        w = [w for w in result["wars"] if w["opponent"] == "Prussia"][0]
        assert w["trend"] == "stable"


# ======================================================
# Test 7: battles_fought count
# ======================================================

class TestBattlesFought:
    def test_battles_fought_matches_records(self):
        """§N4j-7: battles_fought matches count of battle_records for that diplo_key."""
        world = make_world()
        set_war(world, "Prussia")
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.battle_records[diplo_key] = [
            {"turn": 1, "winner": "France", "location": "Saxony"},
            {"turn": 2, "winner": "Prussia", "location": "Prussia"},
            {"turn": 3, "winner": "France", "location": "Bavaria"},
        ]

        result = build_active_wars(world)
        w = [w for w in result["wars"] if w["opponent"] == "Prussia"][0]
        assert w["battles_fought"] == 3


# ======================================================
# Test 8: decisive_won counts only France's decisive victories
# ======================================================

class TestDecisiveWon:
    def test_decisive_won_counts_only_france_victories(self):
        """§N4j-8: decisive_won counts only France's decisive victories."""
        world = make_world()
        set_war(world, "Prussia")
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.decisive_battles[diplo_key] = [
            {"turn": 1, "winner": "France", "location": "Saxony"},
            {"turn": 2, "winner": "Prussia", "location": "Prussia"},
            {"turn": 3, "winner": "France", "location": "Bavaria"},
        ]

        result = build_active_wars(world)
        w = [w for w in result["wars"] if w["opponent"] == "Prussia"][0]
        assert w["decisive_won"] == 2  # Only France's victories


# ======================================================
# Test 9: recent_battles format (last 5, newest first)
# ======================================================

class TestRecentBattles:
    def test_recent_battles_last_5_newest_first(self):
        """§N4j-9: recent_battles returns last 5, newest first, correct fields."""
        world = make_world()
        set_war(world, "Prussia")
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.battle_records[diplo_key] = [
            {"turn": 1, "winner": "France", "location": "Saxony"},
            {"turn": 2, "winner": "Prussia", "location": "Prussia"},
            {"turn": 3, "winner": "France", "location": "Bavaria"},
            {"turn": 4, "winner": "France", "location": "Rhineland"},
            {"turn": 5, "winner": "Prussia", "location": "Netherlands"},
            {"turn": 6, "winner": "France", "location": "Belgium"},
        ]
        world.decisive_battles[diplo_key] = [
            {"turn": 3, "winner": "France", "location": "Bavaria"},
        ]

        result = build_active_wars(world)
        w = [w for w in result["wars"] if w["opponent"] == "Prussia"][0]
        rb = w["recent_battles"]
        assert len(rb) == 5  # Last 5 only
        assert rb[0]["turn"] == 6  # Newest first
        assert rb[4]["turn"] == 2
        # Check fields
        for b in rb:
            assert "turn" in b
            assert "location" in b
            assert "won" in b
            assert "decisive" in b
            assert isinstance(b["turn"], int)
            assert isinstance(b["won"], bool)
            assert isinstance(b["decisive"], bool)

        # Check decisive flag
        decisive_battle = [b for b in rb if b["turn"] == 3][0]
        assert decisive_battle["decisive"] is True
        assert decisive_battle["won"] is True

        non_decisive = [b for b in rb if b["turn"] == 6][0]
        assert non_decisive["decisive"] is False


# ======================================================
# Test 10: war_exhaustion is None when fog-filtered
# ======================================================

class TestWarExhaustionFog:
    def test_war_exhaustion_none_below_partial(self):
        """§N4j-10: war_exhaustion is None when opponent visibility < PARTIAL."""
        world = make_world()
        set_war(world, "Prussia")
        world.war_exhaustion["Prussia"] = 42
        clear_visibility(world, "Prussia")

        result = build_active_wars(world)
        w = [w for w in result["wars"] if w["opponent"] == "Prussia"][0]
        assert w["war_exhaustion"] is None


# ======================================================
# Test 11: war_exhaustion correct when visible
# ======================================================

class TestWarExhaustionVisible:
    def test_war_exhaustion_correct_when_partial_plus(self):
        """§N4j-11: war_exhaustion is correct int when visibility >= PARTIAL."""
        world = make_world()
        set_war(world, "Prussia")
        world.war_exhaustion["Prussia"] = 42
        give_visibility(world, "Prussia", PARTIAL)

        result = build_active_wars(world)
        w = [w for w in result["wars"] if w["opponent"] == "Prussia"][0]
        assert w["war_exhaustion"] == 42
        assert isinstance(w["war_exhaustion"], int)


# ======================================================
# Test 12: army_strength fog-filtered
# ======================================================

class TestArmyStrengthFog:
    def test_army_strength_unknown_when_no_visibility(self):
        """§N4j-12: army_strength is fog-filtered string."""
        world = make_world()
        set_war(world, "Prussia")
        clear_visibility(world, "Prussia")

        result = build_active_wars(world)
        w = [w for w in result["wars"] if w["opponent"] == "Prussia"][0]
        assert w["army_strength"] == "Unknown"

    def test_army_strength_approximate_when_partial(self):
        """§N4j-12: army_strength approximate at PARTIAL visibility."""
        world = make_world()
        set_war(world, "Prussia")
        give_visibility(world, "Prussia", PARTIAL)

        result = build_active_wars(world)
        w = [w for w in result["wars"] if w["opponent"] == "Prussia"][0]
        assert "~" in w["army_strength"]

    def test_army_strength_exact_when_full(self):
        """§N4j-12: army_strength exact at FULL visibility."""
        world = make_world()
        set_war(world, "Prussia")
        give_visibility(world, "Prussia", FULL)

        result = build_active_wars(world)
        w = [w for w in result["wars"] if w["opponent"] == "Prussia"][0]
        assert "men" in w["army_strength"]
        assert "~" not in w["army_strength"]


# ======================================================
# Test 13: in_coalition tagging
# ======================================================

class TestCoalitionTagging:
    def test_in_coalition_true_for_coalition_members(self):
        """§N4j-13: in_coalition is True for coalition members."""
        world = make_world()
        set_war(world, "Britain")
        set_war(world, "Prussia")
        world.active_coalition = {
            "name": "British Coalition",
            "leader": "Britain",
            "members": ["Britain", "Prussia"],
            "strategic_posture": "aggressive",
        }

        result = build_active_wars(world)
        war_opponents = {w["opponent"] for w in result["wars"]}
        assert "Britain" in war_opponents
        assert "Prussia" in war_opponents
        for w in result["wars"]:
            if w["opponent"] in ("Britain", "Prussia"):
                assert w["in_coalition"] is True

    def test_in_coalition_false_for_non_members(self):
        """§N4j-13: in_coalition is False for non-coalition wars."""
        world = make_world()
        set_war(world, "Britain")
        set_war(world, "Saxony")
        world.active_coalition = {
            "name": "British Coalition",
            "leader": "Britain",
            "members": ["Britain"],
            "strategic_posture": "defensive",
        }

        result = build_active_wars(world)
        saxony_war = [w for w in result["wars"] if w["opponent"] == "Saxony"][0]
        assert saxony_war["in_coalition"] is False


# ======================================================
# Test 14: is_coalition_leader
# ======================================================

class TestCoalitionLeader:
    def test_is_coalition_leader_only_for_leader(self):
        """§N4j-14: is_coalition_leader is True only for the coalition leader."""
        world = make_world()
        set_war(world, "Britain")
        set_war(world, "Prussia")
        world.active_coalition = {
            "name": "British Coalition",
            "leader": "Britain",
            "members": ["Britain", "Prussia"],
            "strategic_posture": "aggressive",
        }

        result = build_active_wars(world)
        britain_war = [w for w in result["wars"] if w["opponent"] == "Britain"][0]
        prussia_war = [w for w in result["wars"] if w["opponent"] == "Prussia"][0]
        assert britain_war["is_coalition_leader"] is True
        assert prussia_war["is_coalition_leader"] is False


# ======================================================
# Test 15: coalition.coordination friction quality
# ======================================================

class TestCoalitionCoordination:
    def test_coordination_quality_labels(self):
        """§N4j-15: coalition.coordination shows correct friction quality."""
        world = make_world()
        set_war(world, "Britain")
        set_war(world, "Prussia")
        world.active_coalition = {
            "name": "British Coalition",
            "leader": "Britain",
            "members": ["Britain", "Prussia"],
            "strategic_posture": "aggressive",
        }
        # Set relations between Britain and Prussia
        bp_key = world._make_diplo_key("Britain", "Prussia")
        world.nation_relations[bp_key] = 50  # High relation = Good coordination

        result = build_active_wars(world)
        coord = result["coalition"]["coordination"]
        assert len(coord) == 1  # One pair
        assert coord[0]["nation_a"] == "Britain"
        assert coord[0]["nation_b"] == "Prussia"
        assert coord[0]["quality"] in ("Good", "Strained", "Poor")


# ======================================================
# Test 16: coalition.weak_link
# ======================================================

class TestCoalitionWeakLink:
    def test_weak_link_highest_we(self):
        """§N4j-16: coalition.weak_link identifies member with highest known WE."""
        world = make_world()
        set_war(world, "Britain")
        set_war(world, "Prussia")
        world.active_coalition = {
            "name": "British Coalition",
            "leader": "Britain",
            "members": ["Britain", "Prussia"],
            "strategic_posture": "aggressive",
        }
        world.war_exhaustion["Britain"] = 10
        world.war_exhaustion["Prussia"] = 30
        give_visibility(world, "Britain", PARTIAL)
        give_visibility(world, "Prussia", PARTIAL)

        result = build_active_wars(world)
        assert result["coalition"]["weak_link"] == "Prussia"


# ======================================================
# Test 17: coalition is None when no coalition active
# ======================================================

class TestNoCoalition:
    def test_coalition_none_when_no_coalition(self):
        """§N4j-17: coalition is None when no coalition is active."""
        world = make_world()
        set_war(world, "Prussia")

        result = build_active_wars(world)
        assert result["coalition"] is None


# ======================================================
# Test 18: Armistice data
# ======================================================

class TestArmistice:
    def test_armistice_fields(self):
        """§N4j-18: Armistice: correct remaining, relation, descriptor, trend."""
        world = make_world()
        set_armistice(world, "Austria", elapsed=2)
        diplo_key = world._make_diplo_key("France", "Austria")
        world.nation_relations[diplo_key] = -15

        result = build_active_wars(world)
        wars = result["wars"]
        assert len(wars) == 1
        w = wars[0]
        assert w["status"] == "armistice"
        assert w["armistice_remaining"] == 3  # 5 - 2 elapsed
        assert w["relation"] == -15
        assert isinstance(w["relation"], int)
        assert w["relation_descriptor"] in ("Hostile", "Wary", "Neutral", "Friendly", "Loyal")
        assert w["relation_trend"] in ("rising", "falling", "stable")
        assert w["opponent"] == "Austria"


# ======================================================
# Test 19: Eliminated nations excluded
# ======================================================

class TestEliminatedNations:
    def test_eliminated_nations_excluded(self):
        """§N4j-19: Eliminated nations (0 regions + 0 living marshals) excluded."""
        world = make_world()
        set_war(world, "Saxony")
        # Remove all Saxony regions and kill all marshals
        for r in world.regions.values():
            if r.controller == "Saxony":
                r.controller = "France"
        for m in world.marshals.values():
            if m.nation == "Saxony":
                m.strength = 0

        result = build_active_wars(world)
        saxony_wars = [w for w in result["wars"] if w["opponent"] == "Saxony"]
        assert len(saxony_wars) == 0  # Eliminated, so excluded


# ======================================================
# Test 20: Sort order
# ======================================================

class TestSortOrder:
    def test_wars_sorted_correctly(self):
        """§N4j-20: Wars sorted: coalition leader, coalition members, bilateral, armistice."""
        world = make_world()
        set_war(world, "Britain")
        set_war(world, "Prussia")
        set_war(world, "Saxony")
        set_armistice(world, "Austria")
        world.active_coalition = {
            "name": "British Coalition",
            "leader": "Britain",
            "members": ["Britain", "Prussia"],
            "strategic_posture": "aggressive",
        }

        result = build_active_wars(world)
        wars = result["wars"]
        # Coalition leader first
        assert wars[0]["opponent"] == "Britain"
        assert wars[0]["is_coalition_leader"] is True
        # Then coalition member
        assert wars[1]["opponent"] == "Prussia"
        assert wars[1]["in_coalition"] is True
        # Then bilateral
        saxony_idx = next(i for i, w in enumerate(wars) if w["opponent"] == "Saxony")
        assert wars[saxony_idx]["in_coalition"] is False
        assert wars[saxony_idx]["status"] == "war"
        # Armistice last
        austria_idx = next(i for i, w in enumerate(wars) if w["opponent"] == "Austria")
        assert wars[austria_idx]["status"] == "armistice"
        assert austria_idx > saxony_idx


# ======================================================
# Test 21: Multiple simultaneous wars (0-4+)
# ======================================================

class TestMultipleWars:
    def test_zero_wars(self):
        """§N4j-21: Works with 0 wars."""
        world = make_world()
        result = build_active_wars(world)
        assert len(result["wars"]) == 0

    def test_one_war(self):
        """§N4j-21: Works with 1 war."""
        world = make_world()
        set_war(world, "Prussia")
        result = build_active_wars(world)
        assert len(result["wars"]) == 1

    def test_two_wars(self):
        """§N4j-21: Works with 2 wars."""
        world = make_world()
        set_war(world, "Prussia")
        set_war(world, "Britain")
        result = build_active_wars(world)
        assert len(result["wars"]) == 2

    def test_four_wars(self):
        """§N4j-21: Works with 4 simultaneous wars."""
        world = make_world()
        set_war(world, "Prussia")
        set_war(world, "Britain")
        set_war(world, "Austria")
        set_war(world, "Saxony")
        result = build_active_wars(world)
        assert len(result["wars"]) == 4


# ======================================================
# Test 22: Mixed state (coalition + bilateral + armistice)
# ======================================================

class TestMixedState:
    def test_mixed_coalition_bilateral_armistice(self):
        """§N4j-22: 2 coalition wars + 1 bilateral + 1 armistice."""
        world = make_world()
        set_war(world, "Britain")
        set_war(world, "Prussia")
        set_war(world, "Saxony")
        set_armistice(world, "Austria", elapsed=1)
        world.active_coalition = {
            "name": "British Coalition",
            "leader": "Britain",
            "members": ["Britain", "Prussia"],
            "strategic_posture": "defensive",
        }

        result = build_active_wars(world)
        wars = result["wars"]
        assert len(wars) == 4

        coalition_wars = [w for w in wars if w["in_coalition"]]
        bilateral_wars = [w for w in wars if not w["in_coalition"] and w["status"] == "war"]
        armistice_wars = [w for w in wars if w["status"] == "armistice"]

        assert len(coalition_wars) == 2
        assert len(bilateral_wars) == 1
        assert len(armistice_wars) == 1
        assert result["coalition"] is not None
        assert result["coalition"]["name"] == "British Coalition"


# ======================================================
# Test 23: War → Armistice transition
# ======================================================

class TestWarToArmistice:
    def test_war_disappears_armistice_appears(self):
        """§N4j-23: War entry disappears, armistice entry appears."""
        world = make_world()
        set_war(world, "Prussia")

        result1 = build_active_wars(world)
        prussia_wars = [w for w in result1["wars"] if w["opponent"] == "Prussia"]
        assert len(prussia_wars) == 1
        assert prussia_wars[0]["status"] == "war"

        # Transition to armistice
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "ARMISTICE"
        world.armistice_turns[diplo_key] = 0

        result2 = build_active_wars(world)
        prussia_wars2 = [w for w in result2["wars"] if w["opponent"] == "Prussia"]
        assert len(prussia_wars2) == 1
        assert prussia_wars2[0]["status"] == "armistice"


# ======================================================
# Test 24: All wars end → empty response
# ======================================================

class TestAllWarsEnd:
    def test_all_wars_end_empty_response(self):
        """§N4j-24: All wars end: returns {"wars": [], "coalition": null}."""
        world = make_world()
        set_war(world, "Prussia")
        set_war(world, "Britain")

        # End all wars
        for key in list(world.diplomatic_states.keys()):
            world.diplomatic_states[key] = "PEACE"

        result = build_active_wars(world)
        assert result["wars"] == []
        assert result["coalition"] is None


# ======================================================
# Test 25: record_battle stores location field
# ======================================================

class TestBattleRecordLocation:
    def test_record_battle_stores_location(self):
        """Bug fix: record_battle must store location in the battle record."""
        from backend.game_logic.diplomacy import record_battle
        world = make_world()
        set_war(world, "Prussia")
        record_battle(
            world,
            attacker_nation="France",
            defender_nation="Prussia",
            winner_nation="France",
            attacker_casualties=2000,
            defender_casualties=3000,
            location="Saxony",
        )
        diplo_key = world._make_diplo_key("France", "Prussia")
        records = world.battle_records[diplo_key]
        assert len(records) == 1
        assert records[0]["location"] == "Saxony"

    def test_record_battle_location_default_empty(self):
        """Bug fix: location defaults to empty string when not provided."""
        from backend.game_logic.diplomacy import record_battle
        world = make_world()
        set_war(world, "Prussia")
        record_battle(
            world,
            attacker_nation="France",
            defender_nation="Prussia",
            winner_nation="France",
            attacker_casualties=2000,
            defender_casualties=3000,
        )
        diplo_key = world._make_diplo_key("France", "Prussia")
        records = world.battle_records[diplo_key]
        assert len(records) == 1
        assert records[0]["location"] == ""

    def test_location_appears_in_active_wars_recent_battles(self):
        """Bug fix: location flows through to build_active_wars recent_battles."""
        from backend.game_logic.diplomacy import record_battle
        world = make_world()
        set_war(world, "Prussia")
        record_battle(
            world,
            attacker_nation="France",
            defender_nation="Prussia",
            winner_nation="France",
            attacker_casualties=2000,
            defender_casualties=3000,
            location="Bavaria",
        )
        result = build_active_wars(world)
        w = [w for w in result["wars"] if w["opponent"] == "Prussia"][0]
        assert len(w["recent_battles"]) == 1
        assert w["recent_battles"][0]["location"] == "Bavaria"

    def test_location_not_unknown_when_provided(self):
        """Bug fix: location must not be 'unknown' when location is provided."""
        from backend.game_logic.diplomacy import record_battle
        world = make_world()
        set_war(world, "Prussia")
        record_battle(
            world,
            attacker_nation="France",
            defender_nation="Prussia",
            winner_nation="France",
            attacker_casualties=5000,
            defender_casualties=6000,
            location="Rhineland",
        )
        result = build_active_wars(world)
        w = [w for w in result["wars"] if w["opponent"] == "Prussia"][0]
        assert w["recent_battles"][0]["location"] != "unknown"
        assert w["recent_battles"][0]["location"] == "Rhineland"
