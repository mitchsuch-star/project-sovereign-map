"""Pre-Deploy S14h part 2 — S14G-19's engine-driven pin (October 26, 2026).

A real left press and release on the VISIBLE stack label and a marshal's name
label through `tools/s14h_r19_label_click_harness.gd` (headless Godot): the map
names the label's man and the client selects him. Split out of
`tests/test_s14h_the_third_measure_rows.py` (which keeps the source pins) so
the module sits on conftest's `engine` xdist group — one engine on the machine.
The record is in the merged module's row-19 section.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
BASE_GD = PROJECT / "scenes" / "map_renderer_base.gd"
LABEL_GD = PROJECT / "scenes" / "map_label_layer.gd"
HARNESS = REPO / "tools" / "s14h_r19_label_click_harness.gd"

def _r19_board():
    """Five corps of ours stacked at Rhineland (a collapsed group, "<lead> +4"),
    Bernadotte alone at Franconia (his own name label), on the shipped boot."""
    from tests import _chip_census as C
    import backend.main as M
    from fastapi.testclient import TestClient
    C.boot()
    world = M.world
    for key in ("Ney", "Davout", "Soult", "Lannes", "Murat"):
        world.marshals[key].location = "Rhineland"
    C.refresh_view(world)
    state = C.game_state_now()
    with contextlib.redirect_stdout(io.StringIO()):
        topology = TestClient(M.app).get("/map_topology").json()
    here = [m for m in state["map_data"]["Rhineland"]["marshals"] if m.get("nation") == "France"]
    assert len(here) == 5, [m.get("name") for m in here]
    return {
        "game_state": state,
        "topology": topology,
        "stack": {"text": "", "lead": here[0]["name"], "members": [m["name"] for m in here]},
        "name": {"text": "Bernadotte", "key": "Bernadotte"},
    }


@pytest.fixture(scope="module")
def _r19_driven(tmp_path_factory):
    from tests import _chip_census as C
    exe = C.engine()
    if exe is None:
        pytest.skip("Godot engine not on this machine - the driven pins skip, "
                    "and a skip is not a pass")
    with pytest.MonkeyPatch.context() as mp:
        C.board_env(mp)
        spec = _r19_board()
    work = tmp_path_factory.mktemp("s14h_r19")
    out, log, spec_path = work / "out.json", work / "godot.log", work / "spec.json"
    spec_path.write_text(json.dumps(dict(spec, out=str(out))), encoding="utf-8")
    env = dict(os.environ, S14H_R19_SPEC=str(spec_path))
    proc = subprocess.run(
        [exe, "--headless", "--path", str(PROJECT), "--log-file", str(log),
         "--script", str(HARNESS)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=300, env=env, cwd=str(PROJECT))
    if not out.is_file():
        pytest.fail("the harness wrote no result\n"
                    f"exit={proc.returncode}\nstderr tail:\n{proc.stderr[-2000:]}")
    result = json.loads(out.read_text(encoding="utf-8").replace(" ", " "))
    assert "error" not in result, result.get("error")
    text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    result["script_errors"] = text.count("SCRIPT ERROR")
    result["script_error_lines"] = [ln for ln in text.splitlines() if "SCRIPT ERROR" in ln][:5]
    result["spec"] = spec
    return result


@pytest.mark.engine
class TestS14G19Driven:
    """A real left press and release on the VISIBLE label (a text box the
    pieces do not cover, a point no panel sits over): the map names the label's
    man and the client selects him - it does not open the province under the
    text. The old reading: `hovered_marshal` empty, the colour map's province
    clicked, its panel opened."""

    def test_no_script_errors_and_the_layout_ran(self, _r19_driven):
        assert _r19_driven["script_errors"] == 0, _r19_driven["script_error_lines"]
        assert _r19_driven["layout_ran"] is True
        assert int(_r19_driven["label_hitboxes"]) >= 2

    def test_the_stack_label_is_found_and_has_a_clear_point(self, _r19_driven):
        assert _r19_driven["stack_found"] is True
        assert _r19_driven["stack_text"].endswith(" +4"), _r19_driven["stack_text"]
        assert _r19_driven["stack_clear_point"] is True

    def test_hovering_the_stack_label_names_its_lead(self, _r19_driven):
        lead = _r19_driven["spec"]["stack"]["lead"]
        assert _r19_driven["stack_hovered_marshal"] == lead

    def test_clicking_the_stack_label_selects_its_lead_and_opens_no_panel(self, _r19_driven):
        lead = _r19_driven["spec"]["stack"]["lead"]
        assert _r19_driven["stack_last_click_marshal"] == lead
        assert _r19_driven["stack_selected"] == lead
        assert _r19_driven["stack_panel_open"] is False

    def test_clicking_a_marshals_name_label_selects_him(self, _r19_driven):
        assert _r19_driven["name_found"] is True
        assert _r19_driven["name_clear_point"] is True
        assert _r19_driven["name_hovered_marshal"] == "Bernadotte"
        assert _r19_driven["name_selected"] == "Bernadotte"
        assert _r19_driven["name_panel_open"] is False
