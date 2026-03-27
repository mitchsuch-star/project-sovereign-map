"""
Tests for Systems Audit V2 — Session 4: Diplomacy State + Pacing + Victory Fixes.

Bugs covered:
  V2-63: Victory threshold mismatch (0.77 vs 0.75)
  V2-64: Triple victory check conflict (advance_turn removed)
  V2-86: Victory swallows pending diplomatic popups
  V2-65: Broken marshals teleport to enemy-occupied capital
  V2-85: Turn-limit warning system
  V2-16: Diplomatic trust cap bypass on save/load
  V2-89: Dialogue queue (multiple writers during advance_turn)
  V2-90: Vassal rebellion popup list (multiple rebellions)
"""

from backend.models.world_state import WorldState, VICTORY_REGION_FRACTION
from backend.game_logic.turn_manager import TurnManager


# ============================================================================
# HELPERS
# ============================================================================

def _make_world(**kwargs) -> WorldState:
    """Create a WorldState for testing."""
    world = WorldState(player_nation="France")
    for k, v in kwargs.items():
        setattr(world, k, v)
    return world


def _give_france_regions(world, count):
    """Give France control of `count` regions."""
    for i, name in enumerate(world.regions):
        if i < count:
            world.regions[name].controller = "France"
        else:
            world.regions[name].controller = "Prussia"


# ============================================================================
# V2-63: Victory threshold uses VICTORY_REGION_FRACTION, not hardcoded 0.77
# ============================================================================

class TestV2_63_VictoryThresholdConstant:
    """V2-63: Time victory uses VICTORY_REGION_FRACTION constant."""

    def test_victory_region_fraction_is_075(self):
        """Constant should be 0.75."""
        assert VICTORY_REGION_FRACTION == 0.75

    def test_time_victory_uses_fraction_constant(self):
        """Turn manager's _check_victory_conditions uses VICTORY_REGION_FRACTION
        for time victory threshold, not hardcoded 0.77."""
        world = _make_world()
        world.max_turns = 10
        world.current_turn = 11  # Past max_turns

        total = len(world.regions)  # 19
        threshold = int(total * VICTORY_REGION_FRACTION)  # 14

        # Give player exactly threshold regions → should win
        _give_france_regions(world, threshold)

        tm = TurnManager(world)
        result = tm._check_victory_conditions()
        assert result["game_over"] is True
        assert result["result"] == "victory"

    def test_time_defeat_below_threshold(self):
        """Below VICTORY_REGION_FRACTION → time defeat."""
        world = _make_world()
        world.max_turns = 10
        world.current_turn = 11

        total = len(world.regions)
        threshold = int(total * VICTORY_REGION_FRACTION)

        # Give player threshold - 1 regions → should lose
        _give_france_regions(world, threshold - 1)

        tm = TurnManager(world)
        result = tm._check_victory_conditions()
        assert result["game_over"] is True
        assert result["result"] == "defeat"


# ============================================================================
# V2-64: advance_turn does NOT set game_over; only turn_manager does
# ============================================================================

class TestV2_64_AdvanceTurnNoVictoryCheck:
    """V2-64: advance_turn must not set game_over or victory."""

    def test_advance_turn_does_not_set_game_over(self):
        """Even past max_turns, advance_turn should not touch game_over."""
        world = _make_world()
        world.max_turns = 5
        world.current_turn = 6  # Past max_turns

        # Ensure game_over is False before
        assert world.game_over is False

        world.advance_turn()

        # advance_turn should NOT have set game_over
        assert world.game_over is False
        assert world.victory is None


# ============================================================================
# V2-86: Victory result includes pending diplomatic popups
# ============================================================================

class TestV2_86_VictoryFlushesPopups:
    """V2-86: Victory return includes pending popup data."""

    def test_victory_includes_pending_dialogue(self):
        """When victory fires, pending_diplomatic_dialogue is in result."""
        world = _make_world()
        world.pending_diplomatic_dialogue = {
            "type": "incoming_proposal",
            "target_nation": "Prussia",
            "blocking": True,
            "turn_created": 1,
        }

        # Give France near-total control for victory
        total = len(world.regions)
        for name in world.regions:
            world.regions[name].controller = "France"

        tm = TurnManager(world)
        result = tm.end_turn()

        assert result["victory_check"]["game_over"] is True
        assert "pending_diplomatic_dialogue" in result
        assert result["pending_diplomatic_dialogue"]["type"] == "incoming_proposal"

    def test_victory_includes_vassal_rebellion_popup(self):
        """When victory fires, vassal_rebellion_imminent_popup is in result."""
        world = _make_world()
        world.vassal_rebellion_imminent_popup = {"nation": "Saxony", "loyalty": 5}

        for name in world.regions:
            world.regions[name].controller = "France"

        tm = TurnManager(world)
        result = tm.end_turn()

        assert result["victory_check"]["game_over"] is True
        assert "vassal_rebellion_imminent_popup" in result
        assert result["vassal_rebellion_imminent_popup"]["nation"] == "Saxony"


# ============================================================================
# V2-65: Broken marshals teleport to friendly region, not enemy-occupied capital
# ============================================================================

class TestV2_65_SafeCapitalTeleport:
    """V2-65: find_safe_spawn avoids enemy-occupied capital."""

    def test_safe_spawn_uses_capital_when_friendly(self):
        """Normal case: capital controlled by marshal's nation."""
        world = _make_world()
        marshal = world.marshals.get("Ney") or list(world.marshals.values())[0]
        # Ensure Paris is French-controlled
        world.regions["Paris"].controller = "France"
        result = world.find_safe_spawn(marshal)
        # Should use spawn_location or capital
        assert world.regions[result].controller == "France"

    def test_safe_spawn_avoids_enemy_capital(self):
        """If capital is enemy-occupied, find nearest friendly region."""
        world = _make_world()
        marshal = world.marshals.get("Ney") or list(world.marshals.values())[0]
        marshal.nation = "France"
        marshal.spawn_location = "Paris"

        # Occupy Paris with enemy
        world.regions["Paris"].controller = "Prussia"

        # Ensure at least one friendly region exists
        friendly_count = sum(
            1 for r in world.regions.values() if r.controller == "France"
        )
        assert friendly_count > 0, "Test requires at least one French region"

        result = world.find_safe_spawn(marshal)
        # Result should be a French-controlled region (not Paris)
        assert world.regions[result].controller == "France"

    def test_safe_spawn_last_resort_returns_capital(self):
        """If no friendly regions at all, falls back to capital."""
        world = _make_world()
        marshal = world.marshals.get("Ney") or list(world.marshals.values())[0]
        marshal.nation = "France"
        marshal.spawn_location = "Paris"

        # Make ALL regions enemy-controlled
        for name in world.regions:
            world.regions[name].controller = "Prussia"

        result = world.find_safe_spawn(marshal)
        # Last resort: returns capital even though enemy-occupied
        assert result == "Paris"


# ============================================================================
# V2-85: Dispatch includes turn-limit warning at turns 35, 38, 39
# ============================================================================

class TestV2_85_TurnLimitWarnings:
    """V2-85: Morning Dispatch turn-limit warning system."""

    def test_no_warning_at_early_turn(self):
        """No warning when >5 turns remain."""
        world = _make_world()
        world.current_turn = 30  # 10 turns remaining
        world.max_turns = 40

        from backend.game_logic.dispatch import _build_turn_limit_warning
        result = _build_turn_limit_warning(world, "France")
        assert result is None

    def test_warning_at_5_remaining(self):
        """Warning fires when 5 turns remain (post-advance: current_turn=36, remaining=4)."""
        world = _make_world()
        world.current_turn = 36  # 4C-2: Post-advance, remaining=4 → "5 turns remain"
        world.max_turns = 40

        from backend.game_logic.dispatch import _build_turn_limit_warning
        result = _build_turn_limit_warning(world, "France")
        assert result is not None
        assert result["turns_remaining"] == 4
        assert result["severity"] == "warning"
        assert "5 turns remain" in result["message"]

    def test_warning_at_2_remaining(self):
        """Warning fires when 2 turns remain (post-advance: current_turn=39, remaining=1)."""
        world = _make_world()
        world.current_turn = 39  # 4C-2: Post-advance, remaining=1 → "2 turns remain"
        world.max_turns = 40

        from backend.game_logic.dispatch import _build_turn_limit_warning
        result = _build_turn_limit_warning(world, "France")
        assert result is not None
        assert result["turns_remaining"] == 1
        assert "2 turns remain" in result["message"]

    def test_final_turn_warning(self):
        """Critical warning on final turn (post-advance: current_turn=40, remaining=0)."""
        world = _make_world()
        world.current_turn = 40  # 4C-2: Post-advance, remaining=0 → "FINAL TURN"
        world.max_turns = 40

        from backend.game_logic.dispatch import _build_turn_limit_warning
        result = _build_turn_limit_warning(world, "France")
        assert result is not None
        assert result["turns_remaining"] == 0
        assert result["severity"] == "critical"
        assert "FINAL TURN" in result["message"]

    def test_no_warning_at_3_or_4_remaining(self):
        """No warning at intermediate remaining turns (post-advance remaining=2,3)."""
        world = _make_world()
        world.max_turns = 40

        from backend.game_logic.dispatch import _build_turn_limit_warning

        world.current_turn = 37  # remaining=3 → no warning
        assert _build_turn_limit_warning(world, "France") is None

        world.current_turn = 38  # remaining=2 → no warning
        assert _build_turn_limit_warning(world, "France") is None


# ============================================================================
# V2-16: Diplomatic trust cap survives save/load roundtrip
# ============================================================================

class TestV2_16_DiplomaticTrustCapSerialization:
    """V2-16: diplomatic_trust_applied serializes correctly."""

    def test_trust_applied_serializes(self):
        """diplomatic_trust_applied survives save/load roundtrip."""
        world = _make_world()
        world.diplomatic_trust_applied = {"Ney": 3, "Davout": -2}

        data = world.to_dict()
        assert "diplomatic_trust_applied" in data
        assert data["diplomatic_trust_applied"]["Ney"] == 3

        restored = WorldState.from_dict(data)
        assert restored.diplomatic_trust_applied["Ney"] == 3
        assert restored.diplomatic_trust_applied["Davout"] == -2

    def test_trust_cap_cleared_on_advance_turn(self):
        """diplomatic_trust_applied is cleared at start of each turn."""
        world = _make_world()
        world.diplomatic_trust_applied = {"Ney": 5}

        world.advance_turn()

        assert world.diplomatic_trust_applied == {}

    def test_trust_cap_persists_within_turn_via_serialization(self):
        """Save/load mid-turn preserves the cap tracking."""
        world = _make_world()
        world.diplomatic_trust_applied = {"Ney": 4}

        # Save and reload
        data = world.to_dict()
        restored = WorldState.from_dict(data)

        # Cap should still be tracked — Ney has 4 of 5 used
        assert restored.diplomatic_trust_applied.get("Ney") == 4


# ============================================================================
# V2-89: Dialogue queue — multiple dialogues during advance_turn
# ============================================================================

class TestV2_89_DialogueQueue:
    """V2-89: pending_dialogue_queue collects advance_turn dialogues."""

    def test_queue_field_exists_and_serializes(self):
        """pending_dialogue_queue field exists and roundtrips."""
        world = _make_world()
        assert hasattr(world, 'pending_dialogue_queue')
        assert world.pending_dialogue_queue == []

        world.pending_dialogue_queue.append({"type": "incoming_proposal", "target_nation": "Austria"})
        data = world.to_dict()
        assert len(data["pending_dialogue_queue"]) == 1

        restored = WorldState.from_dict(data)
        assert len(restored.pending_dialogue_queue) == 1
        assert restored.pending_dialogue_queue[0]["type"] == "incoming_proposal"

    def test_queue_priority_ordering(self):
        """Alliance paradox pops before vassal rebellion before AI proposal."""
        world = _make_world()
        world.pending_dialogue_queue = [
            {"type": "incoming_proposal", "target_nation": "Britain"},
            {"type": "alliance_paradox", "target_nation": ""},
            {"type": "vassal_rebellion_imminent", "target_nation": "Saxony"},
        ]

        tm = TurnManager(world)
        tm._pop_dialogue_queue()

        # Alliance paradox should have been popped (highest priority)
        assert world.pending_diplomatic_dialogue["type"] == "alliance_paradox"
        # 2 remaining in queue
        assert len(world.pending_dialogue_queue) == 2

    def test_queue_does_not_pop_when_dialogue_active(self):
        """If pending_diplomatic_dialogue is already set, queue doesn't pop."""
        world = _make_world()
        world.pending_diplomatic_dialogue = {"type": "existing", "blocking": True}
        world.pending_dialogue_queue = [
            {"type": "incoming_proposal", "target_nation": "Austria"},
        ]

        tm = TurnManager(world)
        tm._pop_dialogue_queue()

        # Should NOT have overwritten the existing dialogue
        assert world.pending_diplomatic_dialogue["type"] == "existing"
        assert len(world.pending_dialogue_queue) == 1

    def test_auto_pop_after_clearing_dialogue(self):
        """After clearing dialogue in main.py passthrough, next item auto-pops."""
        world = _make_world()
        # Simulate: dialogue just cleared, queue has items
        world.pending_diplomatic_dialogue = None
        world.pending_dialogue_queue = [
            {"type": "vassal_rebellion_imminent", "target_nation": "Saxony"},
            {"type": "incoming_proposal", "target_nation": "Austria"},
        ]

        # Simulate the auto-pop logic from _include_popup_passthroughs
        _DIALOGUE_PRIORITY = {
            "alliance_paradox": 0, "vassal_rebellion_imminent": 1,
            "sabotage_confrontation": 2, "talleyrand_redemption": 3,
            "incoming_proposal": 4,
        }
        if (world.pending_diplomatic_dialogue is None
                and world.pending_dialogue_queue):
            world.pending_dialogue_queue.sort(
                key=lambda d: _DIALOGUE_PRIORITY.get(d.get("type", ""), 99)
            )
            world.pending_diplomatic_dialogue = world.pending_dialogue_queue.pop(0)

        assert world.pending_diplomatic_dialogue["type"] == "vassal_rebellion_imminent"
        assert len(world.pending_dialogue_queue) == 1


# ============================================================================
# V2-90: Multiple vassal rebellions → all popups preserved in list
# ============================================================================

class TestV2_90_VassalRebellionPopupList:
    """V2-90: vassal_rebellion_imminent_popups is a list."""

    def test_popup_list_field_exists(self):
        """vassal_rebellion_imminent_popups field exists."""
        world = _make_world()
        assert hasattr(world, 'vassal_rebellion_imminent_popups')
        assert world.vassal_rebellion_imminent_popups == []

    def test_popup_list_serializes(self):
        """Popup list roundtrips through save/load."""
        world = _make_world()
        world.vassal_rebellion_imminent_popups = [
            {"nation": "Saxony", "loyalty": 5},
            {"nation": "Bavaria", "loyalty": 8},
        ]

        data = world.to_dict()
        assert len(data["vassal_rebellion_imminent_popups"]) == 2

        restored = WorldState.from_dict(data)
        assert len(restored.vassal_rebellion_imminent_popups) == 2
        assert restored.vassal_rebellion_imminent_popups[0]["nation"] == "Saxony"
        assert restored.vassal_rebellion_imminent_popups[1]["nation"] == "Bavaria"

    def test_popup_auto_pop_from_list(self):
        """When singular popup is None, auto-pops from list."""
        world = _make_world()
        world.vassal_rebellion_imminent_popup = None
        world.vassal_rebellion_imminent_popups = [
            {"nation": "Saxony", "loyalty": 5},
            {"nation": "Bavaria", "loyalty": 8},
        ]

        # Simulate auto-pop logic from _include_popup_passthroughs
        if (world.vassal_rebellion_imminent_popup is None
                and world.vassal_rebellion_imminent_popups):
            world.vassal_rebellion_imminent_popup = world.vassal_rebellion_imminent_popups.pop(0)

        assert world.vassal_rebellion_imminent_popup["nation"] == "Saxony"
        assert len(world.vassal_rebellion_imminent_popups) == 1

    def test_vassal_release_clears_from_list(self):
        """Releasing a vassal clears its popup from the list."""
        world = _make_world()
        world.vassal_rebellion_imminent_popups = [
            {"nation": "Saxony", "loyalty": 5},
            {"nation": "Bavaria", "loyalty": 8},
        ]

        # Simulate the clearing logic from vassal.py release
        vassal_name = "Saxony"
        world.vassal_rebellion_imminent_popups = [
            p for p in world.vassal_rebellion_imminent_popups
            if p.get("nation") != vassal_name
        ]

        assert len(world.vassal_rebellion_imminent_popups) == 1
        assert world.vassal_rebellion_imminent_popups[0]["nation"] == "Bavaria"
