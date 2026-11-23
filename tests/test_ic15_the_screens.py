"""Row IC, Session 4b - IC-15, THE CLIENT'S SCREENS: natures and what you learn.

Source-reading checks: the screens say Bold / Careful / To the letter, and show
what France learned of the enemy (with its age) only when something was learned.
The nature word itself is the SERVER's (`display_names.NATURE_WORDS`, one table):
no client script keeps a private copy.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "godot-client" / "project-sovereign"
SCRIPTS = ROOT / "scripts"


def _src(rel: str) -> str:
    base = ROOT / rel if rel.startswith("scenes/") else SCRIPTS / rel
    return base.read_text(encoding="utf-8")


def test_no_client_script_keeps_its_own_nature_table():
    """One table (the server's): a client copy would drift from it."""
    for path in sorted(list(SCRIPTS.glob("*.gd")) + list((ROOT / "scenes").glob("*.gd"))):
        text = path.read_text(encoding="utf-8")
        assert not re.search(r'return\s+"To the letter"', text), path.name
        assert "func nature_word(" not in text, path.name


def test_utils_reads_a_learned_row_as_plain_words():
    s = _src("utils.gd")
    body = s[s.index("static func learned_orders_text"):s.index("static func learned_tail")]
    # the server sends the orders as a LIST of sentences: joined, never str(list)
    assert "if orders is Array:" in body and '" ".join(parts)' in body
    tail = s[s.index("static func learned_tail"):]
    tail = tail[:tail.index("\nstatic func ")]
    assert 'when + ", " + how' in tail


def test_map_tooltip_shows_nature_outside_the_player_block():
    s = _src("scenes/map_renderer_base.gd")
    nature_at = s.index('"Nature: " + nature')
    personality_at = s.index('if personality != "":', nature_at)
    assert nature_at < personality_at
    assert '"Type: "' not in s
    assert s.index('"Trust: %s', personality_at) > personality_at


def test_bench_badge_uses_nature_with_its_line():
    s = _src("marshal_management.gd")
    assert 'c.get("nature", "")' in s and 'c.get("nature_line", "")' in s
    assert 'personality.capitalize()' not in s[s.index("nature_text"):s.index("nature_text") + 900]


def test_the_generals_card_shows_his_nature_beside_the_arm_and_the_nation():
    s = _src("marshal_management.gd")
    head = s[s.index("# ═══════ HEADER ═══════"):s.index("sheet += _court_line(m)")]
    assert 'm.get("nature", "")' in head and 'm.get("nature_line", "")' in head
    assert 'm.get("personality"' not in head
    # the roster's card — the one the page opens on — carries it too (pressed
    # in the real client: only the sheet's head did)
    roster = s[s.index("# the arm and the nation as tags (inline runs, the card's own idiom)"):]
    roster = roster[:roster.index("# what he is doing, in his status tone")]
    assert 'm.get("nature", "")' in roster and "tags += " in roster
    # every card head that draws the nation's tag draws the nature beside it
    assert s.count('Utils.bb_tag(Utils.display_nation_name(nation)') == s.count('m.get("nature", "")')


def test_help_terms_use_the_nature_words():
    s = _src("codex_terms.gd")
    assert "Each marshal is Bold, Careful or To the letter" in s
    assert "Bold men attack and careful men fortify" in s
    assert "a Literal marshal never defies" not in s
    assert "for an aggressive man" not in s


def test_tutorial_card_iv_uses_the_nature_words():
    s = _src("tutorial_overlay.gd")
    assert "the Bold marshal hates to sit still" in s
    assert "the aggressive marshal hates to sit still" not in s


def test_objection_dialog_says_the_servers_nature_word():
    s = _src("objection_dialog.gd")
    assert 'objection_data.get("nature", "")' in s
    assert '"nature": objection.get("nature", response.get("nature", ""))' in s
    assert '"Personality: %s"' not in s


def test_region_panel_shows_nature_and_learned_orders_only_when_known():
    s = _src("region_panel.gd")
    assert "func set_learned(payload: Dictionary)" in s
    assert "func _enemy_know_lines(m: Dictionary) -> String:" in s
    body = s[s.index("func _enemy_know_lines"):s.index("func set_war_goal_context")]
    assert 'if str(m.get("nation", "")) == _PLAYER_NATION:' in body
    assert "Utils.learned_orders_text(row)" in body and "Utils.learned_tail(row)" in body
    assert 'if orders != "":' in body
    assert s.count("_enemy_know_lines(m)") == 1


def test_war_detail_lists_what_we_know_or_nothing():
    s = _src("war_detail_popup.gd")
    assert "func set_learned(payload: Dictionary)" in s
    assert "What we know of their plans" in s
    block = s[s.index("func _known_plans_block"):s.index("func _table_px")]
    assert 'if lines == "":' in block and 'return ""' in block
    assert "Utils.learned_orders_text(row)" in block
    # the court's words name it already ("Austria's corps lean toward Bohemia")
    assert "display_nation_name(cname)" not in block
    assert "bbcode += _known_plans_block(w)" in s


def test_the_folded_war_page_lists_what_we_know_too():
    """IC4b-32 (pressed in the real client once the war plans were switched
    on): the Folded page — the one a player sees unless he unfolds the
    explanations — returns early with its tiles and tables, and the plans
    block stood only on the On-the-page path below it, so the war's page never
    said what the spy had brought back. The Folded tail carries it, before
    Recent Battles, where the On-the-page path prints it."""
    s = _src("war_detail_popup.gd")
    tail = s[s.index("func _figures_tail"):s.index("func _render_coalition_detail")]
    assert "_known_plans_block(w)" in tail
    assert tail.index("_known_plans_block(w)") < tail.index("_battles_table(w)")
    # the early return that skipped it still stands — the block rides the tail
    render = s[s.index("func _render_war_detail"):s.index("func _known_plans_block")]
    folded_return = render.index("_figures_tail(w, lead_line))")
    assert render.index("bbcode += _known_plans_block(w)") > folded_return


def test_main_caches_hands_on_and_clears_the_learned_key():
    s = _src("main.gd")
    body = s[s.index("func _process_active_wars"):]
    body = body[:body.index("active_wars_data = response.get")]
    assert 'response.get("learned", null)' in body
    # a full reply without the key: nothing is known any more (a peace put it away)
    assert 'response.has("active_wars")' in body and "learned_payload = {}" in body
    assert 'region_panel.has_method("set_learned")' in body
    assert 'war_detail_popup.has_method("set_learned")' in body
