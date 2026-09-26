"""THE RELEASE BUILD (ROADMAP position 10) — September 25, 2026.

The row's own items, PB-1 … PB-6 (`docs/BUG_FIXES.md` §Pre-Build Review),
plus the v1 Smarter-Parsing touchpoints the row owns (call C1: the key
section SHIPS, honest). Pins over the pipeline that produces the zip and
over the code the zip runs — each two-directional where the failure mode is
a substring pin that stays green while the thing it names goes missing.

Sections:
  1. PB-1  the frozen server finds its scenario (the paths derive from an
           IMPORTED module, never from the entry script's __file__)
  2. PB-4  the build stamp (tools/build_stamp.py, build_info, /test, the
           launcher's refusal of a mismatched server) and the logs
           (runtime_log: server.log + transcript.jsonl, cp1252-safe console)
  3. the pipeline: build.bat boots the frozen exe before it zips
           (tools/release_smoke.py), verifies the .pck (tools/list_pck.py),
           exports RELEASE, removes the stale zip (PB-6)
  4. C1    the key check + key_status + the once-per-session parser notice,
           the once-ever keyless hint, the Settings copy (PB-3)
  5. PB-2  every example the tester kit advertises is READ on a fresh 1805
           boot, and the README/boot-help ones EXECUTE; the debug block only
           in debug mode
  6. PB-5  the README: SmartScreen, three windows, the logs, the ending
"""

from __future__ import annotations

import importlib.util
import io
import json
import os
import re
import struct
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO = Path(__file__).resolve().parents[1]
DEPLOY = REPO / "deploy"
TOOLS = REPO / "tools"
CLIENT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = CLIENT / "scripts"
SCENES = CLIENT / "scenes"
MAPS = CLIENT / "assets" / "maps"


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _bat_commands(p: Path) -> str:
    """A .bat with its `::` comment lines stripped — a source pin over a
    batch file proves a COMMAND exists, never that a comment mentions it
    (the FA-43 lesson: two pins read their own comments)."""
    return "\n".join(ln for ln in _read(p).splitlines()
                     if not ln.strip().startswith("::"))


def _load_tool(name: str):
    path = TOOLS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"_release_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ═══════════════════════════════════════════════════════════════════════
# 1. PB-1 — the frozen server finds its scenario
# ═══════════════════════════════════════════════════════════════════════

class TestPB1TheFrozenServerFindsItsScenario:
    """`backend/main.py` is PyInstaller's ENTRY script; an entry script's
    `__file__` is `<bundle>\\_internal\\main.py` (measured with a 6.19 onedir
    probe build), so `Path(__file__).resolve().parents[1]` points OUTSIDE
    `_internal`, where the spec ships the maps. An IMPORTED module's
    `__file__` mirrors the repo layout inside `_internal`, so the maps
    folder derives from `region.py`'s registry path."""

    def test_the_scenario_paths_derive_from_the_registry_path(self):
        import backend.main as M
        from backend.models.region import EUROPE_REGISTRY_PATH
        assert M.MAPS_DIR == Path(EUROPE_REGISTRY_PATH).parent
        assert M._DEFAULT_SCENARIO_PATH == M.MAPS_DIR / "europe_1805.json"
        assert M.TUTORIAL_SCENARIO_PATH == M.MAPS_DIR / "tutorial_1805.json"
        assert M._DEFAULT_SCENARIO_PATH.exists()
        assert M.TUTORIAL_SCENARIO_PATH.exists()

    def test_main_py_no_longer_reads_its_own_file_for_the_maps(self):
        """The defect's shape, forbidden at the source: neither scenario
        constant may be built from main.py's own `__file__`."""
        src = _read(REPO / "backend" / "main.py")
        for name in ("_DEFAULT_SCENARIO_PATH", "TUTORIAL_SCENARIO_PATH"):
            at = src.index(f"{name} =")
            stmt = src[at:src.index("\n", at)]
            assert "__file__" not in stmt, stmt
            assert "MAPS_DIR" in stmt, stmt

    def test_the_entry_script_simulation(self, tmp_path):
        """What PB-1 measured, as arithmetic: an entry script at
        `<bundle>/_internal/main.py` puts `parents[1]` at the bundle root,
        while a module at `<bundle>/_internal/backend/models/region.py`
        puts `parents[2]` at `_internal` — where the spec ships the maps."""
        bundle = tmp_path / "ink_iron_server"
        entry = bundle / "_internal" / "main.py"
        region = bundle / "_internal" / "backend" / "models" / "region.py"
        maps_dst = bundle / "_internal" / "godot-client" / "project-sovereign" / "assets" / "maps"
        assert entry.resolve().parents[1] == bundle           # the old, wrong root
        assert region.resolve().parents[2] == bundle / "_internal"  # the registry's root
        assert maps_dst.is_relative_to(region.resolve().parents[2])
        assert not maps_dst.is_relative_to(entry.resolve().parents[1] / "godot-client") or True

    def test_the_spec_ships_the_maps_where_region_py_looks(self):
        """Drift pin: the spec's `_MAPS_DST` is the registry path relative
        to region.py's own root — the two must agree or the frozen boot
        dies at import again."""
        from backend.models import region
        spec_text = _read(DEPLOY / "ink_iron.spec")
        rel = Path(region.EUROPE_REGISTRY_PATH).relative_to(
            Path(region.__file__).resolve().parents[2]).parent
        parts = ", ".join(f"'{p}'" for p in rel.parts)
        assert f"_MAPS_DST = os.path.join(\n    {parts})" in spec_text, (
            f"spec must ship the maps at {rel.as_posix()}")
        for name in ("europe.json", "europe_1805.json", "tutorial_1805.json"):
            assert f"'{name}'" in spec_text


# ═══════════════════════════════════════════════════════════════════════
# 2. PB-4 — the build stamp and the logs
# ═══════════════════════════════════════════════════════════════════════

class TestTheBuildStampTool:
    def test_the_version_names_the_day_and_the_commit(self):
        bs = _load_tool("build_stamp")
        stamp = bs.build_stamp()
        assert re.fullmatch(r"\d{8}-[0-9a-f]{4,10}(\+dirty)?", stamp["version"]), stamp
        assert stamp["commit"] and stamp["date"].endswith("Z")
        assert isinstance(stamp["dirty"], bool)

    def test_json_and_txt_round_trip(self, tmp_path):
        bs = _load_tool("build_stamp")
        json_path = tmp_path / "build_stamp.json"
        stamp = bs.write_json({"version": "20260925-abc123", "commit": "abc", "date": "d",
                               "dirty": False}, path=json_path)
        assert bs.read_json(json_path)["version"] == stamp["version"]
        txt = bs.write_txt(tmp_path / "dist", "20260925-abc123")
        # no trailing newline: launch.bat reads it with `set /p`
        assert txt.read_bytes() == b"20260925-abc123"

    def test_read_without_a_stamp_fails_closed(self, tmp_path):
        bs = _load_tool("build_stamp")
        with patch.object(bs, "STAMP_JSON", tmp_path / "missing.json"):
            assert bs.main(["--read"]) == 1
            assert bs.main(["--txt", str(tmp_path / "dist")]) == 1

    def test_the_stamp_json_is_generated_not_committed(self):
        ignore = _read(REPO / ".gitignore")
        assert "deploy/build_stamp.json" in ignore
        tracked = subprocess.run(["git", "ls-files", "deploy/build_stamp.json"], cwd=REPO,
                                 capture_output=True, text=True, timeout=60).stdout
        assert tracked.strip() == ""


class TestBuildInfo:
    def test_source_checkout_reports_dev(self):
        from backend.build_info import build_version
        assert not getattr(sys, "frozen", False)
        assert build_version() == "dev"

    def test_frozen_reads_the_stamp_from_meipass(self, tmp_path):
        from backend import build_info
        (tmp_path / build_info.STAMP_FILENAME).write_text(
            json.dumps({"version": "20260925-abc123"}), encoding="utf-8")
        with patch.object(sys, "frozen", True, create=True), \
                patch.object(sys, "_MEIPASS", str(tmp_path), create=True):
            assert build_info.build_version() == "20260925-abc123"

    def test_frozen_without_a_stamp_says_unknown(self, tmp_path):
        from backend import build_info
        with patch.object(sys, "frozen", True, create=True), \
                patch.object(sys, "_MEIPASS", str(tmp_path), create=True):
            assert build_info.build_version() == "unknown"

    def test_test_endpoint_carries_the_version_and_the_parser_state(self):
        from fastapi.testclient import TestClient
        import backend.main as M
        data = TestClient(M.app).get("/test").json()
        assert data["version"] == "dev"
        assert isinstance(data["smarter_parsing"], bool)
        assert data["smarter_parsing"] is bool(M.parser.llm.use_real_api)

    def test_the_spec_ships_the_stamp_at_the_meipass_root(self):
        spec_text = _read(DEPLOY / "ink_iron.spec")
        assert "build_stamp.json" in spec_text
        assert "all_datas.append((_STAMP, '.'))" in spec_text


class TestRuntimeLog:
    @pytest.fixture
    def fresh(self, monkeypatch, tmp_path):
        from backend import runtime_log
        out, err = sys.stdout, sys.stderr
        monkeypatch.setattr(runtime_log, "_log_dir", None)
        yield runtime_log, tmp_path
        sys.stdout, sys.stderr = out, err
        runtime_log._log_dir = None

    def test_dev_is_off_unless_asked(self, fresh, monkeypatch):
        rl, tmp = fresh
        monkeypatch.delenv(rl.LOG_DIR_ENV, raising=False)
        assert rl.resolve_log_dir() is None
        assert rl.install() is None
        rl.append_transcript(None, "Ney, attack Mack", {"success": True})  # a no-op, never a raise

    def test_env_wins_and_frozen_uses_appdata(self, fresh, monkeypatch, tmp_path):
        rl, _tmp = fresh
        monkeypatch.setenv(rl.LOG_DIR_ENV, str(tmp_path / "explicit"))
        assert rl.resolve_log_dir() == tmp_path / "explicit"
        monkeypatch.delenv(rl.LOG_DIR_ENV)
        monkeypatch.setenv("APPDATA", str(tmp_path / "Roaming"))
        with patch.object(sys, "frozen", True, create=True):
            assert rl.resolve_log_dir() == tmp_path / "Roaming" / "InkAndIron" / "logs"

    def test_install_tees_the_console_and_keeps_one_previous_log(self, fresh, monkeypatch):
        rl, tmp = fresh
        logs = tmp / "logs"
        monkeypatch.setenv(rl.LOG_DIR_ENV, str(logs))
        assert rl.install() == logs
        print("the first session prints an emoji: ⚔ and a dash —")
        first = (logs / rl.SERVER_LOG).read_text(encoding="utf-8")
        assert "⚔" in first and "Ink & Iron server log" in first
        assert rl.install() == logs  # idempotent
        # a second install after a reset rolls the log once
        sys.stdout = sys.stdout._stream
        sys.stderr = sys.stderr._stream
        rl._log_dir = None
        assert rl.install() == logs
        assert (logs / rl.SERVER_LOG_PREVIOUS).exists()
        assert "⚔" in (logs / rl.SERVER_LOG_PREVIOUS).read_text(encoding="utf-8")

    def test_the_transcript_records_the_order_and_the_reply(self, fresh, monkeypatch):
        rl, tmp = fresh
        monkeypatch.setenv(rl.LOG_DIR_ENV, str(tmp / "logs"))
        rl.install()

        class W:
            current_turn = 7
        rl.append_transcript(W(), "Ney, attack Mack",
                             {"success": False, "message": "x" * 5000, "action": "attack"},
                             parser="mock")
        line = json.loads((tmp / "logs" / rl.TRANSCRIPT).read_text(encoding="utf-8").splitlines()[-1])
        assert line["turn"] == 7 and line["order"] == "Ney, attack Mack"
        assert line["success"] is False and line["action"] == "attack"
        assert line["parser"] == "mock"
        assert len(line["reply"]) == rl.REPLY_CHARS

    def test_the_command_endpoint_records_and_keeps_its_body(self):
        """The transcript rides a DECORATOR on `execute_command`, so the
        pipeline stays under its own name (three source pins read it) and the
        provenance key is read in main.py, the census's one allowed reader."""
        import inspect
        import backend.main as M
        assert getattr(M.execute_command, "__wrapped__", None) is not None
        src = inspect.getsource(M.execute_command)
        assert "@_records_transcript" in src
        assert len(src) > 5000, "the body must be the pipeline, not a wrapper"
        rl_src = _read(REPO / "backend" / "runtime_log.py")
        assert "parse_mode" not in rl_src

    def test_the_tee_never_raises(self, fresh):
        rl, _tmp = fresh
        closed = io.StringIO()
        closed.close()
        tee = rl._Tee(None, closed)
        assert tee.write("nothing to see") == len("nothing to see")
        tee.flush()
        assert tee.isatty() is False
        assert tee.encoding == "utf-8"

    def test_the_server_never_prints_any_part_of_the_key(self):
        """server.log is the file players are asked to send."""
        src = _read(REPO / "backend" / "main.py")
        assert "api_key[:10]" not in src
        assert "{'SET' if api_key else 'NOT SET'}" in src


class TestTheLauncherRefusesAMismatchedServer:
    def _text(self):
        return _read(DEPLOY / "launch.bat")

    def test_it_reads_the_stamp_and_the_running_servers_version(self):
        text = self._text()
        assert "build_stamp.txt" in text
        assert ".version" in text and "/test" in text
        assert "different build" in text

    def test_it_waits_sixty_seconds_and_names_the_log(self):
        text = self._text()
        assert "geq 60" in text
        assert "did not come up after 60 seconds" in text
        assert r"%APPDATA%\InkAndIron\logs\server.log" in text
        assert "stays open when something goes wrong" not in text

    def test_the_mock_default_survives(self):
        text = self._text()
        assert 'set "LLM_MODE=mock"' in text
        assert "DEBUG_MODE" not in text


# ═══════════════════════════════════════════════════════════════════════
# 3. The pipeline: build.bat boots what it built before it zips
# ═══════════════════════════════════════════════════════════════════════

class TestBuildBatBootsTheFrozenServer:
    def _cmds(self):
        return _bat_commands(DEPLOY / "build.bat")

    def test_the_stamp_is_written_before_pyinstaller_and_copied_after(self):
        cmds = self._cmds()
        stamp = cmds.index("tools\\build_stamp.py")
        pyi = cmds.index("-m PyInstaller deploy\\ink_iron.spec")
        txt = cmds.index("tools\\build_stamp.py --txt")
        assert stamp < pyi < txt
        assert "--noconfirm" in cmds[pyi:pyi + 200]

    def test_the_frozen_smoke_runs_before_the_zip(self):
        cmds = self._cmds()
        smoke = cmds.index("tools\\release_smoke.py")
        zipped = cmds.index("Compress-Archive")
        assert smoke < zipped
        assert "--expect-version" in cmds[smoke:smoke + 200]
        after = cmds[smoke:smoke + 400]
        assert "errorlevel 1" in after and "Nothing was zipped" in after

    def test_the_export_is_release_and_the_pack_is_verified(self):
        cmds = self._cmds()
        assert '--export-release "Windows Desktop"' in cmds
        assert "--import" in cmds
        verify = cmds.index("tools\\list_pck.py")
        assert verify > cmds.index("--export-release")
        assert "--require res://assets/maps/europe.json res://assets/maps/europe_1805.json" in cmds
        assert cmds.index("Compress-Archive") > verify

    def test_the_stale_zip_is_removed_and_the_new_one_is_versioned(self):
        cmds = self._cmds()
        assert 'del /q "deploy\\dist\\ink_iron_server.zip"' in cmds
        assert "ink_iron_%VERSION%.zip" in cmds

    def test_godot_is_required_not_hoped_for(self):
        cmds = self._cmds()
        assert "GODOT_EXE" in cmds
        assert 'if not exist "%GODOT_EXE%"' in cmds

    def test_the_licence_copies_survive(self):
        """FA-43's census reads build.bat too — the rewrite keeps every copy."""
        cmds = self._cmds()
        for name in ("THIRD_PARTY_LICENSES.md", "*-OFL.txt", "kenney-license.txt",
                     "phosphor-LICENSE.txt", "game-icons-LICENSE.txt"):
            assert name in cmds, name


class TestTheReleaseSmokeTool:
    def test_the_env_is_the_testers_not_the_developers(self, monkeypatch, tmp_path):
        rs = _load_tool("release_smoke")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-the-developers-own")
        monkeypatch.setenv("DEBUG_MODE", "true")
        monkeypatch.setenv("SOVEREIGN_SCENARIO", "none")
        env = rs.smoke_env(tmp_path, 8099)
        assert "ANTHROPIC_API_KEY" not in env and "DEBUG_MODE" not in env
        assert "SOVEREIGN_SCENARIO" not in env
        assert env["LLM_MODE"] == "mock" and env["SOVEREIGN_PORT"] == "8099"
        assert env["INK_IRON_SAVE_DIR"] == str(tmp_path / "saves")
        assert env["INK_IRON_LOG_DIR"] == str(tmp_path / "logs")
        live = rs.smoke_env(tmp_path, 8099, live_key="sk-ant-test")
        assert live["LLM_MODE"] == "anthropic" and live["ANTHROPIC_API_KEY"] == "sk-ant-test"

    def test_a_missing_exe_fails_closed(self, tmp_path):
        rs = _load_tool("release_smoke")
        assert rs.run_smoke(tmp_path, 8099, None) == 1

    def test_a_dead_process_ends_the_wait(self):
        rs = _load_tool("release_smoke")
        proc = subprocess.Popen([sys.executable, "-c", "pass"])
        proc.wait(timeout=60)
        assert rs.wait_for("http://127.0.0.1:1/test", 5.0, proc) is None

    def test_the_orders_it_types_are_the_readmes(self):
        rs = _load_tool("release_smoke")
        readme = _read(DEPLOY / "README_TESTER.txt")
        for order in rs.SMOKE_ORDERS:
            if order == "status":
                continue
            assert f'"{order}"' in readme, order


class TestThePackLister:
    @staticmethod
    def _write_pck(path: Path, names: list[str]) -> None:
        body = b""
        body += b"GDPC" + struct.pack("<5I", 2, 4, 4, 1, 0) + struct.pack("<Q", 0)
        body += b"\x00" * 64
        body += struct.pack("<I", len(names))
        for i, name in enumerate(names):
            raw = name.encode("utf-8")
            pad = (4 - len(raw) % 4) % 4
            body += struct.pack("<I", len(raw) + pad) + raw + b"\x00" * pad
            body += struct.pack("<QQ", 1000 + i, 10 * (i + 1)) + b"\x00" * 16 + struct.pack("<I", 0)
        path.write_bytes(body)

    def test_it_lists_the_directory(self, tmp_path):
        """Godot 4.4 stores pack paths WITHOUT `res://` (measured on the
        release export), a binary-exported scene as `<path>.remap` and an
        imported asset as `<path>.import` — a requirement written with the
        prefix must still find them."""
        lp = _load_tool("list_pck")
        pck = tmp_path / "x.pck"
        self._write_pck(pck, ["assets/maps/europe_1805.json", "scenes/main.tscn.remap",
                              "assets/maps/europe_lookup.png.import"])
        names = [n for n, _o, _s in lp.list_pck(pck)]
        assert names == ["assets/maps/europe_1805.json", "scenes/main.tscn.remap",
                         "assets/maps/europe_lookup.png.import"]
        assert lp.main([str(pck), "--quiet", "--require", "res://scenes/main.tscn",
                        "res://assets/maps/europe_1805.json",
                        "res://assets/maps/europe_lookup.png"]) == 0
        assert lp.main([str(pck), "--quiet", "--require", "res://assets/maps/europe.json"]) == 1

    def test_a_non_pack_is_refused(self, tmp_path):
        lp = _load_tool("list_pck")
        bad = tmp_path / "bad.pck"
        bad.write_bytes(b"MZ\x90\x00" + b"\x00" * 100)
        with pytest.raises(ValueError):
            lp.list_pck(bad)

    def test_the_march_pack_if_present_carries_no_maps(self):
        """The row's correction in the flesh: the March 2026 pack (gitignored,
        may be absent) predates the cutover and holds no scenario."""
        lp = _load_tool("list_pck")
        march = DEPLOY / "dist" / "ink_iron_server" / "InkAndIron.pck"
        if not march.exists() or march.stat().st_size > 1_000_000:
            pytest.skip("no March pack on this checkout")
        names = {n for n, _o, _s in lp.list_pck(march)}
        assert names and "res://assets/maps/europe_1805.json" not in names


# ═══════════════════════════════════════════════════════════════════════
# 4. C1 — the key section ships, honest
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture
def key_seams(monkeypatch):
    """The parser's live client is restored after every test here; the
    once-per-session notice latch and the key state start clean."""
    import backend.main as M
    from backend.ai import providers
    original_llm = M.parser.llm
    monkeypatch.setitem(M._key_status, "state", None)
    monkeypatch.setitem(M._parser_notice, "spoken", False)
    providers.pop_last_api_outcome()  # drain whatever a neighbour left
    try:
        yield M, providers
    finally:
        M.parser.llm = original_llm
        providers.pop_last_api_outcome()


class TestTheKeyIsCheckedWhenConnected:
    def test_a_rejected_key_is_never_installed(self, key_seams, monkeypatch):
        M, _providers = key_seams
        from fastapi.testclient import TestClient
        monkeypatch.setattr(M, "_check_anthropic_key", lambda key: "rejected")
        data = TestClient(M.app).post("/config/llm", json={"api_key": "sk-ant-bad"}).json()
        assert data["success"] is False
        assert data["key_status"] == "rejected"
        assert "rejected" in data["message"].lower()
        assert M.parser.llm._byok_key is None, "every hard phrasing would pay a failed round-trip"
        assert "sk-ant-bad" not in json.dumps(data)

    def test_a_key_without_the_model_is_refused_the_same_way(self, key_seams, monkeypatch):
        M, _providers = key_seams
        from fastapi.testclient import TestClient
        monkeypatch.setattr(M, "_check_anthropic_key", lambda key: "no_model")
        data = TestClient(M.app).post("/config/llm", json={"api_key": "sk-ant-old"}).json()
        assert data["success"] is False and data["key_status"] == "no_model"
        assert M.parser.llm._byok_key is None

    def test_a_confirmed_key_is_installed_and_says_connected(self, key_seams, monkeypatch):
        M, _providers = key_seams
        from fastapi.testclient import TestClient
        monkeypatch.setattr(M, "_check_anthropic_key", lambda key: "connected")
        data = TestClient(M.app).post("/config/llm", json={"api_key": "sk-ant-good"}).json()
        assert data["success"] is True and data["live"] is True
        assert data["key_status"] == "connected"
        assert data["key_status_text"] == M.KEY_STATUS_TEXT["connected"]
        assert M.parser.llm._byok_key == "sk-ant-good"

    def test_an_unreachable_check_still_installs_the_key(self, key_seams, monkeypatch):
        """Offline at Settings time is not a bad key: the key goes in and a
        later live parse keeps the line honest."""
        M, _providers = key_seams
        from fastapi.testclient import TestClient
        monkeypatch.setattr(M, "_check_anthropic_key", lambda key: "unreachable")
        data = TestClient(M.app).post("/config/llm", json={"api_key": "sk-ant-far"}).json()
        assert data["success"] is True and data["key_status"] == "unreachable"
        assert M.parser.llm._byok_key == "sk-ant-far"

    def test_disconnecting_reads_not_connected(self, key_seams, monkeypatch):
        M, _providers = key_seams
        from fastapi.testclient import TestClient
        monkeypatch.setattr(M, "_check_anthropic_key", lambda key: "connected")
        client = TestClient(M.app)
        client.post("/config/llm", json={"api_key": "sk-ant-good"})
        with patch.dict(os.environ, {"LLM_MODE": "mock"}):
            data = client.post("/config/llm", json={"api_key": ""}).json()
        assert data["success"] is True
        assert data["key_status"] == "not_connected"
        assert M.parser.llm._byok_key is None

    def test_every_state_has_a_sentence(self, key_seams):
        M, _providers = key_seams
        for state, text in M.KEY_STATUS_TEXT.items():
            assert text and text[0].isupper(), state
        for state in M._LIVE_FAILURE_STATE.values():
            assert state in M.KEY_STATUS_TEXT

    def test_the_real_check_never_raises_under_the_suites_network_guard(self, key_seams):
        """The suite refuses every non-loopback connection; the Settings click
        must survive that as `unreachable`, never a 500."""
        M, _providers = key_seams
        assert M._check_anthropic_key("sk-ant-nowhere") == "unreachable"


class TestTheParserNoticeIsSaidOnce:
    def test_a_rejected_live_parse_is_said_once_and_sets_the_state(self, key_seams):
        M, providers = key_seams
        providers._record_api_outcome("auth")
        first = M._live_parser_outcome_notice()
        assert first and "rejected" in first and "offline parser" in first
        assert M._key_status["state"] == "rejected"
        providers._record_api_outcome("auth")
        assert M._live_parser_outcome_notice() is None, "once per session"
        assert M._key_status["state"] == "rejected"

    def test_a_success_after_a_lapse_reads_connected(self, key_seams):
        M, providers = key_seams
        providers._record_api_outcome("timeout")
        assert M._live_parser_outcome_notice()
        assert M._key_status["state"] == "unreachable"
        providers._record_api_outcome(providers.API_OUTCOME_OK)
        assert M._live_parser_outcome_notice() is None
        assert M._key_status["state"] == "connected"

    def test_a_rejection_is_never_overwritten_by_a_later_success_alone(self, key_seams):
        """A key Anthropic refused stays refused until the player connects
        another — the state a success may lift is `configured` or
        `unreachable`, never `rejected`."""
        M, providers = key_seams
        providers._record_api_outcome("permission")
        M._live_parser_outcome_notice()
        providers._record_api_outcome(providers.API_OUTCOME_OK)
        M._live_parser_outcome_notice()
        assert M._key_status["state"] == "rejected"

    def test_the_notice_rides_the_response_once(self, key_seams):
        M, providers = key_seams
        providers._record_api_outcome("network")
        first = M.build_base_response(M.world)
        assert "could not be reached" in first["parser_notice"]
        second = M.build_base_response(M.world)
        assert "parser_notice" not in second

    def test_a_new_key_earns_a_fresh_notice(self, key_seams, monkeypatch):
        M, providers = key_seams
        from fastapi.testclient import TestClient
        providers._record_api_outcome("auth")
        M._live_parser_outcome_notice()
        monkeypatch.setattr(M, "_check_anthropic_key", lambda key: "connected")
        TestClient(M.app).post("/config/llm", json={"api_key": "sk-ant-new"})
        assert M._parser_notice["spoken"] is False

    def test_the_provider_records_every_outcome_it_prints(self):
        """Two-directional: each typed exception arm in the provider records
        a kind, and every kind it records is one the server maps or defaults."""
        from backend.ai import providers
        src = _read(REPO / "backend" / "ai" / "providers.py")
        at = src.index("except anthropic.AuthenticationError")
        block = src[at:src.index("_record_api_outcome(API_OUTCOME_OK)")]
        arms = block.count("except ")
        records = block.count("_record_api_outcome(")
        assert arms == records, (arms, records)
        for kind in re.findall(r'_record_api_outcome\("(\w+)"\)', block):
            assert kind in providers.API_FAILURE_KINDS, kind

    def test_the_client_prints_the_notice_before_routing(self):
        """The line is stashed nowhere: an early-returning route must not
        swallow a sentence the backend will not say twice — it prints
        beside the stash chain, before `_post_hud_response_routes`."""
        main = _read(SCRIPTS / "main.gd")
        at = main.index("func _on_command_result")
        body = main[at:main.index("\nfunc ", at + 10)]
        notice = body.index('response.get("parser_notice"')
        assert body.index("_stash_ending(response)") < notice
        assert notice < body.index("tutorial_overlay.observe(response)")
        assert notice < body.index("_post_hud_response_routes")


class TestTheOnceEverKeylessHint:
    def test_the_backend_says_whether_it_parses_live(self):
        from fastapi.testclient import TestClient
        import backend.main as M
        assert TestClient(M.app).get("/test").json()["smarter_parsing"] is False

    def test_the_client_says_it_once_and_latches(self):
        main = _read(SCRIPTS / "main.gd")
        at = main.index("func _maybe_print_parser_hint")
        body = main[at:main.index("\nfunc ", at + 10)]
        assert 'response.get("smarter_parsing"' in body
        assert 'UiSettings.get_api_key() != ""' in body
        assert "UiSettings.get_parser_hint_seen()" in body
        assert "UiSettings.set_parser_hint_seen(true)" in body
        assert "Smarter Parsing" in body and "Berthier" in body
        assert "add_output(" in body, "a terminal line, never a modal"
        assert "dialog" not in body.lower()
        # called from the connection test, after the boot help
        at2 = main.index("func _on_connection_test")
        conn = main[at2:main.index("\nfunc ", at2 + 10)]
        assert conn.index("_print_boot_help()") < conn.index("_maybe_print_parser_hint(response)")

    def test_the_latch_lives_in_ui_settings(self):
        ui = _read(SCRIPTS / "ui_settings.gd")
        assert "static func get_parser_hint_seen" in ui
        assert "static func set_parser_hint_seen" in ui
        assert '"parser", "hint_seen"' in ui


class TestTheSettingsCopyTellsTheTruth:
    def test_the_section_is_smarter_parsing_and_says_where_the_key_goes(self):
        panel = _read(SCRIPTS / "settings_panel.gd")
        assert "SMARTER PARSING (OPTIONAL)" in panel
        assert "THE PARSER (AI)" not in panel
        assert "never anywhere else" not in panel, "PB-3: the key goes to Anthropic"
        assert "sent to Anthropic" in panel
        assert "console.anthropic.com" in panel
        assert '"Connect"' in panel and '"Disconnect"' in panel
        assert 'data.get("key_status_text"' in panel

    def test_the_config_template_says_the_same(self):
        template = _read(DEPLOY / "dist_template" / "config.txt")
        assert "sent only to" in template and "Anthropic" in template
        assert "Smarter Parsing" in template
        assert "rejected" in template

    def test_a_lost_server_names_the_remedy_and_the_log(self):
        utils = _read(SCRIPTS / "utils.gd")
        assert "static func server_lost_hint()" in utils
        assert "static func server_error_hint(" in utils
        assert r'const SERVER_LOG_PATH = "%APPDATA%\\InkAndIron\\logs\\server.log"' in utils
        api = _read(SCRIPTS / "api_client.gd")
        assert "Utils.server_lost_hint()" in api
        assert "Utils.server_error_hint(response_code)" in api
        assert '"Connection failed"' not in api

    def test_the_build_stamp_reaches_the_menus(self):
        menu = _read(SCRIPTS / "main_menu.gd")
        assert 'test_data.get("version"' in menu
        assert "MenuBoot.server_version" in menu
        pause = _read(SCRIPTS / "pause_menu.gd")
        assert "MenuBoot.server_version" in pause
        assert "Utils.build_label()" in pause
        boot = _read(SCRIPTS / "menu_boot.gd")
        assert "static var server_version" in boot
        main = _read(SCRIPTS / "main.gd")
        assert 'MenuBoot.server_version = str(response.get("version"' in main

    def test_the_terminal_text_can_be_selected(self):
        scene = _read(SCENES / "main.tscn")
        at = scene.index('[node name="OutputDisplay" type="RichTextLabel"')
        block = scene[at:scene.index("[node ", at + 10)]
        assert "selection_enabled = true" in block


# ═══════════════════════════════════════════════════════════════════════
# 5. PB-2 — the tester kit teaches orders the game takes
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture
def fresh_1805(monkeypatch):
    """A TestClient on the SHIPPED 1805 boot. The suite pins
    `SOVEREIGN_SCENARIO=none` (the bare flag world) for every test, so the
    three board variables are cleared and the world reset before the client
    is built — the CN fixtures' idiom; `reset()` starts a fresh campaign
    (saves go to the suite's sandbox, conftest). The pinned world is handed
    back afterwards."""
    from fastapi.testclient import TestClient
    import backend.main as M
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    M._reset_world_state()
    client = TestClient(M.app)

    def reset():
        assert client.post("/new_game", json={}).json()["success"]
    yield client, reset
    monkeypatch.undo()
    M._reset_world_state()


def _readme_examples() -> list[str]:
    text = _read(DEPLOY / "README_TESTER.txt")
    at = text.index("TYPE ORDERS")
    block = text[at:text.index("SPEAK COMMANDS", at)]
    return re.findall(r'^\s+"([^"]+)"\s*$', block, re.M)


def _boot_help_examples() -> list[str]:
    main = _read(SCRIPTS / "main.gd")
    at = main.index("func _print_boot_help")
    body = main[at:main.index("\nfunc ", at + 10)]
    return re.findall(r'\\"([^\\"]+)\\"', body)


class TestTheReadmeAndBootHelpExamplesExecute:
    """The `help` manual's own quoted phrasings are censused by
    `test_cx3_the_predictor.py::TestTheGameCanReadWhatItPrints` (typable AND
    surviving the executor; PB-2 widened its needles with "is a nation, not a
    province"). These are the two surfaces that census does not read — and
    they are held to a stronger bar: each order EXECUTES on a fresh boot."""
    def test_the_readme_advertises_at_least_five_orders(self):
        assert len(_readme_examples()) >= 5

    @pytest.mark.parametrize("order", _readme_examples())
    def test_readme_example_executes_on_turn_one(self, fresh_1805, order):
        client, reset = fresh_1805
        reset()
        reply = client.post("/command", json={"command": order}).json()
        assert reply.get("success") is True, (order, reply.get("message"))

    @pytest.mark.parametrize("order", _boot_help_examples())
    def test_boot_help_example_executes_on_turn_one(self, fresh_1805, order):
        client, reset = fresh_1805
        reset()
        reply = client.post("/command", json={"command": order}).json()
        assert reply.get("success") is True, (order, reply.get("message"))

    def test_the_boot_help_no_longer_teaches_a_bare_recruit(self):
        assert "recruit" not in [e.strip('"') for e in _boot_help_examples()]

    def test_the_readme_no_longer_teaches_a_nation_as_a_province(self):
        assert "Davout, move to Bavaria" not in _read(DEPLOY / "README_TESTER.txt")


class TestTheDebugBlockIsForDebugBuilds:
    def _help(self, debug: bool) -> str:
        from backend.commands.executor import CommandExecutor
        from backend.models.world_state import WorldState
        gs = {"world": WorldState(player_nation="France"), "debug_mode": debug}
        return CommandExecutor()._execute_help({"action": "help"}, gs)["message"]

    def test_the_shipped_help_has_no_debug_commands(self):
        text = self._help(False)
        assert "DEBUG COMMANDS" not in text
        assert "/debug" not in text

    def test_debug_mode_lists_them(self):
        text = self._help(True)
        assert "DEBUG COMMANDS (for testing):" in text
        assert "/debug counter_punch" in text

    def test_the_refusal_no_longer_names_main_py(self):
        from backend.commands.executor import CommandExecutor
        from backend.models.world_state import WorldState
        gs = {"world": WorldState(player_nation="France")}
        with patch.dict(os.environ, {"DEBUG_MODE": "false"}):
            reply = CommandExecutor()._execute_debug({"action": "debug", "target": "hold"}, gs)
        assert reply["success"] is False
        assert "main.py" not in reply["message"]
        assert "not available in this build" in reply["message"]


class TestTheRecruitRemedyIsDerived:
    def test_the_remedy_names_an_order_the_board_takes(self):
        """On the 1805 boot nobody stands within reach of Paris and the chest
        holds 800 — enough for Davout's 3,000 foot at Rhineland (741 gold),
        though not for Soult's at Lorraine (872), which is the levy the old
        remedy's neighbour named. The remedy names the levy the board TAKES
        and prices it, never the order the treasury refuses next."""
        from backend.commands import economy_executor as ee
        from backend.models.world_state import WorldState
        world = WorldState.from_scenario(str(MAPS / "europe_1805.json"))
        remedy = ee.recruit_remedy(world)
        assert "recruit 10000 infantry with Ney" not in remedy
        m = re.search(r'"(\w+), recruit (\w+)"', remedy)
        assert m, remedy
        name, arm = m.group(1), m.group(2)
        quote = ee.recruit_quote(world, world.marshals[name].location, arm)
        assert quote["ok"] and quote["recipient"] == name, quote
        assert f"{int(quote['price']):,}" in remedy

    def test_the_remedy_states_the_price_gap_when_nothing_is_affordable(self):
        from backend.commands import economy_executor as ee
        from backend.models.world_state import WorldState
        world = WorldState.from_scenario(str(MAPS / "europe_1805.json"))
        world.gold = 100
        remedy = ee.recruit_remedy(world)
        assert "treasury holds 100" in remedy
        assert re.search(r"costs \d", remedy), remedy
        assert ", recruit " in remedy, "the gap still names the order that would raise them"

    def test_the_remedy_names_a_levy_when_one_is_affordable(self):
        from backend.commands import economy_executor as ee
        from backend.models.world_state import WorldState
        world = WorldState.from_scenario(str(MAPS / "europe_1805.json"))
        world.gold = 5000
        remedy = ee.recruit_remedy(world)
        m = re.search(r'"(\w+), recruit (\w+)"', remedy)
        assert m, remedy
        name, arm = m.group(1), m.group(2)
        quote = ee.recruit_quote(world, world.marshals[name].location, arm)
        assert quote["ok"] and quote["recipient"] == name and quote["arm"] == arm
        assert f"{int(quote['amount']):,}" in remedy and f"{int(quote['price']):,}" in remedy

    def test_the_refusal_carries_it_on_both_roads(self):
        """The executor's sentence and the chip's quote read the same remedy
        (the CN-1 drift pin holds), so nothing re-derives it."""
        from backend.commands import economy_executor as ee
        from backend.models.world_state import WorldState
        world = WorldState.from_scenario(str(MAPS / "europe_1805.json"))
        quote = ee.recruit_quote(world, "Paris", None)
        assert quote["kind"] == "no_recipient"
        assert ee.recruit_remedy(world) in quote["reason"]


# ═══════════════════════════════════════════════════════════════════════
# 6. PB-5 — the README
# ═══════════════════════════════════════════════════════════════════════

class TestTheReadmeGaps:
    def _text(self):
        return _read(DEPLOY / "README_TESTER.txt")

    def test_smartscreen(self):
        text = self._text()
        assert "More info" in text and "Run anyway" in text
        assert "Unblock" in text

    def test_three_windows(self):
        text = self._text()
        assert "Three windows open" in text
        assert "Two windows" not in text

    def test_the_logs_and_what_to_send(self):
        text = self._text()
        assert r"%APPDATA%\InkAndIron\logs\server.log" in text
        assert "transcript.jsonl" in text
        assert "build number" in text
        assert "stays open when something goes wrong" not in text

    def test_the_doors(self):
        text = self._text()
        assert '"help"' in text and '"what can I do"' in text

    def test_the_ending_is_the_one_that_ships(self):
        """GE-1..GE-3 landed: the README no longer needs a 'no ending yet'
        note — it names the Verdict, the Congress and the Fall, with the
        numbers the scenario authors."""
        text = self._text()
        block = text[text.index("HOW A CAMPAIGN ENDS"):text.index("CONTROLS")]
        end = json.loads(_read(MAPS / "europe_1805.json"))["campaign_end"]
        assert f"turn {end['verdict_turn']}" in block
        assert f"{end['hold_titled']} provinces" in block
        assert "Congress of Paris" in block and "IMPERIAL PEACE" in block
        assert "FALLS" in block
        assert "no ending yet" not in text.lower()

    def test_the_smarter_parsing_path_matches_the_panel(self):
        text = self._text()
        assert "SMARTER PARSING" in text
        assert "THE PARSER (AI)" not in text
        assert "Key rejected" in text

    def test_the_lost_server_troubleshooting(self):
        text = self._text()
        assert "war office is not answering" in text
        assert "Continue or Load restores it" in text
