"""PF-2 (Combat Overhaul Phase 6 — Parser & Play-Friction Cleanup).

A personality delegation ASK ("Soult, deal with Mack") offers, in its question
text, the natural-language verbs "give battle"/"attacked" and
"observe"/"observed". But the answer interpreter only matched a typed answer
against the option LABELS ("Attack"/"Scout") and TARGETS — so answering in the
question's own words fell through to `{"kind":"pass"}`, got re-parsed as a fresh
command, and produced "Region 'generic' not found".

The fix declares answer `aliases` on each delegation option and matches them
generically in `interpret_clarification_answer`, so the offered verbs rebind to
the correct option (whose `command` already carries the right target).
"""
from backend.models.world_state import WorldState
from backend.commands.delegation import DelegationMatch, build_delegation_clarification
from backend.commands.clarification import interpret_clarification_answer


def _dialogue(personality="literal"):
    world = WorldState()
    match = DelegationMatch(
        marshal="Soult", personality=personality, target="Mack",
        scout_target="Tyrol", target_display="Mack", verb="deal with",
        clause="deal with Mack")
    return build_delegation_clarification(world, match, "Soult deal with Mack")


def test_options_declare_answer_aliases():
    dialogue = _dialogue()
    opts = {o["label"]: o for o in dialogue["options"]}
    assert "give battle" in opts["Attack"]["aliases"]
    assert "observe" in opts["Scout"]["aliases"]


def test_give_battle_resolves_to_attack():
    """The reported failure: 'give battle' now rebinds to the Attack command."""
    dialogue = _dialogue()
    res = interpret_clarification_answer(dialogue, "give battle")
    assert res == {"kind": "command", "command": "Soult attack Mack"}


def test_observe_resolves_to_scout():
    dialogue = _dialogue()
    res = interpret_clarification_answer(dialogue, "observe")
    assert res == {"kind": "command", "command": "Soult scout Tyrol"}


def test_printed_scout_phrase_resolves():
    """Review-fix regression: the literal ASK prints "observe {who}" (e.g.
    "observe Mack") — typing that exact printed phrase must resolve to Scout,
    symmetrically with the attack side's "give battle"."""
    dialogue = _dialogue(personality="literal")
    assert interpret_clarification_answer(dialogue, "observe Mack") == {
        "kind": "command", "command": "Soult scout Tyrol"}
    assert interpret_clarification_answer(dialogue, "observe mack") == {
        "kind": "command", "command": "Soult scout Tyrol"}


def test_target_qualified_attack_phrase_resolves():
    """Parity: "attack Mack" / "engage Mack" resolve to the Attack command."""
    dialogue = _dialogue()
    assert interpret_clarification_answer(dialogue, "attack Mack")["command"] == "Soult attack Mack"
    assert interpret_clarification_answer(dialogue, "engage Mack")["command"] == "Soult attack Mack"


def test_neutral_phrasing_verbs_resolve():
    """The neutral ASK phrasing offers 'attacked'/'observed'."""
    dialogue = _dialogue(personality="")
    assert interpret_clarification_answer(dialogue, "attacked") == {
        "kind": "command", "command": "Soult attack Mack"}
    assert interpret_clarification_answer(dialogue, "observed") == {
        "kind": "command", "command": "Soult scout Tyrol"}


def test_unrelated_answer_still_passes():
    """FALSIFIABLE NEGATIVE: a word that is neither a label, a target, nor an
    alias falls through to a normal parse (kind == 'pass') — the alias matching
    must not swallow arbitrary input."""
    dialogue = _dialogue()
    assert interpret_clarification_answer(dialogue, "banana") == {"kind": "pass"}


def test_existing_paths_preserved():
    """The label / target / numeric / confirm paths still work unchanged."""
    dialogue = _dialogue()
    # Label
    assert interpret_clarification_answer(dialogue, "attack")["command"] == "Soult attack Mack"
    assert interpret_clarification_answer(dialogue, "scout")["command"] == "Soult scout Tyrol"
    # Target name
    assert interpret_clarification_answer(dialogue, "Mack")["command"] == "Soult attack Mack"
    assert interpret_clarification_answer(dialogue, "Tyrol")["command"] == "Soult scout Tyrol"
    # Numeric (1-based option index)
    assert interpret_clarification_answer(dialogue, "1")["command"] == "Soult attack Mack"
    assert interpret_clarification_answer(dialogue, "2")["command"] == "Soult scout Tyrol"
    # Bare confirmation -> the interpreted (question-named) target = Attack
    assert interpret_clarification_answer(dialogue, "yes")["command"] == "Soult attack Mack"


def test_legacy_clarification_without_aliases_unchanged():
    """A clarification whose options declare NO aliases is byte-unchanged — an
    unmatched answer still passes."""
    dialogue = {
        "options": [
            {"label": "Ney", "target": "Ney", "command": "Ney attack Mack"},
            {"label": "Davout", "target": "Davout", "command": "Davout attack Mack"},
        ],
        "marshal": "Berthier",
    }
    assert interpret_clarification_answer(dialogue, "give battle") == {"kind": "pass"}
    assert interpret_clarification_answer(dialogue, "Ney")["command"] == "Ney attack Mack"
