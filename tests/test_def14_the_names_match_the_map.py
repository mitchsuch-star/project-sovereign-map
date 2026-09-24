"""DEF-14 — "The Names Match the Map" (September 24, 2026; user-directed:
*"fix province names commit and push"*). Landing record:
`docs/MAP_IMPLEMENTATION_PLAN.md` DEF-14.

The art is a stylised Europe, and Slice 2 authored historical names onto an
auto-generated draft. NUI-2's coast audit found names on the wrong ground:
Norway's "Bergen" and "Oslo" on the peninsula the art attaches to Germany,
Sweden's "Scania" on the German Baltic coast, "Dalarna" beside the Danish
peninsula, Sweden's "Norrland" on the Finnish landmass, an inland "Toledo"
on Spain's Mediterranean shore and an inland "La Mancha" on its south coast.

`tools/audit_province_names.py` makes that measurable: each name's real
coordinates are fitted, by a local affine transform, to where its
neighbours sit in the art. Nine provinces were renamed — owners, shapes,
adjacency, yards and capitals unchanged, so the game plays identically — and
every remaining outlier is a recorded stylisation with its reason.

  Region_072  Bergen    -> Jutland      Region_095  Scania    -> Stralsund
  Region_097  Oslo      -> Schleswig    Region_041  Gothland  -> Norrland
  Region_096  Jutland   -> Holstein     Region_013  Norrland  -> Uleaborg
  Region_113  Dalarna   -> Scania       Region_071  Toledo    -> Cartagena
                                        Region_049  La Mancha -> Andalusia

Three names were REUSED for a different region, so an old save is renamed
simultaneously, before `from_dict` (world_state.rename_provinces_in_save_data).
"""

import contextlib
import copy
import io
import json
from pathlib import Path

import pytest

from backend.models import world_state as ws
from backend.models.world_state import WorldState
from tools import audit_province_names as apn

REPO = Path(__file__).resolve().parents[1]
MAPS = REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
REGISTRY = MAPS / "europe.json"
SCENARIO = MAPS / "europe_1805.json"
OLD_FIXTURE = REPO / "tests" / "fixtures" / "playtest_saves" / "fixture_t10_ambient.json"

# The nine renamed regions, by id: (old name, new name).
RENAMED_BY_ID = {
    "Region_072": ("Bergen", "Jutland"),
    "Region_097": ("Oslo", "Schleswig"),
    "Region_096": ("Jutland", "Holstein"),
    "Region_113": ("Dalarna", "Scania"),
    "Region_095": ("Scania", "Stralsund"),
    "Region_041": ("Gothland", "Norrland"),
    "Region_013": ("Norrland", "Uleaborg"),
    "Region_071": ("Toledo", "Cartagena"),
    "Region_049": ("La Mancha", "Andalusia"),
}
OWNERS_BY_ID = {
    "Region_072": "Denmark", "Region_097": "Denmark", "Region_096": "Denmark",
    "Region_113": "Sweden", "Region_095": "Sweden", "Region_041": "Sweden",
    "Region_013": "Sweden", "Region_071": "Spain", "Region_049": "Spain",
}
PRE_RENAME_ONLY = {"Bergen", "Oslo", "Dalarna", "Gothland", "Toledo", "La Mancha"}
# The retired names' real places, for re-running the audit on the old map.
RETIRED_GAZETTEER = {
    "Bergen": (5.3, 60.4), "Oslo": (10.75, 59.9), "Dalarna": (14.5, 61.0),
    "Gothland": (14.0, 57.8), "Toledo": (-4.0, 39.9), "La Mancha": (-3.0, 39.2),
}


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(scope="module")
def registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def names(registry):
    return {e["name"] for e in registry["regions"].values()}


def _scenario_world():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


def _old_registry(registry):
    old = copy.deepcopy(registry)
    for rid, (old_name, _new) in RENAMED_BY_ID.items():
        old["regions"][rid]["name"] = old_name
    return old


# ═══════════════════════════════════════════════════════════════════════════
# The registry carries the new names — and only the names moved
# ═══════════════════════════════════════════════════════════════════════════
class TestTheRegistryIsRenamed:

    def test_the_nine_regions_carry_their_new_names(self, registry):
        for rid, (_old, new) in RENAMED_BY_ID.items():
            assert registry["regions"][rid]["name"] == new, rid

    def test_no_pre_rename_only_name_survives(self, names):
        assert not (PRE_RENAME_ONLY & names), PRE_RENAME_ONLY & names

    def test_names_are_unique(self, registry):
        all_names = [e["name"] for e in registry["regions"].values()]
        assert len(all_names) == len(set(all_names))

    def test_owners_did_not_move(self, registry):
        """The names moved; the political map did not."""
        for rid, owner in OWNERS_BY_ID.items():
            assert registry["regions"][rid]["starting_controller"] == owner, rid

    def test_the_save_table_agrees_with_the_registry(self, names):
        """`world_state.RENAMED_PROVINCES` is the same nine renames, and its
        derived pre-rename-only set is exactly the names no save written
        since can carry."""
        table = {old: new for old, new in RENAMED_BY_ID.values()}
        assert ws.RENAMED_PROVINCES == table
        assert set(ws._PRE_RENAME_ONLY) == PRE_RENAME_ONLY
        assert set(table.values()) <= names

    def test_the_rename_is_recorded_in_the_registry(self, registry):
        note = registry["adjacency_derivation"]["def14_rename"]
        for old, new in RENAMED_BY_ID.values():
            assert old in note and new in note, (old, new)


# ═══════════════════════════════════════════════════════════════════════════
# The audit: every outlier renamed or recorded
# ═══════════════════════════════════════════════════════════════════════════
class TestTheAuditHolds:

    def test_the_gazetteer_is_exactly_the_registry(self, names):
        assert set(apn.GAZETTEER) == names

    def test_every_outlier_is_recorded(self):
        assert apn.unrecorded_outliers() == []

    def test_no_renamed_province_is_an_outlier(self):
        rows = {r["name"]: r for r in apn.audit()}
        for _old, new in RENAMED_BY_ID.values():
            assert rows[new]["score"] < apn.THRESHOLD, (new, rows[new]["score"])

    def test_the_old_names_were_outliers(self, registry, monkeypatch):
        """The audit re-run on the map as it was: Bergen and Dalarna were
        outliers, and neither's region is one now.

        MEASURED, and it corrected a claim made while building this slice
        ("the renames created no outlier"): two outliers appear that were
        not there before — Westphalia and East Frisia. Neither their regions
        nor their names changed; their NEIGHBOURHOOD did. Each fit reads the
        ten nearest provinces in the art, and both neighbourhoods included
        the misnamed "Oslo", whose real latitude (60 N) at the Jutland neck
        bent the old fit into discarding Friesland, Artois and East Frisia
        as its misfits — which happened to put Westphalia near its anchor
        (the trim sets were checked, not assumed). Named Schleswig (54.6 N),
        that neighbour fits; the fit discards the Dutch provinces instead
        and sees what the old one could not: the art interleaves Hanover's
        North Sea lands with Holland's (Westphalia and East Frisia painted
        west of Amsterdam, which lies west of them). Both are recorded
        stylisations owned by DEF-15."""
        monkeypatch.setattr(apn, "GAZETTEER", {**apn.GAZETTEER, **RETIRED_GAZETTEER})
        old_outliers = set(apn.outliers(apn.audit(_old_registry(registry))))
        new_outliers = set(apn.outliers(apn.audit(registry)))
        assert {"Bergen", "Dalarna"} <= old_outliers, old_outliers
        renamed = {new for _old, new in RENAMED_BY_ID.values()}
        assert not (new_outliers & renamed), new_outliers & renamed
        surfaced = new_outliers - old_outliers
        assert surfaced == {"Westphalia", "East Frisia"}, surfaced
        for name in surfaced:
            assert apn.STYLISED[name][0] == "outlier"
            assert "DEF-15" in apn.STYLISED[name][1]

    def test_the_stylisation_table_is_honest(self, names):
        """Every entry is a province on the map, not one of the renamed
        nine, carries a reason, and an entry that says it is an outlier
        really is one — a stale 'outlier' would be a claim the map no
        longer supports."""
        rows = {r["name"]: r for r in apn.audit()}
        renamed = {new for _old, new in RENAMED_BY_ID.values()}
        for name, (kind, reason) in apn.STYLISED.items():
            assert name in names, name
            assert name not in renamed, name
            assert kind in ("outlier", "art"), (name, kind)
            assert len(reason) > 20, name
            if kind == "outlier":
                assert rows[name]["score"] >= apn.THRESHOLD, (name, rows[name]["score"])

    def test_the_cli_check_passes(self):
        with _quiet():
            assert apn.main(["--check"]) == 0


# ═══════════════════════════════════════════════════════════════════════════
# The scenario follows its regions
# ═══════════════════════════════════════════════════════════════════════════
class TestTheScenarioFollowsItsRegions:

    def test_the_scenario_names_no_retired_province(self):
        text = SCENARIO.read_text(encoding="utf-8")
        data = json.loads(text)
        blob = json.dumps({k: v for k, v in data.items() if not k.startswith("_")})
        for old in PRE_RENAME_ONLY:
            assert f'"{old}"' not in blob, old

    def test_the_marshals_stand_on_the_same_ground(self):
        world = _scenario_world()
        # Armfelt's army stood in Swedish Pomerania in 1805; Frederick's in
        # Holstein (his own biography says so); Castanos was Andalusia's.
        assert world.marshals["Armfelt"].location == "Stralsund"
        assert world.marshals["Frederick"].location == "Holstein"
        assert world.marshals["Castanos"].location == "Andalusia"

    def test_the_yards_did_not_move(self):
        from backend.game_logic import naval
        world = _scenario_world()
        assert naval.controlled_dockyards(world, "Sweden") == ["Stralsund"]
        assert naval.controlled_dockyards(world, "Spain") == ["Cartagena", "Galicia"]
        assert world.fleets["Spain"]["dockyards"] == ["Galicia", "Cartagena"]

    def test_spains_fleet_now_rides_at_cartagena(self):
        """CONSCIOUS, display only. The station a fleet piece is drawn at is
        its senior yard, `controlled_dockyards(...)[0]`, which is ALPHABETICAL
        (NAVAL_SPEC §17.1). "Cartagena" sorts before "Galicia", where
        "Toledo" did not, so Spain's piece is drawn off Cartagena now: the
        same two yards, and no mechanic reads the order. (It could not be
        named "Murcia", which sorts after Galicia: that scores 73 against
        Marshal Murat, inside the WO-13 typo band.)"""
        from backend.game_logic import naval
        world = _scenario_world()
        stations = {f["nation"]: f["station"] for f in naval.fleet_pieces(world)}
        assert stations["Spain"] == "Cartagena"
        assert stations["Sweden"] == "Stralsund"

    def test_denmark_guards_the_same_province(self):
        data = json.loads(SCENARIO.read_text(encoding="utf-8"))
        deck = data["agendas"]["Denmark"]
        guard = next(e for e in deck if e["id"] == "neutrality_of_the_north")
        assert guard["regions"] == ["Holstein", "Copenhagen"]

    def test_every_renamed_province_resolves_at_boot(self):
        world = _scenario_world()
        for rid, (_old, new) in RENAMED_BY_ID.items():
            region = world.regions[new]
            assert region.controller == OWNERS_BY_ID[rid], new
        for old in PRE_RENAME_ONLY:
            assert old not in world.regions, old


# ═══════════════════════════════════════════════════════════════════════════
# An old save is renamed on load
# ═══════════════════════════════════════════════════════════════════════════
def _raw_old_world():
    return json.loads(OLD_FIXTURE.read_text(encoding="utf-8"))["world_state"]


def _strings(node):
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(k, str):
                yield k
            yield from _strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from _strings(v)
    elif isinstance(node, str):
        yield node


class TestAnOldSaveIsRenamed:

    def test_the_committed_fixture_is_an_old_save(self):
        assert PRE_RENAME_ONLY & set(_raw_old_world()["regions"])

    def test_no_retired_name_survives_anywhere(self):
        data = _raw_old_world()
        assert ws.rename_provinces_in_save_data(data) > 0
        leftovers = [s for s in _strings(data)
                     if s in PRE_RENAME_ONLY
                     or ("|" in s and PRE_RENAME_ONLY & set(s.split("|")))]
        assert leftovers == []

    def test_each_region_keeps_its_own_ground(self, registry):
        """The chained names land on their own regions: the old Scania's
        data is Stralsund's, the old Dalarna's is Scania's, the old
        Jutland's is Holstein's, the old Bergen's is Jutland's. Read off each
        region's saved adjacency, which must equal the registry's."""
        by_name = {e["name"]: e for e in registry["regions"].values()}
        id_to_name = {rid: e["name"] for rid, e in registry["regions"].items()}
        data = _raw_old_world()
        ws.rename_provinces_in_save_data(data)
        for _old, new in RENAMED_BY_ID.values():
            saved = set(data["regions"][new]["adjacent_regions"])
            live = {id_to_name[a] for a in by_name[new]["adjacent"]}
            assert saved == live, (new, saved, live)

    def test_the_fixture_loads_on_the_new_map(self):
        from backend.save_manager import load_game
        with _quiet():
            result = load_game(OLD_FIXTURE)
        assert result["success"], result["message"]
        world = result["world"]
        assert not (PRE_RENAME_ONLY & set(world.regions))
        assert world.marshals["Armfelt"].location == "Stralsund"
        assert world.fleets["Sweden"]["dockyards"] == ["Stralsund"]
        assert world.fleets["Spain"]["dockyards"] == ["Galicia", "Cartagena"]
        # The NUI-2 reconcile ran too — it only runs on a world whose every
        # province the registry knows, which the rename made true.
        assert world.fleets["Holland"]["dockyards"] == ["Friesland"]

    def test_the_rename_is_simultaneous(self):
        data = {"regions": {"Jutland": {"name": "Jutland"},
                            "Bergen": {"name": "Bergen"},
                            "Scania": {"name": "Scania"},
                            "Dalarna": {"name": "Dalarna"}},
                "marshals": {"Frederick": {"location": "Jutland"},
                             "Armfelt": {"location": "Scania"}}}
        ws.rename_provinces_in_save_data(data)
        assert data["regions"] == {"Holstein": {"name": "Holstein"},
                                   "Jutland": {"name": "Jutland"},
                                   "Stralsund": {"name": "Stralsund"},
                                   "Scania": {"name": "Scania"}}
        assert data["marshals"]["Frederick"]["location"] == "Holstein"
        assert data["marshals"]["Armfelt"]["location"] == "Stralsund"

    def test_a_naval_crossing_key_is_renamed_and_resorted(self):
        # "Gothland|Lapland" is the case the re-sort exists for: renamed part
        # by part it reads "Norrland|Lapland", and a crossing key is sorted.
        data = {"regions": {"Oslo": {}},
                "fleets": {"__naval__": {"verdicts": {
                    "Jutland|Oslo": "shut",
                    "Copenhagen|Scania": "open",
                    "Gothland|Lapland": "open",
                    "London|Normandy": "shut",
                }}}}
        ws.rename_provinces_in_save_data(data)
        assert data["fleets"]["__naval__"]["verdicts"] == {
            "Holstein|Schleswig": "shut",
            "Copenhagen|Stralsund": "open",
            "Lapland|Norrland": "open",
            "London|Normandy": "shut",
        }

    def test_prose_is_history_and_is_left_as_written(self):
        data = {"regions": {"Oslo": {}},
                "event_log": [{"message": "Frederick holds Jutland",
                               "region": "Jutland"}]}
        ws.rename_provinces_in_save_data(data)
        assert data["event_log"] == [{"message": "Frederick holds Jutland",
                                      "region": "Holstein"}]

    def test_a_new_save_is_untouched(self):
        """The reused names (Jutland, Scania, Norrland) must NOT be moved
        again in a save written since: that would chain them onto the wrong
        ground."""
        world = _scenario_world()
        data = world.to_dict()
        before = json.dumps(data, sort_keys=True, default=str)
        assert ws.rename_provinces_in_save_data(data) == 0
        assert json.dumps(data, sort_keys=True, default=str) == before

    def test_a_migrated_save_round_trips(self, tmp_path):
        from backend.save_manager import load_game, save_game
        with _quiet():
            world = load_game(OLD_FIXTURE)["world"]
            path = tmp_path / "renamed.json"
            assert save_game(world, "def14", filepath=path)["success"]
            again = load_game(path)["world"]
        assert set(again.regions) == set(world.regions)
        assert again.marshals["Frederick"].location == world.marshals["Frederick"].location

    def test_a_legacy_world_is_never_touched(self):
        data = {"regions": {"Paris": {}, "Vienna": {}}, "note": "Oslo"}
        assert ws.rename_provinces_in_save_data(data) == 0
        assert data["note"] == "Oslo"


# ═══════════════════════════════════════════════════════════════════════════
# The player can type the new names
# ═══════════════════════════════════════════════════════════════════════════
@pytest.fixture(scope="module")
def board():
    from backend.ai.parser_eval import build_llm_game_state, build_world
    from backend.commands.parser import CommandParser
    with _quiet():
        world = build_world("1805")
        state = build_llm_game_state(world)
        parser = CommandParser(use_real_llm=False)
    return world, state, parser


class TestThePlayerCanTypeTheNewNames:

    @pytest.mark.parametrize("province", [
        "Jutland", "Schleswig", "Holstein", "Scania", "Stralsund",
        "Norrland", "Uleaborg", "Cartagena", "Andalusia",
    ])
    def test_a_march_order_resolves_the_new_name(self, board, province):
        """"Andalusia" begins with "and" and "Holstein" is one letter-group
        from "Holland" (a nation): neither may be split or swapped."""
        world, state, parser = board
        with _quiet():
            result = parser.parse(f"Ney, march to {province}", state, world=world)
        command = result.get("command") or {}
        assert command.get("target") == province, (province, command)


# ═══════════════════════════════════════════════════════════════════════════
# A title is not a name
# ═══════════════════════════════════════════════════════════════════════════
@pytest.fixture
def shipped(monkeypatch):
    """A fresh shipped 1805 world behind `/command`, with a keyless parser."""
    import backend.main as M
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient

    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    with _quiet():
        M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False
    return TestClient(M.app), M


class TestATitleIsNotAName:
    """The word after "of" in "the Prince of Moskowa" is the territory of a
    TITLE, not a marshal's name, so the parser's word scan leaves the address
    to the executor's unbound-addressee refusal, which names what the player
    typed (CX-R1, L2-3). Until DEF-14, "Moskowa" reached that refusal only
    by accident: it fuzzy-matched the province "Oslo" (75). "Elchingen"
    never had the accident and got the worse question "There is no Marshal
    'Elchingen'"."""

    TITLES = [
        ("Prince of Moskowa, attack Mack", "Prince of Moskowa"),
        ("the Prince of Moskowa attack Mack", "Prince of Moskowa"),
        ("Duke of Elchingen, attack Mack", "Duke of Elchingen"),
        ("the Duke of Auerstaedt, attack Mack", "Duke of Auerstaedt"),
    ]

    @pytest.mark.parametrize("command,address", TITLES)
    def test_the_whole_title_is_refused_by_name(self, shipped, command, address):
        client, M = shipped
        ap_before = M.world.actions_remaining
        with _quiet():
            reply = client.post("/command", json={"command": command}).json()
        assert reply.get("success") is False, reply.get("message")
        assert reply.get("kind") == "marshal_not_found"
        assert not reply.get("clarification_kind"), reply.get("clarification_kind")
        assert f"no '{address}' in the order of battle" in (reply.get("message") or "")
        assert not reply.get("battle_report")
        assert M.world.actions_remaining == ap_before

    def test_a_bare_unknown_name_is_still_asked_about(self, shipped):
        """The control: the rule reads the word before, so an addressed
        unknown name with no "of" keeps the CR-2 question."""
        client, _M = shipped
        with _quiet():
            reply = client.post("/command", json={"command": "Moskowa, attack Mack"}).json()
        assert reply.get("clarification_kind") == "unknown_name", reply
        assert "no Marshal 'Moskowa'" in (reply.get("message") or "")
