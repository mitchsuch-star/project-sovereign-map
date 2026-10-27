"""The October 27, 2026 enemy-diplomacy sweep — the pins of its fixes.

A 30-turn seeded probe (`tools/playtest_driver.py --seed 7 --diplomacy
decline`) of a passive France read the AI courts' traffic as the player
would: Hesse's non-aggression pact five times in thirty turns at the bare
cadence, "Sweden and Russia sign a Open Borders Agreement", "the War with
Switzerland — Switzerland", "It also France cedes Savoy to Austria; erects
Duchy of Normandy out of France". Each is fixed at its cause and pinned here.
"""
from pathlib import Path

import pytest

from backend.game_logic.ai_diplomacy import (
    REFUSAL_MEMORY_TURNS,
    REPEATED_ASK_COOLDOWN_CAP,
    TYPE_REJECTION_COOLDOWN,
    apply_rejection_cooldowns,
    prior_refusals_of,
    process_diplomatic_phase,
    record_diplomatic_refusal,
    repeated_ask_aside,
    repeated_ask_factor,
)
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (
    REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _peace(world, nation, relation=10):
    key = world._make_diplo_key("France", nation)
    world.diplomatic_states[key] = "PEACE"
    world.nation_relations[key] = relation
    return key


# ════════════════════════════════════════════════════════════════════════
# 1. The repeat-ask governor
# ════════════════════════════════════════════════════════════════════════


class TestRepeatedAskGovernor:
    def test_the_first_refusal_is_the_blessed_number(self, world):
        _peace(world, "Prussia")
        apply_rejection_cooldowns("Prussia", "open_borders", world)
        assert world.ai_proposal_cooldowns["Prussia|open_borders"] == int(TYPE_REJECTION_COOLDOWN)
        assert repeated_ask_factor(world, "Prussia", "open_borders") == 1

    def test_a_refused_ask_brought_again_waits_longer(self, world):
        """One refused episode of the same ask inside the record's memory
        doubles the type cooldown; two make it the cap (×3)."""
        _peace(world, "Prussia")
        world.current_turn = 20
        world.diplomatic_refusals = {"Prussia>France": [
            {"type": "open_borders", "turn": 9},
        ]}
        assert prior_refusals_of(world, "Prussia", "France", "open_borders") == 1
        apply_rejection_cooldowns("Prussia", "open_borders", world)
        assert world.ai_proposal_cooldowns["Prussia|open_borders"] == 2 * int(TYPE_REJECTION_COOLDOWN)
        world.diplomatic_refusals["Prussia>France"].append({"type": "open_borders", "turn": 16})
        assert repeated_ask_factor(world, "Prussia", "open_borders") == 3 == int(REPEATED_ASK_COOLDOWN_CAP)
        # five entries written straight to the store still cap at ×3
        world.diplomatic_refusals["Prussia>France"] = [
            {"type": "open_borders", "turn": t} for t in (9, 11, 13, 15, 17)]
        assert repeated_ask_factor(world, "Prussia", "open_borders") == int(REPEATED_ASK_COOLDOWN_CAP)

    def test_the_memory_window_and_the_type_bound_the_count(self, world):
        _peace(world, "Prussia")
        world.current_turn = 40
        world.diplomatic_refusals = {"Prussia>France": [
            {"type": "open_borders", "turn": 40 - REFUSAL_MEMORY_TURNS},   # aged out
            {"type": "non_aggression", "turn": 38},                        # another ask
        ]}
        assert prior_refusals_of(world, "Prussia", "France", "open_borders") == 0
        assert repeated_ask_factor(world, "Prussia", "open_borders") == 1

    def test_another_recipients_refusals_do_not_count(self, world):
        """The record is ordered-pair keyed: Prussia>Austria's refusals never
        slow Prussia's asks of France."""
        _peace(world, "Prussia")
        world.current_turn = 20
        world.diplomatic_refusals = {"Prussia>Austria": [
            {"type": "open_borders", "turn": 15},
        ]}
        assert repeated_ask_factor(world, "Prussia", "open_borders") == 1
        assert repeated_ask_factor(world, "Prussia", "open_borders", recipient="Austria") == 2

    def test_a_court_at_war_is_never_slowed(self, world):
        """A beaten court's peace must keep coming - the governor reads
        peacetime pairs only."""
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.current_turn = 20
        world.diplomatic_refusals = {"Prussia>France": [
            {"type": "peace", "turn": 12}, {"type": "peace", "turn": 18},
        ]}
        assert repeated_ask_factor(world, "Prussia", "peace") == 1
        apply_rejection_cooldowns("Prussia", "peace", world)
        assert world.ai_proposal_cooldowns["Prussia|peace"] == int(TYPE_REJECTION_COOLDOWN)

    def test_the_deferred_offset_rides_the_factor(self, world):
        _peace(world, "Prussia")
        world.current_turn = 20
        world.diplomatic_refusals = {"Prussia>France": [{"type": "open_borders", "turn": 12}]}
        apply_rejection_cooldowns("Prussia", "open_borders", world, deferred=True)
        assert world.ai_proposal_cooldowns["Prussia|open_borders"] == 2 * int(TYPE_REJECTION_COOLDOWN) + 1

    def test_the_aside_words(self, world):
        assert repeated_ask_aside(world, "Prussia", 0) == ""
        once = repeated_ask_aside(world, "Prussia", 1)
        assert once.startswith(" Prussia has brought this same ask once in the last ")
        assert f"{int(REFUSAL_MEMORY_TURNS)} turns and been refused each time; her envoy comes regardless." in once
        assert " twice " in repeated_ask_aside(world, "Prussia", 2)
        assert " 3 times " in repeated_ask_aside(world, "Prussia", 3)
        assert repeated_ask_aside(world, "PapalStates", 2).startswith(" The Papal States has brought")

    def test_the_envoys_letter_says_how_often_the_court_has_asked(self, world):
        """End to end on the P3 shelter rung: the first letter carries no
        count; the same ask after a refusal carries Talleyrand's note and
        the `repeated_ask_count`."""
        _peace(world, "Prussia", relation=10)
        world.threat_level = 70
        world.nation_gold["Prussia"] = 1000
        first = process_diplomatic_phase("Prussia", world)
        assert first is not None and first.get("recipient") == "France"
        assert "has brought this same ask" not in str(first.get("talleyrand_assessment") or "")
        assert "repeated_ask_count" not in first
        ptype = first["proposal_type"]
        assert record_diplomatic_refusal(world, "Prussia", "France", ptype)
        world.current_turn += int(TYPE_REJECTION_COOLDOWN) + 1
        second = process_diplomatic_phase("Prussia", world)
        assert second is not None and second["proposal_type"] == ptype
        assert second["repeated_ask_count"] == 1
        assert "Prussia has brought this same ask once" in second["talleyrand_assessment"]


# ════════════════════════════════════════════════════════════════════════
# 2. The chronicle's words
# ════════════════════════════════════════════════════════════════════════


class TestTheChroniclesWords:
    def test_two_courts_sign_an_open_borders_agreement(self, world):
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({
            "type": "diplomatic_ai_ai_treaty", "nation_a": "Sweden",
            "nation_b": "Russia", "treaty_type": "Open Borders Agreement",
            "turn": 3}, "France", world)
        assert line == "Sweden and Russia sign an Open Borders Agreement"
        line = format_event_oneliner({
            "type": "diplomatic_ai_ai_treaty", "nation_a": "Sweden",
            "nation_b": "PapalStates", "treaty_type": "Defensive Alliance",
            "turn": 3}, "France", world)
        assert line == "Sweden and the Papal States sign a Defensive Alliance"

    def test_a_one_court_war_carries_no_roster_suffix(self, world):
        """"War with Switzerland — Switzerland" said the name twice on the
        arrival rail, the mailbox and the dispatch; a league or a ground
        title keeps its roster."""
        from backend.game_logic.war_title import war_title
        key = world._make_diplo_key("France", "Switzerland")
        world.diplomatic_states[key] = "WAR"
        out = war_title(world, court="Switzerland")
        if out["source"] == "court":
            assert out["display"] == out["title"] == "War with Switzerland"
            assert " — " not in out["display"]
        else:  # the ground names the war on this board; the roster rides
            assert out["display"].startswith(out["title"])

    def test_the_settlement_rail_frames_its_articles_with_their_subjects(self, world):
        from backend.game_logic.settlement_offers import offer_substance_clause
        clause = offer_substance_clause(world, [
            {"type": "peace"},
            {"type": "territory_cede", "from": "France", "to": "Austria", "region": "Savoy"},
            {"type": "create_client", "from": "France", "to": "Austria", "tag": "Normandy",
             "client_display_name": "Duchy of Normandy", "provinces": ["Normandy"]},
            {"type": "forced_alliance", "from": "France", "to": "Austria"},
        ])
        assert clause == ("France cedes Savoy to Austria; the Duchy of Normandy is erected "
                          "out of France; France is bound in alliance to Austria")
        rail = (REPO / "backend" / "game_logic" / "turn_manager.py").read_text(encoding="utf-8")
        assert ' Its articles: {_substance}.' in rail
        assert ' It also {_substance}.' not in rail
