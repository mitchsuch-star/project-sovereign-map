"""W6-11 — the balance duo: morale symmetry + war-priced recruitment.

Wave 6 slice 11 (docs/WAVE6_FUN_FACTOR_SPEC.md §13), deliberately LAST so
tuning isn't confounded with the legibility gains (measured in the memo §9
addendum before this landed):

1. E-CA-1 morale symmetry: casualty-scaled morale loss applies to BOTH
   sides in every outcome — a winner's delta = outcome bonus − the same
   _scaled_morale_loss curve the loser pays in that arm (blessed defender
   curve factor 1.0, band floor 0.75). Live shape fixed: Mack at morale 95
   after 15k+ casualties across three battles.
2. E-CA-3 war-priced recruitment: x3 at war (band 2-4) composed with
   x(1 + over-limit overage ratio); Europe-scoped (the legacy fixture
   boots at war — its ~20 gold_cost pins must not move); the AI pays the
   same price through the same helper (GR5), and its admin pre-checks now
   price through that helper instead of an inline copy.
"""

from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic.combat import (
    DEFENDER_MORALE_CURVE_FACTOR,
    CombatResolver,
)
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
    return WorldState.from_dict(world1805.to_dict())


def _scaled(rate, base):
    severity = min(rate / 0.15, 2.5)
    return max(base, int(base * severity))


def _deferred_deltas(atk_strength, def_strength, atk_cas, def_cas):
    """Drive the deferred (coordination) copy — deterministic in, out."""
    resolver = CombatResolver()
    attacker = Marshal("Atk", "Paris", atk_strength, "aggressive",
                       nation="France")
    defender = Marshal("Def", "Vienna", def_strength, "cautious",
                       nation="Austria")
    result = resolver._build_deferred_result(
        attacker, defender, atk_cas, def_cas,
        atk_strength, def_strength,
        {"base": 50, "modified": 50, "is_critical_success": False,
         "is_critical_failure": False}, "open", 0, None, False,
        None, None, None, None, None,
        None, None, None, None,
        None, None, None, None,
        {}, {}, False,
    )
    return (result["attacker_morale_delta"],
            result["defender_morale_delta"], result["outcome"])


# ════════════════════════════════════════════════════════════════════════
# 1. E-CA-1 — morale symmetry
# ════════════════════════════════════════════════════════════════════════


class TestMoraleSymmetry:
    def test_blessed_defender_curve_factor(self):
        assert DEFENDER_MORALE_CURVE_FACTOR == 1.0  # band floor 0.75

    def test_audit_battle_2_replay(self):
        """The acceptance case (spec §13): the audit's battle-2 numbers —
        64k attackers bleed 1.6:1 against a 50k defender who 'holds the
        line' (defender_tactical_victory, the memo's 'stalemate'). The
        HOLDER now pays for his 6.3k dead: delta +5 -> -5, a >=8-point
        drop vs the pre-change behavior; the attacker's delta is unchanged
        from today."""
        atk_delta, def_delta, outcome = _deferred_deltas(
            64000, 50000, 10050, 6300)
        assert outcome == "defender_tactical_victory"
        # Attacker: exactly today's formula (unchanged)
        assert atk_delta == -_scaled(10050 / 64000, 10)
        # Defender: bonus +5 minus the same curve (base 10) = -5
        assert def_delta == 5 - _scaled(6300 / 50000, 10)
        assert def_delta == -5
        # >= 8 points below the old flat +5
        assert (5 - def_delta) >= 8

    def test_mack_three_battle_replay_no_more_morale_95(self):
        """§2.3's exhibit: two stalemates + one hold left Mack at 95.
        Under symmetry the same three battles cost him meaningfully."""
        total = 0
        for _ in range(2):  # two stalemates at ~6% defender casualties
            _, d, outcome = _deferred_deltas(64000, 50000, 4000, 3000)
            assert outcome == "stalemate"
            total += d
        _, d, outcome = _deferred_deltas(64000, 50000, 10050, 6300)
        assert outcome == "defender_tactical_victory"
        total += d
        # Old arithmetic: -5 -5 +5 = -5 (morale 95). Now at most 85.
        assert total <= -15

    def test_decisive_winner_also_pays_in_blood(self):
        """attacker_victory: +10 minus the base-20 curve — a pyrrhic
        annihilation no longer refunds morale."""
        atk_delta, def_delta, outcome = _deferred_deltas(
            50000, 20000, 15000, 20000)
        assert outcome == "attacker_victory"
        assert atk_delta == 10 - _scaled(15000 / 50000, 20)
        assert atk_delta < 0  # 30% casualties: the "victory" hurts

    def test_stalemate_stays_symmetric(self):
        atk_delta, def_delta, outcome = _deferred_deltas(
            50000, 50000, 5000, 5000)
        assert outcome == "stalemate"
        assert atk_delta == def_delta == -_scaled(0.1, 5)

    def test_bloodless_win_keeps_full_bonus(self):
        """A winner with trivial casualties keeps (nearly) the old bonus
        minus the floor — the change punishes BLOOD, not winning."""
        atk_delta, def_delta, outcome = _deferred_deltas(
            60000, 50000, 12000, 2000)
        assert outcome == "defender_tactical_victory"
        # 4% casualties: floor gives base 10 -> delta -5; the defender
        # who barely bled is still better off than the mauled attacker
        assert def_delta > atk_delta

    def test_normal_path_matches_deferred_table(self):
        """The normal (apply_casualties=True) path must land the same
        winner arithmetic — derived post-hoc from the battle's own
        recorded casualties (no RNG assumptions)."""
        resolver = CombatResolver()
        attacker = Marshal("Atk", "Paris", 30000, "aggressive",
                           nation="France")
        defender = Marshal("Def", "Vienna", 60000, "cautious",
                           nation="Austria")
        result = resolver.resolve_battle(attacker, defender)
        event = result["log_battle_event"]
        def_cas = event["defender_casualties"]
        outcome = event["outcome"]
        def_rate = def_cas / 60000
        expected = {
            "defender_victory": 10 - _scaled(def_rate, 20),
            "attacker_victory": -_scaled(def_rate, 20),
            "defender_tactical_victory": 5 - _scaled(def_rate, 10),
            "attacker_tactical_victory": -_scaled(def_rate, 10),
            "stalemate": -_scaled(def_rate, 5),
            "mutual_destruction": -_scaled(def_rate, 20),
        }[outcome]
        assert defender.morale == max(0, min(100, 100 + expected))


# ════════════════════════════════════════════════════════════════════════
# 1b. W6-11 review guards — the victor never routs from his own victory
# ════════════════════════════════════════════════════════════════════════


class TestVictorNeverRoutedByOwnVictory:
    def test_victor_never_flagged_forced_retreat(self):
        """Post-review guard: the symmetric morale cost can drop a WINNER
        below the forced-retreat threshold — but a marshal never flees the
        field he just won. Invariant across seeds and both sides."""
        import random as _random
        resolver = CombatResolver()
        for seed in range(30):
            _random.seed(seed)
            attacker = Marshal("Atk", "Paris", 30000, "aggressive",
                               nation="France")
            defender = Marshal("Def", "Vienna", 45000, "cautious",
                               nation="Austria")
            attacker.morale = 30
            defender.morale = 30
            result = resolver.resolve_battle(attacker, defender)
            outcome = result["log_battle_event"]["outcome"]
            if outcome in ("attacker_victory", "attacker_tactical_victory"):
                assert result["attacker"]["forced_retreat"] is False
            if outcome in ("defender_victory", "defender_tactical_victory"):
                assert result["defender"]["forced_retreat"] is False

    def test_loser_still_routs_below_threshold(self):
        """The guard exempts only the victor — a loser (or stalemate side)
        under the threshold keeps the old rule."""
        import random as _random
        resolver = CombatResolver()
        seen_loser_rout = False
        for seed in range(60):
            _random.seed(seed)
            attacker = Marshal("Atk", "Paris", 20000, "aggressive",
                               nation="France")
            defender = Marshal("Def", "Vienna", 60000, "cautious",
                               nation="Austria")
            attacker.morale = 35
            result = resolver.resolve_battle(attacker, defender)
            outcome = result["log_battle_event"]["outcome"]
            if (outcome in ("defender_victory", "defender_tactical_victory")
                    and attacker.strength > 0 and attacker.morale <= 25):
                assert result["attacker"]["forced_retreat"] is True
                seen_loser_rout = True
        assert seen_loser_rout, "no losing-rout case sampled — widen seeds"

    def test_annihilated_enemy_takes_no_prisoners(self, world):
        """W6-7 fate hardening: the fate machinery needs a LIVE captor —
        a destroyed army cannot capture the marshal who destroyed it."""
        executor = CommandExecutor()
        marshal = world.marshals["Ney"]
        marshal.strength = 3000  # under the fate floor
        enemy = next(m for m in world.marshals.values()
                     if m.nation == "Austria")
        enemy.strength = 0  # annihilated
        outcome = executor._combat._check_marshal_fate(marshal, enemy, world)
        assert outcome is None
        assert not getattr(marshal, "captured_by", "")


# ════════════════════════════════════════════════════════════════════════
# 2. E-CA-3 — war-priced recruitment
# ════════════════════════════════════════════════════════════════════════


class TestWarPricedRecruitment:
    def _cost(self, world, nation, base=200, region=None):
        executor = CommandExecutor()
        if region is None:
            region = next(
                r for r in world.regions.values()
                if r.controller == nation and r.region_type != "capital"
                and not (51 <= r.stability <= 75))
        return executor._calculate_recruit_cost(
            region, world, base_cost=base, nation=nation)

    @staticmethod
    def _peaceful_in_limit_nation(world):
        for nation in world.get_active_nations():
            if world.get_nations_at_war_with(nation):
                continue
            if world.calculate_turn_upkeep(nation)["over_limit"]:
                continue
            if not world.get_nation_regions(nation):
                continue
            return nation
        pytest.skip("no peaceful in-limit nation at boot")

    def test_war_multiplier_applies_on_europe(self, world):
        """At war -> x3; at peace within the force limit -> base price.
        (Prussia is at peace but OVER its boot force limit — so the
        peacetime control is chosen dynamically.)"""
        peaceful = self._peaceful_in_limit_nation(world)
        assert self._cost(world, peaceful) == 200
        # Austria is at war at the 1805 boot -> x3 composes on its
        # (possible) overage — assert the war factor is present
        assert world.get_nations_at_war_with("Austria")
        assert self._cost(world, "Austria") >= 600

    def test_war_and_overlimit_compose(self, world):
        """France at the 1805 boot: at war AND over the force limit —
        both multipliers compose on the regional price."""
        upkeep = world.calculate_turn_upkeep("France")
        limit = world.get_force_limit("France")
        total = upkeep["total_strength"]
        assert total > limit  # 189k vs ~130k at boot
        overage = (total - limit) / limit
        expected = int(int(200 * 3) * (1.0 + overage))
        assert self._cost(world, "France") == expected

    def test_peacetime_europe_unchanged(self, world):
        peaceful = self._peaceful_in_limit_nation(world)
        assert self._cost(world, peaceful, base=300) == 300
        # And Prussia's boot overage prices exactly (1 + overage) at peace
        upkeep = world.calculate_turn_upkeep("Prussia")
        if upkeep["over_limit"]:
            limit = world.get_force_limit("Prussia")
            overage = (upkeep["total_strength"] - limit) / limit
            assert self._cost(world, "Prussia") == int(200 * (1.0 + overage))

    def test_legacy_world_prices_never_move(self):
        """N1: the legacy fixture world BOOTS at war with Britain and
        Prussia — the war multiplier is Europe-scoped so every historical
        gold_cost pin holds."""
        legacy = WorldState(player_nation="France")
        assert legacy.is_at_war("France", "Britain")
        executor = CommandExecutor()
        region = next(r for r in legacy.regions.values()
                      if r.region_type != "capital"
                      and not (51 <= r.stability <= 75))
        assert executor._calculate_recruit_cost(
            region, legacy, base_cost=200, nation="France") == 200

    def test_ai_precheck_prices_through_the_same_helper(self, world):
        """GR5: the AI's admin affordability pre-check must see the same
        war-priced number the executor will charge — an optimistic inline
        copy would make the AI attempt-and-fail every admin phase."""
        from backend.ai.enemy_ai import EnemyAI
        ai = EnemyAI(CommandExecutor())
        nation = "Austria"
        assert world.get_nations_at_war_with(nation)
        weakest = ai._find_weakest_marshal_for_admin(nation, world)
        if weakest is None:
            pytest.skip("no admin-recruit candidate at boot")
        region = world.get_region(weakest.location)
        if region is None or region.stability <= 50:
            pytest.skip("candidate region ineligible at boot")
        true_cost = ai.executor._calculate_recruit_cost(
            region, world,
            base_cost=300 if getattr(weakest, "cavalry", False) else 200,
            nation=nation)
        # Treasury below the TRUE price but above the old naive price:
        # the pre-check must NOT pick recruit.
        world.nation_gold[nation] = true_cost - 1
        action = ai._pick_admin_action(nation, world, admin_ap=1)
        assert not (action and action.get("action") == "recruit")

    def test_every_at_war_1805_nation_affords_the_cadence(self, world):
        """The two-sided AI-solvency check (mirrors test_economy_e1_band):
        every 1805 nation at war can pay a war-priced infantry recruit
        from treasury + three turns of positive net income — if a minor
        breaks, the war multiplier drops toward 2x within band."""
        for nation in world.get_active_nations():
            if not world.get_nations_at_war_with(nation):
                continue
            regions = [world.regions[r]
                       for r in world.get_nation_regions(nation)]
            if not regions:
                continue
            region = next((r for r in regions if r.region_type == "capital"),
                          regions[0])
            cost = CommandExecutor()._calculate_recruit_cost(
                region, world, base_cost=200, nation=nation)
            income = world.calculate_turn_income(nation)
            upkeep = world.calculate_turn_upkeep(nation)
            net = (income["income"] - income["occupation"]
                   - income["dotation_skim"] - upkeep["total"])
            budget = world.nation_gold.get(nation, 0) + 3 * max(0, net)
            assert cost <= budget, (
                f"{nation} cannot afford a war-priced recruit "
                f"({cost}g vs budget {budget}g)")

    def test_recruit_flows_into_the_spent_line(self, world):
        """Ledger visibility: the (now much larger) recruit spend shows in
        the economy report's Spent line."""
        executor = CommandExecutor()
        ney = world.marshals["Ney"]
        region = world.get_region(ney.location)
        region.stability = 80
        world.nation_gold["France"] = 20000
        result = executor.execute(
            {"command": {"marshal": "Ney", "action": "recruit",
                         "type": "specific"}},
            {"world": world},
        )
        assert result["success"] is True, result.get("message")
        gold_cost = result["events"][0]["gold_cost"]
        assert gold_cost >= 600  # war-priced (>= 200 x 3)
        assert world.gold_spent_this_turn.get("France", 0) >= gold_cost
        report = executor.execute(
            {"command": {"action": "economy", "type": "meta"}},
            {"world": world},
        )
        assert "Spent this turn" in report["message"]
