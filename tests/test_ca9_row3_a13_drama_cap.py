"""CA9 row 3 / A13 — cap the routine drama lines.

Audit record: `docs/audits/GRIEVANCE_REVISIT_INVESTIGATION_2026_08_09.md`,
item A13 (Phase B). The audit measured ~15 marshal-drama lines per
answerable decision, 48 lines over 12 turns, and a peak of 10-12 in one
briefing — against `INTENT_DISPATCH_CAP = 2` for intent narration and 3
for marshal arcs. Jealousy capped FIRES only, never LINES.

Deliberately built LAST (memo §6 #3): half the volume was duplication and
self-contradiction, so a cap applied first would have preserved the
wrongness and collapsed the correct lines. A12 removed the duplication;
this bounds what remains.

The cap lives in the PRODUCER, AI-6 shape, so it governs routine movement
only. BEATS are exempt — by type, and for `jealousy_resolved` by
`by_action`, because an earned resolution and a timer expiry share a type
and are told apart only by A13's own prerequisite (landed in A2). AI-6's
exemption could be purely structural because its beats are produced
elsewhere; this one cannot, which is exactly why that key had to exist.
"""

import pytest

from backend.game_logic import jealousy as J
from backend.game_logic.dispatch import _DISPATCH_EVENT_TYPES

from tests.conftest import MarshalFactory, WorldFactory


@pytest.fixture()
def world():
    marshals = [MarshalFactory.infantry(name=n, location="Paris",
                                        strength=30000,
                                        personality="aggressive")
                for n in ("Ney", "Davout", "Soult", "Lannes", "Murat")]
    return WorldFactory.with_marshals(marshals, current_turn=6)


def _cap(world, added):
    """Run the producer cap over `added` as if this pass had emitted it."""
    events = J._pending_events(world)
    start = len(events)
    events.extend(added)
    J._cap_routine_drama(world, events, start)
    return events[start:]


def _routine(marshal="Ney", etype="jealousy_fired", **extra):
    ev = {"type": etype, "message": f"{marshal} line", "nation": "France",
          "marshal": marshal}
    ev.update(extra)
    return ev


# ════════════════════════════════════════════════════════════════════════
# The cap
# ════════════════════════════════════════════════════════════════════════

class TestTheCap:
    def test_routine_lines_are_bounded(self, world):
        out = _cap(world, [_routine(n) for n in
                           ("Ney", "Davout", "Soult", "Lannes", "Murat")])
        routine = [e for e in out if e["type"] == "jealousy_fired"]
        assert len(routine) == J.JEALOUSY_DISPATCH_CAP == 3

    def test_the_overflow_is_named_not_silently_dropped(self, world):
        out = _cap(world, [_routine(n) for n in
                           ("Ney", "Davout", "Soult", "Lannes", "Murat")])
        tail = [e for e in out if e["type"] == "jealousy_drama_tail"]
        assert len(tail) == 1
        assert tail[0]["count"] == 2
        assert "2 further matters" in tail[0]["message"]

    def test_one_extra_reads_as_singular(self, world):
        out = _cap(world, [_routine(n) for n in
                           ("Ney", "Davout", "Soult", "Lannes")])
        tail = next(e for e in out if e["type"] == "jealousy_drama_tail")
        assert "1 further matter " in tail["message"], tail["message"]

    def test_under_the_cap_nothing_changes(self, world):
        added = [_routine("Ney"), _routine("Davout")]
        out = _cap(world, list(added))
        assert out == added
        assert not [e for e in out if e["type"] == "jealousy_drama_tail"]

    def test_the_tail_can_reach_the_briefing(self):
        """A type absent from the whitelist is filtered out of TURN
        EVENTS and the overflow would vanish silently — the exact defect
        the tail exists to prevent."""
        assert "jealousy_drama_tail" in _DISPATCH_EVENT_TYPES

    def test_events_stashed_before_the_pass_are_untouched(self, world):
        """The cap governs what THIS pass adds. Battle-time hooks and the
        autonomous-attack pass stash into the same list and have their own
        surfaces and rate limits."""
        events = J._pending_events(world)
        events.extend([_routine(f"Prior{i}") for i in range(5)])
        start = len(events)
        events.extend([_routine(n) for n in
                       ("Ney", "Davout", "Soult", "Lannes", "Murat")])
        J._cap_routine_drama(world, events, start)
        assert len([e for e in events[:start]
                    if e["type"] == "jealousy_fired"]) == 5


# ════════════════════════════════════════════════════════════════════════
# The never-collapsed pin — one case per exempt beat
# ════════════════════════════════════════════════════════════════════════

class TestBeatsAreNeverCollapsed:
    """The pin AI-6's §18.1 handoff demanded, and the reason this slice
    could not be built before A2: the exempt and cappable events come out
    of the same function and two of them share a type string."""

    FLOOD = [_routine(f"Filler{i}") for i in range(8)]

    def _survives(self, world, beat):
        out = _cap(world, list(self.FLOOD) + [beat])
        return beat in out

    def test_the_crown(self, world):
        assert self._survives(world, {
            "type": "glory_crowned", "message": "crowned",
            "nation": "France", "marshal": "Ney"})
        assert self._survives(world, {
            "type": "glory_crown_lost", "message": "lost",
            "nation": "France", "marshal": "Ney"})

    def test_the_autonomous_warning_and_the_attack(self, world):
        assert self._survives(world, {
            "type": "jealousy_autonomous_warning", "message": "warned",
            "nation": "France", "marshal": "Ney"})
        assert self._survives(world, {
            "type": "jealousy_autonomous_attack", "message": "attacked",
            "nation": "France", "marshal": "Ney"})

    def test_the_separation_warning(self, world):
        """The one arm the player OPTED INTO. `test_jealousy_v32.py`
        asserts it is present in the pass output; a naive cap reds it."""
        assert self._survives(world, {
            "type": "jealousy_separation_warning", "message": "warned",
            "nation": "France", "marshal": "Ney"})

    def test_a_petition_arriving(self, world):
        assert self._survives(world, {
            "type": "fontainebleau_petition", "message": "they petition",
            "nation": "France", "marshal": "Ney"})

    def test_an_EARNED_resolution(self, world):
        """A2's discriminator doing the work it was landed for."""
        assert self._survives(world, {
            "type": "jealousy_resolved", "message": "satisfied",
            "nation": "France", "marshal": "Ney", "by_action": True})

    def test_escalation_to_PERMANENT(self, world):
        assert self._survives(world, {
            "type": "jealousy_escalation", "message": "entrenched",
            "nation": "France", "marshal": "Ney",
            "level": J.ESCALATION_PERMANENT_LEVEL})

    def test_the_whole_exempt_set_is_one_auditable_tuple(self):
        assert J.JEALOUSY_NARRATION_EXEMPT == (
            "glory_crowned",
            "glory_crown_lost",
            "jealousy_autonomous_warning",
            "jealousy_autonomous_attack",
            "jealousy_separation_warning",
            "fontainebleau_petition",
            "marshal_commissioned",
        )


class TestWhatIsRoutineAndStaysRoutine:
    FLOOD = [_routine(f"Filler{i}") for i in range(8)]

    def _survives(self, world, beat):
        return beat in _cap(world, list(self.FLOOD) + [beat])

    def test_a_TIMER_expiry_is_routine(self, world):
        """The other half of A2's discriminator: "cooled with time" is
        the archetypal routine line."""
        assert not self._survives(world, {
            "type": "jealousy_resolved", "message": "cooled",
            "nation": "France", "marshal": "Zed", "by_action": False})

    def test_a_level_1_escalation_is_routine(self, world):
        """The memo's list says escalation-to-PERMANENT, and it is right:
        "has become a matter of concern" is movement, not a beat."""
        assert not self._survives(world, {
            "type": "jealousy_escalation", "message": "a matter of concern",
            "nation": "France", "marshal": "Zed", "level": 1})

    def test_the_HELD_promise_line_is_routine(self, world):
        """It repeats for as long as the Emperor's word stands, so it
        cannot be a beat — and it explicitly did NOT move the level."""
        assert not self._survives(world, {
            "type": "jealousy_escalation", "message": "he holds to it",
            "nation": "France", "marshal": "Zed", "held": True,
            "level": J.ESCALATION_PERMANENT_LEVEL})


# ════════════════════════════════════════════════════════════════════════
# Which routine lines survive
# ════════════════════════════════════════════════════════════════════════

class TestTheDeepestQuarrelSurvives:
    def test_ranked_by_escalation_then_fires(self, world):
        deep, mid, shallow = ("Soult", "Davout", "Ney")
        J._set_escalation_level(world.marshals[deep], "Murat", 3)
        J._set_escalation_level(world.marshals[mid], "Murat", 1)
        for name in (deep, mid, shallow):
            world.marshals[name].jealous_of = "Murat"
        world.marshals[shallow].jealousy_history["Murat"] = [1]
        world.marshals[mid].jealousy_history["Murat"] = [1, 2]
        world.marshals[deep].jealousy_history["Murat"] = [1, 2, 3]

        out = _cap(world, [_routine(n, target="Murat") for n in
                           (shallow, mid, deep, "Lannes", "Ney")])
        names = [e["marshal"] for e in out
                 if e["type"] == "jealousy_fired"]
        assert names[0] == deep
        assert mid in names

    def test_the_order_is_stable(self, world):
        """Deterministic: equal-severity quarrels break on name, so the
        briefing does not reshuffle between identical turns."""
        first = [e.get("marshal") for e in _cap(world, [
            _routine(n) for n in
            ("Murat", "Ney", "Davout", "Soult", "Lannes")])]
        J._pending_events(world).clear()
        second = [e.get("marshal") for e in _cap(world, [
            _routine(n) for n in
            ("Murat", "Ney", "Davout", "Soult", "Lannes")])]
        assert first == second


# ════════════════════════════════════════════════════════════════════════
# Through the real pass — the tests above call the cap directly, and a
# mutation sweep showed that deleting its CALL SITE left them all green
# ════════════════════════════════════════════════════════════════════════

class TestTheCapIsActuallyWiredIntoTheTurnPass:
    @pytest.fixture()
    def expiring(self):
        """Five player marshals whose grievances all lapse this pass —
        five routine `jealousy_resolved` lines out of one `process_turn`."""
        names = ("Ney", "Davout", "Soult", "Lannes", "Massena")
        marshals = [MarshalFactory.infantry(name=n, location="Paris",
                                            strength=30000,
                                            personality="aggressive")
                    for n in names] + [
            MarshalFactory.infantry(name="Murat", location="Paris",
                                    strength=30000, personality="aggressive")]
        world = WorldFactory.with_marshals(marshals, current_turn=6)
        for n in names:
            m = world.marshals[n]
            m.jealous_of = "Murat"
            m.jealousy_turns_remaining = 1
        return world

    def _pass(self, world):
        prior = len(J._pending_events(world))
        J.process_turn(world)
        return J._pending_events(world)[prior:]

    def test_the_pass_emits_a_capped_list(self, expiring):
        out = self._pass(expiring)
        routine = [e for e in out
                   if e["type"] == "jealousy_resolved"
                   and not e.get("by_action")]
        assert len(routine) == J.JEALOUSY_DISPATCH_CAP
        assert [e for e in out if e["type"] == "jealousy_drama_tail"]

    def test_events_from_earlier_in_the_turn_survive_the_pass(self, expiring):
        """`_cap_from` is a HIGH-WATER MARK, not zero. Battle-time hooks
        stash into the same list before the pass runs, and they have their
        own surface and their own rate limits."""
        world = expiring
        events = J._pending_events(world)
        earlier = [{"type": "jealousy_fired", "message": f"earlier {i}",
                    "nation": "France", "marshal": "Murat"}
                   for i in range(6)]
        events.extend(earlier)
        J.process_turn(world)
        assert all(e in events for e in earlier), (
            "the pass capped events it did not produce")


class TestTheRankingActuallyRanks:
    def test_escalation_depth_outranks_a_longer_history(self, world):
        """The two keys are made to DISAGREE, so only the escalation term
        can produce the expected order. With them aligned (the first draft)
        the test passed even with the escalation term zeroed out."""
        for n in ("Ney", "Davout", "Soult", "Lannes"):
            world.marshals[n].jealous_of = "Murat"
        # Soult: deepest quarrel, SHORTEST history.
        J._set_escalation_level(world.marshals["Soult"], "Murat", 3)
        world.marshals["Soult"].jealousy_history["Murat"] = [1]
        # Ney: no escalation, LONGEST history.
        world.marshals["Ney"].jealousy_history["Murat"] = [1, 2, 3, 4, 5, 6]
        world.marshals["Davout"].jealousy_history["Murat"] = [1, 2, 3, 4, 5]
        world.marshals["Lannes"].jealousy_history["Murat"] = [1, 2, 3, 4]

        out = _cap(world, [_routine(n, target="Murat") for n in
                           ("Ney", "Davout", "Lannes", "Soult")])
        names = [e["marshal"] for e in out if e["type"] == "jealousy_fired"]
        assert names[0] == "Soult", names

    def test_ties_break_alphabetically(self, world):
        """Explicitly alphabetical, not merely "stable within a process".
        The first draft compared two runs in ONE process, where ordering
        by `id()` is also stable — so it could not see the difference."""
        for n in ("Ney", "Davout", "Soult", "Lannes", "Murat"):
            world.marshals[n].jealous_of = "Enemy"
        out = _cap(world, [_routine(n, target="Enemy") for n in
                           ("Ney", "Murat", "Soult", "Lannes", "Davout")])
        names = [e["marshal"] for e in out if e["type"] == "jealousy_fired"]
        assert names == sorted(names), names
        assert names == ["Davout", "Lannes", "Murat"], names
