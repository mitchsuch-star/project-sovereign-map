"""UXR-3 fixes — the re-read, pinned on its committed records (Pre-Deploy S12
part 1, October 13, 2026).

Part 1 fixed the review's rows by class (the never-shot popups, R3 by token,
R5 / R6's inert controls, R4 by file), then re-read every surface against the
SAME frozen checklist (`docs/UX_CHECKLIST_V1.json`) with the SAME tools:

    a whole-manifest shoot on the part-4 commit, the scenes part 5a touched
    re-shot on its commit and merged (tools/uxr3_merge_index.py); the probe
    over every surface, the 12 popups whose links 5a exposed re-probed; the
    census, the fit report, the contrast report; three FRESH blind readers for
    R2 / R5 / R8; the assembler (tools/uxr3_review.py); the comparison
    (tools/uxr3_reread.py).

The records are `docs/audits/uxr3_s12/`; the write-up
`docs/audits/UXR3_REREAD_2026_10_13.md`. These pins hold the re-read to its
records the way `tests/test_uxr3_the_review.py` holds the review to its: on
the committed JSON, never on Godot.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

from tests._ledgers import doc_text  # CODE-4: the ledger plus its archives

REPO = pathlib.Path(__file__).resolve().parents[1]
REC = REPO / "docs" / "audits" / "uxr3_s12"
BEFORE = REPO / "docs" / "audits" / "uxr3"
CHECKLIST = REPO / "docs" / "UX_CHECKLIST_V1.json"
sys.path.insert(0, str(REPO / "tools"))

import uxr3_reread as RR  # noqa: E402
import uxr3_review as RV  # noqa: E402

ITEMS = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
SHOT_TREE = "337b8621"        # part 4: the whole-manifest shoot and the probe
FIX_TREE = "46f668ef"         # part 5a: the re-shoot and the re-probe
# the states S12 part 2's closing re-read moves a row on to
LATER_STATES = ("FIXED October 14, 2026 — Pre-Deploy S12 part 2", "OPEN — re-homed to UXR-4 (S15)",
                # S15's head (October 25, 2026): the re-homed marks' decided
                # fixes were BUILT and re-shot for the user's eyes; their rows
                # read FIXED at S15's head (`SYSTEMS_REFERENCE.md` §152.11).
                "✅ FIXED October 25, 2026 — S15 head")


def _load(name: str) -> dict:
    path = REC / name
    assert path.is_file(), f"the committed record is missing: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def review() -> dict:
    return _load("review.json")


class TestTheRecordsAreTheTreesRead:
    def test_every_record_is_committed(self):
        for name in ("readability.json", "contrast.json", "consistency.json", "fit.json", "probe.json",
                     "live_citations.json", "instrument_marks.json", "review.json", "reread.json"):
            assert (REC / name).is_file(), name
        for n in (1, 2, 3):
            assert len(list((REC / "panel_raw" / f"reader_{n}").glob("group_*.json"))) == 10, n

    def test_the_shoot_and_the_probe_read_the_committed_trees(self):
        for name in ("readability.json", "contrast.json", "fit.json"):
            assert _load(name)["client_commit"].startswith(SHOT_TREE), name
        probe = _load("probe.json")
        assert probe["client_commit"].startswith(SHOT_TREE)
        assert [r["client_commit"] for r in probe["reprobes"]] == [FIX_TREE]
        assert _load("contrast.json")["high_contrast"] is False
        assert _load("readability.json")["physical_scale"] == "auto"

    def test_the_same_frozen_checklist(self, review):
        assert review["checklist"] == "docs/UX_CHECKLIST_V1.json"
        ids = [s["id"] for g in json.loads(CHECKLIST.read_text(encoding="utf-8"))["groups"]
               for s in g["surfaces"]]
        assert list(review["surfaces"]) == ids


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
        rows = json.loads((BEFORE / "bug_rows.json").read_text(encoding="utf-8"))
        again = RR.compare(json.loads((BEFORE / "review.json").read_text(encoding="utf-8")),
                           _load("review.json"), rows)
        rec = _load("reread.json")
        for key in ("ticks", "items", "flips", "rows", "done_when", "score_histogram"):
            assert again[key] == rec[key], key


class TestTheClassesHeld:
    """What part 1's classes promised, read off the re-read's own records."""

    def test_r1_r3_r4_r7_hold_on_every_surface(self, review):
        for item in ("R1", "R3", "R4", "R7"):
            fails = [sid for sid, row in review["surfaces"].items() if not row["marks"][item]["pass"]]
            assert fails == [], (item, fails)

    def test_no_surface_fails_r5_on_a_silent_control(self, review):
        auto = [sid for sid, row in review["surfaces"].items() if row["marks"]["R5"].get("auto")]
        assert auto == [], auto

    def test_the_three_popups_are_read(self, review):
        for sid in ("objection_dialog", "capture_choice", "talleyrand_objection"):
            assert review["surfaces"][sid]["shot"] == sid
            for item in ("R1", "R3", "R4", "R6", "R7"):
                assert review["surfaces"][sid]["marks"][item]["pass"], (sid, item)


class TestEveryCrossOfTheReReadIsFiled:
    def test_each_cross_is_an_open_rows_or_a_new_rows(self, review):
        rec = _load("reread.json")
        still = {s for r in rec["rows"] if r["state"] == "OPEN" for s in r["still"]}
        new = json.loads((REC / "new_rows.json").read_text(encoding="utf-8"))
        filed = {f"{sid} {item}" for r in new for sid in r["surfaces"] for item in r["items"]}
        for sid, row in review["surfaces"].items():
            for item in ITEMS:
                if not row["marks"][item]["pass"]:
                    assert f"{sid} {item}" in still | filed, (sid, item)

    def test_the_new_rows_are_in_the_ledger(self):
        """Filed OPEN for S12 part 2; part 2's closing re-read
        (`tests/test_uxr3_s12b_reread.py`) then moves each one on: FIXED by
        part 2, or re-homed to UXR-4 with what still reads ✗."""
        text = doc_text("BUG_FIXES.md")
        for r in json.loads((REC / "new_rows.json").read_text(encoding="utf-8")):
            head = f"| **{r['id']}** | {r['sev']} | "
            assert any(head + state in text for state in LATER_STATES + ("OPEN — owner S12 part 2",)), r["id"]
            for sid in r["surfaces"]:
                assert f"`{sid}`" in text, (r["id"], sid)

    def test_a_flipped_row_is_fixed_in_the_ledger_and_an_open_one_is_not(self):
        text = doc_text("BUG_FIXES.md")
        for r in _load("reread.json")["rows"]:
            line = next(ln for ln in text.splitlines() if ln.startswith(f"| **{r['id']}** |"))
            if r["state"] == "FIXED":
                assert "| FIXED October 13, 2026 — Pre-Deploy S12 part 1" in line, r["id"]
            elif any(f"| {state}" in line for state in LATER_STATES):
                pass   # part 2 moved it on; its own re-read pins the move
            else:
                assert "| OPEN — owner S12" in line and "still reads ✗ on:" in line, r["id"]

    def test_every_cited_frame_is_committed(self):
        import re
        for doc in ("docs/audits/UXR3_REREAD_2026_10_13.md", "docs/BUG_FIXES.md"):
            text = (REPO / doc).read_text(encoding="utf-8")
            for path in set(re.findall(r"`(docs/audits/uxr3_s12/frames/[^`]+\.jpg)`", text)):
                assert (REPO / path).is_file(), (doc, path)
