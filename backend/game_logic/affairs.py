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
UNARMED: every function here returns at once and writes nothing — the shipped
1805 boot, until RE-3 arms the deck.

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
AFFAIR_OPS = ("gold", "authority", "admin", "dp", "relation", "loyalty", "enact_law")
AFFAIR_OP_BOUNDS = {"gold": (1, 2000), "authority": (-10, 0), "admin": (1, 1), "dp": (1, 2),
                    "relation": (-20, 20), "loyalty": (-20, 20)}
DECLINE_ALLOWED_OPS = ("relation", "loyalty", "authority")
BARRED_OPS = ("alarm", "autonomy")

# The display copy (§16b): what a letter SAYS, never when it arrives or what
# its answers do — struck from the measured identity (`_s14c_sweep_record`).
DISPLAY_KEYS = ("title", "voice", "record", "line", "counsel", "exhibit", "ground", "watch",
                "source", "button_line")
VARIANT_DISPLAY_KEYS = ("text",)
ANSWER_DISPLAY_KEYS = ("caption", "button_line", "echo", "press", "remember")
TEXT_MAX = {"title": 40, "record": 240, "variant": 240, "line": 200, "counsel": 160,
            "exhibit": 160, "watch": 120, "button_line": 40, "echo": 160, "press": 160,
            "remember": 160, "caption": 36, "source": 400}
VARIANT_FACTS = ("arrival",)        # P18: `last_fate` joins at RE-H with the fleet record
ARRIVAL_FIRST = "first"
ARRIVAL_LATER = "later"

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
    """The runtime store — created on first read of an ARMED world only, so
    an unarmed store (the shipped boot's) is never touched."""
    store = MO._store(world)
    rt = store.get("affairs")
    if not isinstance(rt, dict):
        rt = {}
        if store and armed(world):
            store["affairs"] = rt
    return rt


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


PREDICATES: Dict[str, Callable[[Any, str, Dict[str, Any]], Dict[str, Any]]] = {
    "sovereign_afield": _sovereign_afield,
    "corps_on_host": _corps_on_host,
    "staff_offered": _staff_offered,
}
# The parameters each predicate requires (the validator reads them).
PREDICATE_PARAMS: Dict[str, Tuple[str, ...]] = {
    "sovereign_afield": (),
    "corps_on_host": (),
    "staff_offered": ("law",),
}


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
    return int((runtime(world).get("streaks") or {}).get(_streak_key(str(e["id"]), subject), 0))


def latch_ok(world, e: Dict[str, Any]) -> bool:
    """P7: a template with a `latch` arrives only while its mask carries at
    least `at_least` set bits of the last `of` mornings."""
    latch = e.get("latch")
    if not isinstance(latch, dict):
        return True
    mask = int((runtime(world).get("masks") or {}).get(str(e["id"]), 0))
    return bin(mask).count("1") >= int(latch.get("at_least", 1) or 1)


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
    authority always bites; a lord without a tracker never does."""
    ops = [MO.scaled_op(op, tier) for op in ((e.get("decline") or {}).get("ops") or [])
           if isinstance(op, dict) and op.get("op") == "authority"]
    if not ops:
        return True
    if lord != getattr(world, "player_nation", None) or getattr(world, "authority_tracker", None) is None:
        return False
    from backend.models.authority import AURA_GRIP_FULL, get_imperial_grip
    grip = int(get_imperial_grip(world, lord))
    for op in ops:
        after = grip + int(op.get("amount", 0) or 0)
        if after < MO.AUTHORITY_GRIP_FLOOR or after >= AURA_GRIP_FULL:
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


def form_of(world, e: Dict[str, Any], cand: Dict[str, Any]) -> str:
    """P18: the form frozen at delivery — the first authored form (RE-H's
    squadron chooser replaces this); "" for an entry with none."""
    forms = e.get("forms")
    if isinstance(forms, dict) and forms:
        return str(next(iter(forms)))
    return ""


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
    MO.deliver_letter(world, e, turn, mid=mid, row=row)
    return mid


def write_receipt(world, line: str) -> None:
    """Seam AFN — the rows and notices: one `moment_receipt` dispatch line
    (the set-aside tally, a withdrawal)."""
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, RECEIPT_EVENT, {"line": str(line)}, "always")


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


def fill_slots(world, text: str, row: Dict[str, Any], **extra: Any) -> str:
    """The copy's slots over an occurrence row: `{host}`, `{seat}`,
    `{minister}` (the chancery fallback until RE-R names the ministers),
    `{region}`, `{lord}`, and the caller's figures (`n`, `m`)."""
    if not text:
        return ""
    bind = row.get("bind") if isinstance(row.get("bind"), dict) else {}
    slots = _Slots(extra)
    host = str(bind.get("host") or "")
    if host:
        display = MO._court(world, host, capitalize=True)
        slots.setdefault("host", display)
        slots.setdefault("seat", _seat_of(world, host))
        slots.setdefault("minister", f"the {display} chancery")
    slots.setdefault("region", str(bind.get("region") or ""))
    if row.get("lord"):
        slots.setdefault("lord", MO._court(world, str(row["lord"]), capitalize=True))
    try:
        return str(text).format_map(slots)
    except (ValueError, IndexError):
        return str(text)


def title_of(e: Dict[str, Any], occ: Dict[str, Any]) -> str:
    """The letter's title — the frozen form's when the entry authors forms."""
    forms = (e or {}).get("forms")
    form = (occ or {}).get("form")
    if form and isinstance(forms, dict) and isinstance(forms.get(str(form)), dict):
        title = forms[str(form)].get("title")
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
    """P18: the variant keyed by the occurrence's facts (`arrival`: first /
    later; `last_fate` joins at RE-H) — "" when none matches."""
    facts = {"arrival": _arrival_of(occ)}
    for variant in (e or {}).get("variants") or []:
        if not isinstance(variant, dict):
            continue
        key, value = str(variant.get("key") or ""), str(variant.get("value") or "")
        if key in facts and facts[key] == value:
            return str(variant.get("text") or "")
    return ""


def record_text(world, e: Dict[str, Any], occ: Dict[str, Any]) -> str:
    """The ground (every arrival) and the chapter (by the occurrence's facts),
    in the moments' "Historically …" frame."""
    ground = fill_slots(world, str((e or {}).get("record") or ""), occ)
    chapter = fill_slots(world, chapter_of(e, occ), occ)
    return f"{ground} {chapter}".strip() if chapter else ground


def board_lines(world, e: Dict[str, Any], occ: Dict[str, Any]) -> List[str]:
    """The premise's facts, named — read live at every read (the IGR-2
    lesson), the tier frozen (§5)."""
    try:
        return [str(x) for x in _board(world, e, occ) if x]
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
        region = str(bind.get("region") or (read.get("bind") or {}).get("region") or "the field")
        return [f"The Emperor is afield at {region}, {streak} mornings running; his standing is {standing}."]
    if predicate == "corps_on_host":
        host = str(bind.get("host") or "")
        if not host:
            return []
        from backend.game_logic.diplomacy import STATE_RELATION_THRESHOLDS
        corps = int(read.get("measure") or 0) if (read.get("bind") or {}).get("host") == host else 0
        state = world.get_diplomatic_state(lord, host)
        display = MO._court(world, host, capitalize=True)
        lines = [f"{corps} of your corps stand on {display}'s soil ({MO._standing(world, lord, host)}, "
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
        return [f"At war {streak} turns running; the Staff is not in force; the chest holds "
                f"{int(purse_of(world, lord)[1]):,} gold against {price:,} now and {upkeep:,} a turn."]
    return []


def watch(world) -> List[str]:
    """§12 — the Watch: at most two "may" lines a morning, the nearest-due
    templates' `watch` strings over the premise's own measures (`{n}` the
    measure, `{m}` the streak, `{host}`); nothing standing, on cooldown or
    capped. RE-2 renders them; a line shown is remembered (`watched`) for
    the set-aside tally (§7)."""
    if not armed(world):
        return []
    turn = MO._turn(world)
    rt = runtime(world)
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
        streak = streak_of(world, e, subject)
        measure = read.get("measure")
        measure = streak if measure is None else int(measure)
        text = fill_slots(world, str(e.get("watch") or ""),
                          {"bind": read.get("bind") or {}, "lord": lord}, n=measure, m=streak)
        rows.append((max(0, int(e.get("streak", 1) or 1) - streak), index, template, text))
    rows.sort()
    watched = rt.setdefault("watched", {})
    out: List[str] = []
    for _distance, _index, template, text in rows[:2]:
        if text:
            out.append(text)
            watched[template] = int(turn)
    return out
