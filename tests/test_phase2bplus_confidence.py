"""Phase 2B+ Confidence Follow-up tests.

Fix 1 (R98): Jump transitions charge cumulative DP via get_transition_dp_cost().
Fix 2 (R107): No-downgrade guard returns error dict for player.
Fix 3 (R81): Coalition cleanup on nation elimination.
"""

from backend.models.world_state import WorldState
from backend.game_logic.diplomacy import get_dp_cost, get_transition_dp_cost


def _make_world():
    world = WorldState()
    world.current_turn = 5
    return world


def _set_diplo_state(world, a, b, state):
    key = world._make_diplo_key(a, b)
    world.diplomatic_states[key] = state


# ═══════════════════════════════════════════════════════
# Fix 1: R98 — Jump Transition DP Cost Wiring
# ═══════════════════════════════════════════════════════

class TestR98JumpTransitionDPCost:
    """R98: Jump transitions (e.g. PEACE→ALLIANCE) charge cumulative DP."""

    def test_jump_transition_charges_cumulative_dp(self):
        """PEACE→ALLIANCE costs 6 DP (1+1+2+2), not flat 2."""
        cost = get_transition_dp_cost("PEACE", "ALLIANCE")
        assert cost == 6, f"PEACE→ALLIANCE should cost 6 DP, got {cost}"
        # get_dp_cost with transition_base should use the higher value
        final = get_dp_cost("propose_alliance", 10, transition_base=cost)
        assert final == 6, f"Final cost should be 6, got {final}"

    def test_adjacent_transition_cost_unchanged(self):
        """DEFENSIVE_ALLIANCE→ALLIANCE (adjacent) still costs 2 DP."""
        cost = get_transition_dp_cost("DEFENSIVE_ALLIANCE", "ALLIANCE")
        assert cost == 2, f"Adjacent transition should cost 2, got {cost}"
        final = get_dp_cost("propose_alliance", 10, transition_base=cost)
        assert final == 2, f"Final cost should be 2, got {final}"

    def test_skill_penalty_applies_to_jump_cost(self):
        """Low-skill Talleyrand adds penalty on top of jump cost."""
        jump_cost = get_transition_dp_cost("PEACE", "ALLIANCE")
        assert jump_cost == 6
        # Skill < 4 adds +2
        final = get_dp_cost("propose_alliance", 3, transition_base=jump_cost)
        assert final == 8, f"6 base + 2 skill penalty = 8, got {final}"
        # Skill 4-6 adds +1
        final_mid = get_dp_cost("propose_alliance", 5, transition_base=jump_cost)
        assert final_mid == 7, f"6 base + 1 skill penalty = 7, got {final_mid}"

    def test_transition_base_zero_no_change(self):
        """transition_base=0 gives same result as omitting it."""
        cost_default = get_dp_cost("propose_alliance", 10)
        cost_zero = get_dp_cost("propose_alliance", 10, transition_base=0)
        assert cost_default == cost_zero

    def test_peace_to_non_aggression_jump_cost(self):
        """PEACE→NON_AGGRESSION costs 2 DP (1+1, through OPEN_BORDERS)."""
        cost = get_transition_dp_cost("PEACE", "NON_AGGRESSION")
        assert cost == 2, f"PEACE→NON_AGGRESSION should cost 2, got {cost}"


# ═══════════════════════════════════════════════════════
# Fix 2: R107 — No-Downgrade Guard Returns Error Dict
# ═══════════════════════════════════════════════════════

class TestR107DowngradeGuard:
    """R107: Player downgrade proposals return error dict, AI-AI returns None."""

    def test_player_downgrade_returns_error_dict(self):
        """Player proposing PEACE when at ALLIANCE → error dict with message."""
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")

        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Austria",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        result = world._ratify_treaty(proposal)
        assert result is not None, "Player downgrade should return error dict, not None"
        assert result["type"] == "diplomatic_treaty_failed"
        assert "downgrade" in result["message"].lower() or "ALLIANCE" in result["message"]
        assert result["target"] == "Austria"

    def test_ai_ai_downgrade_still_returns_none(self):
        """AI-AI downgrade proposals → None (silent skip, unchanged)."""
        world = _make_world()
        _set_diplo_state(world, "Prussia", "Austria", "ALLIANCE")

        proposal = {
            "type": "peace",
            "proposer_nation": "Prussia",
            "target_nation": "Austria",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        result = world._ratify_treaty(proposal)
        assert result is None, "AI-AI downgrade should return None"

    def test_player_same_level_returns_error(self):
        """Player proposing same level (PEACE when at PEACE) → error dict."""
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "PEACE")

        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Austria",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        result = world._ratify_treaty(proposal)
        assert result is not None, "Same-level proposal should return error"
        assert result["type"] == "diplomatic_treaty_failed"


# ═══════════════════════════════════════════════════════
# Fix 3: R81 — Coalition Cleanup on Elimination
# ═══════════════════════════════════════════════════════

class TestR81CoalitionCleanupOnElimination:
    """R81: Eliminated nations removed from active coalition."""

    def test_elimination_removes_from_coalition(self):
        """Eliminate a coalition member → removed from active_coalition members."""
        world = _make_world()
        # Ensure all 3 coalition members are at WAR with France (so coalition persists)
        _set_diplo_state(world, "France", "Britain", "WAR")
        _set_diplo_state(world, "France", "Prussia", "WAR")
        _set_diplo_state(world, "France", "Saxony", "WAR")
        world.threat_level = 60  # Above dissolution threshold

        # Set up an active coalition with Saxony as member
        world.active_coalition = {
            "name": "Third Coalition",
            "members": ["Britain", "Prussia", "Saxony"],
            "leader": "Britain",
            "target": "France",
            "formed_turn": 3,
            "strategic_posture": "DEFENSIVE",
            "posture_last_updated": 3,
            "threat_at_formation": 50,
            "war_exhaustion": {},
            "friction_log": [],
        }

        # Give Saxony only one region, then capture it
        for name, region in world.regions.items():
            if region.controller == "Saxony":
                region.controller = "France"
        for name in list(world.regions.keys()):
            if name == "Saxony":
                world.regions[name].controller = "Saxony"
                break

        world.capture_region("Saxony", "France")

        # Coalition should still exist (2 members remain at war)
        assert world.active_coalition is not None, "Coalition should persist with 2 active members"
        # Saxony should be removed from coalition
        assert "Saxony" not in world.active_coalition["members"]
        assert "Britain" in world.active_coalition["members"]
        assert "Prussia" in world.active_coalition["members"]

    def test_elimination_no_coalition_no_crash(self):
        """Eliminate with no active coalition → no error."""
        world = _make_world()
        world.active_coalition = None

        # Give Saxony only one region, then capture it
        for name, region in world.regions.items():
            if region.controller == "Saxony":
                region.controller = "France"
        for name in list(world.regions.keys()):
            if name == "Saxony":
                world.regions[name].controller = "Saxony"
                break

        # Should not crash
        world.capture_region("Saxony", "France")
        assert world.active_coalition is None
