"""UXR-3 fixes — the closing re-read, pinned on its committed records
(Pre-Deploy S12 part 2, October 14, 2026).

Part 2 fixed the rows part 1 left (the grip and the plate, R6's driven
proofs, the never-pressed controls, the boards, the rows found while reading
and fixing), then re-read every surface against the SAME frozen checklist
(`docs/UX_CHECKLIST_V1.json`) with the SAME tools on the final committed
tree:

    a whole-manifest shoot at five resolutions; the probe over every surface;
    the war-room roads (R6's live citations); the census, the fit report, the
    contrast report; the frame census (cut lines, grip overlaps, the centre
    tick); three FRESH blind readers for R2 / R5 / R8 given part 1's brief
    verbatim; the assembler (tools/uxr3_review.py); the comparison
    (tools/uxr3_reread.py, with part 1's filed rows UXR3-74 … 78).

The records are `docs/audits/uxr3_s12b/`; the write-up
`docs/audits/UXR3_REREAD2_2026_10_14.md`. These pins hold the re-read to its
records the way `tests/test_uxr3_s12_reread.py` holds part 1's: on the
committed JSON, never on Godot.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
REC = REPO / "docs" / "audits" / "uxr3_s12b"
BEFORE = REPO / "docs" / "audits" / "uxr3"
PART1 = REPO / "docs" / "audits" / "uxr3_s12"
CHECKLIST = REPO / "docs" / "UX_CHECKLIST_V1.json"
LEDGER = REPO / "docs" / "BUG_FIXES.md"
WRITE_UP = "docs/audits/UXR3_REREAD2_2026_10_14.md"
sys.path.insert(0, str(REPO / "tools"))

import uxr3_reread as RR  # noqa: E402
import uxr3_review as RV  # noqa: E402

ITEMS = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
SHOT_TREE = "cf0e5213"        # part 5c: the whole-manifest shoot, the probe, the war room
FIX_TREE = "4933a332"         # part 5d: its eleven boards re-shot and re-probed, merged
X9_TREE = "d34cbe91"          # part 5e: the tableaux and UXR-X9's board re-shot and re-probed, merged


def _load(name: str) -> dict:
    path = REC / name
    assert path.is_file(), f"the committed record is missing: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def _rows() -> list[dict]:
    return (json.loads((BEFORE / "bug_rows.json").read_text(encoding="utf-8"))
            + json.loads((PART1 / "new_rows.json").read_text(encoding="utf-8")))


def _ledger_line(row_id: str) -> str:
    text = LEDGER.read_text(encoding="utf-8")
    return next(ln for ln in text.splitlines() if ln.startswith(f"| **{row_id}** |"))


@pytest.fixture(scope="module")
def review() -> dict:
    return _load("review.json")


class TestTheRecordsAreTheTreeRead:
    def test_every_record_is_committed(self):
        for name in ("readability.json", "contrast.json", "consistency.json", "fit.json", "probe.json",
                     "war_room.json", "live_citations.json", "frame_census.json", "instrument_marks.json",
                     "review.json", "reread.json", "READER_BRIEF.md"):
            assert (REC / name).is_file(), name
        for n in (1, 2, 3):
            assert len(list((REC / "panel_raw" / f"reader_{n}").glob("group_*.json"))) == 10, n

    def test_one_tree_read_by_every_instrument(self):
        for name in ("readability.json", "contrast.json", "fit.json", "probe.json", "war_room.json",
                     "frame_census.json"):
            assert _load(name)["client_commit"].startswith(SHOT_TREE), name
        assert _load("contrast.json")["high_contrast"] is False
        assert _load("readability.json")["physical_scale"] == "auto"
        probe = _load("probe.json")
        assert probe["crashes"] == []
        assert [r["client_commit"] for r in probe["reprobes"]] == [FIX_TREE, X9_TREE]
        assert sorted(probe["reprobes"][0]["surfaces"]) == sorted(
            s for s in probe["shots"] if s.startswith(("diorama_", "top_bar_", "war_room_"))
            and s != "diorama_verdict_worst")
        assert sorted(probe["reprobes"][1]["surfaces"]) == sorted(
            s for s in probe["shots"] if s.startswith("diorama_"))

    def test_the_same_frozen_checklist_and_the_same_brief(self, review):
        assert review["checklist"] == "docs/UX_CHECKLIST_V1.json"
        ids = [s["id"] for g in json.loads(CHECKLIST.read_text(encoding="utf-8"))["groups"]
               for s in g["surfaces"]]
        assert list(review["surfaces"]) == ids
        # part 1's brief, verbatim
        assert (REC / "READER_BRIEF.md").read_text(encoding="utf-8") == \
            (PART1 / "READER_BRIEF.md").read_text(encoding="utf-8")


class TestTheReadingIsWholeAndReDerives:
    def test_every_surface_has_eight_marks(self, review):
        for sid, row in review["surfaces"].items():
            assert set(row["marks"]) == set(ITEMS), sid
            assert row["score"] == sum(1 for i in ITEMS if row["marks"][i]["pass"]), sid

    def test_the_instrument_marks_re_derive(self, review):
        again = RV.instrument_marks(REC)
        for sid, row in review["surfaces"].items():
            for item in ("R1", "R3", "R4", "R6", "R7"):
                assert row["marks"][item]["pass"] == again[sid][item]["pass"], (sid, item)

    def test_the_fresh_readers_aggregate_two_of_three(self, review):
        again = RV.aggregate(REC, REC)
        for sid, row in review["surfaces"].items():
            for item in ("R2", "R5", "R8"):
                assert again["surfaces"][sid]["marks"][item] == row["marks"][item], (sid, item)
                votes = row["readers"][item]["votes"]
                assert len(votes) == 3 and all(v["why"] != "no mark given" for v in votes), (sid, item)

    def test_the_comparison_re_derives(self):
        again = RR.compare(json.loads((BEFORE / "review.json").read_text(encoding="utf-8")),
                           _load("review.json"), _rows())
        rec = _load("reread.json")
        for key in ("ticks", "items", "flips", "rows", "done_when", "score_histogram"):
            assert again[key] == rec[key], key


class TestTheFrameCensus:
    """F1, F3, F4's completion lines, read off the closing shoot's own frame
    records (tools/uxr3_frame_census.py)."""

    def test_every_frame_carries_the_records(self):
        # the 145 checklist surfaces and UXR-X9's own board, at five resolutions
        fc = _load("frame_census.json")
        assert fc["frames"] == 146 * 5 and fc["frames_without_record"] == []

    def test_uxr_x9_every_verdict_ends_above_the_nameplate(self):
        gaps = _load("frame_census.json")["verdict_gaps"]
        worst = [g for g in gaps if g["surface"] == "diorama_verdict_worst"]
        assert len(worst) == 5, worst
        assert len(gaps) == 6 * 5      # the five tableau boards and the worst case
        assert all(g["gap_px"] >= 0.0 for g in gaps), [g for g in gaps if g["gap_px"] < 0.0]

    def test_f3_no_line_is_cut_at_a_scrolls_edge(self):
        assert _load("frame_census.json")["cut_lines"] == []

    def test_f4_no_grip_or_ornament_sits_on_text_or_a_control(self):
        assert _load("frame_census.json")["grip_overlaps"] == []

    def test_f1_no_centre_tick_sits_on_a_score(self):
        assert _load("frame_census.json")["tick_overlaps"] == []

    def test_f10_the_rails_overflow_badge_answers(self):
        rec = _load("probe.json")["shots"]["rail_t20"]
        badge = [c for c in rec["controls"] if c.get("text") == "+24"]
        assert badge and badge[0]["result"] == "VISIBLE", badge
        assert any("24 more notices" in ch for ch in badge[0]["changes"]), badge[0]["changes"]


class TestEveryRowIsFixedOrReHomed:
    def test_a_row_whose_items_all_read_true_is_fixed_in_the_ledger(self):
        for r in _load("reread.json")["rows"]:
            line = _ledger_line(r["id"])
            if r["state"] == "FIXED":
                assert ("| FIXED October 13, 2026 — Pre-Deploy S12 part 1" in line
                        or "| FIXED October 14, 2026 — Pre-Deploy S12 part 2" in line), r["id"]

    def test_a_row_still_crossed_is_re_homed_to_uxr4_with_its_frames_and_reasons(self):
        for r in _load("reread.json")["rows"]:
            if r["state"] != "OPEN":
                continue
            line = _ledger_line(r["id"])
            assert "| OPEN — re-homed to UXR-4 (S15)" in line, r["id"]
            assert "still reads ✗ on:" in line and "docs/audits/uxr3_s12b/frames/" in line, r["id"]
            for pair in r["still"]:
                assert pair in line, (r["id"], pair)

    def test_every_cited_frame_is_committed(self):
        for doc in (WRITE_UP, "docs/BUG_FIXES.md"):
            text = (REPO / doc).read_text(encoding="utf-8")
            for path in set(re.findall(r"`(docs/audits/uxr3_s12b/frames/[^`]+\.jpg)`", text)):
                assert (REPO / path).is_file(), (doc, path)

    def test_each_cross_of_the_reread_is_a_rows_or_a_new_rows(self, review):
        rec = _load("reread.json")
        still = {s for r in rec["rows"] if r["state"] == "OPEN" for s in r["still"]}
        new_path = REC / "new_rows.json"
        new = json.loads(new_path.read_text(encoding="utf-8")) if new_path.is_file() else []
        filed = {f"{sid} {item}" for r in new for sid in r["surfaces"] for item in r["items"]}
        for sid, row in review["surfaces"].items():
            for item in ITEMS:
                if not row["marks"][item]["pass"]:
                    assert f"{sid} {item}" in still | filed, (sid, item)
