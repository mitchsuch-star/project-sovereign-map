"""
R1 Pipeline Enforcement Tests: Verify _post_combat_pipeline directly.

These tests call the pipeline method in isolation to verify each of the 14 steps
works correctly and that skip flags properly gate each step. They complement
the characterization tests (which verify end-to-end behavior through each path).

Session 2B of Architecture Refactoring Plan.
"""
import pytest
from tests.conftest import MarshalFactory, WorldFactory
from backend.commands.executor import CommandExecutor


def _make_basic_ctx(world, **overrides):
    """Create a minimal valid pipeline context."""
    attacker = world.marshals.get("Ney")
    defender = world.marshals.get("Bluecher")
    ctx = {
        'attacker': attacker,
        'defender': defender,
        'defender_nation': 'Prussia',
        'battle_region': 'Belgium',
        'outcome': 'attacker_victory',
        'attacker_won': True,
        'defender_won': False,
        'attacker_casualties': 3000,
        'defender_casualties': 8000,
        'pre_battle_attacker_strength': 50000,
        'pre_battle_defender_strength': 20000,
        'battle_result': {
            'outcome': 'attacker_victory',
            'attacker_won': True,
            'attacker': {'name': 'Ney', 'casualties': 3000, 'remaining': 47000,
                         'morale': 75, 'forced_retreat': True},
            'defender': {'name': 'Bluecher', 'casualties': 8000, 'remaining': 12000,
                         'morale': 20, 'forced_retreat': True},
            'victor': 'Ney',
            'raw_outcome': 'attacker_victory',
            'attacker_nation': 'France',
            'defender_nation': 'Prussia',
        },
        'conquered': False,
    }
    ctx.update(overrides)
    return ctx


def _setup_war_world():
    """France vs Prussia at war, Ney vs Bluecher."""
    world = WorldFactory.basic()
    world.marshals.clear()
    attacker = MarshalFactory.infantry(
        name="Ney", location="Paris", strength=50000, nation="France")
    defender = MarshalFactory.enemy(
        name="Bluecher", location="Belgium", strength=20000, nation="Prussia")
    world.marshals["Ney"] = attacker
    world.marshals["Bluecher"] = defender
    key = "|".join(sorted(["France", "Prussia"]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = 1
    belgium = world.get_region("Belgium")
    if belgium:
        belgium.controller = "Prussia"
    return world


# ═══════════════════════════════════════════════════════════════════════
# STEP 6: Idle reset
# ═══════════════════════════════════════════════════════════════════════

class TestPipelineIdleReset:
    """Step 6: idle_turns reset to 0."""

    def test_resets_idle_turns(self):
        world = _setup_war_world()
        world.marshals["Ney"].idle_turns = 5
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world)
        executor._post_combat_pipeline(ctx, world)
        assert world.marshals["Ney"].idle_turns == 0

    def test_skip_idle_reset(self):
        world = _setup_war_world()
        world.marshals["Ney"].idle_turns = 5
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world, skip_idle_reset=True)
        executor._post_combat_pipeline(ctx, world)
        assert world.marshals["Ney"].idle_turns == 5


# ═══════════════════════════════════════════════════════════════════════
# STEP 7: Cannon fire record
# ═══════════════════════════════════════════════════════════════════════

class TestPipelineCannonFireRecord:
    """Step 7: battles_this_turn record for cannon fire detection."""

    def test_records_battle(self):
        world = _setup_war_world()
        initial = len(getattr(world, 'battles_this_turn', []))
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world)
        executor._post_combat_pipeline(ctx, world)
        assert len(world.battles_this_turn) > initial

    def test_skip_cannon_fire(self):
        world = _setup_war_world()
        initial = len(getattr(world, 'battles_this_turn', []))
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world, skip_cannon_fire_record=True)
        executor._post_combat_pipeline(ctx, world)
        assert len(getattr(world, 'battles_this_turn', [])) == initial


# ═══════════════════════════════════════════════════════════════════════
# STEP 8: Diplomacy war score record
# ═══════════════════════════════════════════════════════════════════════

def _count_battle_records(world):
    records = getattr(world, 'battle_records', {})
    return sum(len(v) for v in records.values())


class TestPipelineDiploRecord:
    """Step 8: battle_records for war score calculation."""

    def test_records_diplo_battle_on_attacker_win(self):
        world = _setup_war_world()
        initial = _count_battle_records(world)
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world)
        executor._post_combat_pipeline(ctx, world)
        assert _count_battle_records(world) > initial

    def test_records_diplo_battle_on_defender_win(self):
        world = _setup_war_world()
        initial = _count_battle_records(world)
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world, attacker_won=False, defender_won=True,
                              outcome='defender_victory')
        executor._post_combat_pipeline(ctx, world)
        assert _count_battle_records(world) > initial

    def test_skip_diplo_record(self):
        world = _setup_war_world()
        initial = _count_battle_records(world)
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world, skip_diplo_record=True)
        executor._post_combat_pipeline(ctx, world)
        assert _count_battle_records(world) == initial

    def test_bombardment_records_diplo(self):
        """Bombardment (is_bombardment=True) still records diplo when not skipped."""
        world = _setup_war_world()
        initial = _count_battle_records(world)
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world, is_bombardment=True)
        executor._post_combat_pipeline(ctx, world)
        assert _count_battle_records(world) > initial


# ═══════════════════════════════════════════════════════════════════════
# STEP 9: last_combat_result
# ═══════════════════════════════════════════════════════════════════════

class TestPipelineLastCombatResult:
    """Step 9: last_combat_result on attacker and defender."""

    def test_sets_victory_on_attacker_win(self):
        world = _setup_war_world()
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world)
        executor._post_combat_pipeline(ctx, world)
        assert world.marshals["Ney"].last_combat_result == "victory"
        assert world.marshals["Bluecher"].last_combat_result == "defeat"

    def test_sets_defeat_on_defender_win(self):
        world = _setup_war_world()
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world, attacker_won=False, defender_won=True,
                              outcome='defender_victory')
        executor._post_combat_pipeline(ctx, world)
        assert world.marshals["Ney"].last_combat_result == "defeat"
        assert world.marshals["Bluecher"].last_combat_result == "victory"

    def test_sets_stalemate_on_draw(self):
        world = _setup_war_world()
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world, attacker_won=False, defender_won=False,
                              outcome='stalemate')
        executor._post_combat_pipeline(ctx, world)
        assert world.marshals["Ney"].last_combat_result == "stalemate"
        assert world.marshals["Bluecher"].last_combat_result == "stalemate"

    def test_skip_last_combat_result(self):
        world = _setup_war_world()
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world, skip_last_combat_result=True)
        executor._post_combat_pipeline(ctx, world)
        assert getattr(world.marshals["Ney"], 'last_combat_result', None) is None

    def test_bombardment_skips_last_combat_result(self):
        """Bombardment does not set last_combat_result."""
        world = _setup_war_world()
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world, is_bombardment=True)
        executor._post_combat_pipeline(ctx, world)
        assert getattr(world.marshals["Ney"], 'last_combat_result', None) is None

    def test_garrison_sets_last_combat_result(self):
        """Garrison combat sets last_combat_result (Bug 3 fix)."""
        world = _setup_war_world()
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world, is_garrison=True, defender=None)
        executor._post_combat_pipeline(ctx, world)
        assert world.marshals["Ney"].last_combat_result == "victory"


# ═══════════════════════════════════════════════════════════════════════
# STEP 11: Vindication
# ═══════════════════════════════════════════════════════════════════════

class TestPipelineVindication:
    """Step 11: vindication resolution."""

    def test_resolves_pending_vindication_on_win(self):
        world = _setup_war_world()
        world.vindication_tracker.pending["Ney"] = {
            "concern": "Reckless orders",
            "turn": world.current_turn,
            "action": "attack",
            "target": "Bluecher",
            "choice": "proceed",
        }
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world)
        executor._post_combat_pipeline(ctx, world)
        assert not world.vindication_tracker.has_pending("Ney")

    def test_bombardment_skips_vindication(self):
        """Bombardment does not resolve vindication."""
        world = _setup_war_world()
        world.vindication_tracker.pending["Ney"] = {
            "concern": "Reckless orders",
            "turn": world.current_turn,
            "action": "attack",
            "target": "Bluecher",
            "choice": "proceed",
        }
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world, is_bombardment=True)
        executor._post_combat_pipeline(ctx, world)
        assert world.vindication_tracker.has_pending("Ney")

    def test_vindication_msg_in_output(self):
        world = _setup_war_world()
        world.vindication_tracker.pending["Ney"] = {
            "concern": "Reckless orders",
            "turn": world.current_turn,
            "action": "attack",
            "target": "Bluecher",
            "choice": "proceed",
        }
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world)
        out = executor._post_combat_pipeline(ctx, world)
        assert out['vindication_msg'] != ''


# ═══════════════════════════════════════════════════════════════════════
# STEP 12: Authority
# ═══════════════════════════════════════════════════════════════════════

class TestPipelineAuthority:
    """Step 12: authority for major victory/defeat."""

    def test_outnumbered_win_grants_authority(self):
        """Attacker wins while outnumbered → +5 authority."""
        world = _setup_war_world()
        world.authority_tracker.authority = 80  # Below cap so +5 is visible
        initial = world.authority_tracker.authority
        executor = CommandExecutor()
        # Attacker 30k vs defender 50k — outnumbered
        ctx = _make_basic_ctx(world,
                              pre_battle_attacker_strength=30000,
                              pre_battle_defender_strength=50000)
        executor._post_combat_pipeline(ctx, world)
        assert world.authority_tracker.authority == initial + 5

    def test_outnumbering_loss_costs_authority(self):
        """Player loses while outnumbering → -5 authority."""
        world = _setup_war_world()
        initial = world.authority_tracker.authority
        executor = CommandExecutor()
        # Attacker (France) 50k vs defender 30k, France LOSES
        ctx = _make_basic_ctx(world,
                              attacker_won=False, defender_won=True,
                              outcome='defender_victory',
                              pre_battle_attacker_strength=50000,
                              pre_battle_defender_strength=30000)
        executor._post_combat_pipeline(ctx, world)
        assert world.authority_tracker.authority == initial - 5

    def test_bombardment_skips_authority(self):
        """Bombardment does not affect authority."""
        world = _setup_war_world()
        initial = world.authority_tracker.authority
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world, is_bombardment=True,
                              pre_battle_attacker_strength=30000,
                              pre_battle_defender_strength=50000)
        executor._post_combat_pipeline(ctx, world)
        assert world.authority_tracker.authority == initial

    def test_garrison_skips_authority(self):
        """Garrison uses custom inline authority, pipeline skips."""
        world = _setup_war_world()
        initial = world.authority_tracker.authority
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world, is_garrison=True, defender=None,
                              pre_battle_attacker_strength=30000,
                              pre_battle_defender_strength=50000)
        executor._post_combat_pipeline(ctx, world)
        assert world.authority_tracker.authority == initial


# ═══════════════════════════════════════════════════════════════════════
# STEP 13: Coalition threat
# ═══════════════════════════════════════════════════════════════════════

class TestPipelineCoalition:
    """Step 13: coalition threat and war exhaustion."""

    def test_france_win_adds_battle_threat(self):
        """France attacking + winning → +3 battle_win threat."""
        world = _setup_war_world()
        initial = world.threat_level
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world)
        executor._post_combat_pipeline(ctx, world)
        assert world.threat_level >= initial + 3

    def test_decisive_victory_adds_extra_threat(self):
        """2:1+ ratio with >10k total casualties → +5 decisive bonus."""
        world = _setup_war_world()
        initial = world.threat_level
        executor = CommandExecutor()
        # 3k atk vs 12k def casualties, ratio=4, total=15k → decisive
        ctx = _make_basic_ctx(world,
                              attacker_casualties=3000,
                              defender_casualties=12000)
        executor._post_combat_pipeline(ctx, world)
        assert world.threat_level >= initial + 8  # +3 battle + +5 decisive

    def test_tiny_battle_no_decisive(self):
        """Bug 1 fix: small casualties don't trigger decisive_victory."""
        world = _setup_war_world()
        initial = world.threat_level
        executor = CommandExecutor()
        # 50 atk vs 200 def — ratio fine but total < 10k
        ctx = _make_basic_ctx(world,
                              attacker_casualties=50,
                              defender_casualties=200)
        executor._post_combat_pipeline(ctx, world)
        # Only +3, no +5 decisive
        assert world.threat_level >= initial + 3
        assert world.threat_level < initial + 8

    def test_bombardment_skips_coalition(self):
        """Bombardment does not affect coalition threat."""
        world = _setup_war_world()
        initial = world.threat_level
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world, is_bombardment=True)
        executor._post_combat_pipeline(ctx, world)
        assert world.threat_level == initial

    def test_defender_win_adds_exhaustion_to_france(self):
        """France losing adds war exhaustion to France."""
        world = _setup_war_world()
        initial_we = world.war_exhaustion.get("France", 0)
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world, attacker_won=False, defender_won=True,
                              outcome='defender_victory',
                              attacker_casualties=8000)
        executor._post_combat_pipeline(ctx, world)
        assert world.war_exhaustion.get("France", 0) > initial_we

    def test_capital_capture_adds_threat(self):
        """Capturing a capital adds +15 capital_capture threat."""
        world = _setup_war_world()
        # Set Berlin as a capital and mark conquered
        berlin = world.get_region("Berlin")
        if berlin:
            berlin.controller = "France"  # captured
        initial = world.threat_level
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world, conquered=True, battle_region='Berlin')
        executor._post_combat_pipeline(ctx, world)
        # +3 battle_win + +15 capital_capture = +18
        assert world.threat_level >= initial + 18


# ═══════════════════════════════════════════════════════════════════════
# Return value structure
# ═══════════════════════════════════════════════════════════════════════

class TestPipelineReturnValue:
    """Pipeline returns expected dict structure."""

    def test_returns_vindication_msg(self):
        world = _setup_war_world()
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world)
        out = executor._post_combat_pipeline(ctx, world)
        assert 'vindication_msg' in out
        assert isinstance(out['vindication_msg'], str)

    def test_returns_relationship_changes(self):
        world = _setup_war_world()
        executor = CommandExecutor()
        ctx = _make_basic_ctx(world)
        out = executor._post_combat_pipeline(ctx, world)
        assert 'relationship_changes' in out
        assert isinstance(out['relationship_changes'], list)


# ═══════════════════════════════════════════════════════════════════════
# Skip flag coverage — verify all skip flags work
# ═══════════════════════════════════════════════════════════════════════

class TestPipelineSkipFlags:
    """Every skip flag properly gates its step."""

    def test_all_skipped_does_nothing(self):
        """With all skip flags set, pipeline should barely modify state."""
        world = _setup_war_world()
        world.marshals["Ney"].idle_turns = 5
        initial_threat = world.threat_level
        initial_battles = len(getattr(world, 'battles_this_turn', []))
        initial_records = _count_battle_records(world)

        executor = CommandExecutor()
        ctx = _make_basic_ctx(world,
                              is_bombardment=True,  # skips vindication, authority, coalition, last_combat_result
                              skip_coordination_clear=True,
                              skip_log_battle_event=True,
                              skip_combat_notifications=True,
                              skip_intel_update=True,
                              skip_war_damage=True,
                              skip_idle_reset=True,
                              skip_cannon_fire_record=True,
                              skip_diplo_record=True,
                              skip_last_combat_result=True,
                              skip_relationships=True,
                              skip_exhaustion=True)
        executor._post_combat_pipeline(ctx, world)

        assert world.marshals["Ney"].idle_turns == 5
        assert world.threat_level == initial_threat
        assert len(getattr(world, 'battles_this_turn', [])) == initial_battles
        assert _count_battle_records(world) == initial_records
        assert getattr(world.marshals["Ney"], 'last_combat_result', None) is None
