"""Row EP, slice F1 — "The first ten minutes" (`docs/ENDGAME_PLAN.md` §1).

Five rows from the September 23, 2026 live review
(`docs/audits/PLAYTEST_LIVE_REVIEW_2026_09_23.md`, `BUG_FIXES.md`
§Live Review), each driven at the surface the player reads:

* **LV-1** — a fresh campaign (and every Continue/Load) opened on an EMPTY
  terminal: the boot help was printed and then cleared by the world swap,
  and no turn-1 dispatch existed, so the Dispatch screen said "No dispatch
  available yet" on the only turn it ever said it. Now the world is born
  with a BOOT briefing (`build_morning_dispatch(..., boot=True)`: the pure
  halves, no consuming arm), `/new_game` and `/load` carry it, and the
  client prints the briefing and then the help after every world swap.
* **LV-12** — an envoy riding an order's response swallowed the order's own
  result (Berthier's report never printed). A modal the command did not ask
  for now waits behind the command's result.
* **LV-13** — a wholly fogged enemy phase printed one sentence per court
  (nine identical lines); it is one sentence now.
* **LV-7** — "Enemy nations hold 98 regions" counted every controller that
  was not France; the courts at war hold 28.
* **LV-8** — the defensive war purpose printed the 28-name homeland on four
  surfaces; it is one sentence from one source.

The client classes drive the REAL `main.tscn` headlessly
(`tools/ep_f1_first_ten_minutes_harness.gd`) on payloads taken from the real
endpoints; they skip without the engine, and a skip is not a pass — which is
why every payload fact is also pinned engine-free above them.
"""

import contextlib
import copy
import io
import json
import os
import random
import re
import subprocess

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.ai.first_contact import CABINET_DOOR, THREE_DOORS
from backend.commands.parser import CommandParser
from backend.game_logic import dispatch as D
from backend.game_logic import war_status as WS
from backend.game_logic.diplomacy import build_war_context_snapshot
from backend.models.world_state import WorldState
from tests import _chip_census as C

REPO = C.REPO
PROJECT = C.PROJECT
HARNESS = REPO / "tools" / "ep_f1_first_ten_minutes_harness.gd"
MAIN_GD = C.SCRIPTS / "main.gd"
FIXTURES = REPO / "tests" / "fixtures" / "playtest_saves"

HOMELAND_SENTENCE = "the homeland — 28 of 28 provinces held"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(autouse=True)
def _restore_active_world():
    """Whatever world, game_state and parser were active before a test are
    active again after it (the IGR-F hazard: a world left behind leaks into
    the next file)."""
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


@pytest.fixture
def board(monkeypatch):
    """The shipped 1805 boot, the mock parser, a client."""
    C.board_env(monkeypatch)
    return TestClient(M.app)


def _post(client, path, body=None):
    with _quiet():
        return client.post(path, json=body or {}).json()


def _new_game(client):
    response = _post(client, "/new_game")
    assert response["success"], response.get("message")
    M.parser = CommandParser(use_real_llm=False)
    return response


def _scenario_world():
    """The shipped 1805 opening, built directly (the path `/new_game` boots
    when no scenario env is set — `board_env` clears it; this helper must not
    depend on the suite's `SOVEREIGN_SCENARIO=none` pin)."""
    with _quiet():
        return WorldState.from_scenario(str(M._DEFAULT_SCENARIO_PATH))


def _refresh(world):
    with _quiet():
        world.calculate_visibility()
        world.invalidate_active_nations_cache()


# ═══════════════════════════════════════════════════════════════════════════
# LV-1 (b) — the first morning has a briefing
# ═══════════════════════════════════════════════════════════════════════════
class TestTheFirstMorningHasABriefing:

    def test_a_new_campaign_is_born_with_its_briefing(self, board):
        response = _new_game(board)
        briefing = response["morning_dispatch"]
        assert briefing["turn"] == 1
        for section in ("situation", "marshals", "intelligence",
                        "war_objectives", "coalition_status", "berthier_note"):
            assert section in briefing, section
        assert briefing["marshals"], "the marshal status is part of the pure half"
        # Stored, so the Dispatch screen (R) finds it: the "No dispatch
        # available yet" arm is unreachable on a live world.
        assert M.world.last_morning_dispatch["turn"] == 1
        got = board.get("/dispatch").json()["dispatch"]
        assert got == briefing

    def test_the_first_morning_names_the_doors(self, board):
        today = _new_game(board)["morning_dispatch"]["today"]
        assert today["doors"] == THREE_DOORS
        assert today["cabinet"] == CABINET_DOOR
        assert today["orders"], "the board always has an order to give on turn 1"
        assert len(today["orders"]) <= D.FIRST_MORNING_ORDER_LIMIT

    def test_every_order_the_first_morning_names_is_taken(self, board):
        """The TODAY section says "Orders the board will take at once" —
        so each one is sent, as printed, to a fresh copy of the board."""
        orders = _new_game(board)["morning_dispatch"]["today"]["orders"]
        for line in orders:
            _new_game(board)
            reply = _post(board, "/command", {"command": line})
            assert reply["success"], (line, reply.get("message"))

    def test_only_the_boot_briefing_carries_today(self, board):
        _new_game(board)
        with _quiet():
            turn_two = D.build_morning_dispatch(M.world)
        assert "today" not in turn_two

    def test_the_process_boot_world_is_born_with_one_too(self, board):
        """The import-time road (`_reset_world_state()` with no request) —
        the world "Return to the War Room" and a bare launch connect to."""
        with _quiet():
            M._reset_world_state()
        assert M.world.last_morning_dispatch.get("turn") == 1
        assert "today" in M.world.last_morning_dispatch

    def test_lever_down_no_briefing(self, board, monkeypatch):
        monkeypatch.setattr(D, "THE_FIRST_MORNING_HAS_A_BRIEFING", False)
        response = _new_game(board)
        assert response["morning_dispatch"] == {}
        assert M.world.last_morning_dispatch == {}


# ═══════════════════════════════════════════════════════════════════════════
# LV-1 — the boot briefing consumes nothing
# ═══════════════════════════════════════════════════════════════════════════
class TestTheBootBriefingConsumesNothing:

    def test_the_new_world_differs_from_a_fresh_one_only_by_its_briefing(self, board):
        _new_game(board)
        born = copy.deepcopy(M.world.to_dict())
        fresh = copy.deepcopy(_scenario_world().to_dict())
        differ = sorted(k for k in set(born) | set(fresh) if born.get(k) != fresh.get(k))
        assert differ == ["last_morning_dispatch"], differ

    def test_the_first_real_morning_reads_the_same(self, board):
        """The next real dispatch built on a world that had its boot briefing
        equals the one built on the same world without it."""
        briefed = _scenario_world()
        plain = _scenario_world()
        with _quiet():
            D.build_morning_dispatch(briefed, boot=True)
            a = D.build_morning_dispatch(briefed)
            b = D.build_morning_dispatch(plain)
        assert a == b

    def test_no_consuming_arm_is_called(self, monkeypatch):
        world = _scenario_world()

        def _forbidden(name):
            def _raise(*args, **kwargs):
                raise AssertionError(f"the boot briefing called {name}")
            return _raise

        for name in ("_check_talleyrand_session6", "_build_talleyrand_report",
                     "_build_turn_limit_warning", "_build_defeat_imminent_warning",
                     "_build_diplomatic_events_section",
                     "_build_relation_change_events"):
            monkeypatch.setattr(D, name, _forbidden(name))
        with _quiet():
            briefing = D.build_morning_dispatch(world, boot=True)
        assert briefing["talleyrand_report"] == []
        assert briefing["diplomatic_events"] == []
        assert briefing["talleyrand_discovery"] is None

    def test_a_queued_event_waits_for_the_first_real_morning(self):
        world = _scenario_world()
        D.queue_dispatch_event(world, "diplomatic_coalition_dissolved", {}, "always")
        queued = list(world.pending_dispatch_events)
        with _quiet():
            D.build_morning_dispatch(world, boot=True)
        assert world.pending_dispatch_events == queued
        with _quiet():
            real = D.build_morning_dispatch(world)
        assert any(e["type"] == "diplomatic_coalition_dissolved"
                   for e in real["diplomatic_events"])
        assert world.pending_dispatch_events == []

    def test_talleyrand_spends_no_cooldown(self):
        """Control first: on the 1805 boot the real report fires Hesse's
        `acceptance_crossed` and writes its 10-turn cooldown."""
        control = _scenario_world()
        with _quiet():
            D.build_morning_dispatch(control)
        assert control.proactive_suggestion_cooldowns, "control: the real report writes"
        world = _scenario_world()
        with _quiet():
            D.build_morning_dispatch(world, boot=True)
        assert world.proactive_suggestion_cooldowns == {}

    def test_the_expectation_latch_waits(self, monkeypatch):
        from backend.game_logic import dotation
        monkeypatch.setattr(dotation, "get_expectation",
                            lambda m, *a, **k: 500 if m.name == "Ney" else 0)
        world = _scenario_world()
        ney = world.get_marshal("Ney")
        with _quiet():
            briefing = D.build_morning_dispatch(world, boot=True)
        assert int(getattr(ney, "last_expectation_seen", 0)) == 0
        assert briefing["situation"]["expectation_rises"] == []
        with _quiet():
            real = D.build_morning_dispatch(world)
        assert ney.last_expectation_seen == 500, "control: the real dispatch latches"
        assert [r["marshal"] for r in real["situation"]["expectation_rises"]] == ["Ney"]

    def test_the_headline_memory_is_read_not_written(self):
        world = _scenario_world()
        world.headline_lead_memory = {"class": "x", "identity": "y", "streak": 3}
        candidates = [{"class": "region_taken", "identity": "region_taken:Paris",
                       "weight": 60, "text": "Paris taken.", "fields": {}}]
        D._select_headline(world, list(candidates), record=False)
        assert world.headline_lead_memory == {"class": "x", "identity": "y", "streak": 3}
        D._select_headline(world, list(candidates))
        assert world.headline_lead_memory["identity"] == "region_taken:Paris"

    def test_a_boot_headline_leaves_the_lead_memory_alone(self):
        """Through the builder, on a board that HAS a lead (Paris fallen)."""
        def _paris_fallen():
            world = _scenario_world()
            world.regions["Paris"].controller = "Austria"
            world.invalidate_active_nations_cache()
            world.log_event({"type": "region_captured", "region": "Paris",
                             "captured_by": "Austria", "captured_from": "France"})
            return world

        world = _paris_fallen()
        with _quiet():
            briefing = D.build_morning_dispatch(world, boot=True)
        assert briefing.get("headline"), "the board must offer a lead"
        assert not world.headline_lead_memory
        control = _paris_fallen()
        with _quiet():
            D.build_morning_dispatch(control)
        assert control.headline_lead_memory, "control: the real dispatch records its lead"

    def test_the_rail_is_not_written(self):
        world = _scenario_world()
        before = json.dumps(world.notifications.get_pending(), sort_keys=True, default=str)
        with _quiet():
            D.build_morning_dispatch(world, boot=True)
        after = json.dumps(world.notifications.get_pending(), sort_keys=True, default=str)
        assert before == after

    def test_no_module_dice_are_drawn(self):
        world = _scenario_world()
        random.seed(20260923)
        state = random.getstate()
        with _quiet():
            D.build_morning_dispatch(world, boot=True)
        assert random.getstate() == state


# ═══════════════════════════════════════════════════════════════════════════
# LV-1 (c) — the loaded turn is briefed
# ═══════════════════════════════════════════════════════════════════════════
class TestTheLoadedTurnIsBriefed:

    def test_continue_carries_the_saved_turn_one_briefing(self, board):
        born = _new_game(board)["morning_dispatch"]
        loaded = _post(board, "/load", {"filename": "autosave.json"})
        assert loaded["success"], loaded.get("message")
        assert loaded["message"].startswith("Loaded:")
        assert loaded["morning_dispatch"] == born

    def test_a_mid_campaign_save_carries_its_own_briefing(self, board, tmp_path, monkeypatch):
        from backend import save_manager
        monkeypatch.setattr(save_manager, "SAVE_DIR", tmp_path)
        source = FIXTURES / "fixture_t10_ambient.json"
        (tmp_path / source.name).write_bytes(source.read_bytes())
        stored = json.loads(source.read_text(encoding="utf-8"))["world_state"]["last_morning_dispatch"]
        loaded = _post(board, "/load", {"filename": source.name})
        assert loaded["success"], loaded.get("message")
        briefing = loaded["morning_dispatch"]
        assert briefing["turn"] == stored["turn"] == M.world.current_turn
        assert "today" not in briefing, "a stored briefing is never rebuilt as a boot one"
        assert briefing["berthier_note"] == stored["berthier_note"]

    def test_a_save_without_a_briefing_is_given_the_boot_one(self, board, tmp_path, monkeypatch):
        from backend import save_manager
        monkeypatch.setattr(save_manager, "SAVE_DIR", tmp_path)
        _new_game(board)
        M.world.last_morning_dispatch = {}
        with _quiet():
            saved = save_manager.save_game(M.world, "f1_no_briefing")
        assert saved["success"], saved["message"]
        loaded = _post(board, "/load", {"filename": "f1_no_briefing.json"})
        assert loaded["success"], loaded.get("message")
        assert loaded["morning_dispatch"]["turn"] == 1
        assert "today" in loaded["morning_dispatch"]
        assert M.world.last_morning_dispatch == loaded["morning_dispatch"]


# ═══════════════════════════════════════════════════════════════════════════
# LV-7 — the courts at war
# ═══════════════════════════════════════════════════════════════════════════
class TestTheCourtsAtWar:

    def test_the_boot_count_is_the_courts_at_war(self):
        world = _scenario_world()
        situation = D._build_situation(world, "France")
        at_war = sorted(world.get_nations_at_war_with("France"))
        assert at_war == ["Austria", "Britain", "Russia"]
        held = sum(len(world.get_nation_regions(n)) for n in at_war)
        assert situation["enemy_regions"] == held == 28
        assert situation["enemy_regions_are_at_war"] is True

    def test_a_court_at_peace_is_not_counted_until_war(self):
        world = _scenario_world()
        before = D._build_situation(world, "France")["enemy_regions"]
        prussia = len(world.get_nation_regions("Prussia"))
        assert prussia > 0
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "WAR"
        after = D._build_situation(world, "France")["enemy_regions"]
        assert after == before + prussia

    def test_lever_down_counts_every_other_controller(self, monkeypatch):
        monkeypatch.setattr(D, "ONLY_THE_COURTS_AT_WAR_ARE_COUNTED", False)
        world = _scenario_world()
        situation = D._build_situation(world, "France")
        assert situation["enemy_regions"] == 98
        assert "enemy_regions_are_at_war" not in situation

    def test_the_legacy_fixture_keeps_its_count(self):
        """N1: the 19-region rollback world is byte-identical."""
        world = WorldState(player_nation="France")
        situation = D._build_situation(world, "France")
        others = sum(1 for r in world.regions.values()
                     if r.controller not in (None, "France"))
        assert situation["enemy_regions"] == others
        assert "enemy_regions_are_at_war" not in situation


# ═══════════════════════════════════════════════════════════════════════════
# LV-8 — the purpose is one sentence
# ═══════════════════════════════════════════════════════════════════════════
def _defense_lines(world):
    return [row["text"] for row in D._build_war_objective_section(world, "France")
            if row["objective_type"] == "defense"]


def _lose_homeland(world, keep):
    home = list(world.nation_starting_regions["France"])
    for name in home:
        if name not in keep:
            world.regions[name].controller = "Austria"
    world.invalidate_active_nations_cache()
    return home


class TestThePurposeIsOneSentence:

    def test_the_boot_purpose_is_one_sentence(self):
        world = _scenario_world()
        lines = _defense_lines(world)
        assert sorted(re.search(r"vs (\w+)", t).group(1) for t in lines) == [
            "Austria", "Britain", "Russia"]
        for text in lines:
            assert f"— {HOMELAND_SENTENCE}  |  Settlement:" in text, text
            for name in world.nation_starting_regions["France"]:
                assert name not in text, (name, text)
            assert "[HELD]" not in text

    def test_a_partial_hold_is_counted(self):
        world = _scenario_world()
        home = _lose_homeland(world, keep=())
        for name in home[:20]:
            world.regions[name].controller = "France"
        world.invalidate_active_nations_cache()
        for text in _defense_lines(world):
            assert "the homeland — 20 of 28 provinces held" in text, text

    def test_a_rump_names_no_province_it_lost(self):
        world = _scenario_world()
        _lose_homeland(world, keep=("Brittany",))
        for text in _defense_lines(world):
            assert "the homeland — 1 of 28 provinces held" in text, text
            assert "Paris" not in text

    def test_a_fallen_homeland_is_lost(self):
        world = _scenario_world()
        _lose_homeland(world, keep=())
        for text in _defense_lines(world):
            assert text.startswith("War Purpose: Defense vs ")
            assert "— the homeland is lost  |  Settlement:" in text, text

    def test_any_other_list_names_eight(self):
        world = _scenario_world()
        targets = sorted(name for name, region in world.regions.items()
                         if region.controller != "France")[:10]
        assert len(targets) == 10
        objective = {"type": "conquest", "target_regions": targets}
        summary = WS.objective_target_summary(world, "France", objective)
        assert summary == ", ".join(targets[:8]) + ", and 2 more"
        assert WS.objective_target_summary(
            world, "France", {"type": "conquest", "target_regions": targets[:3]}
        ) == ", ".join(targets[:3])

    def test_the_dispatch_line_names_eight(self):
        world = _scenario_world()
        targets = sorted(name for name, region in world.regions.items()
                         if region.controller == "Austria") + ["Swabia", "Franconia", "Lorraine"]
        key = world._make_diplo_key("France", "Austria")
        world.war_objectives[key]["France"] = dict(
            world.war_objectives[key]["France"], type="conquest",
            target_regions=targets)
        line = next(row["text"] for row in D._build_war_objective_section(world, "France")
                    if row["target_nation"] == "Austria")
        assert f"— {', '.join(targets[:8])}, and {len(targets) - 8} more [" in line, line
        assert targets[8] not in line

    def test_every_surface_reads_the_one_source(self, board):
        response = _new_game(board)
        rows = [w for w in response["active_wars"]["wars"] if w.get("objective")]
        assert rows, "the boot wars carry the declaration's defensive purpose"
        for row in rows:
            assert row["objective"]["target_summary"] == HOMELAND_SENTENCE
        with _quiet():
            snapshot = build_war_context_snapshot(M.world, "France", "Austria", "peace")
        assert snapshot["war_objective"]["target_summary"] == HOMELAND_SENTENCE
        texts = [row["text"] for row in response["morning_dispatch"]["war_objectives"]]
        assert all(HOMELAND_SENTENCE in text for text in texts), texts

    def test_lever_down_restores_every_list(self, board, monkeypatch):
        monkeypatch.setattr(WS, "THE_PURPOSE_IS_ONE_SENTENCE", False)
        response = _new_game(board)
        for row in response["active_wars"]["wars"]:
            if row.get("objective"):
                assert "target_summary" not in row["objective"]
        with _quiet():
            snapshot = build_war_context_snapshot(M.world, "France", "Austria", "peace")
        assert "target_summary" not in snapshot["war_objective"]
        for text in _defense_lines(M.world):
            assert "Paris" in text and "[HELD]" in text

    def test_the_legacy_fixture_keeps_its_list(self):
        world = WorldState(player_nation="France")
        assert WS.objective_target_summary(
            world, "France", {"type": "defense",
                              "target_regions": list(world.regions)[:3]}) == ""


# ═══════════════════════════════════════════════════════════════════════════
# LV-13 — a wholly fogged enemy phase is one sentence
# ═══════════════════════════════════════════════════════════════════════════
def _fogged_phase(world, monkeypatch, nations):
    def _hide_everything(phase, _world):
        phase["nations"] = {}
        phase["total_actions"] = 0
        return phase

    monkeypatch.setattr(M, "_filter_enemy_phase_by_visibility", _hide_everything)
    monkeypatch.setattr(M, "_collapse_enemy_move_chains", lambda phase, _w: phase)
    raw = {"nations": {n: {"actions": [{"message": "x"}], "action_count": 1}
                       for n in nations},
           "total_actions": len(nations)}
    with _quiet():
        return M._build_visible_enemy_phase(raw, world)


NINE = ["Britain", "Russia", "Prussia", "Ottoman", "PapalStates",
        "Sweden", "Portugal", "Naples", "Denmark"]


class TestTheFogIsOneSentence:

    def test_nine_fogged_courts_are_one_line(self, monkeypatch):
        world = _scenario_world()
        out = _fogged_phase(world, monkeypatch, NINE)
        assert out["fog_hidden_summary"] == [
            "Britain, Russia, Prussia and 6 other courts stirred, "
            "but their formations remain beyond our sight."]

    def test_one_fogged_court_keeps_its_own_sentence(self, monkeypatch):
        world = _scenario_world()
        out = _fogged_phase(world, monkeypatch, ["Ottoman"])
        assert out["fog_hidden_summary"] == [
            "Our scouts report activity within the borders of the Ottoman "
            "Empire, but their formations remain beyond our sight."]

    def test_lever_down_one_line_per_court(self, monkeypatch):
        monkeypatch.setattr(M, "THE_FOG_IS_ONE_SENTENCE", False)
        world = _scenario_world()
        out = _fogged_phase(world, monkeypatch, NINE)
        assert len(out["fog_hidden_summary"]) == 9


# ═══════════════════════════════════════════════════════════════════════════
# LV-12 — the route table: which modals wait behind the order's result
# ═══════════════════════════════════════════════════════════════════════════
RESULT_FIRST = {"commitment_paradox", "marshal_petition", "incoming_proposal",
                "incoming_settlement_offer", "diplomatic_sabotage",
                "vassal_rebellion",
                # LV-22 (row EP F3): the capture IS asked for, and its question
                # still waits behind Berthier's report — pin flipped consciously.
                "capture_choice"}


def _post_hud_block():
    source = MAIN_GD.read_text(encoding="utf-8")
    start = source.index("_post_hud_response_routes = [")
    return source[start:source.index("]", start)]


class TestTheRouteTable:

    def test_the_modals_the_command_did_not_ask_for_wait(self):
        marked = set(re.findall(r'\{"id": "(\w+)"[^}]*"result_first": true\}',
                                _post_hud_block()))
        assert marked == RESULT_FIRST

    def test_the_command_path_passes_the_renderer(self):
        source = MAIN_GD.read_text(encoding="utf-8")
        start = source.index("func _on_command_result(")
        body = source[start:source.index("\nfunc ", start + 10)]
        assert ("if _route_response_ui(response, _post_hud_response_routes, "
                "_render_own_result):") in body


# ═══════════════════════════════════════════════════════════════════════════
# The client, DRIVEN (LV-1 a/c, LV-12, LV-7 and LV-8 on screen)
# ═══════════════════════════════════════════════════════════════════════════
ARMISTICE_ENVOY = {
    "source": "Austria", "recipient": "France", "proposal_type": "armistice",
    "priority": 1,
    "terms": {"type": "armistice", "proposer_nation": "Austria",
              "target_nation": "France", "clauses": ["armistice"],
              "sweeteners": [], "demands": []},
    "talleyrand_assessment": "", "decision_reason": "war_weariness",
    "turn_generated": 1,
}


def _payloads():
    """Real payloads from the real endpoints, one fresh board each."""
    client = TestClient(M.app)
    new_game = _new_game(client)
    topology = client.get("/map_topology").json()
    load = _post(client, "/load", {"filename": "autosave.json"})
    dispatch = client.get("/dispatch").json()["dispatch"]
    war_row = next(w for w in new_game["active_wars"]["wars"] if w.get("objective"))
    with _quiet():
        snapshot = build_war_context_snapshot(M.world, "France", "Austria", "peace")
    # LV-12's reproduction: Austria's envoy is delivered, then the order.
    _new_game(client)
    from backend.game_logic import ai_diplomacy
    with _quiet():
        ai_diplomacy.deliver_ai_proposal(copy.deepcopy(ARMISTICE_ENVOY), M.world)
    random.seed(5)
    attack = _post(client, "/command", {"command": "Ney, attack Mack"})
    return {"new_game": new_game, "topology": topology, "load": load,
            "dispatch": dispatch, "war_row": war_row, "snapshot": snapshot,
            "attack": attack}


@pytest.fixture(scope="module")
def payloads():
    with pytest.MonkeyPatch.context() as mp:
        C.board_env(mp)
        prior = (M.world, M.game_state.get("world"), M.parser)
        try:
            return _payloads()
        finally:
            M.world, M.parser = prior[0], prior[2]
            M.game_state["world"] = prior[1]


@pytest.fixture(scope="module")
def driven(payloads, tmp_path_factory):
    exe = C.engine()
    if exe is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    work = tmp_path_factory.mktemp("epf1")
    out = work / "out.json"
    log = work / "godot.log"
    spec = work / "spec.json"
    spec.write_text(json.dumps(dict(payloads, out=str(out))), encoding="utf-8")
    env = dict(os.environ, EPF1_SPEC=str(spec))
    proc = subprocess.run(
        [exe, "--headless", "--path", str(PROJECT), "--log-file", str(log),
         "--script", str(HARNESS)],
        capture_output=True, text=True, timeout=300, env=env, cwd=str(PROJECT))
    if not out.is_file():
        pytest.fail("the harness wrote no result\n"
                    f"exit={proc.returncode}\nstderr tail:\n{proc.stderr[-2000:]}")
    result = json.loads(out.read_text(encoding="utf-8"))
    assert "error" not in result, result.get("error")
    text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    result["script_errors"] = text.count("SCRIPT ERROR")
    return result


class TestTheHarnessIsParsed:
    """A driven pin whose harness does not parse fails with no output rather
    than naming the line — so the harness rides the parse check (CN-3's
    convention, `tools/godot_parse_check.gd` TOOL_SCRIPTS)."""

    def test_the_harness_is_in_the_parse_check(self):
        source = (REPO / "tools" / "godot_parse_check.gd").read_text(encoding="utf-8")
        start = source.index("const TOOL_SCRIPTS = [")
        block = source[start:source.index("]", start)]
        assert '"res://../../tools/ep_f1_first_ten_minutes_harness.gd"' in block

    def test_the_committed_report_parsed_it(self):
        report = json.loads((REPO / "tools" / "godot_parse_report.json").read_text(encoding="utf-8"))
        entry = next(s for s in report["scripts"]
                     if str(s.get("path", "")).endswith("ep_f1_first_ten_minutes_harness.gd"))
        assert entry["parse_ok"] and entry["load_ok"], entry


class TestThePayloadsAreTheReproduction:
    """Engine-free: the facts the driven pins stand on."""

    def test_the_attack_carries_its_report_and_the_envoy(self, payloads):
        attack = payloads["attack"]
        assert attack["success"]
        assert attack["events"][0]["type"] == "battle"
        assert attack.get("battle_report")
        assert (attack.get("incoming_proposal") or {}).get("from_nation") == "Austria"
        # No route the command DID ask for stands in front of the envoy.
        for key in ("pending_capture_choice", "pending_interrupt",
                    "pending_objection", "diplomatic_objection"):
            assert not attack.get(key), key

    def test_the_world_swaps_carry_the_briefing(self, payloads):
        assert payloads["new_game"]["morning_dispatch"]["turn"] == 1
        assert payloads["load"]["morning_dispatch"] == payloads["new_game"]["morning_dispatch"]


class TestTheClientDriven:

    def test_the_harness_ran_clean(self, driven):
        assert driven["script_errors"] == 0

    def test_begin_shows_the_briefing_then_the_help(self, driven, payloads):
        text = driven["new_game_terminal"]
        assert "New campaign ready." in text
        brief = text.index("MORNING DISPATCH — Turn 1")
        today = text.index("TODAY", brief)
        help_at = text.index("Your marshals await your orders, Sire.", today)
        assert brief < today < help_at
        for order in payloads["new_game"]["morning_dispatch"]["today"]["orders"]:
            assert order in text, order
        assert THREE_DOORS in text

    def test_continue_shows_the_loaded_turns_briefing(self, driven):
        text = driven["load_terminal"]
        loaded = text.index("Loaded: ")
        brief = text.index("MORNING DISPATCH — Turn 1", loaded)
        assert text.index("Your marshals await your orders, Sire.", brief) > brief
        assert "New campaign ready." not in text, "the load cleared the terminal first"

    def test_the_orders_result_prints_before_the_envoy(self, driven, payloads):
        text = driven["attack_terminal"]
        assert "--- Berthier's Report ---" in text
        muster_line = payloads["attack"]["message"].splitlines()[0]
        assert muster_line[:40] in text
        assert driven["attack_envoy_raised"] is True
        assert driven["attack_modal_open"] is True

    def test_the_courts_at_war_on_both_surfaces(self, driven):
        for key in ("new_game_terminal", "dispatch_view_text"):
            assert "The courts at war hold 28 regions." in driven[key], key
            assert "Enemy nations hold" not in driven[key], key

    def test_the_purpose_is_one_sentence_on_every_surface(self, driven):
        for key in ("new_game_terminal", "dispatch_view_text", "war_tooltip",
                    "war_detail_text", "incoming_summary", "confirm_summary"):
            assert HOMELAND_SENTENCE in driven[key], key
            assert "Berry, Artois" not in driven[key], key
        assert f"Objective: Defense - {HOMELAND_SENTENCE}" in driven["war_tooltip"]

    def test_the_dispatch_screen_renders_the_first_morning(self, driven, payloads):
        text = driven["dispatch_view_text"]
        assert "TODAY" in text
        for order in payloads["dispatch"]["today"]["orders"]:
            assert order in text, order
        assert "No dispatch available yet" not in text
