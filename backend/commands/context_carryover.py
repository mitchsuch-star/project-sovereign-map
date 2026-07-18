"""CR-4 context carryover (COMMAND_ROBUSTNESS_SPEC §2).

Two deliverables built on the existing ``world.command_history`` substrate
(the last 50 structured ``{raw_input, marshal, action, target, turn}`` entries):

1. **Semantic Command History — reference resolution.** Deterministically
   rewrites shorthand references into a concrete command BEFORE the parser
   ever sees them (Golden Rule 6 — the parser and executor stay
   deterministic; the LLM is never consulted to resolve a reference):

   - ``again`` / ``do that again`` / ``same order`` / ``once more`` —
     repeat the last order verbatim.
   - ``same target`` / ``the same enemy`` / ``the same place`` — reuse the
     last order's objective; the enemy/place flavour prefers the last enemy /
     last province respectively.
   - ``him`` / ``her`` / ``them`` — the last enemy the player named.
   - ``there`` — the last province the player named (or, failing that, where
     the last-named enemy stands).
   - ``not you, Davout`` — re-address the last order to another marshal.

2. **Persistent Command Focus.** ``get_focus_marshal`` + ``try_focus_reissue``
   let a bare specific order ("hold", "move to Vienna") default to the
   marshal the player is already commanding instead of re-asking "Which
   marshal, Sire?". This is a fallback at the executor's "Marshal 'None'"
   seam — it only ever answers the question CR-2 would otherwise ask; it
   never overrides an explicitly-addressed marshal, a general/auto-assign
   order, or a collective ("everyone", "all marshals") order.

Design decisions of record (CR-4):
- **Mock mode records history too.** Recording used to be LLM-mode-only
  (repetition detection). Carryover references must resolve with the
  fast/mock parser as well, so main.py now records in both modes (skipping
  only while a diplomatic dialogue awaits an answer). The live-only
  repetition prompt is unaffected.
- **Focus is derived from history, not a new serialized field** — single
  source of truth, no serialization-enforcement churn.
- **``not you, X`` re-issues; it does not auto-undo the prior order.**
  Deterministic undo of an already-executed order (combat may have
  resolved) is unsafe; the reissue re-uses the last order's own phrasing
  addressed to X, and the player keeps ``cancel`` for standing orders.
"""

from typing import Dict, List, Optional

import re

from backend.ai.attack_vocabulary import targeting_anchor_words

# Actions that are not a repeatable field "order" — "again"/"not you" skip
# past them to the last real command (checking status then typing "again"
# should repeat the attack, not the status read).
_NON_ORDER_ACTIONS = frozenset({
    "status", "help", "economy", "debug", "end_turn", "cheat",
    "meta_command", "unknown", None,
})

# Internal action key -> the verb phrasing the parser re-reads cleanly. Most
# action keys ARE their own keyword ("attack", "hold", "scout", "fortify",
# "charge", "defend", "garrison", "recruit", "repair", "drill"); only a few
# need a preposition. Underscore keys ("form_square") normalize to spaces in
# the fallback below.
_ACTION_TO_VERB = {
    "move": "move to",
    "build": "build at",
    "pursue": "pursue",
    "support": "support",
    "reinforce": "support",
    "march": "march to",
}

# The "repeat the last order" phrase alternation, shared by the whole-input
# matcher and the "<Marshal>, <repeat>" addressed form. The trailing "again"
# is OPTIONAL for the "do the same" / "same" branches — a bare "do the same"
# (or "the same" / "same thing") is the same repeat intent as "do the same
# again", and a player who typed it was silently dropping through to the LLM,
# which parsed the vague phrase as a default attack (playtest finding).
_REPEAT_PHRASE = (
    r'do\s+(?:it|that|so)\s+again'
    r'|do\s+the\s+same(?:\s+again)?'
    r'|(?:the\s+)?same(?:\s+(?:order|command|thing|again))?'
    r'|again'
    r'|once\s+more'
    r'|repeat(?:\s+(?:that|it|the\s+order|the\s+last\s+order))?'
    r'|as\s+before'
)

# Whole-input "repeat the last order" family ("again", "do the same").
_REPEAT_RE = re.compile(
    r'^\s*(?:' + _REPEAT_PHRASE + r')\s*[.!]*\s*$',
    re.IGNORECASE)

# Addressed form: "<Marshal>, do the same" / "Davout, again" — repeat the last
# order's action+target, re-addressed to the named marshal ("Ney, scout Swabia"
# then "Davout, do the same" -> "Davout, scout Swabia"). Without this the
# marshal prefix blocks the whole-input _REPEAT_RE and the vague tail dropped to
# the LLM, which parsed it as a default attack (playtest finding).
_ADDRESSED_REPEAT_RE = re.compile(
    r'^\s*(?:marshal\s+)?(?P<marshal>[A-Za-z]+)\s*[,:]\s*(?:'
    + _REPEAT_PHRASE + r')\s*[.!]*\s*$',
    re.IGNORECASE)

# Leading "no / not you / wrong" re-address cue.
_READDRESS_CUE_RE = re.compile(
    r'^\s*(?:no+|not\s+you|not\s+him|not\s+her|nope|wrong(?:\s+marshal)?)\b'
    r'[\s,;:.–—-]*',
    re.IGNORECASE)
# One optional filler phrase between the cue and the marshal name
# ("not you — I meant Davout" / "no, give it to Davout").
_READDRESS_FILLER_RE = re.compile(
    r'^(?:'
    r'it(?:\'s| is| should\s+be| was)?'
    r'|i\s+(?:said|meant|want|wanted)'
    r'|give\s+(?:it\s+)?to'
    r'|send|let|have|use'
    r'|that\'?s|its'
    r')\b[\s,;:]*',
    re.IGNORECASE)

# In-command substitutions. "same <noun>" routes by the noun (finding-4):
# enemy-flavoured prefers the last enemy, place-flavoured the last region,
# and target/objective/one stay type-agnostic.
_SAME_TARGET_RE = re.compile(
    r'\b(?:the\s+)?same\s+'
    r'(?P<noun>target|objective|enemy|foe|place|position|province|city|town|spot|one)\b',
    re.IGNORECASE)
_SAME_ENEMY_NOUNS = frozenset({"enemy", "foe"})
_SAME_PLACE_NOUNS = frozenset({"place", "position", "province", "city", "town", "spot"})
_PERSON_PRONOUN_RE = re.compile(r'\b(?:him|her|them)\b', re.IGNORECASE)
_PLACE_DEIXIS_RE = re.compile(r'\bthere\b', re.IGNORECASE)

# A person pronoun / "there" is only a REFERENCE when it sits in object /
# destination position — immediately after a targeting or movement verb (or
# an object/destination preposition). Anchoring on the preceding word blocks
# the expletive/partitive/phrasal false positives the substitution would
# otherwise mangle ("is there time" -> "is <region> time"; "all of them" ->
# "all of <enemy>"; "hold them off" -> "hold <enemy> off").
#
# Single-sourced from backend/ai/attack_vocabulary.py (July 18, 2026). This
# set used to be an independent literal, and it had silently drifted WIDER
# than the fast parser's keyword table: it listed smash/crush/destroy/engage/
# assault/storm/rout, none of which the parser could route. So "Ney, attack
# Mack" then "Ney, crush him" resolved the pronoun perfectly and still
# produced a Berthier shrug. Deriving both from one vocabulary makes the
# anchor set a superset BY CONSTRUCTION — it can never again promise a
# reference the parser cannot act on.
_TARGETING_ANCHORS = targeting_anchor_words()
_MOVEMENT_ANCHORS = frozenset({
    "move", "march", "go", "head", "advance", "retreat", "deploy", "sail",
    "ride", "redeploy", "reinforce", "station", "hold", "defend", "garrison",
    "fortify", "attack", "scout", "pursue", "regroup", "rally", "to",
    "toward", "towards", "at", "into",
})

# Multi-marshal / collective addressees — focus must NOT silently collapse
# these to a single marshal (finding-3). Bare "all" is deliberately excluded
# ("hold at all costs" is a single-position order, not a collective).
_COLLECTIVE_RE = re.compile(
    r'\b(?:'
    r'everyone|everybody'
    r'|every\s+marshal|each\s+marshal'
    r'|both(?:\s+marshals?)?'
    r'|all\s+(?:marshals?|forces|units|corps|troops|of\s+(?:them|you|our|the))'
    r'|(?:the|our)\s+(?:whole\s+|entire\s+)?(?:army|corps|host|forces|men|troops)'
    r'|(?:whole|entire)\s+army'
    r')\b',
    re.IGNORECASE)


# "give" is DITRANSITIVE: in "give them hell" the pronoun is the indirect
# object and refers to the enemy, but in "give them autonomy" / "give them
# back their land" it refers to a vassal NATION. A preceding-word anchor is
# structurally the wrong instrument — adding a bare "give" to
# _TARGETING_ANCHORS rewrites "give them autonomy" into "give <enemy marshal>
# autonomy", injecting an enemy name into the vassal slot UPSTREAM of the
# parser guard that exists to prevent exactly that contamination.
#
# So the idiom is gated on its TAIL instead: only the combat senses resolve.
_GIVE_VERB_RE = re.compile(r"^giv(?:e|es|ing)$", re.IGNORECASE)
_GIVE_COMBAT_TAIL_RE = re.compile(
    r"^\s*(?:hell|no\s+quarter|the\s+bayonet|battle|a\s+thrashing|"
    r"a\s+bloody\s+nose)\b",
    re.IGNORECASE)


def _is_give_combat_idiom(preceding: Optional[str], tail: str) -> bool:
    """True for the combat sense of "give <pronoun> <object>" only.

    "give them hell" -> the pronoun IS the enemy, resolve it.
    "give them autonomy" / "give them back their land" -> a vassal order,
    leave the pronoun alone (the vassal family owns it)."""
    return bool(preceding and _GIVE_VERB_RE.match(preceding)
                and _GIVE_COMBAT_TAIL_RE.match(tail))


def _preceding_word(text: str, index: int) -> Optional[str]:
    """The alphabetic word immediately before ``index`` (lowercased), skipping
    intervening whitespace/punctuation — or None at the start of the string."""
    match = re.search(r"([A-Za-z']+)[\s,;:.!?]*$", text[:index])
    return match.group(1).lower() if match else None


# ── history accessors ────────────────────────────────────────────────────

def _history(world) -> List[Dict]:
    return list(getattr(world, "command_history", None) or [])


def _last_order_entry(world) -> Optional[Dict]:
    """The most recent recorded command that is a real field order (skips
    status/help/economy/end_turn/etc.)."""
    for entry in reversed(_history(world)):
        if entry.get("action") not in _NON_ORDER_ACTIONS:
            return entry
    return None


def _recent_targets(world) -> List[str]:
    return [e.get("target") for e in reversed(_history(world)) if e.get("target")]


def _last_target(world) -> Optional[str]:
    for target in _recent_targets(world):
        return target
    return None


def _is_region(world, name: Optional[str]) -> bool:
    return bool(name) and name in (getattr(world, "regions", None) or {})


def _is_enemy_marshal(world, name: Optional[str]) -> bool:
    if not name:
        return False
    marshal = world.get_marshal(name)
    return (marshal is not None
            and getattr(marshal, "nation", None) != getattr(world, "player_nation", None))


def _last_enemy_target(world) -> Optional[str]:
    for target in _recent_targets(world):
        if _is_enemy_marshal(world, target):
            return target
    return None


def _last_region_target(world) -> Optional[str]:
    for target in _recent_targets(world):
        if _is_region(world, target):
            return target
    return None


def _resolve_there(world) -> Optional[str]:
    """"there" prefers the last province named; failing that, the province
    the last-named enemy currently stands in."""
    region = _last_region_target(world)
    if region:
        return region
    enemy = _last_enemy_target(world)
    if enemy:
        marshal = world.get_marshal(enemy)
        location = getattr(marshal, "location", None) if marshal else None
        if location:
            return location
    return None


# ── reconstruction ───────────────────────────────────────────────────────

def _reconstruct_order(marshal_name: str, entry: Dict) -> str:
    """Rebuild a concrete command string ("Davout, attack Mack") from a
    stored order entry's action+target, addressed to ``marshal_name``.
    Underscore action keys ("form_square") normalize to their spoken form."""
    action = entry.get("action")
    verb = _ACTION_TO_VERB.get(action, (action or "hold").replace("_", " "))
    target = entry.get("target")
    if target:
        return f"{marshal_name}, {verb} {target}"
    return f"{marshal_name}, {verb}"


def _readdress_command(marshal_name: str, entry: Dict) -> str:
    """Re-address a stored order to ``marshal_name``, preserving the player's
    OWN phrasing: strip a leading addressed-marshal token from the raw input
    and prepend the new name (so "Ney, form square" -> "Davout, form square",
    dodging the underscore-key problem). Falls back to action+target
    reconstruction when the raw input is unavailable."""
    raw = (entry.get("raw_input") or "").strip()
    old = entry.get("marshal")
    if old and raw:
        raw = re.sub(r'^(?:marshal\s+)?' + re.escape(old) + r'\b\s*[,:]?\s*',
                     '', raw, flags=re.IGNORECASE).strip()
    if raw:
        return f"{marshal_name}, {raw}"
    return _reconstruct_order(marshal_name, entry)


def _field_marshal_names(world) -> List[str]:
    try:
        return [m.name for m in world.get_field_marshals()]
    except Exception:
        return []


def _match_roster_name(world, candidate: str) -> Optional[str]:
    """Resolve a typed marshal token to a live field-marshal name (exact,
    honorific-stripped, or edit-distance-1), or None."""
    if not candidate:
        return None
    from backend.commands.parser import _closest_by_edit_distance
    cleaned = re.sub(r'^(?:marshal\s+)', '', candidate, flags=re.IGNORECASE).strip()
    if not cleaned:
        return None
    roster = _field_marshal_names(world)
    for name in roster:
        if name.lower() == cleaned.lower():
            return name
    return _closest_by_edit_distance(cleaned, roster)


# ── public entry points ──────────────────────────────────────────────────

def resolve_context_references(command_text: str, world) -> Dict:
    """Deterministically resolve context references in ``command_text``.

    Returns one of:
        {"kind": "pass"}                      — no reference; parse as typed
        {"kind": "rewrite", "command": str}   — resolved; parse this instead
        {"kind": "error", "message": str}     — a reference with nothing to
                                                 resolve against (helpful
                                                 in-character reply)
    """
    if not command_text or world is None:
        return {"kind": "pass"}
    text = command_text.strip()
    if not text:
        return {"kind": "pass"}

    # 1. "again" — repeat the last order verbatim.
    if _REPEAT_RE.match(text):
        entry = _last_order_entry(world)
        if entry is None:
            return {"kind": "error",
                    "message": 'Berthier: "There is no previous order to '
                               'repeat, Sire."'}
        raw = entry.get("raw_input")
        command = raw if raw else _reconstruct_order(
            entry.get("marshal") or "", entry)
        return {"kind": "rewrite", "command": command.strip()}

    # 1b. "<Marshal>, do the same / again" — re-address the last order to the
    # named marshal. The whole-input _REPEAT_RE only fires on a bare phrase; the
    # marshal prefix would otherwise drop the vague tail to the LLM. Requires a
    # real roster name (a non-marshal leading word falls through untouched).
    addressed = _ADDRESSED_REPEAT_RE.match(text)
    if addressed:
        name = _match_roster_name(world, addressed.group("marshal"))
        if name is not None:
            entry = _last_order_entry(world)
            if entry is None:
                return {"kind": "error",
                        "message": 'Berthier: "There is no previous order to '
                                   'repeat, Sire."'}
            return {"kind": "rewrite",
                    "command": _readdress_command(name, entry)}

    # 2. "not you, X" — re-address the last order to another marshal. A cue
    # with no resolvable marshal is NOT a re-address (bare "no"/"not you" is a
    # dialogue decline or a correction like "no, attack him") — fall through
    # to the substitution phase on the cue-stripped remainder rather than
    # short-circuiting.
    substitution_base = text
    cue = _READDRESS_CUE_RE.match(text)
    if cue:
        rest = text[cue.end():].strip()
        filler = _READDRESS_FILLER_RE.match(rest)
        if filler:
            rest = rest[filler.end():].strip()
        rest = rest.rstrip(".!?").strip()
        matched = _match_roster_name(world, rest)
        if matched is not None:
            entry = _last_order_entry(world)
            if entry is None:
                return {"kind": "error",
                        "message": 'Berthier: "There is no prior order to '
                                   'reassign, Sire."'}
            return {"kind": "rewrite",
                    "command": _readdress_command(matched, entry)}
        substitution_base = rest

    # 3. In-command substitutions.
    working = substitution_base
    changed = False

    same = _SAME_TARGET_RE.search(working)
    if same:
        noun = same.group("noun").lower()
        if noun in _SAME_ENEMY_NOUNS:
            replacement = _last_enemy_target(world) or _last_target(world)
        elif noun in _SAME_PLACE_NOUNS:
            replacement = _last_region_target(world) or _last_target(world)
        else:
            replacement = _last_target(world)
        if replacement:
            working = _SAME_TARGET_RE.sub(replacement, working, count=1)
            changed = True
        else:
            return {"kind": "error",
                    "message": 'Berthier: "There is no previous objective to '
                               'reuse, Sire — name the target."'}

    # Person pronouns resolve ONLY to the last enemy (never a stray region —
    # finding-5) and only in object position after a targeting verb/preposition
    # (finding-2: not "all of them", "hold them off", "get them all").
    for person_match in _PERSON_PRONOUN_RE.finditer(working):
        _prev = _preceding_word(working, person_match.start())
        if _prev in _TARGETING_ANCHORS or _is_give_combat_idiom(
                _prev, working[person_match.end():]):
            enemy = _last_enemy_target(world)
            if enemy:
                working = (working[:person_match.start()] + enemy
                           + working[person_match.end():])
                changed = True
            break

    # "there" resolves only in destination position after a movement/positional
    # verb or "to"/"at"/"into" (finding-1: not the expletive "is there time" or
    # filler "stop right there").
    for there_match in _PLACE_DEIXIS_RE.finditer(working):
        if _preceding_word(working, there_match.start()) in _MOVEMENT_ANCHORS:
            referent = _resolve_there(world)
            if referent:
                working = (working[:there_match.start()] + referent
                           + working[there_match.end():])
                changed = True
            break

    if changed:
        return {"kind": "rewrite", "command": working.strip()}
    return {"kind": "pass"}


def get_focus_marshal(world):
    """The most recently EXPLICITLY-addressed player marshal still fit to
    command (alive, in the field), or None.

    Auto-assigned general orders record ``marshal=None``, so focus tracks
    who the player NAMED, not who a general order happened to reach.
    """
    player_nation = getattr(world, "player_nation", None)
    for entry in reversed(_history(world)):
        name = entry.get("marshal")
        if not name:
            continue
        marshal = world.get_marshal(name)
        if (marshal is not None
                and getattr(marshal, "nation", None) == player_nation
                and getattr(marshal, "strength", 0) > 0
                and not getattr(marshal, "administrative", False)):
            return marshal
    return None


def _focus_eligible_for(parsed: Dict, focus, world) -> bool:
    """The focus marshal can stand in for the missing executor only when the
    order is not about them — mirrors CR-2's clarification candidate filter."""
    command = parsed.get("command") or {}
    target = command.get("target")
    action = command.get("action")
    strategic_type = (parsed.get("strategic_type")
                      if parsed.get("is_strategic") else None)
    condition = parsed.get("strategic_condition") or {}
    condition_marshal = condition.get("until_marshal_arrives")
    if focus.name == target or focus.name == condition_marshal:
        return False
    is_movement = action == "move" or strategic_type == "MOVE_TO"
    if is_movement and target and getattr(focus, "location", None) == target:
        return False
    return True


def try_focus_reissue(world, parser, executor, parsed: Dict,
                      command_text: str, game_state: Dict,
                      llm_game_state: Dict):
    """Persistent Command Focus fallback for a bare specific order that
    failed on the missing marshal.

    Re-issues the order to the focus marshal, re-parsing + re-executing
    through the normal machinery. Returns ``(new_parsed, new_command_text,
    new_result)`` when focus resolved the order, or None to fall through to
    the CR-2 "Which marshal, Sire?" clarification.
    """
    # A collective order ("everyone fortify") is NOT a single-marshal order —
    # never silently collapse it to the focus marshal (finding-3). Let the
    # clarification handle it.
    if _COLLECTIVE_RE.search(command_text):
        return None

    focus = get_focus_marshal(world)
    if focus is None or not _focus_eligible_for(parsed, focus, world):
        return None

    focus_command = f"{focus.name}, {command_text.strip()}"
    reparsed = parser.parse(focus_command, llm_game_state, world=world)
    if not reparsed.get("success"):
        return None
    if not (reparsed.get("command") or {}).get("marshal"):
        return None

    focus_result = executor.execute(reparsed, game_state)
    # Only accept the reissue when it actually cleared the missing-marshal
    # failure — otherwise let the clarification fire as before.
    if "Marshal 'None' not found" in (focus_result.get("message") or ""):
        return None

    # Record the RESOLVED command so subsequent focus / "again" chain off the
    # marshal the player is now commanding (the bare form was already
    # recorded at parse time; both are harmless to the accessors).
    reparsed_command = reparsed.get("command") or {}
    world.add_to_command_history({
        "raw_input": focus_command,
        "marshal": reparsed_command.get("marshal"),
        "action": reparsed_command.get("action"),
        "target": reparsed_command.get("target"),
        "turn": int(world.current_turn),
    })

    # No "Continuing with X" note: the executor's own message always names
    # the marshal ("Grouchy fortifies…", "Ney objects…"), so the routing is
    # already transparent, and a note would contradict a mild objection.
    return (reparsed, focus_command, focus_result)
