"""Pre-Deploy S15's head — the peace report's two layout rows (October 25, 2026).

  PC-F46  The armistice letter's cost sat below the fold, under Accept: the
          envoy popup was 680 x 440 at 1920 x 1080 AND at 5120 x 1440 (3657 x
          1028 logical at 140 %), showing 355 characters of a 966-px letter;
          the war-detail popup's peace table began past its fold. Now the
          letter's box GROWS with the window (80 % of its height, 45 % of its
          width to a reading measure of 860), the Armistice Terms and the
          Political Consequences LEAD the War Summary, and the war popup (a
          wider, taller box) leads with its peace table.
  PC-F47  Hover text stood on Godot's default translucent tooltip panel and
          never wrapped: the counsel's 452-character refusal ran off a 1920
          window at "...the alliance with Bavar". Now `ui/main_theme.tres`
          styles an OPAQUE gold-hairlined TooltipPanel, and ONE hook
          (`Utils.wrap_tooltips`, installed by main_menu.gd and main.gd) gives
          the engine's tooltip label a measured, word-wrapped width.

The pins: the sources (regex), the committed frame record
(`docs/audits/peace_client/s15_layout_record.json`, the `_s15_` frames), and
the DRIVEN pins — the IQ-10 harness itself, headless in its record-only mode
(tests/test_sf_rr5_the_frames.py's idiom), on the report's own Vienna-held
board (capture group `pc_layout`: tests/fixtures/pc_boards/
turn6_vienna_held.json), at the physical sizes of the rows' completion lines.
A driven pin skips without the engine; a skip is not a pass.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
SCENES = PROJECT / "scenes"
TOOLS = REPO / "tools"
FRAMES = REPO / "docs" / "audits" / "peace_client"

SIZES = ("1920x1080", "5120x1440")
LETTER_NEEDLES = ["Armistice Terms", "When it expires", "At expiry", "The cure",
                  "Political Consequences", "War Summary"]
WAR_NEEDLES = ["Settlement Tier", "The peace table reads", "Court by court",
               "This turn's battles and captures"]


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    at = src.index(f"func {name}(")
    ends = [i for i in (src.find("\nfunc ", at + 10), src.find("\nstatic func ", at + 10)) if i != -1]
    return src[at:min(ends) if ends else len(src)]


def _record() -> dict:
    doc = json.loads(_read(FRAMES / "s15_layout_record.json"))
    return {(r["id"], r["resolution"], r["arm"].split(" ")[0]): r for r in doc["frames"]}


def _const(src: str, name: str) -> float:
    m = re.search(rf"^const {name} := ([0-9.]+)\s*$", src, re.M)
    assert m, f"const {name} missing"
    return float(m.group(1))


# ═══════════════════════════════════════════════════════════════════════════
# The driven record: the harness itself, headless, on the report's own board
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="module")
def drive(tmp_path_factory):
    from tests import _chip_census as C
    exe = C.engine()
    if exe is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    import importlib.util
    work = tmp_path_factory.mktemp("s15pc")
    payloads = work / "payloads"
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    cap = subprocess.run(
        [sys.executable, str(TOOLS / "iq10_capture_payloads.py"), "--out", str(payloads),
         "--only", "pc_layout"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=900, env=env, cwd=str(REPO), stdin=subprocess.DEVNULL)
    assert cap.returncode == 0, f"the capture failed:\n{cap.stdout[-2500:]}\n{cap.stderr[-1500:]}"
    spec_mod = importlib.util.spec_from_file_location("_s15_runner", TOOLS / "iq10_run_captures.py")
    runner = importlib.util.module_from_spec(spec_mod)
    spec_mod.loader.exec_module(runner)
    sys.path.insert(0, str(TOOLS))
    from uxr0_readability_report import derive_ui_scale
    wanted = ["pc_armistice_letter", "pc_war_detail", "pc_counsel_paths_tooltip", "pc_war_card_tooltip"]
    rows = []
    for row in [r for r in runner.SHOTS if r["id"] in wanted]:
        for (w, h) in ((1920, 1080), (5120, 1440)):
            r = dict(row)
            r["base_id"] = row["id"]
            r["id"] = f"{row['id']}__{w}x{h}"
            r["window"] = [w, h]
            r["scales"] = [derive_ui_scale(w, h)]
            r["resolution"] = [w, h]
            r["physical_scale"] = r["scales"][0]
            rows.append(r)
    # the 800 x 450 logical window (Interface Scale 2.0 on the default 1600 x 900):
    # the authored floor must still fit the clamp, the answers on screen.
    small = dict(next(r for r in runner.SHOTS if r["id"] == "pc_armistice_letter"))
    small["id"] = "pc_armistice_letter__small"
    small["scales"] = [2.0]
    rows.append(small)
    for sid in ("pc_counsel_paths_tooltip", "pc_war_card_tooltip"):
        tip = dict(next(r for r in runner.SHOTS if r["id"] == sid))
        tip["id"] = f"{sid}__small"
        tip["scales"] = [2.0]
        rows.append(tip)
    manifest = runner.load_manifest(payloads)
    spec_path, result_path = work / "spec.json", work / "result.json"
    spec, _ = runner.build_spec(rows, manifest, [1.0], "s15", spec_path, result_path, work / "png")
    spec["record_only"] = True
    spec_path.write_text(json.dumps(spec, indent=1), encoding="utf-8")
    env.update({"IQ10_SPEC": str(spec_path), "SOVEREIGN_PORT": runner.HARNESS_PORT})
    # NEVER --log-file (it crashes this engine build): script errors are read
    # off the run's own stdout / stderr.
    proc = subprocess.run(
        [exe, "--headless", "--audio-driver", "Dummy", "--path", str(PROJECT), "--script", runner.SCRIPT],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=900, env=env, cwd=str(REPO), stdin=subprocess.DEVNULL)
    if not result_path.is_file():
        pytest.fail(f"the harness wrote no result\nexit={proc.returncode}\n{proc.stderr[-2000:]}")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    frames = {row["id"]: row["frames"][0] for row in result.get("results", []) if row.get("frames")}
    errors = [ln for ln in (proc.stdout + proc.stderr).splitlines() if "SCRIPT ERROR" in ln]
    return {"frames": frames, "results": result.get("results", []), "errors": errors}


def _panel(frame: dict, scene: str) -> list:
    return next(v for k, v in frame["surfaces"].items() if k.startswith(scene) and k.endswith("/PanelContainer"))


def _seen(frame: dict, scene: str) -> str:
    return "\n".join(e.get("seen", "") for e in frame.get("seen_text") or []
                     if e["path"].startswith(scene) and e["path"].endswith("ContentLabel"))


def _inside(r, s, tol: float = 1.0) -> bool:
    return (r[0] >= s[0] - tol and r[1] >= s[1] - tol
            and r[0] + r[2] <= s[0] + s[2] + tol and r[1] + r[3] <= s[1] + s[3] + tol)


# ═══════════════════════════════════════════════════════════════════════════
# PC-F46 — the letter's cost above the fold, the war popup's table above its
# ═══════════════════════════════════════════════════════════════════════════


class TestPCF46:

    # ── the sources ─────────────────────────────────────────────────────────

    def test_the_letters_ceiling_grows_with_the_window(self):
        src = _read(SCRIPTS / "incoming_proposal_popup.gd")
        assert _const(src, "LETTER_HEIGHT_FRACTION") == 0.8
        assert _const(src, "LETTER_WIDTH_FRACTION") == 0.45
        assert _const(src, "LETTER_MAX_WIDTH") == 860.0
        # the authored rect (680 x 440, the .tscn's offsets) is the FLOOR
        assert _const(src, "LETTER_MIN_WIDTH") == 680.0 and _const(src, "LETTER_MIN_HEIGHT") == 440.0
        scene = _read(SCENES / "incoming_proposal_popup.tscn")
        assert "offset_left = -340.0" in scene and "offset_bottom = 220.0" in scene
        raise_ = _func(src, "_raise_letter_ceiling")
        assert 'set_meta("clamp_ceiling_override"' in raise_
        assert "get_viewport().get_visible_rect().size" in raise_
        assert "view.y * LETTER_HEIGHT_FRACTION" in raise_

    def test_the_ceiling_is_raised_before_every_clamp_on_open_and_on_refit(self):
        src = _read(SCRIPTS / "incoming_proposal_popup.gd")
        show = _func(src, "show_proposal")
        assert show.index("_raise_letter_ceiling()") < show.index("Utils.clamp_centered_panel($PanelContainer)")
        refit = _func(src, "refit")      # the live-refit road (Utils.refit_surface -> main._on_root_resized)
        assert refit.index("_raise_letter_ceiling()") < refit.index("Utils.clamp_centered_panel($PanelContainer)")

    def test_the_consequences_lead_the_war_summary(self):
        body = _func(_read(SCRIPTS / "incoming_proposal_popup.gd"), "_build_peace_preview_section")
        order = [body.index(x) for x in ('"Assessment:', "[b]Armistice Terms[/b]",
                                         "[b]Political Consequences[/b]", "[b]War Summary[/b]")]
        assert order == sorted(order), order
        # once each: the blocks MOVED, they were not copied
        assert body.count("[b]Armistice Terms[/b]") == 1 and body.count("[b]Political Consequences[/b]") == 1
        # and the lines the earlier rows pinned inside them are still there
        assert "printed_texts" in body and 'if printed_texts.has(str(item.get("text", ""))):' in body
        assert re.search(r"for item in consequence_items:\n(.*?)\n\n", body, re.S)

    def test_the_war_popup_takes_more_room_and_leads_with_its_peace_table(self):
        src = _read(SCRIPTS / "war_detail_popup.gd")
        assert _const(src, "WIDTH_FRACTION") == 0.24 and _const(src, "FIT_MAX_WIDTH") == 640.0
        assert _const(src, "HEIGHT_FRACTION") == 0.72 and _const(src, "FIT_MAX_HEIGHT") == 880.0
        body = _func(src, "_render_war_detail")
        order = [body.index(x) for x in ('"Settlement Tier: [color="', 'peace_table.get("lines", [])',
                                          "# Breakdown", "]Score Breakdown[/color]")]
        assert order == sorted(order), order
        assert body.count('"Settlement Tier: [color="') == 1      # moved, not copied
        assert 'Settlement Tier (theirs to impose): [color=" + COLOR_RED' in body   # IQ-2's arm intact

    # ── the frames, as committed ────────────────────────────────────────────

    @pytest.mark.parametrize("size", SIZES)
    def test_the_before_frames_reproduce_the_row(self, size):
        """The entry tree: a 680 x 440 letter at both sizes with none of the
        truce's cost in view; a war popup whose peace table is below its fold."""
        rec = _record()
        letter = rec[("pc_armistice_letter", size, "before")]
        assert letter["panel_rect"][2:] == [680, 440]
        assert not any(letter["seen_above_the_fold"][n] for n in LETTER_NEEDLES[:5])
        war = rec[("pc_war_detail", size, "before")]
        assert not war["seen_above_the_fold"]["The peace table reads"]
        assert not war["seen_above_the_fold"]["Court by court"]
        if size == "1920x1080":
            assert war["panel_rect"][2:] == [384, 594]

    @pytest.mark.parametrize("size", SIZES)
    def test_the_after_frames_show_the_cost_and_the_table_without_scrolling(self, size):
        rec = _record()
        letter = rec[("pc_armistice_letter", size, "after")]
        vw, vh = letter["logical_viewport"]
        x, y, w, h = letter["panel_rect"]
        assert h == int(vh * 0.8) and w == 860, letter["panel_rect"]
        assert y >= 44 and y + h <= vh - 12 and x >= 12 and x + w <= vw - 12
        assert all(letter["seen_above_the_fold"][n] for n in LETTER_NEEDLES), letter["seen_above_the_fold"]
        assert {b["text"] for b in letter["buttons"]} >= {"Accept", "Reject", "Not Now"}
        war = rec[("pc_war_detail", size, "after")]
        assert all(war["seen_above_the_fold"][n] for n in WAR_NEEDLES), war["seen_above_the_fold"]
        wvw, wvh = war["logical_viewport"]
        assert _inside(war["panel_rect"], [0, 44, wvw, wvh - 44])

    def test_the_frames_exist(self):
        for stem in ("m7_armistice_letter_s15", "m2_war_detail_s15",
                     "m7_armistice_letter_s15_before", "m2_war_detail_s15_before"):
            for size in SIZES:
                assert (FRAMES / f"{stem}_{size}.jpg").is_file(), (stem, size)

    # ── driven: the current code, headless, on the report's board ──────────

    def test_the_harness_ran_clean(self, drive):
        assert drive["errors"] == [], drive["errors"]
        bad = [(r["id"], r.get("errors")) for r in drive["results"] if not r.get("ok")]
        assert bad == [], bad

    @pytest.mark.parametrize("size", SIZES)
    def test_driven_the_letter_stands_at_eighty_percent_with_its_cost_in_view(self, drive, size):
        frame = drive["frames"][f"pc_armistice_letter__{size}"]
        vw, vh = frame["logical_viewport"]
        x, y, w, h = _panel(frame, "IncomingProposalPopup")
        assert int(h) == int(vh * 0.8) and int(w) == 860, (size, [x, y, w, h])
        assert y >= 44 - 0.5 and y + h <= vh - 12 + 0.5
        seen = _seen(frame, "IncomingProposalPopup")
        for needle in LETTER_NEEDLES:
            assert needle in seen, (size, needle)
        # the answers stand outside the scroll, inside the window
        view = [0.0, 0.0, vw, vh]
        names = {b["text"] for b in frame["buttons"] if b["text"]}
        assert {"Accept", "Reject", "Not Now"} <= names
        for b in frame["buttons"]:
            if b["text"] in ("Accept", "Reject", "Not Now"):
                assert _inside(b["rect_raw"], view), b

    def test_driven_the_authored_floor_still_fits_a_small_window(self, drive):
        """Interface Scale 2.0 on 1600 x 900 is an 800 x 450 logical window:
        the raised ceiling must leave the clamp where it was — under the bar,
        inside the window, every answer on screen."""
        frame = drive["frames"]["pc_armistice_letter__small"]
        vw, vh = frame["logical_viewport"]
        assert (vw, vh) == (800.0, 450.0)
        r = _panel(frame, "IncomingProposalPopup")
        assert r[1] >= 44 - 0.5 and r[1] + r[3] <= vh - 12 + 0.5 and r[0] >= 12 - 0.5 and r[0] + r[2] <= vw - 12 + 0.5
        for b in frame["buttons"]:
            if b["text"] in ("Accept", "Reject", "Not Now"):
                assert _inside(b["rect_raw"], [0.0, 0.0, vw, vh]), b

    @pytest.mark.parametrize("size", SIZES)
    def test_driven_the_war_popups_peace_table_is_above_its_fold(self, drive, size):
        frame = drive["frames"][f"pc_war_detail__{size}"]
        seen = _seen(frame, "WarDetailPopup")
        for needle in WAR_NEEDLES:
            assert needle in seen, (size, needle)
        assert seen.index("Settlement Tier") < seen.index("Score Breakdown")
        vw, vh = frame["logical_viewport"]
        assert _inside(_panel(frame, "WarDetailPopup"), [0, 44, vw, vh - 44])


# ═══════════════════════════════════════════════════════════════════════════
# PC-F47 — hover text on an opaque themed panel, wrapped to the window
# ═══════════════════════════════════════════════════════════════════════════


class TestPCF47:

    # ── the theme ───────────────────────────────────────────────────────────

    def test_the_theme_styles_an_opaque_tooltip_panel(self):
        theme = _read(PROJECT / "ui" / "main_theme.tres")
        assert 'TooltipPanel/styles/panel = SubResource("StyleBoxFlat_tooltip")' in theme
        block = re.search(r'\[sub_resource type="StyleBoxFlat" id="StyleBoxFlat_tooltip"\]\n(.*?)\n\n', theme, re.S)
        assert block, "the tooltip stylebox is missing"
        bg = re.search(r"bg_color = Color\(([0-9., ]+)\)", block.group(1)).group(1).split(",")
        assert float(bg[3]) == 1.0, "the hover panel must be OPAQUE"
        assert "border_width_left = 1" in block.group(1) and "border_color = Color(0.878, 0.753, 0.322, 1)" in block.group(1)
        assert "TooltipLabel/colors/font_color" in theme and "TooltipLabel/font_sizes/font_size = 16" in theme

    # ── the wrap hook ───────────────────────────────────────────────────────

    def test_one_hook_wraps_every_tooltip(self):
        src = _read(SCRIPTS / "utils.gd")
        assert _const(src, "TOOLTIP_WRAP_FRACTION") == 0.4
        assert _const(src, "TOOLTIP_WRAP_MIN") == 240.0 and _const(src, "TOOLTIP_WRAP_MAX") == 720.0
        install = _func(src, "wrap_tooltips")
        assert "tree.node_added.connect(_wrap_tooltip_popup)" in install
        assert 'has_meta("tooltip_wrap")' in install          # once per run
        popup = _func(src, "_wrap_tooltip_popup")
        # told by the engine's own theme variation, never by a node name
        assert "(node as PopupPanel).theme_type_variation != &\"TooltipPanel\"" in popup
        assert "fit_tooltip_label(child as Label, view)" in popup
        fit = _func(src, "fit_tooltip_label")
        # a tip taller than the window widens (to the window's width) before it overflows
        assert "while rows * (line_h + spacing) > view.y - 32.0 and wrap < widest - 1.0:" in fit
        assert "var widest := maxf(view.x - 24.0, wrap)" in fit
        assert "label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART" in fit
        assert "font.get_multiline_string_size(" in fit and "label.custom_minimum_size = Vector2(" in fit
        width = _func(src, "tooltip_wrap_width")
        assert "clampf(view_width * TOOLTIP_WRAP_FRACTION, TOOLTIP_WRAP_MIN, TOOLTIP_WRAP_MAX)" in width
        assert "view_width - 24.0" in width                   # never wider than the window

    def test_the_hook_is_installed_from_the_first_scene_and_from_main(self):
        assert "Utils.wrap_tooltips(get_tree())" in _func(_read(SCRIPTS / "main_menu.gd"), "_ready")
        assert "Utils.wrap_tooltips(get_tree())" in _func(_read(SCRIPTS / "main.gd"), "_ready")

    def test_the_hard_wraps_the_old_tooltips_needed_are_retired(self):
        """PC-X11 hard-wrapped two tooltips at 100 characters because a tooltip
        never wrapped itself; at a narrow window that re-wrapped raggedly."""
        for name in ("diplomacy_wizard.gd", "war_status_panel.gd"):
            assert "tooltip_text = Utils.wrap_text(" not in _read(SCRIPTS / name), name

    def test_the_harness_hovers_for_real_and_records_the_popup(self):
        gd = _read(TOOLS / "iq10_surface_screenshot.gd")
        assert 'elif step.has("hover"):' in gd
        hover = _func(gd, "_hover")
        assert "root.notification(Node.NOTIFICATION_VP_MOUSE_ENTER)" in hover and "root.push_input(ev, true)" in hover
        assert 'frame["tooltip"] = _tooltip_record()' in gd
        assert "root.gui_disable_input = true" in _func(gd, "_teardown")      # the rail goes back up
        runner = _read(TOOLS / "iq10_run_captures.py")
        for shot in ("pc_armistice_letter", "pc_war_detail", "pc_counsel_paths_tooltip", "pc_war_card_tooltip"):
            assert f'"id": "{shot}"' in runner
        assert '"pc_layout": cap_pc_layout' in _read(TOOLS / "iq10_capture_payloads.py")

    # ── the frames, as committed ────────────────────────────────────────────

    @pytest.mark.parametrize("size", SIZES)
    def test_the_after_frames_show_an_opaque_wrapped_tooltip_inside_the_window(self, size):
        rec = _record()
        for shot, min_lines in (("pc_counsel_paths_tooltip", 3), ("pc_war_card_tooltip", 12)):
            row = rec[(shot, size, "after")]
            t = row["tooltip"]
            assert t["bg_alpha"] == 1.0 and t["autowrap"] == 3 and t["inside_window"], (shot, t)
            assert t["lines"] >= min_lines, (shot, t)
            assert t["rect"][2] <= 720 + 40, (shot, t)          # wrapped to the cap, not one line
        # the 452-character refusal reads WHOLE: four lines at the cap
        assert rec[("pc_counsel_paths_tooltip", size, "after")]["tooltip"]["chars"] == 452

    def test_the_frames_exist(self):
        for stem in ("m5_counsel_paths_s15", "m1_war_card_tooltip_s15"):
            for size in SIZES:
                assert (FRAMES / f"{stem}_{size}.jpg").is_file(), (stem, size)

    # ── driven: the engine's own hover, headless ────────────────────────────

    @pytest.mark.parametrize("size", SIZES)
    @pytest.mark.parametrize("shot,min_lines,chars", [("pc_counsel_paths_tooltip", 3, 452),
                                                       ("pc_war_card_tooltip", 12, 1500)])
    def test_driven_the_hover_wraps_on_an_opaque_panel(self, drive, size, shot, min_lines, chars):
        frame = drive["frames"][f"{shot}__{size}"]
        t = frame["tooltip"]
        assert t, f"{shot}: the hover raised no popup"
        assert len(t["text"]) == chars or len(t["text"].replace("\n", " ")) >= chars - 5
        vw, vh = frame["logical_viewport"]
        assert t["autowrap"] == 3 and t["bg_alpha"] == 1.0
        assert t["lines"] >= min_lines, t["lines"]
        assert _inside(t["rect"], [0.0, 0.0, vw, vh]), (t["rect"], vw, vh)
        # a wrapped block: no wider than the cap plus the panel's margins
        assert t["rect"][2] <= 720 + 40

    def test_driven_a_small_window_keeps_the_hover_inside_it(self, drive):
        """Interface Scale 2.0 on 1600 x 900 (800 x 450 logical). The refusal
        wraps to a column and stands whole inside the window; the war card's
        25 lines, which at the 320-px column would stand a thousand px high,
        widen to the window's own width instead (they cannot stand inside 450 px
        at any width — the old unwrapped tooltip was 25 lines tall too)."""
        refusal = drive["frames"]["pc_counsel_paths_tooltip__small"]
        vw, vh = refusal["logical_viewport"]
        assert (vw, vh) == (800.0, 450.0)
        t = refusal["tooltip"]
        assert t and t["bg_alpha"] == 1.0 and t["lines"] >= 6
        assert _inside(t["rect"], [0.0, 0.0, vw, vh]), t["rect"]
        card = drive["frames"]["pc_war_card_tooltip__small"]["tooltip"]
        assert card["rect"][2] > 600, card["rect"]               # widened from the 320 column
        assert card["rect"][0] >= -0.5 and card["rect"][0] + card["rect"][2] <= vw + 0.5, card["rect"]
