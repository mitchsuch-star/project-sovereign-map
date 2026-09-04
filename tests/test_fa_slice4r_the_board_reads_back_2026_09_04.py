"""Final Whole-Game Audit — slice 4 REVIEW ROUND, "The Board Reads Back".

Three review lenses attacked slice 4 ("The AI Reads the Board", d2ca0228)
at master 85130a6f (reports committed under
`docs/audits/fa_build_2026_09_04/REVIEW_slice4_R{1,2,3}_*.md`). The
AI-decisions lens found the board reading back WRONG at eight more seams —
several inside the slice's own fixes:

* R1-1 — the counter-punch and the P7.5 range arm priced a
  `retreated_this_turn` target at his NEIGHBOURS' strength (the field helper
  excludes retreated corps; P4 guards it with `max(field, enemy)`, the two
  new sites did not): a 20k Wellington struck a 30k Ney at "4.0".
* R1-2 — the ally-support "must attack to join" arm was the only unpriced
  attack in the tree and, by rung order, fired only after P4 had DECLINED
  the same target: a cautious 30k Wellington struck a 40k Davout, -2,358.
* R1-3 — the AI's own admin recruit broke the square the phase had just
  paid for, and `_auto_break_square` then forbade re-forming it for two
  turns (Mack, twice on the shipped board).
* R1-4 — the stagnation tracker did not count `form_square` as meaningful
  and read last phase's counter within the phase: it marched squared corps
  out from under the cavalry and cancelled a drill paid a moment earlier.
* R1-5 — FA-R2's mirror: a DRILLING corps was ordered stance / fortify /
  move and refused (six of the shipped board's seven remaining refusals).
* R1-6 (GR5) — the AI's banked counter-punch was destroyed by an undefended
  capture with no free-action credit; the player's exit stamps it.
* R1-7 — FA-N54's oscillation: forced AGGRESSIVE at turn start, the cautious
  rung bought DEFENSIVE back for 2 AP, forced again (Paget, twice in seven).
* R1-8 (GR5, pre-existing) — a fortified AI or autonomous corps could MARCH
  and keep its fortification bonus; the refusal lived in the player branch.

Every fix sits behind a lever whose False arm reproduces the prior
behaviour byte-for-byte; `BASELINE_SERIES` is re-recorded ONCE with a
ten-arm attribution (arm 0 reproduces the prior series). The fixtures below
are the reviewer's own reproductions, re-run on the shipped code.
"""
import contextlib
import io
import random

import pytest

import backend.ai.enemy_ai as ea
import backend.commands.combat_executor as ce
import backend.commands.movement_executor as mv
from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
from backend.commands.strategic import ATTACK_FUTILITY_LIMIT
from backend.models.marshal import Stance
from backend.models.world_state import WorldState

LEVERS = {
    ea: ("FIELD_PRICES_THE_TARGET_TOO", "ALLY_SUPPORT_PRICES_THE_FIELD",
         "ADMIN_RECRUIT_SPARES_THE_SQUARE", "STAGNATION_READS_THE_PHASE",
         "DRILLING_CORPS_IS_LEFT_TO_DRILL", "CAVALRY_AI_READS_THE_LIMIT"),
    ce: ("COUNTER_PUNCH_CREDITS_THE_CAPTURE",),
    mv: ("FORTIFIED_CORPS_NEVER_MARCHES",),
}


@pytest.fixture(autouse=True)
def _levers_at_default():
    saved = [(m, n, getattr(m, n)) for m, names in LEVERS.items() for n in names]
    yield
    for m, n, v in saved:
        setattr(m, n, v)


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _legacy():
    """The 19-region fixture: France vs Britain/Prussia at WAR, Austria at
    PEACE; the French roster parked at Bordeaux."""
    world = WorldState(player_nation="France")
    for m in world.marshals.values():
        if m.nation == "France":
            m.location = "Bordeaux"
    return world


def _british_soil(world):
    """The reviewer's idiom: every French province but Paris is Britain's,
    so the British roster stands on its own soil for the admin and support
    rungs."""
    for r in world.regions.values():
        if r.controller == "France" and r.name != "Paris":
            r.controller = "Britain"


def _rebuild(world):
    world.invalidate_active_nations_cache()
    world._build_marshal_index()
    world.calculate_visibility()


def _ai():
    """A planner with the per-phase tracking sets `process_nation_turn` /
    `decide_single_action` would have created — the rungs are called
    directly here, as the reviewer's probes called them."""
    ai = EnemyAI(CommandExecutor())
    for name in ("_unfortified_this_turn", "_acted_this_phase",
                 "_marshals_done_this_turn", "_stance_changed_this_turn",
                 "_advanced_this_turn", "_attacked_targets_this_turn",
                 "_squares_formed_this_turn"):
        if not hasattr(ai, name):
            setattr(ai, name, set())
    if not hasattr(ai, "_pending_intents"):
        ai._pending_intents = {}
    if not hasattr(ai, "_marshal_visited_locations"):
        ai._marshal_visited_locations = {}
    if not hasattr(ai, "_consecutive_waits"):
        ai._consecutive_waits = {}
    return ai


# ═══════════════════════════════════════════════════════════════════════
# R1-1 — the field prices the target too
# ═══════════════════════════════════════════════════════════════════════

class TestTheFieldPricesTheTargetToo:

    def _board(self):
        world = _legacy()
        wel = world.marshals["Wellington"]
        wel.location, wel.strength, wel.stance = "Belgium", 20000, Stance.DEFENSIVE
        wel.fortified, wel.counter_punch_available, wel.personality = False, True, "cautious"
        ney = world.marshals["Ney"]
        ney.location, ney.strength, ney.retreated_this_turn = "Paris", 30000, True
        dav = world.marshals["Davout"]
        dav.location, dav.strength = "Paris", 5000
        world.marshals["Uxbridge"].location = "Hanover"
        _rebuild(world)
        return world, wel

    def test_a_retreated_target_is_priced_at_his_own_strength(self):
        world, wel = self._board()
        ai = _ai()
        helper = ai._defending_strength_in_region(
            ai._get_hostile_marshals_in_region("Paris", "Britain", world))
        assert helper == 5000, "the exclusion the finding rests on is gone"
        random.seed(7)
        with _quiet():
            blow = ai._get_counter_punch_action(wel, "Britain", world)
        # The retreated 30,000-man Ney is priced at 30,000 and declined; the
        # 5,000-man Davout standing beside him is the corps that would fight
        # (a retreated corps steps aside — the helper's rule), and 20k vs 5k
        # is an honest blow. What the row filed is that Ney was struck at
        # Davout's price: the blow may fire, never at Ney.
        assert not (blow and blow.get("target") == "Ney"), blow
        assert blow is None or blow.get("target") == "Davout", blow

    def test_the_lever_off_arm_reproduces_the_row(self):
        ea.FIELD_PRICES_THE_TARGET_TOO = False
        world, wel = self._board()
        random.seed(7)
        with _quiet():
            blow = _ai()._get_counter_punch_action(wel, "Britain", world)
        assert blow is not None and blow.get("target") == "Ney"

    def _range_board(self):
        world = _legacy()
        for m in world.marshals.values():
            if m.nation == "France":
                m.location = "Lyon"
        ney = world.marshals["Ney"]
        ney.strength, ney.retreated_this_turn = 30000, True
        world.marshals["Davout"].strength = 5000
        world.marshals["Grouchy"].location = "Bordeaux"
        world.marshals["Drouot"].location = "Bordeaux"
        uxb = world.marshals["Uxbridge"]
        uxb.location, uxb.strength, uxb.movement_range, uxb.fortified = "Belgium", 24000, 2, False
        wel = world.marshals["Wellington"]
        wel.location, wel.counter_punch_available = "Paris", False
        world.regions["Paris"].garrison_strength = 0
        _rebuild(world)
        ai = _ai()
        ai._marshal_visited_locations = {
            "Uxbridge": set(world.get_region("Belgium").adjacent_regions)}
        return world, uxb, ai

    def test_the_range_arm_prices_the_target_too(self):
        world, uxb, ai = self._range_board()
        with _quiet():
            act = ai._get_stagnation_action(uxb, "Britain", world, 3, "cautious")
        assert not (act and act.get("action") == "attack" and act.get("target") == "Ney"), act

    def test_the_range_arm_lever_off_strikes_the_retreated_man(self):
        ea.FIELD_PRICES_THE_TARGET_TOO = False
        world, uxb, ai = self._range_board()
        with _quiet():
            act = ai._get_stagnation_action(uxb, "Britain", world, 3, "cautious")
        assert act and act.get("action") == "attack" and act.get("target") == "Ney", act


# ═══════════════════════════════════════════════════════════════════════
# R1-2 — the ally-support strike is priced
# ═══════════════════════════════════════════════════════════════════════

class TestTheAllySupportStrikeIsPriced:

    def _board(self, davout=40000, second=None):
        world = _legacy()
        _british_soil(world)
        wel = world.marshals["Wellington"]
        wel.location, wel.strength, wel.fortified, wel.stance = "Waterloo", 30000, False, Stance.DEFENSIVE
        wel.personality = "cautious"
        world.ai_refortify_cooldown["Wellington"] = 2
        uxb = world.marshals["Uxbridge"]
        uxb.location, uxb.strength = "Netherlands", 8000
        dav = world.marshals["Davout"]
        dav.location, dav.strength = "Netherlands", davout
        if second:
            gro = world.marshals["Grouchy"]
            gro.location, gro.strength = "Netherlands", second
        _rebuild(world)
        return world, wel

    def _support(self, world, wel):
        random.seed(3)
        with _quiet():
            return _ai()._find_ally_support_opportunity(wel, "Britain", world)

    def test_a_cautious_corps_does_not_strike_to_join_at_bad_odds(self):
        world, wel = self._board()
        act = self._support(world, wel)
        assert not (act and act.get("action") == "attack"), act

    def test_the_lever_off_arm_reproduces_the_row(self):
        ea.ALLY_SUPPORT_PRICES_THE_FIELD = False
        world, wel = self._board()
        act = self._support(world, wel)
        assert act and act.get("action") == "attack" and act.get("target") == "Davout", act

    def test_the_field_is_priced_not_one_man(self):
        """Davout 40k with a 10k Grouchy beside him: the weakest is Grouchy,
        and one-man pricing (30k / 10k = 3.0) would strike into a 50k field."""
        world, wel = self._board(davout=40000, second=10000)
        act = self._support(world, wel)
        assert not (act and act.get("action") == "attack"), act

    def test_good_odds_still_strike(self):
        """The floor is a floor, not a ban: a 12k blocker is struck."""
        world, wel = self._board(davout=12000)
        act = self._support(world, wel)
        assert act and act.get("action") == "attack" and act.get("target") == "Davout", act

    def test_futility_brakes_the_strike(self):
        world, wel = self._board(davout=12000)
        world.ai_attack_futility["Wellington:Davout"] = ATTACK_FUTILITY_LIMIT
        act = self._support(world, wel)
        assert not (act and act.get("action") == "attack"), act

    def test_the_crossing_gate_brakes_the_strike(self):
        """The shipped board: a French corps at Normandy, a French ally at
        London with a 5,000-man Moore on him, the Channel SHUT for France at
        0.54. Priced alone the strike is a walkover; the executor would
        refuse it at the water and write a cooldown — the arm reads the
        gate the other attack rungs read."""
        from pathlib import Path
        from backend.game_logic.naval import crossing_allowed
        scenario = str(Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
                       / "assets" / "maps" / "europe_1805.json")
        with _quiet():
            world = WorldState.from_scenario(scenario)
        ney = world.get_marshal("Ney")
        ney.location, ney.strength, ney.personality = "Normandy", 24000, "aggressive"
        massena = world.get_marshal("Massena")
        massena.location = "London"
        moore = world.get_marshal("Moore")
        moore.location, moore.strength = "London", 5000
        _rebuild(world)
        assert not crossing_allowed(world, "France", "Normandy", "London")
        random.seed(3)
        with _quiet():
            act = _ai()._find_ally_support_opportunity(ney, "France", world)
        assert not (act and act.get("action") == "attack"), act
        # The isolation: the SAME strike, priced by the helper alone, is worth
        # it the moment the water is uncovered — so the water was the brake.
        ai = _ai()
        random.seed(3)
        with _quiet():
            barred = ai._ally_strike_is_worth_it(ney, "France", world, moore, [moore], massena)
        world.fleets["Britain"]["ships"] = 0
        random.seed(3)
        with _quiet():
            open_water = ai._ally_strike_is_worth_it(ney, "France", world, moore, [moore], massena)
        assert barred is False and open_water is True


# ═══════════════════════════════════════════════════════════════════════
# R1-3 — the admin recruit spares the square
# ═══════════════════════════════════════════════════════════════════════

class TestTheAdminRecruitSparesTheSquare:

    def _board(self):
        world = _legacy()
        _british_soil(world)
        wel = world.marshals["Wellington"]
        # 15,000 of 40,000: strictly under the 0.50 urgent threshold the
        # admin pick reads, so he is the recruit the phase would choose.
        wel.location, wel.strength, wel.square_formation, wel.ai_square_cooldown = "Belgium", 15000, True, 0
        wel.starting_strength = 40000
        world.marshals["Uxbridge"].location = "Hanover"
        world.marshals["Uxbridge"].starting_strength = world.marshals["Uxbridge"].strength
        ney = world.marshals["Ney"]
        ney.location, ney.strength = "Paris", 60000
        _rebuild(world)
        return world, wel

    def test_the_admin_pick_skips_a_squared_corps(self):
        world, wel = self._board()
        pick = _ai()._find_weakest_marshal_for_admin("Britain", world)
        assert pick is None or pick.name != "Wellington", pick

    def test_the_lever_off_pick_recruits_into_the_square(self):
        ea.ADMIN_RECRUIT_SPARES_THE_SQUARE = False
        world, wel = self._board()
        pick = _ai()._find_weakest_marshal_for_admin("Britain", world)
        assert pick is not None and pick.name == "Wellington"

    def _recruit(self, world):
        with _quiet():
            return CommandExecutor().execute(
                {"command": {"type": "specific", "marshal": "Wellington", "action": "recruit",
                             "target": None, "_autonomous_execution": True}}, {"world": world})

    def test_a_recruit_into_a_square_stamps_no_cooldown(self):
        world, wel = self._board()
        result = self._recruit(world)
        assert result.get("success") is True, result.get("message")
        assert wel.square_formation is False, "the square still breaks — that is not the defect"
        assert int(getattr(wel, "ai_square_cooldown", 0) or 0) == 0

    def test_the_lever_off_recruit_forbids_the_square_for_two_turns(self):
        ea.ADMIN_RECRUIT_SPARES_THE_SQUARE = False
        world, wel = self._board()
        self._recruit(world)
        assert int(getattr(wel, "ai_square_cooldown", 0) or 0) == 2


# ═══════════════════════════════════════════════════════════════════════
# R1-4 — stagnation reads the phase
# ═══════════════════════════════════════════════════════════════════════

class TestStagnationReadsThePhase:

    def _blucher(self):
        world = _legacy()
        _british_soil(world)
        blu = world.marshals["Blucher"]
        blu.location, blu.strength, blu.stance, blu.fortified = "Hanover", 40000, Stance.AGGRESSIVE, False
        world.marshals["Gneisenau"].location = "Berlin"
        for m in world.marshals.values():
            if m.nation == "Britain":
                m.location = "Netherlands"
        world.regions["Hanover"].controller = "Prussia"
        world.ai_stagnation_turns["Blucher"] = 3
        _rebuild(world)
        return world, blu

    def test_a_drilling_corps_is_not_forced(self):
        world, blu = self._blucher()
        blu.drilling = True
        with _quiet():
            act = _ai()._get_stagnation_action(blu, "Prussia", world, 3, "aggressive")
        assert act is None, act

    def test_a_corps_that_acted_this_phase_is_not_forced(self):
        world, blu = self._blucher()
        ai = _ai()
        ai._acted_this_phase = {"Blucher"}
        with _quiet():
            act = ai._get_stagnation_action(blu, "Prussia", world, 3, "aggressive")
        assert act is None, act

    def test_the_lever_off_arm_forces_the_drilling_corps(self):
        ea.STAGNATION_READS_THE_PHASE = False
        world, blu = self._blucher()
        blu.drilling = True
        with _quiet():
            act = _ai()._get_stagnation_action(blu, "Prussia", world, 3, "aggressive")
        assert act is not None and act.get("action") in ("move", "unfortify", "attack"), act

    def _phase(self, world):
        world.nation_actions["Prussia"] = 4
        ai = _ai()
        acts = []
        orig = EnemyAI._execute_action

        def spy(self_, action, game_state):
            acts.append(dict(action))
            return orig(self_, action, game_state)
        EnemyAI._execute_action = spy
        try:
            random.seed(5)
            with _quiet():
                ai.process_nation_turn("Prussia", world, {"world": world})
        finally:
            EnemyAI._execute_action = orig
        return ai, acts

    def test_the_drill_survives_the_phase(self):
        """The reviewer's end-to-end: idle three turns, Blucher drills (1 AP)
        and the stale counter used to force-march him out of it — "[!] DRILL
        CANCELLED", shock_bonus 0."""
        world, blu = self._blucher()
        ai, acts = self._phase(world)
        mine = [(a.get("action"), a.get("target")) for a in acts if a.get("marshal") == "Blucher"]
        assert ("drill", None) in mine or any(a == "drill" for a, _ in mine), mine
        assert blu.drilling is True, mine
        assert "Blucher" in ai._acted_this_phase

    def test_the_lever_off_phase_cancels_the_drill(self):
        ea.STAGNATION_READS_THE_PHASE = False
        world, blu = self._blucher()
        _ai_, acts = self._phase(world)
        mine = [a.get("action") for a in acts if a.get("marshal") == "Blucher"]
        assert "drill" in mine, mine
        assert blu.drilling is False, mine

    def test_a_square_is_meaningful_at_phase_end(self):
        """The phase-end tracker: a corps whose whole phase was `form_square`
        is not idle."""
        world = _legacy()
        _british_soil(world)
        wel = world.marshals["Wellington"]
        wel.location, wel.strength, wel.stance, wel.fortified = "Belgium", 20000, Stance.DEFENSIVE, False
        wel.personality, wel.ai_square_cooldown = "cautious", 0
        world.marshals["Uxbridge"].location = "Hanover"
        ney = world.marshals["Ney"]
        ney.location, ney.strength, ney.cavalry = "Paris", 60000, True
        world.ai_stagnation_turns["Wellington"] = 1
        world.ai_refortify_cooldown["Wellington"] = 3
        _rebuild(world)
        world.nation_actions["Britain"] = 3
        random.seed(4)
        with _quiet():
            results = _ai().process_nation_turn("Britain", world, {"world": world})
        mine = [(r.get("ai_action") or {}).get("action") for r in results
                if (r.get("ai_action") or {}).get("marshal") == "Wellington"]
        assert "form_square" in mine, mine
        assert world.ai_stagnation_turns.get("Wellington", 0) == 0

    def test_the_lever_off_arm_counts_the_square_as_idle(self):
        ea.STAGNATION_READS_THE_PHASE = False
        world = _legacy()
        _british_soil(world)
        wel = world.marshals["Wellington"]
        wel.location, wel.strength, wel.stance, wel.fortified = "Belgium", 20000, Stance.DEFENSIVE, False
        wel.personality, wel.ai_square_cooldown = "cautious", 0
        world.marshals["Uxbridge"].location = "Hanover"
        ney = world.marshals["Ney"]
        ney.location, ney.strength, ney.cavalry = "Paris", 60000, True
        world.ai_stagnation_turns["Wellington"] = 1
        world.ai_refortify_cooldown["Wellington"] = 3
        _rebuild(world)
        world.nation_actions["Britain"] = 3
        random.seed(4)
        with _quiet():
            results = _ai().process_nation_turn("Britain", world, {"world": world})
        mine = [(r.get("ai_action") or {}).get("action") for r in results
                if (r.get("ai_action") or {}).get("marshal") == "Wellington"]
        assert "form_square" in mine, mine
        assert world.ai_stagnation_turns.get("Wellington", 0) >= 2


# ═══════════════════════════════════════════════════════════════════════
# R1-5 — a drilling corps is left to drill
# ═══════════════════════════════════════════════════════════════════════

class TestADrillingCorpsIsLeftToDrill:

    def _board(self, stance=Stance.NEUTRAL):
        world = _legacy()
        _british_soil(world)
        wel = world.marshals["Wellington"]
        wel.location, wel.strength, wel.stance, wel.fortified = "Belgium", 20000, stance, False
        wel.personality, wel.drilling, wel.drilling_locked = "cautious", True, True
        ney = world.marshals["Ney"]
        ney.location, ney.strength = "Paris", 60000
        world.marshals["Uxbridge"].location = "Hanover"
        _rebuild(world)
        return world, wel

    def test_check_threats_returns_none_for_a_drilling_corps(self):
        world, wel = self._board()
        random.seed(1)
        with _quiet():
            assert _ai()._check_threats(wel, "Britain", world) is None

    def test_the_lever_off_arm_orders_the_refused_stance(self):
        ea.DRILLING_CORPS_IS_LEFT_TO_DRILL = False
        world, wel = self._board()
        random.seed(1)
        with _quiet():
            act = _ai()._check_threats(wel, "Britain", world)
        assert act and act.get("action") == "stance_change", act

    def test_the_tree_never_orders_a_drilling_corps_a_stance_or_a_fort(self):
        for stance in (Stance.NEUTRAL, Stance.DEFENSIVE):
            world, wel = self._board(stance)
            random.seed(1)
            with _quiet():
                act, _prio = _ai()._evaluate_marshal(wel, "Britain", world)
            assert not (act and act.get("action") in ("stance_change", "fortify", "move")), (stance, act)


# ═══════════════════════════════════════════════════════════════════════
# R1-6 — the counter-punch credits the capture (GR5)
# ═══════════════════════════════════════════════════════════════════════

class TestTheCounterPunchCreditsTheCapture:

    def _board(self):
        world = _legacy()
        _british_soil(world)
        wel = world.marshals["Wellington"]
        wel.location, wel.strength, wel.stance, wel.fortified = "Belgium", 20000, Stance.DEFENSIVE, False
        wel.counter_punch_available = True
        for m in world.marshals.values():
            if m.nation == "France":
                m.location = "Bordeaux"
        normandy = world.regions["Normandy"]
        normandy.controller, normandy.garrison_strength, normandy.garrison_detachment = "France", 0, False
        _rebuild(world)
        return world, wel

    def _capture(self, world):
        with _quiet():
            return CommandExecutor().execute(
                {"command": {"type": "specific", "marshal": "Wellington", "action": "attack",
                             "target": "Normandy", "_autonomous_execution": True}}, {"world": world})

    def test_an_undefended_capture_carries_the_free_action_credit(self):
        world, wel = self._board()
        result = self._capture(world)
        assert result.get("success") is True, result.get("message")
        assert world.regions["Normandy"].controller == "Britain"
        assert result.get("free_action") is True and result.get("counter_punch_used") is True
        assert wel.counter_punch_available is False

    def test_the_lever_off_arm_eats_the_blow(self):
        ce.COUNTER_PUNCH_CREDITS_THE_CAPTURE = False
        world, wel = self._board()
        result = self._capture(world)
        assert result.get("success") is True
        assert not result.get("free_action") and not result.get("counter_punch_used")
        assert wel.counter_punch_available is False

    def test_the_occupation_exit_carries_the_credit_too(self, monkeypatch):
        world, wel = self._board()
        monkeypatch.setattr(
            ce.CombatExecutor, "_attempt_region_capture",
            lambda self, marshal, region, w, gs, had_garrison=False: {
                "occupation_started": True, "message": "occupation begins",
                "turns_required": 2})
        result = self._capture(world)
        assert result.get("occupation_started") is True, result
        assert result.get("free_action") is True and result.get("counter_punch_used") is True


# ═══════════════════════════════════════════════════════════════════════
# R1-7 — cavalry is not parked
# ═══════════════════════════════════════════════════════════════════════

class TestCavalryIsNotParkedAgain:
    """The tell is the stance: a cautious corps is never AGGRESSIVE by its
    own choice, so AGGRESSIVE horse under the limit means the limit forced
    it out of DEFENSIVE at turn start — and the rungs that used to buy the
    stance straight back (2 AP, then forced again) stand down. A horse that
    has never parked may still park once, as the player's may; an outright
    ban was measured to move the passive board from France 2 to 19 provinces
    and was not taken."""

    def _board(self, no_field=False, stance=Stance.AGGRESSIVE):
        """`no_field`: the war stands but no French corps is in the field, so
        nothing above P8 fires and the cautious DEFAULT is what answers."""
        world = _legacy()
        _british_soil(world)
        uxb = world.marshals["Uxbridge"]
        uxb.location, uxb.strength, uxb.stance, uxb.fortified = "Belgium", 20000, stance, False
        uxb.personality, uxb.cavalry, uxb.drilling = "cautious", True, False
        world.marshals["Wellington"].location = "Hanover"
        ney = world.marshals["Ney"]
        ney.location, ney.strength = "Paris", 60000
        if no_field:
            for m in world.marshals.values():
                if m.nation == "France":
                    m.strength = 0
        _rebuild(world)
        return world, uxb

    def test_the_threat_rung_does_not_buy_the_stance_back(self):
        world, uxb = self._board()
        random.seed(1)
        with _quiet():
            act = _ai()._check_threats(uxb, "Britain", world)
        assert not (act and act.get("action") in ("stance_change", "fortify")), act

    def test_the_lever_off_arm_buys_the_stance_the_limit_just_forced_out(self):
        ea.CAVALRY_AI_READS_THE_LIMIT = False
        world, uxb = self._board()
        random.seed(1)
        with _quiet():
            act = _ai()._check_threats(uxb, "Britain", world)
        assert act and act.get("action") == "stance_change" and act.get("target") == "defensive", act

    def test_a_never_parked_horse_may_still_park_once(self):
        world, uxb = self._board(stance=Stance.NEUTRAL)
        random.seed(1)
        with _quiet():
            act = _ai()._check_threats(uxb, "Britain", world)
        assert act and act.get("action") == "stance_change" and act.get("target") == "defensive", act

    def _default(self, world, uxb):
        """Reach P8: the frontier-fortify rung (P5) is guarded by the same
        tell, and the garrison-placement rung (priority 7) would otherwise
        answer first on an empty field — it is marked spent for the phase."""
        ai = _ai()
        ai._garrison_placed_this_turn = True
        random.seed(1)
        with _quiet():
            act, prio = ai._evaluate_marshal(uxb, "Britain", world)
        return act, prio

    def test_the_cautious_default_does_not_park_it_again(self):
        world, uxb = self._board(no_field=True)
        act, _prio = self._default(world, uxb)
        assert not (act and act.get("action") in ("stance_change", "fortify")), act
        assert act and act.get("action") == "wait", act

    def test_the_default_lever_off_arm_parks_it_again(self):
        ea.CAVALRY_AI_READS_THE_LIMIT = False
        world, uxb = self._board(no_field=True)
        act, _prio = self._default(world, uxb)
        assert act and act.get("action") in ("stance_change", "fortify"), act

    def test_infantry_is_still_parked(self):
        """The rule is about horses: a cautious infantry corps forced
        aggressive by some other road still takes the defensive stance."""
        world, uxb = self._board()
        uxb.cavalry = False
        random.seed(1)
        with _quiet():
            act = _ai()._check_threats(uxb, "Britain", world)
        assert act and act.get("action") == "stance_change", act

    def test_a_forced_unfortify_leaves_the_ai_a_refortify_memory(self):
        """The fort half: the limit's own unfortify wrote no AI memory, so the
        cautious default dug the horse in again the next turn (1 AP, then
        -3 trust the AI never reads, again). It writes the AI's refortify
        cooldown now; the player's horse is untouched."""
        world, uxb = self._board(stance=Stance.DEFENSIVE)
        uxb.fortified, uxb.turns_fortified, uxb.defense_bonus = True, 3, 0.12
        with _quiet():
            events = world._check_cavalry_limits()
        assert any(e.get("type") == "cavalry_fortify_forced" and e.get("marshal") == "Uxbridge"
                   for e in events), events
        assert uxb.fortified is False
        assert world.ai_refortify_cooldown.get("Uxbridge", 0) >= 3

    def test_the_memory_is_the_ai_s_alone(self):
        world, uxb = self._board(stance=Stance.DEFENSIVE)
        murat = world.marshals["Ney"]
        murat.location, murat.cavalry, murat.stance = "Paris", True, Stance.DEFENSIVE
        murat.fortified, murat.turns_fortified, murat.defense_bonus = True, 3, 0.12
        with _quiet():
            world._check_cavalry_limits()
        assert murat.fortified is False
        assert world.ai_refortify_cooldown.get("Ney", 0) == 0


# ═══════════════════════════════════════════════════════════════════════
# R1-8 — a fortified corps never marches (GR5)
# ═══════════════════════════════════════════════════════════════════════

class TestAFortifiedCorpsNeverMarches:

    def _board(self):
        world = _legacy()
        for m in world.marshals.values():
            if m.nation == "Britain":
                m.location = "Hanover"
        dav = world.marshals["Davout"]
        dav.location, dav.fortified, dav.defense_bonus, dav.turns_fortified = "Paris", True, 0.12, 3
        _rebuild(world)
        world.nation_actions["France"] = 6
        return world, dav

    def _move(self, world):
        with _quiet():
            return CommandExecutor().execute(
                {"command": {"type": "specific", "marshal": "Davout", "action": "move",
                             "target": "Lyon", "_autonomous_execution": True}}, {"world": world})

    def test_an_autonomous_move_of_a_fortified_corps_is_refused(self):
        world, dav = self._board()
        result = self._move(world)
        assert result.get("success") is False and result.get("fortified") is True, result
        assert dav.location == "Paris" and dav.fortified is True

    def test_the_lever_off_arm_walks_off_with_the_fortification(self):
        mv.FORTIFIED_CORPS_NEVER_MARCHES = False
        world, dav = self._board()
        result = self._move(world)
        assert result.get("success") is True, result.get("message")
        assert dav.location == "Lyon" and dav.fortified is True

    def _supply_board(self, monkeypatch, fortified=True, drilling=False):
        world = _legacy()
        _british_soil(world)
        wel = world.marshals["Wellington"]
        wel.location, wel.strength, wel.stance = "Belgium", 20000, Stance.DEFENSIVE
        wel.fortified, wel.personality = fortified, "cautious"
        wel.drilling = drilling
        world.marshals["Uxbridge"].location = "Hanover"
        for m in world.marshals.values():
            if m.nation == "France":
                m.location = "Bordeaux"
        _rebuild(world)
        monkeypatch.setattr(WorldState, "get_effective_supply_cap",
                            lambda self, nation, region: 1000 if region.name == "Belgium" else 60000)
        # The fortification-opportunity rung (P3.5) sits above P6.5 and would
        # answer a fortified corps first; held out so the SUPPLY rung is what
        # answers on both arms.
        monkeypatch.setattr(EnemyAI, "_check_fortification_opportunity",
                            lambda self, marshal, nation, world: None)
        world.ai_stagnation_turns["Wellington"] = 0
        return world, wel

    def test_the_supply_rung_does_not_march_a_fortified_corps(self, monkeypatch):
        world, wel = self._supply_board(monkeypatch)
        random.seed(2)
        with _quiet():
            act, _prio = _ai()._evaluate_marshal(wel, "Britain", world)
        assert not (act and act.get("action") == "move"), act

    def test_the_supply_rung_lever_off_marches_it(self, monkeypatch):
        mv.FORTIFIED_CORPS_NEVER_MARCHES = False
        world, wel = self._supply_board(monkeypatch)
        random.seed(2)
        with _quiet():
            act, _prio = _ai()._evaluate_marshal(wel, "Britain", world)
        assert act and act.get("action") == "move", act

    def test_the_supply_rung_does_not_march_a_drilling_corps(self, monkeypatch):
        world, wel = self._supply_board(monkeypatch, fortified=False, drilling=True)
        random.seed(2)
        with _quiet():
            act, _prio = _ai()._evaluate_marshal(wel, "Britain", world)
        assert not (act and act.get("action") == "move"), act

    def test_the_road_home_walker_leaves_his_works_first(self, monkeypatch):
        from backend.game_logic import withdrawal
        world, dav = self._board()
        monkeypatch.setattr(withdrawal, "is_road_home_order", lambda order: True)
        monkeypatch.setattr(withdrawal, "next_step_home", lambda w, m: "Lyon")
        random.seed(2)
        with _quiet():
            act, _prio = _ai()._evaluate_marshal(dav, "France", world)
        assert act and act.get("action") == "unfortify", act
        mv.FORTIFIED_CORPS_NEVER_MARCHES = False
        random.seed(2)
        with _quiet():
            act, _prio = _ai()._evaluate_marshal(dav, "France", world)
        assert act and act.get("action") == "move" and act.get("target") == "Lyon", act


# ═══════════════════════════════════════════════════════════════════════
# R1-11 — the latch is redundant under the shipped lever, by construction
# ═══════════════════════════════════════════════════════════════════════

class TestAFormedSquareEndsThePhase:

    def test_a_formed_square_marks_the_corps_done(self):
        world = _legacy()
        _british_soil(world)
        wel = world.marshals["Wellington"]
        wel.location, wel.strength, wel.stance, wel.fortified = "Belgium", 20000, Stance.DEFENSIVE, False
        wel.personality, wel.ai_square_cooldown = "cautious", 0
        world.marshals["Uxbridge"].location = "Hanover"
        ney = world.marshals["Ney"]
        ney.location, ney.strength, ney.cavalry = "Paris", 60000, True
        world.ai_refortify_cooldown["Wellington"] = 3
        _rebuild(world)
        world.nation_actions["Britain"] = 3
        ai = _ai()
        random.seed(4)
        with _quiet():
            results = ai.process_nation_turn("Britain", world, {"world": world})
        mine = [(r.get("ai_action") or {}).get("action") for r in results
                if (r.get("ai_action") or {}).get("marshal") == "Wellington"]
        assert mine and mine[-1] == "form_square", mine
        assert "Wellington" in ai._marshals_done_this_turn
        assert "Wellington" in ai._squares_formed_this_turn
