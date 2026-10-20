"""ACH-F1 … F3 — THE THREE FINDS ACH-1 FILED OUTSIDE ITS CLASS (October 19,
2026; a side session beside Pre-Deploy S13b part 4; the records are
`docs/BUG_FIXES.md` §ACH-1, the rule `docs/SYSTEMS_REFERENCE.md` §131.3).
Each was reproduced on the shipped 1805 boot through the real
`POST /command` before its fix; the harness is ACH-1's own
(`tests/test_action_cost_honesty.py`: `_board`, `_order`, `_post`,
`_said`, `_honest`).

ACH-F1 (P2): `Ney, aggressive stance` then `Ney, defend` replied "Error:
'NoneType' object has no attribute 'lower'". The parser stamps a bare
verb's `target` PRESENT with None and `_find_compromise` read it with
`.get('target', '')`. One reading of "the same order" now serves Master
Rule #2's tests (`disobedience.order_key`): a None target reads as none,
and an in-place verb that names no target reads as his location — or the
compromise `defend` at his feet would be offered as if it were not the
order given. The sweep's census found the crash on eight roads (the four
aggressive marshals, aggressive or drilling) and nowhere else.

ACH-X9 (F1's sweep): the objection F1 now raises carries no compromise,
and the tactical route accepted a typed 'compromise' it never offered — the
validator read "an alternative OR a compromise" — and ran the order as
given with no trust cost. `dialogue_routing.tactical_objection_answers` is
the one list of the reply, the block, the validator and the re-prompts.

ACH-F2 (the user's ruling, October 19, 2026 — charge 1 at the answer): the
glorious charge's popup buttons fought the battle for nothing while the
typed `charge` / `restrain` paid R18's 1. `/respond_to_glorious_charge`
now charges the answer through `spend_actions` and says so; a press the
pool cannot pay is refused in the typed road's words, the charge pending.

ACH-F3 (the user's ruling — refuse, keep the objection): a strategic
objection blocks nothing, so the pool fell while it waited and the tail
charged what was left — the 2-action PURSUE for 1, every answer for nothing
at an empty pool. The answer is refused at the head, in the typed road's
words, at the price its button quotes; the objection stands.

ACH-X10 (F3's sweep): the tactical road refused an unpayable answer only
after `handle_response` had paid or penalised the marshal and cleared the
question (`Ney, defend` from the aggressive stance at one action: 13 trust
lost, nothing done). The answer is priced first (`tactical_executor.
order_price`, the executors' own figures, pinned against them) and refused
with the objection kept; the popup quotes the defend's two actions.
"""

import pytest

import backend.main as M
from backend.commands import dialogue_routing as DR
from backend.commands import disobedience as D
from backend.commands import executor as executor_mod
from backend.commands import strategic_executor as se_mod
from backend.commands import tactical_executor as TE
from backend.commands.disobedience import order_key
from backend.commands.objection_v2 import ConcernLevel
from backend.models.marshal import Stance
from backend.models.world_state import WorldState
from tests.test_action_cost_honesty import (  # noqa: F401 — the fixture
    _board,
    _honest,
    _order,
    _post,
    _restore_active_world,
    _said,
)


@pytest.fixture
def client(monkeypatch):
    return _board(monkeypatch)


def _aggressive(client, name):
    reply, spent, _ = _order(client, f"{name}, aggressive stance")
    assert reply.get("success") and spent == 1, reply.get("message")
    assert M.world.get_marshal(name).stance == Stance.AGGRESSIVE


def _drilling(client, name):
    marshal = M.world.get_marshal(name)
    marshal.drilling = True
    marshal.drill_complete_turn = M.world.current_turn + 1


_THE_STATES = {"aggressive": _aggressive, "drilling": _drilling}


def _crashed(reply) -> bool:
    return "NoneType" in str(reply.get("message") or "") or \
        str(reply.get("message") or "").startswith("Error:")


# ═══════════════════════════════════════════════════════════════════════
# ACH-F1 — the bare defend is answered
# ═══════════════════════════════════════════════════════════════════════

class TestACHF1TheBareDefendIsAnswered:

    def test_the_rows_own_line(self, client):
        """`Ney, aggressive stance` then `Ney, defend`: his objection — the
        attack on Mack he would rather make — and nothing spent; no
        compromise, since the only one left is the order he was given."""
        _aggressive(client, "Ney")
        reply, spent, _ = _order(client, "Ney, defend")
        assert not _crashed(reply), reply.get("message")
        objection = M.world.pending_objection
        assert objection, reply.get("message")
        assert "Ney firmly objects" in str(reply.get("message")), reply.get("message")
        assert (objection["suggested_alternative"]["action"],
                objection["suggested_alternative"]["target"]) == ("attack", "Mack")
        assert objection["compromise"] is None
        assert (spent, _said(reply)) == (0, 0)

    @pytest.mark.parametrize("name", ["Ney", "Murat", "Massena", "Lannes"])
    @pytest.mark.parametrize("state", ["aggressive", "drilling"])
    def test_every_road_the_census_crashed(self, client, name, state):
        """The sweep's dynamic census (every marshal x five states x 45
        lines, every objection answered four ways — 2,356 runs on HEAD)
        crashed on exactly these eight; all of them are answered now."""
        _THE_STATES[state](client, name)
        reply, spent, _ = _order(client, f"{name}, defend")
        assert not _crashed(reply), reply.get("message")
        assert M.world.pending_objection, reply.get("message")
        assert spent == 0

    @pytest.mark.parametrize("choice,price,stance", [
        ("trust", 1, Stance.AGGRESSIVE),    # his attack on Mack
        ("insist", 2, Stance.DEFENSIVE),    # aggressive -> defensive: two steps
    ])
    def test_each_answer_does_what_it_says(self, client, choice, price, stance):
        _aggressive(client, "Ney")
        _order(client, "Ney, defend")
        reply, spent, _ = _post(client, "/respond_to_objection", {"choice": choice})
        assert reply.get("success"), reply.get("message")
        assert spent == price, (choice, spent)
        _honest(reply, spent, f"Ney, defend -> {choice}")
        assert M.world.get_marshal("Ney").stance == stance
        assert M.world.pending_objection is None

    def test_a_distinct_compromise_is_still_offered(self, client):
        """FALSIFIABLE NEGATIVE — the fix rejects only the order itself: from
        NEUTRAL the aggressive stance is a real middle road and stays one."""
        reply, _, _ = _order(client, "Ney, defend")
        objection = M.world.pending_objection
        assert objection, reply.get("message")
        assert objection["compromise"] == {
            "action": "stance_change", "target": "aggressive",
            "target_stance": "aggressive",
            "description": objection["compromise"].get("description")}

    @pytest.mark.parametrize("line", ["Ney, defend", "Ney, defend Rhineland"])
    def test_the_order_is_never_its_own_compromise(self, client, line):
        """Named or bare, a defend where he stands is the same order — the
        compromise `defend` at his feet is never offered for it."""
        _aggressive(client, "Ney")
        _order(client, line)
        objection = M.world.pending_objection
        assert objection
        comp = objection["compromise"]
        assert comp is None or order_key(comp, M.world.get_marshal("Ney")) != \
            order_key(objection["original_order"], M.world.get_marshal("Ney"))


class TestOrderKey:
    """`order_key` — the one reading of "the same order"."""

    class _At:
        location = "Rhineland"

    @pytest.mark.parametrize("order,key", [
        ({"action": "defend", "target": None}, ("defend", "rhineland")),
        ({"action": "defend"}, ("defend", "rhineland")),
        ({"action": "defend", "target": "Rhineland"}, ("defend", "rhineland")),
        ({"action": "fortify", "target": None}, ("fortify", "rhineland")),
        ({"action": "drill", "target": None}, ("drill", "rhineland")),
        # Not an in-place verb: no target stays no target.
        ({"action": "attack", "target": None}, ("attack", "")),
        ({"action": "move", "target": None}, ("move", "")),
        ({"action": "stance_change", "target": "aggressive",
          "target_stance": "aggressive"}, ("stance_change", "aggressive")),
        ({"action": None, "target": None}, ("", "")),
    ])
    def test_the_reading(self, order, key):
        assert order_key(order, self._At()) == key

    def test_none_and_no_marshal(self):
        assert order_key(None) == ("", "")
        assert order_key({"action": "defend", "target": None}) == ("defend", "")


# ═══════════════════════════════════════════════════════════════════════
# ACH-X9 — no answer the objection never offered
# ═══════════════════════════════════════════════════════════════════════

class TestACHX9NoPhantomCompromise:

    @pytest.mark.parametrize("line", ["Ney, defend", "Ney, defend Rhineland"])
    def test_a_compromise_never_offered_is_refused(self, client, line):
        """`Ney, defend Rhineland` from the aggressive stance reached this on
        HEAD (the census: 2 of 139 compromise answers fell back to the order
        — "Order proceeds as given.", the stance shifted, no trust lost);
        ACH-F1 added the bare defend. Refused now, the objection kept."""
        _aggressive(client, "Ney")
        asked, _, _ = _order(client, line)
        assert asked.get("choices") == ["trust", "insist"], asked.get("choices")
        ney = M.world.get_marshal("Ney")
        trust_before = int(ney.trust.value)
        reply, spent, _ = _order(client, "compromise")
        assert reply.get("success") is False, reply.get("message")
        assert "not one of the roads open" in str(reply.get("message")), reply.get("message")
        assert "'compromise'" in str(reply.get("message"))
        assert M.world.pending_objection is not None, "the objection stands"
        assert (spent, int(ney.trust.value), ney.stance) == (0, trust_before, Stance.AGGRESSIVE)

    @pytest.mark.parametrize("line", [
        "Davout, fortify",   # the executor's block
        "proceed",           # main's re-prompt for a dialogue-ish word
    ])
    def test_the_block_names_the_same_roads(self, client, line):
        _aggressive(client, "Ney")
        _order(client, "Ney, defend")
        reply, spent, _ = _order(client, line)
        assert reply.get("success") is False and spent == 0
        assert "Ney awaits your answer" in str(reply.get("message")), reply.get("message")
        assert str(reply.get("message")).endswith("Reply 'trust' or 'insist'.") or \
            str(reply.get("message")).endswith("reply 'trust' or 'insist'."), reply.get("message")

    def test_a_real_compromise_is_still_taken(self, client):
        """FALSIFIABLE NEGATIVE — from NEUTRAL the compromise exists and the
        word takes it."""
        asked, _, _ = _order(client, "Ney, defend")
        assert asked.get("choices") == ["trust", "insist", "compromise"]
        reply, spent, _ = _post(client, "/respond_to_objection", {"choice": "compromise"})
        assert reply.get("success"), reply.get("message")
        assert M.world.get_marshal("Ney").stance == Stance.AGGRESSIVE
        assert spent == 1

    def test_the_get_reads_the_same_list(self, client):
        _aggressive(client, "Ney")
        _order(client, "Ney, defend")
        with _quiet_get(client) as data:
            assert data["choices"] == ["trust", "insist"]
            assert data["alternative"]["action"] == "attack"


class _quiet_get:
    def __init__(self, client):
        self.client = client

    def __enter__(self):
        return self.client.get("/pending_objection").json()

    def __exit__(self, *exc):
        return False


# ═══════════════════════════════════════════════════════════════════════
# ACH-F2 — the glorious charge's answer pays the attack's price
# ═══════════════════════════════════════════════════════════════════════

def _the_popup(client, recklessness=3):
    """Murat at recklessness 3 attacks Mack: the popup, nothing spent."""
    murat = M.world.get_marshal("Murat")
    murat.recklessness = recklessness
    reply, spent, _ = _order(client, "Murat, attack Mack")
    assert reply.get("pending_glorious_charge"), reply.get("message")
    assert murat.pending_glorious_charge and spent == 0
    return murat


def _the_button(client, choice):
    return _post(client, "/respond_to_glorious_charge", {"choice": choice})


def _empty_the_pool(client):
    for line in ("Ney, hold", "Lannes, hold"):
        _order(client, line)
    assert M.world.actions_remaining == 0


class TestACHF2TheChargeIsPaid:

    @pytest.mark.parametrize("choice", ["charge", "restrain"])
    def test_the_button_pays_the_attacks_price(self, client, choice):
        """Measured on HEAD: 4 -> 4 -> 4 on both buttons."""
        _the_popup(client)
        reply, spent, _ = _the_button(client, choice)
        assert reply.get("success"), reply.get("message")
        assert spent == 1
        _honest(reply, spent, f"the {choice} button")
        assert reply["action_info"]["remaining"] == 3

    @pytest.mark.parametrize("choice", ["charge", "restrain"])
    def test_the_typed_word_and_the_button_agree(self, monkeypatch, choice):
        prices = []
        for road in ("typed", "button"):
            client = _board(monkeypatch)
            _the_popup(client)
            reply, spent, _ = (_order(client, choice) if road == "typed"
                               else _the_button(client, choice))
            assert reply.get("success"), (road, reply.get("message"))
            _honest(reply, spent, f"{road} {choice}")
            prices.append(spent)
        assert prices == [1, 1]

    @pytest.mark.parametrize("recklessness", [0, 4])
    def test_the_same_attack_without_the_popup_costs_one(self, client, recklessness):
        """The reference: no question at recklessness 0, the auto-charge at
        4 — each 1."""
        M.world.get_marshal("Murat").recklessness = recklessness
        reply, spent, _ = _order(client, "Murat, attack Mack")
        assert reply.get("success") and not reply.get("pending_glorious_charge"), reply.get("message")
        assert spent == 1

    @pytest.mark.parametrize("choice", ["charge", "restrain"])
    def test_a_press_the_pool_cannot_pay_is_refused_and_the_charge_waits(self, client, choice):
        """The pending charge blocks nothing: with the pool emptied the
        button fought the battle for nothing. Refused now in the typed
        road's words — and the typed word, after it, still finds the charge."""
        murat = _the_popup(client)
        _empty_the_pool(client)
        reply, spent, _ = _the_button(client, choice)
        assert reply.get("success") is False
        assert reply.get("message") == "Not enough actions! Need 1, have 0."
        assert spent == 0 and murat.pending_glorious_charge and murat.recklessness == 3
        typed, spent, _ = _order(client, choice)
        assert (typed.get("message"), spent) == ("Not enough actions! Need 1, have 0.", 0)
        assert murat.pending_glorious_charge

    def test_no_charge_waiting_is_still_said_so(self, client):
        reply, spent, _ = _the_button(client, "charge")
        assert reply.get("success") is False and spent == 0
        assert "No pending Glorious Charge" in str(reply.get("message"))


# ═══════════════════════════════════════════════════════════════════════
# ACH-F3 — a strategic answer the pool cannot pay is refused
# ═══════════════════════════════════════════════════════════════════════

def _davouts_objection(client, line="Davout, pursue Mack"):
    asked, spent, _ = _order(client, line)
    assert M.world.pending_strategic_objection, asked.get("message")
    assert spent == 0
    return M.world.get_marshal("Davout")


def _drain_to(client, pool):
    lines = {1: ("Ney, hold", "Soult, march to Burgundy"), 0: ("Ney, hold", "Lannes, hold")}[pool]
    for line in lines:
        _order(client, line)
    assert M.world.actions_remaining == pool
    assert M.world.pending_strategic_objection, "a strategic objection blocks nothing"


def _ledger(davout):
    world = M.world
    return (int(davout.trust.value), int(world.authority_tracker.authority),
            len(world.authority_tracker.recent_responses), davout.strategic_order,
            davout.location)


class TestACHF3TheShortPoolIsRefused:

    def test_the_rows_own_line(self, client):
        """`Davout, pursue Mack` objects; `Ney, hold` and `Soult, march to
        Burgundy` leave one action; Insist stood the PURSUE for 1."""
        davout = _davouts_objection(client)
        _drain_to(client, 1)
        before = _ledger(davout)
        reply, spent, _ = _post(client, "/respond_to_objection", {"choice": "insist"})
        assert reply.get("success") is False
        assert reply.get("message") == (
            "Not enough actions! Need 2, have 1 — Davout cannot pursue Mack today. "
            "Davout's objection stands — reply 'trust' or 'cancel'; unanswered, "
            "it lapses at the turn's end."), reply.get("message")
        assert spent == 0 and _said(reply) == 0
        assert M.world.pending_strategic_objection, "the objection stands"
        assert _ledger(davout) == before, "nothing is recorded: trust, authority, order, place"

    def test_the_typed_order_says_the_same_words(self, client):
        _drain_to_without_an_objection(client, 1)
        typed, spent, _ = _order(client, "Davout, pursue Mack")
        assert spent == 0
        assert typed.get("message") == "Not enough actions! Need 2, have 1 — Davout cannot pursue Mack today."

    @pytest.mark.parametrize("line,choice", [
        ("Davout, pursue Mack", "insist"),
        ("Davout, pursue Mack", "trust"),
        ("Davout, pursue Mack", "compromise"),
        ("Davout, march to Swabia", "insist"),
        ("Davout, support Bernadotte", "insist"),
        ("Davout, support Bernadotte", "trust"),
    ])
    def test_at_an_empty_pool_every_answer_is_refused(self, client, line, choice):
        """Measured on HEAD: each went through for nothing — the SUPPORT
        even took its first step to Lorraine."""
        davout = _davouts_objection(client, line)
        _drain_to(client, 0)
        before = _ledger(davout)
        reply, spent, _ = _post(client, "/respond_to_objection", {"choice": choice})
        assert reply.get("success") is False, (line, choice, reply.get("message"))
        assert str(reply.get("message")).startswith("Not enough actions! Need "), reply.get("message")
        assert "reply 'cancel'" in str(reply.get("message"))
        assert spent == 0 and _ledger(davout) == before
        assert M.world.pending_strategic_objection

    def test_cancel_stays_free(self, client):
        _davouts_objection(client)
        _drain_to(client, 0)
        reply, spent, _ = _post(client, "/respond_to_objection", {"choice": "cancel"})
        assert reply.get("success") and reply.get("objection_withdrawn"), reply.get("message")
        assert spent == 0 and M.world.pending_strategic_objection is None

    def test_an_answer_the_pool_can_pay_still_goes(self, client):
        """FALSIFIABLE NEGATIVE: Trust's 1 at one action."""
        _davouts_objection(client)
        _drain_to(client, 1)
        reply, spent, _ = _post(client, "/respond_to_objection", {"choice": "trust"})
        assert reply.get("success"), reply.get("message")
        assert spent == 1
        _honest(reply, spent)


def _drain_to_without_an_objection(client, pool):
    for line in {1: ("Ney, hold", "Soult, march to Burgundy")}[pool]:
        _order(client, line)
    assert M.world.actions_remaining == pool


# ═══════════════════════════════════════════════════════════════════════
# ACH-X10 — the tactical answer is priced before it is recorded
# ═══════════════════════════════════════════════════════════════════════

def _tactical(client, line, stance=None, pool=None):
    ney = M.world.get_marshal("Ney")
    if stance is not None:
        ney.stance = stance
    if pool is not None:
        M.world.actions_remaining = pool
    asked, spent, _ = _order(client, line)
    assert M.world.pending_objection, asked.get("message")
    return ney, asked


def _tactical_ledger(ney):
    world = M.world
    return (int(ney.trust.value), int(world.authority_tracker.authority),
            len(world.authority_tracker.recent_responses), ney.stance)


class TestACHX10TheTacticalAnswerIsPriced:

    def test_the_insist_the_pool_cannot_pay(self, client):
        """`Ney, defend` from the aggressive stance at one action — on HEAD
        Insist cost 13 trust and did nothing, the objection gone."""
        ney, asked = _tactical(client, "Ney, defend", Stance.AGGRESSIVE, pool=1)
        assert ("(Insisting costs 2 actions — he must first abandon his "
                "aggressive posture.)") in str(asked.get("message")), asked.get("message")
        before = _tactical_ledger(ney)
        reply, spent, _ = _post(client, "/respond_to_objection", {"choice": "insist"})
        assert reply.get("success") is False
        assert reply.get("message") == (
            "Not enough actions! Need 2, have 1 — Ney cannot stand on the defensive "
            "today. Ney's objection stands — reply 'trust' or 'cancel'."), reply.get("message")
        assert spent == 0 and _tactical_ledger(ney) == before
        assert M.world.pending_objection, "the objection stands"
        # The road still open: his attack on Mack, one action.
        reply, spent, _ = _post(client, "/respond_to_objection", {"choice": "trust"})
        assert reply.get("success"), reply.get("message")
        assert spent == 1

    def test_the_compromise_the_pool_cannot_pay(self, client):
        """From DEFENSIVE the compromise is the aggressive stance (two
        steps): on HEAD it paid Ney +3 trust and did nothing."""
        ney, _ = _tactical(client, "Ney, fortify", Stance.DEFENSIVE, pool=1)
        assert M.world.pending_objection["compromise"]["target_stance"] == "aggressive"
        before = _tactical_ledger(ney)
        reply, spent, _ = _post(client, "/respond_to_objection", {"choice": "compromise"})
        assert reply.get("success") is False
        assert str(reply.get("message")).startswith(
            "Not enough actions! Need 2, have 1 — Ney cannot change stance today."), reply.get("message")
        assert "reply 'trust', 'insist' or 'cancel'" in str(reply.get("message"))
        assert spent == 0 and _tactical_ledger(ney) == before
        assert M.world.pending_objection

    def test_a_pool_that_fell_while_he_waited(self, client):
        """The Orders tab's Cancel is not held by a tactical objection, so
        the pool can fall while one waits: 4 → Davout's hold (2) → Ney's
        objection at 2 (his defend costs 2) → the Cancel button (1) → 1."""
        _order(client, "Davout, hold")
        ney, _ = _tactical(client, "Ney, defend", Stance.AGGRESSIVE)
        assert M.world.actions_remaining == 2
        cancelled, spent, _ = _post(client, "/cancel_order", {"marshal": "Davout"})
        assert cancelled.get("success") and spent == 1, cancelled.get("message")
        before = _tactical_ledger(ney)
        reply, spent, _ = _post(client, "/respond_to_objection", {"choice": "insist"})
        assert reply.get("success") is False, reply.get("message")
        assert "Ney's objection stands — reply 'trust' or 'cancel'." in str(reply.get("message"))
        assert spent == 0 and _tactical_ledger(ney) == before

    def test_a_tail_behind_the_objection_keeps_waiting(self, client):
        """CR-7-3's relay: the tail that waits behind the objection is
        re-judged when it is answered. A refused answer answers nothing, so
        the tail waits on (the refusal carries the question's key, as RS-5's
        kept objection does), and comes back with the answer that goes."""
        M.world.actions_remaining = 1
        first, spent, _ = _order(client, "Ney, fortify then pursue Mack")
        assert M.world.pending_objection and spent == 0, first.get("message")
        assert first.get("relay_kind") == "question"
        refused, spent, _ = _post(client, "/respond_to_objection", {"choice": "insist"})
        assert refused.get("success") is False and spent == 0, refused.get("message")
        assert refused.get("relay_kind") == "question", refused.get("relay_kind")
        assert M.world._pending_relay is not None, "the tail still waits"
        answered, spent, _ = _post(client, "/respond_to_objection", {"choice": "trust"})
        assert answered.get("success") and spent == 1, answered.get("message")
        assert answered.get("dropped_sequel") == "pursue Mack"
        assert M.world._pending_relay is None

    def test_the_insist_quote(self, client):
        ney = M.world.get_marshal("Ney")
        ney.stance = Stance.AGGRESSIVE
        assert TE.insist_terms(M.world, ney, "defend") == (
            2, "he must first abandon his aggressive posture")
        ney.stance = Stance.NEUTRAL
        assert TE.insist_terms(M.world, ney, "defend") == (1, "")


def _no_objection(*args, **kwargs):
    return ConcernLevel.NONE


def _counter_punch(world):
    davout = world.get_marshal("Davout")
    davout.counter_punch_available = True
    davout.counter_punch_turns = 1


def _soult_far_from_mack(world):
    world.get_marshal("Soult").location = "Brittany"


class TestTheOraclePinnedToTheExecutors:
    """`order_price` against the pool's own fall when the order is typed —
    the drift guard: every verb the objection's answers can carry, in each
    stance its price moves with (objections flattened, so the order runs)."""

    @pytest.mark.parametrize("name,stance,setup,line,order", [
        ("Ney", Stance.NEUTRAL, None, "Ney, defend", {"action": "defend"}),
        ("Ney", Stance.AGGRESSIVE, None, "Ney, defend", {"action": "defend"}),
        ("Ney", Stance.DEFENSIVE, None, "Ney, defend", {"action": "defend"}),
        ("Ney", Stance.NEUTRAL, None, "Ney, fortify", {"action": "fortify"}),
        ("Ney", Stance.DEFENSIVE, None, "Ney, fortify", {"action": "fortify"}),
        ("Ney", Stance.NEUTRAL, None, "Ney, aggressive stance",
         {"action": "stance_change", "target": "aggressive", "target_stance": "aggressive"}),
        ("Ney", Stance.DEFENSIVE, None, "Ney, aggressive stance",
         {"action": "stance_change", "target": "aggressive", "target_stance": "aggressive"}),
        ("Ney", Stance.AGGRESSIVE, None, "Ney, neutral stance",
         {"action": "stance_change", "target": "neutral", "target_stance": "neutral"}),
        ("Ney", Stance.NEUTRAL, None, "Ney, form square", {"action": "form_square"}),
        ("Ney", Stance.NEUTRAL, None, "Ney, wait", {"action": "wait"}),
        ("Ney", Stance.NEUTRAL, None, "Ney, scout Swabia", {"action": "scout", "target": "Swabia"}),
        ("Ney", Stance.NEUTRAL, None, "Ney, attack Mack", {"action": "attack", "target": "Mack"}),
        ("Davout", Stance.NEUTRAL, _counter_punch, "Davout, attack Mack",
         {"action": "attack", "target": "Mack"}),
        ("Ney", Stance.NEUTRAL, None, "Ney, move to Lorraine", {"action": "move", "target": "Lorraine"}),
        ("Ney", Stance.NEUTRAL, None, "Ney, move to Paris", {"action": "move", "target": "Paris"}),
        ("Napoleon", Stance.NEUTRAL, None, "Napoleon, move to Paris", {"action": "move", "target": "Paris"}),
        ("Soult", Stance.NEUTRAL, _soult_far_from_mack, "Soult, drill", {"action": "drill"}),
    ])
    def test_the_price_is_the_charge(self, client, monkeypatch, name, stance, setup, line, order):
        monkeypatch.setattr(executor_mod, "evaluate_situation", _no_objection)
        marshal = M.world.get_marshal(name)
        marshal.stance = stance
        if setup is not None:
            setup(M.world)
        price = TE.order_price(M.world, marshal, order)
        reply, spent, _ = _order(client, line)
        assert reply.get("success"), (line, reply.get("message"))
        assert not M.world.pending_objection
        assert price == spent, (line, stance, price, spent)


# ═══════════════════════════════════════════════════════════════════════
# The sensitivity arms — each pin reds with its fix taken out
# ═══════════════════════════════════════════════════════════════════════

class TestTheSensitivityArms:

    def test_the_old_read_crashes_again(self, client, monkeypatch):
        """`.get('target', '')` put back: the row's crash returns."""
        def old_reading(order, marshal=None):
            order = order or {}
            return (order.get('action', '').lower(),
                    (order.get('target_stance') or order.get('target', '')).lower())
        monkeypatch.setattr(D, "order_key", old_reading)
        _aggressive(client, "Ney")
        reply, _, _ = _order(client, "Ney, defend")
        assert _crashed(reply), "the arm must reproduce the defect"
        assert "'NoneType' object has no attribute 'lower'" in reply["message"]

    def test_without_the_place_the_order_is_its_own_compromise(self, client, monkeypatch):
        """The idiom alone, without the in-place reading: the bare defend
        is answered, and its compromise is the order itself."""
        def idiom_only(order, marshal=None):
            order = order or {}
            return (str(order.get('action') or '').lower(),
                    str(order.get('target_stance') or order.get('target') or '').lower())
        monkeypatch.setattr(D, "order_key", idiom_only)
        _aggressive(client, "Ney")
        _order(client, "Ney, defend")
        comp = M.world.pending_objection["compromise"]
        assert (comp["action"], comp["target"]) == ("defend", "Rhineland"), \
            "the arm must reproduce the fake choice"

    def test_the_old_predicate_runs_the_order_for_nothing(self, client, monkeypatch):
        """ACH-X9's predicate put back ("an alternative or a compromise"):
        the typed 'compromise' runs the order as given, no trust lost."""
        def old_answers(objection):
            choices = ["trust", "insist"]
            if objection and (objection.get("suggested_alternative")
                              or objection.get("compromise")):
                choices.append("compromise")
            return choices
        monkeypatch.setattr(DR, "tactical_objection_answers", old_answers)
        _aggressive(client, "Ney")
        _order(client, "Ney, defend")
        ney = M.world.get_marshal("Ney")
        trust_before = int(ney.trust.value)
        reply, spent, _ = _post(client, "/respond_to_objection", {"choice": "compromise"})
        assert "Order proceeds as given." in str(reply.get("message")), reply.get("message")
        assert (spent, ney.stance, int(ney.trust.value)) == (2, Stance.DEFENSIVE, trust_before)

    def test_without_the_answers_charge_the_button_is_free(self, client, monkeypatch):
        """ACH-F2's charge taken out: the button fights for nothing again."""
        real = WorldState.spend_actions

        def skip_the_answer(self, action_type="generic", times=1):
            if action_type in ("charge", "restrain"):
                return {"action_cost": 0, "turn_advanced": False, "new_turn": None}
            return real(self, action_type, times)
        monkeypatch.setattr(WorldState, "spend_actions", skip_the_answer)
        _the_popup(client)
        reply, spent, _ = _the_button(client, "charge")
        assert reply.get("success") and (spent, _said(reply)) == (0, 0), \
            "the arm must reproduce the defect"

    def test_without_the_gate_the_empty_pool_fights(self, client, monkeypatch):
        """ACH-F2's gate taken out (the answer priced at 0): at an empty pool
        the battle is fought for nothing and the charge is spent."""
        real = WorldState.get_action_cost
        monkeypatch.setattr(WorldState, "get_action_cost",
                            lambda self, action: 0 if action == "charge" else real(self, action))
        murat = _the_popup(client)
        _empty_the_pool(client)
        reply, spent, _ = _the_button(client, "charge")
        assert reply.get("success") and spent == 0, reply.get("message")
        assert murat.recklessness == 0 and not murat.pending_glorious_charge, \
            "the arm must reproduce the defect"

    def test_without_the_strategic_gate_the_short_pool_pays_half(self, client, monkeypatch):
        """ACH-F3's gate taken out: the 2-action PURSUE stands for 1."""
        monkeypatch.setattr(se_mod, "strategic_answer_price", lambda *a, **k: 0)
        davout = _davouts_objection(client)
        _drain_to(client, 1)
        reply, spent, _ = _post(client, "/respond_to_objection", {"choice": "insist"})
        assert reply.get("success") and spent == 1, reply.get("message")
        assert davout.strategic_order is not None and davout.strategic_order.command_type == "PURSUE", \
            "the arm must reproduce the defect"

    def test_with_the_face_price_the_insist_costs_trust_for_nothing(self, client, monkeypatch):
        """ACH-X10's oracle replaced by the verb's face price: Ney's insisted
        defend at one action loses his trust and the question, and does
        nothing."""
        monkeypatch.setattr(TE, "order_price",
                            lambda world, marshal, order: int(world.get_action_cost(
                                str((order or {}).get("action") or ""))))
        ney, _ = _tactical(client, "Ney, defend", Stance.AGGRESSIVE, pool=1)
        trust_before = int(ney.trust.value)
        reply, spent, _ = _post(client, "/respond_to_objection", {"choice": "insist"})
        assert reply.get("success") is False and spent == 0
        assert int(ney.trust.value) < trust_before and M.world.pending_objection is None, \
            "the arm must reproduce the defect"
        assert ney.stance == Stance.AGGRESSIVE
