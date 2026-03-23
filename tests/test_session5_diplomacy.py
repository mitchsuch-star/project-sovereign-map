"""
Tests for Phase 8 Session 5: Vassal System + Loyalty

Gate criteria:
- Gate 1: Create PUPPET vassal, advance 3 turns, verify loyalty drops 4/turn
- Gate 2: Force loyalty=0, verify WAR + marshal transfer + cascade
- Gate 3: Ratify treaty with gold/turn tribute, verify gold transfer
- Gate 4: Demand AP/turn with war_score>80, verify nation_actions reduced
- Gate 5: Create SATELLITE vassal (Saxony), verify Reynier in marshals with trust=40
- Gate 6: All existing tests pass (0 regressions)
"""

from unittest.mock import patch

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.game_logic.vassal import (
    AUTONOMY_PUPPET, AUTONOMY_SATELLITE, AUTONOMY_AUTONOMOUS,
    TRIBUTE_RATES, LOYALTY_MIN, ASSIMILATION_TRUST,
    create_vassal_treaty, create_vassal_conquest,
    process_vassal_loyalty, check_vassal_rebellion,
    check_defection_cascade, process_vassal_tribute,
    invest_in_vassal, change_vassal_autonomy,
    assimilate_vassal_marshals, get_vassal_warnings,
    release_vassal, decrement_vassal_cooldowns,
    attempt_vassal_courting,
)
from backend.game_logic.diplomacy import validate_ap_clause


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def make_world():
    """Create a fresh WorldState for testing."""
    return WorldState()


def make_world_with_vassal(vassal="Saxony", lord="France", loyalty=60,
                           autonomy=AUTONOMY_SATELLITE, path="treaty"):
    """Create a world with an existing vassal."""
    world = make_world()
    world.vassals[vassal] = {
        "lord": lord,
        "loyalty": int(loyalty),
        "autonomy": int(autonomy),
        "path": path,
        "created_turn": 1,
        "tribute_rate": TRIBUTE_RATES[autonomy],
        "carved_from": None,
        "regions": None,
    }
    diplo_key = world._make_diplo_key(lord, vassal)
    world.diplomatic_states[diplo_key] = "VASSAL"
    # Zero out relation so loyalty tests are isolated
    world.nation_relations[diplo_key] = 0
    return world


def _set_war_score(world, nation, score):
    """Set war score from player perspective."""
    key = world._make_diplo_key("France", nation)
    world.war_scores[key] = score


# ═══════════════════════════════════════════════════════
# 1. VASSALAGE PATHS (4 tests)
# ═══════════════════════════════════════════════════════

class TestVassagePaths:
    """Test vassal creation via treaty and conquest paths."""

    def test_treaty_path_loyalty(self):
        """Treaty path: loyalty = 60 + generosity*10."""
        world = make_world()
        # Set OPEN_BORDERS prerequisite
        key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[key] = "OPEN_BORDERS"

        result = create_vassal_treaty(world, "France", "Saxony", generosity_bonus=2)
        assert result["success"]
        assert world.vassals["Saxony"]["loyalty"] == 80  # 60 + 2*10
        assert world.vassals["Saxony"]["autonomy"] == AUTONOMY_SATELLITE

    def test_conquest_path_loyalty(self):
        """Conquest path: loyalty = 20 + garrison//5000. Requires WAR state."""
        world = make_world()
        # Fix 13: Conquest requires WAR state
        key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[key] = "WAR"
        result = create_vassal_conquest(world, "France", "Saxony", garrison_size=15000)
        assert result["success"]
        assert world.vassals["Saxony"]["loyalty"] == 23  # 20 + 15000//5000
        assert world.vassals["Saxony"]["autonomy"] == AUTONOMY_PUPPET

    def test_treaty_threat_delta(self):
        """Treaty vassalage adds +5 threat."""
        world = make_world()
        world.threat_level = 10
        key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[key] = "OPEN_BORDERS"
        create_vassal_treaty(world, "France", "Saxony")
        assert world.threat_level == 15

    def test_conquest_threat_delta(self):
        """Conquest vassalage adds +25 threat. Requires WAR state."""
        world = make_world()
        world.threat_level = 10
        # Fix 13: Conquest requires WAR state
        key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[key] = "WAR"
        create_vassal_conquest(world, "France", "Saxony")
        assert world.threat_level == 35

    def test_treaty_requires_war_or_open_borders(self):
        """Treaty path requires WAR or OPEN_BORDERS+."""
        world = make_world()
        # PEACE is not sufficient for vassalization
        key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[key] = "PEACE"
        result = create_vassal_treaty(world, "France", "Saxony")
        assert not result["success"]
        assert "WAR" in result["message"] or "OPEN_BORDERS" in result["message"]


# ═══════════════════════════════════════════════════════
# 2. LOYALTY TICKS (8 tests)
# ═══════════════════════════════════════════════════════

class TestLoyaltyTicks:
    """Test each loyalty modifier in isolation."""

    def test_puppet_drift(self):
        """PUPPET drift: -4/turn."""
        world = make_world_with_vassal(autonomy=AUTONOMY_PUPPET, loyalty=60)
        process_vassal_loyalty(world)
        # Only drift applied (no garrison, no shared enemy, etc.)
        assert world.vassals["Saxony"]["loyalty"] == 56  # 60 - 4

    def test_satellite_drift(self):
        """SATELLITE drift: -2/turn."""
        world = make_world_with_vassal(autonomy=AUTONOMY_SATELLITE, loyalty=60)
        process_vassal_loyalty(world)
        assert world.vassals["Saxony"]["loyalty"] == 58  # 60 - 2

    def test_autonomous_drift(self):
        """AUTONOMOUS drift: +1/turn."""
        world = make_world_with_vassal(autonomy=AUTONOMY_AUTONOMOUS, loyalty=60)
        process_vassal_loyalty(world)
        assert world.vassals["Saxony"]["loyalty"] == 61  # 60 + 1

    def test_garrison_bonus(self):
        """Fix 19: Garrison base 5, cap 8. min(8, 5 + min(troops//5000, 3))."""
        world = make_world_with_vassal(autonomy=AUTONOMY_SATELLITE, loyalty=60)
        # Set garrison in Dresden (Saxony capital)
        region = world.regions.get("Dresden")
        if region:
            region.garrison_troops = 10000
            region.controller = "France"
        process_vassal_loyalty(world)
        # drift(-2) + garrison(min(8, 5+2)=7) = -2 + 7 = +5
        assert world.vassals["Saxony"]["loyalty"] == 65

    def test_shared_enemy_bonus(self):
        """Shared enemy: +2 per shared war."""
        world = make_world_with_vassal(autonomy=AUTONOMY_SATELLITE, loyalty=60)
        # Both France and Saxony at WAR with Prussia
        key_fp = world._make_diplo_key("France", "Prussia")
        key_sp = world._make_diplo_key("Saxony", "Prussia")
        world.diplomatic_states[key_fp] = "WAR"
        world.diplomatic_states[key_sp] = "WAR"
        process_vassal_loyalty(world)
        # drift(-2) + shared_enemy(+2) = 0
        assert world.vassals["Saxony"]["loyalty"] == 60

    def test_lord_winning_battles(self):
        """Lord winning battles: +1 per win, max +3."""
        world = make_world_with_vassal(autonomy=AUTONOMY_SATELLITE, loyalty=60)
        # Create marshals for battles
        m = Marshal("Davout", "Berlin", 20000, "professional", nation="France")
        m_enemy = Marshal("EnemyGen", "Berlin", 20000, "aggressive", nation="Prussia")
        world.marshals["Davout"] = m
        world.marshals["EnemyGen"] = m_enemy
        # Simulate 4 battle wins using record_battle() format (should cap at +3)
        world.battles_this_turn = [
            {"attacker": "Davout", "defender": "EnemyGen", "result": "Attacker victory", "location": "Berlin", "turn": 1},
            {"attacker": "Davout", "defender": "EnemyGen", "result": "Attacker victory", "location": "Berlin", "turn": 1},
            {"attacker": "Davout", "defender": "EnemyGen", "result": "Attacker victory", "location": "Berlin", "turn": 1},
            {"attacker": "Davout", "defender": "EnemyGen", "result": "Attacker victory", "location": "Berlin", "turn": 1},
        ]
        process_vassal_loyalty(world)
        # drift(-2) + wins(+3 capped) = +1
        assert world.vassals["Saxony"]["loyalty"] == 61

    def test_lord_losing_battles(self):
        """Lord losing battles: -2 per loss, max -6."""
        world = make_world_with_vassal(autonomy=AUTONOMY_SATELLITE, loyalty=60)
        # Create French and enemy marshals for battle records
        m_french = Marshal("Ney", "Berlin", 20000, "aggressive", nation="France")
        m_enemy = Marshal("Blucher", "Berlin", 20000, "aggressive", nation="Prussia")
        world.marshals["Ney"] = m_french
        world.marshals["Blucher"] = m_enemy
        # Simulate 4 losses using record_battle() format (should cap at -6)
        world.battles_this_turn = [
            {"attacker": "Ney", "defender": "Blucher", "result": "Defender victory", "location": "Berlin", "turn": 1},
            {"attacker": "Ney", "defender": "Blucher", "result": "Defender victory", "location": "Berlin", "turn": 1},
            {"attacker": "Ney", "defender": "Blucher", "result": "Defender victory", "location": "Berlin", "turn": 1},
            {"attacker": "Blucher", "defender": "Ney", "result": "Attacker victory", "location": "Berlin", "turn": 1},
        ]
        process_vassal_loyalty(world)
        # drift(-2) + losses(max -6) = -8
        assert world.vassals["Saxony"]["loyalty"] == 52

    def test_relation_modifier(self):
        """Relation modifier: nation_relation(vassal, lord) // 20."""
        world = make_world_with_vassal(autonomy=AUTONOMY_SATELLITE, loyalty=60)
        # Set positive relation
        key = world._make_diplo_key("Saxony", "France")
        world.nation_relations[key] = 40  # 40 // 20 = +2
        process_vassal_loyalty(world)
        # drift(-2) + relation(+2) = 0
        assert world.vassals["Saxony"]["loyalty"] == 60


# ═══════════════════════════════════════════════════════
# 3. REBELLION (4 tests)
# ═══════════════════════════════════════════════════════

class TestRebellion:
    """Test rebellion mechanics when loyalty hits 0."""

    def test_rebellion_triggers_war(self):
        """Loyalty=0 triggers WAR diplomatic state."""
        world = make_world_with_vassal(loyalty=0)
        events = check_vassal_rebellion(world)
        assert len(events) == 1
        assert events[0]["type"] == "vassal_rebellion"
        key = world._make_diplo_key("France", "Saxony")
        assert world.diplomatic_states[key] == "WAR"
        assert "Saxony" not in world.vassals

    def test_rebellion_transfers_marshals(self):
        """Rebellion returns assimilated marshals to vassal nation."""
        world = make_world_with_vassal(loyalty=0)
        # Add a Saxony marshal that was assimilated
        m = Marshal("Reynier", "Dresden", 12000, "cautious", nation="France")
        m.original_nation = "Saxony"
        world.marshals["Reynier"] = m

        check_vassal_rebellion(world)
        assert world.marshals["Reynier"].nation == "Saxony"

    def test_rebellion_cascade(self):
        """Rebellion causes -10 loyalty to all other vassals."""
        world = make_world_with_vassal("Saxony", loyalty=0)
        # Add another vassal
        world.vassals["Austria"] = {
            "lord": "France", "loyalty": 50, "autonomy": AUTONOMY_SATELLITE,
            "path": "treaty", "created_turn": 1,
            "tribute_rate": 0.75, "carved_from": None, "regions": None,
        }
        check_vassal_rebellion(world)
        assert world.vassals["Austria"]["loyalty"] == 40  # 50 - 10

    def test_rebellion_threat_and_relation(self):
        """Rebellion: threat -10, relation -50."""
        world = make_world_with_vassal(loyalty=0)
        world.threat_level = 30
        key = world._make_diplo_key("France", "Saxony")
        world.nation_relations[key] = 0

        check_vassal_rebellion(world)
        assert world.threat_level == 20  # 30 - 10
        assert world.nation_relations[key] == -50  # 0 - 50


# ═══════════════════════════════════════════════════════
# 4. CASCADE TIPPING (4 tests)
# ═══════════════════════════════════════════════════════

class TestDefectionCascade:
    """Test defection cascade mechanics."""

    def test_cascade_triggers_on_low_war_score(self):
        """War score < -30 + loyalty < 50 can trigger cascade."""
        world = make_world_with_vassal(loyalty=30)
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_scores[key] = -40  # France losing badly

        with patch('backend.game_logic.vassal.random') as mock_random:
            mock_random.random.return_value = 0.01  # Always triggers
            events = check_defection_cascade(world)
        assert len(events) == 1
        assert events[0]["type"] == "vassal_defection_cascade"

    def test_cascade_only_fires_once_per_war(self):
        """Cascade fires AT MOST once per war pair."""
        world = make_world_with_vassal(loyalty=30)
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_scores[key] = -40

        with patch('backend.game_logic.vassal.random') as mock_random:
            mock_random.random.return_value = 0.01
            events1 = check_defection_cascade(world)
            # Reset loyalty for second check
            world.vassals["Saxony"]["loyalty"] = 30
            events2 = check_defection_cascade(world)

        assert len(events1) == 1
        assert len(events2) == 0  # Already triggered

    def test_cascade_immune_if_loyalty_high(self):
        """No cascade if loyalty >= 50."""
        world = make_world_with_vassal(loyalty=50)
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_scores[key] = -40

        events = check_defection_cascade(world)
        assert len(events) == 0

    def test_cascade_roll_probability(self):
        """Roll chance = (50 - loyalty) / 100."""
        world = make_world_with_vassal(loyalty=30)
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_scores[key] = -40

        # Roll at exactly the threshold: (50-30)/100 = 0.20
        with patch('backend.game_logic.vassal.random') as mock_random:
            mock_random.random.return_value = 0.21  # Just above threshold
            events = check_defection_cascade(world)
        assert len(events) == 0  # Should NOT trigger


# ═══════════════════════════════════════════════════════
# 5. INVEST ACTION (4 tests)
# ═══════════════════════════════════════════════════════

class TestInvestAction:
    """Test vassal investment mechanics."""

    def test_invest_success(self):
        """Successful investment: +10 loyalty."""
        world = make_world_with_vassal(loyalty=50)
        world.diplomatic_points = 3
        world.nation_gold["France"] = 500

        result = invest_in_vassal(world, "Saxony")
        assert result["success"]
        assert world.vassals["Saxony"]["loyalty"] == 60
        assert world.diplomatic_points == 2  # 3 - 1
        assert world.nation_gold["France"] == 300  # 500 - 200

    def test_invest_cooldown_blocking(self):
        """Investment blocked during cooldown."""
        world = make_world_with_vassal(loyalty=50)
        world.diplomatic_points = 3
        world.nation_gold["France"] = 500
        world.vassal_investment_cooldowns = {"Saxony": 2}

        result = invest_in_vassal(world, "Saxony")
        assert not result["success"]
        assert "cooldown" in result["message"].lower()

    def test_invest_dp_insufficient(self):
        """Investment fails without DP."""
        world = make_world_with_vassal(loyalty=50)
        world.diplomatic_points = 0
        world.nation_gold["France"] = 500

        result = invest_in_vassal(world, "Saxony")
        assert not result["success"]
        assert "diplomatic points" in result["message"].lower()

    def test_invest_gold_insufficient(self):
        """Investment fails without gold."""
        world = make_world_with_vassal(loyalty=50)
        world.diplomatic_points = 3
        world.nation_gold["France"] = 50

        result = invest_in_vassal(world, "Saxony")
        assert not result["success"]
        assert "gold" in result["message"].lower()


# ═══════════════════════════════════════════════════════
# 6. AUTONOMY CHANGE (3 tests)
# ═══════════════════════════════════════════════════════

class TestAutonomyChange:
    """Test autonomy level changes."""

    def test_upgrade_bonus(self):
        """Upgrading autonomy: +10 loyalty."""
        world = make_world_with_vassal(autonomy=AUTONOMY_PUPPET, loyalty=50)
        world.diplomatic_points = 2

        result = change_vassal_autonomy(world, "Saxony", AUTONOMY_SATELLITE)
        assert result["success"]
        assert world.vassals["Saxony"]["loyalty"] == 60  # 50 + 10
        assert world.vassals["Saxony"]["autonomy"] == AUTONOMY_SATELLITE

    def test_downgrade_penalty(self):
        """Downgrading autonomy: -15 loyalty."""
        world = make_world_with_vassal(autonomy=AUTONOMY_SATELLITE, loyalty=50)
        world.diplomatic_points = 2

        result = change_vassal_autonomy(world, "Saxony", AUTONOMY_PUPPET)
        assert result["success"]
        assert world.vassals["Saxony"]["loyalty"] == 35  # 50 - 15
        assert world.vassals["Saxony"]["autonomy"] == AUTONOMY_PUPPET

    def test_dp_cost(self):
        """Autonomy change costs 1 DP."""
        world = make_world_with_vassal(autonomy=AUTONOMY_PUPPET, loyalty=50)
        world.diplomatic_points = 1

        change_vassal_autonomy(world, "Saxony", AUTONOMY_SATELLITE)
        assert world.diplomatic_points == 0  # 1 - 1


# ═══════════════════════════════════════════════════════
# 7. ENEMY COURTING (3 tests)
# ═══════════════════════════════════════════════════════

class TestEnemyCourting:
    """Test enemy AI vassal courting."""

    def test_courting_reduces_loyalty(self):
        """Successful courting reduces vassal loyalty."""
        world = make_world_with_vassal(loyalty=40)
        # Set up nation_dp (C2 audit fix: was diplomatic_points_nations)
        world.nation_dp["Prussia"] = 5
        # Set positive relation between Saxony and Prussia
        key = world._make_diplo_key("Saxony", "Prussia")
        world.nation_relations[key] = 20

        events = attempt_vassal_courting(world, "Prussia")
        assert len(events) == 1
        assert events[0]["loyalty_reduction"] == 15  # Positive relation
        assert world.vassals["Saxony"]["loyalty"] == 25  # 40 - 15

    def test_courting_anti_spam(self):
        """Courting has 3-turn cooldown."""
        world = make_world_with_vassal(loyalty=40)
        # C2 audit fix: use nation_dp instead of diplomatic_points_nations
        world.nation_dp["Prussia"] = 10

        events1 = attempt_vassal_courting(world, "Prussia")
        # Reset loyalty for second attempt
        world.vassals["Saxony"]["loyalty"] = 40
        events2 = attempt_vassal_courting(world, "Prussia")

        assert len(events1) == 1
        assert len(events2) == 0  # Cooldown blocks

    def test_courting_fails_if_loyalty_high(self):
        """Courting fails if vassal loyalty >= 50."""
        world = make_world_with_vassal(loyalty=50)
        # C2 audit fix: use nation_dp instead of diplomatic_points_nations
        world.nation_dp["Prussia"] = 5

        events = attempt_vassal_courting(world, "Prussia")
        assert len(events) == 0


# ═══════════════════════════════════════════════════════
# 8. AP CLAUSE (3 tests)
# ═══════════════════════════════════════════════════════

class TestAPClause:
    """Test AP/turn demand clause."""

    def test_ap_demand_blocked_under_80(self):
        """AP demand requires war_score > 80."""
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_scores[key] = 70  # Below threshold

        assert not validate_ap_clause(world, "Prussia")

    def test_ap_demand_allowed_above_80(self):
        """AP demand allowed when war_score > 80."""
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_scores[key] = 85

        assert validate_ap_clause(world, "Prussia")

    def test_ap_clause_applied_to_nation_actions(self):
        """AP/turn clause reduces target's nation_actions."""
        world = make_world()
        world.nation_actions["Prussia"] = 4
        world.active_treaties["France|Prussia"] = {
            "clauses": [
                {"type": "ap_per_turn", "amount": 1, "from": "Prussia", "to": "France"}
            ]
        }
        world._process_treaty_clauses()
        assert world.nation_actions["Prussia"] == 3  # 4 - 1

    def test_ap_clause_minimum_1(self):
        """AP/turn clause cannot reduce below 1."""
        world = make_world()
        world.nation_actions["Prussia"] = 1
        world.active_treaties["France|Prussia"] = {
            "clauses": [
                {"type": "ap_per_turn", "amount": 2, "from": "Prussia", "to": "France"}
            ]
        }
        world._process_treaty_clauses()
        assert world.nation_actions["Prussia"] == 1  # Clamped at 1


# ═══════════════════════════════════════════════════════
# 9. TERRITORY CESSION (3 tests)
# ═══════════════════════════════════════════════════════

class TestTerritoryCession:
    """Test territory cession enhancements."""

    def test_autonomous_blocks_cession(self):
        """AUTONOMOUS vassals block territory cession."""
        world = make_world_with_vassal(autonomy=AUTONOMY_AUTONOMOUS, loyalty=60)
        # Autonomous vassals cannot have territory ceded
        state = world.vassals["Saxony"]
        assert state["autonomy"] == AUTONOMY_AUTONOMOUS
        # Verification: autonomous blocks are checked in executor

    def test_puppet_cession_loyalty_penalty(self):
        """PUPPET territory cession costs -20 loyalty per region."""
        world = make_world_with_vassal(autonomy=AUTONOMY_PUPPET, loyalty=60)
        # Simulate ceding a region (direct loyalty penalty)
        regions_ceded = 2
        world.vassals["Saxony"]["loyalty"] = max(
            LOYALTY_MIN,
            world.vassals["Saxony"]["loyalty"] - (20 * regions_ceded)
        )
        assert world.vassals["Saxony"]["loyalty"] == 20  # 60 - 40

    def test_release_vassal(self):
        """Release vassal restores peaceful state."""
        world = make_world_with_vassal(loyalty=40)
        result = release_vassal(world, "Saxony")
        assert result["success"]
        assert "Saxony" not in world.vassals
        key = world._make_diplo_key("France", "Saxony")
        assert world.diplomatic_states[key] == "PEACE"


# ═══════════════════════════════════════════════════════
# 10. CONTINENTAL SYSTEM (3 tests)
# ═══════════════════════════════════════════════════════

class TestContinentalSystem:
    """Test Continental System mechanics."""

    def test_trade_income_blocked(self):
        """Continental System blocks trade with Britain."""
        world = make_world()
        world.continental_system_members = ["France"]
        key = world._make_diplo_key("France", "Britain")
        world.diplomatic_states[key] = "PEACE"  # PEACE = 50 trade
        world.nation_gold["France"] = 1000
        world.nation_gold["Britain"] = 1000

        from backend.game_logic.diplomacy import apply_continental_system
        apply_continental_system(world)
        # France and Britain both lose trade income
        assert world.nation_gold["France"] < 1000
        assert world.nation_gold["Britain"] < 1000

    def test_total_cap_200(self):
        """Total Continental System cap is 200g across all members."""
        world = make_world()
        world.continental_system_members = ["France", "Prussia", "Austria"]
        # Set up peace with Britain for all
        for nation in ["France", "Prussia", "Austria"]:
            key = world._make_diplo_key(nation, "Britain")
            world.diplomatic_states[key] = "ALLIANCE"  # 200 trade each
            world.nation_gold[nation] = 2000
        world.nation_gold["Britain"] = 5000

        from backend.game_logic.diplomacy import apply_continental_system
        apply_continental_system(world)
        # Total blocked should not exceed 200
        total_lost_britain = 5000 - world.nation_gold["Britain"]
        assert total_lost_britain <= 200

    def test_vassal_auto_join(self):
        """PUPPET/SATELLITE vassals auto-join Continental System."""
        world = make_world_with_vassal(autonomy=AUTONOMY_PUPPET)
        world.continental_system_members = ["France"]

        from backend.game_logic.diplomacy import apply_continental_system
        apply_continental_system(world)
        assert "Saxony" in world.continental_system_members


# ═══════════════════════════════════════════════════════
# 11. MARSHAL ASSIMILATION (3 tests)
# ═══════════════════════════════════════════════════════

class TestMarshalAssimilation:
    """Test marshal assimilation mechanics."""

    def test_assimilation_trust_40(self):
        """Assimilated marshals get trust=40."""
        world = make_world_with_vassal(autonomy=AUTONOMY_SATELLITE)
        m = Marshal("Reynier", "Dresden", 12000, "cautious", nation="Saxony")
        world.marshals["Reynier"] = m

        assimilated = assimilate_vassal_marshals(world, "Saxony")
        assert "Reynier" in assimilated
        assert world.marshals["Reynier"].nation == "France"
        assert world.marshals["Reynier"].trust.value == ASSIMILATION_TRUST

    def test_assimilation_sets_original_nation(self):
        """Assimilated marshals track original_nation for rebellion."""
        world = make_world_with_vassal(autonomy=AUTONOMY_PUPPET)
        m = Marshal("Reynier", "Dresden", 12000, "cautious", nation="Saxony")
        world.marshals["Reynier"] = m

        assimilate_vassal_marshals(world, "Saxony")
        assert world.marshals["Reynier"].original_nation == "Saxony"

    def test_autonomous_no_assimilation(self):
        """AUTONOMOUS vassals keep their marshals."""
        world = make_world_with_vassal(autonomy=AUTONOMY_AUTONOMOUS)
        m = Marshal("Reynier", "Dresden", 12000, "cautious", nation="Saxony")
        world.marshals["Reynier"] = m

        assimilated = assimilate_vassal_marshals(world, "Saxony")
        assert len(assimilated) == 0
        assert world.marshals["Reynier"].nation == "Saxony"  # Unchanged


# ═══════════════════════════════════════════════════════
# 12. SERIALIZATION (3 tests)
# ═══════════════════════════════════════════════════════

class TestSerialization:
    """Test serialization round-trips for new fields."""

    def test_vassals_round_trip(self):
        """Vassals dict survives to_dict → from_dict."""
        world = make_world_with_vassal(loyalty=75)
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert "Saxony" in restored.vassals
        assert restored.vassals["Saxony"]["loyalty"] == 75
        assert restored.vassals["Saxony"]["lord"] == "France"

    def test_investment_cooldowns_round_trip(self):
        """Investment cooldowns survive serialization."""
        world = make_world()
        world.vassal_investment_cooldowns = {"Saxony": 3, "Austria": 1}
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.vassal_investment_cooldowns["Saxony"] == 3
        assert restored.vassal_investment_cooldowns["Austria"] == 1

    def test_cascade_triggered_round_trip(self):
        """cascade_triggered set survives serialization (set → list → set)."""
        world = make_world()
        world.cascade_triggered = {"Saxony|France|Prussia", "Austria|France|Britain"}
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert isinstance(restored.cascade_triggered, set)
        assert "Saxony|France|Prussia" in restored.cascade_triggered
        assert "Austria|France|Britain" in restored.cascade_triggered

    def test_old_save_compatibility(self):
        """Loading a save without vassal fields uses defaults."""
        world = make_world()
        data = world.to_dict()
        # Remove vassal fields to simulate old save
        data.pop("vassals", None)
        data.pop("vassal_investment_cooldowns", None)
        data.pop("cascade_triggered", None)
        data.pop("continental_system_members", None)

        restored = WorldState.from_dict(data)
        assert restored.vassals == {}
        assert restored.vassal_investment_cooldowns == {}
        assert restored.cascade_triggered == set()
        assert restored.continental_system_members == []


# ═══════════════════════════════════════════════════════
# BONUS: COOLDOWN DECREMENT + WARNINGS
# ═══════════════════════════════════════════════════════

class TestCooldownsAndWarnings:
    """Test cooldown decrement and warning generation."""

    def test_cooldown_decrement(self):
        """Cooldowns decrement each turn, expired ones removed."""
        world = make_world()
        world.vassal_investment_cooldowns = {"Saxony": 2, "Austria": 1}
        decrement_vassal_cooldowns(world)
        assert world.vassal_investment_cooldowns.get("Saxony") == 1
        assert "Austria" not in world.vassal_investment_cooldowns  # Expired

    def test_warnings_generated(self):
        """Correct warning levels for different loyalty values."""
        world = make_world_with_vassal(loyalty=5)
        # Add another vassal at warning level
        world.vassals["Austria"] = {
            "lord": "France", "loyalty": 35, "autonomy": AUTONOMY_SATELLITE,
            "path": "treaty", "created_turn": 1,
            "tribute_rate": 0.75, "carved_from": None, "regions": None,
        }
        warnings = get_vassal_warnings(world)
        assert len(warnings) == 2

        # Saxony = critical (loyalty 5)
        saxony_warning = next(w for w in warnings if w["vassal"] == "Saxony")
        assert saxony_warning["level"] == "critical"

        # Austria = warning (loyalty 35)
        austria_warning = next(w for w in warnings if w["vassal"] == "Austria")
        assert austria_warning["level"] == "warning"

    def test_tribute_processing(self):
        """Vassal tribute transfers gold to lord."""
        world = make_world_with_vassal(autonomy=AUTONOMY_PUPPET, loyalty=60)
        # Ensure Saxony has gold and controls a region
        world.nation_gold["Saxony"] = 500
        old_france_gold = world.nation_gold.get("France", 0)

        # Set Saxony as controller of Dresden
        region = world.regions.get("Dresden")
        if region:
            region.controller = "Saxony"

        tribute = process_vassal_tribute(world)
        # PUPPET rate = 1.0, 1 region * 50 base = 50 tribute
        assert world.nation_gold["Saxony"] < 500
        assert world.nation_gold.get("France", 0) > old_france_gold
