"""NV-0 — The Admiralty substrate (docs/NAVAL_SPEC.md §11).

The ONE store (`world.fleets`), the authored 1805 navies, the four verbs'
first two (build_fleet / set_fleet_posture), the §3.3 readiness economy,
boot postures, the Admiralty upkeep component, N1 legacy dormancy, and the
mock-parser grammar. Anchors pinned here: the §3.2 authored table boots
exactly; ports-only rows are closure-denominator-only; every naval hook is
boot-zero on a fleet-less world by construction (the EC-W idiom).
"""

from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic import naval
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture
def world():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def executor():
    return CommandExecutor()


def _game_state(world):
    return {"world": world}


# ═══════════════════════════════════════════════════════════════════════════
# THE STORE — authored boot, serialization, dormancy
# ═══════════════════════════════════════════════════════════════════════════

class TestAuthoredBoot:
    def test_fifteen_navies_boot(self, world):
        # 10 fleets + 5 ports-only rows (§3.2)
        assert len([k for k in world.fleets if k != naval.META_KEY]) == 15

    def test_britain_boots_the_blockade(self, world):
        """§6: island fleet at war → blockade — the H2 rot begins at once."""
        rec = world.fleets["Britain"]
        assert rec["ships"] == 100
        assert rec["readiness"] == 100
        assert rec["posture"] == "blockade"
        assert rec["island"] is True
        assert rec["trade_dominance"] == 300

    def test_france_boots_guard_at_the_authored_rot(self, world):
        rec = world.fleets["France"]
        assert rec["ships"] == 45
        assert rec["readiness"] == 70   # Brest/Toulon, H2
        assert rec["posture"] == "guard"
        assert rec["camp_provinces"] == [
            "Flanders", "Artois", "Normandy", "Brittany"]

    def test_ports_only_rows_author_no_fleet_fields(self, world):
        for nation in ("Austria", "Prussia", "Hanover", "KingdomOfItaly",
                       "PapalStates"):
            rec = world.fleets[nation]
            assert rec["ships"] == 0
            assert "readiness" not in rec
            assert "posture" not in rec

    def test_continental_denominator_is_the_authored_26(self, world):
        assert naval.continental_ports_total(world) == 26

    def test_iter_fleets_skips_ports_only_and_meta(self, world):
        world.fleets[naval.META_KEY] = {"blockaded": []}
        nations = {n for n, _r in naval.iter_fleets(world)}
        assert "Austria" not in nations
        assert naval.META_KEY not in nations
        assert "Britain" in nations and len(nations) == 10

    def test_serialization_roundtrip_carries_the_store(self, world):
        world.fleets[naval.META_KEY] = {"blockaded": ["France"],
                                        "cs_tier": 0}
        world.fleets["France"]["camp_turns"] = 2
        reloaded = WorldState.from_dict(world.to_dict())
        assert reloaded.fleets == world.fleets

    def test_pre_naval_save_loads_dormant(self, world):
        data = world.to_dict()
        data.pop("fleets", None)
        reloaded = WorldState.from_dict(data)
        assert reloaded.fleets == {}
        assert not naval.has_naval_layer(reloaded)


class TestLegacyDormancy:
    """N1: the legacy fixture world authors no navies — every hook returns
    its dormant value in one truthiness read."""

    def test_legacy_world_has_no_naval_layer(self):
        legacy = WorldState(player_nation="France")
        assert legacy.fleets == {}
        assert not naval.has_naval_layer(legacy)
        assert naval.blockaded_nations(legacy) == []
        assert naval.ship_upkeep(legacy, "France") == 0
        assert naval.crossing_check(
            legacy, "France", "Paris", "Belgium")["allowed"] is True

    def test_legacy_income_has_zero_naval_components(self):
        legacy = WorldState(player_nation="France")
        income = legacy.calculate_turn_income("France")
        assert income["admiralty"] == 0
        result = legacy.process_income_phase("France")
        assert result["admiralty"] == 0

    def test_legacy_britain_naval_income_formula_intact(self):
        """The coastal-count literal survives byte-identically off-Europe."""
        legacy = WorldState(player_nation="France")
        income = legacy.calculate_turn_income("Britain")
        coastal = sum(
            1 for r in legacy.get_nation_regions("Britain")
            if getattr(legacy.regions.get(r), "is_coastal", False))
        assert income["breakdown"]["naval_income"] == min(
            300, 150 + 50 * coastal)


# ═══════════════════════════════════════════════════════════════════════════
# STRENGTH & POOLING (§3.1, H6)
# ═══════════════════════════════════════════════════════════════════════════

class TestPooling:
    def test_effective_strength_is_ships_times_readiness(self, world):
        assert naval.effective_strength(
            world.fleets["France"]) == pytest.approx(31.5)

    def test_the_combined_fleet_pools_at_the_allied_discount(self, world):
        """France + Spain (ally) + Holland (vassal... at boot Holland is at
        war with Britain and France-linked) against Britain — H6's ×0.8."""
        pooled = naval.combined_effective(world, "France", "Britain")
        own = 45 * 0.70
        assert pooled > own
        # Spain (30×0.65) and Holland (12×0.70) both discount at 0.8.
        expected_partners = 0.8 * (30 * 0.65) + 0.8 * (12 * 0.70)
        assert pooled == pytest.approx(own + expected_partners, abs=0.6)

    def test_a_neutral_fleet_never_pools(self, world):
        # Denmark is at peace with everyone: no side may count it.
        pooled = naval.combined_effective(world, "France", "Britain")
        world.fleets["Denmark"]["ships"] = 0
        assert naval.combined_effective(
            world, "France", "Britain") == pytest.approx(pooled)


# ═══════════════════════════════════════════════════════════════════════════
# THE ADMIRALTY COMPONENT (N3) — war upkeep, "laid up in ordinary" at peace
# ═══════════════════════════════════════════════════════════════════════════

class TestShipUpkeep:
    def test_war_upkeep_bills_2g_per_ship(self, world):
        assert naval.ship_upkeep(world, "France") == 90
        assert naval.ship_upkeep(world, "Britain") == 200

    def test_peacetime_fleets_are_laid_up(self, world):
        # Denmark boots at peace — zero upkeep is why fleet-holding minors
        # never bankrupt (§6).
        assert naval.ship_upkeep(world, "Denmark") == 0
        assert naval.ship_upkeep(world, "Sweden") == 0

    def test_admiralty_rides_the_income_phase(self, world):
        income = world.calculate_turn_income("France")
        assert income["admiralty"] == 90
        result = world.process_income_phase("France")
        assert result["admiralty"] == 90
        assert "admiralty" in result["breakdown"]

    def test_admiralty_reduces_net(self, world):
        # EB-1/EB-5a/EB-2 re-bless: war_effort became state_charges, and
        # the two positive components (requisitions, overseas) joined the
        # applied-net identity.
        result = world.process_income_phase("France")
        recomputed = (result["income"] + result["requisitions"]
                      + result["overseas"] - result["occupation"]
                      - result["contributions"] - result["state_charges"]
                      - result["dotation_skim"] - result["rente_cost"]
                      - result["infrastructure"] - result["admiralty"]
                      - result["upkeep"] + result["admin_bonus"])
        assert result["net"] == recomputed


# ═══════════════════════════════════════════════════════════════════════════
# READINESS (§3.3 — the whole H2 economy in four rules)
# ═══════════════════════════════════════════════════════════════════════════

class TestReadinessTick:
    def test_blockaded_fleet_rots_to_the_floor(self, world):
        """France under Britain's boot blockade decays −5/turn to 50."""
        for _ in range(6):
            naval._readiness_tick(world)
        assert world.fleets["France"]["readiness"] == naval.READINESS_BLOCKADE_FLOOR

    def test_blockading_fleet_holds_100(self, world):
        naval._readiness_tick(world)
        assert world.fleets["Britain"]["readiness"] == 100

    def test_war_drill_ceiling_75_vs_a_superior_hostile_fleet(self, world):
        """v1.0.3: when Britain guards (blockade lifted), France recovers —
        but only to 75. Waiting alone can never open the Strait."""
        world.fleets["Britain"]["posture"] = "guard"
        world.fleets["France"]["readiness"] = 50
        for _ in range(20):
            naval._readiness_tick(world)
        assert world.fleets["France"]["readiness"] == naval.NAVY_DRILL_CEILING

    def test_peace_recovers_to_100(self, world):
        # Give France full peace: end its wars.
        for enemy in list(world.get_nations_at_war_with("France")):
            world.diplomatic_states[world._make_diplo_key("France", enemy)] = "PEACE"
        world.invalidate_active_nations_cache()
        world.fleets["France"]["readiness"] = 50
        for _ in range(20):
            naval._readiness_tick(world)
        assert world.fleets["France"]["readiness"] == 100

    def test_the_superior_fleet_itself_keeps_100(self, world):
        world.fleets["Britain"]["posture"] = "guard"
        naval._readiness_tick(world)
        assert world.fleets["Britain"]["readiness"] == 100


# ═══════════════════════════════════════════════════════════════════════════
# BUILD (N2 — the §3.5 three brakes) + the verbs
# ═══════════════════════════════════════════════════════════════════════════

class TestBuildFleet:
    def test_build_costs_gold_and_folds_green_crews(self, world, executor):
        world.nation_gold["France"] = 2000
        ships0 = world.fleets["France"]["ships"]
        r0 = world.fleets["France"]["readiness"]
        result = executor._naval._execute_build_fleet(
            {"marshal": None, "action": "build_fleet"}, _game_state(world))
        assert result["success"], result["message"]
        assert world.nation_gold["France"] == 2000 - naval.SHIP_COST
        rec = world.fleets["France"]
        assert rec["ships"] == ships0 + 1
        expected = int(round((ships0 * r0 + naval.NEW_SHIP_READINESS)
                             / (ships0 + 1)))
        assert rec["readiness"] == expected  # bigger and worse at once

    def test_rate_cap_is_the_time_wall(self, world, executor):
        """§3.5 brake 1 — and brake 2: a blockaded nation builds at 1."""
        world.nation_gold["France"] = 5000
        gs = _game_state(world)
        # France is blockaded at boot → rate 1.
        assert naval.build_rate(world, "France") == naval.SHIP_BUILD_RATE_BLOCKADED
        assert executor._naval._execute_build_fleet(
            {"action": "build_fleet"}, gs)["success"]
        second = executor._naval._execute_build_fleet(
            {"action": "build_fleet"}, gs)
        assert not second["success"]
        assert "capacity" in second["message"]

    def test_unblockaded_rate_is_two(self, world, executor):
        world.nation_gold["Britain"] = 5000
        gs = _game_state(world)
        for i in range(2):
            result = executor._naval._execute_build_fleet(
                {"action": "build_fleet", "_acting_nation": "Britain"}, gs)
            assert result["success"], result["message"]
        third = executor._naval._execute_build_fleet(
            {"action": "build_fleet", "_acting_nation": "Britain"}, gs)
        assert not third["success"]

    def test_no_yard_no_ship(self, world, executor):
        """§3.4a: build rights follow CONTROL of a dockyard province."""
        for prov in world.fleets["France"]["dockyards"]:
            world.regions[prov].controller = "Britain"
        world.invalidate_active_nations_cache()
        world.nation_gold["France"] = 2000
        result = executor._naval._execute_build_fleet(
            {"action": "build_fleet"}, _game_state(world))
        assert not result["success"]
        assert "dockyard" in result["message"]

    def test_conquering_a_yard_grants_the_yard_never_ships(self, world, executor):
        """§3.4a ruling: Austria (ports-only) takes Venice—well, Naples'
        yard — and may found a navy there. Ships never change hands."""
        world.regions["Naples"].controller = "Austria"
        world.invalidate_active_nations_cache()
        world.nation_gold["Austria"] = 2000
        naples_ships = world.fleets["Naples"]["ships"]
        result = executor._naval._execute_build_fleet(
            {"action": "build_fleet", "_acting_nation": "Austria"},
            _game_state(world))
        assert result["success"], result["message"]
        assert world.fleets["Austria"]["ships"] == 1
        assert world.fleets["Austria"]["readiness"] == naval.NEW_SHIP_READINESS
        assert world.fleets["Naples"]["ships"] == naples_ships

    def test_a_court_with_no_navies_row_cannot_conjure_one(self, executor):
        legacy = WorldState(player_nation="France")
        result = executor._naval._execute_build_fleet(
            {"action": "build_fleet"}, _game_state(legacy))
        assert not result["success"]

    def test_build_fleet_is_an_admin_action(self):
        from backend.commands.meta_executor import ADMIN_ACTIONS
        assert "build_fleet" in ADMIN_ACTIONS


class TestSetFleetPosture:
    def test_blockade_order(self, world, executor):
        result = executor._naval._execute_set_fleet_posture(
            {"action": "set_fleet_posture",
             "raw_command": "blockade the enemy"}, _game_state(world))
        assert result["success"]
        assert world.fleets["France"]["posture"] == "blockade"

    def test_guard_order(self, world, executor):
        world.fleets["France"]["posture"] = "blockade"
        result = executor._naval._execute_set_fleet_posture(
            {"action": "set_fleet_posture",
             "raw_command": "guard home waters"}, _game_state(world))
        assert result["success"]
        assert world.fleets["France"]["posture"] == "guard"

    def test_structured_field_wins(self, world, executor):
        result = executor._naval._execute_set_fleet_posture(
            {"action": "set_fleet_posture", "posture": "blockade",
             "raw_command": "guard home waters"}, _game_state(world))
        assert result["success"]
        assert world.fleets["France"]["posture"] == "blockade"

    def test_no_fleet_refusal(self, world, executor):
        result = executor._naval._execute_set_fleet_posture(
            {"action": "set_fleet_posture", "_acting_nation": "Austria",
             "raw_command": "blockade them"}, _game_state(world))
        assert not result["success"]


# ═══════════════════════════════════════════════════════════════════════════
# AI (§6): derived postures + the build rung
# ═══════════════════════════════════════════════════════════════════════════

class TestAIDerivation:
    def test_island_doctrine_blockades_at_war(self, world):
        naval.derive_ai_postures(world)
        assert world.fleets["Britain"]["posture"] == "blockade"

    def test_peace_returns_to_guard(self, world):
        for enemy in list(world.get_nations_at_war_with("Britain")):
            world.diplomatic_states[world._make_diplo_key("Britain", enemy)] = "PEACE"
        world.invalidate_active_nations_cache()
        naval.derive_ai_postures(world)
        assert world.fleets["Britain"]["posture"] == "guard"

    def test_player_posture_is_never_derived(self, world):
        world.fleets["France"]["posture"] = "blockade"
        naval.derive_ai_postures(world)
        assert world.fleets["France"]["posture"] == "blockade"

    def test_ai_build_rung_fires_on_the_blockaded(self, world):
        # France is blockaded and at war: an AI France would lay down ships.
        order = naval.find_ai_build_fleet(world, "France", treasury=2000)
        assert order is not None
        assert order["action"] == "build_fleet"
        assert order["_acting_nation"] == "France"

    def test_ai_build_rung_respects_peace_and_poverty(self, world):
        assert naval.find_ai_build_fleet(world, "Denmark", 99999) is None
        assert naval.find_ai_build_fleet(world, "France", 500) is None


# ═══════════════════════════════════════════════════════════════════════════
# THE MOCK GRAMMAR (§9 typed grammar — corpus sources point here)
# ═══════════════════════════════════════════════════════════════════════════

class TestNavalVerbParsing:
    @pytest.fixture
    def parse(self, world):
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        gs = {"world": world,
              "marshals": {m.name: m for m in
                           world.get_marshals_by_nation("France")}}

        def _parse(text):
            return client._parse_with_mock(text, gs)
        return _parse

    def test_build_ships_parses(self, parse):
        assert parse("build ships").action == "build_fleet"

    def test_raise_a_fleet_parses(self, parse):
        assert parse("raise a fleet").action == "build_fleet"

    def test_blockade_parses(self, parse):
        assert parse("blockade Britain").action == "set_fleet_posture"

    def test_guard_home_waters_parses(self, parse):
        assert parse("guard home waters").action == "set_fleet_posture"

    def test_land_grant_stays_on_the_vassal_path(self, parse):
        # 'grant land to X' / 'hold the land between' never become
        # expeditions (the two-word-window regex).
        result = parse("Ney, hold the land between the rivers")
        assert result.action != "naval_expedition"

    def test_recruit_stays_recruit(self, parse):
        assert parse("raise conscripts").action == "recruit"


# ═══════════════════════════════════════════════════════════════════════════
# THE VALIDATOR (§8 — the gate, runtime never re-clamps)
# ═══════════════════════════════════════════════════════════════════════════

class TestNaviesValidator:
    def _scenario(self, navies):
        import json
        base = json.load(open(SCENARIO_PATH, encoding="utf-8"))
        base["navies"] = navies
        return base

    def _validate(self, navies):
        from backend.modding.validator import validate_scenario
        import json
        base = json.load(open(SCENARIO_PATH, encoding="utf-8"))
        # Inject regions the way from_scenario does, so dockyard checks see
        # controllers.
        from backend.models.region import create_europe_regions, get_europe_starting_controllers
        regions = create_europe_regions()
        controllers = get_europe_starting_controllers()
        base["regions"] = {}
        for name, region in regions.items():
            d = region.to_dict()
            d["controller"] = controllers.get(name)
            base["regions"][name] = d
        base["navies"] = navies
        return validate_scenario(base, check_adjacency=False)

    def test_shipped_block_validates(self, world):
        import json
        shipped = json.load(open(SCENARIO_PATH, encoding="utf-8"))["navies"]
        assert self._validate(shipped).is_valid

    def test_ports_only_row_must_not_author_readiness(self):
        result = self._validate({"Austria": {"ships": 0, "readiness": 80,
                                             "ports": 1}})
        assert not result.is_valid

    def test_unknown_dockyard_rejected(self):
        result = self._validate({"France": {"ships": 10, "readiness": 70,
                                            "dockyards": ["Atlantis"]}})
        assert not result.is_valid

    def test_foreign_dockyard_rejected(self):
        result = self._validate({"France": {"ships": 10, "readiness": 70,
                                            "dockyards": ["London"]}})
        assert not result.is_valid

    def test_ships_range_clamped(self):
        assert not self._validate({"France": {"ships": 999,
                                              "readiness": 70}}).is_valid
        assert not self._validate({"France": {"ships": 10,
                                              "readiness": 20}}).is_valid
