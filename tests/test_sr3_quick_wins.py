"""Score Mandate Chunk 3 — the quick-win reserve (`docs/SCORE_MANDATE_PLAN.md`
§2 Chunk 3; September 26, 2026): CQ-37 (the idioms "at once" and "hold
fast"), the boot help's desk line, and AAR-25 (the counter-punch announced the
turn it opens).

Every pin binds to the production line it names (`tools/_sweep_sr3_reserve.json`);
each rule with a lever has its lever-down pin, so the old behaviour is
reproduced, not remembered. The AAR-25 note is held to the executor: each
thing it says (free, this turn only, the foe it names, the price of breaking
camp, silence for a man locked in drill) is checked against the order that
would be refused or charged.
"""
import contextlib
import io
import random
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.ai.clause_guards as CG
import backend.ai.strategic_parser as SP
import backend.game_logic.dispatch as D
import backend.main as M
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser
from backend.commands.tactical_executor import unfortify_is_free

SCRIPTS = (Path(__file__).resolve().parents[1] / "godot-client"
           / "project-sovereign" / "scripts")
OPENING = "Threw back the enemy — may strike once, free, this turn only."


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    with contextlib.redirect_stdout(io.StringIO()):
        M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def _say(client, text):
    with contextlib.redirect_stdout(io.StringIO()):
        return client.post("/command", json={"command": text}).json()


# ═══════════════════════════════════════════════════════════════════════
# CQ-37 (a) — "at once" is the adverb, never the conditional "once <X>"
# ═══════════════════════════════════════════════════════════════════════

class TestCQ37AtOnceIsNeverACondition:
    ORDER = "recruit infantry at once in Lorrain"

    def test_at_once_mid_sentence_is_an_order(self, shipped):
        client, world = shipped
        world.gold = 5000
        reply = _say(client, self.ORDER)
        assert reply["success"] is True, reply.get("message")
        assert "Lorraine" in reply["message"]
        assert "comes to pass" not in reply["message"]

    def test_the_lever_down_refuses_it_as_a_contingency(self, shipped, monkeypatch):
        client, world = shipped
        world.gold = 5000
        monkeypatch.setattr(CG, "AT_ONCE_IS_NEVER_A_CONDITION", False)
        reply = _say(client, self.ORDER)
        assert reply["success"] is False
        assert "'once in Lorrain' comes to pass" in reply["message"]

    @pytest.mark.parametrize("lever", [True, False])
    def test_a_trailing_at_once_never_needed_the_rule(self, shipped, monkeypatch,
                                                      lever):
        """Nothing follows a trailing "at once", so the clause is elliptical
        and was always blanked — the control that shows the rule matters only
        when an order follows the adverb."""
        client, world = shipped
        world.gold = 5000
        monkeypatch.setattr(CG, "AT_ONCE_IS_NEVER_A_CONDITION", lever)
        assert _say(client, "recruit infantry in Lorrain at once")["success"] is True

    def test_a_real_once_still_refuses(self, shipped):
        client, _ = shipped
        reply = _say(client, "Ney, attack Mack once Soult moves")
        assert reply["success"] is False
        assert "'once Soult moves' comes to pass" in reply["message"]

    def test_the_hand_off_still_reads_a_leading_once(self, shipped):
        client, world = shipped
        reply = _say(client, "once Davout arrives, Ney, hold Rhineland")
        assert reply["success"] is True, reply.get("message")
        order = world.get_marshal("Ney").strategic_order
        assert order is not None and order.command_type == "HOLD"
        assert order.condition.until_marshal_arrives == "Davout"

    def test_the_marker_spans(self, monkeypatch):
        """`condition_marker_spans` is the condition grammar's reader."""
        assert CG.condition_marker_spans(self.ORDER) == []
        # "at once once Mack moves": the adverb is exempt, the condition is not.
        assert CG.condition_marker_spans("attack at once once Mack moves") == [(15, 19)]
        monkeypatch.setattr(CG, "AT_ONCE_IS_NEVER_A_CONDITION", False)
        assert CG.condition_marker_spans(self.ORDER) == [(20, 24)]

    def test_the_guard_verdict(self, monkeypatch):
        """`strip_condition_clauses_with_handoff` is the refusing reader."""
        verdict = CG.strip_condition_clauses_with_handoff(self.ORDER)
        assert verdict.refuse is False and verdict.text == self.ORDER
        monkeypatch.setattr(CG, "AT_ONCE_IS_NEVER_A_CONDITION", False)
        assert CG.strip_condition_clauses_with_handoff(self.ORDER).refuse is True


# ═══════════════════════════════════════════════════════════════════════
# CQ-37 (b) — "hold fast" / "hold firm" / "hold steady" are a bare hold
# ═══════════════════════════════════════════════════════════════════════

class TestCQ37HoldFastIsABareHold:
    @pytest.mark.parametrize("word", ["fast", "firm", "steady"])
    def test_he_holds_where_he_stands(self, shipped, word):
        client, world = shipped
        ney = world.get_marshal("Ney")
        reply = _say(client, f"Ney, hold {word}")
        assert reply["success"] is True, reply.get("message")
        order = ney.strategic_order
        assert order is not None and order.command_type == "HOLD"
        assert order.target == ney.location
        # a hold the game placed claims no reading of a province (SR-3b rider)
        assert "Our maps read" not in reply["message"]

    @pytest.mark.parametrize("word", ["fast", "firm", "steady"])
    def test_without_the_word_it_was_read_as_a_province(self, shipped,
                                                        monkeypatch, word):
        client, world = shipped
        monkeypatch.setattr(SP, "NON_REGION_TARGET_WORDS",
                            SP.NON_REGION_TARGET_WORDS - {word})
        reply = _say(client, f"Ney, hold {word}")
        assert reply["success"] is False
        assert world.get_marshal("Ney").strategic_order is None

    def test_stand_fast_never_needed_it(self, shipped, monkeypatch):
        """The stand-still vocabulary already read "stand fast" — the control."""
        client, world = shipped
        monkeypatch.setattr(SP, "NON_REGION_TARGET_WORDS",
                            SP.NON_REGION_TARGET_WORDS - {"fast", "firm", "steady"})
        assert _say(client, "Ney, stand fast")["success"] is True
        assert world.get_marshal("Ney").strategic_order.command_type == "HOLD"


# ═══════════════════════════════════════════════════════════════════════
# The boot help teaches the desk
# ═══════════════════════════════════════════════════════════════════════

BOOT_QUESTIONS = {
    "who am I fighting": "at war with",
    "is Paris safe": "Paris is ours",
    "what happened last turn": "campaign has just opened",
}


def _boot_help_body():
    main = (SCRIPTS / "main.gd").read_text(encoding="utf-8")
    at = main.index("func _print_boot_help")
    return main[at:main.index("\nfunc ", at + 10)]


class TestTheBootHelpTeachesTheDesk:
    def test_the_line_is_in_the_boot_help(self):
        """The release census (`test_release_build_2026_09_25.py`) posts every
        quoted phrase of the boot help; this pins that these three are there
        for it to post."""
        body = _boot_help_body()
        assert "Ask Berthier" in body and "an answer costs no action" in body
        for question in BOOT_QUESTIONS:
            assert question in body, question

    @pytest.mark.parametrize("question", sorted(BOOT_QUESTIONS))
    def test_each_answer_is_the_desks_and_costs_nothing(self, shipped, question):
        client, world = shipped
        before = (int(world.actions_remaining), int(world.admin_actions_remaining))
        reply = _say(client, question)
        assert reply["success"] is True, reply.get("message")
        assert BOOT_QUESTIONS[question] in reply["message"]
        assert (int(world.actions_remaining),
                int(world.admin_actions_remaining)) == before


# ═══════════════════════════════════════════════════════════════════════
# AAR-25 — the counter-punch is announced the turn it opens
# ═══════════════════════════════════════════════════════════════════════

def _earn_counter_punch(client, world):
    """The real grant: Mack attacks Davout and is thrown back (combat.py's
    cautious-defender arm), then the turn ends and the morning is built."""
    davout, mack = world.get_marshal("Davout"), world.get_marshal("Mack")
    mack.location = davout.location
    mack.strength = 900
    mack.fortified = False
    random.seed(1805)
    with contextlib.redirect_stdout(io.StringIO()):
        CommandExecutor().execute(
            {"command": {"marshal": "Mack", "action": "attack",
                         "target": "Davout", "_acting_nation": "Austria"}},
            {"world": world})
    assert davout.counter_punch_available
    return davout, _say(client, "end turn")


def _dispatch_entry(reply, name):
    dispatch = reply.get("morning_dispatch") or {}
    return next(m for m in dispatch.get("marshals", []) if m.get("name") == name)


def _foe_at_swabia(world, strength=None):
    """Archduke Charles, stood one march from Davout at Rhineland."""
    charles = world.get_marshal("ArchdukeCharles")
    charles.location = "Swabia"
    if strength is not None:
        charles.strength = strength
    world.calculate_visibility()
    return charles


class TestAAR25TheMorningSaysIt:
    def test_the_morning_announces_it(self, shipped):
        client, world = shipped
        davout, reply = _earn_counter_punch(client, world)
        entry = _dispatch_entry(reply, "Davout")
        assert entry["status"] == "counter_punch"
        assert entry["status_note"].startswith(OPENING)

    def test_the_lever_down_is_silent_until_it_expires(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(D, "THE_COUNTER_PUNCH_IS_ANNOUNCED", False)
        davout, reply = _earn_counter_punch(client, world)
        assert davout.counter_punch_available  # the resource is still there
        assert _dispatch_entry(reply, "Davout")["status"] != "counter_punch"

    def test_this_turn_only_is_the_tick(self, shipped):
        """The note's "this turn only": the next end turn expires it."""
        client, world = shipped
        davout, _ = _earn_counter_punch(client, world)
        assert davout.counter_punch_turns == 1
        _say(client, "end turn")
        assert davout.counter_punch_available is False

    def test_a_prisoner_is_not_named_as_a_foe(self, shipped):
        """The staged defence captures Mack: the note stays general."""
        client, world = shipped
        davout, _ = _earn_counter_punch(client, world)
        assert world.get_marshal("Mack").strength == 0
        assert D.counter_punch_foe_in_reach(davout, world) is None
        assert D._derive_marshal_status(davout, world) == ("counter_punch", OPENING)


class TestAAR25TheFoeItNames:
    def test_a_foe_in_reach_is_named(self, shipped):
        client, world = shipped
        davout, _ = _earn_counter_punch(client, world)
        _foe_at_swabia(world)
        _, note = D._derive_marshal_status(davout, world)
        assert note == OPENING + " Archduke Charles stands within reach at Swabia."

    def test_the_foe_is_named_only_in_sight(self, shipped, monkeypatch):
        """Fog-honest: the reader asks `get_visible_enemies`, never the
        omniscient roster — a foe the player cannot see is not named."""
        client, world = shipped
        davout, _ = _earn_counter_punch(client, world)
        _foe_at_swabia(world)
        monkeypatch.setattr(world, "get_visible_enemies", lambda nation: [])
        assert D.counter_punch_foe_in_reach(davout, world) is None

    def test_a_foe_one_march_too_far_is_not_named(self, shipped, monkeypatch):
        """The attack's own reach: Franconia is two hops from Rhineland, one
        past Davout's range. The foe is forced into sight so the pin is about
        reach, not fog."""
        client, world = shipped
        davout, _ = _earn_counter_punch(client, world)
        charles = _foe_at_swabia(world)
        charles.location = "Franconia"
        assert world.get_distance(davout.location, "Franconia") == davout.movement_range + 1
        monkeypatch.setattr(world, "get_visible_enemies", lambda nation: [charles])
        assert D.counter_punch_foe_in_reach(davout, world) is None
        charles.location = "Swabia"
        assert D.counter_punch_foe_in_reach(davout, world) == ("Archduke Charles", "Swabia")

    def test_the_nearest_foe_is_named(self, shipped):
        client, world = shipped
        davout, _ = _earn_counter_punch(client, world)
        _foe_at_swabia(world)
        world.get_marshal("ArchdukeJohn").location = davout.location
        world.calculate_visibility()
        assert D.counter_punch_foe_in_reach(davout, world) == ("Archduke John",
                                                               davout.location)

    def test_the_strike_it_names_is_free_at_zero_actions(self, shipped):
        """The note's "free": the named foe, struck with no action left."""
        client, world = shipped
        davout, _ = _earn_counter_punch(client, world)
        _foe_at_swabia(world, strength=2000)
        world.actions_remaining = 0
        reply = _say(client, "Davout, attack Archduke Charles")
        assert reply["success"] is True, reply.get("message")
        assert davout.counter_punch_available is False  # thrown, not restored
        assert int(world.actions_remaining) == 0


class TestAAR25ThePriceOfBreakingCamp:
    def test_a_cautious_man_breaks_camp_free(self, shipped):
        client, world = shipped
        davout, _ = _earn_counter_punch(client, world)
        _foe_at_swabia(world, strength=2000)
        davout.fortified = True
        _, note = D._derive_marshal_status(davout, world)
        assert note.endswith(" Davout must unfortify first (free).")
        # the executor agrees: refused behind works, the strike handed back...
        refused = _say(client, "Davout, attack Archduke Charles")
        assert refused["success"] is False and "fortified" in refused["message"]
        assert davout.counter_punch_available is True
        # ...and breaking camp costs him nothing
        before = int(world.actions_remaining)
        assert _say(client, "Davout, unfortify")["success"] is True
        assert int(world.actions_remaining) == before

    def test_the_price_is_the_executors(self, shipped):
        """A non-cautious man (the debug grant) is quoted the action he pays."""
        client, world = shipped
        ney = world.get_marshal("Ney")
        assert not unfortify_is_free(ney)
        ney.counter_punch_available = True
        ney.counter_punch_turns = 1
        ney.fortified = True
        _, note = D._derive_marshal_status(ney, world)
        assert note.endswith(" Ney must unfortify first (1 action).")
        before = int(world.actions_remaining)
        assert _say(client, "Ney, unfortify")["success"] is True
        assert int(world.actions_remaining) == before - 1


class TestAAR25WhatOutranksIt:
    def test_a_man_locked_in_drill_is_not_promised_a_strike(self, shipped):
        client, world = shipped
        davout, _ = _earn_counter_punch(client, world)
        davout.drilling = True
        davout.drilling_locked = True
        davout.drill_complete_turn = int(world.current_turn) + 1
        status, _ = D._derive_marshal_status(davout, world)
        assert status == "drilling"
        refused = _say(client, "Davout, attack Swabia")
        assert refused["success"] is False and "drill" in refused["message"]

    def test_a_question_he_holds_outranks_it(self, shipped):
        client, world = shipped
        davout, _ = _earn_counter_punch(client, world)
        assert _say(client, "Davout, hold")["success"] is True
        davout.pending_interrupt = {"interrupt_type": "cannon_fire",
                                    "enemy": "ArchdukeCharles",
                                    "location": davout.location}
        status, _ = D._derive_marshal_status(davout, world)
        assert status == "awaiting_decision"


class TestTheRenderersCarryTheIcon:
    @pytest.mark.parametrize("script", ["main.gd", "dispatch_view.gd"])
    def test_the_status_has_its_glyph(self, script):
        source = (SCRIPTS / script).read_text(encoding="utf-8")
        at = source.index('"counter_punch":')
        assert 'icon = "»"' in source[at:at + 120]
