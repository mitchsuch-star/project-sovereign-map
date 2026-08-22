"""Row WO, slice 16 — "The Objection Channel Pays Honestly" (August 21, 2026).

The strategic-objection channel credited trust for presses that executed
nothing, answered them with raw internal error text, charged the wrong AP,
and refreshed its own budget on every save/load:

  WO-21 (P1) the trust arm paid for nothing and the SUPPORT arm was dead;
  WO-23 (P2) `load_game` wiped `objection_popups_this_turn` while
        `from_dict` restored it — a mid-turn save/load refreshed the ONLY
        limiter on the channel;
  WO-37 (new) the trust arm charged 1 AP twice.

Landing record: docs/WEIRD_OUTCOMES_SPEC.md §3 slice 16.

Measured on the shipped tree before the fix, by hand, end to end:

    2-option objection, "trust"       +8 trust, 0 AP, "Unknown action: None"
    2-option objection, "compromise"  +3 trust, 0 AP, "No compromise available"
    SUPPORT-relationship, "trust"     +8 trust, 0 AP, "Unknown action: cancel"
    trust -> preferred `drill`        2 AP against a button quoting 1

The ROOT is not the credit order the row names. `preferred_action` was
lifted by INDEX (`options[1]`) out of a list whose middle entry is optional,
while the Godot client reads the same list by TYPE. A marshal who proposes
no alternative produced `[proceed, compromise]`, so the backend handed the
compromise dict to the trust arm. Two implementations of one rule, only one
maintained — the CA9 through-line.

Every test names the mutation that kills it.
"""

import contextlib
import io
import re
from pathlib import Path

import pytest

from backend.commands.disobedience import _build_strategic_options
from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
STRATEGIC_EXECUTOR = REPO / "backend" / "commands" / "strategic_executor.py"
META_EXECUTOR = REPO / "backend" / "commands" / "meta_executor.py"
DISOBEDIENCE = REPO / "backend" / "commands" / "disobedience.py"


def _suppress():
    return contextlib.redirect_stdout(io.StringIO())


def _world():
    world = WorldState(player_nation="France")
    world.actions_remaining = 4
    world.admin_actions_remaining = 2
    return world


def _objection(options, marshal="Davout", strategic_type="SUPPORT",
               target="Ney", trust_gain=8):
    return {
        "marshal_name": marshal,
        "original_command": {"marshal": marshal, "action": "support",
                             "target": target},
        "parsed_command": {"command": {"marshal": marshal,
                                       "action": "support", "target": target}},
        "strategic_type": strategic_type,
        "path": [],
        "target": target,
        "options": options,
        "trust_gain": trust_gain,
        "insist_penalty": -10,
    }


PROCEED = {"type": "proceed", "text": "Proceed", "trust_change": -10,
           "ap_cost": 2}
COMPROMISE = {"type": "compromise", "text": "Timed SUPPORT (3 turns)",
              "trust_change": 3, "ap_cost": 2,
              "compromise": {"max_turns": 3}}
CANCEL_PREFERRED = {"type": "preferred",
                    "text": "Trust: Do not issue the SUPPORT order",
                    "action": "cancel", "target": "Ney",
                    "trust_change": 8, "ap_cost": 1}


def _answer(world, choice, options, marshal="Davout", **kw):
    ex = CommandExecutor()
    world.pending_strategic_objection = _objection(options, marshal=marshal,
                                                   **kw)
    with _suppress():
        return ex._strategic._handle_strategic_objection_from_endpoint(
            choice, {"world": world})


# ═══════════════════════════════════════════════════════════════════
# WO-21 — the root: options are lifted by TYPE, as the client reads them
# ═══════════════════════════════════════════════════════════════════


class TestWO21TheOptionsAreLiftedByType:

    def test_a_marshal_with_no_alternative_builds_a_two_option_list(self):
        """The premise, pinned as arithmetic so the rest is not built on an
        assumption: `_build_strategic_options` appends the preferred entry
        only when there IS one, so `options[1]` is the COMPROMISE dict.

        Mutation: make the preferred append unconditional — the list is
        3 long, `options[1]` is preferred again, and this reds."""
        world = _world()
        davout = world.get_marshal("Davout")
        options = _build_strategic_options(
            davout, None, {"action": "support", "max_turns": 3},
            "Proceed with SUPPORT", "Accept: Timed SUPPORT (3 turns)",
            "SUPPORT")
        assert [o["type"] for o in options] == ["proceed", "compromise"]
        assert options[1].get("action") is None, (
            "the positional lift would hand THIS dict to the trust arm")

    def test_trust_with_no_alternative_declines_the_order(self):
        """Was: +8 trust, 0 AP, "Unknown action: None". Trusting a marshal
        who proposed nothing means the order is not issued — the only
        coherent reading of a button the client renders unconditionally.

        Mutation: restore the positional lift at
        `_handle_strategic_objection_from_endpoint` (`options[1]`)."""
        world = _world()
        davout = world.get_marshal("Davout")
        before = davout.trust.value
        result = _answer(world, "trust", [PROCEED, COMPROMISE])
        assert result["success"] is True
        assert "Unknown action" not in result["message"]
        assert "not issued" in result["message"]
        assert davout.trust.value == before + 8
        assert world.actions_remaining == 3
        assert davout.strategic_order is None

    def test_compromise_on_a_two_option_objection_is_honoured(self):
        """Was: +3 trust, 0 AP, "No compromise available" — for a button the
        client rendered from a REAL compromise payload, because `options[2]`
        did not exist. Same mutation as above."""
        world = _world()
        davout = world.get_marshal("Davout")
        before = davout.trust.value
        result = _answer(world, "compromise", [PROCEED, COMPROMISE])
        assert result["success"] is True
        assert "No compromise available" not in result["message"]
        assert davout.trust.value == before + 3
        assert davout.strategic_order is not None

    def test_the_relationship_support_arm_declines_instead_of_erroring(self):
        """WO-21(b). Was: +8 trust, 0 AP, "Unknown action: cancel".

        NOT routed through `_execute_cancel`: the objection returns before
        the StrategicOrder is built, so there is nothing to cancel and a
        real cancel would either no-op or cancel an UNRELATED standing order
        and charge its own -3 trust.

        Mutation: delete the `pref_action == "cancel"` arm — the dispatch
        has no `cancel` handler and the raw error returns."""
        world = _world()
        davout = world.get_marshal("Davout")
        before = davout.trust.value
        result = _answer(world, "trust",
                         [PROCEED, CANCEL_PREFERRED, COMPROMISE])
        assert result["success"] is True
        assert "Unknown action" not in result["message"]
        assert "not issued" in result["message"]
        assert davout.trust.value == before + 8
        assert world.actions_remaining == 3
        assert davout.strategic_order is None

    def test_the_button_no_longer_says_cancel(self):
        """shown = applied: it declines to issue, so it must not promise a
        cancel. Mutation: restore "Trust: Cancel the SUPPORT order"."""
        src = STRATEGIC_EXECUTOR.read_text(encoding="utf-8")
        assert '"text": "Trust: Do not issue the SUPPORT order"' in src
        assert "Trust: Cancel the SUPPORT order" not in src


# ═══════════════════════════════════════════════════════════════════
# WO-21 — credit only what executes
# ═══════════════════════════════════════════════════════════════════


class TestWO21CreditOnlyWhatExecutes:

    def test_a_preferred_action_that_fails_credits_nothing(self):
        """The law the row states. A preferred `recruit` with the admin pool
        empty is refused by the dispatch — and used to bank the trust on the
        way in.

        Mutation: move `modify_trust(v2_trust_gain)` back above the
        dispatch."""
        world = _world()
        world.admin_actions_remaining = 0
        davout = world.get_marshal("Davout")
        before = davout.trust.value
        result = _answer(world, "trust", [
            PROCEED,
            {"type": "preferred", "text": "Trust: raise fresh troops",
             "action": "recruit", "target": None, "trust_change": 8,
             "ap_cost": 1},
            COMPROMISE])
        assert result["success"] is False
        assert davout.trust.value == before, (
            "trust was banked for an action the dispatch refused")

    def test_a_compromise_with_no_safe_path_credits_nothing(self):
        """The THIRD reachable credit-for-nothing, which the filed row never
        named: "No safe path available" sits below the compromise credit.

        Mutation: move `modify_trust(v2_compromise_gain)` back to the top of
        the compromise arm."""
        world = _world()
        davout = world.get_marshal("Davout")
        before = davout.trust.value
        world.find_weighted_path = lambda *a, **k: None
        world.find_path = lambda *a, **k: None
        result = _answer(world, "compromise", [
            PROCEED,
            {"type": "compromise", "text": "Compromise: safe road",
             "trust_change": 3, "ap_cost": 2,
             "compromise": {"safe_path": True}}],
            strategic_type="MOVE_TO", target="Lyon")
        assert result["success"] is False
        assert "No safe path" in result["message"]
        assert davout.trust.value == before

    def test_an_impossible_choice_is_refused_and_the_question_survives(self):
        """The strategic route had NO choice validation at all — it returns
        before the tactical route's `valid_choices` guard, which already
        refuses an impossible answer in Berthier's voice. The refusal must
        run BEFORE the objection is cleared, or it strands the player with
        no valid arm left to press.

        Mutation: delete the guard, or move it below
        `world.pending_strategic_objection = None`."""
        world = _world()
        davout = world.get_marshal("Davout")
        before = davout.trust.value
        result = _answer(world, "compromise", [PROCEED, CANCEL_PREFERRED])
        assert result["success"] is False
        assert "not one of the roads open" in result["message"]
        assert davout.trust.value == before
        assert world.pending_strategic_objection is not None, (
            "the refusal cleared the question the player still has to answer")
        assert "trust" in result["choices"] and "insist" in result["choices"]
        assert "compromise" not in result["choices"]


# ═══════════════════════════════════════════════════════════════════
# WO-37 — the trust arm charges once, at the price it quoted
# ═══════════════════════════════════════════════════════════════════


class TestWO37TheApIsChargedOnce:

    def test_the_trust_arm_charges_one_ap(self):
        """Measured before the fix: 2 AP for a preferred `drill` against a
        button quoting 1 (and 3 for a `fortify` that auto-shifts stance),
        while `action_info` reported 1.

        Mutation: drop `charge_ap=False` at the dispatch call."""
        world = _world()
        result = _answer(world, "trust", [
            PROCEED,
            {"type": "preferred", "text": "Trust: Davout drills troops",
             "action": "drill", "target": None, "trust_change": 8,
             "ap_cost": 1},
            COMPROMISE])
        assert result["success"] is True
        assert world.actions_remaining == 3, "one AP, once"

    def test_action_info_reports_what_was_charged(self):
        """The other half of the same lie: the endpoint stamped `cost: 1`
        over a charge of 2. Mutation: as above."""
        world = _world()
        result = _answer(world, "trust", [
            PROCEED,
            {"type": "preferred", "text": "Trust: Davout drills troops",
             "action": "drill", "target": None, "trust_change": 8,
             "ap_cost": 1},
            COMPROMISE])
        info = result.get("action_info") or {}
        assert info.get("cost") == 1
        assert info.get("remaining") == world.actions_remaining

    def test_the_dead_ap_guard_is_gone(self):
        """`_ap_consumed_by_execute` was read once and set NOWHERE — a guard
        that looked live and was not. It is replaced by an explicit
        parameter.

        Pinned on the two USAGE forms rather than the bare name: the name
        survives deliberately in the prose that records why the flag went,
        and a pin that could not tell code from explanation would have to
        choose between being wrong and forbidding the explanation.

        Mutation: reintroduce either a read or a write of the flag.
        """
        for path in (STRATEGIC_EXECUTOR, META_EXECUTOR):
            text = path.read_text(encoding="utf-8")
            for form in ('get("_ap_consumed_by_execute"',
                         '["_ap_consumed_by_execute"]'):
                assert form not in text, (
                    f"{path.name} still uses the dead flag: {form}")

    def test_the_tactical_objection_route_still_charges_itself(self):
        """FALSIFIABLE NEGATIVE — `charge_ap` defaults True, so the two
        tactical callers are untouched. Mutation: flip the default to
        False and every tactical objection answer becomes free."""
        import inspect

        from backend.commands.meta_executor import MetaExecutor

        sig = inspect.signature(MetaExecutor._execute_post_objection)
        assert sig.parameters["charge_ap"].default is True
        src = META_EXECUTOR.read_text(encoding="utf-8")
        # the two tactical CALL sites (not the def) pass no override
        calls = re.findall(r"self\._execute_post_objection\((.*?)\)",
                           src, re.S)
        assert len(calls) >= 2, (
            f"the call-site parse found {len(calls)} calls — it has drifted "
            f"off the code it is watching")
        assert not any("charge_ap" in c for c in calls), (
            "a tactical caller started suppressing its own AP charge")


# ═══════════════════════════════════════════════════════════════════
# WO-23 — the budget survives the save it is written into
# ═══════════════════════════════════════════════════════════════════


class TestWO23TheBudgetSurvivesALoad:

    def _save_load(self, world, tmp_path):
        from backend.save_manager import load_game, save_game

        path = tmp_path / "wo23.json"
        save_game(world, save_name="wo23", filepath=path)
        result = load_game(path)
        assert result["success"], result["message"]
        return result["world"]

    def test_the_budget_survives(self, tmp_path):
        """`from_dict` restored it and `load_game` immediately discarded it,
        so a mid-turn save/load refreshed every marshal's budget — the ONLY
        live limiter on the objection trust channel.

        Mutation: restore `world.objection_popups_this_turn = set()` in
        `load_game`."""
        world = _world()
        world.objection_popups_this_turn = {"Ney", "Davout"}
        loaded = self._save_load(world, tmp_path)
        assert loaded.objection_popups_this_turn == {"Ney", "Davout"}

    def test_a_restored_budget_is_still_HONOURED(self, tmp_path):
        """Presence is not enough — the readers must still consult it after
        a load. Both objection sites downgrade to a MILD line when the name
        is already in the set.

        Mutation: as above; or make either reader stop consulting it."""
        world = _world()
        world.objection_popups_this_turn = {"Davout"}
        loaded = self._save_load(world, tmp_path)
        src_tac = (REPO / "backend" / "commands"
                   / "executor.py").read_text(encoding="utf-8")
        src_str = STRATEGIC_EXECUTOR.read_text(encoding="utf-8")
        assert "in world.objection_popups_this_turn" in src_tac
        assert "in world.objection_popups_this_turn" in src_str
        assert "Davout" in loaded.objection_popups_this_turn

    def test_the_budget_still_clears_at_the_real_turn_boundary(self):
        """FALSIFIABLE NEGATIVE — this is a per-TURN budget, and the turn
        boundary is where it is supposed to reset. Mutation: delete the
        clear in `_advance_turn_internal` and the budget becomes permanent,
        silencing every objection after the first."""
        world = _world()
        world.objection_popups_this_turn = {"Ney", "Davout"}
        with _suppress():
            world.advance_turn()
        assert world.objection_popups_this_turn == set()

    def test_the_load_side_wipe_names_its_three_exemptions(self):
        """The comment block is the record of a deliberate decision made
        three times for the same reason. Mutation: delete the WO-23
        paragraph and a later reader re-adds the wipe."""
        src = (REPO / "backend" / "save_manager.py").read_text(
            encoding="utf-8")
        block = src[src.index("Clear transient per-turn data"):]
        block = block[:block.index("threat_sources_this_turn")]
        assert "objection_popups_this_turn = set()" not in block
        for name in ("diplomatic_trust_applied", "attacks_this_turn",
                     "objection_popups_this_turn"):
            assert name in block, f"{name} is not named as an exemption"


# ═══════════════════════════════════════════════════════════════════
# The census — every objection option can be answered
# ═══════════════════════════════════════════════════════════════════


class TestTheDispatchCoversEveryOption:

    @staticmethod
    def _dispatch_arms():
        src = META_EXECUTOR.read_text(encoding="utf-8")
        body = src[src.index("def _execute_post_objection"):]
        body = body[:body.index('f"Unknown action: {action}"')]
        return set(re.findall(r'action == "([a-z_]+)"', body))

    def test_the_dispatch_table_parses(self):
        """The pin below is only worth anything if this parse is real.
        Mutation: rename the dispatch variable and this reds rather than
        silently passing on an empty set."""
        arms = self._dispatch_arms()
        assert len(arms) >= 15, arms
        assert {"attack", "drill", "fortify", "stance_change"} <= arms

    def test_every_preferred_option_action_can_be_answered(self):
        """CENSUS — an objection option whose action the dispatch cannot
        route is a button that pays trust and returns raw internal text.
        That was WO-21(b), and the only reason it was ever findable is that
        somebody played it.

        Every action a `"type": "preferred"` option can carry must be
        dispatchable, carry a `strategic_type`, or be one of the two the
        response handler resolves itself.

        Mutation: add `{"type": "preferred", ..., "action": "sortie"}` to
        either producer — the inline scan finds it and this reds naming it.
        """
        HANDLED_BY_THE_RESPONSE_ARM = {
            # WO-21: resolved as "decline to issue", not dispatched.
            "cancel",
        }
        CARRIES_A_STRATEGIC_TYPE = {
            # `_get_aggressive_preferred` stamps strategic_type=PURSUE, so
            # this routes through `_execute_strategic_command` instead.
            "pursue",
        }
        # (a) the indirect producers — `_build_strategic_options` copies
        #     `preferred["action"]` from the eight V1 sites and from
        #     `_get_aggressive_preferred`. Declared with provenance.
        DECLARED = {"attack", "pursue", "stance_change", "drill", "fortify",
                    "scout"}
        # (b) the drift arm — any INLINE preferred option, parsed.
        inline = set()
        found_inline_options = 0
        for path in (STRATEGIC_EXECUTOR, DISOBEDIENCE):
            src = path.read_text(encoding="utf-8")
            for m in re.finditer(r'"type":\s*"preferred"', src):
                found_inline_options += 1
                # Bound the window at the NEXT option dict, not a fixed
                # char count — a fixed count is how the NA-6 dead-name pin
                # went inert in July 2026, and how the first draft of THIS
                # pin did: a comment added inside the option pushed its
                # `"action"` past 500 characters and the mutation survived.
                rest = src[m.end():]
                nxt = re.search(r'"type":\s*"', rest)
                window = rest[:nxt.start()] if nxt else rest[:1500]
                assert len(window) < 2000, (
                    "the option-window bound found no following option — "
                    "the scan is no longer reading one dict at a time")
                inline |= set(re.findall(r'"action":\s*"([a-z_]+)"', window))
        assert found_inline_options >= 1, (
            "the inline-option scan found no preferred options at all — it "
            "has drifted off the code it is supposed to be watching")

        arms = self._dispatch_arms()
        unanswerable = sorted(
            (DECLARED | inline)
            - arms - CARRIES_A_STRATEGIC_TYPE - HANDLED_BY_THE_RESPONSE_ARM)
        assert not unanswerable, (
            "these preferred-option actions have no way to be answered: "
            + ", ".join(unanswerable))


# ═══════════════════════════════════════════════════════════════════
# The two halves are one exploit
# ═══════════════════════════════════════════════════════════════════


def test_the_budget_is_what_rate_limits_the_trust_channel():
    """WO-21 and WO-23 are the same exploit seen from two ends: the trust
    channel's only limiter is one popup per marshal per turn, and WO-23's
    save/load wipe refreshed it. Pinned together so a later slice cannot
    remove one and leave the other looking harmless.

    Mutation: delete either reader's membership check.
    """
    src_tac = (REPO / "backend" / "commands"
               / "executor.py").read_text(encoding="utf-8")
    src_str = STRATEGIC_EXECUTOR.read_text(encoding="utf-8")
    assert src_tac.count("objection_popups_this_turn") >= 2
    assert src_str.count("objection_popups_this_turn") >= 2
    world = _world()
    assert world.objection_popups_this_turn == set()
