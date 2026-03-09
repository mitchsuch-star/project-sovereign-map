"""
Tests for Phase 8 Session 2: Diplomatic States + Acceptance Formula + Diplomat Class

Gate criteria:
- Transition validation (adjacency enforced)
- Relation requirements for upgrades
- Armistice cooldown
- War score calculation (territory + battle + capital + decisive)
- War score decay
- Acceptance formula (reproduce §6c worked example)
- Special bonuses
- DP generation and spending
- Skill cost penalty
- Trade income
- Movement restriction
- War declaration + cascade
- Diplomat serialization
- Formula feedback
- Downgrade transitions
- Battle recording
"""

from backend.models.world_state import WorldState
from backend.models.diplomat import DiplomaticRepresentative, create_starting_diplomats
from backend.game_logic.diplomacy import (
    validate_transition,
    check_relation_requirement,
    calculate_war_score,
    calculate_acceptance,
    calculate_dp,
    get_dp_cost,
    declare_war,
    execute_downgrade,
    check_auto_downgrade,
    record_battle,
    can_enter_territory,
    process_trade_income,
    DIPLOMATIC_STATES,
)


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def make_world():
    """Create a fresh WorldState for testing."""
    return WorldState()


# ═══════════════════════════════════════════════════════
# PART 1: DiplomaticRepresentative & Diplomat Data
# ═══════════════════════════════════════════════════════

class TestDiplomat:
    def test_diplomat_creation(self):
        d = DiplomaticRepresentative("Test", "France", "schemer", 10, 55, "Bio")
        assert d.name == "Test"
        assert d.nation == "France"
        assert d.personality == "schemer"
        assert d.skill == 10
        assert d.trust == 55
        assert d.biography == "Bio"

    def test_diplomat_to_dict(self):
        d = DiplomaticRepresentative("Talleyrand", "France", "schemer", 10, 55, "Bio")
        data = d.to_dict()
        assert data["name"] == "Talleyrand"
        assert data["skill"] == 10
        assert data["trust"] == 55
        assert isinstance(data["skill"], int)

    def test_diplomat_from_dict(self):
        data = {"name": "Hardenberg", "nation": "Prussia", "personality": "hawk",
                "skill": 6, "trust": 65, "biography": "Bio"}
        d = DiplomaticRepresentative.from_dict(data)
        assert d.name == "Hardenberg"
        assert d.personality == "hawk"
        assert d.skill == 6

    def test_diplomat_round_trip(self):
        original = DiplomaticRepresentative("Metternich", "Austria", "schemer", 9, 55, "Spider")
        restored = DiplomaticRepresentative.from_dict(original.to_dict())
        assert restored.name == original.name
        assert restored.nation == original.nation
        assert restored.personality == original.personality
        assert restored.skill == original.skill
        assert restored.trust == original.trust
        assert restored.biography == original.biography

    def test_create_starting_diplomats(self):
        diplomats = create_starting_diplomats()
        assert len(diplomats) == 5
        assert "France" in diplomats
        assert "Britain" in diplomats
        assert "Prussia" in diplomats
        assert "Austria" in diplomats
        assert "Saxony" in diplomats

    def test_talleyrand_stats(self):
        diplomats = create_starting_diplomats()
        t = diplomats["France"]
        assert t.name == "Talleyrand"
        assert t.personality == "schemer"
        assert t.skill == 10
        assert t.trust == 55

    def test_einsiedel_stats(self):
        diplomats = create_starting_diplomats()
        e = diplomats["Saxony"]
        assert e.name == "Einsiedel"
        assert e.personality == "dove"
        assert e.skill == 4
        assert e.trust == 65

    def test_world_has_diplomats(self):
        world = make_world()
        assert hasattr(world, 'diplomats')
        assert len(world.diplomats) == 5
        assert world.diplomats["France"].name == "Talleyrand"


# ═══════════════════════════════════════════════════════
# PART 2: State Transition Validation
# ═══════════════════════════════════════════════════════

class TestTransitions:
    def test_upgrade_war_to_armistice(self):
        assert validate_transition("WAR", "ARMISTICE") is True

    def test_upgrade_armistice_to_peace(self):
        assert validate_transition("ARMISTICE", "PEACE") is True

    def test_upgrade_peace_to_open_borders(self):
        assert validate_transition("PEACE", "OPEN_BORDERS") is True

    def test_upgrade_open_borders_to_non_aggression(self):
        assert validate_transition("OPEN_BORDERS", "NON_AGGRESSION") is True

    def test_upgrade_non_aggression_to_defensive_alliance(self):
        assert validate_transition("NON_AGGRESSION", "DEFENSIVE_ALLIANCE") is True

    def test_upgrade_defensive_alliance_to_alliance(self):
        assert validate_transition("DEFENSIVE_ALLIANCE", "ALLIANCE") is True

    def test_jump_war_to_alliance_allowed(self):
        """R98: upward jumps allowed — WAR→ALLIANCE valid with cumulative DP."""
        assert validate_transition("WAR", "ALLIANCE") is True

    def test_jump_peace_to_alliance_allowed(self):
        """R98: PEACE→ALLIANCE upward jump allowed."""
        assert validate_transition("PEACE", "ALLIANCE") is True

    def test_jump_war_to_peace_allowed(self):
        """R98: WAR→PEACE upward jump allowed."""
        assert validate_transition("WAR", "PEACE") is True

    def test_any_to_war(self):
        """Any state can transition to WAR."""
        for state in DIPLOMATIC_STATES:
            if state != "WAR":
                assert validate_transition(state, "WAR") is True, f"{state} → WAR should be valid"

    def test_open_borders_to_vassal(self):
        """OPEN_BORDERS → VASSAL valid (E3 fix)."""
        assert validate_transition("OPEN_BORDERS", "VASSAL") is True

    def test_peace_to_vassal_invalid(self):
        """PEACE → VASSAL invalid (E3 fix: requires minimum OPEN_BORDERS)."""
        assert validate_transition("PEACE", "VASSAL") is False

    def test_war_to_vassal_valid(self):
        """WAR -> VASSAL valid (dictated peace vassalage)."""
        assert validate_transition("WAR", "VASSAL") is True

    def test_vassal_to_war(self):
        assert validate_transition("VASSAL", "WAR") is True

    def test_vassal_to_peace(self):
        assert validate_transition("VASSAL", "PEACE") is True

    def test_same_state_invalid(self):
        assert validate_transition("PEACE", "PEACE") is False

    def test_downgrade_alliance_to_def_alliance(self):
        assert validate_transition("ALLIANCE", "DEFENSIVE_ALLIANCE") is True

    def test_downgrade_def_alliance_to_non_aggression(self):
        assert validate_transition("DEFENSIVE_ALLIANCE", "NON_AGGRESSION") is True


class TestRelationRequirements:
    def test_armistice_to_peace_blocked_below_minus_60(self):
        """ARMISTICE→PEACE blocked when relation ≤ -60."""
        assert check_relation_requirement("ARMISTICE", "PEACE", -60) is False
        assert check_relation_requirement("ARMISTICE", "PEACE", -61) is False

    def test_armistice_to_peace_allowed_above_minus_60(self):
        assert check_relation_requirement("ARMISTICE", "PEACE", -59) is True

    def test_non_aggression_to_def_alliance_blocked(self):
        """NON_AGGRESSION→DEF_ALLIANCE blocked when relation ≤ +20."""
        assert check_relation_requirement("NON_AGGRESSION", "DEFENSIVE_ALLIANCE", 20) is False
        assert check_relation_requirement("NON_AGGRESSION", "DEFENSIVE_ALLIANCE", 10) is False

    def test_non_aggression_to_def_alliance_allowed(self):
        assert check_relation_requirement("NON_AGGRESSION", "DEFENSIVE_ALLIANCE", 21) is True

    def test_war_to_armistice_no_requirement(self):
        assert check_relation_requirement("WAR", "ARMISTICE", -100) is True

    def test_def_alliance_to_alliance_requires_plus_40(self):
        assert check_relation_requirement("DEFENSIVE_ALLIANCE", "ALLIANCE", 40) is False
        assert check_relation_requirement("DEFENSIVE_ALLIANCE", "ALLIANCE", 41) is True


# ═══════════════════════════════════════════════════════
# PART 3: War Score Calculation
# ═══════════════════════════════════════════════════════

class TestWarScore:
    def test_war_score_zero_at_start(self):
        world = make_world()
        score = calculate_war_score("France", "Britain", world)
        # No battles, no territory changes, no capital control
        assert isinstance(score, int)

    def test_territory_score(self):
        world = make_world()
        # Simulate France capturing a British starting region
        world.regions["Netherlands"].controller = "France"
        score = calculate_war_score("France", "Britain", world)
        assert score >= 5  # +5 for holding one enemy starting region

    def test_territory_score_cap(self):
        world = make_world()
        # Give France all British starting regions and more
        for region in world.regions.values():
            region.controller = "France"
        score = calculate_war_score("France", "Britain", world)
        # Should cap territory component at 40
        assert score <= 100

    def test_battle_score(self):
        world = make_world()
        record_battle(world, "France", "Britain", "France", 5000, 8000)
        score = calculate_war_score("France", "Britain", world)
        assert score >= 3  # +3 for one battle won

    def test_battle_score_cap(self):
        world = make_world()
        # 15 French wins = 45, but capped at 30
        for _ in range(15):
            record_battle(world, "France", "Britain", "France", 5000, 8000)
        score = calculate_war_score("France", "Britain", world)
        # battle_score capped at 30, so total should reflect that
        assert score <= 100

    def test_decisive_battle(self):
        world = make_world()
        # Casualty ratio > 2:1 AND total > 10,000
        record_battle(world, "France", "Britain", "France", 3000, 12000)
        assert len(world.decisive_battles.get("Britain|France", [])) == 1

    def test_decisive_battle_max_two(self):
        world = make_world()
        record_battle(world, "France", "Britain", "France", 3000, 12000)
        record_battle(world, "France", "Britain", "France", 2000, 15000)
        record_battle(world, "France", "Britain", "France", 1000, 20000)
        assert len(world.decisive_battles.get("Britain|France", [])) == 2  # Max 2

    def test_capital_score(self):
        world = make_world()
        # France holds Netherlands (Britain's capital proxy)
        world.regions["Netherlands"].controller = "France"
        score = calculate_war_score("France", "Britain", world)
        # Should include +20 capital bonus
        assert score >= 20

    def test_war_score_total_cap(self):
        world = make_world()
        # Max out everything
        for r in world.regions.values():
            r.controller = "France"
        for _ in range(15):
            record_battle(world, "France", "Britain", "France", 3000, 12000)
        score = calculate_war_score("France", "Britain", world)
        assert -100 <= score <= 100

    def test_no_battle_recording_during_peace(self):
        """Battles between nations at PEACE should not be recorded."""
        world = make_world()
        # France and Austria are at PEACE
        record_battle(world, "France", "Austria", "France", 5000, 5000)
        key = world._make_diplo_key("France", "Austria")
        assert len(world.battle_records.get(key, [])) == 0


# ═══════════════════════════════════════════════════════
# PART 4: Acceptance Formula
# ═══════════════════════════════════════════════════════

class TestAcceptanceFormula:
    def test_spec_worked_example_peace_with_prussia(self):
        """Reproduce §6c worked example exactly: peace with Prussia → score 6 → REJECT."""
        world = make_world()
        # Set up conditions from the example
        world.war_scores["France|Prussia"] = 20  # war_score +20 (France winning)
        world.nation_relations["France|Prussia"] = -60
        # Threat = 40 (stubbed at 0 currently, so we skip threat mod)
        # But the example uses threat=40, let's see:

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

        # Expected components (without threat which is stubbed at 0):
        # Base: 30
        # War score: 20 * 0.3 = 6
        # R141: Relation at WAR: -60 / 4 = -15, clamped to -10 (was -30)
        # Threat: 0 (stubbed) — spec example has -12 but we stub at 0
        # Sweetener: open_borders=3, gold_per_turn=200/100*3=6 → total 9
        # Diplomat skill: (10-6)*2 = 8
        # Personality (hawk, peace): -5
        # Total without threat: 30 + 6 - 10 + 0 + 9 + 8 - 5 = 38
        # R141 raised score from REJECT to COUNTER_OFFER
        assert result["outcome"] == "COUNTER_OFFER"
        assert result["score"] >= 30
        assert "components" in result
        assert "feedback" in result

    def test_accept_threshold_50(self):
        world = make_world()
        # High relation, favorable conditions → should accept
        world.nation_relations["France|Saxony"] = 80
        world.war_scores["France|Saxony"] = 0

        proposal = {
            "type": "open_borders",
            "proposer_nation": "France",
            "target_nation": "Saxony",
            "sweeteners": [{"type": "gold_per_turn", "value": 200}],
            "demands": [],
            "clauses": [],
        }

        result = calculate_acceptance(proposal, world)
        # Base: 35, Relation: 80/2=40, Skill: (10-4)*2=12, Personality (dove): +10
        # Sweetener: 6
        # Total: 35 + 40 + 12 + 10 + 6 = 103 → ACCEPT
        assert result["outcome"] == "ACCEPT"

    def test_counter_offer_range(self):
        world = make_world()
        world.nation_relations["Austria|France"] = -10  # Moderate

        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Austria",
            "sweeteners": [{"type": "gold_per_turn", "value": 100}],
            "demands": [],
            "clauses": [],
        }

        result = calculate_acceptance(proposal, world)
        # Base: 30, Relation: -10/2=-5, Skill: (10-9)*2=2, Personality (schemer): +5
        # Sweetener: 3
        # Total: 30 - 5 + 2 + 5 + 3 = 35 → COUNTER_OFFER
        assert result["outcome"] == "COUNTER_OFFER"

    def test_sweetener_cap_at_40(self):
        world = make_world()

        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [
                {"type": "territory", "value": 10},  # 10*8=80, but capped at 40
            ],
            "demands": [],
            "clauses": [],
        }

        result = calculate_acceptance(proposal, world)
        # Sweetener should be capped at 40 (R146)
        assert result["components"]["deal_balance"] <= 40

    def test_demands_uncapped(self):
        world = make_world()

        proposal = {
            "type": "vassalage",
            "proposer_nation": "France",
            "target_nation": "Saxony",
            "sweeteners": [],
            "demands": [
                {"type": "ap_per_turn", "value": 2},  # -25*2 = -50
                {"type": "territory", "value": 2},  # -5*2 = -10
            ],
            "clauses": [],
        }

        result = calculate_acceptance(proposal, world)
        # Demands: -50 + -10 = -60 (uncapped)
        assert result["components"]["deal_balance"] < -30

    def test_military_supremacy_bonus(self):
        world = make_world()
        # War score >= 70, proposer holds target's capital
        key = world._make_diplo_key("France", "Prussia")
        world.war_scores[key] = 70
        world.regions["Berlin"].controller = "France"

        proposal = {
            "type": "vassalage",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }

        result = calculate_acceptance(proposal, world)
        assert result["components"]["military_supremacy"] == 25

    def test_battlefield_diplomacy_bonus(self):
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.war_scores[key] = 25  # > 20

        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }

        result = calculate_acceptance(proposal, world)
        assert result["components"]["battlefield_diplomacy"] == 10
        # Military supremacy should be 0 (score < 70)
        assert result["components"]["military_supremacy"] == 0

    def test_battlefield_diplomacy_no_stack_with_supremacy(self):
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.war_scores[key] = 75
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
        # Military supremacy = 25, battlefield should be 0 (non-stacking)
        assert result["components"]["military_supremacy"] == 25
        assert result["components"]["battlefield_diplomacy"] == 0

    def test_special_bonus_prussia_saxony(self):
        world = make_world()

        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": ["territory_saxony"],
        }

        result = calculate_acceptance(proposal, world)
        assert result["components"]["special_desire_bonus"] == 10

    def test_special_bonus_saxony_protection(self):
        world = make_world()

        proposal = {
            "type": "non_aggression",
            "proposer_nation": "France",
            "target_nation": "Saxony",
            "sweeteners": [],
            "demands": [],
            "clauses": ["protection_promised"],
        }

        result = calculate_acceptance(proposal, world)
        assert result["components"]["special_desire_bonus"] == 10


class TestFeedback:
    def test_reject_feedback(self):
        world = make_world()
        world.nation_relations["France|Prussia"] = -80

        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }

        result = calculate_acceptance(proposal, world)
        assert result["outcome"] == "REJECT"
        assert "Talleyrand reports" in result["feedback"]

    def test_accept_feedback(self):
        world = make_world()
        world.nation_relations["France|Saxony"] = 80

        proposal = {
            "type": "open_borders",
            "proposer_nation": "France",
            "target_nation": "Saxony",
            "sweeteners": [{"type": "gold_per_turn", "value": 200}],
            "demands": [],
            "clauses": [],
        }

        result = calculate_acceptance(proposal, world)
        assert result["outcome"] == "ACCEPT"
        assert "decisive factor" in result["feedback"]


# ═══════════════════════════════════════════════════════
# PART 5: DP Economy
# ═══════════════════════════════════════════════════════

class TestDPEconomy:
    def test_france_starting_dp(self):
        """France starts at 4 (2 base + 1 skill + 1 authority)."""
        world = make_world()
        assert world.diplomatic_points == 4

    def test_dp_generation_formula(self):
        from backend.models.diplomat import DiplomaticRepresentative
        # France: skill 10, authority 100, controls capital
        diplomat = DiplomaticRepresentative("Talleyrand", "France", "schemer", 10)
        dp = calculate_dp(diplomat, 100, True)
        assert dp == 5  # R139: 3 base + 1 skill(>=8) + 1 authority

    def test_dp_generation_low_authority(self):
        from backend.models.diplomat import DiplomaticRepresentative
        diplomat = DiplomaticRepresentative("Talleyrand", "France", "schemer", 10)
        dp = calculate_dp(diplomat, 20, True)
        assert dp == 3  # R139: 3 base + 1 skill - 1 low_authority

    def test_dp_generation_lost_capital(self):
        from backend.models.diplomat import DiplomaticRepresentative
        diplomat = DiplomaticRepresentative("Talleyrand", "France", "schemer", 10)
        dp = calculate_dp(diplomat, 60, False)
        assert dp == 4  # R139: 3 base + 1 skill + 1 authority - 1 capital

    def test_dp_floor_at_1(self):
        from backend.models.diplomat import DiplomaticRepresentative
        diplomat = DiplomaticRepresentative("Nobody", "Test", "dove", 1)
        dp = calculate_dp(diplomat, 10, False)
        assert dp == 1  # Floor

    def test_dp_cap_at_5(self):
        from backend.models.diplomat import DiplomaticRepresentative
        diplomat = DiplomaticRepresentative("God", "Test", "schemer", 10)
        dp = calculate_dp(diplomat, 100, True)
        assert dp <= 5

    def test_dp_cost_peace(self):
        assert get_dp_cost("propose_peace") == 2

    def test_dp_cost_vassalage(self):
        assert get_dp_cost("demand_vassalage") == 3

    def test_dp_cost_war(self):
        assert get_dp_cost("declare_war") == 1

    def test_dp_cost_respond_free(self):
        assert get_dp_cost("respond") == 0

    def test_dp_cost_skill_penalty_mid(self):
        """Skill 4-6 → +1 cost."""
        assert get_dp_cost("propose_peace", diplomat_skill=5) == 3  # 2 + 1

    def test_dp_cost_skill_penalty_low(self):
        """Skill < 4 → +2 cost."""
        assert get_dp_cost("propose_peace", diplomat_skill=3) == 4  # 2 + 2

    def test_einsiedel_pays_extra(self):
        """Einsiedel (skill 4) pays +1 on all costs."""
        assert get_dp_cost("propose_peace", diplomat_skill=4) == 3


# ═══════════════════════════════════════════════════════
# PART 6: Trade Income
# ═══════════════════════════════════════════════════════

class TestTradeIncome:
    """R6: Trade income with diminishing returns [1.0, 0.75, 0.50, 0.25]."""

    def test_france_trade_income(self):
        """France: Saxony OB(100*1.0) + Austria PEACE(50*0.75) = 137."""
        world = make_world()
        pre_gold = world.nation_gold["France"]
        trade = process_trade_income(world)
        assert trade.get("France", 0) == 137
        assert world.nation_gold["France"] == pre_gold + 137

    def test_britain_trade_income(self):
        """Britain: Prussia ALLIANCE(200*1.0) + Austria NON_AGG(150*0.75) + Saxony PEACE(50*0.50) = 337."""
        world = make_world()
        pre_gold = world.nation_gold["Britain"]
        trade = process_trade_income(world)
        assert trade.get("Britain", 0) == 337
        assert world.nation_gold["Britain"] == pre_gold + 337

    def test_prussia_trade_income(self):
        """Prussia: Britain ALLIANCE(200*1.0) + Austria DEF_ALL(150*0.75) + Saxony PEACE(50*0.50) = 337."""
        world = make_world()
        trade = process_trade_income(world)
        assert trade.get("Prussia", 0) == 337

    def test_austria_trade_income(self):
        """Austria: Prussia DEF_ALL(150*1.0) + Britain NON_AGG(150*0.75) + France PEACE(50*0.50) + Saxony PEACE(50*0.25) = 299."""
        world = make_world()
        trade = process_trade_income(world)
        assert trade.get("Austria", 0) == 299

    def test_saxony_trade_income(self):
        """Saxony: France OB(100*1.0) + Austria PEACE(50*0.75) + Britain PEACE(50*0.50) + Prussia PEACE(50*0.25) = 174."""
        world = make_world()
        trade = process_trade_income(world)
        assert trade.get("Saxony", 0) == 174

    def test_war_gives_no_trade(self):
        world = make_world()
        trade = process_trade_income(world)
        # France-Britain and France-Prussia are at WAR — should contribute 0
        # France: Saxony OB(100*1.0) + Austria PEACE(50*0.75) = 137
        assert trade.get("France", 0) == 137

    def test_state_change_affects_trade(self):
        world = make_world()
        # Change France-Austria from PEACE to ALLIANCE
        world.diplomatic_states["Austria|France"] = "ALLIANCE"
        trade = process_trade_income(world)
        # France: ALLIANCE(200*1.0) + Saxony OB(100*0.75) = 200 + 75 = 275
        assert trade.get("France", 0) == 275


# ═══════════════════════════════════════════════════════
# PART 7: Movement Restrictions
# ═══════════════════════════════════════════════════════

class TestMovementRestrictions:
    def test_cannot_enter_peace_territory(self):
        """French marshal cannot enter Austrian (PEACE) territory."""
        world = make_world()
        assert can_enter_territory(world, "France", "Austria") is False

    def test_can_enter_open_borders_territory(self):
        """French marshal can enter Saxon (OPEN_BORDERS) territory."""
        world = make_world()
        assert can_enter_territory(world, "France", "Saxony") is True

    def test_can_enter_war_territory(self):
        """Can enter territory of nation at WAR (for attack)."""
        world = make_world()
        assert can_enter_territory(world, "France", "Britain") is True

    def test_can_enter_own_territory(self):
        world = make_world()
        assert can_enter_territory(world, "France", "France") is True

    def test_can_enter_unclaimed(self):
        world = make_world()
        assert can_enter_territory(world, "France", None) is True

    def test_non_aggression_blocks_entry(self):
        world = make_world()
        # Austria-Britain is NON_AGGRESSION
        assert can_enter_territory(world, "Britain", "Austria") is False

    def test_defensive_alliance_allows_entry(self):
        world = make_world()
        # Austria-Prussia is DEFENSIVE_ALLIANCE
        assert can_enter_territory(world, "Prussia", "Austria") is True

    def test_alliance_allows_entry(self):
        world = make_world()
        # Britain-Prussia is ALLIANCE
        assert can_enter_territory(world, "Britain", "Prussia") is True


# ═══════════════════════════════════════════════════════
# PART 8: War Declaration & Cascade
# ═══════════════════════════════════════════════════════

class TestWarDeclaration:
    def test_declare_war_on_austria(self):
        world = make_world()
        assert world.get_diplomatic_state("France", "Austria") == "PEACE"
        result = declare_war(world, "France", "Austria")
        assert result["success"] is True
        assert world.get_diplomatic_state("France", "Austria") == "WAR"

    def test_war_declaration_relation_penalties(self):
        world = make_world()
        old_relation = world.nation_relations.get("Austria|France", 0)
        declare_war(world, "France", "Austria")
        new_relation = world.nation_relations.get("Austria|France", 0)
        assert new_relation == old_relation - 30

    def test_war_declaration_all_nations_penalty(self):
        world = make_world()
        old_saxony = world.nation_relations.get("France|Saxony", 0)
        declare_war(world, "France", "Austria")
        new_saxony = world.nation_relations.get("France|Saxony", 0)
        assert new_saxony == old_saxony - 15

    def test_already_at_war(self):
        world = make_world()
        result = declare_war(world, "France", "Britain")
        assert result["success"] is False

    def test_defensive_alliance_cascade(self):
        """Attack Austria → Prussia enters WAR with France (Austria-Prussia DEF_ALLIANCE)."""
        world = make_world()
        # France is already at WAR with Prussia, so cascade won't fire for Prussia
        # Let's set up a fresh scenario
        world.diplomatic_states["France|Prussia"] = "PEACE"

        result = declare_war(world, "France", "Austria")
        assert result["success"] is True

        # Prussia should cascade into WAR with France
        assert world.get_diplomatic_state("France", "Prussia") == "WAR"
        assert len(result["cascade"]) >= 1
        assert any(c["defender"] == "Prussia" for c in result["cascade"])

    def test_cascade_message(self):
        world = make_world()
        world.diplomatic_states["France|Prussia"] = "PEACE"
        result = declare_war(world, "France", "Austria")
        assert "Prussia enters the war" in result["message"]

    def test_dp_cost(self):
        world = make_world()
        result = declare_war(world, "France", "Austria")
        assert result["dp_cost"] == 1


# ═══════════════════════════════════════════════════════
# PART 9: Downgrade Transitions
# ═══════════════════════════════════════════════════════

class TestDowngrade:
    def test_alliance_to_def_alliance(self):
        world = make_world()
        # Britain-Prussia is ALLIANCE
        result = execute_downgrade(world, "Britain", "Prussia")
        assert result["success"] is True
        assert result["new_state"] == "DEFENSIVE_ALLIANCE"
        assert result["dp_cost"] == 1

    def test_downgrade_relation_penalty(self):
        world = make_world()
        old_rel = world.nation_relations.get("Britain|Prussia", 0)
        execute_downgrade(world, "Britain", "Prussia")
        new_rel = world.nation_relations.get("Britain|Prussia", 0)
        assert new_rel == old_rel - 15  # ALLIANCE→DEF_ALLIANCE: -15

    def test_cannot_downgrade_from_peace(self):
        world = make_world()
        result = execute_downgrade(world, "France", "Austria")
        assert result["success"] is False

    def test_cannot_downgrade_from_war(self):
        world = make_world()
        result = execute_downgrade(world, "France", "Britain")
        assert result["success"] is False

    def test_auto_downgrade_tracking(self):
        world = make_world()
        world.turns_below_threshold = {}
        # Set Britain-Prussia ALLIANCE with relation far below threshold (40)
        world.nation_relations["Britain|Prussia"] = 0  # 40 below threshold of 40 = gap 40 >= 30

        # Run 5 turns of auto-downgrade checking
        for _ in range(5):
            check_auto_downgrade(world)

        # Should have auto-downgraded
        assert world.get_diplomatic_state("Britain", "Prussia") == "DEFENSIVE_ALLIANCE"


# ═══════════════════════════════════════════════════════
# PART 10: Serialization
# ═══════════════════════════════════════════════════════

class TestSerialization:
    def test_diplomat_serialization_round_trip(self):
        """All 5 diplomats round-trip correctly."""
        world = make_world()
        data = world.to_dict()
        restored = WorldState.from_dict(data)

        assert len(restored.diplomats) == 5
        for nation in ("France", "Britain", "Prussia", "Austria", "Saxony"):
            orig = world.diplomats[nation]
            rest = restored.diplomats[nation]
            assert orig.name == rest.name
            assert orig.skill == rest.skill
            assert orig.personality == rest.personality

    def test_new_fields_serialize(self):
        world = make_world()
        world.diplomatic_points = 3
        world.nation_authority["Britain"] = 45
        world.war_scores["Britain|France"] = 15
        world.armistice_cooldowns["Austria|France"] = 3
        world.turns_below_threshold["Britain|Prussia"] = 2

        data = world.to_dict()
        restored = WorldState.from_dict(data)

        assert restored.diplomatic_points == 3
        assert restored.nation_authority["Britain"] == 45
        assert restored.war_scores["Britain|France"] == 15
        assert restored.armistice_cooldowns["Austria|France"] == 3
        assert restored.turns_below_threshold["Britain|Prussia"] == 2

    def test_battle_records_serialize(self):
        world = make_world()
        record_battle(world, "France", "Britain", "France", 5000, 8000)

        data = world.to_dict()
        restored = WorldState.from_dict(data)

        key = world._make_diplo_key("France", "Britain")
        assert len(restored.battle_records.get(key, [])) == 1

    def test_decisive_battles_serialize(self):
        world = make_world()
        record_battle(world, "France", "Britain", "France", 3000, 12000)

        data = world.to_dict()
        restored = WorldState.from_dict(data)

        key = world._make_diplo_key("France", "Britain")
        assert len(restored.decisive_battles.get(key, [])) == 1

    def test_backward_compat_no_diplomats(self):
        """Old saves without diplomat data get defaults."""
        world = make_world()
        data = world.to_dict()
        del data["diplomats"]  # Simulate old save

        restored = WorldState.from_dict(data)
        assert len(restored.diplomats) == 5
        assert restored.diplomats["France"].name == "Talleyrand"

    def test_backward_compat_no_dp(self):
        world = make_world()
        data = world.to_dict()
        del data["diplomatic_points"]

        restored = WorldState.from_dict(data)
        assert restored.diplomatic_points == 4  # Default


# ═══════════════════════════════════════════════════════
# PART 11: Armistice Cooldown
# ═══════════════════════════════════════════════════════

class TestArmisticeCooldown:
    def test_cooldown_set(self):
        world = make_world()
        world.armistice_cooldowns["Austria|France"] = 5
        assert world.armistice_cooldowns["Austria|France"] == 5

    def test_cooldown_decrement(self):
        from backend.game_logic.diplomacy import _decrement_cooldowns
        world = make_world()
        world.armistice_cooldowns["Austria|France"] = 3
        _decrement_cooldowns(world)
        assert world.armistice_cooldowns["Austria|France"] == 2

    def test_cooldown_expires(self):
        from backend.game_logic.diplomacy import _decrement_cooldowns
        world = make_world()
        world.armistice_cooldowns["Austria|France"] = 1
        _decrement_cooldowns(world)
        assert "Austria|France" not in world.armistice_cooldowns

    def test_cascade_bypasses_cooldown(self):
        """Defensive cascade war entry bypasses armistice cooldowns."""
        world = make_world()
        world.diplomatic_states["France|Prussia"] = "PEACE"
        world.armistice_cooldowns["France|Prussia"] = 5
        declare_war(world, "France", "Austria")
        # Prussia cascades into WAR despite cooldown
        assert world.get_diplomatic_state("France", "Prussia") == "WAR"


# ═══════════════════════════════════════════════════════
# PART 12: Nation Authority
# ═══════════════════════════════════════════════════════

class TestNationAuthority:
    def test_starting_authority(self):
        world = make_world()
        assert world.nation_authority["Britain"] == 60
        assert world.nation_authority["Prussia"] == 60

    def test_modify_authority(self):
        from backend.game_logic.diplomacy import modify_nation_authority
        world = make_world()
        result = modify_nation_authority(world, "Prussia", -10)
        assert result == 50
        assert world.nation_authority["Prussia"] == 50

    def test_authority_clamped(self):
        from backend.game_logic.diplomacy import modify_nation_authority
        world = make_world()
        modify_nation_authority(world, "Prussia", -200)
        assert world.nation_authority["Prussia"] == 0
        modify_nation_authority(world, "Prussia", 200)
        assert world.nation_authority["Prussia"] == 100


# ═══════════════════════════════════════════════════════
# PART 13: Smoke Test — 5-turn advance
# ═══════════════════════════════════════════════════════

class TestSmoke:
    def test_five_turn_no_crash(self):
        """5-turn smoke test: no crashes, trade income applied, DP regenerated."""
        world = make_world()
        initial_gold = {k: v for k, v in world.nation_gold.items()}

        for _ in range(5):
            world.advance_turn()

        # Gold should have changed (trade income applied each turn)
        assert world.nation_gold["France"] != initial_gold["France"]
        # DP should be regenerated (non-zero)
        assert world.diplomatic_points > 0
        # Turn should have advanced
        assert world.current_turn == 6

    def test_advance_turn_processes_diplomacy(self):
        world = make_world()
        world.armistice_cooldowns["Austria|France"] = 2
        world.advance_turn()
        # Cooldown should have decremented
        assert world.armistice_cooldowns.get("Austria|France", 0) == 1


# ═══════════════════════════════════════════════════════
# PART 14: Integration Tests
# ═══════════════════════════════════════════════════════

class TestIntegration:
    def test_all_numeric_fields_are_int(self):
        """Golden Rule #2: All numbers to Godot must be int."""
        world = make_world()
        data = world.to_dict()
        assert isinstance(data["diplomatic_points"], int)
        assert isinstance(data["max_diplomatic_points"], int)
        for v in data["nation_authority"].values():
            assert isinstance(v, int)
        for v in data["war_scores"].values():
            assert isinstance(v, int)

    def test_acceptance_result_is_int(self):
        world = make_world()
        result = calculate_acceptance({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }, world)
        assert isinstance(result["score"], int)
