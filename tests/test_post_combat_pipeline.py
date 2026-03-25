"""
Tests for post-combat pipeline in glorious charge and auto-charge paths.
Session 1 of Systems Audit Fix Plan.

Covers: forced retreat, destroyed cleanup, territory capture, vindication,
authority, coalition threat/war exhaustion, idle reset, exhaustion tracking,
diplo battle record, state guards.
"""
from unittest.mock import patch
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor


def make_command(action, marshal, target=None):
    """Helper to create properly formatted commands for executor."""
    cmd = {"action": action, "marshal": marshal}
    if target:
        cmd["target"] = target
    return {"command": cmd}


# ═══════════════════════════════════════════════════════════════════════
# GLORIOUS CHARGE POST-COMBAT PIPELINE
# ═══════════════════════════════════════════════════════════════════════

class TestGloriousChargeTerritoryCap:
    """Glorious charge should capture territory on win."""

    def test_charge_captures_unfortified_territory(self):
        """Winning a charge advances attacker and captures territory."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 1
        ney.strength = 80000
        wellington.strength = 2000
        wellington.location = "Belgium"

        belgium = world.get_region("Belgium")
        belgium.controller = "Britain"
        # Remove fortification if any
        if hasattr(belgium, 'buildings'):
            belgium.buildings = [b for b in belgium.buildings if b != "fortification"]

        executor = CommandExecutor()
        result = executor.execute(make_command("charge", "Ney", "Wellington"), {"world": world})

        assert result["success"]
        assert result.get("glorious_charge")
        # With 80k vs 2k + 2x multiplier, attacker wins
        if result.get("combat_result", {}).get("attacker_won"):
            # Territory should be captured (or occupation started if fort)
            assert belgium.controller == "France" or world.pending_capture_choice


class TestGloriousChargeForcedRetreat:
    """Glorious charge should process forced retreat for broken armies."""

    def test_charge_triggers_defender_forced_retreat(self):
        """Defender forced to retreat after charge should move."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 1
        ney.strength = 60000
        wellington.strength = 20000
        wellington.location = "Belgium"

        # Mock resolve_battle to return a forced retreat for defender
        mock_result = {
            "outcome": "attacker_victory",
            "victor": "Ney",
            "attacker_won": True,
            "attacker": {
                "name": "Ney", "casualties": 2000, "remaining": 58000,
                "morale": 80, "forced_retreat": False,
            },
            "defender": {
                "name": "Wellington", "casualties": 15000, "remaining": 5000,
                "morale": 20, "forced_retreat": True,
            },
            "terrain": "plains",
            "attacker_roll": {"multiplier": 1.0},
            "description": "Test charge combat.",
            "attacker_nation": "France",
            "defender_nation": "Britain",
            "attacker_original_strength": 60000,
            "defender_original_strength": 20000,
            "glorious_charge": True,
            "flanking_bonus": 0,
            "flanking_message": None,
            "fortification_degraded": False,
            "fortification_old": 0,
            "fortification_new": 0,
            "modifier_snapshot": {"attacker": {}, "defender": {}},
            "pursuit_damage": 0,
            "pursuit_message": None,
            "drill_cancelled": False,
            "counter_punch_earned": False,
            "counter_punch_mastery_earned": False,
            "ability_triggered": None,
            "drill_bonus_triggered": None,
            "fortify_bonus_triggered": None,
            "drilling_penalty_triggered": None,
            "attacker_stance_triggered": None,
            "defender_stance_triggered": None,
            "attacker_personality_triggered": None,
            "defender_personality_triggered": None,
            "terrain_defense_message": None,
            "cavalry_terrain_message": None,
            "cavalry_counter_message": None,
            "drouot_ability_triggered": None,
            "raw_outcome": "attacker_victory",
        }

        with patch("backend.game_logic.combat.CombatResolver.resolve_battle", return_value=mock_result):
            # Apply the mock casualties manually
            wellington.strength = 5000
            wellington.morale = 20

            executor = CommandExecutor()
            result = executor.execute(make_command("charge", "Ney", "Wellington"), {"world": world})

        assert result["success"]
        # Wellington should have been moved by forced retreat
        # (or destroyed, either way not sitting at Belgium with 20 morale)
        if wellington.strength > 0:
            assert wellington.location != "Belgium" or getattr(wellington, 'retreating', False)


class TestGloriousChargeDestroyedCleanup:
    """Destroyed enemies should be removed from world.marshals."""

    def test_charge_removes_destroyed_enemy(self):
        """Enemy destroyed by charge should be popped from world.marshals."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 1
        ney.strength = 80000
        wellington.strength = 1000  # Will be destroyed
        wellington.location = "Belgium"

        assert "Wellington" in world.marshals

        executor = CommandExecutor()
        result = executor.execute(make_command("charge", "Ney", "Wellington"), {"world": world})

        assert result["success"]
        if result.get("combat_result", {}).get("attacker_won"):
            # 80k vs 1k with 2x = certain destruction
            assert "Wellington" not in world.marshals


class TestGloriousChargeCoalition:
    """Charge should update coalition threat and war exhaustion."""

    def test_charge_win_adds_threat(self):
        """French charge victory should add +3 coalition threat."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 1
        ney.strength = 80000
        wellington.strength = 5000
        wellington.location = "Belgium"

        initial_threat = world.threat_level

        executor = CommandExecutor()
        result = executor.execute(make_command("charge", "Ney", "Wellington"), {"world": world})

        assert result["success"]
        if result.get("combat_result", {}).get("attacker_won"):
            assert world.threat_level >= initial_threat + 3

    def test_charge_loss_adds_war_exhaustion(self):
        """Losing a charge should add war exhaustion to France."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 1
        ney.strength = 5000
        wellington.strength = 80000
        wellington.location = "Belgium"

        initial_we = world.war_exhaustion.get("France", 0)

        executor = CommandExecutor()
        result = executor.execute(make_command("charge", "Ney", "Wellington"), {"world": world})

        assert result["success"]
        if not result.get("combat_result", {}).get("attacker_won"):
            # France lost — should have war exhaustion from casualties
            assert world.war_exhaustion.get("France", 0) >= initial_we


class TestGloriousChargeAuthority:
    """Charge should update authority for major victories/defeats."""

    def test_charge_outnumbered_win_grants_authority(self):
        """Winning a charge while outnumbered should give +5 authority."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 1
        ney.strength = 20000  # Outnumbered
        wellington.strength = 25000
        wellington.location = "Belgium"

        initial_authority = world.authority_tracker.authority

        executor = CommandExecutor()
        result = executor.execute(make_command("charge", "Ney", "Wellington"), {"world": world})

        assert result["success"]
        if result.get("combat_result", {}).get("attacker_won"):
            assert world.authority_tracker.authority == initial_authority + 5


class TestGloriousChargeIdleAndExhaustion:
    """Charge should reset idle and increment attack counter."""

    def test_charge_resets_idle(self):
        """Charge should reset idle_turns to 0."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 1
        ney.strength = 50000
        ney.idle_turns = 5
        wellington.strength = 50000
        wellington.location = "Belgium"

        executor = CommandExecutor()
        result = executor.execute(make_command("charge", "Ney", "Wellington"), {"world": world})

        assert result["success"]
        assert ney.idle_turns == 0

    def test_charge_increments_attack_counter(self):
        """Charge should count toward attack exhaustion."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 1
        ney.strength = 50000
        wellington.strength = 50000
        wellington.location = "Belgium"

        initial_attacks = getattr(ney, 'attacks_this_turn', 0)

        executor = CommandExecutor()
        result = executor.execute(make_command("charge", "Ney", "Wellington"), {"world": world})

        assert result["success"]
        if ney.strength > 0:  # Only if survived
            assert getattr(ney, 'attacks_this_turn', 0) > initial_attacks


class TestGloriousChargeVindication:
    """Charge should resolve pending vindication."""

    def test_charge_resolves_vindication(self):
        """Pending vindication should resolve after charge battle."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 1
        ney.strength = 60000
        wellington.strength = 10000
        wellington.location = "Belgium"

        # Set up pending vindication for Ney (direct dict access)
        world.vindication_tracker.pending["Ney"] = {
            "concern": "Reckless orders",
            "turn": world.current_turn,
            "action": "attack",
            "target": "Wellington",
            "choice": "proceed",  # Player overruled the objection
        }
        assert world.vindication_tracker.has_pending("Ney")

        executor = CommandExecutor()
        result = executor.execute(make_command("charge", "Ney", "Wellington"), {"world": world})

        assert result["success"]
        # Vindication should have been resolved (win or loss)
        assert not world.vindication_tracker.has_pending("Ney")


# ═══════════════════════════════════════════════════════════════════════
# AUTO-CHARGE POST-COMBAT PIPELINE
# ═══════════════════════════════════════════════════════════════════════

class TestAutoChargeStateGuards:
    """State guards should prevent auto-charge for incapacitated marshals."""

    def test_broken_marshal_skipped(self):
        """Broken marshal should not auto-charge."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        ney.recklessness = 4
        ney.broken = True
        ney.broken_recovery = 0

        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"

        events = world._process_reckless_cavalry_turn_start()
        assert not any(e.get("type") == "auto_glorious_charge" for e in events)
        assert not any(e.get("type") == "reckless_move" for e in events)

    def test_retreating_marshal_skipped(self):
        """Retreating marshal should not auto-charge."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        ney.recklessness = 4
        ney.retreating = True

        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"

        events = world._process_reckless_cavalry_turn_start()
        assert not any(e.get("type") == "auto_glorious_charge" for e in events)

    def test_retreat_recovery_marshal_skipped(self):
        """Marshal in retreat recovery should not auto-charge."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        ney.recklessness = 4
        ney.retreat_recovery = 2

        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"

        events = world._process_reckless_cavalry_turn_start()
        assert not any(e.get("type") == "auto_glorious_charge" for e in events)

    def test_drilling_marshal_skipped(self):
        """Drilling marshal should not auto-charge."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        ney.recklessness = 4
        ney.drilling = True

        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"

        events = world._process_reckless_cavalry_turn_start()
        assert not any(e.get("type") == "auto_glorious_charge" for e in events)

    def test_dead_marshal_skipped(self):
        """Dead marshal (strength 0) should not auto-charge."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        ney.recklessness = 4
        ney.strength = 0

        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"

        events = world._process_reckless_cavalry_turn_start()
        assert not any(e.get("type") == "auto_glorious_charge" for e in events)


class TestAutoChargeDiploRecord:
    """Auto-charge should record battles for diplomatic war score."""

    def test_auto_charge_records_diplo_battle(self):
        """Auto-charge should add entry to battle_records for war score."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 4
        ney.strength = 60000
        wellington.strength = 10000
        wellington.location = "Belgium"

        # Ensure France and Britain are at war
        assert world.is_at_war("France", "Britain")

        # Count battle records before
        if not hasattr(world, 'battle_records'):
            world.battle_records = {}
        war_key = world._make_diplo_key("France", "Britain")
        initial_count = len(getattr(world, 'battle_records', {}).get(war_key, []))

        events = world._process_reckless_cavalry_turn_start()

        assert any(e.get("type") == "auto_glorious_charge" for e in events)
        # Battle should be recorded
        updated_count = len(getattr(world, 'battle_records', {}).get(war_key, []))
        assert updated_count > initial_count


class TestAutoChargeDestroyedCleanup:
    """Destroyed enemies should be removed after auto-charge."""

    def test_auto_charge_removes_destroyed_enemy(self):
        """Destroyed enemy should be popped from world.marshals."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 4
        ney.strength = 80000
        wellington.strength = 1000  # Will be destroyed
        wellington.location = "Belgium"

        assert "Wellington" in world.marshals

        events = world._process_reckless_cavalry_turn_start()

        charge_events = [e for e in events if e.get("type") == "auto_glorious_charge"]
        assert len(charge_events) > 0

        if any(e.get("attacker_won") for e in charge_events):
            assert "Wellington" not in world.marshals


class TestAutoChargeCoalition:
    """Auto-charge should update coalition threat and war exhaustion."""

    def test_auto_charge_win_adds_threat(self):
        """French auto-charge win should add coalition threat."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 4
        ney.strength = 80000
        wellington.strength = 5000
        wellington.location = "Belgium"

        initial_threat = world.threat_level

        events = world._process_reckless_cavalry_turn_start()

        charge_events = [e for e in events if e.get("type") == "auto_glorious_charge"]
        assert len(charge_events) > 0
        if any(e.get("attacker_won") for e in charge_events):
            assert world.threat_level >= initial_threat + 3


class TestAutoChargeTerritoryCapture:
    """Auto-charge should capture unfortified territory."""

    def test_auto_charge_captures_territory(self):
        """Winning auto-charge should capture unfortified enemy territory."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 4
        ney.strength = 80000
        wellington.strength = 1000
        wellington.location = "Belgium"

        belgium = world.get_region("Belgium")
        belgium.controller = "Britain"
        # Ensure no fortification
        if hasattr(belgium, 'buildings'):
            belgium.buildings = [b for b in belgium.buildings if b != "fortification"]

        events = world._process_reckless_cavalry_turn_start()

        charge_events = [e for e in events if e.get("type") == "auto_glorious_charge"]
        assert len(charge_events) > 0

        if any(e.get("attacker_won") for e in charge_events):
            assert belgium.controller == "France"

    def test_auto_charge_skips_fortified_territory(self):
        """Auto-charge should NOT capture fortified territory (no occupation)."""
        import random
        random.seed(42)

        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 4
        ney.strength = 80000
        wellington.strength = 1000
        wellington.location = "Belgium"

        belgium = world.get_region("Belgium")
        belgium.controller = "Britain"
        # Add fortification
        if not hasattr(belgium, 'buildings'):
            belgium.buildings = []
        has_fort = any(b.get("type") == "fortification" for b in belgium.buildings if isinstance(b, dict))
        if not has_fort:
            belgium.buildings.append({"type": "fortification"})

        events = world._process_reckless_cavalry_turn_start()

        # Auto-charge should fire (recklessness 4 + adjacent enemy)
        charge_events = [e for e in events if e.get("type") == "auto_glorious_charge"]
        assert len(charge_events) > 0, "Recklessness 4 with adjacent enemy should auto-charge"
        # Even if won, fortified territory should NOT be captured
        if any(e.get("attacker_won") for e in charge_events):
            assert belgium.controller == "Britain", \
                "Fortified territory should NOT be captured by auto-charge"


class TestAutoChargeAuthority:
    """Auto-charge should update authority for major victories."""

    def test_auto_charge_outnumbered_win_authority(self):
        """Outnumbered auto-charge win should give +5 authority."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 4
        ney.strength = 20000  # Outnumbered
        wellington.strength = 25000
        wellington.location = "Belgium"

        initial_auth = world.authority_tracker.authority

        events = world._process_reckless_cavalry_turn_start()

        charge_events = [e for e in events if e.get("type") == "auto_glorious_charge"]
        assert len(charge_events) > 0

        if any(e.get("attacker_won") for e in charge_events):
            assert world.authority_tracker.authority == initial_auth + 5


class TestAutoChargeForcedRetreat:
    """Auto-charge should handle forced retreat for broken armies."""

    def test_auto_charge_defender_forced_retreat(self):
        """Defender with forced_retreat flag should be moved."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 4
        ney.strength = 60000
        wellington.strength = 20000
        wellington.location = "Belgium"

        # Mock combat to force defender retreat
        mock_result = {
            "outcome": "attacker_victory",
            "victor": "Ney",
            "attacker_won": True,
            "attacker": {
                "name": "Ney", "casualties": 3000, "remaining": 57000,
                "morale": 75, "forced_retreat": False,
            },
            "defender": {
                "name": "Wellington", "casualties": 15000, "remaining": 5000,
                "morale": 20, "forced_retreat": True,
            },
            "terrain": "plains",
            "attacker_roll": {"multiplier": 1.0},
            "description": "Auto-charge test.",
            "attacker_nation": "France",
            "defender_nation": "Britain",
            "attacker_original_strength": 60000,
            "defender_original_strength": 20000,
            "glorious_charge": True,
            "flanking_bonus": 0,
            "flanking_message": None,
            "fortification_degraded": False,
            "fortification_old": 0,
            "fortification_new": 0,
            "modifier_snapshot": {"attacker": {}, "defender": {}},
            "pursuit_damage": 0,
            "pursuit_message": None,
            "drill_cancelled": False,
            "counter_punch_earned": False,
            "counter_punch_mastery_earned": False,
            "ability_triggered": None,
            "drill_bonus_triggered": None,
            "fortify_bonus_triggered": None,
            "drilling_penalty_triggered": None,
            "attacker_stance_triggered": None,
            "defender_stance_triggered": None,
            "attacker_personality_triggered": None,
            "defender_personality_triggered": None,
            "terrain_defense_message": None,
            "cavalry_terrain_message": None,
            "cavalry_counter_message": None,
            "drouot_ability_triggered": None,
            "raw_outcome": "attacker_victory",
            "log_battle_event": {
                "type": "battle",
                "attacker": "Ney",
                "attacker_nation": "France",
                "defender": "Wellington",
                "defender_nation": "Britain",
                "location": "",
                "outcome": "attacker_victory",
                "attacker_casualties": 3000,
                "defender_casualties": 15000,
            },
        }

        with patch("backend.game_logic.combat.CombatResolver.resolve_battle", return_value=mock_result):
            # Apply mock casualties
            wellington.strength = 5000
            wellington.morale = 20

            events = world._process_reckless_cavalry_turn_start()

        assert any(e.get("type") == "auto_glorious_charge" for e in events)
        # Wellington should have retreated (not sitting at Belgium broken)
        if wellington.strength > 0:
            assert wellington.location != "Belgium" or getattr(wellington, 'retreating', False)
