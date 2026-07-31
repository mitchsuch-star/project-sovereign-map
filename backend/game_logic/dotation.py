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


# ═══════════════════════════ CORE QUERIES ═════════════════════════════════

def is_dotation_world(world) -> bool:
    """ES-7 is Europe-scoped — the legacy fixture world has no dotations."""
    return getattr(world, "sovereign_map", "legacy") == "europe"


def get_expectation(marshal) -> int:
    """Per-turn income the marshal feels owed (deterministic, GR6)."""
    return int(min(REP_STEP * int(getattr(marshal, "battles_won", 0)),
                   EXPECTATION_CAP))


def get_estate_income(marshal, world) -> int:
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
    """
    disrupted = world.get_disrupted_regions()
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


def _capture_choice_pending(world, region_name: str) -> bool:
    """True while the capture question chain (plunder/secure → W6-8
    confiscate/respect) for region_name is still open. The claim's fate is
    undecided — the player may yet choose RESPECT — so it stays LIVE until
    the answer lands (pinned by test_w6_estate_confiscation: a
    pending-choice region is not endowable)."""
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
                or _capture_choice_pending(world, region_name)):
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
                or _capture_choice_pending(world, region_name)):
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
                    or _capture_choice_pending(world, claim)):
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
    'grant him a rente' after new victories is the top-up verb."""
    return max(0, get_expectation(marshal) - get_estate_income(marshal, world))


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
                f"{capturer_nation} has seized {region.name}, the estate "
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
