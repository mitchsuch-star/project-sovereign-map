"""Final Whole-Game Audit — slice 2, "No Word Came" (the cornered marshal).

The W6-7 last stand is a QUESTION the player owes a beaten marshal: fight to
the last, or attempt a breakout. Every row in this slice is a way that
question was asked and then never honoured.

* **FA-1** (P1) — the ask suppressed his retreat and then nothing ever
  resolved it: every further attack in the same enemy phase re-asked the
  same question and shot him again. Measured on the shipped 1805 board:
  SIX attacks in ONE phase, 8,000 -> 259 men, still standing, still "asked".
  Now a second defeat with the question standing is answered the way the
  marshal's own character would answer it — the enemy did not wait.
* **FA-16** (P2) — an ORDER-FREE parked question never reached the end-turn
  report (the processor's roster is `in_strategic_mode` marshals only), was
  never re-validated, and was finally answered turns later against an enemy
  three provinces away. And any fresh order simply marched him away over
  it — or overwrote it with a contact question.
* **FA-N13** (P2) — `cancel` on a marshal with no order destroyed the parked
  decision, charged 1 AP and -3 trust, and left the rail telling the player
  to answer it.
* **FA-N68** (P3) — a marshal DESTROYED with the question standing kept his
  CRITICAL rail row forever (capture retired it; destruction did not).
* **FA-N25** (P3) — a WON breakout teleported him four provinces to his
  capital on a docstring premise the code beside it contradicts.
* **FA-N72 / FA-35** (P2) — the enemy AI's engagement rung read neither of
  the brakes P4 carries, so a co-located corps attacked the same defender
  twice in one turn, and every corps of the nation queued on a sub-1,000
  stub while the road to the capital stood open.

Every fix sits behind a flip lever (the HOST_RULE_ACTIVE idiom) so the
ambient-series re-record can be attributed arm by arm.
"""

import contextlib
import io
import random

import pytest

from backend.commands import strategic as strategic_mod
from backend.commands.executor import CommandExecutor
from backend.commands.strategic import (
    STANDALONE_DECISION_TYPES,
    StrategicOrderProcessor,
    last_stand_is_live,
    standalone_decision,
)
from backend.models.marshal import StrategicOrder
from backend.notifications import (
    MARSHAL_LAST_STAND,
    NotificationPriority,
    create_notification,
    dismiss_marshal_ask,
)

from tests.conftest import MarshalFactory, WorldFactory


def _war(world, a="France", b="Austria"):
    key = "|".join(sorted([a, b]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn


def _ask(marshal, enemy, location=None, sovereign=False):
    """The dict `_check_marshal_fate` parks (its live shape, incl. FA-16's
    `location`)."""
    ask = {
        "interrupt_type": "last_stand",
        "marshal": marshal.name,
        "enemy": enemy.name,
        "enemy_nation": enemy.nation,
        "location": location or marshal.location,
        "options": ["fight_to_the_last", "attempt_breakout"],
        "message": (f"{marshal.name} is cornered at {marshal.location} — "
                    f"capture looms. He asks leave to fight to the last, "
                    f"or he can attempt a breakout."),
    }
    if sovereign:
        ask["sovereign"] = True
    marshal.pending_interrupt = ask
    return ask


def _rail_row(world, marshal):
    world.notifications.add(create_notification(
        notification_type=MARSHAL_LAST_STAND,
        priority=NotificationPriority.CRITICAL,
        title=f"{marshal.name} is cornered",
        message="decide his fate",
        turn_created=int(world.current_turn),
        details={"marshal": marshal.name},
    ))


def _rail_rows(world, marshal_name):
    return [n for n in world.notifications.get_pending()
            if n.get("type") == MARSHAL_LAST_STAND
            and (n.get("details") or {}).get("marshal") == marshal_name]


def _cornered_ney(enemy_location="Belgium", order=False, strength=3000):
    """Aggressive Ney at Belgium, parked last stand vs Mack, both at war."""
    ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                  strength=strength, personality="aggressive")
    mack = MarshalFactory.enemy(name="Mack", location=enemy_location,
                                nation="Austria", strength=40000)
    world = WorldFactory.with_marshals([ney, mack])
    _war(world)
    if order:
        ney.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Paris", target_type="region",
            started_turn=0, issued_turn=0, path=["Paris"],
            original_command="Ney, march to Paris")
    ask = _ask(ney, mack)
    _rail_row(world, ney)
    return world, ney, mack, ask


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


# ═══════════════════════════════════════════════════════════════════════
# The predicates
# ═══════════════════════════════════════════════════════════════════════

class TestTheStandaloneDecisionPredicates:

    def test_the_standalone_set_is_the_complement_of_order_bound(self):
        assert STANDALONE_DECISION_TYPES == {"last_stand", "muster_confirm"}
        assert not (STANDALONE_DECISION_TYPES
                    & strategic_mod.ORDER_BOUND_INTERRUPT_TYPES)

    def test_an_order_bound_interrupt_is_not_a_decision(self):
        world, ney, _mack, _ask = _cornered_ney()
        ney.pending_interrupt = {"interrupt_type": "cannon_fire",
                                 "marshal": "Ney", "options": ["investigate"]}
        assert standalone_decision(ney) is None
        ney.pending_interrupt = None
        assert standalone_decision(ney) is None

    def test_a_co_located_enemy_keeps_the_question_live(self):
        world, ney, _mack, _ask = _cornered_ney()
        assert last_stand_is_live(ney, world) == (True, "")

    def test_an_adjacent_enemy_keeps_the_question_live(self):
        world, ney, _mack, _ask = _cornered_ney(enemy_location="Rhineland")
        assert last_stand_is_live(ney, world)[0] is True

    @pytest.mark.parametrize("mutate,expect", [
        (lambda w, n, m: setattr(m, "location", "Vienna"), "drawn off"),
        (lambda w, n, m: setattr(m, "strength", 0), "no longer stands"),
        (lambda w, n, m: setattr(n, "location", "Paris"), "marched clear"),
        (lambda w, n, m: setattr(n, "strength", 0), "no longer stands"),
        (lambda w, n, m: w.diplomatic_states.__setitem__(
            "Austria|France", "PEACE"), "no longer at war"),
    ])
    def test_each_broken_premise_retires_with_its_reason(self, mutate, expect):
        world, ney, mack, _ask = _cornered_ney()
        mutate(world, ney, mack)
        live, reason = last_stand_is_live(ney, world)
        assert live is False
        assert expect in reason, reason

    def test_a_missing_location_key_is_tolerated(self):
        """Asks parked before this slice (saves, hand-built tests) carry no
        `location`; the premise is simply not checked."""
        world, ney, _mack, ask = _cornered_ney()
        ask.pop("location")
        assert last_stand_is_live(ney, world)[0] is True

    def test_the_reason_names_the_enemy_humanely(self):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=3000, personality="aggressive")
        charles = MarshalFactory.enemy(name="ArchdukeCharles", location="Vienna",
                                       nation="Austria", strength=40000)
        world = WorldFactory.with_marshals([ney, charles])
        _war(world)
        _ask(ney, charles)
        _live, reason = last_stand_is_live(ney, world)
        assert "Archduke Charles" in reason and "ArchdukeCharles" not in reason


class TestTheRailHelper:

    def test_it_retires_only_that_marshals_rows(self):
        world, ney, _mack, _ask = _cornered_ney()
        other = MarshalFactory.infantry(name="Davout", location="Paris",
                                        personality="cautious")
        world.marshals["Davout"] = other
        _rail_row(world, other)
        assert dismiss_marshal_ask(world, "Ney") == 1
        assert _rail_rows(world, "Ney") == []
        assert len(_rail_rows(world, "Davout")) == 1

    def test_a_world_without_a_rail_is_harmless(self):
        class Bare:
            pass
        assert dismiss_marshal_ask(Bare(), "Ney") == 0


# ═══════════════════════════════════════════════════════════════════════
# FA-16 — an order-free question reaches the end turn, or is retired
# ═══════════════════════════════════════════════════════════════════════

class TestAnOrderFreeQuestionReachesTheEndTurn:

    def test_the_processor_emits_the_row(self):
        world, ney, _mack, ask = _cornered_ney()
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            reports = proc.process_strategic_orders(world, {"world": world})
        rows = [r for r in reports if r.get("marshal") == "Ney"]
        assert len(rows) == 1, reports
        row = rows[0]
        assert row["requires_input"] is True
        assert row["interrupt_type"] == "last_stand"
        assert row["order_status"] == "awaiting_response"
        assert set(row["options"]) == {"fight_to_the_last", "attempt_breakout"}
        # The ask's OWN line, not step 0a's "awaits your orders" (FA-N60's
        # end-turn half): the popup body is what the marshal actually said.
        assert row["message"] == ask["message"]
        assert row["pending_interrupt"] is ask
        assert ney.pending_interrupt is ask, "surfacing never consumes"

    def test_an_ordered_marshal_is_not_reported_twice(self):
        """Step 0a already owns the order-bound roster; pass 3 must not
        duplicate his row."""
        world, ney, _mack, _ask = _cornered_ney(order=True)
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            reports = proc.process_strategic_orders(world, {"world": world})
        rows = [r for r in reports if r.get("marshal") == "Ney"]
        assert len(rows) == 1
        assert rows[0]["requires_input"] is True

    def test_a_muster_confirm_is_surfaced_too(self):
        world, ney, mack, _ask = _cornered_ney()
        ney.pending_interrupt = {
            "interrupt_type": "muster_confirm", "marshal": "Ney",
            "target": "Mack", "options": ["attack_anyway", "cancel_order"],
            "message": "MUSTER — Ney (3,000) vs Mack. Commit?",
        }
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            reports = proc.process_strategic_orders(world, {"world": world})
        rows = [r for r in reports if r.get("marshal") == "Ney"]
        assert rows and rows[0]["interrupt_type"] == "muster_confirm"
        assert rows[0]["requires_input"] is True

    def test_a_marshal_without_a_question_gets_no_row(self):
        world, ney, _mack, _ask = _cornered_ney()
        ney.pending_interrupt = None
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            reports = proc.process_strategic_orders(world, {"world": world})
        assert not [r for r in reports if r.get("marshal") == "Ney"]

    def test_the_end_turn_response_promotes_it_for_headless_clients(self):
        """Through the real endpoint: the row rides `strategic_reports`
        (the client's flow) AND is promoted to `pending_interrupt` (the
        driver's and every scripted client's)."""
        from fastapi.testclient import TestClient
        import backend.main as M
        from backend.commands.parser import CommandParser

        world, ney, mack, _ask = _cornered_ney()
        # Keep Mack from finishing him in the enemy phase: the question is
        # what this test is about, not the battle.
        mack.strength = 0
        mack.location = "Vienna"
        saved = (M.world, M.game_state, M.parser)
        M.world = world
        M.game_state = {"world": world}
        M.parser = CommandParser(use_real_llm=False)
        try:
            assert M.parser.llm.use_real_api is False
            with _quiet():
                reply = TestClient(M.app).post(
                    "/command", json={"command": "end turn"}).json()
        finally:
            M.world, M.game_state, M.parser = saved
        assert reply.get("turn_ended")
        rows = [r for r in reply.get("strategic_reports") or []
                if r.get("marshal") == "Ney"]
        # Mack drew off, so the FIRST end turn retires the question with a
        # reason rather than raising it — the retirement is a report too.
        assert rows and rows[0]["order_status"] == "retired", reply
        assert "drawn off" in rows[0]["message"] or "no longer stands" in rows[0]["message"]


class TestAStaleQuestionIsRetiredNotFought:

    def test_the_processor_retires_it_with_the_reason(self):
        world, ney, mack, _ask = _cornered_ney(enemy_location="Vienna")
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            reports = proc.process_strategic_orders(world, {"world": world})
        rows = [r for r in reports if r.get("marshal") == "Ney"]
        assert rows and rows[0]["order_status"] == "retired"
        assert rows[0]["decision_retired"] is True
        assert "drawn off" in rows[0]["message"]
        assert not rows[0].get("requires_input")
        assert ney.pending_interrupt is None
        assert _rail_rows(world, "Ney") == []

    def test_the_answer_arm_refuses_to_fight_a_ghost(self):
        """FA-16's sharpest measured harm: 'fight to the last' bled an enemy
        three provinces away by 7,500 men and then jailed the marshal."""
        world, ney, mack, _ask = _cornered_ney(enemy_location="Vienna")
        before = mack.strength
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            result = proc.handle_response("Ney", "last_stand",
                                          "fight_to_the_last", world,
                                          {"world": world})
        assert result["success"] is True
        assert result.get("decision_retired") is True
        assert result.get("no_action_cost") is True
        assert "drawn off" in result["message"]
        assert mack.strength == before
        assert ney.captured_by == ""
        assert ney.pending_interrupt is None
        assert _rail_rows(world, "Ney") == []

    def test_a_live_question_still_resolves(self):
        """Control: co-located, at war — the answer still fights."""
        world, ney, mack, _ask = _cornered_ney()
        before = mack.strength
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            result = proc.handle_response("Ney", "last_stand",
                                          "fight_to_the_last", world,
                                          {"world": world})
        assert "LAST STAND" in result["message"]
        assert mack.strength < before
        assert ney.captured_by == "Austria"
        assert _rail_rows(world, "Ney") == []

    def test_an_invalid_choice_is_still_refused_first(self):
        world, ney, _mack, ask = _cornered_ney(enemy_location="Vienna")
        proc = StrategicOrderProcessor(CommandExecutor())
        result = proc.handle_response("Ney", "last_stand", "surrender",
                                      world, {"world": world})
        assert result["success"] is False
        assert ney.pending_interrupt is ask


# ═══════════════════════════════════════════════════════════════════════
# FA-16 — no other order reaches a cornered marshal
# ═══════════════════════════════════════════════════════════════════════

class TestNoOtherOrderReachesACorneredMarshal:

    @pytest.mark.parametrize("command", [
        {"marshal": "Ney", "action": "move", "target": "Paris"},
        {"marshal": "Ney", "action": "attack", "target": "Mack"},
        {"marshal": "Ney", "action": "fortify"},
        {"marshal": "Ney", "action": "retreat"},
    ])
    def test_the_order_is_refused_free_and_names_the_answers(self, command):
        world, ney, _mack, ask = _cornered_ney()
        ap = world.actions_remaining
        trust = ney.trust.value
        with _quiet():
            result = CommandExecutor().execute({"command": command},
                                               {"world": world})
        assert result["success"] is False
        assert result.get("last_stand_pending") is True
        assert "fight to the last" in result["message"]
        assert "attempt a breakout" in result["message"]
        assert ney.pending_interrupt is ask
        assert ney.location == "Belgium"
        assert world.actions_remaining == ap
        assert ney.trust.value == trust

    def test_cancel_is_the_one_exempt_verb(self):
        world, ney, _mack, ask = _cornered_ney()
        with _quiet():
            result = CommandExecutor().execute(
                {"command": {"marshal": "Ney", "action": "cancel"}},
                {"world": world})
        assert result["success"] is True
        assert result.get("last_stand_pending") is None
        assert ney.pending_interrupt is ask

    def test_another_marshal_is_untouched(self):
        world, ney, _mack, ask = _cornered_ney()
        davout = MarshalFactory.infantry(name="Davout", location="Paris",
                                         personality="cautious")
        world.marshals["Davout"] = davout
        with _quiet():
            result = CommandExecutor().execute(
                {"command": {"marshal": "Davout", "action": "move",
                             "target": "Normandy"}},
                {"world": world})
        assert result["success"] is True, result
        assert davout.location == "Normandy"
        assert ney.pending_interrupt is ask

    def test_strategic_execution_is_exempt(self):
        """The processor's own steps are not player orders; step 0a already
        holds an ordered marshal with a question."""
        world, ney, _mack, ask = _cornered_ney()
        with _quiet():
            result = CommandExecutor().execute(
                {"command": {"marshal": "Ney", "action": "move",
                             "target": "Paris", "_strategic_execution": True}},
                {"world": world})
        assert result.get("last_stand_pending") is None
        assert ney.location == "Paris"

    def test_the_lever_reproduces_the_prior_behaviour(self, monkeypatch):
        """False = the pre-slice world: the move executes over the question
        and the processor emits nothing for an order-free marshal."""
        monkeypatch.setattr(strategic_mod,
                            "STANDALONE_DECISION_LIVENESS_ACTIVE", False)
        world, ney, _mack, ask = _cornered_ney()
        with _quiet():
            result = CommandExecutor().execute(
                {"command": {"marshal": "Ney", "action": "move",
                             "target": "Paris"}},
                {"world": world})
        assert result["success"] is True
        assert ney.location == "Paris"
        assert ney.pending_interrupt is ask
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            reports = proc.process_strategic_orders(world, {"world": world})
        assert not [r for r in reports if r.get("marshal") == "Ney"]


# ═══════════════════════════════════════════════════════════════════════
# FA-N13 — cancel never destroys a parked decision
# ═══════════════════════════════════════════════════════════════════════

class TestCancelNeverDestroysAParkedDecision:

    def test_a_parked_last_stand_survives_cancel_free(self):
        world, ney, _mack, ask = _cornered_ney()
        ap = world.actions_remaining
        trust = ney.trust.value
        with _quiet():
            result = CommandExecutor().execute(
                {"command": {"marshal": "Ney", "action": "cancel"}},
                {"world": world})
        assert result["success"] is True
        assert result.get("no_action_cost") is True
        assert "fight to the last" in result["message"]
        assert "attempt a breakout" in result["message"]
        assert ney.pending_interrupt is ask
        assert world.actions_remaining == ap
        assert ney.trust.value == trust
        assert len(_rail_rows(world, "Ney")) == 1

    def test_a_parked_muster_survives_cancel_free(self):
        world, ney, _mack, _ask = _cornered_ney()
        muster = {"interrupt_type": "muster_confirm", "marshal": "Ney",
                  "target": "Mack",
                  "options": ["attack_anyway", "cancel_order"]}
        ney.pending_interrupt = muster
        with _quiet():
            result = CommandExecutor().execute(
                {"command": {"marshal": "Ney", "action": "cancel"}},
                {"world": world})
        assert result["success"] is True
        assert result.get("no_action_cost") is True
        assert "attack anyway" in result["message"]
        assert ney.pending_interrupt is muster

    def test_a_stale_bound_interrupt_with_no_order_dies_free(self):
        """The other order-free shape: a contact question whose order is
        already gone. It is stale by definition and goes at no cost."""
        world, ney, _mack, _ask = _cornered_ney()
        ney.pending_interrupt = {"interrupt_type": "contact_bad_odds",
                                 "marshal": "Ney", "enemy": "Mack",
                                 "options": ["attack_anyway", "cancel_order"]}
        ap = world.actions_remaining
        with _quiet():
            result = CommandExecutor().execute(
                {"command": {"marshal": "Ney", "action": "cancel"}},
                {"world": world})
        assert result["success"] is True
        assert result.get("no_action_cost") is True
        assert ney.pending_interrupt is None
        assert world.actions_remaining == ap

    def test_an_ordered_cancel_still_clears_its_own_question(self):
        """Control (the existing contract): an order's cannon-fire question
        dies with the order, and mid-march cancel still costs -3."""
        world, ney, _mack, _ask = _cornered_ney(order=True)
        ney.pending_interrupt = {"interrupt_type": "cannon_fire",
                                 "marshal": "Ney",
                                 "options": ["investigate", "continue_order"]}
        trust = ney.trust.value
        with _quiet():
            result = CommandExecutor().execute(
                {"command": {"marshal": "Ney", "action": "cancel"}},
                {"world": world})
        assert result["success"] is True
        assert ney.strategic_order is None
        assert ney.pending_interrupt is None
        assert ney.trust.value == trust - 3

    def test_an_ordered_cancel_keeps_a_standalone_decision(self):
        world, ney, _mack, ask = _cornered_ney(order=True)
        with _quiet():
            CommandExecutor().execute(
                {"command": {"marshal": "Ney", "action": "cancel"}},
                {"world": world})
        assert ney.strategic_order is None
        assert ney.pending_interrupt is ask



# ═══════════════════════════════════════════════════════════════════════
# FA-1 — no word came: a second defeat with the question standing
# ═══════════════════════════════════════════════════════════════════════

def _fate_world(personality="aggressive", strength=3000, home_soil=False):
    """A cornered player marshal (Weak) with a standing last-stand ask,
    facing Monster, on soil whose ownership decides the deterministic arm.

    Belgium is France's own in the legacy fixture (home soil -> the fight);
    the breakout arm needs foreign, not-at-war soil whose neighbours are
    ALL at-war Austrian, so the only retreat is desperation soil."""
    from backend.commands.strategic import clear_order_bound_interrupt  # noqa: F401
    # Belgium is French home soil AND adjacent to Paris: the fight arm.
    # Milan is neither (its neighbours are Lyon/Marseille/Tyrol/Vienna): the
    # breakout arm, once it is foreign-but-not-at-war soil ringed by at-war
    # Austrian provinces, so the only retreat is desperation soil.
    location = "Belgium" if home_soil else "Milan"
    weak = MarshalFactory.infantry(name="Weak", location=location,
                                   strength=strength, personality=personality)
    monster = MarshalFactory.enemy(name="Monster", location=location,
                                   nation="Austria", strength=80000,
                                   personality="cautious")
    world = WorldFactory.with_marshals([weak, monster])
    _war(world)
    if not home_soil:
        world.nation_starting_regions["France"] = [
            r for r in world.nation_starting_regions.get("France", [])
            if r != "Milan"]
        world.regions["Milan"].controller = "Netherlands"
        for r in world.regions["Milan"].adjacent_regions:
            world.regions[r].controller = "Austria"
    return world, weak, monster


class TestNoWordCame:

    def test_the_first_defeat_still_asks(self):
        """Control: the W6-7 promise stands — the FIRST time he is cornered
        the player is asked, and the ask now records where."""
        world, weak, monster = _fate_world()
        combat = CommandExecutor()._combat
        with _quiet():
            msg = combat._check_marshal_fate(weak, monster, world)
        assert "CORNERED" in msg
        ask = weak.pending_interrupt
        assert ask["interrupt_type"] == "last_stand"
        assert ask["location"] == weak.location == "Milan"
        assert weak.captured_by == ""

    def test_a_second_defeat_on_home_soil_is_the_last_stand(self):
        world, weak, monster = _fate_world(home_soil=True)
        combat = CommandExecutor()._combat
        with _quiet():
            combat._check_marshal_fate(weak, monster, world)
        _rail_row(world, weak)
        before = monster.strength
        with _quiet():
            msg = combat._check_marshal_fate(weak, monster, world)
        assert msg is not None and "No word came" in msg, msg
        assert "LAST STAND" in msg
        assert monster.strength < before, "he bled the enemy on the way out"
        assert weak.captured_by == "Austria"
        assert weak.pending_interrupt is None
        assert _rail_rows(world, "Weak") == []

    def test_a_second_defeat_off_home_soil_rolls_the_breakout(self):
        outcomes = set()
        for seed in range(16):
            world, weak, monster = _fate_world()
            combat = CommandExecutor()._combat
            with _quiet():
                combat._check_marshal_fate(weak, monster, world)
            assert weak.pending_interrupt, "fixture: the first defeat must ask"
            _rail_row(world, weak)
            random.seed(seed)
            with _quiet():
                msg = combat._check_marshal_fate(weak, monster, world)
            assert msg is not None and "No word came" in msg, msg
            assert weak.pending_interrupt is None, "never re-asked"
            # The breakout arm is the one road where nothing else clears the
            # question (capture clears it itself): the retirement must be
            # the resolution's own.
            assert _rail_rows(world, "Weak") == []
            if weak.captured_by:
                outcomes.add("captured")
                assert weak.strength == 0
            else:
                outcomes.add("escaped")
                assert weak.location != "Milan", "a won breakout LEAVES"
                assert weak.retreating is True
        assert outcomes == {"captured", "escaped"}

    def test_he_is_never_shot_a_third_time_standing(self):
        """The grind itself: whatever the roll, after the second defeat he
        is either a prisoner or off the field — never standing at the
        battle region with a fresh question."""
        for seed in range(8):
            world, weak, monster = _fate_world()
            combat = CommandExecutor()._combat
            with _quiet():
                combat._check_marshal_fate(weak, monster, world)
            random.seed(seed)
            with _quiet():
                combat._check_marshal_fate(weak, monster, world)
            standing_at_bay = (weak.location == "Milan"
                               and weak.strength > 0
                               and not weak.captured_by)
            assert not standing_at_bay
            assert not (weak.pending_interrupt or {}).get("interrupt_type") == "last_stand"

    def test_the_road_opening_retires_the_question_and_he_retreats(self):
        """A standing ask whose premise is gone: a safe retreat now exists,
        so the normal forced retreat is his answer, the question is retired,
        and the retreat line says so."""
        world, weak, monster = _fate_world(home_soil=True, strength=20000)
        # Park the question by hand (he is strong; the gate would not ask).
        _ask(weak, monster)
        _rail_row(world, weak)
        combat = CommandExecutor()._combat
        with _quiet():
            msg = combat._apply_forced_retreat_or_break(weak, monster, world)
        assert "overtaken" in msg and "road has opened" in msg, msg
        assert weak.location != "Belgium"
        assert weak.pending_interrupt is None
        assert _rail_rows(world, "Weak") == []
        assert getattr(weak, "_fate_note", "") == "", "read once, then cleared"

    def test_an_ai_marshal_is_untouched_by_the_player_rule(self):
        """GR5 boundary: the ask is player-only, so an AI marshal never
        carries one and the new arm is unreachable for him — the AI's own
        deterministic rule still resolves him in ONE battle."""
        weak = MarshalFactory.enemy(name="Mack", location="Belgium",
                                    nation="Austria", strength=3000,
                                    personality="aggressive")
        hunter = MarshalFactory.infantry(name="Ney", location="Belgium",
                                         strength=80000)
        world = WorldFactory.with_marshals([weak, hunter])
        _war(world)
        random.seed(3)
        with _quiet():
            msg = CommandExecutor()._combat._check_marshal_fate(weak, hunter, world)
        assert weak.pending_interrupt is None
        assert msg is None or "No word came" not in msg

    def test_the_sovereign_encircled_fights_the_guards_last_stand(self):
        # NP-0: sovereignty is derived from the personality string.
        emperor = MarshalFactory.infantry(name="Napoleon", location="Belgium",
                                          strength=3000, personality="sovereign")
        assert emperor.is_sovereign
        monster = MarshalFactory.enemy(name="Monster", location="Belgium",
                                       nation="Austria", strength=80000)
        world = WorldFactory.with_marshals([emperor, monster])
        _war(world)
        combat = CommandExecutor()._combat
        # Encircle him: every neighbour holds an at-war enemy corps.
        for i, r in enumerate(world.regions["Belgium"].adjacent_regions):
            world.marshals[f"Ring{i}"] = MarshalFactory.enemy(
                name=f"Ring{i}", location=r, nation="Austria", strength=20000)
        with _quiet():
            first = combat._check_marshal_fate(emperor, monster, world)
        assert first is not None and "ENCIRCLED" in first
        assert emperor.pending_interrupt["sovereign"] is True
        before = monster.strength
        with _quiet():
            second = combat._check_marshal_fate(emperor, monster, world)
        assert second is not None and "No word came" in second
        assert "LAST STAND" in second
        assert monster.strength < before
        assert emperor.captured_by == "Austria"

    def test_the_lever_reproduces_the_grind(self):
        """False = the pre-slice world: the second defeat re-asks and he
        stays standing where he was shot."""
        world, weak, monster = _fate_world()
        combat = CommandExecutor()._combat
        with _quiet():
            combat._check_marshal_fate(weak, monster, world)
        first_ask = weak.pending_interrupt
        try:
            type(combat).LAST_STAND_UNANSWERED_RESOLVES = False
            random.seed(1)
            with _quiet():
                msg = combat._check_marshal_fate(weak, monster, world)
        finally:
            type(combat).LAST_STAND_UNANSWERED_RESOLVES = True
        assert "CORNERED" in msg and "No word came" not in msg
        assert weak.location == "Milan" and weak.captured_by == ""
        assert weak.pending_interrupt is not first_ask, "re-asked, not resolved"

    def test_the_grind_is_over_on_the_shipped_board(self):
        """The row's own measurement, through the REAL enemy phase: Massena
        cornered at Milan by three co-located Austrian corps. Before: six
        attacks, 8,000 -> 259, still standing. After: he is resolved by the
        second defeat at the latest, and the nation's remaining actions go
        elsewhere."""
        import os
        from backend.ai.enemy_ai import EnemyAI
        from backend.models.world_state import WorldState

        os.environ.pop("SOVEREIGN_SCENARIO", None)
        with _quiet():
            w = WorldState.from_scenario(
                "godot-client/project-sovereign/assets/maps/europe_1805.json")
        massena = w.get_marshal("Massena")
        massena.location = "Milan"
        massena.strength = 8000
        massena.morale = 30
        for name in ("Mack", "ArchdukeCharles", "ArchdukeJohn"):
            w.get_marshal(name).location = "Milan"
        # Every French neighbour of Milan flips Austrian: tier-5 only.
        milan = w.get_region("Milan")
        for r in milan.adjacent_regions:
            region = w.get_region(r)
            if region and region.controller == "France":
                region.controller = "Austria"
        for m in w.get_player_marshals():
            if m.name != "Massena":
                m.location = "Paris"
        w.invalidate_active_nations_cache()
        w._build_marshal_index()
        w.calculate_visibility()
        random.seed(7)
        ai = EnemyAI(CommandExecutor())
        with _quiet():
            actions = ai.process_nation_turn("Austria", w, {"world": w})
        on_massena = [a for a in actions
                      if a.get("ai_action", {}).get("target") == "Massena"]
        assert len(on_massena) <= 2, [a.get("ai_action") for a in actions]
        assert not (massena.location == "Milan" and massena.strength > 0
                    and not massena.captured_by), (
            massena.location, massena.strength, massena.captured_by)


# ═══════════════════════════════════════════════════════════════════════
# FA-N68 — destruction retires the rail row
# ═══════════════════════════════════════════════════════════════════════

class TestDestructionRetiresTheRow:

    def test_destroy_marshal_retires_his_ask_row(self):
        world, ney, _mack, _ask = _cornered_ney()
        assert len(_rail_rows(world, "Ney")) == 1
        with _quiet():
            removed = world.destroy_marshal(ney, cause="battle", victor="Austria")
        assert removed is True
        assert _rail_rows(world, "Ney") == []

    def test_it_leaves_other_marshals_rows_alone(self):
        world, ney, _mack, _ask = _cornered_ney()
        davout = MarshalFactory.infantry(name="Davout", location="Paris",
                                         personality="cautious")
        world.marshals["Davout"] = davout
        _rail_row(world, davout)
        with _quiet():
            world.destroy_marshal(ney, cause="battle", victor="Austria")
        assert len(_rail_rows(world, "Davout")) == 1

    def test_capture_still_retires_it_through_the_same_helper(self):
        world, ney, _mack, _ask = _cornered_ney()
        with _quiet():
            world.capture_marshal(ney, "Austria")
        assert _rail_rows(world, "Ney") == []
        assert ney.pending_interrupt is None


# ═══════════════════════════════════════════════════════════════════════
# FA-N25 — a won breakout falls back one province, not four
# ═══════════════════════════════════════════════════════════════════════

class TestABreakoutFallsBackOneProvince:

    def test_with_a_safe_retreat_he_takes_it(self):
        """Ney at Belgium with French Paris one hop away: the breakout goes
        to Paris (the producer's own answer), not to `find_safe_spawn`."""
        world, ney, mack, _ask = _cornered_ney(strength=4000)
        ney.spawn_location = "Bordeaux"
        expected = world.get_safe_retreat_destination("Ney", mack.location)
        assert expected is not None
        assert expected in world.regions["Belgium"].adjacent_regions
        with _quiet():
            msg = CommandExecutor()._combat.apply_successful_breakout(ney, mack, world)
        assert ney.location == expected
        assert expected in msg
        assert ney.retreating is True

    def test_the_march_is_charged_like_a_retreat(self):
        world, ney, mack, _ask = _cornered_ney(strength=4000)
        combat = CommandExecutor()._combat
        calls = []
        real = combat._executor._calculate_movement_attrition

        def spy(marshal, dest, w, is_retreat=False):
            calls.append((marshal.name, dest, is_retreat))
            return real(marshal, dest, w, is_retreat=is_retreat)
        combat._executor._calculate_movement_attrition = spy
        with _quiet():
            combat.apply_successful_breakout(ney, mack, world)
        assert calls and calls[0][2] is True, calls

    def test_the_encircled_arm_still_reaches_the_spawn(self):
        world, ney, mack, _ask = _cornered_ney(strength=4000)
        for i, r in enumerate(world.regions["Belgium"].adjacent_regions):
            world.marshals[f"Ring{i}"] = MarshalFactory.enemy(
                name=f"Ring{i}", location=r, nation="Austria", strength=20000)
        assert world.get_safe_retreat_destination("Ney", "Belgium") is None
        spawn = world.find_safe_spawn(ney, exclude="Belgium")
        with _quiet():
            CommandExecutor()._combat.apply_successful_breakout(ney, mack, world)
        assert ney.location == spawn

    def test_the_answer_path_uses_it(self):
        """Through `handle_response`: a won breakout lands one hop away."""
        world, ney, mack, _ask = _cornered_ney(strength=4000)
        expected = world.get_safe_retreat_destination("Ney", mack.location)
        proc = StrategicOrderProcessor(CommandExecutor())
        original = random.random
        random.random = lambda: 0.0  # the roll succeeds
        try:
            with _quiet():
                result = proc.handle_response("Ney", "last_stand",
                                              "attempt_breakout", world,
                                              {"world": world})
        finally:
            random.random = original
        assert "cuts his way out" in result["message"]
        assert ney.location == expected


# ═══════════════════════════════════════════════════════════════════════
# FA-N72 / FA-35 — the engagement rung reads the brakes
# ═══════════════════════════════════════════════════════════════════════

def _engaged_pair(defender_strength=5000):
    """Wellington (AI, Britain) co-located with Ney (player) on the legacy
    fixture, at war, Britain's turn."""
    from backend.ai.enemy_ai import EnemyAI
    from backend.models.world_state import WorldState

    world = WorldState(player_nation="France")
    wel = world.get_marshal("Wellington")
    ney = world.get_marshal("Ney")
    wel.location = "Waterloo"
    wel.strength = 24000
    ney.location = "Waterloo"
    ney.strength = defender_strength
    _war(world, "France", "Britain")
    for m in world.marshals.values():
        if m.name not in ("Wellington", "Ney") and m.location == "Waterloo":
            m.location = m.spawn_location if m.spawn_location != "Waterloo" else "Paris"
    world.invalidate_active_nations_cache()
    world._build_marshal_index()
    ai = EnemyAI(CommandExecutor())
    ai._attacked_targets_this_turn = set()
    return world, ai, wel, ney


class TestTheEngagementRungReadsTheBrakes:

    def test_brakes_clear_it_attacks(self):
        world, ai, wel, ney = _engaged_pair()
        with _quiet():
            action, prio = ai._evaluate_marshal(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack",
                          "target": "Ney"}, action
        assert prio == 0

    def test_the_pair_brake_stops_a_second_attack_this_turn(self):
        world, ai, wel, ney = _engaged_pair()
        ai._attacked_targets_this_turn = {("Wellington", "Ney")}
        with _quiet():
            action, _prio = ai._evaluate_marshal(wel, "Britain", world)
        assert not (action and action.get("action") == "attack"
                    and action.get("target") == "Ney"), action

    def test_the_p8_safety_net_reads_the_same_brake(self):
        world, ai, wel, ney = _engaged_pair()
        ai._attacked_targets_this_turn = {("Wellington", "Ney")}
        with _quiet():
            action = ai._get_default_action(wel, world)
        assert not (action and action.get("action") == "attack"
                    and action.get("target") == "Ney"), action

    def test_the_stub_latch_frees_the_rest_of_the_nation(self):
        """A second British corps arrives on a 500-man remnant one of its
        fellows already engaged this turn: it does NOT queue on the stub."""
        world, ai, wel, ney = _engaged_pair(defender_strength=500)
        second = MarshalFactory.enemy(name="Picton", location="Waterloo",
                                      nation="Britain", strength=20000,
                                      personality="aggressive")
        world.marshals["Picton"] = second
        world._build_marshal_index()
        ai._attacked_targets_this_turn = {("Wellington", "Ney")}
        with _quiet():
            action, _prio = ai._evaluate_marshal(second, "Britain", world)
        assert not (action and action.get("action") == "attack"
                    and action.get("target") == "Ney"), action

    def test_a_real_army_is_not_a_stub(self):
        """The latch is a REMNANT rule: a 5,000-man defender already engaged
        by one corps is still every other corps' business."""
        world, ai, wel, ney = _engaged_pair(defender_strength=5000)
        second = MarshalFactory.enemy(name="Picton", location="Waterloo",
                                      nation="Britain", strength=20000,
                                      personality="aggressive")
        world.marshals["Picton"] = second
        world._build_marshal_index()
        ai._attacked_targets_this_turn = {("Wellington", "Ney")}
        with _quiet():
            action, _prio = ai._evaluate_marshal(second, "Britain", world)
        assert action == {"marshal": "Picton", "action": "attack",
                          "target": "Ney"}, action

    def test_the_latch_is_nation_scoped(self):
        """Another court's pair on the same remnant is not this court's
        engagement (the autonomous player marshal reuses the tree)."""
        world, ai, wel, ney = _engaged_pair(defender_strength=500)
        foreign = MarshalFactory.enemy(name="Blucher", location="Belgium",
                                       nation="Prussia", strength=20000)
        world.marshals["Blucher"] = foreign
        world._build_marshal_index()
        ai._attacked_targets_this_turn = {("Blucher", "Ney")}
        with _quiet():
            action, _prio = ai._evaluate_marshal(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack",
                          "target": "Ney"}, action

    def test_the_lever_reproduces_the_prior_behaviour(self, monkeypatch):
        from backend.ai import enemy_ai as enemy_mod
        monkeypatch.setattr(enemy_mod, "P0_ENGAGEMENT_BRAKES_ACTIVE", False)
        world, ai, wel, ney = _engaged_pair()
        ai._attacked_targets_this_turn = {("Wellington", "Ney")}
        with _quiet():
            action, prio = ai._evaluate_marshal(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack",
                          "target": "Ney"}
        assert prio == 0

    def test_the_real_phase_never_attacks_the_same_pair_twice(self):
        """Through `process_nation_turn`: Wellington cannot be re-selected
        against Ney after his first attack in one phase."""
        world, ai, wel, ney = _engaged_pair(defender_strength=20000)
        world.nation_actions["Britain"] = 3
        random.seed(5)
        with _quiet():
            actions = ai.process_nation_turn("Britain", world, {"world": world})
        pairs = [(a["ai_action"]["marshal"], a["ai_action"].get("target"))
                 for a in actions if a.get("ai_action", {}).get("action") == "attack"]
        assert len(pairs) == len(set(pairs)), pairs


# ═══════════════════════════════════════════════════════════════════════
# The shipped configuration — measured on the ambient board
# ═══════════════════════════════════════════════════════════════════════

class TestTheLeversShipTogether:
    """The eight-arm attribution (see BASELINE_SERIES' record) measured that
    the P0 brakes WITHOUT the unanswered-ask resolution leave an immortal
    remnant: the stub latch protects a corps whose re-asked question keeps
    suppressing his retreat, so Lannes, Massena and Ney all survived the
    40-turn run at a few hundred men each. B is never shipped without A."""

    def test_brakes_never_ship_without_the_resolution(self):
        from backend.ai import enemy_ai as enemy_mod
        from backend.commands.combat_executor import CombatExecutor
        if enemy_mod.P0_ENGAGEMENT_BRAKES_ACTIVE:
            assert CombatExecutor.LAST_STAND_UNANSWERED_RESOLVES is True

    def test_all_three_levers_are_up(self):
        from backend.ai import enemy_ai as enemy_mod
        from backend.commands.combat_executor import CombatExecutor
        assert enemy_mod.P0_ENGAGEMENT_BRAKES_ACTIVE is True
        assert CombatExecutor.LAST_STAND_UNANSWERED_RESOLVES is True
        assert strategic_mod.STANDALONE_DECISION_LIVENESS_ACTIVE is True
