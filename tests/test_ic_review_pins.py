"""Row IC — the review of "on his own" (November 20, 2026): the four defects
the review found in the SHIPPED game. Each was filed as a strict-xfail pin
that turns red the day its fix lands, so the row had to close with it — and
all four landed the same day, in row IC's Session 2 (buttons for orders, the
line for tasks, exact orders): every pin below is a plain behaviour test now.

  IC-V1, IC-V2  the read-back's rows — `tests/test_ic8_the_line.py` holds the
                full behaviour (Taken, Not taken, the line as understood, the
                typed gate).
  IC-V3         a guard on the two jealousy seams (`jealousy.acts_independently`).
                The three turns themselves — the trust crisis's "Grant
                Autonomy" — are replaced by a task to prove himself in row
                IC's own next session (Session 2b: row IC2-D1, the strict
                xfail at the foot of this file; INDEPENDENT_COMMAND_SPEC
                §6.11, §15); these two tests are then re-seated on that state.
  IC-V4         the one client table — `tests/test_ic7_the_buttons.py` holds
                the buttons' behaviour, server and client.

The rows as they were filed:

The design is `docs/INDEPENDENT_COMMAND_SPEC.md` version 6 (§1.3's November 20
list, §6.11, §8); the ledger `docs/BUG_FIXES.md` §"Row IC — the review of 'on
his own'"; every finding and its ruling
`docs/audits/ic_focus_groups/round4_review_ledger.md`.

  IC-V1 (owner IC-8)  "Ney, retreat if outnumbered" reads back as a plain fall
                      back and retreats now: a one-word condition slips under
                      the two-word floor and is dropped without a word (the
                      corpus row `parseneg-retreat-if-outnumbered-executes`
                      pinned it as an accepted trade-off; version 6's
                      read-back rule makes it a defect).
  IC-V2 (owner IC-8)  the read-back shows neither a condition it took ("until
                      Ney arrives", "for three turns") nor an if-then ("if Mack
                      advances, fall back to Lorraine") — both appear only
                      after the order is sent.
  IC-V3 (owner IC-9)  a marshal in the trust crisis's three turns ("Grant
                      Autonomy") who is also jealous and bold is warned,
                      strikes before the enemy moves, and is moved again by the
                      enemy's decision logic after it — two battles in one end
                      of turn (nothing in the strike's path reads `autonomous`).
  IC-V4 (owner IC-7)  eight simple orders and four group orders have no button,
                      and the Help's Orders page says the map's clicks give the
                      same orders as the typed line; IC-7 seats them in one
                      client table, `SIMPLE_ORDER_BUTTONS`.

Each class carries a premise test (green today and after the fix) so the xfail
fails for the reason the row names, not for a broken fixture.
"""
from __future__ import annotations

import contextlib
import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import parse_preview as PP
from backend.commands.parser import CommandParser
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
SCENARIO_PATH = (REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
                 / "europe_1805.json")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


# ═══════════════════════ the read-back (IC-V1, IC-V2) ═══════════════════════

@pytest.fixture(scope="module")
def preview():
    """The shipped 1805 board behind the real app and a mock parser (the
    pattern of `tests/test_parse_preview.py`: swap `M.world`, the game state's
    world and `M.parser` together, and put all three back)."""
    mp = pytest.MonkeyPatch()
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        mp.delenv(key, raising=False)
    mp.setenv("LLM_MODE", "mock")
    prior = (M.world, M.game_state.get("world"), M.parser)
    with _quiet():
        M._reset_world_state()
        M.parser = CommandParser(use_real_llm=False)
    PP.invalidate()
    try:
        with TestClient(M.app) as client:
            def read(line):
                with _quiet():
                    return client.get("/parse_preview", params={"line": line}).json()
            yield read
    finally:
        M.world, M.parser = prior[0], prior[2]
        M.game_state["world"] = prior[1]
        PP.invalidate()
        mp.undo()


def _parts_text(reading) -> str:
    return " · ".join(str(p.get("text") or "") for p in (reading.get("parts") or []))


def _head(reading) -> str:
    for p in reading.get("parts") or []:
        if p.get("role") == "head":
            return str(p.get("text") or "")
    return ""


class TestICV1AOneWordConditionIsNeverDroppedInSilence:

    def test_the_line_is_read_as_neys_fall_back(self, preview):
        reading = preview("Ney, retreat if outnumbered")
        assert reading.get("success") and reading.get("marshal") == "Ney"
        assert reading.get("action") == "retreat"
        assert _head(reading).startswith("Ney")

    def test_the_read_back_names_the_clause_it_did_not_take(self, preview):
        reading = preview("Ney, retreat if outnumbered")
        assert "outnumbered" in _parts_text(reading).lower(), (
            "the read-back must say 'if outnumbered' was not taken before anything is sent "
            "(INDEPENDENT_COMMAND_SPEC §8.4)")


class TestICV2TheReadBackShowsTheConditionAndTheIfThen:

    def test_the_lines_are_read_as_holds(self, preview):
        until = preview("Davout, hold Franconia until Ney arrives")
        assert until.get("success") and until.get("action") == "hold"
        assert _head(until).startswith("Davout")
        contingency = preview("Ney, if Mack advances, fall back to Lorraine")
        assert contingency.get("success") and contingency.get("action") == "hold"

    def test_a_taken_condition_is_shown_before_the_order_goes(self, preview):
        text = _parts_text(preview("Davout, hold Franconia until Ney arrives")).lower()
        assert "until" in text and "ney" in text

    def test_a_taken_if_then_is_shown_before_the_order_goes(self, preview):
        text = _parts_text(preview("Ney, if Mack advances, fall back to Lorraine")).lower()
        assert "lorraine" in text and "mack" in text


# ═══════════════════════ the double act (IC-V3) ═════════════════════════════

@pytest.fixture(scope="module")
def world1805():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO_PATH))


def _warned_ney(world1805, *, autonomous: bool):
    """`tests/test_jealousy_v32.py`'s own setup: Ney jealous of Davout,
    standing with Mack in Swabia (at war), authority neutral."""
    world = WorldState.from_dict(world1805.to_dict())
    world.authority_tracker.authority = 50
    ney = world.marshals["Ney"]
    ney.location = "Swabia"
    ney.jealous_of = "Davout"
    ney.jealousy_turns_remaining = 4
    if autonomous:
        ney.autonomous = True
        ney.autonomy_turns = 2
        ney.autonomy_reason = "redemption"
    return world, ney


class TestICV3AManActingIndependentlyActsOnce:

    def test_a_warned_jealous_man_strikes_at_the_turns_end(self, world1805):
        from backend.commands.executor import CommandExecutor
        from backend.game_logic import jealousy as J
        world, ney = _warned_ney(world1805, autonomous=False)
        ney.jealousy_autonomous_warned = True
        with _quiet():
            fired = J.process_autonomous_attacks(world, CommandExecutor(), {"world": world})
        assert fired, "the premise: the warned strike fires for a man with no other state"

    def test_a_man_acting_independently_is_never_warned(self, world1805):
        from backend.game_logic import jealousy as J
        world, ney = _warned_ney(world1805, autonomous=True)
        world._jealousy_processed_turn = None
        with _quiet():
            J.process_turn(world)
        assert not ney.jealousy_autonomous_warned

    def test_a_man_acting_independently_makes_no_jealous_strike(self, world1805):
        from backend.commands.executor import CommandExecutor
        from backend.game_logic import jealousy as J
        world, ney = _warned_ney(world1805, autonomous=True)
        ney.jealousy_autonomous_warned = True
        with _quiet():
            fired = J.process_autonomous_attacks(world, CommandExecutor(), {"world": world})
        assert not fired, "his one act is the independent one; the strike would be a second"


# ═══════════════════════ the buttons (IC-V4) ═════════════════════════════════

def _client_sources() -> str:
    return "\n".join(p.read_text(encoding="utf-8", errors="replace")
                     for p in sorted(SCRIPTS.glob("*.gd")))


class TestICV4EverySimpleOrderHasAButton:

    def test_the_generals_card_is_the_one_the_row_was_filed_on(self):
        card = (SCRIPTS / "marshal_state.gd").read_text(encoding="utf-8")
        assert "const SLOTS := [" in card, "the general's seven fixed slots, where IC-7 adds"
        codex = (SCRIPTS / "codex_view.gd").read_text(encoding="utf-8")
        assert "_footer.text" in codex

    def test_the_simple_orders_sit_in_one_client_table(self):
        assert "SIMPLE_ORDER_BUTTONS" in _client_sources(), (
            "IC-7's landing: chase, the one-action stand, scout a named province, posture, square, "
            "bombard, a charge you start, stay put, a march's 'then', and the group's attack, "
            "support, fall back and garrison — one table (INDEPENDENT_COMMAND_SPEC §8.1)")


# ═══════════ handed to its own session: the task to prove himself (IC2-D1) ═══
#
# Row IC's Session 2 landed the buttons, the line for tasks and exact orders,
# and at its checkpoint took the plan's decided fork ("the session cannot hold
# all three slices at the standard: … hand IC-9 to its own session the same
# day"): the trust crisis's "Grant Autonomy" is replaced by a TASK TO PROVE
# HIMSELF — and `TurnManager._process_autonomous_marshals` / `_end_autonomy`
# deleted — in row IC's Session 2b (`docs/BUG_FIXES.md` §"Row IC, Session 2",
# row IC2-D1; INDEPENDENT_COMMAND_SPEC §6.11 and §15; `PRE_DEPLOY_PLAN.md` §2
# row IC). Until then the audience offers what it offered, and IC-V3's guard
# keeps a man in those three turns to one act a turn.
#
# The two pins are strict xfails: they turn red the day the trial lands, so
# the row must close with them.

_IC2_D1 = ("IC2-D1 (owner row IC Session 2b, slice IC-9's second half): the trust crisis's "
           "'Grant Autonomy' is replaced by a task to prove himself and the old engine deleted")


class TestIC2D1TheTrialReplacesGrantAutonomy:

    @staticmethod
    def _options(world1805):
        from backend.commands.disobedience import DisobedienceSystem
        with _quiet():
            world = WorldState.from_dict(world1805.to_dict())
            return DisobedienceSystem()._get_available_redemption_options(
                world.marshals["Ney"], world)

    def test_the_audience_has_answers_for_a_man_whose_trust_has_broken(self, world1805):
        """The premise — green today and after the trial lands."""
        options = self._options(world1805)
        assert options and all(option.get("id") for option in options)

    @pytest.mark.xfail(strict=True, reason=_IC2_D1)
    def test_the_audience_offers_a_task_to_prove_himself_and_no_autonomy(self, world1805):
        ids = [option["id"] for option in self._options(world1805)]
        assert "grant_autonomy" not in ids and "trial" in ids

    @pytest.mark.xfail(strict=True, reason=_IC2_D1)
    def test_no_french_marshal_is_moved_by_the_enemys_logic(self):
        from backend.game_logic.turn_manager import TurnManager
        assert not hasattr(TurnManager, "_process_autonomous_marshals")
        assert not hasattr(TurnManager, "_end_autonomy")
