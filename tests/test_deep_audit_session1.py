"""
Tests for Deep Audit Session 1: Core Combat & War Score Fixes.

Covers 10 fixes:
- Fix 1: Defense modifier — verify division is correct (NOT inverted)
- Fix 2: War score records 0 casualties
- Fix 3: Defiance "won" field always False
- Fix 4: Square formation blocks coordination
- Fix 5: Glorious charge missing war score
- Fix 6: Garrison combat not recorded for war score
- Fix 7: Movement engagement treats allies as enemies
- Fix 8: Fortified marshal bypasses fortify check via strategic execution
- Fix 9: DEFEND no-op check in wrong location
- Fix 10: Dead code (no tests needed — style only)
"""

import random

from backend.models.marshal import Marshal, Stance
from backend.models.world_state import WorldState
from backend.game_logic.combat import CombatResolver
from backend.commands.executor import CommandExecutor
from backend.commands.defiance import defiance_succeeded


# ════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════

def _make_marshal(name="TestInf", location="Paris", strength=30000,
                  personality="cautious", nation="France",
                  cavalry=False, artillery=False, **kw):
    """Create a marshal with sensible defaults."""
    return Marshal(
        name=name, location=location, strength=strength,
        personality=personality, nation=nation,
        movement_range=2 if cavalry else 1,
        tactical_skill=7,
        skills=kw.pop("skills", {
            "tactical": 7, "shock": 7, "defense": 7,
            "logistics": 7, "administration": 7, "command": 7,
        }),
        cavalry=cavalry, artillery=artillery,
        spawn_location=kw.pop("spawn_location", location),
        **kw,
    )


def _make_world_with_marshals(marshal_list, current_turn=1):
    """Create a WorldState and replace marshals with given list."""
    world = WorldState()
    world.marshals.clear()
    for m in marshal_list:
        world.marshals[m.name] = m
    world.current_turn = current_turn
    return world


def _make_game_state(world):
    """Wrap world in a game_state dict."""
    return {"world": world}


def _wrap_command(action, marshal=None, target=None, **extra):
    """Wrap command in the parsed format executor.execute() expects."""
    cmd = {"action": action}
    if marshal:
        cmd["marshal"] = marshal
    if target:
        cmd["target"] = target
    cmd.update(extra)
    return {"success": True, "command": cmd}


# ════════════════════════════════════════════════════════════════
# FIX 1: Defense modifier — verify existing code is correct
# ════════════════════════════════════════════════════════════════

class TestFix1DefenseModifierCorrectness:
    """Defensive stance should REDUCE casualties taken (division by >1 is correct)."""

    def test_defensive_stance_reduces_casualties(self):
        """A defender in DEFENSIVE stance should take fewer casualties than NEUTRAL."""
        combat = CombatResolver()
        defensive_total = 0
        neutral_total = 0
        trials = 50

        for _ in range(trials):
            atk = _make_marshal(name="Atk", strength=30000, personality="aggressive", nation="Prussia")
            dfn_def = _make_marshal(name="DefD", strength=25000, personality="cautious")
            dfn_def.stance = Stance.DEFENSIVE

            atk2 = _make_marshal(name="Atk2", strength=30000, personality="aggressive", nation="Prussia")
            dfn_neu = _make_marshal(name="DefN", strength=25000, personality="cautious")
            dfn_neu.stance = Stance.NEUTRAL

            result_def = combat.resolve_battle(atk, dfn_def)
            result_neu = combat.resolve_battle(atk2, dfn_neu)

            defensive_total += result_def["defender"]["casualties"]
            neutral_total += result_neu["defender"]["casualties"]

        assert defensive_total < neutral_total, (
            f"Defensive stance ({defensive_total}) should take fewer casualties than neutral ({neutral_total})"
        )

    def test_aggressive_stance_increases_casualties(self):
        """A defender in AGGRESSIVE stance should take more casualties than NEUTRAL."""
        combat = CombatResolver()
        aggressive_total = 0
        neutral_total = 0
        trials = 50

        for _ in range(trials):
            atk = _make_marshal(name="Atk", strength=30000, personality="aggressive", nation="Prussia")
            dfn_agg = _make_marshal(name="DefA", strength=25000, personality="cautious")
            dfn_agg.stance = Stance.AGGRESSIVE

            atk2 = _make_marshal(name="Atk2", strength=30000, personality="aggressive", nation="Prussia")
            dfn_neu = _make_marshal(name="DefN", strength=25000, personality="cautious")
            dfn_neu.stance = Stance.NEUTRAL

            result_agg = combat.resolve_battle(atk, dfn_agg)
            result_neu = combat.resolve_battle(atk2, dfn_neu)

            aggressive_total += result_agg["defender"]["casualties"]
            neutral_total += result_neu["defender"]["casualties"]

        assert aggressive_total > neutral_total, (
            f"Aggressive stance ({aggressive_total}) should take more casualties than neutral ({neutral_total})"
        )

    def test_neutral_stance_unchanged(self):
        """Neutral stance modifier is 1.0, should produce baseline casualties."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=30000, personality="aggressive", nation="Prussia")
        dfn = _make_marshal(name="Def", strength=25000, personality="cautious")
        dfn.stance = Stance.NEUTRAL

        result = combat.resolve_battle(atk, dfn)
        assert result["defender"]["casualties"] >= 0
        assert result["attacker"]["casualties"] >= 0


# ════════════════════════════════════════════════════════════════
# FIX 2: War score records 0 casualties for ALL battles
# ════════════════════════════════════════════════════════════════

class TestFix2WarScoreCasualties:
    """War score should record actual casualties from nested combat result."""

    def test_solo_battle_records_casualties(self):
        """A single attack with a decisive outcome should record non-zero casualties."""
        # Use lopsided forces to guarantee attacker victory
        atk = _make_marshal(name="Ney", location="Saxony", strength=60000, nation="France")
        dfn = _make_marshal(name="Blucher", location="Saxony", strength=15000, nation="Prussia")
        world = _make_world_with_marshals([atk, dfn])
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "WAR"
        game_state = _make_game_state(world)

        executor = CommandExecutor()
        result = executor.execute(
            _wrap_command("attack", marshal="Ney", target="Blucher"),
            game_state
        )

        assert result.get("success", False)
        key = world._make_diplo_key("France", "Prussia")
        records = getattr(world, 'battle_records', {}).get(key, [])
        assert len(records) > 0, "Decisive battle should have a battle record"
        record = records[0]
        total = record["attacker_casualties"] + record["defender_casualties"]
        assert total > 0, f"Total casualties should be > 0, got {total}"

    def test_war_score_accumulates_across_battles(self):
        """Multiple battles should each add records."""
        # Seed for determinism (this repo runs under pytest-randomly). Without
        # a seed the first 80k-vs-15k assault sometimes ROUTS Blucher, who
        # flees and yields Saxony — leaving a pending capture-choice popup that
        # blocks the second attack, so only one record lands. This seed keeps
        # Blucher holding Saxony so the intended two-battle case is exercised.
        # (Flakiness widened after the Phase 1-2 combat-decisiveness landings;
        # test-only fix, no product behavior change.)
        random.seed(2)
        atk = _make_marshal(name="Ney", location="Saxony", strength=80000, nation="France")
        dfn = _make_marshal(name="Blucher", location="Saxony", strength=15000, nation="Prussia")
        world = _make_world_with_marshals([atk, dfn])
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "WAR"
        game_state = _make_game_state(world)

        executor = CommandExecutor()
        executor.execute(
            _wrap_command("attack", marshal="Ney", target="Blucher"),
            game_state
        )

        # Reset for second battle if both alive
        if atk.strength > 0 and dfn.strength > 0:
            atk.location = "Saxony"
            dfn.location = "Saxony"
            atk.moved_this_turn = False
            atk.attacked_this_turn = False
            executor.execute(
                _wrap_command("attack", marshal="Ney", target="Blucher"),
                game_state
            )

            key = world._make_diplo_key("France", "Prussia")
            records = getattr(world, 'battle_records', {}).get(key, [])
            assert len(records) >= 2, f"Expected 2+ records, got {len(records)}"

    def test_coordinated_battle_records_casualties(self):
        """A coordinated attack (multiple marshals) should also record non-zero casualties."""
        atk1 = _make_marshal(name="Ney", location="Saxony", strength=30000, nation="France")
        atk2 = _make_marshal(name="Davout", location="Saxony", strength=25000, nation="France")
        dfn = _make_marshal(name="Blucher", location="Saxony", strength=40000, nation="Prussia")
        world = _make_world_with_marshals([atk1, atk2, dfn])
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "WAR"
        game_state = _make_game_state(world)

        executor = CommandExecutor()
        result = executor.execute(
            _wrap_command("attack", marshal="Ney", target="Blucher"),
            game_state
        )

        assert result.get("success", False)
        key = world._make_diplo_key("France", "Prussia")
        records = getattr(world, 'battle_records', {}).get(key, [])
        if records:
            total = records[0]["attacker_casualties"] + records[0]["defender_casualties"]
            assert total > 0, f"Coordinated battle should record casualties, got {total}"


# ════════════════════════════════════════════════════════════════
# FIX 3: Defiance "won" field always False
# ════════════════════════════════════════════════════════════════

class TestFix3DefianceWonField:
    """defiance_succeeded() should correctly evaluate attack outcomes."""

    def test_defiant_attack_wins_cleanly(self):
        """Winning with < 50% casualties should evaluate as True (RIGHT)."""
        marshal = _make_marshal(name="Ney", strength=30000)
        battle_result = {
            "attacker_won": True,
            "attacker": {"casualties": 5000, "remaining": 25000},
            "defender": {"casualties": 10000, "remaining": 15000},
        }
        result = defiance_succeeded(marshal, "attack", battle_result, 30000)
        assert result is True

    def test_defiant_attack_loses(self):
        """Losing should evaluate as False (WRONG)."""
        marshal = _make_marshal(name="Ney", strength=30000)
        battle_result = {
            "attacker_won": False,
            "attacker": {"casualties": 15000, "remaining": 15000},
            "defender": {"casualties": 5000, "remaining": 20000},
        }
        result = defiance_succeeded(marshal, "attack", battle_result, 30000)
        assert result is False

    def test_defiant_attack_pyrrhic_victory(self):
        """Winning with > 50% casualties is pyrrhic — evaluates as False."""
        marshal = _make_marshal(name="Ney", strength=30000)
        battle_result = {
            "attacker_won": True,
            "attacker": {"casualties": 16000, "remaining": 14000},
            "defender": {"casualties": 10000, "remaining": 15000},
        }
        result = defiance_succeeded(marshal, "attack", battle_result, 30000)
        assert result is False


# ════════════════════════════════════════════════════════════════
# FIX 4: Square formation blocks coordination
# ════════════════════════════════════════════════════════════════

class TestFix4SquareFormationCoordination:
    """Square formation should NOT block coordination bonuses."""

    def test_square_formation_provides_coordination(self):
        """A marshal in square formation should still provide attack coordination bonus."""
        primary = _make_marshal(name="Ney", location="Saxony", strength=30000, nation="France")
        ally = _make_marshal(name="Davout", location="Saxony", strength=25000, nation="France")
        ally.square_formation = True

        executor = CommandExecutor()
        atk_bonus, def_bonus = executor._calculate_per_ally_coordination(primary, [ally])

        assert atk_bonus > 0, "Square formation ally should provide attack coordination"
        assert def_bonus > 0, "Square formation ally should provide defense coordination"

    def test_square_formation_counted_as_adjacent_ally(self):
        """A marshal in square formation in adjacent region should count for adjacent support."""
        primary = _make_marshal(name="Ney", location="Saxony", strength=30000, nation="France")
        # Berlin is adjacent to Saxony
        ally = _make_marshal(name="Davout", location="Berlin", strength=25000, nation="France")
        ally.square_formation = True

        world = _make_world_with_marshals([primary, ally])

        executor = CommandExecutor()
        count, names = executor._count_adjacent_allies("Saxony", "France", world)

        assert count >= 1, "Square formation ally in adjacent region should be counted"
        assert "Davout" in names


# ════════════════════════════════════════════════════════════════
# FIX 5: Glorious charge missing war score recording
# ════════════════════════════════════════════════════════════════

class TestFix5GloriousChargeWarScore:
    """Glorious charge should record diplomacy war score."""

    def test_glorious_charge_records_war_score(self):
        """A glorious charge should call record_diplo_battle."""
        # Saxony -> Hanover (adjacent)
        atk = _make_marshal(name="Murat", location="Saxony", strength=40000,
                            nation="France", cavalry=True)
        atk.recklessness = 10
        dfn = _make_marshal(name="Blucher", location="Hanover", strength=15000, nation="Prussia")

        world = _make_world_with_marshals([atk, dfn])
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "WAR"

        game_state = _make_game_state(world)

        executor = CommandExecutor()
        result = executor.execute(
            _wrap_command("glorious_charge", marshal="Murat", target="Blucher"),
            game_state
        )

        if result.get("success"):
            key = world._make_diplo_key("France", "Prussia")
            records = getattr(world, 'battle_records', {}).get(key, [])
            assert len(records) > 0, "Glorious charge should record battle for war score"
            if records:
                total = records[0]["attacker_casualties"] + records[0]["defender_casualties"]
                assert total > 0, "Should record non-zero casualties"

    def test_glorious_charge_records_correct_winner(self):
        """War score should record correct winner from glorious charge."""
        atk = _make_marshal(name="Murat", location="Saxony", strength=50000,
                            nation="France", cavalry=True)
        atk.recklessness = 10
        dfn = _make_marshal(name="Blucher", location="Hanover", strength=10000, nation="Prussia")

        world = _make_world_with_marshals([atk, dfn])
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "WAR"

        game_state = _make_game_state(world)

        executor = CommandExecutor()
        result = executor.execute(
            _wrap_command("glorious_charge", marshal="Murat", target="Blucher"),
            game_state
        )

        if result.get("success"):
            key = world._make_diplo_key("France", "Prussia")
            records = getattr(world, 'battle_records', {}).get(key, [])
            if records:
                assert records[0]["winner"] == "France"


# ════════════════════════════════════════════════════════════════
# FIX 6: Garrison combat not recorded for war score
# ════════════════════════════════════════════════════════════════

class TestFix6GarrisonWarScore:
    """Garrison combat should record diplomacy war score."""

    def test_garrison_falls_records_war_score(self):
        """When garrison falls, war score should record the attacker as winner."""
        atk = _make_marshal(name="Ney", location="Saxony", strength=50000, nation="France")
        world = _make_world_with_marshals([atk])
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "WAR"

        # Use Berlin (Prussian capital, adjacent to Saxony)
        berlin = world.get_region("Berlin")
        berlin.garrison_strength = 8000  # Weak garrison to ensure it falls
        berlin.controller = "Prussia"

        game_state = _make_game_state(world)
        executor = CommandExecutor()

        result = executor._resolve_garrison_combat(atk, berlin, world, game_state)

        key = world._make_diplo_key("France", "Prussia")
        records = getattr(world, 'battle_records', {}).get(key, [])
        assert len(records) > 0, "Garrison fall should record war score"
        assert records[0]["winner"] == "France"

    def test_garrison_holds_records_war_score(self):
        """When garrison holds, war score should record the defender as winner."""
        atk = _make_marshal(name="Ney", location="Saxony", strength=15000, nation="France")
        world = _make_world_with_marshals([atk])
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "WAR"

        berlin = world.get_region("Berlin")
        berlin.garrison_strength = 80000  # Very strong garrison
        berlin.controller = "Prussia"

        game_state = _make_game_state(world)
        executor = CommandExecutor()

        result = executor._resolve_garrison_combat(atk, berlin, world, game_state)

        key = world._make_diplo_key("France", "Prussia")
        records = getattr(world, 'battle_records', {}).get(key, [])
        assert len(records) > 0, "Garrison hold should record war score"
        assert records[0]["winner"] == "Prussia"


# ════════════════════════════════════════════════════════════════
# FIX 7: Movement engagement treats allies as enemies
# ════════════════════════════════════════════════════════════════

class TestFix7MovementEngagementAllies:
    """Allied nation marshals should not block movement."""

    def test_allied_marshal_doesnt_block_movement(self):
        """Marshal of an allied (non-war) nation in same region shouldn't block movement."""
        # Saxony -> Bavaria (adjacent, not French-controlled)
        french = _make_marshal(name="Ney", location="Saxony", strength=30000, nation="France")
        prussian = _make_marshal(name="Blucher", location="Saxony", strength=25000, nation="Prussia")

        world = _make_world_with_marshals([french, prussian])
        # Override default WAR state to PEACE
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "PEACE"
        game_state = _make_game_state(world)

        executor = CommandExecutor()
        result = executor.execute(
            _wrap_command("move", marshal="Ney", target="Bavaria"),
            game_state
        )
        # Should NOT fail with "engaged with enemy forces"
        if not result.get("success"):
            assert "engaged" not in result.get("message", "").lower(), \
                "Allied marshal should not cause engagement blocking"

    def test_enemy_marshal_blocks_movement(self):
        """Marshal of an enemy (WAR) nation in same region should block movement to non-friendly territory."""
        french = _make_marshal(name="Ney", location="Saxony", strength=30000, nation="France")
        prussian = _make_marshal(name="Blucher", location="Saxony", strength=25000, nation="Prussia")

        world = _make_world_with_marshals([french, prussian])
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "WAR"
        game_state = _make_game_state(world)

        executor = CommandExecutor()
        # Move to Bavaria (non-French controlled, adjacent to Saxony)
        result = executor.execute(
            _wrap_command("move", marshal="Ney", target="Bavaria"),
            game_state
        )
        assert not result.get("success")
        msg = result.get("message", "").lower()
        assert "engaged" in msg or "retreat" in msg

    def test_allied_marshal_at_destination_doesnt_block(self):
        """Allied marshal at destination shouldn't block MOVE (only enemies should)."""
        # Saxony -> Hanover (adjacent)
        french = _make_marshal(name="Ney", location="Saxony", strength=30000, nation="France")
        prussian = _make_marshal(name="Blucher", location="Hanover", strength=25000, nation="Prussia")

        world = _make_world_with_marshals([french, prussian])
        # Override default WAR state to PEACE
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "PEACE"
        game_state = _make_game_state(world)

        executor = CommandExecutor()
        result = executor.execute(
            _wrap_command("move", marshal="Ney", target="Hanover"),
            game_state
        )
        if not result.get("success"):
            msg = result.get("message", "").lower()
            # Should not say "enemy forces" or "must use attack"
            assert not ("enemy" in msg and "attack" in msg), \
                "Allied marshal at destination should not require attack command"


# ════════════════════════════════════════════════════════════════
# FIX 8: Fortified marshal bypasses fortify check via strategic
# ════════════════════════════════════════════════════════════════

class TestFix8FortifiedStrategicBypass:
    """Strategic execution should NOT bypass the fortified check."""

    def test_strategic_move_to_blocked_by_fortification(self):
        """A fortified marshal executing strategic MOVE_TO should be blocked."""
        marshal = _make_marshal(name="Davout", location="Saxony", strength=30000, nation="France")
        marshal.fortified = True

        world = _make_world_with_marshals([marshal])
        game_state = _make_game_state(world)

        executor = CommandExecutor()
        result = executor.execute(
            {"success": True, "command": {
                "marshal": "Davout", "action": "move", "target": "Bavaria",
                "_strategic_execution": True,
            }},
            game_state
        )

        assert not result.get("success")
        assert "fortified" in result.get("message", "").lower()

    def test_strategic_attack_blocked_by_fortification(self):
        """A fortified marshal executing strategic attack should be blocked."""
        marshal = _make_marshal(name="Davout", location="Saxony", strength=30000, nation="France")
        marshal.fortified = True

        enemy = _make_marshal(name="Blucher", location="Saxony", strength=20000, nation="Prussia")

        world = _make_world_with_marshals([marshal, enemy])
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "WAR"
        game_state = _make_game_state(world)

        executor = CommandExecutor()
        result = executor.execute(
            {"success": True, "command": {
                "marshal": "Davout", "action": "attack", "target": "Blucher",
                "_strategic_execution": True,
            }},
            game_state
        )

        assert not result.get("success")
        assert "fortified" in result.get("message", "").lower()


# ════════════════════════════════════════════════════════════════
# FIX 9: DEFEND no-op check in wrong location
# ════════════════════════════════════════════════════════════════

class TestFix9DefendNoOpPreValidation:
    """DEFEND on fortified+defensive marshal should fail BEFORE objection check."""

    def test_defend_fortified_defensive_returns_failure_before_objection(self):
        """Already defensive + fortified -> immediate failure, no objection dialog."""
        marshal = _make_marshal(name="Davout", location="Saxony", strength=30000, nation="France")
        marshal.stance = Stance.DEFENSIVE
        marshal.fortified = True
        marshal.defense_bonus = 0.15

        world = _make_world_with_marshals([marshal])
        game_state = _make_game_state(world)

        executor = CommandExecutor()
        result = executor.execute(
            _wrap_command("defend", marshal="Davout"),
            game_state
        )

        assert not result.get("success")
        assert "already defending" in result.get("message", "").lower()
        assert not getattr(world, 'pending_objection', None)
        assert not getattr(world, 'pending_strategic_objection', None)
