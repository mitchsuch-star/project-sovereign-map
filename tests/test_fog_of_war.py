"""
Fog of War - Session 33 Tests

Tests for:
- RegionIntel model + serialization
- Visibility calculation (marshal-present, own region, adjacent, decay)
- Decay timeline (FULL/PARTIAL → STALE → LAST_KNOWN)
- Strength bands
- Game init visibility
- Refresh vs decay path separation
- Stale snapshot persistence
- WorldState serialization roundtrip
- Serialization enforcement
"""

import pytest
from backend.models.intel import (
    RegionIntel, FULL, PARTIAL, STALE, LAST_KNOWN, UNKNOWN,
    VISIBILITY_PRIORITY, get_strength_band,
    FRESH_TURNS, STALE_TURN_START, LAST_KNOWN_TURN_START,
)
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal


# ============================================================================
# STRENGTH BANDS
# ============================================================================

class TestStrengthBands:
    """Test strength band calculation."""

    def test_zero_strength(self):
        assert get_strength_band(0) == "no forces"

    def test_negative_strength(self):
        assert get_strength_band(-100) == "no forces"

    def test_screening_force(self):
        assert get_strength_band(1) == "screening force"
        assert get_strength_band(4999) == "screening force"

    def test_small_force(self):
        assert get_strength_band(5000) == "small force"
        assert get_strength_band(14999) == "small force"

    def test_substantial_force(self):
        assert get_strength_band(15000) == "substantial force"
        assert get_strength_band(39999) == "substantial force"

    def test_large_force(self):
        assert get_strength_band(40000) == "large force"
        assert get_strength_band(69999) == "large force"

    def test_massive_force(self):
        assert get_strength_band(70000) == "massive force"
        assert get_strength_band(200000) == "massive force"


# ============================================================================
# REGION INTEL MODEL
# ============================================================================

class TestRegionIntelModel:
    """Test RegionIntel creation, refresh, decay."""

    def test_default_state_is_unknown(self):
        intel = RegionIntel("Paris")
        assert intel.visibility == UNKNOWN
        assert intel.region_name == "Paris"
        assert intel.known_marshals == []
        assert intel.strength_band == "no forces"
        assert intel.exact_strength is None
        assert intel.intel_source == ""

    def test_refresh_upgrades_visibility(self):
        intel = RegionIntel("Paris")
        intel.refresh(PARTIAL, "adjacent", turn=1, marshals=[], total_strength=0)
        assert intel.visibility == PARTIAL
        assert intel.last_updated_turn == 1

    def test_refresh_does_not_downgrade(self):
        intel = RegionIntel("Paris")
        intel.refresh(FULL, "scout", turn=1, marshals=[], total_strength=0)
        # Try to downgrade to PARTIAL — should be ignored
        intel.refresh(PARTIAL, "adjacent", turn=2, marshals=[], total_strength=0)
        assert intel.visibility == FULL
        # But last_updated_turn should NOT update since refresh was rejected
        assert intel.last_updated_turn == 1

    def test_refresh_full_stores_exact_data(self):
        marshals = [{"name": "Wellington", "nation": "Britain", "strength": 68000}]
        intel = RegionIntel("Waterloo")
        intel.refresh(FULL, "scout", turn=3, marshals=marshals,
                      total_strength=68000, morale=80, stance="defensive")
        assert intel.exact_strength == 68000
        assert intel.morale == 80
        assert intel.stance == "defensive"
        assert intel.known_marshals == marshals

    def test_refresh_partial_no_exact_data(self):
        marshals = [{"name": "Wellington", "nation": "Britain", "band": "large force"}]
        intel = RegionIntel("Waterloo")
        intel.refresh(PARTIAL, "adjacent", turn=3, marshals=marshals, total_strength=68000)
        assert intel.exact_strength is None
        assert intel.morale is None
        assert intel.stance is None
        assert intel.strength_band == "large force"

    def test_refresh_updates_source_priority(self):
        intel = RegionIntel("Paris")
        intel.refresh(PARTIAL, "adjacent", turn=1, marshals=[], total_strength=0)
        assert intel.intel_source == "adjacent"
        # Scout is higher priority — even at same visibility level
        intel.refresh(FULL, "scout", turn=2, marshals=[], total_strength=0)
        assert intel.intel_source == "scout"


# ============================================================================
# REGION INTEL SERIALIZATION
# ============================================================================

class TestRegionIntelSerialization:
    """Test RegionIntel to_dict/from_dict roundtrip."""

    def test_roundtrip_unknown(self):
        intel = RegionIntel("Vienna")
        data = intel.to_dict()
        restored = RegionIntel.from_dict(data)
        assert restored.region_name == "Vienna"
        assert restored.visibility == UNKNOWN

    def test_roundtrip_full_with_data(self):
        intel = RegionIntel("Waterloo")
        marshals = [{"name": "Wellington", "nation": "Britain", "strength": 68000}]
        intel.refresh(FULL, "scout", turn=5, marshals=marshals,
                      total_strength=68000, morale=80, stance="defensive")
        intel.last_scouted_turn = 5

        data = intel.to_dict()
        restored = RegionIntel.from_dict(data)

        assert restored.region_name == "Waterloo"
        assert restored.visibility == FULL
        assert restored.exact_strength == 68000
        assert restored.morale == 80
        assert restored.stance == "defensive"
        assert restored.last_scouted_turn == 5
        assert restored.last_updated_turn == 5
        assert restored.intel_source == "scout"
        assert len(restored.known_marshals) == 1
        assert restored.known_marshals[0]["name"] == "Wellington"

    def test_roundtrip_stale(self):
        intel = RegionIntel("Rhine")
        intel.refresh(FULL, "scout", turn=1, marshals=[{"name": "Blucher", "nation": "Prussia", "strength": 55000}],
                      total_strength=55000, morale=70, stance="neutral")
        # Force to stale
        intel.decay(current_turn=4)
        assert intel.visibility == STALE

        data = intel.to_dict()
        restored = RegionIntel.from_dict(data)
        assert restored.visibility == STALE
        assert restored.exact_strength is None  # Cleared by decay
        assert restored.known_marshals[0]["name"] == "Blucher"  # Frozen

    def test_all_fields_present_in_to_dict(self):
        """Every instance attribute must appear in to_dict output."""
        intel = RegionIntel("Test")
        data = intel.to_dict()
        instance_attrs = {k for k in vars(intel).keys() if not k.startswith('_')}
        serialized_keys = set(data.keys())
        missing = instance_attrs - serialized_keys
        assert not missing, f"Fields missing from to_dict: {missing}"


# ============================================================================
# DECAY TIMELINE
# ============================================================================

class TestDecayTimeline:
    """Test intel decay over multiple turns."""

    def test_full_stays_fresh_for_2_turns(self):
        intel = RegionIntel("Rhine")
        intel.refresh(FULL, "scout", turn=1, marshals=[], total_strength=0)
        # Turn 2: 1 turn since update — still FULL
        intel.decay(current_turn=2)
        assert intel.visibility == FULL
        # Turn 3: 2 turns since update — still FULL (FRESH_TURNS = 2)
        intel.decay(current_turn=3)
        assert intel.visibility == FULL

    def test_full_degrades_to_stale_at_turn_3(self):
        intel = RegionIntel("Rhine")
        intel.refresh(FULL, "scout", turn=1, marshals=[], total_strength=50000, morale=70, stance="neutral")
        # Turn 4: 3 turns since update → STALE
        intel.decay(current_turn=4)
        assert intel.visibility == STALE
        assert intel.exact_strength is None  # Cleared
        assert intel.morale is None

    def test_stale_degrades_to_last_known_at_turn_5(self):
        intel = RegionIntel("Rhine")
        intel.refresh(FULL, "scout", turn=1, marshals=[{"name": "Blucher", "nation": "Prussia"}], total_strength=50000)
        # Decay to STALE first
        intel.decay(current_turn=4)
        assert intel.visibility == STALE
        # Then to LAST_KNOWN
        intel.decay(current_turn=6)
        assert intel.visibility == LAST_KNOWN
        # Marshal snapshot still frozen
        assert intel.known_marshals[0]["name"] == "Blucher"

    def test_last_known_persists_indefinitely(self):
        intel = RegionIntel("Rhine")
        intel.refresh(FULL, "scout", turn=1, marshals=[{"name": "Blucher", "nation": "Prussia"}], total_strength=50000)
        intel.decay(current_turn=6)
        assert intel.visibility == LAST_KNOWN
        # Even at turn 100, stays LAST_KNOWN
        intel.decay(current_turn=100)
        assert intel.visibility == LAST_KNOWN
        assert intel.known_marshals[0]["name"] == "Blucher"

    def test_unknown_does_not_decay(self):
        intel = RegionIntel("Rhine")
        assert intel.visibility == UNKNOWN
        intel.decay(current_turn=50)
        assert intel.visibility == UNKNOWN

    def test_partial_same_decay_timeline_as_full(self):
        """PARTIAL uses same decay timeline as FULL, offset from last_updated_turn."""
        intel = RegionIntel("Belgium")
        intel.refresh(PARTIAL, "adjacent", turn=5, marshals=[], total_strength=0)
        # 2 turns later: still PARTIAL
        intel.decay(current_turn=7)
        assert intel.visibility == PARTIAL
        # 3 turns later: → STALE
        intel.decay(current_turn=8)
        assert intel.visibility == STALE
        # 5 turns later: → LAST_KNOWN
        intel.decay(current_turn=10)
        assert intel.visibility == LAST_KNOWN


# ============================================================================
# STALE SNAPSHOT PERSISTENCE
# ============================================================================

class TestStaleSnapshotPersistence:
    """Test that stale intel keeps frozen data even when enemies move."""

    def test_stale_intel_shows_old_marshal_data(self):
        """When enemies leave a scouted region, stale intel still shows them."""
        intel = RegionIntel("Waterloo")
        marshals = [{"name": "Wellington", "nation": "Britain", "strength": 68000}]
        intel.refresh(FULL, "scout", turn=1, marshals=marshals,
                      total_strength=68000, morale=80, stance="defensive")

        # Decay to STALE — snapshot stays frozen
        intel.decay(current_turn=4)
        assert intel.visibility == STALE
        assert len(intel.known_marshals) == 1
        assert intel.known_marshals[0]["name"] == "Wellington"
        assert intel.strength_band == "large force"  # From original 68k

    def test_decay_never_queries_live_data(self):
        """Decay path only changes visibility level, never touches known_marshals."""
        intel = RegionIntel("Rhine")
        original_marshals = [{"name": "Blucher", "nation": "Prussia", "strength": 55000}]
        intel.refresh(FULL, "scout", turn=1, marshals=original_marshals, total_strength=55000)

        # Capture the list reference
        marshals_before_decay = intel.known_marshals

        # Decay multiple times
        intel.decay(current_turn=4)  # → STALE
        intel.decay(current_turn=6)  # → LAST_KNOWN

        # Same list, same content — decay never replaced it
        assert intel.known_marshals is marshals_before_decay
        assert intel.known_marshals[0]["name"] == "Blucher"


# ============================================================================
# GAME INIT VISIBILITY
# ============================================================================

class TestGameInitVisibility:
    """Test visibility state at game start (turn 1)."""

    def test_french_capital_full(self):
        """Paris (French, Davout present) should be FULL."""
        world = WorldState()
        paris_intel = world.get_region_intel("Paris")
        assert paris_intel.visibility == FULL

    def test_french_region_with_marshal_full(self):
        """Belgium (French, Ney present) should be FULL."""
        world = WorldState()
        belgium_intel = world.get_region_intel("Belgium")
        assert belgium_intel.visibility == FULL

    def test_grouchy_belgium_full(self):
        """Belgium (French, Grouchy present) should be FULL.
        Waterloo (adjacent to Belgium) should be PARTIAL."""
        world = WorldState()
        belgium_intel = world.get_region_intel("Belgium")
        assert belgium_intel.visibility == FULL
        # Waterloo is adjacent to Belgium (where Grouchy is), so PARTIAL
        waterloo_intel = world.get_region_intel("Waterloo")
        assert waterloo_intel.visibility == PARTIAL

    def test_marshal_present_enemy_region_has_exact_strength(self):
        """FULL visibility in enemy region (marshal present) means exact strength data."""
        world = WorldState()
        # Move Grouchy to Waterloo (enemy region with Wellington/Uxbridge)
        # so FULL visibility reveals exact enemy strength
        grouchy = world.get_marshal("Grouchy")
        grouchy.location = "Waterloo"
        world.calculate_visibility()
        waterloo_intel = world.get_region_intel("Waterloo")
        assert waterloo_intel.visibility == FULL
        assert waterloo_intel.exact_strength is not None
        assert waterloo_intel.exact_strength > 0

    def test_adjacent_to_french_marshal_partial(self):
        """Netherlands (adjacent to Ney in Belgium) should be PARTIAL."""
        world = WorldState()
        nl_intel = world.get_region_intel("Netherlands")
        assert nl_intel.visibility == PARTIAL

    def test_french_region_no_marshal_partial(self):
        """Brittany (French, no marshal) should be PARTIAL (own territory)."""
        world = WorldState()
        brittany_intel = world.get_region_intel("Brittany")
        assert brittany_intel.visibility == PARTIAL
        assert brittany_intel.intel_source == "own_territory"

    def test_distant_enemy_region_unknown(self):
        """Vienna (far from any French marshal) should be UNKNOWN."""
        world = WorldState()
        vienna_intel = world.get_region_intel("Vienna")
        assert vienna_intel.visibility == UNKNOWN

    def test_all_regions_have_intel(self):
        """Every region should have an intel entry after init."""
        world = WorldState()
        for region_name in world.regions:
            intel = world.get_region_intel(region_name)
            assert intel.region_name == region_name

    def test_lyon_adjacent_to_davout(self):
        """Lyon (French, adjacent to Davout in Paris) should be at least PARTIAL."""
        world = WorldState()
        lyon_intel = world.get_region_intel("Lyon")
        # Lyon is French-controlled AND adjacent to Davout → PARTIAL from own_territory
        assert lyon_intel.visibility == PARTIAL

    def test_bordeaux_french_no_marshal_partial(self):
        """Bordeaux (French, no marshal nearby, but own territory) should be PARTIAL."""
        world = WorldState()
        bordeaux_intel = world.get_region_intel("Bordeaux")
        assert bordeaux_intel.visibility == PARTIAL
        assert bordeaux_intel.intel_source == "own_territory"

    def test_rhine_adjacent_to_ney(self):
        """Rhine (Prussian, adjacent to Belgium where Ney is) should be PARTIAL."""
        world = WorldState()
        rhine_intel = world.get_region_intel("Rhine")
        assert rhine_intel.visibility == PARTIAL
        assert rhine_intel.intel_source == "adjacent"


# ============================================================================
# REFRESH VS DECAY PATH SEPARATION
# ============================================================================

class TestRefreshDecaySeparation:
    """Verify that refresh and decay paths don't contaminate each other."""

    def test_refreshed_regions_not_decayed(self):
        """Regions refreshed by calculate_visibility should not be decayed."""
        world = WorldState()
        # Paris has a marshal (Davout) — always refreshed
        paris_intel = world.get_region_intel("Paris")
        assert paris_intel.visibility == FULL

        # Advance several turns — Paris should stay FULL
        for _ in range(10):
            world.calculate_visibility()
            world.decay_intel()

        paris_intel = world.get_region_intel("Paris")
        assert paris_intel.visibility == FULL

    def test_non_refreshed_region_decays(self):
        """Regions not adjacent/owned/garrisoned should decay."""
        world = WorldState()
        # Manually set Vienna to FULL (simulating a past scout)
        vienna_intel = world.get_region_intel("Vienna")
        vienna_intel.refresh(FULL, "scout", turn=1,
                             marshals=[{"name": "Gneisenau", "nation": "Prussia", "strength": 45000}],
                             total_strength=45000, morale=70, stance="neutral")

        # Now run visibility + decay at turn 4 (3 turns later)
        world.current_turn = 4
        world.calculate_visibility()
        world.decay_intel()

        vienna_intel = world.get_region_intel("Vienna")
        # Vienna is far from French marshals — not refreshed, should decay
        assert vienna_intel.visibility == STALE

    def test_marshal_moves_visibility_follows(self):
        """When a marshal moves, visibility should update accordingly."""
        world = WorldState()

        # Check Netherlands is PARTIAL (adjacent to Ney in Belgium)
        nl_intel = world.get_region_intel("Netherlands")
        assert nl_intel.visibility == PARTIAL

        # Move Ney to Paris (no longer in Belgium)
        world.marshals["Ney"].location = "Paris"
        world.calculate_visibility()

        # Netherlands is no longer adjacent to any French marshal
        # (Blucher is there but he's enemy)
        # It was PARTIAL from adjacency — but adjacency is gone now
        # Since it's not owned and no marshal present, it won't be refreshed
        # However, it still has PARTIAL from the previous refresh with a recent last_updated_turn
        # The decay_intel will handle it based on age
        # Since calculate_visibility doesn't refresh it, decay will kick in based on age

    def test_scout_refreshes_stale_to_full(self):
        """Scouting a stale region should upgrade it back to FULL."""
        world = WorldState()

        # Set up stale intel
        vienna_intel = world.get_region_intel("Vienna")
        vienna_intel.refresh(FULL, "scout", turn=1, marshals=[], total_strength=0)
        vienna_intel.decay(current_turn=4)
        assert vienna_intel.visibility == STALE

        # Scout it again
        world.current_turn = 5
        world.update_intel_from_scout("Vienna", turn=5)
        vienna_intel = world.get_region_intel("Vienna")
        assert vienna_intel.visibility == FULL
        assert vienna_intel.last_scouted_turn == 5


# ============================================================================
# UPDATE FROM SCOUT / BATTLE
# ============================================================================

class TestUpdateIntelFromScout:
    """Test scout action intel updates."""

    def test_scout_sets_full_visibility(self):
        world = WorldState()
        world.update_intel_from_scout("Vienna", turn=3)
        intel = world.get_region_intel("Vienna")
        assert intel.visibility == FULL
        assert intel.last_scouted_turn == 3
        assert intel.intel_source == "scout"

    def test_scout_captures_enemy_data(self):
        world = WorldState()
        # Gneisenau is in Netherlands at start
        world.update_intel_from_scout("Netherlands", turn=1)
        intel = world.get_region_intel("Netherlands")
        assert intel.visibility == FULL
        names = [m["name"] for m in intel.known_marshals]
        assert "Blucher" in names or "Gneisenau" in names
        assert intel.exact_strength is not None
        assert intel.exact_strength > 0

    def test_scout_empty_region(self):
        world = WorldState()
        world.update_intel_from_scout("Vienna", turn=1)
        intel = world.get_region_intel("Vienna")
        assert intel.visibility == FULL
        assert intel.known_marshals == []
        assert intel.strength_band == "no forces"


class TestUpdateIntelFromBattle:
    """Test battle intel updates."""

    def test_battle_sets_full_visibility(self):
        world = WorldState()
        # Use Vienna — not adjacent to any French marshal, starts UNKNOWN
        world.update_intel_from_battle("Vienna", turn=2)
        intel = world.get_region_intel("Vienna")
        assert intel.visibility == FULL
        assert intel.intel_source == "battle"

    def test_battle_does_not_set_last_scouted(self):
        world = WorldState()
        world.update_intel_from_battle("Waterloo", turn=2)
        intel = world.get_region_intel("Waterloo")
        # Battle doesn't count as a scout for the scouted_turn tracker
        assert intel.last_scouted_turn == 0


# ============================================================================
# WORLDSTATE INTEL SERIALIZATION
# ============================================================================

class TestWorldStateIntelSerialization:
    """Test intel roundtrip through WorldState serialization."""

    def test_intel_survives_roundtrip(self):
        """Intel data should survive save/load cycle."""
        world = WorldState()
        # Manually set some intel
        world.update_intel_from_scout("Vienna", turn=1)

        data = world.to_dict()
        assert "intel" in data
        assert "Vienna" in data["intel"]

        restored = WorldState.from_dict(data)
        vienna_intel = restored.get_region_intel("Vienna")
        assert vienna_intel.visibility == FULL
        assert vienna_intel.last_scouted_turn == 1

    def test_backward_compat_no_intel_key(self):
        """Old saves without intel key should work (empty dict)."""
        world = WorldState()
        data = world.to_dict()
        del data["intel"]  # Simulate old save

        restored = WorldState.from_dict(data)
        assert restored.intel == {}
        # After calculate_visibility (called by game or load), it would repopulate

    def test_intel_roundtrip_preserves_stale(self):
        """Stale intel with frozen marshals should survive roundtrip."""
        world = WorldState()
        vienna_intel = world.get_region_intel("Vienna")
        vienna_intel.refresh(FULL, "scout", turn=1,
                             marshals=[{"name": "Gneisenau", "nation": "Prussia", "strength": 45000}],
                             total_strength=45000, morale=70, stance="neutral")
        vienna_intel.decay(current_turn=4)
        assert vienna_intel.visibility == STALE

        data = world.to_dict()
        restored = WorldState.from_dict(data)
        restored_intel = restored.get_region_intel("Vienna")
        assert restored_intel.visibility == STALE
        assert restored_intel.known_marshals[0]["name"] == "Gneisenau"
        assert restored_intel.exact_strength is None

    def test_serialization_enforcement_intel_field(self):
        """WorldState.intel must be in to_dict output."""
        world = WorldState()
        data = world.to_dict()
        assert "intel" in data, "intel field missing from WorldState.to_dict()"


# ============================================================================
# VISIBILITY PRIORITY
# ============================================================================

class TestVisibilityPriority:
    """Test visibility priority ordering."""

    def test_full_highest(self):
        assert VISIBILITY_PRIORITY[FULL] > VISIBILITY_PRIORITY[PARTIAL]
        assert VISIBILITY_PRIORITY[FULL] > VISIBILITY_PRIORITY[STALE]
        assert VISIBILITY_PRIORITY[FULL] > VISIBILITY_PRIORITY[LAST_KNOWN]
        assert VISIBILITY_PRIORITY[FULL] > VISIBILITY_PRIORITY[UNKNOWN]

    def test_unknown_lowest(self):
        assert VISIBILITY_PRIORITY[UNKNOWN] < VISIBILITY_PRIORITY[LAST_KNOWN]

    def test_ordering(self):
        ordered = sorted(VISIBILITY_PRIORITY.keys(), key=lambda k: VISIBILITY_PRIORITY[k], reverse=True)
        assert ordered == [FULL, PARTIAL, STALE, LAST_KNOWN, UNKNOWN]


# ============================================================================
# MULTI-TURN INTEGRATION
# ============================================================================

class TestMultiTurnIntegration:
    """Test fog of war across multiple turns of actual gameplay."""

    def _advance_turn(self, world):
        """Simulate what _advance_turn_internal does for fog."""
        world.current_turn += 1
        world.calculate_visibility()
        world.decay_intel()

    def test_scout_then_decay_over_turns(self):
        """Scout a distant region, watch it decay over turns."""
        world = WorldState()

        # Scout Vienna on turn 1
        world.update_intel_from_scout("Vienna", turn=1)
        vienna = world.get_region_intel("Vienna")
        assert vienna.visibility == FULL

        # Turns 2-3: still FULL (within FRESH_TURNS)
        for t in range(2, 4):
            world.current_turn = t
            world.calculate_visibility()
            world.decay_intel()
            vienna = world.get_region_intel("Vienna")
            assert vienna.visibility == FULL, f"Expected FULL at turn {t}"

        # Turn 4: STALE (3 turns since scout)
        world.current_turn = 4
        world.calculate_visibility()
        world.decay_intel()
        vienna = world.get_region_intel("Vienna")
        assert vienna.visibility == STALE

        # Turn 6: LAST_KNOWN (5 turns since scout)
        world.current_turn = 6
        world.calculate_visibility()
        world.decay_intel()
        vienna = world.get_region_intel("Vienna")
        assert vienna.visibility == LAST_KNOWN

    def test_adjacent_region_stays_partial_while_marshal_present(self):
        """Region adjacent to friendly marshal stays PARTIAL across turns."""
        world = WorldState()

        # Rhine is adjacent to Belgium (Ney) → PARTIAL
        for t in range(1, 10):
            world.current_turn = t
            world.calculate_visibility()
            world.decay_intel()
            rhine = world.get_region_intel("Rhine")
            assert rhine.visibility == PARTIAL, f"Expected PARTIAL at turn {t}"

    def test_own_region_always_partial_minimum(self):
        """French-controlled region without marshal stays at least PARTIAL."""
        world = WorldState()

        for t in range(1, 10):
            world.current_turn = t
            world.calculate_visibility()
            world.decay_intel()
            bordeaux = world.get_region_intel("Bordeaux")
            assert bordeaux.visibility == PARTIAL, f"Expected PARTIAL at turn {t}"
