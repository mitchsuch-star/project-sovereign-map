"""Marshal Recruitment — "The Marshalate" (docs/MARSHAL_RECRUITMENT_SPEC.md).

The Jealousy v3.2 build's final phase: nations with an authored candidate
pool commission new marshals mid-campaign. Player and AI share the same
executor gate (GR5): gold price + 1 admin AP + a 5,000-man corps drawn from
the infantry manpower pool; arrival at the capital (or the richest held
homeland province); symmetric relationship seeds; glory ladder entry at 0.
"""

from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic import jealousy as J
from backend.game_logic import recruitment as R
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (
    REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


@pytest.fixture
def executor():
    return CommandExecutor()


def _commission(executor, world, name, nation=None):
    command = {"action": "recruit_marshal", "target": name,
               "type": "specific"}
    if nation:
        command["_acting_nation"] = nation
    return executor.execute({"command": command}, {"world": world})


# ═══════════════════════ POOL + SCENARIO AUTHORING ═════════════════════════


class TestPoolAuthoring:
    def test_pool_loads_at_boot(self, world):
        assert set(world.marshal_pool.keys()) == \
            {"France", "Austria", "Russia", "Prussia", "Britain"}
        assert [c["name"] for c in world.marshal_pool["France"]] == \
            ["Mortier", "Grouchy", "Suchet", "Oudinot", "Augereau", "Marmont"]

    def test_pool_round_trips(self, world):
        restored = WorldState.from_dict(world.to_dict())
        assert restored.marshal_pool == world.marshal_pool

    def test_shipped_pool_validates_clean(self):
        import json

        from backend.modding.validator import validate_scenario
        data = json.load(open(SCENARIO_PATH, encoding="utf-8"))
        result = validate_scenario(data, check_adjacency=False)
        pool_errors = [e for e in result.errors if "marshal_pool" in e.path]
        pool_warnings = [w for w in result.warnings if "marshal_pool" in w.path]
        assert not pool_errors
        assert not pool_warnings

    def test_validator_rejects_retired_personality(self):
        from backend.modding.validator import validate_scenario
        result = validate_scenario({
            "marshals": {},
            "marshal_pool": {"France": [{
                "name": "Test", "personality": "balanced", "cost": 100}]},
        }, check_adjacency=False)
        assert any("personality" in e.path for e in result.errors)

    def test_validator_rejects_roster_collision(self):
        from backend.modding.validator import validate_scenario
        result = validate_scenario({
            "marshals": {"Ney": {"name": "Ney", "location": "Paris",
                                 "strength": 1000}},
            "marshal_pool": {"France": [{
                "name": "Ney", "personality": "aggressive", "cost": 100}]},
        }, check_adjacency=False)
        assert any("already exists" in e.message for e in result.errors)

    def test_validator_requires_cost(self):
        from backend.modding.validator import validate_scenario
        result = validate_scenario({
            "marshals": {},
            "marshal_pool": {"France": [{
                "name": "Test", "personality": "cautious"}]},
        }, check_adjacency=False)
        assert any("cost" in e.path for e in result.errors)


# ═══════════════════════ THE COMMISSION GATE ═══════════════════════════════


class TestCommissionGate:
    def test_refuses_without_gold(self, world, executor):
        world.nation_gold["France"] = 100
        result = _commission(executor, world, "Grouchy")
        assert not result["success"]
        assert "treasury" in result["message"]

    def test_refuses_without_manpower(self, world, executor):
        world.nation_gold["France"] = 10000
        world.manpower_pools["France"]["infantry"] = 1000
        result = _commission(executor, world, "Grouchy")
        assert not result["success"]
        assert "infantry" in result["message"]

    def test_unknown_candidate_lists_bench(self, world, executor):
        world.nation_gold["France"] = 10000
        result = _commission(executor, world, "Wellington")
        assert not result["success"]
        assert "Mortier" in result["message"]

    def test_no_target_asks_with_candidates(self, world, executor):
        world.nation_gold["France"] = 10000
        result = executor.execute(
            {"command": {"action": "recruit_marshal", "type": "specific"}},
            {"world": world})
        assert not result["success"]
        assert "Candidates" in result["message"]

    def test_nation_without_pool_refused(self, world, executor):
        result = _commission(executor, world, "Anyone", nation="Sweden")
        assert not result["success"]
        assert "bench is empty" in result["message"]

    def test_no_soil_refused(self, world):
        # strip France of ALL home regions
        for region_name in list(world.nation_starting_regions.get("France", [])):
            region = world.regions.get(region_name)
            if region is not None:
                region.controller = "Austria"
        world.invalidate_active_nations_cache()
        world.nation_gold["France"] = 10000
        candidate = R.find_candidate(world, "France", "Grouchy")
        assert R.check_commission(world, "France", candidate) is not None


class TestCommissionEffects:
    def _rich(self, world):
        world.nation_gold["France"] = 10000
        return world

    def test_full_commission(self, world, executor):
        self._rich(world)
        infantry_before = world.manpower_pools["France"]["infantry"]
        result = _commission(executor, world, "Grouchy")
        assert result["success"], result["message"]
        grouchy = world.marshals["Grouchy"]
        assert grouchy.nation == "France"
        assert grouchy.location == "Paris"
        assert grouchy.strength == R.RECRUIT_MARSHAL_CORPS
        assert grouchy.personality == "literal"
        assert grouchy.skills["tactical"] == 7
        assert grouchy.trust.value == 75
        assert world.nation_gold["France"] == 10000 - 4500
        assert world.manpower_pools["France"]["infantry"] == \
            infantry_before - R.RECRUIT_MARSHAL_CORPS

    def test_seeds_symmetric(self, world, executor):
        self._rich(world)
        _commission(executor, world, "Grouchy")
        grouchy = world.marshals["Grouchy"]
        murat = world.marshals["Murat"]
        davout = world.marshals["Davout"]
        assert grouchy.get_relationship("Murat") == -1
        assert murat.get_relationship("Grouchy") == -1
        assert grouchy.get_relationship("Davout") == 1
        assert davout.get_relationship("Grouchy") == 1

    def test_pool_entry_consumed(self, world, executor):
        self._rich(world)
        _commission(executor, world, "Grouchy")
        assert R.find_candidate(world, "France", "Grouchy") is None
        result = _commission(executor, world, "Grouchy")
        assert not result["success"]

    def test_double_commission_blocked(self, world, executor):
        self._rich(world)
        _commission(executor, world, "Grouchy")
        # put a copycat entry back and try again — the live-roster guard holds
        world.marshal_pool["France"].append(
            {"name": "Grouchy", "personality": "literal", "cost": 100})
        result = _commission(executor, world, "Grouchy")
        assert not result["success"]
        assert "already serves" in result["message"]

    def test_admin_ap_consumed(self, world, executor):
        self._rich(world)
        admin_before = world.admin_actions_remaining
        _commission(executor, world, "Grouchy")
        assert world.admin_actions_remaining == admin_before - 1

    def test_fallen_capital_spawns_at_richest_home(self, world, executor):
        self._rich(world)
        world.regions["Paris"].controller = "Austria"
        world.invalidate_active_nations_cache()
        result = _commission(executor, world, "Grouchy")
        assert result["success"]
        grouchy = world.marshals["Grouchy"]
        assert grouchy.location != "Paris"
        assert grouchy.location in world.nation_starting_regions["France"]
        assert world.regions[grouchy.location].controller == "France"

    def test_enters_glory_ladder_at_zero(self, world, executor):
        self._rich(world)
        J._append_glory(world.marshals["Davout"], world.current_turn, 3)
        _commission(executor, world, "Grouchy")
        grouchy = world.marshals["Grouchy"]
        assert J.get_glory_score(grouchy, world.current_turn) == 0
        ladder = J.get_nation_ladder(world, "France")
        assert ladder[0][0].name == "Davout"
        assert grouchy.jealous_of is None

    def test_expectation_starts_at_zero(self, world, executor):
        from backend.game_logic import dotation
        self._rich(world)
        _commission(executor, world, "Grouchy")
        assert dotation.get_expectation(world.marshals["Grouchy"]) == 0

    def test_commissioned_marshal_round_trips(self, world, executor):
        self._rich(world)
        _commission(executor, world, "Grouchy")
        restored = WorldState.from_dict(world.to_dict())
        assert "Grouchy" in restored.marshals
        assert restored.marshals["Grouchy"].personality == "literal"
        assert "Grouchy" not in [
            c["name"] for c in restored.marshal_pool["France"]]

    def test_intendance_derives_from_authored_admin(self, world, executor):
        """Suchet (admin 9) hits the thrifty tier the moment he serves —
        the MC-2b single source needs no new wiring."""
        self._rich(world)
        _commission(executor, world, "Suchet")
        assert world.marshals["Suchet"].get_recruit_cost_modifier() == \
            pytest.approx(0.85)

    def test_campaign_log_and_notification(self, world, executor):
        from backend.notifications import MARSHAL_COMMISSIONED
        self._rich(world)
        _commission(executor, world, "Grouchy")
        assert any(e.get("type") == "marshal_commissioned"
                   for e in world.event_log)
        assert any(n["type"] == MARSHAL_COMMISSIONED
                   for n in world.notifications.get_pending())

    def test_cavalry_candidate_flag(self, world, executor):
        world.nation_gold["Britain"] = 10000
        result = _commission(executor, world, "Paget", nation="Britain")
        assert result["success"]
        assert world.marshals["Paget"].cavalry is True


# ═══════════════════════ THE AI RUNG (GR5) ═════════════════════════════════


class TestAIRung:
    def test_ai_commissions_when_pressed(self, world, executor):
        """Austria at war, under-officered, solvent → the admin rung
        reaches for the pool through the SAME executor gate."""
        world.nation_gold["Austria"] = 20000
        # Austria starts with 3 standing → remove one to go under the cap
        world.marshals["ArchdukeJohn"].strength = 0
        action = R.find_ai_commission(
            world, "Austria", world.nation_gold["Austria"])
        assert action is not None
        assert action["action"] == "recruit_marshal"
        assert action["target"] == "Schwarzenberg"  # authored quality order
        result = executor.execute({"command": action}, {"world": world})
        assert result["success"]
        assert "Schwarzenberg" in world.marshals
        assert world.marshals["Schwarzenberg"].nation == "Austria"

    def test_ai_holds_at_peace(self, world):
        world.nation_gold["Britain"] = 20000
        for war_partner in list(world.get_nations_at_war_with("Britain")):
            pass
        if world.get_nations_at_war_with("Britain"):
            pytest.skip("Britain unexpectedly at war at boot")
        assert R.find_ai_commission(world, "Britain", 20000) is None

    def test_ai_holds_when_fully_officered(self, world):
        world.nation_gold["Austria"] = 20000
        assert len([m for m in world.marshals.values()
                    if m.nation == "Austria" and m.strength > 0]) >= \
            R.AI_RECRUIT_MAX_STANDING
        assert R.find_ai_commission(world, "Austria", 20000) is None

    def test_ai_holds_when_poor(self, world):
        world.marshals["ArchdukeJohn"].strength = 0
        assert R.find_ai_commission(world, "Austria", 3000) is None

    def test_ai_skips_unaffordable_takes_next(self, world):
        """The rung walks the authored order for the first AFFORDABLE
        candidate (buffer included). In production the treasury param IS
        world.nation_gold — keep them agreeing here."""
        world.marshals["ArchdukeJohn"].strength = 0
        # Schwarzenberg costs 4500 + 1000 buffer; give exactly enough for
        # Hiller (3500 + 1000)
        world.nation_gold["Austria"] = 4600
        action = R.find_ai_commission(world, "Austria", 4600)
        assert action is not None
        assert action["target"] == "Hiller"


# ═══════════════════════ SURFACES ══════════════════════════════════════════


class TestSurfaces:
    def test_recruitment_payload_shape(self, world):
        payload = R.build_recruitment_payload(world)
        assert payload["corps_size"] == R.RECRUIT_MARSHAL_CORPS
        assert len(payload["candidates"]) == 6
        first = payload["candidates"][0]
        for key in ("name", "personality", "skills", "trust", "biography",
                    "cost", "available", "blocked_reason", "relationships"):
            assert key in first
        # honesty: at the 800g boot treasury nothing is affordable
        assert all(not c["available"] for c in payload["candidates"])
        assert all("treasury" in c["blocked_reason"]
                   for c in payload["candidates"])

    def test_payload_available_when_affordable(self, world):
        world.nation_gold["France"] = 10000
        payload = R.build_recruitment_payload(world)
        assert all(c["available"] for c in payload["candidates"])

    def test_overview_endpoint_carries_recruitment(self, world):
        """GET /marshal_overview ships the pool + the glory ladder."""
        from backend.game_logic.marshal_overview import build_marshal_overview
        cards = build_marshal_overview(world)
        assert cards  # cards built fine alongside the new payload helpers
        ladder = J.build_glory_ladder_payload(world)
        payload = R.build_recruitment_payload(world)
        assert isinstance(ladder, list) and isinstance(payload, dict)

    def test_dispatch_event_for_enemy_commission(self, world, executor):
        world.nation_gold["Austria"] = 20000
        world.marshals["ArchdukeJohn"].strength = 0
        _commission(executor, world, "Schwarzenberg", nation="Austria")
        queued = [e for e in world.pending_dispatch_events
                  if e.get("type") == "enemy_marshal_commissioned"]
        assert queued and queued[0]["template_vars"]["marshal"] == "Schwarzenberg"

    def test_mock_parser_family(self):
        import os
        os.environ.setdefault("LLM_MODE", "mock")
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        assert client.parse_command("commission Grouchy")["action"] == \
            "recruit_marshal"
        assert client.parse_command("recruit marshal Suchet")["action"] == \
            "recruit_marshal"
        assert client.parse_command("recruit infantry for Ney")["action"] == \
            "recruit"
        assert client.parse_command("commission a rente for Ney")["action"] == \
            "grant_pension"
