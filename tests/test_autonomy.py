"""The TASK TO PROVE HIMSELF — row IC, Session 2b (November 20, 2026).

This file was the old autonomy engine's (Phase 2.5: "Grant Autonomy" — three
turns in which a French marshal took no orders and was moved by the ENEMY's
decision logic). That engine is removed (`docs/INDEPENDENT_COMMAND_SPEC.md`
§6.11, version 6, with the user's consent — "even removing it if needed"), and
the file is REWRITTEN, never deleted, so the audience keeps its cover: every
class below tests what stands where the old engine stood.

    THE PROPOSAL      his own, by his nature, read from what France sees, PURE
    THE AUDIENCE      the arm `trial` — always offered — and its words in full
    GIVING IT         free; an exact order; what the window showed is given
    NO ORDERS         every order to him is refused, the cancel too (the user's
                      ruling in this session's Plan Mode: "No call-back")
    THE NIGHTS        the take, the count-down, the hold put back
    THE ROLL          a last turn ended on a victory presses on, six turns at
                      most (the user's ruling: "He presses on")
    THE BANDS         today's rewards, kept: +40 and +10 authority / +25 / +15 / +5
    THE MORNING       how he did, told once
    THE ENEMY'S LOGIC never moves a French marshal

The rules are `backend/game_logic/trial.py`; SYSTEMS_REFERENCE §232.
"""
from __future__ import annotations

import contextlib
import copy
import io
import random
from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic import trial as T
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
                 / "europe_1805.json")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def base():
    """The shipped 1805 board, loaded once (each test plays on a copy)."""
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(base):
    with _quiet():
        return WorldState.from_dict(base.to_dict())


def _place(world, name: str, where: str) -> None:
    world.marshals[name].location = where
    with _quiet():
        world._build_marshal_index()
        world.calculate_visibility()


def _audience(world, name: str):
    """The game's own question for `name`: trust at 15, the checker asked."""
    marshal = world.marshals[name]
    with _quiet():
        marshal.trust.set(15)
        event = world.disobedience_system.check_redemption_threshold(marshal, world)
    assert event is not None, "the premise: the audience opens at trust 15"
    return marshal, event


def _give(world, name: str):
    marshal, event = _audience(world, name)
    with _quiet():
        result = world.disobedience_system.handle_redemption_response(
            event, T.ARM, {"world": world})
    assert result["success"], result
    return marshal, result


def _end_turn(world, executor=None):
    executor = executor or CommandExecutor()
    with _quiet():
        return executor.execute({"command": {"action": "end_turn"}},
                                {"world": world, "executor": executor})


def _send(world, command: dict, **parsed):
    executor = CommandExecutor()
    with _quiet():
        return executor.execute({"command": dict(command), **parsed},
                                {"world": world, "executor": executor})


# ═══════════════════════════ the proposal ═══════════════════════════════════

class TestTheProposalByNature:

    def test_a_bold_man_goes_for_the_nearest_place_the_enemy_holds(self, world):
        _place(world, "Ney", "Franconia")
        read = T.proposal(world, world.marshals["Ney"])
        assert (read["nature"], read["task"], read["place"]) == ("bold", "take", "Bohemia")
        assert read["line"] == "Ney, take Bohemia and hold it."
        assert read["words"] == (
            "Ney is a bold man, so he asks to march from Franconia and take Bohemia, where France "
            "sees no defenders — and then to hold it, striking any enemy next to him that he "
            "outnumbers.")

    def test_a_careful_man_on_the_same_ground_holds_it_and_digs_in(self, world):
        """The blind reading's premise: two men on one ground, two tasks —
        because of who they are."""
        _place(world, "Ney", "Franconia")
        _place(world, "Davout", "Franconia")
        bold = T.proposal(world, world.marshals["Ney"])
        careful = T.proposal(world, world.marshals["Davout"])
        assert careful["nature"] == "careful" and careful["task"] == "hold"
        assert careful["line"] == "Davout, hold Franconia."
        assert careful["words"] == ("Davout is a careful man, so he asks to hold Franconia, "
                                    "where he stands, and to dig in.")
        assert bold["line"] != careful["line"] and bold["task"] != careful["task"]

    def test_a_bold_man_who_is_outnumbered_holds_and_names_the_enemy_too_strong(self, world):
        """On the opening board Mack's 52,000 stand in Swabia beside Ney's
        24,000 (§7: "attack means attack if not outnumbered")."""
        read = T.proposal(world, world.marshals["Ney"])
        assert read["task"] == "hold" and read["place"] == "Rhineland"
        assert "Mack, at Swabia" in read["words"]
        assert "too strong for his corps alone" in read["words"]
        assert "striking any enemy next to him that he outnumbers" in read["words"]

    def test_an_enemy_army_on_a_friends_ground_is_driven_out_not_taken(self, world):
        """Mack stands on Bavaria's Swabia: with the numbers on his side a bold
        man goes for HIM — the ground is not the enemy's to take."""
        world.marshals["Mack"].strength = 9000
        with _quiet():
            world.calculate_visibility()
        read = T.proposal(world, world.marshals["Ney"])
        assert read["task"] == "take" and read["place"] == "Swabia" and read["foe"] == "Mack"
        assert read["line"].startswith("Ney, drive Mack out of Swabia and hold there.")
        assert "asks to march from Rhineland and drive Mack out of Swabia" in read["words"]
        assert "then to hold where he ends" in read["words"]

    def test_an_allys_ground_in_the_enemys_hands_is_freed_not_taken(self, world):
        """The measure's find (the provoking campaign on `austerlitz`, turn 4):
        Bavaria's Swabia in Austria's hands is handed back to Bavaria by the
        game's own rule (`world_state.liberates_ally_ground`) — "take Swabia
        and hold it" promised a province France does not keep."""
        from backend.commands.strategic import StrategicOrderProcessor
        world.get_region("Swabia").controller = "Austria"
        world.marshals["Mack"].location = "Vienna"            # he has marched away
        with _quiet():
            world._build_marshal_index()
            world.calculate_visibility()
        ney = world.marshals["Ney"]
        read = T.proposal(world, ney)
        assert read["line"].startswith("Ney, free Swabia for Bavaria and hold it.")
        assert "asks to march from Rhineland and free Swabia for Bavaria, where France sees no defenders" \
            in read["words"]
        assert "take Swabia" not in read["words"] + read["line"]
        ney, _result = _give(world, "Ney")
        executor = CommandExecutor()
        with _quiet():
            rows = StrategicOrderProcessor(executor).process_strategic_orders(
                world, {"world": world, "executor": executor})
        row = next(row for row in rows if row.get("marshal") == "Ney")
        assert row["message"] == "Ney marches on Swabia, as he proposed. Swabia is Bavaria's again."
        assert world.get_region("Swabia").controller == "Bavaria" and ney.location == "Swabia"

    def test_a_literal_man_holds_and_falls_back_if_outnumbered(self, world):
        soult = world.marshals["Soult"]
        assert soult.personality == "literal"
        read = T.proposal(world, soult)
        assert read["nature"] == "literal" and read["task"] == "hold"
        first = read["if_thens"][0]
        assert (first["if"], first["then"]) == ("outnumbered", "fall_back")
        assert world.get_region(first["to"]).controller == "France"
        assert read["words"].startswith(
            "Soult follows orders to the letter, so he asks for exact orders: to hold Lorraine")
        assert f"If he is outnumbered, he falls back to {first['to']}." in read["words"]

    def test_each_of_them_helps_the_friend_next_to_him(self, world):
        """One line for a bold or a careful man — the friend's; a literal man
        carries his fall back and the friend's both."""
        for name, lines in (("Ney", 1), ("Davout", 1), ("Soult", 2)):
            read = T.proposal(world, world.marshals[name])
            assert len(read["if_thens"]) == lines, name
            last = read["if_thens"][-1]
            assert (last["if"], last["then"]) == ("friend_attacked", "join")
            friend = world.marshals[last["friend"]]
            assert friend.nation == "France" and friend.location != world.marshals[name].location
            assert f"If {last['friend']} is attacked next to him, he marches to join that battle." \
                in read["words"]

    def test_the_friend_is_the_weakest_beside_him_and_never_a_man_he_hates(self, world):
        ney = world.marshals["Ney"]
        friend = T.proposal(world, ney)["if_thens"][-1]["friend"]
        here = world.get_region(ney.location)
        beside = [m for m in world.get_player_marshals()
                  if m.name != "Ney" and m.location in here.adjacent_regions]
        assert friend == min(beside, key=lambda m: (m.strength, m.name)).name
        ney.relationships[friend] = -2
        other = T.proposal(world, ney)["if_thens"][-1]["friend"]
        assert other != friend

    def test_with_no_board_to_read_he_proposes_to_hold_where_he_stands(self, world):
        read = T.proposal(None, world.marshals["Ney"])
        assert read["task"] == "hold" and read["place"] == "Rhineland" and not read["if_thens"]

    def test_the_proposal_is_pure(self, world):
        """No write, no die — for every marshal of ours (R-INERT's purity)."""
        random.seed(1805)
        dice = random.getstate()
        before = copy.deepcopy(world.to_dict())
        with _quiet():
            for marshal in world.get_player_marshals():
                T.proposal(world, marshal)
                T.option(world, marshal)
        assert world.to_dict() == before
        assert random.getstate() == dice


# ═══════════════════════════ the audience ═══════════════════════════════════

class TestTheAudienceOffersTheTask:

    def test_the_task_is_offered_and_no_autonomy_arm(self, world):
        _ney, event = _audience(world, "Ney")
        ids = [option["id"] for option in event["options"]]
        assert ids[0] == "trial" and "grant_autonomy" not in ids
        assert set(ids) == {"trial", "administrative_role", "dismiss"}

    def test_the_arm_says_his_proposal_and_the_terms_in_full(self, world):
        _place(world, "Ney", "Franconia")
        _ney, event = _audience(world, "Ney")
        arm = event["options"][0]
        assert arm["text"] == "Give Ney a task to prove himself"
        said = arm["description"]
        assert said.startswith("Ney is a bold man, so he asks to march from Franconia and take Bohemia")
        assert said.split("\n")[1] == (
            "He carries this out by himself for 3 turns — this one and the next two — then he is "
            "under your orders again. Until then he takes no orders, and you cannot call him back. "
            "If he wins a battle on his last turn and loses no battle that turn, his task runs one "
            "turn longer, and so on — up to 6 turns in all, the first 3 included. When his task "
            "ends, his trust in you rises by the first of these that is true: 40 (and your authority "
            "by 10) if he won two battles or took a defended place; 25 if he won more battles than "
            "he lost; 15 if he fought none or won as many as he lost; 5 if he lost more than he won.")
        assert arm["proposal"]["line"] == "Ney, take Bohemia and hold it."

    def test_the_fallback_with_no_world_is_the_task_too(self, world):
        with _quiet():
            event = world.disobedience_system._create_redemption_event(world.marshals["Ney"])
        assert [option["id"] for option in event["options"]] == ["trial"]

    def test_a_man_on_his_task_is_not_asked_again(self, world):
        ney, _result = _give(world, "Ney")
        ney.redemption_cooldown_until = 0
        with _quiet():
            again = world.disobedience_system.check_redemption_threshold(ney, world)
        assert again is None and ney.trust.value <= 20


# ═══════════════════════════ giving it ══════════════════════════════════════

class TestGivingIt:

    def test_it_costs_no_action_and_installs_his_exact_order(self, world):
        _place(world, "Ney", "Franconia")
        actions = world.actions_remaining
        ney, result = _give(world, "Ney")
        assert world.actions_remaining == actions
        order = ney.strategic_order
        assert (order.command_type, order.target, order.opening_take) == ("HOLD", "Franconia", "Bohemia")
        assert order.original_command == "Ney, take Bohemia and hold it."
        assert T.on_trial(ney)
        assert {key: ney.trial[key] for key in ("task", "place", "turns_left", "turns_done", "taken")} \
            == {"task": "take", "place": "Bohemia", "turns_left": 3, "turns_done": 0, "taken": 0}
        assert result["trial"]["turns_left"] == 3
        assert "takes no orders until it ends" in result["message"]

    def test_his_lines_are_written_this_turn_and_live_the_next(self, world):
        soult, _result = _give(world, "Soult")
        lines = soult.strategic_order.if_thens
        assert [line["if"] for line in lines] == ["outnumbered", "friend_attacked"]
        assert all(line["written"] == world.current_turn and not line["used"] for line in lines)
        assert soult.holding_position and soult.hold_region == "Lorraine"   # a literal man's hold

    def test_the_latch_is_cleared_and_the_wait_is_five_turns(self, world):
        ney, _result = _give(world, "Ney")
        assert not ney.redemption_pending
        assert ney.redemption_cooldown_until == world.current_turn + 5

    def test_what_the_window_showed_is_what_is_given(self, world):
        """The board changes under the standing question: NOTHING is given,
        the question stands, and it carries what he proposes now."""
        ney, event = _audience(world, "Ney")              # at Rhineland: he proposes to hold
        assert T.shown_line(event).startswith("Ney, hold Rhineland.")
        _place(world, "Ney", "Franconia")                 # ... and now he would take Bohemia
        with _quiet():
            result = world.disobedience_system.handle_redemption_response(
                event, "trial", {"world": world})
        assert result["success"] is False and result["standing"] is True
        assert not T.on_trial(ney) and ney.strategic_order is None
        assert ney.redemption_pending, "the question stands: no latch cleared"
        assert ney.redemption_cooldown_until == 0, "no cooldown paid"
        assert T.shown_line(result["redemption_event"]) == "Ney, take Bohemia and hold it."
        with _quiet():
            second = world.disobedience_system.handle_redemption_response(
                result["redemption_event"], "trial", {"world": world})
        assert second["success"] and ney.strategic_order.opening_take == "Bohemia"

    def test_the_old_arms_id_is_taken_as_the_task(self, world):
        """A standing question from before the change never sticks."""
        ney, event = _audience(world, "Ney")
        with _quiet():
            result = world.disobedience_system.handle_redemption_response(
                event, "grant_autonomy", {"world": world})
        assert result["success"] and result["choice"] == "trial" and T.on_trial(ney)


# ═══════════════════════════ no orders ══════════════════════════════════════

class TestHeTakesNoOrders:

    ORDERS = [
        ({"marshal": "Ney", "action": "attack", "target": "Mack"}, {}),
        ({"marshal": "Ney", "action": "move", "target": "Lorraine"}, {}),
        ({"marshal": "Ney", "action": "defend"}, {}),
        ({"marshal": "Ney", "action": "fortify"}, {}),
        ({"marshal": "Ney", "action": "drill"}, {}),
        ({"marshal": "Ney", "action": "wait"}, {}),
        ({"marshal": "Ney", "action": "retreat"}, {}),
        ({"marshal": "Ney", "action": "stance_change", "target": "defensive"}, {}),
        ({"marshal": "Ney", "action": "hold", "target": "Lorraine"},
         {"is_strategic": True, "strategic_type": "HOLD"}),
        ({"marshal": "Ney", "action": "move", "target": "Lorraine"},
         {"is_strategic": True, "strategic_type": "MOVE_TO"}),
        ({"marshal": "Ney", "action": "cancel"}, {}),
    ]

    @pytest.mark.parametrize("command, parsed", ORDERS,
                             ids=[f"{c['action']}{'-standing' if p else ''}" for c, p in ORDERS])
    def test_every_order_is_refused_free_the_cancel_too(self, world, command, parsed):
        ney, _result = _give(world, "Ney")
        order, actions = ney.strategic_order, world.actions_remaining
        reply = _send(world, command, **parsed)
        assert reply["success"] is False
        assert reply["message"].startswith(
            "Ney is on his task to prove himself and takes no orders until it ends (3 turns left")
        assert world.actions_remaining == actions, "refused free"
        assert ney.strategic_order is order and T.on_trial(ney), "his order and his task stand"
        assert ney.location == "Rhineland"

    def test_the_true_reason_is_given_with_no_action_left(self, world):
        """Never "Not enough actions": the trial's refusal is read before the pool."""
        _ney, _result = _give(world, "Ney")
        world.actions_remaining = 0
        reply = _send(world, {"marshal": "Ney", "action": "attack", "target": "Mack"})
        assert "takes no orders until it ends" in reply["message"]
        # ... the whole sentence, with the count and the longest it can run
        # (the third blind reading: "longer while he keeps winning" was vaguer
        # than the window that had just said six)
        assert reply["message"] == ("Ney is on his task to prove himself and takes no orders until "
                                    "it ends (3 turns left — up to 6 in all while he keeps winning).")

    def test_the_cancel_buttons_road_refuses_free(self, world):
        ney, _result = _give(world, "Ney")
        executor = CommandExecutor()
        with _quiet():
            reply = executor._execute_cancel({"action": "cancel", "marshal": "Ney"}, {"world": world})
        assert reply["success"] is False and reply["no_action_cost"] is True
        assert "takes no orders until it ends" in reply["message"]
        assert T.on_trial(ney) and ney.strategic_order is not None

    def test_a_bare_cancel_never_reaches_for_him(self, world):
        """"cancel" with no name ends some other man's order — never his."""
        ney, _result = _give(world, "Ney")
        executor = CommandExecutor()
        with _quiet():
            reply = executor._execute_cancel({"action": "cancel"}, {"world": world})
        assert reply["success"] is False and "No marshal has an active strategic order" in reply["message"]
        assert ney.strategic_order is not None

    def test_what_is_no_order_to_him_passes(self, world):
        _ney, _result = _give(world, "Ney")
        assert T.order_refusal(world, {"marshal": "Ney"}, "status") is None
        # his pay and his title: what the Emperor does FOR him is no order to him
        for act in ("grant_pension", "revoke_pension", "grant_dotation"):
            assert T.order_refusal(world, {"marshal": "Ney"}, act) is None, act
        assert T.order_refusal(world, {"marshal": "Ney"}, "end_turn") is None
        assert T.order_refusal(world, {}, "attack") is None, "an order that names nobody is the pickers' to refuse"
        assert T.order_refusal(world, {"marshal": "Davout"}, "attack") is None
        assert T.order_refusal(world, {"marshal": "Ney"}, "attack") is not None

    def test_the_screens_probe_refuses_every_verb_and_every_button(self, world):
        from backend.commands import state_probe as SP
        ney, _result = _give(world, "Ney")
        reason = "on his task to prove himself — he takes no orders (3 turns left)"
        assert SP.order_refusals(world, ney) == {verb: reason for verb in SP.VERBS}
        assert SP.button_refusals(world, ney) == {key: reason for key in SP.BUTTONS}
        assert SP.order_refusals(world, world.marshals["Davout"]) != SP.order_refusals(world, ney)

    def test_his_order_on_the_map_says_it_cannot_be_cancelled(self, world):
        from backend.commands.strategic import standing_order_road
        ney, _result = _give(world, "Ney")
        road = standing_order_road(world, ney)
        assert road["kind"] == "hold"
        assert road["trial"] == "On a task to prove himself — 3 turns left"
        assert standing_order_road(world, world.marshals["Davout"]) == {}

    def test_he_is_never_pulled_off_his_task_by_a_distant_battle(self, world):
        from backend.commands.strategic import StrategicOrderProcessor
        from backend.models.marshal import StrategicOrder
        ney = world.marshals["Ney"]
        world.record_battle("Lorraine", "Mack", "Soult", "defender_victory")
        processor = StrategicOrderProcessor(CommandExecutor())
        # the control (the review: without it the test could pass with no
        # guard at all): under a PLAIN standing order the same battle does
        # pull a bold man off his post
        turn = int(world.current_turn)
        ney.strategic_order = StrategicOrder(
            command_type="HOLD", target=ney.location, target_type="region",
            started_turn=turn - 1, issued_turn=turn - 1, original_command="Ney, hold")
        with _quiet():
            heard = processor._check_interrupts(ney, world)
        assert heard is not None, "the premise: the guns call a bold man off a plain hold"
        ney.strategic_order = None
        ney.pending_interrupt = None
        ney, _result = _give(world, "Ney")
        with _quiet():
            assert processor._check_interrupts(ney, world) is None


# ═══════════════════════════ the nights ═════════════════════════════════════

class TestTheNights:

    def test_the_take_runs_on_the_first_night_and_his_hold_follows_him(self, world):
        _place(world, "Ney", "Franconia")
        ney, _result = _give(world, "Ney")
        result = _end_turn(world)
        rows = [row for row in result["strategic_reports"] if row.get("marshal") == "Ney"]
        assert [row.get("action") for row in rows] == ["trial_take"]
        assert rows[0]["message"] == "Ney marches on Bohemia, as he proposed. Bohemia is ours."
        assert ney.location == "Bohemia" and world.get_region("Bohemia").controller == "France"
        order = ney.strategic_order
        assert (order.command_type, order.target, order.opening_take) == ("HOLD", "Bohemia", None)
        assert ney.trial["turns_left"] == 2 and ney.trial["next_take"] is None

    def test_a_take_that_no_longer_stands_is_dropped_and_he_says_why(self, world):
        """The night's last look is the proposal's own reader: he never picks
        another place unannounced."""
        from backend.commands.strategic import StrategicOrderProcessor
        _place(world, "Ney", "Franconia")
        ney, _result = _give(world, "Ney")
        world.get_region("Bohemia").controller = "France"       # a friend took it first
        executor = CommandExecutor()
        with _quiet():                # (the order pass itself: no enemy turn retakes it first)
            rows = StrategicOrderProcessor(executor).process_strategic_orders(
                world, {"world": world, "executor": executor})
        row = next(row for row in rows if row.get("marshal") == "Ney")
        assert row["action"] == "trial_take_dropped"
        assert row["message"] == ("Ney does not march on Bohemia: no enemy holds it any longer. "
                                  "He holds Franconia.")
        assert ney.location == "Franconia" and ney.strategic_order.opening_take is None

    def test_three_turns_then_he_is_back_in_hand(self, world):
        davout, _result = _give(world, "Davout")
        left = []
        for _night in range(3):
            assert T.on_trial(davout)
            _end_turn(world)
            left.append(davout.trial["turns_left"] if T.on_trial(davout) else None)
        assert left == [2, 1, None]
        assert davout.strategic_order is None and not davout.holding_position

    def test_a_hold_that_ended_early_is_put_back_where_he_stands(self, world):
        ney, _result = _give(world, "Ney")
        ney.strategic_order = None                    # his one line fired; a retreat cleared it
        with _quiet():
            T.close_of_turn(world, [])
        order = ney.strategic_order
        assert (order.command_type, order.target) == ("HOLD", "Rhineland")
        assert T.on_trial(ney) and ney.trial["turns_left"] == 2

    def test_a_man_lost_with_his_corps_ends_his_task_with_nothing_to_settle(self, world):
        ney, _result = _give(world, "Ney")
        ney.strength = 0
        with _quiet():
            rows = T.tick(world)
        assert not T.on_trial(ney) and ney.trust.value == 15
        assert rows[-1]["message"] == "Ney's task to prove himself ended with his corps."


class TestTheTakeIsAnOrderSeam:
    """The FA slice-3 census's eighteenth producer (`trial.run_take`'s
    attack — `tests/test_fa_slice3_the_order_tells_the_truth…`
    `test_the_attack_sites_are_counted`): a take the executor REFUSES is
    never narrated as a march or a battle — he holds where he stands, and the
    row carries the executor's own reason (FA-14's rule)."""

    def test_a_refused_take_is_said_with_its_reason_and_he_holds(self, world, monkeypatch):
        from backend.commands.strategic import StrategicOrderProcessor
        _place(world, "Ney", "Franconia")
        ney, _result = _give(world, "Ney")
        executor = CommandExecutor()
        executor_type = type(executor)
        real = executor_type.execute

        def refuse_the_strike(self, command, game_state):
            cmd = (command or {}).get("command") or {}
            if cmd.get("action") == "attack" and cmd.get("_strategic_execution"):
                return {"success": False, "message": "the bridge is down."}
            return real(self, command, game_state)
        monkeypatch.setattr(executor_type, "execute", refuse_the_strike)
        with _quiet():
            rows = StrategicOrderProcessor(executor).process_strategic_orders(
                world, {"world": world, "executor": executor})
        row = next(row for row in rows if row.get("marshal") == "Ney")
        assert row["action"] == "trial_take_refused", row
        assert row["message"] == ("Ney could not march on Bohemia: the bridge is down. "
                                  "He stands at Franconia.")
        assert "marches on" not in row["message"]
        assert ney.location == "Franconia" and world.get_region("Bohemia").controller == "Austria"
        order = ney.strategic_order
        assert (order.command_type, order.target, order.opening_take) == ("HOLD", "Franconia", None)
        assert T.on_trial(ney) and ney.trial["next_take"] is None, "the take runs once"

    def test_a_man_who_answered_a_friends_guns_does_not_march_as_well(self, world):
        """One act a night: he fought beside his friend this turn."""
        from backend.commands.strategic import StrategicOrderProcessor
        _place(world, "Ney", "Franconia")
        ney, _result = _give(world, "Ney")
        ney.reinforced_this_turn = True
        executor = CommandExecutor()
        with _quiet():
            rows = StrategicOrderProcessor(executor).process_strategic_orders(
                world, {"world": world, "executor": executor})
        row = next(row for row in rows if row.get("marshal") == "Ney")
        assert row["action"] == "trial_take_dropped"
        assert row["message"] == ("Ney answered a friend's guns this turn, so he does not march on "
                                  "Bohemia as well. He holds Franconia.")
        assert ney.location == "Franconia" and ney.strategic_order.opening_take is None


# ═══════════════════════════ the roll ═══════════════════════════════════════

class TestTheRoll:

    @staticmethod
    def _nights(world, marshal, wins_from: int, nights: int = 9):
        """Tick the close of each turn; from `wins_from` on, he won a battle
        that turn. Returns the row actions per night."""
        told = []
        for night in range(1, nights + 1):
            if not T.on_trial(marshal):
                break
            if night >= wins_from:
                marshal.battles_won += 1
            with _quiet():
                rows = T.tick(world)
            told.append([row["action"] for row in rows])
        return told

    def test_a_last_turn_ended_on_a_victory_presses_on(self, world):
        _place(world, "Ney", "Franconia")
        ney, _result = _give(world, "Ney")
        ney.strategic_order.opening_take = None       # (the first night's take is not this test's)
        told = self._nights(world, ney, wins_from=3, nights=3)
        assert told == [[], [], ["trial_roll"]]
        assert T.on_trial(ney) and ney.trial["turns_left"] == 1 and ney.trial["rolls"] == 1
        assert ney.trust.value == 15, "nothing is settled while the roll lasts"
        # a bold man on a roll goes for the next enemy place in his reach, announced
        assert ney.trial["next_take"] == "Bohemia" and ney.strategic_order.opening_take == "Bohemia"
        # (the review: "his task runs 1 more turn" read as one AFTER this one,
        # beside a refusal that said "1 turn left" of the same turn)
        assert T.status_words(ney) == ("On a roll with his task — 1 turn left: "
                                       "goes for Bohemia as this turn ends")
        assert T.payload(ney)["next_take"] == "Bohemia"

    def test_the_roll_says_what_he_goes_for_and_when_he_comes_back(self, world):
        _place(world, "Ney", "Franconia")
        ney, _result = _give(world, "Ney")
        ney.strategic_order.opening_take = None
        self._nights(world, ney, wins_from=3, nights=2)
        ney.battles_won += 1
        with _quiet():
            rows = T.tick(world)
        assert rows[-1]["message"] == (
            "Ney is on a roll — last turn he won a battle and lost none. He presses on with his "
            "task one more turn and goes for Bohemia as this turn ends. He still takes no orders; "
            "he comes back to you when a turn ends without a victory, in 3 turns at most.")
        # (the review: told in the morning of the turn it announces — "this turn"
        # stood for the turn just closed AND the one now open)
        assert rows[-1]["message"].count("this turn") == 1

    def test_six_turns_at_most(self, world):
        ney, _result = _give(world, "Ney")
        told = self._nights(world, ney, wins_from=1)
        assert told == [[], [], ["trial_roll"], ["trial_roll"], ["trial_roll"], ["trial_ended"]]
        assert not T.on_trial(ney) and ney.strategic_order is None

    def test_the_roll_ends_with_the_first_turn_without_a_victory(self, world):
        ney, _result = _give(world, "Ney")
        ney.battles_won += 1                 # turn 1: a win
        with _quiet():
            T.tick(world)
            T.tick(world)       # turn 2: nothing
        ney.battles_won += 1                 # turn 3: a win -> a roll
        with _quiet():
            assert [r["action"] for r in T.tick(world)] == ["trial_roll"]
            rows = T.tick(world)    # turn 4: nothing -> settled on the whole task
        assert [r["action"] for r in rows] == ["trial_ended"] and rows[0]["band"] == "spectacular"

    def test_a_turn_with_a_defeat_in_it_is_no_roll(self, world):
        ney, _result = _give(world, "Ney")
        with _quiet():
            T.tick(world)
            T.tick(world)
        ney.battles_won += 1
        ney.battles_lost += 1                # he won one and lost one on his last turn
        with _quiet():
            rows = T.tick(world)
        assert [r["action"] for r in rows] == ["trial_ended"] and rows[0]["band"] == "none"

    def test_a_careful_man_on_a_roll_holds_one_more_turn(self, world):
        davout, _result = _give(world, "Davout")
        told = self._nights(world, davout, wins_from=3, nights=3)
        assert told[-1] == ["trial_roll"]
        assert davout.trial["next_take"] is None and davout.strategic_order.opening_take is None
        assert T.status_words(davout) == "On a roll with his task — 1 turn left"


# ═══════════════════════════ the bands ══════════════════════════════════════

class TestTheBands:

    @pytest.mark.parametrize("won, lost, taken, band, trust", [
        (2, 0, 0, "spectacular", 40),
        (0, 0, 1, "spectacular", 40),
        (2, 5, 0, "spectacular", 40),     # two battles won is spectacular whatever was lost
        (1, 0, 0, "good", 25),
        (0, 0, 0, "none", 15),
        (1, 1, 0, "none", 15),
        (0, 1, 0, "poor", 5),
        (1, 2, 0, "poor", 5),
    ])
    def test_todays_rewards_are_kept(self, won, lost, taken, band, trust):
        assert T.band(won, lost, taken) == (band, trust)

    @pytest.mark.parametrize("won, lost, taken, said", [
        (2, 0, 0, "Ney has proved himself. In 3 turns he won 2 battles. His trust in you rises by "
                  "40 (to 55), and your authority by 10. He is under your orders again."),
        (0, 0, 1, "Ney has proved himself. In 3 turns he took 1 defended place. His trust in you "
                  "rises by 40 (to 55), and your authority by 10. He is under your orders again."),
        # two battles won is the rule's "spectacular" whatever was lost: the
        # line says both, so the player sees what was counted
        (2, 4, 0, "Ney has proved himself. In 3 turns he won 2 battles and lost 4 battles. His "
                  "trust in you rises by 40 (to 55), and your authority by 10. He is under your "
                  "orders again."),
        (1, 0, 0, "Ney did well on his task. In 3 turns he won 1 battle. His trust in you rises "
                  "by 25 (to 40). He is under your orders again."),
        (0, 0, 0, "Ney's task is over with little to show for it. In 3 turns he fought no battle. "
                  "His trust in you rises by 15 (to 30). He is under your orders again."),
        (1, 1, 0, "Ney's task is over with little to show for it. In 3 turns he won 1 battle and "
                  "lost 1 battle. His trust in you rises by 15 (to 30). He is under your orders "
                  "again."),
        (1, 3, 0, "Ney did badly on his task. In 3 turns he won 1 battle and lost 3 battles. His "
                  "trust in you rises by 5 (to 20). He is under your orders again."),
    ])
    def test_his_trust_comes_back_by_what_he_did(self, world, won, lost, taken, said):
        """The whole morning line for each band — its verdict, what he did,
        the figures applied. (The battles are on his record from the first
        turn, so his last turn ends on no victory: no roll.)"""
        world.authority_tracker.authority = 50
        ney, _result = _give(world, "Ney")
        ney.battles_won += won
        ney.battles_lost += lost
        ney.trial["taken"] = taken
        with _quiet():
            assert T.tick(world) == [] and T.tick(world) == []
            rows = T.tick(world)
        assert rows[-1]["message"] == said
        assert not T.on_trial(ney)
        assert ney.trust.value == 15 + T.band(won, lost, taken)[1]
        spectacular = won >= 2 or taken >= 1
        assert world.authority_tracker.authority == (60 if spectacular else 50)

    def test_a_spectacular_return_is_written_in_the_books_of_authority(self, world):
        world.authority_tracker.authority = 50
        ney, _result = _give(world, "Ney")
        ney.trial["taken"] = 1
        with _quiet():
            for _night in range(3):
                rows = T.tick(world)
        assert rows[-1]["band"] == "spectacular" and rows[-1]["authority_gain"] == 10
        assert "and your authority by 10" in rows[-1]["message"]
        assert "took 1 defended place" in rows[-1]["message"]

    def test_his_record_is_read_from_when_the_task_was_given(self, world):
        """Battles before the task do not count; attacking, defending or
        joining a friend's fight afterwards all do (the marshal's own record)."""
        ney = world.marshals["Ney"]
        ney.battles_won, ney.battles_lost = 7, 3
        ney, _result = _give(world, "Ney")
        assert T.achieved(ney) == (0, 0, 0)
        ney.battles_won += 2
        ney.battles_lost += 1
        assert T.achieved(ney) == (2, 1, 0)

    def test_a_defended_place_taken_counts_and_an_empty_one_does_not(self, world):
        """The capture's own seam: `had_garrison` is "its defenders were
        beaten this turn" — an empty province proves nothing."""
        _place(world, "Ney", "Franconia")
        ney, _result = _give(world, "Ney")
        executor = CommandExecutor()
        with _quiet():
            executor._combat._attempt_region_capture(
                ney, "Bohemia", world, {"world": world}, had_garrison=False)
        assert world.get_region("Bohemia").controller == "France" and ney.trial["taken"] == 0
        assert ney.trial["walked_in"] == 1, "said in the morning, counted for nothing"
        world.get_region("Bohemia").controller = "Austria"
        world.pending_capture_choice = None
        with _quiet():
            executor._combat._attempt_region_capture(
                ney, "Bohemia", world, {"world": world}, had_garrison=True)
        assert ney.trial["taken"] == 1 and ney.trial["walked_in"] == 1
        davout = world.marshals["Davout"]              # ... and nothing for a man on no task
        with _quiet():
            T.note_taken(davout)
            T.note_walked_in(davout)
        assert davout.trial is None

    def test_a_place_nobody_defended_is_said_though_it_earns_nothing(self, world):
        """IC2B-X19 (the measure's own record): "Murat's task is over with
        little to show for it. In 3 turns he fought no battle." — of a man who
        had freed the province he asked to free. The morning says he took it;
        the reward is the rule's (an empty province proves nothing: +15)."""
        _place(world, "Ney", "Franconia")
        ney, _result = _give(world, "Ney")
        executor = CommandExecutor()
        with _quiet():
            executor._combat._attempt_region_capture(
                ney, "Bohemia", world, {"world": world}, had_garrison=False)
            for _night in range(3):
                rows = T.tick(world)
        assert rows[-1]["band"] == "none" and rows[-1]["trust_gain"] == 15
        assert rows[-1]["message"] == (
            "Ney's task is over with little to show for it. In 3 turns he fought no battle; he "
            "took 1 place that nobody defended. His trust in you rises by 15 (to 30). He is under "
            "your orders again.")
        # ... and beside a battle it joins the list
        assert T._deeds(1, 0, 0, 3, walked_in=2) == (
            "In 3 turns he won 1 battle and took 2 places that nobody defended.")
        assert T._deeds(0, 0, 0, 3) == "In 3 turns he fought no battle."
        assert T.band(0, 0, 0) == ("none", 15), "the rule is untouched"


# ═══════════════════════════ the morning ════════════════════════════════════

class TestTheMorningSaysHowHeDid:

    def test_the_end_is_told_once_in_the_turns_events(self, world):
        davout, _result = _give(world, "Davout")
        told, rows = [], []
        for _night in range(4):
            result = _end_turn(world)
            told.append([event["message"] for event in result.get("tactical_events") or []
                         if event.get("type") == "marshal_trial"])
            rows.append([row for row in result.get("strategic_reports") or []
                         if row.get("marshal") == "Davout"])
        assert told[0] == [] and told[1] == [] and told[3] == []
        assert len(told[2]) == 1
        assert told[2][0].startswith("Davout's task is over with little to show for it. "
                                     "In 3 turns he fought no battle. His trust in you rises by 15")
        # ONCE: the turn's report prints the turn's events and the standing
        # orders' rows — the count's line is in the first and never the second
        for night in rows:
            assert not [row for row in night
                        if str(row.get("action") or "") in ("trial_ended", "trial_roll")
                        or "task is over" in str(row.get("message") or "")], night

    def test_the_turns_close_returns_the_reports_and_adds_no_row_of_its_own(self, world):
        ney, _result = _give(world, "Ney")
        ney.trial["turns_left"] = 1                    # his last turn
        kept = [{"marshal": "Davout", "message": "kept"}]
        with _quiet():
            out = T.close_of_turn(world, kept)
        assert out == kept and not T.on_trial(ney)
        with _quiet():
            lines = T.morning_events(world)
        assert [line["phase"] for line in lines] == ["ended"]
        with _quiet():
            assert T.morning_events(world) == [], "told once"

    def test_the_morning_dispatch_carries_the_line(self):
        from backend.game_logic import dispatch as D
        assert "marshal_trial" in D._DISPATCH_EVENT_TYPES
        rows = D._build_turn_events(
            [{"type": "marshal_trial", "nation": "France", "phase": "ended",
              "message": "Ney did well on his task."}], "France")
        assert [row["message"] for row in rows] == ["Ney did well on his task."]

    @pytest.mark.parametrize("event, line", [
        ({"phase": "given", "task": "take", "place": "Bohemia"},
         "Ney is given a task to prove himself — to take Bohemia and hold it; "
         "he takes no orders until it ends"),
        ({"phase": "given", "task": "hold", "place": "Rhineland"},
         "Ney is given a task to prove himself — to hold Rhineland; "
         "he takes no orders until it ends"),
        ({"phase": "roll", "place": "Bohemia"},
         "Ney is on a roll — his task runs one more turn and goes for Bohemia"),
        ({"phase": "ended", "band": "spectacular", "trust_gain": 40, "authority_gain": 10},
         "Ney's task to prove himself is over — he has proved himself (trust +40, authority +10)"),
        ({"phase": "ended", "band": "poor", "trust_gain": 5},
         "Ney's task to prove himself is over — a poor result (trust +5)"),
        ({"phase": "ended", "band": ""},
         "Ney's task to prove himself ended with his corps"),
        ({"phase": "settled", "band": "none", "trust_gain": 15},
         "Ney was acting without orders when the game was saved — settled on loading (trust +15)"),
    ])
    def test_the_campaign_log_has_a_line_for_each_phase(self, event, line):
        from backend import campaign_log as CL
        row = {"type": "marshal_trial", "marshal": "Ney", "nation": "France", "turn": 3, **event}
        assert CL.format_event_oneliner(row, "France") == line
        assert "marshal_trial" in CL.CAMPAIGN_LOG_TYPES
        assert CL.CATEGORY_MAP["marshal_trial"] == "command"

    def test_his_card_and_the_generals_screen_say_where_he_stands(self, world):
        from backend.game_logic.marshal_overview import build_marshal_overview
        ney, _result = _give(world, "Ney")
        assert T.status_words(ney) == "On a task to prove himself — 3 turns left"
        with _quiet():
            cards = build_marshal_overview(world)
        by_name = {card["name"]: card for card in cards}
        assert by_name["Ney"]["trial"]["status"] == "On a task to prove himself — 3 turns left"
        assert by_name["Davout"]["trial"] is None
        assert "is_autonomous" not in by_name["Ney"] and "autonomy_reason" not in by_name["Ney"]


# ═══════════════════════════ the enemy's logic ══════════════════════════════

class TestNoFrenchMarshalIsMovedByTheEnemysLogic:

    def test_the_decision_tree_refuses_a_marshal_of_the_players_nation(self, world):
        from backend.ai.enemy_ai import EnemyAI
        ney = world.marshals["Ney"]
        random.seed(7)
        dice = random.getstate()
        before = copy.deepcopy(world.to_dict())
        with _quiet():
            outcome = EnemyAI(CommandExecutor()).decide_single_action(
                ney, "France", world, {"world": world})
        assert outcome is None
        assert world.to_dict() == before, "nothing is written"
        assert random.getstate() == dice, "no draw is taken"

    def test_it_still_decides_for_a_court_that_is_not_the_players(self, world):
        from backend.ai.enemy_ai import EnemyAI
        mack = world.marshals["Mack"]
        with _quiet():
            outcome = EnemyAI(CommandExecutor()).decide_single_action(
                mack, "Austria", world, {"world": world})
        assert isinstance(outcome, dict) and outcome["marshal"] == "Mack"

    def test_the_old_engine_is_gone(self):
        from backend.game_logic.turn_manager import TurnManager
        from backend.models.marshal import Marshal
        assert not hasattr(TurnManager, "_process_autonomous_marshals")
        assert not hasattr(TurnManager, "_end_autonomy")
        marshal = Marshal("Probe", "Paris", 1000, "aggressive", "France")
        for gone in ("autonomous", "autonomy_turns", "autonomy_reason", "autonomous_battles_won",
                     "autonomous_battles_lost", "autonomous_regions_captured"):
            assert not hasattr(marshal, gone), gone
            assert gone not in marshal.to_dict(), gone
        assert marshal.trial is None and "trial" not in marshal.to_dict()

    def test_a_turn_with_a_man_on_his_task_carries_no_old_report(self, world):
        _ney, _result = _give(world, "Ney")
        result = _end_turn(world)
        assert "independent_command_report" not in result
        assert "show_independent_command_report" not in result
        assert "own_way" not in (result.get("while_you_waited") or {})
