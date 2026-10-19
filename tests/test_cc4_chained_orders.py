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
