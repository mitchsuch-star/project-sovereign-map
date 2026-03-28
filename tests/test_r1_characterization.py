"""
R1 Characterization Tests: Pin current post-combat behavior BEFORE refactoring.

These tests document what each combat path currently does (and doesn't do)
in its post-combat section. They serve as a safety net during the pipeline
extraction refactor. Tests marked "pin bug" capture known-buggy behavior
that will be intentionally broken when bugs are fixed in Step 8.

Methodology: Characterization Testing (Michael Feathers)
- Pin existing behavior first
- Restructure code (tests stay green)
- Fix bugs (update pinned tests)
"""
from dataclasses import dataclass
from unittest.mock import patch
import pytest
from tests.conftest import MarshalFactory, WorldFactory
from backend.commands.executor import CommandExecutor
from backend.game_logic.combat import CombatResolver
from backend.models.marshal import StrategicOrder


def make_command(action, marshal, target=None):
    cmd = {"action": action, "marshal": marshal}
    if target:
        cmd["target"] = target
    return {"command": cmd}


def _make_full_battle_result(attacker_name, defender_name,
                             outcome="attacker_victory", atk_cas=3000, def_cas=8000,
                             atk_remaining=47000, def_remaining=12000,
                             atk_morale=75, def_morale=20,
                             def_forced_retreat=True):
    """Create a complete battle result dict matching resolve_battle() output."""
    atk_won = "attacker" in outcome and ("victory" in outcome or "wins" in outcome)
    victor = attacker_name if atk_won else defender_name
    return {
        "outcome": outcome,
        "victor": victor,
        "attacker_won": atk_won,
        "raw_outcome": outcome,
        "attacker": {
            "name": attacker_name, "casualties": atk_cas,
            "remaining": atk_remaining, "morale": atk_morale,
            "forced_retreat": False,
        },
        "defender": {
            "name": defender_name, "casualties": def_cas,
            "remaining": def_remaining, "morale": def_morale,
            "forced_retreat": def_forced_retreat,
        },
        "description": f"{attacker_name} defeats {defender_name}.",
        "battle_report": {"observation": "test obs", "modifiers": {}},
        "cavalry_charge_message": "",
        "cavalry_terrain_message": "",
        "cavalry_counter_message": "",
        "counter_punch_message": "",
        "covering_fire_message": "",
        "attacker_nation": "France",
        "defender_nation": "Prussia",
    }


def _setup_war_world(attacker_loc="Paris", defender_loc="Belgium",
                     atk_str=50000, def_str=20000):
    """Set up France vs Prussia with active war, marshals in position."""
    world = WorldFactory.basic()
    world.marshals.clear()
    attacker = MarshalFactory.infantry(
        name="Ney", location=attacker_loc, strength=atk_str, nation="France")
    defender = MarshalFactory.enemy(
        name="Bluecher", location=defender_loc, strength=def_str, nation="Prussia")
    world.marshals["Ney"] = attacker
    world.marshals["Bluecher"] = defender
    key = "|".join(sorted(["France", "Prussia"]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = 1
    belgium = world.get_region("Belgium")
    if belgium:
        belgium.controller = "Prussia"
    return attacker, defender, world


def _count_battle_records(world):
    """Count total battle records across all diplo keys."""
    records = getattr(world, 'battle_records', {})
    return sum(len(v) for v in records.values())


# ═══════════════════════════════════════════════════════════════════════
# PATH 1: _execute_attack (solo)
# ═══════════════════════════════════════════════════════════════════════

class TestAttackPostCombat:
    """Pin _execute_attack post-combat behavior."""

    def test_attack_sets_last_combat_result_on_victory(self):
        """Attacker win sets last_combat_result='victory' on attacker."""
        atk, dfn, world = _setup_war_world()
        executor = CommandExecutor()
        game_state = {"world": world}

        mock_result = _make_full_battle_result("Ney", "Bluecher")
        with patch.object(CombatResolver, 'resolve_battle', return_value=mock_result):
            result = executor.execute(make_command("attack", "Ney", "Bluecher"), game_state)

        assert result["success"]
        ney = world.marshals.get("Ney")
        if ney:
            assert ney.last_combat_result == "victory"

    def test_attack_sets_last_combat_result_on_defender(self):
        """Defender loss sets last_combat_result='defeat' on defender."""
        atk, dfn, world = _setup_war_world()
        executor = CommandExecutor()
        game_state = {"world": world}

        mock_result = _make_full_battle_result("Ney", "Bluecher")
        with patch.object(CombatResolver, 'resolve_battle', return_value=mock_result):
            result = executor.execute(make_command("attack", "Ney", "Bluecher"), game_state)

        assert result["success"]
        bluecher = world.marshals.get("Bluecher")
        if bluecher:
            assert bluecher.last_combat_result == "defeat"

    def test_attack_records_diplo_battle(self):
        """Attack records battle for diplomacy war score."""
        atk, dfn, world = _setup_war_world()
        executor = CommandExecutor()
        game_state = {"world": world}

        mock_result = _make_full_battle_result("Ney", "Bluecher")
        initial_records = _count_battle_records(world)
        with patch.object(CombatResolver, 'resolve_battle', return_value=mock_result):
            result = executor.execute(make_command("attack", "Ney", "Bluecher"), game_state)

        assert result["success"]
        assert _count_battle_records(world) > initial_records

    def test_attack_resets_idle_turns(self):
        """Attack resets idle_turns to 0."""
        atk, dfn, world = _setup_war_world()
        atk.idle_turns = 3
        executor = CommandExecutor()
        game_state = {"world": world}

        mock_result = _make_full_battle_result("Ney", "Bluecher")
        with patch.object(CombatResolver, 'resolve_battle', return_value=mock_result):
            result = executor.execute(make_command("attack", "Ney", "Bluecher"), game_state)

        assert result["success"]
        ney = world.marshals.get("Ney")
        if ney:
            assert ney.idle_turns == 0

    def test_attack_adds_coalition_threat_on_france_win(self):
        """France winning adds coalition threat (+3 minimum)."""
        atk, dfn, world = _setup_war_world()
        executor = CommandExecutor()
        game_state = {"world": world}

        initial_threat = world.threat_level
        mock_result = _make_full_battle_result("Ney", "Bluecher")
        with patch.object(CombatResolver, 'resolve_battle', return_value=mock_result):
            result = executor.execute(make_command("attack", "Ney", "Bluecher"), game_state)

        assert result["success"]
        assert world.threat_level >= initial_threat + 3

    def test_attack_updates_intel(self):
        """Attack updates fog of war intel for battle region."""
        atk, dfn, world = _setup_war_world()
        executor = CommandExecutor()
        game_state = {"world": world}

        mock_result = _make_full_battle_result("Ney", "Bluecher")
        with patch.object(CombatResolver, 'resolve_battle', return_value=mock_result):
            with patch.object(world, 'update_intel_from_battle',
                            wraps=world.update_intel_from_battle) as mock_intel:
                result = executor.execute(make_command("attack", "Ney", "Bluecher"), game_state)

        assert result["success"]
        mock_intel.assert_called()


# ═══════════════════════════════════════════════════════════════════════
# PATH 2: _execute_glorious_charge
# Called directly to avoid the popup/recklessness routing complexity.
# ═══════════════════════════════════════════════════════════════════════

class TestGloriousChargePostCombat:
    """Pin _execute_glorious_charge post-combat behavior."""

    def _setup_charge(self):
        """Cavalry ready for charge — call _execute_glorious_charge directly."""
        world = WorldFactory.basic()
        world.marshals.clear()
        cav = MarshalFactory.cavalry(
            name="Murat", location="Paris", strength=50000, nation="France")
        cav.recklessness = 4  # Will be reset by charge
        target = MarshalFactory.enemy(
            name="Bluecher", location="Belgium", strength=15000, nation="Prussia")
        world.marshals["Murat"] = cav
        world.marshals["Bluecher"] = target
        key = "|".join(sorted(["France", "Prussia"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = 1
        belgium = world.get_region("Belgium")
        if belgium:
            belgium.controller = "Prussia"
        return cav, target, world

    def test_charge_resets_recklessness(self):
        """Glorious charge always resets recklessness to 0."""
        cav, target, world = self._setup_charge()
        executor = CommandExecutor()
        game_state = {"world": world}

        mock_result = _make_full_battle_result("Murat", "Bluecher")
        with patch.object(CombatResolver, 'resolve_battle', return_value=mock_result):
            result = executor._execute_glorious_charge(cav, "Bluecher", world, game_state)

        assert result["success"]
        assert cav.recklessness == 0

    def test_charge_records_diplo_battle(self):
        """Glorious charge records battle for diplomacy."""
        cav, target, world = self._setup_charge()
        executor = CommandExecutor()
        game_state = {"world": world}

        initial_records = _count_battle_records(world)
        mock_result = _make_full_battle_result("Murat", "Bluecher")
        with patch.object(CombatResolver, 'resolve_battle', return_value=mock_result):
            result = executor._execute_glorious_charge(cav, "Bluecher", world, game_state)

        assert result["success"]
        assert _count_battle_records(world) > initial_records

    def test_charge_resets_idle_turns(self):
        """Glorious charge resets idle_turns."""
        cav, target, world = self._setup_charge()
        cav.idle_turns = 5
        executor = CommandExecutor()
        game_state = {"world": world}

        mock_result = _make_full_battle_result("Murat", "Bluecher")
        with patch.object(CombatResolver, 'resolve_battle', return_value=mock_result):
            result = executor._execute_glorious_charge(cav, "Bluecher", world, game_state)

        assert result["success"]
        assert cav.idle_turns == 0

    def test_charge_sets_last_combat_result(self):
        """Bug 3 fixed: glorious charge NOW sets last_combat_result via pipeline."""
        cav, target, world = self._setup_charge()
        executor = CommandExecutor()
        game_state = {"world": world}

        mock_result = _make_full_battle_result("Murat", "Bluecher")
        with patch.object(CombatResolver, 'resolve_battle', return_value=mock_result):
            result = executor._execute_glorious_charge(cav, "Bluecher", world, game_state)

        assert result["success"]
        assert cav.last_combat_result == "victory"

    def test_charge_adds_coalition_threat(self):
        """Glorious charge adds coalition threat for France win."""
        cav, target, world = self._setup_charge()
        executor = CommandExecutor()
        game_state = {"world": world}

        initial_threat = world.threat_level
        mock_result = _make_full_battle_result("Murat", "Bluecher")
        with patch.object(CombatResolver, 'resolve_battle', return_value=mock_result):
            result = executor._execute_glorious_charge(cav, "Bluecher", world, game_state)

        assert result["success"]
        assert world.threat_level >= initial_threat + 3


# ═══════════════════════════════════════════════════════════════════════
# PATH 3: _resolve_garrison_combat
# ═══════════════════════════════════════════════════════════════════════

class TestGarrisonPostCombat:
    """Pin _resolve_garrison_combat post-combat behavior."""

    def _setup_garrison_assault(self, atk_str=60000, garrison_str=8000):
        """Attacker in Saxony attacks Berlin garrison directly."""
        world = WorldFactory.basic()
        world.marshals.clear()
        attacker = MarshalFactory.infantry(
            name="Davout", location="Saxony", strength=atk_str, nation="France")
        world.marshals["Davout"] = attacker
        key = "|".join(sorted(["France", "Prussia"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = 1
        berlin = world.get_region("Berlin")
        if berlin:
            berlin.controller = "Prussia"
            berlin.garrison_strength = garrison_str
        return attacker, world

    def test_garrison_collapse_records_diplo_battle(self):
        """Garrison collapse records battle for diplomacy."""
        # 60k vs 8k garrison — guaranteed collapse
        atk, world = self._setup_garrison_assault(60000, 8000)
        executor = CommandExecutor()
        berlin = world.get_region("Berlin")

        initial_records = _count_battle_records(world)
        result = executor._resolve_garrison_combat(atk, berlin, world, {"world": world})

        assert result["success"]
        assert _count_battle_records(world) > initial_records

    def test_garrison_hold_records_diplo_battle(self):
        """Garrison hold also records battle for diplomacy."""
        # 15k vs 40k garrison — garrison holds
        atk, world = self._setup_garrison_assault(15000, 40000)
        executor = CommandExecutor()
        berlin = world.get_region("Berlin")

        initial_records = _count_battle_records(world)
        result = executor._resolve_garrison_combat(atk, berlin, world, {"world": world})

        assert result["success"]
        assert _count_battle_records(world) > initial_records

    def test_garrison_sets_last_combat_result(self):
        """Bug 3 fixed: garrison NOW sets last_combat_result via pipeline."""
        atk, world = self._setup_garrison_assault(60000, 8000)
        executor = CommandExecutor()
        berlin = world.get_region("Berlin")

        result = executor._resolve_garrison_combat(atk, berlin, world, {"world": world})

        assert result["success"]
        assert atk.last_combat_result == "victory"

    def test_garrison_resets_idle(self):
        """Bug 3 fixed: garrison NOW resets idle_turns via pipeline."""
        atk, world = self._setup_garrison_assault(60000, 8000)
        atk.idle_turns = 5
        executor = CommandExecutor()
        berlin = world.get_region("Berlin")

        result = executor._resolve_garrison_combat(atk, berlin, world, {"world": world})

        assert result["success"]
        assert atk.idle_turns == 0

    def test_garrison_collapse_adds_threat(self):
        """Garrison collapse adds coalition threat for France."""
        atk, world = self._setup_garrison_assault(60000, 8000)
        executor = CommandExecutor()
        berlin = world.get_region("Berlin")

        initial_threat = world.threat_level
        result = executor._resolve_garrison_combat(atk, berlin, world, {"world": world})

        assert result["success"]
        # France wins garrison — should get +3 (battle_win)
        assert world.threat_level >= initial_threat + 3


# ═══════════════════════════════════════════════════════════════════════
# PATH 4: _execute_bombardment (called directly, like existing tests)
# ═══════════════════════════════════════════════════════════════════════

class TestBombardmentPostCombat:
    """Pin _execute_bombardment post-combat behavior."""

    def _setup_bombardment(self):
        """Artillery in Belgium bombards defender in Waterloo."""
        world = WorldFactory.basic()
        world.marshals.clear()
        art = MarshalFactory.artillery(
            name="Drouot", location="Belgium", strength=10000, nation="France")
        target = MarshalFactory.enemy(
            name="Wellington", location="Waterloo", strength=30000, nation="Britain")
        world.marshals["Drouot"] = art
        world.marshals["Wellington"] = target
        key = "|".join(sorted(["Britain", "France"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = 1
        waterloo = world.get_region("Waterloo")
        if waterloo:
            waterloo.controller = "Britain"
        return art, target, world

    def test_bombardment_records_cannon_fire(self):
        """Bombardment records battle for cannon fire detection."""
        art, target, world = self._setup_bombardment()
        executor = CommandExecutor()
        game_state = {"world": world}

        result = executor._execute_bombardment(art, target, world, game_state)

        assert result["success"]
        battles = getattr(world, 'battles_this_turn', [])
        assert len(battles) > 0

    def test_bombardment_resets_idle(self):
        """Bombardment resets idle_turns."""
        art, target, world = self._setup_bombardment()
        art.idle_turns = 4
        executor = CommandExecutor()
        game_state = {"world": world}

        result = executor._execute_bombardment(art, target, world, game_state)

        assert result["success"]
        assert art.idle_turns == 0

    def test_bombardment_records_diplo_battle(self):
        """Bug 5 fixed: bombardment NOW records diplomacy battle via pipeline."""
        art, target, world = self._setup_bombardment()
        executor = CommandExecutor()
        game_state = {"world": world}

        initial_records = _count_battle_records(world)
        result = executor._execute_bombardment(art, target, world, game_state)

        assert result["success"]
        assert _count_battle_records(world) > initial_records

    def test_bombardment_does_not_add_coalition_threat(self):
        """Pin: bombardment does NOT add coalition threat."""
        art, target, world = self._setup_bombardment()
        executor = CommandExecutor()
        game_state = {"world": world}

        initial_threat = world.threat_level
        result = executor._execute_bombardment(art, target, world, game_state)

        assert result["success"]
        assert world.threat_level == initial_threat

    def test_bombardment_does_not_set_last_combat_result(self):
        """Pin: bombardment does NOT set last_combat_result."""
        art, target, world = self._setup_bombardment()
        executor = CommandExecutor()
        game_state = {"world": world}

        result = executor._execute_bombardment(art, target, world, game_state)

        assert result["success"]
        assert getattr(art, 'last_combat_result', None) is None

    def test_bombardment_updates_intel(self):
        """Bombardment updates fog of war intel."""
        art, target, world = self._setup_bombardment()
        executor = CommandExecutor()
        game_state = {"world": world}

        with patch.object(world, 'update_intel_from_battle',
                         wraps=world.update_intel_from_battle) as mock_intel:
            result = executor._execute_bombardment(art, target, world, game_state)

        assert result["success"]
        mock_intel.assert_called()


# ═══════════════════════════════════════════════════════════════════════
# PATH 5: Auto-bombardment kill (within _execute_attack)
# ═══════════════════════════════════════════════════════════════════════

class TestAutoBombardmentKillPostCombat:
    """Pin auto-bombardment kill post-combat behavior."""

    def _setup_auto_kill_scenario(self):
        """Set up weak defender that auto-bombardment should kill."""
        world = WorldFactory.basic()
        world.marshals.clear()

        attacker = MarshalFactory.infantry(
            name="Ney", location="Paris", strength=40000, nation="France")
        # Very weak defender — auto-bombardment does ~4% * multiplier damage
        # With 10k artillery (shock=7), damage = strength*0.04*1.467*terrain ≈ 5.9% of defender
        # Need defender so weak that single bombardment kills: set to 50
        defender = MarshalFactory.enemy(
            name="Bluecher", location="Belgium", strength=50, nation="Prussia")
        # Artillery on SUPPORT order
        art = MarshalFactory.artillery(
            name="Drouot", location="Paris", strength=10000, nation="France")
        art.strategic_order = StrategicOrder(
            command_type="SUPPORT",
            target="Ney",
            target_type="marshal",
            started_turn=1,
            original_command="Drouot, support Ney",
        )

        world.marshals["Ney"] = attacker
        world.marshals["Bluecher"] = defender
        world.marshals["Drouot"] = art

        key = "|".join(sorted(["France", "Prussia"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = 1
        belgium = world.get_region("Belgium")
        if belgium:
            belgium.controller = "Prussia"
        return attacker, defender, art, world

    def test_auto_kill_removes_defender(self):
        """Auto-bombardment kill removes defender from world."""
        atk, dfn, art, world = self._setup_auto_kill_scenario()
        executor = CommandExecutor()
        game_state = {"world": world}

        result = executor.execute(make_command("attack", "Ney", "Bluecher"), game_state)

        assert result["success"]
        # Defender should be destroyed by auto-bombardment
        assert "Bluecher" not in world.marshals

    def test_auto_kill_records_diplo_with_actual_casualties(self):
        """Bug 2 fixed: auto-kill uses actual bombardment damage, not full pre-battle strength.

        With a 50-troop defender, actual casualties are ~50 (the bombardment damage),
        well below the 1000 threshold, so no diplo record. This is CORRECT behavior —
        Bug 2 was that larger battles would inflate war score with pre-battle strength.
        """
        atk, dfn, art, world = self._setup_auto_kill_scenario()
        executor = CommandExecutor()
        game_state = {"world": world}

        initial_records = _count_battle_records(world)
        result = executor.execute(make_command("attack", "Ney", "Bluecher"), game_state)

        assert result["success"]
        assert "Bluecher" not in world.marshals
        # Actual casualties ~50, below 1000 threshold — no record (correct)
        assert _count_battle_records(world) == initial_records

    def test_auto_kill_adds_coalition_threat_proportional(self):
        """Bug 1 fixed: auto-kill threat is proportional, not unconditional decisive_victory.

        With a 50-troop defender, casualties are tiny (<10000 total) so
        decisive_victory bonus (+5) should NOT trigger. Only base +3 (battle_win).
        """
        atk, dfn, art, world = self._setup_auto_kill_scenario()
        executor = CommandExecutor()
        game_state = {"world": world}

        initial_threat = world.threat_level
        result = executor.execute(make_command("attack", "Ney", "Bluecher"), game_state)

        assert result["success"]
        assert "Bluecher" not in world.marshals
        # Pipeline properly checks casualty ratio — tiny battle gets +3 only, not +8
        assert world.threat_level >= initial_threat + 3
        assert world.threat_level < initial_threat + 8
