"""
Tests for Phase 6.2.H: Supply Depot Forward Logistics.

Covers:
- Depot projection halves movement attrition (destination + adjacent)
- Non-interaction with retreat, friendly stable territory, harassment, supply attrition
- AI depot placement preference for border regions
"""


from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.ai.enemy_ai import EnemyAI


# ============================================================================
# HELPERS
# ============================================================================

def fresh_world() -> WorldState:
    """Create a fresh WorldState for testing."""
    return WorldState(player_nation="France")


def make_executor():
    """Create an executor with combat resolver."""
    return CommandExecutor()


def make_game_state(world):
    """Wrap world in game_state dict."""
    return {"world": world}


def add_depot(region, damaged=False):
    """Add a supply depot building to a region."""
    region.buildings.append({"type": "supply_depot", "damaged": damaged})


# ============================================================================
# CORE PROJECTION TESTS
# ============================================================================

class TestDepotProjection:
    """Test that depot forward logistics halves movement attrition."""

    def test_adjacent_depot_halves_attrition(self):
        """Marshal moving into region adjacent to friendly depot gets 0.5x attrition."""
        world = fresh_world()
        executor = make_executor()
        ney = world.get_marshal("Ney")
        ney.strength = 20000
        ney.location = "Belgium"

        # Belgium is adjacent to Waterloo. Put a depot in Belgium (French controlled).
        belgium = world.get_region("Belgium")
        add_depot(belgium)

        # Waterloo is enemy territory (adjacent to Belgium).
        waterloo = world.get_region("Waterloo")
        waterloo.controller = "Britain"

        result = executor._calculate_movement_attrition(ney, "Waterloo", world)

        # Without depot: base 1% * hills 1.2x = 1.2% -> 240
        # With depot:    1.2% * 0.5 = 0.6% -> 120
        assert result["march_losses"] == 120
        assert result["depot_bonus"] is True

    def test_no_depot_normal_attrition(self):
        """Without depot, normal attrition applies."""
        world = fresh_world()
        executor = make_executor()
        ney = world.get_marshal("Ney")
        ney.strength = 20000
        ney.location = "Belgium"

        waterloo = world.get_region("Waterloo")
        waterloo.controller = "Britain"

        result = executor._calculate_movement_attrition(ney, "Waterloo", world)

        # base 1% * hills 1.2x = 1.2% -> 240
        assert result["march_losses"] == 240
        assert result["depot_bonus"] is False

    def test_depot_in_destination_triggers_bonus(self):
        """Depot in the destination region itself also triggers the bonus."""
        world = fresh_world()
        executor = make_executor()
        ney = world.get_marshal("Ney")
        ney.strength = 20000
        ney.location = "Paris"

        # Belgium is French-controlled with a depot
        belgium = world.get_region("Belgium")
        belgium.controller = "France"
        belgium.stability = 50  # Not stable enough for exemption
        add_depot(belgium)

        result = executor._calculate_movement_attrition(ney, "Belgium", world)

        # base 1% * plains 1.0x = 1.0% -> 200 without depot
        # With depot: 0.5% -> 100
        assert result["march_losses"] == 100
        assert result["depot_bonus"] is True

    def test_damaged_depot_no_projection(self):
        """Damaged depot does not provide the forward logistics bonus."""
        world = fresh_world()
        executor = make_executor()
        ney = world.get_marshal("Ney")
        ney.strength = 20000
        ney.location = "Belgium"

        # Belgium is adjacent to Waterloo, but depot is damaged.
        belgium = world.get_region("Belgium")
        add_depot(belgium, damaged=True)

        waterloo = world.get_region("Waterloo")
        waterloo.controller = "Britain"

        result = executor._calculate_movement_attrition(ney, "Waterloo", world)

        # No depot bonus — damaged
        assert result["march_losses"] == 240
        assert result["depot_bonus"] is False

    def test_enemy_depot_no_projection(self):
        """Enemy-controlled depot does not help the marshal."""
        world = fresh_world()
        executor = make_executor()
        ney = world.get_marshal("Ney")
        ney.strength = 20000
        ney.location = "Belgium"

        # Netherlands is British and adjacent to Waterloo — enemy depot
        netherlands = world.get_region("Netherlands")
        add_depot(netherlands)

        waterloo = world.get_region("Waterloo")
        waterloo.controller = "Britain"

        result = executor._calculate_movement_attrition(ney, "Waterloo", world)

        assert result["march_losses"] == 240
        assert result["depot_bonus"] is False

    def test_multiple_depots_no_stacking(self):
        """Multiple adjacent depots give the same 0.5x as one — no stacking."""
        world = fresh_world()
        executor = make_executor()
        ney = world.get_marshal("Ney")
        ney.strength = 20000
        ney.location = "Paris"

        # Lyon is adjacent to both Paris and Bordeaux (both French).
        # Put depots in both Paris and Bordeaux.
        paris = world.get_region("Paris")
        add_depot(paris)
        bordeaux = world.get_region("Bordeaux")
        add_depot(bordeaux)

        lyon = world.get_region("Lyon")
        lyon.controller = "Britain"

        result = executor._calculate_movement_attrition(ney, "Lyon", world)

        # Lyon terrain = hills (1.2x). Still 0.5x, not 0.25x
        # base 1% * 1.2x = 1.2%, with depot 0.5x = 0.6% -> 120
        assert result["march_losses"] == 120
        assert result["depot_bonus"] is True

    def test_depot_projection_into_enemy_territory(self):
        """Core use case: depot in friendly territory projects into adjacent enemy region."""
        world = fresh_world()
        executor = make_executor()
        ney = world.get_marshal("Ney")
        ney.strength = 20000
        ney.location = "Paris"

        # Depot in Lyon (French). Moving into Rhine (enemy).
        # Lyon is adjacent to Rhine.
        lyon = world.get_region("Lyon")
        add_depot(lyon)

        rhine = world.get_region("Rhineland")
        rhine.controller = "Prussia"

        result = executor._calculate_movement_attrition(ney, "Rhineland", world)

        # Rhine: river_crossing terrain, movement_cost 1.5x
        # base 1% * 1.5 = 1.5% -> 300 without depot
        # With depot: 0.75% -> 150
        assert result["march_losses"] == 150
        assert result["depot_bonus"] is True

    def test_depot_projection_into_neutral_territory(self):
        """Depot projection works into neutral (no controller) regions."""
        world = fresh_world()
        executor = make_executor()
        ney = world.get_marshal("Ney")
        ney.strength = 20000
        ney.location = "Belgium"

        # Belgium is adjacent to Waterloo. Depot in Belgium (French).
        belgium = world.get_region("Belgium")
        add_depot(belgium)

        # Make Waterloo neutral
        waterloo = world.get_region("Waterloo")
        waterloo.controller = None

        result = executor._calculate_movement_attrition(ney, "Waterloo", world)

        # hills 1.2x, base 1%, with depot 0.5x -> 0.6% -> 120
        assert result["march_losses"] == 120
        assert result["depot_bonus"] is True


# ============================================================================
# NON-INTERACTION TESTS
# ============================================================================

class TestDepotNonInteraction:
    """Test that depot projection does NOT affect retreat, friendly stable, harassment."""

    def test_retreat_ignores_depot_projection(self):
        """Retreat uses its own 0.5x rate; depot projection not applied on top."""
        world = fresh_world()
        executor = make_executor()
        ney = world.get_marshal("Ney")
        ney.strength = 20000
        ney.location = "Waterloo"

        paris = world.get_region("Paris")
        add_depot(paris)

        # Retreat into Belgium (adjacent to Paris depot)
        belgium = world.get_region("Belgium")
        belgium.controller = "France"
        belgium.stability = 50  # Not stable, so attrition applies

        result = executor._calculate_movement_attrition(ney, "Belgium", world, is_retreat=True)

        # Retreat: base 0.5% * plains 1.0x = 0.5% -> 100 (no depot halving)
        assert result["march_losses"] == 100
        assert result["depot_bonus"] is False

    def test_friendly_stable_territory_still_exempt(self):
        """Own region with stability >= 76 still has 0 attrition regardless of depot."""
        world = fresh_world()
        executor = make_executor()
        ney = world.get_marshal("Ney")
        ney.strength = 20000
        ney.location = "Waterloo"

        # Belgium: French, stable
        belgium = world.get_region("Belgium")
        belgium.controller = "France"
        belgium.stability = 80

        # Depot exists in Paris (adjacent to Belgium)
        paris = world.get_region("Paris")
        add_depot(paris)

        result = executor._calculate_movement_attrition(ney, "Belgium", world)

        # Friendly stable = 0 losses. Depot doesn't matter.
        assert result["march_losses"] == 0
        assert result["depot_bonus"] is False

    def test_harassment_not_affected_by_depot(self):
        """Enemy fortification harassment (4%) is not reduced by depot projection."""
        world = fresh_world()
        executor = make_executor()
        ney = world.get_marshal("Ney")
        ney.strength = 20000
        ney.location = "Paris"

        # Belgium: enemy with fortification
        belgium = world.get_region("Belgium")
        belgium.controller = "Britain"
        belgium.buildings.append({"type": "fortification", "damaged": False})

        # Depot in Paris (adjacent to Belgium)
        paris = world.get_region("Paris")
        add_depot(paris)

        result = executor._calculate_movement_attrition(ney, "Belgium", world)

        # March losses halved by depot: 1% * 0.5 = 0.5% -> 100
        # Harassment NOT halved: 4% -> 800
        assert result["march_losses"] == 100
        assert result["harassment_losses"] == 800
        assert result["depot_bonus"] is True

    def test_terrain_still_matters_with_depot(self):
        """Mountains (2.0x) with depot: attrition halved but still > plains without depot."""
        world = fresh_world()
        executor = make_executor()
        ney = world.get_marshal("Ney")
        ney.strength = 20000
        ney.location = "Milan"

        # Tyrol: mountains terrain (2.0x), adjacent to Milan
        tyrol = world.get_region("Tyrol")
        tyrol.controller = "Britain"

        # Depot in Milan (adjacent to Tyrol)
        milan = world.get_region("Milan")
        add_depot(milan)

        result = executor._calculate_movement_attrition(ney, "Tyrol", world)

        # Mountains: base 1% * 2.0x = 2.0%, with depot 0.5x = 1.0% -> 200
        assert result["march_losses"] == 200
        assert result["depot_bonus"] is True

        # Compare: plains without depot = 1% -> 200 (same! mountains+depot = plains)
        # Without depot, mountains = 2% -> 400 (twice as much)

    def test_large_army_size_penalty_still_applies(self):
        """50k army with depot: size penalty calculated normally, then total halved."""
        world = fresh_world()
        executor = make_executor()
        ney = world.get_marshal("Ney")
        ney.strength = 50000
        ney.location = "Belgium"

        # Belgium is adjacent to Waterloo. Put depot in Belgium.
        belgium = world.get_region("Belgium")
        add_depot(belgium)

        waterloo = world.get_region("Waterloo")
        waterloo.controller = "Britain"

        result_with_depot = executor._calculate_movement_attrition(ney, "Waterloo", world)

        # Reset strength for control test
        ney.strength = 50000
        belgium.buildings.clear()
        result_without = executor._calculate_movement_attrition(ney, "Waterloo", world)

        # Match production code's step-by-step floating point arithmetic:
        # rate = 0.01 + min(0.02, max(0, (50000 - 20000) / 500000))  # 0.03
        # rate *= 1.2  (hills terrain)
        size_penalty = min(0.02, max(0, (50000 - 20000) / 500000))
        rate = 0.01 + size_penalty
        rate *= 1.2  # hills movement_cost
        expected_without = int(50000 * rate)
        expected_with = int(50000 * rate * 0.5)
        assert result_without["march_losses"] == expected_without
        assert result_with_depot["march_losses"] == expected_with
        assert result_with_depot["march_losses"] < result_without["march_losses"]
        assert result_with_depot["depot_bonus"] is True


# ============================================================================
# AI DEPOT PLACEMENT TESTS
# ============================================================================

class TestAIDepotPlacement:
    """Test AI prefers border regions when placing supply depots."""

    def test_ai_prefers_border_region_for_depot(self):
        """Within same tier, AI picks region bordering enemy over interior."""
        world = fresh_world()
        ai = EnemyAI(make_executor())

        # Give Prussia a cluster of regions. We want two city-tier candidates:
        # Milan (city, interior) vs Marseille (city, border — adj to Bordeaux=France).
        # Surround Milan with all-Prussia neighbors so it's interior.
        # Leave Marseille adjacent to Bordeaux (France) so it borders enemy.
        for name in ["Lyon", "Bavaria", "Rhineland", "Milan", "Marseille",
                      "Bohemia", "Tyrol", "Vienna"]:
            region = world.get_region(name)
            region.controller = "Prussia"
            region.stability = 80

        # Give existing depots to higher-tier regions so city tier is tested:
        # Berlin (capital), Vienna (capital), Lyon (major_city)
        add_depot(world.get_region("Berlin"))
        add_depot(world.get_region("Vienna"))
        add_depot(world.get_region("Lyon"))

        # Milan adj: Lyon(Prussia), Marseille(Prussia), Tyrol(Prussia), Vienna(Prussia) → interior
        # Marseille adj: Lyon(Prussia), Bordeaux(France), Milan(Prussia) → borders France
        # Both are city tier. Marseille should be preferred (borders enemy).
        result = ai._find_best_depot_region("Prussia", world)
        assert result == "Marseille"

    def test_ai_falls_back_when_no_border(self):
        """If no candidates border enemies, AI still picks by type priority."""
        world = fresh_world()
        ai = EnemyAI(make_executor())

        # Give Prussia everything so no borders exist.
        for name in world.regions:
            region = world.get_region(name)
            region.controller = "Prussia"
            region.stability = 80

        # No enemy borders. Should pick capital first (Paris is the only capital).
        result = ai._find_best_depot_region("Prussia", world)
        assert result == "Paris"

    def test_ai_higher_tier_beats_border_lower_tier(self):
        """Higher priority tier (major_city) wins over border region in lower tier (city)."""
        world = fresh_world()
        ai = EnemyAI(make_executor())

        # Prussia controls Vienna (major_city, interior) and Milan (city, border).
        vienna = world.get_region("Vienna")
        vienna.controller = "Prussia"
        vienna.stability = 80

        bavaria = world.get_region("Bavaria")
        bavaria.controller = "Prussia"
        bavaria.stability = 80

        milan = world.get_region("Milan")
        milan.controller = "Prussia"
        milan.stability = 80
        # Milan adj: Lyon (France), Marseille (France), Tyrol (Prussia), Vienna (Prussia) → borders enemy

        # Vienna adj: Bavaria (Prussia), Milan (Prussia) → interior.
        # major_city > city tier, so Vienna picked despite being interior.
        result = ai._find_best_depot_region("Prussia", world)
        assert result == "Vienna"
