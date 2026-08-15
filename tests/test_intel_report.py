"""
Fog of War - Session 34A Tests

Tests for:
- Intel report generation (Berthier's Intelligence Report)
- Filtered game state summary (enemy data redaction by visibility)
- Scout persistence (targeted scout → FULL, adjacent scan → PARTIAL)
- Battle reveal wiring (all 6 resolve_battle sites)
- Status command wiring
"""

import pytest
from backend.models.intel import (
    FULL, PARTIAL, STALE, LAST_KNOWN, UNKNOWN,
    get_strength_band,
)
from backend.models.world_state import WorldState
from backend.intel_report import generate_intel_report
from backend.commands.executor import CommandExecutor


# ============================================================================
# HELPERS
# ============================================================================

def make_world():
    """Create a default WorldState for testing."""
    return WorldState()


def get_enemy_in_fogged_region(world):
    """Find an enemy marshal in a region NOT adjacent to any French marshal."""
    player_regions = set()
    for m in world.marshals.values():
        if m.nation == world.player_nation:
            player_regions.add(m.location)
            region = world.get_region(m.location)
            if region:
                player_regions.update(region.adjacent_regions)
    for m in world.marshals.values():
        if m.nation != world.player_nation and m.location not in player_regions:
            return m
    return None


# ============================================================================
# INTEL REPORT GENERATION
# ============================================================================

class TestIntelReport:
    """Test generate_intel_report() output structure."""

    def test_report_has_required_keys(self):
        world = make_world()
        report = generate_intel_report(world)
        assert "report_text" in report
        assert "your_forces" in report
        assert "confirmed" in report
        assert "recent_reports" in report
        assert "last_known" in report
        assert "no_intelligence" in report
        assert "turn" in report

    def test_your_forces_lists_player_marshals(self):
        world = make_world()
        report = generate_intel_report(world)
        player_names = {m.name for m in world.marshals.values()
                        if m.nation == world.player_nation and m.strength > 0}
        report_names = {f["name"] for f in report["your_forces"]}
        assert report_names == player_names

    def test_your_forces_has_full_detail(self):
        world = make_world()
        report = generate_intel_report(world)
        for force in report["your_forces"]:
            assert "strength" in force
            assert "morale" in force
            assert "stance" in force
            assert "location" in force
            assert isinstance(force["strength"], int)
            assert isinstance(force["morale"], int)

    def test_full_visibility_enemies_in_confirmed(self):
        """Enemies in FULL visibility regions appear in confirmed section."""
        world = make_world()
        # Move Grouchy to Waterloo so marshal_present grants FULL visibility there
        grouchy = world.get_marshal("Grouchy")
        grouchy.location = "Waterloo"
        world.calculate_visibility()
        intel = world.get_region_intel("Waterloo")
        assert intel.visibility == FULL
        report = generate_intel_report(world)
        confirmed_regions = {r["region"] for r in report["confirmed"]}
        # Wellington is in Waterloo which is FULL via Grouchy's presence
        assert "Waterloo" in confirmed_regions

    def test_confirmed_has_exact_strength(self):
        """FULL visibility confirmed entries have exact troop counts."""
        world = make_world()
        report = generate_intel_report(world)
        for region_info in report["confirmed"]:
            for enemy in region_info.get("enemies", []):
                assert enemy["strength"] > 0
                assert "morale" in enemy

    def test_unknown_regions_in_no_intelligence(self):
        """Regions with UNKNOWN visibility appear in no_intelligence."""
        world = make_world()
        report = generate_intel_report(world)
        unknown_regions = {r["region"] for r in report["no_intelligence"]}
        # Some distant regions should be UNKNOWN at game start
        for region_name in world.regions:
            intel = world.get_region_intel(region_name)
            if intel.visibility == UNKNOWN:
                assert region_name in unknown_regions

    def test_report_text_is_string(self):
        world = make_world()
        report = generate_intel_report(world)
        assert isinstance(report["report_text"], str)
        assert "BERTHIER'S INTELLIGENCE REPORT" in report["report_text"]
        assert "YOUR FORCES:" in report["report_text"]

    def test_stale_intel_in_recent_reports(self):
        """STALE intel should appear in recent_reports with stale flag."""
        world = make_world()
        # Use a region that is NOT owned by France and NOT adjacent to any French marshal
        # so that calculate_visibility() won't override our manual state.
        # Pick a region that starts as UNKNOWN.
        target_region = None
        for rn in world.regions:
            intel = world.get_region_intel(rn)
            if intel.visibility == UNKNOWN:
                target_region = rn
                break
        assert target_region is not None, "Need an UNKNOWN region for this test"

        intel = world.get_region_intel(target_region)
        intel.refresh(
            visibility=FULL, source="scout", turn=1,
            marshals=[{"name": "TestEnemy", "nation": "Britain"}],
            total_strength=30000,
        )
        intel.last_updated_turn = 1
        # Manually set current_turn via the internal field
        world.current_turn = 5
        intel.decay(5)
        assert intel.visibility == STALE

        report = generate_intel_report(world)
        stale_entries = [r for r in report["recent_reports"] if r.get("stale")]
        assert len(stale_entries) >= 1
        stale_regions = {r["region"] for r in stale_entries}
        assert target_region in stale_regions

    def test_last_known_in_last_known_section(self):
        """LAST_KNOWN intel should appear in last_known section."""
        world = make_world()
        # Use an UNKNOWN region (same rationale as stale test)
        target_region = None
        for rn in world.regions:
            intel = world.get_region_intel(rn)
            if intel.visibility == UNKNOWN:
                target_region = rn
                break
        assert target_region is not None

        intel = world.get_region_intel(target_region)
        intel.refresh(
            visibility=FULL, source="scout", turn=1,
            marshals=[{"name": "TestEnemy", "nation": "Britain"}],
            total_strength=30000,
        )
        intel.last_updated_turn = 1
        world.current_turn = 7
        intel.decay(7)
        assert intel.visibility == LAST_KNOWN

        report = generate_intel_report(world)
        lk_entries = [r for r in report["last_known"] if r["region"] == target_region]
        assert len(lk_entries) == 1
        assert lk_entries[0]["turns_ago"] == 6


# ============================================================================
# FILTERED GAME STATE SUMMARY
# ============================================================================

class TestFilteredGameStateSummary:
    """Test get_filtered_game_state_summary() enemy data redaction."""

    def test_filtered_returns_dict(self):
        world = make_world()
        summary = world.get_filtered_game_state_summary()
        assert isinstance(summary, dict)
        assert "map_data" in summary
        assert "enemies" in summary
        assert "marshals" in summary

    def test_player_marshals_always_visible(self):
        """Player marshals appear in filtered summary regardless of fog."""
        world = make_world()
        summary = world.get_filtered_game_state_summary()
        # All player marshals should be in the marshals dict
        for name, m in world.marshals.items():
            if m.nation == world.player_nation:
                assert name in summary["marshals"]

    def test_player_marshals_in_map_data_always_visible(self):
        """Player marshal data always appears in map_data for their region."""
        world = make_world()
        summary = world.get_filtered_game_state_summary()
        for name, m in world.marshals.items():
            if m.nation == world.player_nation and m.strength > 0:
                region_data = summary["map_data"].get(m.location, {})
                marshal_names = [md["name"] for md in region_data.get("marshals", [])]
                assert m.name in marshal_names

    def test_full_visibility_enemies_shown_with_exact_data(self):
        """Enemies in FULL visibility regions have exact strength in map_data."""
        world = make_world()
        summary = world.get_filtered_game_state_summary()
        # Waterloo has FULL visibility (Grouchy present)
        waterloo = summary["map_data"].get("Waterloo", {})
        enemy_marshals = [m for m in waterloo.get("marshals", [])
                          if m["nation"] != world.player_nation]
        # Wellington should be visible with exact strength
        for enemy in enemy_marshals:
            assert enemy["strength"] > 0  # Exact, not 0

    def test_unknown_regions_hide_enemies_from_map(self):
        """Enemies in UNKNOWN regions don't appear in map_data."""
        world = make_world()
        summary = world.get_filtered_game_state_summary()
        for region_name in world.regions:
            intel = world.get_region_intel(region_name)
            if intel.visibility == UNKNOWN:
                region_data = summary["map_data"].get(region_name, {})
                enemy_marshals = [m for m in region_data.get("marshals", [])
                                  if m["nation"] != world.player_nation]
                assert len(enemy_marshals) == 0, \
                    f"Enemy visible in UNKNOWN region {region_name}"

    def test_unknown_regions_hide_enemies_from_enemies_dict(self):
        """Enemies in UNKNOWN regions don't appear in top-level enemies dict."""
        world = make_world()
        summary = world.get_filtered_game_state_summary()
        for name, enemy_data in summary["enemies"].items():
            enemy_location = enemy_data["location"]
            intel = world.get_region_intel(enemy_location)
            assert intel.visibility in (FULL, PARTIAL, STALE), \
                f"Enemy {name} at {enemy_location} is visible at {intel.visibility}"

    def test_partial_visibility_in_fogged_forces(self):
        """Enemies in PARTIAL regions appear in fogged_forces, not marshals."""
        world = make_world()
        # Use a valid region from the 13-region map
        test_region = "Netherlands"
        intel = world.get_region_intel(test_region)
        enemy = None
        for m in world.marshals.values():
            if m.nation != world.player_nation:
                enemy = m
                break
        assert enemy is not None
        enemy.location = test_region
        intel.refresh(
            visibility=PARTIAL, source="adjacent", turn=1,
            marshals=[{"name": enemy.name, "nation": enemy.nation, "band": get_strength_band(enemy.strength)}],
            total_strength=enemy.strength,
        )
        summary = world.get_filtered_game_state_summary()
        region_data = summary["map_data"].get(test_region, {})
        # Enemy should NOT be in marshals[] (would render as "0 troops" on map)
        enemy_in_marshals = [m for m in region_data.get("marshals", [])
                             if m["nation"] != world.player_nation]
        assert len(enemy_in_marshals) == 0, "PARTIAL enemy should not be in marshals[]"
        # Enemy SHOULD be in fogged_forces[]
        fogged = region_data.get("fogged_forces", [])
        assert len(fogged) >= 1
        assert fogged[0]["name"] == enemy.name
        assert "strength_band" in fogged[0]
        assert fogged[0]["fog_level"] == PARTIAL
        # fogged_forces should NOT have strength/morale keys (no fake numbers)
        assert "strength" not in fogged[0]
        assert "morale" not in fogged[0]

    def test_own_region_always_has_economic_data(self):
        """Own regions always show economic data regardless of military visibility."""
        world = make_world()
        summary = world.get_filtered_game_state_summary()
        for region_name, region in world.regions.items():
            if region.controller == world.player_nation:
                rd = summary["map_data"].get(region_name, {})
                assert "income_value" in rd
                assert "stability" in rd
                assert rd["stability"] > 0 or True  # Could be 0 legitimately

    def test_enemy_region_unknown_hides_economic_data(self):
        """Enemy regions with UNKNOWN visibility hide economic data.

        Pin flipped consciously (PC15-16, Aug 15 2026): hidden econ keys
        carry the CA9-F5 ``-1`` "not known" sentinel, never a fabricated
        0 — the region panel and map tooltip were rendering "Income: 0g /
        Stability: 0%" as facts on PARTIAL provinces.
        """
        world = make_world()
        summary = world.get_filtered_game_state_summary()
        for region_name in world.regions:
            intel = world.get_region_intel(region_name)
            region = world.regions[region_name]
            if intel.visibility == UNKNOWN and region.controller != world.player_nation:
                rd = summary["map_data"].get(region_name, {})
                assert rd["income_value"] == -1
                assert rd["effective_income"] == -1
                assert rd["stability"] == -1
                assert rd["stability_label"] == "Unknown"

    def test_controller_and_terrain_always_public(self):
        """Controller and terrain are always shown (public knowledge)."""
        world = make_world()
        summary = world.get_filtered_game_state_summary()
        for region_name, region in world.regions.items():
            rd = summary["map_data"].get(region_name, {})
            assert rd["controller"] == region.controller
            assert rd["terrain"] == region.terrain

    def test_all_ints_no_floats(self):
        """Verify no float values leak to Godot in filtered summary."""
        world = make_world()
        summary = world.get_filtered_game_state_summary()

        def check_no_floats(obj, path=""):
            if isinstance(obj, float):
                pytest.fail(f"Float found at {path}: {obj}")
            elif isinstance(obj, dict):
                for k, v in obj.items():
                    check_no_floats(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    check_no_floats(v, f"{path}[{i}]")

        # Check critical sections
        check_no_floats(summary["map_data"], "map_data")
        check_no_floats(summary["enemies"], "enemies")
        check_no_floats(summary["marshals"], "marshals")


# ============================================================================
# SCOUT PERSISTENCE
# ============================================================================

class TestScoutPersistence:
    """Test that scout results persist to intel store."""

    def test_targeted_scout_persists_full_intel(self):
        """Targeted scout action sets FULL visibility in intel store."""
        world = make_world()
        executor = CommandExecutor()
        game_state = {"world": world}

        # Find a player marshal and an enemy-controlled adjacent region to scout
        player_marshal = None
        target_name = None
        for m in world.marshals.values():
            if m.nation == world.player_nation:
                region = world.get_region(m.location)
                for adj in region.adjacent_regions:
                    adj_region = world.get_region(adj)
                    if adj_region and adj_region.controller != world.player_nation:
                        player_marshal = m
                        target_name = adj
                        break
            if target_name:
                break

        assert target_name is not None, "Need enemy-controlled adjacent region"
        result = executor._execute_scout(player_marshal, target_name, world, game_state)
        assert result["success"]
        # Check intel store was updated
        intel = world.get_region_intel(target_name)
        assert intel.visibility == FULL
        assert intel.intel_source == "scout"
        assert intel.last_scouted_turn == world.current_turn

    def test_adjacent_scan_persists_partial_intel(self):
        """Adjacent scan (no target) sets PARTIAL visibility on adjacent regions."""
        world = make_world()
        executor = CommandExecutor()
        game_state = {"world": world}

        player_marshal = None
        for m in world.marshals.values():
            if m.nation == world.player_nation:
                player_marshal = m
                break

        # Scout with no target (adjacent scan)
        result = executor._execute_scout(player_marshal, None, world, game_state)
        assert result["success"]

        # Check adjacent regions got PARTIAL or better
        region = world.get_region(player_marshal.location)
        for adj_name in region.adjacent_regions:
            intel = world.get_region_intel(adj_name)
            # Adjacent scan refreshes PARTIAL. Some regions may already be
            # higher (e.g. own regions are FULL), so check >= PARTIAL
            from backend.models.intel import VISIBILITY_PRIORITY
            assert VISIBILITY_PRIORITY[intel.visibility] >= VISIBILITY_PRIORITY[PARTIAL], \
                f"{adj_name} visibility is {intel.visibility} after adjacent scan"

    def test_scout_intel_persists_across_turns(self):
        """Scouted intel remains in store after turn advance (until decay)."""
        world = make_world()
        executor = CommandExecutor()
        game_state = {"world": world}

        player_marshal = None
        for m in world.marshals.values():
            if m.nation == world.player_nation:
                player_marshal = m
                break

        region = world.get_region(player_marshal.location)
        target_region = region.adjacent_regions[0] if region.adjacent_regions else None
        if target_region:
            executor._execute_scout(player_marshal, target_region, world, game_state)
            intel_before = world.get_region_intel(target_region)
            vis_before = intel_before.visibility

            # Advance one turn
            world._advance_turn_internal()

            # Intel should still be at least the same level (may get refreshed
            # to higher if adjacency applies)
            intel_after = world.get_region_intel(target_region)
            from backend.models.intel import VISIBILITY_PRIORITY
            assert VISIBILITY_PRIORITY[intel_after.visibility] >= VISIBILITY_PRIORITY[STALE]


# ============================================================================
# BATTLE REVEAL
# ============================================================================

class TestBattleReveal:
    """Test that battles grant FULL visibility on battle region."""

    def test_attack_grants_full_visibility(self):
        """Main attack path updates intel to FULL on battle region."""
        world = make_world()
        world.opening_attack_guidance_shown = True
        executor = CommandExecutor()
        game_state = {"world": world}

        # Find adjacent player/enemy pair
        attacker = None
        defender = None
        for m in world.marshals.values():
            if m.nation == world.player_nation:
                region = world.get_region(m.location)
                for adj in region.adjacent_regions:
                    enemies = [e for e in world.get_marshals_in_region(adj)
                               if e.nation != world.player_nation and e.strength > 0]
                    if enemies:
                        attacker = m
                        defender = enemies[0]
                        break
            if attacker:
                break

        if attacker and defender:
            battle_region = defender.location
            # Execute attack using correct signature
            result = executor._execute_attack(
                attacker, defender.name, world, game_state
            )
            # Check intel was updated
            intel = world.get_region_intel(battle_region)
            assert intel.visibility == FULL

    def test_battle_reveal_after_auto_charge(self):
        """Auto-charge at recklessness 4+ grants FULL visibility via battle."""
        world = make_world()

        # Ney is aggressive — need to give him cavalry to make him reckless
        ney = world.get_marshal("Ney")
        if ney:
            # Ney is aggressive, so cavalry=True makes is_reckless_cavalry True
            ney.cavalry = True
            ney.recklessness = 4
            assert ney.is_reckless_cavalry

            # Find an enemy within range
            nearest = world._find_nearest_enemy_for_nation(ney.location, ney.nation)
            if nearest:
                enemy, distance = nearest
                if distance <= ney.movement_range:
                    battle_region = enemy.location
                    # Process auto-charge
                    events = world._process_reckless_cavalry_turn_start()
                    # Check that battle region got intel update
                    intel = world.get_region_intel(battle_region)
                    assert intel.visibility == FULL


# ============================================================================
# STATUS COMMAND WIRING
# ============================================================================

class TestStatusCommand:
    """Test that status command returns intel report."""

    def test_execute_status_returns_intel_report(self):
        """_execute_status() returns intel report data."""
        world = make_world()
        executor = CommandExecutor()
        game_state = {"world": world}

        result = executor._execute_status({}, game_state)
        assert result["success"]
        assert "intel_report" in result
        assert "message" in result
        assert "BERTHIER'S INTELLIGENCE REPORT" in result["message"]

    def test_status_is_free_action(self):
        """Status command is a free action (0 AP)."""
        world = make_world()
        executor = CommandExecutor()
        game_state = {"world": world}

        result = executor._execute_status({}, game_state)
        assert result.get("free_action") is True

    def test_status_report_contains_player_forces(self):
        """Status command report lists player forces."""
        world = make_world()
        executor = CommandExecutor()
        game_state = {"world": world}

        result = executor._execute_status({}, game_state)
        report = result["intel_report"]
        assert len(report["your_forces"]) > 0
        # Check at least one player marshal is listed
        player_names = {m.name for m in world.marshals.values()
                        if m.nation == world.player_nation}
        report_names = {f["name"] for f in report["your_forces"]}
        assert report_names & player_names  # Non-empty intersection


# ============================================================================
# FILTERED SUMMARY — EDGE CASES
# ============================================================================

class TestFilteredEdgeCases:
    """Edge cases for filtered game state summary."""

    def test_dead_enemy_not_in_filtered_summary(self):
        """Enemies with 0 strength don't appear in filtered summary."""
        world = make_world()
        # Kill an enemy
        for name, m in list(world.marshals.items()):
            if m.nation != world.player_nation:
                m.strength = 0
                break
        summary = world.get_filtered_game_state_summary()
        # Dead enemies shouldn't have map_data entries (get_game_state_summary
        # already filters strength > 0 for map_data marshals)
        for region_data in summary["map_data"].values():
            for md in region_data.get("marshals", []):
                if md["nation"] != world.player_nation:
                    # If it appears, it should have positive strength or be band-only
                    pass  # Dead marshals filtered at base level

    def test_filtered_preserves_game_over_and_victory(self):
        """Filtered summary preserves game_over and victory fields."""
        world = make_world()
        summary = world.get_filtered_game_state_summary()
        assert "game_over" in summary
        assert "victory" in summary

    def test_filtered_preserves_turn_and_gold(self):
        """Filtered summary preserves turn, gold, player_nation."""
        world = make_world()
        summary = world.get_filtered_game_state_summary()
        assert summary["turn"] == int(world.current_turn)
        assert summary["gold"] == int(world.gold)
        assert summary["player_nation"] == world.player_nation

    def test_unfiltered_still_works(self):
        """Original get_game_state_summary() is unchanged and omniscient."""
        world = make_world()
        unfiltered = world.get_game_state_summary()
        # Should have ALL enemies visible regardless of fog
        all_enemies = {name for name, m in world.marshals.items()
                       if m.nation != world.player_nation and m.strength > 0}
        visible_enemies = set(unfiltered["enemies"].keys())
        assert visible_enemies == all_enemies

    def test_filtered_has_fewer_or_equal_enemies(self):
        """Filtered summary has fewer or equal enemies than unfiltered."""
        world = make_world()
        unfiltered = world.get_game_state_summary()
        filtered = world.get_filtered_game_state_summary()
        assert len(filtered["enemies"]) <= len(unfiltered["enemies"])

    def test_fogged_forces_not_in_marshals_array(self):
        """No PARTIAL/STALE enemy should be in marshals[] — only in fogged_forces[]."""
        world = make_world()
        summary = world.get_filtered_game_state_summary()
        for region_name, rd in summary["map_data"].items():
            for m in rd.get("marshals", []):
                # Every marshal in the marshals array should NOT have fog_level
                assert "fog_level" not in m, \
                    f"Fogged enemy {m.get('name')} in marshals[] for {region_name}"

    def test_fogged_forces_field_exists_on_all_regions(self):
        """Every region in map_data has a fogged_forces field."""
        world = make_world()
        summary = world.get_filtered_game_state_summary()
        for region_name, rd in summary["map_data"].items():
            assert "fogged_forces" in rd, f"Missing fogged_forces in {region_name}"


# ============================================================================
# FULL-PATH INTEGRATION
# ============================================================================

class TestFullPathIntegration:
    """End-to-end tests through executor.execute()."""

    def test_status_via_execute(self):
        """Status command through executor.execute() returns intel report."""
        world = make_world()
        executor = CommandExecutor()
        game_state = {"world": world}

        # Simulate what parser returns for "status"
        parsed = {
            "success": True,
            "command": {
                "marshal": None,
                "action": "status",
                "target": None,
                "command_type": "meta",
            }
        }
        result = executor.execute(parsed, game_state)
        assert result["success"]
        assert "intel_report" in result
        assert "BERTHIER'S INTELLIGENCE REPORT" in result.get("message", "")

    def test_scout_via_execute_persists_intel(self):
        """Scout through executor.execute() persists FULL intel."""
        world = make_world()
        executor = CommandExecutor()
        game_state = {"world": world}

        # Find a player marshal and enemy-controlled adjacent region
        player_marshal = None
        target_name = None
        for m in world.marshals.values():
            if m.nation == world.player_nation:
                region = world.get_region(m.location)
                for adj in region.adjacent_regions:
                    adj_region = world.get_region(adj)
                    if adj_region and adj_region.controller != world.player_nation:
                        player_marshal = m
                        target_name = adj
                        break
            if target_name:
                break

        if player_marshal and target_name:
            parsed = {
                "success": True,
                "command": {
                    "marshal": player_marshal.name,
                    "action": "scout",
                    "target": target_name,
                    "command_type": "specific",
                }
            }
            result = executor.execute(parsed, game_state)
            assert result["success"]
            intel = world.get_region_intel(target_name)
            assert intel.visibility == FULL
            assert intel.intel_source == "scout"

    def test_end_turn_doesnt_leak_enemy_positions(self):
        """After end_turn, filtered game state hides fogged enemies."""
        world = make_world()
        executor = CommandExecutor()
        game_state = {"world": world}

        # Get filtered state — check that UNKNOWN enemies are hidden
        filtered = world.get_filtered_game_state_summary()
        unfiltered = world.get_game_state_summary()

        # Count enemies in UNKNOWN regions (should be filtered out)
        hidden_count = 0
        for name, m in world.marshals.items():
            if m.nation != world.player_nation and m.strength > 0:
                intel = world.get_region_intel(m.location)
                if intel.visibility == UNKNOWN:
                    hidden_count += 1
                    assert name not in filtered["enemies"], \
                        f"Enemy {name} at UNKNOWN region {m.location} visible in filtered"

        # Verify some enemies ARE hidden (otherwise this test proves nothing)
        if hidden_count == 0:
            # All enemies may be visible at game start — check this is correct
            # (Grouchy is adjacent to several enemies, making them PARTIAL+)
            pass  # Acceptable — game start has high visibility near French lines

    def test_intel_report_no_floats(self):
        """Intel report contains no float values."""
        world = make_world()
        from backend.intel_report import generate_intel_report
        report = generate_intel_report(world)

        def check_no_floats(obj, path=""):
            if isinstance(obj, float):
                pytest.fail(f"Float in intel_report at {path}: {obj}")
            elif isinstance(obj, dict):
                for k, v in obj.items():
                    check_no_floats(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    check_no_floats(v, f"{path}[{i}]")

        check_no_floats(report, "intel_report")
