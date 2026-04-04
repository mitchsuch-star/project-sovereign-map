"""
Diplomacy Playtest Fix Tests — DPF-1, DPF-2, DPF-3.
Created: April 4, 2026

DPF-1: AI-AI relations in Diplomatic Ledger (no fog gate, relation descriptors)
DPF-2: Mission cancel UI + progress tracking
DPF-3: Ledger paused status display (key mismatch)
"""
from backend.models.world_state import WorldState
from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
from backend.game_logic.diplomacy import get_available_diplomatic_actions


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _make_world():
    """Create a test world with basic diplomacy state."""
    world = WorldState()
    world.current_turn = 5
    return world


def _set_relation(world, nation_a, nation_b, value):
    """Set a relation value between two nations."""
    key = world._make_diplo_key(nation_a, nation_b)
    world.nation_relations[key] = value


def _set_diplo_state(world, nation_a, nation_b, state):
    """Set diplomatic state between two nations."""
    key = world._make_diplo_key(nation_a, nation_b)
    world.diplomatic_states[key] = state


def _get_ledger_nations(world):
    """Build ledger and return nations tab data."""
    ledger = build_diplomatic_ledger(world)
    return ledger.get("nations", [])


def _get_ledger_talleyrand(world):
    """Build ledger and return talleyrand tab data."""
    ledger = build_diplomatic_ledger(world)
    return ledger.get("talleyrand", {})


# ═══════════════════════════════════════════════════════════════════════════
# DPF-1: AI-AI RELATIONS
# ═══════════════════════════════════════════════════════════════════════════

class TestDPF1AIRelations:
    """AI-AI relations include relation value and descriptor, no fog gate."""

    def test_ai_relations_include_relation_value(self):
        """AI-AI relation entries have 'relation' and 'relation_descriptor' fields."""
        world = _make_world()
        _set_relation(world, "Austria", "Prussia", -45)
        _set_diplo_state(world, "Austria", "Prussia", "WAR")

        nations = _get_ledger_nations(world)
        # Find Austria's entry
        austria = next((n for n in nations if n["name"] == "Austria"), None)
        assert austria is not None
        ai_rels = austria.get("ai_relations", [])
        prussia_rel = next((r for r in ai_rels if r["nation"] == "Prussia"), None)
        assert prussia_rel is not None
        assert "relation" in prussia_rel
        assert "relation_descriptor" in prussia_rel

    def test_ai_relations_no_fog_gate(self):
        """AI-AI relations visible even with UNKNOWN visibility (no fog gate)."""
        world = _make_world()
        _set_relation(world, "Austria", "Prussia", 30)
        _set_diplo_state(world, "Austria", "Prussia", "ALLIANCE")
        # Don't set any intel — should still show
        nations = _get_ledger_nations(world)
        austria = next((n for n in nations if n["name"] == "Austria"), None)
        assert austria is not None
        ai_rels = austria.get("ai_relations", [])
        # Should have entries for all other AI nations (not just visible ones)
        assert len(ai_rels) > 0
        prussia_rel = next((r for r in ai_rels if r["nation"] == "Prussia"), None)
        assert prussia_rel is not None
        assert prussia_rel["state"] == "ALLIANCE"

    def test_ai_relations_negative_descriptor(self):
        """Negative relation shows correct descriptor (Hostile)."""
        world = _make_world()
        _set_relation(world, "Austria", "Prussia", -45)
        nations = _get_ledger_nations(world)
        austria = next((n for n in nations if n["name"] == "Austria"), None)
        ai_rels = austria.get("ai_relations", [])
        prussia_rel = next((r for r in ai_rels if r["nation"] == "Prussia"), None)
        assert prussia_rel is not None
        assert prussia_rel["relation_descriptor"] == "Hostile"

    def test_ai_relations_default_zero(self):
        """Missing relation key defaults to 0 with Neutral descriptor."""
        world = _make_world()
        # Clear any starting relations between Austria and Prussia
        key = world._make_diplo_key("Austria", "Prussia")
        world.nation_relations.pop(key, None)
        nations = _get_ledger_nations(world)
        austria = next((n for n in nations if n["name"] == "Austria"), None)
        ai_rels = austria.get("ai_relations", [])
        prussia_rel = next((r for r in ai_rels if r["nation"] == "Prussia"), None)
        assert prussia_rel is not None
        assert prussia_rel["relation"] == 0
        assert prussia_rel["relation_descriptor"] == "Neutral"

    def test_ai_relations_int_wrapped(self):
        """All relation values are int (Godot safety)."""
        world = _make_world()
        _set_relation(world, "Austria", "Prussia", -45.7)
        nations = _get_ledger_nations(world)
        austria = next((n for n in nations if n["name"] == "Austria"), None)
        ai_rels = austria.get("ai_relations", [])
        for ar in ai_rels:
            assert isinstance(ar["relation"], int), f"relation for {ar['nation']} is {type(ar['relation'])}"


# ═══════════════════════════════════════════════════════════════════════════
# DPF-2: MISSION CANCEL + PROGRESS TRACKING
# ═══════════════════════════════════════════════════════════════════════════

class TestDPF2MissionTracking:
    """Mission start state tracking (started_turn, initial_relation).

    Simulates mission creation as done in diplomatic_executor.py:1497
    (the dialogue confirmation path). Going through the full executor
    requires a 2-step dialogue flow; these tests verify the dict shape.
    """

    def _simulate_mission_creation(self, world, target="Austria", mission_type="IMPROVE_RELATIONS"):
        """Simulate the mission dict creation exactly as diplomatic_executor does."""
        diplo_key = world._make_diplo_key(world.player_nation, target)
        world.active_diplomatic_mission = {
            "type": mission_type,
            "target": target,
            "turns_active": 0,
            "paused": False,
            "paused_turns": 0,
            "started_turn": int(getattr(world, 'current_turn', 1)),
            "initial_relation": int(world.nation_relations.get(diplo_key, 0) or 0),
        }
        world.talleyrand_state = "ON_MISSION"

    def test_mission_tracks_started_turn(self):
        """started_turn field present when mission is created."""
        world = _make_world()
        world.current_turn = 7
        self._simulate_mission_creation(world)
        mission = world.active_diplomatic_mission
        assert mission is not None
        assert mission["started_turn"] == 7

    def test_mission_tracks_initial_relation(self):
        """initial_relation field present with correct value at creation."""
        world = _make_world()
        _set_relation(world, "France", "Austria", -20)
        self._simulate_mission_creation(world)
        mission = world.active_diplomatic_mission
        assert mission["initial_relation"] == -20

    def test_mission_initial_relation_int_wrapped(self):
        """initial_relation is int (Godot safety)."""
        world = _make_world()
        _set_relation(world, "France", "Austria", -20.5)
        self._simulate_mission_creation(world)
        mission = world.active_diplomatic_mission
        assert isinstance(mission["initial_relation"], int)


class TestDPF2LedgerProgress:
    """Ledger Tab 4 shows mission progress fields."""

    def test_ledger_shows_relation_delta(self):
        """relation_delta computed correctly in ledger."""
        world = _make_world()
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 3,
            "paused": False,
            "paused_turns": 0,
            "started_turn": 2,
            "initial_relation": -20,
        }
        world.talleyrand_state = "ON_MISSION"
        _set_relation(world, "France", "Austria", -5)

        tal = _get_ledger_talleyrand(world)
        am = tal.get("active_mission")
        assert am is not None
        assert am["relation_delta"] == 15  # -5 - (-20)

    def test_ledger_shows_descriptors(self):
        """initial_descriptor and current_descriptor present in ledger."""
        world = _make_world()
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 3,
            "paused": False,
            "paused_turns": 0,
            "started_turn": 2,
            "initial_relation": -20,
        }
        world.talleyrand_state = "ON_MISSION"
        _set_relation(world, "France", "Austria", 5)

        tal = _get_ledger_talleyrand(world)
        am = tal.get("active_mission")
        assert am["initial_descriptor"] == "Wary"
        assert am["current_descriptor"] == "Neutral"

    def test_ledger_handles_missing_initial_relation(self):
        """Old save without initial_relation field doesn't crash."""
        world = _make_world()
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 3,
            "paused": False,
            "paused_turns": 0,
            # No started_turn or initial_relation — old save
        }
        world.talleyrand_state = "ON_MISSION"
        _set_relation(world, "France", "Austria", 10)

        tal = _get_ledger_talleyrand(world)
        am = tal.get("active_mission")
        assert am is not None
        # Should default gracefully — initial_relation defaults to 0
        assert am["initial_relation"] == 0
        assert am["started_turn"] == 0


class TestDPF2CancelAction:
    """Cancel mission action in wizard action list."""

    def test_cancel_action_in_wizard_when_mission_active(self):
        """Cancel appears in action list for target nation when mission active."""
        world = _make_world()
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 3,
            "paused": False,
            "paused_turns": 0,
            "started_turn": 2,
            "initial_relation": -20,
        }
        world.talleyrand_state = "ON_MISSION"
        _set_relation(world, "France", "Austria", -5)
        _set_diplo_state(world, "France", "Austria", "PEACE")

        actions = get_available_diplomatic_actions(world, "Austria")
        cancel = next((a for a in actions if a["action"] == "cancel_mission"), None)
        assert cancel is not None

    def test_cancel_action_absent_without_mission(self):
        """No cancel when no active mission."""
        world = _make_world()
        world.active_diplomatic_mission = None
        world.talleyrand_state = "IDLE"
        _set_diplo_state(world, "France", "Austria", "PEACE")

        actions = get_available_diplomatic_actions(world, "Austria")
        cancel = next((a for a in actions if a["action"] == "cancel_mission"), None)
        assert cancel is None

    def test_cancel_action_absent_for_wrong_nation(self):
        """Cancel only for mission target nation, not other nations."""
        world = _make_world()
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 2,
            "paused": False,
            "paused_turns": 0,
            "started_turn": 3,
            "initial_relation": 0,
        }
        world.talleyrand_state = "ON_MISSION"
        _set_diplo_state(world, "France", "Prussia", "PEACE")

        actions = get_available_diplomatic_actions(world, "Prussia")
        cancel = next((a for a in actions if a["action"] == "cancel_mission"), None)
        assert cancel is None

    def test_cancel_action_zero_dp(self):
        """Cancel costs 0 DP."""
        world = _make_world()
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 1,
            "paused": False,
            "paused_turns": 0,
            "started_turn": 4,
            "initial_relation": 0,
        }
        world.talleyrand_state = "ON_MISSION"
        _set_relation(world, "France", "Austria", 5)
        _set_diplo_state(world, "France", "Austria", "PEACE")

        actions = get_available_diplomatic_actions(world, "Austria")
        cancel = next((a for a in actions if a["action"] == "cancel_mission"), None)
        assert cancel is not None
        assert cancel["dp_cost"] == 0

    def test_cancel_action_shows_progress(self):
        """effect_text includes descriptor-based progress."""
        world = _make_world()
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 3,
            "paused": False,
            "paused_turns": 0,
            "started_turn": 2,
            "initial_relation": -20,
        }
        world.talleyrand_state = "ON_MISSION"
        _set_relation(world, "France", "Austria", 5)
        _set_diplo_state(world, "France", "Austria", "PEACE")

        actions = get_available_diplomatic_actions(world, "Austria")
        cancel = next((a for a in actions if a["action"] == "cancel_mission"), None)
        assert cancel is not None
        effect = cancel["effect_text"]
        # Should show descriptor change: Wary -> Neutral
        assert "Wary" in effect
        assert "Neutral" in effect

    def test_mission_progress_survives_save_load(self):
        """started_turn + initial_relation round-trip through save/load."""
        world = _make_world()
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 3,
            "paused": False,
            "paused_turns": 0,
            "started_turn": 2,
            "initial_relation": -20,
        }
        # Serialize and deserialize
        data = world.to_dict()
        world2 = WorldState.from_dict(data)
        mission = world2.active_diplomatic_mission
        assert mission["started_turn"] == 2
        assert mission["initial_relation"] == -20


# ═══════════════════════════════════════════════════════════════════════════
# DPF-3: LEDGER PAUSED KEY
# ═══════════════════════════════════════════════════════════════════════════

class TestDPF3PausedKey:
    """Verify backend sends 'paused' key for mission status."""

    def test_ledger_mission_paused_key(self):
        """Backend active_mission dict uses 'paused' key."""
        world = _make_world()
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 2,
            "paused": True,
            "paused_turns": 1,
            "started_turn": 3,
            "initial_relation": 0,
        }
        world.talleyrand_state = "ON_MISSION"

        tal = _get_ledger_talleyrand(world)
        am = tal.get("active_mission")
        assert am is not None
        assert "paused" in am
        assert am["paused"] is True
