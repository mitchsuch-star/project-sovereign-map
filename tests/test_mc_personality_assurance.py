"""MC-V — personality-kit assurance (both sides) + enemy-AI-per-personality eval.

Marshal Content Pass, slice MC-V (gate memo §6.7 / spec §2 MC-V row).

Two halves, both landed here:

**(a) Personality-kit assurance.** Every personality type's MECHANICAL grants
must fire for BOTH a player-nation and an enemy-nation marshal through the SAME
combat/executor path (Golden Rule 5 — "Enemy AI uses SAME executor as player").
The modifier seams (`get_attack_modifier`/`get_defense_modifier`) and the
behavior seams (counter-punch trigger, recklessness, order-cost) all read
`self.personality` and never the nation, so the grant is side-agnostic by
construction — these classes pin that as a standing regression gate.

Grants that turn out to be PLAYER-ONLY IN EFFECT are pinned here as KNOWN
behavior (never left as silent gaps) and routed to
`docs/BUG_FIXES.md` §"MC-V Enemy-AI Personality Findings":
  - Literal Precision-Execution / ambiguity combat buff is granted only from a
    player-gated seam (`executor.py:1254`, `is_player_action_check`); an enemy
    literal never receives it. (Routed: MC-V-1.)
  - The literal 1-AP strategic-order discount only ever discounts the player's
    AP pool; enemy strategic execution bypasses AP entirely, so there is no
    enemy-side surface. (Routed: MC-V-1.)

**(b) Enemy-AI-per-personality evaluation.** Verify opposing generals PLAY
their personality rather than merely carrying the label. The headline finding —
`enemy_ai._get_effective_personality` aliases literal→cautious for every
AI-controlled marshal, so enemy literals (Mack, Buxhowden) play as cautious
clones — is pinned as the current documented behavior and routed (MC-V-2).
Aggressive is well-differentiated; cautious/literal converge.

The exhaustive enemy-side ABILITY seam pins (Charles rout threshold, Kutuzov
pursuit/attrition halving, Moore recruit floor) live in
`test_marshal_content_mc1b_t1_abilities.py` (memo §6.2); this file adds the
observed / AI-path angle only.

Full eval write-up: `docs/audits/MC_V_PERSONALITY_EVAL_2026_07_10.md`.
"""

import random
import random as _random

import pytest

from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
from backend.game_logic.combat import CombatResolver, FORCED_RETREAT_THRESHOLD
from backend.models.marshal import Marshal
from backend.models.personality import PERSONALITY_TRIGGERS, Personality
from backend.models.personality_modifiers import (
    get_fortify_rate,
    get_instant_fortify_bonus,
    get_max_fortify_bonus,
)
from backend.models.world_state import WorldState


# ════════════════════════════════════════════════════════════════════════
# Local helpers (mirror the MC-1b/1c idiom)
# ════════════════════════════════════════════════════════════════════════

def make_marshal(name, location="Belgium", strength=30000, nation="France",
                 personality="cautious", ability=None, cavalry=False,
                 morale=100, **kw):
    m = Marshal(name=name, location=location, strength=strength,
                personality=personality, nation=nation,
                movement_range=2 if cavalry else 1,
                ability=ability, cavalry=cavalry, spawn_location=location)
    m.morale = morale
    for k, v in kw.items():
        setattr(m, k, v)
    return m


def make_world(*marshals, wars=(("France", "Britain"),)):
    w = WorldState()
    w.marshals = {m.name: m for m in marshals}
    for a, b in wars:
        key = w._make_diplo_key(a, b)
        w.diplomatic_states[key] = "WAR"
    return w


def execute_attack(world, attacker_name, target_name):
    executor = CommandExecutor()
    command = {"command": {
        "marshal": attacker_name,
        "action": "attack",
        "target": target_name,
        "_muster_confirmed": True,  # skip the W6-4 muster-preview interrupt
    }}
    return executor.execute(command, {"world": world})


FIXED_DICE = {
    "natural": 7, "modified": 9, "is_critical_success": False,
    "is_critical_failure": False, "multiplier": 1.0,
    "skill_bonus": 2, "flanking_bonus": 0,
}


@pytest.fixture()
def fixed_rng(monkeypatch):
    """Fully deterministic combat: fixed dice, midpoint variance, no fumble."""
    monkeypatch.setattr(CombatResolver, "roll_combat_dice",
                        lambda self, marshal, flanking_bonus=0: dict(FIXED_DICE))
    monkeypatch.setattr(_random, "uniform", lambda a, b: (a + b) / 2.0)
    monkeypatch.setattr(_random, "randint", lambda a, b: (a + b) // 2)
    monkeypatch.setattr(_random, "random", lambda: 0.0)
    monkeypatch.setattr(_random, "choice", lambda seq: seq[0])


@pytest.fixture()
def zero_variance(monkeypatch):
    """Pin AI mood variance to 0 so the mood-adjusted threshold == base."""
    monkeypatch.setattr(_random, "uniform", lambda a, b: (a + b) / 2.0)
    monkeypatch.setattr(_random, "randint", lambda a, b: (a + b) // 2)


# ════════════════════════════════════════════════════════════════════════
# HALF (a) — AGGRESSIVE KIT (both sides)
# ════════════════════════════════════════════════════════════════════════

class TestAggressiveKitBothSides:
    """+15% base attack and recklessness escalation fire identically for a
    player-nation and an enemy-nation aggressive marshal."""

    @pytest.mark.parametrize("nation", ["France", "Prussia"])
    def test_plus_15_attack_base(self, nation):
        aggr = make_marshal("A", nation=nation, personality="aggressive")
        ctrl = make_marshal("C", nation=nation, personality="cautious")
        # cautious, neutral stance, no odds context → 1.0; aggressive → 1.15
        assert aggr.get_attack_modifier() == pytest.approx(1.15)
        assert ctrl.get_attack_modifier() == pytest.approx(1.0)

    @pytest.mark.parametrize("nation", ["France", "Prussia"])
    def test_recklessness_escalation(self, nation):
        cav = make_marshal("Cav", nation=nation, personality="aggressive",
                           cavalry=True)
        assert cav.is_reckless_cavalry is True
        cav.recklessness = 3
        assert cav._get_recklessness_attack_bonus() == pytest.approx(0.15)
        assert cav._get_recklessness_defense_penalty() == pytest.approx(0.10)

    def test_recklessness_gate_requires_cavalry_and_aggressive(self):
        inf_aggr = make_marshal("Inf", personality="aggressive", cavalry=False)
        cav_caut = make_marshal("CavCaut", personality="cautious", cavalry=True)
        assert inf_aggr.is_reckless_cavalry is False
        assert cav_caut.is_reckless_cavalry is False

    def test_enemy_aggressive_bonus_flows_through_resolve_battle(self, fixed_rng):
        # Same battle, only the attacker's personality differs; the aggressive
        # +15% must produce strictly more defender casualties through the shared
        # resolve_battle path — the enemy-side grant is live in real combat.
        def _defender_left(personality):
            atk = make_marshal("Atk", nation="Prussia", personality=personality,
                               strength=40000, location="Belgium")
            dfn = make_marshal("Dfn", nation="France", personality="cautious",
                               strength=40000, location="Belgium", morale=100)
            CombatResolver().resolve_battle(atk, dfn)
            return dfn.strength
        aggr_left = _defender_left("aggressive")
        caut_left = _defender_left("cautious")
        assert aggr_left < caut_left

    def test_recklessness_builds_for_enemy_cavalry_on_win(self, fixed_rng):
        # An enemy reckless-cavalry marshal escalates through resolve_battle too.
        murat = make_marshal("MuratEnemy", nation="Prussia",
                             personality="aggressive", cavalry=True,
                             strength=45000, location="Belgium")
        weak = make_marshal("Weak", nation="France", personality="cautious",
                            strength=8000, location="Belgium", morale=40)
        assert murat.recklessness == 0
        CombatResolver().resolve_battle(murat, weak)
        assert murat.recklessness == 1


# ════════════════════════════════════════════════════════════════════════
# HALF (a) — CAUTIOUS KIT (both sides)
# ════════════════════════════════════════════════════════════════════════

class TestCautiousKitBothSides:
    """Outnumbered-defense bonus, counter-punch, and fortify caps fire for a
    player-nation and an enemy-nation cautious marshal."""

    @pytest.mark.parametrize("nation", ["France", "Prussia"])
    def test_outnumbered_defense_plus_10(self, nation):
        out = make_marshal("D", nation=nation,
                           personality="cautious").get_defense_modifier(
            is_outnumbered=True)
        base = make_marshal("D2", nation=nation,
                            personality="cautious").get_defense_modifier(
            is_outnumbered=False)
        assert out == pytest.approx(base * 1.10)

    @pytest.mark.parametrize("def_nation,atk_nation",
                             [("France", "Prussia"), ("Prussia", "France")])
    def test_counter_punch_granted_to_cautious_defender(self, def_nation,
                                                        atk_nation, fixed_rng):
        atk = make_marshal("Atk", nation=atk_nation, personality="aggressive",
                           strength=18000, location="Belgium", morale=100)
        dfn = make_marshal("Dfn", nation=def_nation, personality="cautious",
                           strength=45000, location="Belgium", morale=100)
        CombatResolver().resolve_battle(atk, dfn)
        assert dfn.counter_punch_available is True

    def test_counter_punch_not_granted_to_aggressive_defender(self, fixed_rng):
        atk = make_marshal("Atk", nation="Prussia", personality="aggressive",
                           strength=18000, location="Belgium", morale=100)
        dfn = make_marshal("Dfn", nation="France", personality="aggressive",
                           strength=45000, location="Belgium", morale=100)
        CombatResolver().resolve_battle(atk, dfn)
        assert dfn.counter_punch_available is False

    def test_counter_punch_consumed_by_enemy_free_attack(self, fixed_rng):
        # The consume seam (_execute_attack) clears the flag for an ENEMY
        # cautious marshal — the free-attack mechanic is side-agnostic.
        enemy = make_marshal("EnDef", nation="Britain", personality="cautious",
                             strength=45000, location="Waterloo", morale=100)
        enemy.counter_punch_available = True
        enemy.counter_punch_turns = 2
        target = make_marshal("Fr", nation="France", personality="cautious",
                             strength=20000, location="Waterloo", morale=100)
        world = make_world(enemy, target)
        execute_attack(world, "EnDef", "Fr")
        assert enemy.counter_punch_available is False

    def test_fortify_helpers_are_side_agnostic_constants(self):
        # The fortify helpers key only on the personality STRING; per-turn
        # growth in world_state._process_tactical_states iterates ALL marshals
        # ungated (agent-verified), so the cautious kit fortifies both sides.
        assert get_fortify_rate("cautious") == pytest.approx(0.03)
        assert get_instant_fortify_bonus("cautious") == pytest.approx(0.05)
        assert get_max_fortify_bonus("cautious") == pytest.approx(0.12)
        assert get_max_fortify_bonus("aggressive") == pytest.approx(0.08)


# ════════════════════════════════════════════════════════════════════════
# HALF (a) — LITERAL KIT (both sides where the mechanic is shared)
# ════════════════════════════════════════════════════════════════════════

class TestLiteralKitBothSides:
    """The one literal COMBAT mechanic that is genuinely both-sides — Immovable
    (+15% defense while holding position) — plus the never-objects invariant."""

    @pytest.mark.parametrize("nation", ["France", "Austria"])
    def test_immovable_hold_defense_plus_15(self, nation):
        held = make_marshal("L", nation=nation, personality="literal",
                            holding_position=True).get_defense_modifier()
        free = make_marshal("L2", nation=nation, personality="literal",
                            holding_position=False).get_defense_modifier()
        assert held == pytest.approx(free * 1.15)

    def test_literal_never_objects_invariant(self):
        # W6-5 Literal Doctrine holds as an MC-V invariant: literal marshals
        # carry ZERO objection triggers (objections are player-only by nature;
        # the empty table guarantees a literal never objects, both sides).
        assert PERSONALITY_TRIGGERS[Personality.LITERAL] == {}


# ════════════════════════════════════════════════════════════════════════
# HALF (a) — PLAYER-ONLY ASYMMETRIES (pinned as KNOWN behavior; routed)
# ════════════════════════════════════════════════════════════════════════

class TestPlayerOnlyAsymmetries:
    """Literal grants that are player-only IN EFFECT. Pinned as known behavior
    and routed to BUG_FIXES.md §MC-V (finding MC-V-1)."""

    def test_precision_execution_mechanic_is_side_agnostic(self):
        # The buff FUNCTION itself is GR5-clean — it works for ANY literal
        # marshal, including an enemy one, if it is ever invoked.
        meta = CommandExecutor()._meta
        enemy = make_marshal("Mack", nation="Austria", personality="literal")
        meta._apply_grouchy_ambiguity_buff(enemy, ambiguity=0,
                                           strategic_score=100, action="attack")
        assert enemy.precision_execution_active is True
        assert enemy.strategic_combat_bonus == 15
        assert enemy.strategic_defense_bonus == 15

    def test_precision_execution_never_reaches_enemy_literal_via_ai(self):
        # ROUTED (MC-V-1): the ONLY caller of the buff is player-gated
        # (executor.py:1254, is_player_action_check). An enemy literal marshal
        # that has taken a full AI turn still carries no Precision Execution.
        world = WorldState()  # legacy world, player = France
        wellington = world.get_marshal("Wellington")
        wellington.personality = "literal"
        wellington.precision_execution_active = False
        wellington.strategic_combat_bonus = 0
        random.seed(20260710)
        EnemyAI(CommandExecutor()).process_nation_turn(
            "Britain", world, {"world": world, "debug_mode": True})
        assert wellington.precision_execution_active is False
        assert wellington.strategic_combat_bonus == 0

    def test_literal_order_cost_is_player_economy(self):
        # The 1-AP strategic discount is computed symmetrically, but only ever
        # discounts the PLAYER's AP pool (enemy strategic execution bypasses AP).
        # Pin the player-facing discount: literal costs 1 less AP than cautious
        # for the identical strategic MOVE_TO. Fresh world per measurement so the
        # first move cannot contaminate the second.
        def _cost(personality):
            world = WorldState()  # legacy world, player = France
            ney = world.get_marshal("Ney")
            ney.personality = personality
            ney.location = "Paris"
            ney.strength = 30000
            # clear the path so the order is issued (no first-step block)
            for m in world.marshals.values():
                if m.nation != "France":
                    m.strength = 0
            world.actions_remaining = 5
            before = world.actions_remaining
            CommandExecutor().execute({
                "command": {"raw_input": "Ney, march to Rhineland",
                            "marshal": "Ney", "action": "move",
                            "target": "Rhineland"},
                "is_strategic": True, "strategic_type": "MOVE_TO",
            }, {"world": world})
            return before - world.actions_remaining
        literal_cost = _cost("literal")
        cautious_cost = _cost("cautious")
        assert literal_cost == 1
        assert cautious_cost == 2


# ════════════════════════════════════════════════════════════════════════
# HALF (b) — ENEMY-AI PERSONALITY DIFFERENTIATION
# ════════════════════════════════════════════════════════════════════════

class TestEnemyAIPersonalityDifferentiation:
    """Do opposing generals PLAY their personality? Aggressive vs cautious
    diverge; literal collapses to cautious (routed finding MC-V-2)."""

    def _ai(self):
        return EnemyAI(CommandExecutor())

    def test_effective_personality_enemy_literal_aliases_to_cautious(self):
        # FINDING MC-V-2: _get_effective_personality converts literal→cautious
        # for EVERY AI-controlled marshal (Mack, Buxhowden play as cautious).
        lit = make_marshal("Mack", nation="Austria", personality="literal")
        w = make_world(lit, wars=(("France", "Austria"),))
        assert self._ai()._get_effective_personality(lit, w) == "cautious"

    def test_effective_personality_enemy_aggressive_and_cautious_preserved(self):
        aggr = make_marshal("A", nation="Britain", personality="aggressive")
        caut = make_marshal("C", nation="Britain", personality="cautious")
        w = make_world(aggr, caut)
        ai = self._ai()
        assert ai._get_effective_personality(aggr, w) == "aggressive"
        assert ai._get_effective_personality(caut, w) == "cautious"

    def test_effective_personality_player_literal_preserved_unless_autonomous(self):
        # The literal→cautious swap is documented as the consequence of going
        # autonomous; a player literal under command keeps literal.
        lit = make_marshal("Grouchy", nation="France", personality="literal")
        w = make_world(lit)  # player_nation defaults to France
        lit.autonomous = False
        assert self._ai()._get_effective_personality(lit, w) == "literal"
        lit.autonomous = True
        assert self._ai()._get_effective_personality(lit, w) == "cautious"

    def test_aggressive_threshold_below_cautious(self, zero_variance):
        # Aggressive seeks battle at odds a cautious general declines.
        aggr = make_marshal("A", nation="Britain", personality="aggressive")
        caut = make_marshal("C", nation="Britain", personality="cautious")
        w = make_world(aggr, caut)
        ai = self._ai()
        ta = ai._get_mood_adjusted_threshold(aggr, w)
        tc = ai._get_mood_adjusted_threshold(caut, w)
        assert ta < 1.0 < tc
        assert ta < tc

    def test_enemy_literal_threshold_equals_cautious(self, zero_variance):
        # Consequence of the alias: an enemy literal and an enemy cautious pick
        # the SAME attack threshold — they do not diverge (routed MC-V-2).
        lit = make_marshal("Mack", nation="Austria", personality="literal")
        caut = make_marshal("Charles", nation="Austria", personality="cautious")
        w = make_world(lit, caut, wars=(("France", "Austria"),))
        ai = self._ai()
        assert ai._get_mood_adjusted_threshold(lit, w) == pytest.approx(
            ai._get_mood_adjusted_threshold(caut, w))

    def test_aggressive_seeks_battle_where_cautious_and_literal_hold(self):
        # Observed full-turn divergence: co-located at ratio 0.9 (0.7 <= r < 1.3),
        # an aggressive enemy attacks (the French target bleeds); a cautious OR
        # literal enemy declines (the target is untouched).
        def _target_bled(personality):
            world = WorldState()  # legacy world; Britain at war with France
            for m in world.marshals.values():
                if m.nation == "France" and m.name != "Ney":
                    m.strength = 0
                if m.nation == "Britain" and m.name != "Wellington":
                    m.strength = 0
            ney = world.get_marshal("Ney")
            ney.location = "Belgium"
            ney.strength = 50000
            welly = world.get_marshal("Wellington")
            welly.location = "Belgium"  # co-located → P0 engagement decision
            welly.strength = 45000       # ratio 45k/50k = 0.9
            welly.personality = personality
            welly.fortified = False
            random.seed(11)
            EnemyAI(CommandExecutor()).process_nation_turn(
                "Britain", world, {"world": world, "debug_mode": True})
            survivor = world.marshals.get("Ney")
            return survivor is None or survivor.strength < 50000

        assert _target_bled("aggressive") is True
        assert _target_bled("cautious") is False
        assert _target_bled("literal") is False


# ════════════════════════════════════════════════════════════════════════
# HALF (b) — ENEMY-SIDE MC-1 ABILITIES, OBSERVED ON THE AI PATH
# ════════════════════════════════════════════════════════════════════════

class TestEnemySideAbilitiesLive:
    """Confirm the AI EXERCISES the enemy-side MC-1 abilities. The exhaustive
    seam pins live in test_marshal_content_mc1b (§6.2); these cover the
    enemy-controlled / AI-path angle only."""

    def test_enemy_charles_holds_where_others_rout(self, fixed_rng):
        # Player attacks AI-controlled Charles; his post-battle morale lands in
        # (15, 25] and Habsburg Resolve (threshold 15) keeps him on the field,
        # where an identical non-Charles cautious defender routs.
        def _band_battle(ability):
            attacker = make_marshal("Ney", nation="France", strength=40000,
                                   personality="aggressive")
            charles = make_marshal("ArchdukeCharles", nation="Austria",
                                   personality="cautious", strength=35000,
                                   morale=40, ability=ability)
            result = CombatResolver().resolve_battle(attacker, charles)
            assert 15 < result["defender"]["morale"] <= FORCED_RETREAT_THRESHOLD
            return result

        held = _band_battle({"name": "Habsburg Resolve"})
        assert held["defender"]["forced_retreat"] is False
        assert "close ranks" in held["description"]

        routed = _band_battle(None)
        assert routed["defender"]["forced_retreat"] is True

    def test_enemy_kutuzov_pursuit_halved_when_player_routs_him(self, fixed_rng):
        # AI Kutuzov as the routed defender: The Old Fox halves the incoming
        # pursuit (Murat's 5,000 → 2,500), applied AFTER the attacker's bonus.
        murat = make_marshal("Murat", nation="France", personality="aggressive",
                             cavalry=True, strength=45000, location="Belgium",
                             ability={"name": "First Horseman of Europe"})
        kutuzov = make_marshal("Kutuzov", nation="Russia", personality="cautious",
                               strength=25000, morale=30, location="Belgium",
                               ability={"name": "The Old Fox"})
        result = CombatResolver().resolve_battle(murat, kutuzov)
        assert result["defender"]["forced_retreat"] is True
        assert result["pursuit_damage"] == 2500

    def test_enemy_kutuzov_retreat_attrition_halved(self):
        # AI Kutuzov's fighting retreat pays half the march attrition.
        kutuzov = make_marshal("Kutuzov", location="Belgium", strength=38000,
                               nation="Russia", personality="cautious",
                               ability={"name": "The Old Fox"})
        control = make_marshal("Buxhowden", location="Belgium", strength=38000,
                               nation="Russia", personality="cautious")
        world = make_world(kutuzov, control, wars=())
        ex = CommandExecutor()
        fox = ex._movement._calculate_movement_attrition(
            kutuzov, "Paris", world, is_retreat=True)
        base = ex._movement._calculate_movement_attrition(
            control, "Paris", world, is_retreat=True)
        assert fox["march_losses"] == pytest.approx(base["march_losses"] * 0.5,
                                                    abs=1)
        assert fox["march_losses"] < base["march_losses"]

    def test_shorncliffe_floor_on_ai_recruit_dict(self):
        # The AI recruit action carries {"marshal": <name>} into the SAME
        # _execute_recruit as the player — an enemy Moore's recruits arrive at
        # the drilled morale floor 60.
        moore = make_marshal("Moore", location="Netherlands", strength=30000,
                             nation="Britain", personality="cautious",
                             ability={"name": "Shorncliffe System"})
        world = make_world(moore, wars=())
        region = world.get_region("Netherlands")
        region.controller = "Britain"
        region.stability = 100
        world.nation_gold["Britain"] = 5000
        world.manpower_pools.setdefault("Britain", {})["infantry"] = 50000
        result = CommandExecutor()._economy._execute_recruit(
            {"marshal": "Moore"}, {"world": world})
        assert result["success"] is True, result["message"]
        # 30,000 veterans at 100 + 10,000 recruits at 60 → 90
        assert moore.morale == 90
        assert "Shorncliffe System" in result["message"]
