"""W6-0 — Correctness A: dialogue identity + typed-answer routing.

Wave 6 slice 0 (docs/WAVE6_FUN_FACTOR_SPEC.md §2), covering:
  - BUG-CA-7 (P1): a dialogue response must bind to the PRESENTED dialogue's
    identity, never to whatever is on top of the stack by answer time
    (live audit: answering Britain's settlement offer rejected Saxony's
    never-seen proposal).
  - BUG-CA-1: typed answer tokens the game itself offered ("trust", "2",
    "plunder") resolve the pending question instead of falling into the
    parser.
  - BUG-CA-10: the typed-surface re-prompt enumerates the numbered options.
  - BUG-CA-8: a failed-response re-mount must not degrade the resolved
    diplomat to "Unknown diplomat".
  - The reversed ai_proposal_accepted/rejected campaign-log direction.
"""

import pytest
from fastapi.testclient import TestClient

from backend.commands.executor import CommandExecutor
from backend.models.dialogue_manager import DialogueManager
from backend.models.world_state import WorldState

from tests.conftest import WorldFactory


# ════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════

def _proposal_dialogue(nation: str, proposal_type: str = "open_borders") -> dict:
    """Minimal incoming_proposal dialogue matching the ai_diplomacy shape."""
    return {
        "type": "incoming_proposal",
        "target_nation": nation,
        "talleyrand_text": f"Sire, {nation} proposes {proposal_type}.",
        "options": [
            {"label": "Accept", "description": "", "action": "accept_ai_proposal"},
            {"label": "Reject", "description": "", "action": "reject_ai_proposal"},
            {"label": "Counter-offer", "description": "", "action": "counter_ai_proposal"},
        ],
        "context": {
            "proposal": {"type": proposal_type, "proposer_nation": nation},
            "source_nation": nation,
            "proposal_type": proposal_type,
            "decision_reason": "",
        },
        "turn_created": 1,
        "blocking": False,
    }


# ════════════════════════════════════════════════════════════════════════
# Dialogue-id stamping (DialogueManager)
# ════════════════════════════════════════════════════════════════════════

class TestDialogueIdStamping:
    def test_push_stamps_monotonic_ids(self):
        dm = DialogueManager()
        a = _proposal_dialogue("Britain")
        b = _proposal_dialogue("Saxony")
        dm.push(a)
        dm.push(b)
        assert a["dialogue_id"] == 1
        assert b["dialogue_id"] == 2

    def test_replace_preserves_carried_id(self):
        """Enrichment flows carry the same dict forward — same matter, same id."""
        dm = DialogueManager()
        a = _proposal_dialogue("Britain")
        dm.push(a)
        original_id = a["dialogue_id"]
        a["talleyrand_text"] = "updated"
        dm.replace(a)
        assert a["dialogue_id"] == original_id

    def test_replace_stamps_fresh_id_on_new_dict(self):
        """A freshly-built dict is a NEW matter — it must get a new identity
        (inheriting the old id is exactly the BUG-CA-7 misroute class)."""
        dm = DialogueManager()
        a = _proposal_dialogue("Britain")
        dm.push(a)
        b = _proposal_dialogue("Saxony")
        dm.replace(b)
        assert b["dialogue_id"] != a["dialogue_id"]

    def test_preempt_stamps(self):
        dm = DialogueManager()
        a = _proposal_dialogue("Britain")
        dm.push(a)
        hard = {"type": "commitment_paradox", "options": [], "turn_created": 1}
        dm.preempt(hard)
        assert "dialogue_id" in hard
        assert hard["dialogue_id"] != a["dialogue_id"]

    def test_popup_payload_mirrors_id(self):
        dm = DialogueManager()
        a = _proposal_dialogue("Britain")
        a["popup_payload"] = {"from_nation": "Britain"}
        dm.push(a)
        assert a["popup_payload"]["dialogue_id"] == a["dialogue_id"]

    def test_ids_round_trip_serialization(self):
        dm = DialogueManager()
        a = _proposal_dialogue("Britain")
        b = _proposal_dialogue("Saxony")
        dm.push(a)
        dm.push(b)
        restored = DialogueManager.from_dict(dm.to_dict())
        assert restored.peek()["dialogue_id"] == a["dialogue_id"]
        assert restored.iter_queue()[0]["dialogue_id"] == b["dialogue_id"]
        # The counter continues monotonically after a load — no id reuse.
        c = _proposal_dialogue("Austria")
        restored.push(c)
        assert c["dialogue_id"] == 3

    def test_legacy_migration_stamps_missing_ids(self):
        """A pre-W6-0 save (dialogues without ids) gets stamped on load."""
        data = {
            "current": _proposal_dialogue("Britain"),
            "queue": [_proposal_dialogue("Saxony")],
            "next_mailbox_id": 5,
        }
        dm = DialogueManager.from_dict(data)
        assert dm.peek()["dialogue_id"] is not None
        assert dm.iter_queue()[0]["dialogue_id"] is not None
        assert dm.peek()["dialogue_id"] != dm.iter_queue()[0]["dialogue_id"]

    def test_world_round_trip_preserves_ids(self):
        world = WorldFactory.basic()
        a = _proposal_dialogue("Britain")
        world.dialogue_manager.push(a)
        restored = WorldState.from_dict(world.to_dict())
        assert (restored.dialogue_manager.peek()["dialogue_id"]
                == a["dialogue_id"])


# ════════════════════════════════════════════════════════════════════════
# BUG-CA-7 — the stale-dialogue guard (executor level)
# ════════════════════════════════════════════════════════════════════════

class TestStaleDialogueGuard:
    def _mount_two(self, world):
        """Mount Britain's dialogue (current) with Saxony's queued behind."""
        britain = _proposal_dialogue("Britain")
        saxony = _proposal_dialogue("Saxony")
        world.dialogue_manager.push(britain)
        world.dialogue_manager.push(saxony)
        return britain, saxony

    def test_matching_id_applies(self):
        world = WorldFactory.basic()
        executor = CommandExecutor()
        britain, saxony = self._mount_two(world)
        result = executor.handle_diplomatic_dialogue_response(
            2, {"world": world}, dialogue_id=britain["dialogue_id"])
        assert result["success"] is True
        assert "Britain" in result["message"]

    def test_stale_id_refused_and_reattaches_current(self):
        world = WorldFactory.basic()
        executor = CommandExecutor()
        britain, saxony = self._mount_two(world)
        # Answer carries SAXONY's id while BRITAIN is on top → refuse.
        result = executor.handle_diplomatic_dialogue_response(
            2, {"world": world}, dialogue_id=saxony["dialogue_id"])
        assert result["success"] is False
        assert result["stale_dialogue"] is True
        # The CURRENT dialogue is re-attached, and nothing was applied.
        assert result["diplomatic_dialogue"]["dialogue_id"] == britain["dialogue_id"]
        assert world.pending_diplomatic_dialogue["dialogue_id"] == britain["dialogue_id"]
        assert world.dialogue_manager.queue_size == 1

    def test_misroute_scenario_end_to_end(self):
        """The audit's exact failure: the top shifted between presentation and
        answer. The stale answer must NOT land on the new top."""
        world = WorldFactory.basic()
        executor = CommandExecutor()
        britain, saxony = self._mount_two(world)
        # The player rendered Britain's dialogue... then the stack shifted
        # (Britain popped, Saxony auto-promoted — the live audit's sequence).
        world.dialogue_manager.pop()
        assert world.pending_diplomatic_dialogue["target_nation"] == "Saxony"
        # The answer still carries Britain's id → refused, Saxony untouched.
        result = executor.handle_diplomatic_dialogue_response(
            2, {"world": world}, dialogue_id=britain["dialogue_id"])
        assert result["success"] is False
        assert result["stale_dialogue"] is True
        assert "Saxony" in result["message"]
        # Saxony's proposal is still pending and unanswered — no relations
        # hit, no rejection cooldown, no reversed log line.
        assert world.pending_diplomatic_dialogue["target_nation"] == "Saxony"
        assert not any(e.get("type") == "ai_proposal_rejected"
                       for e in world.event_log)

    def test_typed_path_omits_id_and_answers_top(self):
        """The terminal path always answers the visible top — no id needed."""
        world = WorldFactory.basic()
        executor = CommandExecutor()
        self._mount_two(world)
        result = executor.handle_diplomatic_dialogue_response(
            2, {"world": world})
        assert result["success"] is True
        assert "Britain" in result["message"]


# ════════════════════════════════════════════════════════════════════════
# Endpoint fixture (main.py wiring)
# ════════════════════════════════════════════════════════════════════════

@pytest.fixture()
def endpoint():
    import backend.main as main_module
    from backend.commands.parser import CommandParser as _CP

    original_parser = main_module.parser
    original_world = main_module.world
    original_game_state = main_module.game_state
    main_module.parser = _CP(use_real_llm=False)
    main_module.world = WorldState()
    main_module.game_state = {"world": main_module.world}
    try:
        yield TestClient(main_module.app), main_module
    finally:
        main_module.parser = original_parser
        main_module.world = original_world
        main_module.game_state = original_game_state


class TestStaleDialogueEndpoint:
    def test_endpoint_passes_dialogue_id_through(self, endpoint):
        client, m = endpoint
        britain = _proposal_dialogue("Britain")
        saxony = _proposal_dialogue("Saxony")
        m.world.dialogue_manager.push(britain)
        m.world.dialogue_manager.push(saxony)
        m.world.dialogue_manager.pop()  # the stack shifts under the popup
        data = client.post("/respond_to_diplomatic_dialogue", json={
            "choice": 2, "dialogue_id": britain["dialogue_id"],
        }).json()
        assert data["success"] is False
        assert data["stale_dialogue"] is True
        assert data["diplomatic_dialogue"]["target_nation"] == "Saxony"
        # Saxony still pending — the guard did not consume it.
        assert m.world.pending_diplomatic_dialogue["target_nation"] == "Saxony"

    def test_endpoint_matching_id_applies(self, endpoint):
        client, m = endpoint
        britain = _proposal_dialogue("Britain")
        m.world.dialogue_manager.push(britain)
        data = client.post("/respond_to_diplomatic_dialogue", json={
            "choice": 2, "dialogue_id": britain["dialogue_id"],
        }).json()
        assert data["success"] is True
        assert m.world.pending_diplomatic_dialogue is None


# ════════════════════════════════════════════════════════════════════════
# BUG-CA-1 — the typed pending-question router
# ════════════════════════════════════════════════════════════════════════

class TestPendingQuestionRouter:
    def _pending_objection(self, world, trust_gain=3):
        world.pending_objection = {
            "type": "major_objection",
            "marshal": "Ney",
            "message": "Ney objects!",
            "original_order": {"action": "defend", "marshal": "Ney"},
            "suggested_alternative": None,
            "compromise": None,
            "trust_gain": trust_gain,
        }

    def test_typed_trust_resolves_pending_objection(self, endpoint):
        client, m = endpoint
        self._pending_objection(m.world)
        ney = m.world.get_marshal("Ney")
        trust_before = ney.trust.value if hasattr(ney.trust, "value") else ney.trust
        data = client.post("/command", json={"command": "trust"}).json()
        assert m.world.pending_objection is None
        trust_after = ney.trust.value if hasattr(ney.trust, "value") else ney.trust
        assert trust_after == trust_before + 3
        assert data.get("objection_resolved") is True

    def test_typed_insist_routes_to_objection_not_diplomacy(self, endpoint):
        client, m = endpoint
        self._pending_objection(m.world)
        data = client.post("/command", json={"command": "insist"}).json()
        assert m.world.pending_objection is None
        # The live-audit failure: "insist" hit the diplomatic handler and
        # answered "no pending diplomatic matter". It must not.
        assert "diplomatic matter" not in data.get("message", "")
        assert "complies" in data.get("message", "")

    def test_typed_digit_picks_dialogue_option(self, endpoint):
        client, m = endpoint
        britain = _proposal_dialogue("Britain")
        m.world.dialogue_manager.push(britain)
        data = client.post("/command", json={"command": "2"}).json()
        assert data["success"] is True
        assert "rejected" in data["message"].lower()
        assert m.world.pending_diplomatic_dialogue is None

    def test_typed_action_id_picks_dialogue_option(self, endpoint):
        client, m = endpoint
        britain = _proposal_dialogue("Britain")
        m.world.dialogue_manager.push(britain)
        data = client.post("/command", json={"command": "reject_ai_proposal"}).json()
        assert data["success"] is True
        assert m.world.pending_diplomatic_dialogue is None

    def test_typed_plunder_resolves_capture_choice(self, endpoint):
        client, m = endpoint
        region_name = next(iter(m.world.regions))
        m.world.pending_capture_choice = {
            "region": region_name,
            "capturer": "Ney",
            "previous_controller": "Prussia",
        }
        data = client.post("/command", json={"command": "plunder"}).json()
        assert data["success"] is True
        assert m.world.pending_capture_choice is None
        assert "plunder" in data["message"].lower()

    def test_tokens_with_nothing_pending_fall_through(self, endpoint):
        """No pending state → the router must not fire; the pipeline handles
        the token exactly as before (corpus/keyword ownership unchanged)."""
        client, m = endpoint
        assert m.world.pending_objection is None
        data = client.post("/command", json={"command": "trust"}).json()
        # Falls to the normal pipeline (parse failure / recovery) — the key
        # assertion is that nothing objection-ish was resolved.
        assert data.get("objection_resolved") is None
        data2 = client.post("/command", json={"command": "plunder"}).json()
        assert data2.get("capture_choice") is None

    def test_digit_with_no_dialogue_parses_normally(self, endpoint):
        client, m = endpoint
        data = client.post("/command", json={"command": "2"}).json()
        # No dialogue pending: the digit is NOT consumed as an answer.
        assert m.world.pending_diplomatic_dialogue is None
        assert isinstance(data.get("message", ""), str)


# ════════════════════════════════════════════════════════════════════════
# BUG-CA-10 — typed re-prompt enumerates the options
# ════════════════════════════════════════════════════════════════════════

class TestOptionEnumeration:
    def test_out_of_range_choice_lists_every_option(self):
        world = WorldFactory.basic()
        executor = CommandExecutor()
        world.dialogue_manager.push(_proposal_dialogue("Britain"))
        result = executor.handle_diplomatic_dialogue_response(
            9, {"world": world})
        assert result["success"] is False
        for label in ("Accept", "Reject", "Counter-offer"):
            assert label in result["message"]
        assert "1-3" in result["message"]


# ════════════════════════════════════════════════════════════════════════
# BUG-CA-8 — re-mount keeps the resolved diplomat
# ════════════════════════════════════════════════════════════════════════

class TestRemountDiplomatFidelity:
    def test_failed_response_remount_keeps_diplomat(self, endpoint):
        client, m = endpoint
        from backend.game_logic.ai_diplomacy import build_ai_proposal_dialogue
        proposal = {
            "source": "Prussia",
            "terms": {"type": "open_borders", "proposer_nation": "Prussia",
                      "target_nation": "France"},
            "talleyrand_assessment": "Hardenberg presses for open roads.",
            "decision_reason": "",
            "proposal_type": "open_borders",
        }
        dialogue = build_ai_proposal_dialogue(proposal, m.world)
        m.world.dialogue_manager.push(dialogue)
        original_name = dialogue["popup_payload"]["diplomat_name"]
        assert original_name not in ("", "Unknown diplomat")

        # A response that fails to resolve → the proposal re-mounts.
        data = client.post("/respond_to_diplomatic_dialogue", json={
            "choice": "gibberish-that-matches-nothing",
        }).json()
        assert data["success"] is False
        remounted = data.get("incoming_proposal")
        assert remounted is not None
        assert remounted["diplomat_name"] == original_name
        assert remounted["diplomat_personality"] not in ("Unknown", "")
        # W6-0: the re-mounted payload carries the identity to answer with.
        assert remounted.get("dialogue_id") == dialogue["dialogue_id"]


# ════════════════════════════════════════════════════════════════════════
# Settlement-offer popup carries the id
# ════════════════════════════════════════════════════════════════════════

class TestSettlementOfferPopupId:
    def test_offer_popup_carries_dialogue_id(self):
        from backend.game_logic.settlement_offers import (
            build_incoming_settlement_offer_popup,
        )
        world = WorldFactory.basic()
        offer_dialogue = {
            "type": "incoming_settlement_offer",
            "offer_id": "offer-1",
            "war_id": "war-1",
            "proposer_nation": "Britain",
            "accepting_side": "France",
            "covered_enemy_participants": ["Britain"],
            "settlement_terms": [{"type": "peace"}],
            "turn_created": 1,
        }
        world.dialogue_manager.push(offer_dialogue)
        popup = build_incoming_settlement_offer_popup(world, offer_dialogue)
        assert popup["dialogue_id"] == offer_dialogue["dialogue_id"]


# ════════════════════════════════════════════════════════════════════════
# Campaign-log direction (the reversed one-liner)
# ════════════════════════════════════════════════════════════════════════

class TestProposalLogDirection:
    def test_rejected_line_names_us_as_the_answerer(self):
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({
            "type": "ai_proposal_rejected",
            "source": "Saxony",
            "proposal_type": "open_borders",
            "decision_reason": "counterparty_reversal",
        })
        assert line.startswith("We rejected Saxony's")
        assert "open borders" in line
        # The cooldown-mechanics tag must not render as a motive.
        assert "counterparty" not in line.lower()

    def test_accepted_line_names_us_as_the_answerer(self):
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({
            "type": "ai_proposal_accepted",
            "source": "Prussia",
            "proposal_type": "trade_agreement",
        })
        assert line.startswith("We accepted Prussia's")

    def test_reject_arm_emits_correct_direction_end_to_end(self):
        from backend.campaign_log import format_event_oneliner
        world = WorldFactory.basic()
        executor = CommandExecutor()
        world.dialogue_manager.push(_proposal_dialogue("Saxony"))
        result = executor.handle_diplomatic_dialogue_response(
            2, {"world": world})
        assert result["success"] is True
        rejected = [e for e in world.event_log
                    if e.get("type") == "ai_proposal_rejected"]
        assert len(rejected) == 1
        line = format_event_oneliner(rejected[0])
        assert line.startswith("We rejected Saxony's")
