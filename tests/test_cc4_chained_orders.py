"""CC-4 "Chained orders" — row CC's last slice (Pre-Deploy S13c part 4).

Plan: `~/.claude/plans/sorted-yawning-clover.md` §CC-4 (decisions D6–D8) and
the session's plan `parallel-knitting-hearth.md`; rows `docs/BUG_FIXES.md`
§CC (CC-X6, CC-X7, CC-X9, CC-X17, CF-5, and the siblings from CC-X18).

Every pin drives the real seam — `CommandParser.parse` on the shipped 1805
boot, or `POST /command` — with the objection's mood roll pinned flat (the
MOOD-1 lesson: a pin that rides the roll flakes with its xdist worker's
history).
"""

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.ai import strategic_parser as sp
from backend.commands import executor as executor_mod
from backend.commands import objection_v2 as ov2
from backend.commands import parser as parser_mod
from backend.commands import strategic_executor as se_mod
from backend.commands.parser import CommandParser


@pytest.fixture(autouse=True)
def _no_mood_variance(monkeypatch):
    """The objection's mood roll pinned flat (CC-2's three names)."""
    def flat(concern):
        return concern
    monkeypatch.setattr(executor_mod, "apply_mood_variance", flat)
    monkeypatch.setattr(se_mod, "apply_mood_variance", flat)
    monkeypatch.setattr(ov2, "apply_mood_variance", flat)


@pytest.fixture
def shipped(monkeypatch):
    """A fresh SHIPPED 1805 world at all three seams, with a mock parser
    (the CR-7-1 fixture): Ney and Davout at Rhineland, Mack at Swabia."""
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False, "a probe must never pay for a parse"
    return TestClient(M.app), M.world


def parse(text):
    """The production call shape: `parser.parse(text, llm_game_state, world=)`."""
    return M.parser.parse(text, M.get_llm_game_state(), world=M.world)


def run(shipped, command):
    client, _world = shipped
    return client.post("/command", json={"command": command}).json()


# ═══════════════════════════════════════════════════════════════════════════
# CC-X6 — `hold … until X arrives then attack` no longer drops the attack
# ═══════════════════════════════════════════════════════════════════════════

UNTIL_THEN_ATTACK = [
    "Ney, hold until Davout arrives then attack Mack",
    "Ney, hold until Davout arrives, then attack Mack",
    "Ney, hold until Davout arrives and attack Mack",
    "Ney, hold Rhineland until Davout arrives; attack Mack",
]


class TestCCX6TheUntilTailIsNamed:

    @pytest.mark.parametrize("line", UNTIL_THEN_ATTACK)
    def test_the_hold_goes_out_and_the_attack_is_named(self, shipped, line):
        """Reproduced before the fix: the hold went out, the attack was
        stamped on a HOLD that never reads it, and nothing said so."""
        reply = run(shipped, line)
        assert reply.get("success") is True, reply.get("message")
        assert "will hold" in (reply.get("message") or "")
        assert reply.get("dropped_sequel") == "attack Mack", reply
        assert reply.get("relay_kind") == "contradiction"
        assert "end his standing hold" in (reply.get("relay_note") or "")
        order = M.world.get_marshal("Ney").strategic_order
        assert order.command_type == "HOLD"
        assert order.condition.until_marshal_arrives == "Davout"
        assert not order.attack_on_arrival and order.arrival_target is None

    def test_the_support_sibling_is_split_too(self, shipped):
        """The same fuse on SUPPORT: `until relieved then attack Mack` kept
        `attack_on_arrival` and its object on an order that never reads them."""
        result = parse("Ney, support Davout until relieved then attack Mack")
        assert result.get("strategic_type") == "SUPPORT"
        assert result.get("dropped_sequel") == "attack Mack"
        assert not result.get("attack_on_arrival")

    @pytest.mark.parametrize("text,carries", [
        ("Ney, march to Swabia then attack Mack", True),
        ("Ney, pursue Mack then attack", True),
        ("Ney, hold Rhineland then attack Mack", False),
        ("Ney, support Davout then attack Mack", False),
    ])
    def test_the_flag_is_stamped_only_where_it_is_read(self, shipped, text, carries):
        """`strategic_parser` stamps `attack_on_arrival` only on the order
        types whose executor reads it (`ARRIVAL_CARRYING_TYPES`)."""
        result = sp.detect_strategic_command(text, "Ney", M.world)
        assert bool(result.get("attack_on_arrival")) is carries, result

    def test_the_march_still_carries_its_attack(self, shipped):
        """The engine's one two-step order is untouched: one parse, armed."""
        result = parse("Ney, march to Swabia then attack Mack")
        assert result.get("strategic_type") == "MOVE_TO"
        assert result.get("dropped_sequel") is None
        assert result.get("attack_on_arrival") is True
        assert result.get("arrival_target") == "Mack"

    def test_sensitivity_the_old_fuse_drops_the_tail(self, shipped, monkeypatch):
        """The pin can fail: with the old `until` arm put back the tail is
        fused and never reported."""
        old = parser_mod._head_can_carry_arrival

        def with_until_arm(first):
            return old(first) or (" until " in f" {first.lower()} "
                                  and sp.clause_is_a_standing_order(first))
        monkeypatch.setattr(parser_mod, "_head_can_carry_arrival", with_until_arm)
        result = parse("Ney, hold until Davout arrives then attack Mack")
        assert result.get("dropped_sequel") is None


# ═══════════════════════════════════════════════════════════════════════════
# CC-X7 — Compromise keeps the typed condition, whichever comes first
# CC-X18 — and the FOLLOW keeps its standing
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def objecting(monkeypatch):
    """Every strategic order draws a MODERATE concern, so the marshal objects
    and the Compromise arm is reachable (the evaluator pinned, never rolled)."""
    from backend.commands.objection_v2 import ConcernLevel
    monkeypatch.setattr(se_mod, "evaluate_strategic_situation",
                        lambda *a, **k: ConcernLevel.MODERATE)


def compromise(shipped, line):
    """Send `line`, answer its objection with Compromise; (first, answer)."""
    client, _world = shipped
    first = client.post("/command", json={"command": line}).json()
    assert first.get("pending_objection"), first.get("message")
    kinds = {o.get("type") for o in (first.get("objection") or {}).get("options", [])}
    assert "compromise" in kinds, kinds
    answer = client.post("/respond_to_objection", json={"choice": "compromise"}).json()
    return first, answer


class TestCCX7CompromiseKeepsTheCondition:

    def test_an_any_of_condition_takes_the_term_as_one_more_arm(self, shipped, objecting):
        """Reproduced on HEAD `676e3651`: the order came back `{max_turns: 3}`
        and "until Davout arrives" was gone; Insist kept it."""
        _first, answer = compromise(shipped, "Ney, hold Rhineland until Davout arrives")
        cond = M.world.get_marshal("Ney").strategic_order.condition
        assert (cond.max_turns, cond.until_marshal_arrives, cond.require_all) == (3, "Davout", False)
        assert cond.cap_turns is None
        assert "Your condition stands — until Davout arrives, whichever comes first." in (
            answer.get("message") or ""), answer.get("message")

    def test_an_all_of_condition_is_capped_not_joined(self, shipped, objecting):
        """An all-of `max_turns` would be one more arm to wait for — the agreed
        timer caps the order on its own (`cap_turns`)."""
        _first, answer = compromise(
            shipped, "Ney, hold Rhineland until Davout arrives and until the battle is won")
        cond = M.world.get_marshal("Ney").strategic_order.condition
        assert cond.require_all is True
        assert (cond.until_marshal_arrives, cond.until_battle_won) == ("Davout", True)
        assert (cond.max_turns, cond.cap_turns) == (None, 3)
        assert "both, whichever comes first" in (answer.get("message") or "")

    def test_the_cap_ends_the_all_of_order_on_its_own(self, shipped):
        """Neither arm has landed (Murat is two provinces off, no battle); on
        the agreed turn's tick the order still ends — the issuing turn counts,
        as for every timer (CR-7-9's `count_order_turns`)."""
        from backend.commands.strategic import StrategicOrderProcessor
        from backend.models.marshal import StrategicCondition, StrategicOrder
        _client, world = shipped
        ney = world.get_marshal("Ney")
        ney.strategic_order = StrategicOrder(
            command_type="HOLD", target=ney.location, target_type="region",
            started_turn=world.current_turn, original_command="pin",
            condition=StrategicCondition(until_marshal_arrives="Murat",
                                         until_battle_won=True, require_all=True,
                                         cap_turns=3))
        proc = StrategicOrderProcessor(M.executor)
        start = world.current_turn
        world.current_turn = start + 1
        assert proc._check_condition(ney, ney.strategic_order.condition, world)[0] is False
        world.current_turn = start + 2
        met, line = proc._check_condition(ney, ney.strategic_order.condition, world)
        assert met is True and "the agreed 3 turns" in line

    def test_a_longer_typed_timer_is_not_echoed_as_binding(self, shipped, objecting):
        _first, answer = compromise(shipped, "Ney, hold Rhineland for 5 turns")
        assert M.world.get_marshal("Ney").strategic_order.condition.max_turns == 3
        assert "Your condition stands" not in (answer.get("message") or "")

    def test_with_no_typed_condition_the_bargain_is_unchanged(self, shipped, objecting):
        _first, answer = compromise(shipped, "Ney, hold Rhineland")
        cond = M.world.get_marshal("Ney").strategic_order.condition
        assert cond.to_dict() == {"max_turns": 3, "until_marshal_arrives": None,
                                  "until_marshal_destroyed": None, "until_battle_won": False,
                                  "until_relieved": False, "auto_cancel_below_ratio": None,
                                  "require_all": False, "cap_turns": None}
        assert (answer.get("message") or "").startswith("Ney agrees to hold position for 3 turns.")

    def test_sensitivity_without_the_typed_condition_it_is_lost(self, shipped, objecting,
                                                                monkeypatch):
        monkeypatch.setattr(se_mod, "typed_condition", lambda parsed: None)
        compromise(shipped, "Ney, hold Rhineland until Davout arrives")
        cond = M.world.get_marshal("Ney").strategic_order.condition
        assert cond.until_marshal_arrives is None

    def test_cc_x18_a_follow_keeps_its_standing(self, shipped, objecting):
        """CC-X18 (CC-X7's sweep): the 12-kwarg rebuild also dropped AO's
        `standing_follow` — a FOLLOW answered with Compromise came back a
        plain SUPPORT that lapses the turn its friend is secure."""
        _first, answer = compromise(shipped, "Davout, follow Ney")
        order = M.world.get_marshal("Davout").strategic_order
        assert order.command_type == "SUPPORT" and order.standing_follow is True
        assert order.condition.max_turns == 3
        assert "agrees to follow Ney for 3 turns" in (answer.get("message") or "")

    def test_the_cap_round_trips_and_is_said(self):
        from backend.ai.condition_grammar import describe_condition
        from backend.models.marshal import StrategicCondition
        cond = StrategicCondition(until_marshal_arrives="Davout", until_battle_won=True,
                                  require_all=True, cap_turns=3)
        assert StrategicCondition.from_dict(cond.to_dict()) == cond
        assert StrategicCondition.from_dict({"max_turns": 2}).cap_turns is None
        assert describe_condition(cond) == (
            "until Davout arrives and until the battle is won — both; "
            "or 3 turns at most — whichever comes first")


# ═══════════════════════════════════════════════════════════════════════════
# CC-X9 — no pursuit outlives its quarry
# ═══════════════════════════════════════════════════════════════════════════

def _pursue_mack_then_lose_him(shipped, *, taken=False):
    """Napoleon is told to pursue Mack (issued THIS turn), then Mack leaves the
    board by another seam — destroyed, or taken prisoner (strength 0,
    `captured_by` set, still in `world.marshals`)."""
    reply = run(shipped, "Napoleon, pursue Mack")
    order = M.world.get_marshal("Napoleon").strategic_order
    assert order is not None and order.command_type == "PURSUE", reply.get("message")
    mack = M.world.get_marshal("Mack")
    if taken:
        mack.strength = 0
        mack.captured_by = "France"
    else:
        M.world.destroy_marshal(mack, cause="battle", victor="France")
    return order


def _orders_row(name):
    from backend.game_logic.ledger import build_strategic_ledger
    rows = build_strategic_ledger(M.world).get("orders") or []
    return next(r for r in rows if r.get("marshal") == name)


class TestCCX9NoPursuitOutlivesItsQuarry:

    def test_the_tick_ends_it_on_its_issuing_turn(self, shipped):
        """Reproduced before the fix (the user's live campaign, turn 6): the
        issuing-turn skip passed over `_execute_pursue`'s quarry check, so the
        order outlived the tick and the Orders tab said "tracking" a turn
        after the quarry fell."""
        from backend.commands.strategic import StrategicOrderProcessor
        _pursue_mack_then_lose_him(shipped)
        reports = StrategicOrderProcessor(M.executor).process_strategic_orders(
            M.world, M.game_state)
        nap = M.world.get_marshal("Napoleon")
        assert nap.strategic_order is None
        row = next(r for r in reports if r.get("marshal") == "Napoleon")
        assert row.get("order_status") == "completed"
        assert "Mack destroyed" in (row.get("reason") or "")

    def test_a_paused_pursuer_is_released_too(self, shipped):
        """The recovery pause also passed over the check."""
        from backend.commands.strategic import StrategicOrderProcessor
        order = _pursue_mack_then_lose_him(shipped)
        order.issued_turn = M.world.current_turn - 1
        M.world.get_marshal("Napoleon").retreat_recovery = 2
        StrategicOrderProcessor(M.executor).process_strategic_orders(M.world, M.game_state)
        assert M.world.get_marshal("Napoleon").strategic_order is None

    def test_the_orders_tab_never_says_tracking_a_fallen_man(self, shipped):
        _pursue_mack_then_lose_him(shipped)
        row = _orders_row("Napoleon")
        assert row["condition"] == "Mack destroyed — the pursuit ends at the turn's end"
        from backend.game_logic.ledger import build_strategic_ledger
        forces = build_strategic_ledger(M.world)["forces"]
        summary = next(f for f in forces if f["name"] == "Napoleon")["strategic_order"]
        assert "tracking" not in summary and "destroyed" in summary

    def test_a_prisoner_is_named_a_prisoner(self, shipped):
        _pursue_mack_then_lose_him(shipped, taken=True)
        assert _orders_row("Napoleon")["condition"].startswith("Mack taken prisoner")

    def test_no_arrow_runs_to_a_fallen_man(self, shipped):
        from backend.commands.strategic import standing_order_road
        _pursue_mack_then_lose_him(shipped)
        assert standing_order_road(M.world, M.world.get_marshal("Napoleon")) == {}

    def test_a_live_quarry_is_still_tracked(self, shipped):
        """The control arm (`test_ledger.py`'s "(tracking)" pin, on the 1805 board)."""
        run(shipped, "Napoleon, pursue Mack")
        assert _orders_row("Napoleon")["condition"] == "tracking"


class TestCCX17EveryNameIsRelayedInTurn:
    """CC-X17: a typed named list relays EVERY further name for the seal, in
    turn — never spent by the game (CQ-8). Reproduced before the fix: the
    relay carried one tail ("Davout, fortify") and the third man was only
    named ("Soult needs his own order")."""

    def test_the_line_carries_the_rest_and_each_enter_hands_one_on(self, shipped):
        M.world.actions_remaining = 12   # enough for three fortifies from neutral
        first = run(shipped, "Napoleon, Davout and Soult, fortify")
        assert M.world.get_marshal("Napoleon").fortified is True
        assert first.get("relay_command") == "Davout and Soult, fortify"
        assert M.world.get_marshal("Davout").fortified is False   # never spent
        second = run(shipped, first["relay_command"])
        assert M.world.get_marshal("Davout").fortified is True
        assert M.world.get_marshal("Soult").fortified is False
        assert second.get("relay_command") == "Soult, fortify"
        run(shipped, second["relay_command"])
        assert M.world.get_marshal("Soult").fortified is True

    def test_a_mustered_name_stays_a_clause_off_the_line(self, shipped):
        """The CRT-11 shape is untouched: Lannes marches already."""
        reply = run(shipped, "Ney, Soult and Lannes, attack Mack")
        assert reply.get("relay_command") == "Soult, support Ney"
        assert "Lannes marches already" in (reply.get("relay_note") or "")

    def test_when_the_second_marches_already_the_next_name_takes_his_place(self, shipped):
        """Lannes second (the muster counts him), Soult third: Soult's order
        is relayed — it used to be only named, with nothing on the line."""
        reply = run(shipped, "Ney, Lannes and Soult, attack Mack")
        assert reply.get("relay_command") == "Soult, support Ney"
        assert "Lannes marches with Ney already" in (reply.get("message") or "")
        assert "You named Soult too" in (reply.get("relay_note") or "")

    def test_the_chain_reads_back_through_the_one_splitter(self, shipped):
        """The relayed line is an ordinary named list — `_split_second_name`
        gives its first man the order and hands the rest back."""
        from backend.commands.parser import _split_second_name
        split = _split_second_name("Davout, Soult and Lannes, fortify", M.game_state)
        assert (split["first"], split["second"], split["others"]) == (
            "Davout", "Soult", ["Lannes"])


class TestCCX19NoSupportOutlivesItsFriend:
    """CC-X19 (CC-X9's sweep): the SUPPORT's sibling — `_execute_support`
    breaks on a fallen friend ("X has fallen"), but only when its tick runs;
    the issuing-turn skip and the pauses passed over it, and the Orders tab
    said "active" beside a fallen man."""

    def _support_davout_then_lose_him(self, shipped):
        reply = run(shipped, "Soult, support Davout")
        order = M.world.get_marshal("Soult").strategic_order
        assert order is not None and order.command_type == "SUPPORT", reply.get("message")
        M.world.destroy_marshal(M.world.get_marshal("Davout"), cause="battle", victor="Austria")
        return order

    def test_the_tick_breaks_it_on_its_issuing_turn(self, shipped):
        from backend.commands.strategic import StrategicOrderProcessor
        self._support_davout_then_lose_him(shipped)
        reports = StrategicOrderProcessor(M.executor).process_strategic_orders(
            M.world, M.game_state)
        assert M.world.get_marshal("Soult").strategic_order is None
        row = next(r for r in reports if r.get("marshal") == "Soult")
        assert "Davout has fallen" in (row.get("message") or row.get("reason") or "")

    def test_the_orders_tab_says_he_has_fallen(self, shipped):
        self._support_davout_then_lose_him(shipped)
        assert _orders_row("Soult")["condition"] == (
            "Davout has fallen — the support ends at the turn's end")
        from backend.commands.strategic import standing_order_road
        assert standing_order_road(M.world, M.world.get_marshal("Soult")) == {}


# ═══════════════════════════════════════════════════════════════════════════
# THE BUILDS (commit 2) — D7 the arrival verb (CF-5), D6 the contradiction
# asked first, D8 the standing contingency, and their sweep rows CC-X20…X22
# ═══════════════════════════════════════════════════════════════════════════

def _tick():
    """One pass of the standing orders, as the end turn runs it after the
    enemy phase — driven directly, so no AI move or die rides the pin."""
    from backend.commands.strategic import StrategicOrderProcessor
    return StrategicOrderProcessor(M.executor).process_strategic_orders(M.world, M.game_state)


def _as_if_given_yesterday(name):
    order = M.world.get_marshal(name).strategic_order
    order.issued_turn = int(M.world.current_turn) - 1
    return order


def _row(reports, name):
    return [r for r in reports if r.get("marshal") == name]


def _forces_row(name):
    from backend.game_logic.ledger import build_strategic_ledger
    rows = build_strategic_ledger(M.world).get("forces") or []
    return next(r for r in rows if r.get("name") == name or r.get("marshal") == name)


class TestD7TheArrivalVerb:
    """CF-5: `march to X then fortify` was told "give it when he arrives",
    and on arrival he said "I await further instruction". The march now
    carries ONE verb — fortify / hold / drill / defend — done on arrival,
    free (the march is paid once; its objection asked at issue)."""

    @pytest.mark.parametrize("line,verb", [
        ("Ney, march to Orleanais then fortify", "fortify"),
        ("Ney, march to Orleanais, then hold", "hold"),
        ("Ney, march to Orleanais and drill", "drill"),
        ("Ney, march to Orleanais then defend it", "defend"),
    ])
    def test_the_march_carries_the_verb(self, shipped, line, verb):
        result = parse(line)
        assert result.get("strategic_type") == "MOVE_TO", result
        assert result.get("arrival_verb") == verb, result
        assert result.get("dropped_sequel") is None, result

    def test_a_third_clause_is_split_and_named(self, shipped):
        result = parse("Ney, march to Orleanais then fortify then attack Mack")
        assert result.get("arrival_verb") == "fortify"
        assert result.get("dropped_sequel") == "attack Mack"

    def test_the_first_step_arrival_acts_at_once_and_pays_once(self, shipped):
        """Lorraine is one march from Rhineland: he arrives on the order's
        own first step and fortifies there — the march's price, nothing more
        (Davout's fortify from the neutral stance would cost 2 on its own)."""
        world = M.world
        davout = world.get_marshal("Davout")
        price = davout.strategic_order_ap(order_type="MOVE_TO")
        ap = world.actions_remaining
        reply = run(shipped, "Davout, march to Lorraine then fortify")
        assert reply.get("success") is True, reply.get("message")
        assert "fortif" in reply["message"], reply["message"]
        davout = M.world.get_marshal("Davout")
        assert davout.location == "Lorraine" and davout.fortified is True
        assert davout.strategic_order is None
        assert M.world.actions_remaining == ap - price

    def test_the_verb_fires_on_arrival_free(self, shipped):
        """Orleanais is two marches off: the verb waits for the arrival and
        is done at no cost — the pass runs with no action left."""
        reply = run(shipped, "Ney, march to Orleanais then drill")
        assert reply.get("success") is True, reply.get("message")
        assert M.world.get_marshal("Ney").location == "Lorraine"
        _as_if_given_yesterday("Ney")
        M.world.actions_remaining = 0
        rows = _row(_tick(), "Ney")
        ney = M.world.get_marshal("Ney")
        assert ney.location == "Orleanais"
        assert ney.drilling is True, rows
        assert ney.strategic_order is None
        assert any(r.get("action") == "drill_on_arrival" for r in rows), rows

    def test_hold_on_arrival_becomes_a_standing_hold(self, shipped):
        run(shipped, "Ney, march to Orleanais then hold")
        _as_if_given_yesterday("Ney")
        rows = _row(_tick(), "Ney")
        order = M.world.get_marshal("Ney").strategic_order
        assert order is not None and order.command_type == "HOLD", rows
        assert order.target == "Orleanais"
        assert order.issued_turn == M.world.current_turn   # its first tick is the next turn's
        assert any(r.get("action") == "hold_on_arrival" for r in rows), rows

    def test_a_verb_refused_on_arrival_is_named(self, shipped):
        """Lorraine borders Mack's Swabia: no drill with the enemy that near.
        The march ends there and says why — never a silent arrival."""
        reply = run(shipped, "Davout, march to Lorraine then drill")
        message = reply.get("message") or ""
        davout = M.world.get_marshal("Davout")
        assert davout.location == "Lorraine", message
        assert davout.drilling is False
        assert davout.strategic_order is None
        assert "cannot drill" in message, message

    def test_the_orders_tab_and_the_arrow_name_the_verb(self, shipped):
        from backend.commands.strategic import standing_order_road
        run(shipped, "Ney, march to Orleanais then fortify")
        assert _forces_row("Ney")["strategic_order"].endswith("— then fortify")
        assert standing_order_road(M.world, M.world.get_marshal("Ney"))["then"] == "fortify"


class TestCCX20TheVerbIsPartOfTheOrder:
    """CC-X20: the F10 no-op ("already carrying out that order") compared
    type and target only, so `march to X then fortify` over a standing
    `march to X` was refused and the verb lost."""

    def test_a_verb_added_to_a_standing_march_is_a_new_order(self, shipped):
        """Measured before the fix: "Ney is already carrying out that order"
        and the verb was lost. Now it goes out — one march left, so he
        arrives at once and fortifies."""
        run(shipped, "Ney, march to Orleanais")
        reply = run(shipped, "Ney, march to Orleanais then fortify")
        assert "already carrying out" not in (reply.get("message") or ""), reply.get("message")
        ney = M.world.get_marshal("Ney")
        assert ney.location == "Orleanais" and ney.fortified is True

    def test_the_same_order_twice_is_still_the_no_op(self, shipped):
        run(shipped, "Ney, march to Orleanais then fortify")
        reply = run(shipped, "Ney, march to Orleanais then fortify")
        assert "already carrying out" in (reply.get("message") or ""), reply.get("message")

    def test_the_contingency_is_part_of_the_hold(self, shipped):
        run(shipped, "Ney, if Mack advances fall back to Lorraine")
        same = run(shipped, "Ney, if Mack advances fall back to Lorraine")
        assert "already carrying out" in (same.get("message") or "")
        other = run(shipped, "Ney, if Mack advances fall back to Brabant")
        assert "already carrying out" not in (other.get("message") or ""), other.get("message")
        assert M.world.get_marshal("Ney").strategic_order.contingency["to"] == "Brabant"


class TestCCX22AMoveWithAVerbIsTheMarch:
    """CC-X22: CR-7-1's rider promoted `move to X … attack Y` to the march
    idiom; an arrival verb did not promote, so `move to X then fortify`
    relayed its verb while `march to X then fortify` carried it."""

    def test_the_move_head_is_promoted(self, shipped):
        result = parse("Ney, move to Orleanais then fortify")
        assert result.get("strategic_type") == "MOVE_TO", result
        assert result.get("arrival_verb") == "fortify", result

    def test_a_second_mans_order_never_promotes_the_first(self, shipped):
        result = parse("Ney, move to Lorraine and Davout, hold")
        assert result.get("is_strategic") is not True, result
        assert result.get("arrival_verb") is None
        assert (result.get("command") or {}).get("action") == "move"

    def test_a_bare_move_stays_tactical(self, shipped):
        result = parse("Ney, move to Lorraine")
        assert result.get("is_strategic") is not True, result


D6_LINES = [
    ("Ney, fortify then attack Mack", "Ney, attack Mack then fortify"),
    ("Davout, form square, then attack Mack", "Davout, attack Mack then form square"),
    ("Ney, go defensive then attack Mack", "Ney, attack Mack then go defensive"),
    ("Ney, fortify then march to Lorraine", "Ney, march to Lorraine then fortify"),
    ("Ney, go defensive then march to Lorraine", "Ney, march to Lorraine then defend"),
]


class TestD6TheContradictionIsAskedFirst:
    """D6 (the user's ruling, October 19, 2026: "ask first, spend
    nothing"): a head that would leave the corps standing with a tail that
    moves or attacks sends NOTHING; the order that gives both is offered
    beside the line (never on it, never sent)."""

    @pytest.mark.parametrize("line,remedy", D6_LINES)
    def test_nothing_goes_out_and_the_reorder_is_offered(self, shipped, line, remedy):
        world = M.world
        name = line.split(",")[0]
        before = (world.get_marshal(name).location, world.get_marshal(name).fortified,
                  world.actions_remaining)
        reply = run(shipped, line)
        m = M.world.get_marshal(name)
        assert reply.get("success") is False, reply.get("message")
        assert (m.location, m.fortified, M.world.actions_remaining) == before
        assert m.strategic_order is None and not getattr(m, "in_square", False)
        assert reply.get("remedy_command") == remedy, reply
        assert reply.get("relay_kind") == "contradiction"
        assert "Nothing has gone out" in (reply.get("message") or "")
        assert not reply.get("battle_report")

    def test_the_offered_line_does_both(self, shipped):
        reply = run(shipped, "Ney, fortify then march to Lorraine")
        done = run(shipped, reply["remedy_command"])
        assert done.get("success") is True, done.get("message")
        ney = M.world.get_marshal("Ney")
        assert ney.location == "Lorraine" and ney.fortified is True

    def test_with_no_coherent_reorder_the_head_goes_out_as_before(self, shipped, monkeypatch):
        """The tail illegal now (the state probe refuses it): no reorder is
        offered and CR-7-3's road stands — the head goes out, the tail is
        named. Sensitivity: this is the arm D6 must not swallow."""
        import backend.commands.state_probe as probe
        monkeypatch.setattr(probe, "order_state_refusal", lambda *a, **k: "refused")
        reply = run(shipped, "Davout, fortify then attack Mack")
        assert reply.get("success") is True, reply.get("message")
        assert M.world.get_marshal("Davout").fortified is True
        assert not reply.get("remedy_command")
        assert reply.get("dropped_sequel") == "attack Mack"


class TestD8TheStandingContingency:
    """D8: `Ney, if Mack advances fall back to Lorraine` — a HOLD where he
    stands that watches its province and the neighbours we SEE, and fires
    at no cost at the turn's end."""

    def test_it_is_issued_as_a_watching_hold(self, shipped):
        world = M.world
        price = world.get_marshal("Ney").strategic_order_ap(order_type="HOLD")
        ap = world.actions_remaining
        reply = run(shipped, "Ney, if Mack advances fall back to Lorraine")
        assert reply.get("success") is True, reply.get("message")
        assert "watches Rhineland and its neighbours" in reply["message"]
        assert "Mack is within reach already, at Swabia" in reply["message"]
        order = M.world.get_marshal("Ney").strategic_order
        assert order.command_type == "HOLD" and order.target == "Rhineland"
        assert order.contingency == {"who": "Mack", "then": "fall_back", "to": "Lorraine",
                                     "clause": "Ney, if Mack advances fall back to Lorraine"}
        assert M.world.actions_remaining == ap - price

    def test_a_seen_approach_fires_the_fall_back_free(self, shipped):
        run(shipped, "Ney, if Mack advances fall back to Lorraine")
        ap = M.world.actions_remaining
        rows = _row(_tick(), "Ney")
        ney = M.world.get_marshal("Ney")
        assert ney.location == "Lorraine", rows
        assert ney.strategic_order is None
        assert any(r.get("action") == "contingency_fired" for r in rows), rows
        assert M.world.actions_remaining == ap

    def test_never_on_a_fogged_province(self, shipped):
        from backend.models.intel import UNKNOWN
        run(shipped, "Ney, if Mack advances fall back to Lorraine")
        M.world.get_region_intel("Swabia").visibility = UNKNOWN
        _tick()
        order = M.world.get_marshal("Ney").strategic_order
        assert M.world.get_marshal("Ney").location == "Rhineland"
        assert order is not None and order.contingency

    def test_only_the_named_man_fires_it(self, shipped):
        reply = run(shipped, "Ney, if Kutuzov advances fall back to Lorraine")
        assert reply.get("success") is True, reply.get("message")
        _tick()
        assert M.world.get_marshal("Ney").location == "Rhineland"
        assert M.world.get_marshal("Ney").strategic_order.contingency["who"] == "Kutuzov"

    def test_a_fortified_holder_leaves_his_works(self, shipped):
        from backend.models.marshal import Stance
        ney = M.world.get_marshal("Ney")
        ney.fortified, ney.defense_bonus, ney.stance = True, 0.1, Stance.DEFENSIVE
        reply = run(shipped, "Ney, if Mack advances fall back to Lorraine")
        assert "leaves his works" in reply["message"]
        rows = _row(_tick(), "Ney")
        ney = M.world.get_marshal("Ney")
        assert ney.location == "Lorraine" and ney.fortified is False
        assert any("leaves his works and falls back" in (r.get("message") or "") for r in rows), rows

    def test_the_attack_arm_fights(self, shipped):
        import random
        random.seed(1805)
        mack = M.world.get_marshal("Mack")
        before = mack.strength
        run(shipped, "Ney, if the enemy comes within reach, attack")
        rows = _row(_tick(), "Ney")
        assert any(r.get("action") == "contingency_fired" for r in rows), rows
        assert M.world.get_marshal("Mack").strength < before
        assert M.world.get_marshal("Ney").strategic_order is None

    def test_a_fall_back_with_no_road_breaks_and_keeps_his_works(self, shipped, monkeypatch):
        from backend.models.marshal import Stance
        import backend.commands.strategic as road_law
        ney = M.world.get_marshal("Ney")
        ney.fortified, ney.defense_bonus, ney.stance = True, 0.1, Stance.DEFENSIVE
        run(shipped, "Ney, if Mack advances fall back to Lorraine")
        monkeypatch.setattr(road_law, "march_road",
                            lambda *a, **k: ([], {"message": "the road is closed."}, "road"))
        rows = _row(_tick(), "Ney")
        ney = M.world.get_marshal("Ney")
        assert any(r.get("action") == "contingency_refused" for r in rows), rows
        assert ney.fortified is True and ney.location == "Rhineland"
        assert ney.strategic_order is None

    def test_a_fall_back_to_where_he_stands_is_refused_free(self, shipped):
        ap = M.world.actions_remaining
        reply = run(shipped, "Ney, if Mack advances fall back to Rhineland")
        assert reply.get("success") is False
        assert "already stands at Rhineland" in reply["message"]
        assert M.world.actions_remaining == ap
        assert M.world.get_marshal("Ney").strategic_order is None

    def test_an_unknown_place_is_still_the_refused_contingency(self, shipped):
        ap = M.world.actions_remaining
        reply = run(shipped, "Ney, if Mack advances fall back to Narnia")
        assert reply.get("success") is False
        assert "contingency" in reply["message"]
        assert M.world.actions_remaining == ap

    def test_the_orders_tab_and_the_arrow_show_the_watch(self, shipped):
        from backend.commands.strategic import standing_order_road
        run(shipped, "Ney, if Mack advances fall back to Lorraine")
        assert _forces_row("Ney")["strategic_order"].endswith(
            "if Mack comes within reach, fall back to Lorraine")
        assert _orders_row("Ney")["condition"] == "until it fires"
        road = standing_order_road(M.world, M.world.get_marshal("Ney"))
        assert road["watch"] == "if Mack comes within reach, fall back to Lorraine"
        assert road["watch_who"] == "Mack"

    def test_both_fields_survive_a_save(self, shipped):
        from backend.models.marshal import StrategicOrder
        run(shipped, "Ney, if Mack advances fall back to Lorraine")
        run(shipped, "Davout, march to Orleanais then fortify")
        for name in ("Ney", "Davout"):
            order = M.world.get_marshal(name).strategic_order
            again = StrategicOrder.from_dict(order.to_dict())
            assert again.to_dict() == order.to_dict()
        assert StrategicOrder.from_dict(
            M.world.get_marshal("Davout").strategic_order.to_dict()).arrival_verb == "fortify"


class TestCCX21AContingencyIsNoAnswer:
    """CC-X21 (D8's sweep): with a contact question pending, `Ney, if the
    enemy comes within reach, attack` was read as its answer "attack" and
    fought at once. A conditional line is a fresh order, never an answer."""

    def test_the_contingency_is_issued_and_no_battle_is_fought(self, shipped):
        asked = run(shipped, "Ney, march to Bohemia")
        assert M.world.get_marshal("Ney").pending_interrupt, asked.get("message")
        mack = M.world.get_marshal("Mack").strength
        reply = run(shipped, "Ney, if the enemy comes within reach, attack")
        ney = M.world.get_marshal("Ney")
        assert not reply.get("battle_report"), reply.get("message")
        assert M.world.get_marshal("Mack").strength == mack
        assert ney.strategic_order.command_type == "HOLD"
        assert ney.strategic_order.contingency["then"] == "attack"
        assert not ney.pending_interrupt
        assert "This stops his march to Bohemia" in reply["message"]

    def test_the_rule_reads_the_guards_verdict(self, shipped):
        from backend.main import _line_is_a_contingency
        assert _line_is_a_contingency("Ney, attack anyway", M.world) is False
        assert _line_is_a_contingency("Ney, hold until Davout arrives", M.world) is False
        assert _line_is_a_contingency("Ney, if the enemy comes within reach, attack", M.world)
        assert _line_is_a_contingency("Ney, if Mack advances, fortify", M.world)

    def test_a_plain_answer_still_answers(self, shipped):
        run(shipped, "Ney, march to Bohemia")
        reply = run(shipped, "Ney, hold")
        assert not M.world.get_marshal("Ney").pending_interrupt, reply.get("message")


class TestCCX23ACautiousHoldRaisesItsWorks:
    """CC-X23 (D7's sweep — the fortify gate): a cautious marshal's HOLD
    fortifies each tick under `_strategic_execution`, and the gate asked the
    turn's actions of it — from the neutral stance with fewer than two left
    (the turn's end, as a rule) it was refused, while the report said
    "Davout fortifies Rhineland." (measured on a HEAD `d6a0cd8d` snapshot:
    `fortified` stayed False)."""

    def test_the_works_rise_at_the_turns_end_with_no_action_left(self, shipped):
        run(shipped, "Davout, hold")
        _as_if_given_yesterday("Davout")
        M.world.actions_remaining = 0
        rows = _row(_tick(), "Davout")
        assert M.world.get_marshal("Davout").fortified is True, rows
        assert any(r.get("action") == "hold_fortify" for r in rows), rows

    def test_a_refused_fortify_is_never_narrated_as_works(self, shipped):
        run(shipped, "Davout, hold")
        _as_if_given_yesterday("Davout")
        M.world.get_marshal("Davout").drilling = True
        rows = _row(_tick(), "Davout")
        assert M.world.get_marshal("Davout").fortified is False
        assert not any("fortifies" in (r.get("message") or "") for r in rows), rows
        assert any("cannot fortify" in (r.get("message") or "") for r in rows), rows


class TestCCX24TheSallySaysWhereHeStands:
    """CC-X24 (CC-X23's sweep, found by reading — a sally fires only on
    favourable odds and, on the 1805 board, ends at home, so the displaced
    return was not reproduced in play): the report said "then returns to
    Rhineland!" whatever the return march answered. Driven here with the
    sally's battle ending on the enemy's ground (a victory's advance) and
    the road back refused."""

    def test_a_refused_return_is_said(self, shipped, monkeypatch):
        import random
        random.seed(1805)
        run(shipped, "Ney, hold")
        _as_if_given_yesterday("Ney")
        M.world.get_marshal("Mack").strength = 4000      # a sally's odds
        executor_type = type(M.executor)
        real = executor_type.execute

        def advance_and_no_road_back(self, command, game_state):
            cmd = (command or {}).get("command") or {}
            if cmd.get("action") == "move" and cmd.get("_strategic_execution"):
                return {"success": False, "message": "the road back is closed."}
            result = real(self, command, game_state)
            if cmd.get("action") == "attack" and cmd.get("_strategic_execution"):
                M.world.get_marshal("Ney").location = "Swabia"   # the advance
            return result
        monkeypatch.setattr(executor_type, "execute", advance_and_no_road_back)
        rows = _row(_tick(), "Ney")
        sally = next(r for r in rows if r.get("action") in ("sally", "glorious_charge_sally"))
        assert M.world.get_marshal("Ney").location == "Swabia"
        assert sally["returned_to"] == "Swabia"
        assert "returns to Rhineland" not in sally["message"], sally["message"]
        assert "stands at Swabia, short of Rhineland" in sally["message"], sally["message"]


class TestD8TheContingencysAttackIsAnOrderSeam:
    """The FA slice-3 census's seventeenth producer (`_fire_contingency`'s
    attack): a refused strike is never narrated as a battle — the order
    breaks with the executor's own reason (FA-14's rule)."""

    def test_a_refused_attack_breaks_the_hold_with_its_reason(self, shipped, monkeypatch):
        run(shipped, "Ney, if the enemy comes within reach, attack")
        executor_type = type(M.executor)
        real = executor_type.execute

        def refuse_the_strike(self, command, game_state):
            cmd = (command or {}).get("command") or {}
            if cmd.get("action") == "attack" and cmd.get("_strategic_execution"):
                return {"success": False, "message": "the bridge is down."}
            return real(self, command, game_state)
        monkeypatch.setattr(executor_type, "execute", refuse_the_strike)
        mack = M.world.get_marshal("Mack").strength
        rows = _row(_tick(), "Ney")
        row = next(r for r in rows if r.get("action") == "contingency_refused")
        assert "cannot attack: the bridge is down." in row["message"], row
        assert "attacks, as you ordered" not in row["message"]
        assert M.world.get_marshal("Mack").strength == mack
        assert M.world.get_marshal("Ney").strategic_order is None
