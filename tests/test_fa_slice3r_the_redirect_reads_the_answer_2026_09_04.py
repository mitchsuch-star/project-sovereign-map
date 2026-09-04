"""Final Whole-Game Audit — slice 3 REVIEW ROUND, "The Redirect Reads the
Answer".

Three review lenses attacked slice 3 ("The Order Tells the Truth",
19fba926) at master 16921a6b and found the predicate it built was not read
everywhere an order-driven attack is made, and that two of the seams it did
fix still dropped what the battle carried:

* the cannon-fire REDIRECT cleared the order BEFORE its attack and narrated
  whatever came back — a refused attack destroyed a live order for nothing,
  and, with `in_strategic_mode` False during the attack, a recklessness-3
  cavalryman armed a CHARGE popup the end-turn wire cannot carry (R1-F1/F2,
  R2-F3); the `investigate` answer had the same shape;
* a STALE contact answered `attack` reached the executor's attack-to-pursue
  upgrade: a PURSUE minted, a province marched at 0 AP, the order logged and
  then deleted as "Assault failed" (R1-F3); a contact answered after a peace
  staged the war-purpose HARD STOP wearing a battle sentence (R1-F4); and
  the answered stalemate CANCELLED where `continue_order` keeps (R2-F4);
* the two PURSUE first-step arms replied with the generic order dict —
  events, report, tableau and the CAPTURE PROMPT dropped (R2-F1);
* a HARD STOP staged by an END-TURN battle reached the wire only inside a
  report row's `battle_details`, which no renderer reads (R2-F2);
* the attack-on-arrival arm was a THIRTEENTH order-driven seam, unread and
  mis-filed by the slice's own census as an "answer arm" (R3-S1);
* plus: the destination copy after a stalemate, the phantom log row a
  refused first step left, the client's interrupt-queue drain hole, the
  headless driver answering one question per response, and the row's
  tableau built and discarded.

Every fix sits behind one of two levers (`CANNON_FIRE_READS_THE_ANSWER`,
`ANSWERED_CONTACT_READS_THE_BOARD`) or is structural and player-only;
`BASELINE_SERIES` and M1-M7 are byte-identical by construction (the
processor's roster is the player's, the executor's guard keys on
`_strategic_execution`, which the AI never carries).
"""

import contextlib
import io
import os
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import strategic as strategic_mod
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser
from backend.commands.strategic import (
    StrategicOrderProcessor,
    _combat_carry,
    contact_is_live,
    fought_battle_victor,
    retract_order_log,
)
from backend.models.marshal import StrategicOrder
from backend.models.world_state import WorldState
from tests.test_fa_slice2_no_word_came_2026_09_04 import _war

REPO = Path(__file__).resolve().parents[1]
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
               / "europe_1805.json")


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _order(command_type, target, **kw):
    return StrategicOrder(command_type=command_type, target=target,
                          target_type=kw.pop("target_type", "region"),
                          started_turn=0, issued_turn=0, path=kw.pop("path", []),
                          original_command=f"x, {command_type} {target}", **kw)


def _legacy():
    """Britain vs France on the 19-region fixture; the French roster at
    Bordeaux, Wellington at Belgium (adjacent to Paris)."""
    world = WorldState(player_nation="Britain")
    _war(world, "France", "Britain")
    for m in world.marshals.values():
        if m.nation == "France":
            m.location = "Bordeaux"
    wel = world.marshals["Wellington"]
    wel.location = "Belgium"
    wel.strength = 30000
    wel.fortified = False
    world.invalidate_active_nations_cache()
    world._build_marshal_index()
    world.calculate_visibility()
    return world, wel


def _channel():
    """The shipped board: Ney at Normandy, Moore at London, the Royal Navy
    commanding the water — the executor REFUSES the attack."""
    with _quiet():
        world = WorldState.from_scenario(SCENARIO)
    ney = world.get_marshal("Ney")
    moore = world.get_marshal("Moore")
    ney.location = "Normandy"
    moore.location = "London"
    moore.strength = 20000
    world.invalidate_active_nations_cache()
    world._build_marshal_index()
    world.calculate_visibility()
    return world, ney, moore


def _refusing(executor, message="his guns are not set up"):
    real = executor.execute

    def refuse(command, game_state):
        if command.get("command", {}).get("action") == "attack":
            return {"success": False, "message": message}
        return real(command, game_state)
    executor.execute = refuse
    return executor


def _stubbed(executor, result):
    executor.execute = lambda command, game_state: dict(result)
    return executor


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


# ═══════════════════════════════════════════════════════════════════════
# The redirect reads the answer (R1-F1/F2, R2-F3)
# ═══════════════════════════════════════════════════════════════════════

class TestTheRedirectReadsTheAnswer:

    def _redirect(self, proc, marshal, world, battle_loc):
        with _quiet():
            return proc._handle_interrupt(
                marshal, {"type": "cannon_fire", "action": "redirect",
                          "battle_location": battle_loc},
                world, {"world": world})

    def test_a_refused_attack_leaves_the_order_standing(self):
        world, ney, moore = _channel()
        ney.strategic_order = _order("MOVE_TO", "Paris", path=["Paris"])
        proc = StrategicOrderProcessor(CommandExecutor())
        row = self._redirect(proc, ney, world, "London")
        assert row["order_status"] == "continues", row
        assert row["action_taken"] == "attack_refused"
        assert "cannot answer it" in row["message"] and "continues" in row["message"]
        assert row.get("blocked_naval") == "Britain"
        assert ney.strategic_order is not None, "a refused redirect destroyed the order"
        assert ney.location == "Normandy"
        assert not getattr(world, "battles_this_turn", None)

    def test_a_fought_redirect_abandons_the_order_and_carries_the_battle(self):
        world, wel = _legacy()
        ney = world.marshals["Ney"]
        ney.location = "Paris"
        ney.strength = 5000
        world._build_marshal_index()
        world.calculate_visibility()
        wel.strategic_order = _order("MOVE_TO", "Netherlands", path=["Netherlands"])
        proc = StrategicOrderProcessor(CommandExecutor())
        row = self._redirect(proc, wel, world, "Paris")
        assert row["order_status"] == "interrupted", row
        assert row["action_taken"] == "attack" and row["action_success"] is True
        assert wel.strategic_order is None, "a fought redirect is a real abandonment"
        assert row.get("battle_message"), "R2-F3: the fighting redirect carried no report"
        assert row.get("battle_report") is not None or row.get("battle_details") is not None

    def test_a_reckless_cavalryman_never_arms_the_charge_popup(self):
        """R1-F2: with the order cleared first, `in_strategic_mode` was False
        during the attack and the recklessness-3 popup armed — a question
        the end-turn wire cannot carry, then a 2x charge from a bare
        `charge` (WO-25's shape)."""
        world, wel = _legacy()
        ney = world.marshals["Ney"]           # France's cavalry on this fixture
        assert getattr(ney, "cavalry", False)
        ney.location = "Paris"
        ney.strength = 30000
        ney.recklessness = 3
        ney.personality = "aggressive"
        ney.strategic_order = _order("MOVE_TO", "Lyon", path=["Lyon"])
        wel.location = "Belgium"
        wel.strength = 20000
        world.player_nation = "France"
        world.invalidate_active_nations_cache()
        world._build_marshal_index()
        world.calculate_visibility()
        proc = StrategicOrderProcessor(CommandExecutor())
        row = self._redirect(proc, ney, world, "Belgium")
        assert not getattr(ney, "pending_glorious_charge", False), row
        assert row["order_status"] in ("interrupted", "continues"), row
        if row["order_status"] == "interrupted":
            assert ney.strategic_order is None
        else:
            assert ney.strategic_order is not None

    def test_the_lever_down_destroys_the_order_on_a_refusal(self, monkeypatch):
        monkeypatch.setattr(strategic_mod, "CANNON_FIRE_READS_THE_ANSWER", False)
        world, ney, moore = _channel()
        ney.strategic_order = _order("MOVE_TO", "Paris", path=["Paris"])
        proc = StrategicOrderProcessor(CommandExecutor())
        row = self._redirect(proc, ney, world, "London")
        assert row["order_status"] == "interrupted"
        assert ney.strategic_order is None, "the defect, reproduced"
        assert "Abandoning orders" in row["message"]


class TestTheInvestigateAnswerReadsTheAnswer:

    def _answer(self, proc, marshal, world, battle_loc):
        pending = {"interrupt_type": "cannon_fire", "battle_location": battle_loc,
                   "options": ["investigate", "continue_order", "hold_position"]}
        with _quiet():
            return proc._respond_cannon_fire(marshal, marshal.strategic_order,
                                             "investigate", pending, world, {"world": world})

    def test_a_refused_charge_keeps_the_order(self):
        world, ney, moore = _channel()
        ney.strategic_order = _order("MOVE_TO", "Paris", path=["Paris"])
        proc = StrategicOrderProcessor(CommandExecutor())
        reply = self._answer(proc, ney, world, "London")
        assert reply["success"] is True and reply["order_cleared"] is False, reply
        assert reply["action_taken"] == "attack_refused"
        assert "cannot reach the guns" in reply["message"]
        assert ney.strategic_order is not None

    def test_a_fought_charge_abandons_the_order_and_carries_the_battle(self):
        world, wel = _legacy()
        ney = world.marshals["Ney"]
        ney.location = "Paris"
        ney.strength = 5000
        world._build_marshal_index()
        world.calculate_visibility()
        wel.strategic_order = _order("MOVE_TO", "Netherlands", path=["Netherlands"])
        proc = StrategicOrderProcessor(CommandExecutor())
        reply = self._answer(proc, wel, world, "Paris")
        assert reply["order_cleared"] is True and reply["action_taken"] == "attack"
        assert wel.strategic_order is None
        assert reply.get("events"), "R2-F1's class: the answer must carry the battle"

    def test_no_step_possible_keeps_the_order(self):
        """Too far to attack and every step blocked: the order stands."""
        world, wel = _legacy()
        wel.strategic_order = _order("MOVE_TO", "Netherlands", path=["Netherlands"])
        proc = StrategicOrderProcessor(CommandExecutor())
        proc.executor.execute = lambda c, g: {"success": False, "message": "the road is barred"}
        reply = self._answer(proc, wel, world, "Bordeaux")   # two hops off
        assert reply["order_cleared"] is False, reply
        assert reply["action_taken"] == "investigate_refused"
        assert wel.strategic_order is not None


# ═══════════════════════════════════════════════════════════════════════
# The answered contact reads the board (R1-F3/F4, R2-F4)
# ═══════════════════════════════════════════════════════════════════════

def _davout_contact(enemy_location="Nassau"):
    """Davout at Rhineland under MOVE_TO Munich, a pending contact on Mack
    'at Nassau'; Mack now at `enemy_location`."""
    with _quiet():
        world = WorldState.from_scenario(SCENARIO)
    davout = world.get_marshal("Davout")
    mack = world.get_marshal("Mack")
    davout.location = "Rhineland"
    davout.strategic_order = _order("MOVE_TO", "Munich", path=["Nassau", "Munich"])
    mack.location = enemy_location
    mack.strength = 30000
    world.invalidate_active_nations_cache()
    world._build_marshal_index()
    world.calculate_visibility()
    pending = {"interrupt_type": "contact", "enemy": "Mack", "location": "Nassau",
               "options": ["attack", "go_around", "hold_position", "cancel_order"]}
    return world, davout, mack, pending


class TestTheAnsweredContactReadsTheBoard:

    def _answer(self, proc, marshal, world, pending, choice="attack"):
        with _quiet():
            return proc._respond_blocked_path(marshal, marshal.strategic_order, choice,
                                              pending, world, {"world": world})

    def test_a_contact_whose_man_marched_off_is_retired_not_fought(self):
        world, davout, mack, pending = _davout_contact(enemy_location="Flanders")
        ap = world.actions_remaining
        log_before = len(world.event_log)
        proc = StrategicOrderProcessor(CommandExecutor())
        reply = self._answer(proc, davout, world, pending)
        assert reply.get("decision_retired") is True, reply
        assert reply["order_cleared"] is False and davout.strategic_order is not None
        assert davout.strategic_order.command_type == "MOVE_TO", "no PURSUE was minted"
        assert davout.location == "Rhineland", "nobody marched"
        assert world.actions_remaining == ap
        assert len(world.event_log) == log_before, "no order was logged"
        assert "overtaken" in reply["message"]

    def test_a_contact_after_a_peace_is_retired_not_staged(self):
        world, davout, mack, pending = _davout_contact()
        world.diplomatic_states["Austria|France"] = "PEACE"
        world.invalidate_active_nations_cache()
        proc = StrategicOrderProcessor(CommandExecutor())
        reply = self._answer(proc, davout, world, pending)
        assert reply.get("decision_retired") is True, reply
        assert "no longer at war" in reply["message"]
        assert not world.pending_diplomatic_dialogue, "a HARD STOP was staged by a retired question"
        assert davout.strategic_order is not None

    def test_the_predicates(self):
        world, davout, mack, pending = _davout_contact()
        assert contact_is_live(davout, world, pending) == (True, "")
        mack.strength = 0
        assert contact_is_live(davout, world, pending)[0] is False
        assert fought_battle_victor({"success": True, "message": "x"}, "Davout") is None
        assert fought_battle_victor({"events": [{"type": "battle", "victor": "Davout"}]}, "Davout") == "Davout"
        assert fought_battle_victor({"events": [{"type": "battle", "victor": ""}]}, "Davout") == ""
        assert fought_battle_victor({"events": [{"type": "glorious_charge", "attacker_won": True}]}, "Davout") == "Davout"
        assert fought_battle_victor({"success": False, "message": "refused"}, "Davout") is None

    def test_a_stalemate_keeps_the_order_and_a_defeat_breaks_it(self):
        world, davout, mack, pending = _davout_contact()
        proc = StrategicOrderProcessor(CommandExecutor())
        _stubbed(proc.executor, {"success": True, "message": "inconclusive",
                                 "events": [{"type": "battle", "victor": ""}]})
        reply = self._answer(proc, davout, world, pending)
        assert reply["order_cleared"] is False and davout.strategic_order is not None, reply
        assert davout.strategic_order.combat_attempts == 1
        assert "inconclusive" in reply["message"] and "continues" in reply["message"]
        _stubbed(proc.executor, {"success": False, "message": "routed",
                                 "events": [{"type": "battle", "victor": "Mack"}]})
        reply = self._answer(proc, davout, world, pending)
        assert reply["order_cleared"] is True and davout.strategic_order is None

    def test_a_success_with_no_battle_is_not_an_assault(self):
        world, davout, mack, pending = _davout_contact()
        proc = StrategicOrderProcessor(CommandExecutor())
        _stubbed(proc.executor, {"success": True, "strategic_order": True,
                                 "message": "Davout pursues Mack."})
        reply = self._answer(proc, davout, world, pending)
        assert reply["action_taken"] == "attack_not_made", reply
        assert reply["order_cleared"] is False and davout.strategic_order is not None
        assert davout.strategic_order.combat_attempts == 0
        assert "Assault failed" not in reply["message"]

    def test_the_executor_never_mints_a_pursuit_under_strategic_execution(self):
        """R1-F3(ii): the attack-to-pursue upgrade, reached through the
        answer, minted and marched. An order-driven attack that finds its
        man out of reach is a refusal."""
        world, davout, mack, pending = _davout_contact(enemy_location="Flanders")
        ap = world.actions_remaining
        log_before = len(world.event_log)
        with _quiet():
            result = CommandExecutor().execute(
                {"command": {"marshal": "Davout", "action": "attack", "target": "Mack",
                             "_strategic_execution": True}}, {"world": world})
        assert result["success"] is False and result.get("out_of_reach") is True, result
        assert davout.strategic_order.command_type == "MOVE_TO"
        assert davout.location == "Rhineland"
        assert world.actions_remaining == ap
        assert len(world.event_log) == log_before

    def test_the_typed_attack_still_upgrades(self):
        """The player's own out-of-range `attack <marshal>` keeps its
        pursuit (the upgrade is the typed route's feature)."""
        world, davout, mack, pending = _davout_contact(enemy_location="Flanders")
        davout.strategic_order = None
        with _quiet():
            result = CommandExecutor().execute(
                {"command": {"marshal": "Davout", "action": "attack", "target": "Mack"}},
                {"world": world})
        assert result.get("strategic_order") is True or result.get("strategic_type") == "PURSUE", result

    def test_the_lever_down_mints_and_marches(self, monkeypatch):
        monkeypatch.setattr(strategic_mod, "ANSWERED_CONTACT_READS_THE_BOARD", False)
        world, davout, mack, pending = _davout_contact(enemy_location="Flanders")
        proc = StrategicOrderProcessor(CommandExecutor())
        reply = self._answer(proc, davout, world, pending)
        assert davout.location != "Rhineland" or "pursues" in reply["message"], \
            "the defect: the stale answer marched through the upgrade"


# ═══════════════════════════════════════════════════════════════════════
# The thirteenth seam (R3-S1) and the filed form at the seam (R3-S2)
# ═══════════════════════════════════════════════════════════════════════

class TestTheArrivalArmReadsTheAnswer:

    def _arrival(self, world, wel):
        wel.strategic_order = _order("MOVE_TO", "Belgium", path=[], attack_on_arrival=True)
        ney = world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 5000
        world._build_marshal_index()
        world.calculate_visibility()
        return ney

    def test_a_refused_attack_on_arrival_breaks_the_order_honestly(self):
        world, wel = _legacy()
        self._arrival(world, wel)
        proc = StrategicOrderProcessor(_refusing(CommandExecutor()))
        with _quiet():
            row = proc._handle_move_to_arrival(wel, world, {"world": world})
        assert row["action"] == "attack_refused", row
        assert "and attacks" not in row["message"]
        assert "guns are not set up" in row["message"]
        assert wel.strategic_order is None

    def test_a_fought_arrival_completes_and_carries_the_battle(self):
        world, wel = _legacy()
        self._arrival(world, wel)
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            row = proc._handle_move_to_arrival(wel, world, {"world": world})
        assert row["action"] == "attack_on_arrival" and row["order_status"] == "completed", row
        assert row.get("battle_message"), "the row must carry the battle it reports"


class TestTheFiledFormIsPinnedAtTheSeam:

    def test_an_event_only_victory_is_not_a_refusal(self):
        """R3-S2: the FA-N3 fixtures carry no `success` key; the filed
        `not result.get('success')` at this seam would read them as
        refusals. Pinned AT the seam, not only at the predicate."""
        world, wel = _legacy()
        wel.strategic_order = _order("MOVE_TO", "Paris", path=["Paris"])
        ney = world.marshals["Ney"]
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            row = proc._handle_combat_result(
                wel, ney, {"events": [{"type": "battle", "victor": "Wellington"}],
                           "message": "Wellington defeats Ney"},
                world, {"world": world})
        assert row.get("action") != "attack_refused", row
        assert wel.strategic_order is not None


# ═══════════════════════════════════════════════════════════════════════
# What the first step and the row carry (R2-F1/F2/F7)
# ═══════════════════════════════════════════════════════════════════════

class TestThePursueFirstStepCarriesTheBattle:

    def test_a_co_located_pursue_replies_with_the_battle(self):
        world, wel = _legacy()
        wel.personality = "aggressive"    # the first-step arms strike for an aggressive man
        ney = world.marshals["Ney"]
        ney.location = "Belgium"          # co-located at order creation
        ney.strength = 5000
        world._build_marshal_index()
        world.calculate_visibility()
        parsed = {"is_strategic": True, "strategic_type": "PURSUE", "target": "Ney",
                  "marshal": "Wellington", "action": "attack",
                  "original_command": "Wellington, pursue Ney"}
        with _quiet():
            reply = CommandExecutor()._strategic._execute_strategic_command(
                parsed, {"marshal": "Wellington", "action": "attack", "target": "Ney"},
                {"world": world})
        assert reply["success"] is True and "Engaging" in reply["message"], reply
        assert reply.get("events"), "R2-F1: the first-step battle was dropped from the reply"
        assert any(e.get("type") in ("battle", "conquest", "glorious_charge")
                   for e in reply["events"])

    def test_an_adjacent_pursue_replies_with_the_battle(self):
        world, wel = _legacy()
        wel.personality = "aggressive"    # the first-step arms strike for an aggressive man
        ney = world.marshals["Ney"]
        ney.location = "Paris"            # one march off: the move-failed-at-target arm
        ney.strength = 5000
        world._build_marshal_index()
        world.calculate_visibility()
        parsed = {"is_strategic": True, "strategic_type": "PURSUE", "target": "Ney",
                  "marshal": "Wellington", "action": "attack",
                  "original_command": "Wellington, pursue Ney"}
        with _quiet():
            reply = CommandExecutor()._strategic._execute_strategic_command(
                parsed, {"marshal": "Wellington", "action": "attack", "target": "Ney"},
                {"world": world})
        assert reply["success"] is True, reply
        if "Engaging" in reply["message"]:
            assert reply.get("events"), "R2-F1: the first-step battle was dropped from the reply"


class TestTheRowCarriesWhatTheClientReads:

    def test_combat_carry_lifts_the_tableau_and_the_triad(self):
        carry = _combat_carry({"success": True, "message": "m", "new_state": object(),
                               "battle_diorama": {"significant": True},
                               "diplomatic_dialogue": {"type": "war_purpose_selection"},
                               "awaiting_diplomatic_response": True,
                               "war_purpose_popup": {"x": 1}})
        assert carry["battle_diorama"] == {"significant": True}
        assert carry["diplomatic_dialogue"]["type"] == "war_purpose_selection"
        assert carry["awaiting_diplomatic_response"] is True
        assert carry["war_purpose_popup"] == {"x": 1}
        assert "new_state" not in carry["battle_details"]

    def test_the_end_turn_response_carries_the_deferred_hard_stop(self):
        with _quiet():
            world = WorldState.from_scenario(SCENARIO)
        world.dialogue_manager.push({"type": "war_purpose_selection", "nation": "Prussia",
                                     "options": ["conquest"]})
        assert world.dialogue_manager.is_hard_stop()
        response = {"enemy_phase": {"nations": {}}}
        M._apply_command_popup_contract(response, {}, world)
        assert response.get("deferred_dialogue", {}).get("type") == "war_purpose_selection"

    def test_no_hard_stop_no_key(self):
        with _quiet():
            world = WorldState.from_scenario(SCENARIO)
        response = {"enemy_phase": {"nations": {}}}
        M._apply_command_popup_contract(response, {}, world)
        assert "deferred_dialogue" not in response

    def test_the_client_stashes_raises_and_drains(self):
        src = (REPO / "godot-client/project-sovereign/scripts/main.gd").read_text(encoding="utf-8")
        assert "_stash_deferred_dialogue(response)" in src
        assert "if _show_pending_deferred_dialogue():" in src
        tail = src[src.index("func _return_control_to_player()"):]
        tail = tail[:tail.index("\nfunc ", 10)]
        assert "_show_pending_deferred_dialogue()" in tail
        assert "if not interrupt_queue.is_empty():" in tail and "_process_next_interrupt()" in tail
        capture = src[src.index("func _on_capture_choice_response("):]
        capture = capture[:capture.index("\nfunc ", 10)]
        assert "_return_control_to_player()" in capture, "R2-F5: the capture tail must drain the queue"
        stash = src[src.index("func _stash_diorama("):]
        stash = stash[:stash.index("\nfunc ", 10)]
        assert 'response.get("strategic_reports", [])' in stash, "R2-F7: the row's tableau"


# ═══════════════════════════════════════════════════════════════════════
# The small ones: the copy, the log row, the driver
# ═══════════════════════════════════════════════════════════════════════

class TestTheDestinationCopy:

    def test_after_a_stalemate_the_destination_arm_says_so(self):
        world, wel = _legacy()
        wel.strength = 30000
        wel.strategic_order = _order("MOVE_TO", "Paris", path=["Paris"], combat_attempts=1)
        ney = world.marshals["Ney"]
        ney.location = "Paris"
        ney.strength = 5000
        world._build_marshal_index()
        world.calculate_visibility()
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            row = proc._handle_blocked_path(wel, [ney], "Paris", world, {"world": world})
        assert row.get("requires_input") is True, row
        assert "Previous assault was inconclusive" in row["message"], row["message"]
        assert "Odds unfavorable" not in row["message"]


class TestTheRefusedFirstStepLeavesNoLogRow:

    def test_the_march_is_not_logged(self, monkeypatch):
        # FA slice 5 (Sept 4, 2026): with the road law at issuance this
        # march is refused BEFORE an order exists (the crossing gate, at
        # 0 AP — pinned in test_fa_slice5_the_road_law_2026_09_04.py), so
        # the retraction seam this pin guards is reached through the
        # lever-off arm: it still serves every first-step refusal that is
        # not a road-law refusal (engaged elsewhere, drilling-locked, guns
        # limbered).
        monkeypatch.setattr(strategic_mod, "ROAD_LAW_AT_ISSUANCE", False)
        world, ney, moore = _channel()
        before = [e for e in world.event_log if e.get("type") == "strategic_order"
                  and e.get("marshal") == "Ney"]
        parsed = {"is_strategic": True, "strategic_type": "MOVE_TO", "target": "London",
                  "marshal": "Ney", "action": "move", "original_command": "Ney, march to London"}
        with _quiet():
            result = CommandExecutor().execute(parsed | {"command": {
                "marshal": "Ney", "action": "move", "target": "London"}}, {"world": world})
        assert result.get("success") is False and result.get("attack_refused") is True, result
        after = [e for e in world.event_log if e.get("type") == "strategic_order"
                 and e.get("marshal") == "Ney"]
        assert after == before, "R1-F6: 'Ney ordered to move to London' survived the refusal"

    def test_the_helper_retracts_only_this_turn_and_marshal(self):
        world, ney, moore = _channel()
        world.log_event({"type": "strategic_order", "marshal": "Davout", "order_type": "MOVE_TO"})
        world.log_event({"type": "strategic_order", "marshal": "Ney", "order_type": "MOVE_TO"})
        assert retract_order_log(world, "Ney", "MOVE_TO") is True
        assert retract_order_log(world, "Ney", "MOVE_TO") is False
        assert any(e.get("marshal") == "Davout" for e in world.event_log
                   if e.get("type") == "strategic_order")


class TestTheDriverAnswersEveryMarshal:

    def test_every_awaiting_row_is_answered(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "playtest_driver", REPO / "tools" / "playtest_driver.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        rows = [{"marshal": "Davout", "requires_input": True, "interrupt_type": "contact",
                 "options": ["attack", "go_around", "hold_position", "cancel_order"]},
                {"marshal": "Ney", "requires_input": True, "interrupt_type": "contact",
                 "options": ["attack", "go_around", "hold_position", "cancel_order"]}]
        response = {"strategic_reports": rows, "pending_interrupt": rows[0]}
        assert [r["marshal"] for r in mod._interrupt_reports(response)] == ["Davout", "Ney"]
        posted = []

        class _T:
            def post(self, path, payload):
                posted.append((path, payload.get("marshal_name")))
                return {"success": True}

        class _D:
            def popup(self, *a, **k): pass
            def battle(self, *a, **k): pass

        answerer = mod.Answerer.__new__(mod.Answerer)
        answerer.t = _T()
        answerer.d = _D()
        answerer.policy = {"objection": "trust"}
        with _quiet():
            answerer.scan(response)
        assert [p for p in posted if p[0] == "/strategic_response"] == [
            ("/strategic_response", "Davout"), ("/strategic_response", "Ney")], posted


class TestTheLeversShip:

    def test_both_are_up(self):
        assert strategic_mod.CANNON_FIRE_READS_THE_ANSWER is True
        assert strategic_mod.ANSWERED_CONTACT_READS_THE_BOARD is True
