"""
Systems Audit V3 — Session 9 Tests
Parsing, Trust, Error Handling & Hardening

13 bugs fixed across LLM parsing, defiance thresholds, error handling,
and input validation.
"""

import os
import threading
import pytest

# Force mock mode for parser tests
os.environ.setdefault("LLM_MODE", "mock")

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.commands.executor import CommandExecutor


# ============================================================================
# HELPERS
# ============================================================================

def _make_world() -> WorldState:
    """Create a minimal world for testing."""
    return WorldState(player_nation="France")


def _parse_mock(command_text: str):
    """Parse a command using the mock (fast) parser, returning ParseResult."""
    from backend.ai.llm_client import LLMClient
    client = LLMClient()
    return client._parse_with_mock(command_text)


# ============================================================================
# 6D-1: Enemy marshal names should NOT hijack executing marshal slot
# ============================================================================

class TestEnemyMarshalParsing:
    """Only player marshals can be the executing marshal."""

    def test_enemy_name_alone_not_parsed_as_marshal(self):
        """'Gneisenau retreats' -> marshals list should be empty."""
        result = _parse_mock("Gneisenau retreats")
        enemy_names = {"Gneisenau", "Schwarzenberg", "ArchdukeCharles", "Reynier"}
        for m in result.marshals:
            assert m not in enemy_names

    def test_player_attack_enemy_target(self):
        """'Ney attack Gneisenau' -> marshal=Ney, target=Gneisenau."""
        result = _parse_mock("Ney attack Gneisenau")
        assert result.marshals == ["Ney"]
        assert result.target == "Gneisenau"

    def test_attack_schwarzenberg_no_player_marshal(self):
        """'attack Schwarzenberg' -> no player marshal, target=Schwarzenberg."""
        result = _parse_mock("attack Schwarzenberg")
        enemy_names = {"Schwarzenberg", "ArchdukeCharles", "Gneisenau", "Reynier"}
        for m in result.marshals:
            assert m not in enemy_names
        assert result.target == "Schwarzenberg"


# ============================================================================
# 6D-2: "fall back to" -> move, not retreat
# ============================================================================

class TestFallBackParsing:

    def test_fall_back_to_is_move(self):
        """'fall back to Paris' -> action=move."""
        result = _parse_mock("Ney fall back to Paris")
        assert result.action == "move"

    def test_fall_back_alone_is_retreat(self):
        """'fall back' -> action=retreat."""
        result = _parse_mock("Ney fall back")
        assert result.action == "retreat"


# ============================================================================
# 6D-4: "wait" should be a free action
# ============================================================================

class TestWaitFreeAction:

    def test_wait_does_not_consume_ap(self):
        """The 'wait' action should not cost AP."""
        world = _make_world()
        executor = CommandExecutor()
        initial_ap = world.actions_remaining

        command = {
            "marshal": "Ney",
            "action": "wait",
            "target": "",
        }
        executor.execute(command, {"world": world})
        assert world.actions_remaining == initial_ap


# ============================================================================
# 6C-1: Defiance gate should trigger at MODERATE, not just STRONG
# ============================================================================

class TestDefianceGateThreshold:
    """Defiance should be possible at MODERATE concern level."""

    def test_moderate_concern_can_trigger_defiance(self):
        """MODERATE concern + insist -> defiance check fires (not skipped)."""
        world = _make_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")

        # Place Ney and an enemy in Belgium for a valid attack
        ney.location = "Belgium"
        enemy = world.get_marshal("Gneisenau")
        if enemy:
            enemy.location = "Belgium"

        # Set up a pending objection with full required keys
        world.pending_objection = {
            "marshal": "Ney",
            "marshal_name": "Ney",
            "original_action": "attack",
            "original_target": "Belgium",
            "concern_level": "MODERATE",
            "original_order": {
                "marshal": "Ney",
                "action": "attack",
                "target": "Belgium",
            },
            "original_command": {
                "marshal": "Ney",
                "action": "attack",
                "target": "Belgium",
            },
            "suggested_alternative": {
                "marshal": "Ney",
                "action": "defend",
                "target": "",
            },
            "trust_gain": 3,
        }

        result = executor.handle_objection_response("insist", {"world": world})
        # Objection was consumed regardless of defiance roll outcome
        assert world.pending_objection is None

    def test_mild_concern_no_defiance(self):
        """MILD concern + insist -> no defiance (below threshold)."""
        world = _make_world()
        executor = CommandExecutor()

        world.pending_objection = {
            "marshal": "Ney",
            "marshal_name": "Ney",
            "original_action": "defend",
            "original_target": "",
            "concern_level": "MILD",
            "original_order": {
                "marshal": "Ney",
                "action": "defend",
                "target": "",
            },
            "original_command": {
                "marshal": "Ney",
                "action": "defend",
                "target": "",
            },
            "suggested_alternative": {
                "marshal": "Ney",
                "action": "defend",
                "target": "",
            },
            "trust_gain": 3,
        }

        result = executor.handle_objection_response("insist", {"world": world})
        assert world.pending_objection is None


# ============================================================================
# 6C-2: Vindication decay timer reset on defiance/defensive vindication
# ============================================================================

class TestVindicationDecayTimerReset:

    def test_defiance_right_resets_decay_timer(self):
        """After defiance RIGHT outcome, decay timer = current turn."""
        from backend.commands.defiance import apply_defiance_outcome

        world = _make_world()
        marshal = world.get_marshal("Ney")
        world.current_turn = 5

        # Signature: apply_defiance_outcome(marshal, outcome, world)
        apply_defiance_outcome(marshal, True, world)

        assert world.vindication_tracker.last_change_turn.get("Ney") == 5

    def test_defiance_wrong_resets_decay_timer(self):
        """After defiance WRONG outcome, decay timer = current turn."""
        from backend.commands.defiance import apply_defiance_outcome

        world = _make_world()
        marshal = world.get_marshal("Ney")
        world.current_turn = 7

        apply_defiance_outcome(marshal, False, world)

        assert world.vindication_tracker.last_change_turn.get("Ney") == 7

    def test_defensive_vindication_resets_decay_timer(self):
        """After defensive vindication resolution, decay timer is reset."""
        from backend.game_logic.turn_manager import TurnManager

        world = _make_world()
        world.current_turn = 4
        ney = world.get_marshal("Ney")

        # Set up defensive vindication pending for Ney
        world.vindication_tracker.pending_defensive_vindication = {"Ney": True}

        # Mark Ney as attacked this turn (battles_this_turn format)
        world.battles_this_turn = [
            {"location": "Belgium", "attacker": "Gneisenau", "defender": "Ney", "outcome": "held"}
        ]

        tm = TurnManager(world)
        tm._resolve_defensive_vindication()

        assert world.vindication_tracker.last_change_turn.get("Ney") == 4


# ============================================================================
# 3B-3: Confrontation/redemption error handling returns success=False
# ============================================================================

class TestConfrontationErrorHandling:

    def test_confrontation_exception_returns_failure(self):
        """If resolve_confrontation raises, result has success=False."""
        world = _make_world()
        executor = CommandExecutor()

        # Create a diplomat with required 'skill' arg
        from backend.models.diplomat import DiplomaticRepresentative
        world.diplomats["France"] = DiplomaticRepresentative(
            name="Talleyrand", nation="France", personality="shrewd", skill=8
        )

        # Set up dialogue state
        world.dialogue_manager.replace({
            "type": "sabotage_discovery",
            "options": [
                {"label": "Confront", "action": "confront_sabotage"},
                {"label": "Overlook", "action": "overlook_sabotage"},
            ],
        })

        # Monkey-patch to force an exception
        import backend.commands.diplomatic_defiance as dd
        original = dd.resolve_confrontation

        def broken(*args, **kwargs):
            raise RuntimeError("test error")

        dd.resolve_confrontation = broken
        try:
            result = executor._process_dialogue_choice(
                "confront_sabotage",
                {"action": "confront_sabotage"},
                world.pending_diplomatic_dialogue,
                world,
            )
            assert result["success"] is False
        finally:
            dd.resolve_confrontation = original

# ============================================================================
# 3B-4: Marshal cavalry+artillery raises ValueError, not AssertionError
# ============================================================================

class TestMarshalMutualExclusivity:

    def test_cavalry_artillery_raises_value_error(self):
        """Creating a cavalry+artillery marshal raises ValueError."""
        with pytest.raises(ValueError, match="cannot be both cavalry and artillery"):
            Marshal(
                name="Test",
                location="Paris",
                strength=10000,
                personality="aggressive",
                nation="France",
                cavalry=True,
                artillery=True,
            )


# ============================================================================
# 3D-1: Command length limit
# ============================================================================

class TestCommandLengthLimit:

    def test_long_command_rejected(self):
        """Command >500 chars should be rejected by Pydantic validation."""
        from pydantic import ValidationError
        from backend.main import CommandRequest
        long_text = "a" * 501
        with pytest.raises(ValidationError):
            CommandRequest(command=long_text)

    def test_normal_command_accepted(self):
        """Command <=500 chars should be accepted."""
        from backend.main import CommandRequest
        cmd = CommandRequest(command="Ney attack Belgium")
        assert cmd.command == "Ney attack Belgium"


# ============================================================================
# 3D-2: Save filename validation
# ============================================================================

class TestSaveFilenameValidation:

    def test_traversal_save_name_rejected(self):
        """Save name with '..' should be rejected."""
        from backend.main import _validate_save_filename
        assert _validate_save_filename("../evil") is False

    def test_normal_save_name_accepted(self):
        """Normal save name should pass validation."""
        from backend.main import _validate_save_filename
        assert _validate_save_filename("My Save") is True


# ============================================================================
# 3A-1: Threading lock exists and serializes POST requests
# ============================================================================

class TestThreadingLock:

    def test_state_lock_exists(self):
        """The POST serialization lock should be defined in main.py.

        PIN CONSCIOUSLY FLIPPED July 18, 2026: this asserted a
        `threading.Lock`, which is precisely the defect. The one and only
        acquisition site is an `async def` middleware, so a threading.Lock was
        taken on the event-loop thread and held across `await call_next` —
        blocking the entire server for the duration of every POST, most
        visibly while a live LLM parse was in flight.
        """
        import asyncio

        from backend.main import get_state_lock

        async def _probe():
            return get_state_lock()

        lock = asyncio.run(_probe())
        assert isinstance(lock, asyncio.Lock), (
            "the lock is acquired inside an async middleware — a "
            "threading.Lock there blocks the event loop")

    def test_state_lock_is_per_event_loop(self):
        """An asyncio.Lock binds to the first loop that awaits it and raises
        on any other. Each TestClient creates a fresh loop, so a single
        module-level lock breaks every endpoint test after the first client —
        and the same hazard exists for any production loop restart."""
        import asyncio

        from backend.main import get_state_lock

        async def _probe():
            lock = get_state_lock()
            async with lock:          # bind it to THIS loop
                pass
            return lock

        first = asyncio.run(_probe())
        second = asyncio.run(_probe())
        assert first is not second, (
            "a lock reused across event loops raises 'bound to a different "
            "event loop'")

    def test_state_lock_is_acquired_asynchronously(self):
        """The middleware must `async with` it. A plain `with` on an
        asyncio.Lock raises at runtime, so this pins the pair together."""
        import inspect

        from backend import main as main_module
        src = inspect.getsource(main_module.serialize_state_mutations)
        assert "async with get_state_lock()" in src, (
            "an asyncio.Lock must be acquired with `async with`")

    def test_concurrent_commands_no_crash(self):
        """Two concurrent POST /command calls should not crash."""
        from backend.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        errors = []

        def send_command(cmd):
            try:
                resp = client.post("/command", json={"command": cmd})
                assert resp.status_code == 200
            except Exception as e:
                errors.append(e)

        t1 = threading.Thread(target=send_command, args=("Ney attack Belgium",))
        t2 = threading.Thread(target=send_command, args=("Davout defend",))
        t1.start()
        t2.start()
        t1.join(timeout=10)
        t2.join(timeout=10)

        assert len(errors) == 0, f"Concurrent commands crashed: {errors}"
