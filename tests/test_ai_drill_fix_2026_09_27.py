"""The AI drill fix (user-directed, September 27, 2026): "fix AI, be good —
we don't want them drilling when they can get attacked".

* THE DRILLING PENALTY IS READ (GR4, a pre-existing defect): `combat.py`
  cancelled the drill BEFORE `get_defense_modifier` read it, so the -25% a
  corps caught drilling suffers — printed on the report, snapshotted on the
  battle report — was never applied. Now the modifier reads the drill, then
  the drill is lost (lever `combat.DRILL_PENALTY_READ_BEFORE_THE_CLEAR`).
* THE ONE REACH PREDICATE (`enemy_ai.drill_reach_threat`): the first corps
  AT WAR with the drilling corps' court that could reach and strike it before
  the drill ends — (exposed enemy phases + 1) x its range: 3 regions for
  infantry, 6 for cavalry, 2 for an infantryman against Soult's one-day
  Drillmaster. A court at peace and a prisoner are not threats. Omniscient,
  like `_evaluate_capture_safety`.
* P4.9 DRILL TO HEAL: a debased corps (morale < 70, a real corps, the
  executor would take the order) drills where nothing can reach it — above
  P5, whose works would lock it out; it ignores P6's shock-bonus gate; it
  yields to P6.5's supply move, the AI-3c frontier and P7.4's reinforcement.
  Literals are held out (MC-V-2, the user's July 11 ruling;
  `LITERALS_DRILL_TO_HEAL`).
* P6 READS THE REACH (`AI_DRILL_READS_THE_REACH`): the shock drill asks the
  same predicate — measured, 7 of the old AI's 9 drills on the ambient board
  began within reach of a corps at war.
* THE DAY'S WORK (`DRILL_IS_THE_DAYS_WORK`) and EVERY DEFAULT LEAVES THE
  DRILL (`EVERY_DEFAULT_LEAVES_THE_DRILL`): a corps that began a drill is
  done for the phase; P8's aggressive default no longer orders a drilling
  corps a stance change the executor refuses (R1-5 guarded the cautious
  branch alone).
"""
import contextlib
import io
import json
import random
from pathlib import Path

import pytest

import backend.ai.enemy_ai as EA
import backend.game_logic.combat as CB
from backend.commands.executor import CommandExecutor
from backend.game_logic.combat import CombatResolver
from backend.models.world_state import WorldState

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture
def world():
    with _quiet():
        return WorldState.from_scenario(str(MAP))


@pytest.fixture
def ai():
    return EA.EnemyAI(CommandExecutor())


def _at_distance(world, origin, k):
    for name in sorted(world.regions):
        if world.get_distance(origin, name) == k:
            return name
    raise AssertionError(f"no province {k} hops from {origin}")


def _only_threat(world, marshal, keep):
    """Every corps at war with `marshal`'s court but `keep` stands down (the
    pins are about ONE hostile corps, whatever else the board holds)."""
    for other in world.marshals.values():
        if (other.nation != marshal.nation and other.name != keep
                and world.is_at_war(marshal.nation, other.nation)):
            other.strength = 0


# ═══════════════════════════ THE DRILLING PENALTY IS READ ═════════════════════

def _battle(drilling):
    with _quiet():
        world = WorldState.from_scenario(str(MAP))
    ney, mack = world.marshals["Ney"], world.marshals["Mack"]
    ney.strength, mack.strength = 30000, 20000
    mack.drilling = mack.drilling_locked = drilling
    mack.drill_complete_turn = 5 if drilling else -1
    random.seed(7)
    with _quiet():
        result = CombatResolver().resolve_battle(ney, mack, apply_casualties=False)
    return result, mack


class TestTheDrillingPenaltyIsRead:

    def test_a_corps_caught_drilling_takes_the_printed_penalty(self):
        calm, _ = _battle(False)
        caught, _ = _battle(True)
        assert caught["drilling_penalty_triggered"].endswith("(-25% defense)")
        # the defense modifier x0.75 divides into the casualty share: the
        # defender's loss is the undrilled loss / 0.75, to the man
        assert abs(caught["defender_raw_casualties"]
                   - calm["defender_raw_casualties"] / 0.75) <= 2
        assert caught["attacker_raw_casualties"] == calm["attacker_raw_casualties"]

    def test_the_drill_is_still_lost_after_the_read(self):
        _result, mack = _battle(True)
        assert (mack.drilling, mack.drilling_locked, mack.drill_complete_turn,
                mack.shock_bonus) == (False, False, -1, 0)

    def test_the_lever_down_is_the_old_defect(self, monkeypatch):
        monkeypatch.setattr(CB, "DRILL_PENALTY_READ_BEFORE_THE_CLEAR", False)
        calm, _ = _battle(False)
        caught, _ = _battle(True)
        assert caught["defender_raw_casualties"] == calm["defender_raw_casualties"]
        assert caught["drilling_penalty_triggered"]  # the report said it anyway


# ═══════════════════════════ THE ONE REACH PREDICATE ═════════════════════════

class TestTheReachPredicate:
    """Castanos (Spain, at war with Britain) at Andalusia; Moore the one
    British corps left standing, moved to a chosen distance."""

    def _place(self, world, k, cavalry=False):
        castanos, moore = world.marshals["Castanos"], world.marshals["Moore"]
        _only_threat(world, castanos, "Moore")
        moore.location = _at_distance(world, castanos.location, k)
        moore.movement_range = 2 if cavalry else 1
        return castanos, moore

    def test_infantry_reaches_three_regions(self, world):
        castanos, moore = self._place(world, 3)
        assert EA.drill_reach_threat(world, castanos) is moore
        castanos, _moore = self._place(world, 4)
        assert EA.drill_reach_threat(world, castanos) is None

    def test_cavalry_reaches_six_regions(self, world):
        castanos, moore = self._place(world, 6, cavalry=True)
        assert EA.drill_reach_threat(world, castanos) is moore
        castanos, _moore = self._place(world, 7, cavalry=True)
        assert EA.drill_reach_threat(world, castanos) is None

    def test_a_court_at_peace_is_no_threat(self, world):
        castanos = world.marshals["Castanos"]
        _only_threat(world, castanos, "")
        brunswick = world.marshals["Brunswick"]
        assert not world.is_at_war("Spain", "Prussia")
        brunswick.location = _at_distance(world, castanos.location, 1)
        assert EA.drill_reach_threat(world, castanos) is None

    def test_a_prisoner_is_no_threat(self, world):
        castanos, moore = self._place(world, 1)
        moore.captured_by = "Spain"
        assert EA.drill_reach_threat(world, castanos) is None

    def test_the_drillmaster_stands_exposed_one_phase(self, world):
        """Soult's drill completes the day it is ordered: one enemy phase,
        so an infantryman reaches two regions, not three."""
        soult, ney = world.marshals["Soult"], world.marshals["Ney"]
        assert soult.ability.get("name") == "Drillmaster of Boulogne"
        john = world.marshals["ArchdukeJohn"]
        _only_threat(world, soult, "ArchdukeJohn")
        john.location = _at_distance(world, soult.location, 3)
        assert EA.drill_reach_threat(world, soult) is None
        ney.location = soult.location
        assert EA.drill_reach_threat(world, ney) is john
        john.location = _at_distance(world, soult.location, 2)
        assert EA.drill_reach_threat(world, soult) is john


# ═══════════════════════════ P4.9 — DRILL TO HEAL ═════════════════════════════

def _heal(ai, world, name, nation):
    m = world.marshals[name]
    with _quiet():
        return ai._consider_heal_drill(
            m, nation, world, EA.get_effective_ai_personality(m, world),
            world.get_region(m.location))


class TestTheHealRung:

    @pytest.mark.parametrize("name,nation", [("Castanos", "Spain"),
                                             ("Hohenlohe", "Prussia"),
                                             ("Armfelt", "Sweden")])
    def test_a_debased_corps_out_of_reach_drills_before_it_fortifies(
            self, world, ai, monkeypatch, name, nation):
        world.marshals[name].morale = 50
        with _quiet():
            assert ai._evaluate_marshal(world.marshals[name], nation, world) == (
                {"marshal": name, "action": "drill"}, 5)
        monkeypatch.setattr(EA, "AI_DRILLS_TO_HEAL", False)
        with _quiet():
            action, prio = ai._evaluate_marshal(world.marshals[name], nation, world)
        # the rung it pre-empts: P5, the cautious works (its first step)
        assert (action["action"], prio) == ("stance_change", 5)

    def test_a_corps_within_reach_does_not_heal(self, world, ai):
        """Kutuzov at Podolia: Murat's cavalry is within six regions."""
        world.marshals["Kutuzov"].morale = 50
        assert EA.drill_reach_threat(world, world.marshals["Kutuzov"]) is not None
        assert _heal(ai, world, "Kutuzov", "Russia") is None

    def test_the_gates(self, world, ai):
        castanos = world.marshals["Castanos"]
        castanos.morale = 70
        assert _heal(ai, world, "Castanos", "Spain") is None       # not debased
        castanos.morale = 50
        castanos.strength = EA.STUB_STRENGTH_FLOOR - 1
        assert _heal(ai, world, "Castanos", "Spain") is None       # a remnant
        castanos.strength = 15000
        castanos.broken = True
        assert _heal(ai, world, "Castanos", "Spain") is None       # broken: FA-N6's limited corps
        castanos.broken = False
        castanos.fortified = True
        assert _heal(ai, world, "Castanos", "Spain") is None       # the executor refuses
        castanos.fortified = False
        assert _heal(ai, world, "Castanos", "Spain") == {"marshal": "Castanos", "action": "drill"}

    def test_the_heal_ignores_the_shock_bonus(self, world, ai):
        """P6 refuses a corps that holds a shock bonus — which only an attack
        clears, so a corps at peace would heal once. The heal heals again."""
        castanos = world.marshals["Castanos"]
        castanos.morale, castanos.shock_bonus = 60, 2
        assert _heal(ai, world, "Castanos", "Spain") == {"marshal": "Castanos", "action": "drill"}

    def test_a_literal_is_held_out_by_the_standing_ruling(self, world, ai, monkeypatch):
        """AIDR-D1 DECIDED September 28, 2026 (SR-5a session; the user
        delegated it: "make a decision — remember Mack sucked"): held out.
        The literal's rot in place is the character MC-V-2 authored."""
        assert EA.LITERALS_DRILL_TO_HEAL is False
        armfelt = world.marshals["Armfelt"]
        armfelt.morale, armfelt.personality = 50, "literal"
        assert EA.get_effective_ai_personality(armfelt, world) == "literal"
        assert _heal(ai, world, "Armfelt", "Sweden") is None
        monkeypatch.setattr(EA, "LITERALS_DRILL_TO_HEAL", True)
        assert _heal(ai, world, "Armfelt", "Sweden") == {"marshal": "Armfelt", "action": "drill"}

    @pytest.mark.parametrize("duty", ["_supply_pressure_move",
                                      "_find_defensive_reinforcement_position"])
    def test_it_yields_to_a_more_pressing_duty(self, world, ai, monkeypatch, duty):
        world.marshals["Castanos"].morale = 50
        monkeypatch.setattr(type(ai), duty,
                            lambda self, *a, **k: {"marshal": "Castanos", "action": "move"})
        assert _heal(ai, world, "Castanos", "Spain") is None

    def test_it_yields_to_the_war_intent_frontier(self, world, ai, monkeypatch):
        import backend.game_logic.war_council as WC
        world.marshals["Castanos"].morale = 50
        monkeypatch.setattr(WC, "get_intent_frontier",
                            lambda w, n: {"Portugal"} if n == "Spain" else set())
        assert _heal(ai, world, "Castanos", "Spain") is None

    def test_the_lever_down_heals_no_one(self, world, ai, monkeypatch):
        world.marshals["Castanos"].morale = 50
        monkeypatch.setattr(EA, "AI_DRILLS_TO_HEAL", False)
        assert _heal(ai, world, "Castanos", "Spain") is None


# ═══════════════════════════ P6 READS THE REACH ═══════════════════════════════

class TestTheShockDrillReadsTheReach:

    def test_no_shock_drill_within_reach(self, world, ai, monkeypatch):
        """Moore two regions from Castanos — not adjacent, so the old fog
        check passed, yet he can march and strike before the drill ends."""
        castanos, moore = world.marshals["Castanos"], world.marshals["Moore"]
        castanos.personality = "aggressive"
        _only_threat(world, castanos, "Moore")
        moore.location = _at_distance(world, castanos.location, 2)
        with _quiet():
            assert ai._consider_drill(castanos, world) is None
        monkeypatch.setattr(EA, "AI_DRILL_READS_THE_REACH", False)
        with _quiet():
            assert ai._consider_drill(castanos, world) == {"marshal": "Castanos", "action": "drill"}


# ═══════════════════════════ THE DAY'S WORK / EVERY DEFAULT ═══════════════════

def _spain_phase():
    with _quiet():
        world = WorldState.from_scenario(str(MAP))
        world.marshals["Castanos"].morale = 50
        ai = EA.EnemyAI(CommandExecutor())
        results = ai.process_nation_turn("Spain", world, {"world": world})
    return world, ai, [r["ai_action"] for r in results if isinstance(r, dict) and r.get("ai_action")]


class TestTheDaysWork:

    def test_a_corps_that_began_a_drill_is_done_for_the_phase(self, monkeypatch):
        world, ai, actions = _spain_phase()
        assert actions == [{"marshal": "Castanos", "action": "drill"}]
        assert world.marshals["Castanos"].drilling is True
        assert "Castanos" in ai._marshals_done_this_turn
        monkeypatch.setattr(EA, "DRILL_IS_THE_DAYS_WORK", False)
        _world, _ai, actions = _spain_phase()
        assert actions[0] == {"marshal": "Castanos", "action": "drill"} and len(actions) > 1


class TestEveryDefaultLeavesTheDrill:

    def test_the_aggressive_default_orders_a_drilling_corps_nothing(self, world, ai, monkeypatch):
        from backend.models.marshal import Stance
        castanos = world.marshals["Castanos"]
        castanos.personality = "aggressive"
        castanos.drilling, castanos.drilling_locked = True, True
        castanos.stance = Stance.NEUTRAL
        with _quiet():
            assert ai._get_default_action(castanos, world) == {"marshal": "Castanos", "action": "wait"}
        monkeypatch.setattr(EA, "EVERY_DEFAULT_LEAVES_THE_DRILL", False)
        with _quiet():
            assert ai._get_default_action(castanos, world) == {
                "marshal": "Castanos", "action": "stance_change", "target": "aggressive"}


# ═══════════════════════════ THE MEASURED ACCEPTANCE ══════════════════════════

class TestTheMeasuredArms:
    """`tools/_drill_fix_series_arms.py` — every lever set in the child, the
    recorded ambient board, every AI drill counted with the nearest corps at
    war with its court."""

    @pytest.fixture(scope="class")
    def arms(self):
        return json.loads((ROOT / "tools" / "_drill_fix_series_arms.json").read_text(encoding="utf-8"))

    def test_every_lever_down_reproduces_the_prior_series(self, arms):
        assert arms["arms"]["0"]["series"] == arms["recorded"]

    def test_the_old_ai_drilled_within_reach_and_the_fix_never_does(self, arms):
        assert arms["arms"]["0"]["drillfix"]["within_reach"] >= 1
        assert arms["arms"]["1"]["drillfix"]["within_reach"] == 0

    def test_the_heal_and_the_penalty_alone_leave_the_series_unmoved(self, arms):
        """The recorded SERIES only: the heal alone still changes the board
        (France 2 provinces at turn 40 on arm H, 3 on arm 0)."""
        for lever in ("H", "C"):
            assert arms["arms"][lever]["series"] == arms["recorded"], lever

    def test_the_shipped_series_is_the_fix(self, arms):
        """RE-SEATED by SR-5a "The chest" (September 28, 2026): the series
        was re-recorded once more, for the ruled balance package. The drill
        fix's arm 1 is now the prior record SR-5a's arm 0 (the pre-slice
        scenario, every lever down) reproduces byte for byte; SR-5a's arm 1
        is the standing series (`tools/_sr5a_series_arms.json`)."""
        from tests.test_ai_intent_threat_migration import BASELINE_SERIES
        drill = arms
        # RE-SEATED by SR-5a "The chest" (September 28, 2026): one more link —
        # the drill fix's arm 1 is the prior record SR-5a's arm 0 (the
        # pre-slice scenario, every lever down) reproduces byte for byte, and
        # SR-5a's arm 1 (the ruled balance package) is the standing series.
        sr5a = json.loads((ROOT / "tools" / "_sr5a_series_arms.json").read_text(
            encoding="utf-8"))
        assert drill["arms"]["1"]["series"] == sr5a["recorded"]
        assert sr5a["arms"]["0"]["series"] == sr5a["recorded"]
        # RE-SEATED by Score Finish Step 3 "Europe acts without France" (October
        # 2, 2026): one more link — SR-5a's arm 1 is the prior record Step 3's
        # arm 0 (every Step-3 lever down in the child) reproduces byte for
        # byte, and Step 3's ALL arm (the shipped tree) is the standing series
        # (`tools/_step3_series_arms_final.json`, fifteen arms).
        step3 = json.loads((ROOT / "tools" / "_step3_series_arms_final.json").read_text(
            encoding="utf-8"))
        assert sr5a["arms"]["1"]["series"] == step3["prior"]
        assert step3["arms"]["0"]["series"] == step3["prior"]
        assert BASELINE_SERIES == step3["arms"]["ALL"]["series"]
