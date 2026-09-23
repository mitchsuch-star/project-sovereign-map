"""NUI — "The Admiralty on the Map" (September 23, 2026; user-directed:
*"add naval ui and make the ux and ui work and while at it assure ux and ui
is good in other key areas"*). Landing record: `docs/NAVAL_SPEC.md` §17.

The Wooden Wall shipped mechanically complete and presentationally buried:
ledger tab 7, a few tinted dashes and an anchor glyph, and NOTHING on the
map a player could hover or click. This row gives the theatre a presence:

  * every fleet in commission stands on the map at its senior yard as the
    fourth war-table piece (the NV-7 ship), faction-tinted, its sail count
    above it — `naval_overlay.fleets`, PUBLIC counts (the §9 fog ruling);
  * a sea crossing answers a hover over open water with THE ADMIRALTY's own
    verdict sentence (`naval.crossing_line`, ONE string for the ledger's
    Crossings row, the tooltip and the region panel's THE SEA block);
  * the top bar carries the Admiralty chip (`naval_overlay.player_summary`),
    crimson under blockade, gold while a window stands open;
  * a fleet piece, a crossing, the chip and THE SEA block's link all open THE
    ADMIRALTY — the ledger's own book 7, never a second naval surface;
  * IQ10-X1 (the top bar overflowing at Interface Scale 2.0) and IQ10-X2
    (the petition's dead-button reason at the fold) ride the same slice, as
    the CR-6 triage's "next UI slice" clause required.

The backend pins run everywhere. The DRIVEN pins (the real top_bar.tscn at
two logical viewport sizes, the real region_panel.tscn through the CN-3
harness, the real map.gd through `tools/nui_map_capture.gd`) SKIP when the
engine is absent — and a skip is not a pass.
"""

import contextlib
import io
import json
import os
import pathlib
import subprocess

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands.parser import CommandParser
from backend.game_logic import naval
from backend.models.world_state import WorldState

REPO = pathlib.Path(__file__).resolve().parent.parent
PROJECT = REPO / "godot-client" / "project-sovereign"
SCENARIO = PROJECT / "assets" / "maps" / "europe_1805.json"
TUTORIAL = PROJECT / "assets" / "maps" / "tutorial_1805.json"
SCRIPTS = PROJECT / "scripts"
SCENES = PROJECT / "scenes"

_CANDIDATES = [
    os.environ.get("GODOT_BIN", ""),
    r"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe"
    r"\Godot_v4.4.1-stable_win64.exe",
    "godot",
    "godot4",
]


def _engine():
    import shutil
    for candidate in _CANDIDATES:
        if not candidate:
            continue
        if os.path.sep in candidate or "/" in candidate:
            if pathlib.Path(candidate).is_file():
                return candidate
        elif shutil.which(candidate):
            return shutil.which(candidate)
    return None


def _run_harness(script: pathlib.Path, spec: dict, work: pathlib.Path,
                 timeout: int = 300) -> dict:
    engine = _engine()
    if engine is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    out = work / "result.json"
    log = work / "godot.log"
    spec = dict(spec, out=str(out))
    spec_path = work / "spec.json"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
    env = dict(os.environ, NUI_SPEC=str(spec_path), NUI_OUT=str(out))
    proc = subprocess.run(
        [engine, "--headless", "--path", str(PROJECT), "--log-file", str(log),
         "--script", str(script)],
        capture_output=True, text=True, timeout=timeout, env=env, cwd=str(PROJECT))
    if not out.is_file():
        pytest.fail("the harness wrote no result\n"
                    f"exit={proc.returncode}\nstderr tail:\n{proc.stderr[-2000:]}")
    result = json.loads(out.read_text(encoding="utf-8"))
    log_text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    result["_script_errors"] = log_text.count("SCRIPT ERROR")
    return result


@pytest.fixture(scope="module")
def world():
    with pytest.MonkeyPatch.context() as mp:
        for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
            mp.delenv(key, raising=False)
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def fresh_world():
    with pytest.MonkeyPatch.context() as mp:
        for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
            mp.delenv(key, raising=False)
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture(scope="module")
def boot_payloads():
    """`GET /test` + `GET /map_topology` on the shipped boot — what main.gd
    feeds the map and the top bar."""
    with pytest.MonkeyPatch.context() as mp:
        for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
            mp.delenv(key, raising=False)
        mp.setenv("LLM_MODE", "mock")
        M._reset_world_state()
        mp.setattr(M, "parser", CommandParser(use_real_llm=False))
        client = TestClient(M.app)
        with contextlib.redirect_stdout(io.StringIO()):
            test = client.get("/test").json()
            topology = client.get("/map_topology").json()
    return {"test": test, "game_state": test["game_state"], "topology": topology}


# ═══════════════════════════════════════════════════════════════════════════
# The payload — fleets on the map, public counts
# ═══════════════════════════════════════════════════════════════════════════

FLEET_KEYS = {"nation", "ships", "readiness", "posture", "admiral", "station",
              "is_player", "at_war_with_player", "blockaded_by", "blockading",
              "island"}


class TestTheOverlayCarriesTheFleets:

    def test_every_fleet_in_commission_stands_at_its_senior_yard(self, world):
        """The station is the SENIOR yard — `controlled_dockyards(...)[0]`,
        the same yard the region panel says a keel is laid at — so the piece
        stands where "Lay down ships" puts the ship."""
        by_nation = {f["nation"]: f for f in naval.map_naval_overlay(world)["fleets"]}
        for nation in ("France", "Britain", "Spain", "Russia"):
            yards = naval.controlled_dockyards(world, nation)
            assert yards, nation
            assert by_nation[nation]["station"] == yards[0], nation
        # `controlled_dockyards` sorts alphabetically, so the senior yard is
        # Cornwall for Britain and Bordelais for France — the SAME yard the
        # region panel's "Lay down ships" chip names as where the keel goes.
        assert by_nation["Britain"]["station"] == "Cornwall"
        assert by_nation["Russia"]["station"] == "Estonia"
        for row in by_nation.values():
            assert set(row) == FLEET_KEYS, row
            assert row["ships"] > 0
            for key in ("ships", "readiness"):
                assert isinstance(row[key], int)
        # a ports-only row (Austria, Prussia…) is not a fleet and not drawn
        assert "Austria" not in by_nation and "Prussia" not in by_nation

    def test_the_counts_are_public_by_ruling(self, world):
        """§9 fog ruling: period newspapers printed orders of battle. A
        Russian squadron at Estonia the player has never scouted is on the
        map at its true strength."""
        by_nation = {f["nation"]: f for f in naval.map_naval_overlay(world)["fleets"]}
        assert by_nation["Russia"]["ships"] == 20
        assert by_nation["Britain"]["ships"] == 100

    def test_the_player_and_the_enemy_are_marked(self, world):
        by_nation = {f["nation"]: f for f in naval.map_naval_overlay(world)["fleets"]}
        assert by_nation["France"]["is_player"] is True
        assert [n for n, f in by_nation.items() if f["is_player"]] == ["France"]
        assert by_nation["Britain"]["at_war_with_player"] is True
        assert by_nation["Spain"]["at_war_with_player"] is False

    def test_the_boot_blockade_shows_on_both_fleets(self, world):
        by_nation = {f["nation"]: f for f in naval.map_naval_overlay(world)["fleets"]}
        assert by_nation["France"]["blockaded_by"] == "Britain"
        assert "France" in by_nation["Britain"]["blockading"]
        assert by_nation["Britain"]["blockaded_by"] == ""

    def test_sorted_by_sail_then_name(self, world):
        fleets = naval.map_naval_overlay(world)["fleets"]
        keys = [(-f["ships"], f["nation"]) for f in fleets]
        assert keys == sorted(keys)

    def test_a_fleet_whose_yards_have_all_fallen_has_no_station(self, fresh_world):
        """The ledger still lists it; the map does not invent a berth."""
        for prov in naval.get_fleet(fresh_world, "France")["dockyards"]:
            fresh_world.regions[prov].controller = "Britain"
        by_nation = {f["nation"]: f for f in naval.map_naval_overlay(fresh_world)["fleets"]}
        assert by_nation["France"]["station"] == ""


class TestThePlayerSummary:

    def test_the_boot_line(self, world):
        summary = naval.map_naval_overlay(world)["player_summary"]
        assert summary["active"] is True
        assert summary["ships"] == 45 and summary["readiness"] == 70
        assert summary["posture"] == "guard" and summary["admiral"] == "Villeneuve"
        assert summary["blockaded_by"] == "Britain"
        assert summary["shut"] >= 1
        for key in ("ships", "readiness", "window_turns", "shut", "landing", "window", "open"):
            assert isinstance(summary[key], int), key
        assert "45 sail" in summary["line"]
        assert "BLOCKADED by Britain" in summary["line"]
        assert "crossing(s) shut" in summary["line"]

    def test_a_dormant_world_hides_the_chip(self):
        tw = WorldState.from_scenario(str(TUTORIAL))
        overlay = naval.map_naval_overlay(tw)
        assert overlay["player_summary"] == {"active": False}
        assert overlay["fleets"] == []

    def test_the_summary_counts_the_verdicts_it_is_handed(self, world):
        summary = naval.player_naval_summary(
            world, [{"verdict": "shut"}, {"verdict": "landing"},
                    {"verdict": "open_ratio"}, {"verdict": "window"}])
        assert (summary["shut"], summary["landing"], summary["open"], summary["window"]) == (1, 1, 1, 1)


class TestOneCrossingSentence:

    def test_the_overlay_and_the_admiralty_read_the_same_line(self, world):
        overlay = naval.map_naval_overlay(world)
        report = naval.build_admiralty_report(world)
        ledger = {(c["link_a"], c["link_b"]): c["line"] for c in report["crossings"]}
        assert overlay["sea_link_verdicts"], "the boot board tracks the Channel"
        for entry in overlay["sea_link_verdicts"]:
            assert entry["line"] == ledger[(entry["link_a"], entry["link_b"])]
            for key in ("coverer", "from_region", "to_region"):
                assert isinstance(entry[key], str)

    def test_the_sentence_is_one_function(self, world):
        verdicts = naval.link_verdicts(world)
        key = sorted(verdicts)[0]
        a, b = key.split("|")
        line = naval.crossing_line(world, a, b, verdicts[key], "France")
        assert line.startswith(f"{a}–{b}: ")
        shut = naval.crossing_line(world, "A", "B", {"verdict": "shut", "coverer": "Britain",
                                                    "ratio": 0.5}, "France")
        assert shut == "A–B: SHUT — the Royal Navy at 2.0×"
        assert naval.crossing_line(world, "A", "B", {"verdict": "open"}, "France") == \
            "A–B: OPEN — uncovered"


# ═══════════════════════════════════════════════════════════════════════════
# The client reads it — source pins (the driven classes below are the proof)
# ═══════════════════════════════════════════════════════════════════════════

def _src(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


class TestTheThreeDoorsOpenOneRoom:

    def test_main_routes_every_naval_door_to_the_admiralty(self):
        main = _src(SCRIPTS / "main.gd")
        assert "map_area.fleet_clicked.connect(_on_map_fleet_clicked)" in main
        assert "map_area.sea_link_clicked.connect(_on_map_sea_link_clicked)" in main
        assert "top_bar.admiralty_clicked.connect(_open_admiralty)" in main
        assert "region_panel.admiralty_requested.connect(_open_admiralty)" in main
        assert "top_bar.open_ledger_to_tab(6)" in main

    def test_the_ledger_opens_to_a_book_and_the_bar_knows_the_chip(self):
        ledger = _src(SCRIPTS / "strategic_ledger.gd")
        assert "func open_to_tab(api_client, tab_index: int):" in ledger
        bar = _src(SCRIPTS / "top_bar.gd")
        for needle in ("func update_admiralty(summary: Dictionary):",
                       "func open_ledger_to_tab(tab_index: int):",
                       "func _fit_bar():", "signal admiralty_clicked"):
            assert needle in bar, needle
        assert 'name="AdmiraltyBtn"' in _src(SCENES / "top_bar.tscn")

    def test_the_map_has_the_fleet_and_crossing_arms(self):
        mapgd = _src(SCENES / "map_renderer_base.gd")
        for needle in ("signal fleet_clicked(nation)", "signal sea_link_clicked(link_a, link_b)",
                       "func _update_fleet_pieces() -> void:", "func _nearest_sea_link(",
                       'piece.setup("ship", "l", nation_color, frame)',
                       "func _draw_sea_link_tooltip():", "func _draw_fleet_tooltip():"):
            assert needle in mapgd, needle

    def test_the_region_panel_speaks_of_the_sea(self):
        panel = _src(SCRIPTS / "region_panel.gd")
        assert "THE SEA" in panel
        assert 'Utils.bb_button_chip("admiralty", "THE ADMIRALTY"' in panel
        assert "signal admiralty_requested" in panel

    def test_iq10_x2_the_reason_sits_above_the_fold(self):
        """The dead button's reason is inserted after the body's FIRST line,
        not appended as the last line of a scrollable body."""
        popup = _src(SCRIPTS / "incoming_proposal_popup.gd")
        assert "IQ10-X2" in popup
        assert 'var _head_end := bbcode.find("\\n")' in popup
        assert "bbcode = bbcode.substr(0, _head_end + 1) + _reason_line" in popup

    def test_the_harnesses_are_named_for_the_parse_check(self):
        check = _src(REPO / "tools" / "godot_parse_check.gd")
        assert "res://../../tools/nui_top_bar_harness.gd" in check
        assert "res://../../tools/nui_map_capture.gd" in check


# ═══════════════════════════════════════════════════════════════════════════
# DRIVEN — the top bar fits (IQ10-X1) and carries the chip
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def driven_bar(boot_payloads, tmp_path_factory):
    test = boot_payloads["test"]
    fields = {k: test.get(k) for k in (
        "diplomatic_points", "max_diplomatic_points", "threat_level",
        "coalition_brewing", "talleyrand_mission_summary", "pending_envoy_count",
        "pending_lapsing_count", "pending_lapsing_petitions",
        "pending_marshal_decisions")}
    summary = (boot_payloads["game_state"].get("naval_overlay") or {}).get("player_summary", {})
    return _run_harness(REPO / "tools" / "nui_top_bar_harness.gd", {
        "sizes": [[1600, 900], [800, 450]],
        "diplomatic_fields": fields,
        "admiralty": summary,
    }, tmp_path_factory.mktemp("nui_bar"))


def _run_at(result, width):
    for run in result.get("runs", []):
        if int(run["size"][0]) == width:
            return run
    raise AssertionError(f"no run at width {width}: {result}")


class TestTheTopBarFits:

    def test_the_harness_ran_clean(self, driven_bar):
        assert driven_bar.get("error") is None, driven_bar.get("error")
        assert driven_bar["_script_errors"] == 0

    @pytest.mark.parametrize("width", [1600, 800])
    def test_no_visible_button_lies_outside_the_viewport(self, driven_bar, width):
        """IQ10-X1's completion definition, measured: at 800 logical px
        (Interface Scale 2.0) EventLogBtn used to sit at x=-26."""
        run = _run_at(driven_bar, width)
        vw, vh = run["viewport"]
        for btn in run["buttons"]:
            if not btn["visible"]:
                continue
            x, y, w, h = btn["rect"]
            assert x >= -0.5 and x + w <= vw + 0.5, (width, btn)
            assert y >= -0.5 and y + h <= vh + 0.5, (width, btn)

    def test_the_bar_goes_compact_below_the_threshold_and_not_above(self, driven_bar):
        assert _run_at(driven_bar, 800)["compact"] is True
        assert _run_at(driven_bar, 1600)["compact"] is False

    def test_compact_nav_buttons_keep_their_names_in_the_tooltip(self, driven_bar):
        run = _run_at(driven_bar, 800)
        nav = {b["name"]: b for b in run["buttons"]}
        assert nav["EventLogBtn"]["text"] == ""
        assert nav["EventLogBtn"]["tooltip"].startswith("Event Log")
        assert "Alt+L" in nav["EventLogBtn"]["tooltip"]
        full = {b["name"]: b for b in _run_at(driven_bar, 1600)["buttons"]}
        assert full["EventLogBtn"]["text"] == "Event Log (L)"

    @pytest.mark.parametrize("width", [1600, 800])
    def test_the_admiralty_chip_is_live_on_a_naval_board(self, driven_bar, width):
        run = _run_at(driven_bar, width)
        chip = {b["name"]: b for b in run["buttons"]}["AdmiraltyBtn"]
        assert chip["visible"] is True
        assert "45" in chip["text"]
        assert "Villeneuve" in chip["tooltip"]
        assert "BLOCKADED" in chip["tooltip"]


# ═══════════════════════════════════════════════════════════════════════════
# DRIVEN — the region panel's THE SEA block (the CN-3 harness, real panel)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def driven_panel(boot_payloads, tmp_path_factory):
    engine = _engine()
    if engine is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip")
    work = tmp_path_factory.mktemp("nui_panel")
    out = work / "rendered.json"
    log = work / "godot.log"
    spec = work / "spec.json"
    fleets = (boot_payloads["game_state"].get("naval_overlay") or {}).get("fleets") or []
    stations = {f["nation"]: f["station"] for f in fleets}
    spec.write_text(json.dumps({
        "game_state": boot_payloads["game_state"],
        "regions": sorted({stations["France"], stations["Britain"],
                           "Flanders", "Vienna", "Normandy"}),
        "recruitment": {},
        "out": str(out),
        "stations": stations,
    }), encoding="utf-8")
    env = dict(os.environ, CN3_SPEC=str(spec), CN3_OUT=str(out))
    subprocess.run(
        [engine, "--headless", "--path", str(PROJECT), "--log-file", str(log),
         "--script", str(REPO / "tools" / "cn3_region_panel_harness.gd")],
        capture_output=True, text=True, timeout=300, env=env, cwd=str(PROJECT))
    assert out.is_file(), "the CN-3 harness wrote no result"
    rendered = json.loads(out.read_text(encoding="utf-8")).get("regions", {})
    rendered["_stations"] = stations
    return rendered


class TestTheRegionPanelSpeaksOfTheSea:

    def test_a_dockyard_names_its_fleet_and_its_blockade(self, driven_panel):
        text = driven_panel[driven_panel["_stations"]["France"]]
        assert "THE SEA" in text
        assert "France fleet" in text and "Villeneuve" in text
        assert "45 sail" in text and "readiness 70" in text
        assert "blockaded by Britain" in text
        assert "THE ADMIRALTY" in text

    def test_a_shore_carries_the_admiralty_s_own_crossing_line(self, driven_panel, world):
        """Normandy is the Channel's descent coast (London–Normandy is a
        tracked crossing at boot; the London–Flanders link was cut at NV-8c,
        so Flanders carries no crossing row and says so by silence)."""
        report = naval.build_admiralty_report(world)
        lines = {(c["link_a"], c["link_b"]): c["line"] for c in report["crossings"]}
        touched = 0
        for region in ("Flanders", "Normandy"):
            text = driven_panel[region]
            mine = [line for (a, b), line in lines.items() if region in (a, b)]
            for line in mine:
                assert "THE SEA" in text, region
                assert line.split(" — ")[0] in text, (region, line)
                touched += 1
        assert touched >= 1, "the boot board tracks the Channel at Normandy"

    def test_an_inland_capital_has_no_sea_block(self, driven_panel):
        assert "THE SEA" not in driven_panel["Vienna"]

    def test_the_enemy_yard_shows_the_royal_navy(self, driven_panel):
        text = driven_panel[driven_panel["_stations"]["Britain"]]
        assert "Britain fleet" in text and "Nelson" in text and "100 sail" in text


# ═══════════════════════════════════════════════════════════════════════════
# DRIVEN — the map carries the fleets (real map.gd, headless)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def driven_map(boot_payloads, tmp_path_factory):
    return _run_harness(REPO / "tools" / "nui_map_capture.gd", {
        "topology": boot_payloads["topology"],
        "game_state": boot_payloads["game_state"],
        "png": "",
        "settle": 30,
    }, tmp_path_factory.mktemp("nui_map"), timeout=600)


class TestTheMapCarriesTheFleets:

    def test_the_harness_ran_clean(self, driven_map):
        assert driven_map.get("error") is None, driven_map.get("error")
        assert driven_map["_script_errors"] == 0
        assert driven_map["pieces_layer"] is True

    def test_every_stationed_fleet_has_a_piece_and_a_hitbox(self, driven_map, world):
        expected = {f["nation"] for f in naval.map_naval_overlay(world)["fleets"] if f["station"]}
        got = {p["nation"] for p in driven_map["fleet_pieces"]}
        assert got == expected, (got, expected)
        assert {p["arm"] for p in driven_map["fleet_pieces"]} == {"ship"}
        assert len(driven_map["fleet_hitboxes"]) == len(driven_map["fleet_pieces"])
        stations = {b["nation"]: b["station"] for b in driven_map["fleet_hitboxes"]}
        expected_stations = {f["nation"]: f["station"]
                             for f in naval.map_naval_overlay(world)["fleets"] if f["station"]}
        assert stations == expected_stations

    def test_the_crossings_are_hoverable(self, driven_map):
        assert driven_map["sea_segments"] > 0
        probe = driven_map["midpoint_probe"]
        assert sorted([probe["a"], probe["b"]]) == sorted(driven_map["midpoint_probe_expected"])
