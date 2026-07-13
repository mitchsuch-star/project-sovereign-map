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

from backend.models.intel import (
    RegionIntel, FULL, PARTIAL, STALE, LAST_KNOWN, UNKNOWN,
    VISIBILITY_PRIORITY, get_strength_band,
)
from backend.models.world_state import WorldState


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
        intel = RegionIntel("Rhineland")
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
        intel = RegionIntel("Rhineland")
        intel.refresh(FULL, "scout", turn=1, marshals=[], total_strength=0)
        # Turn 2: 1 turn since update — still FULL
        intel.decay(current_turn=2)
        assert intel.visibility == FULL
        # Turn 3: 2 turns since update — still FULL (FRESH_TURNS = 2)
        intel.decay(current_turn=3)
        assert intel.visibility == FULL

    def test_full_degrades_to_stale_at_turn_3(self):
        intel = RegionIntel("Rhineland")
        intel.refresh(FULL, "scout", turn=1, marshals=[], total_strength=50000, morale=70, stance="neutral")
        # Turn 4: 3 turns since update → STALE
        intel.decay(current_turn=4)
        assert intel.visibility == STALE
        assert intel.exact_strength is None  # Cleared
        assert intel.morale is None

    def test_stale_degrades_to_last_known_at_turn_5(self):
        intel = RegionIntel("Rhineland")
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
        intel = RegionIntel("Rhineland")
        intel.refresh(FULL, "scout", turn=1, marshals=[{"name": "Blucher", "nation": "Prussia"}], total_strength=50000)
        intel.decay(current_turn=6)
        assert intel.visibility == LAST_KNOWN
        # Even at turn 100, stays LAST_KNOWN
        intel.decay(current_turn=100)
        assert intel.visibility == LAST_KNOWN
        assert intel.known_marshals[0]["name"] == "Blucher"

    def test_unknown_does_not_decay(self):
        intel = RegionIntel("Rhineland")
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
        intel = RegionIntel("Rhineland")
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

    def test_lyon_has_grouchy_full(self):
        """Lyon (French, Grouchy stationed here) should be FULL."""
        world = WorldState()
        lyon_intel = world.get_region_intel("Lyon")
        # Lyon has Grouchy (French marshal) → FULL from marshal_present
        assert lyon_intel.visibility == FULL

    def test_bordeaux_french_no_marshal_partial(self):
        """Bordeaux (French, no marshal nearby, but own territory) should be PARTIAL."""
        world = WorldState()
        bordeaux_intel = world.get_region_intel("Bordeaux")
        assert bordeaux_intel.visibility == PARTIAL
        assert bordeaux_intel.intel_source == "own_territory"

    def test_rhine_adjacent_to_ney(self):
        """Rhine (Prussian, adjacent to Belgium where Ney is) should be PARTIAL."""
        world = WorldState()
        rhine_intel = world.get_region_intel("Rhineland")
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
        # Wellington is at Waterloo at start (enemy from France's POV)
        world.update_intel_from_scout("Waterloo", turn=1)
        intel = world.get_region_intel("Waterloo")
        assert intel.visibility == FULL
        names = [m["name"] for m in intel.known_marshals]
        assert "Wellington" in names
        assert intel.exact_strength is not None
        assert intel.exact_strength > 0

    def test_scout_empty_region(self):
        world = WorldState()
        world.update_intel_from_scout("Tyrol", turn=1)
        intel = world.get_region_intel("Tyrol")
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

    def test_battle_sets_last_scouted_for_persistent_full(self):
        """Battle sets last_scouted_turn so FULL persists after marshal leaves.
        Without this, ephemeral marshal_present downgrade would kill battle FULL."""
        world = WorldState()
        world.update_intel_from_battle("Waterloo", turn=2)
        intel = world.get_region_intel("Waterloo")
        assert intel.last_scouted_turn == 2


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
            rhine = world.get_region_intel("Rhineland")
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


# ============================================================================
# EPHEMERAL MARSHAL_PRESENT TESTS
# ============================================================================

class TestEphemeralMarshalPresent:
    """Marshal-present FULL is ephemeral — only while standing there.
    Scout and battle FULL persist for 2 turns."""

    def test_marshal_present_full_while_standing(self):
        """Region has FULL while a friendly marshal is there."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        # Move Ney to an enemy region
        ney.location = "Waterloo"
        world.calculate_visibility()
        intel = world.get_region_intel("Waterloo")
        assert intel.visibility == FULL
        assert intel.intel_source == "marshal_present"

    def test_marshal_present_full_lost_on_departure(self):
        """FULL from marshal_present drops when marshal leaves."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        ney.location = "Waterloo"
        world.current_turn = 1
        world.calculate_visibility()

        intel = world.get_region_intel("Waterloo")
        assert intel.visibility == FULL
        assert intel.intel_source == "marshal_present"

        # Marshal leaves — move to adjacent region
        ney.location = "Belgium"
        world.current_turn = 2
        world.calculate_visibility()

        intel = world.get_region_intel("Waterloo")
        # Should NOT stay FULL — marshal_present is ephemeral
        assert intel.visibility != FULL

    def test_marshal_leaves_drops_to_partial(self):
        """After marshal leaves, non-scouted region drops to PARTIAL."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        ney.location = "Waterloo"
        world.current_turn = 1
        world.calculate_visibility()

        ney.location = "Belgium"
        world.current_turn = 2
        world.calculate_visibility()

        intel = world.get_region_intel("Waterloo")
        # Waterloo is adjacent to Belgium, so gets PARTIAL from adjacency
        assert intel.visibility == PARTIAL

    def test_scout_full_persists_after_leaving(self):
        """Scouted FULL persists for 2 turns even after marshal leaves."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"

        # Scout Waterloo at turn 1
        world.current_turn = 1
        world.update_intel_from_scout("Waterloo", turn=1)
        intel = world.get_region_intel("Waterloo")
        assert intel.visibility == FULL
        assert intel.last_scouted_turn == 1

        # Move Ney into Waterloo then out — marshal_present overwrites source
        ney.location = "Waterloo"
        world.calculate_visibility()
        ney.location = "Belgium"
        world.current_turn = 2
        world.calculate_visibility()

        # Scout was at turn 1, now turn 2 — within FRESH_TURNS (2).
        # Should fall back to scout FULL, not downgrade.
        intel = world.get_region_intel("Waterloo")
        assert intel.visibility == FULL
        assert intel.intel_source == "scout"

    def test_battle_full_persists_after_leaving(self):
        """Battle FULL persists for 2 turns even after marshal leaves."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        ney.location = "Waterloo"

        # Battle at turn 1
        world.current_turn = 1
        world.update_intel_from_battle("Waterloo", turn=1)
        intel = world.get_region_intel("Waterloo")
        assert intel.visibility == FULL
        assert intel.last_scouted_turn == 1  # Battle now sets this

        # Marshal_present overwrites source
        world.calculate_visibility()
        assert intel.intel_source == "marshal_present"

        # Marshal leaves
        ney.location = "Belgium"
        world.current_turn = 2
        world.calculate_visibility()

        # Battle was turn 1, now turn 2 — within FRESH_TURNS.
        # Should fall back to battle/scout FULL.
        intel = world.get_region_intel("Waterloo")
        assert intel.visibility == FULL
        assert intel.intel_source == "scout"  # Falls back to scout source

    def test_old_scout_does_not_prevent_downgrade(self):
        """Scout from many turns ago doesn't prevent marshal_present downgrade."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"

        # Scout Waterloo at turn 1
        world.current_turn = 1
        world.update_intel_from_scout("Waterloo", turn=1)

        # Many turns pass — scout is stale
        world.current_turn = 10
        ney.location = "Waterloo"
        world.calculate_visibility()
        assert world.get_region_intel("Waterloo").visibility == FULL

        # Marshal leaves
        ney.location = "Belgium"
        world.current_turn = 11
        world.calculate_visibility()

        # Scout was at turn 1, now turn 11 — way past FRESH_TURNS.
        # marshal_present downgrade should apply.
        intel = world.get_region_intel("Waterloo")
        assert intel.visibility != FULL

    def test_two_marshals_one_leaves(self):
        """If two marshals in region and one leaves, FULL stays from other."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        davout = world.get_marshal("Davout")
        ney.location = "Waterloo"
        davout.location = "Waterloo"
        world.current_turn = 1
        world.calculate_visibility()

        intel = world.get_region_intel("Waterloo")
        assert intel.visibility == FULL

        # Ney leaves, Davout stays
        ney.location = "Belgium"
        world.calculate_visibility()

        intel = world.get_region_intel("Waterloo")
        assert intel.visibility == FULL  # Davout still there

    def test_enemy_hidden_after_marshal_leaves_unscouted(self):
        """Enemy entering an unscouted region after marshal left is not visible at FULL."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        # Ney visits Bavaria (no enemies there)
        ney.location = "Bavaria"
        wellington.location = "London"
        world.current_turn = 1
        world.calculate_visibility()

        intel = world.get_region_intel("Bavaria")
        assert intel.visibility == FULL

        # Ney leaves, enemy moves in
        ney.location = "Rhineland"
        wellington.location = "Bavaria"
        world.current_turn = 2
        world.calculate_visibility()

        intel = world.get_region_intel("Bavaria")
        # Bavaria should NOT be FULL — marshal left, wasn't scouted
        assert intel.visibility != FULL

    def test_own_territory_drops_to_partial_when_all_marshals_leave(self):
        """Own region with marshal is FULL. When ALL marshals leave, drops to
        PARTIAL (Step 1: own region without marshal)."""
        world = WorldState()
        # Move ALL French marshals to Paris first
        for m in world.marshals.values():
            if m.nation == "France":
                m.location = "Paris"
        world.current_turn = 1
        world.calculate_visibility()

        intel = world.get_region_intel("Paris")
        assert intel.visibility == FULL
        assert intel.intel_source == "own_territory"

        # All marshals leave Paris
        for m in world.marshals.values():
            if m.nation == "France":
                m.location = "Belgium"
        world.current_turn = 2
        world.calculate_visibility()

        # Paris is own territory without marshal — Step 1 gives PARTIAL military
        intel = world.get_region_intel("Paris")
        assert intel.visibility == PARTIAL


# ============================================================================
# STALE INTEL MAP DATA INJECTION (Session 38)
# ============================================================================

class TestStaleIntelMapInjection:
    """Test that stale intel injects frozen snapshots into fogged_forces for Godot."""

    def test_stale_ghost_shows_when_enemies_left(self):
        """When enemies leave a scouted region, stale intel injects fogged_forces."""
        world = WorldState()
        # Move all British out of Waterloo
        for m in world.marshals.values():
            if m.nation == "Britain" and m.location == "Waterloo":
                m.location = "Bavaria"

        # Scout Waterloo with Wellington snapshot
        intel = world.get_region_intel("Waterloo")
        intel.refresh(FULL, "scout", turn=1, marshals=[
            {"name": "Wellington", "nation": "Britain", "strength": 50000,
             "band": get_strength_band(50000)}
        ], total_strength=50000)

        # Decay to stale
        intel.decay(current_turn=4)
        assert intel.visibility == STALE

        filtered = world.get_filtered_game_state_summary()
        wloo = filtered["map_data"]["Waterloo"]
        assert len(wloo["fogged_forces"]) == 1
        assert wloo["fogged_forces"][0]["name"] == "Wellington"
        assert wloo["fogged_forces"][0]["fog_level"] == STALE

    def test_stale_ghost_cleared_when_visible_elsewhere(self):
        """Stale ghost disappears when enemy is visible at FULL/PARTIAL elsewhere."""
        world = WorldState()
        # Move all British out of Waterloo
        for m in world.marshals.values():
            if m.nation == "Britain" and m.location == "Waterloo":
                m.location = "Bavaria"

        # Scout Waterloo with Wellington snapshot
        intel_w = world.get_region_intel("Waterloo")
        intel_w.refresh(FULL, "scout", turn=1, marshals=[
            {"name": "Wellington", "nation": "Britain", "strength": 50000,
             "band": get_strength_band(50000)}
        ], total_strength=50000)

        # Decay Waterloo to stale
        intel_w.decay(current_turn=4)

        # Now see Wellington at Bavaria (move Ney there for FULL visibility)
        world.marshals["Ney"].location = "Bavaria"
        world.current_turn = 4
        world.calculate_visibility()

        filtered = world.get_filtered_game_state_summary()
        wloo = filtered["map_data"]["Waterloo"]
        bav = filtered["map_data"]["Bavaria"]

        # Ghost should be gone — Wellington visible at Bavaria
        assert len(wloo["fogged_forces"]) == 0, "Stale ghost should clear when enemy visible elsewhere"
        assert any(m["name"] == "Wellington" for m in bav["marshals"]), \
            "Wellington should be visible at Bavaria"


# ============================================================================
# DISPLAY-ONLY MARSHAL "arm" FIELD (map war-table pieces, UI-5)
# ============================================================================

class TestMarshalArmField:
    """The filtered summary ships a display-only top-level `arm` for every
    VISIBLE marshal so the Godot map can key its war-table piece to the arm —
    including enemies (whose tactical_state is player-only). It must never leak
    for a fogged enemy reduced to a silhouette."""

    def _find_marshal(self, filtered, region, name):
        for m in filtered["map_data"][region]["marshals"]:
            if m["name"] == name:
                return m
        return None

    def test_own_marshal_arm_matches_type(self):
        world = WorldState()
        davout = world.get_marshal("Davout")   # French (player), at Paris (FULL)
        davout.cavalry = False
        davout.artillery = True
        world.calculate_visibility()
        filtered = world.get_filtered_game_state_summary()
        md = self._find_marshal(filtered, davout.location, "Davout")
        assert md is not None and md["arm"] == "artillery"

    def test_infantry_is_the_default_arm(self):
        world = WorldState()
        davout = world.get_marshal("Davout")
        davout.cavalry = False
        davout.artillery = False
        world.calculate_visibility()
        filtered = world.get_filtered_game_state_summary()
        md = self._find_marshal(filtered, davout.location, "Davout")
        assert md is not None and md["arm"] == "infantry"

    def test_enemy_marshal_arm_present_at_full(self):
        """The whole point: an enemy corps carries its arm at FULL visibility
        (tactical_state is player-only, so without the top-level field every
        enemy would draw as infantry)."""
        world = WorldState()
        wellington = world.get_marshal("Wellington")   # enemy (British)
        wellington.cavalry = True
        wellington.artillery = False
        # Put a French marshal on Wellington's region for FULL visibility.
        grouchy = world.get_marshal("Grouchy")
        grouchy.location = wellington.location
        world.calculate_visibility()
        filtered = world.get_filtered_game_state_summary()
        md = self._find_marshal(filtered, wellington.location, "Wellington")
        assert md is not None, "Wellington should be visible at FULL"
        assert md["arm"] == "cavalry", "enemy arm must ride the FULL-visibility marshal dict"

    def test_arm_never_leaks_into_fogged_forces(self):
        """A PARTIAL/STALE enemy is reduced to a silhouette (name/nation/band
        only) — the arm must not ride along."""
        world = WorldState()
        filtered = world.get_filtered_game_state_summary()
        for region_data in filtered["map_data"].values():
            for fogged in region_data["fogged_forces"]:
                assert "arm" not in fogged, (
                    "arm leaked into a fogged silhouette — fog boundary broken"
                )

    def test_stale_ghost_only_for_enemy_marshals(self):
        """Stale injection should not include player's own marshals."""
        world = WorldState()

        # Use Marseille (empty region, no initial marshals)
        # Create stale intel with a French marshal snapshot (edge case)
        intel = world.get_region_intel("Marseille")
        intel.refresh(FULL, "scout", turn=1, marshals=[
            {"name": "Ney", "nation": "France", "strength": 30000,
             "band": get_strength_band(30000)}
        ], total_strength=30000)

        # Move Ney away (already at Belgium by default) and decay
        intel.decay(current_turn=4)

        filtered = world.get_filtered_game_state_summary()
        marseille = filtered["map_data"]["Marseille"]
        # Own marshal should NOT appear as fogged ghost
        assert len(marseille["fogged_forces"]) == 0, "Player marshals should not appear as stale ghosts"
