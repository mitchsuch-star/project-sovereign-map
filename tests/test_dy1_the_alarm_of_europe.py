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

T4-2 — sign at the last (§3c G5, row DY-1c; `settlement_third_party.
sign_at_the_last`, seam `a_crown_falls_only_by_treaty` in row T4-2; the rules
`SYSTEMS_REFERENCE.md` §200): a crown falls by treaty, never by the sword
alone — a court whose last province falls signs with every AI court holding
homeland it may not keep, gets that ground back and lives on; D2 narrowed,
not deleted; the player's holdings never move; the pair close is ONE body
(`_close_the_pair`); the two capture arms never plunder ground signed home;
the reckless auto-charge asks the chokepoint's question (the sibling sweep).
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
from backend.game_logic import settlement_third_party as TP  # noqa: E402
from backend.game_logic import war_council as WC  # noqa: E402
from tests._t3_seams import T3_SEAMS_BY_ROW, hold_down  # noqa: E402

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")
T4_1_DOWN = T3_SEAMS_BY_ROW["T4-1"]
T4_2_DOWN = T3_SEAMS_BY_ROW["T4-2"]


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
# T4-2 — sign at the last (§3c G5, row DY-1c)
# ═══════════════════════════════════════════════════════════════════════

BAVARIA = ("Munich", "Swabia", "Franconia")
THE_WORDS = ("Bavaria signs at the last — Austria keeps Munich and Swabia by "
             "treaty; Austria evacuates Franconia.")
_LONE = {"war_objective": "conquest", "suppress_unresolved_offensive_cascade": True}


def _quiet():
    import contextlib
    import io
    return contextlib.redirect_stdout(io.StringIO())


def _events(world, etype: str):
    return [e for e in world.event_log if e.get("type") == etype]


def _fallen(world):
    return [e["nation"] for e in _events(world, "nation_eliminated")]


def _last_refuges(world):
    return [e for e in _events(world, "third_party_peace")
            if e.get("exit") == TP.LAST_REFUGE_EXIT]


def _takes(world, nation: str, *regions: str) -> None:
    with _quiet():
        for region_name in regions:
            world.capture_region(region_name, nation)


def _declares(world, aggressor: str, target: str) -> None:
    from backend.game_logic.diplomacy import declare_war
    with _quiet():
        assert declare_war(world, aggressor, target, **_LONE).get("success")


class TestSignAtTheLast:
    """The 1805 board: Austria's Redeem-the-Reich aim names Munich and
    Swabia of Bavaria's three provinces; Franconia she may not keep."""

    def test_bavaria_lives_on_in_franconia(self, world):
        _takes(world, "Austria", *BAVARIA)
        assert sorted(world.get_nation_regions("Bavaria")) == ["Franconia"]
        assert "Bavaria" in world.get_active_nations()
        assert _fallen(world) == []
        assert world.get_diplomatic_state("Austria", "Bavaria") == "PEACE"
        key = world._make_diplo_key("Austria", "Bavaria")
        assert world.armistice_cooldowns[key] == TP.PAIR_EXIT_TRUCE_FLOOR_TURNS == 8
        # her corps is not swept with a fallen court's
        assert [n for n, m in world.marshals.items() if m.nation == "Bavaria"] == ["Deroy"]
        [event] = _last_refuges(world)
        assert event["consequence"] == THE_WORDS
        assert (event["proposer"], event["accepter"]) == ("Bavaria", "Austria")
        assert event["signatories"] == ["Austria"]
        assert event["kept"] == {"Austria": ["Munich", "Swabia"]}
        assert event["evacuated"] == {"Austria": ["Franconia"]}

    def test_what_austria_keeps_she_keeps_by_treaty(self, world):
        from backend.game_logic.game_end import TITLE_TREATY, holds_by_title
        _takes(world, "Austria", *BAVARIA)
        for region_name in ("Munich", "Swabia"):
            assert holds_by_title(world, region_name, "Austria")
            assert world.province_title[region_name]["kind"] == TITLE_TREATY
        assert "Franconia" not in world.province_title, "homeland: title by construction"
        assert WC.annexations_outside_aim(world) == {}

    def test_whichever_province_falls_last(self, world):
        _takes(world, "Austria", "Franconia", "Swabia", "Munich")
        assert sorted(world.get_nation_regions("Bavaria")) == ["Franconia"]
        assert world.regions["Munich"].controller == "Austria"
        assert [e["consequence"] for e in _last_refuges(world)] == [THE_WORDS]

    def test_the_seam_down_is_the_old_erasure(self, world, monkeypatch):
        hold_down(monkeypatch, T4_2_DOWN)
        _takes(world, "Austria", *BAVARIA)
        assert world.get_nation_regions("Bavaria") == []
        assert _fallen(world) == ["Bavaria"]
        assert _last_refuges(world) == []

    def test_d2_is_narrowed_not_deleted(self, world, monkeypatch):
        """A court whose whole homeland lies in hands that may keep it still
        falls — the read is the holders' keepable sets, nothing else."""
        monkeypatch.setattr(WC, "keepable_regions", lambda w, holder, ceder: set(BAVARIA))
        _takes(world, "Austria", *BAVARIA)
        assert _fallen(world) == ["Bavaria"]

    def test_the_kingdom_of_italy_still_falls(self, world):
        """The shape the gate names: France's client, its two provinces both
        inside Austria's Redeem Italy."""
        home = set(world.nation_starting_regions["KingdomOfItaly"])
        assert WC.keepable_regions(world, "Austria", "KingdomOfItaly") >= home
        _takes(world, "Austria", "Piedmont", "Milan")
        assert _fallen(world) == ["KingdomOfItaly"]
        assert _last_refuges(world) == []

    def test_a_client_victim_falls_with_its_lords_war(self, world):
        world.vassals["Bavaria"] = dict(world.vassals["Holland"])
        assert TP.sign_at_the_last(world, "Bavaria") is None
        _takes(world, "Austria", *BAVARIA)
        assert _fallen(world) == ["Bavaria"]

    def test_a_conqueror_with_no_aim_there_hands_everything_back(self, world):
        """Prussia's war on Hesse names no province of Hesse's in any design
        of hers: taking both ends the war, and Hesse keeps both."""
        _declares(world, "Prussia", "Hesse")
        _takes(world, "Prussia", "Nassau", "Frankfurt")
        assert sorted(world.get_nation_regions("Hesse")) == ["Frankfurt", "Nassau"]
        assert [e["consequence"] for e in _last_refuges(world)] == [
            "Hesse signs at the last — Prussia evacuates Frankfurt and Nassau."]

    def test_a_war_with_no_record_binds_nothing(self, world):
        """The T3-3 lesson: the legacy world's wars are bare states — a rule
        that reads the war's record binds only where one stands."""
        world.diplomatic_states[world._make_diplo_key("Prussia", "Hesse")] = "WAR"
        _takes(world, "Prussia", "Nassau")
        assert TP.last_refuge_holders(world, "Hesse") == {}
        _takes(world, "Prussia", "Frankfurt")
        assert _fallen(world) == ["Hesse"]

    def test_a_holder_at_peace_holds_by_right(self, world):
        _declares(world, "Prussia", "Hesse")
        world.regions["Nassau"].controller = "Saxony"      # never at war with Hesse
        world.invalidate_active_nations_cache()
        assert TP.last_refuge_holders(world, "Hesse") == {}

    # ── the player ────────────────────────────────────────────────────
    def test_the_players_holdings_never_move(self, world):
        """France takes Hesse's last province while her ally Bavaria holds
        Nassau outside Bavaria's aims: Hesse signs with Bavaria, gets Nassau
        back and lives on — at war with France, who keeps what she took."""
        _declares(world, "Bavaria", "Hesse")
        _declares(world, "France", "Hesse")
        _takes(world, "Bavaria", "Nassau")
        _takes(world, "France", "Frankfurt")
        assert world.regions["Frankfurt"].controller == "France"
        assert sorted(world.get_nation_regions("Hesse")) == ["Nassau"]
        assert world.get_diplomatic_state("Bavaria", "Hesse") == "PEACE"
        assert world.get_diplomatic_state("France", "Hesse") == "WAR"
        [event] = _last_refuges(world)
        # an ally of the signatory is not of its house: France keeps nothing
        # "by treaty" — her war goes on
        assert event["consequence"] == ("Hesse signs at the last — Bavaria evacuates "
                                        "Nassau. Her other wars go on.")
        assert world._elimination_receipts == [
            "Hesse signs at the last with Bavaria and lives on in Nassau — "
            "your war with her goes on, Sire."]

    def test_only_the_players_house_holding_her_ground_she_falls(self, world):
        """Erasing a court outright stays the hegemon's prerogative (D2): a
        client of France holding the ground is the player's house."""
        _declares(world, "France", "Hesse")
        assert world.get_diplomatic_state("Holland", "Hesse") == "WAR"
        _takes(world, "Holland", "Nassau")
        assert TP.last_refuge_holders(world, "Hesse") == {}
        _takes(world, "France", "Frankfurt")
        assert _fallen(world) == ["Hesse"]
        assert world._elimination_receipts == [
            "Hesse has no province left — the war is over, Sire."]

    # ── the two capture arms ──────────────────────────────────────────
    def test_the_instant_capture_does_not_plunder_ground_signed_home(self, world):
        from backend.commands.executor import CommandExecutor
        _takes(world, "Austria", "Munich", "Swabia")
        franconia = world.get_region("Franconia")
        assert not franconia.has_building("fortification")
        buildings = [dict(b) for b in franconia.buildings]
        gold = int(world.nation_gold["Austria"])
        with _quiet():
            result = CommandExecutor()._combat._attempt_region_capture(
                world.marshals["Mack"], "Franconia", world, {"world": world})
        assert result["captured"] is True and result["signed_home"] is True
        assert result["capture_choice"] is None
        assert (franconia.controller, franconia.stability) == ("Bavaria", 50)
        assert [dict(b) for b in franconia.buildings] == buildings
        assert int(world.nation_gold["Austria"]) == gold
        row = [e for e in _events(world, "region_captured") if e["region"] == "Franconia"][-1]
        assert (row["captured_by"], row["method"]) == ("Austria", "handed back")

    def test_the_occupation_arm_does_not_plunder_it_either(self, world):
        _takes(world, "Austria", "Munich", "Swabia")
        gold = int(world.nation_gold["Austria"])
        with _quiet():
            message = world._apply_occupation_capture_effects(world.marshals["Mack"], "Franconia")
        assert message == (" Franconia falls to Austria — and goes home by the "
                           "peace signed in that hour.")
        assert world.regions["Franconia"].controller == "Bavaria"
        assert world._last_occupation_capture_choice is None
        assert int(world.nation_gold["Austria"]) == gold

    def test_a_province_the_capturer_keeps_is_captured_as_before(self, world):
        from backend.models.world_state import capture_was_signed_home
        _takes(world, "Austria", "Franconia", "Swabia", "Munich")
        assert not capture_was_signed_home(world, world.get_region("Munich"), "Austria")
        # the player's holdings never move, so his arm never asks
        assert not capture_was_signed_home(world, world.get_region("Franconia"), "France")

    # ── the sibling sweep: the one conquest outside the chokepoint ────
    def test_the_auto_charge_asks_the_chokepoints_question(self, world):
        """The reckless auto-charge writes the controller itself; before
        T4-2 it never asked whether it took a court's LAST province. The
        same method answers for both (bare writes are the charge's shape)."""
        for region_name in BAVARIA:
            world.regions[region_name].controller = "Austria"
        world.invalidate_active_nations_cache()
        with _quiet():
            world._settle_a_court_without_ground("Bavaria", "Austria")
        assert sorted(world.get_nation_regions("Bavaria")) == ["Franconia"]
        assert [e["consequence"] for e in _last_refuges(world)] == [THE_WORDS]

    def test_the_charge_site_calls_it_under_the_seam(self):
        from backend.models.world_state import WorldState
        charge = inspect.getsource(WorldState._process_reckless_cavalry_turn_start)
        assert "a_crown_falls_only_by_treaty as _ac_asks" in charge
        assert "self._settle_a_court_without_ground(_lost_ground, _taker)" in charge
        capture = inspect.getsource(WorldState.capture_region)
        assert "self._settle_a_court_without_ground(old_controller, capturing_nation)" in capture
        assert "_eliminate_nation(" not in capture, "ONE military erasure point"

    # ── the contract's edges ──────────────────────────────────────────
    def test_the_forced_peace_is_a_signed_peace_and_no_new_log_type(self):
        from backend.campaign_log import CAMPAIGN_LOG_TYPES
        from backend.game_logic.game_end import SIGNED_PEACE_REASONS
        assert TP.LAST_REFUGE_EXIT in SIGNED_PEACE_REASONS
        assert "third_party_peace" in CAMPAIGN_LOG_TYPES
        assert "last_refuge" not in CAMPAIGN_LOG_TYPES

    def test_the_exits_and_the_refuge_close_by_one_body(self):
        exits = inspect.getsource(TP._process_exhausted_pair_exits)
        refuge = inspect.getsource(TP.sign_at_the_last)
        assert "_close_the_pair(" in exits and "_close_the_pair(" in refuge
        for copy in ("set_diplomatic_state(", "follow_the_lord(", "_return_unheld_homeland("):
            assert copy not in exits and copy not in refuge, copy
        # the tempo stamp is the exits' alone — a forced peace neither
        # spends nor waits for the one-exit-a-turn rule
        assert "_pair_exit_this_turn" not in inspect.getsource(TP._close_the_pair)
        assert "_pair_exit_this_turn" not in refuge

    def test_the_peace_survives_a_save(self, world):
        from backend.models.world_state import WorldState
        _takes(world, "Austria", *BAVARIA)
        with _quiet():
            loaded = WorldState.from_dict(world.to_dict())
        assert sorted(loaded.get_nation_regions("Bavaria")) == ["Franconia"]
        assert loaded.get_diplomatic_state("Austria", "Bavaria") == "PEACE"
        key = loaded._make_diplo_key("Austria", "Bavaria")
        assert loaded.armistice_cooldowns[key] == 8

    def test_the_seam_is_registered(self):
        assert T4_2_DOWN == [
            "backend.game_logic.settlement_third_party:a_crown_falls_only_by_treaty=False"]
        assert TP.a_crown_falls_only_by_treaty() is True


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


BAVARIA_FELL = ["eylau", "friedland", "historical", "jena", "marengo", "rivoli", "wagram"]


def _dump(row) -> str:
    import json
    return json.dumps(row, sort_keys=True)


class TestTheT42Measure:
    """T4-2's three chains, each on the tree it names, each ALONE
    (`tools/_t3_4_measure.py --label t4-2[-control]`,
    `tools/_t3_5_chain_d.py --arms D`). Seeded paths, not laws."""

    def test_the_control_reproduces_the_t4_1_record(self):
        t41 = _record("_dy_signature_t4_1_2026_11_09.json")
        ctl = _record("_dy_signature_t4_2_control_2026_11_09.json")
        for seed in t41["seeds"]:
            assert _dump(ctl["seeds"][seed]) == _dump(t41["seeds"][seed]), seed
        assert _record("_t4_2_control_census_2026_11_09.json")["totals"]["last_refuges"] == 0

    def test_the_kept_debt_is_cleared_on_both_surfaces(self):
        """The deploy gate's line: annexation outside aim, 7 → 0 ambient and
        7 → 0 for the AI courts of the AI-France harness — nothing left to
        put to the user province by province (the done-when's way out)."""
        census = _record("_t4_2_census_2026_11_09.json")
        assert census["totals"]["annexations_outside_aim"] == 0
        assert all(c["annexations_outside_aim_by_court"] == {} for c in census["seeds"].values())
        d = _record("_t4_2_chain_d_2026_11_09.json")
        assert d["totals"]["D"]["annexations_outside_aim"] == 0
        # the harness's France is the player nation: its own entries are
        # reported, never gated
        assert all(set(v["annexations_outside_aim_by_court"]) <= {"France"}
                   for v in d["arms"]["D"].values())

    def test_bavaria_signs_wherever_she_used_to_fall(self):
        census = _record("_t4_2_census_2026_11_09.json")
        signed = {seed: [(r["turn"], r["proposer"]) for r in c["last_refuges"]]
                  for seed, c in census["seeds"].items() if c["last_refuges"]}
        assert signed == {
            "eylau": [(6, "Bavaria")], "friedland": [(12, "Bavaria")],
            "historical": [(6, "Bavaria")],
            "jena": [(6, "Bavaria"), (27, "Switzerland")],
            "marengo": [(6, "Bavaria")], "rivoli": [(6, "Bavaria")],
            "wagram": [(6, "Bavaria")]}
        assert census["totals"]["last_refuges"] == 8
        words = [r["consequence"] for c in census["seeds"].values()
                 for r in c["last_refuges"] if r["proposer"] == "Bavaria"]
        assert len(words) == 7 and all(w.startswith(THE_WORDS) for w in words)

    def test_the_movers_are_exactly_the_seeds_where_bavaria_fell(self):
        t41 = _record("_dy_signature_t4_1_2026_11_09.json")
        fin = _record("_dy_signature_t4_2_2026_11_09.json")
        movers = sorted(seed for seed in t41["seeds"]
                        if _dump(fin["seeds"][seed]) != _dump(t41["seeds"][seed]))
        fell = sorted(seed for seed, s in t41["seeds"].items()
                      if any(nation == "Bavaria" for _, nation in s["signature"]["eliminations"]))
        assert movers == fell == BAVARIA_FELL

    def test_what_a_living_bavaria_brings(self):
        """Prussia's word for her on six more seeds (the alarm rung finds a
        living victim) and the Bavarian Match on every seed — the letter
        could not fire for a court that was gone."""
        fin = _record("_dy_signature_t4_2_2026_11_09.json")
        given = {seed: s["signature"]["guarantees_given"] for seed, s in fin["seeds"].items()}
        assert given["friedland"] == []
        for seed in ("austerlitz", "lodi", "ulm"):
            assert given[seed] == [[7, "Prussia", "Bavaria"]]
        for seed in ("eylau", "historical", "jena", "marengo", "rivoli", "wagram"):
            assert given[seed] == [[6, "Prussia", "Bavaria"]]
        assert _record("_t4_2_census_2026_11_09.json")["totals"]["alarm_guarantees"] == 9
        assert all(s["signature"]["moment_turns"].get("bavarian_match")
                   for s in fin["seeds"].values())

    def test_the_honest_cost_the_fallen_courts_converge(self):
        """Reported, never hidden: the gate's done-when read "the
        eliminations column varies". With Bavaria signing on every seed
        where she fell (and Saxony's wagram erasure gone with that
        world-line) the SET of fallen courts is the same on all ten — the
        Kingdom of Italy alone; only its turn varies. Before T4-2 there
        were four different sets. Story classes 10 → 9 (eylau reads as
        ulm); the deploy gate's ≥ 4 holds; T4-3 and Tier 5 own the
        variety."""
        t41 = _record("_dy_signature_t4_1_2026_11_09.json")
        fin = _record("_dy_signature_t4_2_2026_11_09.json")

        def sets(record):
            return {tuple(sorted({nation for _, nation in s["signature"]["eliminations"]}))
                    for s in record["seeds"].values()}

        assert len(sets(t41)) == 4
        assert sets(fin) == {("KingdomOfItaly",)}
        turns = sorted({turn for s in fin["seeds"].values()
                        for turn, _ in s["signature"]["eliminations"]})
        assert turns == [7, 9, 10, 21, 23]
        assert (t41["story_class_count"], fin["story_class_count"]) == (10, 9)

    def test_the_ai_france_harness(self):
        """Ten courts sign at the last in France's own wars — Austria twice
        (Bavaria hands Vienna back the turn France takes her last
        province: the harness's France fights on against a living
        Austria)."""
        d = _record("_t4_2_chain_d_2026_11_09.json")
        assert d["totals"]["D"]["last_refuges"] == 10
        signed = {seed: [(r[0], r[1], r[2]) for r in v["last_refuges"]]
                  for seed, v in d["arms"]["D"].items() if v["last_refuges"]}
        assert signed["eylau"][0] == signed["friedland"][0] == (11, "Austria", "Bavaria")
        assert sorted({court for rows in signed.values() for _, court, _ in rows}) == [
            "Austria", "Holland", "Switzerland"]
        words = d["arms"]["D"]["eylau"]["last_refuges"][0][3]
        assert words == ("Austria signs at the last — Bavaria evacuates Vienna. "
                         "Her other wars go on.")
