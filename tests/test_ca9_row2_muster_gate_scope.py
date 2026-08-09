"""CA9 row 2 — the attack confirm popup is scoped to disaster AND character.

Gate record: `docs/audits/CA9_GATE_ANSWERS_2026_08_09.md` §2 (authoritative).
The user's ruling, verbatim: *"only show popup if they are entering potential
disaster and general is cautious."*

Before this, the W6-4 muster confirm armed whenever the odds band was not
`favorable`, for every marshal. CA9-F1 then taught the preview to count the
DEFENDER's reinforcements, so `even` became common and the modal fired
constantly. Two narrowings, one predicate
(`objection_v2.muster_gate_arms`):

  1. `even` no longer blocks anybody — only `unfavorable`.
  2. only a `cautious` marshal stops to ask.

The falsifiable core of this file is the 2x2 matrix in
`TestGatePredicateMatrix`: hold the band and flip the personality, hold the
personality and flip the band. Delete either term from the predicate and one
of those cells goes red. Everything else here guards the two things that
could quietly go wrong while satisfying the matrix — that the information is
still delivered when the gate does not arm, and that the copy is never spoken
by a marshal the predicate did not select.
"""

import pytest

from backend.commands.executor import CommandExecutor
from backend.commands.objection_v2 import (
    MUSTER_GATE_BAND,
    MUSTER_GATE_PERSONALITIES,
    ConcernLevel,
    muster_gate_arms,
)
from backend.models.personality import IMPLEMENTED_PERSONALITIES

from tests.conftest import MarshalFactory, WorldFactory


@pytest.fixture(autouse=True)
def _no_mood_variance(monkeypatch):
    """Neutralise `apply_mood_variance` for this file.

    It has a 10% chance of promoting a MILD concern to MODERATE, which
    crosses `is_blocking_concern` — so a cautious marshal in the gate's own
    window objects INSTEAD of meeting the gate, and roughly 1 run in 10 of
    any gate test fails for a reason that has nothing to do with the gate.
    That is what made this file flaky while it was being written.

    Its own docstring prescribes exactly this ("Tests should mock
    random.random() for deterministic results"); neutralising the function
    is the same intent at a stabler seam than a seed, which would shift the
    moment production consumed a different amount of RNG.

    The promotion is real, intended behaviour — day-to-day mood — and is
    pinned by `TestMoodVarianceCanPreEmptTheGate` below. It is disabled
    here, not denied.
    """
    monkeypatch.setattr("backend.commands.executor.apply_mood_variance",
                        lambda concern: concern)


def _war(world, a="France", b="Austria"):
    key = "|".join(sorted([a, b]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn


def _world(personality, own_strength, enemy_strength, name="Davout"):
    """A player marshal of `personality` facing `enemy_strength` at Belgium."""
    mine = MarshalFactory.infantry(name=name, location="Belgium",
                                   strength=own_strength,
                                   personality=personality)
    mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                nation="Austria", strength=enemy_strength,
                                personality="cautious")
    world = WorldFactory.with_marshals([mine, mack])
    _war(world)
    # Fog is load-bearing here and must be pinned, not inherited. A cautious
    # marshal objects on POOR INTEL alone — `evaluate_cautious` returns
    # STRONG on UNKNOWN and MODERATE on STALE/LAST_KNOWN, before it ever
    # looks at the odds — and that objection pre-empts the muster gate. So a
    # test whose intel has drifted silently stops testing the gate. This is
    # the production seam that decides it (`TestFogPreemptsTheGate` pins the
    # behaviour itself).
    world.calculate_visibility()
    return world, CommandExecutor()


def _attack(executor, world, marshal="Davout"):
    return executor.execute(
        {"success": True,
         "command": {"marshal": marshal, "action": "attack",
                     "target": "Mack"}},
        {"world": world})


# ── The measured layering (probe, Aug 9 2026) ───────────────────────────
# Scoping the gate to (unfavorable, cautious) exposed something the gate
# record could not have known: a cautious marshal ordered into SEVERE odds
# already raises a V2a objection, and that fires FIRST. Measured, enemy:own:
#
#   >= 2.00  unfavorable  -> V2a OBJECTION (trust / insist / compromise)
#   1.43-2.00 unfavorable -> MUSTER CONFIRM   <- the gate's surviving window
#   1.00-1.43 even        -> nothing (row 2 removed this)
#   < 1.00   favorable    -> nothing
#
# So the muster confirm is not dead code: it owns the band that is bad but
# not obviously suicidal, BELOW the objection's threshold. And the player is
# never asked twice — `TestTheTwoSurfacesDoNotStack` pins that.
#
# Fixtures therefore need BOTH unfavorable cases, because they route to
# different surfaces. Every test asserts the band it produced rather than
# trusting these numbers, so a ratio-math change fails loudly instead of
# silently re-pointing a test at the wrong surface.
_MUSTER_WINDOW = (30000, 50000)  # unfavorable, below the objection threshold
_SEVERE = (20000, 50000)         # unfavorable, the objection owns it
_COMFORTABLE = (60000, 8000)     # ratio over parity


# ════════════════════════════════════════════════════════════════════════
# The predicate itself — the 2x2 that makes both terms load-bearing
# ════════════════════════════════════════════════════════════════════════

class TestGatePredicateMatrix:
    """Pure-function coverage. No world, no executor — just the rule."""

    def test_cautious_and_unfavorable_arms(self):
        m = MarshalFactory.infantry(name="Davout", personality="cautious")
        assert muster_gate_arms(m, "unfavorable") is True

    def test_cautious_and_even_does_not_arm(self):
        """Hold the personality, flip the band."""
        m = MarshalFactory.infantry(name="Davout", personality="cautious")
        assert muster_gate_arms(m, "even") is False

    def test_cautious_and_favorable_does_not_arm(self):
        m = MarshalFactory.infantry(name="Davout", personality="cautious")
        assert muster_gate_arms(m, "favorable") is False

    def test_aggressive_and_unfavorable_does_not_arm(self):
        """Hold the band, flip the personality. This is the row-2 change."""
        m = MarshalFactory.infantry(name="Ney", personality="aggressive")
        assert muster_gate_arms(m, "unfavorable") is False

    def test_literal_and_unfavorable_does_not_arm(self):
        m = MarshalFactory.infantry(name="Soult", personality="literal")
        assert muster_gate_arms(m, "unfavorable") is False

    def test_exactly_one_implemented_personality_arms(self):
        """Guards against the frozenset quietly widening. If a future gate
        record adds a personality, this number moves WITH the record."""
        arming = {p for p in IMPLEMENTED_PERSONALITIES
                  if muster_gate_arms(
                      MarshalFactory.infantry(name="X", personality=p),
                      MUSTER_GATE_BAND)}
        assert arming == {"cautious"}
        assert MUSTER_GATE_PERSONALITIES == frozenset({"cautious"})

    def test_unknown_or_missing_personality_never_arms(self):
        """MC-4 retired `balanced`/`loyal` but a legacy SAVE can still load
        one, and `from_dict` is deliberately unguarded. A marshal the rule
        does not recognise must fall through to 'no block', never crash."""
        legacy = MarshalFactory.infantry(name="Ghost", personality="cautious")
        legacy.personality = "balanced"
        assert muster_gate_arms(legacy, "unfavorable") is False

        class _Bare:
            pass

        assert muster_gate_arms(_Bare(), "unfavorable") is False


# ════════════════════════════════════════════════════════════════════════
# Through the real attack path
# ════════════════════════════════════════════════════════════════════════

class TestGateThroughTheExecutor:
    def test_cautious_in_the_gate_window_is_stopped(self):
        world, executor = _world("cautious", *_MUSTER_WINDOW)
        mack_before = world.get_marshal("Mack").strength
        ap_before = world.actions_remaining
        result = _attack(executor, world)
        assert result.get("requires_input") is True
        assert result["pending_interrupt"]["interrupt_type"] == "muster_confirm"
        assert result["muster_preview"]["odds_band"] == "unfavorable"
        # Nothing resolved, nothing spent.
        assert world.get_marshal("Mack").strength == mack_before
        assert world.actions_remaining == ap_before

    def test_aggressive_into_disaster_charges(self):
        """The row-2 headline: an aggressive marshal is not asked, and the
        battle happens. This is the behaviour change to watch in play.

        Priced at SEVERE odds deliberately — `evaluate_aggressive` has no
        attack trigger at all, so nothing else catches him either. He is
        genuinely unescorted into a 2.5:1 fight, which is the point.
        """
        world, executor = _world("aggressive", *_SEVERE, name="Ney")
        mack_before = world.get_marshal("Mack").strength
        result = _attack(executor, world, marshal="Ney")
        assert result.get("requires_input") is None
        assert (result.get("pending_interrupt") or {}).get(
            "interrupt_type") != "muster_confirm"
        assert world.get_marshal("Mack").strength < mack_before

    def test_literal_into_disaster_marches(self):
        world, executor = _world("literal", *_SEVERE, name="Soult")
        mack_before = world.get_marshal("Mack").strength
        result = _attack(executor, world, marshal="Soult")
        assert result.get("requires_input") is None
        assert (result.get("pending_interrupt") or {}).get(
            "interrupt_type") != "muster_confirm"
        assert world.get_marshal("Mack").strength < mack_before

    def test_cautious_at_even_odds_is_no_longer_stopped(self):
        """The other half of the narrowing. `even` blocked everyone before
        row 2; it now blocks nobody, including the cautious marshal.

        The fixture asserts the band it produced, so this cannot silently
        become a duplicate of the `favorable` case if the ratio math moves.
        """
        world, executor = _world("cautious", 40000, 50000)
        result = _attack(executor, world)
        assert result["muster_preview"]["odds_band"] == "even", (
            "fixture no longer produces an `even` band — retune the "
            "strengths, do not delete the test")
        assert result.get("requires_input") is None
        assert (result.get("pending_interrupt") or {}).get(
            "interrupt_type") != "muster_confirm"

    def test_favorable_still_resolves_for_a_cautious_marshal(self):
        world, executor = _world("cautious", *_COMFORTABLE)
        result = _attack(executor, world)
        assert result["muster_preview"]["odds_band"] == "favorable"
        assert result.get("requires_input") is None


# ════════════════════════════════════════════════════════════════════════
# The two surfaces that can ask a cautious marshal never both ask
# ════════════════════════════════════════════════════════════════════════

class TestTheTwoSurfacesDoNotStack:
    """Found by building row 2, not by reading the gate record.

    A cautious marshal at SEVERE odds already raises a V2a objection, which
    is the richer decision (trust / insist / compromise, with trust
    consequences) — and it fires before the muster gate. Row 2's ruling is
    therefore coherent rather than redundant: whichever surface owns the
    severity band asks, and the player is asked exactly ONCE. That is the
    CR-5 "objection-first ONE-modal legibility" guardrail, now pinned.

    If a refactor ever lets both fire, the popup count the user asked us to
    reduce doubles in the worst case. These tests are the tripwire.

    Tested at the CONCERN seam, deliberately. The first draft asserted
    "an objection fires" through the full executor and was order-dependent:
    the V2a/V2b stack downgrades, cools down and re-tones objections using
    state that other tests in the same session leave behind, so those
    assertions passed or failed on what ran before them. The claim being
    made here is about concern LEVEL versus the gate predicate, and both are
    pure functions — so they are tested as pure functions, and the executor
    is used only for the negative (no muster confirm), which is stable.

    That order-dependence is itself a real finding and belongs to row 3's
    popup/queue audit, not here.
    """

    def _concern(self, own, enemy, visibility=None):
        from backend.commands.objection_v2 import evaluate_cautious
        world, _ = _world("cautious", own, enemy)
        world.calculate_visibility()
        if visibility is not None:
            world.intel["Belgium"].visibility = visibility
        return evaluate_cautious(
            world.get_marshal("Davout"), "attack", {"target": "Mack"},
            {"world": world})

    def test_severe_odds_are_the_objection_systems_business(self):
        from backend.commands.objection_v2 import is_blocking_concern
        concern = self._concern(*_SEVERE)
        assert is_blocking_concern(concern), (
            f"severe odds should raise a blocking objection, got {concern}")

    def test_gate_window_odds_are_below_the_objection_threshold(self):
        """The other half: in the band the gate owns, the objection system
        declines to block — so the gate is what the player meets, and it is
        not a second modal stacked on a first."""
        from backend.commands.objection_v2 import is_blocking_concern
        concern = self._concern(*_MUSTER_WINDOW)
        assert not is_blocking_concern(concern), (
            f"the gate's own window must not also objection-block, got "
            f"{concern}")

    def test_co_location_makes_the_fixtures_fog_proof(self):
        """Why there is no fog test here, stated as a test.

        `evaluate_cautious` DOES outrank the odds on poor intel — STRONG on
        UNKNOWN, MODERATE on STALE — which would pre-empt the gate even at
        favourable odds. It cannot happen in this file, because
        `get_target_intel_level` returns FULL unconditionally for a
        co-located target (objection_v2.py:485, the "Step 0" rule) and every
        fixture here attacks into the marshal's own province.

        That is worth a test rather than a comment: it is what makes these
        fixtures deterministic, and if the Step 0 rule ever changes, every
        odds-based assertion in this file silently starts depending on fog.
        Pinning the fog behaviour ITSELF needs a non-co-located fixture,
        which routes through a different combat path — so it belongs with
        the objection system's own coverage, not row 2's.
        """
        from backend.commands.objection_v2 import get_target_intel_level
        from backend.models.intel import FULL, UNKNOWN
        world, _ = _world("cautious", *_COMFORTABLE)
        world.calculate_visibility()
        world.intel["Belgium"].visibility = UNKNOWN
        davout = world.get_marshal("Davout")
        assert davout.location == world.get_marshal("Mack").location
        assert get_target_intel_level("Mack", davout, world) == FULL, (
            "the Step 0 co-location rule changed — the odds assertions in "
            "this file now depend on fog state and need pinning")

    def test_the_gate_never_arms_where_the_objection_blocks(self):
        """The no-stacking claim itself, as arithmetic over both predicates
        rather than as a sequence of modals. For every case the objection
        system blocks, the gate must be irrelevant — either because the band
        is not `unfavorable`, or because the objection got there first and
        the post-objection path bypasses the gate (verified by
        `test_insisting_never_yields_a_muster_confirm`)."""
        from backend.commands.objection_v2 import (
            inferred_attack_odds_band, is_blocking_concern,
        )
        world, _ = _world("cautious", *_SEVERE)
        world.calculate_visibility()
        davout, mack = world.get_marshal("Davout"), world.get_marshal("Mack")
        band = inferred_attack_odds_band(davout, mack, {"world": world})
        concern = self._concern(*_SEVERE)
        # Both WOULD fire on their own terms — which is exactly why the
        # ordering guarantee has to be tested, not assumed.
        assert band == MUSTER_GATE_BAND
        assert muster_gate_arms(davout, band) is True
        assert is_blocking_concern(concern) is True

    def test_insisting_never_yields_a_muster_confirm(self):
        """The integration half, asserted only as a NEGATIVE so it does not
        depend on whether the objection fired in this particular ordering.
        Whatever happened first, the player must not then be handed the
        muster confirm for the same attack."""
        world, executor = _world("cautious", *_SEVERE)
        _attack(executor, world)
        after = executor.execute(
            {"success": True,
             "command": {"action": "handle_objection_response",
                         "response": "insist"}},
            {"world": world})
        assert (after.get("pending_interrupt") or {}).get(
            "interrupt_type") != "muster_confirm"
        assert (getattr(world.get_marshal("Davout"), "pending_interrupt",
                        None) or {}).get("interrupt_type") != "muster_confirm"

    def test_both_bands_are_unfavorable_so_the_split_is_severity_not_band(self):
        """Guards the comment block above: the objection/gate split is NOT
        a band difference — both fixtures read `unfavorable`. If the ratio
        math ever moves one of them into `even`, this says so instead of
        letting the layering tests quietly test something else."""
        from backend.commands.objection_v2 import inferred_attack_odds_band
        for label, (own, enemy) in (("severe", _SEVERE),
                                    ("window", _MUSTER_WINDOW)):
            world, _ = _world("cautious", own, enemy)
            band = inferred_attack_odds_band(
                world.get_marshal("Davout"), world.get_marshal("Mack"),
                {"world": world})
            assert band == "unfavorable", f"{label} fixture drifted to {band}"


# ════════════════════════════════════════════════════════════════════════
# The information is not what was removed
# ════════════════════════════════════════════════════════════════════════

class TestNothingIsHidden:
    """The gate record's claim: *"The preview still prints, with honest
    numbers, on every attack. Only the BLOCKING changes."* Made falsifiable
    — if a future change makes the preview conditional on the gate, these go
    red and the claim stops being true silently."""

    def test_unblocked_disaster_still_reports_the_band(self):
        world, executor = _world("aggressive", *_SEVERE, name="Ney")
        result = _attack(executor, world, marshal="Ney")
        assert result.get("muster_preview") is not None
        assert result["muster_preview"]["odds_band"] == "unfavorable"
        # And in the prose the player actually reads.
        assert "MUSTER" in result["message"]
        assert "unfavorable" in result["message"]

    def test_every_personality_gets_the_preview_on_a_resolved_attack(self):
        for personality, name in (("aggressive", "Ney"),
                                  ("literal", "Soult"),
                                  ("cautious", "Bernadotte")):
            world, executor = _world(personality, *_COMFORTABLE, name=name)
            result = _attack(executor, world, marshal=name)
            assert result.get("muster_preview") is not None, personality
            assert "MUSTER" in result["message"], personality


# ════════════════════════════════════════════════════════════════════════
# One predicate decides the popup AND the copy
# ════════════════════════════════════════════════════════════════════════

class TestCopyFollowsThePredicate:
    """The gate record: *"Whatever the rule, the SAME predicate must decide
    the popup and the copy."* The modal is now a character beat, so it
    speaks in the cautious register — and must never do so for a marshal the
    predicate did not select."""

    def test_the_modal_is_spoken_by_the_marshal_who_halted(self):
        world, executor = _world("cautious", *_MUSTER_WINDOW)
        msg = _attack(executor, world)["message"]
        assert "Davout halts before the order is carried out." in msg
        # His own words, not the staff's summary.
        assert '"' in msg
        # And it still names the band it is halting over (shown == applied).
        assert "unfavorable" in msg

    def test_the_halt_line_never_appears_without_the_gate(self):
        """FALSIFIABLE NEGATIVE. An aggressive marshal at the same odds must
        not be narrated as hesitating — that would falsify his character to
        serve a UI change, which the standing rule forbids."""
        world, executor = _world("aggressive", *_SEVERE, name="Ney")
        msg = _attack(executor, world, marshal="Ney")["message"]
        assert "halts before the order is carried out" not in msg

    def test_the_halt_rotates_so_a_grind_is_not_one_line(self):
        from backend.game_logic.marshal_voice import cautious_muster_halt
        lines = {cautious_muster_halt("Davout", t) for t in range(6)}
        assert len(lines) >= 3, (
            "the bank must rotate — a cautious marshal in a long defensive "
            "campaign reaches this modal repeatedly (XR-5's lesson)")
        for line in lines:
            assert line.startswith("Davout halts")

    def test_no_bank_exists_for_the_personalities_that_never_halt(self):
        """Structural: the copy has no arm for aggressive/literal, because
        the predicate can never route them here. If someone adds one, that
        is a gate-record change and this test says so."""
        from backend.game_logic import marshal_voice
        bank = marshal_voice._MUSTER_HALT_LINES
        assert isinstance(bank, list) and len(bank) >= 3
        # It is a flat cautious-only bank, not a per-personality mapping.
        assert not isinstance(bank, dict)


# ════════════════════════════════════════════════════════════════════════
# Mood variance is a fourth thing that can answer instead of the gate
# ════════════════════════════════════════════════════════════════════════

class TestMoodVarianceCanPreEmptTheGate:
    """Pins the behaviour the autouse fixture disables.

    `apply_mood_variance` promotes a concern one level 10% of the time, so
    even inside the gate's own window a cautious marshal will sometimes
    object rather than be gated. That is intended — it is the marshal having
    a bad morning — but it is worth recording, because it means the gate is
    not a hard guarantee even for the personality it is scoped to, and
    because anyone debugging an "it gated yesterday and objected today"
    report should find this test first.
    """

    def test_a_promoted_mood_objects_instead_of_gating(self, monkeypatch):
        monkeypatch.setattr(
            "backend.commands.executor.apply_mood_variance",
            lambda c: ConcernLevel(min(c.value + 1,
                                       ConcernLevel.EXTREME.value)))
        world, executor = _world("cautious", *_MUSTER_WINDOW)
        result = _attack(executor, world)
        assert (result.get("pending_interrupt") or {}).get(
            "interrupt_type") != "muster_confirm"
        assert result.get("awaiting_response") is True

    def test_and_the_unpromoted_case_still_gates(self, monkeypatch):
        """The control. Without this, the test above could pass because the
        fixture is broken rather than because mood variance did anything."""
        monkeypatch.setattr("backend.commands.executor.apply_mood_variance",
                            lambda c: c)
        world, executor = _world("cautious", *_MUSTER_WINDOW)
        result = _attack(executor, world)
        assert result["pending_interrupt"]["interrupt_type"] == "muster_confirm"


# ════════════════════════════════════════════════════════════════════════
# The pre-existing exemptions still hold (GR5 + the bypasses)
# ════════════════════════════════════════════════════════════════════════

class TestExemptionsUnchanged:
    def test_ai_attack_never_arms_even_for_a_cautious_marshal(self):
        """GR5: the confirm is a player legibility surface. Mack is literal
        in the 1805 roster but the enemy here is built cautious on purpose —
        the exemption must be about WHO IS PLAYING, not personality."""
        mine = MarshalFactory.infantry(name="Davout", location="Belgium",
                                       strength=50000, personality="cautious")
        enemy = MarshalFactory.enemy(name="Mack", location="Belgium",
                                     nation="Austria", strength=8000,
                                     personality="cautious")
        world = WorldFactory.with_marshals([mine, enemy])
        _war(world)
        executor = CommandExecutor()
        result = executor.execute(
            {"success": True,
             "command": {"marshal": "Mack", "action": "attack",
                         "target": "Davout", "_autonomous_execution": True,
                         "_acting_nation": "Austria"}},
            {"world": world})
        assert (result.get("pending_interrupt") or {}).get(
            "interrupt_type") != "muster_confirm"
        assert world.get_marshal("Mack").pending_interrupt is None

    def test_strategic_execution_still_bypasses(self):
        world, executor = _world("cautious", *_MUSTER_WINDOW)
        result = executor.execute(
            {"success": True,
             "command": {"marshal": "Davout", "action": "attack",
                         "target": "Mack", "_strategic_execution": True}},
            {"world": world})
        assert (result.get("pending_interrupt") or {}).get(
            "interrupt_type") != "muster_confirm"
        assert world.get_marshal("Mack").strength < 50000

    def test_muster_confirmed_reissue_still_bypasses(self):
        world, executor = _world("cautious", *_MUSTER_WINDOW)
        result = executor.execute(
            {"success": True,
             "command": {"marshal": "Davout", "action": "attack",
                         "target": "Mack", "_muster_confirmed": True}},
            {"world": world})
        assert result.get("requires_input") is None
        assert result.get("muster_preview") is not None
        assert world.get_marshal("Mack").strength < 50000
