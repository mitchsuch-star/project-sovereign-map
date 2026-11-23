"""Row IC, Session 2b (November 20, 2026) — the TASK TO PROVE HIMSELF: old
saves, the window's answer through the endpoint, the save round trip, and the
WORDS CENSUS.

The trial's own behaviour — the proposal by nature, the audience's arm, giving
it, no orders and no call-back, the nights, the roll, the bands, the morning —
is `tests/test_autonomy.py` (rewritten, never deleted). This file holds what
stands around it:

    AN OLD SAVE       a man in the middle of the old three turns ("Grant
                      Autonomy") is settled on loading — the same bands — and
                      the next morning says so in one line; a second load
                      finds nothing to settle
    THE OLD QUESTION  a saved audience whose arms still name `grant_autonomy`
                      is rebuilt at the load, and the old id is answered as
                      the task — a standing question never sticks
    THE WINDOW        what the window showed is what is given (the endpoint)
    THE SAVE          `Marshal.trial`, his exact order and the take it carries
                      survive a save, and the count goes on
    THE WORDS         "autonomy" and "independent command" on no marshals'
                      screen (the vassals' autonomy scale is exempt by name);
                      "on his own" nowhere before the Emperor can set a man on
                      his own; the jealous strike says "without waiting for
                      orders"; a refused order says "refused your order"
                      (`docs/INDEPENDENT_COMMAND_SPEC.md` §13)

The rules are `backend/game_logic/trial.py`; SYSTEMS_REFERENCE §232.
"""
from __future__ import annotations

import ast
import contextlib
import copy
import io
import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser
from backend.game_logic import trial as T
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
CLIENT = REPO / "godot-client" / "project-sovereign"
SCENARIO_PATH = CLIENT / "assets" / "maps" / "europe_1805.json"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def base():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(base):
    with _quiet():
        return WorldState.from_dict(base.to_dict())


def _old_save(base, name: str = "Ney", *, won: int = 0, lost: int = 0, taken: int = 0,
              trust: int = 15, turns: int = 2) -> dict:
    """A save as the game wrote it BEFORE this session: the marshal's row
    carries the six autonomy keys, and no `trial`."""
    with _quiet():
        data = json.loads(json.dumps(base.to_dict(), default=str))
    row = data["marshals"][name]
    row.pop("trial", None)
    row["trust"] = {"value": trust} if isinstance(row.get("trust"), dict) else trust
    row.update({"autonomous": True, "autonomy_turns": turns, "autonomy_reason": "redemption",
                "autonomous_battles_won": won, "autonomous_battles_lost": lost,
                "autonomous_regions_captured": taken})
    return data


def _load(data: dict):
    with _quiet():
        return WorldState.from_dict(copy.deepcopy(data))


def _end_turn(world):
    executor = CommandExecutor()
    with _quiet():
        return executor.execute({"command": {"action": "end_turn"}},
                                {"world": world, "executor": executor})


# ═══════════════════════════ an old save ════════════════════════════════════

class TestAnOldSaveSettlesOnLoading:

    def test_the_premise_the_old_keys_are_what_the_old_game_wrote(self, base):
        """HEAD's `Marshal.to_dict` wrote exactly these six keys (the save
        format's own table, `docs/SAVE_FORMAT_REFERENCE.md`)."""
        row = _old_save(base, won=1)["marshals"]["Ney"]
        for key in ("autonomous", "autonomy_turns", "autonomy_reason", "autonomous_battles_won",
                    "autonomous_battles_lost", "autonomous_regions_captured"):
            assert key in row
        assert "trial" not in row

    @pytest.mark.parametrize("won, lost, taken, band, gain", [
        (2, 0, 0, "spectacular", 40),
        (0, 0, 1, "spectacular", 40),
        (1, 0, 0, "good", 25),
        (0, 0, 0, "none", 15),
        (0, 1, 0, "poor", 5),
    ])
    def test_he_is_settled_on_what_he_had_done_the_same_bands(self, base, won, lost, taken,
                                                               band, gain):
        world = _load(_old_save(base, won=won, lost=lost, taken=taken, trust=15))
        ney = world.marshals["Ney"]
        assert ney.trust.value == 15 + gain
        assert ney.trial is None and ney.strategic_order is None
        for gone in ("autonomous", "autonomy_turns", "autonomy_reason"):
            assert not hasattr(ney, gone), gone
        logged = [e for e in world.event_log if e.get("type") == "marshal_trial"]
        assert [(e["phase"], e["marshal"], e["band"], e["trust_gain"]) for e in logged] == [
            ("settled", "Ney", band, gain)]

    def test_the_line_says_what_happened_in_plain_words(self, base):
        world = _load(_old_save(base, won=1, trust=15))
        line = next(e for e in world.event_log if e.get("type") == "marshal_trial")["message"]
        assert line == ("Ney was acting without orders when this game was saved — a rule that has "
                        "left the game. He is settled on what he had done by then: his trust in "
                        "you rises by 25 (to 40). He is under your orders again.")

    def test_a_spectacular_man_brings_the_authority_too(self, base):
        data = _old_save(base, won=2, trust=15)
        data["authority_tracker"]["authority"] = 50
        world = _load(data)
        assert world.authority_tracker.authority == 60
        line = next(e for e in world.event_log if e.get("type") == "marshal_trial")["message"]
        assert "his trust in you rises by 40 (to 55), and your authority by 10" in line

    def test_the_next_morning_says_so_once(self, base):
        world = _load(_old_save(base, won=1))
        first = _end_turn(world)
        told = [e["message"] for e in first.get("tactical_events") or []
                if e.get("type") == "marshal_trial"]
        assert len(told) == 1 and told[0].startswith("Ney was acting without orders when this game")
        second = _end_turn(world)
        assert not [e for e in second.get("tactical_events") or []
                    if e.get("type") == "marshal_trial"]

    def test_the_line_is_told_at_the_next_morning_across_another_save(self, base):
        """Loaded, saved again before any turn ended, loaded again: the line
        is still owed and is told once (the `told` mark rides the log's row)."""
        world = _load(_old_save(base, won=1))
        with _quiet():
            again = WorldState.from_dict(json.loads(json.dumps(world.to_dict(), default=str)))
        assert again.marshals["Ney"].trust.value == 40, "settled once, never twice"
        told = [e for e in _end_turn(again).get("tactical_events") or []
                if e.get("type") == "marshal_trial"]
        assert len(told) == 1

    def test_a_second_load_finds_nothing_to_settle(self, base):
        world = _load(_old_save(base, won=2, trust=15))
        with _quiet():
            saved = json.loads(json.dumps(world.to_dict(), default=str))
        row = saved["marshals"]["Ney"]
        for key in ("autonomous", "autonomy_turns", "autonomy_reason", "autonomous_battles_won",
                    "autonomous_battles_lost", "autonomous_regions_captured"):
            assert key not in row, f"{key} is written no more"
        again = _load(saved)
        assert again.marshals["Ney"].trust.value == 55
        assert len([e for e in again.event_log if e.get("type") == "marshal_trial"]) == 1

    def test_a_man_not_in_those_turns_is_left_alone(self, base):
        data = _old_save(base, won=2)
        data["marshals"]["Ney"]["autonomous"] = False
        world = _load(data)
        assert world.marshals["Ney"].trust.value == 15
        assert not [e for e in world.event_log if e.get("type") == "marshal_trial"]

    def test_only_the_players_marshals_are_settled(self, base):
        """The old flag on another court's marshal (it was never set by the
        game) moves nothing."""
        with _quiet():
            data = json.loads(json.dumps(base.to_dict(), default=str))
        row = data["marshals"]["Mack"]
        row.update({"autonomous": True, "autonomy_turns": 2, "autonomous_battles_won": 2})
        before = base.marshals["Mack"].trust.value
        world = _load(data)
        assert world.marshals["Mack"].trust.value == before
        assert not [e for e in world.event_log if e.get("type") == "marshal_trial"]

    def test_he_takes_orders_again_at_once(self, base):
        world = _load(_old_save(base, won=1))
        assert T.order_refusal(world, {"marshal": "Ney"}, "attack") is None
        assert not T.on_trial(world.marshals["Ney"])


# ═══════════════════════════ the old question ═══════════════════════════════

OLD_OPTIONS = [
    {"id": "grant_autonomy", "text": "Grant Autonomy",
     "description": "Ney acts independently for 3 turns. Trust resets based on performance.",
     "effect": "autonomy_3_turns"},
    {"id": "administrative_role", "text": "Administrative Role",
     "description": "Ney is removed from the field.", "effect": "administrative"},
    {"id": "dismiss", "text": "Dismiss", "description": "Ney is dismissed.", "effect": "dismiss"},
]


def _save_with_the_old_question(base) -> dict:
    with _quiet():
        data = json.loads(json.dumps(base.to_dict(), default=str))
    row = data["marshals"]["Ney"]
    row["trust"] = {"value": 15} if isinstance(row.get("trust"), dict) else 15
    row["redemption_pending"] = True
    data["pending_redemption"] = {
        "type": "redemption_event", "marshal": "Ney", "trust": 15,
        "message": "Ney's trust in you has broken completely. The relationship must be addressed.",
        "options": copy.deepcopy(OLD_OPTIONS),
    }
    return data


class TestAStandingQuestionFromAnOldSave:

    def test_its_arms_are_rebuilt_at_the_load(self, base):
        world = _load(_save_with_the_old_question(base))
        event = world.pending_redemption
        ids = [option["id"] for option in event["options"]]
        assert ids == ["trial", "administrative_role", "dismiss"]
        arm = event["options"][0]
        assert arm["text"] == "Give Ney a task to prove himself"
        assert "you cannot call him back" in arm["description"]
        assert "independently" not in json.dumps(event)
        # the other arms are the save's own, untouched
        assert event["options"][1:] == OLD_OPTIONS[1:]

    def test_the_rebuilt_question_is_answered(self, base):
        world = _load(_save_with_the_old_question(base))
        ney = world.marshals["Ney"]
        with _quiet():
            result = world.disobedience_system.handle_redemption_response(
                world.pending_redemption, "trial", {"world": world})
        assert result["success"] and T.on_trial(ney) and not ney.redemption_pending

    def test_the_old_id_is_answered_as_the_task_through_the_endpoint(self, base, monkeypatch):
        world = _load(_save_with_the_old_question(base))
        client = _client(monkeypatch, world)
        with _quiet():
            reply = client.post("/respond_to_redemption", json={"choice": "grant_autonomy"}).json()
        assert reply["success"] is True and reply["choice"] == "trial"
        assert reply["trial"]["turns_left"] == 3
        assert "autonomous" not in reply and "autonomy_turns" not in reply
        assert T.on_trial(M.world.marshals["Ney"]) and M.world.pending_redemption is None

    def test_a_question_delivered_with_the_old_arm_is_refreshed_on_the_wire(self, base, monkeypatch):
        """Belt and braces: a question that reaches a delivery seam still
        naming the old arm (set by hand here) goes out as the task."""
        world = _load(_save_with_the_old_question(base))
        world.pending_redemption["options"] = copy.deepcopy(OLD_OPTIONS)
        client = _client(monkeypatch, world)
        with _quiet():
            out = client.get("/pending_redemption").json()
        assert out["has_pending"] is True
        assert [option["id"] for option in out["options"]][0] == "trial"


def _client(monkeypatch, world):
    """The endpoint over `world` (the three module globals swapped together)."""
    with _quiet():
        parser = CommandParser()
    monkeypatch.setattr(M, "world", world)
    monkeypatch.setattr(M, "game_state", {"world": world, "executor": M.executor})
    monkeypatch.setattr(M, "parser", parser)
    return TestClient(M.app)


# ═══════════════════════════ the window ═════════════════════════════════════

class TestWhatTheWindowShowedIsWhatIsGiven:

    @staticmethod
    def _ask(world, name="Ney"):
        marshal = world.marshals[name]
        with _quiet():
            marshal.trust.set(15)
            event = world.disobedience_system.check_redemption_threshold(marshal, world)
        assert event is not None and world.pending_redemption is event
        return marshal

    def test_the_answer_gives_the_task_and_the_reply_carries_it(self, world, monkeypatch):
        ney = self._ask(world)
        client = _client(monkeypatch, world)
        actions = world.actions_remaining
        with _quiet():
            reply = client.post("/respond_to_redemption", json={"choice": "trial"}).json()
        assert reply["success"] is True and reply["choice"] == "trial"
        assert reply["trial"]["status"] == "On a task to prove himself — 3 turns left"
        assert reply["trial"]["line"] == ney.strategic_order.original_command
        assert world.actions_remaining == actions, "giving it costs no action"
        assert world.pending_redemption is None

    def test_a_board_that_changed_gives_nothing_and_the_question_comes_back(self, world, monkeypatch):
        ney = self._ask(world)                                  # at Rhineland: he asks to hold
        shown = T.shown_line(world.pending_redemption)
        assert shown.startswith("Ney, hold Rhineland.")
        ney.location = "Franconia"                              # the board changes under the window
        with _quiet():
            world._build_marshal_index()
            world.calculate_visibility()
        client = _client(monkeypatch, world)
        with _quiet():
            reply = client.post("/respond_to_redemption", json={"choice": "trial"}).json()
        assert reply["success"] is False and reply.get("standing") is True
        assert reply["state"] == "awaiting_redemption_choice"
        with _quiet():
            now = T.proposal(world, ney)["words"]
        assert "take Bohemia" in now
        assert reply["message"] == ("The board has changed since Ney made his proposal — nothing is "
                                    f"given yet. He now proposes: {now}")
        assert T.shown_line(reply["redemption_event"]) == "Ney, take Bohemia and hold it."
        assert not T.on_trial(ney) and ney.strategic_order is None
        assert world.pending_redemption is not None and ney.redemption_pending
        with _quiet():                                          # answered again: now it is given
            second = client.post("/respond_to_redemption", json={"choice": "trial"}).json()
        assert second["success"] is True and ney.strategic_order.opening_take == "Bohemia"

    def test_every_delivery_carries_the_proposal_as_the_board_stands(self, world, monkeypatch):
        """The question waits; the board moves; the window is shown what he
        proposes NOW (the arm is read again at each delivery)."""
        ney = self._ask(world)
        ney.location = "Franconia"
        with _quiet():
            world._build_marshal_index()
            world.calculate_visibility()
        client = _client(monkeypatch, world)
        with _quiet():
            out = client.get("/pending_redemption").json()
        assert out["options"][0]["proposal"]["line"] == "Ney, take Bohemia and hold it."

    def test_the_cancel_button_is_refused_free_at_the_endpoint(self, world, monkeypatch):
        ney = self._ask(world)
        client = _client(monkeypatch, world)
        with _quiet():
            client.post("/respond_to_redemption", json={"choice": "trial"})
        world.actions_remaining = 0                              # ... and with no action left
        with _quiet():
            reply = client.post("/cancel_order", json={"marshal": "Ney"}).json()
        assert reply["success"] is False
        assert "takes no orders until it ends" in reply["message"]
        assert "Not enough" not in reply["message"]
        assert T.on_trial(ney) and ney.strategic_order is not None


# ═══════════════════════════ the save ═══════════════════════════════════════

class TestTheTaskSurvivesASave:

    @staticmethod
    def _given(world):
        ney = world.marshals["Ney"]
        ney.location = "Franconia"
        with _quiet():
            world._build_marshal_index()
            world.calculate_visibility()
            assert T.give(world, ney)["given"]
        return ney

    def test_the_round_trip_keeps_the_task_the_order_and_the_take(self, world):
        ney = self._given(world)
        with _quiet():
            again = WorldState.from_dict(json.loads(json.dumps(world.to_dict(), default=str)))
        back = again.marshals["Ney"]
        assert back.trial == ney.trial and back.trial is not ney.trial
        order = back.strategic_order
        assert (order.command_type, order.target, order.opening_take) == ("HOLD", "Franconia", "Bohemia")
        assert [line["if"] for line in order.if_thens] == [line["if"]
                                                            for line in ney.strategic_order.if_thens]
        assert T.status_words(back) == T.status_words(ney)

    def test_the_field_is_written_only_while_he_is_on_his_task(self, world):
        from backend.models.marshal import Marshal
        assert "trial" in Marshal.KEPT_ONLY_WHEN_HELD_FIELDS
        assert "trial" not in world.marshals["Ney"].to_dict()
        ney = self._given(world)
        assert ney.to_dict()["trial"] == ney.trial

    def test_the_count_goes_on_after_a_load(self, world):
        self._given(world)
        _end_turn(world)                                         # night 1: the take
        with _quiet():
            again = WorldState.from_dict(json.loads(json.dumps(world.to_dict(), default=str)))
        ney = again.marshals["Ney"]
        assert T.on_trial(ney) and ney.trial["turns_left"] == 2 and ney.location == "Bohemia"
        again.pending_capture_choice = None                      # (the capture's own question)
        for _night in range(2):
            _end_turn(again)
            again.pending_capture_choice = None
        assert not T.on_trial(ney) and ney.strategic_order is None
        assert ney.trust.value > 70, "his trust came back by what he did"

    def test_a_malformed_saved_value_loads_as_no_task(self, base):
        with _quiet():
            data = json.loads(json.dumps(base.to_dict(), default=str))
        data["marshals"]["Ney"]["trial"] = "yes"
        world = _load(data)
        assert world.marshals["Ney"].trial is None


# ═══════════════════════════ what the pressing found ════════════════════════
#
# The build was pressed in the real client at the first player's own setup
# (Interface Scale 1.8 on 5120 x 1377) before any reading. What it found, each
# fixed at its cause and pinned here (`docs/BUG_FIXES.md` §"Row IC, Session
# 2b", rows IC2B-X1 … X5).

class TestWhatThePressingFound:

    def test_the_desk_lists_no_matter_for_a_man_who_takes_no_orders(self, world):
        """IC2B-X1: with Ney on his task the desk's TO DECIDE still said "Ney
        will leave his post to join a battle near him — Mack is close." and
        the End Turn warning named him — of a man who drops his task for no
        distant battle, and to whom no order can be given. The ONE gate every
        reader shares (`strategic.aggressive_interrupt_applies`) now knows."""
        from backend.commands import strategic as S
        from backend.game_logic import dispatch, today
        from backend.models.marshal import StrategicOrder
        ney = world.marshals["Ney"]
        turn = int(world.current_turn)
        ney.strategic_order = StrategicOrder(command_type="HOLD", target=ney.location,
                                             target_type="region", started_turn=turn, issued_turn=turn,
                                             original_command=f"Ney, hold {ney.location}")
        # the premise: a bold man's plain standing order IS warned of
        assert S.aggressive_interrupt_applies(world, ney)
        read = dispatch.end_turn_interrupt_reading(world, "France")
        assert read and [row["marshal"] for row in read["corps"]] == ["Ney"]
        assert any(row["id"] == "interrupt:Ney" for row in today.decide(world))
        # ... and on his task to prove himself he is not
        ney.strategic_order = None
        with _quiet():
            assert T.give(world, ney)["given"]
        assert not S.aggressive_interrupt_applies(world, ney)
        assert S.aggressive_interrupt_clause(world, ney) == ""
        assert dispatch.end_turn_interrupt_reading(world, "France") is None
        assert dispatch.end_turn_interrupt_warning(world, "France") is None
        assert not [row for row in today.decide(world) if row["id"] == "interrupt:Ney"]

    def test_the_task_given_is_said_in_the_orders_own_words(self, world):
        """IC2B-X2: the reply said "… so he ASKS to take Bohemia" of a task
        already given. It says what he will do, in the order's own words."""
        ney = world.marshals["Ney"]
        ney.location = "Franconia"
        with _quiet():
            world._build_marshal_index()
            world.calculate_visibility()
            taken = T.give(world, ney)
            held = T.give(world, world.marshals["Davout"])
        assert taken["message"] == (
            'Ney has his task to prove himself: "Ney, take Bohemia and hold it." He marches on '
            "Bohemia as this turn ends. He takes no orders until it ends — 3 turns, or up to 6 "
            "while he keeps winning.")
        assert held["message"].startswith('Davout has his task to prove himself: "Davout, hold ')
        assert "marches on" not in held["message"] and "asks" not in held["message"]

    def test_the_window_shows_his_proposal_and_the_terms_as_two_paragraphs(self, world):
        """IC2B-X3: what HE asks, then the terms — and the words stay with
        their own button, apart from the next answer."""
        arm = T.option(world, world.marshals["Ney"])
        asks, terms = arm["description"].split("\n")
        assert asks.startswith("Ney is a bold man") and terms == T.terms_words()
        scene = (CLIENT / "scenes" / "redemption_dialog.tscn").read_text(encoding="utf-8")
        order = [scene.index(f'[node name="{name}"') for name in
                 ("TrialButton", "ProposalLabel", "ProposalGap", "DismissButton", "AdminButton")]
        assert order == sorted(order)
        dialog = (CLIENT / "scripts" / "redemption_dialog.gd").read_text(encoding="utf-8")
        assert "proposal_gap.visible = proposal_label.visible" in dialog

    def test_his_card_offers_no_click_that_would_be_refused(self):
        """IC2B-X4: under a man who takes no orders the card's hint still said
        "Click a province to send him · an enemy to attack …". It says what a
        click on the map does now."""
        main = (CLIENT / "scripts" / "main.gd").read_text(encoding="utf-8", errors="replace")
        assert 'const ORDER_STRIP_TRIAL_HINT := "Esc closes this card"' in main
        start = main.index("func _render_order_strip() -> void:")
        body = main[start:main.index("\nfunc ", start + 10)]
        assert "_show_order_strip(ORDER_STRIP_TRIAL_HINT)" in body
        assert body.index("ORDER_STRIP_TRIAL_HINT") < body.index("No march today")

    def test_the_generals_page_shows_his_task_not_the_order_under_it(self):
        """IC2B-X5: his page said "Order: HOLD → Franconia" under "marches on
        Bohemia as this turn ends" — the standing order that carries the task
        out, in the code's own word. It shows the task as it was given."""
        page = (CLIENT / "scripts" / "marshal_management.gd").read_text(encoding="utf-8",
                                                                        errors="replace")
        assert page.count(']His task: " + task_line + "[/color]"') == 2
        assert page.count(
            'var task_line := str(on_task.get("line", "")) if on_task is Dictionary else ""') == 2


class TestWhatTheFirstReadingFound:
    """The first blind reading (three fresh readers; `docs/audits/ic_client/
    session2b/README.md`): twelve answers of twelve right by the key — and
    every reader doubted the card it had just read right. What they said, each
    fixed and pinned here (rows IC2B-R1 … R8); the changed screens were then
    read again by three more."""

    def test_r1_his_card_carries_no_order_at_all(self):
        """Three of three: the card said "He takes no orders until it ends"
        above eleven greyed order buttons — "7 Cancel order" among them, under
        "you cannot call him back" — and none could tell whether they worked."""
        card = (CLIENT / "scripts" / "selection_card.gd").read_text(encoding="utf-8")
        start = card.index("func _render() -> void:")
        body = card[start:card.index("\nfunc ", start + 10)]
        proving = body.index("var proving := _trial_row(compact)")
        assert proving < body.index("_specs = MarshalStateKit.order_specs(_view)"), \
            "his task is read before any order is laid out"
        block = body[proving:body.index("_specs = MarshalStateKit.order_specs(_view)")]
        assert "_body.add_child(proving)" in block and "_body.add_child(_hint_label(compact))" in block
        assert "return" in block, "nothing else is drawn for him: no order row, no menu"
        assert "_order_row" not in block and "_simple_row" not in block
        words = card[card.index("func _trial_row("):card.index("func _no_orders_reason(")]
        assert 'His task: \\"" + line + "\\"' in words
        assert "He takes no orders until it ends, and you cannot call him back." in words

    def test_r2_esc_says_what_it_does_on_his_card(self):
        """Three of three: "Esc lets him go" read as perhaps releasing him
        from his task."""
        main = (CLIENT / "scripts" / "main.gd").read_text(encoding="utf-8", errors="replace")
        line = next(row for row in main.split("\n") if row.startswith("const ORDER_STRIP_TRIAL_HINT"))
        assert line.endswith('"Esc closes this card"') and "lets him go" not in line
        assert "click on the map" not in line, "the second reading: oddly worded, two of three"

    def test_r3_the_emperors_pool_is_not_on_his_card(self):
        """Three of three: "4 actions left" on the card of a man who takes no
        orders — "what can they be spent on?"."""
        card = (CLIENT / "scripts" / "selection_card.gd").read_text(encoding="utf-8")
        body = card[card.index("func _figures_bbcode("):card.index("func _order_row(")]
        assert body.index("if not _no_orders_reason().is_empty():") < body.index('"action") + " left"')

    def test_r4_the_terms_say_which_turns_how_many_in_all_and_what_it_pays(self):
        """Three of three could not tell whether "6 turns at most" was a total;
        others asked when the count starts, what "a victory" is, what "most"
        meant, and whether he is then back in hand."""
        said = T.terms_words()
        for needed in ("for 3 turns — this one and the next two — then he is under your orders again",
                       "Until then he takes no orders, and you cannot call him back.",
                       "If he wins a battle on his last turn and loses no battle that turn, his task runs "
                       "one turn longer, and so on — up to 6 turns in all, the first 3 included.",
                       "When his task ends, his trust in you rises by the first of these that is true:",
                       "40 (and your authority by 10) if he won two battles or took a defended place;",
                       "25 if he won more battles than he lost;",
                       "15 if he fought none or won as many as he lost;",
                       "5 if he lost more than he won."):
            assert needed in said, needed
        for gone in ("6 turns at most", "most for two battles", "ends his last turn on a victory",
                     "loses none", "at the least", "from 5", "presses on"):
            assert gone not in said, gone

    def test_r4_the_four_amounts_in_words_are_the_rules_own_arithmetic(self):
        """The window names four amounts and what earns each. Every record a
        man can bring home is put through the rule and through the words."""
        def by_the_words(won: int, lost: int, taken: int) -> int:
            # "the first of these that is true"
            if won >= 2 or taken >= 1:
                return 40            # "if he won two battles or took a defended place"
            if won > lost:
                return 25            # "if he won more battles than he lost"
            if won == lost:
                return 15            # "if he fought none or won as many as he lost"
            return 5                 # "if he lost more than he won"
        for won in range(0, 5):
            for lost in range(0, 6):
                for taken in range(0, 3):
                    assert T.band(won, lost, taken)[1] == by_the_words(won, lost, taken), (won, lost, taken)
        assert (T.REWARDS["spectacular"], T.REWARDS["good"], T.REWARDS["none"], T.REWARDS["poor"]) \
            == (40, 25, 15, 5)
        # the figures are the rule's own
        assert (T.TURNS, T.MOST_TURNS, T.REWARDS["poor"], T.REWARDS["spectacular"],
                T.SPECTACULAR_AUTHORITY) == (3, 6, 5, 40, 10)

    def test_r5_an_open_province_is_said_plainly_and_where_he_sets_out_from(self, world):
        """"which nothing France can see defends" — "I did not know what 'can
        see' refers to"; "the screen did not tell me where Ney is now"."""
        ney = world.marshals["Ney"]
        ney.location = "Franconia"
        with _quiet():
            world._build_marshal_index()
            world.calculate_visibility()
        words = T.proposal(world, ney)["words"]
        assert "march from Franconia and take Bohemia, where France sees no defenders" in words
        assert "nothing France can see" not in words

    def test_r6_every_answer_says_what_it_does_under_its_own_button(self, world):
        """Two of three: "Dismiss Ney" and "Transfer Ney to Staff" stood with
        no words (what each does was a hover); one: the task's words, under its
        button, read at first like a description of the next button."""
        ney = world.marshals["Ney"]
        with _quiet():
            ney.trust.set(15)
            event = world.disobedience_system.check_redemption_threshold(ney, world)
        said = {option["id"]: option["description"] for option in event["options"]}
        assert said["dismiss"] == ("Ney is dismissed for good; his men join the nearest marshal within "
                                   "three provinces, or disband if there is none. Your authority rises "
                                   "by 10.")
        assert said["administrative_role"] == (
            "Ney leaves the field for a post on your staff; his corps waits in depot. While he serves "
            "you get 1 more action each turn; the order \"recall Ney\" brings him back.")
        assert all(len(words) <= 170 for key, words in said.items() if key != "trial"), \
            "two lines at most each at the first player's setup"
        for words in said.values():
            assert "`" not in words and "≤" not in words and "+1" not in words, words
        dialog = (CLIENT / "scripts" / "redemption_dialog.gd").read_text(encoding="utf-8")
        for needed in ("func _caption_under(button: Button) -> Array:",
                       "func _place_captions(roomy: bool) -> void:",
                       "for b in [settle_button, admin_button, dismiss_button]:",
                       "_captions[b] = _caption_under(b)"):
            assert needed in dialog, needed
        # the words are never lost: where they do not stand they are the hover
        place = dialog[dialog.index("func _place_captions("):dialog.index("func _on_settle_pressed")]
        assert 'b.tooltip_text = "" if shown else said' in place

    def test_r6_the_window_is_measured_and_never_runs_past_the_screen(self):
        """Pressed at the first player's setup: with every answer's words the
        window stood 720 px in a 765 px view, over the top bar. The filler line
        went, the spacing tightened (it stands 643 px there now), and the
        window MEASURES itself once its lines have wrapped: words that would
        push it past the screen's band step into their hovers — the task's
        own always stand."""
        dialog = (CLIENT / "scripts" / "redemption_dialog.gd").read_text(encoding="utf-8")
        fit = dialog[dialog.index("func _settle_fit() -> void:"):dialog.index("func _place_captions(")]
        assert "await get_tree().process_frame" in fit
        assert "if need > view - WINDOW_RESERVE - 2.0 * Utils.top_bar_growth():" in fit
        assert "_place_captions(false)" in fit
        assert "Utils.shrink_centered_panel_to_content($PanelContainer)" in fit
        # the task's own words are never put away: no step of the fit hides
        # them — where the window would run off the screen they SCROLL (the
        # review; pressed by `TestRowIC9bTheAudienceAtTheCompactView`)
        assert "proposal_label.visible = false" not in fit
        assert "proposal_label.hide()" not in fit and "proposal_label.text = " not in fit
        scene = (CLIENT / "scenes" / "redemption_dialog.tscn").read_text(encoding="utf-8")
        assert "How will you handle this crisis?" not in scene and "OptionsLabel" not in scene
        assert 'text = "Trust: 15 of 100 — critical"' in scene

    def test_the_map_says_where_he_marches_not_where_he_holds(self, world):
        """The second reading, two of three: the map's badge read "holds
        Franconia" over a man whose task marches on Bohemia as the turn ends —
        "that looked contradictory"."""
        from backend.commands.strategic import standing_order_road
        ney = world.marshals["Ney"]
        ney.location = "Franconia"
        with _quiet():
            world._build_marshal_index()
            world.calculate_visibility()
            assert T.give(world, ney)["given"]
            assert T.give(world, world.marshals["Davout"])["given"]
        assert standing_order_road(world, ney)["goes_for"] == "Bohemia"
        assert standing_order_road(world, world.marshals["Davout"])["goes_for"] == "", "a hold says holds"
        ney.strategic_order.opening_take = None                 # the take has been run
        assert standing_order_road(world, ney)["goes_for"] == ""
        badge = (CLIENT / "scenes" / "map_renderer_base.gd").read_text(encoding="utf-8",
                                                                       errors="replace")
        label = badge[badge.index("func order_arrow_label("):badge.index("func _arrows_take_clicks(")]
        assert 'return "marches on " + goes + " as this turn ends"' in label
        assert label.index('var goes := str(info.get("goes_for", ""))') < label.index('return "holds " + dest')

    def test_an_orders_badge_stands_clear_of_the_selection_ring(self):
        """Three readers over three rounds read the map badge of the selected
        man as "…olds Franconia" / "narches on Bohemia": it began under the
        ring at his feet."""
        layer = (CLIENT / "scenes" / "map_order_layer.gd").read_text(encoding="utf-8", errors="replace")
        geometry = layer[layer.index("func _arrow_geometry() -> Array:"):layer.index("func _clear_of_rings(")]
        assert "if badge.size != Vector2.ZERO and pts.size() == 1:" in geometry
        assert "badge = _clear_of_rings(badge, xform)" in geometry
        clear = layer[layer.index("func _clear_of_rings("):layer.index("static func _overlaps_any(")]
        assert "for ring in _rings:" in clear and "badge.position.x = box.end.x + 2.0" in clear
        # the ring's box is the one `_draw` draws: r wide, 0.42 as tall
        assert "Vector2(r, r * 0.42)" in clear and "maxf(float(ring[\"r\"]) * zoom, 9.0)" in clear
        # the review (the client's lane): the moved badge is kept ON the layer
        # (to the ring's left where the right has no room), and clearing one
        # ring of a group does not leave it under the next (two passes)
        assert "if size.x > 0.0 and box.end.x + 2.0 + badge.size.x > size.x:" in clear
        assert "badge.position.x = maxf(0.0, box.position.x - 2.0 - badge.size.x)" in clear
        assert "for _pass in range(2):" in clear

    def test_r7_trust_is_shown_on_its_scale(self):
        """"Trust: 15 (Critical)" has no scale."""
        dialog = (CLIENT / "scripts" / "redemption_dialog.gd").read_text(encoding="utf-8")
        assert 'trust_label.text = "Trust: %d of 100 — critical" % trust' in dialog


class TestTheCaptureQuestionIsAskedOnce:
    """IC2B-X6 (the pressing): the night of his take the province he took asks
    "plunder or secure" — and on a turn that also opened a great battle the
    question reached the player TWICE: once on the reply to a word given on
    the battle's panel, and again from the end-turn response's stash when
    control came back; the second answer read "No pending capture choice."
    The answer now clears the stash (the server's reply says what still
    stands)."""

    def test_an_answer_clears_the_stashed_copy_before_the_chain(self):
        main = (CLIENT / "scripts" / "main.gd").read_text(encoding="utf-8", errors="replace")
        start = main.index("func _on_capture_choice_response(response):")
        body = main[start:main.index("\nfunc ", start + 10)]
        assert "pending_capture_response = null" in body
        assert body.index("_sync_response_hud(response)") < body.index("pending_capture_response = null") \
            < body.index("if _response_has_capture_choice_route(response):")

    def test_the_server_refuses_a_second_answer_and_spends_nothing(self, world, monkeypatch):
        """The server's half was sound: one question, one answer."""
        from backend.commands.strategic import StrategicOrderProcessor
        ney = world.marshals["Ney"]
        ney.location = "Franconia"
        with _quiet():
            world._build_marshal_index()
            world.calculate_visibility()
            assert T.give(world, ney)["given"]
            executor = CommandExecutor()
            StrategicOrderProcessor(executor).process_strategic_orders(
                world, {"world": world, "executor": executor})
        assert world.pending_capture_choice and world.pending_capture_choice.get("region") == "Bohemia"
        client = _client(monkeypatch, world)
        with _quiet():
            first = client.post("/capture_choice", json={"choice": "secure"}).json()
            second = client.post("/capture_choice", json={"choice": "plunder"}).json()
        assert first["success"] is True
        assert second["success"] is False and "No pending capture choice" in second["message"]
        assert world.get_region("Bohemia").controller == "France"


class TestAGreatBattleOfAManOnHisTask:
    """A great battle is fought in turns, the Emperor's hand in it (row BA).
    When its lead is a man on his task the hand keeps to the ruling: HIS corps
    takes no word of the day (counter-attack, dig in, retreat — each greyed
    with the reason), another corps may still be sent to him, and "Let him
    decide" runs the day by his own judgement — the game's own carrying-out,
    never bounced by the no-orders refusal. The battle is on his task's record."""

    @pytest.fixture
    def served(self):
        """The game server with a campaign on it — the only place a day
        exists (`tests/test_ba3_the_rounds.py`'s own table)."""
        before = M.world
        try:
            with TestClient(M.app) as client:
                with _quiet():
                    booted = client.post("/new_game", json={"seed": "iron-eagle-07"}).json()
                assert booted["success"], booted.get("message")
                yield client
        finally:
            M._set_active_world(before)

    @staticmethod
    def _seat(world):
        """Ney and Davout at Rhineland, Mack's larger army beside them at
        Lorraine, at war and in sight (the served board is bare Europe: the
        marshals carry their own ground)."""
        from backend.models.marshal import Marshal

        def corps(name, where, men, nation="France", personality="aggressive"):
            marshal = Marshal(name=name, location=where, strength=int(men), personality=personality,
                              nation=nation, movement_range=1, tactical_skill=7, spawn_location=where)
            marshal.skills["command"] = 6
            return marshal
        home, field = "Rhineland", "Lorraine"
        assert field in world.get_region(home).adjacent_regions, "the suite's boards changed"
        ney = corps("Ney", home, 55000)
        davout = corps("Davout", home, 20000, personality="cautious")
        mack = corps("Mack", field, 70000, nation="Austria")
        world.marshals = {m.name: m for m in (ney, davout, mack)}
        world.diplomatic_states[world._make_diplo_key("Austria", "France")] = "WAR"
        for province in (home, field):
            world.update_intel_from_battle(province, int(world.current_turn))
        world.battle_days = {}
        world.actions_remaining = 4
        return ney

    def _a_day_on_his_defence(self, client):
        """Ney is given his task (he holds: Mack is too strong for him), the
        turn ends, and Mack opens a great battle against him — tried again on
        the campaign's next dice until the day hangs."""
        for _try in range(30):
            world = M.world
            ney = self._seat(world)
            with _quiet():
                assert T.give(world, ney)["given"]
                client.post("/command", json={"command": "end turn"})
                days = (client.get("/battle_day").json().get("days") or []
                        if (world.battle_days or {}).get("days") else [])
            day = next((d for d in days if d.get("lead") == "Ney" and d.get("open")
                        and d.get("awaits") == "ours"), None)
            if day is not None and T.on_trial(ney):
                return world, ney, day
        raise AssertionError("no day of battle opened on his defence")

    def test_the_days_panel_gives_his_corps_no_word(self, served):
        _world, ney, day = self._a_day_on_his_defence(served)
        left = int(ney.trial["turns_left"])
        reason = f"on his task to prove himself — he takes no orders ({left} turns left)"
        for kind in ("press", "dig_in", "break_off"):
            chip = next(c for c in day["chips"] if c["kind"] == kind)
            assert chip["ok"] is False and chip["why"] == reason, chip
        sent = [c for c in day["chips"] if c["kind"] == "lead"]
        assert sent and all(c["ok"] for c in sent), "another corps may still be sent to him"
        leave = next(c for c in day["chips"] if c.get("word") == "leave_it")
        assert leave["ok"] is True and leave["label"] == "Let Ney decide"

    def test_a_lead_left_to_it_never_brings_up_a_man_on_his_task(self, world):
        """IC2B-X8 (the pressing: "9 Let Ney decide — he will bring up a
        corps", with Davout on his own task beside him): the day's rule for a
        lead left to his own judgement brings up the strongest corps beside
        him — and would have marched a man on his task off it. He is passed
        over; the next corps is weighed."""
        from backend.ai.enemy_ai import EnemyAI
        ney, mack, soult = world.marshals["Ney"], world.marshals["Mack"], world.marshals["Soult"]
        assert soult.location in world.get_region(ney.location).adjacent_regions
        terms = {"marshal": ney, "foe": mack, "world": world, "nation": "France", "purse": 2,
                 "opened": False, "behind": False, "strike_price": 1, "defenders": 52000,
                 "combined": 24000, "ratio": 24000 / 52000, "fit": True}
        ai = EnemyAI(CommandExecutor())
        word = ai._the_days_decision(dict(terms), 1.0)
        assert (word["kind"], word.get("who")) == ("bring_up", "Soult"), "the premise"
        with _quiet():
            assert T.give(world, soult)["given"]
        word = ai._the_days_decision(dict(terms), 1.0)
        assert word.get("who") != "Soult", word
        assert soult.location == "Lorraine" and T.on_trial(soult)

    def test_the_desk_says_he_takes_no_orders_and_what_is_still_yours(self, served):
        """IC2B-X7 (the pressing): the desk's row for his open battle read
        "… Ney still waits for your orders." — of a man who takes none."""
        from backend.game_logic import today
        world, _ney, day = self._a_day_on_his_defence(served)
        row = next(r for r in today.decide(world) if r["id"] == f"day:{day['enemy']}")
        assert row["text"] == ("The battle at Rhineland has no winner yet — Ney takes no orders; "
                               "you can send him help.")
        assert "waits for your orders" not in row["text"]
        assert row["door"] == {"kind": "day", "enemy": "Mack"}

    def test_let_him_decide_runs_the_day_and_the_battle_is_on_his_record(self, served):
        _world, ney, _day = self._a_day_on_his_defence(served)
        with _quiet():
            reply = served.post("/battle_day/word", json={"enemy": "Mack", "word": "leave_it"}).json()
        assert reply["success"] is True, reply.get("message")
        assert "takes no orders" not in str(reply.get("message") or "")
        won, lost, _taken = T.achieved(ney)
        assert won + lost >= 1, "what he fought on his task counts"
        assert T.on_trial(ney)

    def test_his_own_word_typed_is_refused_free(self, served):
        world, ney, _day = self._a_day_on_his_defence(served)
        actions = world.actions_remaining
        with _quiet():
            reply = served.post("/command", json={"command": "Ney, attack Mack"}).json()
        assert reply["success"] is False
        assert "takes no orders until it ends" in reply["message"]
        assert world.actions_remaining == actions


# ═══════════════════════════ the siblings ═══════════════════════════════════
#
# Golden rule 10 — a fix ends with a search for its class. What that search
# found beside this session's own rows (`docs/BUG_FIXES.md` §"Row IC, Session
# 2b": IC2B-X14, X16, X17, X18), each fixed here and pinned.

def _load_the_driver():
    """`tools/playtest_driver.py`, loaded by path (it is a script, not a
    package member — `tests/test_iq7_satellites_have_a_position.py`'s idiom)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "playtest_driver_ic9b", str(REPO / "tools" / "playtest_driver.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestTheSiblingsOfThisSessionsRows:

    def test_x14_the_drivers_digest_says_how_a_task_went(self):
        """The measure's find: a digest showed a task GIVEN and never its end
        — the count's lines ride the turn's events (told once by the game),
        and no order row carries them."""
        driver = _load_the_driver()

        class Rec:
            trial_lines = driver.Digest.trial_lines

            def __init__(self):
                self.lines, self.records = [], []

            def _md(self, text):
                self.lines.append(text)

            def record(self, kind, **fields):
                self.records.append({"kind": kind, **fields})

        rec = Rec()
        rec.trial_lines([
            {"type": "battle", "message": "not a task's line"},
            {"type": "marshal_trial", "phase": "roll", "marshal": "Ney", "band": "",
             "message": "Ney is on a roll — last turn he won a battle and lost none."},
            {"type": "marshal_trial", "phase": "ended", "marshal": "Murat", "band": "good",
             "message": "Murat did well on his task. In 3 turns he won 1 battle. His trust in "
                        "you rises by 25 (to 44). He is under your orders again."},
            {"type": "marshal_trial", "phase": "ended", "marshal": "Lannes", "message": ""},
        ])
        assert rec.lines == [
            "- TASK Ney [roll]: Ney is on a roll — last turn he won a battle and lost none.",
            "- TASK Murat [ended]: Murat did well on his task. In 3 turns he won 1 battle. His "
            "trust in you rises by 25 (to 44). He is under your orders again."]
        assert [(r["kind"], r["marshal"], r["phase"], r["band"]) for r in rec.records] == [
            ("trial", "Ney", "roll", ""), ("trial", "Murat", "ended", "good")]
        rec.trial_lines(None)                       # a reply with no events says nothing
        assert len(rec.lines) == 2
        # a roll's line runs to about 250 characters and is kept WHOLE (the
        # review: the cut at 240 dropped "… in 3 turns at most.")
        roll = ("Ney is on a roll — last turn he won a battle and lost none. He presses on with "
                "his task one more turn and goes for Upper Austria as this turn ends. He still "
                "takes no orders; he comes back to you when a turn ends without a victory, in 3 "
                "turns at most.")
        assert len(roll) > 240
        rec.trial_lines([{"type": "marshal_trial", "phase": "roll", "marshal": "Ney", "message": roll}])
        assert rec.lines[-1] == f"- TASK Ney [roll]: {roll}"
        source = (REPO / "tools" / "playtest_driver.py").read_text(encoding="utf-8")
        assert source.count('digest.trial_lines(response.get("tactical_events"))') == 2, \
            "read at both places a turn's reply is digested"
        assert driver.POLICY_DEFAULTS["redemption"] == "trial"

    def test_x16_the_generals_page_says_any_order_in_the_players_words(self, world):
        """IC2B-X5's sibling: under every OTHER marshal the page still said
        "Order: HOLD → Franconia" — the code's own word. The server sends the
        words (the one display map; the client holds no copy)."""
        from backend.game_logic.marshal_overview import _build_current_status
        from backend.models.marshal import StrategicOrder
        davout = world.marshals["Davout"]
        turn = int(world.current_turn)
        said = {}
        for kind, target in (("HOLD", "Franche_Comte"), ("MOVE_TO", "Upper_Austria"),
                             ("PURSUE", "Archduke_Charles"), ("SUPPORT", "Ney")):
            davout.strategic_order = StrategicOrder(
                command_type=kind, target=target, target_type="region", started_turn=turn,
                issued_turn=turn, original_command="an order")
            row = _build_current_status(davout)["strategic_order"]
            assert (row["command_type"], row["target"]) == (kind, target), \
                "the keys every other reader uses stay as they were"
            said[kind] = (row["display"], row["target_shown"])
        assert said == {"HOLD": ("Hold", "Franche Comte"), "MOVE_TO": ("March", "Upper Austria"),
                        "PURSUE": ("Pursue", "Archduke Charles"), "SUPPORT": ("Support", "Ney")}
        davout.strategic_order = None
        assert _build_current_status(davout)["strategic_order"] is None
        page = (CLIENT / "scripts" / "marshal_management.gd").read_text(encoding="utf-8",
                                                                        errors="replace")
        assert page.count('strat.get("display", strat.get("command_type", "?"))') == 2
        assert page.count('strat.get("target_shown", strat.get("target", "?"))') == 2
        assert '"]Order: " + str(strat.get("command_type"' not in page

    def test_x17_the_turns_report_says_he_takes_no_orders_too(self, world):
        """IC2B-X7's sibling: the report after End Turn said "… no winner yet:
        the battle waits for your orders this turn" of a battle whose lead
        takes none."""
        from backend.game_logic import while_you_waited as W
        ney = world.marshals["Ney"]
        event = {"type": "battle", "attacker_nation": "Austria", "defender_nation": "France",
                 "attacker": {"name": "Mack", "casualties": 900},
                 "defender": {"name": "Ney", "casualties": 700},
                 "victor": "", "outcome": "stalemate", "location": ney.location,
                 "diorama": {"day": {"open": True, "awaits": "ours", "lead": "Ney"}}}
        plain = W._our_battles(world, [event])[0]
        assert plain["result"] == "open"
        assert ("Mack attacked Ney — no winner yet: the battle waits for your orders this turn."
                in plain["line"]), "the premise: any other lead reads as he did"
        with _quiet():
            assert T.give(world, ney)["given"]
        on_task = W._our_battles(world, [event])[0]
        assert ("Mack attacked Ney — no winner yet: Ney takes no orders; you can send him help "
                "this turn.") in on_task["line"]
        assert "waits for your orders" not in on_task["line"]
        # ... and a day that waits on the enemy says what it said
        theirs = dict(event, diorama={"day": {"open": True, "awaits": "theirs", "lead": "Ney"}})
        assert "no winner yet: the battle goes on." in W._our_battles(world, [theirs])[0]["line"]

    def test_x18_a_wrong_answer_is_told_the_answers_in_words(self, world):
        """The audience's refusal of an answer it did not offer listed bare
        keys — "Ney awaits one of: trial, administrative_role, dismiss." Each
        typed key now carries what it does (golden rule 11: a pinned key keeps
        its name; plain words ride beside it)."""
        ney = world.marshals["Ney"]
        with _quiet():
            ney.trust.set(15)
            event = world.disobedience_system.check_redemption_threshold(ney, world)
            refused = world.disobedience_system.handle_redemption_response(
                event, "demand_obedience", {"world": world})
        from backend.commands.disobedience import answers_in_words, not_an_answer_words
        said_no = ("That is not one of the answers open to you. Ney is waiting for one of: "
                   "trial (Give Ney a task to prove himself); administrative_role (Transfer Ney "
                   "to Staff); dismiss (Dismiss Ney).")
        assert refused["success"] is False and refused["message"] == said_no
        assert refused["offered_options"] == ["trial", "administrative_role", "dismiss"]
        assert not T.on_trial(ney) and world.pending_redemption, "nothing given; the question stands"
        # (the review: no period voice outside a character's quoted line)
        assert "Sire" not in refused["message"] and "courses" not in refused["message"]
        # ONE sentence for the handler and the endpoint, which answered the bare
        # keys first ("Invalid choice: 'demand_obedience'. Valid: trial, …")
        assert not_an_answer_words(event, ["trial", "administrative_role", "dismiss"]) == said_no
        # an old save's arm is named by what it is now, never by what left the game
        old = copy.deepcopy(event)
        old["options"][0] = {"id": "grant_autonomy", "text": "Grant Autonomy",
                             "description": "", "effect": ""}
        said = answers_in_words(old, ["trial", "dismiss"])
        assert said == "trial (give him a task to prove himself); dismiss (Dismiss Ney)"
        assert "autonom" not in said.lower()


# ═══════════════════════════ the review ═════════════════════════════════════
#
# The one review before the commit (three readers by lane on a frozen copy
# outside the repository; every finding reproduced on a live board or traced
# in the code before it was fixed — `docs/BUG_FIXES.md` §"Row IC, Session 2b",
# rows IC2B-V1 …). The server's lane found the class that mattered: an order
# typed with NO NAME on it never met the refusal, which reads the name.

def _alone_at_franconia(world, name="Ney"):
    """`name` at Franconia (he proposes to take Bohemia), every other French
    corps far away in Brittany — so he is the nearest man to anything."""
    man = world.marshals[name]
    man.location = "Franconia"
    for key, other in world.marshals.items():
        if other.nation == "France" and key != name:
            other.location = "Brittany"
    with _quiet():
        world._build_marshal_index()
        world.calculate_visibility()
    return man


class TestWhatTheReviewFound:

    # ── orders with no name on them ─────────────────────────────────────────

    def test_v1_a_retreat_with_no_name_leaves_him_at_his_task(self, world, monkeypatch):
        """Reproduced: "retreat" answered "General retreat ordered! Ney
        falling back! …" and walked him from Swabia to Lorraine — the call-back
        the user ruled out."""
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        ney.location, ney.strength = mack.location, 8000         # with a stronger enemy: in danger
        with _quiet():
            world._build_marshal_index()
            world.calculate_visibility()
            assert T.give(world, ney)["given"]
        assert world.is_in_danger("Ney"), "the premise: the general retreat would take him"
        client = _client(monkeypatch, world)
        actions = world.actions_remaining
        with _quiet():
            reply = client.post("/command", json={"command": "retreat"}).json()
        assert "Ney falling back" not in reply["message"]
        assert "Ney keeps to his task to prove himself — he takes no orders." in reply["message"]
        assert ney.location == mack.location and not getattr(ney, "retreating", False)
        assert T.on_trial(ney) and ney.strategic_order.target == mack.location
        with _quiet():            # ... and with nobody else left to go it is refused free, saying why
            again = client.post("/command", json={"command": "everyone retreat"}).json()
        assert again["success"] is False
        assert again["message"] == "Ney keeps to his task to prove himself — he takes no orders."
        assert world.actions_remaining == actions

    def test_v2_an_attack_with_no_name_never_picks_him(self, world):
        """A bare "attack" with nobody in contact marches the nearest corps
        toward the enemy at the player's cost — and the scan had no word for
        a man on his task."""
        ney = _alone_at_franconia(world)
        combat = CommandExecutor()._combat
        ready, far, _why = combat._scan_general_attack_candidates(world)
        assert "Ney" in [m.name for m, _e, _d in ready + far], "the premise: he is the pick"
        with _quiet():
            assert T.give(world, ney)["given"]
        ready, far, why = combat._scan_general_attack_candidates(world)
        assert "Ney" not in [m.name for m, _e, _d in ready + far]
        assert "Ney (on his task to prove himself — he takes no orders)" in why

    def test_v3_a_scout_or_a_bombardment_with_no_name_never_picks_him(self, world, monkeypatch):
        """Reproduced: "scout Bohemia" answered "Ney scouts Bohemia …" and
        took an action — the nameless scout and bombardment are routed to the
        man they pick BELOW the executor's refusal."""
        ney = _alone_at_franconia(world)
        with _quiet():
            assert T.give(world, ney)["given"]
        client = _client(monkeypatch, world)
        actions = world.actions_remaining
        with _quiet():
            reply = client.post("/command", json={"command": "scout Bohemia"}).json()
        assert reply["success"] is False and world.actions_remaining == actions
        assert reply["message"].startswith(
            "No marshal who takes orders is in scout range of Bohemia: Ney is on his task to prove "
            "himself and takes no orders until it ends (3 turns left")
        ney.artillery = True                                     # ... and his guns
        with _quiet():
            fired = CommandExecutor()._combat._execute_auto_assign_bombardment(
                {"target": "Bohemia"}, {"world": world})
        assert fired["success"] is False and fired.get("no_action_cost") is True
        assert "takes no orders until it ends" in fired["message"]
        assert int(getattr(ney, "bombardments_this_turn", 0) or 0) == 0

    def test_v4_the_nearest_man_to_be_ordered_is_never_him(self, world):
        """"attack Mack" names the nearest corps — who would only refuse."""
        ney = _alone_at_franconia(world)
        assert world.find_nearest_marshal_to_region("Bohemia")[0].name == "Ney", "the premise"
        with _quiet():
            assert T.give(world, ney)["given"]
        assert world.find_nearest_marshal_to_region("Bohemia")[0].name == "Ney", \
            "men are still SENT to him: the levy's and the recruit's pick is unchanged"
        assert world.find_nearest_marshal_to_region("Bohemia", for_order=True) is None
        assert ("Ney (on his task to prove himself — he takes no orders)"
                in world._last_nearest_marshal_block)

    def test_v5_an_old_objection_of_his_carries_nothing_out(self, world):
        """An objection can outlive the order it was about; "proceed" on it
        runs that order on a road that sits below the executor's refusal."""
        ney = world.marshals["Ney"]
        world.pending_objection = {"marshal": "Ney", "type": "objection"}
        world.pending_strategic_objection = {"marshal_name": "Ney", "strategic_type": "MOVE_TO"}
        with _quiet():
            assert T.give(world, ney)["given"]
        assert world.pending_objection is None and world.pending_strategic_objection is None
        world.pending_objection = {"marshal": "Davout"}          # another man's question is his own
        T._drop_his_objection(world, ney)
        assert world.pending_objection == {"marshal": "Davout"}
        world.pending_objection = None
        executor = CommandExecutor()
        with _quiet():
            reply = executor._meta._execute_post_objection(
                {"command": {"marshal": "Ney", "action": "attack", "target": "Mack"}},
                {"world": world, "executor": executor}, "Ney")
        assert reply["success"] is False and "takes no orders until it ends" in reply["message"]

    def test_a_list_of_orders_shows_him_unticked_and_orders_nobody_for_him(self, world, monkeypatch):
        """An order to several corps is ONE list first: his row says why he
        will not go, and "everyone …" is the same list."""
        ney = world.marshals["Ney"]
        ney.location = "Franconia"
        with _quiet():
            world._build_marshal_index()
            world.calculate_visibility()
            assert T.give(world, ney)["given"]
        client = _client(monkeypatch, world)
        actions = world.actions_remaining
        with _quiet():
            listed = client.post("/command", json={"command": "Ney and Davout, march to Swabia",
                                                   "list_first": True}).json()
        rows = {row["marshal"]: row for row in listed["directive"]["rows"]}
        assert rows["Ney"]["ok"] is False and rows["Ney"]["ticked"] is False
        assert rows["Ney"]["why"] == "on his task to prove himself — he takes no orders (3 turns left)"
        assert rows["Davout"]["ok"] is True
        with _quiet():
            everyone = client.post("/command", json={"command": "everyone, hold",
                                                     "list_first": True}).json()
        ney_row = next(r for r in everyone["directive"]["rows"] if r["marshal"] == "Ney")
        assert ney_row["ok"] is False and "takes no orders" in ney_row["why"]
        assert world.actions_remaining == actions and ney.location == "Franconia"
        assert ney.strategic_order.opening_take == "Bohemia"

    def test_a_quote_gives_the_true_reason_first(self, world):
        """The probe: the take's quote read "Mack stands there — he must be
        beaten first" of a man who can be sent at nobody; and his reach on the
        map is empty (no road, no price to hover)."""
        from backend.commands import order_quotes as Q
        ney = world.marshals["Ney"]
        ney.location = "Franconia"
        with _quiet():
            world._build_marshal_index()
            world.calculate_visibility()
            assert T.give(world, ney)["given"]
            taken = Q.take_quote(world, ney, "Swabia")
            reach = Q.march_reach(world, ney)
        reason = "on his task to prove himself — he takes no orders (3 turns left)"
        assert taken["ok"] is False and taken["refusal"] == reason
        assert reach["ok"] is False and reach["refusal"] == reason and reach["reach"] == {}

    # ── the second read: the review's own fixes, read by one more reader ────

    def test_the_second_read_a_bare_attack_is_refused_in_his_own_words(self, world, monkeypatch):
        """With the first fix a bare "attack" passed over him — and then
        marched a DISTANT corps toward the enemy at the player's cost
        ("Davout advances toward Mack: Brittany -> Anjou"). The man in contact
        is the man the order meant: it is refused free, in his own words."""
        ney = _alone_at_franconia(world)
        with _quiet():
            assert T.give(world, ney)["given"]
        davout = world.marshals["Davout"]
        client = _client(monkeypatch, world)
        actions = world.actions_remaining
        with _quiet():
            reply = client.post("/command", json={"command": "attack"}).json()
        assert reply["success"] is False and world.actions_remaining == actions
        assert reply["message"].startswith(
            "Ney is on his task to prove himself and takes no orders until it ends (3 turns left")
        assert davout.location == "Brittany" and ney.location == "Franconia", "nobody marched"

    def test_the_second_read_an_attack_on_a_named_place_says_why_nobody_goes(self, world):
        """"attack Bohemia" answered "No marshals in range of Bohemia" — with
        a marshal standing beside it who takes no orders."""
        ney = _alone_at_franconia(world)
        with _quiet():
            assert T.give(world, ney)["given"]
            picked = CommandExecutor()._combat._resolve_auto_assign_attacker(
                {"target": "Bohemia"}, world)
        assert picked["kind"] == "error"
        refused = picked["error"]
        assert refused["success"] is False and refused.get("no_action_cost") is True
        assert "No marshals in range" not in refused["message"]
        assert refused["message"].startswith("Ney is on his task to prove himself and takes no orders")

    def test_the_second_read_the_retreats_other_replies_keep_his_note(self, world, monkeypatch):
        """Two replies of the general retreat dropped "he keeps to his task":
        when another man is held by a last stand, and when the others' retreat
        fails."""
        from backend.commands import strategic as S
        ney, davout, mack = world.marshals["Ney"], world.marshals["Davout"], world.marshals["Mack"]
        for man in (ney, davout):
            man.location, man.strength = mack.location, 8000
        for name, other in world.marshals.items():
            if other.nation == "France" and name not in ("Ney", "Davout"):
                other.location = "Brittany"
        with _quiet():
            world._build_marshal_index()
            world.calculate_visibility()
            assert T.give(world, ney)["given"]
        assert world.is_in_danger("Ney") and world.is_in_danger("Davout"), "the premise"
        stays = "Ney keeps to his task to prove himself — he takes no orders."
        combat = CommandExecutor()._combat
        # (1) Davout is cornered and owes an answer: he is left, and so is Ney — both said
        monkeypatch.setattr(S, "standing_last_stand_refusal",
                            lambda marshal: {"held": True} if marshal.name == "Davout" else None)
        monkeypatch.setattr(S, "last_stand_question_line", lambda marshal: "Davout is cornered.")
        with _quiet():
            held = combat._execute_general_retreat({"action": "retreat"}, {"world": world})
        assert held["success"] is False and held.get("last_stand_pending") is True
        assert held["message"] == f"Davout is cornered. The general retreat leaves him where he stands. {stays}"
        # (2) Davout's retreat fails: the reply still says why Ney did not go
        monkeypatch.setattr(S, "standing_last_stand_refusal", lambda marshal: None)
        monkeypatch.setattr(type(combat._executor._movement), "_execute_retreat_action",
                            lambda self, marshal, w, gs: {"success": False, "message": "surrounded"})
        with _quiet():
            failed = combat._execute_general_retreat({"action": "retreat"}, {"world": world})
        assert failed["success"] is False
        assert failed["message"] == f"Davout: surrounded {stays}"
        assert ney.location == mack.location and T.on_trial(ney)

    # ── the audience's refusals ─────────────────────────────────────────────

    @staticmethod
    def _ask(world, name="Ney"):
        marshal = world.marshals[name]
        with _quiet():
            marshal.trust.set(15)
            event = world.disobedience_system.check_redemption_threshold(marshal, world)
        assert event is not None and world.pending_redemption is event
        return marshal

    def test_an_answer_that_cannot_be_carried_out_brings_the_window_back(self, world, monkeypatch):
        """The client's lane: a refused "pay what he is owed" closed the window
        with nothing to bring it back (the reply carried no question). EVERY
        refusal that leaves the question standing carries it again."""
        ney = self._ask(world)
        client = _client(monkeypatch, world)
        with _quiet():
            wrong = client.post("/respond_to_redemption", json={"choice": "demand_obedience"}).json()
        assert wrong["success"] is False and wrong["standing"] is True
        assert wrong["message"].startswith(
            "That is not one of the answers open to you. Ney is waiting for one of: "
            "trial (Give Ney a task to prove himself);")
        assert "Invalid choice" not in wrong["message"]
        assert wrong["redemption_event"]["marshal"] == "Ney"
        assert wrong["state"] == "awaiting_redemption_choice"
        # ... a rente the treasury cannot pay: the handler's refusal carries no question
        monkeypatch.setattr(type(world.disobedience_system), "handle_redemption_response",
                            lambda self, **kw: {"success": False, "standing": True,
                                                "message": "The treasury cannot pay it."})
        with _quiet():
            poor = client.post("/respond_to_redemption", json={"choice": "trial"}).json()
        assert poor["success"] is False and poor["message"] == "The treasury cannot pay it."
        assert poor["standing"] is True and poor["redemption_event"]["marshal"] == "Ney"
        assert poor["redemption_event"]["options"][0]["id"] == "trial"
        assert world.pending_redemption is not None and ney.redemption_pending

    def test_the_window_sends_back_what_it_showed(self, world, monkeypatch):
        """The server's lane: "what was shown is what is given" compared the
        answer with the server's OWN last read of the board — a delivery the
        window never took up moved that line under the player's eye. The
        window sends back the line it displayed."""
        ney = self._ask(world)                                   # at Rhineland: he asks to hold
        on_screen = T.shown_line(world.pending_redemption)
        assert on_screen.startswith("Ney, hold Rhineland.")
        ney.location = "Franconia"                               # the board changes ...
        with _quiet():
            world._build_marshal_index()
            world.calculate_visibility()
        client = _client(monkeypatch, world)
        with _quiet():
            client.get("/pending_redemption")                    # ... and a read moves the stored line
        assert T.shown_line(world.pending_redemption) == "Ney, take Bohemia and hold it."
        with _quiet():
            reply = client.post("/respond_to_redemption",
                                json={"choice": "trial", "shown": on_screen}).json()
        assert reply["success"] is False and reply["standing"] is True, \
            "what the WINDOW showed is not what he proposes now: nothing is given"
        assert not T.on_trial(ney)
        with _quiet():
            given = client.post("/respond_to_redemption",
                                json={"choice": "trial",
                                      "shown": "Ney, take Bohemia and hold it."}).json()
        assert given["success"] is True and T.on_trial(ney)
        # ... and the client's half: the window keeps the line it shows, and sends it
        dialog = (CLIENT / "scripts" / "redemption_dialog.gd").read_text(encoding="utf-8")
        assert '_shown_line = str(asked.get("line", "")) if asked is Dictionary else ""' in dialog
        assert "func shown_line() -> String:" in dialog
        api = (CLIENT / "scripts" / "api_client.gd").read_text(encoding="utf-8", errors="replace")
        assert 'body["shown"] = shown' in api
        main = (CLIENT / "scripts" / "main.gd").read_text(encoding="utf-8", errors="replace")
        assert "api_client.send_redemption_response(choice, _on_redemption_response, shown)" in main
        assert '["trial", "dismiss", "administrative_role", "settle_account"]' in main, \
            "the typed answers take every answer the fallback names"

    def test_the_client_keeps_every_answer_on_the_screen_and_no_order_on_his_page(self):
        """Pins beside the driven classes that PRESS these in the real client
        (`TestRowIC9bTheAudienceAtTheCompactView`, `TestRowIC9bTheTaskToProve
        Himself::test_the_generals_page_shows_his_task_and_no_order_button`)."""
        dialog = (CLIENT / "scripts" / "redemption_dialog.gd").read_text(encoding="utf-8")
        fit = dialog[dialog.index("func _settle_fit() -> void:"):dialog.index("func _place_captions(")]
        # the other answers' words step aside first (the roomy band) ...
        assert "if need > view - WINDOW_RESERVE - 2.0 * Utils.top_bar_growth():" in fit
        # ... then, only where the window would run off the SCREEN, his quoted
        # line, and then the proposal scrolls - never less than its least room
        assert "var screen: float = view - SCREEN_RESERVE - 2.0 * Utils.top_bar_growth()" in fit
        assert fit.index("message_label.visible = false") < fit.index("_proposal_in_scroll(")
        assert "_proposal_in_scroll(maxf(PROPOSAL_LEAST_ROOM, whole - (need - screen)))" in fit
        assert "scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_RESERVE" in fit
        # the second read: a later fit (a resize, a new audience) makes an
        # earlier one stand down at every one of its waits
        assert "_fit_pass += 1" in fit and "var mine: int = _fit_pass" in fit
        assert fit.count("if mine != _fit_pass or not is_inside_tree() or not visible:") == 4
        # a new audience and a refit start from the whole proposal again
        assert dialog.count("_proposal_out_of_scroll()\n\tmessage_label.visible = true") == 2
        page = (CLIENT / "scripts" / "marshal_management.gd").read_text(encoding="utf-8",
                                                                        errors="replace")
        bar = page[page.index("func _fill_order_bar(m: Dictionary) -> void:"):
                   page.index("func _order_button(")]
        assert 'var proving: bool = on_task is Dictionary and str(on_task.get("status", "")) != ""' in bar
        assert "note.text = TRIAL_NO_ORDERS" in bar and "if proving:\n\t\t\tbreak" in bar.replace("\r\n", "\n")
        assert ('const TRIAL_NO_ORDERS := "He takes no orders until his task ends, and you cannot '
                'call him back."') in page

    # ── his order, his questions, his nights ────────────────────────────────

    def test_a_question_his_order_raised_is_dropped_and_a_last_stand_is_left(self, world):
        ney = world.marshals["Ney"]
        with _quiet():
            assert T.give(world, ney)["given"]
        stands = ney.location
        asked = {"interrupt_type": "destination_blocked", "message": "The road is blocked.",
                 "options": ["wait", "reroute"]}
        ney.pending_interrupt = dict(asked)
        rows = [{"marshal": "Ney", "command": "HOLD", "order_status": "awaiting_response",
                 "requires_input": True, "interrupt_type": "destination_blocked",
                 "message": "Ney awaits your orders.", "options": ["wait", "reroute"],
                 "pending_interrupt": dict(asked)}]
        with _quiet():
            out = T.close_of_turn(world, rows)
        assert ney.pending_interrupt is None, "he asks the Emperor nothing: he takes no orders"
        assert out[0]["action"] == "trial_holds" and out[0]["order_status"] == "continues"
        assert out[0]["message"] == f"Ney keeps to his task: he holds {stands}."
        assert not {"requires_input", "options", "pending_interrupt", "interrupt_type"} & set(out[0])
        assert ney.strategic_order is not None and ney.strategic_order.command_type == "HOLD"
        # a last stand belongs to no order — it is the one question he still asks
        grave = {"interrupt_type": "last_stand", "message": "Surrounded.",
                 "options": ["fight", "breakout"]}
        ney.pending_interrupt = dict(grave)
        rows = [{"marshal": "Ney", "requires_input": True, "interrupt_type": "last_stand",
                 "message": "Surrounded.", "options": ["fight", "breakout"]}]
        with _quiet():
            out = T.close_of_turn(world, rows)
        assert ney.pending_interrupt == grave
        assert out[0]["requires_input"] is True and out[0]["options"] == ["fight", "breakout"]

    def test_a_march_that_asked_is_over_and_he_holds_again(self, world):
        """His fall back (a literal man's line) can leave him a march whose
        road is barred: the march ends with its question, and his hold is put
        back where he stands."""
        from backend.models.marshal import StrategicOrder
        soult = world.marshals["Soult"]
        with _quiet():
            assert T.give(world, soult)["given"]
        turn = int(world.current_turn)
        soult.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Champagne", target_type="region",
            started_turn=turn, issued_turn=turn, original_command="a fall back")
        soult.pending_interrupt = {"interrupt_type": "destination_blocked", "options": ["wait"]}
        with _quiet():
            T.close_of_turn(world, [])
        order = soult.strategic_order
        assert soult.pending_interrupt is None
        assert (order.command_type, order.target) == ("HOLD", soult.location)
        assert order.original_command == soult.trial["line"]

    def test_the_card_promises_a_march_only_while_his_order_carries_it(self, world):
        """The server's lane: the status read a COPY of the place — when his
        order was replaced under him the card kept promising the march."""
        ney = world.marshals["Ney"]
        ney.location = "Franconia"
        with _quiet():
            world._build_marshal_index()
            world.calculate_visibility()
            assert T.give(world, ney)["given"]
        assert T.announced_take(ney) == "Bohemia"
        assert T.status_words(ney) == ("On a task to prove himself — 3 turns left: "
                                       "marches on Bohemia as this turn ends")
        ney.strategic_order.opening_take = "Upper_Austria"       # a key is never shown: the name is
        assert T.status_words(ney).endswith("marches on Upper Austria as this turn ends")
        ney.strategic_order.opening_take = "Bohemia"
        kept = ney.strategic_order
        ney.strategic_order = None                               # a retreat, a fall back, the road home
        assert T.announced_take(ney) == "" and T.payload(ney)["next_take"] == ""
        assert T.status_words(ney) == "On a task to prove himself — 3 turns left"
        with _quiet():
            assert T.keep_the_hold(world, ney)
        assert T.status_words(ney) == "On a task to prove himself — 3 turns left"
        # a take dropped because his own line fired is said ONCE, and never run a night late
        ney.strategic_order = kept
        row = T.drop_take(ney, "he carried out a line of his orders instead")
        assert row["action"] == "trial_take_dropped" and row["place"] == "Bohemia"
        assert row["message"] == ("Ney does not march on Bohemia tonight: he carried out a line of "
                                  "his orders instead.")
        assert kept.opening_take is None and T.drop_take(ney, "again") is None
        assert T.drop_take(world.marshals["Davout"], "no task") is None

    def test_a_rolls_announced_place_is_run_by_the_pass_and_the_words_count_down(self, world):
        """The tests' lane: the roll was only ever ticked with a win poked in.
        Here the place a roll announces is RUN by the standing-order pass, and
        the words are read at every roll up to the cap."""
        from backend.commands.strategic import StrategicOrderProcessor
        ney = world.marshals["Ney"]
        ney.location = "Franconia"
        with _quiet():
            world._build_marshal_index()
            world.calculate_visibility()
            assert T.give(world, ney)["given"]
        ney.strategic_order.opening_take = None                  # (the first night's take is not this test's)
        with _quiet():
            assert T.tick(world) == [] and T.tick(world) == []   # turns 1 and 2
        ney.battles_won += 1                                     # turn 3, his last: a victory
        with _quiet():
            first = T.tick(world)
        assert first[0]["action"] == "trial_roll" and first[0]["place"] == "Bohemia"
        assert first[0]["message"].endswith("in 3 turns at most.")
        assert T.announced_take(ney) == "Bohemia"
        assert T.refusal_words(ney) == ("Ney is on his task to prove himself and takes no orders "
                                        "until it ends (1 turn left — up to 6 in all while he keeps "
                                        "winning).")
        executor = CommandExecutor()
        with _quiet():                                           # turn 4: the pass runs what was announced
            rows = StrategicOrderProcessor(executor).process_strategic_orders(
                world, {"world": world, "executor": executor})
        took = next(row for row in rows if row.get("marshal") == "Ney")
        assert took["action"] == "trial_take" and took["place"] == "Bohemia"
        assert took["message"].startswith("Ney marches on Bohemia, as he proposed.")
        assert world.get_region("Bohemia").controller == "France"
        assert T.announced_take(ney) == "", "run once"
        ney.battles_won += 1
        with _quiet():
            second = T.tick(world)
        assert second[0]["action"] == "trial_roll" and second[0]["message"].endswith("in 2 turns at most.")
        ney.strategic_order.opening_take = None
        ney.battles_won += 1                                     # turn 5
        with _quiet():
            third = T.tick(world)
        assert third[0]["action"] == "trial_roll" and third[0]["message"].endswith("in 1 turn at most.")
        assert T.refusal_words(ney) == ("Ney is on his task to prove himself and takes no orders "
                                        "until it ends (1 turn left)."), "six is reached: no longer"
        ney.strategic_order.opening_take = None
        ney.battles_won += 1                                     # turn 6: a victory still ends it
        with _quiet():
            last = T.tick(world)
        assert last[0]["action"] == "trial_ended" and last[0]["band"] == "spectacular"
        assert "In 6 turns he won 4 battles" in last[0]["message"]
        assert not T.on_trial(ney) and ney.strategic_order is None

    def test_a_refused_take_says_he_had_left_his_works(self, world, monkeypatch):
        from backend.commands.strategic import StrategicOrderProcessor
        ney = world.marshals["Ney"]
        ney.location = "Franconia"
        with _quiet():
            world._build_marshal_index()
            world.calculate_visibility()
            assert T.give(world, ney)["given"]
        ney.fortified = True
        executor = CommandExecutor()
        real = type(executor).execute

        def refuse_the_strike(self, command, game_state):
            cmd = (command or {}).get("command") or {}
            if cmd.get("action") == "attack" and cmd.get("_strategic_execution"):
                return {"success": False, "message": "the bridge is down."}
            return real(self, command, game_state)
        monkeypatch.setattr(type(executor), "execute", refuse_the_strike)
        with _quiet():
            rows = StrategicOrderProcessor(executor).process_strategic_orders(
                world, {"world": world, "executor": executor})
        row = next(row for row in rows if row.get("marshal") == "Ney")
        assert row["action"] == "trial_take_refused"
        assert row["message"] == ("Ney left his works but could not march on Bohemia: the bridge "
                                  "is down. He stands at Franconia.")
        assert not ney.fortified

    def test_a_man_taken_prisoner_or_gone_to_another_crown_has_no_task(self, world):
        ney, davout = world.marshals["Ney"], world.marshals["Davout"]
        with _quiet():
            assert T.give(world, ney)["given"] and T.give(world, davout)["given"]
        trust = ney.trust.value
        ney.captured_by = "Austria"                              # taken, his corps still counted
        with _quiet():
            rows = T.tick(world)
        mine = [row for row in rows if row["marshal"] == "Ney"]
        assert mine and mine[0]["action"] == "trial_ended" and mine[0]["band"] == ""
        assert mine[0]["message"] == "Ney's task to prove himself ended with his corps."
        assert ney.trial is None and ney.trust.value == trust, "nothing to settle"
        assert not T.keep_the_hold(world, ney)
        davout.nation = "Bavaria"                                # another crown's man now
        with _quiet():
            T.close_of_turn(world, [])
        assert davout.trial is None

    def test_a_line_already_told_is_not_told_again_after_a_save(self, world):
        ney = world.marshals["Ney"]
        with _quiet():
            assert T.give(world, ney)["given"]
            for _night in range(3):
                T.tick(world)
        told = T.morning_events(world)
        assert [row["phase"] for row in told] == ["ended"]
        again = _load(world.to_dict())
        assert T.morning_events(again) == [], "the mark is saved with the line"

    def test_the_morning_says_a_freed_or_a_driven_out_task_as_it_was_given(self, world):
        """The words' lane: the campaign log said "to take Swabia and hold it"
        of every take — of a province freed for an ally, or of an enemy driven
        off a friend's ground."""
        from backend import campaign_log as CL
        base_event = {"type": "marshal_trial", "phase": "given", "marshal": "Ney",
                      "nation": "France", "task": "take", "place": "Swabia"}
        freed = CL.format_event_oneliner({**base_event, "doing": "free Swabia for Bavaria and hold it"})
        assert freed == ("Ney is given a task to prove himself — to free Swabia for Bavaria and hold "
                         "it; he takes no orders until it ends")
        plain = CL.format_event_oneliner(dict(base_event))        # an event written before the key
        assert "to take Swabia and hold it" in plain
        ney = world.marshals["Ney"]
        ney.location = "Franconia"
        with _quiet():
            world._build_marshal_index()
            world.calculate_visibility()
            read = T.proposal(world, ney)
            assert T.give(world, ney)["given"]
        assert read["doing"] == "take Bohemia and hold it"
        logged = [e for e in world.event_log if e.get("type") == "marshal_trial"][-1]
        assert logged["doing"] == read["doing"]

    def test_the_odds_are_said_in_plain_words(self, world):
        """The words' lane: "(large force to his 24,000)" — what does "to his"
        mean?"""
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        with _quiet():
            said = T._odds_words(world, ney, "Mack")
        assert said in (f" (a large force, against his {ney.strength:,} men)",
                        f" ({mack.strength:,} men, against his {ney.strength:,} men)"), said
        assert " to his " not in said


# ═══════════════════════════ the words census ═══════════════════════════════
#
# `docs/INDEPENDENT_COMMAND_SPEC.md` §13: "A test reads every player-facing
# string of the marshals' screens: 'autonomy' and 'independent command' appear
# on none; 'on his own' appears only for a man you set; the jealous strike
# says 'without waiting for orders'; V2b says 'refused your order' (the
# vassals' autonomy scale is exempt by name)."
#
# WHAT IS READ: every string of prose (a literal with a space in it) in the
# server's code — docstrings apart — and in the client's scripts and scenes.
# Reading everything, rather than a list of "marshal" files, is what keeps a
# new file from slipping by; what is exempt is exempt BY NAME, below.

WORDS = {
    "autonomy": re.compile(r"autonom", re.I),
    "independent command": re.compile(r"independent command|act(?:s|ed|ing)? independently", re.I),
    "on his own": re.compile(r"\bon his own\b", re.I),
}

# The vassals' autonomy scale — exempt by name, for the word "autonomy" only.
# (1) The files whose whole subject is a client court's leash:
VASSAL_SCALE_FILES = {
    "backend/game_logic/vassal.py",
    "backend/commands/vassal_executor.py",
    "backend/game_logic/diplomacy.py",
    "backend/commands/diplomatic_executor.py",
    "godot-client/project-sovereign/scripts/diplomacy_wizard.gd",
    "godot-client/project-sovereign/scripts/diplomatic_ledger.gd",
}
# (2) Anywhere else: a line that names the scale's own subject.
VASSAL_SCALE_NAMES = re.compile(r"vassal|satellite|puppet|client|tribute", re.I)
# (3) ... and these, which speak of a client court without one of those names:
EXEMPT_BY_NAME = {
    ("backend/ai/state_desk.py", "invest, garrison it or grant autonomy"):
        "the desk's reading of a VASSAL's loyalty",
    ("backend/game_logic/imperial_designs.py", "a member's autonomy drift "):
        "the Confederation's members are client courts",
    ("backend/commands/meta_executor.py", "carries invest / autonomy / release chips per"):
        "the help's VASSALS line (the next line of it reads 'satellite')",
    ("backend/game_logic/moments.py", "whatever its autonomy"):
        "an authored letter about a client court",
    ("backend/game_logic/moments.py", "whatever their autonomy"):
        "an authored letter about client courts",
    # "on his own" as a POSSESSIVE — his own line, his own numbers — never
    # "by himself"; both are battle lines pinned by their own slices:
    ("backend/commands/economy_executor.py", "he stands ON his own "):
        "Berthier: 'he stands ON his own breaking line' (S14G-X143)",
    ("backend/game_logic/combat.py", " on his own numbers — his own "):
        "'at unfavorable odds on his own numbers — his own 26k against 60k' (PT-D1, DDB-36)",
}
# (5) Row IC, Session 3 (November 21, 2026): "on his own" — the reserved words
# of a man YOU set on his own (INDEPENDENT_COMMAND_SPEC §0's table) — taught BY
# NAME, string by string, as the census reads it (whole, whitespace folded).
# The pattern is NOT widened: a new string that says "on his own" fails here
# until it is read and added, and every entry must still stand
# (`test_every_exemption_names_a_string_that_is_there`). Exempt for that word only.
SET_BY_YOU = {
    # Row IC, Session 4 (IC-13): the LESSON's card that teaches it — the School of
    # War's "XX. On His Own" (the client's card and the server's mirror of its title).
    ('backend/game_logic/tutorial_state.py',
     'XIX. On His Own'):
        "the lesson's card that teaches setting a man on his own (Session 4, IC-13)",
    ('godot-client/project-sovereign/scripts/tutorial_overlay.gd',
     'XIX. On His Own'):
        "the lesson's card that teaches setting a man on his own (Session 4, IC-13)",
    ('godot-client/project-sovereign/scripts/tutorial_overlay.gd',
     'You can set a bold or a careful marshal on his own. Type his task on the command line — for example [color=#e8d4a8]Ney, take Swabia on your own[/color] — or use the chips under the line. Before you press Enter he answers in his own words, and the line under it says what he will do tonight. A marshal on his own acts each night without further orders. A marshal who follows orders to the letter (Soult) takes exact orders instead: [color=#e8d4a8]Soult, hold Lorraine. If attacked, dig in.[/color]'):
        "the lesson's card that teaches setting a man on his own (Session 4, IC-13)",
    ('backend/ai/own_words.py',
     'on his own'):
        "a mark of judgement the typed line takes ('on his own' typed of him)",
    ('backend/commands/parse_preview.py',
     'how boldly he goes is his own only on a task on his own, and {}'):
        'the read-back of a task on his own (§8.4)',
    ('backend/commands/parse_preview.py',
     'on his own — once given, {} of the {} you may have (laws raise it)'):
        'the read-back of a task on his own (§8.4)',
    ('backend/commands/parse_preview.py',
     'on his own — {}'):
        'the read-back of a task on his own (§8.4)',
    ('backend/commands/parse_preview.py',
     '{} cannot be set on his own: {}.'):
        'the read-back of a task on his own (§8.4)',
    ('backend/commands/parse_preview.py',
     '{} is not on his own — there is no task of his to change.'):
        'the read-back of a task on his own (§8.4)',
    ('backend/commands/parse_preview.py',
     '{} · on his own'):
        'the read-back of a task on his own (§8.4)',
    ('backend/commands/parse_preview.py',
     '{} · on his own: {}'):
        'the read-back of a task on his own (§8.4)',
    ('backend/commands/task_presets.py',
     'On his own: {} — his idea'):
        'his own proposal, offered on his card (§6.9)',
    ('backend/game_logic/dispatch.py',
     'On his own ({}) — asks for your word: {}.'):
        "the morning's status of a man on his own (§6.9)",
    ('backend/game_logic/dispatch.py',
     'On his own: {}.{}'):
        "the morning's status of a man on his own (§6.9)",
    ('backend/game_logic/jealousy.py',
     'He cannot be set on his own now: {}.'):
        "the petition's Give him a front: his proposal on the line, or why not (§6.9)",
    ('backend/game_logic/jealousy.py',
     '{} straightens. "You will not regret it, Sire." His own proposal is written on your command line — press Enter to set him on his own, or change it first.'):
        "the petition's Give him a front: his proposal on the line, or why not (§6.9)",
    ('backend/game_logic/own_order.py',
     'Setting {} on his own takes {} action{}; you have {}. Nothing was spent.'):
        'the module of a man on his own (§6)',
    ('backend/game_logic/own_order.py',
     'a task on his own is to take a place, chase an army, hold ground or support a friend'):
        'the module of a man on his own (§6)',
    ('backend/game_logic/own_order.py',
     'is on his own'):
        'the module of a man on his own (§6)',
    ('backend/game_logic/own_order.py',
     'only a bold or a careful marshal can be set on his own'):
        'the module of a man on his own (§6)',
    ('backend/game_logic/own_order.py',
     'set on his own while I stood by with no order'):
        'the module of a man on his own (§6)',
    ('backend/game_logic/own_order.py',
     '{} cannot be set on his own: {}.'):
        'the module of a man on his own (§6)',
    ('backend/game_logic/own_order.py',
     '{} follows orders to the letter — he takes exact orders, never a task on his own'):
        'the module of a man on his own (§6)',
    ('backend/game_logic/own_order.py',
     '{} is not on his own'):
        'the module of a man on his own (§6)',
    ('backend/game_logic/own_order.py',
     '{} is not on his own — set him on his own first.'):
        'the module of a man on his own (§6)',
    ('backend/game_logic/own_order.py',
     '{} is not on his own.'):
        'the module of a man on his own (§6)',
    ('backend/game_logic/own_order.py',
     "{}'s trust in you is {} — he needs {} to be trusted on his own"):
        'the module of a man on his own (§6)',
    ('backend/game_logic/reforms.py',
     '+{} marshal{} you may set on his own'):
        'the law effect that raises the count (§6.4)',
    ('backend/game_logic/today.py',
     'Set him on his own'):
        "the desk's rows of a man on his own (§4)",
    ('backend/game_logic/today.py',
     'You could set {} on his own.'):
        "the desk's rows of a man on his own (§4)",
    ('backend/game_logic/today.py',
     '{} is {} marches from you — you could set him on his own ({}).'):
        "the desk's rows of a man on his own (§4)",
    ('backend/game_logic/today.py',
     '{} is {} marches from you — you could set him on his own.'):
        "the desk's rows of a man on his own (§4)",
    ('backend/game_logic/today.py',
     '{}, on his own, asks for your word.'):
        "the desk's rows of a man on his own (§4)",
    ('backend/game_logic/today.py',
     '{}, on his own, asks for your word: {}.'):
        "the desk's rows of a man on his own (§4)",
    ('backend/game_logic/today.py',
     '{}, on his own, asks for your word: {}. Carry on (free), give him a new task, or stand him down (free).'):
        "the desk's rows of a man on his own (§4)",
    ('godot-client/project-sovereign/assets/maps/europe_1805.json',
     "Berthier's headquarters grown into a true general staff: one more order carried each day, and one more marshal you may set on his own."):
        'the laws that raise the count (§6.4)',
    ('godot-client/project-sovereign/assets/maps/europe_1805.json',
     'Officers who carry your intentions to distant commands: one more marshal you may set on his own. Needs the Grand Quartier Général.'):
        'the laws that raise the count (§6.4)',
    ('godot-client/project-sovereign/assets/maps/tutorial_1805.json',
     "Berthier's headquarters grown into a true general staff: one more order carried each day, and one more marshal you may set on his own."):
        "the School's copy of France's laws",
    ('godot-client/project-sovereign/assets/maps/tutorial_1805.json',
     'Officers who carry your intentions to distant commands: one more marshal you may set on his own. Needs the Grand Quartier Général.'):
        "the School's copy of France's laws",
    ('godot-client/project-sovereign/scripts/marshal_state.gd',
     'On his own'):
        'his badge (§12: a shape and a word)',
    ('godot-client/project-sovereign/scripts/marshal_state.gd',
     'On his own:'):
        'his badge (§12: a shape and a word)',
    ('godot-client/project-sovereign/scripts/selection_card.gd',
     'Ends his task on his own:'):
        'his card (§8.1, §8.6)',
    ('godot-client/project-sovereign/scripts/selection_card.gd',
     ']On his own:'):
        'his card (§8.1, §8.6)',
    ('godot-client/project-sovereign/scripts/turn_end_list.gd',
     'On his own. Press to go to him — to order it yourself, or to stand him down.'):
        "the End Turn list's Tonight rows (§5)",
    # Row IC, Session 3b (November 21, 2026): an army's task — its COMMANDER is a man
    # you set on his own; each string read and added by name, as above.
    ('backend/commands/army_task.py',
     'No man of the {} can be set on his own, Sire — {}. For the same words as a plain order to every corps, say “{}, {} by exact orders”.'):
        "an army's task: its commander is a man you set on his own (§9.1)",
    ('backend/commands/army_task.py',
     "No man of the {} can be set on his own — a task needs a bold or a careful marshal whose trust in you is 30 or more. Each man's reason is below."):
        "an army's task: its commander is a man you set on his own (§9.1)",
    ('backend/commands/army_task.py',
     'on his own: {} — not included'):
        "an army's task: its commander is a man you set on his own (§9.1)",
    ('backend/commands/army_task.py',
     'on his own: {} — he keeps that task as his own, and commands the {} no longer'):
        "an army's task: its commander is a man you set on his own (§9.1)",
    ('backend/commands/army_task.py',
     'No man of the {} can be set on his own'):
        "an army's task: its commander is a man you set on his own (§9.1)",
    ('backend/commands/army_task.py',
     'on his own: {}'):
        "an army's task: its commander is a man you set on his own (§9.1)",
    ('backend/commands/army_task.py',
     '{} commands — {}; he is set on his own ({})'):
        "an army's task: its commander is a man you set on his own (§9.1)",
    ('backend/commands/army_task.py',
     'cannot be set on his own'):
        "an army's task: its commander is a man you set on his own (§9.1)",
    ('backend/commands/army_task.py',
     'The same words as an ordinary order for every corps — nobody is set on his own.'):
        "an army's task: its commander is a man you set on his own (§9.1)",
    ('backend/commands/army_task.py',
     'on his own:'):
        "an army's task: its commander is a man you set on his own (§9.1)",
    ('backend/commands/army_task.py',
     'is on his own already'):
        "an army's task: its commander is a man you set on his own (§9.1)",
    ('backend/commands/army_task.py',
     'the highest-ranked of its men who can be set on his own'):
        "an army's task: its commander is a man you set on his own (§9.1)",
    ('backend/commands/army_task.py',
     'would command — but no place is free for another man on his own'):
        "an army's task: its commander is a man you set on his own (§9.1)",
    ('backend/commands/army_task.py',
     'He takes your one place for a man on his own.'):
        "an army's task: its commander is a man you set on his own (§9.1)",
    ('backend/commands/group_orders.py',
     '{} commands, on his own'):
        "the reply to an army's task given (§9.1)",
    ('backend/game_logic/armies.py',
     '{} commands {}. When you give the army a task (“{}, take …”), he is the one set on his own, and the others follow him.'):
        "naming an army's commander — the man set on his own by its task (§9.1)",
    ('backend/game_logic/armies.py',
     '{} no longer commands {} — when it is given a task, the highest-ranked of its men who can be set on his own commands.'):
        "naming an army's commander — the man set on his own by its task (§9.1)",
    ('backend/game_logic/armies.py',
     'Nobody is named to command {} — when it is given a task, the highest-ranked of its men who can be set on his own commands.'):
        "naming an army's commander — the man set on his own by its task (§9.1)",
    ('backend/game_logic/own_order.py',
     "{}'s task on his own is over: {}.{}"):
        'the module of a man on his own (§6)',
    ('godot-client/project-sovereign/scripts/marshal_chip_row.gd',
     'The %s is on its own: %s. %s commands, on his own; %s.'):
        "the army's chip, of its commander (§9.1)",
    ('godot-client/project-sovereign/scripts/order_confirm_card.gd',
     'goes on his own; nobody follows him yet.'):
        "the list of an army's task, of its commander (§9.1)",
    ('godot-client/project-sovereign/scripts/order_confirm_card.gd',
     'on his own,'):
        "the list of an army's task, of its commander (§9.1)",
    ('godot-client/project-sovereign/scripts/selection_card.gd',
     ', take …”). Its commander is set on his own and the others follow him.'):
        'his card (§8.1, §8.6)',
}

# (4) ONE-WORD labels of the vassals' scale (read since the review widened the
# census to a label standing alone) — exempt only as the WHOLE string:
EXEMPT_LABELS = {
    ("backend/game_logic/settlement_ratify.py", "Autonomous"):
        "the scale's third level, named in a treaty's clause (Puppet / Satellite / Autonomous)",
    ("godot-client/project-sovereign/scripts/codex_terms.gd", "Autonomy"):
        "the Help's entry for the scale — 'How much freedom a vassal keeps'",
}


def _python_prose(path: Path):
    """Every string of the file that is no docstring. An f-string is read
    WHOLE — its pieces joined around a `{}` for each value — so that a word
    standing alone beside a value (f"{name} autonomous") is seen as the prose
    it is (the review: a one-word piece read as an identifier and was
    skipped)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(getattr(body[0], "value", None), ast.Constant)
                    and isinstance(body[0].value.value, str)):
                docstrings.add(id(body[0].value))
    pieces = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            parts = []
            for value in node.values:
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    parts.append(value.value)
                    pieces.add(id(value))
                else:
                    parts.append("{}")
            yield node.lineno, "".join(parts)
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and id(node) not in docstrings and id(node) not in pieces):
            yield node.lineno, node.value


def _gdscript_prose(text: str):
    """Every string of a client script: double- AND single-quoted, and a
    triple-quoted block that is DATA (assigned or passed — read whole, across
    its lines). A statement-level triple-quoted block is a docstring and a
    `#` outside a string starts a comment: neither is a player's words."""
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        number = i + 1
        stripped = line.lstrip()
        if stripped.startswith('"""') or stripped.startswith("\'\'\'"):
            mark, rest = stripped[:3], stripped[3:]
            while mark not in rest:
                i += 1
                if i >= len(lines):
                    return
                rest = lines[i]
            i += 1
            continue
        j = 0
        while j < len(line):
            ch = line[j]
            if ch == "#":
                break
            if line.startswith('"""', j) or line.startswith("\'\'\'", j):
                mark, body, k, row = line[j:j + 3], [], j + 3, i
                while True:
                    end = lines[row].find(mark, k)
                    if end >= 0:
                        body.append(lines[row][k:end])
                        break
                    body.append(lines[row][k:])
                    row, k = row + 1, 0
                    if row >= len(lines):
                        yield number, "\n".join(body)
                        return
                yield number, "\n".join(body)
                i, line, j = row, lines[row], end + 3
                continue
            if ch in "\"\'":
                k, body = j + 1, []
                while k < len(line) and line[k] != ch:
                    if line[k] == "\\" and k + 1 < len(line):
                        body.append(line[k:k + 2])
                        k += 2
                        continue
                    body.append(line[k])
                    k += 1
                yield number, "".join(body)
                j = k + 1
                continue
            j += 1
        i += 1


_SCENE_TEXT = re.compile(
    r'^[ \t]*(?:text|tooltip_text|placeholder_text|title)[ \t]*=[ \t]*"((?:[^"\\]|\\.)*)"', re.M)


def _scene_prose(text: str):
    """The texts a scene sets — a value may run over several lines."""
    for match in _SCENE_TEXT.finditer(text):
        yield text.count("\n", 0, match.start()) + 1, match.group(1)


def _data_prose(node):
    """Every string VALUE of an authored data file (a scenario's letters,
    its laws' lines) — keys are the code's own and are not read."""
    if isinstance(node, dict):
        for value in node.values():
            yield from _data_prose(value)
    elif isinstance(node, list):
        for value in node:
            yield from _data_prose(value)
    elif isinstance(node, str):
        yield node


def _all_prose():
    for path in sorted((REPO / "backend").rglob("*.py")):
        rel = path.relative_to(REPO).as_posix()
        for number, value in _python_prose(path):
            yield rel, number, value
    # every script of the client — `scripts/` AND the scene scripts beside
    # the scenes (`scenes/*.gd`: the map, its badges, the war table's pieces)
    for path in sorted(p for p in CLIENT.rglob("*.gd")
                       if not {".godot", "addons"} & set(p.relative_to(CLIENT).parts)):
        rel = path.relative_to(REPO).as_posix()
        for number, value in _gdscript_prose(path.read_text(encoding="utf-8", errors="replace")):
            yield rel, number, value
    for path in sorted((CLIENT / "scenes").rglob("*.tscn")):
        rel = path.relative_to(REPO).as_posix()
        for number, value in _scene_prose(path.read_text(encoding="utf-8", errors="replace")):
            yield rel, number, value
    # the authored data the game shows as written: the scenarios (the review —
    # their letters and laws were read by nobody)
    for path in sorted((CLIENT / "assets" / "maps").glob("*.json")):
        rel = path.relative_to(REPO).as_posix()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            continue
        for value in _data_prose(data):
            yield rel, 0, value


def _is_prose(value: str) -> bool:
    """A string a player could read: more than one word — or ONE word written
    as a label (a capital and no underscore: "Autonomy", "AUTONOMOUS"), which
    an identifier never is ("autonomous", "grant_autonomy")."""
    text = value.strip()
    if " " in text:
        return True
    return bool(text) and "_" not in text and text != text.lower()


def _census(rows):
    """`(file, line, word, the string's own line)` for every string of prose
    that carries one of the census's words and is exempt by no name."""
    found = []
    for rel, number, value in rows:
        if not _is_prose(value):
            continue                                    # an identifier, never prose
        for part in value.split("\n"):
            for word, pattern in WORDS.items():
                if not pattern.search(part):
                    continue
                if any(rel == file and phrase in part for (file, phrase) in EXEMPT_BY_NAME):
                    continue
                if (rel, part.strip()) in EXEMPT_LABELS:
                    continue
                if word == "on his own" and (rel, " ".join(part.split())) in SET_BY_YOU:
                    continue
                if word == "autonomy" and (rel in VASSAL_SCALE_FILES
                                           or VASSAL_SCALE_NAMES.search(part)):
                    continue
                found.append((rel, number, word, " ".join(part.split())[:160]))
    return found


class TestTheWordsCensus:

    def test_the_census_reads_what_it_says_it_reads(self):
        """Not vacuous: the three readers see prose, skip what is no prose,
        and a planted line of each kind is caught."""
        rows = list(_all_prose())
        files = {rel for rel, _n, _v in rows}
        assert len(files) > 250, len(files)
        for needed in ("backend/game_logic/trial.py", "backend/game_logic/jealousy.py",
                       "godot-client/project-sovereign/scenes/map_renderer_base.gd",
                       "godot-client/project-sovereign/scripts/redemption_dialog.gd",
                       "godot-client/project-sovereign/scripts/marshal_management.gd",
                       "godot-client/project-sovereign/scenes/redemption_dialog.tscn"):
            assert needed in files, needed
        planted = [
            ("backend/x.py", 1, "Grant Autonomy"),
            ("backend/x.py", 2, "Ney acts independently for 3 turns."),
            ("backend/x.py", 3, "He acts on his own for 2 more turns."),
            ("godot-client/project-sovereign/scripts/x.gd", 4, "INDEPENDENT COMMAND REPORT"),
            ("backend/x.py", 5, "autonomous"),                         # an identifier: no prose
            ("backend/x.py", 9, "grant_autonomy"),                     # ... a key: no prose
            ("backend/x.py", 10, "AUTONOMOUS"),                        # a LABEL standing alone: prose
            ("backend/x.py", 11, "{} autonomous"),                     # an f-string read whole
            ("backend/game_logic/settlement_ratify.py", 12, "Autonomous"),   # the scale's own label
            ("backend/game_logic/settlement_ratify.py", 13, "Autonomous marshals"),  # ... only whole
            ("backend/x.py", 6, "The puppet may be given more autonomy."),   # the vassal scale
            ("backend/game_logic/vassal.py", 7, "Increase Autonomy"),         # ... by file
            ("backend/game_logic/vassal.py", 8, "He acts on his own tonight."),  # only "autonomy" is exempt there
        ]
        caught = [(rel, number, word) for rel, number, word, _line in _census(planted)]
        assert caught == [
            ("backend/x.py", 1, "autonomy"),
            ("backend/x.py", 2, "independent command"),
            ("backend/x.py", 3, "on his own"),
            ("godot-client/project-sovereign/scripts/x.gd", 4, "independent command"),
            ("backend/x.py", 10, "autonomy"),
            ("backend/x.py", 11, "autonomy"),
            ("backend/game_logic/settlement_ratify.py", 13, "autonomy"),
            ("backend/game_logic/vassal.py", 8, "on his own"),
        ]
        # the readers themselves (the review: what they could not see)
        assert list(_gdscript_prose("var a = 'one two'  # 'no'\nvar b = \"it's fine\"")) == [
            (1, "one two"), (2, "it's fine")]
        block = 'func f():\n\t"""A docstring, on his own."""\n\tvar t = """two\nlines"""'
        assert list(_gdscript_prose(block)) == [(3, "two\nlines")]
        assert list(_scene_prose('text = "two\nlines"\nname = "x"')) == [(1, "two\nlines")]
        assert sorted(_data_prose({"says": "whatever its autonomy", "n": 3, "rows": ["a b", {"k": "c d"}]})) == [
            "a b", "c d", "whatever its autonomy"]
        assert list(_gdscript_prose('var a = "one two"  # "a comment" here\nvar b = "x # y z"')) == [
            (1, "one two"), (2, "x # y z")]
        assert list(_scene_prose('text = "Give him a task"\nname = "No Prose Here"')) == [
            (1, "Give him a task")]

    def test_no_marshals_screen_says_autonomy_independent_command_or_on_his_own(self):
        found = _census(_all_prose())
        assert not found, "\n".join(f"{rel}:{number}  [{word}]  {line}"
                                    for rel, number, word, line in found)

    def test_every_exemption_names_a_string_that_is_there(self):
        """An exemption that names nothing is a hole waiting for a string."""
        texts = {}
        for (rel, phrase), reason in EXEMPT_BY_NAME.items():
            assert reason, (rel, phrase)
            text = texts.setdefault(rel, (REPO / rel).read_text(encoding="utf-8"))
            assert phrase in text, f"{rel} no longer says {phrase!r} — drop the exemption"
        # row IC, Session 3: each string of a man you set is still read where it is taught
        prose = {}
        for rel_p, _n, value in _all_prose():
            for part in str(value).split("\n"):
                prose.setdefault(rel_p, set()).add(" ".join(part.split()))
        for (rel, text), reason in SET_BY_YOU.items():
            assert reason and text in prose.get(rel, set()), f"{rel} no longer says {text!r} — drop it"
        for (rel, label), reason in EXEMPT_LABELS.items():
            assert reason and f'"{label}"' in (REPO / rel).read_text(encoding="utf-8"), (rel, label)
        for rel in VASSAL_SCALE_FILES:
            assert (REPO / rel).is_file(), rel
            assert re.search(r"autonom", (REPO / rel).read_text(encoding="utf-8"), re.I), rel

    def test_the_jealous_strike_says_without_waiting_for_orders(self):
        from backend.game_logic import jealousy as J
        said = " ".join(value for _line, value in
                        _python_prose(REPO / "backend" / "game_logic" / "jealousy.py"))
        assert said.count("without waiting for orders") >= 2
        assert "on his own initiative" not in said
        today = (REPO / "backend" / "game_logic" / "today.py").read_text(encoding="utf-8")
        assert "may attack without waiting for orders when the turn ends" in today
        for script, needed in (("marshal_management.gd", "HE MAY ATTACK WITHOUT WAITING FOR ORDERS"),
                               ("tutorial_overlay.gd", "may even attack without waiting for orders."),
                               ("codex_terms.gd", "may attack without waiting for orders.")):
            text = (CLIENT / "scripts" / script).read_text(encoding="utf-8", errors="replace")
            assert needed in text, (script, needed)
        assert J.on_his_task is not None and not hasattr(J, "acts_independently")

    def test_a_refused_order_says_refused_your_order(self):
        for rel in ("backend/commands/strategic_executor.py", "backend/commands/meta_executor.py"):
            said = " ".join(value for _line, value in _python_prose(REPO / rel))
            assert "refused your order!" in said and "refused your order to " in said, rel
            assert "defied your order" not in said, rel
        defiance = (REPO / "backend" / "commands" / "defiance.py").read_text(encoding="utf-8")
        assert "{marshal} refused your order... and then stood idle." in defiance

    def test_the_audience_and_the_cards_name_the_task(self):
        scene = (CLIENT / "scenes" / "redemption_dialog.tscn").read_text(encoding="utf-8")
        assert 'text = "Give him a task to prove himself"' in scene
        assert "AutonomyButton" not in scene and "TrialButton" in scene and "ProposalLabel" in scene
        dialog = (CLIENT / "scripts" / "redemption_dialog.gd").read_text(encoding="utf-8")
        assert 'choice_made.emit("trial")' in dialog and "grant_autonomy" not in dialog
        main = (CLIENT / "scripts" / "main.gd").read_text(encoding="utf-8", errors="replace")
        assert "A TASK TO PROVE HIMSELF" in main and "AUTONOMY GRANTED" not in main
        state = (CLIENT / "scripts" / "marshal_state.gd").read_text(encoding="utf-8")
        assert '"proving"' in state
