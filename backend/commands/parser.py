"""
Command Parser for Project Sovereign
Converts natural language commands into validated, executable orders
"""

import re
from typing import Dict, List, Optional
from backend.ai.llm_client import (
    STAND_STILL_ALTERNATION,
    repair_leading_verb_typo,
    LLMClient,
    ADDRESS_TOKEN_RE,
    ADDRESS_NON_NAME_WORDS,
    SUPPORT_OBJECT_PREFIX_RE,
    CONDITION_CLAUSE_RE,
)
from backend.ai.attack_vocabulary import IDIOM_FILLER_WORDS
from backend.ai.clause_guards import (
    HONORIFIC,
    is_question,
    strip_deferred_clauses,
    strip_negated_clauses,
)
from backend.ai.validation import (
    META_ACTIONS,
    NEVER_STRATEGIC_ACTIONS,
    NON_ORDER_ACTIONS,
    PARSER_ONLY_META,
)
from backend.ai.generic_targets import normalize_target
from backend.ai.recruit_arm import extract_requested_arm
from backend.ai.nation_names import resolve_typed_nation
from backend.ai.strategic_parser import (
    detect_strategic_command, _nation_demonyms, demonym_to_nation,
)
from backend.utils.fuzzy_matcher import FuzzyMatcher

# CR-0: split camelCase scenario keys ("ArchdukeCharles") into their typed
# word forms when building skip-word sets (mirrors llm_client)
_CAMEL_SPLIT_RE = re.compile(r'(?<=[a-z])(?=[A-Z])')

# Aug 30, 2026 review: actions that are a READ or a housekeeping verb, never an
# order to a marshal. A parse that resolves to one of these must never be
# stamped `is_strategic` — the executor intercepts on that flag alone and would
# create (and begin) a real standing order off a question or a status query.
# Deliberately NOT the parser's `meta_actions` list, which also holds genuine
# orders (charge, restrain, build, repair, recruit); and deliberately NOT the
# executor's `free_actions`, which holds order-shaped verbs (retreat, wait)
# whose long-standing strategic upgrade is out of scope here.
# FA slice 7 (FA-N9): the set now lives in validation.NON_ORDER_ACTIONS —
# ONE list, read by llm_client's LLM-fallback gate too. This name is kept
# for the Aug-30 pin and every reader below.
_NON_ORDER_ACTIONS = NON_ORDER_ACTIONS

# FA slice 7 flip levers (each False reproduces the pre-slice behaviour).
ADMIN_VERBS_NEVER_MARCH = True      # the strategic gate reads NEVER_STRATEGIC_ACTIONS
A_BARE_RETREAT_IS_A_RETREAT = True  # "Ney, fall back" is not a MOVE_TO toward the enemy
ADMIRAL_IS_AN_ADDRESSEE = True      # "Villeneuve, order the diversion" accepts the admiral
_NAVAL_META_VERBS = frozenset({"build_fleet", "set_fleet_posture", "naval_diversion"})

# CR-2: sequential compound orders — "attack Bern, then hold your positions".
# The second clause used to leak into target extraction and strategic
# detection (phantom region "Your Positions" + a stray HOLD upgrade).
_SEQUEL_SPLIT_RE = re.compile(r'[,;]?\s+then\b\s+', re.IGNORECASE)
# A tail that STARTS with an attack verb is the long-standing
# attack-on-arrival hint ("march to Vienna then attack" / "... then attack
# Mack" / "... then engage the Austrians") — never split those.
# Adversarial-review fix: the first cut only exempted BARE verbs, which
# silently downgraded every named-object form to a plain MOVE_TO
# (strategic_parser._detect_attack_on_arrival matches "then attack" with
# ANY suffix, and _extract_target_text already strips the tail cleanly).
_ATTACK_ON_ARRIVAL_TAIL_RE = re.compile(
    r'^(?:attack|engage|assault)\b', re.IGNORECASE)
# FA-7. "Ney, wait for Davout then attack Mack" fought Mack immediately: the
# exemption above refuses to split ANY tail beginning with an attack verb, so
# the whole sentence stayed one parse and `attack` outranked `wait`. But
# attack-on-arrival is a MOVEMENT idiom — it means "march there and hit
# whatever you find". A first clause that orders the marshal to STAND STILL
# cannot carry an arrival, so the exemption has nothing to protect.
#
# `until` is excluded because it is the one condition the engine actually
# implements: "Ney, hold until Davout arrives then attack" is a supported
# standing HOLD and a pinned corpus row, and must stay one parse.
# FA slice 7 review round (R1-2): ONE stand-still vocabulary, shared with
# the mock chain's wait arm — the slice taught "stay here" / "rest your men"
# / "stand your ground" to the chain alone, and "Ney, stay here, then attack
# Mack" FOUGHT because this gate never saw the first clause as a halt.
_STAND_FAST_FIRST_CLAUSE_RE = re.compile(
    r'\b(?:' + STAND_STILL_ALTERNATION + r')\b', re.IGNORECASE)
_ENGINE_CONDITION_RE = re.compile(r'\buntil\b', re.IGNORECASE)


# ── FA-50: the compound shapes `then` never covered ─────────────────────────
# The split fired only on the literal word "then" (a `;` was consumed merely
# as an optional PREFIX to it), so every other way of writing two orders on
# one line went unsplit — and the title's "silently drop the second clause"
# is the kinder half of what happened. Measured on the 1805 boot, in 9 of 14
# compound shapes the SECOND clause's action and target were executed BY THE
# FIRST MARSHAL, in place of the order actually given, at 2 AP, reported as
# success: `Ney, attack Mack and hold Rhineland` made Ney HOLD, and
# `Ney, attack Mack and march to Vienna` marched him to Vienna.
#
# Two patterns, because they need different evidence.
_SEMICOLON_SPLIT_RE = re.compile(r'\s*;\s*')
# `and <Marshal>, <verb>` — a second marshal named outright.
_AND_MARSHAL_SPLIT_RE_TEMPLATE = r'\s+and\s+(?={names}\b)'
# A bare `and <verb>` cannot be split on sight: "defend and hold belgium",
# "secure and hold vienna", "Ney, defend and hold" and "Ney, fortify and
# hold position" are all LEGITIMATE single orders, pinned in the corpus and
# in test_systems_audit_v2_session5. The discriminator is measurable, not
# stylistic — see `_and_clause_is_a_second_order`.
_AND_VERB_SPLIT_RE = re.compile(
    r'\s+and\s+(?=(?:attack|assault|engage|storm|charge|bombard|retreat'
    r'|withdraw|move|march|advance|scout|hold|defend|fortify|entrench'
    r'|drill|wait|garrison|recruit|build|repair|support|reinforce'
    r'|pursue|chase|blockade)\b)',
    re.IGNORECASE)
# The hold IDIOMS. These are one order, not two, and `llm_client`'s own hold
# branch enumerates them verbatim — "defend and hold", "fortify and hold",
# "secure and hold". `defend and hold belgium` and `Ney, fortify and hold
# position` are pinned in the golden corpus and in
# test_systems_audit_v2_session5; splitting them would turn a single order
# into an order plus a warning about a clause the player never meant to give.
# A drift pin holds this list against `llm_client`'s.
_HOLD_IDIOM_RE = re.compile(r'\b(?:defend|fortify|secure)\s+and\s+hold\b',
                            re.IGNORECASE)


def _player_marshal_names(game_state) -> list:
    world = (game_state or {}).get("world")
    player = getattr(world, "player_nation", None)
    return [name for name, m in (getattr(world, "marshals", {}) or {}).items()
            if getattr(m, "nation", None) == player]


def _split_sequential_orders(command_text: str, game_state=None):
    """Split "<first order>, then <second order>" into (first, tail), or
    None when the command is not a sequential compound.

    FA-50 widens the boundary from `then` alone to `;` and to `and` before a
    second marshal. The bare `and <verb>` arm is decided by the caller,
    which alone can trial-parse both clauses.
    """
    match = _SEQUEL_SPLIT_RE.search(command_text)
    if not match:
        match = _SEMICOLON_SPLIT_RE.search(command_text)
    if not match:
        names = _player_marshal_names(game_state)
        if names:
            pattern = _AND_MARSHAL_SPLIT_RE_TEMPLATE.format(
                names="|".join(re.escape(n) for n in sorted(names, key=len,
                                                            reverse=True)))
            match = re.search(pattern, command_text, re.IGNORECASE)
    if not match:
        return None
    first = command_text[:match.start()].strip().rstrip(',;')
    tail = command_text[match.end():].strip()
    if not first or not tail:
        return None
    if _ATTACK_ON_ARRIVAL_TAIL_RE.match(tail) and not (
            _STAND_FAST_FIRST_CLAUSE_RE.search(first)
            and not _ENGINE_CONDITION_RE.search(first)):
        return None
    return (first, tail)


# ══════════════════════════════════════════════════════════════════════════
# NP-1 — THE EMPEROR'S HAND (NAPOLEON_SPEC.md §4.1)
# Sovereign address normalization: orders to the sovereign are the player's
# own will, so they accept first-person phrasing. A raw-string rewrite at
# the TOP of parse (the CR-4 precedent) so the fast parser, the LLM, fuzzy
# matching and detect_strategic_command all agree by construction. Fires
# ONLY when a sovereign exists in the player roster — every other world
# parses byte-identically (the NP dormancy pin).
# ══════════════════════════════════════════════════════════════════════════

# The ONE military/movement verb set both no-comma arms gate on. Kept as
# a single source so the Emperor-lead and first-person forms can never
# drift apart (they did: the lead arm shipped with no verb requirement at
# all — see below).
# NP-V follow-up: EVERY verb here must be one the parser can actually act
# on, or the rewrite binds the Emperor to an order the executor then
# refuses — the advisory-diverges-from-executor shape this project keeps
# fighting. Measured at the endpoint, which retired four: `ride` and
# `advance` (both shipped in the NP-1 list and neither parses) and
# `take`/`besiege` (added, then measured, then dropped).
#
# ⚠ The spec's own worked example — §4.1 "the Emperor will take Vienna" —
# therefore does NOT rewrite, because `take` is not a verb this game has.
# The spec is wrong there, not the code; recorded in §15.8.
#
# `test_every_sovereign_order_verb_actually_parses` is the standing guard.
_SOVEREIGN_ORDER_VERBS = (
    r"attack|march|move|withdraw|retreat|fortify|"
    r"hold|scout|charge|bombard|defend|pursue|assault|storm|drill|"
    r"seize|garrison|reinforce|support")
_SOVEREIGN_MODALS = r"(?:(?:will|shall|must|am\s+going\s+to)\s+)?"

# "(the) Emperor, attack Vienna" — today this hard-errors
# "Marshal 'Emperor' not found".
_SOVEREIGN_EMPEROR_COMMA_RE = re.compile(
    r"^\s*(?:the\s+)?emperor\s*[,:]\s*", re.IGNORECASE)
# "the Emperor will march to Swabia" — the no-comma form.
#
# NP-V follow-up: this arm originally required only the article and NO
# verb, so ANY sentence opening "the Emperor …" was rewritten into an
# order — including one about a DIFFERENT sovereign. Measured:
#   "the Emperor of Austria demands Venetia"
#       -> "Napoleon, of Austria demands Venetia"
#   "the Emperor is displeased"  -> "Napoleon, is displeased"
# It now gates on the same verb set as the first-person arm, so a title
# ("the Emperor of Austria") and a remark ("the Emperor is displeased")
# both pass through untouched.
# The modal is CONSUMED, not carried, so this arm strips to the verb
# exactly as the first-person arm does — otherwise "the Emperor will take
# Vienna" rewrote to "Napoleon, will take Vienna" and the parser, which
# has no "will take" verb, dropped the whole order.
_SOVEREIGN_EMPEROR_LEAD_RE = re.compile(
    r"^\s*the\s+emperor\s+" + _SOVEREIGN_MODALS
    + r"(?=(?:" + _SOVEREIGN_ORDER_VERBS + r")(?:e?s)?\b)",
    re.IGNORECASE)
# Leading first person with a military/movement verb ONLY (gate b) —
# "I will march to Ulm", "I'll attack Vienna", "I ride for the Rhine".
# Diplomacy keeps its verbs (no "I offer/I propose" forms rewrite).
_SOVEREIGN_FIRST_PERSON_RE = re.compile(
    r"^\s*i(?:['’]ll)?\s+" + _SOVEREIGN_MODALS
    + r"(?P<verb>" + _SOVEREIGN_ORDER_VERBS + r")\b",
    re.IGNORECASE)
# "march to Ulm myself" / "scout Bavaria in person" — trailing marker.
#
# ⚠ NP promise audit (Aug 15, 2026): this arm shipped with NO verb gate —
# the third sibling of the defect §15.8 item 3 fixed for the Emperor-lead
# arm, left live here. §4.1's gate (b) is "military/movement verbs only;
# diplomacy keeps its verbs", and without it every trailing-"myself"
# sentence became an order to the Emperor:
#   "I will offer an alliance to Prussia myself"
#       -> "Napoleon, I will offer an alliance to Prussia"
#   "review the terms myself"     -> "Napoleon, review the terms"
# Measured at the mock layer the outcomes happened to be unchanged (the
# keyword parser ignores the prefix), so nothing complained — but the
# rewrite runs UPSTREAM OF BOTH PARSERS, so in live mode the LLM is handed
# a marshal-addressed diplomatic sentence and invited to make it a
# marshal's order. The body must contain a real order verb, exactly as the
# other two arms require.
_SOVEREIGN_SELF_MARKER_RE = re.compile(
    r"\b(?:myself|in\s+person)\s*[.!]?\s*$", re.IGNORECASE)
_SOVEREIGN_BODY_HAS_VERB_RE = re.compile(
    r"\b(?:" + _SOVEREIGN_ORDER_VERBS + r")(?:e?s|ing|ed)?\b", re.IGNORECASE)


def _find_player_sovereign(world=None, game_state=None) -> Optional[str]:
    """The player roster's standing sovereign marshal name, or None.

    Live world first (the CR-0 discipline); the LLM game_state's
    player-only marshals dict as the fallback so mock-only parses see the
    same roster. A captured sovereign still resolves — the downstream
    prisoner guard answers the order honestly ("he sits in a foreign
    capital") instead of a phantom-marshal error.
    """
    if world is not None:
        player_nation = getattr(world, "player_nation", None)
        for m in getattr(world, "marshals", {}).values():
            # NP-V (adversarial review P1, reproduced through /command): a
            # CAPTURED sovereign must not resolve here. The PC15-4
            # lost-marshal guard runs upstream in main.py and keys on a
            # leading comma-address, so it never sees "I fortify" /
            # "Emperor, fortify" / "march to X myself" — the prisoner
            # accepted orders, was charged AP, and (worse) came home from
            # captivity fortified and locked in a stance he never chose.
            # `context_carryover._player_sovereign_name` already filtered
            # this; the two seams now agree.
            if (m.nation == player_nation
                    and getattr(m, "is_sovereign", False)
                    and not getattr(m, "captured_by", "")):
                return m.name
        return None
    if game_state:
        marshals = game_state.get("marshals")
        if isinstance(marshals, dict):
            for name, info in marshals.items():
                if (isinstance(info, dict)
                        and info.get("personality") == "sovereign"):
                    return info.get("name", name)
    return None


def normalize_sovereign_address(command_text: str,
                                sovereign_name: str) -> str:
    """Rewrite sovereign-address forms to a canonical marshal address.

    Order of rules matters:
      1. Emperor forms first — "Emperor," IS a leading address token today
         (a failed name attempt), so they must run before the gate below.
      2. An explicit address token always wins (gate a: "Ney, I want you
         to move to Lorraine" is Ney's order — corpus row pinned).
      3. The question detector runs before the first-person arm (gate c:
         "Can I attack Vienna?" stays help) — structurally redundant since
         an interrogative lead never matches the first-person regex, but
         kept as the belt the spec names.
    """
    if not sovereign_name or not command_text:
        return command_text

    # The trailing self-marker is CONSUMED, not carried. Live-drive
    # finding (NP-V): keeping it produced the phantom province "Bavaria
    # Myself" — the destination extraction reads to end-of-string and
    # never consults the fuzzy skip lists, so the reflexive-word guards
    # below could not save it. The raw phrasing still survives on the
    # order's `original_command` (rider (d)'s record seam).
    #
    # ⚠ NP promise audit (Aug 15, 2026): that fix stripped the marker
    # inside its OWN arm only, and the two arms above it return first — so
    # the phantom came straight back the moment a player COMBINED the
    # forms, which is the more natural phrasing of the two:
    #   "I will march to Swabia myself"        -> target 'Swabia Myself'
    #   "the Emperor will march to Swabia myself" -> target 'Swabia Myself'
    # Strip once, up front, so every arm below is marker-free. If no arm
    # fires the ORIGINAL text is returned untouched — a sentence we do not
    # rewrite never silently loses a word.
    text = command_text
    marker = _SOVEREIGN_SELF_MARKER_RE.search(command_text)
    if marker:
        stripped = command_text[:marker.start()].rstrip().rstrip(",")
        if stripped:
            text = stripped

    match = _SOVEREIGN_EMPEROR_COMMA_RE.match(text)
    if match:
        return f"{sovereign_name}, {text[match.end():]}"
    match = _SOVEREIGN_EMPEROR_LEAD_RE.match(text)
    if match:
        return f"{sovereign_name}, {text[match.end():]}"
    if _leading_addressed_token(text):
        # Gate (a): an address token always wins — this stays HIS order.
        # But the marker still must not survive into the destination:
        # "Ney, march to Swabia myself" was parsing to the phantom
        # province 'Swabia Myself'. NP-1 claimed this family closed by
        # adding "myself" to both fuzzy skip lists; it is not, because the
        # destination extraction reads to end-of-string and never consults
        # them (NP-V's own note). Scoped to sovereign worlds, so the
        # dormancy pin is untouched; the general seam is routed (§15.9).
        if marker and text is not command_text and _SOVEREIGN_BODY_HAS_VERB_RE.search(text):
            return text
        return command_text
    if is_question(text):
        return command_text
    match = _SOVEREIGN_FIRST_PERSON_RE.match(text)
    if match:
        return f"{sovereign_name}, {text[match.start('verb'):]}"
    if marker and text is not command_text:
        if _SOVEREIGN_BODY_HAS_VERB_RE.search(text):
            return f"{sovereign_name}, {text}"
    return command_text


def _leading_addressed_token(command_text: str) -> Optional[str]:
    """The leading comma-addressed token ("Murat, charge" → "Murat"), or
    None when the command has no address prefix or it is an interjection /
    bare order verb ("No, charge!")."""
    match = ADDRESS_TOKEN_RE.match(command_text)
    if not match:
        return None
    token = match.group(1)
    if len(token) < 3 or token.lower() in ADDRESS_NON_NAME_WORDS:
        return None
    return token


def _names_the_admiral(token: str, world) -> bool:
    """FA slice 7: the player's fleet has a named admiral (Villeneuve on the
    1805 boot); an address to him on a naval verb is decoration, not a
    marshal typo to clarify."""
    if not token or world is None:
        return False
    try:
        fleets = getattr(world, "fleets", None) or {}
        record = fleets.get(getattr(world, "player_nation", None)) or {}
        admiral = str(record.get("admiral") or "")
    except Exception:
        return False
    return bool(admiral) and token.strip().lower() == admiral.lower()


# WO-1 boundary (review round, Aug 21 2026): a lead followed by one of
# these is NARRATION, not an address — third-person inflections and
# auxiliaries cannot be imperatives, so "Mack is at Swabia, Ney attack him"
# keeps its correct parse while "Kutuzov, retreat" (imperative next word)
# still refuses. Closed-class by construction: only forms an imperative
# order can never take.
_NARRATION_NEXT_WORDS = frozenset({
    "is", "was", "are", "were", "has", "have", "had", "will", "shall",
    "would", "may", "might", "must", "can", "cannot", "seems", "appears",
    "holds", "held", "approaches", "approached", "advances", "advanced",
    "marches", "marched", "moves", "moved", "stands", "stood", "lands",
    "landed", "remains", "remained", "nears", "neared", "retreats",
    "retreated", "withdraws", "withdrew", "flees", "fled", "surrenders",
    "surrendered", "comes", "came", "waits", "waited", "camps", "camped",
    "threatens", "threatened", "sits", "still",
})


def _resolve_enemy_addressee(command_text: str, known_enemies: List[str],
                             known_regions: List[str]):
    """WO-1: the raw command's LEADING token resolved against the enemy
    roster — the addressee register the whole guard family keys on.

    An enemy name in the ADDRESSEE slot is a command TO the enemy, not a
    target reference: "Kutuzov, retreat" executed a bare army-wide retreat
    (every French corps changed province), "Mack, attack Vienna" sent the
    whole army at Swabia, "Kutuzov, scout Swabia" made Soult scout. Keyed
    on the name's leading position, never the comma — "Kutuzov retreat"
    without one behaved identically. Returns `(enemy_name, arm, token)`
    with arm in {"exact", "typo"}, or None when the lead is not an enemy
    addressee.

    Deliberate boundaries:
    * a lead that is ALSO a region name is NOT treated as an enemy
      ("Vienna, hold" stays a region address) — but the EXACT enemy roster
      is consulted first, so a real commander who shares a province name is
      still refused by name. ⚠ AMENDED by WO slice 10, September 1, 2026:
      this clause used to read "`Brunswick` … resolves as the province, the
      recorded WO-13 collision rule", and that was false in both halves.
      There is no province-addressee route at all, and the carve-out was
      letting the player COMMAND the Prussian marshal Brunswick. The rule,
      stated once in `executor._correction_survives`, is that the name means
      the MAN wherever a man can be meant; the province is reached by a
      region-only verb (`move to Brunswick`);
    * possessive leads are narration, not address ("Kutuzov's corps…"),
      and so is a lead followed by a third-person/auxiliary form
      (`_NARRATION_NEXT_WORDS` — none of them can be an imperative, so
      "Mack has surrendered, march on Vienna" keeps its pre-guard parse
      while "Mack, attack Vienna" still refuses);
    * the TYPO arm requires the explicit comma-address shape AND a token
      that is not ordinary English (`_NON_TARGET_WORDS` — "More, cavalry
      to the front" must never become Moore); the CALLER additionally
      gives the player roster right of first refusal on typo'd addresses
      ("Mark, attack" belongs to the CR-2 did-you-mean flow, not to an
      enemy refusal).
    """
    text = command_text.strip()
    honorific = re.match("^" + HONORIFIC, text, flags=re.IGNORECASE)
    if honorific:
        text = text[honorific.end():]
    words = text.split()
    if not words:
        return None

    def _narration_follows(n_words: int) -> bool:
        if len(words) <= n_words:
            return False
        next_word = words[n_words].strip(",:;.!?-—").lower()
        return next_word in _NARRATION_NEXT_WORDS

    region_forms = set()
    for region in known_regions:
        region_forms.add(region.lower())
        region_forms.add(_CAMEL_SPLIT_RE.sub(" ", region).lower())
    enemy_forms = {}
    for enemy in known_enemies:
        enemy_forms[enemy.lower()] = enemy
        enemy_forms[_CAMEL_SPLIT_RE.sub(" ", enemy).lower()] = enemy

    for n_words in (2, 1):
        if len(words) < n_words:
            continue
        token = " ".join(words[:n_words]).rstrip(",:;.!?").strip()
        token_lower = token.lower()
        if (len(token_lower) < 3
                or token_lower in ADDRESS_NON_NAME_WORDS
                or token_lower.endswith("'s") or token_lower.endswith("s'")
                or token_lower.endswith("’s")):
            continue
        # WO-13: the ENEMY roster is consulted BEFORE the region carve-out.
        # The carve-out exists so an ordinary place word is never read as an
        # address ("Vienna, hold"); it must not shelter a real enemy
        # commander who happens to share a province name. Measured: with the
        # carve-out first, `Brunswick, hold` skipped slice 2's refusal
        # entirely and the executor let FRANCE FORTIFY A PRUSSIAN MARSHAL AT
        # BERLIN — the one collision on the board punched the one hole in
        # slice 2's guard. `Mack` and `Kutuzov` were refused all along; only
        # the province-named marshal escaped.
        match = enemy_forms.get(token_lower)
        if match:
            if _narration_follows(n_words):
                return None
            return (match, "exact", token)
        if token_lower in region_forms:
            return None

    addressed = _leading_addressed_token(command_text)
    if (addressed and addressed.lower() not in region_forms
            and addressed.lower() not in _NON_TARGET_WORDS):
        for enemy in known_enemies:
            if _plausible_name_typo(addressed, enemy):
                return (enemy, "typo", addressed)
    return None


def _edit_distance_at_most(a: str, b: str, limit: int) -> bool:
    """True if Levenshtein(a, b) <= limit. Band-limited DP — strings here
    are short name candidates."""
    if abs(len(a) - len(b)) > limit:
        return False
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        row_min = i
        for j, cb in enumerate(b, 1):
            cost = min(previous[j] + 1,
                       current[j - 1] + 1,
                       previous[j - 1] + (ca != cb))
            current.append(cost)
            row_min = min(row_min, cost)
        if row_min > limit:
            return False
        previous = current
    return previous[-1] <= limit


def _closest_by_edit_distance(word: str, names, limit: int = 1):
    """The unique name within `limit` edits of `word` (case-insensitive),
    or None when zero or multiple qualify. Used to keep an edit-distance-1
    enemy-name typo ('Mach') from fuzzy-drifting into a region whose
    partial-ratio score happens to be higher ('La Mancha')."""
    word_lower = word.lower()
    hits = [n for n in names if _edit_distance_at_most(word_lower, n.lower(), limit)]
    return hits[0] if len(hits) == 1 else None


# PARSE-NEG evaluation: ordinary English words the free-text target scan below
# used to fuzzy-match into real provinces. The loose partial-ratio scorer is
# what made the corpus of victims so strange — "not" became Brabant, "how"
# Buxhowden, "able" Naples, "happens" White Russia, "lost" Ulster, "thinking"
# Wales, "square" Normandy, "rente" Crete — and every one of them rode out at
# confidence 0.9, above the LLM-fallback gate, as the province a marshal was
# ordered to attack. This list is the first of two independent gates; the
# second (`_plausible_name_typo`) catches the ones no stopword list can, such
# as "relieved" -> Rhineland.
_NON_TARGET_WORDS = frozenset({
    # determiners / quantifiers / degree
    "all", "any", "both", "each", "every", "few", "many", "more", "most",
    "much", "less", "least", "no", "none", "some", "such", "own", "same",
    "other", "another", "enough", "very", "too", "quite", "rather", "just",
    "only", "even", "still", "again", "also", "once", "twice",
    # pronouns / possessives beyond the existing deixis list
    "his", "hers", "its", "ours", "yours", "theirs", "who", "whom", "whose",
    "what", "which", "why", "how", "when", "where", "whether",
    "myself", "ourselves", "himself", "herself", "themselves", "itself",
    # auxiliaries / modals / common verbs that are never place names
    "are", "was", "were", "been", "being", "has", "have", "had", "does",
    "did", "done", "will", "would", "shall", "should", "can", "could",
    "may", "might", "must", "let", "get", "got", "put", "keep", "kept",
    "make", "made", "take", "took", "give", "gave", "come", "came", "went",
    "know", "knew", "think", "thought", "thinking", "want", "wanted",
    "need", "needed", "like", "liked", "seem", "look", "looking", "tell",
    "told", "say", "said", "ask", "asked", "able", "unable", "happens",
    "happen", "happened", "lost", "lose", "win", "won", "sure", "please",
    "possible", "impossible", "ready", "relieved", "relief",
    # prepositions / conjunctions / connectives
    "about", "above", "across", "after", "against", "along", "among",
    "around", "away", "back", "because", "before", "behind", "below",
    "beneath", "beside", "between", "beyond", "but", "down", "during",
    "except", "from", "into", "near", "off", "onto", "out", "over",
    "past", "since", "than", "through", "toward", "towards", "under",
    "until", "unless", "upon", "with", "within", "without", "while",
    "whilst", "however", "instead", "therefore", "though", "although",
    # military prose nouns that are not places
    "attacking", "attacked", "defending", "defended", "moving", "moved",
    "holding", "held", "advance", "advancing", "retreating", "retreated",
    "position", "positions", "ground", "line", "lines", "flank", "flanks",
    "front", "rear", "centre", "center", "wing", "wings", "square",
    "formation", "column", "columns", "corps", "division", "brigade",
    "regiment", "battalion", "battery", "guns", "gun", "cannon", "sabre",
    "bridge", "river", "road", "roads", "hill", "hills", "ridge", "wood",
    "woods", "village", "town", "city", "fort", "forts", "pass", "passes",
    "field", "fields", "supply", "supplies", "orders", "order", "command",
    "battle", "war", "campaign", "victory", "defeat", "casualties",
    "morale", "strength", "men", "soldier", "soldiers", "prisoners",
    "rente", "pension", "estate", "duchy", "treasury", "gold",
})

# Words shorter than this can only bind as an EXACT name — a three-letter
# fuzzy hit is noise, not a typo.
_MIN_FUZZY_TARGET_LEN = 4


# Aug 30, 2026 review: a word that an article or a locative preposition
# introduces is a common noun, not a commander — "across the moor" is not a
# typo for Moore. Used by the free-text enemy scan, which had no shape gate at
# all where its siblings gate on `_plausible_name_typo`.
_NAME_BLOCKING_PREFIXES = frozenset({
    "the", "a", "an", "this", "that", "these", "those",
    "across", "over", "through", "along", "behind", "beyond", "near",
    "past", "around", "beside", "below", "above", "under", "onto", "upon",
})


def _introduced_by_article(command_text: str, token: str) -> bool:
    """True when `token` appears in `command_text` behind an article or a
    locative preposition — "attack across the moor", "hold the pass".

    Companion to `_NAME_BLOCKING_PREFIXES` for the arm that has already
    extracted a target PHRASE and so cannot look at the previous word itself.
    """
    if not command_text or not token:
        return False
    words = [w.strip(",.!?;:").lower() for w in command_text.split()]
    head = token.strip().split()[0].strip(",.!?;:").lower()
    for i, w in enumerate(words):
        if w == head and i and words[i - 1] in _NAME_BLOCKING_PREFIXES:
            return True
    return False


def _is_targetable_enemy(name: str, world) -> bool:
    """False for a prisoner or a spent corps.

    A captured marshal stays in `world.marshals` at strength 0 sitting at his
    captor's capital, so the omniscient roster the free-text scan reads still
    offers him as an attack target. PC15-4 refuses him by name one layer down;
    this stops a stray sentence word from ever nominating him.
    """
    if world is None:
        return True
    try:
        marshal = world.get_marshal(name)
    except Exception:
        return True
    if marshal is None:
        return True
    return not getattr(marshal, "captured_by", None) and getattr(
        marshal, "strength", 0) > 0


def _plausible_name_typo(word: str, candidate: str) -> bool:
    """True when `word` is close enough to `candidate` to be a typed mistake.

    The fuzzy matcher scores by partial ratio, which rewards a short word for
    being contained in a long name — that is how "relieved" scored high enough
    against "Rhineland" (shared 'r', similar length, almost no letters in
    common) to become a marshal's destination. Real typos stay within a couple
    of edits AND keep their first letter, which is the same shape the CR-1
    marshal-scan guard uses; this is its target-side twin.
    """
    if len(word) < _MIN_FUZZY_TARGET_LEN:
        return False
    if word[:1].lower() != candidate[:1].lower():
        return False
    limit = 2 if len(word) >= 6 else 1
    return _edit_distance_at_most(word.lower(), candidate.lower(), limit)


# PT-H3: promoted from a method local so the demonym-hint stamp at the
# end of `parse` reads the SAME set the drop rules read, rather than a
# second copy that could drift.
VASSAL_FAMILY_ACTIONS = ("invest_vassal", "release_vassal",
                         "make_vassal", "change_autonomy",
                         "grant_region_to_vassal",
                         # AI-2b: instrument targets are nations too
                         "sponsor_design", "buy_off_design",
                         "guarantee_nation")


def _is_nation_demonym(target: Optional[str], world) -> bool:
    """True if `target` names a NATION's army by demonym ("the Austrians",
    "Prussians", "Austrian") rather than a province.

    Demonyms must NEVER be fuzzy-rewritten into a region: "Austrians" fuzz-
    matched the Spanish province "Asturias" (playtest finding). Word-boundary
    matched against the live roster's demonyms, so a place name that merely
    contains a demonym substring is not caught. Returns False with no world
    (tests) — same as the pre-fix behavior."""
    if not target or world is None:
        return False
    try:
        demonyms = set(_nation_demonyms(world))
    except Exception:
        return False
    if not demonyms:
        return False
    tokens = re.findall(r"[A-Za-z]+", target.lower())
    return any(tok in demonyms for tok in tokens)


def _build_fallback_known_enemies() -> List[str]:
    """
    Build the fallback enemy marshal roster by inspecting the canonical
    marshal factory rather than hardcoding names (SCALE_READINESS_PLAN §3.4).

    This is only used when no live world state is provided to the parser.
    """
    try:
        from backend.models.marshal import create_enemy_marshals
        return list(create_enemy_marshals().keys())
    except Exception:
        return []


def _extract_enemy_marshal_names(world, player_nation: Optional[str]) -> List[str]:
    """Return all marshal names in `world` that do NOT belong to player_nation."""
    marshals = getattr(world, "marshals", None) or {}
    names: List[str] = []
    for name, marshal in marshals.items():
        if player_nation and getattr(marshal, "nation", None) == player_nation:
            continue
        names.append(name)
    return names


def _extract_player_marshal_names(world, player_nation: Optional[str]) -> List[str]:
    """Return all marshal names in `world` that DO belong to player_nation."""
    marshals = getattr(world, "marshals", None) or {}
    names: List[str] = []
    for name, marshal in marshals.items():
        if player_nation and getattr(marshal, "nation", None) != player_nation:
            continue
        names.append(name)
    return names


class CommandParser:
    """
    Parses player commands and validates them against game state.
    Uses LLM client to interpret natural language.
    """

    def __init__(self, use_real_llm: bool = None):
        """
        Initialize the parser with an LLM client.

        Args:
            use_real_llm: If True, use real Claude API. If False, use mock.
                         If None (default), read from LLM_MODE environment variable.
        """
        # Pass None to let LLMClient read from environment
        self.llm = LLMClient(use_real_api=use_real_llm)
        self.fuzzy_matcher = FuzzyMatcher()

        # Fallback player-marshal roster (CR-0) — matches the legacy
        # create_starting_marshals() factory. Only used when no live world
        # is passed to parse() (cold command parsing in unit tests); normal
        # gameplay reads live names via `_get_player_marshals(world)`.
        self.valid_marshals = ["Ney", "Davout", "Grouchy", "Drouot"]

        # Valid actions
        # NOTE: When adding new actions, update ALL of these locations:
        # 1. validation.py: Add to VALID_ACTIONS set (single source of truth for LLM)
        # 2. executor.py: Add _execute_* method
        # 3. executor.py: Update help_text in _execute_help()
        # 4. executor.py: Add to objection_actions if personality can object
        # 5. llm_client.py: Add keyword detection for mock parser (~line 416+)
        # 6. prompt_builder.py: Add few-shot example if action is complex/ambiguous
        # 7. personality.py: Add triggers if marshals can object to it
        # 8. world_state.py: Add cost to _action_costs dict
        # 9. CLAUDE.md: Update documentation
        self.valid_actions = [
            "attack", "defend", "retreat", "move", "scout",
            "recruit", "help", "end_turn",
            # CR-1: typed "status" was the ONLY leg missing — VALID_ACTIONS
            # (validation.py:92), the mock parser, and the executor
            # (free_actions + _execute_status) all already supported it,
            # but this list's omission sent it to Berthier recovery.
            "status",
            # Tactical state actions (Phase 2.6)
            "drill", "fortify", "unfortify",
            # Stance system (Phase 2.7)
            "stance_change",
            # Hold/Wait actions
            "hold",  # Alias for defend - same mechanics
            "wait",  # Free action (0 cost) - pass turn for this marshal
            # Debug commands (Phase 2.8)
            "debug",  # For testing abilities: /debug counter_punch Davout
            # Cavalry recklessness (Phase 3)
            "charge",    # Glorious Charge - available at recklessness >= 1
            "restrain",  # Restrain marshal - normal attack instead of charge
            # Strategic cancel (Phase E)
            "cancel",    # Cancel active strategic order
            # Economy actions (Phase 6.2.E)
            "build",     # Build a building at a region
            "repair",    # Repair war damage or damaged building
            # Economy info command (Phase 6.2.G)
            "economy",   # Display treasury/income/upkeep (free action)
            # Garrison command (Session 31)
            "garrison",  # Detach troops to garrison a region
            # Square formation (Session 67) — Tactical Triangle Part A
            "form_square",   # Infantry anti-cavalry formation (1 AP)
            "break_square",  # Return to line formation (free)
            # Vassal System (Phase 8 Session 5)
            "invest_vassal",    # Invest in vassal (+10 loyalty)
            "change_autonomy",  # Change vassal autonomy level
            "make_vassal",      # Create a vassal
            "release_vassal",   # Release a vassal nation (P8-4 sync)
            "grant_region_to_vassal",  # VS-3: cede a province to a vassal
            # AI-2b D5 counter-instruments (AI_INTENT_SPEC §6 D5)
            "sponsor_design",    # Directed sponsorship / licence
            "buy_off_design",    # Compensation — buy off a design
            "guarantee_nation",  # Pledge to defend a nation
            # Strategic actions (LLM may return these directly) — P8-4 sync
            "pursue",           # Strategic PURSUE - chasing enemy marshal
            "support",          # Strategic SUPPORT - marching to ally
            "reinforce",        # Alias for support
            "march",            # Strategic MOVE_TO - multi-turn movement
            # Diplomatic meta-actions — P8-4 sync
            "diplomatic_proposal",     # Start diplomatic proposal dialogue
            "diplomatic_mission",      # Start diplomatic mission
            "diplomatic_feasibility",  # Request feasibility check
            "diplomatic_advisory",     # Request advisory conversation
            "diplomatic_error",        # Diplomatic error fallback
            # Diplomatic actions — break/downgrade (Phase 8 wiring)
            "diplomatic_break",      # Break an active treaty
            "diplomatic_downgrade",  # Voluntarily downgrade diplomatic state
            # Diplomatic actions — Phase 4 (war declaration, ultimatum)
            "diplomatic_declare_war",  # Declare war on a nation
            "diplomatic_ultimatum",    # Issue ultimatum to a nation
            # Memory and Pressure v2.4.3 — B-B7 Make Amends (spec §8.6.1)
            "make_amends",
            # WPS-A: Set war purpose for defensive wars
            "set_war_purpose",
            # WB-C: Repudiate a live war bargain
            "repudiate_bargain",
            # Imperial Settlement (WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC §11)
            "propose_common_peace",  # Open the C2 settlement_confirm dialogue
            # SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1: distinct white
            # peace action — surfaced only via the wizard's structured
            # payload, but valid_actions still names it so action-id
            # validation accepts it.
            "propose_white_peace",
            # SC-30 / Slice G1: Request Terms lifecycle
            "request_terms",
            # ES-7 Estate Endowment (Economy Revisit S7)
            "grant_dotation",   # "endow Ney with Swabia" — 1 admin AP + fee
            # ES-7 second pass (§0.6.8): the rente
            "grant_pension",    # "grant Ney a rente" — 1 admin AP, no fee
            "revoke_pension",   # "revoke Ney's rente"
            # Marshal Recruitment (Jealousy v3.2 final phase)
            "recruit_marshal",  # "commission Grouchy" — 1 admin AP + gold
            # DEF-5 naval — "The Wooden Wall" (NAVAL_SPEC §9)
            "build_fleet",       # "build ships" — 1 admin AP + 400g
            "set_fleet_posture",  # "blockade the enemy" / "guard home waters"
            "naval_expedition",  # "land Soult in Munster" — the H4 gamble
            "naval_diversion",   # "order the diversion" — §5.3
        ]

        # Valid stances for stance_change command (Phase 2.7)
        self.valid_stances = ["neutral", "defensive", "aggressive"]

        # Fallback region roster (CR-0) — legacy REGIONS_DATA fixture names.
        # Only used when no live world is passed; normal gameplay reads the
        # live 126-province names via `_get_known_regions(world)`.
        from backend.models.region import REGIONS_DATA
        self.known_regions = list(REGIONS_DATA.keys())

        # Fallback enemy marshal roster — derived from the canonical marshal
        # factory instead of a hardcoded string list (§3.4). This is only
        # used when no world state is available (e.g. cold command parsing
        # in unit tests); normal gameplay reads live names via
        # `_get_known_enemies(world)`.
        self._fallback_known_enemies = _build_fallback_known_enemies()

        # Show actual mode from LLMClient (which reads from env if use_real_llm=None)
        mode = self.llm.provider_name.upper()
        key_source = self.llm.key_source
        print(f"Command Parser initialized: mode={mode}, key_source={key_source}")

    def _get_known_enemies(self, world=None) -> List[str]:
        """
        Return the current enemy marshal roster for fuzzy matching.

        Prefers live world state so mid-game-spawned marshals are recognised
        and emergent nation rosters work without editing this file. Falls
        back to the factory-derived seed roster otherwise (§3.4).
        """
        if world is not None:
            player_nation = getattr(world, "player_nation", None)
            names = _extract_enemy_marshal_names(world, player_nation)
            if names:
                return names
        return list(self._fallback_known_enemies)

    def _get_player_marshals(self, world=None, game_state=None) -> List[str]:
        """
        Return the current PLAYER marshal roster for fuzzy matching (CR-0).

        Prefers live world state so scenario rosters (e.g. the 7-marshal
        1805 campaign) are commandable without editing this file. Second
        choice: the LLM game_state's player-only "marshals" dict — so a
        parse called with game_state but no world validates against the
        SAME roster the mock extracted from. Falls back to the legacy
        4-name seed roster otherwise (cold parses in unit tests keep
        their historical behavior).
        """
        if world is not None:
            player_nation = getattr(world, "player_nation", None)
            names = _extract_player_marshal_names(world, player_nation)
            if names:
                return names
        if isinstance(game_state, dict):
            marshals = game_state.get("marshals")
            if isinstance(marshals, dict) and marshals:
                return list(marshals)
        return list(self.valid_marshals)

    def _get_known_regions(self, world=None) -> List[str]:
        """
        Return the current region roster for fuzzy matching (CR-0).

        Prefers live world state (126 provinces on the shipped 1805 boot);
        falls back to the legacy REGIONS_DATA seed when no world is
        available. Runs once per typed command — not a hot path.
        """
        regions = getattr(world, "regions", None) if world is not None else None
        if regions:
            return list(regions.keys())
        return list(self.known_regions)

    def _enemy_addressee_refusal(self, command_text: str, world=None,
                                 game_state=None) -> Optional[Dict]:
        """WO-1: build the by-name refusal for an enemy-addressed command,
        or None. ONE builder for both parse routes (the fuzzy pass and the
        diplomatic early-return) so the register can never fork."""
        resolved = _resolve_enemy_addressee(
            command_text, self._get_known_enemies(world),
            self._get_known_regions(world))
        if resolved is None:
            return None
        enemy_addressee, arm, token = resolved
        # Review round (Aug 21): the PLAYER roster gets right of first
        # refusal on a TYPO'D address — "Mark, attack Vienna" belongs to
        # the CR-2 did-you-mean flow (Murat), not to an enemy refusal
        # (Mack). Exact enemy names are never deferred.
        if arm == "typo":
            player_result = self.fuzzy_matcher.match_with_context(
                token, self._get_player_marshals(world, game_state))
            if player_result.get("action") in ("exact", "auto_correct",
                                               "suggest"):
                return None
        enemy_nation = ""
        if world is not None:
            enemy_obj = getattr(world, "marshals", {}).get(enemy_addressee)
            if enemy_obj is not None:
                from backend.game_logic.formations import (
                    formed_display_name,
                )
                enemy_nation = formed_display_name(
                    world, getattr(enemy_obj, "nation", ""))
        side = enemy_nation or "the enemy"
        return {
            "error": (f"Marshal {enemy_addressee} commands for {side}, "
                      f"Sire — he does not answer to us."),
            # Review round: an enemy-name lead can be an intel ask, not an
            # attempted order — name the intel road beside the sword.
            "suggestion": (f"To move against him: 'attack "
                           f"{enemy_addressee}' or 'pursue "
                           f"{enemy_addressee}'; for word of him, ask "
                           f"'where is {enemy_addressee}'."),
            "kind": "enemy_addressee",
            "unknown_name": enemy_addressee,
            "candidates": [],
        }

    def _apply_fuzzy_matching(self, llm_result: Dict, command_text: str, world=None,
                              game_state=None) -> tuple:
        """
        Apply fuzzy matching to correct typos in marshal and target names.

        Args:
            llm_result: The result from LLM parsing
            command_text: Original command text
            world: Optional live WorldState — used to derive the current
                enemy marshal roster instead of the factory fallback.
            game_state: Optional LLM game_state dict — roster fallback when
                world is absent (keeps fuzzy validation consistent with
                what the mock parser extracted).

        Returns:
            Tuple of (updated llm_result, error_dict or None)
            error_dict is set if an invalid marshal name was detected
        """
        # PARSE-NEG: a refusal is a finished verdict — the parser read the
        # sentence and there is no order in it. Fuzzy matching has nothing to
        # correct here, and letting it run REPLACED the verdict: the addressed
        # name of "Talleyrand, do not propose peace with Austria" was fuzzed
        # into "Did you mean 'Ney'?", which lost the refusal and told the
        # player something false about what went wrong.
        if llm_result.get("refusal"):
            return (llm_result, None)
        known_enemies = self._get_known_enemies(world)
        # CR-0: rosters come from the live world when available — the
        # hardcoded legacy lists are only the no-world/no-game_state fallback.
        valid_marshals = self._get_player_marshals(world, game_state)
        known_regions = self._get_known_regions(world)

        # ══════════════════════════════════════════════════════════════
        # WO-1: an ENEMY name in the addressee slot refuses by name, for
        # every verb, BEFORE any family early-return or extraction can
        # strip it. Both extraction layers lost the addressee: the mock
        # never binds an enemy lead as marshal (it is in
        # known_target_words), so "Kutuzov, retreat" degraded to the bare
        # army-wide form with target=Kutuzov; the live layer binds it as
        # marshal and the CR-1 demotion below then strips it. And the
        # recruit/vassal early-returns below discard the addressee
        # outright — "Kutuzov, grant Holland more autonomy" EXECUTED the
        # grant (review finding, Aug 21). Either way the player named the
        # man the game printed and the game acted on somebody else. Third
        # member of the family PC15-4 opened: invented names guarded,
        # fallen names guarded, enemy names now too.
        # ══════════════════════════════════════════════════════════════
        enemy_refusal = self._enemy_addressee_refusal(
            command_text, world, game_state)
        if enemy_refusal is not None:
            return (llm_result, enemy_refusal)
        # Marshal Recruitment (Jealousy v3.2): a recruit_marshal "marshal"
        # is a POOL CANDIDATE, not a roster marshal — "recruit marshal
        # Suchet" must not die in the roster validation below. Move the
        # name into target (the executor resolves it against the pool)
        # and skip marshal matching entirely.
        if llm_result.get("action") == "recruit_marshal":
            if llm_result.get("marshal") and not llm_result.get("target"):
                llm_result["target"] = llm_result["marshal"]
            llm_result["marshal"] = None
            return (llm_result, None)
        # Vassal-family actions target a NATION, not a marshal — the executor
        # resolves the nation (and the more/less/grant direction) from
        # raw_command (F6). A stray direction word must NOT be fuzzy-matched to
        # a marshal: "grant Holland MORE autonomy" was matching "more" -> "Murat"
        # and failing the whole command (Sweep 4 finding), while "grant Holland
        # autonomy" (no direction word) parsed. Skip marshal matching here, same
        # as recruit_marshal; move any extracted name into target so an explicit
        # nation survives for the executor.
        if llm_result.get("action") in (
                "change_autonomy", "invest_vassal", "release_vassal",
                "make_vassal", "grant_region_to_vassal",
                "sponsor_design", "buy_off_design", "guarantee_nation"):
            if llm_result.get("marshal") and not llm_result.get("target"):
                llm_result["target"] = llm_result["marshal"]
            llm_result["marshal"] = None
            return (llm_result, None)

        # Fuzzy match marshal name if LLM extracted one
        if llm_result.get("marshal"):
            # CR-1: an extracted "marshal" that IS a known enemy commander
            # is a target reference, not an executing marshal — the fogged
            # honorific form ("Attack Marshal Kutuzov" while Kutuzov is
            # outside the fog-filtered game_state) reaches here.
            extracted = llm_result["marshal"]
            enemy_match = next(
                (e for e in known_enemies if e.lower() == extracted.lower()),
                None)
            if enemy_match is None and len(extracted) >= 3:
                enemy_match = _closest_by_edit_distance(extracted, known_enemies)
            if enemy_match is not None:
                llm_result["marshal"] = None
                if not llm_result.get("target"):
                    llm_result["target"] = enemy_match
        if llm_result.get("marshal"):
            marshal_result = self.fuzzy_matcher.match_with_context(
                llm_result["marshal"],
                valid_marshals
            )
            # WO-13, September 1, 2026: gated like its five siblings in this
            # file. UPSTREAM of the executor's three seams and invisible to
            # their census, which is scoped to `executor.py` by construction
            # — measured, this arm rewrote SEVEN province names to "Ney"
            # (Brittany, Champagne, Gascony, Guyenne, Lorraine, Maine,
            # Ukraine). The CR-0 guard below is written for exactly this
            # ("'Hold Bern!' must not hijack Bernadotte") and cannot cover
            # this arm, because it filters the ADDRESSEE scan, not the
            # LLM-supplied marshal slot.
            if (marshal_result["action"] == "exact"
                    or (marshal_result["action"] == "auto_correct"
                        and _plausible_name_typo(
                            llm_result["marshal"],
                            marshal_result.get("match") or ""))):
                llm_result["marshal"] = marshal_result["match"]
            elif marshal_result["action"] == "suggest":
                # Medium confidence match - suggest to user
                # CR-2: structured fields let main.py raise a clarification
                # question instead of dropping the suggestion text
                return (llm_result, {
                    "error": f"Did you mean '{marshal_result['match']}'? ('{llm_result['marshal']}' not found)",
                    "suggestion": f"Try: '{marshal_result['match']}' or one of: {', '.join(valid_marshals)}",
                    "kind": "marshal_suggest",
                    "unknown_name": llm_result["marshal"],
                    "candidates": [marshal_result["match"]],
                })
            else:  # action == "error"
                # No good match - return error with suggestions
                suggestions = marshal_result.get("suggestions", valid_marshals[:3])
                return (llm_result, {
                    "error": f"Marshal '{llm_result['marshal']}' not found",
                    "suggestion": f"Available marshals: {', '.join(suggestions)}",
                    "kind": "marshal_not_found",
                    "unknown_name": llm_result["marshal"],
                    "candidates": list(suggestions[:3]),
                })
        # If marshal is None, try to extract from command text with fuzzy matching
        elif not llm_result.get("marshal"):
            # Skip fuzzy marshal matching if target already identified
            existing_target = (llm_result.get("target") or "").lower()
            # CR-0: multiword/camelCase targets must skip word-by-word —
            # "attack East Prussia" scans "East" and "Prussia" separately
            existing_target_words = set(existing_target.split())
            existing_target_words.update(
                _CAMEL_SPLIT_RE.sub(' ', llm_result.get("target") or "")
                .lower().replace('-', ' ').split())
            # CR-0: words that exactly name a known region/enemy are targets,
            # never marshal-name candidates ("Hold Bern!" must not hijack
            # Bernadotte via fuzzy auto-correct)
            known_target_words = {n.lower() for n in known_regions}
            known_target_words.update(n.lower() for n in known_enemies)

            # BUG-002 FIX: Skip fuzzy marshal matching for meta/help commands
            # Actions that don't require a marshal (meta commands + pending charge responses)
            # FA slice 7 (FA-N9): ONE list, DERIVED — validation.META_ACTIONS
            # (the declared source of truth) plus the seven parser-only
            # entries; the three naval verbs join by construction.
            meta_actions = META_ACTIONS | PARSER_ONLY_META
            if llm_result.get("action") in meta_actions:
                # CR-2 (silent-marshal-drop fix): an EXPLICITLY-addressed name
                # must bind or clarify, never drop — "Murat, charge" used to
                # execute with marshal=None, silently discarding the
                # addressee. Only the leading comma-address form is checked;
                # bare meta commands ("charge", "recruit infantry") keep
                # their marshal-less fast path.
                addressed = _leading_addressed_token(command_text)
                # FA slice 7: the fleet's own admiral is a legitimate
                # addressee of a naval verb ("Villeneuve, order the
                # diversion"), not a marshal typo — accepted as decoration.
                if (ADMIRAL_IS_AN_ADDRESSEE and addressed
                        and llm_result.get("action") in _NAVAL_META_VERBS
                        and _names_the_admiral(addressed, world)):
                    addressed = None
                if (addressed
                        and addressed.lower() not in known_target_words
                        and addressed.lower() != existing_target
                        and addressed.lower() not in existing_target_words):
                    marshal_result = self.fuzzy_matcher.match_with_context(
                        addressed, valid_marshals)
                    # WO-13: gated. The CR-0 filter above reads
                    # `_get_known_regions(world)`, which falls back to the
                    # 19-region LEGACY map whenever the world does not
                    # arrive — so on the 126-province board "Gascony, charge"
                    # passed the filter and this arm bound marshal "Ney" at
                    # 0.55 confidence. Gating here fixes the consequence
                    # world-or-no-world; the plumbing question is recorded
                    # rather than papered over, and no consequence could be
                    # exhibited downstream (the marshal is discarded for all
                    # four reachable verbs and `command_history` records
                    # `marshal: null`, so CR-4 focus is not poisoned).
                    if (marshal_result["action"] == "exact"
                            or (marshal_result["action"] == "auto_correct"
                                and _plausible_name_typo(
                                    addressed,
                                    marshal_result.get("match") or ""))):
                        llm_result["marshal"] = marshal_result["match"]
                    elif marshal_result["action"] == "suggest":
                        return (llm_result, {
                            "error": f"Did you mean '{marshal_result['match']}'? ('{addressed}' not found)",
                            "suggestion": f"Try: '{marshal_result['match']}' or one of: {', '.join(valid_marshals)}",
                            "kind": "marshal_suggest",
                            "unknown_name": addressed,
                            "candidates": [marshal_result["match"]],
                        })
                    else:
                        suggestions = marshal_result.get("suggestions", valid_marshals[:3])
                        return (llm_result, {
                            "error": f"Marshal '{addressed}' not found",
                            "suggestion": f"Available marshals: {', '.join(suggestions)}",
                            "kind": "marshal_not_found",
                            "unknown_name": addressed,
                            "candidates": list(suggestions[:3]),
                        })
                return (llm_result, None)  # Don't try to find a marshal

            # CR-2: same executor-eligibility rules as the mock extraction —
            # a name inside a condition clause ("until Ney arrives") or in
            # support-object position ("support Ney") must not be re-bound
            # as the executor here (this scan used to undo the mock layer's
            # demotion and make marshals support themselves).
            condition_match = CONDITION_CLAUSE_RE.search(command_text)
            condition_start = (condition_match.start() if condition_match
                               else len(command_text) + 1)

            words = [(w.group(0), w.start())
                     for w in re.finditer(r'\S+', command_text)]
            for word_index, (word, word_pos) in enumerate(words):
                if word_pos >= condition_start:
                    continue
                if SUPPORT_OBJECT_PREFIX_RE.search(command_text[:word_pos]):
                    continue
                # Address syntax ("Wittgenstein, attack") — a trailing comma
                # marks an explicitly-addressed name; such words keep the
                # helpful not-found error even in first position (CR-1)
                was_addressed = word.rstrip(".!?;:").endswith(",")
                # CR-0: strip punctuation FIRST — "Mack!" must be recognized
                # as the already-parsed target / a known name before any
                # marshal fuzzy-matching sees it
                word = word.strip(",.!?;:")
                word_lower = word.lower()
                # Skip words that match the already-parsed target (e.g., "Rhineland" in "bombard Rhineland")
                if existing_target and (word_lower == existing_target
                                        or word_lower in existing_target_words):
                    continue
                if word_lower in known_target_words:
                    continue

                # Skip very short words, common words, and action keywords
                # BUG-002 FIX: Added help, wait, hold, retreat, fortify, drill, etc.
                skip_words = [
                    "to", "the", "at", "in", "on", "and", "or",
                    "attack", "defend", "move", "scout", "retreat",
                    "help", "wait", "hold", "fortify", "drill", "recruit",
                    "reinforce", "unfortify", "stance", "aggressive", "defensive", "neutral",
                    "go", "take", "be", "switch", "adopt", "return",  # Stance command verbs
                    "debug", "/debug", "set_location", "set_retreat", "set_recovery",  # Debug commands
                    "set_strength", "set_morale", "set_fortified", "ai_turn", "ai_state",
                    "charge", "restrain", "glorious",  # Cavalry recklessness commands
                    # Generic/ambiguous terms — don't try to match as marshal names
                    "general", "marshal", "commander", "enemy", "enemies",
                    "someone", "somebody", "anyone", "whoever",
                    "support", "pursue", "chase", "hunt", "intercept",
                    "cancel", "halt", "abort", "stop",
                    "bombard", "barrage", "shell", "cannonade", "garrison",
                    # Troop type keywords — not marshal names (M2 parse fix)
                    "infantry", "cavalry", "artillery", "troops", "soldiers",
                    "horsemen", "riders", "foot", "guns",
                    # Vassal command verbs — not marshal names (CR-0; typed
                    # "invest in saxony" died here in every world)
                    "invest", "release", "vassal", "vassalize", "subjugate",
                    "autonomy", "puppet", "satellite", "make",
                    # Strategic-order verbs/phrasing words — not marshal
                    # names (CR-1; "march to vienna" hard-errored with
                    # "Marshal 'march' not found" on the legacy world)
                    "march", "advance", "head", "deploy", "campaign",
                    "press", "push", "sweep", "drive", "guard", "protect",
                    "secure", "maintain", "rally", "link", "combine",
                    "bolster", "shore", "track", "follow", "shadow",
                    "harry", "hound", "assist", "aid", "stand", "withdraw",
                ]
                if len(word) < 2 or word_lower in skip_words:
                    continue

                marshal_result = self.fuzzy_matcher.match_with_context(
                    word,
                    valid_marshals
                )
                # CR-1: partial-ratio scoring rewards substrings — 'journey'
                # scored a perfect auto-correct against 'Ney' and 'rhine'
                # scored 80 against it too. A real marshal typo stays within
                # a couple of characters of the name AND keeps its first
                # letter; anything else is a sentence word, not a name.
                _match = marshal_result.get("match") or ""
                if (marshal_result["action"] in ("auto_correct", "suggest")
                        and (abs(len(word) - len(_match)) > 2
                             or word_lower[:1] != _match[:1].lower())):
                    marshal_result = dict(marshal_result)
                    marshal_result["action"] = "error"
                if marshal_result["action"] in ["exact", "auto_correct"]:
                    llm_result["marshal"] = marshal_result["match"]
                    break
                elif marshal_result["action"] == "suggest":
                    # Found a word that looks like a marshal but medium confidence
                    # Suggest to user instead of auto-assigning
                    return (llm_result, {
                        "error": f"Did you mean '{marshal_result['match']}'? ('{word}' not found)",
                        "suggestion": f"Try: '{marshal_result['match']}' or one of: {', '.join(valid_marshals)}",
                        "kind": "marshal_suggest",
                        "unknown_name": word,
                        "candidates": [marshal_result["match"]],
                    })
                elif marshal_result["action"] == "error":
                    # Word doesn't match any marshal well. Check if it's a valid target.
                    # If it's not a target either, it's probably a bad marshal name.
                    all_targets = known_regions + known_enemies
                    target_check = self.fuzzy_matcher.match_with_context(word, all_targets)

                    # If this word also doesn't match any target, it's likely a bad marshal attempt
                    if target_check["action"] == "error":
                        # CR-1: only a CAPITALIZED unknown word reads as a
                        # name attempt worth a hard error — lowercase
                        # sentence words ("costs", "positions", "all") were
                        # hard-failing whole commands. The FIRST token is
                        # exempt too (English sentence case capitalizes it —
                        # "Withdraw to Vienna" is not a name attempt) UNLESS
                        # it carries address syntax ("Wittgenstein, attack"
                        # must keep its helpful suggestions error).
                        if not word[:1].isupper() or (word_index == 0
                                                      and not was_addressed):
                            continue
                        suggestions = marshal_result.get("suggestions", valid_marshals[:3])
                        return (llm_result, {
                            "error": f"Marshal '{word}' not found",
                            "suggestion": f"Available marshals: {', '.join(suggestions)}",
                            "kind": "marshal_not_found",
                            "unknown_name": word,
                            "candidates": list(suggestions[:3]),
                        })
                    # Otherwise, skip this word - it might be a target, not a marshal

        # Fuzzy match target name
        # CR-0: vassal-family targets are NATION names — never rewrite them
        # to regions/enemies ("invest in Austria" must not become the
        # Spanish region Asturias)
        _VASSAL_ACTIONS = VASSAL_FAMILY_ACTIONS
        # IGR-A3: a bare NATION name ("move to Austria") is neither a province
        # nor a demonym. It must not be fuzzy-rewritten — that marched Ney to
        # Asturias, and "Britain" to Brittany — and it must NOT be nulled
        # either: nulling discards the word the player typed and answers
        # "Where shall Ney march, Sire?", which is the Sweep-5 defect. Carry
        # the name through unchanged; the executor's region chokepoint names
        # the nation and lists its provinces.
        #
        # Checked BEFORE the demonym rule so "Ottoman" / "Papal States" (whose
        # tags collide with their own demonym overrides) get the helpful
        # answer instead of the dead-end ask. `resolve_typed_nation` returns
        # None for a word that is also an exact region (Hanover, Naples,
        # Normandy), so those keep resolving to the province.
        _typed_nation = None
        if (llm_result.get("target")
                and llm_result.get("action") not in _VASSAL_ACTIONS):
            _typed_nation = resolve_typed_nation(llm_result["target"], world)

        # A nation demonym ("the Austrians", "Prussians") names an ARMY, not a
        # province — drop it to None so neither the fuzzy ladder below nor the
        # command-text fallback rewrites it into a region ("the Austrians" →
        # the Spanish province "Asturias", playtest finding). None lets the
        # executor auto-target the nearest enemy, mirroring the mock parser's
        # deliberate demonym omission.
        if (llm_result.get("target")
                and not _typed_nation
                and llm_result.get("action") not in _VASSAL_ACTIONS
                and _is_nation_demonym(llm_result["target"], world)):
            # ══════════════════════════════════════════════════════════
            # PT-H3. ⚠ The DROP is correct and stays — it is the fix for
            # "the Austrians" -> the Spanish province Asturias. What was
            # missing is that the nation the player NAMED was discarded
            # with it and never re-applied, so `Murat, attack the
            # Austrians` sent him at Shrapnel (British) one turn after an
            # armistice with Austria, and said nothing about it.
            #
            # The nation he named is stamped ONCE at the end of `parse`,
            # from the raw sentence — not here. Two drop sites plus a mock
            # parser that never produces a demonym at all is three places
            # to keep in step; the tail stamp is path-independent.
            # ══════════════════════════════════════════════════════════
            llm_result["target"] = None
        if (llm_result.get("target")
                and not _typed_nation
                and llm_result.get("action") not in _VASSAL_ACTIONS):
            # CR-0 precedence ladder: exact enemy > exact region >
            # enemy auto-correct > region auto-correct. With 126 live
            # provinces, region fuzzy rewrote exact/typo'd enemy names
            # ("Mack" → "La Mancha", "Mach" → "La Mancha").
            enemy_result = self.fuzzy_matcher.match_with_context(
                llm_result["target"],
                known_enemies
            )
            region_result = self.fuzzy_matcher.match_with_context(
                llm_result["target"],
                known_regions
            )
            # Aug 30, 2026 review: the WO-2 comment below records the shape
            # gate being added to the two auto_correct arms — and this
            # edit-distance arm, which OUTRANKS both, was left ungated, so the
            # very family WO-2 names ("Moon->Moore") still binds one rung up:
            # measured, "Ney, attack across the moor" -> Moore. A proper name
            # does not take an article, and a prisoner is not a target.
            near_enemy = (_closest_by_edit_distance(llm_result["target"], known_enemies)
                          if (len(llm_result["target"]) >= 3
                              and not _introduced_by_article(
                                  command_text, llm_result["target"]))
                          else None)
            if near_enemy is not None and not _is_targetable_enemy(near_enemy, world):
                near_enemy = None
            if enemy_result["action"] == "exact":
                llm_result["target"] = enemy_result["match"]
            elif region_result["action"] == "exact":
                llm_result["target"] = region_result["match"]
            elif near_enemy is not None:
                # An edit-distance-1 enemy typo beats any region fuzz —
                # partial-ratio scoring rewards long containing names
                # ("Mach" scored higher against "La Mancha" than "Mack")
                llm_result["target"] = near_enemy
            # WO-2: both auto-correct arms gated with the typo-shape test
            # their four siblings already carry (the tactical scan, the
            # strategic-region scan, and the two strategic_executor sites).
            # Ungated, partial-ratio junk marched: Avalon→Leon (a 2-AP
            # standing order eight provinces into Spain), Moon→Moore,
            # Troy→Deroy, Hell→Hohenlohe, Eden→Buxhowden.
            elif (enemy_result["action"] == "auto_correct"
                    and _plausible_name_typo(
                        llm_result["target"], enemy_result.get("match") or "")):
                llm_result["target"] = enemy_result["match"]
            elif (region_result["action"] == "auto_correct"
                    and _plausible_name_typo(
                        llm_result["target"], region_result.get("match") or "")):
                llm_result["target"] = region_result["match"]
            # suggest/error on both sides: leave the typed target unchanged
            # (pre-CR-0 behavior — the executor reports it helpfully)

        # If target is still None, try to extract it from command text.
        #
        # July 18, 2026 playtest sweep: gated on the action being RESOLVABLE. A
        # failed parse has no action to hang a target on, and scanning anyway
        # fuzzy-matched arbitrary sentence words into real provinces ("hell" →
        # Algiers, "deal" → Bordelais). That fabricated province then rode into
        # `partial_target` and was fed to Berthier's live recovery prompt as a
        # fact the Emperor had stated, so his suggested rephrasing could name a
        # province 1,500km from the marshal. The marshal-less path already
        # skips this via the meta_actions early return; this restores the
        # symmetry when a marshal binds.
        elif not llm_result.get("target") and llm_result.get("action") != "unknown":
            # Build skip list: common words + action words + marshal name
            skip_words = [
                "to", "the", "at", "in", "on", "and", "or", "a", "an",
                # Action words - don't match these to targets
                "attack", "defend", "move", "scout", "retreat", "recruit",
                "reinforce", "help", "wait", "hold", "fortify", "drill",
                "unfortify", "stance", "aggressive", "defensive", "neutral",
                "charge", "restrain", "glorious",  # Cavalry recklessness commands
                # Pronouns / deixis / collective references — never fuzzy-match
                # these into a province. Unresolved by carryover, they otherwise
                # short-name auto-correct to a random region ("them" -> "Bohemia",
                # "here" -> "Bergen"). Leaving target None routes to auto-target /
                # the "which enemy?" clarification instead of a silent mis-order.
                "them", "they", "him", "her", "it", "us", "me", "you",
                "here", "there", "this", "that", "those", "these",
                "someone", "somebody", "anyone", "anybody", "whoever",
                "enemy", "enemies", "foe", "foes", "target", "yourself",
                # NP-1: the sovereign self-marker ("march to Ulm myself")
                # was fuzzy-matchable into a province — the PARSE-NEG
                # phantom family. Closed regardless of the sovereign gate.
                "myself", "ourselves", "person",
            ]
            # July 18, 2026: the same rule for combat-idiom filler. "Ney, give
            # them hell" now parses as an attack, so the gate above no longer
            # protects it — and "hell" auto-corrects into the province Algiers.
            # Single-sourced with the vocabulary that introduced the idioms.
            skip_words.extend(IDIOM_FILLER_WORDS)
            # PARSE-NEG evaluation: and the same rule for ordinary English. The
            # two lists above were assembled defect-by-defect from whatever
            # playtest had just produced a phantom province; _NON_TARGET_WORDS
            # is the general case, so "Ney, form square" stops marching on
            # Normandy and "Ney, hold the pass" stops holding Nassau.
            skip_words.extend(_NON_TARGET_WORDS)
            # Also skip the marshal name if identified
            if llm_result.get("marshal"):
                skip_words.append(llm_result["marshal"].lower())

            # Extract potential target words from command (words after action)
            words = command_text.split()
            for _wi, word in enumerate(words):
                # Aug 30, 2026 review: the word BEFORE matters (see the
                # near-enemy arm below), so the raw previous token is kept.
                _prev_word = words[_wi - 1].strip(",.!?;:").lower() if _wi else ""
                # CR-0: strip trailing punctuation so "Bernadotte," is
                # recognized as the (skipped) marshal name, not fuzzy-matched
                # into a region ("Bern")
                word = word.strip(",.!?;:")
                # Skip common/action words and marshal name
                if word.lower() in skip_words:
                    continue
                # Skip very short words (likely not valid targets)
                if len(word) < 3:
                    continue
                # IGR-A3: a bare nation name scanned out of the command text
                # gets the same treatment as one the parser resolved — keep it
                # verbatim so the executor can name the nation, rather than
                # letting the combined fuzzy pass auto-correct it into a
                # province. Checked before the demonym rule for the same
                # reason as above.
                _word_nation = resolve_typed_nation(word, world)
                if _word_nation:
                    # The canonical tag, not the raw casing — "austria" is not
                    # in the validator's target set and would be silently
                    # nulled back to None.
                    llm_result["target"] = _word_nation
                    break

                # A nation demonym ("Austrians") is a generic army reference,
                # not a province — never fuzzy-match it into a region here
                # (it drifted to "Asturias"). Leave target None → auto-target.
                if _is_nation_demonym(word, world):
                    continue

                # CR-0: an exact or edit-distance-1 enemy name wins before
                # the combined fuzzy pass (partial-ratio scoring rewarded
                # "La Mancha" over "Mack" for the typo "Mach")
                #
                # Aug 30, 2026 review: this arm carried NONE of the shape gates
                # its two sibling auto-correct arms below carry, so any
                # sentence word within one edit of a commander's name became
                # the attack target — measured, "Ney, attack across the moor"
                # resolved target=Moore, a fogged British marshal in London,
                # and the refusal ("No intelligence on Moore's position")
                # confirmed a hidden commander's existence from a landscape
                # noun. Two rules, both stating something true about names:
                # a proper name does not take an article or sit behind a
                # locative preposition ("the moor", "across the moor"), and a
                # PRISONER is not a target — he is at his captor's capital at
                # strength 0, and PC15-4 already refuses him by name.
                _articled = _prev_word in _NAME_BLOCKING_PREFIXES
                near_enemy = (_closest_by_edit_distance(word, known_enemies)
                              if len(word) >= 3 and not _articled else None)
                if near_enemy is not None and _is_targetable_enemy(near_enemy, world):
                    llm_result["target"] = near_enemy
                    break

                # Try matching against all targets
                all_targets = known_regions + known_enemies
                target_result = self.fuzzy_matcher.match_with_context(
                    word,
                    all_targets
                )

                # PARSE-NEG evaluation: an EXACT name still binds outright, but
                # an auto-correct must now look like a typed mistake. Without
                # this second gate the partial-ratio scorer kept promoting
                # sentence words no stopword list would ever catch — "relieved"
                # became Rhineland, and "Ney, hold until relieved" issued a HOLD
                # on a province 400km away, at confidence 0.9.
                # Aug 30, 2026 review: `_plausible_name_typo` cannot separate a
                # real typo from an ordinary English word that happens to sit
                # one edit from a name — "moor" and "Moore" share a first
                # letter and one edit, so "Ney, attack across the moor" bound
                # a fogged British marshal in London and the refusal ("No
                # intelligence on Moore's position") disclosed him. Grammar
                # separates them where spelling cannot: a proper NAME does not
                # take an article. Applied to commander names ONLY — plenty of
                # provinces are spoken with one ("the Rhineland", "the Tyrol"),
                # so gating regions here would break ordinary orders.
                _match_name = target_result.get("match") or ""
                if _articled and _match_name in known_enemies:
                    continue
                if target_result["action"] == "exact":
                    llm_result["target"] = target_result["match"]
                    break
                if (target_result["action"] == "auto_correct"
                        and _plausible_name_typo(word, _match_name)):
                    llm_result["target"] = target_result["match"]
                    break

        return (llm_result, None)

    def _and_clause_is_a_second_order(self, command_text: str, game_state):
        """FA-50: the bare `and <verb>` arm, decided by evidence.

        "Ney, attack Mack and hold Rhineland" is two orders; "Ney, defend
        and hold" and "secure and hold vienna" are one, and both are pinned.
        The discriminator is evidence, not style: SPLIT only when clause 1
        parses to a real action on its own AND clause 2 carries its OWN
        object. A bare second verb names no object, so "Ney, defend and
        hold" stays one order — and the three hold IDIOMS are exempted
        outright, because `defend and hold belgium` DOES name an object and
        is still one order.

        Returns (first, tail) or None. Never splits when both clauses name
        the same object — "attack Mack and destroy Mack" is one order said
        twice.
        """
        if _HOLD_IDIOM_RE.search(command_text):
            return None
        match = _AND_VERB_SPLIT_RE.search(command_text)
        if not match:
            return None
        first = command_text[:match.start()].strip().rstrip(',;')
        tail = command_text[match.end():].strip()
        if not first or not tail:
            return None
        head_parse = self.llm.fast_parse(first, game_state)
        if head_parse.action == "unknown":
            return None
        tail_parse = self.llm.fast_parse(tail, game_state)
        if tail_parse.action == "unknown" or not tail_parse.target:
            return None
        if head_parse.target and str(tail_parse.target).strip().lower() == str(
                head_parse.target).strip().lower():
            return None
        return (first, tail)

    def parse(self, command_text: str, game_state: Optional[Dict] = None, world=None) -> Dict:
        """FA slice 7 review round (R1-1): the verb-typo repair is applied
        HERE, before any reader sees the sentence — the first cut rewrote
        only the mock chain's own text, so "Davout, hodl Lorraine" parsed as
        `hold` while the strategic layer read "hodl" and produced a stance
        change at Rhineland, and "hodl Lorraine, then attack Mack" FOUGHT
        (the split gate never saw a halt). The typed text stays the record
        (`raw_input` / `raw_command`, R1-11); the note rides the `warning`
        seam on success and `typo_note` on a refusal.
        """
        import backend.ai.llm_client as _lc
        typed_text = command_text
        typo_note = None
        if getattr(_lc, "VERB_TYPO_PASS_ACTIVE", False):
            repaired, typo_note = repair_leading_verb_typo(command_text, game_state)
            if repaired and repaired != command_text:
                command_text = repaired
            else:
                typo_note = None
        result = self._parse_text(command_text, game_state, world)
        if typo_note and isinstance(result, dict):
            result["raw_input"] = typed_text
            command = result.get("command")
            if isinstance(command, dict):
                command["raw_command"] = typed_text
            result["typo_note"] = typo_note
            if result.get("success"):
                result["warning"] = (f"{result['warning']} {typo_note}"
                                     if result.get("warning") else typo_note)
        return result

    def _parse_text(self, command_text: str, game_state: Optional[Dict] = None, world=None) -> Dict:
        """
        Parse a command from the player.

        Args:
            command_text: Natural language command
            game_state: Current game state (for validation)

        Returns:
            Dict with the following structure on success:
            {
                "success": True,
                "command": {
                    "marshal": str | None,
                    "action": str,
                    "target": str | None,
                    "confidence": float,
                    "type": str | None,
                    "target_stance": str | None  # For stance_change
                },
                "raw_input": str,
                # Phase 5 - REQUIRED by main.py for feedback generation:
                "strategic_score": int,  # 0-100, from LLM or default 10
                "ambiguity": int,        # 0-100, from LLM or default 5
                "mode": str,             # "mock" or "live"
                "warning": str | None    # Optional validation warning
            }

            On failure:
            {
                "success": False,
                "error": str,
                "suggestion": str | None,
                "raw_input": str
            }

        IMPORTANT: main.py reads strategic_score, ambiguity, and mode from
        the TOP LEVEL of this return dict for feedback generation. If these
        fields are missing, feedback will silently fail to generate.
        """
        try:
            # NP-1: sovereign address normalization — "(the) Emperor, ...",
            # leading first person ("I will march to Ulm") and the trailing
            # self-marker ("... myself") rewrite to a canonical address
            # BEFORE every downstream stage, so the fast parser, LLM,
            # fuzzy matching and strategic detection agree by construction.
            # Dormant unless the player roster holds a sovereign.
            _sovereign = _find_player_sovereign(world, game_state)
            if _sovereign:
                command_text = normalize_sovereign_address(
                    command_text, _sovereign)

            # CR-2: sequential compound orders — parse the FIRST clause and
            # report the dropped tail instead of letting the second clause
            # leak into target extraction / strategic detection ("attack
            # Bern, then hold your positions" fabricated a phantom region
            # "Your Positions" with a stray HOLD upgrade). The trial parse
            # is the deterministic fast layer only; when the first clause
            # alone is unparseable ("if attacked, then retreat"), the full
            # text keeps its historical behavior.
            effective_text = command_text
            dropped_sequel = None
            sequel_split = _split_sequential_orders(command_text, game_state)
            if sequel_split is None:
                sequel_split = self._and_clause_is_a_second_order(
                    command_text, game_state)
            if sequel_split is not None:
                first_clause, sequel_tail = sequel_split
                # FA-50: this gate is what stops the ADDRESS form
                # "Ney and Davout, attack Mack" from splitting into
                # ("Ney", "Davout, attack Mack") — `fast_parse("Ney")`
                # returns `unknown`. That protection was incidental and
                # unasserted; it is pinned now, because the muster surface
                # depends on it.
                if self.llm.fast_parse(first_clause, game_state).action != "unknown":
                    effective_text = first_clause
                    dropped_sequel = sequel_tail

            # Step 1: Use LLM to parse natural language
            llm_result = self.llm.parse_command(effective_text, game_state)

            # ════════════════════════════════════════════════════════════
            # DIPLOMATIC COMMAND ROUTING (Phase 8 Session 3)
            # If the parser detected a Talleyrand command, route to
            # diplomatic processing — skip marshal fuzzy matching entirely.
            # ════════════════════════════════════════════════════════════
            if llm_result.get("diplomatic_data"):
                # WO-1 (review finding, Aug 21 2026): this early-return ran
                # BEFORE the enemy-addressee guard, so "Mack, declare war
                # on Prussia" staged the whole ceremony with the addressee
                # silently discarded, and "Kutuzov, improve relations with
                # Prussia" started a standing mission. Same refusal, same
                # register, same builder as the fuzzy pass.
                enemy_refusal = self._enemy_addressee_refusal(
                    effective_text, world, game_state)
                if enemy_refusal is not None:
                    return {
                        "success": False,
                        "error": enemy_refusal["error"],
                        "suggestion": enemy_refusal.get("suggestion"),
                        "raw_input": command_text,
                        "kind": enemy_refusal["kind"],
                        "unknown_name": enemy_refusal["unknown_name"],
                        "candidates": [],
                    }
                diplomatic_data = llm_result["diplomatic_data"]
                action = diplomatic_data.get("action", "diplomatic_proposal")

                # Error case: military command to Talleyrand
                if action == "diplomatic_error":
                    diplomatic_result = {
                        "success": True,
                        "command": {
                            "marshal": None,
                            "action": action,
                            "target": None,
                            "confidence": 1.0,
                            "type": "diplomatic",
                            "raw_command": command_text,
                            "diplomatic_data": diplomatic_data,
                        },
                        "raw_input": command_text,
                        "strategic_score": 0,
                        "ambiguity": 0,
                        "mode": llm_result.get("mode", "mock"),
                    }
                else:
                    diplomatic_result = {
                        "success": True,
                        "command": {
                            "marshal": None,
                            "action": action,
                            "target": diplomatic_data.get("target_nation"),
                            "confidence": llm_result.get("confidence", 0.95),
                            "type": "diplomatic",
                            "raw_command": command_text,
                            "diplomatic_data": diplomatic_data,
                        },
                        "raw_input": command_text,
                        "strategic_score": 0,
                        "ambiguity": 5,
                        "mode": llm_result.get("mode", "mock"),
                    }
                # Adversarial-review fix: a diplomatic FIRST clause must
                # report a dropped sequel exactly like the military path —
                # "Talleyrand, propose peace with Austria, then attack
                # Bern" silently discarded the second order.
                if dropped_sequel:
                    diplomatic_result["warning"] = (
                        f'One order at a time, Sire — I have relayed the '
                        f'first. "{dropped_sequel}" must follow as its own '
                        f'command.')
                    diplomatic_result["dropped_sequel"] = dropped_sequel
                return diplomatic_result

            # Step 2: Apply fuzzy matching to correct typos
            llm_result, fuzzy_error = self._apply_fuzzy_matching(
                llm_result, effective_text, world=world, game_state=game_state)

            # CR-2: the fast parser cleared the 0.7 confidence gate, so the
            # live LLM never saw this command — and the fuzzy pass just
            # proved the fast parse wrong. One deliberate LLM retry before
            # surfacing the error (no-op in mock mode).
            if fuzzy_error and llm_result.get("mode", "mock") == "mock":
                retried, retry_llm_error = self.llm.reparse_with_llm(
                    effective_text, game_state, llm_result)
                # Carry the RETRY's own API-failure signal onto the result
                # dict, so the failure branch below can stamp it and Berthier
                # recovery does not stack a third blocking call.
                if retry_llm_error:
                    llm_result["llm_error"] = True
                if retried is not None:
                    retried, retry_error = self._apply_fuzzy_matching(
                        retried, effective_text, world=world,
                        game_state=game_state)
                    if retry_error is None:
                        llm_result, fuzzy_error = retried, None

            # If fuzzy matching found an invalid marshal/target, return error immediately
            if fuzzy_error:
                failure = {
                    "success": False,
                    "error": fuzzy_error["error"],
                    "suggestion": fuzzy_error.get("suggestion"),
                    "raw_input": command_text,
                    # The action the fast layer recognized — lets the
                    # clarification builder cost the would-be reissue
                    "partial_action": llm_result.get("action"),
                }
                # CR-3(c): main.py's Berthier recovery must not fire a second
                # blocking LLM call when this request's parse call already
                # failed at the API layer.
                if llm_result.get("llm_error"):
                    failure["llm_error"] = True
                # CR-2: structured candidate fields (when present) let
                # main.py raise a clarification question with reissue
                # options instead of a dead-end error string
                for key in ("kind", "unknown_name", "candidates"):
                    if fuzzy_error.get(key) is not None:
                        failure[key] = fuzzy_error[key]
                return failure

            # Step 3: Validate the parsed command
            validation_result = self._validate_command(
                llm_result, game_state,
                player_roster=self._get_player_marshals(world, game_state))

            # Step 4: Return complete result
            if validation_result.get("valid"):
                # Classify command type
                command_type = self._classify_command(llm_result, command_text)

                command_dict = {
                    "marshal": llm_result.get("marshal"),  # Can be None for general orders
                    "action": llm_result["action"],
                    # July 19, 2026: collapse the "no specific target" sentinels
                    # to None. The prompt INSTRUCTS the model to answer a vague
                    # order with target="generic", PARSE_TOOL advertises it and
                    # validation blesses it — but the tactical executor rejected
                    # it outright ("Unknown target: generic" / "Region 'generic'
                    # not found"), so every vague command that reached the LLM
                    # died on arrival. With None, the executor's existing
                    # auto-resolve path handles it, which is what the strategic
                    # path has always done with the very same sentinel set.
                    "target": normalize_target(llm_result.get("target")),
                    "confidence": llm_result.get("confidence", 0.9),
                    "type": command_type,
                    "raw_command": llm_result.get("raw_command", command_text),
                    # CR-3(d): actual client state for this parse — the cheat
                    # gate keys off key_source ("none" = no live key armed)
                    # instead of the LLM_MODE env var, which BYOK bypasses.
                    "mode": llm_result.get("mode", "mock"),
                    "key_source": llm_result.get("key_source", "none"),
                }

                # BUG-005 FIX: Preserve target_stance for stance_change action
                if llm_result["action"] == "stance_change" and llm_result.get("target_stance"):
                    command_dict["target_stance"] = llm_result["target_stance"]

                # M2 FIX: Propagate requested recruit type for soft correction message
                # FA slice 7: the question desk's classified question rides
                # `status` into the executor.
                if llm_result.get("question"):
                    command_dict["question"] = llm_result["question"]
                if llm_result.get("requested_type"):
                    command_dict["requested_type"] = llm_result["requested_type"]
                elif llm_result.get("action") == "recruit":
                    # July 18, 2026: derive it from the player's own words when
                    # the upstream parse carries none. PARSE_TOOL has no
                    # `requested_type` property and the prompt never asks for
                    # one, so on the LIVE path this was always None — a recruit
                    # phrasing the fast parser could not classify silently lost
                    # the arm and the soft-correction message never fired.
                    # Deterministic, so it is GR6-safe and also repairs the
                    # case where a live re-parse discarded a fast-parsed arm.
                    _arm = extract_requested_arm(command_text)
                    if _arm:
                        command_dict["requested_type"] = _arm

                # CR-5b Flavor Echoing: carry the LLM's delegation flavor line to
                # the RESPONSE seam. command_dict is hand-built from named .get()s,
                # so without this lift the field is silently dropped end-to-end.
                # COSMETIC ONLY — read at main.py's delegation attach seam, never
                # consulted by CR-5 routing (Golden Rule 6).
                if llm_result.get("flavor"):
                    command_dict["flavor"] = llm_result["flavor"]

                # Phase 8 Session 8A: Preserve cheat data
                if llm_result["action"] == "cheat":
                    command_dict["cheat_type"] = llm_result.get("cheat_type")
                    command_dict["cheat_args"] = llm_result.get("cheat_args", [])

                result = {
                    "success": True,
                    "command": command_dict,
                    "raw_input": command_text,
                    # Phase 5: Include scores for feedback generation
                    "strategic_score": llm_result.get("strategic_score", 10),
                    "ambiguity": llm_result.get("ambiguity", 5),
                    "mode": llm_result.get("mode", "mock"),
                }
                if llm_result.get("llm_error"):
                    result["llm_error"] = True  # CR-3(c)

                # Add warning if present
                if validation_result.get("warning"):
                    result["warning"] = validation_result["warning"]

                # ════════════════════════════════════════════════════════════
                # STRATEGIC COMMAND DETECTION (Phase 5.2)
                # Check if this is a multi-turn strategic order
                # ════════════════════════════════════════════════════════════
                # Aug 30, 2026 review: this block used to be gated on `world`
                # ALONE, so it re-read the utterance no matter WHAT the action
                # chain had resolved — and stamped is_strategic on a parse the
                # chain had already ruled was not an order. The executor
                # intercepts on is_strategic + strategic_type alone, so:
                #
                #   "Davout, can you support Ney?"  ->  action=help (llm_client
                #   routes every interrogative there, PARSE-NEG "a question is
                #   not an order"), marshal bound by the CR-2 address fix,
                #   is_strategic=SUPPORT stamped here -> a REAL standing SUPPORT
                #   order created and begun.
                #
                # And because "help" is in the executor's `free_actions`, the
                # 2-AP strategic pre-gate AND the charge were both skipped:
                # measured on the 1805 boot, "march to Frankfurt" cost 4->3 AP
                # while "can you march to Frankfurt?" produced the identical
                # order for free, at 0 AP, while the reply still printed
                # "(2 AP — a standing strategic order…)".
                #
                # Two gates, both stating a rule rather than patching a symptom:
                # a pure-read/meta action is not an order, and a QUESTION is not
                # an order — the same doctrine the action chain already applies.
                _resolved_action = (command_dict.get("action") or "").lower()
                # FA slice 7: an ADMINISTRATIVE verb is not an order either.
                # Measured: `withdraw Ney's rente` parsed as revoke_pension
                # and the strategic table's bare "withdraw" then upgraded it
                # into a 2-AP MOVE_TO toward the phantom province
                # "Ney'S Rente".
                _never_strategic = (NEVER_STRATEGIC_ACTIONS
                                    if ADMIN_VERBS_NEVER_MARCH
                                    else _NON_ORDER_ACTIONS)
                _is_order = (_resolved_action not in _never_strategic
                             and not is_question(command_text))
                if world is not None and _is_order:
                    marshal_name = command_dict.get("marshal")
                    # PARSE-NEG: the strategic layer reads the raw utterance
                    # too, so it needs the same negation guard the action chain
                    # got — "Ney, march to Vienna, do not attack Mack" would
                    # otherwise still trip _detect_attack_on_arrival and arrive
                    # swinging. Only the NEGATION half is applied: blanking
                    # condition clauses here would destroy the `until …` that
                    # StrategicCondition exists to parse.
                    #
                    # FA-7, the same rule for the same reason: a DEFERRED
                    # clause must not reach the strategic layer either.
                    # Measured before this line existed — and identical at the
                    # pre-slice commit, so it is not a regression but a
                    # residue the deferral guard should have closed:
                    # `Ney, attack Mack, and hold Rhineland later` created a
                    # 2 AP STANDING HOLD on the phantom province "Rhineland
                    # Later" while the action chain had correctly read
                    # `attack`. `strip_deferred_clauses` never touches
                    # `until`, so StrategicCondition's one supported condition
                    # is safe here in a way `strip_condition_clauses` is not.
                    strategic_text, _ = strip_negated_clauses(effective_text)
                    strategic_text, _ = strip_deferred_clauses(strategic_text)
                    strategic = detect_strategic_command(strategic_text, marshal_name, world)
                    # FA slice 7: a BARE retreat verb is a retreat. "Ney, fall
                    # back" / "Ney, withdraw" parsed as `retreat` and were then
                    # upgraded by the strategic table's bare "fall back" /
                    # "withdraw" into a MOVE_TO with a GENERIC target — which
                    # the resolver reads as the nearest ENEMY's province
                    # (measured: "Mack blocks the path at Swabia", a retreat
                    # plotted toward the guns). "fall back to X" keeps its
                    # march; "Ney, retreat" was never upgraded.
                    if (strategic and A_BARE_RETREAT_IS_A_RETREAT
                            and _resolved_action == "retreat"
                            and strategic.get("strategic_type") == "MOVE_TO"
                            and (strategic.get("target") or "generic") == "generic"):
                        strategic = None
                    if strategic:
                        result["is_strategic"] = True
                        result["strategic_type"] = strategic["strategic_type"]
                        result["target_snapshot_location"] = strategic.get("target_snapshot_location")
                        result["strategic_condition"] = strategic.get("condition")
                        result["attack_on_arrival"] = strategic.get("attack_on_arrival", False)
                        # Override target with canonical name from strategic parser
                        strategic_target = strategic["target"]
                        # Apply fuzzy matching to strategic target (strategic parser
                        # only does exact match — typos like "bordeuex" slip through)
                        if strategic.get("target_type") == "region":
                            # IGR-A3: the SAME nation guard as the tactical
                            # ladder. Without it this fuzzy pass reopened the
                            # whole defect on the strategic verbs — "Ney,
                            # march/advance/head/proceed/make for/travel/push/
                            # deploy/relocate/journey to Austria" all created a
                            # real MOVE_TO order to Asturias, because only the
                            # bare "move to" phrasing reaches the guarded path.
                            _strategic_nation = resolve_typed_nation(
                                strategic_target, world)
                            if _strategic_nation:
                                # Keep the NATION, but in its canonical casing —
                                # the tactical ladder above already does this,
                                # and the bare `pass` here shipped the player's
                                # own lowercase ("Ney, proceed to Bavaria to
                                # support Davout" ordered a march to "bavaria").
                                strategic_target = _strategic_nation
                            else:
                                fuzzy_result = self.fuzzy_matcher.match_with_context(
                                    strategic_target, self._get_known_regions(world))
                                # PARSE-NEG evaluation: the same typo-shape gate
                                # the tactical scan got. Ungated, this promoted
                                # any leftover noun into a province — "Ney, hold
                                # the pass" became a standing HOLD on Nassau.
                                if fuzzy_result["action"] == "exact" or (
                                        fuzzy_result["action"] == "auto_correct"
                                        and _plausible_name_typo(
                                            strategic_target,
                                            fuzzy_result.get("match") or "")):
                                    strategic_target = fuzzy_result["match"]
                        elif strategic.get("target_type") == "marshal":
                            all_marshals = self._get_player_marshals(world) + self._get_known_enemies(world)
                            fuzzy_result = self.fuzzy_matcher.match_with_context(
                                strategic_target, all_marshals)
                            # WO-2: the strategic-marshal sibling of the two
                            # arms gated above — same typo-shape gate, same
                            # reason (partial-ratio junk bound sentence words
                            # to real commanders).
                            if fuzzy_result["action"] == "exact" or (
                                    fuzzy_result["action"] == "auto_correct"
                                    and _plausible_name_typo(
                                        strategic_target,
                                        fuzzy_result.get("match") or "")):
                                strategic_target = fuzzy_result["match"]
                        result["command"]["target"] = strategic_target
                        result["command"]["target_type"] = strategic["target_type"]
                        # CR-2: an order can never target its own executor —
                        # "support Ney" means SOMEONE supports Ney. The mock
                        # layer demotes these, but a live-LLM parse can still
                        # return marshal == target; unbinding here lets the
                        # marshal-choice clarification fire instead of the
                        # executor rejecting a self-targeted order.
                        if (strategic["target_type"] == "marshal"
                                and result["command"].get("marshal") == strategic_target):
                            result["command"]["marshal"] = None

                # CR-2: tell the player the sequel clause was not relayed —
                # design pillar: every input gets a response, nothing is
                # silently dropped.
                if dropped_sequel:
                    sequel_note = (
                        f'One order at a time, Sire — I have relayed the first. '
                        f'"{dropped_sequel}" must follow as its own command.')
                    result["warning"] = (f"{result['warning']} {sequel_note}"
                                         if result.get("warning") else sequel_note)
                    result["dropped_sequel"] = dropped_sequel

                # ══════════════════════════════════════════════════════
                # PT-H3: stamp the court the player NAMED, from the raw
                # sentence, once — here rather than beside either drop
                # site, because the two paths drop a demonym in different
                # ways and the MOCK parser never produces one at all
                # (it omits the target deliberately, mirroring the LLM
                # rule). A stamp beside the drops covers the live path
                # only, which is exactly what the mutation sweep caught.
                #
                # The DROP itself is untouched — it is the fix for
                # "the Austrians" -> the Spanish province Asturias.
                # ══════════════════════════════════════════════════════
                if (world is not None
                        and isinstance(result.get("command"), dict)
                        and not result["command"].get("target")
                        and result["command"].get("action")
                        not in VASSAL_FAMILY_ACTIONS):
                    _hint = demonym_to_nation(command_text, world)
                    if _hint:
                        result["command"]["target_nation_hint"] = _hint

                return result
            else:
                failure = {
                    "success": False,
                    "error": validation_result.get("error", "Unknown validation error"),
                    "suggestion": validation_result.get("suggestion"),
                    "raw_input": command_text,
                    "partial_marshal": llm_result.get("marshal"),
                    "partial_target": llm_result.get("target"),
                }
                # PARSE-NEG: this is not a failure to understand — the parser
                # read the sentence exactly and there is no order in it. main.py
                # answers with a specific Berthier line instead of the generic
                # recovery shrug.
                if llm_result.get("refusal"):
                    failure["refusal"] = llm_result["refusal"]
                    failure["refusal_phrase"] = llm_result.get("refusal_phrase")
                if llm_result.get("llm_error"):
                    failure["llm_error"] = True  # CR-3(c)
                return failure
        except Exception as e:
            # Safety net - should never happen but prevents crashes
            return {
                "success": False,
                "error": f"Parser error: {str(e)}",
                "raw_input": command_text
            }

    def _validate_command(self, parsed_command: Dict, game_state: Optional[Dict],
                          player_roster: Optional[List[str]] = None) -> Dict:
        """
        Validate that the parsed command makes sense.
        Now handles None marshal (for general orders).

        player_roster: live player-marshal names (CR-0); defaults to the
        legacy fallback seed when not supplied (direct/cold callers).
        """
        marshal = parsed_command.get("marshal")
        action = parsed_command.get("action")
        roster = player_roster if player_roster else self.valid_marshals

        # Meta commands (save/load) and cheat commands bypass all validation
        if action in ("meta_command", "cheat"):
            return {"valid": True, "warning": None}

        # Validation 1: Check action is valid
        if action not in self.valid_actions:
            return {
                "valid": False,
                "error": f"Unknown action: {action}",
                "suggestion": f"Valid actions: {', '.join(self.valid_actions)}"
            }

        # Validation 2: Marshal can be None for general orders - that's OK!
        # Only validate if a marshal was specified
        warning = None
        if marshal is not None and marshal not in roster:
            warning = f"Note: '{marshal}' is not a standard marshal. Standard marshals: {', '.join(roster)}"

        # Validation 3: Attack with no marshal and no target is ambiguous
        # (Let this through - executor will handle "find nearest enemy")
        # if action == "attack" and not parsed_command.get("target") and marshal is None:
        #     return {
        #         "valid": False,
        #         "error": "Attack command needs either a target or a marshal",
        #         "suggestion": "Try: 'attack Wellington' or 'Ney, attack'"
        #     }

        # All validations passed
        return {
            "valid": True,
            "warning": warning
        }

    # Bombardment keywords for auto-assign routing (checked against raw input)
    BOMBARD_KEYWORDS = ["bombard", "barrage", "shell", "cannonade"]

    def _classify_command(self, parsed_command: Dict, raw_input: str) -> str:
        """
        Classify the type of command.

        Args:
            parsed_command: The parsed command dict from LLM (AFTER fuzzy matching)
            raw_input: The original command text

        Returns:
            Command type string
        """
        action = parsed_command.get("action", "")
        target = parsed_command.get("target")
        marshal = parsed_command.get("marshal")

        # If a marshal is set (after fuzzy matching), it's a specific order
        if marshal is not None:
            return "specific"

        # No marshal specified - classify as general order based on action
        # Check raw input for bombardment keywords (routes to artillery auto-assign)
        raw_lower = raw_input.lower()
        is_bombardment = any(kw in raw_lower for kw in self.BOMBARD_KEYWORDS)

        if action == "attack":
            if is_bombardment:
                return "auto_assign_bombardment"  # "bombard Rhineland" - find nearest artillery
            elif not target:
                return "general_attack"  # "attack" alone - find nearest enemy
            else:
                return "auto_assign_attack"  # "attack Wellington" - find closest marshal to target
        elif action == "retreat":
            return "general_retreat"  # All forces retreat
        elif action == "defend":
            return "general_defensive"  # All forces defend
        elif action == "scout":
            if target:
                return "auto_assign_scout"  # "scout Rhineland" - find nearest marshal in range
            # "scout" alone with no target or marshal → fall through to specific (will error helpfully)

        # Default fallback
        return "specific"
    def parse_multiple(self, command_text: str, game_state: Optional[Dict] = None, world=None) -> List[Dict]:
        """
        Parse commands that mention multiple marshals.

        Example: "Ney and Davout, attack Wellington"

        Returns list of individual commands.
        """

        # V2-61: Only split on " and " when it appears between marshal names,
        # not mid-phrase (e.g. "defend and hold" should NOT split).
        all_marshal_names = set(n.lower() for n in (self._get_player_marshals(world) + self._get_known_enemies(world)))

        if " and " in command_text.lower():
            # Find all " and " positions and check if both sides have marshal names
            lower = command_text.lower()
            split_pos = None
            idx = 0
            while True:
                pos = lower.find(" and ", idx)
                if pos == -1:
                    break
                # Check word before " and " — is it a marshal name?
                before = lower[:pos].strip()
                before_word = before.split()[-1] if before.split() else ""
                # Check word after " and " — is it a marshal name?
                after = lower[pos + 5:].strip()
                after_word = after.split()[0].rstrip(",.!") if after.split() else ""
                if before_word in all_marshal_names and after_word in all_marshal_names:
                    split_pos = pos
                    break
                idx = pos + 1

            if split_pos is not None:
                # Split at the marshal-and-marshal boundary
                before_text = command_text[:split_pos].strip()
                after_text = command_text[split_pos + 5:].strip()

                # Extract the shared action/target from whichever part has it
                # Typically: "Ney and Davout, attack Wellington"
                # before = "Ney", after = "Davout, attack Wellington"
                results = []
                # If before is just a marshal name, apply after's action to both
                before_lower = before_text.lower().strip().rstrip(",")
                if before_lower in all_marshal_names:
                    # "Ney" + "Davout, attack Wellington" → make "Ney, attack Wellington"
                    # Extract action part from after_text (everything after the marshal name)
                    after_parts = after_text.split(",", 1)
                    if len(after_parts) > 1:
                        action_part = after_parts[1].strip()
                    else:
                        # No comma — try splitting after first word
                        after_words = after_text.split(None, 1)
                        action_part = after_words[1] if len(after_words) > 1 else ""
                    if action_part:
                        results.append(self.parse(f"{before_text}, {action_part}", game_state, world=world))
                    else:
                        results.append(self.parse(before_text, game_state, world=world))
                    results.append(self.parse(after_text, game_state, world=world))
                else:
                    # Both parts have their own actions
                    results.append(self.parse(before_text, game_state, world=world))
                    results.append(self.parse(after_text, game_state, world=world))
                return results

        # Single command (no marshal-and-marshal split found)
        return [self.parse(command_text, game_state, world=world)]

    def get_help(self) -> str:
        """
        Return help text for players.
        """
        return f"""
COMMAND HELP:

Valid Marshals:
{chr(10).join(f'  • {m}' for m in self.valid_marshals)}

Valid Actions:
{chr(10).join(f'  • {a}' for a in self.valid_actions)}

Example Commands:
  • "Ney, attack Wellington"
  • "Marshal Davout, defend the ridge"
  • "Grouchy, scout the area"
  • "Retreat to Paris"
  • "Ney and Davout, attack"

Tips:
  • You can be casual: "attack!" works
  • Commands are case-insensitive
  • Multiple marshals: Use "and" between names
"""


# Test code
if __name__ == "__main__":
    """
    Test the command parser with various inputs.
    """
    print("=" * 60)
    print("COMMAND PARSER TEST")
    print("=" * 60)

    # Create parser in mock mode
    parser = CommandParser(use_real_llm=False)

    print("\n" + "=" * 60)
    print("TEST 1: Valid Commands")
    print("=" * 60)

    valid_commands = [
        "Ney, attack Wellington",
        "Marshal Davout, defend",
        "Grouchy, scout the area",
        "Retreat!",
    ]

    for cmd in valid_commands:
        print(f"\nCommand: '{cmd}'")
        result = parser.parse(cmd)
        if result["success"]:
            print(f"✓ SUCCESS: {result['command']}")
        else:
            print(f"✗ FAILED: {result['error']}")

    print("\n" + "=" * 60)
    print("TEST 2: Invalid Commands (Should Fail)")
    print("=" * 60)

    invalid_commands = [
        "Murat, attack Wellington",  # Invalid marshal
        "Ney, dance",  # Invalid action
        "attack",  # Attack without target
    ]

    for cmd in invalid_commands:
        print(f"\nCommand: '{cmd}'")
        result = parser.parse(cmd)
        if result["success"]:
            print(f"✓ SUCCESS: {result['command']}")
        else:
            print(f"✗ FAILED (expected): {result['error']}")
            if result.get("suggestion"):
                print(f"  Suggestion: {result['suggestion']}")

    print("\n" + "=" * 60)
    print("TEST 3: Multiple Marshals")
    print("=" * 60)

    multi_command = "Ney and Davout, attack Wellington"
    print(f"\nCommand: '{multi_command}'")
    results = parser.parse_multiple(multi_command)

    for i, result in enumerate(results, 1):
        print(f"\n  Command {i}:")
        if result["success"]:
            print(f"  ✓ {result['command']}")
        else:
            print(f"  ✗ {result['error']}")
    print("\n" + "=" * 60)
    print("TEST 5: General Orders (No Marshal Specified)")
    print("=" * 60)

    general_commands = [
        ("attack", "Should find nearest enemy"),
        ("attack Wellington", "Should assign closest marshal to Wellington"),
        ("retreat", "Should retreat all forces"),
        ("defend", "Should put all forces on defensive"),
    ]

    for cmd, description in general_commands:
        print(f"\nCommand: '{cmd}'")
        print(f"Expected: {description}")
        result = parser.parse(cmd)
        if result["success"]:
            cmd_type = result["command"].get("type", "unknown")
            print(f"✓ Type: {cmd_type}")
            print(f"  Command: {result['command']}")
        else:
            print(f"✗ FAILED: {result['error']}")
    print("\n" + "=" * 60)
    print("TEST 4: Help Text")
    print("=" * 60)
    print(parser.get_help())

    print("=" * 60)
    print("ALL TESTS COMPLETE!")
    print("=" * 60)

