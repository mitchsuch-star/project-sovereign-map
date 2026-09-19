"""CX-7 slice 3 — THE PREDICTOR, DRIVEN.

Row CX ("The Hand on the Keyboard"), review round. Landing record:
`docs/COMMAND_EXPERIENCE_SPEC.md` §8.9; rows `BUG_FIXES.md` §Row CX.

⛔ WHY THIS FILE EXISTS AT ALL
=============================
CX-3 pinned its client half by READING THE SOURCE, and said so in a docstring:

    "The client half, pinned by reading the source — there is no headless way
     to press Up in this project, and the alternative is no pin at all."

**That is false, and the review round proved it by doing it.** The same
`Viewport.push_input(InputEventKey)` the row already used for Tab reaches
`_on_command_input_gui_input`, and every key the completer binds is handled in
that one function. Four confirmed defects were living behind that belief —
three of them in the completer's own behaviour, invisible to two green source
censuses on the very function that held them.

`tools/cx7_predictor_harness.gd` instantiates the REAL `main.tscn` under
Godot 4.4.1 headless, swaps an API stub in before `_ready` can fetch (IQ-10's
own shape), presses real keys, and writes one JSON object. This file reads it.

**It SKIPS when the engine is absent**, so the suite stays green on a machine
without Godot — and a skip is not a pass, which is why the four assertions
below are also the four rows' completion definitions.

THE FOUR DEFECTS
================
**CX3-R3 — the completer's grammar half was DEAD on the ordinary boot path.**
`_remember_game_state` was called only inside the `_initial_map_bootstrapped`
TRUE arm, and that flag is measurably false from frame 3 through frame 60 on a
fresh scene (the topology request that flips it is issued four lines above).
So after "Return to the War Room" — the default road from the main menu —
`Ney, ` offered NOTHING until the player issued a real command, while the same
probe on the Begin path offered all five verbs. The board was on the wire the
whole time: `/test` serves the same fog-filtered builder `/command` does, and
the handler already reads five other things out of it.

**CX3-R7 — the completer went silent at exactly the keystroke it exists for.**
`history_index` is cleared only by SENDING, so recalling a line with Up
switched the completer off for the rest of that line. The ordinary thing a
player does with a shell history is recall the last order and change its
target: measured, after `Up` + four backspaces + `Bru`, the shipped code
offered nothing where a live completer had **one unambiguous completion**.

**CX3-R1 — the list drew five and delivered one.** Tab accepts the highlighted
offer and then RE-DERIVES from the longer line, so the other offers are gone
before they can be reached; no sequence of keys could place offer #2 on the
line. Down now walks them. A separate `elif` ABOVE the Tab arm on purpose —
editing the Tab line reds `test_tab_is_the_accept_key_and_was_free`.

**CX3-R8 — the suggestion row was the largest text in the terminal.** It took
no font override, so it inherited the theme's RichTextLabel 16 while the
game's prose is 11 and the line it completes is 12. Measured off the live
nodes: capitals 21px against 14px and 16px.
"""

import json
import os
import pathlib
import shutil
import subprocess

import pytest

_REPO = pathlib.Path(__file__).resolve().parents[1]
_PROJECT = _REPO / "godot-client" / "project-sovereign"
_HARNESS = _REPO / "tools" / "cx7_predictor_harness.gd"

_CANDIDATES = [
    os.environ.get("GODOT_BIN", ""),
    r"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe"
    r"\Godot_v4.4.1-stable_win64.exe",
    "godot",
    "godot4",
]


def _engine():
    for candidate in _CANDIDATES:
        if not candidate:
            continue
        if os.path.sep in candidate or "/" in candidate:
            if pathlib.Path(candidate).is_file():
                return candidate
            continue
        found = shutil.which(candidate)
        if found:
            return found
    return None


@pytest.fixture(scope="module")
def driven(tmp_path_factory):
    """One headless run of the real scene, shared by every assertion."""
    engine = _engine()
    if engine is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    out = tmp_path_factory.mktemp("cx7") / "predictor.json"
    env = dict(os.environ, CX7_OUT=str(out))
    proc = subprocess.run(
        [engine, "--headless", "--path", str(_PROJECT),
         "--script", str(_HARNESS)],
        capture_output=True, text=True, timeout=300, env=env,
        cwd=str(_PROJECT),
    )
    if not out.is_file():
        pytest.fail(
            "the harness wrote no result\n"
            f"exit={proc.returncode}\n"
            f"stdout tail:\n{proc.stdout[-2000:]}\n"
            f"stderr tail:\n{proc.stderr[-2000:]}")
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert "error" not in payload, payload
    return payload


class TestTheBoardSurvivesTheBoot:
    """CX3-R3."""

    def test_the_flag_that_gated_the_old_call_is_false_at_boot(self, driven):
        """The mechanism, not just the symptom: if this is ever True on a
        fresh scene the defect could not have existed, and the pin is about
        the wrong thing."""
        assert driven["r3_bootstrapped_at_boot"] is False

    def test_the_flag_is_still_false_when_the_handler_runs(self, driven):
        """⛔ The first cut of this pin PASSED with the fix reverted, because
        the harness's stub answered the topology request synchronously and
        flipped the flag — handing `_on_connection_test` the arm it takes in
        no real boot. The stub records that call and never answers it now,
        which is the real client's timing."""
        assert driven["r3_bootstrapped_after"] is False

    def test_the_connection_test_remembers_the_board(self, driven):
        assert driven["r3_remembered"] is True

    def test_the_grammar_half_is_live_before_any_command(self, driven):
        """Five verbs on `Ney, ` — the Begin path's own answer, now on the
        Return path too."""
        offers = driven["r3_offers_after_boot"]
        assert len(offers) >= 4, offers
        assert all(str(o).startswith("Ney, ") for o in offers), offers


class TestEveryDrawnOfferCanBeReached:
    """CX3-R1."""

    def test_the_list_draws_more_than_one(self, driven):
        """Or the next assertion is vacuous."""
        assert driven["r1_drawn"] >= 2, driven["r1_drawn"]

    def test_nothing_drawn_is_unreachable(self, driven):
        assert driven["r1_unreachable"] == [], driven["r1_unreachable"]


class TestTheCompleterWakesWhenTheRecalledLineIsEdited:
    """CX3-R7."""

    def test_it_offers_before_the_recall(self, driven):
        assert driven["r7_before_up"] >= 1

    def test_up_fills_the_line_from_history(self, driven):
        assert driven["r7_line_after_up"] == "Ney, attack Mack"

    def test_the_list_closes_under_the_line_the_walk_filled(self, driven):
        """CX-3's original intent, kept: a walk must not re-open the list
        under the line it just put there."""
        assert driven["r7_during_walk"] == 0

    def test_editing_the_recalled_line_wakes_it(self, driven):
        """The defect. `Ney, attack Bru` → one unambiguous completion."""
        assert driven["r7_after_edit"] == ["Ney, attack Brunswick"], \
            driven["r7_after_edit"]

    def test_the_walk_is_over(self, driven):
        assert driven["r7_history_index"] == -1


class TestTheRowMatchesTheLineItCompletes:
    """CX3-R8."""

    def test_the_font_sizes_agree(self, driven):
        assert driven["row_font_size"] == driven["input_font_size"], driven

    def test_it_is_the_command_line_size_and_not_the_theme_default(self, driven):
        """16 is the theme's RichTextLabel default and is what it inherited."""
        assert driven["row_font_size"] == 12, driven["row_font_size"]


class TestTheCompleterNeverSends:
    """The rule CX-3 landed with, re-proven by DRIVING it rather than by
    reading the source — which is the whole point of this file."""

    def test_tab_fills_the_line(self, driven):
        assert driven["tab_filled"].startswith("Ne"), driven["tab_filled"]

    def test_tab_sends_nothing(self, driven):
        assert driven["tab_sent"] is False
