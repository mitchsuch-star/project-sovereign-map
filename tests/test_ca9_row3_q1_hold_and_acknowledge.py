"""CA9 row 3 — Q1(b) the escalation hold, and §3 the honest refusal.

Audit record: `docs/audits/GRIEVANCE_REVISIT_INVESTIGATION_2026_08_09.md`
§3 and §5-Q1. Both rulings taken at the memo's recommendation.

**Why these two are one slice.** The audit's root cause was that escalation
history and level are written ONLY at fire time, so no petition arm could
reach either: measured over 9 turns, `acknowledge` / no-answer / `promise` /
`rebuke` all converged on escalation level 2, stored −2, coordination ×0.0,
differing only in price (0 AP / 0 AP / 7 AP / permanent −5 trust). And
`promise` cleared with `resolved_by_action=False`, forfeiting the +10% surge
the free battle path grants — so **the paid arm was strictly worse than
ignoring the popup, and ignoring it was byte-identical to Acknowledge.**

Q1(b) gives the paid arm the one thing no other arm can buy: the quarrel
cannot HARDEN while the Emperor's word stands. §3 then makes the free arm an
honest refusal with its price stated in men rather than adjectives. Together
they are what turns the card from a price list into a decision.

`TestTheArmsNoLongerConverge` is the falsifiable core — it is the audit's own
measurement, inverted.
"""

import pytest

from backend.game_logic import jealousy as J
from backend.models.marshal import Marshal

from tests.conftest import MarshalFactory, WorldFactory


@pytest.fixture()
def pair():
    murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                    strength=30000, personality="aggressive")
    davout = MarshalFactory.infantry(name="Davout", location="Paris",
                                     strength=30000, personality="cautious")
    world = WorldFactory.with_marshals([murat, davout])
    return world, world.marshals["Murat"], world.marshals["Davout"]


def _qualifying(marshal, target, stored=-1):
    """A pair whose next fire WOULD escalate: stored Rival-or-worse."""
    marshal.set_relationship(target.name, stored)
    target.set_relationship(marshal.name, stored)


# ════════════════════════════════════════════════════════════════════════
# Q1(b) — the hold
# ════════════════════════════════════════════════════════════════════════

class TestQ1TheHold:
    def test_a_qualifying_fire_escalates_without_a_hold(self, pair):
        """The baseline the hold acts against. Without it there is nothing
        to prove."""
        world, murat, davout = pair
        _qualifying(murat, davout)
        events = []
        J._check_escalation(world, murat, davout, events)
        assert J.get_escalation_level(murat, "Davout") == 1

    def test_a_hold_stops_the_next_rung(self, pair):
        world, murat, davout = pair
        _qualifying(murat, davout)
        murat.jealousy_escalation_hold["Davout"] = world.current_turn + 3
        events = []
        J._check_escalation(world, murat, davout, events)
        assert J.get_escalation_level(murat, "Davout") == 0
        assert J.get_escalation_level(davout, "Murat") == 0

    def test_the_hold_is_narrated_as_the_promise_holding(self, pair):
        world, murat, davout = pair
        _qualifying(murat, davout)
        murat.jealousy_escalation_hold["Davout"] = world.current_turn + 3
        events = []
        J._check_escalation(world, murat, davout, events)
        line = next(e for e in events
                    if e["type"] == "jealousy_escalation")["message"]
        assert "Emperor's word" in line, line
        assert line_does_not_claim_escalation(line), line

    def test_the_held_event_does_not_claim_a_level_it_did_not_reach(self, pair):
        world, murat, davout = pair
        _qualifying(murat, davout)
        murat.jealousy_escalation_hold["Davout"] = world.current_turn + 3
        events = []
        J._check_escalation(world, murat, davout, events)
        ev = next(e for e in events if e["type"] == "jealousy_escalation")
        assert ev["held"] is True
        assert ev["level"] == 0

    def test_an_expired_hold_stops_holding(self, pair):
        world, murat, davout = pair
        _qualifying(murat, davout)
        murat.jealousy_escalation_hold["Davout"] = world.current_turn - 1
        events = []
        J._check_escalation(world, murat, davout, events)
        assert J.get_escalation_level(murat, "Davout") == 1

    def test_the_hold_is_read_in_both_directions(self, pair):
        """`_set_escalation_level` writes the pair together, so a promise
        given to one man must not be defeated by his rival's fire arriving
        first."""
        world, murat, davout = pair
        _qualifying(murat, davout)
        davout.jealousy_escalation_hold["Murat"] = world.current_turn + 3
        events = []
        J._check_escalation(world, murat, davout, events)
        assert J.get_escalation_level(murat, "Davout") == 0

    def test_forced_escalation_bypasses_the_hold(self, pair):
        """Deliberate: the mutual-spiral path and the ladder's own tests pass
        `forced=True` and are asserting the ladder, not the promise."""
        world, murat, davout = pair
        _qualifying(murat, davout)
        murat.jealousy_escalation_hold["Davout"] = world.current_turn + 9
        events = []
        J._check_escalation(world, murat, davout, events, forced=True)
        assert J.get_escalation_level(murat, "Davout") == 1

    def test_the_hold_does_not_un_write_history(self, pair):
        """The ruling chose a hold over buying a rung back precisely because a
        hold cannot rewrite what already happened."""
        world, murat, davout = pair
        _qualifying(murat, davout)
        events = []
        J._check_escalation(world, murat, davout, events)
        assert J.get_escalation_level(murat, "Davout") == 1
        murat.jealousy_escalation_hold["Davout"] = world.current_turn + 5
        J._check_escalation(world, murat, davout, events)
        assert J.get_escalation_level(murat, "Davout") == 1, (
            "the hold must freeze the level, never lower it")


def line_does_not_claim_escalation(line: str) -> bool:
    for claim in ("has become entrenched", "matter of concern",
                  "no longer a passing mood"):
        if claim in line:
            return False
    return True


class TestQ1ThePromiseGrantsIt:
    def _queue_and_answer(self, world, murat, davout, choice):
        murat.jealous_of = "Davout"
        murat.jealousy_turns_remaining = 4
        J.queue_confrontation_petition(world, murat, davout, level=0)
        return J.handle_petition_response(world, choice)

    def test_promise_writes_the_hold_both_ways(self, pair):
        world, murat, davout = pair
        result = self._queue_and_answer(world, murat, davout, "promise")
        assert result["success"] is True
        expected = world.current_turn + J.CONFRONT_PROMISE_HOLD_TURNS
        assert murat.jealousy_escalation_hold["Davout"] == expected
        assert davout.jealousy_escalation_hold["Murat"] == expected

    def test_promise_says_so_in_the_message(self, pair):
        world, murat, davout = pair
        result = self._queue_and_answer(world, murat, davout, "promise")
        assert "go no further" in result["message"], result["message"]

    def test_letting_it_stand_writes_no_hold(self, pair):
        """The free arm must remain free of mechanical effect — §3 makes it an
        honest refusal, not a fourth price."""
        world, murat, davout = pair
        self._queue_and_answer(world, murat, davout, "acknowledge")
        assert murat.jealousy_escalation_hold == {}
        assert davout.jealousy_escalation_hold == {}

    def test_rebuke_writes_no_hold(self, pair):
        world, murat, davout = pair
        self._queue_and_answer(world, murat, davout, "rebuke")
        assert murat.jealousy_escalation_hold == {}

    def test_the_arm_states_the_hold_it_buys(self, pair):
        world, murat, davout = pair
        murat.jealous_of = "Davout"
        murat.jealousy_turns_remaining = 4
        J.queue_confrontation_petition(world, murat, davout, level=0)
        by_id = {o["id"]: o
                 for o in world.pending_marshal_petition["options"]}
        detail = by_id["promise"]["detail"]
        assert str(J.CONFRONT_PROMISE_HOLD_TURNS) in detail
        assert "cannot harden" in detail


class TestTheArmsNoLongerConverge:
    """The audit's own measurement, inverted. It held the glory gap constant
    over 9 turns and found `acknowledge` / no-answer / `promise` / `rebuke`
    ALL landing on escalation level 2. If they converge again, the card is a
    vending machine again and this row's core claim is false."""

    def _outcome(self, choice):
        murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                        strength=30000,
                                        personality="aggressive")
        davout = MarshalFactory.infantry(name="Davout", location="Paris",
                                         strength=30000,
                                         personality="cautious")
        world = WorldFactory.with_marshals([murat, davout])
        m, d = world.marshals["Murat"], world.marshals["Davout"]
        _qualifying(m, d)
        m.jealous_of = "Davout"
        m.jealousy_turns_remaining = 4
        if choice is not None:
            J.queue_confrontation_petition(world, m, d, level=0)
            J.handle_petition_response(world, choice)
        # A later qualifying fire, well inside the hold window.
        world.current_turn += 2
        J._check_escalation(world, m, d, [])
        return J.get_escalation_level(m, "Davout")

    def test_the_paid_arm_now_buys_a_different_outcome(self):
        assert self._outcome("promise") == 0
        assert self._outcome("acknowledge") == 1
        assert self._outcome(None) == 1

    def test_and_that_is_the_whole_difference(self):
        """Named explicitly so the claim is legible: the paid arm is the only
        one that changes where the pair ENDS UP, which is what makes it a
        decision rather than a price."""
        paid = self._outcome("promise")
        free = self._outcome("acknowledge")
        assert paid != free, (
            "every arm reaches the same escalation level again — the modal is "
            "back to being a price list")


# ════════════════════════════════════════════════════════════════════════
# §3 — the honest refusal
# ════════════════════════════════════════════════════════════════════════

class TestAcknowledgeBecomesLetItStand:
    def _arm(self, world, marshal, target):
        J.queue_confrontation_petition(world, marshal, target, level=0)
        by_id = {o["id"]: o
                 for o in world.pending_marshal_petition["options"]}
        return by_id["acknowledge"]

    def test_the_label_is_the_systems_own_vocabulary(self, pair):
        world, murat, davout = pair
        assert self._arm(world, murat, davout)["label"] == "Let it stand"

    def test_the_option_id_is_unchanged(self, pair):
        """The id is the POST value — renaming it would break every client
        and every stored answer."""
        world, murat, davout = pair
        assert self._arm(world, murat, davout)["id"] == "acknowledge"

    def test_the_price_is_stated_in_men(self, pair):
        world, murat, davout = pair
        murat.jealousy_turns_remaining = 4
        detail = self._arm(world, murat, davout)["detail"]
        assert f"{int(murat.strength):,}" in detail, detail
        assert "4 more turns" in detail

    def test_an_aggressive_marshal_withholds_everything(self, pair):
        world, murat, davout = pair
        assert murat.personality == "aggressive"
        assert "NONE" in self._arm(world, murat, davout)["detail"]

    def test_a_cautious_marshal_withholds_half(self, pair):
        world, murat, davout = pair
        murat.personality = "cautious"
        assert "half" in self._arm(world, murat, davout)["detail"]

    def test_the_two_arms_match_the_combat_rule(self, pair):
        """The figure quoted must be the rule the battle resolves on, not a
        second opinion. `_pair_contribution_scale` is that rule."""
        from backend.commands.executor import CommandExecutor
        world, murat, davout = pair
        ce = CommandExecutor()._combat
        murat.jealous_of = "Davout"
        assert ce._pair_contribution_scale(davout, murat) == 0.0
        assert "NONE" in self._arm(world, murat, davout)["detail"]
        murat.personality = "cautious"
        assert ce._pair_contribution_scale(davout, murat) == 0.50
        assert "half" in self._arm(world, murat, davout)["detail"]

    def test_it_is_still_free_and_still_does_nothing(self, pair):
        """§3 deliberately does NOT give it teeth. A fourth price on a card
        whose problem was that all prices bought the same outcome would make
        it worse; and deleting it would make Rebuke the only free arm and
        coerce a -5 trust hit at 0 AP."""
        world, murat, davout = pair
        arm = self._arm(world, murat, davout)
        assert arm["cost_note"] == "Free"
        assert "ap_cost" not in arm
        assert arm["enabled"] is True


class TestQ4TheMendArmsAreNoLongerInert:
    """Q4(a) (CA9 row 3 ruling). `force_reconciliation` charged 2 AP, rolled,
    printed "Under your eye they shake hands" and changed nothing any
    mechanic reads: `_restore` writes STORED while `get_relationship`
    subtracts 1 for a live grievance. A second inert paid arm, on top of the
    promise arm the audit found strictly dominated.

    The ruling also states the trapdoor is INTENDED and clamps the mend so a
    free 60%-chance arm cannot launder authored hostility into neutrality.
    """

    def _rivalry(self, new_value, stored=None, authority=100):
        murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                        strength=30000,
                                        personality="aggressive")
        davout = MarshalFactory.infantry(name="Davout", location="Paris",
                                         strength=30000,
                                         personality="cautious")
        world = WorldFactory.with_marshals([murat, davout])
        m, d = world.marshals["Murat"], world.marshals["Davout"]
        base = stored if stored is not None else new_value
        m.set_relationship("Davout", base)
        d.set_relationship("Murat", base)
        world.authority_tracker.authority = authority
        J.queue_rivalry_petition(world, m, d, new_value)
        return world, m, d

    def test_a_successful_mend_clears_the_live_grievance(self, monkeypatch):
        import random
        world, m, d = self._rivalry(-2)
        m.jealous_of = "Davout"
        monkeypatch.setattr(random, "random", lambda: 0.0)   # forced success
        J.handle_petition_response(world, "force_reconciliation")
        assert m.jealous_of is None, (
            "the handshake still moves nothing a mechanic reads")

    def test_a_failed_mend_leaves_it_alone(self, monkeypatch):
        """FALSIFIABLE NEGATIVE: the clear must be tied to SUCCESS, not to
        pressing the button."""
        import random
        world, m, d = self._rivalry(-2, authority=50)
        m.jealous_of = "Davout"
        monkeypatch.setattr(random, "random", lambda: 0.99)  # forced failure
        J.handle_petition_response(world, "force_reconciliation")
        assert m.jealous_of == "Davout"

    def test_the_derived_value_actually_moves_on_success(self, monkeypatch):
        import random
        world, m, d = self._rivalry(-2)
        m.jealous_of = "Davout"
        before = m.get_relationship("Davout")
        monkeypatch.setattr(random, "random", lambda: 0.0)
        J.handle_petition_response(world, "force_reconciliation")
        assert m.get_relationship("Davout") > before, (
            "stored moved but derived did not — the grievance is still on")

    def test_an_entrenched_pair_cannot_be_mended_above_rival(self, monkeypatch):
        """The clamp. A pair the game has called PERMANENT keeps its record;
        a handshake may stop the bleeding, not erase the wound."""
        import random
        world, m, d = self._rivalry(-1, stored=-2)
        J._set_escalation_level(m, "Davout", J.ESCALATION_PERMANENT_LEVEL)
        J._set_escalation_level(d, "Murat", J.ESCALATION_PERMANENT_LEVEL)
        monkeypatch.setattr(random, "random", lambda: 0.0)
        J.handle_petition_response(world, "mediate")
        assert m.relationships["Davout"] <= -1, (
            "a mend laundered an entrenched pair back to neutral")

    def test_a_non_entrenched_pair_still_mends_fully(self, monkeypatch):
        """FALSIFIABLE NEGATIVE for the clamp — otherwise it could be
        clamping everything and the test above would prove nothing."""
        import random
        world, m, d = self._rivalry(-1)
        monkeypatch.setattr(random, "random", lambda: 0.0)
        J.handle_petition_response(world, "mediate")
        assert m.relationships["Davout"] == 0


class TestTheHoldSerializes:
    def test_it_round_trips(self):
        m = MarshalFactory.infantry(name="Murat", personality="aggressive")
        m.jealousy_escalation_hold["Davout"] = 11
        back = Marshal.from_dict(m.to_dict())
        assert back.jealousy_escalation_hold == {"Davout": 11}

    def test_a_legacy_save_has_no_promise_outstanding(self):
        m = MarshalFactory.infantry(name="Murat")
        data = m.to_dict()
        data.pop("jealousy_escalation_hold", None)
        assert Marshal.from_dict(data).jealousy_escalation_hold == {}

    def test_the_hold_is_written_at_exactly_one_site(self):
        """Why M1–M7 and `BASELINE_SERIES` are byte-identical, as a pin
        rather than a hope.

        The hold is only ever WRITTEN by a player answering the §6 promise
        arm, and no harness answers a petition — so no enemy pair can ever
        carry one and the ambient escalation ladder is untouched. If a
        producer is ever added elsewhere (an AI arm, a scenario key), that
        stops being true and the harnesses must be re-measured.
        """
        import inspect
        src = inspect.getsource(J)
        writes = [ln.strip() for ln in src.split("\n")
                  if "jealousy_escalation_hold[" in ln and "=" in ln
                  and "==" not in ln]
        assert len(writes) == 2, writes   # the pair, both directions
        promise_src = inspect.getsource(J._apply_confrontation_choice)
        for ln in writes:
            assert ln in promise_src.replace("\n", "\n").strip() or \
                ln in "\n".join(l.strip() for l in promise_src.split("\n")), (
                f"the hold is written outside the player's promise arm: {ln}")

    def test_the_field_is_not_underscore_prefixed(self):
        """A10's lesson: `test_serialization_enforcement.py` filters `_`
        names out of the field set it derives, which is how four latches
        hid. A new field must not walk into that."""
        m = MarshalFactory.infantry(name="Murat")
        assert "jealousy_escalation_hold" in vars(m)
