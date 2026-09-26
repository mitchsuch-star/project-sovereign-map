"""SR-1a "Status quo is a cession" (Score Mandate Chunk 1, September 26,
2026; `DESIGN_REFINEMENT.md` AAR-D2; landing record `SCORE_MANDATE_PLAN.md`
§2 Chunk 1).

A province one signatory HOLDS of the other's — the other's homeland, or
ground captured from it — that a SIGNED war-ending peace leaves in its
hands is titled by treaty at the signature (uti possidetis). The AAR's
Treaty of Vienna left Vienna, Bohemia, Hungary and Moravia "held,
unsettled"; the road to 45 was four provinces shorter than the count said.

Written at the ONE diplomatic-state setter, per pair, after the state
write, so every ratifier inherits it (GR5). Only a SIGNED road titles:
`game_end.SIGNED_PEACE_REASONS`. A retained title is a title for the COUNT
and breaks like any treaty, and it is never reconciled — the loser signed
no cession, so its designs still covet the ground and the Congress is still
won at the table.
"""
import contextlib
import io
from pathlib import Path

import pytest

from backend.game_logic import congress, game_end
from backend.game_logic.diplomacy import set_diplomatic_state
from backend.game_logic.settlement_ratify import ratify_settlement_confirm
from backend.models.world_state import WorldState
from tests.test_common_peace_c2_ratification import (
    _install_two_v_two_war, _stage_dialogue,
)

SCENARIO_PATH = (Path(__file__).resolve().parents[1] / "godot-client"
                 / "project-sovereign" / "assets" / "maps" / "europe_1805.json")

THE_FOUR = ("Bohemia", "Hungary", "Moravia", "Vienna")


def _boot() -> WorldState:
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO_PATH))


def _hold(world, region, holder, taken_from, kind=game_end.TITLE_CONQUEST):
    """Stage `holder` holding `region` the way a capture leaves it: the
    controller written and a conquest record naming the court it was
    taken from."""
    world.regions[region].controller = holder
    game_end.record_province_title(world, region, kind, taken_from, holder)
    world.invalidate_active_nations_cache()


def _ratify(world, proposer, target, ptype="peace", demands=None):
    with contextlib.redirect_stdout(io.StringIO()):
        return world._ratify_treaty({
            "proposer_nation": proposer, "target_nation": target,
            "type": ptype, "sweeteners": [], "demands": list(demands or [])})


@pytest.fixture
def vienna_road():
    """The AAR's turn-9 shape: France holds the four Austrian provinces by
    conquest, the war still on, nothing signed."""
    w = _boot()
    for region in THE_FOUR:
        _hold(w, region, "France", "Austria")
    return w


class TestTheAARShape:

    def test_the_four_are_held_unsettled_before_the_peace(self, vienna_road):
        view = congress.titled(vienna_road)
        assert view["count"] == 35
        assert all(r in view["held"] for r in THE_FOUR)
        line = congress.state_line(vienna_road)
        assert line.startswith("THE CONGRESS OF PARIS — 35 of 45 titled (4 held, unsettled: ")

    def test_a_signed_peace_titles_them_the_same_turn(self, vienna_road):
        w = vienna_road
        result = _ratify(w, "Austria", "France")
        assert result is not None and result.get("success", True) is not False, result
        for region in THE_FOUR:
            rec = w.province_title[region]
            assert rec["kind"] == game_end.TITLE_TREATY
            assert rec["retained"] is True
            assert rec["from"] == "Austria" and rec["holder"] == "France"
            assert game_end.province_title_kind(w, region, "France") == "treaty"
        view = congress.titled(w)
        assert view["count"] == 39
        assert not any(r in view["held"] for r in THE_FOUR)
        assert congress.state_line(w).startswith("THE CONGRESS OF PARIS — 39 of 45 titled")

    def test_the_ratification_summary_says_so(self, vienna_road):
        w = vienna_road
        _ratify(w, "Austria", "France")
        summary = w.peace_ratification_log[-1]
        assert summary["status_quo_titled"] == sorted(THE_FOUR)
        line = [t for t in summary["terms_ratified"] if t.startswith("Status quo:")]
        assert line == ["Status quo: Bohemia, Hungary, Moravia and Vienna stay ours by the treaty — titled."]

    def test_the_dispatch_beat_is_queued_for_the_player(self, vienna_road):
        w = vienna_road
        _ratify(w, "Austria", "France")
        beats = [e for e in w.pending_dispatch_events if e["type"] == "status_quo_titled"]
        assert len(beats) == 1
        assert beats[0]["template_vars"]["count"] == 4
        assert "Vienna" in beats[0]["template_vars"]["provinces"]
        assert beats[0]["template_vars"]["ceder"] == "Austria"

    def test_the_stash_is_read_then_cleared(self, vienna_road):
        w = vienna_road
        _ratify(w, "Austria", "France")
        assert game_end.take_status_quo_titled(w) == []


class TestBothDirections:

    def test_what_they_hold_of_ours_is_titled_to_them(self):
        w = _boot()
        ours = sorted(w.nation_starting_regions["France"])[0]
        _hold(w, ours, "Austria", "France")
        _ratify(w, "Austria", "France")
        rec = w.province_title[ours]
        assert rec["kind"] == game_end.TITLE_TREATY and rec["retained"] is True
        assert rec["from"] == "France" and rec["holder"] == "Austria" and rec["house"] == "Austria"
        summary = w.peace_ratification_log[-1]
        assert summary["status_quo_titled"] == []
        theirs = [t for t in summary["terms_ratified"] if t.startswith("Status quo:")]
        assert theirs == [f"Status quo: {ours} stays Austrian by the treaty."]

    def test_ground_captured_from_the_ceder_counts_even_off_its_homeland(self):
        """Munich is Bavaria's; taken FROM Austria it is Austria's to
        renounce. A conquest record naming the ceder is the second read."""
        w = _boot()
        bavarian = sorted(w.nation_starting_regions["Bavaria"])[0]
        _hold(w, bavarian, "France", "Austria")
        _ratify(w, "Austria", "France")
        rec = w.province_title[bavarian]
        assert rec["kind"] == game_end.TITLE_TREATY and rec["retained"] is True
        assert rec["from"] == "Austria"

    def test_ground_captured_from_a_third_court_is_not_the_ceders_to_renounce(self):
        w = _boot()
        russian = sorted(w.nation_starting_regions["Russia"])[0]
        _hold(w, russian, "France", "Russia")
        _ratify(w, "Austria", "France")
        assert w.province_title[russian]["kind"] == game_end.TITLE_CONQUEST
        assert "retained" not in w.province_title[russian]


class TestOnlyASignedPeace:

    def test_a_truce_titles_nothing(self, vienna_road):
        w = vienna_road
        _ratify(w, "Austria", "France", ptype="armistice")
        assert w.get_diplomatic_state("Austria", "France") == "ARMISTICE"
        for region in THE_FOUR:
            assert w.province_title[region]["kind"] == game_end.TITLE_CONQUEST

    def test_the_peace_signed_after_a_truce_titles(self, vienna_road):
        w = vienna_road
        _ratify(w, "Austria", "France", ptype="armistice")
        _ratify(w, "Austria", "France", ptype="peace")
        for region in THE_FOUR:
            assert w.province_title[region]["kind"] == game_end.TITLE_TREATY

    @pytest.mark.parametrize("reason", ["armistice_expired_peace", "nation_eliminated",
                                        "treaty_break", "cheat_command", ""])
    def test_an_unsigned_road_to_peace_titles_nothing(self, vienna_road, reason):
        w = vienna_road
        set_diplomatic_state(w, "France", "Austria", "PEACE", reason)
        for region in THE_FOUR:
            assert w.province_title[region]["kind"] == game_end.TITLE_CONQUEST

    @pytest.mark.parametrize("reason", sorted(game_end.SIGNED_PEACE_REASONS))
    def test_every_signed_road_titles(self, vienna_road, reason):
        w = vienna_road
        target = "VASSAL" if "vassal" in reason else "PEACE"
        set_diplomatic_state(w, "France", "Austria", target, reason)
        for region in THE_FOUR:
            assert w.province_title[region]["kind"] == game_end.TITLE_TREATY, reason
            assert w.province_title[region]["retained"] is True

    def test_a_peace_that_was_never_a_war_titles_nothing(self):
        """Prussia at peace with France on the boot: a treaty between them
        leaves WAR nowhere, so the retention pass never runs (the reason
        alone is not the gate)."""
        w = _boot()
        prussian = sorted(w.nation_starting_regions["Prussia"])[0]
        _hold(w, prussian, "France", "Prussia")
        assert w.get_diplomatic_state("France", "Prussia") != "WAR"
        set_diplomatic_state(w, "France", "Prussia", "OPEN_BORDERS", "treaty_ratification")
        assert w.province_title[prussian]["kind"] == game_end.TITLE_CONQUEST

    def test_the_lever_down_writes_nothing(self, vienna_road, monkeypatch):
        monkeypatch.setattr(game_end, "STATUS_QUO_IS_A_CESSION", False)
        w = vienna_road
        _ratify(w, "Austria", "France")
        for region in THE_FOUR:
            assert w.province_title[region]["kind"] == game_end.TITLE_CONQUEST
        assert congress.titled(w)["count"] == 35


class TestTheClauseOutranksTheRetention:

    def test_a_province_the_same_treaty_cedes_back_is_not_retained(self, vienna_road):
        w = vienna_road
        _ratify(w, "Austria", "France",
                demands=[{"type": "territory_cede", "regions": ["Vienna"],
                          "from": "France", "to": "Austria"}])
        assert w.regions["Vienna"].controller == "Austria"
        # Home again: no record at all (homeland is title by construction).
        assert "Vienna" not in w.province_title
        for region in ("Bohemia", "Hungary", "Moravia"):
            assert w.province_title[region]["kind"] == game_end.TITLE_TREATY


class TestAHolderStillAtWar:

    def test_a_satellite_whose_own_pair_is_still_at_war_retains_nothing(self):
        """The Kingdom of Italy holds Tyrol and is still at war with Austria
        on its own account when the lord's pair is set: the peace is not its
        yet. The moment ITS pair is signed, Tyrol is titled."""
        w = _boot()
        _hold(w, "Tyrol", "KingdomOfItaly", "Austria")
        assert w.is_at_war("KingdomOfItaly", "Austria")
        set_diplomatic_state(w, "France", "Austria", "PEACE", "treaty_ratification")
        assert w.province_title["Tyrol"]["kind"] == game_end.TITLE_CONQUEST
        set_diplomatic_state(w, "KingdomOfItaly", "Austria", "PEACE", "treaty_ratification")
        rec = w.province_title["Tyrol"]
        assert rec["kind"] == game_end.TITLE_TREATY and rec["retained"] is True
        assert rec["holder"] == "KingdomOfItaly" and rec["house"] == "France"
        assert game_end.province_title_kind(w, "Tyrol", "France") == "treaty"


class TestWhatARetainedTitleIsAndIsNot:

    def test_it_is_not_reconciled(self, vienna_road):
        w = vienna_road
        _ratify(w, "Austria", "France")
        assert not (set(THE_FOUR) & game_end.reconciled_regions(w, "Austria"))

    def test_a_signed_cession_still_is(self):
        w = _boot()
        _hold(w, "Tyrol", "France", "Austria", kind=game_end.TITLE_TREATY)
        set_diplomatic_state(w, "France", "Austria", "PEACE", "treaty_ratification")
        assert "Tyrol" in game_end.reconciled_regions(w, "Austria")

    def test_a_renewed_war_breaks_it(self, vienna_road):
        w = vienna_road
        _ratify(w, "Austria", "France")
        w.current_turn += 3
        set_diplomatic_state(w, "France", "Austria", "WAR", "war_declaration")
        for region in THE_FOUR:
            rec = w.province_title[region]
            assert rec["kind"] == game_end.TITLE_CONQUEST
            assert rec["since"] == w.current_turn
            assert rec["reopened_by"] == "Austria"

    def test_it_does_not_latch_the_congress(self, vienna_road):
        """A retention is not a cession the court signed: the Congress's
        beaten-court latch reads applied cessions and stays empty."""
        w = vienna_road
        _ratify(w, "Austria", "France")
        assert not (congress.record(w) or {}).get("signed")

    def test_the_record_round_trips(self, vienna_road):
        w = vienna_road
        _ratify(w, "Austria", "France")
        with contextlib.redirect_stdout(io.StringIO()):
            again = WorldState.from_dict(w.to_dict())
        assert again.province_title["Vienna"]["retained"] is True
        assert congress.titled(again)["count"] == 39


class TestTheSettlementRoad:

    def test_the_table_titles_what_the_covered_court_leaves_in_our_hands(self):
        world = WorldState()
        _install_two_v_two_war(world)
        austrian = sorted(world.nation_starting_regions["Austria"])[0]
        _hold(world, austrian, "France", "Austria")
        dialogue = _stage_dialogue(world, covered_enemy_participants=["Austria"])
        with contextlib.redirect_stdout(io.StringIO()):
            result = ratify_settlement_confirm(world, dialogue)
        assert result["success"] is True
        rec = world.province_title[austrian]
        assert rec["kind"] == game_end.TITLE_TREATY and rec["retained"] is True
        assert result["status_quo_titled"] == [austrian]
        assert f"Status quo: {austrian} stays ours by the treaty — titled." in result["message"]

    def test_an_uncovered_court_keeps_its_claim(self):
        world = WorldState()
        _install_two_v_two_war(world)
        prussian = sorted(world.nation_starting_regions["Prussia"])[0]
        _hold(world, prussian, "France", "Prussia")
        dialogue = _stage_dialogue(world, covered_enemy_participants=["Austria"])
        with contextlib.redirect_stdout(io.StringIO()):
            ratify_settlement_confirm(world, dialogue)
        assert world.province_title[prussian]["kind"] == game_end.TITLE_CONQUEST
