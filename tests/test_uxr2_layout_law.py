"""UXR-2 part 3 — the layout law's census (Pre-Deploy S9 Slice C, October 12, 2026).

"Only some boxes are adjustable." The law (`docs/UX_UI_REVIEW_PLAN.md` §UXR-2):

    A surface is either ANCHORED (its rect a fraction of the viewport, with
    min and max in logical px) or CLAMPED-AND-GRIPPED (a fixed authored rect
    that `clamp_centered_panel` shrinks and a grip lets the player resize, the
    size remembered in `ui_settings.cfg`). No surface is a bare fixed rect.

This census walks EVERY CanvasLayer scene (not only the 101–122 modal band:
the HUD lives at 25, 26, 30, 75 and 90) and every CanvasLayer built in code,
and puts each top-level Control in exactly one class:

* ANCHORED-FULL — a full-rect overlay;
* CLAMPED — a centre-anchored panel whose script calls
  `Utils.clamp_centered_panel($<it>)` and whose scene is registered in
  `main.gd` (so the one live-refit road, `main._on_root_resized` →
  `DialogManager.refit_visible` / `top_bar.refit_active_screen`, reaches it);
* CLAMPED+GRIPPED — CLAMPED, plus `ResizeGrip.attach_centered($<it>, "<key>")`
  in its `_ready` with a key `UiSettings.PANEL_LIMITS` knows (every layer-50
  screen);
* FITTED — an edge-anchored or stretched rect fitted by a named function that
  the viewport's `size_changed` (or a `refit()` the road calls) reaches;
* CHROME — a small fixed rect (≤ 296×152, inside the clamp floor's own
  viewport) outside the modal band;
* ALLOWLISTED — named, with the slice that removes it; the list may only fall.

A centred decoration beside a clamped panel is forbidden (it stays where the
authored rect was when the clamp or a grip moves the panel — the Generals
screen's filigree did), and a stale `anchors_preset` fails.
"""
from __future__ import annotations

import re

import pytest

from tests import _godot_scenes as G

# The 16 presets: anchors (left, top, right, bottom).
PRESETS = {
    0: (0, 0, 0, 0), 1: (1, 0, 1, 0), 2: (0, 1, 0, 1), 3: (1, 1, 1, 1),
    4: (0, .5, 0, .5), 5: (.5, 0, .5, 0), 6: (1, .5, 1, .5), 7: (.5, 1, .5, 1),
    8: (.5, .5, .5, .5), 9: (0, 0, 0, 1), 10: (0, 0, 1, 0), 11: (1, 0, 1, 1),
    12: (0, 1, 1, 1), 13: (.5, 0, .5, 1), 14: (0, .5, 1, .5), 15: (0, 0, 1, 1),
}
MODAL_BAND = 101
CHROME_MAX = (296.0, 152.0)
# (scene, node) → (fitter, reach, evidence). `reach` is "size_changed" (the
# script connects the viewport's size_changed to a handler that is or calls
# the fitter) or "refit" (a `func refit()` that calls it — the road's hook).
FITTERS = {
    ("region_panel", "PanelContainer"): ("_fit_width", "size_changed", "Utils.fraction_px("),
    ("war_status_panel", "PanelContainer"): ("_fit_panel_to_content", "size_changed", "Utils.fraction_px("),
    ("top_bar", "BarContainer"): ("_fit_bar", "size_changed", "COMPACT_BELOW_PX"),
    ("top_bar", "NotificationArea"): ("_fit_rail", "size_changed", "Utils.fraction_px("),
    ("tutorial_overlay", "Card"): ("_fit_card_width", "size_changed", "CARD_WIDTH_FRACTION"),
    ("war_detail_popup", "PanelContainer"): ("refit", "refit", "Utils.clamp_anchored_panel("),
}
# Fixed rects still owed a fit, each with the slice that removes it. RATCHET:
# its length may only fall, and it is empty when UXR-2 lands.
ALLOWLIST: dict = {}   # emptied by UXR-2 Slice D (the anchors)
ALLOWLIST_RATCHET = 0
# CanvasLayers / centred panels built in code, each with its proof.
CODE_BUILT = {
    ("main.gd", "CanvasLayer.new()"): "Utils.clamp_centered_panel(_scale_card)",
    ("scale_card.gd", "set_anchors_preset(Control.PRESET_CENTER)"): "Utils.clamp_centered_panel(self)",
    ("main_menu.gd", "set_anchors_preset(Control.PRESET_CENTER)"): "_refit_open_panels",
    ("battle_diorama.gd", "set_anchors_preset(Control.PRESET_CENTER)"): "func refit()",
}


def _num(props: dict, key: str, default: float) -> float:
    v = props.get(key)
    return float(v) if v is not None else default


def rect_of(node) -> dict:
    p = node.props
    anchors = tuple(_num(p, f"anchor_{s}", 0.0) for s in ("left", "top", "right", "bottom"))
    offsets = tuple(_num(p, f"offset_{s}", 0.0) for s in ("left", "top", "right", "bottom"))
    preset = int(p["anchors_preset"]) if "anchors_preset" in p else None
    return {"anchors": anchors, "offsets": offsets, "preset": preset,
            "extent": (offsets[2] - offsets[0], offsets[3] - offsets[1])}


def _is_chrome(node, r: dict) -> bool:
    """A small FIXED rect: a point on both axes (a stretched axis is a
    viewport fraction, not chrome), a positive extent within CHROME_MAX, and no
    content minimum that could grow it past that (offsets read 0 x 0 on a
    container sized by `custom_minimum_size` alone)."""
    a = r["anchors"]
    if a[0] != a[2] or a[1] != a[3]:
        return False
    w, h = r["extent"]
    if not (0 < w <= CHROME_MAX[0] and 0 < h <= CHROME_MAX[1]):
        return False
    m = re.search(r"Vector2\(([-\d.]+),\s*([-\d.]+)\)", node.props.get("custom_minimum_size", ""))
    return not m or (float(m.group(1)) <= CHROME_MAX[0] and float(m.group(2)) <= CHROME_MAX[1])


def canvas_scenes(scenes: dict) -> dict:
    out = {}
    for name, text in scenes.items():
        nodes = G.parse_tscn(text)
        if nodes and nodes[0].type == "CanvasLayer":
            out[name] = nodes
    return out


def classify(stem: str, nodes: list, script: str, main_src: str, panel_keys: set,
             fitters: dict | None = None) -> list:
    """[(node, class, violation-or-'')] for every top-level Control of one scene.
    The script is read as CODE (comments and docstrings dropped), so a
    commented-out clamp, grip or fitter call proves nothing."""
    fitters = FITTERS if fitters is None else fitters
    script = G.code_lines(script)
    root = nodes[0]
    layer = int(root.props.get("layer", "1"))
    tops = [n for n in nodes if n.parent == "." and n.type not in ("", "Node", "Node2D", "Timer")]
    registered = f'"res://scenes/{stem}.tscn"' in G.code_lines(main_src)
    out = []
    clamped_here = False
    for n in tops:
        r = rect_of(n)
        a = r["anchors"]
        if r["preset"] is not None and r["preset"] in PRESETS and PRESETS[r["preset"]] != a:
            out.append((n, "?", "STALE_PRESET"))
            continue
        if a == (0, 0, 1, 1):
            out.append((n, "ANCHORED-FULL", ""))
            continue
        if a == (.5, .5, .5, .5) and f"Utils.clamp_centered_panel(${n.name})" in script:
            clamped_here = True
            if not registered:
                out.append((n, "CLAMPED", "UNREACHED_BY_THE_REFIT_ROAD"))
                continue
            grip = re.search(r'ResizeGrip\.attach_centered\(\$%s, "(\w+)"\)' % re.escape(n.name),
                             G.func_body(script, "_ready") if "func _ready(" in script else "")
            if layer == 50:
                if not grip:
                    out.append((n, "CLAMPED", "UNGRIPPED_SCREEN"))
                elif grip.group(1) not in panel_keys:
                    out.append((n, "CLAMPED+GRIPPED", "UNKNOWN_PANEL_KEY"))
                else:
                    out.append((n, "CLAMPED+GRIPPED", ""))
            else:
                out.append((n, "CLAMPED", ""))
            continue
        if a == (.5, .5, .5, .5):
            out.append((n, "?", "CLAMP_MISSING"))
            continue
        key = (stem, n.name)
        if key in fitters:
            fitter, reach, evidence = fitters[key]
            ok = f"func {fitter}(" in script and evidence in script
            if reach == "size_changed":
                handlers = re.findall(r"size_changed\.connect\((\w+)", script)
                ok = ok and any(h == fitter or f"{fitter}(" in G.func_body(script, h)
                                or f"{fitter}.call_deferred(" in G.func_body(script, h)
                                for h in handlers if f"func {h}(" in script)
            else:
                ok = ok and "func refit(" in script and fitter in G.func_body(script, "refit")
            out.append((n, "FITTED", "" if ok else "FITTER_UNREACHED"))
            continue
        if key in ALLOWLIST:
            out.append((n, "ALLOWLISTED", "MODAL_NOT_FITTED" if layer >= MODAL_BAND else ""))
            continue
        if _is_chrome(n, r):
            out.append((n, "CHROME", "MODAL_NOT_FITTED" if layer >= MODAL_BAND else ""))
            continue
        out.append((n, "?", "UNCOVERED_RECT"))
    if clamped_here:
        for i, (n, cls, v) in enumerate(out):
            if cls not in ("CLAMPED", "CLAMPED+GRIPPED", "ANCHORED-FULL") and not v:
                out[i] = (n, cls, "SIBLING_DECORATION")
    return out


@pytest.fixture(scope="module")
def tree():
    scenes = {p.stem: G.read(p) for p in G.client_scenes()}
    scripts = {p.stem: G.read(p) for p in G.client_scripts()}
    main_src = scripts["main"]
    limits = re.search(r"const PANEL_LIMITS := \{(.*?)\n\}", G.read(G.SCRIPTS_DIR / "ui_settings.gd"), re.S)
    keys = set(re.findall(r'"(\w+)":', limits.group(1))) if limits else set()
    return scenes, scripts, main_src, keys


class TestTheLaw:
    def test_every_surface_is_anchored_or_clamped(self, tree):
        scenes, scripts, main_src, keys = tree
        violations = []
        for stem, nodes in canvas_scenes(scenes).items():
            for n, cls, v in classify(stem, nodes, scripts.get(stem, ""), main_src, keys):
                if v:
                    violations.append((stem, n.name, cls, v))
        assert violations == []

    def test_every_layer_50_screen_is_gripped(self, tree):
        scenes, scripts, main_src, keys = tree
        gripped = {}
        for stem, nodes in canvas_scenes(scenes).items():
            if int(nodes[0].props.get("layer", "1")) != 50:
                continue
            for n, cls, _v in classify(stem, nodes, scripts.get(stem, ""), main_src, keys):
                if n.name == "PanelContainer":
                    gripped[stem] = cls
        assert gripped == {s: "CLAMPED+GRIPPED" for s in (
            "campaign_log", "diplomatic_ledger", "dispatch_view", "gazette_view",
            "marshal_management", "strategic_ledger")}, gripped

    def test_the_grip_keys_are_distinct(self, tree):
        _scenes, scripts, _main, keys = tree
        found = [m.group(1) for s in scripts.values()
                 for m in re.finditer(r'ResizeGrip\.attach_centered\(\$\w+, "(\w+)"\)', G.code_lines(s))]
        assert len(found) == len(set(found)) == 6, found
        assert set(found) <= keys

    def test_the_clamped_set_is_the_derived_set(self, tree):
        scenes, scripts, main_src, keys = tree
        clamped = set()
        for stem, nodes in canvas_scenes(scenes).items():
            for n, cls, _v in classify(stem, nodes, scripts.get(stem, ""), main_src, keys):
                if cls in ("CLAMPED", "CLAMPED+GRIPPED") and n.name == "PanelContainer":
                    clamped.add(stem)
        assert clamped == set(G.centre_anchored_surfaces())

    def test_the_parser_sees_every_node(self, tree):
        scenes, _scripts, _main, _keys = tree
        for stem, text in scenes.items():
            assert len(G.parse_tscn(text)) == len(re.findall(r"(?m)^\[node ", text)), stem

    def test_the_allowlist_only_falls(self, tree):
        assert len(ALLOWLIST) <= ALLOWLIST_RATCHET
        scenes, scripts, main_src, keys = tree
        live = {(stem, n.name) for stem, nodes in canvas_scenes(scenes).items()
                for n, cls, _v in classify(stem, nodes, scripts.get(stem, ""), main_src, keys)
                if cls == "ALLOWLISTED"}
        assert live == set(ALLOWLIST), "a stale or missing allowlist entry"

    def test_code_built_surfaces_carry_their_proof(self, tree):
        _scenes, scripts, _main, _keys = tree
        hits = set()
        for stem, src in scripts.items():
            code = G.code_lines(src)
            for needle in ("CanvasLayer.new()", "set_anchors_preset(Control.PRESET_CENTER)"):
                if needle in code:
                    hits.add((f"{stem}.gd", needle))
        assert hits == set(CODE_BUILT), hits
        for (script, _needle), proof in CODE_BUILT.items():
            assert proof in scripts[script[:-3]], (script, proof)


class TestTheRefitRoad:
    def test_one_road_refits_every_open_surface(self, tree):
        _s, scripts, _m, _k = tree
        body = G.func_body(scripts["main"], "_on_root_resized")
        assert "dialog_manager.refit_visible()" in body
        assert "top_bar.refit_active_screen()" in body
        assert "Utils.clamp_centered_panel(_scale_card)" in body
        assert "Utils.refit_surface(" in G.func_body(scripts["dialog_manager"], "refit_visible")
        assert "Utils.refit_surface(" in G.func_body(scripts["top_bar"], "refit_active_screen")

    def test_a_bespoke_fit_is_honoured_before_the_generic_clamp(self, tree):
        _s, scripts, _m, _k = tree
        body = G.func_body(scripts["utils"], "refit_surface")
        assert body.index('has_method("refit")') < body.index("clamp_centered_panel(")
        for stem, call in (("battle_diorama", "_fit_tray_to_viewport()"),
                           ("interrupt_popup", '_fit_to_content'),
                           ("marshal_petition_dialog", "_fit_body()"),
                           ("diplomacy_wizard", "Utils.clamp_centered_panel($PanelContainer)")):
            assert call in G.func_body(scripts[stem], "refit"), stem

    def test_the_menu_refits_its_open_panels(self, tree):
        _s, scripts, _m, _k = tree
        src = scripts["main_menu"]
        assert "resized.connect(_refit_open_panels)" in src
        assert "_refit_open_panels()" in G.func_body(src, "_on_ui_scale_changed")


class TestTheGripMechanics:
    def test_the_clamp_reads_the_players_size_between_the_authored_rect_and_the_override(self, tree):
        _s, scripts, _m, _k = tree
        body = G.func_body(scripts["utils"], "clamp_centered_panel")
        a = body.index('has_meta("design_size")')
        b = body.index('has_meta("clamp_user_size")')
        c = body.index('has_meta("clamp_ceiling_override")')
        assert a < b < c
        assert 'design = panel.get_meta("clamp_user_size")' in body

    def test_the_store(self, tree):
        _s, scripts, _m, keys = tree
        assert keys == {"terminal", "war_status", "ledger", "diplomatic_ledger", "generals",
                        "dispatch", "event_log", "gazette"}
        ui = scripts["ui_settings"]
        assert "clear_all_panel_sizes()" in G.func_body(ui, "reset_layout")
        assert 'set_panel_size("terminal", Vector2(width, height))' in G.func_body(ui, "set_terminal_size")

    def test_a_click_is_not_a_resize(self, tree):
        _s, scripts, _m, _k = tree
        grip = G.func_body(scripts["resize_grip"], "_finish_drag")
        assert grip.index("if not _moved:") < grip.index("UiSettings.set_panel_size(")
        term = G.func_body(scripts["main"], "_on_grip_gui_input")
        assert term.index("if _grip_moved:") < term.index("UiSettings.set_terminal_size(")

    def test_the_grip_is_the_panels_last_sibling(self, tree):
        _s, scripts, _m, _k = tree
        assert "get_parent().add_child" in G.func_body(scripts["resize_grip"], "_bind")

    def test_a_stored_size_is_loaded_on_attach_and_on_every_open(self, tree):
        """The REMEMBER half: a new session's screen opens at the stored size."""
        _s, scripts, _m, _k = tree
        grip = scripts["resize_grip"]
        assert "load_stored_size()" in G.code_lines(G.func_body(grip, "attach_centered"))
        assert "load_stored_size()" in G.code_lines(G.func_body(grip, "_on_host_visibility_changed"))
        assert "UiSettings.get_panel_size(store_name" in G.func_body(grip, "load_stored_size")

    def test_the_command_window_grip_has_the_click_threshold(self, tree):
        _s, scripts, _m, _k = tree
        body = G.func_body(scripts["main"], "_on_grip_gui_input")
        assert "ResizeGrip.MOVE_THRESHOLD" in body and "_grip_grab_offset" in body

    def test_reset_layout_reaches_every_grip(self, tree):
        _s, scripts, _m, _k = tree
        assert 'call_group(ResizeGrip.GROUP, "reset_to_authored")' in G.func_body(
            scripts["main"], "_on_layout_reset")


class TestTheAnchors:
    """Slice D: the HUD family is ANCHORED, and the top bar's 36 px is one
    number every HUD surface derives from."""

    def test_the_top_bar_height_is_one_number(self, tree):
        scenes, scripts, _m, _k = tree
        def const(stem, name):
            m = re.search(r"(?m)^const %s := ([\d.]+)" % name, scripts[stem])
            assert m, (stem, name)
            return float(m.group(1))
        bar = G.node_block(scenes["top_bar"], "BarContainer")
        height = float(re.search(r"offset_bottom = ([\d.]+)", bar).group(1))
        assert const("utils", "TOP_BAR_HEIGHT") == height == const("main", "TOP_BAR_RESERVED_PX")
        hud = const("utils", "HUD_MARGIN")
        assert const("region_panel", "_PANEL_TOP") == height + 12.0
        assert "offset_top = 48.0" in G.node_block(scenes["region_panel"], "PanelContainer")
        assert const("tutorial_overlay", "CARD_TOP") == height + hud
        slot = G.node_block(scenes["top_bar"], "NotificationArea")
        assert f"offset_top = {height + const('top_bar', 'RAIL_GAP'):.1f}" in slot
        assert "view.y - 88.0" in G.func_body(scripts["utils"], "clamp_centered_panel")
        assert 88.0 == 2.0 * (height + hud)

    def test_the_war_hud_is_gripped_and_the_hidden_band_is_gone(self, tree):
        _s, scripts, _m, _k = tree
        ws = G.code_lines(scripts["war_status_panel"])
        assert "func _input(" not in ws and "DRAG_MARGIN" not in ws
        assert ('ResizeGrip.attach_edge(panel_container, "war_status", '
                "ResizeGrip.Corner.TOP_LEFT)") in G.func_body(ws, "_ready")
        assert "UiSettings.get_panel_size(\"war_status\"" in G.func_body(ws, "_apply_geometry")

    def test_the_war_detail_popup_refits_on_every_show(self, tree):
        _s, scripts, _m, _k = tree
        wd = G.code_lines(scripts["war_detail_popup"])
        for show in ("show_war", "show_coalition", "show_armistice"):
            body = G.func_body(wd, show)
            assert body.index("\tshow()") < body.index("\trefit()"), show
        assert "Utils.clamp_anchored_panel(panel)" in G.func_body(wd, "refit")

    def test_the_hud_is_wired_to_what_it_avoids(self, tree):
        _s, scripts, _m, _k = tree
        main = G.code_lines(scripts["main"])
        assert "war_detail_popup.dock_beside = war_status_panel.panel_container" in main
        assert "tutorial_overlay.avoid_rail = notification_bar.rail_panel" in main
        tutor = G.func_body(scripts["tutorial_overlay"], "_card_placement")
        assert "avoid_rail.get_global_rect()" in tutor


class TestTheCensusCanFail:
    """Each violation code from a synthetic scene (the PS18-R7 lesson)."""

    @staticmethod
    def _scene(layer, child):
        return ('[gd_scene format=3]\n\n[node name="S" type="CanvasLayer"]\n'
                f"layer = {layer}\n\n{child}")

    def _codes(self, layer, child, script="", main='"res://scenes/x.tscn"'):
        nodes = G.parse_tscn(self._scene(layer, child))
        return {v for _n, _c, v in classify("x", nodes, script, main, {"ledger"}) if v}

    CENTRE = ('[node name="PanelContainer" type="PanelContainer" parent="."]\n'
              "anchors_preset = 8\nanchor_left = 0.5\nanchor_top = 0.5\n"
              "anchor_right = 0.5\nanchor_bottom = 0.5\noffset_left = -300.0\n"
              "offset_top = -200.0\noffset_right = 300.0\noffset_bottom = 200.0\n")

    def test_a_centred_panel_without_a_clamp(self):
        assert self._codes(105, self.CENTRE) == {"CLAMP_MISSING"}

    def test_an_ungripped_screen(self):
        assert self._codes(50, self.CENTRE, "func _ready():\n\tpass\nfunc open():\n"
                           "\tUtils.clamp_centered_panel($PanelContainer)\n") == {"UNGRIPPED_SCREEN"}

    def test_an_unregistered_surface(self):
        assert self._codes(105, self.CENTRE, "Utils.clamp_centered_panel($PanelContainer)",
                           main="") == {"UNREACHED_BY_THE_REFIT_ROAD"}

    def test_a_bare_edge_rect(self):
        child = ('[node name="Box" type="PanelContainer" parent="."]\nanchors_preset = 1\n'
                 "anchor_left = 1.0\nanchor_right = 1.0\noffset_left = -400.0\noffset_bottom = 300.0\n")
        assert self._codes(26, child) == {"UNCOVERED_RECT"}

    def test_chrome_in_the_modal_band(self):
        child = ('[node name="Tag" type="Label" parent="."]\noffset_right = 100.0\n'
                 "offset_bottom = 20.0\n")
        assert self._codes(105, child) == {"MODAL_NOT_FITTED"}

    def test_a_centred_decoration_beside_a_clamped_panel(self):
        """The Generals filigree's own shape: a centred rect no clamp reaches."""
        deco = ('[node name="Filigree" type="TextureRect" parent="."]\nanchors_preset = 8\n'
                "anchor_left = 0.5\nanchor_top = 0.5\nanchor_right = 0.5\nanchor_bottom = 0.5\n"
                "offset_left = -417.0\noffset_top = 283.0\noffset_right = -390.0\noffset_bottom = 310.0\n")
        codes = self._codes(105, self.CENTRE + "\n" + deco, "Utils.clamp_centered_panel($PanelContainer)")
        assert codes == {"CLAMP_MISSING"}

    def test_a_corner_decoration_beside_a_clamped_panel(self):
        """A small corner rect would pass as CHROME on its own; beside a clamped
        panel it is a decoration that stays put when the panel moves."""
        deco = ('[node name="Corner" type="TextureRect" parent="."]\noffset_right = 27.0\n'
                "offset_bottom = 27.0\n")
        alone = self._codes(30, deco)
        beside = self._codes(30, self.CENTRE + "\n" + deco, "Utils.clamp_centered_panel($PanelContainer)")
        assert alone == set() and beside == {"SIBLING_DECORATION"}

    def test_an_unknown_grip_key(self):
        script = ('func _ready():\n\tResizeGrip.attach_centered($PanelContainer, "nope")\n'
                  "func open():\n\tUtils.clamp_centered_panel($PanelContainer)\n")
        assert self._codes(50, self.CENTRE, script) == {"UNKNOWN_PANEL_KEY"}

    def test_a_commented_out_grip_is_no_grip(self):
        script = ('func _ready():\n\t# ResizeGrip.attach_centered($PanelContainer, "ledger")\n\tpass\n'
                  "func open():\n\tUtils.clamp_centered_panel($PanelContainer)\n")
        assert self._codes(50, self.CENTRE, script) == {"UNGRIPPED_SCREEN"}

    def test_an_unreached_fitter(self):
        child = ('[node name="Box" type="PanelContainer" parent="."]\nanchors_preset = 1\n'
                 "anchor_left = 1.0\nanchor_right = 1.0\noffset_left = -400.0\noffset_bottom = 300.0\n")
        fitters = {("x", "Box"): ("_fit_box", "size_changed", "EVIDENCE")}
        script = "const EVIDENCE := 1\nfunc _ready():\n\tpass\nfunc _fit_box():\n\tpass\n"
        nodes = G.parse_tscn(self._scene(26, child))
        codes = {v for _n, _c, v in classify("x", nodes, script, '"res://scenes/x.tscn"',
                                              {"ledger"}, fitters) if v}
        assert codes == {"FITTER_UNREACHED"}
        reached = script + "func _ready2():\n\tget_viewport().size_changed.connect(_fit_box)\n"
        codes = {v for _n, _c, v in classify("x", nodes, reached, '"res://scenes/x.tscn"',
                                              {"ledger"}, fitters) if v}
        assert codes == set()

    def test_a_stretched_or_min_sized_rect_is_not_chrome(self):
        wide = ('[node name="Strip" type="PanelContainer" parent="."]\nanchors_preset = 12\n'
                "anchor_top = 1.0\nanchor_right = 1.0\nanchor_bottom = 1.0\noffset_top = -150.0\n")
        big = ('[node name="Big" type="PanelContainer" parent="."]\n'
               "custom_minimum_size = Vector2(900, 700)\n")
        assert self._codes(26, wide) == {"UNCOVERED_RECT"}
        assert self._codes(26, big) == {"UNCOVERED_RECT"}

    def test_a_grouped_node_is_parsed(self):
        """Godot writes `groups=[...]` inside the header; the parser must keep
        the node (the review's P2: it had folded it into the node before)."""
        child = ('[node name="BackgroundOverlay" type="ColorRect" parent="."]\nanchors_preset = 15\n'
                 "anchor_right = 1.0\nanchor_bottom = 1.0\n\n"
                 '[node name="Big" type="PanelContainer" parent="." groups=["hud"]]\n'
                 "offset_right = 900.0\noffset_bottom = 700.0\n")
        assert self._codes(105, child) == {"UNCOVERED_RECT"}

    def test_a_stale_preset(self):
        child = ('[node name="P" type="PanelContainer" parent="."]\nanchors_preset = 8\n'
                 "anchor_left = 1.0\nanchor_top = 0.5\nanchor_right = 0.5\nanchor_bottom = 0.5\n")
        assert self._codes(105, child) == {"STALE_PRESET"}
