"""UXR3-F11 — the titled tally past the bar (Pre-Deploy S14b's head, October 21,
2026; `BUG_FIXES.md` §UXR-3 the review).

The imperial-peace end screen read "50 of 45 titled provinces in the Empire and
its satellites": the played Congress board holds 50 titled provinces and GE-V
lowered the bar to 45, so "N of M" printed a numerator above its denominator —
on the end screen (the client's `campaign_end.gd`), the Congress's gate text
(`congress.py`), every Congress line of the rail and the dispatch. One phrasing
now: "43 of 45 titled" short of the bar or on it, "50 titled, 45 needed" past
it; the end screen's line comes from the backend (`titled_line`).
"""
import contextlib
import io
import re
from pathlib import Path

import pytest

from backend.game_logic import congress
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCEN = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json")
_OVER = re.compile(r"\b(\d+) of (\d+)\b")


def _boot() -> WorldState:
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(SCEN)


def _never_more_than_all(text: str) -> None:
    for have, need in _OVER.findall(text or ""):
        assert int(have) <= int(need), text


class TestThePhrasing:
    def test_short_of_the_bar_reads_as_before(self):
        assert congress.titled_tally(43, 45) == "43 of 45 titled"
        assert congress.titled_held_clause(43, 45) == "(43 of 45)"
        assert congress.titled_summary_line(43, 45) == \
            "43 of 45 titled provinces in the Empire and its satellites."

    def test_on_the_bar_reads_as_before(self):
        assert congress.titled_tally(45, 45) == "45 of 45 titled"

    def test_past_the_bar_never_reads_more_than_all(self):
        assert congress.titled_tally(50, 45) == "50 titled, 45 needed"
        assert congress.titled_held_clause(50, 45) == "(50 held)"
        assert congress.titled_summary_line(50, 45) == (
            "50 titled provinces in the Empire and its satellites — 45 were needed.")


@pytest.fixture
def past_the_bar(monkeypatch):
    """The boot's 35 titled provinces against a bar lowered to 30."""
    w = _boot()
    assert congress.titled(w)["count"] == 35
    monkeypatch.setattr(congress, "hold_titled", lambda world: 30)
    return w


class TestTheSurfaces:
    def test_the_gate_line(self, past_the_bar):
        line = congress.state_line(past_the_bar)
        assert "35 titled, 30 needed" in line, line
        _never_more_than_all(line)

    def test_the_gate_terms(self, past_the_bar):
        term = next(t for t in congress.gate_terms(past_the_bar) if t["key"] == "titled")
        assert term["text"] == "30 titled provinces (35 held)" and term["met"] is True

    def test_the_end_screens_line_is_the_backends(self):
        block = congress.summary_block({"titled": 50, "hold_titled": 45})
        assert block["titled_line"] == (
            "50 titled provinces in the Empire and its satellites — 45 were needed.")
        _never_more_than_all(block["titled_line"])
        assert congress.summary_block({"titled": 43, "hold_titled": 45})["titled_line"] == \
            "43 of 45 titled provinces in the Empire and its satellites."
        assert congress.summary_block({})["titled_line"] == ""

    def test_the_client_prints_the_backends_line(self):
        src = (REPO / "godot-client" / "project-sovereign" / "scripts" / "campaign_end.gd").read_text(
            encoding="utf-8")
        assert 'congress.get("titled_line")' in src
        # the fallback for an older stamp is phrased the same way
        assert '" were needed.\\n"' in src
        assert 'str(_n(congress, "titled")) + " of " + str(hold)' not in src
