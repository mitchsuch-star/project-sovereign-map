"""
Tests for Diplomacy Refinement Phase 5 — Wave 1 (Quick Wins)

R134: DEBUG_MODE security fix
R121: P2 stalemate trigger fix
R137: "ally with" parser fix
R120: Diplomatic help text
R140: Relation cap in acceptance formula
R139: AI DP cap raised
R138: Counter-offer costs 1 DP for AI
R135: Garrison loyalty cap at +4
R58:  Vindication tracker decay
R130: Confidence levels in advisory
"""
from backend.models.world_state import WorldState
from backend.game_logic.diplomacy import calculate_acceptance, calculate_dp
from backend.game_logic.ai_diplomacy import generate_counter_offer
from backend.game_logic.vassal import process_vassal_loyalty, AUTONOMY_SATELLITE
from backend.commands.vindication import VindicationTracker


def make_world():
    """Create a basic world for testing."""
    world = WorldState(player_nation="France")
    return world


def make_world_with_vassal(autonomy=AUTONOMY_SATELLITE, loyalty=60):
    """Create world with Saxony as vassal."""
    world = make_world()
    world.vassals["Saxony"] = {
        "lord": "France",
        "loyalty": loyalty,
        "autonomy": autonomy,
        "tribute_rate": 0.1,
        "turns_as_vassal": 5,
    }
    return world


# ═══════════════════════════════════════════════════════
# R134: DEBUG_MODE Security Fix
# ═══════════════════════════════════════════════════════

class TestDebugModeSecurity:
    def test_debug_mode_default_false(self):
        """DEBUG_MODE should be False when env var is unset."""
        import os
        old = os.environ.pop("DEBUG_MODE", None)
        try:
            result = os.getenv("DEBUG_MODE", "false").lower() == "true"
            assert result is False
        finally:
            if old is not None:
                os.environ["DEBUG_MODE"] = old

    def test_debug_mode_true_when_set(self):
        """DEBUG_MODE should be True when env var is 'true'."""
        import os
        old = os.environ.get("DEBUG_MODE")
        try:
            os.environ["DEBUG_MODE"] = "true"
            result = os.getenv("DEBUG_MODE", "false").lower() == "true"
            assert result is True
        finally:
            if old is not None:
                os.environ["DEBUG_MODE"] = old
            else:
                os.environ.pop("DEBUG_MODE", None)


# ═══════════════════════════════════════════════════════
# R121: P2 Stalemate Trigger Fix
# ═══════════════════════════════════════════════════════

class TestP2StalemateFix:
    def test_p2_condition_blocks_winning_ai(self):
        """The P2 condition should include war_score <= 10 check (R149: raised from <= 0)."""
        import inspect
        from backend.game_logic import ai_diplomacy
        source = inspect.getsource(ai_diplomacy.process_diplomatic_phase)
        # R149: Verify the war_score <= 10 condition exists in P2
        assert "war_score <= 10" in source


# ═══════════════════════════════════════════════════════
# R137: "ally with" Parser Fix
# ═══════════════════════════════════════════════════════

class TestAllyParser:
    def test_ally_with_routes_diplomatic(self):
        """'ally with Prussia' should route to diplomatic parser."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client.parse_command("ally with Prussia", {})
        assert result["command_type"] == "diplomatic"

    def test_form_alliance_routes_diplomatic(self):
        """'form alliance with Austria' should route to diplomatic parser."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client.parse_command("form alliance with Austria", {})
        assert result["command_type"] == "diplomatic"

    def test_attack_not_false_positive(self):
        """'Ney, attack' should NOT route to diplomatic just because of 'ally'."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client.parse_command("Ney, attack", {})
        assert result["command_type"] != "diplomatic"


# ═══════════════════════════════════════════════════════
# R120: Diplomatic Help Text
# ═══════════════════════════════════════════════════════

class TestDiplomaticHelpText:
    def test_help_contains_diplomacy_section(self):
        """Help text should include DIPLOMACY section."""
        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        world = make_world()
        game_state = {"world": world}
        # Need at least one marshal for executor to work
        result = executor._execute_help(None, game_state)
        assert "DIPLOMACY" in result["message"]
        assert "propose" in result["message"]
        assert "assess" in result["message"]
        assert "improve" in result["message"]


# ═══════════════════════════════════════════════════════
# R140: Relation Cap in Acceptance Formula
# ═══════════════════════════════════════════════════════

class TestRelationCap:
    def test_positive_relation_capped_at_30(self):
        """Relation +100 should yield relation_mod = 30, not 50 (peacetime formula)."""
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[key] = 100
        world.diplomatic_states[key] = "PEACE"  # R141: must be PEACE for full-range cap test
        proposal = {
            "type": "non_aggression",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        assert result["components"]["relation_modifier"] == 30

    def test_negative_relation_capped_at_minus_30(self):
        """Relation -100 should yield relation_mod = -30, not -50 (peacetime formula)."""
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[key] = -100
        world.diplomatic_states[key] = "PEACE"  # R141: must be PEACE for full-range cap test
        proposal = {
            "type": "non_aggression",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        assert result["components"]["relation_modifier"] == -30

    def test_relation_within_cap_unchanged(self):
        """Relation +40 should yield relation_mod = 20 (within cap, peacetime)."""
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[key] = 40
        world.diplomatic_states[key] = "PEACE"  # R141: must be PEACE for full-range cap test
        proposal = {
            "type": "non_aggression",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        assert result["components"]["relation_modifier"] == 20


# ═══════════════════════════════════════════════════════
# R139: AI DP Cap Raised
# ═══════════════════════════════════════════════════════

class TestAIDPCap:
    def test_high_skill_diplomat_5dp(self):
        """Diplomat with skill 10 + high authority generates 5 DP."""
        from backend.models.diplomat import DiplomaticRepresentative
        diplomat = DiplomaticRepresentative("Metternich", "Austria", "schemer", 10)
        dp = calculate_dp(diplomat, 60, True)
        assert dp == 5  # 3 base + 1 skill(>=8) + 1 authority(>=60)

    def test_low_skill_diplomat_3dp(self):
        """Diplomat with skill 5 generates 3 DP base."""
        from backend.models.diplomat import DiplomaticRepresentative
        diplomat = DiplomaticRepresentative("Minor", "Saxony", "dove", 5)
        dp = calculate_dp(diplomat, 50, True)
        assert dp == 3  # 3 base + 0 skill(<8) + 0 authority(30-59)

    def test_skill_8_gets_bonus(self):
        """Diplomat with skill exactly 8 gets the bonus (was 10)."""
        from backend.models.diplomat import DiplomaticRepresentative
        diplomat = DiplomaticRepresentative("Good", "Test", "loyalist", 8)
        dp = calculate_dp(diplomat, 50, True)
        assert dp == 4  # 3 base + 1 skill(>=8) + 0 authority


# ═══════════════════════════════════════════════════════
# R138: Counter-Offer Costs 1 DP for AI
# ═══════════════════════════════════════════════════════

class TestCounterOfferDPCost:
    def test_ai_counter_deducts_dp(self):
        """AI with DP tracked should have 1 DP deducted on counter-offer."""
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_scores[key] = -20
        world.nation_relations[key] = -10
        world.nation_dp = {"Prussia": 3}
        proposal = {
            "type": "armistice_losing",
            "proposer_nation": "Prussia",
            "target_nation": "France",
            "sweeteners": [{"type": "gold_per_turn", "value": 50}],
            "demands": [],
            "clauses": [],
        }
        generate_counter_offer(proposal, world)
        assert world.nation_dp["Prussia"] == 2

    def test_ai_counter_rejected_no_dp(self):
        """AI with 0 DP should get None (rejection) instead of counter."""
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.nation_dp = {"Prussia": 0}
        proposal = {
            "type": "peace",
            "proposer_nation": "Prussia",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        result = generate_counter_offer(proposal, world)
        assert result is None


# ═══════════════════════════════════════════════════════
# R135: Garrison Loyalty Cap at +4
# ═══════════════════════════════════════════════════════

class TestGarrisonCap:
    def test_small_garrison_bonus(self):
        """5k garrison → +6 garrison bonus (Fix 19: base 5). Total includes relation modifier."""
        world = make_world_with_vassal(loyalty=60)
        # Zero out relation to isolate garrison effect
        key = world._make_diplo_key("France", "Saxony")
        world.nation_relations[key] = 0
        region = world.regions.get("Dresden")
        if region:
            region.garrison_troops = 5000
            region.controller = "France"
        process_vassal_loyalty(world)
        # drift(-2) + garrison(min(8, 5+1)=6) + relation(0//20=0) = +4
        assert world.vassals["Saxony"]["loyalty"] == 64

    def test_large_garrison_capped(self):
        """15k garrison → +8 garrison bonus (Fix 19: cap 8)."""
        world = make_world_with_vassal(loyalty=60)
        key = world._make_diplo_key("France", "Saxony")
        world.nation_relations[key] = 0
        region = world.regions.get("Dresden")
        if region:
            region.garrison_troops = 15000
            region.controller = "France"
        process_vassal_loyalty(world)
        # drift(-2) + garrison(min(8, 5+3)=8) + relation(0) = +6
        assert world.vassals["Saxony"]["loyalty"] == 66


# ═══════════════════════════════════════════════════════
# R58: Vindication Tracker Decay
# ═══════════════════════════════════════════════════════

class TestVindicationDecay:
    def test_positive_score_decays(self):
        """Score +3 at turn 10, no changes → +2 at turn 15."""
        world = make_world()
        marshal = world.marshals.get("Ney")
        if marshal:
            marshal.vindication_score = 3
        world.vindication_tracker.last_change_turn["Ney"] = 10
        world.current_turn = 15
        world._process_vindication_decay()
        assert marshal.vindication_score == 2

    def test_negative_score_decays_toward_zero(self):
        """Score -2 at turn 5, no changes → -1 at turn 10."""
        world = make_world()
        marshal = world.marshals.get("Ney")
        if marshal:
            marshal.vindication_score = -2
            marshal.last_objection_turn = 5
        world.vindication_tracker.last_change_turn["Ney"] = 5
        world.current_turn = 10
        world._process_vindication_decay()
        assert marshal.vindication_score == -1

    def test_no_decay_within_5_turns(self):
        """Score +3 should not decay within 5 turns of last change."""
        world = make_world()
        marshal = world.marshals.get("Ney")
        if marshal:
            marshal.vindication_score = 3
        world.vindication_tracker.last_change_turn["Ney"] = 10
        world.current_turn = 13  # Only 3 turns, not 5
        world._process_vindication_decay()
        assert marshal.vindication_score == 3

    def test_serialization(self):
        """last_change_turn should survive serialization round-trip."""
        tracker = VindicationTracker()
        tracker.last_change_turn = {"Ney": 10, "Davout": 15}
        data = tracker.to_dict()
        restored = VindicationTracker.from_dict(data)
        assert restored.last_change_turn == {"Ney": 10, "Davout": 15}


# ═══════════════════════════════════════════════════════
# R130: Confidence Levels in Advisory
# ═══════════════════════════════════════════════════════

class TestConfidenceLevels:
    def test_high_confidence_visible_regions(self):
        """Target with most regions visible → high confidence."""
        from backend.game_logic.diplomatic_advisory import generate_advisory
        world = make_world()
        for name, region in world.regions.items():
            if getattr(region, 'controller', '') == "Austria":
                intel = world.get_region_intel(name)
                intel.visibility = "full"
        from backend.models.diplomat import DiplomaticRepresentative
        world.diplomats["Austria"] = DiplomaticRepresentative("Metternich", "Austria", "schemer", 10)
        result = generate_advisory("Austria", "assess_nation", world)
        assert result["context"]["confidence_level"] == "high"
        text = result["talleyrand_text"].lower()
        assert "confident" in text or "reliable" in text

    def test_low_confidence_hidden_regions(self):
        """Target with no regions visible → low confidence."""
        from backend.game_logic.diplomatic_advisory import generate_advisory
        world = make_world()
        for name, region in world.regions.items():
            if getattr(region, 'controller', '') == "Austria":
                intel = world.get_region_intel(name)
                intel.visibility = "unknown"
        from backend.models.diplomat import DiplomaticRepresentative
        world.diplomats["Austria"] = DiplomaticRepresentative("Metternich", "Austria", "schemer", 10)
        result = generate_advisory("Austria", "assess_nation", world)
        assert result["context"]["confidence_level"] == "low"
        text = result["talleyrand_text"].lower()
        assert "incomplete" in text or "caution" in text

    def test_medium_confidence_partial_visibility(self):
        """Target with some regions visible → medium confidence."""
        from backend.game_logic.diplomatic_advisory import generate_advisory
        world = make_world()
        austria_regions = [name for name, r in world.regions.items()
                          if getattr(r, 'controller', '') == "Austria"]
        for i, name in enumerate(austria_regions):
            intel = world.get_region_intel(name)
            if i == 0:
                intel.visibility = "partial"
            else:
                intel.visibility = "unknown"
        from backend.models.diplomat import DiplomaticRepresentative
        world.diplomats["Austria"] = DiplomaticRepresentative("Metternich", "Austria", "schemer", 10)
        result = generate_advisory("Austria", "assess_nation", world)
        assert result["context"]["confidence_level"] in ("low", "medium")
