"""Row EP, slice GE-2 — "the client" (`docs/ENDGAME_PLAN.md` §4, §6 GE-2).

The end screen — `campaign_end.tscn` (CanvasLayer 122), four registers fed by
ONE backend payload (`game_end.screen_payload`) — raised from every road an
ending arrives on by the NA-6b stash-and-raise discipline; the Fall closes the
command line for good (R3) and offers Load / Main Menu; a marked ending
(the Verdict, a Humbled Peace) is acknowledged with Continue; the exile
epilogue on the Fall register; the clock line on three surfaces from ONE
source (`fall.clock_line`); the legacy terminal text de-legacied and kept as
the fallback; the driver's END SCREEN block and its arms.

The client classes drive the REAL `main.tscn` headlessly
(`tools/ge2_campaign_end_harness.gd`) on payloads taken from the real
endpoints; they skip without the engine, and a skip is not a pass — which is
why every payload fact is also pinned engine-free above them.
"""

import contextlib
import io
import json
import os
import random
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend import save_manager as SM
from backend.game_logic import fall, game_end, ledger
from backend.models.world_state import WorldState
from tests import _chip_census as C

REPO = C.REPO
PROJECT = C.PROJECT
SCRIPTS = C.SCRIPTS
SCENES = PROJECT / "scenes"
TOOLS = REPO / "tools"
AUDITS = REPO / "docs" / "audits"
HARNESS = TOOLS / "ge2_campaign_end_harness.gd"
SCENARIO = PROJECT / "assets" / "maps" / "europe_1805.json"
FIXTURES = REPO / "tests" / "fixtures" / "playtest_saves"
FRAME_DATE = "2026_09_25"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _gd(name: str) -> str:
    return _read(SCRIPTS / f"{name}.gd")


def _func_body(src: str, name: str) -> str:
    start = src.index(f"func {name}(")
    nxt = src.find("\nfunc ", start + 10)
    return src[start:] if nxt == -1 else src[start:nxt]


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


def _boot() -> WorldState:
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


def _tick(world, n=1):
    for _ in range(n):
        world.current_turn += 1
        game_end.process_end_of_turn(world, turn_ended=world.current_turn - 1)


def _reduce_france_to(world, keep, to="Austria"):
    for region in list(world.get_nation_regions("France")):
        if region not in keep:
            world.regions[region].controller = to
    world.invalidate_active_nations_cache()


def _set(world, a, b, state, reason="ge2 test"):
    from backend.game_logic.diplomacy import set_diplomatic_state
    with _quiet():
        set_diplomatic_state(world, a, b, state, reason)


def _cede(world, regions, to="Austria"):
    with _quiet():
        return world._ratify_treaty({
            "proposer_nation": to, "target_nation": "France", "type": "peace",
            "demands": [{"type": "territory_cede", "regions": list(regions)}],
            "sweeteners": [],
        })


def _post(tc, path, body, seed=7):
    random.seed(seed)
    with _quiet():
        return tc.post(path, json=body).json()


def _get(tc, path):
    with _quiet():
        return tc.get(path).json()


def _war_room_text(world) -> str:
    """The war room ("assess our situation") as the player reads it — the
    `talleyrand_text` the IQ-2 pins read."""
    from backend.game_logic.diplomatic_advisory import _assess_situation
    result = _assess_situation(world)
    assert isinstance(result, dict) and result.get("talleyrand_text"), result
    return str(result["talleyrand_text"])


# ═══════════════════════════════════════════════════════════════════════════
# The staging helpers — shared with tools/iq10_capture_payloads.py, which
# imports this module for them (the IQ-10 convention: a frame is shot off the
# row's OWN staged board, never a hand-written payload).
# ═══════════════════════════════════════════════════════════════════════════


def stage_funeral(tc, world):
    """`Napoleon, attack Mack` at SOVEREIGN_DEATH_CHANCE_PCT = 100 — the
    command road: the war ends INSIDE the command (GE-1 review #10: no
    dispatch, no Moniteur special; the end screen is the fall's only
    surface). Returns the /command response."""
    for m in world.marshals.values():
        if m.nation == "France" and not m.is_sovereign:
            m.location = "Brittany"
    nap = world.marshals["Napoleon"]
    nap.location = "Lorraine"
    nap.strength = 60
    world._build_marshal_index()
    prior = game_end.SOVEREIGN_DEATH_CHANCE_PCT
    game_end.SOVEREIGN_DEATH_CHANCE_PCT = 100
    try:
        return _post(tc, "/command", {"command": "Napoleon, attack Mack"})
    finally:
        game_end.SOVEREIGN_DEATH_CHANCE_PCT = prior


def stage_verdict(tc, world):
    """The end turn that stamps the Verdict — a MARKED ending on the ordinary
    end-turn road (enemy phase and all)."""
    world.current_turn = int(game_end.verdict_turn(world) or 44)
    return _post(tc, "/command", {"command": "end turn"}, seed=44)


def stage_humbled(tc, world):
    """Paris signed away — the Humbled Peace stamped at the ratify seam; the
    next response carries it ONLY in `game_state.endings` (no `ending`), the
    shape the settlement road's responses have."""
    _cede(world, ["Paris"])
    return _post(tc, "/command", {"command": "status"})


def stage_soil_fall(tc, world):
    """France reduced to Brittany, five real end turns — the R1 arm on the
    wire (GE-1's own staging). Returns every response; the last carries the
    Fall."""
    _reduce_france_to(world, {"Brittany"})
    responses = []
    for i in range(8):
        r = _post(tc, "/command", {"command": "end turn"}, seed=4000 + i)
        responses.append(r)
        if r.get("game_over"):
            break
    return responses


def stage_soil_fall_one_turn(tc, world):
    """The soil clock one tick in — the briefing the R screen re-reads with
    the clock at 1 of 5 (a fallen campaign's last dispatch carries none)."""
    _reduce_france_to(world, {"Brittany"})
    return _post(tc, "/command", {"command": "end turn"}, seed=4000)


def stage_chains_payload(world):
    """The Eagle in Chains — the Emperor taken by Austria, ten ticks of war
    (the ONE per-turn caller, as GE-1's pins tick it). Returns the screen
    payload of the terminal record."""
    with _quiet():
        world.capture_marshal(world.marshals["Napoleon"], "Austria", context="ge2")
    _tick(world, 10)
    return game_end.screen_payload(game_end.terminal_ending(world))


def stage_ledger_clock(tc, world):
    """Two arms at once for the Territories tab: the realm at Brittany alone
    (the soil clock TICKING against Britain and Russia) and the Emperor a
    prisoner of Austria under a truce (the chains clock PAUSED — no date).
    Returns GET /ledger."""
    _reduce_france_to(world, {"Brittany"})
    with _quiet():
        world.capture_marshal(world.marshals["Napoleon"], "Austria", context="ge2")
    _set(world, "France", "Austria", "ARMISTICE", "ge2 staged truce")
    _tick(world, 1)
    return _get(tc, "/ledger")


# ═══════════════════════════════════════════════════════════════════════════
# The clock line — ONE source, three surfaces (backend)
# ═══════════════════════════════════════════════════════════════════════════


def _soil_world(turns=1):
    w = _boot()
    _reduce_france_to(w, {"Brittany"})
    if turns:
        _tick(w, turns)
    return w


def _arm(w, arm):
    state = fall.get_fall_state(w)
    assert state is not None
    return state["arms"][arm]


class TestTheClockLine:

    def test_a_ticking_arm_is_dated(self):
        w = _soil_world(1)
        line = fall.clock_line(w, _arm(w, fall.ARM_SOIL))
        assert line == ("THE EMPIRE WITHOUT SOIL OR SWORD — 1 of 5 · the Empire falls "
                        "at the end of turn 5 (4 turns remain)")

    def test_a_clock_at_nought_says_when_it_starts(self):
        w = _soil_world(0)
        view = _arm(w, fall.ARM_SOIL)
        assert view["falls_at_end_of_turn"] is None
        line = fall.clock_line(w, view)
        assert "0 of 5" in line and "the clock starts at this end turn" in line
        assert "end of turn" not in line

    def test_a_paused_truce_names_no_date(self):
        w = _soil_world(2)
        for court in ("Austria", "Britain", "Russia"):
            _set(w, "France", court, "ARMISTICE")
        view = _arm(w, fall.ARM_SOIL)
        assert view["ticking"] is False and view["paused_by"] == "truce"
        line = fall.clock_line(w, view)
        assert line == ("THE EMPIRE WITHOUT SOIL OR SWORD — 2 of 5 · the clock stands "
                        "still while the truce holds")
        assert "turn" not in line.split("·")[1]

    def test_a_captor_pause_names_no_date(self):
        w = _boot()
        with _quiet():
            w.capture_marshal(w.marshals["Napoleon"], "Austria", context="t")
        _tick(w, 3)
        _set(w, "France", "Austria", "ARMISTICE")
        view = _arm(w, fall.ARM_CHAINS)
        assert view["ticking"] is False and view["paused_by"] == "captor"
        assert view["falls_at_end_of_turn"] is None
        line = fall.clock_line(w, view)
        assert line == ("THE EAGLE IN CHAINS — 3 of 10 · the clock stands still — no war "
                        "with his captor")

    def test_a_ticking_chains_arm_names_the_regency(self):
        w = _boot()
        with _quiet():
            w.capture_marshal(w.marshals["Napoleon"], "Austria", context="t")
        _tick(w, 3)
        line = fall.clock_line(w, _arm(w, fall.ARM_CHAINS))
        # Taken on turn 1, three ticks: the clock reads 3 of 10 on turn 4 and
        # the tenth tick lands at the end of turn 10.
        assert line == ("THE EAGLE IN CHAINS — 3 of 10 · the regency falls at the end of "
                        "turn 10 (7 turns remain)")

    def test_a_resuming_truce_counts_this_turn(self):
        w = _soil_world(2)
        view = dict(_arm(w, fall.ARM_SOIL))
        # The verification round's shape: a truce that collapses into war at
        # THIS advance — dated, and said.
        view.update({"ticking": False, "paused_by": "truce", "truce_ends": "war",
                     "resuming": True, "falls_at_end_of_turn": 6, "turns_left": 3})
        line = fall.clock_line(w, view)
        assert line.startswith("THE EMPIRE WITHOUT SOIL OR SWORD — 2 of 5 · the truce ends "
                               "this turn and the war resumes; the Empire falls at the end "
                               "of turn 6 (3 turns remain)")

    def test_severity_is_decided_once(self):
        assert fall.clock_severity({"ticking": True, "turns_left": 3}) == "warning"
        assert fall.clock_severity({"ticking": True, "turns_left": 2}) == "critical"
        assert fall.clock_severity({"ticking": False, "resuming": True, "turns_left": 1}) == "critical"
        assert fall.clock_severity({"ticking": False, "turns_left": 1}) == "paused"

    def test_the_warning_arms_carry_the_line(self):
        w = _soil_world(1)
        warning = fall.warning_state(w)
        arm = warning["fall"]["arms"][0]
        assert arm["clock_line"] == fall.clock_line(w, _arm(w, fall.ARM_SOIL))
        assert arm["severity"] == "warning"
        # and the dispatch's own warning carries the same rows
        from backend.game_logic.turn_manager import get_defeat_imminent_state
        dispatch_warning = get_defeat_imminent_state(w)
        assert dispatch_warning["fall"]["arms"][0]["clock_line"] == arm["clock_line"]

    def test_the_ledger_carries_the_clock_only_while_an_arm_holds(self):
        w = _soil_world(1)
        payload = ledger.build_strategic_ledger(w)
        assert payload["fall_clock"]["arms"][0]["clock_line"] == fall.clock_line(
            w, _arm(w, fall.ARM_SOIL))
        standing = _boot()
        assert "fall_clock" not in ledger.build_strategic_ledger(standing)
        legacy = WorldState()
        assert "fall_clock" not in ledger.build_strategic_ledger(legacy)

    def test_the_war_room_prints_every_held_arm(self):
        w = _boot()
        _reduce_france_to(w, {"Brittany"})
        with _quiet():
            w.capture_marshal(w.marshals["Napoleon"], "Austria", context="t")
        _set(w, "France", "Austria", "ARMISTICE")
        _tick(w, 1)
        rows = fall.clock_lines(w)
        assert [r["arm"] for r in rows] == [fall.ARM_CHAINS, fall.ARM_SOIL]
        assert rows[0]["severity"] == "paused" and rows[1]["severity"] == "warning"
        text = _war_room_text(w)
        for row in rows:
            assert row["clock_line"] in text, (row["clock_line"], text)
        # the paused chains clock was NOT named here before GE-2 — the scope
        # sentence carried the soonest arm alone
        assert text.index("Our own state") < text.index(rows[0]["clock_line"])

    def test_the_three_surfaces_print_the_same_words(self):
        w = _soil_world(2)
        line = fall.clock_line(w, _arm(w, fall.ARM_SOIL))
        assert fall.warning_state(w)["fall"]["arms"][0]["clock_line"] == line
        assert ledger.build_strategic_ledger(w)["fall_clock"]["arms"][0]["clock_line"] == line
        assert line in _war_room_text(w)

    def test_lever_down_restores_the_ge1_payloads(self, monkeypatch):
        w = _soil_world(1)
        monkeypatch.setattr(fall, "THE_CLOCK_HAS_ONE_LINE", False)
        arm = fall.warning_state(w)["fall"]["arms"][0]
        assert "clock_line" not in arm and "severity" not in arm
        assert fall.clock_lines(w) == []
        assert "fall_clock" not in ledger.build_strategic_ledger(w)
        assert "1 of 5 · " not in _war_room_text(w)


# ═══════════════════════════════════════════════════════════════════════════
# The fourth register (GE-3's, declared now so the scene takes it)
# ═══════════════════════════════════════════════════════════════════════════


class TestTheFourthRegister:

    def test_imperial_peace_is_a_marked_gold_register(self):
        w = _boot()
        record = game_end.record_ending(w, "victory", game_end.CAUSE_IMPERIAL_PEACE)
        assert record["register"] == "imperial_peace"
        assert record["title"] == "THE IMPERIAL PEACE"
        assert record["cause_line"] == "Europe accepts the order of the French Empire."
        assert record["terminal"] is False and w.game_over is False
        payload = game_end.screen_payload(record)
        assert payload["kind"] == "victory" and "epilogue" not in payload["summary"]

    def test_the_three_ge1_registers_are_untouched(self):
        assert game_end.REGISTERS[game_end.CAUSE_SOIL] == "fall"
        assert game_end.REGISTERS[game_end.CAUSE_HUMBLED] == "humbled_peace"
        assert game_end.REGISTERS[game_end.CAUSE_VERDICT] == "verdict"
        assert game_end.CAUSE_IMPERIAL_PEACE not in game_end.TERMINAL_CAUSES


# ═══════════════════════════════════════════════════════════════════════════
# The payloads — the client's spec, taken off the real endpoints
# ═══════════════════════════════════════════════════════════════════════════


def _strip_keys(value, keys):
    """A deep copy with every dict key in `keys` removed at any depth — the
    enemy phase's own actions carry their tableaux too."""
    if isinstance(value, dict):
        return {k: _strip_keys(v, keys) for k, v in value.items() if k not in keys}
    if isinstance(value, list):
        return [_strip_keys(v, keys) for v in value]
    return value


def _payloads():
    work = Path(tempfile.mkdtemp(prefix="ge2_"))
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(SM, "SAVE_DIR", work)
        prior = (M.world, M.game_state.get("world"), M.parser)
        try:
            C.board_env(mp)
            tc = TestClient(M.app)
            topology = _get(tc, "/map_topology")

            C.board_env(mp)
            funeral = stage_funeral(tc, M.world)
            funeral_refusal = _post(tc, "/command", {"command": "end turn"})

            C.board_env(mp)
            verdict = stage_verdict(tc, M.world)

            C.board_env(mp)
            humbled = stage_humbled(tc, M.world)
            campaign_end = _get(tc, "/campaign_end")

            C.board_env(mp)
            fall_responses = stage_soil_fall(tc, M.world)
            final = game_end.terminal_ending(M.world)["final_save"]
            saves = _get(tc, "/saves")
            load_final = _post(tc, "/load", {"filename": Path(final).name})
            dispatch = fall_responses[0]["morning_dispatch"]

            C.board_env(mp)
            ledger_payload = stage_ledger_clock(tc, M.world)
        finally:
            M.world, M.parser = prior[0], prior[2]
            M.game_state["world"] = prior[1]
    # The Verdict without the turn's battle tableau riding it: the tail must
    # raise the card itself (with a tableau, the diorama's own dismissal hands
    # the raise on and would mask a tail that never raised).
    verdict_plain = _strip_keys(verdict, {"battle_diorama", "naval_diorama", "jealousy_attacks"})
    return {"topology": topology, "funeral": funeral, "funeral_refusal": funeral_refusal,
            "verdict": verdict, "verdict_plain": verdict_plain,
            "humbled": humbled, "campaign_end": campaign_end,
            "fall_responses": fall_responses, "load_final": load_final,
            "dispatch": dispatch, "ledger": ledger_payload, "saves": saves}


@pytest.fixture(scope="module")
def payloads():
    return _payloads()


class TestThePayloadsAreTheReproduction:

    def test_the_command_road_death_has_no_dispatch_and_the_funeral(self, payloads):
        r = payloads["funeral"]
        assert r["success"] is True and r["game_over"] is True
        assert r["game_state"]["game_over"] is True
        assert "morning_dispatch" not in r        # the war ended inside the command
        assert r["ending"]["register"] == "fall" and r["ending"]["terminal"] is True
        assert r["ending"]["cause"] == game_end.CAUSE_EAGLE_FALLS
        assert r["ending"]["summary"]["epilogue"]["variant"] == "funeral"
        assert r["ending"]["summary"]["verdict"]["tier"] == "eclipse"
        refusal = payloads["funeral_refusal"]
        assert refusal["success"] is False and refusal["game_over"] is True
        assert refusal["ending"]["cause"] == game_end.CAUSE_EAGLE_FALLS

    def test_the_verdict_rides_the_end_turn_road(self, payloads):
        r = payloads["verdict"]
        assert r["ending"]["cause"] == game_end.CAUSE_VERDICT
        assert r["ending"]["terminal"] is False and not r.get("game_over")
        assert r.get("enemy_phase") is not None
        assert r["ending"]["summary"]["verdict"]["title"]

    def test_the_humbled_peace_is_named_only_in_the_compact_list(self, payloads):
        r = payloads["humbled"]
        assert "ending" not in r
        causes = [e["cause"] for e in r["game_state"]["endings"]]
        assert causes == [game_end.CAUSE_HUMBLED]
        ge = payloads["campaign_end"]
        assert [e["cause"] for e in ge["endings"]] == [game_end.CAUSE_HUMBLED]
        assert ge["endings"][0]["summary"]["epilogue"]["variant"] == "humbled"
        assert ge["endings"][0]["register"] == "humbled_peace"

    def test_a_final_save_loads_with_its_ending(self, payloads):
        r = payloads["load_final"]
        assert r["success"] is True and r["game_over"] is True
        assert r["ending"]["cause"] == game_end.CAUSE_SOIL and r["ending"]["terminal"] is True
        assert r["ending"]["summary"]["epilogue"]["variant"] == "abdication"
        names = [s["metadata"]["save_name"] for s in payloads["saves"]["saves"]]
        assert any(n.startswith("Final — ") for n in names)

    def test_the_dispatch_and_the_ledger_carry_the_clock(self, payloads):
        arms = payloads["dispatch"]["defeat_imminent_warning"]["fall"]["arms"]
        assert arms and all(a["clock_line"] and a["severity"] for a in arms)
        assert "1 of 5 · the Empire falls at the end of turn" in arms[0]["clock_line"]
        clock = payloads["ledger"]["ledger"]["fall_clock"]["arms"]
        by_arm = {a["arm"]: a for a in clock}
        assert by_arm[fall.ARM_CHAINS]["severity"] == "paused"
        assert by_arm[fall.ARM_CHAINS]["falls_at_end_of_turn"] is None
        assert "the clock stands still" in by_arm[fall.ARM_CHAINS]["clock_line"]
        assert "end of turn" in by_arm[fall.ARM_SOIL]["clock_line"]


# ═══════════════════════════════════════════════════════════════════════════
# The client — static pins (the wiring that must exist)
# ═══════════════════════════════════════════════════════════════════════════


class TestTheSceneAndItsWiring:

    def test_the_scene_sits_on_layer_122_and_is_registered(self):
        scene = _read(SCENES / "campaign_end.tscn")
        assert "layer = 122" in scene
        assert 'script = ExtResource("1_script")' in scene
        main = _gd("main")
        assert 'dialog_manager.register("campaign_end", "res://scenes/campaign_end.tscn")' in main
        for sig in ("continued", "load_requested", "main_menu_requested"):
            assert f"campaign_end.{sig}.connect(" in main
        assert "122: campaign_end" in _gd("dialog_manager")

    def test_the_four_registers_and_their_buttons(self):
        gd = _gd("campaign_end")
        for reg in ("fall", "humbled_peace", "verdict", "imperial_peace"):
            assert f'"{reg}": {{' in gd
        assert '"primary": "Load a campaign"' in gd and '"secondary": "Main Menu"' in gd
        assert '"primary": "Continue the reign"' in gd
        assert '"secondary": "Retire to the Tuileries"' in gd
        assert "Utils.clamp_centered_panel($PanelContainer)" in gd
        assert "content_label.mouse_filter = Control.MOUSE_FILTER_PASS" in gd

    def test_the_fall_takes_no_reflex_escape(self):
        body = _func_body(_gd("campaign_end"), "esc_control")
        assert "if is_terminal():" in body and "return null" in body

    def test_every_response_is_stashed_before_its_handler(self):
        api = _gd("api_client")
        assert "signal response_received(data)" in api
        emit_at = api.index("response_received.emit(json.data)")
        callback_at = api.index("callback.call(json.data)", emit_at)
        assert emit_at < callback_at
        assert "func get_campaign_end(callback: Callable):" in api
        main = _gd("main")
        assert "api_client.response_received.connect(_stash_ending)" in main
        stash_chain = _func_body(main, "_on_command_result")
        assert "_stash_ending(response)" in stash_chain

    def test_every_game_over_road_ends_at_one_seam(self):
        main = _gd("main")
        assert "_show_game_over_screen(response.game_state)" not in main
        # the six roads that read `game_state.game_over` (not the definition)
        assert len(re.findall(r"^\s+_on_campaign_over\(response\)", main, re.M)) == 6
        body = _func_body(main, "_on_campaign_over")
        assert "set_input_enabled(false)" in body and "_campaign_over = true" in body
        assert "_show_pending_ending()" in body and "_show_game_over_screen(" in body

    def test_the_ending_is_raised_after_the_tableau_and_before_the_landmark(self):
        tail = _func_body(_gd("main"), "_return_control_to_player")
        assert tail.index("_show_pending_diorama()") < tail.index("_show_pending_ending()") \
            < tail.index("_show_pending_proclamation()")
        for name in ("_on_battle_diorama_dismissed", "_on_proclamation_dismissed",
                     "_on_marshal_petition_deferred", "_apply_world_swap_response"):
            assert "_show_pending_ending()" in _func_body(_gd("main"), name), name

    def test_the_command_line_never_reopens_after_the_fall(self):
        body = _func_body(_gd("main"), "set_input_enabled")
        assert "if enabled and _campaign_over:" in body
        assert body.index("_campaign_over") < body.index("command_input.editable = enabled")
        cancel = _func_body(_gd("main"), "_on_load_cancelled")
        assert "campaign_end.reraise()" in cancel

    def test_a_world_swap_adopts_history_and_lifts_the_fall(self):
        main = _gd("main")
        reset = _func_body(main, "_reset_frontend_state_for_world_swap")
        for line in ("pending_ending_queue.clear()", "_endings_shown.clear()",
                     "_campaign_over = false"):
            assert line in reset
        adopt = _func_body(main, "_adopt_endings_on_world_swap")
        assert 'bool(row.get("terminal", false))' in adopt
        assert "_adopt_endings_on_world_swap(response)" in _func_body(main, "_apply_world_swap_response")
        assert "_adopt_endings_on_world_swap(response)" in _func_body(main, "_on_connection_test")

    def test_the_legacy_text_is_de_legacied(self):
        body = _func_body(_gd("main"), "_show_game_over_screen")
        assert "13" not in body
        assert "VICTOIRE" not in body and "DÉFAITE" not in body
        assert 'ending.get("cause_line", "")' in body
        assert "func _show_game_over_screen(game_state: Dictionary, ending = null):" in body

    def test_the_clock_line_reaches_the_banner_and_the_r_screen_and_the_tab(self):
        main = _gd("main")
        assert "_add_fall_clock_lines(defeat_imminent_warning)" in _func_body(main, "_display_morning_dispatch")
        helper = _func_body(main, "_add_fall_clock_lines")
        assert 'arm.get("clock_line", "")' in helper and 'arm.get("severity", "warning")' in helper
        view = _gd("dispatch_view")
        assert 'arm.get("clock_line", "")' in view
        ledger_gd = _gd("strategic_ledger")
        assert "_fall_clock_lines()" in _func_body(ledger_gd, "_render_territories")
        assert 'cached_data.get("fall_clock", null)' in _func_body(ledger_gd, "_fall_clock_lines")

    def test_the_parse_check_lists_the_new_scripts_and_scene(self):
        src = _read(TOOLS / "godot_parse_check.gd")
        for entry in ("res://scripts/campaign_end.gd", "res://scripts/api_client.gd",
                      "res://scenes/campaign_end.tscn",
                      "res://../../tools/ge2_campaign_end_harness.gd"):
            assert entry in src, entry

    def test_the_committed_report_parsed_them(self):
        report = json.loads(_read(TOOLS / "godot_parse_report.json"))
        paths = {row["path"]: row for row in report["scripts"]}
        for path in ("res://scripts/campaign_end.gd", "res://scripts/api_client.gd",
                     "res://../../tools/ge2_campaign_end_harness.gd"):
            assert path in paths, path
            assert paths[path]["parse_ok"] and paths[path]["load_ok"], paths[path]
        scenes = {row["path"]: row for row in report["scenes"]}
        assert scenes["res://scenes/campaign_end.tscn"]["instantiate_ok"]


# ═══════════════════════════════════════════════════════════════════════════
# The driver — the END SCREEN block, the stop flag, the four arms, the fixtures
# ═══════════════════════════════════════════════════════════════════════════


def _driver():
    import importlib.util
    spec = importlib.util.spec_from_file_location("_ge2_driver", TOOLS / "playtest_driver.py")
    module = importlib.util.module_from_spec(spec)
    with _quiet():
        spec.loader.exec_module(module)
    return module


class TestTheDriverRendersTheScreen:

    def test_the_end_screen_block_reads_the_payload(self):
        drv = _driver()
        w = _boot()
        payload = stage_chains_payload(w)
        lines = drv._end_screen_lines(payload)
        text = "\n".join(lines)
        assert "register `fall` · TERMINAL — Load / Main Menu" in text
        assert "THE VERDICT — THE ECLIPSE:" in text
        assert "THE RECORD — battles" in text
        assert "THE EXILE (captivity) — " in text
        assert "Olmütz" in text

    def test_a_marked_ending_reads_as_continuing(self):
        drv = _driver()
        w = _boot()
        w.current_turn = 44
        _tick(w, 1)
        payload = game_end.screen_payload(game_end.latest_ending(w))
        text = "\n".join(drv._end_screen_lines(payload))
        assert "marked — the campaign continues" in text
        assert "THE EXILE" not in text

    def test_the_lever_keeps_the_ge1_one_liner(self, monkeypatch):
        drv = _driver()
        monkeypatch.setattr(drv, "THE_DIGEST_RENDERS_THE_END_SCREEN", False)

        class _T:
            def get(self, path):
                return {"endings": [{"title": "T", "cause_line": "C", "tier_title": "E",
                                     "summary": {"verdict": {"title": "E", "lines": ["x"]}}}]}

        class _D:
            def __init__(self):
                self.notes = []

            def note(self, text):
                self.notes.append(text)

        d = _D()
        assert drv._note_new_endings(_T(), d, 0) == 1
        assert d.notes == ["ENDING — T: C [E]"]
        monkeypatch.setattr(drv, "THE_DIGEST_RENDERS_THE_END_SCREEN", True)
        d = _D()
        drv._note_new_endings(_T(), d, 0)
        assert len(d.notes) > 1 and d.notes[1].lstrip().startswith("↳")

    def test_the_stop_flag_stops_on_a_new_marked_ending(self):
        drv = _driver()

        class _A:
            stop_on_ending = True

        class _Off:
            stop_on_ending = False

        assert drv._ending_stop_due(_A(), 0, 1) is True
        assert drv._ending_stop_due(_A(), 1, 1) is False      # nothing new this turn
        assert drv._ending_stop_due(_Off(), 0, 1) is False    # the flag is off
        assert drv._ending_stop_due(object(), 0, 1) is False  # no flag at all
        src = _read(TOOLS / "playtest_driver.py")
        assert '"--stop-on-ending"' in src
        # the loop reads the ONE predicate, and stops on it
        loop = src[src.index("def run(args):"):]
        at = loop.index("if _ending_stop_due(args, _endings_before_turn, _endings_seen):")
        assert 'status = "ending-reached"' in loop[at:at + 400]
        assert "break" in loop[at:at + 400]

    @pytest.mark.parametrize("name, title, status", [
        ("ge2-eagle-falls", "The Emperor is dead.", "game-over"),
        ("ge2-chains", "is deposed.", "game-over"),
        ("ge2-soil-or-sword", "a province, not a realm.", "game-over"),
        ("ge2-verdict", "THE VERDICT OF HISTORY", "ending-reached"),
    ])
    def test_the_arm_reached_its_ending_and_the_screen_block_is_archived(self, name, title, status):
        digest = AUDITS / "playtest_digests" / name / "digest.md"
        meta = AUDITS / "playtest_digests" / name / "meta.json"
        assert digest.exists() and meta.exists(), name
        text = _read(digest)
        assert "ENDING — " in text and title in text
        assert "THE RECORD — battles" in text
        assert json.loads(_read(meta))["status"] == status

    @pytest.mark.parametrize("name, check", [
        ("fixture_ge2_soil_or_sword.json",
         lambda ws: sum(1 for r in ws["regions"].values() if r.get("controller") == "France") == 1),
        ("fixture_ge2_chains.json",
         lambda ws: ws["marshals"]["Napoleon"].get("captured_by") == "Austria"),
    ])
    def test_the_staged_fixture_is_what_it_says(self, name, check):
        data = json.loads(_read(FIXTURES / name))
        assert data["metadata"]["save_name"].startswith("GE-2 staged — ")
        assert check(data["world_state"])
        with _quiet():
            world = WorldState.from_dict(data["world_state"])
        assert world.endings_armed is True
        assert fall.get_fall_state(world) is not None


# ═══════════════════════════════════════════════════════════════════════════
# The IQ-10 frames — the surface table and the committed evidence
# ═══════════════════════════════════════════════════════════════════════════


class TestTheFrames:

    def test_the_surface_table_shoots_every_register_and_both_clock_surfaces(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("_ge2_runner", TOOLS / "iq10_run_captures.py")
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        ids = {row["id"]: row for row in runner.SHOTS}
        for shot in ("campaign_end_fall_funeral", "campaign_end_fall_chains",
                     "campaign_end_fall_abdication", "campaign_end_humbled",
                     "campaign_end_verdict", "campaign_end_imperial",
                     "ledger_fall_clock_territories", "dispatch_fall_clock"):
            assert shot in ids, shot
            assert ids[shot]["must_show"] and ids[shot]["surface"]
        for reg in ("fall_funeral", "fall_chains", "fall_abdication", "humbled", "verdict", "imperial"):
            row = ids[f"campaign_end_{reg}"]
            assert row["scene"] == "res://scenes/campaign_end.tscn"
            assert row["mode"] == "call" and row["method"] == "show_ending"
        assert ids["ledger_fall_clock_territories"]["tab"] == 1
        assert '"campaign_end": cap_campaign_end' in _read(TOOLS / "iq10_capture_payloads.py")

    @pytest.mark.parametrize("stem", [
        "IQ10_CAMPAIGN_END_FALL_FUNERAL", "IQ10_CAMPAIGN_END_FALL_CHAINS",
        "IQ10_CAMPAIGN_END_FALL_ABDICATION", "IQ10_CAMPAIGN_END_HUMBLED",
        "IQ10_CAMPAIGN_END_VERDICT", "IQ10_CAMPAIGN_END_IMPERIAL",
        "IQ10_LEDGER_FALL_CLOCK_TERRITORIES", "IQ10_DISPATCH_FALL_CLOCK",
    ])
    def test_the_frame_is_committed_at_both_scales(self, stem):
        for tail in ("", "_X2"):
            png = AUDITS / f"{stem}{tail}_{FRAME_DATE}.png"
            assert png.exists(), f"missing evidence frame: {png.name}"
            assert png.stat().st_size > 8000, f"{png.name} is too small to be a real frame"


# ═══════════════════════════════════════════════════════════════════════════
# The client, DRIVEN
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="module")
def driven(payloads, tmp_path_factory):
    exe = C.engine()
    if exe is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    work = tmp_path_factory.mktemp("ge2")
    out = work / "out.json"
    log = work / "godot.log"
    spec = work / "spec.json"
    spec.write_text(json.dumps(dict(payloads, out=str(out)), default=str), encoding="utf-8")
    env = dict(os.environ, GE2_SPEC=str(spec))
    env.pop("PYTHONIOENCODING", None)
    proc = subprocess.run(
        [exe, "--headless", "--path", str(PROJECT), "--log-file", str(log),
         "--script", str(HARNESS)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=300, env=env, cwd=str(PROJECT))
    if not out.is_file():
        pytest.fail("the harness wrote no result\n"
                    f"exit={proc.returncode}\nstderr tail:\n{proc.stderr[-2000:]}")
    result = json.loads(out.read_text(encoding="utf-8"))
    assert "error" not in result, result.get("error")
    text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    result["script_errors"] = text.count("SCRIPT ERROR")
    result["script_error_lines"] = [ln for ln in text.splitlines() if "SCRIPT ERROR" in ln][:10]
    return result


class TestTheClientDriven:

    def test_the_harness_ran_clean(self, driven):
        assert driven["script_errors"] == 0, driven["script_error_lines"]
        assert driven["registered"] is True

    def test_the_command_road_death_raises_the_funeral_and_closes_the_line(self, driven, payloads):
        s = driven["funeral"]
        assert s["visible"] is True and s["register"] == "fall" and s["terminal"] is True
        assert s["layer"] == 122
        assert s["title"] == "THE FALL OF THE EMPIRE"
        assert s["cause"] == "The Emperor is dead."
        assert "THE FUNERAL" in s["content"] and "THE RECORD" in s["content"]
        assert "THE VERDICT OF HISTORY" in s["content"] and "THE ECLIPSE" in s["content"]
        first = payloads["funeral"]["ending"]["summary"]["epilogue"]["paragraphs"][0][:60]
        assert first in s["content"]
        assert s["primary"] == {"text": "Load a campaign", "visible": True, "disabled": False}
        assert s["secondary"] == {"text": "Main Menu", "visible": True, "disabled": False}
        assert s["input_enabled"] is False and s["campaign_over"] is True
        # the scrollback record beneath the card, de-legacied
        term = driven["funeral_terminal"]
        assert "THE FALL OF THE EMPIRE" in term and "The Emperor is dead." in term
        assert "13" not in term.split("THE RECORD")[-1][:400]

    def test_load_steps_the_card_aside_and_a_cancel_brings_it_back(self, driven):
        assert driven["funeral_load_dialog_raised"] is True
        assert driven["funeral_screen_hidden_for_load"] is True
        assert driven["funeral_input_during_load"] is False
        after = driven["funeral_after_cancel"]
        assert after["visible"] is True and after["input_enabled"] is False
        assert after["primary"]["disabled"] is False

    def test_the_fallen_campaigns_next_response_raises_nothing_new(self, driven):
        assert driven["funeral_refusal_reraised"] is False
        assert driven["funeral_refusal_input_enabled"] is False

    def test_a_world_swap_lifts_the_fall(self, driven):
        assert driven["after_swap_input_enabled"] is True

    def test_the_verdict_waits_behind_the_enemy_phase_then_continues(self, driven, payloads):
        assert driven["verdict_enemy_phase_raised"] is True
        assert driven["verdict_screen_before_dismiss"] is False
        s = driven["verdict"]
        # (`verdict_ahead_of_the_card` names what the tail raised first — the
        # battle tableau of the turn's fighting; the card came after it.)
        assert s["visible"] is True and s["register"] == "verdict" and s["terminal"] is False, \
            driven["verdict_ahead_of_the_card"]
        tier = payloads["verdict"]["ending"]["summary"]["verdict"]["title"]
        assert tier in s["content"] and "THE RECORD" in s["content"]
        assert s["primary"]["text"] == "Continue" and s["secondary"]["visible"] is False
        assert s["input_enabled"] is False
        assert "THE VERDICT OF HISTORY" in driven["verdict_terminal"]
        after = driven["verdict_after_continue"]
        assert after == {"visible": False, "input_enabled": True, "modal_open": False}
        assert driven["verdict_repeat_raised"] is False

    def test_the_tail_itself_raises_the_card_when_no_tableau_stands(self, driven):
        """The mutation the tableau masks: with nothing standing ahead of the
        card, `_return_control_to_player`'s own raise is the only road."""
        assert driven["verdict_plain_diorama_visible"] is False
        s = driven["verdict_plain"]
        assert s["visible"] is True and s["register"] == "verdict"
        assert s["input_enabled"] is False

    def test_the_humbled_peace_is_fetched_off_the_record_and_raised(self, driven):
        assert driven["humbled_fetched"] is True
        s = driven["humbled"]
        assert s["visible"] is True and s["register"] == "humbled_peace"
        assert "THE PEACE" in s["content"] and s["primary"]["text"] == "Continue"
        assert s["secondary"]["visible"] is False
        assert driven["humbled_after_continue"] == {"visible": False, "input_enabled": True}
        assert driven["humbled_repeat_raised"] is False
        assert driven["humbled_repeat_fetched"] is False

    def test_a_final_save_loads_onto_the_end_screen(self, driven):
        s = driven["load_final"]
        assert s["visible"] is True and s["register"] == "fall" and s["terminal"] is True
        assert "THE EXILE" in s["content"]
        assert s["input_enabled"] is False and s["campaign_over"] is True
        assert driven["load_final_fetched"] is False
        # The load prints the briefing and the boot help ABOVE the record, so
        # the terminal's own cap trims the top; the record's closing line is
        # the last thing printed and is what the scrollback keeps.
        assert "The campaign is over. Load another, or return to the Main Menu." \
            in driven["load_final_terminal"]

    def test_the_clock_line_on_the_banner_and_the_tab_is_the_backends(self, driven, payloads):
        line = payloads["dispatch"]["defeat_imminent_warning"]["fall"]["arms"][0]["clock_line"]
        assert line in driven["dispatch_terminal"]
        for arm in payloads["ledger"]["ledger"]["fall_clock"]["arms"]:
            assert arm["clock_line"] in driven["ledger_territories_text"], arm["clock_line"]
