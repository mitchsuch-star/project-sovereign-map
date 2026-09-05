"""Pre-build fixes (Aug 14, 2026) — the shippable-build P0/P1 gaps.

The Aug 14 whole-game health check ruled the project NOT yet at build
stage and named the gaps, all owned by ROADMAP position 10:

  1. launch.bat hard-required an Anthropic key — contradicting the
     mock-default v1 ruling (LLM_MONETIZATION_RESEARCH_2026_08_14.md:
     "Default = full game, offline, no AI").
  2. Cheats were armed in exactly the keyless-mock configuration a
     shipped build runs (meta_executor keyed on key_source != "none").
  3. Saves were CWD-relative — a frozen exe scattered them wherever it
     was launched from.
  4. README_TESTER.txt described the deleted 19-region game.
  5. No client-side backend supervision (launcher hoped 3s was enough).
  6. A stray 265MB movies.avi sat inside res://.

This file pins each fix. The .pck re-export itself stays position-10
work (it needs the Godot editor); build.bat's step text now demands it.

ENV HYGIENE: the dev .env sets DEBUG_MODE=true (and dotenv loads it via
LLMClient), so every refusal assertion here patches DEBUG_MODE
explicitly — never rely on the ambient environment for a closed-gate
pin.
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

from backend import save_manager
from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState

REPO_ROOT = Path(__file__).resolve().parent.parent
DEPLOY = REPO_ROOT / "deploy"
GODOT_PROJECT = REPO_ROOT / "godot-client" / "project-sovereign"


# ═══════════════════════════════════════════════════════════════════
# 1. The cheat gate: explicit debug only (build P0)
# ═══════════════════════════════════════════════════════════════════

class TestCheatGateExplicitDebug:
    """The shipped configuration is keyless mock — the old gate armed
    cheats there. The new gate opens ONLY on an affirmative debug switch."""

    def _executor_and_state(self, debug=None):
        world = WorldState(player_nation="France")
        gs = {"world": world}
        if debug is not None:
            gs["debug_mode"] = debug
        return CommandExecutor(), gs

    def _cheat(self, key_source=None):
        command = {"action": "cheat", "cheat_type": "set_threat",
                   "cheat_args": ["50"]}
        if key_source is not None:
            command["key_source"] = key_source
        return command

    def test_shipped_config_refuses_cheats(self):
        # THE build P0: keyless mock (key_source="none", mock env, no
        # debug) is what a tester runs. Cheats must be OFF there.
        executor, gs = self._executor_and_state()
        with patch.dict(os.environ, {"LLM_MODE": "mock", "DEBUG_MODE": "false"}):
            result = executor._execute_cheat(self._cheat("none"), gs)
        assert result["success"] is False
        assert "debug" in result["message"].lower()

    def test_shipped_config_refusal_mutates_nothing(self):
        executor, gs = self._executor_and_state()
        before = gs["world"].threat_level
        with patch.dict(os.environ, {"LLM_MODE": "mock", "DEBUG_MODE": "false"}):
            executor._execute_cheat(self._cheat("none"), gs)
        assert gs["world"].threat_level == before

    def test_game_state_debug_opens_gate(self):
        executor, gs = self._executor_and_state(debug=True)
        with patch.dict(os.environ, {"DEBUG_MODE": "false"}):
            result = executor._execute_cheat(self._cheat("none"), gs)
        assert result["success"] is True

    def test_env_debug_opens_gate_for_handbuilt_state(self):
        executor, gs = self._executor_and_state()
        with patch.dict(os.environ, {"DEBUG_MODE": "true"}):
            result = executor._execute_cheat(self._cheat(), gs)
        assert result["success"] is True

    def test_key_source_no_longer_opens_gate(self):
        # The retired CR-3(d) rule: key_source=="none" used to mean
        # "allowed". Every key_source value now refuses without debug.
        executor, gs = self._executor_and_state()
        with patch.dict(os.environ, {"LLM_MODE": "mock", "DEBUG_MODE": "false"}):
            for src in ("none", "byok", "inhouse"):
                result = executor._execute_cheat(self._cheat(src), gs)
                assert result["success"] is False, src

    def test_llm_mode_no_longer_opens_gate(self):
        # Neither mock nor anthropic env alone may arm the surface.
        executor, gs = self._executor_and_state()
        for mode in ("mock", "anthropic"):
            with patch.dict(os.environ, {"LLM_MODE": mode, "DEBUG_MODE": "false"}):
                result = executor._execute_cheat(self._cheat(), gs)
            assert result["success"] is False, mode

    def test_gate_source_is_not_key_source(self):
        # Structural pin: the gate must not READ key_source — the field
        # stays on the command (the parser still threads it) but the
        # decision consults only the debug switches. Pin the actual
        # read expression, not the word (the comment may explain it).
        import inspect
        from backend.commands import meta_executor
        src = inspect.getsource(meta_executor.MetaExecutor._execute_cheat)
        assert 'command.get("key_source")' not in src
        assert "command.get('key_source')" not in src


# ═══════════════════════════════════════════════════════════════════
# 2. Save directory: %APPDATA% when frozen, repo-relative in dev
# ═══════════════════════════════════════════════════════════════════

class TestSaveDirResolution:
    def test_dev_default_is_repo_relative(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("INK_IRON_SAVE_DIR", None)
            assert not getattr(sys, "frozen", False)
            assert save_manager._resolve_save_dir() == Path("saves")

    def test_env_override_wins_everywhere(self, tmp_path):
        target = str(tmp_path / "custom_saves")
        with patch.dict(os.environ, {"INK_IRON_SAVE_DIR": target}):
            assert save_manager._resolve_save_dir() == Path(target)
            # ...even frozen
            with patch.object(sys, "frozen", True, create=True):
                assert save_manager._resolve_save_dir() == Path(target)

    def test_frozen_build_uses_appdata(self, tmp_path):
        appdata = str(tmp_path / "AppData" / "Roaming")
        with patch.dict(os.environ, {"APPDATA": appdata}):
            os.environ.pop("INK_IRON_SAVE_DIR", None)
            with patch.object(sys, "frozen", True, create=True):
                resolved = save_manager._resolve_save_dir()
        assert resolved == Path(appdata) / "InkAndIron" / "saves"

    def test_frozen_without_appdata_falls_back_to_home(self):
        env = {k: v for k, v in os.environ.items()
               if k not in ("APPDATA", "INK_IRON_SAVE_DIR")}
        with patch.dict(os.environ, env, clear=True):
            with patch.object(sys, "frozen", True, create=True):
                resolved = save_manager._resolve_save_dir()
        assert resolved == Path.home() / ".ink_iron" / "saves"

    def test_ensure_save_dir_creates_nested_parents(self, tmp_path):
        # The APPDATA location is two levels deep on first run —
        # mkdir(parents=True) or the first save on a fresh PC crashes.
        nested = tmp_path / "Roaming" / "InkAndIron" / "saves"
        with patch("backend.save_manager.SAVE_DIR", nested):
            save_manager.ensure_save_dir()
        assert nested.is_dir()

    def test_module_save_dir_still_patchable(self, tmp_path):
        # The whole suite patches backend.save_manager.SAVE_DIR; the
        # resolver must not have moved the seam.
        world = WorldState(player_nation="France")
        with patch("backend.save_manager.SAVE_DIR", tmp_path):
            result = save_manager.save_game(world, "prebuild-pin")
        assert result["success"] is True
        assert list(tmp_path.glob("*.json"))


# ═══════════════════════════════════════════════════════════════════
# 3. The launcher: mock-default, key optional, honest supervision
# ═══════════════════════════════════════════════════════════════════

class TestLauncherMockDefault:
    def _text(self):
        return (DEPLOY / "launch.bat").read_text(encoding="utf-8")

    def test_mock_arm_exists(self):
        assert 'set "LLM_MODE=mock"' in self._text()

    def test_missing_config_no_longer_fatal(self):
        # The old launcher printed "[ERROR] config.txt not found!" and
        # exited — the exact contradiction of the mock-default DoD.
        text = self._text()
        assert "config.txt not found" not in text

    def test_placeholder_key_degrades_to_mock(self):
        # The placeholder guard must match the template's placeholder.
        text = self._text()
        assert 'if "!API_KEY!"=="your_key_here" set "API_KEY="' in text

    def test_template_placeholder_matches_guard(self):
        template = (DEPLOY / "dist_template" / "config.txt").read_text(
            encoding="utf-8")
        assert "ANTHROPIC_API_KEY=your_key_here" in template
        assert "OPTIONAL" in template  # framed optional, not required

    def test_health_poll_exists(self):
        # Supervision: poll GET /test until the server answers, with an
        # honest failure branch — not a fixed 3-second hope.
        text = self._text()
        assert "http://127.0.0.1:8005/test" in text
        assert "curl" in text
        assert "did not come up" in text

    def test_launcher_never_arms_debug(self):
        # Cheats key on DEBUG_MODE; the shipped launcher must never set it.
        assert "DEBUG_MODE" not in self._text()

    def test_key_arm_still_supported(self):
        # BYOK stays: a real key in config.txt switches to anthropic mode.
        text = self._text()
        assert 'set "LLM_MODE=anthropic"' in text
        assert 'set "ANTHROPIC_API_KEY=!API_KEY!"' in text


# ═══════════════════════════════════════════════════════════════════
# 4. README_TESTER: describes the game that ships
# ═══════════════════════════════════════════════════════════════════

class TestReadmeTesterCurrent:
    def _text(self):
        return (DEPLOY / "README_TESTER.txt").read_text(encoding="utf-8")

    def test_no_key_required_is_the_lead(self):
        text = self._text()
        assert "No account, no key" in text

    def test_stale_19_region_world_is_gone(self):
        text = self._text()
        # Legacy-roster markers of the deleted world: Drouot was the
        # legacy artillery marshal; "8 of 19 regions" was its map.
        assert "Drouot" not in text
        assert "19 regions" not in text
        assert "8 of 19" not in text
        # Grouchy is a commission-bench name now, not a starting marshal.
        assert "GROUCHY (" not in text

    def test_current_roster_present(self):
        text = self._text()
        for name in ("NEY", "DAVOUT", "SOULT", "LANNES", "MURAT",
                     "BERNADOTTE", "MASSENA"):
            assert name in text, name

    def test_hotkeys_match_main_gd(self):
        # The old README taught D = dispatch; D is the diplomatic ledger
        # and R is the dispatch since Session A. N = the Gazette (HC-G).
        #
        # FA-N56 (slice 13) re-pointed these three off their exact
        # column spacing: the README now advertises the Alt form
        # beside each bare key, because the bare key is dead in the
        # state the client puts itself in. The mapping is what this
        # test was ever about, so it asserts the mapping.
        # The slice-12 review round measured the first amendment to be
        # WEAKER than the exact-column pin it replaced: it asserted the
        # keys and the screens existed SOMEWHERE, so a README that
        # swapped two mappings stayed green. It pins the MAPPING now —
        # the key, its Alt form, and the screen on the same line.
        text = self._text()
        for key, screen in (("R", "Morning Dispatch"),
                            ("D", "Diplomatic Ledger"),
                            ("N", "Le Moniteur"),
                            ("T", "Strategic Ledger"),
                            ("G", "Generals"),
                            ("L", "Campaign Log")):
            row = "%s / Alt+%s" % (key, key)
            line = next((ln for ln in text.splitlines()
                         if ln.strip().startswith(row)), None)
            assert line is not None, (
                "%s must be advertised in its focus-safe form" % key)
            assert screen in line, (
                "%s must still name %s, not %r" % (key, screen, line))

    def test_appdata_saves_documented(self):
        assert r"%APPDATA%\InkAndIron\saves" in self._text()

    def test_smarter_parsing_framing(self):
        # The monetization ruling's language discipline: optional,
        # cost-honest, never framed as a requirement.
        text = self._text()
        assert "SMARTER PARSING (OPTIONAL)" in text
        assert "billed by" in text


# ═══════════════════════════════════════════════════════════════════
# 5. res:// hygiene: no stray video payloads in the Godot project
# ═══════════════════════════════════════════════════════════════════

class TestResourceHygiene:
    def test_no_avi_inside_res(self):
        # A 265MB movies.avi lived in assets/ — anything like it bloats
        # the export and slows every editor import scan.
        stray = [p for p in GODOT_PROJECT.rglob("*.avi")]
        assert stray == [], f"video files inside res://: {stray}"

    def test_build_bat_demands_fresh_export_and_mock_smoke(self):
        text = (DEPLOY / "build.bat").read_text(encoding="utf-8")
        assert "FRESH export" in text
        assert "mock mode" in text
