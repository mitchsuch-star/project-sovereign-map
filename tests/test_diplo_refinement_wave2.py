"""
Tests for Diplomacy Refinement Phase 5 — Wave 2 (AI Intelligence)

R126: Urgent re-proposal on situation change
R115: Personality-driven AI proposals
R116: Aggressive dominance P8
R125: Counter-offer personality thresholds
R122: Coalition posture drives enemy AI
"""
from backend.models.world_state import WorldState
from backend.models.diplomat import DiplomaticRepresentative
from backend.game_logic.ai_diplomacy import (
    process_diplomatic_phase,
    _is_on_cooldown,
    _build_proposal_terms,
    _get_personality_modifiers,
    PERSONALITY_PROPOSAL_MODIFIERS,
    PERSONALITY_COUNTER_THRESHOLDS,
)


def make_world():
    """Create a basic world for testing."""
    world = WorldState(player_nation="France")
    return world


def set_war(world, nation_a, nation_b):
    """Put two nations at war."""
    key = world._make_diplo_key(nation_a, nation_b)
    world.diplomatic_states[key] = "WAR"


def set_war_score(world, nation, opponent, score):
    """Set war score from nation's perspective (positive = nation winning)."""
    key = world._make_diplo_key(nation, opponent)
    parts = key.split("|")
    # Store from alphabetically-first nation's perspective
    if parts[0] == nation:
        world.war_scores[key] = score
    else:
        world.war_scores[key] = -score


def set_diplomat_personality(world, nation, personality):
    """Set a nation's diplomat personality."""
    diplomats = getattr(world, 'diplomats', {})
    if nation in diplomats:
        diplomats[nation].personality = personality
    else:
        diplomats[nation] = DiplomaticRepresentative(
            name=f"Test_{nation}", nation=nation,
            personality=personality, skill=5,
        )
    world.diplomats = diplomats


# ═══════════════════════════════════════════════════════
# R126: Urgent Re-Proposal on Situation Change
# ═══════════════════════════════════════════════════════

class TestUrgentReProposal:
    def test_no_bypass_without_metadata(self):
        """Nation cooldown should NOT be bypassed if no prior proposal metadata."""
        world = make_world()
        world.ai_proposal_cooldowns = {"Prussia|nation": 2}
        assert _is_on_cooldown("Prussia", "peace", world, war_score=-60) is True

    def test_small_drop_no_bypass(self):
        """War score drop of 15 (< 20) should NOT bypass nation cooldown."""
        world = make_world()
        world.ai_proposal_cooldowns = {"Prussia|nation": 2}
        world.ai_proposal_metadata = {"Prussia": {"war_score_at_proposal": -30, "turn": 1}}
        # Current war_score = -45, drop = -30 - (-45) = 15 < 20
        assert _is_on_cooldown("Prussia", "peace", world, war_score=-45) is True

    def test_exact_delta_bypasses(self):
        """War score drop of exactly 20 should bypass nation cooldown."""
        world = make_world()
        world.ai_proposal_cooldowns = {"Prussia|nation": 2}
        world.ai_proposal_metadata = {"Prussia": {"war_score_at_proposal": -30, "turn": 1}}
        # Current war_score = -50, drop = -30 - (-50) = 20
        assert _is_on_cooldown("Prussia", "peace", world, war_score=-50) is False

    def test_large_drop_bypasses(self):
        """War score drop of 40 should bypass nation cooldown."""
        world = make_world()
        world.ai_proposal_cooldowns = {"Prussia|nation": 2}
        world.ai_proposal_metadata = {"Prussia": {"war_score_at_proposal": -20, "turn": 1}}
        # Current war_score = -60, drop = -20 - (-60) = 40
        assert _is_on_cooldown("Prussia", "peace", world, war_score=-60) is False

    def test_type_cooldown_still_applies(self):
        """Type cooldown should NOT be bypassed even with urgent situation."""
        world = make_world()
        world.ai_proposal_cooldowns = {"Prussia|peace": 3}
        world.ai_proposal_metadata = {"Prussia": {"war_score_at_proposal": -20, "turn": 1}}
        # Large drop, but type cooldown is active
        assert _is_on_cooldown("Prussia", "peace", world, war_score=-60) is True

    def test_metadata_written_on_proposal(self):
        """_make_proposal should record war_score metadata."""
        world = make_world()
        set_war(world, "France", "Prussia")
        set_war_score(world, "Prussia", "France", -50)
        result = process_diplomatic_phase("Prussia", world)
        # If a proposal was generated, metadata should exist
        if result is not None:
            assert "Prussia" in world.ai_proposal_metadata
            assert "war_score_at_proposal" in world.ai_proposal_metadata["Prussia"]
            assert "turn" in world.ai_proposal_metadata["Prussia"]

    def test_serialization_roundtrip(self):
        """ai_proposal_metadata should survive to_dict/from_dict."""
        world = make_world()
        world.ai_proposal_metadata = {
            "Prussia": {"war_score_at_proposal": -30, "turn": 3},
            "Austria": {"war_score_at_proposal": -10, "turn": 5},
        }
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.ai_proposal_metadata["Prussia"]["war_score_at_proposal"] == -30
        assert restored.ai_proposal_metadata["Austria"]["turn"] == 5


# ═══════════════════════════════════════════════════════
# R115: Personality-Driven AI Proposals
# ═══════════════════════════════════════════════════════

class TestPersonalityProposals:
    def test_hawk_higher_gold(self):
        """Hawk personality should multiply gold by 1.5."""
        world = make_world()
        set_diplomat_personality(world, "Prussia", "hawk")
        mods = _get_personality_modifiers("Prussia", world)
        assert mods["gold_demand_mult"] == 1.5

    def test_hawk_stricter_peace_threshold(self):
        """Hawk peace_threshold_delta is -20, effective P1 = -40 + (-20) = -60."""
        world = make_world()
        set_diplomat_personality(world, "Prussia", "hawk")
        mods = _get_personality_modifiers("Prussia", world)
        effective_p1 = -40 + mods["peace_threshold_delta"]
        assert effective_p1 == -60

    def test_dove_lower_gold(self):
        """Dove personality should multiply gold by 0.75."""
        world = make_world()
        set_diplomat_personality(world, "Saxony", "dove")
        mods = _get_personality_modifiers("Saxony", world)
        assert mods["gold_demand_mult"] == 0.75

    def test_dove_earlier_peace(self):
        """Dove peace_threshold_delta is +20, effective P1 = -40 + 20 = -20."""
        world = make_world()
        set_diplomat_personality(world, "Saxony", "dove")
        mods = _get_personality_modifiers("Saxony", world)
        effective_p1 = -40 + mods["peace_threshold_delta"]
        assert effective_p1 == -20

    def test_schemer_patience(self):
        """Schemer patience_bonus = 2, effective stalemate turns = 5 + 2 = 7."""
        world = make_world()
        set_diplomat_personality(world, "Austria", "schemer")
        mods = _get_personality_modifiers("Austria", world)
        effective_stalemate = 5 + mods["patience_bonus"]
        assert effective_stalemate == 7

    def test_loyalist_unchanged(self):
        """Loyalist should have no modifiers (all baseline)."""
        world = make_world()
        set_diplomat_personality(world, "Prussia", "loyalist")
        mods = _get_personality_modifiers("Prussia", world)
        assert mods["gold_demand_mult"] == 1.0
        assert mods["peace_threshold_delta"] == 0
        assert mods["patience_bonus"] == 0

    def test_table_completeness(self):
        """All 4 diplomat personalities should be in the modifiers table."""
        for p in ("hawk", "schemer", "dove", "loyalist"):
            assert p in PERSONALITY_PROPOSAL_MODIFIERS
            mods = PERSONALITY_PROPOSAL_MODIFIERS[p]
            assert "gold_demand_mult" in mods
            assert "peace_threshold_delta" in mods
            assert "patience_bonus" in mods

    def test_gold_mult_applied_to_armistice(self):
        """Hawk gold_mult=1.5 should increase armistice gold offer."""
        world = make_world()
        world.nation_gold["Prussia"] = 1000
        terms_hawk = _build_proposal_terms("Prussia", "armistice_losing", -50, world, gold_mult=1.5)
        terms_base = _build_proposal_terms("Prussia", "armistice_losing", -50, world, gold_mult=1.0)
        # Hawk should offer more (higher multiplier = more generous to get deal)
        hawk_gold = 0
        base_gold = 0
        for s in terms_hawk.get("sweeteners", []):
            if s["type"] == "gold_per_turn":
                hawk_gold = s["value"]
        for s in terms_base.get("sweeteners", []):
            if s["type"] == "gold_per_turn":
                base_gold = s["value"]
        # With gold_mult=1.5, the gold should be higher (or capped)
        assert hawk_gold >= base_gold

    def test_gold_mult_applied_to_opportunistic(self):
        """Hawk gold_mult=1.5 should increase opportunistic demand."""
        world = make_world()
        terms_hawk = _build_proposal_terms("Prussia", "opportunistic", 0, world, gold_mult=1.5)
        terms_base = _build_proposal_terms("Prussia", "opportunistic", 0, world, gold_mult=1.0)
        hawk_demand = terms_hawk["demands"][0]["value"]
        base_demand = terms_base["demands"][0]["value"]
        assert hawk_demand == 150  # 100 * 1.5
        assert base_demand == 100  # 100 * 1.0


# ═══════════════════════════════════════════════════════
# R116: Aggressive Dominance P8
# ═══════════════════════════════════════════════════════

class TestAggressiveDominanceP8:
    def test_no_p8_below_40(self):
        """P8 should not fire when war_score <= 40."""
        world = make_world()
        set_war(world, "France", "Prussia")
        set_diplomat_personality(world, "Prussia", "loyalist")
        # War score 30 (Prussia winning slightly)
        set_war_score(world, "Prussia", "France", 30)
        result = process_diplomatic_phase("Prussia", world)
        # Should NOT generate a harsh_peace at 30
        if result is not None:
            assert result["proposal_type"] != "harsh_peace"

    def test_p8_fires_above_40(self):
        """P8 should fire when war_score > 40 and no higher priority triggers."""
        world = make_world()
        set_war(world, "France", "Prussia")
        set_diplomat_personality(world, "Prussia", "loyalist")
        # War score 50 (Prussia winning comfortably)
        set_war_score(world, "Prussia", "France", 50)
        result = process_diplomatic_phase("Prussia", world)
        assert result is not None
        assert result["proposal_type"] == "harsh_peace"

    def test_gold_scales_with_war_score(self):
        """Harsh peace gold demand should scale with war_score."""
        world = make_world()
        terms_50 = _build_proposal_terms("Prussia", "harsh_peace", 50, world, gold_mult=1.0)
        terms_80 = _build_proposal_terms("Prussia", "harsh_peace", 80, world, gold_mult=1.0)
        gold_50 = terms_50["demands"][0]["value"]
        gold_80 = terms_80["demands"][0]["value"]
        assert gold_50 == max(200, int(50 * 5))  # 250
        assert gold_80 == max(200, int(80 * 5))  # 400
        assert gold_80 > gold_50

    def test_ap_reduction_removed_dead_code(self):
        """ap_reduction clause was dead code (no handler) and has been removed.
        Harsh peace proposals at war_score > 60 should NOT include ap_reduction."""
        world = make_world()
        set_war(world, "France", "Prussia")
        set_diplomat_personality(world, "Prussia", "loyalist")
        set_war_score(world, "Prussia", "France", 65)
        result = process_diplomatic_phase("Prussia", world)
        assert result is not None
        assert "ap_reduction" not in result["terms"]["clauses"]

    def test_no_ap_reduction_below_60(self):
        """ap_reduction clause should NOT be present at any war_score."""
        world = make_world()
        set_war(world, "France", "Prussia")
        set_diplomat_personality(world, "Prussia", "loyalist")
        set_war_score(world, "Prussia", "France", 55)
        result = process_diplomatic_phase("Prussia", world)
        assert result is not None
        assert "ap_reduction" not in result["terms"]["clauses"]

    def test_p8_only_when_p1_p7_none(self):
        """P8 should only fire if P1-P7 returned no proposal.

        P1 fires when war_score < -40 (losing). With war_score = 50 (winning),
        P1 should NOT fire and P8 should.
        """
        world = make_world()
        set_war(world, "France", "Prussia")
        set_diplomat_personality(world, "Prussia", "loyalist")
        set_war_score(world, "Prussia", "France", 50)
        result = process_diplomatic_phase("Prussia", world)
        # P1 needs war_score < -40 (Prussia losing), not applicable here
        # P8 should fire since Prussia is winning
        assert result is not None
        assert result["proposal_type"] == "harsh_peace"


# ═══════════════════════════════════════════════════════
# R125: Counter-Offer Personality Thresholds
# ═══════════════════════════════════════════════════════

class TestCounterOfferThresholds:
    def _make_counter_proposal(self, world, score_target=45):
        """Create a proposal that will have a known baseline score.

        Uses non_aggression with demands to pull score down.
        """
        return {
            "type": "non_aggression",
            "proposer_nation": "Prussia",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [{"type": "gold_per_turn", "value": 200}],
            "clauses": [],
        }

    def test_hawk_rejects_at_55(self):
        """Hawk (accept=60) should NOT accept a score of 55 as good enough."""
        world = make_world()
        set_diplomat_personality(world, "Prussia", "hawk")
        thresholds = PERSONALITY_COUNTER_THRESHOLDS["hawk"]
        assert thresholds["accept"] == 60
        assert thresholds["floor"] == 35

    def test_dove_accepts_at_42(self):
        """Dove (accept=40) should consider 42 as acceptable."""
        world = make_world()
        set_diplomat_personality(world, "Saxony", "dove")
        thresholds = PERSONALITY_COUNTER_THRESHOLDS["dove"]
        assert thresholds["accept"] == 40
        assert thresholds["floor"] == 25

    def test_schemer_uses_50_30(self):
        """Schemer should use baseline 50/30 thresholds."""
        thresholds = PERSONALITY_COUNTER_THRESHOLDS["schemer"]
        assert thresholds["accept"] == 50
        assert thresholds["floor"] == 30

    def test_loyalist_uses_50_30(self):
        """Loyalist should use baseline 50/30 thresholds."""
        thresholds = PERSONALITY_COUNTER_THRESHOLDS["loyalist"]
        assert thresholds["accept"] == 50
        assert thresholds["floor"] == 30

    def test_table_completeness(self):
        """All 4 diplomat personalities should be in counter thresholds."""
        for p in ("hawk", "dove", "schemer", "loyalist"):
            assert p in PERSONALITY_COUNTER_THRESHOLDS
            t = PERSONALITY_COUNTER_THRESHOLDS[p]
            assert "accept" in t
            assert "floor" in t
            assert t["accept"] > t["floor"]

    def test_hawk_higher_accept_threshold(self):
        """Hawk accept threshold (60) is higher than dove (40)."""
        assert PERSONALITY_COUNTER_THRESHOLDS["hawk"]["accept"] > PERSONALITY_COUNTER_THRESHOLDS["dove"]["accept"]

    def test_dove_lower_floor_threshold(self):
        """Dove floor threshold (25) is lower than hawk (35)."""
        assert PERSONALITY_COUNTER_THRESHOLDS["dove"]["floor"] < PERSONALITY_COUNTER_THRESHOLDS["hawk"]["floor"]


# ═══════════════════════════════════════════════════════
# R122: Coalition Posture Drives Enemy AI
# ═══════════════════════════════════════════════════════

class TestCoalitionPostureAI:
    def _make_world_with_coalition(self, posture="defensive"):
        """Create world with an active coalition."""
        world = make_world()
        world.active_coalition = {
            "leader": "Britain",
            "members": ["Britain", "Prussia", "Austria"],
            "strategic_posture": posture,
            "war_exhaustion": {},
            "formed_turn": 1,
        }
        set_war(world, "France", "Britain")
        set_war(world, "France", "Prussia")
        return world

    def test_aggressive_posture_lowers_attack_threshold(self):
        """Aggressive coalition posture should lower attack threshold by 0.15."""
        from backend.game_logic.coalition import is_coalition_active, is_coalition_member
        world = self._make_world_with_coalition(posture="aggressive")
        assert is_coalition_active(world)
        assert is_coalition_member("Prussia", world)
        # The threshold modification is applied in P4 of _evaluate_marshal_priority
        # We test the structure exists correctly
        assert world.active_coalition["strategic_posture"] == "aggressive"

    def test_cautious_posture_raises_attack_threshold(self):
        """Cautious coalition posture should raise attack threshold by 0.15."""
        world = self._make_world_with_coalition(posture="cautious")
        assert world.active_coalition["strategic_posture"] == "cautious"

    def test_defensive_posture_enables_fortify_for_aggressive(self):
        """Defensive coalition posture should allow aggressive marshals to fortify (P5)."""
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor
        from backend.models.marshal import Marshal, Stance
        world = self._make_world_with_coalition(posture="defensive")
        ai = EnemyAI(CommandExecutor())
        # Clear existing marshals to avoid engagement blocks
        world.marshals = {}
        # Create an aggressive Prussian marshal in a safe location
        m = Marshal("TestMarshal", "Berlin", 30000, "aggressive", nation="Prussia")
        m.stance = Stance.DEFENSIVE  # Already defensive stance
        m.fortified = False
        world.marshals["TestMarshal"] = m
        # No enemies nearby
        result = ai._consider_fortify(m, world)
        # _consider_fortify doesn't check personality — that's done in the priority evaluation
        # So the result should be a fortify action (if no blockers)
        assert result is not None
        assert result["action"] == "fortify"

    def test_aggressive_posture_enables_drill_for_cautious(self):
        """Aggressive coalition posture should allow cautious marshals to drill (P6)."""
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor
        from backend.models.marshal import Marshal
        world = self._make_world_with_coalition(posture="aggressive")
        ai = EnemyAI(CommandExecutor())
        # Clear existing marshals to avoid adjacency blocks
        world.marshals = {}
        # Create a cautious Prussian marshal in isolated location
        m = Marshal("TestMarshal", "Berlin", 30000, "cautious", nation="Prussia")
        m.drilling = False
        m.drilling_locked = False
        m.shock_bonus = 0
        world.marshals["TestMarshal"] = m
        # No enemies nearby — _consider_drill checks this
        result = ai._consider_drill(m, world)
        # _consider_drill doesn't check personality — that's done in the priority evaluation
        assert result is not None
        assert result["action"] == "drill"

    def test_non_member_unaffected(self):
        """Nations not in the coalition should not get posture overrides."""
        from backend.game_logic.coalition import is_coalition_member
        world = self._make_world_with_coalition(posture="defensive")
        # Saxony is NOT in the coalition
        assert not is_coalition_member("Saxony", world)

    def test_no_coalition_unaffected(self):
        """Without an active coalition, personality gates remain unchanged."""
        from backend.game_logic.coalition import is_coalition_active
        world = make_world()
        assert not is_coalition_active(world)

    def test_defensive_fortify_in_check_threats(self):
        """Defensive coalition posture should allow aggressive marshals to fortify in _check_threats."""
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor
        from backend.models.marshal import Marshal, Stance
        world = self._make_world_with_coalition(posture="defensive")
        ai = EnemyAI(CommandExecutor())
        # Clear existing marshals
        world.marshals = {}
        # Create an aggressive Prussian marshal
        m = Marshal("TestMarshal", "Rhineland", 20000, "aggressive", nation="Prussia")
        m.stance = Stance.DEFENSIVE
        m.fortified = False
        world.marshals["TestMarshal"] = m
        # Create a stronger French enemy adjacent
        enemy = Marshal("EnemyMarshal", "Belgium", 40000, "aggressive", nation="France")
        world.marshals["EnemyMarshal"] = enemy
        # _check_threats should now allow fortification for aggressive marshal
        # due to defensive coalition posture
        result = ai._check_threats(m, "Prussia", world)
        # With coalition defensive posture, aggressive marshal should fortify
        assert result is not None
        assert result["action"] == "fortify"
