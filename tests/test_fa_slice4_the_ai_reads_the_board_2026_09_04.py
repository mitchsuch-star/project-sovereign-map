"""Final Whole-Game Audit — slice 4, "The AI Reads the Board".

Nine rows, one through-line: an enemy-AI rung computed a decision from a
board it had not actually read — the garrison but not the army standing
over it (FA-8), the square before the strikes that break it (FA-27/N38),
the acting corps' own `broken` flag (FA-N6), one man instead of the field
and no floor at all for the free blow (FA-N7), the crossing gate every
other attack rung reads (FA-N80), the player's horses but not its own
(FA-N54), an assault that was never an attack (FA-N59), an ALLY standing
beside the friend it meant to support (FA-R1), and a fortification the
executor refuses a drill over (FA-R2). Every row was reproduced before a
line was written (`docs/audits/fa_build_2026_09_04/REPRO_B_*.md`, and the
slice-2 review round's probes for FA-R1/FA-R2), and every fix sits behind
its own lever so the ambient-series re-record is attributed row by row.
"""

import contextlib
import io
import random

import pytest

import backend.ai.enemy_ai as enemy_mod
import backend.models.world_state as world_mod
from backend.ai.enemy_ai import EnemyAI
from backend.commands.combat_executor import CombatExecutor
from backend.commands.executor import CommandExecutor
from backend.models.marshal import Stance
from backend.models.world_state import WorldState
from tests.test_fa_slice2_no_word_came_2026_09_04 import _war


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _legacy():
    """The 19-region fixture world, France vs Britain at war, the French
    roster moved to Bordeaux so Paris holds its garrison alone."""
    world = WorldState(player_nation="France")
    _war(world, "France", "Britain")
    for m in world.marshals.values():
        if m.nation == "France":
            m.location = "Bordeaux"
    world.invalidate_active_nations_cache()
    world._build_marshal_index()
    return world


def _ai():
    return EnemyAI(CommandExecutor())


# ═══════════════════════════════════════════════════════════════════════
# FA-8 — the garrison rung sees the field army
# ═══════════════════════════════════════════════════════════════════════

class TestTheGarrisonRungSeesTheFieldArmy:

    def _wellington_at_belgium(self):
        world = _legacy()
        wel = world.marshals["Wellington"]
        wel.location = "Belgium"
        wel.strength = 100000
        world._build_marshal_index()
        return world, wel

    def test_a_garrison_alone_is_assaulted(self):
        world, wel = self._wellington_at_belgium()
        with _quiet():
            action = _ai()._find_garrison_attack(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack", "target": "Paris"}

    def test_a_garrison_with_a_field_army_is_p4s_business(self):
        """The row's shape: 101,000 Frenchmen stood in Munich and the rung
        priced the 10,000 garrison as a walkover — the executor then fought
        the field battle the order actually is."""
        world, wel = self._wellington_at_belgium()
        for name in ("Davout", "Ney"):
            world.marshals[name].location = "Paris"
            world.marshals[name].strength = 50000
        world._build_marshal_index()
        world.calculate_visibility()
        with _quiet():
            action = _ai()._find_garrison_attack(wel, "Britain", world)
        assert action is None, action

    def test_the_lever_down_prices_the_garrison_alone(self, monkeypatch):
        monkeypatch.setattr(enemy_mod, "P425_SKIPS_A_HELD_FIELD", False)
        world, wel = self._wellington_at_belgium()
        world.marshals["Davout"].location = "Paris"
        world.marshals["Davout"].strength = 50000
        world._build_marshal_index()
        world.calculate_visibility()
        with _quiet():
            action = _ai()._find_garrison_attack(wel, "Britain", world)
        assert action and action["target"] == "Paris", "the defect, reproduced"

    def test_the_range_arm_prices_the_field(self):
        """FA-8's rider: the stagnation breaker's range arm read ONE man.
        A cavalry corps two hops from a 5,000-man stub standing in a
        95,000-man field must not charge it."""
        world = _legacy()
        uxb = world.marshals["Uxbridge"]
        assert getattr(uxb, "cavalry", False)
        uxb.location = "Belgium"
        uxb.strength = 24000
        uxb.movement_range = 2
        uxb.fortified = False
        for m in world.marshals.values():
            if m.nation == "France":
                m.location = "Lyon"          # two hops: Belgium -> Paris -> Lyon
                m.strength = 30000           # 24k/30k = 0.8 — only the stub tempts
        world.marshals["Ney"].strength = 5000
        world.regions["Paris"].garrison_strength = 0
        # The contacts list is fog-aware: Wellington stands at Paris so
        # Britain can SEE Lyon (Paris is adjacent to both Belgium and Lyon).
        world.marshals["Wellington"].location = "Paris"
        world._build_marshal_index()
        world.calculate_visibility()
        ai = _ai()
        ai._marshal_visited_locations = {
            "Uxbridge": set(world.get_region("Belgium").adjacent_regions)}
        with _quiet():
            action = ai._get_stagnation_action(uxb, "Britain", world, 3, "cautious")
        assert not (action and action.get("action") == "attack"), action
        with _quiet(), pytest.MonkeyPatch.context() as mp:
            mp.setattr(enemy_mod, "P425_SKIPS_A_HELD_FIELD", False)
            ai2 = _ai()
            ai2._marshal_visited_locations = {
                "Uxbridge": set(world.get_region("Belgium").adjacent_regions)}
            down = ai2._get_stagnation_action(uxb, "Britain", world, 3, "cautious")
        assert down == {"marshal": "Uxbridge", "action": "attack", "target": "Ney"}, \
            "the pre-slice range arm charged the 5,000-man stub in a 95,000-man field"


# ═══════════════════════════════════════════════════════════════════════
# FA-27 / FA-N38 — the square is the last word of a phase
# ═══════════════════════════════════════════════════════════════════════

class TestTheSquareIsTheLastWord:

    def _cavalry_shape(self):
        """Wellington (infantry, neutral stance) at Belgium; Ney's cavalry
        adjacent at Paris, too strong to strike; nothing to capture."""
        world = _legacy()
        wel = world.marshals["Wellington"]
        wel.location = "Belgium"
        wel.strength = 20000
        wel.stance = Stance.NEUTRAL
        wel.fortified = False
        ney = world.marshals["Ney"]
        assert getattr(ney, "cavalry", False), "the shape needs real cavalry"
        ney.location = "Paris"
        ney.strength = 60000
        # The rest of the French stay at Bordeaux (not adjacent to Belgium):
        # Drouot's ARTILLERY beside the cavalry would veto the square by rule.
        for region in world.regions.values():
            if region.controller == "France" and region.name != "Paris":
                region.controller = "Britain"   # nothing undefended to capture
        world.invalidate_active_nations_cache()
        world._build_marshal_index()
        world.calculate_visibility()
        return world, wel

    def _with_a_stub(self):
        """The cavalry shape plus a 4,000-man French stub alone at Normandy
        (adjacent to Belgium): P4 prices THAT field at 5:1 — a strike."""
        world, wel = self._cavalry_shape()
        davout = world.marshals["Davout"]
        davout.location = "Normandy"
        davout.strength = 4000
        world._build_marshal_index()
        world.calculate_visibility()
        return world, wel

    def test_p3s_posture_yields_and_the_square_forms(self):
        world, wel = self._cavalry_shape()
        with _quiet():
            action, prio = _ai()._evaluate_marshal(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "form_square"}, action
        assert prio == 2

    def test_a_strike_outranks_the_square(self):
        world, wel = self._with_a_stub()
        with _quiet():
            action, _prio = _ai()._evaluate_marshal(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack", "target": "Davout"}, action

    def test_a_fortified_corps_keeps_its_works(self):
        world, wel = self._cavalry_shape()
        wel.fortified = True
        wel.stance = Stance.DEFENSIVE
        with _quiet():
            action, _prio = _ai()._evaluate_marshal(wel, "Britain", world)
        assert not (action and action.get("action") == "form_square"), action

    def test_a_formed_square_ends_the_corps_phase(self):
        """Isolation pin (the first sweep found the sequence assertion
        inert — on this shape the latch and the in-square stance guard
        already leave him nothing to do): the EXECUTION seam marks him
        done, so a strike that appears later in the phase cannot reach
        him."""
        world, wel = self._cavalry_shape()
        world.nation_actions["Britain"] = 4
        random.seed(3)
        ai = _ai()
        with _quiet():
            results = ai.process_nation_turn("Britain", world, {"world": world})
        seq = [(r.get("ai_action") or {}).get("action") for r in results
               if (r.get("ai_action") or {}).get("marshal") == "Wellington"]
        assert "form_square" in seq, seq
        assert seq.index("form_square") == len(seq) - 1, seq
        assert "Wellington" in ai._marshals_done_this_turn, "he stands in square — done for the phase"

    def test_a_square_broken_by_his_own_action_takes_the_cooldown(self):
        world = _legacy()
        wel = world.marshals["Wellington"]
        wel.square_formation = True
        wel.ai_square_cooldown = 0
        CommandExecutor()._tactical._auto_break_square(wel, "attack")
        assert wel.square_formation is False
        assert wel.ai_square_cooldown == 2

    def test_the_lever_down_forms_first_and_sets_no_cooldown(self, monkeypatch):
        monkeypatch.setattr(enemy_mod, "SQUARE_FORMS_AFTER_THE_STRIKES", False)
        world, wel = self._with_a_stub()
        with _quiet():
            action, _prio = _ai()._evaluate_marshal(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "form_square"}, \
            "the pre-slice order: the square before the strike that breaks it"
        wel.square_formation = True
        wel.ai_square_cooldown = 0
        CommandExecutor()._tactical._auto_break_square(wel, "attack")
        assert wel.ai_square_cooldown == 0


# ═══════════════════════════════════════════════════════════════════════
# FA-N6 — a broken corps takes the limiter
# ═══════════════════════════════════════════════════════════════════════

class TestABrokenCorpsTakesTheLimiter:

    def _broken_on_french_soil(self):
        world = _legacy()
        wel = world.marshals["Wellington"]
        wel.location = "Belgium"
        wel.strength = 1000
        wel.broken = True
        wel.stance = Stance.DEFENSIVE
        world.regions["Belgium"].controller = "France"
        world.regions["Belgium"].garrison_strength = 0
        world.invalidate_active_nations_cache()
        world._build_marshal_index()
        world.calculate_visibility()
        return world, wel

    def test_no_capture_from_a_broken_corps(self):
        world, wel = self._broken_on_french_soil()
        with _quiet():
            action, _prio = _ai()._evaluate_marshal(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "wait"}, action

    def test_no_stored_intent_from_a_broken_corps(self):
        world, wel = self._broken_on_french_soil()
        ai = _ai()
        ai._pending_intents["Wellington"] = {"intent": "capture", "target": "Belgium"}
        with _quiet():
            action, _prio = ai._evaluate_marshal(wel, "Britain", world)
        assert not (action and action.get("action") == "attack"), action

    def test_a_whole_corps_still_captures(self):
        world, wel = self._broken_on_french_soil()
        wel.broken = False
        wel.strength = 20000
        with _quiet():
            action, _prio = _ai()._evaluate_marshal(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack", "target": "Belgium"}, action

    def test_the_lever_down_lets_the_broken_corps_capture(self, monkeypatch):
        monkeypatch.setattr(enemy_mod, "BROKEN_AI_CORPS_IS_LIMITED", False)
        world, wel = self._broken_on_french_soil()
        with _quiet():
            action, _prio = _ai()._evaluate_marshal(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack", "target": "Belgium"}, \
            "the defect: a broken 1,000-man corps took the province"


# ═══════════════════════════════════════════════════════════════════════
# FA-N7 — the counter-punch prices the field, under a floor
# ═══════════════════════════════════════════════════════════════════════

class TestTheCounterPunchIsPriced:

    def _armed(self, field):
        """Wellington (cautious, 20k) at Belgium with a banked counter-punch;
        `field` = the French strengths standing at Paris."""
        world = _legacy()
        wel = world.marshals["Wellington"]
        wel.location = "Belgium"
        wel.strength = 20000
        wel.stance = Stance.DEFENSIVE
        wel.fortified = False
        wel.counter_punch_available = True
        names = ["Ney", "Davout"]
        for name, strength in zip(names, field):
            world.marshals[name].location = "Paris"
            world.marshals[name].strength = strength
        world._build_marshal_index()
        world.calculate_visibility()
        assert wel.has_counter_punch()
        return world, wel

    def test_a_suicidal_free_blow_is_declined(self):
        world, wel = self._armed([60000])
        with _quiet():
            action = _ai()._get_counter_punch_action(wel, "Britain", world)
        assert action is None, action

    def test_the_field_is_priced_not_the_man(self):
        """Two 12,000-man corps: one-man 1.67 clears any mood-jittered
        floor a cautious marshal can draw; the 24,000 field (0.83) does not."""
        world, wel = self._armed([12000, 12000])
        with _quiet():
            action = _ai()._get_counter_punch_action(wel, "Britain", world)
        assert action is None, "one-man 1.67 hid a 0.83 field"

    def test_a_real_opportunity_still_strikes(self):
        world, wel = self._armed([5000])
        with _quiet():
            action = _ai()._get_counter_punch_action(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack", "target": "Ney"}, action

    def test_the_lever_down_counter_punches_the_giant(self, monkeypatch):
        monkeypatch.setattr(enemy_mod, "COUNTER_PUNCH_PRICES_THE_FIELD", False)
        world, wel = self._armed([60000])
        with _quiet():
            action = _ai()._get_counter_punch_action(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack", "target": "Ney"}

    def test_the_threshold_is_drawn_only_when_a_target_exists(self):
        """RNG discipline: no adjacent enemy, no `random.uniform` draw."""
        world = _legacy()
        wel = world.marshals["Wellington"]
        wel.location = "Netherlands"
        wel.counter_punch_available = True
        wel.fortified = False
        world._build_marshal_index()
        world.calculate_visibility()
        random.seed(11)
        before = random.random()
        random.seed(11)
        with _quiet():
            _ai()._get_counter_punch_action(wel, "Britain", world)
        assert random.random() == before, "the stream moved with no target in reach"


# ═══════════════════════════════════════════════════════════════════════
# FA-N80 — the stagnation breaker reads the crossing gate
# ═══════════════════════════════════════════════════════════════════════

class TestTheStagnationBreakerReadsTheCrossing:

    @pytest.fixture
    def channel(self):
        from pathlib import Path
        scenario = (Path(__file__).resolve().parents[1] / "godot-client"
                    / "project-sovereign" / "assets" / "maps" / "europe_1805.json")
        with _quiet():
            world = WorldState.from_scenario(str(scenario))
        cast = world.get_marshal("Castanos")
        moore = world.get_marshal("Moore")
        cast.location = "Normandy"
        cast.fortified = False
        moore.location = "London"
        moore.strength = 20000
        assert world.is_at_war("Spain", "Britain")
        world.invalidate_active_nations_cache()
        world._build_marshal_index()
        world.calculate_visibility()
        from backend.game_logic.naval import crossing_allowed
        assert crossing_allowed(world, "Spain", "Normandy", "London") is False
        return world, cast

    def _boxed(self, world, name):
        ai = _ai()
        ai._marshal_visited_locations = {
            name: set(world.get_region(world.get_marshal(name).location).adjacent_regions)}
        return ai

    def test_the_surrounded_arm_never_orders_an_attack_across_barred_water(self, channel):
        world, cast = channel
        ai = self._boxed(world, "Castanos")
        with _quiet():
            action = ai._get_stagnation_action(cast, "Spain", world, 3, "cautious")
        assert not (action and action.get("action") == "attack"
                    and action.get("target") == "Moore"), action

    def test_the_lever_down_orders_the_refused_attack(self, channel, monkeypatch):
        monkeypatch.setattr(enemy_mod, "STAGNATION_READS_THE_CROSSING", False)
        world, cast = channel
        ai = self._boxed(world, "Castanos")
        with _quiet():
            action = ai._get_stagnation_action(cast, "Spain", world, 3, "cautious")
        assert action == {"marshal": "Castanos", "action": "attack", "target": "Moore"}, \
            "the defect: the breaker ordered the attack the executor refuses"

    def test_a_land_neighbour_is_still_struck(self):
        world = _legacy()
        wel = world.marshals["Wellington"]
        wel.location = "Belgium"
        wel.strength = 30000
        wel.fortified = False
        world.marshals["Ney"].location = "Paris"
        world.marshals["Ney"].strength = 5000
        world._build_marshal_index()
        world.calculate_visibility()
        ai = self._boxed(world, "Wellington")
        with _quiet():
            action = ai._get_stagnation_action(wel, "Britain", world, 3, "cautious")
        assert action == {"marshal": "Wellington", "action": "attack", "target": "Ney"}, action


# ═══════════════════════════════════════════════════════════════════════
# FA-N54 — the cavalry limits for every nation
# ═══════════════════════════════════════════════════════════════════════

class TestTheHorseObeysBothSides:

    def _restless(self):
        world = _legacy()
        uxb = world.marshals["Uxbridge"]
        assert getattr(uxb, "cavalry", False)
        uxb.stance = Stance.DEFENSIVE
        uxb.turns_in_defensive_stance = 3
        trust = uxb.trust.value
        return world, uxb, trust

    def test_an_ai_cavalry_corps_is_forced_out_of_its_defensive_stance(self):
        world, uxb, trust = self._restless()
        events = world._check_cavalry_limits()
        assert any(e.get("marshal") == "Uxbridge" and e.get("type") == "cavalry_stance_forced"
                   for e in events), events
        assert uxb.stance == Stance.AGGRESSIVE
        assert uxb.trust.value == trust - 3

    def test_no_redemption_is_raised_for_the_ai(self):
        world, uxb, _trust = self._restless()
        events = world._check_cavalry_limits()
        assert not any(e.get("type") == "redemption_event" for e in events)

    def test_the_lever_down_spares_the_ai(self, monkeypatch):
        monkeypatch.setattr(world_mod, "CAVALRY_LIMITS_ALL_NATIONS", False)
        world, uxb, trust = self._restless()
        events = world._check_cavalry_limits()
        assert not [e for e in events if e.get("marshal") == "Uxbridge"]
        assert uxb.stance == Stance.DEFENSIVE and uxb.trust.value == trust


# ═══════════════════════════════════════════════════════════════════════
# FA-N59 — the garrison assault counts as an attack
# ═══════════════════════════════════════════════════════════════════════

class TestTheGarrisonAssaultCounts:

    def _assault(self):
        world = _legacy()
        wel = world.marshals["Wellington"]
        wel.location = "Belgium"
        wel.strength = 40000
        world.regions["Paris"].garrison_strength = 15000
        world._build_marshal_index()
        combat = CommandExecutor()._combat
        with _quiet():
            combat._resolve_garrison_combat(wel, world.regions["Paris"], world, {"world": world})
        return wel

    def test_the_assault_writes_the_counters(self):
        wel = self._assault()
        assert wel.attacks_this_turn == 1
        assert wel.in_combat_this_turn is True

    def test_the_lever_down_leaves_them_untouched(self, monkeypatch):
        monkeypatch.setattr(CombatExecutor, "GARRISON_ASSAULT_COUNTS", False)
        wel = self._assault()
        assert wel.attacks_this_turn == 0
        assert wel.in_combat_this_turn is False


# ═══════════════════════════════════════════════════════════════════════
# FA-R1 — the ally-support strike picks an enemy
# ═══════════════════════════════════════════════════════════════════════

class TestAllySupportNeverStrikesAnAlly:

    def _shape(self):
        """Uxbridge (Britain) at Netherlands is threatened by Ney's 40k at
        Belgium; Blucher's Prussians — Britain's ALLIES — stand with him.
        Wellington at Waterloo (adjacent to Netherlands) comes to help."""
        world = _legacy()
        world.diplomatic_states["Britain|Prussia"] = "ALLIANCE"
        world.invalidate_active_nations_cache()
        wel = world.marshals["Wellington"]
        wel.location = "Waterloo"
        wel.strength = 30000
        wel.fortified = False
        uxb = world.marshals["Uxbridge"]
        uxb.location = "Netherlands"
        uxb.strength = 8000
        ney = world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 40000
        blucher = world.marshals["Blucher"]       # the fixture's own Prussian
        blucher.location = "Netherlands"
        blucher.strength = 6000
        world.marshals["Gneisenau"].location = "Berlin"
        world._build_marshal_index()
        world.calculate_visibility()
        assert not world.is_at_war("Britain", "Prussia")
        assert "Netherlands" in world.get_region("Waterloo").adjacent_regions
        assert "Netherlands" in world.get_region("Belgium").adjacent_regions
        return world, wel

    def test_the_support_move_never_attacks_the_ally(self):
        world, wel = self._shape()
        with _quiet():
            action = _ai()._find_ally_support_opportunity(wel, "Britain", world)
        assert action is not None, "the ally is threatened and adjacent — a support action is due"
        assert not (action.get("action") == "attack" and action.get("target") == "Blucher"), action

    def test_an_enemy_standing_with_the_ally_is_still_struck(self):
        world, wel = self._shape()
        world.marshals["Blucher"].nation = "France"
        world._build_marshal_index()
        world.calculate_visibility()
        with _quiet():
            action = _ai()._find_ally_support_opportunity(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack", "target": "Blucher"}, action

    def test_the_lever_down_attacks_the_ally(self, monkeypatch):
        monkeypatch.setattr(enemy_mod, "ALLY_SUPPORT_FIGHTS_ONLY_ENEMIES", False)
        world, wel = self._shape()
        with _quiet():
            action = _ai()._find_ally_support_opportunity(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack", "target": "Blucher"}, \
            "the defect: 'attacking Blucher to support Uxbridge' — Blucher is our ally"


# ═══════════════════════════════════════════════════════════════════════
# FA-R2 — no drill order to a fortified corps
# ═══════════════════════════════════════════════════════════════════════

class TestNoDrillOrderToAFortifiedCorps:

    def _idle(self, fortified):
        world = _legacy()
        wel = world.marshals["Wellington"]
        wel.location = "Netherlands"
        wel.fortified = fortified
        wel.drilling = False
        wel.shock_bonus = 0
        world._build_marshal_index()
        world.calculate_visibility()
        return world, wel

    def test_a_fortified_corps_is_not_ordered_to_drill(self):
        world, wel = self._idle(True)
        with _quiet():
            assert _ai()._consider_drill(wel, world) is None

    def test_an_unfortified_corps_still_drills(self):
        world, wel = self._idle(False)
        with _quiet():
            assert _ai()._consider_drill(wel, world) == {"marshal": "Wellington", "action": "drill"}

    def test_the_executor_refuses_what_the_rung_used_to_order(self):
        world, wel = self._idle(True)
        with _quiet():
            result = CommandExecutor().execute(
                {"command": {"marshal": "Wellington", "action": "drill",
                             "_autonomous_execution": True}}, {"world": world})
        assert result["success"] is False and "fortified" in result["message"].lower()

    def test_the_lever_down_orders_the_refused_drill(self, monkeypatch):
        monkeypatch.setattr(enemy_mod, "DRILL_RUNG_READS_FORTIFIED", False)
        world, wel = self._idle(True)
        with _quiet():
            assert _ai()._consider_drill(wel, world) == {"marshal": "Wellington", "action": "drill"}


class TestTheLeversShip:

    def test_all_nine_are_up(self):
        assert enemy_mod.P425_SKIPS_A_HELD_FIELD is True
        assert enemy_mod.SQUARE_FORMS_AFTER_THE_STRIKES is True
        assert enemy_mod.BROKEN_AI_CORPS_IS_LIMITED is True
        assert enemy_mod.COUNTER_PUNCH_PRICES_THE_FIELD is True
        assert enemy_mod.STAGNATION_READS_THE_CROSSING is True
        assert world_mod.CAVALRY_LIMITS_ALL_NATIONS is True
        assert CombatExecutor.GARRISON_ASSAULT_COUNTS is True
        assert enemy_mod.ALLY_SUPPORT_FIGHTS_ONLY_ENEMIES is True
        assert enemy_mod.DRILL_RUNG_READS_FORTIFIED is True
