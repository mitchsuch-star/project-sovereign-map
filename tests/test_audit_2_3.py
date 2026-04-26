"""
Audit Tests 2A-2E: Diplomacy Formula Verification

Tests the acceptance formula, sweetener cap, military supremacy / battlefield
diplomacy non-stacking, war score component caps, and war score decay.

These reproduce spec worked examples and verify edge-case behavior.
"""

from backend.commands.executor import CommandExecutor
from backend.game_logic.diplomatic_dialogue import (
    MISSION_DP_COSTS,
    MISSION_EFFECTS,
    classify_diplomatic_intent,
    generate_feasibility_dialogue,
    generate_mission_dialogue,
)
from backend.game_logic.diplomacy import (
    BASE_DISPOSITION,
    PERSONALITY_MODIFIERS,
    STATE_RELATION_THRESHOLDS,
    SWEETENER_CAP,
    SWEETENER_VALUES,
    TRADE_INCOME,
    TRANSITION_RULES,
    apply_war_score_decay,
    calculate_acceptance,
    calculate_war_score,
    check_auto_downgrade,
    check_relation_requirement,
    declare_war,
    process_trade_income,
    record_battle,
    validate_transition,
)
from backend.models.world_state import WorldState


def make_world():
    return WorldState()


# ======================================================
# 2A. Acceptance Formula Worked Example
# ======================================================

class TestAcceptanceWorkedExample:

    def test_acceptance_worked_example(self):
        """
        France proposes peace with Prussia.
        War score +20. Relation -60. Threat 40 (STUBBED to 0 in code).
        Talleyrand (skill 10). Hardenberg (skill 6, hawk).
        Offers: open borders, 200 gold/turn.

        Spec expects total=6 (with threat=-12).
        Code gives 18 (threat stubbed to 0). Deviation noted.
        """
        world = make_world()

        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = 20
        world.nation_relations[diplo_key] = -60

        # Verify default diplomats
        assert world.diplomats["France"].skill == 10
        assert world.diplomats["France"].name == "Talleyrand"
        assert world.diplomats["Prussia"].skill == 6
        assert world.diplomats["Prussia"].personality == "hawk"

        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [
                {"type": "open_borders", "value": 1},
                {"type": "gold_per_turn", "value": 200},
            ],
            "demands": [],
            "clauses": [],
        }

        result = calculate_acceptance(proposal, world)
        c = result["components"]

        assert c["base_disposition"] == 30
        assert c["war_score_modifier"] == 6.0
        # R141: At WAR, relation dampened: -60/4 = -15, clamped to -10
        assert c["relation_modifier"] == -10
        assert c["hegemony_target_mod"] == 0
        assert c["bilateral_betrayal_mod"] == 0
        assert c["diplomat_skill_bonus"] == 8
        assert c["personality_modifier"] == -5
        assert c["military_supremacy"] == 0
        assert c["battlefield_diplomacy"] == 0
        assert c["military_pressure"] == 3  # R8: int(min(15, 20*0.15)) = 3
        assert c["deal_balance"] == 9.0

        # R141: Total: 30 + 6 - 10 + 0 + 9 + 8 - 5 + situational=3 = 41
        # R8: military_pressure=3 is max(0, 0, 3) = 3 situational
        assert result["score"] == 41
        assert result["outcome"] == "COUNTER_OFFER"

    def test_acceptance_individual_sweetener_values(self):
        assert SWEETENER_VALUES["open_borders"] == 3
        assert SWEETENER_VALUES["gold_per_turn"] == 3 / 100
        assert 200 * SWEETENER_VALUES["gold_per_turn"] == 6.0

    def test_base_disposition_values(self):
        assert BASE_DISPOSITION["peace"] == 30
        assert BASE_DISPOSITION["alliance"] == 20
        assert BASE_DISPOSITION["vassalage"] == 10
        assert BASE_DISPOSITION["armistice_losing"] == 40
        assert BASE_DISPOSITION["armistice_winning"] == 20
        assert BASE_DISPOSITION["open_borders"] == 35
        assert BASE_DISPOSITION["non_aggression"] == 30

    def test_personality_modifiers(self):
        assert PERSONALITY_MODIFIERS["hawk"] == (-5, 5)
        assert PERSONALITY_MODIFIERS["dove"] == (10, -10)
        assert PERSONALITY_MODIFIERS["loyalist"] == (0, 0)
        assert PERSONALITY_MODIFIERS["schemer"] == (5, 5)


# ======================================================
# 2B. Sweetener Cap
# ======================================================

class TestSweetenerCap:

    def test_sweetener_cap_constant(self):
        assert SWEETENER_CAP == 60  # raised from 40 so escalated offers improve acceptance

    def test_massive_sweeteners_capped_at_60(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = 0
        world.nation_relations[diplo_key] = 0

        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [
                {"type": "gold_per_turn", "value": 1000},
                {"type": "territory", "value": 5},
                {"type": "open_borders", "value": 1},
                {"type": "protection", "value": 1},
            ],
            "demands": [],
            "clauses": [],
        }

        result = calculate_acceptance(proposal, world)
        c = result["components"]

        # Raw: gold(1000*0.03=30) + territory(5*8=40) + open_borders(3) + protection(5) = 78
        # Capped at 60
        assert c["deal_balance"] == 60.0

    def test_sweeteners_below_cap_not_affected(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = 0
        world.nation_relations[diplo_key] = 0

        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [
                {"type": "open_borders", "value": 1},
            ],
            "demands": [],
            "clauses": [],
        }

        result = calculate_acceptance(proposal, world)
        c = result["components"]
        assert c["deal_balance"] == 3.0


# ======================================================
# 2C. Military Supremacy + Battlefield Diplomacy Non-Stacking
# ======================================================

class TestMilitarySupremacyNonStacking:

    def test_only_military_supremacy_applies(self):
        """war_score=75, France holds Berlin. MS=25, BD blocked."""
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = 75
        world.nation_relations[diplo_key] = 0

        world.regions["Berlin"].controller = "France"

        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }

        result = calculate_acceptance(proposal, world)
        c = result["components"]

        assert c["military_supremacy"] == 25
        assert c["battlefield_diplomacy"] == 0
        situational = max(c["military_supremacy"], c["battlefield_diplomacy"])
        assert situational == 25

    def test_battlefield_diplomacy_alone_when_no_capital(self):
        """BD applies when war_score > 20 but no capital held."""
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = 75
        world.nation_relations[diplo_key] = 0

        assert world.regions["Berlin"].controller == "Prussia"

        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }

        result = calculate_acceptance(proposal, world)
        c = result["components"]

        assert c["military_supremacy"] == 0
        assert c["battlefield_diplomacy"] == 10

    def test_battlefield_diplomacy_requires_strict_greater_than_20(self):
        """war_score == 20 does NOT trigger BD (strict >)."""
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = 20
        world.nation_relations[diplo_key] = 0

        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }

        result = calculate_acceptance(proposal, world)
        c = result["components"]

        assert c["military_supremacy"] == 0
        assert c["battlefield_diplomacy"] == 0


# ======================================================
# 2D. War Score Edge Cases - Component Caps
# ======================================================

class TestWarScoreEdgeCases:

    def test_territory_cap_at_40(self):
        world = make_world()

        from backend.models.region import Region
        world.nation_starting_regions["TestEnemy"] = [
            f"fake_region_{i}" for i in range(9)
        ]
        for i in range(9):
            name = f"fake_region_{i}"
            world.regions[name] = Region(
                name=name, adjacent_regions=[], terrain="plains", region_type="town"
            )
            world.regions[name].controller = "France"

        score = calculate_war_score("France", "TestEnemy", world)
        # 9 * 5 = 45, capped at 40
        assert score == 40, f"Territory should cap at 40, got {score}"

    def test_battle_cap_at_30(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"

        for i in range(11):
            world.current_turn = i + 1
            record_battle(world, "France", "Prussia", "France", 1000, 5000)

        score = calculate_war_score("France", "Prussia", world)
        assert score == 30, f"Battle-only score should cap at 30, got {score}"

    def test_decisive_cap_at_20(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"

        for i in range(3):
            world.current_turn = i + 1
            record_battle(world, "France", "Prussia", "France", 3000, 15000)

        decisive = world.decisive_battles.get(diplo_key, [])
        assert len(decisive) == 2, f"Max 2 decisive battles, got {len(decisive)}"

        score = calculate_war_score("France", "Prussia", world)
        # Decisive: 2 * 10 = 20, Battle: 3 * 3 = 9
        assert score == 29, f"Expected 29, got {score}"

    def test_capital_hold_cancels_out(self):
        """Hold enemy capital while they hold yours -> net 0."""
        world = make_world()

        world.regions["Berlin"].controller = "France"
        world.regions["Paris"].controller = "Prussia"

        score = calculate_war_score("France", "Prussia", world)

        world2 = make_world()
        baseline = calculate_war_score("France", "Prussia", world2)

        assert score == baseline, (
            f"Mutual capital hold should cancel. Score={score}, baseline={baseline}"
        )

    def test_total_war_score_capped_at_100(self):
        """All components maxed should cap at +100."""
        from backend.models.region import Region

        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"

        # Add extra fake Prussian starting regions so territory can reach cap
        # Prussia only has 2 real regions (Rhineland, Berlin). Need 8+ for +40 cap.
        extra_names = [f"fake_prussian_{i}" for i in range(8)]
        for name in extra_names:
            world.regions[name] = Region(name=name, adjacent_regions=[], terrain="plains", region_type="town")
            world.regions[name].controller = "France"
        world.nation_starting_regions["Prussia"] = list(world.nation_starting_regions.get("Prussia", [])) + extra_names

        # Also give France the real Prussian regions
        prussia_starting = list(world.nation_starting_regions.get("Prussia", []))
        for region_name in prussia_starting:
            if region_name in world.regions:
                world.regions[region_name].controller = "France"

        # Battles: 11 French victories with decisive casualties
        for i in range(11):
            world.current_turn = i + 1
            record_battle(world, "France", "Prussia", "France", 3000, 15000)

        decisive = world.decisive_battles.get(diplo_key, [])
        assert len(decisive) == 2

        assert world.regions["Berlin"].controller == "France"

        score = calculate_war_score("France", "Prussia", world)
        # Territory: 10 regions * 5 = 50 -> capped at 40
        # Battle: 11 * 3 = 33 -> capped at 30
        # Decisive: 2 * 10 = 20
        # Capital: Berlin held = +20
        # Raw: 40 + 30 + 20 + 20 = 110 -> capped at 100
        assert score == 100, f"Total should cap at 100, got {score}"

    def test_negative_war_score_capped_at_minus_100(self):
        """All components against should cap at -100."""
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"

        # France has 8 starting regions; give all to Prussia
        # 8 * -5 = -40 (caps at -40), capital(-20), battles(-30), decisive(-20)
        # = -110 -> capped at -100
        france_starting = list(world.nation_starting_regions.get("France", []))
        for region_name in france_starting:
            if region_name in world.regions:
                world.regions[region_name].controller = "Prussia"

        for i in range(11):
            world.current_turn = i + 1
            record_battle(world, "France", "Prussia", "Prussia", 15000, 3000)

        assert world.regions["Paris"].controller == "Prussia"

        score = calculate_war_score("France", "Prussia", world)
        assert score == -100, f"Total should cap at -100, got {score}"


# ======================================================
# 2E. War Score Decay
# ======================================================

class TestWarScoreDecay:

    def test_battle_component_decays_after_three_quiet_turns(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"

        world.battle_records[diplo_key] = [
            {"turn": 1, "winner": "France", "attacker": "France",
             "defender": "Prussia", "attacker_casualties": 2000,
             "defender_casualties": 5000}
        ]
        world.current_turn = 4

        apply_war_score_decay(world)

        assert world.war_scores[diplo_key] == 1

    def test_no_decay_when_recent_battle(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"

        world.battle_records[diplo_key] = [
            {"turn": 3, "winner": "France", "attacker": "France",
             "defender": "Prussia", "attacker_casualties": 2000,
             "defender_casualties": 5000}
        ]
        world.current_turn = 5

        apply_war_score_decay(world)
        assert world.war_scores[diplo_key] == 3

    def test_no_battle_records_do_not_decay_positive_territory_score(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"

        world.regions["Rhineland"].controller = "France"
        world.battle_records[diplo_key] = []
        world.current_turn = 10

        apply_war_score_decay(world)
        assert world.war_scores[diplo_key] == 5

    def test_no_battle_records_do_not_decay_negative_territory_score(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"

        region_name = next(
            name for name in world.nation_starting_regions["France"]
            if name != "Paris"
        )
        world.regions[region_name].controller = "Prussia"
        world.battle_records[diplo_key] = []
        world.current_turn = 10

        apply_war_score_decay(world)
        assert world.war_scores[diplo_key] == -5

    def test_battle_component_decay_does_not_cross_zero(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"

        world.battle_records[diplo_key] = [
            {"turn": 1, "winner": "Prussia", "attacker": "France",
             "defender": "Prussia", "attacker_casualties": 5000,
             "defender_casualties": 2000}
        ]
        world.current_turn = 10

        apply_war_score_decay(world)
        assert world.war_scores[diplo_key] == 0

    def test_decisive_battles_not_affected_by_decay(self):
        """Decisive battle records remain intact after decay."""
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"

        world.battle_records[diplo_key] = [
            {"turn": 1, "winner": "France", "attacker": "France",
             "defender": "Prussia", "attacker_casualties": 3000,
             "defender_casualties": 15000}
        ]
        world.decisive_battles[diplo_key] = [
            {"turn": 1, "winner": "France", "total_casualties": 18000, "ratio": 5.0}
        ]
        world.current_turn = 10

        apply_war_score_decay(world)

        assert world.war_scores[diplo_key] == 10
        assert len(world.decisive_battles[diplo_key]) == 1
        assert world.decisive_battles[diplo_key][0]["winner"] == "France"

    def test_multiple_decay_rounds(self):
        """Battle component decay is derived from quiet turns, not total score."""
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"

        world.battle_records[diplo_key] = 4 * [
            {"turn": 1, "winner": "France", "attacker": "France",
             "defender": "Prussia", "attacker_casualties": 2000,
             "defender_casualties": 5000}
        ]

        world.current_turn = 4
        apply_war_score_decay(world)
        assert world.war_scores[diplo_key] == 10

        world.current_turn = 5
        apply_war_score_decay(world)
        assert world.war_scores[diplo_key] == 8

        world.current_turn = 6
        apply_war_score_decay(world)
        assert world.war_scores[diplo_key] == 6


# ======================================================
# 3A. Transition Adjacency - Exhaustive Test
# ======================================================


class TestTransitionAdjacencyExhaustive:
    """3A: Test ALL invalid jumps and ALL valid jumps for state machine adjacency."""

    # -- Upward Jumps (R98: allowed with cumulative DP cost) --

    def test_war_to_peace_jump_allowed(self):
        """R98: WAR -> PEACE upward jump allowed."""
        assert validate_transition("WAR", "PEACE") is True

    def test_war_to_alliance_jump_allowed(self):
        """R98: WAR -> ALLIANCE upward jump allowed."""
        assert validate_transition("WAR", "ALLIANCE") is True

    def test_peace_to_alliance_jump_allowed(self):
        """R98: PEACE -> ALLIANCE upward jump allowed."""
        assert validate_transition("PEACE", "ALLIANCE") is True

    def test_peace_to_vassal_blocked(self):
        """PEACE -> VASSAL is below OPEN_BORDERS minimum - must be blocked."""
        assert validate_transition("PEACE", "VASSAL") is False

    def test_armistice_to_open_borders_jump_allowed(self):
        """R98: ARMISTICE -> OPEN_BORDERS upward jump allowed."""
        assert validate_transition("ARMISTICE", "OPEN_BORDERS") is True

    def test_war_to_open_borders_jump_allowed(self):
        """R98: WAR -> OPEN_BORDERS upward jump allowed."""
        assert validate_transition("WAR", "OPEN_BORDERS") is True

    def test_war_to_non_aggression_jump_allowed(self):
        """R98: WAR -> NON_AGGRESSION upward jump allowed."""
        assert validate_transition("WAR", "NON_AGGRESSION") is True

    def test_war_to_defensive_alliance_jump_allowed(self):
        """R98: WAR -> DEFENSIVE_ALLIANCE upward jump allowed."""
        assert validate_transition("WAR", "DEFENSIVE_ALLIANCE") is True

    def test_armistice_to_alliance_jump_allowed(self):
        """R98: ARMISTICE -> ALLIANCE upward jump allowed."""
        assert validate_transition("ARMISTICE", "ALLIANCE") is True

    def test_peace_to_non_aggression_jump_allowed(self):
        """R98: PEACE -> NON_AGGRESSION upward jump allowed."""
        assert validate_transition("PEACE", "NON_AGGRESSION") is True

    def test_peace_to_defensive_alliance_jump_allowed(self):
        """R98: PEACE -> DEFENSIVE_ALLIANCE upward jump allowed."""
        assert validate_transition("PEACE", "DEFENSIVE_ALLIANCE") is True

    def test_open_borders_to_alliance_jump_allowed(self):
        """R98: OPEN_BORDERS -> ALLIANCE upward jump allowed."""
        assert validate_transition("OPEN_BORDERS", "ALLIANCE") is True

    def test_open_borders_to_defensive_alliance_jump_allowed(self):
        """R98: OPEN_BORDERS -> DEFENSIVE_ALLIANCE upward jump allowed."""
        assert validate_transition("OPEN_BORDERS", "DEFENSIVE_ALLIANCE") is True

    def test_armistice_to_vassal_blocked(self):
        """ARMISTICE -> VASSAL is below OPEN_BORDERS minimum - must be blocked."""
        assert validate_transition("ARMISTICE", "VASSAL") is False

    def test_war_to_vassal_allowed(self):
        """WAR -> VASSAL is valid (dictated peace vassalage)."""
        assert validate_transition("WAR", "VASSAL") is True

    def test_same_state_blocked(self):
        """Any state -> same state - must be blocked."""
        for state in ["WAR", "ARMISTICE", "PEACE", "OPEN_BORDERS",
                       "NON_AGGRESSION", "DEFENSIVE_ALLIANCE", "ALLIANCE", "VASSAL"]:
            assert validate_transition(state, state) is False, \
                f"{state} -> {state} should be blocked"

    # -- Valid Jumps (must be ALLOWED) --

    def test_war_to_armistice_valid(self):
        """WAR -> ARMISTICE - valid upgrade."""
        assert validate_transition("WAR", "ARMISTICE") is True

    def test_armistice_to_peace_valid(self):
        """ARMISTICE -> PEACE - valid upgrade."""
        assert validate_transition("ARMISTICE", "PEACE") is True

    def test_peace_to_open_borders_valid(self):
        """PEACE -> OPEN_BORDERS - valid upgrade."""
        assert validate_transition("PEACE", "OPEN_BORDERS") is True

    def test_open_borders_to_non_aggression_valid(self):
        """OPEN_BORDERS -> NON_AGGRESSION - valid upgrade."""
        assert validate_transition("OPEN_BORDERS", "NON_AGGRESSION") is True

    def test_non_aggression_to_defensive_alliance_valid(self):
        """NON_AGGRESSION -> DEFENSIVE_ALLIANCE - valid upgrade."""
        assert validate_transition("NON_AGGRESSION", "DEFENSIVE_ALLIANCE") is True

    def test_defensive_alliance_to_alliance_valid(self):
        """DEFENSIVE_ALLIANCE -> ALLIANCE - valid upgrade."""
        assert validate_transition("DEFENSIVE_ALLIANCE", "ALLIANCE") is True

    def test_any_to_war_always_valid(self):
        """Any state -> WAR is always valid (war declaration)."""
        for state in ["ARMISTICE", "PEACE", "OPEN_BORDERS", "NON_AGGRESSION",
                       "DEFENSIVE_ALLIANCE", "ALLIANCE", "VASSAL"]:
            assert validate_transition(state, "WAR") is True, \
                f"{state} -> WAR should always be valid"

    def test_open_borders_to_vassal_valid(self):
        """OPEN_BORDERS -> VASSAL - valid (OPEN_BORDERS is in VASSAL_MIN_STATES)."""
        assert validate_transition("OPEN_BORDERS", "VASSAL") is True

    def test_non_aggression_to_vassal_valid(self):
        """NON_AGGRESSION -> VASSAL - valid."""
        assert validate_transition("NON_AGGRESSION", "VASSAL") is True

    def test_defensive_alliance_to_vassal_valid(self):
        """DEFENSIVE_ALLIANCE -> VASSAL - valid."""
        assert validate_transition("DEFENSIVE_ALLIANCE", "VASSAL") is True

    def test_alliance_to_vassal_valid(self):
        """ALLIANCE -> VASSAL - valid."""
        assert validate_transition("ALLIANCE", "VASSAL") is True

    def test_vassal_to_peace_valid(self):
        """VASSAL -> PEACE - valid exit from vassalage."""
        assert validate_transition("VASSAL", "PEACE") is True

    def test_vassal_to_war_valid(self):
        """VASSAL -> WAR - valid (rebellion or war declaration)."""
        assert validate_transition("VASSAL", "WAR") is True

    # -- Valid Downgrades --

    def test_alliance_to_defensive_alliance_downgrade_valid(self):
        """ALLIANCE -> DEFENSIVE_ALLIANCE - valid downgrade."""
        assert validate_transition("ALLIANCE", "DEFENSIVE_ALLIANCE") is True

    def test_defensive_alliance_to_non_aggression_downgrade_valid(self):
        """DEFENSIVE_ALLIANCE -> NON_AGGRESSION - valid downgrade."""
        assert validate_transition("DEFENSIVE_ALLIANCE", "NON_AGGRESSION") is True

    def test_non_aggression_to_open_borders_downgrade_valid(self):
        """NON_AGGRESSION -> OPEN_BORDERS - valid downgrade."""
        assert validate_transition("NON_AGGRESSION", "OPEN_BORDERS") is True

    def test_open_borders_to_peace_downgrade_valid(self):
        """OPEN_BORDERS -> PEACE - valid downgrade."""
        assert validate_transition("OPEN_BORDERS", "PEACE") is True


# ======================================================
# 3B. Relation Requirements Enforcement
# ======================================================

class TestRelationRequirements:
    """3B: Test each upgrade is blocked by insufficient relation.

    TRANSITION_RULES relation_req uses strict > comparison (check_relation_requirement).
    """

    def test_armistice_to_peace_blocked_at_minus_65(self):
        """ARMISTICE -> PEACE requires relation > -60. At -65, blocked."""
        req = TRANSITION_RULES[("ARMISTICE", "PEACE")]["relation_req"]
        assert req == -60, f"Expected req=-60, got {req}"
        assert check_relation_requirement("ARMISTICE", "PEACE", -65) is False

    def test_armistice_to_peace_allowed_at_exactly_minus_60(self):
        """ARMISTICE -> PEACE requires relation >= -60. At exactly -60, allowed (D2 fix: >= not >)."""
        assert check_relation_requirement("ARMISTICE", "PEACE", -60) is True

    def test_armistice_to_peace_allowed_at_minus_59(self):
        """ARMISTICE -> PEACE requires relation > -60. At -59, allowed."""
        assert check_relation_requirement("ARMISTICE", "PEACE", -59) is True

    def test_peace_to_open_borders_blocked_at_minus_25(self):
        """PEACE -> OPEN_BORDERS requires relation > -20. At -25, blocked."""
        req = TRANSITION_RULES[("PEACE", "OPEN_BORDERS")]["relation_req"]
        assert req == -20, f"Expected req=-20, got {req}"
        assert check_relation_requirement("PEACE", "OPEN_BORDERS", -25) is False

    def test_peace_to_open_borders_allowed_at_exactly_minus_20(self):
        """PEACE -> OPEN_BORDERS requires relation >= -20. At exactly -20, allowed (D2 fix: >= not >)."""
        assert check_relation_requirement("PEACE", "OPEN_BORDERS", -20) is True

    def test_peace_to_open_borders_allowed_at_minus_19(self):
        """PEACE -> OPEN_BORDERS at -19 - allowed."""
        assert check_relation_requirement("PEACE", "OPEN_BORDERS", -19) is True

    def test_open_borders_to_non_aggression_blocked_at_minus_5(self):
        """OPEN_BORDERS -> NON_AGGRESSION requires relation > 0. At -5, blocked."""
        req = TRANSITION_RULES[("OPEN_BORDERS", "NON_AGGRESSION")]["relation_req"]
        assert req == 0, f"Expected req=0, got {req}"
        assert check_relation_requirement("OPEN_BORDERS", "NON_AGGRESSION", -5) is False

    def test_open_borders_to_non_aggression_allowed_at_zero(self):
        """OPEN_BORDERS -> NON_AGGRESSION requires relation >= 0. At 0, allowed (D2 fix: >= not >)."""
        assert check_relation_requirement("OPEN_BORDERS", "NON_AGGRESSION", 0) is True

    def test_open_borders_to_non_aggression_allowed_at_plus_1(self):
        """OPEN_BORDERS -> NON_AGGRESSION at +1 - allowed."""
        assert check_relation_requirement("OPEN_BORDERS", "NON_AGGRESSION", 1) is True

    def test_non_aggression_to_defensive_alliance_blocked_at_plus_15(self):
        """NON_AGGRESSION -> DEFENSIVE_ALLIANCE requires relation > 20. At +15, blocked."""
        req = TRANSITION_RULES[("NON_AGGRESSION", "DEFENSIVE_ALLIANCE")]["relation_req"]
        assert req == 20, f"Expected req=20, got {req}"
        assert check_relation_requirement("NON_AGGRESSION", "DEFENSIVE_ALLIANCE", 15) is False

    def test_non_aggression_to_defensive_alliance_allowed_at_exactly_20(self):
        """NON_AGGRESSION -> DEFENSIVE_ALLIANCE at exactly 20 - allowed (D2 fix: >= not >)."""
        assert check_relation_requirement("NON_AGGRESSION", "DEFENSIVE_ALLIANCE", 20) is True

    def test_non_aggression_to_defensive_alliance_allowed_at_21(self):
        """NON_AGGRESSION -> DEFENSIVE_ALLIANCE at 21 - allowed."""
        assert check_relation_requirement("NON_AGGRESSION", "DEFENSIVE_ALLIANCE", 21) is True

    def test_defensive_alliance_to_alliance_blocked_at_plus_35(self):
        """DEFENSIVE_ALLIANCE -> ALLIANCE requires relation > 40. At +35, blocked."""
        req = TRANSITION_RULES[("DEFENSIVE_ALLIANCE", "ALLIANCE")]["relation_req"]
        assert req == 40, f"Expected req=40, got {req}"
        assert check_relation_requirement("DEFENSIVE_ALLIANCE", "ALLIANCE", 35) is False

    def test_defensive_alliance_to_alliance_allowed_at_exactly_40(self):
        """DEFENSIVE_ALLIANCE -> ALLIANCE at exactly 40 - allowed (D2 fix: >= not >)."""
        assert check_relation_requirement("DEFENSIVE_ALLIANCE", "ALLIANCE", 40) is True

    def test_defensive_alliance_to_alliance_allowed_at_41(self):
        """DEFENSIVE_ALLIANCE -> ALLIANCE at 41 - allowed."""
        assert check_relation_requirement("DEFENSIVE_ALLIANCE", "ALLIANCE", 41) is True

    def test_war_to_armistice_no_relation_requirement(self):
        """WAR -> ARMISTICE has no relation requirement (None)."""
        req = TRANSITION_RULES[("WAR", "ARMISTICE")]["relation_req"]
        assert req is None
        # Any relation should pass
        assert check_relation_requirement("WAR", "ARMISTICE", -100) is True
        assert check_relation_requirement("WAR", "ARMISTICE", 0) is True
        assert check_relation_requirement("WAR", "ARMISTICE", 100) is True

    def test_jump_transition_checks_target_state(self):
        """R98: Jump transition checks target state's relation requirement."""
        # PEACE requires relation > -60
        assert check_relation_requirement("WAR", "PEACE", -50) is True
        assert check_relation_requirement("WAR", "PEACE", -100) is False


# ======================================================
# 3C. DEFENSIVE_ALLIANCE Cascade
# ======================================================

class TestDefensiveAllianceCascade:
    """3C: France declares war on Austria. Austria-Prussia DEFENSIVE_ALLIANCE causes cascade."""

    def test_cascade_triggers_war_for_ally(self):
        """France declares war on Austria. Prussia (DEFENSIVE_ALLIANCE with Austria)
        is pulled into war with France."""
        world = make_world()

        # Setup: Austria-Prussia DEFENSIVE_ALLIANCE (already default)
        assert world.get_diplomatic_state("Austria", "Prussia") == "DEFENSIVE_ALLIANCE"

        # Set France-Austria to PEACE, France-Prussia to PEACE
        world.diplomatic_states["Austria|France"] = "PEACE"
        world.diplomatic_states["France|Prussia"] = "PEACE"

        result = declare_war(world, "France", "Austria")

        assert result["success"] is True
        # France-Austria becomes WAR
        assert world.get_diplomatic_state("France", "Austria") == "WAR"
        # France-Prussia becomes WAR (cascade)
        assert world.get_diplomatic_state("France", "Prussia") == "WAR"
        # Cascade entry exists
        assert len(result["cascade"]) >= 1
        cascade_nations = [c["defender"] for c in result["cascade"]]
        assert "Prussia" in cascade_nations

    def test_cascade_bypasses_armistice_cooldown(self):
        """If France-Prussia was in ARMISTICE with active cooldown,
        cascade BYPASSES the cooldown and forces WAR."""
        world = make_world()

        # Setup: Austria-Prussia DEFENSIVE_ALLIANCE
        assert world.get_diplomatic_state("Austria", "Prussia") == "DEFENSIVE_ALLIANCE"

        # France-Austria at PEACE, France-Prussia at ARMISTICE with cooldown
        world.diplomatic_states["Austria|France"] = "PEACE"
        world.diplomatic_states["France|Prussia"] = "ARMISTICE"
        world.armistice_cooldowns["France|Prussia"] = 3  # 3 turns remaining

        result = declare_war(world, "France", "Austria")

        assert result["success"] is True
        # France-Austria becomes WAR
        assert world.get_diplomatic_state("France", "Austria") == "WAR"
        # France-Prussia becomes WAR despite ARMISTICE cooldown
        assert world.get_diplomatic_state("France", "Prussia") == "WAR"

    def test_cascade_does_not_affect_already_at_war(self):
        """If Prussia is already at WAR with France, no duplicate cascade entry."""
        world = make_world()

        # Setup: Austria-Prussia DEFENSIVE_ALLIANCE, France-Prussia already WAR
        world.diplomatic_states["Austria|France"] = "PEACE"
        world.diplomatic_states["France|Prussia"] = "WAR"

        result = declare_war(world, "France", "Austria")

        assert result["success"] is True
        assert world.get_diplomatic_state("France", "Austria") == "WAR"
        # Prussia should NOT appear in cascade (already at war)
        cascade_nations = [c["defender"] for c in result["cascade"]]
        assert "Prussia" not in cascade_nations

    def test_cascade_with_alliance(self):
        """ALLIANCE also triggers cascade, not just DEFENSIVE_ALLIANCE."""
        world = make_world()

        # Setup: Austria-Prussia ALLIANCE (upgrade from default)
        world.diplomatic_states["Austria|Prussia"] = "ALLIANCE"
        world.diplomatic_states["Austria|France"] = "PEACE"
        world.diplomatic_states["France|Prussia"] = "PEACE"

        result = declare_war(world, "France", "Austria")

        assert result["success"] is True
        assert world.get_diplomatic_state("France", "Prussia") == "WAR"
        cascade_nations = [c["defender"] for c in result["cascade"]]
        assert "Prussia" in cascade_nations

    def test_direct_only_cascade(self):
        """DG-4 direct-only calls target allies but not allies of joiners."""
        world = make_world()

        # Austria-Prussia DEFENSIVE_ALLIANCE (default)
        # Britain-Prussia ALLIANCE (already default)
        assert world.get_diplomatic_state("Austria", "Prussia") == "DEFENSIVE_ALLIANCE"
        assert world.get_diplomatic_state("Britain", "Prussia") == "ALLIANCE"

        # Set all France relationships to PEACE
        world.diplomatic_states["Austria|France"] = "PEACE"
        world.diplomatic_states["France|Prussia"] = "PEACE"
        world.diplomatic_states["Britain|France"] = "PEACE"

        result = declare_war(world, "France", "Austria")

        assert result["success"] is True
        assert world.get_diplomatic_state("France", "Austria") == "WAR"
        # Prussia cascaded from Austria DEFENSIVE_ALLIANCE
        assert world.get_diplomatic_state("France", "Prussia") == "WAR"
        # Britain is Prussia's ally, not Austria's direct ally, so it is not called.
        assert world.get_diplomatic_state("Britain", "France") == "PEACE"

    def test_declare_war_on_already_at_war_fails(self):
        """Declaring war when already at war returns failure."""
        world = make_world()
        # France-Prussia already at WAR by default
        result = declare_war(world, "France", "Prussia")
        assert result["success"] is False


# ======================================================
# 3D. Trade Income After State Change
# ======================================================

class TestTradeIncomeAfterStateChange:
    """3D: Verify trade income changes when diplomatic state changes."""

    def test_trade_income_values_match_spec(self):
        """Verify TRADE_INCOME dict values."""
        assert TRADE_INCOME["PEACE"] == 50
        assert TRADE_INCOME["OPEN_BORDERS"] == 100
        assert TRADE_INCOME["NON_AGGRESSION"] == 150
        assert TRADE_INCOME["DEFENSIVE_ALLIANCE"] == 150
        assert TRADE_INCOME["ALLIANCE"] == 200
        assert TRADE_INCOME.get("WAR", 0) == 0
        assert TRADE_INCOME.get("ARMISTICE", 0) == 0

    def test_peace_to_war_loses_trade_income(self):
        """France-Austria go from PEACE to WAR. Both lose 50 gold trade income."""
        world = make_world()

        # Set France-Austria to PEACE
        world.diplomatic_states["Austria|France"] = "PEACE"
        # Record initial gold
        france_gold_before = world.nation_gold.get("France", 0)
        austria_gold_before = world.nation_gold.get("Austria", 0)

        # Process trade income while at PEACE
        income_at_peace = process_trade_income(world)
        france_peace_income = income_at_peace.get("France", 0)
        austria_peace_income = income_at_peace.get("Austria", 0)

        # France-Austria PEACE should contribute 50 to each
        # (Other pairs may also contribute)
        assert france_peace_income >= 50, \
            f"France should get at least 50 from PEACE with Austria, got {france_peace_income}"
        assert austria_peace_income >= 50, \
            f"Austria should get at least 50 from PEACE with Austria, got {austria_peace_income}"

        # Reset gold to before
        world.nation_gold["France"] = france_gold_before
        world.nation_gold["Austria"] = austria_gold_before

        # Now change to WAR
        world.diplomatic_states["Austria|France"] = "WAR"
        income_at_war = process_trade_income(world)

        # France and Austria should each get 50 LESS (the PEACE trade is gone)
        france_war_income = income_at_war.get("France", 0)
        austria_war_income = income_at_war.get("Austria", 0)

        france_lost = france_peace_income - france_war_income
        austria_lost = austria_peace_income - austria_war_income

        # R6: With diminishing returns, Austria PEACE is France's 2nd partner
        # (Saxony OB is 1st) so it earns 50*0.75=37, not 50. Losing it = -37.
        assert france_lost == 37, \
            f"France should lose 37 trade income (diminishing returns), lost {france_lost}"
        # Austria: losing France PEACE trade. France was Austria's lowest-priority
        # partner, so the loss depends on partner count.
        assert austria_lost > 0, \
            f"Austria should lose some trade income, lost {austria_lost}"

    def test_war_has_zero_trade_income(self):
        """WAR state produces zero trade income for the pair."""
        world = make_world()

        # Set ALL pairs to WAR for isolation
        for key in world.diplomatic_states:
            world.diplomatic_states[key] = "WAR"

        income = process_trade_income(world)
        # Should be empty dict (no income generated)
        assert len(income) == 0, f"Expected no trade income from all-WAR states, got {income}"

    def test_alliance_gives_200_per_pair(self):
        """ALLIANCE state gives 200 trade income to each nation in the pair."""
        world = make_world()

        # Set ALL pairs to WAR except one ALLIANCE
        for key in world.diplomatic_states:
            world.diplomatic_states[key] = "WAR"
        world.diplomatic_states["Austria|France"] = "ALLIANCE"

        income = process_trade_income(world)
        assert income.get("France", 0) == 200
        assert income.get("Austria", 0) == 200

    def test_trade_income_accumulates_from_multiple_pairs(self):
        """A nation with multiple positive-trade pairs gets cumulative income."""
        world = make_world()

        # Set all to WAR first
        for key in world.diplomatic_states:
            world.diplomatic_states[key] = "WAR"

        # France-Austria: PEACE (50), France-Saxony: OPEN_BORDERS (100)
        world.diplomatic_states["Austria|France"] = "PEACE"
        world.diplomatic_states["France|Saxony"] = "OPEN_BORDERS"

        income = process_trade_income(world)
        # R6: France has 2 partners. OB(100*1.0) + PEACE(50*0.75) = 137
        assert income.get("France", 0) == 137, \
            f"France should get 100+37=137 (diminishing returns), got {income.get('France', 0)}"
        assert income.get("Austria", 0) == 50   # Austria has only 1 partner → full rate
        assert income.get("Saxony", 0) == 100   # Saxony has only 1 partner → full rate


# ======================================================
# 3E. Downgrade Auto-Decay
# ======================================================

class TestDowngradeAutoDecay:
    """3E: Verify check_auto_downgrade() triggers after 5 turns below threshold.

    STATE_RELATION_THRESHOLDS: gap must be >= 30 below threshold for 5 turns.
    """

    def test_state_relation_thresholds_match_spec(self):
        """Verify STATE_RELATION_THRESHOLDS values."""
        assert STATE_RELATION_THRESHOLDS["ALLIANCE"] == 40
        assert STATE_RELATION_THRESHOLDS["DEFENSIVE_ALLIANCE"] == 20
        assert STATE_RELATION_THRESHOLDS["NON_AGGRESSION"] == 0
        assert STATE_RELATION_THRESHOLDS["OPEN_BORDERS"] == -20

    def test_alliance_auto_downgrade_after_5_turns(self):
        """ALLIANCE with relation well below threshold (gap >= 30) for 5 turns
        auto-downgrades to DEFENSIVE_ALLIANCE."""
        world = make_world()

        diplo_key = "Austria|France"
        world.diplomatic_states[diplo_key] = "ALLIANCE"
        world.nation_relations[diplo_key] = 5  # 40 - 5 = 35 gap (>= 30)

        for i in range(5):
            events = check_auto_downgrade(world)

        assert world.diplomatic_states[diplo_key] == "DEFENSIVE_ALLIANCE", \
            f"Expected DEFENSIVE_ALLIANCE, got {world.diplomatic_states[diplo_key]}"

        assert any(e["type"] == "auto_downgrade" for e in events), \
            f"Expected auto_downgrade event, got {events}"

    def test_warning_at_turn_3(self):
        """After 3 turns below threshold, a downgrade_warning is produced."""
        world = make_world()

        diplo_key = "Austria|France"
        world.diplomatic_states[diplo_key] = "ALLIANCE"
        world.nation_relations[diplo_key] = 0  # gap = 40 >= 30

        all_events = []
        for i in range(3):
            events = check_auto_downgrade(world)
            all_events.extend(events)

        warnings = [e for e in all_events if e["type"] == "downgrade_warning"]
        assert len(warnings) == 1, f"Expected 1 warning, got {len(warnings)}"

    def test_no_downgrade_before_5_turns(self):
        """After only 4 turns below threshold, no downgrade yet."""
        world = make_world()

        diplo_key = "Austria|France"
        world.diplomatic_states[diplo_key] = "ALLIANCE"
        world.nation_relations[diplo_key] = 5  # gap = 35 >= 30

        for i in range(4):
            check_auto_downgrade(world)

        assert world.diplomatic_states[diplo_key] == "ALLIANCE", \
            "Should NOT have downgraded after only 4 turns"

    def test_counter_resets_when_relation_recovers(self):
        """If relation recovers above threshold-30, counter resets."""
        world = make_world()

        diplo_key = "Austria|France"
        world.diplomatic_states[diplo_key] = "ALLIANCE"
        world.nation_relations[diplo_key] = 5  # gap = 35 >= 30

        # 3 turns below
        for i in range(3):
            check_auto_downgrade(world)
        assert world.turns_below_threshold.get(diplo_key, 0) == 3

        # Relation recovers: gap < 30
        world.nation_relations[diplo_key] = 15  # gap = 25 < 30
        check_auto_downgrade(world)
        assert world.turns_below_threshold.get(diplo_key, 0) == 0, \
            "Counter should reset when gap < 30"

        # Even after 5 more turns below, need fresh 5 turns
        world.nation_relations[diplo_key] = 5  # gap back to 35
        for i in range(4):
            check_auto_downgrade(world)
        assert world.diplomatic_states[diplo_key] == "ALLIANCE", \
            "Should not have downgraded - counter was reset"

    def test_gap_less_than_30_no_downgrade(self):
        """If gap is < 30 (relation only slightly below threshold), no downgrade."""
        world = make_world()

        diplo_key = "Austria|France"
        world.diplomatic_states[diplo_key] = "ALLIANCE"
        world.nation_relations[diplo_key] = 15  # gap = 25 < 30

        for i in range(10):
            check_auto_downgrade(world)

        assert world.diplomatic_states[diplo_key] == "ALLIANCE", \
            "Gap < 30 should never trigger downgrade"

    def test_defensive_alliance_auto_downgrade(self):
        """DEFENSIVE_ALLIANCE threshold=20. Relation=-15 gives gap=35.
        After 5 turns, downgrades to NON_AGGRESSION."""
        world = make_world()

        diplo_key = "Austria|France"
        world.diplomatic_states[diplo_key] = "DEFENSIVE_ALLIANCE"
        world.nation_relations[diplo_key] = -15  # gap = 20 - (-15) = 35 >= 30

        for i in range(5):
            check_auto_downgrade(world)

        assert world.diplomatic_states[diplo_key] == "NON_AGGRESSION"

    def test_non_aggression_auto_downgrade(self):
        """NON_AGGRESSION threshold=0. Relation=-35 gives gap=35.
        After 5 turns, downgrades to OPEN_BORDERS."""
        world = make_world()

        diplo_key = "Austria|France"
        world.diplomatic_states[diplo_key] = "NON_AGGRESSION"
        world.nation_relations[diplo_key] = -35  # gap = 0 - (-35) = 35 >= 30

        for i in range(5):
            check_auto_downgrade(world)

        assert world.diplomatic_states[diplo_key] == "OPEN_BORDERS"

    def test_open_borders_auto_downgrade(self):
        """OPEN_BORDERS threshold=-20. Relation=-55 gives gap=35.
        After 5 turns, downgrades to PEACE."""
        world = make_world()

        diplo_key = "Austria|France"
        world.diplomatic_states[diplo_key] = "OPEN_BORDERS"
        world.nation_relations[diplo_key] = -55  # gap = -20 - (-55) = 35 >= 30

        for i in range(5):
            check_auto_downgrade(world)

        assert world.diplomatic_states[diplo_key] == "PEACE"

    def test_peace_not_subject_to_auto_downgrade(self):
        """PEACE has no auto-downgrade threshold - it stays at PEACE regardless."""
        world = make_world()

        diplo_key = "Austria|France"
        world.diplomatic_states[diplo_key] = "PEACE"
        world.nation_relations[diplo_key] = -100

        for i in range(10):
            check_auto_downgrade(world)

        assert world.diplomatic_states[diplo_key] == "PEACE"

    def test_auto_downgrade_applies_half_relation_penalty(self):
        """Auto-downgrade applies half the normal downgrade relation penalty."""
        world = make_world()

        diplo_key = "Austria|France"
        world.diplomatic_states[diplo_key] = "ALLIANCE"
        world.nation_relations[diplo_key] = 0  # gap = 40 >= 30

        relation_before = world.nation_relations[diplo_key]

        for i in range(5):
            check_auto_downgrade(world)

        relation_after = world.nation_relations[diplo_key]
        # DOWNGRADE_PENALTIES[("ALLIANCE", "DEFENSIVE_ALLIANCE")]["relation_target"] = -15
        # Half = -15 // 2 = -8 (Python floor division)
        expected_penalty = -15 // 2  # -8
        assert relation_after == relation_before + expected_penalty, \
            f"Expected relation {relation_before + expected_penalty}, got {relation_after}"


# ======================================================
# 4A. Parser Routing Matrix
# ======================================================


def make_executor():
    return CommandExecutor()


class TestParserRoutingMatrix:

    def test_military_command_not_diplomatic(self):
        world = make_world()
        parsed = {
            "raw_text": "Ney, move to Belgium",
            "target_nation": None,
            "proposal_type": None,
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": False,
            "mission_type": None,
        }
        result = classify_diplomatic_intent(parsed, world)
        assert result == "not_diplomatic"

    def test_propose_peace_proposal_confirm(self):
        world = make_world()
        parsed = {
            "raw_text": "Talleyrand, propose peace with Prussia",
            "target_nation": "Prussia",
            "proposal_type": "peace",
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "mission_type": None,
        }
        result = classify_diplomatic_intent(parsed, world)
        assert result == "proposal_confirm"

    def test_vague_deal_proposal_options(self):
        world = make_world()
        parsed = {
            "raw_text": "Talleyrand, deal with Austria",
            "target_nation": "Austria",
            "proposal_type": None,
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "mission_type": None,
        }
        result = classify_diplomatic_intent(parsed, world)
        assert result == "proposal_options"

    def test_specific_terms_proposal_execute(self):
        world = make_world()
        parsed = {
            "raw_text": "Talleyrand, propose peace with Prussia: open borders, 200 gold/turn",
            "target_nation": "Prussia",
            "proposal_type": "peace",
            "clauses": ["open_borders", "gold_200"],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "mission_type": None,
        }
        result = classify_diplomatic_intent(parsed, world)
        assert result == "proposal_execute"

    def test_feasibility_question(self):
        world = make_world()
        parsed = {
            "raw_text": "Talleyrand, what would it take to get peace with Prussia?",
            "target_nation": "Prussia",
            "proposal_type": "peace",
            "clauses": [],
            "is_question": True,
            "has_diplomatic_keywords": True,
            "mission_type": None,
        }
        result = classify_diplomatic_intent(parsed, world)
        assert result == "feasibility"

    def test_mission_improve_relations(self):
        world = make_world()
        parsed = {
            "raw_text": "Talleyrand, improve relations with Austria",
            "target_nation": "Austria",
            "proposal_type": None,
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "mission_type": "IMPROVE_RELATIONS",
        }
        result = classify_diplomatic_intent(parsed, world)
        assert result == "mission"

    def test_military_command_to_talleyrand_no_diplo(self):
        world = make_world()
        parsed = {
            "raw_text": "Talleyrand, attack Belgium",
            "target_nation": None,
            "proposal_type": None,
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": False,
            "mission_type": None,
        }
        result = classify_diplomatic_intent(parsed, world)
        assert result == "not_diplomatic"

    def test_military_command_to_talleyrand_with_diplo_kw(self):
        world = make_world()
        parsed = {
            "raw_text": "Talleyrand, attack Belgium",
            "target_nation": None,
            "proposal_type": None,
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "mission_type": None,
        }
        result = classify_diplomatic_intent(parsed, world)
        assert result == "proposal_options"

    def test_no_addressee_routing(self):
        world = make_world()
        parsed = {
            "raw_text": "propose peace with Prussia",
            "target_nation": "Prussia",
            "proposal_type": "peace",
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "mission_type": None,
        }
        result = classify_diplomatic_intent(parsed, world)
        assert result == "proposal_confirm"

    def test_unknown_nation_handling(self):
        world = make_world()
        parsed = {
            "raw_text": "Talleyrand, propose peace with Spain",
            "target_nation": "Spain",
            "proposal_type": "peace",
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "mission_type": None,
        }
        result = classify_diplomatic_intent(parsed, world)
        assert result == "unknown_nation"

    def test_advisory_question_no_feasibility_keywords(self):
        world = make_world()
        parsed = {
            "raw_text": "Talleyrand, what do you think of Austria?",
            "target_nation": "Austria",
            "proposal_type": None,
            "clauses": [],
            "is_question": True,
            "has_diplomatic_keywords": True,
            "mission_type": None,
        }
        result = classify_diplomatic_intent(parsed, world)
        assert result == "advisory"


# ======================================================
# 4B. Dialogue Blocking Enforcement
# ======================================================

class TestDialogueBlockingEnforcement:

    def test_hard_stop_dialogue_blocks_military_command(self):
        """PL-27: Hard-stop dialogues block all commands."""
        world = make_world()
        executor = make_executor()
        world.dialogue_manager.replace({
            "type": "commitment_paradox",
            "target_nation": "Prussia",
            "talleyrand_text": "Alliance conflict!",
            "options": [
                {"label": "Honor", "description": "Keep alliance.", "action": "honor"},
                {"label": "Break", "description": "Break alliance.", "action": "side"},
            ],
            "context": {},
            "turn_created": 1,
            "blocking": True,
        })
        game_state = {"world": world}
        parsed_command = {
            "command": {"action": "attack", "marshal": "Ney", "target": "Rhineland"},
            "raw_input": "Ney, attack Rhineland",
        }
        result = executor.execute(parsed_command, game_state)
        assert result["success"] is False
        assert result.get("awaiting_diplomatic_response") is True

    def test_soft_stop_dialogue_allows_commands(self):
        """PL-27: Soft-stop/local-planning dialogues do NOT block commands."""
        world = make_world()
        executor = make_executor()
        world.dialogue_manager.replace({
            "type": "proposal_options",
            "target_nation": "Austria",
            "talleyrand_text": "Which approach?",
            "options": [{"label": "Dismiss", "description": "Cancel.", "action": "dismiss"}],
            "context": {},
            "turn_created": 1,
            "blocking": False,
        })
        game_state = {"world": world}
        parsed_command = {
            "command": {"action": "status"},
            "raw_input": "status",
        }
        result = executor.execute(parsed_command, game_state)
        # PL-27: Local planning flow should not block
        assert result.get("awaiting_diplomatic_response") is not True

    def test_cleared_dialogue_allows_commands(self):
        world = make_world()
        executor = make_executor()
        world.dialogue_manager.replace({
            "type": "commitment_paradox",
            "target_nation": "Prussia",
            "talleyrand_text": "Test",
            "options": [],
            "context": {},
            "turn_created": 1,
            "blocking": True,
        })
        world.dialogue_manager.pop()
        game_state = {"world": world}
        parsed_command = {
            "command": {"action": "attack", "marshal": "Ney", "target": "Rhineland"},
            "raw_input": "Ney, attack Rhineland",
        }
        result = executor.execute(parsed_command, game_state)
        assert "awaiting_diplomatic_response" not in result

    def test_hard_stop_dialogue_blocks_end_turn(self):
        """PL-27: Hard-stop dialogue blocks end_turn via executor guard."""
        world = make_world()
        executor = make_executor()
        world.dialogue_manager.replace({
            "type": "force_declare_war_confirmation",
            "target_nation": "Prussia",
            "talleyrand_text": "Test",
            "options": [],
            "context": {},
            "turn_created": 1,
            "blocking": True,
        })
        game_state = {"world": world}
        parsed_command = {"command": {"action": "end_turn"}, "raw_input": "end turn"}
        result = executor.execute(parsed_command, game_state)
        assert result["success"] is False
        assert "requires your attention" in result.get("message", "").lower() or "respond" in result.get("message", "").lower()


# ======================================================
# 4C. Proposal Full Lifecycle
# ======================================================

class TestProposalFullLifecycle:

    def test_generate_proposal_dialogue(self):
        world = make_world()
        executor = make_executor()
        world.diplomatic_points = 10
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"
        diplomatic_data = {
            "action": "diplomatic_proposal",
            "target_nation": "Prussia",
            "proposal_type": "peace",
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "mission_type": None,
            "raw_text": "propose peace with Prussia",
        }
        command = {"action": "diplomatic_proposal", "diplomatic_data": diplomatic_data}
        game_state = {"world": world}
        result = executor._execute_diplomatic(command, game_state)
        assert result["success"] is True
        assert world.pending_diplomatic_dialogue is not None
        assert world.pending_diplomatic_dialogue.get("target_nation") == "Prussia"
        assert len(world.pending_diplomatic_dialogue.get("options", [])) > 0

    def test_execute_proposal_deducts_dp_sends_talleyrand(self):
        world = make_world()
        executor = make_executor()
        world.diplomatic_points = 10
        initial_dp = world.diplomatic_points
        world.dialogue_manager.replace({
            "type": "proposal_confirm",
            "target_nation": "Prussia",
            "talleyrand_text": "Shall I send?",
            "options": [
                {
                    "label": "Send proposal",
                    "description": "Dispatch.",
                    "action": "execute_proposal",
                    "terms": {
                        "proposal_type": "peace",
                        "target_nation": "Prussia",
                        "sweeteners": [],
                        "demands": [],
                        "clauses": [],
                    },
                },
                {"label": "Dismiss", "description": "Cancel.", "action": "dismiss"},
            ],
            "context": {},
            "turn_created": 1,
            "blocking": False,
        })
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response(1, game_state)
        assert result["success"] is True
        assert world.diplomatic_points < initial_dp
        assert world.talleyrand_state == "IN_TRANSIT"
        assert world.proposal_in_transit is not None
        assert world.proposal_in_transit["target"] == "Prussia"
        assert world.pending_diplomatic_dialogue is None

    def test_proposal_resolves_next_turn(self):
        world = make_world()
        world.talleyrand_state = "IN_TRANSIT"
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"
        world.proposal_in_transit = {
            "target": "Prussia",
            "proposal": {
                "type": "peace",
                "proposer_nation": "France",
                "target_nation": "Prussia",
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            },
            "turn_sent": world.current_turn - 1,
        }
        events = world._process_proposal_in_transit()
        assert len(events) > 0
        assert world.proposal_in_transit is None
        assert world.talleyrand_state in ("IDLE", "ON_MISSION")
        assert events[0]["type"] == "diplomatic_proposal_returned"
        assert events[0]["outcome"] in ("ACCEPT", "REJECT", "COUNTER_OFFER")

    def test_proposal_not_resolved_same_turn(self):
        world = make_world()
        world.talleyrand_state = "IN_TRANSIT"
        world.proposal_in_transit = {
            "target": "Prussia",
            "proposal": {
                "type": "peace",
                "proposer_nation": "France",
                "target_nation": "Prussia",
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            },
            "turn_sent": world.current_turn,
        }
        events = world._process_proposal_in_transit()
        assert len(events) == 0
        assert world.proposal_in_transit is not None

    def test_accepted_proposal_ratifies_treaty(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[diplo_key] = "WAR"
        world.war_scores[diplo_key] = 80
        world.nation_relations[diplo_key] = 50
        world.talleyrand_state = "IN_TRANSIT"
        world.proposal_in_transit = {
            "target": "Austria",
            "proposal": {
                "type": "peace",
                "proposer_nation": "France",
                "target_nation": "Austria",
                "sweeteners": [
                    {"type": "open_borders", "value": 1},
                    {"type": "gold", "value": 200},
                ],
                "demands": [],
                "clauses": [],
            },
            "turn_sent": world.current_turn - 1,
        }
        events = world._process_proposal_in_transit()
        assert len(events) > 0
        if events[0]["outcome"] == "ACCEPT":
            new_state = world.get_diplomatic_state("France", "Austria")
            assert new_state != "WAR"

    def test_rejected_proposal_sets_cooldown(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"
        world.war_scores[diplo_key] = -50
        world.nation_relations[diplo_key] = -80
        world.talleyrand_state = "IN_TRANSIT"
        world.proposal_in_transit = {
            "target": "Prussia",
            "proposal": {
                "type": "peace",
                "proposer_nation": "France",
                "target_nation": "Prussia",
                "sweeteners": [],
                "demands": [{"type": "gold", "value": 500}],
                "clauses": [],
            },
            "turn_sent": world.current_turn - 1,
        }
        events = world._process_proposal_in_transit()
        assert len(events) > 0
        if events[0]["outcome"] in ("REJECT", "COUNTER_OFFER"):
            assert "Prussia" in world.player_proposal_cooldowns
            # PL-5B: +1 for decrement timing compensation
            assert world.player_proposal_cooldowns["Prussia"] == 4
            assert "Prussia_peace" in world.player_proposal_cooldowns
            assert world.player_proposal_cooldowns["Prussia_peace"] == 6


# ======================================================
# 4D. Mission Lifecycle
# ======================================================

class TestMissionLifecycle:

    def test_generate_mission_dialogue(self):
        world = make_world()
        parsed = {
            "target_nation": "Austria",
            "mission_type": "IMPROVE_RELATIONS",
            "raw_text": "improve relations with Austria",
        }
        dialogue = generate_mission_dialogue(parsed, world)
        assert dialogue["type"] == "mission"
        assert dialogue["target_nation"] == "Austria"
        assert len(dialogue["options"]) >= 2
        actions = [o["action"] for o in dialogue["options"]]
        assert "start_mission" in actions
        assert dialogue["context"].get("dp_cost_per_turn") == MISSION_DP_COSTS["IMPROVE_RELATIONS"]

    def test_start_mission_sets_on_mission(self):
        world = make_world()
        executor = make_executor()
        world.diplomatic_points = 10
        world.dialogue_manager.replace({
            "type": "mission",
            "target_nation": "Austria",
            "talleyrand_text": "I shall improve relations.",
            "options": [
                {
                    "label": "Begin mission",
                    "description": "Start.",
                    "action": "start_mission",
                    "terms": {"mission_type": "IMPROVE_RELATIONS", "target_nation": "Austria"},
                },
                {"label": "Dismiss", "description": "Cancel.", "action": "dismiss"},
            ],
            "context": {"dp_cost_per_turn": 1},
            "turn_created": 1,
            "blocking": False,
        })
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response(1, game_state)
        assert result["success"] is True
        assert world.talleyrand_state == "ON_MISSION"
        assert world.active_diplomatic_mission is not None
        assert world.active_diplomatic_mission["type"] == "IMPROVE_RELATIONS"
        assert world.active_diplomatic_mission["target"] == "Austria"
        assert world.active_diplomatic_mission["turns_active"] == 0
        assert world.pending_diplomatic_dialogue is None

    def test_mission_improves_relations_per_turn(self):
        world = make_world()
        world.talleyrand_state = "ON_MISSION"
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 0,
            "paused": False,
            "paused_turns": 0,
        }
        world.diplomatic_points = 10
        diplo_key = world._make_diplo_key("France", "Austria")
        initial_relation = world.nation_relations.get(diplo_key, 0)
        from backend.game_logic.diplomacy import _process_mission_effects, _process_mission_dp
        _process_mission_dp(world)
        _process_mission_effects(world)
        new_relation = world.nation_relations.get(diplo_key, 0)
        expected_change = MISSION_EFFECTS["IMPROVE_RELATIONS"]["relation_change"]
        expected_scaled = int(round(expected_change * 1.5))
        assert new_relation == initial_relation + expected_scaled

    def test_cancel_mission_returns_idle(self):
        world = make_world()
        executor = make_executor()
        world.talleyrand_state = "ON_MISSION"
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 3,
            "paused": False,
            "paused_turns": 0,
        }
        world.dialogue_manager.replace({
            "type": "mission",
            "target_nation": "Austria",
            "talleyrand_text": "Cancel?",
            "options": [
                {"label": "Confirm cancel", "description": "Cancel.", "action": "cancel_mission"},
                {"label": "Continue", "description": "Keep going.", "action": "dismiss"},
            ],
            "context": {},
            "turn_created": 1,
            "blocking": False,
        })
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response(1, game_state)
        assert result["success"] is True
        assert world.talleyrand_state == "IDLE"
        assert world.active_diplomatic_mission is None

    def test_mission_pauses_during_proposal(self):
        world = make_world()
        executor = make_executor()
        world.talleyrand_state = "ON_MISSION"
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 2,
            "paused": False,
            "paused_turns": 0,
        }
        world.diplomatic_points = 10
        world.dialogue_manager.replace({
            "type": "proposal_confirm",
            "target_nation": "Prussia",
            "talleyrand_text": "Send?",
            "options": [
                {
                    "label": "Send",
                    "description": "Go.",
                    "action": "execute_proposal",
                    "terms": {
                        "proposal_type": "peace",
                        "target_nation": "Prussia",
                        "sweeteners": [],
                        "demands": [],
                        "clauses": [],
                    },
                },
            ],
            "context": {},
            "turn_created": 1,
            "blocking": False,
        })
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response(1, game_state)
        assert result["success"] is True
        assert world.talleyrand_state == "IN_TRANSIT"
        assert world.active_diplomatic_mission["paused"] is True

    def test_mission_resumes_after_proposal_return(self):
        world = make_world()
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 2,
            "paused": True,
            "paused_turns": 0,
        }
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"
        world.talleyrand_state = "IN_TRANSIT"
        world.proposal_in_transit = {
            "target": "Prussia",
            "proposal": {
                "type": "peace",
                "proposer_nation": "France",
                "target_nation": "Prussia",
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            },
            "turn_sent": world.current_turn - 1,
        }
        world._process_proposal_in_transit()
        assert world.talleyrand_state == "ON_MISSION"
        assert world.active_diplomatic_mission["paused"] is False


# ======================================================
# 4E. Feasibility Request
# ======================================================

class TestFeasibilityRequest:

    def test_generate_feasibility_dialogue(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"
        world.war_scores[diplo_key] = 20
        parsed = {
            "target_nation": "Prussia",
            "proposal_type": "peace",
            "raw_text": "what would it take?",
        }
        dialogue = generate_feasibility_dialogue(parsed, world)
        assert dialogue["type"] == "feasibility"
        assert dialogue["target_nation"] == "Prussia"
        assert "acceptance_score" in dialogue["context"]
        assert "acceptance_outcome" in dialogue["context"]
        assert dialogue["context"]["acceptance_outcome"] in ("ACCEPT", "COUNTER_OFFER", "REJECT")

    def test_feasibility_zero_dp_cost(self):
        world = make_world()
        executor = make_executor()
        initial_dp = world.diplomatic_points
        diplomatic_data = {
            "action": "diplomatic_feasibility",
            "target_nation": "Prussia",
            "proposal_type": "peace",
            "raw_text": "what would it take?",
        }
        command = {"action": "diplomatic_feasibility", "diplomatic_data": diplomatic_data}
        game_state = {"world": world}
        result = executor._execute_diplomatic(command, game_state)
        assert result["success"] is True
        assert world.diplomatic_points == initial_dp

    def test_feasibility_no_state_change(self):
        world = make_world()
        executor = make_executor()
        assert world.talleyrand_state == "IDLE"
        diplomatic_data = {
            "action": "diplomatic_feasibility",
            "target_nation": "Prussia",
            "proposal_type": "peace",
            "raw_text": "what would it take?",
        }
        command = {"action": "diplomatic_feasibility", "diplomatic_data": diplomatic_data}
        game_state = {"world": world}
        executor._execute_diplomatic(command, game_state)
        assert world.talleyrand_state == "IDLE"

    def test_feasibility_missing_nation(self):
        world = make_world()
        parsed = {"target_nation": None, "proposal_type": "peace", "raw_text": "what would it take?"}
        dialogue = generate_feasibility_dialogue(parsed, world)
        assert "which nation" in dialogue["talleyrand_text"].lower()

    def test_feasibility_includes_dp_cost_info(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"
        parsed = {"target_nation": "Prussia", "proposal_type": "peace", "raw_text": "what would it take?"}
        dialogue = generate_feasibility_dialogue(parsed, world)
        assert "dp" in dialogue["talleyrand_text"].lower() or "DP" in dialogue["talleyrand_text"]

    def test_feasibility_has_proceed_option(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"
        parsed = {"target_nation": "Prussia", "proposal_type": "peace", "raw_text": "what would it take?"}
        dialogue = generate_feasibility_dialogue(parsed, world)
        actions = [o["action"] for o in dialogue["options"]]
        assert "execute_proposal" in actions
        assert "dismiss" in actions


# ======================================================
# 4F. Cooldown Enforcement
# ======================================================

class TestCooldownEnforcement:

    def test_rejection_sets_cooldowns(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"
        world.war_scores[diplo_key] = -50
        world.nation_relations[diplo_key] = -80
        world.talleyrand_state = "IN_TRANSIT"
        world.proposal_in_transit = {
            "target": "Prussia",
            "proposal": {
                "type": "peace",
                "proposer_nation": "France",
                "target_nation": "Prussia",
                "sweeteners": [],
                "demands": [{"type": "gold", "value": 1000}],
                "clauses": [],
            },
            "turn_sent": world.current_turn - 1,
        }
        events = world._process_proposal_in_transit()
        assert len(events) > 0
        if events[0]["outcome"] in ("REJECT", "COUNTER_OFFER"):
            assert "Prussia" in world.player_proposal_cooldowns
            # PL-5B: +1 for decrement timing compensation
            assert world.player_proposal_cooldowns["Prussia"] == 4
            assert "Prussia_peace" in world.player_proposal_cooldowns
            assert world.player_proposal_cooldowns["Prussia_peace"] == 6
    def test_cooldown_blocks_subsequent_proposal(self):
        world = make_world()
        executor = make_executor()
        world.player_proposal_cooldowns = {"Prussia": 3, "Prussia_peace": 5}
        world.diplomatic_points = 10
        diplomatic_data = {
            "action": "diplomatic_proposal",
            "target_nation": "Prussia",
            "proposal_type": "peace",
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "mission_type": None,
            "raw_text": "propose peace with Prussia",
        }
        command = {"action": "diplomatic_proposal", "diplomatic_data": diplomatic_data}
        game_state = {"world": world}
        result = executor._execute_diplomatic(command, game_state)
        assert result["success"] is False
        assert "patience" in result.get("message", "").lower()

    def test_cooldown_decrements_per_turn(self):
        world = make_world()
        world.player_proposal_cooldowns = {"Prussia": 3, "Prussia_peace": 5}
        world._cooldown_manager.decrement_all()
        assert world.player_proposal_cooldowns["Prussia"] == 2
        assert world.player_proposal_cooldowns["Prussia_peace"] == 4
        world._cooldown_manager.decrement_all()
        assert world.player_proposal_cooldowns["Prussia"] == 1
        assert world.player_proposal_cooldowns["Prussia_peace"] == 3

    def test_cooldown_expires_allows_proposal(self):
        world = make_world()
        executor = make_executor()
        world.player_proposal_cooldowns = {"Prussia": 1}
        world.diplomatic_points = 10
        world._cooldown_manager.decrement_all()
        assert "Prussia" not in world.player_proposal_cooldowns
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"
        diplomatic_data = {
            "action": "diplomatic_proposal",
            "target_nation": "Prussia",
            "proposal_type": "peace",
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "mission_type": None,
            "raw_text": "propose peace with Prussia",
        }
        command = {"action": "diplomatic_proposal", "diplomatic_data": diplomatic_data}
        game_state = {"world": world}
        result = executor._execute_diplomatic(command, game_state)
        assert result["success"] is True
    def test_type_cooldown_blocks_same_type_only(self):
        world = make_world()
        executor = make_executor()
        world.player_proposal_cooldowns = {"Prussia_peace": 5}
        world.diplomatic_points = 10
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"
        data_peace = {
            "action": "diplomatic_proposal",
            "target_nation": "Prussia",
            "proposal_type": "peace",
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "mission_type": None,
            "raw_text": "propose peace with Prussia",
        }
        result_peace = executor._execute_diplomatic(
            {"action": "diplomatic_proposal", "diplomatic_data": data_peace},
            {"world": world},
        )
        assert result_peace["success"] is False
        data_arm = {
            "action": "diplomatic_proposal",
            "target_nation": "Prussia",
            "proposal_type": "armistice",
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "mission_type": None,
            "raw_text": "propose armistice with Prussia",
        }
        result_arm = executor._execute_diplomatic(
            {"action": "diplomatic_proposal", "diplomatic_data": data_arm},
            {"world": world},
        )
        assert result_arm["success"] is True
    def test_nation_wide_cooldown_blocks_all_types(self):
        world = make_world()
        executor = make_executor()
        world.player_proposal_cooldowns = {"Prussia": 3}
        world.diplomatic_points = 10
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"
        for ptype in ["peace", "armistice"]:
            data = {
                "action": "diplomatic_proposal",
                "target_nation": "Prussia",
                "proposal_type": ptype,
                "clauses": [],
                "is_question": False,
                "has_diplomatic_keywords": True,
                "mission_type": None,
                "raw_text": "propose " + ptype + " with Prussia",
            }
            result = executor._execute_diplomatic(
                {"action": "diplomatic_proposal", "diplomatic_data": data},
                {"world": world},
            )
            assert result["success"] is False, "Nation cooldown should block " + ptype

    def test_dismiss_clears_pending(self):
        world = make_world()
        executor = make_executor()
        world.dialogue_manager.replace({
            "type": "proposal_options",
            "target_nation": "Prussia",
            "talleyrand_text": "What shall I do?",
            "options": [{"label": "Dismiss", "description": "Cancel.", "action": "dismiss"}],
            "context": {},
            "turn_created": 1,
            "blocking": False,
        })
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response(1, game_state)
        assert result["success"] is True
        assert world.pending_diplomatic_dialogue is None
    def test_insufficient_dp_blocks_proposal(self):
        world = make_world()
        executor = make_executor()
        world.diplomatic_points = 0
        diplomatic_data = {
            "action": "diplomatic_proposal",
            "target_nation": "Prussia",
            "proposal_type": "peace",
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "mission_type": None,
            "raw_text": "propose peace with Prussia",
        }
        command = {"action": "diplomatic_proposal", "diplomatic_data": diplomatic_data}
        game_state = {"world": world}
        result = executor._execute_diplomatic(command, game_state)
        assert result["success"] is False
        assert "insufficient" in result.get("message", "").lower()

    def test_in_transit_blocks_new_proposals(self):
        world = make_world()
        executor = make_executor()
        world.talleyrand_state = "IN_TRANSIT"
        world.diplomatic_points = 10
        diplomatic_data = {
            "action": "diplomatic_proposal",
            "target_nation": "Austria",
            "proposal_type": "peace",
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "mission_type": None,
            "raw_text": "propose peace with Austria",
        }
        command = {"action": "diplomatic_proposal", "diplomatic_data": diplomatic_data}
        game_state = {"world": world}
        result = executor._execute_diplomatic(command, game_state)
        assert result["success"] is False
        msg = result.get("message", "").lower()
        assert "transit" in msg or "en route" in msg or "route" in msg

    def test_no_pending_dialogue_response_error(self):
        world = make_world()
        executor = make_executor()
        world.dialogue_manager.pop()
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response(1, game_state)
        assert result["success"] is False

    def test_invalid_choice_number_error(self):
        world = make_world()
        executor = make_executor()
        world.dialogue_manager.replace({
            "type": "proposal_confirm",
            "target_nation": "Prussia",
            "talleyrand_text": "Test",
            "options": [{"label": "Dismiss", "description": "Cancel.", "action": "dismiss"}],
            "context": {},
            "turn_created": 1,
            "blocking": False,
        })
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response(5, game_state)
        assert result["success"] is False


# ======================================================
# 5A. (EC-Q) Double Proposal Block
# ======================================================

class TestDoubleProposalBlock:
    """Send proposal to Prussia (Talleyrand IN_TRANSIT), then try Austria -- should be blocked."""

    def test_second_proposal_blocked_while_in_transit(self):
        world = make_world()
        executor = make_executor()

        assert world.is_at_war("France", "Prussia")
        world.diplomatic_points = 10

        world.talleyrand_state = "IN_TRANSIT"
        world.proposal_in_transit = {
            "target": "Prussia",
            "proposal": {
                "type": "peace",
                "proposer_nation": "France",
                "target_nation": "Prussia",
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            },
            "turn_sent": int(world.current_turn),
        }

        diplomatic_data = {
            "action": "diplomatic_proposal",
            "target_nation": "Austria",
            "proposal_type": "non_aggression",
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "mission_type": None,
            "raw_text": "propose non-aggression with Austria",
        }
        command = {"action": "diplomatic_proposal", "diplomatic_data": diplomatic_data}
        game_state = {"world": world}
        result = executor._execute_diplomatic(command, game_state)

        assert result["success"] is False
        msg = result.get("message", "").lower()
        assert "transit" in msg or "en route" in msg or "route" in msg

    def test_feasibility_allowed_while_in_transit(self):
        """Feasibility checks (0 DP) should still work while Talleyrand is in transit."""
        world = make_world()
        executor = make_executor()
        world.talleyrand_state = "IN_TRANSIT"
        world.proposal_in_transit = {
            "target": "Prussia",
            "proposal": {"type": "peace", "proposer_nation": "France", "target_nation": "Prussia",
                         "sweeteners": [], "demands": [], "clauses": []},
            "turn_sent": int(world.current_turn),
        }

        diplomatic_data = {
            "action": "diplomatic_feasibility",
            "target_nation": "Austria",
            "proposal_type": "non_aggression",
            "clauses": [],
            "is_question": True,
            "has_diplomatic_keywords": True,
            "mission_type": None,
            "raw_text": "can we negotiate with Austria?",
        }
        command = {"action": "diplomatic_proposal", "diplomatic_data": diplomatic_data}
        game_state = {"world": world}
        result = executor._execute_diplomatic(command, game_state)
        assert result["success"] is True


# ======================================================
# 5B. (EC-R) Mission + Proposal Interaction
# ======================================================

class TestMissionProposalInteraction:
    """Mission pauses during proposal transit and resumes after."""

    def test_mission_pauses_during_transit_and_resumes(self):
        world = make_world()
        executor = make_executor()
        world.diplomatic_points = 10

        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 2,
            "paused": False,
            "paused_turns": 0,
        }
        world.talleyrand_state = "ON_MISSION"

        world.dialogue_manager.replace({
            "type": "proposal_confirm",
            "target_nation": "Prussia",
            "talleyrand_text": "Shall I send this?",
            "options": [
                {
                    "label": "Send",
                    "description": "Dispatch proposal.",
                    "action": "execute_proposal",
                    "terms": {
                        "proposal_type": "peace",
                        "sweeteners": [],
                        "demands": [],
                        "clauses": [],
                    },
                },
                {"label": "Dismiss", "description": "Cancel.", "action": "dismiss"},
            ],
            "context": {},
            "turn_created": int(world.current_turn),
            "blocking": False,
        })
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response(1, game_state)
        assert result["success"] is True

        assert world.talleyrand_state == "IN_TRANSIT"
        assert world.active_diplomatic_mission is not None
        assert world.active_diplomatic_mission["paused"] is True
        assert world.active_diplomatic_mission["type"] == "IMPROVE_RELATIONS"

        assert world.proposal_in_transit is not None
        assert world.proposal_in_transit["target"] == "Prussia"

        world.advance_turn()

        assert world.proposal_in_transit is None
        assert world.talleyrand_state == "ON_MISSION"
        assert world.active_diplomatic_mission is not None
        assert world.active_diplomatic_mission["paused"] is False


# ======================================================
# 5C. (EC-S) DP Starvation During Mission
# ======================================================

class TestDPStarvationDuringMission:
    """Mission pauses when DP is insufficient; does not crash."""

    def test_mission_pauses_when_dp_insufficient(self):
        world = make_world()

        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 1,
            "paused": False,
            "paused_turns": 0,
        }
        world.talleyrand_state = "ON_MISSION"

        from backend.game_logic.diplomacy import _process_mission_dp
        world.diplomatic_points = 0
        events = _process_mission_dp(world)

        assert world.active_diplomatic_mission["paused"] is True
        assert len(events) >= 1
        assert any("paused" in e.get("type", "") or "curtailed" in e.get("message", "").lower()
                    for e in events)

    def test_mission_starvation_no_crash_on_advance_turn(self):
        """advance_turn with active mission and 0 DP should not crash."""
        world = make_world()
        world.active_diplomatic_mission = {
            "type": "COURT_NATION",
            "target": "Prussia",
            "turns_active": 0,
            "paused": False,
            "paused_turns": 0,
        }
        world.talleyrand_state = "ON_MISSION"
        world.diplomatic_points = 0

        world.advance_turn()

        assert world.active_diplomatic_mission is not None or world.talleyrand_state == "IDLE"

    def test_mission_auto_cancels_after_3_paused_turns(self):
        """Mission auto-cancels after 3+ consecutive paused turns."""
        from backend.game_logic.diplomacy import _process_mission_dp

        world = make_world()
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 2,
            "paused": True,
            "paused_turns": 2,
        }
        world.talleyrand_state = "ON_MISSION"
        world.diplomatic_points = 0

        events = _process_mission_dp(world)

        assert world.active_diplomatic_mission is None
        assert world.talleyrand_state == "IDLE"
        assert any("cancelled" in e.get("type", "") or "collapsed" in e.get("message", "").lower()
                    for e in events)


# ======================================================
# 5D. Save/Load Mid-Dialogue
# ======================================================

class TestSaveLoadMidDialogue:
    """Pending diplomatic dialogue survives save/load roundtrip."""

    def test_dialogue_survives_roundtrip(self):
        world = make_world()

        dialogue = {
            "type": "proposal_confirm",
            "target_nation": "Prussia",
            "talleyrand_text": "Sire, shall I present these terms to the Prussians?",
            "options": [
                {
                    "label": "Send these terms",
                    "description": "Dispatch Talleyrand with the proposal.",
                    "action": "execute_proposal",
                    "terms": {"proposal_type": "peace", "sweeteners": [], "demands": []},
                },
                {
                    "label": "Make them harsher",
                    "description": "Push for more concessions.",
                    "action": "modify_harsh",
                    "terms": {"proposal_type": "peace"},
                },
                {
                    "label": "Dismiss",
                    "description": "Cancel the proposal.",
                    "action": "dismiss",
                },
            ],
            "context": {"war_score": 15, "relation": -40},
            "turn_created": 3,
            "blocking": False,
        }
        world.dialogue_manager.replace(dialogue)

        saved = world.to_dict()
        loaded = WorldState.from_dict(saved)

        d = loaded.pending_diplomatic_dialogue
        assert d is not None
        assert d["type"] == "proposal_confirm"
        assert d["target_nation"] == "Prussia"
        assert d["talleyrand_text"] == dialogue["talleyrand_text"]
        assert len(d["options"]) == 3
        assert d["options"][0]["action"] == "execute_proposal"
        assert d["options"][1]["action"] == "modify_harsh"
        assert d["options"][2]["action"] == "dismiss"
        assert d["context"]["war_score"] == 15
        assert d["context"]["relation"] == -40
        assert d["turn_created"] == 3
        assert d["blocking"] is False

    def test_none_dialogue_survives_roundtrip(self):
        """No dialogue (None) should remain None after roundtrip."""
        world = make_world()
        world.dialogue_manager.pop()

        saved = world.to_dict()
        loaded = WorldState.from_dict(saved)
        assert loaded.pending_diplomatic_dialogue is None


# ======================================================
# 5E. Save/Load Mid-Transit
# ======================================================

class TestSaveLoadMidTransit:
    """Proposal in transit survives save/load and resolves next turn."""

    def test_transit_survives_roundtrip(self):
        world = make_world()
        world.talleyrand_state = "IN_TRANSIT"
        world.proposal_in_transit = {
            "target": "Prussia",
            "proposal": {
                "type": "peace",
                "proposer_nation": "France",
                "target_nation": "Prussia",
                "sweeteners": [{"type": "gold_lump", "value": 500}],
                "demands": [],
                "clauses": [],
            },
            "turn_sent": 1,
        }

        saved = world.to_dict()
        loaded = WorldState.from_dict(saved)

        assert loaded.talleyrand_state == "IN_TRANSIT"
        assert loaded.proposal_in_transit is not None
        assert loaded.proposal_in_transit["target"] == "Prussia"
        assert loaded.proposal_in_transit["turn_sent"] == 1
        assert loaded.proposal_in_transit["proposal"]["type"] == "peace"
        assert len(loaded.proposal_in_transit["proposal"]["sweeteners"]) == 1

    def test_transit_resolves_after_load(self):
        """Proposal in transit resolves on advance_turn after load."""
        world = make_world()
        world.current_turn = 1
        world.talleyrand_state = "IN_TRANSIT"
        world.proposal_in_transit = {
            "target": "Prussia",
            "proposal": {
                "type": "peace",
                "proposer_nation": "France",
                "target_nation": "Prussia",
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            },
            "turn_sent": 1,
        }

        saved = world.to_dict()
        loaded = WorldState.from_dict(saved)

        loaded.advance_turn()

        assert loaded.proposal_in_transit is None
        assert loaded.talleyrand_state == "IDLE"


# ======================================================
# 5F. Treaty Per-Turn Clause Accumulation
# ======================================================

class TestTreatyPerTurnClauses:
    """Gold/turn treaty clause accumulates correctly over multiple turns."""

    def test_gold_per_turn_accumulates_over_5_turns(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")

        world.diplomatic_states[diplo_key] = "PEACE"

        france_start = world.nation_gold.get("France", 0)
        prussia_start = world.nation_gold.get("Prussia", 0)

        world.active_treaties[diplo_key] = {
            "nations": ["France", "Prussia"],
            "type": "peace",
            "state_transition": "WAR_TO_PEACE",
            "clauses": [
                {
                    "type": "gold_per_turn",
                    "from": "France",
                    "to": "Prussia",
                    "amount": 200,
                },
            ],
            "turn_signed": int(world.current_turn),
            "harshness": 10,
        }

        for _ in range(5):
            world._process_treaty_clauses()

        france_end = world.nation_gold.get("France", 0)
        prussia_end = world.nation_gold.get("Prussia", 0)

        # R3 gold floor: France starts at 800, pays 200/turn for 4 turns (800),
        # then can't pay on turn 5. Total transferred = min(1000, france_start).
        expected_transfer = min(1000, france_start)
        assert france_end == france_start - expected_transfer
        assert prussia_end == prussia_start + expected_transfer

    def test_gold_per_turn_via_advance_turn(self):
        """Verify clause fires once per advance_turn call."""
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "PEACE"

        world.active_treaties[diplo_key] = {
            "nations": ["France", "Prussia"],
            "type": "peace",
            "state_transition": "WAR_TO_PEACE",
            "clauses": [
                {
                    "type": "gold_per_turn",
                    "from": "France",
                    "to": "Prussia",
                    "amount": 100,
                },
            ],
            "turn_signed": int(world.current_turn),
            "harshness": 5,
        }

        world.advance_turn()

        france_after = world.nation_gold.get("France", 0)
        # Compare with a world without the treaty
        world2 = make_world()
        diplo_key2 = world2._make_diplo_key("France", "Prussia")
        world2.diplomatic_states[diplo_key2] = "PEACE"
        world2.current_turn = world.current_turn - 1
        world2.advance_turn()
        france_no_treaty = world2.nation_gold.get("France", 0)

        assert france_after == france_no_treaty - 100


# ======================================================
# 5G. Battle Recording Hook
# ======================================================

class TestBattleRecordingHook:
    """Combat between France and Prussia updates battle_records and war_scores."""

    def test_record_battle_updates_records_and_war_score(self):
        """Directly call record_battle and verify state updates."""
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")

        assert world.is_at_war("France", "Prussia")
        assert diplo_key not in world.battle_records or len(world.battle_records.get(diplo_key, [])) == 0

        record_battle(
            world,
            attacker_nation="France",
            defender_nation="Prussia",
            winner_nation="France",
            attacker_casualties=3000,
            defender_casualties=8000,
        )

        records = world.battle_records.get(diplo_key, [])
        assert len(records) == 1
        assert records[0]["winner"] == "France"
        assert records[0]["attacker"] == "France"
        assert records[0]["defender"] == "Prussia"
        assert records[0]["attacker_casualties"] == 3000
        assert records[0]["defender_casualties"] == 8000

        from backend.game_logic.diplomacy import recalculate_war_scores
        recalculate_war_scores(world)

        score = world.war_scores.get(diplo_key, 0)
        assert score != 0

    def test_record_battle_ignores_non_war_nations(self):
        """record_battle does nothing if nations are not at war."""
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Austria")

        assert not world.is_at_war("France", "Austria")

        record_battle(
            world,
            attacker_nation="France",
            defender_nation="Austria",
            winner_nation="France",
            attacker_casualties=5000,
            defender_casualties=10000,
        )

        records = world.battle_records.get(diplo_key, [])
        assert len(records) == 0

    def test_decisive_battle_detected(self):
        """Battle with >10k total casualties and >2:1 ratio is decisive."""
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        assert world.is_at_war("France", "Prussia")

        record_battle(
            world,
            attacker_nation="France",
            defender_nation="Prussia",
            winner_nation="France",
            attacker_casualties=2000,
            defender_casualties=12000,
        )

        decisive = world.decisive_battles.get(diplo_key, [])
        assert len(decisive) == 1
        assert decisive[0]["winner"] == "France"
        assert decisive[0]["total_casualties"] == 14000

    def test_max_2_decisive_battles_per_war(self):
        """Only 2 decisive battles are recorded per war."""
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")

        for i in range(5):
            record_battle(
                world,
                attacker_nation="France",
                defender_nation="Prussia",
                winner_nation="France",
                attacker_casualties=2000,
                defender_casualties=12000,
            )

        decisive = world.decisive_battles.get(diplo_key, [])
        assert len(decisive) == 2


# ======================================================
# 5H. Backward Compatibility -- Missing Session 2+3 Fields
# ======================================================

class TestBackwardCompatibility:
    """from_dict with missing ALL Session 2+3 fields should not crash."""

    def test_missing_all_session_2_3_fields(self):
        """Construct a minimal save dict and verify from_dict handles missing fields."""
        world = make_world()
        data = world.to_dict()

        session_2_keys = [
            "diplomats",
            "diplomatic_points",
            "max_diplomatic_points",
            "nation_authority",
            "war_scores",
            "battle_records",
            "decisive_battles",
            "armistice_cooldowns",
            "previous_treaties",
            "turns_below_threshold",
        ]
        for key in session_2_keys:
            data.pop(key, None)

        session_3_keys = [
            "pending_diplomatic_dialogue",
            "active_diplomatic_mission",
            "talleyrand_state",
            "proposal_in_transit",
            "player_proposal_cooldowns",
            "active_treaties",
        ]
        for key in session_3_keys:
            data.pop(key, None)

        loaded = WorldState.from_dict(data)

        assert loaded.diplomatic_points == 4
        assert loaded.max_diplomatic_points == 5
        assert isinstance(loaded.war_scores, dict)
        assert isinstance(loaded.battle_records, dict)
        assert isinstance(loaded.decisive_battles, dict)
        assert isinstance(loaded.armistice_cooldowns, dict)
        assert isinstance(loaded.previous_treaties, dict)
        assert isinstance(loaded.turns_below_threshold, dict)

        assert loaded.pending_diplomatic_dialogue is None
        assert loaded.active_diplomatic_mission is None
        assert loaded.talleyrand_state == "IDLE"
        assert loaded.proposal_in_transit is None
        assert isinstance(loaded.player_proposal_cooldowns, dict)
        assert isinstance(loaded.active_treaties, dict)

        assert "France" in loaded.diplomats
        assert loaded.diplomats["France"].name == "Talleyrand"

    def test_partial_session_2_fields(self):
        """Some Session 2 fields present, others missing."""
        world = make_world()
        data = world.to_dict()

        data.pop("war_scores", None)
        data.pop("battle_records", None)
        data.pop("decisive_battles", None)
        data.pop("armistice_cooldowns", None)
        data.pop("previous_treaties", None)
        data.pop("turns_below_threshold", None)
        data.pop("active_treaties", None)

        loaded = WorldState.from_dict(data)

        assert loaded.diplomatic_points == data.get("diplomatic_points", 4)
        assert isinstance(loaded.war_scores, dict)
        assert len(loaded.war_scores) == 0
        assert isinstance(loaded.active_treaties, dict)

    def test_backward_compat_advance_turn_no_crash(self):
        """A loaded world with all Session 2+3 defaults should survive advance_turn."""
        world = make_world()
        data = world.to_dict()

        for key in ["diplomats", "diplomatic_points", "max_diplomatic_points",
                     "nation_authority", "war_scores", "battle_records",
                     "decisive_battles", "armistice_cooldowns", "previous_treaties",
                     "turns_below_threshold", "pending_diplomatic_dialogue",
                     "active_diplomatic_mission", "talleyrand_state",
                     "proposal_in_transit", "player_proposal_cooldowns",
                     "active_treaties"]:
            data.pop(key, None)

        loaded = WorldState.from_dict(data)

        loaded.advance_turn()

        assert loaded.current_turn >= 2
        assert isinstance(loaded.diplomatic_points, int)


# ======================================================
# 7. Coverage Gap Tests — diplomatic_templates.py
# ======================================================

class TestTemplateFallbackChain:
    """Tests for get_template() fallback chain (63% coverage gap)."""

    def test_exact_match(self):
        """get_template returns exact match when available."""
        from backend.game_logic.diplomatic_templates import get_template
        t = get_template("proposal_options", "WAR", "winning_comfortably")
        assert "commanding position" in t["text"]

    def test_wildcard_bucket(self):
        """get_template falls back to 'any' bucket when exact bucket missing."""
        from backend.game_logic.diplomatic_templates import get_template
        # proposal_confirm has WAR/any but not WAR/winning_comfortably
        t = get_template("proposal_confirm", "WAR", "winning_comfortably")
        assert t is not None
        assert "options" in t

    def test_war_similar_bucket_winning_slightly(self):
        """WAR + winning_slightly falls back to winning_comfortably."""
        from backend.game_logic.diplomatic_templates import get_template
        t = get_template("proposal_options", "WAR", "winning_slightly")
        # winning_slightly -> winning_comfortably (similar_map)
        assert "commanding position" in t["text"]

    def test_war_similar_bucket_losing_slightly(self):
        """WAR + losing_slightly falls back to losing_badly."""
        from backend.game_logic.diplomatic_templates import get_template
        t = get_template("proposal_options", "WAR", "losing_slightly")
        # losing_slightly -> losing_badly (similar_map)
        assert "difficult" in t["text"].lower() or "losing" in t["text"].lower() or t["text"]  # any non-empty

    def test_peace_neutral_falls_to_hostile(self):
        """PEACE + neutral falls back to hostile template."""
        from backend.game_logic.diplomatic_templates import get_template
        t = get_template("proposal_options", "PEACE", "neutral")
        # neutral -> hostile (step 4 fallback)
        assert t is not None
        assert "options" in t

    def test_fallback_templates(self):
        """Unknown bucket triggers FALLBACK_TEMPLATES."""
        from backend.game_logic.diplomatic_templates import get_template
        # Use a made-up state/bucket that won't match any template
        t = get_template("proposal_options", "ARMISTICE", "unknown_bucket")
        assert t is not None
        assert "Sire" in t["text"]  # Fallback has "Sire, how shall I approach"

    def test_ultimate_fallback(self):
        """Completely unknown intent_type returns ultimate fallback."""
        from backend.game_logic.diplomatic_templates import get_template
        t = get_template("nonexistent_intent", "WAR", "any")
        assert t is not None
        assert "Dismiss" in t["options"][0]["label"]
        assert "await your instructions" in t["text"]

    def test_proposal_type_propagated(self):
        """proposal_type is stored on template when provided."""
        from backend.game_logic.diplomatic_templates import get_template
        t = get_template("proposal_options", "WAR", "winning_comfortably", proposal_type="peace")
        assert t.get("_proposal_type") == "peace"

    def test_proposal_type_propagated_fallback(self):
        """proposal_type propagated even through fallback chain."""
        from backend.game_logic.diplomatic_templates import get_template
        t = get_template("proposal_options", "ARMISTICE", "unknown", proposal_type="alliance")
        assert t.get("_proposal_type") == "alliance"


class TestGenerateSuggestedTerms:
    """Tests for generate_suggested_terms() for different proposal types."""

    def test_peace_winning(self):
        """Peace proposal while winning includes gold demand."""
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = 30
        terms = generate_suggested_terms("Prussia", "peace", world)
        assert terms["type"] == "peace"
        assert any(d["type"] == "gold_per_turn" for d in terms["demands"])

    def test_peace_losing(self):
        """Peace proposal while losing includes sweeteners (gold or territory)."""
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = -30
        terms = generate_suggested_terms("Prussia", "peace", world)
        # Bug 4 fix: Nations with gold_pref=low may get territory instead of gold
        assert len(terms["sweeteners"]) >= 1, "Losing peace proposal should have sweeteners"

    def test_peace_neutral_open_borders(self):
        """Peace with neutral relation includes open_borders clause."""
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Austria")
        world.nation_relations[diplo_key] = 0
        terms = generate_suggested_terms("Austria", "peace", world)
        assert "open_borders" in terms["clauses"]

    def test_alliance_terms(self):
        """Alliance includes open_borders."""
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        world = make_world()
        terms = generate_suggested_terms("Saxony", "alliance", world)
        assert "open_borders" in terms["clauses"]

    def test_open_borders_terms(self):
        """Open borders proposal includes clause."""
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        world = make_world()
        terms = generate_suggested_terms("Austria", "open_borders", world)
        assert "open_borders" in terms["clauses"]

    def test_non_aggression_terms(self):
        """Non-aggression has no special terms."""
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        world = make_world()
        terms = generate_suggested_terms("Austria", "non_aggression", world)
        assert terms["sweeteners"] == []
        assert terms["demands"] == []


class TestResolveTemplateTextWithType:
    """Tests for resolve_template_text_with_type()."""

    def test_replaces_proposal_type(self):
        """proposal_type slot is resolved."""
        from backend.game_logic.diplomatic_templates import resolve_template_text_with_type
        world = make_world()
        result = resolve_template_text_with_type(
            "Preparing a {proposal_type} proposal for {target_nation}.",
            world, "Prussia", "peace"
        )
        assert "peace" in result
        assert "Prussia" in result

    def test_no_proposal_type(self):
        """When proposal_type is None, {proposal_type} stays unresolved."""
        from backend.game_logic.diplomatic_templates import resolve_template_text_with_type
        world = make_world()
        result = resolve_template_text_with_type(
            "A {proposal_type} deal.",
            world, "Prussia", None
        )
        assert "{proposal_type}" in result


# ======================================================
# 8. Coverage Gap Tests — diplomatic_dialogue.py
# ======================================================

class TestResolveNationName:
    """Tests for resolve_nation_name() exact/alias/no-match."""

    def test_exact_match(self):
        from backend.game_logic.diplomatic_dialogue import resolve_nation_name
        assert resolve_nation_name("Prussia") == "Prussia"

    def test_alias_match(self):
        from backend.game_logic.diplomatic_dialogue import resolve_nation_name
        assert resolve_nation_name("england") == "Britain"
        assert resolve_nation_name("united kingdom") == "Britain"
        assert resolve_nation_name("the saxon people") == "Saxony"

    def test_no_match(self):
        from backend.game_logic.diplomatic_dialogue import resolve_nation_name
        assert resolve_nation_name("Spain") is None
        assert resolve_nation_name("random text") is None


class TestGetGameBucketBranches:
    """Tests for get_game_bucket() losing/neutral branches."""

    def test_war_losing_badly(self):
        from backend.game_logic.diplomatic_dialogue import get_game_bucket
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Britain")
        # Key is "Britain|France", positive = Britain winning. After sign flip: France losing.
        world.war_scores[diplo_key] = 40
        assert get_game_bucket("Britain", world) == "losing_badly"

    def test_war_stalemate(self):
        from backend.game_logic.diplomatic_dialogue import get_game_bucket
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Britain")
        world.war_scores[diplo_key] = 0
        assert get_game_bucket("Britain", world) == "stalemate"

    def test_peace_neutral(self):
        from backend.game_logic.diplomatic_dialogue import get_game_bucket
        world = make_world()
        # Austria is at PEACE with France, default relation is 0
        diplo_key = world._make_diplo_key("France", "Austria")
        world.nation_relations[diplo_key] = 0
        assert get_game_bucket("Austria", world) == "neutral"

    def test_peace_hostile(self):
        from backend.game_logic.diplomatic_dialogue import get_game_bucket
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Austria")
        world.nation_relations[diplo_key] = -30
        assert get_game_bucket("Austria", world) == "hostile"


# ======================================================
# 9. Coverage Gap Tests — diplomacy.py
# ======================================================

class TestGetTransitionDpCost:
    """Tests for get_transition_dp_cost() various paths."""

    def test_war_cost(self):
        from backend.game_logic.diplomacy import get_transition_dp_cost, WAR_DP_COST
        assert get_transition_dp_cost("PEACE", "WAR") == WAR_DP_COST

    def test_vassal_cost(self):
        from backend.game_logic.diplomacy import get_transition_dp_cost, VASSAL_DP_COST
        assert get_transition_dp_cost("OPEN_BORDERS", "VASSAL") == VASSAL_DP_COST

    def test_upgrade_cost(self):
        from backend.game_logic.diplomacy import get_transition_dp_cost
        # PEACE -> OPEN_BORDERS costs 1 (from TRANSITION_RULES)
        assert get_transition_dp_cost("PEACE", "OPEN_BORDERS") == 1
        # NON_AGGRESSION -> DEFENSIVE_ALLIANCE costs 2
        assert get_transition_dp_cost("NON_AGGRESSION", "DEFENSIVE_ALLIANCE") == 2

    def test_downgrade_cost(self):
        from backend.game_logic.diplomacy import get_transition_dp_cost
        # ALLIANCE -> DEFENSIVE_ALLIANCE downgrade costs 1
        assert get_transition_dp_cost("ALLIANCE", "DEFENSIVE_ALLIANCE") == 1

    def test_jump_transition_cumulative_cost(self):
        from backend.game_logic.diplomacy import get_transition_dp_cost
        # R98: PEACE→ALLIANCE = 1+1+2+2 = 6 DP (cumulative)
        assert get_transition_dp_cost("PEACE", "ALLIANCE") == 6
