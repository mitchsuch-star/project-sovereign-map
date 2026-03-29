"""
Systems Audit V2 Fix Plan — Session 3: AI + Economy + Turn Manager Fixes

Tests for 9 bugs across AI, economy, and turn management:
- V2-5:  LLM prompt leaks all enemy data through fog
- V2-20/21: AI cooldowns tick 4x per turn (once per nation instead of once per turn)
- V2-19: Enemy phase try/except swallows state mutations
- V2-26: Autonomous marshal phase has no error handling
- V2-29: Supply attrition creates 0-strength zombie marshals
- V2-24: Overwatch self-count inflates penalty
- V2-96: AI gets 75g vs player 25g per unused admin AP
- V2-81: max_free_actions assigned but never checked
"""

from unittest.mock import patch
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.models.intel import FULL, PARTIAL, STALE
from backend.commands.executor import CommandExecutor
from backend.ai.enemy_ai import EnemyAI


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def make_world():
    """Fresh WorldState."""
    return WorldState()


def make_marshal(name="Ney", location="Belgium", strength=50000,
                 nation="France", personality="aggressive"):
    return Marshal(name=name, location=location, strength=strength,
                   personality=personality, nation=nation,
                   spawn_location=location)


def make_enemy(name="Wellington", location="Waterloo", strength=30000,
               nation="Britain", personality="cautious"):
    return Marshal(name=name, location=location, strength=strength,
                   personality=personality, nation=nation,
                   spawn_location=location)


# ═══════════════════════════════════════════════════════
# V2-5: LLM prompt fog-filters enemies
# ═══════════════════════════════════════════════════════

class TestLLMFogFilter:
    """V2-5: get_llm_game_state() only includes enemies in PARTIAL+ regions."""

    def test_full_visibility_shows_exact_strength(self):
        """Enemy in FULL visibility region → exact strength in LLM state."""
        world = make_world()
        enemy = make_enemy(name="Wellington", location="Waterloo", strength=30000)
        world.marshals["Wellington"] = enemy

        # Set FULL visibility
        intel = world.get_region_intel("Waterloo")
        intel.visibility = FULL

        # Import and call
        import backend.main as main_module
        old_world = main_module.world
        main_module.world = world
        try:
            state = main_module.get_llm_game_state()
        finally:
            main_module.world = old_world

        assert "Wellington" in state["enemies"]
        assert state["enemies"]["Wellington"]["strength"] == 30000

    def test_partial_visibility_shows_unknown_strength(self):
        """Enemy in PARTIAL visibility region → 'unknown' strength."""
        world = make_world()
        enemy = make_enemy(name="Wellington", location="Waterloo", strength=30000)
        world.marshals["Wellington"] = enemy

        intel = world.get_region_intel("Waterloo")
        intel.visibility = PARTIAL

        import backend.main as main_module
        old_world = main_module.world
        main_module.world = world
        try:
            state = main_module.get_llm_game_state()
        finally:
            main_module.world = old_world

        assert "Wellington" in state["enemies"]
        assert state["enemies"]["Wellington"]["strength"] == "unknown"

    def test_stale_visibility_excludes_enemy(self):
        """Enemy in STALE region → excluded from LLM state."""
        world = make_world()
        enemy = make_enemy(name="Wellington", location="Waterloo", strength=30000)
        world.marshals["Wellington"] = enemy

        intel = world.get_region_intel("Waterloo")
        intel.visibility = STALE

        import backend.main as main_module
        old_world = main_module.world
        main_module.world = world
        try:
            state = main_module.get_llm_game_state()
        finally:
            main_module.world = old_world

        assert "Wellington" not in state["enemies"]

    def test_unknown_visibility_excludes_enemy(self):
        """Enemy in UNKNOWN region → excluded from LLM state."""
        world = make_world()
        enemy = make_enemy(name="Wellington", location="Waterloo", strength=30000)
        world.marshals["Wellington"] = enemy

        # Force UNKNOWN visibility (clear any default intel)
        from backend.models.intel import UNKNOWN as UNK
        intel = world.get_region_intel("Waterloo")
        intel.visibility = UNK

        import backend.main as main_module
        old_world = main_module.world
        main_module.world = world
        try:
            state = main_module.get_llm_game_state()
        finally:
            main_module.world = old_world

        assert "Wellington" not in state["enemies"]


# ═══════════════════════════════════════════════════════
# V2-5: prompt_builder handles "unknown" strength
# ═══════════════════════════════════════════════════════

class TestPromptBuilderUnknownStrength:
    """V2-5: _format_enemies handles 'unknown' strength without crashing."""

    def test_unknown_strength_formats_correctly(self):
        from backend.ai.prompt_builder import _format_enemies
        game_state = {
            "enemies": {
                "Wellington": {
                    "location": "Waterloo",
                    "strength": "unknown",
                    "nation": "Britain"
                }
            }
        }
        result = _format_enemies(game_state)
        assert "unknown troops" in result
        assert "Wellington" in result

    def test_normal_strength_still_works(self):
        from backend.ai.prompt_builder import _format_enemies
        game_state = {
            "enemies": {
                "Wellington": {
                    "location": "Waterloo",
                    "strength": 30000,
                    "nation": "Britain"
                }
            }
        }
        result = _format_enemies(game_state)
        assert "30K troops" in result


# ═══════════════════════════════════════════════════════
# V2-20/21: Cooldowns decrement once per turn
# ═══════════════════════════════════════════════════════

class TestCooldownDecrement:
    """V2-20/21: Cooldowns must tick once per turn, not once per nation."""

    def test_decrement_all_cooldowns_ticks_once(self):
        """decrement_all_cooldowns reduces cooldown by exactly 1."""
        world = make_world()
        world.ai_failed_action_cooldowns = {
            "Wellington": {"attack": 3}
        }
        world.ai_refortify_cooldown = {
            "Blucher": 2
        }

        executor = CommandExecutor()
        ai = EnemyAI(executor)
        ai.decrement_all_cooldowns(world)

        assert world.ai_failed_action_cooldowns["Wellington"]["attack"] == 2
        assert world.ai_refortify_cooldown["Blucher"] == 1

    def test_cooldowns_not_in_process_nation_turn(self):
        """process_nation_turn no longer decrements cooldowns internally."""
        world = make_world()
        world.ai_failed_action_cooldowns = {
            "Wellington": {"attack": 3}
        }
        world.ai_refortify_cooldown = {"Blucher": 2}

        executor = CommandExecutor()
        ai = EnemyAI(executor)

        # Run process_nation_turn for Britain — cooldowns should NOT change
        # We need minimal setup to avoid crashes
        brit_marshal = make_enemy(name="Wellington", location="Waterloo",
                                  strength=30000, nation="Britain")
        world.marshals["Wellington"] = brit_marshal
        world.enemy_nations = ["Britain"]
        game_state = {"world": world}

        # Patch _select_next_marshal_action to return None (end immediately)
        with patch.object(ai, '_select_next_marshal_action', return_value=(None, None, 0)):
            ai.process_nation_turn("Britain", world, game_state)

        # Cooldowns unchanged — they should only be decremented by decrement_all_cooldowns
        assert world.ai_failed_action_cooldowns["Wellington"]["attack"] == 3
        assert world.ai_refortify_cooldown["Blucher"] == 2

    def test_expired_cooldown_removed(self):
        """Cooldown at 1 expires to 0 and is removed."""
        world = make_world()
        world.ai_failed_action_cooldowns = {
            "Wellington": {"attack": 1}
        }
        world.ai_refortify_cooldown = {"Blucher": 1}

        executor = CommandExecutor()
        ai = EnemyAI(executor)
        ai.decrement_all_cooldowns(world)

        assert "Wellington" not in world.ai_failed_action_cooldowns
        assert "Blucher" not in world.ai_refortify_cooldown


# ═══════════════════════════════════════════════════════
# V2-19: Enemy phase error produces visible result
# ═══════════════════════════════════════════════════════

class TestEnemyPhaseErrorHandling:
    """V2-19: Crashed enemy turn produces visible error, not empty list."""

    def test_crash_produces_error_action(self):
        """Exception during nation turn → error action result (not empty list)."""
        from backend.game_logic.turn_manager import TurnManager

        world = make_world()
        brit = make_enemy(name="Wellington", location="Waterloo", strength=30000, nation="Britain")
        world.marshals["Wellington"] = brit
        world.enemy_nations = ["Britain"]

        tm = TurnManager(world)
        game_state = {"world": world}

        # Patch process_nation_turn to raise
        with patch.object(EnemyAI, 'process_nation_turn', side_effect=RuntimeError("test crash")):
            with patch.object(EnemyAI, 'decrement_all_cooldowns'):
                results = tm._process_enemy_turns(game_state)

        nation_data = results["nations"]["Britain"]
        assert len(nation_data["actions"]) == 1
        assert nation_data["actions"][0]["action"] == "error"
        assert "Britain" in nation_data["actions"][0]["message"]


# ═══════════════════════════════════════════════════════
# V2-26: Autonomous marshal crash doesn't break turn
# ═══════════════════════════════════════════════════════

class TestAutonomousPhaseErrorHandling:
    """V2-26: Single autonomous marshal crash doesn't kill entire turn."""

    def test_autonomous_crash_produces_error_entry(self):
        """Exception during autonomous action → error report entry."""
        from backend.game_logic.turn_manager import TurnManager

        world = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=50000, nation="France")
        ney.autonomy_turns = 3
        ney.autonomous = True
        ney.autonomous_battles_won = 0
        ney.autonomous_battles_lost = 0
        ney.autonomous_regions_captured = 0
        world.marshals["Ney"] = ney

        tm = TurnManager(world)
        game_state = {"world": world}

        with patch.object(EnemyAI, 'decide_single_action', side_effect=RuntimeError("test crash")):
            result = tm._process_autonomous_marshals(game_state)

        report = result["independent_command_report"]
        assert len(report) == 1
        assert report[0]["action"] == "error"
        assert report[0]["marshal"] == "Ney"
        # Autonomy turns still decremented
        assert ney.autonomy_turns == 2


# ═══════════════════════════════════════════════════════
# V2-29: Supply attrition eliminates 0-strength marshals
# ═══════════════════════════════════════════════════════

class TestZombieMarshalCleanup:
    """V2-29: Attrition to 0 strength removes marshal from world."""

    def test_attrition_eliminates_zero_strength(self):
        """Marshal reduced to 0 by attrition is removed from world.marshals."""
        world = make_world()
        # Tiny strength, high supply pressure
        m = make_marshal(name="Ney", location="Belgium", strength=100, nation="France")
        world.marshals["Ney"] = m

        # Another marshal to create massive overstacking
        m2 = make_marshal(name="Davout", location="Belgium", strength=200000, nation="France")
        world.marshals["Davout"] = m2

        events = world.process_supply_attrition()

        # Check for elimination event
        elim_events = [e for e in events if e["type"] == "marshal_eliminated"]
        if "Ney" not in world.marshals:
            # Ney was eliminated
            assert any(e["marshal"] == "Ney" for e in elim_events)
        else:
            # Even if Ney survived, verify no zombie (strength > 0)
            assert world.marshals["Ney"].strength > 0

    def test_attrition_elimination_removes_from_marshals(self):
        """Directly test elimination: set strength to 0-eligible via attrition."""
        world = make_world()
        # Use a marshal with 1 strength in massively oversupplied region
        m = make_marshal(name="Ney", location="Belgium", strength=1, nation="France")
        world.marshals["Ney"] = m

        # Put 999999 troops of enemies too to trigger high attrition
        m2 = make_enemy(name="Wellington", location="Belgium", strength=500000, nation="Britain")
        world.marshals["Wellington"] = m2

        events = world.process_supply_attrition()

        # If Ney still exists, strength must be > 0
        if "Ney" in world.marshals:
            assert world.marshals["Ney"].strength > 0
        else:
            # Was eliminated — check event exists
            assert any(e.get("type") == "marshal_eliminated" and e["marshal"] == "Ney"
                       for e in events)


# ═══════════════════════════════════════════════════════
# V2-24: Overwatch self-count exclusion
# ═══════════════════════════════════════════════════════

class TestOverwatchSelfExclusion:
    """V2-24: Defending artillery doesn't count as its own overwatch."""

    def test_defender_excluded_from_own_overwatch(self):
        """Artillery defender should not provide overwatch to itself."""
        world = make_world()
        executor = CommandExecutor()

        # Attacker
        attacker = make_marshal(name="Ney", location="Paris", strength=50000, nation="France")
        world.marshals["Ney"] = attacker

        # Defender is artillery
        defender = make_enemy(name="Wellington", location="Waterloo", strength=30000,
                              nation="Britain")
        defender.artillery = True
        world.marshals["Wellington"] = defender

        count = executor._calculate_overwatch(
            attacker, [], "Waterloo", world, defender_name="Wellington"
        )
        assert count == 0  # Wellington excluded from own overwatch

    def test_other_artillery_still_counted(self):
        """Non-defender artillery in same region still provides overwatch."""
        world = make_world()
        executor = CommandExecutor()

        attacker = make_marshal(name="Ney", location="Paris", strength=50000, nation="France")
        world.marshals["Ney"] = attacker

        # Defender (not artillery)
        defender = make_enemy(name="Wellington", location="Waterloo", strength=30000,
                              nation="Britain")
        world.marshals["Wellington"] = defender

        # Other artillery in same region
        other_art = make_enemy(name="Blucher", location="Waterloo", strength=20000,
                               nation="Prussia")
        other_art.artillery = True
        world.marshals["Blucher"] = other_art

        count = executor._calculate_overwatch(
            attacker, [], "Waterloo", world, defender_name="Wellington"
        )
        assert count == 1  # Blucher provides overwatch

    def test_no_defender_name_backward_compatible(self):
        """Without defender_name, all artillery counted (backward compat)."""
        world = make_world()
        executor = CommandExecutor()

        attacker = make_marshal(name="Ney", location="Paris", strength=50000, nation="France")
        world.marshals["Ney"] = attacker

        defender_art = make_enemy(name="Wellington", location="Waterloo", strength=30000,
                                   nation="Britain")
        defender_art.artillery = True
        world.marshals["Wellington"] = defender_art

        # No defender_name → Wellington counted
        count = executor._calculate_overwatch(attacker, [], "Waterloo", world)
        assert count == 1


# ═══════════════════════════════════════════════════════
# V2-96: Admin AP bonus alignment
# ═══════════════════════════════════════════════════════

class TestAdminAPBonusAlignment:
    """V2-96: Both player and AI get 25g per unused admin AP."""

    def test_player_admin_bonus_is_25(self):
        """Player _calculate_admin_bonus uses 25g rate."""
        world = make_world()
        world.admin_actions_remaining = 3
        bonus = world._calculate_admin_bonus(world.player_nation)
        assert bonus == 75  # 3 * 25

    def test_ai_admin_bonus_is_25(self):
        """AI execute_admin_phase uses 25g rate (not 75g)."""
        world = make_world()
        world.nation_gold["Britain"] = 0

        executor = CommandExecutor()
        ai = EnemyAI(executor)

        # Patch _pick_admin_action to return None (no actions → all AP saved)
        with patch.object(ai, '_pick_admin_action', return_value=None):
            ai.execute_admin_phase("Britain", world, {"world": world})

        # Default 3 admin AP saved → 75g (3 * 25), not 225g (3 * 75)
        assert world.nation_gold["Britain"] <= 75

    def test_display_string_says_25(self):
        """Economy report display string says 'x 25', not 'x 75'."""
        # Read the source file directly to verify the display string
        import os
        economy_path = os.path.join(os.path.dirname(__file__), "..", "backend", "commands", "economy_executor.py")
        with open(economy_path, "r", encoding="utf-8") as f:
            source = f.read()
        assert "unused AP x 25" in source
        assert "unused AP x 75" not in source


# ═══════════════════════════════════════════════════════
# V2-81: Free action cap enforcement
# ═══════════════════════════════════════════════════════

class TestFreeActionCap:
    """V2-81: max_free_actions = 2 is actually enforced."""

    def test_free_actions_capped(self):
        """After 2 free actions, further free-type actions are blocked."""
        world = make_world()
        executor = CommandExecutor()
        ai = EnemyAI(executor)

        brit = make_enemy(name="Wellington", location="Waterloo", strength=30000, nation="Britain")
        world.marshals["Wellington"] = brit
        world.enemy_nations = ["Britain"]
        world.nation_actions = {"Britain": 4}

        # Track calls to _execute_action
        execute_calls = []
        original_execute = ai._execute_action

        def counting_execute(action, gs):
            execute_calls.append(action)
            # Return a free action success
            if action["action"] == "wait":
                return {"success": True, "message": "Waiting", "free_action": False}
            return {"success": True, "message": "ok"}

        action_sequence = [
            # First return 3 wait actions (free), then None to end
            (brit, {"action": "wait", "marshal": "Wellington"}, 100),
            (brit, {"action": "wait", "marshal": "Wellington"}, 100),
            (brit, {"action": "wait", "marshal": "Wellington"}, 100),
            (brit, {"action": "wait", "marshal": "Wellington"}, 100),
            (None, None, 0),
        ]
        call_idx = [0]

        def mock_select(*args, **kwargs):
            idx = call_idx[0]
            call_idx[0] += 1
            if idx < len(action_sequence):
                return action_sequence[idx]
            return (None, None, 0)

        with patch.object(ai, '_select_next_marshal_action', side_effect=mock_select):
            with patch.object(ai, '_execute_action', side_effect=counting_execute):
                ai.process_nation_turn("Britain", world, {"world": world})

        # "wait" is a free action — after 2 free waits, further waits should be blocked
        # The cap prevents more than 2 free actions from executing
        wait_executions = [c for c in execute_calls if c["action"] == "wait"]
        assert len(wait_executions) <= 2
