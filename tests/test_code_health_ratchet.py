"""The code-health ratchet (`docs/CODE_HEALTH_PLAN.md` §The ratchet pin;
landed with CODE-1 batch 1, Pre-Deploy S2, October 9, 2026).

Reads `tools/_code_health_census.py`'s own reading — the instrument, not a
grep, so a text mutation cannot satisfy it — and caps four numbers at the
reading the slice left. Each cap may only be LOWERED (edit the constant
when a slice brings the count down; a slice that raises one fails here).
The caps are the plan's gains; this is what keeps them from leaking back.

    levers               CODE-1 retires them in batches; done under 40
    functions over 500   CODE-2 splits them; done when the eight named are staged
    silent handlers      CODE-3 makes every broad except speak; done under 60
    CLAUDE.md bytes      CODE-4's diet; the cap is the dieted size
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from tools import _code_health_census as census_tool  # noqa: E402

# ── the caps: the reading after CODE-1 batch 1 (October 9, 2026); lower-only ──
LEVERS_CAP = 645
FUNCTIONS_OVER_500_CAP = 34
SILENT_HANDLERS_CAP = 367
CLAUDE_MD_BYTES_CAP = 62_000
STATUS_MD_BYTES_CAP = 200_000


@pytest.fixture(scope="module")
def reading():
    return census_tool.census()


class TestTheRatchet:
    def test_levers_do_not_grow(self, reading):
        n = len(reading["levers"])
        assert n <= LEVERS_CAP, (
            f"{n} module-level flip levers, cap {LEVERS_CAP}: a new lever lands "
            "with its attribution and is retired the session after (CODE-1); "
            "retire one before adding one, or lower nothing")

    def test_functions_over_500_lines_do_not_grow(self, reading):
        n = sum(1 for length, _, _ in reading["functions"] if length > 500)
        assert n <= FUNCTIONS_OVER_500_CAP, (
            f"{n} functions over 500 lines, cap {FUNCTIONS_OVER_500_CAP}: "
            + ", ".join(name for length, _, name in reading["functions"] if length > 500))

    def test_silent_handlers_do_not_grow(self, reading):
        n = reading["except"]["silent"]
        assert n <= SILENT_HANDLERS_CAP, (
            f"{n} `except Exception` handlers that neither log nor re-raise, "
            f"cap {SILENT_HANDLERS_CAP} (CODE-3): " + str(reading["silent_by_file"].most_common(5)))

    def test_claude_md_stays_on_its_diet(self, reading):
        assert reading["claude_md_bytes"] <= CLAUDE_MD_BYTES_CAP, (
            f"CLAUDE.md is {reading['claude_md_bytes']} bytes, cap {CLAUDE_MD_BYTES_CAP}: "
            "history goes to docs/archive/, the Current Phase stays one screen (CODE-4)")

    def test_status_md_stays_on_its_diet(self, reading):
        assert reading["status_md_bytes"] <= STATUS_MD_BYTES_CAP


class TestTheCapsAreRealReadings:
    """A cap set above the reading is a pin that cannot fail; each cap must
    sit within a slice's reach of the number it guards."""

    def test_each_cap_is_near_its_reading(self, reading):
        levers = len(reading["levers"])
        funcs = sum(1 for length, _, _ in reading["functions"] if length > 500)
        silent = reading["except"]["silent"]
        assert LEVERS_CAP - levers <= 10, (levers, LEVERS_CAP)
        assert FUNCTIONS_OVER_500_CAP - funcs <= 2, (funcs, FUNCTIONS_OVER_500_CAP)
        assert SILENT_HANDLERS_CAP - silent <= 10, (silent, SILENT_HANDLERS_CAP)
        assert CLAUDE_MD_BYTES_CAP - reading["claude_md_bytes"] <= 8_000


class TestTheInstrumentSeesWhatItCaps:
    """Sensitivity: the census must count the things the caps name."""

    def test_the_lever_regex_reads_a_lever(self):
        assert census_tool.LEVER_RE.search("THE_RULE_IS_SO = True\n")
        assert census_tool.LEVER_RE.search("SOME_FLAG: bool = False  # why\n")
        assert not census_tool.LEVER_RE.search("MAX_SAIL = 100\n")

    def test_the_reading_carries_every_key_the_caps_read(self, reading):
        for key in ("functions", "levers", "except", "silent_by_file",
                    "claude_md_bytes", "status_md_bytes"):
            assert key in reading, key
        assert set(reading["except"]) <= {"silent", "logs", "reraise"}
