"""Session UI-6: the enemy phase (F19) and the battle diorama (F20).

Source pins (no engine): the readers' complaints, each answered where it can be
read off the scripts.  F19: a one-line summary leads the report, the detail ink
is lifted to >= 4.5 : 1 on the dialog's ground, the scroll rests on a whole
entry; the page branch is gated on the folded switch.  F20: the armies are
larger and fill a taller stage, the italic captions stand on the body step, and
Replay / Close are real buttons (Close the primary).
"""
from __future__ import annotations

import re
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "godot-client" / "project-sovereign" / "scripts"
ENEMY = (SCRIPTS / "enemy_phase_dialog.gd").read_text(encoding="utf-8")
DIORAMA = (SCRIPTS / "battle_diorama.gd").read_text(encoding="utf-8")


def _const(src: str, name: str) -> float:
    return float(re.search(r"(?m)^const %s := ([0-9.]+)" % name, src).group(1))


def _lum(rgb):
    def ch(v):
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _lighten(rgb, amount):
    return tuple(c + (1.0 - c) * amount for c in rgb)


def _ratio(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


class TestEnemyPhaseSummary:
    def test_a_summary_line_leads_the_entries(self):
        assert "func _phase_summary(nations: Dictionary) -> String:" in ENEMY
        head = ENEMY.index("var summary := _phase_summary(nations)")
        first_court = ENEMY.index("for nation in nations:", head)
        assert head < first_court, "the summary is built before the first court's entries"

    def test_summary_is_counted_from_the_entries_own_kinds(self):
        body = ENEMY[ENEMY.index("func _phase_summary"):ENEMY.index("func _connect_entry_snap")]
        for needle in ('"battle"', '"garrison_assault"', '"conquest"', "captured_from",
                       "region_conquered", "advances", "advance"):
            assert needle in body, needle

    def test_summary_is_folded_only(self):
        i = ENEMY.index("var summary := _phase_summary(nations)")
        assert "if Utils.explanations_folded():" in ENEMY[i - 120:i]

    def test_on_the_page_every_entry_is_byte_for_byte(self):
        assert re.search(r"if Utils\.explanations_folded\(\):\n\t+entry_text = _lighten_details\(entry_text\)", ENEMY)
        assert "content += entry_text" in ENEMY


class TestDetailInkReads:
    GROUND = (0.102, 0.102, 0.18)

    def test_ground_matches_the_scene_fill(self):
        tscn = (SCRIPTS.parent / "scenes" / "enemy_phase_dialog.tscn").read_text(encoding="utf-8")
        assert "bg_color = Color(0.102, 0.102, 0.18, 1)" in tscn
        assert "const DETAIL_GROUND := Color(0.102, 0.102, 0.18, 1.0)" in ENEMY

    def test_lifted_error_ink_reads_at_least_4_5(self):
        lift = _const_lift()
        for hexv in ("d16969", "a0a0a8"):
            rgb = tuple(int(hexv[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
            assert _ratio(_lighten(rgb, lift), self.GROUND) >= 4.5, hexv

    def test_the_lift_loops_until_the_floor_is_met(self):
        body = ENEMY[ENEMY.index("func _detail_hex"):ENEMY.index("func _contrast")]
        assert "< 4.5" in body and "lightened(" in body

    def test_only_indented_detail_runs_are_lifted(self):
        body = ENEMY[ENEMY.index("func _lighten_details"):ENEMY.index("func _phase_summary")]
        assert '"]    "' in body, "the heading line (no indent) keeps its ink"


def _const_lift() -> float:
    return float(re.search(r"const DETAIL_LIFT := ([0-9.]+)", ENEMY).group(1))


class TestWholeEntryScroll:
    def test_the_scroll_snaps_to_a_card_head(self):
        assert "func _snap_to_entry() -> void:" in ENEMY
        assert "Utils.CARD_UNDERLAY.cards_in(" in ENEMY
        assert "_connect_entry_snap()" in ENEMY[ENEMY.index("fit_reading_window"):]


class TestDioramaFillsTheField:
    def test_armies_are_larger(self):
        assert _const(DIORAMA, "FIGURE_PX") >= 76.0
        assert "var spread := 84.0 if arm == \"ship\" else 42.0" in DIORAMA

    def test_the_stage_carries_the_battle(self):
        assert _const(DIORAMA, "STAGE_H") >= 430.0
        assert _const(DIORAMA, "TRAY_H") >= _const(DIORAMA, "STAGE_H") + 300.0

    def test_italic_captions_stand_on_the_body_step(self):
        assert 'faith_l.theme_type_variation = &"BodyLarge"' in DIORAMA
        assert 'g.theme_type_variation = &"BodyLarge"' in DIORAMA

    def test_close_is_primary_and_replay_is_gilt(self):
        assert '_btn_close.theme_type_variation = &"PrimaryButton"' in DIORAMA
        assert 'add_theme_stylebox_override("normal", _replay_face(false))' in DIORAMA
        assert "func _replay_face(hover: bool) -> StyleBox:" in DIORAMA

    def test_no_font_size_overrides_added(self):
        assert "add_theme_font_size_override" not in DIORAMA
        assert "[font_size" not in DIORAMA and "[font_size" not in ENEMY
