"""The save floor: the suite never writes into the developer's own ``saves/``.

IQ-7 review round, September 18, 2026. ``tests/conftest.py`` already redirected
``save_manager.SAVE_DIR`` per TEST, but pytest builds module-scoped fixtures
before function-scoped autouse ones, and a child process never sees a
monkeypatch at all — so a module-scoped fixture that played real end turns, and
every spawned driver run, still rewrote ``saves/autosave.json``, the slot the
main menu's Continue loads (measured: a full-suite run replaced it with
"Autosave - Turn 13" of a test campaign).

The floor is the environment variable, set at conftest import before any
backend module loads. These pins read it from the three places that escaped.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_SAVES = (REPO_ROOT / "saves").resolve()


def _is_repo_saves(path) -> bool:
    resolved = Path(path).resolve()
    return resolved == REPO_SAVES or REPO_SAVES in resolved.parents


@pytest.fixture(scope="module")
def save_dir_seen_by_a_module_fixture():
    """Built BEFORE the function-scoped `_isolate_save_dir` — the escape."""
    import backend.save_manager as save_manager
    return Path(save_manager.SAVE_DIR)


def test_a_module_scoped_fixture_never_sees_the_repo_saves(
        save_dir_seen_by_a_module_fixture):
    assert not _is_repo_saves(save_dir_seen_by_a_module_fixture), (
        "a module-scoped fixture resolved the developer's own saves/ — an "
        "end turn inside it overwrites the Continue slot")


def test_the_floor_is_the_environment_variable():
    floor = os.environ.get("INK_IRON_SAVE_DIR")
    assert floor, "conftest no longer sets the save floor at import"
    assert not _is_repo_saves(floor)


def test_a_child_process_inherits_the_floor():
    """The driver and sweep pins spawn subprocesses; a monkeypatch never
    reaches them, the environment does."""
    code = ("import backend.save_manager as s, pathlib; "
            "print(pathlib.Path(s.SAVE_DIR).resolve())")
    out = subprocess.run([sys.executable, "-c", code], cwd=REPO_ROOT,
                         capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr[-500:]
    assert not _is_repo_saves(out.stdout.strip().splitlines()[-1])


def test_the_pin_is_sensitive_to_a_missing_floor():
    """Without the variable the dev default IS the repo's saves/ — which is
    what the three pins above would see if the floor were removed."""
    code = ("import os; os.environ.pop('INK_IRON_SAVE_DIR', None); "
            "import backend.save_manager as s, pathlib; "
            "print(pathlib.Path(s.SAVE_DIR).resolve())")
    env = {k: v for k, v in os.environ.items() if k != "INK_IRON_SAVE_DIR"}
    out = subprocess.run([sys.executable, "-c", code], cwd=REPO_ROOT, env=env,
                         capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr[-500:]
    assert _is_repo_saves(out.stdout.strip().splitlines()[-1])
