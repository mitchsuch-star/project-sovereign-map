"""CA9 row 3 / Q3(b) — a first grievance gets a first act.

Audit record: `docs/audits/GRIEVANCE_REVISIT_INVESTIGATION_2026_08_09.md`
§5 Q3, ruled (b).

`_check_escalation` qualified on `stored_rel <= -1 or fires >= 3`. On the
authored 1805 board 14 of the 18 negative directed French edges sit at
Rival, so the player's very FIRST card on nearly every quarrel opened at
escalation 1 — *"The staff now speak of the quarrel openly — this is no
longer a passing mood."* — about a resentment one turn old. The mild
register existed in the code and was unreachable in play.

The ruling required ONE change that moves three things together: the
level, the card's escalation register, and the `pair@L{level}` petition
latch. It is one predicate, because the register and the latch are both
DERIVED from the level.

A stored HOSTILE pair still escalates on sight — those men have a history
the campaign did not invent (Davout–Bernadotte is the Auerstedt no-show).
"""

import pytest

from backend.game_logic import jealousy as J

from tests.conftest import MarshalFactory, WorldFactory


@pytest.fixture()
def pair():
    ney = MarshalFactory.infantry(name="Ney", location="Paris",
                                  strength=30000, personality="aggressive")
    murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                    strength=30000, personality="aggressive")
    world = WorldFactory.with_marshals([ney, murat], current_turn=3)
    return world, world.marshals["Ney"], world.marshals["Murat"]


def _fire(world, marshal, target):
    """One complete fire through the production path (which appends the
    history entry BEFORE `_check_escalation` reads it)."""
    events = []
    marshal.jealous_of = None
    J.apply_jealousy(world, marshal, target, delta=2, threshold=1,
                     events=events)
    return events


# ════════════════════════════════════════════════════════════════════════
# The rule
# ════════════════════════════════════════════════════════════════════════

class TestTheRule:
    def test_a_rival_pairs_first_fire_does_not_escalate(self, pair):
        world, ney, murat = pair
        ney.set_relationship("Murat", -1)
        murat.set_relationship("Ney", -1)
        _fire(world, ney, murat)
        assert J.get_escalation_level(ney, "Murat") == 0

    def test_the_second_fire_does(self, pair):
        world, ney, murat = pair
        ney.set_relationship("Murat", -1)
        murat.set_relationship("Ney", -1)
        _fire(world, ney, murat)
        J.clear_jealousy(world, ney, resolved_by_action=False)
        _fire(world, ney, murat)
        assert J.get_escalation_level(ney, "Murat") == 1

    def test_a_hostile_pair_still_escalates_on_sight(self, pair):
        """The exemption, and the reason this is a narrowing rather than a
        blanket delay: an authored Hostile pair has a history."""
        world, ney, murat = pair
        ney.set_relationship("Murat", -2)
        murat.set_relationship("Ney", -2)
        _fire(world, ney, murat)
        assert J.get_escalation_level(ney, "Murat") == 1

    def test_a_professional_pair_is_unchanged(self, pair):
        """Stored 0 still needs three lifetime fires — untouched."""
        world, ney, murat = pair
        for _ in range(2):
            _fire(world, ney, murat)
            assert J.get_escalation_level(ney, "Murat") == 0
            J.clear_jealousy(world, ney, resolved_by_action=False)
        _fire(world, ney, murat)
        assert J.get_escalation_level(ney, "Murat") == 1

    def test_the_constants_say_what_the_rule_is(self):
        assert J.ESCALATION_RIVAL_FIRES == 2
        assert J.ESCALATION_IMMEDIATE_RELATIONSHIP == -2
        assert J.ESCALATION_LIFETIME_FIRES == 3


# ════════════════════════════════════════════════════════════════════════
# All three surfaces move together — the ruling's actual requirement
# ════════════════════════════════════════════════════════════════════════

class TestTheCardOpensInTheMildRegister:
    def _card(self, world, marshal, target):
        world.pending_marshal_petition = None
        J.queue_confrontation_petition(
            world, marshal, target,
            J.get_escalation_level(marshal, target.name))
        return world.pending_marshal_petition

    def test_the_first_card_does_not_announce_an_entrenched_feud(self, pair):
        world, ney, murat = pair
        ney.set_relationship("Murat", -1)
        murat.set_relationship("Ney", -1)
        _fire(world, ney, murat)
        body = self._card(world, ney, murat)["body"]
        assert "no longer a passing mood" not in body, body

    def test_the_second_card_does(self, pair):
        world, ney, murat = pair
        ney.set_relationship("Murat", -1)
        murat.set_relationship("Ney", -1)
        _fire(world, ney, murat)
        J.clear_jealousy(world, ney, resolved_by_action=False)
        _fire(world, ney, murat)
        body = self._card(world, ney, murat)["body"]
        assert "no longer a passing mood" in body, body

    def test_the_latch_moves_with_the_level(self, pair):
        """The `pair@L{level}` key is derived from the level READ AFTER
        `_check_escalation`, so a first fire now latches L0 and leaves L1
        available for the recurrence. That is what buys the extra
        audience, and it needed no separate wiring."""
        world, ney, murat = pair
        ney.set_relationship("Murat", -1)
        murat.set_relationship("Ney", -1)
        ney.nation = world.player_nation
        murat.nation = world.player_nation
        _fire(world, ney, murat)
        seen = set(getattr(world, "jealousy_confrontations_seen", []) or [])
        assert any(k.endswith("@L0") for k in seen), seen
        assert not any(k.endswith("@L1") for k in seen), seen


# ════════════════════════════════════════════════════════════════════════
# The rejected variant, and why
# ════════════════════════════════════════════════════════════════════════

class TestTheRejectedVariantWouldHaveBeenInert:
    def test_the_history_already_holds_the_current_fire(self, pair):
        """Memo §6 #5: the variant that gates the level-1 ANNOUNCEMENT on
        `fires >= 2` is inert AND backwards, because `apply_jealousy`
        appends to `jealousy_history` BEFORE `_check_escalation` runs — so
        fire 1 already reads a lifetime count of 1, and gating on >= 2
        would make the MILD announcement unreachable while leaving "the
        wound will not close on its own" as the player's first spoken
        escalation. The real seam is the qualifier, which is what moved.
        """
        world, ney, murat = pair
        ney.set_relationship("Murat", -1)
        seen = {}

        real = J._check_escalation

        def spy(w, m, t, ev, forced=False, fire_announced=False):
            seen["fires_at_check_time"] = J._lifetime_fires(m, t.name)
            return real(w, m, t, ev, forced=forced,
                        fire_announced=fire_announced)

        J._check_escalation = spy
        try:
            _fire(world, ney, murat)
        finally:
            J._check_escalation = real
        assert seen["fires_at_check_time"] == 1


# ════════════════════════════════════════════════════════════════════════
# Knock-ons the pre-build refutation named — pinned, not discovered later
# ════════════════════════════════════════════════════════════════════════

class TestKnownConsequences:
    def test_the_q1b_hold_needs_a_qualifying_fire(self, pair):
        """`qualifies` returns ABOVE the hold check, so on a Rival pair's
        first fire the "he holds to the Emperor's word" beat is not
        reached — there is nothing yet to hold. It fires from the second
        fire onward. Named here so it is not filed later as a Q1(b)
        regression."""
        world, ney, murat = pair
        ney.set_relationship("Murat", -1)
        murat.set_relationship("Ney", -1)
        ney.nation = murat.nation = world.player_nation
        ney.jealousy_escalation_hold["Murat"] = world.current_turn + 3

        first = _fire(world, ney, murat)
        assert not [e for e in first if e.get("held")]

        J.clear_jealousy(world, ney, resolved_by_action=False)
        second = _fire(world, ney, murat)
        assert [e for e in second if e.get("held")], (
            "the hold beat must be reachable from the second fire")

    def test_tier_2_permanent_damage_is_merely_delayed_not_removed(self, pair):
        """Delaying the level also delays the tier-2
        `modify_relationship(-1)` that hardens a pair to Hostile. The
        mechanic is unchanged; it arrives one fire later."""
        world, ney, murat = pair
        ney.set_relationship("Murat", -1)
        murat.set_relationship("Ney", -1)
        for _ in range(2):
            _fire(world, ney, murat)
            J.clear_jealousy(world, ney, resolved_by_action=False)
        before = ney.relationships.get("Murat", 0)
        _fire(world, ney, murat)
        assert J.get_escalation_level(ney, "Murat") == 2
        assert ney.relationships.get("Murat", 0) == before - 1
