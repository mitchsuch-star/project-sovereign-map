"""SR-6a "The dispatch pass" (Score Finish Step 2, October 2, 2026) — the rows
outside the headline builder: the cascade grouped (RS-23), the coverage
labels (RS-9 / RS-19), the PL-14 net's neutral fallback (RS-20), the desk
reading the table (SRX-5) and placing a court / reading the alarm (RS-14).
"""
import contextlib
import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands.parser import CommandParser
from backend.game_logic import diplomacy as D
from backend.game_logic import dispatch, game_end
from backend.game_logic import settlement_presentation as SP
from backend.game_logic import settlement_ratify as SR
from backend.game_logic import settlement_scoring as SS
from backend.game_logic.settlement_ratify import ratify_settlement_confirm
from backend.game_logic.settlement_staging import stage_settlement_confirm
from backend.models.world_state import WorldState
from backend.notifications import (ALLIANCE_CASCADE_WAR,
                                   DIPLOMATIC_PROPOSAL_RESULT, WAR_DECLARED)

REPO = Path(__file__).resolve().parents[1]
SCEN = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
           / "europe_1805.json")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture
def world():
    with _quiet():
        return WorldState.from_scenario(SCEN)


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False
    return TestClient(M.app), M.world


def post(client, command):
    return client.post("/command", json={"command": command}).json()


# ═══════════════════════════════════════════════════════════════════════════
# RS-23 — the alliance cascade, grouped and naming the enemy
# ═══════════════════════════════════════════════════════════════════════════

def _cascade_rows(world):
    return [n for n in world.notifications.get_pending() if n["type"] == ALLIANCE_CASCADE_WAR]


class TestTheCascadeIsGrouped:

    def test_one_rail_row_per_ally_per_turn_naming_the_enemies(self, world):
        world.notifications.dismiss_by_type(ALLIANCE_CASCADE_WAR)
        for nation in ("Prussia", "Spain", "Bavaria"):
            for enemy in ("Austria", "Russia"):
                D._note_alliance_cascade(world, nation, "France", enemy)
        rows = _cascade_rows(world)
        assert len(rows) == 1, [r["title"] for r in rows]
        assert rows[0]["title"] == "Prussia, Spain and Bavaria Enter War!"
        assert rows[0]["message"] == ("Prussia, Spain and Bavaria enter the war against "
                                      "Austria and Russia via their alliance with France.")
        assert rows[0].get("repeat_count", 1) == 1, "never (x8)"

    def test_one_dispatch_line_per_ally(self, world):
        world.pending_dispatch_events = []
        for nation in ("Prussia", "Spain"):
            for enemy in ("Austria", "Russia"):
                D._note_alliance_cascade(world, nation, "France", enemy)
        rows = [r for r in dispatch._build_diplomatic_events_section(world, "France")
                if r["type"] == "diplomatic_alliance_cascade"]
        assert len(rows) == 1, rows
        assert rows[0]["text"] == ("Prussia and Spain enter the war against Austria and "
                                   "Russia via their alliance with France.")
        assert rows[0]["priority"] == "HIGH"

    def test_a_second_turn_is_a_second_row(self, world):
        world.notifications.dismiss_by_type(ALLIANCE_CASCADE_WAR)
        D._note_alliance_cascade(world, "Prussia", "France", "Austria")
        world.current_turn += 1
        D._note_alliance_cascade(world, "Prussia", "France", "Russia")
        rows = _cascade_rows(world)
        assert len(rows) == 2 and all(r.get("repeat_count", 1) == 1 for r in rows)

    def test_the_real_producer(self, world):
        """A declaration whose cascade pulls an ally in names the declarer."""
        world.notifications.dismiss_by_type(ALLIANCE_CASCADE_WAR)
        world.pending_dispatch_events = []
        D.set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "test")
        assert not world.is_at_war("Prussia", "Sweden")
        D.set_diplomatic_state(world, "France", "Sweden", "PEACE", "test")
        with _quiet():
            result = D.declare_war(world, "Sweden", "France")
        assert result.get("success"), result
        rows = _cascade_rows(world)
        assert rows and "Sweden" in rows[0]["message"], rows
        events = [e for e in world.pending_dispatch_events
                  if e["type"] == "diplomatic_alliance_cascade"]
        assert events and events[0]["template_vars"]["against"] == "Sweden"

    def test_the_log_names_the_enemy(self):
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({"type": "diplomatic_alliance_cascade",
                                      "nation": "Prussia", "ally": "France",
                                      "against": "Austria"})
        assert line == "Alliance cascade: Prussia enters war against Austria via France"

    def test_lever_down_is_the_old_row_and_line(self, world, monkeypatch):
        monkeypatch.setattr(dispatch, "THE_CASCADE_IS_GROUPED", False)
        world.notifications.dismiss_by_type(ALLIANCE_CASCADE_WAR)
        world.pending_dispatch_events = []
        for enemy in ("Austria", "Russia"):
            D._note_alliance_cascade(world, "Prussia", "France", enemy)
        rows = _cascade_rows(world)
        assert len(rows) == 1 and rows[0]["title"] == "Prussia Enters War! (x2)"
        lines = [r["text"] for r in dispatch._build_diplomatic_events_section(world, "France")
                 if r["type"] == "diplomatic_alliance_cascade"]
        assert lines == ["Prussia enters the war via alliance with France."] * 2


# ═══════════════════════════════════════════════════════════════════════════
# RS-9 / RS-19 — the coverage labels
# ═══════════════════════════════════════════════════════════════════════════

def _carrying(monkeypatch):
    real = SS.calculate_common_peace_acceptance

    def carries(*args, **kwargs):
        out = dict(real(*args, **kwargs))
        out["score"] = 100
        out["verdict"] = "accept"
        return out
    monkeypatch.setattr(SS, "calculate_common_peace_acceptance", carries)


def _stage(world, covered):
    while world.dialogue_manager.pop() is not None:
        pass                                   # a fresh table each time
    with _quiet():
        staged = stage_settlement_confirm(
            world, war_id="war_1", settlement_terms=[{"type": "peace"}],
            covered_enemy_participants=list(covered))
    assert staged["success"], staged
    return world.pending_diplomatic_dialogue


class TestTheCoverageLabels:

    def test_the_record_names_the_coverage(self, world, monkeypatch):
        _carrying(monkeypatch)
        dialogue = _stage(world, ["Austria"])
        assert dialogue["war_label"] == "France vs Austria"
        world.pending_dispatch_events = []
        with _quiet():
            result = ratify_settlement_confirm(world, dialogue)
        assert result["success"], result
        events = [e for e in world.pending_dispatch_events
                  if str(e.get("type", "")).startswith("settlement_")]
        assert events, "the ratification writes its dispatch record"
        for e in events:
            label = str(e.get("war_label") or "")
            assert label == "France vs Austria", label
        rows = [n for n in world.notifications.get_pending()
                if "settlement" in str(n.get("type", "")).lower()
                or "Settlement" in str(n.get("title", ""))]
        for n in rows:
            assert "Britain" not in n["message"] and "Russia" not in n["message"], n

    def test_lever_down_names_the_whole_war(self, world, monkeypatch):
        monkeypatch.setattr(SR, "THE_RECORD_NAMES_THE_COVERAGE", False)
        _carrying(monkeypatch)
        dialogue = _stage(world, ["Austria"])
        world.pending_dispatch_events = []
        with _quiet():
            ratify_settlement_confirm(world, dialogue)
        events = [e for e in world.pending_dispatch_events
                  if str(e.get("type", "")).startswith("settlement_")]
        assert any("Britain" in str(e.get("war_label") or "") for e in events)

    def test_uncovered_courts_are_every_court_left_at_war(self, world, monkeypatch):
        _carrying(monkeypatch)
        dialogue = _stage(world, ["Austria"])
        assert sorted(dialogue["uncovered_enemy_display_chips"]) == ["Britain", "Russia"]
        assert dialogue["coverage_scope_display"] == "Separate settlement"
        assert dialogue["review_sections"]["coverage_label"] == "France vs Austria"
        # The covered chips are the TABLE's — Britain's army is out of sight
        # at the boot, and the fog-filtered review had dropped her.
        dialogue = _stage(world, ["Austria", "Britain"])
        assert dialogue["covered_enemy_display_chips"] == ["Austria", "Britain"]
        assert dialogue["review_sections"]["coverage_label"] == "France vs Austria + Britain"

    def test_whole_war_only_when_nothing_is_uncovered(self, world, monkeypatch):
        _carrying(monkeypatch)
        dialogue = _stage(world, ["Austria", "Britain"])
        assert dialogue["uncovered_enemy_display_chips"] == ["Russia"]
        assert dialogue["coverage_scope_display"] != "Whole-war settlement"
        dialogue = _stage(world, ["Austria", "Britain", "Russia"])
        assert dialogue["uncovered_enemy_display_chips"] == []
        assert dialogue["coverage_scope_display"] == "Whole-war settlement"

    def test_lever_down_reads_the_fog_filtered_rows(self, world, monkeypatch):
        """The row's defect: Britain, covered by the table, is dropped from the
        chips because no British corps is in view — and read as still at war."""
        monkeypatch.setattr(SP, "THE_COVERAGE_LINE_KEEPS_EVERY_COURT", False)
        _carrying(monkeypatch)
        dialogue = _stage(world, ["Austria", "Britain"])
        assert dialogue["covered_enemy_display_chips"] == ["Austria"]
        # … and the "Still at war:" line is EMPTY while Russia stands at war
        # (the chips were read off the capped, fog-filtered ally rows).
        assert dialogue["uncovered_enemy_display_chips"] == []


# ═══════════════════════════════════════════════════════════════════════════
# RS-20 — the PL-14 net's neutral fallback; the declaration never rides it
# ═══════════════════════════════════════════════════════════════════════════

class TestTheNetFallsBackNeutral:

    def test_a_result_naming_no_outcome_is_noted_not_rejected(self):
        assert M._derive_proposal_result_outcome(
            {"message": "War with Prussia! The declaration is read at every court."}) == "RESOLVED"
        assert M._derive_proposal_result_outcome({"message": "Prussia declines the pact."}) == "REJECT"
        assert M._derive_proposal_result_outcome({"outcome": "accept"}) == "ACCEPT"

    def test_lever_down_rejects(self, monkeypatch):
        monkeypatch.setattr(M, "THE_NET_FALLS_BACK_NEUTRAL", False)
        assert M._derive_proposal_result_outcome({"message": "War with Prussia!"}) == "REJECT"

    def test_the_rail_word(self, world):
        world.notifications.dismiss_by_type(DIPLOMATIC_PROPOSAL_RESULT)
        M._queue_informational_diplomacy_notices(
            {"proposal_result": {"target_nation": "Prussia",
                                 "proposal_type": "Diplomatic Action",
                                 "message": "War with Prussia!", "feedback": ""}}, world)
        rows = [n for n in world.notifications.get_pending()
                if n["type"] == DIPLOMATIC_PROPOSAL_RESULT]
        assert [n["title"] for n in rows] == ["Diplomatic Action Noted"]

    def test_the_played_road_raises_no_rejection_row(self, shipped):
        """The retest's road: the declaration, its purpose, Talleyrand's
        objection, the ally-entry review — then the war, with "War with
        Prussia!" on the rail and NO "Diplomatic Action Rejected" beside it."""
        client, world = shipped
        world.notifications.dismiss_by_type(DIPLOMATIC_PROPOSAL_RESULT)
        r = post(client, "declare war on Prussia")
        assert r.get("awaiting_diplomatic_response"), r.get("message")
        r = post(client, "1")                                   # the purpose
        assert "advise against" in r.get("message", ""), r.get("message")
        # The objection's own return carries the flag (the typed road's net).
        objection = M.executor._diplomatic._execute_diplomatic_declare_war(
            {"target_nation": "Prussia", "war_objective": "conquest"}, world)
        assert objection.get("suppress_proposal_result_popup") is True, objection
        r = client.post("/respond_to_diplomatic_objection",
                        json={"choice": "proceed", "action": "diplomatic_declare_war",
                              "target_nation": "Prussia"}).json()
        assert r.get("success"), r.get("message")
        if r.get("awaiting_diplomatic_response"):
            r = post(client, "1")                               # proceed without allies
        assert world.is_at_war("France", "Prussia")
        assert r.get("proposal_result") is None, r.get("proposal_result")
        pending = world.notifications.get_pending()
        assert not [n for n in pending if n["type"] == DIPLOMATIC_PROPOSAL_RESULT], pending
        assert any(n["type"] == WAR_DECLARED for n in pending)


# ═══════════════════════════════════════════════════════════════════════════
# SRX-5 / RS-14 — the desk reads the table, places a court, reads the alarm
# ═══════════════════════════════════════════════════════════════════════════

def _push_letter(world, letter):
    world.dialogue_manager.push(letter)


class TestTheDeskReadsTheTable:

    def test_a_settlement_letter_on_the_desk(self, shipped):
        client, world = shipped
        _push_letter(world, {
            "type": "incoming_settlement_offer",
            "dialogue_type": "incoming_settlement_offer",
            "proposer_nation": "Russia", "war_id": "war_1",
            "war_label": "France vs Russia",
            "terms_summary": ["Peace", "Gold indemnity: 500 gold from France to Russia"],
            "settlement_terms": [{"type": "peace"}],
            "turn_created": int(world.current_turn),
            "options": [], "available_action_ids": [],
        })
        r = post(client, "Berthier, remind me what the Russians demanded at the table")
        msg = r.get("message", "")
        assert "Russia's envoy brought a settlement" in msg, msg
        assert "Gold indemnity: 500 gold from France to Russia" in msg
        assert "waits in the mailbox" in msg

    def test_a_proposal_letter_names_its_terms(self, shipped):
        client, world = shipped
        _push_letter(world, {
            "type": "ai_proposal", "target_nation": "Austria",
            "proposal_type": "non_aggression",
            "context": {"proposal": {"type": "non_aggression", "clauses": [],
                                     "demands": [{"type": "gold_lump", "value": 300}]},
                        "proposal_type": "non_aggression", "source_nation": "Austria"},
            "turn_created": int(world.current_turn), "options": [],
        })
        msg = post(client, "what did Austria offer?").get("message", "")
        assert "Austria's envoy brought a proposal" in msg, msg
        assert "pays 300 gold" in msg, msg

    def test_no_letter_says_so(self, shipped):
        client, world = shipped
        msg = post(client, "what did Austria demand?").get("message", "")
        assert msg == "No letter from Austria has reached the desk, Sire — nothing was demanded."

    def test_the_congress_table_is_read(self, shipped):
        client, world = shipped
        world.congress = {"status": "sitting", "number": 1,
                          "summoned_turn": int(world.current_turn),
                          "answers": {"Russia": {"stance": "REFUSES", "court": "Russia"}}}
        msg = post(client, "what did Russia demand at the table?").get("message", "")
        assert msg.startswith("At the table while the Congress sits, Russia refuses, Sire"), msg

    def test_an_answered_letter_is_the_logs(self, shipped):
        client, world = shipped
        world.log_event({"type": "proposal_arrived", "source": "Austria",
                         "proposal_type": "non_aggression"})
        msg = post(client, "what did Austria propose?").get("message", "")
        assert f"Austria's last letter came on turn {int(world.current_turn)}" in msg, msg
        assert "no longer on the desk" in msg

    def test_the_design_question_keeps_its_answer(self, shipped):
        client, world = shipped
        msg = post(client, "what does Austria want?").get("message", "")
        assert msg.startswith("Austria pursues"), msg

    def test_lever_down_shrugs(self, shipped, monkeypatch):
        from backend.ai import question_desk as QD
        monkeypatch.setattr(QD, "THE_DESK_READS_THE_TABLE", False)
        client, world = shipped
        msg = post(client, "what did Austria demand?").get("message", "")
        assert "nothing was demanded" not in msg


class TestTheDeskPlacesACourt:

    def test_a_court_in_and_out_of_view(self, shipped):
        client, world = shipped
        msg = post(client, "where are the Austrians?").get("message", "")
        assert msg.startswith("Sire — Austria: "), msg
        assert "Mack at Swabia" in msg
        msg = post(client, "where are the Russians?").get("message", "")
        assert msg.startswith("Sire — Russia: ") and "no word of Kutuzov" in msg, msg
        kutuzov = world.marshals["Kutuzov"]
        world.get_region_intel(kutuzov.location).refresh(
            "full", "scout", int(world.current_turn),
            marshals=[{"name": "Kutuzov", "nation": "Russia", "strength": int(kutuzov.strength)}],
            total_strength=int(kutuzov.strength))
        msg = post(client, "where are the Russians?").get("message", "")
        assert f"Kutuzov at {kutuzov.location} ({int(kutuzov.strength):,} men, confirmed)" in msg, msg

    def test_the_enemy_is_every_court_at_war(self, shipped):
        client, world = shipped
        msg = post(client, "where is the enemy?").get("message", "")
        assert "Austria: " in msg and "Britain: " in msg and "Russia: " in msg, msg

    def test_the_alarm(self, shipped):
        client, world = shipped
        from backend.game_logic.coalition import displayed_threat
        level = int(displayed_threat(world))
        for q in ("why is Europe alarmed?", "how alarmed is Europe?",
                  "what is the threat level?"):
            msg = post(client, q).get("message", "")
            assert msg.startswith(f"Europe's alarm stands at {level} — "), (q, msg)
            assert "the Diplomatic Ledger (press D)" in msg

    def test_lever_down_shrugs(self, shipped, monkeypatch):
        from backend.ai import question_desk as QD
        monkeypatch.setattr(QD, "THE_DESK_PLACES_A_COURT", False)
        monkeypatch.setattr(QD, "THE_DESK_READS_THE_ALARM", False)
        client, world = shipped
        assert not post(client, "where are the Russians?").get("message", "").startswith("Sire — Russia:")
        assert "Europe's alarm stands" not in post(client, "why is Europe alarmed?").get("message", "")
