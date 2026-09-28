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
THE_STATE_HAS_LAWS = True

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
)
# The types WIRED to their seam in this build. The validator refuses a row
# whose effect is not wired: a law must do what it says the day it ships
# ("strike, never invent" — §4; GR9). RF-1 wired `actions`; RF-2 the next
# eight (September 27, 2026); the doctrines' DC-2 wires `cures`.
WIRED_EFFECT_TYPES = (
    "actions",
    "manpower_regen", "recruit_price", "recruit_morale", "drill_morale",
    "supply_capacity", "satellite_loyalty", "cs_closure", "blockade_denial",
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
    return (THE_STATE_HAS_LAWS and isinstance(row, dict)
            and row.get("enacted_turn") is not None)


def laws_in_force(world, nation: str) -> List[Dict]:
    if not THE_STATE_HAS_LAWS:
        return []
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
    return out


def effect_clauses(world, nation: str, effect_type: str) -> List[Dict]:
    """Every clause of `effect_type` among the laws in force."""
    return [clause for _row, clause in effect_terms(world, nation, effect_type)]


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


def recruit_morale_bonus(world, nation: str, arm: Optional[str]) -> int:
    return int(sum(v for _n, v in recruit_morale_terms(world, nation, arm)))


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
    return tuple(sorted(str(r.get("id") or "") for r in laws_in_force(world, nation)))


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
    if nation == getattr(world, "player_nation", None):
        return int(getattr(world, "gold", 0) or 0)
    return int((getattr(world, "nation_gold", {}) or {}).get(nation, 0) or 0)


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
    if not THE_STATE_HAS_LAWS:
        return "The state has no laws to enact."
    row = find_law(world, nation, law_id)
    if row is None:
        return f"That is not one of {nation}'s laws."
    name = display_name(row)              # "the Grand Quartier Général"
    head = name[0].upper() + name[1:]     # at a sentence's head
    if is_in_force(row):
        return f"{head} is already in force (since turn {int(row['enacted_turn'])})."
    quote = restoration_price(world, nation, row)
    gold = _court_gold(world, nation)
    if quote["currency"] == "authority":
        authority = _court_authority(world, nation)
        if authority < quote["price"]:
            return (f"{head} costs {quote['price']} authority; the court holds "
                    f"{authority}.")
        if gold < quote["arrears"]:
            return (f"Restoring {name} costs {quote['arrears']:,} gold in "
                    f"arrears; the treasury holds {gold:,}.")
    else:
        need = quote["price"] + quote["arrears"]
        if gold < need:
            return f"{head} costs {need:,} gold; the treasury holds {gold:,}."
    if admin_actions is None:
        admin_actions = int(getattr(world, "admin_actions_remaining", 0) or 0)
    if int(admin_actions) < ADMIN_ACTIONS_PER_ACT:
        return f"Enacting {name} takes an admin action; none remains this turn."
    return ""


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

def _spend_authority(world, nation: str, amount: int) -> None:
    if nation == getattr(world, "player_nation", None):
        tracker = getattr(world, "authority_tracker", None)
        if tracker is not None:
            tracker.modify_authority(-int(amount))
        return
    table = getattr(world, "nation_authority", None)
    if isinstance(table, dict):
        table[nation] = max(0, int(table.get(nation, 0) or 0) - int(amount))


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
    if gold:
        world.nation_gold[nation] = int(world.nation_gold.get(nation, 0) or 0) - gold
        world.record_gold_spent(nation, gold)
    if authority:
        _spend_authority(world, nation, authority)
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
    return {"quote": quote, "gold": int(gold), "authority": int(authority),
            "authority_before": int(authority_before),
            "authority_after": int(_court_authority(world, nation))}


def repeal_refusal(world, nation: str, law_id: str,
                   admin_actions: Optional[int] = None) -> str:
    """"" when the court may repeal the law now, else the reason (R4)."""
    if not THE_STATE_HAS_LAWS:
        return "The state has no laws to repeal."
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
    row.pop("enacted_turn", None)
    world.log_event({
        "type": "law_repealed",
        "nation": nation,
        "law": str(row.get("id") or ""),
        "name": str(row.get("name") or ""),
        "upkeep": int(row.get("upkeep", 0) or 0),
    })


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
    if not THE_STATE_HAS_LAWS:
        return events
    store = getattr(world, "reforms", None) or {}
    if not store:
        return events
    for nation in world.get_active_nations():
        if nation not in store:
            continue
        while int(world.nation_gold.get(nation, 0) or 0) < 0:
            order = lapse_order(world, nation)
            if not order:
                break
            row = order[0]
            refund = int(row.get("upkeep", 0) or 0)
            row.pop("enacted_turn", None)
            row["lapsed_turn"] = int(getattr(world, "current_turn", 0) or 0)
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
            if nation == getattr(world, "player_nation", None):
                quote = restoration_price(world, nation, row)
                total = int(quote["price"]) + int(quote["arrears"])
                unit = ("gold" if quote["currency"] == "gold"
                        else f"authority and {int(quote['arrears']):,} gold")
                cost = (f"{total:,} gold" if quote["currency"] == "gold"
                        else f"{int(quote['price'])} {unit}")
                staff = (" Its extra order of the day goes with it at the "
                         "next refill." if is_staff(row) else "")
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
