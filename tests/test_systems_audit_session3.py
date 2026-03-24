"""
Systems Audit Fix Plan — Session 3: Fog of War Fixes

Tests for 3 actionable fixes:
1. Campaign log missing fog filter for 5 event types (P5-2)
2. /marshal_trust endpoint returns enemy data (P21-03)
3. STALE visibility shows exact strength numbers (P21-04 to P21-06)
"""

from backend.models.world_state import WorldState
from backend.models.intel import (
    FULL, PARTIAL, STALE, UNKNOWN,
    get_strength_band,
)
from backend.campaign_log import filter_campaign_log
from backend.game_logic.ledger import _build_intel
from backend.game_logic.dispatch import (
    _build_intelligence, _estimate_enemy_strength_from_intel,
    BAND_MIDPOINTS,
)


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def make_world():
    """Fresh WorldState."""
    return WorldState()


def _set_region_visibility(world, region_name, visibility, known_marshals=None):
    """Helper to force a region's intel to a specific visibility + known_marshals."""
    intel = world.get_region_intel(region_name)
    intel.visibility = visibility
    if known_marshals is not None:
        intel.known_marshals = known_marshals
    intel.last_updated_turn = world.current_turn


# ═══════════════════════════════════════════════════════
# FIX 1: Campaign log fog filter for 5 event types
# ═══════════════════════════════════════════════════════

class TestCampaignLogFogFilter:
    """Fix 1: war_declaration, defensive/offensive_cascade, coalition events."""

    def test_war_declaration_visible_when_france_involved(self):
        """war_declaration shows when France is aggressor or target."""
        world = make_world()
        events = [
            {"type": "war_declaration", "aggressor": "France", "target": "Prussia", "turn": 1},
            {"type": "war_declaration", "aggressor": "Austria", "target": "France", "turn": 2},
        ]
        filtered = filter_campaign_log(events, world)
        assert len(filtered) == 2

    def test_war_declaration_hidden_for_ai_only_at_unknown(self):
        """war_declaration between AI nations hidden when both at UNKNOWN visibility."""
        world = make_world()
        # Force all regions to UNKNOWN so no nation is visible
        for region_name in world.regions:
            _set_region_visibility(world, region_name, UNKNOWN, [])
        # Remove all enemy marshals so _get_nation_visibility returns UNKNOWN
        enemy_marshals = [n for n, m in world.marshals.items() if m.nation != world.player_nation]
        for name in enemy_marshals:
            world.marshals[name].strength = 0

        events = [
            {"type": "war_declaration", "aggressor": "Austria", "target": "Russia", "turn": 1},
        ]
        filtered = filter_campaign_log(events, world)
        assert len(filtered) == 0

    def test_coalition_events_always_shown(self):
        """coalition_declared and coalition_dissolved always visible."""
        world = make_world()
        # Force everything to UNKNOWN
        for region_name in world.regions:
            _set_region_visibility(world, region_name, UNKNOWN, [])
        enemy_marshals = [n for n, m in world.marshals.items() if m.nation != world.player_nation]
        for name in enemy_marshals:
            world.marshals[name].strength = 0

        events = [
            {"type": "coalition_declared", "coalition_name": "Anti-French Coalition",
             "leader": "Britain", "members": ["Britain", "Austria", "Prussia"],
             "posture": "defensive", "turn": 1},
            {"type": "coalition_dissolved", "coalition_name": "Anti-French Coalition",
             "reason": "war_exhaustion", "turn": 2},
        ]
        filtered = filter_campaign_log(events, world)
        assert len(filtered) == 2

    def test_cascade_visible_at_partial_visibility(self):
        """defensive_cascade visible when a nation has PARTIAL+ visibility."""
        world = make_world()
        # Find an Austrian marshal and place them somewhere visible
        austrian_marshal = None
        for m in world.marshals.values():
            if m.nation == "Austria":
                austrian_marshal = m
                break

        if austrian_marshal:
            _set_region_visibility(world, austrian_marshal.location, PARTIAL, [
                {"name": austrian_marshal.name, "nation": "Austria", "band": "large force"}
            ])

        events = [
            {"type": "defensive_cascade", "defender": "Austria", "ally": "Russia",
             "against": "Prussia", "turn": 1},
        ]
        filtered = filter_campaign_log(events, world)
        assert len(filtered) == 1


# ═══════════════════════════════════════════════════════
# FIX 2: /marshal_trust endpoint fog guard
# ═══════════════════════════════════════════════════════

class TestMarshalTrustEndpoint:
    """Fix 2: Nation guard on /marshal_trust."""

    def test_player_marshal_returns_data(self):
        """Player marshal trust data is accessible."""
        from backend.main import get_marshal_trust, world as app_world
        # Use a known player marshal
        player_marshal = None
        for m in app_world.marshals.values():
            if m.nation == app_world.player_nation:
                player_marshal = m
                break
        assert player_marshal is not None, "No player marshal found"

        result = get_marshal_trust(player_marshal.name)
        assert result["success"] is True
        assert "trust" in result

    def test_enemy_marshal_denied(self):
        """Enemy marshal trust data is denied."""
        from backend.main import get_marshal_trust, world as app_world
        # Use a known enemy marshal
        enemy_marshal = None
        for m in app_world.marshals.values():
            if m.nation != app_world.player_nation:
                enemy_marshal = m
                break
        assert enemy_marshal is not None, "No enemy marshal found"

        result = get_marshal_trust(enemy_marshal.name)
        assert result["success"] is False
        assert "No intelligence available" in result["message"]


# ═══════════════════════════════════════════════════════
# FIX 3a: STALE ledger strength band
# ═══════════════════════════════════════════════════════

class TestStaleLedgerStrengthBand:
    """Fix 3a: Ledger uses band for STALE, not exact numbers."""

    def test_stale_shows_band_not_exact_number(self):
        """STALE marshal display should show band string, not exact number."""
        world = make_world()
        # Find an enemy marshal
        enemy = None
        for m in world.marshals.values():
            if m.nation != world.player_nation:
                enemy = m
                break
        assert enemy is not None

        # Set their region to STALE with known strength
        _set_region_visibility(world, enemy.location, STALE, [
            {"name": enemy.name, "nation": enemy.nation, "strength": 25000}
        ])

        intel_section = _build_intel(world, world.player_nation)
        enemies = intel_section["known_enemies"]

        # Find our test enemy
        test_entry = None
        for e in enemies:
            if e["name"] == enemy.name:
                test_entry = e
                break
        assert test_entry is not None, f"Enemy {enemy.name} not found in intel"

        # Should show band, not exact number
        display = test_entry["strength_display"]
        assert "last seen:" in display
        # Should NOT contain "25,000" (exact formatted number)
        assert "25,000" not in display
        # Should contain a band string
        expected_band = get_strength_band(25000)
        assert expected_band in display

    def test_stale_nation_summary_uses_band_midpoint(self):
        """Nation summary estimated_strength should use band midpoint for STALE."""
        world = make_world()
        # Clear all visibility first
        for region_name in world.regions:
            _set_region_visibility(world, region_name, UNKNOWN, [])

        # Find an enemy marshal
        enemy = None
        for m in world.marshals.values():
            if m.nation != world.player_nation:
                enemy = m
                break
        assert enemy is not None

        # Set a single STALE sighting with known strength
        test_strength = 25000
        _set_region_visibility(world, enemy.location, STALE, [
            {"name": enemy.name, "nation": enemy.nation, "strength": test_strength}
        ])

        intel_section = _build_intel(world, world.player_nation)
        summaries = intel_section["nation_summaries"]

        nation_summary = None
        for ns in summaries:
            if ns["nation"] == enemy.nation:
                nation_summary = ns
                break
        assert nation_summary is not None

        # Should use band midpoint, not exact number
        expected_band = get_strength_band(test_strength)
        expected_midpoint = BAND_MIDPOINTS.get(expected_band, 0)
        # The estimated_strength should match midpoint (not exact 25000)
        assert nation_summary["estimated_strength"] == expected_midpoint
        assert nation_summary["estimated_strength"] != test_strength


# ═══════════════════════════════════════════════════════
# FIX 3b: STALE dispatch intelligence strength band
# ═══════════════════════════════════════════════════════

class TestStaleDispatchStrengthBand:
    """Fix 3b: Dispatch intelligence uses band for STALE."""

    def test_intelligence_section_shows_band(self):
        """STALE in dispatch intelligence should show band, not ~N exact."""
        world = make_world()
        # Find an enemy marshal
        enemy = None
        for m in world.marshals.values():
            if m.nation != world.player_nation:
                enemy = m
                break
        assert enemy is not None

        # Clear all intel, then set one STALE sighting
        for region_name in world.regions:
            _set_region_visibility(world, region_name, UNKNOWN, [])

        _set_region_visibility(world, enemy.location, STALE, [
            {"name": enemy.name, "nation": enemy.nation, "strength": 30000}
        ])

        sightings = _build_intelligence(world, world.player_nation)
        test_entry = None
        for s in sightings:
            if s["name"] == enemy.name:
                test_entry = s
                break
        assert test_entry is not None

        display = test_entry["strength_display"]
        # Should NOT contain the ~ prefix exact format
        assert "~30,000" not in display
        # Should be a band string
        expected_band = get_strength_band(30000)
        assert display == expected_band

    def test_strength_estimate_uses_midpoint(self):
        """STALE in dispatch strength estimation should use band midpoint."""
        world = make_world()
        # Find an enemy marshal
        enemy = None
        for m in world.marshals.values():
            if m.nation != world.player_nation:
                enemy = m
                break
        assert enemy is not None

        # Clear all intel, then set one STALE sighting
        for region_name in world.regions:
            _set_region_visibility(world, region_name, UNKNOWN, [])

        test_strength = 30000
        _set_region_visibility(world, enemy.location, STALE, [
            {"name": enemy.name, "nation": enemy.nation, "strength": test_strength}
        ])

        estimate = _estimate_enemy_strength_from_intel(world, world.player_nation)
        expected_band = get_strength_band(test_strength)
        expected_midpoint = BAND_MIDPOINTS.get(expected_band, 0)

        # Should use midpoint, not exact
        assert estimate == expected_midpoint
        assert estimate != test_strength


# ═══════════════════════════════════════════════════════
# FIX 3c: FULL vs STALE estimation comparison
# ═══════════════════════════════════════════════════════

class TestStaleDispatchEstimation:
    """Fix 3c: FULL uses exact, STALE uses band midpoint."""

    def test_full_uses_exact_strength(self):
        """FULL visibility should use exact strength in estimation."""
        world = make_world()
        enemy = None
        for m in world.marshals.values():
            if m.nation != world.player_nation:
                enemy = m
                break
        assert enemy is not None

        for region_name in world.regions:
            _set_region_visibility(world, region_name, UNKNOWN, [])

        test_strength = 25000
        _set_region_visibility(world, enemy.location, FULL, [
            {"name": enemy.name, "nation": enemy.nation, "strength": test_strength}
        ])

        estimate = _estimate_enemy_strength_from_intel(world, world.player_nation)
        assert estimate == test_strength

    def test_stale_uses_band_midpoint_not_exact(self):
        """STALE visibility should NOT use exact strength."""
        world = make_world()
        enemy = None
        for m in world.marshals.values():
            if m.nation != world.player_nation:
                enemy = m
                break
        assert enemy is not None

        for region_name in world.regions:
            _set_region_visibility(world, region_name, UNKNOWN, [])

        test_strength = 25000
        _set_region_visibility(world, enemy.location, STALE, [
            {"name": enemy.name, "nation": enemy.nation, "strength": test_strength}
        ])

        estimate = _estimate_enemy_strength_from_intel(world, world.player_nation)
        # Must NOT be the exact value
        assert estimate != test_strength
        # Must be the band midpoint
        expected_band = get_strength_band(test_strength)
        assert estimate == BAND_MIDPOINTS.get(expected_band, 0)
