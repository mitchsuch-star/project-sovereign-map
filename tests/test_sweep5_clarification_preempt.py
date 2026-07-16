"""Sweep-5 live finding (Combat Overhaul, Parsing/UX sweep, July 16 2026).

With a SOFT-STOP dialogue occupying the DialogueManager (e.g. an incoming AI
proposal riding the mailbox after the enemy phase), `register_pending_
clarification` refused to register ANY clarification — so the typed-answer
channel silently died and typing the delegation ASK's own words ("give
battle") fell through to a fresh LLM parse and mis-resolved ("Region
'generic' not found"). In the terminal client the typed channel is the
PRIMARY answer path, so the fix PREEMPTS a non-hard-stop dialogue: the
clarification becomes current and the displaced dialogue returns through
normal queue promotion once the answer pops it. A HARD-STOP dialogue still
skips registration (it blocks all commands, so the ASK could never be
answered anyway).
"""
from backend.commands.clarification import (
    CLARIFICATION_DIALOGUE_TYPE,
    interpret_clarification_answer,
    register_pending_clarification,
)
from backend.commands.delegation import (
    DelegationMatch,
    build_delegation_clarification,
)
from backend.models.world_state import WorldState


def _ask_response(world):
    match = DelegationMatch(
        marshal="Soult", personality="literal", target="Mack",
        scout_target="Tyrol", target_display="Mack", verb="deal with",
        clause="deal with Mack")
    return build_delegation_clarification(world, match, "Soult deal with Mack")


def _soft_stop(world):
    world.dialogue_manager.push({
        "type": "diplomatic_proposal",
        "turn_created": int(world.current_turn),
        "message": "Prussia proposes a trade agreement.",
    })


def test_empty_stack_still_registers_as_current():
    world = WorldState()
    assert register_pending_clarification(world, _ask_response(world), "x")
    top = world.dialogue_manager.peek()
    assert top is not None and top["type"] == CLARIFICATION_DIALOGUE_TYPE


def test_soft_stop_is_preempted_not_skipped():
    """The live failure: an ASK issued while a soft-stop proposal is current
    must still own the typed-answer slot."""
    world = WorldState()
    _soft_stop(world)
    assert register_pending_clarification(world, _ask_response(world), "x") is True
    top = world.dialogue_manager.peek()
    assert top is not None and top["type"] == CLARIFICATION_DIALOGUE_TYPE


def test_give_battle_resolves_through_preempted_slot():
    """End-to-end over the dialogue manager: with the soft-stop displaced, the
    typed answer 'give battle' resolves to the rebound attack command."""
    world = WorldState()
    _soft_stop(world)
    register_pending_clarification(world, _ask_response(world), "x")
    pending = world.dialogue_manager.peek()
    res = interpret_clarification_answer(pending, "give battle")
    assert res == {"kind": "command", "command": "Soult attack Mack"}


def test_displaced_soft_stop_returns_after_pop():
    """The mailbox dialogue is preserved: answering (popping) the
    clarification promotes the displaced proposal back to current."""
    world = WorldState()
    _soft_stop(world)
    register_pending_clarification(world, _ask_response(world), "x")
    world.dialogue_manager.pop()  # main.py pops on the next typed input
    top = world.dialogue_manager.peek()
    assert top is not None and top["type"] == "diplomatic_proposal"


def test_hard_stop_still_skips_registration():
    """A hard-stop question blocks all commands — never shadow it."""
    world = WorldState()
    world.dialogue_manager.push({
        "type": "commitment_paradox",
        "turn_created": int(world.current_turn),
        "message": "A paradox demands resolution.",
    })
    assert register_pending_clarification(world, _ask_response(world), "x") is False
    top = world.dialogue_manager.peek()
    assert top is not None and top["type"] == "commitment_paradox"


def test_non_clarification_response_never_registers():
    world = WorldState()
    assert register_pending_clarification(
        world, {"state": "done", "options": []}, "x") is False
    assert world.dialogue_manager.peek() is None
