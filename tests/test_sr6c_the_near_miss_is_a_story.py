"""SR-6c "The near miss is a story" (Score Finish Step 2, October 2, 2026).

RS-17's Moniteur half: the paper speaks the morning the gate OPENS, not
only within five provinces of it. EAS-2's backend half: every campaign-log
row carries an importance tier.
"""
import contextlib
import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend import campaign_log as CL
from backend.commands.parser import CommandParser
from backend.game_logic import congress, game_end
from backend.game_logic import gazette as GZ
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCEN = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
           / "europe_1805.json")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture
def world():
    with _quiet():
        return WorldState.from_scenario(SCEN)


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def _title_until(world, target):
    """Title enemy provinces BY TREATY until the count reaches `target`."""
    assert congress.armed(world)
    have = congress.titled(world)["count"]
    for region_name, region in sorted(world.regions.items()):
        if have >= target:
            break
        if region.controller == "France" or region.controller in (world.vassals or {}):
            continue
        prev = region.controller
        region.controller = "France"
        game_end.record_province_title(world, region_name, game_end.TITLE_TREATY,
                                       prev, "France")
        have += 1
    world.invalidate_active_nations_cache()
    return congress.titled(world)


class TestTheMoniteurSeesTheOpenGate:

    def test_the_morning_the_gate_opens(self, world):
        need = congress.hold_titled(world)
        view = _title_until(world, need + 2)
        with _quiet():
            lines = GZ._congress_column(world, None)
        assert lines, "the column stayed silent at the open gate"
        head = lines[0]
        assert head.startswith(f"THE CONGRESS OF PARIS — {view['count']} of {need} "
                               f"provinces titled: the Emperor may summon the powers."), head
        assert "would refuse today" in head or "would sign" in head or "would sue" in head, head

    def test_the_count_met_but_a_term_unmet_names_the_term(self, world):
        need = congress.hold_titled(world)
        _title_until(world, need + 3)   # the count stays met without the capital
        capital = world.get_nation_capital("France")
        world.regions[capital].controller = "Austria"
        world.invalidate_active_nations_cache()
        assert congress.titled(world)["count"] >= need
        terms = congress.gate_terms(world)
        blocking = [t for t in terms if not t.get("met") and t.get("key") != "admin"]
        assert blocking, terms
        with _quiet():
            lines = GZ._congress_column(world, None)
        assert lines and "yet the summons waits: " in lines[0], lines
        assert blocking[0]["text"] in lines[0]
        assert "may summon the powers" not in lines[0]

    def test_the_near_miss_column_is_unchanged(self, world):
        need = congress.hold_titled(world)
        view = _title_until(world, need - 2)
        with _quiet():
            lines = GZ._congress_column(world, None)
        assert lines and lines[0].startswith(
            f"THE CONGRESS OF PARIS — {view['count']} of {need} provinces titled; 2 more")

    def test_lever_down_is_silent_at_the_open_gate(self, world, monkeypatch):
        monkeypatch.setattr(GZ, "THE_MONITEUR_SEES_THE_OPEN_GATE", False)
        need = congress.hold_titled(world)
        _title_until(world, need + 1)
        with _quiet():
            lines = GZ._congress_column(world, None)
        assert lines == []


class TestTheLogHasAnImportanceTier:

    def test_every_type_is_classified_exactly_once(self):
        all_types = set(CL.CAMPAIGN_LOG_TYPES)
        union = CL.LOG_TIER_LEAD | CL.LOG_TIER_NOTABLE | CL.LOG_TIER_ROUTINE
        assert union == all_types, (sorted(all_types - union), sorted(union - all_types))
        assert not (CL.LOG_TIER_LEAD & CL.LOG_TIER_NOTABLE)
        assert not (CL.LOG_TIER_LEAD & CL.LOG_TIER_ROUTINE)
        assert not (CL.LOG_TIER_NOTABLE & CL.LOG_TIER_ROUTINE)

    def test_the_table_and_the_refinements(self, world):
        assert CL.event_tier({"type": "war_declaration"}) == "lead"
        assert CL.event_tier({"type": "strategic_order"}) == "routine"
        assert CL.event_tier({"type": "glory_crowned"}) == "notable"
        assert CL.event_tier({"type": "never_authored"}) == "routine"
        assert CL.event_tier({"type": "battle", "outcome": "attacker_victory"}) == "notable"
        assert CL.event_tier({"type": "battle", "outcome": "decisive_victory"}) == "lead"
        assert CL.event_tier({"type": "battle", "outcome": "attacker_victory",
                              "defender": {"forced_retreat": True}}) == "lead"
        assert CL.event_tier({"type": "battle", "outcome": "attacker_victory",
                              "region_conquered": True}) == "lead"
        capital = world.get_nation_capital("Austria")
        assert CL.event_tier({"type": "region_captured", "region": capital}, world) == "lead"
        assert CL.event_tier({"type": "region_captured", "region": "Bohemia"}, world) == "notable"
        assert CL.event_tier({"type": "region_captured", "region": "Bohemia"}) == "notable"

    def test_lever_down_has_no_tier(self, monkeypatch):
        monkeypatch.setattr(CL, "THE_LOG_HAS_AN_IMPORTANCE_TIER", False)
        assert CL.event_tier({"type": "war_declaration"}) == ""

    def test_every_row_on_the_wire_carries_one(self, shipped):
        client, world = shipped
        world.log_event({"type": "war_declaration", "attacker": "France", "defender": "Prussia"})
        world.log_event({"type": "strategic_order", "marshal": "Ney", "order": "MOVE_TO",
                         "target": "Swabia"})
        payload = client.get("/campaign_log").json()
        rows = [e for t in payload["turns"] for e in t["events"]]
        assert rows
        assert all(e.get("tier") in CL.LOG_TIERS for e in rows), [e.get("tier") for e in rows]
        assert any(e["tier"] == "lead" for e in rows if e.get("type") == "war_declaration")
