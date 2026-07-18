"""Single source for the "give battle" verb + idiom vocabulary.

Three seams previously carried three independent, silently-diverging copies
of "what counts as an attack word":

  - ``llm_client._parse_with_mock``      — the fast parser's keyword chain
  - ``context_carryover._TARGETING_ANCHORS`` — pronoun-reference anchoring
  - ``combat_executor._attack_verbs``    — the ESP-EV-4 guessed-target guard

The drift was player-visible. ``_TARGETING_ANCHORS`` already listed
smash/crush/destroy/engage/assault/storm/hit/strike/rout — verbs the fast
parser had no keyword for — so "Ney, attack Mack" then "Ney, crush him"
resolved the pronoun perfectly and *still* produced a Berthier shrug. And
the July-18 playtest report ("Ney, give them hell" did nothing) was the same
gap seen from the front: an idiom every player knows, routed nowhere.

This module owns the vocabulary once. Each consumer composes the pieces it
is entitled to — the sets are deliberately split rather than exported as one
blob, because the three seams are NOT interchangeable:

  - ``BATTLE_VERBS`` is safe at the PARSE seam (each word routes to the
    ``attack`` action).
  - ``MOVEMENT_ATTACK_VERBS`` (march / advance) must NEVER reach the parse
    seam — they belong to the ``move`` branch — but the post-resolution
    guard does need them, because "Ney, march on Vienna" is an attack order
    by the time it reaches combat.
  - ``POSITION_ONLY_ANCHORS`` are permissive for pronoun anchoring only;
    they deliberately route nowhere.

Golden Rule 6 holds throughout: this is a deterministic keyword table, never
an LLM judgement.
"""

import re

# ── Verbs that MEAN "give battle at the named target" ───────────────────────
# Safe to route to action="attack" at the parse seam. Every entry is matched
# WORD-BOUNDED by the helpers below (never as a bare substring), so a region
# or marshal name can never be a false positive ("Bordelais" must not match a
# "rout" fragment, "route" must not match "rout").
BATTLE_VERBS = frozenset({
    "attack", "charge", "engage", "assault", "storm", "smash", "crush",
    "destroy", "annihilate", "obliterate", "rout", "strike", "defeat",
    "fight", "ambush",
})

# Province-capture verbs. Distinct from BATTLE_VERBS because they take a
# REGION objective rather than an enemy army, but they resolve to the same
# executor action. "occupy" was historically the only one wired, so
# "Ney, take Vienna" / "capture Vienna" / "seize Vienna" all shrugged while
# "occupy Vienna" worked.
#
# DELIBERATE EXCLUSIONS (do not add — each is pinned by a regression test):
#   - "take"   — stamps mock confidence 0.95, which short-circuits the live
#                LLM (llm_client gate) and would silently degrade the CR-5
#                personality arms for "take care of X" to ASK. It also
#                swallows the corpus row "Talleyrand, what would it take to
#                get peace with Prussia?".
#   - "secure" — owned by the HOLD family ("secure and hold vienna").
CAPTURE_VERBS = frozenset({"occupy", "capture", "seize"})

# Attack verbs that are NOT parse-seam safe: at the parse seam they belong to
# the `move` branch ("Ney, march to Paris" is a move). The post-resolution
# guessed-target guard still needs them, because by the time an order reaches
# combat resolution "march on Vienna" is an attack.
MOVEMENT_ATTACK_VERBS = frozenset({"march", "advance"})

# Permissive for pronoun anchoring only — these describe a POSITION relative
# to a target ("flank him", "hit them on the left") and deliberately route to
# no action. Listed here so the anchor set stays a documented superset of the
# routed vocabulary rather than drifting by accident.
POSITION_ONLY_ANCHORS = frozenset({"hit", "flank", "harry"})

# Prepositions that put a pronoun/deixis token in object position.
TARGET_PREPOSITIONS = frozenset({
    "against", "at", "on", "upon", "toward", "towards",
})

# Pursuit verbs — already routed by their own fast-parser branch (the
# strategic parser upgrades them to PURSUE). Named here so the anchor set can
# include them without a second literal list.
PURSUIT_VERBS = frozenset({
    "pursue", "hunt", "chase", "hound", "intercept",
})

# Bombardment verbs — likewise already routed by their own branch.
BOMBARD_VERBS = frozenset({"bombard", "shell", "cannonade"})


def _word_alternation(words) -> str:
    """A word-bounded regex alternation over ``words`` (longest first, so the
    fullest verb wins and the pattern is stable regardless of set ordering)."""
    ordered = sorted(words, key=lambda w: (-len(w), w))
    return r"\b(?:" + "|".join(re.escape(w) for w in ordered) + r")\w*\b"


# Word-bounded matchers. ``\w*`` admits regular inflections (crush/crushes/
# crushing, destroy/destroys, storm/storms) without listing each form — but
# NOT across a word boundary, so "route" still cannot match "rout" (the "e"
# is inside the same word, and `\brout\w*\b` DOES match "route", so "rout" is
# handled separately below).
_INFLECTED = BATTLE_VERBS - {"rout"}
BATTLE_VERB_RE = re.compile(
    "(?:" + _word_alternation(_INFLECTED) + r"|\brouts?\b)", re.IGNORECASE)
CAPTURE_VERB_RE = re.compile(_word_alternation(CAPTURE_VERBS), re.IGNORECASE)

# ── Idioms: whole phrases that mean "attack", with no routable verb ─────────
# "give them hell" is the reported case. Each of these is a phrase a player
# actually types; none contains a word this module could route on its own
# ("give" alone is ditransitive — "give them autonomy" is a vassal order).
ATTACK_IDIOM_RE = re.compile(
    r"\bgiv\w*\s+(?:\w+\s+){0,3}?hell\b"          # give / gives / giving ... hell
    r"|\b(?:give|offer|force|join|accept)\s+(?:a\s+|the\s+)?battle\b"
    r"|\bbring\s+(?:\w+\s+){0,3}?to\s+battle\b"
    r"|\bno\s+quarter\b"
    r"|\bshow\s+(?:\w+\s+){0,2}?no\s+mercy\b"
    r"|\bput\s+(?:\w+\s+){0,3}?to\s+the\s+sword\b"
    r"|\b(?:wipe|stamp)\s+(?:\w+\s+){0,2}?out\b"
    # Object-anchored: "ride them down" is an attack, "ride down to Naples"
    # is a march. Requiring the pronoun keeps the two apart.
    r"|\b(?:cut|run|ride)\s+(?:them|him|her|it)\s+down\b"
    r"|\b(?:have|hack)\s+at\s+(?:them|him|her|it)\b"
    r"|\b(?:fall|set)\s+upon\b"
    r"|\bfinish\s+(?:him|her|them|it|off)\b"
    r"|\btake\s+the\s+fight\s+to\b",
    re.IGNORECASE,
)

# The semantically-empty words these idioms contribute. They must never reach
# the parser's fuzzy region-extraction pass: "hell" auto-corrected into the
# province *Algiers*, which then rode into Berthier's live recovery prompt as
# a fact the Emperor had stated. Consumed at the parser seam, not here.
IDIOM_FILLER_WORDS = frozenset({
    "give", "gives", "giving", "given", "hell", "quarter", "mercy", "sword",
    "battle", "fight", "finish", "wipe", "stamp", "hack", "upon", "down",
    "off", "out", "hard", "'em", "em",
})


def mentions_attack(command_lower: str) -> bool:
    """True when the text carries a battle verb, capture verb, or attack
    idiom. Deterministic; the single predicate the fast parser's attack
    branch consumes."""
    return bool(
        BATTLE_VERB_RE.search(command_lower)
        or CAPTURE_VERB_RE.search(command_lower)
        or ATTACK_IDIOM_RE.search(command_lower)
    )


def targeting_anchor_words() -> frozenset:
    """The pronoun-anchor allowlist for CR-4 context carryover: every verb
    that can put a pronoun in TARGET position, plus the object prepositions.

    Superset-by-construction of the routed vocabulary — the anchor set can
    never again drift narrower than what the parser can act on."""
    return (BATTLE_VERBS | CAPTURE_VERBS | MOVEMENT_ATTACK_VERBS
            | POSITION_ONLY_ANCHORS | PURSUIT_VERBS | BOMBARD_VERBS
            | TARGET_PREPOSITIONS | {"scout"})


def guard_attack_verbs() -> frozenset:
    """The verb set the ESP-EV-4 guessed-target guard strips from the raw
    order before asking "did the player name anything specific?".

    Includes MOVEMENT_ATTACK_VERBS (unlike the parse seam) because the guard
    runs AFTER resolution, where "march on Vienna" is an attack order."""
    return (BATTLE_VERBS | CAPTURE_VERBS | MOVEMENT_ATTACK_VERBS
            | POSITION_ONLY_ANCHORS | PURSUIT_VERBS | BOMBARD_VERBS
            | {"take", "go"})
