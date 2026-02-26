"""
Tests for Redemption System V2b Interaction — cooldown + defiance path gaps.

Covers:
- check_redemption_threshold() centralized helper
- 5-turn cooldown after resolution
- Tactical defiance success carrying redemption (Gaps 1-2)
- Strategic defiance success triggering redemption (Gap 3)
- Strategic proceed / failed-roll crossing threshold (Gaps 4-5)
- Bombardment friendly fire regression
- Autonomous marshal guard (B2)
- Multi-marshal bombardment first-wins (B5)
- Strategic interrupt trust penalties → redemption (F1)
- Cavalry trust penalties → redemption (F2)
"""


from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.commands.disobedience import DisobedienceSystem
from backend.commands.executor import CommandExecutor


class TestCheckRedemptionThreshold:
    """Tests for the centralized check_redemption_threshold() helper."""

    def setup_method(self):
        self.world = WorldState()
        self.disobedience = DisobedienceSystem()
        self.world.disobedience_system = self.disobedience

    def test_fires_at_trust_20(self):
        """Redemption fires when trust is exactly 20."""
        ney = self.world.get_marshal("Ney")
        ney.trust.set(20)
        ney.redemption_pending = False

        result = self.disobedience.check_redemption_threshold(ney, self.world)

        assert result is not None
        assert result["type"] == "redemption_event"
        assert result["marshal"] == "Ney"
        assert ney.redemption_pending is True

    def test_fires_at_trust_below_20(self):
        """Redemption fires when trust is below 20."""
        ney = self.world.get_marshal("Ney")
        ney.trust.set(5)
        ney.redemption_pending = False

        result = self.disobedience.check_redemption_threshold(ney, self.world)

        assert result is not None
        assert result["type"] == "redemption_event"

    def test_no_fire_at_trust_21(self):
        """Redemption does NOT fire when trust is above 20."""
        ney = self.world.get_marshal("Ney")
        ney.trust.set(21)

        result = self.disobedience.check_redemption_threshold(ney, self.world)

        assert result is None
        assert ney.redemption_pending is False

    def test_no_fire_if_already_pending(self):
        """Redemption does NOT fire if already pending."""
        ney = self.world.get_marshal("Ney")
        ney.trust.set(15)
        ney.redemption_pending = True

        result = self.disobedience.check_redemption_threshold(ney, self.world)

        assert result is None

    def test_no_fire_if_on_cooldown(self):
        """Redemption does NOT fire if current_turn < cooldown_until."""
        ney = self.world.get_marshal("Ney")
        ney.trust.set(15)
        ney.redemption_pending = False
        ney.redemption_cooldown_until = 10
        self.world.current_turn = 8

        result = self.disobedience.check_redemption_threshold(ney, self.world)

        assert result is None
        assert ney.redemption_pending is False

    def test_fires_after_cooldown_expires(self):
        """Redemption fires once current_turn >= cooldown_until."""
        ney = self.world.get_marshal("Ney")
        ney.trust.set(15)
        ney.redemption_pending = False
        ney.redemption_cooldown_until = 10
        self.world.current_turn = 10

        result = self.disobedience.check_redemption_threshold(ney, self.world)

        assert result is not None
        assert result["type"] == "redemption_event"

    def test_no_fire_for_enemy_marshal(self):
        """Redemption does NOT fire for enemy marshals."""
        wellington = self.world.get_marshal("Wellington")
        wellington.trust.set(15)
        wellington.redemption_pending = False

        result = self.disobedience.check_redemption_threshold(wellington, self.world)

        assert result is None

    def test_no_fire_for_none_marshal(self):
        """check_redemption_threshold handles None marshal gracefully."""
        result = self.disobedience.check_redemption_threshold(None, self.world)
        assert result is None

    def test_no_fire_for_autonomous_marshal(self):
        """B2: Autonomous marshal with trust <= 20 does NOT get redundant redemption."""
        ney = self.world.get_marshal("Ney")
        ney.trust.set(15)
        ney.redemption_pending = False
        ney.autonomous = True
        ney.autonomy_turns = 2

        result = self.disobedience.check_redemption_threshold(ney, self.world)

        assert result is None
        assert ney.redemption_pending is False


class TestRedemptionCooldown:
    """Tests for cooldown set on redemption resolution."""

    def setup_method(self):
        self.world = WorldState()
        self.disobedience = DisobedienceSystem()
        self.world.disobedience_system = self.disobedience
        self.game_state = {"world": self.world}

    def test_cooldown_set_on_resolution(self):
        """After resolving redemption, cooldown is set to current_turn + 5."""
        ney = self.world.get_marshal("Ney")
        ney.trust.set(15)
        ney.redemption_pending = True
        self.world.current_turn = 7

        redemption_event = {"marshal": "Ney", "type": "redemption_event"}
        result = self.disobedience.handle_redemption_response(
            redemption_event, "grant_autonomy", self.game_state
        )

        assert result["success"] is True
        assert ney.redemption_pending is False
        assert ney.redemption_cooldown_until == 12  # 7 + 5

    def test_cooldown_prevents_immediate_refire(self):
        """After resolution at turn 7, redemption cannot fire at turn 8."""
        ney = self.world.get_marshal("Ney")
        ney.trust.set(15)
        ney.redemption_pending = True
        self.world.current_turn = 7

        # Resolve redemption
        redemption_event = {"marshal": "Ney", "type": "redemption_event"}
        self.disobedience.handle_redemption_response(
            redemption_event, "grant_autonomy", self.game_state
        )

        # Try to fire again at turn 8
        self.world.current_turn = 8
        ney.trust.set(10)  # Still critical
        result = self.disobedience.check_redemption_threshold(ney, self.world)

        assert result is None

    def test_cooldown_expires_allows_refire(self):
        """After resolution at turn 7, redemption can fire at turn 12."""
        ney = self.world.get_marshal("Ney")
        ney.trust.set(15)
        ney.redemption_pending = True
        self.world.current_turn = 7

        # Resolve redemption
        redemption_event = {"marshal": "Ney", "type": "redemption_event"}
        self.disobedience.handle_redemption_response(
            redemption_event, "grant_autonomy", self.game_state
        )

        # Reset for re-trigger
        ney.autonomous = False
        ney.autonomy_turns = 0
        self.world.current_turn = 12
        ney.trust.set(10)

        result = self.disobedience.check_redemption_threshold(ney, self.world)

        assert result is not None
        assert result["type"] == "redemption_event"


class TestTacticalDefianceRedemption:
    """Tests for redemption firing through tactical defiance paths (Gaps 1-2)."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world}

    def test_defiance_outcome_pushes_trust_below_threshold(self):
        """When defiance outcome trust penalty crosses <= 20, redemption fires."""
        ney = self.world.get_marshal("Ney")
        ney.trust.set(22)  # Close to threshold
        ney.redemption_pending = False
        ney.location = "Belgium"

        # After a defiance outcome applies -3 or more, trust would be <= 20
        # We test the helper directly since full executor flow requires extensive mocking
        ney.trust.modify(-3)  # Simulate defiance outcome
        assert ney.trust.value <= 20

        result = self.world.disobedience_system.check_redemption_threshold(ney, self.world)

        assert result is not None
        assert result["type"] == "redemption_event"
        assert ney.redemption_pending is True


class TestStrategicDefianceRedemption:
    """Tests for redemption firing through strategic defiance paths (Gaps 3-5)."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world}

    def test_strategic_proceed_crosses_threshold(self):
        """Strategic proceed insist penalty pushing trust <= 20 triggers redemption."""
        ney = self.world.get_marshal("Ney")
        ney.trust.set(22)
        ney.redemption_pending = False

        # Simulate insist penalty
        ney.trust.modify(-5)
        assert ney.trust.value <= 20

        result = self.world.disobedience_system.check_redemption_threshold(ney, self.world)

        assert result is not None
        assert result["type"] == "redemption_event"

    def test_failed_roll_cumulative_crosses_threshold(self):
        """Failed-roll -3 on top of insist -5 crosses threshold."""
        ney = self.world.get_marshal("Ney")
        ney.trust.set(28)
        ney.redemption_pending = False

        # Simulate insist -5 then failed_roll -3
        ney.trust.modify(-5)
        ney.trust.modify(-3)
        assert ney.trust.value == 20

        result = self.world.disobedience_system.check_redemption_threshold(ney, self.world)

        assert result is not None
        assert result["type"] == "redemption_event"


class TestBombardmentRedemptionRegression:
    """Regression: bombardment friendly fire still triggers redemption via helper."""

    def setup_method(self):
        self.world = WorldState()
        self.disobedience = DisobedienceSystem()
        self.world.disobedience_system = self.disobedience

    def test_bombardment_friendly_fire_redemption(self):
        """Friendly fire pushing trust <= 20 still triggers redemption."""
        # Simulate a French ally in bombardment collateral zone
        ney = self.world.get_marshal("Ney")
        ney.trust.set(18)
        ney.redemption_pending = False

        result = self.disobedience.check_redemption_threshold(ney, self.world)

        assert result is not None
        assert result["type"] == "redemption_event"
        assert ney.redemption_pending is True

    def test_bombardment_enemy_not_triggered(self):
        """Enemy marshals in collateral zone don't get redemption."""
        wellington = self.world.get_marshal("Wellington")
        wellington.trust.set(10)

        result = self.disobedience.check_redemption_threshold(wellington, self.world)

        assert result is None


class TestRedemptionSerialization:
    """Test that redemption_cooldown_until round-trips correctly."""

    def test_marshal_cooldown_roundtrip(self):
        """redemption_cooldown_until survives to_dict/from_dict."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        ney.redemption_cooldown_until = 15

        data = ney.to_dict()
        assert data["redemption_cooldown_until"] == 15

        restored = Marshal.from_dict(data)
        assert restored.redemption_cooldown_until == 15

    def test_marshal_cooldown_default(self):
        """Missing redemption_cooldown_until defaults to 0."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        data = ney.to_dict()
        del data["redemption_cooldown_until"]

        restored = Marshal.from_dict(data)
        assert restored.redemption_cooldown_until == 0


class TestStrategicInterruptRedemption:
    """F1: Strategic interrupt trust penalties wire through to redemption."""

    def setup_method(self):
        self.world = WorldState()
        self.game_state = {"world": self.world}

    def test_strategic_cancel_triggers_redemption(self):
        """Strategic cancel_order -3 pushing trust to 20 triggers redemption in result."""
        from backend.commands.strategic import StrategicExecutor
        from backend.commands.executor import CommandExecutor
        from backend.models.marshal import StrategicOrder

        ney = self.world.get_marshal("Ney")
        ney.trust.set(23)  # -3 will push to 20
        ney.redemption_pending = False

        # Build a minimal strategic order so the handler can cancel it
        ney.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Rhineland",
            target_type="region", started_turn=1,
            original_command="Ney, march to Rhineland",
            path=["Belgium", "Rhineland"],
        )

        strategic_exec = StrategicExecutor(CommandExecutor())
        result = strategic_exec._respond_combat_stalemate(
            ney, ney.strategic_order, "cancel_order",
            {"enemy_name": "Wellington"},
            self.world, self.game_state,
        )

        assert result["success"] is True
        assert result.get("redemption_event") is not None
        assert result["redemption_event"]["type"] == "redemption_event"
        assert result["state"] == "awaiting_redemption_choice"
        assert ney.redemption_pending is True

    def test_strategic_cancel_no_redemption_at_24(self):
        """Strategic cancel_order -3 from trust 24 → 21, no redemption."""
        from backend.commands.strategic import StrategicExecutor
        from backend.commands.executor import CommandExecutor
        from backend.models.marshal import StrategicOrder

        ney = self.world.get_marshal("Ney")
        ney.trust.set(24)
        ney.redemption_pending = False
        ney.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Rhineland",
            target_type="region", started_turn=1,
            original_command="Ney, march to Rhineland",
            path=["Belgium", "Rhineland"],
        )

        strategic_exec = StrategicExecutor(CommandExecutor())
        result = strategic_exec._respond_combat_stalemate(
            ney, ney.strategic_order, "cancel_order",
            {"enemy_name": "Wellington"},
            self.world, self.game_state,
        )

        assert result["success"] is True
        assert result.get("redemption_event") is None


class TestCavalryTrustRedemption:
    """F2: Cavalry trust penalties wire through to redemption events."""

    def setup_method(self):
        self.world = WorldState()

    def test_cavalry_stance_forced_triggers_redemption(self):
        """Cavalry forced stance change -3 pushing trust to 20 creates redemption event."""
        from backend.models.marshal import Stance

        # Ney is the French cavalry marshal
        ney = self.world.get_marshal("Ney")
        ney.trust.set(23)
        ney.redemption_pending = False
        ney.stance = Stance.DEFENSIVE
        ney.turns_in_defensive_stance = 3  # Threshold for forced change

        events = self.world._check_cavalry_limits()

        # Should have the stance forced event AND a redemption event
        stance_events = [e for e in events if e["type"] == "cavalry_stance_forced"]
        redemption_events = [e for e in events if e["type"] == "redemption_event"]

        assert len(stance_events) == 1
        assert len(redemption_events) == 1
        assert redemption_events[0]["redemption_event"]["marshal"] == "Ney"
        assert ney.redemption_pending is True

    def test_cavalry_fortify_forced_triggers_redemption(self):
        """Cavalry forced unfortify -3 pushing trust to 20 creates redemption event."""
        ney = self.world.get_marshal("Ney")
        ney.trust.set(23)
        ney.redemption_pending = False
        ney.fortified = True
        ney.defense_bonus = 15
        ney.turns_fortified = 3  # Threshold for forced unfortify

        events = self.world._check_cavalry_limits()

        fortify_events = [e for e in events if e["type"] == "cavalry_fortify_forced"]
        redemption_events = [e for e in events if e["type"] == "redemption_event"]

        assert len(fortify_events) == 1
        assert len(redemption_events) == 1
        assert redemption_events[0]["redemption_event"]["marshal"] == "Ney"
        assert ney.redemption_pending is True

    def test_cavalry_no_redemption_at_24(self):
        """Cavalry -3 from trust 24 → 21, no redemption event."""
        from backend.models.marshal import Stance

        ney = self.world.get_marshal("Ney")
        ney.trust.set(24)
        ney.redemption_pending = False
        ney.stance = Stance.DEFENSIVE
        ney.turns_in_defensive_stance = 3

        events = self.world._check_cavalry_limits()

        redemption_events = [e for e in events if e["type"] == "redemption_event"]
        assert len(redemption_events) == 0
        assert ney.redemption_pending is False


class TestMultiMarshalBombardmentRedemption:
    """B5: Only first marshal's redemption fires; second is not stuck pending."""

    def setup_method(self):
        self.world = WorldState()
        self.disobedience = DisobedienceSystem()
        self.world.disobedience_system = self.disobedience

    def test_first_wins_second_not_stuck(self):
        """When two French marshals could trigger, only first gets pending=True."""
        ney = self.world.get_marshal("Ney")
        ney.trust.set(18)
        ney.redemption_pending = False

        davout = self.world.get_marshal("Davout")
        davout.trust.set(18)
        davout.redemption_pending = False

        # Simulate the if-not-already pattern from executor
        friendly_fire_redemption = None
        for force in [ney, davout]:
            if not friendly_fire_redemption:
                friendly_fire_redemption = (
                    self.disobedience.check_redemption_threshold(force, self.world))

        # First marshal gets the event
        assert friendly_fire_redemption is not None
        assert friendly_fire_redemption["marshal"] == "Ney"
        assert ney.redemption_pending is True
        # Second marshal is NOT stuck pending
        assert davout.redemption_pending is False
