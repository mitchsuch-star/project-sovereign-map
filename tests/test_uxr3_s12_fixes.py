"""UXR-3 fixes — Pre-Deploy S12 part 1 (October 13, 2026).

The S11 review (`docs/audits/UXR3_REVIEW_2026_10_13.md`) filed 84 rows against
the frozen `docs/UX_CHECKLIST_V1.json`. S12 part 1 fixes them by class:

  Part 1  the harness's gaps — the three popups the checklist names and the
          IQ-10 manifest had never shot (UXR3-56 … 58), shot under the
          checklist's own ids; and two defects found shooting them (UXR3-X1,
          UXR3-X2).

The re-read of every flipped item is `docs/audits/UXR3_REREAD_2026_10_13.md`;
its records are `docs/audits/uxr3_s12/`. Rules `SYSTEMS_REFERENCE.md` §113.6.

The pins are engine-free where the source is the subject, and DRIVEN (the real
Godot binary, headless) where behaviour is. A driven pin skips without the
engine, and a skip is not a pass.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys

import pytest

from tests import _chip_census as C

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
SCENES = PROJECT / "scenes"
TOOLS = REPO / "tools"
CHECKLIST = REPO / "docs" / "UX_CHECKLIST_V1.json"
sys.path.insert(0, str(TOOLS))

import iq10_capture_payloads as P  # noqa: E402
import iq10_run_captures as R  # noqa: E402
import uxr3_consistency_census as CEN  # noqa: E402
import uxr3_review as RV  # noqa: E402

NEVER_SHOT = ("objection_dialog", "capture_choice", "talleyrand_objection")


def _src(rel: str) -> str:
    return (PROJECT / rel).read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    """The body of one GDScript func (to the next top-level func)."""
    m = re.search(rf"(?ms)^(?:static )?func {re.escape(name)}\(.*?(?=^(?:static )?func |\Z)", src)
    assert m, name
    return m.group(0)


# ═══ Part 1 — the harness's gaps (UXR3-56 … 58) ═══════════════════════════════

class TestTheThreePopupsAreShotUnderTheChecklistsIds:
    @pytest.fixture(scope="class")
    def checklist(self) -> dict:
        return json.loads(CHECKLIST.read_text(encoding="utf-8"))

    def test_each_has_a_shot_row_named_by_the_checklist(self, checklist):
        rows = {s["id"]: s for s in R.SHOTS}
        named = {s["id"]: s for g in checklist["groups"] for s in g["surfaces"]}
        for sid in NEVER_SHOT:
            assert named[sid]["shot"] is None            # the frozen checklist, untouched
            row = rows[sid]
            assert row["scene"] == named[sid]["scene"], sid
            assert row["payload"] == sid and row["mode"] == "call", sid
            assert row["must_show"], sid

    def test_each_is_opened_the_way_main_gd_opens_it(self):
        rows = {s["id"]: s for s in R.SHOTS}
        main = _src("scripts/main.gd")
        assert rows["objection_dialog"]["method"] == "show_from_response"
        assert rows["capture_choice"]["method"] == "show_capture_choice"
        assert rows["capture_choice"]["args"] == ["$payload.capture_data"]
        assert "capture_choice_dialog.show_capture_choice(capture_data)" in main
        assert rows["talleyrand_objection"]["method"] == "show_objection"
        assert rows["talleyrand_objection"]["args"] == ["$payload.diplomatic_objection"]
        assert "talleyrand_objection_popup.show_objection(response.diplomatic_objection)" in main

    def test_the_payloads_come_from_the_rows_own_boards(self):
        assert P.CAPTURES["popups_s12"] is P.cap_popups_s12
        src = pathlib.Path(P.__file__).read_text(encoding="utf-8")
        body = src[src.index("def cap_popups_s12"):src.index("CAPTURES = {")]
        # B4b's staged board, imported — never re-typed
        assert 'test_module("test_b4b_the_one_tail")' in body and "T._payloads(mp)" in body
        # the deep-audit declaration road, on the unstaged boot
        assert 'cmd(c, "declare war on Prussia")' in body and 'cmd(c, "1")' in body

    def test_the_review_reads_them_under_their_own_ids(self):
        for sid in NEVER_SHOT:
            assert RV.shot_of({"id": sid, "shot": None}) == sid
        assert RV.shot_of({"id": "never_in_the_manifest", "shot": None}) is None
        assert RV.shot_of({"id": "x", "shot": "ledger_boot_forces"}) == "ledger_boot_forces"

    def test_their_own_files_carry_no_one_off_grey_or_size(self):
        cache: dict = {}
        for f in ("res://scenes/objection_dialog.tscn", "res://scripts/objection_dialog.gd",
                  "res://scenes/capture_choice_dialog.tscn", "res://scripts/capture_choice_dialog.gd",
                  "res://scenes/talleyrand_objection_popup.tscn",
                  "res://scripts/talleyrand_objection_popup.gd"):
            assert CEN.census_file(f, cache) == [], f


# ═══ UXR3-X1 — the objection dialog's mapping, one home ══════════════════════

class TestTheObjectionMappingLivesInTheDialog:
    def test_main_gd_opens_the_dialog_through_the_dialogs_own_mapping(self):
        main = _src("scripts/main.gd")
        body = _func(main, "_show_objection_dialog")
        assert "ObjectionDialogScript.data_from_response(response)" in body
        assert '"insist_penalty": objection.get(' not in main      # the hand-built copy is gone
        assert 'const ObjectionDialogScript := preload("res://scripts/objection_dialog.gd")' in main

    def test_the_mapping_carries_every_key_the_dialog_reads(self):
        dlg = _src("scripts/objection_dialog.gd")
        mapping = _func(dlg, "data_from_response")
        shown = _func(dlg, "show_objection")
        read = set(re.findall(r'objection_data\.get\("(\w+)"', shown)) | \
            set(re.findall(r'objection_data\.has\("(\w+)"\)', shown))
        built = set(re.findall(r'^\t\t"(\w+)":', mapping, re.M))
        assert read, "the dialog reads no keys?"
        assert read <= built, sorted(read - built)
        assert {"insist_ap_cost", "insist_note", "trust_gain_modifier"} <= built


@pytest.fixture(scope="module")
def driven_mapping(tmp_path_factory):
    exe = C.engine()
    if exe is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    work = tmp_path_factory.mktemp("uxr3_s12_map")
    out = work / "out.json"
    script = work / "objection_map_check.gd"
    script.write_text(
        "extends SceneTree\n"
        "func _init():\n"
        "\tvar S = load(\"res://scripts/objection_dialog.gd\")\n"
        "\tvar strategic = S.data_from_response({\"pending_objection\": true, \"marshal\": \"Ney\",\n"
        "\t\t\"trust\": 55, \"objection\": {\"marshal\": \"Ney\", \"tone\": \"firm\", \"message\": \"m\",\n"
        "\t\t\"trust_gain_modifier\": 0.5, \"insist_ap_cost\": 2,\n"
        "\t\t\"insist_note\": \"he must first go defensive\"}})\n"
        "\tvar tactical = S.data_from_response({\"marshal\": \"Lannes\", \"message\": \"t\",\n"
        "\t\t\"insist_note\": \"x\", \"insist_ap_cost\": 3, \"trust_gain_modifier\": 0.75})\n"
        "\tvar f = FileAccess.open(OS.get_environment(\"UXR3_OUT\"), FileAccess.WRITE)\n"
        "\tf.store_string(JSON.stringify({\"strategic\": strategic, \"tactical\": tactical}))\n"
        "\tf.close()\n"
        "\tquit(0)\n", encoding="utf-8")
    env = dict(os.environ, UXR3_OUT=str(out))
    proc = subprocess.run([exe, "--headless", "--path", str(PROJECT), "--script", str(script)],
                          capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=180, env=env, cwd=str(PROJECT), stdin=subprocess.DEVNULL)
    if not out.is_file():
        pytest.fail(f"the check wrote nothing\nexit={proc.returncode}\n{proc.stderr[-1500:]}")
    return json.loads(out.read_text(encoding="utf-8"))


class TestTheMappingDriven:
    def test_a_strategic_objection_carries_its_price_and_the_damper(self, driven_mapping):
        d = driven_mapping["strategic"]
        assert d["is_strategic"] is True and d["marshal"] == "Ney"
        assert d["insist_note"] == "he must first go defensive" and int(d["insist_ap_cost"]) == 2
        assert float(d["trust_gain_modifier"]) == 0.5
        assert int(d["trust"]) == 55                        # the response's own trust

    def test_a_tactical_objection_reads_the_top_level(self, driven_mapping):
        d = driven_mapping["tactical"]
        assert d["is_strategic"] is False and d["marshal"] == "Lannes"
        assert d["insist_note"] == "x" and int(d["insist_ap_cost"]) == 3
        assert float(d["trust_gain_modifier"]) == 0.75


# ═══ UXR3-X2 — the two popups fit their content ══════════════════════════════

class TestThePopupsFitTheirContent:
    @pytest.mark.parametrize("script, opener", [("objection_dialog.gd", "show_objection"),
                                                ("capture_choice_dialog.gd", "show_capture_choice")])
    def test_open_and_refit_shrink_after_the_clamp(self, script, opener):
        src = _src(f"scripts/{script}")
        for name in (opener, "refit"):
            body = _func(src, name)
            clamp = body.index("Utils.clamp_centered_panel($PanelContainer)")
            shrink = body.index("Utils.shrink_centered_panel_to_content($PanelContainer)")
            assert clamp < shrink, (script, name)

    def test_the_helper_only_ever_shrinks(self):
        body = _func(_src("scripts/utils.gd"), "shrink_centered_panel_to_content")
        assert "if need > 0.0 and need < have:" in body
        assert body.count("await panel.get_tree().process_frame") == 2


# ═══ Part 2 — R3 Contrast, by token (UXR3-3 … 6, 21, 22, 25, 32 … 35, 42, 47, 50 … 52) ═══
#
# Decided: a body-class row never takes a dim step below the floor step a0a0a8
# (`Utils.DIM_FLOOR_INDEX`). Every body use of COLOR_DIM (666670) and
# COLOR_DIMMED / COLOR_GREY (808080) became COLOR_INFO; a caption-class row
# keeps 808080 only where it reads >= 3 : 1 on its panel. Coloured text under
# the floor keeps its hue and lightens until it reads >= 4.5 : 1 (body) or
# >= 3 : 1 (caption) on its own panel. High contrast still raises every step.

import uxr2b_contrast_report as CR  # noqa: E402
from tests import _godot_scenes as GS  # noqa: E402

_DIM_TOKEN = re.compile(r'Utils\.COLOR_(?:DIMMED|GREY|DIM)\b|toned_hex\("(?:808080|666670)"\)')
# The one allowance: the tableau's two engraved Caption labels (the skip hint
# on the tray and a side's tail line), 808080 at >= 4.1 : 1 on its dark field.
CAPTION_KEEPS = {"battle_diorama.gd": 2}


class TestNoBodyLineTakesADimStepUnderTheFloor:
    def test_the_dim_tokens_survive_only_on_the_named_captions(self):
        found = {}
        for p in GS.client_scripts():
            if p.name == "utils.gd":
                continue
            n = len(_DIM_TOKEN.findall(GS.code_lines(GS.read(p))))
            if n:
                found[p.name] = n
        assert found == CAPTION_KEEPS, found

    def test_the_kept_ones_are_caption_labels(self):
        code = GS.code_lines(GS.read(SCRIPTS / "battle_diorama.gd"))
        for m in re.finditer(r"Color\(Utils\.COLOR_DIMMED\)", code):
            call = code[code.rfind("_mk_label(", 0, m.start()):m.end()]
            assert '&"Caption"' in call, call

    def test_the_floor_step_reads_on_every_panel_the_review_measured(self):
        info = CR._hex("a0a0a8")
        for bg in ("141926", "1a1a2e", "1f181d", "2a1e14", "1a1d27", "233043"):
            assert CR.ratio(info, CR._hex(bg)) >= CR.BODY_FLOOR, bg
        # 808080 kept on a caption still clears the caption floor there
        for bg in ("111b14", "0d141c", "131b24"):
            assert CR.ratio(CR._hex("808080"), CR._hex(bg)) >= CR.CAPTION_FLOOR, bg


# Each lightened colour, the panels the review measured it on, and its floor.
LIGHTENED = [
    # (file, the source line, new hex, panels, floor)
    ("diplomatic_ledger.gd", 'const COLOR_RED = "d16969"', "d16969", ("141926",), 4.5),
    ("enemy_phase_dialog.gd", 'const COLOR_ERROR = "d16969"', "d16969", ("1a1a2e",), 4.5),
    ("utils.gd", 'const COLOR_ERROR_CHIP = "d68686"', "d68686", ("233043",), 4.5),
    ("battle_diorama.gd", "const CRIMSON := Color(0.843, 0.388, 0.369, 1.0)", "d7635e",
     ("0d141c", "0e141c", "111a23", "111b14", "121b14", "121c15", "131b24"), 4.5),
    ("war_detail_popup.gd", 'const COLOR_RED = "#c36969"', "c36969", ("14141f",), 4.5),
    # the side tags and the ⚔ at full alpha
    ("war_detail_popup.gd", 'enemy_lbl.add_theme_color_override("font_color", Color(0.8, 0.5, 0.5, 1.0))',
     "cc8080", ("2c2a32", "2f2e33", "2f2f33", "332e36", "393133"), 3.0),
    ("war_detail_popup.gd", 'france_lbl.add_theme_color_override("font_color", Color(0.5, 0.6, 0.8, 1.0))',
     "8099cc", ("282a33", "2a2e33", "2c2d36"), 3.0),
    ("battle_diorama.gd", '_clash_label.add_theme_color_override("font_color", Utils.UI_GOLD)',
     "d9bf8c", ("374935", "2f3b45"), 4.5),
]


class TestColouredTextKeepsItsHueAndClearsTheFloor:
    @pytest.mark.parametrize("name, line, new, panels, floor", LIGHTENED,
                             ids=[f"{r[0]}:{r[2]}" for r in LIGHTENED])
    def test_the_new_value_is_in_the_source_and_reads(self, name, line, new, panels, floor):
        assert line in GS.code_lines(GS.read(SCRIPTS / name)), (name, line)
        for bg in panels:
            assert CR.ratio(CR._hex(new), CR._hex(bg)) >= floor, (new, bg)

    def test_the_red_chips_use_the_chip_red(self):
        for name in ("diplomatic_ledger.gd", "region_panel.gd"):
            code = GS.code_lines(GS.read(SCRIPTS / name))
            assert "Utils.COLOR_ERROR_CHIP" in code, name
        region = GS.code_lines(GS.read(SCRIPTS / "region_panel.gd"))
        assert not re.search(r"bb_button_chip\([^\n]*Utils\.COLOR_ERROR,", region)

    def test_the_old_values_are_gone(self):
        for name, old in (("diplomatic_ledger.gd", '"cd5c5c"'), ("enemy_phase_dialog.gd", '"cd5c5c"'),
                          ("war_detail_popup.gd", '"#a44"'), ("war_detail_popup.gd", "0.5, 0.6, 0.8, 0.6"),
                          ("war_detail_popup.gd", "0.8, 0.5, 0.5, 0.6"),
                          ("battle_diorama.gd", "Color(Utils.UI_GOLD, 0.55)"),
                          ("battle_diorama.gd", "Color(0.72, 0.20, 0.18, 1.0)")):
            assert old not in GS.code_lines(GS.read(SCRIPTS / name)), (name, old)

    def test_the_enemy_phase_title_takes_the_dialogs_lighter_red(self):
        scene = GS.read(SCENES / "enemy_phase_dialog.tscn")
        title = GS.node_block(scene, "TitleLabel")
        assert "theme_override_colors/font_color = Color(0.82, 0.41, 0.41, 1)" in title
        assert CR.ratio((0.82, 0.41, 0.41), CR._hex("1a1a2e")) >= CR.BODY_FLOOR


# ═══ Part 3 — R5 / R6, the controls that answer nothing ═══════════════════════
# (UXR3-12 … 14, 23, 37, 38, 43, 63, 67, 68, and R6's SILENT halves)
#
# Decided (honest availability): a control that cannot act in the current
# state is DISABLED, with its reason as a tooltip. The readers' inert-looking
# controls are drawn as what they are, or stop looking like links.

def _code(rel: str) -> str:
    return GS.code_lines(GS.read(PROJECT / rel))


class TestTheOpenBooksTabIsSelectedAndDisabled:
    def test_the_shared_rule(self):
        body = _func(_src("scripts/utils.gd"), "mark_active_tab")
        assert "tab.disabled = active" in body
        assert 'const ACTIVE_TAB_TIP := "You are reading this book"' in _src("scripts/utils.gd")
        assert "tab.tooltip_text = ACTIVE_TAB_TIP" in body
        # it keeps the selected look, never the greyed disabled one
        assert 'tab.add_theme_stylebox_override("disabled", active_style)' in body
        assert 'tab.add_theme_color_override("font_disabled_color", tab.get_theme_color("font_color"))' in body

    @pytest.mark.parametrize("script", ["strategic_ledger.gd", "diplomatic_ledger.gd"])
    def test_both_ledgers_mark_it(self, script):
        body = _func(_src(f"scripts/{script}"), "_update_tab_highlights")
        assert "Utils.mark_active_tab(tab_buttons[i], i == current_tab, _active_tab_style)" in body


class TestTheWarRoomsControlsSayWhenTheyCannotAct:
    def test_execute_waits_for_an_order(self):
        main = _code("scripts/main.gd")
        assert "command_input.draw.connect(_refresh_send_button)" in main
        assert 'const EXECUTE_EMPTY_TIP := "Type an order first"' in main
        assert "send_button.disabled = not enabled" not in main
        enable = _func(_src("scripts/main.gd"), "set_input_enabled")
        assert "_input_open = enabled" in enable and "_refresh_send_button()" in enable
        refresh = _func(_src("scripts/main.gd"), "_refresh_send_button")
        assert "Utils.set_available(send_button, _input_open and not empty" in refresh

    def test_the_map_reports_its_view(self):
        rend = _code("scenes/map_renderer_base.gd")
        assert "signal view_changed" in rend
        for name in ("_set_camera_zoom_level", "_set_camera_position", "_update_zoom_floor"):
            assert "view_changed.emit()" in _func(_src("scenes/map_renderer_base.gd"), name), name
        assert "func is_at_min_zoom() -> bool:" in rend and "func is_fit_view() -> bool:" in rend

    def test_zoom_out_and_fit_follow_the_view(self):
        main = _src("scripts/main.gd")
        assert "map_area.view_changed.connect(_refresh_map_controls)" in main
        body = _func(main, "_refresh_map_controls")
        assert "not map_area.is_at_min_zoom()" in body and "ZOOM_OUT_FLOOR_TIP" in body
        assert "not map_area.is_fit_view()" in body and "FIT_EUROPE_DONE_TIP" in body

    def test_the_helper_writes_only_on_change(self):
        body = _func(_src("scripts/utils.gd"), "set_available")
        assert "if button.disabled == available:" in body
        assert "if button.tooltip_text != tip:" in body


class TestSettingsAndTheTitleScreen:
    def test_connect_needs_a_key_and_disconnect_a_connection(self):
        src = _src("scripts/settings_panel.gd")
        body = _func(src, "_refresh_key_buttons")
        assert 'Utils.set_available(_connect_btn, _key_edit.text.strip_edges() != ""' in body
        assert 'Utils.set_available(_disconnect_btn, UiSettings.get_api_key() != ""' in body
        assert "_refresh_key_buttons()" in _func(src, "_show_stored_parser_state")
        for name in ("_on_apply_key", "_on_clear_key"):
            assert "_refresh_key_buttons()" in _func(src, name), name
        assert "_key_edit.text_changed.connect(func(_t): _refresh_key_buttons())" in src

    def test_the_menus_settings_answers_while_open(self):
        src = _src("scripts/main_menu.gd")
        assert '_add_menu_button("settings", "Settings", _toggle_settings, false)' in src
        body = _func(src, "_toggle_settings")
        assert "_close_settings()" in body and "_open_settings()" in body

    def test_a_waiting_campaign_button_says_why(self):
        src = _src("scripts/main_menu.gd")
        assert "const WAITING_TIP := \"Waiting for the game's server…\"" in src
        body = _func(src, "_apply_backend_state")
        assert body.count("WAITING_TIP") >= 3 and "NO_SAVES_TIP" in body


class TestTheInertLookingControls:
    def test_the_war_huds_header_and_rows_are_drawn_as_controls(self):
        src = _src("scripts/war_status_panel.gd")
        chrome = _func(src, "_give_row_chrome")
        assert "btn.flat = false" in chrome
        assert "btn.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND" in chrome
        for name in ('"normal"', '"hover"', '"pressed"'):
            assert f"btn.add_theme_stylebox_override({name}" in chrome, name
        assert "_give_row_chrome(btn)" in _func(src, "_add_coalition_header")
        assert "_give_row_chrome(row_btn)" in _func(src, "_add_war_entry")

    def test_the_coalition_leader_is_marked_in_words_not_an_underline(self):
        body = _func(_src("scripts/war_detail_popup.gd"), "_render_coalition_detail")
        assert "[u]" not in body and "— leads the coalition" in body

    def test_the_settlement_tables_links_live_in_the_labels_text(self):
        """Its names and '+ Add demand' were always [url] links; append_text
        left the labels' `text` empty, so the probe read them as absent."""
        code = _code("scripts/proposal_confirm_popup.gd")
        for label in ("content_label", "per_court_table", "footer_label"):
            assert f"{label}.append_text(" not in code, label
        assert "per_court_table.text = Utils.humanize_nation_keys_in_text(" in code

    def test_todays_orders_are_chips_that_type_the_order(self):
        src = _src("scripts/dispatch_view.gd")
        assert 'Utils.bb_button_chip("type:" + str(order), str(order)' in src
        body = _func(src, "_on_meta_clicked")
        assert "order_typed.emit(m.substr(5))" in body and "close_view()" in body
        main = _src("scripts/main.gd")
        assert "dispatch_view.order_typed.connect(_on_tutorial_suggest_command)" in main
        fill = _func(main, "_on_tutorial_suggest_command")
        assert "command_input.text = cmd" in fill and "send_command" not in fill   # never sends

    def test_a_mailbox_row_is_a_press(self):
        body = _func(_src("scripts/mailbox_panel.gd"), "_build_item_row")
        assert "panel.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND" in body
        assert 'open_label.text = "Open ▸"' in body
