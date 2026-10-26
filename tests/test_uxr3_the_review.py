"""UXR-3 — the look-and-feel review's reading, pinned on its committed records
(Pre-Deploy S11, October 13, 2026).

The review read every surface of `docs/UX_CHECKLIST_V1.json` (frozen in Part 1,
`tests/test_uxr3_checklist_frozen.py`) against eight items. Its evidence is
committed under `docs/audits/uxr3/`:

    readability.json      R1   tools/uxr0_readability_report.py over the shoot
    contrast.json         R3   tools/uxr2b_contrast_report.py, High contrast OFF
    contrast_hc_on.json        the same, High contrast ON (recorded beside, never scored)
    consistency.json      R4   tools/uxr3_consistency_census.py
    fit.json              R7   tools/uxr3_fit_report.py
    probe.json            R5 / R6   tools/uxr3_action_probe.py (the driven record)
    modec.json                 the Mode C session (the live-backend record R6 may cite)
    live_citations.json        what each cited HANDOFF / NOT PRESSED road rests on
    instrument_marks.json      tools/uxr3_review.py marks
    panel_raw/reader_{1,2,3}/  the three blind readers' raw marks, group by group
    review.json                tools/uxr3_review.py aggregate: 145 surfaces x 8 items

These pins hold the reading to its records: the instruments' marks re-derive
from the records the same way, the readers' marks aggregate two of three the
same way, the scores and the worst five are what `review.json` says, and every
✗ is filed as a row of `docs/BUG_FIXES.md` §UXR-3 — the review, owned by S12.
They run on the committed JSON, never on Godot.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

import pytest

from tests._ledgers import doc_text  # CODE-4: the ledger plus its archives

REPO = pathlib.Path(__file__).resolve().parents[1]
RECORDS = REPO / "docs" / "audits" / "uxr3"
CHECKLIST = REPO / "docs" / "UX_CHECKLIST_V1.json"
TOOLS = REPO / "tools"
sys.path.insert(0, str(TOOLS))

import uxr3_review as RV  # noqa: E402

ITEMS = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
# The tree the reading read: the Part 1 commit (the checklist's own).
READ_TREE = "603d983f"


def _load(name: str) -> dict:
    path = RECORDS / name
    assert path.is_file(), f"the committed record is missing: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def review() -> dict:
    return _load("review.json")


@pytest.fixture(scope="module")
def checklist() -> dict:
    return json.loads(CHECKLIST.read_text(encoding="utf-8"))


class TestTheRecordsAreTheTreeRead:
    def test_every_record_is_committed(self):
        for name in ("readability.json", "contrast.json", "contrast_hc_on.json", "consistency.json",
                     "fit.json", "probe.json", "modec.json", "live_citations.json",
                     "instrument_marks.json", "review.json"):
            assert (RECORDS / name).is_file(), name

    def test_the_shoot_and_the_probe_read_the_frozen_tree(self):
        for name in ("readability.json", "contrast.json", "fit.json", "probe.json"):
            assert _load(name)["client_commit"].startswith(READ_TREE), name
        assert _load("contrast.json")["high_contrast"] is False
        assert _load("contrast_hc_on.json")["high_contrast"] is True

    def test_every_frame_was_shot_at_the_derived_scale(self):
        assert _load("readability.json")["physical_scale"] == "auto"
        assert _load("fit.json")["physical_scale"] == "auto"


class TestTheReadingIsWhole:
    def test_every_surface_in_the_order_has_eight_marks(self, review, checklist):
        ids = [s["id"] for g in checklist["groups"] for s in g["surfaces"]]
        assert list(review["surfaces"]) == ids
        for sid, row in review["surfaces"].items():
            assert set(row["marks"]) == set(ITEMS), sid
            assert row["score"] == sum(1 for i in ITEMS if row["marks"][i]["pass"]), sid

    def test_the_instrument_marks_re_derive_from_the_records(self, review):
        again = RV.instrument_marks(RECORDS)
        for sid, row in review["surfaces"].items():
            for item in ("R1", "R3", "R4", "R6", "R7"):
                assert row["marks"][item]["pass"] == again[sid][item]["pass"], (sid, item)

    def test_the_readers_aggregate_two_of_three(self, review):
        again = RV.aggregate(RECORDS, RECORDS)
        for sid, row in review["surfaces"].items():
            for item in ("R2", "R5", "R8"):
                assert again["surfaces"][sid]["marks"][item] == row["marks"][item], (sid, item)
                spread = row["readers"][item]["spread"]
                assert spread in ("3–0", "2–1"), (sid, item, spread)

    def test_every_reader_marked_every_surface(self, review):
        for sid, row in review["surfaces"].items():
            for item in ("R2", "R5", "R8"):
                votes = row["readers"][item]["votes"]
                assert len(votes) == 3, (sid, item)
                assert all(v["why"] != "no mark given" for v in votes), (sid, item)

    def test_the_worst_five_are_the_lowest_scores_in_the_review_order(self, review):
        order = list(review["surfaces"])
        ranked = sorted(order, key=lambda k: (review["surfaces"][k]["score"], order.index(k)))
        assert review["worst_five"] == ranked[:5]


class TestEveryFailIsFiled:
    @pytest.fixture(scope="class")
    def section(self) -> str:
        text = doc_text("BUG_FIXES.md")
        m = re.search(r"(?ms)^## UXR-3 — the review.*?(?=^## |\Z)", text)
        assert m, "BUG_FIXES.md has no '## UXR-3 — the review' section"
        return m.group(0)

    def test_every_fail_names_its_surface_and_item_in_a_row(self, review, section):
        rows = _load("bug_rows.json")
        filed = {(sid, item) for r in rows for sid in r["surfaces"] for item in r["items"]}
        for sid, row in review["surfaces"].items():
            for item in ITEMS:
                if not row["marks"][item]["pass"]:
                    assert (sid, item) in filed, (sid, item)
        for r in rows:
            assert f"**{r['id']}**" in section, r["id"]
            for sid in r["surfaces"]:
                assert f"`{sid}`" in section, (r["id"], sid)

    def test_every_row_is_tagged_for_s12(self, section):
        """Filed OPEN for S12; S12 part 1 (October 13, 2026) flips a row to
        FIXED only with its re-read (`docs/audits/uxr3_s12/reread.json`): every
        (surface, item) it names reads ✓ against the same frozen checklist.
        S12 part 2's closing re-read (`docs/audits/uxr3_s12b/reread.json`,
        October 14, 2026) flips the rest to FIXED the same way, or re-homes a
        row still ✗ to UXR-4 (S15) — never closes one without its re-read."""
        rows = [ln for ln in section.split("\n") if re.match(r"\| \*\*UXR3-\d+\*\*", ln)]
        assert len(rows) == len(_load("bug_rows.json"))

        def _states(rel: str) -> dict:
            path = REPO / "docs" / "audits" / rel / "reread.json"
            rec = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
            return {r["id"]: r["state"] for r in rec.get("rows", [])}

        state, closing = _states("uxr3_s12"), _states("uxr3_s12b")
        for ln in rows:
            assert "⟨SF step=pre-deploy S12 · UXR-3 " in ln and "pillar=ui_ux⟩" in ln, ln[:80]
            rid = re.match(r"\| \*\*(UXR3-\d+)\*\*", ln).group(1)
            if "| FIXED October 13, 2026 — Pre-Deploy S12 part 1" in ln:
                assert state.get(rid) == "FIXED", (rid, "flipped without its re-read")
            elif "| FIXED October 14, 2026 — Pre-Deploy S12 part 2" in ln:
                assert closing.get(rid) == "FIXED", (rid, "flipped without the closing re-read")
            elif "| OPEN — re-homed to UXR-4 (S15)" in ln:
                assert closing.get(rid) == "OPEN", (rid, "re-homed, but the closing re-read reads it FIXED")
            elif "| ✅ FIXED October 25, 2026 — S15 head" in ln:
                # S15's head (October 25, 2026): a row the closing re-read
                # re-homed to UXR-4, its decided fix BUILT and re-shot for the
                # user's eyes (`SYSTEMS_REFERENCE.md` §152.11, `docs/audits/uxr4_s15/`).
                assert closing.get(rid) == "OPEN", (rid, "built at S15's head, but it was never re-homed")
                assert "docs/audits/uxr4_s15/" in ln, rid
            elif "| ✅ CLOSED October 25, 2026 — the walk at UXR-4" in ln:
                # S15 (October 25, 2026): a row the closing re-read re-homed to
                # UXR-4, closed by the walk's mark (delegated to the session) to
                # its own decided fix — never by a re-read.
                assert closing.get(rid) == "OPEN", (rid, "closed by the walk, but it was never re-homed")
                assert "UXR-4" in ln, rid
            else:
                assert "| OPEN — owner S12" in ln, ln[:80]
                assert state.get(rid, "OPEN") == "OPEN", (rid, "the re-read reads it FIXED, the row says OPEN")

    def test_the_rows_found_while_reading_are_owned(self, section):
        """F1 … F11: the readers' notes and the conductor's checks — defects no
        item's mark rests on, filed so none is left unowned. F11 is backend
        COPY, routed to the ending pillar's owner (S14) by the plan."""
        found = {m.group(1): ln for ln in section.split("\n")
                 for m in [re.match(r"\| \*\*(UXR3-F\d+)\*\*", ln)] if m}
        assert sorted(found, key=lambda k: int(k.split("F")[1])) == [f"UXR3-F{i}" for i in range(1, 12)]
        for rid, ln in found.items():
            if rid == "UXR3-F11":
                assert "⟨SF step=pre-deploy S14 · ending copy · pillar=ending⟩" in ln
            else:
                assert "⟨SF step=pre-deploy S12 · UXR-3 " in ln and "pillar=ui_ux⟩" in ln, rid
            assert re.search(r"`docs/audits/uxr3/frames/[^`]+\.jpg`", ln), rid

    def test_every_cited_frame_is_committed(self, section):
        for path in set(re.findall(r"`(docs/audits/uxr3/frames/[^`]+\.jpg)`", section)):
            assert (REPO / path).is_file(), path


class TestTheInstrumentsKeepTheirRails:
    def test_the_probe_never_writes_settings_or_touches_8005(self):
        gd = (TOOLS / "uxr3_action_probe.gd").read_text(encoding="utf-8")
        assert "UiSettings._cfg = ConfigFile.new()" in gd
        assert 'settings_class.set("_persist", false)' in gd
        assert not re.search(r"UiSettings\.set_\w+\(", gd)
        assert 'Utils.backend_url().ends_with(":8005")' in gd
        runner = (TOOLS / "uxr3_action_probe.py").read_text(encoding="utf-8")
        assert 'env["SOVEREIGN_PORT"] = HARNESS_PORT' in runner and 'HARNESS_PORT = "8999"' in runner
        check = (TOOLS / "godot_parse_check.gd").read_text(encoding="utf-8")
        assert '"res://../../tools/uxr3_action_probe.gd"' in check

    def test_the_probe_drags_a_drag_control(self):
        """S12 part 2 (UXR3-74): a visible non-button Control taking the mouse
        whose default cursor is a resize shape is a control of kind `drag`. It
        is pressed as a drag in a fresh instance (a press at its centre, two
        motions of 20 px down and right, a release) and answers VISIBLE when a
        control's rect changed; the record holds it, so the readers see it."""
        gd = (TOOLS / "uxr3_action_probe.gd").read_text(encoding="utf-8")
        assert ("const DRAG_CURSORS := [Control.CURSOR_FDIAGSIZE, Control.CURSOR_BDIAGSIZE,\n"
                "\t\tControl.CURSOR_HSIZE, Control.CURSOR_VSIZE]") in gd
        assert "const DRAG_STEP := Vector2(20.0, 20.0)" in gd
        enum = re.search(r"(?ms)^func _enumerate\(.*?(?=^func )", gd).group(0)
        assert "ctrl.mouse_default_cursor_shape in DRAG_CURSORS" in enum
        assert "ctrl.mouse_filter != Control.MOUSE_FILTER_IGNORE" in enum
        assert 'base["kind"] = "drag"' in enum
        # after the button and pointer branches: a button is never a drag
        assert enum.index('base["kind"] = "button"') < enum.index('base["kind"] = "drag"')
        press = re.search(r"(?ms)^func _press_and_read\(.*?(?=^func )", gd).group(0)
        for step in ("_mouse(from, true)", "_motion(from + DRAG_STEP, from)",
                     "_motion(from + 2.0 * DRAG_STEP, from + DRAG_STEP)",
                     "_mouse(from + 2.0 * DRAG_STEP, false)"):
            assert step in press, step
        assert press.index("_mouse(from, true)") < press.index("_mouse(from + 2.0 * DRAG_STEP, false)")
        # VISIBLE for a drag iff a rect moved
        assert 'if str(k).begins_with("r:"):' in press and "if is_drag:" in press
        verdict = press[press.index("if is_drag:"):]
        assert verdict.index("if moved:") < verdict.index('out["result"] = "VISIBLE"')

    def test_the_capture_harness_records_what_r7_and_r4_read(self):
        gd = (TOOLS / "iq10_surface_screenshot.gd").read_text(encoding="utf-8")
        for field in ('frame["truncated_text"] = _truncated_text()', 'frame["buttons"] = _visible_buttons()',
                      "var fit := _under_modal(view)", 'frame["files"] = _visible_files()',
                      'entry["rect_raw"] = [r.position.x, r.position.y, r.size.x, r.size.y]'):
            assert field in gd, field

    def test_the_census_holds_the_checklists_dim_class(self):
        import uxr3_consistency_census as C
        assert C.UI_TEXT_DIM == (0.75, 0.72, 0.65)
        assert C.is_dim((0.4, 0.4, 0.4392)) and C.is_dim((0.502, 0.502, 0.502))
        assert not C.is_dim((0.93, 0.93, 0.93))          # bright text is not dim
        assert not C.is_dim((0.85, 0.75, 0.55))          # gold is coloured, not grey
        assert C.on_ladder((0.6275, 0.6275, 0.6588)) and not C.on_ladder((0.7, 0.7, 0.75))
