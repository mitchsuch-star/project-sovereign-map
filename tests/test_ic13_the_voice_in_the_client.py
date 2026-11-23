"""Row IC, Session 4 (IC-13): the voice in the client.

Source-text pins (no engine): one helper draws a marshal's quoted line, the
terminal, the read-back, the morning report and the desk reach for it, and no
file prints a doubled opening quote.
"""
from pathlib import Path

CLIENT = Path(__file__).resolve().parent.parent / "godot-client" / "project-sovereign"
SCRIPTS = CLIENT / "scripts"


def _text(name: str) -> str:
    return (SCRIPTS / name).read_text(encoding="utf-8")


def test_voice_line_helper_exists():
    src = _text("voice_line.gd")
    assert "class_name VoiceLine" in src
    for sig in ("static func make(", "static func bbcode(", "static func rows("):
        assert sig in src


def test_main_reads_voices_and_uses_the_helper():
    src = _text("main.gd")
    assert '"voices"' in src
    assert "VoiceLine." in src


def test_card_and_desk_carry_says():
    assert "says" in _text("order_confirm_card.gd")
    desk = _text("desk_lines.gd")
    assert "says" in desk and "VoiceLine." in desk


def test_no_doubled_opening_quote():
    for path in list(SCRIPTS.glob("*.gd")) + list((CLIENT / "scenes").glob("*.gd")):
        assert "\u201c\u201c" not in path.read_text(encoding="utf-8"), path.name


def test_the_inline_portrait_stands_beside_the_name():
    src = _text("voice_line.gd")
    assert "static func portrait_bbcode(" in src
    assert "PortraitLocket._portrait_path(" in src
    assert "portrait_bbcode(speaker) +" in src       # `bbcode` leads with it
    assert "region=%d,%d,%d,%d" in src               # cropped to the locket's centre square


def test_his_own_idea_carries_his_line_on_the_ready_task():
    card = _text("selection_card.gd")
    assert "VoiceLine.plain_text(" in card and '.get("says", "")' in card


def test_every_line_said_is_drawn_once_with_his_name():
    """The census's client half (November 22, 2026): the task to prove himself
    (its own reply road) prints what he said; the after-battle report and the
    enemy phase's report stand the speaker's portrait beside each line; a
    refused reply on the renderer ahead of a modal prints his words; the order
    list's quoted line carries his name and portrait; the audience window
    heads his proposal with his own line, by name."""
    main = _text("main.gd")
    start = main.index("func _on_redemption_response")
    assert "_say_reply_voices(response)" in main[start:start + 4000]
    assert 'report.get("marshal_voice_by"' in main
    phase = _text("enemy_phase_dialog.gd")
    assert 'report.get("enemy_voice_by"' in phase and 'report.get("marshal_voice_by"' in phase
    assert phase.count("VoiceLine.bbcode(") >= 2
    card = _text("order_confirm_card.gd")
    assert 'VoiceLine.bbcode(str(r.get("marshal", "")), noted)' in card
    window = _text("redemption_dialog.gd")
    assert 'VoiceLine.plain_text(str(opt.get("speaker", "")), str(opt.get("says", "")))' in window
    renderer = main[main.index("func _render_own_result"):]
    renderer = renderer[:renderer.index("func _response_has_objection_route")]
    assert renderer.count("_say_reply_voices(response)") == 1


def test_the_battle_tableau_keeps_the_enemys_line_as_text():
    """Decided, not missed: the tableau's verdict plate has a fixed room and a
    recorded walk pins it (`tests/test_ba2_the_review.py`); the enemy's line
    stands there as text, and with his portrait in the enemy phase's report."""
    assert "VoiceLine" not in _text("battle_diorama.gd")
