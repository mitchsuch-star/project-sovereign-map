"""CR-7-9 — "The conditions say what they mean" (September 22, 2026).

Three findings from asking the landed CR-7 how several conditions behave:

1. `and` between clauses was stored exactly like `or`, and the echo listed
   the arms with a comma that said nothing about how they combine. Now:
   `and` = every arm must be met (`StrategicCondition.require_all`, latched
   on `StrategicOrder.condition_progress` so an arm that was true and passed
   stays counted, with a progress beat on the tick it lands); `or`, a comma,
   or no word = whichever comes first — and the echo and the Ledger SAY
   which (`… or … — whichever comes first`, `… and … — both`, `(met)`).
   A bare second clause reads without its own `until`; a dangling connector
   never reaches the target; an arrival referent already at his side is noted.
2. A timed hold ran one turn longer than the Ledger said (the Ledger read
   "0 turn(s) remaining" on a live order for a whole turn). ONE rule now,
   `strategic.count_order_turns`, read by the checker, the hold handler's own
   expiry, the skip branch and the Ledger: a HOLD counts the turn it was
   given (its enemy phase is fought with him holding; the issuing turn's tick
   now reads the condition), a SUPPORT counts from the turn after arrival
   (the enemy phase precedes the tick that lands him).
3. A tail stashed behind a question was dropped in silence by another order
   or the turn's end, after a note that said it would wait. The note now says
   for how long, and the drop is SAID (`relay_let_go`), on the reply that
   dropped it; the typed interrupt answer brings the tail back like the popup.
"""

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.ai import condition_grammar as grammar
from backend.commands import relay as relay_mod
from backend.commands.parser import CommandParser
from backend.commands.strategic import StrategicOrderProcessor, count_order_turns
from backend.game_logic.ledger import build_strategic_ledger
from backend.models.marshal import StrategicCondition, StrategicOrder


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def run(shipped, command):
    client, _world = shipped
    return client.post("/command", json={"command": command}).json()


def end_turn(shipped):
    return run(shipped, "end turn")


def ledger_condition(world, name):
    for row in build_strategic_ledger(world).get("orders") or []:
        if isinstance(row, dict) and row.get("marshal") == name:
            return row.get("condition")
    return None


def report_for(reply, name):
    for row in reply.get("strategic_reports") or []:
        if row.get("marshal") == name:
            return row
    return None


def away(world, name, where="Paris"):
    """Open an arrival arm: move a friendly marshal off the holder's ground."""
    world.get_marshal(name).location = where


# ═══════════════════════════════════════════════════════════════════════════
# 1. The connector
# ═══════════════════════════════════════════════════════════════════════════

class TestTheConnectorIsRead:

    def test_and_means_every_arm(self):
        read = grammar.parse_condition(
            "hold lorraine until davout arrives and until the battle is won", "Lorraine")
        assert read.condition == {"until_marshal_arrives": "Davout",
                                  "until_battle_won": True, "require_all": True}

    def test_or_means_whichever_first_and_carries_no_key(self):
        read = grammar.parse_condition(
            "hold lorraine until davout arrives or until the battle is won", "Lorraine")
        assert read.condition == {"until_marshal_arrives": "Davout", "until_battle_won": True}
        assert "require_all" not in read.condition

    def test_no_connector_is_any_of(self):
        read = grammar.parse_condition("hold lorraine for 3 turns until davout arrives", "Lorraine")
        assert read.condition == {"until_marshal_arrives": "Davout", "max_turns": 3}

    def test_a_bare_second_clause_reads_without_its_own_until(self):
        read = grammar.parse_condition(
            "hold lorraine until davout arrives or the battle is won", "Lorraine")
        assert read.condition == {"until_marshal_arrives": "Davout", "until_battle_won": True}
        # The legacy (world-less) read resolves a destroyed referent to the
        # TARGET — unchanged; the connector still reads.
        read = grammar.parse_condition(
            "hold lorraine until davout arrives and mack is destroyed", "Lorraine")
        assert read.condition == {"until_marshal_arrives": "Davout",
                                  "until_marshal_destroyed": "Lorraine", "require_all": True}

    def test_the_connector_before_a_for_clause_counts(self):
        assert grammar.read_connector("hold lorraine until davout arrives and for 2 turns")[0] == "and"
        assert grammar.read_connector("hold lorraine for 2 turns, or until davout arrives")[0] == "or"
        assert grammar.read_connector("hold lorraine for 2 turns until davout arrives") == (None, [])

    def test_mixed_connectors_read_as_any_of_and_say_so(self, shipped):
        _client, world = shipped
        read = grammar.parse_condition(
            "hold rhineland until davout arrives and until relieved or until the battle is won",
            "Rhineland", world=world, issuing_marshal="Ney")
        assert read.condition and "require_all" not in read.condition
        assert any("both used" in n for n in read.notes)

    def test_a_dangling_connector_never_reaches_the_target(self):
        assert grammar.strip_condition_text("hold lorraine for 2 turns and until davout arrives") == "hold lorraine"
        assert grammar.strip_condition_text("hold lorraine until davout arrives or the battle is won") == "hold lorraine"
        assert grammar.strip_condition_text("hold lorraine for 2 turns or") == "hold lorraine"

    def test_the_single_arm_reads_are_byte_identical(self):
        # The one-armed strings every older pin holds must not move.
        assert grammar.describe_condition({"max_turns": 3}) == "for 3 turn(s)"
        assert grammar.describe_condition({"max_turns": 3}, remaining=2) == "2 turn(s) remaining"
        assert grammar.describe_condition({"until_marshal_arrives": "Davout"}) == "until Davout arrives"
        assert grammar.describe_condition({"until_battle_won": True}) == "until the battle is won"


class TestTheSentenceNamesTheConnector:

    def test_any_of_says_whichever_comes_first(self):
        text = grammar.describe_condition({"max_turns": 3, "until_marshal_arrives": "Davout"}, remaining=2)
        assert text == "2 turn(s) remaining or until Davout arrives — whichever comes first"
        assert " and " not in text and "," not in text

    def test_all_of_says_both_and_ticks_off_a_met_arm(self):
        cond = {"until_marshal_arrives": "Davout", "until_battle_won": True, "require_all": True}
        assert grammar.describe_condition(cond) == "until Davout arrives and until the battle is won — both"
        assert grammar.describe_condition(cond, progress=["until_marshal_arrives"]) == \
            "until Davout arrives (met) and until the battle is won — both"
        assert grammar.describe_condition(cond, progress=["until_marshal_arrives"], only_unmet=True) == \
            "until the battle is won"

    def test_three_arms_say_all_three(self):
        cond = {"max_turns": 2, "until_marshal_arrives": "Davout", "until_battle_won": True,
                "require_all": True}
        assert grammar.describe_condition(cond).endswith("— all 3")
        # a met timer arm reads as passed, never as "0 remaining"
        assert "2 turn(s) passed (met)" in grammar.describe_condition(
            cond, remaining=0, progress=["max_turns"])


class TestTheEchoAndTheLedgerAgree:

    def test_or_on_the_wire(self, shipped):
        _client, world = shipped
        away(world, "Davout")
        ney = world.get_marshal("Ney")
        reply = run(shipped, f"Ney, hold {ney.location} until Davout arrives or the battle is won")
        assert reply["success"], reply.get("message")
        cond = ney.strategic_order.condition
        assert cond.until_marshal_arrives == "Davout" and cond.until_battle_won and not cond.require_all
        assert "— whichever comes first" in reply["message"]
        assert ledger_condition(world, "Ney") == \
            "until Davout arrives or until the battle is won — whichever comes first"
        assert ledger_condition(world, "Ney") == grammar.describe_condition(cond)

    def test_and_on_the_wire_keeps_the_target(self, shipped):
        _client, world = shipped
        away(world, "Davout")
        ney = world.get_marshal("Ney")
        here = ney.location
        reply = run(shipped, f"Ney, hold {here} for 2 turns and until Davout arrives")
        assert reply["success"], reply.get("message")
        order = ney.strategic_order
        assert order.target == here, order.target                      # no "… and"
        assert order.condition.require_all and order.condition.max_turns == 2
        assert "for 2 turn(s) and until Davout arrives — both" in reply["message"]
        assert ledger_condition(world, "Ney") == "2 turn(s) remaining and until Davout arrives — both"

    def test_an_arrival_referent_already_at_his_side_is_noted(self, shipped):
        _client, world = shipped
        ney = world.get_marshal("Ney")
        world.get_marshal("Davout").location = ney.location
        reply = run(shipped, f"Ney, hold {ney.location} until Davout arrives")
        assert reply["success"]
        assert "Davout is already at" in reply["message"]


# ═══════════════════════════════════════════════════════════════════════════
# 2. The model
# ═══════════════════════════════════════════════════════════════════════════

class TestTheModelSerializes:

    def test_require_all_round_trips_and_defaults_false(self):
        cond = StrategicCondition(until_marshal_arrives="Davout", until_battle_won=True, require_all=True)
        again = StrategicCondition.from_dict(cond.to_dict())
        assert again.require_all is True
        legacy = StrategicCondition.from_dict({"until_marshal_arrives": "Davout"})
        assert legacy.require_all is False

    def test_condition_progress_round_trips_and_defaults_empty(self):
        order = StrategicOrder(command_type="HOLD", target="Lorraine", target_type="region",
                               started_turn=1, original_command="hold Lorraine",
                               condition=StrategicCondition(until_marshal_arrives="Davout",
                                                            until_battle_won=True, require_all=True),
                               condition_progress=["until_marshal_arrives"])
        again = StrategicOrder.from_dict(order.to_dict())
        assert again.condition_progress == ["until_marshal_arrives"]
        assert again.condition.require_all is True
        d = order.to_dict()
        d.pop("condition_progress")
        assert StrategicOrder.from_dict(d).condition_progress == []


# ═══════════════════════════════════════════════════════════════════════════
# 3. The timer counts the turn it was given
# ═══════════════════════════════════════════════════════════════════════════

class TestTheTimerCountsTheTurnItWasGiven:

    def test_hold_for_one_turn_ends_with_the_turn_it_was_given(self, shipped):
        _client, world = shipped
        ney = world.get_marshal("Ney")
        run(shipped, f"Ney, hold {ney.location} for 1 turn")
        assert ledger_condition(world, "Ney") == "1 turn(s) remaining"
        reply = end_turn(shipped)
        row = report_for(reply, "Ney")
        assert row and row["order_status"] == "completed", row
        assert ney.strategic_order is None

    def test_hold_for_two_turns_reads_one_remaining_then_completes(self, shipped):
        _client, world = shipped
        dav = world.get_marshal("Davout")
        run(shipped, f"Davout, hold {dav.location} for 2 turns")
        reply = end_turn(shipped)
        row = report_for(reply, "Davout")
        assert row["order_status"] == "active" and row["turns_remaining"] == 1, row
        assert "(1 turn(s) remaining)" in row["message"]
        assert ledger_condition(world, "Davout") == "1 turn(s) remaining"
        reply = end_turn(shipped)
        assert report_for(reply, "Davout")["order_status"] == "completed"

    @pytest.mark.parametrize("turns", [1, 2, 3])
    def test_the_ledger_never_reads_zero_on_a_live_order(self, shipped, turns):
        # Soult: the literal never takes a cannon-fire interrupt, so the hold
        # runs its term unhalted (Davout was halted by one on turn 2).
        _client, world = shipped
        soult = world.get_marshal("Soult")
        run(shipped, f"Soult, hold {soult.location} for {turns} turns")
        assert soult.strategic_order is not None
        for _ in range(turns + 1):
            if soult.strategic_order is None:
                break
            assert ledger_condition(world, "Soult") == f"{turns - _} turn(s) remaining"
            end_turn(shipped)
        assert soult.strategic_order is None

    def test_until_turn_n_means_the_hold_is_over_when_turn_n_begins(self, shipped):
        _client, world = shipped
        dav = world.get_marshal("Davout")
        assert int(world.current_turn) == 1
        run(shipped, f"Davout, hold {dav.location} until turn 3")
        assert dav.strategic_order.condition.max_turns == 2
        end_turn(shipped)                                   # turn 1 closes
        assert dav.strategic_order is not None
        end_turn(shipped)                                   # turn 2 closes
        assert dav.strategic_order is None and int(world.current_turn) == 3

    def test_the_one_rule_hold_and_support(self):
        hold = StrategicOrder(command_type="HOLD", target="Lorraine", target_type="region",
                              started_turn=4, original_command="hold Lorraine for 2 turns",
                              condition=StrategicCondition(max_turns=2))
        assert count_order_turns(hold, 4) == 1                      # the issuing turn's tick
        assert count_order_turns(hold, 4, including_current=False) == 0   # the Ledger that turn
        assert count_order_turns(hold, 5) == 2                      # completes at the next tick
        support = StrategicOrder(command_type="SUPPORT", target="Davout", target_type="marshal",
                                 started_turn=1, original_command="support Davout for 3 turns",
                                 path=[], condition=StrategicCondition(max_turns=3))
        assert count_order_turns(support, 2) == 0                   # not arrived: no clock
        support.arrived_turn = 2
        assert count_order_turns(support, 2) == 0                   # the arrival turn gave no support
        assert count_order_turns(support, 4) == 2
        assert count_order_turns(support, 5) == 3                   # three enemy phases at his side
        assert count_order_turns(support, 3, including_current=False) == 0   # Ledger on turn 3: 3 left

    def test_the_hold_handlers_own_expiry_agrees(self, shipped):
        """`_execute_hold` keeps a timer of its own (the compromise arm); it
        counts the same way and never fires an all-of alone."""
        _client, world = shipped
        ney = world.get_marshal("Ney")
        ney.strategic_order = StrategicOrder(
            command_type="HOLD", target=ney.location, target_type="region", started_turn=1,
            issued_turn=1, original_command="hold", condition=StrategicCondition(max_turns=1))
        ney.holding_position = True
        ney.hold_region = ney.location
        proc = StrategicOrderProcessor(M.executor)
        assert proc._execute_hold(ney, world, M.game_state)["order_status"] == "expired"
        away(world, "Davout")
        ney.strategic_order = StrategicOrder(
            command_type="HOLD", target=ney.location, target_type="region", started_turn=1,
            issued_turn=1, original_command="hold",
            condition=StrategicCondition(max_turns=1, until_marshal_arrives="Davout", require_all=True))
        ney.holding_position = True
        result = proc._execute_hold(ney, world, M.game_state)
        assert result.get("order_status") != "expired" and ney.strategic_order is not None


# ═══════════════════════════════════════════════════════════════════════════
# 4. The all-of latch
# ═══════════════════════════════════════════════════════════════════════════

class TestTheAllOfLatch:

    def test_an_arm_that_lands_is_a_progress_beat_and_stays_counted(self, shipped):
        _client, world = shipped
        away(world, "Davout")
        ney = world.get_marshal("Ney")
        run(shipped, f"Ney, hold {ney.location} until Davout arrives and until the battle is won")
        world.get_marshal("Davout").location = ney.location          # he arrives
        reply = end_turn(shipped)
        row = report_for(reply, "Ney")
        assert row["order_status"] == "active"
        assert "Davout has arrived. Ney holds on — until the battle is won as well." in row["message"]
        assert ney.strategic_order.condition_progress == ["until_marshal_arrives"]
        assert ledger_condition(world, "Ney") == \
            "until Davout arrives (met) and until the battle is won — both"
        away(world, "Davout")                                        # and marches on
        ney.last_combat_result = "victory"
        ney.last_combat_turn = int(world.current_turn)
        reply = end_turn(shipped)
        row = report_for(reply, "Ney")
        assert row["order_status"] == "completed", row
        assert "Victory achieved! With that, every condition of Ney's order is met." in row["message"]
        assert ney.strategic_order is None

    def test_any_of_still_ends_on_the_first_arm(self, shipped):
        _client, world = shipped
        away(world, "Davout")
        ney = world.get_marshal("Ney")
        run(shipped, f"Ney, hold {ney.location} until Davout arrives or the battle is won")
        world.get_marshal("Davout").location = ney.location
        reply = end_turn(shipped)
        assert report_for(reply, "Ney")["order_status"] == "completed"
        assert ney.strategic_order is None

    def test_a_timer_that_lands_early_in_an_all_of_does_not_abandon(self, shipped):
        _client, world = shipped
        away(world, "Davout")
        ney = world.get_marshal("Ney")
        run(shipped, f"Ney, hold {ney.location} for 1 turn and until Davout arrives")
        reply = end_turn(shipped)
        row = report_for(reply, "Ney")
        assert row["order_status"] == "active", row
        assert "The agreed 1 turn(s) have passed. Ney holds on — until Davout arrives as well." in row["message"]
        assert "abandons" not in row["message"]
        assert ney.strategic_order is not None
        assert ney.strategic_order.condition_progress == ["max_turns"]

    def test_a_progress_beat_on_a_later_tick_rides_the_handler_report(self, shipped):
        """The issuing turn reports through the skip branch; a later turn
        through the handler — both carry the beat."""
        # Soult (literal) never takes a cannon-fire redirect, which pulled Ney off
        # his hold on the second turn of the first cut of this pin.
        _client, world = shipped
        away(world, "Davout")
        soult = world.get_marshal("Soult")
        run(shipped, f"Soult, hold {soult.location} until Davout arrives and until the battle is won")
        assert soult.strategic_order is not None
        reply = end_turn(shipped)                                   # nothing lands
        assert "holds on" not in (report_for(reply, "Soult") or {}).get("message", "")
        world.get_marshal("Davout").location = soult.location
        reply = end_turn(shipped)
        row = report_for(reply, "Soult")
        # the handler reports a standing hold as "continues"; the skip branch "active"
        assert row and row["order_status"] in ("active", "continues"), row
        assert "Davout has arrived. Soult holds on — until the battle is won as well." in row["message"]

    def test_the_checker_latches_only_all_of(self, shipped):
        _client, world = shipped
        away(world, "Davout")
        ney = world.get_marshal("Ney")
        run(shipped, f"Ney, hold {ney.location} for 3 turns until Davout arrives")
        proc = StrategicOrderProcessor(M.executor)
        met, _ = proc._check_condition(ney, ney.strategic_order.condition, world)
        assert met is False and ney.strategic_order.condition_progress == []


# ═══════════════════════════════════════════════════════════════════════════
# 5. The tail is let go with a word
# ═══════════════════════════════════════════════════════════════════════════

class TestTheTailIsLetGoWithAWord:

    def _stash(self, shipped):
        reply = run(shipped, "march to Lorraine, then fortify")     # "Which marshal, Sire?"
        assert reply.get("relay_kind") == "question", reply.get("message")
        assert "another order, or the turn's end, lets it go" in reply["relay_note"]
        assert M.world._pending_relay and M.world._pending_relay["tail"] == "fortify"
        return reply

    def test_another_order_lets_it_go_and_says_so(self, shipped):
        self._stash(shipped)
        reply = run(shipped, "Davout, scout Swabia")
        assert reply.get("relay_let_go") == "fortify"
        assert 'is let go with it' in reply["message"] and '"fortify"' in reply["message"]
        assert M.world._pending_relay is None and M.world._relay_let_go is None

    def test_the_turns_end_lets_it_go_and_says_so(self, shipped):
        self._stash(shipped)
        reply = end_turn(shipped)
        assert reply.get("relay_let_go") == "fortify"
        assert 'is let go with it' in reply["message"]

    def test_re_typing_the_tail_is_not_a_drop(self, shipped):
        self._stash(shipped)
        reply = run(shipped, "Ney, march to Lorraine, then fortify")
        assert reply.get("relay_let_go") is None
        assert reply.get("dropped_sequel") == "fortify"
        assert "is let go" not in reply["message"]

    def test_the_boundary_speaks_on_the_next_reply(self, shipped):
        _client, world = shipped
        world._pending_relay = {"tail": "attack Mack", "marshal": "Ney",
                                "head_action": "fortify", "turn": int(world.current_turn)}
        world.advance_turn()
        assert world._pending_relay is None and world._relay_let_go["tail"] == "attack Mack"
        reply = run(shipped, "status")
        assert reply.get("relay_let_go") == "attack Mack" and 'is let go with it' in reply["message"]
        assert world._relay_let_go is None

    def test_an_answered_relay_is_never_let_go(self, shipped):
        _client, world = shipped
        pending = {"tail": "fortify", "marshal": "Ney", "head_action": "move", "turn": 1}
        world._relay_let_go = pending
        response = {"message": "done"}
        M._attach_answered_relay(response, {"success": True}, pending)
        assert world._relay_let_go is None
        assert response.get("dropped_sequel") == "fortify" and response.get("relay_kind")

    def test_the_let_go_line_names_the_tail(self):
        line = relay_mod.let_go_line({"tail": "attack Mack"})
        assert line.startswith('Berthier: "') and '"attack Mack"' in line
        assert "Give it again when you mean it" in line


# ═══════════════════════════════════════════════════════════════════════════
# 6. The help teaches it
# ═══════════════════════════════════════════════════════════════════════════

class TestTheHelpTeachesTheConnector:

    def test_the_help_names_or_and_and(self, shipped):
        reply = run(shipped, "help")
        text = reply.get("message") or ""
        assert "or / and" in text and "whichever comes first" in text and "BOTH must land" in text
        assert "'for 2 turns' counts the turn you give it" in text
