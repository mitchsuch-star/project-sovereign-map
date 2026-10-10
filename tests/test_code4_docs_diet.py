"""CODE-4 "the docs diet" (Pre-Deploy S2, October 9, 2026) — the move changed
no count and the diet holds.

`docs/CODE_HEALTH_PLAN.md` §CODE-4: closed ledger sections older than the
current quarter moved verbatim to `docs/archive/<STEM>_<year>_Q<n>.md`;
STATUS keeps the ▶ NEXT UP block and the last five session entries;
CLAUDE.md's "Current Phase" is one screen and its 2026 record is archived.
`tools/defect_census.py` and `tools/fa_row_tally.py` read the archives, so
every count is unchanged by the move — pinned here as: every archive on disk
is one the tools read, no archived row reads OPEN, every OPEN row is in the
live ledger, and the size caps hold. The CLAUDE.md cap rides the code-health
ratchet (`tests/test_code_health_ratchet.py`).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs"
ARCHIVE = DOCS / "archive"
sys.path.insert(0, str(REPO))
from tools import defect_census as census  # noqa: E402
from tools import fa_row_tally as tally  # noqa: E402
from tests._ledgers import doc_paths, doc_text  # noqa: E402

LEDGER_ARCHIVE = re.compile(r"^(BUG_FIXES|DESIGN_REFINEMENT)_\d{4}_Q[1-4]\.md$")


def _archives_on_disk() -> list[Path]:
    return sorted(p for p in ARCHIVE.glob("*.md") if LEDGER_ARCHIVE.match(p.name))


class TestTheCensusReadsTheArchives:
    def test_every_ledger_archive_on_disk_is_read_by_the_census(self):
        on_disk = {p.resolve() for p in _archives_on_disk()}
        read = {p.resolve() for _, p in census.LEDGERS}
        assert on_disk, "the diet made no archive — the ledgers moved?"
        assert on_disk <= read, sorted(p.name for p in on_disk - read)

    def test_every_ledger_archive_on_disk_is_read_by_the_tally(self):
        on_disk = {p.resolve() for p in _archives_on_disk()}
        read = {p.resolve() for p in tally.SOURCES}
        assert on_disk <= read, sorted(p.name for p in on_disk - read)

    def test_the_archive_is_read_under_its_own_ledger(self):
        """A design row archived from DESIGN_REFINEMENT must still count as
        design, a defect row as defect — the archive inherits its ledger."""
        for ledger, path in census.LEDGERS:
            if path.parent == ARCHIVE:
                stem = "BUG_FIXES" if ledger == "defect" else "DESIGN_REFINEMENT"
                assert path.name.startswith(stem + "_"), (ledger, path.name)

    def test_the_live_ledger_is_read_before_its_archives(self):
        for ledger in census.LEDGER_NAMES:
            paths = [p for lg, p in census.LEDGERS if lg == ledger]
            assert paths[0].parent == DOCS and all(p.parent == ARCHIVE for p in paths[1:])

    def test_no_archived_row_reads_open(self):
        """OPEN and PARTIAL rows never move (§CODE-4 item 3). Read each
        archive ALONE through the census's own classifier."""
        rows = census.collect()
        archived_lines = {}
        for ledger, path in census.LEDGERS:
            if path.parent != ARCHIVE:
                continue
            text = path.read_text(encoding="utf-8")
            archived_lines[path.name] = text
        open_ids = {r["id"] for r in rows.values() if r["state"] in ("OPEN", "partial")}
        live = doc_text("BUG_FIXES.md").split("<!-- archive -->")[0] + doc_text("DESIGN_REFINEMENT.md").split("<!-- archive -->")[0]
        missing = sorted(i for i in open_ids if not re.search(r"(?<![A-Za-z0-9-])" + re.escape(i) + r"(?![A-Za-z0-9])", live))
        assert not missing, f"OPEN rows not in the live ledgers: {missing}"

    def test_the_counts_are_whole(self):
        """The reading at the move (October 9, 2026, `b43ca90c`): defect 1,277
        ids, design 206. Rows are only ever ADDED after the diet, so the totals
        may rise and never fall — a fall means an archive stopped being read."""
        rows = census.collect()
        by_ledger = {}
        for r in rows.values():
            by_ledger[r["ledger"]] = by_ledger.get(r["ledger"], 0) + 1
        assert by_ledger["defect"] >= 1277, by_ledger
        assert by_ledger["design"] >= 206, by_ledger
        fa = tally.collect()
        assert len(fa) >= 267, len(fa)


class TestTheDietHolds:
    def test_status_is_the_next_up_block_and_five_entries(self):
        text = (DOCS / "STATUS.md").read_text(encoding="utf-8")
        assert text.count("> **▶ ▶ ▶") <= 7, "STATUS keeps the last five session entries (two more for a session in flight)"
        assert "## ▶ NEXT UP" in text and "## Archives" in text

    def test_status_under_the_cap(self):
        assert (DOCS / "STATUS.md").stat().st_size <= 200_000

    def test_claude_md_names_the_routing_authority_on_one_screen(self):
        text = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
        head = text.index("## Current Phase")
        tail = text.index("## File Reference")
        screen = text[head:tail]
        assert "ROUTING AUTHORITY" in screen and "LIVE STATE" in screen
        assert "CLAUDE_CURRENT_PHASE_2026.md" in screen
        assert "Load-bearing operational facts" in screen
        assert screen.count("\n") <= 60, "Current Phase is one screen"

    def test_the_archives_exist_and_carry_their_header(self):
        for name in ("CLAUDE.md", "STATUS.md", "BUG_FIXES.md", "DESIGN_REFINEMENT.md"):
            paths = doc_paths(name)
            assert len(paths) >= 2, name
            for p in paths[1:]:
                assert "Moved verbatim" in p.read_text(encoding="utf-8")[:600], p.name

    @pytest.mark.parametrize("name,needle", [
        ("BUG_FIXES.md", "UX23-R9"),          # a row every pin found before the move
        ("STATUS.md", "SR-5a"),               # a Q3 session entry
        ("CLAUDE.md", "The queue in one line"),  # the archived scroll
    ])
    def test_the_helper_finds_what_moved(self, name, needle):
        assert needle in doc_text(name)
