"""HC-G "Le Moniteur" (gate §7a) — the deterministic Gazette.

An issue every 5 turns + forced specials; composed at publish time from
the SAME fog-filtered rows the campaign-log screen shows, stored in the
serialized `world.gazette_issues` (cap 20, oldest evicted — never
recomposed from the 500-capped event log, the IGR-B trap); masthead
dated by HC-0; display-only (GR6); dormant on worlds without a calendar
anchor (the legacy fixture never prints, byte-identically).
"""

from pathlib import Path

import pytest

from backend.campaign_log import filter_campaign_log, format_event_oneliner
from backend.game_logic.gazette import (
    ISSUE_INTERVAL,
    MAX_ISSUES,
    compose_issue,
    process_gazette,
)
from backend.models.world_state import WorldState

from tests.conftest import WorldFactory

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture
def europe():
    return WorldState.from_scenario(str(SCENARIO_PATH))


def _log_battle(world, turn, location="Swabia", winner="France"):
    world.current_turn = turn
    world.log_event({
        "type": "battle", "attacker": "Ney", "defender": "Mack",
        "attacker_nation": "France", "defender_nation": "Austria",
        "nations": ["France", "Austria"], "location": location,
        "outcome": "attacker_victory" if winner == "France"
        else "defender_victory",
        "attacker_casualties": 2000, "defender_casualties": 4000,
        "battle_name": f"the Battle of {location}",
    })


class TestCadence:
    def test_dormant_without_an_anchor(self):
        world = WorldFactory.basic()
        assert world.start_date == ""
        world.current_turn = ISSUE_INTERVAL
        assert process_gazette(world) is None
        assert world.gazette_issues == []

    def test_first_issue_at_the_interval(self, europe):
        europe.current_turn = ISSUE_INTERVAL - 1
        assert process_gazette(europe) is None
        europe.current_turn = ISSUE_INTERVAL
        issue = process_gazette(europe)
        assert issue is not None and issue["number"] == 1
        # The returned issue IS the stored one — no divergent copy.
        assert europe.gazette_issues[-1] is issue
        assert len(europe.gazette_issues) == 1

    def test_one_issue_max_per_turn(self, europe):
        europe.current_turn = ISSUE_INTERVAL
        assert process_gazette(europe) is not None
        assert process_gazette(europe) is None
        assert len(europe.gazette_issues) == 1

    def test_interval_counts_from_the_last_issue(self, europe):
        europe.current_turn = ISSUE_INTERVAL
        process_gazette(europe)
        europe.current_turn = ISSUE_INTERVAL + 1
        assert process_gazette(europe) is None
        europe.current_turn = ISSUE_INTERVAL * 2
        assert process_gazette(europe) is not None

    def test_twelve_turn_campaign_produces_two_dated_issues(self, europe):
        # The gate's acceptance: >=2 dated issues whose battle lines
        # match the campaign log's own rows.
        _log_battle(europe, 3)
        _log_battle(europe, 8, location="Franconia")
        published = []
        for turn in range(1, 13):
            europe.current_turn = turn
            issue = process_gazette(europe)
            if issue:
                published.append(issue)
        assert len(published) >= 2
        for issue in published:
            assert issue["dateline"]
            assert "1805" in issue["dateline"] or "1806" in issue["dateline"]
        # Battle lines ARE the log's own one-liners (fog-honest rows).
        visible = filter_campaign_log(europe.event_log, europe)
        log_lines = {format_event_oneliner(e) for e in visible
                     if e.get("type") == "battle"}
        printed = [line for issue in published for line in issue["war"]]
        battle_lines = [ln for ln in printed if "Battle" in ln or "battle" in ln]
        assert battle_lines, "no battle line reached print"
        for line in battle_lines:
            assert line in log_lines, line


class TestSpecials:
    def test_capital_storm_forces_an_edition(self, europe):
        # Review round [17]: the event carries the PRODUCTION shape —
        # `captured_from` (capture_executor/movement_executor/AI arms),
        # never the invented previous_controller key.
        europe.current_turn = 2  # off-cadence
        europe.log_event({
            "type": "region_captured", "region": "Vienna",
            "captured_by": "France", "captured_from": "Austria",
            "method": "secure",
        })
        issue = process_gazette(europe)
        assert issue is not None and issue["special"]
        assert issue["special_reason"] == "a capital stormed"

    def test_capital_storm_fires_through_the_real_advance_seam(self, europe):
        """Review round [6/11/16/22]: events are stamped with the
        PRE-increment turn while the publication check runs
        post-increment — the special must fire for the JUST-PLAYED
        campaign turn, driven through the real advance_turn."""
        # The player storms Vienna during campaign turn 1 (stamped 1)...
        europe.log_event({
            "type": "region_captured", "region": "Vienna",
            "captured_by": "France", "captured_from": "Austria",
            "method": "secure",
        })
        assert europe.event_log[-1]["turn"] == europe.current_turn
        # ...and ends the turn: the tick runs at current_turn == 2.
        europe.advance_turn()
        assert europe.gazette_issues, "the special never published"
        assert europe.gazette_issues[-1]["special"]
        assert europe.gazette_issues[-1]["special_reason"] == \
            "a capital stormed"

    def test_nation_eliminated_forces_an_edition(self, europe):
        europe.current_turn = 2
        europe.log_event({
            "type": "nation_eliminated", "nation": "Austria",
            "eliminated_by": "France",
            "message": "Austria has been eliminated",
        })
        issue = process_gazette(europe)
        assert issue is not None and issue["special"]

    def test_great_power_war_forces_an_edition(self, europe):
        europe.current_turn = 2
        europe.log_event({
            "type": "war_declaration", "aggressor": "Prussia",
            "target": "Austria", "nation": "Prussia",
            "message": "Prussia declares war on Austria",
        })
        issue = process_gazette(europe)
        assert issue is not None and issue["special"]
        assert issue["special_reason"] == "war between the great powers"

    def test_minor_war_does_not_force(self, europe):
        europe.current_turn = 2
        europe.log_event({
            "type": "war_declaration", "aggressor": "Baden",
            "target": "Wurttemberg", "nation": "Baden",
            "message": "Baden declares war on Wurttemberg",
        })
        assert process_gazette(europe) is None

    def test_an_ordinary_turn_does_not_force(self, europe):
        europe.current_turn = 2
        _log_battle(europe, 2)
        assert process_gazette(europe) is None

    def test_special_resets_the_clock(self, europe):
        europe.current_turn = 4
        europe.log_event({
            "type": "nation_eliminated", "nation": "Baden",
            "message": "Baden has been eliminated",
        })
        assert process_gazette(europe) is not None
        # The 5-turn clock now counts from the special.
        europe.current_turn = 5
        assert process_gazette(europe) is None
        europe.current_turn = 9
        assert process_gazette(europe) is not None


class TestComposition:
    def test_masthead_is_dated_by_hc0(self, europe):
        europe.current_turn = ISSUE_INTERVAL
        issue = process_gazette(europe)
        assert issue["masthead"].startswith("LE MONITEUR — Paris, ")
        assert issue["dateline"] == europe.get_calendar_label()

    def test_press_register_triumphal_on_victory(self, europe):
        _log_battle(europe, 4, winner="France")
        europe.current_turn = ISSUE_INTERVAL
        issue = process_gazette(europe)
        assert "VICTOIRE" in issue["lead"]

    def test_press_register_delicate_on_reverse(self, europe):
        _log_battle(europe, 4, winner="Austria")
        europe.current_turn = ISSUE_INTERVAL
        issue = process_gazette(europe)
        assert "VICTOIRE" not in issue["lead"]
        assert "delicacy" in issue["lead"]

    def test_third_party_battle_never_makes_the_lead(self, europe):
        # Review round [10/19]: a fog-visible AI-vs-AI field is news for
        # the sections, never a French triumph or reverse — the paper
        # claims only battles France actually fought.
        europe.current_turn = 4
        europe.log_event({
            "type": "battle", "attacker": "Hohenlohe",
            "defender": "Kutuzov",
            "attacker_nation": "Prussia", "defender_nation": "Russia",
            "nations": ["Prussia", "Russia"], "location": "Silesia",
            "outcome": "defender_victory",
            "attacker_casualties": 2000, "defender_casualties": 1000,
            "battle_name": "the Battle of Silesia",
        })
        europe.current_turn = ISSUE_INTERVAL
        issue = process_gazette(europe)
        assert "VICTOIRE" not in issue["lead"]
        assert "delicacy" not in issue["lead"]

    def test_bourse_line_reads_standing_facts(self, europe):
        europe.current_turn = ISSUE_INTERVAL
        issue = process_gazette(europe)
        assert issue["bourse"].startswith("THE BOURSE")
        treasury = int(europe.nation_gold.get("France", 0))
        assert f"{treasury:,}" in issue["bourse"]

    def test_fog_hidden_event_never_appears_in_print(self, europe):
        # A battle between two fogged third parties in an unseen province
        # is invisible to the log screen — the paper may not scoop it.
        europe.current_turn = 4
        hidden = {
            "type": "battle", "attacker": "Kutuzov", "defender": "Mack",
            "attacker_nation": "Russia", "defender_nation": "Austria",
            "nations": ["Russia", "Austria"], "location": "Galicia-East",
            "outcome": "attacker_victory",
            "attacker_casualties": 1000, "defender_casualties": 1000,
            "battle_name": "the Battle of Galicia-East",
        }
        europe.log_event(dict(hidden))
        visible = filter_campaign_log(
            [e for e in europe.event_log
             if e.get("type") == "battle"
             and e.get("location") == "Galicia-East"], europe)
        europe.current_turn = ISSUE_INTERVAL
        issue = process_gazette(europe)
        hidden_line = format_event_oneliner(hidden)
        if not visible:
            assert hidden_line not in issue["war"]
        else:
            pytest.skip("boot visibility reaches Galicia-East at FULL")

    def test_compose_issue_is_a_pure_read(self, europe):
        _log_battle(europe, 3)
        europe.current_turn = 4
        before = europe.to_dict()
        compose_issue(europe, 0)
        assert europe.to_dict() == before


class TestArchive:
    def test_cap_evicts_oldest(self, europe):
        for i in range(MAX_ISSUES + 5):
            europe.gazette_issues.append(
                {"number": i + 1, "turn": i + 1, "dateline": "x",
                 "masthead": "m", "special": False, "special_reason": "",
                 "lead": "", "war": [], "courts": [], "army": [],
                 "bourse": ""})
        europe.current_turn = MAX_ISSUES + 5 + ISSUE_INTERVAL
        process_gazette(europe)
        assert len(europe.gazette_issues) == MAX_ISSUES
        # The newest survives; the oldest five were evicted.
        assert europe.gazette_issues[-1]["turn"] == europe.current_turn
        assert europe.gazette_issues[0]["number"] != 1

    def test_numbering_continues_past_the_cap(self, europe):
        # Review round [1/4/7/20]: № 25 is followed by № 26 — the number
        # continues from the last ISSUE, never from the capped length.
        for i in range(MAX_ISSUES + 5):
            europe.gazette_issues.append(
                {"number": i + 1, "turn": i + 1, "dateline": "x",
                 "masthead": "m", "special": False, "special_reason": "",
                 "lead": "", "war": [], "courts": [], "army": [],
                 "bourse": ""})
        europe.current_turn = MAX_ISSUES + 5 + ISSUE_INTERVAL
        issue = process_gazette(europe)
        assert issue["number"] == MAX_ISSUES + 5 + 1
        europe.current_turn += ISSUE_INTERVAL
        assert process_gazette(europe)["number"] == MAX_ISSUES + 5 + 2

    def test_no_campaign_turn_is_lost_between_issues(self, europe):
        """Review round [18]: the campaign turn played AFTER a
        publication carries the SAME stamp as that issue's advance-tail
        rows — the next issue must still print its fighting."""
        # Issue N publishes at the advance into turn 5.
        europe.current_turn = ISSUE_INTERVAL
        first = process_gazette(europe)
        assert first is not None
        # The player then fights DURING campaign turn 5 (stamped 5)...
        _log_battle(europe, ISSUE_INTERVAL, location="Franconia")
        # ...and issue N+1 publishes at the advance into turn 10.
        europe.current_turn = ISSUE_INTERVAL * 2
        second = process_gazette(europe)
        assert any("Franconia" in line for line in second["war"]), \
            "the fifth turn's fighting vanished from the archive"

    def test_tail_rows_never_print_twice(self, europe):
        # The inclusive window re-reads the last issue's stamp turn —
        # rows the previous issue already printed are dropped.
        _log_battle(europe, 4, location="Swabia")
        europe.current_turn = ISSUE_INTERVAL
        first = process_gazette(europe)
        swabia_rows = [ln for ln in first["war"] if "Swabia" in ln]
        assert swabia_rows
        europe.current_turn = ISSUE_INTERVAL * 2
        second = process_gazette(europe)
        for line in swabia_rows:
            assert line not in second["war"]

    def test_save_load_round_trips_the_archive(self, europe):
        europe.current_turn = ISSUE_INTERVAL
        process_gazette(europe)
        restored = WorldState.from_dict(europe.to_dict())
        assert restored.gazette_issues == europe.gazette_issues
        assert restored.gazette_issues[0]["masthead"].startswith(
            "LE MONITEUR")

    def test_pre_gazette_save_backfills_empty(self):
        world = WorldFactory.basic()
        data = world.to_dict()
        data.pop("gazette_issues", None)
        restored = WorldState.from_dict(data)
        assert restored.gazette_issues == []

    def test_notification_rides_the_rail(self, europe):
        from backend.notifications import GAZETTE_PUBLISHED
        europe.current_turn = ISSUE_INTERVAL
        process_gazette(europe)
        types = [n.get("type") for n in europe.notifications.to_list()]
        assert GAZETTE_PUBLISHED in types


class TestAdvanceTurnWiring:
    def test_the_tick_publishes_through_advance_turn(self, europe):
        # The real seam: advancing to the interval turn prints an issue
        # without any endpoint being involved.
        for _ in range(ISSUE_INTERVAL):
            europe.advance_turn()
        assert len(europe.gazette_issues) >= 1

    def test_legacy_advance_turn_stays_dormant(self):
        world = WorldFactory.basic()
        for _ in range(ISSUE_INTERVAL + 1):
            world.advance_turn()
        assert world.gazette_issues == []
