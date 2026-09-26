"""SR-1c "The gate line teaches the road" (Score Mandate Chunk 1, September
26, 2026; landing record `SCORE_MANDATE_PLAN.md` §2 Chunk 1).

For every held-unsettled province the Congress surfaces name its shortest
road to title — derived from the same `province_title` record the count
reads (`game_end.title_roads`), so road and count never disagree; the alarm
term names what lowers it and by how much; the war room's counsel and the
settlement blocker name the DP price of the road they recommend (AAR-D5's
counsel half); the Moniteur's Congress column tells the near miss.
"""
import contextlib
import io
from pathlib import Path

import pytest

from backend.ai import first_contact
from backend.game_logic import congress, diplomatic_advisory, game_end, gazette
from backend.game_logic.diplomacy import (
    diplomatic_price_quote, get_dp_cost, get_transition_dp_cost, set_diplomatic_state,
)
from backend.game_logic.ledger import build_strategic_ledger
from backend.models.world_state import WorldState

SCENARIO_PATH = (Path(__file__).resolve().parents[1] / "godot-client"
                 / "project-sovereign" / "assets" / "maps" / "europe_1805.json")


def _boot() -> WorldState:
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO_PATH))


def _hold(world, region, holder, taken_from, since=None, kind=game_end.TITLE_CONQUEST):
    world.regions[region].controller = holder
    game_end.record_province_title(world, region, kind, taken_from, holder)
    if since is not None:
        world.province_title[region]["since"] = int(since)
    world.invalidate_active_nations_cache()


def _road(world, region):
    return next(r for r in game_end.title_roads(world, "France") if r["region"] == region)


class TestTheFourRoads:

    def test_a_conquest_at_war_with_the_ceder_needs_the_peace(self):
        w = _boot()
        _hold(w, "Vienna", "France", "Austria")
        road = _road(w, "Vienna")
        assert road["kind"] == game_end.ROAD_PEACE and road["at_war"] is True
        assert road["ceder"] == "Austria"
        assert road["text"] == ("Vienna — a peace with Austria that leaves it ours titles it "
                                "at the signature; otherwise 12 quiet turns from the peace")
        assert road["short"] == "Vienna needs a peace with Austria"

    def test_a_conquest_at_peace_names_its_clock(self):
        w = _boot()
        set_diplomatic_state(w, "France", "Austria", "PEACE", "")
        w.current_turn = 10
        _hold(w, "Vienna", "France", "Austria", since=6)
        road = _road(w, "Vienna")
        assert road["kind"] == game_end.ROAD_QUIET and road["at_war"] is False
        assert road["turns_left"] == 8 and road["titles_on_turn"] == 18
        assert road["text"].startswith("Vienna — 8 more quiet turns (titled on turn 18)")
        assert road["short"] == "Vienna titles on turn 18"

    def test_the_road_and_the_count_agree(self):
        """The turn the road names IS the turn the count moves."""
        w = _boot()
        set_diplomatic_state(w, "France", "Austria", "PEACE", "")
        w.current_turn = 10
        _hold(w, "Vienna", "France", "Austria", since=6)
        on = _road(w, "Vienna")["titles_on_turn"]
        w.current_turn = on - 1
        assert "Vienna" in congress.titled(w)["held"]
        w.current_turn = on
        assert "Vienna" in game_end.titled_provinces(w, "France")["titled"]

    def test_a_reopened_cession_says_so(self):
        w = _boot()
        _hold(w, "Vienna", "France", "Austria", kind=game_end.TITLE_TREATY)
        set_diplomatic_state(w, "France", "Austria", "PEACE", "")
        w.current_turn = 5
        set_diplomatic_state(w, "France", "Austria", "WAR", "war_declaration")
        set_diplomatic_state(w, "France", "Austria", "PEACE", "")
        road = _road(w, "Vienna")
        assert road["kind"] == game_end.ROAD_QUIET
        assert "reopened by war on turn 5" in road["text"]

    def test_a_satellites_homeland_names_its_loyalty(self):
        w = _boot()
        w.vassals["KingdomOfItaly"]["loyalty"] = 31
        road = _road(w, "Milan")
        assert road["kind"] == game_end.ROAD_LOYALTY
        assert road["text"].startswith("Milan — the Kingdom of Italy's own soil; it counts once its loyalty reaches 40 (now 31)")
        assert road["short"] == "Milan waits on the Kingdom of Italy's loyalty (31 of 40)"

    def test_a_province_with_no_record_has_no_clock(self):
        w = _boot()
        w.regions["Tyrol"].controller = "France"
        w.province_title.pop("Tyrol", None)
        w.invalidate_active_nations_cache()
        road = _road(w, "Tyrol")
        assert road["kind"] == game_end.ROAD_SIGNATURE
        assert road["short"] == "Tyrol waits on a treaty"

    def test_nothing_held_means_no_roads(self):
        assert game_end.title_roads(_boot(), "France") == []


class TestTheSurfaces:

    @pytest.fixture
    def vienna(self):
        w = _boot()
        for region in ("Vienna", "Bohemia"):
            _hold(w, region, "France", "Austria")
        return w

    def test_the_congress_payload_carries_the_roads_and_the_alarm_road(self, vienna):
        payload = congress.build_congress_payload(vienna)
        assert [r["region"] for r in payload["held_roads"]] == ["Bohemia", "Vienna"]
        assert all(isinstance(r["turns_left"], int) for r in payload["held_roads"])
        assert payload["alarm_road"].startswith("it falls ")
        alarm = next(t for t in payload["gate_terms"] if t["text"].startswith("Europe's alarm"))
        assert payload["alarm_road"] in alarm["text"]

    def test_the_alarm_road_reads_the_ticks_own_decay(self, vienna):
        from backend.game_logic.coalition import _calculate_threat_decay
        decay = _calculate_threat_decay(vienna)
        assert congress.alarm_road(vienna).startswith(f"it falls {decay} a turn (one, plus one for each court at peace with us, at most three")
        assert "a treaty that dissolves a league halves it" in congress.alarm_road(vienna)

    def test_the_state_line_is_untouched(self, vienna):
        line = congress.state_line(vienna)
        assert line.startswith("THE CONGRESS OF PARIS — 35 of 45 titled (2 held, unsettled: Bohemia, Vienna)")
        assert line.endswith(congress.CABINET_HINT)

    def test_the_territories_tab_carries_the_roads_under_the_clock(self, vienna):
        with contextlib.redirect_stdout(io.StringIO()):
            ledger = build_strategic_ledger(vienna)
        clock = ledger["congress_clock"]
        assert clock["line"] == congress.state_line(vienna)
        assert [r["region"] for r in clock["held_roads"]] == ["Bohemia", "Vienna"]

    def test_the_war_room_lists_the_roads_under_the_gate_line(self, vienna):
        with contextlib.redirect_stdout(io.StringIO()):
            dialogue = diplomatic_advisory.generate_advisory(None, "assess_situation", vienna)
        text = dialogue["talleyrand_text"]
        assert congress.state_line(vienna) in text
        assert "Vienna — a peace with Austria that leaves it ours titles it at the signature" in text
        assert "Bohemia — a peace with Austria" in text

    def test_the_war_room_caps_at_four_and_says_where_the_rest_are(self):
        w = _boot()
        for region in ("Vienna", "Bohemia", "Hungary", "Moravia", "Tyrol", "Carniola"):
            _hold(w, region, "France", "Austria")
        with contextlib.redirect_stdout(io.StringIO()):
            text = diplomatic_advisory.generate_advisory(None, "assess_situation", w)["talleyrand_text"]
        assert "… and 2 more on the Diplomatic Ledger's CONGRESS tab." in text

    def test_the_question_desk_names_the_roads(self, vienna):
        answer = first_contact._congress_answer("how do I summon the congress", vienna)
        assert "The held provinces and their roads: Bohemia needs a peace with Austria; Vienna needs a peace with Austria." in answer


class TestTheMoniteurNearMiss:

    def test_the_boot_column_stays_quiet(self):
        assert gazette._congress_column(_boot(), None) == []

    def test_within_five_the_paper_counts_the_road(self):
        from tests.test_congress_of_paris import _stage_titles
        w = _boot()
        _stage_titles(w, need=42)
        set_diplomatic_state(w, "France", "Austria", "PEACE", "")
        w.current_turn = 10
        _hold(w, "Vienna", "France", "Austria", since=6)
        assert congress.titled(w)["count"] == 42
        column = gazette._congress_column(w, None)
        assert column == ["THE CONGRESS OF PARIS — 42 of 45 provinces titled; 3 more and "
                          "the Emperor may summon the powers. Vienna titles on turn 18."]

    def test_beyond_five_the_paper_is_silent(self):
        from tests.test_congress_of_paris import _stage_titles
        w = _boot()
        _stage_titles(w, need=39)
        assert gazette._congress_column(w, None) == []


class TestTheCounselNamesItsPrice:

    def test_the_quote_is_the_executors_own_arithmetic(self):
        w = _boot()
        w.diplomatic_points = 2
        quote = diplomatic_price_quote(w, "peace", "Austria")
        from backend.nation_config import get_player_diplomat
        skill = get_player_diplomat(w).skill
        expected = get_dp_cost("propose_peace", skill,
                               transition_base=get_transition_dp_cost("WAR", "PEACE"))
        assert quote == {"cost": expected, "have": 2, "affordable": 2 >= expected,
                         "text": f"{expected} DP; you have 2"}
        assert expected == 3

    def test_the_blocker_prices_the_road_it_names(self):
        from backend.game_logic.settlement_staging import legitimacy_sentence
        w = _boot()
        w.diplomatic_points = 2
        # Stored from the alphabetically-first court's chair ("Austria|France"):
        # -40 is Austria beaten at -40, France +40.
        w.war_scores[w._make_diplo_key("France", "Austria")] = -40
        rows = [{"nation": "Austria", "total": 51, "threshold": 50},
                {"nation": "Britain", "total": 24, "threshold": 50}]
        sentence = legitimacy_sentence(w, rows, ["Britain", "Austria"], 50)
        assert "Press Austria alone: the separate peace." in sentence
        assert sentence.endswith("Press Austria alone: the separate peace. It costs 3 diplomatic points; you have 2.")

    def test_the_request_terms_counsel_names_the_players_points(self, monkeypatch):
        w = _boot()
        w.diplomatic_points = 4
        rows = [{"opponent": "Austria", "opponents": ["Austria"], "war_score": -30,
                 "status": "war", "request_terms_state": {"state": "available"},
                 "settlement_available": True}]
        monkeypatch.setattr(diplomatic_advisory, "_settlement_candidates",
                            lambda world, player, war_rows: [{
                                "opponent": "Austria", "row": rows[0], "outcome": "ACCEPT",
                                "stuck": False, "pair_losing": True, "age": 3,
                                "terms_open": True}])
        rec = diplomatic_advisory._build_situation_recommendation(w, "France", rows, None, "defensive")
        assert rec["kind"] == "request_terms"
        assert rec["description"] == "Ask their court to name settlement terms (1 DP; you have 4)."
