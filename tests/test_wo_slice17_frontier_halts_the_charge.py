"""Row WO, slice 17 - "The Frontier Halts the Charge" (WO-24/25/28/31).

Landing record: docs/WEIRD_OUTCOMES_SPEC.md section 3 slice 17.

Four rows in the autonomous layer, every one re-reproduced on the current
tree before a line was written (the legacy fixture board: Ney at Belgium,
Rhineland is PRUSSIA's soil, Netherlands is BRITAIN's, France at war with
Britain):

  WO-24  Ney's glorious charge out of Belgium against a British corps
         standing on Rhineland, France and Prussia at PEACE, ended with Ney
         STANDING IN RHINELAND - capture correctly refused by PT-F1, the
         standing itself illegal. The reckless auto-charge (world_state's
         own copy) did the same with no check at all, while its auto-MOVE
         arm consults the movement law.
  WO-25  a jealousy-autonomous attack on a reckless-3 cavalryman returned
         the CHARGE/RESTRAIN popup; answering "charge" re-entered the
         charge with the provenance gone and staged `war_purpose_selection`
         - a HARD STOP the player never asked for.
  WO-28  a REFUSED autonomous attack was narrated as fought: the standing
         order voided, `order_voided_by_battle` + `jealousy_autonomous_attack`
         + the campaign-log row all written, no battle anywhere.
  WO-31  a HOLD sally that "returns to hold position" flipped Netherlands
         to France with Ney still at Belgium, AND mounted the plunder /
         secure question for a province he never entered.

DECIDED at build (WO-31, the rules call the spec left open): a province is
taken by the army that STANDS on it. The artillery arm at the same seam
already says so, the charge path already gates its capture on standing,
and the alternative would let a fortified holder strip every adjacent
province in turn without leaving his works.

METHOD NOTE (slice 9/10): where this slice protects a code path the test
drives the real executor and observes state; source scans are censuses
only and go through `_code_only` so a comment naming the fix cannot
satisfy them. Every test names the mutation that kills it.
"""

import ast
import contextlib
import io
import re
import tokenize
from pathlib import Path

import pytest

from backend.commands import combat_executor as CE
from backend.commands.executor import CommandExecutor
from backend.commands.strategic import (
    ORDER_BOUND_INTERRUPT_TYPES,
    StrategicOrderProcessor,
)
from backend.game_logic import dispatch as D
from backend.game_logic import jealousy as J
from backend.models import world_state as WS
from backend.models.marshal import StrategicOrder
from tests.conftest import MarshalFactory, WorldFactory

REPO = Path(__file__).resolve().parents[1]
COMBAT_PY = REPO / "backend" / "commands" / "combat_executor.py"

_DOCSTRING_HEADS = ('"""', "'''", 'r"""')


def _code_only(text: str) -> str:
    """`text` with comments and docstrings removed (the slice-10 idiom)."""
    out = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                continue
            if (tok.type == tokenize.STRING
                    and tok.line.strip().startswith(_DOCSTRING_HEADS)):
                continue
            out.append(tok.string)
    except (tokenize.TokenError, IndentationError):
        return text
    return chr(10).join(out)


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def _pair(world, a, b, state):
    key = world._make_diplo_key(a, b)
    world.diplomatic_states[key] = state
    if state == "WAR":
        world.war_start_turns[key] = world.current_turn


def _executor():
    return _quiet(CommandExecutor)


AUTONOMOUS = {"_strategic_execution": True, "_jealousy_autonomous": True}


def _attack_cmd(marshal, target, **flags):
    return {"command": {"marshal": marshal, "action": "attack",
                        "target": target, **flags}}


def _charge_world(reck, enemy_loc="Rhineland", host_state="PEACE",
                  cavalry=True):
    """Ney at Belgium facing a weak British corps at `enemy_loc`.
    Rhineland is Prussia's (the legacy fixture); `host_state` is the
    France|Prussia state. Netherlands is Britain's own war soil."""
    if cavalry:
        ney = MarshalFactory.cavalry(name="Ney", location="Belgium",
                                     strength=40000, personality="aggressive")
    else:
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=40000, personality="aggressive")
    ney.recklessness = reck
    wel = MarshalFactory.enemy(name="Wellington", location=enemy_loc,
                               nation="Britain", strength=2000)
    wel.morale = 26   # one exchange breaks him - the field is CLEARED
    world = WorldFactory.with_marshals([ney, wel])
    _pair(world, "France", "Britain", "WAR")
    _pair(world, "France", "Prussia", host_state)
    return world, ney, wel


# ══════════════════════════════════════════════════════════════════
# 1. WO-24 - the frontier halts the charge (both implementations)
# ══════════════════════════════════════════════════════════════════

class TestWO24TheGloriousChargeHaltsAtTheFrontier:

    def test_the_charge_halts_at_a_peaceful_courts_frontier(self):
        """Killed by deleting the neutral-arm halt in
        `_execute_glorious_charge` (or freezing `CHARGE_FRONTIER_HALT_ACTIVE`
        at import time)."""
        world, ney, _ = _charge_world(2)
        ex = _executor()
        res = _quiet(ex._combat._execute_glorious_charge, ney, "Wellington",
                     world, {"world": world})
        assert res["success"] is True
        assert ney.location == "Belgium"
        assert world.get_region("Rhineland").controller == "Prussia"
        assert "halts at the frontier of Rhineland" in res["message"]
        assert "advances into Rhineland" not in res["message"]
        # Review round: the halt line is not doubled by the capture block's
        # own "halts at the edge of conquest" (killed by `if True:` there).
        assert "edge of conquest" not in res["message"]

    def test_the_halted_player_charge_still_stages_the_war_choice(self):
        """Parity with `_execute_attack`: the halt is not a silence. Killed
        by dropping `or charge_halted` from the capture block's gate."""
        world, ney, _ = _charge_world(2)
        ex = _executor()
        res = _quiet(ex._combat._execute_glorious_charge, ney, "Wellington",
                     world, {"world": world})
        assert (world.pending_diplomatic_dialogue or {}).get("type") \
            == "war_purpose_selection"
        assert "To seize it is to make war on Prussia" in res["message"]
        assert res.get("awaiting_diplomatic_response") is True

    def test_with_the_lever_down_the_cavalry_stands_on_neutral_soil(
            self, monkeypatch):
        """The measured defect, reproduced by the flip lever - so the
        BASELINE_SERIES attribution arm is a real lever, not a comment."""
        monkeypatch.setattr(WS, "CHARGE_FRONTIER_HALT_ACTIVE", False)
        world, ney, _ = _charge_world(2)
        ex = _executor()
        res = _quiet(ex._combat._execute_glorious_charge, ney, "Wellington",
                     world, {"world": world})
        assert ney.location == "Rhineland"
        assert "halts at the frontier" not in res["message"]

    def test_an_enemys_own_war_soil_is_still_taken_by_the_charge(self):
        """The halt is the NEUTRAL arm only. Killed by halting on `is not
        None` instead of `arm == "neutral"`."""
        world, ney, _ = _charge_world(2, enemy_loc="Netherlands")
        ex = _executor()
        res = _quiet(ex._combat._execute_glorious_charge, ney, "Wellington",
                     world, {"world": world})
        assert res["success"] is True
        assert ney.location == "Netherlands"
        assert world.get_region("Netherlands").controller == "France"
        assert "advances into Netherlands" in res["message"]

    def test_an_allys_soil_is_entered_as_a_liberator_and_never_transfers(self):
        """PT-F1's ally arm is untouched: the charge advances, the soil
        stays. Killed by halting on the ally arm too."""
        world, ney, _ = _charge_world(2, host_state="ALLIANCE")
        ex = _executor()
        res = _quiet(ex._combat._execute_glorious_charge, ney, "Wellington",
                     world, {"world": world})
        assert ney.location == "Rhineland"
        assert world.get_region("Rhineland").controller == "Prussia"
        assert "remains Prussia's soil" in res["message"]
        assert world.pending_diplomatic_dialogue is None

    def test_the_reckless_auto_charge_halts_too(self):
        """The second implementation. Killed by deleting the
        `_halt_owner` arm in `_process_reckless_cavalry_turn_start`."""
        world, ney, _ = _charge_world(4)
        events = _quiet(world._process_reckless_cavalry_turn_start)
        assert [e["type"] for e in events] == ["auto_glorious_charge"]
        assert ney.location == "Belgium"
        assert world.get_region("Rhineland").controller == "Prussia"
        assert "halts at the frontier of Rhineland" in events[0]["message"]

    def test_the_reckless_auto_charge_lever_down_relocates_again(
            self, monkeypatch):
        monkeypatch.setattr(WS, "CHARGE_FRONTIER_HALT_ACTIVE", False)
        world, ney, _ = _charge_world(4)
        _quiet(world._process_reckless_cavalry_turn_start)
        assert ney.location == "Rhineland"

    def test_the_reckless_auto_charge_still_takes_war_soil(self):
        """Killed by an inverted predicate (`is_at_war` -> `not`)."""
        world, ney, _ = _charge_world(4, enemy_loc="Netherlands")
        events = _quiet(world._process_reckless_cavalry_turn_start)
        assert ney.location == "Netherlands"
        assert world.get_region("Netherlands").controller == "France"
        assert "advances into Netherlands" in events[0]["message"]

    @pytest.mark.parametrize("state", [
        "WAR", "PEACE", "ARMISTICE", "OPEN_BORDERS", "NON_AGGRESSION",
        "DEFENSIVE_ALLIANCE", "ALLIANCE", "VASSAL",
    ])
    def test_the_two_frontier_predicates_agree_on_every_state(self, state):
        """The drift pin: `frontier_halt_owner` (world_state, read by the
        reckless copy) halts exactly where `_pursuit_capture_guard`'s
        neutral arm halts (the executor copy). Killed by changing either
        predicate alone - e.g. reading `can_enter_territory` in one."""
        world, ney, _ = _charge_world(2, host_state=state)
        ex = _executor()
        guard = ex._combat._pursuit_capture_guard(ney, "Rhineland", world)
        halt = WS.frontier_halt_owner(world, "France", "Rhineland")
        executor_halts = guard is not None and guard["arm"] == "neutral"
        assert (halt is not None) == executor_halts, (state, guard, halt)
        if halt is not None:
            assert halt == guard["owner"] == "Prussia"

    def test_own_and_unclaimed_soil_never_halt(self):
        world, ney, _ = _charge_world(2)
        assert WS.frontier_halt_owner(world, "France", "Belgium") is None
        world.get_region("Rhineland").controller = None
        assert WS.frontier_halt_owner(world, "France", "Rhineland") is None


# ══════════════════════════════════════════════════════════════════
# 2. WO-25 - an attack the player never ordered never asks, never stages
# ══════════════════════════════════════════════════════════════════

class TestWO25TheAutonomousAttackNeverAsks:

    def test_an_autonomous_attack_at_recklessness_three_charges_at_once(self):
        """The strategic-sally road, taken by the autonomous attack. Killed
        by dropping the `_jealousy_autonomous` arm from `_no_charge_popup`
        (the popup returns, `success` False)."""
        world, ney, _ = _charge_world(3, enemy_loc="Netherlands")
        ex = _executor()
        res = _quiet(ex.execute, _attack_cmd("Ney", "Wellington", **AUTONOMOUS),
                     {"world": world})
        assert res["success"] is True
        assert res.get("glorious_charge") is True
        assert "pending_glorious_charge" not in res
        assert ney.pending_glorious_charge is False
        assert ney.pending_charge_target == ""

    def test_the_popup_door_is_shut_behind_it(self):
        """`respond_to_glorious_charge` is unreachable from an autonomous
        attack - the fourth PC15-D1 site is closed by construction."""
        world, ney, _ = _charge_world(3, enemy_loc="Netherlands")
        ex = _executor()
        _quiet(ex.execute, _attack_cmd("Ney", "Wellington", **AUTONOMOUS),
               {"world": world})
        res = _quiet(ex._combat.respond_to_glorious_charge, "charge", world)
        assert res["success"] is False
        assert "No pending Glorious Charge" in res["message"]

    def test_an_autonomous_charge_onto_neutral_soil_stages_no_war_decision(self):
        """The third staging site, guarded. Killed by dropping the
        `_jealousy_autonomous` read from the charge's staging condition, or
        by not passing `command` into `_execute_glorious_charge`."""
        world, ney, _ = _charge_world(3)
        ex = _executor()
        res = _quiet(ex.execute, _attack_cmd("Ney", "Wellington", **AUTONOMOUS),
                     {"world": world})
        assert res["success"] is True
        assert res.get("glorious_charge") is True
        assert world.pending_diplomatic_dialogue is None
        assert "choose our purpose" not in res["message"]
        assert ney.location == "Belgium"
        assert "halts at the frontier of Rhineland" in res["message"]

    def test_a_player_charge_onto_the_same_soil_still_asks(self):
        """The guard keys on the FLAG, not the path: the same charge typed
        by the player stages the war choice as PT-F1 intends."""
        world, ney, _ = _charge_world(3)
        ex = _executor()
        res = _quiet(ex.execute, {"command": {"marshal": "Ney", "action": "charge",
                                              "target": "Wellington"}},
                     {"world": world})
        assert res["success"] is True
        assert (world.pending_diplomatic_dialogue or {}).get("type") \
            == "war_purpose_selection"

    def test_with_the_lever_down_the_popup_returns(self, monkeypatch):
        monkeypatch.setattr(CE, "AUTONOMOUS_CHARGE_GUARD_ACTIVE", False)
        world, ney, _ = _charge_world(3, enemy_loc="Netherlands")
        ex = _executor()
        res = _quiet(ex.execute, _attack_cmd("Ney", "Wellington", **AUTONOMOUS),
                     {"world": world})
        assert res["success"] is False
        assert res.get("pending_glorious_charge") is True
        assert ney.pending_glorious_charge is True

    def test_with_the_lever_down_the_answered_charge_stages_the_war_decision(
            self, monkeypatch):
        """The measured defect end to end, reproduced by the lever: the
        answered popup relocates Ney onto Prussian PEACE soil (WO-24's
        halt is ALSO down here, to reproduce the pre-slice tree) and
        stages the modal from an attack nobody ordered."""
        monkeypatch.setattr(CE, "AUTONOMOUS_CHARGE_GUARD_ACTIVE", False)
        monkeypatch.setattr(WS, "CHARGE_FRONTIER_HALT_ACTIVE", False)
        world, ney, _ = _charge_world(3)
        ex = _executor()
        _quiet(ex.execute, _attack_cmd("Ney", "Wellington", **AUTONOMOUS),
               {"world": world})
        res = _quiet(ex._combat.respond_to_glorious_charge, "charge", world)
        assert res["success"] is True
        assert ney.location == "Rhineland"
        assert (world.pending_diplomatic_dialogue or {}).get("type") \
            == "war_purpose_selection"

    def _blocked_terrain_world(self, reck=3):
        """Wellington on PARIS (urban - charges blocked) with an
        alternative at Netherlands (plains): the redirect popup's arm."""
        ney = MarshalFactory.cavalry(name="Ney", location="Belgium",
                                     strength=40000, personality="aggressive")
        ney.recklessness = reck
        wel = MarshalFactory.enemy(name="Wellington", location="Paris",
                                   nation="Britain", strength=3000)
        alt = MarshalFactory.enemy(name="Uxbridge", location="Netherlands",
                                   nation="Britain", strength=2000)
        world = WorldFactory.with_marshals([ney, wel, alt])
        _pair(world, "France", "Britain", "WAR")
        return world, ney

    def test_the_redirect_popup_is_never_mounted_by_an_autonomous_attack(self):
        """Killed by dropping `not _no_charge_popup` from the redirect arm
        (`charge_redirected` returns, `pending_glorious_charge` armed)."""
        world, ney = self._blocked_terrain_world()
        ex = _executor()
        res = _quiet(ex.execute, _attack_cmd("Ney", "Wellington", **AUTONOMOUS),
                     {"world": world})
        assert res.get("charge_redirected") is None
        assert "pending_glorious_charge" not in res
        assert ney.pending_glorious_charge is False
        # ...and the attack the marshal meant went in, on the named man.
        assert res["success"] is True
        assert any(e.get("type") == "battle" for e in res.get("events", []))

    def test_a_strategic_sally_never_mounts_the_redirect_popup_either(self):
        """The pre-existing hole the same predicate closes: a HOLD sally on
        blocked terrain with an alternative in range used to return the
        redirect popup from INSIDE end-turn processing."""
        world, ney = self._blocked_terrain_world()
        ney.strategic_order = StrategicOrder(
            command_type="HOLD", target="Belgium", target_type="region",
            started_turn=1, original_command="Ney, hold Belgium", issued_turn=1)
        ex = _executor()
        res = _quiet(ex.execute,
                     _attack_cmd("Ney", "Wellington", _strategic_execution=True,
                                 _sortie=True),
                     {"world": world})
        assert res.get("charge_redirected") is None
        assert ney.pending_glorious_charge is False

    def test_a_player_attack_on_blocked_terrain_still_gets_the_redirect(self):
        """The popup itself is untouched for the player it exists for."""
        world, ney = self._blocked_terrain_world()
        ex = _executor()
        res = _quiet(ex.execute, _attack_cmd("Ney", "Wellington"),
                     {"world": world})
        assert res.get("charge_redirected") is True
        assert ney.pending_glorious_charge is True

    def test_every_pending_charge_write_sits_behind_the_predicate(self):
        """Structural census: `pending_glorious_charge = True` is written at
        exactly two sites in combat_executor, each inside an `if` whose
        test names `_no_charge_popup`. Killed by adding a third write, or
        by lifting either out from under the predicate."""
        tree = ast.parse(COMBAT_PY.read_text(encoding="utf-8"))
        writes = []

        def walk(node, guards):
            if isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if (isinstance(tgt, ast.Attribute)
                            and tgt.attr == "pending_glorious_charge"
                            and isinstance(node.value, ast.Constant)
                            and node.value.value is True):
                        writes.append(guards)
            if isinstance(node, ast.If):
                # Review round: only the BODY sits behind the test — an
                # `else`/`elif` arm sits behind its negation, and the first
                # cut credited it with the guard anyway.
                body_guards = guards + [ast.unparse(node.test)]
                for child in node.body:
                    walk(child, body_guards)
                for child in node.orelse:
                    walk(child, guards)
                return
            for child in ast.iter_child_nodes(node):
                walk(child, guards)

        walk(tree, [])
        assert len(writes) == 2, writes
        for guards in writes:
            assert any("_no_charge_popup" in g for g in guards), guards

    def test_the_unordered_attack_predicate_is_a_census(self):
        """Code-only count of `_attack_is_unordered(command)` call sites in
        combat_executor: the two `_execute_attack` staging sites, the
        charge's staging site, the reckless-popup predicate and the muster
        gate (review round). The flags themselves are read ONCE, inside the
        predicate. A sixth site or a lost one changes this consciously."""
        code = _code_only(COMBAT_PY.read_text(encoding="utf-8"))
        # `_code_only` emits one token per line - squeeze before matching
        # a multi-token needle (the slice-10 trap, met again here).
        squeezed = re.sub(r"\s+", "", code)
        # The definition line matches the needle too - subtract it, so a
        # lost site cannot hide behind the def.
        calls = (squeezed.count("_attack_is_unordered(command)")
                 - squeezed.count("def_attack_is_unordered(command)"))
        assert calls == 5
        assert code.count('"_jealousy_autonomous"') == 1
        assert code.count('"_defiance"') == 1


# ══════════════════════════════════════════════════════════════════
# 3. WO-28 - a refused autonomous attack restores what it voided
# ══════════════════════════════════════════════════════════════════

def _jealous_world(*, fortified, order=None, hold=False):
    """Ney, warned and envious of Davout, with Wellington adjacent on
    Britain's own war soil. `fortified` makes the executor REFUSE the
    attack ("fortified ... cannot attack") - the refusal shape left once
    WO-25 closed the popup one."""
    ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                  strength=40000, personality="aggressive")
    ney.fortified = fortified
    ney.jealous_of = "Davout"
    ney.jealousy_autonomous_warned = True
    if order is not None:
        ney.strategic_order = order
    if hold:
        ney.holding_position = True
        ney.hold_region = "Belgium"
    dav = MarshalFactory.infantry(name="Davout", location="Paris",
                                  strength=30000, personality="cautious")
    wel = MarshalFactory.enemy(name="Wellington", location="Netherlands",
                               nation="Britain", strength=2000)
    wel.morale = 26
    world = WorldFactory.with_marshals([ney, dav, wel])
    _pair(world, "France", "Britain", "WAR")
    return world, ney


def _move_order():
    return StrategicOrder(command_type="MOVE_TO", target="Paris",
                          target_type="region", started_turn=1,
                          original_command="Ney, march to Paris", issued_turn=1)


def _hold_order():
    return StrategicOrder(command_type="HOLD", target="Belgium",
                          target_type="region", started_turn=1,
                          original_command="Ney, hold Belgium", issued_turn=1)


def _types(world):
    return [e["type"] for e in getattr(world, "_pending_jealousy_turn_events", [])]


class TestWO28TheRefusedAttackRestoresTheOrder:

    def test_a_refused_attack_gives_the_order_back_and_fires_no_beat(self):
        """Killed by deleting the refusal arm in `process_autonomous_attacks`
        (order stays None, the attack beat and log row are written)."""
        order = _move_order()
        world, ney = _jealous_world(fortified=True, order=order)
        ex = _executor()
        results = _quiet(J.process_autonomous_attacks, world, ex, {"world": world})
        assert results == []
        assert ney.strategic_order is order
        types = _types(world)
        assert "jealousy_autonomous_refused" in types
        assert "jealousy_autonomous_attack" not in types
        assert "order_voided_by_battle" not in types
        assert not [e for e in world.event_log
                    if e.get("type") == "jealousy_autonomous"]

    def test_the_refusal_line_carries_the_executors_reason(self):
        world, ney = _jealous_world(fortified=True, order=_move_order())
        _quiet(J.process_autonomous_attacks, world, _executor(), {"world": world})
        refused = [e for e in world._pending_jealousy_turn_events
                   if e["type"] == "jealousy_autonomous_refused"]
        assert len(refused) == 1
        msg = refused[0]["message"]
        assert msg.startswith("Ney meant to go at Wellington on his own initiative, but ")
        assert "fortified" in msg
        assert msg.endswith("his orders are unchanged.")
        assert refused[0]["nation"] == "France"
        assert refused[0]["marshal"] == "Ney"

    def test_a_refused_hold_keeps_its_hold(self):
        """The void clears `holding_position`/`hold_region` too; the
        refusal restores them. Killed by restoring the order alone."""
        world, ney = _jealous_world(fortified=True, order=_hold_order(), hold=True)
        _quiet(J.process_autonomous_attacks, world, _executor(), {"world": world})
        assert ney.holding_position is True
        assert ney.hold_region == "Belgium"

    def test_the_order_bound_interrupt_survives_a_refusal(self):
        """NPC-2 clears the order's question with the order; a refusal that
        gives the order back gives the question back. Killed by dropping
        the `_interrupt_before` restore."""
        world, ney = _jealous_world(fortified=True, order=_move_order())
        interrupt = {"interrupt_type": sorted(ORDER_BOUND_INTERRUPT_TYPES)[0],
                     "marshal": "Ney", "enemy": "Wellington"}
        ney.pending_interrupt = interrupt
        _quiet(J.process_autonomous_attacks, world, _executor(), {"world": world})
        assert ney.pending_interrupt is interrupt

    def test_a_fought_attack_still_voids_narrates_and_logs_in_order(self):
        """The success path is byte-for-byte the old one, INCLUDING the
        order of the two beats (void first, then the attack). Killed by
        appending the void beat after the battle instead of inserting it
        at its taken index."""
        order = _move_order()
        world, ney = _jealous_world(fortified=False, order=order)
        results = _quiet(J.process_autonomous_attacks, world, _executor(),
                         {"world": world})
        assert len(results) == 1 and results[0]["jealousy_autonomous"] == "Ney"
        assert results[0]["success"] is True
        assert ney.strategic_order is None
        types = _types(world)
        assert "jealousy_autonomous_refused" not in types
        assert types.index("order_voided_by_battle") \
            < types.index("jealousy_autonomous_attack")
        assert [e for e in world.event_log
                if e.get("type") == "jealousy_autonomous"]

    def test_the_void_beat_keeps_its_place_before_what_the_battle_appends(self):
        """The void line's index is taken BEFORE the attack runs and the
        line is inserted there afterwards, so anything the battle itself
        appends (a resolution note, a crown) still reads after it - the
        pre-slice order. Killed by appending instead of inserting."""
        world, ney = _jealous_world(fortified=False, order=_move_order())

        class _Stub:
            def execute(self, command, game_state):
                J._pending_events(world).append(
                    {"type": "marker", "nation": "France", "marshal": "Ney"})
                return {"success": True, "message": "fought"}

        _quiet(J.process_autonomous_attacks, world, _Stub(), {"world": world})
        assert _types(world) == ["order_voided_by_battle", "marker",
                                 "jealousy_autonomous_attack"]

    def test_with_the_lever_down_the_refusal_is_narrated_as_a_battle(
            self, monkeypatch):
        """The measured defect, reproduced by the flip lever."""
        monkeypatch.setattr(J, "AUTONOMOUS_REFUSAL_RESTORES_ORDER_ACTIVE", False)
        world, ney = _jealous_world(fortified=True, order=_move_order())
        results = _quiet(J.process_autonomous_attacks, world, _executor(),
                         {"world": world})
        assert len(results) == 1 and results[0]["success"] is False
        assert ney.strategic_order is None
        types = _types(world)
        assert "jealousy_autonomous_attack" in types
        assert "order_voided_by_battle" in types
        assert "jealousy_autonomous_refused" not in types

    def test_the_refusal_beat_reaches_the_dispatch_uncapped(self):
        """A new pending-event type is dropped at the dispatch whitelist
        unless added there (the shadow_petition lesson), and collapsed
        into the drama tail unless exempt. Both pinned, then RENDERED."""
        assert "jealousy_autonomous_refused" in D._DISPATCH_EVENT_TYPES
        assert "jealousy_autonomous_refused" in J.JEALOUSY_NARRATION_EXEMPT
        rows = D._build_turn_events([{
            "type": "jealousy_autonomous_refused", "nation": "France",
            "marshal": "Ney",
            "message": "Ney meant to go at Wellington on his own initiative, "
                       "but he is fortified — his orders are unchanged."}],
            "France")
        assert any("his orders are unchanged" in r.get("message", "")
                   for r in rows), rows

    @pytest.mark.parametrize("message,expected", [
        ("[Cavalry][Blocked] Ney is fortified at Belgium and cannot attack. "
         "Order 'unfortify' first.",
         "Ney is fortified at Belgium and cannot attack"),
        ("", "the attack could not be made"),
        ("ArchdukeCharles holds Vienna.", "Archduke Charles holds Vienna"),
        ("[color=#cd6b6b]No enemies found to attack![/color]",
         "No enemies found to attack"),
    ])
    def test_the_reason_is_the_executors_first_sentence_without_chrome(
            self, message, expected):
        assert J._refusal_reason({"message": message}) == expected
        assert J._refusal_reason(None) == "the attack could not be made"


# ══════════════════════════════════════════════════════════════════
# 4. WO-31 - the sally clears the field and does not take the ground
# ══════════════════════════════════════════════════════════════════

def _sally_world(enemy_loc="Netherlands", host_state="PEACE", with_order=True):
    ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                  strength=40000, personality="aggressive")
    if with_order:
        ney.strategic_order = _hold_order()
        ney.holding_position = True
        ney.hold_region = "Belgium"
    wel = MarshalFactory.enemy(name="Wellington", location=enemy_loc,
                               nation="Britain", strength=2000)
    wel.morale = 26   # one exchange breaks him - the field is CLEARED
    world = WorldFactory.with_marshals([ney, wel], current_turn=2)
    _pair(world, "France", "Britain", "WAR")
    _pair(world, "France", "Prussia", host_state)
    return world, ney


def _run_hold(world):
    ex = _executor()
    return _quiet(StrategicOrderProcessor(ex).process_strategic_orders,
                  world, {"world": world}), ex


class TestWO31TheSallyDoesNotTakeTheGround:

    def test_a_won_sally_leaves_the_province_where_it_was(self):
        """Killed by deleting `sortie_stands_off` from the capture gate
        (Netherlands flips, a plunder question is mounted)."""
        world, ney = _sally_world()
        reports, _ = _run_hold(world)
        assert [r.get("action") for r in reports] == ["sally"]
        assert reports[0]["outcome"] == "attacker_tactical_victory"
        assert ney.location == "Belgium"
        assert world.get_region("Netherlands").controller == "Britain"
        assert not world.pending_capture_choice
        assert not getattr(ney, "occupation_region", None)
        msg = (reports[0].get("battle_details") or {}).get("message", "")
        assert "sally clears Netherlands but does not hold it" in msg
        assert "taken by the army that stands on it" in msg

    def test_with_the_lever_down_the_sally_flips_the_province(self, monkeypatch):
        """The measured defect: the flip AND the question for a province
        he never entered."""
        monkeypatch.setattr(CE, "SORTIE_CAPTURE_REQUIRES_STANDING_ACTIVE", False)
        world, ney = _sally_world()
        _run_hold(world)
        assert ney.location == "Belgium"
        assert world.get_region("Netherlands").controller == "France"
        assert world.pending_capture_choice

    def test_a_direct_attack_from_the_same_position_still_takes_it(self):
        """The predicate is `_current_sortie`, not "attacked from
        adjacent". Killed by keying on `marshal.location != target`
        alone."""
        world, ney = _sally_world(with_order=False)
        ex = _executor()
        res = _quiet(ex.execute, _attack_cmd("Ney", "Wellington"), {"world": world})
        assert res["success"] is True
        assert ney.location == "Netherlands"
        assert world.get_region("Netherlands").controller == "France"

    def test_a_sortie_already_standing_on_the_field_still_takes_it(self):
        """Killed by dropping `marshal.location != target_location` from
        the predicate."""
        ney = MarshalFactory.infantry(name="Ney", location="Netherlands",
                                      strength=40000, personality="aggressive")
        wel = MarshalFactory.enemy(name="Wellington", location="Netherlands",
                                   nation="Britain", strength=2000)
        wel.morale = 26
        world = WorldFactory.with_marshals([ney, wel])
        _pair(world, "France", "Britain", "WAR")
        ex = _executor()
        res = _quiet(ex.execute,
                     _attack_cmd("Ney", "Wellington", _strategic_execution=True,
                                 _sortie=True),
                     {"world": world})
        assert res["success"] is True
        assert world.get_region("Netherlands").controller == "France"

    def test_the_sally_never_stages_a_war_decision_on_neutral_soil(self):
        """A sally cannot seize the ground even at war, so the neutral-arm
        "choose our purpose" modal has nothing to offer it - the whole
        capture block is short-circuited, staging included."""
        world, ney = _sally_world(enemy_loc="Rhineland")
        reports, _ = _run_hold(world)
        assert [r.get("action") for r in reports] == ["sally"]
        assert world.pending_diplomatic_dialogue is None
        assert world.get_region("Rhineland").controller == "Prussia"
        assert ney.location == "Belgium"
        msg = (reports[0].get("battle_details") or {}).get("message", "")
        assert "choose our purpose" not in msg
        # Review round: on a third party's soil the reason is the soil,
        # not the standing - "the army that stands on it" would take
        # nothing either. Killed by printing the at-war line here.
        assert "Rhineland remains Prussia's soil" in msg
        assert "the sally was against the enemy standing on it" in msg
        assert "does not hold it" not in msg

    def test_a_won_sally_with_defenders_left_claims_nothing(self):
        """The "clears ... but does not hold it" line is for a CLEARED
        field. Killed by printing it whenever `sortie_stands_off`."""
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=40000, personality="aggressive")
        ney.strategic_order = _hold_order()
        ney.holding_position = True
        ney.hold_region = "Belgium"
        wel = MarshalFactory.enemy(name="Wellington", location="Netherlands",
                                   nation="Britain", strength=2000)
        wel.morale = 26
        # A second corps that stays on the field: hostile to Wellington's
        # nation as well, so it neither reinforces him nor routs with him.
        stay = MarshalFactory.enemy(name="Reynier", location="Netherlands",
                                    nation="Saxony", strength=30000)
        world = WorldFactory.with_marshals([ney, wel, stay], current_turn=2)
        _pair(world, "France", "Britain", "WAR")
        _pair(world, "France", "Saxony", "WAR")
        _pair(world, "Britain", "Saxony", "WAR")
        reports, _ = _run_hold(world)
        assert [r.get("action") for r in reports] == ["sally"]
        assert reports[0]["outcome"] == "attacker_tactical_victory"
        assert stay.location == "Netherlands" and stay.strength > 0
        msg = (reports[0].get("battle_details") or {}).get("message", "")
        assert "does not hold it" not in msg
        assert world.get_region("Netherlands").controller == "Britain"

    def test_a_lost_sally_says_nothing_about_holding(self):
        """The copy is gated on the field being cleared. Killed by
        printing the line whenever `sortie_stands_off`."""
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=6000, personality="aggressive")
        ney.strategic_order = _hold_order()
        ney.holding_position = True
        ney.hold_region = "Belgium"
        wel = MarshalFactory.enemy(name="Wellington", location="Netherlands",
                                   nation="Britain", strength=5000)
        wel2 = MarshalFactory.enemy(name="Uxbridge", location="Netherlands",
                                    nation="Britain", strength=50000)
        world = WorldFactory.with_marshals([ney, wel, wel2], current_turn=2)
        _pair(world, "France", "Britain", "WAR")
        reports, _ = _run_hold(world)
        for r in reports:
            msg = (r.get("battle_details") or {}).get("message", "")
            assert "does not hold it" not in msg
        assert world.get_region("Netherlands").controller == "Britain"


# ══════════════════════════════════════════════════════════════════
# 5. The levers exist as module globals, read at call time
# ══════════════════════════════════════════════════════════════════

class TestTheLeversAreRealLevers:

    def test_all_four_levers_ship_up(self):
        assert WS.CHARGE_FRONTIER_HALT_ACTIVE is True
        assert CE.AUTONOMOUS_CHARGE_GUARD_ACTIVE is True
        assert CE.SORTIE_CAPTURE_REQUIRES_STANDING_ACTIVE is True
        assert J.AUTONOMOUS_REFUSAL_RESTORES_ORDER_ACTIVE is True

    def test_the_charge_reads_world_states_lever_at_call_time(self):
        """A from-import would freeze the lever at import and make the
        attribution arm a no-op on the executor path. Code-only scan for
        the module-alias read."""
        code = _code_only(COMBAT_PY.read_text(encoding="utf-8"))
        squeezed = re.sub(r"\s+", "", code)
        assert "_ws_mod.CHARGE_FRONTIER_HALT_ACTIVE" in squeezed
        assert "importCHARGE_FRONTIER_HALT_ACTIVE" not in squeezed


# ══════════════════════════════════════════════════════════════════
# 6. The review round at the committed SHA (611013f2) - three lenses
# ══════════════════════════════════════════════════════════════════

def _objection_to_defend(marshal="Ney"):
    """The pending tactical objection the meta executor answers - the
    reviewer's reproduction shape."""
    return {
        "type": "major_objection", "concern_level": "MODERATE",
        "trust_tier": "TRUSTING", "tone": "firm", "insist_penalty": -10,
        "trust_gain": 3, "compromise_gain": 2, "trust_gain_modifier": 1.0,
        "severity": "major",
        "message": f"{marshal} objects to sitting on the defensive.",
        "marshal": marshal, "personality": "aggressive",
        "original_order": {"marshal": marshal, "action": "defend", "target": ""},
        "suggested_alternative": None, "compromise": None,
    }


def _force_defiance(monkeypatch):
    import backend.commands.defiance as DF
    import backend.commands.meta_executor as ME

    monkeypatch.setattr(DF, "calculate_defiance_chance", lambda *a, **k: 1.0)
    monkeypatch.setattr(ME.random, "random", lambda: 0.0)


class TestTheReviewRound:

    def test_a_defiant_charge_never_arms_the_popup_nor_stages_a_war(
            self, monkeypatch):
        """[P2] The defiance callers passed NO command, so a reckless-3
        cavalryman defying a defend order armed the CHARGE/RESTRAIN popup,
        the caller discarded the question, and the flag stayed armed for the
        next bare `charge` - which then fired a 2x charge AND the war-purpose
        HARD STOP from an attack nobody ordered. Killed by dropping
        `_defiance` from `_attack_is_unordered`, or the stamp from the
        objection defiance site."""
        world, ney, _ = _charge_world(3)          # Wellington on PEACE soil
        world.actions_remaining = 3
        world.pending_objection = _objection_to_defend()
        _force_defiance(monkeypatch)
        ex = _executor()
        res = _quiet(ex._meta.handle_objection_response, "insist", {"world": world})
        assert ney.pending_glorious_charge is False
        assert ney.pending_charge_target == ""
        # He DID go - the charge fired at once (recklessness spent)...
        assert ney.recklessness == 0
        assert "pending_glorious_charge" not in res
        # ...halted at the frontier, and staged nothing.
        assert ney.location == "Belgium"
        assert world.pending_diplomatic_dialogue is None
        later = _quiet(ex._combat.respond_to_glorious_charge, "charge", world)
        assert later["success"] is False
        assert "No pending Glorious Charge" in later["message"]

    def test_both_defiance_sites_carry_the_stamp(self):
        """Census: the strategic-objection defiance site is reached only
        through a strategic objection answer, so its stamp is pinned by
        source (code-only) rather than driven."""
        for name in ("strategic_executor.py", "meta_executor.py"):
            code = _code_only((REPO / "backend" / "commands" / name)
                              .read_text(encoding="utf-8"))
            assert re.sub(r"\s+", "", code).count(
                'command={"_defiance":True}') == 1, name

    def test_the_muster_gate_never_arms_on_a_defiance(self, monkeypatch):
        """A stamped defiance carries a command dict, which used to be the
        muster gate's whole arming condition. Killed by dropping the
        predicate from the gate (the defiance returns the muster confirm
        instead of fighting)."""
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=40000, personality="aggressive")
        wel = MarshalFactory.enemy(name="Wellington", location="Netherlands",
                                   nation="Britain", strength=2000)
        wel.morale = 26
        world = WorldFactory.with_marshals([ney, wel])
        _pair(world, "France", "Britain", "WAR")
        world.actions_remaining = 3
        world.pending_objection = _objection_to_defend()
        _force_defiance(monkeypatch)
        ex = _executor()
        res = _quiet(ex._meta.handle_objection_response, "insist", {"world": world})
        assert not res.get("muster_confirm")
        assert res.get("state") != "awaiting_clarification"
        assert "muster" not in (res.get("message") or "").lower()

    def _blocked_terrain_world(self):
        ney = MarshalFactory.cavalry(name="Ney", location="Belgium",
                                     strength=40000, personality="aggressive")
        ney.recklessness = 3
        wel = MarshalFactory.enemy(name="Wellington", location="Paris",
                                   nation="Britain", strength=3000)
        alt = MarshalFactory.enemy(name="Uxbridge", location="Netherlands",
                                   nation="Britain", strength=2000)
        world = WorldFactory.with_marshals([ney, wel, alt])
        _pair(world, "France", "Britain", "WAR")
        return world, ney, wel, alt

    def test_restrain_attacks_the_man_the_popup_named(self):
        """[P2, pre-existing] The redirect popup says "RESTRAIN: Normal
        attack on {original}" and fought the ALTERNATIVE. Killed by
        `if False:` on the restrain-target arm, or by dropping the
        `from_dict` restore."""
        world, ney, wel, alt = self._blocked_terrain_world()
        ex = _executor()
        res = _quiet(ex.execute, _attack_cmd("Ney", "Wellington"), {"world": world})
        assert res.get("charge_redirected") is True
        assert ney.pending_charge_target == "Uxbridge"
        assert ney.pending_charge_restrain_target == "Wellington"
        assert "Normal attack on Wellington" in res["message"]
        res2 = _quiet(ex._combat.respond_to_glorious_charge, "restrain", world)
        assert res2["success"] is True
        assert wel.strength < 3000, "the promised man was not attacked"
        assert alt.strength == 2000, "the alternative was attacked instead"
        assert ney.pending_charge_restrain_target == ""

    def test_the_restrain_target_survives_a_save(self):
        from backend.models.marshal import Marshal

        ney = MarshalFactory.cavalry(name="Ney", location="Belgium",
                                     strength=10000, personality="aggressive")
        ney.pending_glorious_charge = True
        ney.pending_charge_target = "Uxbridge"
        ney.pending_charge_restrain_target = "Wellington"
        back = Marshal.from_dict(ney.to_dict())
        assert back.pending_charge_restrain_target == "Wellington"
        legacy = ney.to_dict()
        del legacy["pending_charge_restrain_target"]
        assert Marshal.from_dict(legacy).pending_charge_restrain_target == ""

    def test_the_pending_question_dies_with_the_momentum(self):
        """[P2] A popup armed by a player attack and overtaken by an
        auto-charge stayed armed - serialized - and the next bare `charge`
        fired a 2x charge at recklessness 0 on a turn-old decision, staging
        the war-purpose HARD STOP with it. Killed by restoring
        `reset_recklessness` to the bare `recklessness = 0`."""
        world, ney, _ = _charge_world(3)
        ex = _executor()
        armed = _quiet(ex.execute, _attack_cmd("Ney", "Wellington"), {"world": world})
        assert armed.get("pending_glorious_charge") is True
        assert ney.pending_glorious_charge is True
        # The autonomous glory attack overtakes the question and spends
        # the momentum it asked about.
        _quiet(ex.execute, _attack_cmd("Ney", "Wellington", **AUTONOMOUS),
               {"world": world})
        assert ney.recklessness == 0
        assert ney.pending_glorious_charge is False
        assert ney.pending_charge_target == ""
        later = _quiet(ex._combat.respond_to_glorious_charge, "charge", world)
        assert later["success"] is False

    def test_a_neutral_bystander_does_not_silence_the_sally_line(self):
        """The cleared-field test reads AT-WAR defenders: a peaceful
        court's corps standing on the enemy's province is not a defender.
        Killed by dropping `is_at_war` from `_sortie_remaining`."""
        world, ney = _sally_world()
        bystander = MarshalFactory.enemy(name="Blucher", location="Netherlands",
                                         nation="Prussia", strength=30000)
        world.marshals["Blucher"] = bystander
        _pair(world, "France", "Prussia", "PEACE")
        _pair(world, "Britain", "Prussia", "PEACE")
        reports, _ = _run_hold(world)
        assert [r.get("action") for r in reports] == ["sally"]
        assert reports[0]["outcome"] == "attacker_tactical_victory"
        msg = (reports[0].get("battle_details") or {}).get("message", "")
        assert "sally clears Netherlands but does not hold it" in msg
        assert world.get_region("Netherlands").controller == "Britain"

    def test_a_same_province_reckless_charge_prints_no_frontier(self):
        """The reckless copy halts a MOVE, never a stand: on his own field
        (however he got there) there is no frontier to halt at. Killed by
        dropping the location clause from the halt arm."""
        ney = MarshalFactory.cavalry(name="Ney", location="Rhineland",
                                     strength=40000, personality="aggressive")
        ney.recklessness = 4
        wel = MarshalFactory.enemy(name="Wellington", location="Rhineland",
                                   nation="Britain", strength=2000)
        wel.morale = 26
        world = WorldFactory.with_marshals([ney, wel])
        _pair(world, "France", "Britain", "WAR")
        _pair(world, "France", "Prussia", "PEACE")
        events = _quiet(world._process_reckless_cavalry_turn_start)
        assert [e["type"] for e in events] == ["auto_glorious_charge"]
        assert ney.location == "Rhineland"
        assert "halts at the frontier" not in events[0]["message"]

    def _jealous_ney_world(self):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=40000, personality="aggressive")
        ney.jealous_of = "Davout"
        ney.jealousy_turns_remaining = 4
        dav = MarshalFactory.infantry(name="Davout", location="Paris",
                                      strength=30000, personality="cautious")
        wel = MarshalFactory.enemy(name="Wellington", location="Netherlands",
                                   nation="Britain", strength=2000)
        world = WorldFactory.with_marshals([ney, dav, wel])
        _pair(world, "France", "Britain", "WAR")
        world._jealousy_processed_turn = None
        return world, ney

    def test_a_fortified_marshal_is_never_warned(self):
        """[P3] The warning promised a battle the fortified gate then
        refused, every turn of the window. Killed by removing the
        `fortified` skip from the warning step."""
        world, ney = self._jealous_ney_world()
        ney.fortified = True
        events = _quiet(J.process_turn, world)
        assert ney.jealousy_autonomous_warned is False
        assert not [e for e in events
                    if e["type"] == "jealousy_autonomous_warning"]
        # ...and unfortified, the same marshal IS warned (the skip is the
        # fortification, not the marshal).
        world2, ney2 = self._jealous_ney_world()
        events2 = _quiet(J.process_turn, world2)
        assert ney2.jealousy_autonomous_warned is True
        assert [e for e in events2
                if e["type"] == "jealousy_autonomous_warning"]

    def test_a_warned_marshal_whose_quarry_left_is_told(self):
        """[P3] A consumed warning is never silent. Killed by restoring the
        bare `continue`."""
        world, ney = self._jealous_ney_world()
        ney.jealousy_autonomous_warned = True
        world.get_marshal("Wellington").location = "Hanover"   # out of reach
        results = _quiet(J.process_autonomous_attacks, world, _executor(),
                         {"world": world})
        assert results == []
        assert ney.jealousy_autonomous_warned is False
        refused = [e for e in _types(world) if e == "jealousy_autonomous_refused"]
        assert len(refused) == 1
        msg = [e for e in world._pending_jealousy_turn_events
               if e["type"] == "jealousy_autonomous_refused"][0]["message"]
        assert "no enemy stood within his reach" in msg
        assert "his orders are unchanged" in msg

    def test_the_refused_line_renders_in_its_siblings_register(self):
        """Killed by dropping the type from the dispatch's warning tuple."""
        rows = D._build_turn_events([{
            "type": "jealousy_autonomous_refused", "nation": "France",
            "marshal": "Ney", "message": "Ney meant to go, but did not."}],
            "France")
        assert rows and rows[0]["severity"] == "warning"

    def test_the_sortie_flag_is_initialised(self):
        assert _executor()._current_sortie is False
