"""Jealousy System v3.2 (docs/JEALOUSY_SPEC.md, §0 build record, July 11 2026).

The glory ladder, relationship-scaled grievance triggers, the three
personality expressions, battle-time resolution, the Crowned-with-Glory
buff, escalation, the marshal-petition channel (§6 confrontation + §6b
rivalry), enemy jealousy (Building Blocks §9b), and the aggressive
autonomous attack.

Conventions: the 1805 campaign fixture is module-scoped read-only; mutating
tests deep-copy via to_dict/from_dict. Glory is injected through the same
record/append seams the combat pipeline uses.
"""

from pathlib import Path

import pytest

from backend.game_logic import jealousy as J
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (
    REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    w = WorldState.from_dict(world1805.to_dict())
    # Neutral authority: outside both polarity bands so trigger tests
    # exercise the relationship thresholds, not the authority override.
    w.authority_tracker.authority = 50
    return w


def _glory(world, name, points, turn=None):
    J._append_glory(world.marshals[name], turn or world.current_turn, points)


def _run_pass(world):
    world._jealousy_processed_turn = None
    return J.process_turn(world)


# ═══════════════════════ GLORY SCORING (spec §1) ═══════════════════════════


class TestGloryScoring:
    def test_victory_base_point(self):
        assert J._victory_points(100, 100, False, False) == 1

    def test_decisive_win_bonus(self):
        assert J._victory_points(100, 200, False, False) == 2

    def test_flawless_counts_as_decisive(self):
        assert J._victory_points(0, 500, False, False) == 2

    def test_territory_bonus(self):
        assert J._victory_points(100, 100, True, False) == 2

    def test_outnumbered_bonus(self):
        assert J._victory_points(100, 100, False, True) == 2

    def test_full_stack(self):
        assert J._victory_points(100, 200, True, True) == 4

    # CA8-19(ii): `test_garrison_stomp_is_zero` USED to live here as
    # `_victory_points(100, 500, True, True, True) == 0` — a direct unit call
    # with a fifth argument no production path could supply, so it stayed green
    # whether the exemption was wired or dead. It was dead. The rule is now
    # structural (the pipeline's glory step states the garrison exclusion) and
    # is pinned end-to-end, through a real garrison assault, in
    # tests/test_creative_audit_ca8_2026_08_04.py::TestCA819GarrisonSeams.

    def test_defeat_base(self):
        assert J._defeat_points(100, 100, False, False) == -1

    def test_decisive_loss_extra(self):
        assert J._defeat_points(200, 100, False, False) == -2

    def test_territory_lost_extra(self):
        assert J._defeat_points(100, 100, True, False) == -2

    def test_outnumbered_loss_no_stigma(self):
        assert J._defeat_points(500, 100, True, True) == 0

    def test_window_prunes_and_floors(self, world):
        ney = world.marshals["Ney"]
        world.current_turn = 10
        J._append_glory(ney, 2, 5)      # outside the 5-turn window
        J._append_glory(ney, 8, -3)     # inside
        J._append_glory(ney, 9, 1)      # inside
        assert J.get_glory_score(ney, 10) == 0  # floor at 0 (-3+1=-2)
        J.prune_glory_events(ney, 10)
        assert all(10 - e["turn"] < J.GLORY_WINDOW for e in ney.glory_events)

    def test_record_battle_glory_primaries_and_participants(self, world):
        ney = world.marshals["Ney"]
        davout = world.marshals["Davout"]
        mack = world.marshals["Mack"]
        J.record_battle_glory(
            world, ney, mack, attacker_won=True, defender_won=False,
            attacker_casualties=1000, defender_casualties=3000,
            conquered=True,
            pre_attacker_strength=24000, pre_defender_strength=52000,
            attacker_participants=[ney, davout], defender_participants=[])
        # Ney: 1 base + 1 decisive + 1 territory + 1 outnumbered = 4
        assert J.get_glory_score(ney, world.current_turn) == 4
        # Davout (participant): base +1 only
        assert J.get_glory_score(davout, world.current_turn) == 1
        # Mack (loser, NOT outnumbered): -1 decisive -1 = floored at 0
        assert J.get_glory_score(mack, world.current_turn) == 0
        assert mack.glory_events  # the negative event IS recorded


# ═══════════════════════ THE LADDER (spec §1 v3) ═══════════════════════════


class TestLadder:
    def test_one_rung_above(self, world):
        _glory(world, "Davout", 7)
        _glory(world, "Ney", 4)
        _glory(world, "Lannes", 2)
        # Lannes (2) looks at Ney (4), not Davout (7)
        target = J.find_jealousy_target(world.marshals["Lannes"], world)
        assert target.name == "Ney"
        # Ney looks at Davout
        assert J.find_jealousy_target(world.marshals["Ney"], world).name == "Davout"
        # Davout is top — no target
        assert J.find_jealousy_target(world.marshals["Davout"], world) is None

    def test_ties_use_worse_relationship(self, world):
        # Murat: Ney -1, Davout -1, Lannes -1, Bernadotte -2
        _glory(world, "Davout", 3)
        _glory(world, "Bernadotte", 3)
        target = J.find_jealousy_target(world.marshals["Murat"], world)
        assert target.name == "Bernadotte"  # -2 beats -1 on the tiebreak

    def test_same_nation_only(self, world):
        _glory(world, "Mack", 9)
        assert J.find_jealousy_target(world.marshals["Ney"], world) is None

    def test_broken_and_captured_excluded(self, world):
        _glory(world, "Davout", 5)
        world.marshals["Davout"].broken = True
        assert J.find_jealousy_target(world.marshals["Ney"], world) is None
        world.marshals["Davout"].broken = False
        world.marshals["Davout"].captured_by = "Austria"
        assert J.find_jealousy_target(world.marshals["Ney"], world) is None


# ═══════════════ TRIGGERS: THRESHOLDS + POLARITY (spec §1) ═════════════════


class TestTriggers:
    def test_professional_fires_at_two(self, world):
        # Massena has no authored edge to Davout → Professional (0).
        # Isolate the pair — the 2-per-nation rate limit would otherwise
        # let a hair-trigger rival (Murat) outrank Massena in the queue.
        for m in world.marshals.values():
            if m.nation == "France" and m.name not in ("Massena", "Davout"):
                m.strength = 0
        _glory(world, "Davout", 2)
        _run_pass(world)
        assert world.marshals["Massena"].jealous_of == "Davout"

    def test_friendly_resists_until_four(self, world):
        # Lannes → Ney is authored +1 (Friendly): delta 3 not enough
        for m in world.marshals.values():
            if m.nation == "France" and m.name not in ("Lannes", "Ney"):
                m.strength = 0
        _glory(world, "Ney", 3)
        _run_pass(world)
        assert world.marshals["Lannes"].jealous_of != "Ney"
        world2 = WorldState.from_dict(world.to_dict())
        world2.authority_tracker.authority = 50
        _glory(world2, "Ney", 1)  # delta now 4
        _run_pass(world2)
        assert world2.marshals["Lannes"].jealous_of == "Ney"

    def test_rival_hair_trigger(self, world):
        # Murat → Davout authored -1 (Rival): delta 1 fires
        _glory(world, "Davout", 1)
        _run_pass(world)
        assert world.marshals["Murat"].jealous_of == "Davout"

    def test_hostile_needs_idle(self, world):
        # Bernadotte → Davout authored -2 (Hostile): delta 1 + idle >= 2
        _glory(world, "Davout", 1)
        world.marshals["Bernadotte"].idle_turns = 0
        world.marshals["Murat"].idle_turns = 0
        world.marshals["Murat"].strength = 0  # keep Murat off this test
        _run_pass(world)
        assert world.marshals["Bernadotte"].jealous_of is None
        world.marshals["Bernadotte"].idle_turns = 2
        _run_pass(world)
        assert world.marshals["Bernadotte"].jealous_of == "Davout"

    def test_devoted_immune(self, world):
        ney = world.marshals["Ney"]
        ney.set_relationship("Davout", 2)
        _glory(world, "Davout", 10)
        for m in world.marshals.values():
            if m.nation == "France" and m.name not in ("Ney", "Davout"):
                m.strength = 0
        _run_pass(world)
        assert ney.jealous_of is None

    def test_authority_above_70_dampens(self, world):
        """§0.2 build amendment: high authority RAISES every threshold by
        one rather than suppressing outright — a professional-pair delta
        of 2 no longer fires, while a big enough gap still does (the
        marshals feuded at the height of empire)."""
        world.authority_tracker.authority = 85
        for m in world.marshals.values():
            if m.nation == "France" and m.name not in ("Massena", "Davout"):
                m.strength = 0
        _glory(world, "Davout", 2)      # professional threshold 2 → dampened 3
        _run_pass(world)
        assert world.marshals["Massena"].jealous_of is None
        world2 = WorldState.from_dict(world.to_dict())
        world2.authority_tracker.authority = 85
        _glory(world2, "Davout", 1)     # delta 3 ≥ dampened 3 → fires
        _run_pass(world2)
        assert world2.marshals["Massena"].jealous_of == "Davout"

    def test_authority_below_30_accelerates(self, world):
        world.authority_tracker.authority = 20
        # Lannes → Ney Friendly (+1): normally needs 4; accelerated fires at 1
        _glory(world, "Ney", 1)
        for m in world.marshals.values():
            if m.nation == "France" and m.name not in ("Lannes", "Ney"):
                m.strength = 0
        _run_pass(world)
        assert world.marshals["Lannes"].jealous_of == "Ney"

    def test_capital_threatened_suppresses(self, world):
        mack = world.marshals["Mack"]
        mack.location = "Paris"
        assert world.is_at_war("France", "Austria")
        _glory(world, "Davout", 10)
        _run_pass(world)
        assert all(m.jealous_of is None for m in world.marshals.values()
                   if m.nation == "France")

    def test_broken_source_suppressed(self, world):
        _glory(world, "Davout", 5)
        world.marshals["Massena"].broken = True
        _run_pass(world)
        assert world.marshals["Massena"].jealous_of is None

    def test_rate_limit_two_per_nation(self, world):
        _glory(world, "Davout", 9)
        _run_pass(world)
        jealous = [m for m in world.marshals.values()
                   if m.nation == "France" and m.jealous_of]
        assert len(jealous) <= J.MAX_FIRES_PER_NATION_TURN

    def test_duration_scales_with_delta(self, world):
        for m in world.marshals.values():
            if m.nation == "France" and m.name not in ("Massena", "Davout"):
                m.strength = 0
        _glory(world, "Davout", 2)
        _run_pass(world)
        massena = world.marshals["Massena"]
        assert massena.jealous_of == "Davout"
        assert massena.jealousy_turns_remaining == 2  # delta==threshold → min
        # a bigger gap caps at 5
        assert J._duration_for(delta=9, threshold=2) == 5

    def test_timer_expiry_no_surge(self, world):
        massena = world.marshals["Massena"]
        massena.jealous_of = "Davout"
        massena.jealousy_turns_remaining = 1
        _glory(world, "Davout", 3)  # keep Davout above (no ladder shift)
        _run_pass(world)
        assert massena.jealous_of is None
        assert massena.jealousy_surge_turns == 0

    def test_ladder_shift_resolves_with_surge(self, world):
        massena = world.marshals["Massena"]
        massena.jealous_of = "Davout"
        massena.jealousy_turns_remaining = 5
        _glory(world, "Massena", 4)
        _glory(world, "Davout", 1)
        _run_pass(world)
        assert massena.jealous_of is None
        assert massena.jealousy_surge_turns == 1
        # history still records the lifetime instance? (applied at fire —
        # this grievance was injected, so no history entry is expected here)

    def test_gone_target_clears(self, world):
        massena = world.marshals["Massena"]
        massena.jealous_of = "Davout"
        massena.jealousy_turns_remaining = 4
        world.marshals["Davout"].captured_by = "Austria"
        world.marshals["Davout"].strength = 0
        _run_pass(world)
        assert massena.jealous_of is None
        assert massena.jealousy_surge_turns == 0


# ═══════════ DERIVED -1 RELATIONSHIP + CASCADES (spec §8, §0.2) ═════════════


class TestDerivedRelationship:
    def test_derived_minus_one(self, world):
        ney = world.marshals["Ney"]
        assert ney.get_relationship("Davout") == 0
        ney.jealous_of = "Davout"
        assert ney.get_relationship("Davout") == -1
        ney.jealous_of = None
        assert ney.get_relationship("Davout") == 0  # self-restoring

    def test_hostile_floor(self, world):
        bernadotte = world.marshals["Bernadotte"]
        assert bernadotte.get_relationship("Davout") == -2
        bernadotte.jealous_of = "Davout"
        assert bernadotte.get_relationship("Davout") == -2  # floor holds

    def test_stored_dict_untouched_and_unserialized(self, world):
        ney = world.marshals["Ney"]
        ney.jealous_of = "Davout"
        assert ney.relationships.get("Davout", 0) == 0
        data = ney.to_dict()
        assert data["relationships"].get("Davout", 0) == 0
        assert data["jealous_of"] == "Davout"

    def test_coordination_scale_drops(self, world):
        """The derived -1 cascades through _RELATIONSHIP_SCALING."""
        from backend.commands.combat_executor import CombatExecutor
        scaling = CombatExecutor._RELATIONSHIP_SCALING
        soult = world.marshals["Soult"]     # literal — no hard-zero arm
        massena = world.marshals["Massena"]  # Soult↔Massena authored +1
        assert scaling[soult.get_relationship("Massena")] == 1.25
        soult.jealous_of = "Massena"
        assert scaling[soult.get_relationship("Massena")] == 1.0

    def test_aggressive_pair_hard_zero(self, world):
        """An aggressive grievance zeroes the PAIR's coordination."""
        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        ney = world.marshals["Ney"]
        davout = world.marshals["Davout"]
        ney.jealous_of = "Davout"
        # Davout receiving from ally Ney: the pair reads 0.0 (Ney refuses)
        atk, defense = executor._combat._calculate_per_ally_coordination(
            davout, [ney])
        assert atk == 0.0 and defense == 0.0
        # And Ney receiving from Davout is equally poisoned
        atk2, def2 = executor._combat._calculate_per_ally_coordination(
            ney, [davout])
        assert atk2 == 0.0 and def2 == 0.0

    def test_cautious_pair_reads_worse_direction(self, world):
        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        bernadotte = world.marshals["Bernadotte"]  # cautious
        soult = world.marshals["Soult"]
        assert bernadotte.get_relationship("Soult") == 0
        bernadotte.jealous_of = "Soult"
        # Soult receiving from Bernadotte: pair reads min(0, -1) = -1 → ×0.5
        atk, defense = executor._combat._calculate_per_ally_coordination(
            soult, [bernadotte])
        assert atk == pytest.approx(0.03 * 0.5)
        assert defense == pytest.approx(0.05 * 0.5)


# ═══════════ EXPRESSIONS: SOLO BUFF, SURGE, CROWN (spec §3, §4, §1) ═════════


class TestExpressionsAndCrown:
    def test_solo_attack_buff(self, world):
        ney = world.marshals["Ney"]
        ney.jealous_of = "Davout"
        ney._jealousy_solo_attack = True
        boosted = ney.get_attack_modifier()
        ney2 = world.marshals["Lannes"]
        base = ney2.get_attack_modifier()
        # both aggressive, same stance — the ratio isolates the buff
        assert boosted / base == pytest.approx(1.15, rel=1e-6)

    def test_no_buff_when_not_solo(self, world):
        ney = world.marshals["Ney"]
        ney.jealous_of = "Davout"
        assert not getattr(ney, "_jealousy_solo_attack", False)
        lannes = world.marshals["Lannes"]
        assert ney.get_attack_modifier() == pytest.approx(
            lannes.get_attack_modifier())

    def test_aggressive_surge_attack(self, world):
        ney = world.marshals["Ney"]
        lannes = world.marshals["Lannes"]
        ney.jealousy_surge_turns = 1
        assert ney.get_attack_modifier() / lannes.get_attack_modifier() == \
            pytest.approx(1.10, rel=1e-6)

    def test_cautious_surge_defense(self, world):
        davout = world.marshals["Davout"]
        base = davout.get_defense_modifier()
        davout.jealousy_surge_turns = 1
        assert davout.get_defense_modifier() == pytest.approx(
            min(base * 1.10, 1.75), rel=1e-6)

    def test_surge_decays_next_pass(self, world):
        ney = world.marshals["Ney"]
        ney.jealousy_surge_turns = 1
        _run_pass(world)
        assert ney.jealousy_surge_turns == 0

    def test_crown_goes_to_top_scorer(self, world):
        _glory(world, "Davout", 4)
        _run_pass(world)
        assert world.marshals["Davout"].glory_crowned
        assert not world.marshals["Ney"].glory_crowned

    def test_crown_transfers_and_announces(self, world):
        _glory(world, "Davout", 3)
        events = _run_pass(world)
        assert any(e["type"] == "glory_crowned" for e in events)
        _glory(world, "Ney", 5)
        events2 = _run_pass(world)
        assert world.marshals["Ney"].glory_crowned
        assert not world.marshals["Davout"].glory_crowned
        assert any(e["type"] == "glory_crown_lost" for e in events2)

    def test_tied_top_leaves_crown_vacant(self, world):
        _glory(world, "Davout", 3)
        _glory(world, "Ney", 3)
        _run_pass(world)
        assert not world.marshals["Davout"].glory_crowned
        assert not world.marshals["Ney"].glory_crowned

    def test_crown_boosts_shock_defense_admin_only(self, world):
        ney = world.marshals["Ney"]  # shock 9, defense 6, admin 3, tactical 5
        ney.glory_crowned = True
        assert ney.get_effective_skill("shock") == 10
        assert ney.get_effective_skill("defense") == 7
        assert ney.get_effective_skill("tactical") == 5   # not crowned
        assert ney.get_effective_skill("command") == 7    # not crowned

    def test_crown_clamps_at_ten(self, world):
        ney = world.marshals["Ney"]
        ney.skills["shock"] = 10
        ney.glory_crowned = True
        assert ney.get_effective_skill("shock") == 10

    def test_crown_flips_intendance_tier(self, world):
        soult = world.marshals["Soult"]  # admin 7 → baseline
        assert soult.get_recruit_cost_modifier() == 1.0
        soult.glory_crowned = True       # admin 7+1=8 → thrifty
        assert soult.get_recruit_cost_modifier() == pytest.approx(0.85)

    def test_crown_flips_steward_tier(self, world):
        soult = world.marshals["Soult"]
        assert soult.get_estate_stability_bonus() == 0
        soult.glory_crowned = True
        assert soult.get_estate_stability_bonus() == 5

    def test_precision_does_not_leak_into_admin(self, world):
        """The MC-1 Precision +1 stays combat-only: admin tiers never see it."""
        soult = world.marshals["Soult"]
        soult.precision_execution_active = True
        assert soult.get_recruit_cost_modifier() == 1.0
        assert soult.get_estate_stability_bonus() == 0

    def test_uncrowned_effective_skill_byte_identical(self, world):
        for m in world.marshals.values():
            for skill in ("shock", "defense", "tactical"):
                assert m.get_effective_skill(skill) == m.skills.get(skill, 5)


# ═══════════ LITERAL: THE VINDICATED GARRISON (spec §3) ═════════════════════


class TestLiteralExpression:
    def _sideline_soult(self, world, turns):
        soult = world.marshals["Soult"]
        soult.consecutive_hold_turns = turns
        return soult

    def test_hold_counter_increments_when_peers_engaged(self, world):
        ney = world.marshals["Ney"]
        ney.attacks_this_turn = 1
        J.update_literal_hold_counters(world)
        assert world.marshals["Soult"].consecutive_hold_turns == 1

    def test_no_counter_when_everyone_idle(self, world):
        """EC-D: if ALL marshals are idle, nobody is being singled out."""
        for m in world.marshals.values():
            m.attacks_this_turn = 0
            m.moved_this_turn = False
            m.in_combat_this_turn = False
            m.strategic_order = None
        J.update_literal_hold_counters(world)
        assert world.marshals["Soult"].consecutive_hold_turns == 0

    def test_counter_resets_when_he_acts(self, world):
        soult = self._sideline_soult(world, 2)
        soult.attacks_this_turn = 1
        world.marshals["Ney"].attacks_this_turn = 1
        J.update_literal_hold_counters(world)
        assert soult.consecutive_hold_turns == 0

    def test_sidelining_trigger_fires(self, world):
        soult = self._sideline_soult(world, J.LITERAL_HOLD_TRIGGER)
        world.marshals["Ney"].attacks_this_turn = 1  # peers engaged
        _run_pass(world)
        assert soult.jealous_of is not None

    def test_intel_enhancement_boosts_sector(self, world):
        from backend.models.intel import FULL, PARTIAL, UNKNOWN
        soult = world.marshals["Soult"]
        soult.jealous_of = "Ney"
        world.calculate_visibility()
        home = world.regions[soult.location]
        assert world.get_region_intel(soult.location).visibility == FULL
        for adj in home.adjacent_regions:
            vis = world.get_region_intel(adj).visibility
            assert vis in (FULL, PARTIAL)
            assert vis != UNKNOWN

    def test_intel_boost_stops_after_clear(self, world):
        """No jealousy + no surge = the ordinary visibility rules."""
        soult = world.marshals["Soult"]
        soult.jealous_of = None
        soult.jealousy_surge_turns = 0
        world.calculate_visibility()  # must not raise; boost path skipped

    def test_intel_lingers_on_surge(self, world):
        from backend.models.intel import FULL, PARTIAL
        soult = world.marshals["Soult"]
        soult.jealous_of = None
        soult.jealousy_surge_turns = 1
        world.calculate_visibility()
        home = world.regions[soult.location]
        for adj in home.adjacent_regions:
            assert world.get_region_intel(adj).visibility in (FULL, PARTIAL)


# ═══════════ BATTLE-TIME RESOLUTION (spec §3 + EC-F/EC-K/EC-L) ══════════════


class TestBattleResolution:
    def test_aggressive_resolves_on_worthy_win(self, world):
        ney = world.marshals["Ney"]
        mack = world.marshals["Mack"]
        ney.jealous_of = "Davout"
        J.check_battle_resolution(
            world, ney, mack, attacker_won=True, defender_won=False,
            pre_attacker_strength=24000, pre_defender_strength=20000)
        assert ney.jealous_of is None
        assert ney.jealousy_surge_turns == 1

    def test_aggressive_stomp_does_not_resolve(self, world):
        ney = world.marshals["Ney"]
        mack = world.marshals["Mack"]
        ney.jealous_of = "Davout"
        J.check_battle_resolution(
            world, ney, mack, attacker_won=True, defender_won=False,
            pre_attacker_strength=24000, pre_defender_strength=5000)
        assert ney.jealous_of == "Davout"

    def test_aggressive_loss_does_not_resolve(self, world):
        ney = world.marshals["Ney"]
        mack = world.marshals["Mack"]
        ney.jealous_of = "Davout"
        J.check_battle_resolution(
            world, ney, mack, attacker_won=False, defender_won=True,
            pre_attacker_strength=24000, pre_defender_strength=52000)
        assert ney.jealous_of == "Davout"

    def test_cautious_shared_victory_resolves(self, world):
        davout = world.marshals["Davout"]
        ney = world.marshals["Ney"]
        mack = world.marshals["Mack"]
        davout.jealous_of = "Ney"
        J.check_battle_resolution(
            world, ney, mack, attacker_won=True, defender_won=False,
            pre_attacker_strength=24000, pre_defender_strength=5000,
            attacker_participants=[ney, davout])
        assert davout.jealous_of is None
        assert davout.jealousy_surge_turns == 1

    def test_cautious_three_ally_win_resolves(self, world):
        davout = world.marshals["Davout"]
        lannes = world.marshals["Lannes"]
        murat = world.marshals["Murat"]
        mack = world.marshals["Mack"]
        davout.jealous_of = "Ney"  # Ney NOT in the battle
        J.check_battle_resolution(
            world, lannes, mack, attacker_won=True, defender_won=False,
            pre_attacker_strength=18000, pre_defender_strength=5000,
            attacker_participants=[lannes, davout, murat])
        assert davout.jealous_of is None

    def test_cautious_pair_win_without_target_does_not_resolve(self, world):
        davout = world.marshals["Davout"]
        lannes = world.marshals["Lannes"]
        mack = world.marshals["Mack"]
        davout.jealous_of = "Ney"
        J.check_battle_resolution(
            world, lannes, mack, attacker_won=True, defender_won=False,
            pre_attacker_strength=18000, pre_defender_strength=5000,
            attacker_participants=[lannes, davout])
        assert davout.jealous_of == "Ney"

    def test_literal_contact_resolves_even_on_loss(self, world):
        soult = world.marshals["Soult"]
        mack = world.marshals["Mack"]
        soult.jealous_of = "Ney"
        J.check_battle_resolution(
            world, soult, mack, attacker_won=False, defender_won=True,
            pre_attacker_strength=40000, pre_defender_strength=52000)
        assert soult.jealous_of is None
        assert soult.jealousy_surge_turns == 1

    def test_literal_defense_survived_resolves(self, world):
        soult = world.marshals["Soult"]
        mack = world.marshals["Mack"]
        soult.jealous_of = "Ney"
        J.check_battle_resolution(
            world, mack, soult, attacker_won=True, defender_won=False,
            pre_attacker_strength=52000, pre_defender_strength=40000,
            defender_broken=False)
        assert soult.jealous_of is None

    def test_literal_broken_defense_does_not_resolve(self, world):
        soult = world.marshals["Soult"]
        mack = world.marshals["Mack"]
        soult.jealous_of = "Ney"
        J.check_battle_resolution(
            world, mack, soult, attacker_won=True, defender_won=False,
            pre_attacker_strength=52000, pre_defender_strength=40000,
            defender_broken=True)
        assert soult.jealous_of == "Ney"


# ═══════════ ESCALATION (spec §10) ══════════════════════════════════════════


class TestEscalation:
    def _fire(self, world, marshal, target):
        events = []
        J.apply_jealousy(world, marshal, target, delta=2, threshold=2,
                         events=events)
        return events

    def test_professional_pair_no_escalation(self, world):
        massena = world.marshals["Massena"]
        davout = world.marshals["Davout"]
        self._fire(world, massena, davout)
        assert J.get_escalation_level(massena, "Davout") == 0

    def test_rival_pair_escalates_immediately(self, world):
        murat = world.marshals["Murat"]   # authored -1 toward Davout
        davout = world.marshals["Davout"]
        self._fire(world, murat, davout)
        assert J.get_escalation_level(murat, "Davout") == 1

    def test_second_escalation_permanent_damage(self, world):
        murat = world.marshals["Murat"]
        davout = world.marshals["Davout"]
        self._fire(world, murat, davout)
        J.clear_jealousy(world, murat, resolved_by_action=False)
        stored_before = murat.relationships.get("Davout", 0)
        self._fire(world, murat, davout)
        assert J.get_escalation_level(murat, "Davout") == 2
        assert murat.relationships.get("Davout", 0) == stored_before - 1
        # permanent: does NOT restore on resolution
        J.clear_jealousy(world, murat, resolved_by_action=False)
        assert murat.relationships.get("Davout", 0) == stored_before - 1

    def test_third_escalation_mutual_spiral(self, world):
        murat = world.marshals["Murat"]
        davout = world.marshals["Davout"]
        for _ in range(2):
            self._fire(world, murat, davout)
            J.clear_jealousy(world, murat, resolved_by_action=False)
        self._fire(world, murat, davout)
        assert J.get_escalation_level(murat, "Davout") == 3
        # tier 3: Davout automatically resents him right back
        assert davout.jealous_of == "Murat"

    def test_third_lifetime_fire_qualifies_even_professional(self, world):
        massena = world.marshals["Massena"]
        davout = world.marshals["Davout"]
        for _ in range(2):
            self._fire(world, massena, davout)
            J.clear_jealousy(world, massena, resolved_by_action=False)
        self._fire(world, massena, davout)
        assert J.get_escalation_level(massena, "Davout") >= 1


# ═══════════ THE PETITION CHANNEL (spec §6, §6b, §0.2 item 10) ══════════════


class TestConfrontationPetition:
    def _fire_first_time(self, world):
        massena = world.marshals["Massena"]
        davout = world.marshals["Davout"]
        events = []
        J.apply_jealousy(world, massena, davout, delta=2, threshold=2,
                         events=events)
        return massena, davout

    def test_first_time_queues_petition(self, world):
        self._fire_first_time(world)
        petition = world.pending_marshal_petition
        assert petition is not None
        assert petition["kind"] == "jealousy_confrontation"
        assert {o["id"] for o in petition["options"]} == \
            {"acknowledge", "promise", "rebuke"}

    def test_second_time_no_petition(self, world):
        massena, davout = self._fire_first_time(world)
        J.handle_petition_response(world, "acknowledge")
        J.clear_jealousy(world, massena, resolved_by_action=False)
        events = []
        J.apply_jealousy(world, massena, davout, delta=2, threshold=2,
                         events=events)
        assert world.pending_marshal_petition is None

    def test_promise_costs_ap_and_shortens(self, world):
        massena, _ = self._fire_first_time(world)
        duration = massena.jealousy_turns_remaining
        world.actions_remaining = 3
        result = J.handle_petition_response(world, "promise")
        assert result["success"]
        assert world.actions_remaining == 3 - J.CONFRONT_PROMISE_AP
        assert massena.jealousy_turns_remaining == max(
            0, duration - J.CONFRONT_PROMISE_DURATION_CUT)

    def test_promise_greyed_and_refused_at_zero_ap(self, world):
        massena, _ = self._fire_first_time(world)
        world.actions_remaining = 0
        # EC-I: the queued petition computed enabled from AP at build time —
        # rebuild honesty is executor-side: the response revalidates.
        result = J.handle_petition_response(world, "promise")
        assert not result["success"]

    def test_rebuke_trust_and_rider(self, world):
        massena, _ = self._fire_first_time(world)
        trust_before = massena.trust.value
        result = J.handle_petition_response(world, "rebuke")
        assert result["success"]
        assert massena.trust.value == trust_before + J.CONFRONT_REBUKE_TRUST

    def test_unknown_choice_rejected(self, world):
        self._fire_first_time(world)
        result = J.handle_petition_response(world, "bribe")
        assert not result["success"]
        assert world.pending_marshal_petition is not None  # still pending

    def test_petition_survives_save_load(self, world):
        self._fire_first_time(world)
        world2 = WorldState.from_dict(world.to_dict())
        assert world2.pending_marshal_petition["kind"] == "jealousy_confrontation"
        result = J.handle_petition_response(world2, "acknowledge")
        assert result["success"]


class TestRivalryPetition:
    def _transition(self, world):
        ney = world.marshals["Ney"]
        soult = world.marshals["Soult"]  # authored Ney↔Soult -1... use a 0 pair
        massena = world.marshals["Massena"]
        # Massena↔Ney is unauthored (0): drive it down to -1
        changes = [{
            "marshal": "Massena", "toward": "Ney", "change": -1,
            "new_value": -1, "nation": "France",
        }]
        massena.set_relationship("Ney", -1)
        J.check_rivalry_transitions(world, changes)
        return massena, ney

    def test_downward_transition_queues_once(self, world):
        self._transition(world)
        petition = world.pending_marshal_petition
        assert petition is not None and petition["kind"] == "rivalry_confrontation"
        J.handle_petition_response(world, "let_be")
        # same transition again: seen-set blocks
        J.check_rivalry_transitions(world, [{
            "marshal": "Massena", "toward": "Ney", "change": -1,
            "new_value": -1, "nation": "France"}])
        assert world.pending_marshal_petition is None

    def test_enemy_transitions_ignored(self, world):
        J.check_rivalry_transitions(world, [{
            "marshal": "Kutuzov", "toward": "Buxhowden", "change": -1,
            "new_value": -2, "nation": "Russia"}])
        assert world.pending_marshal_petition is None

    def test_positive_changes_ignored(self, world):
        J.check_rivalry_transitions(world, [{
            "marshal": "Massena", "toward": "Ney", "change": 1,
            "new_value": 1, "nation": "France"}])
        assert world.pending_marshal_petition is None

    def test_separate_them_flags_and_warns(self, world):
        massena, ney = self._transition(world)
        # escalate to the -2 shape for the separate option
        world.pending_marshal_petition = None
        world.rivalry_transitions_seen = []
        massena.set_relationship("Ney", -2)
        J.check_rivalry_transitions(world, [{
            "marshal": "Massena", "toward": "Ney", "change": -1,
            "new_value": -2, "nation": "France"}])
        result = J.handle_petition_response(world, "separate")
        assert result["success"]
        assert massena.separation_flagged.get("Ney")
        assert ney.separation_flagged.get("Massena")
        # co-located pair produces the dispatch warning
        massena.location = ney.location
        events = _run_pass(world)
        assert any(e["type"] == "jealousy_separation_warning" for e in events)

    def test_mediate_charges_ap(self, world):
        self._transition(world)
        world.actions_remaining = 2
        result = J.handle_petition_response(world, "mediate")
        assert result["success"]
        assert world.actions_remaining == 1


# ═══════════ ENEMY JEALOUSY — BUILDING BLOCKS (spec §9b) ════════════════════


class TestEnemyJealousy:
    def test_authority_proxy_healthy(self, world):
        assert J.get_authority_proxy(world, "Austria") == 75

    def test_authority_proxy_lost_capital(self, world):
        vienna = world.get_nation_capital("Austria")
        world.regions[vienna].controller = "France"
        assert J.get_authority_proxy(world, "Austria") == 25

    def test_enemy_pair_fires_through_same_pass(self, world):
        # Kutuzov↔Buxhowden authored -1: hair trigger at delta 1 — but a
        # WHOLE Russia (capital + majority home) sits at proxy 75, which
        # SUPPRESSES (winning cures ego, spec §9b). Cost Russia its capital
        # first: the losing faction starts fracturing. Buxhowden is LITERAL
        # (sidelining trigger), so the glory-envy side of this pair is the
        # cautious Kutuzov resenting a laurelled Buxhowden.
        moscow = world.get_nation_capital("Russia")
        world.regions[moscow].controller = "France"
        assert J.get_authority_proxy(world, "Russia") == 25
        _glory(world, "Buxhowden", 2)
        _run_pass(world)
        assert world.marshals["Kutuzov"].jealous_of == "Buxhowden"

    def test_enemy_gets_no_petition_popup(self, world):
        _glory(world, "Kutuzov", 2)
        _run_pass(world)
        petition = world.pending_marshal_petition
        assert petition is None or petition["context"].get("marshal") not in (
            "Buxhowden",)

    def test_enemy_ai_glory_attack_rung(self, world):
        """A jealous aggressive ENEMY marshal reaches for the weakest
        adjacent enemy through the P3.9 rung."""
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor
        bagration_like = world.marshals["Hohenlohe"]  # Prussia, cautious
        # use an aggressive enemy: author one on the fly
        mack = world.marshals["Mack"]
        mack.personality = "aggressive"
        mack.jealous_of = "ArchdukeCharles"
        target_info = J.find_autonomous_attack_target(world, mack)
        if target_info is None:
            # bring a weak French marshal adjacent to Mack
            ney = world.marshals["Ney"]
            ney.location = "Swabia"
            ney.strength = 8000
            target_info = J.find_autonomous_attack_target(world, mack)
        assert target_info is not None
        assert bagration_like is not None  # roster sanity

    def test_glory_records_for_enemy_side(self, world):
        mack = world.marshals["Mack"]
        charles = world.marshals["ArchdukeCharles"]
        J.record_battle_glory(
            world, charles, world.marshals["Ney"], attacker_won=True,
            defender_won=False, attacker_casualties=500,
            defender_casualties=2000, conquered=False,
            pre_attacker_strength=54000, pre_defender_strength=24000)
        assert J.get_glory_score(charles, world.current_turn) > 0
        assert mack.glory_events == []


# ═══════════ AUTONOMOUS ATTACK (spec §7 + §0.2 item 7) ══════════════════════


class TestAutonomousAttack:
    def _warned_ney(self, world):
        ney = world.marshals["Ney"]
        mack = world.marshals["Mack"]
        ney.location = "Swabia"          # co-located with Mack (at-war)
        ney.jealous_of = "Davout"
        ney.jealousy_turns_remaining = 4
        return ney, mack

    def test_target_priority_weakest_adjacent(self, world):
        ney, mack = self._warned_ney(world)
        # add a weaker enemy adjacent
        charles = world.marshals["ArchdukeCharles"]
        charles.location = "Swabia"
        charles.strength = 9000
        target = J.find_autonomous_attack_target(world, ney)
        assert target is not None and target[0].name == "ArchdukeCharles"

    def test_warning_event_and_latch(self, world):
        ney, _ = self._warned_ney(world)
        events = _run_pass(world)
        assert ney.jealousy_autonomous_warned
        assert any(e["type"] == "jealousy_autonomous_warning" for e in events)

    def test_player_order_cancels_cycle(self, world):
        ney, _ = self._warned_ney(world)
        ney.jealousy_autonomous_warned = True
        note = J.cancel_autonomous_warning_on_order(world, ney)
        assert note and not ney.jealousy_autonomous_warned
        assert ney.jealous_of == "Davout"  # jealousy persists

    def test_attack_fires_at_end_turn(self, world):
        from backend.commands.executor import CommandExecutor
        ney, mack = self._warned_ney(world)
        ney.jealousy_autonomous_warned = True
        executor = CommandExecutor()
        game_state = {"world": world}
        results = J.process_autonomous_attacks(world, executor, game_state)
        assert results, "the warned attack must fire"
        assert results[0].get("jealousy_autonomous") == "Ney"
        assert not ney.jealousy_autonomous_warned
        assert ney.attacks_this_turn >= 1 or ney.in_combat_this_turn

    def test_attack_clears_standing_order(self, world):
        """EC-B: the autonomous attack clears any active strategic order."""
        from backend.commands.executor import CommandExecutor
        from backend.models.marshal import StrategicOrder
        ney, _ = self._warned_ney(world)
        ney.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Paris", target_type="region",
            started_turn=world.current_turn, original_command="move to Paris")
        ney.jealousy_autonomous_warned = True
        J.process_autonomous_attacks(world, CommandExecutor(),
                                     {"world": world})
        assert ney.strategic_order is None

    def test_no_ap_consumed(self, world):
        from backend.commands.executor import CommandExecutor
        ney, _ = self._warned_ney(world)
        ney.jealousy_autonomous_warned = True
        ap_before = world.actions_remaining
        J.process_autonomous_attacks(world, CommandExecutor(),
                                     {"world": world})
        assert world.actions_remaining == ap_before

    def test_rebuke_suppresses_cycle(self, world):
        # A10 (CA9 row 3): the latch lost its `_` prefix and is now declared
        # in `Marshal.__init__` and serialized, so a save between the rebuke
        # and the next evaluation pass no longer breaks the promise the modal
        # makes out loud ("He will not act on his own this cycle"). The
        # rename is also what puts it inside
        # `test_serialization_enforcement.py`'s derived field set, which
        # filters `_`-prefixed names — that filter is how it hid.
        ney, _ = self._warned_ney(world)
        ney.jealousy_rebuked_cycle = True
        _run_pass(world)
        assert not ney.jealousy_autonomous_warned


# ═══════════ SERIALIZATION + SURFACES ═══════════════════════════════════════


class TestSerializationAndSurfaces:
    def test_marshal_fields_round_trip(self, world):
        ney = world.marshals["Ney"]
        ney.jealous_of = "Davout"
        ney.jealousy_turns_remaining = 3
        ney.jealousy_surge_turns = 1
        ney.jealousy_autonomous_warned = True
        ney.glory_events = [{"turn": 2, "points": 3}]
        ney.jealousy_history = {"Davout": [2], "__levels__": {"Davout": 1}}
        ney.consecutive_hold_turns = 2
        ney.separation_flagged = {"Murat": True}
        ney.glory_crowned = True
        restored = Marshal.from_dict(ney.to_dict())
        assert restored.jealous_of == "Davout"
        assert restored.jealousy_turns_remaining == 3
        assert restored.jealousy_surge_turns == 1
        assert restored.jealousy_autonomous_warned is True
        assert restored.glory_events == [{"turn": 2, "points": 3}]
        assert restored.jealousy_history == {"Davout": [2],
                                             "__levels__": {"Davout": 1}}
        assert restored.consecutive_hold_turns == 2
        assert restored.separation_flagged == {"Murat": True}
        assert restored.glory_crowned is True

    def test_world_fields_round_trip(self, world):
        world.jealousy_confrontations_seen = ["Davout|Ney"]
        world.rivalry_transitions_seen = ["Massena|Ney@-1"]
        world.fontainebleau_last_turn = 7
        restored = WorldState.from_dict(world.to_dict())
        assert restored.jealousy_confrontations_seen == ["Davout|Ney"]
        assert restored.rivalry_transitions_seen == ["Massena|Ney@-1"]
        assert restored.fontainebleau_last_turn == 7

    def test_card_fields(self, world):
        from backend.game_logic.marshal_overview import build_marshal_overview
        _glory(world, "Davout", 4)
        _run_pass(world)
        cards = build_marshal_overview(world)
        davout = next(c for c in cards if c["name"] == "Davout")
        assert davout["glory"] == 4
        assert davout["glory_rank"] == 1
        assert davout["glory_crowned"] is True
        assert "jealous_of" in davout and "feuds" in davout

    def test_glory_ladder_payload(self, world):
        _glory(world, "Davout", 4)
        _glory(world, "Ney", 2)
        _run_pass(world)
        ladder = J.build_glory_ladder_payload(world)
        assert ladder[0]["name"] == "Davout" and ladder[0]["crowned"]
        assert {row["name"] for row in ladder} >= {"Ney", "Soult", "Murat"}

    def test_dispatch_whitelist_covers_events(self):
        from backend.game_logic.dispatch import _DISPATCH_EVENT_TYPES
        for etype in ("jealousy_restlessness", "jealousy_fired",
                      "jealousy_autonomous_warning", "jealousy_escalation",
                      "jealousy_resolved", "jealousy_ladder_shift",
                      "glory_crowned", "fontainebleau_petition",
                      "marshal_commissioned"):
            assert etype in _DISPATCH_EVENT_TYPES

    def test_campaign_log_formatters(self):
        from backend.campaign_log import (CAMPAIGN_LOG_TYPES, CATEGORY_MAP,
                                          format_event_oneliner)
        for etype in ("jealousy_fired", "jealousy_resolved",
                      "jealousy_escalation", "jealousy_autonomous",
                      "jealousy_confrontation", "rivalry_confrontation",
                      "glory_crowned", "fontainebleau_petition",
                      "rente_defaulted", "marshal_commissioned"):
            assert etype in CAMPAIGN_LOG_TYPES
            assert etype in CATEGORY_MAP
            line = format_event_oneliner({
                "type": etype, "marshal": "Ney", "target": "Davout",
                "other": "Davout", "nation": "France",
                "marshals": ["Ney"], "face": 40, "location": "Paris",
                "personality": "aggressive"})
            assert line and "Event:" not in line

    def test_campaign_log_player_only_fog(self, world):
        from backend.campaign_log import filter_campaign_log
        events = [
            {"type": "jealousy_fired", "marshal": "Ney", "target": "Davout",
             "nation": "France", "turn": 1},
            {"type": "jealousy_fired", "marshal": "Buxhowden",
             "target": "Kutuzov", "nation": "Russia", "turn": 1},
        ]
        filtered = filter_campaign_log(events, world)
        nations = {e["nation"] for e in filtered
                   if e["type"] == "jealousy_fired"}
        assert nations == {"France"}

    def test_berthier_note_names_grievance(self, world):
        from backend.game_logic.dispatch import _pick_berthier_note
        world.marshals["Ney"].jealous_of = "Davout"
        note = _pick_berthier_note(
            world, "France",
            [{"name": "Ney", "status": "ready", "strength": 20000}],
            {"treasury_delta": 5, "bankrupt": False})
        assert "rivalries" in note or "grievance" in note

    def test_dotation_never_touches_relationships(self):
        """The standing dotation/jealousy boundary, re-pinned from this
        side: jealousy.py owns modify_relationship, dotation never."""
        import inspect

        from backend.game_logic import dotation
        source = inspect.getsource(dotation)
        # the docstring MENTIONS the boundary; the check is for CALLS
        assert ".modify_relationship(" not in source
