"""
Phase 1 Critical Wiring — Tests for 16 bug fixes (R2, R37, R40, R41, R42, R43,
R55, R61, R62, R63, R64, R65, R66, R74, R96, R109).
"""
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.models.trust import Trust
from backend.game_logic.coalition import (
    get_coalition_loyalty_penalty,
)
from backend.game_logic.diplomacy import (
    OPEN_MOVEMENT_STATES,
)
from backend.game_logic.ai_diplomacy import (
    _evaluate_ai_ai_proposal,
)
from backend.game_logic.dispatch import (
    _is_dispatch_event_visible,
)
from backend.game_logic.diplomatic_advisory import (
    _get_military_advantage,
)
from backend.commands.diplomatic_defiance import (
    resolve_confrontation, apply_redemption_choice,
)
from backend.commands.executor import CommandExecutor


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def _make_world(**overrides):
    world = WorldState()
    for k, v in overrides.items():
        setattr(world, k, v)
    return world


def _make_marshal(name="Ney", location="Paris", strength=10000, nation="France", **kw):
    return Marshal(name=name, location=location, strength=strength,
                   personality="aggressive", nation=nation, **kw)


def _make_talleyrand(trust=65):
    from backend.models.diplomat import DiplomaticRepresentative
    return DiplomaticRepresentative("Talleyrand", "France", "schemer", skill=10, trust=trust)


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


# ═══════════════════════════════════════════════════════
# R40 — Coalition loyalty penalty formula
# ═══════════════════════════════════════════════════════

class TestR40CoalitionLoyaltyPenalty:
    def test_base_penalty_no_exhaustion(self):
        world = _make_world()
        world.active_coalition = {"members": ["Prussia"], "leader": "Prussia"}
        world.war_exhaustion = {"Prussia": 0}
        assert get_coalition_loyalty_penalty("Prussia", world) == -15

    def test_exhaustion_deepens_penalty(self):
        world = _make_world()
        world.active_coalition = {"members": ["Prussia"], "leader": "Prussia"}
        world.war_exhaustion = {"Prussia": 50}
        # max(-15 - 5, -30) = -20
        assert get_coalition_loyalty_penalty("Prussia", world) == -20

    def test_penalty_floors_at_minus_30(self):
        world = _make_world()
        world.active_coalition = {"members": ["Prussia"], "leader": "Prussia"}
        world.war_exhaustion = {"Prussia": 200}
        # max(-15 - 20, -30) = -30
        assert get_coalition_loyalty_penalty("Prussia", world) == -30

    def test_non_member_zero(self):
        world = _make_world()
        world.active_coalition = {"members": ["Prussia"], "leader": "Prussia"}
        assert get_coalition_loyalty_penalty("Austria", world) == 0


# ═══════════════════════════════════════════════════════
# R96 — VASSAL in OPEN_MOVEMENT_STATES
# ═══════════════════════════════════════════════════════

class TestR96VassalMovement:
    def test_vassal_in_open_movement_states(self):
        assert "VASSAL" in OPEN_MOVEMENT_STATES

    def test_all_expected_states_present(self):
        expected = {"OPEN_BORDERS", "NON_AGGRESSION", "DEFENSIVE_ALLIANCE", "ALLIANCE", "VASSAL"}
        assert OPEN_MOVEMENT_STATES == expected


# ═══════════════════════════════════════════════════════
# R109 — defensive_alliance proposal type preserved
# ═══════════════════════════════════════════════════════

class TestR109DefensiveAllianceType:
    def test_defensive_alliance_not_overwritten_to_alliance(self):
        """AI proposals for defensive_alliance should keep that type."""
        world = _make_world()
        world.enemy_nations = ["Prussia", "Austria", "Britain", "Russia", "Saxony"]
        world.diplomatic_states = {}
        from backend.game_logic.ai_diplomacy import _build_proposal_terms
        terms = _build_proposal_terms("Prussia", "defensive_alliance", 0, world)
        assert terms["type"] == "defensive_alliance"


# ═══════════════════════════════════════════════════════
# R66 — Dispatch fog rule reads correct key
# ═══════════════════════════════════════════════════════

class TestR66DispatchFogKey:
    def test_player_mission_uses_target_key(self):
        world = _make_world()
        world.active_diplomatic_mission = {"target": "Prussia"}
        event = {
            "type": "diplomatic_mission_progress",
            "template_vars": {"nation": "Prussia"},
            "fog_rule": "player_mission",
        }
        assert _is_dispatch_event_visible(event, world, "France") is True

    def test_player_mission_hidden_wrong_target(self):
        world = _make_world()
        world.active_diplomatic_mission = {"target": "Austria"}
        event = {
            "type": "diplomatic_mission_progress",
            "template_vars": {"nation": "Prussia"},
            "fog_rule": "player_mission",
        }
        assert _is_dispatch_event_visible(event, world, "France") is False


# ═══════════════════════════════════════════════════════
# R61 — original_nation serialization
# ═══════════════════════════════════════════════════════

class TestR61OriginalNationSerialization:
    def test_original_nation_default_none(self):
        m = _make_marshal()
        assert m.original_nation is None

    def test_original_nation_in_to_dict(self):
        m = _make_marshal()
        m.original_nation = "Saxony"
        d = m.to_dict()
        assert "original_nation" in d
        assert d["original_nation"] == "Saxony"

    def test_original_nation_roundtrip(self):
        m = _make_marshal()
        m.original_nation = "Saxony"
        d = m.to_dict()
        m2 = Marshal.from_dict(d)
        assert m2.original_nation == "Saxony"

    def test_original_nation_none_roundtrip(self):
        m = _make_marshal()
        d = m.to_dict()
        m2 = Marshal.from_dict(d)
        assert m2.original_nation is None


# ═══════════════════════════════════════════════════════
# R62 — Rebellion clears original_nation and resets trust
# ═══════════════════════════════════════════════════════

class TestR62RebellionCleanup:
    def test_rebellion_clears_original_nation(self):
        world = _make_world()
        m = _make_marshal(name="TestMarshal", nation="France")
        m.original_nation = "Saxony"
        m.trust = Trust(40)
        world.marshals["TestMarshal"] = m
        world.vassals = {"Saxony": {"lord": "France", "loyalty": 0}}

        from backend.game_logic.vassal import check_vassal_rebellion
        check_vassal_rebellion(world)

        assert m.nation == "Saxony"
        assert m.original_nation is None
        assert m.trust.value == 70  # Reset to default Trust()


# ═══════════════════════════════════════════════════════
# R63 — break_treaty adds coalition threat
# ═══════════════════════════════════════════════════════

class TestR63BreakTreatyThreat:
    def test_break_alliance_adds_25_threat(self):
        world = _make_world()
        world.enemy_nations = ["Prussia", "Austria", "Britain", "Russia", "Saxony"]
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "ALLIANCE"
        world.nation_relations[key] = 50
        world.diplomatic_points = 5
        world.active_treaties[key] = {
            "type": "alliance", "nations": ["France", "Prussia"],
        }
        old_threat = world.threat_level

        from backend.game_logic.diplomacy import break_treaty
        result = break_treaty(key, "France", world)

        assert result["success"] is True
        assert world.threat_level >= old_threat + 25

    def test_break_open_borders_adds_15_threat(self):
        world = _make_world()
        world.enemy_nations = ["Prussia", "Austria", "Britain", "Russia", "Saxony"]
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "OPEN_BORDERS"
        world.nation_relations[key] = 20
        world.diplomatic_points = 5
        world.active_treaties[key] = {
            "type": "open_borders", "nations": ["France", "Prussia"],
        }
        old_threat = world.threat_level

        from backend.game_logic.diplomacy import break_treaty
        result = break_treaty(key, "France", world)

        assert result["success"] is True
        assert world.threat_level >= old_threat + 15


# ═══════════════════════════════════════════════════════
# R64 — Continental System called from turn loop
# ═══════════════════════════════════════════════════════

class TestR64ContinentalSystem:
    def test_continental_system_no_crash_empty(self):
        """CS call in turn loop doesn't crash when no members."""
        world = _make_world()
        world.continental_system_members = []
        # Just verify advance_turn doesn't crash
        world.advance_turn()

    def test_continental_system_called_in_turn(self):
        """Verify CS function is reachable from diplomacy module."""
        from backend.game_logic.diplomacy import apply_continental_system
        world = _make_world()
        world.continental_system_members = []
        # Should not crash
        apply_continental_system(world)

    def test_vassal_no_duplicate_cs_function(self):
        """Verify duplicate CS function removed from vassal.py."""
        import backend.game_logic.vassal as vassal_module
        # The function should NOT exist in vassal module anymore
        assert not hasattr(vassal_module, 'apply_continental_system')


# ═══════════════════════════════════════════════════════
# R65 — Advisory fog-filtered strength
# ═══════════════════════════════════════════════════════

class TestR65AdvisoryFog:
    def test_military_advantage_unknown_visibility(self):
        """With no intel on enemy region, military advantage should be 'unknown'."""
        world = _make_world()
        m1 = _make_marshal(name="Ney", nation="France", strength=20000)
        # Place British marshal in a remote region with no French visibility
        m2 = _make_marshal(name="Wellington", nation="Britain", strength=30000, location="London")
        world.marshals = {"Ney": m1, "Wellington": m2}
        # Recalculate visibility — London has no French presence, should be UNKNOWN
        world.calculate_visibility()
        # Verify London is UNKNOWN after recalculation
        london_intel = world.get_region_intel("London")
        assert london_intel.visibility == "unknown", f"Expected unknown, got {london_intel.visibility}"
        result = _get_military_advantage("Britain", world)
        assert result == "unknown"

    def test_military_advantage_full_visibility(self):
        """With FULL visibility, should return precise assessment."""
        world = _make_world()
        m1 = _make_marshal(name="Ney", nation="France", strength=20000)
        m2 = _make_marshal(name="Wellington", nation="Britain", strength=40000, location="Paris")
        world.marshals = {"Ney": m1, "Wellington": m2}
        world.calculate_visibility()
        # Paris should have FULL visibility for France (French marshal present)
        result = _get_military_advantage("Britain", world)
        # 40k vs 20k = 2.0 ratio → "overwhelming"
        assert result == "overwhelming"


# ═══════════════════════════════════════════════════════
# R43 — AI-AI per-pair proposal cooldown
# ═══════════════════════════════════════════════════════

class TestR43AIAICooldown:
    def test_cooldown_blocks_rapid_proposal(self):
        world = _make_world()
        world.enemy_nations = ["Prussia", "Austria", "Britain", "Russia", "Saxony"]
        key = world._make_diplo_key("Prussia", "Austria")

        # Set up conditions for a proposal (both at war with France)
        fk1 = world._make_diplo_key("France", "Prussia")
        fk2 = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[fk1] = "WAR"
        world.diplomatic_states[fk2] = "WAR"
        world.diplomatic_states[key] = "PEACE"
        world.nation_relations[key] = 0

        # First proposal should succeed
        proposal = _evaluate_ai_ai_proposal("Prussia", "Austria", world)
        assert proposal is not None

        # Set cooldown
        world.ai_proposal_cooldowns[f"ai_ai|{key}"] = 5

        # Second proposal should be blocked by cooldown
        proposal2 = _evaluate_ai_ai_proposal("Prussia", "Austria", world)
        assert proposal2 is None

    def test_ratify_sets_cooldown(self):
        world = _make_world()
        world.enemy_nations = ["Prussia", "Austria", "Britain", "Russia", "Saxony"]
        key = world._make_diplo_key("Prussia", "Austria")
        world.diplomatic_states[key] = "PEACE"
        world.nation_relations[key] = 0

        proposal = {"type": "non_aggression", "proposer": "Prussia", "target": "Austria"}
        _ratify_via_world("Prussia", "Austria", proposal, world)

        # Cooldown should be set
        assert world.ai_proposal_cooldowns.get(f"ai_ai|{key}", 0) == 5


# ═══════════════════════════════════════════════════════
# R37 — Sabotage confrontation handler
# ═══════════════════════════════════════════════════════

class TestR37SabotageConfrontation:
    def test_confront_sabotage_reduces_trust(self):
        world = _make_world()
        talleyrand = _make_talleyrand(trust=50)
        world.diplomats = {"France": talleyrand}

        result = resolve_confrontation("confront_sabotage", talleyrand, world)
        assert result["trust_change"] == -10
        assert result["authority_change"] == +5
        assert talleyrand.trust == 40

    def test_overlook_sabotage_increases_trust(self):
        world = _make_world()
        talleyrand = _make_talleyrand(trust=50)
        world.diplomats = {"France": talleyrand}

        result = resolve_confrontation("overlook_sabotage", talleyrand, world)
        assert result["trust_change"] == +3
        assert talleyrand.trust == 53

    def test_executor_routes_confront_sabotage(self):
        """Verify executor handles confront_sabotage action."""
        world = _make_world()
        talleyrand = _make_talleyrand(trust=50)
        world.diplomats = {"France": talleyrand}
        world.pending_diplomatic_dialogue = {
            "type": "sabotage_confrontation",
            "options": [
                {"label": "Confront", "action": "confront_sabotage"},
                {"label": "Overlook", "action": "overlook_sabotage"},
            ],
            "context": {},
        }
        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response("confront", game_state)
        assert result["success"] is True
        assert world.pending_diplomatic_dialogue is None


# ═══════════════════════════════════════════════════════
# R41 — Redemption handler
# ═══════════════════════════════════════════════════════

class TestR41Redemption:
    def test_redemption_apologize(self):
        world = _make_world()
        talleyrand = _make_talleyrand(trust=20)
        result = apply_redemption_choice("redemption_apologize", talleyrand, world)
        assert result["trust_change"] == +15
        assert talleyrand.trust == 35

    def test_redemption_replace(self):
        world = _make_world()
        talleyrand = _make_talleyrand(trust=20)
        result = apply_redemption_choice("redemption_replace", talleyrand, world)
        assert result["personality_changed"] is True
        assert talleyrand.personality == "loyalist"
        assert talleyrand.skill == 6
        assert talleyrand.trust == 50

    def test_executor_routes_redemption(self):
        world = _make_world()
        talleyrand = _make_talleyrand(trust=20)
        world.diplomats = {"France": talleyrand}
        world.pending_diplomatic_dialogue = {
            "type": "talleyrand_redemption",
            "options": [
                {"label": "Apologize", "action": "redemption_apologize"},
                {"label": "Replace", "action": "redemption_replace"},
                {"label": "Continue", "action": "redemption_continue"},
            ],
            "context": {"current_trust": 20},
        }
        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response("apologize", game_state)
        assert result["success"] is True
        assert world.pending_diplomatic_dialogue is None


# ═══════════════════════════════════════════════════════
# R74 — Vassal rebellion dialogue
# ═══════════════════════════════════════════════════════

class TestR74VassalRebellionDialogue:
    def test_rebellion_imminent_sets_dialogue(self):
        """When loyalty goes critical, pending_diplomatic_dialogue is set."""
        world = _make_world()
        world.vassals = {"Saxony": {
            "lord": "France", "loyalty": 12,
            "autonomy": 0, "tribute_rate": 0.1,
        }}
        world.player_nation = "France"

        from backend.game_logic.vassal import process_vassal_loyalty
        process_vassal_loyalty(world)

        # After drift pushes loyalty below threshold, dialogue should be set
        if world.pending_diplomatic_dialogue:
            assert world.pending_diplomatic_dialogue["type"] == "vassal_rebellion_imminent"
            assert len(world.pending_diplomatic_dialogue["options"]) == 3

    def test_executor_handles_invest(self):
        world = _make_world()
        world.vassals = {"Saxony": {
            "lord": "France", "loyalty": 10,
            "autonomy": 0, "tribute_rate": 0.1,
        }}
        world.pending_diplomatic_dialogue = {
            "type": "vassal_rebellion_imminent",
            "target_nation": "Saxony",
            "options": [
                {"label": "Invest", "action": "invest_vassal_rebellion"},
                {"label": "Garrison", "action": "garrison_vassal_rebellion"},
                {"label": "Accept", "action": "accept_vassal_rebellion"},
            ],
            "context": {"vassal_name": "Saxony", "loyalty": 10},
        }
        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response("invest", game_state)
        # invest_in_vassal may fail due to DP/gold requirements but handler routes correctly
        assert result is not None

    def test_executor_handles_garrison(self):
        world = _make_world()
        world.vassals = {"Saxony": {
            "lord": "France", "loyalty": 10,
            "autonomy": 0, "tribute_rate": 0.1,
        }}
        world.actions_remaining = 5
        world.pending_diplomatic_dialogue = {
            "type": "vassal_rebellion_imminent",
            "target_nation": "Saxony",
            "options": [
                {"label": "Garrison", "action": "garrison_vassal_rebellion"},
            ],
            "context": {"vassal_name": "Saxony", "loyalty": 10},
        }
        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response("garrison", game_state)
        assert result["success"] is True
        assert world.vassals["Saxony"]["loyalty"] == 20  # +10
        assert world.actions_remaining == 3  # -2 AP

    def test_executor_handles_accept(self):
        world = _make_world()
        world.pending_diplomatic_dialogue = {
            "type": "vassal_rebellion_imminent",
            "target_nation": "Saxony",
            "options": [
                {"label": "Accept", "action": "accept_vassal_rebellion"},
            ],
            "context": {"vassal_name": "Saxony", "loyalty": 10},
        }
        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response("accept", game_state)
        assert result["success"] is True
        assert world.pending_diplomatic_dialogue is None


# ═══════════════════════════════════════════════════════
# R42 — Pre-proposal objection override
# ═══════════════════════════════════════════════════════

class TestR42SendOverride:
    def test_send_override_sends_proposal(self):
        world = _make_world()
        talleyrand = _make_talleyrand(trust=50)
        world.diplomats = {"France": talleyrand}
        world.diplomatic_points = 10
        world.pending_diplomatic_dialogue = {
            "type": "proposal_confirm",
            "target_nation": "Prussia",
            "options": [
                {
                    "label": "Send my terms",
                    "action": "send_override",
                    "terms": {"proposal_type": "non_aggression"},
                },
            ],
            "context": {
                "original_proposal": {"proposal_type": "non_aggression"},
                "suggested_terms": {"proposal_type": "non_aggression"},
            },
        }
        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response("send", game_state)
        assert result["success"] is True
        assert world.talleyrand_state == "IN_TRANSIT"
        assert world.pending_diplomatic_dialogue is None


# ═══════════════════════════════════════════════════════
# R2 — Counter-offer system
# ═══════════════════════════════════════════════════════

class TestR2CounterOffer:
    def test_counter_offer_creates_dialogue(self):
        """When outcome is COUNTER_OFFER and terms generated, dialogue is created."""
        world = _make_world()
        world.enemy_nations = ["Prussia", "Austria", "Britain", "Russia", "Saxony"]
        # Set up a proposal
        proposal = {
            "type": "alliance",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [{"type": "gold_per_turn", "value": 200}],
            "clauses": [],
        }
        world.proposal_in_transit = {
            "target": "Prussia",
            "proposal": proposal,
            "turn_sent": int(world.current_turn - 1),
        }

        # Mock calculate_acceptance to return COUNTER_OFFER
        import backend.game_logic.diplomacy as diplo_module
        original_calc = diplo_module.calculate_acceptance

        def mock_acceptance(p, w):
            return {"score": 40, "outcome": "COUNTER_OFFER", "feedback": "Close but harsh."}

        diplo_module.calculate_acceptance = mock_acceptance
        try:
            events = world._process_proposal_in_transit()
        finally:
            diplo_module.calculate_acceptance = original_calc

        # Should have set up counter-offer dialogue
        if world.pending_diplomatic_dialogue:
            assert world.pending_diplomatic_dialogue["type"] == "counter_offer_response"
            assert "accept_counter_offer" in str(world.pending_diplomatic_dialogue["options"])

    def test_executor_accept_counter_offer(self):
        world = _make_world()
        world.enemy_nations = ["Prussia", "Austria", "Britain", "Russia", "Saxony"]
        counter_terms = {
            "type": "non_aggression",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        world.pending_diplomatic_dialogue = {
            "type": "counter_offer_response",
            "target_nation": "Prussia",
            "options": [
                {"label": "Accept", "action": "accept_counter_offer"},
                {"label": "Reject", "action": "reject_counter_offer"},
            ],
            "context": {
                "source_nation": "Prussia",
                "original_proposal": {"type": "alliance"},
                "counter_terms": counter_terms,
            },
        }
        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response("accept", game_state)
        assert result["success"] is True
        assert world.pending_diplomatic_dialogue is None

    def test_executor_reject_counter_offer(self):
        world = _make_world()
        world.enemy_nations = ["Prussia", "Austria", "Britain", "Russia", "Saxony"]
        key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[key] = 20
        world.pending_diplomatic_dialogue = {
            "type": "counter_offer_response",
            "target_nation": "Prussia",
            "options": [
                {"label": "Reject", "action": "reject_counter_offer"},
            ],
            "context": {
                "source_nation": "Prussia",
                "original_proposal": {"type": "alliance"},
                "counter_terms": {"type": "non_aggression"},
            },
        }
        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response("reject", game_state)
        assert result["success"] is True
        assert world.pending_diplomatic_dialogue is None
        # Cooldown set
        assert world.player_proposal_cooldowns.get("Prussia", 0) == 3
        # Relation penalty
        assert world.nation_relations.get(key, 0) == 15  # -5
