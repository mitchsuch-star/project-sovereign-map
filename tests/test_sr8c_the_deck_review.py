"""SR-8c — Score Finish Step 5's deck review (SCORE_FINISH_SPEC.md §3 Step 5).

Three items, each pinned on the SHIPPED 1805 board:

* IQ6-D2's build, as ruled (§6 row 12, October 3, 2026): a client's
  partition is the hegemon's act — the volte-face's NOT-HUMILIATED clause
  reads a punitive memory (and an emergent revanche) authored by ANY member
  of the hegemon's bloc. Pinned on the Bavaria-charged partition, with the
  lever-down arm that reproduces the hole.
* IQ7-D3 (ruled at Step 5 under the user's delegation; gate record
  VASSAL_DEEPENING_SPEC.md §9.1 R11): Holland's deck authors
  `ostfriesland` [East Frisia] — the Treaty of Fontainebleau's 1807 gift to
  the Kingdom of Holland — a non-capital, non-homeland province its lord can
  conquer and give. `TestT5TheDecksPrice` reads it unstaged.
* AI-V §7a scene 1, the Confederation of the Rhine (ruled at Step 5;
  AI_INTENT_SPEC.md §7a scene-1 row): recorded UNREACHABLE BY DESIGN — the
  1805 half is the boot state (Bavaria's Bogenhausen alliance, authored as
  ALLIANCE), the 1806 half was Napoleon's act (the Treaty of Paris, 12 July
  1806), and a German minor's own covet design measured as refusal noise,
  never the scene. Pinned as the board's honest state.
"""

from __future__ import annotations

import contextlib
import io
from pathlib import Path

import pytest

from backend.game_logic import emergent_designs as ED
from backend.game_logic.emergent_designs import (
    PUNITIVE_MEMORY_TYPE,
    record_punitive_cessions,
    volte_face_failing_clauses,
    volte_face_receptive,
)
from backend.models.world_state import WorldState
from tests.test_ai_intent_emergent_designs import _beat_and_court

REPO = Path(__file__).resolve().parents[1]
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
               / "europe_1805.json")


@pytest.fixture(scope="module")
def boot():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(SCENARIO)


@pytest.fixture
def world(boot):
    return WorldState.from_dict(boot.to_dict())


# ═══════════════════════════════════════════════════════════════════════════
# IQ6-D2 — a client's partition is the hegemon's act
# ═══════════════════════════════════════════════════════════════════════════

class TestAClientsPartitionIsTheHegemons:
    def test_bavaria_stands_in_frances_bloc(self, world):
        """The fixture's own geometry: the client the partition is charged to
        is in the hegemon's bloc on the boot board (Bogenhausen, 1805)."""
        assert world.get_diplomatic_state("Bavaria", "France") == "ALLIANCE"
        assert "Bavaria" in world.get_bloc_members("France")

    def test_the_tilsit_state_is_receptive_before_the_partition(self, world):
        _beat_and_court(world)
        assert volte_face_receptive(world, "Russia", "France") is True

    def test_a_partition_charged_to_bavaria_forecloses_the_door(self, world):
        _beat_and_court(world)
        record_punitive_cessions(world, {
            "Russia": [("Lithuania", "Bavaria"), ("Livonia", "Bavaria")]})
        from backend.game_logic.settlement_reactions import get_settlement_memories
        records = get_settlement_memories(world, subject="Russia",
                                          memory_type=PUNITIVE_MEMORY_TYPE)
        assert records and records[0]["actor"] == "Bavaria"
        assert volte_face_receptive(world, "Russia", "France") is False
        assert volte_face_failing_clauses(world, "Russia", "France") == [
            ED.VOLTE_CLAUSE_PUNITIVE]

    def test_lever_down_the_hole_reopens(self, world, monkeypatch):
        """The measured defect, reproduced: the hegemon's own memories alone
        leave the door open after its client partitioned the court."""
        monkeypatch.setattr(ED, "A_CLIENTS_PARTITION_IS_THE_HEGEMONS", False)
        _beat_and_court(world)
        record_punitive_cessions(world, {
            "Russia": [("Lithuania", "Bavaria"), ("Livonia", "Bavaria")]})
        assert volte_face_receptive(world, "Russia", "France") is True

    def test_a_revanche_charged_to_the_client_forecloses(self, world):
        _beat_and_court(world)
        world.agendas["Russia"].insert(0, {
            "id": "revanche_russia", "type": "acquire_regions",
            "title": "Revanche", "regions": ["Lithuania"],
            "emergent": True, "author": "Bavaria"})
        assert volte_face_failing_clauses(world, "Russia", "France") == [
            ED.VOLTE_CLAUSE_REVANCHE]

    def test_a_partition_by_a_court_outside_the_bloc_does_not(self, world):
        """Prussia is no member of France's bloc: its partition of Russia is
        Prussia's quarrel, not France's humiliation of Russia."""
        _beat_and_court(world)
        assert "Prussia" not in world.get_bloc_members("France")
        record_punitive_cessions(world, {
            "Russia": [("Lithuania", "Prussia"), ("Livonia", "Prussia")]})
        assert volte_face_receptive(world, "Russia", "France") is True


# ═══════════════════════════════════════════════════════════════════════════
# IQ7-D3 — a satellite design province its lord can give
# ═══════════════════════════════════════════════════════════════════════════

class TestASatelliteDesignItsLordCanGive:
    def test_hollands_deck_authors_east_frisia(self, world):
        deck = world.agendas["Holland"]
        assert [e["id"] for e in deck] == [
            "the_seventeen_provinces", "merchants_peace", "ostfriesland"]
        entry = deck[2]
        assert entry["type"] == "acquire_regions" and entry["regions"] == ["East Frisia"]

    def test_east_frisia_is_givable_by_construction(self, world):
        """Non-capital, never French homeland, held by a court France can
        fight, and contiguous to the client (Friesland) — VS-3's own gates."""
        from backend.game_logic import vassal as V
        region = world.regions["East Frisia"]
        assert not region.is_capital
        assert "East Frisia" not in (world.nation_starting_regions.get("France") or [])
        assert region.controller == "Hanover"
        assert "Friesland" in region.adjacent_regions
        region.controller = "France"
        world.invalidate_active_nations_cache()
        grantable = [e["region"] for e in V.list_grantable_regions(world, "Holland", actor="France")]
        assert "East Frisia" in grantable
        terms = V.petition_terms(world, "Holland")
        assert terms["region"] == "East Frisia" and terms["in_design"] is True

    def test_the_formation_goal_is_untouched(self, world):
        """Appended, never inserted: NA-6's post-formation goal stays deck
        index 1 (§11.1-4)."""
        assert world.agendas["Holland"][1]["id"] == "merchants_peace"


# ═══════════════════════════════════════════════════════════════════════════
# AI-V §7a scene 1 — recorded unreachable by design
# ═══════════════════════════════════════════════════════════════════════════

class TestTheConfederationIsRecordedUnreachable:
    def test_the_german_minors_carry_no_deck(self, world):
        for minor in ("Bavaria", "Saxony", "Hesse"):
            assert minor not in world.agendas, minor

    def test_their_intent_reads_no_want(self, world):
        from backend.game_logic.intent import get_nation_intent
        for minor in ("Bavaria", "Saxony", "Hesse"):
            assert get_nation_intent(minor, world).want_id is None, minor

    def test_the_1805_half_is_the_boot_state(self, world):
        """Bogenhausen (25 August 1805): Bavaria is France's ally at boot —
        the bandwagon of 1805 is authored, not awaited."""
        assert world.get_diplomatic_state("Bavaria", "France") == "ALLIANCE"
