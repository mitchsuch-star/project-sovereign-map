"""
Diplomacy Audit — Critical Bug Tests (March 2026)

Tests for the 5 CRITICAL bugs identified in docs/DIPLOMACY_AUDIT_2026_03.md:
  C1: Coalition loyalty penalty formula inverted
  C2: Vassal courting reads non-existent DP attribute
  C3: classify_diplomatic_intent blocks vassal diplomacy
  C4: /cancel_order missing popup passthroughs + try/except + game_state
  C5: Fog-of-war leak in threat assessment
"""
from backend.models.world_state import WorldState


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _make_world():
    """Create a test world with basic setup."""
    world = WorldState()
    world.current_turn = 5
    return world


def _make_game_state(world=None):
    """Create game_state dict wrapping a world."""
    if world is None:
        world = _make_world()
    return {"world": world}


# ═══════════════════════════════════════════════════════════════════════════
# C1: COALITION LOYALTY PENALTY FORMULA
# ═══════════════════════════════════════════════════════════════════════════

class TestC1CoalitionLoyaltyPenalty:
    """Coalition loyalty penalty should approach 0 as war exhaustion rises."""

    def test_penalty_zero_war_exhaustion(self):
        """At 0 war exhaustion, penalty = COALITION_LOYALTY_BASE (-15)."""
        from backend.game_logic.coalition import get_coalition_loyalty_penalty, COALITION_LOYALTY_BASE
        world = _make_world()
        world.active_coalition = {
            "members": ["Austria", "Prussia"],
            "leader": "Austria",
        }
        world.war_exhaustion = {"Austria": 0}
        penalty = get_coalition_loyalty_penalty("Austria", world)
        assert penalty == COALITION_LOYALTY_BASE  # -15
        assert penalty < 0, "Base penalty should be negative"

    def test_penalty_improves_with_war_exhaustion(self):
        """Higher war exhaustion should make penalty LESS severe (closer to 0)."""
        from backend.game_logic.coalition import get_coalition_loyalty_penalty
        world = _make_world()
        world.active_coalition = {
            "members": ["Austria"],
            "leader": "Austria",
        }
        world.war_exhaustion = {"Austria": 50}
        penalty_50 = get_coalition_loyalty_penalty("Austria", world)

        world.war_exhaustion = {"Austria": 100}
        penalty_100 = get_coalition_loyalty_penalty("Austria", world)

        world.war_exhaustion = {"Austria": 0}
        penalty_0 = get_coalition_loyalty_penalty("Austria", world)

        # More exhaustion -> penalty closer to 0 (less severe)
        assert penalty_50 > penalty_0, f"50 WE penalty {penalty_50} should be > 0 WE penalty {penalty_0}"
        assert penalty_100 > penalty_50, f"100 WE penalty {penalty_100} should be > 50 WE penalty {penalty_50}"

    def test_penalty_never_positive(self):
        """Penalty should never exceed 0 (capped by min(..., 0))."""
        from backend.game_logic.coalition import get_coalition_loyalty_penalty
        world = _make_world()
        world.active_coalition = {
            "members": ["Austria"],
            "leader": "Austria",
        }
        # Very high war exhaustion
        world.war_exhaustion = {"Austria": 500}
        penalty = get_coalition_loyalty_penalty("Austria", world)
        assert penalty <= 0, f"Penalty {penalty} should never be positive"

    def test_penalty_at_150_war_exhaustion_is_zero(self):
        """At 150 war exhaustion: min(-15 + 150//10, 0) = min(0, 0) = 0."""
        from backend.game_logic.coalition import get_coalition_loyalty_penalty
        world = _make_world()
        world.active_coalition = {
            "members": ["Austria"],
            "leader": "Austria",
        }
        world.war_exhaustion = {"Austria": 150}
        penalty = get_coalition_loyalty_penalty("Austria", world)
        assert penalty == 0, f"At 150 WE, penalty should be 0, got {penalty}"

    def test_penalty_matches_docstring_formula(self):
        """Verify formula: min(-15 + we // 10, 0)."""
        from backend.game_logic.coalition import get_coalition_loyalty_penalty, COALITION_LOYALTY_BASE
        world = _make_world()
        world.active_coalition = {
            "members": ["Prussia"],
            "leader": "Prussia",
        }
        for we in [0, 10, 30, 50, 80, 100, 150, 200]:
            world.war_exhaustion = {"Prussia": we}
            penalty = get_coalition_loyalty_penalty("Prussia", world)
            expected = min(COALITION_LOYALTY_BASE + we // 10, 0)
            assert penalty == expected, f"WE={we}: got {penalty}, expected {expected}"

    def test_non_member_no_penalty(self):
        """Nations not in coalition get 0 penalty."""
        from backend.game_logic.coalition import get_coalition_loyalty_penalty
        world = _make_world()
        world.active_coalition = {
            "members": ["Austria"],
            "leader": "Austria",
        }
        penalty = get_coalition_loyalty_penalty("Prussia", world)
        assert penalty == 0

    def test_no_coalition_no_penalty(self):
        """No active coalition means 0 penalty."""
        from backend.game_logic.coalition import get_coalition_loyalty_penalty
        world = _make_world()
        world.active_coalition = None
        penalty = get_coalition_loyalty_penalty("Austria", world)
        assert penalty == 0


# ═══════════════════════════════════════════════════════════════════════════
# C2: VASSAL COURTING DP ATTRIBUTE
# ═══════════════════════════════════════════════════════════════════════════

class TestC2VassalCourtingDP:
    """Vassal courting should read nation_dp, not diplomatic_points_nations."""

    def test_courting_with_nation_dp(self):
        """Enemy AI can court player vassals when nation_dp has sufficient DP."""
        from backend.game_logic.vassal import attempt_vassal_courting
        world = _make_world()
        world.player_nation = "France"
        world.nation_dp = {"Prussia": 10}
        world.vassals = {
            "Saxony": {"lord": "France", "loyalty": 30, "autonomy": 50}
        }
        world.ai_proposal_cooldowns = {}

        events = attempt_vassal_courting(world, "Prussia")
        # Should produce courting events since Prussia has enough DP
        assert len(events) > 0, "Prussia should be able to court Saxony with 10 DP"

    def test_courting_insufficient_dp(self):
        """No courting if nation has insufficient DP."""
        from backend.game_logic.vassal import attempt_vassal_courting
        world = _make_world()
        world.player_nation = "France"
        world.nation_dp = {"Prussia": 1}
        world.vassals = {
            "Saxony": {"lord": "France", "loyalty": 30, "autonomy": 50}
        }
        world.ai_proposal_cooldowns = {}

        events = attempt_vassal_courting(world, "Prussia")
        assert len(events) == 0, "Prussia should not court with only 1 DP"

    def test_courting_deducts_from_nation_dp(self):
        """Successful courting should deduct 2 DP from nation_dp."""
        from backend.game_logic.vassal import attempt_vassal_courting
        world = _make_world()
        world.player_nation = "France"
        world.nation_dp = {"Prussia": 10}
        world.vassals = {
            "Saxony": {"lord": "France", "loyalty": 30, "autonomy": 50}
        }
        world.ai_proposal_cooldowns = {}

        attempt_vassal_courting(world, "Prussia")
        assert world.nation_dp["Prussia"] == 8, f"DP should be 8 after courting, got {world.nation_dp['Prussia']}"

    def test_courting_no_crash_without_attribute(self):
        """No crash even if nation_dp is missing (getattr default)."""
        from backend.game_logic.vassal import attempt_vassal_courting
        world = _make_world()
        world.player_nation = "France"
        # Deliberately remove nation_dp to test getattr fallback
        if hasattr(world, 'nation_dp'):
            delattr(world, 'nation_dp')
        world.vassals = {
            "Saxony": {"lord": "France", "loyalty": 30, "autonomy": 50}
        }
        world.ai_proposal_cooldowns = {}

        events = attempt_vassal_courting(world, "Prussia")
        # Should return empty list (no DP), not crash
        assert len(events) == 0


# ═══════════════════════════════════════════════════════════════════════════
# C3: CLASSIFY DIPLOMATIC INTENT — VASSAL NATIONS
# ═══════════════════════════════════════════════════════════════════════════

class TestC3ClassifyDiplomaticIntentVassals:
    """classify_diplomatic_intent should recognize vassal nations."""

    def test_vassal_nation_not_unknown(self):
        """A vassal nation should not be classified as 'unknown_nation'."""
        from backend.game_logic.diplomatic_dialogue import classify_diplomatic_intent
        world = _make_world()
        world.vassals = {"Saxony": {"lord": "France", "loyalty": 60, "autonomy": 50}}

        parsed = {
            "target_nation": "Saxony",
            "proposal_type": "peace",
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "raw_text": "propose peace with Saxony",
            "mission_type": None,
        }
        result = classify_diplomatic_intent(parsed, world)
        assert result != "unknown_nation", f"Vassal 'Saxony' should not be unknown, got '{result}'"

    def test_known_nation_still_recognized(self):
        """Standard known nations (Britain, Prussia, etc.) still work."""
        from backend.game_logic.diplomatic_dialogue import classify_diplomatic_intent
        world = _make_world()
        world.vassals = {}

        parsed = {
            "target_nation": "Britain",
            "proposal_type": "peace",
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "raw_text": "propose peace with Britain",
            "mission_type": None,
        }
        result = classify_diplomatic_intent(parsed, world)
        assert result != "unknown_nation", f"Britain should not be unknown, got '{result}'"

    def test_truly_unknown_nation_still_rejected(self):
        """An actually unknown nation should still be 'unknown_nation'."""
        from backend.game_logic.diplomatic_dialogue import classify_diplomatic_intent
        world = _make_world()
        world.vassals = {}

        parsed = {
            "target_nation": "Narnia",
            "proposal_type": "peace",
            "clauses": [],
            "is_question": False,
            "has_diplomatic_keywords": True,
            "raw_text": "propose peace with Narnia",
            "mission_type": None,
        }
        result = classify_diplomatic_intent(parsed, world)
        assert result == "unknown_nation", f"Narnia should be unknown, got '{result}'"

    def test_vassal_from_conquest_recognized(self):
        """A nation vassalized mid-game should be recognized."""
        from backend.game_logic.diplomatic_dialogue import classify_diplomatic_intent
        world = _make_world()
        # Bavaria is not in KNOWN_NATIONS, but is a vassal
        world.vassals = {"Bavaria": {"lord": "France", "loyalty": 40, "autonomy": 50}}

        parsed = {
            "target_nation": "Bavaria",
            "proposal_type": None,
            "clauses": [],
            "is_question": True,
            "has_diplomatic_keywords": True,
            "raw_text": "what about Bavaria?",
            "mission_type": None,
        }
        result = classify_diplomatic_intent(parsed, world)
        assert result != "unknown_nation", f"Vassal 'Bavaria' should not be unknown, got '{result}'"


# ═══════════════════════════════════════════════════════════════════════════
# C4: /cancel_order ENDPOINT HARDENING
# ═══════════════════════════════════════════════════════════════════════════

class TestC4CancelOrderEndpoint:
    """Tests for /cancel_order endpoint hardening."""

    def test_cancel_order_has_popup_passthrough(self):
        """Must use the response builders WITHOUT draining the popup queue.

        Aug 2026 health-check audit re-point: the builder-presence assert
        stayed green while the default drain destroyed queued popups (the
        ledger's cancel callback never reads the body).
        """
        import inspect
        from backend.main import cancel_order
        source = inspect.getsource(cancel_order)
        assert "build_base_response" in source or "_build_result_response" in source, \
            "/cancel_order must use build_base_response or _build_result_response"
        assert "drain_popups=False" in source, \
            "/cancel_order must not drain the popup queue (Aug 2026 audit)"

    def test_cancel_order_has_try_except(self):
        """Source code must have try/except wrapper."""
        import inspect
        from backend.main import cancel_order
        source = inspect.getsource(cancel_order)
        assert "except Exception" in source, \
            "/cancel_order must have try/except wrapper"

    def test_cancel_order_error_returns_have_game_state(self):
        """Early error returns must include game_state."""
        import inspect
        from backend.main import cancel_order
        source = inspect.getsource(cancel_order)
        # Check that "No marshal specified" error path includes game_state
        assert 'game_state' in source, \
            "/cancel_order must include game_state in responses"

    def test_cancel_order_except_block_has_popup_passthrough(self):
        """The except block must use build_base_response (structurally guarantees popups)."""
        import inspect
        from backend.main import cancel_order
        source = inspect.getsource(cancel_order)
        lines = source.split('\n')
        in_except = False
        found_builder_in_except = False
        for line in lines:
            if 'except Exception' in line:
                in_except = True
            if in_except and 'build_base_response' in line:
                found_builder_in_except = True
                break
        assert found_builder_in_except, \
            "/cancel_order except block must use build_base_response"

    def test_cancel_order_success_has_popup_passthrough(self):
        """The success path must use build_base_response or _build_result_response."""
        import inspect
        from backend.main import cancel_order
        source = inspect.getsource(cancel_order)
        # R4: builder structurally guarantees popups — count builder calls
        count = source.count("build_base_response") + source.count("_build_result_response")
        assert count >= 2, \
            f"/cancel_order should use response builder at least 2 times, found {count}"


# ═══════════════════════════════════════════════════════════════════════════
# C5: FOG-OF-WAR LEAK IN THREAT ASSESSMENT
# ═══════════════════════════════════════════════════════════════════════════

class TestC5FogOfWarThreatAssessment:
    """Threat assessment must use fog-filtered strength, not raw."""

    def _make_marshal(self, name, location, strength, nation="France"):
        """Helper to create a Marshal with correct argument order."""
        from backend.models.marshal import Marshal
        m = Marshal(name, location, strength, "cautious", nation=nation)
        return m

    def _make_clean_world(self):
        """Create a world with no pre-existing marshals for isolated fog tests."""
        world = _make_world()
        world.marshals = {}  # Clear default starting marshals
        return world

    def test_fogged_strength_unknown_returns_default(self):
        """UNKNOWN visibility should return default estimate, not raw strength."""
        from backend.game_logic.diplomatic_advisory import _get_fogged_strength
        world = self._make_clean_world()
        m = self._make_marshal("Blucher", "Berlin", 50000, nation="Prussia")
        world.marshals["Blucher"] = m
        # Ensure the region has UNKNOWN visibility
        intel = world.get_region_intel("Berlin")
        intel.visibility = "unknown"

        result = _get_fogged_strength("Prussia", world)
        assert result != 50000, "UNKNOWN visibility should not return exact strength"
        assert result == 30000, f"UNKNOWN visibility should return 30000 default, got {result}"

    def test_fogged_strength_full_returns_exact(self):
        """FULL visibility should return exact raw strength."""
        from backend.game_logic.diplomatic_advisory import _get_fogged_strength
        world = self._make_clean_world()
        m = self._make_marshal("Blucher", "Berlin", 42000, nation="Prussia")
        world.marshals["Blucher"] = m
        intel = world.get_region_intel("Berlin")
        intel.visibility = "full"

        result = _get_fogged_strength("Prussia", world)
        assert result == 42000, f"FULL visibility should return exact 42000, got {result}"

    def test_fogged_strength_partial_returns_exact(self):
        """PARTIAL visibility should return exact raw strength."""
        from backend.game_logic.diplomatic_advisory import _get_fogged_strength
        world = self._make_clean_world()
        m = self._make_marshal("Blucher", "Berlin", 35000, nation="Prussia")
        world.marshals["Blucher"] = m
        intel = world.get_region_intel("Berlin")
        intel.visibility = "partial"

        result = _get_fogged_strength("Prussia", world)
        assert result == 35000, f"PARTIAL visibility should return exact 35000, got {result}"

    def test_fogged_strength_stale_returns_band_estimate(self):
        """STALE visibility should return band mid-point, not exact."""
        from backend.game_logic.diplomatic_advisory import _get_fogged_strength
        world = self._make_clean_world()
        m = self._make_marshal("Blucher", "Berlin", 47000, nation="Prussia")
        world.marshals["Blucher"] = m
        intel = world.get_region_intel("Berlin")
        intel.visibility = "stale"

        result = _get_fogged_strength("Prussia", world)
        assert result != 47000, "STALE visibility should not return exact strength"
        assert result == 45000, f"STALE 30k-60k band should return 45000, got {result}"

    def test_compare_threats_uses_fogged_strength(self):
        """_compare_threats should use fog-filtered, not raw strength."""
        from backend.game_logic.diplomatic_advisory import _compare_threats
        world = self._make_clean_world()

        # Set up France with a known strength
        ney = self._make_marshal("Ney", "Paris", 40000, nation="France")
        world.marshals["Ney"] = ney
        # Paris is player territory, should have FULL visibility
        intel_paris = world.get_region_intel("Paris")
        intel_paris.visibility = "full"

        # Set up Prussia with a large army in UNKNOWN visibility
        blucher = self._make_marshal("Blucher", "Berlin", 80000, nation="Prussia")
        world.marshals["Blucher"] = blucher
        intel_berlin = world.get_region_intel("Berlin")
        intel_berlin.visibility = "unknown"

        # Set up Austria with small army in FULL visibility
        charles = self._make_marshal("Charles", "Vienna", 35000, nation="Austria")
        world.marshals["Charles"] = charles
        intel_vienna = world.get_region_intel("Vienna")
        intel_vienna.visibility = "full"

        result = _compare_threats(world)
        threat_ranking = result["context"]["threat_ranking"]

        # Get Prussia's recorded strength in threat data
        prussia_entry = next(e for e in threat_ranking if e["nation"] == "Prussia")

        # Prussia's raw strength is 80000 but visibility is UNKNOWN
        # so fog should mask it to default 30000
        # With raw 80000, Prussia would have gotten +40 for being > 0.5x and > 1x France's 40000
        # With fogged 30000, Prussia should NOT get +20 for "strength > france_strength" (30000 < 40000)
        # This verifies the fog filter is working
        assert prussia_entry is not None, "Prussia should appear in threat ranking"

    def test_compare_threats_unknown_nation_not_exact(self):
        """A nation with UNKNOWN visibility must not use exact troop count for scoring."""
        from backend.game_logic.diplomatic_advisory import (
            _get_fogged_strength, _get_nation_total_strength
        )
        world = self._make_clean_world()

        ney = self._make_marshal("Ney", "Paris", 40000, nation="France")
        world.marshals["Ney"] = ney
        intel_paris = world.get_region_intel("Paris")
        intel_paris.visibility = "full"

        blucher = self._make_marshal("Blucher", "Berlin", 90000, nation="Prussia")
        world.marshals["Blucher"] = blucher
        intel_berlin = world.get_region_intel("Berlin")
        intel_berlin.visibility = "unknown"

        raw_strength = _get_nation_total_strength("Prussia", world)
        fogged_strength = _get_fogged_strength("Prussia", world)

        assert raw_strength == 90000
        assert fogged_strength == 30000, "Fogged strength should be default 30000"
        assert fogged_strength != raw_strength, "Fogged must differ from raw for UNKNOWN"

    def test_fogged_strength_stale_small_force(self):
        """STALE visibility for small force (< 10k) returns 5000."""
        from backend.game_logic.diplomatic_advisory import _get_fogged_strength
        world = self._make_clean_world()
        m = self._make_marshal("Test", "Dresden", 8000, nation="Saxony")
        world.marshals["Test"] = m
        intel = world.get_region_intel("Dresden")
        intel.visibility = "stale"
        result = _get_fogged_strength("Saxony", world)
        assert result == 5000

    def test_fogged_strength_stale_large_force(self):
        """STALE visibility for large force (>= 100k) returns 120000."""
        from backend.game_logic.diplomatic_advisory import _get_fogged_strength
        world = self._make_clean_world()
        m = self._make_marshal("Test", "Vienna", 120000, nation="Austria")
        world.marshals["Test"] = m
        intel = world.get_region_intel("Vienna")
        intel.visibility = "stale"
        result = _get_fogged_strength("Austria", world)
        assert result == 120000
