"""The counter-punch is usable at 0 AP — Aug 23, 2026.

User report (live turn-3 France/1805 campaign): *"the Bernadotte free attack
didn't work"*. Bernadotte is `cautious`, so a won defence grants him the
Phase-2.8 counter-punch and a notification reading

    "<name> earned a free attack from their defensive victory.
     Use it THIS turn or the opportunity expires."

The measured state at the moment of the report was `actions_remaining: 0`.

THE DEFECT, in one sentence: the waiver that makes the attack free lived
inside `combat_executor._execute_attack`, ~200 lines downstream of the two AP
pre-gates in `executor.execute` that stopped the command ever reaching it.

  * `executor.py` gate 1 (early, pre-objection) — `actions_remaining <
    required_actions` -> "Not enough actions! Need 1, have 0."
  * `executor.py` gate 2 (AP PRE-CHECK, before the objection battery) — same.
  * Only AFTER a successful execution did `free_action` waive the charge.

So the free attack worked silently while the player still had AP (where being
free changes nothing) and was impossible once the AP was spent (the only state
in which "free" means anything). No test caught it because no test spent the
AP first.

It also broke GR5: `is_player_action_check` is False for an enemy marshal, so
both gates are skipped for the AI and its counter-punch always worked.

THE SECOND HALF: `_execute_attack` clears `counter_punch_available` at its head
and only then runs the drill-lock / artillery-moved / range refusals, so a
REFUSED attack silently burned the free strike. The counter-punch is an
action-economy resource and now obeys the same rule AP does — spent only on
success.

Fixes: `Marshal.has_counter_punch()` is the one predicate (GR1), consulted by
the consumption site and by both pre-gates via `counter_punch_waiver`; the
executor snapshots and restores the flag when the command fails.
"""

import os
import re

import pytest

from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_NOT_ENOUGH = re.compile(r"not enough action", re.I)


def _world_with_cautious_attacker(ap=0, counter_punch=True):
    """Davout (cautious) at Belgium, adjacent to Wellington at Waterloo.

    France boots at WAR with Britain in the legacy fixture world, so the
    attack is legal and only the action economy is under test.
    """
    world = WorldState()
    davout = world.marshals["Davout"]
    assert davout.personality == "cautious", "fixture roster changed"
    davout.location = "Belgium"
    davout.counter_punch_available = bool(counter_punch)
    davout.counter_punch_turns = 2 if counter_punch else 0
    world.actions_remaining = ap
    return world, davout


def _attack(world, marshal_name="Davout", target="Wellington"):
    executor = CommandExecutor()
    game_state = {"world": world}
    command = {"command": {
        "action": "attack", "type": "specific",
        "marshal": marshal_name, "target": target,
    }}
    return executor.execute(command, game_state)


# ══════════════════════════════════════════════════════════════════════
# The headline — the gate that made "free" meaningless
# ══════════════════════════════════════════════════════════════════════

class TestCounterPunchSurvivesTheAPGate:

    def test_zero_ap_counter_punch_is_not_refused_for_want_of_ap(self):
        """THE regression. Fails before the fix with 'Not enough actions!'."""
        world, _ = _world_with_cautious_attacker(ap=0, counter_punch=True)
        result = _attack(world)
        assert not _NOT_ENOUGH.search(str(result.get("message", ""))), (
            "a cautious marshal holding a counter-punch was refused for want "
            "of AP — the free attack is unusable in the only state where "
            "'free' means anything"
        )

    def test_zero_ap_without_counter_punch_still_refuses(self):
        """Negative control: the waiver is not a blanket AP bypass."""
        world, _ = _world_with_cautious_attacker(ap=0, counter_punch=False)
        result = _attack(world)
        assert result.get("success") is False
        assert _NOT_ENOUGH.search(str(result.get("message", ""))), (
            "an ordinary attack at 0 AP must still be refused"
        )

    def test_the_counter_punch_attack_costs_no_ap(self):
        """`>= 0` was unfalsifiable — `use_action` early-returns at 0 and
        clamps with `int(max(0, ...))`, so that assertion held with the fix
        reverted. The claim is that the AP is UNCHANGED (review round)."""
        world, _ = _world_with_cautious_attacker(ap=2, counter_punch=True)
        before = world.actions_remaining
        result = _attack(world)
        assert result.get("success") is True, result.get("message")
        assert world.actions_remaining == before, (
            "a counter-punch attack must not spend an action")

    def test_a_successful_counter_punch_spends_the_flag_not_the_ap(self):
        world, davout = _world_with_cautious_attacker(ap=0, counter_punch=True)
        result = _attack(world)
        # UNCONDITIONAL. Wrapping these in `if result.get("success")` made the
        # test pass vacuously in the reverted arm — the condition under test
        # was being used as the guard for testing it.
        assert result.get("success") is True, result.get("message")
        assert davout.counter_punch_available is False, (
            "a thrown counter-punch must be consumed")
        assert world.actions_remaining == 0


# ══════════════════════════════════════════════════════════════════════
# Spent only on success — the same rule AP obeys
# ══════════════════════════════════════════════════════════════════════

class TestRefusedAttackDoesNotBurnTheCounterPunch:
    """The refusal used here must be one that actually REACHES
    `_execute_attack`. A first draft of this test used the drill-lock, which
    an executor-level guard refuses ~3,000 lines earlier — so the pin passed
    with the fix reverted (caught by the mutation sweep, M3 survived). The
    tell is the message: a refusal raised inside `_execute_attack` reads
    differently from the pre-dispatch guard for the same condition
    ("locked in drill formation and cannot attack" vs "locked in drill
    exercises and cannot receive orders")."""

    def test_artillery_refusal_reaches_the_consumption_site(self):
        """Guard for the test below: prove `_execute_attack` really runs and
        really clears the flag, so the restore has something to undo."""
        world, davout = _world_with_cautious_attacker(ap=4, counter_punch=True)
        davout.artillery = True
        davout.moved_this_turn = True

        executor = CommandExecutor()
        result = executor._execute_attack(
            davout, "Wellington", world, {"world": world})

        assert result.get("success") is False
        assert davout.counter_punch_available is False, (
            "_execute_attack is expected to clear the flag at its head — if "
            "this ever stops being true the restore below is unnecessary"
        )

    def test_refused_attack_restores_the_counter_punch(self):
        world, davout = _world_with_cautious_attacker(ap=4, counter_punch=True)
        davout.artillery = True
        davout.moved_this_turn = True

        result = _attack(world)

        assert result.get("success") is False
        assert "setting up after repositioning" in str(result.get("message", "")), (
            "this refusal must be the one raised INSIDE _execute_attack, "
            "past the point where the counter-punch is cleared"
        )
        assert davout.counter_punch_available is True, (
            "a refused attack must not spend the counter-punch"
        )
        assert davout.counter_punch_turns == 2, (
            "the expiry clock must be restored too, or the free strike "
            "silently expires a turn early"
        )

    def test_not_at_war_refusal_also_restores(self):
        """A second, independent reachable path — so the pin does not rest on
        one quirk of the artillery rules."""
        world, davout = _world_with_cautious_attacker(ap=4, counter_punch=True)
        result = _attack(world, target="ArchdukeCharles")   # Austria: at peace

        assert result.get("success") is False
        assert "not at war" in str(result.get("message", "")).lower()
        assert davout.counter_punch_available is True


# ══════════════════════════════════════════════════════════════════════
# GR1 — one predicate, read by every site
# ══════════════════════════════════════════════════════════════════════

class TestTheWaiverBuysAStrikeAndNothingElse:
    """Both arms found by the review round on 4b09e59. The first was a
    regression this fix introduced."""

    def test_pursue_is_not_waived(self):
        """P1. `pursue` parses to `action == "attack"` with `is_strategic`,
        but costs 2 AP for a STANDING ORDER — which the counter-punch does not
        pay for. Waiving it let the order attach and the marshal march while
        the response said "Not enough actions", with `cancel` costing an AP
        the player did not have."""
        world, davout = _world_with_cautious_attacker(ap=0, counter_punch=True)
        executor = CommandExecutor()
        # `is_strategic` / `strategic_type` sit at the TOP level of the parsed
        # command, beside `command` — that is where the existing 2-AP pricing
        # arm reads them, and reading them from the wrong level is what makes
        # this pin bind or not.
        result = executor.execute({
            "is_strategic": True,
            "strategic_type": "PURSUE",
            "command": {
                "action": "attack", "type": "specific", "marshal": "Davout",
                "target": "Wellington",
            },
        }, {"world": world})

        assert result.get("success") is False
        assert _NOT_ENOUGH.search(str(result.get("message", "")))
        assert davout.strategic_order is None, (
            "a refused strategic order must not have been attached anyway")
        assert davout.location == "Belgium", "and he must not have marched"

    def test_an_out_of_range_attack_is_not_waived(self):
        """An out-of-range attack does not fight — it degrades into an
        approach march or a PURSUE clarification. Waiving it would buy free
        MOVEMENT at 0 AP, repeatably, because the strike is restored whenever
        no blow lands.

        Asserts the SPECIFIC refusal: "success is False" alone was inert,
        because the degraded path also fails at 0 AP, just further downstream
        and after moving him (caught by the round-2 mutation sweep)."""
        world, davout = _world_with_cautious_attacker(ap=0, counter_punch=True)
        far = world.marshals["Uxbridge"]                 # Hanover, 2 hops
        assert world.get_distance(davout.location, far.location) > davout.movement_range

        before = davout.location
        result = _attack(world, target="Uxbridge")

        assert result.get("success") is False
        msg = str(result.get("message", ""))
        assert _NOT_ENOUGH.search(msg), msg
        # ...and refused by the ATTACK gate, not by the strategic executor two
        # stages downstream. Matching "not enough actions" alone was inert:
        # with the waiver wrongly on, the command sails past the gate, reaches
        # `_execute_attack`, auto-upgrades to PURSUE and is refused there
        # instead — with a message that also says "not enough actions".
        assert "strategic" not in msg.lower(), (
            "the waiver let an out-of-range attack past the gate that should "
            "have stopped it: %s" % msg)
        assert davout.location == before, "no free march at 0 AP"
        assert davout.strategic_order is None

    def test_the_no_strike_set_names_every_outcome_that_does_not_fight(self):
        """STRUCTURAL, and deliberately so. The behavioural cases sit behind
        the objection battery, which intercepts before `_execute_attack` for
        precisely the cautious marshals who hold counter-punches — so the
        realistic route to them is a two-step objection flow that pins the
        objection's own copy rather than this rule. This binds the rule."""
        with open(os.path.join(REPO_ROOT, "backend", "commands",
                               "executor.py"), encoding="utf-8") as fh:
            src = fh.read()
        block = src[src.index("_no_strike = ("):]
        block = block[:block.index("\n            )")]
        for marker in ("requires_input", "pending_interrupt",
                       "awaiting_diplomatic_response", "war_purpose_popup",
                       "opening_attack_guidance", "occupation_started",
                       "awaiting_clarification"):
            assert marker in block, (
                f"{marker} is an outcome that throws no blow; dropping it "
                f"from the no-strike set spends the counter-punch for nothing")

    def test_a_thrown_strike_is_stamped_free_even_if_its_exit_forgot(self):
        """STRUCTURAL companion. Four `success: True` exits of
        `_execute_attack` resolve a strike without stamping `free_action` —
        the garrison assault and the auto-bombardment kill among them — so the
        player paid an action for a free attack, and one of those exits
        printed "This attack costs NO actions" while doing it."""
        with open(os.path.join(REPO_ROOT, "backend", "commands",
                               "executor.py"), encoding="utf-8") as fh:
            src = fh.read()
        block = src[src.index("_no_strike = ("):]
        block = block[:block.index("\n        # ==")]
        assert 'result["free_action"] = True' in block
        assert 'result["counter_punch_used"] = True' in block

    def test_the_strike_is_restored_when_no_blow_lands(self):
        """Fail-closed companion: whatever the outcome, an attack that did not
        fight must give the counter-punch back."""
        world, davout = _world_with_cautious_attacker(ap=4, counter_punch=True)
        _attack(world, target="ArchdukeCharles")   # out of range -> degrades
        assert davout.counter_punch_available is True


class TestSingleSourcePredicate:

    def _read(self, *parts):
        with open(os.path.join(REPO_ROOT, *parts), encoding="utf-8") as fh:
            return fh.read()

    def test_marshal_owns_the_predicate(self):
        src = self._read("backend", "models", "marshal.py")
        assert "def has_counter_punch(self)" in src

    def test_predicate_requires_both_flag_and_personality(self):
        world = WorldState()
        davout = world.marshals["Davout"]        # cautious
        ney = world.marshals["Ney"]              # aggressive

        assert davout.has_counter_punch() is False
        davout.counter_punch_available = True
        assert davout.has_counter_punch() is True

        ney.counter_punch_available = True
        assert ney.has_counter_punch() is False, (
            "the counter-punch is a cautious commander's reflex; the "
            "personality half of the predicate is load-bearing"
        )

    def test_consumption_site_no_longer_inlines_the_predicate(self):
        """The inline copy at the consumption site is what allowed the two
        gates to disagree with it. Re-introducing it re-opens this bug."""
        src = self._read("backend", "commands", "combat_executor.py")
        assert "marshal.has_counter_punch()" in src
        assert "counter_punch_available', False) and marshal.personality" not in src, (
            "the predicate was re-inlined at the consumption site"
        )

    def test_the_post_objection_gate_consults_it_too(self):
        """The THIRD gate, and the one a cautious marshal actually meets —
        because a cautious marshal is who objects. Without it the player paid
        −8 trust to insist past the objection, was told "he follows your
        orders", and was then refused for want of an action with the free
        strike still unspent."""
        src = self._read("backend", "commands", "meta_executor.py")
        assert "counter_punch_waiver" in src
        assert "if action_costs_point and not counter_punch_waiver:" in src
        block = src[src.index("counter_punch_waiver = bool("):]
        block = block[:block.index("if action_costs_point")]
        assert "has_counter_punch()" in block
        assert 'is_strategic' in block, "same exclusion as the pre-gates"
        assert "_attack_target_beyond_range" in block

    def test_the_predicate_has_no_remaining_inline_copies(self):
        """Widened from `combat_executor.py` to the whole backend after the
        review found a third copy in `enemy_ai.py` comparing against the
        EFFECTIVE personality while every other reader used the raw one."""
        import subprocess

        out = subprocess.run(
            ["git", "grep", "-n", "counter_punch_available", "--", "backend/"],
            cwd=REPO_ROOT, capture_output=True, text=True).stdout
        offenders = [ln for ln in out.split("\n")
                     if "personality" in ln and "def has_counter_punch" not in ln]
        assert not offenders, (
            "an inline (flag AND personality) copy of the predicate has come "
            "back:\n  " + "\n  ".join(offenders))

    def test_both_ap_pre_gates_consult_the_waiver(self):
        """A structural pin, because the two gates are 550 lines apart and
        only one of them being fixed reproduces the bug exactly."""
        src = self._read("backend", "commands", "executor.py")
        assert src.count("counter_punch_waiver") >= 3, (
            "expected the waiver to be computed once and read by BOTH "
            "AP pre-gates"
        )
        gate1 = "if action_costs_point and is_player_action_check and not counter_punch_waiver:"
        assert gate1 in src, "gate 1 (early AP check) does not consult the waiver"
        gate2 = ("if (action_costs_point and is_player_action_check\n"
                 "                        and not counter_punch_waiver):")
        assert gate2 in src, "gate 2 (AP PRE-CHECK) does not consult the waiver"

    def test_waiver_is_scoped_to_the_attack_action(self):
        src = self._read("backend", "commands", "executor.py")
        block = src[src.index("counter_punch_waiver = False"):]
        block = block[:block.index("if action_costs_point and is_player_action_check")]
        assert 'action == "attack"' in block, (
            "the waiver must not apply to any action other than the attack "
            "the counter-punch pays for"
        )


# ══════════════════════════════════════════════════════════════════════
# GR5 — the AI already worked; it must keep working, unchanged
# ══════════════════════════════════════════════════════════════════════

class TestEnemySideUnchanged:

    def test_enemy_counter_punch_predicate_is_the_same_one(self):
        world = WorldState()
        wellington = world.marshals["Wellington"]   # Britain, cautious
        assert wellington.nation != world.player_nation
        wellington.counter_punch_available = True
        assert wellington.has_counter_punch() is True, (
            "the enemy reads the same predicate — GR5"
        )


# ══════════════════════════════════════════════════════════════════════
# The stated boundary (GR9: recorded, not left open)
# ══════════════════════════════════════════════════════════════════════

class TestBareAttackBoundary:

    def test_bare_attack_with_no_named_marshal_still_refuses_at_zero_ap(self):
        """DELIBERATE, not an oversight. A bare "attack" is resolved to a
        marshal further down `execute()`, AFTER gate 1, so there is nobody to
        ask for a waiver at the gate. The counter-punch notification names its
        marshal ("<name> earned a free attack"), so the player has the name;
        naming him is what buys the waiver."""
        world, _ = _world_with_cautious_attacker(ap=0, counter_punch=True)
        executor = CommandExecutor()
        command = {"command": {"action": "attack", "type": "general_attack"}}
        result = executor.execute(command, {"world": world})
        assert result.get("success") is False
