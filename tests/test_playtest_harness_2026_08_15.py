"""The playtest harness (Aug 15, 2026 "make the test easier" session).

Pins the three levers the session landed, so future refactors cannot
silently break the documented playtest path:

  1. The port override — SOVEREIGN_PORT moves BOTH sides (backend
     __main__ + Utils.backend_url()), and no .gd hardcodes the origin.
  2. The driver — tools/playtest_driver.py runs a short campaign
     end-to-end as a subprocess and produces the digest contract
     (digest.md / digest.jsonl / meta.json).
  3. The fixtures — committed mid-campaign saves load-viable at v3.

Documentation contract: docs/PLAYTESTING.md is the doc of record and
CLAUDE.md's Document Map must keep pointing at it — "document somewhere
clear how future sessions can playtest" was the user's ask; the pointer
IS the deliverable.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "godot-client" / "project-sovereign" / "scripts"
SCENES_DIR = REPO_ROOT / "godot-client" / "project-sovereign" / "scenes"
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "playtest_saves"


def _read(path):
    return path.read_text(encoding="utf-8", errors="replace")


# ═══════════════════════════════════════════════════════════════════
# 1. SOVEREIGN_PORT — one origin, both sides
# ═══════════════════════════════════════════════════════════════════

class TestPortOverride:
    def test_backend_reads_sovereign_port(self):
        source = _read(REPO_ROOT / "backend" / "main.py")
        assert 'os.getenv("SOVEREIGN_PORT", "8005")' in source

    def test_utils_is_the_client_single_source(self):
        source = _read(SCRIPTS_DIR / "utils.gd")
        assert "static func backend_url()" in source
        assert 'OS.get_environment("SOVEREIGN_PORT")' in source
        assert '"8005"' in source  # the default lives here and only here

    def test_no_gd_hardcodes_the_origin_outside_utils(self):
        # Golden Rule 7 (amended Aug 15, 2026): every script derives from
        # Utils.backend_url(). A new hardcode reintroduces the port-
        # collision class the CA9 audit had to skip its visual half for.
        offenders = []
        for directory in (SCRIPTS_DIR, SCENES_DIR):
            for path in directory.glob("*.gd"):
                if path.name == "utils.gd":
                    continue
                if "http://127.0.0.1:" in _read(path):
                    offenders.append(path.name)
        assert offenders == [], f"hardcoded backend origin in: {offenders}"

    def test_consumer_sites_derive_from_utils(self):
        for name in ("api_client.gd", "diplomacy_wizard.gd",
                     "main_menu.gd", "settings_panel.gd"):
            source = _read(SCRIPTS_DIR / name)
            assert "Utils.backend_url()" in source, name


# ═══════════════════════════════════════════════════════════════════
# 2. The driver — an end-to-end subprocess campaign
# ═══════════════════════════════════════════════════════════════════

class TestPlaytestDriver:
    def test_driver_import_is_side_effect_free(self):
        # Importing the module must not import the backend (the backend
        # boots a world at import; the driver defers it so env prep can
        # run first). Subprocess so the suite's own modules don't mask it.
        code = (
            "import importlib.util, sys; "
            "spec = importlib.util.spec_from_file_location("
            "'playtest_driver', r'%s'); "
            "m = importlib.util.module_from_spec(spec); "
            "spec.loader.exec_module(m); "
            "assert 'backend.main' not in sys.modules, 'backend imported'; "
            "print('CLEAN')"
        ) % (REPO_ROOT / "tools" / "playtest_driver.py")
        result = subprocess.run([sys.executable, "-c", code],
                                capture_output=True, text=True,
                                cwd=REPO_ROOT, timeout=120)
        assert result.returncode == 0, result.stderr
        assert "CLEAN" in result.stdout

    def test_two_turn_ambient_run_produces_the_digest_contract(self, tmp_path):
        # The real thing: a 2-turn seeded mock campaign through
        # /new_game + /command, popups answered, digest written.
        env = dict(os.environ)
        env.pop("PYTHONIOENCODING", None)  # standing rule: never set it
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "playtest_driver.py"),
             "--turns", "2", "--name", "suite-smoke", "--fresh",
             "--out", str(tmp_path)],
            capture_output=True, text=True, cwd=REPO_ROOT,
            env=env, timeout=420,
        )
        assert result.returncode == 0, (result.stdout or "") + (result.stderr or "")

        run_dir = tmp_path / "suite-smoke"
        digest = _read(run_dir / "digest.md")
        assert digest.count("## Turn") == 2
        assert "end turn" in digest

        meta = json.loads(_read(run_dir / "meta.json"))
        assert meta["status"] == "completed"
        assert meta["counters"]["turns"] == 2
        assert meta["unknown_blockers"] == []

        records = [json.loads(line) for line in
                   _read(run_dir / "digest.jsonl").splitlines() if line]
        kinds = {record["kind"] for record in records}
        assert {"turn", "command", "ledger"} <= kinds

        # The sandbox held: the run's saves live in the run dir, and the
        # repo-level saves/ was not touched by this subprocess (the
        # driver sets INK_IRON_SAVE_DIR before backend import).
        assert (run_dir / "saves" / "autosave.json").exists()

    def test_driver_never_defaults_to_live_llm(self):
        # The dev .env says LLM_MODE=anthropic; an unattended playtest
        # spending real tokens by DEFAULT would be a footgun. mock is
        # forced unless --llm anthropic is explicit.
        source = _read(REPO_ROOT / "tools" / "playtest_driver.py")
        assert '"--llm", default="mock"' in source.replace("'", '"')


# ═══════════════════════════════════════════════════════════════════
# 3. Fixtures — committed mid-campaign starts
# ═══════════════════════════════════════════════════════════════════

class TestFixtureSaves:
    def test_fixtures_exist_and_are_v3(self):
        for name, turn in (("fixture_t10_ambient.json", 10),
                           ("fixture_t20_ambient.json", 20)):
            path = FIXTURE_DIR / name
            assert path.exists(), f"{name} missing — run tools/gen_playtest_fixtures.py"
            payload = json.loads(_read(path))
            assert payload["metadata"]["format_version"] == 3, name
            assert payload["metadata"]["turn"] == turn, name
            assert "world_state" in payload, name

    def test_fixtures_are_not_swallowed_by_the_saves_gitignore(self):
        # .gitignore has a bare `saves/` pattern (matches ANY dir named
        # saves at any level) — the fixture dir dodges it by name. If
        # someone renames it to .../saves/, the fixtures silently stop
        # being tracked and regen "commits" vanish.
        assert FIXTURE_DIR.name != "saves"
        tracked = subprocess.run(
            ["git", "check-ignore", str(FIXTURE_DIR / "fixture_t10_ambient.json")],
            capture_output=True, text=True, cwd=REPO_ROOT, timeout=60)
        assert tracked.returncode != 0, "fixtures are gitignored!"


# ═══════════════════════════════════════════════════════════════════
# 4. The documentation contract
# ═══════════════════════════════════════════════════════════════════

class TestDocumentationContract:
    def test_playtesting_doc_exists_and_names_the_pieces(self):
        doc = _read(REPO_ROOT / "docs" / "PLAYTESTING.md")
        for needle in ("playtest_driver.py", "gen_playtest_fixtures.py",
                       "fixture_t10_ambient.json", "SOVEREIGN_PORT",
                       "digest.md", "--from-save"):
            assert needle in doc, needle

    def test_claude_md_points_at_the_doc(self):
        claude = _read(REPO_ROOT / "CLAUDE.md")
        assert "PLAYTESTING.md" in claude
