"""Final Whole-Game Audit — slice 2 REVIEW ROUND, "The Word Is Owed".

Three review lenses attacked commit aa6faa01 ("No Word Came") and every one
of them found the same hole from a different side: the FA-16 gate sat under
`should_check_objection`, whose predicate EXCLUDES strategic commands and
whose action list omits charge/bombard/garrison/unfortify — so `Ney, march
to Paris` issued a MOVE_TO and overwrote the parked last stand with a
contact question (the third destroyer the record claimed closed), `Ney,
pursue Mack` co-located ran the attack at once and FA-1's resolution fired
in the PLAYER phase, and the un-addressed `retreat` walked him out for
free with the ask still standing. Plus, on the AI side, the P0 brakes
traded the grind for a FREEZE (an engaged corps fell through to an attack
the executor refuses, writing a two-turn cooldown) and mispriced the field.

Fixed here, each behind the existing or a new lever:

* the gate is ONE function (`standing_last_stand_refusal`), read by the
  executor ABOVE the objection predicate for every marshal-bearing verb,
  by the general retreat / bare attack / auto-scout rosters, and by
  Berthier's parse-recovery line;
* liveness re-keys to the CURRENT besieger instead of retiring the
  question when the man who asked it has drawn off (R1-F4);
* step 0a re-validates a decision parked on an ORDERED marshal (R2-F4);
* the muster is re-validated like the last stand (R2-F5);
* `pending_marshal_decisions` rides beside `pending_lapsing_count` so the
  client can warn before the enemy phase decides for him (R1-F5);
* P0: a braked corps HOLDS (R1-F1), the field is priced whole (R1-F2), and
  the futility brake is read (FA-N72's non-stub half).
"""

import contextlib
import io
import pathlib
import random

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.ai import enemy_ai as enemy_mod
from backend.ai.enemy_ai import EnemyAI
from backend.commands import strategic as strategic_mod
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser
from backend.commands.strategic import (
    ATTACK_FUTILITY_LIMIT,
    STANDING_DECISION_EXEMPT_ACTIONS,
    StrategicOrderProcessor,
    current_besieger,
    last_stand_is_live,
    last_stand_question_line,
    muster_is_live,
    pending_marshal_decisions,
    standing_last_stand_refusal,
)
from backend.models.marshal import StrategicOrder
from tests.conftest import MarshalFactory, WorldFactory
from tests.test_fa_slice2_no_word_came_2026_09_04 import (
    _ask,
    _cornered_ney,
    _engaged_pair,
    _rail_row,
    _rail_rows,
    _war,
)

REPO = pathlib.Path(__file__).resolve().parents[1]


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@contextlib.contextmanager
def _served(world):
    """The real endpoints on `world`, with the mock parser (never a paid
    call), all three module seams swapped and restored."""
    saved = (M.world, M.game_state, M.parser)
    M.world = world
    M.game_state = {"world": world}
    M.parser = CommandParser(use_real_llm=False)
    try:
        assert M.parser.llm.use_real_api is False
        yield TestClient(M.app)
    finally:
        M.world, M.game_state, M.parser = saved


def _adjacent_geometry():
    """The reviewers' shape: Ney cornered at Belgium, Mack ADJACENT at
    Rhineland — where the pre-existing "engaged" rule does NOT mask the
    gate, which is why slice 2's co-located pins were all green."""
    world, ney, mack, ask = _cornered_ney(enemy_location="Rhineland")
    world.calculate_visibility()
    return world, ney, mack, ask


# ═══════════════════════════════════════════════════════════════════════
# The gate is one function, above the objection predicate
# ═══════════════════════════════════════════════════════════════════════

class TestTheGateCoversEveryVerb:

    def test_the_refusal_is_one_function(self):
        world, ney, _mack, _ask = _adjacent_geometry()
        refusal = standing_last_stand_refusal(ney, "move")
        assert refusal["success"] is False
        assert refusal["no_action_cost"] is True
        assert refusal["last_stand_pending"] is True
        assert refusal["message"].startswith(last_stand_question_line(ney))
        assert "No other order can reach him" in refusal["message"]

    @pytest.mark.parametrize("action", sorted(STANDING_DECISION_EXEMPT_ACTIONS))
    def test_the_exempt_verbs_are_not_orders(self, action):
        world, ney, _mack, _ask = _adjacent_geometry()
        assert standing_last_stand_refusal(ney, action) is None

    def test_no_question_no_refusal(self):
        world, ney, _mack, _ask = _adjacent_geometry()
        ney.pending_interrupt = None
        assert standing_last_stand_refusal(ney, "move") is None
        ney.pending_interrupt = {"interrupt_type": "muster_confirm",
                                 "marshal": "Ney", "target": "Mack",
                                 "options": ["attack_anyway", "cancel_order"]}
        assert standing_last_stand_refusal(ney, "move") is None, \
            "a muster is a soft question; only the last stand bars orders"

    @pytest.mark.parametrize("parsed", [
        # The strategic family — the reviewers' headline bypass.
        {"is_strategic": True, "strategic_type": "MOVE_TO", "target": "Paris",
         "marshal": "Ney", "action": "move", "original_command": "Ney, march to Paris",
         "command": {"marshal": "Ney", "action": "move", "target": "Paris"}},
        {"is_strategic": True, "strategic_type": "HOLD", "target": "Belgium",
         "marshal": "Ney", "action": "hold", "original_command": "Ney, hold Belgium",
         "command": {"marshal": "Ney", "action": "hold", "target": "Belgium"}},
        {"is_strategic": True, "strategic_type": "PURSUE", "target": "Mack",
         "marshal": "Ney", "action": "attack", "original_command": "Ney, pursue Mack",
         "command": {"marshal": "Ney", "action": "attack", "target": "Mack"}},
        # The verbs the objection list never named.
        {"command": {"marshal": "Ney", "action": "charge", "target": "Mack"}},
        {"command": {"marshal": "Ney", "action": "bombard", "target": "Mack"}},
        {"command": {"marshal": "Ney", "action": "garrison"}},
        {"command": {"marshal": "Ney", "action": "unfortify"}},
        {"command": {"marshal": "Ney", "action": "scout", "target": "Rhineland"}},
        {"command": {"marshal": "Ney", "action": "recruit"}},
    ])
    def test_every_verb_is_refused_free_with_the_question_standing(self, parsed):
        world, ney, _mack, ask = _adjacent_geometry()
        ap = world.actions_remaining
        trust = ney.trust.value
        rail = len(_rail_rows(world, "Ney"))
        with _quiet():
            result = CommandExecutor().execute(dict(parsed), {"world": world})
        assert result["success"] is False, result
        assert result.get("last_stand_pending") is True, result
        assert "fight to the last" in result["message"]
        assert ney.pending_interrupt is ask, "the ask was overwritten or consumed"
        assert ney.strategic_order is None, "a phantom order was issued"
        assert ney.location == "Belgium"
        assert world.actions_remaining == ap
        assert ney.trust.value == trust
        assert len(_rail_rows(world, "Ney")) == rail, "the rail row was orphaned"

    def test_cancel_still_names_the_question_for_free(self):
        world, ney, _mack, ask = _adjacent_geometry()
        with _quiet():
            result = CommandExecutor().execute(
                {"command": {"marshal": "Ney", "action": "cancel"}}, {"world": world})
        assert result["success"] is True
        assert "fight to the last" in result["message"]
        assert ney.pending_interrupt is ask

    def test_the_ai_and_the_processor_are_exempt(self):
        world, ney, _mack, ask = _adjacent_geometry()
        with _quiet():
            r = CommandExecutor().execute(
                {"command": {"marshal": "Ney", "action": "move", "target": "Paris",
                             "_strategic_execution": True}}, {"world": world})
        assert r.get("last_stand_pending") is None and ney.location == "Paris"

    def test_the_lever_down_lets_the_march_through(self, monkeypatch):
        monkeypatch.setattr(strategic_mod, "STANDALONE_DECISION_LIVENESS_ACTIVE", False)
        world, ney, _mack, ask = _adjacent_geometry()
        parsed = {"is_strategic": True, "strategic_type": "MOVE_TO", "target": "Paris",
                  "marshal": "Ney", "action": "move", "original_command": "Ney, march to Paris",
                  "command": {"marshal": "Ney", "action": "move", "target": "Paris"}}
        with _quiet():
            result = CommandExecutor().execute(parsed, {"world": world})
        assert result.get("last_stand_pending") is None
        assert ney.strategic_order is not None or ney.location != "Belgium"


class TestTheTypedRouteThroughTheEndpoint:
    """R2-F1's own repro, through POST /command with the mock parser."""

    @pytest.mark.parametrize("text", [
        "Ney, march to Paris",
        "Ney, advance to Rhineland",
        "Ney, hold Belgium",
        "Ney, pursue Mack",
    ])
    def test_a_strategic_order_is_refused_and_nothing_moves(self, text):
        world, ney, mack, ask = _adjacent_geometry()
        ap = world.actions_remaining
        with _served(world) as client, _quiet():
            reply = client.post("/command", json={"command": text}).json()
        assert reply.get("success") is False, reply.get("message")
        assert "fight to the last" in (reply.get("message") or ""), reply.get("message")
        assert reply.get("last_stand_pending") is True, "the marker is on the wire"
        assert ney.pending_interrupt is ask
        assert ney.strategic_order is None
        assert ney.location == "Belgium"
        assert world.actions_remaining == ap
        assert _rail_rows(world, "Ney"), "the rail row survives"

    def test_a_co_located_pursue_never_fights_in_the_player_phase(self):
        """R1-F3(ii): the attack ran under `_strategic_execution`, Ney
        broke, and FA-1's "no word came" resolution fired on the player's
        own order. The gate closes it before any attack is dispatched."""
        world, ney, mack, ask = _cornered_ney()  # Mack CO-LOCATED at Belgium
        ney.morale = 20
        world.calculate_visibility()
        fates = []
        combat = CommandExecutor()._combat
        real = combat.__class__._check_marshal_fate

        def spy(self, marshal, enemy, w):
            fates.append(marshal.name)
            return real(self, marshal, enemy, w)
        with _served(world) as client, _quiet(), \
                pytest.MonkeyPatch.context() as mp:
            mp.setattr(combat.__class__, "_check_marshal_fate", spy)
            reply = client.post("/command", json={"command": "Ney, pursue Mack"}).json()
        assert reply.get("success") is False
        assert "fight to the last" in (reply.get("message") or "")
        assert fates == [], "a battle was fought on a cornered marshal's order"
        assert not getattr(world, "battles_this_turn", None)
        assert ney.pending_interrupt is ask
        assert not getattr(ney, "captured_by", "")

    def test_the_answers_still_route_before_the_gate(self):
        world, ney, mack, ask = _cornered_ney()
        with _served(world) as client, _quiet():
            reply = client.post("/command", json={"command": "fight to the last"}).json()
        assert ney.pending_interrupt is None, reply.get("message")
        assert "last stand" in (reply.get("message") or "").lower()

    def test_berthier_names_the_two_words_instead_of_scout_or_defend(self):
        """R2-F7: a parse failure addressed to a cornered marshal offered
        orders the gate would refuse."""
        world, ney, mack, ask = _adjacent_geometry()
        with _served(world) as client, _quiet():
            reply = client.post("/command", json={"command": "Ney, cut your way out"}).json()
        msg = reply.get("message") or ""
        assert reply.get("success") is False
        assert "fight to the last" in msg and "attempt a breakout" in msg, msg
        assert "scout" not in msg and "Might you mean" not in msg, msg
        assert reply.get("last_stand_pending") is True
        assert ney.pending_interrupt is ask


# ═══════════════════════════════════════════════════════════════════════
# The un-addressed rosters
# ═══════════════════════════════════════════════════════════════════════

class TestTheGeneralRetreatLeavesHimStanding:
    """R2-F2: `retreat` carried no marshal, so the gate never saw it, and
    it walked the cornered marshal out — 0 lost, 0 AP, ask standing."""

    def _board(self):
        world, ney, mack, ask = _adjacent_geometry()
        # Davout shares Belgium with Ney: both adjacent to Mack at Rhineland,
        # both "in danger", only one of them owes an answer.
        davout = MarshalFactory.infantry(name="Davout", location="Belgium",
                                         strength=20000, personality="cautious")
        world.marshals["Davout"] = davout
        world._build_marshal_index()
        world.calculate_visibility()
        assert world.is_in_danger("Ney") and world.is_in_danger("Davout")
        return world, ney, davout, ask

    def test_the_others_retreat_and_he_stays(self):
        world, ney, davout, ask = self._board()
        with _quiet():
            result = CommandExecutor().execute(
                {"command": {"action": "retreat", "type": "general_retreat"}},
                {"world": world})
        assert result["success"] is True, result
        assert davout.location != "Belgium", "the general retreat still moves the rest"
        assert ney.location == "Belgium"
        assert ney.pending_interrupt is ask
        assert "fight to the last" in result["message"], result["message"]
        assert "Ney" in result["message"]

    def test_alone_he_is_named_and_nothing_moves(self):
        world, ney, _mack, ask = _adjacent_geometry()
        with _quiet():
            result = CommandExecutor().execute(
                {"command": {"action": "retreat", "type": "general_retreat"}},
                {"world": world})
        assert result["success"] is False
        assert result.get("last_stand_pending") is True
        assert "leaves him where he stands" in result["message"], result["message"]
        assert ney.location == "Belgium" and ney.pending_interrupt is ask

    def test_the_typed_bare_retreat_reaches_the_same_arm(self):
        world, ney, _mack, ask = _adjacent_geometry()
        with _served(world) as client, _quiet():
            reply = client.post("/command", json={"command": "retreat"}).json()
        assert ney.location == "Belgium", reply.get("message")
        assert ney.pending_interrupt is ask
        assert "fight to the last" in (reply.get("message") or ""), reply.get("message")

    def test_the_lever_down_walks_him_out(self, monkeypatch):
        monkeypatch.setattr(strategic_mod, "STANDALONE_DECISION_LIVENESS_ACTIVE", False)
        world, ney, _mack, ask = _adjacent_geometry()
        with _quiet():
            result = CommandExecutor().execute(
                {"command": {"action": "retreat", "type": "general_retreat"}},
                {"world": world})
        assert result["success"] is True and ney.location != "Belgium"


class TestTheBareAttackAndScoutRostersSkipHim:

    def test_a_bare_attack_never_picks_the_cornered_man(self):
        """Ney alone is in contact; a bare `attack` used to be his."""
        world, ney, mack, ask = _cornered_ney()
        combat = CommandExecutor()._combat
        ready, _out, filtered = combat._scan_general_attack_candidates(world)
        assert all(m.name != "Ney" for m, _e, _d in ready), ready
        assert any("Ney" in f and "awaits your word" in f for f in filtered), filtered

    def test_the_auto_scout_roster_skips_him(self):
        """Ney is the ONLY marshal in scout range of Rhineland (Davout at
        Paris is two hops off); the bare scout must not be his."""
        world, ney, mack, ask = _adjacent_geometry()
        davout = MarshalFactory.infantry(name="Davout", location="Paris",
                                         strength=20000, personality="cautious")
        world.marshals["Davout"] = davout
        world._build_marshal_index()
        ap = world.actions_remaining
        with _quiet():
            result = CommandExecutor().execute(
                {"command": {"action": "scout", "target": "Rhineland",
                             "type": "auto_assign_scout"}}, {"world": world})
        msg = result.get("message") or ""
        assert "Ney" not in msg, msg
        assert ney.pending_interrupt is ask
        if result.get("success"):
            assert "Davout" in msg, msg
        else:
            assert world.actions_remaining == ap


# ═══════════════════════════════════════════════════════════════════════
# Liveness: the question is about HIM, not about Mack
# ═══════════════════════════════════════════════════════════════════════

class TestLivenessReKeysToTheCurrentBesieger:

    def test_a_replacement_on_him_keeps_the_question_live(self):
        """R1-F4: Mack draws off to Vienna; Charles now stands ON Ney."""
        world, ney, mack, ask = _cornered_ney(enemy_location="Vienna")
        charles = MarshalFactory.enemy(name="ArchdukeCharles", location="Belgium",
                                       nation="Austria", strength=40000)
        world.marshals["ArchdukeCharles"] = charles
        world._build_marshal_index()
        world.calculate_visibility()
        live, reason = last_stand_is_live(ney, world, ask)
        assert live is True, reason
        assert ask["enemy"] == "ArchdukeCharles" and ask["enemy_nation"] == "Austria"

    def test_an_adjacent_replacement_counts_too_and_the_nearer_wins(self):
        world, ney, mack, ask = _cornered_ney(enemy_location="Vienna")
        near = MarshalFactory.enemy(name="Hiller", location="Rhineland",
                                    nation="Austria", strength=12000)
        on = MarshalFactory.enemy(name="ArchdukeCharles", location="Belgium",
                                  nation="Austria", strength=9000)
        world.marshals["Hiller"] = near
        world.marshals["ArchdukeCharles"] = on
        world._build_marshal_index()
        world.calculate_visibility()
        assert current_besieger(ney, world, exclude="Mack").name == "ArchdukeCharles"
        live, _ = last_stand_is_live(ney, world, ask)
        assert live and ask["enemy"] == "ArchdukeCharles"

    def test_nobody_on_or_beside_him_still_retires(self):
        world, ney, mack, ask = _cornered_ney(enemy_location="Vienna")
        world.calculate_visibility()
        live, reason = last_stand_is_live(ney, world, ask)
        assert live is False and "drawn off" in reason
        assert ask["enemy"] == "Mack", "no re-key without a besieger"

    def test_the_retirement_reason_never_names_an_unscouted_province(self):
        """`get_marshal` is omniscient; the reason must not be. Vienna is
        unscouted on this fixture; Lyon is French soil and may be named."""
        world, ney, mack, ask = _cornered_ney(enemy_location="Vienna")
        world.calculate_visibility()
        _live, reason = last_stand_is_live(ney, world, ask)
        assert "Vienna" not in reason and "out of sight" in reason, reason
        mack.location = "Lyon"
        world._build_marshal_index()
        world.calculate_visibility()
        _live, reason = last_stand_is_live(ney, world, ask)
        assert "drawn off to Lyon" in reason, reason

    def test_a_court_at_peace_is_not_a_besieger(self):
        world, ney, mack, ask = _cornered_ney(enemy_location="Vienna")
        neutral = MarshalFactory.enemy(name="Blucher", location="Belgium",
                                       nation="Prussia", strength=30000)
        world.marshals["Blucher"] = neutral
        # The legacy fixture boots every court at WAR; make Prussia's peace
        # explicit, which is the case under test.
        world.diplomatic_states["France|Prussia"] = "PEACE"
        world.invalidate_active_nations_cache()
        world._build_marshal_index()
        world.calculate_visibility()
        assert not world.is_at_war("France", "Prussia")
        assert current_besieger(ney, world, exclude="Mack") is None
        live, _ = last_stand_is_live(ney, world, ask)
        assert live is False

    def test_the_answer_fights_the_man_who_is_actually_there(self):
        world, ney, mack, ask = _cornered_ney(enemy_location="Vienna")
        charles = MarshalFactory.enemy(name="ArchdukeCharles", location="Belgium",
                                       nation="Austria", strength=40000)
        world.marshals["ArchdukeCharles"] = charles
        world._build_marshal_index()
        world.calculate_visibility()
        before_mack, before_charles = mack.strength, charles.strength
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            result = proc.handle_response("Ney", "last_stand", "fight_to_the_last",
                                          world, {"world": world})
        assert result["success"] is True and not result.get("decision_retired"), result
        assert charles.strength < before_charles, "the last stand bled the besieger"
        assert mack.strength == before_mack


# ═══════════════════════════════════════════════════════════════════════
# Step 0a re-validates; the muster is re-validated
# ═══════════════════════════════════════════════════════════════════════

class TestStepZeroARunsLiveness:

    def test_a_dead_question_on_an_ordered_marshal_is_retired(self):
        """R2-F4: the ordered roster never ran liveness — the popup came
        back every turn, context-free, over a frozen order."""
        world, ney, mack, ask = _cornered_ney(enemy_location="Vienna", order=True)
        world.calculate_visibility()
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            reports = proc.process_strategic_orders(world, {"world": world})
        rows = [r for r in reports if r.get("marshal") == "Ney"]
        assert rows and rows[0]["order_status"] == "retired", reports
        assert rows[0].get("decision_retired") is True
        assert "drawn off" in rows[0]["message"] and "resumes next turn" in rows[0]["message"]
        assert ney.pending_interrupt is None
        assert ney.strategic_order is not None, "the order stands"
        assert not _rail_rows(world, "Ney")

    def test_a_live_question_on_an_ordered_marshal_still_asks_with_its_own_line(self):
        world, ney, mack, ask = _cornered_ney(order=True)
        world.calculate_visibility()
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            reports = proc.process_strategic_orders(world, {"world": world})
        rows = [r for r in reports if r.get("marshal") == "Ney"]
        assert rows and rows[0].get("requires_input") is True
        assert rows[0]["message"] == ask["message"]
        assert rows[0]["pending_interrupt"] is ask

    def test_an_order_bound_interrupt_is_not_touched(self):
        world, ney, mack, ask = _cornered_ney(enemy_location="Vienna", order=True)
        ney.pending_interrupt = {"interrupt_type": "contact_bad_odds", "marshal": "Ney",
                                 "options": ["attack", "go_around", "cancel"],
                                 "message": "Mack blocks the path."}
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            reports = proc.process_strategic_orders(world, {"world": world})
        rows = [r for r in reports if r.get("marshal") == "Ney"]
        assert rows and rows[0].get("requires_input") is True
        assert rows[0]["interrupt_type"] == "contact_bad_odds"


def _mustered_ney(target_location="Belgium"):
    world, ney, mack, _ask = _cornered_ney(enemy_location=target_location)
    ney.pending_interrupt = {
        "interrupt_type": "muster_confirm", "marshal": "Ney", "target": "Mack",
        "options": ["attack_anyway", "cancel_order"],
        "message": "MUSTER — Ney (3,000) vs Mack. Commit?",
    }
    world.calculate_visibility()
    return world, ney, mack


class TestTheMusterIsReValidated:

    def test_a_present_target_is_live(self):
        world, ney, mack = _mustered_ney()
        assert muster_is_live(ney, world) == (True, "")

    @pytest.mark.parametrize("mutate, expect", [
        (lambda w, n, m: setattr(m, "strength", 0), "no longer stands"),
        # Vienna is unscouted: the reason must NOT name it (fog-honest).
        (lambda w, n, m: setattr(m, "location", "Vienna"), "slipped out of contact"),
        # Lyon is French soil (seen) and not adjacent to Belgium: named.
        (lambda w, n, m: setattr(m, "location", "Lyon"), "marched to Lyon"),
        (lambda w, n, m: w.diplomatic_states.__setitem__("Austria|France", "PEACE"),
         "no longer at war"),
    ])
    def test_a_vanished_target_retires_with_its_reason(self, mutate, expect):
        world, ney, mack = _mustered_ney()
        mutate(world, ney, mack)
        world._build_marshal_index()
        world.invalidate_active_nations_cache()
        world.calculate_visibility()
        live, reason = muster_is_live(ney, world)
        assert live is False and expect in reason, reason

    def test_a_region_target_is_left_to_the_re_issue(self):
        world, ney, mack = _mustered_ney()
        ney.pending_interrupt["target"] = "Rhineland"
        assert muster_is_live(ney, world) == (True, "")

    def test_the_answer_arm_retires_a_dead_muster_instead_of_objecting_about_a_ghost(self):
        """R2-F5(B): the destroyed target answered `attack_anyway` with a
        marshal's objection about a man who no longer exists."""
        world, ney, mack = _mustered_ney()
        mack.strength = 0
        world._build_marshal_index()
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            result = proc.handle_response("Ney", "muster_confirm", "attack_anyway",
                                          world, {"world": world})
        assert result.get("decision_retired") is True, result
        assert result.get("no_action_cost") is True
        assert "muster is overtaken" in result["message"]
        assert "objects" not in result["message"]
        assert ney.pending_interrupt is None

    def test_pass_three_retires_a_dead_muster_with_a_row(self):
        world, ney, mack = _mustered_ney(target_location="Vienna")
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            reports = proc.process_strategic_orders(world, {"world": world})
        rows = [r for r in reports if r.get("marshal") == "Ney"]
        assert rows and rows[0]["order_status"] == "retired", reports
        assert rows[0]["command"] == "Muster"
        assert ney.pending_interrupt is None

    def test_a_live_muster_still_re_issues_the_attack(self):
        world, ney, mack = _mustered_ney()
        executed = []
        proc = StrategicOrderProcessor(CommandExecutor())
        proc.executor.execute = lambda cmd, gs: (executed.append(cmd) or {"success": True, "message": "x"})
        with _quiet():
            result = proc.handle_response("Ney", "muster_confirm", "attack_anyway",
                                          world, {"world": world})
        assert result == {"success": True, "message": "x"}
        assert executed and executed[0]["command"].get("_muster_confirmed") is True


# ═══════════════════════════════════════════════════════════════════════
# The end-turn soft-stop
# ═══════════════════════════════════════════════════════════════════════

class TestTheEndTurnSoftStop:

    def test_the_names_ride_beside_the_lapsing_count(self):
        world, ney, mack, ask = _cornered_ney()
        assert pending_marshal_decisions(world) == ["Ney"]
        with _served(world) as client, _quiet():
            reply = client.post("/command", json={"command": "status"}).json()
        assert reply.get("pending_marshal_decisions") == ["Ney"], sorted(reply.keys())
        assert "pending_lapsing_count" in reply

    def test_a_muster_is_not_a_decision_the_enemy_takes_for_him(self):
        world, ney, mack = _mustered_ney()
        assert pending_marshal_decisions(world) == []

    def test_a_captured_or_dead_marshal_is_not_listed(self):
        world, ney, mack, ask = _cornered_ney()
        ney.captured_by = "Austria"
        assert pending_marshal_decisions(world) == []

    def test_the_client_reads_the_field_and_gates_end_turn_on_it(self):
        src = (REPO / "godot-client/project-sovereign/scripts/main.gd").read_text(
            encoding="utf-8")
        assert 'response.get(\n\t\t\t"pending_marshal_decisions", [])' in src
        assert "_set_pending_decisions(diplo_data.get(\"pending_marshal_decisions\", []))" in src
        assert "if _current_lapsing_count > 0 or not _current_decision_names.is_empty():" in src
        assert "'fight to the last' or 'attempt a breakout'" in src

    def test_the_lever_down_lists_nobody(self, monkeypatch):
        monkeypatch.setattr(strategic_mod, "STANDALONE_DECISION_LIVENESS_ACTIVE", False)
        world, ney, mack, ask = _cornered_ney()
        assert pending_marshal_decisions(world) == []


class TestThePromotionPinIsNotVacuous:
    """R2-F6: the slice-2 endpoint pin set the enemy's strength to 0, so
    the row was RETIRED and `pending_interrupt` was never read. This is
    the live arm: the question is promoted for a headless client."""

    def test_a_live_question_is_promoted_on_the_end_turn_response(self):
        world, ney, mack, ask = _cornered_ney()
        # Keep the enemy phase from resolving it first: Austria has no
        # actions this turn, so the ask survives to pass 3.
        world.nation_actions["Austria"] = 0
        with _served(world) as client, _quiet():
            reply = client.post("/command", json={"command": "end turn"}).json()
        assert reply.get("turn_ended")
        if ney.pending_interrupt is None:
            pytest.skip("the enemy phase resolved the question first on this board")
        promoted = reply.get("pending_interrupt") or {}
        assert promoted.get("interrupt_type") == "last_stand", reply.get("strategic_reports")
        assert promoted.get("marshal") == "Ney"
        assert reply.get("requires_input") is True


# ═══════════════════════════════════════════════════════════════════════
# The AI side: the braked corps holds; the field is priced whole
# ═══════════════════════════════════════════════════════════════════════

class TestTheBrakedCorpsHolds:

    def test_an_emptied_list_holds_instead_of_falling_through(self):
        """R1-F1: the fall-through reached an attack-elsewhere the
        executor's engaged rule refuses, which wrote a two-turn cooldown."""
        world, ai, wel, ney = _engaged_pair()
        ai._attacked_targets_this_turn = {("Wellington", "Ney")}
        with _quiet():
            action, prio = ai._evaluate_marshal(wel, "Britain", world)
        assert action is None and prio == 999, action
        assert "Wellington" in ai._marshals_done_this_turn

    def test_no_cooldown_is_written_across_a_real_phase(self):
        world, ai, wel, ney = _engaged_pair(defender_strength=20000)
        world.nation_actions["Britain"] = 4
        random.seed(5)
        with _quiet():
            ai.process_nation_turn("Britain", world, {"world": world})
        assert not world.ai_failed_action_cooldowns.get("Wellington"), \
            world.ai_failed_action_cooldowns

    def test_the_lever_down_falls_through(self, monkeypatch):
        monkeypatch.setattr(enemy_mod, "P0_BRAKED_CORPS_HOLDS", False)
        world, ai, wel, ney = _engaged_pair()
        ai._attacked_targets_this_turn = {("Wellington", "Ney")}
        with _quiet():
            action, _prio = ai._evaluate_marshal(wel, "Britain", world)
        assert action is not None, "the pre-round fall-through"
        assert "Wellington" not in getattr(ai, "_marshals_done_this_turn", set())

    def test_an_unbraked_corps_is_untouched(self):
        world, ai, wel, ney = _engaged_pair()
        with _quiet():
            action, prio = ai._evaluate_marshal(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack", "target": "Ney"}


class TestTheFieldIsPricedWhole:

    def _field(self):
        """Wellington 30k vs Ney 20k + Massena 8k co-located; the pair
        (Wellington, Ney) already stamped. The real field is 28k."""
        world, ai, wel, ney = _engaged_pair(defender_strength=20000)
        wel.strength = 30000
        massena = MarshalFactory.infantry(name="Massena", location="Waterloo",
                                          strength=8000, personality="aggressive")
        world.marshals["Massena"] = massena
        world._build_marshal_index()
        ai._attacked_targets_this_turn = {("Wellington", "Ney")}
        return world, ai, wel

    def test_the_braked_corps_still_prices_the_field(self):
        world, ai, wel = self._field()
        with _quiet():
            action, _prio = ai._evaluate_marshal(wel, "Britain", world)
        assert not (action and action.get("action") == "attack"), \
            f"charged a 28,000 field priced as 8,000: {action}"

    def test_the_lever_down_charges_the_mispriced_field(self, monkeypatch):
        monkeypatch.setattr(enemy_mod, "P0_PRICES_THE_WHOLE_FIELD", False)
        world, ai, wel = self._field()
        with _quiet():
            action, _prio = ai._evaluate_marshal(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack", "target": "Massena"}


class TestTheFutilityBrakeReachesP0:
    """FA-N72's non-stub half: three failures against the same man."""

    def test_a_futile_target_is_dropped(self):
        """A 5,000-man defender is one the cautious Wellington ATTACKS
        without the brake (the lever-down pin below proves it); at 20,000
        his own ratio check retreats him and the brake is never what
        stops the blow — the first sweep found the pin inert on that
        fixture."""
        world, ai, wel, ney = _engaged_pair(defender_strength=5000)
        world.ai_attack_futility["Wellington:Ney"] = ATTACK_FUTILITY_LIMIT
        with _quiet():
            action, _prio = ai._evaluate_marshal(wel, "Britain", world)
        assert not (action and action.get("action") == "attack"
                    and action.get("target") == "Ney"), action

    def test_below_the_limit_he_still_attacks(self):
        world, ai, wel, ney = _engaged_pair(defender_strength=5000)
        world.ai_attack_futility["Wellington:Ney"] = ATTACK_FUTILITY_LIMIT - 1
        with _quiet():
            action, _prio = ai._evaluate_marshal(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack", "target": "Ney"}

    def test_the_lever_down_ignores_futility(self, monkeypatch):
        monkeypatch.setattr(enemy_mod, "P0_READS_FUTILITY", False)
        world, ai, wel, ney = _engaged_pair(defender_strength=5000)
        world.ai_attack_futility["Wellington:Ney"] = ATTACK_FUTILITY_LIMIT + 2
        with _quiet():
            action, _prio = ai._evaluate_marshal(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack", "target": "Ney"}

    def test_p4_reads_the_same_limit(self):
        src = (REPO / "backend/ai/enemy_ai.py").read_text(encoding="utf-8")
        assert "futility.get(key, 0) >= ATTACK_FUTILITY_LIMIT" in src
        assert "futility.get(key, 0) >= 3" not in src


class TestTheLeversShip:

    def test_all_are_up(self):
        assert enemy_mod.P0_BRAKED_CORPS_HOLDS is True
        assert enemy_mod.P0_PRICES_THE_WHOLE_FIELD is True
        assert enemy_mod.P0_READS_FUTILITY is True
        assert strategic_mod.STANDALONE_DECISION_LIVENESS_ACTIVE is True
