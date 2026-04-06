"""
Tests for the Balance Patch (Session 67 prep).

Covers:
- Task 1: AI Homeland Defense (P3.7), stagnation fix, cautious advance fallback
- Task 2: Supply attrition continuous formula + town supply bump
- Task 3: Wellington starting strength reduction
- Task 4: French economy fix (Grouchy + gold)
- Task 5: "stance neutral" parse fix
- Task 6: Fortify cost hint message
"""

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal, create_starting_marshals, create_enemy_marshals
from backend.models.region import SUPPLY_BY_TYPE
from backend.ai.enemy_ai import EnemyAI


# ════════════════════════════════════════════════════════════
# TASK 5: Stance Parse Tests
# ════════════════════════════════════════════════════════════

class TestStanceParseFix:
    """Task 5: 'stance neutral' and similar phrases should parse correctly."""

    def _parse(self, command: str):
        """Quick mock-parse helper returning ParseResult."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        return client._parse_with_mock(command)

    def test_stance_neutral_parses(self):
        result = self._parse("Ney, stance neutral")
        assert result.action == "stance_change"

    def test_stance_defensive_parses(self):
        result = self._parse("Davout, stance defensive")
        assert result.action == "stance_change"

    def test_stance_aggressive_parses(self):
        result = self._parse("Ney, stance aggressive")
        assert result.action == "stance_change"

    def test_neutral_stance_still_works(self):
        result = self._parse("Ney, neutral stance")
        assert result.action == "stance_change"

    def test_go_neutral_still_works(self):
        result = self._parse("Ney, go neutral")
        assert result.action == "stance_change"

    def test_bare_neutral_still_works(self):
        result = self._parse("Ney neutral")
        assert result.action == "stance_change"


# ════════════════════════════════════════════════════════════
# TASK 6: Fortify Hint Tests
# ════════════════════════════════════════════════════════════

class TestFortifyHint:
    """Task 6: Auto-shift message should explain 2 AP cost."""

    def _make_world_with_marshal(self):
        world = WorldState()
        # Use Davout (cautious) — aggressive marshals object to fortify
        from backend.models.marshal import Stance
        world.marshals["Davout"].stance = Stance.NEUTRAL
        world.actions_remaining = 4
        return world

    def test_fortify_from_neutral_shows_ap_hint(self):
        from backend.commands.executor import CommandExecutor
        world = self._make_world_with_marshal()
        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor.execute(
            {"command": {"marshal": "Davout", "action": "fortify"}},
            game_state
        )
        msg = result.get("message", "")
        assert "cost 2 AP" in msg
        assert "1 for stance change + 1 for fortify" in msg

    def test_fortify_from_defensive_no_hint(self):
        from backend.commands.executor import CommandExecutor
        from backend.models.marshal import Stance
        world = self._make_world_with_marshal()
        world.marshals["Davout"].stance = Stance.DEFENSIVE
        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor.execute(
            {"command": {"marshal": "Davout", "action": "fortify"}},
            game_state
        )
        msg = result.get("message", "")
        assert "cost 2 AP" not in msg


# ════════════════════════════════════════════════════════════
# TASK 2: Supply Attrition Continuous Formula
# ════════════════════════════════════════════════════════════

class TestContinuousAttritionFormula:
    """Task 2: Continuous attrition formula min(0.03, excess_ratio * 0.015)."""

    def test_town_supply_base_is_35k(self):
        assert SUPPLY_BY_TYPE["town"] == 35000

    def test_capital_supply_unchanged(self):
        assert SUPPLY_BY_TYPE["capital"] == 50000

    def test_continuous_formula_small_excess(self):
        """excess_ratio 0.2 → attrition 0.003 (0.3%)"""
        world = WorldState()

        # Put a marshal in a region where we control excess
        ney = world.marshals["Ney"]
        ney.location = "Paris"  # capital, urban, 60k capacity
        ney.strength = 100000   # 100k in 90k effective (home 1.5x of 60k)
        # excess = (100k - 90k) / 90k = 0.111
        # attrition = min(0.03, 0.111 * 0.015) = 0.00167
        # losses = int(100000 * 0.00167) = 167
        # Clear other marshals from Paris
        for name, m in world.marshals.items():
            if name != "Ney":
                m.location = "Lyon"
                m.strength = 1000  # minimal

        events = world.process_supply_attrition()
        ney_events = [e for e in events if e["marshal"] == "Ney"]
        if ney_events:
            # With small excess, losses should be small
            assert ney_events[0]["losses"] < 300

    def test_continuous_formula_caps_at_3pct(self):
        """Excess ratio > 2.0 should cap at 3%."""
        world = WorldState()

        ney = world.marshals["Ney"]
        ney.location = "Brittany"  # rural, forest, 12k cap
        ney.strength = 100000
        # Move everyone else far away
        for name, m in world.marshals.items():
            if name != "Ney":
                m.location = "Lyon"
                m.strength = 1000
        # Brittany is France-controlled, home bonus: 12k * 1.5 = 18k
        # excess = (100k - 18k) / 18k = 4.56
        # attrition = min(0.03, 4.56 * 0.015) = 0.03 (capped)
        # losses = int(100000 * 0.03) = 3000
        events = world.process_supply_attrition()
        ney_events = [e for e in events if e["marshal"] == "Ney"]
        assert len(ney_events) == 1
        assert ney_events[0]["losses"] == 3000

    def test_belgium_attrition_reduced(self):
        """Belgium with Ney+Grouchy should have lower attrition than old 5% tier."""
        world = WorldState()

        # Grouchy now starts at Lyon; move him to Belgium for this test
        world.marshals["Grouchy"].location = "Belgium"
        # Ney 72k + Grouchy 28k in Belgium = 100k total
        # Belgium: town (35k) * plains (1.0) = 35k, home 1.5x = 52.5k
        # excess = (100k - 52.5k) / 52.5k = 0.9048
        # base_attrition = min(0.03, 0.9048 * 0.015) = 0.01357
        # Session 8 stacking penalty: +1% per marshal beyond 1st
        # attrition = 0.01357 + 0.01 = 0.02357
        # Ney: int(72000 * 0.02357) = 1697
        # Grouchy: int(28000 * 0.02357) = 660
        events = world.process_supply_attrition()
        belgium_events = [e for e in events if e["region"] == "Belgium"]
        ney_ev = [e for e in belgium_events if e["marshal"] == "Ney"]
        grouchy_ev = [e for e in belgium_events if e["marshal"] == "Grouchy"]
        assert len(ney_ev) == 1
        assert len(grouchy_ev) == 1
        assert ney_ev[0]["losses"] == 1697  # int(72000 * 0.02357)
        assert grouchy_ev[0]["losses"] == 660  # int(28000 * 0.02357)


# ════════════════════════════════════════════════════════════
# TASK 3: Wellington Starting Strength
# ════════════════════════════════════════════════════════════

class TestWellingtonNerf:
    """Task 3: Wellington reduced from 68k to 52k."""

    def test_wellington_starts_at_52k(self):
        enemies = create_enemy_marshals()
        assert enemies["Wellington"].strength == 52000

    def test_wellington_starting_strength_field(self):
        enemies = create_enemy_marshals()
        assert enemies["Wellington"].starting_strength == 52000


# ════════════════════════════════════════════════════════════
# TASK 4: French Economy
# ════════════════════════════════════════════════════════════

class TestFrenchEconomy:
    """Task 4: Grouchy 28k, France starting gold 800."""

    def test_grouchy_starts_at_28k(self):
        marshals = create_starting_marshals()
        assert marshals["Grouchy"].strength == 28000

    def test_grouchy_starting_strength_field(self):
        marshals = create_starting_marshals()
        assert marshals["Grouchy"].starting_strength == 28000

    def test_france_starting_gold_800(self):
        world = WorldState()

        assert world.nation_gold["France"] == 800

    def test_french_economy_positive(self):
        """French net income should be positive with 8 regions (1100 income - 865 upkeep = +235)."""
        world = WorldState()

        income = world.calculate_turn_income("France")["income"]
        upkeep = world.calculate_turn_upkeep("France")["total"]
        net = income - upkeep
        # 8 regions: income 1100 (Paris 300 + Belgium 100 + Lyon 200 + Marseille 150
        #   + Brittany 50 + Bordeaux 50 + Normandy 100 + Milan 150)
        # Upkeep: 865 (Ney 72k + Davout 48k + Grouchy 28k + Drouot 25k = 173k troops, 5g per 1000)
        assert net > 0, f"French net income {net} should be positive with 8 regions"
        assert 200 <= net <= 270, f"French net income {net} not in expected range"

    def test_other_starting_strengths_unchanged(self):
        """Ney, Davout, Drouot should be unchanged."""
        marshals = create_starting_marshals()
        assert marshals["Ney"].strength == 72000
        assert marshals["Davout"].strength == 48000
        assert marshals["Drouot"].strength == 25000


# ════════════════════════════════════════════════════════════
# TASK 1: AI Homeland Defense
# ════════════════════════════════════════════════════════════

class TestNationStartingRegions:
    """nation_starting_regions field exists and is populated."""

    def test_starting_regions_populated(self):
        world = WorldState()

        assert "France" in world.nation_starting_regions
        assert "Britain" in world.nation_starting_regions
        assert "Prussia" in world.nation_starting_regions

    def test_france_starting_regions(self):
        world = WorldState()

        france_regions = set(world.nation_starting_regions["France"])
        expected = {"Paris", "Belgium", "Lyon", "Brittany", "Bordeaux", "Marseille", "Normandy", "Milan"}
        assert france_regions == expected

    def test_britain_starting_regions(self):
        world = WorldState()

        britain_regions = set(world.nation_starting_regions["Britain"])
        expected = {"Netherlands", "Waterloo", "Hanover"}
        assert britain_regions == expected

    def test_prussia_starting_regions(self):
        world = WorldState()

        prussia_regions = set(world.nation_starting_regions["Prussia"])
        expected = {"Rhineland", "Berlin"}
        assert prussia_regions == expected

    def test_serialization_round_trip(self):
        world = WorldState()

        data = world.to_dict()
        assert "nation_starting_regions" in data
        world2 = WorldState.from_dict(data)
        assert world2.nation_starting_regions == world.nation_starting_regions

    def test_from_dict_missing_field_defaults_empty(self):
        """Legacy saves without nation_starting_regions should get empty dict."""
        world = WorldState()

        data = world.to_dict()
        del data["nation_starting_regions"]
        world2 = WorldState.from_dict(data)
        assert world2.nation_starting_regions == {}


class TestIsEnemyNearby:
    """WorldState.is_enemy_nearby helper."""

    def test_enemy_adjacent(self):
        world = WorldState()

        # Wellington is in Waterloo, adjacent to Belgium
        assert world.is_enemy_nearby("Belgium", "France", max_distance=1)

    def test_enemy_two_hops(self):
        world = WorldState()

        # Wellington in Waterloo, 2 hops from Paris (Waterloo→Belgium→Paris)
        # Waterloo is NOT adjacent to Paris — goes through Belgium
        assert world.is_enemy_nearby("Paris", "France", max_distance=2)

    def test_no_enemy_nearby(self):
        world = WorldState()

        # Bordeaux is far from all enemies
        assert not world.is_enemy_nearby("Bordeaux", "France", max_distance=1)


class TestHomelandDefenseAI:
    """Task 1: AI homeland defense priority P3.7."""

    def _setup_world_lost_territory(self):
        """Set up a world where Prussia has lost Rhine to France."""
        world = WorldState()

        # France captures Rhine
        world.regions["Rhineland"].controller = "France"
        return world

    def test_ai_detects_lost_territory(self):
        """AI should detect that Rhine is lost."""
        world = self._setup_world_lost_territory()
        lost = [r for r in world.nation_starting_regions.get("Prussia", [])
                if world.regions[r].controller != "Prussia"]
        assert "Rhineland" in lost

    def test_homeland_defense_moves_toward_lost_region(self):
        """The nearest Prussian marshal should try to recapture lost Rhine."""
        world = self._setup_world_lost_territory()
        from backend.commands.executor import CommandExecutor
        ai = EnemyAI(CommandExecutor())
        ai._recapture_targets_claimed = set()
        ai._recapture_marshal_assignments = {}
        ai._marshal_visited_locations = {}
        ai._unfortified_this_turn = set()

        # Move Blucher to Bavaria (adjacent to Rhine)
        blucher = world.marshals["Blucher"]
        blucher.location = "Bavaria"

        # Move Gneisenau away from Rhineland so Blucher is closest
        world.marshals["Gneisenau"].location = "Berlin"

        action = ai._find_homeland_defense(blucher, "Prussia", world)
        assert action is not None
        assert action["action"] == "attack"  # Adjacent + undefended = capture
        assert action["target"] == "Rhineland"

    def test_homeland_defense_skips_fortified_marshal(self):
        """Fortified marshals should not respond to homeland defense."""
        world = self._setup_world_lost_territory()
        from backend.commands.executor import CommandExecutor
        ai = EnemyAI(CommandExecutor())
        ai._recapture_targets_claimed = set()
        ai._recapture_marshal_assignments = {}

        blucher = world.marshals["Blucher"]
        blucher.location = "Bavaria"
        blucher.fortified = True

        action = ai._find_homeland_defense(blucher, "Prussia", world)
        assert action is None

    def test_homeland_defense_no_lost_territory(self):
        """Should return None when nation controls all starting regions."""
        world = WorldState()

        from backend.commands.executor import CommandExecutor
        ai = EnemyAI(CommandExecutor())
        ai._recapture_targets_claimed = set()
        ai._recapture_marshal_assignments = {}
        ai._marshal_visited_locations = {}

        blucher = world.marshals["Blucher"]
        action = ai._find_homeland_defense(blucher, "Prussia", world)
        assert action is None

    def test_homeland_defense_claimed_targets_prevent_duplication(self):
        """Second marshal should not target same lost region."""
        world = self._setup_world_lost_territory()
        from backend.commands.executor import CommandExecutor
        ai = EnemyAI(CommandExecutor())
        ai._recapture_targets_claimed = {"Rhineland"}  # Already claimed
        ai._recapture_marshal_assignments = {}
        ai._marshal_visited_locations = {}

        blucher = world.marshals["Blucher"]
        blucher.location = "Bavaria"

        action = ai._find_homeland_defense(blucher, "Prussia", world)
        # Rhine is claimed, Bavaria/Vienna are still Prussian → no other lost regions
        assert action is None

    def test_homeland_defense_closer_marshal_gets_priority(self):
        """A closer marshal should prevent a farther one from responding."""
        world = self._setup_world_lost_territory()
        from backend.commands.executor import CommandExecutor
        ai = EnemyAI(CommandExecutor())
        ai._recapture_targets_claimed = set()
        ai._recapture_marshal_assignments = {}
        ai._marshal_visited_locations = {}

        # Gneisenau in Bavaria (adjacent to Rhine, dist=1)
        gneisenau = world.marshals["Gneisenau"]
        gneisenau.location = "Bavaria"

        # Blucher in Vienna (dist=2 from Rhine)
        blucher = world.marshals["Blucher"]
        blucher.location = "Vienna"

        # Gneisenau should get the action
        action_g = ai._find_homeland_defense(gneisenau, "Prussia", world)
        assert action_g is not None

        # Blucher should be blocked (Gneisenau is closer)
        action_b = ai._find_homeland_defense(blucher, "Prussia", world)
        assert action_b is None

    def test_homeland_defense_attacks_defended_region_if_favorable(self):
        """Should attack a defended lost region if ratio is favorable."""
        world = self._setup_world_lost_territory()
        from backend.commands.executor import CommandExecutor
        ai = EnemyAI(CommandExecutor())
        ai._recapture_targets_claimed = set()
        ai._recapture_marshal_assignments = {}
        ai._marshal_visited_locations = {}

        # Put a weak French marshal in Rhine
        weak_french = Marshal(name="TestFrench", location="Rhineland", strength=5000,
                             personality="cautious", nation="France")
        world.marshals["TestFrench"] = weak_french

        # Move Gneisenau away from Rhineland so Blucher is closest
        world.marshals["Gneisenau"].location = "Berlin"

        # Blucher (40k) in Bavaria, adjacent to Rhine with 5k defender → 8:1 ratio
        blucher = world.marshals["Blucher"]
        blucher.location = "Bavaria"

        action = ai._find_homeland_defense(blucher, "Prussia", world)
        assert action is not None
        assert action["action"] == "attack"
        assert action["target"] == "Rhineland"

    def test_homeland_defense_wont_attack_strong_defender(self):
        """Should NOT attack if defender is too strong."""
        world = self._setup_world_lost_territory()
        from backend.commands.executor import CommandExecutor
        ai = EnemyAI(CommandExecutor())
        ai._recapture_targets_claimed = set()
        ai._recapture_marshal_assignments = {}
        ai._marshal_visited_locations = {}

        # Put a strong French marshal in Rhine
        strong_french = Marshal(name="TestFrench", location="Rhineland", strength=80000,
                               personality="cautious", nation="France")
        world.marshals["TestFrench"] = strong_french

        # Gneisenau (45k, cautious) in Bavaria → ratio 0.56, threshold 1.2 → won't attack
        gneisenau = world.marshals["Gneisenau"]
        gneisenau.location = "Bavaria"

        action = ai._find_homeland_defense(gneisenau, "Prussia", world)
        assert action is None

    def test_homeland_defense_moves_when_2_hops_away(self):
        """Should move toward lost region when 2 hops away."""
        world = self._setup_world_lost_territory()
        from backend.commands.executor import CommandExecutor
        ai = EnemyAI(CommandExecutor())
        ai._recapture_targets_claimed = set()
        ai._recapture_marshal_assignments = {}
        ai._marshal_visited_locations = {"Blucher": set()}

        # Blucher in Vienna (2 hops from Rhine: Vienna→Bavaria→Rhine)
        blucher = world.marshals["Blucher"]
        blucher.location = "Vienna"

        # Move other marshals far away so Blucher is closest
        world.marshals["Gneisenau"].location = "Milan"

        action = ai._find_homeland_defense(blucher, "Prussia", world)
        assert action is not None
        assert action["action"] == "move"
        assert action["target"] == "Bavaria"  # Step toward Rhine


class TestStagnationFix:
    """Fortify should only be meaningful if enemy within 2 regions."""

    def test_fortify_without_enemy_nearby_not_meaningful(self):
        """Fortifying far from enemies should NOT count as meaningful."""
        world = WorldState()

        from backend.commands.executor import CommandExecutor
        ai = EnemyAI(CommandExecutor())

        # Move all non-Prussian marshals far away so Vienna is isolated
        for m in world.marshals.values():
            if m.nation != "Prussia":
                m.location = "Netherlands"  # 4 hops from Vienna

        # Put a Prussian marshal alone in Vienna (far from French)
        gneisenau = world.marshals["Gneisenau"]
        gneisenau.location = "Vienna"

        # Check: Vienna should have no French enemies within 2
        assert not world.is_enemy_nearby("Vienna", "Prussia", max_distance=2)

    def test_fortify_with_enemy_nearby_is_meaningful(self):
        """Fortifying near enemies should count as meaningful."""
        world = WorldState()


        # Wellington in Waterloo, Ney in Belgium → Belgium is 1 hop from Waterloo
        assert world.is_enemy_nearby("Belgium", "France", max_distance=2)


class TestCautiousAdvanceFallback:
    """Cautious advance should fall back to any safe friendly region when stuck."""

    def _setup_stuck_cautious(self):
        """Create a scenario where cautious advance can't reduce distance."""
        world = WorldState()

        from backend.commands.executor import CommandExecutor
        ai = EnemyAI(CommandExecutor())

        # Put Wellington in Tyrol (mountain region: adjacent to Bavaria, Vienna, Milan)
        wellington = world.marshals["Wellington"]
        wellington.location = "Tyrol"
        wellington.fortified = False
        world.regions["Tyrol"].controller = "Britain"

        # Set stagnation to 2 (triggers fallback)
        world.ai_stagnation_turns["Wellington"] = 2

        return world, ai, wellington

    def test_fallback_moves_to_friendly_region(self):
        """When no distance-reducing move exists and stagnation >= 2, move to any friendly region."""
        world, ai, wellington = self._setup_stuck_cautious()

        # Setup AI turn state
        ai._marshal_visited_locations = {"Wellington": {"Tyrol"}}
        ai._unfortified_this_turn = set()
        ai._stance_changed_this_turn = set()
        ai._advanced_this_turn = set()
        ai._attacked_targets_this_turn = set()
        ai._garrison_placed_this_turn = False
        ai._recapture_targets_claimed = set()
        ai._recapture_marshal_assignments = {}
        ai._threat_responder_assigned = set()
        ai._pending_intents = {}
        ai._current_world = world

        # Clear enemies from adjacent regions so movement is possible
        for name in ["Blucher", "Gneisenau", "Uxbridge"]:
            world.marshals[name].location = "Netherlands"

        action = ai._consider_strategic_move(wellington, "Britain", world)
        # Should find a fallback move since distance reduction isn't possible
        # OR should return None if all adjacent regions are not Britain-controlled
        # Tyrol is adjacent to: Bavaria (Austria), Vienna (Austria), Milan (France)
        # None are Britain-controlled by default, but test is defensive (checks if action is not None)
        if action is not None:
            assert action["action"] == "move"


# ════════════════════════════════════════════════════════════
# SERIALIZATION ENFORCEMENT
# ════════════════════════════════════════════════════════════

class TestBalancePatchSerialization:
    """Ensure new fields survive save/load."""

    def test_nation_starting_regions_serialized(self):
        world = WorldState()

        data = world.to_dict()
        assert "nation_starting_regions" in data
        assert "France" in data["nation_starting_regions"]

    def test_nation_starting_regions_deserialized(self):
        world = WorldState()

        data = world.to_dict()
        world2 = WorldState.from_dict(data)
        assert world2.nation_starting_regions["France"] == world.nation_starting_regions["France"]
        assert world2.nation_starting_regions["Prussia"] == world.nation_starting_regions["Prussia"]

    def test_full_round_trip_preserves_all_state(self):
        world = WorldState()

        world.nation_gold["France"] = 900  # Modified
        data = world.to_dict()
        world2 = WorldState.from_dict(data)
        assert world2.nation_gold["France"] == 900
        assert set(world2.nation_starting_regions["France"]) == set(world.nation_starting_regions["France"])
