"""MC-1b pin tests (MARSHAL_CONTENT_PASS_SPEC.md §4, memo §6.2 — the T1 set).

Eight abilities, one pin per seam, per the July 10, 2026 blessed gate memo:

- Soult "Drillmaster of Boulogne" — 1-turn drill, never drilling_locked
  (tactical_executor._execute_drill + the _process_tactical_states tick)
- Lannes "Roland of the Army" — +15 arrival score + honest muster arm
- Bernadotte "Eyes on a Crown" — -15 arrival + SUPPORT counter-lever +
  +10pp defiance after insisted objections (defiance.py)
- Murat "First Horseman of Europe" — +5,000 pursuit, cavalry-gated,
  primary-attacker only, exercised at BOTH pursuit copies
- Kutuzov "The Old Fox" — pursuit vs him halved AFTER the attacker's bonus
  (5,000 -> 2,500, ordering pinned) + retreat attrition halved
- Massena "Child of Victory" — +10% defense when outnumbered, under the
  1.75 hard cap, battle-report row
- ArchdukeCharles "Habsburg Resolve" rout threshold 15 — BOTH forced-retreat
  copies + the close-ranks legibility line
- Moore "Shorncliffe System" — recruit morale floor 60 (GR5: same executor
  serves the AI), Training Ground 70 strictly better, intel famed-for rider
"""

import random as _random

import pytest

from backend.ai.parser_eval import build_world
from backend.commands.defiance import calculate_defiance_chance
from backend.commands.executor import CommandExecutor
from backend.commands.objection_v2 import ConcernLevel
from backend.display_names import MUSTER_REASON_DISPLAY
from backend.game_logic.battle_report import snapshot_defender_modifiers
from backend.game_logic.combat import FORCED_RETREAT_THRESHOLD, CombatResolver
from backend.intel_report import generate_intel_report
from backend.models.marshal import Marshal, StrategicOrder
from backend.models.world_state import WorldState


# ════════════════════════════════════════════════════════════════════════
# Helpers (legacy 19-region synthetic worlds — combat mechanics key off the
# ability NAME, so scenario authoring is pinned separately in TestBootPins)
# ════════════════════════════════════════════════════════════════════════

FIXED_DICE = {
    "natural": 7, "modified": 9, "is_critical_success": False,
    "is_critical_failure": False, "multiplier": 1.0,
    "skill_bonus": 2, "flanking_bonus": 0,
}


@pytest.fixture()
def fixed_rng(monkeypatch):
    """Fully deterministic combat: fixed dice, midpoint variance, no fumble,
    and pinned escape/choice rolls (W6-7 capture rolls use random.random —
    0.0 always escapes, so two compared runs never diverge on a fate roll)."""
    monkeypatch.setattr(CombatResolver, "roll_combat_dice",
                        lambda self, marshal, flanking_bonus=0: dict(FIXED_DICE))
    monkeypatch.setattr(_random, "uniform", lambda a, b: (a + b) / 2.0)
    monkeypatch.setattr(_random, "randint", lambda a, b: (a + b) // 2)
    monkeypatch.setattr(_random, "random", lambda: 0.0)
    monkeypatch.setattr(_random, "choice", lambda seq: seq[0])


def make_marshal(name, location="Belgium", strength=30000, nation="France",
                 personality="aggressive", ability=None, cavalry=False,
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
        "_muster_confirmed": True,
    }}
    return executor.execute(command, {"world": world})


# ════════════════════════════════════════════════════════════════════════
# Boot pins: the seven T1 ability blocks survive the scenario pipeline
# ════════════════════════════════════════════════════════════════════════

class TestBootPins:
    EXPECTED = {
        "Soult": "Drillmaster of Boulogne",
        "Lannes": "Roland of the Army",
        "Murat": "First Horseman of Europe",
        "Massena": "Child of Victory",
        "Bernadotte": "Eyes on a Crown",
        "Kutuzov": "The Old Fox",
        "Moore": "Shorncliffe System",
    }

    @pytest.mark.parametrize("name,ability", sorted(EXPECTED.items()))
    def test_t1_marshal_boots_with_ability(self, name, ability):
        w = build_world("1805")
        assert w.get_marshal(name).ability.get("name") == ability

    def test_davout_boots_with_iron_resolve_after_mc1c(self):
        # FLIPPED + RENAMED at MC-1c: the T2 slice landed — Davout boots
        # with Iron Resolve (the tenth and last blessed MC-1 ability).
        w = build_world("1805")
        assert w.get_marshal("Davout").ability.get("name") == "Iron Resolve"

    def test_murat_is_cavalry(self):
        # First Horseman is cavalry-gated; the roster flag is load-bearing.
        w = build_world("1805")
        assert w.get_marshal("Murat").cavalry is True


# ════════════════════════════════════════════════════════════════════════
# Soult — Drillmaster of Boulogne
# ════════════════════════════════════════════════════════════════════════

DRILLMASTER = {"name": "Drillmaster of Boulogne"}


class TestSoultDrillmaster:
    def _drill(self, world, name):
        ex = CommandExecutor()
        return ex._tactical._execute_drill({"marshal": name}, {"world": world})

    def test_drill_completes_at_this_turns_tick(self):
        soult = make_marshal("Soult", ability=DRILLMASTER, personality="literal")
        world = make_world(soult)
        result = self._drill(world, "Soult")
        assert result["success"] is True
        assert soult.drill_complete_turn == world.current_turn
        assert "remains at your orders" in result["message"]

        world._process_tactical_states()
        assert soult.shock_bonus == 2          # payoff unchanged
        assert soult.drilling is False
        assert soult.drilling_locked is False  # NEVER locked

    def test_never_enters_locked_state(self):
        soult = make_marshal("Soult", ability=DRILLMASTER, personality="literal")
        world = make_world(soult)
        self._drill(world, "Soult")
        assert soult.drilling_locked is False
        events = world._process_tactical_states()
        assert soult.drilling_locked is False
        assert not [e for e in events
                    if e.get("type") == "drill_locked" and e.get("marshal") == "Soult"]
        assert [e for e in events
                if e.get("type") == "drill_complete" and e.get("marshal") == "Soult"]

    def test_keeps_one_enemy_phase_of_exposure(self):
        # Between the order and the end-of-turn tick, drilling=True costs
        # the standard -25% defense (the blessed exposure window).
        soult = make_marshal("Soult", ability=DRILLMASTER, personality="literal")
        world = make_world(soult)
        self._drill(world, "Soult")
        exposed = soult.get_defense_modifier(is_outnumbered=False)
        soult.drilling = False
        safe = soult.get_defense_modifier(is_outnumbered=False)
        assert exposed == pytest.approx(safe * 0.75)

    def test_baseline_marshal_still_two_turn_locked(self):
        davout = make_marshal("Davout", personality="cautious")
        world = make_world(davout)
        result = self._drill(world, "Davout")
        assert result["success"] is True
        assert davout.drill_complete_turn == world.current_turn + 1

        world._process_tactical_states()
        assert davout.drilling_locked is True   # locked, unorderable
        assert davout.shock_bonus == 0

        world.current_turn += 1
        world._process_tactical_states()
        assert davout.shock_bonus == 2
        assert davout.drilling_locked is False


# ════════════════════════════════════════════════════════════════════════
# Lannes / Bernadotte — the arrival mirror (+15 / -15) + honest muster arms
# ════════════════════════════════════════════════════════════════════════

ROLAND = {"name": "Roland of the Army"}
EYES_ON_A_CROWN = {"name": "Eyes on a Crown"}


class TestArrivalMirror:
    def _score(self, marshal, primary, world):
        return CommandExecutor()._calculate_arrival_score(marshal, primary, world)

    def test_roland_adds_15(self, fixed_rng):
        primary = make_marshal("Ney", location="Waterloo")
        lannes = make_marshal("Lannes", location="Belgium", ability=ROLAND)
        world = make_world(primary, lannes)
        with_ability = self._score(lannes, primary, world)
        lannes.ability["name"] = "None"
        without = self._score(lannes, primary, world)
        assert with_ability - without == 15

    def test_eyes_on_a_crown_subtracts_15(self, fixed_rng):
        primary = make_marshal("Ney", location="Waterloo")
        bernadotte = make_marshal("Bernadotte", location="Belgium",
                                  personality="cautious", ability=EYES_ON_A_CROWN)
        world = make_world(primary, bernadotte)
        with_ability = self._score(bernadotte, primary, world)
        bernadotte.ability["name"] = "None"
        without = self._score(bernadotte, primary, world)
        assert with_ability - without == -15

    def test_support_order_counter_lever_adds_10(self, fixed_rng):
        # The written word mostly cancels the -15 (memo: bless jointly).
        primary = make_marshal("Ney", location="Waterloo")
        bernadotte = make_marshal("Bernadotte", location="Belgium",
                                  personality="cautious", ability=EYES_ON_A_CROWN)
        world = make_world(primary, bernadotte)
        without_order = self._score(bernadotte, primary, world)
        bernadotte.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Ney", target_type="marshal",
            started_turn=1, original_command="Support Ney")
        with_order = self._score(bernadotte, primary, world)
        assert with_order - without_order == 10

    def test_muster_reason_roland_marches(self):
        primary = make_marshal("Ney", location="Waterloo")
        lannes = make_marshal("Lannes", location="Belgium", ability=ROLAND)
        world = make_world(primary, lannes)
        will_join, code = CommandExecutor()._combat._muster_reason(
            lannes, primary, "Waterloo", "France", world)
        assert will_join is True
        assert code == "roland_marches"

    def test_muster_reason_eyes_on_a_crown_hesitates(self):
        # W6-4 honesty: without the written word the preview says he
        # will NOT march — his base score usually loses to the threshold.
        primary = make_marshal("Ney", location="Waterloo")
        bernadotte = make_marshal("Bernadotte", location="Belgium",
                                  personality="cautious", ability=EYES_ON_A_CROWN)
        world = make_world(primary, bernadotte)
        will_join, code = CommandExecutor()._combat._muster_reason(
            bernadotte, primary, "Waterloo", "France", world)
        assert will_join is False
        assert code == "eyes_on_a_crown"

    def test_muster_reason_support_order_wins_over_hesitation(self):
        primary = make_marshal("Ney", location="Waterloo")
        bernadotte = make_marshal("Bernadotte", location="Belgium",
                                  personality="cautious", ability=EYES_ON_A_CROWN)
        bernadotte.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Ney", target_type="marshal",
            started_turn=1, original_command="Support Ney")
        world = make_world(primary, bernadotte)
        will_join, code = CommandExecutor()._combat._muster_reason(
            bernadotte, primary, "Waterloo", "France", world)
        assert will_join is True
        assert code == "has_support_order"

    def test_display_map_carries_both_codes(self):
        assert "roland_marches" in MUSTER_REASON_DISPLAY
        assert "eyes_on_a_crown" in MUSTER_REASON_DISPLAY

    def test_muster_preview_hints_the_written_word(self):
        primary = make_marshal("Ney", location="Waterloo")
        enemy = make_marshal("Wellington", location="Waterloo",
                             nation="Britain", personality="cautious")
        bernadotte = make_marshal("Bernadotte", location="Belgium",
                                  personality="cautious", ability=EYES_ON_A_CROWN)
        world = make_world(primary, enemy, bernadotte)
        preview = CommandExecutor()._combat._build_muster_preview(
            primary, enemy, world, {"world": world})
        row = next(r for r in preview["rows"] if r["marshal"] == "Bernadotte")
        assert row["will_join"] is False
        assert row["reason"] == "eyes_on_a_crown"
        assert "support" in row.get("standing_order_hint", "")


# ════════════════════════════════════════════════════════════════════════
# Bernadotte — Eyes on a Crown (defiance arm)
# ════════════════════════════════════════════════════════════════════════

class TestBernadotteDefiance:
    def _world_with(self, marshal):
        world = make_world(marshal)
        world.authority_tracker.authority = 60  # neutral tier (no modifier)
        world.current_turn = 5
        return world

    def test_plus_10pp_at_moderate(self, fixed_rng):
        bernadotte = make_marshal("Bernadotte", personality="cautious",
                                  ability=EYES_ON_A_CROWN)
        world = self._world_with(bernadotte)
        with_ability = calculate_defiance_chance(
            bernadotte, ConcernLevel.MODERATE, world)
        bernadotte.ability["name"] = "None"
        without = calculate_defiance_chance(
            bernadotte, ConcernLevel.MODERATE, world)
        assert without == pytest.approx(0.05)
        assert with_ability == pytest.approx(0.15)

    def test_extreme_still_hard_capped_at_40(self, fixed_rng):
        bernadotte = make_marshal("Bernadotte", personality="cautious",
                                  ability=EYES_ON_A_CROWN)
        world = self._world_with(bernadotte)
        chance = calculate_defiance_chance(
            bernadotte, ConcernLevel.EXTREME, world)
        assert chance == pytest.approx(0.40)  # 0.35 + 0.10 -> capped


# ════════════════════════════════════════════════════════════════════════
# Murat — First Horseman of Europe (BOTH pursuit copies)
# ════════════════════════════════════════════════════════════════════════

FIRST_HORSEMAN = {"name": "First Horseman of Europe"}
OLD_FOX = {"name": "The Old Fox"}


def _murat(location="Belgium", cavalry=True):
    return make_marshal("Murat", location=location, strength=45000,
                        cavalry=cavalry, ability=dict(FIRST_HORSEMAN))


def _routing_enemy(name="Mack", location="Belgium", nation="Britain",
                   ability=None):
    # Strong enough to stay above the 1,000-survivor floor with room for
    # the full 5,000 pursuit; morale low enough that losing routs him.
    return make_marshal(name, location=location, strength=25000,
                        nation=nation, personality="cautious",
                        morale=30, ability=ability)


class TestMuratFirstHorseman:
    def test_solo_copy_pursuit_5000(self, fixed_rng):
        murat = _murat()
        enemy = _routing_enemy()
        result = CombatResolver().resolve_battle(murat, enemy)
        assert result["defender"]["forced_retreat"] is True
        assert result["pursuit_damage"] == 5000
        assert "First Horseman of Europe" in (result.get("pursuit_message") or "")
        assert "First Horseman of Europe" in result["description"]

    def test_cavalry_gate(self, fixed_rng):
        murat = _murat(cavalry=False)
        enemy = _routing_enemy()
        result = CombatResolver().resolve_battle(murat, enemy)
        assert result["defender"]["forced_retreat"] is True
        assert result["pursuit_damage"] == 0

    def test_no_pursuit_without_rout(self, fixed_rng):
        murat = _murat()
        enemy = _routing_enemy()
        enemy.morale = 100  # survives with morale above threshold
        result = CombatResolver().resolve_battle(murat, enemy)
        if not result["defender"]["forced_retreat"]:
            assert result["pursuit_damage"] == 0

    def test_coordinated_copy_pursuit_as_primary(self, fixed_rng):
        # Murat leads with Ney on the same field -> coordinated path.
        murat = _murat()
        ney = make_marshal("Ney", location="Belgium", strength=30000)
        enemy = _routing_enemy()
        world = make_world(murat, ney, enemy)
        pre = enemy.strength
        result = execute_attack(world, "Murat", "Mack")
        assert "First Horseman of Europe" in result.get("message", "")
        assert enemy.strength < pre
        assert enemy.strength >= 1000  # survivor floor intact

    def test_coordinated_reinforcer_murat_earns_nothing(self, fixed_rng):
        # The killing blow must be HIS — Ney primary, Murat on the field.
        murat = _murat()
        ney = make_marshal("Ney", location="Belgium", strength=30000)
        enemy = _routing_enemy()
        world = make_world(murat, ney, enemy)
        result = execute_attack(world, "Ney", "Mack")
        assert "First Horseman of Europe" not in result.get("message", "")


# ════════════════════════════════════════════════════════════════════════
# Kutuzov — The Old Fox (both pursuit copies + retreat attrition)
# ════════════════════════════════════════════════════════════════════════

class TestKutuzovOldFox:
    def test_solo_copy_halves_after_attacker_bonus(self, fixed_rng):
        # Ordering pin: Murat's 5,000 -> 2,500 (halve AFTER the bonus).
        murat = _murat()
        kutuzov = _routing_enemy("Kutuzov", nation="Britain",
                                 ability=dict(OLD_FOX))
        result = CombatResolver().resolve_battle(murat, kutuzov)
        assert result["defender"]["forced_retreat"] is True
        assert result["pursuit_damage"] == 2500
        assert "Old Fox halves the harvest" in result["pursuit_message"]

    def test_coordinated_copy_halves(self, fixed_rng):
        murat = _murat()
        ney = make_marshal("Ney", location="Belgium", strength=30000)
        kutuzov = _routing_enemy("Kutuzov", nation="Britain",
                                 ability=dict(OLD_FOX))
        world = make_world(murat, ney, kutuzov)
        result = execute_attack(world, "Murat", "Kutuzov")
        assert "Old Fox halves the harvest" in result.get("message", "")

    def test_retreat_attrition_halved(self):
        kutuzov = make_marshal("Kutuzov", location="Belgium", strength=38000,
                               nation="Russia", personality="cautious",
                               ability=dict(OLD_FOX))
        control = make_marshal("Buxhowden", location="Belgium", strength=38000,
                               nation="Russia", personality="cautious")
        world = make_world(kutuzov, control, wars=())
        ex = CommandExecutor()
        fox = ex._movement._calculate_movement_attrition(
            kutuzov, "Paris", world, is_retreat=True)
        base = ex._movement._calculate_movement_attrition(
            control, "Paris", world, is_retreat=True)
        assert fox["march_losses"] == pytest.approx(base["march_losses"] * 0.5, abs=1)
        assert fox["march_losses"] < base["march_losses"]

    def test_normal_march_pays_full_price(self):
        kutuzov = make_marshal("Kutuzov", location="Belgium", strength=38000,
                               nation="Russia", personality="cautious",
                               ability=dict(OLD_FOX))
        control = make_marshal("Buxhowden", location="Belgium", strength=38000,
                               nation="Russia", personality="cautious")
        world = make_world(kutuzov, control, wars=())
        ex = CommandExecutor()
        fox = ex._movement._calculate_movement_attrition(
            kutuzov, "Paris", world, is_retreat=False)
        base = ex._movement._calculate_movement_attrition(
            control, "Paris", world, is_retreat=False)
        assert fox["march_losses"] == base["march_losses"]


# ════════════════════════════════════════════════════════════════════════
# Massena — Child of Victory
# ════════════════════════════════════════════════════════════════════════

CHILD_OF_VICTORY = {"name": "Child of Victory"}


class TestMassenaChildOfVictory:
    def test_plus_10_percent_when_outnumbered(self):
        massena = make_marshal("Massena", ability=dict(CHILD_OF_VICTORY))
        with_ability = massena.get_defense_modifier(is_outnumbered=True)
        massena.ability["name"] = "None"
        without = massena.get_defense_modifier(is_outnumbered=True)
        assert with_ability == pytest.approx(without * 1.10)

    def test_no_bonus_when_not_outnumbered(self):
        massena = make_marshal("Massena", ability=dict(CHILD_OF_VICTORY))
        with_ability = massena.get_defense_modifier(is_outnumbered=False)
        massena.ability["name"] = "None"
        without = massena.get_defense_modifier(is_outnumbered=False)
        assert with_ability == pytest.approx(without)

    def test_stack_stays_under_175_hard_cap(self):
        from backend.models.marshal import Stance
        massena = make_marshal("Massena", ability=dict(CHILD_OF_VICTORY))
        massena.stance = Stance.DEFENSIVE
        massena.defense_bonus = 0.30
        massena.square_formation = True
        massena.total_coordination_defense_bonus = 0.10
        modifier = massena.get_defense_modifier(is_outnumbered=True)
        assert modifier == pytest.approx(1.75)

    def test_battle_report_row_when_outnumbered(self):
        massena = make_marshal("Massena", strength=42000,
                               ability=dict(CHILD_OF_VICTORY))
        attacker = make_marshal("Charles", strength=54000, nation="Austria",
                                personality="cautious")
        mods = snapshot_defender_modifiers(massena, attacker, "open", 0.0)
        labels = [m["label"] for m in mods]
        assert "Child of Victory (outnumbered)" in labels

    def test_no_battle_report_row_when_stronger(self):
        massena = make_marshal("Massena", strength=60000,
                               ability=dict(CHILD_OF_VICTORY))
        attacker = make_marshal("Charles", strength=54000, nation="Austria",
                                personality="cautious")
        mods = snapshot_defender_modifiers(massena, attacker, "open", 0.0)
        labels = [m["label"] for m in mods]
        assert "Child of Victory (outnumbered)" not in labels


# ════════════════════════════════════════════════════════════════════════
# Archduke Charles — Habsburg Resolve rout threshold (both copies)
# ════════════════════════════════════════════════════════════════════════

HABSBURG = {"name": "Habsburg Resolve"}


class TestCharlesRoutThreshold:
    def test_helper_returns_15_for_habsburg_resolve(self):
        charles = make_marshal("Charles", nation="Austria",
                               personality="cautious", ability=dict(HABSBURG))
        assert charles.get_rout_threshold(FORCED_RETREAT_THRESHOLD) == 15

    def test_helper_passes_base_through_for_others(self):
        ney = make_marshal("Ney")
        assert ney.get_rout_threshold(FORCED_RETREAT_THRESHOLD) == FORCED_RETREAT_THRESHOLD

    def _band_battle(self, ability):
        """Deterministic solo battle whose loser lands in (15, 25] morale."""
        attacker = make_marshal("Ney", strength=40000)
        charles = make_marshal("Charles", nation="Britain",
                               personality="cautious", strength=35000,
                               morale=40, ability=ability)
        result = CombatResolver().resolve_battle(attacker, charles)
        post_morale = result["defender"]["morale"]
        assert 15 < post_morale <= FORCED_RETREAT_THRESHOLD, (
            f"tune the fixture: post-battle morale {post_morale} must land in "
            f"(15, {FORCED_RETREAT_THRESHOLD}] for the isolation to be meaningful")
        return result

    def test_solo_copy_charles_holds_where_others_rout(self, fixed_rng):
        held = self._band_battle(dict(HABSBURG))
        assert held["defender"]["forced_retreat"] is False
        assert "close ranks" in held["description"]

        routed = self._band_battle(None)
        assert routed["defender"]["forced_retreat"] is True

    def test_coordinated_copy_charles_holds(self, fixed_rng):
        def run(ability):
            ney = make_marshal("Ney", strength=40000)
            davout = make_marshal("Davout", strength=30000,
                                  personality="cautious")
            charles = make_marshal("Charles", location="Belgium",
                                   nation="Britain", personality="cautious",
                                   strength=35000, morale=40, ability=ability)
            world = make_world(ney, davout, charles)
            result = execute_attack(world, "Ney", "Charles")
            return charles, result

        charles_held, result_held = run(dict(HABSBURG))
        assert 15 < charles_held.morale <= FORCED_RETREAT_THRESHOLD, (
            f"tune the fixture: coordinated post-battle morale "
            f"{charles_held.morale} must land in (15, {FORCED_RETREAT_THRESHOLD}]")
        assert charles_held.retreating is False
        assert charles_held.broken is False
        assert "close ranks" in result_held.get("message", "")

        charles_routed, _ = run(None)
        assert charles_routed.retreating or charles_routed.broken


# ════════════════════════════════════════════════════════════════════════
# Moore — Shorncliffe System (GR5: same recruit seam serves the AI)
# ════════════════════════════════════════════════════════════════════════

SHORNCLIFFE = {"name": "Shorncliffe System"}


class TestMooreShorncliffe:
    def _recruit(self, world, name):
        ex = CommandExecutor()
        return ex._economy._execute_recruit({"marshal": name}, {"world": world})

    def _moore_world(self, ability=dict(SHORNCLIFFE)):
        # The legacy test map has no London — garrison Moore on a legacy
        # region and hand it to Britain (recruit requires controller match).
        moore = make_marshal("Moore", location="Netherlands", strength=30000,
                             nation="Britain", personality="cautious",
                             ability=dict(ability) if ability else None)
        world = make_world(moore, wars=())
        region = world.get_region("Netherlands")
        region.controller = "Britain"
        region.stability = 100
        world.nation_gold["Britain"] = 5000
        world.manpower_pools.setdefault("Britain", {})["infantry"] = 50000
        return moore, world

    def test_recruits_arrive_at_morale_floor_60(self):
        moore, world = self._moore_world()
        result = self._recruit(world, "Moore")
        assert result["success"] is True, result["message"]
        # 30,000 veterans at 100 + 10,000 recruits at 60 -> 90
        assert moore.morale == 90
        assert "Shorncliffe System" in result["message"]

    def test_baseline_recruits_arrive_at_40(self):
        moore, world = self._moore_world(ability=None)
        result = self._recruit(world, "Moore")
        assert result["success"] is True, result["message"]
        # 30,000 veterans at 100 + 10,000 recruits at 40 -> 85
        assert moore.morale == 85
        assert "Shorncliffe" not in result["message"]

    def test_training_ground_70_stays_strictly_better(self, monkeypatch):
        moore, world = self._moore_world()
        region = world.get_region("Netherlands")
        monkeypatch.setattr(region, "has_building",
                            lambda b: b == "training_ground")
        result = self._recruit(world, "Moore")
        assert result["success"] is True, result["message"]
        # 30,000 at 100 + 10,000 at 70 -> 92 (int) — floor never fires
        assert moore.morale == 92
        assert "Shorncliffe" not in result["message"]

    def test_ai_nation_pays_its_own_treasury(self):
        # GR5: acting nation derives from the marshal — Britain's gold and
        # pool move, not the player's.
        moore, world = self._moore_world()
        france_gold = world.nation_gold.get("France", 0)
        result = self._recruit(world, "Moore")
        assert result["success"] is True, result["message"]
        assert world.nation_gold["Britain"] < 5000
        assert world.manpower_pools["Britain"]["infantry"] == 40000
        assert world.nation_gold.get("France", 0) == france_gold


# ════════════════════════════════════════════════════════════════════════
# Intel visibility rider — famed abilities named at FULL visibility
# ════════════════════════════════════════════════════════════════════════

class TestIntelFamedAbility:
    def test_full_visibility_names_the_famed_ability(self):
        w = build_world("1805")
        # March Massena onto Charles's ground -> FULL visibility there.
        massena = w.get_marshal("Massena")
        charles = w.get_marshal("ArchdukeCharles")
        massena.location = charles.location
        w.calculate_visibility()
        report = generate_intel_report(w)
        entries = [e for r in report["confirmed"] for e in r.get("enemies", [])
                   if e["name"] == "ArchdukeCharles"]
        assert entries and entries[0]["ability"] == "Habsburg Resolve"
        assert "famed for 'Habsburg Resolve'" in report["report_text"]

    def test_no_ability_no_famed_tag(self):
        w = build_world("1805")
        ney = w.get_marshal("Ney")
        mack = w.get_marshal("Mack")
        ney.location = mack.location
        w.calculate_visibility()
        report = generate_intel_report(w)
        entries = [e for r in report["confirmed"] for e in r.get("enemies", [])
                   if e["name"] == "Mack"]
        assert entries and entries[0]["ability"] == ""


# ════════════════════════════════════════════════════════════════════════
# Review-pass fixes (post-implementation adversarial review, July 10, 2026)
# ════════════════════════════════════════════════════════════════════════

class TestNonPrimaryRoutThreshold:
    """The THIRD rout-decision copy: the [S62] coordinated non-primary sweep
    must consult get_rout_threshold (Habsburg Resolve holds a non-primary
    Charles to 15 where the old hardcoded 25 routed him)."""

    def _run(self, ability):
        ney = make_marshal("Ney", strength=40000)
        mack = make_marshal("Mack", location="Belgium", nation="Britain",
                            personality="cautious", strength=35000, morale=60)
        charles = make_marshal("Charles", location="Belgium",
                               nation="Britain", personality="cautious",
                               strength=30000, morale=36, ability=ability)
        world = make_world(ney, mack, charles)
        result = execute_attack(world, "Ney", "Mack")
        return charles, result

    def test_non_primary_charles_holds_in_the_band(self, fixed_rng):
        charles, result = self._run(dict(HABSBURG))
        assert 15 < charles.morale <= FORCED_RETREAT_THRESHOLD, (
            f"tune the fixture: non-primary post-battle morale "
            f"{charles.morale} must land in (15, {FORCED_RETREAT_THRESHOLD}]")
        assert charles.retreating is False
        assert charles.broken is False
        assert "close ranks" in result.get("message", "")

    def test_non_primary_control_routs(self, fixed_rng):
        charles, _ = self._run(None)
        assert charles.retreating or charles.broken


class TestPursuitHonestyAndFloor:
    """Shown = applied near the 1,000-survivor floor: the message carries the
    ACTUAL clipped figure, and the coordinated copy never resurrects a
    sub-floor defender (the > 1000 guard, revert-proofed)."""

    def test_solo_message_carries_the_clipped_actual(self, fixed_rng):
        murat = _murat()
        enemy = make_marshal("Mack", location="Belgium", nation="Britain",
                             personality="cautious", strength=6000, morale=26)
        result = CombatResolver().resolve_battle(murat, enemy)
        assert result["defender"]["forced_retreat"] is True
        actual = result["pursuit_damage"]
        assert 0 < actual < 5000, (
            f"tune the fixture: pursuit {actual} must be floor-clipped")
        assert enemy.strength == 1000
        assert f"+{actual:,} pursuit casualties" in result["pursuit_message"]
        assert "5,000" not in result["pursuit_message"]

    def test_coordinated_no_resurrection_below_floor(self, fixed_rng):
        def run(with_ability):
            murat = _murat()
            if not with_ability:
                murat.ability["name"] = "None"
            ney = make_marshal("Ney", location="Belgium", strength=30000)
            enemy = make_marshal("Weak", location="Belgium", nation="Britain",
                                 personality="cautious", strength=2900,
                                 morale=26)
            world = make_world(murat, ney, enemy)
            result = execute_attack(world, "Murat", "Weak")
            return enemy, result

        enemy_ability, result_ability = run(True)
        enemy_control, _ = run(False)
        assert 0 < enemy_control.strength <= 1000, (
            f"tune the fixture: post-battle strength {enemy_control.strength} "
            f"must land in (0, 1000] to exercise the floor guard")
        # Pursuit must neither fire nor RAISE him back up to the floor.
        assert enemy_ability.strength == enemy_control.strength
        assert "First Horseman of Europe" not in result_ability.get("message", "")


class TestCoordinatedNumericMirror:
    """The coordinated copy's constants are pinned numerically (message
    substrings alone survive mirror drift — review mutation-tested)."""

    def _coordinated(self, murat_ability=True, murat_cavalry=True,
                     defender_ability=None):
        murat = _murat(cavalry=murat_cavalry)
        if not murat_ability:
            murat.ability["name"] = "None"
        ney = make_marshal("Ney", location="Belgium", strength=30000)
        enemy = _routing_enemy(ability=defender_ability)
        world = make_world(murat, ney, enemy)
        result = execute_attack(world, "Murat", "Mack")
        return enemy, result

    def test_coordinated_pursuit_is_exactly_5000(self, fixed_rng):
        enemy_with, result = self._coordinated(murat_ability=True)
        enemy_without, _ = self._coordinated(murat_ability=False)
        assert enemy_without.strength - enemy_with.strength == 5000
        assert "+5,000 pursuit casualties" in result.get("message", "")

    def test_coordinated_old_fox_is_exactly_2500(self, fixed_rng):
        enemy_fox, result = self._coordinated(defender_ability=dict(OLD_FOX))
        enemy_nofox, _ = self._coordinated(defender_ability=None)
        # The Old Fox keeps exactly 2,500 more men than the unscreened rout.
        assert enemy_fox.strength - enemy_nofox.strength == 2500
        assert "+2,500 pursuit casualties" in result.get("message", "")

    def test_coordinated_cavalry_gate(self, fixed_rng):
        _, result = self._coordinated(murat_cavalry=False)
        assert "First Horseman of Europe" not in result.get("message", "")

    def test_coordinated_report_numbers_include_pursuit(self, fixed_rng):
        # Review fix: remaining/casualties/casualty_summary must agree with
        # the prose (they were frozen pre-pursuit — the two-copy mirror gap).
        enemy, result = self._coordinated(murat_ability=True)
        report = result.get("battle_report") or {}
        cs = report.get("casualty_summary") or {}
        assert cs.get("defender_remaining") == enemy.strength
        assert (cs.get("defender_original") - cs.get("defender_casualties")
                == enemy.strength)


class TestEyesOnACrownTrustSeam:
    """His ability-driven no-show is by-design character (like the literal
    no-march) — no silent -3 trust drain; a no-show UNDER a written SUPPORT
    order is a genuine failure and stays docked."""

    def _battle_with_bernadotte(self, support_order=False, relationship=0):
        ney = make_marshal("Ney", location="Waterloo", strength=45000)
        enemy = make_marshal("Wellington", location="Waterloo",
                             nation="Britain", personality="cautious",
                             strength=15000, morale=60)
        bernadotte = make_marshal("Bernadotte", location="Belgium",
                                  personality="cautious",
                                  ability=dict(EYES_ON_A_CROWN))
        if relationship:
            bernadotte.set_relationship("Ney", relationship)
        if support_order:
            bernadotte.strategic_order = StrategicOrder(
                command_type="SUPPORT", target="Ney", target_type="marshal",
                started_turn=1, original_command="Support Ney")
        world = make_world(ney, enemy, bernadotte)
        result = execute_attack(world, "Ney", "Wellington")
        return bernadotte, result

    def test_no_show_without_order_costs_no_trust(self, fixed_rng):
        bernadotte, result = self._battle_with_bernadotte()
        rows = result.get("reinforcement_results", {}).get("attacker", [])
        row = next(r for r in rows if r["marshal"] == "Bernadotte")
        assert row["arrived"] is False
        assert row["reason"] == "eyes_on_a_crown"
        assert bernadotte.trust.value == 70  # exempt, like the literal no-march

    def test_failure_copy_names_ambition_not_the_roads(self, fixed_rng):
        _, result = self._battle_with_bernadotte()
        messages = " ".join(result.get("reinforcement_messages", []))
        assert "weighed its own ambitions" in messages
        assert "could not reach the battlefield" not in messages

    def test_stood_up_support_order_still_docks_trust(self, fixed_rng):
        # rel -1 (-10) + SUPPORT (+10): score 55 vs threshold 60 -> fails
        # as a genuine "low_score" and the Session-61a dock applies.
        bernadotte, result = self._battle_with_bernadotte(
            support_order=True, relationship=-1)
        rows = result.get("reinforcement_results", {}).get("attacker", [])
        row = next(r for r in rows if r["marshal"] == "Bernadotte")
        assert row["arrived"] is False
        assert row["reason"] == "low_score"
        assert bernadotte.trust.value == 67

    def test_muster_arm_softens_at_positive_relationship(self):
        # Review fix: at rel +1 the arrival roll is genuinely winnable, so
        # the hard "WILL NOT" gives way to the hedged generic arm.
        primary = make_marshal("Ney", location="Waterloo")
        bernadotte = make_marshal("Bernadotte", location="Belgium",
                                  personality="cautious",
                                  ability=dict(EYES_ON_A_CROWN))
        bernadotte.set_relationship("Ney", 1)
        world = make_world(primary, bernadotte)
        will_join, code = CommandExecutor()._combat._muster_reason(
            bernadotte, primary, "Waterloo", "France", world)
        assert will_join is True
        assert code == "answers_the_guns"


class TestLannesGR5Symmetry:
    """Memo §6.2: the arrival mirror serves BOTH sides through the same seam
    — an enemy-initiated battle picks up Lannes on the defender side."""

    def _enemy_attacks(self, lannes_ability):
        ney = make_marshal("Ney", location="Waterloo", strength=30000)
        wellington = make_marshal("Wellington", location="Waterloo",
                                  nation="Britain", personality="aggressive",
                                  strength=35000)
        lannes = make_marshal("Lannes", location="Belgium",
                              ability=lannes_ability)
        world = make_world(ney, wellington, lannes)
        result = execute_attack(world, "Wellington", "Ney")
        rows = result.get("reinforcement_results", {}).get("defender", [])
        return next(r for r in rows if r["marshal"] == "Lannes")

    def test_defender_side_lannes_gets_plus_15(self, fixed_rng):
        with_ability = self._enemy_attacks(dict(ROLAND))
        without = self._enemy_attacks(None)
        assert with_ability["score"] - without["score"] == 15
        assert with_ability["arrived"] is True


class TestDrillmasterTooltipFlag:
    """The map tooltip's derived flag (Q3 pattern): a completing-tonight
    drill must not render 'Will lock next turn'."""

    def test_flag_set_for_drillmaster_order_turn(self):
        soult = make_marshal("Soult", location="Paris", nation="France",
                             personality="literal", ability=DRILLMASTER)
        world = make_world(soult, wars=())
        CommandExecutor()._tactical._execute_drill(
            {"marshal": "Soult"}, {"world": world})
        summary = world.get_game_state_summary()
        data = next(m for m in summary["map_data"]["Paris"]["marshals"]
                    if m["name"] == "Soult")
        assert data["tactical_state"]["drill_completes_this_turn"] is True

    def test_flag_clear_for_baseline_drill(self):
        davout = make_marshal("Davout", location="Paris", nation="France",
                              personality="cautious")
        world = make_world(davout, wars=())
        CommandExecutor()._tactical._execute_drill(
            {"marshal": "Davout"}, {"world": world})
        summary = world.get_game_state_summary()
        data = next(m for m in summary["map_data"]["Paris"]["marshals"]
                    if m["name"] == "Davout")
        assert data["tactical_state"]["drill_completes_this_turn"] is False
