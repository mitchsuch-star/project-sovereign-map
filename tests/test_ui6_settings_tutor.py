"""Session UI-6: the Settings segmented controls, the two new switches, the
merged cards, and the School of War card's lead line + bullets. Source pins
only (no engine)."""
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "godot-client" / "project-sovereign" / "scripts"


def _read(name):
    return (SCRIPTS / name).read_text(encoding="utf-8")


def _func(src, head):
    start = src.index(head)
    nxt = src.find("\nfunc ", start + 1)
    nxt2 = src.find("\nstatic func ", start + 1)
    ends = [e for e in (nxt, nxt2) if e > 0]
    return src[start:min(ends) if ends else len(src)]


class TestSettingsSegments:
    SRC = _read("settings_panel.gd")

    def test_short_choices_are_segmented_and_the_dropdowns_stay(self):
        for call in ("_add_segments(row, _window_mode,", "_add_segments(hud_row, _hud_width,",
                     "_add_segments(wide_row, _wide_map,", "_add_segments(font_row, _body_font,",
                     "_add_segments(explain_row, _explanations,",
                     "if keys.size() <= _SEGMENT_MAX_CHOICES:"):
            assert call in self.SRC, call
        # RE-POINTED by the interim blind reading ("a long wall of toggles and
        # segmented buttons"): a segmented control is for a choice of up to THREE;
        # the four-way choices (window, HUD width, tooltip delay) keep their drop-down
        assert "const _SEGMENT_MAX_CHOICES := 3" in self.SRC
        segs = _func(self.SRC, "func _add_segments")
        assert "if keys.size() > _SEGMENT_MAX_CHOICES:" in segs
        assert segs.index("if keys.size() > _SEGMENT_MAX_CHOICES:") < segs.index("ButtonGroup.new()")
        # the page branch is the dropdown, untouched
        body = _func(self.SRC, "func _sync_segments")
        assert "option.visible = not folded" in body and "b.visible = folded" in body

    def test_a_segment_fires_the_dropdowns_own_handler(self):
        body = _func(self.SRC, "func _on_segment_pressed")
        assert "option.select(index)" in body and "option.item_selected.emit(index)" in body

    def test_cards_merge_folded_only_and_restore(self):
        body = _func(self.SRC, "func _apply_card_merge")
        assert "Utils.explanations_folded()" in body
        assert ".reparent(lbox, false)" in body and ".reparent(fbox, false)" in body
        assert "_apply_card_merge()" in _func(self.SRC, "func _show_tab")

    def test_the_two_new_switches(self):
        assert '"NextMarshalToggle"' in self.SRC and "UiSettings.set_next_marshal_after_order(on)" in self.SRC
        assert '"ReadbackToggle"' in self.SRC and "UiSettings.set_readback(on)" in self.SRC
        refresh = _func(self.SRC, "func _refresh_new_controls")
        assert "get_next_marshal_after_order()" in refresh and "get_readback()" in refresh

    def test_the_scroll_rests_on_whole_rows(self):
        assert "Utils.keep_whole_lines(self)" in self.SRC
        assert "_snap_whole_rows.call_deferred()" in _func(self.SRC, "func _ready")


class TestTutorCard:
    SRC = _read("tutorial_overlay.gd")

    def test_folded_lead_and_bullets_page_paragraphs(self):
        body = _func(self.SRC, "func _render")
        assert "_lead_and_bullets(str(step[\"body\"]))" in body
        assert '_paragraphs(str(step["body"]), "\\n" if compact else "\\n\\n")' in body
        assert "Utils.explanations_folded()" in body

    def test_bullets_keep_every_sentence(self):
        body = _func(self.SRC, "static func _lead_and_bullets")
        assert "for i in range(1, sentences.size())" in body and "[ul]" in body and "[b]" in body

    def test_the_banner_is_a_wide_scene_and_short(self):
        assert 'const BANNER_PICTURE := {"tutorial": "ulm", "tutorial_table": "treaty"}' in self.SRC
        assert "BANNER_MAX_HEIGHT" in _func(self.SRC, "func _sync_banner")

    def test_the_action_wraps_and_the_card_clears_the_war_list(self):
        assert "_act_button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART" in self.SRC
        assert "rect.position.y - 2.0 * CARD_MARGIN" in self.SRC


class TestATabsHeadingStandsOnThePage:
    """UI6-X52 (Session UI-6, the final page census): a heading that only repeats
    its tab's name was FREED with its rule, in both modes — but On the page the
    tab row steps aside, so DISPLAY / SOUND / CONTROLS / CREDITS went missing
    there. Such a heading (and its rule) now steps aside only while the tabs
    show; On the page it stands as authored."""
    SRC = _read("settings_panel.gd")

    def test_the_heading_is_kept_and_marked_not_freed(self):
        body = _func(self.SRC, "func _paginate")
        assert "_tab_repeats.append(child)" in body and "mark_rule = true" in body
        assert "child.queue_free()" not in body

    def test_it_steps_aside_only_while_the_tabs_show(self):
        body = _func(self.SRC, "func _show_tab")
        assert "for node in _tab_repeats:" in body
        assert "(node as Control).visible = not paged" in body
        assert body.index("var paged := Utils.explanations_folded()") < body.index("for node in _tab_repeats:")
