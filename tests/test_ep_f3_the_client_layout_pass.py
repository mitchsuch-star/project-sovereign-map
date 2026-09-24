"""Row EP, slice F3 — "The client layout pass" (`docs/ENDGAME_PLAN.md` §1 F3).

Seven rows from the September 23, 2026 live review (`BUG_FIXES.md` §Live
Review, `DESIGN_REFINEMENT.md` LV-D3), each at the surface the player reads:

* **LV-5** — the marshal-petition body was cut off below the fold and a
  closed arm showed NO reason (it rendered under the last button, off-screen,
  and twice when it did). The body sizes to its text (relax_last), a closed
  arm's reason is one line under the header, never duplicated.
* **LV-14(b)** — the settlement table's Press/Ease/Drop chips were a
  three-column grid under a 96px floor that clipped the third court. One row
  per court now, in their own scroll block whose floor follows the rows.
* **LV-15** — the wizard's action chips ran off the panel with the gate
  reason clipped and a horizontal scrollbar under the list. Chips wrap, the
  reason is its own smaller line, the sideways scroll is gone.
* **LV-16** — campaign-log rows were prefixed with LETTERS (`D An envoy…`).
  Glyphs from the phosphor set the rail uses; the letters stay the fallback.
* **LV-20** — the wizard's step 1 opened a blank gap above the list, and the
  Sponsor chip told the player to "aim" at France a court whose design was
  already aimed at France. One-line prompt; honest copy; hidden at war.
* **LV-22** — a battle that ENDS IN A CAPTURE swallowed Berthier's report
  (the capture route rendered the message only) and printed the message
  twice on the muster road. The order's result renders first, once.
* **LV-D3** — the STRATEGIC ORDERS recap modal blocked every turn start.
  Retired: the terminal block stays, the dispatch's MARSHAL STATUS carries
  each order's ETA from the report's own arithmetic, and only an order that
  needs an ANSWER raises a modal (its own interrupt popup).

The client classes drive the REAL `main.tscn` headlessly
(`tools/ep_f3_client_layout_harness.gd`) on payloads taken from the real
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
from backend.commands import strategic as S
from backend.models.marshal import StrategicCondition, StrategicOrder
from backend.game_logic import dispatch as D
from backend.game_logic import jealousy as J
from backend.game_logic.diplomacy import get_available_diplomatic_actions
from backend.models.world_state import WorldState
from tests import _chip_census as C

REPO = C.REPO
PROJECT = C.PROJECT
SCRIPTS = C.SCRIPTS
SCENES = PROJECT / "scenes"
HARNESS = REPO / "tools" / "ep_f3_client_layout_harness.gd"
MAIN_GD = SCRIPTS / "main.gd"
SCENARIO = PROJECT / "assets" / "maps" / "europe_1805.json"

REPORT_HEADER = "--- Berthier's Report ---"
UPDATES_HEADER = "--- Strategic Order Updates ---"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _read(path):
    return path.read_text(encoding="utf-8")


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


@pytest.fixture(scope="module")
def _boot():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def world(_boot):
    return WorldState.from_dict(_boot.to_dict())


# ═══════════════════════════════════════════════════════════════════════════
# LV-D3 — the order tells its ETA from ONE arithmetic
# ═══════════════════════════════════════════════════════════════════════════


def _order(cmd, target, path, condition=None):
    order = StrategicOrder(command_type=cmd, target=target, target_type="region",
                           started_turn=3, original_command="test")
    order.path = list(path)
    order.condition = condition
    return order


class TestTheOrderTellsItsEta:

    def test_the_road_ahead_is_the_reading(self):
        assert S.order_turns_remaining(_order("MOVE_TO", "Vienna", ["A", "B", "C"]), 5) == 3
        assert S.order_turns_remaining(_order("MOVE_TO", "Vienna", []), 5) == 0

    def test_the_phrases(self):
        assert S.order_eta_phrase(_order("MOVE_TO", "Vienna", ["A"]), 5) == " — arrives next turn"
        assert S.order_eta_phrase(_order("MOVE_TO", "Vienna", ["A", "B", "C"]), 5) == " — 3 turns out"
        assert S.order_eta_phrase(_order("PURSUE", "Mack", ["A"]), 5) == " — closes next turn"
        assert S.order_eta_phrase(_order("PURSUE", "Mack", ["A", "B"]), 5) == " — 2 turns behind him"
        assert S.order_eta_phrase(_order("SUPPORT", "Davout", ["A"]), 5) == " — joins him next turn"
        assert S.order_eta_phrase(_order("MOVE_TO", "Vienna", []), 5) == ""

    def test_a_timed_hold_counts_its_turns_from_the_dispatch_side(self):
        cond = StrategicCondition(max_turns=3)
        order = _order("HOLD", "Swabia", [], condition=cond)
        # The tick (turn 3 being closed) counts the issuing turn; the dispatch
        # at the start of turn 4 has two turns still to play.
        assert S.order_turns_remaining(order, 3) == 2
        assert S.order_turns_remaining(order, 4, including_current=False) == 2
        assert S.order_eta_phrase(order, 4) == " — holds 2 more turns"
        assert S.order_eta_phrase(order, 5) == " — holds 1 more turn"

    def test_a_bare_fake_order_is_tolerated(self):
        class Fake:
            command_type = "MOVE_TO"
            target = "Vienna"
        assert S.order_turns_remaining(Fake(), 5) == 0
        assert S.order_eta_phrase(Fake(), 5) == ""

    def test_the_dispatch_status_carries_the_eta(self, world):
        ney = world.marshals["Ney"]
        ney.strategic_order = _order("MOVE_TO", "Vienna", ["Swabia", "Bavaria"])
        status, note = D._derive_marshal_status(ney, world)
        assert status == "en_route"
        assert note == "Moving to Vienna — 2 turns out."

    def test_the_arrival_wording_and_the_letter_survive(self, world):
        soult = world.marshals["Soult"]
        soult.strategic_order = _order("MOVE_TO", "Vienna", ["Vienna"])
        status, note = D._derive_marshal_status(soult, world)
        assert status == "en_route"
        assert note.startswith("Moving to Vienna — arrives next turn.")
        if getattr(soult, "personality", "") == "literal":
            assert note.endswith("(to the letter)")


class TestTheRecapModalIsRetired:

    def test_the_turn_start_never_raises_the_popup(self):
        body = _func_body(_read(MAIN_GD), "_show_strategic_reports")
        assert "show_reports(" not in body, "the recap modal is retired (LV-D3)"
        assert "_on_strategic_report_dismissed()" in body
        assert UPDATES_HEADER in body, "the terminal block is the record"

    def test_the_scene_stays_registered_and_dismissable(self):
        src = _read(MAIN_GD)
        assert 'dialog_manager.register("strategic_report"' in src
        assert "func _unhandled_input" in _read(SCRIPTS / "strategic_report_popup.gd")

    def test_the_report_and_the_dispatch_share_the_arithmetic(self):
        src = _read(REPO / "backend" / "commands" / "strategic.py")
        body = src[src.index("def process_strategic_orders"):]
        assert "remaining = order_turns_remaining(order, int(world.current_turn))" in body
        dsrc = _read(REPO / "backend" / "game_logic" / "dispatch.py")
        assert "eta = order_eta_phrase(order, int(world.current_turn))" in dsrc


# ═══════════════════════════════════════════════════════════════════════════
# LV-22 — the capture waits behind the report (source half)
# ═══════════════════════════════════════════════════════════════════════════


class TestTheCaptureRouteIsResultFirst:

    def test_the_route_is_marked(self):
        src = _read(MAIN_GD)
        block = src[src.index("_post_hud_response_routes = ["):]
        block = block[:block.index("]")]
        row = next(ln for ln in block.splitlines() if '"id": "capture_choice"' in ln)
        assert '"result_first": true' in row

    def test_the_renderer_stamps_and_the_capture_reads_the_stamp(self):
        src = _read(MAIN_GD)
        display = _func_body(src, "_display_result")
        assert 'response["_result_rendered"] = true' in display
        capture = _func_body(src, "_show_capture_choice_dialog")
        assert 'not bool(response.get("_result_rendered", false))' in capture

    def test_the_muster_road_renders_before_it_routes(self):
        body = _func_body(_read(MAIN_GD), "_on_interrupt_response")
        assert body.index("_display_result(response)") < body.index(
            "_route_response_ui(response, _post_hud_response_routes)")


# ═══════════════════════════════════════════════════════════════════════════
# LV-20 — the Sponsor chip says what the money does
# ═══════════════════════════════════════════════════════════════════════════


def _chips(world, nation):
    return {a["action"]: a for a in get_available_diplomatic_actions(world, nation)}


class TestTheSponsorChipSpeaksTrue:

    def _pacify(self, world, nation):
        key = world._make_diplo_key("France", nation)
        if world.diplomatic_states.get(key) == "WAR":
            world.diplomatic_states[key] = "PEACE"
        world.invalidate_bloc_members_cache()

    def test_a_court_at_war_whose_design_is_against_us_gets_no_sponsor_chip(self, world):
        assert world.is_at_war("France", "Britain")
        assert "sponsor_design" not in _chips(world, "Britain")
        assert "buy_off_design" in _chips(world, "Britain"), "only the sponsor chip hides"

    def test_at_peace_the_chip_says_it_funds_the_design_against_us(self, world):
        self._pacify(world, "Britain")
        chip = _chips(world, "Britain")["sponsor_design"]
        assert "Fund the design they already pursue against us" in chip["effect_text"]
        assert "Aim their court" not in chip["effect_text"]
        assert chip["available"] is False
        assert "aimed at France" in chip["disabled_reason"]

    def test_a_court_aimed_elsewhere_keeps_the_aiming_copy(self, world):
        chip = _chips(world, "Prussia")["sponsor_design"]
        assert chip["effect_text"].startswith("Aim their court at ")
        assert "against us" not in chip["effect_text"]


# ═══════════════════════════════════════════════════════════════════════════
# LV-16 — the log rows are glyphs
# ═══════════════════════════════════════════════════════════════════════════


class TestTheLogRowsAreGlyphs:

    def test_every_category_glyph_exists_on_disk(self):
        src = _read(SCRIPTS / "campaign_log.gd")
        block = src[src.index("const CATEGORY_GLYPHS = {"):]
        block = block[:block.index("}")]
        names = re.findall(r'"(\w+)": "([\w-]+)"', block)
        assert {c for c, _ in names} == {"combat", "territory", "economy", "command", "diplomacy"}
        for _, glyph in names:
            assert (PROJECT / "assets" / "ui" / "icons" / "phosphor" / f"{glyph}.svg").is_file(), glyph

    def test_the_prefix_is_the_tinted_glyph_and_the_letter_is_the_fallback(self):
        src = _read(SCRIPTS / "campaign_log.gd")
        body = _func_body(src, "_category_icon")
        assert "Utils.bb_icon(path, 12, color)" in body
        assert "ResourceLoader.exists(path)" in body
        assert "CATEGORY_LETTERS" in body
        assert "_category_icon(str(category))" in src
        assert "CATEGORY_ICONS" not in src


# ═══════════════════════════════════════════════════════════════════════════
# LV-5 — the petition names its closed arm above the fold
# ═══════════════════════════════════════════════════════════════════════════


def _closed_command_petition(world):
    """Murat's confrontation with Ney, with Murat sent to Brittany (no enemy
    within his reach), so the command arm arrives CLOSED with the backend's
    reason — the live review's frame."""
    murat = world.marshals["Murat"]
    ney = world.marshals["Ney"]
    murat.location = "Brittany"
    murat.strategic_order = None
    with _quiet():
        status = J.queue_confrontation_petition(world, murat, ney, level=0)
    assert status == J.PETITION_QUEUED, status
    return world.pending_marshal_petition


class TestThePetitionNamesItsClosedArm:

    def test_the_backend_sends_the_reason_the_line_prints(self, world):
        petition = _closed_command_petition(world)
        arm = next(o for o in petition["options"] if o["id"] == J.COMMAND_ARM_ID)
        assert arm["enabled"] is False and arm["available"] is False
        assert arm["unavailable_reason"], "a closed arm always names its reason"
        assert arm["detail"] == arm["unavailable_reason"], "the duplicate the client drops"

    def test_the_scene_has_the_gate_line_under_the_header(self):
        scene = _read(SCENES / "marshal_petition_dialog.tscn")
        gate = scene.index('[node name="GateLabel" type="Label"')
        assert scene.index('[node name="HSeparator" type="HSeparator"') < gate < scene.index(
            '[node name="BodyLabel" type="RichTextLabel"')
        block = scene[gate:scene.index("[node", gate + 10)]
        assert "autowrap_mode = 3" in block and "visible = false" in block

    def test_the_script_fills_the_gate_line_and_drops_the_duplicate(self):
        src = _read(SCRIPTS / "marshal_petition_dialog.gd")
        show = _func_body(src, "show_petition")
        assert 'option.get("unavailable_reason", "")' in show
        assert '" is closed — "' in show
        assert "gate_label.visible = not closed_lines.is_empty()" in show
        add = _func_body(src, "_add_option")
        assert 'if not is_enabled and reason != "" and detail == reason:' in add
        assert 'reason + "  " + detail' not in add

    def test_the_body_sizes_to_its_text_and_yields_last(self):
        src = _read(SCRIPTS / "marshal_petition_dialog.gd")
        assert 'body_label.set_meta("relax_last", true)' in _func_body(src, "_ready")
        fit = _func_body(src, "_fit_body")
        assert "get_content_height()" in fit
        assert "clampf(wanted, 120.0, 360.0)" in fit
        assert "Utils.clamp_centered_panel($PanelContainer)" in fit
        assert 'call_deferred("_fit_body")' in _func_body(src, "show_petition")


# ═══════════════════════════════════════════════════════════════════════════
# LV-14(b) — one row per court
# ═══════════════════════════════════════════════════════════════════════════


class TestTheSettlementRowsPerCourt:

    def test_the_scene_is_a_column_of_rows(self):
        scene = _read(SCENES / "proposal_confirm_popup.tscn")
        assert '[node name="Tier2ButtonContainer" type="VBoxContainer"' in scene
        assert "columns = 3" not in scene.split('[node name="Tier2ButtonContainer"')[1].split("[node")[0]

    def test_the_builder_groups_by_court_and_derives_the_floor(self):
        body = _func_body(_read(SCRIPTS / "proposal_confirm_popup.gd"), "_add_settlement_tier2_buttons")
        assert "court_rows.append({" in body
        assert 'Utils.display_nation_name(str(row.get("nation", "?")))' in body
        assert "tier2_button_container.add_child(line)" in body
        assert "line.add_child(btn)" in body
        assert "float(court_rows.size()) * 42.0 + 10.0" in body
        assert "vp.get_visible_rect().size.y * 0.30" in body


# ═══════════════════════════════════════════════════════════════════════════
# LV-15 + LV-20 — the wizard wraps, and its first step has no gap
# ═══════════════════════════════════════════════════════════════════════════


class TestTheWizardWraps:

    def test_the_chip_wraps_and_the_reason_is_its_own_line(self):
        src = _read(SCRIPTS / "diplomacy_wizard.gd")
        body = _func_body(src, "_add_action_button")
        assert "btn.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART" in body
        assert "btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL" in body
        assert 'text += "  [" + disabled_reason + "]"' not in body
        assert "reason_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART" in body
        assert "scroll_container.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED" in _func_body(src, "_ready")

    def test_step_one_pins_the_prompt_and_steps_two_and_three_expand(self):
        src = _read(SCRIPTS / "diplomacy_wizard.gd")
        assert "_lay_out_prompt(1)" in _func_body(src, "open")
        assert "_lay_out_prompt(1)" in _func_body(src, "_go_back")
        assert "_lay_out_prompt(2)" in _func_body(src, "open_for_nation")
        assert "_lay_out_prompt(2)" in _func_body(src, "_on_nation_selected")
        assert "_lay_out_prompt(2)" in _func_body(src, "_on_formables_pressed")
        lay = _func_body(src, "_lay_out_prompt")
        assert "Control.SIZE_FILL" in lay and "Control.SIZE_EXPAND_FILL" in lay

    def test_the_offline_refit_is_the_live_clamp(self):
        assert "Utils.clamp_centered_panel($PanelContainer)" in _func_body(
            _read(SCRIPTS / "diplomacy_wizard.gd"), "refit")


# ═══════════════════════════════════════════════════════════════════════════
# The payloads, from the real endpoints
# ═══════════════════════════════════════════════════════════════════════════


def _post(client, path, body=None):
    response = client.post(path, json=body or {})
    assert response.status_code == 200, (path, response.status_code, response.text[:300])
    return response.json()


def _new_game(client):
    with _quiet():
        return _post(client, "/new_game")


def _payloads():
    client = TestClient(M.app)
    _new_game(client)
    topology = client.get("/map_topology").json()
    # LV-22: Archduke John cut to a remnant on AUSTRIAN Tyrol, so Massena's
    # attack destroys him and the province falls — the response carries the
    # report AND the Plunder/Secure question. (Mack stands on Bavaria's soil:
    # driving him off an ally's province takes nothing.)
    M.world.marshals["ArchdukeJohn"].strength = 600
    for m in M.world.marshals.values():
        # Charles at Carniola is ADJACENT and marches in as a reinforcement
        # (54,000 committed on the first staging); every other Austrian corps
        # goes to Vienna, two provinces off, beyond reinforcement reach.
        if m.nation == "Austria" and m.name != "ArchdukeJohn":
            m.location = "Vienna"
            m.strategic_order = None
    random.seed(7)
    with _quiet():
        capture = _post(client, "/command", {"command": "Massena, attack Archduke John"})
    # LV-D3: a standing march through French soil (no enemy on the road, so
    # no interrupt), then an end turn.
    _new_game(client)
    with _quiet():
        march = _post(client, "/command", {"command": "Davout, march to Brittany"})
        end_turn = _post(client, "/command", {"command": "end turn"})
    return {"topology": topology, "capture": capture, "march": march,
            "end_turn": end_turn}


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


class TestThePayloadsAreTheReproduction:

    def test_the_attack_ends_in_a_capture_with_its_report(self, payloads):
        capture = payloads["capture"]
        assert capture["success"] is True
        assert capture.get("pending_capture_choice") is True, capture.get("message")
        assert capture.get("battle_report"), "the report the capture route used to swallow"
        assert str(capture.get("message", "")).strip()
        assert capture.get("capture_data", {}).get("region")

    def test_the_end_turn_carries_orders_and_the_briefing(self, payloads):
        assert payloads["march"]["success"] is True, payloads["march"].get("message")
        end_turn = payloads["end_turn"]
        reports = end_turn.get("strategic_reports") or []
        assert reports, "a standing order reports at the tick"
        davout = next(r for r in reports if r.get("marshal") == "Davout")
        assert davout.get("requires_input", False) is False
        assert int(davout.get("turns_remaining", -1)) >= 1
        assert end_turn.get("enemy_phase") is not None
        marshals = end_turn["morning_dispatch"]["marshals"]
        row = next(m for m in marshals if m["name"] == "Davout")
        assert row["status"] == "en_route"
        assert " — " in row["status_note"], row["status_note"]
        assert ("turns out" in row["status_note"]
                or "arrives next turn" in row["status_note"]), row["status_note"]

    def test_the_dispatch_eta_is_the_reports_own_number(self, payloads):
        end_turn = payloads["end_turn"]
        report = next(r for r in end_turn["strategic_reports"] if r.get("marshal") == "Davout")
        row = next(m for m in end_turn["morning_dispatch"]["marshals"] if m["name"] == "Davout")
        remaining = int(report["turns_remaining"])
        if remaining == 1:
            assert "arrives next turn" in row["status_note"]
        else:
            assert f"{remaining} turns out" in row["status_note"]


# ═══════════════════════════════════════════════════════════════════════════
# The client, DRIVEN
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="module")
def driven(payloads, tmp_path_factory):
    exe = C.engine()
    if exe is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    work = tmp_path_factory.mktemp("epf3")
    out = work / "out.json"
    log = work / "godot.log"
    spec = work / "spec.json"
    spec.write_text(json.dumps(dict(payloads, out=str(out))), encoding="utf-8")
    env = dict(os.environ, EPF3_SPEC=str(spec))
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
    return result


class TestTheHarnessIsParsed:

    def test_the_harness_is_in_the_parse_check(self):
        src = _read(REPO / "tools" / "godot_parse_check.gd")
        assert "res://../../tools/ep_f3_client_layout_harness.gd" in src


class TestTheCaptureWaitsBehindTheReport:

    def test_the_harness_ran_clean(self, driven):
        assert driven["script_errors"] == 0

    def test_the_command_path_prints_the_report_once_then_asks(self, driven, payloads):
        text = driven["command_terminal"]
        assert text.count(REPORT_HEADER) == 1, text
        first_line = str(payloads["capture"]["message"]).splitlines()[0][:40]
        assert text.count(first_line) == 1, text
        assert "Plunder or Secure?" in text
        assert text.index(REPORT_HEADER) < text.index("Plunder or Secure?")
        assert driven["command_capture_raised"] is True
        assert driven["command_modal_open"] is True

    def test_the_muster_road_prints_the_report_once_and_the_message_once(self, driven, payloads):
        text = driven["muster_terminal"]
        assert text.count(REPORT_HEADER) == 1, text
        first_line = str(payloads["capture"]["message"]).splitlines()[0][:40]
        assert text.count(first_line) == 1, text
        assert "Plunder or Secure?" in text
        assert driven["muster_capture_raised"] is True


class TestTheTurnStartRaisesNoRecap:

    def test_the_enemy_phase_still_shows(self, driven):
        assert driven["enemy_phase_raised"] is True

    def test_the_recap_never_stands_after_the_enemy_phase(self, driven):
        """The retired modal is never raised. What MAY stand is a surface a
        control-return tail legitimately raises (a stashed diorama, a
        petition, the letter-book) — never the strategic-report popup, and
        the command line is back unless one of those took the flow."""
        assert driven["strategic_report_popup_raised"] is False
        standing = driven.get("standing_after_end_turn", [])
        assert "strategic_report_popup" not in standing, standing
        assert driven["input_enabled_after_end_turn"] is True or standing, (
            "control returned to nobody")

    def test_the_block_and_the_briefing_carry_the_order(self, driven, payloads):
        text = driven["end_turn_terminal"]
        assert UPDATES_HEADER in text
        row = next(m for m in payloads["end_turn"]["morning_dispatch"]["marshals"]
                   if m["name"] == "Davout")
        assert "MARSHAL STATUS" in text
        assert row["status_note"] in text, row["status_note"]
        assert text.index(UPDATES_HEADER) < text.index("MARSHAL STATUS")
        assert "STRATEGIC ORDERS - Turn" not in text, "the modal's title never prints"
