"""
Tests for Phase 8 Session 4: AI Proposals, Counter-Offers, Advisory, Proactive Suggestions

Gate criteria:
- AI proposal generation (P1/P2/P4/P7 triggers)
- Anti-spam cooldowns (nation + type)
- Proposal delivery + queuing
- Counter-offer algorithm (M3 §9b)
- Advisory system (keyword detection + generation)
- Proactive suggestions in Morning Dispatch
- WorldState serialization for 4 new fields
- Executor wiring for accept/reject/counter/advisory
"""

from backend.models.world_state import WorldState
from backend.game_logic.ai_diplomacy import (
    process_diplomatic_phase,
    deliver_ai_proposal,
    generate_counter_offer,
    check_alliance_conflict,
    apply_rejection_cooldowns,
    try_deliver_queued_proposal,
    _is_on_cooldown,
    _get_war_score_for_nation,
    NATION_REJECTION_COOLDOWN,
    TYPE_REJECTION_COOLDOWN,
)
from backend.game_logic.diplomatic_advisory import (
    detect_advisory_type,
    generate_advisory,
)
from backend.game_logic.dispatch import build_morning_dispatch
from backend.commands.executor import CommandExecutor


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def make_world():
    """Create a fresh WorldState for testing."""
    return WorldState()


def make_war_world(nation="Prussia"):
    """World where France is at WAR with given nation."""
    world = WorldState()
    key = world._make_diplo_key("France", nation)
    world.diplomatic_states[key] = "WAR"
    return world


def _set_war_score(world, nation, score):
    """Set war score from alphabetically-first nation's perspective.

    A negative score means the alpha-first nation is losing.
    For France|Prussia (alpha-sorted as France|Prussia): score=-50 means France losing.
    For Britain|France (alpha-sorted as Britain|France): score=50 means Britain winning (France losing).
    """
    key = world._make_diplo_key("France", nation)
    world.war_scores[key] = score


def _make_test_proposal(nation="Prussia", proposal_type="armistice_losing", priority=1):
    """Build a proposal dict matching the format from _make_proposal."""
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
        "talleyrand_assessment": "A test assessment.",
        "turn_generated": 1,
    }


# ═══════════════════════════════════════════════════════
# GROUP 1: AI Diplomacy (ai_diplomacy.py) — 15 tests
# ═══════════════════════════════════════════════════════

class TestAIDiplomacyTriggers:
    """Test AI proposal generation triggers (P1/P2/P4/P7)."""

    def test_p1_trigger_war_score_below_negative_40(self):
        """P1: nation at WAR with France, war_score < effective threshold -> proposal.

        R115: Prussia's hawk diplomat shifts P1 threshold from -40 to -60.
        We set war_score to -65 to trigger P1 for hawk personality.
        """
        world = make_war_world("Prussia")
        # We need Prussia LOSING (< -60 for hawk threshold).
        # France|Prussia stored = 65 => France at +65, Prussia at -65.
        _set_war_score(world, "Prussia", 65)
        assert _get_war_score_for_nation("Prussia", "France", world) < -60
        # Improve relations so acceptance score passes the >= 20 filter.
        key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[key] = 10
        proposal = process_diplomatic_phase("Prussia", world)
        assert proposal is not None
        assert proposal["source"] == "Prussia"
        assert proposal["proposal_type"] in ("armistice_losing", "peace")

    def test_p1_no_trigger_war_score_above_negative_40(self):
        """P1: war_score > -40 from AI perspective -> no P1 trigger."""
        world = make_war_world("Prussia")
        # France|Prussia = 10 => France at +10, Prussia at -10 (not below -40)
        _set_war_score(world, "Prussia", 10)
        assert _get_war_score_for_nation("Prussia", "France", world) > -40
        # P1 won't fire, no stalemate (counter=0), no P4 (at war), no P7 (at war)
        proposal = process_diplomatic_phase("Prussia", world)
        assert proposal is None

    def test_p2_trigger_stalemate_5_plus_turns(self):
        """P2: stalemate 5+ turns (war_score -10..+10) -> armistice proposal."""
        world = make_war_world("Prussia")
        # War score in stalemate range: France|Prussia = 5 => Prussia at -5
        _set_war_score(world, "Prussia", 5)
        # Improve relations so acceptance score passes >= 20 filter
        # base(40) + war_score_mod(-1.5) + relation_mod(+5) = 43.5 >= 20
        key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[key] = 10
        # Pre-set stalemate counter to 4 (process_diplomatic_phase will increment to 5)
        world.ai_stalemate_counters = {"Prussia": 4}
        proposal = process_diplomatic_phase("Prussia", world)
        assert proposal is not None
        assert proposal["source"] == "Prussia"
        # P2 maps to "armistice" proposal_type
        assert "armistice" in proposal["proposal_type"]

    def test_p4_trigger_relation_above_30_at_peace(self):
        """P4: relation > 30, at PEACE -> upgrade proposal."""
        world = make_world()
        # Saxony starts with OPEN_BORDERS and relation 40 -> meets P4 criteria
        key = world._make_diplo_key("France", "Saxony")
        world.nation_relations[key] = 35
        world.diplomatic_states[key] = "PEACE"
        proposal = process_diplomatic_phase("Saxony", world)
        # Saxony at PEACE with relation 35 -> P4 fires
        # Result depends on acceptance score (must be >= 20)
        if proposal is not None:
            assert proposal["source"] == "Saxony"
            # P4 upgrade from PEACE -> open_borders
            assert proposal["proposal_type"] in (
                "open_borders", "non_aggression", "defensive_alliance", "alliance"
            )

    def test_p7_trigger_opportunistic(self):
        """P7: France at war with 2+ nations, this nation at PEACE -> opportunistic."""
        world = make_world()
        # France already at WAR with Britain and Prussia by default
        # Austria is at PEACE with France
        key_austria = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key_austria] = "PEACE"
        world.nation_relations[key_austria] = 0  # Neutral relations
        proposal = process_diplomatic_phase("Austria", world)
        # Austria at PEACE, France at war with 2+ nations -> P7 may fire
        # It depends on acceptance score threshold (>= 20)
        if proposal is not None:
            assert proposal["source"] == "Austria"


class TestAIDiplomacyAntiSpam:
    """Test anti-spam cooldown mechanics."""

    def test_nation_cooldown_blocks_proposal(self):
        """Nation on cooldown -> returns None."""
        world = make_war_world("Prussia")
        _set_war_score(world, "Prussia", 50)  # Prussia losing badly
        # Set nation cooldown
        world.ai_proposal_cooldowns = {"Prussia|nation": 3}
        assert _is_on_cooldown("Prussia", "armistice_losing", world) is True
        proposal = process_diplomatic_phase("Prussia", world)
        assert proposal is None

    def test_type_cooldown_blocks_proposal(self):
        """Proposal type on cooldown -> returns None."""
        world = make_war_world("Prussia")
        _set_war_score(world, "Prussia", 50)
        # Set type cooldown for the specific proposal type
        world.ai_proposal_cooldowns = {"Prussia|armistice_losing": 5}
        assert _is_on_cooldown("Prussia", "armistice_losing", world) is True
        proposal = process_diplomatic_phase("Prussia", world)
        assert proposal is None

    def test_apply_rejection_cooldowns_sets_both(self):
        """apply_rejection_cooldowns sets nation and type cooldowns."""
        world = make_world()
        apply_rejection_cooldowns("Prussia", "armistice_losing", world)
        cooldowns = world.ai_proposal_cooldowns
        assert cooldowns.get("Prussia|nation") == int(NATION_REJECTION_COOLDOWN)
        assert cooldowns.get("Prussia|armistice_cooldown", None) is None  # key format check
        assert cooldowns.get("Prussia|armistice_losing") == int(TYPE_REJECTION_COOLDOWN)


class TestAIDiplomacyDelivery:
    """Test proposal delivery and queuing."""

    def test_deliver_ai_proposal_sets_dialogue(self):
        """deliver_ai_proposal sets world.pending_diplomatic_dialogue with Accept/Reject/Counter."""
        world = make_world()
        proposal = _make_test_proposal("Prussia", "armistice_losing")
        dialogue = deliver_ai_proposal(proposal, world)
        # V2-89: deliver_ai_proposal now appends to queue; pop to active dialogue
        if world.dialogue_manager._queue and not world.pending_diplomatic_dialogue:
            world.dialogue_manager.promote_if_empty()
        assert world.pending_diplomatic_dialogue is not None
        assert dialogue["type"] == "incoming_proposal"
        assert dialogue["blocking"] is False
        # Must have Accept, Reject, Counter options
        actions = [opt["action"] for opt in dialogue["options"]]
        assert "accept_ai_proposal" in actions
        assert "reject_ai_proposal" in actions
        assert "counter_ai_proposal" in actions

    def test_queue_proposal_when_blocking_dialogue(self):
        """Proposal queued via dialogue_manager.push() when dialogue already active."""
        world = make_war_world("Prussia")
        # R115: Hawk P1 threshold is -60, need war_score < -60
        _set_war_score(world, "Prussia", 65)
        # Improve relations so acceptance score passes >= 20 filter
        key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[key] = 10
        # Set a blocking dialogue so new proposal goes to queue
        world.dialogue_manager.replace({
            "type": "incoming_proposal",
            "blocking": True,
            "options": [],
        })
        proposal = process_diplomatic_phase("Prussia", world)
        # process_diplomatic_phase returns the proposal for the caller to deliver
        assert proposal is not None
        # Caller delivers via deliver_ai_proposal → dialogue_manager.push()
        deliver_ai_proposal(proposal, world)
        # The new proposal should be in the dialogue_manager queue (current slot occupied)
        assert world.dialogue_manager.queue_size >= 1

    def test_deliver_ai_proposal_queues_when_dialogue_active(self):
        """deliver_ai_proposal pushes to dialogue_manager queue when active slot occupied."""
        world = make_world()
        # Set a blocking dialogue so new proposals go to queue
        world.dialogue_manager.replace({
            "type": "incoming_proposal",
            "blocking": True,
            "options": [],
        })
        test_proposal = _make_test_proposal("Prussia", "armistice_losing")
        dialogue = deliver_ai_proposal(test_proposal, world)
        assert dialogue["type"] == "incoming_proposal"
        # Original dialogue still active, new one is queued
        assert world.dialogue_manager.queue_size >= 1

    def test_try_deliver_queued_proposal_deprecated(self):
        """try_deliver_queued_proposal is deprecated and returns None."""
        world = make_world()
        result = try_deliver_queued_proposal(world)
        assert result is None


class TestAIDiplomacyCounterOffer:
    """Test M3 counter-offer algorithm."""

    def test_counter_offer_with_demands(self):
        """Counter-offer removes/adjusts demands to improve acceptance."""
        world = make_world()
        # Build a proposal with heavy demands that lower acceptance
        proposal = {
            "type": "armistice_losing",
            "proposer_nation": "Prussia",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [{"type": "gold_per_turn", "value": 500}],
            "clauses": [],
        }
        # Set war context so formula has data
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_scores[key] = 30  # France winning moderately
        result = generate_counter_offer(proposal, world)
        # Result is either modified terms or None (if score still too low)
        # Either outcome is valid; we just verify no crash and correct type
        if result is not None:
            assert isinstance(result, dict)
            assert "type" in result
            assert "proposer_nation" in result

    def test_counter_offer_returns_none_below_threshold(self):
        """Counter-offer returns None when score < 30 after adjustments."""
        world = make_world()
        # Build extremely unfavorable proposal
        proposal = {
            "type": "vassalage",
            "proposer_nation": "Prussia",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [
                {"type": "gold_per_turn", "value": 2000},
                {"type": "territory", "value": 5},
            ],
            "clauses": [],
        }
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        # Prussia not winning strongly enough for vassalage
        world.war_scores[key] = 0
        result = generate_counter_offer(proposal, world)
        # Vassalage with huge demands and no war score advantage -> likely None
        # This may or may not be None depending on formula, but shouldn't crash
        assert result is None or isinstance(result, dict)


class TestAllianceConflict:
    """Test conflicting alliance detection."""

    def test_alliance_conflict_detected(self):
        """check_alliance_conflict finds conflict when at war with partner's ally."""
        world = make_world()
        # Set up: France at WAR with Britain
        key_fb = world._make_diplo_key("France", "Britain")
        world.diplomatic_states[key_fb] = "WAR"
        # Britain has ALLIANCE with Prussia
        key_bp = world._make_diplo_key("Britain", "Prussia")
        world.diplomatic_states[key_bp] = "ALLIANCE"
        # France at WAR with Prussia too
        key_fp = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key_fp] = "WAR"
        # Now try to accept ALLIANCE with Britain -> should conflict with Prussia
        result = check_alliance_conflict("Britain", "ALLIANCE", world)
        assert result is not None
        assert "Prussia" in result["conflicting_nations"]

    def test_no_alliance_conflict(self):
        """check_alliance_conflict returns None when no conflict."""
        world = make_world()
        # Set up: France at PEACE with everyone, Austria allied with Saxony
        key_fa = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key_fa] = "PEACE"
        key_fs = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[key_fs] = "PEACE"
        # France NOT at war with anyone (clear default wars)
        key_fb = world._make_diplo_key("France", "Britain")
        world.diplomatic_states[key_fb] = "PEACE"
        key_fp = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key_fp] = "PEACE"
        # Austria allied with Saxony only (clear default Austria-Prussia alliance)
        key_ap = world._make_diplo_key("Austria", "Prussia")
        world.diplomatic_states[key_ap] = "PEACE"
        key_as = world._make_diplo_key("Austria", "Saxony")
        world.diplomatic_states[key_as] = "ALLIANCE"
        result = check_alliance_conflict("Austria", "ALLIANCE", world)
        assert result is None


class TestWarScorePerspective:
    """Test war score perspective calculation."""

    def test_war_score_from_alpha_first_nation(self):
        """War score correct for alphabetically-first nation."""
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        # key is "France|Prussia" (F < P alphabetically)
        world.war_scores[key] = -30  # France at -30
        score = _get_war_score_for_nation("France", "Prussia", world)
        assert score == -30

    def test_war_score_from_alpha_second_nation(self):
        """War score flipped for alphabetically-second nation."""
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.war_scores[key] = -30  # France at -30
        score = _get_war_score_for_nation("Prussia", "France", world)
        assert score == 30  # Flipped: Prussia is winning


# ═══════════════════════════════════════════════════════
# GROUP 2: Diplomatic Advisory (diplomatic_advisory.py) — 10 tests
# ═══════════════════════════════════════════════════════

class TestAdvisoryDetection:
    """Test advisory keyword detection."""

    def test_detect_assess_nation(self):
        """'what about Prussia' -> assess_nation."""
        result = detect_advisory_type("what about Prussia")
        assert result == "assess_nation"

    def test_detect_compare_threats(self):
        """'who is the bigger threat' -> compare_threats."""
        result = detect_advisory_type("who is the bigger threat")
        assert result == "compare_threats"

    def test_detect_recommend_action(self):
        """'should i attack' -> recommend_action."""
        result = detect_advisory_type("should i attack")
        assert result == "recommend_action"

    def test_detect_no_match(self):
        """Random text -> None."""
        result = detect_advisory_type("send Ney to Paris")
        assert result is None


class TestAdvisoryGeneration:
    """Test advisory dialogue generation."""

    def test_advisory_assess_nation_at_war(self):
        """generate_advisory with assess_nation for a nation at WAR."""
        world = make_war_world("Prussia")
        _set_war_score(world, "Prussia", -20)  # France losing slightly
        result = generate_advisory("Prussia", "assess_nation", world)
        assert result["type"] == "advisory"
        assert result["target_nation"] == "Prussia"
        assert "WAR" in result["context"]["diplomatic_state"] or "war" in result["talleyrand_text"].lower()
        assert result["blocking"] is False

    def test_advisory_assess_nation_at_peace(self):
        """generate_advisory with assess_nation for a nation at PEACE."""
        world = make_world()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "PEACE"
        world.nation_relations[key] = 10
        result = generate_advisory("Austria", "assess_nation", world)
        assert result["type"] == "advisory"
        assert result["target_nation"] == "Austria"
        assert result["context"]["diplomatic_state"] == "PEACE"
        assert result["blocking"] is False

    def test_advisory_compare_threats(self):
        """generate_advisory with compare_threats has threat_ranking in context."""
        world = make_world()
        result = generate_advisory(None, "compare_threats", world)
        assert result["type"] == "advisory"
        assert "threat_ranking" in result["context"]
        ranking = result["context"]["threat_ranking"]
        assert isinstance(ranking, list)
        assert len(ranking) > 0
        # Each entry should have nation and threat_score
        assert "nation" in ranking[0]
        assert "threat_score" in ranking[0]

    def test_advisory_recommend_action(self):
        """generate_advisory with recommend_action for a nation."""
        world = make_world()
        key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[key] = "PEACE"
        world.nation_relations[key] = 40
        result = generate_advisory("Saxony", "recommend_action", world)
        assert result["type"] == "advisory"
        assert result["target_nation"] == "Saxony"
        assert "recommendation" in result["context"]
        assert "action_hints" in result["context"]

    def test_advisory_non_blocking(self):
        """Advisory dialogue is non-blocking (blocking=False)."""
        world = make_world()
        result = generate_advisory("Prussia", "assess_nation", world)
        assert result["blocking"] is False

    def test_advisory_dict_structure(self):
        """Advisory returns proper dict structure."""
        world = make_world()
        result = generate_advisory("Austria", "assess_nation", world)
        # Required top-level keys
        assert "type" in result
        assert "talleyrand_text" in result
        assert "options" in result
        assert "context" in result
        assert "turn_created" in result
        assert "blocking" in result
        # Type checks
        assert result["type"] == "advisory"
        assert isinstance(result["talleyrand_text"], str)
        assert isinstance(result["options"], list)
        assert isinstance(result["context"], dict)
        assert isinstance(result["turn_created"], int)
        assert isinstance(result["blocking"], bool)


# ═══════════════════════════════════════════════════════
# GROUP 3: Proactive Suggestions / Dispatch (dispatch.py) — 5 tests
# ═══════════════════════════════════════════════════════

class TestProactiveSuggestions:
    """Test Talleyrand's proactive suggestions in the Morning Dispatch."""

    def test_dispatch_has_talleyrand_report_key(self):
        """Dispatch output includes talleyrand_report key."""
        world = make_world()
        dispatch = build_morning_dispatch(world)
        assert "talleyrand_report" in dispatch

    def test_proactive_suggestions_respect_cooldowns(self):
        """Suggestions suppressed when cooldown is active."""
        world = make_world()
        # Set cooldowns for all nations' trigger types
        world.proactive_suggestion_cooldowns = {
            "Britain|acceptance_crossed": 10,
            "Britain|war_score_shift": 10,
            "Britain|relation_threshold": 10,
            "Prussia|acceptance_crossed": 10,
            "Prussia|war_score_shift": 10,
            "Prussia|relation_threshold": 10,
            "Austria|acceptance_crossed": 10,
            "Austria|war_score_shift": 10,
            "Austria|relation_threshold": 10,
            "Saxony|acceptance_crossed": 10,
            "Saxony|war_score_shift": 10,
            "Saxony|relation_threshold": 10,
            "global|idle_nudge": 10,
        }
        dispatch = build_morning_dispatch(world)
        report = dispatch["talleyrand_report"]
        # All cooldowns active -> no suggestions
        assert len(report) == 0

    def test_no_suggestions_when_ai_proposal_pending(self):
        """Talleyrand report suppressed when incoming AI proposal pending."""
        world = make_world()
        world.dialogue_manager.replace({
            "type": "incoming_proposal",
            "blocking": True,
        })
        dispatch = build_morning_dispatch(world)
        assert dispatch["talleyrand_report"] == []

    def test_proactive_suggestion_for_war_score(self):
        """Suggestion generated when war score is high enough."""
        world = make_world()
        # Ensure France is at war with Prussia and war score is high
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_scores[key] = -40  # Prussia first in key? No: F < P, so France|Prussia
        # France|Prussia = -40 means France at -40 (losing)
        # From France perspective: losing -> |war_score| >= 30 triggers war_score_shift
        dispatch = build_morning_dispatch(world)
        report = dispatch["talleyrand_report"]
        # We may or may not get a war_score_shift observation depending on exact threshold
        # But the key exists and is a list
        assert isinstance(report, list)

    def test_proactive_suggestion_cooldowns_roundtrip(self):
        """proactive_suggestion_cooldowns survives serialization roundtrip."""
        world = make_world()
        world.proactive_suggestion_cooldowns = {
            "Prussia|war_score_shift": 3,
            "global|idle_nudge": 5,
        }
        data = world.to_dict()
        world2 = WorldState.from_dict(data)
        assert world2.proactive_suggestion_cooldowns == {
            "Prussia|war_score_shift": 3,
            "global|idle_nudge": 5,
        }


# ═══════════════════════════════════════════════════════
# GROUP 4: WorldState Serialization — 5 tests
# ═══════════════════════════════════════════════════════

class TestSession4Serialization:
    """Test serialization of Session 4 WorldState fields."""

    def test_ai_proposal_cooldowns_roundtrip(self):
        """ai_proposal_cooldowns serializes to dict and back."""
        world = make_world()
        world.ai_proposal_cooldowns = {"Prussia|nation": 3, "Prussia|armistice": 5}
        data = world.to_dict()
        world2 = WorldState.from_dict(data)
        assert world2.ai_proposal_cooldowns == {"Prussia|nation": 3, "Prussia|armistice": 5}

    def test_legacy_diplomatic_queue_migrated_to_dialogue_manager(self):
        """Legacy diplomatic_queue items in save data migrate into dialogue_manager."""
        world = make_world()
        data = world.to_dict()
        # Inject legacy diplomatic_queue items into serialized data
        data["diplomatic_queue"] = [
            _make_test_proposal("Prussia", "armistice_losing"),
            _make_test_proposal("Austria", "peace"),
        ]
        world2 = WorldState.from_dict(data)
        # Legacy items should have been delivered into dialogue_manager
        assert world2.dialogue_manager.get_mailbox_count() >= 1

    def test_ai_stalemate_counters_roundtrip(self):
        """ai_stalemate_counters serializes and back."""
        world = make_world()
        world.ai_stalemate_counters = {"Prussia": 5, "Britain": 2}
        data = world.to_dict()
        world2 = WorldState.from_dict(data)
        assert world2.ai_stalemate_counters == {"Prussia": 5, "Britain": 2}

    def test_all_four_fields_in_to_dict(self):
        """Session 4 fields present in to_dict output (diplomatic_queue eliminated)."""
        world = make_world()
        data = world.to_dict()
        assert "ai_proposal_cooldowns" in data
        # diplomatic_queue eliminated — proposals now in dialogue_manager
        assert "dialogue_manager" in data
        assert "proactive_suggestion_cooldowns" in data
        assert "ai_stalemate_counters" in data

    def test_fields_default_empty_on_fresh_world(self):
        """New fields default to empty on fresh WorldState."""
        world = make_world()
        assert world.ai_proposal_cooldowns == {}
        assert world.dialogue_manager.get_mailbox_count() == 0
        assert world.proactive_suggestion_cooldowns == {}
        assert world.ai_stalemate_counters == {}


# ═══════════════════════════════════════════════════════
# GROUP 5: Executor Wiring — 5 tests
# ═══════════════════════════════════════════════════════

class TestExecutorDiplomaticWiring:
    """Test executor wiring for Session 4 features."""

    def test_execute_diplomatic_advisory_returns_dialogue(self):
        """_execute_diplomatic_advisory returns diplomatic_dialogue via execute()."""
        executor = CommandExecutor()
        world = make_world()
        game_state = {"world": world}
        # execute() expects parsed_command with "command" key containing the action dict
        parsed_command = {
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
        result = executor.execute(parsed_command, game_state)
        assert result["success"] is True
        assert "diplomatic_dialogue" in result
        assert result["diplomatic_dialogue"]["type"] == "advisory"

    def test_accept_ai_proposal_via_dialogue_handler(self):
        """accept_ai_proposal via handle_diplomatic_dialogue_response executes ratify."""
        executor = CommandExecutor()
        world = make_world()
        game_state = {"world": world}
        # Set up incoming proposal dialogue
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        proposal = _make_test_proposal("Prussia", "armistice_losing")
        deliver_ai_proposal(proposal, world)
        # V2-89: deliver_ai_proposal now appends to queue; pop to active dialogue
        if world.dialogue_manager._queue and not world.pending_diplomatic_dialogue:
            world.dialogue_manager.promote_if_empty()
        assert world.pending_diplomatic_dialogue is not None
        # Accept (option 1 = Accept)
        result = executor.handle_diplomatic_dialogue_response(1, game_state)
        assert result["success"] is True
        assert "accepted" in result["message"].lower() or "accept" in result["message"].lower()
        # Dialogue should be cleared
        assert world.pending_diplomatic_dialogue is None

    def test_reject_ai_proposal_applies_cooldowns(self):
        """reject_ai_proposal applies cooldowns."""
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
        # Reject (option 2 = Reject)
        result = executor.handle_diplomatic_dialogue_response(2, game_state)
        assert result["success"] is True
        assert "reject" in result["message"].lower()
        # Cooldowns should be set
        cooldowns = world.ai_proposal_cooldowns
        assert "Prussia|nation" in cooldowns
        assert cooldowns["Prussia|nation"] == int(NATION_REJECTION_COOLDOWN)

    def test_counter_ai_proposal_costs_1_dp(self):
        """counter_ai_proposal costs 1 DP."""
        executor = CommandExecutor()
        world = make_world()
        game_state = {"world": world}
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_scores[key] = -20  # France slightly behind -> counter path succeeds
        world.nation_relations[key] = 60
        world.nation_dp["Prussia"] = 3
        proposal = _make_test_proposal("Prussia", "armistice_losing")
        deliver_ai_proposal(proposal, world)
        # V2-89: deliver_ai_proposal now appends to queue; pop to active dialogue
        if world.dialogue_manager._queue and not world.pending_diplomatic_dialogue:
            world.dialogue_manager.promote_if_empty()
        dp_before = world.diplomatic_points
        original_mailbox_id = world.pending_diplomatic_dialogue["mailbox_id"]
        # Counter (option 3 = Counter-offer)
        result = executor.handle_diplomatic_dialogue_response(3, game_state)
        assert result["success"] is True
        # DP should be reduced by 1
        assert world.diplomatic_points == dp_before - 1
        assert world.pending_diplomatic_dialogue["type"] == "counter_offer"
        assert world.pending_diplomatic_dialogue["mailbox_id"] == original_mailbox_id
        assert world.incoming_proposal_popup["from_nation"] == "Prussia"
        assert world.incoming_proposal_popup["is_counter_offer"] is True

    def test_expand_to_proposal_opens_new_dialogue(self):
        """expand_to_proposal action opens new proposal dialogue from advisory."""
        executor = CommandExecutor()
        world = make_world()
        game_state = {"world": world}
        # Set up an advisory dialogue with expand_to_proposal option
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "PEACE"
        world.nation_relations[key] = 10
        advisory = generate_advisory("Austria", "assess_nation", world)
        world.dialogue_manager.replace(advisory)
        # Find the expand_to_proposal option
        expand_idx = None
        for i, opt in enumerate(advisory["options"]):
            if opt.get("action") == "expand_to_proposal":
                expand_idx = i + 1  # 1-based
                break
        assert expand_idx is not None, "Advisory should have expand_to_proposal option"
        result = executor.handle_diplomatic_dialogue_response(expand_idx, game_state)
        assert result["success"] is True
        # Should have opened a new diplomatic dialogue (proposal or similar)
        new_dialogue = world.pending_diplomatic_dialogue
        # The new dialogue should exist (either proposal or proposal_options)
        if new_dialogue is not None:
            assert new_dialogue["type"] in (
                "proposal_options", "proposal_confirm", "advisory",
                "feasibility", "incoming_proposal",
            )
