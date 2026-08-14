"""HC-2 "The Butcher's Ledger Speaks" (gate §3) — the PT-J2 per-war
ledgers finally feed narration. Stateless by design: ZERO new serialized
fields, no latch, no seen-map — both lines derive at render from the
same figures the war-detail popup already shows, own dead only (the
[PTJ-D1] attribution-safe half).
"""

from pathlib import Path

import pytest

from backend.game_logic.battle_report import (
    CAMPAIGN_COST_NOTE_THRESHOLD,
    compose_campaign_cost_note,
)
from backend.game_logic.diplomatic_advisory import _assess_situation
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


class TestWarRoomRung:
    """One rung per active war, reading the pair ledger(s)."""

    def test_rung_renders_the_ledger_figures(self):
        world = WorldFactory.with_war("France", "Prussia")
        key = world._make_diplo_key("France", "Prussia")
        world.campaign_ledgers[key] = {
            "captures": {"France": ["Rhineland", "Bavaria"]},
            "casualties": {"France": 12000, "Prussia": 30000},
        }
        text = _assess_situation(world)["talleyrand_text"]
        assert ("This war has taken 12,000 of our men and yielded "
                "2 provinces, Sire.") in text

    def test_singular_province(self):
        world = WorldFactory.with_war("France", "Prussia")
        key = world._make_diplo_key("France", "Prussia")
        world.campaign_ledgers[key] = {
            "captures": {"France": ["Rhineland"]},
            "casualties": {"France": 500},
        }
        text = _assess_situation(world)["talleyrand_text"]
        assert "yielded 1 province, Sire." in text

    def test_fresh_war_renders_nothing(self):
        # The gate's negative acceptance: an empty ledger says nothing.
        world = WorldFactory.with_war("France", "Prussia")
        text = _assess_situation(world)["talleyrand_text"]
        assert "This war has taken" not in text

    def test_own_dead_only_never_the_enemy_figure(self):
        # [PTJ-D1]: the line voices the side's OWN recorded dead — the
        # enemy's 30,000 must never appear as "our men".
        world = WorldFactory.with_war("France", "Prussia")
        key = world._make_diplo_key("France", "Prussia")
        world.campaign_ledgers[key] = {
            "captures": {},
            "casualties": {"France": 4000, "Prussia": 30000},
        }
        text = _assess_situation(world)["talleyrand_text"]
        assert "taken 4,000 of our men" in text
        assert "30,000 of our men" not in text

    def test_rung_is_stateless(self):
        world = WorldFactory.with_war("France", "Prussia")
        key = world._make_diplo_key("France", "Prussia")
        world.campaign_ledgers[key] = {
            "captures": {}, "casualties": {"France": 2000},
        }
        before = world.to_dict()
        _assess_situation(world)
        _assess_situation(world)
        assert world.to_dict() == before


class TestBattleReportClosingClause:
    """The 25,000-dead threshold clause (blessed, in-band)."""

    def _load_ledger(self, world, own, foe, dead):
        key = world._make_diplo_key(own, foe)
        world.campaign_ledgers[key] = {
            "captures": {}, "casualties": {own: dead},
        }

    def test_note_past_the_threshold(self, europe):
        self._load_ledger(europe, "France", "Austria", 31204)
        note = compose_campaign_cost_note(europe, "France", "Austria")
        assert note == "The war's cost now stands at 31,204 of our men."

    def test_silent_below_the_threshold(self, europe):
        self._load_ledger(europe, "France", "Austria",
                          CAMPAIGN_COST_NOTE_THRESHOLD - 1)
        assert compose_campaign_cost_note(europe, "France", "Austria") == ""

    def test_exact_threshold_speaks(self, europe):
        self._load_ledger(europe, "France", "Austria",
                          CAMPAIGN_COST_NOTE_THRESHOLD)
        assert compose_campaign_cost_note(
            europe, "France", "Austria") != ""

    def test_europe_scoped_only(self):
        world = WorldFactory.with_war("France", "Prussia")
        self._load_ledger(world, "France", "Prussia", 40000)
        assert compose_campaign_cost_note(world, "France", "Prussia") == ""

    def test_no_ledger_is_silent(self, europe):
        assert compose_campaign_cost_note(europe, "France", "Austria") == ""

    def test_glued_onto_the_executor_battle_report(self, europe):
        """The clause rides the real after-action seam: a player attack
        in a war past the threshold carries campaign_cost_note."""
        from backend.commands.executor import CommandExecutor
        # Ney stands at Alsace on the boot; Austria's war is live. Move
        # an Austrian corps into an adjacent province and strike it.
        ney = europe.marshals.get("Ney")
        assert ney is not None
        foe = next(m for m in europe.marshals.values()
                   if m.nation == "Austria" and m.strength > 0)
        foe.location = ney.location
        self._load_ledger(europe, "France", "Austria", 60000)
        result = CommandExecutor().execute(
            {"success": True,
             "command": {"marshal": ney.name, "action": "attack",
                         "target": foe.name}},
            {"world": europe})
        assert result.get("success"), result.get("message")
        report = result.get("battle_report") or {}
        assert report.get("campaign_cost_note") == (
            "The war's cost now stands at "
            f"{europe.campaign_ledgers[europe._make_diplo_key('France', 'Austria')]['casualties']['France']:,}"
            " of our men.")
