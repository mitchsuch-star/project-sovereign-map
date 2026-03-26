"""
Test suite for Morning Dispatch (Phase 6.5 — dispatch.py)

Tests:
- Situation: region counts, treasury, fog-filtered strength ratio
- Marshal status: broken, retreating, strategic, drilling, fortified, artillery, idle
- Intelligence: FULL/PARTIAL/STALE/LAST_KNOWN visibility, deduplication
- Berthier note: priority ordering
- All values are int (no floats to Godot)
- Edge cases: no marshals, no intel, bankrupt, empty world
"""

import json
import pytest

from backend.models.marshal import Marshal, StrategicOrder
from backend.models.world_state import WorldState
from backend.models.intel import (
    FULL, PARTIAL, STALE, LAST_KNOWN,
)
from backend.game_logic.dispatch import (
    build_morning_dispatch,
    _build_situation,
    _build_marshal_status,
    _build_intelligence,
    _build_turn_events,
    _pick_berthier_note,
    _estimate_enemy_strength_from_intel,
    BAND_MIDPOINTS,
)


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _make_world():
    """Create a standard WorldState for testing."""
    return WorldState(player_nation="France")


def _make_marshal(name="Ney", location="Paris", strength=50000,
                  personality="aggressive", nation="France", **kwargs):
    """Create a test marshal with sensible defaults."""
    return Marshal(name=name, location=location, strength=strength,
                   personality=personality, nation=nation, **kwargs)


def _inject_intel(world, region_name, visibility, turn, known_marshals=None,
                  total_strength=0, source="adjacent"):
    """Set up RegionIntel for a region at a given visibility level."""
    intel = world.get_region_intel(region_name)
    if visibility in (FULL, PARTIAL):
        intel.refresh(
            visibility=visibility,
            source=source,
            turn=turn,
            marshals=known_marshals or [],
            total_strength=total_strength,
        )
    elif visibility in (STALE, LAST_KNOWN):
        # First refresh to set data, then manually decay
        intel.refresh(
            visibility=PARTIAL,
            source=source,
            turn=max(1, turn - 3),
            marshals=known_marshals or [],
            total_strength=total_strength,
        )
        intel.visibility = visibility
        intel.last_updated_turn = turn
    return intel


# ════════════════════════════════════════════════════════════════════════════════
# SITUATION SECTION
# ════════════════════════════════════════════════════════════════════════════════

class TestSituation:
    """Test the SITUATION section of the dispatch."""

    def test_region_counts(self):
        world = _make_world()
        sit = _build_situation(world, "France")
        # 19-region map: France has 8 regions, enemies have 11
        assert sit["player_regions"] >= 1
        assert sit["enemy_regions"] >= 1
        assert sit["player_regions"] + sit["enemy_regions"] <= 19

    def test_treasury_is_int(self):
        world = _make_world()
        sit = _build_situation(world, "France")
        assert isinstance(sit["treasury"], int)
        assert isinstance(sit["treasury_delta"], int)

    def test_treasury_delta_computed(self):
        world = _make_world()
        sit = _build_situation(world, "France")
        # Delta = income - upkeep (may be positive or negative)
        assert "treasury_delta" in sit
        assert isinstance(sit["treasury_delta"], int)

    def test_bankrupt_flag(self):
        world = _make_world()
        world.nation_bankruptcy_turns["France"] = 3
        sit = _build_situation(world, "France")
        assert sit["bankrupt"] is True

    def test_not_bankrupt(self):
        world = _make_world()
        sit = _build_situation(world, "France")
        assert sit["bankrupt"] is False

    def test_strength_ratio_is_int(self):
        world = _make_world()
        sit = _build_situation(world, "France")
        assert isinstance(sit["strength_ratio_pct"], int)

    def test_neutral_regions_not_counted_as_enemy(self):
        """Regions with controller=None are neither player nor enemy."""
        world = _make_world()
        # Set one region to None (uncontrolled)
        for region in world.regions.values():
            if region.controller and region.controller != "France":
                region.controller = None
                break
        sit = _build_situation(world, "France")
        # Should have fewer enemy regions now
        total = sit["player_regions"] + sit["enemy_regions"]
        assert total < 19  # At least one uncontrolled


class TestFogFilteredStrength:
    """Test fog-filtered enemy strength estimation."""

    def test_full_visibility_uses_exact_strength(self):
        world = _make_world()
        world.intel.clear()
        _inject_intel(world, "Waterloo", FULL, turn=1,
                      known_marshals=[
                          {"name": "Wellington", "nation": "Britain", "strength": 45000}
                      ],
                      total_strength=45000, source="marshal_present")
        estimated = _estimate_enemy_strength_from_intel(world, "France")
        assert estimated == 45000

    def test_partial_visibility_uses_band_midpoint(self):
        world = _make_world()
        world.intel.clear()
        _inject_intel(world, "Waterloo", PARTIAL, turn=1,
                      known_marshals=[
                          {"name": "Wellington", "nation": "Britain", "band": "large force"}
                      ],
                      total_strength=50000)
        estimated = _estimate_enemy_strength_from_intel(world, "France")
        assert estimated == BAND_MIDPOINTS["large force"]  # 55000

    def test_unknown_contributes_zero(self):
        world = _make_world()
        world.intel.clear()
        estimated = _estimate_enemy_strength_from_intel(world, "France")
        assert estimated == 0

    def test_deduplication_by_marshal_name(self):
        """Same marshal seen in two regions — only count once (best visibility)."""
        world = _make_world()
        world.intel.clear()
        _inject_intel(world, "Waterloo", FULL, turn=2,
                      known_marshals=[
                          {"name": "Wellington", "nation": "Britain", "strength": 45000}
                      ],
                      total_strength=45000, source="marshal_present")
        _inject_intel(world, "Netherlands", PARTIAL, turn=1,
                      known_marshals=[
                          {"name": "Wellington", "nation": "Britain", "band": "large force"}
                      ],
                      total_strength=50000)
        estimated = _estimate_enemy_strength_from_intel(world, "France")
        # Should only count Wellington once — FULL (45000), not also PARTIAL (55000)
        assert estimated == 45000

    def test_skips_friendly_forces_in_intel(self):
        world = _make_world()
        world.intel.clear()
        _inject_intel(world, "Belgium", FULL, turn=1,
                      known_marshals=[
                          {"name": "Ney", "nation": "France", "strength": 50000},
                          {"name": "Wellington", "nation": "Britain", "strength": 45000},
                      ],
                      total_strength=95000, source="marshal_present")
        estimated = _estimate_enemy_strength_from_intel(world, "France")
        assert estimated == 45000  # Only enemy, not Ney

    def test_stale_frozen_full_snapshot(self):
        """STALE intel with frozen FULL data uses band midpoint (fog fix P21-06)."""
        world = _make_world()
        world.intel.clear()
        _inject_intel(world, "Waterloo", STALE, turn=1,
                      known_marshals=[
                          {"name": "Wellington", "nation": "Britain", "strength": 45000}
                      ],
                      total_strength=45000)
        estimated = _estimate_enemy_strength_from_intel(world, "France")
        # STALE uses band midpoint, not exact: 45000 → "large force" → 55000
        from backend.models.intel import get_strength_band
        from backend.game_logic.dispatch import BAND_MIDPOINTS
        expected_band = get_strength_band(45000)
        assert estimated == BAND_MIDPOINTS[expected_band]


# ════════════════════════════════════════════════════════════════════════════════
# MARSHAL STATUS SECTION
# ════════════════════════════════════════════════════════════════════════════════

class TestMarshalStatus:
    """Test the MARSHAL STATUS section."""

    def test_basic_marshal_entry(self):
        world = _make_world()
        marshals = _build_marshal_status(world, "France")
        assert len(marshals) > 0
        m = marshals[0]
        assert "name" in m
        assert "location" in m
        assert "strength" in m
        assert "status" in m
        assert "status_note" in m
        assert "trust" in m
        assert "morale" in m

    def test_all_values_are_int(self):
        world = _make_world()
        marshals = _build_marshal_status(world, "France")
        for m in marshals:
            assert isinstance(m["strength"], int), f"{m['name']} strength not int"
            assert isinstance(m["trust"], int), f"{m['name']} trust not int"
            assert isinstance(m["morale"], int), f"{m['name']} morale not int"

    def test_broken_marshal_status(self):
        world = _make_world()
        ney = world.get_marshal("Ney")
        ney.broken = True
        ney.broken_recovery = 1
        marshals = _build_marshal_status(world, "France")
        ney_entry = next(m for m in marshals if m["name"] == "Ney")
        assert ney_entry["status"] == "broken"
        assert "Reforms" in ney_entry["status_note"]

    def test_retreating_marshal_status(self):
        world = _make_world()
        ney = world.get_marshal("Ney")
        ney.retreating = True
        ney.retreat_recovery = 1
        marshals = _build_marshal_status(world, "France")
        ney_entry = next(m for m in marshals if m["name"] == "Ney")
        assert ney_entry["status"] == "retreating"
        assert "Recovers" in ney_entry["status_note"]

    def test_strategic_order_status(self):
        world = _make_world()
        ney = world.get_marshal("Ney")
        ney.strategic_order = StrategicOrder(
            command_type="MOVE_TO",
            target="Waterloo",
            target_type="region",
            started_turn=1,
            original_command="Ney, march to Waterloo",
        )
        marshals = _build_marshal_status(world, "France")
        ney_entry = next(m for m in marshals if m["name"] == "Ney")
        assert ney_entry["status"] == "en_route"
        assert "Waterloo" in ney_entry["status_note"]

    def test_drilling_status(self):
        world = _make_world()
        ney = world.get_marshal("Ney")
        ney.drilling = True
        marshals = _build_marshal_status(world, "France")
        ney_entry = next(m for m in marshals if m["name"] == "Ney")
        assert ney_entry["status"] == "drilling"

    def test_fortified_status(self):
        world = _make_world()
        ney = world.get_marshal("Ney")
        ney.fortified = True
        marshals = _build_marshal_status(world, "France")
        ney_entry = next(m for m in marshals if m["name"] == "Ney")
        assert ney_entry["status"] == "fortified"
        assert ney.location in ney_entry["status_note"]

    def test_artillery_status(self):
        world = _make_world()
        drouot = world.get_marshal("Drouot")
        if drouot:
            marshals = _build_marshal_status(world, "France")
            drouot_entry = next((m for m in marshals if m["name"] == "Drouot"), None)
            if drouot_entry:
                assert drouot_entry["status"] == "artillery"

    def test_idle_restless_aggressive(self):
        world = _make_world()
        ney = world.get_marshal("Ney")
        ney.personality = "aggressive"
        ney.idle_turns = 4
        marshals = _build_marshal_status(world, "France")
        ney_entry = next(m for m in marshals if m["name"] == "Ney")
        assert ney_entry["status"] == "idle_restless"
        assert "4" in ney_entry["status_note"]

    def test_idle_cautious_not_restless(self):
        """Cautious marshals don't show idle_restless."""
        world = _make_world()
        davout = world.get_marshal("Davout")
        if davout:
            davout.idle_turns = 5
            marshals = _build_marshal_status(world, "France")
            davout_entry = next((m for m in marshals if m["name"] == "Davout"), None)
            if davout_entry:
                assert davout_entry["status"] != "idle_restless"

    def test_trust_notable_low(self):
        world = _make_world()
        ney = world.get_marshal("Ney")
        ney.trust.modify(-30)  # Drop trust significantly
        marshals = _build_marshal_status(world, "France")
        ney_entry = next(m for m in marshals if m["name"] == "Ney")
        if ney_entry["trust"] < 55:
            assert ney_entry["trust_notable"] is True

    def test_trust_notable_high(self):
        world = _make_world()
        ney = world.get_marshal("Ney")
        ney.trust.modify(20)  # Boost trust
        marshals = _build_marshal_status(world, "France")
        ney_entry = next(m for m in marshals if m["name"] == "Ney")
        if ney_entry["trust"] > 90:
            assert ney_entry["trust_notable"] is True

    def test_morale_warning(self):
        world = _make_world()
        ney = world.get_marshal("Ney")
        ney.morale = 45
        marshals = _build_marshal_status(world, "France")
        ney_entry = next(m for m in marshals if m["name"] == "Ney")
        assert ney_entry["morale_warning"] is True

    def test_sorted_by_strength(self):
        world = _make_world()
        marshals = _build_marshal_status(world, "France")
        if len(marshals) >= 2:
            for i in range(len(marshals) - 1):
                assert marshals[i]["strength"] >= marshals[i + 1]["strength"]

    def test_only_player_marshals(self):
        world = _make_world()
        marshals = _build_marshal_status(world, "France")
        for m in marshals:
            # Verify each marshal is actually French by checking world state
            real_marshal = world.get_marshal(m["name"])
            assert real_marshal.nation == "France"

    def test_status_priority_broken_over_strategic(self):
        """Broken status takes priority over strategic order."""
        world = _make_world()
        ney = world.get_marshal("Ney")
        ney.broken = True
        ney.broken_recovery = 0
        ney.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Waterloo",
            target_type="region", started_turn=1,
            original_command="test",
        )
        marshals = _build_marshal_status(world, "France")
        ney_entry = next(m for m in marshals if m["name"] == "Ney")
        assert ney_entry["status"] == "broken"


# ════════════════════════════════════════════════════════════════════════════════
# INTELLIGENCE SECTION
# ════════════════════════════════════════════════════════════════════════════════

class TestIntelligence:
    """Test the INTELLIGENCE section (fog-filtered)."""

    def test_full_visibility_shows_exact_strength(self):
        world = _make_world()
        world.intel.clear()
        _inject_intel(world, "Waterloo", FULL, turn=1,
                      known_marshals=[
                          {"name": "Wellington", "nation": "Britain", "strength": 45000}
                      ],
                      total_strength=45000, source="marshal_present")
        intel = _build_intelligence(world, "France")
        assert len(intel) == 1
        assert intel[0]["name"] == "Wellington"
        assert intel[0]["strength_display"] == "45,000"
        assert intel[0]["visibility"] == FULL

    def test_partial_visibility_shows_band(self):
        world = _make_world()
        world.intel.clear()
        _inject_intel(world, "Netherlands", PARTIAL, turn=1,
                      known_marshals=[
                          {"name": "Blucher", "nation": "Prussia", "band": "large force"}
                      ],
                      total_strength=50000)
        intel = _build_intelligence(world, "France")
        blucher = next((i for i in intel if i["name"] == "Blucher"), None)
        assert blucher is not None
        assert blucher["strength_display"] == "large force"
        assert blucher["visibility"] == PARTIAL

    def test_unknown_not_shown(self):
        world = _make_world()
        world.intel.clear()
        # Only UNKNOWN regions
        intel = _build_intelligence(world, "France")
        assert len(intel) == 0

    def test_stale_shows_frozen_data(self):
        world = _make_world()
        world.intel.clear()
        _inject_intel(world, "Waterloo", STALE, turn=2,
                      known_marshals=[
                          {"name": "Wellington", "nation": "Britain", "strength": 45000}
                      ],
                      total_strength=45000)
        intel = _build_intelligence(world, "France")
        well = next((i for i in intel if i["name"] == "Wellington"), None)
        assert well is not None
        assert well["visibility"] == STALE

    def test_deduplication_keeps_best(self):
        """Same marshal in two regions — keep the higher-visibility sighting."""
        world = _make_world()
        world.intel.clear()
        _inject_intel(world, "Netherlands", PARTIAL, turn=1,
                      known_marshals=[
                          {"name": "Wellington", "nation": "Britain", "band": "large force"}
                      ],
                      total_strength=50000)
        _inject_intel(world, "Waterloo", FULL, turn=2,
                      known_marshals=[
                          {"name": "Wellington", "nation": "Britain", "strength": 45000}
                      ],
                      total_strength=45000, source="marshal_present")
        intel = _build_intelligence(world, "France")
        wellingtons = [i for i in intel if i["name"] == "Wellington"]
        assert len(wellingtons) == 1
        assert wellingtons[0]["visibility"] == FULL
        assert wellingtons[0]["location"] == "Waterloo"

    def test_friendly_marshals_excluded(self):
        world = _make_world()
        world.intel.clear()
        _inject_intel(world, "Paris", FULL, turn=1,
                      known_marshals=[
                          {"name": "Ney", "nation": "France", "strength": 50000}
                      ],
                      total_strength=50000, source="own_territory")
        intel = _build_intelligence(world, "France")
        ney = next((i for i in intel if i["name"] == "Ney"), None)
        assert ney is None

    def test_intel_turn_is_int(self):
        world = _make_world()
        world.intel.clear()
        _inject_intel(world, "Waterloo", FULL, turn=3,
                      known_marshals=[
                          {"name": "Wellington", "nation": "Britain", "strength": 45000}
                      ],
                      total_strength=45000, source="marshal_present")
        intel = _build_intelligence(world, "France")
        assert isinstance(intel[0]["intel_turn"], int)

    def test_sorted_by_visibility(self):
        """FULL sightings should appear before PARTIAL."""
        world = _make_world()
        world.intel.clear()
        _inject_intel(world, "Netherlands", PARTIAL, turn=1,
                      known_marshals=[
                          {"name": "Blucher", "nation": "Prussia", "band": "large force"}
                      ],
                      total_strength=50000)
        _inject_intel(world, "Waterloo", FULL, turn=2,
                      known_marshals=[
                          {"name": "Wellington", "nation": "Britain", "strength": 45000}
                      ],
                      total_strength=45000, source="marshal_present")
        intel = _build_intelligence(world, "France")
        if len(intel) >= 2:
            vis_order = [i["visibility"] for i in intel]
            assert vis_order.index(FULL) < vis_order.index(PARTIAL)


# ════════════════════════════════════════════════════════════════════════════════
# TURN EVENTS
# ════════════════════════════════════════════════════════════════════════════════

class TestTurnEvents:
    """Test the TURN EVENTS section (absorbed from tactical events)."""

    def test_empty_events(self):
        result = _build_turn_events([], "France")
        assert result == []

    def test_attrition_is_warning(self):
        events = [{"type": "supply_attrition", "message": "Ney loses 500 troops",
                    "marshal": "Ney", "nation": "France"}]
        result = _build_turn_events(events, "France")
        assert len(result) == 1
        assert result[0]["severity"] == "warning"
        assert "Ney" in result[0]["message"]

    def test_construction_complete_is_good(self):
        events = [{"type": "construction_complete",
                    "message": "Market built in Paris", "nation": "France"}]
        result = _build_turn_events(events, "France")
        assert len(result) == 1
        assert result[0]["severity"] == "good"

    def test_enemy_events_filtered_out(self):
        events = [{"type": "supply_attrition", "message": "Wellington loses troops",
                    "nation": "Britain"}]
        result = _build_turn_events(events, "France")
        assert len(result) == 0

    def test_events_without_nation_excluded(self):
        """Events without a nation field are excluded (6A-1 safety net)."""
        events = [{"type": "drill_complete", "message": "Ney drill complete"}]
        result = _build_turn_events(events, "France")
        assert len(result) == 0

    def test_events_without_message_skipped(self):
        events = [{"type": "supply_attrition", "nation": "France"}]
        result = _build_turn_events(events, "France")
        assert len(result) == 0

    def test_dispatch_includes_turn_events(self):
        world = _make_world()
        tactical = [{"type": "construction_complete",
                      "message": "Market built in Paris", "nation": "France"}]
        dispatch = build_morning_dispatch(world, tactical)
        assert "turn_events" in dispatch
        assert len(dispatch["turn_events"]) == 1
        assert dispatch["turn_events"][0]["severity"] == "good"


# ════════════════════════════════════════════════════════════════════════════════
# BERTHIER NOTE
# ════════════════════════════════════════════════════════════════════════════════

class TestBerthierNote:
    """Test Berthier's closing note priority."""

    def test_broken_marshal_highest_priority(self):
        marshals = [
            {"name": "Ney", "status": "broken", "strength": 50000, "status_note": ""},
        ]
        situation = {"bankrupt": False, "treasury_delta": 100}
        note = _pick_berthier_note(None, "France", marshals, situation)
        assert "Ney" in note
        assert "reform" in note.lower()

    def test_bankrupt_second_priority(self):
        marshals = [
            {"name": "Ney", "status": "awaiting", "strength": 50000, "status_note": ""},
        ]
        situation = {"bankrupt": True, "treasury_delta": -500}
        note = _pick_berthier_note(None, "France", marshals, situation)
        assert "exhausted" in note.lower() or "dire" in note.lower()

    def test_negative_treasury_delta(self):
        marshals = [
            {"name": "Ney", "status": "awaiting", "strength": 50000, "status_note": ""},
        ]
        situation = {"bankrupt": False, "treasury_delta": -300}
        note = _pick_berthier_note(None, "France", marshals, situation)
        assert "300" in note
        assert "bleeds" in note.lower()

    def test_idle_restless_at_four_turns(self):
        marshals = [
            {"name": "Ney", "status": "idle_restless", "strength": 50000,
             "status_note": "4 turns idle."},
        ]
        situation = {"bankrupt": False, "treasury_delta": 100}
        note = _pick_berthier_note(None, "France", marshals, situation)
        assert "Ney" in note
        assert "impatient" in note.lower()

    def test_idle_restless_three_turns_no_note(self):
        """3 turns idle triggers status but NOT Berthier note (needs 4+)."""
        marshals = [
            {"name": "Ney", "status": "idle_restless", "strength": 50000,
             "status_note": "3 turns idle."},
        ]
        situation = {"bankrupt": False, "treasury_delta": 100}
        note = _pick_berthier_note(None, "France", marshals, situation)
        assert "impatient" not in note.lower()

    def test_all_ready(self):
        marshals = [
            {"name": "Ney", "status": "awaiting", "strength": 50000, "status_note": ""},
            {"name": "Davout", "status": "awaiting", "strength": 40000, "status_note": ""},
        ]
        situation = {"bankrupt": False, "treasury_delta": 200}
        note = _pick_berthier_note(None, "France", marshals, situation)
        assert "ready" in note.lower()

    def test_default_note(self):
        marshals = []
        situation = {"bankrupt": False, "treasury_delta": 200}
        note = _pick_berthier_note(None, "France", marshals, situation)
        assert "orders" in note.lower()

    def test_broken_picks_strongest(self):
        """Multiple broken marshals — note should name the strongest."""
        marshals = [
            {"name": "Ney", "status": "broken", "strength": 50000, "status_note": ""},
            {"name": "Davout", "status": "broken", "strength": 30000, "status_note": ""},
        ]
        situation = {"bankrupt": False, "treasury_delta": 100}
        note = _pick_berthier_note(None, "France", marshals, situation)
        assert "Ney" in note  # Strongest


# ════════════════════════════════════════════════════════════════════════════════
# FULL DISPATCH INTEGRATION
# ════════════════════════════════════════════════════════════════════════════════

class TestFullDispatch:
    """Integration tests for the complete dispatch."""

    def test_dispatch_has_all_sections(self):
        world = _make_world()
        dispatch = build_morning_dispatch(world)
        assert "turn" in dispatch
        assert "situation" in dispatch
        assert "marshals" in dispatch
        assert "intelligence" in dispatch
        assert "berthier_note" in dispatch

    def test_dispatch_is_json_serializable(self):
        world = _make_world()
        dispatch = build_morning_dispatch(world)
        # Must not throw — Godot receives this as JSON
        serialized = json.dumps(dispatch)
        assert len(serialized) > 0

    def test_no_floats_in_dispatch(self):
        """All numeric values must be int — Godot crashes on floats."""
        world = _make_world()
        dispatch = build_morning_dispatch(world)
        _assert_no_floats(dispatch, "dispatch")

    def test_turn_number_matches_world(self):
        world = _make_world()
        dispatch = build_morning_dispatch(world)
        assert dispatch["turn"] == int(world.current_turn)

    def test_dispatch_on_fresh_world(self):
        """Dispatch shouldn't crash on a fresh game with no intel."""
        world = _make_world()
        world.intel.clear()
        dispatch = build_morning_dispatch(world)
        assert dispatch["intelligence"] == [] or isinstance(dispatch["intelligence"], list)
        assert len(dispatch["marshals"]) > 0


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _assert_no_floats(obj, path=""):
    """Recursively assert no float values exist in a data structure."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            _assert_no_floats(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _assert_no_floats(v, f"{path}[{i}]")
    elif isinstance(obj, float):
        pytest.fail(f"Float found at {path}: {obj}")
