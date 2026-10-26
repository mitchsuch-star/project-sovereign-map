"""Pre-Deploy S15's head (October 25, 2026) — UXR3-41's two boards re-staged.

`docs/BUG_FIXES.md` UXR3-41 / `docs/UX_UI_REVIEW_PLAN.md` §UXR-4: the closing
re-read of S12 part 2 read `ledger_mission_transit_forces` and
`ledger_mission_starved_forces` ✗ on R2 because the boards NEVER STAGED their
subject — both payloads carried `paused: false`, so the client's paused branch
(`strategic_ledger.gd` `_cabinet_block`: the warning colour, no Recall) never
ran. The transit board's proposal went to Sweden, whom the backend's own gate
refuses (−60 where Open Borders needs −20), so Talleyrand never left; the
starved board's DP write before the end turn was refilled by the turn's own
regeneration (`diplomacy._process_dp_regen`, step 1) before the mission's tick
(step 2) read it.

The fix is in the staging (`tools/iq10_capture_payloads.py` `cap_missions`):
the letter goes to Prussia (−10, the gate passed); the shortfall is written
AFTER the refill for that one turn; and each capture ASSERTS `paused: true`
with its reason before it records, so the board cannot be shot unstaged again.
The facts the capture recorded are committed beside the frames
(`docs/audits/uxr4_s15/uxr3_41_restage_facts.json`) and pinned here; the
frames themselves are for the user's eyes at their monitor.
"""
from __future__ import annotations

import json
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "iq10_capture_payloads.py"
FACTS = REPO / "docs" / "audits" / "uxr4_s15" / "uxr3_41_restage_facts.json"


class TestUXR3_41TheRestage:
    def test_a_the_transit_letter_goes_to_a_court_the_gate_passes(self):
        src = TOOL.read_text(encoding="utf-8")
        assert 'iq4._send_http(c, "propose open borders with Prussia")' in src
        assert 'propose open borders with Sweden' not in src

    def test_b_the_starved_shortfall_is_written_after_the_refill(self):
        src = TOOL.read_text(encoding="utf-8")
        body = src[src.index("# Starved: the mission paused for want of DP."):
                   src.index('record("ledger_mission_starved"')]
        assert "_regen = _dip._process_dp_regen" in body
        assert re.search(r"def _regen_then_starve\(w\):\s*\n\s*_regen\(w\)\s*\n\s*w\.diplomatic_points = 0", body)
        assert "_dip._process_dp_regen = _regen_then_starve" in body
        assert "finally:" in body and "_dip._process_dp_regen = _regen" in body

    def test_c_each_capture_asserts_the_board_is_staged_before_it_records(self):
        src = TOOL.read_text(encoding="utf-8")
        transit = src[src.index("# Transit: he carries a proposal"):src.index('record("ledger_mission_transit"')]
        starved = src[src.index("# Starved: the mission paused for want of DP."):
                      src.index('record("ledger_mission_starved"')]
        assert 'assert _transit_facts.get("paused") is True and _transit_facts.get("pause_reason") == "transit"' in transit
        assert 'assert _starved_facts.get("paused") is True and _starved_facts.get("pause_reason") == "starved"' in starved

    def test_d_the_recorded_facts_read_paused_with_their_reason(self):
        facts = json.loads(FACTS.read_text(encoding="utf-8"))
        boards = facts["boards"]
        transit = boards["ledger_mission_transit"]["facts"]
        starved = boards["ledger_mission_starved"]["facts"]
        assert transit["cabinet"]["paused"] is True
        assert transit["cabinet"]["pause_reason"] == "transit"
        assert transit["cabinet"]["recall_command"] == "", "no Recall while he carries a letter"
        assert transit["talleyrand_state"] == "IN_TRANSIT"
        assert "Prussian court" in transit["send_message"]
        assert starved["cabinet"]["paused"] is True
        assert starved["cabinet"]["pause_reason"] == "starved"
        assert starved["cabinet"]["remaining_note"].startswith("paused: 2 DP needed")
        assert "collapses in 2 turns" in starved["cabinet"]["remaining_note"]

    def test_e_the_after_frames_show_the_paused_block_in_the_first_screenful(self):
        """The re-shot frames (the IQ-10 harness, --physical, 1920×1080 and
        5120×1440) and their records: the Cabinet block's paused line is among
        the whole lines inside the window, and the transit board carries no
        Recall. The frames are for the user's eyes; the record is the pin."""
        index = json.loads((REPO / "docs" / "audits" / "uxr4_s15" / "index.json").read_text(encoding="utf-8"))
        rows = {(f["id"], f["resolution"]): f for f in index["frames"]}
        for board, needle, recall in (
                ("ledger_mission_transit_forces", "paused: he is carrying your proposal", False),
                ("ledger_mission_starved_forces", "paused: 2 DP needed", True)):
            for res in ("1920x1080", "5120x1440"):
                f = rows[(board, res)]
                assert f["rows"] == ["UXR3-41"]
                assert (REPO / f["after"]).is_file(), f["after"]
                assert f["before"] and (REPO / f["before"]).is_file()
                assert not f["errors"]
                seen = "\n".join(str(x.get("seen") if isinstance(x, dict) else x) for x in f["seen_text"])
                assert "THE CABINET" in seen and needle in seen, (board, res)
                assert ("[Recall]" in seen) is recall, (board, res)
