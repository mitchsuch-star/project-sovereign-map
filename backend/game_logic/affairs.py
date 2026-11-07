"""RE-1 "Affairs of State" — the recurring letters (`docs/RECURRING_EVENTS_SPEC.md`
§5–§13: the block §5, the pacing §7, one function §8, the engine §9, the seeds
§10, the saves §11, Rule 8 §13; Pre-Deploy row RE — RE-1: the engine, UNARMED).

An affair is a RECURRING letter of state — a bill of the player's own acts
(the Emperor afield while the Council waits; corps quartered on an ally) or a
war-time door (the Staff offered) — on the moments' transport
(`backend/game_logic/moments.py`): the same letter, the same `plan` and
`_apply`, the same answer roads, the same readers. What is NEW lives here: the
premises and their streaks, the pulse, `deliver_due`, the Watch, the free
withdrawal, and a `resolve_courts` that does nothing (Q4: France's content on
code shared by every court).

The authored deck rides the scenario's `moments.affairs` key and lands at
`world.moments["block"]["affairs"]`; the RUNTIME store is
`world.moments["affairs"]` — {"streaks": {"<template>|<subject>": n},
"masks": {"<template>": int}, "due": {"<template>|<subject>": turn},
"set_aside": {"count", "turn"}, "watched": {"<template>": turn},
"morning": turn, "not_before": turn} — ints and short strings only (§11).
Each arrival is an OCCURRENCE row of `world.moments["state"]`,
"<template>#<n>", frozen at delivery with {id, lord, bind, tier, form} (§5),
so "the_host#2 = Bavaria, tier 2" survives a save, a premise that changes and
the lapse two turns later. A world whose block authors no `affairs` deck is
UNARMED: every function here returns at once and writes nothing — the
tutorials and the bare flag world. The shipped 1805 boot is ARMED from RE-3
(November 1, 2026): `moments.affairs` is `tests/fixtures/affairs_block.json`'s
block verbatim, its reach measured (`tools/_affairs_measure.py`).

The rules:

* **No dice** (§10). The premise, held for its streak, decides WHETHER; the
  seeded pulse decides WHEN (`first`, then a `gap` per arrival); `historical`
  collapses every band to its value and ties fall to authored order. Nothing
  here draws from `random` or `enemy_ai.ai_rng`.
* **The moments never see an affair** (§7). The moments' tick reads
  `moments.moment_rows`; an affair standing when a moment arrives is
  withdrawn free (nothing applied, its cooldown re-armed, one line); the
  look-ahead (P8) stands an affair aside when a dated moment's window opens
  within two mornings with its premise true.
* **Rule 8** (§13). No premise iterates `world.regions`: one pass over the
  marshal list, a handful of state lookups, the purse — each behind a
  per-turn memo on the world object.
* **Shown = applied.** Every figure is `moments.plan`'s; the Decline is never
  priced in a purse (the validator); the alarm is never touched.
"""
from __future__ import annotations

import copy
import re
from typing import Any, Callable, Dict, List, Optional, Tuple

from backend.errors import report
from backend.game_logic import moments as MO

KIND_AFFAIR = "affair"
SHAPES = ("bill", "door", "offer")
SCOPES = ("owner", "any_lord")
VOICES = ("named", "office", "host")
ID_RE = re.compile(r"^[a-z_]{1,32}$")
SUBJECT_SEP = "|"

# The pacing (§7): authored under `affairs.pacing`; a band collapses to its
# value on `historical`. In-band tunables, validator-limited.
PACING_DEFAULTS = {"first": 7, "gap": 5, "cap_act": 6, "wait": 4}
PACING_BANDS = {"first": (6, 9), "gap": (4, 7)}
PACING_BOUNDS = {"cap_act": (1, 12), "wait": (1, 6)}
STREAK_BOUNDS = (1, 12)
COOLDOWN_BOUNDS = (6, 30)
CAP_BOUNDS = (1, 4)
GRACE_BOUNDS = (1, 6)
SCALE_MAX_TIER = 3
LATCH_OF_MAX = 16
LOOK_AHEAD = 2         # P8: an affair stands aside this many mornings before a dated moment
SET_ASIDE_EVERY = 6    # §7: the aggregated "set aside" line, at most once in six turns

# The op table (§5): the moments' closed table less the alarm (barred from
# every affair) and the autonomy write, plus `authority` and `admin`.
AFFAIR_OPS = ("gold", "authority", "admin", "dp", "relation", "loyalty", "enact_law", "squadron", "edict")
AFFAIR_OP_BOUNDS = {"gold": (1, 2000), "authority": (-10, 0), "admin": (1, 1), "dp": (1, 2),
                    "relation": (-20, 20), "loyalty": (-20, 20)}
# RE-H (§6.5, P4): the squadron op — Accept-only, at most one per entry, an
# entry carrying it authors a fallback form (the bill) and its owner a navy.
SQUADRON_BOUNDS = {"ships": (1, 8), "away": (3, 6), "to": 32}
# P18: a form's `requires` — the first form whose requirement holds is frozen
# at delivery; a form without one is the fallback.
FORM_REQUIRES = ("hunter_at_sea",)
DECLINE_ALLOWED_OPS = ("relation", "loyalty", "authority")
BARRED_OPS = ("alarm", "autonomy")
# RE-6 (§0 Q2, §6.2 E1–E3, §16 "RE-6"): the Edicts — an `offer`'s Accept is
# exactly `admin` + `edict`; the `edict` op's price, term, rest and effect
# clauses live on the template's `edict` block (the door's `enact_law` idiom:
# the price is the decree's, outside the gold bound). The effect types are the
# ruling's three alone — `actions`, `force_limit` and `cures` would grant a
# Staff order, a force-limit floor or a cure by decree.
EDICT_OP = "edict"
EDICT_BOUNDS = {"price": (500, 5000), "term": (4, 16), "rest": (4, 16), "effects": 2,
                "below_pct": (10, 90)}
EDICT_EFFECT_TYPES = ("supply_capacity", "recruit_price", "drill_morale")
EDICT_DISPLAY_KEYS = ("name", "court_press")
EDICTS_KEY, DECREED_KEY, EDICT_GOLD_KEY = "edicts", "decreed", "edict_gold"
EDICT_AUTHORITY_KEY = "edict_authority"   # AU-3a: the authority the Decree spent, per lord (the measure)
EDICT_AUTHORITY_BOUNDS = (1, 10)          # AU-3a: the block's `authority` price (the Decree), the validator's

# The display copy (§16b): what a letter SAYS, never when it arrives or what
# its answers do — struck from the measured identity (`_s14c_sweep_record`).
DISPLAY_KEYS = ("title", "voice", "record", "line", "counsel", "exhibit", "exhibit_from", "ground",
                "watch", "source", "button_line", "closing", "slots")
VARIANT_DISPLAY_KEYS = ("text",)
# RE-3 (P12, §12c): `situation` is the morning-after SITUATION line an answer
# authors (RE-R renders it); `echo` the response's reply, `press` the Gazette's
# COURTS line, `remember` the board line on the template's next occurrence.
ANSWER_DISPLAY_KEYS = ("caption", "button_line", "echo", "press", "remember", "situation", "outcome")
TEXT_MAX = {"title": 40, "record": 240, "variant": 240, "line": 200, "counsel": 160,
            "exhibit": 160, "exhibit_from": 40, "watch": 120, "button_line": 40, "echo": 160,
            "press": 160, "remember": 160, "situation": 160, "caption": 36, "source": 400,
            "closing": 240, "slot": 60, "outcome_line": 160,
            "court_press": 160, "edict_name": 40}          # RE-6: the edict block's copy
OUTCOMES = ("home", "caught")       # RE-H: a squadron's two fates (the Accept's `outcome` copy)
# RE-H (§6.5, P18): the chapter is keyed by the arrival (first / later) and by
# the last squadron's fate (home / caught — the row's frozen `last_fate`, from
# the fleet record at delivery); the fate chapters are authored BEFORE the
# later-arrival chapter, so a letter that remembers a sailing says so first.
VARIANT_FACTS = ("arrival", "last_fate")
VARIANT_VALUES = {"arrival": ("first", "later"), "last_fate": ("home", "caught")}
VARIANTS_MAX = 4
EXHIBITS_MAX = 2          # the exhibits alternate by arrival
CLOSING_MAX = 2           # the closing record and the 1825 line (RE-C renders them)
ARRIVAL_FIRST = "first"
ARRIVAL_LATER = "later"
# RE-H (the user's word, November 1, 2026 — §0b P16 amended for the Haiti
# letter): `bites: true` asks both halves (the Decline's loss lands below the
# aura's full line AND the floor allows it whole); `bites: "floor"` the floor
# half alone, so the letter arrives at full standing too.
BITES_FLOOR = "floor"
# AU-2a's first reading reversed by the user's word ("Clamp it first",
# November 4, 2026): `bites: "clamp"` asks neither half — the letter arrives at
# any standing and its plan takes what the floor allows, saying the rest
# (`moments._plan_authority`). Only a Decline that carries a price besides
# authority may clamp (the validator): clamped, a bill in authority alone would
# cost nothing, and the floor is its only honest rule.
BITES_CLAMP = "clamp"
BITES_MODES = (True, BITES_FLOOR, BITES_CLAMP)
# AU-2a (AUTHORITY_CURRENCY_SPEC.md §5.4, §5.8): deck content a slice added that
# a series arm may hold down to the tree before it — an op's `since`, an
# entry's `bites_since` — each naming a row whose seam `row_armed` reads.
# AU-2c: an ENTRY's own `since` holds the whole template out of the deck
# (`moments.affairs_deck`) while its row is unarmed.
SINCE_ROWS = ("AU-2a", "AU-2b", "AU-2c", "AU-3a", "AU-3b")


def row_armed(row: str) -> bool:
    """The seam behind a row's deck content: AU-2a's is `standing.hits_armed`
    (the Chancellor's floor clause, the Host's authority op); AU-2b's is
    `standing.sources_armed` (the ceremonies' op, the Show's two Acts);
    AU-2c's is `standing.letters_armed` (the Bank's and the Pope's letters,
    armed by the user's word); AU-3a's is `standing.buys_armed` (the Edict
    letters' third answer, "Decree it"); AU-3b's is `standing.proclamation_armed`
    (the Proclamation, armed by the user's word)."""
    if row == "AU-3b":
        from backend.game_logic import standing
        return bool(standing.proclamation_armed())
    if row == "AU-3a":
        from backend.game_logic import standing
        return bool(standing.buys_armed())
    if row == "AU-2a":
        from backend.game_logic import standing
        return bool(standing.hits_armed())
    if row == "AU-2b":
        from backend.game_logic import standing
        return bool(standing.sources_armed())
    if row == "AU-2c":
        from backend.game_logic import standing
        return bool(standing.letters_armed())
    return True


def entry_armed(e: Dict[str, Any]) -> bool:
    """AU-2c: a template authored `since` a row is in the deck only while
    that row is armed (the whole entry, not a clause of it)."""
    since = str((e or {}).get("since") or "")
    return not since or row_armed(since)


def op_armed(op: Dict[str, Any]) -> bool:
    """An op authored `since` a row is planned only while that row is armed."""
    since = str((op or {}).get("since") or "")
    return not since or row_armed(since)


def side_armed(side: Optional[Dict[str, Any]]) -> bool:
    """AU-3a: an answer authored `since` a row (the Edict letters' `decree`)
    is offered only while that row is armed — held out whole, as an entry is."""
    if not isinstance(side, dict) or not side:
        return False
    since = str(side.get("since") or "")
    return not since or row_armed(since)


def floor_mode(e: Dict[str, Any]) -> bool:
    """`bites` reads "floor" — the floor half alone — unless the clause is a
    row's (`bites_since`) held down, when it reads `true` (both halves)."""
    if (e or {}).get("bites") != BITES_FLOOR:
        return False
    since = str(e.get("bites_since") or "")
    return not since or row_armed(since)


def clamp_mode(e: Dict[str, Any]) -> bool:
    """`bites` reads "clamp" — the letter arrives at any standing; the floor
    is the plan's to keep, and the plan says what it kept."""
    return (e or {}).get("bites") == BITES_CLAMP

# The dispatch row an affair's set-aside and withdrawal lines ride — the
# moments' own receipt type (`moments.RECEIPT_EVENT`), named by its literal so
# the producer census (`test_fa_slice17_r…`) resolves the site.
RECEIPT_EVENT = "moment_receipt"

ARRIVED = (MO.STATUS_FIRED, MO.STATUS_ANSWERED, MO.STATUS_LAPSED)
# A withdrawn letter and a `passed(crowded)` row arm the cooldown (§11); only
# an arrival counts toward a cap.
COOLDOWN_STATUSES = ARRIVED + (MO.STATUS_WITHDRAWN, MO.STATUS_PASSED)
HOST_STATES = ("ALLIANCE", "DEFENSIVE_ALLIANCE")


# ════════════════════════════════════════════════════════════════════════
# The store
# ════════════════════════════════════════════════════════════════════════

def block(world) -> Dict[str, Any]:
    return MO.affairs_block(world)


def deck(world) -> List[Dict[str, Any]]:
    return MO.affairs_deck(world)


def armed(world) -> bool:
    return bool(deck(world))


def runtime(world) -> Dict[str, Any]:
    """The runtime store for a WRITER — created on first use of an ARMED
    world only, so an unarmed store is never touched. A pure read passes
    `runtime_read` (RE3-10's rule, AU-18)."""
    store = MO._store(world)
    rt = store.get("affairs")
    if not isinstance(rt, dict):
        rt = {}
        if store and armed(world):
            store["affairs"] = rt
    return rt


def runtime_read(world) -> Dict[str, Any]:
    """The runtime store read PURELY — never created (AU-18, BUG_FIXES.md §AU:
    the armed Proclamation's premise holds on the 1805 boot, so the boot
    briefing's Watch read its streak and its latch through `runtime`, which
    created `moments.affairs = {}` — the new world differed from a fresh one
    by it, EP-F1's rule; RE3-10 fixed the Watch's own write, these were its
    readers). A GET, the boot briefing and the Watch pass here."""
    rt = MO._store(world).get("affairs")
    return rt if isinstance(rt, dict) else {}


def _band(value: Any, default: int, band: Tuple[int, int]) -> Tuple[int, Tuple[int, int]]:
    if isinstance(value, dict):
        v = value.get("value", default)
        v = int(v) if isinstance(v, int) and not isinstance(v, bool) else default
        b = value.get("band")
        if (isinstance(b, (list, tuple)) and len(b) == 2
                and all(isinstance(x, int) and not isinstance(x, bool) for x in b)):
            return v, (int(b[0]), int(b[1]))
        return v, (v, v)
    if isinstance(value, int) and not isinstance(value, bool):
        return int(value), (int(value), int(value))
    return default, band


def pacing(world) -> Dict[str, Any]:
    """The pulse's numbers: `first` and `gap` with their bands, `cap_act`,
    `wait` — the authored values, else the spec's defaults."""
    authored = block(world).get("pacing") or {}
    if not isinstance(authored, dict):
        authored = {}
    out: Dict[str, Any] = {}
    for key in ("first", "gap"):
        out[key], out[key + "_band"] = _band(authored.get(key), PACING_DEFAULTS[key], PACING_BANDS[key])
    for key in ("cap_act", "wait"):
        v = authored.get(key)
        out[key] = int(v) if isinstance(v, int) and not isinstance(v, bool) else PACING_DEFAULTS[key]
    return out


def occurrences(world, template: str) -> List[Tuple[str, Dict[str, Any]]]:
    """The template's occurrence rows, (id, row), in store order."""
    prefix = str(template) + MO.OCCURRENCE_SEP
    return [(str(k), r) for k, r in MO._state(world).items()
            if isinstance(r, dict) and str(k).startswith(prefix)]


def all_occurrences(world) -> List[Tuple[str, Dict[str, Any]]]:
    return [(str(k), r) for k, r in MO._state(world).items()
            if isinstance(r, dict) and MO.is_occurrence(k)]


def row_subject(row: Dict[str, Any]) -> str:
    bind = row.get("bind") if isinstance(row.get("bind"), dict) else {}
    return str(bind.get("host") or "")


# ════════════════════════════════════════════════════════════════════════
# The seeds — timing only (§10)
# ════════════════════════════════════════════════════════════════════════

def _seed(world) -> str:
    return str(getattr(world, "campaign_seed", "") or "historical")


def pulse_first(world) -> int:
    """The first affair's morning: the authored value on `historical`, a
    seeded int in the band otherwise (namespace `affair::first`)."""
    from backend.game_logic.campaign_variance import is_historical, seeded_int
    rules = pacing(world)
    lo, hi = rules["first_band"]
    if is_historical(_seed(world)) or lo >= hi:
        return int(rules["first"])
    return int(seeded_int(_seed(world), "affair::first", lo, hi))


def pulse_gap(world, n: int) -> int:
    """The gap before the (n+1)th arrival, n the occurrence rows already in
    the store (derived, never stored): the value on `historical`, else a
    seeded int in the band (namespace `affair::gap::<n>`)."""
    from backend.game_logic.campaign_variance import is_historical, seeded_int
    rules = pacing(world)
    lo, hi = rules["gap_band"]
    if is_historical(_seed(world)) or lo >= hi:
        return int(rules["gap"])
    return int(seeded_int(_seed(world), f"affair::gap::{int(n)}", lo, hi))


# ════════════════════════════════════════════════════════════════════════
# The premises — (world, lord, params) → {holds, bind, measure, latch}
# ════════════════════════════════════════════════════════════════════════

def _no() -> Dict[str, Any]:
    return {"holds": False, "bind": {}, "measure": None, "latch": False}


def _sovereign_afield(world, lord: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """T1: the lord's standing sovereign — never a captive — stands outside
    its homeland (`nation_starting_regions`). The measure is the streak."""
    from backend.game_logic.fall import sovereign_of
    sovereign = sovereign_of(world, lord)
    if sovereign is None or getattr(sovereign, "captured_by", ""):
        return _no()
    home = set((getattr(world, "nation_starting_regions", {}) or {}).get(lord, []) or [])
    location = str(getattr(sovereign, "location", "") or "")
    if not location or location in home:
        return _no()
    return {"holds": True, "bind": {"region": location, "sovereign": str(sovereign.name)},
            "measure": None, "latch": False}


def _is_host(world, lord: str, court: str, vassals: Dict[str, Any]) -> bool:
    row = vassals.get(court)
    if isinstance(row, dict) and row.get("lord") == lord:
        return True
    return world.get_diplomatic_state(lord, court) in HOST_STATES


def _corps_on_host(world, lord: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """T2: `min_corps` or more of the lord's corps — the sovereign, captives
    and a client's contingent commander not counted — stand on an ally's or
    a client's soil. One pass over the marshal list (Rule 8); the host with
    the most corps, ties by the active-nation order. The measure is the
    corps count."""
    min_corps = int(params.get("min_corps", 2) or 2)
    regions = getattr(world, "regions", {}) or {}
    vassals = getattr(world, "vassals", {}) or {}
    contingents = {str(r.get("marshal") or "") for r in
                   (getattr(world, "vassal_contingents", None) or {}).values() if isinstance(r, dict)}
    counts: Dict[str, int] = {}
    for m in (getattr(world, "marshals", {}) or {}).values():
        if (getattr(m, "nation", "") != lord or getattr(m, "is_sovereign", False)
                or getattr(m, "captured_by", "") or getattr(m, "name", "") in contingents):
            continue
        region = regions.get(str(getattr(m, "location", "") or ""))
        host = str(getattr(region, "controller", "") or "") if region is not None else ""
        if not host or host == lord or not _is_host(world, lord, host, vassals):
            continue
        counts[host] = counts.get(host, 0) + 1
    if not counts:
        return _no()
    order = {n: i for i, n in enumerate(world.get_active_nations())}
    host = min(counts, key=lambda h: (-counts[h], order.get(h, 10 ** 6), h))
    if counts[host] < min_corps:
        return _no()
    return {"holds": True, "bind": {"host": host}, "measure": int(counts[host]), "latch": False}


def _staff_offered(world, lord: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """T3: at war, the named law not in force with `reforms.law_refusal`
    open, and the purse at or above the price plus the AI's own reserve and
    upkeep turns — one source with the AI's law rung. The measure is the
    streak (turns at war)."""
    from backend.game_logic import reforms
    from backend.game_logic.instruments import purse_of
    law_id = str(params.get("law") or "")
    row = reforms.find_law(world, lord, law_id)
    if row is None or reforms.is_in_force(row):
        return _no()
    try:
        at_war = bool(world.get_nations_at_war_with(lord))
    except Exception as exc:
        report(exc, "affairs._staff_offered: world.get_nations_at_war_with")
        at_war = False
    if not at_war or reforms.law_refusal(world, lord, law_id):
        return _no()
    price = int(row.get("price", 0) or 0)
    upkeep = int(row.get("upkeep", 0) or 0)
    bar = price + int(reforms.AI_PURSE_RESERVE) + int(reforms.AI_PURSE_UPKEEP_TURNS) * upkeep
    if int(purse_of(world, lord)[1]) < bar:
        return _no()
    return {"holds": True, "bind": {"law": law_id}, "measure": None, "latch": False}


def _colony_cut_off(world, lord: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """H1 the Haiti letter (§6.5, P7): the LATCH bit first — the lord
    blockaded this morning by the trade-dominant power (`naval.is_blockaded`
    against `naval.trade_dominance_nation`), returned whether or not the rest
    holds so `update_morning` shifts the 12-bit mask — then the sovereign
    standing, not a captive, WHEREVER HE IS (the Marine's dispatches reached
    the Emperor in the field — the user's word of November 1, 2026, "let
    Decrès write to headquarters"; the October 30 at-home clause is dropped,
    the pulse's gap keeps H1 and T1 apart, and the board says whether the
    letter found him at court or at headquarters), at least `min_ships` sail
    in port and the purse at or above `min_purse` + the AI's own reserve. No region
    scan (Rule 8): one marshal, one fleet record, one purse read."""
    from backend.game_logic import naval
    from backend.game_logic.fall import sovereign_of
    from backend.game_logic.instruments import purse_of
    from backend.game_logic.reforms import AI_PURSE_RESERVE
    out = _no()
    if not naval.has_naval_layer(world):
        return out
    dominant = naval.trade_dominance_nation(world)
    blockader, _coverage = naval.blockader_against(world, lord)
    out["latch"] = bool(dominant) and blockader == dominant
    sovereign = sovereign_of(world, lord)
    if sovereign is None or getattr(sovereign, "captured_by", ""):
        return out
    location = str(getattr(sovereign, "location", "") or "")
    rec = naval.get_fleet(world, lord) or {}
    if int(rec.get("ships", 0) or 0) < int(params.get("min_ships", 25) or 25):
        return out
    if int(purse_of(world, lord)[1]) < int(params.get("min_purse", 500) or 500) + int(AI_PURSE_RESERVE):
        return out
    out.update({"holds": True, "bind": {"region": location, "sovereign": str(sovereign.name)},
                "measure": None})
    return out


def _template_by_id(world, template: str) -> Optional[Dict[str, Any]]:
    """The affairs template with this id, or None (an offer names its own
    entry in `when.edict`, as the door names its law)."""
    for e in deck(world):
        if str(e.get("id") or "") == str(template or ""):
            return e
    return None


def _offer_entry(world, lord: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """RE-6: the offers' shared clause — the named template with its `edict`
    block, available (not in force, not resting) and within the purse at
    the laws rung's own bar — one source with the courts' rung
    (`edict_refusal`); None when any clause fails."""
    e = _template_by_id(world, str(params.get("edict") or ""))
    if e is None:
        return None
    if edict_currency(e) == "authority":
        # AU-3b: an edict priced in authority alone (the Proclamation) arrives
        # only where its price could land — the purchases' floor at the
        # recency rise; a court's road rides the courts' flip (AU-14, arm AUC)
        return None if edict_refusal(world, lord, e, currency="authority") else e
    if edict_refusal(world, lord, e, with_reserve=True):
        # AU-3a (§5.7): a court may decree at its own floors where the gold
        # refuses; the player's letter stays gold-gated — it arrives where it
        # arrived, the Decree a second purse on it (§6.5 reading 1)
        if lord == getattr(world, "player_nation", None) or edict_refusal(world, lord, e, currency="authority"):
            return None
    return e


def _corps_on_campaign_pay(world, lord: str) -> int:
    """E1: the lord's corps drawing campaign pay this morning — the bill's
    own predicate (`campaign_pay_homeland` / `campaign_pay_at`), one pass
    over the marshal list (Rule 8); 0 at peace (the homeland read is None)."""
    homeland = world.campaign_pay_homeland(lord) if hasattr(world, "campaign_pay_homeland") else None
    if homeland is None:
        return 0
    count = 0
    for m in (getattr(world, "marshals", {}) or {}).values():
        if getattr(m, "nation", "") != lord or getattr(m, "captured_by", ""):
            continue
        due = world.campaign_pay_at(lord, str(getattr(m, "location", "") or ""),
                                    int(getattr(m, "strength", 0) or 0), homeland)
        if due:
            count += 1
    return count


def _storm_gathering(world, lord: str) -> bool:
    """E1's second clause: for the player, a coalition brewing against the
    lord and not yet formed (the dispatch gauge's "Brewing" tier —
    `coalition.brewing_gate`); for a court, a war-intent record in tenure
    whose target is the lord (those records are court-against-court only)."""
    if lord == getattr(world, "player_nation", None):
        from backend.game_logic.coalition import brewing_gate
        formed = getattr(world, "active_coalition", None)
        if isinstance(formed, dict) and formed.get("target_nation") == lord:
            return False
        return int(getattr(world, "threat_level", 0) or 0) >= int(brewing_gate(world, lord))
    from backend.game_logic.war_council import record_in_tenure
    turn = MO._turn(world)
    return any(isinstance(r, dict) and r.get("target") == lord and record_in_tenure(r, turn)
               for r in (getattr(world, "war_intents", {}) or {}).values())


def _magazines_wanted(world, lord: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """E1 the Magazines: at war with a corps drawing campaign pay, or the
    storm gathering; then the offers' shared clause. The measure is the
    corps on campaign pay (the streak is the watch's `{m}`)."""
    if _offer_entry(world, lord, params) is None:
        return _no()
    corps = _corps_on_campaign_pay(world, lord)
    if corps <= 0 and not _storm_gathering(world, lord):
        return _no()
    return {"holds": True, "bind": {}, "measure": int(corps), "latch": False}


def _weakest_cavalry_corps_pct(world, lord: str) -> int:
    """E2's second clause: the lord's weakest cavalry corps as a percent of
    its establishment (`starting_strength`) — the horse lost on campaign;
    100 when the lord has no cavalry corps. One pass over the marshal list
    (Rule 8)."""
    weakest = 100
    for m in (getattr(world, "marshals", {}) or {}).values():
        if (getattr(m, "nation", "") != lord or getattr(m, "captured_by", "")
                or not getattr(m, "cavalry", False)):
            continue
        establishment = int(getattr(m, "starting_strength", 0) or 0)
        if establishment <= 0:
            continue
        weakest = min(weakest, int(getattr(m, "strength", 0) or 0) * 100 // establishment)
    return max(0, weakest)


def _remounts_wanted(world, lord: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """E2 the Remounts: the lord's cavalry pool under `below_pct` of the one
    cap (`MAX_CAVALRY_POOL`, the stables rung's own 60 %), OR a cavalry corps
    under `below_pct` of its establishment (the measure found the pool alone
    reached no board — 0 of 55 arms, the six hand-played boards at the cap;
    the horse is lost on campaign, not in the depots); then the shared
    clause. The measure is the weaker of the two percents."""
    if _offer_entry(world, lord, params) is None:
        return _no()
    from backend.models.world_state import MAX_CAVALRY_POOL
    pool = int(((getattr(world, "manpower_pools", {}) or {}).get(lord) or {}).get("cavalry", 0) or 0)
    cap = max(1, int(MAX_CAVALRY_POOL))
    below = int(params.get("below_pct", 60) or 60)
    measure = min(int(pool * 100 // cap), _weakest_cavalry_corps_pct(world, lord))
    if measure >= below:
        return _no()
    return {"holds": True, "bind": {}, "measure": int(measure), "latch": False}


def _camps_wanted(world, lord: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """E3 the Camps of Instruction: at peace with every other great power
    and the Charges' rate carrying the crown term alone (no war
    establishment, no war exhaustion left, no ill war, no pensions of the
    fallen — the golden peace); then the shared clause. The measure is the
    streak (the template's six mornings)."""
    if _offer_entry(world, lord, params) is None:
        return _no()
    from backend.game_logic.reforms import GREAT_POWERS
    for power in GREAT_POWERS:
        if power != lord and world.get_diplomatic_state(lord, power) == "WAR":
            return _no()
    terms = (world.get_state_charges_rate(lord) or {}).get("terms") or []
    if {str(t.get("key") or "") for t in terms if isinstance(t, dict)} - {"crown"}:
        return _no()
    return {"holds": True, "bind": {}, "measure": None, "latch": False}


def _enemy_within_a_march(world, lord: str) -> Optional[Tuple[str, str]]:
    """AU-3b re-premised (the user's "Re-premise it first", November 5, 2026):
    an enemy army SEEN — PARTIAL or better, `world.get_visible_enemies`, never
    the omniscient list — in the Emperor's own province or one march from it;
    (that marshal, his province), or None. One marshal list and one
    province's neighbours (Rule 8)."""
    from backend.game_logic.fall import sovereign_of
    sovereign = sovereign_of(world, lord)
    if sovereign is None or getattr(sovereign, "captured_by", ""):
        return None
    here = str(getattr(sovereign, "location", "") or "")
    region = (getattr(world, "regions", {}) or {}).get(here)
    if region is None:
        return None
    near = {here, *[str(r) for r in (getattr(region, "adjacent_regions", None) or [])]}
    # AU-4: the lord's own sight — the player's fog for the player; a court's
    # live sight for a court (`get_visible_enemies` reads the player's intel)
    seen = (world.get_visible_enemies(lord) if lord == getattr(world, "player_nation", None)
            else world.get_live_visible_enemies(lord))
    for m in seen:
        if (int(getattr(m, "strength", 0) or 0) > 0 and not getattr(m, "captured_by", "")
                and str(getattr(m, "location", "") or "") in near):
            return str(m.name), str(m.location)
    return None


def _proclamation_wanted(world, lord: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """AU-3b the Proclamation (AUTHORITY_CURRENCY_SPEC.md §5.3, §6.6), re-premised
    on the eve of battle (the user's "Re-premise it first", November 5, 2026 —
    on the Emperor afield it lost every pulse to the Chancellor's older letter
    on the same fact): the LATCH bit first — an enemy army seen within a march
    of the Emperor this morning (`_enemy_within_a_march`, fog-safe), returned
    whether or not the rest holds so `update_morning` shifts the mask (the
    Haiti idiom: an army that slips out of sight for a morning keeps its
    count); then the premise proper — at war, the price able to land (the
    shared clause on the decree's own purse: the purchases' floor at the
    recency rise). It binds nothing — the board reads the field live. The
    streak counts the war; the latch, the battle's approach."""
    out = _no()
    out["latch"] = _enemy_within_a_march(world, lord) is not None
    if _offer_entry(world, lord, params) is None:
        return out
    if not _at_war(world, lord, "_proclamation_wanted"):
        return out
    out.update({"holds": True, "bind": {}, "measure": None})
    return out


def _at_war(world, lord: str, where: str) -> bool:
    try:
        return bool(world.get_nations_at_war_with(lord))
    except Exception as exc:
        report(exc, f"affairs.{where}: world.get_nations_at_war_with")
        return False


def _chest_strained(world, lord: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """AU-2c the Bank's Panic (AUTHORITY_CURRENCY_SPEC.md §5.4): the chest
    strained at war. The LATCH bit first — at war, the ledger's forecast Net
    (`ledger.chest_forecast`, THE one projection of the chest after this
    turn) in deficit deep enough to empty the chest within `within` turns —
    returned whether or not the rest holds, so `update_morning` shifts the
    12-bit mask (the Haiti letter's idiom: a strain that eases for a morning
    keeps its count, where a premise of the deficit itself reset its streak
    and lost every pulse to the older matters — 0 arrivals on 55 runs, §6.4);
    then the premise proper: at war, the purse at or above `min_purse` + the
    AI's own reserve (the Accept payable). A rich chest in deficit does not
    strain — the Charges draw more from a fuller chest by design (EB-1). The
    forecast walks the lord's own provinces only, as the ledger does each
    morning (Rule 8)."""
    from backend.game_logic.instruments import purse_of
    from backend.game_logic.reforms import AI_PURSE_RESERVE
    out = _no()
    if not _at_war(world, lord, "_chest_strained"):
        return out
    from backend.game_logic.ledger import chest_forecast
    forecast = chest_forecast(world, lord)
    chest, net = int(forecast.get("chest", 0) or 0), int(forecast.get("net", 0) or 0)
    out["latch"] = net < 0 and chest + int(params.get("within", 20) or 20) * net < 0
    if int(purse_of(world, lord)[1]) < int(params.get("min_purse", 1000) or 1000) + int(AI_PURSE_RESERVE):
        return out
    out.update({"holds": True, "measure": None})
    return out


def _ports_defied(world, lord: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """AU-2c the Pope's Refusal (§5.4; the user's word of November 4, 2026,
    "War with Britain" — the Berlin Decree's premise never held on a measured
    run): the lord at war with the trade-dominant power
    (`naval.trade_dominance_nation`, the Haiti letter's own read), the named
    `court` standing — active, neither the lord's client nor at war with him,
    outside the System (`continental_system_members`) — and the purse at or
    above `min_purse` + the AI's own reserve. The measure is the streak. A
    handful of state lookups, no region scan (Rule 8)."""
    from backend.game_logic import naval
    from backend.game_logic.instruments import purse_of
    from backend.game_logic.reforms import AI_PURSE_RESERVE
    court = str(params.get("court") or "")
    target = naval.trade_dominance_nation(world)
    if not court or court == lord or not target or not world.is_at_war(lord, target):
        return _no()
    if court not in world.get_active_nations():
        return _no()
    row = (getattr(world, "vassals", {}) or {}).get(court)
    if isinstance(row, dict) and row.get("lord") == lord:
        return _no()
    if world.get_diplomatic_state(lord, court) == "WAR":
        return _no()
    if court in (getattr(world, "continental_system_members", None) or []):
        return _no()
    if int(purse_of(world, lord)[1]) < int(params.get("min_purse", 800) or 800) + int(AI_PURSE_RESERVE):
        return _no()
    return {"holds": True, "bind": {}, "measure": None, "latch": False}


PREDICATES: Dict[str, Callable[[Any, str, Dict[str, Any]], Dict[str, Any]]] = {
    "sovereign_afield": _sovereign_afield,
    "corps_on_host": _corps_on_host,
    "staff_offered": _staff_offered,
    "colony_cut_off": _colony_cut_off,
    # RE-6: the Edicts' offers (§6.2 E1–E3)
    "magazines_wanted": _magazines_wanted,
    "remounts_wanted": _remounts_wanted,
    "camps_wanted": _camps_wanted,
    # AU-3b: the Proclamation, an Edict priced in authority (AUTHORITY_CURRENCY_SPEC.md §5.3)
    "proclamation_wanted": _proclamation_wanted,
    # AU-2c: the Bank's Panic and the Pope's Refusal (AUTHORITY_CURRENCY_SPEC.md §5.4)
    "chest_strained": _chest_strained,
    "ports_defied": _ports_defied,
}
# The parameters each predicate requires (the validator reads them).
PREDICATE_PARAMS: Dict[str, Tuple[str, ...]] = {
    "sovereign_afield": (),
    "corps_on_host": (),
    "staff_offered": ("law",),
    "colony_cut_off": (),
    "magazines_wanted": ("edict",),
    "remounts_wanted": ("edict",),
    "camps_wanted": ("edict",),
    "proclamation_wanted": ("edict",),
    "chest_strained": ("within", "min_purse"),
    "ports_defied": ("court", "min_purse"),
}
OFFER_PREDICATES = ("magazines_wanted", "remounts_wanted", "camps_wanted", "proclamation_wanted")
# The predicates whose `watch` and board count a LATCH (`{n}` = the set bits
# of the mask) rather than a streak or a corps count.
LATCHED_PREDICATES = ("colony_cut_off", "chest_strained", "proclamation_wanted")


def _lord_of(world, e: Dict[str, Any]) -> str:
    """v1 authors every template `owner` (Q4); `any_lord` is RE-4's."""
    return MO.owner(world)


def _memo(world) -> Dict[Tuple[str, str], Dict[str, Any]]:
    """The per-turn memo on the world object (an underscore attribute: never
    serialized, never a module dict — a reload starts it empty)."""
    turn = MO._turn(world)
    memo = world.__dict__.get("_affairs_memo")
    if not isinstance(memo, dict) or memo.get("turn") != turn:
        memo = {"turn": turn, "reads": {}}
        world.__dict__["_affairs_memo"] = memo
    return memo["reads"]


def premise_holds(world, e: Dict[str, Any], lord: str) -> Dict[str, Any]:
    """The premise's reading this morning, memoised per (turn, template,
    lord) — {holds, bind, measure, latch}; the trace wraps it."""
    reads = _memo(world)
    key = (str(e.get("id") or ""), str(lord))
    if key in reads:
        return reads[key]
    when = e.get("when") or {}
    fn = PREDICATES.get(str(when.get("predicate") or ""))
    out = _no()
    if fn is not None:
        try:
            out = fn(world, lord, when) or _no()
        except Exception as exc:
            report(exc, "affairs.premise_holds: the predicate")
            out = _no()
    reads[key] = out
    return out


def subject_of(read: Dict[str, Any]) -> str:
    """The subject a streak, a cooldown and a cap are kept per: the bound
    host, else "" (the lord's own)."""
    bind = read.get("bind") if isinstance(read.get("bind"), dict) else {}
    return str(bind.get("host") or "")


def _streak_key(template: str, subject: str) -> str:
    return f"{template}{SUBJECT_SEP}{subject}"


def update_morning(world) -> None:
    """Once a morning (keyed to the turn): every template's streak per
    subject — +1 while the premise holds, reset otherwise, another subject's
    streak of the same template reset — and its latch mask shifted."""
    if not armed(world):
        return
    rt = runtime(world)
    turn = MO._turn(world)
    if int(rt.get("morning", -1)) == turn:
        return
    rt["morning"] = turn
    streaks = rt.setdefault("streaks", {})
    masks = rt.setdefault("masks", {})
    for e in deck(world):
        template = str(e["id"])
        read = premise_holds(world, e, _lord_of(world, e))
        prefix = template + SUBJECT_SEP
        key = _streak_key(template, subject_of(read))
        for other in [k for k in streaks if k.startswith(prefix) and (k != key or not read.get("holds"))]:
            streaks.pop(other, None)
        if read.get("holds"):
            streaks[key] = int(streaks.get(key, 0)) + 1
        latch = e.get("latch")
        if isinstance(latch, dict):
            of = max(1, min(LATCH_OF_MAX, int(latch.get("of", 12) or 12)))
            masks[template] = ((int(masks.get(template, 0)) << 1) | (1 if read.get("latch") else 0)) \
                & ((1 << of) - 1)


def streak_of(world, e: Dict[str, Any], subject: str) -> int:
    return int((runtime_read(world).get("streaks") or {}).get(_streak_key(str(e["id"]), subject), 0))


def latch_count(world, e: Dict[str, Any]) -> int:
    """P7: the set bits of the template's mask — the mornings of the last
    `of` the latch read true (the Haiti letter's "blockaded {n} of the last
    12 mornings")."""
    if not isinstance(e.get("latch"), dict):
        return 0
    mask = int((runtime_read(world).get("masks") or {}).get(str(e["id"]), 0))
    return bin(mask).count("1")


def latch_ok(world, e: Dict[str, Any]) -> bool:
    """P7: a template with a `latch` arrives only while its mask carries at
    least `at_least` set bits of the last `of` mornings."""
    latch = e.get("latch")
    if not isinstance(latch, dict):
        return True
    return latch_count(world, e) >= int(latch.get("at_least", 1) or 1)


def latch_distance(world, e: Dict[str, Any]) -> int:
    """How many more mornings the latch needs — 0 for a template without one."""
    latch = e.get("latch")
    if not isinstance(latch, dict):
        return 0
    return max(0, int(latch.get("at_least", 1) or 1) - latch_count(world, e))


# ════════════════════════════════════════════════════════════════════════
# Tiers, `bites`, cooldowns and caps
# ════════════════════════════════════════════════════════════════════════

def tier_of(e: Dict[str, Any], measure: int) -> int:
    """§5 `scale`: {measure, from, step, max} → 1 + (measure − from) // step,
    clamped to [1, max]; {measure, at, then} → tier `then` once measure ≥ at."""
    scale = e.get("scale")
    if not isinstance(scale, dict):
        return 1
    measure = int(measure or 0)
    if "at" in scale:
        then = int(scale.get("then", 2) or 2)
        return max(1, min(SCALE_MAX_TIER, then)) if measure >= int(scale.get("at", 0) or 0) else 1
    start = int(scale.get("from", 0) or 0)
    step = max(1, int(scale.get("step", 1) or 1))
    top = max(1, min(SCALE_MAX_TIER, int(scale.get("max", SCALE_MAX_TIER) or SCALE_MAX_TIER)))
    return max(1, min(top, 1 + (measure - start) // step))


def bites(world, lord: str, e: Dict[str, Any], tier: int) -> bool:
    """§6.1: an `authority`-priced template arrives only where the price
    BITES — the Decline's tiered loss lands below the aura's full line (85)
    on the grip, and the floor (71) allows it whole. A template priced in no
    authority always bites; a lord without a tracker never does.

    RE-H (the user's word of November 1, 2026; §0b P16 amended): a template
    authored `bites: "floor"` asks the floor half alone — the loss must land
    whole above the floor — so the Haiti letter arrives at full standing,
    where the Decline is a dent and the squadron the stake.

    AU-2a, the user's "Clamp it first" (November 4, 2026): a template authored
    `bites: "clamp"` asks neither — the Host's Claims arrive on the bled boards
    too, and the plan takes what lies above the floor and says the rest."""
    ops = [MO.scaled_op(op, tier) for op in ((e.get("decline") or {}).get("ops") or [])
           if isinstance(op, dict) and op.get("op") == "authority" and op_armed(op)]
    if not ops:
        return True
    if lord != getattr(world, "player_nation", None) or getattr(world, "authority_tracker", None) is None:
        return False
    if clamp_mode(e):
        return True
    from backend.models.authority import AURA_GRIP_FULL, get_imperial_grip
    floor_only = floor_mode(e)
    grip = int(get_imperial_grip(world, lord))
    for op in ops:
        after = grip + int(op.get("amount", 0) or 0)
        if after < MO.AUTHORITY_GRIP_FLOOR or (after >= AURA_GRIP_FULL and not floor_only):
            return False
    return True


def _act_start(world, turn: int) -> int:
    """The act's first morning: 0, or the Verdict's turn once the deck runs
    on past it (Q12: the caps reset there, a second act)."""
    from backend.game_logic import game_end
    verdict = game_end.verdict_turn(world)
    return int(verdict) if verdict is not None and turn >= int(verdict) else 0


def on_cooldown(world, e: Dict[str, Any], subject: str, turn: int) -> bool:
    """The template's cooldown per subject, derived from its rows: from the
    arrival, or from the withdrawal of a letter withdrawn free (re-armed)."""
    cooldown = int(e.get("cooldown", 12) or 12)
    last = [int(r.get("withdrawn_turn", r.get("turn", 0)) or 0) for _k, r in occurrences(world, str(e["id"]))
            if r.get("status") in COOLDOWN_STATUSES and row_subject(r) == subject]
    return bool(last) and turn - max(last) < cooldown


def under_cap(world, e: Dict[str, Any], subject: str, turn: int) -> bool:
    cap = int(e.get("cap", 2) or 2)
    start = _act_start(world, turn)
    n = sum(1 for _k, r in occurrences(world, str(e["id"]))
            if r.get("status") in ARRIVED and row_subject(r) == subject
            and int(r.get("turn", 0) or 0) >= start)
    return n < cap


def act_count(world, turn: int) -> int:
    start = _act_start(world, turn)
    return sum(1 for _k, r in all_occurrences(world)
               if r.get("status") in ARRIVED and int(r.get("turn", 0) or 0) >= start)


# ════════════════════════════════════════════════════════════════════════
# The morning — the candidates, the pulse, the pick, the delivery (§7)
# ════════════════════════════════════════════════════════════════════════

def candidates(world, turn: int) -> List[Dict[str, Any]]:
    """Every template DUE this morning: premise held for its streak, latch
    satisfied, road open, before `ends`, `bites`, off cooldown, under cap —
    with its lord, subject, streak, measure, tier and bind."""
    out: List[Dict[str, Any]] = []
    for index, e in enumerate(deck(world)):
        lord = _lord_of(world, e)
        read = premise_holds(world, e, lord)
        if not read.get("holds"):
            continue
        subject = subject_of(read)
        streak = streak_of(world, e, subject)
        if streak < int(e.get("streak", 1) or 1) or not latch_ok(world, e):
            continue
        if MO.road_gate(world, e) != MO.GATE_OPEN:
            continue
        ends = e.get("ends")
        if isinstance(ends, dict) and turn > int(ends.get("turn", 10 ** 6) or 10 ** 6):
            continue
        measure = read.get("measure")
        measure = streak if measure is None else int(measure)
        tier = tier_of(e, measure)
        if not bites(world, lord, e, tier):
            continue
        if on_cooldown(world, e, subject, turn) or not under_cap(world, e, subject, turn):
            continue
        out.append({"e": e, "lord": lord, "subject": subject, "streak": streak, "measure": measure,
                    "tier": tier, "bind": dict(read.get("bind") or {}), "index": index})
    return out


def moment_imminent(world, turn: int) -> bool:
    """P8 — the look-ahead: a pending DATED moment whose window opens within
    `LOOK_AHEAD` mornings, its premise true and its road open. The moments
    stay blind; this keeps a T7 affair from being withdrawn by the T8 Match."""
    state = MO._state(world)
    for e in MO.deck(world):
        if str(e.get("id")) in state or e.get("lag") is not None:
            continue
        span = MO.window(world, e)
        if span is None:
            continue
        lo = int(span[0])
        if turn < lo <= turn + LOOK_AHEAD and MO.road_gate(world, e) == MO.GATE_OPEN \
                and MO.premise(world, e):
            return True
    return False


def pulse_block(world, turn: int) -> str:
    """Why the PULSE keeps the deck silent this morning — "" when the deck
    may speak: the act's cap, the gap since the last arrival of either deck,
    the look-ahead (P8). The pulse decides WHEN; a matter it holds back is
    not waiting on a busy desk, so it is never crowded out by it."""
    if act_count(world, turn) >= int(pacing(world)["cap_act"]):
        return "cap_act"
    state = MO._state(world)
    arrivals = [int(r.get("turn", 0) or 0) for k, r in state.items() if isinstance(r, dict)
                and (r.get("status") in ARRIVED
                     or (MO.is_occurrence(k) and r.get("status") == MO.STATUS_WITHDRAWN))]
    if arrivals and turn - max(arrivals) < pulse_gap(world, len(all_occurrences(world))):
        return "gap"
    if moment_imminent(world, turn):
        return "look_ahead"
    return ""


def desk_block(world, delivered: Optional[List[str]]) -> str:
    """Why the DESK is busy this morning — "" when the Emperor can be
    reached: a moment arrived this morning (R3), a letter of either kind
    stands, a foregrounded crisis (R1). A matter due by the pulse that meets
    a busy desk waits, and is crowded out past its grace (§7)."""
    if delivered:
        return "arrived"
    state = MO._state(world)
    if any(isinstance(r, dict) and r.get("status") == MO.STATUS_FIRED for r in state.values()):
        return "open"
    from backend.game_logic.war_council import foreground_in_tenure
    if foreground_in_tenure(world):
        return "crisis"
    return ""


def _last_template(world) -> str:
    """The template of the most recent arrival (the one set behind)."""
    rows = [(int(r.get("turn", 0) or 0), MO.template_of(k)) for k, r in all_occurrences(world)
            if r.get("status") in ARRIVED + (MO.STATUS_WITHDRAWN,)]
    return max(rows)[1] if rows else ""


def pick(world, cands: List[Dict[str, Any]], turn: int) -> Optional[Dict[str, Any]]:
    """Which affair (§7): the premise that has stood longest; ties by
    `seeded_tiebreak` (authored order on `historical`); the last-arrived
    template set behind the others — never barred when it stands alone (its
    cooldown already spaces it)."""
    if not cands:
        return None
    last = _last_template(world)
    pool = [c for c in cands if str(c["e"]["id"]) != last] or list(cands)
    best = max(int(c["streak"]) for c in pool)
    top = [c for c in pool if int(c["streak"]) == best]
    if len(top) == 1:
        return top[0]
    from backend.game_logic.campaign_variance import seeded_tiebreak
    keys = [_streak_key(str(c["e"]["id"]), c["subject"]) for c in top]
    chosen = seeded_tiebreak(_seed(world), f"affair::tie::{int(turn)}", keys)
    return top[keys.index(chosen)]


def _short(bind: Dict[str, Any]) -> Dict[str, str]:
    return {str(k)[:32]: str(v)[:40] for k, v in (bind or {}).items() if v not in (None, "")}


def requirement_holds(world, lord: str, name: str) -> bool:
    """A form's `requires`, read live: `hunter_at_sea` — an enemy fleet in
    blockade posture at war with the lord would hunt a squadron sailing alone
    (`naval.squadron_hunter`). An unknown name never holds."""
    if name == "hunter_at_sea":
        from backend.game_logic import naval
        try:
            return bool(naval.squadron_hunter(world, lord))
        except Exception as exc:
            report(exc, "affairs.requirement_holds: naval.squadron_hunter")
            return False
    return False


def form_of(world, e: Dict[str, Any], cand: Dict[str, Any]) -> str:
    """P18: the form frozen at delivery — the first authored form whose
    `requires` holds (the squadron when a hunter is at sea), else the first
    form without a requirement (the bill); "" for an entry with none. A
    standing letter never changes form: `refresh_letter` re-plans the frozen
    form, and a hunter that vanished closes the Accept with the refusal."""
    forms = e.get("forms")
    if not isinstance(forms, dict) or not forms:
        return ""
    lord = str(cand.get("lord") or _lord_of(world, e))
    fallback = ""
    for name, form in forms.items():
        requires = str((form or {}).get("requires") or "") if isinstance(form, dict) else ""
        if requires:
            if requirement_holds(world, lord, requires):
                return str(name)
        elif not fallback:
            fallback = str(name)
    return fallback or str(next(iter(forms)))


def _next_id(world, template: str) -> str:
    return f"{template}{MO.OCCURRENCE_SEP}{len(occurrences(world, template)) + 1}"


def _deliver(world, cand: Dict[str, Any], turn: int) -> str:
    e = cand["e"]
    mid = _next_id(world, str(e["id"]))
    row: Dict[str, Any] = {"id": mid, "lord": str(cand["lord"]), "bind": _short(cand["bind"]),
                           "tier": int(cand["tier"])}
    form = form_of(world, e, cand)
    if form:
        row["form"] = form
    # RE-H (P18): the last squadron's fate, frozen into the row at delivery —
    # the chapter and the board line read the row, never the live record
    from backend.game_logic import naval
    last = naval.last_squadron(world, str(cand["lord"]))
    if last and str(last.get("outcome") or "") in OUTCOMES:
        row["last_fate"] = str(last["outcome"])
        row["last_sailed"] = int(last.get("sailed", 0) or 0)
        row["last_ships"] = int(last.get("ships", 0) or 0)
    MO.deliver_letter(world, e, turn, mid=mid, row=row)
    return mid


def write_receipt(world, line: str) -> None:
    """Seam AFN — the rows and notices: one `moment_receipt` dispatch line
    (the set-aside tally, a withdrawal). RE-3 (BUG_FIXES RE3-1): the row
    names its register, so the sweep never counts an affair's receipt as a
    moment crowded out."""
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, RECEIPT_EVENT, {"line": str(line), "register": KIND_AFFAIR}, "always")


def _crowd_out(world, cand: Dict[str, Any], turn: int) -> str:
    """§7: a due affair still waiting after its grace writes a
    `passed(crowded)` occurrence row — not an arrival (no gap moves), the
    cooldown armed — and, when its Watch line had shown, joins the
    aggregated set-aside line (at most one in six turns)."""
    e = cand["e"]
    mid = _next_id(world, str(e["id"]))
    MO._state(world)[mid] = {"id": mid, "status": MO.STATUS_PASSED, "reason": MO.PASS_CROWDED,
                             "turn": int(turn), "lord": str(cand["lord"]),
                             "bind": _short(cand["bind"]), "tier": int(cand["tier"])}
    MO._log(world, "passed", e, reason=MO.PASS_CROWDED,
            line=f"{title_of(e, {})} was set aside by the Secretariat",
            lord=str(cand["lord"]), register=MO.REGISTER_AFFAIR, occurrence=mid)
    rt = runtime(world)
    if str(e["id"]) in (rt.get("watched") or {}):
        tally = rt.setdefault("set_aside", {"count": 0, "turn": 0})
        tally["count"] = int(tally.get("count", 0)) + 1
        if turn - int(tally.get("turn", 0)) >= SET_ASIDE_EVERY:
            n = int(tally["count"])
            write_receipt(world, f"The Secretariat set aside {n} matter{'' if n == 1 else 's'}")
            tally["count"], tally["turn"] = 0, int(turn)
    return mid


def deliver_due(world, delivered: Optional[List[str]] = None) -> List[str]:
    """Seam AF0 — the morning's affair, called from `moments.tick` AFTER
    `_tick` returns (which returns early on a morning with no moment
    candidate). Unarmed: []. Before the pulse's first morning: the streaks
    build and nothing is due. Otherwise: the matters due this morning
    (`candidates`); the pulse (`pulse_block`) decides whether the deck may
    speak at all; the desk (`desk_block`) whether the Emperor can be reached.
    Both open: the pick arrives. The pulse open and the desk busy — or
    another matter took the morning (R3) — a due matter WAITS: its mark
    counts the busy mornings, and past its grace (default `pacing.wait`) it
    is crowded out (§7). The pulse closed: nothing waits and nothing ages."""
    if not armed(world):
        return []
    turn = MO._turn(world)
    update_morning(world)
    rt = runtime(world)
    if turn < max(pulse_first(world), int(rt.get("not_before", 0) or 0)):
        return []
    cands = candidates(world, turn)
    pulse_open = not pulse_block(world, turn)
    desk_free = not desk_block(world, delivered)
    chosen = pick(world, cands, turn) if (pulse_open and desk_free) else None
    due = rt.setdefault("due", {})
    wait = int(pacing(world)["wait"])
    live: set = set()
    out: List[str] = []
    for c in cands:
        key = _streak_key(str(c["e"]["id"]), c["subject"])
        live.add(key)
        if chosen is not None and c is chosen:
            out.append(_deliver(world, c, turn))
            due.pop(key, None)
            continue
        if not pulse_open:
            continue                # held by the pulse, not by a busy desk
        waited = int(due.get(key, 0)) + 1
        grace = int(c["e"].get("grace", wait) or wait)
        if waited > grace:
            _crowd_out(world, c, turn)
            due.pop(key, None)
        else:
            due[key] = waited
    for key in [k for k in due if k not in live]:
        due.pop(key, None)          # no longer due: the Watch said "may"
    return out


def withdraw_standing(world, delivered: Optional[List[str]]) -> List[str]:
    """§7: a moment delivered this morning while an affair letter stands —
    the affair is withdrawn FREE: its dialogue popped, its notice dismissed,
    its row `withdrawn` (nothing applied; the cooldown re-armed), one
    dispatch line; the moment's popup slot is then re-checked."""
    if not delivered or not armed(world):
        return []
    state = MO._state(world)
    turn = MO._turn(world)
    out: List[str] = []
    moment = MO.entry(world, str(delivered[0])) or {}
    for mid, row in list(state.items()):
        if not MO.is_occurrence(mid) or not isinstance(row, dict) or row.get("status") != MO.STATUS_FIRED:
            continue
        e = MO.entry(world, mid) or {}
        dm = getattr(world, "dialogue_manager", None)
        if dm is not None:
            dm.remove_matching(lambda d, _mid=mid: MO.is_moment_letter(d) and MO.moment_id_of(d) == _mid)
        MO._dismiss_notice(world, mid)
        line = (f"{title_of(e, row)} was set aside for "
                f"{moment.get('title') or 'a moment of history'}")
        row.update({"status": MO.STATUS_WITHDRAWN, "withdrawn_turn": int(turn),
                    "set_aside_for": str(delivered[0])[:40], "receipt": line[:120]})
        MO._log(world, "withdrawn", e, line=line, lord=str(row.get("lord") or ""),
                register=MO.REGISTER_AFFAIR, occurrence=mid)
        write_receipt(world, line)
        out.append(mid)
    if out:
        _promote_popup(world, [str(d) for d in delivered])
    return out


def _promote_popup(world, delivered: List[str]) -> None:
    dm = getattr(world, "dialogue_manager", None)
    head = dm.peek() if dm is not None else None
    if (head is not None and MO.is_moment_letter(head) and MO.moment_id_of(head) in delivered
            and not getattr(world, "incoming_proposal_popup", None)):
        world.incoming_proposal_popup = copy.deepcopy(head.get("popup_payload") or {})


def resolve_courts(world) -> List[str]:
    """Seam AFA — the courts' affairs. v1 authors France's content only
    (Q4); the function stands so a court-run deck (RE-4) lands behind the
    same seam. It does nothing."""
    return []


def settle_squadrons(world) -> List[str]:
    """Seam AFS — the squadrons' fates (RE-H, §6.5 step 7): the affairs tick's
    first step. For every fleet record whose `squadron_last` returned THIS
    morning (`naval._squadron_tick` ran earlier in the advance) and whose
    occurrence row is not yet settled: the row gains `outcome`,
    `outcome_turn` and the authored `outcome_line` (the Accept's `outcome`
    copy by fate), its `receipt` the fate's words; one `moment` log row with
    phase `outcome` carries the line, the Moniteur's `press` and the figures.
    The naval module stays pure naval."""
    if not armed(world):
        return []
    from backend.game_logic import naval
    turn = MO._turn(world)
    state = MO._state(world)
    out: List[str] = []
    for lord, rec in naval.iter_fleet_records(world):
        last = rec.get("squadron_last")
        if not isinstance(last, dict) or int(last.get("returned", -1) if last.get("returned") is not None else -1) != turn:
            continue
        mid = str(last.get("tag") or "")
        row = state.get(mid)
        if not isinstance(row, dict) or row.get("outcome"):
            continue
        e = MO.entry(world, mid)
        if e is None:
            continue
        outcome = str(last.get("outcome") or "")
        side = MO._answer_side(e, MO.ANSWER_ACCEPT, row.get("form"))
        copy_by_fate = side.get("outcome") if isinstance(side.get("outcome"), dict) else {}
        words = (copy_by_fate.get(outcome) or {}) if isinstance(copy_by_fate, dict) else {}
        line = fill_slots(world, str(words.get("line") or ""), row, e)[:TEXT_MAX["outcome_line"]]
        press = fill_slots(world, str(words.get("press") or ""), row, e)[:TEXT_MAX["press"]]
        lost = int(last.get("lost", 0) or 0)
        fate = "home whole" if outcome == "home" else f"{MO.sail_words(lost)} lost"
        row.update({"outcome": outcome, "outcome_turn": int(turn), "outcome_line": line,
                    "receipt": f"{row.get('receipt') or ''} — {fate}"[:120]})
        MO._log(world, "outcome", e, outcome=outcome, line=line or f"{title_of(e, row)} — {fate}", press=press,
                title=title_of(e, row), ships=int(last.get("ships", 0) or 0), lost=lost,
                odds=int(last.get("odds", 0) or 0), draw=int(last.get("draw", 0) or 0), lord=str(lord),
                register=MO.REGISTER_AFFAIR, occurrence=mid)
        out.append(mid)
    return out


def fate_lines(world) -> List[str]:
    """RE-H (reading 0c): the squadrons' fates on THIS morning — the rows whose
    `outcome_turn` is the turn — for the morning's SITUATION in both views
    (amber); RE-R joins the answers' receipts to the same key family."""
    if not armed(world):
        return []
    turn = MO._turn(world)
    return [str(r.get("outcome_line") or "") for _k, r in all_occurrences(world)
            if isinstance(r.get("outcome_turn"), int) and int(r["outcome_turn"]) == turn and r.get("outcome_line")]


# ════════════════════════════════════════════════════════════════════════
# The copy — the record, the board, the Watch, the slots
# ════════════════════════════════════════════════════════════════════════

class _Slots(dict):
    def __missing__(self, key):
        return "?"


def _seat_of(world, host: str) -> str:
    try:
        return str(world.get_nation_capital(host) or host)
    except Exception as exc:
        report(exc, "affairs._seat_of: world.get_nation_capital")
        return str(host)


def _is_chancery(name: str) -> bool:
    """The cast's own fallback ("The Chancery of X") or an authored chancery
    name ("Chancery of Helvetia") — never a minister, never an office line."""
    return "chancery" in str(name or "").lower()


def chancery_of(world, host: str, capitalize: bool = False) -> str:
    """The chancery's name as a phrase: "the chancery of Bavaria", "the chancery
    of the Kingdom of Italy" — the court's display form carries its own
    article, so it is never "the The …"."""
    phrase = f"the chancery of {MO._court(world, host)}"
    return phrase[0].upper() + phrase[1:] if capitalize else phrase


def in_tenure_gap(e: Optional[Dict[str, Any]], host: str, turn: Optional[int]) -> bool:
    """RE-3 (P6, §12c): the host's cast minister is OUT of office on `turn`
    when the template's authored `voice.tenure[host]` holds a gap
    [{from: {turn}, to?: {turn}}] that covers it (an open gap has no `to`).
    Turns only — the validator checked each date against its turn (HC-0)."""
    if turn is None or not isinstance(e, dict):
        return False
    tenure = ((e.get("voice") or {}).get("tenure") or {}) if isinstance(e.get("voice"), dict) else {}
    for gap in tenure.get(host) or []:
        if not isinstance(gap, dict):
            continue
        start = (gap.get("from") or {}).get("turn") if isinstance(gap.get("from"), dict) else None
        end = (gap.get("to") or {}).get("turn") if isinstance(gap.get("to"), dict) else None
        if isinstance(start, int) and not isinstance(start, bool) and int(turn) >= int(start):
            if end is None or int(turn) < int(end):
                return True
    return False


def minister_of(world, e: Optional[Dict[str, Any]], host: str, turn: Optional[int] = None) -> str:
    """The host court's minister by the cast (`resolve_named_diplomat`'s
    envoy arm — Montgelas for Bavaria, Hardenberg for Prussia), or "" where
    the cast names only a chancery, or the cast's name is out of office on
    the issued turn (the template's `voice.tenure`). The caller writes the
    chancery itself (`chancery_of`)."""
    if not host:
        return ""
    if in_tenure_gap(e, host, turn):
        return ""
    from backend.game_logic.diplomatic_templates import resolve_named_diplomat
    try:
        name = str(resolve_named_diplomat("envoy", host, world) or "").strip()
    except Exception as exc:
        report(exc, "affairs.minister_of: resolve_named_diplomat")
        return ""
    return "" if _is_chancery(name) else name


def fill_slots(world, text: str, row: Dict[str, Any], e: Optional[Dict[str, Any]] = None,
               **extra: Any) -> str:
    """The copy's slots over an occurrence row: `{host}`, `{seat}`, `{SEAT}`,
    `{minister}` (the cast's minister on the row's turn, else the chancery —
    RE-3), `{month}` (the row's answered or issued dateline — the `remember`
    line on the next occurrence), `{region}`, `{lord}`, and the caller's
    figures (`n`, `m`)."""
    if not text:
        return ""
    bind = row.get("bind") if isinstance(row.get("bind"), dict) else {}
    slots = _Slots(extra)
    host = str(bind.get("host") or "")
    if host:
        # `{host}` mid-sentence ("the court of the Kingdom of Italy"; "Bavaria"),
        # `{Host}` at a sentence's head; `{minister}` / `{Minister}` the same way
        seat = _seat_of(world, host)
        slots.setdefault("host", MO._court(world, host))
        slots.setdefault("Host", MO._court(world, host, capitalize=True))
        slots.setdefault("seat", seat)
        slots.setdefault("SEAT", seat.upper())
        turn = row.get("turn")
        minister = (minister_of(world, e, host, turn if isinstance(turn, int) else None)
                    or chancery_of(world, host))
        slots.setdefault("minister", minister)
        slots.setdefault("Minister", minister[0].upper() + minister[1:] if minister else "")
    slots.setdefault("region", str(bind.get("region") or ""))
    if row.get("lord"):
        slots.setdefault("lord", MO._court(world, str(row["lord"]), capitalize=True))
        # RE-6: `{court}` mid-sentence / `{Court}` at the head, and the lord's
        # own seat when no host is bound (the courts' press lines)
        slots.setdefault("court", MO._court(world, str(row["lord"])))
        slots.setdefault("Court", MO._court(world, str(row["lord"]), capitalize=True))
        if not host:
            own_seat = _seat_of(world, str(row["lord"]))
            slots.setdefault("seat", own_seat)
            slots.setdefault("SEAT", own_seat.upper())
    # RE-6: `{until}` — the morning an edict's term ends (the row's `until`)
    until = row.get("until")
    if isinstance(until, int) and not isinstance(until, bool):
        slots.setdefault("until", MO._dateline(world, int(until)))
    when = row.get("answered_turn") or row.get("lapsed_turn") or row.get("turn")
    if isinstance(when, int) and not isinstance(when, bool):
        slots.setdefault("month", MO._dateline(world, int(when)))
    # RE-H: `{date}` is the squadron's expected return (the row's `home_by`,
    # written at the answer); the template's authored `slots` table gives a
    # phrase by the ISSUED turn ("last February" until T26, "two years ago"
    # after — the engine reads turns alone, HC-0).
    home_by = row.get("home_by")
    if isinstance(home_by, int) and not isinstance(home_by, bool):
        slots.setdefault("date", MO._dateline(world, int(home_by)))
    issued = row.get("turn")
    for name, phrase in authored_slots(e, issued if isinstance(issued, int) else None).items():
        slots.setdefault(name, phrase)
    try:
        return str(text).format_map(slots)
    except (ValueError, IndexError):
        return str(text)


def authored_slots(e: Optional[Dict[str, Any]], issued: Optional[int]) -> Dict[str, str]:
    """The template's `slots` {name: [{until: {turn}, text}, …, {text}]} read
    at the issued turn: the first entry whose `until` turn is still ahead,
    else the last (the entry without `until`). Display only."""
    table = (e or {}).get("slots") if isinstance(e, dict) else None
    if not isinstance(table, dict):
        return {}
    out: Dict[str, str] = {}
    for name, entries in table.items():
        if not isinstance(entries, list) or not entries:
            continue
        chosen = ""
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            until = (entry.get("until") or {}).get("turn") if isinstance(entry.get("until"), dict) else None
            chosen = str(entry.get("text") or "")
            if until is None or issued is None or int(issued) < int(until):
                break
        out[str(name)] = chosen
    return out


def form_block(e: Dict[str, Any], occ: Dict[str, Any]) -> Dict[str, Any]:
    """The frozen form's authored block (P18) — {} for an entry with none."""
    forms = (e or {}).get("forms")
    form = (occ or {}).get("form")
    if form and isinstance(forms, dict) and isinstance(forms.get(str(form)), dict):
        return forms[str(form)]
    return {}


def seat_of(world, host: str) -> str:
    """The host's seat (its capital region), for "for the court of Munich"."""
    return _seat_of(world, host) if host else ""


def title_of(e: Dict[str, Any], occ: Dict[str, Any]) -> str:
    """The letter's title — the frozen form's when the entry authors forms."""
    title = form_block(e, occ).get("title")
    if title:
        return str(title)
    return str((e or {}).get("title") or "")


def _arrival_of(occ: Dict[str, Any]) -> str:
    try:
        return ARRIVAL_FIRST if int(str(occ.get("id") or "").split(MO.OCCURRENCE_SEP, 1)[1]) <= 1 \
            else ARRIVAL_LATER
    except (IndexError, ValueError):
        return ARRIVAL_FIRST


def chapter_of(e: Dict[str, Any], occ: Dict[str, Any]) -> str:
    """P18: the variant keyed by the occurrence's facts — `arrival` (first /
    later) and `last_fate` (home / caught, the row's frozen reading of the
    fleet record at delivery) — in authored order, "" when none matches."""
    facts = {"arrival": _arrival_of(occ)}
    fate = str((occ or {}).get("last_fate") or "")
    if fate:
        facts["last_fate"] = fate
    for variant in (e or {}).get("variants") or []:
        if not isinstance(variant, dict):
            continue
        key, value = str(variant.get("key") or ""), str(variant.get("value") or "")
        if key in facts and facts[key] == value:
            return str(variant.get("text") or "")
    return ""


def _arrival_index(occ: Dict[str, Any]) -> int:
    try:
        return int(str((occ or {}).get("id") or "").split(MO.OCCURRENCE_SEP, 1)[1])
    except (IndexError, ValueError):
        return 1


def exhibit_of(e: Dict[str, Any], occ: Dict[str, Any]) -> str:
    """§6.5: the exhibit — one authored string, or a list the arrivals walk
    in turn (odd arrivals the first, even the second); "" when none."""
    exhibit = (e or {}).get("exhibit")
    if isinstance(exhibit, list):
        texts = [str(x) for x in exhibit if isinstance(x, str) and x]
        return texts[(_arrival_index(occ) - 1) % len(texts)] if texts else ""
    return str(exhibit or "")


def record_text(world, e: Dict[str, Any], occ: Dict[str, Any]) -> str:
    """The ground (every arrival) and the chapter (by the occurrence's facts),
    in the moments' "Historically …" frame."""
    ground = fill_slots(world, str((e or {}).get("record") or ""), occ, e)
    chapter = fill_slots(world, chapter_of(e, occ), occ, e)
    return f"{ground} {chapter}".strip() if chapter else ground


def board_lines(world, e: Dict[str, Any], occ: Dict[str, Any]) -> List[str]:
    """The premise's facts, named — read live at every read (the IGR-2
    lesson), the tier frozen (§5)."""
    try:
        lines = [str(x) for x in _board(world, e, occ) if x]
        # RE-R (§12c): the previous letter's answer, remembered — the last line
        remembered = remember_line(world, e, occ)
        if remembered:
            lines.append(remembered)
        return lines
    except Exception as exc:
        report(exc, "affairs.board_lines: the board")
        return []


def _board(world, e: Dict[str, Any], occ: Dict[str, Any]) -> List[str]:
    when = e.get("when") or {}
    predicate = str(when.get("predicate") or "")
    lord = str(occ.get("lord") or MO.owner(world))
    bind = occ.get("bind") if isinstance(occ.get("bind"), dict) else {}
    read = premise_holds(world, e, lord)
    streak = streak_of(world, e, subject_of(read)) if read.get("holds") else 0
    if predicate == "sovereign_afield":
        tracker = getattr(world, "authority_tracker", None)
        standing = int(getattr(tracker, "authority", 0) or 0) if tracker is not None else 0
        if not read.get("holds"):
            # AU-12's sibling: home again while the letter stands — said, never "0 mornings running"
            return [f"The Emperor is no longer afield this morning; his authority is {standing}."]
        region = str(bind.get("region") or (read.get("bind") or {}).get("region") or "the field")
        return [f"The Emperor is afield at {region}, {streak} mornings running; his authority is {standing}."]
    if predicate == "corps_on_host":
        host = str(bind.get("host") or "")
        if not host:
            return []
        from backend.display_names import possessive
        from backend.game_logic.diplomacy import STATE_RELATION_THRESHOLDS
        corps = int(read.get("measure") or 0) if (read.get("bind") or {}).get("host") == host else 0
        state = world.get_diplomatic_state(lord, host)
        # AU-10's sibling: the host sits mid-sentence ("stand on the Kingdom of
        # Italy's soil", never "on The Kingdom of Italy's")
        display = possessive(MO._court(world, host))
        lines = [f"{corps} of your corps stand on {display} soil ({MO._standing(world, lord, host)}, "
                 f"goodwill {MO._relation(world, lord, host)}); tier {int(occ.get('tier') or 1)}."]
        threshold = STATE_RELATION_THRESHOLDS.get(state)
        if threshold is not None and MO._vassal_row(world, host, lord) is None:
            distance = int(MO._relation(world, lord, host)) - int(threshold)
            lines.append(f"The alliance steps down at goodwill {int(threshold)} held five turns — "
                         f"{max(0, distance)} points away.")
        return lines
    if predicate == "staff_offered":
        from backend.game_logic import reforms
        from backend.game_logic.instruments import purse_of
        row = reforms.find_law(world, lord, str(bind.get("law") or when.get("law") or ""))
        price = int((row or {}).get("price", 0) or 0)
        upkeep = int((row or {}).get("upkeep", 0) or 0)
        # AU-12's sibling: read live — a peace, or the Staff decreed, while the letter stands is said
        if streak:
            war = f"At war {streak} turns running"
        else:
            war = "At war" if _at_war(world, lord, "_board") else "At peace this morning"
        staff = ("the Staff is in force" if row is not None and reforms.is_in_force(row)
                 else "the Staff is not in force")
        return [f"{war}; {staff}; the chest holds "
                f"{int(purse_of(world, lord)[1]):,} gold against {price:,} now and {upkeep:,} a turn."]
    if predicate == "colony_cut_off":
        return _board_colony_cut_off(world, e, occ, lord, bind, read)
    if predicate in OFFER_PREDICATES:
        return _board_offer(world, e, lord, read, streak)
    if predicate == "chest_strained":
        # AU-2c the Bank: the latch's count, then this morning's figures — the one forecast
        from backend.game_logic.ledger import chest_forecast
        of = int((e.get("latch") or {}).get("of", 12) or 12)
        lines = [f"At war, the chest ran short {latch_count(world, e)} of the last {of} mornings."]
        forecast = chest_forecast(world, lord)
        chest, net = int(forecast.get("chest", 0) or 0), int(forecast.get("net", 0) or 0)
        if net >= 0:
            lines.append(f"This morning the chest holds {chest:,} gold and the forecast Net is "
                         f"+{net:,} a turn.")
        else:
            lines.append(f"This morning the chest holds {chest:,} gold against a deficit of {-net:,} "
                         f"a turn: at this rate it runs dry in {chest // -net} turns.")
        return lines
    if predicate == "ports_defied":
        # AU-2c the Pope: the war with the trade-dominant power, the court's ports —
        # read live (AU-12): a peace, or the System, that came while the letter
        # stands is said, never the war it ended
        from backend.game_logic import naval
        court = str(when.get("court") or "")
        target = naval.trade_dominance_nation(world)
        if target and streak:
            war = f"At war with {MO._court(world, target)} {streak} mornings running"
        elif target and world.is_at_war(lord, target):
            war = f"At war with {MO._court(world, target)}"
        elif target:
            war = f"{MO._court(world, target, capitalize=True)} is {MO._standing(world, lord, target)} this morning"
        else:
            war = "No power is master of the sea this morning"
        members = getattr(world, "continental_system_members", None) or []
        ports = "are closed under the System" if court in members else "stay open outside the System"
        return [f"{war}; the ports of {MO._court(world, court)} {ports} "
                f"({MO._standing(world, lord, court)}, goodwill {MO._relation(world, lord, court)})."]
    return []


def _board_offer(world, e: Dict[str, Any], lord: str, read: Dict[str, Any], streak: int) -> List[str]:
    """RE-6: an offer's board — the premise's facts and the chest against the
    decree's price (shown = applied: the price is the `edict` block's)."""
    from backend.game_logic.instruments import purse_of
    predicate = str((e.get("when") or {}).get("predicate") or "")
    if predicate == "proclamation_wanted":
        # AU-3b re-premised: the eve of battle — the enemy seen within a march
        # (fog-safe, read live), the latch's count, the price in authority
        from backend.display_names import humanize_entity_name
        from backend.game_logic import standing
        seen = _enemy_within_a_march(world, lord)
        of = int((e.get("latch") or {}).get("of", 4) or 4)
        fact = (f"{humanize_entity_name(seen[0])} stands at {humanize_entity_name(seen[1])}, within a march "
                f"of the Emperor" if seen else "No enemy army is seen within a march of the Emperor this morning")
        asks = standing.push_price(world, lord, int(edict_block(e).get("authority", 0) or 0))
        return [f"{fact} ({latch_count(world, e)} of the last {of} mornings); his authority stands at "
                f"{standing.standing_of(world, lord)} against the {asks} the proclamation asks."]
    price = int(edict_block(e).get("price", 0) or 0)
    purse = f"the chest holds {int(purse_of(world, lord)[1]):,} gold against {price:,}"
    if predicate == "magazines_wanted":
        corps = int(read.get("measure") or 0)
        fact = (f"{corps} of your corps draw campaign pay on foreign soil" if corps > 0 else
                f"Europe gathers against you (the alarm at {int(getattr(world, 'threat_level', 0) or 0)})")
        return [f"{fact}; {purse}."]
    if predicate == "remounts_wanted":
        from backend.models.world_state import MAX_CAVALRY_POOL
        pool = int(((getattr(world, "manpower_pools", {}) or {}).get(lord) or {}).get("cavalry", 0) or 0)
        cap = int(MAX_CAVALRY_POOL)
        return [f"The cavalry depots hold {pool:,} of {cap:,} ({int(pool * 100 // max(1, cap))}%); the weakest "
                f"squadrons stand at {_weakest_cavalry_corps_pct(world, lord)}% of their establishment; {purse}."]
    return [f"At peace with every great power {streak} mornings running, the Charges carrying "
            f"the crown alone; {purse}."]


def _board_colony_cut_off(world, e, occ, lord: str, bind: Dict[str, Any],
                          read: Dict[str, Any]) -> List[str]:
    """§6.5's board: the latch's count and where the letter found the Emperor
    (at court, or at headquarters in the field); the hunter's
    sail against ours (ints, as the crossing refusal casts them); in the
    squadron form the passage's odds; from the second arrival the last
    squadron's fate (RE-H's second landing writes `last_sailed`)."""
    from backend.game_logic import naval
    of = int(((e.get("latch") or {}).get("of", 12)) or 12) if isinstance(e.get("latch"), dict) else 12
    region = str(bind.get("region") or (read.get("bind") or {}).get("region") or "")
    home = set((getattr(world, "nation_starting_regions", {}) or {}).get(lord, []) or [])
    if region and region in home:
        seat = f"the Emperor holds court at {region}"
    elif region:
        seat = f"the letter reaches headquarters at {region}"
    else:
        seat = "the letter reaches the Emperor"
    lines = [f"{MO._court(world, lord, capitalize=True)} blockaded {latch_count(world, e)} of the last "
             f"{of} mornings; {seat}."]
    rec = naval.get_fleet(world, lord) or {}
    ours = int(naval.effective_strength(rec))
    hunter, coverage = naval.blockader_against(world, lord)
    if hunter:
        from backend.display_names import possessive
        lines.append(f"{possessive(MO._court(world, hunter, capitalize=True))} squadrons hold the coast: "
                     f"{int(coverage)} sail effective against our {ours}.")
    else:
        lines.append(f"No enemy squadron holds the coast this morning; {ours} sail effective in port.")
    # RE-H: the squadron form's passage, from the one quote the Accept applies;
    # a hunter that vanished reads as the Accept's own refusal, never silence
    side = MO._answer_side(e, MO.ANSWER_ACCEPT, (occ or {}).get("form"))
    sq = next((op for op in side.get("ops") or [] if isinstance(op, dict) and op.get("op") == "squadron"), None)
    if sq is not None:
        q = naval.squadron_quote(world, lord, int(sq.get("ships", 5) or 5), int(sq.get("away", 4) or 4),
                                 str(sq.get("to") or ""), MO._turn(world))
        lines.append(f"The passage: {int(q['odds'])} in 100 to come home whole." if not q["refusal"]
                     else f"The passage: {q['refusal']}")
    # from the second arrival: the last squadron's fate, frozen into the row
    sailed, fate = (occ or {}).get("last_sailed"), str((occ or {}).get("last_fate") or "")
    if isinstance(sailed, int) and not isinstance(sailed, bool) and fate in OUTCOMES:
        lost = int((occ or {}).get("last_ships", 0) or 0)
        what = "home whole" if fate == "home" else f"{MO.sail_words(lost)} lost"
        lines.append(f"Your last squadron sailed {MO._dateline(world, int(sailed))}: {what}.")
    return lines


def watch(world, record: bool = True) -> List[str]:
    """§12 — the Watch: at most two "may" lines a morning, the nearest-due
    templates' `watch` strings over the premise's own measures (`{n}` the
    measure, `{m}` the streak, `{host}`); nothing standing, on cooldown or
    capped. RE-2 renders them; a line shown is remembered (`watched`) for
    the set-aside tally (§7). RE-C: `record=False` is the Correspondence's
    pure read — IN THE OFFING shows the same lines and writes nothing (a GET
    never mutates)."""
    if not armed(world):
        return []
    turn = MO._turn(world)
    rows: List[Tuple[int, int, str, str]] = []
    for index, e in enumerate(deck(world)):
        template = str(e["id"])
        lord = _lord_of(world, e)
        read = premise_holds(world, e, lord)
        if not read.get("holds"):
            continue
        subject = subject_of(read)
        if any(r.get("status") == MO.STATUS_FIRED for _k, r in occurrences(world, template)):
            continue
        if on_cooldown(world, e, subject, turn) or not under_cap(world, e, subject, turn):
            continue
        ends = e.get("ends")
        if isinstance(ends, dict) and turn > int(ends.get("turn", 10 ** 6) or 10 ** 6):
            continue                # the file is closed (RE-H; `candidates` says the same)
        streak = streak_of(world, e, subject)
        measure = read.get("measure")
        measure = streak if measure is None else int(measure)
        # RE5-2 (the Mode C walk, November 2, 2026): a letter the standing
        # closes is not in the offing — `candidates` asks `bites` and the
        # Watch must ask the same, or it promises for twelve mornings what
        # the floor forbids (the live board at standing 70: "Decrès may
        # write" while the Marine's Decline could not land above 71).
        if not bites(world, lord, e, tier_of(e, measure)):
            continue
        latched = str((e.get("when") or {}).get("predicate") or "") in LATCHED_PREDICATES
        if latched:
            measure = latch_count(world, e)      # "blockaded {n} of the last 12 mornings"
            # AU-13 (AU-2c's arming, November 5, 2026): a latch that has counted
            # no morning is not in the offing — "The chest ran short at war 0 of
            # the last 12 mornings — the Bank's regents may write" promised a
            # letter no strain had begun (the Marine's line the same at 0)
            if measure <= 0:
                continue
        # RE5-1 (the Mode C walk, November 2, 2026): `{m}` is read against the
        # authored need ("{m} of 2 mornings") — a matter held past its need
        # by a busy desk or the pulse keeps counting, and the line read
        # "7 of 2 mornings"; the slot is capped at the need, the streak itself
        # untouched (the measure and the distance read it whole).
        need = max(1, int(e.get("streak", 1) or 1))
        text = fill_slots(world, str(e.get("watch") or ""),
                          {"bind": read.get("bind") or {}, "lord": lord}, e, n=measure, m=min(streak, need))
        distance = max(max(0, int(e.get("streak", 1) or 1) - streak), latch_distance(world, e))
        rows.append((distance, index, template, text))
    rows.sort()
    out: List[str] = []
    shown = [template for _distance, _index, template, text in rows[:2] if text]
    if not shown:
        # RE3-10: a Watch that shows nothing writes nothing — the runtime
        # key is created on the first WRITE of an armed world, never by a
        # read (the boot briefing's Watch wrote an empty `watched` map and
        # the new world differed from a fresh one by it; EP-F1's rule).
        return out
    if not record:
        return [text for _distance, _index, _template, text in rows[:2] if text]
    watched = runtime(world).setdefault("watched", {})
    for _distance, _index, template, text in rows[:2]:
        if text:
            out.append(text)
            watched[template] = int(turn)
    return out


def closing_record(world) -> List[Dict[str, Any]]:
    """RE-C (§6.5, §12b.1): the closing record and the 1825 line of a FILE
    THAT HAS CLOSED — a template with authored `closing` whose `ends.turn`
    lies behind this morning (the engine's own test in `candidates` and
    `watch`). P13's earlier close (the cap spent after a loss) is built
    nowhere, so the page never claims it. A pure read."""
    if not armed(world):
        return []
    turn = MO._turn(world)
    out: List[Dict[str, Any]] = []
    for e in deck(world):
        closing, ends = e.get("closing"), e.get("ends")
        if not isinstance(closing, list) or not isinstance(ends, dict):
            continue
        end_turn = int(ends.get("turn", 10 ** 6) or 10 ** 6)
        if turn > end_turn:
            out.append({"id": str(e["id"]), "title": str(e.get("title") or ""), "turn": end_turn,
                        "label": MO._dateline(world, end_turn),
                        "lines": [str(line) for line in closing if line]})
    return out


# ════════════════════════════════════════════════════════════════════════
# RE-6 — the Edicts (RECURRING_EVENTS_SPEC.md §0 Q2, §6.2 E1–E3, §16 "RE-6"):
# a fixed-term decree on the laws' closed effect set — `term` turns in force,
# then `rest` turns before it may be offered again; gold and one
# administrative action, no upkeep. ONE store entry per lord and template
# (`{lord|template: until}` in the affairs runtime — a `{str: int}` map the
# save round-trips), in force while `until > turn`: expiry is DERIVED, never
# ticked. `reforms.effect_terms` reads the edicts in force as its second
# source, so every seam that applies a law applies an edict. Every reader
# here is pure (`_store`, never `runtime()`); `grant_edict` is the one
# writer, for the letter's Accept and the courts' rung alike (GR5).
# ════════════════════════════════════════════════════════════════════════

def edict_block(e: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    block = (e or {}).get("edict") if isinstance(e, dict) else None
    return block if isinstance(block, dict) else {}


def edict_currency(e: Optional[Dict[str, Any]]) -> str:
    """AU-3b: the purse an offer's Accept pays — "authority" for an edict
    priced in authority alone (the Proclamation: its block carries no gold
    price, only `authority`), else "gold"."""
    block = edict_block(e)
    if block and not int(block.get("price", 0) or 0) and int(block.get("authority", 0) or 0) > 0:
        return "authority"
    return "gold"


def edict_name(e: Dict[str, Any]) -> str:
    return str(edict_block(e).get("name") or e.get("title") or e.get("id") or "the decree")


def template_by_id(world, template: str) -> Optional[Dict[str, Any]]:
    return _template_by_id(world, template)


def edict_key(lord: str, template: str) -> str:
    return f"{lord}{SUBJECT_SEP}{template}"


def _edicts_store(world) -> Dict[str, int]:
    """The `{lord|template: until}` map — a pure read of the store (a GET,
    the boot briefing and the supply cap all pass here)."""
    store = runtime_read(world).get(EDICTS_KEY)
    return store if isinstance(store, dict) else {}


def edict_until(world, lord: str, template: str) -> int:
    return int(_edicts_store(world).get(edict_key(lord, template), 0) or 0)


def edict_state(world, lord: str, e: Dict[str, Any]) -> str:
    """in_force | resting | available — derived from the turn alone."""
    until = edict_until(world, lord, str(e.get("id") or ""))
    if until <= 0:
        return "available"
    turn = MO._turn(world)
    if turn < until:
        return "in_force"
    if turn < until + int(edict_block(e).get("rest", 0) or 0):
        return "resting"
    return "available"


def edicts_in_force(world, lord: str) -> List[Tuple[Dict[str, Any], int]]:
    """[(template, until)] for the lord's edicts in force this turn — the
    second source `reforms.effect_terms` reads; [] without a store."""
    store = _edicts_store(world)
    if not store or not lord:
        return []
    turn = MO._turn(world)
    prefix = f"{lord}{SUBJECT_SEP}"
    # T0-D (GR-60, Golden Rule 8): the store is read FIRST — a court with no
    # decree running past this turn has none in force, and the deck (rebuilt
    # and filtered on every read) is never walked. Every law and edict read
    # comes here, once per province in the supply cap; the store holds one
    # key per decree taken. When one runs, the deck's order is kept below.
    if not any(str(k).startswith(prefix) and int(v or 0) > turn
               for k, v in store.items()):
        return []
    out: List[Tuple[Dict[str, Any], int]] = []
    for e in deck(world):
        until = int(store.get(prefix + str(e.get("id") or ""), 0) or 0)
        if until > turn and edict_block(e):
            out.append((e, until))
    return out


def edict_row(e: Dict[str, Any], until: int) -> Dict[str, Any]:
    """The pseudo-row `effect_terms` yields for an edict — `name` so
    `reforms.display_name` names it, `effects` its clauses, `until` its end."""
    block = edict_block(e)
    return {"id": str(e.get("id") or ""), "name": edict_name(e),
            "effects": list(block.get("effects") or []), "until": int(until), "edict": True}


def edict_refusal(world, lord: str, e: Dict[str, Any], treasury: Optional[int] = None,
                  with_reserve: bool = False, currency: str = "gold") -> str:
    """"" when the decree may be taken, else why — ONE gate for the premise
    and the courts' rung (`with_reserve`: the laws rung's own bar — the
    price plus the AI's reserve and five turns of the slate's upkeep), and
    for the letter's plan and the courts' verb (the price alone). AU-3a:
    `currency="authority"` reads the block's `authority` price at the
    recency rise against the purchases' floor (`standing.refusal` — a
    court's `ai_refusal`), never the chest."""
    block = edict_block(e)
    if not armed(world) or not block:
        return "the decree is not in the book."
    state = edict_state(world, lord, e)
    until = edict_until(world, lord, str(e.get("id") or ""))
    name = edict_name(e)
    name = name[0].upper() + name[1:] if name else name
    if state == "in_force":
        return f"{name} stands until {MO._dateline(world, until)}."
    if state == "resting":
        return f"{name} rests until {MO._dateline(world, until + int(block.get('rest', 0) or 0))}."
    if currency == "authority":
        from backend.game_logic import standing
        base = int(block.get("authority", 0) or 0)
        if not standing.buys_armed() or base <= 0:
            return "the decree is not in the book."
        if lord != getattr(world, "player_nation", None) and not standing.courts_move():
            # AU-14 (BUG_FIXES.md §AU): measured, not inert — the courts boot at
            # 60, their floors pass, and a court whose gold refuses decrees in
            # authority (AU-20: that T11 move was its gold road); flipped up with the
            # courts (AU-4, `courts_move` — arm AUC holds it down)
            return "the courts' Decree waits for the courts' flip."
        return str(standing.refusal(world, lord, -standing.push_price(world, lord, base)) or "")
    if edict_currency(e) == "authority":
        # AU-3b: an edict priced in authority alone has no gold road — so the
        # courts' rung proclaims on its authority road alone (AU-14, AU-4)
        return "the decree is paid in authority alone."
    price = int(block.get("price", 0) or 0)
    if treasury is None:
        from backend.game_logic.instruments import purse_of
        treasury = int(purse_of(world, lord)[1])
    bar = price
    if with_reserve:
        from backend.game_logic.reforms import AI_PURSE_RESERVE, AI_PURSE_UPKEEP_TURNS, law_upkeep_bill
        bar += int(AI_PURSE_RESERVE) + int(AI_PURSE_UPKEEP_TURNS) * int(law_upkeep_bill(world, lord))
    if int(treasury) < bar:
        return f"{price:,} gold is asked; the treasury holds {int(treasury):,}."
    return ""


def grant_edict(world, lord: str, e: Dict[str, Any], currency: str = "gold", party: str = "") -> int:
    """THE writer: charge the price through the gold op's own path
    (`record_gold_spent`), write `until`, tally the decree and the gold for
    the measure. Returns `until`. The administrative action is the
    caller's — the letter's `admin` op, or the court's admin budget. AU-3a:
    `currency="authority"` — the Decree — spends the block's `authority`
    price through `standing.buy` (the recency rise, the cause
    `edict_decreed`, the minister its party) and leaves the chest untouched;
    the authority tally beside the gold's."""
    block = edict_block(e)
    until = MO._turn(world) + int(block.get("term", 0) or 0)
    rt = runtime(world)
    if currency == "authority":
        from backend.game_logic import standing
        paid = standing.buy(world, lord, int(block.get("authority", 0) or 0), "edict_decreed",
                            party=str(party or ""), edict=edict_name(e))
        spent = rt.setdefault(EDICT_AUTHORITY_KEY, {})
        spent[lord] = int(spent.get(lord, 0) or 0) - int(paid.get("applied", 0) or 0)
    else:
        price = int(block.get("price", 0) or 0)
        MO._apply_gold(world, lord, {"amount": price})
        spent = rt.setdefault(EDICT_GOLD_KEY, {})
        spent[lord] = int(spent.get(lord, 0) or 0) + price
    key = edict_key(lord, str(e.get("id") or ""))
    rt.setdefault(EDICTS_KEY, {})[key] = int(until)
    decreed = rt.setdefault(DECREED_KEY, {})
    decreed[key] = int(decreed.get(key, 0) or 0) + 1
    return until


def decree_for_court(world, lord: str, e: Dict[str, Any], currency: str = "gold") -> int:
    """A court's decree (the rung's verb): the same grant, then one `moment`
    / `outcome` row through the moments' own writer — the Moniteur prints its
    `press`, the campaign log its line; no state row, no notice, no popup.
    AU-3a: `currency="authority"` — the Decree at the court's floors."""
    until = grant_edict(world, lord, e, currency=currency)
    block = edict_block(e)
    own_seat = _seat_of(world, lord)
    press = fill_slots(world, str(block.get("court_press") or ""), {"lord": lord, "until": until}, e,
                       seat=own_seat, SEAT=own_seat.upper())[:160]
    paid = (f"{int(block.get('authority', 0) or 0)} authority" if currency == "authority"
            else f"{int(block.get('price', 0) or 0):,} gold")
    line = (f"{MO._court(world, lord, capitalize=True)} decrees {edict_name(e)} for "
            f"{int(block.get('term', 0) or 0)} turns ({paid})")
    MO._log(world, "outcome", e, lord=lord, register=MO.REGISTER_AFFAIR, line=line,
            press=press or None, until=int(until))
    return until


def ai_decrees() -> bool:
    """The courts' Edicts — ARMED by the user's word (RE-6, November 2, 2026:
    "Flip it on"; `RECURRING_EVENTS_SPEC.md` §25.3, §25.6). Measured first
    with the rung up on the live tree and escalated: the five courts with a
    laws deck decree two to four edicts a campaign (4–7k gold each, 15–30 %
    of a T40 chest), the ambient alarm series moves from turn 10 and every
    road arm's end turn moves against the unarmed control while the player's
    letters alone move nothing — history with teeth, the brake on France the
    gate's Q5 foresaw. True arms the courts at the player's prices through
    `find_ai_edict` (GR5); the series rig's AFE arm holds it down
    (`tests/_affairs_seams.py`), and False parks it again in one line."""
    return True


def last_decree_turn(world, lord: str) -> Optional[int]:
    """The turn of the court's latest decree, derived from the store (until −
    term); None when it has decreed nothing."""
    store = _edicts_store(world)
    prefix = f"{lord}{SUBJECT_SEP}"
    turns = []
    for e in deck(world):
        until = int(store.get(prefix + str(e.get("id") or ""), 0) or 0)
        if until > 0:
            turns.append(until - int(edict_block(e).get("term", 0) or 0))
    return max(turns) if turns else None


def find_ai_edict(world, nation: str, treasury: int, admin_ap: int) -> Optional[Dict[str, Any]]:
    """The courts' rung (priority 1.79, beside the laws): the first offer in
    deck order whose premise holds this morning for the court and whose
    purse passes the laws rung's bar, for the courts that keep a laws deck
    (`reforms.REFORM_DECKS`), one decree every `AI_ENACTMENT_EVERY_TURNS`,
    never while a law would lapse, never the player; the instantaneous read
    (no streak — the streak paces the player's letter). The gate is read
    fresh, outside the premise memo. AU-3a (§5.7): gold first; where the gold
    refuses, the Decree at the court's floors (`standing.ai_refusal` — 30,
    and three diplomatic points a turn), the order carrying its `currency`."""
    if not ai_decrees() or not armed(world) or not nation or int(admin_ap) < 1:
        return None
    if nation == getattr(world, "player_nation", None):
        return None
    from backend.game_logic.reforms import AI_ENACTMENT_EVERY_TURNS, REFORM_DECKS, ai_holds_the_purse
    if nation not in REFORM_DECKS or ai_holds_the_purse(world, nation):
        return None
    last = last_decree_turn(world, nation)
    if last is not None and MO._turn(world) - last < int(AI_ENACTMENT_EVERY_TURNS):
        return None
    for e in deck(world):
        if not edict_block(e):
            continue
        currency = "gold"
        if edict_refusal(world, nation, e, treasury=int(treasury), with_reserve=True):
            if edict_refusal(world, nation, e, currency="authority"):
                continue
            currency = "authority"
        read = premise_holds(world, e, nation)
        if not read.get("holds"):
            continue
        # AU-4: a latched offer (the Proclamation) asks its latch's bit this
        # morning — a court proclaims on its own eve of battle, never by the
        # war alone (the player's letter waits on the latch's window)
        if str((e.get("when") or {}).get("predicate") or "") in LATCHED_PREDICATES and not read.get("latch"):
            continue
        order = {"action": "decree_edict", "target": str(e.get("id") or "")}
        if currency == "authority":
            order["currency"] = currency
        return order
    return None


# ════════════════════════════════════════════════════════════════════════
# RE-R — the reactions (RECURRING_EVENTS_SPEC.md §12c): the marshal's remark
# on "Live off the land", the morning-after receipt, the Moniteur's line and
# the remember line. Reads only — the answer writes the row (`echo`,
# `remark_by`) and the log row (`press`); the budget is one line per
# surface per letter, and nothing here opens a popup or sounds.
# ════════════════════════════════════════════════════════════════════════

HOST_REMARKS: Dict[str, str] = {
    "Davout": "I will hang the first man who takes a hen unpaid, Sire — but discipline does not feed a corps.",
    "Massena": "{Host} is a fat country, Sire. My men will not go hungry, nor will I.",
    "Ney": "My men will eat, Sire. The minister may send his bill to me.",
    "Lannes": "They fought beside us, Sire. Eating their harvest is a poor way to say so.",
    "Murat": "My horses want oats, Sire, and the country grows them.",
    "Soult": "The quartermasters have their lists, Sire; {seat} shall have its receipts in good time.",
    "Bernadotte": "I will give receipts, Sire, though no one will ever pay them.",
}
HOST_REMARKS_BY_PERSONALITY: Dict[str, str] = {
    "aggressive": "The country is rich, Sire, and my quartermasters are thorough.",
    "cautious": "I will have every requisition signed for, Sire. A hungry ally makes a poor neighbour.",
    "literal": "The order is to live off the land, Sire. The corps lives off the land.",
}
HOST_REMARK_DEFAULT = "The corps will take what the country gives, Sire, and sign for it."
REMARK_BY_MAX = 40


def largest_corps_on_host(world, lord: str, host: str) -> str:
    """The marshal with the most men on the host's soil this morning —
    `_corps_on_host`'s own filter (the lord's marshals; no sovereign, no
    captive, no contingent commander), the region's controller the host;
    "" when none stands there. One pass over the marshal list (Rule 8)."""
    regions = getattr(world, "regions", {}) or {}
    contingents = {str(r.get("marshal") or "") for r in
                   (getattr(world, "vassal_contingents", None) or {}).values() if isinstance(r, dict)}
    best, best_men = "", -1
    for m in (getattr(world, "marshals", {}) or {}).values():
        if (getattr(m, "nation", "") != lord or getattr(m, "is_sovereign", False)
                or getattr(m, "captured_by", "") or getattr(m, "name", "") in contingents):
            continue
        region = regions.get(str(getattr(m, "location", "") or ""))
        if region is None or str(getattr(region, "controller", "") or "") != str(host):
            continue
        men = int(getattr(m, "strength", 0) or 0)
        if men > best_men:
            best, best_men = str(getattr(m, "name", "") or ""), men
    return best


def host_remark(world, e: Dict[str, Any], row: Dict[str, Any]) -> Tuple[str, str]:
    """The marshal's remark (§12c): by name in `HOST_REMARKS`, else by
    personality, else the default — "{name}: {line}", the `{Host}` / `{seat}`
    slots filled over the row; ("", "") for a row without a host or with no
    corps left on its soil at the answer (the response keeps its one line)."""
    host = row_subject(row)
    if not host:
        return "", ""
    lord = str(row.get("lord") or _lord_of(world, e))
    name = largest_corps_on_host(world, lord, host)
    if not name:
        return "", ""
    marshal = (getattr(world, "marshals", {}) or {}).get(name)
    personality = str(getattr(marshal, "personality", "") or "")
    text = HOST_REMARKS.get(name) or HOST_REMARKS_BY_PERSONALITY.get(personality) or HOST_REMARK_DEFAULT
    return f"{name}: {fill_slots(world, text, row, e)}"[:TEXT_MAX["echo"]], name[:REMARK_BY_MAX]


def press_of(world, e: Dict[str, Any], row: Dict[str, Any], answer_key: str) -> str:
    """The Moniteur's line for an answer (§12c, P20): the side's authored
    `press`, filled over the row; "" where none is authored — Berthier's Not
    now, and the squadron form's Accept, whose paper line is its `outcome`
    row's."""
    side = MO._answer_side(e, answer_key, row.get("form"))
    return fill_slots(world, str(side.get("press") or ""), row, e)[:TEXT_MAX["press"]]


def receipt_lines(world) -> List[str]:
    """The morning-after SITUATION lines (§12c, P10): the occurrence rows
    answered on the previous turn whose side authors `situation`, filled over
    the row (`{date}` for a squadron). A lapsed letter prints none here — both
    views already carry it under LAPSED ENVOYS. A pure read."""
    if not armed(world):
        return []
    turn = MO._turn(world)
    out: List[str] = []
    for mid, row in all_occurrences(world):
        if row.get("status") != MO.STATUS_ANSWERED or int(row.get("answered_turn") or -1) != turn - 1:
            continue
        e = MO.entry(world, mid)
        if e is None:
            continue
        side = MO._answer_side(e, str(row.get("answer") or ""), row.get("form"))
        text = fill_slots(world, str(side.get("situation") or ""), row, e)[:TEXT_MAX["situation"]]
        if text:
            out.append(text)
    return out


def remember_line(world, e: Dict[str, Any], occ: Dict[str, Any]) -> str:
    """The `remember` board line (§12c; authored at RE-3, drawn from RE-R):
    the previous occurrence's answer side — the same template, the same
    subject where the template binds one (the Host's Claims: the same host),
    answered or lapsed — filled over THAT row (its `{month}`, its host); ""
    for a first letter."""
    mid = str(occ.get("id") or "")
    if not MO.is_occurrence(mid):
        return ""
    subject = row_subject(occ)
    previous = None
    for key, row in occurrences(world, MO.template_of(mid)):
        if key == mid:
            break
        if row.get("status") not in (MO.STATUS_ANSWERED, MO.STATUS_LAPSED):
            continue
        if subject and row_subject(row) != subject:
            continue
        previous = row
    if previous is None:
        return ""
    side = MO._answer_side(e, str(previous.get("answer") or ""), previous.get("form"))
    return fill_slots(world, str(side.get("remember") or ""), previous, e)[:TEXT_MAX["remember"]]
