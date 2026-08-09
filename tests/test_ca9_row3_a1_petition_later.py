"""CA9 row 3 / A1 — the petition's "Later" button no longer bricks the turn.

Audit record: `docs/audits/GRIEVANCE_REVISIT_INVESTIGATION_2026_08_09.md` §4
item A1 (the one P1 in that memo that needed no design ruling).

`marshal_petition_dialog._on_later()` was a bare `hide()` with no signal. The
card is shown from `_post_hud_response_routes`, and EVERY entry in that list
returns before `set_input_enabled(true)` — the Proclamation carries a
`dismissed` signal for exactly this reason and says so in a comment. So the
polite button left the command line, Send, End Turn and the diplomacy wizard
disabled for the rest of the session, with no recovery short of a reload.

This is a `.gd`-only fix, so it is pinned by source assertion the way the
project's other client-side contracts are (precedent: the NA-6 dead-name pin
and `test_naval_ui_clarity.py`). The assertions are deliberately narrow —
each one fails if the specific link in the chain is removed, rather than
matching a broad blob of text that would survive the regression.
"""

import io
import re
from pathlib import Path

import pytest

_CLIENT = Path("godot-client/project-sovereign/scripts")
_DIALOG = _CLIENT / "marshal_petition_dialog.gd"
_MAIN = _CLIENT / "main.gd"


def _src(path: Path) -> str:
    assert path.exists(), f"{path} moved — re-point this pin, do not delete it"
    return io.open(path, encoding="utf-8", errors="replace").read()


@pytest.fixture(scope="module")
def dialog() -> str:
    return _src(_DIALOG)


@pytest.fixture(scope="module")
def main() -> str:
    return _src(_MAIN)


class TestTheDeferralEmits:
    def test_the_signal_is_declared(self, dialog):
        assert re.search(r"^signal petition_deferred", dialog, re.M), (
            "the deferral signal is gone — `Later` cannot hand control back")

    def test_on_later_emits_it(self, dialog):
        """Scoped to the body of `_on_later` so a stray emit elsewhere in the
        file cannot satisfy this."""
        match = re.search(r"^func _on_later\(\):\n((?:\t.*\n|\n)+)",
                          dialog, re.M)
        assert match, "_on_later disappeared"
        body = match.group(1)
        assert "petition_deferred.emit()" in body, (
            f"_on_later does not emit — it is a bare hide() again:\n{body}")

    def test_on_later_still_hides(self, dialog):
        match = re.search(r"^func _on_later\(\):\n((?:\t.*\n|\n)+)",
                          dialog, re.M)
        assert "hide()" in match.group(1)


class TestMainReconnectsControl:
    def test_the_signal_is_connected(self, main):
        assert "petition_deferred.connect(" in main, (
            "the signal is emitted into nothing — the soft-lock is back")

    def test_the_handler_exists(self, main):
        assert re.search(r"^func _on_marshal_petition_deferred\(\)",
                         main, re.M)

    def test_the_handler_re_enables_input(self, main):
        """The whole point. Bounded to the handler's own body — an unbounded
        scrape would match any of main.gd's ~40 other `set_input_enabled`
        calls and pass over a completely empty handler."""
        match = re.search(
            r"^func _on_marshal_petition_deferred\(\).*?\n((?:\t.*\n|\n)+)",
            main, re.M | re.S)
        assert match, "handler disappeared"
        body = match.group(1)
        assert "set_input_enabled(true)" in body, (
            f"the handler does not hand control back:\n{body}")

    def test_the_handler_drains_what_was_stashed_behind_it(self, main):
        """Follows the Proclamation's tail. If a formation or a letter-book
        was stashed while the petition was up, deferring must not swallow
        it — that is the NA-6b / IGR-F failure mode."""
        match = re.search(
            r"^func _on_marshal_petition_deferred\(\).*?\n((?:\t.*\n|\n)+)",
            main, re.M | re.S)
        body = match.group(1)
        assert "_show_pending_proclamation()" in body
        assert "_show_pending_envoy_digest()" in body


class TestTheTrapItselfIsStillReal:
    """Guards the PREMISE. If the route ever starts returning control on its
    own, this fix becomes redundant and these pins should be revisited
    deliberately rather than left asserting a contract nobody relies on."""

    def test_the_petition_is_still_a_post_hud_route(self, main):
        assert '{"id": "marshal_petition"' in main, (
            "the petition left _post_hud_response_routes — re-read A1's "
            "premise before trusting the pins above")

    def test_that_route_family_still_returns_before_re_enabling(self, main):
        """The two lines that make the trap: `_route_response_ui` returns, and
        `set_input_enabled(true)` sits after it."""
        match = re.search(
            r"if _route_response_ui\(response, _post_hud_response_routes\):\n"
            r"\t\treturn[^\n]*\n",
            main)
        assert match, (
            "the early return is gone — if control is now handed back "
            "centrally, A1's signal is belt-and-braces and the comment "
            "in marshal_petition_dialog.gd should be corrected")
