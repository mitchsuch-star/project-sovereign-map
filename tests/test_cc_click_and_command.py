"""Row CC "Click & Command" — CC-0 "The line is the player's" and CC-1 "Click
names into the line" (October 15, 2026; plan: the user's "let's focus on
commands" ruling, with the edge case they named — "overwriting commands when
you click something").

CC-0 found the edge cases already live and fixes them:

* a map press releases the line's focus (pinned elsewhere), after which the
  next bare key was a HOTKEY — `Soult, march to `, a click on the map, then
  `e` ENDED THE TURN. Keys now go to a draft (type-through);
* a dispatch TODAY chip (and the tutor's) wrote OVER a half-typed order. An
  offer now waits beside the line, and taking it parks the draft one Tab
  away; the parked draft comes back when control returns;
* the end-turn warning, then any chip, then a bare Enter on the empty line
  ended the turn — only the terminal path disarmed the latch. Every sender
  now retires it;
* the province panel's chips posted behind a typed command still on the wire.

CC-1: a map click while the caret waits for a name WRITES the name (a
province, or the piece clicked), the suggestion row is clickable, the piece in
FRONT wins the hover, and the map lights the province the draft names.

The client pins are DRIVEN: `tools/cc_client_harness.gd` boots the real
`main.tscn` behind an API stub on the real boot board and presses real keys
through `root.push_input`. They SKIP when the engine is absent — and a skip
is not a pass.
"""

import json
import os
import re
import subprocess

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.display_names import humanize_entity_name
from tests import _chip_census as C

REPO = C.REPO
PROJECT = C.PROJECT
HARNESS = REPO / "tools" / "cc_client_harness.gd"
MAIN_GD = PROJECT / "scripts" / "main.gd"
MAP_GD = PROJECT / "scenes" / "map_renderer_base.gd"


def _src(path):
    return path.read_text(encoding="utf-8")


def _func(src, name):
    start = src.index(f"func {name}(")
    nxt = src.find("\nfunc ", start + 1)
    return src[start:] if nxt < 0 else src[start:nxt]


# ═══ the source pins ════════════════════════════════════════════════════════

class TestEverySenderRetiresTheLatch:
    """The end-turn confirmation is a latch a SEND must disarm — the player
    moved on. Only `_execute_command` used to (pinned in its own words by
    `test_ux_fixes_2026_08_23.py`); every other sender now calls the one
    helper. `_send_end_turn` IS the confirmation, and `_on_proposal_confirm_
    choice` answers an envoy inside the warning's own "review the envoys"
    instruction, which keeps the latch armed by design."""

    EXEMPT = {"_send_end_turn", "_execute_command", "_on_proposal_confirm_choice"}

    def _senders(self):
        src = _src(MAIN_GD)
        out = {}
        for m in re.finditer(r"\nfunc (\w+)\(", src):
            body = _func(src, m.group(1))
            if ("api_client.send_command(" in body
                    or "api_client.send_structured_command(" in body):
                out[m.group(1)] = body
        return out

    def test_the_senders_are_the_known_set(self):
        senders = set(self._senders())
        assert len(senders) >= 13, senders

    def test_every_sender_retires_the_latch_before_it_sends(self):
        for name, body in self._senders().items():
            if name in self.EXEMPT:
                continue
            assert "_retire_line_latches()" in body, name
            first_send = min(i for i in (body.find("api_client.send_command("),
                                         body.find("api_client.send_structured_command("))
                             if i >= 0)
            assert body.index("_retire_line_latches()") < first_send, name

    def test_the_helper_disarms_the_latch_and_the_offer(self):
        body = _func(_src(MAIN_GD), "_retire_line_latches")
        for clear in ("_awaiting_end_turn_confirmation = false",
                      'pending_relay_command = ""', '_offered_command = ""'):
            assert clear in body, clear

    def test_the_panel_chip_waits_for_a_command_on_the_wire(self):
        body = _func(_src(MAIN_GD), "_on_region_panel_command")
        guard = body.index("if not command_input.editable:")
        assert guard < body.index("_chip_command_in_flight = true")


class TestTheMapRecordsWhatTheClickCarried:

    def test_the_signal_keeps_its_one_argument(self):
        src = _src(MAP_GD)
        assert "region_clicked.emit(clicked_region)" in src
        assert "signal region_clicked(region_name)" in src

    def test_the_piece_and_the_modifiers_are_recorded_before_any_emit(self):
        src = _src(MAP_GD)
        left = src[src.index("elif event.button_index == MOUSE_BUTTON_LEFT:"):]
        left = left[:left.index("elif event.button_index == MOUSE_BUTTON_RIGHT:")]
        record = left.index("last_click_marshal =")
        assert record < left.index("fleet_clicked.emit(")
        assert record < left.index("region_clicked.emit(clicked_region)")
        assert "last_click_shift = event.shift_pressed" in left

    def test_the_front_piece_wins_the_hover(self):
        body = _func(_src(MAP_GD), "_refresh_hover_state")
        assert "rect.end.y >= front_bottom" in body


class TestTheHarness:

    def test_the_harness_is_in_the_parse_check(self):
        text = (REPO / "tools" / "godot_parse_check.gd").read_text(encoding="utf-8")
        assert "res://../../tools/cc_client_harness.gd" in text


# ═══ the driven pins ════════════════════════════════════════════════════════

def _pick_board():
    gs = C.game_state_now()
    with TestClient(M.app) as client:
        topology = client.get("/map_topology").json()
    keys = sorted(gs["marshals"])
    own_key = "Ney" if "Ney" in keys else keys[0]
    second_key = "Soult" if "Soult" in keys and own_key != "Soult" else next(k for k in keys if k != own_key)
    enemies = gs.get("enemies") or {}
    at_war = [k for k, v in enemies.items() if isinstance(v, dict) and v.get("at_war_with_player")]
    enemy_key = "ArchdukeCharles" if "ArchdukeCharles" in at_war else (at_war or sorted(enemies) or ["Mack"])[0]
    regions = sorted(gs["map_data"])
    province = "Moravia" if "Moravia" in regions else regions[0]
    spaced = next(r for r in regions if " " in r)
    return {
        "game_state": gs,
        "topology": topology,
        "own_marshal": humanize_entity_name(own_key),
        "second_marshal": humanize_entity_name(second_key),
        "second_marshal_key": second_key,
        "second_location": gs["marshals"][second_key].get("location", ""),
        "enemy_key": enemy_key,
        "enemy_shown": humanize_entity_name(enemy_key),
        "province": province,
        "spaced_province": spaced,
    }


@pytest.fixture(scope="module")
def board():
    with pytest.MonkeyPatch.context() as mp:
        C.board_env(mp)
        return _pick_board()


@pytest.fixture(scope="module")
def driven(board, tmp_path_factory):
    exe = C.engine()
    if exe is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    work = tmp_path_factory.mktemp("cc")
    out = work / "out.json"
    log = work / "godot.log"
    spec = work / "spec.json"
    spec.write_text(json.dumps(dict(board, out=str(out))), encoding="utf-8")
    env = dict(os.environ, CC_SPEC=str(spec))
    proc = subprocess.run(
        [exe, "--headless", "--path", str(PROJECT), "--log-file", str(log),
         "--script", str(HARNESS)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=300, env=env, cwd=str(PROJECT))
    if not out.is_file():
        pytest.fail("the harness wrote no result\n"
                    f"exit={proc.returncode}\nstderr tail:\n{proc.stderr[-2000:]}")
    # UXR3-83 (S15, October 26, 2026): a chip label binds its spaces (U+00A0)
    # in the bbcode; this door reads them as spaces, as the instruments do.
    result = json.loads(out.read_text(encoding="utf-8").replace("\u00a0", " "))
    assert "error" not in result, result.get("error")
    text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    result["script_errors"] = text.count("SCRIPT ERROR")
    result["script_error_lines"] = [ln for ln in text.splitlines() if "SCRIPT ERROR" in ln][:5]
    return result


class TestTheHarnessRanClean:

    def test_no_script_errors(self, driven):
        assert driven["script_errors"] == 0, driven["script_error_lines"]


class TestAnOfferNeverOverwritesADraft:
    """CC-0 s1/s2/s7 — the dispatch TODAY chip, the tutor, a relayed tail."""

    def test_the_draft_stays_and_the_offer_waits_at_the_head_of_the_row(self, driven, board):
        draft = board["own_marshal"] + ", march to " + board["province"][:3]
        assert driven["s1_line_kept"] == draft
        assert driven["s1_offered"] == board["second_marshal"] + ", fortify"
        assert driven["s1_row_head"] == driven["s1_offered"]

    def test_tab_takes_the_offer_and_parks_the_draft(self, driven, board):
        draft = board["own_marshal"] + ", march to " + board["province"][:3]
        assert driven["s1_line_after_tab"] == board["second_marshal"] + ", fortify"
        assert driven["s1_parked"] == draft
        assert driven["s1_row_head_after_tab"] == draft

    def test_tab_again_swaps_back(self, driven, board):
        draft = board["own_marshal"] + ", march to " + board["province"][:3]
        assert driven["s1_line_after_swap"] == draft
        assert driven["s1_offered_after_swap"] == board["second_marshal"] + ", fortify"
        assert driven["s1_sends"] == []   # nothing was ever sent

    def test_the_parked_draft_comes_back_when_control_returns(self, driven, board):
        draft = board["own_marshal"] + ", march to " + board["province"][:3]
        assert driven["s2_sent"] == ["send:" + board["second_marshal"] + ", fortify"]
        assert driven["s2_line_while_in_flight"] == ""
        assert driven["s2_line_at_return"] == draft

    def test_a_relayed_tail_over_a_draft_waits_beside_it(self, driven, board):
        tail = board["own_marshal"] + ", support " + board["second_marshal"]
        assert driven["s7_line"] == board["second_marshal"] + ", mar"
        assert driven["s7_offered"] == tail
        assert driven["s7_last_relay_fill"] == tail   # still the unchanged tail


class TestTypingAfterAMapClick:
    """CC-0 s3/s4 — the user's edge case: type, click the map, keep typing."""

    def test_e_goes_to_the_draft_and_does_not_end_the_turn(self, driven, board):
        assert driven["s3_line"] == board["own_marshal"] + ", march to e"
        assert driven["s3_focused"] is True
        assert driven["s3_sends"] == []

    def test_the_hotkey_still_ends_the_turn_on_an_empty_line(self, driven):
        """The control arm — the pin above is sensitive, not vacuous."""
        assert driven["s3_control_sends"] == ["send:end turn"]

    def test_the_arrows_still_pan(self, driven, board):
        assert driven["s4_focused_after_arrow"] is False
        assert driven["s4_line"] == board["own_marshal"] + ", march to "

    def test_backspace_edits_the_draft(self, driven, board):
        assert driven["s4_line_after_backspace"] == board["own_marshal"] + ", march to"


class TestTheNextOrdersKeysLand:
    """CC-X10 (s8) — found by the Mode C capture of this row: after an order
    was sent with Enter, Godot 4.4's LineEdit left EDITING and kept focus, so
    the control-return `grab_focus()` re-armed nothing and every key of the
    next order was dropped until the player clicked the line. Reproduced on
    the untouched client (`04e2348b`) before the fix."""

    def test_the_first_order_is_typed_and_sent(self, driven):
        assert driven["s8_typed_first"] == "ab"
        assert driven["s8_sent"] == ["send:ab"]

    def test_the_line_is_editing_when_control_returns(self, driven):
        assert driven["s8_editing_at_return"] is True

    def test_the_next_orders_keys_land(self, driven):
        assert driven["s8_line_after_return"] == "cd"

    def test_a_focused_line_that_is_not_editing_still_takes_a_key(self, driven):
        assert driven["s8b_line"] == "cdx"

    def test_the_line_keeps_editing_on_submit(self):
        src = _src(MAIN_GD)
        assert "command_input.keep_editing_on_text_submit = true" in src
        body = _func(src, "set_input_enabled")
        assert body.index("command_input.grab_focus()") < body.index("_resume_editing()")


class TestTheLatchAndTheWire:
    """CC-0 s5/s6."""

    def test_a_chip_after_the_warning_disarms_it(self, driven, board):
        assert driven["s5_sends"] == ["send:" + board["second_marshal"] + ", drill"]
        assert driven["s5_latch_after"] is False

    def test_a_panel_chip_waits_for_a_command_on_the_wire(self, driven):
        assert driven["s6_sends"] == []
        assert driven["s6_latch"] is False


class TestClickNamesIntoTheLine:
    """CC-1 c1…c8."""

    def test_a_province_click_writes_the_name_where_the_caret_waits(self, driven, board):
        assert driven["c1_line"] == board["own_marshal"] + ", march to " + board["province"]
        assert driven["c1_panel_open"] is False
        assert driven["c1_focused"] is True

    def test_a_typed_prefix_of_the_name_is_replaced(self, driven, board):
        assert driven["c2_line"] == board["own_marshal"] + ", march to " + board["province"]

    def test_a_two_word_name_is_completed_across_the_space(self, driven, board):
        assert driven["c3_line"] == board["own_marshal"] + ", march to " + board["spaced_province"]

    def test_with_no_name_slot_the_click_opens_the_panel_as_before(self, driven, board):
        assert driven["c4_line"] == board["own_marshal"] + ", ho"
        assert driven["c4_panel_open"] is True

    def test_a_piece_clicked_writes_the_mans_shown_name(self, driven, board):
        assert driven["c5_line"] == board["own_marshal"] + ", attack " + board["enemy_shown"]

    def test_shift_on_an_empty_line_makes_an_own_piece_the_addressee(self, driven, board):
        assert driven["c6_line"] == board["second_marshal"] + ", "

    def test_shift_on_an_empty_line_writes_a_province(self, driven, board):
        assert driven["c7_line"] == board["province"]

    def test_the_rest_of_the_draft_is_untouched(self, driven, board):
        assert driven["c8_line"] == (board["own_marshal"] + ", march to " + board["province"]
                                     + " then attack " + board["enemy_shown"])


class TestTheRowAndTheMap:
    """CC-1 c9…c11."""

    def test_a_click_on_an_offer_is_tab(self, driven):
        assert driven["c9_offers"], "the row offered nothing to click"
        assert driven["c9_line"] == driven["c9_clicked"]
        assert driven["c9_sends"] == []

    def test_the_piece_in_front_wins_the_hover(self, driven):
        assert driven["c10_hovered"] == "Front"

    def test_the_map_lights_the_province_the_draft_names(self, driven, board):
        assert driven["c11_glow"] == board["province"]
        assert driven["c11_glow_addressee"] == board["second_location"]
        assert driven["c11_glow_cleared"] == ""
