"""UXR-X28 — the map's furniture at the whole-map view (Pre-Deploy S12b,
Slice 0, October 14, 2026).

UXR-X4's floor made every name, chip and sail count readable at the fit zoom;
where the boot board masses corps it also crowded them. The marshals' names
brushed the nation names, a garrison chip sat on HOLLAND, and at Venetia a
fogged "?" covered Masséna's name: the furniture (world-space Labels in the
map's SubViewport, built by `map_renderer_base.gd`) and the place names (draw
calls in `map_label_layer.gd`) were laid out by two systems that never saw
each other.

The instrument came first: the capture harness records every map-tier text
row's SCREEN rect (through the SubViewport's canvas transform and the
display's offset and scale) and the place names the label layer drew;
`tools/uxr3_frame_census.py` reads `map_overlaps` from them. Then the fix:
the label layer lays the furniture out in ONE priority order — the place
names keep their place, then the standees' names, then the chips, which
yield (nudged within one chip's width, or hidden at that zoom).

These pins hold the result on its committed record
(`docs/audits/uxr_d4/map_census.json`, `tools/uxr_d4_map_census.py`) and the
order on the source — never on Godot.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
RECORD = REPO / "docs" / "audits" / "uxr_d4" / "map_census.json"
SCENES = REPO / "godot-client" / "project-sovereign" / "scenes"
LABEL_GD = SCENES / "map_label_layer.gd"
BASE_GD = SCENES / "map_renderer_base.gd"
HARNESS = REPO / "tools" / "iq10_surface_screenshot.gd"
sys.path.insert(0, str(REPO / "tools"))

import uxr3_frame_census as FC  # noqa: E402
from uxr0_readability_report import PHYSICAL_RESOLUTIONS  # noqa: E402

FIVE = [f"{w}x{h}" for (w, h) in PHYSICAL_RESOLUTIONS]
NAME_KINDS = {"name", "stack", "fog_name", "nation", "province"}
CHIP_KINDS = {"fog_chip", "garrison", "sail"}


def _record() -> dict:
    assert RECORD.is_file(), f"the committed record is missing: {RECORD}"
    return json.loads(RECORD.read_text(encoding="utf-8"))


def _func_body(source: str, signature: str) -> str:
    return source.split(signature, 1)[1].split("\nfunc ", 1)[0]


class TestTheCensusOnItsRecord:
    def test_the_before_board_measured_the_crowd(self):
        before = _record()["boards"]["before"]
        assert before["surfaces"] == ["war_room_boot"]
        assert sorted(before["resolutions"]) == sorted(FIVE)
        assert before["map_frames"] == 5
        # Measured before any fix (the slice's commit records the count).
        assert before["map_overlaps_count"] == 71
        assert before["map_overlaps_count"] == len(before["map_overlaps"])
        # The row's own sightings are in it: a garrison chip on a nation's
        # name, a fogged "?" on Masséna's.
        kinds = before["map_overlaps_by_kind"]
        assert kinds.get("garrison / nation", 0) > 0
        assert any(o["a"] == "name:Massena" and o["b"] == "fog_chip:?" for o in before["map_overlaps"])

    def test_the_whole_map_reads_clear_with_the_dock_closed(self):
        board = _record()["boards"]["dock_closed"]
        assert board["surfaces"] == ["war_room_boot"]
        assert sorted(board["resolutions"]) == sorted(FIVE)
        assert board["map_frames"] == 5
        assert board["map_overlaps_count"] == 0 and board["map_overlaps"] == []
        assert set(board["map_overlaps_by_resolution"].values()) == {0}

    def test_the_whole_map_reads_clear_with_the_dock_open(self):
        # S12b Slice 3: the Side Desk's dock narrows the map's room and the
        # whole-map view re-fits into it (a denser map) — still 0.
        board = _record()["boards"]["dock_open"]
        assert sorted(board["surfaces"]) == ["side_desk_generals", "side_desk_ledger"]
        assert sorted(set(board["resolutions"])) == sorted(FIVE)
        assert board["map_frames"] == 10
        assert board["map_overlaps_count"] == 0 and board["map_overlaps"] == []

    def test_no_standee_name_ever_hides(self):
        # The zero is never bought by hiding a standee's name: what the
        # layout hid is recorded, and it is chips, or a fogged force's name
        # (the lowest of the names: its "?" chip and its tooltip stay) — and
        # with the dock closed, chips alone.
        for name, board in _record()["boards"].items():
            for row in board["map_hidden"]:
                kind = row["what"].split(":", 1)[0]
                assert kind in CHIP_KINDS | {"fog_name"}, (name, row)
                if name == "dock_closed":
                    assert kind in CHIP_KINDS, (name, row)

    def test_the_census_reads_the_furniture_and_the_place_names(self):
        frame = {
            "texts": [
                {"tier": "map", "text": "Ney", "map_kind": "name", "path": "a", "rect": [0, 0, 40, 16]},
                {"tier": "map", "text": "12k", "map_kind": "garrison", "path": "b", "rect": [30, 10, 30, 16]},
                {"tier": "body", "text": "Execute", "path": "c", "rect": [0, 0, 80, 20]},
            ],
            "map_labels": [{"text": "Holland", "tier": "nation", "rect": [100, 0, 80, 30]}],
            "map_furniture": {"hidden": ["fog_chip:?"]},
        }
        rows = FC.map_rows(frame)
        assert [r["kind"] for r in rows] == ["name", "garrison", "nation"]
        out = {"map_frames": 0, "map_overlaps": [], "map_hidden": []}
        FC._map_census(out, "s", "1920x1080", frame)
        assert [(o["a"], o["b"]) for o in out["map_overlaps"]] == [("name:Ney", "garrison:12k")]
        assert out["map_hidden"] == [{"surface": "s", "res": "1920x1080", "what": "fog_chip:?"}]


class TestThePriorityOrder:
    def test_names_first_then_chips(self):
        src = LABEL_GD.read_text(encoding="utf-8")
        order = re.search(r"const FURNITURE_PRIORITY := \[(.*?)\]", src).group(1)
        assert [s.strip().strip('"') for s in order.split(",")] == [
            "name", "stack", "fog_name", "fog_chip", "garrison", "sail"]
        names = re.search(r"const FURNITURE_NAME_KINDS := \[(.*?)\]", src).group(1)
        assert [s.strip().strip('"') for s in names.split(",")] == ["name", "stack", "fog_name"]
        # A chip moves within one chip's width, or hides.
        assert re.search(r"const CHIP_REACH_WIDTHS: float = 1\.0\b", src)
        ordered = _func_body(src, "func _ordered_furniture() -> Array:")
        assert "FURNITURE_PRIORITY.find(" in ordered and "_by_rank_then_order" in ordered

    def test_the_place_names_stand_before_any_furniture(self):
        src = LABEL_GD.read_text(encoding="utf-8")
        body = _func_body(src, "func _lay_out(proj: Dictionary) -> void:")
        # Every place name is placed (no UI, no cull) before the furniture
        # is laid out against them.
        assert body.index("placed.append(rect)") < body.index("_lay_out_furniture(xform, placed, pieces)")
        furniture = _func_body(src, "func _lay_out_furniture(xform: Transform2D, obstacles: Array, pieces: Array) -> void:")
        # Each laid-out item becomes an obstacle for the ones after it; one
        # with no free place hides.
        assert "obstacles.append(Rect2(r.position + d, r.size))" in furniture
        assert "(n as CanvasItem).visible = false" in furniture
        assert "_reset_item(item)" in furniture, "every layout starts from the authored places"

    def test_a_name_off_its_laid_out_place_clears_the_furniture(self):
        src = LABEL_GD.read_text(encoding="utf-8")
        tier = _func_body(src, "func _draw_label_tier(spec: Dictionary, xform: Transform2D, avoid: Array, ui_rects: Array,")
        assert "if fresh and _laid_out_offsets.has(i):" in tier
        assert "avoid + ui_rects + guard" in tier

    def test_the_layout_runs_once_per_settled_zoom(self):
        src = LABEL_GD.read_text(encoding="utf-8")
        proc = _func_body(src, "func _process(_delta: float) -> void:")
        assert "is_zoom_settled()" in proc and "if key == _laid_out_key:" in proc
        assert "_projection()[\"xform\"] != _drawn_xform" in proc, (
            "a camera moved in code redraws the names once its transform lands")
        base = BASE_GD.read_text(encoding="utf-8")
        settled = _func_body(base, "func is_zoom_settled() -> bool:")
        assert "zoom_tween.is_running()" in settled and "_furniture_rescale_pending" in settled


class TestTheRendererHandsItOver:
    def test_every_text_furniture_kind_is_an_item(self):
        base = BASE_GD.read_text(encoding="utf-8")
        for kind in ("name", "stack", "fog_name", "fog_chip", "garrison"):
            assert f'_add_furniture("{kind}", [' in base, kind
            assert f'set_meta("furniture_kind", "{kind}")' in base, kind
        assert 'set_meta("furniture_kind", "sail")' in base
        assert '_sail_items[sail.get_instance_id()] = {"kind": "sail"' in base
        for fn in ("func _rebuild_dynamic_nodes():", "func _update_fleet_pieces() -> void:",
                   "func _layout_sail_labels() -> void:"):
            assert "_push_furniture()" in _func_body(base, fn), fn

    def test_the_pieces_alone_push_a_place_name(self):
        # The text furniture no longer pushes a place name off its place: it
        # yields to it. Only the pieces' footprints are avoid rects.
        base = BASE_GD.read_text(encoding="utf-8")
        appends = re.findall(r"_label_avoid_world_rects\.append\((.*?)\)\n", base)
        assert appends == ["hitbox_rect"], appends

    def test_a_fogged_name_is_the_man_not_the_key(self):
        base = BASE_GD.read_text(encoding="utf-8")
        body = _func_body(base, "func _create_fogged_force_nodes(")
        assert 'Utils.display_marshal_name(str(force.get("name", "?")))' in body


class TestTheInstrument:
    def test_the_harness_records_map_rects_and_the_drawn_names(self):
        src = HARNESS.read_text(encoding="utf-8")
        assert 'entry["rect"] = mr' in _func_body(src, "func _add_fit_fields(entry: Dictionary, n: Control) -> void:")
        assert "get_global_transform_with_canvas()" in _func_body(src, "func _map_screen_rect(n: Control) -> Array:")
        assert 'frame["map_labels"] = _map_labels()' in src
        assert 'frame["map_furniture"] = _map_furniture_report()' in src
        label = LABEL_GD.read_text(encoding="utf-8")
        assert "func drawn_label_rects() -> Array:" in label and "func furniture_report() -> Dictionary:" in label
