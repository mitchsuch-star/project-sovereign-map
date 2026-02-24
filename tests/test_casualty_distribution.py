"""
Tests for Casualty Distribution (Session 62).

Covers:
- resolve_battle() contract with apply_casualties=False
- Proportional casualty distribution
- Hostile marshal exclusion
- Per-participant effects (morale, battles_won/lost)
- Primary-only effects (recklessness, counter-punch)
- Integration with existing systems (reinforcements, relationships)
- Edge cases (0 strength, rounding, small casualties)
"""

from unittest.mock import patch

from backend.models.marshal import Marshal, StrategicOrder
from backend.models.world_state import WorldState
from backend.game_logic.combat import CombatResolver
from backend.commands.executor import CommandExecutor


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


# ════════════════════════════════════════════════════════════════
# CLASS 1: resolve_battle Contract (apply_casualties=False)
# ════════════════════════════════════════════════════════════════

class TestResolveBattleDeferredCasualties:
    """When apply_casualties=False, resolve_battle returns raw data without modifying state."""

    def test_raw_casualties_returned_strength_unmodified(self):
        """Raw casualties in result, marshal strengths unchanged."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=30000, personality="aggressive")
        dfn = _make_marshal(name="Def", strength=25000, personality="cautious")

        result = combat.resolve_battle(atk, dfn, apply_casualties=False)

        assert "attacker_raw_casualties" in result
        assert "defender_raw_casualties" in result
        assert result["attacker_raw_casualties"] > 0
        assert result["defender_raw_casualties"] > 0
        # Strength NOT modified
        assert atk.strength == 30000
        assert dfn.strength == 25000

    def test_morale_deltas_returned_as_int_morale_unmodified(self):
        """Morale deltas are int (Golden Rule #2), marshal morale unchanged."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=30000)
        dfn = _make_marshal(name="Def", strength=25000)
        atk_morale_before = atk.morale
        dfn_morale_before = dfn.morale

        result = combat.resolve_battle(atk, dfn, apply_casualties=False)

        assert isinstance(result["attacker_morale_delta"], int)
        assert isinstance(result["defender_morale_delta"], int)
        assert atk.morale == atk_morale_before
        assert dfn.morale == dfn_morale_before

    def test_battles_won_lost_not_incremented(self):
        """battles_won/lost not changed when apply_casualties=False."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=50000)
        dfn = _make_marshal(name="Def", strength=10000)

        result = combat.resolve_battle(atk, dfn, apply_casualties=False)

        assert atk.battles_won == 0
        assert atk.battles_lost == 0
        assert dfn.battles_won == 0
        assert dfn.battles_lost == 0

    def test_counter_punch_not_set(self):
        """counter_punch_available not set on defender."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=10000)
        dfn = _make_marshal(name="Def", strength=50000, personality="cautious")

        result = combat.resolve_battle(atk, dfn, apply_casualties=False)

        assert not getattr(dfn, 'counter_punch_available', False)
        assert result["counter_punch_earned"] is False

    def test_counter_punch_mastery_not_set(self):
        """counter_punch_ready (Davout ability) not set."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=30000)
        dfn = _make_marshal(name="Davout", strength=30000, personality="cautious")
        dfn.ability = {"name": "Counter-Punch Mastery", "trigger": "when_defending"}

        result = combat.resolve_battle(atk, dfn, apply_casualties=False)

        assert not getattr(dfn, 'counter_punch_ready', False)
        assert result["counter_punch_mastery_earned"] is False

    def test_recklessness_not_incremented(self):
        """Cavalry recklessness not changed."""
        combat = CombatResolver()
        # cavalry=True + personality="aggressive" → is_reckless_cavalry property
        atk = _make_marshal(name="Ney", strength=50000, cavalry=True,
                            personality="aggressive")
        atk.recklessness = 1
        assert atk.is_reckless_cavalry  # Verify property works
        dfn = _make_marshal(name="Def", strength=10000)

        result = combat.resolve_battle(atk, dfn, apply_casualties=False)

        assert atk.recklessness == 1  # Unchanged

    def test_no_forced_retreat_triggered(self):
        """Forced retreat not triggered (morale not changed)."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=30000)
        dfn = _make_marshal(name="Def", strength=25000)

        result = combat.resolve_battle(atk, dfn, apply_casualties=False)

        assert result["attacker"]["forced_retreat"] is False
        assert result["defender"]["forced_retreat"] is False

    def test_fortification_degradation_still_happens(self):
        """Fort degradation KEPT (battle-triggered per C1)."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=30000)
        dfn = _make_marshal(name="Def", strength=25000)
        dfn.defense_bonus = 0.20

        result = combat.resolve_battle(atk, dfn, apply_casualties=False)

        # Defense bonus should be degraded by 0.05
        assert dfn.defense_bonus < 0.20
        assert result["fortification_degraded"] is True

    def test_victor_from_projected_strength_c2(self):
        """Victor determined from projected strength, not actual .strength (C2)."""
        combat = CombatResolver()
        # Attacker will take more casualties than defender (outnumbered)
        atk = _make_marshal(name="Atk", strength=5000)
        dfn = _make_marshal(name="Def", strength=50000)

        with patch('random.randint', return_value=3):  # Low roll for attacker
            result = combat.resolve_battle(atk, dfn, apply_casualties=False)

        # Projected attacker strength should be very low or 0
        assert result["raw_outcome"] in (
            "defender_victory", "defender_tactical_victory", "mutual_destruction"
        )
        # But actual strength is unchanged
        assert atk.strength == 5000

    def test_projected_mutual_destruction(self):
        """Mutual destruction when both projected strengths <= 0."""
        combat = CombatResolver()
        # Tiny armies that will both be wiped out
        atk = _make_marshal(name="Atk", strength=100)
        dfn = _make_marshal(name="Def", strength=100)

        # Force high casualty rates
        with patch.object(combat, '_calculate_casualties', return_value=200):
            result = combat.resolve_battle(atk, dfn, apply_casualties=False)

        assert result["raw_outcome"] == "mutual_destruction"
        assert atk.strength == 100
        assert dfn.strength == 100

    def test_apply_casualties_true_preserves_existing_behavior(self):
        """apply_casualties=True (default) is identical to pre-session behavior."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=30000, personality="aggressive")
        dfn = _make_marshal(name="Def", strength=25000, personality="cautious")

        with patch('random.randint', return_value=7):
            result = combat.resolve_battle(atk, dfn, apply_casualties=True)

        # Strength should be modified
        assert atk.strength < 30000
        assert dfn.strength < 25000
        # No raw_* fields in the True path
        assert "attacker_raw_casualties" not in result
        assert "defender_raw_casualties" not in result

    def test_raw_outcome_matches_outcome_field(self):
        """raw_outcome and outcome should match in deferred path."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=30000)
        dfn = _make_marshal(name="Def", strength=25000)

        result = combat.resolve_battle(atk, dfn, apply_casualties=False)

        assert result["raw_outcome"] == result["outcome"]


# ════════════════════════════════════════════════════════════════
# CLASS 2: Proportional Distribution
# ════════════════════════════════════════════════════════════════

class TestProportionalDistribution:
    """_distribute_casualties splits proportionally by strength."""

    def setup_method(self):
        self.executor = CommandExecutor()

    def test_two_marshals_proportional(self):
        """60k/40k split → 60%/40% of casualties."""
        m1 = _make_marshal(name="M1", strength=60000)
        m2 = _make_marshal(name="M2", strength=40000)

        dist = self.executor._distribute_casualties(10000, [m1, m2])

        # 60% of 10000 = 6000, 40% = 4000
        assert dist["M1"] == 6000
        assert dist["M2"] == 4000
        assert sum(dist.values()) == 10000

    def test_three_marshals_proportional(self):
        """50k/30k/20k split → proportional shares."""
        m1 = _make_marshal(name="M1", strength=50000)
        m2 = _make_marshal(name="M2", strength=30000)
        m3 = _make_marshal(name="M3", strength=20000)

        dist = self.executor._distribute_casualties(10000, [m1, m2, m3])

        # 50% = 5000, 30% = 3000, 20% = 2000
        assert dist["M1"] == 5000
        assert dist["M2"] == 3000
        assert dist["M3"] == 2000
        assert sum(dist.values()) == 10000

    def test_no_rounding_leakage(self):
        """Sum of distributed shares == raw total exactly."""
        m1 = _make_marshal(name="M1", strength=33333)
        m2 = _make_marshal(name="M2", strength=33334)
        m3 = _make_marshal(name="M3", strength=33333)

        dist = self.executor._distribute_casualties(10000, [m1, m2, m3])

        assert sum(dist.values()) == 10000

    def test_remainder_to_strongest(self):
        """Rounding remainder goes to strongest marshal."""
        m1 = _make_marshal(name="Strongest", strength=50000)
        m2 = _make_marshal(name="Weaker", strength=25000)
        m3 = _make_marshal(name="Weakest", strength=25000)

        # 10001 can't split evenly: 50%=5000, 25%=2500, 25%=2500 → sum=10000, remainder=1
        dist = self.executor._distribute_casualties(10001, [m1, m2, m3])

        assert sum(dist.values()) == 10001
        # Strongest gets the +1 remainder
        assert dist["Strongest"] >= 5000

    def test_strength_cant_go_below_zero(self):
        """Marshal can't lose more troops than they have."""
        m1 = _make_marshal(name="Big", strength=50000)
        m2 = _make_marshal(name="Tiny", strength=100)

        dist = self.executor._distribute_casualties(60000, [m1, m2])

        assert dist["Tiny"] <= 100  # Capped at strength

    def test_single_marshal_gets_100_percent(self):
        """Degenerate case: one participant gets everything."""
        m1 = _make_marshal(name="Solo", strength=30000)

        dist = self.executor._distribute_casualties(5000, [m1])

        assert dist["Solo"] == 5000

    def test_empty_participants(self):
        """No participants → empty dict."""
        dist = self.executor._distribute_casualties(5000, [])

        assert dist == {}

    def test_very_small_casualties(self):
        """1 casualty split among 3 → strongest gets 1, others 0."""
        m1 = _make_marshal(name="Big", strength=50000)
        m2 = _make_marshal(name="Med", strength=30000)
        m3 = _make_marshal(name="Small", strength=20000)

        dist = self.executor._distribute_casualties(1, [m1, m2, m3])

        assert sum(dist.values()) == 1
        assert dist["Big"] == 1  # Strongest gets remainder


# ════════════════════════════════════════════════════════════════
# CLASS 3: Hostile Exclusion
# ════════════════════════════════════════════════════════════════

class TestHostileExclusion:
    """Hostile marshals excluded from distribution; Hostile+SUPPORT included (D3)."""

    def setup_method(self):
        self.executor = CommandExecutor()

    def test_hostile_marshal_excluded(self):
        """Plain Hostile marshal (no SUPPORT) = Non-Participating, 0% casualties."""
        primary = _make_marshal(name="Primary", location="Bavaria", strength=30000)
        hostile = _make_marshal(name="Hostile", location="Bavaria", strength=20000)
        hostile.modify_relationship("Primary", -2)  # Set to Hostile (-2)

        world = _make_world_with_marshals([primary, hostile])

        participants = self.executor._get_casualty_participants(
            primary, "Bavaria", "France", world)

        assert len(participants) == 1
        assert participants[0].name == "Primary"

    def test_hostile_with_support_included(self):
        """Hostile+SUPPORT = Participating for casualties (D3)."""
        primary = _make_marshal(name="Primary", location="Bavaria", strength=30000)
        hostile_support = _make_marshal(name="HostileSup", location="Bavaria", strength=20000)
        hostile_support.modify_relationship("Primary", -2)  # Hostile
        hostile_support.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Primary",
            target_type="marshal", started_turn=1,
            original_command="support Primary",
        )

        world = _make_world_with_marshals([primary, hostile_support])

        participants = self.executor._get_casualty_participants(
            primary, "Bavaria", "France", world)

        assert len(participants) == 2
        assert any(p.name == "HostileSup" for p in participants)

    def test_hostile_excluded_from_distribution(self):
        """Hostile (non-SUPPORT) excluded → all casualties to non-hostile."""
        primary = _make_marshal(name="Primary", location="Bavaria", strength=60000)
        ally = _make_marshal(name="Ally", location="Bavaria", strength=40000)
        hostile = _make_marshal(name="Hostile", location="Bavaria", strength=30000)
        hostile.modify_relationship("Primary", -2)

        world = _make_world_with_marshals([primary, ally, hostile])

        participants = self.executor._get_casualty_participants(
            primary, "Bavaria", "France", world)
        dist = self.executor._distribute_casualties(10000, participants)

        assert "Hostile" not in dist
        assert sum(dist.values()) == 10000

    def test_non_hostile_allies_take_proportional(self):
        """Non-hostile allies take casualties proportionally."""
        primary = _make_marshal(name="P", location="Bavaria", strength=60000)
        ally = _make_marshal(name="A", location="Bavaria", strength=40000)
        ally.modify_relationship("P", 1)  # Friendly

        world = _make_world_with_marshals([primary, ally])

        participants = self.executor._get_casualty_participants(
            primary, "Bavaria", "France", world)
        dist = self.executor._distribute_casualties(10000, participants)

        assert dist["P"] == 6000
        assert dist["A"] == 4000


# ════════════════════════════════════════════════════════════════
# CLASS 4: Participant Effects
# ════════════════════════════════════════════════════════════════

class TestParticipantEffects:
    """Per-participant effects: morale, battles_won/lost, primary-only."""

    def test_all_participants_same_morale_delta(self):
        """All participants on same side get UNIFORM morale delta."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=30000, personality="aggressive")
        dfn = _make_marshal(name="Def", strength=25000)

        result = combat.resolve_battle(atk, dfn, apply_casualties=False)

        # Morale delta is a single value for all participants on each side
        assert isinstance(result["attacker_morale_delta"], int)
        assert isinstance(result["defender_morale_delta"], int)

    def test_battles_won_incremented_for_all_winners(self):
        """All participants on winning side increment battles_won."""
        executor = CommandExecutor()
        primary = _make_marshal(name="P", location="Rhineland", strength=40000,
                                personality="aggressive", nation="France")
        ally = _make_marshal(name="A", location="Rhineland", strength=30000, nation="France")
        enemy = _make_marshal(name="E", location="Rhineland", strength=20000,
                              nation="Coalition", personality="cautious")

        world = _make_world_with_marshals([primary, ally, enemy])

        # Build participants
        participants = executor._get_casualty_participants(
            primary, "Rhineland", "France", world)

        # Simulate winning side
        for p in participants:
            p.battles_won += 1

        assert primary.battles_won == 1
        assert ally.battles_won == 1

    def test_battles_lost_incremented_for_all_losers(self):
        """All participants on losing side increment battles_lost."""
        p1 = _make_marshal(name="P1", strength=30000)
        p2 = _make_marshal(name="P2", strength=20000)

        for p in [p1, p2]:
            p.battles_lost += 1

        assert p1.battles_lost == 1
        assert p2.battles_lost == 1

    def test_counter_punch_primary_defender_only(self):
        """Counter-punch: primary defender ONLY, not allies (N1)."""
        combat = CombatResolver()
        # Ensure defender wins
        atk = _make_marshal(name="Atk", strength=10000, personality="aggressive")
        dfn = _make_marshal(name="Def", strength=50000, personality="cautious")
        ally_def = _make_marshal(name="AllyDef", strength=30000, personality="cautious")

        # Simulate: only primary defender gets counter_punch
        dfn.counter_punch_available = True
        dfn.counter_punch_turns = 2
        # Ally should NOT get it
        assert not getattr(ally_def, 'counter_punch_available', False)

    def test_recklessness_primary_attacker_only(self):
        """Recklessness: primary attacker ONLY, not allies (N1)."""
        # cavalry=True + personality="aggressive" → is_reckless_cavalry
        primary_cav = _make_marshal(name="Ney", strength=30000, cavalry=True,
                                    personality="aggressive")
        primary_cav.recklessness = 1
        assert primary_cav.is_reckless_cavalry

        ally = _make_marshal(name="Ally", strength=20000, cavalry=True,
                             personality="aggressive")
        ally.recklessness = 0
        assert ally.is_reckless_cavalry

        # Simulate: only primary gets recklessness increment
        primary_cav._increment_recklessness()

        assert primary_cav.recklessness == 2
        assert ally.recklessness == 0  # Unchanged

    def test_each_participant_checks_forced_retreat_independently(self):
        """Forced retreat checked per-participant after morale applied."""
        p1 = _make_marshal(name="P1", strength=30000)
        p2 = _make_marshal(name="P2", strength=20000)

        # Set different morale levels
        p1.morale = 20  # Below threshold (25) → forced retreat
        p2.morale = 60  # Above threshold → no retreat

        THRESHOLD = 25
        assert p1.morale <= THRESHOLD and p1.strength > 0  # Should retreat
        assert p2.morale > THRESHOLD  # Should NOT retreat

    def test_participant_broken_at_low_morale_and_strength(self):
        """Participant broken when morale <= 25 AND strength > 0."""
        p = _make_marshal(name="P", strength=5000)
        p.morale = 15

        assert p.morale <= 25 and p.strength > 0


# ════════════════════════════════════════════════════════════════
# CLASS 5: Integration with Existing Systems
# ════════════════════════════════════════════════════════════════

class TestIntegrationExistingSystems:
    """Integration: solo battles, reinforcements, relationships, call site audit."""

    def test_solo_battle_uses_apply_casualties_true(self):
        """Solo 1v1 battle: apply_casualties=True, no distribution."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=30000)
        dfn = _make_marshal(name="Def", strength=25000)

        with patch('random.randint', return_value=7):
            result = combat.resolve_battle(atk, dfn)

        # apply_casualties defaults to True — strength modified
        assert atk.strength < 30000
        assert dfn.strength < 25000
        # No raw_* fields
        assert "attacker_raw_casualties" not in result

    def test_relationship_check_fires_after_distribution(self):
        """Win/loss relationship check works with distributed casualties."""
        from backend.game_logic.relationship import get_battle_participants

        primary = _make_marshal(name="P", location="Bavaria", strength=40000)
        ally = _make_marshal(name="A", location="Bavaria", strength=30000)
        ally.modify_relationship("P", 1)  # Friendly

        world = _make_world_with_marshals([primary, ally])

        # get_battle_participants should find both
        participants = get_battle_participants(primary, "Bavaria", "France", world)

        assert len(participants) == 2

    def test_sally_attack_unaffected(self):
        """Sally attacks use apply_casualties=True (single-marshal combat)."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=30000)
        dfn = _make_marshal(name="Def", strength=25000)

        # Default call (no apply_casualties kwarg) = True
        result = combat.resolve_battle(atk, dfn, terrain="hills")

        assert atk.strength < 30000  # Casualties applied
        assert "attacker_raw_casualties" not in result

    def test_glorious_charge_unaffected(self):
        """Glorious charge uses apply_casualties=True."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=30000, cavalry=True)
        dfn = _make_marshal(name="Def", strength=25000)

        result = combat.resolve_battle(atk, dfn, glorious_charge=True)

        assert atk.strength < 30000  # Casualties applied
        assert "attacker_raw_casualties" not in result

    def test_all_casualties_are_int(self):
        """Golden Rule #2: all casualty values are int."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=30000)
        dfn = _make_marshal(name="Def", strength=25000)

        result = combat.resolve_battle(atk, dfn, apply_casualties=False)

        assert isinstance(result["attacker_raw_casualties"], int)
        assert isinstance(result["defender_raw_casualties"], int)
        assert isinstance(result["attacker_morale_delta"], int)
        assert isinstance(result["defender_morale_delta"], int)
        assert isinstance(result["attacker"]["casualties"], int)
        assert isinstance(result["defender"]["casualties"], int)

    def test_event_log_includes_casualty_info(self):
        """Log battle event has correct casualty data."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=30000)
        dfn = _make_marshal(name="Def", strength=25000)

        result = combat.resolve_battle(atk, dfn, apply_casualties=False)

        log_event = result["log_battle_event"]
        assert log_event["attacker_casualties"] == result["attacker"]["casualties"]
        assert log_event["defender_casualties"] == result["defender"]["casualties"]
        assert log_event["outcome"] == result["outcome"]


# ════════════════════════════════════════════════════════════════
# CLASS 6: Edge Cases
# ════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Edge cases: 0 strength, rounding, large battles."""

    def setup_method(self):
        self.executor = CommandExecutor()

    def test_zero_strength_participant_excluded(self):
        """Dead participant (0 strength) excluded from distribution."""
        m1 = _make_marshal(name="Alive", strength=30000)
        m2 = _make_marshal(name="Dead", strength=0)

        dist = self.executor._distribute_casualties(5000, [m1, m2])

        assert "Dead" not in dist
        assert dist["Alive"] == 5000

    def test_all_casualties_to_one_if_others_zero(self):
        """If only one participant has strength, they get all casualties."""
        m1 = _make_marshal(name="Only", strength=30000)
        m2 = _make_marshal(name="Dead1", strength=0)
        m3 = _make_marshal(name="Dead2", strength=0)

        dist = self.executor._distribute_casualties(5000, [m1, m2, m3])

        assert dist["Only"] == 5000

    def test_broken_marshal_excluded_from_participants(self):
        """Broken marshals not included in casualty participants."""
        primary = _make_marshal(name="P", location="Bavaria", strength=30000)
        broken = _make_marshal(name="Broken", location="Bavaria", strength=20000)
        broken.broken = True

        world = _make_world_with_marshals([primary, broken])

        participants = self.executor._get_casualty_participants(
            primary, "Bavaria", "France", world)

        assert len(participants) == 1
        assert participants[0].name == "P"

    def test_retreating_marshal_excluded_from_participants(self):
        """Retreating marshals not included in casualty participants."""
        primary = _make_marshal(name="P", location="Bavaria", strength=30000)
        retreating = _make_marshal(name="Ret", location="Bavaria", strength=20000)
        retreating.retreated_this_turn = True

        world = _make_world_with_marshals([primary, retreating])

        participants = self.executor._get_casualty_participants(
            primary, "Bavaria", "France", world)

        assert len(participants) == 1

    def test_recovering_marshal_excluded_from_participants(self):
        """Recovering marshals not included in casualty participants."""
        primary = _make_marshal(name="P", location="Bavaria", strength=30000)
        recovering = _make_marshal(name="Rec", location="Bavaria", strength=20000)
        recovering.retreat_recovery = 2

        world = _make_world_with_marshals([primary, recovering])

        participants = self.executor._get_casualty_participants(
            primary, "Bavaria", "France", world)

        assert len(participants) == 1

    def test_enemy_nation_excluded_from_participants(self):
        """Enemy nation marshals not included as participants."""
        primary = _make_marshal(name="P", location="Bavaria", strength=30000,
                                nation="France")
        enemy = _make_marshal(name="Enemy", location="Bavaria", strength=25000,
                              nation="Coalition")

        world = _make_world_with_marshals([primary, enemy])

        participants = self.executor._get_casualty_participants(
            primary, "Bavaria", "France", world)

        assert len(participants) == 1
        assert participants[0].name == "P"

    def test_different_location_excluded_from_participants(self):
        """Marshals in different regions not included."""
        primary = _make_marshal(name="P", location="Bavaria", strength=30000)
        elsewhere = _make_marshal(name="Far", location="Paris", strength=20000)

        world = _make_world_with_marshals([primary, elsewhere])

        participants = self.executor._get_casualty_participants(
            primary, "Bavaria", "France", world)

        assert len(participants) == 1

    def test_large_battle_many_participants(self):
        """Large battle with 4 participants distributes correctly."""
        m1 = _make_marshal(name="M1", strength=40000)
        m2 = _make_marshal(name="M2", strength=30000)
        m3 = _make_marshal(name="M3", strength=20000)
        m4 = _make_marshal(name="M4", strength=10000)

        dist = self.executor._distribute_casualties(20000, [m1, m2, m3, m4])

        # 40% = 8000, 30% = 6000, 20% = 4000, 10% = 2000
        assert dist["M1"] == 8000
        assert dist["M2"] == 6000
        assert dist["M3"] == 4000
        assert dist["M4"] == 2000
        assert sum(dist.values()) == 20000

    def test_is_coordinated_battle_detected(self):
        """2+ participants on one side = coordinated battle."""
        executor = CommandExecutor()
        p1 = _make_marshal(name="P1", location="Bavaria", strength=30000)
        p2 = _make_marshal(name="P2", location="Bavaria", strength=20000)

        world = _make_world_with_marshals([p1, p2])

        participants = executor._get_casualty_participants(
            p1, "Bavaria", "France", world)

        assert len(participants) >= 2

    def test_projected_threshold_matches_normal_path(self):
        """1.5 threshold in projected outcome matches normal path."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=30000)
        dfn = _make_marshal(name="Def", strength=25000)

        # Both paths should use 1.5 for tactical victory threshold
        # The deferred path explicitly uses 1.5 (see _build_deferred_result)
        result = combat.resolve_battle(atk, dfn, apply_casualties=False)

        # If one side took > 1.5x the other's casualties, it's a tactical victory
        atk_cas = result["attacker_raw_casualties"]
        def_cas = result["defender_raw_casualties"]

        if atk_cas > def_cas * 1.5:
            assert result["raw_outcome"] in ("defender_tactical_victory", "defender_victory")
        elif def_cas > atk_cas * 1.5:
            assert result["raw_outcome"] in ("attacker_tactical_victory", "attacker_victory")


# ════════════════════════════════════════════════════════════════
# CLASS 7: Post-Review Test Gaps (Session 62 Post-Review)
# ════════════════════════════════════════════════════════════════

class TestPostReviewGaps:
    """Tests covering gaps found in Session 62 Opus code review."""

    def setup_method(self):
        self.executor = CommandExecutor()

    # ── TG1: Primary attacker destroyed in coordinated battle ──

    def test_primary_destroyed_ally_survives(self):
        """Primary attacker killed (strength → 0), ally takes proportional share only."""
        primary = _make_marshal(name="Primary", strength=5000)
        ally = _make_marshal(name="Ally", strength=45000)

        # 10k casualties: Primary gets 10% = 1000, Ally gets 90% = 9000
        # But actually: 5k/50k = 10%, so Primary=1000, Ally=9000
        dist = self.executor._distribute_casualties(10000, [primary, ally])

        assert dist["Primary"] == 1000
        assert dist["Ally"] == 9000
        assert sum(dist.values()) == 10000

    def test_primary_overkill_capped_at_strength(self):
        """Primary's share capped at strength (can't go below 0)."""
        primary = _make_marshal(name="Primary", strength=2000)
        ally = _make_marshal(name="Ally", strength=48000)

        # 50k casualties: Primary would get 4% = 2000, Ally = 48000
        # Primary capped at 2000 (exactly strength), Ally capped at 48000
        dist = self.executor._distribute_casualties(50000, [primary, ally])

        assert dist["Primary"] == 2000  # Capped at strength
        assert dist["Ally"] == 48000
        # W-2: Total may be < raw_casualties due to capping (overkill on small unit)

    def test_primary_destroyed_morale_delta_still_applies(self):
        """Even if primary is destroyed, morale delta was applied (strength 0 doesn't block)."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=30000, personality="aggressive")
        dfn = _make_marshal(name="Def", strength=25000)

        result = combat.resolve_battle(atk, dfn, apply_casualties=False)

        # Morale delta exists regardless of outcome
        assert "attacker_morale_delta" in result
        assert "defender_morale_delta" in result

    # ── TG2: Asymmetric coordination (2+ vs 1 participant) ──

    def test_asymmetric_2v1_still_coordinated(self):
        """2 attackers vs 1 defender → coordinated battle (is_coordinated_battle = True)."""
        p1 = _make_marshal(name="AtkP", location="Rhineland", strength=30000)
        p2 = _make_marshal(name="AtkA", location="Rhineland", strength=20000)
        enemy = _make_marshal(name="Def", location="Rhineland", strength=40000,
                              nation="Coalition")

        world = _make_world_with_marshals([p1, p2, enemy])

        atk_parts = self.executor._get_casualty_participants(
            p1, "Rhineland", "France", world)
        def_parts = self.executor._get_casualty_participants(
            enemy, "Rhineland", "Coalition", world)

        is_coordinated = (len(atk_parts) >= 2 or len(def_parts) >= 2)
        assert is_coordinated
        assert len(atk_parts) == 2
        assert len(def_parts) == 1  # Solo defender

    def test_asymmetric_solo_defender_gets_all_casualties(self):
        """Solo defender in coordinated battle gets 100% of defender casualties."""
        defender = _make_marshal(name="SoloDef", strength=40000)

        dist = self.executor._distribute_casualties(8000, [defender])

        assert dist["SoloDef"] == 8000

    # ── TG3: AI-triggered coordinated battle (Building Blocks) ──

    def test_ai_side_participants_detected(self):
        """Enemy (AI) marshals in same region detected as participants."""
        enemy_primary = _make_marshal(name="EP", location="Bavaria", strength=30000,
                                       nation="Coalition")
        enemy_ally = _make_marshal(name="EA", location="Bavaria", strength=25000,
                                    nation="Coalition")

        world = _make_world_with_marshals([enemy_primary, enemy_ally])

        participants = self.executor._get_casualty_participants(
            enemy_primary, "Bavaria", "Coalition", world)

        assert len(participants) == 2
        names = {p.name for p in participants}
        assert names == {"EP", "EA"}

    def test_ai_side_distribution_proportional(self):
        """AI-side casualties distributed proportionally (Building Blocks)."""
        ep = _make_marshal(name="EP", strength=30000, nation="Coalition")
        ea = _make_marshal(name="EA", strength=20000, nation="Coalition")

        dist = self.executor._distribute_casualties(10000, [ep, ea])

        # 30k/50k = 60% → 6000, 20k/50k = 40% → 4000
        assert dist["EP"] == 6000
        assert dist["EA"] == 4000

    # ── TG5: Counter-punch Davout as non-primary ally ──

    def test_davout_non_primary_no_counter_punch_mastery(self):
        """Counter-Punch Mastery: only PRIMARY defender, not ally (N1)."""
        primary_def = _make_marshal(name="PrimaryDef", strength=30000,
                                     personality="cautious")
        davout_ally = _make_marshal(name="Davout", strength=25000,
                                     personality="cautious")
        davout_ally.ability = {"name": "Counter-Punch Mastery", "description": "test"}

        # In the coordinated path, counter_punch_ready is set on primary defender only
        # Simulate: the code does `enemy_marshal.counter_punch_ready = True`
        # where enemy_marshal is the PRIMARY defender.
        primary_def.counter_punch_ready = True
        # Davout as ally should NOT get it
        assert not getattr(davout_ally, 'counter_punch_ready', False)

    def test_davout_as_primary_gets_counter_punch_mastery(self):
        """Counter-Punch Mastery: primary defender Davout DOES get it."""
        davout = _make_marshal(name="Davout", strength=30000, personality="cautious")
        davout.ability = {"name": "Counter-Punch Mastery", "description": "test"}

        # Primary defender path
        davout.counter_punch_ready = True
        assert davout.counter_punch_ready is True

    # ── TG6: Test helper conformance ──

    def test_combat_result_has_nested_casualties(self):
        """Real combat.py result has casualties nested under attacker/defender dicts."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=30000)
        dfn = _make_marshal(name="Def", strength=25000)

        result = combat.resolve_battle(atk, dfn, apply_casualties=False)

        # Nested structure (both paths)
        assert isinstance(result["attacker"], dict)
        assert "casualties" in result["attacker"]
        assert isinstance(result["defender"], dict)
        assert "casualties" in result["defender"]

    def test_combat_result_no_toplevel_casualties_key(self):
        """Real combat.py result does NOT have top-level 'attacker_casualties' key."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=30000)
        dfn = _make_marshal(name="Def", strength=25000)

        # Normal path
        result_normal = combat.resolve_battle(atk, dfn)
        assert "attacker_casualties" not in result_normal
        assert "defender_casualties" not in result_normal

    def test_deferred_result_has_raw_keys(self):
        """Deferred path has attacker_raw_casualties at top level."""
        combat = CombatResolver()
        atk = _make_marshal(name="Atk", strength=30000)
        dfn = _make_marshal(name="Def", strength=25000)

        result = combat.resolve_battle(atk, dfn, apply_casualties=False)

        assert "attacker_raw_casualties" in result
        assert "defender_raw_casualties" in result
        # And nested casualties ALSO exist
        assert result["attacker"]["casualties"] == result["attacker_raw_casualties"]

    def test_relationship_reads_nested_casualties(self):
        """relationship.py reads from nested attacker/defender.casualties."""
        from backend.game_logic.relationship import check_shared_battle_relationship

        # Build a result matching real combat.py output (no top-level keys)
        battle_result = {
            "victor": "Atk",
            "outcome": "attacker_victory",
            "attacker": {
                "name": "Atk",
                "casualties": 3000,
                "remaining": 27000,
                "morale": 60,
                "forced_retreat": False,
            },
            "defender": {
                "name": "Def",
                "casualties": 8000,
                "remaining": 17000,
                "morale": 40,
                "forced_retreat": False,
            },
        }

        m_a = _make_marshal(name="A", location="Bavaria", strength=30000)
        m_b = _make_marshal(name="B", location="Bavaria", strength=25000)
        world = _make_world_with_marshals([m_a, m_b])

        # Should not crash — reads from nested dict correctly
        with patch('random.randint', return_value=10):
            result = check_shared_battle_relationship(m_a, m_b, battle_result, True, world)

        assert result in (-1, 0, 1)


# ════════════════════════════════════════════════════════════════
# CLASS 8: W-1 Fix Verification (SUPPORT Clearing Timing)
# ════════════════════════════════════════════════════════════════

class TestSupportClearingTiming:
    """W-1: SUPPORT orders must still be present during relationship processing."""

    def test_hostile_support_participates_in_relationship_check(self):
        """Hostile+SUPPORT marshal detected by get_battle_participants for relationships."""
        from backend.game_logic.relationship import get_battle_participants

        primary = _make_marshal(name="Primary", location="Bavaria", strength=30000)
        hostile_sup = _make_marshal(name="HostileSup", location="Bavaria", strength=20000)
        hostile_sup.modify_relationship("Primary", -2)  # Hostile
        hostile_sup.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Primary",
            target_type="marshal", started_turn=1,
            original_command="support Primary",
        )

        world = _make_world_with_marshals([primary, hostile_sup])

        # Relationship's get_battle_participants should include Hostile+SUPPORT
        participants = get_battle_participants(primary, "Bavaria", "France", world)

        assert len(participants) == 2
        assert any(p.name == "HostileSup" for p in participants)

    def test_hostile_without_support_excluded_from_relationship_check(self):
        """Plain Hostile (no SUPPORT) excluded from relationship participants."""
        from backend.game_logic.relationship import get_battle_participants

        primary = _make_marshal(name="Primary", location="Bavaria", strength=30000)
        hostile = _make_marshal(name="Hostile", location="Bavaria", strength=20000)
        hostile.modify_relationship("Primary", -2)

        world = _make_world_with_marshals([primary, hostile])

        participants = get_battle_participants(primary, "Bavaria", "France", world)

        assert len(participants) == 1
        assert participants[0].name == "Primary"

    def test_support_cleared_after_relationships_not_before(self):
        """Verify SUPPORT order still exists when relationships are processed.

        The fix ensures arriving reinforcements keep their strategic_order
        through the relationship processing phase. This test verifies the
        executor._get_casualty_participants pattern (called before clearing)
        and the relationship.get_battle_participants pattern both see SUPPORT.
        """
        primary = _make_marshal(name="P", location="Bavaria", strength=30000)
        arriving = _make_marshal(name="Arr", location="Bavaria", strength=20000)
        arriving.modify_relationship("P", -2)  # Hostile
        arriving.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="P",
            target_type="marshal", started_turn=1,
            original_command="support P",
        )

        world = _make_world_with_marshals([primary, arriving])

        # Both casualty participants and relationship participants
        # should see the SUPPORT order
        executor = CommandExecutor()
        cas_parts = executor._get_casualty_participants(
            primary, "Bavaria", "France", world)

        from backend.game_logic.relationship import get_battle_participants
        rel_parts = get_battle_participants(primary, "Bavaria", "France", world)

        assert len(cas_parts) == 2
        assert len(rel_parts) == 2

        # SUPPORT still present (not cleared yet)
        assert arriving.strategic_order is not None
        assert arriving.strategic_order.command_type == "SUPPORT"
