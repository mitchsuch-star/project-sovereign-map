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

SECOND PASS (§0.6.8, user-directed July 11, 2026): the reward PORTFOLIO —
land is one instrument, not the only one. The RENTE (grant_pension) is the
treasury alternative: face counts fully toward satisfaction, the treasury
pays ceil(RENTE_PREMIUM × face)/turn. Estates stay the better rate and
APPRECIATE (effective income recovers with stability, faster under a
high-administration Steward) but are lumpy, conquest-gated, and lootable;
rentes are precise, instant, war-safe, revocable — and premium-priced,
static, titleless. Neither dominates; the flip is the decision.
"""

import math
from typing import Dict, List, Optional, Tuple

from backend.game_logic.formations import formed_display_name

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

# Grace debounce: erosion fires only once a shortfall has persisted
# GRACE_TURNS full turns — a marshal must not begin souring two turns after a
# victory.
#
# Aug 23, 2026: 2 -> 4 (user: "it happens so early in the war them wanting
# raises"). An IN-BAND retune of a blessed starting value, not a new mechanic:
# §0.6.7 row E5 blesses "grace-turn 2 (was 1)" as a starting value and its
# preamble says retunes inside the band need no new gate. Measured on the
# user's live turn-3 board, grace 2 meant erosion opened on turn 4 of 60 and
# the Fontainebleau collective petition — an END-OF-EMPIRE beat — was
# reachable on turn 4.
#
# The binding constraint is admin AP, not patience: four marshals opened
# shortfalls simultaneously against a fixed budget of 2 admin actions per turn
# (`world_state.py`, never scaled anywhere), so at grace 2 the player had to
# spend EVERY admin action of two consecutive turns on rentes — no recruiting,
# no building, no repair — at the exact moment a war opened. Grace 4 makes the
# demand affordable without touching what is owed.
#
# What this does NOT fix: the nag still opens on the first victory, because
# any positive REP_STEP opens a shortfall on win 1. That is the curve's shape,
# and reshaping it (a free-wins floor, keying to `glory` instead of the
# monotonic `battles_won` ratchet, a war-age damper) is structural and gated —
# see docs/DESIGN_REFINEMENT.md.
#
# `BASELINE_SERIES` and M1-M7 are byte-identical across this change (measured,
# both directions).
GRACE_TURNS = 4

# AI grant rung (GR5): the enemy AI endows its most-shortfalling marshal
# once the shortfall clears this threshold (2 wins' worth of expectation).
AI_GRANT_SHORTFALL_THRESHOLD = 80

# ═══════ ES-7 SECOND PASS (§0.6.8, July 11, 2026) — THE RENTE ═══════
# The Domaine Extraordinaire paid in rentes as well as land (Monte
# Napoleone annuities, chronically in arrears). The premium is the price
# of paying honor in paper — the structural reason an available estate
# usually beats a rente on rate, while the rente wins on supply, safety,
# and precision. In-band tunable.
RENTE_PREMIUM = 1.5

# AI rente rung guard (GR5): the AI only pensions a marshal when its
# treasury can carry the bill — >= RENTE_AI_TREASURY_MULT × per-turn cost,
# never below RENTE_AI_TREASURY_FLOOR.
RENTE_AI_TREASURY_MULT = 10
RENTE_AI_TREASURY_FLOOR = 400

# ═══════════ W6-8 "THE SPOILS OF WAR" BLESSED CONSTANTS (spec §10) ═════════
# Conquering the province that sustains an ENEMY marshal's estate poses a
# choice: confiscate (windfall + grudge) or respect the title (goodwill).

CONFISCATION_INCOME_MULT = 2          # windfall = 2x base income, war-damage scaled (band 1.5-3x)
CONFISCATION_RELATIONS_PENALTY = -10  # with the estate-holder's nation (band -5..-15)
CONFISCATION_CAUTIOUS_TRUST = -1      # one-time; property is sacred
RESPECT_ACCEPTANCE_BONUS = 5          # additive acceptance term, cap one per nation


def confiscation_windfall(region) -> int:
    """Gold a confiscated estate pays its captor — THE single source.

    IGR-X4: the W6-8 cut read ``get_effective_income()`` AFTER stage 1 had
    left stability at 10 (plunder) or 25 (secure), where the stability
    modifier is 0.0 — so the windfall was **exactly 0 gold on every province
    in the game**, both branches, both sides, and the player was asked to pay
    -10 relations plus a trust dock per cautious marshal for nothing. Same
    pathology IGR-E fixed for plunder one stage up, so the fix mirrors it:
    read BASE ``income_value`` (never effective income at the post-capture
    read point).

    The ``(1 - war_damage)`` term is what keeps the original design promise
    ("a plundered estate is worth confiscating less than one kept whole")
    TRUE rather than deleting it: plunder applies +0.35 war damage before
    this is computed, so plunder-then-confiscate pays ~35% less than
    secure-then-confiscate, deterministically and order-honestly.

    The blessed 2x multiplier and its 1.5-3x band stand unchanged — only the
    income BASE is re-keyed, because the blessed base was structurally zero
    and had never priced anything (the W6-8 pins passed as ``0 == 0``).
    Decision taken under the user's July 31, 2026 delegated grant; recorded
    in WAVE6_FUN_FACTOR_SPEC.md §10 and BUG_FIXES.md §IGR-E.
    """
    return int(CONFISCATION_INCOME_MULT * region.income_value
               * (1.0 - region.war_damage))


# ═══════════════════════════ DERIVED FLAVOR ═══════════════════════════════

def derive_title(region_name: str) -> str:
    """Province-derived honorific — flavor only (Golden Rule 6).

    Derived at render/grant time from the province name, so it needs no
    serialized field and no ES-8 per-region-victory greenfield.
    """
    return f"Duke of {region_name}"


def derive_estate_noun(region_name: str) -> str:
    """The ESTATE, not the man — "the Duchy of Swabia".

    `derive_title` returns a personal honorific ("Duke of Swabia"), which is
    the object of *styled*, never of *endowed with*. Three call sites were
    already reaching for this noun by hand — two `.replace("Duke of",
    "Duchy of")` patches in `capture_executor` and the help text's own
    "Endow Ney with the Duchy of Swabia" — and the CA8-9 review found a
    fourth site interpolating the honorific after the wrong preposition and
    printing "endowed with Duke of Carniola" to the player.
    """
    return f"the Duchy of {region_name}"


# ═══════════════════════════ CORE QUERIES ═════════════════════════════════

def dotation_dormant(world) -> bool:
    """PC15-D3 (gate ruling, Aug 15 2026 — the TUT-F5 pattern extended,
    not the TUT-F5 function): the School of War keeps the reward economy
    out of the classroom. TUT-F5 silenced the jealousy machine but the
    EXPECTATION machine is separate, and it has real teeth inside the
    12-turn lesson — grace opens at 2 turns and `modify_trust` then
    erodes every turn, so "Ney's grievance is 9 turns old" fired mid-
    lesson and his objection cited victories the school never taught him
    to expect rewards for. Gate the STATE, not the beats: no grace
    clock, no erosion, no rail notices, no card block. Glory and
    `battles_won` still accrue (the Generals screen stays honest — the
    claim DERIVED from the record sleeps, the record does not). GR5:
    both sides go quiet together. Same serialized discriminator as
    TUT-F2/TUT-F5. No reward beat is added to the lesson (the syllabus
    is over-full; the school's doctrine for un-taught systems is
    dormancy) — deliberately no player-facing promise, so nothing is
    deferred (GR9)."""
    return getattr(world, "scenario_name", "") == "tutorial"


def is_dotation_world(world) -> bool:
    """ES-7 is Europe-scoped — the legacy fixture world has no dotations,
    and the School of War (PC15-D3) keeps them out of the lesson."""
    return (getattr(world, "sovereign_map", "legacy") == "europe"
            and not dotation_dormant(world))


def expectation_for_wins(battles_won: int) -> int:
    """The curve itself: what N victories are felt to be worth, per turn.

    GR1. `combat_executor` needed the value for a marshal's win count BEFORE
    the battle (to say "victory RAISES his expectation") and hand-rolled
    `int(min(REP_STEP * n, EXPECTATION_CAP))` inline — a second
    implementation of the one formula the whole reward economy is priced
    off, 6,800 lines from the first. That is the divergence pattern this
    codebase keeps paying for, and it would have silently outlived any
    future retune of the curve's shape.
    """
    return int(min(REP_STEP * int(battles_won), EXPECTATION_CAP))


def get_expectation(marshal) -> int:
    """Per-turn income the marshal feels owed (deterministic, GR6).

    NP-0 (NAPOLEON_SPEC §6.1): a sovereign's expectation is 0 FOREVER —
    the Empire is his estate. Every downstream claim (shortfall, erosion,
    Unmet Marshals, Fontainebleau, war-weary, the AI grant rung) cascades
    from this single return.
    """
    if getattr(marshal, "is_sovereign", False):
        return 0
    return expectation_for_wins(getattr(marshal, "battles_won", 0))


def get_estate_income(marshal, world, ignore_disruption: bool = False) -> int:
    """Full effective income of the marshal's still-held estates (§0.6.7
    amendment 1 — the 0.30 skim constant is DELETED).

    State-driven: recomputed from currently-held regions, so ANY way a
    funding province leaves the nation's hands (cede, recapture, rebellion,
    vassal grab) drops satisfaction next turn with no seam-specific hook.

    W6-8: an occupied estate whose TITLE the occupier chose to respect still
    sustains the marshal's household — the courtesy is precisely that his
    revenues keep flowing, so no shortfall opens and no erosion begins.

    EC-W1: an estate with a hostile army STANDING on it (pre-capture) feeds
    nobody — the invader eats its revenues in place, the household collects
    nothing, and the marshal's satisfaction falls with his lands (the same
    rule calculate_turn_income applies to the nation's treasury).

    EWC-F2 (Econ Balance gate Aug 7 2026, EB-5.2): `ignore_disruption` is
    for FACE COMPUTATION only (compute_rente_face) — a one-turn hostile
    presence on the estate at grant time must not lock an oversized
    pension that double-counts after liberation. Satisfaction and every
    display keep the disruption rule (the default).
    """
    disrupted = set() if ignore_disruption else world.get_disrupted_regions()
    total = 0
    for region_name in getattr(marshal, "dotation_regions", []):
        region = world.regions.get(region_name)
        if region is None:
            continue
        if region_name in disrupted:
            continue
        if (region.controller == marshal.nation
                or is_estate_respected(world, marshal.name, region_name)):
            total += region.get_effective_income()
    return int(total)


def get_satisfaction(marshal, world) -> int:
    """Estate income + rente face (§0.6.8). A captured marshal's rente
    neither counts nor pays (W6-7 — his expectations are frozen anyway)."""
    total = get_estate_income(marshal, world)
    if not getattr(marshal, "captured_by", ""):
        total += int(getattr(marshal, "pension", 0))
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
    # Un-dotated: one estate funds one household (any nation's marshal) —
    # but only a LIVE claim blocks (§0.6.8 item 5): the claimant's nation
    # still controls the region, or the occupier respects his title. A DEAD
    # claim (province changed hands, no respect entry) is pruned eagerly at
    # grant time instead, closing the one-turn dead zone after treaty
    # transfers hand you a province still sitting on an enemy's rolls.
    claimant = find_live_estate_claimant(world, region_name)
    if claimant is not None:
        return False, (f"{region_name} already sustains Marshal "
                       f"{claimant.name}'s household.")
    return True, ""


def capture_choice_pending(world, region_name: str) -> bool:
    """True while the capture question chain (plunder/secure → W6-8
    confiscate/respect) for region_name is still open. The claim's fate is
    undecided — the player may yet choose RESPECT — so it stays LIVE until
    the answer lands (pinned by test_w6_estate_confiscation: a
    pending-choice region is not endowable).

    WO-27: public because the per-turn estate prune in
    ``WorldState._process_dotation_state`` is the FIFTH consumer of this
    rule and was the one that did not carry it — a stage-1 question
    crossing a turn boundary had its province pruned off the holder's
    rolls, which deletes the W6-8 question outright
    (``find_enemy_estate_holder`` reads ``dotation_regions``)."""
    pending = getattr(world, "pending_capture_choice", None)
    return isinstance(pending, dict) and pending.get("region") == region_name


def find_live_estate_claimant(world, region_name: str):
    """The marshal whose estate claim on region_name is LIVE — he still
    controls it through his nation, the occupier respects his title, or
    the confiscate/respect question is still pending. Returns None when no
    claim stands (including when only DEAD claims remain). Marshal-count
    loop (GR8-safe)."""
    region = world.regions.get(region_name)
    if region is None:
        return None
    for marshal in world.marshals.values():
        if region_name not in getattr(marshal, "dotation_regions", []):
            continue
        if (region.controller == marshal.nation
                or is_estate_respected(world, marshal.name, region_name)
                or capture_choice_pending(world, region_name)):
            return marshal
    return None


def strip_dead_estate_claims(world, region_name: str) -> List[str]:
    """Eagerly prune DEAD claims on region_name (the holder's nation no
    longer controls it, no respect entry stands, and no capture choice is
    pending) so a fresh grant preserves the one-estate-per-region invariant
    without waiting for the next turn's prune. Runs the same estate_lost
    event/notification path the per-turn prune uses. Returns the stripped
    holders' names."""
    region = world.regions.get(region_name)
    stripped: List[str] = []
    for marshal in world.marshals.values():
        if region_name not in getattr(marshal, "dotation_regions", []):
            continue
        if region is not None and (
                region.controller == marshal.nation
                or is_estate_respected(world, marshal.name, region_name)
                or capture_choice_pending(world, region_name)):
            continue
        marshal.dotation_regions.remove(region_name)
        log_estate_lost(world, marshal, region_name)
        stripped.append(marshal.name)
    return stripped


def log_estate_lost(world, marshal, region_name: str) -> None:
    """The single estate_lost event + player notification path — used by
    the per-turn prune (world_state._process_dotation_state) AND the eager
    grant-time strip, so both read identically to the player."""
    world.log_event({
        "type": "estate_lost",
        "marshal": marshal.name,
        "nation": marshal.nation,
        "region": region_name,
    })
    if marshal.nation == world.player_nation:
        from backend.notifications import (
            ESTATE_LOST, NotificationPriority, create_notification,
        )
        world.notifications.add(create_notification(
            notification_type=ESTATE_LOST,
            priority=NotificationPriority.HIGH,
            title=f"Marshal {marshal.name} stripped of his estate",
            message=(
                f"{region_name}, the estate that funded Marshal "
                f"{marshal.name}'s honor, has passed from our hands. "
                f"He will not forget, Sire."
            ),
            turn_created=int(world.current_turn),
            details={"marshal": marshal.name, "region": region_name},
        ))


def list_eligible_estates(world, nation: str) -> List[str]:
    """Eligible endowment provinces for a nation, richest first.

    Rides the cached get_nation_regions index (GR8) — never a full
    region scan.

    W6-8 review fix: the exclusion covers ANY nation's marshal's rolls
    (matching check_estate_eligibility's un-dotated rule) — a RESPECTED
    foreign estate on our occupied soil stays on its holder's rolls
    indefinitely, and offering it here starved the AI's grant rung (the
    refusal added grant_dotation to skip_actions) and showed the player
    a suggestion the executor always refused.

    §0.6.8 item 5: only LIVE claims exclude (mirror of
    check_estate_eligibility) — a DEAD claim on a province we just gained
    by treaty no longer hides it from the list.
    """
    dotated = set()
    for marshal in world.marshals.values():
        for claim in getattr(marshal, "dotation_regions", []):
            claim_region = world.regions.get(claim)
            if claim_region is not None and (
                    claim_region.controller == marshal.nation
                    or is_estate_respected(world, marshal.name, claim)
                    or capture_choice_pending(world, claim)):
                dotated.add(claim)
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


def estate_yield(world, region_name: str) -> int:
    """What this province would ACTUALLY pay a marshal endowed with it today.

    CA8-20. The two terms are `get_estate_income`'s own, narrowed to one
    region, so there is one source for "does an estate pay?":

      * `get_effective_income()` is **0** at stability <= 25, and BOTH capture
        branches land inside that tier (`_apply_secure` sets 25,
        `apply_plunder_effects` sets 10). So on fresh conquest every candidate
        yields nothing, whatever its base income.
      * a DISRUPTED province (EC-W1: a hostile army standing on it) feeds
        nobody — and `list_eligible_estates` has no disruption term at all, so
        a 200g disrupted province sorts FIRST and still pays zero.

    Deliberately NOT applied inside `list_eligible_estates`: that list is
    shared with three player surfaces, and endowing a fresh conquest is a
    legal, sometimes-correct player play because estates appreciate — the
    reward dialog already discloses "covers 0g of 120g" and lets him choose.
    """
    if region_name in world.get_disrupted_regions():
        return 0
    region = world.regions.get(region_name)
    return int(region.get_effective_income()) if region is not None else 0


def list_paying_estates(world, nation: str) -> List[str]:
    """`list_eligible_estates` narrowed to provinces that would pay TODAY.

    Read by the AI grant rung and by the erosion notification's honest-advice
    branch — the two callers that must not act on, or recommend, a province
    worth nothing.
    """
    return [r for r in list_eligible_estates(world, nation)
            if estate_yield(world, r) > 0]


def compute_investiture_fee(marshal) -> int:
    """200g creates the title (first estate); adding land to an existing
    title is free of ceremony (1 AP only)."""
    return 0 if getattr(marshal, "dotation_regions", []) else INVESTITURE_FEE


# ═══════════════════ THE RENTE (§0.6.8, second pass) ═══════════════════════

def get_rente_cost(face: int) -> int:
    """Treasury cost of a rente: ceil(RENTE_PREMIUM × face).

    The premium is the arrears-and-fees of paying honor in paper — the
    structural reason an available estate usually beats a rente on rate."""
    face = int(face)
    if face <= 0:
        return 0
    return int(math.ceil(RENTE_PREMIUM * face))


def compute_rente_face(marshal, world) -> int:
    """The face a fresh grant sets: expectation − estate income (never
    below 0). Granting REPLACES any existing rente with this size — one
    rente per marshal, always re-sized to close the gap at grant time, so
    'grant him a rente' after new victories is the top-up verb.

    EWC-F2 (fixed at the Aug-7 Econ Balance gate): the face reads estate
    income IGNORING transient EC-W1 disruption — a hostile army standing
    on the estate for the grant turn must not lock an oversized pension
    that double-counts once the province is liberated. Satisfaction (and
    every display) keeps the disruption rule."""
    return max(0, get_expectation(marshal)
               - get_estate_income(marshal, world, ignore_disruption=True))


def rente_grant_would_not_help(marshal, world) -> bool:
    """True when granting a rente right now would do him no good — or harm.

    Found by the UX23-A review round and reproduced by hand. The two halves of
    the reward economy read a marshal's estates differently ON PURPOSE:
    `compute_rente_face` ignores EC-W1 disruption (EWC-F2 — a hostile army
    standing on an estate for one turn must not lock an oversized pension),
    while `get_satisfaction` counts the disruption he actually feels. When an
    estate IS disrupted the two disagree by exactly its income, and three bad
    things became reachable through a single "settle it now" click:

    * **A grant that DESTROYS his rente.** Measured: Ney, expectation 300, two
      150g estates, a 100g rente; an Austrian corps marches onto one estate;
      satisfaction 250, shortfall 50. The face is `300 − 300` = **0**, so the
      button read "Re-size rente — 0g/turn" and pressing it set `pension` to 0
      — shortfall 50 → **150**, tripled, for one of the turn's two admin
      actions, on the control advertised as the remedy.
    * **A no-op that still charges.** Face lands on exactly the pension he
      already holds: success, a decree, an admin action, nothing changed.
    * **A 0g grant.** Every estate disrupted: face 0, held 0, "granted a rente
      of 0g/turn upon the treasury", grievance untouched.

    The rule that covers all three without touching the EWC-F2 asymmetry:
    **a grant must leave him better off, or at least still met.** Anything
    that lowers what he holds while he is genuinely short is not a reward.

    Read by `rente_would_change`, so the executor, the marshal card, the AI
    rung and the rail's button all inherit it from one place (GR1) — the
    enemy AI already carried half of it as a bare `face > 0`, which is the
    asymmetry that made the player's button the only one that could fire.
    """
    held = int(getattr(marshal, "pension", 0))
    face = compute_rente_face(marshal, world)
    if face > held:
        return False                      # a real, increasing payment
    # He is about to hold LESS paper (or none). That is legitimate only when
    # his land covers him without it — the §0.6.8 re-size-down case. Counted
    # with the disruption he actually feels, because that is what erodes him.
    return get_estate_income(marshal, world) + face < get_expectation(marshal)


def rente_would_change(marshal, world) -> bool:
    """True when granting/re-sizing the rente actually changes something.

    GR1, added Aug 23, 2026 after the review round found FOUR implementations
    of "is he met": the executor guard, `reward_dialog.gd`'s enabled state, the
    AI rung, and `compute_rente_face` itself. They disagreed, so the card
    offered "Re-size rente — 80g/turn" to a fully-paid marshal, the executor
    refused the click, and the AI issued a command its own executor rejected.

    Two clauses, and both are load-bearing:

    * `get_satisfaction` is the honest "is he met" test — it counts the rente
      he already holds, which `compute_rente_face` deliberately does not (the
      face is `expectation − ESTATE income`, so a marshal paid entirely by
      rente still reports a positive face). Using the face alone refused a
      marshal whose estate had been DISRUPTED out from under him: expectation
      240, rente 90, real shortfall 150, and the tray telling the player his
      loyalty was fraying while the order to fix it answered "already met".
    * ...but being met is not the end of it. A marshal met by an oversized
      rente should still be re-sized DOWN when an estate starts paying —
      expectation 240 / rente 240 / a new 150g estate means the treasury pays
      360g/turn forever for something 135g/turn now buys.
    """
    if rente_grant_would_not_help(marshal, world):
        # UX23-A review: "would it change something" is not the same question
        # as "would it help". A disrupted estate makes the face collapse below
        # the rente he already holds, and the first clause below — any live
        # shortfall — waved that straight through to a click that made him
        # WORSE. One predicate, so the card, the AI and the rail all learn it
        # at once.
        return False
    if get_satisfaction(marshal, world) < get_expectation(marshal):
        return True
    return compute_rente_face(marshal, world) != int(getattr(marshal, "pension", 0))


def build_rente_offer(marshal, world) -> Dict:
    """The reward surface's rente line: face + true treasury cost stated
    together (§0.6.8 item 6 — every option explains its instrument)."""
    face = compute_rente_face(marshal, world)
    return {"face": int(face), "cost": int(get_rente_cost(face))}


def get_nation_rente_bill(world, nation: str) -> int:
    """Per-turn treasury cost of a nation's rentes (marshal-count loop,
    GR8). A captured marshal's rente neither pays nor counts (W6-7)."""
    if not is_dotation_world(world):
        return 0
    total = 0
    for marshal in world.marshals.values():
        if marshal.nation != nation or getattr(marshal, "captured_by", ""):
            continue
        total += get_rente_cost(int(getattr(marshal, "pension", 0)))
    return int(total)


# ═══════════════ THE STEWARD (§0.6.8 item 2, second pass) ══════════════════

def get_estate_steward_map(world) -> Dict[str, int]:
    """{region_name: stability-growth delta} for estate provinces whose
    holder's administration tier moves the needle (single source =
    Marshal.get_estate_stability_bonus). Emits entries only while the
    holder's nation controls the region — respected-occupied soil never
    benefits. Built once per stability tick (marshal-count loop, GR8)."""
    if not is_dotation_world(world):
        return {}
    result: Dict[str, int] = {}
    for marshal in world.marshals.values():
        regions = getattr(marshal, "dotation_regions", [])
        if not regions:
            continue
        bonus = int(marshal.get_estate_stability_bonus())
        if bonus == 0:
            continue
        for region_name in regions:
            region = world.regions.get(region_name)
            if region is not None and region.controller == marshal.nation:
                result[region_name] = bonus
    return result


# ═══════════ FORESIGHT WARNINGS (§0.6.8 item 3, second pass) ═══════════════

def estate_cession_warning(world, region_name: str) -> str:
    """One-line warning when ceding region_name would strip one of the
    PLAYER's marshals of his estate. Empty string otherwise — AI estates
    are the AI's problem. Requires the player to actually CONTROL the
    region (a respected estate on foreign soil being returned to us is a
    gain, not a cession). Rendered verbatim at every territory-term
    authoring/confirm surface (settlement wizard, bilateral terms,
    incoming offers)."""
    if not is_dotation_world(world):
        return ""
    region = world.regions.get(region_name)
    if region is None or region.controller != world.player_nation:
        return ""
    holder = get_nation_dotation_map(world, world.player_nation).get(region_name)
    if not holder:
        return ""
    return (f"{region_name} sustains Marshal {holder}'s title — ceding it "
            f"strips his estate, and his loyalty will bleed.")


# ═══════════════ W6-8 — THE SPOILS OF WAR (estate capture) ════════════════
#
# world.respected_estates: List[{region, marshal, nation, respecter}] — the
# serialized record of titles the conqueror chose to honor. An entry is LIVE
# only while the respecter still controls the region AND the marshal still
# lists it; prune_respected_estates() drops the rest each turn. `respecter`
# is recorded (not derived) so a region changing hands OUTSIDE the capture
# pipeline (settlement cede to a third party) can never credit a nation
# that made no such choice.


def find_enemy_estate_holder(world, region_name: str, capturer_nation: str):
    """The captured province funds another nation's marshal? Marshal-count
    loop (GR8-safe); one estate per region is a check_estate_eligibility
    invariant, so first match is the only match."""
    if not is_dotation_world(world):
        return None
    for marshal in world.marshals.values():
        if (marshal.nation != capturer_nation
                and region_name in getattr(marshal, "dotation_regions", [])):
            return marshal
    return None


def is_estate_respected(world, marshal_name: str, region_name: str) -> bool:
    """LIVE respect check: entry exists AND the respecter still holds the
    region (a stale entry confers nothing even before the prune runs)."""
    region = world.regions.get(region_name)
    if region is None:
        return False
    for entry in getattr(world, "respected_estates", None) or []:
        if (entry.get("region") == region_name
                and entry.get("marshal") == marshal_name
                and region.controller == entry.get("respecter")):
            return True
    return False


def _drop_respected_entries(world, region_name: str) -> None:
    entries = getattr(world, "respected_estates", None) or []
    world.respected_estates = [
        e for e in entries if e.get("region") != region_name
    ]


def prune_respected_estates(world) -> None:
    """Drop dead respect entries: region/marshal gone, estate no longer on
    the marshal's rolls (confiscated elsewhere), the respecter lost the
    region, or the estate returned to its own nation's hands."""
    entries = getattr(world, "respected_estates", None) or []
    if not entries:
        return
    live = []
    for entry in entries:
        region = world.regions.get(entry.get("region"))
        holder = world.marshals.get(entry.get("marshal"))
        if region is None or holder is None:
            continue
        if entry.get("region") not in getattr(holder, "dotation_regions", []):
            continue
        if region.controller != entry.get("respecter"):
            continue
        live.append(entry)
    world.respected_estates = live


def apply_estate_confiscation(world, region, holder, capturer_nation: str,
                              windfall: Optional[int] = None) -> Dict:
    """Strip the estate for a windfall. The holder's satisfaction drops and
    the EXISTING erosion machinery does the rest — no new erosion code.
    Symmetric (GR5): the AI confiscating a player marshal's estate runs this
    exact function.

    windfall: the player pipeline passes the number the popup SHOWED so the
    charge always equals the promise; the AI path computes it here — through
    the SAME single source the popup prices with (IGR-X4)."""
    if windfall is None:
        windfall = confiscation_windfall(region)
    windfall = int(windfall)
    world.nation_gold[capturer_nation] = (
        world.nation_gold.get(capturer_nation, 0) + windfall)
    if region.name in getattr(holder, "dotation_regions", []):
        holder.dotation_regions.remove(region.name)
    _drop_respected_entries(world, region.name)
    world.modify_nation_relation(
        capturer_nation, holder.nation, CONFISCATION_RELATIONS_PENALTY)
    # Property is sacred: the CAPTURER's own cautious marshals disapprove
    # (one-time, capped at 1 point each).
    disapproving = []
    for marshal in world.marshals.values():
        if (marshal.nation == capturer_nation
                and marshal.personality == "cautious"):
            marshal.modify_trust(CONFISCATION_CAUTIOUS_TRUST)
            disapproving.append(marshal.name)
    world.log_event({
        "type": "estate_confiscated",
        "region": region.name,
        "marshal": holder.name,
        "nation": holder.nation,
        "confiscated_by": capturer_nation,
        "windfall": int(windfall),
        "turn": int(world.current_turn),
    })
    # The victim's court learns at once (the prune's estate_lost notification
    # never fires — the region is already off his rolls).
    if holder.nation == world.player_nation:
        from backend.notifications import (
            ESTATE_CONFISCATED, NotificationPriority, create_notification,
        )
        world.notifications.add(create_notification(
            notification_type=ESTATE_CONFISCATED,
            priority=NotificationPriority.HIGH,
            title=f"Marshal {holder.name}'s estate confiscated",
            message=(
                # CA8 sweep 4: a raw nation tag in a player-facing
                # notification — "KingdomOfItaly has seized ..." — while
                # the dispatch narrating the SAME confiscation uses the
                # R7 chokepoint.
                f"{formed_display_name(world, capturer_nation)} has "
                f"seized {region.name}, the estate "
                f"that funded Marshal {holder.name}'s honor. He will not "
                f"forget it, Sire."
            ),
            turn_created=int(world.current_turn),
            details={"marshal": holder.name, "region": region.name,
                     "confiscated_by": capturer_nation},
        ))
    return {"choice": "confiscate", "windfall": int(windfall),
            "holder": holder.name, "holder_nation": holder.nation,
            "disapproving": disapproving}


def apply_estate_respect(world, region, holder, capturer_nation: str) -> Dict:
    """Honor the title: the estate stays on the marshal's rolls (the prune
    skips it, his satisfaction keeps counting it) and the holder's nation
    remembers the courtesy as a +5 acceptance term (cap one per nation)."""
    _drop_respected_entries(world, region.name)
    entries = getattr(world, "respected_estates", None) or []
    entries.append({
        "region": region.name,
        "marshal": holder.name,
        "nation": holder.nation,
        "respecter": capturer_nation,
    })
    world.respected_estates = entries
    world.log_event({
        "type": "estate_respected",
        "region": region.name,
        "marshal": holder.name,
        "nation": holder.nation,
        "respected_by": capturer_nation,
        "turn": int(world.current_turn),
    })
    return {"choice": "respect", "holder": holder.name,
            "holder_nation": holder.nation,
            "title": derive_title(region.name)}


def apply_ai_estate_rule(world, region, capturer_nation: str) -> Optional[Dict]:
    """GR5 — the AI conqueror decides without a popup: confiscate when at
    war with the estate-holder's nation, respect otherwise. Returns the
    applied result dict, or None when the region funds no enemy estate."""
    holder = find_enemy_estate_holder(world, region.name, capturer_nation)
    if holder is None:
        return None
    if world.is_at_war(capturer_nation, holder.nation):
        return apply_estate_confiscation(world, region, holder, capturer_nation)
    return apply_estate_respect(world, region, holder, capturer_nation)


def respected_estate_mod(world, proposer: str, target: str) -> int:
    """The single additive acceptance term (settlement-memories pattern):
    +5 when the proposer honors at least one of the target nation's
    marshals' titles on occupied soil — capped at one bonus per nation."""
    for entry in getattr(world, "respected_estates", None) or []:
        if (entry.get("respecter") == proposer
                and entry.get("nation") == target
                and is_estate_respected(
                    world, entry.get("marshal"), entry.get("region"))):
            return int(RESPECT_ACCEPTANCE_BONUS)
    return 0


# ══════════════════════════════════════════════════════════════════════
# THE REWARD RAIL — one implementation of "what the tray currently says"
#
# Aug 23, 2026 (user: "when you pay them it doesn't dismiss their popup of
# wanting"). These producers used to be closures and inline blocks inside
# `WorldState.process_dotation_state`, which runs ONCE PER TURN. So the rail
# was reconciled only at a turn boundary: paying a marshal mid-turn left
# "Marshal Ney expects reward … holds 0g" standing beside the grant
# confirmation that had just told the player his expectation was met, until
# the turn ended.
#
# They live here now so the per-turn pass AND the grant/revoke executors
# share ONE implementation. The tray's own docstring calls itself "a list of
# things still true"; the moment satisfaction changes, that list has to
# change with it.
# ══════════════════════════════════════════════════════════════════════

def dismiss_reward_notices(world, marshal) -> None:
    """Retire BOTH reward-rail notices for one marshal.

    CA9-N3: the two branches that end erosion — expectation MET, and the
    W6-7 capture freeze — each left the HIGH `DOTATION_EROSION` row standing
    while retiring only the NORMAL one. Measured: a marshal paid in full
    still read "his victories remain unrewarded … holds 0g/turn" eighteen
    turns later.

    Filtered per marshal: an unfiltered dismiss would clear everyone else's
    live grievance, which is the laziest wrong fix and is pinned against.
    """
    if marshal.nation != world.player_nation:
        return
    from backend.notifications import DOTATION_EROSION, DOTATION_EXPECTATION

    def _mine(n, mn=marshal.name):
        return n.get("details", {}).get("marshal") == mn

    world.notifications.dismiss_by_type(DOTATION_EXPECTATION, filter_fn=_mine)
    world.notifications.dismiss_by_type(DOTATION_EROSION, filter_fn=_mine)


def _has_standing_reward_notice(world, marshal) -> bool:
    from backend.notifications import DOTATION_EROSION, DOTATION_EXPECTATION
    family = (DOTATION_EXPECTATION, DOTATION_EROSION)
    return any(n.get("type") in family
               and n.get("details", {}).get("marshal") == marshal.name
               for n in world.notifications.get_pending())


def restate_reward_notice(world, marshal) -> None:
    """Bring a STANDING reward row back into line with live numbers, or
    retire it once the debt is settled.

    UX23-A. The rail was reconciled only by the once-per-turn
    `_process_dotation_state`, so a row's figures could go stale WITHIN a
    turn. That mattered little while they were prose. It matters a great deal
    now the same figure sits on a button that spends an administrative
    action. Measured before this existed: Ney at 2 wins shows "Grant rente —
    120g/turn"; he wins a battle; the row does not move; the click grants a
    face of 120 and the treasury pays **180**. A 50% understatement on the
    control the player pressed — the CA9 through-line exactly.

    Two rules:

    * It never OPENS a row. Opening one starts the grace clock, and the grace
      clock belongs to the per-turn pass — a mid-turn victory must not shorten
      a marshal's patience. A marshal with no standing row is left alone.
    * Retiring uses the same `shortfall <= 0` gate the payment seams already
      had, so this is a SUPERSET of the old dismiss-if-settled call rather
      than a second rule standing beside it (GR1).

    Safe to call mid-turn only because UX23-R2 landed first: the producers
    refresh in place and keep the row's uuid, so re-stating no longer mints a
    new id — and the client's desk bell, which dedupes on that id, no longer
    rings at the moment of payment.
    """
    if not is_dotation_world(world):
        return
    # No player-nation guard here on purpose. All three things this can reach
    # — `dismiss_reward_notices`, `post_expectation_notice`,
    # `post_erosion_notice` — already own that rule and return early for a
    # foreign marshal. A fourth copy here was written, found INERT by the
    # mutation sweep (it could be deleted with the whole suite green), and
    # removed rather than given a test that proves nothing. The rule is
    # pinned where it actually lives.
    expectation = get_expectation(marshal)
    satisfaction = get_satisfaction(marshal, world)
    shortfall = max(0, expectation - satisfaction)
    if shortfall <= 0:
        dismiss_reward_notices(world, marshal)
        return
    if not _has_standing_reward_notice(world, marshal):
        return
    grace_start = int(getattr(marshal, "expectation_grace_turn", -1))
    if grace_start < 0:
        return
    elapsed = int(world.current_turn) - grace_start
    if elapsed < GRACE_TURNS:
        post_expectation_notice(world, marshal, expectation, satisfaction,
                                shortfall, GRACE_TURNS - elapsed)
    else:
        post_erosion_notice(world, marshal, expectation, satisfaction,
                            shortfall)


def rente_action_keys(marshal, world) -> Dict:
    """The one-click rente affordance a reward-rail row carries, or `{}`.

    UX23-A (Aug 23, 2026; user: "no way to do it without menuing" → "reward a
    general from the notification itself"). The rail's detail panel could only
    ever point somewhere else; these three display-only keys turn the row into
    the place the thing is DONE. The client renders `action_label` as a button
    and sends `action_command` down the ordinary typed-command pipeline, so
    the executor, its refusals, the AP charge and the campaign log are
    untouched (GR6 — nothing here decides anything).

    Three rules the row must not break:

    * **Shown = applied.** The figure is `get_rente_cost(compute_rente_face())`
      — the exact pair `_execute_grant_pension` prices the grant with, and the
      same pair the row's own message quotes.
    * **Never offer what the executor refuses.** Gated on `rente_would_change`,
      the GR1 predicate the executor, the marshal card and the AI rung all
      read. (A row only exists on a live shortfall, so this is true in
      practice — reading the predicate is what keeps it true under retune.)
    * **No baked `enabled` flag.** `_process_dotation_state` runs at
      `world_state.py:9470` and admin AP is refilled at `:9522`, AFTER it — so
      a gate evaluated here would ship permanently disabled, which is exactly
      the IGR-2 P1 that made every AP-priced marshal-petition arm unusable.
      The button stays live and the executor refuses honestly at zero cost.

    The ESTATE arm deliberately gets no one-click button: `estate_yield`'s own
    docstring records that endowing a fresh 0g conquest "is a legal,
    sometimes-correct player play because estates appreciate", so the province
    is a choice the §0.6.8 portfolio design exists to pose. `[Reward…]` still
    opens the dialog that poses it.
    """
    # UX23-A review round: the docstring promised "never offer what the
    # executor refuses" while mirroring only two of its five refusals.
    # Measured on the live boot, the builder returned a complete, priced
    # affordance for NAPOLEON (whom `_execute_grant_pension` refuses in
    # character — "the treasury is already his") and for MACK, an Austrian,
    # quoted against the FRENCH treasury. Both are latent, because the two
    # producers return early for a foreign marshal — but a claim that is only
    # true because of a guard somewhere else is not a claim this function can
    # keep, and this is the one builder a future surface will reuse.
    if marshal.nation != getattr(world, "player_nation", None):
        return {}
    if getattr(marshal, "is_sovereign", False):
        return {}
    if getattr(marshal, "captured_by", ""):
        return {}
    if not rente_would_change(marshal, world):
        return {}
    face = compute_rente_face(marshal, world)
    cost = get_rente_cost(face)
    held = int(getattr(marshal, "pension", 0))
    verb = "Re-size rente" if held > 0 else "Grant rente"
    return {
        "action_command": f"grant {marshal.name} a rente",
        "action_label": f"{verb} — {cost}g/turn",
        # UX23-A review round: two clauses were false in reachable states.
        # "every turn" — `get_nation_rente_bill` skips a captured marshal, so
        # the crown pays only while he is at liberty. "Reversible" implied a
        # free undo; `revoke_pension` is itself an ADMIN action.
        "action_detail": (
            f"{face}g/turn to his household; {cost}g/turn from the treasury "
            f"for as long as he is at liberty, and 1 administrative action "
            f"now. Revocable with \"revoke {marshal.name}'s rente\" — for "
            f"another administrative action."
        ),
    }


def post_expectation_notice(world, marshal, expectation, satisfaction,
                            shortfall, remaining_grace) -> None:
    """The NORMAL "expects reward" row, re-stated with live numbers.

    S5-3: it was created once at shortfall-open with static numbers and a
    frozen grace line, so it drifted from the same-response dispatch (rail
    "80g/turn … holds 2 turns" vs dispatch "160g/turn … fraying").

    UX23-R2 (Aug 23, 2026): it now REFRESHES in place. The old dismiss-by-type
    + re-add dodged `add`'s "(x2)" repeat marker but threw the row's uuid away
    with it, and `notification_bar.gd` dedupes the desk bell on that uuid — so
    a standing grievance rang the bell once a turn, per marshal, forever.
    `NotificationCollector.refresh` is the same identity match without the
    repeat marker, so the id survives and the bell rings once per grievance.
    Player-only.
    """
    if marshal.nation != world.player_nation:
        return
    from backend.notifications import (
        DOTATION_EXPECTATION, NotificationPriority, create_notification,
    )
    if remaining_grace <= 1:
        patience = "His patience holds one more turn"
    else:
        patience = f"His patience holds {remaining_grace} turns"
    # Shown = applied: quoted off the SAME two functions the executor prices
    # the grant with, so the figure on the rail is the figure the treasury
    # pays if the player acts on it.
    rente_cost = get_rente_cost(compute_rente_face(marshal, world))
    # Honest availability, the same rule the erosion notice has carried since
    # §0.6.8 item 4d — applied here too, because THIS is the first thing the
    # player is ever told about the reward economy. France holds ZERO
    # conquered provinces at the 1805 boot, so the old copy's "endow an estate
    # (a Duchy)" named an instrument that did not exist, on turn 2, as the
    # system's opening line. Only offer the land when land is actually paying.
    # No "press G" on either arm. The row now carries a [Reward…] button
    # that opens his card directly (review round: the clause survived exactly
    # where the deep link is most useful, and it disagreed with the dialog,
    # which builds its estate options from `eligible_estate_details` rather
    # than from paying ones).
    estate_clause = ""
    if list_paying_estates(world, marshal.nation):
        estate_clause = ", or endow him with an estate"
    world.notifications.refresh(create_notification(
        notification_type=DOTATION_EXPECTATION,
        priority=NotificationPriority.NORMAL,
        title=f"Marshal {marshal.name} expects reward",
        message=(
            # Aug 23, 2026 (user: "there's no way to do it without
            # menuing"): the row used to end "open the Generals screen
            # (press G) and use [ Reward… ] on his card" — an instruction to
            # go somewhere else, on a rail the player is already looking at.
            # It now leads with the one-line typed order that settles it
            # where they stand. `pension <name>` is a live golden-corpus
            # utterance (es7sp-pension-davout), and the rente's face is
            # auto-sized to the gap, so the short form is the whole action.
            f"Marshal {marshal.name} looks for {expectation}g/turn and holds "
            f"{satisfaction}g. {patience} — settle it now with "
            f"\"pension {marshal.name}\" (a rente, {rente_cost}g/turn)"
            f"{estate_clause}."
        ),
        turn_created=int(world.current_turn),
        details={"marshal": marshal.name,
                 "expectation": int(expectation),
                 "satisfaction": int(satisfaction),
                 "shortfall": int(shortfall),
                 "grace_turns": int(GRACE_TURNS),
                 "remaining_grace": int(max(0, remaining_grace)),
                 # The rail row becomes a way IN, not just a sign-post. The
                 # client already forwards `route_id` through
                 # `notification_review_requested`; this is the arm that
                 # opens the reward dialog on the named marshal.
                 "review_target": "marshal_reward",
                 "review_label": "Reward…",
                 "route_id": marshal.name,
                 # UX23-A: and the row is where it gets DONE, not only where
                 # it is announced. `[Reward…]` still opens the portfolio for
                 # the estate half.
                 **rente_action_keys(marshal, world)},
    ))


def reward_remedy_phrase(world, nation: str) -> str:
    """§0.6.8 item 4d: honest advice — never tell the player to endow when
    no eligible province exists.

    CA8-20: "eligible" is not "useful" — a province that yields 0g stops no
    erosion, so recommending it was the same lie in a longer sentence. But
    NARROWING the predicate alone made the else-branch false in turn: it
    says no conquered province REMAINS while the marshal's own card is
    offering four by name. Three arms, so each sentence is true of the state
    that reaches it. The middle one covers BOTH of `estate_yield`'s terms —
    a raw conquest that has not settled AND an EC-W1 province with a hostile
    army standing on it — so it must not promise that waiting is enough: a
    disrupted province does not settle, it drains.
    """
    if list_paying_estates(world, nation):
        return ("endow him with an estate or grant him a rente to stop the "
                "erosion.")
    if list_eligible_estates(world, nation):
        return ("the provinces we hold yield him nothing yet — endow one "
                "against its recovery, or grant a rente for gold now.")
    return ("no conquered province remains to endow — grant a rente, or let "
            "victory furnish an estate.")


def post_erosion_notice(world, marshal, expectation, satisfaction,
                        shortfall) -> None:
    """The HIGH "grows bitter" row, re-stated with live numbers.

    CA9-N3: this was posted ONCE, at the instant erosion began, and its
    figures froze there — so a marshal now drawing a 240g rente against a
    300g expectation still read "holds 0g/turn", contradicted by the same
    screen's `"pension": 240`. It is REPLACED on every eroding turn, and on
    any mid-turn change to his satisfaction, so its numbers are the numbers.
    """
    if marshal.nation != world.player_nation:
        return
    from backend.notifications import (
        DOTATION_EROSION, NotificationPriority, create_notification,
    )
    remedy = reward_remedy_phrase(world, marshal.nation)
    # UX23-R2: refreshed in place — see `post_expectation_notice`. This row is
    # HIGH and stands for as long as the neglect does, so it was the loudest
    # instance of the per-turn bell.
    world.notifications.refresh(create_notification(
        notification_type=DOTATION_EROSION,
        priority=NotificationPriority.HIGH,
        title=f"Marshal {marshal.name} grows bitter",
        message=(
            f"Marshal {marshal.name}'s victories remain unrewarded "
            f"(expects {expectation}g/turn of estates; holds "
            f"{satisfaction}g/turn). His loyalty is fraying — {remedy}"
        ),
        turn_created=int(world.current_turn),
        details={"marshal": marshal.name,
                 "expectation": int(expectation),
                 "satisfaction": int(satisfaction),
                 "shortfall": int(shortfall),
                 "review_target": "marshal_reward",
                 "review_label": "Reward…",
                 "route_id": marshal.name,
                 **rente_action_keys(marshal, world)},
    ))
