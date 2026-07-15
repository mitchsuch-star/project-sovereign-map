"""CR-5 Personality-Biased Disambiguation — delegation detection + routing
(COMMAND_ROBUSTNESS_SPEC.md §6; CR5_IMPLEMENTATION_BRIEF.md).

A *delegation verb* hands a marshal a problem and cedes the method ("Soult,
deal with Mack"). Unlike an explicit order ("Soult, attack Mack"), the
concrete action is not stated — it must be *inferred from the marshal's
character*:

    aggressive -> engage and destroy       (attack / move-to-engage)
    cautious   -> observe first, stay poised (scout / hold)
    literal    -> refuse to guess            -> ASK the Emperor
    neutral/unset/mock -> never guess a default -> ASK

**Golden Rule 6 holds:** the live LLM only picks which concrete *action* an
aggressive/cautious delegation becomes (via the prompt table); the literal /
neutral / mock ASK arm and ALL routing here are DETERMINISTIC. The LLM never
decides to ask, and the deterministic layer overrides the LLM for the literal
arm (a literal marshal asks even if the model guessed an action).

This module owns:
  - the frozen delegation-verb allowlist (§6.2);
  - ``detect_delegation`` — is this raw command a delegation to a known
    marshal at a resolvable target?
  - ``classify_arm`` — which of {aggressive, cautious, ask} applies, given the
    marshal's personality and whether the parse resolved to a real action;
  - ``build_delegation_clarification`` — the deterministic two-option ASK
    (routes into the shipped CR-2 ``command_clarification`` surface).

The excluded strategic/diplomatic verbs (march/pursue/support/reinforce/...)
are OWNED by the fast parser + CR-3 remaps and must NOT appear here (§6.2
double-ownership guard).
"""

import re
from typing import Dict, List, Optional

from backend.ai.validation import VALID_ACTIONS
from backend.commands.clarification import _clarification_response
from backend.display_names import humanize_entity_name

# ── Frozen delegation-verb allowlist (COMMAND_ROBUSTNESS_SPEC §6.2) ──────────
# Method-free "hand it to the marshal" phrasings with NO fast-parser owner.
# Ordered longest-first so "take care of" wins over a bare "care" fragment and
# the matched phrase is the fullest one.
DELEGATION_VERBS = (
    "do something about",
    "take care of",
    "deal with",
    "attend to",
    "sort out",
    "see to",
    "handle",
)

# Word-boundary alternation; longest phrases first (see ordering above).
_DELEGATION_RE = re.compile(
    r"\b(" + "|".join(re.escape(v) for v in DELEGATION_VERBS) + r")\b\s*(.*)$",
    re.IGNORECASE,
)

# A leading "Marshal Ney, ..." / "Ney, ..." / "Marshal Ney ..." address token
# (mirrors the parser's ADDRESS_TOKEN_RE contract) — used to recover the
# addressed marshal when the upstream parse dropped it (mock "deal with X" leaves
# marshal unset). The trailing comma is OPTIONAL: "Marshal Soult deal with Mack"
# (no comma — the most natural English phrasing of the exact affordance CR-5
# exists to honor) must resolve the same as "Soult, deal with Mack". The captured
# word is always validated against the live roster via ``get_marshal`` below, so a
# non-marshal first word (e.g. the verb in a bare "handle Mack") is rejected — the
# relaxed comma cannot manufacture a false delegation.
_ADDRESS_RE = re.compile(r"^\s*(?:marshal\s+)?([A-Za-z][A-Za-z'\-]+)\s*,?",
                         re.IGNORECASE)

_NEUTRAL_PERSONALITIES = frozenset({"balanced", "loyal"})

# §6.7 discoverability hint — shown ONCE per campaign the first time the player
# delegates, teaching that the affordance exists. Static copy (mock-safe).
DELEGATION_FIRST_USE_HINT = (
    'Berthier: "You may hand a marshal a task and let him solve it his own '
    'way, Sire — each acts to his character."')


def maybe_delegation_hint(world) -> Optional[str]:
    """Return the once-per-campaign delegation discoverability hint (§6.7) the
    first time it is called for a real delegation, latching the flag; None
    thereafter. Never fires on explicit verbs (the caller only invokes it once
    a delegation has been detected)."""
    if getattr(world, "delegation_hint_shown", False):
        return None
    world.delegation_hint_shown = True
    return DELEGATION_FIRST_USE_HINT


class DelegationMatch:
    """A resolved delegation command: a known marshal, a real target, and the
    verbatim clause the player used.

    ``target`` is the ATTACK target (an enemy marshal to give battle, or a
    region to assault). ``scout_target`` is the OBSERVE target — you attack an
    army but you scout a *place*, so for an enemy marshal this is his LOCATION
    (region), which the scout executor can actually reach; for a region
    objective the two coincide.
    """

    __slots__ = ("marshal", "personality", "target", "scout_target",
                 "target_display", "verb", "clause")

    def __init__(self, marshal: str, personality: str, target: str,
                 scout_target: str, target_display: str, verb: str,
                 clause: str):
        self.marshal = marshal
        self.personality = personality
        self.target = target                # ATTACK target (marshal or region)
        self.scout_target = scout_target    # OBSERVE target (a region)
        self.target_display = target_display  # player-facing label
        self.verb = verb                    # matched delegation verb
        self.clause = clause                # e.g. 'deal with Mack' (verbatim-ish)


def _resolve_target(world, remainder: str) -> Optional[tuple]:
    """Resolve the text after the delegation verb to a concrete target.

    Prefers an enemy marshal (the §6.2 "target = enemy" table), then a region
    (the "target = objective" table). Returns (attack_target, scout_target,
    display) or None. For an enemy marshal, scout_target is his LOCATION (you
    scout a place); for a region they coincide. Matches the LONGEST known
    entity name in the remainder so "ArchdukeCharles" beats a "Charles"
    fragment. Backend uses raw names; Godot humanizes camelCase at render.
    """
    if not remainder:
        return None
    hay = remainder.lower()

    best = None  # (length, raw_name, scout_target)

    def _consider(name: str, scout_target: str):
        nonlocal best
        if not name:
            return
        # Match the raw KEY ("ArchdukeCharles") OR its humanized spaced form
        # ("Archduke Charles"), so a player who types the natural spaced name the
        # UI shows resolves too (not just the exact camelCase token). The winner
        # is still keyed by the RAW name — display humanization happens on return.
        for needle in {name.lower(), humanize_entity_name(name).lower()}:
            if needle in hay and (best is None or len(needle) > best[0]):
                best = (len(needle), name, scout_target)

    for m in world.get_enemy_marshals():
        if getattr(m, "strength", 0) > 0:
            # Scout the marshal's LOCATION (a reachable region); attack the
            # marshal himself.
            _consider(m.name, getattr(m, "location", m.name) or m.name)
    if best is not None:
        # target/scout_target stay RAW (executor + reissue keys); the display is
        # humanized so no camelCase key ever reaches player copy (R7).
        return best[1], best[2], humanize_entity_name(best[1])

    # No enemy matched — try a region objective (attack == scout == region).
    for region_name in getattr(world, "regions", {}):
        _consider(region_name, region_name)
    if best is not None:
        return best[1], best[2], humanize_entity_name(best[1])
    return None


def detect_delegation(world, raw_command: str,
                      parsed_command: Optional[Dict] = None
                      ) -> Optional[DelegationMatch]:
    """Return a DelegationMatch when ``raw_command`` is a delegation verb
    addressed to a known field marshal at a resolvable target, else None.

    Deterministic and LLM-free. Works whether the upstream parse succeeded
    (live: resolved to some action) or failed (mock: action unknown) — the
    delegation verb in the raw text is the authority, not the parse.
    """
    if not raw_command:
        return None
    m = _DELEGATION_RE.search(raw_command)
    if not m:
        return None
    verb = m.group(1).lower()
    remainder = (m.group(2) or "").strip()

    # ── Recover the addressed marshal ──
    marshal_name = None
    if parsed_command:
        marshal_name = parsed_command.get("marshal")
    if not marshal_name:
        addr = _ADDRESS_RE.match(raw_command)
        if addr:
            candidate = addr.group(1)
            found = world.get_marshal(candidate) if hasattr(world, "get_marshal") else None
            if found is not None:
                marshal_name = found.name
    if not marshal_name:
        return None

    marshal = world.get_marshal(marshal_name) if hasattr(world, "get_marshal") else None
    # Delegation applies to the player's OWN field marshals only.
    if marshal is None or getattr(marshal, "strength", 0) <= 0:
        return None
    if marshal.name not in {fm.name for fm in world.get_field_marshals()}:
        return None

    resolved = _resolve_target(world, remainder)
    if resolved is None:
        # No concrete target ("handle the situation") — fall through to the
        # existing pipeline (CR-4 carryover already ran; Berthier recovers).
        return None
    target, scout_target, target_display = resolved

    personality = (getattr(marshal, "personality", "") or "").lower()
    clause = f"{verb} {target_display}".strip()
    return DelegationMatch(marshal.name, personality, target, scout_target,
                           target_display, verb, clause)


# Battle-STARTING actions. A cautious marshal must never be handed one of these
# off a vague order (§6.2 cautious row / §6.3c "never launches an assault on a
# vague order") — the live LLM is not reliable enough to guarantee it, so the
# router clamps a cautious delegation that resolved to a battle action back to
# scout. Deterministic safety net, not a personality change.
BATTLE_ACTIONS = frozenset({"attack", "charge", "bombard"})

# The aggressive -> engage arm resolves an inferred, AP-committing, undo-less
# battle start. It rides a delegation-INFERRED strategic PURSUE order whose every
# auto-attack seam is now covered by the CR-5 Phase-3 fortification/terrain-aware
# bad-odds gate (strategic.py `_inferred_attack_gate` + the first-step gates in
# strategic_executor.py). Phase 4 (July 7, 2026) flipped this True after the
# guardrail-(d) personality freeze sign-off (§6.8) and after closing the two
# first-step PURSUE seams the per-turn gate did not cover (co-located creation +
# move-failed-at-target). An aggressive delegation now produces a tagged PURSUE
# that engages on contact, with the one-modal confirm protecting a dug-in
# superior force. Setting this back to False re-degrades the arm to the safe ASK.
AGGRESSIVE_ATTACK_ARM_ENABLED = True


def classify_arm(personality: str, parse_resolved_to_action: bool) -> str:
    """Which interpretation arm applies.

    - aggressive / cautious WITH a resolved concrete action (live LLM gave us
      one via the §6.2 prompt table) -> that biased arm.
    - literal, neutral (balanced/loyal), unset, OR any personality whose parse
      did NOT resolve to a real action (mock mode / LLM failure) -> ASK.

    This single rule delivers guardrail (e): mock never produces a bias, it
    degrades to the ASK clarification.
    """
    p = (personality or "").lower()
    if parse_resolved_to_action and p == "aggressive":
        return "aggressive"
    if parse_resolved_to_action and p == "cautious":
        return "cautious"
    return "ask"


def route_arm(personality: str, parse_resolved: bool) -> str:
    """The arm the router acts on, applying the phase gate: an aggressive
    delegation degrades to ASK until the Phase-3 lethal-seam gate lands and
    Phase 4 flips AGGRESSIVE_ATTACK_ARM_ENABLED."""
    arm = classify_arm(personality, parse_resolved)
    if arm == "aggressive" and not AGGRESSIVE_ATTACK_ARM_ENABLED:
        return "ask"
    return arm


def parse_resolved_to_action(parsed: Dict) -> bool:
    """True when the upstream parse produced a real, executable action via the
    LIVE LLM — never a mock / fast-parser result.

    Guardrail (e) is a MODE gate, not merely a validity gate: the personality
    bias is a live-LLM feature (§6.7 live-only exposure). The mock/fast parser
    can incidentally resolve a delegation to a real action when the remainder
    carries an action keyword ("deal with the *attack* on Wellington" -> attack),
    and confidence >= 0.7 short-circuits the live call even in anthropic mode. In
    BOTH cases the LLM never applied the §6.2 table, so there is no bias to act
    on — the delegation must degrade to the ASK clarification. Only the live
    providers stamp mode anthropic/groq; the fast parser stamps "mock"."""
    if not parsed or not parsed.get("success"):
        return False
    if (parsed.get("mode") or "").lower() == "mock":
        return False
    action = (parsed.get("command") or {}).get("action")
    return bool(action) and action in VALID_ACTIONS and action != "unknown"


def describe_cautious_delegation(match: DelegationMatch,
                                 action: Optional[str]) -> str:
    """Soft-note attribution for a cautious delegation (§6.3c legibility — the
    surface NAMES the marshal's character) with a typed one-tap reissue. Honest
    copy: the scout still burns a turn (§6.3c "battle-starting vs not, NOT
    reversible vs irreversible")."""
    if action == "scout":
        deed = f"will reconnoiter {match.target_display} before he commits"
    elif action == "hold":
        deed = "will hold his ground and stay poised"
    elif action == "fortify":
        deed = "will dig in rather than rush forward"
    else:
        deed = f"will observe {match.target_display} first"
    # Reissue hint uses the humanized DISPLAY (never the raw camelCase key) —
    # _resolve_target now resolves the spaced form too, so the suggested typed
    # command parses (R7 — no internal key in player copy).
    return (f'{match.marshal}, cautious as ever, {deed} — it costs a turn. '
            f'Say "{match.marshal}, attack {match.target_display}" to press the '
            f'assault instead.')


def describe_inferred_bad_odds(marshal_name: str, enemy_name: str) -> str:
    """One-modal bad-odds confirm copy for a delegation-INFERRED aggressive
    assault into a fortified / superior force (§6.3c legibility — the surface
    NAMES the acting marshal's reading; Acc #7). Used ONLY for delegation-
    inferred orders; an explicitly-typed order keeps the generic contact message
    and never triggers this modal. Deterministic template (mock-safe, Golden-
    Rule-6-safe — no LLM echo; word-echoing is CR-5b)."""
    # Humanize the enemy KEY so a camelCase name (ArchdukeCharles) never reaches
    # this modal (R7). The acting marshal is always an authored-clean player name.
    enemy_display = humanize_entity_name(enemy_name)
    return (f"{marshal_name} reads this as a call to give battle, Sire — but "
            f"{enemy_display} stands dug in and in greater strength. He will "
            f"charge on your word. Confirm the assault, or hold him back?")


# ── CR-5b Flavor Echoing (COMMAND_ROBUSTNESS_SPEC §6.4 rider (a)) ────────────
# "The game heard me": on a delegation, the marshal's IMMEDIATE reply (the
# RESPONSE seam) echoes the player's tone. LIVE mode composes it (the `flavor`
# field on the parse call — zero extra LLM call); this module owns the
# deterministic FLOOR (used when the live line is empty/errored/register-
# violating) and the REGISTER GATE that drops a bad live line to that floor.
#
# The non-parroting contract (the CR-5b entry gate): the reply is keyed to the
# marshal's CHARACTER + the RESOLVED deed's ATTITUDE, and NEVER splices the raw
# delegation verb or names a mechanical action. The deterministic router owns
# the deed (the pursue-order confirmation / cautious note); the flavor is pure
# character color layered on top, so it can never contradict the action the
# marshal actually took (the live LLM is unreliable for delegation-shaped input
# — July 7 probe — so it must not be trusted to name the deed).

# Deed/action words a flavor line must NOT contain — the deterministic router,
# not the LLM, owns the deed. Superset of the mechanically-meaningful VALID_
# ACTIONS verbs (+ inflections), the strategic enums, and the plain-English
# deed synonyms (reconnoiter/observe/watch — so a cautious prefix cannot restate
# the "scout" its note already owns). Matched WORD-BOUNDED (never as a substring)
# so an enemy/region name is never a false positive.
_FLAVOR_ACTION_WORDS = frozenset({
    "attack", "attacks", "attacking", "assault", "assaults", "assaulting",
    "scout", "scouts", "scouting", "reconnoiter", "reconnoitre", "recon",
    "observe", "observes", "observing", "watch", "watches", "watching",
    "move", "moves", "moving", "march", "marches", "marching",
    "pursue", "pursues", "pursuing", "chase", "chases", "chasing",
    "hold", "holds", "holding", "defend", "defends", "defending",
    "fortify", "fortifies", "fortifying", "entrench", "entrenches",
    "charge", "charges", "charging", "bombard", "bombards", "bombarding",
    "retreat", "retreats", "garrison", "recruit", "engage", "engages",
    "support", "reinforce", "reinforces",
    # strategic enums (lowercased below before matching)
    "move_to",
})

# Personality/temperament adjectives a flavor line must NOT contain — the
# describe_cautious_delegation note already says "cautious as ever", so a live
# line restating the character word double-narrates (§4: personality is *what*,
# not a label to echo). Word-bounded like the action set.
_FLAVOR_PERSONALITY_WORDS = frozenset({
    "cautious", "prudent", "prudence", "aggressive", "eager",
    "literal", "measured", "impetuous", "reckless",
})

_FLAVOR_FIRST_PERSON = frozenset({
    "i", "me", "my", "mine", "we", "us", "our", "ours",
})

# The raw delegation verbs, matched WORD-BOUNDED (an incidental substring like
# "mishandled" / "handles" must NOT trip the parroting guard — only a genuine
# spliced verb does). Mirrors _DELEGATION_RE's word-boundary contract.
_FLAVOR_VERB_RE = re.compile(
    r"\b(" + "|".join(re.escape(v) for v in DELEGATION_VERBS) + r")\b",
    re.IGNORECASE,
)
_FLAVOR_WORD_RE = re.compile(r"[a-z_]+")


def _strip_quoted_spans(line: str) -> str:
    """Blank out quoted spans (the marshal's own speech) so the first-person
    guard only inspects the NARRATOR's words — first person is legitimate inside
    a quoted line, forbidden outside it (§4 register).

    A speech-delimiter apostrophe is one NOT flanked by letters on BOTH sides;
    a CONTRACTION apostrophe (letter'letter, as in "they'll"/"won't") is not a
    delimiter, so a contraction inside quoted speech no longer corrupts the span
    (the review's high finding). Double-quoted spans strip whole via regex."""
    line = re.sub(r'"[^"]*"', " ", line)
    delims = [
        i for i, ch in enumerate(line)
        if ch == "'" and not (0 < i < len(line) - 1
                              and line[i - 1].isalpha()
                              and line[i + 1].isalpha())
    ]
    chars = list(line)
    for k in range(0, len(delims) - 1, 2):
        for j in range(delims[k], delims[k + 1] + 1):
            chars[j] = " "
    return "".join(chars)


def flavor_passes_register(line: Optional[str],
                           match: Optional[DelegationMatch]) -> bool:
    """The register gate: True iff a LIVE flavor line is safe to show the
    player; False drops it to the deterministic floor. Enforces the CR-5b
    non-parroting contract + the §4 voice register. Pure predicate, no state."""
    if not line or not isinstance(line, str) or not line.strip():
        return False
    low = line.lower()
    words = set(_FLAVOR_WORD_RE.findall(low))

    # (i) Parroting guard — the raw delegation verb must never be spliced back
    # (the exact §6.4 failure mode this gate exists to forbid). Word-bounded so
    # an incidental substring ("mishandled") is not a false positive.
    if _FLAVOR_VERB_RE.search(low):
        return False
    # (ii) Double-parrot-with-rider-(d) guard — the RECORD seam already quotes
    # the verbatim clause; the RESPONSE seam must not repeat it.
    if match is not None:
        if match.clause and match.clause.lower() in low:
            return False
        if match.verb and match.verb.lower() in low:
            return False
    # (iii) Action-contradiction guard — the router owns the deed; a flavor line
    # that names an action risks contradicting the deterministic resolution.
    if words & _FLAVOR_ACTION_WORDS:
        return False
    # (iii-b) Personality-label guard — the note already names his character;
    # echoing "cautious"/"eager" double-narrates (§4 personality is not a label).
    if words & _FLAVOR_PERSONALITY_WORDS:
        return False
    # (iv) Internal-key / camelCase leak guard (R7) — no raw entity key.
    if "_" in line or re.search(r"[a-z][A-Z]", line):
        return False
    # (v) Length guard — one to two short clauses, not a paragraph.
    if line.count(".") + line.count("!") + line.count("?") > 2:
        return False
    if line.count(",") > 2:
        return False
    # (vi) Voice-register guard — first person only INSIDE a quoted span (the
    # marshal speaking); a narrator in first person breaks §4 voice.
    outside = set(_FLAVOR_WORD_RE.findall(_strip_quoted_spans(low)))
    if outside & _FLAVOR_FIRST_PERSON:
        return False
    return True


# A small set of interchangeable aggressive-floor templates (all target-anchored
# ATTITUDE, all register-clean). Picking DETERMINISTICALLY across (marshal,
# target) means different quarries read differently, so the floor is not a single
# memorizable sentence — while staying a pure function (testable, no RNG). The
# LIVE ceiling still carries the per-command variance; this only blunts the
# fixed-floor memorization edge on the fallback path (review DESIGN_INTENT note).
_AGGRESSIVE_FLOORS = (
    "{marshal} needs no second word, Sire — {target} is his.",
    "{marshal} asks no further order, Sire — {target} will not slip him.",
    "{marshal} takes {target} for his own, Sire, and asks no more.",
)


def describe_aggressive_delegation(match: DelegationMatch) -> str:
    """The AGGRESSIVE arm's deterministic FLOOR — the live-mode fallback shown
    when the LLM flavor line is empty/errored/register-dropped (mock never
    reaches this arm; guardrail e routes it to ASK). Target-anchored ATTITUDE
    only: the pursue-order confirmation / bad-odds modal owns the deed, so this
    NEVER names a mechanical action or echoes the raw delegation verb (§6.4
    non-parroting contract). Deterministic + mock-safe (no LLM echo — that is
    the live ceiling). target_display is humanized upstream (R7)."""
    idx = (len(match.marshal) + len(match.target_display)) % len(_AGGRESSIVE_FLOORS)
    return _AGGRESSIVE_FLOORS[idx].format(
        marshal=match.marshal, target=match.target_display)


def resolve_delegation_flavor(match: DelegationMatch, arm: str,
                              live_flavor: Optional[str]) -> Optional[str]:
    """Ceiling -> floor resolver for the AGGRESSIVE executed arm: the register-
    passing live line when present, else the deterministic floor. Mirrors the
    generate_berthier_recovery ceiling/fallback shape but with NO extra LLM call
    (the flavor already rode the parse). Returns None for any other arm — the
    cautious arm uses resolve_live_cautious_prefix, and the ASK arm is out of
    CR-5b scope (its clause-quote is already the echo)."""
    if arm != "aggressive":
        return None
    if flavor_passes_register(live_flavor, match):
        return live_flavor.strip()
    return describe_aggressive_delegation(match)


def resolve_live_cautious_prefix(match: DelegationMatch,
                                 live_flavor: Optional[str]) -> Optional[str]:
    """A LIVE-ONLY, register-gated spoken PREFIX for the cautious arm. The
    existing describe_cautious_delegation note keeps sole ownership of the deed
    ("reconnoiter ... costs a turn ... press the assault"); this adds one short
    clause of character color IN FRONT of it, carrying NO deed word (the gate's
    action guard drops any line that restates "scout"/"observe"). Returns None
    when the live line is absent or register-violating — so nothing is prefixed
    and ONLY the existing note shows. There is deliberately NO deterministic
    cautious floor sentence: that would double-narrate the shipped note.

    A cautious marshal's register is *measured* (§4), so an exclamatory line is
    dropped too — an eager "!" would read as a tonal contradiction with the
    reconnoiter-first deed the note then states."""
    if flavor_passes_register(live_flavor, match) and "!" not in (live_flavor or ""):
        return live_flavor.strip()
    return None


def _ask_question(match: DelegationMatch) -> str:
    """The personality-named ASK copy (§6.3c legibility — the surface NAMES
    the marshal's character). Literal Soult declines to presume; a neutral /
    unset marshal has no character to read, so Berthier asks plainly."""
    who = match.target_display
    if match.personality == "literal":
        return (f'{match.marshal} will not presume your meaning, Sire. '
                f'"{match.clause}" — give battle, or observe {who}?')
    # neutral / balanced / loyal / unset
    return (f'How shall this be done, Sire? "{match.clause}" — '
            f'is {who} to be attacked, or observed?')


def build_delegation_clarification(world, match: DelegationMatch,
                                   raw_command: str) -> Dict:
    """The deterministic two-option ASK, rendered onto the shipped CR-2
    ``command_clarification`` surface (no parallel question path).

    Each option carries a full reissue ``command`` string the popup / typed
    answer re-parses verbatim (Golden Rule 6 — the answer is a plain re-parse,
    never an LLM call)."""
    # PF-2: the ASK's question text offers the natural-language verbs "give
    # battle"/"attacked" and "observe"/"observed", but a typed answer was only
    # matched against option labels ("Attack"/"Scout") and targets — so typing
    # the very words the question used fell through to a fresh mis-parse
    # ("Region 'generic' not found"). Each option now declares answer aliases
    # (consumed generically by interpret_clarification_answer) that cover both
    # the literal and the neutral phrasings.
    options: List[Dict] = [
        {
            "label": "Attack",
            "value": "delegation_choice",
            "target": match.target,
            "command": f"{match.marshal} attack {match.target}",
            # Include the target-qualified forms a player naturally types back
            # ("attack Mack", "engage Mack") so the printed choice resolves.
            "aliases": ["attack", "attacked", "give battle", "battle",
                        "engage", "fight", "assault",
                        f"attack {match.target_display}",
                        f"engage {match.target_display}"],
        },
        {
            "label": "Scout",
            "value": "delegation_choice",
            "target": match.scout_target,
            "command": f"{match.marshal} scout {match.scout_target}",
            # PF-2 review fix: the literal ASK prints "observe {who}" (e.g.
            # "observe Mack"), so the target-qualified forms MUST be aliased or
            # typing the printed scout choice verbatim still mis-parses —
            # asymmetric with the attack side's bare "give battle".
            "aliases": ["scout", "observe", "observed", "watch",
                        "reconnoiter", "recon", "reconnaissance",
                        f"observe {match.target_display}",
                        f"watch {match.target_display}"],
        },
    ]
    response = _clarification_response(
        world,
        question=_ask_question(match),
        options=options,
        clarification_kind="delegation",
        strategic_type=None,
        raw_input=raw_command,
    )
    # The Godot popup titles from ``marshal`` ("<NAME> ASKS:"). A LITERAL
    # marshal declines to presume in HIS OWN voice, so the title reads
    # "SOULT ASKS:" — the spec §6.1 headline. A neutral / interim fallback has
    # no character to read, so it stays the chief of staff's question
    # ("BERTHIER ASKS:", the _clarification_response default).
    if match.personality == "literal":
        response["marshal"] = match.marshal
    # The ASK names a concrete target — a bare "yes" resolves to Attack (the
    # first option), which the CR-2 answer-interpreter already does.
    response["interpreted_target"] = match.target
    return response
