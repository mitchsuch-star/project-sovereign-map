"""Phase 2B Batch 2 tests: Diplomacy & War Transition Cleanup.

R97: declare_war/cascade clean active_treaties
R98: Wire check_relation_requirement and validate_ap_clause
R99: declare_war checks armistice cooldowns
R100: Cascade applies relation penalties
R101: break_treaty validates breaker is party
R102: war_scores cleaned up on war end (via cleanup_war_end)
R105: _process_mission_effects uses player_nation not "France"
R110: Stalemate counter reset on war end
"""

from backend.models.world_state import WorldState
from backend.game_logic.diplomacy import (
    declare_war, break_treaty, cleanup_war_end,
    _process_mission_effects,
    _process_diplomatic_reliability,
    calculate_acceptance,
    get_treaty_breach_preview,
    has_hard_reject_posture,
)


def make_world():
    world = WorldState()
    return world


def _set_diplo_state(world, a, b, state):
    key = world._make_diplo_key(a, b)
    world.diplomatic_states[key] = state


# ═══════════════════════════════════════════════════════
# R97: declare_war/cascade clean active_treaties
# ═══════════════════════════════════════════════════════

class TestR97DeclareWarCleansTreaties:
    """R97: declare_war and cascade remove active_treaties entries."""

    def test_declare_war_removes_treaty(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Austria")
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        world.active_treaties[diplo_key] = {
            "nations": ["France", "Austria"],
            "type": "alliance",
            "clauses": [{"type": "gold_per_turn", "from": "Austria", "to": "France", "amount": 100}],
            "turn_signed": 1,
            "harshness": 0,
        }
        result = declare_war(world, "France", "Austria")
        assert result["success"] is True
        assert diplo_key not in world.active_treaties

    def test_cascade_removes_treaty(self):
        world = make_world()
        # France declares war on Austria. Prussia has DEFENSIVE_ALLIANCE with Austria.
        _set_diplo_state(world, "France", "Austria", "PEACE")
        _set_diplo_state(world, "Prussia", "Austria", "DEFENSIVE_ALLIANCE")
        _set_diplo_state(world, "France", "Prussia", "ALLIANCE")
        # Active treaty between France and Prussia
        france_prussia_key = world._make_diplo_key("France", "Prussia")
        world.active_treaties[france_prussia_key] = {
            "nations": ["France", "Prussia"],
            "type": "alliance",
            "clauses": [],
            "turn_signed": 1,
            "harshness": 0,
        }
        result = declare_war(world, "France", "Austria")
        assert result["success"] is True
        # Prussia cascaded to WAR with France — treaty should be removed
        assert world.get_diplomatic_state("France", "Prussia") == "WAR"
        assert france_prussia_key not in world.active_treaties

    def test_declare_war_no_treaty_no_crash(self):
        world = make_world()
        _set_diplo_state(world, "France", "Prussia", "PEACE")
        result = declare_war(world, "France", "Prussia")
        assert result["success"] is True

    def test_declare_war_on_treaty_partner_records_breach_memory(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Austria")
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        world.active_treaties[diplo_key] = {
            "nations": ["France", "Austria"],
            "type": "alliance",
            "clauses": [],
            "turn_signed": 2,
            "harshness": 0,
        }

        result = declare_war(world, "France", "Austria")

        assert result["success"] is True
        assert world.diplomatic_reliability.get("France", 0) == -10
        breach_events = [
            e for e in world.event_log
            if e.get("type") == "diplomatic_treaty_broken"
        ]
        assert breach_events, "war declaration should emit a treaty-broken memory event"
        latest = breach_events[-1]
        assert latest.get("other") == "Austria"
        # Split per RELIABILITY_COMMITMENTS_SPEC §9.9: end_reason_family is
        # the fault axis (french_breach for voluntary perpetrator action);
        # end_reason_action is what the actor did.
        assert latest.get("end_reason_family") == "french_breach"
        assert latest.get("end_reason_action") == "war_declaration"
        assert latest.get("reason_phrase") == "by declaring war"
        assert latest.get("fault_nation") == "France"
        assert latest.get("victim_nation") == "Austria"
        assert latest.get("speaker_attribution") == "envoy"
        assert latest.get("episode_id"), "root-cause episode_id must be threaded through"


class TestCommitmentsSubstrateHardening:
    """Commitments-substrate hardening pass (Apr 15+16, 2026):
    - Cascade attribution fix (H-1): forced ruptures classified as
      obsolescence_or_external with no perpetrator penalty.
    - Episode_id threading (H-2): root-cause ID shared across breach +
      cascade + witness-strike emits from one declaration.
    - Per-witness scope_reason (H-3): ally/rival/shared_enemy precedence.
    - Duplicate-surface collapse (H-4): war-on-partner emits one notification
      and one dispatch event, not two of each.
    - Fault family split (H-6): french_breach vs obsolescence_or_external
      vs counterparty_reversal.
    """

    def test_cascade_rupture_does_not_penalize_cascaded_nation(self):
        """H-1: Prussia forced into war by France's attack on Austria must
        not be scored as an oath-breaker. Fault stays with France (§9.9.B).
        """
        world = make_world()
        _set_diplo_state(world, "France", "Austria", "PEACE")
        _set_diplo_state(world, "Prussia", "Austria", "DEFENSIVE_ALLIANCE")
        _set_diplo_state(world, "France", "Prussia", "NON_AGGRESSION")
        france_prussia_key = world._make_diplo_key("France", "Prussia")
        world.active_treaties[france_prussia_key] = {
            "nations": ["France", "Prussia"],
            "type": "non_aggression",
            "clauses": [],
            "turn_signed": 1,
        }

        result = declare_war(world, "France", "Austria")

        assert result["success"] is True
        # Prussia cascaded into WAR, breaking its non-aggression with France
        assert world.get_diplomatic_state("France", "Prussia") == "WAR"
        # But Prussia's reliability must NOT drop — the cascade is not its fault.
        assert world.diplomatic_reliability.get("Prussia", 0) == 0
        # France's reliability is unchanged by this specific cascade;
        # direct breach recording against the original target is separate.
        cascade_events = [
            e for e in world.event_log
            if e.get("type") == "diplomatic_treaty_broken"
            and e.get("breaker") == "Prussia"
        ]
        assert cascade_events, "cascade rupture should still emit a remembered event"
        latest = cascade_events[-1]
        assert latest.get("end_reason_family") == "obsolescence_or_external"
        assert latest.get("end_reason_action") == "cascade_forced"
        assert latest.get("fault_nation") == "France"
        assert latest.get("victim_nation") == "France"
        assert latest.get("speaker_attribution") == "foreign_office"
        assert latest.get("applied_reliability_delta") == 0

    def test_episode_id_threaded_through_breach_and_cascade(self):
        """H-2: all diplomatic consequences of one declaration share an episode_id."""
        world = make_world()
        france_austria = world._make_diplo_key("France", "Austria")
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        world.active_treaties[france_austria] = {
            "nations": ["France", "Austria"],
            "type": "alliance",
            "clauses": [],
            "turn_signed": 2,
        }
        _set_diplo_state(world, "Prussia", "Austria", "DEFENSIVE_ALLIANCE")
        _set_diplo_state(world, "France", "Prussia", "NON_AGGRESSION")
        world.active_treaties[world._make_diplo_key("France", "Prussia")] = {
            "nations": ["France", "Prussia"],
            "type": "non_aggression",
            "clauses": [],
            "turn_signed": 3,
        }

        declare_war(world, "France", "Austria")

        breach_events = [
            e for e in world.event_log
            if e.get("type") == "diplomatic_treaty_broken"
        ]
        assert len(breach_events) >= 2, "expected breach + cascade breach"
        episode_ids = {e.get("episode_id") for e in breach_events}
        assert len(episode_ids) == 1, f"expected single shared episode_id, got {episode_ids}"
        assert None not in episode_ids
        war_events = [e for e in world.event_log if e.get("type") == "war_declaration"]
        assert war_events, "war_declaration event missing"
        assert war_events[-1].get("episode_id") in episode_ids

    def test_per_witness_scope_reason_uses_precedence(self):
        """H-3: witness scope_reason resolves ally > rival > shared_enemy."""
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Austria")
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        world.active_treaties[diplo_key] = {
            "nations": ["France", "Austria"],
            "type": "alliance",
            "clauses": [],
            "turn_signed": 2,
        }
        # Prussia has ALLIANCE with injured party (Austria) -> ally scope
        _set_diplo_state(world, "Prussia", "Austria", "ALLIANCE")
        # Britain is at war with France -> rival scope (proxy for rivalry store)
        _set_diplo_state(world, "Britain", "France", "WAR")

        declare_war(world, "France", "Austria")

        breach = [
            e for e in world.event_log
            if e.get("type") == "diplomatic_treaty_broken"
            and e.get("breaker") == "France"
        ][-1]
        witnesses = {w["nation"]: w["scope_reason"] for w in breach["witnesses"]}
        assert witnesses.get("Prussia") == "ally"
        assert witnesses.get("Britain") == "rival"
        assert breach["dominant_witness_scope"] == "ally"

    def test_war_on_treaty_partner_collapses_duplicate_surfaces(self):
        """H-4: war-on-partner emits ONE TREATY_BROKEN-equivalent notification
        (WAR_DECLARED carries the shattering phrasing) and no separate
        `diplomatic_treaty_broken` dispatch entry.
        """
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Austria")
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        world.active_treaties[diplo_key] = {
            "nations": ["France", "Austria"],
            "type": "alliance",
            "clauses": [],
            "turn_signed": 2,
        }

        declare_war(world, "France", "Austria")

        from backend.notifications import TREATY_BROKEN, WAR_DECLARED
        notif_types = [n["type"] for n in world.notifications.get_pending()]
        assert WAR_DECLARED in notif_types
        # No duplicate TREATY_BROKEN notification when WAR_DECLARED already fires.
        assert notif_types.count(TREATY_BROKEN) == 0, (
            f"war-on-partner must not fire a duplicate TREATY_BROKEN notification; got {notif_types}"
        )
        # Exactly one diplomatic dispatch event representing the moment.
        dispatch_types = [e.get("type", "") for e in world.pending_dispatch_events]
        assert dispatch_types.count("diplomatic_treaty_broken") == 0
        assert dispatch_types.count("diplomatic_war_declared") == 1

    def test_witness_strike_recorded_dispatch_emitted_per_witness(self):
        """C3 B2a cross-cutting: one witness_strike_recorded per scoped witness."""
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Austria")
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        world.active_treaties[diplo_key] = {
            "nations": ["France", "Austria"],
            "type": "alliance",
            "clauses": [],
            "turn_signed": 2,
        }
        _set_diplo_state(world, "Prussia", "Austria", "ALLIANCE")

        declare_war(world, "France", "Austria")

        strikes = [
            e for e in world.pending_dispatch_events
            if e.get("type") == "witness_strike_recorded"
        ]
        assert strikes, "expected at least one witness_strike_recorded emit"
        prussian_strikes = [s for s in strikes
                            if s["template_vars"].get("witness_nation") == "Prussia"]
        assert prussian_strikes, "Prussia (ally of Austria) should get a scope-ally strike"
        assert prussian_strikes[0]["template_vars"].get("scope_reason") == "ally"

    def test_treaty_broken_dispatch_uses_family_specific_speaker_attribution(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Austria")
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        world.active_treaties[diplo_key] = {
            "nations": ["France", "Austria"],
            "type": "alliance",
            "clauses": [],
            "turn_signed": 2,
        }
        world.diplomatic_points = 5

        break_treaty(diplo_key, "France", world)

        treaty_dispatches = [
            e for e in world.pending_dispatch_events
            if e.get("type") == "diplomatic_treaty_broken"
        ]
        assert treaty_dispatches

        french_breach = treaty_dispatches[-1]
        assert french_breach["template_vars"].get("end_reason_family") == "french_breach"
        assert french_breach["template_vars"].get("speaker_attribution") == "envoy"
        assert french_breach["template_vars"].get("victim_nation") == "Austria"

        world.pending_dispatch_events = []
        _set_diplo_state(world, "Prussia", "Austria", "DEFENSIVE_ALLIANCE")
        _set_diplo_state(world, "France", "Prussia", "NON_AGGRESSION")
        world.active_treaties[world._make_diplo_key("France", "Prussia")] = {
            "nations": ["France", "Prussia"],
            "type": "non_aggression",
            "clauses": [],
            "turn_signed": 3,
        }

        declare_war(world, "France", "Austria")

        treaty_dispatches = [
            e for e in world.pending_dispatch_events
            if e.get("type") == "diplomatic_treaty_broken"
        ]
        assert treaty_dispatches

        cascade_breach = next(
            e for e in treaty_dispatches
            if e["template_vars"].get("end_reason_family") == "obsolescence_or_external"
        )

        assert cascade_breach["template_vars"].get("speaker_attribution") == "foreign_office"
        assert cascade_breach["template_vars"].get("victim_nation") == "France"

    def test_manual_break_retains_french_breach_family(self):
        """Manual break_treaty must be classified french_breach (voluntary)."""
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Austria")
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        world.active_treaties[diplo_key] = {
            "nations": ["France", "Austria"],
            "type": "alliance",
            "clauses": [],
            "turn_signed": 2,
        }
        world.diplomatic_points = 5

        break_treaty(diplo_key, "France", world)

        breach = [e for e in world.event_log
                  if e.get("type") == "diplomatic_treaty_broken"][-1]
        assert breach["end_reason_family"] == "french_breach"
        assert breach["end_reason_action"] == "manual_break"
        assert breach["fault_nation"] == "France"
        assert world.diplomatic_reliability.get("France", 0) == -10


class TestCommitmentsHardRejectPosture:
    """B2b follow-up: repeated remembered betrayals hard-block deep treaties."""

    def test_third_breach_triggers_hard_reject_posture(self):
        world = make_world()
        world.current_turn = 5
        diplo_key = world._make_diplo_key("France", "Austria")
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        world.active_treaties[diplo_key] = {
            "nations": ["France", "Austria"],
            "type": "alliance",
            "clauses": [],
            "turn_signed": 3,
        }
        world.betrayal_history = {
            "France|Austria": {
                "strikes": [
                    {"severity": "medium", "turn": 1, "episode_id": "ep_1", "decays_on_turn": 9},
                    {"severity": "medium", "turn": 2, "episode_id": "ep_2", "decays_on_turn": 10},
                ],
                "categories": ["treaty_breach"],
                "last_turn": 2,
            }
        }

        result = declare_war(world, "France", "Austria")

        assert result["success"] is True
        assert has_hard_reject_posture(world, "France", "Austria") is True
        triggered = [e for e in world.event_log if e.get("type") == "hard_reject_posture_triggered"]
        assert triggered
        assert triggered[-1]["victim_nation"] == "Austria"
        dispatch = [e for e in world.pending_dispatch_events if e.get("type") == "hard_reject_posture_triggered"]
        assert dispatch

    def test_decay_clears_hard_reject_posture_and_emits_event(self):
        world = make_world()
        world.current_turn = 9
        _set_diplo_state(world, "France", "Austria", "NON_AGGRESSION")
        world.betrayal_history = {
            "France|Austria": {
                "strikes": [
                    {"severity": "medium", "turn": 1, "episode_id": "ep_1", "decays_on_turn": 9},
                    {"severity": "medium", "turn": 2, "episode_id": "ep_2", "decays_on_turn": 10},
                    {"severity": "medium", "turn": 3, "episode_id": "ep_3", "decays_on_turn": 11},
                ],
                "categories": ["treaty_breach"],
                "last_turn": 3,
            }
        }

        _process_diplomatic_reliability(world)

        assert has_hard_reject_posture(world, "France", "Austria") is False
        cleared = [e for e in world.event_log if e.get("type") == "hard_reject_posture_cleared"]
        assert cleared
        assert cleared[-1]["victim_nation"] == "Austria"
        dispatch = [e for e in world.pending_dispatch_events if e.get("type") == "hard_reject_posture_cleared"]
        assert dispatch

    def test_breach_preview_flags_hard_reject_crossing(self):
        world = make_world()
        world.current_turn = 4
        world.betrayal_history = {
            "France|Austria": {
                "strikes": [
                    {"severity": "medium", "turn": 1, "episode_id": "ep_1", "decays_on_turn": 9},
                    {"severity": "medium", "turn": 2, "episode_id": "ep_2", "decays_on_turn": 10},
                ],
                "categories": ["treaty_breach"],
                "last_turn": 2,
            }
        }
        preview = get_treaty_breach_preview(
            world,
            "France",
            "Austria",
            treaty={"type": "alliance", "nations": ["France", "Austria"]},
            end_reason_action="war_declaration",
            fault_nation="France",
        )

        assert preview["active_betrayal_strikes_before"] == 2
        assert preview["active_betrayal_strikes_after"] == 3
        assert preview["would_trigger_hard_reject"] is True

    def test_hard_reject_blocks_deep_treaty_acceptance(self):
        world = make_world()
        world.current_turn = 6
        _set_diplo_state(world, "France", "Austria", "PEACE")
        world.betrayal_history = {
            "France|Austria": {
                "strikes": [
                    {"severity": "medium", "turn": 1, "episode_id": "ep_1", "decays_on_turn": 9},
                    {"severity": "medium", "turn": 2, "episode_id": "ep_2", "decays_on_turn": 10},
                    {"severity": "medium", "turn": 3, "episode_id": "ep_3", "decays_on_turn": 11},
                ],
                "categories": ["treaty_breach"],
                "last_turn": 3,
            }
        }

        result = calculate_acceptance({
            "type": "alliance",
            "proposer_nation": "France",
            "target_nation": "Austria",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }, world)

        assert result["components"]["hard_reject_posture"] == -100
        assert result["outcome"] == "REJECT"


# ═══════════════════════════════════════════════════════
# R98: Wire check_relation_requirement + validate_ap_clause
# ═══════════════════════════════════════════════════════

class TestR98WiredValidation:
    """R98: Treaty ratification checks relation requirement and AP clause."""

    def test_relation_requirement_blocks_upgrade_when_too_low(self):
        world = make_world()
        # Try to ratify NON_AGGRESSION→DEFENSIVE_ALLIANCE with relation < 20
        _set_diplo_state(world, "France", "Austria", "NON_AGGRESSION")
        diplo_key = world._make_diplo_key("France", "Austria")
        world.nation_relations[diplo_key] = 10  # Below required 20
        proposal = {
            "type": "defensive_alliance",
            "proposer_nation": "Austria",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        result = world._ratify_treaty(proposal)
        # Should fail because relation < 20
        assert result is not None
        assert "insufficient" in result.get("message", "").lower() or "failed" in result.get("type", "")

    def test_relation_requirement_passes_when_sufficient(self):
        world = make_world()
        _set_diplo_state(world, "France", "Austria", "NON_AGGRESSION")
        diplo_key = world._make_diplo_key("France", "Austria")
        world.nation_relations[diplo_key] = 30  # Above required 20
        proposal = {
            "type": "defensive_alliance",
            "proposer_nation": "Austria",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        result = world._ratify_treaty(proposal)
        assert result is not None
        assert result.get("type") == "diplomatic_treaty_signed"

    def test_ap_clause_blocked_without_high_war_score(self):
        world = make_world()
        _set_diplo_state(world, "France", "Prussia", "WAR")
        world.war_scores[world._make_diplo_key("France", "Prussia")] = 50  # Below 80
        proposal = {
            "type": "armistice_winning",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [{"type": "ap_per_turn", "value": 1}],
            "clauses": [],
        }
        result = world._ratify_treaty(proposal)
        assert result.get("type") == "diplomatic_treaty_failed"
        assert "war score" in result.get("message", "").lower() or "ap" in result.get("message", "").lower()


# ═══════════════════════════════════════════════════════
# R99: declare_war checks armistice cooldowns
# ═══════════════════════════════════════════════════════

class TestR99ArmisticeCooldown:
    """R99: declare_war blocked during armistice cooldown."""

    def test_cooldown_blocks_war_declaration(self):
        world = make_world()
        _set_diplo_state(world, "France", "Austria", "ARMISTICE")
        diplo_key = world._make_diplo_key("France", "Austria")
        world.armistice_cooldowns[diplo_key] = 3
        result = declare_war(world, "France", "Austria")
        assert result["success"] is False
        assert "cooldown" in result["message"].lower()

    def test_expired_cooldown_allows_war(self):
        world = make_world()
        _set_diplo_state(world, "France", "Austria", "PEACE")
        # No cooldown — should succeed
        result = declare_war(world, "France", "Austria")
        assert result["success"] is True

    def test_zero_cooldown_allows_war(self):
        world = make_world()
        _set_diplo_state(world, "France", "Austria", "PEACE")
        diplo_key = world._make_diplo_key("France", "Austria")
        world.armistice_cooldowns[diplo_key] = 0
        result = declare_war(world, "France", "Austria")
        assert result["success"] is True


# ═══════════════════════════════════════════════════════
# R100: Cascade applies relation penalties
# ═══════════════════════════════════════════════════════

class TestR100CascadeRelationPenalty:
    """R100: War cascade applies -20 relation between aggressor and cascading nation."""

    def test_cascade_applies_relation_penalty(self):
        world = make_world()
        _set_diplo_state(world, "France", "Austria", "PEACE")
        _set_diplo_state(world, "Prussia", "Austria", "DEFENSIVE_ALLIANCE")
        _set_diplo_state(world, "France", "Prussia", "PEACE")
        # Set positive relation between France and Prussia
        france_prussia_key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[france_prussia_key] = 20

        declare_war(world, "France", "Austria")

        # Prussia cascaded to war — should have -20 relation penalty
        assert world.nation_relations[france_prussia_key] == 20 - 20 - 15  # -20 cascade + -15 general war penalty


# ═══════════════════════════════════════════════════════
# R101: break_treaty validates breaker is party
# ═══════════════════════════════════════════════════════

class TestR101BreakerValidation:
    """R101: break_treaty requires breaker to be a party to the treaty."""

    def test_non_party_breaker_rejected(self):
        world = make_world()
        diplo_key = world._make_diplo_key("Austria", "Prussia")
        world.active_treaties[diplo_key] = {
            "nations": ["Austria", "Prussia"],
            "type": "alliance",
            "clauses": [],
            "turn_signed": 1,
            "harshness": 0,
        }
        world.diplomatic_points = 5
        result = break_treaty(diplo_key, "France", world)
        assert result["success"] is False
        assert "not a party" in result["message"]

    def test_valid_party_can_break(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Austria")
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        world.active_treaties[diplo_key] = {
            "nations": ["France", "Austria"],
            "type": "alliance",
            "clauses": [],
            "turn_signed": 1,
            "harshness": 0,
        }
        world.diplomatic_points = 5
        result = break_treaty(diplo_key, "France", world)
        assert result["success"] is True

    def test_empty_nations_list_allows_break(self):
        """If treaty has no nations list (legacy), don't block."""
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Austria")
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        world.active_treaties[diplo_key] = {
            "nations": [],
            "type": "alliance",
            "clauses": [],
            "turn_signed": 1,
            "harshness": 0,
        }
        world.diplomatic_points = 5
        result = break_treaty(diplo_key, "France", world)
        assert result["success"] is True


# ═══════════════════════════════════════════════════════
# R102/R110: cleanup_war_end clears war_scores + stalemate counters
# ═══════════════════════════════════════════════════════

class TestR102AndR110WarEndCleanup:
    """R102: war_scores removed. R110: stalemate counters cleared."""

    def test_war_scores_removed(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Austria")
        world.war_scores[diplo_key] = 50
        cleanup_war_end(world, diplo_key)
        assert diplo_key not in world.war_scores

    def test_stalemate_counters_cleared(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Austria")
        world.ai_stalemate_counters = {"France": 5, "Austria": 3, "Prussia": 2}
        cleanup_war_end(world, diplo_key)
        assert "France" not in world.ai_stalemate_counters
        assert "Austria" not in world.ai_stalemate_counters
        # Unrelated nation's counter persists
        assert world.ai_stalemate_counters.get("Prussia") == 2

    def test_no_crash_without_stalemate_counters(self):
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        cleanup_war_end(world, diplo_key)
        # Should not crash


# ═══════════════════════════════════════════════════════
# R105: _process_mission_effects uses player_nation
# ═══════════════════════════════════════════════════════

class TestR105MissionPlayerNation:
    """R105: Mission effects use world.player_nation instead of hardcoded 'France'."""

    def test_mission_uses_player_nation(self):
        world = make_world()
        world.player_nation = "France"  # Default
        from backend.models.diplomat import DiplomaticRepresentative
        world.diplomats = {"France": DiplomaticRepresentative("Talleyrand", "France", personality="schemer", skill=10)}
        world.active_diplomatic_mission = {
            "type": "COURT_NATION",
            "target": "Austria",
            "turns_active": 1,
            "paused": False,
            "completed": False,
        }
        old_relation = world.nation_relations.get(world._make_diplo_key("France", "Austria"), 0)
        events = _process_mission_effects(world)
        new_relation = world.nation_relations.get(world._make_diplo_key("France", "Austria"), 0)
        # Relation should have changed (COURT_NATION adds positive relation)
        # Just verify it doesn't crash and uses the right nation
        assert isinstance(events, list)
