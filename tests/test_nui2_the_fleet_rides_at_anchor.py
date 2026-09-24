"""NUI-2 — "The Fleet Rides at Anchor" (September 24, 2026; user-directed:
*"amsterdam is no attached to ocean on map look for any more bugs like this
explain how i use boats whats the ux"*, then *"fix all those and we should add
buttons for naval stuff maybe? its less clear what to type there and they
never disobey etc"*). Landing record: `docs/NAVAL_SPEC.md` §18.

The coast audit (`tools/gen_port_anchors.py --audit`) read every province
against the painted map. It found three dockyards on provinces the map draws
inland — Holland's Amsterdam, France's Flanders and Russia's only yard, the
province named Estonia, whose one "shore" is a lake pocket — three coastal
flags the map contradicts (Flanders, White Russia, Volhynia), and every fleet
piece drawn at its province's CENTRE (Russia's 260 px from the water). Then
the user's second point: the naval orders are typed-only and carry no
marshal's voice to prompt the words.

  * the yards move to the coast (Friesland, Normandy, Livonia), the flags are
    corrected, and a dockyard on an inland province is a validation ERROR —
    as is one with no open water to moor at on the Europe registry (the
    Estonia case: coastal as a sea-link end, with no sea);
  * every coastal province carries a `port_anchor` on open water off its own
    shore, and the map draws the fleet and the blockade glyph there;
  * a save written before the move migrates on load (the flags, the yards);
  * THE ADMIRALTY opens with its orders, and the expedition's road is
    buttons — commission a marshal (priced even when unaffordable), march him
    to a yard, land him — each the typed command the terminal takes;
  * FA-D16 reaches its last two surfaces: nothing tells the player to ship
    the Emperor, or to "march one there" when no corps exists.

The registry pins read the art with the stdlib PNG decoder
(`tools/validate_province_map.py`) — the generator needs Pillow and numpy,
which the suite does not. The DRIVEN pins (the real map and the real ledger)
skip when the engine is absent — and a skip is not a pass.
"""

import contextlib
import io
import json
import math
import os
import pathlib
import subprocess

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import strategic
from backend.commands.parser import CommandParser
from backend.game_logic import naval, recruitment
from backend.models import world_state as ws
from backend.models.world_state import WorldState
from backend.modding.validator import validate_scenario
from backend.save_manager import load_game, save_game
from tests.test_nui_the_admiralty_on_the_map import _engine, _run_harness
from tools import gen_port_anchors as gpa
from tools import validate_province_map as vpm

REPO = pathlib.Path(__file__).resolve().parent.parent
PROJECT = REPO / "godot-client" / "project-sovereign"
MAPS = PROJECT / "assets" / "maps"
REGISTRY = MAPS / "europe.json"
SCENARIO = MAPS / "europe_1805.json"
LOOKUP = MAPS / "europe_lookup.png"
VISUAL = MAPS / "europe_visual.png"
SCENES = PROJECT / "scenes"
SCRIPTS = PROJECT / "scripts"

CORRECTED_INLAND = ("Flanders", "White Russia", "Volhynia")
DEF8_FIVE = ("Bern", "Franche-Comte", "Milan", "Munich", "Tyrol")
# The fleet piece's core, relative to its base — `gen_port_anchors.PIECE_BOXES[1]`:
# every yard's anchor carries at least the hull on open water.
YARD_CORE_BOX = gpa.PIECE_BOXES[1]


def _src(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _func_body(source: str, header: str) -> str:
    start = source.index(header)
    nxt = source.find("\nfunc ", start + len(header))
    return source[start:nxt if nxt != -1 else len(source)]


@pytest.fixture(scope="module")
def registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def scenario():
    return json.loads(SCENARIO.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def by_name(registry):
    return {e["name"]: e for e in registry["regions"].values()}


@pytest.fixture(scope="module")
def art():
    """(width, lookup rgb bytes, visual rgb bytes) — decoded ONCE."""
    w, h, look = vpm.read_png_rgb_bytes(LOOKUP)
    w2, h2, vis = vpm.read_png_rgb_bytes(VISUAL)
    assert (w, h) == (w2, h2)
    return w, h, look, vis


def _rgb(buf, w, x, y):
    i = (y * w + x) * 3
    return buf[i], buf[i + 1], buf[i + 2]


def _is_water(art, x, y) -> bool:
    w, h, look, vis = art
    if not (0 <= x < w and 0 <= y < h):
        return False
    r, g, b = _rgb(look, w, x, y)
    if (r, g, b) != (0, 0, 0):
        return False
    vr, _vg, vb = _rgb(vis, w, x, y)
    return (vr - vb) < gpa.SEA_RB_MAX


def _yards(scenario):
    return {nation: list(rec.get("dockyards") or [])
            for nation, rec in scenario["navies"].items()
            if isinstance(rec, dict) and rec.get("dockyards")}


def _scenario_world():
    with pytest.MonkeyPatch.context() as mp:
        for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
            mp.delenv(key, raising=False)
        return WorldState.from_scenario(str(SCENARIO))


# ═══════════════════════════════════════════════════════════════════════════
# The registry agrees with the painted map
# ═══════════════════════════════════════════════════════════════════════════
class TestTheCoastIsWhereTheMapDrawsIt:

    def test_the_three_corrected_flags_are_inland(self, by_name):
        for name in CORRECTED_INLAND:
            assert by_name[name]["is_coastal"] is False, name

    def test_the_recorded_exceptions_keep_their_flags_and_reasons(self, by_name):
        """The DEF-8 five stay inland (the stylised Adriatic reaches them; the
        real places are landlocked) and Estonia stays coastal (a DEF-7
        sea-link end — rule G3). Each exception carries a written reason."""
        assert set(gpa.ART_EXCEPTIONS) == set(DEF8_FIVE) | {"Estonia"}
        for name in DEF8_FIVE:
            assert by_name[name]["is_coastal"] is False, name
            assert "DEF-8" in gpa.ART_EXCEPTIONS[name]
        assert by_name["Estonia"]["is_coastal"] is True
        assert "G3" in gpa.ART_EXCEPTIONS["Estonia"]

    def test_every_coastal_province_but_estonia_carries_a_port_anchor(self, by_name):
        for name, entry in by_name.items():
            has = "port_anchor" in entry
            if entry["is_coastal"] and name != "Estonia":
                assert has, f"{name} is coastal but carries no port_anchor"
            else:
                assert not has, f"{name} carries a port_anchor it cannot use"

    def test_every_port_anchor_is_open_water_off_its_own_shore(self, by_name, art):
        """The anchor pixel is no province AND sea paint; the nearest province
        to it (Euclidean, within the offshore limit) is the province itself."""
        w, h, look, _vis = art
        reach = gpa.MAX_OFFSHORE + 6
        for name, entry in by_name.items():
            if "port_anchor" not in entry:
                continue
            x, y = entry["port_anchor"]
            assert _is_water(art, x, y), f"{name}'s port anchor is not water"
            own = tuple(entry["lookup_color"])
            own_d = other_d = math.inf
            for yy in range(max(0, y - reach), min(h, y + reach + 1)):
                for xx in range(max(0, x - reach), min(w, x + reach + 1)):
                    rgb = _rgb(look, w, xx, yy)
                    if rgb == (0, 0, 0):
                        continue
                    d = math.hypot(xx - x, yy - y)
                    if rgb == own:
                        own_d = min(own_d, d)
                    else:
                        other_d = min(other_d, d)
            assert own_d <= gpa.MAX_OFFSHORE, (name, own_d)
            assert own_d < other_d, (name, own_d, other_d)

    def test_every_yard_moors_a_ship_on_open_water(self, by_name, scenario, art):
        x0, x1, y0, y1 = YARD_CORE_BOX
        for nation, yards in _yards(scenario).items():
            for yard in yards:
                x, y = by_name[yard]["port_anchor"]
                dry = [(xx, yy) for yy in range(y + y0, y + y1 + 1)
                       for xx in range(x + x0, x + x1 + 1)
                       if not _is_water(art, xx, yy)]
                assert not dry, (nation, yard, dry[:3])

    def test_yards_keep_their_distance(self, by_name, scenario):
        anchors = [(yard, by_name[yard]["port_anchor"])
                   for yards in _yards(scenario).values() for yard in yards]
        for i, (a, pa) in enumerate(anchors):
            for b, pb in anchors[i + 1:]:
                assert math.dist(pa, pb) >= gpa.MIN_SEPARATION, (a, b)

    def test_the_registry_note_records_the_pass(self, registry):
        note = registry["adjacency_derivation"]["nui2_coast_pass"]
        for word in ("Flanders", "White Russia", "Volhynia", "port_anchor",
                     "Adjacency untouched"):
            assert word in note, word


# ═══════════════════════════════════════════════════════════════════════════
# The dockyards stand on the sea
# ═══════════════════════════════════════════════════════════════════════════
class TestTheYardsStandOnTheSea:

    def test_every_yard_is_coastal_with_an_anchor(self, scenario, by_name):
        for nation, yards in _yards(scenario).items():
            for yard in yards:
                assert by_name[yard]["is_coastal"] is True, (nation, yard)
                assert "port_anchor" in by_name[yard], (nation, yard)

    def test_the_three_yards_moved(self, scenario):
        yards = _yards(scenario)
        assert yards["Holland"] == ["Friesland"]
        assert yards["Russia"] == ["Livonia"]
        assert "Normandy" in yards["France"] and "Flanders" not in yards["France"]
        # Flanders stays a CAMP province — Davout's camp at Bruges. The camp
        # counts men standing there and never asks for a coast.
        assert scenario["navies"]["France"]["camp_provinces"] == [
            "Flanders", "Artois", "Normandy", "Brittany"]

    def test_the_retired_yards_table_matches_the_scenario(self, scenario, by_name):
        """Drift pin (the EB-2 OVERSEAS_INCOME_BACKFILL idiom): the table
        duplicates the scenario on purpose."""
        yards = _yards(scenario)
        assert naval.RETIRED_DOCKYARDS == {
            "Holland": {"Amsterdam": "Friesland"},
            "France": {"Flanders": "Normandy"},
            "Russia": {"Estonia": "Livonia"},
        }
        for nation, table in naval.RETIRED_DOCKYARDS.items():
            for old, new in table.items():
                assert new in yards[nation], (nation, new)
                assert old not in yards[nation], (nation, old)
                assert "port_anchor" not in by_name[old], old

    def test_the_save_coast_table_matches_the_registry(self, by_name):
        assert set(ws.SAVE_COAST_CORRECTIONS) == set(CORRECTED_INLAND)
        for name, flag in ws.SAVE_COAST_CORRECTIONS.items():
            assert by_name[name]["is_coastal"] is flag, name

    def test_the_boot_world_builds_at_the_coast(self):
        world = _scenario_world()
        assert naval.controlled_dockyards(world, "Holland") == ["Friesland"]
        assert naval.controlled_dockyards(world, "Russia") == ["Livonia"]
        assert naval.controlled_dockyards(world, "France") == [
            "Bordelais", "Brittany", "Normandy", "Provence"]
        stations = {f["nation"]: f["station"] for f in naval.fleet_pieces(world)}
        assert stations["Holland"] == "Friesland"
        assert stations["Russia"] == "Livonia"
        for region in CORRECTED_INLAND:
            assert world.regions[region].is_coastal is False, region


# ═══════════════════════════════════════════════════════════════════════════
# The validator refuses an inland yard
# ═══════════════════════════════════════════════════════════════════════════
class TestAnInlandYardIsRefused:

    def _with_amsterdam(self, scenario):
        data = json.loads(json.dumps(scenario))
        data["navies"]["Holland"]["dockyards"] = ["Amsterdam"]
        return data

    def test_the_cli_path_reads_the_registry(self, scenario):
        """The raw file omits `regions`; the check reads the registry rather
        than skipping (the shipped file validates clean)."""
        assert validate_scenario(json.loads(json.dumps(scenario))).is_valid
        result = validate_scenario(self._with_amsterdam(scenario))
        messages = [e.message for e in result.errors]
        assert any("Dockyard 'Amsterdam' is an inland province" in m
                   for m in messages), messages

    def test_the_boot_path_refuses_to_load_it(self, scenario, tmp_path):
        path = tmp_path / "amsterdam_yard.json"
        path.write_text(json.dumps(self._with_amsterdam(scenario)), encoding="utf-8")
        with pytest.MonkeyPatch.context() as mp:
            for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
                mp.delenv(key, raising=False)
            with pytest.raises(ValueError, match="inland province"):
                WorldState.from_scenario(str(path))

    def _with_estonia(self, scenario):
        data = json.loads(json.dumps(scenario))
        data["navies"]["Russia"]["dockyards"] = ["Estonia"]
        return data

    def test_a_coastal_flag_with_no_open_water_is_refused_too(self, scenario, tmp_path):
        """Estonia keeps `is_coastal` (a DEF-7 sea-link end, rule G3), so the
        flag rule alone passed a yard there. It has no open water to moor at
        (the registry gives it no `port_anchor`), and the fleet would be
        drawn on land. The mooring rule refuses it on both paths."""
        result = validate_scenario(self._with_estonia(scenario))
        messages = [e.message for e in result.errors]
        assert any("Dockyard 'Estonia' has no open water to moor at" in m
                   for m in messages), messages
        assert not any("Dockyard 'Estonia' is an inland province" in m
                       for m in messages), messages
        path = tmp_path / "estonia_yard.json"
        path.write_text(json.dumps(self._with_estonia(scenario)), encoding="utf-8")
        with pytest.MonkeyPatch.context() as mp:
            for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
                mp.delenv(key, raising=False)
            with pytest.raises(ValueError, match="no open water to moor at"):
                WorldState.from_scenario(str(path))


# ═══════════════════════════════════════════════════════════════════════════
# An old save migrates on load
# ═══════════════════════════════════════════════════════════════════════════
class TestAnOldSaveComesAshore:

    def _old_world(self):
        world = _scenario_world()
        world.fleets["Holland"]["dockyards"] = ["Amsterdam"]
        world.fleets["France"]["dockyards"] = ["Brittany", "Provence",
                                               "Flanders", "Bordelais"]
        world.fleets["Russia"]["dockyards"] = ["Estonia"]
        for region in CORRECTED_INLAND:
            world.regions[region].is_coastal = True
        return world

    def test_the_yards_and_flags_move_on_load(self, tmp_path):
        path = tmp_path / "old_save.json"
        assert save_game(self._old_world(), "pre-NUI-2", filepath=path)["success"]
        loaded = load_game(path)
        assert loaded["success"], loaded["message"]
        world = loaded["world"]
        assert world.fleets["Holland"]["dockyards"] == ["Friesland"]
        # Authored order kept — the replacement takes the retired yard's place.
        assert world.fleets["France"]["dockyards"] == [
            "Brittany", "Provence", "Normandy", "Bordelais"]
        assert world.fleets["Russia"]["dockyards"] == ["Livonia"]
        for region in CORRECTED_INLAND:
            assert world.regions[region].is_coastal is False, region

    def test_a_new_save_moves_nothing(self):
        assert ws.reconcile_saved_registry_corrections(_scenario_world()) == {
            "coast": 0, "dockyards": 0}

    def test_the_count_is_honest(self):
        assert ws.reconcile_saved_registry_corrections(self._old_world()) == {
            "coast": 3, "dockyards": 3}

    def test_a_replacement_already_listed_is_not_doubled(self):
        world = _scenario_world()
        world.fleets["France"]["dockyards"] = ["Flanders", "Normandy"]
        assert naval.migrate_retired_dockyards(world) == 1
        assert world.fleets["France"]["dockyards"] == ["Normandy"]

    def test_a_world_the_registry_does_not_own_is_left_alone(self):
        """The all-or-nothing scope `_reconcile_saved_adjacency` argues for:
        a province the registry does not know (the legacy fixture's Belgium,
        a mod's own) leaves the whole world untouched."""
        world = self._old_world()
        world.regions["Belgium"] = world.regions.pop("Flanders")
        assert ws.reconcile_saved_registry_corrections(world) == {
            "coast": 0, "dockyards": 0}
        assert world.fleets["Holland"]["dockyards"] == ["Amsterdam"]


# ═══════════════════════════════════════════════════════════════════════════
# The Admiralty's buttons: the expedition's road
# ═══════════════════════════════════════════════════════════════════════════
def _board_env(mp):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        mp.delenv(key, raising=False)
    mp.setenv("LLM_MODE", "mock")
    with contextlib.redirect_stdout(io.StringIO()):
        M._reset_world_state()
    mp.setattr(M, "parser", CommandParser(use_real_llm=False))


def _post(line):
    with contextlib.redirect_stdout(io.StringIO()):
        return TestClient(M.app).post("/command", json={"command": line}).json()


def _road():
    return naval.build_admiralty_report(M.world)["expedition_chips"]


def _stage(board):
    """boot | funded | raised (a new marshal at Paris) | ready (at Normandy)."""
    if board == "boot":
        return None
    M.world.nation_gold["France"] = 20000
    if board == "funded":
        return None
    cand = recruitment.first_affordable_commission(M.world, "France")
    response = _post(f"commission {cand['name']}")
    assert response.get("success"), response.get("message")
    marshal = M.world.marshals[cand["name"]]
    if board == "ready":
        marshal.location = "Normandy"
    return marshal


class TestTheExpeditionIsButtons:

    def test_the_boot_names_the_commission_and_its_price(self, monkeypatch):
        _board_env(monkeypatch)
        cand = recruitment.cheapest_commission_if_funded(M.world, "France")
        assert cand is not None
        assert recruitment.first_affordable_commission(M.world, "France") is None
        [chip] = _road()
        assert chip["command"] == f"commission {cand['name']}"
        assert chip["label"] == f"Commission {cand['name']} ({int(cand['cost']):,}g)"
        assert chip["enabled"] is False
        assert chip["reason"] == recruitment.check_commission(M.world, "France", cand)
        assert f"costs {int(cand['cost']):,}g" in chip["reason"]
        assert "the treasury holds 800g" in chip["reason"]

    def test_every_button_is_its_gate(self, monkeypatch):
        """The CN-4 census, on the road's four boards: an enabled button's
        command acts, a disabled one's is refused."""
        seen = set()
        for board in ("boot", "funded", "raised", "ready"):
            _board_env(monkeypatch)
            _stage(board)
            chips = _road()
            assert chips, board
            for chip in chips:
                _board_env(monkeypatch)
                _stage(board)
                response = _post(chip["command"])
                assert bool(response.get("success")) == bool(chip["enabled"]), (
                    board, chip["command"], chip.get("reason"),
                    (response.get("message") or "")[:160])
                seen.add(chip["command"].split(" ")[0].rstrip(","))
        assert {"commission", "land"} <= seen

    def test_the_march_takes_the_shortest_lawful_road(self, monkeypatch):
        _board_env(monkeypatch)
        marshal = _stage("raised")
        [chip] = _road()
        yards = naval.controlled_dockyards(M.world, "France")
        lengths = {}
        for yard in yards:
            road, verdict = strategic.plot_route(M.world, marshal, yard,
                                                 use_weighted=True, want_verdict=True)
            if road and not strategic.issuance_road_refusal(
                    M.world, marshal, yard, "MOVE_TO", verdict):
                lengths[yard] = len(road)
        best = min(lengths, key=lambda y: (lengths[y], y))
        assert chip["command"] == f"{marshal.name}, march to {best}"
        assert best == "Normandy" and lengths[best] == 1
        assert chip["enabled"] is True

    def test_a_yard_the_road_law_refuses_is_not_offered(self, monkeypatch):
        """The march button asks the executor's own issuance gate: a yard
        whose road it would refuse is skipped for the next lawful one."""
        _board_env(monkeypatch)
        marshal = _stage("raised")
        real = strategic.issuance_road_refusal

        def refuse_normandy(world, m, destination, strategic_type, verdict):
            if destination == "Normandy":
                return {"success": False, "message": "no lawful corridor"}
            return real(world, m, destination, strategic_type, verdict)

        monkeypatch.setattr(strategic, "issuance_road_refusal", refuse_normandy)
        [chip] = _road()
        assert chip["command"].startswith(f"{marshal.name}, march to ")
        assert not chip["command"].endswith("Normandy")

    def test_landings_rank_enemy_shores_then_odds(self, monkeypatch):
        _board_env(monkeypatch)
        marshal = _stage("ready")
        chips = _road()
        assert 0 < len(chips) <= naval.EXPEDITION_CHIP_LANDINGS
        options = naval.expedition_landing_options(M.world, "France")
        rows = []
        for region, corps in options.items():
            holder = M.world.regions[region].controller
            enemy = bool(holder and holder != "France"
                         and M.world.is_at_war("France", holder))
            for c in corps:
                rows.append((0 if enemy else 1, -int(c["odds"]),
                             naval._grid_distance(M.world, c["from"], region),
                             region))
        best = sorted(rows)[:len(chips)]
        for chip, (_e, neg_odds, _dist, region) in zip(chips, best):
            assert chip["command"] == f"land {marshal.name} in {region}"
            assert chip["note"].startswith(f"{-neg_odds} in 100 slip past")
        # Enemy shores first: at the boot every best landing is Britain's.
        assert all(r[0] == 0 for r in best)
        assert len(rows) > len(chips), "the map offers more than the list"

    def test_the_emperor_is_never_the_counsel(self, monkeypatch):
        _board_env(monkeypatch)
        report = naval.build_admiralty_report(M.world)
        assert all("Napoleon" not in c["command"] for c in report["expedition_chips"])
        term = report["expedition_terms"][1]["detail"]
        assert "Napoleon's Guard is under the 15,000 lift" in term
        assert "the Emperor does not sail" in term
        assert "march Napoleon" not in term

    def test_the_lever_restores_the_old_term(self, monkeypatch):
        _board_env(monkeypatch)
        monkeypatch.setattr(naval, "THE_LIFT_COUNSEL_NAMES_THE_MARSHALATE", False)
        term = naval.build_admiralty_report(M.world)["expedition_terms"][1]["detail"]
        assert "march Napoleon (10,000) to a yard" in term

    def test_the_panel_names_the_real_road(self, monkeypatch):
        """The region panel's withheld landing chip said "march one there"
        at the boot, when the only corps under the lift is the Guard."""
        _board_env(monkeypatch)
        blocked = naval.expedition_blocked_reasons(M.world, "France")
        line = naval.no_small_corps_line(M.world, "France")
        at_war = [r for r, why in blocked.items()
                  if M.world.is_at_war("France", M.world.regions[r].controller)]
        assert at_war
        for region in at_war:
            assert blocked[region] == line, region
        assert "march one there" not in line


class TestTheLiftCounselNamesThePrice:

    def _soult_refusal(self, monkeypatch, price_lever=None):
        # None = the SHIPPED lever: setting it here would mask a flipped
        # default (the sweep caught exactly that — NUI2-24 read INERT).
        _board_env(monkeypatch)
        if price_lever is not None:
            monkeypatch.setattr(naval, "THE_LIFT_COUNSEL_NAMES_THE_PRICE", price_lever)
        soult = M.world.marshals["Soult"]
        return naval.over_lift_refusal(M.world, soult)

    def test_the_road_is_named_when_the_treasury_cannot_pay(self, monkeypatch):
        text = self._soult_refusal(monkeypatch)
        cand = recruitment.cheapest_commission_if_funded(M.world, "France")
        assert (f"Or, when the treasury allows, commission {cand['name']} — "
                f"5,000 men for {int(cand['cost']):,}g (we hold 800g)") in text

    def test_the_lever_restores_the_silence(self, monkeypatch):
        assert "commission" not in self._soult_refusal(monkeypatch, price_lever=False)

    def test_an_affordable_road_keeps_its_old_sentence(self, monkeypatch):
        _board_env(monkeypatch)
        M.world.nation_gold["France"] = 20000
        cand = recruitment.first_affordable_commission(M.world, "France")
        text = naval.over_lift_refusal(M.world, M.world.marshals["Soult"])
        assert f"Or commission {cand['name']} — 5,000 men for {int(cand['cost']):,}g" in text


class TestTheGateIsAskedNotCopied:

    def test_the_counterfactual_treasury(self):
        world = _scenario_world()
        cand = recruitment.cheapest_commission_if_funded(world, "France")
        cost = int(cand["cost"])
        assert recruitment.check_commission(world, "France", cand) is not None
        assert recruitment.check_commission(world, "France", cand, treasury=cost) is None
        assert recruitment.check_commission(world, "France", cand,
                                            treasury=cost - 1) is not None
        assert world.nation_gold["France"] == 800  # never touched

    def test_a_refusal_gold_cannot_fix_is_not_offered(self):
        world = _scenario_world()
        world.manpower_pools["France"] = {k: 0 for k in world.manpower_pools["France"]}
        assert recruitment.cheapest_commission_if_funded(world, "France") is None
        world.nation_gold["France"] = 50000
        assert recruitment.first_affordable_commission(world, "France") is None

    def test_the_cheapest_wins(self):
        world = _scenario_world()
        cand = recruitment.cheapest_commission_if_funded(world, "France")
        pool = recruitment.get_marshal_pool(world, "France")
        assert int(cand["cost"]) == min(int(c["cost"]) for c in pool)


class TestTheWordsTeachALandingThatSails:
    """The example was 'land Soult in Munster' — Soult's 30,000 are twice the
    transports' lift, so the help taught an order that always fails."""

    def test_the_help(self, monkeypatch):
        _board_env(monkeypatch)
        text = _post("help").get("message") or ""
        section = text[text.index("THE ADMIRALTY"):]
        assert "every order below" in section and "is a button there" in section
        # The form is written UNQUOTED: every quoted string in the help is
        # parsed as a command by the CX-3 manual census, and `<marshal>` is
        # not a marshal (the /debug block's convention).
        assert "land <marshal> in <province> (2 AP)" in section
        assert '"land <marshal>' not in section
        assert "our yards or from a foreign shore" in section
        assert "the Emperor does not sail" in section
        assert "land Soult" not in text

    def test_the_refusals_name_the_form(self, monkeypatch):
        _board_env(monkeypatch)
        naval_ex = M.executor._naval
        unnamed = naval_ex._execute_naval_expedition(
            {"marshal": ""}, {"world": M.world})["message"]
        assert "'land <marshal> in <province>'" in unnamed
        assert "THE ADMIRALTY (press T, then 7)" in unnamed
        assert "Soult" not in unnamed
        nowhere = naval_ex._execute_naval_expedition(
            {"marshal": "Lannes", "target": ""}, {"world": M.world})["message"]
        assert "'land Lannes in <a coastal province>'" in nowhere
        assert "Soult" not in nowhere


# ═══════════════════════════════════════════════════════════════════════════
# The client: the map draws the fleet at anchor; the tab opens with orders
# ═══════════════════════════════════════════════════════════════════════════
class TestTheClientReadsTheAnchor:

    def test_the_renderer_reads_the_port_anchor(self):
        source = _src(SCENES / "map_renderer_base.gd")
        assert 'region_data.has("port_anchor")' in source
        fleets = _func_body(source, "func _update_fleet_pieces() -> void:")
        assert "_fleet_anchor(station, positions)" in fleets
        assert "positions[station] + FLEET_PIECE_OFFSET" not in fleets
        glyphs = _func_body(source, "func _refresh_port_glyphs() -> void:")
        assert 'shape["port_anchor"] + PORT_GLYPH_BESIDE_SHIP' in glyphs

    def test_the_orders_come_first(self):
        block = _func_body(_src(SCRIPTS / "strategic_ledger.gd"),
                           "func _render_admiralty_block(adm: Dictionary) -> String:")
        assert block.index("_render_admiralty_orders(adm)") < block.index(
            'adm.get("continental_system")')
        assert block.count("_render_admiralty_orders(adm)") == 1

    def test_the_harness_is_named_for_the_parse_check(self):
        assert "res://../../tools/nui2_admiralty_harness.gd" in _src(
            REPO / "tools" / "godot_parse_check.gd")


@pytest.fixture(scope="module")
def boot_payloads():
    with pytest.MonkeyPatch.context() as mp:
        _board_env(mp)
        client = TestClient(M.app)
        with contextlib.redirect_stdout(io.StringIO()):
            test = client.get("/test").json()
            topology = client.get("/map_topology").json()
    return {"game_state": test["game_state"], "topology": topology}


@pytest.fixture(scope="module")
def driven_map(boot_payloads, tmp_path_factory):
    return _run_harness(REPO / "tools" / "nui_map_capture.gd", {
        "topology": boot_payloads["topology"],
        "game_state": boot_payloads["game_state"],
        "png": "",
        "settle": 30,
    }, tmp_path_factory.mktemp("nui2_map"), timeout=600)


class TestTheMapDrawsTheFleetAtAnchor:

    def test_every_fleet_stands_on_its_yard_s_port_anchor(self, driven_map, by_name):
        """The hitbox is the piece's rect in WORLD coords, rising from its
        base: the base is (x + w/2, y + h) — the registry's port anchor."""
        assert driven_map.get("error") is None, driven_map.get("error")
        assert driven_map["_script_errors"] == 0
        assert driven_map["fleet_hitboxes"], "no fleet was drawn"
        for box in driven_map["fleet_hitboxes"]:
            x, y, w, h = box["rect"]
            base = (x + w / 2.0, y + h)
            want = by_name[box["station"]]["port_anchor"]
            assert abs(base[0] - want[0]) < 0.05 and abs(base[1] - want[1]) < 0.05, (
                box["nation"], box["station"], base, want)


def _run_admiralty(boards, work):
    engine = _engine()
    if engine is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    out = work / "result.json"
    log = work / "godot.log"
    spec = work / "spec.json"
    spec.write_text(json.dumps({"boards": boards, "out": str(out)}), encoding="utf-8")
    env = dict(os.environ, NUI2_SPEC=str(spec), NUI2_OUT=str(out))
    proc = subprocess.run(
        [engine, "--headless", "--path", str(PROJECT), "--log-file", str(log),
         "--script", str(REPO / "tools" / "nui2_admiralty_harness.gd")],
        capture_output=True, text=True, timeout=300, env=env, cwd=str(PROJECT))
    if not out.is_file():
        pytest.fail(f"the harness wrote no result (exit={proc.returncode})\n"
                    f"{proc.stderr[-2000:]}")
    result = json.loads(out.read_text(encoding="utf-8"))
    log_text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    result["_script_errors"] = log_text.count("SCRIPT ERROR")
    return result


@pytest.fixture(scope="module")
def driven_tab(tmp_path_factory):
    boards = []
    with pytest.MonkeyPatch.context() as mp:
        for board in ("boot", "ready"):
            _board_env(mp)
            _stage(board)
            with contextlib.redirect_stdout(io.StringIO()):
                ledger = TestClient(M.app).get("/ledger").json()
            boards.append({"name": board, "ledger": ledger})
    return _run_admiralty(boards, tmp_path_factory.mktemp("nui2_tab"))


class TestTheAdmiraltyOpensWithItsOrders:

    def test_the_harness_ran_clean(self, driven_tab):
        assert driven_tab.get("error") is None, driven_tab.get("error")
        assert driven_tab["_script_errors"] == 0
        assert set(driven_tab["boards"]) == {"boot", "ready"}

    def test_the_orders_sit_above_the_report(self, driven_tab):
        text = driven_tab["boards"]["boot"]["text"]
        orders = text.index("Orders to the Admiralty")
        assert orders < text.index("The Continental System")
        assert orders < text.index("The Blockade Board")
        assert orders < text.index("The Crossings")
        assert text.index("Fleet: 45 sail of the line") < orders

    def test_the_boot_prices_the_commission_and_does_not_link_it(self, driven_tab):
        board = driven_tab["boards"]["boot"]
        assert "The expedition — the next step:" in board["text"]
        assert "Commission Oudinot (3,500g)" in board["text"]
        assert ("Commissioning Oudinot costs 3,500g — the treasury holds 800g."
                in board["text"])
        assert "[url=do:commission" not in board["bbcode"]  # dimmed, no link
        assert "[url=do:blockade the enemy]" in board["bbcode"]

    def test_a_ready_corps_is_offered_its_landings(self, driven_tab):
        board = driven_tab["boards"]["ready"]
        links = [seg.split("]", 1)[0] for seg in board["bbcode"].split("[url=do:land ")[1:]]
        assert 0 < len(links) <= naval.EXPEDITION_CHIP_LANDINGS
        assert all(link.startswith("Oudinot in ") for link in links)
        assert "or click any coastal province for another landing." in board["text"]
