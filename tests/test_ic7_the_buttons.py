"""Row IC, Session 2 — IC-7, A BUTTON FOR EVERY SIMPLE ORDER (November 20, 2026).

The user's word: "make sure buttons exist for simpler things but typing is used
for missions". The design is `docs/INDEPENDENT_COMMAND_SPEC.md` version 6, §8.1
(the inventory of November 20: eight simple orders and four group orders had
no button — row IC-V4); the rules `docs/SYSTEMS_REFERENCE.md` §231.

A button says what it will do and what it costs BEFORE the press (row PW), and
is greyed with the executor's own reason where the order would be refused —
never a dead button. So every new button's price and refusal come from the
reader the executor itself uses:

    posture (stance)   `tactical_executor.stance_refusal` + `stance_change_cost`
    form / break square  `tactical_executor.square_refusal`
    stay put           the bare `wait` (free) — and `Marshal.stay_put_turn`
    chase / stand / look   `state_probe.VERBS` (pursue / defend / scout), as before
    bombard / charge / held back / a march's "then"   the order card's quote
                       (`order_quotes` — `alts`, `thens`)

This file pins the SERVER half: the probe refuses exactly what the executor
refuses and prices what it charges. The client half (the one table
`SIMPLE_ORDER_BUTTONS`, IC-V4's pin) is `tests/test_ic_review_pins.py` and the
driven walk in `tests/test_dd_b_the_client_hands.py`.
"""
from __future__ import annotations

import contextlib
import io
import json
import random
from pathlib import Path

import pytest

from backend.commands import state_probe as SP
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser
from backend.models.marshal import Stance
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
                 / "europe_1805.json")

# the line each button sends (the client's own: `<Marshal>, <words>`)
LINES = {
    "wait": "wait",
    "form_square": "form square",
    "break_square": "break square",
    "stance:aggressive": "aggressive stance",
    "stance:neutral": "neutral stance",
    "stance:defensive": "defensive stance",
}


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def world1805():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO_PATH))


def _fresh(world1805) -> WorldState:
    with _quiet():
        return WorldState.from_dict(world1805.to_dict())


# ── the staged states ───────────────────────────────────────────────────────

def _plain(world, m):
    pass


def _defensive(world, m):
    m.stance = Stance.DEFENSIVE


def _aggressive(world, m):
    m.stance = Stance.AGGRESSIVE


def _fortified(world, m):
    m.fortified = True
    m.defense_bonus = 0.1


def _drill_locked(world, m):
    m.drilling = True
    m.drilling_locked = True
    m.drill_complete_turn = int(world.current_turn) + 1


def _in_square(world, m):
    m.square_formation = True


def _guns(world, m):
    m.artillery = True


def _retreating(world, m):
    m.retreating = True
    m.retreat_recovery = 1


def _broken(world, m):
    m.broken = True
    m.broken_recovery = 1


def _securing(world, m):
    m.occupation_region = "Swabia"


def _no_actions(world, m):
    world.actions_remaining = 0


def _one_action(world, m):
    world.actions_remaining = 1
    m.stance = Stance.DEFENSIVE       # across to attacking costs two


def _blood_up_2(world, m):
    m.recklessness = 2


def _blood_up_3(world, m):
    m.recklessness = 3


STATES = [
    ("Ney", _plain), ("Ney", _defensive), ("Ney", _aggressive), ("Ney", _fortified),
    ("Ney", _drill_locked), ("Ney", _in_square), ("Ney", _guns), ("Ney", _retreating),
    ("Ney", _broken), ("Ney", _securing), ("Ney", _no_actions), ("Ney", _one_action),
    ("Davout", _plain), ("Soult", _plain),
    ("Murat", _plain), ("Murat", _blood_up_2), ("Murat", _blood_up_3),
]


def _send(world, name, key):
    """The button's own line through the real parser and executor."""
    random.seed(1805)
    parser = CommandParser(use_real_llm=False)
    with _quiet():
        parsed = parser.parse(f"{name}, {LINES[key]}", {"world": world}, world=world)
        assert parsed.get("success"), (name, key, parsed.get("error"))
        return CommandExecutor().execute(parsed, {"world": world})


def _asked(result) -> bool:
    """He was ASKED (an objection, a question): the order was not refused."""
    return (result.get("state") in ("awaiting_player_choice", "awaiting_clarification")
            or bool(result.get("objection")) or bool(result.get("pending_objection")))


class TestTheProbeIsTheExecutorsOwnReader:

    @pytest.mark.parametrize("name, stage", STATES, ids=[f"{n}-{s.__name__.strip('_')}"
                                                         for n, s in STATES])
    def test_a_button_is_greyed_exactly_where_the_order_is_refused(self, world1805, name, stage):
        wrong = []
        for key in SP.BUTTONS:
            world = _fresh(world1805)
            marshal = world.marshals[name]
            stage(world, marshal)
            reason = SP.button_refusal(world, marshal, key)
            price = SP.button_price(world, marshal, key)
            before = int(world.actions_remaining)
            result = _send(world, name, key)
            went = bool(result.get("success"))
            if bool(reason) == went:
                wrong.append((key, "probe says: " + (reason or "it goes"),
                              "executor: " + str(result.get("message"))[:140]))
            elif went and not _asked(result):
                spent = before - int(world.actions_remaining)
                if spent != price:
                    wrong.append((key, f"probe prices {price}", f"executor charged {spent}"))
        assert not wrong, wrong

    def test_the_probe_writes_nothing_and_casts_no_die(self, world1805):
        world = _fresh(world1805)
        before = json.dumps(world.to_dict(), sort_keys=True, default=str)
        state = random.getstate()
        for marshal in world.get_player_marshals():
            SP.button_prices(world, marshal)
            SP.button_refusals(world, marshal)
        assert random.getstate() == state
        assert json.dumps(world.to_dict(), sort_keys=True, default=str) == before

    def test_only_the_players_marshals_carry_them(self, world1805):
        world = _fresh(world1805)
        mack = world.marshals["Mack"]
        assert SP.button_prices(world, mack) == {} and SP.button_refusals(world, mack) == {}
        ney = world.marshals["Ney"]
        assert set(SP.button_prices(world, ney)) == set(SP.BUTTONS)

    def test_the_screen_verbs_table_is_untouched(self):
        """`VERBS` is counted by its own censuses and read by the completer as
        "a typed verb": the new buttons are no members of it."""
        assert not set(SP.BUTTONS) & set(SP.VERBS)
        assert {"pursue", "defend", "scout"} <= set(SP.VERBS), "chase, stand, look read VERBS"


class TestThePostureButtons:

    def test_a_posture_is_priced_by_its_steps(self, world1805):
        world = _fresh(world1805)
        ney = world.marshals["Ney"]
        ney.stance = Stance.NEUTRAL
        assert [SP.button_price(world, ney, f"stance:{p}") for p in SP.POSTURES] == [1, 0, 1]
        ney.stance = Stance.DEFENSIVE
        assert SP.button_price(world, ney, "stance:aggressive") == 2
        assert SP.button_price(world, ney, "stance:neutral") == 0

    def test_the_posture_he_has_is_greyed_in_plain_words(self, world1805):
        world = _fresh(world1805)
        ney = world.marshals["Ney"]
        mine = f"stance:{ney.stance.value}"
        assert SP.button_refusals(world, ney)[mine] == "already in that posture"

    def test_the_executor_refuses_with_the_same_reader(self):
        """The three checks and the horsemen's blood are ONE function now."""
        import inspect
        from backend.commands import tactical_executor as T
        body = inspect.getsource(T.TacticalExecutor._execute_stance_change)
        assert "stance_refusal(marshal, target_stance)" in body
        assert "is engaged in drill exercises" not in body, "the copy is gone"


class TestTheSquareButtons:

    def test_one_reader_for_the_three_that_refused_a_square(self):
        import inspect
        from backend.commands import combat_executor, executor, parse_preview
        for module in (combat_executor, executor, parse_preview):
            source = inspect.getsource(module)
            assert "square_refusal(marshal)" in source, module.__name__
            assert "cannot form an infantry square" not in source, module.__name__

    def test_a_drilling_man_keeps_his_works_when_the_square_is_refused(self, world1805):
        """`_execute_form_square` used to leave the fortification FIRST and
        refuse the square for the drill after."""
        world = _fresh(world1805)
        ney = world.marshals["Ney"]
        ney.fortified, ney.defense_bonus = True, 0.1
        ney.drilling = True
        with _quiet():
            result = CommandExecutor()._combat._execute_form_square(
                {"marshal": "Ney"}, {"world": world})
        assert result["success"] is False and "drilling" in result["message"]
        assert ney.fortified is True and ney.defense_bonus == 0.1

    def test_break_square_is_free_and_only_in_square(self, world1805):
        world = _fresh(world1805)
        ney = world.marshals["Ney"]
        assert SP.button_refusal(world, ney, "break_square") == "not in square"
        ney.square_formation = True
        assert SP.button_refusal(world, ney, "break_square") == ""
        assert SP.button_price(world, ney, "break_square") == 0


class TestStayPut:
    """ "Stay put · free": it quiets his "no orders" row for THIS turn; it is
    not work for a literal man's restlessness and stands no warning down."""

    def test_it_is_free_and_marks_the_turn(self, world1805):
        world = _fresh(world1805)
        davout = world.marshals["Davout"]
        before = int(world.actions_remaining)
        result = _send(world, "Davout", "wait")
        assert result["success"] and int(world.actions_remaining) == before
        assert davout.stay_put_turn == int(world.current_turn)

    def test_a_bold_man_may_object_first_and_is_marked_when_told_again(self, world1805):
        """Ney, with Mack next to him, objects to standing still — the button
        is an order like any other. Nothing is marked while he is only asked;
        insisting sends the same wait, and that marks it."""
        world = _fresh(world1805)
        ney = world.marshals["Ney"]
        asked = _send(world, "Ney", "wait")
        assert _asked(asked) and ney.stay_put_turn is None
        import inspect
        from backend.commands import meta_executor
        told = inspect.getsource(meta_executor.MetaExecutor._execute_post_objection)
        assert told.count("marshal.stay_put_turn = int(world.current_turn)") == 1

    def test_he_is_not_idle_this_turn_and_is_again_the_next(self, world1805):
        from backend.game_logic import today
        world = _fresh(world1805)
        davout = world.marshals["Davout"]
        turn = int(world.current_turn)
        assert davout in today.idle_corps(world)
        _send(world, "Davout", "wait")
        assert davout not in today.idle_corps(world)
        assert today.is_idle(davout, turn) is False and today.is_idle(davout, turn + 1) is True
        assert today.is_idle(davout) is True, "without a turn it reads as it always did"

    def test_the_board_ships_it_for_the_end_turn_list(self, world1805):
        world = _fresh(world1805)
        _send(world, "Davout", "wait")
        with _quiet():
            board = world.get_game_state_summary()["map_data"]
        row = {str(m.get("name")): m for region in board.values()
               for m in (region.get("marshals") or [])}
        assert row["Davout"]["tactical_state"]["stay_put"] is True
        assert row["Soult"]["tactical_state"]["stay_put"] is False
        buttons = row["Davout"]["tactical_state"]["buttons"]
        assert set(buttons["prices"]) == set(SP.BUTTONS)
        assert all(isinstance(v, int) for v in buttons["prices"].values())
        # an enemy corps carries none of it (the fog boundary)
        assert "tactical_state" not in row["Mack"] or "buttons" not in row["Mack"]["tactical_state"]

    def test_a_wait_the_game_gives_itself_marks_nothing(self, world1805):
        world = _fresh(world1805)
        ney = world.marshals["Ney"]
        with _quiet():
            CommandExecutor().execute({"command": {"marshal": "Ney", "action": "wait",
                                                   "_strategic_execution": True}}, {"world": world})
        assert ney.stay_put_turn is None

    def test_it_is_no_work_for_a_literal_mans_restlessness(self, world1805):
        from backend.game_logic import jealousy
        world = _fresh(world1805)
        soult = world.marshals["Soult"]
        world.marshals["Ney"].moved_this_turn = True
        _send(world, "Soult", "wait")
        from backend.models.marshal import StrategicOrder
        soult.strategic_order = StrategicOrder(
            command_type="HOLD", target=soult.location, target_type="region",
            started_turn=int(world.current_turn) - 1, issued_turn=int(world.current_turn) - 1,
            original_command="Soult, hold Lorraine")
        with _quiet():
            jealousy.update_literal_hold_counters(world)
        assert soult.consecutive_hold_turns == 1, "staying put is not being given work"


# ═══════════════════ the order card's other choices ═════════════════════════

@pytest.fixture(scope="module")
def road():
    """The shipped 1805 board behind the real app and the mock parser (the
    pattern of `tests/test_ic8_the_line.py`)."""
    import backend.main as M
    from backend.commands import parse_preview as PP
    from fastapi.testclient import TestClient
    mp = pytest.MonkeyPatch()
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        mp.delenv(key, raising=False)
    mp.setenv("LLM_MODE", "mock")
    prior = (M.world, M.game_state.get("world"), M.parser)
    with _quiet():
        M._reset_world_state()
    snap = json.dumps(M.world.to_dict(), default=str)
    try:
        with TestClient(M.app) as client:
            yield client, snap
    finally:
        M.world, M.parser = prior[0], prior[2]
        M.game_state["world"] = prior[1]
        PP.invalidate()
        mp.undo()


def _board(snap, tweak=None) -> WorldState:
    import backend.main as M
    from backend.commands import parse_preview as PP
    with _quiet():
        world = WorldState.from_dict(json.loads(snap))
        if tweak is not None:
            tweak(world)
        M._set_active_world(world)
        M.parser = CommandParser(use_real_llm=False)
    PP.invalidate()
    return world


def _quote(client, **params):
    with _quiet():
        return client.get("/march_quotes", params=params).json()


def _post(client, line, **body):
    random.seed(1805)
    with _quiet():
        return client.post("/command", json={"command": line, **body}).json()


def _blood_up(world):
    world.marshals["Murat"].recklessness = 3


def _alts(client, who, foe="Mack"):
    return {row["id"]: row for row in _quote(client, marshal=who, enemy=foe)["quote"]["alts"]}


class TestTheEnemyCardsOtherChoices:
    """The card that opens on an enemy quoted the attack and nothing else: a
    pursuit, the guns, a horseman's charge and an attack held back from it
    could only be typed (IC-V4)."""

    def test_any_corps_may_chase_him(self, road):
        client, snap = road
        _board(snap)
        alts = _alts(client, "Ney")
        assert list(alts) == ["pursue"], "foot with no guns: the pursuit only"
        assert alts["pursue"] == {"id": "pursue", "label": "Chase him", "ok": True, "ap": 2,
                                  "command": "Ney, pursue Mack", "turns": 0, "refusal": "",
                                  "note": ""}

    def test_a_man_who_follows_orders_to_the_letter_chases_for_one_action(self, road):
        client, snap = road
        _board(snap)
        assert _alts(client, "Soult")["pursue"]["ap"] == 1

    def test_horse_is_offered_the_charge_greyed_with_the_executors_reason(self, road):
        client, snap = road
        _board(snap)
        alts = _alts(client, "Murat")
        assert list(alts) == ["pursue", "charge"]
        assert alts["charge"]["ok"] is False
        assert alts["charge"]["refusal"] == "he needs one victory as the attacker first"

    def test_blood_up_offers_the_charge_and_the_attack_held_back(self, road):
        client, snap = road
        _board(snap, _blood_up)
        alts = _alts(client, "Murat")
        assert list(alts) == ["pursue", "charge", "held_back"]
        assert alts["charge"]["ok"] and alts["charge"]["ap"] == 1
        assert alts["held_back"]["ok"] and alts["held_back"]["ap"] == 1
        assert alts["held_back"]["command"] == "Murat, attack Mack, held back"
        assert alts["held_back"]["note"] == "held back from the charge"

    def test_a_gun_corps_is_offered_the_bombardment(self, road):
        client, snap = road

        def guns(world):
            world.marshals["Ney"].artillery = True
        _board(snap, guns)
        alts = _alts(client, "Ney")
        assert "bombard" in alts and alts["bombard"]["command"] == "Ney, bombard Mack"
        assert alts["bombard"]["ok"] and alts["bombard"]["ap"] == 1

    def test_a_row_is_the_line_the_command_road_takes_or_refuses(self, road):
        """A button is priced and greyed by the reader the typed line meets."""
        client, snap = road
        import backend.main as M
        for who, tweak in (("Ney", None), ("Murat", None), ("Murat", _blood_up)):
            _board(snap, tweak)
            for row in _alts(client, who).values():
                board = _board(snap, tweak)
                before = int(board.actions_remaining)
                reply = _post(client, row["command"])
                went = bool(reply.get("success")) or bool(reply.get("pending_glorious_charge"))
                assert went == row["ok"], (who, row, reply.get("message"))
                if (row["ok"] and reply.get("success")
                        and reply.get("state") != "awaiting_player_choice"):
                    assert before - int(M.world.actions_remaining) == row["ap"], (who, row)

    def test_the_quote_itself_is_the_attack_as_before(self, road):
        client, snap = road
        _board(snap)
        quote = _quote(client, marshal="Ney", enemy="Mack")["quote"]
        assert quote["kind"] == "attack" and quote["command"] == "Ney, attack Mack" and quote["ok"]

    def test_the_rows_spend_nothing(self, road):
        client, snap = road
        board = _board(snap, _blood_up)
        before = json.dumps(board.to_dict(), sort_keys=True, default=str)
        state = random.getstate()
        _alts(client, "Murat")
        _quote(client, marshal="Ney", dest="Lorraine")
        _quote(client, region="Swabia")
        assert random.getstate() == state
        assert json.dumps(board.to_dict(), sort_keys=True, default=str) == before


class TestTheAttackHeldBack:
    """ "Attack, held back": the restraint the player STARTS — the answer
    "restrain" to the question a reckless horseman's attack would ask, given
    beforehand. Only where that question would be asked."""

    def test_without_the_words_the_question_is_asked(self, road):
        client, snap = road
        board = _board(snap, _blood_up)
        reply = _post(client, "Murat, attack Mack")
        assert reply.get("pending_glorious_charge") is True
        assert board.marshals["Murat"].pending_glorious_charge is True

    def test_with_them_the_attack_goes_and_no_question_is_raised(self, road):
        client, snap = road
        board = _board(snap, _blood_up)
        mack = int(board.marshals["Mack"].strength)
        reply = _post(client, "Murat, attack Mack, held back")
        assert reply.get("success"), reply.get("message")
        assert not reply.get("pending_glorious_charge")
        assert board.marshals["Murat"].pending_glorious_charge is False
        assert reply.get("battle_report") or "MUSTER" in str(reply.get("message")), (
            "the attack is on its way — its muster, or its battle")
        assert int(board.marshals["Mack"].strength) <= mack
        assert int(board.marshals["Murat"].recklessness) >= 3, "held back, his blood stays up"

    def test_where_no_charge_is_in_question_the_words_change_nothing(self, road):
        from backend.commands import parse_preview as PP
        client, snap = road
        board = _board(snap)
        mack = int(board.marshals["Mack"].strength)
        with _quiet():
            reading = client.get("/parse_preview",
                                 params={"line": "Ney, attack Mack, held back"}).json()
        rows = [p for p in reading["parts"] if p.get("role") == "nottaken"]
        assert rows == [{"role": "nottaken", "blocks": False,
                         "text": "‘held back’ — no cavalry that would charge unasked — "
                                 "order the attack"}]
        assert reading["understood"] == "" and reading["kind"] == "order"
        PP.invalidate()
        board = _board(snap)
        reply = _post(client, "Ney, attack Mack, held back", typed=True)
        assert reply.get("success") or reply.get("state") == "awaiting_player_choice"
        assert "restrained" not in str(reply.get("message"))
        assert not board.marshals["Ney"].pending_glorious_charge
        assert int(board.marshals["Mack"].strength) <= mack

    def test_the_words_stand_at_the_end_of_the_line_behind_the_enemy(self, road):
        """The review, L2: a remark about somebody else is no such word."""
        from backend.commands import if_thens as IT
        names = ["Mack", "ArchdukeCharles"]
        for line in ("Murat, attack Mack, held back", "Murat, attack Mack held back.",
                     "Murat, attack Mack without charging",
                     "Murat, attack Archduke Charles, held back"):
            assert IT.held_back_in(line, names) is True, line
        for line in ("Murat, attack Mack, Soult is holding back",
                     "Murat, attack Mack — the reserve is held back",
                     "Murat, held back, attack Mack", "Murat, attack Mack", ""):
            assert IT.held_back_in(line, names) is False, line
        client, snap = road
        _board(snap, _blood_up)
        reply = _post(client, "Murat, attack Mack, Soult is holding back")
        assert reply.get("pending_glorious_charge") is True, "the question is still asked"

    def test_the_reader_is_one(self, world1805):
        from backend.commands import tactical_executor as T
        world = _fresh(world1805)
        murat, ney = world.marshals["Murat"], world.marshals["Ney"]
        assert T.restrain_refusal(world, ney, "Mack")[1] == (
            "no cavalry that would charge unasked — order the attack")
        assert T.restrain_refusal(world, murat, "Mack")[1] == (
            "his cavalry is not about to charge — order the attack")
        murat.recklessness = 4
        assert T.restrain_refusal(world, murat, "Mack")[1] == (
            "his cavalry is past holding back — it will charge")
        murat.recklessness = T.RESTRAIN_AT
        assert T.restrain_refusal(world, murat, "Mack") == ("", "")
        assert T.restrain_refusal(world, murat, "Nobody")[1] == "name an enemy in sight"
        world.actions_remaining = 0
        assert T.restrain_refusal(world, murat, "Mack")[1] == "no military action left this turn"

    def test_restrain_alone_is_still_the_questions_answer(self, road):
        client, snap = road
        _board(snap, _blood_up)
        reply = _post(client, "Murat, restrain")
        assert reply.get("success") is False
        assert "No pending Glorious Charge to restrain" in reply["message"]


class TestAMarchsThen:
    """What he does on arrival was typed or nothing: the march card's pick."""

    def test_the_four_arrival_verbs_each_its_own_line(self, road):
        client, snap = road
        _board(snap)
        thens = _quote(client, marshal="Ney", dest="Lorraine")["quote"]["thens"]
        assert [(t["id"], t["label"], t["command"]) for t in thens] == [
            ("then:hold", "then hold", "Ney, march to Lorraine then hold"),
            ("then:fortify", "then dig in", "Ney, march to Lorraine then fortify"),
            ("then:drill", "then drill", "Ney, march to Lorraine then drill"),
            ("then:defend", "then stand", "Ney, march to Lorraine then defend"),
        ]
        assert all(t["ok"] for t in thens)

    def test_they_are_the_word_tables_arrival_verbs(self):
        from backend.ai import task_words as TW
        from backend.commands import order_quotes as OQ
        assert {verb for verb, _label in OQ.MARCH_THENS} == set(TW.ARRIVAL_THENS.values())

    def test_each_is_taken_by_the_command_road_and_done_on_arrival(self, road):
        client, snap = road
        _board(snap)
        thens = _quote(client, marshal="Ney", dest="Lorraine")["quote"]["thens"]
        for then in thens:
            board = _board(snap)
            reply = _post(client, then["command"])
            assert reply.get("success") or reply.get("state") == "awaiting_player_choice", (
                then, reply.get("message"))
            if reply.get("state") == "awaiting_player_choice":
                continue
            ney = board.marshals["Ney"]
            assert ney.location == "Lorraine", then
            if then["id"] == "then:fortify":
                assert ney.fortified
            if then["id"] == "then:hold":
                assert ney.strategic_order and ney.strategic_order.command_type == "HOLD"

    def test_no_pick_where_the_march_itself_is_refused(self, road):
        client, snap = road
        _board(snap)
        quote = _quote(client, marshal="Ney", dest="Rhineland")["quote"]
        assert "thens" not in quote, "he already stands there"


class TestLookAtIt:
    """ "Look at Swabia": a click on a province a corps of ours can look into."""

    def test_the_corps_within_scout_range_are_listed_nearest_first(self, road):
        client, snap = road
        board = _board(snap)
        rows = _quote(client, region="Swabia")["look"]
        assert rows and len(rows) <= 4
        assert [r["marches"] for r in rows] == sorted(r["marches"] for r in rows)
        for row in rows:
            marshal = board.marshals[row["marshal"]]
            assert marshal.location != "Swabia" and row["ok"] and row["ap"] == 1
            assert row["command"] == f"{row['shown']}, scout Swabia"
            assert row["label"] == f"{row['shown']}: look at Swabia"

    def test_a_corps_too_far_is_not_listed(self, road):
        from backend.commands.movement_executor import scout_range
        client, snap = road
        board = _board(snap)
        listed = {r["marshal"] for r in _quote(client, region="Paris")["look"]}
        for marshal in board.get_player_marshals():
            gap = board.get_distance(marshal.location, "Paris")
            within = isinstance(gap, int) and 1 <= gap <= scout_range(marshal)
            assert (marshal.name in listed) == within or len(listed) == 4

    def test_a_scout_his_state_refuses_is_greyed_with_the_reason(self, road):
        client, snap = road

        def spent(world):
            world.actions_remaining = 0
        _board(snap, spent)
        rows = _quote(client, region="Swabia")["look"]
        assert rows and all(not r["ok"] and r["refusal"] == "no military action left this turn"
                            for r in rows)

    def test_a_row_is_the_scout_the_command_road_takes(self, road):
        client, snap = road
        _board(snap)
        row = _quote(client, region="Swabia")["look"][0]
        board = _board(snap)
        before = int(board.actions_remaining)
        reply = _post(client, row["command"])
        assert reply.get("success"), reply.get("message")
        assert before - int(board.actions_remaining) == row["ap"]

    def test_only_the_players_corps(self, road):
        client, snap = road
        board = _board(snap)
        for region in ("Swabia", "Tyrol", "Franconia"):
            for row in _quote(client, region=region)["look"]:
                assert board.marshals[row["marshal"]].nation == board.player_nation


# ═══════════════════ the group's orders ═════════════════════════════════════

def _list_of(client, line):
    with _quiet():
        return client.get("/directive_quote", params={"line": line}).json()


class TestTheGroupsOrders:
    """The group face had Hold…, Fortify… and Drill…: an attack, a support, a
    fall back and a garrison for several could only be typed (IC-V4). Support
    and garrison were lists already; a fall back is one now; an attack by
    several is ONE battle — the first man leads and the muster calls the
    others — so "Attack…" opens the lead's attack card."""

    def test_a_named_list_falls_back_man_by_man_on_one_list(self, road):
        client, snap = road
        board = _board(snap)
        line = "Ney, Davout and Lannes, fall back"
        got = _list_of(client, line)
        assert got["success"], got.get("message")
        rows = got["directive"]["rows"]
        assert [(r["marshal"], r["ok"], r["ap"], r["says"]) for r in rows] == [
            ("Ney", True, 0, "fall back"), ("Davout", True, 0, "fall back"),
            ("Lannes", True, 0, "fall back")]
        before = {n: board.marshals[n].location for n in ("Ney", "Davout", "Lannes")}
        reply = _post(client, line, members=["Ney", "Davout", "Lannes"], expect_ap=0,
                      list_first=True)
        assert reply.get("success"), reply.get("message")
        assert all(board.marshals[n].location != before[n] for n in before)

    def test_a_man_who_is_in_no_danger_is_a_row_that_cannot_go(self, road):
        client, snap = road

        def far_from_the_enemy(world):
            world.marshals["Davout"].location = "Paris"
            world._build_marshal_index()
        _board(snap, far_from_the_enemy)
        rows = {r["marshal"]: r for r in
                _list_of(client, "Ney and Davout, fall back")["directive"]["rows"]}
        assert rows["Ney"]["ok"] is True
        assert rows["Davout"]["ok"] is False and "not in danger" in rows["Davout"]["why"]

    def test_everyone_retreat_is_still_the_general_retreat(self, road):
        from backend.commands import group_orders as GO
        client, snap = road
        _board(snap)
        assert "retreat" not in GO.GROUPABLE_ACTIONS and GO.NAMED_ONLY == {"retreat"}
        assert _list_of(client, "everyone retreat")["success"] is False
        reply = _post(client, "everyone retreat")
        assert "directive" not in reply or not reply.get("directive")

    @pytest.mark.parametrize("line, says", [
        ("Ney, Davout and Soult, support Lannes", "support Lannes"),
        ("Ney, Davout and Soult, garrison", ""),
        ("Ney, Davout and Soult, hold", "hold"),
    ])
    def test_the_groups_other_buttons_open_a_list(self, road, line, says):
        client, snap = road
        _board(snap)
        got = _list_of(client, line)
        assert got["success"], got.get("message")
        rows = got["directive"]["rows"]
        assert [r["marshal"] for r in rows] == ["Ney", "Davout", "Soult"]
        assert all(r["says"] == says for r in rows if r["ok"])

    def test_an_attack_by_several_is_one_battle(self, road):
        """No list: the lead's attack card says who answers the guns."""
        client, snap = road
        _board(snap)
        assert _list_of(client, "Ney, Davout and Soult, attack Mack")["success"] is False
        quote = _quote(client, marshal="Ney", enemy="Mack")["quote"]
        assert quote["ok"] and quote["muster"], "the card says who would join"


# ═══════════════════ the client's ONE table (IC-V4) ═════════════════════════

import re  # noqa: E402

SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
_ROW_RE = re.compile(
    r'\{"id": "(?P<id>[^"]+)", "where": "(?P<where>[^"]+)"(?:, "verb": "(?P<verb>[^"]+)")?,'
    r'\s*"label": "(?P<label>[^"]+)",\s*"line": "(?P<line>[^"]*)",\s*"price": "(?P<price>[^"]+)"')


def _src(name: str) -> str:
    return (SCRIPTS / name).read_text(encoding="utf-8").replace("\r\n", "\n")


def _func(source: str, name: str) -> str:
    start = source.index("func " + name + "(")
    nxt = source.find("\nfunc ", start + 5)
    alt = source.find("\nstatic func ", start + 5)
    ends = [e for e in (nxt, alt) if e != -1]
    return source[start:min(ends)] if ends else source[start:]


def _table() -> list:
    rows = [m.groupdict() for m in _ROW_RE.finditer(_src("simple_orders.gd"))]
    assert rows, "simple_orders.gd: the table's rows were not read"
    return rows


class TestTheOneTable:
    """`SIMPLE_ORDER_BUTTONS` (scripts/simple_orders.gd): every simple order
    that had no button, seated in one table the card, the map's cards, the
    province panel, the group face and the Help page read (IC-V4)."""

    def test_it_seats_every_order_the_review_listed(self):
        ids = {row["id"] for row in _table()}
        assert {"stand", "stay_put", "posture", "task",                          # the card
                "posture_attacking", "posture_steady", "posture_defending",     # posture
                "form_square", "break_square",                                  # the square
                "pursue", "bombard", "charge", "held_back",                     # an enemy
                "then",                                                         # a march's "then"
                "look",                                                         # a named province
                "group_attack", "group_support", "group_retreat", "group_garrison"} == ids

    def test_a_card_buttons_price_and_refusal_are_the_state_probes(self):
        """`probe:<verb>` is a screen verb, `button:<key>` one of the new
        buttons — so each face is priced and greyed by the executor's reader."""
        for row in _table():
            price = row["price"]
            if price.startswith("probe:"):
                assert price[6:] in SP.VERBS, row
            elif price.startswith("button:"):
                assert price[7:] in SP.BUTTONS, row
            else:
                assert price in ("quote", "list", "none"), row
        covered = {row["price"][7:] for row in _table() if row["price"].startswith("button:")}
        assert covered == set(SP.BUTTONS), "every new server button has a row"

    def test_a_card_buttons_line_is_the_order_its_price_names(self, world1805):
        """What a press sends ("<Marshal>, <line>") parses to that very order."""
        want = {"stand": "defend", "stay_put": "wait", "posture_attacking": "stance_change",
                "posture_steady": "stance_change", "posture_defending": "stance_change",
                "form_square": "form_square", "break_square": "break_square"}
        stance = {"posture_attacking": "aggressive", "posture_steady": "neutral",
                  "posture_defending": "defensive"}
        world = _fresh(world1805)
        parser = CommandParser(use_real_llm=False)
        seen = 0
        for row in _table():
            if row["id"] not in want:
                continue
            seen += 1
            with _quiet():
                parsed = parser.parse(f"Davout, {row['line']}", {"world": world}, world=world)
            command = parsed.get("command") or {}
            assert parsed.get("success") and command.get("action") == want[row["id"]], row
            assert command.get("marshal") == "Davout" and not parsed.get("is_strategic"), row
            if row["id"] in stance:
                said = str(command.get("target_stance") or command.get("target") or "").lower()
                assert said.startswith(stance[row["id"]][:6]), (row, command)
        assert seen == len(want)

    def test_the_enemy_rows_are_the_servers_alternatives(self):
        from backend.commands import order_quotes as OQ
        enemy = [row for row in _table() if row["where"] == "enemy"]
        assert [row["id"] for row in enemy] == [key for key, _label, _verb in OQ.ENEMY_ALTS]
        assert [row["label"] for row in enemy] == [label for _key, label, _verb in OQ.ENEMY_ALTS]

    def test_the_group_rows_are_the_verbs_the_face_sends(self):
        group = {row["verb"]: row["label"] for row in _table() if row["where"] == "group"}
        assert group == {"attack": "Attack…", "support": "Support…", "retreat": "Fall back…",
                         "garrison": "Garrison…"}
        card = _src("selection_card.gd")
        row = _func(card, "_group_buttons_row")
        assert 'for entry in SimpleOrders.rows("group"):' in row
        assert '_emit_group_verb.bind(str(entry["verb"]))' in row
        main = _src("main.gd")
        verb = _func(main, "_on_group_verb")
        assert 'if verb == "attack" or verb == "support":' in verb and "_group_pick = verb" in verb
        pick = _func(main, "_group_pick_resolve")
        assert '_open_order_card(target)' in pick, "an attack by several opens the LEAD's card"
        assert '", support "' in pick and "_open_directive_line(" in pick

    def test_the_card_draws_the_tables_rows_under_the_seven_slots(self):
        card = _src("selection_card.gd")
        assert 'const SimpleOrders = preload("res://scripts/simple_orders.gd")' in card
        render = _func(card, "_render")
        assert render.index("_body.add_child(_order_row(compact))") < render.index(
            "_body.add_child(_simple_row(compact))")
        simple = _func(card, "_simple_row")
        assert 'for entry in SimpleOrders.rows("card"):' in simple
        button = _func(card, "_order_button")
        assert "SimpleOrders.price_of(entry, _view)" in button
        assert "SimpleOrders.refusal_of(entry, _view)" in button
        made = _func(card, "_simple_button")
        assert 'btn.disabled = reason != ""' in made, "refused = greyed, with the reason as hover"
        assert "btn.tooltip_text = Utils.clean_tip(tip)" in made
        # a press sends "<Marshal>, <line>" down the slots' own road
        assert "verb_pressed.emit(line, _marshal)" in _func(card, "_fire_line")
        # the seven digit slots are untouched
        assert len(re.findall(r'\{"slot": \d', _src("marshal_state.gd"))) == 7

    def test_the_hold_slot_says_hold_the_ground_on_the_card_only(self):
        kit = _src("marshal_state.gd")
        assert '"label": "Hold", "glyph": "defense", "card_label": "Hold the ground"' in kit
        assert 'var label := str(spec.get("card_label", spec["label"]))' in _func(
            _src("selection_card.gd"), "_slot_button")

    def test_stay_put_is_read_by_both_idle_readers(self):
        assert 'if bool(ts.get("stay_put", false)):' in _func(_src("main.gd"), "_idle_marshals")
        assert 'if bool(view.get("stay_put", false)):' in _func(_src("marshal_state.gd"), "is_idle")
        board = _func(_src("marshal_state.gd"), "from_board")
        assert '"buttons": _dict_of(ts.get("buttons", {}))' in board
        assert '"stay_put": bool(ts.get("stay_put", false))' in board

    def test_the_cards_show_the_quotes_other_rows(self):
        card = _src("order_confirm_card.gd")
        terms = _func(card, "_terms")
        assert terms.count("lines.append_array(_alt_lines(q))") == 2, "refused quote and ok quote"
        assert terms.rindex("_alt_lines(q)") > terms.index('q.get("terms", "")'), \
            "after every line the card already printed"
        alts = _func(card, "_alt_lines")
        assert 'for key in ["alts", "thens"]:' in alts
        assert 'Utils.bb_button_chip("do:" + str(a.get("command", "")), label,' in alts
        assert "Utils.bb_chip_disabled(" in alts
        # each chip's hover says what its order does, in the one table's words
        assert 'SimpleOrders.row(str(a.get("id", "")).get_slice(":", 0)).get("tip", "")' in alts
        assert 'Utils.COLOR_GOLD, BRING_CHIP_BG, "", tip))' in alts
        panel = _src("region_panel.gd")
        assert 'out += _look_rows(_quotes.get("look", []))' in _func(panel, "_march_here_section")
        assert 'Utils.bb_button_chip("do:" + str(r.get("command", "")), label,' in _func(
            panel, "_look_rows")

    def test_the_help_says_what_is_true(self):
        """IC-V4: the Orders page said the map's clicks "give the same orders"."""
        codex = _src("codex_view.gd")
        assert "the map's clicks give the same orders" not in codex
        assert ("Simple orders are buttons — on a general's card and on the map's cards (right-click a "
                "province to see a march's card first). A task — an order with a time limit, a condition "
                "or an if-then — is typed") in codex
        # ... and the right click does open it: the march's "then" is always one gesture away
        click = _func(_src("main.gd"), "_order_click")
        assert ('if via_right and key.begins_with("dest:"):\n\t\t_open_order_card(key)\n\t\treturn'
                in click)
        assert click.index("if via_right and key.begins_with") < click.index("\t_order_go(key)\n"), (
            "the left click still sends a plain march at once")
        assert "for entry in CodexTerms.TASKS:" in _func(codex, "_page_orders")

    def test_every_sentence_the_help_teaches_is_one_the_census_runs(self):
        from backend.ai import task_words as TW
        terms = _src("codex_terms.gd")
        block = terms[terms.index("const TASKS: Array = ["):terms.index("# Commands with no marshal.")]
        said = re.findall(r'^\t\["([^"]+)",', block, re.MULTILINE)
        assert said == list(TW.EXAMPLES), "the page's sentences are the word table's examples"


class TestTheTypedLinesClientHalf:
    """IC-8 on the client: the command window alone says a line was typed;
    Enter sends the line as understood; the read-back draws labelled lines."""

    def test_only_the_command_window_marks_a_line_typed(self):
        main = _src("main.gd")
        assert main.count("api_client.typed_line = true") == 1
        execute = _func(main, "_execute_command")
        assert execute.index("api_client.typed_line = true") < execute.index(
            "api_client.send_command(command, _on_command_result, relayed)")
        client = _src("api_client.gd")
        send = _func(client, "send_command")
        assert 'if typed_line:\n\t\tbody["typed"] = true\n\ttyped_line = false' in send
        assert client.count('body["typed"] = true') == 1, "no other sender can say it"

    def test_enter_sends_the_line_as_understood(self):
        execute = _func(_src("main.gd"), "_execute_command")
        read = "var understood := _readback_understood(command_input.text.strip_edges())"
        assert execute.index("if _order_card_open():") < execute.index(read) < execute.index(
            "_readback_cancel()"), "read BEFORE the reading is let go"
        assert 'if understood != "" and understood != command:' in execute
        assert execute.index("command = understood") < execute.index("_add_to_history(command)")
        reader = _func(_src("main.gd"), "_readback_understood")
        assert 'str(_readback_last.get("line", "")).strip_edges() != line' in reader

    def test_a_held_line_comes_back_on_the_command_line(self):
        main = _src("main.gd")
        assert "_stash_understood(response)  # row IC, Session 2 (IC-8)" in _func(
            main, "_stash_pending_surfaces")
        enabled = _func(main, "set_input_enabled")
        assert enabled.index("_fill_pending_relay()") < enabled.index(
            "_fill_pending_understood()") < enabled.index("_fill_pending_remedy()")
        fill = _func(main, "_fill_pending_understood")
        assert "send_command" not in fill and "_execute_command" not in fill, "never sent"
        assert 'pending_understood_command = ""  # row IC, Session 2' in _func(
            main, "_clear_pending_surfaces")

    def test_the_read_back_draws_its_rows_on_their_own_lines(self):
        main = _src("main.gd")
        render = _func(main, "_readback_render")
        assert 'if role == "taken" or role == "nottaken" or role == "answer":\n\t\t\t\tcontinue' in render
        assert "+ _readback_task_lines(resp))" in render
        rows = _func(main, "_readback_task_lines")
        for label in ('"Taken: "', '"Not taken: "', '"He says: "', '"Enter sends: "'):
            assert label in rows, label
        # "Not taken" is never folded: it is no `note` part, and no fold reads it
        assert "explanations_folded" not in rows

    def test_give_him_a_task_writes_and_never_sends(self):
        main = _src("main.gd")
        task = _func(main, "_on_task_presets")
        assert "_selection_card.show_tasks(marshal, presets)" in task
        # the review, C1: nothing is written unasked — writing on the line lets
        # the selection go, and the card closed with the other tasks unread
        assert "_write_on_the_line" not in task and "command_input" not in task
        write = _func(main, "_write_on_the_line")
        assert "send_command" not in write and "_execute_command" not in write
        assert '["task_pressed", _on_selection_task], ["task_line_pressed", _write_on_the_line]' in main
        assert "func get_task_presets(marshal_name: String, callback: Callable):" in _src("api_client.gd")

    def test_a_ready_task_wraps_inside_the_card_and_goes_with_its_board(self):
        """The review, C2 and C4."""
        card = _src("selection_card.gd")
        rows = _func(card, "_task_rows")
        assert "btn.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART" in rows
        assert "btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL" in rows
        assert "_emit_task_line.bind(line)" in rows
        show = _func(card, "show_for")
        assert "if marshal != _tasks_for or actions_left != _actions_left:" in show
        for name in ("hide_card", "show_group"):
            body = _func(card, name)
            assert "_tasks = []" in body and '_tasks_for = ""' in body, name
            assert "_posture_open = false" in body, name

    def test_the_second_looks_rows(self):
        """One more reader went over the fixes made AFTER the review: no P1,
        three small faults fixed (IC2-R21 … IC2-R23)."""
        main = _src("main.gd")
        pick = _func(main, "_group_pick_resolve")
        # a wrong click leaves the pick waiting, as its toast says
        assert pick.count("_group_pick = pick") == 2
        assert pick.index("_group_pick = pick") < pick.index('"Click an enemy corps in sight to attack."')
        # a late answer for a man the card has left is dropped whole
        presets = _func(main, "_on_task_presets")
        assert "str(_selection_card.current_marshal()) != marshal" in presets
        assert presets.index("current_marshal()") < presets.index("_on_first_open_seen")
        # an order given from the card puts its menus away, a free one too
        card = _src("selection_card.gd")
        away = _func(card, "_put_menus_away")
        assert "_posture_open = false" in away and "_tasks = []" in away and '_tasks_for = ""' in away
        assert "_put_menus_away()" in _func(card, "_fire") and "_put_menus_away()" in _func(card, "_fire_line")

    def test_a_group_pick_never_outlives_the_press_that_made_it(self):
        """The review, C3: "Attack…" then "Hold…" — the next click on the map
        was still read as the attack's."""
        main = _src("main.gd")
        verb = _func(main, "_on_group_verb")
        assert verb.index('_group_pick = ""') < verb.index("if _order_group.size() < 2")
        for name in ("_set_order_group", "_select_marshal", "_clear_order_selection"):
            assert '_group_pick = ""' in _func(main, name), name
        click = _func(main, "_group_click")
        assert click.index('_group_pick = ""') < click.index("_group_pick_resolve(")

    def test_a_desk_row_about_an_exact_order_writes_its_sentence(self):
        door = _func(_src("main.gd"), "_ic_open_door")
        assert '_write_on_the_line(str(door.get("line", "")))' in door

    def test_the_standing_card_says_how_many_lines_are_left(self):
        head = _func(_src("order_confirm_card.gd"), "standing_headline")
        assert 'var left := str(info.get("watch_left", ""))' in head
        assert 'watch += " (" + left + ")"' in head
