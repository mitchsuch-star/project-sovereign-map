"""Row WO, slice 9 - "The Courting Cap" (WO-8) + WO-D9's damper.

Landing record: docs/WEIRD_OUTCOMES_SPEC.md section 3 slice 9.

Two things, and the second is not cosmetic.

(a) WO-8. Every throttle on enemy vassal courting was keyed per-COURTIER
    - the `court|{nation}|{vassal}` cooldown and the per-call `break` -
    and none per-TARGET. Measured on the BASELINE_SERIES board itself,
    with the real runner's `game_state` (an `end_turn()` without one
    skips the whole AI diplomatic phase, which is how a first probe of
    mine read zero events and nearly filed the defect as unreachable):

        turn 28: 19 courting events, every one against Switzerland,
                 loyalty 47 -> 42 -> ... -> 2 -> 0, then Denmark,
                 Bavaria, Saxony, Hanover, Hesse, PapalStates, Sardinia,
                 Holland, KingdomOfItaly and Switzerland each moving it
                 from 0 to 0 while still spending 2 DP and raising a
                 notification apiece,
        ending Switzerland-France: VASSAL -> WAR (vassal_rebellion).

    Two of those courtiers were France's OTHER satellites and the last
    was Switzerland courting itself - reachable because the three French
    client states are full roster nations, sitting in `enemy_nations`
    and in `world.vassals` at once.

    The spec's own account is wrong in two places and the landing record
    corrects both: the "-95 loyalty" is the NOMINAL sum of printed
    reductions, not a realized swing - the gate requires loyalty < 50 and
    the write floors at LOYALTY_MIN, so the true maximum is ~-49
    (measured -47), with ten of the nineteen courts costing the target
    nothing at all; and "bounded -5..-15" ignores the VS-R grip scale, so
    the real bound is -5..-22 (pinned at
    test_vassal_authority_coupling.py:310).

(b) WO-D9, ruled by the user August 22, 2026 at the recommended default:
    wire the existing `get_trust_gain_modifier`. The contract said "one
    call at the objection trust-pay seam". There is no such seam - six
    positive-gain sites across two handlers that never meet - and paying
    there would have left the objection dialog's own button quoting the
    undamped figure. It is applied at the QUOTE instead, which damps all
    six and keeps shown == applied.

Every test names the mutation that kills it.
"""

import contextlib
import io
import re
from pathlib import Path

from backend.game_logic import vassal as V
from backend.models import authority as AUTH
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
VASSAL_PY = REPO / "backend" / "game_logic" / "vassal.py"

_DOCSTRING_HEADS = ('"""', "'''", 'r"""')


def _read(path):
    return io.open(path, encoding="utf-8").read()


def _code_only(text: str) -> str:
    """`text` with comments and docstrings removed.

    Slice 9's own guards each carry a comment naming the rule they
    implement, so a bare substring scan would find the prose and pass
    with the code deleted - the INERT shape this row keeps re-finding.
    """
    import io as _io
    import tokenize
    out = []
    try:
        for tok in tokenize.generate_tokens(_io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                continue
            if (tok.type == tokenize.STRING
                    and tok.line.strip().startswith(_DOCSTRING_HEADS)):
                continue
            out.append(tok.string)
    except (tokenize.TokenError, IndentationError):
        return text
    return chr(10).join(out)


def _code_norm(text: str) -> str:
    """`_code_only` with all whitespace squeezed out.

    `_code_only` emits one token per line, so a multi-token needle never
    matches it - a trap of the same shape, since the pin reads as
    passing. Squeeze both sides and compare.
    """
    return re.sub(r"\s+", "", _code_only(text))


def _suppress():
    return contextlib.redirect_stdout(io.StringIO())


def _satellite(lord="France", loyalty=40):
    return {"lord": lord, "loyalty": loyalty, "autonomy": 0,
            "path": "scenario", "created_turn": 1, "tribute_rate": 0.5,
            "carved_from": None, "regions": None}


def _world(vassals=None, dp=10, turn=5):
    """A minimal world carrying a vassal web and DP for every courtier."""
    world = WorldState(player_nation="France")
    world.current_turn = turn
    world.vassals = dict(vassals or {"Switzerland": _satellite()})
    for nation in ("Britain", "Russia", "Austria", "Prussia", "Switzerland",
                   "Holland", "KingdomOfItaly", "Bavaria"):
        world.nation_dp[nation] = dp
    world.ai_proposal_cooldowns = {}
    return world


def _court(world, nation):
    with _suppress():
        return V.attempt_vassal_courting(world, nation)


# ══════════════════════════════════════════════════════════════════
# (a) The cap - one success per TARGET per turn, world-wide
# ══════════════════════════════════════════════════════════════════

class TestOneCourtPerTargetPerTurn:

    def test_the_second_courtier_of_the_same_vassal_wins_nothing(self):
        """Killed by: deleting the `courted_turn` skip."""
        world = _world()
        first = _court(world, "Britain")
        second = _court(world, "Russia")
        assert len(first) == 1, "the first courtier must still succeed"
        assert second == [], "the second must be turned away by the cap"

    def test_the_losing_courtier_spends_no_dp(self):
        """The contract's own clause: their DP is not spent.

        Killed by: moving the cap below the DP debit."""
        world = _world()
        _court(world, "Britain")
        before = world.nation_dp["Russia"]
        _court(world, "Russia")
        assert world.nation_dp["Russia"] == before, (
            "a courtier the cap turned away paid for the privilege")

    def test_the_losing_courtier_burns_no_cooldown(self):
        """It must be free to try again next turn.

        Killed by: moving the cap below the cooldown set."""
        world = _world()
        _court(world, "Britain")
        _court(world, "Russia")
        assert "court|Russia|Switzerland" not in world.ai_proposal_cooldowns

    def test_the_winner_is_the_first_courtier_in_nation_order(self):
        """Deterministic without a sort - the order is a list all the way
        down (EUROPE_ROSTER -> enemy_nations -> turn_manager's filtering
        comprehension).

        Killed by: any reordering that lets the later caller win."""
        world = _world()
        won = _court(world, "Britain")
        lost = _court(world, "Russia")
        assert won and not lost
        assert won[0]["nation"] == "Britain"

    def test_the_cap_lifts_on_the_next_turn(self):
        """Killed by: stamping a constant instead of the current turn."""
        world = _world()
        assert len(_court(world, "Britain")) == 1
        assert _court(world, "Russia") == []
        world.current_turn = int(world.current_turn) + 1
        assert len(_court(world, "Russia")) == 1, (
            "the cap is per TURN, not permanent")

    def test_a_second_vassal_is_still_courtable_in_the_same_turn(self):
        """The cap is per TARGET, not a global one-court-per-turn.

        Killed by: keying the stamp on the world instead of the row."""
        world = _world({"Switzerland": _satellite(),
                        "Naples": _satellite(loyalty=30)})
        first = _court(world, "Britain")
        second = _court(world, "Russia")
        assert len(first) == 1 and len(second) == 1
        assert first[0]["vassal"] != second[0]["vassal"]

    def test_the_pile_on_is_bounded_to_one(self):
        """The measured defect, reproduced in miniature: many courtiers,
        one target, one tick.

        Killed by: deleting the cap."""
        world = _world()
        courtiers = ["Britain", "Russia", "Austria", "Prussia", "Bavaria"]
        events = [e for n in courtiers for e in _court(world, n)]
        assert len(events) == 1, (
            "five courtiers produced %d events in one turn" % len(events))


class TestNoSelfCourtAndNoFellowSatellite:

    def test_a_nation_does_not_court_itself(self):
        """Switzerland courting Switzerland - observed live at
        server_console.log:11656.

        Killed by: deleting the `nation == vassal_name` guard."""
        world = _world()
        assert _court(world, "Switzerland") == []

    def test_the_self_court_costs_the_courtier_nothing(self):
        """Killed by: siting the self-court guard below the DP debit."""
        world = _world()
        before = world.nation_dp["Switzerland"]
        _court(world, "Switzerland")
        assert world.nation_dp["Switzerland"] == before

    def test_a_satellite_does_not_court_its_fellow_satellite(self):
        """Holland and KingdomOfItaly both courted Switzerland live
        (server_console.log:11654-11655).

        Killed by: deleting the lord-comparison guard."""
        world = _world({"Switzerland": _satellite(),
                        "Holland": _satellite(loyalty=90)})
        assert _court(world, "Holland") == []

    def test_a_foreign_court_may_still_court(self):
        """The negative control - the guards must not shut the mechanic
        off.

        Killed by: making the lord guard unconditional."""
        world = _world({"Switzerland": _satellite(),
                        "Holland": _satellite(loyalty=90)})
        assert len(_court(world, "Britain")) == 1

    def test_the_guard_compares_lords_not_the_player(self):
        """A vassal of a DIFFERENT lord is a legitimate courtier - the
        general comparison, not `== player`. A carved client
        (`formations.py` stamps the carver) or a defected satellite
        (VS-6 transfers one to the briber) has a non-player lord, so
        `== player` would be wrong the moment this loop widens.

        Killed by: rewriting the guard as `nation in world.vassals`."""
        world = _world({"Switzerland": _satellite(lord="France"),
                        "Bavaria": _satellite(lord="Austria", loyalty=90)})
        assert len(_court(world, "Bavaria")) == 1, (
            "Austria's satellite may court France's")


class TestTheCapIsSitedBelowTheOlderCooldown:

    def test_the_cap_does_not_shadow_the_per_courtier_cooldown(self):
        """Behavioural half: with the target un-stamped, the 3-turn
        per-courtier cooldown must still refuse on its own.

        Killed by: siting the cap above the cooldown read - which would
        also silently neuter test_session5_diplomacy's cooldown pin, as
        that calls the same nation twice in one turn and asserts zero
        events, an assertion the cap alone would satisfy."""
        world = _world()
        world.ai_proposal_cooldowns["court|Britain|Switzerland"] = 3
        assert _court(world, "Britain") == []
        # the target was never stamped, so a different court still wins
        assert len(_court(world, "Russia")) == 1

    def test_the_cap_block_follows_the_cooldown_read_in_source(self):
        """Structural half, comment-blind."""
        code = _code_norm(_read(VASSAL_PY))
        cooldown = code.index("ifcooldown>0")
        cap = code.index('ifstate.get("courted_turn")==int(world.current_turn)')
        debit = code.index("dp_nations[nation]=dp_nations.get(nation,0)-2")
        assert cooldown < cap < debit, (
            "the cap must sit below the cooldown read and above the DP debit")


class TestTheStampRidesTheVassalRow:

    def test_courted_turn_survives_a_save_load_round_trip(self):
        """Zero new serialized fields - the row carries it, the VS-3
        `grant_cooldown` precedent.

        Killed by: storing the stamp on the world instead of the row."""
        world = _world()
        _court(world, "Britain")
        assert world.vassals["Switzerland"]["courted_turn"] == (
            world.current_turn)
        restored = WorldState.from_dict(world.to_dict())
        assert restored.vassals["Switzerland"]["courted_turn"] == (
            world.current_turn), "the stamp did not round-trip"

    def test_the_cap_holds_across_the_round_trip(self):
        """Killed by: dropping the stamp from to_dict/from_dict."""
        world = _world()
        _court(world, "Britain")
        restored = WorldState.from_dict(world.to_dict())
        restored.nation_dp["Russia"] = 10
        assert _court(restored, "Russia") == []


class TestTheFlipLever:

    def test_the_lever_is_true_at_rest(self):
        assert V.COURTING_TARGET_CAP_ACTIVE is True

    def test_false_reproduces_the_pile_on(self, monkeypatch):
        """The BASELINE_SERIES attribution arm, as a behaviour test: with
        the lever down, five courtiers strip one satellite in a single
        tick and the self-court returns."""
        monkeypatch.setattr(V, "COURTING_TARGET_CAP_ACTIVE", False)
        world = _world()
        courtiers = ["Britain", "Russia", "Austria", "Prussia", "Switzerland"]
        events = [e for n in courtiers for e in _court(world, n)]
        assert len(events) == 5, "the lever did not restore prior behaviour"
        assert any(e["nation"] == e["vassal"] for e in events), (
            "the self-court is part of the prior behaviour")


# ══════════════════════════════════════════════════════════════════
# (b) WO-D9 - the anti-pushover damper, at the quote
# ══════════════════════════════════════════════════════════════════

PUSHOVER = ["trust"] * 5
BALANCED = ["trust", "trust", "insist", "insist", "compromise"]


def _answers(world, choices):
    world.authority_tracker.recent_responses = [
        {"choice": c, "turn": i} for i, c in enumerate(choices)
    ]


class TestTheDamperIsWired:

    def test_a_pushover_is_paid_less_than_a_balanced_player(self):
        """THE RULED BEHAVIOUR TEST (DESIGN_REFINEMENT section WO-D9): a
        pushover player's objection trust gain is strictly less than a
        balanced player's for the same press.

        This pins the RULE, at the helper. It does NOT pin the wiring —
        reverting either quote site leaves it green, as a review caught
        when the first draft of this docstring claimed otherwise. The
        wiring is pinned end-to-end by TestTheDamperOnTheRealPath."""
        pushover, balanced = _world(), _world()
        _answers(pushover, PUSHOVER)
        _answers(balanced, BALANCED)
        assert (AUTH.damp_objection_trust_gain(pushover, 8)
                < AUTH.damp_objection_trust_gain(balanced, 8))

    def test_the_ruled_thresholds_are_the_ones_applied(self):
        """Trust-ratio > 0.80 -> x0.5, > 0.60 -> x0.75, else x1.0 - the
        ruling's own numbers, unchanged.

        Killed by: any retune of the modifier."""
        severe, moderate, clean = _world(), _world(), _world()
        _answers(severe, ["trust"] * 10)
        _answers(moderate, ["trust"] * 7 + ["insist"] * 3)
        _answers(clean, ["insist"] * 10)
        assert AUTH.damp_objection_trust_gain(severe, 8) == 4
        assert AUTH.damp_objection_trust_gain(moderate, 8) == 6
        assert AUTH.damp_objection_trust_gain(clean, 8) == 8

    def test_under_five_recorded_answers_nothing_is_damped(self):
        """The guard the ruling names.

        Killed by: dropping the `< 5` early return."""
        world = _world()
        _answers(world, ["trust"] * 4)
        assert AUTH.damp_objection_trust_gain(world, 8) == 8

    def test_an_insist_penalty_is_never_softened(self):
        """Gains only.

        Killed by: removing the `<= 0` guard."""
        world = _world()
        _answers(world, PUSHOVER)
        assert AUTH.damp_objection_trust_gain(world, -12) == -12

    def test_a_world_without_a_tracker_does_not_crash(self):
        """Legacy worlds and hand-rolled doubles.

        Killed by: reading the tracker without the defensive probe."""
        class Bare:
            pass
        assert AUTH.damp_objection_trust_gain(Bare(), 8) == 8

    def test_the_lever_is_true_at_rest(self):
        assert AUTH.OBJECTION_TRUST_DAMPER_ACTIVE is True

    def test_false_is_a_no_op(self, monkeypatch):
        monkeypatch.setattr(AUTH, "OBJECTION_TRUST_DAMPER_ACTIVE", False)
        world = _world()
        _answers(world, PUSHOVER)
        assert AUTH.damp_objection_trust_gain(world, 8) == 8


class TestShownEqualsApplied:

    def test_both_quote_sites_route_through_the_damper(self):
        """The contract said ONE call at the pay seam. There are six pay
        sites across two handlers that never meet, and all six read the
        figure back off the objection dict - so the damper belongs at the
        two places the figure is MINTED.

        Killed by: reverting either site."""
        for path in ("backend/commands/executor.py",
                     "backend/commands/strategic_executor.py"):
            code = _code_norm(_read(REPO / path))
            assert "damp_objection_trust_gain(" in code, path
            assert "trust_gain=calculate_trust_gain(" not in code, (
                "%s still mints an undamped trust gain" % path)

    def test_the_strategic_option_label_mirrors_the_dict(self):
        """The three v1_options producers each mint the trust arm's label
        from an undamped table read, while the handler pays
        `objection['trust_gain']`.

        Killed by: deleting the normalisation loop."""
        code = _code_norm(_read(REPO / "backend" / "commands"
                                / "strategic_executor.py"))
        assert '_opt.get("type")=="preferred"' in code
        assert '_opt["trust_change"]=trust_gain' in code

    def test_the_damper_is_not_applied_to_battle_or_estate_trust(self):
        """Scope: the ruling covers the objection channel only. The
        battle award has its own, older application in `vindication.py`
        and must not be double-damped.

        Honest about what this proves: only that no FOURTH file calls the
        helper. It would still pass if the helper were applied to a
        battle award inside `executor.py` itself. The stronger guarantee
        is structural — both call sites assign only the local
        `trust_gain`, which nothing but the objection dict reads."""
        callers = []
        for path in REPO.joinpath("backend").rglob("*.py"):
            if "damp_objection_trust_gain(" in _code_norm(_read(path)):
                callers.append(path.name)
        assert sorted(callers) == ["authority.py", "executor.py",
                                   "strategic_executor.py"], callers


class TestTheDamperOnTheRealPath:
    """End-to-end coverage the first draft of this file did not have.

    A review found BOTH wiring pins were source-text greps, and that a
    mutation preserving the substring while breaking reachability would
    survive the whole sweep — which is exactly what happened to the
    `v1_options` normalisation, whose lever guard was missing and which
    no test could see. These drive the real executor.
    """

    @staticmethod
    def _raise_objection(answers):
        """Davout (cautious, TRUSTING) attacks Blucher at 2.4:1 against —
        the standing V2a integration fixture — and objects for real."""
        from unittest.mock import patch
        from backend.commands.executor import CommandExecutor
        from tests.test_objection_v2 import TestV2aIntegrationFixtures

        world = TestV2aIntegrationFixtures.make_integration_world()
        world.marshals["Davout"].location = "Rhineland"
        if answers:
            _answers(world, answers)
        executor = CommandExecutor()
        command = {"command": {"marshal": "Davout", "action": "attack",
                               "target": "Blucher"}}
        with patch("backend.commands.objection_v2.random.random",
                   return_value=0.5), _suppress():
            result = executor.execute(command, {"world": world})
        return world, result.get("objection")

    def test_a_raised_objection_quotes_a_damped_figure(self):
        """Killed by: reverting the tactical quote site (which the
        source-grep pin catches too) AND by any change that makes the
        damper unreachable from it (which only this catches)."""
        _, clean = self._raise_objection([])
        _, pushover = self._raise_objection(PUSHOVER)
        assert clean is not None and pushover is not None
        assert pushover["trust_gain"] < clean["trust_gain"], (
            "the raised objection quoted an undamped figure")

    def test_the_damped_quote_is_exactly_what_is_paid(self):
        """shown == applied, on the real path: the button's number and
        the marshal's trust delta are the same integer.

        Killed by: damping at the payment instead of the quote."""
        world, objection = self._raise_objection(PUSHOVER)
        davout = world.marshals["Davout"]
        before = davout.trust.value
        with _suppress():
            world.disobedience_system.handle_response(
                world.pending_objection, "trust", world)
        assert davout.trust.value - before == objection["trust_gain"]

    def test_the_lever_down_restores_the_undamped_quote(self):
        """The attribution arm, behaviourally: with the lever down a
        pushover is quoted exactly what a clean player is.

        Killed by: freezing the flag at import time (a module-level
        `from ... import OBJECTION_TRUST_DAMPER_ACTIVE` would do it) —
        which no source-text pin can see."""
        import pytest
        _, clean = self._raise_objection([])
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(AUTH, "OBJECTION_TRUST_DAMPER_ACTIVE", False)
            _, pushover = self._raise_objection(PUSHOVER)
        assert pushover["trust_gain"] == clean["trust_gain"]

    def test_the_normalisation_loop_sits_behind_the_lever(self):
        """The review's headline: the loop was OUTSIDE the flip lever, so
        with the lever down the strategic Trust button read +6/+9 where
        it had read +3 — the lever's own comment promises byte-identical
        pre-slice behaviour, and it was not.

        Killed by: hoisting the loop back out of the `if _DAMPER_ACTIVE`
        block."""
        code = _code_norm(_read(REPO / "backend" / "commands"
                                / "strategic_executor.py"))
        guarded = ('if_DAMPER_ACTIVE:for_optinv1_options:'
                   'if_opt.get("type")=="preferred":'
                   '_opt["trust_change"]=trust_gain')
        assert guarded in code, "the normalisation loop escaped its lever"


class TestTheCapRedistributesRatherThanReduces:
    """Measured consequence, recorded rather than fixed.

    A blocked courtier `continue`s to the next eligible satellite, so with
    several satellites under the gate the cap SPREADS courting instead of
    suppressing it — and because the uncapped pile-on wasted most of its
    courts against `LOYALTY_MIN`, empire-wide realized loss can go UP.
    Pinned so the property is visible; the one-vassal fixture the rest of
    this file uses cannot see it.
    """

    ROSTER = ["Britain", "Russia", "Austria", "Prussia", "Spain", "Ottoman",
              "Sweden", "Naples", "Portugal", "Denmark"]

    def _board(self, n):
        world = WorldState(player_nation="France")
        world.current_turn = 5
        world.vassals = {f"Sat{i}": _satellite(loyalty=47) for i in range(n)}
        for nation in self.ROSTER:
            world.nation_dp[nation] = 10
        world.ai_proposal_cooldowns = {}
        return world

    def _sweep(self, world):
        return [e for n in self.ROSTER for e in _court(world, n)]

    def test_one_court_per_satellite_not_one_court_in_total(self):
        """Ten courtiers, ten eligible satellites: ten courts, each on a
        different target, each satellite hit exactly once.

        Killed by: turning the cap's `continue` into a `break`."""
        world = self._board(10)
        events = self._sweep(world)
        assert len(events) == 10
        assert len({e["vassal"] for e in events}) == 10
        assert all(v["loyalty"] == 42 for v in world.vassals.values())

    def test_a_blocked_courtier_still_pays_for_the_target_it_does_reach(self):
        """Corrects this slice's own commit message: "the losers spend
        nothing" holds only when there is no OTHER eligible target. With
        ten satellites, ten courtiers each spend their 2 DP — on someone
        else.

        Killed by: making the cap `break` out of the candidate loop."""
        world = self._board(10)
        before = {n: world.nation_dp[n] for n in self.ROSTER}
        self._sweep(world)
        spent = [n for n in self.ROSTER if world.nation_dp[n] < before[n]]
        assert len(spent) == 10, (
            "a courtier redirected by the cap did not court anyone")

    def test_with_a_single_target_the_losers_truly_spend_nothing(self):
        """The claim as originally written, and the case it is true in.

        Killed by: moving the cap below the DP debit."""
        world = self._board(1)
        before = {n: world.nation_dp[n] for n in self.ROSTER}
        self._sweep(world)
        spent = [n for n in self.ROSTER if world.nation_dp[n] < before[n]]
        assert spent == ["Britain"]
