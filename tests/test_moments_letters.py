"""S14c part 2, first landing — S14C-X10: one autonomy plan, read by the
executor, the wizard's row, the ledger's chip and a moment letter, its
consequence line derived from the real functions (`docs/EVENTS_SPEC.md` §2
M2, §10; `docs/BUG_FIXES.md` §S14C).

Reproduced: the wizard's Increase Autonomy row carried a DP cost and nothing
else, the ledger's chip hand-copied the gain, and nothing said that a
Satellite made Autonomous leaves the count of ports shut against Britain —
or that Holland's stay counted because she fights Britain herself.
"""
import contextlib
import io
import re
from pathlib import Path

import pytest

import backend.main as M
from backend.game_logic import moments as MO
from backend.game_logic import naval
from backend.game_logic import vassal as V
from tests import _chip_census as C
from tests.test_moments_engine import _block, _rich

REPO = Path(__file__).resolve().parents[1]
GODOT = REPO / "godot-client" / "project-sovereign" / "scripts"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


@pytest.fixture
def world(monkeypatch):
    C.board_env(monkeypatch)
    return M.world


def _at_peace_with_britain(world, court="Holland"):
    world.diplomatic_states[world._make_diplo_key(court, "Britain")] = "PEACE"
    world.invalidate_active_nations_cache()


class TestThePlanNamesTheClosure:
    def test_holland_at_war_keeps_her_ports_and_says_why(self, world):
        plan = V.autonomy_change_plan(world, "Holland", 2, actor="France")
        assert plan["ok"] and plan["ports_before"] == plan["ports_after"]
        assert plan["closure_line"] == "its ports stay counted — Holland is herself at war with Britain"

    def test_holland_at_peace_takes_her_ports_out_and_the_count_is_the_real_one(self, world):
        _at_peace_with_britain(world)
        world.diplomatic_points = 3
        plan = V.autonomy_change_plan(world, "Holland", 2, actor="France")
        assert plan["ports_after"] < plan["ports_before"]
        assert plan["closure_line"] == (f"its ports leave the count against Britain: "
                                        f"{plan['ports_before']} → {plan['ports_after']} of 26")
        assert V.change_vassal_autonomy(world, "Holland", 2, actor="France")["success"]
        assert naval.closed_ports_against(world, "Britain") == plan["ports_after"]

    def test_the_tribute_in_gold_is_the_collection_s_own(self, world):
        plan = V.autonomy_change_plan(world, "Holland", 2, actor="France")
        owed = V.vassal_tribute_owed(world, "Holland")
        assert plan["tribute_gold_before"] == owed
        assert f"({plan['tribute_gold_after'] - owed:+,} gold a turn)" in plan["line"]

    def test_the_as_if_read_leaves_the_live_row_alone(self, world):
        _at_peace_with_britain(world)
        before = dict(world.vassals["Holland"])
        naval.closed_ports_against(world, "Britain", autonomy_as={"Holland": 2})
        assert world.vassals["Holland"] == before


class TestEverySurfaceReadsThePlan:
    def test_the_wizard_row_says_what_the_change_does(self, world):
        from backend.game_logic.diplomacy import get_available_diplomatic_actions
        with _quiet():
            rows = {a["action"]: a for a in get_available_diplomatic_actions(world, "Holland")}
        up = V.autonomy_change_plan(world, "Holland", 2, actor="France")["line"]
        down = V.autonomy_change_plan(world, "Holland", 0, actor="France")["line"]
        assert rows["increase_autonomy"]["effect_text"] == up
        assert rows["decrease_autonomy"]["effect_text"] == down
        assert "ports" in up and "tribute 75% → 50%" in up

    def test_the_ledger_chip_carries_the_line(self, world):
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        with _quiet():
            ledger = build_diplomatic_ledger(world)
        rows = (ledger.get("vassals") or {}).get("rows") or []
        holland = next(r for r in rows if r.get("name") == "Holland")
        assert holland["autonomy_up_line"] == V.autonomy_change_plan(world, "Holland", 2, actor="France")["line"]
        gd = (GODOT / "diplomatic_ledger.gd").read_text(encoding="utf-8")
        assert 'v.get("autonomy_up_line", "")' in gd and 'v.get("autonomy_down_line", "")' in gd
        assert 'v.get("autonomy_up_gain"' in gd          # the fallback stays (UI-6 pin)

    def test_the_moment_letter_quotes_the_same_line(self, world):
        _at_peace_with_britain(world)
        world.vassals["Holland"]["loyalty"] = 60
        _rich(world)
        e = dict(_block()["deck"][1])
        e["turn"] = 18
        world.moments = {"block": {"owner": "France", "deck": [e]},
                         "state": {"throne_of_holland": {"status": "fired", "turn": 18}}}
        quote = MO.plan(world, MO.entry(world, "throne_of_holland"), "accept")["quote"]
        assert V.autonomy_change_plan(world, "Holland", 2, actor="France")["line"] in quote
        assert "its ports leave the count against Britain" in quote

    def test_no_surface_hand_copies_the_gain(self):
        """The executor applies the plan; the only `int(10 * …)` left is the
        plan's own and the ledger's legacy field the UI-6 pin reads."""
        src = (REPO / "backend" / "game_logic" / "vassal.py").read_text(encoding="utf-8")
        fn = src[src.index("def change_vassal_autonomy"):src.index("def vassal_military_contribution")]
        assert "autonomy_change_plan(" in fn and not re.search(r"int\(10 \* mult\)", fn)
