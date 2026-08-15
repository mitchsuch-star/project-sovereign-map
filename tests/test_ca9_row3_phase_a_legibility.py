"""CA9 row 3 / Phase A batch 2 — the quarrel is named where it bites.

Audit record: `docs/audits/GRIEVANCE_REVISIT_INVESTIGATION_2026_08_09.md` §4.

The audit's headline measurement: an active grievance takes committed
strength from **24,840 to 0** and a win rate from **7/8 to 1/8**, and that
consequence was named on **no surface anywhere**. These three items put it on
the three surfaces that decide, report and depict a battle.

* **A5** — the muster preview stops lying. Two holes: a co-located
  derived-hostile marshal was listed as sharing the field AND promised to
  absorb casualties, while `_get_casualty_participants` drops him outright;
  and a marshal who marches but withholds had no word said about him at all.
  The contribution scale is now ONE source (`_pair_contribution_scale`,
  extracted from `_committed_reinforcement_strength`) that the preview CALLS.
* **A6** — a grievance-driven no-show is attributed to ambition, not to the
  roads. Reclassified out of `low_score`, with the Session-61a trust dock
  left byte-identical on purpose.
* **A8** — the rivalry petition is queued from the man who is actually
  aggrieved, and Berthier stops congratulating the player on a thaw that
  never landed.

**`TestBandInvariance` is the load-bearing safety pin.** Row 2 (`075982e`)
scopes the attack-confirm modal to an `unfavorable` band, so if A5 moved the
band or the committed figure it would silently re-arm or disarm that gate.
It does not, and this proves it rather than asserting it.
"""

import pytest

from backend.commands.combat_executor import CombatExecutor
from backend.commands.executor import CommandExecutor
from backend.display_names import MUSTER_REASON_DISPLAY
from backend.game_logic import jealousy as J

from tests.conftest import MarshalFactory, WorldFactory


def _war(world, a="France", b="Austria"):
    key = "|".join(sorted([a, b]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn


@pytest.fixture()
def field():
    """Ney leads at Belgium, Murat stands beside him, Mack opposes."""
    ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                 strength=24000, personality="aggressive")
    murat = MarshalFactory.infantry(name="Murat", location="Belgium",
                                    strength=24000, personality="aggressive")
    mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                nation="Austria", strength=30000)
    world = WorldFactory.with_marshals([ney, murat, mack])
    _war(world)
    world.calculate_visibility()
    ex = CommandExecutor()
    return world, ex, world.marshals["Ney"], world.marshals["Murat"], \
        world.marshals["Mack"]


def _preview(ex, world, lead, enemy):
    return ex._combat._build_muster_preview(lead, enemy, world,
                                            {"world": world})


def _row(preview, name):
    return next(r for r in preview["rows"] if r["marshal"] == name)


# ════════════════════════════════════════════════════════════════════════
# A5 — the scale is one source, and the preview reads it
# ════════════════════════════════════════════════════════════════════════

class TestA5OneSourceForTheScale:
    def test_the_scale_helper_matches_the_committed_math(self, field):
        """`_pair_contribution_scale` was EXTRACTED from
        `_committed_reinforcement_strength`, so a hostile pair must still
        drive the committed figure to zero through the real function."""
        world, ex, ney, murat, _ = field
        murat.set_relationship("Ney", -2)
        ney.set_relationship("Murat", -2)
        assert ex._combat._pair_contribution_scale(ney, murat) == 0.0
        assert ex._combat._committed_reinforcement_strength(
            ney, [ney, murat], world) == 0.0

    def test_an_aggressive_grievance_is_a_hard_zero(self, field):
        world, ex, ney, murat, _ = field
        murat.jealous_of = "Ney"
        assert murat.personality == "aggressive"
        assert ex._combat._pair_contribution_scale(ney, murat) == 0.0

    def test_a_cautious_grievance_is_half_not_nothing(self, field):
        world, ex, ney, murat, _ = field
        murat.personality = "cautious"
        murat.jealous_of = "Ney"
        assert ex._combat._pair_contribution_scale(ney, murat) == 0.50

    def test_a_clean_pair_is_full_weight(self, field):
        world, ex, ney, murat, _ = field
        assert ex._combat._pair_contribution_scale(ney, murat) == 1.0


class TestA5TheCoLocatedHole:
    def test_a_hostile_neighbour_is_not_promised_as_a_fighter(self, field):
        world, ex, ney, murat, mack = field
        murat.set_relationship("Ney", -2)
        preview = _preview(ex, world, ney, mack)
        row = _row(preview, "Murat")
        assert row["will_join"] is False
        assert row["reason"] == "shares_the_field_apart"

    def test_and_the_casualty_promise_is_withdrawn(self, field):
        """The specific lie: `_get_casualty_participants` DROPS him, so
        'his men will absorb part of any losses' was false."""
        world, ex, ney, murat, mack = field
        murat.set_relationship("Ney", -2)
        preview = _preview(ex, world, ney, mack)
        assert preview["shared_casualty_note"] == ""

    def test_a_written_support_order_restores_him(self, field):
        """Same SUPPORT exemption `_get_casualty_participants` uses — the two
        must not disagree, which is the whole point of siting it here."""
        from backend.models.marshal import StrategicOrder
        world, ex, ney, murat, mack = field
        murat.set_relationship("Ney", -2)
        murat.strategic_order = StrategicOrder(
            "SUPPORT", "Ney", "marshal", world.current_turn, "Murat, support Ney")
        preview = _preview(ex, world, ney, mack)
        row = _row(preview, "Murat")
        assert row["will_join"] is True
        assert row["reason"] == "shares_the_field"
        assert "absorb part of any losses" in preview["shared_casualty_note"]

    def test_a_clean_neighbour_still_shares_the_field(self, field):
        """FALSIFIABLE NEGATIVE: without this the new arm could be firing for
        everyone and every test above would still pass."""
        world, ex, ney, murat, mack = field
        preview = _preview(ex, world, ney, mack)
        row = _row(preview, "Murat")
        assert row["will_join"] is True
        assert row["reason"] == "shares_the_field"

    def test_the_display_string_has_no_raw_placeholder(self):
        """`MUSTER_REASON_DISPLAY` is consumed as `.get(code, code)`, so a
        `{placeholder}` would render its braces to the player."""
        text = MUSTER_REASON_DISPLAY["shares_the_field_apart"]
        assert "{" not in text and "}" not in text
        assert text and not text.startswith("shares_the_field_apart")


class TestA5TheWithholdingRow:
    def test_a_zero_contributor_is_named_as_bringing_nothing(self, field):
        world, ex, ney, murat, mack = field
        # Adjacent, not co-located, so he is a genuine reinforcer.
        murat.location = "Paris"
        murat.jealous_of = "Ney"           # aggressive -> hard 0.0
        preview = _preview(ex, world, ney, mack)
        row = _row(preview, "Murat")
        assert row["will_join"] is True, "will_join must NOT flip — it feeds "\
            "the odds band"
        assert "NOTHING" in row.get("withholds", "")

    def test_a_half_contributor_is_named_as_half(self, field):
        world, ex, ney, murat, mack = field
        murat.location = "Paris"
        murat.personality = "cautious"
        murat.jealous_of = "Ney"           # non-aggressive -> x0.5
        preview = _preview(ex, world, ney, mack)
        row = _row(preview, "Murat")
        assert "half" in row.get("withholds", "")

    def test_a_clean_reinforcer_says_nothing_extra(self, field):
        world, ex, ney, murat, mack = field
        murat.location = "Paris"
        preview = _preview(ex, world, ney, mack)
        assert "withholds" not in _row(preview, "Murat")

    def test_the_line_renders_the_withholding(self, field):
        world, ex, ney, murat, mack = field
        murat.location = "Paris"
        murat.jealous_of = "Ney"
        preview = _preview(ex, world, ney, mack)
        text = ex._combat._format_muster_lines(preview)
        assert "NOTHING" in text, text


class TestA5TheBadOddsNote:
    def test_a_withholder_is_not_named_in_the_promise(self, field):
        """The CR-5 modal named everyone who 'would answer the guns' and then
        printed a joint figure that already excluded the withholder.

        A CLEAN reinforcer is added deliberately. With the withholder alone,
        `committed <= 0` makes the note empty and 'Murat not in ""' passes
        whether the filter exists or not — which is exactly how the first
        draft of this test survived a mutation that deleted the filter.
        """
        world, ex, ney, murat, mack = field
        murat.location = "Paris"
        murat.jealous_of = "Ney"
        lannes = MarshalFactory.infantry(name="Lannes", location="Paris",
                                         strength=20000,
                                         personality="aggressive")
        world.marshals["Lannes"] = lannes
        note = ex._combat._bad_odds_muster_note(ney, mack, world)
        assert note, "precondition: a clean reinforcer must produce a note"
        assert "Lannes" in note, note
        assert "Murat" not in note, note

    def test_a_real_reinforcer_is_still_named(self, field):
        world, ex, ney, murat, mack = field
        murat.location = "Paris"
        note = ex._combat._bad_odds_muster_note(ney, mack, world)
        assert "Murat" in note, note


# ════════════════════════════════════════════════════════════════════════
# The safety pin — row 2's gate must not move
# ════════════════════════════════════════════════════════════════════════

class TestBandInvariance:
    """A5 changes `will_join` for a co-located hostile. That field feeds
    `committed_attacker` and therefore `odds_band`, and row 2 (`075982e`)
    scopes the attack-confirm modal to an `unfavorable` band — so a moved
    band would silently re-arm or disarm that gate.

    It cannot move, because a derived-hostile ally already scaled to ×0.0 in
    the committed math and contributed nothing. These pins PROVE that instead
    of trusting the reasoning.
    """

    def _band_and_committed(self, world, ex, ney, mack):
        p = _preview(ex, world, ney, mack)
        return p["odds_band"], p["attacker"]["committed_strength"]

    def test_a_hostile_neighbour_changes_neither_band_nor_figure(self, field):
        world, ex, ney, murat, mack = field
        # Baseline: hostile, but computed as if the old code had counted him.
        murat.set_relationship("Ney", -2)
        ney.set_relationship("Murat", -2)
        band, committed = self._band_and_committed(world, ex, ney, mack)
        # His own strength is excluded either way, so the committed figure is
        # the lead's alone.
        assert committed == int(ney.strength)
        assert band in ("favorable", "even", "unfavorable")

    def test_a_grievance_does_not_move_the_figure_it_already_zeroed(self, field):
        world, ex, ney, murat, mack = field
        murat.location = "Paris"
        before = self._band_and_committed(world, ex, ney, mack)
        murat.jealous_of = "Ney"
        after = self._band_and_committed(world, ex, ney, mack)
        assert after[1] < before[1], (
            "precondition: the grievance must actually remove his weight, "
            "or this test proves nothing")
        # And the WITHHOLDING row is what tells the player about it.
        assert "withholds" in _row(_preview(ex, world, ney, mack), "Murat")

    def test_the_co_located_arm_is_invisible_for_a_clean_pair(self, field):
        """The new arm must not fire unless the pair is hostile. Asserted as
        an exact equality against the production formula rather than a `>`
        with an `or` — a disjunction here would pass against almost any
        number, which is the inert-pin shape this project keeps finding."""
        world, ex, ney, murat, mack = field
        expected_extra = ex._combat._committed_reinforcement_strength(
            ney, [ney, murat], world)
        assert expected_extra > 0, "precondition: a clean ally contributes"
        _band, committed = self._band_and_committed(world, ex, ney, mack)
        assert committed == int(ney.strength + expected_extra)


# ════════════════════════════════════════════════════════════════════════
# A6 — character, not weather
# ════════════════════════════════════════════════════════════════════════

class TestA6AttributionIsHonest:
    def test_the_reason_code_names_the_quarrel(self):
        import inspect
        src = inspect.getsource(CombatExecutor)
        assert 'reason = "grievance_withheld"' in src
        # And it is gated on a WRITTEN order being absent, like its two
        # siblings — a no-show under a SUPPORT order the player issued stays
        # a logistics failure he can be held to.
        idx = src.index('reason = "grievance_withheld"')
        window = src[max(0, idx - 400):idx]
        assert "not has_explicit_order" in window

    def test_the_copy_names_the_man_not_the_roads(self):
        import inspect
        src = inspect.getsource(CombatExecutor)
        assert "kept him where he stood" in src
        assert 'reason == "grievance_withheld"' in src

    def test_the_diorama_shelf_has_a_label(self):
        from backend.game_logic.battle_diorama import (
            _ABSENCE_LABELS, _REFUSAL_REASONS,
        )
        assert "grievance_withheld" in _ABSENCE_LABELS
        assert "could not reach" not in _ABSENCE_LABELS["grievance_withheld"]
        # A choice, not a failed roll — so it sits with the by-design
        # refusals, which is also what keeps the trust dock off it there.
        assert "grievance_withheld" in _REFUSAL_REASONS


class TestA6TrustDockUnchanged:
    """DELIBERATE: `grievance_withheld` is NOT in the Session-61a exempt
    tuple. Before A6 the same marshal carried `low_score` and was docked, so
    leaving him docked keeps the trust arithmetic byte-identical and keeps a
    copy fix out of the balance. Whether a sulk should also be exempt is Q1's
    business."""

    def test_the_exempt_tuple_does_not_include_the_new_code(self):
        import inspect
        src = inspect.getsource(CombatExecutor)
        marker = '"literal_personality", "fate_intervened",\n'
        assert marker in src
        idx = src.index(marker)
        window = src[idx:idx + 220]
        assert "grievance_withheld" not in window, (
            "the new code was added to the trust-dock exemption — that is a "
            "balance change, not the copy fix A6 shipped. Move the gate "
            "record first.")


# ════════════════════════════════════════════════════════════════════════
# A8 — the story is told about the right man
# ════════════════════════════════════════════════════════════════════════

class TestA8ThePetitionNamesTheSulker:
    def test_the_aggrieved_man_is_the_petitioner(self, field):
        world, ex, ney, murat, _ = field
        murat.jealous_of = "Ney"
        # The change record arrives from NEY's side, which is the whole bug:
        # Murat's own delta returns 0 because `modify_relationship` reads the
        # derived value.
        # PC15-10 B0 (F5-S4): the transition value is re-read from STORED,
        # so the claimed -1 must be backed by a real write.
        ney.set_relationship("Murat", -1)
        J.check_rivalry_transitions(world, [{
            "marshal": "Ney", "toward": "Murat", "change": -1,
            "new_value": -1, "nation": "France",
        }])
        petition = world.pending_marshal_petition
        assert petition is not None
        assert petition["context"]["marshal"] == "Murat", (
            "the petition still names the wrong man as the sulker")
        assert petition["context"]["other"] == "Ney"

    def test_a_pair_with_no_grievance_is_left_as_recorded(self, field):
        """FALSIFIABLE NEGATIVE: the swap must be driven by `jealous_of`, not
        applied to every transition."""
        world, ex, ney, murat, _ = field
        # F5-S4: back the claimed transition with the stored write.
        ney.set_relationship("Murat", -1)
        J.check_rivalry_transitions(world, [{
            "marshal": "Ney", "toward": "Murat", "change": -1,
            "new_value": -1, "nation": "France",
        }])
        assert world.pending_marshal_petition["context"]["marshal"] == "Ney"

    def test_a_mutual_feud_is_left_as_recorded(self, field):
        world, ex, ney, murat, _ = field
        ney.jealous_of = "Murat"
        murat.jealous_of = "Ney"
        # F5-S4: back the claimed transition with the stored write.
        ney.set_relationship("Murat", -1)
        J.check_rivalry_transitions(world, [{
            "marshal": "Ney", "toward": "Murat", "change": -1,
            "new_value": -1, "nation": "France",
        }])
        assert world.pending_marshal_petition["context"]["marshal"] == "Ney"


class TestA8NoFalseThaw:
    def test_a_change_that_did_not_land_is_marked(self, field):
        """`modify_relationship` reads derived and writes stored, so on a
        jealous pair a `+1` returns +1 and moves nothing."""
        world, ex, ney, murat, _ = field
        murat.set_relationship("Ney", -1)
        murat.jealous_of = "Ney"
        stored_before = murat.relationships.get("Ney")
        returned = murat.modify_relationship("Ney", +1)
        assert returned == 1, "precondition: the writer still reports +1"
        assert murat.relationships.get("Ney") == stored_before, (
            "precondition: stored did not move — if this fails the writer "
            "was fixed and A8's display guard can be retired (Q5 option b)")

    def test_berthier_does_not_narrate_it(self):
        from backend.game_logic.battle_report import _pick_observation
        battle = {
            "outcome": "stalemate",
            "attacker": {"nation": "France"}, "defender": {"nation": "Austria"},
            "relationship_changes": [{
                "marshal": "Murat", "toward": "Ney", "change": 1,
                "new_value": -1, "new_label": "Rival",
                "direction": "improved", "nation": "France",
                "stored_moved": False,
            }],
        }
        line = _pick_observation(battle, player_nation="France")
        # Asserted against the actual bank rather than a keyword disjunction:
        # `A not in line or B not in line` passes whenever EITHER is absent,
        # so it would survive the guard being deleted.
        from backend.game_logic.battle_report import _OBSERVATIONS
        for template in _OBSERVATIONS["coordination_rival_improved"]:
            stem = template.split("{")[0].strip()
            assert not (stem and line.startswith(stem)), line

    def test_but_a_real_thaw_still_is(self):
        """FALSIFIABLE NEGATIVE — otherwise the filter could be dropping
        every improvement and the test above would pass regardless."""
        from backend.game_logic.battle_report import _pick_observation
        battle = {
            "outcome": "stalemate",
            "attacker": {"nation": "France"}, "defender": {"nation": "Austria"},
            "relationship_changes": [{
                "marshal": "Murat", "toward": "Ney", "change": 1,
                "new_value": 0, "new_label": "Professional",
                "direction": "improved", "nation": "France",
                "stored_moved": True,
            }],
        }
        assert "Ney" in _pick_observation(battle, player_nation="France")

    def test_the_flag_defaults_true_for_other_producers(self):
        from backend.game_logic.battle_report import _pick_observation
        battle = {
            "outcome": "stalemate",
            "attacker": {"nation": "France"}, "defender": {"nation": "Austria"},
            "relationship_changes": [{
                "marshal": "Murat", "toward": "Ney", "change": 1,
                "new_value": 0, "new_label": "Professional",
                "direction": "improved", "nation": "France",
            }],
        }
        assert "Ney" in _pick_observation(battle, player_nation="France")
