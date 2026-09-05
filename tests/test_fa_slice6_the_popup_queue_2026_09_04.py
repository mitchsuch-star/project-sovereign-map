"""Final Whole-Game Audit — slice 6, "The Popup Queue" (FA-5, FA-30, FA-N20,
FA-N67, FA-N62, FA-99).

`build_base_response` drains the PopupQueue by default and `pop_highest`
REMOVES the entry — so every response whose client callback renders no popup
key, or renders only ONE route of what it carries, destroyed whatever was
queued. Reproduced on the shipped board before a line was written
(`docs/audits/fa_build_2026_09_04/REPRO_E_the_popup_queue.md`, all six rows
REAL, every filed line number stale by +140..+165):

* FA-5 (P1) — the end-turn response never carried the marshal petition (the
  choice-popup deferral skipped `_include_popup_passthroughs`), so an
  end-turn-only stretch never delivered the card and the undelivered card
  starved Fontainebleau and every later petition — a Lannes|Murat card stood
  from turn 4 with zero delivery across thirteen end-turn-only turns.
* FA-30 / FA-N20 — ten of the twelve /command question-bearing early returns
  DRAINED the queue into a response the client renders one route of: the
  one-shot Talleyrand sabotage card died beside a clarification, an
  objection, a delegation ask, a proposal_confirm.
* FA-N67 — fifteen refusal arms in seven endpoints whose callbacks read no
  popup key drained too (the Aug-2026 conversion covered /cancel_order's
  success arm only, and its pin was a substring grep one site satisfied).
* FA-N62 — the Orders-tab [Cancel] blocked on ANY pending dialogue while the
  typed `cancel` blocks only on hard stops: refused 12 of 12 ambient turns
  behind a letter that lapses on its own, naming Talleyrand for a settlement.
* FA-99 — /load drained the settlement draft notices into a response the
  world-swap handler never renders.

ONE rule: a response may carry a popped popup only when the callback that
consumes it runs the route table AND the response carries no question of its
own (`_result_carries_question`, read by `_build_result_response`); refusals
on the no-popup-key endpoints build through `_refusal_response`; `/load`
keeps the draft notices; the cancel guard reads the hard stop; the petition
rides the end-turn response under `deferred_marshal_petition`, which the
client stashes and raises at control return (the NA-6b discipline). Each
behaviour behind a lever whose False arm reproduces the prior behaviour.
"""
import contextlib
import io
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands.parser import CommandParser
from backend.game_logic import jealousy as J
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
               / "europe_1805.json")
MAIN_GD = REPO / "godot-client" / "project-sovereign" / "scripts" / "main.gd"

LEVERS = ("POPUP_DRAIN_READS_THE_QUESTION", "REFUSAL_ARMS_NEVER_DRAIN",
          "CANCEL_BUTTON_READS_THE_HARD_STOP", "LOAD_KEEPS_THE_DRAFT_NOTICES",
          "PETITION_RIDES_THE_END_TURN")

SAB = {"target_nation": "Austria", "sabotage_type": "leaked_terms",
       "authority_bonus_if_confronted": 5, "authority_penalty_if_overlooked": 3,
       "message": "probe"}
POPUP_KEYS = ("coalition_popup", "diplomatic_sabotage", "vassal_rebellion_imminent",
              "nation_proclamation", "diplomatic_objection", "marshal_petition",
              "incoming_proposal", "incoming_settlement_offer", "proposal_result",
              "commitment_paradox_popup")


@pytest.fixture(autouse=True)
def _levers_at_default():
    saved = {n: getattr(M, n) for n in LEVERS}
    yield
    for n, v in saved.items():
        setattr(M, n, v)


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _boot():
    with _quiet():
        return WorldState.from_scenario(SCENARIO)


@contextlib.contextmanager
def _served(world):
    saved = (M.world, M.game_state, M.parser)
    M.world = world
    M.game_state = {"world": world}
    M.parser = CommandParser(use_real_llm=False)
    try:
        assert M.parser.llm.use_real_api is False
        yield TestClient(M.app)
    finally:
        M.world, M.game_state, M.parser = saved


def _post(client, path, body):
    with _quiet():
        r = client.post(path, json=body)
    assert r.status_code == 200, (path, r.status_code, r.text[:200])
    return r.json()


def _cmd(client, line):
    return _post(client, "/command", {"command": line})


def _prime_sab(world):
    world.diplomatic_sabotage_popup = dict(SAB)


def _queued(world):
    return {k for k, v in world._popup_queue._queue.items() if v}


def _delivered(resp):
    return sorted(k for k in POPUP_KEYS if resp.get(k) is not None)


def _petition(world):
    return J.queue_confrontation_petition(world, world.marshals["Ney"],
                                          world.marshals["Davout"], 0)


# ═══════════════════════════════════════════════════════════════════════
# FA-30 / FA-N20 — a question never carries a popped popup
# ═══════════════════════════════════════════════════════════════════════

class TestAQuestionNeverCarriesAPoppedPopup:

    def test_the_predicate_reads_states_and_keys(self):
        q = M._result_carries_question
        assert q({"state": "awaiting_clarification"}) is True
        assert q({"state": "awaiting_player_choice"}) is True
        assert q({"pending_objection": {"marshal": "Ney"}}) is True
        assert q({"diplomatic_dialogue": {"type": "proposal_confirm"}}) is True
        assert q({"pending_interrupt": {"interrupt_type": "contact"}}) is True
        assert q({"success": True, "message": "Ney marches."}) is False
        assert q({"marshal_petition": None, "pending_objection": None}) is False
        assert q(None) is False

    def test_a_clarification_leaves_the_queue_intact(self):
        world = _boot()
        _prime_sab(world)
        with _served(world) as client:
            reply = _cmd(client, "move to Brittany")
            assert reply.get("state") == "awaiting_clarification", reply.get("message")
            assert reply.get("diplomatic_sabotage") is None
            assert "diplomatic_sabotage_popup" in _queued(world), "the card was destroyed"
            after = _cmd(client, "cancel")
            later = _cmd(client, "status")
        assert "diplomatic_sabotage" in _delivered(after) + _delivered(later)

    def test_the_lever_off_arm_destroys_the_card(self):
        M.POPUP_DRAIN_READS_THE_QUESTION = False
        world = _boot()
        _prime_sab(world)
        with _served(world) as client:
            reply = _cmd(client, "move to Brittany")
        assert reply.get("state") == "awaiting_clarification"
        assert reply.get("diplomatic_sabotage") is not None, "the row: popped beside the question"
        assert "diplomatic_sabotage_popup" not in _queued(world)

    @pytest.mark.parametrize("line", ["Soult, deal with Mack", "Grouchy, attack Mack"])
    def test_the_other_asks_leave_the_queue_intact(self, line):
        world = _boot()
        _prime_sab(world)
        with _served(world) as client:
            reply = _cmd(client, line)
        assert reply.get("state") == "awaiting_clarification", reply.get("message")
        assert reply.get("diplomatic_sabotage") is None
        assert "diplomatic_sabotage_popup" in _queued(world)

    def test_an_objection_leaves_the_queue_intact(self):
        world = _boot()
        _prime_sab(world)
        with _served(world) as client:
            reply = _cmd(client, "Bernadotte, attack Brunswick")
            assert reply.get("pending_objection"), reply.get("message")
            assert reply.get("diplomatic_sabotage") is None
            assert "diplomatic_sabotage_popup" in _queued(world)
            answer = _post(client, "/respond_to_objection", {"choice": "trust"})
            later = _cmd(client, "status")
        assert "diplomatic_sabotage" in _delivered(answer) + _delivered(later)

    def test_a_proposal_confirm_leaves_the_petition_queued(self):
        world = _boot()
        assert _petition(world) == "queued"
        with _served(world) as client:
            reply = _cmd(client, "propose peace with Austria")
        dialogue = reply.get("diplomatic_dialogue") or {}
        assert dialogue.get("type") == "proposal_confirm", reply.get("message")
        assert reply.get("marshal_petition") is None
        assert "pending_marshal_petition" in _queued(world)


# ═══════════════════════════════════════════════════════════════════════
# FA-N67 — a refusal never drains
# ═══════════════════════════════════════════════════════════════════════

class TestARefusalNeverDrains:

    def _refused(self, world, path, body, expect_success=False):
        _prime_sab(world)
        with _served(world) as client:
            reply = _post(client, path, body)
        assert reply.get("success") is expect_success, reply.get("message")
        return reply

    def test_cancel_order_no_marshal(self):
        world = _boot()
        reply = self._refused(world, "/cancel_order", {"marshal": ""})
        assert reply.get("diplomatic_sabotage") is None
        assert "diplomatic_sabotage" in reply, "keys stay present for the client contract"
        assert "diplomatic_sabotage_popup" in _queued(world)

    def test_cancel_order_no_ap(self):
        world = _boot()
        with _served(world) as client:
            _cmd(client, "Ney, march to Vienna")
        assert world.marshals["Ney"].strategic_order is not None
        world.actions_remaining = 0
        reply = self._refused(world, "/cancel_order", {"marshal": "Ney"})
        assert reply.get("diplomatic_sabotage") is None
        assert "diplomatic_sabotage_popup" in _queued(world)

    def test_cancel_order_game_over(self):
        world = _boot()
        world.game_over = True
        reply = self._refused(world, "/cancel_order", {"marshal": "Ney"})
        assert reply.get("game_over") is True
        assert reply.get("diplomatic_sabotage") is None
        assert "diplomatic_sabotage_popup" in _queued(world)

    def test_cancel_order_hard_stop_guard(self):
        world = _boot()
        world.dialogue_manager.push({"type": "war_purpose_selection", "nation": "Austria",
                                     "options": [{"action": "select_war_objective",
                                                  "label": "Conquest"}]})
        reply = self._refused(world, "/cancel_order", {"marshal": "Ney"})
        assert "awaits your answer" in (reply.get("message") or "")
        assert reply.get("diplomatic_sabotage") is None
        assert "diplomatic_sabotage_popup" in _queued(world)

    def test_the_lever_off_arm_destroys_the_card(self):
        M.REFUSAL_ARMS_NEVER_DRAIN = False
        world = _boot()
        reply = self._refused(world, "/cancel_order", {"marshal": ""})
        assert reply.get("diplomatic_sabotage") is not None, "the row: the refusal ate the card"
        assert "diplomatic_sabotage_popup" not in _queued(world)

    def test_cancel_order_except_arm(self, monkeypatch):
        world = _boot()

        def boom(command, game_state):
            raise RuntimeError("probe")
        monkeypatch.setattr(M.executor, "_execute_cancel", boom)
        reply = self._refused(world, "/cancel_order", {"marshal": "Ney"})
        assert "Error" in (reply.get("message") or "")
        assert reply.get("diplomatic_sabotage") is None
        assert "diplomatic_sabotage_popup" in _queued(world)

    def test_redemption_none_pending(self):
        world = _boot()
        reply = self._refused(world, "/respond_to_redemption", {"choice": "accept"})
        assert reply.get("diplomatic_sabotage") is None
        assert "diplomatic_sabotage_popup" in _queued(world)

    def test_glorious_charge_invalid(self):
        world = _boot()
        reply = self._refused(world, "/respond_to_glorious_charge", {"choice": "invalid"})
        assert reply.get("diplomatic_sabotage") is None
        assert "diplomatic_sabotage_popup" in _queued(world)

    @pytest.mark.parametrize("path,body", [
        ("/strategic_response", {"marshal_name": "Ney", "response_type": "contact",
                                 "choice": "attack"}),
        ("/capture_choice", {"choice": "secure"}),
        ("/respond_to_objection", {"choice": "trust"}),
        ("/mailbox/respond", {"mailbox_id": 1, "choice": "accept"}),
    ])
    def test_game_over_arms(self, path, body):
        world = _boot()
        world.game_over = True
        reply = self._refused(world, path, body)
        assert reply.get("diplomatic_sabotage") is None, path
        assert "diplomatic_sabotage_popup" in _queued(world), path


# ═══════════════════════════════════════════════════════════════════════
# FA-N62 — the cancel button reads the hard stop
# ═══════════════════════════════════════════════════════════════════════

class TestTheCancelButtonReadsTheHardStop:

    def _ordered(self):
        world = _boot()
        with _served(world) as client:
            _cmd(client, "Ney, march to Vienna")
        assert world.marshals["Ney"].strategic_order is not None
        world.actions_remaining = 4
        return world

    def test_a_soft_stop_no_longer_blocks_the_button(self):
        world = self._ordered()
        world.dialogue_manager.push({"type": "incoming_proposal", "from_nation": "Saxony",
                                     "target_nation": "Saxony", "options": [], "message": "probe"})
        assert world.dialogue_manager.is_hard_stop() is False
        with _served(world) as client:
            reply = _post(client, "/cancel_order", {"marshal": "Ney"})
        assert reply.get("success") is True, reply.get("message")
        assert world.marshals["Ney"].strategic_order is None

    def test_a_hard_stop_still_blocks_and_is_named(self):
        world = self._ordered()
        world.dialogue_manager.push({"type": "war_purpose_selection", "nation": "Austria",
                                     "options": [{"action": "select_war_objective",
                                                  "label": "Conquest"}]})
        assert world.dialogue_manager.is_hard_stop() is True
        with _served(world) as client:
            reply = _post(client, "/cancel_order", {"marshal": "Ney"})
        assert reply.get("success") is False
        message = reply.get("message") or ""
        assert "war purpose" in message and "awaits your answer" in message, message
        assert "Talleyrand" not in message
        assert world.marshals["Ney"].strategic_order is not None

    def test_the_lever_off_arm_blocks_on_any_letter(self):
        M.CANCEL_BUTTON_READS_THE_HARD_STOP = False
        world = self._ordered()
        world.dialogue_manager.push({"type": "incoming_proposal", "from_nation": "Saxony",
                                     "target_nation": "Saxony", "options": [], "message": "probe"})
        with _served(world) as client:
            reply = _post(client, "/cancel_order", {"marshal": "Ney"})
        assert reply.get("success") is False
        assert world.marshals["Ney"].strategic_order is not None


# ═══════════════════════════════════════════════════════════════════════
# FA-99 — /load keeps the draft notices
# ═══════════════════════════════════════════════════════════════════════

class TestLoadKeepsTheDraftNotices:

    NOTICE = {"war_id": "war_1", "turn_discarded": 3, "draft_clause_count": 2,
              "selected_target_nation": "Austria", "message_display": "probe notice"}

    def _saved(self):
        from backend.save_manager import save_game
        world = _boot()
        world.pending_settlement_draft_notices = [dict(self.NOTICE)]
        with _quiet():
            res = save_game(world, save_name="fa_slice6_probe")
        assert res.get("success"), res
        return world, res.get("filename") or "fa_slice6_probe.json"

    def test_the_notice_survives_the_load_and_reaches_the_first_command(self):
        world, fname = self._saved()
        with _served(world) as client:
            reply = _post(client, "/load", {"filename": fname})
            assert reply.get("success") is True, reply.get("message")
            assert not reply.get("settlement_draft_notices")
            assert M.world.pending_settlement_draft_notices, "the notice was drained on load"
            later = _cmd(client, "status")
        assert later.get("settlement_draft_notices") == [self.NOTICE]

    def test_the_lever_off_arm_drains_it_into_the_swap(self):
        M.LOAD_KEEPS_THE_DRAFT_NOTICES = False
        world, fname = self._saved()
        with _served(world) as client:
            reply = _post(client, "/load", {"filename": fname})
            assert reply.get("settlement_draft_notices") == [self.NOTICE], "the row"
            assert not M.world.pending_settlement_draft_notices
            later = _cmd(client, "status")
        assert not later.get("settlement_draft_notices")

    def test_the_builder_kwarg_is_honoured(self):
        world = _boot()
        world.pending_settlement_draft_notices = [dict(self.NOTICE)]
        kept = M.build_base_response(world, include_popup_passthroughs=False,
                                     drain_draft_notices=False)
        assert not kept.get("settlement_draft_notices")
        assert world.pending_settlement_draft_notices == [self.NOTICE]
        drained = M.build_base_response(world, include_popup_passthroughs=False)
        assert drained.get("settlement_draft_notices") == [self.NOTICE]
        assert not world.pending_settlement_draft_notices


# ═══════════════════════════════════════════════════════════════════════
# FA-5 — the petition rides the end-turn response
# ═══════════════════════════════════════════════════════════════════════

class TestThePetitionRidesTheEndTurn:

    def test_the_end_turn_response_carries_the_card_under_its_own_key(self):
        world = _boot()
        assert _petition(world) == "queued"
        with _served(world) as client:
            reply = _cmd(client, "end turn")
        assert reply.get("enemy_phase") is not None
        card = reply.get("deferred_marshal_petition")
        assert isinstance(card, dict) and card.get("kind") == "jealousy_confrontation", reply.keys()
        assert reply.get("marshal_petition") is None, "the route key would swallow the report"
        assert "pending_marshal_petition" not in _queued(world), "the slot was not popped"
        assert world.pending_marshal_petition is not None, "the standing petition is durable"

    def test_the_card_is_answerable_and_the_channel_frees(self):
        world = _boot()
        _petition(world)
        with _served(world) as client:
            reply = _cmd(client, "end turn")
            assert reply.get("deferred_marshal_petition")
            answer = _post(client, "/marshal_petition_response", {"choice": "acknowledge"})
        assert answer.get("success") is True, answer.get("message")
        assert world.pending_marshal_petition is None

    def test_the_card_is_priced_at_delivery(self):
        """IGR-2's class: the jealousy pass runs BEFORE `advance_turn` refills
        AP, so a flag baked at queue time reads zero. The deferred card is
        re-priced where it is delivered."""
        world = _boot()
        world.actions_remaining = 0
        _petition(world)
        with _served(world) as client:
            reply = _cmd(client, "end turn")
        card = reply.get("deferred_marshal_petition")
        assert card
        command_arm = next(o for o in card.get("options", []) if o.get("id") == "command")
        assert command_arm.get("enabled") is True, command_arm

    def test_the_lever_off_arm_never_delivers_it(self):
        M.PETITION_RIDES_THE_END_TURN = False
        world = _boot()
        _petition(world)
        with _served(world) as client:
            for _ in range(3):
                reply = _cmd(client, "end turn")
                assert "deferred_marshal_petition" not in reply
                assert reply.get("marshal_petition") is None
        assert "pending_marshal_petition" in _queued(world)

    def test_the_client_stashes_and_raises_the_card(self):
        """The wiring the payload needs, pinned where it lives: the stash beside
        its siblings, the raise in every control-return tail (a structural
        pin — the .gd seam cannot run here; the parse harness + boot smoke
        cover the file)."""
        src = MAIN_GD.read_text(encoding="utf-8")
        assert "var pending_petition_data" in src
        assert re.search(r"func _stash_petition\(response: Dictionary\) -> void:", src)
        assert re.search(r"func _show_pending_petition\(\) -> bool:", src)
        assert "deferred_marshal_petition" in src

        def body(name):
            m = re.search(r"^func %s\([^\n]*\n(.*?)(?=^func |\Z)" % re.escape(name), src,
                          flags=re.M | re.S)
            assert m, name
            return m.group(1)
        assert "_stash_petition(response)" in body("_on_command_result")
        for tail in ("_return_control_to_player", "_on_proclamation_dismissed",
                     "_on_battle_diorama_dismissed", "_process_next_interrupt"):
            assert "_show_pending_petition()" in body(tail), tail
        # the route table is untouched — the petition stays a post-HUD route
        assert '{"id": "marshal_petition"' in src
