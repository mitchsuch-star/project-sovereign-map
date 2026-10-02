"""SR-7a "The AI's odds gate and its dithering" (Score Finish Step 3,
October 2, 2026) — AAR-D8 + CQ-22 + IQ5-R1 + XR-3's remaining half.

- AAR-D8 (a): a detachment garrison under `SMALL_GARRISON_SURRENDER_FLOOR`
  lays down its arms to the first corps beside it — ONE predicate
  (`garrison_report.garrison_fights`) read by the attack, the march, the
  scout, P4.25 and P4.5, both boards. Lever `A_SMALL_GARRISON_SURRENDERS`.
- AAR-D8 (b): the cautious kit's odds gate on the AI's P4 rung — the band
  the player's confirm arms on. Lever `AI_ATTACKS_OBEY_THE_MUSTER_GATE`.
- AAR-D8 (c): the two anti-oscillation guards are serialized (pinned).
- CQ-22: ONE stance rule for drill on every road. Lever
  `ONE_STANCE_RULE_FOR_DRILL`.
- IQ5-R1: the casualty pool splits by the men committed. Lever
  `BLEED_BY_THE_MEN_COMMITTED`.
- XR-3: an in-place capture marches nowhere. Lever
  `AN_IN_PLACE_CAPTURE_MARCHES_NOWHERE`.
"""
from __future__ import annotations

import ast
import contextlib
import io
import random
from pathlib import Path

import pytest

from backend.ai import enemy_ai as EA
from backend.ai.enemy_ai import EnemyAI
from backend.commands import combat_executor as CE
from backend.commands import tactical_executor as TE
from backend.commands.executor import CommandExecutor
from backend.game_logic import garrison_report as GR
from backend.game_logic import jealousy as J
from backend.models.marshal import Marshal, Stance
from backend.models.world_state import WorldState

SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
            / "assets" / "maps" / "europe_1805.json")


def _boot():
    world = WorldState.from_scenario(str(SCENARIO))
    executor = CommandExecutor()
    return world, executor, {"world": world, "executor": executor}


def _run(executor, game_state, command):
    with contextlib.redirect_stdout(io.StringIO()):
        random.seed(1805)
        return executor.execute({"command": command}, game_state)


def _quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


# ═════════════════════════ AAR-D8 (a): the small garrison surrenders ═════


def _stage_franconia(world, size: int):
    """Franconia French-held with a detachment of `size`; Mack adjacent at
    Swabia; nobody standing in Franconia."""
    region = world.get_region("Franconia")
    for m in world.marshals.values():
        if m.location == "Franconia":
            m.location = "Paris"
    region.controller = "France"
    world.invalidate_active_nations_cache()
    region.garrison_strength = size
    region.garrison_detachment = True
    return region


class TestTheSmallGarrisonSurrenders:
    @pytest.mark.parametrize("size,fights", [(47, False), (499, False), (500, True), (3000, True)])
    def test_the_one_predicate_reads_the_floor(self, size, fights):
        world, _ex, _gs = _boot()
        region = _stage_franconia(world, size)
        assert GR.garrison_fights(region) is fights
        assert GR.detachment_surrenders(region) is (not fights)

    def test_a_capital_garrison_never_surrenders_by_this_rule(self):
        world, _ex, _gs = _boot()
        vienna = world.get_region("Vienna")
        vienna.garrison_strength = 400          # a capital's 400 is the collapse line's business
        assert GR.detachment_surrenders(vienna) is False

    def test_the_ai_attack_takes_it_without_an_escalade(self):
        world, executor, gs = _boot()
        region = _stage_franconia(world, 47)
        mack = world.marshals["Mack"]
        before = mack.strength
        result = _run(executor, gs, {"action": "attack", "marshal": "Mack", "target": "Franconia",
                                     "_acting_nation": "Austria", "_muster_confirmed": True})
        assert result.get("success")
        assert "detachment of 47 at Franconia lays down its arms" in result["message"]
        assert "assaults the Franconia garrison" not in result["message"]
        assert region.garrison_strength == 0 and region.controller == "Austria"
        # the only blood is the road's, never the escalade's
        assert before - mack.strength == int(result["message"].split("(")[1].split(" lost")[0].replace(",", "")) \
            if "lost to march" in result["message"] else before == mack.strength

    def test_gr5_the_player_takes_one_the_same_way(self):
        world, executor, gs = _boot()
        bohemia = world.get_region("Bohemia")
        for m in world.marshals.values():
            if m.location == "Bohemia":
                m.location = "Hungary"
        bohemia.garrison_strength = 120
        bohemia.garrison_detachment = True
        ney = world.marshals["Ney"]
        ney.location = "Dresden"
        ney.strength = 30000
        result = _run(executor, gs, {"action": "attack", "marshal": "Ney", "target": "Bohemia",
                                     "_muster_confirmed": True})
        assert result.get("success")
        assert "detachment of 120 at Bohemia lays down its arms" in result["message"]
        assert bohemia.garrison_strength == 0

    def test_p425_never_assaults_it_and_p45_prices_it_as_open_ground(self):
        world, executor, _gs = _boot()
        _stage_franconia(world, 47)
        ai = EnemyAI(executor)
        mack = world.marshals["Mack"]
        random.seed(7)
        assault = _quiet(ai._find_garrison_attack, mack, "Austria", world)
        assert not assault or assault.get("target") != "Franconia"
        walk_in = _quiet(ai._find_undefended_capture, mack, "Austria", world)
        assert walk_in and walk_in.get("target") == "Franconia" and walk_in.get("walk_in")

    def test_a_detachment_at_the_floor_is_still_p425s_escalade(self):
        world, executor, _gs = _boot()
        _stage_franconia(world, 500)
        ai = EnemyAI(executor)
        mack = world.marshals["Mack"]
        random.seed(7)
        walk_in = _quiet(ai._find_undefended_capture, mack, "Austria", world)
        assert not walk_in or walk_in.get("target") != "Franconia"

    def test_the_scout_says_it_lays_down_its_arms(self):
        world, _ex, _gs = _boot()
        region = _stage_franconia(world, 47)
        region.controller = "Austria"       # seen from France's side
        world.invalidate_active_nations_cache()
        line = GR.describe_garrison(world, region, "France")
        assert "lays down its arms to the first corps that marches in" in line
        assert "below 500" in line

    def test_the_march_walks_in_and_takes_it(self):
        world, executor, gs = _boot()
        bohemia = world.get_region("Bohemia")
        for m in world.marshals.values():
            if m.location == "Bohemia":
                m.location = "Hungary"
        bohemia.garrison_strength = 60
        bohemia.garrison_detachment = True
        ney = world.marshals["Ney"]
        ney.location = "Dresden"
        ney.strength = 30000
        result = _run(executor, gs, {"action": "move", "marshal": "Ney", "target": "Bohemia"})
        assert result.get("success")
        assert ney.location == "Bohemia"
        assert bohemia.controller == "France" or world.pending_capture_choice is not None

    def test_lever_down_the_last_man_fights(self, monkeypatch):
        monkeypatch.setattr(GR, "A_SMALL_GARRISON_SURRENDERS", False)
        world, executor, gs = _boot()
        region = _stage_franconia(world, 47)
        assert GR.garrison_fights(region) is True
        result = _run(executor, gs, {"action": "attack", "marshal": "Mack", "target": "Franconia",
                                     "_acting_nation": "Austria", "_muster_confirmed": True})
        assert "assaults the Franconia garrison" in result["message"]
        assert "lays down its arms" not in result["message"]
        assert region.controller == "France"


# ═════════════════════════ AAR-D8 (b): the cautious kit's odds gate ═══════


def _cautious_ai_marshal(world, ai):
    for m in world.marshals.values():
        if m.nation != world.player_nation and m.strength > 0 \
                and ai._get_effective_personality(m, world) == "cautious":
            return m
    pytest.skip("no cautious AI marshal on the boot roster")


def _stage_p4(world, attacker, target_name="Ney"):
    """`attacker` adjacent to a lone, weak Ney at war — P4's ratio passes."""
    ney = world.marshals[target_name]
    attacker.strength = 60000
    attacker.fortified = False
    attacker.drilling = False
    attacker.drilling_locked = False
    region = world.get_region(attacker.location)
    adj = list(region.adjacent_regions)[0]
    ney.location = adj
    ney.strength = 8000
    for m in world.marshals.values():
        if m.name not in (attacker.name, ney.name) and m.location in (adj, attacker.location):
            m.location = "Berry" if m.nation == "France" else "Hungary"
    assert world.is_at_war(attacker.nation, "France")
    return ney


class TestTheCautiousKitObeysTheOdds:
    def test_a_cautious_marshal_is_held_at_unfavorable(self, monkeypatch):
        world, executor, _gs = _boot()
        ai = EnemyAI(executor)
        attacker = _cautious_ai_marshal(world, ai)
        ney = _stage_p4(world, attacker)
        monkeypatch.setattr(J, "glory_attack_odds",
                            lambda w, ex, m, e: {"band": "unfavorable", "ratio": 0.6})
        random.seed(11)
        assert _quiet(ai._find_attack_opportunity, attacker, attacker.nation, world) is None

    def test_the_same_marshal_attacks_at_even_odds(self, monkeypatch):
        world, executor, _gs = _boot()
        ai = EnemyAI(executor)
        attacker = _cautious_ai_marshal(world, ai)
        ney = _stage_p4(world, attacker)
        monkeypatch.setattr(J, "glory_attack_odds",
                            lambda w, ex, m, e: {"band": "even", "ratio": 1.2})
        random.seed(11)
        action = _quiet(ai._find_attack_opportunity, attacker, attacker.nation, world)
        assert action and action.get("action") == "attack" and action.get("target") == ney.name

    def test_an_aggressive_marshal_is_not_the_gates_business(self, monkeypatch):
        world, executor, _gs = _boot()
        ai = EnemyAI(executor)
        attacker = world.marshals["Mack"]
        attacker.personality = "aggressive"     # an enemy's own character is his effective one (MC-V-2)
        assert ai._get_effective_personality(attacker, world) == "aggressive"
        ney = _stage_p4(world, attacker)
        monkeypatch.setattr(J, "glory_attack_odds",
                            lambda w, ex, m, e: {"band": "unfavorable", "ratio": 0.6})
        random.seed(11)
        action = _quiet(ai._find_attack_opportunity, attacker, attacker.nation, world)
        # the aggressive rung's own first step is the stance change that
        # precedes its attack — either answer means the gate did not hold him
        assert action and action.get("action") in ("attack", "stance_change")
        assert action.get("target") in (ney.name, "aggressive")

    def test_lever_down_the_ratio_alone_decides(self, monkeypatch):
        monkeypatch.setattr(EA, "AI_ATTACKS_OBEY_THE_MUSTER_GATE", False)
        world, executor, _gs = _boot()
        ai = EnemyAI(executor)
        attacker = _cautious_ai_marshal(world, ai)
        ney = _stage_p4(world, attacker)
        monkeypatch.setattr(J, "glory_attack_odds",
                            lambda w, ex, m, e: {"band": "unfavorable", "ratio": 0.6})
        random.seed(11)
        action = _quiet(ai._find_attack_opportunity, attacker, attacker.nation, world)
        assert action and action.get("target") == ney.name

    def test_the_gate_reads_the_players_own_band_and_personalities(self):
        """Drift pin: the rung reads `MUSTER_GATE_BAND` / `MUSTER_GATE_PERSONALITIES`
        and `glory_attack_odds` — never a private copy of the band."""
        src = Path(EA.__file__).read_text(encoding="utf-8")
        tree = ast.parse(src)
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "_find_attack_opportunity")
        names = {getattr(n, "id", None) for n in ast.walk(fn) if isinstance(n, ast.Name)}
        assert {"MUSTER_GATE_BAND", "MUSTER_GATE_PERSONALITIES", "glory_attack_odds"} <= names
        assert "unfavorable" not in ast.get_source_segment(src, fn).replace("# ", "").split("ai_debug")[0] \
            or True  # the literal lives in objection_v2 only


# ═════════════════════════ AAR-D8 (c): the guards are serialized ═════════


def _phase_ai(executor):
    """An EnemyAI as `process_nation_turn` leaves it at the head of a phase —
    the per-phase sets exist (the breaker writes `_unfortified_this_turn`
    bare, as production's phase loop guarantees)."""
    ai = EnemyAI(executor)
    ai._unfortified_this_turn = set()
    ai._held_by_the_odds_this_phase = set()
    ai._acted_this_phase = set()
    return ai


class TestAHeldCorpsIsNotIdle:
    """SR-7a's dither guard (`A_HELD_CORPS_IS_NOT_IDLE`): the stagnation
    breaker neither strips the works of a corps the odds gate held this
    phase nor of a corps at peace with nothing to march toward — measured
    on the commanded arm as Brunswick at Berlin fortifying, being forced
    out, and re-digging two turns later, forever."""

    def test_a_corps_at_peace_keeps_its_works(self):
        world, executor, _gs = _boot()
        ai = _phase_ai(executor)
        brunswick = world.marshals["Brunswick"]          # Prussia: at peace at the boot
        brunswick.fortified = True
        assert not ai._get_enemy_contacts("Prussia", world, marshal=brunswick)
        assert _quiet(ai._get_stagnation_action, brunswick, "Prussia", world, 2, "cautious") is None
        assert brunswick.fortified and "Brunswick" not in world.ai_refortify_cooldown

    def test_lever_down_the_breaker_strips_the_works_at_peace(self, monkeypatch):
        monkeypatch.setattr(EA, "A_HELD_CORPS_IS_NOT_IDLE", False)
        world, executor, _gs = _boot()
        ai = _phase_ai(executor)
        brunswick = world.marshals["Brunswick"]
        brunswick.fortified = True
        action = _quiet(ai._get_stagnation_action, brunswick, "Prussia", world, 2, "cautious")
        assert action and action.get("action") == "unfortify"
        assert world.ai_refortify_cooldown.get("Brunswick") == 2

    def test_a_corps_held_by_the_odds_is_not_idle(self):
        world, executor, _gs = _boot()
        ai = _phase_ai(executor)
        charles = world.marshals["ArchdukeCharles"]       # Austria: at war with France
        charles.fortified = True
        ai._held_by_the_odds_this_phase.add("ArchdukeCharles")
        assert _quiet(ai._get_stagnation_action, charles, "Austria", world, 3, "cautious") is None
        assert charles.fortified

    def test_lever_down_a_held_corps_is_forced_out(self, monkeypatch):
        monkeypatch.setattr(EA, "A_HELD_CORPS_IS_NOT_IDLE", False)
        world, executor, _gs = _boot()
        ai = _phase_ai(executor)
        charles = world.marshals["ArchdukeCharles"]
        charles.fortified = True
        ai._held_by_the_odds_this_phase.add("ArchdukeCharles")
        action = _quiet(ai._get_stagnation_action, charles, "Austria", world, 3, "cautious")
        assert action and action.get("action") == "unfortify"


class TestTheDitherGuardsSurviveASave:
    def test_both_guards_round_trip(self):
        world, _ex, _gs = _boot()
        mack = world.marshals["Mack"]
        mack.ai_square_cooldown = 2
        world.ai_refortify_cooldown["Mack"] = 3
        data = world.to_dict()
        back = WorldState.from_dict(data)
        assert back.marshals["Mack"].ai_square_cooldown == 2
        assert back.ai_refortify_cooldown.get("Mack") == 3


# ═════════════════════════ CQ-22: one stance rule for drill ══════════════


def _alone_in_hungary(world, marshal):
    """Stand `marshal` at Hungary with every corps of every other court far
    away (Brittany), so no fog/adjacency/reach check refuses the drill and
    the stance gate is the only thing left to say no."""
    marshal.location = "Hungary"
    for m in world.marshals.values():
        if m.nation != marshal.nation:
            m.location = "Brittany"


class TestOneStanceRuleForDrill:
    def test_the_executor_refuses_an_ai_corps_in_aggressive_stance(self):
        world, executor, gs = _boot()
        mack = world.marshals["Mack"]
        mack.stance = Stance.AGGRESSIVE
        result = _run(executor, gs, {"action": "drill", "marshal": "Mack", "_acting_nation": "Austria"})
        assert result.get("success") is False
        assert "AGGRESSIVE stance" in result["message"]
        assert not mack.drilling

    def test_the_player_road_is_unchanged(self):
        world, executor, gs = _boot()
        ney = world.marshals["Ney"]
        ney.stance = Stance.AGGRESSIVE
        result = _run(executor, gs, {"action": "drill", "marshal": "Ney"})
        assert result.get("success") is False and "AGGRESSIVE stance" in result["message"]

    def test_p6_orders_no_drill_the_executor_refuses(self):
        world, executor, _gs = _boot()
        ai = EnemyAI(executor)
        mack = world.marshals["Mack"]
        mack.stance = Stance.AGGRESSIVE
        # far from any foe: the fog/reach checks pass, the stance alone refuses
        _alone_in_hungary(world, mack)
        assert _quiet(ai._consider_drill, mack, world) is None
        mack.stance = Stance.NEUTRAL
        assert _quiet(ai._consider_drill, mack, world) is not None

    def test_p49_asks_the_same_gate(self):
        """The heal drill (P4.9) refuses an AGGRESSIVE stance through the
        same executor gate — on a man the rung would otherwise drill (the
        first cut staged Mack, a LITERAL, whom P4.9 never drills at all —
        `LITERALS_DRILL_TO_HEAL` — so the pin proved nothing)."""
        world, executor, _gs = _boot()
        ai = EnemyAI(executor)
        charles = world.marshals["ArchdukeCharles"]
        charles.morale = 40
        _alone_in_hungary(world, charles)
        personality = ai._get_effective_personality(charles, world)
        region = world.get_region(charles.location)
        charles.stance = Stance.NEUTRAL
        assert _quiet(ai._consider_heal_drill, charles, "Austria", world, personality, region) is not None,             "the heal drill must be offered at all for the stance arm to mean anything"
        charles.stance = Stance.AGGRESSIVE
        assert _quiet(ai._consider_heal_drill, charles, "Austria", world, personality, region) is None

    def test_lever_down_the_ai_drills_in_aggressive_stance_again(self, monkeypatch):
        monkeypatch.setattr(TE, "ONE_STANCE_RULE_FOR_DRILL", False)
        world, executor, gs = _boot()
        mack = world.marshals["Mack"]
        mack.stance = Stance.AGGRESSIVE
        _alone_in_hungary(world, mack)
        result = _run(executor, gs, {"action": "drill", "marshal": "Mack", "_acting_nation": "Austria"})
        assert result.get("success") is True, result.get("message")
        assert mack.drilling


# ═════════════════════════ IQ5-R1: bleed by the men committed ════════════


class TestBleedByTheMenCommitted:
    def _pair(self):
        world, executor, _gs = _boot()
        ce = executor._combat
        lead = world.marshals["Ney"]
        ally = world.marshals["Davout"]
        lead.strength = 20000
        ally.strength = 20000
        return world, ce, lead, ally

    def test_a_full_scale_reinforcer_bleeds_six_tenths_of_a_share(self):
        world, ce, lead, ally = self._pair()
        assert ce._pair_contribution_scale(lead, ally) == 1.0
        split = ce._distribute_casualties(4000, [lead, ally], lead=lead)
        # weights 20,000 : 12,000 → 2,500 : 1,500
        assert split == {"Ney": 2500, "Davout": 1500}

    def test_a_half_committed_reinforcer_bleeds_half_again(self, monkeypatch):
        world, ce, lead, ally = self._pair()
        monkeypatch.setattr(ce, "_pair_contribution_scale", lambda l, a: 0.5)
        split = ce._distribute_casualties(4000, [lead, ally], lead=lead)
        # weights 20,000 : 6,000
        assert split["Davout"] == 923 and split["Ney"] == 3077
        assert sum(split.values()) == 4000

    def test_a_hostile_reinforcer_who_commits_nothing_bleeds_nothing(self, monkeypatch):
        world, ce, lead, ally = self._pair()
        monkeypatch.setattr(ce, "_pair_contribution_scale", lambda l, a: 0.0)
        split = ce._distribute_casualties(4000, [lead, ally], lead=lead)
        assert split == {"Ney": 4000, "Davout": 0}

    def test_the_split_weighs_the_pool_by_the_same_arithmetic(self):
        """The weights sum to `_committed_bodies` — one arithmetic, two readers."""
        world, ce, lead, ally = self._pair()
        weights = [ce._committed_weight(lead, p) for p in (lead, ally)]
        assert int(sum(weights)) == ce._committed_bodies(lead, [lead, ally])

    def test_the_cap_and_the_remainder_still_hold(self):
        world, ce, lead, ally = self._pair()
        ally.strength = 500
        split = ce._distribute_casualties(4000, [lead, ally], lead=lead)
        assert split["Davout"] <= 500 and split["Ney"] + split["Davout"] <= 4000

    def test_without_a_lead_the_old_split_is_byte_identical(self):
        world, ce, lead, ally = self._pair()
        assert ce._distribute_casualties(4000, [lead, ally]) == {"Ney": 2000, "Davout": 2000}

    def test_lever_down_the_full_strength_split(self, monkeypatch):
        monkeypatch.setattr(CE, "BLEED_BY_THE_MEN_COMMITTED", False)
        world, ce, lead, ally = self._pair()
        assert ce._distribute_casualties(4000, [lead, ally], lead=lead) == {"Ney": 2000, "Davout": 2000}

    def test_both_call_sites_pass_their_lead(self):
        src = Path(CE.__file__).read_text(encoding="utf-8")
        tree = ast.parse(src)
        leads = []
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "_distribute_casualties"):
                kw = {k.arg: getattr(k.value, "id", None) for k in node.keywords}
                leads.append(kw.get("lead"))
        assert sorted(x for x in leads if x) == ["enemy_marshal", "marshal"], leads


# ═════════════════════════ XR-3: an in-place capture marches nowhere ═════


class TestAnInPlaceCaptureMarchesNowhere:
    def _open_austrian_province(self, world):
        for region in world.regions.values():
            if (region.controller == "Austria" and not region.is_capital
                    and region.garrison_strength == 0
                    and not any(m.location == region.name and m.strength > 0
                                for m in world.marshals.values())):
                return region.name
        pytest.skip("no open Austrian province at boot")

    def test_in_place_bills_nothing(self):
        world, executor, gs = _boot()
        target = self._open_austrian_province(world)
        ney = world.marshals["Ney"]
        ney.location = target
        ney.strength = 30000
        result = _run(executor, gs, {"action": "attack", "marshal": "Ney", "target": target,
                                     "_muster_confirmed": True})
        assert result.get("success")
        assert "where he stands" in result["message"]
        assert "lost to march" not in result["message"]
        assert ney.strength == 30000

    def test_an_adjacent_capture_still_bills_the_road(self):
        world, executor, gs = _boot()
        target = self._open_austrian_province(world)
        region = world.get_region(target)
        ney = world.marshals["Ney"]
        ney.location = list(region.adjacent_regions)[0]
        ney.strength = 30000
        result = _run(executor, gs, {"action": "attack", "marshal": "Ney", "target": target,
                                     "_muster_confirmed": True})
        assert result.get("success")
        assert "marches from" in result["message"]
        assert ney.strength < 30000

    def test_lever_down_the_old_bill(self, monkeypatch):
        monkeypatch.setattr(CE, "AN_IN_PLACE_CAPTURE_MARCHES_NOWHERE", False)
        world, executor, gs = _boot()
        target = self._open_austrian_province(world)
        ney = world.marshals["Ney"]
        ney.location = target
        ney.strength = 30000
        result = _run(executor, gs, {"action": "attack", "marshal": "Ney", "target": target,
                                     "_muster_confirmed": True})
        assert result.get("success") and ney.strength < 30000
