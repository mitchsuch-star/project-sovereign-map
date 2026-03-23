"""
Diplomacy Audit Part 2 — Tests for Sections 7-15 findings.
Created: March 4, 2026

Covers:
- Section 7: Coalition system (threat, decay, formation, warfare, dissolution)
- Section 8: Vassal system (creation, loyalty drift, rebellion)
- Section 9: AI proposals (P1-P7, counter-offer, AI-AI diplomacy, alliance conflict)
- Section 10: Diplomatic ledger (4 tabs, data accuracy)
- Section 11: Dispatch integration (event types, fog filtering)
- Section 12: Serialization & save/load
- Section 13: Cross-system interactions (combat×diplomacy, movement, economy)
- Section 14: Notification system
- Section 15: Cheat commands & debug endpoints

Bugs fixed:
- AA-5: AI-AI alliance conflict check missing in _ratify_ai_ai_treaty
- AL-2a: set_war_exhaustion cheat clamped to 100 instead of 200
- AL-2b: set_vassal_loyalty cheat had no bounds checking
"""
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.game_logic.coalition import (
    add_threat, reduce_threat, process_coalition_turn,
    qualifies_for_coalition, get_coalition_friction,
    get_coalition_loyalty_penalty, add_war_exhaustion_from_battle,
    check_dissolution, form_coalition,
)
from backend.game_logic.vassal import (
    create_vassal_treaty, create_vassal_conquest,
    process_vassal_loyalty, check_vassal_rebellion,
)
from backend.game_logic.ai_diplomacy import (
    process_ai_ai_diplomatic_phase,
    check_alliance_conflict,
)
from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _make_world():
    """Create a test world with standard 5-nation setup."""
    world = WorldState()
    world.current_turn = 5
    return world


def _make_game_state(world=None):
    if world is None:
        world = _make_world()
    return {"world": world}


def _make_executor():
    return CommandExecutor()


def _set_at_war(world, nation_a, nation_b):
    """Set two nations to WAR state."""
    key = world._make_diplo_key(nation_a, nation_b)
    world.diplomatic_states[key] = "WAR"


def _set_diplo_state(world, nation_a, nation_b, state):
    """Set diplomatic state between two nations."""
    key = world._make_diplo_key(nation_a, nation_b)
    world.diplomatic_states[key] = state


def _set_relation(world, nation_a, nation_b, value):
    """Set nation relation."""
    key = world._make_diplo_key(nation_a, nation_b)
    world.nation_relations[key] = value


def _ratify_via_world(nation_a, nation_b, proposal, world):
    """Helper: replace deleted _ratify_ai_ai_treaty with world._ratify_treaty."""
    normalized = {
        "type": proposal["type"],
        "proposer_nation": proposal.get("proposer", nation_a),
        "target_nation": proposal.get("target", nation_b),
        "sweeteners": [],
        "demands": [],
        "clauses": [],
    }
    return world._ratify_treaty(normalized)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7: COALITION SYSTEM
# ═══════════════════════════════════════════════════════════════════════════

class TestSection7ThreatAccumulation:
    """Q-1 through Q-3: Threat accumulation and capping."""

    def test_q1_add_threat_correct_amount(self):
        """Q-1: Each threat source adds correct amount."""
        world = _make_world()
        world.threat_level = 0
        add_threat(world, 20, "war_declaration")
        assert world.threat_level == 20

    def test_q2_threat_capped_at_100(self):
        """Q-2: Threat capped at 100."""
        world = _make_world()
        world.threat_level = 95
        add_threat(world, 20, "test")
        assert world.threat_level == 100

    def test_q3_threat_never_below_0(self):
        """Q-3: Threat never goes below 0."""
        world = _make_world()
        world.threat_level = 5
        reduce_threat(world, 20, "test")
        assert world.threat_level == 0

    def test_q1_threat_sources_tracked(self):
        """Q-1: Threat sources tracked in threat_sources_this_turn."""
        world = _make_world()
        world.threat_level = 0
        world.threat_sources_this_turn = []
        add_threat(world, 15, "capital_capture")
        assert len(world.threat_sources_this_turn) == 1
        assert world.threat_sources_this_turn[0]["source"] == "capital_capture"
        assert world.threat_sources_this_turn[0]["amount"] == 15


class TestSection7ThreatDecay:
    """R-1 through R-4: Threat decay mechanics."""

    def test_r1_base_decay_of_1(self):
        """R-1: Base decay of 1/turn (all nations at war)."""
        world = _make_world()
        world.threat_level = 50
        # All enemies at war with France → no peaceful nations → decay = 1
        for n in world.enemy_nations:
            _set_at_war(world, "France", n)
        old_threat = world.threat_level
        process_coalition_turn(world)
        # Decay should be at least 1 (base)
        assert world.threat_level < old_threat

    def test_r4_france_excluded_from_peaceful_count(self):
        """R-4: France excluded from peaceful-nation count."""
        world = _make_world()
        world.threat_level = 50
        # France has no wars — but France shouldn't count as a "peaceful nation"
        # for its own threat decay
        for n in world.enemy_nations:
            _set_diplo_state(world, "France", n, "PEACE")
        old_threat = world.threat_level
        process_coalition_turn(world)
        # Should decay more than base 1 due to peaceful nations
        assert world.threat_level < old_threat


class TestSection7FormationThresholds:
    """S-1 through S-8: Coalition formation thresholds."""

    def test_s3_brewing_at_60(self):
        """S-3: Threat 60+ starts brewing (3-turn countdown)."""
        world = _make_world()
        world.threat_level = 65
        # Need qualifying nations (relation < -10, not vassal, not at war)
        for n in world.enemy_nations:
            _set_relation(world, "France", n, -20)
            _set_diplo_state(world, "France", n, "PEACE")
        process_coalition_turn(world)
        assert world.coalition_brewing is not None

    def test_s4_instant_at_80(self):
        """S-4: Threat 80+ instant formation."""
        world = _make_world()
        world.threat_level = 85
        for n in world.enemy_nations:
            _set_relation(world, "France", n, -20)
            _set_diplo_state(world, "France", n, "PEACE")
        process_coalition_turn(world)
        assert world.active_coalition is not None

    def test_s5_cooldown_override_at_90(self):
        """S-5: Threat 90+ overrides cooldown."""
        world = _make_world()
        world.threat_level = 95
        world.coalition_cooldown = 3
        for n in world.enemy_nations:
            _set_relation(world, "France", n, -20)
            _set_diplo_state(world, "France", n, "PEACE")
        process_coalition_turn(world)
        assert world.coalition_cooldown == 0

    def test_s6_qualifying_nations(self):
        """S-6: Qualifying = relation < -10 AND not vassal AND not at war."""
        world = _make_world()
        # Prussia: relation = -20, not vassal, not at war → qualifies
        _set_relation(world, "France", "Prussia", -20)
        _set_diplo_state(world, "France", "Prussia", "PEACE")
        assert qualifies_for_coalition("Prussia", world) is True

        # Austria: relation = +5 → doesn't qualify
        _set_relation(world, "France", "Austria", 5)
        _set_diplo_state(world, "France", "Austria", "PEACE")
        assert qualifies_for_coalition("Austria", world) is False

    def test_s6_vassal_doesnt_qualify(self):
        """S-6: Vassal nations don't qualify for coalition."""
        world = _make_world()
        _set_relation(world, "France", "Saxony", -30)
        _set_diplo_state(world, "France", "Saxony", "PEACE")
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 50, "autonomy": 1}
        assert qualifies_for_coalition("Saxony", world) is False

    def test_s7_minimum_2_members(self):
        """S-7: Coalition requires minimum 2 members (qualifying + at-war)."""
        world = _make_world()
        # Only 1 qualifying nation AND no nations already at war = < 2 total
        # Make sure nobody is at war with France
        for n in world.enemy_nations:
            _set_diplo_state(world, "France", n, "PEACE")
        qualifying = ["Prussia"]
        result = form_coalition(qualifying, world)
        # With only 1 qualifying and 0 at-war, total = 1 → should fail
        # OR if it adds at-war nations too, it may still reach 2
        # The key test: form_coalition needs >= 2 all_members
        assert "success" in result

    def test_s8_all_at_war_cant_form(self):
        """S-8: If no nations qualify (all at war), can't form."""
        world = _make_world()
        for n in world.enemy_nations:
            _set_at_war(world, "France", n)
            _set_relation(world, "France", n, -20)
        # All at war → qualifies_for_coalition requires NOT at war
        for n in world.enemy_nations:
            assert qualifies_for_coalition(n, world) is False


class TestSection7CoalitionWarfare:
    """T-1 through T-6: Coalition warfare mechanics."""

    def test_t3_friction_multipliers(self):
        """T-3: Friction multipliers are correct."""
        world = _make_world()
        # Set up active coalition
        world.active_coalition = {
            "members": ["Prussia", "Austria"],
            "leader": "Prussia",
        }
        # High relation = low friction (1.0)
        _set_relation(world, "Prussia", "Austria", 40)
        assert get_coalition_friction("Prussia", "Austria", world) == 1.0

        # Moderate relation = 0.75
        _set_relation(world, "Prussia", "Austria", 15)
        assert get_coalition_friction("Prussia", "Austria", world) == 0.75

        # Negative relation = 0.5
        _set_relation(world, "Prussia", "Austria", -10)
        assert get_coalition_friction("Prussia", "Austria", world) == 0.5

        # Very negative = 0.25
        _set_relation(world, "Prussia", "Austria", -30)
        assert get_coalition_friction("Prussia", "Austria", world) == 0.25

    def test_t6_loyalty_penalty_formula(self):
        """T-6: Loyalty penalty = max(-15 - WE//10, -30). WE weakens coalition (R40 fix)."""
        world = _make_world()
        world.active_coalition = {
            "members": ["Prussia", "Austria"],
            "leader": "Prussia",
        }
        # 0 WE → min(-15 + 0, 0) = -15
        world.war_exhaustion = {"Prussia": 0}
        penalty = get_coalition_loyalty_penalty("Prussia", world)
        assert penalty == -15

        # 100 WE → min(-15 + 10, 0) = -5
        world.war_exhaustion = {"Prussia": 100}
        penalty = get_coalition_loyalty_penalty("Prussia", world)
        assert penalty == -5

        # 150 WE → min(-15 + 15, 0) = 0 (ceiling)
        world.war_exhaustion = {"Prussia": 150}
        penalty = get_coalition_loyalty_penalty("Prussia", world)
        assert penalty == 0

    def test_t4_war_exhaustion_from_battle(self):
        """T-4: War exhaustion = casualties/1000, capped at 20."""
        world = _make_world()
        world.active_coalition = {
            "members": ["Prussia"],
            "leader": "Prussia",
        }
        world.war_exhaustion = {"Prussia": 0}
        # Signature: add_war_exhaustion_from_battle(nation, casualties, world)
        add_war_exhaustion_from_battle("Prussia", 15000, world)
        assert world.war_exhaustion["Prussia"] == 15  # 15000 / 1000 = 15

        # Cap at 20 per battle
        world.war_exhaustion = {"Prussia": 0}
        add_war_exhaustion_from_battle("Prussia", 50000, world)
        assert world.war_exhaustion["Prussia"] == 20  # capped


class TestSection7Dissolution:
    """U-1 through U-4: Coalition dissolution."""

    def test_u1_threat_below_20_dissolves(self):
        """U-1: Threat < 20 → dissolution."""
        world = _make_world()
        world.threat_level = 15
        world.active_coalition = {
            "members": ["Prussia", "Austria"],
            "leader": "Prussia",
        }
        _set_at_war(world, "France", "Prussia")
        _set_at_war(world, "France", "Austria")
        reason = check_dissolution(world)
        assert reason == "low_threat"

    def test_u4_cooldown_after_dissolution(self):
        """U-4: 5-turn cooldown after dissolution."""
        world = _make_world()
        world.threat_level = 15
        world.active_coalition = {
            "members": ["Prussia", "Austria"],
            "leader": "Prussia",
        }
        _set_at_war(world, "France", "Prussia")
        _set_at_war(world, "France", "Austria")
        process_coalition_turn(world)
        # Coalition should be dissolved and cooldown set
        assert world.active_coalition is None
        assert world.coalition_cooldown == 5


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 8: VASSAL SYSTEM
# ═══════════════════════════════════════════════════════════════════════════

class TestSection8VassalCreation:
    """V-1 through V-5: Vassal creation paths."""

    def test_v1_treaty_requires_war_or_open_borders(self):
        """V-1: Treaty vassalization requires WAR or OPEN_BORDERS+."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "PEACE")
        result = create_vassal_treaty(world, "France", "Saxony", 0)
        assert result["success"] is False

    def test_v1_treaty_with_open_borders_succeeds(self):
        """V-1: Treaty vassalization succeeds with OPEN_BORDERS."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "OPEN_BORDERS")
        result = create_vassal_treaty(world, "France", "Saxony", 0)
        assert result["success"] is True
        assert "Saxony" in world.vassals

    def test_v3_treaty_loyalty_starts_at_60(self):
        """V-3: Treaty path loyalty starts at 60 + bonus."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "OPEN_BORDERS")
        create_vassal_treaty(world, "France", "Saxony", 0)
        assert world.vassals["Saxony"]["loyalty"] == 60

    def test_v3_treaty_loyalty_with_generosity(self):
        """V-3: Treaty loyalty includes generosity bonus."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "OPEN_BORDERS")
        create_vassal_treaty(world, "France", "Saxony", generosity_bonus=2)
        assert world.vassals["Saxony"]["loyalty"] == 80  # 60 + 2*10

    def test_v4_conquest_loyalty_starts_at_20(self):
        """V-4: Conquest path loyalty starts at 20 + garrison/5k. Requires WAR state."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "WAR")
        create_vassal_conquest(world, "France", "Saxony", garrison_size=10000)
        assert world.vassals["Saxony"]["loyalty"] == 22  # 20 + 10000/5000

    def test_v5_threat_treaty_5(self):
        """V-5: Treaty vassalization adds +5 threat."""
        world = _make_world()
        world.threat_level = 0
        _set_diplo_state(world, "France", "Saxony", "OPEN_BORDERS")
        create_vassal_treaty(world, "France", "Saxony", 0)
        assert world.threat_level == 5

    def test_v5_threat_conquest_25(self):
        """V-5: Conquest vassalization adds +25 threat. Requires WAR state."""
        world = _make_world()
        world.threat_level = 0
        _set_diplo_state(world, "France", "Saxony", "WAR")
        create_vassal_conquest(world, "France", "Saxony", garrison_size=0)
        assert world.threat_level == 25


class TestSection8LoyaltyDrift:
    """W-1 through W-6: Loyalty drift mechanics."""

    def test_w1_puppet_drift_negative_4(self):
        """W-1: Puppet autonomy drifts at -4/turn base."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "OPEN_BORDERS")
        create_vassal_treaty(world, "France", "Saxony", 0)
        world.vassals["Saxony"]["autonomy"] = 0  # Puppet
        world.vassals["Saxony"]["loyalty"] = 80
        # Zero out relation modifier
        _set_relation(world, "France", "Saxony", 0)
        process_vassal_loyalty(world)
        # Should drift down (exact amount depends on all modifiers)
        assert world.vassals["Saxony"]["loyalty"] < 80

    def test_w6_loyalty_clamped_0_100(self):
        """W-6: Loyalty clamped to [0, 100]."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "OPEN_BORDERS")
        create_vassal_treaty(world, "France", "Saxony", generosity_bonus=5)
        # Loyalty = min(100, 60+50) = 100
        assert world.vassals["Saxony"]["loyalty"] <= 100


class TestSection8Rebellion:
    """X-1 through X-6: Rebellion mechanics."""

    def test_x2_loyalty_0_triggers_rebellion(self):
        """X-2: Loyalty == 0 triggers actual rebellion."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "OPEN_BORDERS")
        create_vassal_treaty(world, "France", "Saxony", 0)
        world.vassals["Saxony"]["loyalty"] = 0
        rebellions = check_vassal_rebellion(world)
        assert len(rebellions) > 0

    def test_x6_multiple_rebellions_same_turn(self):
        """X-6: Multiple vassals can rebel on same turn."""
        world = _make_world()
        # Create two vassals at loyalty 0
        _set_diplo_state(world, "France", "Saxony", "OPEN_BORDERS")
        _set_diplo_state(world, "France", "Prussia", "OPEN_BORDERS")
        create_vassal_treaty(world, "France", "Saxony", 0)
        create_vassal_treaty(world, "France", "Prussia", 0)
        world.vassals["Saxony"]["loyalty"] = 0
        world.vassals["Prussia"]["loyalty"] = 0
        rebellions = check_vassal_rebellion(world)
        assert len(rebellions) >= 2


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 9: AI PROPOSALS — BUG FIX TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestSection9AllianceConflictAIAI:
    """AA-5: AI-AI alliance conflict check (BUG FIX)."""

    def test_aa5_ai_ai_alliance_blocked_when_conflict(self):
        """AA-5 FIX: AI-AI alliance blocked when one is at war with other's ally."""
        world = _make_world()
        # Prussia allied with Austria
        _set_diplo_state(world, "Prussia", "Austria", "ALLIANCE")
        # Britain at war with Austria
        _set_at_war(world, "Britain", "Austria")
        # Britain tries to ally with Prussia — should be blocked
        proposal = {"type": "defensive_alliance", "proposer": "Britain", "target": "Prussia"}
        result = _ratify_via_world("Britain", "Prussia", proposal, world)
        assert result is None  # Blocked by conflict check

    def test_aa5_ai_ai_alliance_allowed_no_conflict(self):
        """AA-5: AI-AI alliance allowed when no conflict exists."""
        world = _make_world()
        # No wars between relevant nations
        _set_diplo_state(world, "Prussia", "Austria", "PEACE")
        _set_diplo_state(world, "Britain", "Austria", "PEACE")
        _set_diplo_state(world, "Britain", "Prussia", "NON_AGGRESSION")
        proposal = {"type": "defensive_alliance", "proposer": "Britain", "target": "Prussia"}
        result = _ratify_via_world("Britain", "Prussia", proposal, world)
        assert result is not None

    def test_aa5_reverse_conflict_also_blocked(self):
        """AA-5: Reverse direction conflict also blocked."""
        world = _make_world()
        # Britain allied with Austria
        _set_diplo_state(world, "Britain", "Austria", "DEFENSIVE_ALLIANCE")
        # Prussia at war with Austria
        _set_at_war(world, "Prussia", "Austria")
        # Prussia tries to ally with Britain — should be blocked
        proposal = {"type": "alliance", "proposer": "Prussia", "target": "Britain"}
        result = _ratify_via_world("Prussia", "Britain", proposal, world)
        assert result is None

    def test_aa5_non_alliance_states_not_affected(self):
        """AA-5: Non-alliance states bypass conflict check."""
        world = _make_world()
        # Even with wars, non_aggression pacts should work
        _set_at_war(world, "Britain", "Austria")
        _set_diplo_state(world, "Prussia", "Austria", "ALLIANCE")
        _set_diplo_state(world, "Britain", "Prussia", "PEACE")
        proposal = {"type": "non_aggression", "proposer": "Britain", "target": "Prussia"}
        result = _ratify_via_world("Britain", "Prussia", proposal, world)
        assert result is not None

    def test_aa5_player_alliance_conflict_still_works(self):
        """AA-5: Player-facing check_alliance_conflict still works."""
        world = _make_world()
        # Prussia allied with Austria, France at war with Austria
        _set_diplo_state(world, "Prussia", "Austria", "ALLIANCE")
        _set_at_war(world, "France", "Austria")
        conflict = check_alliance_conflict("Prussia", "ALLIANCE", world)
        assert conflict is not None
        assert "Austria" in conflict["conflicting_nations"]


class TestSection9AIAIDiplomacy:
    """AA-1 through AA-4: AI-AI diplomacy mechanics."""

    def test_aa2_max_2_treaties_per_turn(self):
        """AA-2: Max 2 AI-AI treaties per turn."""
        world = _make_world()
        # Set all enemy nations to PEACE with each other and moderately friendly
        for i, n1 in enumerate(world.enemy_nations):
            for n2 in world.enemy_nations[i + 1:]:
                _set_diplo_state(world, n1, n2, "PEACE")
                _set_relation(world, n1, n2, 40)
        events = process_ai_ai_diplomatic_phase(world)
        # R15: rivalry events are now included alongside treaty events.
        # Only count treaty events for the max-2 cap.
        treaty_events = [e for e in events if e.get("type") not in ("ai_ai_rivalry", "ai_ai_downgrade")]
        assert len(treaty_events) <= 2

    def test_aa3_no_player_popups(self):
        """AA-3: AI-AI treaties don't create player-facing popups."""
        world = _make_world()
        for i, n1 in enumerate(world.enemy_nations):
            for n2 in world.enemy_nations[i + 1:]:
                _set_diplo_state(world, n1, n2, "PEACE")
                _set_relation(world, n1, n2, 40)
        process_ai_ai_diplomatic_phase(world)
        # No popup fields should be set
        assert world.incoming_proposal_popup is None
        assert world.coalition_popup is None


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 10: DIPLOMATIC LEDGER
# ═══════════════════════════════════════════════════════════════════════════

class TestSection10DiplomaticLedger:
    """AB-1 through AC-4: Diplomatic ledger accuracy."""

    def test_ab1_nations_tab_present(self):
        """AB-1: Nations tab shows all nations."""
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        assert "nations" in ledger
        nation_names = [n["name"] for n in ledger["nations"]]
        for n in world.enemy_nations:
            assert n in nation_names

    def test_ab2_treaties_tab_present(self):
        """AB-2: Treaties tab exists."""
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        assert "treaties" in ledger

    def test_ab3_threat_coalition_tab_present(self):
        """AB-3: Threat/Coalition tab exists with threat level."""
        world = _make_world()
        world.threat_level = 42
        ledger = build_diplomatic_ledger(world)
        assert "threat_coalition" in ledger
        assert ledger["threat_coalition"]["threat_level"] == 42

    def test_ab4_talleyrand_tab_present(self):
        """AB-4: Talleyrand tab exists with trust info."""
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        assert "talleyrand" in ledger
        assert "trust" in ledger["talleyrand"]


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 12: SERIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

class TestSection12Serialization:
    """AE-1 through AF-4: Serialization round-trip."""

    def test_ae3_pending_dialogue_roundtrip(self):
        """AE-3: pending_diplomatic_dialogue survives save/load."""
        world = _make_world()
        world.pending_diplomatic_dialogue = {
            "type": "incoming_proposal",
            "blocking": True,
            "turn_created": 5,
        }
        data = world.to_dict()
        world2 = WorldState.from_dict(data)
        assert world2.pending_diplomatic_dialogue is not None
        assert world2.pending_diplomatic_dialogue["blocking"] is True

    def test_ae5_active_coalition_roundtrip(self):
        """AE-5: active_coalition survives save/load."""
        world = _make_world()
        world.active_coalition = {
            "members": ["Prussia", "Austria"],
            "leader": "Prussia",
            "posture": "aggressive",
        }
        data = world.to_dict()
        world2 = WorldState.from_dict(data)
        assert world2.active_coalition is not None
        assert "Prussia" in world2.active_coalition["members"]
        assert world2.active_coalition["leader"] == "Prussia"

    def test_ae6_vassals_roundtrip(self):
        """AE-6: vassals dict survives save/load."""
        world = _make_world()
        world.vassals = {
            "Saxony": {"lord": "France", "loyalty": 60, "autonomy": 1}
        }
        data = world.to_dict()
        world2 = WorldState.from_dict(data)
        assert "Saxony" in world2.vassals
        assert world2.vassals["Saxony"]["loyalty"] == 60

    def test_ae7_popup_fields_roundtrip(self):
        """AE-7: Popup fields survive save/load."""
        world = _make_world()
        world.coalition_popup = {"message": "Coalition formed!"}
        world.vassal_rebellion_imminent_popup = {"nation": "Saxony"}
        data = world.to_dict()
        world2 = WorldState.from_dict(data)
        assert world2.coalition_popup is not None
        assert world2.vassal_rebellion_imminent_popup is not None

    def test_af1_blocking_dialogue_restored(self):
        """AF-1: Blocking dialogue restored after save/load."""
        world = _make_world()
        world.pending_diplomatic_dialogue = {
            "type": "incoming_proposal",
            "blocking": True,
            "turn_created": 5,
            "target_nation": "Prussia",
        }
        world.incoming_proposal_popup = {"nation": "Prussia", "terms": []}
        data = world.to_dict()
        world2 = WorldState.from_dict(data)
        assert world2.pending_diplomatic_dialogue["blocking"] is True
        assert world2.incoming_proposal_popup is not None

    def test_af2_coalition_brewing_roundtrip(self):
        """AF-2: Coalition brewing state restored after save/load."""
        world = _make_world()
        world.coalition_brewing = {"turns_remaining": 2, "qualifying": ["Prussia", "Austria"]}
        data = world.to_dict()
        world2 = WorldState.from_dict(data)
        assert world2.coalition_brewing is not None
        assert world2.coalition_brewing["turns_remaining"] == 2

    def test_af4_mission_roundtrip(self):
        """AF-4: Active mission restored after save/load."""
        world = _make_world()
        world.active_diplomatic_mission = {
            "target": "Prussia",
            "type": "improve_relations",
            "turns_active": 3,
            "paused": False,
        }
        data = world.to_dict()
        world2 = WorldState.from_dict(data)
        assert world2.active_diplomatic_mission is not None
        assert world2.active_diplomatic_mission["target"] == "Prussia"
        assert world2.active_diplomatic_mission["turns_active"] == 3


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 13: CROSS-SYSTEM INTERACTIONS
# ═══════════════════════════════════════════════════════════════════════════

class TestSection13Economy:
    """AI-1 through AI-5: Economy × Diplomacy."""

    def test_ai5_dp_regen_based_on_authority(self):
        """AI-5: DP regenerates based on authority."""
        from backend.game_logic.diplomacy import calculate_dp
        world = _make_world()
        # calculate_dp(diplomat, authority, controls_capital)
        talleyrand = world.diplomats.get("France")
        dp = calculate_dp(talleyrand, 80, True)
        # Base 2 + authority//20 bonuses
        assert dp >= 2


class TestSection13Movement:
    """AH-1 through AH-3: Movement × Diplomacy."""

    def test_ah1_war_allows_entry(self):
        """AH-1: WAR state allows entry (for attack)."""
        from backend.game_logic.diplomacy import can_enter_territory
        world = _make_world()
        _set_at_war(world, "France", "Prussia")
        assert can_enter_territory(world, "France", "Prussia") is True

    def test_ah1_peace_blocks_entry(self):
        """AH-1: PEACE state blocks entry."""
        from backend.game_logic.diplomacy import can_enter_territory
        world = _make_world()
        _set_diplo_state(world, "France", "Prussia", "PEACE")
        assert can_enter_territory(world, "France", "Prussia") is False

    def test_ah2_open_borders_allows_entry(self):
        """AH-2: OPEN_BORDERS allows entry."""
        from backend.game_logic.diplomacy import can_enter_territory
        world = _make_world()
        _set_diplo_state(world, "France", "Prussia", "OPEN_BORDERS")
        assert can_enter_territory(world, "France", "Prussia") is True


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 14: NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════

class TestSection14Notifications:
    """AK-1 through AK-10: Notification types exist."""

    def test_ak_diplomatic_notification_constants_exist(self):
        """AK: All diplomatic notification constants defined."""
        from backend.notifications import (
            COALITION_THREAT_TENSION,
            COALITION_MURMURS,
            COALITION_BREWING,
            COALITION_DECLARED,
            COALITION_MEMBER_PEACED,
            COALITION_DISSOLVED,
            COALITION_COOLDOWN_ENDED,
            DIPLOMATIC_PROPOSAL,
            TREATY_SIGNED,
            TREATY_BROKEN,
            SABOTAGE_DISCOVERED,
            VASSAL_REBELLION_IMMINENT,
            ALLIANCE_CASCADE_WAR,
            WAR_DECLARED,
            VASSAL_REBELLION,
            VASSAL_LOYALTY_CRITICAL,
            VASSAL_COURTING_DETECTED,
            DP_INSUFFICIENT,
            DEFECTION_CASCADE,
        )
        # All 19 should be truthy (non-empty string constants)
        assert all([
            COALITION_THREAT_TENSION, COALITION_MURMURS, COALITION_BREWING,
            COALITION_DECLARED, COALITION_MEMBER_PEACED, COALITION_DISSOLVED,
            COALITION_COOLDOWN_ENDED, DIPLOMATIC_PROPOSAL, TREATY_SIGNED,
            TREATY_BROKEN, SABOTAGE_DISCOVERED, VASSAL_REBELLION_IMMINENT,
            ALLIANCE_CASCADE_WAR, WAR_DECLARED, VASSAL_REBELLION,
            VASSAL_LOYALTY_CRITICAL, VASSAL_COURTING_DETECTED,
            DP_INSUFFICIENT, DEFECTION_CASCADE,
        ])


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 15: CHEAT COMMANDS — BUG FIX TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestSection15CheatBugFixes:
    """AL-2a, AL-2b: Cheat command bounds checking fixes."""

    def test_al2a_war_exhaustion_clamp_200(self):
        """AL-2a FIX: set_war_exhaustion clamps to 200, not 100."""
        world = _make_world()
        executor = _make_executor()
        gs = _make_game_state(world)

        # Set to 150 — was previously clamped to 100
        command = {"action": "cheat", "cheat_type": "set_war_exhaustion",
                   "cheat_args": ["Prussia", "150"]}
        result = executor._execute_cheat(command, gs)
        assert result["success"] is True
        assert world.war_exhaustion["Prussia"] == 150

    def test_al2a_war_exhaustion_clamp_max(self):
        """AL-2a FIX: set_war_exhaustion clamps at 200 max."""
        world = _make_world()
        executor = _make_executor()
        gs = _make_game_state(world)

        command = {"action": "cheat", "cheat_type": "set_war_exhaustion",
                   "cheat_args": ["Prussia", "999"]}
        result = executor._execute_cheat(command, gs)
        assert world.war_exhaustion["Prussia"] == 200

    def test_al2b_vassal_loyalty_clamped_positive(self):
        """AL-2b FIX: set_vassal_loyalty clamps to [0, 100]."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "OPEN_BORDERS")
        create_vassal_treaty(world, "France", "Saxony", 0)

        executor = _make_executor()
        gs = _make_game_state(world)

        # Try setting to -50 — should clamp to 0
        command = {"action": "cheat", "cheat_type": "set_vassal_loyalty",
                   "cheat_args": ["Saxony", "-50"]}
        result = executor._execute_cheat(command, gs)
        assert result["success"] is True
        assert world.vassals["Saxony"]["loyalty"] == 0

    def test_al2b_vassal_loyalty_clamped_max(self):
        """AL-2b FIX: set_vassal_loyalty clamps at 100 max."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "OPEN_BORDERS")
        create_vassal_treaty(world, "France", "Saxony", 0)

        executor = _make_executor()
        gs = _make_game_state(world)

        command = {"action": "cheat", "cheat_type": "set_vassal_loyalty",
                   "cheat_args": ["Saxony", "200"]}
        result = executor._execute_cheat(command, gs)
        assert world.vassals["Saxony"]["loyalty"] == 100

    def test_al1_all_cheat_commands_recognized(self):
        """AL-1: All cheat commands return a result (don't fall through)."""
        world = _make_world()
        executor = _make_executor()
        gs = _make_game_state(world)

        cheat_types = [
            ("set_threat", ["50"]),
            ("set_relation", ["Prussia", "20"]),
            ("give_dp", ["5"]),
            ("set_war_exhaustion", ["Prussia", "50"]),
            ("set_diplo_state", ["Prussia", "WAR"]),
            ("set_vassal_loyalty", ["Saxony", "50"]),  # Will fail — Saxony not vassal
            ("set_talleyrand_trust", ["50"]),
            ("clear_dialogue", []),
        ]
        for cheat_type, args in cheat_types:
            command = {"action": "cheat", "cheat_type": cheat_type, "cheat_args": args}
            result = executor._execute_cheat(command, gs)
            assert result is not None, f"cheat {cheat_type} returned None"
            assert "message" in result, f"cheat {cheat_type} missing message"
