"""Score Finish Step 7b "The front page of the peace" (October 5, 2026).

SF-NAR-1 "Every morning has a front page" + SF-LB-3 "Europe arms in plain
sight", with the three rows the Step 7 exit filed for this step (SF7-X37
France's own truce ending never led, SF7-X38 raw nation keys on the rail,
SF7-X39 living balance C5's probe read the headline line only) and the two
found building it (SF7-X45 the alarm forecast read the clock one turn
early, SF7-X46 the passage warning told a corps with no turn to spare that
its passage had run out). Spec: docs/SCORE_FINISH_SPEC.md §3 Step 7b;
rules SYSTEMS_REFERENCE.md §94.

Every pin drives a production seam — the headline's own builder and
selector, the league's ONE reader against the real coalition and diplomacy
ticks, POST /command, or the driver on the three commanded arms read by the
instrument's own readers — and reads the answer back.
"""
import contextlib
import copy
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands.parser import CommandParser
from backend.game_logic import coalition as CO
from backend.game_logic import congress
from backend.game_logic import diplomacy as D
from backend.game_logic import dispatch, game_end, instruments
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCEN = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
           / "europe_1805.json")
SCRIPT = REPO / "tools" / "playtest_scripts" / "commanded_full40.json"
ARCHIVE = REPO / "docs" / "audits" / "score_runs" / "2026_10_05_step7" / "arms"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _boot() -> WorldState:
    with _quiet():
        return WorldState.from_scenario(SCEN)


def _quiet_france(turn=20, threat=45, quiet=11, rel=-50) -> WorldState:
    """A France at peace with every court after the opening war: no league
    stands or brews, the three great powers at `rel` (they QUALIFY below
    -10), and France's last battle `quiet` turns ago (11 by default: the
    fuse's beats at 8, 4 and 2 turns left are event news of their own)."""
    w = _boot()
    france = w.player_nation
    w.current_turn = turn
    w.active_coalition = None
    w.coalition_brewing = None
    w.coalition_cooldown = 0
    for nation in w.get_active_nations():
        if nation == france:
            continue
        key = w._make_diplo_key(france, nation)
        if w.diplomatic_states.get(key) == "WAR":
            w.diplomatic_states[key] = "PEACE"
        if nation in ("Austria", "Britain", "Russia"):
            w.nation_relations[key] = rel
    w.invalidate_active_nations_cache()
    w.threat_by_target[france] = int(threat)
    w.threat_sources_this_turn = []
    w.pending_dispatch_events = []
    w.event_log = []
    w.headline_lead_memory = {}
    for m in w.marshals.values():
        m.last_battle_turn = int(turn - quiet)
    return w


def _page(world, record=True, rows=None):
    with _quiet():
        return dispatch._build_headline(world, "France", record=record,
                                        diplomatic_rows=rows) or {}


def _cand(cls, identity=None, text=None, weight=None, fields=None):
    return {"class": cls, "weight": int(weight if weight is not None
                                        else dispatch.HEADLINE_WEIGHTS[cls]),
            "text": text or f"Sire — {cls} {identity or ''}".strip(),
            "identity": identity or cls, "fields": dict(fields or {})}


def _select(world, candidates):
    with _quiet():
        return dispatch._select_headline(world, [dict(c) for c in candidates])


def _tick(world):
    """The production order: `advance_turn` moves the turn on BEFORE the
    coalition tick (world_state's increment precedes it)."""
    world.current_turn += 1
    with _quiet():
        CO.process_coalition_turn(world)


# ═════════════════════ SF7-X45 — the forecast reads the tick's clock ═════════

class TestTheForecastReadsTheTicksClock:
    def test_the_lapse_turn_is_forecast_as_advance_turn_plays_it(self):
        """19 quiet turns: the next tick lights the fuse (+3). The forecast
        read 45; `advance_turn` gave 49."""
        world = _quiet_france(turn=30, quiet=19)
        forecast = CO.forecast_alarm_tick(world)
        played = copy.deepcopy(world)
        with _quiet():
            played.advance_turn()
        assert forecast["next"] == int(played.threat_level) == 49
        assert any("re-arm" in label for label, _ in forecast["gains"])

    def test_lever_down_misses_the_lapse(self, monkeypatch):
        monkeypatch.setattr(CO, "THE_FORECAST_READS_THE_TICKS_CLOCK", False)
        world = _quiet_france(turn=30, quiet=19)
        assert CO.forecast_alarm_tick(world)["next"] == 45

    def test_a_marker_on_its_last_turn_is_not_counted(self):
        world = _quiet_france(turn=30, quiet=5)
        world.ultimatum_rejection_pressure = {"Austria": world.current_turn + 1}
        labels = [label for label, _ in CO.forecast_alarm_tick(world)["gains"]]
        assert "the ultimatums we defied" not in labels
        played = copy.deepcopy(world)
        _tick(played)
        assert not played.ultimatum_rejection_pressure, "the tick dropped it too"


# ═════════════════════ SF-LB-3 — the league's ONE reader ══════════════════════

class TestTheLeagueForecast:
    def test_each_quoted_price_flips_the_gate(self):
        world = _quiet_france()
        # Prussia three points below the bar: a buy-off's +5 alone keeps
        # her out; the others need Talleyrand's road.
        world.nation_relations[world._make_diplo_key("France", "Prussia")] = -13
        rows = [r for r in CO.league_forecast(world)["courts"]
                if r["status"] == CO.LEAGUE_JOINS]
        prussia = next(r for r in rows if r["nation"] == "Prussia")
        assert prussia["buyoff"] is not None and prussia["buyoff_alone"] is True
        assert {r["nation"] for r in rows} >= {"Austria", "Britain", "Russia"}
        for row in rows:
            n = row["nation"]
            assert CO.qualifies_for_coalition(n, world)
            assert not CO.qualifies_for_coalition(n, world, relation_shift=row["need"])
            assert CO.qualifies_for_coalition(n, world, relation_shift=row["need"] - 1)
            if row["buyoff"] is not None:
                assert row["buyoff"] == instruments.compute_buyoff_price(world, n)
                assert row["buyoff_alone"] == (not CO.qualifies_for_coalition(
                    n, world, relation_shift=instruments.BUYOFF_RELATION_BONUS))

    def test_the_road_is_the_real_diplomacy_tick(self):
        """Talleyrand's Improve Relations mission, ticked by the real
        `process_diplomacy_turn`, reaches -10 on exactly the turn quoted."""
        world = _quiet_france()
        row = next(r for r in CO.league_forecast(world)["courts"] if r["nation"] == "Austria")
        turns, dp = row["road"]
        played = copy.deepcopy(world)
        played.diplomatic_points = 99
        key = played._make_diplo_key("France", "Austria")
        played.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS", "target": "Austria", "turns_active": 0,
            "paused": False, "paused_turns": 0, "started_turn": played.current_turn,
            "initial_relation": int(played.nation_relations[key])}
        played.talleyrand_state = "ON_MISSION"
        reached = None
        for k in range(1, 20):
            played.current_turn += 1
            with _quiet():
                D.process_diplomacy_turn(played)
            if int(played.nation_relations[key]) >= CO.LEAGUE_KEEP_OUT_RELATION:
                reached = k
                break
        assert reached == turns
        assert dp == turns * 1

    def test_the_consult_and_declare_turns_are_the_ticks(self):
        world = _quiet_france(turn=30, threat=50, quiet=17)
        forecast = CO.league_forecast(world)
        consult, declare = forecast["consult_turns"], forecast["declare_turns"]
        assert consult is not None and declare == consult + CO.BREWING_COUNTDOWN
        played = copy.deepcopy(world)
        brewed = formed = None
        for k in range(1, 30):
            _tick(played)
            if brewed is None and played.coalition_brewing:
                brewed = k
            if played.active_coalition:
                formed = k
                break
        assert (brewed, formed) == (consult, declare)

    def test_the_buy_off_refusal_is_the_verbs(self):
        """The row's gate is the verb's: '' exactly when `buy off X` goes through."""
        from backend.commands.executor import CommandExecutor
        for gold in (0, 99999):
            world = _quiet_france()
            world.nation_gold["France"] = gold
            world.diplomatic_points = 5
            row = next(r for r in CO.league_forecast(world)["courts"] if r["nation"] == "Austria")
            with _quiet():
                result = CommandExecutor()._diplomatic._execute_buy_off_design(
                    {"action": "buy_off_design", "target": "Austria",
                     "raw_input": "buy off Austria"}, {"world": world})
            assert bool(result.get("success")) == (row["buyoff_refusal"] == ""), (gold, row, result)

    def test_a_court_out_of_time_will_march(self):
        world = _quiet_france(turn=30, threat=57, quiet=25, rel=-90)
        forecast = CO.league_forecast(world)
        row = next(r for r in forecast["courts"] if r["nation"] == "Russia")
        assert row["out_of_time"] and row["road"][0] > forecast["declare_turns"]
        text = CO.league_row_text(world, row, forecast)
        assert text.endswith("She will march.") and "Courtship needs" in text

    def test_a_court_refusing_the_congress(self):
        world = _quiet_france(threat=30, quiet=5)
        need = congress.hold_titled(world)
        for nation in ("Hanover", "Denmark", "Portugal", "Sardinia", "Naples",
                       "Saxony", "Hesse", "Holland", "Switzerland"):
            for region in sorted(world.get_nation_regions(nation)):
                if congress.titled(world)["count"] >= need:
                    break
                if region == "Lisbon":
                    continue
                world.regions[region].controller = "France"
                game_end.record_province_title(world, region, game_end.TITLE_TREATY,
                                               nation, "France")
        world.invalidate_active_nations_cache()
        world.diplomatic_points = 6
        with _quiet():
            assert congress.summon(world)["success"]
        forecast = CO.league_forecast(world)
        prussia = next(r for r in forecast["courts"] if r["nation"] == "Prussia")
        assert congress.answer(world, "Prussia")["stance"] == congress.REFUSES
        assert prussia["status"] == CO.LEAGUE_REFUSES
        text = CO.league_row_text(world, prussia, forecast)
        assert "She refuses the Congress" in text and "Congress tab" in text
        assert "Talleyrand brings her" not in text

    def test_the_titles_her_war_would_reopen_are_the_break_rules(self):
        world = _quiet_france()
        world.regions["Tyrol"].controller = "France"
        game_end.record_province_title(world, "Tyrol", game_end.TITLE_TREATY,
                                       "Austria", "France")
        row = next(r for r in CO.league_forecast(world)["courts"] if r["nation"] == "Austria")
        assert row["titles"] == ["Tyrol"]
        assert "Her war would reopen the titles she ceded: Tyrol." in \
            CO.league_row_text(world, row, CO.league_forecast(world))
        game_end.break_signed_titles(world, "Austria", "France")
        assert world.province_title["Tyrol"]["kind"] == game_end.TITLE_CONQUEST

    def test_a_fresh_peace_binds(self):
        world = _quiet_france()
        inst = next(i for i in world.war_instances.values()
                    if world._make_diplo_key("France", "Austria") in (i.get("diplo_key_meta") or {}))
        meta = inst["diplo_key_meta"][world._make_diplo_key("France", "Austria")]
        meta["pair_status"], meta["resolved_turn"] = "resolved", world.current_turn - 1
        row = next(r for r in CO.league_forecast(world)["courts"] if r["nation"] == "Austria")
        assert row["status"] == CO.LEAGUE_BOUND
        assert row["bound_turns"] == CO.FRESH_PEACE_FLOOR_TURNS - 1
        assert not CO.qualifies_for_coalition("Austria", world)

    def test_an_order_moves_the_reader_the_same_turn(self):
        world = _quiet_france()
        before = next(r for r in CO.league_forecast(world)["courts"] if r["nation"] == "Austria")
        world.modify_nation_relation("France", "Austria", 45)
        after = next(r for r in CO.league_forecast(world)["courts"] if r["nation"] == "Austria")
        assert before["status"] == CO.LEAGUE_JOINS and after["status"] == CO.LEAGUE_OUT

    def test_lever_down_reads_nothing(self, monkeypatch):
        monkeypatch.setattr(CO, "THE_LEAGUE_IS_SEEN", False)
        world = _quiet_france()
        assert CO.league_forecast(world)["courts"] == []
        assert CO.league_rows(world) == [] and CO.league_summary_line(world) == ""


class TestTheCourtshipClauseIsStepped:
    def test_a_named_court_reads_the_stepped_road(self):
        world = _quiet_france()
        key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[key] = 20
        road = D.courtship_road(world, "Prussia", 80, start=20)
        clause = congress.courtship_clause(world, 60, court="Prussia")
        assert f"about {road[0]} turns" in clause
        flat = congress.courtship_clause(world, 60)
        assert flat != clause, "the drift toward zero slows a warm court"

    def test_lever_down_is_the_flat_rate(self, monkeypatch):
        monkeypatch.setattr(congress, "THE_COURTSHIP_IS_STEPPED", False)
        world = _quiet_france()
        assert congress.courtship_clause(world, 60, court="Prussia") == \
            congress.courtship_clause(world, 60)


# ═════════════════════ SF-NAR-1 — every morning has a front page ══════════════

class TestEveryMorningHasAFrontPage:
    def test_a_quiet_peace_leads_with_the_league(self):
        world = _quiet_france()
        head = _page(world)
        assert head["class"] == "realm_league", head
        assert head["text"].startswith("Sire — Europe has watched us 11 quiet turns.")
        assert "The cheapest court to keep out of it is" in head["text"]

    def test_the_biggest_row_leads_without_its_rail_tag(self):
        world = _quiet_france()
        rows = [{"type": "law_enacted_abroad",
                 "text": "THE LAWS: Britain enacts the Commissariat — fed provinces feed 25% more men (×1.25)."},
                {"type": "intent_hardens", "text": "The court of Russia hardens over Finland."}]
        head = _page(world, rows=rows)
        assert head["class"] == "courts_laws"
        assert head["text"] == ("Sire — Britain enacts the Commissariat — fed provinces "
                                "feed 25% more men (×1.25).")

    def test_a_raw_court_tag_is_named_on_the_page(self):
        world = _quiet_france()
        head = _page(world, rows=[{"type": "allegiance_in_play",
                                   "text": "The allegiance of KingdomOfItaly is in play."}])
        assert head["class"] == "courts_treaties"
        assert "the Kingdom of Italy" in head["text"] and "KingdomOfItaly" not in head["text"]

    def test_a_page_with_nothing_says_it_is_quiet(self, monkeypatch):
        monkeypatch.setattr(CO, "THE_LEAGUE_IS_SEEN", False)
        monkeypatch.setattr(dispatch, "_realm_candidates", lambda world, nation: [])
        assert _page(_quiet_france())["class"] == "quiet_morning"

    def test_lever_down_a_quiet_board_has_no_headline(self, monkeypatch):
        monkeypatch.setattr(dispatch, "EVERY_MORNING_HAS_A_FRONT_PAGE", False)
        assert _page(_quiet_france()) == {}

    def test_event_news_keeps_the_front_page_off(self):
        """The courts' rows fill a page with no event news, never beside it."""
        world = _quiet_france()
        world.log_event({"type": "region_captured", "region": "Limousin",
                         "captured_by": "Britain", "captured_from": "France",
                         "turn": world.current_turn})
        world.regions["Limousin"].controller = "Britain"
        world.invalidate_active_nations_cache()
        head = _page(world, rows=[{"type": "law_enacted_abroad", "text": "THE LAWS: Britain enacts X."}])
        assert head["class"] == "home_captured"
        assert not any("enacts X" in b for b in head["sub_beats"])


class TestTheFamilyAllowance:
    def _run(self, world, candidates, mornings):
        out = []
        for _ in range(mornings):
            world.current_turn += 1
            out.append(_select(world, candidates))
        return out

    def test_the_family_leads_its_allowance_then_the_front_page(self):
        world = _boot()
        world.headline_lead_memory = {}
        cands = [_cand("estate_eroding", "estate_eroding:Ney",
                       text="Sire — Marshal Ney's household goes unpaid."),
                 _cand("courts_laws", "courts_laws:x", text="Sire — Britain enacts a law.")]
        heads = self._run(world, cands, 6)
        assert [h["class"] for h in heads] == (["estate_eroding"] * dispatch.STANDING_LEAD_MAX
                                               + ["courts_laws"] * (6 - dispatch.STANDING_LEAD_MAX))
        assert all(any("Ney" in b for b in h["sub_beats"]) for h in heads[2:])

    def test_lever_down_pc7_alone_lets_the_nag_return(self, monkeypatch):
        monkeypatch.setattr(dispatch, "EVERY_MORNING_HAS_A_FRONT_PAGE", False)
        world = _boot()
        world.headline_lead_memory = {}
        cands = [_cand("estate_eroding", "estate_eroding:Ney"),
                 _cand("courts_laws", "courts_laws:x")]
        classes = [h["class"] for h in self._run(world, cands, 4)]
        assert classes == ["estate_eroding", "estate_eroding", "courts_laws", "estate_eroding"]

    def test_a_new_crisis_is_new_stakes(self):
        world = _boot()
        world.headline_lead_memory = {}
        ney = [_cand("estate_eroding", "estate_eroding:Ney"), _cand("courts_laws", "courts_laws:x")]
        self._run(world, ney, 3)
        davout = ney + [_cand("estate_eroding", "estate_eroding:Davout", weight=56)]
        assert self._run(world, davout, 1)[0]["class"] == "estate_eroding"

    def test_a_new_war_is_new_stakes(self):
        world = _boot()
        world.headline_lead_memory = {}
        cands = [_cand("estate_eroding", "estate_eroding:Ney"), _cand("courts_laws", "courts_laws:x")]
        self._run(world, cands, 3)
        D.set_diplomatic_state(world, "France", "Prussia", "WAR", "test")
        assert self._run(world, cands, 1)[0]["class"] == "estate_eroding"

    def test_a_wound_outranks_the_family(self):
        world = _boot()
        world.headline_lead_memory = {}
        head = _select(world, [_cand("estate_eroding", "estate_eroding:Ney"),
                               _cand("own_mauled", "own_mauled:Ney")])
        assert head["class"] == "own_mauled"

    def test_a_standing_crisis_rides_beneath_three_wounds(self):
        world = _boot()
        world.headline_lead_memory = {}
        head = _select(world, [_cand("region_lost", "region_lost:A"), _cand("own_mauled", "own_mauled:B"),
                               _cand("own_broken", "own_broken:C"),
                               _cand("estate_eroding", "estate_eroding:Ney",
                                     text="Sire — Marshal Ney's household goes unpaid.")])
        assert head["class"] == "own_broken"
        assert "Sire — Marshal Ney's household goes unpaid." in head["sub_beats"]
        assert len(head["sub_beats"]) == dispatch.SUB_BEAT_SLOTS + 1


class TestTheRotationGuard:
    def test_no_front_page_class_leads_a_fifth_time_in_ten(self):
        world = _boot()
        world.headline_lead_memory = {"leads_window": ["courts_laws"] * 4 + ["realm_league"] * 2}
        head = _select(world, [_cand("courts_laws", "courts_laws:x"), _cand("realm_titles")])
        assert head["class"] == "realm_titles"

    def test_event_news_is_exempt(self):
        world = _boot()
        world.headline_lead_memory = {"leads_window": ["region_lost"] * 6}
        head = _select(world, [_cand("region_lost", "region_lost:x"), _cand("realm_titles")])
        assert head["class"] == "region_lost"

    def test_everything_capped_the_least_led_leads(self):
        world = _boot()
        world.headline_lead_memory = {"leads_window": ["courts_laws"] * 5 + ["realm_league"] * 4}
        head = _select(world, [_cand("courts_laws", "courts_laws:x"), _cand("realm_league")])
        assert head["class"] == "realm_league"


# ═════════════════════ the league's news on the page ══════════════════════════

class TestTheLeaguesNews:
    def test_a_sponsorship_against_us_leads_a_quiet_morning(self):
        """The CMD-H turn-24 shape (spec): London pays Vienna — the subsidy
        leads, with the price to keep her out."""
        world = _quiet_france()
        instruments.grant_directed_sponsorship(world, payer="Britain", recipient="Austria",
                                               aim="France", amount_per_turn=500)
        head = _page(world)
        assert head["class"] == "league_paid"
        assert head["text"].startswith("Sire — London now pays Vienna 500 gold a turn against us.")
        assert "the price to keep her out: Talleyrand brings her to −10" in head["text"]

    def test_a_burst_of_grants_is_one_line(self):
        world = _quiet_france()
        for payer, recipient in (("Britain", "Austria"), ("Britain", "Russia"), ("Russia", "Britain")):
            instruments.grant_directed_sponsorship(world, payer=payer, recipient=recipient,
                                                   aim="France", amount_per_turn=200)
        head = _page(world)
        lines = [head["text"]] + head["sub_beats"]
        paid = [t for t in lines if "against us" in t and "pays" in t]
        assert len(paid) == 1 and head["class"] == "league_paid"
        assert "London now pays Vienna and St Petersburg 200 gold a turn each" in paid[0] or \
            "London now pays" in paid[0]
        assert "St Petersburg now pays London" in paid[0]

    def test_a_great_power_newly_free_to_join(self):
        world = _quiet_france()
        world.headline_lead_memory = {"league": {"joiners": ["Britain", "Russia"], "bound": []}}
        head = _page(world)
        assert head["class"] == "league_joins"
        assert head["text"].startswith("Sire — Austria would now join a league against us — relations −50.")

    def test_the_first_morning_only_remembers(self):
        world = _quiet_france()
        head = _page(world)
        assert head["class"] != "league_joins"
        assert world.headline_lead_memory["league"]["joiners"] == ["Austria", "Britain", "Russia"]

    def test_the_fuse_at_eight_four_and_two_never_a_streak(self):
        world = _quiet_france(quiet=12)
        world.headline_lead_memory = {"league": {"joiners": ["Austria", "Britain", "Russia"],
                                                 "bound": []}}
        assert _page(world)["class"] == "league_fuse"
        assert _page(world)["class"] != "league_fuse", "told once at 8"
        for m in world.marshals.values():
            m.last_battle_turn = world.current_turn - 16
        head = _page(world)
        assert head["class"] == "league_fuse" and head["text"].startswith(
            "Sire — 4 more quiet turns and the courts of Europe re-arm.")

    def test_a_fresh_peace_binding_a_great_power_is_told(self):
        world = _quiet_france()
        world.headline_lead_memory = {"league": {"joiners": ["Austria", "Britain", "Russia"],
                                                 "bound": []}}
        inst = next(i for i in world.war_instances.values()
                    if world._make_diplo_key("France", "Austria") in (i.get("diplo_key_meta") or {}))
        meta = inst["diplo_key_meta"][world._make_diplo_key("France", "Austria")]
        meta["pair_status"], meta["resolved_turn"] = "resolved", world.current_turn
        lines = [_page(world)]
        texts = [lines[0]["text"]] + lines[0]["sub_beats"]
        assert any("our peace binds Austria for 5 more turns" in t for t in texts), texts


# ═════════════════════ SF7-X37 / X38 / X46 ════════════════════════════════════

def _truce(rel):
    world = _quiet_france()
    key = world._make_diplo_key("France", "Russia")
    world.diplomatic_states[key] = "ARMISTICE"
    world.nation_relations[key] = rel
    world.armistice_turns = {key: D.ARMISTICE_DURATION - 1}
    with _quiet():
        D._process_armistice_expiration(world)
    return world


class TestTheTruceEndingIsNews:
    def test_a_collapsed_truce_leads(self):
        head = _page(_truce(-90))
        assert head["class"] == "war_touches_us"
        assert head["text"] == "Sire — the truce with Russia has collapsed — the war resumes where it stood."

    def test_a_truce_ripened_into_peace_leads(self):
        head = _page(_truce(D.ARMISTICE_AUTO_PEACE_RELATION))
        assert head["class"] == "peace_signed"
        assert head["text"] == "Sire — peace with Russia is signed. The truce has ripened into peace."

    def test_lever_down_neither(self, monkeypatch):
        monkeypatch.setattr(dispatch, "A_TRUCES_END_IS_NEWS", False)
        assert _page(_truce(-90)).get("class") != "war_touches_us"


class TestTheRawKeysAreNamed:
    @pytest.mark.parametrize("etype,vars_,want", [
        ("diplomatic_treaty_signed", {"nation_a": "PapalStates", "nation_b": "France",
                                      "treaty_type": "Open Borders Agreement"},
         "Sire — the Papal States and France have signed the Open Borders Agreement."),
        ("blockade_begins", {"blockader": "Britain", "nation": "KingdomOfItaly", "trade_words": "halved"},
         "BLOCKADE: Britain closes the Kingdom of Italy's ports."),
        ("allegiance_in_play", {"nation": "PapalStates"}, "The allegiance of the Papal States is in play"),
        ("law_enacted_abroad", {"nation": "Ottoman", "verb": "enacts", "law": "the Nizam", "effect": "x"},
         "THE LAWS: the Ottoman Empire enacts the Nizam"),
        ("diplomatic_armistice_expired_war", {"nation_a": "KingdomOfItaly", "nation_b": "Austria"},
         "The armistice between the Kingdom of Italy and Austria has collapsed."),
    ])
    def test_the_template_names_the_court(self, etype, vars_, want):
        text = dispatch._format_dispatch_event_text(etype, vars_)
        assert text.startswith(want), text

    def test_the_relation_shift_names_the_court(self):
        world = _boot()
        world._relation_deltas_this_turn = {"KingdomOfItaly": 12}
        rows = dispatch._build_relation_change_events(world, "France")
        assert rows[0]["text"] == "Relations with the Kingdom of Italy have improved significantly (+12 this turn)."


class TestThePassageCountsItsSlack:
    def _lapse(self, turns_left):
        world = _boot()
        world.event_log = []
        world.marshals["Ney"].location = "Bohemia"
        world.log_event({"type": "evacuation_lapsing", "nation": "France", "marshal": "Ney",
                         "turns_left": turns_left, "region": "Bohemia",
                         "turn": world.current_turn})
        head = _page(world, record=False)
        return " ".join([head.get("text", "")] + head.get("sub_beats", []))

    def test_no_turn_to_spare(self):
        text = self._lapse(0)
        assert "the safe passage leaves no turn to spare — he must march today." in text
        assert "runs out in 0 turns" not in text

    def test_turns_to_spare(self):
        assert "the safe passage leaves 2 turns to spare." in self._lapse(2)

    def test_lever_down_is_the_old_sentence(self, monkeypatch):
        monkeypatch.setattr(dispatch, "THE_PASSAGE_COUNTS_ITS_SLACK", False)
        assert "the safe passage runs out in 0 turns." in self._lapse(0)


# ═════════════════════ the desk, the counsel, the ledger, the log ═════════════

@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    world = M.world
    france = world.player_nation
    world.active_coalition = None
    world.coalition_brewing = None
    for nation in world.get_active_nations():
        if nation == france:
            continue
        key = world._make_diplo_key(france, nation)
        if world.diplomatic_states.get(key) == "WAR":
            world.diplomatic_states[key] = "PEACE"
        if nation in ("Austria", "Britain", "Russia"):
            world.nation_relations[key] = -50
    world.invalidate_active_nations_cache()
    world.threat_by_target[france] = 45
    return TestClient(M.app), world


def _ask(client, text):
    with _quiet():
        return client.post("/command", json={"command": text}).json().get("message", "")


class TestTheDeskReadsTheLeague:
    def test_who_will_march_against_us(self, shipped):
        client, world = shipped
        msg = _ask(client, "who will march against us?")
        assert msg.startswith("Sire — "), msg
        assert "would march" in msg and "Austria — relations −50: she would join." in msg
        assert "The cheapest court to keep out of a league is" in msg

    def test_what_keeps_austria_out(self, shipped):
        client, world = shipped
        msg = _ask(client, "what keeps Austria out?")
        assert msg.startswith("Sire — Austria — relations −50: she would join."), msg
        assert "'improve relations with Austria'" in msg

    def test_the_alarm_names_the_league(self, shipped):
        client, world = shipped
        msg = _ask(client, "how alarmed is Europe?")
        assert "would march" in msg, msg

    def test_lever_down_the_desk_shrugs_the_league(self, shipped, monkeypatch):
        from backend.ai import question_desk as QD
        monkeypatch.setattr(QD, "THE_DESK_READS_THE_LEAGUE", False)
        client, world = shipped
        assert "would march" not in _ask(client, "who will march against us?")


class TestTheCounselNamesTheKeepOut:
    def test_at_peace_what_can_i_do_names_the_cheapest(self):
        """Prussia three points below the bar: with the gold, the buy-off
        alone (immediate) is the cheapest order; without it, Talleyrand's
        one-turn road — the buy-off's gate is the verb's."""
        from backend.ai.counsel import league_counsel, what_can_i_do
        world = _quiet_france()
        world.nation_relations[world._make_diplo_key("France", "Prussia")] = -13
        world.nation_gold["France"] = 99999
        line = league_counsel(world, "France")
        assert line and line[0].startswith(
            "buy off Prussia — keeps Prussia out of the next league: buying off her design ("), line
        assert any("out of the next league" in x for x in what_can_i_do(world, "France", limit=10))
        world.nation_gold["France"] = 0
        line = league_counsel(world, "France")
        assert line == ["improve relations with Prussia — keeps Prussia out of the next "
                        "league: Talleyrand brings her to −10 in 1 turn (1 DP)"], line

    def test_at_war_with_a_great_power_it_is_silent(self):
        from backend.ai.counsel import league_counsel
        world = _quiet_france()
        D.set_diplomatic_state(world, "France", "Austria", "WAR", "test")
        assert league_counsel(world, "France") == []


class TestTheLedgerAndTheLog:
    def test_the_balance_of_europe_tab_carries_the_table(self):
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        world = _quiet_france()
        boe = build_diplomatic_ledger(world)["balance_of_europe"]
        assert boe["league_rows"] and boe["league_line"]
        assert f"{instruments.INSTRUMENT_DP_COST} DP" in boe["league_footer"]
        assert f"{instruments.COMPENSATION_TERM_TURNS} turns" in boe["league_footer"]

    def test_the_dispatch_section_carries_the_line(self):
        world = _quiet_france()
        with _quiet():
            d = dispatch.build_morning_dispatch(world)
        assert d["coalition_status"]["league_line"] == CO.league_summary_line(world)
        assert d["coalition_status"]["league_rows"] == CO.league_rows(world)

    def test_the_courts_treaty_is_prose(self):
        from backend import campaign_log as CL
        line = CL.format_event_oneliner({"type": "diplomatic_ai_ai_treaty", "nation_a": "Sweden",
                                         "nation_b": "PapalStates",
                                         "treaty_type": "Defensive Alliance"})
        assert line == "Sweden and the Papal States sign a Defensive Alliance"

    def test_lever_down_the_old_line(self, monkeypatch):
        from backend import campaign_log as CL
        monkeypatch.setattr(CL, "THE_COURTS_TREATIES_READ_AS_PROSE", False)
        line = CL.format_event_oneliner({"type": "diplomatic_ai_ai_treaty", "nation_a": "Sweden",
                                         "nation_b": "Austria", "treaty_type": "Defensive Alliance"})
        assert line == "AI-AI treaty: Sweden and Austria (Defensive Alliance)"


# ═════════════════════ the three commanded arms, driven ═══════════════════════

ARMS = {"CMD-H": "historical", "CMD-A": "austerlitz", "CMD-M": "marengo"}
LEVERS_DOWN = ["backend.game_logic.dispatch:EVERY_MORNING_HAS_A_FRONT_PAGE=0",
               "backend.game_logic.coalition:THE_LEAGUE_IS_SEEN=0",
               "backend.game_logic.dispatch:THE_PASSAGE_COUNTS_ITS_SLACK=0",
               "backend.game_logic.withdrawal:THE_PASSAGE_COUNTS_ITS_SLACK=0"]


@pytest.fixture(scope="module")
def driven(tmp_path_factory):
    """The three commanded arms (the instrument's own argv) and CMD-H with
    every Step 7b page lever down, in parallel; then `score_run.py check`
    on the run — the instrument's own readers and probes."""
    run = tmp_path_factory.mktemp("sf7b_run")
    arms_dir = run / "arms"
    arms_dir.mkdir()
    env = dict(os.environ, PYTHONHASHSEED="0", LLM_MODE="mock", PYTHONIOENCODING="utf-8")
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START", "SOVEREIGN_SEED"):
        env.pop(key, None)
    procs = []
    jobs = [(name, seed, []) for name, seed in ARMS.items()] + [("CMD-H-DOWN", "historical", LEVERS_DOWN)]
    for name, seed, levers in jobs:
        out = arms_dir if not levers else run / "down"
        out.mkdir(exist_ok=True)
        argv = [sys.executable, str(REPO / "tools" / "playtest_driver.py"), "--name", name,
                "--fresh", "--out", str(out), "--llm", "mock", "--script", str(SCRIPT),
                "--turns", "40", "--diplomacy", "accept", "--save-at", "10,20,30,40",
                "--seed", seed]
        for lever in levers:
            argv += ["--lever", lever]
        procs.append(subprocess.Popen(
            argv, cwd=str(REPO), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            env=dict(env, INK_IRON_SAVE_DIR=str(run / f"_saves_{name}"))))
    for p in procs:
        assert p.wait(timeout=1500) == 0
    check = subprocess.run([sys.executable, str(REPO / "tools" / "score_run.py"), "check",
                            "--run", str(run)], cwd=str(REPO), env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=1500)
    assert check.returncode == 0, check.stdout[-2000:] + check.stderr[-2000:]
    checklist = json.loads((run / "checklist.json").read_text(encoding="utf-8"))
    return run, checklist


def _item(checklist, pillar, item):
    pp = checklist["pillars"][pillar]
    items = pp["items"] if isinstance(pp, dict) and "items" in pp else pp
    return next(i for i in items if i.get("id") == item)


def _records(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _pages(path):
    out, turn = [], None
    for r in _records(path):
        if r.get("kind") == "turn":
            turn = r.get("turn")
        if r.get("kind") == "dispatch":
            out.append((turn, r))
    return out


class TestTheDrivenArms:
    def test_no_turn_without_a_headline_and_no_raw_key(self, driven):
        _run, checklist = driven
        f1 = _item(checklist, "narration", "F1")
        assert f1["measured"] and f1["pass"], f1["evidence"]
        assert all(v.startswith("0/40") for v in json.loads(f1["evidence"]).values())

    def test_no_class_leads_more_than_four_of_ten(self, driven):
        _run, checklist = driven
        c1 = _item(checklist, "narration", "C1")
        assert c1["measured"] and c1["pass"], c1["evidence"]

    def test_the_league_reaches_the_page_and_every_quoted_lever_flips(self, driven):
        _run, checklist = driven
        c5 = _item(checklist, "living_balance", "C5")
        assert c5["measured"] and c5["pass"], c5["evidence"]

    def test_a_standing_crisis_is_on_the_page_every_turn_it_stands(self, driven):
        run, _checklist = driven
        nag = re.compile(r"arrears|unrewarded|without settlement|household goes unpaid|claim is")
        for name in ARMS:
            pages = _pages(run / "arms" / name / "digest.jsonl")
            on = [t for t, r in pages
                  if any(nag.search(x) for x in [r.get("headline_text") or ""] + list(r.get("sub_beats") or []))]
            assert on, name
            gaps = [t for t, r in pages if on[0] <= t <= on[-1] and t not in on]
            assert gaps == [], (name, gaps)

    def test_the_driver_records_the_whole_page(self, driven):
        run, _checklist = driven
        records = [r for _t, r in _pages(run / "arms" / "CMD-H" / "digest.jsonl")]
        assert all("sub_beats" in r and "headline_text" in r for r in records)
        assert any(r.get("league_rows") for r in records)

    def test_every_lever_down_is_the_step_7_page(self, driven):
        """CMD-H with every Step 7b page lever down reproduces the Step 7
        final reading's headlines and classes, turn for turn."""
        run, _checklist = driven
        down = [(t, r.get("headline"), r.get("headline_class"))
                for t, r in _pages(run / "down" / "CMD-H-DOWN" / "digest.jsonl")]
        archived = [(t, r.get("headline"), r.get("headline_class"))
                    for t, r in _pages(ARCHIVE / "CMD-H" / "digest.jsonl")]
        assert down == archived


# ═════════════════════ the sweep's own pins ═══════════════════════════════════

def _sitting_congress():
    """The staged sitting Congress of the refusing-court pin (minors titled
    by treaty up to the count, then the summons)."""
    w = _quiet_france(threat=30, quiet=5)
    need = congress.hold_titled(w)
    for nation in ("Hanover", "Denmark", "Portugal", "Sardinia", "Naples",
                   "Saxony", "Hesse", "Holland", "Switzerland"):
        for region in sorted(w.get_nation_regions(nation)):
            if congress.titled(w)["count"] >= need:
                break
            if region == "Lisbon":
                continue
            w.regions[region].controller = "France"
            game_end.record_province_title(w, region, game_end.TITLE_TREATY, nation, "France")
    w.invalidate_active_nations_cache()
    w.diplomatic_points = 6
    with _quiet():
        assert congress.summon(w)["success"]
    return w


class TestTheEdges:
    def test_the_cooldown_holds_the_consult(self):
        world = _quiet_france(turn=30, threat=59, quiet=25)
        assert CO.league_forecast(world)["consult_turns"] == 1
        world.coalition_cooldown = 3
        forecast = CO.league_forecast(world)
        assert forecast["consult_turns"] == 3
        played = copy.deepcopy(world)
        brewed = None
        for k in range(1, 10):
            _tick(played)
            if played.coalition_brewing:
                brewed = k
                break
        assert brewed == 3

    def test_a_road_that_closes_on_the_declaration_is_in_time(self):
        """The mission ticks before the coalition's check in the same
        advance, so a road of exactly `declare` turns keeps her out."""
        world = _quiet_france(turn=30, threat=57, quiet=25, rel=-46)
        forecast = CO.league_forecast(world)
        row = next(r for r in forecast["courts"] if r["nation"] == "Russia")
        assert row["road"][0] == forecast["declare_turns"]
        assert not row["out_of_time"]

    def test_a_grant_is_told_once(self):
        world = _quiet_france()
        instruments.grant_directed_sponsorship(world, payer="Britain", recipient="Austria",
                                               aim="France", amount_per_turn=500)
        assert _page(world)["class"] == "league_paid"
        world.current_turn += 1
        page = _page(world)
        assert page["class"] != "league_paid"
        assert not any("now pays" in b for b in page.get("sub_beats") or [])

    def test_only_our_titles_ride_her_row(self):
        world = _quiet_france()
        for region, frm, house in (("Tyrol", "Austria", "France"), ("Lorraine", "France", "Austria")):
            world.regions[region].controller = house
            game_end.record_province_title(world, region, game_end.TITLE_TREATY, frm, house)
        row = next(r for r in CO.league_forecast(world)["courts"] if r["nation"] == "Austria")
        assert row["titles"] == ["Tyrol"]
        assert game_end.treaty_titles_between(world, "Austria", "France") == ["Lorraine", "Tyrol"]

    def test_the_road_starts_where_it_is_told(self):
        world = _quiet_france()
        full = D.courtship_road(world, "Austria", -10)
        short = D.courtship_road(world, "Austria", -10, start=-20)
        assert short[0] < full[0]
        row = next(r for r in CO.league_forecast(world)["courts"] if r["nation"] == "Austria")
        assert row["road_with_buyoff"] == D.courtship_road(world, "Austria", -10, start=-45)

    def test_a_refuser_with_cold_relations_is_still_a_refuser(self):
        """Austria at −50 refusing the Congress: the shift that would lift
        her relations does not keep her out — the refuser's arm does."""
        w = _sitting_congress()
        austria = next(r for r in CO.league_forecast(w)["courts"] if r["nation"] == "Austria")
        assert austria["relation"] == -50 and austria["status"] == CO.LEAGUE_REFUSES

    def test_the_withdrawal_warning_counts_its_slack(self, monkeypatch):
        from backend.game_logic import withdrawal as W
        world = _boot()
        ney = world.marshals["Ney"]
        msg = W._warn(world, ney, "France", 2, 0)["message"]
        assert "no turn to spare on the safe passage before his corps is interned." in msg
        monkeypatch.setattr(W, "THE_PASSAGE_COUNTS_ITS_SLACK", False)
        assert "0 turns of safe passage left" in W._warn(world, ney, "France", 2, 0)["message"]


class TestTheInstrumentReadsTheWholePage:
    MORNING = {"headline": {"class": "courts_laws", "text": "Sire — Britain enacts a law.",
                            "sub_beats": ["Sire — London now pays Vienna 200 gold a turn against us."]},
               "coalition_status": {"league_line": "At this pace the courts consult on turn 31.",
                                    "league_rows": [{"nation": "Austria", "status": "joins",
                                                     "major": True, "text": "Austria — x"}]}}

    def _record(self, morning, monkeypatch, lever=True):
        import tools.playtest_driver as PD
        if not lever:
            monkeypatch.setattr(PD, "THE_DIGEST_READS_THE_WHOLE_PAGE", False)
        seen = {}

        class _Digest:
            def dispatch(self, text, events=None, turn_events=None, headline_class="",
                         page=None):
                seen.update(text=text, page=page)

        PD._record_morning_headline(_Digest(), morning)
        return seen

    def test_the_driver_records_the_whole_page(self, monkeypatch):
        page = self._record(self.MORNING, monkeypatch)["page"]
        assert page["sub_beats"] == ["Sire — London now pays Vienna 200 gold a turn against us."]
        assert page["league_rows"][0]["nation"] == "Austria"
        assert page["league_line"].startswith("At this pace")
        assert page["headline_text"] == "Sire — Britain enacts a law."

    def test_lever_down_the_record_is_as_it_was(self, monkeypatch):
        assert self._record(self.MORNING, monkeypatch, lever=False)["page"] is None

    def test_the_probe_reads_a_sub_beat(self, monkeypatch, tmp_path):
        """A sponsorship told in a SUB-BEAT is on the page; the first probe
        read the headline line only and called it missed."""
        import tools._score_probes as SP
        import tools.score_run as SR
        arm = tmp_path / "arms" / "CMD-H"
        arm.mkdir(parents=True)
        (arm / "meta.json").write_text(json.dumps({"status": "completed"}), encoding="utf-8")
        recs = [{"kind": "turn", "turn": 1},
                {"kind": "dispatch", "headline": "Sire — x.", "headline_text": "Sire — x.",
                 "sub_beats": [], "league_rows": [], "league_line": ""},
                {"kind": "turn", "turn": 2},
                {"kind": "campaign_log",
                 "text": "sponsorship_granted: Britain sponsors Austria against France (200g/turn)"},
                {"kind": "dispatch", "headline": "Sire — Britain enacts a law.",
                 "headline_text": "Sire — Britain enacts a law.",
                 "sub_beats": ["Sire — London now pays Vienna 200 gold a turn against us."],
                 "league_rows": [], "league_line": ""}]
        (arm / "digest.jsonl").write_text("\n".join(json.dumps(r) for r in recs),
                                          encoding="utf-8")
        (arm / "digest.md").write_text(
            "# digest\n## Turn 1 — x\n  - LOG Treaty signed: France → Peace with Austria\n"
            "## Turn 2 — y\n", encoding="utf-8")
        arms = SR.load_arms(tmp_path)
        monkeypatch.setattr(SP, "_c5_quoted_levers_flip", lambda arms, ctx, peace: (1, 1, []))
        ctx = {"run_dir": tmp_path, "arms": arms}
        result = SP.living_balance_c5_front_page(arms, ctx)
        assert result["measured"] and result["pass"], result
        monkeypatch.setattr(SP, "THE_PROBE_READS_THE_WHOLE_PAGE", False)
        assert SP.living_balance_c5_front_page(arms, ctx)["pass"] is False


# ═════════════════════ SF7-X47 — the first morning's list is a choice ═════════

class TestTheTodayListIsAChoice:
    """SF7-X47 (found reading the Step 7b exit's re-check): the boot
    briefing printed "Orders the board will take at once:" over four orders
    that, typed top to bottom on one boot, refuse each other — Ney's attack
    draws Davout into the field (his march: "engaged with Mack") and its
    materiel bill leaves the levy unpaid. The header now says the list is a
    choice; both screens render the backend's sentence."""

    def _today(self):
        w = _boot()
        with _quiet():
            return dispatch.build_morning_dispatch(w, boot=True)["today"], w

    def test_the_header_names_the_choice(self):
        today, _w = self._today()
        assert today["orders"], "the boot board always has an order to give"
        assert today["orders_header"] == dispatch.TODAY_ORDERS_HEADER
        assert "choose among them" in today["orders_header"]
        assert "one treasury and one army" in today["orders_header"]

    def test_the_list_is_not_a_plan(self):
        """Why the header must say so, on the shipped boot: the priced lines
        alone ask more gold than the treasury holds. If this ever reds, the
        list became affordable — re-read the header, do not just re-pin."""
        today, w = self._today()
        asked = 0
        for line in today["orders"]:
            m = re.search(r"— ([\d,]+)g\b", line)
            if m:
                asked += int(m.group(1).replace(",", ""))
        assert asked > int(w.nation_gold[w.player_nation]), (asked, today["orders"])

    def test_both_screens_render_the_backends_header(self):
        for rel in ("main.gd", "dispatch_view.gd"):
            src = (REPO / "godot-client" / "project-sovereign" / "scripts" / rel).read_text(
                encoding="utf-8")
            assert 'today.get("orders_header"' in src, rel
            assert ']  Orders the board will take at once:[/color]' not in src, rel

    def test_lever_down_the_old_header(self, monkeypatch):
        monkeypatch.setattr(dispatch, "THE_TODAY_LIST_IS_A_CHOICE", False)
        today, _w = self._today()
        assert today["orders_header"] == "Orders the board will take at once:"


# ═════════════════════ the first morning and the quiet close ═════════════════

class TestTheFirstMorningAndTheQuietClose:
    """Two of the front page's own edges, caught by the related suites
    before the commit: the boot briefing led "a quiet morning on the front"
    over a campaign that had not begun (the desk lost "the campaign has just
    opened" — `test_crt7_the_desk_reads_the_order.py::TestTheNews`), and a
    quiet morning closed on "the levy among them" when no levy stood
    (FA-N29's "Your armies stand ready" silenced —
    `test_fa_slice17_d_the_status_tells_the_truth_2026_09_11.py`)."""

    QUIET = dispatch._HEADLINE_BERTHIER_NOTES["quiet_morning"]

    def _boot_page(self):
        w = _boot()
        with _quiet():
            return dispatch.build_morning_dispatch(w, boot=True)

    def test_the_first_morning_keeps_its_own_front_page(self):
        d = self._boot_page()
        assert "headline" not in d, d.get("headline")
        assert d["today"]["orders"], "the first morning's front page is TODAY"

    def test_lever_down_the_first_morning_reads_quiet(self, monkeypatch):
        monkeypatch.setattr(dispatch, "THE_FIRST_MORNING_KEEPS_ITS_OWN_FRONT_PAGE", False)
        assert self._boot_page()["headline"]["class"] == "quiet_morning"

    def _close(self, monkeypatch, levy_said):
        w = _boot()
        w.current_turn = 12
        quiet = {"class": "quiet_morning", "weight": 5, "sub_beats": [],
                 "text": dispatch._HEADLINE_TEMPLATES["quiet_morning"]}
        monkeypatch.setattr(dispatch, "_build_headline", lambda *a, **k: dict(quiet))
        w.headline_lead_memory = {"levy_said": levy_said} if levy_said else {}
        with _quiet():
            return dispatch.build_morning_dispatch(w)["berthier_note"]

    def test_a_quiet_morning_closes_on_the_ladder(self, monkeypatch):
        note = self._close(monkeypatch, None)
        assert self.QUIET not in note, note

    def test_the_levy_note_stands_while_the_levy_yields(self, monkeypatch):
        assert self._close(monkeypatch, {"count": 3}).startswith(self.QUIET)

    def test_lever_down_the_quiet_note_always(self, monkeypatch):
        monkeypatch.setattr(dispatch, "A_QUIET_MORNING_CLOSES_ON_THE_LADDER", False)
        assert self._close(monkeypatch, None).startswith(self.QUIET)


# ═════════════════════ SF7-X48 — the alarm has one name ══════════════════════

class TestTheAlarmHasOneName:
    """SF7-X48 (found shooting Step 7b's frames): the Balance of Europe tab
    printed "45 / 100 [MODERATE]" beside a dispatch reading "45/100
    [Murmurs]" — two names for one alarm. The tab keeps its severity band
    for the colour and the pulse, and prints the dispatch's own name."""

    def _both(self, world):
        from backend.game_logic.diplomatic_ledger import _build_balance_of_europe
        with _quiet():
            boe = _build_balance_of_europe(world)
            section = dispatch._build_coalition_section(world, "France") or {}
        return boe, section

    def test_one_alarm_one_name_at_murmurs(self):
        boe, section = self._both(_quiet_france(threat=45))
        assert boe["threat_name"] == section["tier"] == "Murmurs", (boe["threat_name"], section)
        assert boe["threat_tier"] == "MODERATE", "the band still colours the bar"

    def test_one_alarm_one_name_when_it_brews(self):
        boe, section = self._both(_quiet_france(threat=65))
        assert boe["threat_name"] == section["tier"] == "Brewing"

    def test_a_formed_league_is_formed_on_both(self):
        w = _quiet_france(threat=70)
        w.active_coalition = {"name": "Fourth Coalition", "leader": "Britain",
                              "members": ["Britain", "Austria"], "target_nation": "France"}
        boe, section = self._both(w)
        assert boe["threat_name"] == section["tier"] == "Formed"

    def test_the_congress_gate_names_it_brewing_on_both(self):
        """A sitting Congress that two great powers refuse lowers the brewing
        gate (`coalition.brewing_gate`): the same alarm brews earlier, and
        both surfaces say so."""
        w = _sitting_congress()
        w.threat_by_target["France"] = 45
        gate = CO.brewing_gate(w)
        boe, section = self._both(w)
        expected = "Brewing" if 45 >= gate else "Murmurs"
        assert boe["threat_name"] == section["tier"] == expected, (gate, boe["threat_name"])
        assert CO.threat_tier_name(w, 45) == CO.get_threat_tier(45, brewing_at=gate)

    def test_lever_down_the_tab_names_the_band(self, monkeypatch):
        from backend.game_logic import diplomatic_ledger as DL
        monkeypatch.setattr(DL, "THE_ALARM_HAS_ONE_NAME", False)
        boe, _section = self._both(_quiet_france(threat=45))
        assert boe["threat_name"] == ""

    def test_the_client_prints_the_name_and_reds_a_brewing_league(self):
        scripts = REPO / "godot-client" / "project-sovereign" / "scripts"
        ledger = (scripts / "diplomatic_ledger.gd").read_text(encoding="utf-8")
        assert 'boe.get("threat_name", "")' in ledger
        assert 'var tier_shown = threat_name if threat_name != "" else threat_tier' in ledger
        assert '" / 100  [" + tier_shown + "]' in ledger
        for rel in ("dispatch_view.gd", "main.gd"):
            src = (scripts / rel).read_text(encoding="utf-8")
            assert 'tier in ["Brewing", "Formed", "CRITICAL", "HIGH"]' in src, rel


# ═════════════════════ the frames' own instrument ════════════════════════════

class TestTheFramesRunnerKeepsTheRowsSteps:
    """Found shooting Step 7b's frames: the IQ-10 runner REPLACED a row's own
    `steps` with its tab switch, so THE NEXT LEAGUE's scroll never ran and the
    scale-2.0 frame showed the tab's top in silence (the first row ever to
    carry both)."""

    def _runner(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_iq10_runner_7b", REPO / "tools" / "iq10_run_captures.py")
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        return runner

    def test_a_tab_and_the_rows_steps_compose(self, tmp_path):
        runner = self._runner()
        row = next(r for r in runner.SHOTS if r["id"] == "diplo_balance_next_league")
        caps = {row["payload"]: {"file": "x.json", "staging": "", "facts": {}}}
        built, _index = runner.build_spec([row], caps, [1.0], "pin", tmp_path / "spec.json",
                                          tmp_path / "result.json")
        steps = built["shots"][0]["steps"]
        assert steps[0] == {"call": "_switch_tab", "args": [2], "then_wait": 4}, steps
        assert steps[1:] == row["steps"], steps
