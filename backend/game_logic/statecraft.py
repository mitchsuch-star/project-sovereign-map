"""Great-power statecraft — AI-2c (docs/AI_INTENT_SPEC.md §3.4).

The assurance that the machinery produces RECOGNISABLE political actors:
Austria the aggrieved patient revanchist, Prussia the hesitant
opportunist, Russia the distant arbiter, Britain the paymaster. The
authored table lives in `nation_config.NATION_STATECRAFT` (the
honor-bias idiom — no LLM, no serialized object, read through
`world.get_statecraft`); this module owns the behaviour it biases.

It biases FOUR things only (§3.4): which rung a power prefers (ask
ordering — the NA-2 design-advancing front-move still outranks style),
which instrument it reaches for first, how it answers being coerced
(the acceptance delta at the ultimatum seam), and a `weight_mod` on its
design (authored 0 on every 1805 court — §5 pin 1 boot-neutrality by
construction, asserted in tests).

Britain's coercion answer is DERIVED, never hard-coded (§3.4 / pin 10):
*Britain answers coercion with subsidy while no hostile army stands on
British home soil.* Once one does, the subsidy wall drops and Britain
concedes on the ordinary path like any power. London is land-reachable
(the Channel is a toll, not a moat) — a hard-coded never-folds would be
the unbeatable-paymaster failure principle 7 forbids.
"""

from typing import Dict, List

# Coercion answers → acceptance delta on a coercive demand (blessed,
# in-band tunable; shape escalates). Applied at the player-ultimatum
# decision seam AFTER the ordinary acceptance score.
COERCION_HARDENS_DELTA = -15   # Austria: coercion confirms the grievance
COERCION_FOLDS_DELTA = 10      # Prussia: folds, then resents (§3.3)
COERCION_HONOUR_DELTA = -10    # Russia: escalates on honour
COERCION_SUBSIDY_WALL = -40    # Britain, while home soil is clear

# The AI-2c court-to-court counter arm: a haggling recipient whose
# refusal fell in this band tries one step down the ladder instead of
# walking away (who haggles is character; the band keeps it rare).
HAGGLE_BAND_FLOOR = 35

_ASK_FAMILY = {
    # reaches_first token -> the ask types that express it
    "align": ("non_aggression", "defensive_alliance", "alliance"),
    "buy": ("friendly_gift", "open_borders"),
    "bandwagon": ("open_borders", "non_aggression"),
    "ask": ("open_borders",),
    # "sponsor" is a branch, not an ask — it never reorders candidates.
}


def hostile_army_on_home_soil(world, nation: str) -> bool:
    """Any at-war enemy marshal standing on one of `nation`'s home
    regions. One marshal pass (GR8 — the get_disrupted_regions idiom);
    derived fresh each call, never latched."""
    home = set((getattr(world, "nation_starting_regions", {}) or {})
               .get(nation, []) or [])
    if not home:
        return False
    for marshal in world.marshals.values():
        owner = getattr(marshal, "nation", None)
        if not owner or owner == nation:
            continue
        # Review fix: the Marshal field is `captured_by` (not
        # `captured`) — a PRISONER paraded at the captor's capital is
        # not a hostile army, and neither is an empty-handed general.
        if getattr(marshal, "captured_by", ""):
            continue
        if int(getattr(marshal, "strength", 0) or 0) < 1000:
            continue
        location = getattr(marshal, "location", None)
        if location in home and world.is_at_war(nation, owner):
            return True
    return False


def coercion_acceptance_delta(world, nation: str) -> int:
    """The statecraft answer to being coerced — a delta on the ordinary
    acceptance score at the ultimatum seam. Neutral courts read 0
    byte-identically."""
    coercion = (world.get_statecraft(nation) or {}).get("coercion",
                                                        "neutral")
    if coercion == "hardens":
        return COERCION_HARDENS_DELTA
    if coercion == "folds":
        return COERCION_FOLDS_DELTA
    if coercion == "honour":
        return COERCION_HONOUR_DELTA
    if coercion == "subsidy":
        # Derived, never hard-coded: the wall stands only while no
        # hostile army stands on the home provinces (pin 10's narrowed
        # Britain clause — with one, the ordinary path decides).
        if hostile_army_on_home_soil(world, nation):
            return 0
        return COERCION_SUBSIDY_WALL
    return 0


def order_asks_by_statecraft(nation: str, candidates: List[str],
                             world) -> List[str]:
    """Reorder ask candidates so the power's preferred instrument family
    leads — a stable partition, never an addition or removal. Called
    BEFORE the NA-2 design-advancing front-move, so the design still
    outranks the style."""
    profile = world.get_statecraft(nation) or {}
    preferred: List[str] = []
    for token in profile.get("reaches_first", ()) or ():
        preferred.extend(_ASK_FAMILY.get(token, ()))
    if not preferred:
        return list(candidates)
    ranks: Dict[str, int] = {}
    for index, ask in enumerate(preferred):
        ranks.setdefault(ask, index)
    fallback = len(preferred)
    return sorted(candidates,
                  key=lambda ask: (ranks.get(ask, fallback),
                                   candidates.index(ask)))


def haggles(world, nation: str) -> bool:
    """Does this court counter rather than walk away? (The AI-2c
    court-to-court counter-offer arm's gate.)"""
    return bool((world.get_statecraft(nation) or {}).get("haggles", False))


def statecraft_weight_mod(world, nation: str) -> int:
    """The §3.4 weight modifier on the nation's design. Authored 0 for
    every 1805 court — the wire exists, the boot is untouched (pin 1)."""
    try:
        return int((world.get_statecraft(nation) or {})
                   .get("weight_mod", 0) or 0)
    except (TypeError, ValueError):
        return 0
