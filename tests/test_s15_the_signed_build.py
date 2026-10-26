"""Pre-Deploy S15 (October 25, 2026) — the signed release build.

`docs/PRE_DEPLOY_PLAN.md` §2 S15: the release build signs the server and the
client executables with the user's code-signing certificate, and the
clean-machine run checks that SmartScreen raises no block. The certificate is
the user's (an OV/EV certificate or Azure Trusted Signing); the build's seam
for it is wired here so the day the certificate arrives nothing else moves:
`deploy/build.bat` signs BOTH executables through one `:sign_exe` subroutine
driven by `INK_IRON_SIGNTOOL_ARGS` (unset = an unsigned build, said so), a
configured signing that fails stops the build, and the frozen server's smoke
verifies the signature it will ship under (`tools/release_smoke.py
--expect-signed`). The tester README's SmartScreen note is conditional now.

Source pins over the build script's COMMANDS (its `::` comments stripped, the
FA-43 lesson), plus the smoke's verifier driven with a stub signtool.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
DEPLOY = REPO / "deploy"


def _commands(text: str) -> str:
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("::"))


@pytest.fixture(scope="module")
def build() -> str:
    return _commands((DEPLOY / "build.bat").read_text(encoding="utf-8", errors="replace"))


class TestS15TheSignedBuild:
    def test_a_one_signing_subroutine_driven_by_the_environment(self, build):
        assert ":sign_exe" in build
        assert "if not defined INK_IRON_SIGNTOOL_ARGS (" in build
        assert '"%SIGNTOOL%" sign %INK_IRON_SIGNTOOL_ARGS% "%~1"' in build
        assert '"%SIGNTOOL%" verify /pa "%~1"' in build
        # the default tool is the SDK's signtool on PATH; SIGNTOOL overrides
        assert 'if not defined SIGNTOOL set "SIGNTOOL=signtool"' in build

    def test_b_both_executables_are_signed_where_they_are_made(self, build):
        server = build.index('call :sign_exe "%DIST%\\ink_iron_server.exe"')
        client = build.index('call :sign_exe "%DIST%\\InkAndIron.exe"')
        pyinstaller = build.index("-m PyInstaller deploy\\ink_iron.spec")
        export = build.index("--export-release")
        smoke = build.index("tools\\release_smoke.py")
        zipped = build.index("Compress-Archive")
        # the server right after PyInstaller and BEFORE the smoke boots it;
        # the client right after the export and before the zip
        assert pyinstaller < server < smoke
        assert export < client < zipped

    def test_c_a_configured_signing_that_fails_stops_the_build(self, build):
        sub = build[build.index("\n:sign_exe\n"):build.index("\n:after_sign_exe")]
        assert sub.count("exit /b 1") == 2, "the sign and the verify each stop the build"
        for site in ('call :sign_exe "%DIST%\\ink_iron_server.exe"',
                     'call :sign_exe "%DIST%\\InkAndIron.exe"'):
            after = build[build.index(site):build.index(site) + 120]
            assert "if errorlevel 1 (" in after and "exit /b 1" in after, site

    def test_d_the_smoke_verifies_the_signature_when_signing_is_configured(self, build):
        assert 'if defined INK_IRON_SIGNTOOL_ARGS set "_SMOKE_SIGNED=--expect-signed"' in build
        assert "release_smoke.py --dist" in build and "%_SMOKE_SIGNED%" in build
        smoke = (REPO / "tools" / "release_smoke.py").read_text(encoding="utf-8")
        assert "--expect-signed" in smoke and "def signature_verifies(" in smoke

    def test_e_the_banner_and_the_readme_say_which_build_it_is(self, build):
        assert 'set "SIGNED=UNSIGNED"' in build
        assert 'if defined INK_IRON_SIGNTOOL_ARGS set "SIGNED=signed"' in build
        assert "BUILD COMPLETE - %VERSION% (%SIGNED%)" in build
        readme = (DEPLOY / "README_TESTER.txt").read_text(encoding="utf-8", errors="replace")
        assert "If this build is unsigned" in readme and "a signed release" in readme
        assert "this build is not code-signed" not in readme

    def test_f_the_plan_names_the_seam(self):
        plan = (REPO / "docs" / "PRE_DEPLOY_PLAN.md").read_text(encoding="utf-8", errors="replace")
        assert "INK_IRON_SIGNTOOL_ARGS" in plan


class TestTheSmokesVerifier:
    """`signature_verifies` is driven with a stub signtool — a script that
    answers the way the SDK's does (exit 0 verified / 1 not)."""

    def _stub(self, tmp_path: pathlib.Path, code: int) -> str:
        stub = tmp_path / "signtool.py"
        stub.write_text(f"import sys\nprint('stub signtool', sys.argv[1:])\nsys.exit({code})\n",
                        encoding="utf-8")
        wrapper = tmp_path / ("signtool.cmd" if sys.platform.startswith("win") else "signtool")
        if sys.platform.startswith("win"):
            wrapper.write_text(f'@"{sys.executable}" "{stub}" %*\r\n', encoding="utf-8")
        else:
            wrapper.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{stub}" "$@"\n', encoding="utf-8")
            wrapper.chmod(0o755)
        return str(wrapper)

    def test_a_verified(self, tmp_path):
        sys.path.insert(0, str(REPO / "tools"))
        from release_smoke import signature_verifies
        exe = tmp_path / "ink_iron_server.exe"
        exe.write_bytes(b"MZ")
        assert signature_verifies(exe, self._stub(tmp_path, 0)) is True

    def test_b_not_verified_and_a_missing_tool(self, tmp_path):
        sys.path.insert(0, str(REPO / "tools"))
        from release_smoke import signature_verifies
        exe = tmp_path / "ink_iron_server.exe"
        exe.write_bytes(b"MZ")
        assert signature_verifies(exe, self._stub(tmp_path, 1)) is False
        assert signature_verifies(exe, str(tmp_path / "no_such_signtool.exe")) is False

    def test_c_the_smoke_refuses_an_unsigned_server_when_signing_is_expected(self, tmp_path):
        sys.path.insert(0, str(REPO / "tools"))
        import release_smoke
        exe = tmp_path / "ink_iron_server.exe"
        exe.write_bytes(b"MZ")
        rc = release_smoke.run_smoke(tmp_path, 8099, None, None, 1.0,
                                     expect_signed=True) if False else None
        # the verifier is consulted BEFORE the server is started: with a stub
        # that refuses, run_smoke returns 1 without booting anything
        proc = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0, r'%s'); import release_smoke as r; "
             "sys.exit(r.run_smoke(__import__('pathlib').Path(r'%s'), 8099, None, None, 1.0, "
             "expect_signed=True))" % (str(REPO / "tools"), str(tmp_path))],
            capture_output=True, timeout=120,
            env={**__import__("os").environ, "SIGNTOOL": self._stub(tmp_path, 1)})
        assert proc.returncode == 1, proc.stdout.decode("utf-8", errors="replace")[-500:]
        assert b"is not signed" in proc.stdout
        assert rc is None
