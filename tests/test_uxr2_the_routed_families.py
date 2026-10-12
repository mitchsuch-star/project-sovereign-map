"""UXR-2 Slice A — "the routed families read" (Pre-Deploy S9, October 12, 2026).

The two families the whole-client readability census routed to UXR-2
(`docs/BUG_FIXES.md` §UXR-1b): UXR-X6, the war-detail popup's bar text, and
UXR-X5, the battle diorama's tableau labels. Both escaped UXR-1's floor
because their sizes were COMPUTED — `max(7, font_size - 3)` and
`_mk_label(…, fsize)` — and the floor's census read only literal overrides.

The fix gives both families the theme's sizes (body 16, Caption 14). For the
diorama that took a structural change: the per-depth scale `1 − 0.12·depth`
now applies to a block's ART (figures, standard, locket) and not to its
TEXT, whose anchors alone follow the depth; the status line moves under the
feet beside the faith caption, because two lines at the floor's sizes fit
between ranks and three do not. These pins hold the structure and mirror
the geometry in Python (the house style of `TestTheLineFitsTheBaize` in
`tests/test_sf7_s9_the_frames.py`); the readings themselves are the
committed record `docs/audits/uxr0/readability_routed_2026_10_12.json`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
ROUTED_RECORD = REPO / "docs" / "audits" / "uxr0" / "readability_routed_2026_10_12.json"

# EB Garamond's hhea line height (ascent + descent + gap) in em, read off the
# font file by the reconnaissance; a 14-px caption line is ≈ 18.3 px tall.
LINE_EM = 1.305
CAPTION_PX = 14.0
BODY_PX = 16.0


def _src(name: str) -> str:
    return (SCRIPTS / name).read_text(encoding="utf-8")


def _body(name: str, func: str) -> str:
    """One function's text: from its `func` line to the next top-level
    `func` / `static func` (a static func ends a body too)."""
    src = _src(name)
    m = re.search(r"(?m)^(static )?func %s\(" % re.escape(func), src)
    assert m, f"{name}: func {func} is gone"
    rest = src[m.end():]
    nxt = re.search(r"(?m)^(static )?func ", rest)
    return src[m.start():m.end() + (nxt.start() if nxt else len(rest))]


def _call_args(src: str, func: str) -> list:
    """Every call of `func(` in `src` (not its definition), split into its
    top-level arguments — bracket- and string-aware, since an argument like
    `c.get("name", "")` carries its own commas."""
    calls = []
    for m in re.finditer(r"(?<!\w)%s\(" % re.escape(func), src):
        if src[max(0, m.start() - 5):m.start()] == "func ":
            continue
        depth, i, start, args, quote = 1, m.end(), m.end(), [], None
        while depth:
            ch = src[i]
            if quote:
                if ch == "\\":
                    i += 1
                elif ch == quote:
                    quote = None
            elif ch in "\"'":
                quote = ch
            elif ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
            elif ch == "," and depth == 1:
                args.append(src[start:i].strip())
                start = i + 1
            i += 1
        args.append(src[start:i - 1].strip())
        calls.append(args)
    return calls


def _const(name: str, const: str) -> float:
    m = re.search(r"(?m)^const %s := ([-0-9.]+)" % const, _src(name))
    assert m, f"{name}: const {const} is gone"
    return float(m.group(1))


# ═══════════════════════════════════════════════════════════════════════
# UXR-X6 — the war-detail popup's bar text
# ═══════════════════════════════════════════════════════════════════════

class TestTheBarTextIsCaption:
    def test_no_size_override_anywhere_in_the_popup(self):
        assert "add_theme_font_size_override" not in _src("war_detail_popup.gd"), (
            "the bar's text takes the theme's Caption, never a computed size")

    def test_the_score_and_both_tags_are_caption(self):
        body = _body("war_detail_popup.gd", "_create_tug_of_war_bar")
        for who in ("score_label", "enemy_lbl", "france_lbl"):
            assert f'{who}.theme_type_variation = &"Caption"' in body, who
        assert "font_size" not in body, "the font_size parameter is gone"

    def test_the_bar_is_tall_enough_for_a_caption_line(self):
        height = _const("war_detail_popup.gd", "WAR_BAR_HEIGHT")
        assert height >= CAPTION_PX * LINE_EM + 3.0, (
            "a 14-px line is ≈ 18.3 px tall; the bar must hold it")
        src = _src("war_detail_popup.gd")
        assert "_current_nation, 280, WAR_BAR_HEIGHT" in src
        assert "_add_labeled_tug_of_war_bar(opp, score, 280, WAR_BAR_HEIGHT)" in src

    def test_a_tag_slot_holds_two_capitals_at_14_past_the_rim(self):
        """UXR-X8: the track's rounded cap is 14 px (its 3-slice margin); a tag
        3 px in sat under the gold rim, clipped once it was readable."""
        assert _const("war_detail_popup.gd", "WAR_BAR_TAG_W") >= 26.0
        assert _const("war_detail_popup.gd", "WAR_BAR_TAG_INSET") >= 14.0
        body = _body("war_detail_popup.gd", "_create_tug_of_war_bar")
        assert "track.patch_margin_left = 14" in body
        assert ("_anchor_bar_child(enemy_lbl, 0.0, 0.0, WAR_BAR_TAG_INSET, "
                "WAR_BAR_TAG_INSET + WAR_BAR_TAG_W)") in body
        assert ("_anchor_bar_child(france_lbl, 1.0, 1.0, -WAR_BAR_TAG_INSET - WAR_BAR_TAG_W, "
                "-WAR_BAR_TAG_INSET)") in body


# ═══════════════════════════════════════════════════════════════════════
# UXR-X5 — the diorama's text leaves the depth scale
# ═══════════════════════════════════════════════════════════════════════

class TestTheTextLeavesTheDepthScale:
    def test_the_art_recedes_the_block_does_not(self):
        body = _body("battle_diorama.gd", "_make_block")
        assert "art.scale = Vector2(block_scale, block_scale)" in body
        assert "block.scale =" not in body
        # the figures, the standard and the locket ride the art
        assert body.count("art.add_child(f)") == 2
        assert "art.add_child(standard)" in body
        assert "art.add_child(locket)" in body

    def test_no_counter_scale(self):
        """A `1/b` counter-scale lands a float hair under 1.0: a 14-px caption
        would read 13.99999 against the instrument's tolerance and flip RED."""
        assert "/ block_scale" not in _src("battle_diorama.gd")

    def test_mk_label_takes_a_theme_variation_never_a_size(self):
        body = _body("battle_diorama.gd", "_mk_label")
        assert "variation: StringName" in body
        assert "add_theme_font_size_override" not in body
        calls = _call_args(_src("battle_diorama.gd"), "_mk_label")
        assert len(calls) >= 12, calls
        for args in calls:
            assert args[2] in ('&"Caption"', '&""'), f"a size reached _mk_label: {args}"

    def test_the_only_literal_sizes_are_the_engraved_display(self):
        """The tableau keeps five display sizes (clash 26, the odometer
        figures 24, the banner 30, the plate 19) and the verdict's 17 —
        every one a literal at or above the body floor; nothing computed."""
        calls = _call_args(_src("battle_diorama.gd"), "add_theme_font_size_override")
        assert all(re.fullmatch(r"\d+", a[1]) for a in calls), calls
        assert sorted(int(a[1]) for a in calls) == [17, 17, 19, 24, 24, 26, 30]

    def test_the_status_is_a_fate_line_under_the_feet(self):
        body = _body("battle_diorama.gd", "_make_block")
        assert "var fate_y := FAITH_CAPTION_Y * block_scale" in body
        assert "status_l.position = Vector2(text_x" not in body
        assert body.index("status_l.position") < body.index("fate_y += FATE_PITCH")
        assert body.index("fate_y += FATE_PITCH") < body.index("faith_l.position")
        assert body.count("_keep_fate_on_baize(") == 2


class TestFourRanksStayLegible:
    """UXR-X7, found by the four-contingent board (never shot before): at four
    ranks the next rank's standard (a block's art at +3) stood over a name,
    and the reserve tail — one step beyond the last rank — ran across the
    depth-2 name row. Both held at HEAD before any UXR-2 change."""

    def test_every_rank_s_words_draw_above_every_standard(self):
        body = _body("battle_diorama.gd", "_make_block")
        text_z = _const("battle_diorama.gd", "TEXT_Z")
        std_z = float(re.search(r"std\.z_index = (\d+)", _src("battle_diorama.gd")).group(1))
        # a rank's block is 20 − depth (depth ≤ 3); its text block + TEXT_Z,
        # the next rank's standard (20 − depth − 1) + std_z
        assert 20 - 3 + text_z > 20 + std_z
        for who in ("name_l", "strength_l", "status_l", "faith_l"):
            assert f"{who}.z_index = TEXT_Z" in body, who
        for who in ("name_l", "strength_l"):
            assert f"_outline_over_colours({who})" in body, who

    def test_the_tail_sits_in_the_outboard_bottom_corner(self):
        src = _src("battle_diorama.gd")
        assert "base_y - step_y * fought.size() - 8.0" not in src
        assert "_stage.size.y - BAIZE_PAD - tail.get_minimum_size().y" in src


class TestTheLineHoldsTheText:
    """The Python mirror of the tableau's geometry (stage-local px, tray scale
    1.0): for every count of contingents the cap allows, the identity stack
    (name, strength) clears the next rank's locket, and the fate lines stay
    on the baize."""

    @staticmethod
    def _stage():
        def c(k):
            return _const("battle_diorama.gd", k)
        return c("TRAY_W") - c("STAGE_MARGIN_X") * 2.0, c("STAGE_H")

    @classmethod
    def _rows(cls, n):
        sw, sh = cls._stage()
        base_y = sh - 58.0
        step_y = 66.0
        if n > 1:
            last = 1.0 - 0.12 * (n - 1)
            step_y = min(66.0, max(30.0, (base_y - 60.0 - 158.0 * last) / (n - 1)))
        return [(base_y - step_y * i, 1.0 - 0.12 * i) for i in range(n)]

    @pytest.mark.parametrize("n", [2, 3, 4])
    def test_the_strength_line_clears_the_inner_locket(self, n):
        pitch = _const("battle_diorama.gd", "TEXT_PITCH")
        assert pitch >= BODY_PX * 1.1, "the name's line needs its own height"
        rows = self._rows(n)
        for i in range(1, n):
            y, b = rows[i]
            inner_y, inner_b = rows[i - 1]
            strength_bottom = y - 156.0 * b + pitch + CAPTION_PX
            inner_locket_top = inner_y - 158.0 * inner_b
            assert strength_bottom <= inner_locket_top + 0.5, (n, i)

    def test_the_leads_status_stays_on_the_baize(self):
        _sw, sh = self._stage()
        y, b = self._rows(1)[0]
        bottom = y + _const("battle_diorama.gd", "FAITH_CAPTION_Y") * b + CAPTION_PX * LINE_EM
        assert bottom <= sh

    @pytest.mark.parametrize("n", [2, 3, 4])
    def test_a_reinforcers_status_and_three_lines_of_faith_stay_on_the_baize(self, n):
        _sw, sh = self._stage()
        y, b = self._rows(n)[1]
        fate = (y + _const("battle_diorama.gd", "FAITH_CAPTION_Y") * b
                + _const("battle_diorama.gd", "FATE_PITCH") + 3 * CAPTION_PX * LINE_EM)
        assert fate <= sh, (n, fate, sh)


# ═══════════════════════════════════════════════════════════════════════
# The reading
# ═══════════════════════════════════════════════════════════════════════

class TestTheRoutedReading:
    """The committed reading of the two families and their unshot states at
    the five resolutions with the derived scale. The whole-client ratchet in
    `tests/test_uxr0_readability.py` falls to 0 at UXR-2's landing re-shoot."""

    @pytest.fixture(scope="class")
    def record(self):
        assert ROUTED_RECORD.is_file(), ROUTED_RECORD
        return json.loads(ROUTED_RECORD.read_text(encoding="utf-8"))

    def test_every_routed_surface_reads_clean(self, record):
        flagged = []
        for sid, s in record["surfaces"].items():
            for key, r in s["readings"].items():
                if r["counts"]["red"] or r["counts"]["p1"] or r["flagged"]:
                    flagged.append((sid, key, r["counts"]["red"], r["counts"]["p1"]))
        assert flagged == []
        assert sum(r["counts"]["rows"] for s in record["surfaces"].values()
                   for r in s["readings"].values()) >= 800, "the census read the text"

    def test_the_new_states_were_shot_at_every_resolution(self, record):
        ids = record["surfaces"]
        for sid in ("diorama_aadj", "diorama_dadj", "diorama_rout_conquest",
                    "diorama_four_contingents", "diorama_naval", "war_detail_boot",
                    "war_detail_collapse_one", "war_detail_collapse_none", "war_detail_t20",
                    "war_detail_coalition_boot", "war_detail_coalition_t20"):
            assert sid in ids, sid
            assert len(ids[sid]["readings"]) == 5, sid
        assert record["physical_scale"] == "auto"
