"""Reforms of State — SR-D1 "Reforms, not research" (`docs/REFORMS_SPEC.md`,
gate record §0 authoritative; the readings of §0.1 CONFIRMED by the user,
September 27, 2026, with R3 + R8 replaced by "The Arrears").

A law is a named 1805-period act, authored per court under the scenario key
`reforms` (`europe_1805.json`, validated by `modding/validator.py`). It is
bought once — gold for a material act, authority for a political one, plus one
admin action — and paid for in gold every turn as ONE signed Net component,
"Laws". It lapses when the treasury cannot pay (the largest upkeep first,
before the rentes — R5), and a lapsed law may be restored within ten turns for
half its price plus its arrears (R8 "The Arrears"). Nothing is in force at
boot, on any board.

This module owns the closed set of effect types (§4) and the lifecycle (§2);
the prices, upkeeps and parameters are authored content, reviewable by reading
the scenario file. Every effect is DERIVED at its seam from the laws in force
— a lapse or a repeal removes it by construction, and no second store can
drift (§2 "Effects are derived, never written").

ONE store: `world.reforms = {court: [row, …]}` — the catalogue copied from the
scenario at `from_scenario` (the agendas-deck idiom), with the in-force state
ON each row (the recon's trap 8: the scenario and the save share one shape):
  * `enacted_turn` — present while the law is in force;
  * `lapsed_turn`  — present after a lapse, until the law is restored or
    re-enacted (a repeal never records it, so a repeal never earns the
    Arrears price).
The validator refuses either field in a scenario: nothing is in force at boot.
"""
from __future__ import annotations

import math
import re
import unicodedata
from typing import Dict, List, Optional

# ── Flip lever (REFORMS_SPEC §7 "Balance") ───────────────────────────────────
# False = the state has no laws: every seam reads "nothing in force", the
# verbs refuse, the lapse loop is a no-op — the prior BASELINE_SERIES
# reproduces byte for byte.

# ── §4 The closed set of effect types ────────────────────────────────────────
EFFECT_TYPES = (
    "actions",            # +1, the Staff only — calculate_max_actions / the AI restore
    "manpower_regen",     # +N% on a named pool — get_manpower_regen_rates
    "recruit_price",      # ×m on a named arm or all — _calculate_recruit_cost
    "recruit_morale",     # ±N on a named arm's green-conscript morale
    "drill_morale",       # +N — the drill morale readers
    "supply_capacity",    # ×m on the fed multiplier — _supply_multiplier
    "satellite_loyalty",  # +N a turn for every satellite of the lord
    "cs_closure",         # who counts toward the Continental System closure
    "blockade_denial",    # ×m on a blockaded court's trade loss
    "cures",              # removes one named doctrine flaw (lands at DC-2)
    "force_limit",        # S14k G3: the force-limit floor rises to a tier's — world_state.force_limit_floor
    "rank",               # T4-3: the court's rank rises to a tier's — WorldState.get_power_tier
)
# The types WIRED to their seam in this build. The validator refuses a row
# whose effect is not wired: a law must do what it says the day it ships
# ("strike, never invent" — §4; GR9). RF-1 wired `actions`; RF-2 the next
# eight (September 27, 2026); the doctrines' DC-2 wires `cures`.
WIRED_EFFECT_TYPES = (
    "actions",
    "manpower_regen", "recruit_price", "recruit_morale", "drill_morale",
    "supply_capacity", "satellite_loyalty", "cs_closure", "blockade_denial",
    "cures",              # SR-7d DC-2: read at the doctrine's own seam (DOCTRINES_SPEC §3)
    "force_limit",        # S14k G3: read at `world_state.force_limit_floor` (K5's seam)
    "rank",               # T4-3: read at `WorldState.get_power_tier` (`rank_of_laws`)
)
# RF-2: each wired type's clause parameters — what the validator checks (a
# number inside a type is in-band; a new type or a new parameter is
# structural, §4). ("int"|"float", low, high) bounds a value, a tuple of
# strings closes a choice. `actions` is special-cased (value exactly 1, R7).
ARMS = ("infantry", "cavalry", "artillery")
CLAUSE_SHAPES = {
    # infantry only: the cavalry and artillery rates are recomputed by the
    # stables chip's own marginal (`stables_cavalry_marginal`), so a law on
    # those pools would sit on TWO sources — struck until that is one.
    "manpower_regen": {"pool": ("infantry",), "value": ("int", 1, 100)},
    "recruit_price": {"arm": ARMS + ("all",), "value": ("float", 0.5, 1.5)},
    "recruit_morale": {"arm": ARMS + ("all",), "value": ("int", -30, 30)},
    "drill_morale": {"value": ("int", 1, 20)},
    "supply_capacity": {"value": ("float", 1.0, 2.0)},
    "satellite_loyalty": {"value": ("int", 1, 5)},
    "cs_closure": {"rule": ("every_client",)},
    "blockade_denial": {"value": ("float", 1.0, 2.0)},
    "force_limit": {"tier": ("major", "secondary")},
    # T4-3 (DYNAMISM_SPEC.md §3c G6): no court rises to major by law.
    "rank": {"tier": ("secondary",)},
}
CURRENCIES = ("gold", "authority")
MAX_CLAUSES = 2                       # §4: at most two clauses per law
ADMIN_ACTIONS_PER_ACT = 1             # Q2 / R4: one to enact, one to repeal

# ── R8 "The Arrears" (RULED by the user, September 27, 2026) ─────────────────
# A LAPSED law may be restored within ARREARS_WINDOW_TURNS of its lapse for
# half its price (rounded up) plus its upkeep for every turn it lay dead,
# counting the turn whose upkeep bounced. After the window it has dispersed
# and costs its full price again. A REPEALED law always costs its full price.
ARREARS_WINDOW_TURNS = 10
ARREARS_PRICE_DIVISOR = 2

# The five decks of v1 (R6); a minor court has no laws.
GREAT_POWERS = ("France", "Austria", "Prussia", "Russia", "Britain")
# R6 AMENDED by S14k G3 (October 28, 2026 — the user: "what if ottomans
# reformed"): the Porte's one-row deck, the New Order. It carries no Staff —
# the one-Staff rule binds the five great powers.
REFORM_DECKS = GREAT_POWERS + ("Ottoman",)


# ════════════════════════════ reading the store ═══════════════════════════════

def deck(world, nation: str) -> List[Dict]:
    """The court's authored laws, in its deck order (the AI's order, §7)."""
    store = getattr(world, "reforms", None) or {}
    rows = store.get(nation) or []
    return rows if isinstance(rows, list) else []


def find_law(world, nation: str, law_id: str) -> Optional[Dict]:
    for row in deck(world, nation):
        if isinstance(row, dict) and row.get("id") == law_id:
            return row
    return None


def is_in_force(row) -> bool:
    return (isinstance(row, dict)
            and row.get("enacted_turn") is not None)


def laws_in_force(world, nation: str) -> List[Dict]:
    return [row for row in deck(world, nation) if is_in_force(row)]


def law_upkeep_bill(world, nation: str) -> int:
    """Gold a turn for the laws in force — the "Laws" Net component (§2)."""
    return int(sum(int(row.get("upkeep", 0) or 0)
                   for row in laws_in_force(world, nation)))


def effect_terms(world, nation: str, effect_type: str) -> List[tuple]:
    """(law row, clause) for every clause of `effect_type` among the laws in
    force — the one read every seam makes (derived, never written), with the
    law beside its clause so every surface can NAME it (§11 T8)."""
    out: List[tuple] = []
    if not nation:
        return out
    for row in laws_in_force(world, nation):
        for clause in row.get("effects") or []:
            if isinstance(clause, dict) and clause.get("type") == effect_type:
                out.append((row, clause))
    # RE-6 (RECURRING_EVENTS_SPEC.md §16 "RE-6"): the second source — the
    # Edicts in force, a source that EXPIRES (derived from the turn, never
    # ticked); the pseudo-row names the decree, so every seam that applies
    # and names a law does the same for an edict. A pure read.
    from backend.game_logic import affairs
    for e, until in affairs.edicts_in_force(world, nation):
        row = affairs.edict_row(e, until)
        for clause in row.get("effects") or []:
            if isinstance(clause, dict) and clause.get("type") == effect_type:
                out.append((row, clause))
    return out


def effect_clauses(world, nation: str, effect_type: str) -> List[Dict]:
    """Every clause of `effect_type` among the laws in force."""
    return [clause for _row, clause in effect_terms(world, nation, effect_type)]


def force_limit_floor_of_laws(world, nation: str) -> int:
    """S14k G3: the highest force-limit floor a law in force raises the
    court to (0 = none) — the `force_limit` clause names a tier, read at
    `world_state.force_limit_floor`, K5's one seam."""
    from backend.models.world_state import FORCE_LIMIT_BASE_BY_TIER
    return max((int(FORCE_LIMIT_BASE_BY_TIER.get(str(clause.get("tier")), 0))
                for clause in effect_clauses(world, nation, "force_limit")), default=0)


# ══════════════ T4-3 — promotion (DYNAMISM_SPEC.md §3b, the gate §3c G6) ══════
# A minor that fulfils an ambition and HOLDS its grounds may rise: its
# promotion law (the 1806 crowns — Bavaria's Royal Crown for the Tyrol,
# Saxony's Royal Dignity for Posen, Hesse's Grand Ducal Title for
# Westphalia, Denmark's both shores of the Sound for Scania, Sardinia's
# mainland restored for Piedmont and Savoy) carries a `rank` clause and
# names the design whose provinces are its grounds (`requires_design`).
# Rank is DERIVED — `WorldState.get_power_tier` reads the higher of the
# authored tier and a rank law in force — so everything that reads rank
# moves at once (Q5: teeth at once): the force limit, the capital's guard,
# the table's standing, the bloc's weight, the call to arms against it,
# vassal eligibility. No store, no hold clock: the grounds are the design's
# provinces in the court's hands with a title record at least
# PROMOTION_HOLD_TURNS old (its `since`, which the quiet clock resets while
# the province is contested); the law LAPSES the turn any of them is lost
# (`reason: grounds_lost` — the demotion).
PROMOTION_HOLD_TURNS = 6            # N-DY1b: K
RANK_ORDER = {"minor": 1, "secondary": 2, "major": 3}
GROUNDS_LOST = "grounds_lost"       # `law_lapsed`'s reason for a demotion


def a_minor_may_rise() -> bool:
    """T4-3 seam: a `rank` law may be enacted and raises its court's rank.
    Down: the promotion laws are struck at boot (no deck — as before they
    were authored), a rank law enacts nothing and raises nothing, and no
    law lapses for its grounds."""
    return True


def is_promotion(row) -> bool:
    return isinstance(row, dict) and any(
        isinstance(clause, dict) and clause.get("type") == "rank"
        for clause in row.get("effects") or [])


def standing_deck(rows):
    """The deck as it boots: with the T4-3 seam down the promotion laws are
    struck (`WorldState.from_scenario`, before validation)."""
    if a_minor_may_rise() or not isinstance(rows, list):
        return rows
    return [row for row in rows if not is_promotion(row)]


def rank_of_laws(world, nation: str) -> str:
    """The highest tier a `rank` law in force raises the court to ('' =
    none). The court's OWN laws only — an edict never crowns. Read at
    `WorldState.get_power_tier`, on every rank read: one dict lookup for a
    court with no deck."""
    rows = (getattr(world, "reforms", None) or {}).get(nation)
    if not rows or not a_minor_may_rise():
        return ""
    best = ""
    for row in rows:
        if not is_in_force(row):
            continue
        for clause in row.get("effects") or []:
            if isinstance(clause, dict) and clause.get("type") == "rank":
                tier = str(clause.get("tier") or "")
                if RANK_ORDER.get(tier, 0) > RANK_ORDER.get(best, 0):
                    best = tier
    return best


def promotion_grounds(world, nation: str, row) -> Optional[List[str]]:
    """The provinces a law's `requires_design` names — that design's
    regions on the court's own deck; None when the law names no design or
    the deck carries none by that id (a seam that strikes the design
    leaves the law unenactable, never wrongly open)."""
    design_id = str((row or {}).get("requires_design") or "")
    if not design_id:
        return None
    for entry in (getattr(world, "agendas", None) or {}).get(nation) or []:
        if isinstance(entry, dict) and str(entry.get("id") or "") == design_id:
            return [str(r) for r in entry.get("regions") or [] if r]
    return None


def grounds_title_age(world, nation: str, region_name: str) -> Optional[int]:
    """Turns the court has held `region_name` by its title record — None
    when it does not hold it; its own homeland is title by construction (a
    very old one); a province held with no record reads 0."""
    region = (getattr(world, "regions", None) or {}).get(region_name)
    if region is None or region.controller != nation:
        return None
    if region_name in ((getattr(world, "nation_starting_regions", None) or {})
                       .get(nation) or []):
        return 10 ** 6
    rec = (getattr(world, "province_title", None) or {}).get(region_name) or {}
    if str(rec.get("holder") or "") != nation:
        return 0
    return max(0, int(getattr(world, "current_turn", 0) or 0)
               - int(rec.get("since", 0) or 0))


def _join_grounds(names: List[str]) -> str:
    names = [str(n) for n in names if n]
    if len(names) <= 1:
        return "".join(names)
    return ", ".join(names[:-1]) + " and " + names[-1]


def grounds_refusal(world, nation: str, row) -> str:
    """"" when the law's grounds stand (or it names none): every province
    of its design in the court's hands, each title at least
    PROMOTION_HOLD_TURNS old. Otherwise the reason — what is not held, or
    how long the youngest title still wants."""
    if not (row or {}).get("requires_design"):
        return ""
    name = display_name(row)
    head = name[0].upper() + name[1:]
    grounds = promotion_grounds(world, nation, row)
    if not grounds:
        return f"{head} rests on a design this court does not pursue."
    ages = {r: grounds_title_age(world, nation, r) for r in grounds}
    missing = [r for r in grounds if ages[r] is None]
    if missing:
        return f"{head} waits on {_join_grounds(missing)}: the court does not hold it."
    young = [r for r in grounds if int(ages[r]) < PROMOTION_HOLD_TURNS]
    if young:
        wait = PROMOTION_HOLD_TURNS - min(int(ages[r]) for r in young)
        return (f"{head} waits on {_join_grounds(young)}: held, but not yet "
                f"{PROMOTION_HOLD_TURNS} quiet turns ({wait} more).")
    return ""


def grounds_lost(world, nation: str, row) -> List[str]:
    """The provinces of a law's grounds the court no longer holds ([] =
    the grounds stand, or the law names none it can read)."""
    grounds = promotion_grounds(world, nation, row) or []
    regions = getattr(world, "regions", None) or {}
    return [r for r in grounds
            if getattr(regions.get(r), "controller", None) != nation]


def threat_moves_the_court(world, nation: str) -> bool:
    """S14k G3: a law its scenario marks `under_threat` (the Porte's New
    Order) is enacted by the AI only while its court is at war or called to
    arms by a design priced against it — Selim's reform answered defeat, and
    Alemdar's restoration came in the 1806 war, so a quiet Porte stays
    unreformed and a threatened one may not. The player's verb is ungated."""
    if world.get_nations_at_war_with(nation):
        return True
    from backend.game_logic.recruitment import court_called_to_arms
    return court_called_to_arms(world, nation)


def staff_actions(world, nation: str) -> int:
    """§5: the Staff's +1, read at `calculate_max_actions` and at the AI's
    per-turn restore. 0 or 1 — never written into `bonus_actions`."""
    total = 0
    for clause in effect_clauses(world, nation, "actions"):
        try:
            total += int(clause.get("value", 1) or 0)
        except (TypeError, ValueError):
            continue
    return max(0, total)


# ════════════════════════ RF-2: the eight seams' readers ═══════════════════════
# Each seam calls ONE of these (derived at every read — a lapse or a repeal
# removes the effect by construction). Every reader returns the law's display
# name beside its term, so the surface that applies it can name it (T8).

def _terms(world, nation, effect_type, key=None, want=None, cast=float):
    out = []
    for row, clause in effect_terms(world, nation, effect_type):
        if key is not None and clause.get(key) not in want:
            continue
        try:
            out.append((display_name(row), cast(clause.get("value"))))
        except (TypeError, ValueError):
            continue
    return out


def manpower_regen_terms(world, nation: str, pool: str = "infantry") -> List[tuple]:
    """[(law, +percent)] on `pool`'s regen rate — `get_manpower_regen_rates`."""
    return _terms(world, nation, "manpower_regen", "pool", (pool,), int)


def apply_manpower_regen(world, nation: str, rates: Dict[str, int]) -> Dict[str, int]:
    """The rates with every regen law applied — last, after the war
    exhaustion and the caps (the percentages add, then apply once)."""
    for pool in list(rates):
        pct = sum(v for _n, v in manpower_regen_terms(world, nation, pool))
        if pct:
            rates[pool] = int(rates[pool] * (100 + pct) // 100)
    return rates


def recruit_price_terms(world, nation: str, arm: Optional[str]) -> List[tuple]:
    """[(law, ×multiplier)] on a DRAFT levy of `arm` (a clause for `all`
    arms always applies; an unknown arm meets only those)."""
    want = ("all", arm) if arm else ("all",)
    return _terms(world, nation, "recruit_price", "arm", want, float)


def recruit_morale_terms(world, nation: str, arm: Optional[str]) -> List[tuple]:
    """[(law, ±morale)] on a DRAFT levy's green-conscript morale."""
    want = ("all", arm) if arm else ("all",)
    return _terms(world, nation, "recruit_morale", "arm", want, int)


# T0-D (GR-49): `recruit_morale_bonus` — a second, unread sum of these terms
# (tests only; the levy reads `recruit_morale_terms` to name each law) — is
# removed: one reader per seam.


def drill_morale_terms(world, nation: str) -> List[tuple]:
    """[(law, +morale)] on a completed drill's morale gain."""
    return _terms(world, nation, "drill_morale", cast=int)


def drill_morale_bonus(world, nation: str) -> int:
    return int(sum(v for _n, v in drill_morale_terms(world, nation)))


def supply_capacity_terms(world, nation: str) -> List[tuple]:
    """[(law, ×multiplier)] on the FED supply multiplier."""
    return _terms(world, nation, "supply_capacity", cast=float)


def supply_capacity_factor(world, nation: str) -> float:
    factor = 1.0
    for _n, value in supply_capacity_terms(world, nation):
        factor *= value
    return factor


def satellite_loyalty_terms(world, lord: str) -> List[tuple]:
    """[(law, +loyalty a turn)] for every client of `lord` — the ONE term the
    loyalty tick applies and the forecast quotes."""
    return _terms(world, lord, "satellite_loyalty", cast=int)


def decree_counts_every_client(world, lord: str) -> Optional[str]:
    """The name of the law by which every client of `lord` shuts its ports,
    whatever its autonomy (the Berlin Decree), or None."""
    for row, clause in effect_terms(world, lord, "cs_closure"):
        if clause.get("rule") == "every_client":
            return display_name(row)
    return None


def blockade_denial_terms(world, blockader: str) -> List[tuple]:
    """[(law, ×multiplier)] on the trade a court `blockader` blockades
    loses (the Orders in Council) — the BLOCKADER's laws."""
    return _terms(world, blockader, "blockade_denial", cast=float)


def blockade_denial_factor(world, blockader: str) -> float:
    factor = 1.0
    for _n, value in blockade_denial_terms(world, blockader):
        factor *= value
    return factor


def laws_signature(world, nation: str) -> tuple:
    """The laws in force, as a hashable key — for a cache whose figure a law
    can move without moving the chest (an authority-priced law)."""
    laws = tuple(sorted(str(r.get("id") or "") for r in laws_in_force(world, nation)))
    # RE-6: an edict in force moves the figures a law moves — it joins the key
    from backend.game_logic import affairs
    edicts = tuple(sorted((str(e.get("id") or ""), int(until))
                          for e, until in affairs.edicts_in_force(world, nation)))
    return laws + edicts


# ════════════════════════════ the price, shown = applied ═════════════════════

def turns_dead(world, row) -> Optional[int]:
    """How many turns a lapsed law has lain dead, counting the turn whose
    upkeep bounced; None for a law that did not lapse."""
    lapsed = row.get("lapsed_turn") if isinstance(row, dict) else None
    if lapsed is None:
        return None
    return int(getattr(world, "current_turn", 0) or 0) - int(lapsed) + 1


def restoration_price(world, nation: str, row: Dict) -> Dict:
    """THE price of enacting `row` now — the chip, the confirm, the AI rung
    and the executor all read this one function (R8, shown = applied).

    Returns {"kind": "enact"|"restore", "currency": "gold"|"authority",
             "price": int (in `currency`), "arrears": int (gold),
             "turns_dead": int|None, "disperses_after": int|None}.
    """
    currency = str(row.get("currency") or "gold")
    full = int(row.get("price", 0) or 0)
    dead = turns_dead(world, row)
    if dead is not None and 0 < dead <= ARREARS_WINDOW_TURNS:
        upkeep = int(row.get("upkeep", 0) or 0)
        return {"kind": "restore", "currency": currency,
                "price": int(math.ceil(full / ARREARS_PRICE_DIVISOR)),
                "arrears": int(upkeep * dead),
                "turns_dead": int(dead),
                "disperses_after": int(ARREARS_WINDOW_TURNS - dead)}
    return {"kind": "enact", "currency": currency, "price": full,
            "arrears": 0, "turns_dead": dead, "disperses_after": None}


def _court_gold(world, nation: str) -> int:
    """The gold a court can lay on a law: an AI court's raw treasury; the
    PLAYER's CHEST (S14E-X196 / S14E-D19, `instruments.purse_of` - the
    treasury less the recurring settlement payments still owed), the one
    figure every lump gold verb is gated against. Nothing owed: the treasury."""
    from backend.game_logic.instruments import purse_of
    return int(purse_of(world, nation)[1])


def _court_authority(world, nation: str) -> int:
    if nation == getattr(world, "player_nation", None):
        tracker = getattr(world, "authority_tracker", None)
        return int(getattr(tracker, "authority", 0) or 0)
    return int((getattr(world, "nation_authority", {}) or {}).get(nation, 0) or 0)


def law_refusal(world, nation: str, law_id: str,
                admin_actions: Optional[int] = None) -> str:
    """ONE predicate for the verb, its chip, the AI rung and the preview
    (§2): "" when the court may enact (or restore) the law now, otherwise the
    reason, in the order §2 names them — not this court's law, already in
    force, the price, no admin action left. Refuses free.

    `admin_actions` is the acting court's admin budget; the AI's is a local
    of its turn (the recon's trap 4), so the rung passes it. The player's is
    read off the world when omitted.
    """
    row = find_law(world, nation, law_id)
    if row is None:
        return f"That is not one of {nation}'s laws."
    name = display_name(row)              # "the Grand Quartier Général"
    head = name[0].upper() + name[1:]     # at a sentence's head
    if is_in_force(row):
        return f"{head} is already in force (since turn {int(row['enacted_turn'])})."
    # T4-3: a promotion law waits on its grounds (and on its seam).
    if is_promotion(row) and not a_minor_may_rise():
        return f"{head} is not this court's to take."
    grounds = grounds_refusal(world, nation, row)
    if grounds:
        return grounds
    quote = restoration_price(world, nation, row)
    # S14E-X196 / S14E-D19: the PLAYER's gold is the chest (`_court_gold`);
    # the sentence says so where the coffers hold more than the chest.
    from backend.game_logic.instruments import FREE_OF_OBLIGATIONS, purse_of
    treasury, gold = purse_of(world, nation)
    held = f"{gold:,} gold{FREE_OF_OBLIGATIONS}" if gold < treasury else f"{gold:,}"
    if quote["currency"] == "authority":
        authority = _court_authority(world, nation)
        if authority < quote["price"]:
            return (f"{head} costs {quote['price']} authority; the court holds "
                    f"{authority}.")
        if gold < quote["arrears"]:
            return (f"Restoring {name} costs {quote['arrears']:,} gold in "
                    f"arrears; the treasury holds {held}.")
    else:
        need = quote["price"] + quote["arrears"]
        if gold < need:
            return f"{head} costs {need:,} gold; the treasury holds {held}."
    if admin_actions is None:
        admin_actions = int(getattr(world, "admin_actions_remaining", 0) or 0)
    if int(admin_actions) < ADMIN_ACTIONS_PER_ACT:
        return f"Enacting {name} takes an admin action; none remains this turn."
    return ""


def peace_sink_law(world, nation: str) -> Optional[Dict]:
    """DDB-R7 (Pre-Deploy S13b part 3; `DESIGN_REFINEMENT.md` DDB-D7 — KEEP THE
    RICH PEACE, SURFACE ITS SINK): at peace — no war and no truce — the first
    unenacted gold law of the court's deck the chest can buy, as
    {"row", "name", "need"}; None at war, in a truce, when no law is
    affordable, and for any court but the player's (the AI enacts through
    its own rung). The verb's own predicate decides "can buy"
    (`law_refusal`), its admin-action term set aside: the morning reads the
    sink before the day's first order."""
    if world is None or nation != getattr(world, "player_nation", None):
        return None
    for key, state in (getattr(world, "diplomatic_states", None) or {}).items():
        if state in ("WAR", "ARMISTICE") and nation in str(key).split("|"):
            return None
    for row in deck(world, nation):
        if (not isinstance(row, dict) or is_in_force(row)
                or str(row.get("currency") or "gold") != "gold"):
            continue
        if law_refusal(world, nation, str(row.get("id") or ""),
                       admin_actions=ADMIN_ACTIONS_PER_ACT):
            continue
        quote = restoration_price(world, nation, row)
        return {"row": row, "name": display_name(row),
                "need": int(quote["price"]) + int(quote["arrears"])}
    return None


def peace_sink_line(world, nation: str) -> str:
    """DDB-R7: the morning dispatch's treasury note — "the chest could found
    the Grand Quartier Général — 9,000g" — or "" (the predicate above)."""
    sink = peace_sink_law(world, nation)
    if sink is None:
        return ""
    verb = "found" if is_staff(sink["row"]) else "enact"
    return f"the chest could {verb} {sink['name']} — {sink['need']:,}g"


# ════════════════════════════ the words (RF-1) ════════════════════════════════
# The typed road names a law by its id, its authored name (accents, case and a
# leading "the" ignored — "enact the Grand Quartier General" is the Grand
# Quartier Général) or, for its one `actions` law, "the Staff" (§8 "The
# words": `enact the Staff`). A name that is a word short or long resolves when
# exactly one law holds it.

STAFF_WORDS = ("staff", "general staff", "staff reform", "staff reforms")
_MIN_PARTIAL = 4


def _fold(text) -> str:
    folded = unicodedata.normalize("NFKD", str(text or ""))
    folded = folded.encode("ascii", "ignore").decode("ascii").lower()
    folded = re.sub(r"[^a-z0-9]+", " ", folded).strip()
    return re.sub(r"^the\s+", "", folded)


def is_staff(row) -> bool:
    """The court's one `actions` law (§5)."""
    return any(isinstance(c, dict) and c.get("type") == "actions"
               for c in ((row or {}).get("effects") or []))


# What losing the Staff costs, in the ONE phrase every surface that takes it
# away says: the repeal's answer, the lapse's line, and the Repeal chip (RF-4c:
# the chip — a repeal's only preview, since a repeal is not confirmed — named
# the gold it saves and not the order it takes away).
STAFF_LOSS = "its extra order of the day goes with it at the next refill"


def staff_loss_sentence(row) -> str:
    """" Its extra order of the day goes with it at the next refill." for the
    Staff; "" for any other law."""
    return f" {STAFF_LOSS[0].upper()}{STAFF_LOSS[1:]}." if is_staff(row) else ""


def resolve_law(world, nation: str, text) -> Optional[Dict]:
    """The court's law these words name, or None (the verb then refuses free
    and lists the court's laws)."""
    want = _fold(text)
    if not want:
        return None
    rows = [r for r in deck(world, nation) if isinstance(r, dict)]
    for row in rows:
        if want in (_fold(str(row.get("id") or "").replace("_", " ")),
                    _fold(row.get("name"))):
            return row
    if want in STAFF_WORDS:
        staffs = [r for r in rows if is_staff(r)]
        if len(staffs) == 1:
            return staffs[0]
    if len(want) >= _MIN_PARTIAL:
        partial = [r for r in rows if _fold(r.get("name"))
                   and (want in _fold(r.get("name")) or _fold(r.get("name")) in want)]
        if len(partial) == 1:
            return partial[0]
    return None


def display_name(row) -> str:
    """"the Grand Quartier Général" — the authored name, its article in lower
    case for the middle of a sentence."""
    name = str((row or {}).get("name") or (row or {}).get("id") or "the law")
    return ("the " + name[4:]) if name.startswith("The ") else name


def deck_listing(world, nation: str) -> str:
    """"the Grand Quartier Général (9,000 gold)" for each of the court's
    laws, in deck order — the refusal's own list of what may be named."""
    parts = []
    for row in deck(world, nation):
        if not isinstance(row, dict):
            continue
        price = int(row.get("price", 0) or 0)
        unit = "authority" if row.get("currency") == "authority" else "gold"
        state = " — in force" if is_in_force(row) else ""
        parts.append(f"{display_name(row)} ({price:,} {unit}{state})")
    return "; ".join(parts)


# ════════════════════════════ the lifecycle (RF-1) ════════════════════════════

def _spend_authority(world, nation: str, amount: int, law: str = "") -> None:
    """AU-1: through the one writer (`standing.move`) — the player's tracker
    books the law as its cause; a court's table is clamped the same way."""
    from backend.game_logic import standing
    standing.move(world, nation, -int(amount), "law", law=law or "a political act")


def enact_law(world, nation: str, row: Dict) -> Dict:
    """THE enactment (§2.1) — the player's verb and the AI rung both call it
    (GR5), after `law_refusal` has passed. Charges exactly the price
    `restoration_price` quotes (shown = applied), puts the law in force from
    this moment (each effect reads it at its seam's next read), logs it."""
    quote = restoration_price(world, nation, row)
    gold = int(quote["arrears"]) + (int(quote["price"])
                                    if quote["currency"] == "gold" else 0)
    authority = int(quote["price"]) if quote["currency"] == "authority" else 0
    authority_before = _court_authority(world, nation)
    from backend.game_logic.doctrines import flaw_cured as _flaw_cured
    _cured_before = _flaw_cured(world, nation)
    _tier_before = str(world.get_power_tier(nation) or "")
    if gold:
        world.nation_gold[nation] = int(world.nation_gold.get(nation, 0) or 0) - gold
        world.record_gold_spent(nation, gold)
    if authority:
        _spend_authority(world, nation, authority, law=display_name(row))
    row["enacted_turn"] = int(getattr(world, "current_turn", 0) or 0)
    row.pop("lapsed_turn", None)
    world.log_event({
        "type": "law_enacted",
        "nation": nation,
        "law": str(row.get("id") or ""),
        "name": str(row.get("name") or ""),
        "restored": quote["kind"] == "restore",
        "gold": int(gold),
        "authority": int(authority),
        "upkeep": int(row.get("upkeep", 0) or 0),
    })
    # T4-3: a law that RAISES the court's rank is a promotion — its own log
    # row and its own beat (in place of the routine law line).
    _tier_after = str(world.get_power_tier(nation) or "")
    if is_promotion(row) and _tier_after != _tier_before:
        announce_promotion(world, nation, row, _tier_before, _tier_after)
    else:
        queue_law_beat(world, nation, row,
                       "restored" if quote["kind"] == "restore" else "enacted")
    # SR-7d DC-2 (DOCTRINES_SPEC §4 "the catch-up is announced"): the cure
    # takes effect the moment its law AND the court's Staff both stand —
    # once, derived from the before/after read, zero new fields.
    _cured_now = _flaw_cured(world, nation)
    _refresh_doctrines(world)
    if _cured_now and not _cured_before:
        queue_cure_beat(world, nation, "cured")
    return {"quote": quote, "gold": int(gold), "authority": int(authority),
            "authority_before": int(authority_before),
            "authority_after": int(_court_authority(world, nation)),
            "cure_took_effect": bool(_cured_now and not _cured_before)}


def announce_promotion(world, nation: str, row: Dict, tier_before: str,
                       tier_after: str) -> None:
    """T4-3 — THE promotion's record: ONE `rank_promotion` log row (DY-0's
    column reads it) and one beat, "A CROWN: Bavaria proclaims the Royal
    Crown — …". The rank itself is derived (nothing is written here but the
    words); every per-turn cache that weighs a court by its tier is
    released."""
    from backend.game_logic.dispatch import queue_dispatch_event
    grounds = promotion_grounds(world, nation, row) or []
    name = display_name(row)
    world.log_event({
        "type": "rank_promotion",
        "nation": nation,
        "law": str(row.get("id") or ""),
        "name": str(row.get("name") or ""),
        "tier": tier_after,
        "from_tier": tier_before,
        "grounds": list(grounds),
    })
    queue_dispatch_event(world, "rank_promoted", {
        "nation": nation, "law": name,
        "grounds_clause": (f"with {_join_grounds(grounds)} held, " if grounds else ""),
    }, "always")
    if hasattr(world, "invalidate_active_nations_cache"):
        world.invalidate_active_nations_cache()


def process_grounds_lapses(world) -> List[Dict]:
    """T4-3 — the demotion: a law in force whose grounds are lost (any
    province of its `requires_design` out of the court's hands) LAPSES —
    `law_lapsed` with `reason: grounds_lost`, the Arrears clock started as
    for any lapse (it restores at the Arrears price once the grounds have
    stood PROMOTION_HOLD_TURNS again). Nothing is refunded: the law stood
    this turn. Walks the courts with a deck and their laws in force only
    (Rule 8). Returns the player's tactical events."""
    events: List[Dict] = []
    if not a_minor_may_rise():
        return events
    from backend.game_logic.dispatch import queue_dispatch_event
    store = getattr(world, "reforms", None) or {}
    player = getattr(world, "player_nation", None)
    for nation in world.get_active_nations():
        if nation not in store:
            continue
        for row in list(laws_in_force(world, nation)):
            if not row.get("requires_design"):
                continue
            lost = grounds_lost(world, nation, row)
            if not lost:
                continue
            tier_before = str(world.get_power_tier(nation) or "")
            row.pop("enacted_turn", None)
            row["lapsed_turn"] = int(getattr(world, "current_turn", 0) or 0)
            _refresh_doctrines(world)
            name = display_name(row)
            world.log_event({
                "type": "law_lapsed",
                "nation": nation,
                "law": str(row.get("id") or ""),
                "name": str(row.get("name") or ""),
                "upkeep": int(row.get("upkeep", 0) or 0),
                "reason": GROUNDS_LOST,
                "grounds": list(lost),
                "demoted": str(world.get_power_tier(nation) or "") != tier_before,
            })
            queue_dispatch_event(world, "rank_lost", {
                "nation": nation, "law": name, "grounds": _join_grounds(lost)}, "always")
            if hasattr(world, "invalidate_active_nations_cache"):
                world.invalidate_active_nations_cache()
            if nation == player:
                events.append({
                    "type": "law_lapsed", "nation": nation,
                    "law": str(row.get("id") or ""),
                    "message": (f"{_join_grounds(lost)} is out of our hands, Sire — "
                                f"{name} lapses with its grounds.")})
    return events


def _refresh_doctrines(world) -> None:
    """SR-7d RV-6: every enactment, repeal and lapse refreshes the marshals'
    standing terms (the cure may have changed)."""
    from backend.game_logic.doctrines import refresh_doctrine_terms
    refresh_doctrine_terms(world)


def queue_cure_beat(world, nation: str, kind: str) -> None:
    """SR-7d DC-3b: the cure's beat — a rival's catch-up ("Vienna adopts the
    corps d'armée — the Hofkriegsrat's delays are over") or its lapse
    ("Vienna can no longer pay for its corps"); the player's own lapse is a
    wound. Diplomacy has no fog."""
    from backend.game_logic.dispatch import queue_dispatch_event
    from backend.game_logic.doctrines import cure_beat_vars
    player = getattr(world, "player_nation", None)
    vars_ = cure_beat_vars(world, nation)
    if kind == "cured":
        if nation == player:
            return      # the verb's own answer names it
        queue_dispatch_event(world, "doctrine_cured_abroad", vars_, "always")
        return
    queue_dispatch_event(
        world, "doctrine_cure_lost_home" if nation == player else "doctrine_cure_lost_abroad",
        vars_, "always")


def repeal_refusal(world, nation: str, law_id: str,
                   admin_actions: Optional[int] = None) -> str:
    """"" when the court may repeal the law now, else the reason (R4)."""
    row = find_law(world, nation, law_id)
    if row is None:
        return f"That is not one of {nation}'s laws."
    name = display_name(row)
    if not is_in_force(row):
        return f"{name[0].upper() + name[1:]} is not in force."
    if admin_actions is None:
        admin_actions = int(getattr(world, "admin_actions_remaining", 0) or 0)
    if int(admin_actions) < ADMIN_ACTIONS_PER_ACT:
        return f"Repealing {name} takes an admin action; none remains this turn."
    return ""


def repeal_law(world, nation: str, row: Dict) -> None:
    """R4: out of force at once, nothing refunded. A repeal never records
    `lapsed_turn`, so re-enacting a repealed law costs its full price (R8)."""
    from backend.game_logic.doctrines import flaw_cured as _flaw_cured
    _cured_before = _flaw_cured(world, nation)
    row.pop("enacted_turn", None)
    world.log_event({
        "type": "law_repealed",
        "nation": nation,
        "law": str(row.get("id") or ""),
        "name": str(row.get("name") or ""),
        "upkeep": int(row.get("upkeep", 0) or 0),
    })
    _refresh_doctrines(world)
    if _cured_before and not _flaw_cured(world, nation):
        queue_cure_beat(world, nation, "lost")


def lapse_order(world, nation: str) -> List[Dict]:
    """R5: the order the court's laws lapse in when its chest cannot pay —
    the largest upkeep first; on a tie, the most recently enacted; then the
    later in the deck."""
    rows = list(enumerate(laws_in_force(world, nation)))
    rows.sort(key=lambda item: (-int(item[1].get("upkeep", 0) or 0),
                                -int(item[1].get("enacted_turn", 0) or 0),
                                -item[0]))
    return [row for _, row in rows]


def process_law_lapses(world) -> List[Dict]:
    """§2.3 THE LAPSE — after the income phase charged the "Laws" line, and
    immediately BEFORE ESP-4's rente default (the state sheds its machinery
    before it breaks faith with its marshals — R5). While a court's chest is
    negative and it has laws in force, the first law in `lapse_order` lapses:
    its upkeep BOUNCED, so this turn's charge is refunded into the chest AND
    folded out of the applied income record (Net == the measured change in
    the chest — ESP-4's shape), `lapsed_turn` is stamped (R8: its Arrears
    clock starts), and the lapse is logged. GR5: every court, one rule.
    Returns the player's tactical events (the end-turn report)."""
    events: List[Dict] = []
    store = getattr(world, "reforms", None) or {}
    if not store:
        return events
    # T4-3: a law whose grounds are lost lapses first (the demotion).
    events.extend(process_grounds_lapses(world))
    for nation in world.get_active_nations():
        if nation not in store:
            continue
        while int(world.nation_gold.get(nation, 0) or 0) < 0:
            order = lapse_order(world, nation)
            if not order:
                break
            row = order[0]
            refund = int(row.get("upkeep", 0) or 0)
            from backend.game_logic.doctrines import flaw_cured as _flaw_cured
            _cured_before = _flaw_cured(world, nation)
            row.pop("enacted_turn", None)
            row["lapsed_turn"] = int(getattr(world, "current_turn", 0) or 0)
            _refresh_doctrines(world)
            if _cured_before and not _flaw_cured(world, nation):
                queue_cure_beat(world, nation, "lost")
            world.nation_gold[nation] = int(world.nation_gold.get(nation, 0) or 0) + refund
            applied = (getattr(world, "_income_phase_results", None) or {}).get(nation)
            if applied:
                applied["laws"] = max(0, int(applied.get("laws", 0) or 0) - refund)
                applied["net"] = int(applied.get("net", 0) or 0) + refund
            world.log_event({
                "type": "law_lapsed",
                "nation": nation,
                "law": str(row.get("id") or ""),
                "name": str(row.get("name") or ""),
                "upkeep": refund,
            })
            queue_law_beat(world, nation, row, "lapsed")
            if nation == getattr(world, "player_nation", None):
                quote = restoration_price(world, nation, row)
                total = int(quote["price"]) + int(quote["arrears"])
                unit = ("gold" if quote["currency"] == "gold"
                        else f"authority and {int(quote['arrears']):,} gold")
                cost = (f"{total:,} gold" if quote["currency"] == "gold"
                        else f"{int(quote['price'])} {unit}")
                staff = staff_loss_sentence(row)
                events.append({
                    "type": "law_lapsed",
                    "nation": nation,
                    "law": str(row.get("id") or ""),
                    "message": (
                        f"The treasury cannot pay the {refund:,} gold a turn "
                        f"that {display_name(row)} costs, Sire — the law "
                        f"lapses.{staff} Restored within "
                        f"{ARREARS_WINDOW_TURNS} turns it costs {cost} "
                        f"(half its price and its arrears, dearer each turn); "
                        f"after that its officers disperse and it costs its "
                        f"full price again."),
                })
    return events



# ════════════════════════════ what the player sees (RF-4a) ════════════════════
# REFORMS_SPEC §8 / §8a: every law says what it does, what it costs and what
# would take it away, on the surface where the player decides. ONE source for
# the LAWS tab, its chips, the enactment confirm and the verb's own result.

# §3's teeth, read exactly as the engine reads them: the marshals' calm holds
# only ABOVE 70 (`jealousy`: authority > AUTHORITY_SUPPRESS_ABOVE); the extra
# diplomatic point at 60 and above, and a point lost below 30
# (`diplomacy.calculate_dp`).
CALM_ABOVE = 70
DP_LINE = 60
FLOOR_LINE = 30


def authority_line(before: int, after: int) -> str:
    """"Authority 100 → 85 — the marshals' calm holds above 70." Every line
    the spend crosses is named as lost; when none is crossed, the nearest
    line that still holds is named (§8 "Authority, priced aloud")."""
    before, after = int(before), int(after)
    lost = []
    if before > CALM_ABOVE >= after:
        lost.append("the marshals' calm above 70 is lost")
    if before >= DP_LINE > after:
        lost.append("the extra diplomatic point is lost (it needs 60)")
    if before >= FLOOR_LINE > after:
        lost.append("under 30 the court loses a diplomatic point a turn")
    if lost:
        tail = "; ".join(lost)
    elif after > CALM_ABOVE:
        tail = "the marshals' calm holds above 70"
    elif after >= DP_LINE:
        tail = "the extra diplomatic point holds (60 and above)"
    elif after >= FLOOR_LINE:
        tail = "the court stays at 30 or above"
    else:
        tail = "the court is already under 30"
    return f"Authority {before} → {after} — {tail}."


_ARM_NOUN = {"infantry": "infantry", "cavalry": "cavalry",
             "artillery": "artillery"}


def effect_line(clause) -> str:
    """One clause of a law in numbers — the LAWS tab's "what it does" (§8).
    "" for a clause the build does not render (an unwired type)."""
    if not isinstance(clause, dict):
        return ""
    etype = clause.get("type")
    value = clause.get("value")
    if etype == "actions":
        n = int(value or 0)
        return f"+{n} order{'s' if n != 1 else ''} of the day, from the next refill"
    if etype == "recruit_price":
        v = float(value)
        pct = int(round((v - 1.0) * 100))
        arm = clause.get("arm")
        who = "every levy" if arm == "all" else f"{_ARM_NOUN.get(arm, arm)} levies"
        verb = "cost" if arm != "all" else "costs"
        return f"{who} {verb} {abs(pct)}% {'less' if pct < 0 else 'more'} (×{v:g})"
    if etype == "recruit_morale":
        n = int(value or 0)
        arm = clause.get("arm")
        who = "every draft" if arm == "all" else f"{_ARM_NOUN.get(arm, arm)} drafts"
        return f"{who} muster at {n:+d} morale"
    if etype == "drill_morale":
        return f"+{int(value or 0)} morale from every drill"
    if etype == "manpower_regen":
        return f"{clause.get('pool', 'infantry')} manpower returns {int(value or 0)}% faster"
    if etype == "supply_capacity":
        v = float(value)
        return f"fed provinces feed {int(round((v - 1.0) * 100))}% more men (×{v:g})"
    if etype == "satellite_loyalty":
        return f"+{int(value or 0)} loyalty a turn in every client"
    if etype == "cs_closure":
        # SR-6b RS-25: true only AT WAR (`naval._decree_counts` sits behind
        # the lord-at-war test).
        return "every client shuts its ports to Britain at war, whatever its autonomy"
    if etype == "blockade_denial":
        from backend.game_logic.naval import blockade_cut_percent
        return (f"a blockade it lays cuts the enemy's trade by "
                f"{blockade_cut_percent(float(value))}%, not half (×{float(value):g})")
    if etype == "cures":
        # SR-7d DC-2 (DOCTRINES_SPEC D-R4, RV-15)
        return f"cures {clause.get('flaw')} — the court's doctrine flaw — while its Staff stands"
    if etype == "force_limit":
        # S14k G3: the Porte's New Order
        from backend.models.world_state import FORCE_LIMIT_BASE_BY_TIER
        tier = str(clause.get("tier"))
        return (f"the army may grow as a {tier} power's — the force limit's floor rises to "
                f"{int(FORCE_LIMIT_BASE_BY_TIER.get(tier, 0)):,}")
    if etype == "rank":
        # T4-3: the 1806 crowns — everything that reads rank moves at once
        from backend.models.world_state import FORCE_LIMIT_BASE_BY_TIER
        from backend.nation_config import CAPITAL_GARRISON_BY_TIER
        tier = str(clause.get("tier"))
        return (f"the court ranks as a {tier} power — its army may grow to "
                f"{int(FORCE_LIMIT_BASE_BY_TIER.get(tier, 0)):,}, its capital's guard to "
                f"{int(CAPITAL_GARRISON_BY_TIER.get(tier, 0)):,}, and its voice at the "
                f"table rises with it")
    return ""


def _currency_words(amount: int, currency: str) -> str:
    return f"{int(amount):,} gold" if currency == "gold" else f"{int(amount)} authority"


def terms_line(world, nation: str, row: Dict) -> str:
    """What enacting (or restoring) this law costs, now and every turn —
    `restoration_price`'s quote in words, with the authority priced aloud.
    The chip's note and the confirm read it (shown = applied). It never ends
    in a full stop: the confirm writes its own."""
    quote = restoration_price(world, nation, row)
    upkeep = int(row.get("upkeep", 0) or 0)
    now = _currency_words(quote["price"], quote["currency"])
    if int(quote["arrears"]):
        now += f" + {int(quote['arrears']):,} gold in arrears"
    line = f"{now} now, then {upkeep:,} gold a turn"
    if is_staff(row):
        line += "; one more order each day from the next refill"
    if quote["currency"] == "authority":
        # AU-1: the one quote (`standing.quote`) — `authority_line` + the
        # Charges' grip clause (EAD-2) + the Presence clause when the aura
        # would change; shown = applied.
        from backend.game_logic import standing
        line += ". " + standing.quote(world, nation, -int(quote["price"]))["line"].rstrip(".")
    return line


def laws_payload(world, nation: str) -> Optional[Dict]:
    """The LAWS tab (§8, §8a): one row per law in the court's deck, in deck
    order — what it does, what it costs, its status, and ONE chip (Enact,
    Restore or Repeal) whose enabled state IS the predicate the verb calls
    and whose reason is the predicate's own words (honest availability).
    None on a world with no deck, so a legacy payload stays byte-identical."""
    rows = [r for r in deck(world, nation) if isinstance(r, dict)]
    if not rows:
        return None
    from backend.game_logic.naval import ap_cost_note
    out = []
    for row in rows:
        law_id = str(row.get("id") or "")
        name = display_name(row)
        spoken = name[0].upper() + name[1:]
        price = int(row.get("price", 0) or 0)
        currency = str(row.get("currency") or "gold")
        upkeep = int(row.get("upkeep", 0) or 0)
        entry = {
            "id": law_id,
            "name": str(row.get("name") or law_id),
            "date": str(row.get("date") or ""),
            "says": str(row.get("says") or ""),
            "effects": [line for line in (effect_line(c) for c in (row.get("effects") or [])) if line],
            "price": price,
            "currency": currency,
            "price_words": _currency_words(price, currency),
            "upkeep": upkeep,
            "is_staff": is_staff(row),
        }
        if is_in_force(row):
            entry["status"] = "in_force"
            entry["status_line"] = f"In force since turn {int(row['enacted_turn'])}."
            refusal = repeal_refusal(world, nation, law_id)
            chip = {"label": "Repeal", "command": f"repeal {name}",
                    "enabled": not refusal}
            # S14G-X139 (Pre-Deploy S14h part 2, October 26, 2026): the chip named
            # gold and authority and never the ACTION it spends - "(1 Admin AP)",
            # from the world's own action table (`naval.ap_cost_note`, the
            # Admiralty's chips' reader; the ledger's `_chip_row` renders it).
            chip["cost_note"] = ap_cost_note(world, "repeal_law")
            if refusal:
                chip["reason"] = refusal
            else:
                lost = f" — {STAFF_LOSS}" if is_staff(row) else ""
                chip["note"] = (f"ends {upkeep:,} gold a turn{lost}; nothing is "
                                f"refunded, and enacting it again costs the full "
                                f"{_currency_words(price, currency)}")
        else:
            quote = restoration_price(world, nation, row)
            refusal = law_refusal(world, nation, law_id)
            lapsed = row.get("lapsed_turn")
            if quote["kind"] == "restore":
                # S14D-X27 (October 23, 2026): a lapsed row prices itself ONCE —
                # the Arrears price the chip's note quotes, never the full price
                # printed beside it ("a quote that disagrees with the result").
                entry["price"] = int(quote["price"])
                entry["arrears"] = int(quote["arrears"])
                entry["price_words"] = _currency_words(int(quote["price"]), currency) + (
                    f" + {int(quote['arrears']):,} gold in arrears" if int(quote["arrears"]) > 0 else "")
                entry["status"] = "lapsed"
                entry["status_line"] = (
                    f"Lapsed on turn {int(lapsed)}. It restores at its Arrears "
                    f"price for {int(quote['disperses_after'])} more turn"
                    f"{'s' if int(quote['disperses_after']) != 1 else ''}; "
                    f"then it costs its full price.")
            elif lapsed is not None:
                entry["status"] = "dispersed"
                entry["status_line"] = (f"Lapsed on turn {int(lapsed)} and has "
                                        f"dispersed — its full price again.")
            else:
                entry["status"] = "refused" if refusal else "available"
                entry["status_line"] = refusal or "Not in force."
            chip = {"label": "Restore" if quote["kind"] == "restore" else "Enact",
                    "command": f"enact {name}", "enabled": not refusal}
            chip["cost_note"] = ap_cost_note(world, "enact_law")   # S14G-X139
            if refusal:
                chip["reason"] = refusal
            else:
                chip["note"] = terms_line(world, nation, row)
        # SR-7d DC-3a (DOCTRINES_SPEC §4): a cure law says what it cures,
        # what it would lift THIS turn, and the Staff it needs.
        from backend.game_logic.doctrines import law_cure_line
        _cure = law_cure_line(world, nation, row)
        if _cure:
            entry["cure_line"] = _cure
        entry["spoken"] = spoken
        entry["chip"] = chip
        out.append(entry)
    upkeep_total = int(law_upkeep_bill(world, nation))
    in_force = [e for e in out if e["status"] == "in_force"]
    footer = (f"The laws in force cost {upkeep_total:,} gold a turn."
              if in_force else "No law is in force.")
    payload = {"rows": out, "upkeep_total": upkeep_total, "footer": footer,
               "forecast": lapse_forecast(world, nation)}
    # RE-6: the EDICTS block — only where the recurring deck is armed, so a
    # legacy payload stays byte-identical
    from backend.game_logic import affairs
    if affairs.armed(world):
        payload["edicts"] = edicts_payload(world, nation)
    return payload


def edicts_payload(world, nation: str) -> List[Dict]:
    """RE-6 (RECURRING_EVENTS_SPEC.md §16 "RE-6"): the LAWS book's EDICTS
    block — one row per decree in force, what it does (the laws' own
    `effect_line`) and the morning its term ends; [] with none in force."""
    from backend.game_logic import affairs
    from backend.game_logic.moments import _dateline
    rows = []
    for e, until in affairs.edicts_in_force(world, nation):
        row = affairs.edict_row(e, until)
        when = _dateline(world, int(until))
        name = str(row["name"])
        rows.append({"id": row["id"], "name": name,
                     "spoken": (name[0].upper() + name[1:]) if name else name,
                     "effects": [line for line in (effect_line(c) for c in row["effects"]) if line],
                     "until": int(until), "until_words": when,
                     "status_line": f"In force until {when}."})
    return rows


# ════════════════════════════ the laws everywhere else (RF-4b) ════════════════
# REFORMS_SPEC §8 "The forecast", "The events"; §8a. Nothing about a law ever
# surprises the player at the end of a turn.

def lapse_forecast(world, nation: str) -> Optional[Dict]:
    """§8 THE FORECAST — shown = applied: the lapse rule itself
    (`lapse_order`, §2) run against the ledger's own projection of this turn's
    end (the chest + the forecast Net, `ledger._build_economy`). None when the
    slate is paid. Otherwise: the law that lapses first, the gold that saves
    the whole slate, the laws the rule would take after it, and the player's
    one lever (§8b) — the cheapest OTHER law in force whose repeal alone keeps
    them, with its honest availability (`repeal_refusal`). The LAWS tab, the
    end-turn banner and the morning dispatch all read this."""
    in_force = laws_in_force(world, nation)
    if not in_force:
        return None
    # SF-LB-2b: the ONE projection seam (`ledger.chest_forecast`) — the war
    # council's crisis opening reads the same figure; never a second copy.
    from backend.game_logic.ledger import chest_forecast
    forecast = chest_forecast(world, nation)
    chest = int(forecast["chest"])
    net = int(forecast["net"])
    projected = int(forecast["projected"])
    if projected >= 0:
        return None
    shortfall = -projected
    doomed: List[Dict] = []
    running = projected
    for row in lapse_order(world, nation):
        if running >= 0:
            break
        doomed.append(row)
        running += int(row.get("upkeep", 0) or 0)
    first = doomed[0]
    name = display_name(first)
    spoken = name[0].upper() + name[1:]
    line = (f"{spoken} lapses when this turn ends unless {shortfall:,} gold is "
            f"found — the chest ({chest:,}) cannot carry the turn's Net "
            f"({net:+,}).")
    if len(doomed) > 1:
        after = [display_name(r) for r in doomed[1:]]
        line += (f" {_join_names(after)[0].upper() + _join_names(after)[1:]} "
                 f"would go after it.")
    plan = repeal_plan(world, nation, first, shortfall)
    rescue = None
    if plan:
        pick = plan[0]
        pick_name = display_name(pick)
        refusal = repeal_refusal(world, nation, str(pick.get("id")))
        saves = int(pick.get("upkeep", 0) or 0)
        rescue = {
            "law": str(pick.get("id") or ""),
            "label": f"Repeal {pick_name} instead",
            "command": f"repeal {pick_name}",
            "enabled": not refusal,
            "note": (f"saves {saves:,} gold a turn and keeps {name}"
                     if len(plan) == 1 else
                     f"saves {saves:,} gold a turn — the first of {len(plan)} "
                     f"repeals that keep {name}"),
            "plan": [str(r.get("id") or "") for r in plan],
        }
        names = _join_names([display_name(r) for r in plan])
        if len(plan) == 1:
            sentence = f" Repealing {names} instead keeps it"
        else:
            sentence = (f" Repealing {names} instead would keep it — one admin "
                        f"action each")
        if refusal:
            rescue["reason"] = refusal
            line += sentence + ", but no admin action remains this turn."
        else:
            left = int(getattr(world, "admin_actions_remaining", 0) or 0)
            if nation == getattr(world, "player_nation", None) and left < len(plan):
                # The first repeal alone would lose that law AND the doomed
                # one — the chip is withheld, never a trap.
                short = (f"only {left} admin action{'s' if left != 1 else ''} "
                         f"remain{'s' if left == 1 else ''} this turn")
                rescue["enabled"] = False
                rescue["reason"] = (f"It takes {len(plan)} repeals to keep "
                                    f"{name}, and {short}.")
                line += sentence + f", and {short}."
            else:
                line += sentence + "."
    elif len(in_force) > 1:
        line += " No repeal of the other laws would keep it."
    return {
        "law": str(first.get("id") or ""),
        "name": spoken,
        "shortfall": int(shortfall),
        "chest": int(chest),
        "net": int(net),
        "doomed": [str(r.get("id") or "") for r in doomed],
        "line": line,
        "repeal_instead": rescue,
    }


def repeal_plan(world, nation: str, doomed: Dict, shortfall: int) -> List[Dict]:
    """The player's one lever against a lapse (§8b "What to lose"): the fewest
    repeals of the OTHER laws in force whose saved upkeep covers `shortfall`
    and so keeps `doomed`. The cheapest single law when one suffices (the
    smallest sacrifice); else the largest first until it is covered. [] when
    no repeal of the others would keep it."""
    others = [r for r in laws_in_force(world, nation) if r is not doomed]

    def _upkeep(r):
        return int(r.get("upkeep", 0) or 0)
    single = sorted((r for r in others if _upkeep(r) >= shortfall),
                    key=lambda r: (_upkeep(r), str(r.get("id") or "")))
    if single:
        return [single[0]]
    plan, total = [], 0
    for r in sorted(others, key=lambda r: (-_upkeep(r), str(r.get("id") or ""))):
        if total >= shortfall:
            break
        plan.append(r)
        total += _upkeep(r)
    return plan if total >= shortfall else []


def _join_names(names: List[str]) -> str:
    if len(names) <= 1:
        return "".join(names)
    return ", ".join(names[:-1]) + " and " + names[-1]


def laws_line(world, nation: str) -> Optional[str]:
    """The Diplomatic Ledger's nation-card line (§8a): the court's laws in
    force by name and what they cost it a turn — diplomacy has no fog. None
    when none is in force (the card omits the row)."""
    rows = laws_in_force(world, nation)
    if not rows:
        return None
    return (f"{_join_names([display_name(r) for r in rows])} "
            f"({law_upkeep_bill(world, nation):,} gold a turn)")


def law_named_in(world, nation: str, text) -> Optional[Dict]:
    """The court's law a question NAMES, or None — the desk's world-aware read
    ("what does the Staff cost?" carries no word the parser's law router
    knows). A law's authored name (its article dropped) or its id's words, as
    whole words; "staff" names the court's one Staff."""
    folded = " " + re.sub(r"[^a-z0-9]+", " ", _fold(text)) + " "
    if folded.strip() == "":
        return None
    rows = [r for r in deck(world, nation) if isinstance(r, dict)]
    for row in rows:
        name = _fold(row.get("name"))
        if name.startswith("the "):
            name = name[4:]
        name = re.sub(r"[^a-z0-9]+", " ", name).strip()
        words = str(row.get("id") or "").replace("_", " ").strip()
        for probe in (name, words):
            if probe and f" {probe} " in folded:
                return row
    if " staff " in folded:
        staffs = [r for r in rows if is_staff(r)]
        if len(staffs) == 1:
            return staffs[0]
    return None


def queue_law_beat(world, nation: str, row: Dict, kind: str) -> None:
    """§8 "The events": a court's act is a beat on the next morning dispatch
    — a rival's enactment, restoration or lapse (court knowledge, diplomacy
    has no fog), and the player's own lapse. The player's enactments are the
    verb's own answer; the Staff's arrival is derived at the refill."""
    from backend.game_logic.dispatch import queue_dispatch_event
    player = getattr(world, "player_nation", None)
    name = display_name(row)
    if nation == player:
        if kind == "lapsed":
            queue_dispatch_event(world, "law_lapsed_home", {
                "law": name[0].upper() + name[1:],
                "upkeep": f"{int(row.get('upkeep', 0) or 0):,}",
                "window": str(ARREARS_WINDOW_TURNS),
            }, "always")
        return
    if kind == "lapsed":
        queue_dispatch_event(world, "law_lapsed_abroad", {
            "nation": nation, "law": name}, "always")
        return
    effect = "; ".join(line for line in (effect_line(c) for c in (row.get("effects") or [])) if line)
    queue_dispatch_event(world, "law_enacted_abroad", {
        "nation": nation,
        "verb": "restores" if kind == "restored" else "enacts",
        "law": name,
        "effect": effect or "its terms are its own",
    }, "always")


def staff_arrival(world, nation: str) -> Optional[str]:
    """The Staff's first refill (§8a "the dispatch names why"): the law's
    name when the court's Staff went into force LAST turn — this morning is
    the first with its extra order — else None. Derived (no queue), so a
    Staff enacted and struck down in the same turn announces nothing."""
    now = int(getattr(world, "current_turn", 0) or 0)
    for row in laws_in_force(world, nation):
        if is_staff(row) and int(row.get("enacted_turn", -99)) == now - 1:
            name = display_name(row)
            return name[0].upper() + name[1:]
    return None

AI_ENACTMENT_EVERY_TURNS = 3
# SR-7d DC-2 (DOCTRINES_SPEC §5, REFORMS_SPEC §7 "the recommended fix"):
# every rival's cure rides its Staff (RV-15), and measured at RF-3 only
# Austria's Staff came in on the ambient historical board (turn 33) — the
# rung took cheaper laws first and their upkeep raised the Staff's bar. With
# this lever the rung SAVES for the Staff: once the chest passes half the
# Staff's price it enacts nothing cheaper until the Staff is in force.
THE_AI_SAVES_FOR_THE_STAFF = True
AI_SAVES_FOR_THE_STAFF_FROM = 0.5     # of the Staff's price
AI_PURSE_RESERVE = 1000          # the chest keeps a reserve …
AI_PURSE_UPKEEP_TURNS = 5        # … and five turns of the slate's upkeep
AI_AUTHORITY_FLOOR = 30          # a political act never takes the court below 30
# The diplomatic term (§3: "the AI rung weighs it" — made TRUE at RF-3). Every
# AI court boots at authority 60, so its first political act loses the +1 a
# turn above 60 (`diplomacy.calculate_dp`). The rung weighs that point by a
# floor in the house style: a political act never leaves the court fewer than
# AI_DIPLOMACY_FLOOR diplomatic points a turn. A hard "never cross 60" would bar
# all seven political acts of the four rival decks; the floor binds a court
# that has lost its capital and has no skilled envoy.
AI_DIPLOMACY_FLOOR = 3


def _last_enactment_turn(world, nation: str) -> Optional[int]:
    """The turn the court last enacted a law still in force (derived from
    the rows — zero new fields; a law that lapsed or was repealed no longer
    paces the next)."""
    turns = [int(r["enacted_turn"]) for r in laws_in_force(world, nation)]
    return max(turns) if turns else None


def _court_dp_after(world, nation: str, authority_after: int) -> int:
    from backend.game_logic.diplomacy import calculate_dp
    diplomat = (getattr(world, "diplomats", {}) or {}).get(nation)
    capital = world.get_nation_capital(nation)
    holds = bool(capital and capital in world.regions
                 and world.regions[capital].controller == nation)
    return int(calculate_dp(diplomat, int(authority_after), holds))


def a_crown_is_bought_with_the_whole_chest() -> bool:
    """Session G — the gate earned (DYNAMISM_SPEC.md §7a, November 11, 2026):
    the AI's purse bar for a PROMOTION law (`is_promotion` — the five crowns
    of 1806) is the price and any arrears alone — no `AI_PURSE_RESERVE`, no
    five turns' upkeep: Bavaria paid for its crown with everything it had. A
    minor booting at 800 and netting ~150 a turn reached the 4,500 bar near
    turn 36 and the price near turn 26 (measured, Hesse after Emil's 2,500).
    Every other law keeps the reserve; the Net test stands; the player's and
    the AI's shared gate `law_refusal` is untouched. Down: 4,500."""
    return True


def ai_reads_net_before_charges() -> bool:
    """S14j (the economy rebalance, October 27, 2026): the AI's purse reads the
    Net BEFORE the Charges of Empire, the player's counsel's rule (EA-18).

    EAD-9 kept the plain read because, with the crown term at 30, the two
    reads agreed on every commanded seed. With the crown at 250 they do not.
    A rich court's forecast Net turns negative as the Charges draw on its
    hoard, so the plain read refused a law and a levy BECAUSE the court was
    rich (measured: Britain at war on 60,000 refused to arm). Read by the
    laws rung and by `EnemyAI._court_arms_with_its_purse`. The seam the
    series holds down (False = the plain read)."""
    return True


def _purse_bar(world, nation: str, row: Dict, quote: Optional[Dict] = None) -> int:
    """The chest a court must hold before it buys `row` (§7, ONE source —
    `ai_purse_refusal`'s chest half and T0-G's reachability guard): the
    gold price (and any arrears) + AI_PURSE_RESERVE + AI_PURSE_UPKEEP_TURNS
    × the slate's upkeep including the new law's own."""
    if quote is None:
        quote = restoration_price(world, nation, row)
    need = (int(quote["price"]) if quote["currency"] == "gold" else 0) + int(quote["arrears"])
    if a_crown_is_bought_with_the_whole_chest() and is_promotion(row):
        return need    # session G: a crown is bought with the whole chest
    upkeep = int(row.get("upkeep", 0) or 0)
    return need + AI_PURSE_RESERVE + AI_PURSE_UPKEEP_TURNS * (
        law_upkeep_bill(world, nation) + upkeep)


def the_staff_must_be_reachable() -> bool:
    """T0-G (GR-47, the November 6, 2026 review): the save-for-the-Staff
    rule's reachability guard — the rung saves only for a Staff its chest
    can REACH, else it buys what it can afford. A court sitting in the
    band [half the Staff's price, an unreachable bar) enacted nothing for
    the rest of the game (Prussia and Russia never afford their Staff in
    forty turns on any seed — DC-2's own landing record; the T8 probe at
    this slice's head read 0 of 4 cured by T30). Down (False): the band —
    saving unconditional, the pre-fix rule."""
    return True


def staff_is_reachable(world, nation: str, staff: Dict) -> bool:
    """T0-G (GR-47): can this court's chest ever stand at the Staff's bar?
    The purse ceiling is the Charges' fixed point (`state_charges_ceiling`
    read through `_build_economy`, the caller distinguishing its two zero
    states): CEILING_NO_RATE — the Charges do not draw — reaches any bar
    while the gross is positive; CEILING_BOUNDED reaches the bar iff the
    ceiling stands at or above it; CEILING_NO_SURPLUS — the chest is not
    growing — reaches nothing it does not already hold. Re-read every
    turn, so a court whose economy recovers resumes saving."""
    from backend.game_logic.ledger import (CEILING_BOUNDED, CEILING_NO_RATE,
                                           _build_economy)
    econ = _build_economy(world, nation, rows=False)
    state = econ.get("ceiling_state")
    if state == CEILING_NO_RATE:
        return True
    if state == CEILING_BOUNDED:
        return int(econ.get("ceiling", 0) or 0) >= _purse_bar(world, nation, staff)
    return False


def ai_is_saving_for_the_staff(world, nation: str, treasury: int) -> Optional[Dict]:
    """§7 + T0-G: the ONE saving predicate — the lever up, a Staff pending,
    the chest past AI_SAVES_FOR_THE_STAFF_FROM of its price, and (GR-47)
    the Staff REACHABLE (`staff_is_reachable`, unless that guard's seam is
    down). Returns the Staff row while the court is saving, else None.
    Readers: `find_ai_enactment` (the laws rung) and `affairs.find_ai_edict`
    (GR-15 — gold decrees held while saving). `counsel._law_terms` keeps
    its own lever semantics (the player's hint must not flip with the AI
    rung's flag) and reads only the guard, `staff_is_reachable`."""
    if not THE_AI_SAVES_FOR_THE_STAFF:
        return None
    rows = deck(world, nation)
    staff = next((r for r in rows
                  if isinstance(r, dict) and is_staff(r)), None)
    if staff is None or is_in_force(staff):
        return None
    if int(treasury) < int(staff.get("price", 0) or 0) * AI_SAVES_FOR_THE_STAFF_FROM:
        return None
    if the_staff_must_be_reachable() and not staff_is_reachable(world, nation, staff):
        return None
    return staff


def ai_purse_refusal(world, nation: str, row: Dict,
                     treasury: Optional[int] = None,
                     net_before_charges: bool = False) -> str:
    """"" when an AI court's purse test passes for `row` (§7), else why:
      * the chest ≥ the price (and any arrears) + AI_PURSE_RESERVE +
        AI_PURSE_UPKEEP_TURNS × the slate's upkeep INCLUDING the new law;
      * the court's forecast Net (the ledger's own projection) stays ≥ 0
        after the new upkeep;
      * an authority price never takes the court below AI_AUTHORITY_FLOOR,
        nor leaves it fewer than AI_DIPLOMACY_FLOOR diplomatic points a
        turn.

    `net_before_charges` (the economy audit, October 5, 2026 — EA-18, the
    player's counsel only): the Charges of Empire are a share of the chest
    ABOVE its floor, so they fall as the chest falls and can never take it
    below the floor on their own account. A law is therefore sustainable
    when the Net BEFORE the Charges carries its upkeep — the chest settles
    at a lower ceiling instead of draining. Read the plain forecast Net and a
    rich court is refused for being rich (measured: a France holding 30,000
    nets +47 and is told to levy 3,000 infantry, not to enact the Staff).
    The AI rung kept the plain read until S14j (EAD-9). It now passes
    `ai_reads_net_before_charges()`, because the raised crown term made the
    two reads disagree for every rich court."""
    quote = restoration_price(world, nation, row)
    gold = _court_gold(world, nation) if treasury is None else int(treasury)
    upkeep = int(row.get("upkeep", 0) or 0)
    bar = _purse_bar(world, nation, row, quote=quote)
    if gold < bar:
        return f"the chest ({gold}) is under the bar ({bar})"
    from backend.game_logic.ledger import _build_economy
    econ = _build_economy(world, nation, rows=False)   # T0-D (GR-33): the purse read
    net = int(econ.get("net", 0) or 0)
    if net_before_charges:
        net += int(econ.get("state_charges", 0) or 0)
        if net - upkeep < 0:
            return (f"the Net before the Charges of Empire ({net}) cannot "
                    f"carry {upkeep} a turn")
    if net - upkeep < 0:
        return f"the forecast Net ({net}) cannot carry {upkeep} a turn"
    if quote["currency"] == "authority":
        # AU-1: the courts' floors read through ONE gate (`standing.ai_refusal`)
        from backend.game_logic import standing
        reason = standing.ai_refusal(world, nation, int(quote["price"]))
        if reason:
            return reason
    return ""


def ai_repeal_before_lapse(world, nation: str, admin_ap: int) -> Optional[Dict]:
    """SFR-B14 (SF-RR4, October 21, 2026): an AI court repeals before a law
    lapses — the player's one lever against the lapse (§8b, the forecast's
    "Repeal X instead"), through the same verb (GR5). CMD-M (marengo) read
    "Austria cannot pay for the Landwehr — the law lapses" and two turns
    later "… the Generalissimus — the law lapses"; the rung never repealed
    (it read the purse only at enactment). It fires only when a repeal KEEPS
    the doomed law (`repeal_plan`): a lapse refunds the turn's charge and
    leaves a half-price restoration (R8), a repeal does neither, so a repeal
    that saves nothing would only be dearer. The plan's first law, when the
    admin budget carries the whole plan; else None."""
    if not nation or nation == getattr(world, "player_nation", None):
        return None
    forecast = lapse_forecast(world, nation)
    if not forecast:
        return None
    doomed = find_law(world, nation, str(forecast.get("law") or ""))
    if doomed is None:
        return None
    plan = repeal_plan(world, nation, doomed, int(forecast.get("shortfall") or 0))
    if not plan or int(admin_ap) < len(plan) * ADMIN_ACTIONS_PER_ACT:
        return None
    return {"action": "repeal_law", "target": str(plan[0].get("id") or "")}


def ai_holds_the_purse(world, nation: str) -> bool:
    """SFR-B14's sibling (RR4-X9): a court whose law would lapse at this
    turn's end spends no gold on anything else this admin phase — the
    spending rungs (the levy, the works, a commission, a new law) never read
    the forecast, so a court on the edge spent itself over it (the staged
    board: Austria built, and both its laws lapsed). The repeal rung still
    runs first; the unspent orders earn their gold as ever."""
    if not nation or nation == getattr(world, "player_nation", None):
        return False
    return lapse_forecast(world, nation) is not None


def find_ai_enactment(world, nation: str, treasury: int,
                      admin_ap: int) -> Optional[Dict]:
    """§7 THE RUNG: the order an AI court gives this admin phase, or None —
    the first law in deck order that `law_refusal` (its own admin budget)
    and `ai_purse_refusal` both pass, at most one every
    AI_ENACTMENT_EVERY_TURNS. The same verb the player types (GR5)."""
    if not nation or nation == getattr(world, "player_nation", None):
        return None
    rows = deck(world, nation)
    if not rows:
        return None
    last = _last_enactment_turn(world, nation)
    now = int(getattr(world, "current_turn", 0) or 0)
    if last is not None and now - last < AI_ENACTMENT_EVERY_TURNS:
        return None
    # T0-G (GR-47): the ONE saving predicate, reachability-guarded — the
    # rung saves only for a Staff its chest can reach (ceiling ≥ bar),
    # else it buys what it can afford.
    saving = ai_is_saving_for_the_staff(world, nation, int(treasury)) is not None
    for row in rows:
        if not isinstance(row, dict) or is_in_force(row):
            continue
        if saving and not is_staff(row):
            continue
        if row.get("under_threat") and not threat_moves_the_court(world, nation):
            continue
        law_id = str(row.get("id") or "")
        if law_refusal(world, nation, law_id, admin_actions=admin_ap):
            continue
        if ai_purse_refusal(world, nation, row, treasury,
                            net_before_charges=ai_reads_net_before_charges()):
            continue
        return {"action": "enact_law", "target": law_id}
    return None

