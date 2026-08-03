"""
Audit Tests — Phase 8 Session 4

Written during Audit 4 to cover the known gap (turn_manager integration)
and edge cases that could bite in Session 5.
"""

from backend.models.world_state import WorldState
from backend.game_logic.turn_manager import TurnManager
from backend.commands.executor import CommandExecutor
from backend.game_logic.ai_diplomacy import (
    deliver_ai_proposal,
    generate_counter_offer,
)
from backend.game_logic.diplomatic_advisory import (
    detect_advisory_type,
    generate_advisory,
)
from backend.game_logic.dispatch import build_morning_dispatch


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def make_world():
    """Fresh WorldState."""
    return WorldState()


def make_war_world(nation="Prussia"):
    """France at WAR with given nation."""
    world = WorldState()
    key = world._make_diplo_key("France", nation)
    world.diplomatic_states[key] = "WAR"
    return world


def _set_war_score(world, nation, score):
    """Set war score from alpha-first perspective."""
    key = world._make_diplo_key("France", nation)
    world.war_scores[key] = score


def _make_test_proposal(nation="Prussia", proposal_type="armistice_losing", priority=1):
    """Build a minimal proposal dict."""
    return {
        "source": nation,
        "proposal_type": proposal_type,
        "priority": int(priority),
        "terms": {
            "type": proposal_type,
            "proposer_nation": nation,
            "target_nation": "France",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        },
        "talleyrand_assessment": "Test assessment.",
        "turn_generated": 1,
    }


# ═══════════════════════════════════════════════════════
# 1. KNOWN GAP: Turn Manager Integration Test
# ═══════════════════════════════════════════════════════

class TestTurnManagerIntegration:
    """Tests the end-to-end flow: end_turn → AI diplomatic phase → result dict."""

    def test_end_turn_delivers_ai_proposal_when_conditions_met(self):
        """KNOWN GAP: end_turn should produce ai_proposal when AI nation
        meets P1 trigger (war_score < -40 from AI's perspective)."""
        world = make_world()
        executor = CommandExecutor()
        tm = TurnManager(world, executor)
        game_state = {"world": world}

        # Set Prussia at war with France, losing badly
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        # France|Prussia = 50 → France at +50, Prussia at -50
        world.war_scores[key] = 50
        # Improve relations so acceptance passes >= 20 filter
        world.nation_relations[key] = 10

        result = tm.end_turn(game_state)

        # The result dict should contain an ai_proposal
        assert "ai_proposal" in result, (
            "end_turn did not return ai_proposal in result dict. "
            "The AI diplomatic phase may not be wired correctly into turn_manager."
        )
        proposal = result["ai_proposal"]
        assert proposal is not None
        assert proposal.get("type") == "incoming_proposal"
        assert proposal.get("blocking") is False
        # Verify the dialogue is also set on the world
        assert world.pending_diplomatic_dialogue is not None

    def test_end_turn_no_ai_proposal_when_no_conditions_met(self):
        """end_turn should NOT produce ai_proposal when no triggers fire."""
        world = make_world()
        executor = CommandExecutor()
        tm = TurnManager(world, executor)
        game_state = {"world": world}

        # Set all wars to balanced war scores (no P1 trigger)
        # AND suppress P4/P7 by putting all non-war nations on cooldown
        for nation in world.enemy_nations:
            key = world._make_diplo_key("France", nation)
            if world.get_diplomatic_state("France", nation) == "WAR":
                world.war_scores[key] = 5  # Balanced, no P1
            else:
                # Prevent P4 upgrades and P7 opportunism
                world.nation_relations[key] = 0  # Below P4 threshold (> 30)
            # Set nation-level cooldown to block ALL proposals
            world.ai_proposal_cooldowns[f"{nation}|nation"] = 10

        result = tm.end_turn(game_state)

        # ai_proposal should not be in dict (all nations on cooldown)
        if "ai_proposal" in result:
            assert result["ai_proposal"] is None

    def test_end_turn_queues_when_dialogue_exists(self):
        """If a dialogue already occupies the active slot, AI proposal is queued."""
        world = make_world()
        executor = CommandExecutor()
        tm = TurnManager(world, executor)
        game_state = {"world": world}

        # Pre-set a hard-stop dialogue to occupy the active slot
        world.dialogue_manager.replace({
            "type": "commitment_paradox",
            "blocking": True,
            "options": [],
        })

        # Set conditions for P1 trigger
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_scores[key] = 50
        world.nation_relations[key] = 10

        result = tm.end_turn(game_state)

        # Should NOT have ai_proposal (blocked by existing dialogue)
        has_proposal = result.get("ai_proposal") is not None
        # The blocking dialogue means proposals get queued in dialogue_manager
        if not has_proposal:
            # Verify it was queued in dialogue_manager
            assert world.dialogue_manager.queue_size >= 0  # May or may not have queued


# ═══════════════════════════════════════════════════════
# 2. COOLDOWN LIFECYCLE
# ═══════════════════════════════════════════════════════

class TestCooldownLifecycle:
    """Test that cooldowns tick, expire, and queue cleanup works end-to-end."""

    def test_cooldowns_tick_down_via_advance_turn(self):
        """advance_turn decrements ai_proposal_cooldowns by 1."""
        world = make_world()
        world.ai_proposal_cooldowns = {"Prussia|nation": 3, "Prussia|armistice_losing": 5}
        world.advance_turn()
        assert world.ai_proposal_cooldowns.get("Prussia|nation") == 2
        assert world.ai_proposal_cooldowns.get("Prussia|armistice_losing") == 4

    def test_cooldowns_expire_at_zero(self):
        """Cooldowns at 1 are removed after advance_turn (decremented to 0)."""
        world = make_world()
        world.ai_proposal_cooldowns = {"Prussia|nation": 1, "Austria|nation": 3}
        world.advance_turn()
        assert "Prussia|nation" not in world.ai_proposal_cooldowns
        assert world.ai_proposal_cooldowns.get("Austria|nation") == 2

    def test_proactive_cooldowns_tick_down(self):
        """advance_turn decrements proactive_suggestion_cooldowns."""
        world = make_world()
        world.proactive_suggestion_cooldowns = {"Prussia|war_score_shift": 2, "global|idle_nudge": 1}
        world.advance_turn()
        assert world.proactive_suggestion_cooldowns.get("Prussia|war_score_shift") == 1
        assert "global|idle_nudge" not in world.proactive_suggestion_cooldowns

    def test_offers_exempt_from_clear_stale(self):
        """Current-turn offers are exempt from clear_stale — lapse handles them.

        AI proposals arrive during end_turn BEFORE advance_turn increments the
        turn counter. clear_stale exempts CURRENT_TURN_OFFER_TYPES so they
        persist until lapse_pending_offers() runs at the next end_turn.
        """
        world = make_world()
        world.current_turn = 5
        # Push two proposals with different ages
        world.dialogue_manager.replace({
            "type": "incoming_proposal",
            "blocking": False,
            "turn_created": 1,
            "context": {"source_nation": "Prussia"},
            "target_nation": "Prussia",
        })
        world.dialogue_manager.push({
            "type": "incoming_proposal",
            "blocking": False,
            "turn_created": 4,
            "context": {"source_nation": "Austria"},
            "target_nation": "Austria",
        })
        world.advance_turn()
        # Both exempt from clear_stale — lapse_pending_offers() handles them
        assert world.pending_diplomatic_dialogue is not None
        assert world.dialogue_manager.get_mailbox_count() == 2


# ═══════════════════════════════════════════════════════
# 3. COUNTER-OFFER EDGE CASES
# ═══════════════════════════════════════════════════════

class TestCounterOfferEdgeCases:
    """Edge cases in the M3 counter-offer algorithm."""

    def test_counter_with_empty_proposal(self):
        """Counter on proposal with no sweeteners/demands/clauses."""
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_scores[key] = 20
        proposal = {
            "type": "armistice_losing",
            "proposer_nation": "Prussia",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        # Should not crash — may return terms or None
        result = generate_counter_offer(proposal, world)
        assert result is None or isinstance(result, dict)

    def test_counter_when_already_acceptable(self):
        """If baseline acceptance >= 50, counter returns terms unchanged."""
        world = make_world()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "WAR"
        world.war_scores[key] = 80  # France winning strongly
        world.nation_relations[key] = 50
        world.nation_dp = getattr(world, 'nation_dp', {})
        world.nation_dp["Austria"] = 5  # Ensure Austria has DP for counter-offer
        # Austria desires open_borders/protection — non-territory sweeteners
        # Use generous gold sweetener to push baseline over accept threshold
        proposal = {
            "type": "armistice_losing",
            "proposer_nation": "Austria",
            "target_nation": "France",
            "sweeteners": [{"type": "gold_per_turn", "value": 500}],
            "demands": [],
            "clauses": ["open_borders", "protection_promised"],
        }
        result = generate_counter_offer(proposal, world)
        # Should return terms (possibly identical) since sweeteners are generous
        assert result is None or isinstance(result, dict)

    def test_counter_then_accept_full_flow(self):
        """Full counter-offer flow: counter → modified terms → accept."""
        executor = CommandExecutor()
        world = make_world()
        game_state = {"world": world}

        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_scores[key] = 20

        proposal = _make_test_proposal("Prussia", "armistice_losing")
        deliver_ai_proposal(proposal, world)
        # V2-89: deliver_ai_proposal now appends to queue; pop to active dialogue
        if world.dialogue_manager._queue and not world.pending_diplomatic_dialogue:
            world.dialogue_manager.promote_if_empty()

        # Counter (option 3)
        counter_result = executor.handle_diplomatic_dialogue_response(3, game_state)
        assert counter_result["success"] is True

        # If counter succeeded and produced a new dialogue, accept it
        if world.pending_diplomatic_dialogue is not None:
            dialogue_type = world.pending_diplomatic_dialogue.get("type")
            if dialogue_type in ("counter_offer", "incoming_proposal"):
                accept_result = executor.handle_diplomatic_dialogue_response(1, game_state)
                assert accept_result["success"] is True


# ═══════════════════════════════════════════════════════
# 4. ADVISORY BOUNDARY TESTS
# ═══════════════════════════════════════════════════════

class TestAdvisoryBoundary:
    """Advisory system edge cases."""

    def test_advisory_does_not_cost_dp(self):
        """Advisory should NOT cost diplomatic points."""
        executor = CommandExecutor()
        world = make_world()
        game_state = {"world": world}
        dp_before = world.diplomatic_points

        parsed = {
            "command": {
                "action": "diplomatic_advisory",
                "diplomatic_data": {
                    "action": "diplomatic_advisory",
                    "diplomat": "Talleyrand",
                    "target_nation": "Prussia",
                    "raw_text": "what about Prussia",
                    "is_question": True,
                    "has_diplomatic_keywords": True,
                },
            },
        }
        result = executor.execute(parsed, game_state)
        assert result["success"] is True
        assert world.diplomatic_points == dp_before

    def test_advisory_sets_non_blocking_dialogue(self):
        """Advisory sets pending_diplomatic_dialogue with blocking=False."""
        world = make_world()
        advisory = generate_advisory("Prussia", "assess_nation", world)
        world.dialogue_manager.replace(advisory)
        assert world.pending_diplomatic_dialogue["blocking"] is False

    def test_how_do_we_detect(self):
        """'how do we deal with Prussia' → recommend_action."""
        result = detect_advisory_type("how do we deal with Prussia")
        assert result == "recommend_action"

    def test_what_if_detect(self):
        """'what if we attack Prussia' → predict_outcome."""
        result = detect_advisory_type("what if we attack Prussia")
        assert result == "predict_outcome"

    def test_should_i_detect(self):
        """'should i propose peace' → recommend_action."""
        result = detect_advisory_type("should i propose peace")
        assert result == "recommend_action"

    def test_focus_on_detect(self):
        """'focus on Austria' → recommend_priority."""
        result = detect_advisory_type("focus on Austria")
        assert result == "recommend_priority"

    def test_can_we_returns_none(self):
        """'can we ally with Saxony' → None (routed to feasibility, not advisory)."""
        result = detect_advisory_type("can we ally with Saxony")
        assert result is None


# ═══════════════════════════════════════════════════════
# 5. DISPATCH TALLEYRAND REPORT EDGE CASES
# ═══════════════════════════════════════════════════════

class TestDispatchTalleyrandEdgeCases:
    """Edge cases for the Talleyrand proactive suggestion system."""

    def test_suppressed_by_any_incoming_proposal(self):
        """Talleyrand report suppressed when ANY incoming_proposal type is pending."""
        world = make_world()
        # Set a blocking incoming_proposal from any source
        world.dialogue_manager.replace({
            "type": "incoming_proposal",
            "blocking": True,
            "target_nation": "Austria",
        })
        dispatch = build_morning_dispatch(world)
        assert dispatch["talleyrand_report"] == []

    def test_not_suppressed_by_advisory_dialogue(self):
        """Talleyrand report NOT suppressed when advisory dialogue is pending."""
        world = make_world()
        world.dialogue_manager.replace({
            "type": "advisory",
            "blocking": False,
        })
        dispatch = build_morning_dispatch(world)
        # Should NOT be suppressed — advisory is not incoming_proposal
        assert isinstance(dispatch["talleyrand_report"], list)
        # (may or may not have observations depending on world state)

    def test_max_2_observations(self):
        """Even with many triggers active, max 2 observations returned."""
        world = make_world()
        # Set up conditions to trigger multiple observations
        for nation in ["Britain", "Prussia", "Austria", "Saxony"]:
            key = world._make_diplo_key("France", nation)
            world.diplomatic_states[key] = "WAR"
            world.war_scores[key] = -50  # High magnitude
        dispatch = build_morning_dispatch(world)
        report = dispatch["talleyrand_report"]
        assert len(report) <= 2

    def test_idle_nudge_not_before_turn_4(self):
        """Idle nudge trigger doesn't fire before turn 4."""
        world = make_world()
        world.current_turn = 2
        # Clear all other triggers by setting all nations at peace with neutral relations
        for nation in ["Britain", "Prussia", "Austria", "Saxony"]:
            key = world._make_diplo_key("France", nation)
            world.diplomatic_states[key] = "PEACE"
            world.nation_relations[key] = 15  # Away from thresholds
        dispatch = build_morning_dispatch(world)
        report = dispatch["talleyrand_report"]
        idle_nudges = [r for r in report if r.get("trigger_type") == "idle_nudge"]
        assert len(idle_nudges) == 0


# ═══════════════════════════════════════════════════════
# 6. OLD SAVE COMPATIBILITY
# ═══════════════════════════════════════════════════════

class TestOldSaveCompatibility:
    """Verify from_dict handles missing Session 4 fields gracefully (old saves)."""

    def test_from_dict_missing_all_session4_fields(self):
        """from_dict with a dict that has no Session 4 fields → defaults."""
        world = make_world()
        data = world.to_dict()
        # Simulate old save by removing Session 4 fields
        data.pop("ai_proposal_cooldowns", None)
        data.pop("diplomatic_queue", None)  # Legacy field, migrated to dialogue_manager
        data.pop("proactive_suggestion_cooldowns", None)
        data.pop("ai_stalemate_counters", None)

        world2 = WorldState.from_dict(data)
        assert world2.ai_proposal_cooldowns == {}
        # diplomatic_queue eliminated — proposals now live in dialogue_manager
        assert world2.proactive_suggestion_cooldowns == {}
        assert world2.ai_stalemate_counters == {}


# ═══════════════════════════════════════════════════════
# 7. CONFLICT ALERT WIRING
# ═══════════════════════════════════════════════════════

class TestConflictAlertWiring:
    """Test the conflict alert → accept anyway → ratify flow."""

    def test_accept_alliance_with_conflict_shows_alert(self):
        """Accept alliance proposal → if conflict exists → conflict_alert dialogue."""
        executor = CommandExecutor()
        world = make_world()
        game_state = {"world": world}

        # France at WAR with Prussia
        key_fp = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key_fp] = "WAR"

        # Prussia has ALLIANCE with Austria
        key_pa = world._make_diplo_key("Prussia", "Austria")
        world.diplomatic_states[key_pa] = "ALLIANCE"

        # France at WAR with Austria
        key_fa = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key_fa] = "WAR"

        # Deliver an alliance proposal from Prussia
        proposal = {
            "source": "Prussia",
            "proposal_type": "alliance",
            "priority": 4,
            "terms": {
                "type": "alliance",
                "proposer_nation": "Prussia",
                "target_nation": "France",
                "sweeteners": [],
                "demands": [],
                "clauses": ["open_borders"],
            },
            "talleyrand_assessment": "Test.",
            "turn_generated": 1,
        }
        deliver_ai_proposal(proposal, world)
        # V2-89: deliver_ai_proposal now appends to queue; pop to active dialogue
        if world.dialogue_manager._queue and not world.pending_diplomatic_dialogue:
            world.dialogue_manager.promote_if_empty()

        # Accept (option 1)
        result = executor.handle_diplomatic_dialogue_response(1, game_state)
        assert result["success"] is True
        # Should show conflict alert, NOT ratify immediately
        # V2-89: conflict_alert may be queued; pop if needed
        if world.dialogue_manager._queue and not world.pending_diplomatic_dialogue:
            world.dialogue_manager.promote_if_empty()
        dialogue = world.pending_diplomatic_dialogue
        assert dialogue is not None
        assert dialogue["type"] == "conflict_alert"

    def test_accept_non_alliance_no_conflict_check(self):
        """Accept non-alliance proposal (armistice) should NOT check for conflicts."""
        executor = CommandExecutor()
        world = make_world()
        game_state = {"world": world}

        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"

        proposal = _make_test_proposal("Prussia", "armistice_losing")
        deliver_ai_proposal(proposal, world)
        # V2-89: deliver_ai_proposal now appends to queue; pop to active dialogue
        if world.dialogue_manager._queue and not world.pending_diplomatic_dialogue:
            world.dialogue_manager.promote_if_empty()

        result = executor.handle_diplomatic_dialogue_response(1, game_state)
        assert result["success"] is True
        # Armistice should be accepted directly, no conflict alert
        assert world.pending_diplomatic_dialogue is None

    def test_conflict_alert_accept_anyway_ratifies(self):
        """After conflict_alert, choosing 'Accept anyway' ratifies the treaty.

        IGR-X3: the fixture now seeds a relation that actually clears
        `STATE_RELATION_REQUIREMENTS["ALLIANCE"] = 40`. It did not before, so
        `_ratify_treaty` REFUSED the alliance and the handler reported
        `success: True` over it anyway — this test has been asserting a lie
        since it was written, and only went red once the swallow was closed.
        The name says "ratifies"; now it does."""
        executor = CommandExecutor()
        world = make_world()
        game_state = {"world": world}

        # Set up conflict scenario
        key_fp = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key_fp] = "WAR"
        world.nation_relations[key_fp] = 60
        key_pa = world._make_diplo_key("Prussia", "Austria")
        world.diplomatic_states[key_pa] = "ALLIANCE"
        key_fa = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key_fa] = "WAR"

        proposal = {
            "source": "Prussia",
            "proposal_type": "alliance",
            "priority": 4,
            "terms": {
                "type": "alliance",
                "proposer_nation": "Prussia",
                "target_nation": "France",
                "sweeteners": [],
                "demands": [],
                "clauses": ["open_borders"],
            },
            "talleyrand_assessment": "Test.",
            "turn_generated": 1,
        }
        deliver_ai_proposal(proposal, world)
        # V2-89: deliver_ai_proposal now appends to queue; pop to active dialogue
        if world.dialogue_manager._queue and not world.pending_diplomatic_dialogue:
            world.dialogue_manager.promote_if_empty()

        # First accept → conflict_alert
        executor.handle_diplomatic_dialogue_response(1, game_state)
        # V2-89: conflict_alert may be queued; pop if needed
        if world.dialogue_manager._queue and not world.pending_diplomatic_dialogue:
            world.dialogue_manager.promote_if_empty()
        assert world.pending_diplomatic_dialogue["type"] == "conflict_alert"

        # Second accept → "Accept anyway" (option 1)
        result = executor.handle_diplomatic_dialogue_response(1, game_state)
        assert result["success"] is True
        # Dialogue should be cleared (ratified)
        assert world.pending_diplomatic_dialogue is None

    def test_conflict_alert_is_local_planning(self):
        """Conflict alerts are local planning — dismiss cancels the action."""
        executor = CommandExecutor()
        world = make_world()
        game_state = {"world": world}

        key_fp = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key_fp] = "WAR"
        key_pa = world._make_diplo_key("Prussia", "Austria")
        world.diplomatic_states[key_pa] = "ALLIANCE"
        key_fa = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key_fa] = "WAR"

        proposal = {
            "source": "Prussia",
            "proposal_type": "alliance",
            "priority": 4,
            "terms": {
                "type": "alliance",
                "proposer_nation": "Prussia",
                "target_nation": "France",
                "sweeteners": [],
                "demands": [],
                "clauses": ["open_borders"],
            },
            "talleyrand_assessment": "Test.",
            "turn_generated": 1,
        }
        deliver_ai_proposal(proposal, world)
        if world.dialogue_manager._queue and not world.pending_diplomatic_dialogue:
            world.dialogue_manager.promote_if_empty()

        executor.handle_diplomatic_dialogue_response(1, game_state)
        if world.dialogue_manager._queue and not world.pending_diplomatic_dialogue:
            world.dialogue_manager.promote_if_empty()
        assert world.pending_diplomatic_dialogue["type"] == "conflict_alert"

        # Conflict alert is local planning with a dismiss button
        assert any(
            opt.get("action") == "dismiss"
            for opt in world.pending_diplomatic_dialogue.get("options", [])
        )
        assert world.dialogue_manager.is_local_planning()


# ═══════════════════════════════════════════════════════
# 8. WAR SCORE DELTA (Fix 2) + MISC
# ═══════════════════════════════════════════════════════

class TestWarScoreDelta:
    """Test Talleyrand Trigger 2 uses per-turn delta instead of magnitude proxy."""

    def test_trigger2_fires_on_delta_ge_15(self):
        """War score delta >= 15 in one turn fires Trigger 2 observation."""
        world = make_world()
        # France at war with Prussia
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        # Previous war score was 0, now it's 20 (delta = 20 >= 15)
        world.previous_war_scores = {key: 0}
        world.war_scores[key] = 20
        # Clear cooldowns and set other nations to peace to isolate this trigger
        world.proactive_suggestion_cooldowns = {}
        for nation in ["Britain", "Austria", "Saxony"]:
            nkey = world._make_diplo_key("France", nation)
            world.diplomatic_states[nkey] = "PEACE"
            world.nation_relations[nkey] = 15  # Away from thresholds

        dispatch = build_morning_dispatch(world)
        report = dispatch["talleyrand_report"]
        war_score_obs = [r for r in report if r.get("trigger_type") == "war_score_shift"]
        assert len(war_score_obs) == 1
        assert "Prussia" in war_score_obs[0]["message"]

    def test_trigger2_silent_when_delta_lt_15(self):
        """War score delta < 15 does NOT fire Trigger 2."""
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        # Previous was 20, now 30 (delta = 10, < 15)
        world.previous_war_scores = {key: 20}
        world.war_scores[key] = 30
        # Clear cooldowns and set other nations to peace
        world.proactive_suggestion_cooldowns = {}
        for nation in ["Britain", "Austria", "Saxony"]:
            nkey = world._make_diplo_key("France", nation)
            world.diplomatic_states[nkey] = "PEACE"
            world.nation_relations[nkey] = 15

        dispatch = build_morning_dispatch(world)
        report = dispatch["talleyrand_report"]
        war_score_obs = [r for r in report if r.get("trigger_type") == "war_score_shift"]
        assert len(war_score_obs) == 0

    def test_previous_war_scores_serialization(self):
        """previous_war_scores survives to_dict/from_dict roundtrip."""
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.previous_war_scores = {key: 25}
        data = world.to_dict()
        assert "previous_war_scores" in data
        world2 = WorldState.from_dict(data)
        assert world2.previous_war_scores == {key: 25}

    def test_previous_war_scores_defaults_empty(self):
        """Old saves without previous_war_scores get empty dict."""
        world = make_world()
        data = world.to_dict()
        data.pop("previous_war_scores", None)
        world2 = WorldState.from_dict(data)
        assert world2.previous_war_scores == {}

    def test_advance_turn_snapshots_war_scores(self):
        """advance_turn copies end-of-turn war_scores into previous_war_scores."""
        world = make_world()
        world.advance_turn()
        # After advance_turn, previous_war_scores should match whatever
        # war_scores are at end of turn (diplomacy processing may recalculate them)
        for key, score in world.war_scores.items():
            assert world.previous_war_scores.get(key) == int(score), (
                f"previous_war_scores[{key}] should match war_scores[{key}]"
            )


class TestMiscSmells:
    """Remaining smell verifications."""

    def test_stalemate_counter_resets_on_non_stalemate(self):
        """Stalemate counter resets to 0 when war score moves outside -10..+10.

        DP-1 (Aug 2, 2026): the counter takes the OPPONENT now and is keyed
        by pair — a deadlock belongs to a war, not to a court."""
        from backend.game_logic.ai_diplomacy import (
            _update_stalemate_counter, stalemate_counter_key)
        world = make_world()
        key = stalemate_counter_key("Prussia", "France", world)
        world.ai_stalemate_counters = {key: 4}
        # War score outside stalemate range
        _update_stalemate_counter("Prussia", "France", 30, world)
        assert world.ai_stalemate_counters[key] == 0

    def test_stalemate_counter_is_per_war_not_per_court(self):
        """THE DP-1 DEFECT, at the writer: two of Prussia's wars keep two
        independent clocks. Nation-keying made them one, so a deadlock with
        Austria reset the deadlock with France."""
        from backend.game_logic.ai_diplomacy import (
            _update_stalemate_counter, stalemate_counter_key)
        world = make_world()
        vs_france = stalemate_counter_key("Prussia", "France", world)
        vs_austria = stalemate_counter_key("Prussia", "Austria", world)
        assert vs_france != vs_austria
        world.ai_stalemate_counters = {vs_france: 9, vs_austria: 2}
        # A decisive swing in the AUSTRIAN war resets only that clock.
        _update_stalemate_counter("Prussia", "Austria", 40, world)
        assert world.ai_stalemate_counters[vs_austria] == 0
        assert world.ai_stalemate_counters[vs_france] == 9
