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
# them (the Score Finish residue's SF-RR slices are S14's). S13c (row CC "Click
# & Command") and S13d (row PC, the peace report's fixes) joined the table on
# October 15, 2026; S13e (row PC part 2, the peace research's defects) on October 16.
# S13f (AO "the army order", from the command-feel review's CF rows) joined on
# October 17, 2026. Row AU (authority as a currency — the seven slices AU-1 …
# AU-4, all before S15 by the user's ruling of November 3, 2026) joined with its
# gate; AU-1's two courts' rows are homed to the AU-4 slice (the courts' flip).
# Row BA (the battle in acts — BA-1 … BA-3, all before S15 by the user's ruling
# of November 14, 2026, "Before the deploy") joined with its gate; WS-16 (the
# reload's other dice) was homed to BA-3 and closed there. BA-4 ("the roads
# and the fog") joined November 15, 2026 with the user's approval of BA-3's
# plan: every BA2 row that moves a measured world-line lands there, with one
# re-read of the gate, still before S15. Row IC's Sessions 2-4 (IC-7 ... IC-15, all
# before S15 by the design's D23 and the user's no-cuts rule) joined November 20,
# 2026 with the review of "on his own" (`docs/INDEPENDENT_COMMAND_SPEC.md` v6 §15;
# `PRE_DEPLOY_PLAN.md` §2 row IC): the typed road's rows moved there from Session H.
# Row FR (the five open rows, Sessions FR-1 and FR-2, before row TU and S15 by the
# user's word of November 23, 2026) joined that day: the five moved there from Session H.
SESSION = re.compile(r"\bS13[b-f]\b|\bS14[b-i]?\b|\bSF-RR[1-7]\b|\bUXR-4\b|\bS15\b|\bAU-[1-4][abc]?\b"
                     r"|\bBA-[1-4]\b|\bIC-(?:[7-9]|1[0-5])\b|\bFR-[12]\b"
                     # row FUN (November 25, 2026 — the user's "Yes, start FUN-1"): its five sessions
                     r"|\bFUN-[1-5]b?\b")


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
        for row in ("| S14b ", "| S14c ", "| S14d ", "| S14e ", "| S14f ", "| S14g ", "| S14h "):
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
