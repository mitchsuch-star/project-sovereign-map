"""CA9 row 3 / Phase A — the grievance channel stops lying and stops nagging.

Audit record: `docs/audits/GRIEVANCE_REVISIT_INVESTIGATION_2026_08_09.md`
(authoritative). A1 (the "Later" soft-lock) is pinned separately in
`test_ca9_row3_a1_petition_later.py`.

Covered here:

* **A2** — `clear_jealousy`'s non-action branch reads its own `reason`. A
  grievance ended by the Emperor's paid promise, by a rebuke costing 5 trust,
  and by the rival being ridden down all printed *"cooled with time"*. Both
  CA8-8 pins must survive, so the cause is a CLAUSE inside the existing
  three-variant ladder, not a fourth variant.
* **A3** — the stale-answer guard. CA9-N4's fixable half: a card queued on
  turn 11 and answered on turn 16 spent AP and applied trust to a quarrel
  that was already over, and reported success.
* **A4** — the war_weary producer stops destroying a pending confrontation,
  and stops burning its once-per-pair promise on a push it never made.
* **A9** — "Separate Them" gets a retirement path and a cooldown. It was
  written True in one place and False in NO place anywhere in `backend/`.
* **A10** — four dynamic `_`-prefixed latches become declared, serialized
  fields. They escaped `test_serialization_enforcement.py` because it filters
  `_` names out of the field set it derives; the rename is what makes the
  coverage structural rather than a bespoke pin.
"""

import pytest

from backend.game_logic import jealousy as J
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState

from tests.conftest import MarshalFactory, WorldFactory


def _new_events(world):
    """Only the events THIS pass appended.

    `jealousy.process_turn` writes into a PERSISTENT list on the world
    (`_pending_jealousy_turn_events`, via `_pending_events`) which
    `advance_turn` collects and clears. Calling `process_turn` twice in a
    test and reading its return value therefore hands you turn 1's events
    again — which made the cooldown pin below fail while the cooldown was
    working perfectly. Read the delta.
    """
    prior = len(J._pending_events(world))
    J.process_turn(world)
    return J._pending_events(world)[prior:]


@pytest.fixture()
def pair():
    """Murat envious of Davout, both standing, France the player."""
    murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                   strength=30000, personality="aggressive")
    davout = MarshalFactory.infantry(name="Davout", location="Paris",
                                     strength=30000, personality="cautious")
    world = WorldFactory.with_marshals([murat, davout])
    return world, world.marshals["Murat"], world.marshals["Davout"]


# ════════════════════════════════════════════════════════════════════════
# A2 — the cooling names its cause
# ════════════════════════════════════════════════════════════════════════

class TestA2CoolingNamesItsCause:
    def _cool(self, world, marshal, reason):
        marshal.jealous_of = "Davout"
        events = []
        J.clear_jealousy(world, marshal, resolved_by_action=False,
                         events=events, reason=reason)
        return next(e for e in events if e["type"] == "jealousy_resolved")

    def test_the_promise_is_not_narrated_as_patience(self, pair):
        world, murat, _ = pair
        line = self._cool(world, murat, "the Emperor's promise")["message"]
        assert "cooled with time" not in line, line
        assert "your word" in line, line

    def test_the_rebuke_is_not_narrated_as_patience(self, pair):
        world, murat, _ = pair
        line = self._cool(world, murat, "the Emperor's rebuke")["message"]
        assert "cooled with time" not in line, line
        assert "rebuke" in line, line

    def test_a_dead_rival_is_not_narrated_as_patience(self, pair):
        world, murat, _ = pair
        line = self._cool(world, murat, "the rival is gone")["message"]
        assert "cooled with time" not in line, line
        assert "no one left to envy" in line, line

    def test_the_three_causes_are_distinguishable(self, pair):
        """The point of A2. If two arms print the same sentence the player
        still cannot tell what their action bought."""
        world, murat, _ = pair
        lines = set()
        for reason in ("the Emperor's promise", "the Emperor's rebuke",
                       "the rival is gone", "time"):
            murat.jealous_of = "Davout"
            lines.add(self._cool(world, murat, reason)["message"])
        assert len(lines) == 4, lines

    def test_time_is_byte_identical_to_before(self, pair):
        """CA8-8 pin, restated locally: an ordinary pair cooling on the timer
        must still read exactly 'cooled with time'."""
        world, murat, _ = pair
        line = self._cool(world, murat, "time")["message"]
        assert "cooled with time" in line, line

    def test_an_unknown_reason_falls_through_to_the_old_wording(self, pair):
        """Every legacy or future caller that passes something unmapped keeps
        today's behaviour rather than printing a bare sentence fragment."""
        world, murat, _ = pair
        line = self._cool(world, murat, "some future reason")["message"]
        assert "cooled with time" in line, line

    def test_entrenched_outranks_the_cause(self, pair):
        """CA8-8's other pin: a pair the game called permanent must still be
        told its standing has NOT cooled, whatever ended the timer."""
        world, murat, davout = pair
        J._set_escalation_level(murat, "Davout", J.ESCALATION_PERMANENT_LEVEL)
        line = self._cool(world, murat, "the Emperor's promise")["message"]
        assert "has not been" in line, line
        assert "cooled with time" not in line, line


class TestA13Discriminator:
    """A2 also lays A13's prerequisite: an EARNED resolution and a timer
    expiry were both `jealousy_resolved` with no way to tell them apart, so a
    narration cap could not exempt the beat and collapse the noise."""

    def test_an_earned_resolution_is_flagged(self, pair):
        world, murat, davout = pair
        murat.jealous_of = "Davout"
        events = []
        J.clear_jealousy(world, murat, resolved_by_action=True,
                         events=events, reason="he has proven himself")
        ev = next(e for e in events if e["type"] == "jealousy_resolved")
        assert ev["by_action"] is True

    def test_a_timer_expiry_is_flagged(self, pair):
        world, murat, _ = pair
        murat.jealous_of = "Davout"
        events = []
        J.clear_jealousy(world, murat, resolved_by_action=False,
                         events=events, reason="time")
        ev = next(e for e in events if e["type"] == "jealousy_resolved")
        assert ev["by_action"] is False

    def test_no_new_campaign_log_type_was_added(self):
        """A key on an existing event, per the house pattern — the type count
        is pinned in five files."""
        from backend.campaign_log import CAMPAIGN_LOG_TYPES
        assert len(CAMPAIGN_LOG_TYPES) == 160  # 157->158 flipped consciously: PC15-1 adds `marshal_destroyed`  # 158->160 flipped consciously: WIN-D3 adds `evacuation_granted` + `evacuation_lapsing` (internment itself reuses PC15-1's `marshal_destroyed` with cause="interned").


# ════════════════════════════════════════════════════════════════════════
# A3 — the stale-answer guard
# ════════════════════════════════════════════════════════════════════════

class TestA3StaleAnswerGuard:
    def _queue(self, world, murat, davout):
        J.queue_confrontation_petition(world, murat, davout, level=0)
        return world.pending_marshal_petition

    def test_a_stale_promise_spends_nothing(self, pair):
        world, murat, davout = pair
        murat.jealous_of = "Davout"
        murat.jealousy_turns_remaining = 4
        self._queue(world, murat, davout)
        # The quarrel ends before the player answers.
        murat.jealous_of = None
        ap_before = world.actions_remaining
        result = J.handle_petition_response(world, "promise")
        assert world.actions_remaining == ap_before, "AP was spent on a "\
            "quarrel that was already over"
        assert "already behind him" in result["message"]

    def test_a_stale_rebuke_docks_no_trust(self, pair):
        world, murat, davout = pair
        murat.jealous_of = "Davout"
        murat.jealousy_turns_remaining = 4
        self._queue(world, murat, davout)
        murat.jealous_of = None
        trust_before = murat.trust.value
        J.handle_petition_response(world, "rebuke")
        assert murat.trust.value == trust_before, "trust was docked for a "\
            "quarrel that was already over"

    def test_the_card_is_retired_not_re_served(self, pair):
        """A card whose subject has changed must not go back on the queue —
        re-pushing is how the memo's turn-4-to-41 zombie happened."""
        world, murat, davout = pair
        murat.jealous_of = "Davout"
        self._queue(world, murat, davout)
        murat.jealous_of = None
        J.handle_petition_response(world, "promise")
        assert world.pending_marshal_petition is None

    def test_a_grievance_against_a_DIFFERENT_man_is_also_stale(self, pair):
        """The guard compares the card's target to the live one, not merely
        'is he still jealous of somebody'."""
        world, murat, davout = pair
        murat.jealous_of = "Davout"
        murat.jealousy_turns_remaining = 4
        self._queue(world, murat, davout)
        murat.jealous_of = "Soult"      # rival memory re-fixed elsewhere
        ap_before = world.actions_remaining
        J.handle_petition_response(world, "promise")
        assert world.actions_remaining == ap_before

    def test_a_LIVE_answer_still_works(self, pair):
        """FALSIFIABLE NEGATIVE. Without this the guard could reject
        everything and every test above would still pass."""
        world, murat, davout = pair
        murat.jealous_of = "Davout"
        murat.jealousy_turns_remaining = 4
        self._queue(world, murat, davout)
        ap_before = world.actions_remaining
        result = J.handle_petition_response(world, "promise")
        assert result["success"] is True
        assert world.actions_remaining < ap_before, "the live path stopped "\
            "spending AP — the guard is rejecting valid answers"
        assert murat.jealousy_turns_remaining < 4

    def test_the_guard_is_scoped_to_the_confrontation_kind(self):
        """DELIBERATE: `war_weary` carries the assembled declare-war command
        in its context, so retiring one of those on a mismatch would silently
        cancel a war declaration — worse than the bug being fixed."""
        import inspect
        src = inspect.getsource(J._apply_confrontation_choice)
        assert "already behind him" in src
        for other in (J._apply_war_weary_choice, J._apply_rivalry_choice,
                      J._apply_fontainebleau_choice):
            assert "already behind him" not in inspect.getsource(other), (
                f"{other.__name__} grew a stale guard — read A3's note first")


# ════════════════════════════════════════════════════════════════════════
# A9 — the separation subscription can be retired, and stops nagging
# ════════════════════════════════════════════════════════════════════════

class TestA9SeparationRetirementAndCooldown:
    def _flagged(self, world, murat, davout, stored=-1):
        murat.set_relationship("Davout", stored)
        davout.set_relationship("Murat", stored)
        murat.separation_flagged["Davout"] = True
        davout.separation_flagged["Murat"] = True

    def test_the_first_proximity_warns(self, pair):
        world, murat, davout = pair
        self._flagged(world, murat, davout)
        events = _new_events(world)
        assert any(e["type"] == "jealousy_separation_warning" for e in events), \
            [e["type"] for e in events]

    def test_a_mended_rivalry_retires_the_subscription(self, pair):
        world, murat, davout = pair
        self._flagged(world, murat, davout)
        # Mediation succeeded: stored standing is back to professional.
        murat.set_relationship("Davout", 0)
        davout.set_relationship("Murat", 0)
        events = _new_events(world)
        assert "Davout" not in murat.separation_flagged
        assert "Murat" not in davout.separation_flagged
        assert any("closes the file" in e.get("message", "") for e in events)

    def test_a_live_grievance_does_not_retire_it(self, pair):
        """The retirement reads STORED standing. `get_relationship` subtracts
        1 for a live grievance, so using the derived getter would keep the
        file open forever on exactly the pairs the player wants closed — and
        conversely must not close it while the rivalry itself stands."""
        world, murat, davout = pair
        self._flagged(world, murat, davout, stored=-1)
        murat.jealous_of = "Davout"
        _new_events(world)
        assert murat.separation_flagged.get("Davout") is True

    def test_the_warning_has_a_cooldown(self, pair):
        world, murat, davout = pair
        self._flagged(world, murat, davout)
        first = _new_events(world)
        assert any(e["type"] == "jealousy_separation_warning" for e in first)
        # Same turn / next turn, still adjacent: silent.
        world.current_turn += 1
        again = _new_events(world)
        assert not any(e["type"] == "jealousy_separation_warning"
                       for e in again), "the per-turn nag is back"

    def test_it_warns_again_after_the_cooldown(self, pair):
        world, murat, davout = pair
        self._flagged(world, murat, davout)
        _new_events(world)
        world.current_turn += J.SEPARATION_WARNING_COOLDOWN
        later = _new_events(world)
        assert any(e["type"] == "jealousy_separation_warning" for e in later), \
            "the subscription stopped working entirely"




# ════════════════════════════════════════════════════════════════════════
# A10 — the four latches are real fields now
# ════════════════════════════════════════════════════════════════════════

class TestA10LatchesSerialize:
    def test_marshal_latches_round_trip(self):
        m = MarshalFactory.infantry(name="Ney", personality="aggressive")
        m.jealousy_rebuked_cycle = True
        m.literal_intel_paused_turn = 7
        m.separation_flagged["Davout"] = True
        m.separation_warned_turn["Davout"] = 5
        back = Marshal.from_dict(m.to_dict())
        assert back.jealousy_rebuked_cycle is True
        assert back.literal_intel_paused_turn == 7
        assert back.separation_warned_turn == {"Davout": 5}

    def test_marshal_latch_defaults_on_a_legacy_save(self):
        m = MarshalFactory.infantry(name="Ney")
        data = m.to_dict()
        for key in ("jealousy_rebuked_cycle", "literal_intel_paused_turn",
                    "separation_warned_turn"):
            data.pop(key, None)
        back = Marshal.from_dict(data)
        assert back.jealousy_rebuked_cycle is False
        assert back.literal_intel_paused_turn == -1
        assert back.separation_warned_turn == {}

    def test_world_latches_round_trip(self):
        world = WorldFactory.basic()
        world.war_weary_petitions_seen = {"Ney|Prussia", "Davout|Austria"}
        world.fontainebleau_armed = False
        back = WorldState.from_dict(world.to_dict())
        assert back.war_weary_petitions_seen == {"Ney|Prussia",
                                                "Davout|Austria"}
        assert back.fontainebleau_armed is False

    def test_world_latch_defaults_on_a_legacy_save(self):
        world = WorldFactory.basic()
        data = world.to_dict()
        data.pop("war_weary_petitions_seen", None)
        data.pop("fontainebleau_armed", None)
        back = WorldState.from_dict(data)
        assert back.war_weary_petitions_seen == set()
        assert back.fontainebleau_armed is True, (
            "the Fontainebleau latch must boot ARMED — the pre-A10 code read "
            "`getattr(world, ..., True)`")

    def test_the_seen_set_is_saved_sorted(self):
        """A set's iteration order is not stable (str hashing is randomised
        per process), so an unsorted dump makes every save byte-different for
        no reason.

        Ten elements, deliberately: with three, a plain `list(set)` matches
        sorted order by chance often enough that this pin survived the
        mutation that removed `sorted()`. At ten the odds are ~1 in 3.6
        million, which is the difference between a pin and a coin flip.
        """
        world = WorldFactory.basic()
        keys = {f"{c}|N{i}" for i, c in enumerate("jcahfbeidg")}
        world.war_weary_petitions_seen = set(keys)
        dumped = world.to_dict()["war_weary_petitions_seen"]
        assert dumped == sorted(keys)

    def test_none_of_the_four_is_underscore_prefixed_any_more(self):
        """The rename is the load-bearing half: `test_serialization_
        enforcement.py` derives its field set from `vars()` and filters
        `_`-prefixed names, which is exactly how all four hid. If any of
        these regains its underscore it leaves that net again."""
        m = MarshalFactory.infantry(name="Ney")
        world = WorldFactory.basic()
        assert "jealousy_rebuked_cycle" in vars(m)
        assert "literal_intel_paused_turn" in vars(m)
        assert "war_weary_petitions_seen" in vars(world)
        assert "fontainebleau_armed" in vars(world)
        for dead in ("_jealousy_rebuked_cycle", "_literal_intel_paused_turn"):
            assert dead not in vars(m)
        for dead in ("_war_weary_petitions_seen", "_fontainebleau_armed"):
            assert dead not in vars(world)
