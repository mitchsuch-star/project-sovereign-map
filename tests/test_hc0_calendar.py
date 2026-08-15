"""HC-0 "The Calendar" — display-only turn dating (gate §2a).

One turn = HALF A MONTH (~15 days): two turns per month, 24 per year.
Gate acceptance: turn 1 renders "Late September 1805", turn 6
"Early December 1805", turn 25 "Late September 1806"; the legacy world
stays byte-identical (label ""); `current_turn` remains the single
source of time (the label is derived, never stored).
"""

import json
from pathlib import Path

from backend.game_logic.calendar import (
    MONTH_NAMES,
    TURNS_PER_YEAR,
    calendar_label,
    parse_start_date,
)
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
MAPS = REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
EUROPE_SCENARIO = MAPS / "europe_1805.json"
TUTORIAL_SCENARIO = MAPS / "tutorial_1805.json"


class TestPureDerivation:
    """The gate's acceptance arithmetic, pinned as falsifiable cases."""

    def test_turn_1_is_late_september_1805(self):
        assert calendar_label("1805-09-25", 1) == "Late September 1805"

    def test_turn_6_is_early_december_1805(self):
        # Winter arrives on time for Austerlitz (HC-6 consumes this).
        assert calendar_label("1805-09-25", 6) == "Early December 1805"

    def test_turn_25_wraps_the_year(self):
        assert calendar_label("1805-09-25", 25) == "Late September 1806"

    def test_two_turns_per_month(self):
        assert calendar_label("1805-09-25", 2) == "Early October 1805"
        assert calendar_label("1805-09-25", 3) == "Late October 1805"

    def test_day_15_opens_the_early_half(self):
        assert calendar_label("1805-09-15", 1) == "Early September 1805"

    def test_day_16_opens_the_late_half(self):
        assert calendar_label("1805-09-16", 1) == "Late September 1805"

    def test_full_year_cycle_returns_to_the_same_half(self):
        for anchor in ("1805-09-25", "1805-01-01", "1812-06-24"):
            first = calendar_label(anchor, 1)
            year_later = calendar_label(anchor, 1 + TURNS_PER_YEAR)
            # Same "Half Month", year advanced by exactly one.
            assert first.rsplit(" ", 1)[0] == year_later.rsplit(" ", 1)[0]
            assert int(year_later.rsplit(" ", 1)[1]) == int(first.rsplit(" ", 1)[1]) + 1

    def test_december_late_half_rolls_the_year(self):
        assert calendar_label("1805-12-20", 1) == "Late December 1805"
        assert calendar_label("1805-12-20", 2) == "Early January 1806"

    def test_absent_or_invalid_anchor_derives_empty(self):
        assert calendar_label("", 1) == ""
        assert calendar_label(None, 1) == ""  # type: ignore[arg-type]
        assert calendar_label("1805-13-01", 1) == ""
        assert calendar_label("1805-00-10", 1) == ""
        assert calendar_label("1805-02-30", 1) == ""
        assert calendar_label("Sept 25, 1805", 1) == ""
        assert calendar_label("1805-9-25", 1) == ""

    def test_non_positive_turn_derives_empty(self):
        assert calendar_label("1805-09-25", 0) == ""
        assert calendar_label("1805-09-25", -3) == ""

    def test_parse_start_date_shapes(self):
        assert parse_start_date("1805-09-25") == (1805, 9, 25)
        assert parse_start_date("") is None
        assert parse_start_date("1805/09/25") is None

    def test_leap_day_is_leap_checked(self):
        # Review round [5/14]: 1805 is no leap year — an impossible
        # authored date hard-fails; a real leap day parses.
        assert parse_start_date("1805-02-29") is None
        assert parse_start_date("1808-02-29") == (1808, 2, 29)
        assert parse_start_date("1900-02-29") is None  # century rule
        assert parse_start_date("2000-02-29") == (2000, 2, 29)

    def test_month_table_is_complete(self):
        assert len(MONTH_NAMES) == 12
        assert MONTH_NAMES[8] == "September"


class TestWorldWiring:
    """The anchor rides the scenario_name funnel; the label rides the
    summary/dispatch/ledger/save-metadata surfaces."""

    def test_scenario_boot_carries_the_anchor(self):
        world = WorldState.from_scenario(str(EUROPE_SCENARIO))
        assert world.start_date == "1805-09-25"
        assert world.get_calendar_label() == "Late September 1805"

    def test_tutorial_scenario_same_anchor(self):
        world = WorldState.from_scenario(str(TUTORIAL_SCENARIO))
        assert world.start_date == "1805-09-25"
        assert world.get_calendar_label() == "Late September 1805"

    def test_legacy_world_is_dormant(self):
        world = WorldState()
        assert world.start_date == ""
        assert world.get_calendar_label() == ""
        assert world.get_action_summary()["calendar_label"] == ""
        assert world.get_filtered_game_state_summary()["calendar_label"] == ""

    def test_label_advances_with_the_turn(self):
        world = WorldState.from_scenario(str(EUROPE_SCENARIO))
        world.current_turn = 6
        assert world.get_calendar_label() == "Early December 1805"
        assert world.get_action_summary()["calendar_label"] == "Early December 1805"

    def test_serialization_round_trip(self):
        world = WorldState()
        world.start_date = "1805-09-25"
        data = world.to_dict()
        assert data["start_date"] == "1805-09-25"
        restored = WorldState.from_dict(data)
        assert restored.start_date == "1805-09-25"

    def test_pre_field_save_backfills_empty(self):
        world = WorldState()
        data = world.to_dict()
        data.pop("start_date", None)
        restored = WorldState.from_dict(data)
        assert restored.start_date == ""
        assert restored.get_calendar_label() == ""

    def test_turn_stays_an_int_beside_the_label(self):
        # The Godot int pin: the label is a SEPARATE string key, never a
        # replacement of the int `turn`.
        world = WorldState.from_scenario(str(EUROPE_SCENARIO))
        summary = world.get_action_summary()
        assert isinstance(summary["turn"], int)
        assert isinstance(summary["calendar_label"], str)

    def test_dispatch_carries_the_label(self):
        from backend.game_logic.dispatch import build_morning_dispatch
        world = WorldState.from_scenario(str(EUROPE_SCENARIO))
        dispatch = build_morning_dispatch(world, [])
        assert dispatch["calendar_label"] == "Late September 1805"
        assert dispatch["turn"] == world.current_turn

    def test_dispatch_empty_on_legacy(self):
        from backend.game_logic.dispatch import build_morning_dispatch
        world = WorldState()
        dispatch = build_morning_dispatch(world, [])
        assert dispatch["calendar_label"] == ""

    def test_ledger_carries_the_label(self):
        from backend.game_logic.ledger import build_strategic_ledger
        world = WorldState.from_scenario(str(EUROPE_SCENARIO))
        ledger = build_strategic_ledger(world)
        assert ledger["calendar_label"] == "Late September 1805"

    def test_save_metadata_carries_the_label(self, tmp_path):
        from backend import save_manager
        world = WorldState.from_scenario(str(EUROPE_SCENARIO))
        target = tmp_path / "hc0_calendar_save.json"
        result = save_manager.save_game(world, "HC0 test", filepath=target)
        assert result["success"], result
        saved = json.loads(target.read_text(encoding="utf-8"))
        assert saved["metadata"]["calendar_label"] == "Late September 1805"
        assert saved["metadata"]["turn"] == world.current_turn


class TestValidator:
    def _validate(self, extra):
        from backend.modding.validator import validate_scenario
        data = {"scenario_schema_version": 1}
        data.update(extra)
        return validate_scenario(data)

    def test_valid_start_date_passes(self):
        result = self._validate({"start_date": "1805-09-25"})
        assert not any(e.path == "start_date" for e in result.errors)

    def test_absent_start_date_is_fine(self):
        result = self._validate({})
        assert not any(e.path == "start_date" for e in result.errors)

    def test_malformed_date_hard_fails(self):
        for bad in ("1805-02-30", "sept 25", "1805-9-25", 1805):
            result = self._validate({"start_date": bad})
            assert any(e.path == "start_date" for e in result.errors), bad


class TestDisplayOnlyPin:
    """Never-do pin: no mechanic reads the calendar in this slice —
    `current_turn` stays the single source of time. The calendar module
    must stay a pure derivation (no world mutation, no game_logic
    imports beyond itself)."""

    def test_calendar_module_is_pure(self):
        import ast
        import inspect
        import backend.game_logic.calendar as cal
        tree = ast.parse(Path(cal.__file__).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names]
                module = getattr(node, "module", "") or ""
                assert "world_state" not in module, (
                    "calendar.py must never import the world")
                assert all("world" not in n for n in names)
            if isinstance(node, ast.FunctionDef):
                args = [a.arg for a in node.args.args]
                assert "world" not in args, (
                    f"{node.name} must stay a pure (anchor, turn) "
                    "derivation — it must never take a world")
        # And the callable surface is exactly the pure pair.
        public = [n for n, f in vars(cal).items()
                  if inspect.isfunction(f) and not n.startswith("_")]
        assert sorted(public) == ["calendar_label", "parse_start_date"]

    def test_label_derivation_does_not_mutate_the_world(self):
        world = WorldState.from_scenario(str(EUROPE_SCENARIO))
        before = world.to_dict()
        world.get_calendar_label()
        world.get_calendar_label()
        assert world.to_dict() == before
