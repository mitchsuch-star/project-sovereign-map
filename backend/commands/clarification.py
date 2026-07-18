"""CR-2 unified command-clarification surface (COMMAND_ROBUSTNESS_SPEC §2).

One question, one answer: when a typed command is missing its executor
("support Ney", "move to Belgium") or names an unknown one ("Murat, charge"
on a world without Murat), the game asks a single in-character question
instead of silently dropping information or burying suggestions inside an
error string nobody surfaces.

Design contract:
- Responses ride the EXISTING ``state == "awaiting_clarification"`` surface
  (clarification_popup.tscn). Every actionable option carries a full
  ``command`` string that the popup reissues verbatim through /command, so
  resolution is a plain deterministic re-parse (Golden Rule 6: the LLM is
  never consulted to resolve an answer).
- The pending question is registered on the DialogueManager as a
  LOCAL_PLANNING ``command_clarification`` — soft, never blocks commands,
  auto-dismissed at the next turn boundary by clear_stale, and consumed by
  whatever the player types next.
- Registration happens ONLY in backend/main.py's player-command path.
  Executor-side emitters stay pure response builders, so AI-originated
  commands (which share the executor) can never create a player dialogue.
"""

import re
from typing import Dict, List, Optional

CLARIFICATION_DIALOGUE_TYPE = "command_clarification"

# Mirrors main.gd's keyword_map so backend-built reissue commands and the
# popup's legacy fallback produce the same phrasing.
STRATEGIC_REISSUE_KEYWORDS = {
    "PURSUE": "pursue",
    "MOVE_TO": "march to",
    "SUPPORT": "support",
    "HOLD": "hold",
}

_CANCEL_WORDS = frozenset({
    "cancel", "no", "never mind", "nevermind", "belay", "belay that",
    "abort", "stop", "withdraw", "forget it", "nothing", "disregard",
})
_CONFIRM_WORDS = frozenset({
    "yes", "proceed", "confirm", "do it", "very well", "as ordered",
    "correct", "aye", "make it so",
})

# Question copy per strategic type / tactical action — "Which marshal
# shall <verb phrase>, Sire?"
_ACTION_VERB_PHRASES = {
    "attack": "attack",
    "charge": "charge",
    "move": "march to",
    "scout": "scout",
    "hold": "hold",
    "defend": "defend",
    "garrison": "garrison",
    "recruit": "recruit at",
    "build": "build at",
    "repair": "repair",
}


def strategic_reissue_command(marshal_name: str, strategic_type: str,
                              target: str) -> str:
    """The command the clarification popup reissues for a strategic choice
    ("Ney pursue Bagration") — identical format to main.gd's legacy path."""
    keyword = STRATEGIC_REISSUE_KEYWORDS.get(strategic_type, "pursue")
    return f"{marshal_name} {keyword} {target}"


# Actions the executor treats as free — asking a clarification for these is
# always affordable. (The executor's own free_actions list is authoritative
# at execution time; this only gates whether a QUESTION is worth asking.)
_FREE_CLARIFIABLE_ACTIONS = frozenset({
    "wait", "retreat", "status", "help", "economy",
})


def _answer_is_affordable(world, action: Optional[str], *,
                          strategic_type: Optional[str] = None,
                          candidates=None) -> bool:
    """Adversarial-review fix: never ask a question whose every answer must
    then fail on AP (the established order is AP pre-validation BEFORE
    objections/clarifications). Uses the MINIMUM plausible cost of any
    answer — strategic orders cost 2 (1 for a literal candidate), tactical
    actions their action cost, unknown actions a floor of 1."""
    if action in _FREE_CLARIFIABLE_ACTIONS:
        return True
    remaining = int(getattr(world, "actions_remaining", 0))
    if strategic_type:
        required = 2
        if candidates and any(getattr(m, "personality", "") == "literal"
                              for m in candidates):
            required = 1
        return remaining >= required
    try:
        required = int(world.get_action_cost(action)) if action else 1
    except Exception:
        required = 1
    return remaining >= max(1, required)


def _verb_phrase(action: Optional[str], strategic_type: Optional[str],
                 target: Optional[str]) -> str:
    if strategic_type in STRATEGIC_REISSUE_KEYWORDS:
        verb = STRATEGIC_REISSUE_KEYWORDS[strategic_type]
    else:
        verb = _ACTION_VERB_PHRASES.get(action or "", "")
    if not verb:
        return "carry out this order"
    return f"{verb} {target}" if target else verb


def build_marshal_choice_clarification(world, parsed: Dict,
                                       raw_input: str) -> Optional[Dict]:
    """Build the "Which marshal, Sire?" question for a valid order that
    names no executor ("support Ney", "move to Belgium", "hold until Ney
    arrives").

    ``parsed`` is the successful parser.parse() result whose execution
    failed on the missing marshal. Returns a response dict for the
    awaiting_clarification surface, or None when no candidate exists
    (caller falls back to Berthier recovery).
    """
    command = parsed.get("command") or {}
    action = command.get("action")
    target = command.get("target")
    strategic_type = parsed.get("strategic_type") if parsed.get("is_strategic") else None
    # "hold Munich until Ney arrives" — the condition marshal can no more
    # execute the order than the support target can support himself
    condition = parsed.get("strategic_condition") or {}
    condition_marshal = condition.get("until_marshal_arrives")

    is_movement = action == "move" or strategic_type == "MOVE_TO"
    candidates = [
        m for m in world.get_field_marshals()
        if m.strength > 0 and m.name != target and m.name != condition_marshal
        # A marshal already standing at the destination cannot "march to" it
        and not (is_movement and target and m.location == target)
    ]
    if not candidates:
        return None
    if not _answer_is_affordable(world, action, strategic_type=strategic_type,
                                 candidates=candidates):
        return None

    order_text = raw_input.strip()
    options: List[Dict] = []
    for m in candidates[:8]:
        options.append({
            "label": m.name,
            "value": "assign_marshal",
            "target": m.name,
            "command": f"{m.name}, {order_text}",
        })

    question = f"Which marshal shall {_verb_phrase(action, strategic_type, target)}, Sire?"
    return _clarification_response(
        world,
        question=question,
        options=options,
        clarification_kind="marshal_choice",
        strategic_type=strategic_type,
        raw_input=raw_input,
    )


def build_contact_attack_clarification(world, candidates, raw_input: str) -> Optional[Dict]:
    """CR-6 / S5-D1: the "Which marshal shall lead the attack, Sire?" question
    for a bare "attack" (no marshal named) when MORE THAN ONE player marshal is
    in enemy contact. Single-contact keeps the instant auto-pick — this fires
    only for genuine ambiguity, so the most lethal lazy order stops being the
    only one with no gate.

    ``candidates`` is a list of ``(marshal, enemy)`` pairs — each an alive
    player marshal adjacent to that enemy. Every option reissues a fully-formed
    ``"<marshal>, attack <enemy>"`` so the answer resolves through the ordinary
    named-attack pipeline (W6-4 muster gate + objection included). Returns None
    when fewer than two candidates survive, or no answer could afford the
    attack (AP pre-validation before clarification — same rule as the other
    emitters).
    """
    pairs = [(m, e) for (m, e) in candidates
             if m is not None and e is not None
             and getattr(m, "strength", 0) > 0]
    if len(pairs) < 2:
        return None
    if not _answer_is_affordable(world, "attack"):
        return None

    options: List[Dict] = []
    for m, enemy in pairs[:8]:
        options.append({
            "label": m.name,
            "value": "assign_marshal",
            "target": m.name,
            "command": f"{m.name}, attack {enemy.name}",
        })

    return _clarification_response(
        world,
        question="Which marshal shall lead the attack, Sire?",
        options=options,
        clarification_kind="marshal_choice",
        strategic_type=None,
        raw_input=raw_input,
    )


def build_attack_target_clarification(world, marshal, enemies,
                                      raw_input: str) -> Optional[Dict]:
    """ESP-EV-4: "Which foe, Sire?" — the answer surface for an attack order
    whose target the player named but our maps do not know.

    The guard used to end in a flat terminal refusal that listed the visible
    enemies as prose and offered nothing to click or type back. The July 18,
    2026 playtest report is exactly that dead end: "Ney, give them hell" printed
    a list and did nothing, while "Ney, give Charles hell" — a name resolution
    happened to ground — opened a popup. Same intent, two unrelated surfaces,
    and only one of them was answerable.

    Every option reissues a fully-formed ``"<marshal>, attack <enemy>"`` so the
    answer resolves through the ordinary named-attack pipeline (muster preview,
    fortification-aware bad-odds gate and objection block all included) rather
    than re-entering the guess that was just refused. Returns None when nothing
    is visible to offer or no answer could afford the attack, so the caller
    keeps its plain refusal for the genuinely empty case.
    """
    if marshal is None:
        return None
    visible = [e for e in (enemies or []) if getattr(e, "strength", 0) > 0]
    if not visible:
        return None
    if not _answer_is_affordable(world, "attack"):
        return None

    options: List[Dict] = []
    for enemy in visible[:6]:
        options.append({
            "label": f"{enemy.name} at {enemy.location}",
            "value": "attack_target_choice",
            "target": enemy.name,
            "command": f"{marshal.name}, attack {enemy.name}",
            # The typed channel is the PRIMARY answer path in the terminal, so
            # the bare name and the target-qualified form must both resolve.
            "aliases": [enemy.name, enemy.location,
                        f"attack {enemy.name}", f"attack {enemy.location}"],
        })

    return _clarification_response(
        world,
        question=(f"Your order names no foe our maps know, Sire — "
                  f"{marshal.name} will not charge at a guess. Whom shall "
                  f"he engage?"),
        options=options,
        clarification_kind="attack_target",
        strategic_type=None,
        raw_input=raw_input,
    )


def build_unknown_name_clarification(world, unknown_name: str,
                                     candidates: List[str], raw_input: str,
                                     kind: str,
                                     partial_action: Optional[str] = None) -> Optional[Dict]:
    """Build the did-you-mean question for an addressed name that failed
    fuzzy matching ("Murat, charge" on a world without Murat).

    Each option's reissue command substitutes the candidate for the unknown
    token in the player's own words. Returns None when no substitution is
    possible or no answer could afford to execute (caller falls back to the
    plain error / Berthier recovery).
    """
    if not unknown_name or not candidates:
        return None
    if not _answer_is_affordable(world, partial_action):
        return None

    try:
        token_re = re.compile(r'\b' + re.escape(unknown_name) + r'\b',
                              re.IGNORECASE)
    except re.error:
        return None

    options: List[Dict] = []
    seen = set()
    for candidate in candidates[:4]:
        if not candidate or candidate.lower() in seen:
            continue
        seen.add(candidate.lower())
        reissued, count = token_re.subn(candidate, raw_input, count=1)
        if count == 0:
            continue
        options.append({
            "label": candidate,
            "value": "substitute_marshal",
            "target": candidate,
            "command": reissued,
        })
    if not options:
        return None

    if kind == "marshal_suggest":
        question = (f"I do not find '{unknown_name}' in the order of battle, "
                    f"Sire. Did you mean {options[0]['label']}?")
    else:
        question = (f"There is no Marshal '{unknown_name}' in the order of "
                    f"battle, Sire. Whom did you intend?")
    return _clarification_response(
        world,
        question=question,
        options=options,
        clarification_kind="unknown_name",
        strategic_type=None,
        raw_input=raw_input,
    )


def _clarification_response(world, *, question: str, options: List[Dict],
                            clarification_kind: str,
                            strategic_type: Optional[str],
                            raw_input: str) -> Dict:
    """Assemble the awaiting_clarification response envelope (same shape as
    the Grouchy/literal emitters so the existing popup renders it)."""
    response = {
        "success": True,
        "free_action": True,
        "state": "awaiting_clarification",
        "type": "clarification",
        "clarification_kind": clarification_kind,
        # The popup titles from this field ("BERTHIER ASKS:") — command-level
        # questions are the chief of staff's, not a marshal's.
        "marshal": "Berthier",
        "message": question,
        "original_command": raw_input,
        "options": options,
        "action_summary": world.get_action_summary(),
        "game_state": world.get_filtered_game_state_summary(),
    }
    # Adversarial-review fix: a PRESENT-but-null strategic_type crashed the
    # Godot popup (Dictionary.get's default only applies to MISSING keys,
    # and assigning Nil to a typed String var is a runtime error) — omit
    # the key entirely for non-strategic questions.
    if strategic_type:
        response["strategic_type"] = strategic_type
    return response


def register_pending_clarification(world, response: Dict,
                                   raw_input: str) -> bool:
    """Store an emitted clarification question on the DialogueManager so the
    player's next typed input can answer it.

    Only called from main.py's player-command path (never for AI commands).
    Skips registration only when a HARD-STOP dialogue is active (that question
    blocks all commands, so the clarification could never be answered anyway).
    A soft-stop / local dialogue (e.g. an incoming AI proposal riding the
    mailbox) is PREEMPTED instead: the clarification becomes current and the
    displaced dialogue returns through normal queue promotion once the answer
    pops it. Sweep-5 live finding: the old any-dialogue skip killed the typed
    answer channel behind every soft-stop, so typing the delegation ASK's own
    words ("give battle") fell to a fresh LLM parse and mis-resolved
    ("Region 'generic' not found") — in the terminal the typed channel is the
    PRIMARY answer path, not a popup fallback.
    """
    if response.get("state") != "awaiting_clarification":
        return False
    dm = world.dialogue_manager
    options = response.get("options") or []
    dialogue = {
        "type": CLARIFICATION_DIALOGUE_TYPE,
        "turn_created": int(world.current_turn),
        "question": response.get("message", ""),
        "marshal": response.get("marshal"),
        "strategic_type": response.get("strategic_type"),
        # The target the QUESTION names — a bare "yes" must resolve to it,
        # not to whatever option happens to be listed first
        "interpreted_target": response.get("interpreted_target"),
        "raw_input": raw_input,
        "options": [dict(o) for o in options if isinstance(o, dict)],
    }
    current = dm.peek()
    if current is None:
        dm.push(dialogue)
        return True
    if dm.is_hard_stop():
        return False
    dm.preempt(dialogue)
    return True


def _resolve_option_command(dialogue: Dict, option: Dict) -> Optional[str]:
    """The full command an option resolves to. Prefers the option's own
    ``command``; falls back to the strategic keyword rebuild the Godot
    popup has always used for legacy-shaped options."""
    command = option.get("command")
    if command:
        return str(command)
    target = option.get("target")
    marshal = dialogue.get("marshal")
    if not target or not marshal or marshal == "Berthier":
        return None
    return strategic_reissue_command(
        marshal, str(dialogue.get("strategic_type") or ""), str(target))


def interpret_clarification_answer(dialogue: Dict, typed: str) -> Dict:
    """Deterministically interpret typed input as an answer to the pending
    clarification.

    Returns one of:
        {"kind": "command", "command": str}  — resolved; reissue this
        {"kind": "cancel"}                    — order withdrawn
        {"kind": "pass"}                      — not an answer; parse normally
    """
    text = (typed or "").strip().lower().rstrip(".!?")
    if not text:
        return {"kind": "pass"}
    if text in _CANCEL_WORDS:
        return {"kind": "cancel"}

    options = dialogue.get("options") or []
    actionable = [o for o in options if isinstance(o, dict)
                  and (o.get("command") or o.get("target"))]
    if not actionable:
        return {"kind": "pass"}

    # Numeric answer ("2") — 1-based option index
    if text.isdigit():
        index = int(text) - 1
        if 0 <= index < len(actionable):
            command = _resolve_option_command(dialogue, actionable[index])
            if command:
                return {"kind": "command", "command": command}
        return {"kind": "pass"}

    # Bare confirmation takes the option the QUESTION named (the
    # interpreted target) when known, else the first option. Adversarial
    # review: options are not guaranteed interpreted-first on every
    # emitter, and "yes" must never resolve to an enemy the question
    # didn't ask about.
    if text in _CONFIRM_WORDS:
        confirm_option = actionable[0]
        interpreted = dialogue.get("interpreted_target")
        if interpreted:
            for option in actionable:
                if option.get("target") == interpreted:
                    confirm_option = option
                    break
        command = _resolve_option_command(dialogue, confirm_option)
        if command:
            return {"kind": "command", "command": command}
        return {"kind": "pass"}

    # Name answer — exact, honorific-stripped, or edit-distance-1 typo
    from backend.commands.parser import _closest_by_edit_distance

    stripped = re.sub(r"^(?:marshal\s+)", "", text).strip()
    by_target = {str(o.get("target") or "").lower(): o for o in actionable
                 if o.get("target")}
    by_label = {str(o.get("label") or "").lower(): o for o in actionable
                if o.get("label")}
    # PF-2: an option may declare answer `aliases` — the natural-language verbs
    # its question text offered (e.g. a delegation ASK offers "give battle" /
    # "observe"). Matching them lets the player answer in the question's own
    # words instead of only the button label/target. Options without aliases
    # (every legacy clarification) are byte-unchanged.
    by_alias = {str(a).lower(): o for o in actionable
                for a in (o.get("aliases") or [])}
    option = (by_target.get(stripped) or by_label.get(stripped)
              or by_alias.get(stripped))
    if option is None and len(stripped) >= 3:
        near = _closest_by_edit_distance(stripped, list(by_target))
        if near is not None:
            option = by_target[near]
    if option is not None:
        command = _resolve_option_command(dialogue, option)
        if command:
            return {"kind": "command", "command": command}
    return {"kind": "pass"}
