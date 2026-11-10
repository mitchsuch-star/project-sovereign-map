"""DY-1 — the Alarm of Europe (`DYNAMISM_SPEC.md` §3; the Tier-4 gate record
§3c, ruled November 9, 2026 in Plan Mode; the rules `SYSTEMS_REFERENCE.md`
§199). One file for the tier (§3b: DY-1b and DY-1c ride it as they land).

T4-1 — the Alarm (`backend/game_logic/alarm.py`, seams `the_alarm_sounds` and
`an_alarmed_court_guarantees` in `tests/_t3_seams.py` row T4-1):

* THE WRITE (§3c G1): an AI court's capture writes Europe's alarm against its
  HOUSE at the one capture chokepoint — 6 a province, 12 a capital, 8 a third
  court's client — on top of the +2 every conqueror already paid (census
  correction C1), under the same three skips; the player's house writes
  nothing new; the auto-charge mirror writes it too; event-driven, no scan.
* THE GUARANTEE RUNG (§3c G2): a court alarmed by a conqueror pledges the
  existing D5 guarantee for the likely next victim — a DEFENDING ward's
  guarantor marches at the instruments tick (the Fürstenbund); a ward that
  declared its own war (Bavaria in 1805 — census correction C2) is neither
  marched for nor branded.
* THE BREW (§3c G3): D3 untouched — past its gates the alarm carries a
  non-France conqueror into the eclipse brew.
* THE WORDS (§3c G4, Q6): "Vienna's appetite is remarked in Berlin …" —
  Talleyrand, the Balance tab, Le Moniteur; never a figure.
"""
from __future__ import annotations

import inspect
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.game_logic import alarm as AL  # noqa: E402
from backend.game_logic import instruments as INS  # noqa: E402
from tests._t3_seams import T3_SEAMS_BY_ROW, hold_down  # noqa: E402

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")
T4_1_DOWN = T3_SEAMS_BY_ROW["T4-1"]


@pytest.fixture()
def world():
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(str(SCENARIO), seed="historical")


def _slot(world, nation: str) -> int:
    return int((world.threat_by_target or {}).get(nation, 0) or 0)


def _alarm_rows(world):
    return [row for row in (world.threat_sources_this_turn or [])
            if str(row.get("source", "")).startswith("alarm:")]


def _relation(world, a: str, b: str, value: int) -> None:
    world.nation_relations[world._make_diplo_key(a, b)] = int(value)


def _alarmed(world, nation: str = "Austria", value: int = 40) -> None:
    world.threat_by_target[nation] = int(value)


def _austria_takes(world, region_name: str) -> None:
    world.capture_region(region_name, "Austria")


# ═══════════════════════════════════════════════════════════════════════
# The write — G1
# ═══════════════════════════════════════════════════════════════════════

class TestTheWrite:
    def test_a_province_writes_six_above_the_two(self, world):
        before = _slot(world, "Austria")
        _austria_takes(world, "Swabia")
        assert _slot(world, "Austria") - before == 2 + AL.ALARM_PROVINCE
        rows = _alarm_rows(world)
        assert [(r["source"], r["amount"], r["target"]) for r in rows] == [
            ("alarm:Swabia", AL.ALARM_PROVINCE, "Austria")]

    def test_a_capital_writes_twelve(self, world):
        before = _slot(world, "Austria")
        _austria_takes(world, "Munich")
        assert _slot(world, "Austria") - before == 2 + AL.ALARM_CAPITAL

    def test_a_third_courts_client_writes_eight(self, world):
        # Piedmont is the Kingdom of Italy's, a client of France's.
        assert world._top_overlord("KingdomOfItaly") == "France"
        before = _slot(world, "Austria")
        _austria_takes(world, "Piedmont")
        assert _slot(world, "Austria") - before == 2 + AL.ALARM_CLIENT

    def test_the_numbers_are_the_gates(self):
        assert (AL.ALARM_PROVINCE, AL.ALARM_CAPITAL, AL.ALARM_CLIENT) == (6, 12, 8)
        assert AL.ALARM_GUARANTEE_COOLDOWN_TURNS == 12

    def test_own_soil_writes_nothing(self, world):
        world.regions["Vienna"].controller = "France"
        world.invalidate_active_nations_cache()
        _austria_takes(world, "Vienna")
        assert _alarm_rows(world) == []

    def test_a_recovered_title_writes_nothing(self, world):
        from backend.game_logic import game_end as GE
        GE.record_province_title(world, "Swabia", GE.TITLE_TREATY, "Bavaria", "Austria")
        _austria_takes(world, "Swabia")
        assert _alarm_rows(world) == []

    def test_a_liberation_writes_nothing(self, world, monkeypatch):
        from backend.models import world_state as WS
        monkeypatch.setattr(WS, "liberates_ally_ground",
                            lambda w, region, capturer: "Bavaria")
        world.regions["Swabia"].controller = "France"
        _austria_takes(world, "Swabia")
        assert _alarm_rows(world) == []

    def test_the_players_capture_writes_nothing_new(self, world):
        world.capture_region("Tyrol", "France")
        assert _alarm_rows(world) == []

    def test_the_players_client_writes_nothing_new(self, world):
        world.capture_region("Tyrol", "KingdomOfItaly")
        assert _alarm_rows(world) == []

    def test_a_client_alarms_against_its_lords_house(self, world):
        world.vassals["Hesse"] = {"lord": "Prussia"}
        world.capture_region("Franconia", "Hesse")
        rows = _alarm_rows(world)
        assert [(r["target"], r["amount"]) for r in rows] == [("Prussia", AL.ALARM_PROVINCE)]

    def test_the_seam_down_writes_nothing(self, world, monkeypatch):
        hold_down(monkeypatch, T4_1_DOWN)
        before = _slot(world, "Austria")
        _austria_takes(world, "Swabia")
        assert _slot(world, "Austria") - before == 2
        assert _alarm_rows(world) == []

    def test_the_auto_charge_mirror_writes_through_the_same_writer(self):
        # The one conquest outside capture_region mirrors every capture
        # write; the alarm rides it, reading the prior title BEFORE the
        # charge's own title record overwrites it (the sibling sweep).
        from backend.models import world_state as WS
        src = inspect.getsource(WS)
        read = src.index("_ac_prior_title = dict(")
        title = src.index("_ge.record_province_title(\n"
                          "                                self, auto_charge_battle_region")
        call = src.index("_ac_alarm.sound_the_alarm(")
        assert read < title < call
        assert "prior_title=_ac_prior_title" in src[call:call + 400]


class TestTheScaleContract:
    """Golden Rule 8: the write is event-driven at the chokepoint, and the
    module never scans the regions."""

    def test_the_module_never_walks_the_map(self):
        src = inspect.getsource(AL)
        for scan in ("regions.values()", "regions.items()", "in world.regions"):
            assert scan not in src, scan

    def test_the_write_reads_no_roster(self, world, monkeypatch):
        def _boom(*_a, **_k):
            raise AssertionError("the write must not derive victims")
        monkeypatch.setattr(AL, "_eaten_from", _boom)
        monkeypatch.setattr(AL, "alarming_conquerors", _boom)
        assert AL.sound_the_alarm(world, "Swabia", "Austria", "Bavaria",
                                  liberated=False, prior_title={}) == AL.ALARM_PROVINCE


# ═══════════════════════════════════════════════════════════════════════
# The guarantee rung — G2
# ═══════════════════════════════════════════════════════════════════════

def _boot_war_board(world):
    """1805: Austria holds Swabia of Bavaria — Bavaria the war's ATTACKER (it
    marched beside France); Prussia, at peace, borders Franconia."""
    _austria_takes(world, "Swabia")
    _alarmed(world)
    _relation(world, "Prussia", "Austria", 0)
    _relation(world, "Prussia", "Bavaria", 0)


def _defensive_board(world):
    """Austria declares on Hesse — alone, its allies' cascade held — and
    holds Nassau: Hesse DEFENDS against Austria only; Prussia, at peace,
    borders Frankfurt. (With the cascade, Britain and Russia join and the
    word would bind Prussia against them too — the conqueror-alone rule.)"""
    from backend.game_logic.diplomacy import declare_war
    assert declare_war(world, "Austria", "Hesse", war_objective="conquest",
                       suppress_unresolved_offensive_cascade=True).get("success")
    assert world.get_nations_at_war_with("Hesse") == ["Austria"]
    _austria_takes(world, "Nassau")
    _alarmed(world)
    _relation(world, "Prussia", "Austria", 0)
    _relation(world, "Prussia", "Hesse", 0)


class TestTheRung:
    def test_the_alarmed_neighbour_gives_its_word(self, world):
        _boot_war_board(world)
        assert AL.likely_next_victim(world, "Austria") == "Bavaria"
        events = AL.process_alarm_guarantees(world)
        assert [(e["guarantor"], e["protected"], e["against"]) for e in events] == [
            ("Prussia", "Bavaria", "Austria")]
        assert events[0]["message"] == "Prussia guarantees Bavaria against Austria's appetite."
        logged = [e for e in world.event_log if e.get("type") == "guarantee_pledged"]
        assert logged[-1]["against"] == "Austria"
        assert "Prussia" in INS.guarantors_of(world, "Bavaria")
        assert world._ai_guarantee_this_turn == world.current_turn
        assert world.ai_proposal_cooldowns.get("Prussia|alarm_guarantee") == 12

    def test_a_ward_that_declared_its_war_is_neither_marched_for_nor_branded(self, world):
        _boot_war_board(world)
        AL.process_alarm_guarantees(world)
        INS.process_instruments(world)
        assert not world.is_at_war("Prussia", "Austria")
        assert not [e for e in world.event_log
                    if e.get("type") in ("guarantee_abandoned", "guarantee_honored")]
        assert "Prussia" in INS.guarantors_of(world, "Bavaria")

    def test_a_defending_wards_guarantor_marches_at_the_tick(self, world):
        _defensive_board(world)
        assert AL.likely_next_victim(world, "Austria") == "Hesse"
        events = AL.process_alarm_guarantees(world)
        assert [(e["guarantor"], e["protected"]) for e in events] == [("Prussia", "Hesse")]
        INS.process_instruments(world)
        assert world.is_at_war("Prussia", "Austria")
        honoured = [e for e in world.event_log if e.get("type") == "guarantee_honored"]
        assert [(e["guarantor"], e["ward"], e["aggressor"]) for e in honoured] == [
            ("Prussia", "Hesse", "Austria")]

    def test_the_word_answers_the_conqueror_alone(self, world, monkeypatch):
        """The measure's own catch: Prussia holds Bohemia and the Porte —
        secondary, at peace, Austria's neighbour — would give its word for
        Austria; but Austria defends against France, Bavaria and the Kingdom
        of Italy, and the word would march the Porte on France. The alarm is
        about Prussia: no word whose exposure names another court."""
        world.regions["Bohemia"].controller = "Prussia"
        world.invalidate_active_nations_cache()
        _alarmed(world, "Prussia")
        assert AL.likely_next_victim(world, "Prussia") == "Austria"
        assert "France" in INS.guarantee_exposure(world, "Ottoman", "Austria")
        assert AL.alarmed_guarantor(world, "Prussia", "Austria") is None
        monkeypatch.setattr(INS, "guarantee_exposure", lambda w, g, p: [])
        assert AL.alarmed_guarantor(world, "Prussia", "Austria") == "Ottoman"

    def test_a_ward_fighting_the_conquerors_allies_too_is_not_given_a_word(self, world):
        from backend.game_logic.diplomacy import declare_war
        assert declare_war(world, "Austria", "Hesse", war_objective="conquest").get("success")
        assert set(world.get_nations_at_war_with("Hesse")) == {"Austria", "Britain", "Russia"}
        _austria_takes(world, "Nassau")
        _alarmed(world)
        assert AL.alarmed_guarantor(world, "Austria", "Hesse") is None

    def test_below_the_notice_line_nobody_pledges(self, world):
        _boot_war_board(world)
        _alarmed(world, value=29)
        assert AL.process_alarm_guarantees(world) == []

    def test_a_friend_of_the_conqueror_never_pledges(self, world):
        _boot_war_board(world)
        _relation(world, "Prussia", "Austria", 10)
        assert AL.process_alarm_guarantees(world) == []

    def test_an_enemy_of_the_victim_never_pledges(self, world):
        _boot_war_board(world)
        _relation(world, "Prussia", "Bavaria", -5)
        assert AL.process_alarm_guarantees(world) == []

    def test_a_minor_never_promises(self, world):
        # Saxony and Hesse border Bavaria too; with Prussia out of the way
        # (a friend of Vienna's) no minor steps forward.
        _boot_war_board(world)
        _relation(world, "Prussia", "Austria", 10)
        _relation(world, "Saxony", "Austria", -50)
        _relation(world, "Hesse", "Austria", -50)
        assert AL.alarmed_guarantor(world, "Austria", "Bavaria") is None

    def test_a_court_at_war_has_no_hand_free(self, world):
        from backend.game_logic.diplomacy import declare_war
        _boot_war_board(world)
        assert declare_war(world, "Prussia", "Hanover", war_objective="conquest").get("success")
        assert AL.alarmed_guarantor(world, "Austria", "Bavaria") is None

    def test_one_ai_guarantee_a_turn_shared_with_the_crisis_producer(self, world):
        _boot_war_board(world)
        world._ai_guarantee_this_turn = world.current_turn
        assert AL.process_alarm_guarantees(world) == []

    def test_the_guarantor_rests_on_its_cooldown(self, world):
        _boot_war_board(world)
        world.ai_proposal_cooldowns = {"Prussia|alarm_guarantee": 3}
        assert AL.process_alarm_guarantees(world) == []

    def test_a_guaranteed_court_is_protection_enough(self, world):
        _boot_war_board(world)
        INS.pledge_guarantee(world, guarantor="Russia", protected="Bavaria")
        assert AL.likely_next_victim(world, "Austria") is None

    def test_the_players_house_is_never_a_ward(self, world):
        # Piedmont is the Kingdom of Italy's — France's client: no AI court
        # answers for the human's wards.
        _austria_takes(world, "Piedmont")
        _alarmed(world)
        assert AL.likely_next_victim(world, "Austria") is None

    def test_with_nothing_eaten_the_victim_is_the_defenceless_prize(self, world, monkeypatch):
        from backend.game_logic import war_council as WC
        _alarmed(world)
        monkeypatch.setattr(WC, "defenceless_prize", lambda w, coveter, view=None: "Saxony")
        assert AL.likely_next_victim(world, "Austria") == "Saxony"

    def test_the_seam_down_pledges_nothing(self, world, monkeypatch):
        _boot_war_board(world)
        hold_down(monkeypatch, T4_1_DOWN)
        assert AL.process_alarm_guarantees(world) == []

    def test_the_rung_rides_the_ai_ai_phase(self, world):
        from backend.game_logic.ai_diplomacy import process_ai_ai_diplomatic_phase
        _boot_war_board(world)
        events = process_ai_ai_diplomatic_phase(world)
        assert any(e.get("type") == "guarantee_pledged" and e.get("by") == "alarm"
                   for e in events)

    def test_the_player_and_crisis_pledges_log_what_they_logged(self, world):
        INS.pledge_guarantee(world, guarantor="Russia", protected="Saxony")
        logged = [e for e in world.event_log if e.get("type") == "guarantee_pledged"][-1]
        assert set(logged) == {"type", "guarantor", "protected", "turn"}


# ═══════════════════════════════════════════════════════════════════════
# The brew — G3 (D3 untouched)
# ═══════════════════════════════════════════════════════════════════════

class TestTheBrew:
    def _eclipse_board(self, world):
        """No league standing, France quiet, and Austria's bloc above
        France's share (D3's clause met by the board, not waived)."""
        world.active_coalition = None
        world.brewing_coalition = None
        world.coalition_cooldown = 0
        world.threat_by_target["France"] = 10
        for region_name in ("Lorraine", "Champagne", "Burgundy", "Lyonnais",
                            "Franche-Comte", "Orleanais", "Nivernais", "Picardy"):
            world.regions[region_name].controller = "Austria"
        world.invalidate_active_nations_cache()
        world.threat_by_target["Austria"] = 49

    def test_the_alarm_carries_a_conqueror_past_the_eclipse_line(self, world):
        from backend.game_logic.coalition import _eclipse_candidate
        self._eclipse_board(world)
        assert _eclipse_candidate(world) is None
        _austria_takes(world, "Munich")
        assert _slot(world, "Austria") == 49 + 2 + AL.ALARM_CAPITAL
        assert _eclipse_candidate(world) == ("Austria", 63)

    def test_without_the_alarm_the_line_is_not_crossed(self, world, monkeypatch):
        from backend.game_logic.coalition import _eclipse_candidate
        hold_down(monkeypatch, T4_1_DOWN)
        self._eclipse_board(world)
        _austria_takes(world, "Munich")
        assert _eclipse_candidate(world) is None


# ═══════════════════════════════════════════════════════════════════════
# The words — G4 (Q6: never a figure)
# ═══════════════════════════════════════════════════════════════════════

DIGIT = re.compile(r"\d")


class TestTheWords:
    def test_the_line_names_the_seat_and_the_cold_great_power(self, world):
        _alarmed(world)
        line = AL.alarm_line(world, "Austria")
        assert line.startswith("Vienna's appetite is remarked in Berlin")
        assert line.endswith(".")
        assert not DIGIT.search(line)

    def test_below_the_line_there_is_no_line(self, world):
        _alarmed(world, value=29)
        assert AL.alarm_line(world, "Austria") == ""
        assert AL.alarm_lines(world) == []

    def test_the_guarantor_is_named_first(self, world):
        _boot_war_board(world)
        _relation(world, "Prussia", "Austria", 0)
        INS.pledge_guarantee(world, guarantor="Sweden", protected="Bavaria")
        assert AL.remarking_courts(world, "Austria")[0] == "Sweden"

    def test_a_victim_does_not_remark(self, world):
        _boot_war_board(world)
        assert "Bavaria" not in AL.remarking_courts(world, "Austria")

    def test_talleyrand_reads_it_in_the_war_room(self, world):
        from backend.game_logic.diplomatic_advisory import _assess_situation
        _alarmed(world)
        reading = _assess_situation(world)
        line = AL.alarm_line(world, "Austria")
        assert line in reading["talleyrand_text"]
        assert reading["context"]["alarm_lines"][0] == line

    def test_no_alarm_no_new_key(self, world):
        from backend.game_logic.diplomatic_advisory import _assess_situation
        assert "alarm_lines" not in _assess_situation(world)["context"]

    def test_talleyrand_reads_it_of_the_court(self, world):
        from backend.game_logic.diplomatic_advisory import _assess_nation
        _alarmed(world)
        assert AL.alarm_line(world, "Austria") in _assess_nation("Austria", world)["talleyrand_text"]

    def test_the_balance_tab_says_it_in_sentences(self, world):
        from backend.game_logic.diplomatic_ledger import _build_balance_of_europe
        _alarmed(world)
        balance = _build_balance_of_europe(world)
        assert balance["alarm_lines"] == AL.alarm_lines(world)
        assert all(not DIGIT.search(line) for line in balance["alarm_lines"])
        assert "threat_by_target" not in balance

    def test_the_balance_tab_is_unchanged_when_nobody_is_loud(self, world):
        from backend.game_logic.diplomatic_ledger import _build_balance_of_europe
        assert "alarm_lines" not in _build_balance_of_europe(world)

    def test_the_client_renders_the_sentences(self):
        gd = (REPO / "godot-client" / "project-sovereign" / "scripts"
              / "diplomatic_ledger.gd").read_text(encoding="utf-8")
        assert 'boe.get("alarm_lines", [])' in gd
        assert "THE COURTS TAKE NOTE" in gd

    def test_le_moniteur_prints_the_word_given(self, world):
        from backend.campaign_log import format_event_oneliner
        from backend.game_logic import gazette
        assert "guarantee_pledged" in gazette._COURT_TYPES
        line = format_event_oneliner({"type": "guarantee_pledged", "guarantor": "Prussia",
                                      "protected": "Bavaria", "against": "Austria",
                                      "turn": 3})
        assert "Prussia guarantees Bavaria against Austria's appetite" in line


# ═══════════════════════════════════════════════════════════════════════
# The page's sibling — found by the Alarm's own measure
# ═══════════════════════════════════════════════════════════════════════

class TestThePageSibling:
    """`dispatch.a_lone_filler_yields_to_the_quiet_floor`: on the commanded
    marengo arm Prussia's word for Bavaria deterred Austria's crisis, the
    mornings went quiet, and the league's standing line — the page's ONLY
    candidate — led five of ten, against the rotation rule's own statement.
    A board with one kind of capped filler now gets the quiet floor as its
    second kind; a board with two kinds alternates exactly as before."""

    def _head(self, window, classes):
        from tests.test_sf_page_the_front_page_of_the_peace import _boot, _cand, _select
        world = _boot()
        world.headline_lead_memory = {"leads_window": list(window)}
        return _select(world, [_cand(cls) for cls in classes])

    def test_a_lone_capped_filler_yields_to_the_quiet_floor(self):
        head = self._head(["realm_league"] * 4, ["realm_league"])
        assert head["class"] == "quiet_morning"
        assert any("realm_league" in beat for beat in head["sub_beats"])

    def test_under_the_cap_the_filler_still_leads(self):
        head = self._head(["realm_league"] * 3, ["realm_league"])
        assert head["class"] == "realm_league"

    def test_two_kinds_capped_still_alternate(self):
        head = self._head(["courts_laws"] * 5 + ["realm_league"] * 4,
                          ["courts_laws", "realm_league"])
        assert head["class"] == "realm_league"

    def test_the_seam_down_restores_the_gap(self, monkeypatch):
        hold_down(monkeypatch, ["backend.game_logic.dispatch:"
                                "a_lone_filler_yields_to_the_quiet_floor=False"])
        head = self._head(["realm_league"] * 4, ["realm_league"])
        assert head["class"] == "realm_league"


# ═══════════════════════════════════════════════════════════════════════
# The measure — the committed records (seeded paths, not laws)
# ═══════════════════════════════════════════════════════════════════════

def _record(name):
    import json
    return json.loads((REPO / "tools" / name).read_text(encoding="utf-8"))


class TestTheMeasure:
    """Three chains, each on the tree it names, each ALONE
    (`tools/_t3_4_measure.py --label`, `tools/_t3_5_chain_d.py --arms D`);
    the movers named by single-run replays with the rung held down."""

    def test_the_control_reproduces_the_t3_6_record(self):
        import json
        t36 = _record("_dy_signature_t3_6_2026_11_09.json")
        ctl = _record("_dy_signature_t4_1_control_2026_11_09.json")
        for seed in t36["seeds"]:
            assert (json.dumps(ctl["seeds"][seed], sort_keys=True)
                    == json.dumps(t36["seeds"][seed], sort_keys=True)), seed

    def test_the_word_is_given_where_bavaria_lives_through_the_opening(self):
        fin = _record("_dy_signature_t4_1_2026_11_09.json")
        given = {seed: s["signature"]["guarantees_given"] for seed, s in fin["seeds"].items()
                 if s["signature"]["guarantees_given"]}
        assert given == {seed: [[7, "Prussia", "Bavaria"]] for seed in ("austerlitz", "lodi", "ulm")}
        census = _record("_t4_1_census_2026_11_09.json")
        assert census["totals"]["alarm_guarantees"] == 3
        assert census["totals"]["guarantees_honoured"] == 0, "Bavaria declared her war"

    def test_story_classes_rise_and_the_kept_debt_waits_for_t4_2(self):
        fin = _record("_dy_signature_t4_1_2026_11_09.json")
        assert fin["story_class_count"] == 10
        census = _record("_t4_1_census_2026_11_09.json")
        assert census["totals"]["annexations_outside_aim"] == 7

    def test_the_ai_france_harness(self):
        d = _record("_t4_1_chain_d_2026_11_09.json")
        assert d["totals"]["D"]["annexations_outside_aim"] == 7
        assert d["totals"]["D"]["alarm_guarantees"] == 3
        honoured = {seed: v["guarantees_honoured"] for seed, v in d["arms"]["D"].items()
                    if v["guarantees_honoured"]}
        assert set(honoured) == {"austerlitz", "lodi", "marengo"}
        assert all(h[0][1:] == ["Prussia", "Bavaria", "Switzerland"] for h in honoured.values())
        # never a war on France from an alarm word (the conqueror-alone rule)
        assert not any(h[3] == "France" for v in d["arms"]["D"].values()
                       for h in v["guarantees_honoured"])
