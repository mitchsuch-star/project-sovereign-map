"""WIN-D3 "The Road Home" — the evacuation corridor and its free march orders.

Build contract: `docs/WAR_WITHDRAWAL_SPEC.md`; gate record §7a.
Measured defect: `docs/audits/PLAYTEST_WIN_CAMPAIGN_2026_08_16.md` §5.3.

The spec's §3.4 lists five things the corridor must never become. They are
written here as FALSIFIABLE TESTS rather than comments, which is the whole
point of that section: a permission arm bolted onto the single movement
chokepoint is exactly the kind of change that quietly grows into an
open-borders treaty nobody voted for.

Several tests carry a CONTROL ARM that disables `WITHDRAWAL_ACTIVE` and
asserts the old behaviour still reproduces. Without them a test like "the
corps is not stranded" could pass for reasons having nothing to do with this
slice — the 1805 board is large and most marshals can get home most of the
time.
"""

from __future__ import annotations

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic import withdrawal as W
from backend.game_logic.diplomacy import (
    can_enter_territory, cleanup_war_end, set_diplomatic_state,
)
from backend.models.world_state import WorldState

SCENARIO = ("godot-client/project-sovereign/assets/maps/europe_1805.json")


@pytest.fixture(scope="module")
def base_world():
    return WorldState.from_scenario(SCENARIO)


@pytest.fixture
def world(base_world):
    return WorldState.from_dict(base_world.to_dict())


def _stage_measured_shape(world, marshal_name="Davout"):
    """The exact shape PLAYTEST_WIN_CAMPAIGN §5.3 measured.

    A French corps stands on soil France has CAPTURED — its own colour on the
    map, so it occupies nothing it has no right to — enclosed on every side by
    the newly-sovereign Russian frontier. **Volhynia** is the province that
    makes this exact: its four neighbours (White Russia, Lithuania, Ukraine,
    Vilna) are all Russian, so the peace shuts every road out of it at once.

    This is deliberately NOT the shape §4.1 describes ("standing on soil he
    now has no right to occupy"). The spec's own predicate would have missed
    the defect that produced the spec; see `withdrawal.py`, correction 1. The
    §4.1 shape is covered separately, in `test_playtest_2026_03.py`.

    France stays AT WAR with Austria — its boot state, and the campaign's:
    that is what makes the road home genuinely exist once the corridor opens
    (out through Russia, then across Austrian soil war already lets him
    cross). Without it the corps is not stranded but cut off, which is a
    different row of §5 and is tested as one.
    """
    world.regions["Volhynia"].controller = "France"
    for m in list(world.marshals.values()):
        if m.nation == "France" and m.name != marshal_name:
            m.location = "Paris"
        elif m.nation == "Russia":
            # Single-subject fixture: park the other signatory's army at
            # home, so a surviving corridor can only ever be about OUR corps.
            # (The mutual case has its own test, and it is a real one — a
            # grant stays open while EITHER side still has a man on the road.)
            m.location = world.get_nation_capital("Russia")
    marshal = world.marshals[marshal_name]
    marshal.location = "Volhynia"
    set_diplomatic_state(world, "France", "Russia", "WAR")
    return marshal


def _make_peace(world):
    return set_diplomatic_state(world, "France", "Russia", "PEACE")


# ══════════════════════════════════════════════════════════════════════════
# THE MEASURED DEFECT
# ══════════════════════════════════════════════════════════════════════════

class TestTheMeasuredDefect:

    def test_control_arm_reproduces_the_stranding(self, world, monkeypatch):
        """With the slice disabled, the played campaign's failure recurs.

        If this ever stops failing, the fixture has drifted and every
        assertion in the class below is passing vacuously.
        """
        monkeypatch.setattr(W, "WITHDRAWAL_ACTIVE", False)
        davout = _stage_measured_shape(world)
        _make_peace(world)

        assert not can_enter_territory(world, "France", "Russia")
        assert world.evacuation_grants == {}
        assert davout.strategic_order is None
        home = W.get_home_zone(world, "France")
        assert davout.location not in home, "he is cut off from his own realm"

    def test_the_peace_grants_the_road(self, world):
        davout = _stage_measured_shape(world)
        _make_peace(world)

        assert can_enter_territory(world, "France", "Russia"), (
            "the corridor must open the frontier the peace just closed")
        assert "France|Russia" in world.evacuation_grants
        assert W.is_road_home_order(davout.strategic_order)
        assert davout.strategic_order.command_type == "MOVE_TO"

    def test_the_order_carries_a_real_path_home(self, world):
        davout = _stage_measured_shape(world)
        _make_peace(world)

        order = davout.strategic_order
        home = W.get_home_zone(world, "France")
        assert order.target in home
        assert order.path and order.path[0] == davout.location
        assert order.path[-1] == order.target
        # Every hop is legally enterable now — the road is walkable, not
        # merely drawn.
        for hop in order.path[1:]:
            controller = world.regions[hop].controller
            assert (not controller or controller == "France"
                    or can_enter_territory(world, "France", controller))

    def test_the_duration_covers_the_march(self, world):
        davout = _stage_measured_shape(world)
        _make_peace(world)

        home = W.get_home_zone(world, "France")
        distance = W.distance_home(world, davout, home)
        expiry = world.evacuation_grants["France|Russia"]
        assert distance is not None and distance > 0
        assert expiry - world.current_turn >= distance, (
            "a grant too short to walk is not a corridor")


# ══════════════════════════════════════════════════════════════════════════
# §3.4 — WHAT THE CORRIDOR IS NOT (the five never-do pins)
# ══════════════════════════════════════════════════════════════════════════

class TestNeverDoPins:

    def test_it_never_permits_an_attack(self, world, monkeypatch):
        """Pin 1. Attacking requires WAR; the pair is at peace.

        Asserted as an IDENTITY between two arms rather than as a particular
        refusal string: whatever the objection machinery does with the order,
        it must do exactly the same thing whether or not a corridor stands.
        The first draft of this test passed vacuously — it used the wrong
        command envelope, so the executor answered "Marshal 'None' not found"
        and `not success` was true for a reason having nothing to do with the
        corridor.
        """
        def arm(active: bool):
            w = WorldState.from_dict(world.to_dict())
            monkeypatch.setattr(W, "WITHDRAWAL_ACTIVE", active)
            _stage_measured_shape(w)          # Davout stranded at Volhynia
            kutuzov = w.marshals["Kutuzov"]
            kutuzov.location = "Ukraine"      # adjacent to Volhynia
            kutuzov.strength = 40000
            _make_peace(w)
            assert can_enter_territory(w, "France", "Russia") is active, (
                "precondition: the arm really does what it says")
            assert not w.is_at_war("France", "Russia")
            CommandExecutor().execute(
                {"command": {"action": "attack", "marshal": "Davout",
                             "target": "Kutuzov"}},
                {"world": w})
            return kutuzov.strength, len(w.battles_this_turn)

        with_corridor = arm(True)
        without = arm(False)
        assert with_corridor == (40000, 0), (
            "safe passage is not a licence to fight — no blood was allowed "
            f"to be drawn, got {with_corridor}")
        assert with_corridor == without, (
            "the corridor must not change attack behaviour in any direction")

    def test_it_never_permits_a_capture(self, world, monkeypatch):
        """Pin 2. Marching through a province must not flip it.

        The control arm is what makes this real: with the corridor disabled
        the very same march is REFUSED, so the successful march below happened
        because of the corridor and nothing else.
        """
        def arm(active: bool):
            w = WorldState.from_dict(world.to_dict())
            monkeypatch.setattr(W, "WITHDRAWAL_ACTIVE", active)
            davout = _stage_measured_shape(w)   # stranded at Volhynia
            target = "Ukraine"                  # Russian, and his way out
            w.regions[target].controller = "Russia"
            w.regions[target].garrison_strength = 0
            for m in list(w.marshals.values()):
                if m.location == target:
                    m.location = "Vilna"
            _make_peace(w)
            assert target in w.regions["Volhynia"].adjacent_regions
            result = CommandExecutor().execute(
                {"command": {"action": "move", "marshal": "Davout",
                             "target": target}},
                {"world": w})
            return (bool(result.get("success")), davout.location,
                    w.regions[target].controller)

        assert arm(False) == (False, "Volhynia", "Russia"), (
            "control: without the corridor the frontier is shut")

        succeeded, where, controller = arm(True)
        assert succeeded and where == "Ukraine", (
            "precondition: the corridor really did carry him across")
        assert controller == "Russia", (
            "the corridor is a right of transit, not of conquest")

    def test_it_is_not_open_borders(self, world):
        """Pin 3. It expires, and it exists only because a war just ended."""
        _stage_measured_shape(world)
        _make_peace(world)

        assert world.get_diplomatic_state("France", "Russia") == "PEACE"
        expiry = world.evacuation_grants["France|Russia"]
        assert isinstance(expiry, int)

        # Walk past the expiry with nobody left to evacuate: the frontier
        # shuts again by itself.
        for m in list(world.marshals.values()):
            if m.nation == "France":
                m.location = "Paris"
        world.current_turn = expiry + 1
        W.process_evacuation_grants(world)
        assert "France|Russia" not in world.evacuation_grants
        assert not can_enter_territory(world, "France", "Russia")

    def test_it_dies_the_instant_war_resumes(self, world):
        """Pin 4. A peace instrument cannot outlive the peace."""
        _stage_measured_shape(world)
        _make_peace(world)
        assert can_enter_territory(world, "France", "Russia")

        set_diplomatic_state(world, "France", "Russia", "WAR")
        assert "France|Russia" not in world.evacuation_grants
        # (Entry is True again only because WAR itself permits it.)
        set_diplomatic_state(world, "France", "Russia", "PEACE")
        set_diplomatic_state(world, "France", "Russia", "WAR")
        world.diplomatic_states["France|Russia"] = "PEACE"
        assert not can_enter_territory(world, "France", "Russia"), (
            "the revoked grant must not linger behind a state flip")

    def test_it_does_not_feed_the_army(self, world, monkeypatch):
        """Pin 5. The corridor is a road, not a billet.

        Falsifiable by construction: the SAME over-capacity stack on the SAME
        foreign soil is attrited identically with the corridor open and with
        the slice disabled. If the corridor ever started counting as friendly
        supply, these two numbers would diverge.
        """
        def strength_after(active: bool) -> int:
            w = WorldState.from_dict(world.to_dict())
            monkeypatch.setattr(W, "WITHDRAWAL_ACTIVE", active)
            davout = _stage_measured_shape(w)
            region = w.regions[davout.location]
            region.controller = "Russia"          # plainly foreign soil
            davout.strength = 90000               # far over any capacity
            _make_peace(w)
            w.process_supply_attrition()
            return davout.strength

        with_corridor = strength_after(True)
        without = strength_after(False)
        assert with_corridor < 90000, "precondition: attrition really bites"
        assert with_corridor == without, (
            "safe passage must not feed the army")


# ══════════════════════════════════════════════════════════════════════════
# §3.5 — the self-refreshing corridor
# ══════════════════════════════════════════════════════════════════════════

class TestSelfRefreshingCorridor:

    def _march_home(self, world, marshal):
        """Walk him along his own road, one province a turn."""
        seen = []
        for step in list(marshal.strategic_order.path[1:]):
            world.current_turn += 1
            marshal.location = step
            seen.append(W.process_evacuation_grants(world))
        return seen

    def test_a_marching_corps_is_never_warned_and_never_interned(self, world):
        davout = _stage_measured_shape(world)
        _make_peace(world)
        rounds = self._march_home(world, davout)

        mine = [e for turn in rounds for e in turn
                if e.get("marshal") == "Davout"]
        assert mine == [], f"a corps that is walking home must be left alone: {mine}"
        assert "Davout" in world.marshals

    def test_arriving_home_retires_the_corridor(self, world):
        davout = _stage_measured_shape(world)
        _make_peace(world)
        self._march_home(world, davout)

        assert davout.location in W.get_home_zone(world, "France")
        assert "France|Russia" not in world.evacuation_grants, (
            "the corridor closes because it is finished, not because it "
            "timed out")

    def test_standing_still_earns_three_warnings_then_internment(self, world):
        """§6's promise, counted."""
        davout = _stage_measured_shape(world)
        _make_peace(world)

        warnings, interned = [], False
        for _ in range(12):
            world.current_turn += 1
            for e in W.process_evacuation_grants(world):
                if e.get("marshal") != "Davout":
                    continue
                if e["type"] == "evacuation_lapsing":
                    warnings.append(e["turns_left"])
                elif e["type"] == "marshal_interned":
                    interned = True
            if interned:
                break

        assert interned, "loitering must cost something, or the corridor is decorative"
        assert warnings == [2, 1, 0], (
            f"three explicit warnings, counting down: got {warnings}")
        assert "Davout" not in world.marshals
        assert "Davout" in world.fallen_marshals, (
            "internment goes through the PC15-1 removal seam, tombstone and all")

    def test_a_second_unrelated_corridor_cannot_shorten_his_road(self, world):
        """Regression: found by measurement during the build.

        France held two corridors at once (Austria's, signed earlier and
        shorter; Russia's, signed now). Judging every stranded marshal against
        every grant interned Davout mid-march under the Austrian clock, which
        had nothing to do with his route.
        """
        davout = _stage_measured_shape(world)
        _make_peace(world)
        # An earlier, SHORTER corridor from some other peace France signed.
        # Written directly: what is under test is how the tick JUDGES a
        # marshal against the grants standing, not how they were opened.
        world.evacuation_grants["France|Prussia"] = world.current_turn + 2
        assert (world.evacuation_grants["France|Prussia"]
                < world.evacuation_grants["France|Russia"])

        for step in list(davout.strategic_order.path[1:]):
            world.current_turn += 1
            davout.location = step
            W.process_evacuation_grants(world)

        assert "Davout" in world.marshals, (
            "the shorter unrelated corridor must not intern a corps that is "
            "marching home inside the longer one")

    def test_a_broken_corps_is_given_grace_not_interned(self, world):
        davout = _stage_measured_shape(world)
        _make_peace(world)
        davout.retreat_recovery = 2
        expiry_before = world.evacuation_grants["France|Russia"]

        for _ in range(6):
            world.current_turn += 1
            W.process_evacuation_grants(world)

        assert "Davout" in world.marshals, (
            "a corps reforming after a rout is not loitering")
        assert world.evacuation_grants["France|Russia"] > expiry_before


# ══════════════════════════════════════════════════════════════════════════
# §4 — the free march orders
# ══════════════════════════════════════════════════════════════════════════

class TestFreeMarchOrders:

    def test_the_order_costs_the_player_nothing(self, world):
        _stage_measured_shape(world)
        before = world.actions_remaining
        _make_peace(world)
        assert world.actions_remaining == before, (
            "it is not the player's order, it is the treaty's")

    def test_the_order_is_ordinary_and_overridable(self, world):
        davout = _stage_measured_shape(world)
        _make_peace(world)
        assert W.is_road_home_order(davout.strategic_order)

        # The player says otherwise; nothing about the corridor resists him.
        davout.strategic_order = None
        assert davout.strategic_order is None
        W.process_evacuation_grants(world)  # must not crash or re-fight him

    def test_a_standing_player_order_is_not_overruled(self, world):
        from backend.models.marshal import StrategicOrder

        davout = _stage_measured_shape(world)
        davout.strategic_order = StrategicOrder(
            command_type="HOLD", target="Ukraine", target_type="region",
            started_turn=1, original_command="Davout, hold position")
        _make_peace(world)

        assert davout.strategic_order.command_type == "HOLD", (
            "the treaty offers a road; it does not overrule the Emperor")

    def test_the_ai_actually_walks_the_road(self, world):
        """GR5, at the only seam where it is real.

        The free march order is a `strategic_order`, and `enemy_ai.py` had
        never read that field for anything — `StrategicOrderProcessor` is the
        PLAYER's. So the AI was handed a road it could not see and would then
        be interned for not walking it: measured at THREE AI corps destroyed
        in a 40-turn ambient run before rung P1.2 was added, one of them a
        single march from its own border.

        Asserted against the AI's own evaluator rather than a whole enemy
        phase, so a failure names the rung instead of the turn.
        """
        from backend.ai.enemy_ai import EnemyAI

        kutuzov = world.marshals["Kutuzov"]
        set_diplomatic_state(world, "France", "Russia", "WAR")
        world.regions["Moravia"].controller = "France"
        kutuzov.location = "Moravia"
        kutuzov.retreat_recovery = 0
        set_diplomatic_state(world, "France", "Russia", "PEACE")

        assert W.is_road_home_order(kutuzov.strategic_order), (
            "precondition: the ex-enemy was handed the road")
        step = W.next_step_home(world, kutuzov)
        assert step, "precondition: there is a next province to walk to"

        action, priority = EnemyAI(CommandExecutor())._evaluate_marshal(
            kutuzov, "Russia", world)
        assert action is not None
        assert action["action"] == "move" and action["target"] == step, (
            f"the AI must take the treaty's road, got {action}")

    def test_symmetry_the_ex_enemy_gets_the_same_road(self, world):
        """GR5. Not a player courtesy — it is what ending a war means."""
        kutuzov = world.marshals["Kutuzov"]
        set_diplomatic_state(world, "France", "Russia", "WAR")
        world.regions["Moravia"].controller = "France"
        kutuzov.location = "Moravia"
        set_diplomatic_state(world, "France", "Russia", "PEACE")

        assert W.is_road_home_order(kutuzov.strategic_order), (
            "the enemy's corps on our soil gets the corridor too")
        assert can_enter_territory(world, "Russia", "France")

    def test_a_marshal_already_home_is_untouched(self, world):
        """§5 row 1: no order, no mention."""
        ney = world.marshals["Ney"]
        ney.location = "Paris"
        set_diplomatic_state(world, "France", "Russia", "WAR")
        set_diplomatic_state(world, "France", "Russia", "PEACE")
        assert ney.strategic_order is None

    def test_a_marshal_on_allied_soil_is_untouched(self, world):
        """§5 row 1's other half — "or ON PASSABLE SOIL".

        Found by the acceptance playtest, not by this suite: an earlier cut
        of `is_stranded` tested only "is he outside the home zone", and the
        home zone is the nation's OWN provinces. Every corps standing
        perfectly legally on an ally's ground was swept up — the run had
        **the Emperor himself, at Munich in allied Bavaria, told to march
        home or be interned.** He is abroad; he is not stranded.
        """
        ney = world.marshals["Ney"]
        ney.location = "Franconia"
        assert world.regions["Franconia"].controller == "Bavaria"
        assert world.get_diplomatic_state("France", "Bavaria") == "ALLIANCE"

        _stage_measured_shape(world, marshal_name="Davout")
        ney.location = "Franconia"          # the stage parks the others home
        _make_peace(world)

        assert W.is_road_home_order(world.marshals["Davout"].strategic_order), (
            "precondition: a corridor really did open this turn")
        assert ney.strategic_order is None, (
            "a corps on an ally's soil needs no treaty to get home")

        warned = []
        for _ in range(10):
            world.current_turn += 1
            warned += [e for e in W.process_evacuation_grants(world)
                       if e.get("marshal") == "Ney"]
        assert warned == [], f"and it is never put on a clock: {warned}"
        assert "Ney" in world.marshals


# ══════════════════════════════════════════════════════════════════════════
# §5 — the cut-off corps (gate Q4: refuse honestly)
# ══════════════════════════════════════════════════════════════════════════

class TestCutOffCorps:

    def _strand_beyond_rescue(self, world):
        """A corps on an island of soil with no land route home at all."""
        set_diplomatic_state(world, "France", "Austria", "PEACE")
        for m in list(world.marshals.values()):
            if m.nation == "France":
                m.location = "Paris"
        davout = world.marshals["Davout"]
        davout.location = "Ionian Islands"
        set_diplomatic_state(world, "France", "Russia", "WAR")
        return davout

    def test_no_order_is_invented_for_a_corps_with_no_road(self, world):
        davout = self._strand_beyond_rescue(world)
        _make_peace(world)

        home = W.get_home_zone(world, "France")
        if W.distance_home(world, davout, home) is not None:
            pytest.skip("fixture drift: this province is reachable by land")
        assert davout.strategic_order is None, (
            "v1 does not invent a rescue (gate Q4)")

    def test_the_dispatch_says_so_plainly(self, world):
        davout = self._strand_beyond_rescue(world)
        _make_peace(world)
        home = W.get_home_zone(world, "France")
        if W.distance_home(world, davout, home) is not None:
            pytest.skip("fixture drift: this province is reachable by land")

        granted = [e for e in world.event_log
                   if e["type"] == "evacuation_granted"]
        assert granted, "the peace must still say something"
        assert "Davout" in (granted[-1].get("cut_off") or [])
        assert "cut off" in granted[-1]["message"]

    def test_the_corridor_still_expires_over_a_corps_it_cannot_help(self, world):
        """The other way a grant ends.

        Found by mutation sweep: every earlier test retired its corridor by
        bringing the army home, so the "the clock simply ran out" branch had
        no coverage at all and could be deleted with the suite green.

        Reaching it needs a MIXED peace — someone who can walk (so a corridor
        is opened at all; an all-cut-off peace grants nothing, which is right)
        and someone who cannot. Once the walkers are resolved the cut-off man
        keeps the grant standing, because he is still stranded; it then ends
        on the clock rather than on his arrival.
        """
        davout = _stage_measured_shape(world)            # can walk home
        massena = world.marshals["Massena"]
        massena.location = "Ionian Islands"              # cannot
        _make_peace(world)

        home = W.get_home_zone(world, "France")
        if W.distance_home(world, massena, home) is not None:
            pytest.skip("fixture drift: this province is reachable by land")
        expiry = world.evacuation_grants["France|Russia"]

        # Davout dawdles and is eventually interned; Massena simply cannot go.
        while world.current_turn < expiry and "Davout" in world.marshals:
            world.current_turn += 1
            W.process_evacuation_grants(world)

        assert "France|Russia" in world.evacuation_grants, (
            "a corridor with a stranded man left on it does not close early")
        assert "Massena" in world.marshals

        world.current_turn = expiry + 1
        W.process_evacuation_grants(world)
        assert "France|Russia" not in world.evacuation_grants
        assert not can_enter_territory(world, "France", "Russia")

    def test_a_cut_off_corps_is_never_interned(self, world):
        davout = self._strand_beyond_rescue(world)
        _make_peace(world)
        home = W.get_home_zone(world, "France")
        if W.distance_home(world, davout, home) is not None:
            pytest.skip("fixture drift: this province is reachable by land")

        for _ in range(15):
            world.current_turn += 1
            W.process_evacuation_grants(world)
        assert "Davout" in world.marshals, (
            "refusing to invent a rescue must not become punishing a corps "
            "for failing to walk a road that does not exist")


# ══════════════════════════════════════════════════════════════════════════
# §3.1 — the chokepoint, and the endings cleanup_war_end never sees
# ══════════════════════════════════════════════════════════════════════════

class TestGrantChokepoint:

    def test_armistice_grants_the_corridor(self, world):
        """§5: an armistice strands an army exactly as a peace does, and the
        forced-alliance ARMISTICE arm is PT-J1's second road that never
        reaches `cleanup_war_end`."""
        davout = _stage_measured_shape(world)
        set_diplomatic_state(world, "France", "Russia", "ARMISTICE")
        assert "France|Russia" in world.evacuation_grants
        assert W.is_road_home_order(davout.strategic_order)

    def test_vassalization_needs_no_corridor_because_it_opens_the_border(
            self, world):
        """PT-J1's first missed road, and the honest answer for it.

        Typed conquest-vassalization never reaches `cleanup_war_end`, which
        is why the grant is written at `set_diplomatic_state` instead. But
        VASSAL and ALLIANCE are themselves open-movement states: the corps is
        not stranded, because the frontier it would need is already open. No
        corridor is issued, and none is needed — what matters, and what is
        asserted here, is that the army can get home.
        """
        davout = _stage_measured_shape(world)
        for terminal in ("VASSAL", "ALLIANCE"):
            w = WorldState.from_dict(world.to_dict())
            set_diplomatic_state(w, "France", "Russia", terminal)
            marshal = w.marshals[davout.name]
            assert can_enter_territory(w, "France", "Russia"), terminal
            assert not W.is_stranded(
                w, marshal, W.get_home_zone(w, "France")), terminal
            assert w.evacuation_grants == {}, (
                f"{terminal} needs no corridor — it already opens the border")


class TestTeleportRetired:

    def test_cleanup_war_end_relocates_nobody(self, world):
        davout = _stage_measured_shape(world)
        davout.location = "Podolia"
        world.regions["Podolia"].controller = "Russia"
        world.diplomatic_states["France|Russia"] = "PEACE"
        cleanup_war_end(world, "France|Russia")
        assert davout.location == "Podolia"

    def test_the_teleport_is_gone_from_the_module(self):
        from backend.game_logic import diplomacy
        assert not hasattr(diplomacy, "_force_retreat_displaced_marshals"), (
            "retired, not disabled — a dead teleport is a GR9 placeholder")


# ══════════════════════════════════════════════════════════════════════════
# State
# ══════════════════════════════════════════════════════════════════════════

class TestWhatThePlayerReads:
    """§4.3 — the surfaces, end to end through `build_morning_dispatch`.

    Every defect in this class was found by driving the game, not by reading
    the code, which is why they are pinned here rather than trusted.
    """

    def _arc(self, world, names=("Davout", "Soult")):
        from backend.game_logic.dispatch import build_morning_dispatch
        world.regions["Volhynia"].controller = "France"
        for m in list(world.marshals.values()):
            if m.nation == "France" and m.name not in names:
                m.location = "Paris"
            elif m.nation == "Russia":
                m.location = world.get_nation_capital("Russia")
        for n in names:
            world.marshals[n].location = "Volhynia"
        set_diplomatic_state(world, "France", "Russia", "WAR")
        set_diplomatic_state(world, "France", "Russia", "PEACE")
        out = []
        for _ in range(6):
            world.current_turn += 1
            W.process_evacuation_grants(world)
            head = build_morning_dispatch(world).get("headline")
            out.append(head["text"] if head else "")
        return out

    def test_the_peace_beat_names_names_and_the_deadline(self, world):
        from backend.game_logic.dispatch import build_morning_dispatch
        _stage_measured_shape(world)
        _make_peace(world)
        head = build_morning_dispatch(world)["headline"]
        assert head["class"] == "road_home"
        assert "Davout" in head["text"] and "safe passage" in head["text"]
        assert "1 corps stands" in head["text"], (
            "the count is the PLAYER's corps, and it agrees with its verb")

    def test_every_lapsing_corps_is_named_once(self, world):
        """Two defects at once, both found by the acceptance run.

        The dispatch shows ONE headline, so per-marshal beats meant only the
        luckiest corps was ever warned — a marshal was interned having never
        appeared in a briefing. And because the event window is two turns
        wide, the first aggregate read "Davout, Soult, Davout and Soult".
        """
        texts = self._arc(world)
        warnings = [t for t in texts if "no nearer home" in t]
        assert warnings, "precondition: the lapse warnings fired"
        for text in warnings:
            assert "Davout" in text and "Soult" in text, (
                f"both corps must be named: {text!r}")
            assert text.count("Davout") == 1 and text.count("Soult") == 1, (
                f"and each exactly once: {text!r}")

    def test_the_warning_does_not_claim_he_stood_still(self, world):
        """Nothing here tracks movement — it tracks whether he can still get
        home in the time left. The first copy said "has not moved from
        Lithuania" about a corps that had marched all turn."""
        texts = self._arc(world)
        assert any("no nearer home" in t for t in texts)
        assert not any("has not moved" in t for t in texts)

    def test_internment_is_not_reported_as_annihilation(self, world):
        """An interned corps was disarmed, not destroyed, and the briefing
        must not say otherwise."""
        texts = self._arc(world)
        interned = [t for t in texts if "interned at" in t]
        assert interned, f"precondition: someone was interned: {texts}"
        for text in interned:
            assert "DESTROYED" not in text
            assert "disarmed" in text

    def test_the_captor_is_never_his_own_emperor(self, world):
        """The measured case interns a corps inside its own cut-off enclave,
        where the ground underfoot is FRANCE — and the first cut read the
        controller unconditionally: "interned at Volhynia by France"."""
        texts = self._arc(world, names=("Davout",))
        interned = [t for t in texts if "interned at" in t]
        assert interned
        assert "by Russia" in interned[0], interned[0]
        assert "by France" not in interned[0]


class TestWinD5EmperorStartsForward:
    """WIN-D5 — the Emperor boots on the Rhine, not at the Tuileries.

    Shipped alongside WIN-D3 as the second half of "The Road Home"
    (WAR_WITHDRAWAL_SPEC §9). Authoring only: no mechanism changes, and the
    Seat's +1 DP is simply not active at boot — a place he returns to rather
    than a bonus he abandons on turn 2.
    """

    def test_he_boots_at_lorraine(self, base_world):
        assert base_world.marshals["Napoleon"].location == "Lorraine"

    def test_he_is_one_march_from_the_opening_battle(self, base_world):
        """§9.1 reason 1 — the whole point of moving him."""
        assert base_world.marshals["Mack"].location == "Swabia"
        assert base_world.get_distance("Lorraine", "Swabia") == 1
        assert base_world.get_distance("Paris", "Swabia") == 5, (
            "the measured cost of the old start, kept as the contrast")

    def test_his_guard_stands_with_its_parent_corps(self, base_world):
        """§9.1 reason 3 — the carve reads as a detachment, not a
        subtraction performed at long distance."""
        assert base_world.marshals["Soult"].location == "Lorraine"

    def test_the_biography_no_longer_says_the_tuileries(self, base_world):
        bio = base_world.marshals["Napoleon"].biography or ""
        assert "Tuileries" not in bio
        assert "Rhine" in bio

    def test_the_carve_is_untouched(self, base_world):
        """The economy pins ride these two numbers; moving a man must not
        move them."""
        assert base_world.marshals["Napoleon"].strength == 10000
        assert base_world.marshals["Soult"].strength == 30000
        total = sum(m.strength for m in base_world.marshals.values()
                    if m.nation == "France")
        assert total == 189000, "France's national total is unchanged"

    def test_the_seat_is_not_active_at_boot(self, base_world):
        """§9.2's honest cost, pinned rather than asserted in prose."""
        capital = base_world.get_nation_capital("France")
        assert capital == "Paris"
        assert base_world.marshals["Napoleon"].location != capital


class TestSerialization:

    def test_the_grant_survives_a_save_load(self, world):
        _stage_measured_shape(world)
        _make_peace(world)
        expiry = world.evacuation_grants["France|Russia"]

        reloaded = WorldState.from_dict(world.to_dict())
        assert reloaded.evacuation_grants["France|Russia"] == expiry
        assert can_enter_territory(reloaded, "France", "Russia")

    def test_a_pre_slice_save_loads_with_an_empty_store(self, world):
        data = world.to_dict()
        data.pop("evacuation_grants", None)
        reloaded = WorldState.from_dict(data)
        assert reloaded.evacuation_grants == {}

    def test_only_one_new_field(self, world):
        """The slice's whole state footprint, pinned."""
        before = set(WorldState.from_dict(world.to_dict()).to_dict())
        assert "evacuation_grants" in before
        # The marshal-side record is the order's own words, not a new field.
        from backend.models.marshal import StrategicOrder
        order = StrategicOrder(command_type="MOVE_TO", target="Paris",
                               target_type="region", started_turn=1,
                               original_command=W.ROAD_HOME_COMMAND)
        assert "evacuation" not in order.to_dict()
        assert W.is_road_home_order(order)
