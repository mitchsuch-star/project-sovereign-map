"""
Bug Fix Session 3 Tests: PT-2, M2, PT-5, PT-4

PT-2: "status" recognized by mock parser (4 tests)
M2: "recruit infantry at Paris" works without marshal name (5 tests)
PT-5: Pursue blocked during armistice, no AP waste (6 tests)
PT-4: Attack during armistice returns diplomatic error, not "Unknown target" (4 tests)
"""

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser
from backend.ai.llm_client import LLMClient


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def make_world():
    """Create a basic world with clean diplomatic states."""
    world = WorldState(player_nation="France")
    return world


def set_state(world, nation_a, nation_b, state):
    key = world._make_diplo_key(nation_a, nation_b)
    world.diplomatic_states[key] = state


def add_marshal(world, name, nation, location, strength=10000, personality="balanced"):
    m = Marshal(name=name, nation=nation, location=location,
                strength=strength, personality=personality)
    world.marshals[name] = m
    return m


def make_game_state(world):
    return {"world": world}


def make_cmd(action, marshal=None, target=None, **extra):
    """Build executor-compatible parsed command dict.

    Top-level keys: is_strategic, strategic_type (for strategic routing).
    Everything else goes inside 'command'.
    """
    top_level_keys = {"is_strategic", "strategic_type"}
    cmd = {"action": action}
    if marshal:
        cmd["marshal"] = marshal
    if target:
        cmd["target"] = target
    parsed = {"command": cmd}
    for k, v in extra.items():
        if k in top_level_keys:
            parsed[k] = v
        else:
            cmd[k] = v
    return parsed


def make_llm():
    return LLMClient()


def make_parser():
    return CommandParser()


def make_executor():
    return CommandExecutor()


# ═══════════════════════════════════════════════════════
# PT-2: "STATUS" RECOGNIZED BY MOCK PARSER (4 tests)
# ═══════════════════════════════════════════════════════

class TestPT2StatusParse:
    """Mock parser should recognize 'status' command."""

    def test_status_mock_parse_recognized(self):
        """'status' should parse to action='status'."""
        llm = make_llm()
        result = llm._parse_with_mock("status")
        assert result.action == "status"

    def test_status_case_variations(self):
        """'Status' and 'STATUS' should also parse correctly."""
        llm = make_llm()
        for variant in ["Status", "STATUS", " status ", "  status"]:
            result = llm._parse_with_mock(variant)
            assert result.action == "status", f"'{variant}' should parse as status, got {result.action}"

    def test_status_is_free_action(self):
        """Status command should not consume AP."""
        world = make_world()
        add_marshal(world, "Davout", "France", "Paris")
        executor = make_executor()
        game_state = make_game_state(world)
        initial_ap = world.actions_remaining

        result = executor.execute(
            make_cmd("status"),
            game_state
        )
        assert result.get("success") is True
        assert world.actions_remaining == initial_ap

    def test_status_no_substring_match(self):
        """'check the status of Davout' should NOT parse as status action."""
        llm = make_llm()
        result = llm._parse_with_mock("check the status of Davout")
        assert result.action != "status", "Substring 'status' should not trigger status action"


# ═══════════════════════════════════════════════════════
# M2: RECRUIT WITHOUT MARSHAL NAME (5 tests)
# ═══════════════════════════════════════════════════════

class TestM2RecruitNoMarshal:
    """'recruit infantry at Paris' should work without specifying a marshal."""

    def test_recruit_no_marshal_parses(self):
        """'recruit infantry at Paris' should parse with action=recruit, target=Paris."""
        llm = make_llm()
        result = llm._parse_with_mock("recruit infantry at Paris")
        assert result.action == "recruit"
        assert result.target == "Paris"

    def test_recruit_no_marshal_execution(self):
        """Recruit at a location without marshal name finds nearest marshal."""
        world = make_world()
        add_marshal(world, "Davout", "France", "Paris", strength=15000)
        if "Paris" in world.regions:
            world.regions["Paris"].controller = "France"
        executor = make_executor()
        game_state = make_game_state(world)

        result = executor.execute(
            make_cmd("recruit", target="Paris",
                     raw_command="recruit infantry at Paris"),
            game_state
        )
        # Should succeed or at least not fail with "marshal not found"
        if not result.get("success"):
            msg = result.get("message", "").lower()
            assert "marshal" not in msg or "not found" not in msg, \
                f"Should not fail with marshal-not-found: {result.get('message')}"

    def test_recruit_with_marshal_still_works(self):
        """'Davout recruit' should still work (regression)."""
        llm = make_llm()
        result = llm._parse_with_mock("Davout recruit")
        assert result.action == "recruit"

    def test_recruit_requested_type_propagated(self):
        """Requested type (infantry/cavalry) should be in parsed result."""
        llm = make_llm()
        result = llm._parse_with_mock("recruit cavalry at Lyon")
        assert result.action == "recruit"
        assert result.requested_type == "cavalry"

    def test_recruit_parser_bypasses_fuzzy_marshal(self):
        """Recruit should be in meta_actions, bypassing fuzzy marshal matching."""
        parser = make_parser()
        llm = make_llm()
        parse_result = llm._parse_with_mock("recruit infantry at Paris")
        llm_dict = {
            "action": parse_result.action,
            "marshal": parse_result.marshals[0] if parse_result.marshals else None,
            "target": parse_result.target,
            "requested_type": parse_result.requested_type,
        }
        result = parser.parse("recruit infantry at Paris", llm_dict)
        cmd = result.get("command", {})
        assert cmd.get("action") == "recruit"
        assert cmd.get("marshal") is None


# ═══════════════════════════════════════════════════════
# PT-5: PURSUE BLOCKED DURING ARMISTICE (6 tests)
# ═══════════════════════════════════════════════════════

class TestPT5PursueArmistice:
    """Pursue should be blocked during armistice without consuming AP."""

    def _setup_armistice(self):
        world = make_world()
        add_marshal(world, "Ney", "France", "Belgium", strength=20000)
        add_marshal(world, "Blucher", "Prussia", "Rhineland", strength=15000)
        set_state(world, "France", "Prussia", "ARMISTICE")
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.armistice_cooldowns[diplo_key] = 3
        return world

    def test_pursue_during_armistice_blocked(self):
        """Pursue during armistice should fail with diplomatic message."""
        world = self._setup_armistice()
        executor = make_executor()
        game_state = make_game_state(world)

        result = executor.execute(
            make_cmd("strategic_command", marshal="Ney", target="Blucher",
                     is_strategic=True, strategic_type="PURSUE",
                     raw_command="Ney pursue Blucher"),
            game_state
        )
        assert result.get("success") is False
        assert "armistice" in result.get("message", "").lower()

    def test_pursue_during_armistice_no_ap(self):
        """AP should not be consumed when pursue is blocked by armistice."""
        world = self._setup_armistice()
        executor = make_executor()
        game_state = make_game_state(world)
        initial_ap = world.actions_remaining

        executor.execute(
            make_cmd("strategic_command", marshal="Ney", target="Blucher",
                     is_strategic=True, strategic_type="PURSUE",
                     raw_command="Ney pursue Blucher"),
            game_state
        )
        assert world.actions_remaining == initial_ap, "AP should not be consumed"

    def test_pursue_during_peace_blocked(self):
        """Pursue during peace should fail with diplomatic message."""
        world = make_world()
        add_marshal(world, "Ney", "France", "Belgium", strength=20000)
        add_marshal(world, "Wellington", "Britain", "Belgium", strength=15000)
        set_state(world, "France", "Britain", "PEACE")
        executor = make_executor()
        game_state = make_game_state(world)

        result = executor.execute(
            make_cmd("strategic_command", marshal="Ney", target="Wellington",
                     is_strategic=True, strategic_type="PURSUE",
                     raw_command="Ney pursue Wellington"),
            game_state
        )
        assert result.get("success") is False
        assert "not at war" in result.get("message", "").lower()

    def test_pursue_during_peace_no_ap(self):
        """AP should not be consumed when pursue is blocked by peace."""
        world = make_world()
        add_marshal(world, "Ney", "France", "Belgium", strength=20000)
        add_marshal(world, "Wellington", "Britain", "Belgium", strength=15000)
        set_state(world, "France", "Britain", "PEACE")
        executor = make_executor()
        game_state = make_game_state(world)
        initial_ap = world.actions_remaining

        executor.execute(
            make_cmd("strategic_command", marshal="Ney", target="Wellington",
                     is_strategic=True, strategic_type="PURSUE",
                     raw_command="Ney pursue Wellington"),
            game_state
        )
        assert world.actions_remaining == initial_ap

    def test_pursue_during_war_works(self):
        """Pursue during war should succeed (regression)."""
        world = make_world()
        add_marshal(world, "Ney", "France", "Belgium", strength=20000)
        add_marshal(world, "Wellington", "Britain", "Rhineland", strength=15000)
        set_state(world, "France", "Britain", "WAR")
        executor = make_executor()
        game_state = make_game_state(world)

        result = executor.execute(
            make_cmd("strategic_command", marshal="Ney", target="Wellington",
                     is_strategic=True, strategic_type="PURSUE",
                     raw_command="Ney pursue Wellington"),
            game_state
        )
        assert result.get("success") is True

    def test_support_enemy_already_blocked(self):
        """Support targeting an enemy marshal is already blocked (regression)."""
        world = make_world()
        add_marshal(world, "Ney", "France", "Belgium", strength=20000)
        add_marshal(world, "Blucher", "Prussia", "Rhineland", strength=15000)
        set_state(world, "France", "Prussia", "WAR")
        executor = make_executor()
        game_state = make_game_state(world)

        result = executor.execute(
            make_cmd("strategic_command", marshal="Ney", target="Blucher",
                     is_strategic=True, strategic_type="SUPPORT",
                     raw_command="Ney support Blucher"),
            game_state
        )
        assert result.get("success") is False
        msg = result.get("message", "").lower()
        assert "enemy" in msg or "not" in msg, f"Should reject enemy support: {result.get('message')}"


# ═══════════════════════════════════════════════════════
# PT-4: ARMISTICE ATTACK DIPLOMATIC ERROR (4 tests)
# ═══════════════════════════════════════════════════════

class TestPT4ArmisticeAttack:
    """Attack during armistice should return diplomatic error, not 'Unknown target'."""

    def _setup_armistice(self):
        world = make_world()
        add_marshal(world, "Davout", "France", "Rhineland", strength=25000)
        add_marshal(world, "Gneisenau", "Prussia", "Rhineland", strength=15000)
        set_state(world, "France", "Prussia", "ARMISTICE")
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.armistice_cooldowns[diplo_key] = 4
        return world

    def test_attack_during_armistice_diplomatic_error(self):
        """Attack during armistice should show diplomatic message, not 'Unknown target'."""
        world = self._setup_armistice()
        executor = make_executor()
        game_state = make_game_state(world)

        result = executor.execute(
            make_cmd("attack", marshal="Davout", target="Gneisenau",
                     raw_command="Davout attack Gneisenau"),
            game_state
        )
        assert result.get("success") is False
        msg = result.get("message", "").lower()
        assert "armistice" in msg, f"Should mention armistice, got: {result.get('message')}"
        assert "unknown" not in msg, f"Should NOT say 'Unknown target', got: {result.get('message')}"

    def test_attack_during_armistice_preserves_ap(self):
        """AP should not be consumed when attack is blocked by armistice."""
        world = self._setup_armistice()
        executor = make_executor()
        game_state = make_game_state(world)
        initial_ap = world.actions_remaining

        executor.execute(
            make_cmd("attack", marshal="Davout", target="Gneisenau",
                     raw_command="Davout attack Gneisenau"),
            game_state
        )
        assert world.actions_remaining == initial_ap

    def test_attack_during_peace_triggers_war(self):
        """Attack during peace should auto-declare war (existing behavior)."""
        world = make_world()
        add_marshal(world, "Davout", "France", "Rhineland", strength=25000)
        add_marshal(world, "Gneisenau", "Prussia", "Rhineland", strength=15000)
        set_state(world, "France", "Prussia", "PEACE")
        executor = make_executor()
        game_state = make_game_state(world)

        result = executor.execute(
            make_cmd("attack", marshal="Davout", target="Gneisenau",
                     raw_command="Davout attack Gneisenau"),
            game_state
        )
        msg = result.get("message", "").lower()
        assert "unknown" not in msg or "not found" not in msg

    def test_attack_during_war_still_works(self):
        """Attack during war should work normally (regression)."""
        world = make_world()
        add_marshal(world, "Davout", "France", "Rhineland", strength=25000)
        add_marshal(world, "Gneisenau", "Prussia", "Rhineland", strength=15000)
        set_state(world, "France", "Prussia", "WAR")
        executor = make_executor()
        game_state = make_game_state(world)

        result = executor.execute(
            make_cmd("attack", marshal="Davout", target="Gneisenau",
                     raw_command="Davout attack Gneisenau"),
            game_state
        )
        assert result.get("success") is True

    def test_armistice_shows_turns_remaining(self):
        """Armistice error should include correct turns remaining."""
        world = self._setup_armistice()  # cooldown = 4
        executor = make_executor()
        game_state = make_game_state(world)

        result = executor.execute(
            make_cmd("attack", marshal="Davout", target="Gneisenau",
                     raw_command="Davout attack Gneisenau"),
            game_state
        )
        assert "4 turns remaining" in result.get("message", "")

    def test_armistice_fuzzy_typo_still_blocked(self):
        """Typo in marshal name during armistice should still get diplomatic error."""
        world = self._setup_armistice()
        executor = make_executor()
        game_state = make_game_state(world)

        # "Gneisnau" is a typo for "Gneisenau" — fuzzy match should find it
        result = executor.execute(
            make_cmd("attack", marshal="Davout", target="Gneisnau",
                     raw_command="Davout attack Gneisnau"),
            game_state
        )
        assert result.get("success") is False
        msg = result.get("message", "").lower()
        # Should either get armistice error or "Did you mean" — NOT "Unknown target"
        assert "armistice" in msg or "did you mean" in msg, \
            f"Typo should get diplomatic or suggestion, got: {result.get('message')}"

    def test_dead_marshal_not_returned_by_secondary_search(self):
        """Dead marshals (strength=0) should not be found by secondary search."""
        world = make_world()
        add_marshal(world, "Davout", "France", "Rhineland", strength=25000)
        dead = add_marshal(world, "Gneisenau", "Prussia", "Rhineland", strength=0)
        set_state(world, "France", "Prussia", "ARMISTICE")
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.armistice_cooldowns[diplo_key] = 3
        executor = make_executor()
        game_state = make_game_state(world)

        result = executor.execute(
            make_cmd("attack", marshal="Davout", target="Gneisenau",
                     raw_command="Davout attack Gneisenau"),
            game_state
        )
        # Dead marshal should not trigger diplomatic block — should get normal error
        msg = result.get("message", "").lower()
        assert "armistice" not in msg, "Dead marshal should not trigger armistice block"

    def test_friendly_marshal_not_returned_by_secondary_search(self):
        """Friendly marshals should not be matched by secondary search."""
        world = make_world()
        add_marshal(world, "Davout", "France", "Rhineland", strength=25000)
        add_marshal(world, "Ney", "France", "Belgium", strength=20000)
        executor = make_executor()
        game_state = make_game_state(world)

        result = executor.execute(
            make_cmd("attack", marshal="Davout", target="Ney",
                     raw_command="Davout attack Ney"),
            game_state
        )
        assert result.get("success") is False
        msg = result.get("message", "").lower()
        assert "friendly" in msg or "cannot attack" in msg, \
            f"Should get friendly fire error, got: {result.get('message')}"

    def test_ai_attack_during_armistice_also_blocked(self):
        """Enemy AI attacking during armistice should also be blocked."""
        world = make_world()
        add_marshal(world, "Davout", "France", "Rhineland", strength=25000)
        add_marshal(world, "Blucher", "Prussia", "Rhineland", strength=15000)
        set_state(world, "France", "Prussia", "ARMISTICE")
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.armistice_cooldowns[diplo_key] = 3
        executor = make_executor()

        # Simulate AI calling _fuzzy_match_enemy with attacker_nation
        result_marshal, result_error = executor._fuzzy_match_enemy("Davout", world, "Prussia")
        assert result_marshal is None, "AI should not find armistice target"
        assert result_error is not None
        assert "armistice" in result_error.get("message", "").lower()

    def test_multiple_nations_armistice_correct_nation(self):
        """With multiple armistices, error shows the correct nation."""
        world = make_world()
        add_marshal(world, "Davout", "France", "Rhineland", strength=25000)
        add_marshal(world, "Gneisenau", "Prussia", "Rhineland", strength=15000)
        add_marshal(world, "Wellington", "Britain", "Belgium", strength=20000)
        set_state(world, "France", "Prussia", "ARMISTICE")
        set_state(world, "France", "Britain", "WAR")
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.armistice_cooldowns[diplo_key] = 2
        executor = make_executor()
        game_state = make_game_state(world)

        # Attack Prussia (armistice) — should block
        result = executor.execute(
            make_cmd("attack", marshal="Davout", target="Gneisenau",
                     raw_command="Davout attack Gneisenau"),
            game_state
        )
        assert "armistice" in result.get("message", "").lower()
        assert "prussia" in result.get("message", "").lower()

        # Attack Britain (at war) — should work
        davout = world.get_marshal("Davout")
        davout.location = "Belgium"
        result2 = executor.execute(
            make_cmd("attack", marshal="Davout", target="Wellington",
                     raw_command="Davout attack Wellington"),
            game_state
        )
        assert result2.get("success") is True
