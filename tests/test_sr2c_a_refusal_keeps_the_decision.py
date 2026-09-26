"""SR-2c / WO-32 (P1) — a refused arm keeps the decision (Score Mandate
Chunk 2 DIPLOMACY, September 26, 2026; `docs/SCORE_MANDATE_PLAN.md` §2 Chunk
2; row `BUG_FIXES.md` WO-32).

The vassal-rebellion popup no longer destroys its decision on a refused arm:
the arm runs first; the dialogue is retired and the rail row dismissed ONLY on
success; a refused Invest / Garrison re-seats the modal with the refusal on
it (PT-A1's pattern, ported from the marshal-petition channel).
"""

from __future__ import annotations

import contextlib
import io
from pathlib import Path

import pytest

import backend.game_logic.vassal as V
import backend.main as M
from backend.commands.parser import CommandParser
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
               / "europe_1805.json")

with contextlib.redirect_stdout(io.StringIO()):
    _PARSER = CommandParser(use_real_llm=False)


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _europe():
    with _quiet():
        return WorldState.from_scenario(SCENARIO)


# ═══════════════════════════════════════════════════════════════════════
# WO-32 — a refused arm keeps the decision
# ═══════════════════════════════════════════════════════════════════════

def _rebellion_world():
    """Holland at loyalty 9 on the 1805 boot (the producer fires at <= 10): the producer fires the modal on
    the loyalty pass; the dialogue is current, its popup queued."""
    w = _europe()
    w.vassals["Holland"]["loyalty"] = 9
    with _quiet():
        V.process_vassal_loyalty(w)
    dlg = w.dialogue_manager.peek()
    assert dlg and dlg.get("type") == "vassal_rebellion_imminent", dlg
    assert dlg["context"]["vassal_name"] == "Holland"
    return w, dlg


def _rebellion_rows(world, vassal=None):
    from backend.notifications import VASSAL_REBELLION_IMMINENT
    rows = [n for n in world.notifications.get_pending()
            if n.get("type") == VASSAL_REBELLION_IMMINENT]
    if vassal:
        rows = [n for n in rows if (n.get("details") or {}).get("vassal") == vassal]
    return rows


class TestARefusedArmKeepsTheDecision:

    def test_the_producer_and_the_re_seat_share_one_builder(self):
        w, dlg = _rebellion_world()
        popup = w.vassal_rebellion_imminent_popups[0] if w.vassal_rebellion_imminent_popups else w.vassal_rebellion_imminent_popup
        rebuilt = V.rebellion_popup_for_dialogue(w, dlg)
        for key in ("nation", "loyalty", "invest_cost_dp", "garrison_ap_cost",
                    "invest_effect", "garrison_effect", "accept_effect", "dialogue_id"):
            assert rebuilt[key] == popup[key], key

    def test_a_refused_invest_keeps_the_dialogue_and_re_seats_the_modal(self):
        w, dlg = _rebellion_world()
        w.vassal_investment_cooldowns = {"Holland": 2}     # the cooldown arm
        from backend.commands.executor import CommandExecutor
        ex = CommandExecutor()._diplomatic
        with _quiet():
            r = ex.handle_diplomatic_dialogue_response(
                "invest_vassal_rebellion", {"world": w}, dialogue_id=dlg["dialogue_id"])
        assert r["success"] is False
        assert "cooldown" in r["message"].lower()
        assert r.get("vassal_rebellion_retained") is True
        assert w.dialogue_manager.peek() is dlg           # the decision stands
        popup = w.vassal_rebellion_imminent_popup
        assert popup and popup["dialogue_id"] == dlg["dialogue_id"]
        assert popup["refusal"] == r["message"]
        assert _rebellion_rows(w, "Holland")                # the row stands

    def test_a_refused_garrison_keeps_the_dialogue_too(self):
        w, dlg = _rebellion_world()
        w.actions_remaining = 1
        from backend.commands.executor import CommandExecutor
        ex = CommandExecutor()._diplomatic
        with _quiet():
            r = ex.handle_diplomatic_dialogue_response(
                "garrison_vassal_rebellion", {"world": w}, dialogue_id=dlg["dialogue_id"])
        assert r["success"] is False and "Insufficient AP" in r["message"]
        assert w.dialogue_manager.peek() is dlg
        assert w.vassal_rebellion_imminent_popup["refusal"] == r["message"]

    def test_the_other_arms_survive_a_refusal(self):
        w, dlg = _rebellion_world()
        w.vassal_investment_cooldowns = {"Holland": 2}
        from backend.commands.executor import CommandExecutor
        ex = CommandExecutor()._diplomatic
        with _quiet():
            ex.handle_diplomatic_dialogue_response(
                "invest_vassal_rebellion", {"world": w}, dialogue_id=dlg["dialogue_id"])
            r = ex.handle_diplomatic_dialogue_response(
                "accept_vassal_rebellion", {"world": w}, dialogue_id=dlg["dialogue_id"])
        assert r["success"] is True
        assert w.dialogue_manager.peek() is not dlg
        assert not _rebellion_rows(w, "Holland")

    def test_a_successful_invest_retires_the_decision_and_this_row_only(self):
        w, dlg = _rebellion_world()
        w.diplomatic_points = 5
        w.nation_gold["France"] = 5000
        # a second satellite's row must survive Holland's decision
        from backend.notifications import (VASSAL_REBELLION_IMMINENT,
                                           NotificationPriority, create_notification)
        w.notifications.add(create_notification(
            VASSAL_REBELLION_IMMINENT, NotificationPriority.HIGH, "Switzerland Critical!",
            "x", int(w.current_turn), details={"vassal": "Switzerland"}))
        from backend.commands.executor import CommandExecutor
        ex = CommandExecutor()._diplomatic
        with _quiet():
            r = ex.handle_diplomatic_dialogue_response(
                "invest_vassal_rebellion", {"world": w}, dialogue_id=dlg["dialogue_id"])
        assert r["success"] is True, r
        assert w.dialogue_manager.peek() is not dlg
        assert w.vassal_rebellion_imminent_popup is None
        assert not _rebellion_rows(w, "Holland")
        assert _rebellion_rows(w, "Switzerland")

    def test_the_lever_down_is_the_old_pop_first(self, monkeypatch):
        monkeypatch.setattr(V, "A_REFUSED_ARM_KEEPS_THE_DECISION", False)
        w, dlg = _rebellion_world()
        w.vassal_investment_cooldowns = {"Holland": 2}
        from backend.commands.executor import CommandExecutor
        ex = CommandExecutor()._diplomatic
        with _quiet():
            r = ex.handle_diplomatic_dialogue_response(
                "invest_vassal_rebellion", {"world": w}, dialogue_id=dlg["dialogue_id"])
        assert r["success"] is False
        assert w.dialogue_manager.peek() is not dlg

    def test_the_wire_re_shows_the_modal_on_a_refusal(self, monkeypatch):
        """The client hides the modal before the answer arrives (its own
        `_on_invest`), so the response must carry the modal again."""
        w, dlg = _rebellion_world()
        w.vassal_investment_cooldowns = {"Holland": 2}
        monkeypatch.setattr(M, "world", w)
        monkeypatch.setattr(M, "parser", _PARSER)
        monkeypatch.setitem(M.game_state, "world", w)
        from fastapi.testclient import TestClient
        client = TestClient(M.app)
        with _quiet():
            r = client.post("/respond_to_diplomatic_dialogue",
                            json={"choice": "invest_vassal_rebellion",
                                  "dialogue_id": dlg["dialogue_id"]}).json()
        assert r["success"] is False
        modal = r.get("vassal_rebellion_imminent")
        assert modal and modal["dialogue_id"] == dlg["dialogue_id"]
        assert modal["nation"] == "Holland"
        assert "cooldown" in str(modal.get("refusal", "")).lower()


