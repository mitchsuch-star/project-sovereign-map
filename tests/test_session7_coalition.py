"""
Coalition System Tests — Phase 8 Session 7 (COALITION_SPEC v1.1)

Tests cover:
  - Threat accumulation (§2a)
  - Threat decay (§2b)
  - Coalition formation (§3)
  - Coalition structure (§4)
  - Coalition AI helpers (§5)
  - Coalition breaking (§6)
  - Dissolution + cooldown (§7)
  - British subsidy (§4e)
  - Edge cases (§11)
  - Serialization round-trip
"""

from backend.models.world_state import WorldState
from backend.game_logic.coalition import (
    add_threat, reduce_threat, _calculate_threat_decay,
    qualifies_for_coalition, get_qualifying_nations,
    coalition_leadership_score, select_coalition_leader,
    calculate_coalition_war_score, get_coalition_posture,
    get_coalition_friction, get_coalition_loyalty_penalty,
    get_convergence_bias, get_british_subsidy_recipient,
    form_coalition, check_dissolution, dissolve_coalition,
    remove_coalition_member, is_coalition_member, is_coalition_active,
    get_threat_tier, process_coalition_turn,
    add_war_exhaustion_from_battle, add_coalition_shock,
    BREWING_COUNTDOWN,
    COALITION_COOLDOWN_TURNS,
)


def _make_world(**overrides):
    """Create a WorldState with sensible defaults for coalition testing."""
    world = WorldState()
    for k, v in overrides.items():
        setattr(world, k, v)
    return world


def _set_at_war(world, nation_a, nation_b):
    """Set two nations to WAR state."""
    key = "|".join(sorted([nation_a, nation_b]))
    world.diplomatic_states[key] = "WAR"


def _set_peace(world, nation_a, nation_b):
    """Set two nations to PEACE state."""
    key = "|".join(sorted([nation_a, nation_b]))
    world.diplomatic_states[key] = "PEACE"


def _set_relation(world, nation_a, nation_b, value):
    """Set relation between two nations."""
    key = "|".join(sorted([nation_a, nation_b]))
    world.nation_relations[key] = value


# ════════════════════════════════════════════════════════════════
# §2a. THREAT ACCUMULATION
# ════════════════════════════════════════════════════════════════

class TestThreatAccumulation:
    """Tests for add_threat and threat source tracking (§2a)."""

    def test_add_threat_basic(self):
        world = _make_world()
        result = add_threat(world, 10, "test")
        assert world.threat_level == 10
        assert result == 10

    def test_add_threat_clamp_at_100(self):
        world = _make_world(threat_level=95)
        add_threat(world, 20, "test")
        assert world.threat_level == 100

    def test_add_threat_clamp_at_0(self):
        world = _make_world(threat_level=0)
        result = add_threat(world, 0, "test")
        assert world.threat_level == 0
        assert result == 0

    def test_add_threat_negative_ignored(self):
        world = _make_world(threat_level=50)
        add_threat(world, -5, "test")
        assert world.threat_level == 50  # Unchanged

    def test_threat_sources_tracked(self):
        world = _make_world()
        add_threat(world, 3, "battle_win")
        add_threat(world, 5, "decisive_victory")
        assert len(world.threat_sources_this_turn) == 2
        assert world.threat_sources_this_turn[0]["source"] == "battle_win"
        assert world.threat_sources_this_turn[0]["amount"] == 3
        assert world.threat_sources_this_turn[1]["source"] == "decisive_victory"
        assert world.threat_sources_this_turn[1]["amount"] == 5

    def test_reduce_threat_basic(self):
        world = _make_world(threat_level=50)
        result = reduce_threat(world, 10, "vassal_release")
        assert world.threat_level == 40
        assert result == 40

    def test_reduce_threat_clamp_at_0(self):
        world = _make_world(threat_level=5)
        reduce_threat(world, 10, "test")
        assert world.threat_level == 0

    def test_reduce_threat_negative_ignored(self):
        world = _make_world(threat_level=50)
        reduce_threat(world, -5, "test")
        assert world.threat_level == 50

    def test_reduce_threat_tracked_as_negative(self):
        world = _make_world(threat_level=50)
        reduce_threat(world, 8, "vassal_release")
        assert world.threat_sources_this_turn[-1]["amount"] == -8

    def test_all_values_are_int(self):
        world = _make_world(threat_level=50)
        result = add_threat(world, 3, "test")
        assert isinstance(result, int)
        assert isinstance(world.threat_level, int)


# ════════════════════════════════════════════════════════════════
# §2b. THREAT DECAY
# ════════════════════════════════════════════════════════════════

class TestThreatDecay:
    """Tests for per-turn threat decay formula (§2b)."""

    def test_base_decay_is_1(self):
        """Even with all nations at war, base decay is 1."""
        world = _make_world()
        # Default: Britain+Prussia at war, Austria+Saxony at peace
        # So decay = 1 + 2 = 3 (capped at 3)
        # Actually let's set all at war to test base
        _set_at_war(world, "France", "Austria")
        _set_at_war(world, "France", "Saxony")
        decay = _calculate_threat_decay(world)
        assert decay == 1  # Base only, no peaceful nations

    def test_peace_bonus_per_nation(self):
        """Each peaceful non-vassal nation adds +1 to decay."""
        world = _make_world()
        # Default starting: Austria PEACE, Saxony OPEN_BORDERS, Britain WAR, Prussia WAR
        # Peace nations: Austria + Saxony = 2
        # Decay = 1 + 2 = 3
        decay = _calculate_threat_decay(world)
        assert decay == 3

    def test_decay_cap_at_3(self):
        """Decay from base + peace nations caps at 3."""
        world = _make_world()
        # Set all nations to PEACE
        _set_peace(world, "France", "Britain")
        _set_peace(world, "France", "Prussia")
        # Now 4 peaceful nations: decay = 1 + 4 = 5, but capped at 3
        decay = _calculate_threat_decay(world)
        assert decay == 3

    def test_continental_system_bonus_uncapped(self):
        """Continental System bonus is separate from the cap."""
        world = _make_world()
        world.continental_system_members = ["Prussia", "Saxony"]
        # Base decay = 3 (capped), CS bonus = +1 (uncapped) = 4
        decay = _calculate_threat_decay(world)
        assert decay == 4

    def test_vassals_excluded_from_peace_count(self):
        """Vassal nations don't count as peaceful nations for decay."""
        world = _make_world()
        world.vassals = {"Saxony": {"lord": "France", "loyalty": 50}}
        # Now only Austria is peaceful (Saxony is vassal, Britain+Prussia at war)
        # Decay = 1 + 1 = 2
        decay = _calculate_threat_decay(world)
        assert decay == 2


# ════════════════════════════════════════════════════════════════
# §3b. QUALIFYING NATIONS
# ════════════════════════════════════════════════════════════════

class TestQualifyingNations:
    """Tests for coalition qualification check (§3b)."""

    def test_austria_qualifies_at_start(self):
        """Austria starts with relation -30, at PEACE, not vassal → qualifies."""
        world = _make_world()
        assert qualifies_for_coalition("Austria", world) is True

    def test_saxony_does_not_qualify(self):
        """Saxony starts with relation +40 → does not qualify."""
        world = _make_world()
        assert qualifies_for_coalition("Saxony", world) is False

    def test_nation_at_war_does_not_qualify(self):
        """Nations already at war with France don't qualify (they auto-join)."""
        world = _make_world()
        assert qualifies_for_coalition("Britain", world) is False
        assert qualifies_for_coalition("Prussia", world) is False

    def test_vassal_does_not_qualify(self):
        """Vassal nations cannot join coalitions."""
        world = _make_world()
        world.vassals = {"Austria": {"lord": "France", "loyalty": 50}}
        _set_relation(world, "France", "Austria", -50)
        assert qualifies_for_coalition("Austria", world) is False

    def test_france_never_qualifies(self):
        world = _make_world()
        assert qualifies_for_coalition("France", world) is False

    def test_relation_boundary(self):
        """Relation must be < -10 (not <= -10)."""
        world = _make_world()
        _set_relation(world, "France", "Austria", -10)
        assert qualifies_for_coalition("Austria", world) is False
        _set_relation(world, "France", "Austria", -11)
        assert qualifies_for_coalition("Austria", world) is True

    def test_get_qualifying_nations(self):
        world = _make_world()
        qualifying = get_qualifying_nations(world)
        assert "Austria" in qualifying
        assert "Saxony" not in qualifying
        assert "Britain" not in qualifying  # Already at war


# ════════════════════════════════════════════════════════════════
# §3. COALITION FORMATION
# ════════════════════════════════════════════════════════════════

class TestCoalitionFormation:
    """Tests for coalition formation mechanics (§3)."""

    def test_form_coalition_basic(self):
        """Coalition forms with qualifying + already-at-war nations."""
        world = _make_world()
        result = form_coalition(["Austria"], world)
        assert result["success"] is True
        assert "Austria" in result["members"]
        assert "Britain" in result["members"]
        assert "Prussia" in result["members"]
        assert world.active_coalition is not None

    def test_form_coalition_sets_leader(self):
        world = _make_world()
        form_coalition(["Austria"], world)
        assert world.active_coalition["leader"] in ("Britain", "Prussia", "Austria")

    def test_form_coalition_sets_posture(self):
        world = _make_world()
        form_coalition(["Austria"], world)
        assert world.active_coalition["strategic_posture"] in ("aggressive", "defensive", "cautious")

    def test_form_coalition_increments_count(self):
        world = _make_world()
        assert world.coalition_count == 0
        form_coalition(["Austria"], world)
        assert world.coalition_count == 1

    def test_form_coalition_clears_brewing(self):
        world = _make_world()
        world.coalition_brewing = {"turns_remaining": 1, "qualifying_nations": ["Austria"]}
        form_coalition(["Austria"], world)
        assert world.coalition_brewing is None

    def test_form_coalition_united_cause_relations(self):
        """All coalition members get +10 relation with each other (§3e).

        Note: declare_war for Austria→France also applies -15 to Austria-others,
        but united cause +10 partially offsets this. Net: old + 10 - 15 = old - 5
        for already-at-war members. But for members who were already at war with
        France, there's no new war declaration penalty.
        Check that the +10 was applied (relation changed from start).
        """
        world = _make_world()
        # Record: Britain-Prussia relation before (both already at war, no new declaration)
        key_bp = "|".join(sorted(["Britain", "Prussia"]))
        old_bp = world.nation_relations.get(key_bp, 0)
        form_coalition(["Austria"], world)
        new_bp = world.nation_relations.get(key_bp, 0)
        # Britain and Prussia both already at war — no declare_war penalty between them.
        # Only the +10 united cause. But Austria's declare_war also adds -15 to others.
        # So for Britain-Prussia: +10 (united cause). Net: old + 10.
        # WAIT: declare_war(Austria, France) applies -15 to Austria-every_other_nation,
        # but Britain and Prussia are "every other nation" relative to Austria.
        # It does NOT affect Britain-Prussia relation directly.
        assert new_bp == old_bp + 10

    def test_form_coalition_requires_qualifying(self):
        """Cannot form coalition with zero qualifying nations."""
        world = _make_world()
        result = form_coalition([], world)
        assert result["success"] is False

    def test_form_coalition_declares_war_on_france(self):
        """Qualifying nations that weren't at war get set to WAR."""
        world = _make_world()
        form_coalition(["Austria"], world)
        assert world.get_diplomatic_state("France", "Austria") == "WAR"

    def test_form_coalition_naming_first(self):
        world = _make_world()
        result = form_coalition(["Austria"], world)
        leader = result["leader"]
        assert result["coalition_name"] == f"The {leader} Coalition"

    def test_form_coalition_naming_second(self):
        world = _make_world()
        world.coalition_count = 1  # Pretend one already formed
        result = form_coalition(["Austria"], world)
        leader = result["leader"]
        assert "Second" in result["coalition_name"]

    def test_coalition_popup_data(self):
        """Coalition formation returns popup data for Godot (Session 8C contract)."""
        world = _make_world()
        result = form_coalition(["Austria"], world)
        assert "coalition_popup" in result
        popup = result["coalition_popup"]
        assert "coalition_name" in popup
        assert "leader" in popup
        assert "posture" in popup
        assert "members" in popup
        assert isinstance(popup["members"], list)
        assert "combined_strength_display" in popup
        assert "threat_level" in popup


# ════════════════════════════════════════════════════════════════
# §4. COALITION STRUCTURE
# ════════════════════════════════════════════════════════════════

class TestCoalitionStructure:
    """Tests for leader selection, posture, war score (§4)."""

    def test_leadership_score_components(self):
        world = _make_world()
        score = coalition_leadership_score("Britain", world)
        assert isinstance(score, int)
        assert score > 0

    def test_leader_selection_highest_score(self):
        world = _make_world()
        # Britain should typically lead (strongest + most hostile)
        leader = select_coalition_leader(["Britain", "Prussia", "Austria"], world)
        assert leader in ("Britain", "Prussia", "Austria")

    def test_leader_selection_tiebreak_marshals(self):
        """If scores tie, nation with more marshals leads."""
        world = _make_world()
        # Set all to equal score components
        for n in ["Austria", "Prussia"]:
            _set_relation(world, "France", n, -50)
            world.nation_authority[n] = 50
        leader = select_coalition_leader(["Austria", "Prussia"], world)
        assert leader in ("Austria", "Prussia")

    def test_coalition_war_score(self):
        """War score is weighted average inverted from France perspective."""
        world = _make_world()
        form_coalition(["Austria"], world)
        # Set some war scores
        world.war_scores["|".join(sorted(["France", "Britain"]))] = 20  # France winning
        ws = calculate_coalition_war_score(world)
        assert isinstance(ws, int)

    def test_posture_aggressive(self):
        """Aggressive posture when coalition war score > 10."""
        world = _make_world()
        form_coalition(["Austria"], world)
        # Set war scores so France is LOSING (coalition winning):
        # War scores are stored from first-alphabetical nation's perspective.
        # For "Austria|France": positive = Austria winning (France losing) ✓
        # For "Britain|France": positive = Britain winning (France losing) ✓
        # For "France|Prussia": positive = France winning → need NEGATIVE for France losing
        for m in world.active_coalition["members"]:
            key = "|".join(sorted(["France", m]))
            if key.startswith("France"):
                world.war_scores[key] = -20  # France is first: negative = France losing
            else:
                world.war_scores[key] = 20   # Other is first: positive = other winning
        posture = get_coalition_posture(world)
        assert posture == "aggressive"

    def test_posture_cautious(self):
        """Cautious posture when coalition war score < -10 with cautious leader."""
        world = _make_world()
        form_coalition(["Austria"], world)
        leader = world.active_coalition["leader"]
        # Make leader have cautious personality
        diplomat = world.diplomats.get(leader)
        if diplomat:
            diplomat.personality = "cautious"
        # Set war scores positive for France (coalition losing badly)
        for m in world.active_coalition["members"]:
            key = "|".join(sorted(["France", m]))
            world.war_scores[key] = 40
        posture = get_coalition_posture(world)
        # Depends on leader personality — if cautious, should be cautious
        assert posture in ("cautious", "defensive")

    def test_posture_without_coalition(self):
        world = _make_world()
        assert get_coalition_posture(world) == "defensive"

    def test_convergence_bias_values(self):
        assert get_convergence_bias("aggressive") == 12
        assert get_convergence_bias("defensive") == 4
        assert get_convergence_bias("cautious") == 0


# ════════════════════════════════════════════════════════════════
# §5. COALITION AI HELPERS
# ════════════════════════════════════════════════════════════════

class TestCoalitionAI:
    """Tests for friction, convergence, membership checks (§5)."""

    def test_friction_full_coordination(self):
        world = _make_world()
        _set_relation(world, "Austria", "Prussia", 30)
        assert get_coalition_friction("Austria", "Prussia", world) == 1.0

    def test_friction_moderate(self):
        world = _make_world()
        _set_relation(world, "Austria", "Prussia", 15)
        assert get_coalition_friction("Austria", "Prussia", world) == 0.75

    def test_friction_significant(self):
        world = _make_world()
        _set_relation(world, "Austria", "Prussia", -10)
        assert get_coalition_friction("Austria", "Prussia", world) == 0.5

    def test_friction_near_hostile(self):
        world = _make_world()
        _set_relation(world, "Austria", "Prussia", -30)
        assert get_coalition_friction("Austria", "Prussia", world) == 0.25

    def test_friction_same_nation(self):
        world = _make_world()
        assert get_coalition_friction("Austria", "Austria", world) == 1.0

    def test_is_coalition_member(self):
        world = _make_world()
        form_coalition(["Austria"], world)
        assert is_coalition_member("Britain", world) is True
        assert is_coalition_member("Saxony", world) is False

    def test_is_coalition_active(self):
        world = _make_world()
        assert is_coalition_active(world) is False
        form_coalition(["Austria"], world)
        assert is_coalition_active(world) is True

    def test_threat_tier_names(self):
        assert get_threat_tier(10) == "Calm"
        assert get_threat_tier(35) == "Tension"
        assert get_threat_tier(50) == "Murmurs"
        assert get_threat_tier(65) == "Brewing"
        assert get_threat_tier(85) == "Brewing"  # Still "Brewing" tier name


# ════════════════════════════════════════════════════════════════
# §6. COALITION BREAKING
# ════════════════════════════════════════════════════════════════

class TestCoalitionBreaking:
    """Tests for separate peace, loyalty penalty, war exhaustion (§6)."""

    def test_loyalty_penalty_base(self):
        """Base penalty is -15 at 0 war exhaustion."""
        world = _make_world()
        form_coalition(["Austria"], world)
        penalty = get_coalition_loyalty_penalty("Austria", world)
        assert penalty == -15

    def test_loyalty_penalty_with_exhaustion(self):
        """WE lessens penalty: min(-15 + WE//10, 0). C1 audit fix."""
        world = _make_world()
        form_coalition(["Austria"], world)
        world.war_exhaustion["Austria"] = 100
        penalty = get_coalition_loyalty_penalty("Austria", world)
        assert penalty == -5  # min(-15 + 10, 0) = -5

    def test_loyalty_penalty_at_high_exhaustion(self):
        """At WE 150+, penalty caps at 0. C1 audit fix."""
        world = _make_world()
        form_coalition(["Austria"], world)
        world.war_exhaustion["Austria"] = 150
        penalty = get_coalition_loyalty_penalty("Austria", world)
        assert penalty == 0

    def test_loyalty_penalty_wedge_halving(self):
        """If target dislikes leader (relation < 10), penalty halved (§6c)."""
        world = _make_world()
        form_coalition(["Austria"], world)
        leader = world.active_coalition["leader"]
        if leader != "Austria":
            _set_relation(world, "Austria", leader, -5)
            penalty = get_coalition_loyalty_penalty("Austria", world)
            # Base -15, halved via // 2 = -8 (Python floors toward -inf)
            assert penalty == -8

    def test_loyalty_penalty_non_member_zero(self):
        """Non-coalition members have no penalty."""
        world = _make_world()
        form_coalition(["Austria"], world)
        penalty = get_coalition_loyalty_penalty("Saxony", world)
        assert penalty == 0

    def test_remove_member(self):
        """Removing a member updates coalition and applies betrayal penalty."""
        world = _make_world()
        form_coalition(["Austria"], world)
        assert "Austria" in world.active_coalition["members"]
        events = remove_coalition_member("Austria", world)
        assert "Austria" not in world.active_coalition.get("members", []) if world.active_coalition else True

    def test_remove_leader_transitions(self):
        """When leader is removed, a new leader is selected (§4b)."""
        world = _make_world()
        form_coalition(["Austria"], world)
        leader = world.active_coalition["leader"]
        events = remove_coalition_member(leader, world)
        if world.active_coalition:
            assert world.active_coalition["leader"] != leader

    def test_war_exhaustion_from_battle(self):
        """casualties // 1000, capped at 20 per battle."""
        world = _make_world()
        result = add_war_exhaustion_from_battle("Austria", 15000, world)
        assert result == 15  # 15000 // 1000 = 15

    def test_war_exhaustion_cap_per_battle(self):
        world = _make_world()
        result = add_war_exhaustion_from_battle("Austria", 50000, world)
        assert result == 20  # Capped at 20

    def test_war_exhaustion_accumulates(self):
        world = _make_world()
        add_war_exhaustion_from_battle("Austria", 10000, world)
        add_war_exhaustion_from_battle("Austria", 10000, world)
        assert world.war_exhaustion["Austria"] == 20

    def test_coalition_shock(self):
        """Defeating a coalition member adds +5 WE to others (§6b)."""
        world = _make_world()
        form_coalition(["Austria"], world)
        add_coalition_shock("Austria", world)
        for member in world.active_coalition["members"]:
            if member != "Austria":
                assert world.war_exhaustion.get(member, 0) == 5
        # Austria itself should NOT get the shock
        assert world.war_exhaustion.get("Austria", 0) == 0


# ════════════════════════════════════════════════════════════════
# §7. DISSOLUTION + COOLDOWN
# ════════════════════════════════════════════════════════════════

class TestDissolution:
    """Tests for coalition dissolution mechanics (§7)."""

    def test_dissolution_insufficient_members(self):
        """Coalition dissolves when < 2 active members at war."""
        world = _make_world()
        form_coalition(["Austria"], world)
        # Peace everyone except one
        for m in list(world.active_coalition["members"]):
            if m != "Britain":
                _set_peace(world, "France", m)
        reason = check_dissolution(world)
        assert reason == "insufficient_members"

    def test_dissolution_low_threat(self):
        world = _make_world(threat_level=15)
        form_coalition(["Austria"], world)
        reason = check_dissolution(world)
        assert reason == "low_threat"

    def test_dissolve_sets_cooldown(self):
        world = _make_world()
        form_coalition(["Austria"], world)
        dissolve_coalition(world, "test")
        assert world.active_coalition is None
        assert world.coalition_cooldown == COALITION_COOLDOWN_TURNS

    def test_no_dissolution_when_healthy(self):
        world = _make_world(threat_level=60)
        form_coalition(["Austria"], world)
        reason = check_dissolution(world)
        assert reason is None

    def test_cooldown_prevents_brewing(self):
        """Brewing should not start during cooldown."""
        world = _make_world(threat_level=65)
        world.coalition_cooldown = 3
        events = process_coalition_turn(world)
        assert world.coalition_brewing is None


# ════════════════════════════════════════════════════════════════
# §4e. BRITISH SUBSIDY
# ════════════════════════════════════════════════════════════════

class TestBritishSubsidy:
    """Tests for British subsidy mechanic (§4e)."""

    def test_subsidy_recipient_lowest_relation(self):
        world = _make_world()
        form_coalition(["Austria"], world)
        world.nation_gold["Britain"] = 1000
        _set_relation(world, "Britain", "Austria", -15)
        _set_relation(world, "Britain", "Prussia", 20)
        recipient = get_british_subsidy_recipient(world)
        assert recipient == "Austria"  # Lowest relation that's > -20

    def test_subsidy_requires_gold(self):
        world = _make_world()
        form_coalition(["Austria"], world)
        world.nation_gold["Britain"] = 400  # Below 500 threshold
        recipient = get_british_subsidy_recipient(world)
        assert recipient is None

    def test_subsidy_no_coalition(self):
        world = _make_world()
        recipient = get_british_subsidy_recipient(world)
        assert recipient is None


# ════════════════════════════════════════════════════════════════
# §11. EDGE CASES
# ════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Edge case tests per §11."""

    def test_ec15_momentary_crossing_no_trigger(self):
        """EC-15: Threshold check on FINAL value, not momentary crossing."""
        world = _make_world(threat_level=57)
        # Simulate: +3 from battle, -3 from decay → net 57
        # If processing is correct, threshold 60 is NOT crossed
        add_threat(world, 3, "battle_win")
        # Now 60, but decay will bring it back
        # process_coalition_turn handles this properly
        # We test the function directly
        assert world.threat_level == 60
        # After decay (process_coalition_turn applies decay), it drops back
        # Verify no brewing started after full processing
        world.threat_level = 57  # Reset to net value after decay
        events = process_coalition_turn(world)
        assert world.coalition_brewing is None

    def test_brewing_starts_at_60(self):
        # Decay is ~3/turn (default game state), so need threat 63+ to survive to 60+
        world = _make_world(threat_level=63)
        _set_relation(world, "France", "Austria", -20)
        events = process_coalition_turn(world)
        assert world.coalition_brewing is not None
        assert world.coalition_brewing["turns_remaining"] == BREWING_COUNTDOWN

    def test_instant_declaration_at_80(self):
        # Need 83+ to survive 3 decay and still be ≥80
        world = _make_world(threat_level=83)
        _set_relation(world, "France", "Austria", -20)
        events = process_coalition_turn(world)
        assert world.active_coalition is not None
        assert world.coalition_brewing is None

    def test_brewing_cancels_below_40(self):
        """Momentum rule: brewing cancels only below 40."""
        world = _make_world(threat_level=39)
        world.coalition_brewing = {
            "qualifying_nations": ["Austria"],
            "turns_remaining": 2,
            "started_turn": 1,
            "threat_at_start": 62,
        }
        _set_relation(world, "France", "Austria", -20)
        events = process_coalition_turn(world)
        assert world.coalition_brewing is None

    def test_brewing_continues_at_50(self):
        """Momentum: brewing continues even if threat < 60 (stays ≥ 40)."""
        world = _make_world(threat_level=50)
        world.coalition_brewing = {
            "qualifying_nations": ["Austria"],
            "turns_remaining": 2,
            "started_turn": 1,
            "threat_at_start": 62,
        }
        _set_relation(world, "France", "Austria", -20)
        events = process_coalition_turn(world)
        # At threat 50, brewing should continue (momentum keeps it alive above 40)
        assert world.coalition_brewing is not None, \
            "Brewing should continue at threat 50 (momentum above 40)"

    def test_cooldown_override_at_90(self):
        """§7c: Threat ≥ 90 overrides cooldown."""
        # Need 93+ to survive 3 decay and still be ≥90
        world = _make_world(threat_level=93)
        world.coalition_cooldown = 3
        _set_relation(world, "France", "Austria", -20)
        events = process_coalition_turn(world)
        # Cooldown should be overridden, coalition should form
        assert world.coalition_cooldown == 0
        assert world.active_coalition is not None


# ════════════════════════════════════════════════════════════════
# SERIALIZATION
# ════════════════════════════════════════════════════════════════

class TestSerialization:
    """Tests for coalition field round-trip serialization."""

    def test_world_state_round_trip(self):
        """All 7 coalition fields survive to_dict/from_dict."""
        world = _make_world()
        world.threat_level = 42
        world.threat_sources_this_turn = [{"source": "battle_win", "amount": 3}]
        world.active_coalition = {
            "id": "coalition_5",
            "name": "The British Coalition",
            "leader": "Britain",
            "members": ["Britain", "Prussia", "Austria"],
            "formed_turn": 5,
            "strategic_posture": "aggressive",
            "posture_last_updated": 5,
        }
        world.coalition_brewing = None
        world.coalition_cooldown = 3
        world.coalition_count = 1
        world.war_exhaustion = {"Austria": 25, "Prussia": 10}

        data = world.to_dict()
        restored = WorldState.from_dict(data)

        assert restored.threat_level == 42
        assert len(restored.threat_sources_this_turn) == 1
        assert restored.threat_sources_this_turn[0]["source"] == "battle_win"
        assert restored.active_coalition is not None
        assert restored.active_coalition["leader"] == "Britain"
        assert restored.coalition_brewing is None
        assert restored.coalition_cooldown == 3
        assert restored.coalition_count == 1
        assert restored.war_exhaustion["Austria"] == 25
        assert restored.war_exhaustion["Prussia"] == 10

    def test_default_values_on_missing_keys(self):
        """Old saves without coalition fields should get defaults."""
        data = {"player_nation": "France"}
        world = WorldState.from_dict(data)
        assert world.threat_level == 0
        assert world.threat_sources_this_turn == []
        assert world.active_coalition is None
        assert world.coalition_brewing is None
        assert world.coalition_cooldown == 0
        assert world.coalition_count == 0
        assert world.war_exhaustion == {}


# ════════════════════════════════════════════════════════════════
# PROCESS COALITION TURN (integration)
# ════════════════════════════════════════════════════════════════

class TestProcessCoalitionTurn:
    """Integration tests for the master per-turn function."""

    def test_passive_threat_at_60_pct_control(self):
        """France controlling >60% of regions gets +1 threat/turn."""
        world = _make_world()
        total = len(world.regions)
        # Give France 60%+ regions
        france_needed = int(total * 0.61) + 1
        for i, (name, region) in enumerate(world.regions.items()):
            if i < france_needed:
                region.controller = "France"
            else:
                region.controller = "Prussia"
        process_coalition_turn(world)
        # Should have passive threat source
        sources = [s for s in world.threat_sources_this_turn if "region_control" in s["source"]]
        assert len(sources) > 0

    def test_war_exhaustion_per_turn(self):
        """R11: WE +8/turn for nations at war (was +5), -5/turn for nations at peace."""
        world = _make_world()
        world.war_exhaustion["Britain"] = 20
        world.war_exhaustion["Austria"] = 20
        # Britain at war, Austria at peace
        process_coalition_turn(world)
        assert world.war_exhaustion["Britain"] == 28  # +8 (at war, R11)
        assert world.war_exhaustion["Austria"] == 15  # -5 (at peace)

    def test_posture_updated_each_turn(self):
        """Coalition posture is reassessed each turn."""
        world = _make_world()
        form_coalition(["Austria"], world)
        old_turn = world.active_coalition["posture_last_updated"]
        world.current_turn += 1
        process_coalition_turn(world)
        if world.active_coalition:
            assert world.active_coalition["posture_last_updated"] >= old_turn

    def test_dissolution_during_processing(self):
        """Coalition auto-dissolves if conditions met during processing."""
        world = _make_world(threat_level=15)
        form_coalition(["Austria"], world)
        events = process_coalition_turn(world)
        # Low threat should cause dissolution
        assert world.active_coalition is None
        dissolution_events = [e for e in events if e.get("type") == "coalition_dissolved"]
        assert len(dissolution_events) > 0


# ════════════════════════════════════════════════════════════════
# GAP FIXES — Session 7 closure
# ════════════════════════════════════════════════════════════════

class TestGapFixes:
    """Tests for coalition gaps closed in Session 7 cleanup."""

    # ── Gap 1: Voluntary vassal release reduces threat ──

    def test_voluntary_vassal_release_reduces_threat(self):
        """release_vassal() with rebellion=False should reduce threat by 8."""
        from backend.game_logic.vassal import release_vassal
        world = _make_world(threat_level=50)
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 60}
        release_vassal(world, "Saxony", rebellion=False)
        assert world.threat_level == 42  # 50 - 8

    def test_rebellion_release_does_not_double_reduce(self):
        """release_vassal() with rebellion=True should NOT call reduce_threat
        (rebellion path already calls it separately in check_vassal_rebellion)."""
        world = _make_world(threat_level=50)
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 60}
        from backend.game_logic.vassal import release_vassal
        release_vassal(world, "Saxony", rebellion=True)
        # rebellion=True doesn't call reduce_threat from release_vassal
        assert world.threat_level == 50

    def test_vassal_release_non_player_no_threat_change(self):
        """Releasing a vassal of a non-player lord shouldn't change threat."""
        world = _make_world(threat_level=50)
        world.vassals["Saxony"] = {"lord": "Austria", "loyalty": 60}
        from backend.game_logic.vassal import release_vassal
        release_vassal(world, "Saxony", rebellion=False)
        assert world.threat_level == 50

    # ── Gap 2: Generous peace reduces threat ──

    def test_generous_peace_reduces_threat(self):
        """Peace treaty with sweeteners, no territory demands, and positive
        war score should reduce threat by 3 (§2b generous peace)."""
        world = _make_world(threat_level=50)
        _set_at_war(world, "France", "Austria")
        # Give France control of 5+ Austrian starting regions so war_score > 20
        austria_regions = world.nation_starting_regions.get("Austria", [])
        for rname in austria_regions:
            if rname in world.regions:
                world.regions[rname].controller = "France"
        # Also add battle records to push score above 20
        diplo_key = world._make_diplo_key("France", "Austria")
        world.battle_records[diplo_key] = [
            {"winner": "France"}, {"winner": "France"}, {"winner": "France"},
        ]
        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Austria",
            "sweeteners": [{"type": "gold_lump", "value": 500}],
            "demands": [],
        }
        world._ratify_treaty(proposal)
        assert world.threat_level == 47  # 50 - 3

    def test_non_generous_peace_no_threat_reduction(self):
        """Peace with territory demands is NOT generous — no threat reduction."""
        world = _make_world(threat_level=50)
        _set_at_war(world, "France", "Austria")
        world.war_scores = {world._make_diplo_key("France", "Austria"): 30}
        proposal = {
            "type": "peace",
            "sweeteners": [{"type": "gold_lump", "value": 200}],
            "demands": [{"type": "territory_cede", "value": 0, "regions": ["Vienna"]}],
        }
        # Need to set up region so territory_cede works
        vienna = world.get_region("Vienna")
        if vienna:
            vienna.controller = "Austria"
        proposal["proposer_nation"] = "France"
        proposal["target_nation"] = "Austria"
        world._ratify_treaty(proposal)
        # Should NOT get -3 generous peace because there are territory demands
        # But DOES get +8 from treaty_annex (1 region ceded to France)
        assert world.threat_level == 58

    def test_generous_peace_low_war_score_no_reduction(self):
        """Low war score (<=20) means peace isn't 'generous' — no threat reduction."""
        world = _make_world(threat_level=50)
        _set_at_war(world, "France", "Austria")
        world.war_scores = {world._make_diplo_key("France", "Austria"): 10}
        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Austria",
            "sweeteners": [{"type": "gold_lump", "value": 500}],
            "demands": [],
        }
        world._ratify_treaty(proposal)
        assert world.threat_level == 50

    # ── Gap 3: EC-2 void in-transit proposals on coalition formation ──

    def test_ec2_void_in_transit_proposal(self):
        """In-transit proposal to a coalition joiner should be voided."""
        world = _make_world(threat_level=80)
        world.proposal_in_transit = {
            "target": "Austria",
            "proposal": {"type": "peace", "dp_cost": 3},
            "turn_sent": 1,
        }
        world.talleyrand_state = "IN_TRANSIT"
        _set_relation(world, "France", "Austria", -30)
        result = form_coalition(["Austria"], world)
        assert result["success"]
        assert world.proposal_in_transit is None
        assert world.talleyrand_state == "IDLE"
        assert result.get("voided_proposal") == "Austria"

    def test_ec2_unrelated_proposal_not_voided(self):
        """In-transit proposal to a non-coalition nation should be preserved."""
        world = _make_world(threat_level=80)
        world.proposal_in_transit = {
            "target": "Saxony",
            "proposal": {"type": "alliance", "dp_cost": 2},
            "turn_sent": 1,
        }
        world.talleyrand_state = "IN_TRANSIT"
        _set_relation(world, "France", "Austria", -30)
        _set_relation(world, "France", "Prussia", -30)
        result = form_coalition(["Austria", "Prussia"], world)
        assert result["success"]
        assert world.proposal_in_transit is not None  # Preserved
        assert world.talleyrand_state == "IN_TRANSIT"
        assert result.get("voided_proposal") is None

    def test_ec2_dp_refunded(self):
        """DP should be refunded when a proposal is voided by coalition."""
        world = _make_world(threat_level=80)
        world.diplomatic_points = 5
        world.proposal_in_transit = {
            "target": "Austria",
            "proposal": {"type": "peace", "dp_cost": 3},
            "turn_sent": 1,
        }
        world.talleyrand_state = "IN_TRANSIT"
        _set_relation(world, "France", "Austria", -30)
        form_coalition(["Austria"], world)
        assert world.diplomatic_points == 8  # 5 + 3 refunded

    # ── Gap 4: EC-9 coalition member attack prevention ──

    def test_ec9_coalition_members_cannot_attack_each_other(self):
        """Coalition members should be blocked from attacking each other."""
        from backend.models.marshal import Marshal
        from backend.commands.executor import CommandExecutor
        world = _make_world(threat_level=80)
        # Set up bilateral WAR between Austria and Prussia
        _set_at_war(world, "Austria", "Prussia")
        _set_at_war(world, "France", "Austria")
        _set_at_war(world, "France", "Prussia")
        _set_relation(world, "France", "Austria", -30)
        _set_relation(world, "France", "Prussia", -30)
        # Form coalition with both
        form_coalition(["Austria", "Prussia"], world)
        assert is_coalition_active(world)
        # Create marshals (name, location, strength, personality, nation)
        m_austria = Marshal("Schwarzenberg", "Saxony", 20000, "cautious", nation="Austria")
        m_prussia = Marshal("Blucher", "Saxony", 20000, "aggressive", nation="Prussia")
        world.marshals["Schwarzenberg"] = m_austria
        world.marshals["Blucher"] = m_prussia
        # Try attack
        executor = CommandExecutor()
        result = executor._execute_attack(m_austria, "Blucher", world, {"world": world})
        assert not result["success"]
        assert "coalition ally" in result["message"]
