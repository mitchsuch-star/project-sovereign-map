"""Voice-to-Text v1 (Road to EA position 8) — OS dictation as the supported path.

The approach gate (Aug 8, 2026, user-delegated: "what works best for steam or
itch release" / "use best decision") ruled option (a): Windows voice typing
(Win+H) into the command line, verified live, with embedded STT (whisper.cpp)
deferred behind a named re-open condition (Round-0 tester usage / store-page
need). Cloud STT is out — a second vendor key breaks the single-key BYOK design.

What this file pins:

1. The Settings surface carries the SPOKEN ORDERS hint (the discoverability
   half of the slice — dictation that nobody can find does not exist).
2. The hint names the review-then-send flow: dictation FILLS the command line
   and the player sends with Enter. Nothing auto-submits (the PARSE-NEG
   lesson: a misheard negation must never execute on its own).
3. GR6 stands structurally: the voice section is display-only — no HTTP, no
   parse call, no new input path. Dictation is Windows typing into the same
   LineEdit; the deterministic parser never learns the text was spoken.
4. README_TESTER.txt carries the tester-facing line (the build row inherits
   this file as its regeneration source).
5. GR9: the deferred embedded-STT work has a HOME — ROADMAP row 8 must keep
   naming whisper.cpp behind its re-open condition.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "godot-client" / "project-sovereign" / "scripts"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestSpokenOrdersSettingsHint:
    def test_settings_panel_builds_voice_section(self):
        panel = _read(SCRIPTS / "settings_panel.gd")
        assert "_build_voice_section()" in panel, "voice section not wired into _ready"
        assert '"SPOKEN ORDERS"' in panel

    def test_hint_names_win_h_and_the_command_line(self):
        panel = _read(SCRIPTS / "settings_panel.gd")
        assert "Win+H" in panel
        assert "command " in panel.lower()

    def test_hint_is_review_then_send_never_auto_submit(self):
        """PARSE-NEG discipline: dictated text is reviewed and sent with Enter."""
        panel = _read(SCRIPTS / "settings_panel.gd")
        body = self._voice_section_body(panel)
        assert "review" in body and "Enter" in body

    def test_voice_section_is_display_only(self):
        """GR6 structural pin: the section may only add a header and hint labels.

        If someone later routes audio, HTTP, or a parse call through this
        section, this test is the tripwire that says 'that is the (b) slice —
        re-open the gate, do not bolt it onto the hint.'
        """
        panel = _read(SCRIPTS / "settings_panel.gd")
        body = self._voice_section_body(panel)
        assert "http" not in body.lower()
        assert "request(" not in body
        allowed = re.findall(r"_add_(?:header|hint)\(", body)
        calls = re.findall(r"(?<!func )\b\w+\(", body)
        # Every call in the section body is _add_header/_add_hint (String
        # concatenation aside, which produces no call tokens).
        disallowed = [c for c in calls if c not in ("_add_header(", "_add_hint(")]
        assert not disallowed, f"voice section grew non-display calls: {disallowed}"
        assert len(allowed) >= 2

    @staticmethod
    def _voice_section_body(panel: str) -> str:
        m = re.search(
            r"func _build_voice_section\(\) -> void:\n(.*?)\n\n\n", panel, re.DOTALL
        )
        assert m, "_build_voice_section not found"
        return m.group(1)


class TestTesterReadmeLine:
    def test_readme_tester_carries_the_dictation_block(self):
        readme = _read(REPO_ROOT / "deploy" / "README_TESTER.txt")
        assert "SPEAK COMMANDS" in readme
        assert "Win+H" in readme
        assert "press Enter to send" in readme


class TestDeferredWorkHasAHome:
    def test_roadmap_row8_names_the_embedded_stt_reopen_condition(self):
        """GR9: (b) whisper.cpp is DEFERRED, not dropped — the row must keep
        naming the trigger that re-opens it."""
        roadmap = _read(REPO_ROOT / "docs" / "ROADMAP.md")
        assert "whisper.cpp" in roadmap
        row = roadmap[roadmap.index("VOICE-TO-TEXT") :][:4000]
        assert "re-open" in row.lower()
        assert "Round-0" in row or "Round 0" in row
