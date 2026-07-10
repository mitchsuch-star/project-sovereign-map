"""W6-1 §3.1 — Retreat doctrine (BUG-CA-2 + E-CA-2).

The live audit's exhibit: "Bernadotte, retreat to Rhineland" went to Dresden
silently, then auto-retreats marched him Dresden → Silesia → Lithuania →
White Russia — each hop deeper into at-war Russia (17,000 men → 316).

Doctrine landed here:
  1. At-war soil is a new bottom tier (desperation-only, vs encirclement).
  2. Homeward bias inside each tier: homeland first, then nearer the
     capital, THEN away from the attacker.
  3. An explicitly stated destination is honored when legal and NAMED when
     substituted — never silently discarded.
  4. GR5: the enemy AI's retreat fallback avoids at-war soil the same way.
"""

from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor

from tests.conftest import MarshalFactory, WorldFactory


def _declare_war(world, a, b):
    key = "|".join(sorted([a, b]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn


def _make_world(marshals):
    world = WorldFactory.with_marshals(marshals)
    return world


class TestSafeRetreatDestinationDoctrine:
    def test_at_war_soil_avoided_when_alternative_exists(self):
        """From Belgium with friendly Paris/Normandy available, at-war
        Waterloo (Britain) and Rhineland (Prussia) must never be chosen."""
        ney = MarshalFactory.infantry(name="Ney", location="Belgium")
        enemy = MarshalFactory.enemy(name="Blucher", location="Netherlands",
                                     nation="Prussia")
        world = _make_world([ney, enemy])
        _declare_war(world, "France", "Prussia")
        _declare_war(world, "France", "Britain")
        # Waterloo (Britain) / Rhineland (Prussia) are at-war soil.
        dest = world.get_safe_retreat_destination("Ney", "Netherlands")
        assert dest in ("Paris", "Normandy")

    def test_homeward_tiebreak_prefers_capital(self):
        """Two friendly options → the one nearer the capital wins, even
        though 'away from the attacker' used to dominate."""
        ney = MarshalFactory.infantry(name="Ney", location="Belgium")
        enemy = MarshalFactory.enemy(name="Blucher", location="Waterloo",
                                     nation="Prussia")
        world = _make_world([ney, enemy])
        _declare_war(world, "France", "Prussia")
        dest = world.get_safe_retreat_destination("Ney", "Waterloo")
        # Paris (capital, dist 0) beats Normandy (dist 1) inside the same tier.
        assert dest == "Paris"

    def test_desperation_tier_still_retreats_when_encircled_by_war(self):
        """Every neighbor at-war → tier 5 fires (the old guarantee that an
        army retreats SOMEWHERE rather than breaking is preserved)."""
        ney = MarshalFactory.infantry(name="Ney", location="Waterloo")
        enemy = MarshalFactory.enemy(name="Blucher", location="Hanover",
                                     nation="Prussia")
        world = _make_world([ney, enemy])
        _declare_war(world, "France", "Prussia")
        # Waterloo's neighbors: Belgium, Netherlands, Hanover — make the
        # reachable ones Prussian at-war soil (Hanover holds Blucher and is
        # skipped for enemy presence).
        world.regions["Belgium"].controller = "Prussia"
        world.regions["Netherlands"].controller = "Prussia"
        world.regions["Hanover"].controller = "Prussia"
        dest = world.get_safe_retreat_destination("Ney", "Hanover")
        assert dest in ("Belgium", "Netherlands")

    def test_bernadotte_chain_now_falls_back_homeward(self):
        """The audit chain, reproduced in miniature: a French marshal on
        at-war soil with the attacker to the WEST used to flee EAST (away
        from the attacker, deeper into enemy land). The homeward bias +
        at-war tier now pull him back toward France."""
        ney = MarshalFactory.infantry(name="Ney", location="Rhineland")
        enemy = MarshalFactory.enemy(name="Blucher", location="Belgium",
                                     nation="Prussia")
        world = _make_world([ney, enemy])
        _declare_war(world, "France", "Prussia")
        # Rhineland's neighbors: Belgium (enemy marshal — skipped), Bavaria,
        # Lyon (France homeland), Saxony (Prussia, at-war). Bavaria stays
        # foreign-neutral: the doctrine must pick FRIENDLY Lyon, west, even
        # though it lies TOWARD the attacker.
        assert world.regions["Lyon"].controller == "France"
        dest = world.get_safe_retreat_destination("Ney", "Belgium")
        assert dest == "Lyon"


class TestExplicitRetreatDestination:
    def _danger_world(self):
        """Ney at Belgium with an at-war Prussian adjacent (in danger)."""
        ney = MarshalFactory.infantry(name="Ney", location="Belgium")
        enemy = MarshalFactory.enemy(name="Blucher", location="Waterloo",
                                     nation="Prussia")
        world = _make_world([ney, enemy])
        _declare_war(world, "France", "Prussia")
        return world, ney

    def test_stated_adjacent_legal_destination_honored(self):
        world, ney = self._danger_world()
        executor = CommandExecutor()
        result = executor._movement._execute_retreat_action(
            ney, world, {"world": world}, target="Normandy")
        assert result["success"] is True
        assert ney.location == "Normandy"
        assert "cannot be reached" not in result["message"]

    def test_illegal_destination_substitution_is_named(self):
        world, ney = self._danger_world()
        executor = CommandExecutor()
        # Lyon is not adjacent to Belgium.
        result = executor._movement._execute_retreat_action(
            ney, world, {"world": world}, target="Lyon")
        assert result["success"] is True
        assert ney.location != "Lyon"
        assert "Lyon cannot be reached" in result["message"]
        assert ney.location in result["message"]

    def test_at_war_destination_substituted_and_named(self):
        world, ney = self._danger_world()
        executor = CommandExecutor()
        # Rhineland is adjacent but Prussian at-war soil.
        result = executor._movement._execute_retreat_action(
            ney, world, {"world": world}, target="Rhineland")
        assert result["success"] is True
        assert ney.location != "Rhineland"
        assert "Rhineland cannot be reached" in result["message"]
        assert "at war" in result["message"]

    def test_target_plumbed_through_executor_dispatch(self):
        world, ney = self._danger_world()
        executor = CommandExecutor()
        result = executor.execute(
            {"success": True,
             "command": {"marshal": "Ney", "action": "retreat",
                         "target": "Normandy"}},
            {"world": world})
        assert result["success"] is True
        assert ney.location == "Normandy"

    def test_no_stated_destination_keeps_doctrine_choice(self):
        world, ney = self._danger_world()
        executor = CommandExecutor()
        result = executor._movement._execute_retreat_action(
            ney, world, {"world": world})
        assert result["success"] is True
        assert "cannot be reached" not in result["message"]


class TestEnemyAIRetreatDoctrine:
    def test_ai_avoids_at_war_soil_when_alternative_exists(self):
        """GR5: with no friendly neighbor, the AI fallback picks the
        non-at-war option over at-war soil."""
        blucher = MarshalFactory.enemy(name="Blucher", location="Waterloo",
                                       nation="Prussia")
        world = _make_world([blucher])
        _declare_war(world, "Prussia", "France")
        # Waterloo neighbors: Belgium (France, at-war), Netherlands
        # (unclaimed → enterable), Hanover (France, at-war).
        world.regions["Belgium"].controller = "France"
        world.regions["Netherlands"].controller = None
        world.regions["Hanover"].controller = "France"
        ai = EnemyAI(CommandExecutor())
        dest = ai._find_retreat_destination(blucher, "Prussia", world)
        assert dest == "Netherlands"

    def test_ai_desperation_into_at_war_only_when_encircled(self):
        blucher = MarshalFactory.enemy(name="Blucher", location="Waterloo",
                                       nation="Prussia")
        world = _make_world([blucher])
        _declare_war(world, "Prussia", "France")
        world.regions["Belgium"].controller = "France"
        world.regions["Netherlands"].controller = "France"
        world.regions["Hanover"].controller = "France"
        ai = EnemyAI(CommandExecutor())
        dest = ai._find_retreat_destination(blucher, "Prussia", world)
        # Still retreats (desperation) rather than returning None.
        assert dest in ("Belgium", "Netherlands", "Hanover")
