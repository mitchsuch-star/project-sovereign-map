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
    "cures",              # SR-7d DC-2: read at the doctrine's own seam (DOCTRINES_SPEC §3)
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
    from backend.game_logic.doctrines import flaw_cured as _flaw_cured
    _cured_before = _flaw_cured(world, nation)
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
        before = _court_authority(world, nation)
        line += ". " + authority_line(before, before - int(quote["price"])).rstrip(".")
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
    return {"rows": out, "upkeep_total": upkeep_total, "footer": footer,
            "forecast": lapse_forecast(world, nation)}


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
    if not THE_STATE_HAS_LAWS:
        return None
    in_force = laws_in_force(world, nation)
    if not in_force:
        return None
    from backend.game_logic.ledger import _build_economy
    chest = _court_gold(world, nation)
    net = int(_build_economy(world, nation).get("net", 0) or 0)
    projected = chest + net
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

# ════════════════════════════ the AI (RF-3) ═══════════════════════════════════
# REFORMS_SPEC §7. Every AI great power enacts from its own authored deck, in
# deck order, at the player's prices, through the SAME verb and executor
# (GR5). The rung takes the first law `law_refusal` passes (with the court's
# own admin budget) and whose purse test passes; at most one enactment every
# AI_ENACTMENT_EVERY_TURNS; it never repeals (the lapse rule is its
# discipline). Lever `THE_AI_ENACTS` — down, no AI court enacts: the prior
# BASELINE_SERIES reproduces byte for byte.
THE_AI_ENACTS = True
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


def ai_purse_refusal(world, nation: str, row: Dict,
                     treasury: Optional[int] = None) -> str:
    """"" when an AI court's purse test passes for `row` (§7), else why:
      * the chest ≥ the price (and any arrears) + AI_PURSE_RESERVE +
        AI_PURSE_UPKEEP_TURNS × the slate's upkeep INCLUDING the new law;
      * the court's forecast Net (the ledger's own projection) stays ≥ 0
        after the new upkeep;
      * an authority price never takes the court below AI_AUTHORITY_FLOOR,
        nor leaves it fewer than AI_DIPLOMACY_FLOOR diplomatic points a
        turn."""
    quote = restoration_price(world, nation, row)
    gold = _court_gold(world, nation) if treasury is None else int(treasury)
    need = (int(quote["price"]) if quote["currency"] == "gold" else 0) + int(quote["arrears"])
    upkeep = int(row.get("upkeep", 0) or 0)
    bar = need + AI_PURSE_RESERVE + AI_PURSE_UPKEEP_TURNS * (
        law_upkeep_bill(world, nation) + upkeep)
    if gold < bar:
        return f"the chest ({gold}) is under the bar ({bar})"
    from backend.game_logic.ledger import _build_economy
    net = int(_build_economy(world, nation).get("net", 0) or 0)
    if net - upkeep < 0:
        return f"the forecast Net ({net}) cannot carry {upkeep} a turn"
    if quote["currency"] == "authority":
        authority = _court_authority(world, nation)
        after = authority - int(quote["price"])
        if after < AI_AUTHORITY_FLOOR:
            return f"authority {authority} → {after} is under {AI_AUTHORITY_FLOOR}"
        if _court_dp_after(world, nation, after) < AI_DIPLOMACY_FLOOR:
            return (f"authority {after} would leave fewer than "
                    f"{AI_DIPLOMACY_FLOOR} diplomatic points a turn")
    return ""


def find_ai_enactment(world, nation: str, treasury: int,
                      admin_ap: int) -> Optional[Dict]:
    """§7 THE RUNG: the order an AI court gives this admin phase, or None —
    the first law in deck order that `law_refusal` (its own admin budget)
    and `ai_purse_refusal` both pass, at most one every
    AI_ENACTMENT_EVERY_TURNS. The same verb the player types (GR5)."""
    if not (THE_STATE_HAS_LAWS and THE_AI_ENACTS):
        return None
    if not nation or nation == getattr(world, "player_nation", None):
        return None
    rows = deck(world, nation)
    if not rows:
        return None
    last = _last_enactment_turn(world, nation)
    now = int(getattr(world, "current_turn", 0) or 0)
    if last is not None and now - last < AI_ENACTMENT_EVERY_TURNS:
        return None
    saving = False
    if THE_AI_SAVES_FOR_THE_STAFF:
        staff = next((r for r in rows if isinstance(r, dict) and is_staff(r)), None)
        if (staff is not None and not is_in_force(staff)
                and int(treasury) >= int(staff.get("price", 0) or 0) * AI_SAVES_FOR_THE_STAFF_FROM):
            saving = True
    for row in rows:
        if not isinstance(row, dict) or is_in_force(row):
            continue
        if saving and not is_staff(row):
            continue
        law_id = str(row.get("id") or "")
        if law_refusal(world, nation, law_id, admin_actions=admin_ap):
            continue
        if ai_purse_refusal(world, nation, row, treasury):
            continue
        return {"action": "enact_law", "target": law_id}
    return None

