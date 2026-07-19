"""The "no specific target named" sentinels, and one predicate for them.

``generic`` is a DESIGNED sentinel, not an accident. The parse prompt tells the
model to emit it in so many words:

    "target region is obvious; otherwise set target to \\"generic\\""
    "support whoever needs it" -> target the most threatened ally (set target
        to generic)
    "pursue the enemy" -> target the nearest enemy marshal (set target to
        generic)
    "If you cannot determine the specific region, set target to \\"generic\\"
        and ambiguity to 60+."

PARSE_TOOL advertises it ("Enemy commander, region name, or 'generic'"), and
``_extract_valid_targets`` puts it in the valid-target list so validation
blesses it.

And then, until July 19, 2026, the TACTICAL executor rejected it:

    attack "generic" -> "Unknown target: generic"
    move   "generic" -> "Region 'generic' not found. Nearby: Guyenne, ..."

Three layers agreeing to produce a value the fourth refuses. That is the real
reason "Ney, give them hell" misbehaved in live mode — the model answered it
CORRECTLY (action=attack, target=generic, ambiguity 65, no invented enemy) and
the order died downstream. Every vague command that reaches the LLM shares the
fault, because vagueness is exactly what the prompt says to answer this way.

The STRATEGIC executor had the right idea all along and carried this set
privately; the fix is to hoist it here, share it, and normalize a generic
target to ``None`` at the parser seam — where the executor's existing,
well-exercised "no target -> resolve the nearest sensible one" path takes
over. That path already works: with ``target=None`` the same order produces a
full muster preview.
"""

from typing import Optional

# Hoisted verbatim from strategic_executor so the two paths cannot drift.
GENERIC_TARGETS = frozenset({
    "generic", "the enemy", "enemy", "enemies", "them",
    "the marshal", "marshal", "the general", "general",
    "the commander", "commander",
    "the region", "someone", "somebody", "anyone",
    "whoever", "nearest", "closest",
})


def is_generic_target(target: Optional[str]) -> bool:
    """True when ``target`` names no specific foe or place.

    A missing target counts: "no target" and "a target that means no target"
    must resolve the same way, which is the invariant the tactical path was
    missing.
    """
    if not target:
        return True
    return str(target).strip().lower() in GENERIC_TARGETS


def normalize_target(target: Optional[str]) -> Optional[str]:
    """Collapse a generic sentinel to ``None``; pass a real target through."""
    return None if is_generic_target(target) else target
