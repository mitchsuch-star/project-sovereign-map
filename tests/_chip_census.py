"""CN-4 shared helpers: boot a mock-parser 1805 board, drive a command at
POST /command and read its effect, and render the REAL region panel headless
through `tools/cn3_region_panel_harness.gd`.

Not a test module (leading underscore): imported by
tests/test_cn4_the_chip_honesty_census.py.
"""

import contextlib
import io
import json
import os
import pathlib
import re
import shutil
import subprocess

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands.parser import CommandParser

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
HARNESS = REPO / "tools" / "cn3_region_panel_harness.gd"

_CANDIDATES = [
    os.environ.get("GODOT_BIN", ""),
    r"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe"
    r"\Godot_v4.4.1-stable_win64.exe",
    "godot",
    "godot4",
]

CHIP_RE = re.compile(r"\[url=((?:do|order):[^\]]*)\](?:\[color=#[0-9a-fA-F]+\])?"
                     r"([^\[]*)")


def engine():
    for candidate in _CANDIDATES:
        if not candidate:
            continue
        if os.path.sep in candidate or "/" in candidate:
            if pathlib.Path(candidate).is_file():
                return candidate
            continue
        found = shutil.which(candidate)
        if found:
            return found
    return None


def board_env(mp):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        mp.delenv(key, raising=False)
    mp.setenv("LLM_MODE", "mock")
    boot()
    mp.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False


def boot():
    with contextlib.redirect_stdout(io.StringIO()):
        M._reset_world_state()


def refresh_view(world):
    with contextlib.redirect_stdout(io.StringIO()):
        world.calculate_visibility()
        world.invalidate_active_nations_cache()


def post(client, body):
    with contextlib.redirect_stdout(io.StringIO()):
        return client.post("/command", json=body).json()


def chip_command(url):
    """The command a chip url sends — the region panel's `_on_meta_clicked`
    turns "order:<verb>:<Name>" into "<Name>, <verb>" and "do:<cmd>" into
    <cmd>."""
    if url.startswith("order:"):
        _, verb, who = url.split(":", 2)
        return f"{who}, {verb}"
    return url[len("do:"):]


def chips(bbcode):
    """(url, label, tail) for every enabled chip — `tail` is the text after
    the chip up to the next chip or the end of its line (its stated terms)."""
    out = []
    for m in CHIP_RE.finditer(bbcode):
        rest = bbcode[m.end():]
        line_end = rest.find("\n")
        tail = rest if line_end < 0 else rest[:line_end]
        nxt = tail.find("[url=")
        if nxt >= 0:
            tail = tail[:nxt]
        tail = re.sub(r"\[/?[a-z]+[^\]]*\]", "", tail).strip()
        out.append((m.group(1), m.group(2).strip(), tail))
    return out


def render(game_state, regions, recruitment, work, overview=None, wizard_cases=None):
    """Run the harness once. Returns {"regions": {region: bbcode}, "bench":
    bbcode, "cards": bbcode (the Generals cards, when `overview` — the
    `/marshal_overview` response — is given), "errors": SCRIPT ERROR count}.
    Skips when the engine is absent."""
    exe = engine()
    if exe is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    out = work / "rendered.json"
    log = work / "godot.log"
    spec = work / "spec.json"
    spec.write_text(json.dumps({"game_state": game_state, "regions": regions,
                                "recruitment": recruitment,
                                "overview": overview or {},
                                "wizard_cases": wizard_cases or [],
                                "out": str(out)}),
                    encoding="utf-8")
    env = dict(os.environ, CN3_SPEC=str(spec), CN3_OUT=str(out))
    proc = subprocess.run(
        [exe, "--headless", "--path", str(PROJECT), "--log-file", str(log),
         "--script", str(HARNESS)],
        capture_output=True, text=True, timeout=300, env=env, cwd=str(PROJECT))
    if not out.is_file():
        pytest.fail("the harness wrote no result\n"
                    f"exit={proc.returncode}\nstderr tail:\n{proc.stderr[-2000:]}")
    result = json.loads(out.read_text(encoding="utf-8"))
    assert "error" not in result, result.get("error")
    log_text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    return {"regions": result["regions"], "bench": result.get("bench", ""),
            "cards": result.get("cards", ""),
            "wizard": result.get("wizard", []),
            "errors": log_text.count("SCRIPT ERROR")}


def game_state_now():
    with contextlib.redirect_stdout(io.StringIO()):
        return TestClient(M.app).get("/test").json()["game_state"]


def overview_now():
    with contextlib.redirect_stdout(io.StringIO()):
        return TestClient(M.app).get("/marshal_overview").json()
