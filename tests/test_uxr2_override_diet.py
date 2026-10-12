"""UXR-2 part 4 — the override diet (Pre-Deploy S9 Slice B, October 12, 2026).

The client's type sizes live in the THEME, as named steps, not in raw
per-node overrides. UXR-1 lifted the floor (no raw size under 15); UXR-2 turns
what survived into named references (`theme_type_variation`), pixel-identical
by the user's ruling — one step per size in use:

    Caption / CaptionButton / CaptionRich 14 · (the theme's own 16) ·
    BodyLarge / BodyLargeRich 17 · Lead / LeadRich 18 · ScreenTitle 20 ·
    DialogTitle 22 · DialogTitleLarge 24 · DisplayTitle 28 · DisplayTitleLarge 30
    (+ HeadingLabel 22, the styled heading, unchanged)

At S9's start the client carried 72 raw overrides (44 in scenes, 28 in
scripts — not the plan's 268, which predated UXR-1's sweep). 22 were the
theme's own 16 and were deleted; the rest became named steps. What remains is
a NAMED exemption with an exact count per file, and the total is a RATCHET.

This census also closes the loophole UXR-X5 and UXR-X6 escaped through: the
floor's census read only literal overrides, so a size passed through a
parameter (`_mk_label(…, fsize)`, `max(7, font_size - 3)`) was invisible. Here
every `add_theme_font_size_override(` counts, literal or not, and a computed
size outside the named ledger fails.
"""
from __future__ import annotations

import re

import pytest

from tests import _godot_scenes as G

# The raw overrides that survive, per file, with the reason each stays raw.
EXEMPT = {
    "map_renderer_base.gd": 7,   # the map's world-space furniture, sized by the camera (UXR-X4, S9b)
    "europe_map_smoke.gd": 1,    # the developer smoke scene — no player sees it
    "main_menu.gd": 5,           # the title screen's display type on its own runtime FontVariations
    "battle_diorama.gd": 5,      # the tableau's engraved display: clash 26, odometers 24, banner 30, plate 19
}
RAW_RATCHET = 18                 # 72 at S9's start → 18; it may fall, never rise
# Sizes passed as an expression, not a literal — each named, nowhere else.
NON_LITERAL = {
    "map_renderer_base.gd": 1,   # label_font_size, the camera's zoom tier
    "main_menu.gd": 1,           # the prominent / plain menu button
}
BBCODE_SIZE_RATCHET = 2          # main.gd's end heading 24, proclamation_popup.gd's 26
# The named ladder, exactly (a step's size is a visible decision).
LADDER = {
    "Caption": {"font_size": 14},
    "CaptionButton": {"font_size": 14},
    "CaptionRich": {"normal_font_size": 14, "bold_font_size": 14,
                    "italics_font_size": 14, "bold_italics_font_size": 14},
    "BodyLarge": {"font_size": 17},
    "BodyLargeRich": {"normal_font_size": 17, "bold_font_size": 17, "italics_font_size": 17},
    "Lead": {"font_size": 18},
    "LeadRich": {"normal_font_size": 18, "bold_font_size": 18},
    "ScreenTitle": {"font_size": 20},
    "DialogTitle": {"font_size": 22},
    "HeadingLabel": {"font_size": 22},
    "DialogTitleLarge": {"font_size": 24},
    "DisplayTitle": {"font_size": 28},
    "DisplayTitleLarge": {"font_size": 30},
}
STYLED = {"HeadingLabel"}        # the one step that also sets a face, a colour, an outline
# A variation's base type, and the node classes it may be set on.
ACCEPTS = {
    "Label": {"Label"},
    "Button": {"Button", "CheckBox", "CheckButton", "OptionButton", "MenuButton"},
    "RichTextLabel": {"RichTextLabel"},
}

_SCENE_OVERRIDE = re.compile(r"(?m)^theme_override_font_sizes/")
_CALL_STRINGS = re.compile(r'set\("theme_override_font_sizes/|"add_theme_font_size_override"')


def raw_sites(name: str, text: str) -> list:
    """Every raw font-size override in one file: a scene's override lines, or
    a script's override calls in CODE (comments and docstrings dropped), plus
    the `set(...)` / string-call forms that would dodge a plain grep."""
    if name.endswith(".tscn"):
        return _SCENE_OVERRIDE.findall(text)
    code = G.code_lines(text)
    return G.call_args(code, "add_theme_font_size_override") + _CALL_STRINGS.findall(code)


def non_literal_sites(text: str) -> list:
    code = G.code_lines(text)
    return [a for a in G.call_args(code, "add_theme_font_size_override")
            if len(a) < 2 or not re.fullmatch(r"\d+", a[1])]


@pytest.fixture(scope="module")
def files():
    out = {}
    for p in G.client_scenes() + G.client_scripts():
        out[p.name] = G.read(p)
    return out


@pytest.fixture(scope="module")
def theme():
    return G.theme_variations(G.read(G.THEME))


class TestTheRatchet:
    def test_the_raw_total_is_the_ratchet(self, files):
        total = sum(len(raw_sites(n, t)) for n, t in files.items())
        assert total <= RAW_RATCHET, f"{total} raw overrides (ratchet {RAW_RATCHET})"
        assert total == RAW_RATCHET, (
            f"the diet fell to {total}: lower RAW_RATCHET and the EXEMPT table")

    def test_only_the_named_exemptions_carry_raw_sizes(self, files):
        counts = {n: len(raw_sites(n, t)) for n, t in files.items()}
        offenders = {n: c for n, c in counts.items() if c and n not in EXEMPT}
        assert offenders == {}, f"raw sizes outside the exemptions: {offenders}"
        for name, want in EXEMPT.items():
            assert counts.get(name) == want, (name, counts.get(name), want)
        assert sum(EXEMPT.values()) == RAW_RATCHET

    def test_no_computed_size_outside_the_ledger(self, files):
        found = {n: len(non_literal_sites(t)) for n, t in files.items() if n.endswith(".gd")}
        found = {n: c for n, c in found.items() if c}
        assert found == NON_LITERAL, found

    def test_no_raw_size_below_the_body_floor_outside_the_map(self, files):
        low = []
        for name, text in files.items():
            if name == "map_renderer_base.gd" or not name.endswith(".gd"):
                continue
            for args in G.call_args(G.code_lines(text), "add_theme_font_size_override"):
                if len(args) > 1 and re.fullmatch(r"\d+", args[1]) and int(args[1]) < 16:
                    low.append((name, args))
        assert low == []

    def test_bbcode_sizes_are_a_ratchet(self, files):
        hits = [(n, m) for n, t in files.items() if n.endswith(".gd")
                for m in re.findall(r"\[font_size=", G.code_lines(t))]
        assert len(hits) <= BBCODE_SIZE_RATCHET, hits


class TestTheLadder:
    def test_the_ladder_is_exactly_the_named_steps(self, theme):
        assert {n: v["sizes"] for n, v in theme.items()} == LADDER

    def test_every_step_but_the_heading_is_size_only(self, theme):
        for name, v in theme.items():
            if name in STYLED:
                continue
            assert v["other"] == [], (name, v["other"])

    def test_a_rich_step_sets_its_body_size_and_agrees_with_itself(self, theme):
        for name, v in theme.items():
            if v["base_type"] != "RichTextLabel":
                continue
            assert "normal_font_size" in v["sizes"], name
            assert len(set(v["sizes"].values())) == 1, (name, v["sizes"])

    def test_the_instrument_knows_every_caption_step(self, theme):
        """UXR-0 scores a row CAPTION only if its variation is in the harness's
        own list; a sub-16 step missing from it would be judged as body."""
        harness = G.read(G.REPO / "tools" / "iq10_surface_screenshot.gd")
        m = re.search(r"_CAPTION_VARIATIONS := \[([^\]]*)\]", harness)
        assert m, "the harness's caption list is gone"
        listed = set(re.findall(r'"(\w+)"', m.group(1)))
        for name, v in theme.items():
            if min(v["sizes"].values()) < 16:
                assert name in listed, name
        for name in listed:
            assert name in theme and min(theme[name]["sizes"].values()) >= 14, name


class TestEveryReferenceResolves:
    def test_scene_references_exist_and_fit_their_node(self, files, theme):
        seen = 0
        for name, text in files.items():
            if not name.endswith(".tscn"):
                continue
            for node in G.parse_tscn(text):
                var = node.props.get("theme_type_variation")
                if not var:
                    continue
                seen += 1
                step = var.strip('&"')
                assert step in theme, (name, node.path, step)
                if node.type:
                    assert node.type in ACCEPTS[theme[step]["base_type"]], (
                        name, node.path, node.type, step)
                assert not any(k.startswith("theme_override_font_sizes/") for k in node.props), (
                    name, node.path, "a variation AND a raw override")
        assert seen >= 100, f"the census saw only {seen} scene references"

    def test_script_references_exist_and_fit_where_the_class_is_known(self, files, theme):
        seen = resolved = 0
        for name, text in files.items():
            if not name.endswith(".gd"):
                continue
            code = G.code_lines(text)
            for m in re.finditer(r"([\w.]+)\.theme_type_variation = &\"(\w+)\"", code):
                seen += 1
                var, step = m.group(1).split(".")[-1], m.group(2)
                assert step in theme, (name, var, step)
                # the NEAREST preceding declaration: one name is reused per function
                decls = list(re.finditer(r"\b(?:var\s+)?%s\s*:?=\s*(\w+)\.new\(\)" % re.escape(var),
                                         code[:m.start()]))
                cls = decls[-1] if decls else None
                if cls and cls.group(1) in {c for s in ACCEPTS.values() for c in s}:
                    resolved += 1
                    assert cls.group(1) in ACCEPTS[theme[step]["base_type"]], (
                        name, var, cls.group(1), step)
        assert seen >= 60, f"the census saw only {seen} script references"
        assert resolved >= 30, f"only {resolved} script references resolved to a class"

    def test_the_tableau_helper_passes_only_named_steps(self, files, theme):
        """`_mk_label`'s one non-literal assignment is fed by its callers."""
        code = G.code_lines(files["battle_diorama.gd"])
        assert "l.theme_type_variation = variation" in code
        for args in G.call_args(code, "_mk_label"):
            step = args[2].strip('&"')
            assert step == "" or (step in theme and theme[step]["base_type"] == "Label"), args


class TestTheCensusSeesWhatItCounts:
    def test_blindness_guards(self, files, theme):
        assert sum(n.endswith(".tscn") for n in files) >= 39
        assert sum(n.endswith(".gd") for n in files) >= 56
        assert len(theme) >= 13

    def test_a_computed_size_is_caught(self):
        src = 'func f():\n\tx.add_theme_font_size_override("font_size", size)\n'
        assert len(raw_sites("a.gd", src)) == 1
        assert len(non_literal_sites(src)) == 1

    def test_the_dodges_are_caught(self):
        src = ('func f():\n\tx.set("theme_override_font_sizes/font_size", 12)\n'
               '\tx.call("add_theme_font_size_override", "font_size", 12)\n')
        assert len(raw_sites("a.gd", src)) == 2

    def test_a_comment_is_not_counted(self):
        src = '# add_theme_font_size_override("font_size", 12)\nfunc f():\n\tpass\n'
        assert raw_sites("a.gd", src) == []

    def test_a_scene_override_and_a_double_node_are_caught(self, theme):
        scene = ('[gd_scene format=3]\n\n[node name="Root" type="Control"]\n\n'
                 '[node name="T" type="Label" parent="."]\ntheme_type_variation = &"ScreenTitle"\n'
                 "theme_override_font_sizes/font_size = 20\n")
        assert len(raw_sites("a.tscn", scene)) == 1
        node = G.by_path(G.parse_tscn(scene))["T"]
        assert node.props["theme_type_variation"] == '&"ScreenTitle"'
        assert any(k.startswith("theme_override_font_sizes/") for k in node.props)
