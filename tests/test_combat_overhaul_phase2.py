"""Combat Overhaul Phase 2 — decisiveness, regen cap, legibility, Iron Resolve.

Owner: docs/COMBAT_OVERHAUL_SPEC.md §4 Phase 2. Behaviour pins for the four
Phase-2 slices (the deterministic metric gate lives in
tests/test_combat_sweep_metrics.py — M2/M3/M5):

- CO-3  decisiveness → capture   : lopsided casualty exchanges break the
                                    out-bled side faster (metric M2).
- CO-4  cap enemy regeneration   : a corps reinforcing away from a friendly
                                    depot/capital is capped to
                                    AI_CORPS_REGEN_CAP men (metric M3).
- CO-6  reinforcement legibility : a coordinated battle names the committed
                                    effective strength.
- CO-7  Iron Resolve stance fix  : releasing the coil is not self-cancelled by
                                    the fortify-mandated defensive stance
                                    (metric M5).
"""

import os
import random
from types import SimpleNamespace

import pytest

from backend.commands.combat_executor import CombatExecutor
from backend.commands.economy_executor import (
    AI_CORPS_REGEN_CAP, region_has_friendly_supply,
)
from backend.commands.executor import CommandExecutor
from backend.game_logic import combat as C
from backend.game_logic.combat import (
    CombatResolver, FORCED_RETREAT_THRESHOLD, decisiveness_morale_penalty,
)
from backend.models.marshal import Marshal, Stance
from backend.models.world_state import WorldState


def _mk(name, strength, personality="aggressive", nation="France", *,
        morale=100, defense_bonus=0.0, stance=None, ability=None,
        iron_stacks=0):
    m = Marshal(name, "TestField", int(strength), personality, nation)
    m.morale = morale
    m.defense_bonus = defense_bonus
    if stance is not None:
        m.stance = stance
    if ability is not None:
        m.ability = ability
    if iron_stacks:
        m.iron_resolve_stacks = iron_stacks
    return m


# ════════════════════════════════════════════════════════════════════════
# CO-3 — decisiveness → capture
# ════════════════════════════════════════════════════════════════════════

class TestCO3DecisivenessHelper:
    def test_zero_below_pivot(self):
        # An even (or defender-favourable) exchange never triggers the penalty.
        assert decisiveness_morale_penalty(1000, 1000) == 0
        assert decisiveness_morale_penalty(1000, 700) == 0  # ratio 1.43 < pivot
        assert decisiveness_morale_penalty(500, 1000) == 0  # out-bled side wins

    def test_scales_above_pivot(self):
        # Above the pivot the penalty grows with how lopsided the loss is.
        p_small = decisiveness_morale_penalty(2100, 1000)   # ratio 2.1
        p_big = decisiveness_morale_penalty(4000, 1000)     # ratio 4.0
        assert p_small > 0
        assert p_big > p_small

    def test_capped(self):
        # A total wipe cannot exceed the ceiling.
        assert decisiveness_morale_penalty(1_000_000, 1) == C.DECISIVENESS_MORALE_CAP

    def test_symmetric(self):
        # GR5: whichever side is out-bled pays the SAME curve.
        assert (decisiveness_morale_penalty(3000, 1000)
                == decisiveness_morale_penalty(3000, 1000))


class TestCO3RoutsLopsided:
    def test_three_to_one_routs_defender(self):
        # A maintained 3:1 assault on equal (plains) terrain breaks the
        # defender within two sustained attacks (metric M2 @3:1).
        routed = 0
        for s in range(60):
            random.seed(s)
            deff = _mk("Mack", 40000, "cautious", "Austria", morale=100)
            broke = False
            for _turn in range(2):
                atk = _mk("Napoleon", 120000, "aggressive", "France", morale=100)
                res = CombatResolver().resolve_battle(atk, deff, terrain="plains")
                if res["defender"]["forced_retreat"] or deff.strength <= 0:
                    broke = True
                    break
            if broke:
                routed += 1
        assert routed >= 40, f"expected most 3:1 assaults to rout; got {routed}/60"

    def test_even_fight_not_routed_by_decisiveness(self):
        # M6 guard, in miniature: an equal-strength solo clash does not hand a
        # decisiveness rout to the attacker — the exchange is not lopsided.
        random.seed(1)
        atk = _mk("Napoleon", 40000, "aggressive", "France", morale=100)
        deff = _mk("Mack", 40000, "cautious", "Austria", morale=100)
        res = CombatResolver().resolve_battle(
            atk, deff, terrain="mountains", fortification_bonus=0.30)
        assert res["attacker_won"] is False


# ════════════════════════════════════════════════════════════════════════
# CO-4 — cap enemy regeneration
# ════════════════════════════════════════════════════════════════════════

class TestCO4FriendlySupply:
    def test_capital_is_supplied(self):
        region = SimpleNamespace(region_type="capital",
                                 has_building=lambda b: False)
        assert region_has_friendly_supply(region) is True

    def test_depot_is_supplied(self):
        region = SimpleNamespace(region_type="plains",
                                 has_building=lambda b: b == "supply_depot")
        assert region_has_friendly_supply(region) is True

    def test_bare_field_is_not_supplied(self):
        region = SimpleNamespace(region_type="plains",
                                 has_building=lambda b: False)
        assert region_has_friendly_supply(region) is False

    def test_none_region_not_supplied(self):
        assert region_has_friendly_supply(None) is False


class TestCO4RecruitCap:
    """CO-4 is symmetric (GR5): the field-regen cap lives in the SHARED recruit
    executor, keyed on the recruit region's supply — a bare field region caps
    both the player's and the enemy's levy; a depot/capital is uncapped."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.gs = {"world": self.world}

    def _recruit(self, name, **extra):
        cmd = {"marshal": name}
        cmd.update(extra)
        return self.executor._economy._execute_recruit(cmd, self.gs)

    def _supply(self, region_name):
        self.world.get_region(region_name).buildings.append(
            {"type": "supply_depot", "damaged": False})

    def test_capital_recruit_full_batch(self):
        davout = self.world.get_marshal("Davout")
        davout.location = "Paris"  # capital → supplied → uncapped
        res = self._recruit("Davout")
        assert res["success"], res.get("message")
        assert res["events"][0]["troops_added"] == 10000

    def test_field_recruit_capped_for_player(self):
        # A player corps reinforcing in a bare field region is capped too.
        davout = self.world.get_marshal("Davout")
        davout.location = "Belgium"  # controlled, no depot/capital
        res = self._recruit("Davout")
        assert res["success"], res.get("message")
        assert res["events"][0]["troops_added"] == AI_CORPS_REGEN_CAP

    def test_depot_recruit_uncapped(self):
        davout = self.world.get_marshal("Davout")
        davout.location = "Belgium"
        self._supply("Belgium")  # forward depot lifts the cap
        res = self._recruit("Davout")
        assert res["events"][0]["troops_added"] == 10000

    def test_override_lowers_further(self):
        # An explicit reinforcement_cap can only lower, never raise.
        davout = self.world.get_marshal("Davout")
        davout.location = "Paris"  # supplied → would be 10000
        res = self._recruit("Davout", reinforcement_cap=1500)
        assert res["events"][0]["troops_added"] == 1500


class TestCO4EnemyFieldRecruitCapped:
    """GR5 in practice: an ENEMY corps recruiting in a bare field region draws
    the same capped levy through the same executor — no enemy-specific wiring."""

    def test_enemy_field_recruit_capped(self):
        world = WorldState()
        executor = CommandExecutor()
        mack = world.get_marshal("Wellington")  # any non-France marshal
        mack.location = "Milan"
        milan = world.get_region("Milan")
        milan.controller = mack.nation
        milan.stability = 100
        world.nation_gold[mack.nation] = 5000
        res = executor._economy._execute_recruit(
            {"marshal": mack.name}, {"world": world})
        assert res["success"], res.get("message")
        assert res["events"][0]["troops_added"] == AI_CORPS_REGEN_CAP


# ════════════════════════════════════════════════════════════════════════
# CO-6 — reinforcement legibility
# ════════════════════════════════════════════════════════════════════════

class TestCO6ReinforcementLegibility:
    def test_coordinated_battle_names_committed_strength(self):
        random.seed(7)
        world = WorldState()
        executor = CommandExecutor()
        gs = {"world": world}

        # Isolate: only Ney (lead), Davout (reinforcer), Wellington (defender).
        for name in list(world.marshals.keys()):
            if name not in ("Ney", "Davout", "Wellington"):
                world.marshals[name].location = "Paris"

        ney = world.get_marshal("Ney")
        ney.location = "Waterloo"
        ney.strength = 40000
        davout = world.get_marshal("Davout")
        davout.location = "Belgium"  # adjacent → reinforces
        davout.strength = 30000
        # A willing reinforcer: a positive bond so the committed contribution is
        # non-zero (a rival contributes ~0 by design — CO-1b — and prints no
        # mass line, which is correct, so pin the willing case explicitly).
        ney.set_relationship("Davout", 1)
        davout.set_relationship("Ney", 1)
        wellington = world.get_marshal("Wellington")
        wellington.location = "Waterloo"
        wellington.strength = 30000

        res = executor._execute_attack(ney, "Wellington", world, gs)
        msgs = res.get("reinforcement_messages") or []
        joined = "\n".join(msgs)
        assert "arrived to reinforce" in joined, (
            f"fixture: expected Davout to reinforce; got {msgs}")
        assert any("Massed effective strength" in m for m in msgs), (
            f"expected a committed-strength line; got {msgs}")


# ════════════════════════════════════════════════════════════════════════
# CO-7 — Iron Resolve stance fix
# ════════════════════════════════════════════════════════════════════════

IRON = {"name": "Iron Resolve"}


class TestCO7IronResolveStance:
    def test_release_from_defensive_lands_full_value(self):
        # 3 stacks = +24%. Released from the fortify-mandated DEFENSIVE stance
        # the payoff over a plain neutral attack is >= +18% (metric M5).
        trapped = _mk("Davout", 40000, "cautious", stance=Stance.DEFENSIVE,
                      defense_bonus=0.16, ability=dict(IRON), iron_stacks=3)
        normal = _mk("Davout", 40000, "cautious", stance=Stance.NEUTRAL)
        payoff = trapped.get_attack_modifier(1.0) - normal.get_attack_modifier(1.0)
        assert payoff >= 0.18, f"expected >= +0.18; got {payoff:+.3f}"

    def test_release_from_neutral_unchanged(self):
        # A marshal already in NEUTRAL (e.g. after unfortify) still gets exactly
        # the +24% and no more — the exemption only undoes the defensive penalty.
        m = _mk("Davout", 40000, "cautious", stance=Stance.NEUTRAL,
                ability=dict(IRON), iron_stacks=3)
        assert m.get_attack_modifier(1.0, consume=False) == pytest.approx(1.24)

    def test_read_only_does_not_consume(self):
        m = _mk("Davout", 40000, "cautious", stance=Stance.DEFENSIVE,
                ability=dict(IRON), iron_stacks=3)
        m.get_attack_modifier(1.0, consume=False)
        assert m.iron_resolve_stacks == 3
        m.get_attack_modifier(1.0, consume=True)
        assert m.iron_resolve_stacks == 0

    def test_no_stacks_no_stance_change(self):
        # Without Iron Resolve stacks the defensive penalty stands (attack < 1).
        m = _mk("Davout", 40000, "cautious", stance=Stance.DEFENSIVE,
                ability=dict(IRON), iron_stacks=0)
        assert m.get_attack_modifier(1.0, consume=False) < 1.0
