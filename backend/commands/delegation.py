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

# A leading "Marshal Ney, ..." / "Ney, ..." address token (mirrors the parser's
# ADDRESS_TOKEN_RE contract) — used to recover the addressed marshal when the
# upstream parse dropped it (mock "deal with X" leaves marshal unset).
_ADDRESS_RE = re.compile(r"^\s*(?:marshal\s+)?([A-Za-z][A-Za-z'\-]+)\s*,",
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

    best = None  # (length, name, scout_target)

    def _consider(name: str, scout_target: str):
        nonlocal best
        if not name:
            return
        needle = name.lower()
        # word-ish containment: the entity name appears as a run in the text
        if needle in hay and (best is None or len(needle) > best[0]):
            best = (len(needle), name, scout_target)

    for m in world.get_enemy_marshals():
        if getattr(m, "strength", 0) > 0:
            # Scout the marshal's LOCATION (a reachable region); attack the
            # marshal himself.
            _consider(m.name, getattr(m, "location", m.name) or m.name)
    if best is not None:
        return best[1], best[2], best[1]

    # No enemy matched — try a region objective (attack == scout == region).
    for region_name in getattr(world, "regions", {}):
        _consider(region_name, region_name)
    if best is not None:
        return best[1], best[2], best[1]
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

# The aggressive -> attack arm resolves an inferred, AP-committing, undo-less
# battle start that rides the fortification-BLIND attack-on-arrival seam
# (strategic_executor.py, `_strategic_execution: True`). It CANNOT ship until
# the Phase-3 legibility gate covers that seam (CR5_IMPLEMENTATION_BRIEF §3).
# Until Phase 4 flips this True, an aggressive delegation degrades to the ASK —
# the same safe default as a neutral marshal (never an ungated battle start).
AGGRESSIVE_ATTACK_ARM_ENABLED = False


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
    """True when the upstream parse produced a real, executable action (the
    live path) rather than unknown/failed (the mock path)."""
    if not parsed or not parsed.get("success"):
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
    return (f'{match.marshal}, cautious as ever, {deed} — it costs a turn. '
            f'Say "{match.marshal}, attack {match.target}" to press the '
            f'assault instead.')


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
    options: List[Dict] = [
        {
            "label": "Attack",
            "value": "delegation_choice",
            "target": match.target,
            "command": f"{match.marshal} attack {match.target}",
        },
        {
            "label": "Scout",
            "value": "delegation_choice",
            "target": match.scout_target,
            "command": f"{match.marshal} scout {match.scout_target}",
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
    # The ASK names a concrete target — a bare "yes" resolves to Attack (the
    # first option), which the CR-2 answer-interpreter already does.
    response["interpreted_target"] = match.target
    return response
