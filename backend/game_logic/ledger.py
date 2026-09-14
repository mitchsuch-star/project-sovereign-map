"""
Strategic Ledger — 6-section backend builder (Session B + Orders tab)

Builds a structured dict for the Godot Strategic Ledger screen.
All values int()-wrapped per CLAUDE.md rule: "All numbers to Godot: int()".

Fog-filtered: intel section uses RegionIntel visibility, never raw marshal data.
"""

import math
from typing import Dict, Any

from backend.models.intel import (
    FULL, PARTIAL, STALE, UNKNOWN,
    get_strength_band,
)
from backend.game_logic.dispatch import BAND_MIDPOINTS
from backend.models.world_state import (
    MAX_INFANTRY_POOL, MAX_CAVALRY_POOL, MAX_ARTILLERY_POOL,
    INFANTRY_RECRUIT_AMOUNT, CAVALRY_RECRUIT_AMOUNT, ARTILLERY_RECRUIT_AMOUNT,
    INFANTRY_RECRUIT_GOLD_COST_BASE, CAVALRY_RECRUIT_GOLD_COST_BASE,
    ARTILLERY_RECRUIT_GOLD_COST_BASE,
)


def build_strategic_ledger(world) -> Dict[str, Any]:
    """
    Build the strategic ledger dict for Godot rendering.

    Args:
        world: WorldState instance

    Returns:
        Dict with forces, territories, economy, intel, manpower, orders sections.
        All numeric values int()-wrapped.
    """
    player = world.player_nation

    # Authority — global player stat (V2b)
    authority = int(world.authority_tracker.authority) if hasattr(world, 'authority_tracker') else 100
    if authority >= 80:
        authority_label = "Strong"
    elif authority >= 50:
        authority_label = "Normal"
    else:
        authority_label = "Weak"

    # DEF-5 naval §9 — THE ADMIRALTY block (rendered inside the economy
    # tab; {"active": False} on fleet-less worlds and the .gd arm skips).
    from backend.game_logic.naval import build_admiralty_report
    admiralty_report = build_admiralty_report(world)

    # IQ-2: the standing fact of a collapsed realm, from the one source every
    # surface reads (`collapse.get_collapse_state`), and the scope note spoken
    # beside it — the ledger states the collapse, it never ends anything.
    # Sandbox worlds only (the legacy payload stays byte-identical); "" when
    # the realm stands.
    from backend.game_logic import collapse as _collapse
    collapse_fields = {}
    if _collapse.THE_COLLAPSE_IS_LEGIBLE and getattr(world, "sandbox_mode", False):
        _state = _collapse.get_collapse_state(world)
        collapse_fields["collapse_note"] = (
            f"{_collapse.summary_line(world, _state)} {_collapse.CAMPAIGN_CONTINUES}"
            if _state else "")

    return {
        **collapse_fields,
        "forces": _build_forces(world, player),
        "territories": _build_territories(world, player),
        "economy": _build_economy(world, player),
        "intel": _build_intel(world, player),
        "manpower": _build_manpower(world, player),
        "orders": _build_orders(world, player),
        "admiralty": admiralty_report,
        # HC-0: dated header for the ledger screen ("" without an anchor).
        "calendar_label": world.get_calendar_label(),
        "authority": int(authority),
        "authority_label": authority_label,
        "actions_remaining": int(world.actions_remaining),
        # AI-0b: the campaign seed, shown and shareable — a good opening can
        # be replayed or reported against (docs/AI_INTENT_SPEC.md §3.8.1).
        "campaign_seed": str(getattr(world, "campaign_seed", "historical")),
    }


# ============================================================================
# FORCES SECTION
# ============================================================================

# FA-32 (slice 11) flip lever: False restores the ledger's silence about a
# prisoner (an `idle` corps standing in the captor's capital at strength 0).
THE_LEDGER_KNOWS_ITS_PRISONERS = True
# FA-N36 (slice 17): a marshal frozen by an unanswered interrupt is
# `awaiting_decision` on the FORCES tab, his order summary says HALTED, and
# the ORDERS row stops claiming progress — the same lie the dispatch was
# fixed for on July 19. One word shared with `dispatch._derive_marshal_status`;
# `strategic_ledger.gd` already renders it ("Awaiting decision") unchanged.
THE_LEDGER_SEES_THE_HALT = True
# FA-N65 (slice 17): the ORDERS tab lists no prisoner. FA-32 fixed the FORCES
# half ("Held by Austria at Vienna"); the ORDERS half still appended him to
# `idle_marshals` as "Ney at Vienna │ No active orders" — the client's
# literal at strategic_ledger.gd:945, so no payload word could fix it. He is
# on FORCES and in the dispatch's PRISONERS OF WAR block; here he is absent.
THE_ORDERS_TAB_KNOWS_ITS_PRISONERS = True


def _is_halted(marshal) -> bool:
    """FA-N36. Slice 17 review round (L1-5): a standalone DECISION, or an
    order-BOUND interrupt whose order still stands. A stale interrupt with
    no order (the TUT-F4a class, reachable from a pre-slice save) is not a
    halt — the dispatch reads "Awaiting orders." for it and both surfaces
    must say the same word."""
    if not THE_LEDGER_SEES_THE_HALT:
        return False
    from backend.commands.strategic import standalone_decision
    if standalone_decision(marshal):
        return True
    return bool(getattr(marshal, "pending_interrupt", None)
                and getattr(marshal, "strategic_order", None))


def _derive_status(marshal) -> str:
    """Derive marshal status from priority chain (highest wins)."""
    if THE_LEDGER_KNOWS_ITS_PRISONERS and getattr(marshal, "captured_by", ""):
        # FA-32: the Strategic Ledger is the surface a player OPENS, and it
        # was the surface that lied. A captured marshal was listed on the
        # FORCES tab as an `idle` corps at `Vienna` with strength 0 and "No
        # active orders" — no captivity marker anywhere, in the backend or in
        # `strategic_ledger.gd`. Captivity outranks every other status: a man
        # in irons is not idle, not holding, not fortified.
        return "captured"
    if _is_halted(marshal):
        # FA-N36: the pending decision outranks the order it suspends.
        return "awaiting_decision"
    if marshal.broken:
        return "broken"
    if marshal.retreating:
        return "retreating"
    if marshal.drilling or marshal.drilling_locked:
        return "drilling"
    if marshal.fortified:
        return "fortified"
    if marshal.in_strategic_mode:
        cmd = marshal.strategic_order.command_type
        if cmd == "HOLD":
            return "holding"
        if cmd == "PURSUE":
            return "pursuing"
        if cmd == "MOVE_TO":
            return "moving_to"
        if cmd == "SUPPORT":
            return "supporting"
    return "idle"


def _derive_strategic_order_summary(marshal) -> str:
    """Format strategic order summary string (player-facing verbs, R7)."""
    from backend.display_names import get_strategic_display

    order = marshal.strategic_order
    if order is None:
        return "None"
    cmd = order.command_type
    target = order.target
    if _is_halted(marshal):
        # FA-N36: no turns-left count for a man who is not moving.
        return f"{get_strategic_display(cmd)} {target} — HALTED, awaiting your word"
    if cmd == "MOVE_TO":
        turns_left = len(order.path)
        return f"{get_strategic_display(cmd)} {target} ({turns_left} turns left)"
    if cmd == "PURSUE":
        return f"{get_strategic_display(cmd)} {target} (tracking)"
    if cmd == "SUPPORT":
        return f"{get_strategic_display(cmd)} {target} (active)"
    if cmd == "HOLD":
        return f"{get_strategic_display(cmd)} at {target}"
    return f"{get_strategic_display(cmd)} {target}"


def _derive_unit_type(marshal) -> str:
    """Derive unit type string."""
    if getattr(marshal, 'artillery', False):
        return "artillery"
    if getattr(marshal, 'cavalry', False):
        return "cavalry"
    return "infantry"


def _build_forces(world, player: str) -> list:
    """Build forces section: per player marshal."""
    forces = []
    for marshal in world.marshals.values():
        if marshal.nation != player:
            continue
        forces.append({
            "name": marshal.name,
            "type": _derive_unit_type(marshal),
            "personality": marshal.personality,
            "location": marshal.location,
            "strength": int(marshal.strength),
            "morale": int(marshal.morale),
            "trust": int(marshal.trust.value),
            "stance": marshal.stance.value,
            "status": _derive_status(marshal),
            "strategic_order": _derive_strategic_order_summary(marshal),
            "battles_won": int(marshal.battles_won),
            "battles_lost": int(marshal.battles_lost),
            "special_flags": {
                "shock_ready": marshal.shock_bonus > 0,
                "counter_punch": marshal.counter_punch_available,
                "reckless": int(marshal.recklessness) if getattr(marshal, 'cavalry', False) else 0,
                "exhausted": marshal._get_exhaustion_penalty() > 0,
            },
            # FA-32: so the FORCES tab can say where he is and whose guest.
            "captured": bool(getattr(marshal, "captured_by", "")),
            "captured_by": str(getattr(marshal, "captured_by", "") or ""),
        })
    return forces


# ============================================================================
# TERRITORIES SECTION
# ============================================================================

def _build_territories(world, player: str) -> list:
    """Build territories section: per player-controlled region."""
    territories = []
    # WO slice 8: one naval shore-verdict memo for the whole pass (GR8).
    _shore_cache: dict = {}
    for region in world.regions.values():
        if region.controller != player:
            continue

        # Buildings
        buildings = []
        for b in region.buildings:
            status = "damaged" if b.get("damaged", False) else "built"
            buildings.append({"name": b["type"], "status": status})
        if region.building_under_construction:
            buc = region.building_under_construction
            buildings.append({
                "name": buc["type"],
                "status": f"constructing ({buc['turns_remaining']}t)",
            })

        # Supply status
        total_occupant_strength = sum(
            m.strength for m in world.marshals.values()
            if m.location == region.name
        )
        # WO slice 8 (§2 C-7): verdict AND figure read the player's
        # EFFECTIVE cap — the threshold the attrition engine bills at.
        # The raw property fired "Over capacity" inside the 1.5× home
        # band where the engine charges nothing (the PT-D5 false alarm),
        # and printed a figure a third below the bill on every own-soil
        # row.
        effective_cap = world.get_effective_supply_cap(
            player, region, _shore_cache=_shore_cache)
        # Slice-8 review [C-F2]: the verdict reads the SAME rate function
        # the engine bills with, so the death-ball arm shows too — three
        # corps under the cap read "Crowded" (2%+/turn), not "OK", on the
        # tab beside the muster preview that quotes that exact cost.
        living_occupants = sum(
            1 for m in world.marshals.values()
            if m.location == region.name and m.strength > 0)
        attrition_rate = world.supply_attrition_rate(
            int(total_occupant_strength), int(effective_cap),
            living_occupants)
        supply_status = "OK"
        if total_occupant_strength > effective_cap:
            supply_status = "Over capacity"
        elif attrition_rate > 0:
            supply_status = "Crowded"

        # Occupant count
        occupant_count = sum(
            1 for m in world.marshals.values()
            if m.location == region.name
        )

        territories.append({
            "name": region.name,
            "terrain": region.terrain,
            "region_type": region.region_type,
            "buildings": buildings,
            "garrison": int(region.garrison_strength),
            "supply_capacity": int(effective_cap),
            "occupant_count": int(occupant_count),
            "supply_status": supply_status,
            "stability": int(region.stability),
            "war_damage": int(region.war_damage * 100),
            "income": int(region.get_effective_income()),
        })
    return territories


# ============================================================================
# ECONOMY SECTION
# ============================================================================

def _levy_block(world, nation: str = None) -> dict:
    """Lazy door onto the single source (see `economy_executor.get_levy_status`).

    IQ1-2 review round: the `nation` argument did not exist, and
    `get_levy_status` defaults to `world.player_nation` — so this was the
    THIRD player-scoped read inside `_build_economy`, and IQ1-2's first cut
    fixed two of the three. That left the payload contradicting itself:
    `_build_economy(world, "Austria")` returned Austria's treasury beside
    FRANCE's force limit, army total and infantry pool. Two independent
    reviewers found it. The lesson is this repo's own, for the sixth time:
    a fix that touches one reader of a pipeline must be checked against
    every other reader in the same function.
    """
    from backend.commands.economy_executor import get_levy_status
    return get_levy_status(world, nation)


# IQ-2 (Sept 14, 2026): the MANPOWER tab priced every arm "at the capital"
# while the capital was enemy-held — measured with Austria in Paris, "Live
# price at the capital" beside a figure `_execute_recruit` refuses. The note
# now asks the executor's own depot gate (`recruit_location_gate`) and names
# the closed depot. Flip lever: False = the pre-IQ-2 note on every board.
THE_MANPOWER_TAB_READS_THE_DEPOT = True

# FA-D26 (slice 17, Phase 2) flip lever: the economy tab carries the Materiel
# bill as an informational line (charged at the battle, not in Net). False =
# no row (the prior ledger).
THE_LEDGER_SHOWS_THE_MATERIEL_BILL = True

# IQ-1 SW-0 "The Chest Speaks" flip lever: the economy tab states what the
# turn has SPENT and where the treasury is headed under the charges now in
# force. False = neither line, and a byte-identical payload.
#
# Why this exists: `gold_spent_this_turn` has been serialized since Phase 6
# and rendered on no screen in the game, and the treasury's own fixed point
# — the single most decision-relevant number in the economy — is recomputed
# every turn inside `get_state_charges_rate` and shown to nobody. Measured
# September 12, 2026: a commanded France reaches 88,556g by turn 40 having
# spent 2.5% of 199,101g gross, because the two admin actions a turn can
# only reach ~1,308g of purchases against a boot net of 1,842g.
THE_CHEST_STATES_ITS_CEILING = True

# IQ-1 IQ1-2 "The Chest Tells the Truth" flip lever. False restores every
# pre-slice reading: the POST-charge ceiling argument, the player-scoped
# `treasury` / `bankruptcy_turns` keys, and the single `ceiling == 0`
# sentinel. The rest of the payload is byte-identical either way.
#
# Three defects, all display, all measured on ONE unchanged 1805 boot world:
#
# 1. THE CEILING WAS NOT A FIXED POINT. `_build_economy` fed
#    `state_charges_ceiling` the net that had ALREADY had `state_charges`
#    subtracted, so a figure defined to be independent of the chest slid
#    with it. At rate 80, varying only the treasury:
#        800 -> 59,562 · 5,000 -> 56,562 · 20,000 -> 41,562
#        40,000 -> 21,562 · 60,000 -> 0 · 88,556 -> 0
#    against a true fixed point of 59,562 at all six. The shipped figure
#    always UNDERSTATES the destination, and once the charge exceeds the
#    gross it collapsed to the GR2 zero sentinel — and `strategic_ledger.gd`
#    renders `if ceiling > 0`, so the line vanished exactly when the chest
#    was largest. On the turn-40 peace board the row was opened over (rate
#    30) it rendered 252,000 against a true 338,500: the player was told the
#    brake was 86,500 gold closer than it is.
#
# 2. THE ECONOMY TAB ANSWERED FOR FRANCE WHEN ASKED ABOUT AUSTRIA.
#    `"treasury": int(world.gold)` and `bankruptcy_turns` read
#    `player_nation`-scoped properties (`world_state.gold`, :2268) while the
#    function takes a `player` argument every other key honours. Measured on
#    the boot: asked about Austria it reported 800 against a real 700; about
#    Britain, 800 against 2,000. No GR5 claim about an AI court's economy
#    was readable.
#
# 3. THE SENTINEL SAID ONE WORD FOR TWO STATES. "no rate, so unbounded" and
#    "not making money, so no such treasury" both returned 0. They are
#    different sentences to a player, and they are named separately now.
#
#    ⚠ SYNTHESIS-ROUND CORRECTION. This used to end "…and the fix makes a
#    THIRD state reachable — a chest already past its own fixed point — which
#    had no copy at all because it could not previously be rendered." That is
#    FALSE, and it was measured false: on the pre-slice (post-charge)
#    argument, 29 of 58 probed chests from 31,000 to 59,000 at rate 80 DID
#    render the above-the-ceiling case — with the BOUNDED copy at the calm
#    DIMMED colour (chest 31,000 read ceiling 30,562; chest 59,000 read
#    2,562). Only above about 60,000, where the post-charge net went
#    non-positive, did the line vanish entirely. What was unreachable was a
#    ceiling below the chest that is ALSO CORRECT.
THE_CHEST_TELLS_THE_TRUTH = True

# The signed components of `_build_economy`'s `net` expression, as the
# CANONICAL map. The ledger is the source of this truth: the
# reconciliation test's own docstring has always said it "MUST mirror
# ledger.py _build_economy's net expression", and `tools/playtest_driver.py`
# kept a THIRD hand-maintained copy which had drifted — it omitted
# `admin_bonus`, leaving a residual of exactly +50 on 40 of 40 LEDGER rows
# of both archived IQ-1 arms. Both readers now import this.
#
# `materiel`, `spent` and `ceiling` are deliberately absent: the first is
# charged at the battle and documented outside Net, and the other two are
# informational (see THE_CHEST_STATES_ITS_CEILING).
NET_GOLD_COMPONENTS = {
    "income": +1,
    "trade_income": +1,
    "admin_bonus": +1,
    "treaty_gold": +1,
    "vassal_tribute": +1,
    "settlement_gold": +1,
    "requisitions": +1,
    "overseas": +1,
    "occupation": -1,
    "contributions": -1,
    "state_charges": -1,
    "dotation_skim": -1,
    "rente_cost": -1,
    "infrastructure": -1,
    "blockade": -1,
    "admiralty": -1,
    "upkeep_base": -1,
    "upkeep_surcharge": -1,
}

# The three states `ceiling` can be in. GR2: `ceiling` stays an int for
# Godot; `ceiling_state` says which sentence to print.
CEILING_BOUNDED = "bounded"        # a real fixed point; `ceiling` is it
CEILING_NO_RATE = "unbounded"      # rate 0 — THE CHARGES do not draw at all
CEILING_NO_SURPLUS = "no_surplus"  # gross <= 0 — the chest is not growing
# ⚠ Review round: CEILING_NO_RATE's copy must name the CHARGES, not "the
# chest". A legacy world pays no Charges of Empire and still pays upkeep, so
# "nothing is drawing on the chest" is printed ~20 lines under an
# "Upkeep: -865g" line that is drawing on it. And the ladder asks the gross
# BEFORE the rate, so a losing legacy world gets the honest sentence.


def state_charges_ceiling(net: int, rate: int) -> int:
    """The treasury EB-1's Charges of Empire are steering toward.

    `calculate_state_charges` draws `(treasury - FLOOR) * rate // DIVISOR`
    each turn, so the fixed point — where the draw finally equals the gold
    coming in — is `FLOOR + net * DIVISOR / rate`. Returns 0 as the
    int-safe "unbounded at this rate" sentinel (GR2) when the rate is 0 or
    the nation is not making money, which are the two cases where no such
    treasury exists.

    SINGLE SOURCE. It takes the rate rather than deriving it so the caller
    passes the SAME rate the charge was applied with (shown = applied — the
    CA9-N11 rule this module already documents for every fraction term).

    `net` MUST be the gold coming in BEFORE the charge is drawn from it.
    That is the whole content of the fixed point, and the one production
    caller (`_build_economy`) passed the post-charge figure until IQ1-2 —
    see THE_CHEST_TELLS_THE_TRUTH for the measurement.

    IQ1-2 correction: this docstring used to claim three readers ("the
    ledger, the dispatch and the playtest driver"). There is exactly ONE
    production call site — `_build_economy` — and the caller is responsible
    for distinguishing the two zero cases (CEILING_NO_RATE vs
    CEILING_NO_SURPLUS), which this function cannot tell apart in its
    return type.
    """
    from backend.models.world_state import CHARGES_HOARD_FLOOR, WAR_EFFORT_DIVISOR
    if int(rate) <= 0 or int(net) <= 0:
        return 0
    return int(CHARGES_HOARD_FLOOR + int(net) * int(WAR_EFFORT_DIVISOR) // int(rate))


def _state_charges_rate_note() -> str:
    from backend.models.world_state import CHARGES_HOARD_FLOOR, WAR_EFFORT_DIVISOR
    return (f"rate points — each draws 1g per {int(WAR_EFFORT_DIVISOR):,}g of the chest "
            f"above the {int(CHARGES_HOARD_FLOOR):,}g floor")


def _build_economy(world, player: str, income_data: dict = None) -> dict:
    """Build economy section.

    CA9-N11: every treasury-FRACTION term — EB-1's Charges of Empire above
    all — is priced on the PRE-income chest, so recomputing AFTER the phase
    has run yields a number that was never charged. A caller describing a
    turn that ALREADY HAPPENED passes the applied income-phase result; a
    caller projecting forward (the ledger's own economy tab) passes nothing
    and keeps today's behaviour byte-identically.
    """
    if income_data is None:
        income_data = world.calculate_turn_income(player)
    # Same prefer-applied contract for upkeep: calculate_turn_upkeep reads
    # nation_bankruptcy_turns, which _update_bankruptcy mutates AFTER the
    # income phase — recomputing on a bankruptcy-flip turn is off by half
    # the upkeep (Aug 2026 health-check audit). The applied phase result
    # carries the charged breakdown as "upkeep_data"; a projection caller
    # (income_data=None) recomputes, byte-identical to before.
    upkeep_data = income_data.get("upkeep_data") or world.calculate_turn_upkeep(player)

    income = int(income_data["income"])
    upkeep = int(upkeep_data["total"])
    # ES-3 (S5): the over-limit surcharge is split out of Upkeep so the
    # economy tab can render it as its own line (§3 breakdown-visible).
    # calculate_turn_upkeep guarantees total == base + surcharge (even
    # under bankruptcy mercy), so the split lines reconcile to Net.
    upkeep_surcharge = int(upkeep_data.get("surcharge", 0))
    upkeep_base = upkeep - upkeep_surcharge
    # EC-U3: the Grande Armée portion OF the surcharge (informational — already
    # inside upkeep_surcharge, so Net reconciliation is untouched; lets the UI
    # split the surcharge line into the ES-3 over-limit part and the EC-U3 part).
    grande_armee = int(upkeep_data.get("grande_armee", 0))
    # ES-2 (S6): recurring cost of holding non-homeland soil — its own
    # signed Net component (income stays GROSS), rendered as an
    # "Occupation" line so the visible lines still sum to Net (SC-33).
    occupation = int(income_data.get("occupation", 0))
    # EC-W1: income suspended by hostile armies standing on our provinces —
    # its own signed Net component, rendered as a "Contributions" line
    # (SC-33 contract; NET_GOLD_COMPONENTS-guarded).
    contributions = int(income_data.get("contributions", 0))
    # EB-5a: what OUR armies requisition from the provinces they disrupt —
    # its own positive signed Net component ("Requisitions" line).
    requisitions = int(income_data.get("requisitions", 0))
    # EB-2: the authored overseas/colonial pool, sea-power-modulated —
    # its own positive signed Net component ("Overseas Trade" line).
    overseas = int(income_data.get("overseas", 0))
    # EB-1: the Charges of Empire (absorbs EC-W2's War Effort) — its own
    # signed Net component, rendered as a "Charges of Empire" line, with
    # the named condition terms riding beside it for the tooltip.
    state_charges = int(income_data.get("state_charges", 0))
    state_charges_terms = list(
        (income_data.get("breakdown") or {}).get("state_charges_terms") or [])
    # ES-7 (S7): full income of endowed provinces redirected to marshals'
    # estates — its own signed Net component, rendered as a "Dotations"
    # line (SC-33 both-halves; forced by the NET_GOLD_COMPONENTS guard).
    dotation_skim = int(income_data.get("dotation_skim", 0))
    # ES-7 second pass (§0.6.8): the rente bill — its own signed Net
    # component, rendered as a "Rentes" line (same SC-33 contract).
    rente_cost = int(income_data.get("rente_cost", 0))
    # EC-U2 (Combat Overhaul Phase 4): per-turn maintenance of built
    # structures — its own signed Net component, rendered as an
    # "Infrastructure" line (same SC-33 contract; NET_GOLD_COMPONENTS-guarded).
    infrastructure = int(income_data.get("infrastructure", 0))
    # DEF-5 naval N3: the fleet's war upkeep — its own signed "Admiralty"
    # Net component (same SC-33 contract).
    admiralty = int(income_data.get("admiralty", 0))

    # Trade income from diplomatic states (read-only calculation).
    # DEF-5 naval §4.2: trade stays GROSS here (the EC-W1 pattern) and the
    # blockade's halving is its own signed "Blockade" Net component — the
    # applied gold is gross − loss (process_trade_income).
    from backend.game_logic.diplomacy import calculate_trade_income
    trade_income_all = calculate_trade_income(world)
    trade_income = int(trade_income_all.get(player, 0))
    blockade = 0
    if getattr(world, "fleets", None):
        from backend.game_logic.naval import blockade_trade_loss
        blockade = int(blockade_trade_loss(world).get(player, 0))

    # Admin bonus (unused AP → gold). Prefer the APPLIED figure when
    # describing a turn that already ran — _advance_turn_internal refills
    # admin AP after the income phase, so a live recompute reports the full
    # bonus on every turn the player actually spent admin AP (Aug 2026
    # health-check audit). Projection callers keep the live read.
    if "admin_bonus" in income_data:
        admin_bonus = int(income_data.get("admin_bonus") or 0)
    else:
        admin_bonus = int(world._calculate_admin_bonus(player))

    # Treaty gold/turn income (clauses where we receive gold)
    # Verify-fleet correction (Aug 2026 health check): shown = applied via
    # the ENGINES' own recorded transfers, never a view-time balance re-read
    # (the chest is post-debit at read time, so a cap here understated a
    # fully-solvent 300g clause as 114). Applied mode = the caller passed
    # the phase result (it carries "upkeep_data"); projection mode keeps the
    # face-amount computation byte-identical to pre-audit behavior.
    _applied_mode = isinstance(income_data, dict) and "upkeep_data" in income_data
    _transfers = getattr(world, "_applied_income_transfers", None) or {}

    if _applied_mode and "treaty_gold" in _transfers:
        treaty_gold = int(_transfers["treaty_gold"].get(player, 0))
    else:
        treaty_gold = 0
        for pair_key, treaty in world.active_treaties.items():
            for clause in treaty.get("clauses", []):
                if clause.get("type") == "gold_per_turn" and clause.get("to") == player:
                    treaty_gold += abs(clause.get("amount", 0))
                elif clause.get("type") == "gold_per_turn" and clause.get("from") == player:
                    treaty_gold -= abs(clause.get("amount", 0))
        treaty_gold = int(treaty_gold)

    # Vassal tribute income
    # Golden Rule 8: mirror process_vassal_tribute's cached-index derivation —
    # a per-vassal full region scan here was O(vassals × regions) per request.
    # EC-W1: mirror the disruption skip too (a vassal province with a hostile
    # army on it pays nobody), so the shown tribute matches the applied one.
    vassal_tribute = 0
    if _applied_mode and "vassal_tribute" in _transfers and world.vassals:
        # The tribute engine recorded what it actually moved this turn.
        vassal_tribute = int(_transfers["vassal_tribute"].get(player, 0))
    elif world.vassals:
        tribute_disrupted = world.get_disrupted_regions()
        for vassal_name, state in world.vassals.items():
            if state.get("lord") == player:
                tribute_rate = state.get("tribute_rate", 0.5)
                v_income = sum(
                    world.regions[name].get_effective_income()
                    for name in world.get_nation_regions(vassal_name)
                    if name not in tribute_disrupted
                )
                vassal_tribute += int(v_income * tribute_rate)

    # SC-33 recurring settlement streams (G4F smoke follow-up): the
    # ratified gold_per_turn obligations the income phase actually moves —
    # previously the per-turn tribute was invisible everywhere except the
    # one-morning dispatch line. Sign mirrors `treaty_gold` (incoming
    # positive).
    settlement_gold = 0
    settlement_streams = []
    for entry in getattr(world, "recurring_settlement_payments", None) or []:
        if not isinstance(entry, dict):
            continue
        payer = str(entry.get("from") or "")
        recipient = str(entry.get("to") or "")
        stream_amount = int(entry.get("amount_per_turn", 0) or 0)
        stream_turns = int(entry.get("turns_remaining", 0) or 0)
        if stream_amount <= 0 or stream_turns <= 0:
            continue
        if player not in (payer, recipient):
            continue
        incoming = recipient == player
        # `stream_amount` stays the CONTRACTUAL face for the row display;
        # the aggregate below prefers the engine's applied record.
        settlement_gold += stream_amount if incoming else -stream_amount
        counterparty = payer if incoming else recipient
        settlement_streams.append({
            "direction": "incoming" if incoming else "outgoing",
            "counterparty": counterparty,
            "amount_per_turn": int(stream_amount),
            "turns_remaining": int(stream_turns),
            "display": (
                f"{'+' if incoming else '-'}{stream_amount}g/turn "
                f"{'from' if incoming else 'to'} {counterparty} "
                f"({stream_turns} turns remain)"
            ),
        })
    settlement_gold = int(settlement_gold)
    if _applied_mode and "settlement_gold" in _transfers:
        # Prefer the engine's applied per-turn record (partial payments) —
        # the rows above keep the contractual face for display.
        settlement_gold = int(_transfers["settlement_gold"].get(player, 0))

    net = int(
        income + trade_income + admin_bonus + treaty_gold + vassal_tribute
        + settlement_gold + requisitions + overseas
        - occupation - contributions - state_charges
        - dotation_skim - rente_cost
        - infrastructure - blockade - admiralty - upkeep_base - upkeep_surcharge
    )

    # Construction queue: iterate player regions with active builds
    construction_queue = []
    for region in world.regions.values():
        if region.controller != player:
            continue
        if region.building_under_construction is not None:
            buc = region.building_under_construction
            construction_queue.append({
                "region": region.name,
                "building": buc["type"],
                "turns_remaining": int(buc["turns_remaining"]),
            })

    # Income breakdown per region
    income_breakdown = []
    for region in world.regions.values():
        if region.controller != player:
            continue
        income_breakdown.append({
            "region": region.name,
            "income": int(region.get_effective_income()),
            "type": region.region_type,
        })

    # IQ1-2 (2): answer for the nation that was ASKED about. `world.gold`
    # and `world.bankruptcy_turns` are player-scoped properties, so every
    # AI court's economy read France's chest back.
    if THE_CHEST_TELLS_THE_TRUTH:
        _treasury = int((getattr(world, "nation_gold", None) or {}).get(player, 0))
        _bankruptcy = int(
            (getattr(world, "nation_bankruptcy_turns", None) or {}).get(player, 0))
    else:
        _treasury = int(world.gold)
        _bankruptcy = int(world.bankruptcy_turns)

    # IQ1-2 (1): the fixed point is defined against the gold coming IN, which
    # is the net BEFORE the charge is taken out of it — `net` above has
    # already subtracted `state_charges`. Passing the post-charge figure made
    # the "destination" move with the chest it is the destination OF.
    _ceiling_rate = sum(int(t.get("amount", 0)) for t in state_charges_terms)
    _ceiling_gross = net + state_charges if THE_CHEST_TELLS_THE_TRUTH else net
    if not THE_CHEST_STATES_ITS_CEILING:
        _ceiling_value, _ceiling_state = 0, CEILING_BOUNDED
    elif not THE_CHEST_TELLS_THE_TRUTH:
        _ceiling_value = state_charges_ceiling(net, _ceiling_rate)
        _ceiling_state = CEILING_BOUNDED
    elif _ceiling_gross <= 0:
        # Review round: the GROSS is asked FIRST. The first cut asked the rate
        # first, so a legacy world (rate 0 by construction) that was BLEEDING
        # money was told "nothing is drawing on the chest" — true of the
        # charges and false of the situation, and the more urgent fact is that
        # the chest is not growing.
        _ceiling_value, _ceiling_state = 0, CEILING_NO_SURPLUS
    elif _ceiling_rate <= 0:
        _ceiling_value, _ceiling_state = 0, CEILING_NO_RATE
    else:
        _ceiling_value = state_charges_ceiling(_ceiling_gross, _ceiling_rate)
        _ceiling_state = CEILING_BOUNDED

    return {
        "treasury": _treasury,
        "income": income,
        "trade_income": trade_income,
        "admin_bonus": admin_bonus,
        "treaty_gold": treaty_gold,
        "vassal_tribute": vassal_tribute,
        "settlement_gold": settlement_gold,
        "settlement_streams": settlement_streams,
        "blockade": blockade,
        "admiralty": admiralty,
        "occupation": occupation,
        "contributions": contributions,
        "requisitions": requisitions,
        "overseas": overseas,
        "state_charges": state_charges,
        "state_charges_terms": state_charges_terms,
        # Slice 17 review round (L2-7): the terms are RATE POINTS under a gold
        # figure; say the unit, from the constants the charge is computed with.
        "state_charges_rate_note": _state_charges_rate_note(),
        # FA-D26 (slice 17, Phase 2): the Butcher's Bill (EC-W3) is charged at
        # the battle, OUTSIDE Net by design (the plunder-gold precedent), and
        # the ledger had no row for it — the one component the applied
        # identity needs. Informational in both modes: the gold the turn's
        # battles have cost SO FAR (the store resets when the turn ends), so
        # a mid-turn read is "spent so far" and the applied read is the
        # whole turn's bill.
        "materiel": (int((getattr(world, "materiel_spent_this_turn", {}) or {}).get(player, 0))
                     if THE_LEDGER_SHOWS_THE_MATERIEL_BILL else 0),
        # IQ-1 SW-0: what this turn has actually cost, and where the chest is
        # headed. Both informational and OUTSIDE Net — `spent` is money that
        # has already left the treasury this turn (so counting it in a
        # projection would charge it twice), and `ceiling` is a destination,
        # not a flow. The SC-33 identity is untouched by construction.
        "spent": (int((getattr(world, "gold_spent_this_turn", {}) or {}).get(player, 0))
                  if THE_CHEST_STATES_ITS_CEILING else 0),
        "ceiling": _ceiling_value,
        "ceiling_state": _ceiling_state,
        "dotation_skim": dotation_skim,
        "rente_cost": rente_cost,
        "infrastructure": infrastructure,
        "upkeep": upkeep,
        "upkeep_base": upkeep_base,
        "upkeep_surcharge": upkeep_surcharge,
        "grande_armee": grande_armee,
        # 0 = no limit (legacy world) — int-safe sentinel for Godot (GR2)
        "force_limit": int(upkeep_data.get("force_limit") or 0),
        "over_force_limit": bool(upkeep_data.get("over_limit", False)),
        "army_strength_total": int(upkeep_data.get("total_strength", 0)),
        # "The Levy is Open" (econ spec review §6): headroom, the live price
        # and the pool, from the SAME source the map summary and the region
        # panel read. Before this the force limit reached the ledger but was
        # rendered only inside the over-limit warning — visible exactly when
        # the gate was shut, invisible the moment it opened.
        "levy": _levy_block(world, player if THE_CHEST_TELLS_THE_TRUTH else None),
        "net": net,
        "bankruptcy_turns": _bankruptcy,
        "construction_queue": construction_queue,
        "income_breakdown": income_breakdown,
    }


# ============================================================================
# INTEL SECTION
# ============================================================================

def _format_strength_display(strength: int) -> str:
    """Format exact strength with commas (e.g. 45000 -> '45,000')."""
    return f"{int(strength):,}"


def _build_intel(world, player: str) -> dict:
    """Build intel section: fog-filtered enemy sightings."""
    known_enemies = []
    # Track best sighting per marshal name to dedup
    best_sightings: Dict[str, dict] = {}

    unknown_count = 0

    for region_name, region in world.regions.items():
        intel = world.get_region_intel(region_name)
        if intel.visibility == UNKNOWN:
            unknown_count += 1
            continue

        for km in intel.known_marshals:
            name = km.get("name", "?")
            nation = km.get("nation", "?")

            # Skip player marshals
            if nation == player:
                continue

            # Determine strength display based on visibility
            if intel.visibility == FULL:
                strength_val = km.get("strength", 0)
                strength_display = _format_strength_display(strength_val)
            elif intel.visibility == PARTIAL:
                band = km.get("band") or get_strength_band(km.get("strength", 0))
                strength_display = band
            elif intel.visibility == STALE:
                frozen = km.get("strength", 0)
                strength_display = f"last seen: {get_strength_band(frozen)}"
            else:  # LAST_KNOWN
                strength_display = "unknown"

            entry = {
                "name": name,
                "nation": nation,
                "location": region_name,
                "strength_display": strength_display,
                "visibility": intel.visibility,
            }

            # Dedup: best visibility wins
            from backend.models.intel import VISIBILITY_PRIORITY
            if name not in best_sightings:
                best_sightings[name] = entry
            else:
                existing_vis = best_sightings[name]["visibility"]
                if VISIBILITY_PRIORITY.get(intel.visibility, 0) > VISIBILITY_PRIORITY.get(existing_vis, 0):
                    best_sightings[name] = entry

    known_enemies = list(best_sightings.values())

    # Nation summaries
    nation_data: Dict[str, dict] = {}
    for enemy in known_enemies:
        nation = enemy["nation"]
        if nation not in nation_data:
            nation_data[nation] = {
                "nation": nation,
                "known_marshals": 0,
                "estimated_strength": 0,
                "regions_controlled": 0,
            }
        nation_data[nation]["known_marshals"] += 1

        # Estimate strength from display
        vis = enemy["visibility"]
        if vis == FULL:
            # Parse exact strength from formatted string
            raw = enemy["strength_display"].replace(",", "")
            try:
                nation_data[nation]["estimated_strength"] += int(raw)
            except ValueError:
                pass
        elif vis == PARTIAL:
            band = enemy["strength_display"]
            nation_data[nation]["estimated_strength"] += BAND_MIDPOINTS.get(band, 0)
        elif vis == STALE:
            band = enemy["strength_display"].replace("last seen: ", "")
            nation_data[nation]["estimated_strength"] += BAND_MIDPOINTS.get(band, 0)
        # LAST_KNOWN: "unknown" — add 0

    # Count regions controlled per enemy nation
    for region in world.regions.values():
        if region.controller and region.controller != player:
            nation = region.controller
            if nation not in nation_data:
                nation_data[nation] = {
                    "nation": nation,
                    "known_marshals": 0,
                    "estimated_strength": 0,
                    "regions_controlled": 0,
                }
            nation_data[nation]["regions_controlled"] += 1

    # Ensure all estimated_strength values are int
    nation_summaries = []
    for nd in nation_data.values():
        nd["estimated_strength"] = int(nd["estimated_strength"])
        nd["regions_controlled"] = int(nd["regions_controlled"])
        nd["known_marshals"] = int(nd["known_marshals"])
        nation_summaries.append(nd)

    return {
        "known_enemies": known_enemies,
        "nation_summaries": nation_summaries,
        "unknown_region_count": int(unknown_count),
    }


# ============================================================================
# MANPOWER SECTION
# ============================================================================

def _build_manpower(world, player: str) -> dict:
    """Build manpower section: pool status + regen rates."""
    pools = world.manpower_pools.get(player, {})
    rates = world.get_manpower_regen_rates(player)

    pool_configs = {
        "infantry": {
            "max": MAX_INFANTRY_POOL,
            "recruit_amount": INFANTRY_RECRUIT_AMOUNT,
            "recruit_base_cost": INFANTRY_RECRUIT_GOLD_COST_BASE,
        },
        "cavalry": {
            "max": MAX_CAVALRY_POOL,
            "recruit_amount": CAVALRY_RECRUIT_AMOUNT,
            "recruit_base_cost": CAVALRY_RECRUIT_GOLD_COST_BASE,
        },
        "artillery": {
            "max": MAX_ARTILLERY_POOL,
            "recruit_amount": ARTILLERY_RECRUIT_AMOUNT,
            "recruit_base_cost": ARTILLERY_RECRUIT_GOLD_COST_BASE,
        },
    }

    # Shown = applied (Aug 2026 health-check audit): the panel used to quote
    # the BASE price with a "±25% stability" note describing a rule the
    # executor does not have — while at war the real charge is up to 2.25×
    # the quoted figure. Price each arm through the executor's OWN
    # _calculate_recruit_cost at the capital (the levy-headline idiom), so
    # this panel and the charge agree.
    from backend.commands.economy_executor import (
        _levy_pricer, depot_closed_reason, recruit_location_gate)
    capital = world.get_nation_capital(player)
    capital_region = world.get_region(capital) if capital else None
    # IQ-2: the tab priced the levy "at the capital" with Austria in Paris —
    # a figure `_execute_recruit` refuses ("We do not control Paris…").
    # Ask the executor's own depot gate and say the depot is closed instead.
    depot_note = ""
    if THE_MANPOWER_TAB_READS_THE_DEPOT and capital_region is not None:
        depot_note = depot_closed_reason(
            world, capital, capital_region,
            recruit_location_gate(capital_region, player))
        # IQ-2 review round: the capital's depot is the DEFAULT recruit path
        # only. A marshal-addressed recruit levies where he stands, through
        # the same location gate (our own soil, stability above 50) — so
        # while France holds any province the note says which path is shut.
        if depot_note and world.get_nation_regions(player):
            depot_note += (" A marshal may still levy where he stands, on "
                           "our own settled soil.")

    result = {}
    for pool_type, config in pool_configs.items():
        current = int(pools.get(pool_type, 0))
        max_val = int(config["max"])
        regen = int(rates.get(pool_type, 0))

        # turns_until_full
        if current >= max_val:
            turns_until_full = 0
        elif regen > 0:
            turns_until_full = int(math.ceil((max_val - current) / regen))
        else:
            turns_until_full = -1

        live_price = int(config["recruit_base_cost"])
        if capital_region is not None:
            live_price = int(_levy_pricer()._calculate_recruit_cost(
                capital_region, world,
                base_cost=int(config["recruit_base_cost"]),
                nation=player))

        result[pool_type] = {
            "current": current,
            "max": max_val,
            "regen_rate": regen,
            "recruit_amount": int(config["recruit_amount"]),
            "recruit_base_cost": int(config["recruit_base_cost"]),
            # the executor's own figure, priced at the capital
            "recruit_price": int(live_price),
            "cost_note": (
                "Live price at the capital — war, stability, force limit "
                "and the recruiting marshal all move it"),
            "turns_until_full": int(turns_until_full),
        }
        if depot_note:
            # IQ-2: the note names the closed depot; `depot_closed` lets the
            # client drop the refused figure (the key is absent while open).
            result[pool_type]["cost_note"] = depot_note
            result[pool_type]["depot_closed"] = True

    return result


# ============================================================================
# ORDERS SECTION
# ============================================================================

from backend.display_names import get_strategic_display as _derive_order_display_name


def _derive_condition_text(order, world) -> str:
    """Derive human-readable condition text from StrategicCondition."""
    cond = order.condition
    if cond is None:
        if order.command_type == "MOVE_TO":
            remaining = len(order.path)
            if remaining > 0:
                return f"{remaining} region(s) left"
            return "arriving"
        if order.command_type == "PURSUE":
            return "tracking"
        if order.command_type == "HOLD":
            return "indefinite"
        if order.command_type == "SUPPORT":
            return "active"
        return "active"

    if cond.max_turns is not None:
        ref_turn = order.arrived_turn if order.arrived_turn is not None else order.started_turn
        elapsed = world.current_turn - ref_turn
        remaining = max(0, cond.max_turns - elapsed)
        return f"{remaining} turn(s) remaining"
    if cond.until_relieved:
        return "until relieved"
    if cond.until_battle_won:
        return "until battle won"
    if cond.until_marshal_arrives:
        return f"until {cond.until_marshal_arrives} arrives"
    if cond.until_marshal_destroyed:
        return f"until {cond.until_marshal_destroyed} destroyed"
    return "active"


def _build_orders(world, player: str) -> list:
    """Build orders section: per player marshal strategic order status."""
    active_orders = []
    idle_marshals = []

    for marshal in world.marshals.values():
        if marshal.nation != player:
            continue
        if THE_ORDERS_TAB_KNOWS_ITS_PRISONERS and getattr(marshal, "captured_by", ""):
            # FA-N65: a prisoner has no orders row — see the lever's note.
            continue

        order = marshal.strategic_order
        if order is not None:
            condition_text = _derive_condition_text(order, world)
            halted = _is_halted(marshal)
            if halted:
                # FA-N36: the client composes "(N regions left)" from
                # `path_remaining` itself, so a frozen march must publish 0
                # or the ORDERS tab keeps promising progress.
                condition_text = "HALTED — awaiting your word"

            active_orders.append({
                "marshal": marshal.name,
                "unit_type": _derive_unit_type(marshal),
                "location": marshal.location,
                "order_type": _derive_order_display_name(order.command_type),
                "order_type_raw": order.command_type,
                "target": order.target,
                "path_remaining": 0 if halted else int(len(order.path)),
                "turns_active": int(world.current_turn - order.started_turn),
                "condition": condition_text,
                "started_turn": int(order.started_turn),
                "arrived_turn": int(order.arrived_turn) if order.arrived_turn is not None else -1,
                "has_order": True,
            })
        else:
            # FA-N36, slice 17 review round (L3-4): an order-FREE decision
            # (last stand, muster confirm) is not idle. The FORCES tab already
            # said `awaiting_decision`; the ORDERS tab said "No active orders"
            # for a man asked to fight to the last. One word on both tabs.
            from backend.commands.strategic import standalone_decision
            pending = standalone_decision(marshal) if THE_LEDGER_SEES_THE_HALT else None
            if pending:
                kind = str(pending.get("interrupt_type") or "")
                quarry = str(pending.get("enemy") or pending.get("quarry")
                             or pending.get("target") or "")
                idle_marshals.append({
                    "marshal": marshal.name,
                    "unit_type": _derive_unit_type(marshal),
                    "location": marshal.location,
                    "order_type": ("Last stand" if kind == "last_stand" else "Muster")
                                  + " — awaiting your word",
                    "order_type_raw": "",
                    "target": quarry,
                    "path_remaining": 0,
                    "turns_active": 0,
                    "condition": "HALTED — awaiting your word",
                    "started_turn": 0,
                    "arrived_turn": -1,
                    "has_order": False,
                    "decision": kind,
                })
                continue
            idle_marshals.append({
                "marshal": marshal.name,
                "unit_type": _derive_unit_type(marshal),
                "location": marshal.location,
                "order_type": "No active orders",
                "order_type_raw": "",
                "target": "",
                "path_remaining": 0,
                "turns_active": 0,
                "condition": "idle",
                "started_turn": 0,
                "arrived_turn": -1,
                "has_order": False,
            })

    return active_orders + idle_marshals
