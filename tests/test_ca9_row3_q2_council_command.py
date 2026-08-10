"""CA9 row 3 / Q2(a) — the council command ("to my tent").

Audit record: `docs/audits/GRIEVANCE_REVISIT_INVESTIGATION_2026_08_09.md`
§5 Q2, ruled (a). `JEALOUSY_SPEC.md` deferred a "Council command" arm with
NO owner row — a GR9 orphan — while the confrontation body has always
asked for precisely that: *"He requests a command worthy of his talents."*

The audit's ROOT finding was that escalation history and level are written
only at fire time, so no petition arm can reach them: acknowledge /
no-answer / promise / rebuke all converge to the same state and differ
only in price. Every existing arm writes `jealousy_turns_remaining` and
nothing else.

This arm is different IN KIND. It gives him a named objective by issuing
an existing strategic order (PURSUE) through the shared executor, and the
grievance then ends the way the system says grievances end — on the field,
through `check_battle_resolution`'s per-personality predicate.

Sizing: no new verb, no parser row, no `VALID_ACTIONS` entry, no
serialized field, no PopupQueue slot, no campaign-log TYPE, and zero
`.gd` (the client renders the option list from data).

Everything below either pins an amendment the pre-build refutation
demanded, or a defect it measured in the first-draft design.
"""

import pytest

from backend.campaign_log import CAMPAIGN_LOG_TYPES, format_event_oneliner
from backend.commands.executor import CommandExecutor
from backend.game_logic import jealousy as J

from tests.conftest import MarshalFactory, WorldFactory


def _war(world, a="France", b="Austria"):
    key = "|".join(sorted([a, b]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn


@pytest.fixture()
def board():
    """Ney (aggressive) envious of Murat, with Mack co-located to fight.

    Co-located is deliberate: a PURSUE at an enemy in the marshal's own
    province is handled in place and never reaches
    `_handle_first_step_blocked`, which is the one second-modal path
    `objection_response` cannot suppress.
    """
    ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                  strength=30000, personality="aggressive")
    murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                    strength=30000, personality="aggressive")
    mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                nation="Austria", strength=12000,
                                personality="cautious")
    world = WorldFactory.with_marshals([ney, murat, mack])
    _war(world)
    world.calculate_visibility()
    world.actions_remaining = 4
    world.marshals["Ney"].jealous_of = "Murat"
    return world, CommandExecutor()


@pytest.fixture()
def objecting_board():
    """Cautious Ney against a force that dwarfs him.

    MEASURED: this is the configuration in which
    `_execute_strategic_command` raises a strategic objection AND returns
    WITHOUT a `variable_action_cost` key. An aggressive marshal at good
    odds - the first draft of these tests - never objects at all, so the
    suppression pins passed while testing nothing.
    """
    ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                  strength=30000, personality="cautious")
    murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                    strength=30000, personality="aggressive")
    mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                nation="Austria", strength=60000,
                                personality="cautious")
    world = WorldFactory.with_marshals([ney, murat, mack])
    _war(world)
    world.calculate_visibility()
    world.actions_remaining = 4
    world.marshals["Ney"].jealous_of = "Murat"
    return world, CommandExecutor()


def _petition(world):
    J.queue_confrontation_petition(world, world.marshals["Ney"],
                                   world.marshals["Murat"], 1)
    return world.pending_marshal_petition


def _answer(world, executor, choice="command"):
    return J.handle_petition_response(
        world, choice, executor=executor,
        game_state={"world": world, "executor": executor})


# ════════════════════════════════════════════════════════════════════════
# The option exists, and says what it does
# ════════════════════════════════════════════════════════════════════════

class TestTheCardOffersACommand:
    def test_the_fourth_arm_is_on_the_card(self, board):
        world, _ = board
        petition = _petition(world)
        ids = {o["id"] for o in petition["options"]}
        assert ids == {"acknowledge", "promise", "rebuke", "command"}

    def test_it_names_the_enemy_and_the_place(self, board):
        world, _ = board
        opt = next(o for o in _petition(world)["options"]
                   if o["id"] == "command")
        assert opt["enabled"] is True
        assert "Mack" in opt["detail"]

    def test_it_warns_that_a_battle_may_follow(self, board):
        """The order can resolve a battle inside the arm. Saying so is the
        cheapest half of the fix — the alternative is a card that quietly
        fights one."""
        world, _ = board
        opt = next(o for o in _petition(world)["options"]
                   if o["id"] == "command")
        assert "bring on a battle" in opt["detail"]

    def test_the_literal_pays_the_literal_price(self, board):
        world, _ = board
        world.marshals["Ney"].personality = "literal"
        opt = next(o for o in _petition(world)["options"]
                   if o["id"] == "command")
        assert opt["ap_cost"] == J.COMMAND_ARM_AP_LITERAL == 1

    def test_the_others_pay_a_strategic_orders_own_price(self, board):
        world, _ = board
        opt = next(o for o in _petition(world)["options"]
                   if o["id"] == "command")
        assert opt["ap_cost"] == J.COMMAND_ARM_AP == 2


# ════════════════════════════════════════════════════════════════════════
# Honest availability — every gate mirrors an executor refusal
# ════════════════════════════════════════════════════════════════════════

class TestHonestAvailability:
    def _reason(self, world):
        opt = next(o for o in _petition(world)["options"]
                   if o["id"] == "command")
        assert opt["enabled"] is False
        return opt.get("unavailable_reason", "")

    def test_no_reachable_enemy(self, board):
        """Removed rather than relocated: Paris is ADJACENT to Belgium in
        the fixture world, so moving him leaves him perfectly reachable —
        the first draft of this test passed him straight through."""
        world, _ = board
        world.marshals.pop("Mack")
        assert "no enemy within his reach" in self._reason(world)

    def test_broken(self, board):
        world, _ = board
        world.marshals["Ney"].broken = True
        assert "broken" in self._reason(world)

    def test_recovering_from_a_retreat(self, board):
        world, _ = board
        world.marshals["Ney"].retreat_recovery = 2
        assert "reforming" in self._reason(world)

    def test_artillery_cannot_pursue(self, board):
        world, _ = board
        world.marshals["Ney"].artillery = True
        assert "guns cannot pursue" in self._reason(world)

    def test_the_F10_no_op_is_never_offered(self, board):
        """A marshal already carrying that identical PURSUE gets
        "already carrying out that order. No change." — success, zero
        cost, nothing done. Offering it would be the exact CA9 shape:
        a surface promising what the executor will not do."""
        world, executor = board
        _petition(world)
        _answer(world, executor)                    # issues the PURSUE
        world.pending_marshal_petition = None
        assert "already marching on Mack" in self._reason(world)

    def test_a_contested_destination_is_refused(self, board):
        """The one second-modal path `objection_response` cannot suppress
        is `_handle_first_step_blocked`. A co-located quarry never takes
        it and an adjacent one filters ITSELF out of the blocking set, so
        the only opening left is a THIRD army standing where we are
        sending him. Refuse it, with the reason said.

        Paris is adjacent to Belgium in the fixture world, which is what
        makes this reachable at all."""
        world, _ = board
        world.marshals["Mack"].location = "Paris"
        world.marshals["Murat"].location = "Belgium"
        charles = MarshalFactory.enemy(name="Charles", location="Paris",
                                       nation="Austria", strength=40000)
        world.marshals["Charles"] = charles
        assert "held in force" in self._reason(world)

    def test_engaged_elsewhere(self, board):
        """The executor refuses a strategic march by an engaged marshal
        unless the quarry is one of the enemies standing on him."""
        world, _ = board
        other = MarshalFactory.enemy(name="Charles", location="Belgium",
                                     nation="Austria", strength=40000)
        world.marshals["Charles"] = other
        world.marshals["Mack"].strength = 1        # weakest -> the quarry
        # Mack IS here, so this must stay available...
        opt = next(o for o in _petition(world)["options"]
                   if o["id"] == "command")
        assert opt["enabled"] is True

    def test_an_unavailable_arm_still_refuses_at_answer_time(self, board):
        """Re-derived, not trusted from the card. The petition may be
        several turns old — the A3 discipline."""
        world, executor = board
        _petition(world)
        world.marshals.pop("Mack")                  # the world moved on
        result = _answer(world, executor)
        assert result["success"] is False
        assert "no enemy within his reach" in result["message"]
        assert world.actions_remaining == 4          # nothing spent


# ════════════════════════════════════════════════════════════════════════
# The arm does what it says
# ════════════════════════════════════════════════════════════════════════

class TestTheArmIssuesARealOrder:
    def test_a_pursue_order_is_created(self, board):
        world, executor = board
        _petition(world)
        result = _answer(world, executor)
        assert result["success"] is True
        order = world.marshals["Ney"].strategic_order
        assert order is not None
        assert order.command_type == "PURSUE"
        assert order.target == "Mack"

    def test_the_ap_comes_off(self, board):
        world, executor = board
        _petition(world)
        _answer(world, executor)
        assert world.actions_remaining == 4 - J.COMMAND_ARM_AP

    def test_the_marshal_speaks(self, board):
        world, executor = board
        _petition(world)
        result = _answer(world, executor)
        assert "Mack" in result["message"]

    def test_the_words_become_the_record(self, board):
        """The order carries the card's own phrase, so the campaign log
        and battle attribution quote what was actually said."""
        world, executor = board
        _petition(world)
        _answer(world, executor)
        order = world.marshals["Ney"].strategic_order
        assert "deal with Mack" in str(getattr(order, "original_command", ""))

    def test_the_battle_surface_is_carried_not_swallowed(self, board):
        """A co-located PURSUE attacks at once. The card must not eat the
        result of the battle it just caused.

        Driven through a stub, because the live path's own message names
        the enemy either way - the first draft accepted that as evidence
        and could not tell a carried report from a swallowed one."""
        world, executor = board
        _petition(world)
        marker = {"casualty_summary": "PROOF", "jealousy_note": "note"}
        executor._execute_strategic_command = lambda *_a: {
            "success": True, "message": "ordered",
            "variable_action_cost": 2, "battle_report": marker}
        result = _answer(world, executor)
        assert result.get("battle_report") is marker

    def test_a_first_step_interrupt_is_carried_too(self, board):
        """The other half: an interrupt the player must answer cannot be
        dropped on the floor by the card that caused it."""
        world, executor = board
        _petition(world)
        executor._execute_strategic_command = lambda *_a: {
            "success": True, "message": "ordered", "requires_input": True,
            "pending_interrupt": {"marshal": "Ney"}}
        result = _answer(world, executor)
        assert result.get("pending_interrupt") == {"marshal": "Ney"}
        assert result.get("requires_input") is True

    def test_the_autonomous_attack_is_called_off(self, objecting_board):
        """`cancel_autonomous_warning_on_order` normally rides
        `executor.execute`, which this path bypasses. A marshal who has
        just been GIVEN an objective must not still launch the attack he
        was warned about.

        Uses the CAUTIOUS board deliberately: on the aggressive board the
        order brings on a battle that RESOLVES the grievance, and
        `clear_jealousy` zeroes this flag by itself - so the pin passed
        with the cancel call deleted."""
        world, executor = objecting_board
        world.marshals["Ney"].jealousy_autonomous_warned = True
        _petition(world)
        _answer(world, executor)
        assert world.marshals["Ney"].jealousy_autonomous_warned is False

    def test_the_bare_order_really_would_object(self, objecting_board):
        """NEGATIVE CONTROL. Without this the suppression pin below is
        vacuous - and it WAS: an aggressive marshal at good odds never
        objects, so the first draft asserted the absence of something
        that was never going to happen. A mutation sweep caught it."""
        world, executor = objecting_board
        bare = executor._execute_strategic_command(
            {"strategic_type": "PURSUE", "raw_input": "x"},
            {"marshal": "Ney", "target": "Mack", "target_type": "marshal"},
            {"world": world, "executor": executor}) or {}
        assert bare.get("pending_objection") is True
        # ...and that return carries NO cost key, which is the KeyError
        # the charge has to survive.
        assert "variable_action_cost" not in bare

    def test_no_second_modal_is_stacked_on_the_petition(self,
                                                        objecting_board):
        """`objection_response="proceed"` suppresses the strategic
        objection. Without it the player answers one modal and is handed
        another on top of it."""
        world, executor = objecting_board
        _petition(world)
        result = _answer(world, executor)
        assert not result.get("pending_objection")
        assert world.pending_strategic_objection in (None, {}, [])
        assert world.marshals["Ney"].strategic_order is not None

    def test_the_suppression_does_not_cost_trust(self, objecting_board):
        """Omitting `v2_insist_penalty=0` applies a real -10: the
        "proceed" path runs `modify_trust(penalty)` and the default is
        the insist penalty, not zero."""
        world, executor = objecting_board
        before = world.marshals["Ney"].trust.value
        _petition(world)
        _answer(world, executor)
        assert world.marshals["Ney"].trust.value == before


# ════════════════════════════════════════════════════════════════════════
# The crash paths the refutation found in the first-draft design
# ════════════════════════════════════════════════════════════════════════

class TestItCannotCrashOrLieOnRefusal:
    def test_an_absent_variable_action_cost_is_survivable(self, board):
        """MEASURED by the pre-build refutation: on the objection return
        the key is ABSENT, not 0. A subscript would raise KeyError into
        `main.py`'s blanket except AFTER the petition was popped and the
        world mutated — the player sees
        "Error: 'variable_action_cost'" and the card is gone."""
        world, executor = board
        _petition(world)

        def _no_cost(_parsed, _cmd, _gs):
            return {"success": True, "message": "ordered"}   # no cost key

        executor._execute_strategic_command = _no_cost
        result = _answer(world, executor)
        assert result["success"] is True
        assert world.actions_remaining == 4        # charged nothing, no crash

    def test_a_failed_order_charges_nothing_and_says_why(self, board):
        world, executor = board
        _petition(world)

        def _refuse(_parsed, _cmd, _gs):
            return {"success": False, "message": "He is engaged.",
                    "variable_action_cost": 0}

        executor._execute_strategic_command = _refuse
        result = _answer(world, executor)
        assert result["success"] is False
        assert "engaged" in result["message"]
        assert world.actions_remaining == 4

    def test_a_None_return_is_survivable(self, board):
        world, executor = board
        _petition(world)
        executor._execute_strategic_command = lambda *_a: None
        result = _answer(world, executor)
        assert result["success"] is False
        assert world.actions_remaining == 4

    def test_no_staff_no_order(self, board):
        """`handle_petition_response` is reachable without an executor
        (several call sites pass none)."""
        world, _ = board
        _petition(world)
        result = J.handle_petition_response(world, "command")
        assert result["success"] is False
        assert world.actions_remaining == 4

    def test_an_unknown_id_never_reaches_the_silent_else(self, board):
        """`handle_petition_response` validates against the petition's own
        option ids; the bare `else` in the confrontation arm returns
        SUCCESS with a soothing message, so an id that slipped through
        would look like it worked."""
        world, executor = board
        _petition(world)
        result = _answer(world, executor, choice="to_my_tent")
        assert result["success"] is False
        assert "Unknown answer" in result["message"]
        assert world.pending_marshal_petition is not None


# ════════════════════════════════════════════════════════════════════════
# Sizing — the claim that this is a small slice
# ════════════════════════════════════════════════════════════════════════

class TestSizing:
    def test_no_new_campaign_log_type(self):
        assert len(CAMPAIGN_LOG_TYPES) == 157

    def test_the_log_does_not_call_an_army_a_hearing(self, board):
        """Without its own row the shared `choice_str` map falls through
        to "was heard" — for a player who handed the man a corps."""
        world, executor = board
        _petition(world)
        _answer(world, executor)
        line = format_event_oneliner({
            "type": "jealousy_confrontation", "marshal": "Ney",
            "target": "Murat", "nation": "France", "choice": "command"})
        assert "was given a command" in line
        assert "was heard" not in line

    def test_no_new_serialized_field(self, board):
        """The arm writes only `strategic_order`, which has always been
        serialized."""
        world, executor = board
        _petition(world)
        _answer(world, executor)
        payload = world.to_dict()
        assert payload  # round-trips
        from backend.models.world_state import WorldState
        restored = WorldState.from_dict(payload)
        order = restored.marshals["Ney"].strategic_order
        assert order is not None and order.target == "Mack"

    def test_the_client_needs_no_change(self):
        """The option list is data-driven — `marshal_petition_dialog.gd`
        builds a button per option and posts its `id`."""
        from pathlib import Path
        gd = (Path(__file__).resolve().parents[1] / "godot-client"
              / "project-sovereign" / "scenes"
              / "marshal_petition_dialog.gd")
        if not gd.exists():
            gd = (Path(__file__).resolve().parents[1] / "godot-client"
                  / "project-sovereign" / "scripts"
                  / "marshal_petition_dialog.gd")
        src = gd.read_text(encoding="utf-8")
        assert "acknowledge" not in src, (
            "the client hardcodes an option id — a fourth arm would need "
            "a .gd change and this slice's sizing claim is wrong")
