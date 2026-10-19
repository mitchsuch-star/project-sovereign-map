"""ACH-1 — THE REPLY SAYS WHAT THE ORDER COST (October 19, 2026; found in
passing by Pre-Deploy S13c part 4, CC-4; the record is `docs/BUG_FIXES.md`
§ACH-1, the rule `docs/SYSTEMS_REFERENCE.md` §131).

Measured on the shipped 1805 boot through the real `POST /command`: every
strategic order that costs two actions replied `action_info.cost: 1` while
the pool fell by 2. The executor's charge loop kept only its LAST
`use_action` reply. The client printed nothing wrong (it gates its actions
line on `cost > 0` and prints `remaining`), but every reader that trusts the
field — the School's lesson predicates, the tools, a digest — read a wrong
price. The sweep found the class on eleven roads: the post-objection road,
the strategic objection's tail, both defiance arms, the collective order and
its resume, the Orders tab's Cancel, the dialogue arms that spend actions
and the shared dialogue assembly, and the marshal petition's answers.

THE RULE: `WorldState.spend_actions` is the one charge — `times` uses of a
verb, `action_cost` = what the pool actually LOST — and every `action_info`
is `WorldState.get_action_info(<that reading>)`. Each pin below drives a
road and asserts `action_info.cost == before − after` (an absent `cost` is
read as 0, the client's own reading), and pins the price measured, so a
price that moves is re-seated on purpose.
"""

import contextlib
import io
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.commands.defiance as DEF
import backend.main as M
from backend.commands import executor as executor_mod
from backend.commands import group_orders as G
from backend.commands import objection_v2 as ov2
from backend.commands import strategic_executor as se_mod
from backend.commands.executor import CommandExecutor
from backend.game_logic import jealousy as J
from backend.game_logic import reforms
from backend.game_logic import vassal as V
from backend.game_logic.diplomacy import (
    create_war_bargain_commitment,
    set_diplomatic_state,
)
from backend.game_logic.diplomatic_advisory import generate_advisory
from backend.models.marshal import Stance
from backend.models.world_state import WorldState
from tests import _chip_census as C

REPO = Path(__file__).resolve().parents[1]
EUROPE = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
CORPUS = REPO / "tests" / "data" / "parser_golden_corpus.json"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


def _board(monkeypatch, *, defiance: float = 0.0) -> TestClient:
    """A fresh shipped 1805 board behind the real app: the mood roll flat
    (the one source of randomness in the objection triggers) and the
    Insist roll pinned — to obedience, unless a class asks for defiance."""
    C.board_env(monkeypatch)

    def flat(concern):
        return concern
    for mod in (executor_mod, se_mod, ov2):
        monkeypatch.setattr(mod, "apply_mood_variance", flat)
    monkeypatch.setattr(DEF, "calculate_defiance_chance", lambda *a, **k: defiance)
    client = TestClient(M.app)
    with _quiet():
        client.post("/new_game")
    return client


@pytest.fixture
def client(monkeypatch):
    return _board(monkeypatch)


@pytest.fixture
def defiant(monkeypatch):
    return _board(monkeypatch, defiance=1.0)


def _post(client, path, body):
    """POST and read what the pools gave: (reply, military spent, admin spent)."""
    world = M.world
    mil, adm = int(world.actions_remaining), int(world.admin_actions_remaining)
    with _quiet():
        reply = client.post(path, json=body).json()
    assert M.world is world, "the board changed under the measure"
    return (reply, mil - int(world.actions_remaining),
            adm - int(world.admin_actions_remaining))


def _order(client, line):
    return _post(client, "/command", {"command": line})


def _said(reply) -> int:
    """The price a reply says. No `action_info`, or none with a `cost`,
    says 0 — `main.gd` `_show_action_cost`'s own reading."""
    info = reply.get("action_info")
    return int(info.get("cost") or 0) if isinstance(info, dict) else 0


def _honest(reply, spent, line=""):
    assert _said(reply) == spent, (
        f"{line!r}: the reply says {_said(reply)}, the pool gave {spent} — "
        f"{str(reply.get('message') or '')[:160]!r}")


def _interrupt_answer(client, choice=None):
    for marshal in M.world.get_player_marshals():
        pending = getattr(marshal, "pending_interrupt", None)
        if pending:
            return _post(client, "/strategic_response", {
                "marshal_name": pending.get("marshal", ""),
                "response_type": pending.get("interrupt_type", ""),
                "choice": choice or (pending.get("options") or ["hold_position"])[0]})
    raise AssertionError("no interrupt stands")


# ═══════════════════════════════════════════════════════════════════════
# ACH-1 — every order type says its price
# ═══════════════════════════════════════════════════════════════════════

class TestEveryOrderSaysItsPrice:
    """The row: the reply's `cost` is the actions the order took. The price
    column is the measured price on the boot board (a moved price is
    re-seated on purpose, never by accident)."""

    @pytest.mark.parametrize("line,price", [
        # The standing orders — 2 for a marshal who is neither literal nor
        # the sovereign (`Marshal.strategic_order_ap`). Every one said 1.
        ("Ney, hold", 2),
        ("Ney, hold Rhineland", 2),
        ("Davout, hold", 2),
        ("Ney, march to Lorraine", 2),
        ("Ney, march to Lorraine then fortify", 2),
        ("Ney, if Mack advances fall back to Lorraine", 2),
        ("Ney, if the enemy comes within reach, attack", 2),
        ("Ney, pursue Mack", 2),
        ("Davout, hold Rhineland and wait", 2),
        # The one-action tiers, which always read true.
        ("Soult, march to Burgundy", 1),
        ("Soult, march to Burgundy then fortify", 1),
        ("Napoleon, march to Burgundy", 1),
        ("Davout, support Ney", 1),
        ("Soult, follow Ney", 1),
        # A march whose first step meets Mack asks before it walks, at the
        # first-step interrupt's own price.
        ("Ney, march to Swabia", 1),
        # The tactical verbs.
        ("Ney, attack Mack", 1),
        ("Ney, scout Swabia", 1),
        ("Ney, move to Lorraine", 1),
        ("Soult, defend", 1),
        ("Soult, form square", 1),
        ("Ney, aggressive stance", 1),
        ("Davout, fortify", 2),
        ("Ney, retreat", 0),
        ("Soult, wait", 0),
    ])
    def test_the_reply_says_what_the_pool_gave(self, client, line, price):
        reply, spent, _adm = _order(client, line)
        assert reply.get("success"), (line, reply.get("message"))
        assert spent == price, (line, spent)
        _honest(reply, spent, line)

    def test_the_rows_own_line(self, client):
        """`Ney, hold` on the boot: before 4, after 2 — and `cost: 2`."""
        reply, spent, _ = _order(client, "Ney, hold")
        assert (spent, reply["action_info"]["cost"],
                reply["action_info"]["remaining"]) == (2, 2, 2)


# ═══════════════════════════════════════════════════════════════════════
# ACH-1 — the variable costs (`variable_action_cost`)
# ═══════════════════════════════════════════════════════════════════════

def _stance(name, stance):
    def setup(world):
        world.get_marshal(name).stance = stance
    return setup


def _fortified(name):
    def setup(world):
        marshal = world.get_marshal(name)
        marshal.fortified = True
        marshal.stance = Stance.DEFENSIVE
    return setup


def _square(name):
    def setup(world):
        world.get_marshal(name).square_formation = True
    return setup


def _counter_punch(name):
    def setup(world):
        marshal = world.get_marshal(name)
        marshal.counter_punch_available = True
        marshal.counter_punch_turns = 1
    return setup


def _armed(name):
    def setup(world):
        world.get_marshal(name).recklessness = 1
    return setup


def _a_garrison_freed(world):
    for name in world.get_nation_regions(world.player_nation):
        region = world.regions[name]
        if region.garrison_strength > 0 and name != "Rhineland":
            region.garrison_strength = 0
            return
    raise AssertionError("the boot holds no garrison to free")


def _far_from_mack(world):
    world.get_marshal("Soult").location = "Brittany"


class TestTheVariableCostsSayTheirPrice:

    @pytest.mark.parametrize("label,setup,line,price", [
        ("a two-step stance shift", _stance("Ney", Stance.AGGRESSIVE), "Ney, defensive stance", 2),
        ("a free return to neutral", _stance("Ney", Stance.DEFENSIVE), "Ney, neutral stance", 0),
        ("a fortify from defensive", _stance("Davout", Stance.DEFENSIVE), "Davout, fortify", 1),
        ("a defend from aggressive", _stance("Soult", Stance.AGGRESSIVE), "Soult, defend", 2),
        ("the free unfortify", _fortified("Davout"), "Davout, unfortify", 0),
        ("the free square break", _square("Soult"), "Soult, break square", 0),
        ("a garrison detached", _a_garrison_freed, "Ney, garrison Rhineland", 2),
        ("an armed charge", _armed("Murat"), "Murat, charge Mack", 1),
        ("the counter-punch's free strike", _counter_punch("Davout"), "Davout, attack Mack", 0),
        ("a drill out of Mack's reach", _far_from_mack, "Soult, drill", 1),
    ])
    def test_the_reply_says_the_variable_price(self, client, label, setup, line, price):
        setup(M.world)
        reply, spent, _adm = _order(client, line)
        assert reply.get("success"), (label, reply.get("message"))
        assert spent == price, (label, spent)
        _honest(reply, spent, label)

    def test_a_fleet_posture_says_its_price(self, client):
        M.world.nation_gold[M.world.player_nation] = 50000
        reply, spent, _ = _order(client, "blockade Britain")
        assert reply.get("success"), reply.get("message")
        assert spent == 1
        _honest(reply, spent)


class TestTheAdminPoolSaysItsPrice:
    """An administrative act spends the admin pool, and says so: `cost` is
    the admin action the charge took, the military pool untouched."""

    def test_a_build(self, client):
        reply, mil, adm = _order(client, "build fortress in Lorraine")
        assert reply.get("success"), reply.get("message")
        assert (mil, adm, _said(reply)) == (0, 1, 1)

    def test_a_commission(self, client):
        M.world.nation_gold[M.world.player_nation] = 50000
        reply, mil, adm = _order(client, "commission Grouchy")
        assert reply.get("success"), reply.get("message")
        assert (mil, adm, _said(reply)) == (0, 1, 1)

    def test_a_law_enacted_on_its_yes(self, client):
        M.world.nation_gold[M.world.player_nation] = 50000
        asked, mil, adm = _order(client, "enact the grand quartier general")
        assert (mil, adm, _said(asked)) == (0, 0, 0)
        reply, mil, adm = _order(client, "yes")
        assert reply.get("success"), reply.get("message")
        assert (mil, adm, _said(reply)) == (0, 1, 1)


# ═══════════════════════════════════════════════════════════════════════
# ACH-X1 … X3 — the answers to an objection say their price
# ═══════════════════════════════════════════════════════════════════════

class TestTheAnswersSayTheirPrice:

    @pytest.mark.parametrize("line,choice,price", [
        # Tactical objections (`_execute_post_objection`).
        ("Ney, fortify", "insist", 2),       # ACH-X1: said 1 — the stance shift first
        ("Ney, defend", "trust", 1),         # his alternative: the attack on Mack
        ("Ney, defend", "insist", 1),
        ("Ney, form square", "insist", 1),
        ("Ney, wait", "insist", 0),
        # Strategic objections (the objection's tail, ACH-X3).
        ("Davout, march to Swabia", "trust", 1),
        ("Davout, march to Swabia", "insist", 1),
        ("Davout, march to Swabia", "compromise", 1),
        ("Davout, pursue Mack", "insist", 2),
        ("Davout, support Bernadotte", "insist", 1),
        ("Davout, support Bernadotte", "compromise", 1),
        ("Davout, march to Swabia", "cancel", 0),
    ])
    def test_the_answer_says_what_it_spent(self, client, line, choice, price):
        asked, spent, _ = _order(client, line)
        assert M.world.pending_objection or M.world.pending_strategic_objection, \
            (line, asked.get("message"))
        assert spent == 0 and _said(asked) == 0, "an objection spends nothing"
        reply, spent, _ = _post(client, "/respond_to_objection", {"choice": choice})
        assert reply.get("success"), (line, choice, reply.get("message"))
        assert spent == price, (line, choice, spent)
        _honest(reply, spent, f"{line} -> {choice}")

    def test_a_short_pool_says_what_it_took(self, client):
        """ACH-X2: a strategic objection blocks nothing, so the pool can
        fall while it waits; the tail charges what is left (the clamp — a
        price question filed as ACH-F3, whose ruling re-seats the 1 here)
        and said the price it was asked: 2 for the 1 it took."""
        asked, _, _ = _order(client, "Davout, pursue Mack")
        assert M.world.pending_strategic_objection, asked.get("message")
        _order(client, "Ney, hold")
        _order(client, "Soult, march to Burgundy")
        assert M.world.actions_remaining == 1
        assert M.world.pending_strategic_objection, "the objection still waits"
        reply, spent, _ = _post(client, "/respond_to_objection", {"choice": "insist"})
        assert reply.get("success"), reply.get("message")
        assert spent == 1
        _honest(reply, spent, "Davout, pursue Mack -> insist at 1")

    @pytest.mark.parametrize("line,choice,price", [
        ("Ney, defend", "insist", 1),
        ("Davout, march to Swabia", "trust", 1),
    ])
    def test_a_typed_answer_says_the_same(self, client, line, choice, price):
        _order(client, line)
        reply, spent, _ = _order(client, choice)
        assert spent == price, (line, choice, spent)
        _honest(reply, spent, f"{line} -> typed {choice}")


class TestDefianceSaysWhatItTook:
    """ACH-X4: the defiance arms took an action and replied `action_info`
    with no `cost` at all — the sub-executor's reply carries none."""

    @pytest.mark.parametrize("line", ["Ney, defend", "Davout, march to Swabia"])
    def test_the_defiant_act_is_priced(self, defiant, line):
        _order(defiant, line)
        reply, spent, _ = _post(defiant, "/respond_to_objection", {"choice": "insist"})
        assert reply.get("defiance") or "Despite your insistence" in str(reply.get("message")), \
            reply.get("message")
        assert spent == 1
        _honest(reply, spent, line)
        assert "cost" in reply["action_info"]


# ═══════════════════════════════════════════════════════════════════════
# ACH-X5 / X6 — the collective order and its resume
# ═══════════════════════════════════════════════════════════════════════

def _staff_on(world):
    row = next(r for r in reforms.deck(world, world.player_nation) if reforms.is_staff(r))
    row["enacted_turn"] = world.current_turn
    assert reforms.staff_actions(world, world.player_nation) == 1


class TestTheArmySaysWhatItSpent:

    def test_the_fan_out_says_its_sum(self, client):
        """Said 0 while the corps spent the pool."""
        reply, spent, _ = _order(client, "all marshals march to Swabia")
        assert reply.get("success"), reply.get("message")
        assert spent >= 1
        _honest(reply, spent)

    def test_the_interrupt_that_resumes_it_says_the_corps_it_released(self, client):
        """The interrupt road's reply carried no `action_info` at all while
        the corps it released marched. Ney's first step meets Mack and asks;
        Soult alone is left waiting behind him (Davout would object next,
        and an objection spends nothing) — the literal marches without a
        question, at 1."""
        _order(client, "all marshals march to Swabia")
        assert M.world._pending_group and "Soult" in M.world._pending_group["members"]
        M.world._pending_group["members"] = ["Soult"]
        reply, spent, _ = _interrupt_answer(client, "hold_position")
        assert "The order goes on." in str(reply.get("message")), reply.get("message")
        assert spent == 1
        _honest(reply, spent)

    def test_the_answer_that_resumes_it_says_the_corps_it_released(self, client):
        """Ney's insisted fortify (2) and the corps behind his question
        — said 1, the pool gave 4."""
        asked, spent, _ = _order(client, "everyone fortify")
        assert M.world.pending_objection, asked.get("message")
        assert spent == 0 and _said(asked) == 0
        reply, spent, _ = _post(client, "/respond_to_objection", {"choice": "insist"})
        assert "The order goes on." in str(reply.get("message")), reply.get("message")
        assert spent > 2
        _honest(reply, spent)

    def test_the_army_order_says_the_staffs_price(self, client):
        _staff_on(M.world)
        reply, spent, _ = _order(client, "the army marches on Munich")
        assert str(reply.get("message")).startswith("The Grand Quartier"), reply.get("message")
        assert spent == G.ARMY_ORDER_AP
        _honest(reply, spent)


# ═══════════════════════════════════════════════════════════════════════
# ACH-X7 — the Orders tab's Cancel
# ═══════════════════════════════════════════════════════════════════════

class TestTheCancelSaysItsPrice:
    """Since CC-X15 the button's reply is read by `_on_command_result`; it
    carried no `action_info`, so the button printed no actions line where
    the typed cancel prints one."""

    def test_the_button(self, client):
        _order(client, "Ney, hold")
        reply, spent, _ = _post(client, "/cancel_order", {"marshal": "Ney"})
        assert reply.get("success"), reply.get("message")
        assert spent == 1
        _honest(reply, spent)

    def test_the_button_with_nothing_to_cancel(self, client):
        reply, spent, _ = _post(client, "/cancel_order", {"marshal": "Davout"})
        assert spent == 0
        assert reply["action_info"]["cost"] == 0

    def test_the_typed_cancel_agrees(self, client):
        _order(client, "Ney, hold")
        reply, spent, _ = _order(client, "Ney, cancel order")
        assert reply.get("success"), reply.get("message")
        assert spent == 1
        _honest(reply, spent)


# ═══════════════════════════════════════════════════════════════════════
# ACH-X8 / X9 — the letters that spend actions
# ═══════════════════════════════════════════════════════════════════════

def _raise_rebellion(world, vassal="Holland"):
    world.vassals[vassal]["loyalty"] = 9
    with _quiet():
        V.process_vassal_loyalty(world)
    current = world.dialogue_manager.peek()
    assert current and current.get("type") == "vassal_rebellion_imminent", current


class TestTheLettersSayTheirPrice:

    @pytest.mark.parametrize("answer", ["garrison", "2"])
    def test_showing_the_flag_typed(self, client, answer):
        """`/command` read `{}` for the word and nothing at all for the
        digit (the shared dialogue assembly dropped the arm's reply)."""
        _raise_rebellion(M.world)
        reply, spent, _ = _order(client, answer)
        assert reply.get("success"), reply.get("message")
        assert spent == 2
        _honest(reply, spent, answer)

    def test_the_repudiation(self):
        world = WorldState()
        world.enemy_nations = ["Austria", "Prussia", "Britain", "Russia", "Saxony"]
        world.diplomatic_states, world.active_treaties, world.vassals = {}, {}, {}
        world.diplomatic_commitments, world.next_commitment_id = {}, 1
        world.diplomatic_reliability = {"France": 50, "Prussia": 50, "Britain": 50}
        world.betrayal_history, world.nation_relations = {}, {}
        world.current_turn = 5
        set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
        world.active_treaties[world._make_diplo_key("France", "Prussia")] = {
            "nations": ["France", "Prussia"], "type": "alliance", "clauses": [],
            "turn_signed": 4}
        set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
        create_war_bargain_commitment(
            world, "France", "Prussia", "Britain", "Hanover", "treaty_clause",
            world._make_diplo_key("France", "Prussia"))
        world.actions_remaining = 2
        executor = CommandExecutor()
        staged = executor._diplomatic._execute_repudiate_bargain(
            {"action": "repudiate_bargain", "target_nation": "Prussia"}, world)
        assert staged.get("no_action_cost") is True
        before = int(world.actions_remaining)
        result = executor.handle_diplomatic_dialogue_response(1, {"world": world})
        assert result.get("success"), result.get("message")
        assert before - int(world.actions_remaining) == 1
        assert result["action_info"]["cost"] == 1

    def test_the_counsels_commission(self):
        """The war room's bench counsel charges the admin action the typed
        commission charges, and now says so."""
        with _quiet():
            world = WorldState.from_scenario(str(EUROPE))
        for key, state in list(world.diplomatic_states.items()):
            if state == "WAR":
                world.diplomatic_states[key] = "PEACE"
        world.war_exhaustion.clear()
        world.threat_level = 0
        world.agendas = {}
        world._agenda_cache = None
        world.nation_gold["France"] = 50000
        for marshal in [m for m in world.marshals.values() if m.nation == "France"][2:]:
            marshal.strength = 0
        dialogue = generate_advisory(None, "assess_situation", world)
        assert dialogue["context"]["recommendation"]["kind"] == "commission_marshal"
        world.dialogue_manager.replace(dialogue)
        before = int(world.admin_actions_remaining)
        result = CommandExecutor().handle_diplomatic_dialogue_response(1, {"world": world})
        assert result.get("success"), result.get("message")
        assert before - int(world.admin_actions_remaining) == 1
        assert result["action_info"]["cost"] == 1


class TestThePetitionSaysWhatItTook:
    """The petition's answer is read by `_on_command_result` too, and its
    arms charge the pool directly."""

    @pytest.mark.parametrize("choice,price", [
        ("promise", 1), ("command", 2), ("acknowledge", 0), ("rebuke", 0)])
    def test_the_answer(self, client, choice, price):
        world = M.world
        world.get_marshal("Ney").jealous_of = "Murat"
        J.queue_confrontation_petition(world, world.get_marshal("Ney"),
                                       world.get_marshal("Murat"), 1)
        reply, spent, _ = _post(client, "/marshal_petition_response", {"choice": choice})
        assert reply.get("success"), (choice, reply.get("message"))
        assert spent == price, (choice, spent)
        _honest(reply, spent, choice)


# ═══════════════════════════════════════════════════════════════════════
# The instrument's class, kept: the corpus lines that said 1 for 2
# ═══════════════════════════════════════════════════════════════════════

# The parser golden corpus, driven whole through POST /command on the boot
# board (an objection answered Insist, then Trust; a first-step interrupt
# answered with its first option): on 48f0a3d7, 61 of 751 replies (Insist)
# and 56 of 751 (Trust) disagreed with the pool. These are their lines.
THE_CENSUS_IDS = (
    "davout-move-to-viena", "ney-dig-in", "massena-hold-milan",
    "lannes-pursue-the-austrians", "ney-pursue-the-prussians",
    "marshal-bernadotte-hold", "ney-move-to-paris-via-champagne",
    "ney-move-from-burgundy-to-paris", "ney-hold-position",
    "parseneg-hold-position-do-not-attack", "parseneg-negated-clause-not-in-target",
    "parseneg-instead-of-attacking-fortify", "cc4-arrival-verb-hold-comma",
    "cc4-contingency-fall-back", "cc4-contingency-attack-any-enemy",
    "cc4-contingency-retreat-synonym", "parseneg-until-then-attack-holds",
    "parseneg-unless-elliptical-holds", "wo6-stand-by-ney-move-to-paris",
    "fa7-hold-here-and-attack-next-turn-holds", "fa6-fortify-until-next-turn-fortifies",
    "fa50-fortify-and-scout-keeps-the-fortify", "fa-n39-gen-dot-ney-holds",
    "fa80-stand-your-ground-is-hold", "fa80-pull-back-to-lorraine-is-a-march",
    "fa-d20-protect-rhineland-stays-hold", "r7-hodl-lorraine-is-a-standing-hold",
    "r7-hodl-then-attack-holds", "r7-remain-and-fortify-fortifies",
    "r7-fall-back-towards-lorraine-marches", "r7-would-you-march-for-me-is-an-order",
    "r7-push-on-towards-paris-targets-paris", "cr7-till-is-until",
    "cr7-word-number-turns", "cr7-honorific-in-the-condition",
    "cr7-relief-arrives-is-relieved", "cr7-until-turn-is-read-as-turns",
    "cr7-handoff-when-arrives-holds", "cr7-9-and-means-both",
    "cr7-9-or-means-whichever-first", "cr7-9-for-turns-and-until",
    "rs8-march-against", "sfcmd2-move-with-the-guard", "sfcmd2-protect-the-rear",
    "sfcmd2-guard-the-retreat", "sfcmd2-protect-our-flank",
    "sfcmd2r-pursue-the-mans-retreat", "sfr-d11-march-home-to-a-province",
    "sfr-d11-march-back-to-a-province", "dd0-10-because-tail-is-not-the-province",
    "dd0-9-earthworks-is-fortify", "dd0-s4-support-suffix-on-a-reason",
    "dd0-s4-surname-on-his-heels", "dd0-s4-h3-tell-x-to-typo-and-precaution",
    "dd0-s4-d24-stop-chasing-and-hold", "dd0-s4-d37-keep-going-to",
    "dd0-s4-d37-take-back", "dd0-s4-guard-subject-dig-in",
    "ao-follow-an-enemy-is-the-chase", "ao-the-army-marches-is-read-as-a-march",
)


class TestTheCorpusSaysItsPrice:

    def test_every_line_the_census_caught(self, monkeypatch):
        entries = {e["id"]: e for e in json.loads(CORPUS.read_text(encoding="utf-8"))["entries"]}
        missing = [i for i in THE_CENSUS_IDS if i not in entries]
        assert not missing, f"corpus ids gone (re-seat the census list): {missing}"
        lied, priced = [], 0
        for entry_id in THE_CENSUS_IDS:
            answers = ["insist", "trust"]
            while answers:
                answer = answers.pop(0)
                client = _board(monkeypatch)
                posts = [_order(client, entries[entry_id]["utterance"])]
                asked = False
                for _ in range(3):
                    if M.world.pending_objection or M.world.pending_strategic_objection:
                        asked = True
                        posts.append(_post(client, "/respond_to_objection", {"choice": answer}))
                    elif any(getattr(m, "pending_interrupt", None)
                             for m in M.world.get_player_marshals()):
                        posts.append(_interrupt_answer(client))
                    else:
                        break
                for reply, spent, _adm in posts:
                    priced += spent >= 2
                    if _said(reply) != spent:
                        lied.append((entry_id, answer, _said(reply), spent))
                if not asked:
                    answers = []   # no objection: the Trust arm is the same road
        assert not lied, lied
        assert priced >= 50, f"the census is vacuous: {priced} two-action replies"


# ═══════════════════════════════════════════════════════════════════════
# The sensitivity arms — each pin reds with its fix taken out
# ═══════════════════════════════════════════════════════════════════════

class TestTheSensitivityArms:

    def test_the_old_loop_reds_the_row(self, client, monkeypatch):
        """The pre-ACH-1 charge put back: every use charged, only the last
        reply kept."""
        def last_reply_only(self, action_type="generic", times=1):
            reply = {"action_cost": 0, "turn_advanced": False, "new_turn": None}
            for _ in range(max(0, int(times or 0))):
                reply = self.use_action(action_type)
            return reply
        monkeypatch.setattr(WorldState, "spend_actions", last_reply_only)
        reply, spent, _ = _order(client, "Ney, hold")
        assert spent == 2
        assert _said(reply) == 1, "the arm must reproduce the defect"

    def test_the_collectives_lost_sum_reds_the_fan_out(self, client, monkeypatch):
        """The collective's members' sum dropped: the reply says the head
        alone (0 without the Staff)."""
        real = G._run_members

        def run_without_the_sum(*args, **kwargs):
            out = real(*args, **kwargs)
            out["spent"] = 0
            return out
        monkeypatch.setattr(G, "_run_members", run_without_the_sum)
        reply, spent, _ = _order(client, "all marshals march to Swabia")
        assert spent >= 1 and _said(reply) == 0
