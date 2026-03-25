"""
Systems Audit V2 — Session 7: Missing Coverage Tests

V2-38: get_llm_game_state() fog of war filtering
V2-39: diplomatic_trust_applied cap survives save/load
V2-40: Multi-cavalry recklessness independence
"""

import io
import contextlib

from backend.models.world_state import WorldState
from backend.models.intel import UNKNOWN, STALE, PARTIAL, FULL  # noqa: F401


def _suppress():
    return contextlib.redirect_stdout(io.StringIO())


# ═══════════════════════════════════════════════════════════════════
# V2-38: get_llm_game_state() fog of war filtering
# ═══════════════════════════════════════════════════════════════════

class TestLlmGameStateFog:
    """Verify get_llm_game_state() respects fog of war for enemy positions."""

    def test_enemy_hidden_at_none_visibility(self):
        """Enemies at NONE visibility should not appear in LLM game state."""
        world = WorldState(player_nation="France")
        wellington = world.get_marshal("Wellington")
        wellington.strength = 30000
        wellington.location = "Vienna"  # Far from France

        # Set visibility to NONE for Vienna
        intel = world.get_region_intel("Vienna")
        intel.visibility = UNKNOWN

        # Build enemies dict using same logic as get_llm_game_state
        from backend.models.intel import VISIBILITY_PRIORITY
        enemies = {}
        for m in world.get_enemy_marshals():
            if m.strength > 0:
                region_intel = world.get_region_intel(m.location)
                vis = region_intel.visibility
                if VISIBILITY_PRIORITY.get(vis, 0) >= VISIBILITY_PRIORITY[PARTIAL]:
                    enemies[m.name] = {
                        "location": m.location,
                        "strength": int(m.strength) if vis == FULL else "unknown",
                        "nation": m.nation,
                    }

        assert "Wellington" not in enemies, \
            "Wellington at NONE visibility should be hidden from LLM"

    def test_enemy_hidden_at_stale_visibility(self):
        """Enemies at STALE visibility should not appear in LLM game state."""
        world = WorldState(player_nation="France")
        wellington = world.get_marshal("Wellington")
        wellington.strength = 30000
        wellington.location = "Vienna"

        intel = world.get_region_intel("Vienna")
        intel.visibility = STALE

        from backend.models.intel import VISIBILITY_PRIORITY
        enemies = {}
        for m in world.get_enemy_marshals():
            if m.strength > 0:
                region_intel = world.get_region_intel(m.location)
                vis = region_intel.visibility
                if VISIBILITY_PRIORITY.get(vis, 0) >= VISIBILITY_PRIORITY[PARTIAL]:
                    enemies[m.name] = {"location": m.location, "nation": m.nation}

        assert "Wellington" not in enemies, \
            "Wellington at STALE visibility should be hidden from LLM"

    def test_enemy_visible_at_partial(self):
        """Enemies at PARTIAL visibility should appear with 'unknown' strength."""
        world = WorldState(player_nation="France")
        wellington = world.get_marshal("Wellington")
        wellington.strength = 30000
        wellington.location = "Belgium"

        intel = world.get_region_intel("Belgium")
        intel.visibility = PARTIAL

        from backend.models.intel import VISIBILITY_PRIORITY
        enemies = {}
        for m in world.get_enemy_marshals():
            if m.strength > 0:
                region_intel = world.get_region_intel(m.location)
                vis = region_intel.visibility
                if VISIBILITY_PRIORITY.get(vis, 0) >= VISIBILITY_PRIORITY[PARTIAL]:
                    enemies[m.name] = {
                        "location": m.location,
                        "strength": int(m.strength) if vis == FULL else "unknown",
                        "nation": m.nation,
                    }

        assert "Wellington" in enemies, "Wellington at PARTIAL should be visible"
        assert enemies["Wellington"]["strength"] == "unknown", \
            "PARTIAL visibility should show 'unknown' strength"

    def test_enemy_visible_at_full(self):
        """Enemies at FULL visibility should appear with exact strength."""
        world = WorldState(player_nation="France")
        wellington = world.get_marshal("Wellington")
        wellington.strength = 30000
        wellington.location = "Belgium"

        intel = world.get_region_intel("Belgium")
        intel.visibility = FULL

        from backend.models.intel import VISIBILITY_PRIORITY
        enemies = {}
        for m in world.get_enemy_marshals():
            if m.strength > 0:
                region_intel = world.get_region_intel(m.location)
                vis = region_intel.visibility
                if VISIBILITY_PRIORITY.get(vis, 0) >= VISIBILITY_PRIORITY[PARTIAL]:
                    enemies[m.name] = {
                        "location": m.location,
                        "strength": int(m.strength) if vis == FULL else "unknown",
                        "nation": m.nation,
                    }

        assert "Wellington" in enemies, "Wellington at FULL should be visible"
        assert enemies["Wellington"]["strength"] == 30000, \
            "FULL visibility should show exact strength"


# ═══════════════════════════════════════════════════════════════════
# V2-39: diplomatic_trust_applied survives save/load
# ═══════════════════════════════════════════════════════════════════

class TestDiplomaticTrustAppliedSaveLoad:
    """V2-16 fix: diplomatic_trust_applied must survive save/load roundtrip."""

    def test_diplomatic_trust_applied_roundtrip(self):
        """Save then load should preserve diplomatic_trust_applied values."""
        world = WorldState(player_nation="France")
        world.diplomatic_trust_applied = {
            "Ney": 15,
            "Davout": -10,
            "Grouchy": 5,
        }

        data = world.to_dict()
        loaded = WorldState.from_dict(data)

        assert loaded.diplomatic_trust_applied == {"Ney": 15, "Davout": -10, "Grouchy": 5}

    def test_diplomatic_trust_applied_empty_default(self):
        """Missing diplomatic_trust_applied in save data should default to empty dict."""
        world = WorldState(player_nation="France")
        data = world.to_dict()
        # Simulate old save format missing the field
        data.pop("diplomatic_trust_applied", None)

        loaded = WorldState.from_dict(data)
        assert loaded.diplomatic_trust_applied == {}

    def test_diplomatic_trust_applied_values_are_int(self):
        """Values should be int after roundtrip (Godot safety)."""
        world = WorldState(player_nation="France")
        world.diplomatic_trust_applied = {"Ney": 15}

        data = world.to_dict()
        loaded = WorldState.from_dict(data)

        for key, val in loaded.diplomatic_trust_applied.items():
            assert isinstance(val, int), f"{key} trust should be int, got {type(val)}"


# ═══════════════════════════════════════════════════════════════════
# V2-40: Multi-cavalry recklessness independence
# ═══════════════════════════════════════════════════════════════════

class TestMultiCavalryRecklessness:
    """Two aggressive cavalry marshals at recklessness 4+ should both auto-charge."""

    def test_two_cavalry_both_charge_independently(self):
        """Two reckless cavalry marshals should each auto-charge their own targets."""
        world = WorldState(player_nation="France")

        # Ney is already cavalry + aggressive
        ney = world.get_marshal("Ney")
        ney.recklessness = 4
        ney.strength = 40000
        ney.location = "Belgium"

        # Create a second aggressive cavalry marshal
        from backend.models.marshal import Marshal
        with _suppress():
            murat = Marshal("Murat", "Paris", 35000, "aggressive", "France", cavalry=True)
        murat.recklessness = 4
        world.marshals["Murat"] = murat

        # Place enemies for each
        wellington = world.get_marshal("Wellington")
        wellington.strength = 20000
        wellington.location = "Belgium"  # Same region as Ney → direct charge

        blucher = world.get_marshal("Blucher")
        blucher.strength = 20000
        blucher.location = "Lyon"  # Adjacent to Paris → Murat charges

        events = world._process_reckless_cavalry_turn_start()

        charge_events = [e for e in events if e.get("type") == "auto_glorious_charge"]
        charging_marshals = {e.get("marshal") for e in charge_events}

        # Both cavalry marshals should have charged
        assert "Ney" in charging_marshals, "Ney at recklessness 4 should auto-charge"
        assert "Murat" in charging_marshals, "Murat at recklessness 4 should auto-charge"

    def test_recklessness_resets_after_charge(self):
        """Both marshals' recklessness should reset to 0 after auto-charging."""
        world = WorldState(player_nation="France")

        ney = world.get_marshal("Ney")
        ney.recklessness = 4
        ney.strength = 40000

        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"  # Adjacent to Ney
        wellington.strength = 10000

        events = world._process_reckless_cavalry_turn_start()

        charge_events = [e for e in events if e.get("type") == "auto_glorious_charge"]
        assert len(charge_events) > 0, "Should auto-charge at recklessness 4"
        assert ney.recklessness == 0, "Recklessness should reset after charge"
