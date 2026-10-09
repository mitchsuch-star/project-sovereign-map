"""Score Finish Step 7 slice 8 (October 4, 2026) — Chunk 9's client half.

The rows, each re-measured at HEAD before a line was written:

  * CX3-R2 — `Ney, march to ` (the completer's own slotted line, one Tab from
    the verb) cost an action, staged a standing order for the nearest enemy
    province and raised a bad-odds interrupt at Mack; its sibling `move to `
    asked where, free. A march whose destination slot is EMPTY now asks.
  * CX3-R5 — the drill verb is a word: "Drillmaster of Boulogne", an ability
    name the game prints, read as an order.
  * CX3-R10 — closed by SR-3b's rider (a hold the game placed claims no
    reading); pinned here.
  * CX3-R11 — the manual leads with a recruit form the boot board takes.
  * WO-D14 — the greyed separate-peace road names its DP price.
  * The counter-punch rail row carries its own button (UX23-A's idiom),
    re-derived on every read of the rail and retired once the strike is
    spent.
  * CX3-R4 / R6 / R9 / R12, WO-V-D1, WO-V-D2, EAS-2's client half and the
    auto-end's client half are `.gd`: pinned by source here and DRIVEN in
    `test_cx7_predictor_driven.py` (R4, R6) and below (the Build fold).
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import re
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.ai.strategic_parser import march_slot_is_empty
from backend.commands import strategic_executor as SE
from backend.commands.parser import CommandParser
from backend.game_logic import dispatch as D
from backend.game_logic import settlement_validation as SV

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
HARNESS = ROOT / "tools" / "cn3_region_panel_harness.gd"


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    with contextlib.redirect_stdout(io.StringIO()):
        M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    # The objection roll is random (the recorded trap): pin the mood
    # variance to the base concern at both importers, so an order this
    # file sends meets the same objection on every run.
    monkeypatch.setattr("backend.commands.executor.apply_mood_variance",
                        lambda concern: concern)
    monkeypatch.setattr("backend.commands.strategic_executor.apply_mood_variance",
                        lambda concern: concern)
    return TestClient(M.app), M.world


def post(client, command):
    with contextlib.redirect_stdout(io.StringIO()):
        return client.post("/command", json={"command": command}).json()


# ═══════════════════════ CX3-R2 — a bare march asks where ═══════════════════════

class TestABareMarchAsksWhere:
    @pytest.mark.parametrize("line", ["Ney, march to ", "Ney, march to", "Ney, march toward",
                                      "Ney, advance on", "Ney, make for "])
    def test_an_empty_destination_slot_asks_free(self, shipped, line):
        client, world = shipped
        body = post(client, line)
        ney = world.marshals["Ney"]
        assert world.actions_remaining == 4, body.get("message")
        assert ney.strategic_order is None
        assert not getattr(ney, "pending_interrupt", None)
        assert body.get("state") == "awaiting_clarification"
        assert body["message"] == "Where shall Ney march, Sire? He stands at Rhineland."
        commands = [o["command"] for o in body.get("options") or []]
        assert commands and all(c.startswith("Ney, march to ") for c in commands), commands

    def test_the_question_prices_the_marshals_own_rate(self, shipped):
        """A literal marches for one action (`strategic_order_ap`), so one
        action left still asks him; the generic floor is two."""
        client, world = shipped
        world.actions_remaining = 1
        body = post(client, "Soult, march to ")
        assert body.get("state") == "awaiting_clarification", body.get("message")
        commands = [o["command"] for o in body.get("options") or []]
        assert commands and all(c.startswith("Soult, march to ") for c in commands), commands

    def test_no_affordable_answer_is_refused_before_the_question(self, shipped):
        """Ney's march is two actions: with one left the AP pre-validation
        refuses first (the established order — AP before objections and
        questions), free, with no menu of answers nobody could pay for. The
        gate's own no-menu line is the defensive arm for a province with no
        neighbour, which the shipped map does not have."""
        client, world = shipped
        world.actions_remaining = 1
        body = post(client, "Ney, march to ")
        assert world.actions_remaining == 1, body.get("message")
        assert not body.get("options"), body.get("options")
        assert "Need 2, have 1" in body["message"], body["message"]

    def test_the_answer_marches(self, shipped):
        client, world = shipped
        body = post(client, "Ney, march to ")
        target = body["options"][0]["target"]
        post(client, target)
        ney = world.marshals["Ney"]
        assert (ney.location == target
                or (ney.strategic_order is not None and ney.strategic_order.target == target)), (
            ney.location, ney.strategic_order)

    def test_a_named_destination_still_marches(self, shipped):
        client, world = shipped
        post(client, "Ney, march to Swabia")
        order = world.marshals["Ney"].strategic_order
        assert order is not None and order.target == "Swabia"

    def test_the_vague_order_keeps_its_designed_reading(self, shipped):
        """"march on the enemy" is the generic resolution's own case."""
        client, world = shipped
        post(client, "Ney, march on the enemy")
        order = world.marshals["Ney"].strategic_order
        assert order is not None and order.command_type == "MOVE_TO"

    def test_the_ai_is_never_asked(self, shipped):
        """The question is the player's: an enemy marshal's order through the
        ONE shared executor (GR5) with the same empty slot is never answered
        with THIS gate's question. (A generic target still meets the older
        generic resolver's confirmation, which no AI rung reaches — every
        rung names its province.)"""
        _, world = shipped
        parsed = {"strategic_type": "MOVE_TO", "raw_input": "Mack, march to",
                  "command": {"marshal": "Mack", "action": "move", "target": None,
                              "target_type": "generic"}}
        with contextlib.redirect_stdout(io.StringIO()):
            result = M.executor._strategic._execute_strategic_command(
                parsed, parsed["command"], M.game_state) or {}
        assert "Where shall Mack march" not in str(result.get("message")), result

    def test_a_standing_order_turn_is_never_asked(self, shipped):
        """A standing order executed at the turn (`_strategic_execution`)
        carries the line it was given; the gate is the issuance's."""
        _, world = shipped
        parsed = {"strategic_type": "MOVE_TO", "raw_input": "Ney, march to",
                  "command": {"marshal": "Ney", "action": "move", "target": None,
                              "target_type": "generic", "_strategic_execution": True}}
        with contextlib.redirect_stdout(io.StringIO()):
            result = M.executor._strategic._execute_strategic_command(
                parsed, parsed["command"], M.game_state) or {}
        assert "Where shall Ney march" not in str(result.get("message")), result

    def test_lever_down_restores_the_priced_march_at_mack(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(SE, "A_BARE_MARCH_ASKS_WHERE", False)
        post(client, "Ney, march to ")
        order = world.marshals["Ney"].strategic_order
        assert order is not None and order.target == "Swabia"

    @pytest.mark.parametrize("text,empty", [
        ("Ney, march to", True), ("Ney, march to ", True), ("Ney, march to.", True),
        ("Ney, fall back to", True), ("Ney, advance upon", True),
        ("Ney, march to Swabia", False), ("Ney, march", False), ("Ney, march on the enemy", False),
        ("", False), (None, False),
    ])
    def test_the_slot_reader(self, text, empty):
        assert march_slot_is_empty(text) is empty


# ═══════════════════════ CX3-R5 — the drill verb is a word ═══════════════════════

class TestTheDrillIsAWord:
    def test_an_ability_name_is_not_an_order(self, shipped):
        client, world = shipped
        body = post(client, "Drillmaster of Boulogne")
        assert body.get("state") != "awaiting_clarification"
        assert "Which marshal shall carry out this order" not in str(body.get("message"))
        assert world.actions_remaining == 4

    @pytest.mark.parametrize("line", ["Ney, drill", "Ney, drill the men", "Davout, training",
                                      "Soult, exercise the troops", "Ney, train"])
    def test_the_drill_forms_still_drill(self, shipped, line):
        client, _ = shipped
        body = post(client, line)
        assert "cannot drill" in str(body.get("message")), body.get("message")

    def test_lever_down_reads_the_substring(self, shipped, monkeypatch):
        from backend.ai import llm_client as LC
        client, _ = shipped
        monkeypatch.setattr(LC, "THE_DRILL_IS_A_WORD", False)
        body = post(client, "Drillmaster of Boulogne")
        assert "Which marshal shall carry out this order" in str(body.get("message"))


# ═══════════════════════ CX3-R10 / CX3-R11 — what the order and the manual say ═══════════════════════

class TestTheHoldAndTheManual:
    def test_a_hold_names_no_substitution(self, shipped):
        """CX3-R10: closed by SR-3b's rider — the hold the game placed claims
        no reading of a province the player never named."""
        client, _ = shipped
        body = post(client, "Ney, hold")
        assert "Ney will hold Rhineland" in body["message"]
        assert "Our maps read" not in body["message"]

    def test_the_manuals_first_recruit_form_runs_on_the_boot_board(self, shipped):
        """CX3-R11: the help used to lead with `recruit`, which refuses on
        turn 1 on every seed (no corps within reach of a depot)."""
        from backend.commands.meta_executor import MetaExecutor
        client, world = shipped
        with contextlib.redirect_stdout(io.StringIO()):
            body = MetaExecutor(None)._execute_help({}, world)["message"]
        block = body[body.index("  recruit    -"):]
        block = block[:block.index("Infantry 10k")]
        quoted = re.findall(r'"([^"\n]+)"', block)
        assert quoted[0] == "recruit for Davout", quoted
        assert "must stand within reach" in block
        reply = post(client, quoted[0])
        assert reply.get("success") is True, reply.get("message")


# ═══════════════════════ WO-D14 — the greyed road names its price ═══════════════════════

class TestTheGreyedRoadNamesItsPrice:
    def _war(self, world):
        for wid, w in (getattr(world, "war_instances", {}) or {}).items():
            sides = w.get("side_by_nation") or {}
            if "France" in sides and "Austria" in sides and sides["France"] != sides["Austria"]:
                return wid
        raise AssertionError("no France–Austria war on the boot board")

    def test_a_road_short_of_points_states_the_price(self, shipped):
        from backend.game_logic.diplomacy import diplomatic_price_quote
        _, world = shipped
        world.diplomatic_points = 0
        res = SV.evaluate_pair_peace_substitute_eligibility(
            world, war_id=self._war(world), actor_nation="France",
            target_nation="Austria", action="seek_bilateral_peace")
        assert res["refusal_code"] == "insufficient_resources", res
        quote = diplomatic_price_quote(world, "peace", "Austria")
        assert res["disabled_reason_display"].endswith(f"It costs {quote['text']}."), res
        assert quote["text"].endswith("you have 0")
        # the schema stays closed
        assert set(res) == {"eligible", "refusal_code", "disabled_reason_display", "selected_pair"}

    def test_lever_down_is_the_bare_refusal(self, shipped, monkeypatch):
        _, world = shipped
        monkeypatch.setattr(SV, "THE_GREYED_ROAD_NAMES_ITS_PRICE", False)
        world.diplomatic_points = 0
        res = SV.evaluate_pair_peace_substitute_eligibility(
            world, war_id=self._war(world), actor_nation="France",
            target_nation="Austria", action="seek_bilateral_peace")
        assert "It costs" not in res["disabled_reason_display"]


# ═══════════════════════ the counter-punch rail row ═══════════════════════

def _earned(world, name="Davout"):
    m = world.marshals[name]
    m.counter_punch_available = True
    m.counter_punch_turns = 1
    return m


def _post_the_row(world, marshal):
    """The row as the combat seam posts it (its own reader, its own call)."""
    with contextlib.redirect_stdout(io.StringIO()):
        M.executor._combat._process_combat_notifications(
            {"counter_punch_earned": True}, world.marshals["Mack"], marshal, world)


def _rows(notifications):
    from backend.notifications import COUNTER_PUNCH_EARNED
    return [n for n in notifications if n.get("type") == COUNTER_PUNCH_EARNED]


def _read(client):
    with contextlib.redirect_stdout(io.StringIO()):
        return client.get("/notifications").json()["notifications"]


def _strike(client, command):
    """Send the row's command down the typed pipeline and, where the
    marshal objects (a cautious man facing bad odds — his character, and
    the same modal every attack order meets), insist: the strike is
    thrown and the LAST response is the one the client renders."""
    body = post(client, command)
    if body.get("pending_objection"):
        with contextlib.redirect_stdout(io.StringIO()):
            body = client.post("/respond_to_objection", json={"choice": "insist"}).json()
    return body


class TestTheCounterPunchRowHasItsButton:
    """Davout (cautious) at Rhineland, Mack at Swabia one hop away: the boot
    board's own counter-punch geometry."""

    def test_a_foe_in_reach_puts_the_strike_on_the_row(self, shipped):
        _, world = shipped
        davout = _earned(world)
        note = D.counter_punch_notice(davout, world)
        assert note["details"]["action_command"] == "Davout, attack Mack"
        assert note["details"]["action_label"] == "Strike Mack — free"
        assert "Mack stands within reach at Swabia" in note["message"]

    def test_the_combat_seam_posts_the_row_with_its_button(self, shipped):
        """Read off the collector itself, not a response: the reader
        re-derives the row and would mask what the seam posted."""
        _, world = shipped
        _post_the_row(world, _earned(world))
        rows = _rows(world.notifications.get_pending())
        assert len(rows) == 1
        assert rows[0]["details"]["action_command"] == "Davout, attack Mack"

    def test_the_button_is_an_order_the_game_takes_free(self, shipped):
        client, world = shipped
        davout = _earned(world)
        command = D.counter_punch_notice(davout, world)["details"]["action_command"]
        body = _strike(client, command)
        assert body.get("success") is True, body.get("message")
        assert davout.counter_punch_available is False, "the strike was never thrown"
        assert world.actions_remaining == 4, body.get("message")

    def test_a_spent_strike_leaves_the_rail_on_the_same_response(self, shipped):
        client, world = shipped
        _post_the_row(world, _earned(world))
        assert _rows(_read(client))
        body = _strike(client, "Davout, attack Mack")
        assert body.get("success") is True, body.get("message")
        assert world.marshals["Davout"].counter_punch_available is False
        assert not _rows(body["notifications"]), _rows(body["notifications"])

    def test_a_fortified_man_gets_the_note_not_the_button(self, shipped):
        client, world = shipped
        davout = _earned(world)
        _post_the_row(world, davout)
        davout.fortified = True
        rows = _rows(_read(client))
        assert len(rows) == 1
        assert "action_command" not in rows[0]["details"]
        assert "must unfortify first" in rows[0]["message"]

    def test_a_drill_locked_man_gets_the_note_not_the_button(self, shipped):
        _, world = shipped
        davout = _earned(world)
        davout.drilling_locked = True
        note = D.counter_punch_notice(davout, world)
        assert "action_command" not in note["details"]
        assert "locked in drill" in note["message"]

    def test_a_foe_in_sight_but_out_of_reach_gets_no_button(self, shipped):
        """Mack two hops off at Franconia — still in sight, beyond a
        one-march man's reach: the note says so, and there is no button."""
        _, world = shipped
        davout = _earned(world)
        assert int(davout.movement_range or 1) == 1
        assert world.get_distance(davout.location, "Franconia") == 2
        for enemy in world.get_visible_enemies("France"):
            if enemy.name != "Mack":
                enemy.location = "Vienna"
        world.marshals["Mack"].location = "Franconia"
        world.invalidate_active_nations_cache()
        assert "Mack" in [e.name for e in world.get_visible_enemies("France")]
        note = D.counter_punch_notice(davout, world)
        assert "action_command" not in note["details"]
        assert "No foe stands within his reach" in note["message"]

    def test_a_captured_or_spent_man_loses_the_row_on_the_next_read(self, shipped):
        client, world = shipped
        davout = _earned(world)
        _post_the_row(world, davout)
        davout.captured_by = "Austria"
        assert not _rows(_read(client))
        davout.captured_by = None
        _post_the_row(world, _earned(world))
        assert _rows(_read(client))
        davout.counter_punch_turns = 0
        assert not _rows(_read(client))

    def test_a_requoted_row_keeps_its_id(self, shipped):
        client, world = shipped
        davout = _earned(world)
        _post_the_row(world, davout)
        before = _rows(_read(client))[0]["id"]
        davout.fortified = True
        after = _rows(_read(client))[0]
        assert after["id"] == before
        assert "action_command" not in after["details"]

    def test_an_aggressive_man_holds_no_strike_and_gets_no_button(self, shipped):
        """The counter-punch is a cautious commander's (`has_counter_punch`);
        a flag set on Ney prices the attack, so the row offers nothing."""
        _, world = shipped
        note = D.counter_punch_notice(_earned(world, "Ney"), world)
        assert "action_command" not in note["details"]

    def test_lever_down_is_the_plain_row(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(D, "THE_COUNTER_PUNCH_ROW_HAS_ITS_BUTTON", False)
        note = D.counter_punch_notice(_earned(world), world)
        assert set(note["details"]) == {"marshal"}
        # and the reader leaves a row it no longer re-derives alone
        _post_the_row(world, world.marshals["Davout"])
        world.marshals["Davout"].fortified = True
        rows = _rows(_read(client))
        assert len(rows) == 1 and "must unfortify" not in rows[0]["message"]


# ═══════════════════════ the client's half, by source ═══════════════════════

def _gd(name):
    return (SCRIPTS / name).read_text(encoding="utf-8")


class TestTheClientHalf:
    def test_the_panel_resize_reruns_the_layout_pass(self):
        """CX3-R4 (driven in test_cx7_predictor_driven.py::TestTheGripFollowsThePanel)."""
        assert "bottom_left_ui.resized.connect(_reposition_after_layout)" in _gd("main.gd")

    def test_the_unused_parameter_says_so(self):
        """CX3-R12: renamed, never wired (wiring silences 1,016 of 1,486 lines)."""
        src = _gd("main.gd")
        assert "func _add_verb_or_target(marshal: String, rest: String, _prefix: String," in src

    def test_the_log_sizes_a_row_by_its_tier(self):
        """EAS-2's client half. Re-seated by UXR-1b (October 9, 2026): the
        three sizes were 14 / 12 / 11 and the routine tier read P1 on every
        monitor in the whole-client census; the hierarchy stands at 18 / 16 /
        14, with the routine row in the Caption class."""
        src = _gd("campaign_log.gd")
        assert 'const TIER_FONT_SIZES := {"lead": 18, "notable": 16, "routine": 14}' in src
        assert 'TIER_FONT_SIZES.get(tier, DEFAULT_ROW_FONT_SIZE)' in src
        assert 'label.theme_type_variation = &"CaptionRich"' in src
        assert 'if tier == "lead":' in src

    def test_our_own_soil_carries_no_fog_hedge(self):
        """WO-V-D2."""
        src = _gd("region_panel.gd")
        assert 'if visibility == "partial" and controller != _PLAYER_NATION:' in src
        assert 'elif visibility == "stale" and controller != _PLAYER_NATION:' in src

    def test_the_day_says_when_it_ends(self):
        """The auto-end confirm's client half."""
        src = _gd("main.gd")
        assert "_note_the_end_of_the_day()" in src
        assert "var _auto_end_warned_turn := -1" in src
        assert '"spends your last action ends the turn at once."' in src

    def test_the_screenshot_board_is_the_real_boot(self):
        """CX3-R9."""
        tool = (ROOT / "tools" / "cx3_completer_screenshot.gd").read_text(encoding="utf-8")
        assert "_main._last_game_state = _board()" in tool
        assert "_apply_terminal_size(UiSettings.DEFAULT_TERMINAL_WIDTH" in tool
        board = json.loads((ROOT / "tools" / "cx3_completer_board.json").read_text(encoding="utf-8"))
        assert len(board["map_data"]) == 126
        assert board.get("player_nation") == "France"


# ═══════════════════════ WO-V-D1 — the Build rows fold (driven) ═══════════════════════

def _engine():
    for candidate in (os.environ.get("GODOT_BIN", ""),
                      r"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe"
                      r"\Godot_v4.4.1-stable_win64.exe"):
        if candidate and Path(candidate).is_file():
            return candidate
    return None


@pytest.fixture(scope="module")
def folded(tmp_path_factory):
    engine = _engine()
    if engine is None:
        pytest.skip("Godot engine not on this machine — the driven pin skips, "
                    "and a skip is not a pass")
    from backend.game_logic.recruitment import build_recruitment_payload
    work = tmp_path_factory.mktemp("s8fold")
    with pytest.MonkeyPatch.context() as mp:
        for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
            mp.delenv(key, raising=False)
        mp.setenv("LLM_MODE", "mock")
        with contextlib.redirect_stdout(io.StringIO()):
            M._reset_world_state()
        mp.setattr(M, "parser", CommandParser(use_real_llm=False))
        with contextlib.redirect_stdout(io.StringIO()):
            game_state = TestClient(M.app).get("/test").json()["game_state"]
        recruitment = build_recruitment_payload(M.world)
    out = work / "rendered.json"
    spec = work / "spec.json"
    spec.write_text(json.dumps({
        "game_state": game_state, "regions": ["Paris"], "folded_region": "Paris",
        "recruitment": recruitment, "out": str(out)}), encoding="utf-8")
    env = dict(os.environ, CN3_SPEC=str(spec), CN3_OUT=str(out))
    proc = subprocess.run(
        [engine, "--headless", "--path", str(PROJECT), "--script", str(HARNESS)],
        capture_output=True, text=True, timeout=300, env=env, cwd=str(PROJECT))
    if not out.is_file():
        pytest.fail(f"the harness wrote no result\nexit={proc.returncode}\n{proc.stderr[-2000:]}")
    return json.loads(out.read_text(encoding="utf-8"))


class TestTheBuildRowsFold:
    def test_the_panel_opens_folded(self, folded):
        """The default the panel instantiates with, read by the harness before
        anything is set (§6 row 21 (d): folded by default)."""
        assert folded["build_open_default"] is False

    def test_one_click_on_the_header_opens_the_rows(self, folded):
        text = folded["after_one_click"]
        assert "[url=toggle:build]▾ Build[/url]" in text
        assert "[url=do:build " in text

    def test_folded_the_header_names_the_count_and_hides_the_rows(self, folded):
        text = folded["folded"]
        assert re.search(r"\[url=toggle:build\]▸ Build — \d+ works?\[/url\]", text), text
        assert "[url=do:build " not in text

    def test_open_the_rows_are_there(self, folded):
        text = folded["regions"]["Paris"]
        assert "[url=toggle:build]▾ Build[/url]" in text
        assert "[url=do:build " in text
