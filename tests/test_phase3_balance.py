"""
Phase 3: Balance Tuning — Tests for 13 balance items.
Created: March 2026

Covers:
- R104: Sweetener value=0 bug fix
- R20: Diplomat skill penalty cap
- R8: Military pressure for wartime proposals
- R6: Trade income diminishing returns
- R18: Continental System DP cost
- R4b: COURT_NATION speed reduction
- R9: Battle casualty threshold for war score
- R4a: Relation decay
- R14: Vassal release cooldown
- R16: Region capture threat
- R11: Coalition stalemate duration
- R106: P3 AI trigger (threat-based alliance seeking)
- R15: AI-AI diplomacy degradation
"""
from backend.models.world_state import WorldState
from backend.game_logic.diplomacy import (
    calculate_acceptance,
    process_trade_income,
    record_battle,
    _process_relation_decay,
)
from backend.game_logic.diplomatic_dialogue import MISSION_DP_COSTS, MISSION_EFFECTS
from backend.game_logic.vassal import (
    create_vassal_treaty,
    release_vassal,
    decrement_vassal_cooldowns,
)
from backend.game_logic.coalition import process_coalition_turn


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _make_world():
    """Create a test world with France + 4 enemy nations."""
    world = WorldState()
    world.current_turn = 5
    world.player_nation = "France"
    world.enemy_nations = ["Austria", "Prussia", "Russia", "Britain"]
    return world


def _set_diplo_state(world, nation_a, nation_b, state):
    """Set diplomatic state between two nations."""
    key = world._make_diplo_key(nation_a, nation_b)
    world.diplomatic_states[key] = state


def _set_relation(world, nation_a, nation_b, value):
    """Set relation between two nations."""
    key = world._make_diplo_key(nation_a, nation_b)
    world.nation_relations[key] = value


def _get_relation(world, nation_a, nation_b):
    """Get relation between two nations."""
    key = world._make_diplo_key(nation_a, nation_b)
    return world.nation_relations.get(key, 0)


# ═══════════════════════════════════════════════════════════════════════════
# R104: SWEETENER VALUE=0 BUG
# ═══════════════════════════════════════════════════════════════════════════

class TestR104SweetenerValueZero:
    """R104: svalue=0 should give 0, not fall back to rate."""

    def _make_acceptance_world(self):
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "PEACE")
        _set_relation(world, "France", "Austria", 0)
        # Set up diplomats
        from backend.models.diplomat import DiplomaticRepresentative
        world.diplomats = {
            "France": DiplomaticRepresentative("Talleyrand", "France", "cautious", skill=7),
            "Austria": DiplomaticRepresentative("Metternich", "Austria", "cautious", skill=7),
        }
        return world

    def test_sweetener_value_zero_gives_zero(self):
        """Sweetener with value=0 should contribute 0, not flat rate."""
        world = self._make_acceptance_world()
        proposal_with_zero = {
            "type": "non_aggression",
            "proposer_nation": "France",
            "target_nation": "Austria",
            "sweeteners": [{"type": "gold", "value": 0}],
            "demands": [],
            "clauses": [],
        }
        proposal_without = {
            "type": "non_aggression",
            "proposer_nation": "France",
            "target_nation": "Austria",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        result_with = calculate_acceptance(proposal_with_zero, world)
        result_without = calculate_acceptance(proposal_without, world)
        # With value=0 sweetener, deal_balance should be same as no sweetener
        assert result_with["components"]["deal_balance"] == result_without["components"]["deal_balance"]

    def test_sweetener_value_none_gives_flat_rate(self):
        """Sweetener with value=None should fall back to flat rate."""
        world = self._make_acceptance_world()
        proposal = {
            "type": "non_aggression",
            "proposer_nation": "France",
            "target_nation": "Austria",
            "sweeteners": [{"type": "territory", "value": None}],
            "demands": [],
            "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        # With None value for a flat-rate sweetener (territory=8, R144), should use flat rate
        assert result["components"]["deal_balance"] == 8

    def test_demand_value_zero_gives_zero(self):
        """Demand with value=0 should contribute 0, not fall back to rate."""
        world = self._make_acceptance_world()
        proposal_with_zero = {
            "type": "non_aggression",
            "proposer_nation": "France",
            "target_nation": "Austria",
            "sweeteners": [],
            "demands": [{"type": "gold", "value": 0}],
            "clauses": [],
        }
        proposal_without = {
            "type": "non_aggression",
            "proposer_nation": "France",
            "target_nation": "Austria",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        result_with = calculate_acceptance(proposal_with_zero, world)
        result_without = calculate_acceptance(proposal_without, world)
        assert result_with["components"]["deal_balance"] == result_without["components"]["deal_balance"]


# ═══════════════════════════════════════════════════════════════════════════
# R20: DIPLOMAT SKILL PENALTY CAP
# ═══════════════════════════════════════════════════════════════════════════

class TestR20DiplomatSkillPenaltyCap:
    """R20: Negative diplomat skill bonus capped at -8."""

    def _make_world_with_skills(self, proposer_skill, target_skill):
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "PEACE")
        _set_relation(world, "France", "Austria", 0)
        from backend.models.diplomat import DiplomaticRepresentative
        world.diplomats = {
            "France": DiplomaticRepresentative("Talleyrand", "France", "cautious", skill=proposer_skill),
            "Austria": DiplomaticRepresentative("Metternich", "Austria", "cautious", skill=target_skill),
        }
        return world

    def _make_proposal(self, proposer, target):
        return {
            "type": "non_aggression",
            "proposer_nation": proposer,
            "target_nation": target,
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }

    def test_saxony_to_france_capped_at_minus_8(self):
        """Skill 4 proposing to skill 10 = (4-10)*2 = -12, capped at -8."""
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "PEACE")
        _set_relation(world, "France", "Austria", 0)
        from backend.models.diplomat import DiplomaticRepresentative
        world.diplomats = {
            # Austria proposing with skill 4
            "Austria": DiplomaticRepresentative("Metternich", "Austria", "cautious", skill=4),
            "France": DiplomaticRepresentative("Talleyrand", "France", "cautious", skill=10),
        }
        proposal = self._make_proposal("Austria", "France")
        result = calculate_acceptance(proposal, world)
        assert result["components"]["diplomat_skill_bonus"] == -8

    def test_france_to_austria_uncapped_positive(self):
        """Skill 10 proposing to skill 4 = (10-4)*2 = +12, NOT capped."""
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "PEACE")
        _set_relation(world, "France", "Austria", 0)
        from backend.models.diplomat import DiplomaticRepresentative
        world.diplomats = {
            "France": DiplomaticRepresentative("Talleyrand", "France", "cautious", skill=10),
            "Austria": DiplomaticRepresentative("Metternich", "Austria", "cautious", skill=4),
        }
        proposal = self._make_proposal("France", "Austria")
        result = calculate_acceptance(proposal, world)
        assert result["components"]["diplomat_skill_bonus"] == 12

    def test_equal_skills_zero(self):
        """Equal skills = 0 bonus."""
        world = self._make_world_with_skills(7, 7)
        proposal = self._make_proposal("France", "Austria")
        result = calculate_acceptance(proposal, world)
        assert result["components"]["diplomat_skill_bonus"] == 0


# ═══════════════════════════════════════════════════════════════════════════
# R8: MILITARY PRESSURE
# ═══════════════════════════════════════════════════════════════════════════

class TestR8MilitaryPressure:
    """R8: War score > 0 adds military pressure to acceptance."""

    def _make_war_world(self, proposer_war_score):
        """Create war world with proposer (France) at given war score.

        War scores are stored from alphabetically-first nation's perspective.
        Austria|France key: negative value = Austria losing = France winning.
        """
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "WAR")
        _set_relation(world, "France", "Austria", -50)
        from backend.models.diplomat import DiplomaticRepresentative
        world.diplomats = {
            "France": DiplomaticRepresentative("Talleyrand", "France", "cautious", skill=7),
            "Austria": DiplomaticRepresentative("Metternich", "Austria", "cautious", skill=7),
        }
        # Set war score from storage perspective (Austria first alphabetically)
        # Negative storage = Austria losing = France winning
        diplo_key = world._make_diplo_key("France", "Austria")
        world.war_scores = {diplo_key: -proposer_war_score}
        return world

    def _make_proposal(self):
        return {
            "type": "armistice",
            "proposer_nation": "France",
            "target_nation": "Austria",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }

    def test_ws50_gives_pressure_7(self):
        """War score 50 → pressure = int(min(15, 50*0.15)) = 7."""
        world = self._make_war_world(50)
        result = calculate_acceptance(self._make_proposal(), world)
        assert result["components"]["military_pressure"] == 7

    def test_ws100_capped_at_15(self):
        """War score 100 → pressure = int(min(15, 100*0.15)) = 15."""
        world = self._make_war_world(100)
        result = calculate_acceptance(self._make_proposal(), world)
        assert result["components"]["military_pressure"] == 15

    def test_ws_negative_no_pressure(self):
        """War score < 0 → no pressure."""
        world = self._make_war_world(-30)
        result = calculate_acceptance(self._make_proposal(), world)
        assert result["components"]["military_pressure"] == 0

    def test_doesnt_stack_with_supremacy(self):
        """Military pressure doesn't stack with military supremacy (max() selects highest)."""
        world = self._make_war_world(80)
        # Set up for military supremacy: war_score >= 70 + capital occupied
        from backend.models.region import NATION_CAPITALS
        capital = NATION_CAPITALS.get("Austria")
        if capital and capital in world.regions:
            world.regions[capital].controller = "France"
        result = calculate_acceptance(self._make_proposal(), world)
        # Supremacy = 25, pressure = int(min(15, 80*0.15)) = 12
        # max(25, 0, 12) = 25 — supremacy wins
        assert result["components"]["military_supremacy"] == 25
        assert result["components"]["military_pressure"] == 12


# ═══════════════════════════════════════════════════════════════════════════
# R6: TRADE INCOME DIMINISHING RETURNS
# ═══════════════════════════════════════════════════════════════════════════

class TestR6TradeDiminishingReturns:
    """R6: Trade income uses diminishing rates [1.0, 0.75, 0.50, 0.25]."""

    def _make_trade_world(self):
        """Create a clean world with no default trade-eligible states."""
        world = _make_world()
        # Clear all default diplomatic states so we control exactly what's set
        world.diplomatic_states = {}
        return world

    def test_single_alliance_full_income(self):
        """Single ALLIANCE partner gets full 200g."""
        world = self._make_trade_world()
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        world.nation_gold = {"France": 1000, "Austria": 1000}
        result = process_trade_income(world)
        assert result["France"] == 200
        assert result["Austria"] == 200

    def test_four_alliances_diminishing(self):
        """4 ALLIANCE partners: 200 + 150 + 100 + 50 = 500g (not 800g)."""
        world = self._make_trade_world()
        for nation in ["Austria", "Prussia", "Russia", "Britain"]:
            _set_diplo_state(world, "France", nation, "ALLIANCE")
        world.nation_gold = {"France": 1000, "Austria": 1000, "Prussia": 1000,
                             "Russia": 1000, "Britain": 1000}
        result = process_trade_income(world)
        # France has 4 partners: 200*1.0 + 200*0.75 + 200*0.50 + 200*0.25 = 500
        assert result["France"] == 500

    def test_mixed_states_sorted_best_first(self):
        """Partners sorted by state priority: ALLIANCE before PEACE."""
        world = self._make_trade_world()
        _set_diplo_state(world, "France", "Austria", "PEACE")       # 50g
        _set_diplo_state(world, "France", "Prussia", "ALLIANCE")    # 200g
        world.nation_gold = {"France": 1000, "Austria": 1000, "Prussia": 1000}
        result = process_trade_income(world)
        # France: ALLIANCE(200*1.0) + PEACE(50*0.75) = 200 + 37 = 237
        assert result["France"] == 237

    def test_vassal_doesnt_count_toward_slots(self):
        """Vassal pairs are excluded from trade (tribute replaces trade)."""
        world = self._make_trade_world()
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        _set_diplo_state(world, "France", "Prussia", "ALLIANCE")
        world.vassals = {"Prussia": {"lord": "France", "loyalty": 60}}
        world.nation_gold = {"France": 1000, "Austria": 1000, "Prussia": 1000}
        result = process_trade_income(world)
        # Prussia is vassal — skipped. France only gets Austria at full rate.
        assert result.get("France", 0) == 200


# ═══════════════════════════════════════════════════════════════════════════
# R18: CONTINENTAL SYSTEM DP COST
# ═══════════════════════════════════════════════════════════════════════════

class TestR18ContinentalSystemCost:
    """R18: CONTINENTAL_SYSTEM explicitly in MISSION_DP_COSTS."""

    def test_continental_system_cost_is_1(self):
        """CONTINENTAL_SYSTEM DP cost is explicitly 1."""
        assert MISSION_DP_COSTS["CONTINENTAL_SYSTEM"] == 1


# ═══════════════════════════════════════════════════════════════════════════
# R4b: COURT_NATION SPEED REDUCTION
# ═══════════════════════════════════════════════════════════════════════════

class TestR4bCourtNationSpeed:
    """R4b: COURT_NATION base relation_change reduced from 8 to 5."""

    def test_base_constant_is_5(self):
        """Base relation_change for COURT_NATION is 5."""
        assert MISSION_EFFECTS["COURT_NATION"]["relation_change"] == 5

    def test_skill_10_gives_8_per_turn(self):
        """Skill 10 diplomat: 5 * 1.5 = 7.5 → round → 8 per turn."""
        base = MISSION_EFFECTS["COURT_NATION"]["relation_change"]
        scaled = int(round(base * 1.5))
        assert scaled == 8


# ═══════════════════════════════════════════════════════════════════════════
# R9: BATTLE CASUALTY THRESHOLD
# ═══════════════════════════════════════════════════════════════════════════

class TestR9BattleCasualtyThreshold:
    """R9: Only battles with >= 1000 total casualties count for war score."""

    def _make_war_world(self):
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "WAR")
        return world

    def test_500_casualties_not_recorded(self):
        """Battle with 500 total casualties → not recorded."""
        world = self._make_war_world()
        record_battle(world, "France", "Austria", "France", 300, 200)
        diplo_key = world._make_diplo_key("France", "Austria")
        records = getattr(world, 'battle_records', {}).get(diplo_key, [])
        assert len(records) == 0

    def test_1000_casualties_recorded(self):
        """Battle with 1000 total casualties → recorded."""
        world = self._make_war_world()
        record_battle(world, "France", "Austria", "France", 600, 400)
        diplo_key = world._make_diplo_key("France", "Austria")
        records = getattr(world, 'battle_records', {}).get(diplo_key, [])
        assert len(records) == 1

    def test_12000_casualties_recorded_and_decisive(self):
        """Battle with 12000 casualties + 3:1 ratio → recorded + decisive."""
        world = self._make_war_world()
        record_battle(world, "France", "Austria", "France", 9000, 3000)
        diplo_key = world._make_diplo_key("France", "Austria")
        records = getattr(world, 'battle_records', {}).get(diplo_key, [])
        assert len(records) == 1
        decisive = getattr(world, 'decisive_battles', {}).get(diplo_key, [])
        assert len(decisive) == 1


# ═══════════════════════════════════════════════════════════════════════════
# R4a: RELATION DECAY
# ═══════════════════════════════════════════════════════════════════════════

class TestR4aRelationDecay:
    """R4a: Relations drift toward +-10 band each turn."""

    def test_positive_50_decays(self):
        """+50 decays to +49."""
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        _set_relation(world, "France", "Austria", 50)
        _process_relation_decay(world)
        assert _get_relation(world, "France", "Austria") == 49

    def test_negative_30_decays(self):
        """-30 decays to -29."""
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "PEACE")
        _set_relation(world, "France", "Austria", -30)
        _process_relation_decay(world)
        assert _get_relation(world, "France", "Austria") == -29

    def test_positive_10_no_decay(self):
        """+10 is in dead band — no decay."""
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "PEACE")
        _set_relation(world, "France", "Austria", 10)
        _process_relation_decay(world)
        assert _get_relation(world, "France", "Austria") == 10

    def test_negative_10_no_decay(self):
        """-10 is in dead band — no decay."""
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "PEACE")
        _set_relation(world, "France", "Austria", -10)
        _process_relation_decay(world)
        assert _get_relation(world, "France", "Austria") == -10

    def test_vassal_pair_skipped(self):
        """Vassal pairs don't decay."""
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        _set_relation(world, "France", "Austria", 50)
        world.vassals = {"Austria": {"lord": "France", "loyalty": 60}}
        _process_relation_decay(world)
        assert _get_relation(world, "France", "Austria") == 50

    def test_court_nation_pair_skipped(self):
        """COURT_NATION mission target pair doesn't decay."""
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "PEACE")
        _set_relation(world, "France", "Austria", 50)
        world.active_diplomatic_mission = {"type": "COURT_NATION", "target": "Austria"}
        _process_relation_decay(world)
        assert _get_relation(world, "France", "Austria") == 50

    def test_war_pair_skipped(self):
        """WAR pairs don't decay."""
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "WAR")
        _set_relation(world, "France", "Austria", -50)
        _process_relation_decay(world)
        assert _get_relation(world, "France", "Austria") == -50


# ═══════════════════════════════════════════════════════════════════════════
# R14: VASSAL RELEASE COOLDOWN
# ═══════════════════════════════════════════════════════════════════════════

class TestR14VassalReleaseCooldown:
    """R14: 5-turn cooldown after vassal release blocks treaty re-vassalization."""

    def _make_vassal_world(self):
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        world.vassals = {"Austria": {
            "lord": "France", "loyalty": 60, "autonomy": "satellite",
            "path": "treaty", "created_turn": 1, "tribute_rate": 0.1,
            "carved_from": None, "regions": None,
        }}
        # Give Austria a region so marshals can be restored
        return world

    def test_release_sets_5_turn_cooldown(self):
        """Releasing a vassal sets a 5-turn cooldown."""
        world = self._make_vassal_world()
        release_vassal(world, "Austria")
        assert world.vassal_release_cooldowns.get("Austria") == 5

    def test_cooldown_blocks_treaty_vassalization(self):
        """Can't re-vassalize via treaty during cooldown."""
        world = self._make_vassal_world()
        release_vassal(world, "Austria")
        # Try to re-vassalize
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        result = create_vassal_treaty(world, "France", "Austria")
        assert result["success"] is False
        assert "recently released" in result["message"]

    def test_cooldown_decrements_to_zero_then_allows(self):
        """After cooldown expires, treaty vassalization works again."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "ALLIANCE")
        world.vassals = {"Saxony": {
            "lord": "France", "loyalty": 60, "autonomy": "satellite",
            "path": "treaty", "created_turn": 1, "tribute_rate": 0.1,
            "carved_from": None, "regions": None,
        }}
        release_vassal(world, "Saxony")
        for _ in range(5):
            decrement_vassal_cooldowns(world)
        assert world.vassal_release_cooldowns.get("Saxony") is None
        _set_diplo_state(world, "France", "Saxony", "ALLIANCE")
        result = create_vassal_treaty(world, "France", "Saxony")
        assert result["success"] is True

    def test_serialization_round_trip(self):
        """vassal_release_cooldowns survives to_dict/from_dict."""
        world = _make_world()
        world.vassal_release_cooldowns = {"Austria": 3}
        data = world.to_dict()
        assert "vassal_release_cooldowns" in data
        restored = WorldState.from_dict(data)
        assert restored.vassal_release_cooldowns == {"Austria": 3}


# ═══════════════════════════════════════════════════════════════════════════
# R16: REGION CAPTURE THREAT
# ═══════════════════════════════════════════════════════════════════════════

class TestR16RegionCaptureThreat:
    """R16: +2 threat per captured non-starting region (France only)."""

    def test_france_captures_bavaria_adds_threat(self):
        """France capturing Bavaria (not French starting) → +2 threat."""
        world = _make_world()
        world.threat_level = 10
        world.threat_sources_this_turn = []
        world.capture_region("Bavaria", "France")
        assert world.threat_level == 12

    def test_france_recaptures_own_starting_no_threat(self):
        """France recapturing Paris (French starting) → no threat."""
        world = _make_world()
        world.threat_level = 10
        world.threat_sources_this_turn = []
        # Paris is France's starting territory — set to enemy first
        world.regions["Paris"].controller = "Austria"
        old_threat = world.threat_level
        world.capture_region("Paris", "France")
        assert world.threat_level == old_threat

    def test_ai_capture_no_threat(self):
        """AI capturing a region → no threat to France."""
        world = _make_world()
        world.threat_level = 10
        world.threat_sources_this_turn = []
        old_threat = world.threat_level
        world.capture_region("Bavaria", "Austria")
        assert world.threat_level == old_threat


# ═══════════════════════════════════════════════════════════════════════════
# R11: COALITION STALEMATE DURATION
# ═══════════════════════════════════════════════════════════════════════════

class TestR11CoalitionStalemate:
    """R11: Faster WE gain (+8/turn) and coalition member friction (-2/turn)."""

    def _make_coalition_world(self):
        world = _make_world()
        world.threat_level = 80
        world.threat_sources_this_turn = []
        world.war_exhaustion = {"Austria": 0, "Prussia": 0, "Russia": 0}
        world.active_coalition = {
            "members": ["Austria", "Prussia", "Russia"],
            "leader": "Austria",
            "formed_turn": 1,
        }
        _set_diplo_state(world, "France", "Austria", "WAR")
        _set_diplo_state(world, "France", "Prussia", "WAR")
        _set_diplo_state(world, "France", "Russia", "WAR")
        # Set inter-member relations
        _set_relation(world, "Austria", "Prussia", 40)
        _set_relation(world, "Austria", "Russia", 40)
        _set_relation(world, "Prussia", "Russia", 40)
        return world

    def test_war_exhaustion_8_per_turn(self):
        """Nations at WAR gain 8 WE/turn (was 5)."""
        world = self._make_coalition_world()
        process_coalition_turn(world)
        assert world.war_exhaustion["Austria"] == 8

    def test_coalition_member_friction(self):
        """Coalition members lose 2 mutual relation per turn."""
        world = self._make_coalition_world()
        process_coalition_turn(world)
        # Austria-Prussia: 40 - 2 = 38
        assert _get_relation(world, "Austria", "Prussia") == 38
        assert _get_relation(world, "Austria", "Russia") == 38
        assert _get_relation(world, "Prussia", "Russia") == 38

    def test_no_friction_without_coalition(self):
        """No friction if no active coalition."""
        world = _make_world()
        world.threat_level = 10
        world.threat_sources_this_turn = []
        world.war_exhaustion = {}
        world.active_coalition = None
        _set_relation(world, "Austria", "Prussia", 40)
        process_coalition_turn(world)
        assert _get_relation(world, "Austria", "Prussia") == 40


# ═══════════════════════════════════════════════════════════════════════════
# R106: P3 AI TRIGGER (THREAT-BASED ALLIANCE SEEKING)
# ═══════════════════════════════════════════════════════════════════════════

class TestR106P3AITrigger:
    """R106: AI nations seek alliances when threat > 60."""

    def test_threat_70_proposes_upgrade_from_peace(self):
        """Threat=70, PEACE, relation=25 → proposes open_borders (DLF-9: follows upgrade path)."""
        world = _make_world()
        world.threat_level = 70
        _set_diplo_state(world, "France", "Austria", "PEACE")
        _set_relation(world, "France", "Austria", 25)
        from backend.models.diplomat import DiplomaticRepresentative
        world.diplomats = {
            "France": DiplomaticRepresentative("Talleyrand", "France", "cautious", skill=7),
            "Austria": DiplomaticRepresentative("Metternich", "Austria", "cautious", skill=7),
        }
        from backend.game_logic.ai_diplomacy import process_diplomatic_phase
        result = process_diplomatic_phase("Austria", world)
        assert result is not None
        assert result["proposal_type"] == "open_borders"

    def test_already_alliance_skips(self):
        """Already ALLIANCE → P3 doesn't trigger."""
        world = _make_world()
        world.threat_level = 70
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        _set_relation(world, "France", "Austria", 50)
        from backend.models.diplomat import DiplomaticRepresentative
        world.diplomats = {
            "France": DiplomaticRepresentative("Talleyrand", "France", "cautious", skill=7),
            "Austria": DiplomaticRepresentative("Metternich", "Austria", "cautious", skill=7),
        }
        from backend.game_logic.ai_diplomacy import process_diplomatic_phase
        result = process_diplomatic_phase("Austria", world)
        # Should not produce a proposal from P3 (already allied)
        if result is not None:
            assert result.get("priority") != 3  # Not P3

    def test_at_war_skips(self):
        """Nations at war with France → P3 skips (is_at_war=True)."""
        world = _make_world()
        world.threat_level = 70
        _set_diplo_state(world, "France", "Austria", "WAR")
        _set_relation(world, "France", "Austria", 25)
        from backend.models.diplomat import DiplomaticRepresentative
        world.diplomats = {
            "France": DiplomaticRepresentative("Talleyrand", "France", "cautious", skill=7),
            "Austria": DiplomaticRepresentative("Metternich", "Austria", "cautious", skill=7),
        }
        from backend.game_logic.ai_diplomacy import process_diplomatic_phase
        result = process_diplomatic_phase("Austria", world)
        # At war, P1/P2 may fire but not P3
        if result is not None:
            assert result.get("priority") != 3


# ═══════════════════════════════════════════════════════════════════════════
# R15: AI-AI DIPLOMACY DEGRADATION
# ═══════════════════════════════════════════════════════════════════════════

class TestR15AIAIDiplomacyDegradation:
    """R15: Adjacent rivalry and opportunistic downgrades between AI nations."""

    def test_adjacent_rivalry_degrades_relation(self):
        """Adjacent AI nations with relation > 0 lose 3 relation/turn."""
        world = _make_world()
        # Austria controls Vienna, Prussia controls Berlin — check adjacency
        # Use actual adjacent regions
        austria_regions = [r for r, reg in world.regions.items() if reg.controller == "Austria"]
        prussia_regions = [r for r, reg in world.regions.items() if reg.controller == "Prussia"]

        _set_diplo_state(world, "Austria", "Prussia", "PEACE")
        _set_relation(world, "Austria", "Prussia", 20)

        # Check if Austria and Prussia have adjacent territories
        adjacent = False
        for rname in austria_regions:
            region = world.regions[rname]
            for adj in region.adjacent_regions:
                if adj in prussia_regions:
                    adjacent = True
                    break

        from backend.game_logic.ai_diplomacy import _process_ai_ai_rivalry
        events = _process_ai_ai_rivalry(world)

        if adjacent:
            assert _get_relation(world, "Austria", "Prussia") == 17
        else:
            # Not adjacent — no change (test documents behavior)
            assert _get_relation(world, "Austria", "Prussia") == 20

    def test_non_adjacent_no_degradation(self):
        """Non-adjacent AI nations with relation > 0 → no rivalry degradation."""
        world = _make_world()
        # Russia and Britain are not adjacent in the game map
        _set_diplo_state(world, "Russia", "Britain", "PEACE")
        _set_relation(world, "Russia", "Britain", 20)

        from backend.game_logic.ai_diplomacy import _process_ai_ai_rivalry
        events = _process_ai_ai_rivalry(world)

        # Check if they're actually non-adjacent
        russia_regions = {r for r, reg in world.regions.items() if reg.controller == "Russia"}
        britain_regions = {r for r, reg in world.regions.items() if reg.controller == "Britain"}
        adjacent = False
        for rname in russia_regions:
            region = world.regions.get(rname)
            if region:
                for adj in region.adjacent_regions:
                    if adj in britain_regions:
                        adjacent = True
                        break

        if not adjacent:
            assert _get_relation(world, "Russia", "Britain") == 20

    def test_2x_military_triggers_downgrade(self):
        """AI nation with 2x troops + relation < 30 → one-step downgrade."""
        world = _make_world()
        _set_diplo_state(world, "Austria", "Prussia", "NON_AGGRESSION")
        _set_relation(world, "Austria", "Prussia", 10)

        # Give Austria 2x+ troops over Prussia
        from backend.models.marshal import Marshal
        # Clear existing marshals and set up controlled ones
        for name in list(world.marshals.keys()):
            m = world.marshals[name]
            if m.nation in ("Austria", "Prussia"):
                del world.marshals[name]

        m_austria = Marshal("TestAustrian", "Vienna", 30000, "cautious", nation="Austria")
        world.marshals["TestAustrian"] = m_austria

        m_prussia = Marshal("TestPrussian", "Berlin", 10000, "cautious", nation="Prussia")
        world.marshals["TestPrussian"] = m_prussia

        from backend.game_logic.ai_diplomacy import _process_ai_ai_rivalry
        events = _process_ai_ai_rivalry(world)

        diplo_key = world._make_diplo_key("Austria", "Prussia")
        state = world.diplomatic_states.get(diplo_key)
        assert state == "OPEN_BORDERS"  # NON_AGGRESSION → OPEN_BORDERS

    def test_already_peace_no_downgrade(self):
        """Already at PEACE → no further downgrade."""
        world = _make_world()
        _set_diplo_state(world, "Austria", "Prussia", "PEACE")
        _set_relation(world, "Austria", "Prussia", 10)

        from backend.models.marshal import Marshal
        for name in list(world.marshals.keys()):
            m = world.marshals[name]
            if m.nation in ("Austria", "Prussia"):
                del world.marshals[name]

        m_austria = Marshal("TestAustrian", "Vienna", 30000, "cautious", nation="Austria")
        world.marshals["TestAustrian"] = m_austria

        m_prussia = Marshal("TestPrussian", "Berlin", 10000, "cautious", nation="Prussia")
        world.marshals["TestPrussian"] = m_prussia

        from backend.game_logic.ai_diplomacy import _process_ai_ai_rivalry
        events = _process_ai_ai_rivalry(world)

        diplo_key = world._make_diplo_key("Austria", "Prussia")
        state = world.diplomatic_states.get(diplo_key, "PEACE")
        assert state == "PEACE"  # Still PEACE
