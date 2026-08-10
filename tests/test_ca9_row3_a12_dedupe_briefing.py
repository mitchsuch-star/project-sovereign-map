"""CA9 row 3 / A12 — the briefing stops contradicting itself.

Audit record: `docs/audits/GRIEVANCE_REVISIT_INVESTIGATION_2026_08_09.md`,
item A12. Three sub-changes, deliberately built BEFORE any cap (memo §6
#3: half the volume is duplication and self-contradiction, so a cap
preserves the wrongness and collapses the correct lines).

(a) A pair that cooled in step 1 of the jealousy pass could be handed
    straight back by step 3 of the SAME pass — `clear_jealousy` writes no
    "cooled this turn" marker, so the marshal reads `jealous_of is None`
    and `JEALOUSY_RIVAL_MEMORY` returns the man he just stopped
    resenting. Measured: 26 events over 20 of 40 ambient turns, and a
    briefing page carrying "his resentment has cooled" above "he resents
    him, for the fourth time".
(b) The level-1 escalation line co-emitted with the `jealousy_fired`
    line that caused it — one trigger, two bullets, same news, two
    registers.
(c) Rung 3.5 of Berthier's note read `jealous[0]` / `jealous[:2]` in
    `world.marshals` DICT ORDER, i.e. whichever Frenchman is earliest in
    the scenario JSON — never the most aggrieved.

The whole rung sits inside a bare `try/except: pass`, so a ranking bug
would silently fall through to rung 4 with the suite green. Hence the
positive-reach pin.
"""

import io
import tokenize

import pytest

from backend.game_logic import jealousy as J
from backend.game_logic.dispatch import _pick_berthier_note

from tests.conftest import MarshalFactory, WorldFactory


def _strip_comments(src: str) -> str:
    """Source with `#` comments removed.

    Load-bearing: several pins below index into `process_turn`'s source to
    assert that one gate is evaluated before another. Comments legitimately
    NAME both constants, so an unstripped index can compare two comment
    positions and pass without reading code — which is exactly what the
    first draft of `test_the_suppression_does_not_burn_a_nation_fire_slot`
    did.
    """
    src = "\n".join(line[4:] if line.startswith("    ") else line
                    for line in src.splitlines())
    out = []
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type != tokenize.COMMENT:
            out.append(tok.string)
    return "\n".join(out)


def _new_events(world):
    """Only the events THIS pass appended (the persistent-list trap —
    `process_turn` writes into a world-owned list that `advance_turn`
    collects and clears)."""
    prior = len(J._pending_events(world))
    J.process_turn(world)
    return J._pending_events(world)[prior:]


def _mark_processed_clear(world):
    """`process_turn` no-ops if already run this turn."""
    world._jealousy_processed_turn = None


@pytest.fixture()
def feud():
    """Ney envious of Murat, Murat ahead on glory, both standing."""
    ney = MarshalFactory.infantry(name="Ney", location="Paris",
                                  strength=30000, personality="aggressive")
    murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                    strength=30000, personality="aggressive")
    world = WorldFactory.with_marshals([ney, murat], current_turn=5)
    return world, world.marshals["Ney"], world.marshals["Murat"]


# ════════════════════════════════════════════════════════════════════════
# (a) a resentment cannot cool and flare on the same page
# ════════════════════════════════════════════════════════════════════════

class TestNoSamePassRefire:
    def _arm(self, world, ney, murat):
        """Ney holds a grievance with one turn left; Murat is above him."""
        ney.jealous_of = "Murat"
        ney.jealousy_turns_remaining = 1
        ney.relationships["Murat"] = -1
        murat.relationships["Ney"] = -1
        J._append_glory(murat, world.current_turn, 6)

    def test_the_pair_that_cooled_does_not_re_fire_this_pass(self, feud):
        world, ney, murat = feud
        self._arm(world, ney, murat)
        events = _new_events(world)
        cooled = [e for e in events if e["type"] == "jealousy_resolved"]
        fired = [e for e in events if e["type"] == "jealousy_fired"]
        assert cooled, "the timer should have expired"
        assert not [e for e in fired if e.get("target") == "Murat"], (
            "the same page said the resentment cooled AND that it flared")
        assert ney.jealous_of is None

    def test_it_may_fire_again_on_a_LATER_pass(self, feud):
        """The suppression is one pass, not a cooldown. The quarrel is
        still real; it just does not resolve and re-arm on one page."""
        world, ney, murat = feud
        self._arm(world, ney, murat)
        _new_events(world)
        assert ney.jealous_of is None

        world.current_turn += 1
        _mark_processed_clear(world)
        _new_events(world)
        assert ney.jealous_of == "Murat"

    def test_the_flag_reproduces_the_prior_behaviour(self, feud, monkeypatch):
        """The flip-experiment discipline: disabling the flag restores the
        exact defect, which is what makes the BASELINE_SERIES attribution
        in `test_ai_intent_threat_migration.py` checkable."""
        world, ney, murat = feud
        monkeypatch.setattr(J, "JEALOUSY_SUPPRESS_SAME_PASS_REFIRE", False)
        self._arm(world, ney, murat)
        events = _new_events(world)
        assert [e for e in events if e["type"] == "jealousy_resolved"]
        assert [e for e in events if e["type"] == "jealousy_fired"
                and e.get("target") == "Murat"]
        assert ney.jealous_of == "Murat"

    def test_a_DIFFERENT_pair_may_still_fire_in_the_same_pass(self, feud):
        """Scoped to the pair, not to the turn or the nation. Another
        marshal's first grievance is real news and must not be eaten."""
        world, ney, murat = feud
        self._arm(world, ney, murat)
        davout = MarshalFactory.infantry(name="Davout", location="Paris",
                                         strength=30000,
                                         personality="aggressive")
        world.marshals["Davout"] = davout
        davout.relationships["Murat"] = -1
        murat.relationships["Davout"] = -1
        events = _new_events(world)
        fired = [e for e in events if e["type"] == "jealousy_fired"]
        assert any(e["marshal"] == "Davout" for e in fired), (
            "Davout's own grievance was suppressed by Ney's cooling")

    def test_the_same_marshal_may_take_a_DIFFERENT_rival_this_pass(self):
        """The unit of suppression is the PAIR, not the man.

        A quarrel that ends and a new one that begins are two different
        pieces of news; only "cooled and flared at the same man on the
        same page" is the contradiction. Widening the key to the envious
        marshal would silently eat the second, and a mutation sweep found
        nothing else in this file could tell the difference.
        """
        ney = MarshalFactory.infantry(name="Ney", location="Paris",
                                      personality="aggressive")
        murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                        personality="aggressive")
        davout = MarshalFactory.infantry(name="Davout", location="Paris",
                                         personality="cautious")
        world = WorldFactory.with_marshals([ney, murat, davout],
                                           current_turn=5)
        ney, murat, davout = (world.marshals["Ney"], world.marshals["Murat"],
                              world.marshals["Davout"])
        ney.jealous_of = "Murat"
        ney.jealousy_turns_remaining = 1        # cools this pass
        ney.relationships["Davout"] = -1        # hair-trigger toward Davout
        davout.relationships["Ney"] = -1
        J._append_glory(davout, world.current_turn, 8)   # far above Ney

        events = _new_events(world)
        assert ney.jealous_of == "Davout", (
            "Ney's quarrel with Murat ended and he could not take up a "
            "genuinely new one in the same pass")
        assert [e for e in events if e["type"] == "jealousy_fired"
                and e.get("target") == "Davout"]

    def test_the_suppression_does_not_burn_a_nation_fire_slot(self):
        """BEHAVIOURAL, not positional.

        A suppressed marshal must not consume one of his nation's
        `MAX_FIRES_PER_NATION_TURN` slots — the slot goes to the
        next-most-aggrieved man. Two earlier drafts of this pin were
        worthless: one compared the positions of two mentions inside
        COMMENTS, and the source-order version could not tell the
        difference between the gate sitting above the rate limit and it
        sitting one line below, which is behaviourally identical. Only
        placing the gate after the slot is CONSUMED is a real defect, and
        only counting fires detects it.

        Ney cools this pass (suppressed). Davout and Soult are both
        eligible. With the cap at 2, both must still fire.
        """
        murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                        personality="aggressive")
        ney = MarshalFactory.infantry(name="Ney", location="Paris",
                                      personality="aggressive")
        davout = MarshalFactory.infantry(name="Davout", location="Paris",
                                         personality="cautious")
        # NOT a `literal` — that personality routes through the
        # sidelining arm above the normal target path and would never
        # appear in the candidate list at all.
        lannes = MarshalFactory.infantry(name="Lannes", location="Paris",
                                         personality="aggressive")
        world = WorldFactory.with_marshals([ney, davout, lannes, murat],
                                           current_turn=5)
        assert J.MAX_FIRES_PER_NATION_TURN == 2
        m = world.marshals
        J._append_glory(m["Murat"], world.current_turn, 9)
        for name in ("Ney", "Davout", "Lannes"):
            m[name].relationships["Murat"] = -1
            m["Murat"].relationships[name] = -1
        m["Ney"].jealous_of = "Murat"
        m["Ney"].jealousy_turns_remaining = 1      # cools in step 1

        events = _new_events(world)
        fired = {e["marshal"] for e in events
                 if e["type"] == "jealousy_fired"}
        assert "Ney" not in fired
        assert fired == {"Davout", "Lannes"}, (
            f"Ney's suppressed re-fire ate a nation fire slot: {fired}")

    def test_a_forced_spiral_fire_is_never_suppressed(self):
        """Deliberate exclusion: the level-3 mutual spiral writes
        `jealous_of` on the TARGET through `_check_escalation`'s
        reciprocity arm. Suppressing that would break the ladder, not
        de-duplicate a sentence — so the gate lives in `process_turn`'s
        natural trigger loop, which never passes `forced=True`."""
        import inspect
        src = _strip_comments(inspect.getsource(J.process_turn))
        assert "forced=True" not in src
        assert "JEALOUSY_SUPPRESS_SAME_PASS_REFIRE" in src
        # ...and the forced writer is elsewhere, unguarded by the set.
        esc = _strip_comments(inspect.getsource(J._check_escalation))
        assert "cooled_this_pass" not in esc


# ════════════════════════════════════════════════════════════════════════
# (b) one trigger, one bullet
# ════════════════════════════════════════════════════════════════════════

class TestTheEscalationLineDoesNotEchoItsOwnFire:
    def test_a_fired_grievance_that_escalates_says_it_once(self, feud):
        world, ney, murat = feud
        ney.relationships["Murat"] = -1
        murat.relationships["Ney"] = -1
        events = []
        # Fire until the pair reaches level 1, capturing each pass. Q3(b)
        # makes that the SECOND fire on a Rival pair, which is exactly why
        # this loop is written to drive to the level rather than assume
        # which fire reaches it.
        for _ in range(4):
            if J.get_escalation_level(ney, "Murat") >= 1:
                break
            ney.jealous_of = None
            events = []
            J.apply_jealousy(world, ney, murat, 4, 1, events)
        assert J.get_escalation_level(ney, "Murat") >= 1

        fired = [e for e in events if e["type"] == "jealousy_fired"]
        level1 = [e for e in events if e["type"] == "jealousy_escalation"
                  and "matter of concern" in e.get("message", "")]
        assert fired, "the fire line is the one that survives"
        assert not level1, (
            "the level-1 escalation echoed the fire line that caused it")

    def test_levels_2_and_3_still_announce(self, feud):
        """"Entrenched" and "mutual" are new facts — level 2 additionally
        applies a permanent -1 in both directions — so they are NOT
        collapsed."""
        world, ney, murat = feud
        # `qualifies` (stored Rival-or-worse, or a 3rd lifetime fire) gates
        # the whole escalation body — without it `_check_escalation` returns
        # before the level is even computed.
        ney.relationships["Murat"] = -1
        murat.relationships["Ney"] = -1
        # Q3(b): a Rival pair qualifies on its SECOND fire, and
        # `apply_jealousy` appends the current one — so one prior fire in
        # the history is what makes the next call qualify.
        ney.jealousy_history.setdefault("Murat", []).append(0)
        J._set_escalation_level(ney, "Murat", 1)
        J._set_escalation_level(murat, "Ney", 1)
        ney.jealous_of = None
        events = []
        J.apply_jealousy(world, ney, murat, 4, 1, events)
        assert [e for e in events if e["type"] == "jealousy_escalation"
                and "entrenched" in e.get("message", "")]

    def test_a_silent_fire_still_gets_its_escalation_line(self, feud):
        """The suppression keys on whether the FIRE was announced, not on
        the level. If no fire line was shown, the escalation must speak."""
        world, ney, murat = feud
        ney.relationships["Murat"] = -1
        # Q3(b): `_check_escalation` is called DIRECTLY here, so the
        # history must already carry the fire that production would have
        # appended — two entries for a Rival pair's qualifying moment.
        ney.jealousy_history.setdefault("Murat", []).extend([0, 0])
        events = []
        J._check_escalation(world, ney, murat, events, fire_announced=False)
        assert [e for e in events if e["type"] == "jealousy_escalation"
                and "matter of concern" in e.get("message", "")]

    def test_the_q1b_hold_arm_is_untouched(self, feud):
        """`3f8468c` landed the Emperor's promise as an escalation HOLD.
        A12 must not silence it — it is the one arm that reports the
        player's paid choice working."""
        world, ney, murat = feud
        ney.relationships["Murat"] = -1
        ney.jealousy_history.setdefault("Murat", []).extend([0, 0])
        ney.jealousy_escalation_hold["Murat"] = world.current_turn + 3
        events = []
        J._check_escalation(world, ney, murat, events, fire_announced=True)
        held = [e for e in events if e.get("held")]
        assert held, "the hold beat was collapsed with the level-1 line"


# ════════════════════════════════════════════════════════════════════════
# (c) Berthier names the worst quarrel, not the first-listed one
# ════════════════════════════════════════════════════════════════════════

class TestTheNoteRanksTheGrievances:
    @pytest.fixture()
    def three(self):
        """Insertion order Ney, Davout, Soult — but SOULT is the worst."""
        ney = MarshalFactory.infantry(name="Ney", location="Paris",
                                      personality="aggressive")
        davout = MarshalFactory.infantry(name="Davout", location="Paris",
                                         personality="cautious")
        soult = MarshalFactory.infantry(name="Soult", location="Paris",
                                        personality="literal")
        murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                        personality="aggressive")
        world = WorldFactory.with_marshals([ney, davout, soult, murat],
                                           current_turn=9)
        for m in ("Ney", "Davout", "Soult"):
            world.marshals[m].jealous_of = "Murat"
        J._set_escalation_level(world.marshals["Soult"], "Murat", 3)
        J._set_escalation_level(world.marshals["Davout"], "Murat", 1)
        return world

    # The rungs ABOVE 3.5 must not pre-empt it: no broken marshal, no
    # bankruptcy, no treasury bleed. `status`/`strength` are required keys
    # (rung 1 subscripts them) — an incomplete payload raises, which is how
    # the first draft of this file discovered it was testing nothing.
    SITUATION = {"bankrupt": False, "treasury_delta": 100}

    def _note(self, world, idle=0):
        data = [{"name": m.name, "status": "normal", "strength": 30000,
                 "idle_turns": idle}
                for m in world.marshals.values()]
        return _pick_berthier_note(world, "France", data,
                                   dict(self.SITUATION))

    def test_the_rung_is_actually_reached(self, three):
        """POSITIVE-REACH PIN. The whole rung sits in a bare
        `try/except: pass`, so any error inside it — an import, a bad
        ranking key — silently falls through to rung 4 and the suite
        stays green. Nothing asserted this before."""
        note = self._note(three)
        assert "grievance" in note or "rivalries" in note, note

    def test_the_worst_quarrel_is_named_first(self, three):
        note = self._note(three)
        assert "Soult" in note
        assert note.index("Soult") < note.index("Davout"), note

    def test_dict_order_does_not_decide(self, three):
        """Ney is FIRST in insertion order and has the mildest quarrel
        (level 0). He must not lead the sentence."""
        note = self._note(three)
        assert not note.startswith("Ney"), note
        assert "Soult" in note

    def test_the_dead_singular_branch_is_gone(self, three):
        """`nurse{'s' if len(jealous) == 1 ...}` sat below two `len == 1`
        returns and could never render the singular."""
        note = self._note(three)
        assert "nurses a grievance" not in note or "Sire." in note
        assert "nurse a grievance" in note

    def test_a_lone_grievance_still_takes_the_singular_arm(self):
        ney = MarshalFactory.infantry(name="Ney", location="Paris",
                                      personality="aggressive")
        murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                        personality="aggressive")
        world = WorldFactory.with_marshals([ney, murat], current_turn=9)
        world.marshals["Ney"].jealous_of = "Murat"
        note = self._note(world)
        assert "Ney nurses a grievance against Murat" in note, note

    def test_the_idle_arm_survives(self):
        """CA8-8's best line — "he nurses a grievance and has stood idle
        four turns; those are the same fact"."""
        ney = MarshalFactory.infantry(name="Ney", location="Paris",
                                      personality="aggressive")
        murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                        personality="aggressive")
        world = WorldFactory.with_marshals([ney, murat], current_turn=9)
        world.marshals["Ney"].jealous_of = "Murat"
        data = [{"name": "Ney", "status": "normal", "strength": 30000,
                 "idle_turns": 5},
                {"name": "Murat", "status": "normal", "strength": 30000,
                 "idle_turns": 0}]
        note = _pick_berthier_note(world, "France", data,
                                   dict(self.SITUATION))
        assert "the same fact" in note, note
