"""
ES-7 "The Cost of Success" — estate endowments / dotations (Economy Revisit S7).

Spec: docs/ECONOMY_REVISIT_SPEC.md §0.6.2 as amended by the §0.6.7 gate record
(July 9, 2026 — authoritative): the endowment is a FULL-income redirect.

A marshal who wins battles builds a rising expectation of reward
(`REP_STEP × battles_won`, capped). The player meets it by endowing him with
an ESTATE in a conquered province — the province's full effective income is
redirected to his household (the nation's ledger loses the same amount as a
signed "Dotations" component) and he gains a province-derived honorific
title (flavor only, Golden Rule 6). An unmet or revoked expectation erodes
loyalty via `modify_trust` — NEVER `modify_relationship` (the Jealousy graph
is out of bounds; a grep-assert guard test pins this file).

Paying stops the bleed, never buys trust: `grant_dotation` applies ZERO
trust on grant — the endowment is a promise, not a purchase.

Europe-scoped (N1 pattern, like ES-2/ES-3): the legacy 19-region fixture
world has no dotation economy, so no legacy test pins move.

All constants are the E5 blessed starting values (§0.6.7) — the two-sided
stacked band test (test_economy_e1_band.py) is the tuning instrument;
retunes inside the blessed band need no new gate.
"""

from typing import Dict, List, Optional, Tuple

# ═══════════════ E5 BLESSED CONSTANTS (§0.6.7, July 9, 2026) ═══════════════

# Expectation: gold/turn a marshal feels owed per battle won, and its cap.
# Comparable 1:1 with estate income — that comparability IS the legibility.
REP_STEP = 40
EXPECTATION_CAP = 300

# One-time investiture fee (gold) for creating a marshal's title — his FIRST
# estate. Adding further estates to an existing title is 1 AP, no fee.
# (A marshal stripped of ALL estates needs a fresh investiture — the title
# lapsed with the land; recorded interpretation, see spec Track-2 S7 note.)
INVESTITURE_FEE = 200

# Erosion curve: -min(EROSION_MAX, ceil(shortfall / SHORTFALL_PER_POINT))
# per turn via modify_trust. Trust's native floor at 0 is the only floor.
EROSION_MAX = 3
SHORTFALL_PER_POINT = 50

# Grace debounce (blessed 2, was 1): erosion fires only once a shortfall has
# persisted GRACE_TURNS full turns — a marshal must not begin souring two
# turns after a victory.
GRACE_TURNS = 2

# AI grant rung (GR5): the enemy AI endows its most-shortfalling marshal
# once the shortfall clears this threshold (2 wins' worth of expectation).
AI_GRANT_SHORTFALL_THRESHOLD = 80


# ═══════════════════════════ DERIVED FLAVOR ═══════════════════════════════

def derive_title(region_name: str) -> str:
    """Province-derived honorific — flavor only (Golden Rule 6).

    Derived at render/grant time from the province name, so it needs no
    serialized field and no ES-8 per-region-victory greenfield.
    """
    return f"Duke of {region_name}"


# ═══════════════════════════ CORE QUERIES ═════════════════════════════════

def is_dotation_world(world) -> bool:
    """ES-7 is Europe-scoped — the legacy fixture world has no dotations."""
    return getattr(world, "sovereign_map", "legacy") == "europe"


def get_expectation(marshal) -> int:
    """Per-turn income the marshal feels owed (deterministic, GR6)."""
    return int(min(REP_STEP * int(getattr(marshal, "battles_won", 0)),
                   EXPECTATION_CAP))


def get_satisfaction(marshal, world) -> int:
    """Full effective income of the marshal's still-held estates (§0.6.7
    amendment 1 — the 0.30 skim constant is DELETED).

    State-driven: recomputed from currently-held regions, so ANY way a
    funding province leaves the nation's hands (cede, recapture, rebellion,
    vassal grab) drops satisfaction next turn with no seam-specific hook.
    """
    total = 0
    for region_name in getattr(marshal, "dotation_regions", []):
        region = world.regions.get(region_name)
        if region is not None and region.controller == marshal.nation:
            total += region.get_effective_income()
    return int(total)


def get_shortfall(marshal, world) -> int:
    return max(0, get_expectation(marshal) - get_satisfaction(marshal, world))


def is_eroding(marshal, world) -> bool:
    """True once a shortfall has persisted past the grace window — the
    cosmetic 'loyalty frayed by neglect' legibility check."""
    grace = int(getattr(marshal, "expectation_grace_turn", -1))
    if grace < 0:
        return False
    if get_shortfall(marshal, world) <= 0:
        return False
    return (world.current_turn - grace) >= GRACE_TURNS


def get_nation_dotation_map(world, nation: str) -> Dict[str, str]:
    """{region_name: marshal_name} over the nation's LIVE marshals.

    A removed marshal's estates die with him (the prune path for marshal
    removal, E5) — this map only ever sees `world.marshals`. Marshal-count
    loop, not a region scan (GR8-safe).
    """
    result: Dict[str, str] = {}
    for marshal in world.marshals.values():
        if marshal.nation != nation:
            continue
        for region_name in getattr(marshal, "dotation_regions", []):
            result[region_name] = marshal.name
    return result


# ═══════════════════════ GRANT ELIGIBILITY ════════════════════════════════

def check_estate_eligibility(world, nation: str, region_name: str
                             ) -> Tuple[bool, str]:
    """The §0.6.7 amendment-4 endow predicate: player-held, non-capital,
    non-vassal (structural — vassal soil has the vassal as controller),
    un-dotated, NON-HOMELAND (conquered) provinces only.

    Returns (eligible, reason) — reason is player-facing copy on refusal.
    """
    region = world.regions.get(region_name)
    if region is None:
        return False, f"Unknown region: {region_name}"
    if region.controller != nation:
        return False, (f"We do not hold {region_name} — an estate must "
                       f"stand on our own soil.")
    if getattr(region, "is_capital", False) or region.region_type == "capital":
        return False, (f"{region_name} is a capital — its revenues belong "
                       f"to the state, not a marshal's household.")
    homeland = set(world.nation_starting_regions.get(nation, []))
    if region_name in homeland:
        return False, (f"{region_name} is homeland soil — the Domaine "
                       f"Extraordinaire draws only on conquered provinces.")
    # Un-dotated: one estate funds one household (any nation's marshal).
    for marshal in world.marshals.values():
        if region_name in getattr(marshal, "dotation_regions", []):
            return False, (f"{region_name} already sustains Marshal "
                           f"{marshal.name}'s household.")
    return True, ""


def list_eligible_estates(world, nation: str) -> List[str]:
    """Eligible endowment provinces for a nation, richest first.

    Rides the cached get_nation_regions index (GR8) — never a full
    region scan.
    """
    dotated = get_nation_dotation_map(world, nation)
    homeland = set(world.nation_starting_regions.get(nation, []))
    eligible = []
    for region_name in world.get_nation_regions(nation):
        if region_name in homeland or region_name in dotated:
            continue
        region = world.regions[region_name]
        if getattr(region, "is_capital", False) or region.region_type == "capital":
            continue
        eligible.append(region_name)
    eligible.sort(key=lambda r: world.regions[r].get_effective_income(),
                  reverse=True)
    return eligible


def compute_investiture_fee(marshal) -> int:
    """200g creates the title (first estate); adding land to an existing
    title is free of ceremony (1 AP only)."""
    return 0 if getattr(marshal, "dotation_regions", []) else INVESTITURE_FEE
