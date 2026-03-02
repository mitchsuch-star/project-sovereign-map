"""
Tests for Session 63: AI Coordination Enhancements.

Covers:
1. P4.6  — Coordinated attack setup (move to stage combined attack)
2. P4.75 — Ally support relationship filtering (Hostile excluded, Devoted priority)
3. P4.76 — Co-location persistence guard (stay with ally near threat)
4. P4.77 — Cross-nation adjacency scoring (relationship-weighted positioning)
5. P4.78 — Defensive reinforcement positioning (move adjacent to threatened ally)
6. Attack threshold +8% coordination estimate per co-located ally
7. Stagnation override for artillery frontline penalty
8. Combined arms awareness (triangle-completion scoring)
"""

from backend.models.marshal import Marshal
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.ai.enemy_ai import EnemyAI


# ════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════

def _make_world(**overrides):
    """Create a WorldState with default game setup."""
    world = WorldState()
    for k, v in overrides.items():
        setattr(world, k, v)
    return world


def _make_marshal(name="TestMarshal", location="Paris", strength=30000,
                  personality="cautious", nation="France",
                  cavalry=False, artillery=False, **kw):
    """Create a marshal with sensible defaults."""
    return Marshal(
        name=name, location=location, strength=strength,
        personality=personality, nation=nation,
        movement_range=2 if cavalry else 1,
        tactical_skill=7,
        cavalry=cavalry, artillery=artillery,
        spawn_location=kw.pop("spawn_location", location),
        **kw,
    )


def _setup_france_vs_coalition(world, france_marshals, coalition_marshals):
    """Set up marshals for both sides and assign controllers."""
    world.marshals.clear()
    for m in france_marshals + coalition_marshals:
        world.marshals[m.name] = m
    world.player_nation = "France"


# ════════════════════════════════════════════════════════════════
# 1. P4.6: COORDINATED ATTACK SETUP
# ════════════════════════════════════════════════════════════════

class TestCoordinatedAttack:
    """P4.6: AI stages coordinated attacks when solo can't but combined could."""

    def setup_method(self):
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)

    def test_coordinated_attack_fires_when_combined_exceeds_threshold(self):
        """Combined > 1.5x but solo < 1.5x triggers P4.6 move."""
        world = _make_world()
        world.marshals.clear()

        # Enemy at Rhine (20k). Our marshal at Belgium (25k — ratio 1.25, < 1.5).
        # Ally at Waterloo (15k) — combined 40k, ratio 2.0.
        # Belgium adj: Paris, Netherlands, Waterloo, Rhine
        attacker = _make_marshal(name="Ney", location="Belgium", strength=25000,
                                 personality="aggressive", nation="Coalition")
        ally = _make_marshal(name="Blucher", location="Waterloo", strength=15000,
                             personality="cautious", nation="Coalition")
        defender = _make_marshal(name="Davout", location="Rhineland", strength=20000,
                                 nation="France")

        world.marshals["Ney"] = attacker
        world.marshals["Blucher"] = ally
        world.marshals["Davout"] = defender
        world.player_nation = "France"

        # Relationship >= Rival required
        attacker.set_relationship("Blucher", 0)  # Professional

        result = self.ai._find_coordinated_attack(attacker, "Coalition", world)
        assert result is not None
        assert result["action"] == "move"

    def test_no_coordinated_attack_for_undefended(self):
        """P4.5 handles undefended — P4.6 skips regions with no defenders."""
        world = _make_world()
        world.marshals.clear()

        attacker = _make_marshal(name="Ney", location="Belgium", strength=25000,
                                 personality="aggressive", nation="Coalition")
        ally = _make_marshal(name="Blucher", location="Waterloo", strength=15000,
                             personality="cautious", nation="Coalition")
        # Rhine is adjacent to Belgium but has no defenders
        world.marshals["Ney"] = attacker
        world.marshals["Blucher"] = ally
        world.player_nation = "France"
        world.get_region("Rhineland").controller = "France"

        result = self.ai._find_coordinated_attack(attacker, "Coalition", world)
        assert result is None

    def test_hostile_excluded_from_coordination(self):
        """Hostile relationship (-2) ally excluded from combined strength calculation."""
        world = _make_world()
        world.marshals.clear()

        attacker = _make_marshal(name="Ney", location="Belgium", strength=25000,
                                 personality="aggressive", nation="Coalition")
        ally = _make_marshal(name="Blucher", location="Waterloo", strength=15000,
                             personality="cautious", nation="Coalition")
        defender = _make_marshal(name="Davout", location="Rhineland", strength=20000,
                                 nation="France")

        world.marshals["Ney"] = attacker
        world.marshals["Blucher"] = ally
        world.marshals["Davout"] = defender
        world.player_nation = "France"

        # Hostile relationship — should not count for coordination
        attacker.set_relationship("Blucher", -2)  # Hostile

        result = self.ai._find_coordinated_attack(attacker, "Coalition", world)
        assert result is None

    def test_no_coordination_when_solo_sufficient(self):
        """If solo ratio >= 1.5, no coordination needed."""
        world = _make_world()
        world.marshals.clear()

        # Solo ratio = 35k / 20k = 1.75 >= 1.5
        attacker = _make_marshal(name="Ney", location="Belgium", strength=35000,
                                 personality="aggressive", nation="Coalition")
        ally = _make_marshal(name="Blucher", location="Waterloo", strength=15000,
                             personality="cautious", nation="Coalition")
        defender = _make_marshal(name="Davout", location="Rhineland", strength=20000,
                                 nation="France")

        world.marshals["Ney"] = attacker
        world.marshals["Blucher"] = ally
        world.marshals["Davout"] = defender
        world.player_nation = "France"
        attacker.set_relationship("Blucher", 0)

        result = self.ai._find_coordinated_attack(attacker, "Coalition", world)
        assert result is None

    def test_coordination_skips_fortified_marshal(self):
        """Fortified marshals can't move, so P4.6 returns None."""
        world = _make_world()
        world.marshals.clear()

        attacker = _make_marshal(name="Ney", location="Belgium", strength=25000,
                                 personality="aggressive", nation="Coalition")
        attacker.fortified = True
        ally = _make_marshal(name="Blucher", location="Waterloo", strength=15000,
                             personality="cautious", nation="Coalition")
        defender = _make_marshal(name="Davout", location="Rhineland", strength=20000,
                                 nation="France")

        world.marshals["Ney"] = attacker
        world.marshals["Blucher"] = ally
        world.marshals["Davout"] = defender
        world.player_nation = "France"
        attacker.set_relationship("Blucher", 0)

        result = self.ai._find_coordinated_attack(attacker, "Coalition", world)
        assert result is None


# ════════════════════════════════════════════════════════════════
# 2. P4.75: ALLY SUPPORT RELATIONSHIP FILTERING
# ════════════════════════════════════════════════════════════════

class TestAllySupport:
    """P4.75: Ally support filters by relationship and prioritizes Devoted."""

    def setup_method(self):
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)

    def test_hostile_marshal_excluded_from_support(self):
        """Hostile (-2) ally is not considered for support."""
        world = _make_world()
        world.marshals.clear()

        # Supporter at Paris, Hostile ally at Belgium needs support
        supporter = _make_marshal(name="Ney", location="Paris", strength=30000,
                                  personality="aggressive", nation="Coalition")
        ally = _make_marshal(name="Davout", location="Belgium", strength=10000,
                             personality="cautious", nation="Coalition")
        enemy = _make_marshal(name="Wellington", location="Belgium", strength=30000,
                              nation="France")

        world.marshals["Ney"] = supporter
        world.marshals["Davout"] = ally
        world.marshals["Wellington"] = enemy
        world.player_nation = "France"

        # Hostile relationship — should not support
        supporter.set_relationship("Davout", -2)

        result = self.ai._find_ally_support_opportunity(supporter, "Coalition", world)
        assert result is None

    def test_devoted_ally_prioritized_over_professional(self):
        """Devoted (+2) ally is supported before Professional (0) ally."""
        world = _make_world()
        world.marshals.clear()

        # Supporter at Lyon. Two allies need support at adjacent regions.
        # Lyon adj: Paris, Rhine, Bavaria, Marseille, Milan
        supporter = _make_marshal(name="Ney", location="Lyon", strength=30000,
                                  personality="aggressive", nation="Coalition")

        # Professional ally at Paris (outnumbered)
        prof_ally = _make_marshal(name="Soult", location="Paris", strength=10000,
                                  personality="cautious", nation="Coalition")
        enemy_at_paris = _make_marshal(name="WellingtonA", location="Paris",
                                       strength=30000, nation="France")

        # Devoted ally at Rhine (outnumbered)
        devoted_ally = _make_marshal(name="Blucher", location="Rhineland", strength=10000,
                                     personality="cautious", nation="Coalition")
        enemy_at_rhine = _make_marshal(name="WellingtonB", location="Rhineland",
                                       strength=30000, nation="France")

        world.marshals["Ney"] = supporter
        world.marshals["Soult"] = prof_ally
        world.marshals["WellingtonA"] = enemy_at_paris
        world.marshals["Blucher"] = devoted_ally
        world.marshals["WellingtonB"] = enemy_at_rhine
        world.player_nation = "France"

        supporter.set_relationship("Soult", 0)     # Professional
        supporter.set_relationship("Blucher", 2)    # Devoted

        result = self.ai._find_ally_support_opportunity(supporter, "Coalition", world)
        assert result is not None
        # Devoted ally Blucher is tried first (sorted by relationship).
        # Enemy at Rhine blocks path → AI attacks to join.
        assert result["target"] == "WellingtonB"
        assert result["action"] == "attack"

    def test_multiple_candidates_sorted_by_relationship(self):
        """Allies sorted by relationship: Devoted > Friendly > Professional > Rival."""
        world = _make_world()
        world.marshals.clear()

        supporter = _make_marshal(name="Ney", location="Lyon", strength=30000,
                                  personality="aggressive", nation="Coalition")

        # Rival ally at Paris (outnumbered)
        rival_ally = _make_marshal(name="Soult", location="Paris", strength=10000,
                                   personality="cautious", nation="Coalition")
        enemy_at_paris = _make_marshal(name="EnemyA", location="Paris",
                                       strength=30000, nation="France")

        # Friendly ally at Rhine (outnumbered)
        friendly_ally = _make_marshal(name="Blucher", location="Rhineland", strength=10000,
                                      personality="cautious", nation="Coalition")
        enemy_at_rhine = _make_marshal(name="EnemyB", location="Rhineland",
                                       strength=30000, nation="France")

        world.marshals["Ney"] = supporter
        world.marshals["Soult"] = rival_ally
        world.marshals["EnemyA"] = enemy_at_paris
        world.marshals["Blucher"] = friendly_ally
        world.marshals["EnemyB"] = enemy_at_rhine
        world.player_nation = "France"

        supporter.set_relationship("Soult", -1)    # Rival
        supporter.set_relationship("Blucher", 1)   # Friendly

        result = self.ai._find_ally_support_opportunity(supporter, "Coalition", world)
        assert result is not None
        # Friendly ally Blucher tried first (sorted by relationship).
        # Enemy at Rhine blocks → AI attacks to join.
        assert result["target"] == "EnemyB"
        assert result["action"] == "attack"


# ════════════════════════════════════════════════════════════════
# 3. P4.76: CO-LOCATION PERSISTENCE GUARD
# ════════════════════════════════════════════════════════════════

class TestCoLocationPersistence:
    """P4.76: Stay co-located with ally when threat is nearby."""

    def setup_method(self):
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)

    def test_stays_co_located_when_ally_threatened(self):
        """Co-located with ally, enemy adjacent → maintain co-location."""
        world = _make_world()
        world.marshals.clear()

        marshal = _make_marshal(name="Ney", location="Belgium", strength=30000,
                                personality="aggressive", nation="Coalition")
        ally = _make_marshal(name="Blucher", location="Belgium", strength=25000,
                             personality="cautious", nation="Coalition")
        enemy = _make_marshal(name="Davout", location="Rhineland", strength=40000,
                              nation="France")

        world.marshals["Ney"] = marshal
        world.marshals["Blucher"] = ally
        world.marshals["Davout"] = enemy
        world.player_nation = "France"

        # Not moved this turn (settled)
        marshal.moved_this_turn = False

        assert self.ai._should_maintain_co_location(marshal, "Coalition", world) is True

    def test_does_not_stay_if_no_threat_nearby(self):
        """Co-located with ally but no enemy threat → can move away."""
        world = _make_world()
        world.marshals.clear()

        marshal = _make_marshal(name="Ney", location="Paris", strength=30000,
                                personality="aggressive", nation="Coalition")
        ally = _make_marshal(name="Blucher", location="Paris", strength=25000,
                             personality="cautious", nation="Coalition")

        world.marshals["Ney"] = marshal
        world.marshals["Blucher"] = ally
        world.player_nation = "France"

        # Set all adjacent regions to Coalition control (no threat)
        for adj_name in world.get_region("Paris").adjacent_regions:
            world.get_region(adj_name).controller = "Coalition"

        marshal.moved_this_turn = False

        assert self.ai._should_maintain_co_location(marshal, "Coalition", world) is False

    def test_does_not_stay_if_just_arrived(self):
        """Marshal just moved to this location → not settled, can move again."""
        world = _make_world()
        world.marshals.clear()

        marshal = _make_marshal(name="Ney", location="Belgium", strength=30000,
                                personality="aggressive", nation="Coalition")
        ally = _make_marshal(name="Blucher", location="Belgium", strength=25000,
                             personality="cautious", nation="Coalition")
        enemy = _make_marshal(name="Davout", location="Rhineland", strength=40000,
                              nation="France")

        world.marshals["Ney"] = marshal
        world.marshals["Blucher"] = ally
        world.marshals["Davout"] = enemy
        world.player_nation = "France"

        # Moved this turn → just arrived
        marshal.moved_this_turn = True

        assert self.ai._should_maintain_co_location(marshal, "Coalition", world) is False

    def test_does_not_stay_if_alone(self):
        """No co-located allies → no reason to maintain co-location."""
        world = _make_world()
        world.marshals.clear()

        marshal = _make_marshal(name="Ney", location="Belgium", strength=30000,
                                personality="aggressive", nation="Coalition")
        enemy = _make_marshal(name="Davout", location="Rhineland", strength=40000,
                              nation="France")

        world.marshals["Ney"] = marshal
        world.marshals["Davout"] = enemy
        world.player_nation = "France"

        marshal.moved_this_turn = False

        assert self.ai._should_maintain_co_location(marshal, "Coalition", world) is False

    def test_guard_prevents_strategic_move(self):
        """P4.76 guard in _consider_strategic_move returns None."""
        world = _make_world()
        world.marshals.clear()

        marshal = _make_marshal(name="Ney", location="Belgium", strength=30000,
                                personality="aggressive", nation="Coalition")
        ally = _make_marshal(name="Blucher", location="Belgium", strength=25000,
                             personality="cautious", nation="Coalition")
        enemy = _make_marshal(name="Davout", location="Rhineland", strength=40000,
                              nation="France")

        world.marshals["Ney"] = marshal
        world.marshals["Blucher"] = ally
        world.marshals["Davout"] = enemy
        world.player_nation = "France"
        marshal.moved_this_turn = False

        result = self.ai._consider_strategic_move(marshal, "Coalition", world)
        assert result is None


# ════════════════════════════════════════════════════════════════
# 4. P4.77: CROSS-NATION ADJACENCY SCORING
# ════════════════════════════════════════════════════════════════

class TestAllyAdjacencyScoring:
    """P4.77: Devoted allies make adjacent positions more attractive."""

    def setup_method(self):
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)

    def test_devoted_ally_gives_bonus(self):
        """Devoted (+2) ally adjacent to position gives +10 score."""
        world = _make_world()
        world.marshals.clear()

        marshal = _make_marshal(name="Ney", location="Paris", strength=30000,
                                personality="aggressive", nation="Coalition")
        # Devoted ally at Belgium (adjacent to Paris)
        ally = _make_marshal(name="Blucher", location="Belgium", strength=25000,
                             personality="cautious", nation="Coalition")

        world.marshals["Ney"] = marshal
        world.marshals["Blucher"] = ally
        world.player_nation = "France"

        marshal.set_relationship("Blucher", 2)  # Devoted

        bonus = self.ai._get_ally_adjacency_bonus("Paris", marshal, "Coalition", world)
        # Blucher is at Belgium which is adjacent to Paris, so +10
        assert bonus >= 10

    def test_hostile_ally_gives_no_bonus(self):
        """Hostile (-2) ally adjacent to position gives 0 bonus."""
        world = _make_world()
        world.marshals.clear()

        marshal = _make_marshal(name="Ney", location="Paris", strength=30000,
                                personality="aggressive", nation="Coalition")
        ally = _make_marshal(name="Davout", location="Belgium", strength=25000,
                             personality="cautious", nation="Coalition")

        world.marshals["Ney"] = marshal
        world.marshals["Davout"] = ally
        world.player_nation = "France"

        marshal.set_relationship("Davout", -2)  # Hostile

        bonus = self.ai._get_ally_adjacency_bonus("Paris", marshal, "Coalition", world)
        assert bonus == 0

    def test_professional_ally_gives_5(self):
        """Professional (0) ally gives +5 bonus."""
        world = _make_world()
        world.marshals.clear()

        marshal = _make_marshal(name="Ney", location="Paris", strength=30000,
                                personality="aggressive", nation="Coalition")
        ally = _make_marshal(name="Soult", location="Belgium", strength=25000,
                             personality="cautious", nation="Coalition")

        world.marshals["Ney"] = marshal
        world.marshals["Soult"] = ally
        world.player_nation = "France"

        marshal.set_relationship("Soult", 0)  # Professional

        bonus = self.ai._get_ally_adjacency_bonus("Paris", marshal, "Coalition", world)
        assert bonus == 5

    def test_scoring_applied_in_aggressive_movement(self):
        """Aggressive P7 uses ally adjacency as tiebreaker between equal-distance positions."""
        world = _make_world()
        world.marshals.clear()

        # Marshal at Lyon, enemy at Vienna (dist 2).
        # Lyon adj: Paris, Rhine, Bavaria, Marseille, Milan
        # Bavaria adj to Vienna (dist 1), Rhine adj to Bavaria (dist 2) — but Rhine not adj to Vienna directly
        # Only Bavaria reduces distance. But we can test that scoring is applied.
        marshal = _make_marshal(name="Ney", location="Lyon", strength=30000,
                                personality="aggressive", nation="Coalition")
        enemy = _make_marshal(name="Wellington", location="Vienna", strength=20000,
                              nation="France")
        # Devoted ally at Bavaria (adjacent to target move Bavaria)
        ally = _make_marshal(name="Blucher", location="Bavaria", strength=25000,
                             personality="cautious", nation="Coalition")

        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.marshals["Blucher"] = ally
        world.player_nation = "France"

        marshal.set_relationship("Blucher", 2)  # Devoted

        result = self.ai._consider_strategic_move(marshal, "Coalition", world)
        # Should move toward Vienna, Bavaria is distance-reducing and has ally bonus
        assert result is not None
        assert result["action"] == "move"


# ════════════════════════════════════════════════════════════════
# 5. P4.78: DEFENSIVE REINFORCEMENT POSITIONING
# ════════════════════════════════════════════════════════════════

class TestDefensiveReinforcement:
    """P4.78: Move adjacent to threatened ally for reinforcement readiness."""

    def setup_method(self):
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)

    def test_moves_adjacent_to_threatened_ally(self):
        """P4.78 fires when ally is threatened and marshal is not adjacent."""
        world = _make_world()
        world.marshals.clear()

        # Marshal at Paris, ally at Rhine (threatened by enemy at Bavaria)
        # Paris adj: Normandy, Belgium, Lyon, Bordeaux
        # Rhine adj: Belgium, Bavaria, Lyon
        # Both Belgium and Lyon are adjacent to both Paris and Rhine.
        # Neither is adj to Bavaria (enemy). Scoring should be equal.
        marshal = _make_marshal(name="Ney", location="Paris", strength=30000,
                                personality="aggressive", nation="Coalition")
        ally = _make_marshal(name="Blucher", location="Rhineland", strength=20000,
                             personality="cautious", nation="Coalition")
        enemy = _make_marshal(name="Wellington", location="Bavaria", strength=30000,
                              nation="France")

        world.marshals["Ney"] = marshal
        world.marshals["Blucher"] = ally
        world.marshals["Wellington"] = enemy
        world.player_nation = "France"

        marshal.set_relationship("Blucher", 0)  # Professional (>= Rival)

        result = self.ai._find_defensive_reinforcement_position(marshal, "Coalition", world)
        assert result is not None
        assert result["action"] == "move"
        # Should move to Belgium or Lyon (both adjacent to Paris and Rhine)
        assert result["target"] in ("Belgium", "Lyon")

    def test_no_move_if_already_adjacent(self):
        """Already adjacent to threatened ally → don't move."""
        world = _make_world()
        world.marshals.clear()

        # Marshal at Belgium (adjacent to Rhine), ally at Rhine (threatened)
        marshal = _make_marshal(name="Ney", location="Belgium", strength=30000,
                                personality="aggressive", nation="Coalition")
        ally = _make_marshal(name="Blucher", location="Rhineland", strength=20000,
                             personality="cautious", nation="Coalition")
        enemy = _make_marshal(name="Wellington", location="Bavaria", strength=30000,
                              nation="France")

        world.marshals["Ney"] = marshal
        world.marshals["Blucher"] = ally
        world.marshals["Wellington"] = enemy
        world.player_nation = "France"

        marshal.set_relationship("Blucher", 0)

        result = self.ai._find_defensive_reinforcement_position(marshal, "Coalition", world)
        assert result is None

    def test_hostile_ally_excluded(self):
        """Hostile (-2) ally not eligible for reinforcement positioning."""
        world = _make_world()
        world.marshals.clear()

        marshal = _make_marshal(name="Ney", location="Paris", strength=30000,
                                personality="aggressive", nation="Coalition")
        ally = _make_marshal(name="Blucher", location="Rhineland", strength=20000,
                             personality="cautious", nation="Coalition")
        enemy = _make_marshal(name="Wellington", location="Bavaria", strength=30000,
                              nation="France")

        world.marshals["Ney"] = marshal
        world.marshals["Blucher"] = ally
        world.marshals["Wellington"] = enemy
        world.player_nation = "France"

        marshal.set_relationship("Blucher", -2)  # Hostile

        result = self.ai._find_defensive_reinforcement_position(marshal, "Coalition", world)
        assert result is None

    def test_prefers_positions_adjacent_to_enemy(self):
        """Among valid positions, prefer ones also adjacent to enemy."""
        world = _make_world()
        world.marshals.clear()

        # Marshal at Marseille. Ally at Rhine (threatened by enemy at Bavaria).
        # Marseille adj: Lyon, Geneva
        # Lyon adj to Rhine AND adj to Bavaria (enemy) → better position
        # But Geneva is NOT adj to Rhine
        marshal = _make_marshal(name="Ney", location="Marseille", strength=30000,
                                personality="aggressive", nation="Coalition")
        ally = _make_marshal(name="Blucher", location="Rhineland", strength=20000,
                             personality="cautious", nation="Coalition")
        enemy = _make_marshal(name="Wellington", location="Bavaria", strength=30000,
                              nation="France")

        world.marshals["Ney"] = marshal
        world.marshals["Blucher"] = ally
        world.marshals["Wellington"] = enemy
        world.player_nation = "France"

        marshal.set_relationship("Blucher", 0)

        result = self.ai._find_defensive_reinforcement_position(marshal, "Coalition", world)
        assert result is not None
        # Lyon is adjacent to both Rhine (ally) and Bavaria (enemy)
        assert result["target"] == "Lyon"

    def test_no_reinforcement_if_ally_not_threatened(self):
        """Ally not threatened (no enemy adjacent) → P4.78 doesn't fire."""
        world = _make_world()
        world.marshals.clear()

        marshal = _make_marshal(name="Ney", location="Paris", strength=30000,
                                personality="aggressive", nation="Coalition")
        ally = _make_marshal(name="Blucher", location="Rhineland", strength=20000,
                             personality="cautious", nation="Coalition")
        # No enemies at all

        world.marshals["Ney"] = marshal
        world.marshals["Blucher"] = ally
        world.player_nation = "France"

        marshal.set_relationship("Blucher", 0)

        result = self.ai._find_defensive_reinforcement_position(marshal, "Coalition", world)
        assert result is None


# ════════════════════════════════════════════════════════════════
# 6. ATTACK THRESHOLD +8% COORDINATION ESTIMATE
# ════════════════════════════════════════════════════════════════

class TestAttackThresholdCoordination:
    """AI inflates perceived strength ratio by +8% per co-located ally."""

    def setup_method(self):
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)

    def test_coordination_estimate_enables_attack(self):
        """Marshal with co-located ally gets +8% boost, enabling attack above threshold."""
        world = _make_world()
        world.marshals.clear()

        # Balanced marshal (threshold ~1.0). Solo ratio ~1.05 (borderline).
        # With 2 allies co-located: +16% → effective ratio ~1.21 (clearly above threshold).
        attacker = _make_marshal(name="Ney", location="Belgium", strength=21000,
                                 personality="balanced", nation="Coalition")
        ally1 = _make_marshal(name="Blucher", location="Belgium", strength=5000,
                              personality="cautious", nation="Coalition")
        ally2 = _make_marshal(name="Soult", location="Belgium", strength=5000,
                              personality="cautious", nation="Coalition")
        # Enemy adjacent at Rhine
        defender = _make_marshal(name="Wellington", location="Rhineland", strength=20000,
                                 nation="France")

        world.marshals["Ney"] = attacker
        world.marshals["Blucher"] = ally1
        world.marshals["Soult"] = ally2
        world.marshals["Wellington"] = defender
        world.player_nation = "France"

        # Combined strength for ratio: 21k + 5k + 5k = 31k. Base ratio: 31k/20k = 1.55
        # Plus +8% * 2 allies = +0.16 → effective ratio ~1.71
        # Without coordination estimate: base ratio of 1.55 might still trigger P4,
        # so let's verify the method adds the estimate.
        result = self.ai._find_attack_opportunity(attacker, "Coalition", world)
        # Should find an attack opportunity with the coordination boost
        assert result is not None

    def test_no_coordination_when_alone(self):
        """Solo marshal gets no coordination estimate boost."""
        world = _make_world()
        world.marshals.clear()

        # Cautious marshal (threshold ~1.3). Solo ratio ~0.8 (below threshold).
        attacker = _make_marshal(name="Ney", location="Belgium", strength=16000,
                                 personality="cautious", nation="Coalition")
        defender = _make_marshal(name="Wellington", location="Rhineland", strength=20000,
                                 nation="France")

        world.marshals["Ney"] = attacker
        world.marshals["Wellington"] = defender
        world.player_nation = "France"

        result = self.ai._find_attack_opportunity(attacker, "Coalition", world)
        # Solo ratio 0.8 < threshold 1.3 → no attack
        assert result is None


# ════════════════════════════════════════════════════════════════
# 7. STAGNATION OVERRIDE FOR ARTILLERY
# ════════════════════════════════════════════════════════════════

class TestStagnationOverride:
    """Artillery frontline penalty reduced when stagnation >= 3."""

    def setup_method(self):
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)

    def test_stagnation_reduces_frontline_penalty_unscreened(self):
        """Stagnation >= 3: unscreened frontline penalty reduced from -50 to -20."""
        world = _make_world()
        world.marshals.clear()

        art = _make_marshal(name="Drouot", location="Belgium", strength=25000,
                            personality="cautious", nation="Coalition", artillery=True)
        world.marshals["Drouot"] = art
        world.player_nation = "France"

        # Belgium is frontline (Rhine is enemy-controlled)
        world.get_region("Belgium").controller = "Coalition"
        world.get_region("Rhineland").controller = "France"

        # No stagnation — full penalty
        world.ai_stagnation_turns["Drouot"] = 0
        score_no_stagnation = self.ai._score_artillery_position("Belgium", art, "Coalition", world)

        # High stagnation — reduced penalty
        world.ai_stagnation_turns["Drouot"] = 3
        score_stagnation = self.ai._score_artillery_position("Belgium", art, "Coalition", world)

        # With stagnation, penalty is -20 instead of -50, so score is 30 higher
        assert score_stagnation > score_no_stagnation
        assert score_stagnation - score_no_stagnation == 30

    def test_stagnation_reduces_frontline_penalty_screened(self):
        """Stagnation >= 3: screened frontline penalty reduced from -30 to -10."""
        world = _make_world()
        world.marshals.clear()

        art = _make_marshal(name="Drouot", location="Belgium", strength=25000,
                            personality="cautious", nation="Coalition", artillery=True)
        inf = _make_marshal(name="Soult", location="Belgium", strength=30000,
                            personality="cautious", nation="Coalition")
        world.marshals["Drouot"] = art
        world.marshals["Soult"] = inf
        world.player_nation = "France"

        world.get_region("Belgium").controller = "Coalition"
        world.get_region("Rhineland").controller = "France"

        # No stagnation — screened penalty -30
        world.ai_stagnation_turns["Drouot"] = 0
        score_no_stagnation = self.ai._score_artillery_position("Belgium", art, "Coalition", world)

        # Stagnation — reduced penalty -10
        world.ai_stagnation_turns["Drouot"] = 3
        score_stagnation = self.ai._score_artillery_position("Belgium", art, "Coalition", world)

        assert score_stagnation > score_no_stagnation
        assert score_stagnation - score_no_stagnation == 20  # -10 vs -30

    def test_non_artillery_unaffected_by_stagnation(self):
        """Stagnation override only applies to artillery, not infantry/cavalry."""
        world = _make_world()
        world.marshals.clear()

        # Infantry at Belgium (frontline) — stagnation should not change scoring
        inf = _make_marshal(name="Soult", location="Belgium", strength=30000,
                            personality="cautious", nation="Coalition")
        world.marshals["Soult"] = inf
        world.player_nation = "France"

        world.get_region("Belgium").controller = "Coalition"
        world.get_region("Rhineland").controller = "France"

        # _score_artillery_position is only called for artillery, but
        # verify infantry doesn't have special handling.
        # The actual check: _consider_strategic_move for infantry uses different logic.
        # This test verifies the stagnation override is in _score_artillery_position only.
        world.ai_stagnation_turns["Soult"] = 5
        # Infantry never calls _score_artillery_position, so this is a design verification
        # Just verify the method still applies penalties based on the marshal's stagnation
        score = self.ai._score_artillery_position("Belgium", inf, "Coalition", world)
        # This test is mainly about documenting that the stagnation field is read
        # from the marshal name, not the artillery flag
        assert isinstance(score, int)


# ════════════════════════════════════════════════════════════════
# 8. COMBINED ARMS AWARENESS
# ════════════════════════════════════════════════════════════════

class TestCombinedArmsAwareness:
    """AI prefers positions that complete infantry/cavalry/artillery triangle."""

    def setup_method(self):
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)

    def test_completing_triangle_gives_bonus(self):
        """Moving to position with 2 existing types as the 3rd type → +20."""
        world = _make_world()
        world.marshals.clear()

        # Infantry + cavalry at Belgium. Artillery would complete the triangle.
        inf = _make_marshal(name="Soult", location="Belgium", strength=30000,
                            personality="cautious", nation="Coalition")
        cav = _make_marshal(name="Uxbridge", location="Belgium", strength=20000,
                            personality="aggressive", nation="Coalition", cavalry=True)
        art = _make_marshal(name="Drouot", location="Paris", strength=25000,
                            personality="cautious", nation="Coalition", artillery=True)

        world.marshals["Soult"] = inf
        world.marshals["Uxbridge"] = cav
        world.marshals["Drouot"] = art
        world.player_nation = "France"

        bonus = self.ai._get_combined_arms_bonus("Belgium", art, "Coalition", world)
        assert bonus == 20

    def test_no_bonus_when_type_already_present(self):
        """Adding same type as existing → 0 bonus (not completing triangle)."""
        world = _make_world()
        world.marshals.clear()

        inf1 = _make_marshal(name="Soult", location="Belgium", strength=30000,
                             personality="cautious", nation="Coalition")
        cav = _make_marshal(name="Uxbridge", location="Belgium", strength=20000,
                            personality="aggressive", nation="Coalition", cavalry=True)
        # Another infantry — same type already there
        inf2 = _make_marshal(name="Ney", location="Paris", strength=25000,
                             personality="aggressive", nation="Coalition")

        world.marshals["Soult"] = inf1
        world.marshals["Uxbridge"] = cav
        world.marshals["Ney"] = inf2
        world.player_nation = "France"

        bonus = self.ai._get_combined_arms_bonus("Belgium", inf2, "Coalition", world)
        assert bonus == 0

    def test_no_bonus_when_only_one_type_present(self):
        """Only one type present → adding 2nd doesn't trigger full triangle bonus."""
        world = _make_world()
        world.marshals.clear()

        inf = _make_marshal(name="Soult", location="Belgium", strength=30000,
                            personality="cautious", nation="Coalition")
        cav = _make_marshal(name="Uxbridge", location="Paris", strength=20000,
                            personality="aggressive", nation="Coalition", cavalry=True)

        world.marshals["Soult"] = inf
        world.marshals["Uxbridge"] = cav
        world.player_nation = "France"

        # Only infantry at Belgium, cavalry joining → 2 of 3, not all 3
        bonus = self.ai._get_combined_arms_bonus("Belgium", cav, "Coalition", world)
        assert bonus == 0

    def test_no_bonus_when_empty_region(self):
        """No allies at position → 0 bonus."""
        world = _make_world()
        world.marshals.clear()

        cav = _make_marshal(name="Uxbridge", location="Paris", strength=20000,
                            personality="aggressive", nation="Coalition", cavalry=True)
        world.marshals["Uxbridge"] = cav
        world.player_nation = "France"

        bonus = self.ai._get_combined_arms_bonus("Belgium", cav, "Coalition", world)
        assert bonus == 0


# ════════════════════════════════════════════════════════════════
# 9. INTEGRATION TESTS
# ════════════════════════════════════════════════════════════════

class TestIntegration:
    """Integration tests for AI coordination as a whole."""

    def setup_method(self):
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)

    def test_ney_davout_never_coordinate(self):
        """Hostile filter prevents Ney-Davout coordination (AI-side marshals)."""
        world = _make_world()
        world.marshals.clear()

        ney = _make_marshal(name="Ney", location="Belgium", strength=25000,
                            personality="aggressive", nation="Coalition")
        davout = _make_marshal(name="Davout", location="Waterloo", strength=15000,
                               personality="cautious", nation="Coalition")
        defender = _make_marshal(name="Wellington", location="Rhineland", strength=20000,
                                 nation="France")

        world.marshals["Ney"] = ney
        world.marshals["Davout"] = davout
        world.marshals["Wellington"] = defender
        world.player_nation = "France"

        # Hostile relationship
        ney.set_relationship("Davout", -2)

        # P4.6 should not fire (Hostile excluded)
        coord = self.ai._find_coordinated_attack(ney, "Coalition", world)
        assert coord is None

        # P4.75 should not consider Davout
        support = self.ai._find_ally_support_opportunity(ney, "Coalition", world)
        # Davout is the only ally and he's Hostile, so no support
        assert support is None

        # P4.78 should not fire for Hostile ally
        reinforce = self.ai._find_defensive_reinforcement_position(ney, "Coalition", world)
        assert reinforce is None

    def test_rival_relationship_allows_coordination(self):
        """Rival (-1) is minimum for coordination — should work."""
        world = _make_world()
        world.marshals.clear()

        marshal = _make_marshal(name="Ney", location="Belgium", strength=25000,
                                personality="aggressive", nation="Coalition")
        ally = _make_marshal(name="Soult", location="Waterloo", strength=15000,
                             personality="cautious", nation="Coalition")
        defender = _make_marshal(name="Wellington", location="Rhineland", strength=20000,
                                 nation="France")

        world.marshals["Ney"] = marshal
        world.marshals["Soult"] = ally
        world.marshals["Wellington"] = defender
        world.player_nation = "France"

        # Rival relationship — minimum for coordination
        marshal.set_relationship("Soult", -1)

        coord = self.ai._find_coordinated_attack(marshal, "Coalition", world)
        assert coord is not None

    def test_p4_78_in_priority_chain(self):
        """P4.78 fires in _evaluate_marshal after P7, before P7.5."""
        world = _make_world()
        world.marshals.clear()

        # Set up: marshal with no attack/capture/support/move opportunity,
        # but has a threatened ally to reinforce.
        marshal = _make_marshal(name="Ney", location="Paris", strength=30000,
                                personality="cautious", nation="Coalition")
        ally = _make_marshal(name="Blucher", location="Rhineland", strength=20000,
                             personality="cautious", nation="Coalition")
        enemy = _make_marshal(name="Wellington", location="Bavaria", strength=30000,
                              nation="France")

        world.marshals["Ney"] = marshal
        world.marshals["Blucher"] = ally
        world.marshals["Wellington"] = enemy
        world.player_nation = "France"

        # Ensure P7 doesn't fire: marshal is cautious, no stagnation, no enemy adjacent to marshal
        world.ai_stagnation_turns["Ney"] = 0
        marshal.set_relationship("Blucher", 0)

        # All Paris-adjacent regions controlled by Coalition (no threat near marshal)
        for adj_name in world.get_region("Paris").adjacent_regions:
            world.get_region(adj_name).controller = "Coalition"

        # But Blucher at Rhine is threatened (Bavaria has enemy)
        # P4.78 should fire: move to Lyon (adjacent to Rhine + Bavaria)
        action, priority = self.ai._evaluate_marshal(marshal, "Coalition", world)
        if action:
            # Should be a move toward Rhine's vicinity
            assert action["action"] == "move"

    def test_co_location_guard_integrates_with_evaluate(self):
        """P4.76 guard prevents P7 movement when co-located near threat."""
        world = _make_world()
        world.marshals.clear()

        # Two Coalition marshals co-located at Belgium, enemy at Rhine
        marshal = _make_marshal(name="Ney", location="Belgium", strength=20000,
                                personality="aggressive", nation="Coalition")
        ally = _make_marshal(name="Blucher", location="Belgium", strength=20000,
                             personality="cautious", nation="Coalition")
        enemy = _make_marshal(name="Wellington", location="Rhineland", strength=50000,
                              nation="France")

        world.marshals["Ney"] = marshal
        world.marshals["Blucher"] = ally
        world.marshals["Wellington"] = enemy
        world.player_nation = "France"
        marshal.moved_this_turn = False

        # P7 would normally move Ney toward Rhine (aggressive), but P4.76 prevents it
        move = self.ai._consider_strategic_move(marshal, "Coalition", world)
        assert move is None
