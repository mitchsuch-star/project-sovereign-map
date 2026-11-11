"""T2-3 — Prussia's hook: the bandwagoner (`DYNAMISM_SPEC.md` §2 Tier 2;
November 8, 2026; the rules `SYSTEMS_REFERENCE.md` §189).

A court whose statecraft prefers the bandwagon rung (§3.4: Prussia, the
hesitant opportunist — DERIVED from `reaches_first`, never a name) joins
a live AI-vs-AI war on the STRONGER side when its relation with the
weaker side's leader is below 0 — the ally-entry join idiom — and quits
at most ONCE a campaign, the turn its side reads strictly weaker. The
quota is derived from the `reneged_turn` stamp inside the serialized
`war_instances` participant row (no new world field). The seam
`a_bandwagoner_joins_the_stronger_side` (tests/_t2_seams.py) holds the
pre-T2-3 board for the recorded arms.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.game_logic import war_council as WC  # noqa: E402
from backend.game_logic.war_council import (  # noqa: E402
    _bandwagon_courts,
    _bandwagon_renege_spent,
    process_bandwagon,
)
from tests._t2_seams import T2_SEAMS_BY_ROW, hold_down  # noqa: E402

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")


@pytest.fixture()
def world():
    from backend.models.world_state import WorldState
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO), seed="historical")


STRENGTHS = {}


@pytest.fixture()
def scales(monkeypatch):
    """The staged scales: `_standing_strength` reads this dict (default
    10,000), so a pin sets each side's weight without raising armies."""
    STRENGTHS.clear()
    monkeypatch.setattr(
        WC, "_standing_strength",
        lambda w, n: int(STRENGTHS.get(n, 10000)))
    return STRENGTHS


def _stage_war(world, a: str, b: str, entry_path: str = "war_declaration"):
    """A live AI-vs-AI war by the production attach + state idioms."""
    from backend.game_logic.diplomacy import set_diplomatic_state
    from backend.game_logic.settlement_helpers import (
        ensure_war_instance_for_pair,
    )
    attach = ensure_war_instance_for_pair(
        world, a, b, entry_path=entry_path, reason="T2-3 pin staging")
    assert attach.get("ok"), attach
    set_diplomatic_state(world, a, b, "WAR", "t2_3_pin")
    world.invalidate_active_nations_cache()
    return str(attach["war_id"])


def _set_relation(world, a: str, b: str, value: int) -> None:
    world.nation_relations[world._make_diplo_key(a, b)] = int(value)


@pytest.fixture(autouse=True)
def _the_join_on_its_own_staging(monkeypatch):
    """Session G4 (November 11, 2026): a bandwagoner joins only against a
    NEIGHBOUR of its house (`war_council.a_bandwagoner_joins_a_neighbours_war`),
    and this module stages T2-3's join on Sweden against Denmark — no
    neighbour of Prussia's on the drawn map. The pins below are T2-3's own
    mechanics (the scales, the tempo, the renege); they hold the reach rule
    down. Its own pins: `tests/test_session_g4_the_open_readings.py`."""
    from tests._t3_seams import T3_SEAMS_BY_ROW, hold_down
    hold_down(monkeypatch, T3_SEAMS_BY_ROW["G4-WAGON"])


class TestTheJoin:
    def test_the_eligibility_is_derived_never_a_name(self, world):
        assert _bandwagon_courts(world) == ["Prussia"]
        world.vassals["Prussia"] = {"lord": "France"}
        assert _bandwagon_courts(world) == []

    def test_prussia_joins_the_stronger_side(self, world, scales):
        war_id = _stage_war(world, "Sweden", "Denmark")
        scales.update({"Sweden": 100000, "Denmark": 20000,
                       "Prussia": 60000})
        _set_relation(world, "Prussia", "Denmark", -30)
        events = process_bandwagon(world)
        assert [e["type"] for e in events] == ["ai_bandwagon_joined"]
        assert events[0]["against"] == "Denmark"
        assert events[0]["beside"] == "Sweden"
        assert world.get_diplomatic_state("Prussia", "Denmark") == "WAR"
        inst = world.war_instances[war_id]
        assert "Prussia" in (inst.get("active_participants") or [])
        row = inst["participant_meta"]["Prussia"]
        assert row.get("entry_path") == "bandwagon"
        logged = [e for e in world.event_log
                  if e.get("type") == "war_declaration"
                  and e.get("aggressor") == "Prussia"]
        assert logged and logged[-1].get("entry_path") == "bandwagon"

    def test_no_join_without_the_grudge(self, world, scales):
        _stage_war(world, "Sweden", "Denmark")
        scales.update({"Sweden": 100000, "Denmark": 20000})
        _set_relation(world, "Prussia", "Denmark", 0)
        assert process_bandwagon(world) == []
        assert world.get_diplomatic_state("Prussia", "Denmark") != "WAR"

    def test_no_join_at_even_scales(self, world, scales):
        _stage_war(world, "Sweden", "Denmark")
        scales.update({"Sweden": 50000, "Denmark": 50000})
        _set_relation(world, "Prussia", "Denmark", -30)
        assert process_bandwagon(world) == []

    def test_the_players_war_is_never_joined(self, world, scales):
        """§16.2's v1 narrowing: the anti-France road stays the
        coalition's, and France's own side is the player's to invite —
        the boot war (France in it) is skipped whatever the scales."""
        scales.update({"France": 200000, "Austria": 10000})
        _set_relation(world, "Prussia", "Austria", -60)
        events = process_bandwagon(world)
        assert events == []
        assert world.get_diplomatic_state("Prussia", "Austria") != "WAR"

    def test_the_weaker_side_is_never_joined(self, world, scales):
        """Reversed scales reverse the enemy: with Denmark's side the
        stronger, the target would be SWEDEN — a grudge against Denmark
        alone joins nothing."""
        _stage_war(world, "Sweden", "Denmark")
        scales.update({"Sweden": 20000, "Denmark": 100000})
        _set_relation(world, "Prussia", "Denmark", -30)
        _set_relation(world, "Prussia", "Sweden", 10)
        assert process_bandwagon(world) == []

    def test_one_join_a_turn(self, world, scales):
        _stage_war(world, "Sweden", "Denmark")
        _stage_war(world, "Sardinia", "Naples")
        scales.update({"Sweden": 100000, "Denmark": 20000,
                       "Sardinia": 100000, "Naples": 20000})
        _set_relation(world, "Prussia", "Denmark", -30)
        _set_relation(world, "Prussia", "Naples", -30)
        events = process_bandwagon(world)
        assert len(events) == 1

    def test_the_seam_down_restores_the_old_board(self, world, scales,
                                                  monkeypatch):
        _stage_war(world, "Sweden", "Denmark")
        scales.update({"Sweden": 100000, "Denmark": 20000})
        _set_relation(world, "Prussia", "Denmark", -30)
        hold_down(monkeypatch, T2_SEAMS_BY_ROW["T2-3"])
        assert process_bandwagon(world) == []

    def test_deckless_worlds_no_op(self):
        from backend.models.world_state import WorldState
        with contextlib.redirect_stdout(io.StringIO()):
            legacy = WorldState()
        assert process_bandwagon(legacy) == []


class TestTheRenege:
    def _join(self, world, scales):
        war_id = _stage_war(world, "Sweden", "Denmark")
        scales.update({"Sweden": 100000, "Denmark": 20000,
                       "Prussia": 60000})
        _set_relation(world, "Prussia", "Denmark", -30)
        assert process_bandwagon(world)
        return war_id

    def test_the_scales_turn_and_the_bandwagoner_quits(self, world, scales):
        war_id = self._join(world, scales)
        scales.update({"Sweden": 10000, "Denmark": 200000,
                       "Prussia": 10000})
        events = process_bandwagon(world)
        kinds = [e["type"] for e in events]
        assert "ai_bandwagon_reneged" in kinds
        assert world.get_diplomatic_state("Prussia", "Denmark") == "PEACE"
        row = world.war_instances[war_id]["participant_meta"]["Prussia"]
        assert row.get("reneged_turn") is not None
        assert row.get("exited_turn") is not None
        assert _bandwagon_renege_spent(world, "Prussia")
        peaced = [e for e in world.event_log
                  if e.get("type") == "third_party_peace"
                  and e.get("proposer") == "Prussia"]
        assert peaced, "the renege must be on the record"

    def test_one_renege_a_campaign(self, world, scales):
        self._join(world, scales)
        scales.update({"Sweden": 10000, "Denmark": 200000,
                       "Prussia": 10000})
        assert any(e["type"] == "ai_bandwagon_reneged"
                   for e in process_bandwagon(world))
        # The second adventure: a fresh war, joined — the scales turn
        # again, and the quota holds the line.
        war_id2 = _stage_war(world, "Sardinia", "Naples")
        scales.update({"Sardinia": 100000, "Naples": 20000,
                       "Prussia": 60000})
        _set_relation(world, "Prussia", "Naples", -30)
        assert any(e["type"] == "ai_bandwagon_joined"
                   for e in process_bandwagon(world))
        scales.update({"Sardinia": 10000, "Naples": 200000,
                       "Prussia": 10000})
        assert process_bandwagon(world) == []
        assert "Prussia" in (world.war_instances[war_id2]
                             .get("active_participants") or [])

    def test_a_courts_own_war_never_reneges(self, world, scales):
        """Only a bandwagoned entry carries the path — a war the court
        declared itself is fought to its end, however the scales read."""
        war_id = _stage_war(world, "Prussia", "Hanover")
        scales.update({"Prussia": 10000, "Hanover": 200000})
        assert process_bandwagon(world) == []
        assert "Prussia" in (world.war_instances[war_id]
                             .get("active_participants") or [])

    def test_a_reneged_war_is_never_rejoined(self, world, scales):
        """Pin 13's guard: after the renege, the same war cannot be
        re-entered — not even from the other, now-stronger side."""
        war_id = self._join(world, scales)
        scales.update({"Sweden": 10000, "Denmark": 200000,
                       "Prussia": 10000})
        assert any(e["type"] == "ai_bandwagon_reneged"
                   for e in process_bandwagon(world))
        _set_relation(world, "Prussia", "Sweden", -40)
        scales.update({"Prussia": 60000})
        assert process_bandwagon(world) == []
        assert "Prussia" not in (world.war_instances[war_id]
                                 .get("active_participants") or [])

    def test_the_quota_round_trips(self, world, scales):
        self._join(world, scales)
        scales.update({"Sweden": 10000, "Denmark": 200000,
                       "Prussia": 10000})
        assert any(e["type"] == "ai_bandwagon_reneged"
                   for e in process_bandwagon(world))
        from backend.models.world_state import WorldState
        with contextlib.redirect_stdout(io.StringIO()):
            back = WorldState.from_dict(
                json.loads(json.dumps(world.to_dict(), default=str)))
        assert _bandwagon_renege_spent(back, "Prussia")


# The seeds whose 40-turn world-lines moved under the hook, T2-2 record →
# T2-3 record (the per-seed truth): marengo ALONE — Prussia bandwagons
# into Hesse's war on Hanover at T20, the turn it opens, and Hanover,
# which survived before, is eliminated at T23. The other nine keep
# theirs, HISTORICAL among them (Prussia at peace in 1805, the historian
# clause untouched).
MOVED_SEEDS = ["marengo"]


class TestTheMeasure:
    """The dated re-record `tools/_dy_signature_t2_3_2026_11_08.json`
    against the T2-2 record (the kept-record idiom — each committed
    record stays its slice's truth)."""

    @pytest.fixture(scope="class")
    def records(self):
        prev = json.loads(
            (REPO / "tools" / "_dy_signature_t2_2_2026_11_08.json")
            .read_text(encoding="utf-8"))
        new = json.loads(
            (REPO / "tools" / "_dy_signature_t2_3_2026_11_08.json")
            .read_text(encoding="utf-8"))
        return prev, new

    def test_the_hook_keeps_the_floor(self, records):
        prev, new = records
        assert new["story_class_count"] >= prev["story_class_count"]
        assert new["story_class_count"] == 10

    def test_the_moved_seeds_are_the_record(self, records):
        prev, new = records
        moved = [s for s in sorted(prev["seeds"])
                 if prev["seeds"][s]["signature"]
                 != new["seeds"][s]["signature"]]
        assert moved == MOVED_SEEDS, moved

    def test_historical_is_byte_identical(self, records):
        prev, new = records
        assert prev["seeds"]["historical"] == new["seeds"]["historical"]

    def test_hanover_falls_on_marengo(self, records):
        """The mover's content: the bandwagoned weight finishes the war
        the join joined — Hanover's elimination at T23 is the one new
        row, Bavaria's and Switzerland's unchanged."""
        prev, new = records
        assert (new["seeds"]["marengo"]["signature"]["eliminations"]
                == [[6, "Bavaria"], [23, "Hanover"], [27, "Switzerland"]])
        assert (prev["seeds"]["marengo"]["signature"]["eliminations"]
                == [[6, "Bavaria"], [27, "Switzerland"]])
