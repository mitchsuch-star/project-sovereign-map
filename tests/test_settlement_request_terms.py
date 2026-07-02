"""SC-30 / Slice G1 — the Request Terms lifecycle (July 2, 2026).

The AI settlement-offer producer, mailbox promotion, and the offer answer
verbs landed with the May 2026 SC-5 reversal; this slice ships the one
remaining SC-30 promise: `request_terms` as a REAL lifecycle —

- the affordance appears only when the lifecycle can advance (absent on
  every structural block, disabled-with-named-clock on deterministic
  temporal blocks — never a click-only polite refusal);
- the click writes an observable `settlement_terms_requests` entry (1 DP);
- the next AI phase resolves it: GRANT (a real incoming offer through the
  SAME producer emission, tagged `requested_by_player`) unless the
  answering side is decisively winning -> voiced REFUSAL + cooldown; a war
  that changed shape lapses with a Talleyrand notice.

The two spec-named tests live in `test_incoming_offer_deferral_no_leaks.py`
(inverted from their absence forms in this slice); this file owns the rest
of the lifecycle contract.
"""

from __future__ import annotations

from backend.game_logic.ai_diplomacy import (
    REQUEST_TERMS_COOLDOWN_TURNS,
    REQUEST_TERMS_REFUSAL_WAR_SCORE,
    process_settlement_offer_phase,
)
from backend.game_logic.diplomatic_templates import (
    resolve_settlement_voice_line,
)
from backend.game_logic.settlement_routes import (
    evaluate_request_terms_affordance,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)


def _install_war(world: WorldState, war_id: str = "war_1") -> dict:
    war = make_synthetic_war_instance(
        war_id,
        attackers=["France", "Saxony"],
        defenders=["Austria", "Britain"],
        attacker_leader="France",
        defender_leader="Austria",
        created_turn=1,
    )
    world.war_instances[war_id] = war
    for atk in ("France", "Saxony"):
        for dfd in ("Austria", "Britain"):
            world.diplomatic_states["|".join(sorted([atk, dfd]))] = "WAR"
    world.invalidate_war_instance_indexes()
    return war


def _world(turn: int = 5) -> WorldState:
    world = WorldState()
    world.current_turn = turn
    world.diplomatic_points = 5
    return world


def _request(world: WorldState, war_id: str = "war_1") -> dict:
    from backend.commands.diplomatic_executor import DiplomaticExecutor

    return DiplomaticExecutor(None)._execute_request_terms(
        {"action": "request_terms", "war_id": war_id, "target_nation": ""},
        {"world": world},
    )


class TestRequestVerb:
    def test_request_writes_state_charges_dp_and_voices(self):
        world = _world()
        _install_war(world)
        dp_before = int(world.diplomatic_points)
        result = _request(world)
        assert result["success"] is True, result.get("message")
        assert "next dispatches" in str(result.get("message") or "")
        entry = world.settlement_terms_requests["war_1"]
        assert entry["status"] == "requested"
        assert entry["requested_turn"] == 5
        assert entry["answering_leader"] == "Austria"
        assert int(world.diplomatic_points) == dp_before - 1
        assert result["request_terms_state"]["status"] == "requested"

    def test_ineligible_click_refuses_without_dp_cost(self):
        world = _world()
        # One-to-one war: structurally absent.
        duel = make_synthetic_war_instance(
            "war_1", attackers=["France"], defenders=["Prussia"],
            attacker_leader="France", defender_leader="Prussia",
            created_turn=1,
        )
        world.war_instances["war_1"] = duel
        world.diplomatic_states["France|Prussia"] = "WAR"
        world.invalidate_war_instance_indexes()
        dp_before = int(world.diplomatic_points)
        result = _request(world)
        assert result["success"] is False
        assert str(result.get("error_display") or "").strip()
        assert int(world.diplomatic_points) == dp_before
        assert "war_1" not in world.settlement_terms_requests

    def test_pending_request_click_refuses_with_clock_and_no_double_charge(self):
        world = _world()
        _install_war(world)
        assert _request(world)["success"] is True
        dp_before = int(world.diplomatic_points)
        again = _request(world)
        assert again["success"] is False
        assert again["error"] == "request_pending"
        assert "next dispatches" in str(again.get("error_display") or "")
        assert int(world.diplomatic_points) == dp_before

    def test_insufficient_dp_refuses_before_state_write(self):
        world = _world()
        world.diplomatic_points = 0
        _install_war(world)
        result = _request(world)
        assert result["success"] is False
        assert "Diplomatic Points" in str(result.get("message") or "")
        assert "war_1" not in world.settlement_terms_requests


class TestResolutionPaths:
    def test_refusal_by_winning_court_voices_and_cools_down(self):
        world = _world()
        _install_war(world)
        # Austria decisively winning vs France (sorted key Austria|France,
        # first-nation perspective) -> the court refuses.
        world.war_scores["Austria|France"] = REQUEST_TERMS_REFUSAL_WAR_SCORE + 10
        assert _request(world)["success"] is True
        produced = process_settlement_offer_phase(world)
        # No offer for war_1 from the request (the periodic scan may not
        # fire either — cooldown untouched by a refusal).
        assert all(o.get("war_id") != "war_1" or not o.get("requested_by_player")
                   for o in produced)
        entry = world.settlement_terms_requests["war_1"]
        assert entry["status"] == "refused"
        assert entry["resolve_reason"] == "winning_side_refuses"
        assert entry["cooldown_until_turn"] == 5 + REQUEST_TERMS_COOLDOWN_TURNS
        # Voiced, never anonymous: the notification carries the court line.
        notes = [
            n for n in world.notifications.get_pending()
            if n.get("type") == "settlement_terms_request_result"
        ]
        assert notes, "refusal must notify"
        assert "no need to name" in str(notes[0].get("message") or "")
        # Campaign log carries the refusal beat.
        events = [e for e in world.event_log
                  if e.get("type") == "settlement_terms_request_refused"]
        assert events and events[0]["war_id"] == "war_1"

    def test_refusal_cooldown_disables_with_named_clock(self):
        world = _world()
        _install_war(world)
        world.war_scores["Austria|France"] = REQUEST_TERMS_REFUSAL_WAR_SCORE + 10
        _request(world)
        process_settlement_offer_phase(world)
        affordance = evaluate_request_terms_affordance(world, "war_1")
        assert affordance["state"] == "disabled"
        assert affordance["reason"] == "request_cooldown"
        assert "remaining" in affordance["reason_display"]
        # After the cooldown expires the affordance returns.
        world.current_turn = 5 + REQUEST_TERMS_COOLDOWN_TURNS
        assert evaluate_request_terms_affordance(world, "war_1")["state"] == (
            "available"
        )

    def test_grant_produces_offer_with_provenance_and_shared_cooldowns(self):
        world = _world()
        _install_war(world)
        _request(world)
        produced = process_settlement_offer_phase(world)
        granted = [o for o in produced if o.get("requested_by_player")]
        assert len(granted) == 1
        assert granted[0]["war_id"] == "war_1"
        assert any(t.get("type") == "peace"
                   for t in granted[0]["settlement_terms"])
        entry = world.settlement_terms_requests["war_1"]
        assert entry["status"] == "granted"
        assert entry["resolve_reason"] == "terms_granted"
        # BOTH clocks written: the producer's periodic cooldown and the
        # request's own cooldown.
        assert world.ai_settlement_cooldowns["war_1"] == 5 + 5
        assert entry["cooldown_until_turn"] == 5 + REQUEST_TERMS_COOLDOWN_TURNS
        events = [e for e in world.event_log
                  if e.get("type") == "settlement_terms_request_granted"]
        assert events and events[0]["war_id"] == "war_1"

    def test_grant_respects_one_active_offer(self):
        world = _world()
        _install_war(world)
        # The periodic producer fires first (no request yet).
        first = process_settlement_offer_phase(world)
        assert len(first) == 1
        # A request placed while that offer sits on the desk cannot be
        # authored at all (affordance absent) — force the state anyway to
        # prove the resolver never double-produces.
        world.settlement_terms_requests["war_1"] = {
            "status": "requested", "requested_turn": 5,
            "resolved_turn": None, "resolve_reason": "",
            "cooldown_until_turn": 0, "answering_leader": "Austria",
        }
        second = process_settlement_offer_phase(world)
        assert second == []
        entry = world.settlement_terms_requests["war_1"]
        assert entry["status"] == "granted"
        assert entry["resolve_reason"] == "offer_already_available"
        offers = [o for o in world.pending_settlement_dialogues
                  if o.get("war_id") == "war_1"]
        assert len(offers) == 1

    def test_lapse_when_war_archives_before_the_answer(self):
        world = _world()
        war = _install_war(world)
        _request(world)
        war["ended_turn"] = 5
        world.invalidate_war_instance_indexes()
        produced = process_settlement_offer_phase(world)
        assert produced == []
        entry = world.settlement_terms_requests["war_1"]
        assert entry["status"] == "refused"
        assert entry["resolve_reason"] == "war_changed"
        notes = [
            n for n in world.notifications.get_pending()
            if n.get("type") == "settlement_terms_request_result"
        ]
        assert notes and "lapsed" in str(notes[0].get("message") or "")


class TestSerializationAndVoice:
    def test_request_state_round_trips_through_save_load(self):
        world = _world()
        _install_war(world)
        _request(world)
        snapshot = world.to_dict()
        restored = WorldState.from_dict(snapshot)
        assert restored.settlement_terms_requests["war_1"]["status"] == (
            "requested"
        )
        assert restored.settlement_terms_requests["war_1"][
            "answering_leader"
        ] == "Austria"

    def test_voice_templates_are_committed_copy(self):
        sent = resolve_settlement_voice_line(
            "settlement_request_terms_sent_talleyrand",
            court="Austria", war_label="France vs Austria",
        )
        refused = resolve_settlement_voice_line(
            "settlement_request_terms_refused_court",
            speaker="Metternich", court="Austria",
        )
        lapsed = resolve_settlement_voice_line(
            "settlement_request_terms_lapsed_talleyrand",
            war_label="France vs Austria",
        )
        assert "Sire" in sent and "Austria" in sent
        assert refused.startswith("Metternich")
        assert "lapsed" in lapsed
        # SC-32 D5 boundary: no conference/congress/veto vocabulary.
        for line in (sent, refused, lapsed):
            lowered = line.lower()
            assert "conference" not in lowered
            assert "congress" not in lowered
            assert "veto" not in lowered


class TestActionWiring:
    def test_request_terms_is_a_backend_valid_action(self):
        # The W1 whitelist-sync contract unions both sets (marshal-less
        # settlement actions live in META_ACTIONS).
        from backend.ai.validation import META_ACTIONS, VALID_ACTIONS

        assert "request_terms" in (set(VALID_ACTIONS) | set(META_ACTIONS))

    def test_executor_routes_request_terms(self):
        from backend.commands.diplomatic_executor import DiplomaticExecutor

        assert hasattr(DiplomaticExecutor, "_execute_request_terms")

    def test_mock_parser_routes_request_terms(self):
        from backend.ai.llm_client import LLMClient

        result = LLMClient()._parse_with_mock("request terms from Austria")
        assert result.matched is True
        assert result.action == "request_terms"
        assert result.diplomatic_data["target_nation"] == "Austria"

    def test_war_detail_popup_renders_the_affordance_contract(self):
        """Source pins: the popup renders Request Terms from
        `request_terms_state` (absent never renders; disabled carries the
        pre-click reason), and main.gd sends the structured action."""
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        popup = (root / "godot-client" / "project-sovereign" / "scripts"
                 / "war_detail_popup.gd").read_text(encoding="utf-8")
        assert "request_terms_clicked" in popup
        assert "_add_request_terms_button" in popup
        assert 'str(rt_state.get("state", "absent")) != "absent"' in popup
        assert 'rt_state.get("reason_display"' in popup
        main_gd = (root / "godot-client" / "project-sovereign" / "scripts"
                   / "main.gd").read_text(encoding="utf-8")
        assert "_on_war_request_terms_clicked" in main_gd
        assert '"action": "request_terms"' in main_gd
