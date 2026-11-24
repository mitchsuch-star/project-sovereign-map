"""Row IC, Session 2 — IC-8, THE LINE FOR TASKS (November 20, 2026).

The design is `docs/INDEPENDENT_COMMAND_SPEC.md` version 6, §8.2–§8.5 and §8.7;
the rules `docs/SYSTEMS_REFERENCE.md` §231; the ledger `docs/BUG_FIXES.md`
(§UI6, §WS and §"Row IC — the review of 'on his own'").

The typed line is the road for a TASK — a standing order with a condition, a
time limit or an if-then. Its promise is the read-back: before anything is
spent the line says what it TOOK, what it did NOT take, the marshal's answer
and the price, and what goes when you press Enter is exactly what was shown.
That promise stood on the typed road's open defects, so they were fixed first:

  WS-12   a live model's own score moved morale, trust and attack on the
          player's marshal (golden rule 6) — retired; the literal marshal's
          buff reads the FAST parser's own numbers.
  GRD-33  that buff never expired — it is for the turn it is given in.
  WS-14   the read-back called every line an answer while a question stood —
          it asks `/command`'s own readers now.
  IC-V1   a one-word condition ("if outnumbered") was dropped without a word —
          the guard records what it blanks and the read-back names it.
  IC-V2   the read-back showed no condition and no if-then before the order
          went — it shows each one it took.

(UI6-X70 / X73 / X74 / X75 — the typed road's compound subjects and lists —
are pinned where they were filed, `tests/test_ui6_fog_siblings.py`.)
"""
from __future__ import annotations

import contextlib
import io
import json
import random
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import parse_preview as PP
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
                 / "europe_1805.json")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def world1805():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO_PATH))


def _fresh(world1805) -> WorldState:
    with _quiet():
        return WorldState.from_dict(world1805.to_dict())


@pytest.fixture(scope="module")
def road():
    """The shipped 1805 board behind the real app and the mock parser — the
    pattern of `tests/test_ui6_fog_siblings.py`: one portal for the module,
    `M.world`, the game state's world and `M.parser` swapped together and put
    back."""
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
    with _quiet():
        world = WorldState.from_dict(json.loads(snap))
        if tweak is not None:
            tweak(world)
        M._set_active_world(world)
        M.parser = CommandParser(use_real_llm=False)
    PP.invalidate()
    return world


def _post(client, line, **body):
    random.seed(1805)
    with _quiet():
        return client.post("/command", json={"command": line, **body}).json()


def _preview(client, line):
    PP.invalidate()
    with _quiet():
        return client.get("/parse_preview", params={"line": line}).json()


def _parts(reading, role=None):
    return [str(p.get("text") or "") for p in (reading.get("parts") or [])
            if role is None or p.get("role") == role]


def _text(reading) -> str:
    return " · ".join(_parts(reading))


# ═══════════════════ WS-12 — the model's number moves nothing ═══════════════

def _live(marshal, action, **extra):
    """A parse as a LIVE answer hands it to the executor: the model's own
    figures (a perfect score, no ambiguity) beside the fast parser's."""
    parsed = {"success": True, "raw_input": f"{marshal}, {action}", "mode": "live",
              "strategic_score": 95, "ambiguity": 0,
              "command": {"marshal": marshal, "action": action, "type": "specific",
                          "raw_command": f"{marshal}, {action}", "mode": "live"}}
    parsed.update(extra)
    return parsed


class TestWS12TheModelsNumberMovesNothing:

    def test_a_live_score_moves_no_morale_trust_or_attack(self, world1805):
        world = _fresh(world1805)
        ney = world.marshals["Ney"]
        ney.morale = 50
        before = (int(ney.morale), int(ney.trust.value), int(ney.strategic_combat_bonus))
        with _quiet():
            result = CommandExecutor().execute(_live("Ney", "wait"), {"world": world})
        assert result.get("success"), result.get("message")
        assert (int(ney.morale), int(ney.trust.value), int(ney.strategic_combat_bonus)) == before, (
            "a number the model wrote reached a marshal (WS-12)")

    def test_the_literal_buff_reads_the_fast_parsers_ambiguity_never_the_models(self, world1805):
        # the model says "crystal clear" (0); the fast parser could not read the line (75)
        world = _fresh(world1805)
        soult = world.marshals["Soult"]
        assert soult.personality == "literal"
        with _quiet():
            CommandExecutor().execute(_live("Soult", "defend", fast_ambiguity=75,
                                            fast_strategic_score=0), {"world": world})
        assert int(soult.strategic_combat_bonus) == 0 and int(soult.strategic_defense_bonus) == 0
        # the fast parser read it crisply (5): the buff is its own figure's
        world = _fresh(world1805)
        soult = world.marshals["Soult"]
        with _quiet():
            CommandExecutor().execute(_live("Soult", "defend", fast_ambiguity=5,
                                            fast_strategic_score=10), {"world": world})
        assert int(soult.strategic_combat_bonus) == 15 and int(soult.strategic_defense_bonus) == 15

    def test_a_live_score_arms_no_precision_execution(self, world1805):
        world = _fresh(world1805)
        soult = world.marshals["Soult"]
        with _quiet():
            CommandExecutor().execute(_live("Soult", "defend", fast_ambiguity=5,
                                            fast_strategic_score=10), {"world": world})
        assert not soult.precision_execution_active, (
            "the model's 95 armed precision execution — the fast parser's own score is 10")

    def test_a_live_answer_with_no_fast_numbers_reads_as_unread(self, world1805):
        world = _fresh(world1805)
        soult = world.marshals["Soult"]
        with _quiet():
            CommandExecutor().execute(_live("Soult", "defend"), {"world": world})
        assert int(soult.strategic_combat_bonus) == 0

    def test_a_mock_parse_is_the_fast_parsers_own(self, world1805):
        """The control: with no model, the parse's numbers ARE the fast
        parser's — a crisp "defend" still buffs the literal man (15)."""
        world = _fresh(world1805)
        soult = world.marshals["Soult"]
        parser = CommandParser(use_real_llm=False)
        with _quiet():
            parsed = parser.parse("Soult, defend", {"world": world}, world=world)
            CommandExecutor().execute(parsed, {"world": world})
        assert "fast_ambiguity" not in parsed and parsed.get("mode", "mock") == "mock"
        assert int(soult.strategic_combat_bonus) == 15 and int(soult.strategic_defense_bonus) == 15

    def test_where_a_live_answer_is_adopted_the_fast_numbers_ride_beside_it(self, monkeypatch):
        from backend.ai.llm_client import LLMClient
        from backend.ai.schemas import ParseResult
        client = LLMClient()
        model = ParseResult(matched=True, marshals=["Ney"], action="defend", target=None,
                            ambiguity=0, strategic_score=95, interpretation="", confidence=0.9,
                            mode="live", key_source="none", raw_command="Ney, defend")
        monkeypatch.setattr(type(client), "_should_fallback_to_llm", lambda self, fast, gs: True)
        monkeypatch.setattr(type(client), "_parse_with_live_provider",
                            lambda self, text, gs, fast: model)
        with _quiet():
            adopted = client.parse_command("Ney, defend", None)
        assert adopted["ambiguity"] == 0 and adopted["strategic_score"] == 95   # the model's, for text
        assert adopted["fast_ambiguity"] == 5 and adopted["fast_strategic_score"] == 10
        # ... and a fast parse that stands (no model) carries none: its own are the numbers
        monkeypatch.setattr(type(client), "_should_fallback_to_llm", lambda self, fast, gs: False)
        with _quiet():
            stands = client.parse_command("Ney, defend", None)
        assert "fast_ambiguity" not in stands

    def test_the_courts_formula_is_untouched(self):
        """`feedback.apply_strategic_bonuses` stays — the enemy's AI scores its
        own marshals by a formula (`enemy_ai.calculate_ai_strategic_score`),
        no model in it."""
        import inspect

        from backend.ai import enemy_ai, feedback
        assert callable(feedback.apply_strategic_bonuses)
        assert "apply_strategic_bonuses" in inspect.getsource(enemy_ai)


# ═══════════════════ GRD-33 — the literal buff expires with the turn ════════

class TestGRD33TheLiteralBuffExpiresWithTheTurn:

    @staticmethod
    def _buffed(world1805):
        world = _fresh(world1805)
        soult = world.marshals["Soult"]
        soult.strategic_combat_bonus = 15
        soult.strategic_defense_bonus = 15
        return world, soult

    def test_it_is_gone_when_the_turn_advances(self, world1805):
        world, soult = self._buffed(world1805)
        with _quiet():
            world.advance_turn()
        assert int(soult.strategic_combat_bonus) == 0 and int(soult.strategic_defense_bonus) == 0

    def test_it_stands_through_the_turn_it_was_given_in(self, world1805):
        """It covers the enemy's phase behind the order: nothing clears it
        before the turn advances."""
        world = _fresh(world1805)
        soult = world.marshals["Soult"]
        parser = CommandParser(use_real_llm=False)
        with _quiet():
            CommandExecutor().execute(
                parser.parse("Soult, defend", {"world": world}, world=world), {"world": world})
        assert int(soult.strategic_defense_bonus) == 15

    def test_with_the_seam_down_it_banks_as_before(self, world1805, monkeypatch):
        from backend.commands import meta_executor as ME
        monkeypatch.setattr(ME, "the_literal_buff_expires_with_the_turn", lambda: False)
        world, soult = self._buffed(world1805)
        with _quiet():
            world.advance_turn()
        assert int(soult.strategic_combat_bonus) == 15 and int(soult.strategic_defense_bonus) == 15

    def test_every_holders_bonus_expires_with_the_turn(self, world1805):
        """WS-R4 (row FR, Session FR-2): the rule covers every holder. A
        court's bonus is now set before the attack it rewards and spent by it,
        so whatever an attack refused before its blow left standing — or any
        stray bonus — is gone at dawn; before, a court's literal man (Mack)
        kept his for his next attack, however many turns later."""
        world = _fresh(world1805)
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        assert ney.personality != "literal" and mack.personality == "literal"
        assert mack.nation != world.player_nation
        ney.strategic_combat_bonus = 10
        mack.strategic_combat_bonus = 10
        with _quiet():
            world.advance_turn()
        assert int(ney.strategic_combat_bonus) == 0 and int(mack.strategic_combat_bonus) == 0

    def test_with_wsr4_down_only_the_players_literal_marshal_is_cleared(self, world1805,
                                                                        monkeypatch):
        """GRD-33 as it was built: with WS-R4's seam down only the player's
        literal marshals are cleared (the courts' marshals banked theirs)."""
        from backend.ai import feedback as FB
        monkeypatch.setattr(FB, "a_courts_bonus_rides_its_own_act", lambda: False)
        world = _fresh(world1805)
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        ney.strategic_combat_bonus = 10
        mack.strategic_combat_bonus = 10
        with _quiet():
            world.advance_turn()
        assert int(ney.strategic_combat_bonus) == 10 and int(mack.strategic_combat_bonus) == 10


# ═══════════════════ WS-14 — the read-back and Enter agree ══════════════════

def _ney_meets_mack(world):
    """Ney's march into Swabia meets Mack: his question waits, with answers."""
    world.marshals["Ney"].pending_interrupt = {
        "marshal": "Ney", "interrupt_type": "contact_bad_odds", "enemy": "Mack",
        "location": "Swabia", "is_first_step": True,
        "options": ["attack_anyway", "go_around", "hold_position", "cancel_order"],
        "message": "Ney: 'Mack blocks the path at Swabia. Odds unfavorable. Your orders?'"}


class TestWS14TheReadBackAsksTheCommandsOwnReaders:

    @staticmethod
    def _asked(client, snap):
        """A real question on the real road: Ney marches into Mack."""
        world = _board(snap)
        reply = _post(client, "Ney, march to Swabia")
        assert world.marshals["Ney"].pending_interrupt, reply.get("message")
        return world

    @pytest.mark.parametrize("line", ["attack anyway", "hold", "go around", "cancel"])
    def test_a_line_that_answers_is_called_an_answer_and_is_one(self, road, line):
        client, snap = road
        world = self._asked(client, snap)
        reading = _preview(client, line)
        assert reading["kind"] == "pending", reading
        assert _text(reading) == "Ney’s question stands — this line answers it"
        _post(client, line)
        assert not world.marshals["Ney"].pending_interrupt, "Enter did not take it as the answer"

    @pytest.mark.parametrize("line, who", [("Davout, fortify", "Davout"),
                                           ("Soult, defend", "Soult"),
                                           ("Lannes, march to Lorraine", "Lannes")])
    def test_an_order_to_another_marshal_is_read_as_that_order(self, road, line, who):
        """The row's defect: the read-back said "A question stands — answer it
        first" of every line; Enter let an order to another marshal through."""
        client, snap = road
        world = self._asked(client, snap)
        reading = _preview(client, line)
        assert reading["kind"] == "order" and reading["marshal"] == who, reading
        assert "question stands" not in _text(reading)
        before = int(world.actions_remaining)
        reply = _post(client, line)
        assert reply.get("success") and int(world.actions_remaining) < before, reply.get("message")
        assert world.marshals["Ney"].pending_interrupt, "his question must still wait"

    def test_a_question_is_not_an_answer_on_either_road(self, road):
        client, snap = road
        world = self._asked(client, snap)
        reading = _preview(client, "should we attack?")
        assert reading["kind"] == "pending"
        assert _text(reading) == "Ney’s question stands — a question is not an answer"
        before = int(world.actions_remaining)
        reply = _post(client, "should we attack?")
        assert "A question is not an answer" in reply["message"]
        assert int(world.actions_remaining) == before and world.marshals["Ney"].pending_interrupt

    def test_a_fresh_order_to_the_same_man_elsewhere_is_an_order(self, road):
        client, snap = road
        world = self._asked(client, snap)
        reading = _preview(client, "Ney, march to Lorraine")
        assert reading["kind"] == "order" and reading["action"] == "move", reading
        _post(client, "Ney, march to Lorraine")
        order = world.marshals["Ney"].strategic_order
        assert order is not None and order.target == "Lorraine"

    def test_a_conditional_order_is_never_read_as_the_answer(self, road):
        """CC-X21's rule, on the read-back too: "if Mack advances, attack"
        names "attack" but is a fresh conditional order."""
        client, snap = road
        self._asked(client, snap)
        reading = _preview(client, "Ney, if Mack advances, fall back to Lorraine")
        assert reading["kind"] != "pending", reading

    def test_the_routes_reader_is_the_stages_own_test(self, road):
        client, snap = road
        world = _board(snap, tweak=_ney_meets_mack)
        ney = world.marshals["Ney"]
        pending = ney.pending_interrupt
        assert M._interrupt_addressed_other("Davout, fortify", ney, pending, world) is True
        assert M._interrupt_addressed_other("attack anyway", ney, pending, world) is False
        assert M._interrupt_addressed_other("Ney, march to Lorraine", ney, pending, world) is True
        assert M._interrupt_reading(world, "Davout, fortify") is None
        assert M._interrupt_reading(world, "attack anyway") == (
            "Ney’s question stands — this line answers it")
        # no words of the question's, no answer: the line goes on to the parser
        assert M._interrupt_reading(world, "what now?") is None

    def test_berthiers_question_stands_only_for_an_answer(self, road):
        client, snap = road
        world = _board(snap)
        reply = _post(client, "Soult, pursue")
        assert reply["message"].startswith("You wish me to pursue"), reply["message"]
        assert world.dialogue_manager.peek() is not None
        for line in ("yes", "1", "Mack"):
            assert _text(_preview(client, line)) == (
                "Berthier’s question stands — this line answers it"), line
        assert _text(_preview(client, "cancel")) == (
            "Berthier’s question stands — this line withdraws the order")
        fresh = _preview(client, "Davout, fortify")
        assert fresh["kind"] == "order" and fresh["marshal"] == "Davout", fresh
        # ... and Enter agrees: the fresh order is carried out, the question let go
        reply = _post(client, "Davout, fortify")
        assert reply.get("success") and world.marshals["Davout"].fortified, reply.get("message")
        assert world.dialogue_manager.peek() is None

    def test_without_the_routes_reader_an_interrupt_still_claims_every_line(self, world1805):
        """The cautious reading for a caller outside the route."""
        world = _fresh(world1805)
        _ney_meets_mack(world)
        assert PP._pending_question(world, "Davout, fortify") == (
            "A question stands — answer it first")
        assert PP._pending_question(world, "Davout, fortify", lambda w, t: None) is None


# ═══════════════════ IC-V1 — the guard records what it blanks ═══════════════

class TestICV1TheGuardRecordsWhatItBlanks:

    @staticmethod
    def _blanked(line, friends=("Ney", "Davout", "Soult")):
        from backend.ai.clause_guards import strip_condition_clauses_with_handoff
        verdict = strip_condition_clauses_with_handoff(
            line, friendly_names=friends, roster_names=list(friends) + ["Mack"])
        return verdict, [(b["clause"], b["marker"], b["kind"]) for b in verdict.blanked]

    def test_a_one_word_clause_is_blanked_and_recorded(self):
        verdict, blanked = self._blanked("Ney, retreat if outnumbered")
        assert not verdict.refuse and "outnumbered" not in verdict.text
        assert blanked == [("if outnumbered", "if", "one_word")]
        verdict, blanked = self._blanked("Ney, unless attacked, hold position")
        assert not verdict.refuse and blanked == [("unless attacked", "unless", "one_word")]

    def test_the_two_word_floor_is_untouched(self):
        """`cr2-when-ready-then-retreat-not-split` and PARSE-NEG's refusal both
        stand: one word is blanked (and now said), two refuse."""
        verdict, blanked = self._blanked("when ready then retreat")
        assert not verdict.refuse and blanked == [("when ready", "when", "one_word")]
        verdict, blanked = self._blanked("Ney, attack if Mack advances")
        assert verdict.refuse and blanked == []

    def test_until_while_before_are_recorded_as_blank_only(self):
        _v, blanked = self._blanked("Davout, hold Lorraine while Ney marches")
        assert blanked == [("while Ney marches", "while", "blank_only")]
        _v, blanked = self._blanked("Ney, fortify until relieved")
        assert blanked == [("until relieved", "until", "blank_only")]

    def test_a_handed_off_clause_is_taken_not_blanked(self):
        verdict, blanked = self._blanked("Davout, when Ney arrives, hold Lorraine")
        assert verdict.handoff and verdict.handoff["until_marshal_arrives"] == "Ney"
        assert blanked == []

    def test_the_parse_carries_them_and_the_order_is_unchanged(self, world1805):
        world = _fresh(world1805)
        parser = CommandParser(use_real_llm=False)
        with _quiet():
            parsed = parser.parse("Ney, retreat if outnumbered", {"world": world}, world=world)
        assert parsed["success"] and parsed["command"]["action"] == "retreat"
        assert parsed["blanked_clauses"] == [
            {"clause": "if outnumbered", "marker": "if", "kind": "one_word"}]
        with _quiet():
            plain = parser.parse("Ney, retreat", {"world": world}, world=world)
        assert "blanked_clauses" not in plain


# ═══════════════════ IC-V2 — the read-back shows what it took ═══════════════

def _roles(reading, role):
    return [p for p in (reading.get("parts") or []) if p.get("role") == role]


class TestICV2TheReadBackShowsWhatItTook:
    """§8.4 row 1, "Taken": each condition, each if-then, what a march does on
    arrival — BEFORE the order is sent, in the words its own echo uses."""

    @pytest.mark.parametrize("line, said", [
        ("Davout, hold Franconia until Ney arrives", "until Ney arrives"),
        ("Ney, hold Rhineland for three turns", "for 3 turns"),
        ("Murat, chase Mack until he is destroyed", "until Mack is destroyed"),
        ("Ney, hold Rhineland until relieved", "until relieved"),
        ("Ney, pursue Mack until he is destroyed or for 4 turns",
         "for 4 turns or until Mack is destroyed — whichever comes first"),
        ("Davout, when Ney arrives, hold Rhineland", "until Ney arrives"),
    ])
    def test_a_condition_it_took_is_shown(self, road, line, said):
        client, snap = road
        _board(snap)
        reading = _preview(client, line)
        assert reading["kind"] == "order", reading
        assert _parts(reading, "taken") == [said]
        assert reading["understood"] == "" and not _roles(reading, "nottaken")

    def test_an_if_then_it_took_is_shown(self, road):
        client, snap = road
        _board(snap)
        reading = _preview(client, "Ney, if Mack advances, fall back to Lorraine")
        assert _parts(reading, "taken") == ["if Mack comes within reach, fall back to Lorraine"]
        assert _parts(reading, "head") == ["Ney · hold"]

    def test_what_a_march_does_on_arrival_is_shown(self, road):
        client, snap = road
        _board(snap)
        # one word for one thing (the review, W1): the chip says "then dig in"
        assert _parts(_preview(client, "Ney, march to Lorraine then dig in"),
                      "taken") == ["then dig in on arrival"]
        assert _parts(_preview(client, "Ney, march to Lorraine then defend"),
                      "taken") == ["then stand on the defensive on arrival"]
        assert _parts(_preview(client, "Ney, march to Lorraine then hold"),
                      "taken") == ["then hold on arrival"]

    def test_a_literal_mans_lines_and_his_answer(self, road):
        client, snap = road
        board = _board(snap)
        reading = _preview(client, "Soult, hold Lorraine. If attacked, dig in. If outnumbered, "
                                   "fall back on Champagne. If Ney arrives, attack.")
        assert _parts(reading, "taken") == [
            "if he is attacked, dig in", "if he is outnumbered, fall back to Champagne",
            "if Ney arrives, attack"]
        assert _parts(reading, "cost") == ["1 action"]
        said = _parts(reading, "answer")
        # Row IC, Session 4 (IC-13): the line is from SOULT'S OWN bank now
        # (`own_voice` — "exact"); `marshal_voice.LITERAL_EXACT` is the
        # fallback for a man with no such bank.
        from backend.game_logic import own_voice
        assert len(said) == 1 and said[0].strip("“”") in own_voice.LINES["Soult"]["exact"]
        # ... a man who does not follow orders to the letter answers nothing here
        ney = _preview(client, "Ney, hold Rhineland. If attacked, dig in.")
        assert _parts(ney, "taken") == ["if he is attacked, dig in"] and not _parts(ney, "answer")
        assert board.marshals["Soult"].strategic_order is None, "a reading gives no order"

    def test_what_the_echo_would_warn_of_is_said_before_the_send(self, road):
        client, snap = road
        _board(snap)
        reading = _preview(client, "Davout, hold Franconia until Ney arrives")
        assert any("Ney is already at Rhineland with him" in w for w in _parts(reading, "warn"))

    def test_a_plain_order_reads_exactly_as_it_did(self, road):
        client, snap = road
        _board(snap)
        for line in ("Ney, attack Mack", "Ney, hold Rhineland", "Ney, march to Lorraine"):
            reading = _preview(client, line)
            assert {p["role"] for p in reading["parts"]} <= {"head", "cost", "turns", "warn", "note"}
            assert reading["understood"] == ""

    def test_the_rows_of_a_list_carry_them(self, road):
        client, snap = road
        _board(snap)
        listing = _post(client, "Ney and Davout, hold Rhineland until Soult arrives",
                        list_first=True)["directive"]
        for row in listing["rows"]:
            assert "until Soult arrives" in row["notes"], row


# ═══════════════════ IC-V1 — the read-back names what it did NOT take ═══════

class TestICV1TheReadBackNamesWhatItDidNotTake:
    """§8.4 row 2, "Not taken": every part that would change what he does,
    quoted, with the plain reason — and the line as understood."""

    def test_the_filed_line(self, road):
        """ "Ney, retreat if outnumbered" — the spec's own example row."""
        client, snap = road
        _board(snap)
        reading = _preview(client, "Ney, retreat if outnumbered")
        assert reading["kind"] == "order" and reading["action"] == "retreat"
        assert _parts(reading, "head") == ["Ney · fall back"]
        (row,) = _roles(reading, "nottaken")
        assert row["blocks"] is True
        assert row["text"] == "‘if outnumbered’ — " + PP.WHY_NO_CONDITION
        assert reading["understood"] == "Ney, retreat"
        # ... offered back as the exact order it means
        assert reading["candidates"] == [
            {"label": "Ney, hold. If he is outnumbered, fall back to Lorraine.",
             "line": "Ney, hold. If he is outnumbered, fall back to Lorraine."}]

    @pytest.mark.parametrize("line, clause, why, understood", [
        ("Ney, hold Rhineland unless attacked", "unless attacked", "WHY_NO_CONDITION",
         "Ney, hold Rhineland"),
        ("Ney, retreat if necessary", "if necessary", "WHY_NO_CONDITION", "Ney, retreat"),
        ("Ney, fortify for 3 turns", "for 3 turns", "WHY_NO_CLOCK", "Ney, fortify"),
        ("Ney, defend until relieved", "until relieved", "WHY_NO_CLOCK", "Ney, defend"),
        ("Ney, hold Rhineland until the cows come home", "until the cows come home",
         "WHY_NOT_HELD", "Ney, hold Rhineland"),
        # Row IC, Session 3: a how-bold word on a STANDING task to a bold or
        # careful man now sets him on his own (`tests/test_ic10_on_his_own.py`);
        # to a literal man, and on a one-turn attack, it is still not taken.
        ("Soult, hold Lorraine carefully", "carefully", "WHY_AS_WRITTEN", "Soult, hold Lorraine"),
        ("Ney, attack Mack only at good odds", "only at good odds", "WHY_AS_WRITTEN",
         "Ney, attack Mack"),
        ("Soult, hold Lorraine, boldly.", "boldly", "WHY_AS_WRITTEN", "Soult, hold Lorraine."),
    ])
    def test_a_part_that_would_change_what_he_does_blocks(self, road, line, clause, why,
                                                          understood):
        client, snap = road
        _board(snap)
        reading = _preview(client, line)
        assert reading["kind"] == "order", reading
        (row,) = _roles(reading, "nottaken")
        assert row == {"role": "nottaken", "blocks": True,
                       "text": f"‘{clause}’ — {getattr(PP, why)}"}
        assert reading["understood"] == understood

    @pytest.mark.parametrize("line, clause, why", [
        ("Ney, attack Mack if possible", "if possible", "WHY_FILLER"),
        ("Ney, attack Mack when ready", "when ready", "WHY_FILLER"),
        ("Ney, attack Mack before he retreats", "before he retreats", "WHY_REASON"),
        ("Ney, attack Mack while Davout holds Rhineland", "while Davout holds Rhineland",
         "WHY_REASON"),
    ])
    def test_filler_is_a_quiet_note_and_blocks_nothing(self, road, line, clause, why):
        client, snap = road
        _board(snap)
        reading = _preview(client, line)
        (row,) = _roles(reading, "nottaken")
        assert row == {"role": "nottaken", "blocks": False,
                       "text": f"‘{clause}’ — {getattr(PP, why)}"}
        assert reading["understood"] == ""

    def test_an_until_the_grammar_read_is_taken_not_untaken(self, road):
        client, snap = road
        _board(snap)
        reading = _preview(client, "Davout, hold Franconia until Ney arrives")
        assert not _roles(reading, "nottaken") and _parts(reading, "taken")

    def test_an_exact_orders_line_that_cannot_be_taken(self, road):
        client, snap = road
        _board(snap)
        reading = _preview(client, "Ney, hold Rhineland. If attacked, dig in. If outnumbered, "
                                   "fall back on Lorraine.")
        assert reading["kind"] == "order" and _parts(reading, "head") == ["Ney · hold Rhineland"]
        assert reading["line"].startswith("Ney, hold Rhineland. If attacked, dig in. If outnum")
        assert _parts(reading, "taken") == ["if he is attacked, dig in"]
        (row,) = _roles(reading, "nottaken")
        assert row["blocks"] and "Ney's orders carry one if-then" in row["text"]
        assert reading["understood"] == "Ney, hold Rhineland. If he is attacked, dig in."

    def test_what_is_understood_reads_back_with_nothing_left_to_block(self, road):
        client, snap = road
        _board(snap)
        # (row IC, Session 3: "Ney, hold Rhineland carefully" is a task on his own
        # now — the literal man's line keeps the case of a how-bold word not taken)
        for line in ("Ney, retreat if outnumbered", "Soult, hold Lorraine carefully",
                     "Ney, fortify for 3 turns",
                     "Ney, hold Rhineland. If attacked, dig in. If outnumbered, fall back on "
                     "Lorraine."):
            first = _preview(client, line)
            again = _preview(client, first["understood"])
            assert again["kind"] == "order" and again["understood"] == "", (line, again)
            assert not [p for p in _roles(again, "nottaken") if p.get("blocks")]
            assert again["action"] == first["action"] and again["ap"] == first["ap"]

    def test_the_rows_are_pure(self, world1805):
        world = _fresh(world1805)
        parser = CommandParser(use_real_llm=False)
        with _quiet():
            parsed = parser.parse("Ney, retreat if outnumbered", {"world": world}, world=world)
        before = json.dumps(world.to_dict(), sort_keys=True, default=str)
        state = random.getstate()
        rows = PP.not_taken_rows(world, parsed, "Ney, retreat if outnumbered")
        assert rows and rows[0]["offer"].startswith("Ney, hold. If he is outnumbered")
        assert random.getstate() == state
        assert json.dumps(world.to_dict(), sort_keys=True, default=str) == before


# ═══════════════════ the typed gate — "Send what I understood" ══════════════

class TestTheTypedLineIsNeverSentWithAPartMissing:
    """§8.4: while a "Not taken" row blocks, what goes is the line as
    understood. The command window sends `typed: true`; `/command` refuses a
    typed line that would go out without the part, free, and hands back the
    line as understood. Nothing else that posts a line is touched."""

    LINE = "Ney, retreat if outnumbered"

    def test_a_typed_line_is_held_free_with_the_line_as_understood(self, road):
        client, snap = road
        board = _board(snap)
        actions, where = int(board.actions_remaining), board.marshals["Ney"].location
        reply = _post(client, self.LINE, typed=True)
        assert reply["success"] is False and reply["refusal"] == "not_taken"
        assert reply["understood"] == "Ney, retreat"
        assert reply["not_taken"] == [{"clause": "if outnumbered", "why": PP.WHY_NO_CONDITION}]
        assert "'if outnumbered'" in reply["message"] and "Nothing was spent" in reply["message"]
        assert int(board.actions_remaining) == actions
        assert board.marshals["Ney"].location == where

    def test_the_same_line_from_any_other_sender_goes_as_it_always_did(self, road):
        """R-INERT: a button, a chip, a script, the band — no `typed` field."""
        client, snap = road
        board = _board(snap)
        where = board.marshals["Ney"].location
        reply = _post(client, self.LINE)
        assert reply.get("success") and "understood" not in reply
        assert board.marshals["Ney"].location != where, "he fell back, as the line always did"

    def test_the_understood_line_typed_goes(self, road):
        client, snap = road
        board = _board(snap)
        where = board.marshals["Ney"].location
        held = _post(client, self.LINE, typed=True)
        reply = _post(client, held["understood"], typed=True)
        assert reply.get("success") and board.marshals["Ney"].location != where

    def test_filler_holds_nothing(self, road):
        client, snap = road
        _board(snap)
        reply = _post(client, "Ney, attack Mack if possible", typed=True)
        assert reply.get("refusal") != "not_taken" and "understood" not in reply

    def test_the_gate_and_the_reading_are_one_reader(self, road):
        client, snap = road
        # (row IC, Session 3: "Ney, hold Rhineland carefully" is a task on his own
        # now — the literal man's line keeps the case of a how-bold word not taken)
        for line in ("Ney, retreat if outnumbered", "Soult, hold Lorraine carefully",
                     "Ney, fortify for 3 turns", "Ney, defend until relieved",
                     "Ney, hold Rhineland unless attacked", "Ney, attack Mack if possible",
                     "Ney, attack Mack", "Davout, hold Franconia until Ney arrives"):
            _board(snap)
            reading = _preview(client, line)
            _board(snap)
            reply = _post(client, line, typed=True)
            held = reply.get("refusal") == "not_taken"
            assert held == bool(reading["understood"]), line
            if held:
                assert reply["understood"] == reading["understood"], line

    def test_a_line_that_answers_a_standing_question_is_the_questions(self, road):
        client, snap = road
        board = _board(snap)
        _post(client, "Ney, march to Swabia")
        assert board.marshals["Ney"].pending_interrupt
        reply = _post(client, "hold if possible", typed=True)
        assert reply.get("refusal") != "not_taken"

    def test_the_request_field_defaults_off(self):
        assert M.CommandRequest(command="x").typed is False


# ═══════════════════ how bold — read and set aside ══════════════════════════

class TestHowBoldIsReadAndSetAside:

    @staticmethod
    def _parse(world, line):
        parser = CommandParser(use_real_llm=False)
        with _quiet():
            return parser.parse(line, {"world": world}, world=world)

    def test_a_word_behind_a_name_is_no_part_of_the_name(self, world1805):
        """ "Ney, hold Rhineland carefully" held the province "Rhineland
        Carefully" — the strategic table took the word for the name."""
        world = _fresh(world1805)
        parsed = self._parse(world, "Ney, hold Rhineland carefully")
        assert parsed["success"] and parsed["strategic_type"] == "HOLD"
        assert parsed["command"]["target"] == "Rhineland"
        # row IC, Session 3: to a bold or careful man who may be set on his own
        # the word is TAKEN — the task is his own, one step more careful
        assert parsed["own_risk_words"] == ["carefully"] and parsed["own"]["risk"] == -1
        assert parsed["raw_input"] == "Ney, hold Rhineland carefully"
        literal = self._parse(world, "Soult, hold Lorraine carefully")
        assert literal["command"]["target"] == "Lorraine" and literal["risk_words"] == ["carefully"]

    def test_every_how_bold_word_of_the_table_is_read(self, world1805):
        from backend.ai import task_words as TW
        world = _fresh(world1805)
        for word in tuple(TW.BOLDER_WORDS) + tuple(TW.CAREFUL_WORDS):
            parsed = self._parse(world, f"Ney, hold Rhineland {word}")
            assert parsed["success"] and parsed["command"]["target"] == "Rhineland", word
            # row IC, Session 3: taken for a man who may be set on his own …
            assert parsed["own_risk_words"] == [word], word
            # … and set aside for a literal man
            literal = self._parse(world, f"Soult, hold Lorraine {word}")
            assert literal["risk_words"] == [word], word

    def test_a_posture_order_keeps_its_own_word(self, world1805):
        world = _fresh(world1805)
        parsed = self._parse(world, "Ney, aggressive stance")
        assert parsed["command"]["action"] == "stance_change" and "risk_words" not in parsed

    def test_an_if_thens_whatever_the_odds_is_its_own(self, world1805):
        world = _fresh(world1805)
        parsed = self._parse(world, "Soult, hold Lorraine. If Mack comes within reach, "
                                    "attack at any cost.")
        assert parsed["if_thens"][0]["any_odds"] is True and "risk_words" not in parsed

    def test_a_line_without_one_is_untouched(self):
        from backend.commands import if_thens as IT
        assert IT.set_aside_risk_words("Ney, attack Mack", ["Ney", "Mack"]) == (
            "Ney, attack Mack", [])
        # a word in a verb's place stays where today's readers found it
        text, found = IT.set_aside_risk_words("Ney, aggressively attack Mack", ["Ney", "Mack"])
        assert text == "Ney, aggressively attack Mack" and found == ["aggressively"]


# ═══════════════════ THE WORD TABLE — the census ════════════════════════════

_FILL = {"{enemy}": "Mack", "{friend}": "Ney", "{place}": "Rhineland", "{n}": "3"}


def _filled(phrase: str) -> str:
    for slot, word in _FILL.items():
        phrase = phrase.replace(slot, word)
    return phrase


class TestTheWordTable:
    """§8.3: ONE table (`backend/ai/word_table.py`); the parser's lists and the
    client's are GENERATED from it, so no word is promised that is not read.
    Every phrase of the generated lists is run through the real parser on the
    1805 board."""

    @pytest.fixture(scope="class")
    def parse(self, road):
        client, snap = road
        board = _board(snap)

        def run(line):
            with _quiet():
                return M.parser.parse(line, M.get_llm_game_state(), world=board)
        return run

    def test_both_generated_files_are_current(self):
        from tools import gen_routed_order_words, gen_task_words
        with _quiet():
            assert gen_task_words.main(["--check"]) == 0
            assert gen_routed_order_words.main(["--check"]) == 0

    def test_a_changed_table_makes_them_stale(self, monkeypatch):
        from backend.ai import word_table
        from tools import gen_task_words
        monkeypatch.setattr(word_table, "FILLER", word_table.FILLER + ("if it suits",))
        with _quiet():
            assert gen_task_words.main(["--check"]) == 1
        rendered = gen_task_words.render_py(gen_task_words.build())
        assert "'if it suits'" in rendered

    def test_a_new_task_words_verb_reaches_the_addressee_rule(self):
        """The AST trap: the new task words are restated before the keyword
        chain, so the routed-words harvest reads them from `TASK_VERBS`."""
        from backend.ai import task_words as TW
        from backend.ai.routed_order_words import ROUTED_ORDER_WORDS
        from tools import gen_routed_order_words as GEN
        assert set(TW.TASK_VERBS) <= set(ROUTED_ORDER_WORDS)
        source = GEN.TASK_WORDS_PATH.read_text(encoding="utf-8")
        mutated = source.replace("TASK_VERBS = (", "TASK_VERBS = (\n    'zapfenstreich',", 1)
        assert mutated != source
        assert "zapfenstreich" in GEN.harvest(task_words_source=mutated)
        assert "zapfenstreich" not in GEN.harvest()

    def test_every_if_phrase_is_read_to_its_if(self, parse):
        from backend.ai import task_words as TW
        wrong = []
        for marker, table in (("if", TW.IF_PHRASES), ("should", TW.IF_SHOULD_PHRASES)):
            for name, slot, phrase in table:
                line = f"Soult, hold Lorraine. {marker.capitalize()} {_filled(phrase)}, dig in."
                got = parse(line)
                lines = got.get("if_thens") or []
                if not (got.get("success") and len(lines) == 1 and lines[0]["if"] == name
                        and lines[0]["then"] == "dig_in"
                        and (slot != "enemy" or lines[0]["who"] == "Mack")
                        and (slot != "friend" or lines[0]["friend"] == "Ney")
                        and (slot != "place" or lines[0]["place"] == "Rhineland")):
                    wrong.append((line, got.get("error") or lines))
        assert not wrong, wrong[:5]
        assert len(TW.IF_PHRASES) + len(TW.IF_SHOULD_PHRASES) > 100

    def test_every_then_phrase_is_read_to_its_then(self, parse):
        from backend.ai import task_words as TW
        wrong = []
        for name, any_odds, phrase in TW.THEN_PHRASES:
            head = "If Ney is attacked next to you" if name == "join" else "If attacked"
            line = f"Soult, hold Lorraine. {head}, {_filled(phrase)}."
            got = parse(line)
            lines = got.get("if_thens") or []
            if not (got.get("success") and len(lines) == 1 and lines[0]["then"] == name
                    and bool(lines[0]["any_odds"]) == bool(any_odds)
                    and (name not in ("fall_back", "march") or lines[0]["to"] == "Rhineland")):
                wrong.append((line, got.get("error") or lines))
        assert not wrong, wrong[:5]

    def test_every_if_word_opens_a_line(self, parse):
        from backend.ai import task_words as TW
        assert set(TW.IF_MARKERS) == {"if", "when", "should", "in case"}
        for marker, body in (("if", "Mack advances"), ("when", "Mack advances"),
                             ("should", "Mack advance"), ("in case", "Mack advances")):
            got = parse(f"Ney, {marker} {body}, fall back to Lorraine")
            assert got.get("success") and got["if_thens"][0]["who"] == "Mack", marker

    def test_every_task_word_gives_its_standing_order(self, parse):
        from backend.ai import task_words as TW
        objects = {"enemy": ("Ney", "Mack"), "place": ("Ney", "Lorraine"), "friend": ("Soult", "Ney")}
        wrong = []
        for order, row in TW.TASKS.items():
            who, obj = objects[row["object"]]
            lines = [f"{who}, {word} {obj}" for word in list(row["words"]) + list(row["new"])]
            lines += [f"{who}, {word}" for word in row["bare"]]
            for line in lines:
                got = parse(line)
                if not (got.get("success") and got.get("is_strategic")
                        and got.get("strategic_type") == order):
                    wrong.append((line, got.get("strategic_type"),
                                  (got.get("command") or {}).get("action")))
        assert not wrong, wrong

    def test_the_new_task_words_bind_only_to_their_object(self, parse):
        """ "keep" is a hold only before a province; "stay with" a follow only
        before one of our men — whatever stands behind the name is the other
        readers' (the metamorphic ratchet found the first cut losing it)."""
        assert parse("Ney, keep an eye on Swabia")["command"]["action"] == "scout"
        for line in ("Davout, keep Lorraine because the men are ready",
                     "Davout, keep Lorraine - at once",
                     "Davout, keep Lorraine with Lannes in support"):
            assert parse(line).get("strategic_type") == "HOLD", line
        assert parse("Soult, stay with Ney because he is weak").get("strategic_type") == "SUPPORT"

    def test_every_how_long_is_a_condition_the_grammar_reads(self, parse):
        from backend.ai import condition_grammar as CG
        from backend.ai import task_words as TW
        assert {key for key, _say in TW.HOW_LONG} == {key for key, _rx in CG._READ_CLAUSES}
        for key, say in TW.HOW_LONG:
            head = "Ney, pursue Mack" if key == "until_marshal_destroyed" else "Ney, hold Rhineland"
            said = _filled(say).replace("until Ney arrives", "until Davout arrives")
            got = parse(f"{head} {said}")
            cond = got.get("strategic_condition") or {}
            want = "max_turns" if key == "until_turn" else key
            assert got.get("success") and cond.get(want), (key, got.get("error"), cond)

    def test_every_arrival_then_is_an_arrival_verb(self, parse):
        from backend.ai import strategic_parser as SP
        from backend.ai import task_words as TW
        assert set(TW.ARRIVAL_THENS.values()) == set(SP.ARRIVAL_VERBS)
        for phrase, verb in TW.ARRIVAL_THENS.items():
            got = parse(f"Ney, march to Lorraine then {phrase}")
            assert got.get("success") and got.get("arrival_verb") == verb, phrase

    def test_every_filler_clause_is_under_the_guards_floor(self, parse):
        from backend.ai import task_words as TW
        for clause in TW.FILLER:
            got = parse(f"Ney, attack Mack {clause}")
            assert got.get("success") and got["command"]["action"] == "attack", clause
            assert [b["clause"] for b in got.get("blanked_clauses") or []] == [clause], clause

    def test_the_read_back_says_each_part_it_took(self, road):
        """On the READ-BACK too: one sentence per IF and per THEN."""
        from backend.commands import if_thens as IT
        client, snap = road
        _board(snap)
        for line in ("Soult, hold Lorraine. If an enemy comes within reach, attack.",
                     "Soult, hold Lorraine. If Mack comes within reach, attack whatever the odds.",
                     "Soult, hold Lorraine. If attacked, dig in.",
                     "Soult, hold Lorraine. If outnumbered, fall back on Champagne.",
                     "Soult, hold Lorraine. If you are being surrounded, march to Champagne.",
                     "Soult, hold. If Ney is attacked next to you, join his battle.",
                     "Soult, hold Lorraine. If Rhineland falls, march to Rhineland.",
                     "Soult, hold Lorraine. If Ney arrives, attack."):
            reading = _preview(client, line)
            with _quiet():
                parsed = M.parser.parse(line, M.get_llm_game_state(), world=M.world)
            assert reading["kind"] == "order" and reading["understood"] == "", (line, reading)
            assert _parts(reading, "taken") == [IT.describe(row) for row in parsed["if_thens"]], line

    def test_every_example_the_help_teaches_reads_back_clean(self, road):
        from backend.ai import task_words as TW
        client, snap = road
        assert len(TW.EXAMPLES) == 6
        with_a_part = 0
        for line in TW.EXAMPLES:
            _board(snap)
            reading = _preview(client, line)
            assert reading["kind"] == "order" and reading["ok"], (line, reading)
            assert not _roles(reading, "nottaken") and reading["understood"] == "", (line, reading)
            with_a_part += bool(_parts(reading, "taken"))
            _board(snap)
            reply = _post(client, line, typed=True)
            assert reply.get("success"), (line, reply.get("message"))
        # all but the bare "Soult, follow Ney." carry a part the read-back names
        assert with_a_part == 5


# ═══════════════════ what the line refuses (§8.3) ═══════════════════════════

class TestWhatTheLineRefuses:
    """§8.3: "What the line refuses — free, with the nearest real sentence
    already written in." Each of these was read as something ELSE before:
    a march to hold a province called "Between Munich", an attack on the
    province of Maine, a hold with no limit."""

    @pytest.mark.parametrize("line, short, offers", [
        ("Davout, hold between Munich and Vienna",
         "Name one province — a corps holds a province, not a stretch between two",
         ["Davout, hold Munich", "Davout, hold Vienna"]),
        ("Davout, hold the line of the Inn",
         "Name one province — a corps holds a province, not a line",
         ["Davout, hold Rhineland"]),
        ("Ney, attack their main army",
         "Name its commander — an order goes against a man, not an army",
         ["Ney, attack Mack", "Ney, attack Archduke John"]),
    ])
    def test_a_stretch_and_their_main_army_are_refused_free_on_both_roads(self, road, line,
                                                                          short, offers):
        client, snap = road
        board = _board(snap)
        reading = _preview(client, line)
        assert reading["kind"] == "refusal" and _parts(reading, "bad") == [short]
        assert [c["line"] for c in reading["candidates"]] == offers
        actions = int(board.actions_remaining)
        where = {m.name: m.location for m in board.get_player_marshals()}
        reply = _post(client, line)
        assert reply["success"] is False and reply["offers"] == offers
        assert "Nothing has been relayed" in reply["message"] and offers[0] in reply["message"]
        assert int(board.actions_remaining) == actions
        assert {m.name: m.location for m in board.get_player_marshals()} == where
        assert all(m.strategic_order is None for m in board.get_player_marshals())

    def test_every_offered_sentence_is_an_order_the_line_takes(self, road):
        client, snap = road
        for line in ("Davout, hold between Munich and Vienna", "Davout, hold the line of the Inn",
                     "Ney, attack their main army"):
            _board(snap)
            for offer in _preview(client, line)["candidates"]:
                _board(snap)
                again = _preview(client, offer["line"])
                assert again["kind"] == "order" and again["ok"], (offer, again)

    def test_only_a_commander_france_can_see_is_offered(self, road):
        """R5: "their main army" never names a man out of sight."""
        client, snap = road
        board = _board(snap)
        seen = {m.name for m in board.get_visible_enemies(board.player_nation)}
        hidden = [m for m in board.marshals.values()
                  if m.nation != board.player_nation and m.name not in seen]
        assert hidden, "the premise: some commander is out of France's sight"
        from backend.display_names import humanize_entity_name
        offered = " ".join(c["line"] for c in
                           _preview(client, "Ney, attack their main army")["candidates"])
        assert not [m.name for m in hidden if humanize_entity_name(m.name) in offered]

    def test_the_lines_beside_them_read_as_they_did(self, road):
        client, snap = road
        _board(snap)
        assert _preview(client, "Ney, hold the line")["kind"] == "order"
        assert _preview(client, "Ney, hold Rhineland")["kind"] == "order"
        from backend.commands import task_line as TL
        friends, places = ["Ney", "Davout"], ["Munich", "Vienna", "Paris", "Lorraine"]
        assert TL.refusal(None, "Ney, march along the road to Paris", friends, places) is None
        assert TL.refusal(None, "Ney, choose between attack and retreat", friends, places) is None
        assert TL.refusal(None, "hold between Munich and Vienna", friends, places) is None, \
            "nobody of ours is addressed: the old readers'"

    @pytest.mark.parametrize("line, phrase", [
        ("Ney, hold Rhineland through the winter", "through the winter"),
        ("Ney, hold Rhineland for two weeks", "for two weeks"),
        ("Ney, hold Rhineland as long as it takes", "as long as it takes"),
    ])
    def test_a_loose_time_is_named_and_offered_in_turns(self, road, line, phrase):
        from backend.commands import task_line as TL
        client, snap = road
        board = _board(snap)
        reading = _preview(client, line)
        assert reading["kind"] == "order" and _parts(reading, "head") == ["Ney · hold Rhineland"]
        (row,) = _roles(reading, "nottaken")
        assert row == {"role": "nottaken", "blocks": True,
                       "text": f"‘{phrase}’ — {TL.WHY_LOOSE_TIME}"}
        assert reading["understood"] == "Ney, hold Rhineland"
        assert [c["line"] for c in reading["candidates"]] == ["Ney, hold Rhineland for 3 turns"]
        # ... the parse itself is the clean hold (the words used to swallow the place)
        with _quiet():
            parsed = M.parser.parse(line, M.get_llm_game_state(), world=board)
        assert parsed["command"]["target"] == "Rhineland" and parsed["loose_time"] == [phrase]
        assert not parsed.get("strategic_condition")

    def test_for_now_asks_for_no_limit_and_is_left_alone(self):
        from backend.commands import task_line as TL
        for line in ("Ney, hold your position for now", "Ney, hold Rhineland for a while",
                     "Ney, hold Rhineland for 3 turns", "Ney, hold Rhineland until turn 9"):
            assert TL.set_aside_loose_time(line) == (line, []), line

    def test_a_tail_no_marshals_order_carries_is_named(self, road):
        from backend.commands import task_line as TL
        client, snap = road
        _board(snap)
        reading = _preview(client, "Ney, hold Rhineland and build a fort")
        (row,) = _roles(reading, "nottaken")
        assert row["blocks"] and row["text"] == f"‘and build a fort’ — {TL.WHY_NOT_A_MARSHALS}"
        assert reading["understood"] == "Ney, hold Rhineland"
        # a tail the relay already offers back is the relay's, said once
        relayed = _preview(client, "Ney, hold Rhineland then recruit")
        assert not _roles(relayed, "nottaken")
        assert "a second order waits behind it" in _parts(relayed, "warn")

    def test_a_leading_first_no_longer_drops_the_first_order(self, road):
        client, snap = road
        board = _board(snap)
        with _quiet():
            parsed = M.parser.parse("Murat, first take Swabia then support Soult",
                                    M.get_llm_game_state(), world=board)
        assert parsed["success"] and parsed["command"]["target"] == "Swabia"
        assert parsed["dropped_sequel"] == "support Soult"
        assert parsed["raw_input"] == "Murat, first take Swabia then support Soult"

    def test_a_contingency_is_offered_back_as_the_exact_order_it_means(self, road):
        client, snap = road
        board = _board(snap)
        line = "Ney, hold Rhineland unless Mack advances"
        offer = "Ney, hold Rhineland. If Mack comes within reach, fall back to Lorraine."
        reading = _preview(client, line)
        assert reading["kind"] == "refusal"
        assert [c["line"] for c in reading["candidates"]] == [offer]
        reply = _post(client, line)
        assert reply["success"] is False and f"Did you mean: '{offer}'?" in reply["message"]
        assert board.marshals["Ney"].strategic_order is None
        _board(snap)
        sent = _post(client, offer, typed=True)
        assert sent.get("success"), sent.get("message")

    def test_a_contingency_the_table_cannot_say_offers_nothing(self, road):
        client, snap = road
        _board(snap)
        reading = _preview(client, "Ney, attack Mack if the moon is full")
        assert reading["kind"] == "refusal" and reading["candidates"] == []
        reply = _post(client, "Ney, attack Mack if the moon is full")
        assert reply["success"] is False and "Did you mean" not in reply["message"]


# ═══════════════════ "Give him a task…" — the line is never blank ═══════════

class TestGiveHimATask:
    """§8.2: the general's card opens the line ALREADY WRITTEN — ready
    sentences with real names (`GET /task_presets`). Nothing is sent."""

    @staticmethod
    def _presets(client, name):
        with _quiet():
            return client.get("/task_presets", params={"marshal": name}).json()

    def test_a_literal_man_is_offered_exact_orders(self, road):
        client, snap = road
        board = _board(snap)
        got = self._presets(client, "Soult")
        assert got["success"] and got["literal"] is True and got["if_thens"] == 3
        lines = [row["line"] for row in got["presets"]]
        assert lines[0] == "Soult, hold Lorraine. If outnumbered, fall back to Franche-Comte."
        assert all(line.startswith("Soult, hold Lorraine. If ") for line in lines)
        assert {row["price"] for row in got["presets"]} == {"1 action"}
        assert board.marshals["Soult"].strategic_order is None, "asking gives no order"

    def test_anyone_else_is_offered_standing_orders_with_their_parts(self, road):
        client, snap = road
        _board(snap)
        ney = self._presets(client, "Ney")
        assert ney["literal"] is False and ney["if_thens"] == 1
        # row IC, Session 3: a bold or careful man who may be set on his own
        # is offered HIS OWN proposal first (`own_order.proposal`)
        assert [row["label"] for row in ney["presets"]] == [
            "On his own: hold Rhineland — his idea", "Chase Mack", "Hold for three turns",
            "Hold; if attacked, dig in"]
        # a careful man's first sentence is the hold, a bold man's the chase
        davout = self._presets(client, "Davout")
        # (row IC, Session 3: after his own proposal — on his own, he holds and digs in)
        assert davout["presets"][0]["line"] == "Davout, hold Rhineland on your own."
        assert davout["presets"][1]["line"] == "Davout, hold Rhineland for 3 turns."

    def test_every_preset_of_every_marshal_reads_back_clean_and_is_taken(self, road):
        client, snap = road
        board = _board(snap)
        names = [m.name for m in board.get_player_marshals()]
        offered = 0
        for name in names:
            _board(snap)
            for row in self._presets(client, name)["presets"]:
                offered += 1
                _board(snap)
                reading = _preview(client, row["line"])
                assert reading["kind"] == "order" and reading["ok"], (row, reading)
                assert reading["understood"] == "" and not _roles(reading, "nottaken"), row
                assert _parts(reading, "cost") == [row["price"]], row
                reply = _post(client, row["line"], typed=True)
                assert reply.get("success"), (row, reply.get("message"))
        assert offered >= 3 * len(names) - 2

    def test_an_enemy_out_of_sight_is_never_named(self, road):
        client, snap = road
        board = _board(snap)
        from backend.display_names import humanize_entity_name
        seen = {m.name for m in board.get_visible_enemies(board.player_nation)}
        hidden = [humanize_entity_name(m.name) for m in board.marshals.values()
                  if m.nation != board.player_nation and m.name not in seen]
        said = " ".join(row["line"] for m in board.get_player_marshals()
                        for row in self._presets(client, m.name)["presets"])
        assert hidden and not [name for name in hidden if name in said]

    def test_only_our_own_marshals_in_the_field(self, road):
        client, snap = road
        board = _board(snap)
        assert self._presets(client, "Mack")["success"] is False
        assert self._presets(client, "Nobody")["success"] is False
        board.marshals["Ney"].strength = 0
        assert self._presets(client, "Ney")["success"] is False

    def test_the_first_task_carries_its_first_open_line(self, road):
        from backend.game_logic import first_open
        client, snap = road
        board = _board(snap)
        got = self._presets(client, "Ney")
        assert got["first_open"]["screen"] == "task"
        line = got["first_open"]["line"]
        assert line.startswith("A task is typed, Sire") and len(line) <= first_open.LINE_CAP
        assert first_open.mark_seen(board, "task") is True
        board.current_turn += 1
        assert "first_open" not in self._presets(client, "Ney")

    def test_it_is_a_pure_read(self, road):
        client, snap = road
        board = _board(snap)
        before = json.dumps(board.to_dict(), sort_keys=True, default=str)
        state = random.getstate()
        for m in board.get_player_marshals():
            self._presets(client, m.name)
        assert random.getstate() == state
        assert json.dumps(board.to_dict(), sort_keys=True, default=str) == before


# ═══════════════════ the word-chips — what the line could carry next ════════

class TestTheWordChips:
    """§8.2: "Word-chips under the line write into the sentence: until… · for
    N turns · if…". They are the read-back's own fill chips (`candidates`):
    a press writes the words in place, nothing is sent."""

    @staticmethod
    def _chips(client, line):
        return [(c["label"], c["line"]) for c in _preview(client, line)["candidates"]]

    def test_a_plain_hold_offers_how_long_and_an_if(self, road):
        client, snap = road
        _board(snap)
        assert self._chips(client, "Soult, hold Lorraine") == [
            ("+ for 3 turns", "Soult, hold Lorraine for 3 turns"),
            ("+ until Davout arrives", "Soult, hold Lorraine until Davout arrives"),
            ("+ If attacked, dig in", "Soult, hold Lorraine. If attacked, dig in.")]

    def test_a_chase_offers_its_own_ending(self, road):
        client, snap = road
        _board(snap)
        assert self._chips(client, "Murat, chase Mack") == [
            ("+ for 3 turns", "Murat, chase Mack for 3 turns"),
            ("+ until he is destroyed", "Murat, chase Mack until he is destroyed")]

    def test_the_next_if_then_is_offered_while_his_order_may_carry_one(self, road):
        client, snap = road
        _board(snap)
        # a marshal who follows orders to the letter: up to three
        assert self._chips(client, "Soult, hold Lorraine. If attacked, dig in.") == [
            ("+ If outnumbered, fall back to Franche-Comte",
             "Soult, hold Lorraine. If attacked, dig in. If outnumbered, fall back to "
             "Franche-Comte.")]
        # anyone else: one, on a hold — none is offered once he has it
        assert self._chips(client, "Ney, hold Rhineland. If attacked, dig in.") == []
        # ... and none on a march, which carries no if-then for him
        assert self._chips(client, "Ney, march to Lorraine") == []

    def test_a_one_turn_order_offers_none(self, road):
        client, snap = road
        _board(snap)
        for line in ("Ney, attack Mack", "Ney, fortify", "Ney, defend"):
            assert self._chips(client, line) == [], line

    def test_nothing_is_offered_while_a_part_blocks(self, road):
        """The blocking row's own offer (the if-then it means) stands alone."""
        client, snap = road
        _board(snap)
        assert self._chips(client, "Ney, hold Rhineland unless attacked") == [
            ("Ney, hold Rhineland. If he is attacked, fall back to Lorraine.",
             "Ney, hold Rhineland. If he is attacked, fall back to Lorraine.")]

    def test_every_chip_writes_a_line_the_game_takes_with_that_part(self, road):
        client, snap = road
        for line in ("Soult, hold Lorraine", "Murat, chase Mack", "Ney, hold Rhineland",
                     "Davout, follow Soult", "Soult, hold Lorraine. If attacked, dig in."):
            _board(snap)
            for label, written in self._chips(client, line):
                _board(snap)
                again = _preview(client, written)
                assert again["kind"] == "order" and again["ok"], (label, again)
                assert again["understood"] == "" and _parts(again, "taken"), (label, again)

    def test_at_most_three(self, road):
        client, snap = road
        _board(snap)
        for m in ("Ney", "Davout", "Soult", "Lannes", "Murat"):
            assert len(self._chips(client, f"{m}, hold")) <= PP.CONTINUATIONS_MAX


# ═══════════════════════════ the review's rows ══════════════════════════════

class TestTheReviewsRowsOnTheLine:
    """The one review before the commit (three readers on a frozen copy):
    its rows on the typed line, each a behaviour pinned here."""

    def test_a_part_that_blocks_with_no_clean_line_still_holds_the_line(self, road):
        """L3: where the restated line would NOT be the same order, the part
        used to stop blocking — and the typed line went out without it."""
        from backend.commands import parse_preview as PP
        client, snap = road
        board = _board(snap)
        parsed = M.parser.parse("Ney, retreat if outnumbered", M.get_llm_game_state(),
                                world=board)
        assert parsed.get("blanked_clauses")

        def reads_differently(line):
            return {"success": True, "command": {"marshal": "Ney", "action": "attack",
                                                 "target": "Mack"}}

        line, rows = PP.understood_line(board, parsed, "Ney, retreat if outnumbered",
                                        reads_differently)
        assert line == "" and [row["blocks"] for row in rows] == [True]
        held = PP.typed_gate(board, parsed, "Ney, retreat if outnumbered", reads_differently)
        assert held is not None and held["understood"] == ""
        assert "Type the order again without it." in held["message"]
        assert "What I understood is" not in held["message"]
        # a reader with no second read at all (a nested reading) blocks nothing
        line, rows = PP.understood_line(board, parsed, "Ney, retreat if outnumbered", None)
        assert line == "" and [row["blocks"] for row in rows] == [False]

    def test_the_forced_second_read_keeps_what_the_guard_blanked(self):
        """L3b: `reparse_with_llm`'s answer carries the fast parser's own
        numbers and the clauses its guard blanked (read off its source: the
        live model is never called by a test)."""
        import inspect

        from backend.ai import llm_client
        body = inspect.getsource(llm_client.LLMClient.reparse_with_llm)
        for key in ("fast_ambiguity", "fast_strategic_score", "blanked_clauses"):
            assert key in body, key

    def test_the_army_as_a_whole_is_held_like_one_man(self, road):
        """IC-V1's sibling (the review's sweep): "everyone retreat if
        outnumbered" sent every corps back with the condition dropped unsaid —
        the one order to all that has no list first."""
        client, snap = road
        board = _board(snap)
        reading = _preview(client, "everyone retreat if outnumbered")
        assert _parts(reading, "nottaken") == [
            "‘if outnumbered’ — this order takes no condition; it would go out now"]
        assert reading["understood"] == "everyone retreat"
        before = {m.name: m.location for m in board.get_player_marshals()}
        reply = _post(client, "everyone retreat if outnumbered", typed=True)
        assert reply["success"] is False and reply["refusal"] == "not_taken"
        assert reply["understood"] == "everyone retreat"
        assert {m.name: m.location for m in board.get_player_marshals()} == before
        # words that change nothing do not hold it
        assert _preview(client, "general retreat when ready")["understood"] == ""
        # an order to several corps shows it on every row of its list instead
        with _quiet():
            got = client.get("/directive_quote",
                             params={"line": "all corps fortify if attacked"}).json()
        rows = got["directive"]["rows"]
        assert rows and all(any("not taken: ‘if attacked’" in note for note in row["notes"])
                            for row in rows)

    def test_our_own_main_army_is_no_refusal(self, road):
        """L1: "the main army" by itself is ours as readily as theirs; only
        the enemy's, as the object of a fighting word, is refused."""
        from backend.commands import task_line as TL
        client, snap = road
        board = _board(snap)
        friends = [m.name for m in board.get_player_marshals()]
        places = list(board.regions)
        for line in ("Ney, support the main army", "Davout, join the main army at Lorraine",
                     "Ney, march to the main army", "Ney, their main army is near — hold Rhineland"):
            assert TL.refusal(board, line, friends, places) is None, line
        for line in ("Ney, attack their main army", "Ney, attack the main Austrian army",
                     "Ney, chase the enemy's main body", "Ney, attack the main enemy army"):
            got = TL.refusal(board, line, friends, places)
            assert got is not None and "Name its commander" in got["error"], line

    def test_a_time_limit_on_the_second_order_is_not_the_firsts(self, road):
        """L4: "for 3 turns" on the order the relay holds back."""
        client, snap = road
        _board(snap)
        reading = _preview(client, "Ney, fortify, then hold Lorraine for 3 turns")
        assert _parts(reading, "nottaken") == [] and reading["understood"] == ""
        assert "a second order waits behind it" in _parts(reading, "warn")
        # ... and on the order itself it still is
        assert _parts(_preview(client, "Ney, fortify for 3 turns"), "nottaken") == [
            "‘for 3 turns’ — this order has no time limit; it is carried out once, now"]

    def test_a_river_word_in_another_clause_is_no_line_to_hold(self, road):
        """L5: the holding word must stand in the SAME clause."""
        from backend.commands import task_line as TL
        client, snap = road
        board = _board(snap)
        friends = [m.name for m in board.get_player_marshals()]
        places = list(board.regions)
        assert TL.refusal(board, "Ney, hold Lorraine, then march along the road to Champagne",
                          friends, places) is None
        got = TL.refusal(board, "Ney, hold the line of the Rhine", friends, places)
        assert got is not None and "not a line" in got["error"]

    def test_a_loose_time_ends_its_clause(self, road):
        """L7: "during the fall of Vienna" is no season."""
        from backend.commands import task_line as TL
        assert TL.set_aside_loose_time("Ney, attack Mack during the fall of Vienna") == (
            "Ney, attack Mack during the fall of Vienna", [])
        assert TL.set_aside_loose_time("Ney, hold Rhineland through the winter") == (
            "Ney, hold Rhineland", ["through the winter"])
        assert TL.set_aside_loose_time("Ney, hold Rhineland through the winter, then drill")[1] == [
            "through the winter"]

    def test_only_raising_men_is_the_states_work(self):
        from backend.commands import task_line as TL
        assert TL.forbidden_tail("Ney, march to Lorraine and raise the alarm") == ""
        assert TL.forbidden_tail("Ney, march to Lorraine and raise troops") == "and raise troops"
        assert TL.forbidden_tail("Ney, march to Lorraine, then recruit") == "then recruit"
        assert TL.forbidden_tail("Ney, march to Lorraine and sign for the stores") == ""

    def test_the_reasons_are_in_plain_words(self):
        """W4, W5: the two reasons a reader had to guess at."""
        from backend.commands import parse_preview as PP
        assert PP.WHY_NOT_HELD == ("not an end this order can keep; it would go on until you "
                                   "change it")
        assert PP.WHY_REASON == "taken as your reason, not as a condition; he acts now"


class TestICN1TheReadBackOfARenewedHold:
    """`BUG_FIXES.md` IC4-N1 (found by row IC, Session 4, in the last commit
    too — owner row IC Session 4b): given a hold with new if-thens on the ground
    he already holds, the read-back REFUSES it ("already holding here", a free
    refusal) while Enter GIVES it and charges an action. A button says what it
    will do before the press: the reading must be the order. STRICT — the day it
    is fixed (Session 4b) the pin below holds."""

    def test_the_reading_of_a_renewed_hold_is_what_enter_does(self, road):
        client, snap = road
        board = _board(snap)
        board.actions_remaining = 12
        assert _post(client, "Soult, hold Lorraine. If attacked, dig in.")["success"]
        line = "Soult, hold Lorraine. If outnumbered, fall back on Champagne."
        reading = _preview(client, line)
        sent = _post(client, line)
        assert sent["success"], sent.get("message")
        assert reading.get("ok") is True and reading.get("kind") == "order", reading

    def test_an_identical_renewed_hold_still_reads_already_holding(self, road):
        client, snap = road
        board = _board(snap)
        board.actions_remaining = 12
        line = "Soult, hold Lorraine. If attacked, dig in."
        assert _post(client, line)["success"]
        reading = _preview(client, line)
        assert reading.get("ok") is False
        assert "already holding here" in str(reading), reading

    def test_a_hold_of_another_province_reads_as_the_order_enter_gives(self, road):
        """Session 4b's review of the fix: the typed hold's PLACE sits on the
        parse's command (where the executor reads it). Read from the wrong key
        it was always "where he stands", so a hold of ANOTHER province, given
        while he holds his own, read "already holding here"."""
        import backend.main as M
        from backend.commands.state_probe import order_state_refusal
        client, snap = road
        board = _board(snap)
        board.actions_remaining = 12
        soult = board.get_marshal("Soult")
        assert _post(client, f"Soult, hold {soult.location}")["success"]
        other = sorted(board.regions[soult.location].adjacent_regions)[0]
        with _quiet():
            elsewhere = M.parser.parse(f"Soult, hold {other}", {"world": board}, world=board)
            here = M.parser.parse("Soult, hold here", {"world": board}, world=board)
        assert (elsewhere.get("command") or {}).get("target") == other, elsewhere
        assert order_state_refusal(board, soult, "hold", parsed=elsewhere) == ""
        assert order_state_refusal(board, soult, "hold", parsed=here) == "already holding here"
