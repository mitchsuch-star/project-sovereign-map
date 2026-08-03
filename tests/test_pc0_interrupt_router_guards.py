"""PC-0 — the pending-interrupt router re-opened PARSE-NEG (quiet-France
played campaign, August 3 2026).

`main.py`'s pending-interrupt router maps a typed reply onto an interrupt's
`options` and RETURNS. It runs above the parser, so PARSE-NEG's clause guards
— which landed the day before — were never reaching it. Two defects, both
reproduced in a live 42-turn campaign against the shipped 1805 board:

1.  **No word boundaries.** The matcher used `keyword in cmd_lower`, and
    "flee" is a substring of "fleet". Every naval order in the game therefore
    answered a cornered marshal's last stand as `attempt_breakout` — a −10%
    escape roll with the marshal's liberty staked on it. Observed at turn 42:
    typing `set the fleet to raid commerce` with Massena cornered produced
    `[INTERRUPT ROUTE] ... Massena last_stand response: attempt_breakout`,
    then "The breakout fails — MARSHAL CAPTURED — Massena is taken by Austria
    at Limousin!". The fleet posture was never changed. `raise a fleet` is a
    golden-corpus utterance and is hijacked identically.

2.  **No negation guard.** `"attack" in cmd_lower` fires on every negated
    form, and the attack branch was tested BEFORE the hold branch — so
    PARSE-NEG's own headline sentence, "hold your position, do not attack",
    resolved to HOLD at the parser and to ATTACK here.

Neither could be caught by the corpus: `parser_eval` calls
`CommandParser.parse` directly and never traverses this router, and there is
no last-stand fixture in the corpus.

The tests below pin both defects, pin the counter-examples the fix must NOT
disturb, and carry a negative control that re-runs the OLD matching rule and
asserts it fails — so a regression to raw `in` matching reds these tests
rather than silently passing them.
"""
import pytest
from fastapi.testclient import TestClient

from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser
from backend.main import _interrupt_choice_from_text

from tests.conftest import MarshalFactory, WorldFactory

BAD_ODDS = ["attack_anyway", "go_around", "hold_position", "cancel_order"]
LAST_STAND = ["fight_to_the_last", "attempt_breakout"]


# ── the two defects ────────────────────────────────────────────────────────

@pytest.mark.parametrize("utterance", [
    "raise a fleet",                    # golden-corpus row, build_fleet
    "set the fleet to raid commerce",   # the live turn-42 loss
    "build the fleet at Brittany",
    "set fleet posture to guard",
])
def test_naval_orders_never_answer_a_last_stand(utterance):
    """'flee' must not match inside 'fleet'. No naval verb may stake a
    cornered marshal on an escape roll."""
    assert _interrupt_choice_from_text(utterance, LAST_STAND) is None


@pytest.mark.parametrize("utterance,expected", [
    ("hold your position, do not attack", "hold_position"),
    ("do not attack", None),
    ("never attack", None),
    ("ney, without attacking, move to lorraine", None),
    ("ney, instead of attacking, fortify", None),
])
def test_negated_orders_do_not_resolve_as_attack(utterance, expected):
    """What survives the negation is what routes. When nothing survives the
    router declines, and the command falls through to the parser — which
    refuses it — instead of executing the verb the player forbade."""
    assert _interrupt_choice_from_text(utterance, BAD_ODDS) == expected


def test_stand_down_is_not_an_assault():
    """'stop attacking' contains 'attack'; the attack branch is tested first.
    A stand-down must reach cancel/hold, never attack_anyway."""
    assert _interrupt_choice_from_text("ney, stop attacking", BAD_ODDS) == "cancel_order"
    assert _interrupt_choice_from_text(
        "stop attacking", ["attack_anyway", "hold_position"]) == "hold_position"


# ── counter-examples: the fix must not over-correct ────────────────────────

@pytest.mark.parametrize("utterance,expected", [
    ("press on", "attack_anyway"),          # Sweep-5 contract
    ("push through", "attack_anyway"),
    ("continue", "attack_anyway"),
    ("attack anyway", "attack_anyway"),     # W6-4 popup label
    ("march to the guns", "attack_anyway"),
    ("attack", "attack_anyway"),
    ("hold", "hold_position"),
    ("halt", "hold_position"),
    ("wait", "hold_position"),
    ("go around", "go_around"),
    ("reroute", "go_around"),
    ("cancel", "cancel_order"),
    ("belay that", "cancel_order"),
])
def test_affirmative_answers_still_route(utterance, expected):
    assert _interrupt_choice_from_text(utterance, BAD_ODDS) == expected


@pytest.mark.parametrize("utterance,expected", [
    ("fight to the last", "fight_to_the_last"),   # W6-7
    ("last stand", "fight_to_the_last"),
    ("attempt breakout", "attempt_breakout"),
    ("break out", "attempt_breakout"),
    ("escape", "attempt_breakout"),
    ("flee", "attempt_breakout"),
])
def test_last_stand_answers_still_route(utterance, expected):
    assert _interrupt_choice_from_text(utterance, LAST_STAND) == expected


def test_avoid_answers_go_around_despite_being_a_negation_marker():
    """'avoid' is in PARSE-NEG's negation marker set AND is the affirmative
    label of this option. Answering the game's own question is not negating
    an order, and both readings land on go_around, so this branch reads raw
    text. Without the carve-out the answer is blanked and lost."""
    assert _interrupt_choice_from_text("avoid it", BAD_ODDS) == "go_around"
    assert _interrupt_choice_from_text("avoid attacking", BAD_ODDS) == "go_around"


def test_continue_order_preferred_over_attack_anyway_when_offered():
    assert _interrupt_choice_from_text(
        "press on", ["continue_order", "attack_anyway"]) == "continue_order"


def test_choice_must_be_an_offered_option():
    """A keyword hit whose choice is not on the interrupt's own option list
    yields None rather than an invented answer."""
    assert _interrupt_choice_from_text("go around", ["attack_anyway"]) is None
    assert _interrupt_choice_from_text("flee", ["attack_anyway"]) is None


# ── negative control: the OLD rule must fail these ─────────────────────────

def _legacy_choice(cmd_lower, options):
    """The pre-fix matcher, verbatim in behaviour: raw substring, no negation
    guard, attack tested before hold."""
    if "fight_to_the_last" in options and any(
            kw in cmd_lower for kw in ["fight", "last stand", "to the last", "die "]):
        return "fight_to_the_last"
    if "attempt_breakout" in options and any(
            kw in cmd_lower for kw in ["breakout", "break out", "escape", "cut", "flee"]):
        return "attempt_breakout"
    if any(kw in cmd_lower for kw in ["investigate", "march to", "guns", "attack",
                                      "charge", "join", "commit", "proceed"]):
        return ("investigate" if "investigate" in options
                else "attack" if "attack" in options
                else "attack_anyway" if "attack_anyway" in options else None)
    if any(kw in cmd_lower for kw in ["hold", "stay", "stop", "wait", "halt"]):
        return "hold_position" if "hold_position" in options else None
    return None


def test_negative_control_the_old_rule_reproduces_both_defects():
    """Falsifiability: if someone reverts to raw `in` matching, these are the
    behaviours that return. The control asserts the OLD rule is wrong, so the
    test file cannot pass vacuously."""
    assert _legacy_choice("set the fleet to raid commerce", LAST_STAND) == "attempt_breakout"
    assert _legacy_choice("raise a fleet", LAST_STAND) == "attempt_breakout"
    assert _legacy_choice("hold your position, do not attack", BAD_ODDS) == "attack_anyway"
    assert _legacy_choice("ney, stop attacking", BAD_ODDS) == "attack_anyway"
    # ...and the fixed rule disagrees with the old one on every one of them.
    for utterance, options in [("set the fleet to raid commerce", LAST_STAND),
                               ("raise a fleet", LAST_STAND),
                               ("hold your position, do not attack", BAD_ODDS),
                               ("ney, stop attacking", BAD_ODDS)]:
        assert _interrupt_choice_from_text(utterance, options) != _legacy_choice(
            utterance, options)


# ── end-to-end through the real endpoint ───────────────────────────────────

def _last_stand_world():
    massena = MarshalFactory.infantry(name="Massena", location="Belgium",
                                      strength=3000, personality="aggressive")
    enemy = MarshalFactory.enemy(name="Mack", location="Belgium",
                                 nation="Austria", strength=50000,
                                 personality="cautious")
    world = WorldFactory.with_marshals([massena, enemy])
    key = "|".join(sorted(["France", "Austria"]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn
    return world


@pytest.fixture()
def endpoint():
    import backend.main as main_module

    saved = (main_module.parser, main_module.world,
             main_module.game_state, main_module.executor)
    main_module.parser = CommandParser(use_real_llm=False)
    main_module.world = _last_stand_world()
    main_module.game_state = {"world": main_module.world}
    main_module.executor = CommandExecutor()
    try:
        yield TestClient(main_module.app), main_module
    finally:
        (main_module.parser, main_module.world,
         main_module.game_state, main_module.executor) = saved


def test_naval_order_leaves_a_pending_last_stand_untouched(endpoint):
    """The live turn-42 loss, end to end: with a last stand pending, a fleet
    order must NOT consume it. The interrupt is still there afterwards."""
    client, m = endpoint
    massena = m.world.get_marshal("Massena")
    massena.pending_interrupt = {
        "marshal": "Massena",
        "interrupt_type": "last_stand",
        "options": ["fight_to_the_last", "attempt_breakout"],
    }
    client.post("/command", json={"command": "raise a fleet"})
    assert m.world.get_marshal("Massena").pending_interrupt is not None, (
        "a naval order answered the last stand — 'flee' matched inside 'fleet'")
