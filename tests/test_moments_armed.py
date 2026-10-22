"""S14c part 2, second landing — three letters armed (`docs/EVENTS_SPEC.md`
§2, §3.6, §7, §9 Part 2).

The shipped 1805 scenario carries the `moments` block with the Bavarian
Match, the Throne of Holland and the Decree of Berlin — pinned equal to the
staged deck's entries (the Crown of the Reich arms in part 3). On the boot:
the windows resolve (historical = value), the road matrix's nine cells hold
(M1, M2 on every road; M4 with no road and on Road III, forsworn on I and
II), Holland's letter applies exactly its quote through the real endpoint,
and on the passive `historical` board the Match and the Decree pass silently
(their premises false — Bavaria gone, no port to shut) while Holland's letter
arrives where her loyalty dips, stands two turns behind the settlement
offer, and lapses as its empty decline.
"""
import contextlib
import io
import json
import random
from pathlib import Path

import pytest

import backend.main as M
from backend.game_logic import imperial_designs as ID
from backend.game_logic import moments as MO
from backend.game_logic import naval
from tests import _chip_census as C
from tests.test_moments_engine import _at, _letter, _make_current, _rich, _tick

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
FIXTURE = REPO / "tests" / "fixtures" / "moments_block.json"
ARMED = ("bavarian_match", "throne_of_holland", "decree_of_berlin")


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


class TestTheShippedBlock:
    def test_the_scenario_ships_the_three_letters_as_ruled(self):
        shipped = json.loads(SCENARIO.read_text(encoding="utf-8"))["moments"]
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        assert shipped["owner"] == fixture["owner"] and shipped["pacing"] == fixture["pacing"]
        by_id = {e["id"]: e for e in fixture["deck"]}
        assert [e["id"] for e in shipped["deck"]] == list(ARMED)
        for e in shipped["deck"]:
            assert e == by_id[e["id"]], e["id"]          # the staged deck IS the shipped content

    def test_the_shipped_scenario_validates(self):
        from backend.modding.validator import validate_scenario
        errors = [e for e in validate_scenario(str(SCENARIO)).errors if e.path.startswith("moments")]
        assert errors == []

    def test_the_boot_is_armed_on_its_authored_turns(self, world):
        assert MO.armed(world)
        assert {e["id"]: e["turn"] for e in MO.deck(world)} == {
            "bavarian_match": 8, "throne_of_holland": 18, "decree_of_berlin": 29}
        assert world.to_dict()["moments"]["state"] == {}


class TestTheRoadMatrix:
    """§3.6: M1 and M2 ride every road; M4 rides no road and Road III, and is
    forsworn on Roads I and II (the Crown of the Reich's three cells are
    part 3's)."""

    @pytest.mark.parametrize("road, gates", [
        ("", {"bavarian_match": "open", "throne_of_holland": "open", "decree_of_berlin": "open"}),
        ("rhine", {"bavarian_match": "open", "throne_of_holland": "open", "decree_of_berlin": "forsworn"}),
        ("crowns", {"bavarian_match": "open", "throne_of_holland": "open", "decree_of_berlin": "forsworn"}),
        ("system", {"bavarian_match": "open", "throne_of_holland": "open", "decree_of_berlin": "open"}),
    ])
    def test_each_cell(self, world, road, gates):
        if road:
            state = ID._state(world)
            state["road"], state["proclaimed_turn"] = road, 2
        assert {mid: MO.road_gate(world, MO.entry(world, mid)) for mid in ARMED} == gates

    def test_a_forsworn_decree_never_arrives(self, world):
        state = ID._state(world)
        state["road"], state["proclaimed_turn"] = "rhine", 2
        _at(world, 9)
        _tick(world)
        assert MO.status_row(world, "decree_of_berlin")["reason"] == "forsworn"


class TestHollandThroughTheEndpoint:
    def test_crown_louis_applies_its_quote_and_its_closure(self, world):
        from fastapi.testclient import TestClient
        world.vassals["Holland"]["loyalty"] = 60
        world.diplomatic_states[world._make_diplo_key("Holland", "Britain")] = "PEACE"
        _rich(world)
        for mid in ("bavarian_match",):
            world.moments["state"][mid] = {"status": "passed", "turn": 11, "reason": "premise"}
        _at(world, 18)
        assert _tick(world) == ["throne_of_holland"]
        letter = _letter(world, "throne_of_holland")
        _make_current(world, letter)
        row = MO.plan(world, MO.entry(world, "throne_of_holland"), "accept")["rows"][0]
        with _quiet():
            result = TestClient(M.app).post("/respond_to_diplomatic_dialogue", json={
                "choice": "accept", "dialogue_id": letter["dialogue_id"]}).json()
        assert result["success"] is True, result
        assert world.vassals["Holland"]["autonomy"] == 2
        assert world.vassals["Holland"]["loyalty"] == row["loyalty_after"]
        assert naval.closed_ports_against(world, "Britain") == row["ports_after"] < row["ports_before"]


class TestTheBackfill:
    """§3.5: a pre-S14c 1805 save is armed on load with the shipped block,
    resolved with its own seed; a window closed by the save turn is
    `passed(before_save)` — nothing fires retroactively."""

    @pytest.mark.parametrize("name, turn, passed", [
        ("fixture_t10_ambient", 10, {"bavarian_match"}),
        ("fixture_t20_ambient", 20, {"bavarian_match", "throne_of_holland"}),
    ])
    def test_a_pre_s14c_save_is_armed_with_its_closed_windows_passed(self, tmp_path, name, turn, passed):
        from backend import save_manager
        source = REPO / "tests" / "fixtures" / "playtest_saves" / f"{name}.json"
        data = json.loads(source.read_text(encoding="utf-8"))
        assert "moments" not in data["world_state"]              # written before S14c
        copy_path = tmp_path / source.name
        copy_path.write_text(json.dumps(data), encoding="utf-8")
        with _quiet():
            loaded = save_manager.load_game(copy_path)
        assert loaded["success"], loaded.get("message")
        world = loaded["world"]
        assert int(world.current_turn) == turn and MO.armed(world)
        state = world.moments["state"]
        assert {mid for mid, row in state.items() if row.get("reason") == "before_save"} == passed
        assert all(state[mid]["turn"] == turn for mid in passed)


@pytest.mark.xdist_group(name="engine")
class TestThePassiveBoard:
    """The series harness's own loop (passive France, `random.seed(10_000 +
    turn)`) on the shipped boot, 32 end turns."""

    @pytest.fixture(scope="class")
    def campaign(self):
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.turn_manager import TurnManager
        from backend.models.world_state import WorldState
        with _quiet():
            world = WorldState.from_scenario(str(SCENARIO))
            executor = CommandExecutor()
            tm = TurnManager(world, executor=executor)
            game_state = {"world": world, "executor": executor}
            lapse_rows = []
            for turn in range(31):
                random.seed(10_000 + turn)
                tm.end_turn(game_state)
                if int(world.current_turn) == 20:     # before the 500-row roll can evict it
                    lapse_rows = [dict(e) for e in world.event_log if e.get("type") == "offer_lapsed"
                                  and e.get("proposal_type") == "moment_letter"]
        world._s14c_lapse_rows = lapse_rows
        return world

    def test_holland_arrives_where_she_slips_and_lapses_as_her_decline(self, campaign):
        row = MO.status_row(campaign, "throne_of_holland")
        assert row["status"] == "lapsed" and row["turn"] == 18 and row["answer"] == "decline"
        lapse = campaign._s14c_lapse_rows
        assert lapse and lapse[0]["nation"] == "" and lapse[0]["moment"]["id"] == "throne_of_holland"

    def test_the_match_and_the_decree_pass_silently(self, campaign):
        assert MO.status_row(campaign, "bavarian_match")["reason"] == "premise"
        assert MO.status_row(campaign, "decree_of_berlin")["reason"] == "premise"
        fired = sorted(mid for mid, row in campaign.moments["state"].items()
                       if row.get("status") in ("fired", "answered", "lapsed"))
        assert fired == ["throne_of_holland"]

    def test_no_cooldown_key_for_a_court_called_unknown(self, campaign):
        keys = list(getattr(campaign, "ai_proposal_cooldowns", {}) or {})
        assert not [k for k in keys if k.startswith("Unknown") or k.startswith("|")
                    or "moment_letter" in k], keys
