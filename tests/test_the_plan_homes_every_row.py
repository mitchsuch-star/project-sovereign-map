"""The plan homes every row before the deploy (the user's delegation, October
14, 2026: "assure the plan has all errors fixed in coming sessions and any
similar errors they find while working").

`docs/PRE_DEPLOY_PLAN.md` §2 states the guarantee: every open row has a
session; the sibling sweep files what a fix finds; the re-measure's rows
become S14f; the release build waits for 0 open defect rows. This pin holds
the first clause on the ledgers themselves: every OPEN row of
`docs/BUG_FIXES.md` and `docs/DESIGN_REFINEMENT.md` (read by the ONE census,
`tools/defect_census.py`, archives included) names a session of the plan in
its owner cell — never a row after the deploy, never "later".
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools import defect_census as census  # noqa: E402

# The sessions left in the plan's §2 table, and the slice names that live in
# them (the Score Finish residue's SF-RR slices are S14's).
SESSION = re.compile(r"\bS13b\b|\bS14[b-f]?\b|\bSF-RR[1-7]\b|\bUXR-4\b|\bS15\b")


def _open_rows():
    return [r for r in census.collect().values() if r.get("state") in ("OPEN", "partial")]


class TestThePlanHomesEveryRow:
    def test_every_open_row_names_a_session_of_the_plan(self):
        unhomed = [r["id"] for r in _open_rows()
                   if not SESSION.search(str(r.get("owner") or "") + " " + str(r.get("finding") or ""))]
        assert unhomed == [], f"open rows with no session of PRE_DEPLOY_PLAN §2: {unhomed}"

    def test_no_open_row_is_homed_after_the_deploy(self):
        after = [r["id"] for r in _open_rows()
                 if re.search(r"ROADMAP (row )?1[3-9]\b|after the deploy|post-deploy", str(r.get("owner") or ""))
                 and not SESSION.search(str(r.get("owner") or ""))]
        assert after == [], after

    def test_the_plan_states_the_guarantee(self):
        plan = (REPO / "docs" / "PRE_DEPLOY_PLAN.md").read_text(encoding="utf-8")
        assert "**Every error is fixed before the deploy**" in plan
        assert "**The sibling sweep**" in plan
        assert "the release build waits for 0 OPEN defect rows" in plan
        claude = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
        assert "10. **Sibling sweep**" in claude

    def test_the_items_brought_before_the_deploy_have_their_rows(self):
        """The user, October 14, 2026: "add events to plan as well … i agree with
        rest … make sure everything reflects future plans"."""
        plan = (REPO / "docs" / "PRE_DEPLOY_PLAN.md").read_text(encoding="utf-8")
        for row in ("| S14b ", "| S14c ", "| S14d ", "| S14e ", "| S14f "):
            assert row in plan, row
        assert "**Code signing**" in plan
        roadmap = (REPO / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
        assert "## ▶ WHERE THE FUTURE WORK LIVES" in roadmap
        assert "Pre-Deploy S14c" in roadmap and "Pre-Deploy S14b" in roadmap

    def test_the_dd_b_design_rows_are_ruled_and_their_builds_open(self):
        rows = census.collect()
        for n in range(1, 10):
            assert rows[f"DDB-D{n}"]["state"] == "closed", f"DDB-D{n} is ruled"
        # A build is tracked as a defect row: OPEN until it lands, then closed by
        # its FIXED / BUILT line — never disposed, never dropped.
        for rid in [f"DDB-R{n}" for n in range(1, 8)] + [f"DDB-X{n}" for n in range(1, 7)] + ["SFR-B3"]:
            assert rid in rows and rows[rid]["state"] in ("OPEN", "partial", "closed"), rid
            if rows[rid]["state"] != "closed":
                assert SESSION.search(str(rows[rid].get("owner") or "") + " " + str(rows[rid].get("finding") or "")), rid
