"""SR-2b — "The Talleyrand verbs" (Score Mandate Chunk 2 DIPLOMACY,
September 26, 2026; `docs/SCORE_MANDATE_PLAN.md` §2 Chunk 2; rows
`BUG_FIXES.md` AAR-20, AAR-21; CRT-8's mission half).

AAR-20a — "recall Talleyrand" recalls (the recall vocabulary is the CANCEL
          mission inside the diplomat-addressed parse; `recall Murat` and
          `recall the fleet` keep their own roads).
AAR-20b — the open nation list may claim a line only when the line IS the
          court; the resolver matches courts as whole words. The recon
          overturned the row's diagnosis: the running mission was never the
          cause — the list left open by the previous command claimed the
          order by substring, and the resolver matched "russia" inside
          "Prussia".
AAR-21  — the Cabinet's rules on the typed road: a mission is offered on
          both roads or neither (`mission_state_refusal` mirrors the wizard's
          per-state rows), read BEFORE the price.
"""
from __future__ import annotations

import contextlib
import io
from pathlib import Path

import pytest

import backend.commands.dialogue_routing as DR
import backend.game_logic.diplomatic_dialogue as DD
import backend.main as M
from backend.ai.llm_client import LLMClient
from backend.commands.parser import CommandParser
from backend.game_logic.diplomacy import get_available_diplomatic_actions
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


def _parse(text: str):
    with _quiet():
        return LLMClient(use_real_api=False).parse_command(text)


def _diplo(text: str):
    return (_parse(text) or {}).get("diplomatic_data") or {}


@pytest.fixture
def http(monkeypatch):
    """The legacy world on the wire with the MOCK parser: Prussia and Britain
    boot at WAR, Austria at PEACE (the phase-4 fixture's own geometry)."""
    world = WorldState()
    world.diplomatic_points = 10
    world.talleyrand_defiance_cooldown = 99
    monkeypatch.setattr(M, "world", world)
    monkeypatch.setattr(M, "parser", _PARSER)
    monkeypatch.setitem(M.game_state, "world", world)
    from fastapi.testclient import TestClient
    return world, TestClient(M.app)


@pytest.fixture
def http_1805(monkeypatch):
    """The 1805 boot on the wire with the MOCK parser — the AAR's own board,
    where the executor's nation list holds Prussia AND Russia (the substring
    collision) and Russia boots at WAR."""
    with _quiet():
        world = WorldState.from_scenario(SCENARIO)
    world.diplomatic_points = 10
    world.talleyrand_defiance_cooldown = 99
    monkeypatch.setattr(M, "world", world)
    monkeypatch.setattr(M, "parser", _PARSER)
    monkeypatch.setitem(M.game_state, "world", world)
    from fastapi.testclient import TestClient
    return world, TestClient(M.app)


def _cmd(client, text):
    with _quiet():
        return client.post("/command", json={"command": text}).json()


def _respond(client, choice, dialogue_id=None):
    with _quiet():
        return client.post("/respond_to_diplomatic_dialogue",
                           json={"choice": choice, "dialogue_id": dialogue_id}).json()


# ═══════════════════════════════════════════════════════════════════════
# AAR-20a — "recall Talleyrand" recalls
# ═══════════════════════════════════════════════════════════════════════

class TestRecallTalleyrand:

    @pytest.mark.parametrize("text", [
        "recall Talleyrand",
        "Recall Talleyrand",
        "recall our envoy",
        "Talleyrand, come home",
        "bring Talleyrand home",
        "call Talleyrand back",
        "Talleyrand, return to Paris",
    ])
    def test_the_recall_words_are_the_cancel_mission(self, text):
        data = _diplo(text)
        assert data.get("mission_type") == "CANCEL", (text, data)
        assert (_parse(text) or {}).get("action") == "diplomatic_mission"

    def test_the_buttons_own_label_is_typable(self):
        assert _diplo(DD.MISSION_RECALL_LABEL).get("mission_type") == "CANCEL"

    def test_a_marshal_and_the_fleet_keep_their_own_roads(self):
        assert (_parse("recall Murat") or {}).get("action") == "recall_marshal"
        naval = (_parse("recall the fleet") or {}).get("action")
        assert naval != "diplomatic_mission"

    def test_the_typed_recall_ends_a_live_mission(self, http):
        world, client = http
        r = _cmd(client, "Talleyrand, improve relations with Austria")
        dlg = r.get("diplomatic_dialogue") or {}
        assert dlg.get("type") == "mission", r.get("message")
        actions = [o.get("action") for o in dlg.get("options", [])]
        assert "start_mission" in actions
        _respond(client, actions.index("start_mission") + 1, dlg.get("dialogue_id"))
        assert DD.mission_is_live(world)
        r2 = _cmd(client, "recall Talleyrand")
        assert r2.get("success") is True, r2.get("message")
        assert not DD.mission_is_live(world)
        assert world.talleyrand_state == "IDLE"

    def test_a_recall_with_nothing_running_says_so(self, http):
        world, client = http
        r = _cmd(client, "recall Talleyrand")
        assert r.get("success") is False
        assert "no active" in str(r.get("message", "")).lower() \
            or "nothing" in str(r.get("message", "")).lower() \
            or "mission" in str(r.get("message", "")).lower()


# ═══════════════════════════════════════════════════════════════════════
# AAR-20b — the nation list claims only the court; whole-word courts
# ═══════════════════════════════════════════════════════════════════════

def _nation_list(courts):
    return {
        "type": "proposal_options", "target_nation": "",
        "talleyrand_text": "Sire, which nation shall I approach?",
        "options": [
            {"label": c, "description": "", "action": "expand_options",
             "terms": {"target_nation": c}} for c in courts
        ],
        "context": {}, "blocking": False,
    }


class TestTheNationListClaimsOnlyTheCourt:

    def test_the_line_that_is_the_court(self):
        assert DR._line_is_only_the_court("russia", "Russia")
        assert DR._line_is_only_the_court("choose russia", "Russia")
        assert DR._line_is_only_the_court("kingdom of italy", "Kingdom of Italy")
        assert not DR._line_is_only_the_court("improve relations with russia", "Russia")
        assert not DR._line_is_only_the_court("prussia", "Russia")

    def test_an_order_naming_a_court_is_not_claimed(self):
        dlg = _nation_list(["Austria", "Prussia", "Russia"])
        assert DR.match_dialogue_answer(
            dlg, "improve relations with russia", [], world_regions=[]) is None
        assert DR.match_dialogue_answer(
            dlg, "talleyrand, propose an alliance with austria", [], world_regions=[]) is None

    def test_the_court_alone_is_claimed(self):
        dlg = _nation_list(["Austria", "Prussia", "Russia"])
        assert DR.match_dialogue_answer(dlg, "russia", [], world_regions=[]) == "russia"
        assert DR.match_dialogue_answer(dlg, "choose russia", [], world_regions=[]) == "russia"

    def _open_the_list(self, client):
        """A nation-less overture reaches the executor's no-target branch,
        which answers with the nation list — the very branch the pre-SR-2b
        `recall Talleyrand` fell into (the AAR, turn 11: "which nation shall
        I approach?"). The recall is a CANCEL now, so the list is opened
        here by a sentence that still asks for a court."""
        r = _cmd(client, "Talleyrand, open talks")
        dlg = r.get("diplomatic_dialogue") or {}
        assert dlg.get("type") == "proposal_options", r.get("message")
        labels = [o.get("label") for o in dlg.get("options", [])]
        assert "Prussia" in labels and "Russia" in labels, labels
        assert labels.index("Prussia") < labels.index("Russia")
        return dlg

    def test_the_wire_answers_for_the_court_named(self, http_1805):
        """The AAR's line: the list open from the previous command,
        `improve relations with Russia` typed — the order for RUSSIA runs
        (the mission confirm), not Prussia's proposal menu. Russia stands at
        ARMISTICE, as it did on the AAR's turn 11."""
        world, client = http_1805
        world.diplomatic_states[world._make_diplo_key("France", "Russia")] = "ARMISTICE"
        self._open_the_list(client)
        r2 = _cmd(client, "improve relations with Russia")
        d2 = r2.get("diplomatic_dialogue") or {}
        assert d2.get("type") == "mission", (r2.get("message"), d2.get("type"))
        assert d2.get("target_nation") == "Russia"

    def test_the_resolver_matches_courts_as_whole_words(self, http_1805):
        """Typed "russia" to the open list picks RUSSIA — the resolver's
        containment arms had matched "russia" inside "Prussia", the
        alphabetical first."""
        world, client = http_1805
        dlg = self._open_the_list(client)
        r2 = _respond(client, "russia", dlg.get("dialogue_id"))
        d2 = r2.get("diplomatic_dialogue") or {}
        assert d2.get("target_nation") == "Russia", (r2.get("message"), d2)


# ═══════════════════════════════════════════════════════════════════════
# AAR-21 — the Cabinet's rules on the typed road
# ═══════════════════════════════════════════════════════════════════════

_ROW_FOR = {
    "IMPROVE_RELATIONS": "mission_improve_relations",
    "COURT_NATION": "mission_court",
    "GATHER_INTEL": "mission_gather_intel",
    "UNDERMINE_ALLIANCE": "mission_undermine",
    "REASSURE_ALLY": "mission_reassure",
}
_STATES = ["WAR", "ARMISTICE", "PEACE", "OPEN_BORDERS", "NON_AGGRESSION",
           "DEFENSIVE_ALLIANCE", "ALLIANCE"]


def _world_with(state: str, court: str = "Austria") -> WorldState:
    w = WorldState()
    w.diplomatic_points = 10
    key = w._make_diplo_key("France", court)
    w.diplomatic_states[key] = state
    return w


class TestTheCabinetsRulesOnTheTypedRoad:

    def test_offered_on_both_roads_or_neither(self):
        """The census: for every state and every mission type, the Cabinet
        offers the row exactly when the typed road accepts the mission."""
        for state in _STATES:
            w = _world_with(state)
            with _quiet():
                rows = get_available_diplomatic_actions(w, "Austria")
            offered = {r.get("action") for r in rows}
            for mission, row in _ROW_FOR.items():
                cabinet = row in offered
                typed = DD.mission_state_refusal(w, "Austria", mission) is None
                assert cabinet == typed, (state, mission, cabinet, typed)

    def test_a_belligerent_is_not_courted(self, http):
        world, client = http          # Prussia boots at WAR
        before = int(world.diplomatic_points)
        r = _cmd(client, "Talleyrand, improve relations with Prussia")
        assert r.get("success") is False
        assert "belligerent" in str(r.get("message", "")).lower()
        assert r.get("diplomatic_dialogue") is None
        assert int(world.diplomatic_points) == before
        assert not DD.mission_is_live(world)

    def test_intelligence_is_a_mission_a_war_allows(self, http):
        world, client = http
        r = _cmd(client, "Talleyrand, gather intel on Prussia")
        dlg = r.get("diplomatic_dialogue") or {}
        assert dlg.get("type") == "mission", r.get("message")

    def test_the_ground_speaks_before_the_price(self):
        w = _world_with("WAR")
        w.diplomatic_points = 0
        from backend.commands.executor import CommandExecutor
        ex = CommandExecutor()
        r = ex._execute_diplomatic_mission(
            {"mission_type": "improve_relations", "target_nation": "Austria"}, w)
        assert r["success"] is False
        assert "belligerent" in r["message"].lower()
        assert "Insufficient" not in r["message"]

    def test_an_ally_is_reassured_not_courted(self):
        w = _world_with("ALLIANCE")
        assert DD.mission_state_refusal(w, "Austria", "IMPROVE_RELATIONS")
        assert DD.mission_state_refusal(w, "Austria", "COURT_NATION")
        assert DD.mission_state_refusal(w, "Austria", "REASSURE_ALLY") is None

    def test_reassurance_is_for_a_full_alliance_only(self):
        w = _world_with("PEACE")
        msg = DD.mission_state_refusal(w, "Austria", "REASSURE_ALLY")
        assert msg and "full alliance" in msg

    def test_a_vassal_is_governed_not_courted(self):
        w = WorldState()
        w.vassals["Saxony"] = {"lord": "France", "loyalty": 60, "autonomy": 1}
        msg = DD.mission_state_refusal(w, "Saxony", "IMPROVE_RELATIONS")
        assert msg and "client" in msg

    def test_a_recall_is_never_refused(self):
        w = _world_with("WAR")
        assert DD.mission_state_refusal(w, "Austria", "CANCEL") is None

    def test_the_lever_down_is_the_old_road(self, monkeypatch):
        monkeypatch.setattr(DD, "THE_CABINETS_RULES_ON_EVERY_ROAD", False)
        w = _world_with("WAR")
        assert DD.mission_state_refusal(w, "Austria", "IMPROVE_RELATIONS") is None

    def test_the_wizard_sends_the_typed_sentence(self):
        """The two roads meet at the typed executor: the wizard composes a
        plain command and `main.gd` sends it through `send_command`."""
        src = (REPO / "godot-client" / "project-sovereign" / "scripts"
               / "diplomacy_wizard.gd").read_text(encoding="utf-8")
        assert "improve relations with" in src
        main_src = (REPO / "godot-client" / "project-sovereign" / "scripts"
                    / "main.gd").read_text(encoding="utf-8")
        assert "send_command" in main_src
