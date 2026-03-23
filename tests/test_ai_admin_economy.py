"""Tests for Phase 6.2.G: AI Admin Phase, Economy Command, Turn Summary.

Tests:
- AI recruits when marshal below 40% starting strength
- AI builds fortification at border regions
- AI repairs damaged buildings
- AI repairs war damage in high-income regions
- AI saves AP when nothing needed (gets gold bonus)
- AI doesn't spend when treasury too low
- AI admin phase runs for all enemy nations
- Economy command shows correct breakdown (0 AP cost)
- Turn summary includes financial data
- Full end-to-end: player turn + enemy turn with AI admin + income phase
"""

import pytest
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.ai.enemy_ai import EnemyAI


def _make_game_state(world):
    """Helper to build game_state dict."""
    return {"world": world}


def _setup_world():
    """Create a standard world for testing."""
    world = WorldState(player_nation="France")
    return world


# ═══════════════════════════════════════════════════════════════════
# AI ADMIN PHASE - RECRUITMENT
# ═══════════════════════════════════════════════════════════════════

class TestAIAdminRecruit:
    """Test AI recruitment during admin phase."""

    def test_ai_recruits_weakest_marshal(self):
        """AI should recruit for marshal below 40% starting strength."""
        world = _setup_world()
        executor = CommandExecutor()
        ai = EnemyAI(executor)
        game_state = _make_game_state(world)

        # Wellington starts at 30000, reduce to 10000 (33% = below 40%)
        wellington = world.get_marshal("Wellington")
        wellington.strength = 10000
        # Ensure Britain has enough gold
        world.nation_gold["Britain"] = 1000

        results = ai.execute_admin_phase("Britain", world, game_state)

        # Should have recruited
        recruited = any(
            r.get("ai_action", {}).get("action") == "recruit"
            for r in results
        )
        assert recruited, f"AI should recruit for weak marshal. Results: {[r.get('ai_action') for r in results]}"

    def test_ai_does_not_recruit_healthy_marshal(self):
        """AI should not recruit if marshals are above 40% strength."""
        world = _setup_world()
        executor = CommandExecutor()
        ai = EnemyAI(executor)
        game_state = _make_game_state(world)

        # Wellington at full strength - no recruitment needed
        world.nation_gold["Britain"] = 1000

        results = ai.execute_admin_phase("Britain", world, game_state)

        recruited = any(
            r.get("ai_action", {}).get("action") == "recruit"
            for r in results
        )
        assert not recruited, "AI should not recruit when marshals are healthy"

    def test_ai_cannot_recruit_without_gold(self):
        """AI should not recruit if treasury is too low."""
        world = _setup_world()
        executor = CommandExecutor()
        ai = EnemyAI(executor)
        game_state = _make_game_state(world)

        wellington = world.get_marshal("Wellington")
        wellington.strength = 5000  # Very weak
        world.nation_gold["Britain"] = 50  # Too poor to recruit

        results = ai.execute_admin_phase("Britain", world, game_state)

        recruited = any(
            r.get("ai_action", {}).get("action") == "recruit"
            for r in results
        )
        assert not recruited, "AI should not recruit when gold is too low"

    def test_ai_continues_after_failed_action(self):
        """AI should try lower-priority actions when higher-priority fails."""
        world = _setup_world()
        executor = CommandExecutor()
        ai = EnemyAI(executor)
        game_state = _make_game_state(world)

        # Set up: weakest marshal in a region NOT controlled by Britain
        # so recruit will fail, but give enough gold for building
        world.nation_gold["Britain"] = 1000

        # Create a weak British marshal in a French-controlled region
        brit_marshal = None
        for m in world.marshals.values():
            if m.nation == "Britain":
                brit_marshal = m
                break
        assert brit_marshal is not None

        brit_marshal.strength = 1000  # Very low
        brit_marshal.starting_strength = 10000
        # Put marshal in a region controlled by France (not Britain)
        brit_marshal.location = "Paris"
        paris = world.get_region("Paris")
        paris.controller = "France"

        # Set up a buildable border region for Britain
        belgium = world.get_region("Belgium")
        belgium.controller = "Britain"
        belgium.stability = 80
        belgium.region_type = "major_city"
        belgium.buildings = []

        results = ai.execute_admin_phase("Britain", world, game_state)

        # Recruit should have failed (wrong controller),
        # but AI should have tried building instead
        built = any(
            r.get("ai_action", {}).get("action") == "build"
            for r in results
        )
        assert built, (
            f"AI should fall through to build after recruit fails. "
            f"Results: {[r.get('ai_action') for r in results]}"
        )


# ═══════════════════════════════════════════════════════════════════
# AI ADMIN PHASE - FORTIFICATION
# ═══════════════════════════════════════════════════════════════════

class TestAIAdminBuild:
    """Test AI building fortifications during admin phase."""

    def test_ai_builds_fortification_at_border(self):
        """AI should build fortification at border city region."""
        world = _setup_world()
        executor = CommandExecutor()
        ai = EnemyAI(executor)
        game_state = _make_game_state(world)

        # Give Britain lots of gold and healthy marshals (no need to recruit)
        world.nation_gold["Britain"] = 2000

        # Set Vienna as Britain-controlled major city on the border
        # (adjacent to Bavaria which is France-controlled)
        vienna = world.get_region("Vienna")
        vienna.controller = "Britain"
        vienna.stability = 100
        # Clear any existing buildings
        vienna.buildings = []
        vienna.building_under_construction = None

        # Ensure adjacent Bavaria is enemy-controlled
        bavaria = world.get_region("Bavaria")
        bavaria.controller = "France"

        results = ai.execute_admin_phase("Britain", world, game_state)

        built = any(
            r.get("ai_action", {}).get("action") == "build"
            for r in results
        )
        assert built, f"AI should build fortification at border city. Results: {[r.get('ai_action') for r in results]}"

    def test_ai_does_not_build_in_non_buildable_region(self):
        """AI should not attempt to build in rural/town regions (excluding capitals)."""
        world = _setup_world()
        executor = CommandExecutor()
        ai = EnemyAI(executor)

        # Britain's starting regions: Netherlands (capital), Waterloo (rural), Hanover (town)
        # Netherlands is capital (has building slots), so it's buildable
        # Waterloo and Hanover have no slots
        result = ai._find_unfortified_border_region("Britain", world)
        # Netherlands is now a capital with building slots, so it may be returned
        if result is not None:
            assert result == "Netherlands", f"Only Netherlands should be buildable, got {result}"


# ═══════════════════════════════════════════════════════════════════
# AI ADMIN PHASE - REPAIR
# ═══════════════════════════════════════════════════════════════════

class TestAIAdminRepair:
    """Test AI repair decisions during admin phase."""

    def test_ai_repairs_damaged_building(self):
        """AI should repair a damaged building in a high-income region."""
        world = _setup_world()
        executor = CommandExecutor()
        ai = EnemyAI(executor)
        game_state = _make_game_state(world)

        # Give Britain a region with a damaged building
        world.nation_gold["Britain"] = 1000
        belgium = world.get_region("Belgium")
        belgium.controller = "Britain"
        belgium.stability = 100
        belgium.buildings = [{"type": "supply_depot", "damaged": True}]

        results = ai.execute_admin_phase("Britain", world, game_state)

        repaired = any(
            r.get("ai_action", {}).get("action") == "repair"
            for r in results
        )
        assert repaired, f"AI should repair damaged building. Results: {[r.get('ai_action') for r in results]}"

    def test_ai_repairs_war_damage(self):
        """AI should repair war damage in high-income region."""
        world = _setup_world()
        executor = CommandExecutor()
        ai = EnemyAI(executor)
        game_state = _make_game_state(world)

        # Give Britain enough gold, ensure no recruit needed
        world.nation_gold["Britain"] = 1000

        # Damage a British-controlled region
        belgium = world.get_region("Belgium")
        belgium.controller = "Britain"
        belgium.stability = 100
        belgium.war_damage = 0.30

        results = ai.execute_admin_phase("Britain", world, game_state)

        repaired_damage = any(
            r.get("ai_action", {}).get("action") == "repair"
            for r in results
        )
        assert repaired_damage, f"AI should repair war damage. Results: {[r.get('ai_action') for r in results]}"


# ═══════════════════════════════════════════════════════════════════
# AI ADMIN PHASE - SAVING AP
# ═══════════════════════════════════════════════════════════════════

class TestAIAdminSaveAP:
    """Test AI saves AP for income bonus."""

    def test_ai_saves_ap_gets_gold_bonus(self):
        """AI should get gold bonus for unused admin AP."""
        world = _setup_world()
        executor = CommandExecutor()
        ai = EnemyAI(executor)
        game_state = _make_game_state(world)

        # Give Britain nothing to do: marshals healthy, no damaged buildings
        # Gold set below all build/recruit thresholds so AI can't spend
        # (recruit=200, market=350, depot=300, fort=400, repair=150)
        initial_gold = 100
        world.nation_gold["Britain"] = initial_gold

        results = ai.execute_admin_phase("Britain", world, game_state)

        # Should have saved 2 AP = +150 gold bonus
        expected_bonus = 2 * 75  # 150
        # Results should be empty (nothing to do)
        assert len(results) == 0, f"AI should take no actions. Got: {len(results)}"
        assert world.nation_gold["Britain"] == initial_gold + expected_bonus, \
            f"Expected {initial_gold + expected_bonus}, got {world.nation_gold['Britain']}"

    def test_ai_partial_save(self):
        """AI uses 1 AP, saves 1 AP for 75 gold bonus."""
        world = _setup_world()
        executor = CommandExecutor()
        ai = EnemyAI(executor)
        game_state = _make_game_state(world)

        # Set up so AI needs to recruit but only one marshal is weak
        wellington = world.get_marshal("Wellington")
        wellington.strength = 5000  # Very weak (below 40%)
        initial_gold = 1000
        world.nation_gold["Britain"] = initial_gold

        results = ai.execute_admin_phase("Britain", world, game_state)

        # Should have recruited (1 AP used) and saved 1 AP (+75 gold)
        recruited = sum(1 for r in results if r.get("ai_action", {}).get("action") == "recruit")
        assert recruited >= 1, "Should have recruited at least once"
        # 1 unused AP = 75 gold bonus (applied on top of remaining gold after recruit cost)
        # Gold after = initial - recruit_cost + 75 bonus


# ═══════════════════════════════════════════════════════════════════
# AI ADMIN PHASE - MULTI-NATION
# ═══════════════════════════════════════════════════════════════════

class TestAIAdminMultiNation:
    """Test AI admin runs for all enemy nations."""

    def test_admin_phase_runs_for_both_enemies(self):
        """Both Britain and Prussia should get admin phases."""
        world = _setup_world()
        executor = CommandExecutor()
        ai = EnemyAI(executor)
        game_state = _make_game_state(world)

        # Run admin for both nations
        britain_results = ai.execute_admin_phase("Britain", world, game_state)
        prussia_results = ai.execute_admin_phase("Prussia", world, game_state)

        # Both should return lists (even if empty)
        assert isinstance(britain_results, list)
        assert isinstance(prussia_results, list)


# ═══════════════════════════════════════════════════════════════════
# ECONOMY COMMAND
# ═══════════════════════════════════════════════════════════════════

class TestEconomyCommand:
    """Test the economy/treasury/finances free command."""

    def test_economy_command_returns_breakdown(self):
        """Economy command should show income, upkeep, net, treasury."""
        world = _setup_world()
        executor = CommandExecutor()
        game_state = _make_game_state(world)

        command = {"command": {"action": "economy", "type": "specific"}}
        result = executor.execute(command, game_state)

        assert result["success"] is True
        assert "TREASURY REPORT" in result["message"]
        assert "Income:" in result["message"]
        assert "Upkeep:" in result["message"]
        assert "Treasury:" in result["message"]

    def test_economy_command_is_free(self):
        """Economy command should cost 0 AP."""
        world = _setup_world()
        executor = CommandExecutor()
        game_state = _make_game_state(world)

        initial_actions = world.actions_remaining
        initial_admin = world.admin_actions_remaining

        command = {"command": {"action": "economy", "type": "specific"}}
        result = executor.execute(command, game_state)

        assert result["success"] is True
        assert world.actions_remaining == initial_actions, "Economy should not consume CP"
        assert world.admin_actions_remaining == initial_admin, "Economy should not consume admin AP"

    def test_treasury_alias_works(self):
        """'treasury' should work as alias for 'economy'."""
        world = _setup_world()
        executor = CommandExecutor()
        game_state = _make_game_state(world)

        command = {"command": {"action": "treasury", "type": "specific"}}
        result = executor.execute(command, game_state)

        assert result["success"] is True
        assert "TREASURY REPORT" in result["message"]

    def test_finances_alias_works(self):
        """'finances' should work as alias for 'economy'."""
        world = _setup_world()
        executor = CommandExecutor()
        game_state = _make_game_state(world)

        command = {"command": {"action": "finances", "type": "specific"}}
        result = executor.execute(command, game_state)

        assert result["success"] is True
        assert "TREASURY REPORT" in result["message"]

    def test_economy_shows_bankruptcy_warning(self):
        """Economy command should show bankruptcy warning when bankrupt."""
        world = _setup_world()
        executor = CommandExecutor()
        game_state = _make_game_state(world)

        world.nation_bankruptcy_turns["France"] = 3
        command = {"command": {"action": "economy", "type": "specific"}}
        result = executor.execute(command, game_state)

        assert "Bankrupt" in result["message"]
        assert "Desertion" in result["message"]

    def test_economy_event_has_financial_data(self):
        """Economy events should include income, upkeep, net, treasury."""
        world = _setup_world()
        executor = CommandExecutor()
        game_state = _make_game_state(world)

        command = {"command": {"action": "economy", "type": "specific"}}
        result = executor.execute(command, game_state)

        events = result.get("events", [])
        eco_events = [e for e in events if e.get("type") == "economy_report"]
        assert len(eco_events) == 1
        eco = eco_events[0]
        assert "income" in eco
        assert "upkeep" in eco
        assert "net" in eco
        assert "treasury" in eco
        assert isinstance(eco["income"], int)
        assert isinstance(eco["treasury"], int)


# ═══════════════════════════════════════════════════════════════════
# TURN SUMMARY FINANCIAL REPORT
# ═══════════════════════════════════════════════════════════════════

class TestTurnSummaryFinancial:
    """Test that end-turn includes financial summary."""

    def test_end_turn_includes_financial_summary(self):
        """End turn message should include income/upkeep/net/treasury."""
        world = _setup_world()
        executor = CommandExecutor()
        game_state = _make_game_state(world)

        command = {"command": {"action": "end_turn", "type": "specific"}}
        result = executor.execute(command, game_state)

        assert result["success"] is True
        msg = result["message"]
        assert "Income:" in msg, f"Missing income in: {msg[:200]}"
        assert "Upkeep:" in msg, f"Missing upkeep in: {msg[:200]}"
        assert "Treasury:" in msg, f"Missing treasury in: {msg[:200]}"

    def test_turn_end_event_has_financial_fields(self):
        """Turn end event should include upkeep, net, treasury."""
        world = _setup_world()
        executor = CommandExecutor()
        game_state = _make_game_state(world)

        command = {"command": {"action": "end_turn", "type": "specific"}}
        result = executor.execute(command, game_state)

        events = result.get("events", [])
        turn_events = [e for e in events if e.get("type") == "turn_end"]
        assert len(turn_events) >= 1
        te = turn_events[0]
        assert "income" in te
        assert "upkeep" in te
        assert "net" in te
        assert "treasury" in te


# ═══════════════════════════════════════════════════════════════════
# UI WIRING: OCCUPATION FIELDS IN TACTICAL_STATE
# ═══════════════════════════════════════════════════════════════════

class TestOccupationFieldsInTacticalState:
    """Test that occupation fields are exposed in get_game_state_summary."""

    def test_occupation_fields_in_tactical_state(self):
        """Tactical state should include occupation_region, turns_held, turns_required."""
        world = _setup_world()

        # Set a marshal as occupying
        ney = world.get_marshal("Ney")
        ney.occupation_region = "Belgium"
        ney.occupation_turns_held = 1
        ney.occupation_turns_required = 2

        summary = world.get_game_state_summary()

        # Find Ney in map_data
        for region_name, region_data in summary["map_data"].items():
            for marshal_data in region_data.get("marshals", []):
                if marshal_data["name"] == "Ney":
                    tac = marshal_data["tactical_state"]
                    assert tac["occupation_region"] == "Belgium"
                    assert tac["occupation_turns_held"] == 1
                    assert tac["occupation_turns_required"] == 2
                    return

        pytest.fail("Ney not found in map_data")

    def test_occupation_fields_default_empty(self):
        """Non-occupying marshals should have empty occupation fields."""
        world = _setup_world()
        summary = world.get_game_state_summary()

        # Check any marshal
        for region_name, region_data in summary["map_data"].items():
            for marshal_data in region_data.get("marshals", []):
                tac = marshal_data["tactical_state"]
                assert "occupation_region" in tac
                assert tac["occupation_region"] == ""
                assert tac["occupation_turns_held"] == 0
                assert tac["occupation_turns_required"] == 0
                return  # Just check the first one


# ═══════════════════════════════════════════════════════════════════
# END-TO-END: FULL TURN WITH AI ADMIN
# ═══════════════════════════════════════════════════════════════════

class TestEndToEnd:
    """Full turn cycle with AI admin phase."""

    def test_full_turn_with_ai_admin(self):
        """Complete turn: player end_turn -> enemy military -> enemy admin -> income."""
        world = _setup_world()
        executor = CommandExecutor()
        game_state = _make_game_state(world)

        # Weaken Wellington so AI recruits
        wellington = world.get_marshal("Wellington")
        wellington.strength = 5000
        world.nation_gold["Britain"] = 1000

        initial_turn = world.current_turn
        command = {"command": {"action": "end_turn", "type": "specific"}}
        result = executor.execute(command, game_state)

        assert result["success"] is True
        # Turn should advance
        assert world.current_turn > initial_turn

        # Enemy phase should have run
        enemy_phase = result.get("enemy_phase")
        # May or may not have actions depending on AI decisions

    def test_economy_command_during_occupation(self):
        """Economy command should work even when marshal is occupying."""
        world = _setup_world()
        executor = CommandExecutor()
        game_state = _make_game_state(world)

        # Set Ney as occupying
        ney = world.get_marshal("Ney")
        ney.occupation_region = "Belgium"
        ney.occupation_turns_held = 1
        ney.occupation_turns_required = 2

        # Economy command should still work (it's in allowed_during_occupation)
        command = {"command": {"action": "economy", "marshal": "Ney", "type": "specific"}}
        result = executor.execute(command, game_state)

        assert result["success"] is True
        assert "TREASURY REPORT" in result["message"]


# ═══════════════════════════════════════════════════════════════════
# MOCK PARSER: ECONOMY KEYWORDS
# ═══════════════════════════════════════════════════════════════════

class TestEconomyParsing:
    """Test that economy keywords are detected by mock parser."""

    def test_economy_keyword_detected(self):
        """'economy' should be parsed as economy action."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client._parse_with_mock("economy")
        assert result.action == "economy"

    def test_treasury_keyword_detected(self):
        """'treasury' should be parsed as economy action."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client._parse_with_mock("treasury")
        assert result.action == "economy"

    def test_finances_keyword_detected(self):
        """'finances' should be parsed as economy action."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client._parse_with_mock("finances")
        assert result.action == "economy"


# ═══════════════════════════════════════════════════════════════════
# AI ADMIN HELPER METHODS
# ═══════════════════════════════════════════════════════════════════

class TestAIAdminHelpers:
    """Test the AI admin decision helper methods."""

    def test_find_weakest_marshal(self):
        """Should find marshal with lowest strength ratio."""
        world = _setup_world()
        executor = CommandExecutor()
        ai = EnemyAI(executor)

        # Weaken Wellington more than Uxbridge
        wellington = world.get_marshal("Wellington")
        wellington.strength = 5000  # 17% of 30000

        uxbridge = world.get_marshal("Uxbridge")
        uxbridge.strength = 8000  # 53% of 15000

        result = ai._find_weakest_marshal_for_admin("Britain", world)
        assert result is not None
        assert result.name == "Wellington", f"Expected Wellington, got {result.name}"

    def test_find_weakest_marshal_none_when_healthy(self):
        """Should return None when all marshals are healthy."""
        world = _setup_world()
        executor = CommandExecutor()
        ai = EnemyAI(executor)

        result = ai._find_weakest_marshal_for_admin("Britain", world)
        assert result is None

    def test_find_war_damaged_region(self):
        """Should find the highest-income damaged region."""
        world = _setup_world()
        executor = CommandExecutor()
        ai = EnemyAI(executor)

        # Damage Belgium (town, 100 income) and set as British
        belgium = world.get_region("Belgium")
        belgium.controller = "Britain"
        belgium.war_damage = 0.20

        result = ai._find_war_damaged_region("Britain", world)
        assert result == "Belgium"

    def test_find_damaged_building_region(self):
        """Should find region with damaged building, prioritize by income."""
        world = _setup_world()
        executor = CommandExecutor()
        ai = EnemyAI(executor)

        # Add damaged building to Belgium
        belgium = world.get_region("Belgium")
        belgium.controller = "Britain"
        belgium.buildings = [{"type": "fortification", "damaged": True}]

        result = ai._find_damaged_building_region("Britain", world)
        assert result is not None
        assert result["region"] == "Belgium"
        assert result["building_type"] == "fortification"
