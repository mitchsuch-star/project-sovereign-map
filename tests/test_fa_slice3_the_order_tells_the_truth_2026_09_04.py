"""Final Whole-Game Audit — slice 3, "The Order Tells the Truth".

Eleven sites in `strategic.py` / `strategic_executor.py` execute an attack
for a standing order, and exactly one of them read the executor's answer
before narrating it. Reproduced on the shipped 1805 boot (Ney at Normandy,
Moore at London, the Royal Navy commanding the Channel — the executor's
crossing gate REFUSES the attack):

* **FA-14 / FA-19** — the refusal became "attacked Moore during march but
  the battle was inconclusive. Continue move to?", a `combat_stalemate`
  interrupt, a charged `combat_attempts`, and a corrupted combat record.
* **FA-15** — the cautious twin ASKED "Enemy at London. How shall I
  proceed?" and offered an 'attack' the executor would refuse; answered, it
  read "Davout attacks Moore. <barred> Assault failed — orders cancelled".
* **FA-20** — a refused first-step attack left a PHANTOM order standing at
  0 AP (in the Orders ledger), which fired next turn into FA-14.
* **FA-34** — the stalemate popup's "Continue as Ordered" CANCELLED the
  order; the copy carried the raw enum ("Continue move to?").
* **FA-N40 / FA-N26** — the HOLD sally narrated a refused sortie as
  "sallies forth to attack Moore, then returns to Normandy!" every turn.
* **FA-N10** — a real battle under a standing order reached the client with
  no casualty text: `_combat_carry` omitted the one key the renderers read.
* **FA-N42 / FA-N48** — the first-step auto-attack's success branch rebuilt
  a fresh dict and dropped the report, diorama, events and the war-purpose
  HARD STOP.
* **FA-N60** — the stored interrupt carried no `message`, so the popup read
  "Awaiting your orders, Sire."
* **FA-68** — the processor broke after the first marshal awaiting input;
  the second lost his turn and his question.
* the unfiled PURSUE arm — a refused attack COMPLETED the pursuit with the
  refusal as its reason and the aggressive completion line appended.
"""

import contextlib
import io
import os

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import strategic as strategic_mod
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser
from backend.commands.strategic import (
    _COMBAT_PASSTHROUGH_FIELDS,
    StrategicOrderProcessor,
    _combat_carry,
    attack_was_refused,
    refusal_keys,
    refusal_reason,
    strike_crossing_verdict,
)
from backend.models.marshal import StrategicOrder
from backend.models.world_state import WorldState

from tests.conftest import MarshalFactory, WorldFactory

SCENARIO = "godot-client/project-sovereign/assets/maps/europe_1805.json"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _boot():
    os.environ.pop("SOVEREIGN_SCENARIO", None)
    with _quiet():
        return WorldState.from_scenario(SCENARIO)


@pytest.fixture
def channel():
    """The shipped board with Ney (aggressive) and Davout (cautious) on the
    Normandy shore, Moore at London, the Royal Navy covering the water."""
    world = _boot()
    ney = world.get_marshal("Ney")
    davout = world.get_marshal("Davout")
    moore = world.get_marshal("Moore")
    ney.location = "Normandy"
    davout.location = "Normandy"
    moore.location = "London"
    moore.strength = 20000
    world.invalidate_active_nations_cache()
    world._build_marshal_index()
    world.calculate_visibility()
    verdict = strike_crossing_verdict(world, ney, "London")
    assert verdict is not None and verdict.get("allowed") is False, verdict
    return world


@pytest.fixture
def shipped(monkeypatch):
    """A fresh SHIPPED 1805 world at all three seams, with a mock parser."""
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False
    return TestClient(M.app), M.world


def _post(client, command):
    """POST /command, insisting through a marshal's objection if one is
    raised first (the cautious marshals object to a march on London)."""
    with _quiet():
        reply = client.post("/command", json={"command": command}).json()
        if reply.get("pending_objection") or reply.get("state") == "awaiting_player_choice":
            reply = client.post("/respond_to_objection", json={"choice": "insist"}).json()
    return reply


def _order(command_type, target, path=None, **kw):
    return StrategicOrder(command_type=command_type, target=target,
                          target_type=kw.pop("target_type", "region"),
                          started_turn=0, issued_turn=0, path=path or [],
                          original_command=f"x, {command_type} {target}", **kw)


def _tick(world):
    proc = StrategicOrderProcessor(CommandExecutor())
    with _quiet():
        return proc.process_strategic_orders(world, {"world": world}), proc


def _battles(world):
    return len(getattr(world, "battles_this_turn", []) or [])


REFUSAL = {"success": False, "message": "the crossing is barred — 100 sail",
           "blocked_naval": "Britain", "naval_ratio": 0.54}


# ═══════════════════════════════════════════════════════════════════════
# The predicate
# ═══════════════════════════════════════════════════════════════════════

class TestThePredicate:

    def test_a_refusal_is_success_false_with_no_battle(self):
        assert attack_was_refused(REFUSAL) is True
        assert refusal_reason(REFUSAL).startswith("the crossing is barred")
        assert refusal_keys(REFUSAL) == {"blocked_naval": "Britain", "naval_ratio": 0.54}

    @pytest.mark.parametrize("result", [
        {"events": [{"type": "battle", "victor": "Ney"}]},          # FA-N3 fixture: no success key
        {"success": True, "events": [{"type": "battle"}]},
        {"success": False, "events": [{"type": "battle", "outcome": "stalemate"}]},
        {"success": False, "events": [{"type": "glorious_charge", "attacker_won": False}]},
        {"success": False, "battle_result": {"victor": "Mack"}},
        None, "not a dict",
    ])
    def test_a_fought_battle_or_a_foreign_shape_is_never_a_refusal(self, result):
        assert attack_was_refused(result) is False

    def test_a_dict_with_no_verdict_at_all_is_not_a_refusal(self):
        """Isolation pin for `is not False`: the FA-N3 fixtures carry no
        `success` key and no refusal keys either — `not success` would read
        them as refusals; `is not False` does not."""
        assert attack_was_refused({"message": "no verdict at all"}) is False
        assert attack_was_refused({"success": None, "message": "x"}) is False

    def test_the_reason_never_defaults_to_a_battle_word(self):
        assert refusal_reason({"success": False}) == "the attack could not be made"
        assert refusal_keys({"success": False}) == {}

    def test_the_crossing_verdict_is_the_executors_own(self, channel):
        ney = channel.get_marshal("Ney")
        verdict = strike_crossing_verdict(channel, ney, "London")
        assert verdict["coverer"] == "Britain"
        assert strike_crossing_verdict(channel, ney, "Paris") is None, "dry land"
        assert strike_crossing_verdict(channel, ney, ney.location) is None
        fleets = channel.fleets
        try:
            channel.fleets = None
            assert strike_crossing_verdict(channel, ney, "London") is None, "no naval layer"
        finally:
            channel.fleets = fleets


# ═══════════════════════════════════════════════════════════════════════
# FA-14 / FA-19 — the per-turn MOVE_TO across the Channel
# ═══════════════════════════════════════════════════════════════════════

class TestARefusedMarchIsNotABattle:

    def test_the_march_halts_at_the_waters_edge(self, channel):
        ney = channel.get_marshal("Ney")
        moore = channel.get_marshal("Moore")
        ney.strategic_order = _order("MOVE_TO", "London", path=["London"])
        before = (ney.strength, moore.strength, _battles(channel))
        reports, _ = _tick(channel)
        row = next(r for r in reports if r["marshal"] == "Ney")
        assert row["order_status"] == "breaks", row
        assert row["action"] == "attack_refused"
        assert row.get("blocked_naval") == "Britain"
        assert "water's edge" in row["message"]
        assert "inconclusive" not in row["message"]
        assert not row.get("requires_input")
        assert "outcome" not in row and "battle_message" not in row
        assert ney.pending_interrupt is None
        assert ney.strategic_order is None
        assert (ney.strength, moore.strength, _battles(channel)) == before

    def test_the_combat_record_is_untouched(self, channel):
        ney = channel.get_marshal("Ney")
        ney.last_combat_result = "victory"
        ney.in_combat_this_turn = False
        ney.strategic_order = _order("MOVE_TO", "London", path=["London"])
        _tick(channel)
        assert ney.last_combat_result == "victory"
        assert ney.in_combat_this_turn is False

    def test_a_fought_battle_still_narrates(self, channel):
        """Negative control: with the Royal Navy gone the same order FIGHTS,
        and the row carries an outcome and the casualty text (FA-N10)."""
        channel.fleets = None
        ney = channel.get_marshal("Ney")
        ney.strategic_order = _order("MOVE_TO", "London", path=["London"])
        reports, _ = _tick(channel)
        row = next(r for r in reports if r["marshal"] == "Ney")
        assert row.get("outcome") in ("victory", "defeat", "stalemate"), row
        assert row.get("battle_message"), row
        assert row["battle_message"] == row["battle_details"]["message"]
        assert _battles(channel) == 1

    def test_the_helper_breaks_the_order_with_the_reason(self, channel):
        """Direct: `_handle_combat_result` fed the executor's refusal dict."""
        ney = channel.get_marshal("Ney")
        moore = channel.get_marshal("Moore")
        ney.strategic_order = _order("MOVE_TO", "London", path=["London"])
        proc = StrategicOrderProcessor(CommandExecutor())
        row = proc._handle_combat_result(ney, moore, dict(REFUSAL), channel,
                                         {"world": channel})
        assert row["order_status"] == "breaks" and row["action"] == "attack_refused"
        assert row["blocked_naval"] == "Britain"
        assert "water's edge" in row["message"], row["message"]
        assert ney.strategic_order is None
        # A non-naval refusal is worded as a refusal, not as a shore.
        ney.strategic_order = _order("MOVE_TO", "London", path=["London"])
        row2 = proc._handle_combat_result(
            ney, moore, {"success": False, "message": "his guns are not set up"},
            channel, {"world": channel})
        assert "cannot attack Moore" in row2["message"] and "water" not in row2["message"]

    def test_an_order_free_refusal_still_says_why(self, channel):
        ney = channel.get_marshal("Ney")
        moore = channel.get_marshal("Moore")
        ney.strategic_order = None
        proc = StrategicOrderProcessor(CommandExecutor())
        row = proc._handle_combat_result(ney, moore, dict(REFUSAL), channel,
                                         {"world": channel})
        assert row["action"] == "attack_refused"
        assert "barred" in row["message"]


# ═══════════════════════════════════════════════════════════════════════
# FA-15 — the contact producers never ask about a shore the gate refuses
# ═══════════════════════════════════════════════════════════════════════

class TestNoQuestionIsAskedAboutABarredShore:

    def test_the_per_turn_cautious_march_breaks_instead_of_asking(self, channel):
        davout = channel.get_marshal("Davout")
        davout.strategic_order = _order("MOVE_TO", "London", path=["London"])
        reports, _ = _tick(channel)
        row = next(r for r in reports if r["marshal"] == "Davout")
        assert row["order_status"] == "breaks"
        assert not row.get("requires_input")
        assert davout.pending_interrupt is None
        assert "water's edge" in row["message"]

    def test_the_first_step_cautious_march_is_refused_free(self, shipped):
        client, world = shipped
        davout = world.get_marshal("Davout")
        davout.location = "Normandy"
        world.get_marshal("Moore").location = "London"
        world.calculate_visibility()
        ap = world.actions_remaining
        reply = _post(client, "Davout, march to London")
        davout = M.world.get_marshal("Davout")
        assert reply.get("success") is False, reply.get("message")
        assert reply.get("pending_interrupt") in (None, {}, False)
        assert "barred" in (reply.get("message") or "")
        assert davout.strategic_order is None, "no phantom order (FA-20)"
        assert davout.pending_interrupt is None
        assert M.world.actions_remaining == ap

    def test_the_first_step_aggressive_march_is_refused_free(self, shipped):
        """FA-20's own case: `Ney, march to London` from Normandy."""
        client, world = shipped
        ney = world.get_marshal("Ney")
        ney.location = "Normandy"
        world.get_marshal("Moore").location = "London"
        world.calculate_visibility()
        ap = world.actions_remaining
        reply = _post(client, "Ney, march to London")
        ney = M.world.get_marshal("Ney")
        assert reply.get("success") is False, reply.get("message")
        # (`order_cleared` / `blocked_naval` are not `/command` wire fields —
        # the main path's allowlist drops them; the WORLD is the contract.)
        assert "barred" in (reply.get("message") or "")
        assert ney.strategic_order is None, "no phantom order (FA-20)"
        assert M.world.actions_remaining == ap
        assert "Engaging" not in (reply.get("message") or "")


class TestANonNavalRefusalReachesTheArmsThemselves:
    """The Channel case is caught by the pre-gate BEFORE the personality
    arms; these reach the arms with a refusal the gate cannot see (a stubbed
    executor refusing the attack), so each arm's own read is pinned."""

    def _refusing(self, executor):
        real = executor.execute

        def refuse(command, game_state):
            if command.get("command", {}).get("action") == "attack":
                return {"success": False, "message": "his guns are not set up"}
            return real(command, game_state)
        executor.execute = refuse
        return executor

    def test_the_aggressive_first_step_arm(self, channel):
        channel.fleets = None
        executor = self._refusing(CommandExecutor())
        ney = channel.get_marshal("Ney")
        moore = channel.get_marshal("Moore")
        ney.strategic_order = _order("MOVE_TO", "London", path=["London"])
        with _quiet():
            result = executor._strategic._handle_first_step_blocked(
                ney, [moore], "London", channel, {"world": channel})
        assert result["success"] is False and result.get("attack_refused") is True
        assert result.get("order_cleared") is True
        assert result.get("variable_action_cost") == 0
        assert "guns are not set up" in result["message"]
        assert ney.strategic_order is None, "no phantom order"

    def test_the_co_located_pursue_arm(self, channel):
        channel.fleets = None
        executor = self._refusing(CommandExecutor())
        ney = channel.get_marshal("Ney")
        moore = channel.get_marshal("Moore")
        moore.location = "Normandy"  # co-located at order creation
        channel._build_marshal_index()
        channel.calculate_visibility()
        parsed = {"is_strategic": True, "strategic_type": "PURSUE",
                  "target": "Moore", "marshal": "Ney", "action": "move",
                  "original_command": "Ney, pursue Moore"}
        with _quiet():
            result = executor._strategic._execute_strategic_command(
                parsed, {"marshal": "Ney", "action": "move", "target": "Moore"},
                {"world": channel})
        assert result is not None
        assert "Engaging" not in (result.get("message") or ""), result
        assert result.get("attack_refused") is True
        assert ney.strategic_order is None, "no PURSUE left standing on a refusal"


# ═══════════════════════════════════════════════════════════════════════
# FA-20 family — the PURSUE first-step arms and the per-turn completions
# ═══════════════════════════════════════════════════════════════════════

class TestARefusedPursuitNeverCompletes:

    def test_the_first_step_pursue_is_refused_and_no_order_stands(self, shipped):
        client, world = shipped
        ney = world.get_marshal("Ney")
        ney.location = "Normandy"
        world.get_marshal("Moore").location = "London"
        world.calculate_visibility()
        reply = _post(client, "Ney, pursue Moore")
        ney = M.world.get_marshal("Ney")
        msg = reply.get("message") or ""
        assert "Engaging" not in msg and "spotted" not in msg, msg
        assert ney.strategic_order is None
        assert reply.get("order_cleared") is True or reply.get("success") is False

    def test_the_per_turn_pursuit_halts_rather_than_completes(self, channel):
        ney = channel.get_marshal("Ney")
        ney.strategic_order = _order("PURSUE", "Moore", target_type="marshal")
        reports, _ = _tick(channel)
        row = next(r for r in reports if r["marshal"] == "Ney")
        assert row["order_status"] == "breaks", row
        assert row["action"] == "attack_refused"
        assert "fire in it" not in row["message"]
        assert "water's edge" in row["message"]
        assert ney.strategic_order is None
        assert _battles(channel) == 0

    def test_the_helper_completes_a_fought_pursuit(self, channel):
        ney = channel.get_marshal("Ney")
        moore = channel.get_marshal("Moore")
        ney.strategic_order = _order("PURSUE", "Moore", target_type="marshal")
        proc = StrategicOrderProcessor(CommandExecutor())
        row = proc._pursuit_engagement(
            ney, channel, moore,
            {"success": True, "message": "A battle!",
             "events": [{"type": "battle", "victor": "Ney"}]})
        assert row["order_status"] == "completed"
        assert "A battle!" in row["message"]


# ═══════════════════════════════════════════════════════════════════════
# FA-15 (the answer) — the answered contact 'attack'
# ═══════════════════════════════════════════════════════════════════════

class TestTheAnsweredAttackReportsARefusalAsARefusal:

    def test_a_refused_answer_ends_the_order_and_says_why(self, channel):
        davout = channel.get_marshal("Davout")
        davout.strategic_order = _order("MOVE_TO", "London", path=["London"])
        davout.pending_interrupt = {
            "marshal": "Davout", "interrupt_type": "contact", "enemy": "Moore",
            "location": "London", "is_first_step": True,
            "options": ["attack", "go_around", "hold_position", "cancel_order"],
        }
        proc = StrategicOrderProcessor(CommandExecutor())
        attempts_before = davout.strategic_order.combat_attempts
        with _quiet():
            result = proc.handle_response("Davout", "contact", "attack",
                                          channel, {"world": channel})
        assert result["success"] is True
        assert result["action_taken"] == "attack_refused"
        assert result["order_cleared"] is True
        assert result.get("blocked_naval") == "Britain"
        assert "attacks Moore" not in result["message"]
        assert "Assault failed" not in result["message"]
        assert "cannot attack Moore" in result["message"]
        assert davout.strategic_order is None
        assert attempts_before == 0 and _battles(channel) == 0

    def test_a_fought_answer_still_narrates(self, channel):
        channel.fleets = None
        davout = channel.get_marshal("Davout")
        davout.strategic_order = _order("MOVE_TO", "London", path=["London"])
        davout.pending_interrupt = {
            "marshal": "Davout", "interrupt_type": "contact", "enemy": "Moore",
            "location": "London", "is_first_step": True,
            "options": ["attack", "go_around", "hold_position", "cancel_order"],
        }
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            result = proc.handle_response("Davout", "contact", "attack",
                                          channel, {"world": channel})
        assert result["action_taken"] == "attack"
        assert _battles(channel) == 1


# ═══════════════════════════════════════════════════════════════════════
# FA-34 — "Continue as Ordered" continues; the copy speaks
# ═══════════════════════════════════════════════════════════════════════

class TestContinueAsOrderedContinues:

    def _stalemate(self, channel):
        channel.fleets = None
        ney = channel.get_marshal("Ney")
        moore = channel.get_marshal("Moore")
        ney.strategic_order = _order("MOVE_TO", "London", path=["London"])
        proc = StrategicOrderProcessor(CommandExecutor())
        row = proc._handle_combat_result(
            ney, moore,
            {"success": True, "message": "Bloody and indecisive.",
             "events": [{"type": "battle", "outcome": "stalemate"}]},
            channel, {"world": channel})
        assert row["outcome"] == "stalemate" and row["requires_input"]
        return proc, ney, row

    def test_the_stalemate_copy_names_the_march_not_the_enum(self, channel):
        _proc, ney, row = self._stalemate(channel)
        assert "Continue his march?" in row["message"], row["message"]
        assert "move to" not in row["message"].lower()
        assert ney.pending_interrupt["message"] == row["message"], "FA-N60: stored"

    def test_continue_order_keeps_the_order(self, channel):
        proc, ney, _row = self._stalemate(channel)
        trust = ney.trust.value
        with _quiet():
            result = proc.handle_response("Ney", "combat_stalemate",
                                          "continue_order", channel,
                                          {"world": channel})
        assert result["success"] is True
        assert result["order_cleared"] is False
        assert "presses on" in result["message"]
        assert "cancelled" not in result["message"]
        assert ney.strategic_order is not None
        assert ney.trust.value == trust

    def test_cancel_order_still_cancels(self, channel):
        proc, ney, _row = self._stalemate(channel)
        with _quiet():
            result = proc.handle_response("Ney", "combat_stalemate",
                                          "cancel_order", channel,
                                          {"world": channel})
        assert result["order_cleared"] is True
        assert ney.strategic_order is None

    def test_the_loop_guard_still_stops_a_free_re_attack(self, channel):
        """The order stands, but `_should_auto_attack` refuses the same man
        while `combat_attempts > 0` — the guard the cancel was pretending
        to be."""
        proc, ney, _row = self._stalemate(channel)
        with _quiet():
            proc.handle_response("Ney", "combat_stalemate", "continue_order",
                                 channel, {"world": channel})
        moore = channel.get_marshal("Moore")
        assert ney.strategic_order.combat_attempts == 1
        assert proc._should_auto_attack(ney, moore, channel) is False


# ═══════════════════════════════════════════════════════════════════════
# FA-N40 / FA-N26 — the HOLD sally
# ═══════════════════════════════════════════════════════════════════════

class TestARefusedSallyIsNotASally:

    def test_a_barred_shore_is_never_a_sally_target(self, channel):
        ney = channel.get_marshal("Ney")
        ney.strength = 40000
        ney.strategic_order = _order("HOLD", "Normandy")
        proc = StrategicOrderProcessor(CommandExecutor())
        dispatched = []
        real = proc.executor.execute

        def spy(command, game_state):
            if command.get("command", {}).get("action") == "attack":
                dispatched.append(command["command"].get("target"))
            return real(command, game_state)
        proc.executor.execute = spy
        with _quiet():
            reports = proc.process_strategic_orders(channel, {"world": channel})
        row = next(r for r in reports if r["marshal"] == "Ney")
        assert row["action"] == "hold_active", row
        assert "sallies forth" not in row["message"]
        assert "GLORIOUS CHARGE" not in row["message"]
        assert "battle_message" not in row and "outcome" not in row
        # The filter, not the refusal arm: no sortie was even DISPATCHED, so
        # the row is the ordinary "ready to strike" hold, not a refusal.
        assert dispatched == [], dispatched
        assert "ready to strike" in row["message"], row["message"]
        assert _battles(channel) == 0
        assert ney.location == "Normandy"

    def test_the_refusal_arm_holds_and_says_why(self, channel):
        """Direct: the sortie dispatch refused (a stubbed executor), so the
        honest arm — the artillery twin's — is what returns."""
        ney = channel.get_marshal("Ney")
        ney.strength = 40000
        ney.strategic_order = _order("HOLD", "Normandy")
        proc = StrategicOrderProcessor(CommandExecutor())
        real_execute = proc.executor.execute

        def refuse(command, game_state):
            if command.get("command", {}).get("action") == "attack":
                return dict(REFUSAL)
            return real_execute(command, game_state)
        proc.executor.execute = refuse
        # Let the candidate scan see Moore by pretending the water is open
        # for the scan only: clear the naval layer, so the sortie is
        # dispatched and the STUB refuses it.
        channel.fleets = None
        with _quiet():
            row = proc._execute_hold(ney, channel, {"world": channel})
        assert row["action"] == "hold_active", row
        assert "holds Normandy" in row["message"] and "barred" in row["message"]
        assert row.get("blocked_naval") == "Britain"
        assert "battle_details" not in row

    def test_a_real_sally_still_sallies(self, channel):
        channel.fleets = None
        ney = channel.get_marshal("Ney")
        ney.strength = 40000
        ney.strategic_order = _order("HOLD", "Normandy")
        reports, _ = _tick(channel)
        row = next(r for r in reports if r["marshal"] == "Ney")
        assert row["action"] in ("sally", "glorious_charge_sally"), row
        assert _battles(channel) == 1


# ═══════════════════════════════════════════════════════════════════════
# FA-N10 / FA-N42 / FA-N48 — what a battle carries
# ═══════════════════════════════════════════════════════════════════════

class TestABattleReachesTheClientWhole:

    def test_the_carry_has_the_key_the_renderers_read(self):
        carry = _combat_carry({"message": "Casualties: 1,000", "battle_report": {"x": 1},
                               "new_state": object()})
        assert carry["battle_message"] == "Casualties: 1,000"
        assert "new_state" not in carry["battle_details"]
        assert _combat_carry(None) == {"battle_report": None, "battle_details": None}

    def test_the_allowlist_carries_events_and_the_triad(self):
        for key in ("events", "diplomatic_dialogue",
                    "awaiting_diplomatic_response", "war_purpose_popup"):
            assert key in _COMBAT_PASSTHROUGH_FIELDS

    def test_the_first_step_auto_attack_arrives_whole(self, shipped):
        """`Ney, march to Nassau` with a 3,000-man Mack standing in Hesse's
        Nassau: the aggressive arm auto-attacks, wins, and the response
        carries the report, the diorama, the battle event — and the
        war-purpose HARD STOP the neutral-soil capture guard stages."""
        client, world = shipped
        ney = world.get_marshal("Ney")
        mack = world.get_marshal("Mack")
        ney.location = "Rhineland"
        ney.strength = 40000
        mack.location = "Nassau"
        mack.strength = 3000
        world.calculate_visibility()
        reply = _post(client, "Ney, march to Nassau")
        assert reply.get("success") is True, reply.get("message")
        assert "Engaging" in (reply.get("message") or "")
        assert reply.get("battle_report"), "the after-action report"
        assert reply.get("battle_diorama"), "the diorama"
        events = reply.get("events") or []
        assert any(e.get("type") == "battle" for e in events), events
        if M.world.pending_diplomatic_dialogue and \
                M.world.pending_diplomatic_dialogue.get("type") == "war_purpose_selection":
            assert (reply.get("diplomatic_dialogue") or {}).get("type") == "war_purpose_selection"
            assert reply.get("awaiting_diplomatic_response") is True

    def test_the_interrupt_route_carries_the_triad(self, shipped):
        """The maintained route, through `/strategic_response`: a cautious
        contact answered `attack` onto Hesse-held Nassau."""
        client, world = shipped
        davout = world.get_marshal("Davout")
        mack = world.get_marshal("Mack")
        davout.location = "Rhineland"
        davout.strength = 40000
        mack.location = "Nassau"
        mack.strength = 3000
        world.calculate_visibility()
        first = _post(client, "Davout, march to Nassau")
        pending = first.get("pending_interrupt") or {}
        assert pending.get("interrupt_type") == "contact", first.get("message")
        assert pending.get("message"), "FA-N60: the stored ask carries its line"
        with _quiet():
            second = client.post("/strategic_response", json={
                "marshal_name": "Davout", "response_type": "contact",
                "choice": "attack"}).json()
        assert second.get("battle_report")
        if M.world.pending_diplomatic_dialogue and \
                M.world.pending_diplomatic_dialogue.get("type") == "war_purpose_selection":
            assert (second.get("diplomatic_dialogue") or {}).get("type") == "war_purpose_selection"
            # The next order is not swallowed by an unrendered HARD STOP.
            assert second.get("awaiting_diplomatic_response") is True


# ═══════════════════════════════════════════════════════════════════════
# FA-N60 — the stored question carries its own line
# ═══════════════════════════════════════════════════════════════════════

class TestTheStoredQuestionCarriesItsLine:

    def test_the_first_step_bad_odds_ask(self, shipped):
        client, world = shipped
        with _quiet():
            reply = client.post("/command", json={"command": "Ney, march to Munich"}).json()
        pending = reply.get("pending_interrupt") or {}
        assert pending.get("interrupt_type") == "contact_bad_odds", reply.get("message")
        assert "Mack" in pending.get("message", "") and "Swabia" in pending.get("message", "")
        assert M.world.get_marshal("Ney").pending_interrupt["message"] == pending["message"]

    def test_step_0a_repeats_the_stored_line(self, channel):
        ney = channel.get_marshal("Ney")
        ney.strategic_order = _order("MOVE_TO", "Paris", path=["Paris"])
        ney.pending_interrupt = {
            "marshal": "Ney", "interrupt_type": "contact_bad_odds", "enemy": "Moore",
            "location": "London", "options": ["attack_anyway", "cancel_order"],
            "message": "Ney: 'Moore blocks the path. Odds unfavorable.'",
        }
        reports, _ = _tick(channel)
        row = next(r for r in reports if r["marshal"] == "Ney")
        assert row["requires_input"] is True
        assert row["message"] == "Ney: 'Moore blocks the path. Odds unfavorable.'"
        assert row["pending_interrupt"] is ney.pending_interrupt

    def test_the_inferred_gate_stores_its_line(self, channel, monkeypatch):
        import backend.commands.objection_v2 as ov2
        monkeypatch.setattr(ov2, "inferred_attack_favorable", lambda *a, **k: False)
        channel.fleets = None
        ney = channel.get_marshal("Ney")
        moore = channel.get_marshal("Moore")
        ney.strategic_order = _order("PURSUE", "Moore", target_type="marshal",
                                     delegation_inferred=True)
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            row = proc._inferred_attack_gate(ney, moore, {"world": channel})
        assert row is not None and row["requires_input"]
        assert ney.pending_interrupt["message"] == row["message"]
        assert "Moore" in row["message"]


# ═══════════════════════════════════════════════════════════════════════
# FA-68 — every marshal awaiting input is asked
# ═══════════════════════════════════════════════════════════════════════

class TestEveryDeferredMarshalGetsHisTurn:

    def test_two_cannon_fire_questions_in_one_end_turn(self):
        """Two cautious marshals within two of a recorded battle: both are
        asked, and the second marshal's question is STORED on him."""
        a = MarshalFactory.infantry(name="Bernadotte", location="Paris",
                                    personality="cautious")
        b = MarshalFactory.infantry(name="Davout", location="Normandy",
                                    personality="cautious")
        enemy = MarshalFactory.enemy(name="Mack", location="Belgium",
                                     nation="Austria", strength=20000)
        world = WorldFactory.with_marshals([a, b, enemy])
        for m in (a, b):
            m.strategic_order = _order("MOVE_TO", "Bordeaux", path=["Bordeaux"])
        world.battles_this_turn = [{"location": "Belgium", "attacker": "Mack",
                                    "defender": "Nobody", "turn": 1}]
        reports, _ = _tick(world)
        asked = [r for r in reports if r.get("requires_input")]
        assert [r["marshal"] for r in asked] == ["Bernadotte", "Davout"], reports
        assert b.pending_interrupt is not None, "the second question is stored"


# ═══════════════════════════════════════════════════════════════════════
# The census — a twelfth site cannot drift in unpinned
# ═══════════════════════════════════════════════════════════════════════

class TestTheCensus:

    def test_the_attack_sites_are_counted(self):
        """Every `"action": "attack"` literal in the two strategic files:
        SIXTEEN today — the eleven ORDER-DRIVEN seams slice 3 reads the
        refusal predicate at (the contact answer, the four PURSUE arms, the
        HOLD sally, the two `_handle_blocked_path` arms, the first-step
        aggressive arm and the two first-step PURSUE arms) plus five
        ANSWER/REDIRECT seams the player's own word drives (the muster
        re-issue, the cannon-fire investigate and redirect, and two more
        answer arms). A seventeenth must be added here AND pinned above."""
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        total = 0
        for rel in ("backend/commands/strategic.py",
                    "backend/commands/strategic_executor.py"):
            with open(os.path.join(root, rel), encoding="utf-8") as fh:
                total += len(re.findall(r'"action": "attack"', fh.read()))
        assert total == 16, total

    def test_the_lever_free_seams_read_the_predicate(self):
        """Source pin: the refusal predicate is consulted where each family
        of seams narrates (the helper names are the contract)."""
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root, "backend/commands/strategic.py"), encoding="utf-8") as fh:
            src = fh.read()
        assert src.count("attack_was_refused(") >= 4  # combat result, sally, pursuit, answered contact
        with open(os.path.join(root, "backend/commands/strategic_executor.py"), encoding="utf-8") as fh:
            xsrc = fh.read()
        assert xsrc.count("attack_was_refused(") >= 3   # first-step aggressive + two PURSUE arms
        assert xsrc.count("strike_crossing_verdict(") >= 1
        assert strategic_mod.strike_crossing_verdict is not None
