"""UXR-2 part 5 — scroll where content is unbounded (Pre-Deploy S9 Slice B,
October 12, 2026).

The rule `Utils.clamp_centered_panel`'s own docstring states: a `fit_content`
RichTextLabel outside any ScrollContainer imposes its height through its
text, so no clamp can bound it. The class has shipped before — PS18-10 (the
settle-a-war window ran off the screen on a fit_content footer), PS18-14 (the
reward explainer), PS18-R4 (six modals clamped while keeping an unbounded
label; the "all inside ScrollContainers (verified)" claim was never pinned),
UXR-X3 (the tutor card at scale 3.0). This census pins it, three ways:

* the SCENE arm — every `fit_content = true` RichTextLabel in a .tscn has a
  ScrollContainer somewhere in its WHOLE ancestor chain (the PC15-18 wheel
  census reads only the direct parent);
* the SCRIPT arm — every `RichTextLabel.new()` given `fit_content = true` is
  added, through its parents, under a ScrollContainer;
* the TOGGLE arm — a label a script switches to `fit_content = true` sits in a
  function that also switches it back to a bounded scroll.

What may stand outside a scroll is a short, named list, each entry with the
proof the test checks: it bounds itself, it is count-capped, or it is
free-positioned (its parent is no Container, so it feeds no panel minimum).
"""
from __future__ import annotations

import re

import pytest

from tests import _godot_scenes as G

# (scene, node path) → why it may stand outside a scroll, checked below.
ALLOW_SCENE = {
    ("tutorial_overlay.tscn", "Card/VBox/BodyText"): "bounds itself",
}
# (script, variable) → why, checked below.
ALLOW_SCRIPT = {
    # ("battle_diorama.gd", "_verdict") left this list with UXR-X9 (Pre-Deploy
    # S12 part 2, part 5e): the verdict is a bounded room above the nameplate
    # that scrolls on whole lines, no longer fit_content (proof below).
    ("main.gd", "_suggestion_row"): "count-capped",
    ("notification_bar.gd", "body"): "bounds itself",
    # Pre-Deploy S12 (UXR3-62): two fixed lines over the proclamation's name —
    # the heading and the struck old name; the body below stays in its scroll.
    ("proclamation_popup.gd", "head_label"): "two fixed lines",
    # SF-RR5 (SFR-B11, October 21, 2026): the perspective line ("By your
    # hand.") — one fixed line under the body's scroll, above Acknowledge.
    ("proclamation_popup.gd", "subtitle_label"): "one fixed line",
}
# ScrollContainers that declare no height floor: a floorless list is squeezed
# to a strip by fixed chrome (the IGR-F letter-book shape). It may only fall.
FLOORLESS_SCROLL_RATCHET = 8

_NEW = re.compile(r"(?:var\s+)?(\w+)\s*:?=\s*RichTextLabel\.new\(\)")
_FUNC = re.compile(r"(?m)^(?:static )?func (\w+)\(")


def _functions(src: str) -> dict:
    heads = list(_FUNC.finditer(src))
    return {m.group(1): src[m.start():(heads[i + 1].start() if i + 1 < len(heads) else len(src))]
            for i, m in enumerate(heads)}


def scene_violations(name: str, text: str) -> list:
    """Every fit_content RichTextLabel in a scene with no ScrollContainer above it."""
    nodes = G.parse_tscn(text)
    out = []
    for node in nodes:
        if node.type != "RichTextLabel" or node.props.get("fit_content") != "true":
            continue
        if any(a.type == "ScrollContainer" for a in G.ancestors(nodes, node.path)):
            continue
        out.append((name, node.path))
    return out


def _onready_paths(src: str) -> dict:
    return {m.group(1): m.group(2) for m in re.finditer(
        r"@onready var (\w+)(?:\s*:\s*\w+)?\s*=\s*\$([\w/]+)", src)}


def _under_scroll_in_scene(scene_text: str, path: str) -> bool:
    nodes = G.parse_tscn(scene_text)
    index = G.by_path(nodes)
    if path not in index:
        return False
    if index[path].type == "ScrollContainer":
        return True
    return any(a.type == "ScrollContainer" for a in G.ancestors(nodes, path))


def resolves_under_scroll(body: str, var: str, onready: dict, scene_text: str | None,
                          hops: int = 0) -> bool:
    """Follow `<parent>.add_child(<var>)` up through locally built containers
    to a ScrollContainer, or to an `@onready $Path` that sits under one."""
    if hops > 4:
        return False
    m = re.search(r"(\w+)\.add_child\(%s\b" % re.escape(var), body)
    if not m:
        return False
    parent = m.group(1)
    local = re.search(r"(?:var\s+)?%s\s*:?=\s*(\w+)\.new\(\)" % re.escape(parent), body)
    if local:
        if local.group(1) == "ScrollContainer":
            return True
        return resolves_under_scroll(body, parent, onready, scene_text, hops + 1)
    if parent in onready and scene_text is not None:
        return _under_scroll_in_scene(scene_text, onready[parent])
    return False


def script_census(name: str, src: str, scene_text: str | None):
    """(resolved, unresolved) code-built fit_content RichTextLabels."""
    resolved, unresolved = [], []
    onready = _onready_paths(src)
    for fname, body in _functions(src).items():
        for m in _NEW.finditer(body):
            var = m.group(1)
            if f"{var}.fit_content = true" not in body:
                continue
            if resolves_under_scroll(body, var, onready, scene_text):
                resolved.append((name, var, fname))
            else:
                unresolved.append((name, var, fname))
    return resolved, unresolved


def toggles(name: str, src: str) -> list:
    """`<v>.fit_content = true` on a label the function did not build here."""
    out = []
    for fname, body in _functions(src).items():
        built = {m.group(1) for m in _NEW.finditer(body)}
        for m in re.finditer(r"(\w+)\.fit_content = true", body):
            if m.group(1) not in built:
                out.append((name, fname, m.group(1), body))
    return out


@pytest.fixture(scope="module")
def tree():
    scenes = {p.name: G.read(p) for p in G.client_scenes()}
    scripts = {p.name: G.read(p) for p in G.client_scripts()}
    return scenes, scripts


def _scene_for(script_name: str, scenes: dict):
    return scenes.get(script_name.replace(".gd", ".tscn"))


class TestTheSceneArm:
    def test_every_fit_content_label_has_a_scroll_above_it(self, tree):
        scenes, _ = tree
        found = [v for n, t in scenes.items() for v in scene_violations(n, t)]
        assert sorted(found) == sorted(ALLOW_SCENE), found

    def test_the_census_saw_the_labels(self, tree):
        scenes, _ = tree
        labels = fit = inside = 0
        for text in scenes.values():
            nodes = G.parse_tscn(text)
            for node in nodes:
                if node.type != "RichTextLabel":
                    continue
                labels += 1
                if node.props.get("fit_content") == "true":
                    fit += 1
                    if any(a.type == "ScrollContainer" for a in G.ancestors(nodes, node.path)):
                        inside += 1
        assert labels >= 24 and fit >= 13 and inside >= 12, (labels, fit, inside)
        for scene, path in (("main.tscn", "OutputDisplay"), ("strategic_ledger.tscn", "ContentArea")):
            nodes = G.parse_tscn(scenes[scene])
            assert any(n.name == path for n in nodes), (scene, path)


class TestTheScriptArm:
    def test_every_code_built_fit_content_label_resolves_or_is_named(self, tree):
        scenes, scripts = tree
        unresolved = set()
        for name, src in scripts.items():
            _resolved, missing = script_census(name, G.code_lines(src), _scene_for(name, scenes))
            unresolved |= {(n, v) for n, v, _f in missing}
        assert unresolved == set(ALLOW_SCRIPT), unresolved

    def test_the_census_resolved_the_known_lists(self, tree):
        scenes, scripts = tree
        resolved = []
        for name, src in scripts.items():
            r, _u = script_census(name, G.code_lines(src), _scene_for(name, scenes))
            resolved += r
        assert len(resolved) >= 9, resolved
        # 8 -> 12 flipped consciously: VP-1 (S14b part 2) adds the road page's
        # four labels (the step-1 row, the empty page, the headline, a road's
        # block) — every one in the wizard's scrolled list. 12 -> 15 flipped
        # consciously at S14b part 3: the Acts block's three (its heading, an
        # Act's row, a refusal's reason) — the same scrolled list. 15 -> 16
        # flipped consciously at S14d part 1 (October 23, 2026): the first-open
        # line's row (`_add_first_open_line`) — the same scrolled list.
        assert sum(1 for n, _v, _f in resolved if n == "diplomacy_wizard.gd") == 16
        assert any(n == "campaign_log.gd" for n, _v, _f in resolved), "the log's rows"


class TestTheToggleArm:
    def test_a_switched_label_switches_back_to_a_bounded_scroll(self, tree):
        _, scripts = tree
        found = []
        for name, src in scripts.items():
            for n, fname, var, body in toggles(name, G.code_lines(src)):
                ok = (f"{var}.fit_content = false" in body and f"{var}.scroll_active = true" in body)
                found.append((n, fname, var, ok))
        assert all(ok for *_rest, ok in found), found
        names = {(n, f) for n, f, _v, _ok in found}
        assert ("tutorial_overlay.gd", "_fit_card_height") in names
        assert ("utils.gd", "bound_rich_body") in names


class TestTheAllowListIsProven:
    def test_each_entry_carries_its_proof(self, tree):
        _, scripts = tree
        tutor = G.func_body(scripts["tutorial_overlay.gd"], "_fit_card_height")
        assert "_body.fit_content = false" in tutor and "_body.scroll_active = true" in tutor
        assert "Utils.bound_rich_body(" in G.func_body(scripts["notification_bar.gd"],
                                                      "_fit_expanded_body")
        assert "_fit_expanded_body.call_deferred()" in G.func_body(
            scripts["notification_bar.gd"], "_position_expanded_panel")
        assert "const MAX_SUGGESTIONS := 5" in scripts["main.gd"]
        # UXR-X9: the verdict no longer stands free — a bounded room that ends
        # above the nameplate and scrolls inside itself.
        verdict = G.func_body(scripts["battle_diorama.gd"], "_build_verdict_and_plate")
        assert "_verdict.fit_content = false" in verdict and "_verdict.scroll_active = true" in verdict
        assert "_verdict.size = Vector2(_verdict.size.x, maxf(room, VERDICT_ROOM_MIN))" in G.func_body(
            scripts["battle_diorama.gd"], "_fit_verdict_room")

    def test_the_rail_body_scrolls_with_the_wheel(self, tree):
        """A bounded body that scrolls must take the wheel itself (a
        RichTextLabel's default filter is STOP; nothing may set it IGNORE)."""
        _, scripts = tree
        body = G.func_body(scripts["notification_bar.gd"], "_show_expanded_panel")
        assert "body.mouse_filter" not in body

    def test_floorless_scrolls_only_fall(self, tree):
        scenes, _ = tree
        floorless = []
        for name, text in scenes.items():
            for node in G.parse_tscn(text):
                if node.type == "ScrollContainer" and "custom_minimum_size" not in node.props:
                    floorless.append((name, node.path))
        assert len(floorless) <= FLOORLESS_SCROLL_RATCHET, floorless


class TestTheCensusCatchesTheClass:
    """The PS18-R7 lesson: a census that cannot fail proves nothing."""

    def test_a_label_under_a_plain_box_is_caught(self):
        scene = ('[gd_scene format=3]\n\n[node name="Root" type="CanvasLayer"]\n\n'
                 '[node name="PanelContainer" type="PanelContainer" parent="."]\n\n'
                 '[node name="VBox" type="VBoxContainer" parent="PanelContainer"]\n\n'
                 '[node name="Body" type="RichTextLabel" parent="PanelContainer/VBox"]\n'
                 "fit_content = true\n")
        assert scene_violations("x.tscn", scene) == [("x.tscn", "PanelContainer/VBox/Body")]

    def test_a_label_deep_under_a_scroll_passes(self):
        scene = ('[gd_scene format=3]\n\n[node name="Root" type="Control"]\n\n'
                 '[node name="Scroll" type="ScrollContainer" parent="."]\n\n'
                 '[node name="VBox" type="VBoxContainer" parent="Scroll"]\n\n'
                 '[node name="Margin" type="MarginContainer" parent="Scroll/VBox"]\n\n'
                 '[node name="Body" type="RichTextLabel" parent="Scroll/VBox/Margin"]\n'
                 "fit_content = true\n")
        assert scene_violations("x.tscn", scene) == []

    def test_a_code_built_label_in_a_plain_box_is_caught(self):
        src = ("func f():\n\tvar box = VBoxContainer.new()\n\tadd_child(box)\n"
               "\tvar lbl = RichTextLabel.new()\n\tlbl.fit_content = true\n\tbox.add_child(lbl)\n")
        resolved, unresolved = script_census("x.gd", src, None)
        assert resolved == [] and unresolved == [("x.gd", "lbl", "f")]

    def test_a_toggle_without_its_way_back_is_caught(self):
        src = "func f():\n\t_body.fit_content = true\n"
        (n, fname, var, body), = toggles("x.gd", src)
        assert not (f"{var}.fit_content = false" in body and f"{var}.scroll_active = true" in body)
