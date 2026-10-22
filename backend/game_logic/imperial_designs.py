"""VP-1 "The Emperor's Designs" — France's own objectives (Pre-Deploy S14b;
the gate record `docs/VP1_DESIGNS_SPEC.md`, RULED October 22, 2026).

Three ROADS of two designs each — a construction, then a seal — chosen by an
irreversible proclamation. The designs live in their OWN store,
`world.imperial_designs` (the record's A1: the agenda substrate's schema,
predicates and payload shapes, never `world.agendas` — no AI code reads this
store, so a France deck there would move every AI arm):

    {"block": <the scenario's authored `imperial_designs` key>,
     "state": {"road", "proclaimed_turn", "prologue_turn", "fulfilled",
               "rewarded", "hold", "terms", "britain_signed", "acts"}}

A world with no authored block is UNARMED: every reader here answers None /
False / 0 and nothing is shown (the bare flag world and the tutorial; the
shipped 1805 boot is armed from S14b part 2). Every predicate is nation-parameterized
on the block's authored `owner`; the roads are player CONTENT (an asymmetry of
content, as the minors have no laws), never of code.

The seams the series attribution holds down (`tools/_vp1_series_arms.py`):
`note_ratification` (the terms latch), `drift_suspended` (the Rhine's shield),
`order_decay` (the Continent's order) and `decisive_peace_released` (the
stamp — released by S14b part 3, with the register, the client and the arms).

The Acts of the Empire (the record §5 — SF-ECON-1 absorbed) are authored in
the block's `acts` list and decreed once each (`state.acts`, {act: turn}).
"""
from __future__ import annotations

import copy
import math
from typing import Any, Dict, Iterable, List, Optional, Tuple

from backend.errors import report

# ── Roads, design types, manners (closed sets — the record §0 Q7, §2) ──────
ROAD_RHINE = "rhine"
ROAD_CROWNS = "crowns"
ROAD_SYSTEM = "system"
ROADS = (ROAD_RHINE, ROAD_CROWNS, ROAD_SYSTEM)

ROLE_CONSTRUCTION = "construction"
ROLE_SEAL = "seal"

TYPE_CLIENTS = "clients"                    # 2.1
TYPE_BROUGHT_TO_TERMS = "brought_to_terms"  # 2.2
TYPE_TITLED = "titled"                      # 2.3
TYPE_TITLED_AND_TERMS = "titled_and_terms"  # 2.4
TYPE_SHUT_PORTS = "shut_ports"              # 2.5
TYPE_BRITAIN_SIGNS = "britain_signs"        # 2.6
DESIGN_TYPES = (TYPE_CLIENTS, TYPE_BROUGHT_TO_TERMS, TYPE_TITLED,
                TYPE_TITLED_AND_TERMS, TYPE_SHUT_PORTS, TYPE_BRITAIN_SIGNS)

GATE_ALLY_OR_VASSAL = "ally_or_vassal"
GATE_VASSAL = "vassal"
GATE_AT_WAR_WITH_TRADE_DOMINANCE = "at_war_with_trade_dominance"
GATE_TYPES = (GATE_ALLY_OR_VASSAL, GATE_VASSAL, GATE_AT_WAR_WITH_TRADE_DOMINANCE)

MANNER_SUBJUGATION = "subjugation"
MANNER_PARTITION = "partition"
MANNER_MODERATE = "moderate"
# One closed set, in precedence order (one treaty that reads two takes the first).
MANNERS = (MANNER_SUBJUGATION, MANNER_PARTITION, MANNER_MODERATE)

# ── In-band tunables (the record §8; all ints) ─────────────────────────────
SATELLITE_TITLE_LOYALTY = 40   # the province_title_kind line, one named constant
CLIENTS_HOLD_DEFAULT = 4
PORTS_HOLD_DEFAULT = 6         # K — reported per seed, never moved to fit an arm
TITLED_HOLD_DEFAULT = 1
PARTITION_MIN_PROVINCES = 2    # or her capital
MODERATE_MIN_CESSIONS = 1
VOLTE_FACE_WINDOW = 20         # turns from the moderate peace to her alliance
CS_ORDER_DECAY = 2             # the Continent's order (2.5's reward)
NAPLES_AUTHORITY = 15          # 2.3's one-shot reward
PROCLAIM_DP_COST = 2           # §8: the proclamation's price
PROCLAIM_ADMIN_COST = 1
DECISIVE_PEACE_ALARM = 15      # §4 / §8: the reward, never below the Armed Peace's watch
ACT_ADMIN_COST = 1             # §5: each Act's administrative action

# The Cabinet row every surface names (the user's rule: diplomacy is never
# typed — the proclamation's one player road is the road page's button).
DESIGNS_CONTROL = "F1 → The Emperor's Designs"

# Condition (c) (the record §0) — printed verbatim by the desk's goal answer.
CONDITION_C = ("A campaign is for deciding what Napoleon's empire will be — "
               "Protector of the Rhine, master of Italy from Milan to Naples, or "
               "a Continent shut against Britain — and forcing the decisive peace "
               "that seals it, while the coalitions you provoke, the satellites' "
               "bills and the Verdict of History in July 1807 judge the reign; the "
               "Congress of Paris, where Europe signs or is shut out, crowns the "
               "greatest.")

# The prologue (the record §3): the first war-ending peace with one of these
# courts, or their capital taken, while no road is proclaimed.
PROLOGUE_COURTS = ("Austria", "Russia")


# ════════════════════════════════════════════════════════════════════════
# The store
# ════════════════════════════════════════════════════════════════════════

def fresh_state() -> Dict[str, Any]:
    return {"road": "", "proclaimed_turn": -1, "prologue_turn": -1,
            "fulfilled": {}, "rewarded": [], "hold": {}, "terms": {},
            "britain_signed": {}, "acts": {}}


def from_block(block: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """The store a boot (or a backfill) seeds from the authored block — {} when
    the scenario authors none (unarmed)."""
    if not isinstance(block, dict) or not block.get("roads"):
        return {}
    return {"block": copy.deepcopy(block), "state": fresh_state()}


def store_from_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """ONE shape for the scenario and the save (the doctrines idiom): a
    scenario's `imperial_designs` key is the authored block (`owner`,
    `roads`); a save's is the store (`block`, `state`). Comment keys dropped;
    {} when neither (unarmed)."""
    raw = (data or {}).get("imperial_designs")
    if not isinstance(raw, dict):
        return {}
    if isinstance(raw.get("block"), dict):
        block = {k: copy.deepcopy(v) for k, v in raw["block"].items() if not str(k).startswith("_")}
        if not block.get("roads"):
            return {}
        state = fresh_state()
        state.update(copy.deepcopy(raw.get("state") or {}))
        return {"block": block, "state": state}
    block = {k: copy.deepcopy(v) for k, v in raw.items() if not str(k).startswith("_")}
    return from_block(block)


def _store(world) -> Dict[str, Any]:
    store = getattr(world, "imperial_designs", None)
    return store if isinstance(store, dict) else {}


def armed(world) -> bool:
    return bool(_store(world).get("block"))


def _state(world) -> Dict[str, Any]:
    store = _store(world)
    state = store.get("state")
    if not isinstance(state, dict):
        state = fresh_state()
        if store:
            store["state"] = state
    for key, default in fresh_state().items():
        state.setdefault(key, copy.deepcopy(default))
    return state


def owner(world) -> str:
    return str((_store(world).get("block") or {}).get("owner") or "")


def roads(world) -> List[Dict[str, Any]]:
    return [r for r in ((_store(world).get("block") or {}).get("roads") or [])
            if isinstance(r, dict)]


def road(world, road_id: str) -> Optional[Dict[str, Any]]:
    return next((r for r in roads(world) if r.get("id") == road_id), None)


def designs_of(road_row: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [d for d in ((road_row or {}).get("designs") or []) if isinstance(d, dict)]


def design(world, design_id: str) -> Optional[Dict[str, Any]]:
    for r in roads(world):
        for d in designs_of(r):
            if d.get("id") == design_id:
                return d
    return None


def proclaimed_road(world) -> str:
    return str(_state(world).get("road") or "") if armed(world) else ""


def is_fulfilled(world, design_id: str) -> bool:
    return design_id in (_state(world).get("fulfilled") or {})


def fulfilled_turn(world, design_id: str) -> Optional[int]:
    """The turn a design was stamped fulfilled (the turn that ENDED), or None
    — a public reader beside `is_fulfilled` (S14c: the Reich letter's lag
    counts from it, `docs/EVENTS_SPEC.md` §3.6)."""
    turn = (_state(world).get("fulfilled") or {}).get(design_id) if armed(world) else None
    return None if turn is None else int(turn)


ROAD_STATE_PROCLAIMED = "proclaimed"
ROAD_STATE_FORSWORN = "forsworn"
ROAD_STATE_OPEN = "open"


def road_state(world, road_id: str) -> str:
    """S14C-X17: the ONE reading of a road against the proclamation —
    "proclaimed" (it is the Emperor's road), "forsworn" (another road was
    proclaimed; irreversible), "open" (no road yet, or an unarmed world).
    Every "forsworn" test in this module, the moments' road gate and the
    payload's flags route through it (a census pins that none re-derives
    it)."""
    chosen = proclaimed_road(world)
    if not chosen:
        return ROAD_STATE_OPEN
    return ROAD_STATE_PROCLAIMED if chosen == road_id else ROAD_STATE_FORSWORN


# ════════════════════════════════════════════════════════════════════════
# Readings — pure reads of live state (the record §2)
# ════════════════════════════════════════════════════════════════════════

def _turn(world) -> int:
    return int(getattr(world, "current_turn", 0) or 0)


def _gone(world, nation: str) -> bool:
    try:
        return nation not in set(world.get_active_nations())
    except Exception as exc:
        report(exc, "imperial_designs._gone: world.get_active_nations")
        return False


def _top(world, nation: str) -> str:
    try:
        return str(world._top_overlord(nation) or nation)
    except Exception as exc:
        report(exc, "imperial_designs._top: world._top_overlord")
        return nation


def _loyalty(world, nation: str) -> int:
    row = (getattr(world, "vassals", {}) or {}).get(nation) or {}
    return int(row.get("loyalty", 0) or 0)


def _bloc_holds(world, lord: str, region_name: str) -> bool:
    from backend.game_logic.agendas import _controlled_by_self_or_vassal
    return bool(_controlled_by_self_or_vassal(world, lord, region_name))


def client_rows(world, lord: str, courts: Iterable[str]) -> List[Dict[str, Any]]:
    """2.1's rows: each named court, whether it stands under the lord's
    protection (its top overlord the lord, loyalty at the title line), and why
    not. A court that is gone counts when its capital is titled to the lord's
    bloc (`province_title_kind`)."""
    from backend.game_logic.game_end import province_title_kind
    rows = []
    for court in courts:
        court = str(court)
        if _gone(world, court):
            capital = world.get_nation_capital(court) or ""
            ok = bool(capital) and province_title_kind(world, capital, lord) in (
                "homeland", "treaty", "conquest")
            rows.append({"court": court, "member": ok, "gone": True,
                         "loyalty": 0, "why": "gone — its capital titled" if ok else "gone"})
            continue
        under = court != lord and _top(world, court) == lord
        loyalty = _loyalty(world, court) if under else 0
        member = under and loyalty >= SATELLITE_TITLE_LOYALTY
        if member:
            why = "under the Emperor's protection"
        elif under:
            why = f"loyalty {loyalty} of {SATELLITE_TITLE_LOYALTY}"
        else:
            why = str(world.get_diplomatic_state(lord, court)).lower()
        rows.append({"court": court, "member": bool(member), "gone": False,
                     "loyalty": int(loyalty), "why": why})
    return rows


def ports_reading(world, lord: str) -> Dict[str, int]:
    """2.5: (shut, needed, total) against the trade-dominance court. `needed`
    is DERIVED from the Congress's SHUT OUT line, never tuned."""
    from backend.game_logic import naval
    from backend.game_logic.game_end import cfg
    target = naval.trade_dominance_nation(world)
    total = int(naval.continental_ports_total(world) or 0)
    pct = int(cfg(world, "cs_shutout_pct", 50) or 50)
    needed = int(math.ceil(pct * total / 100.0)) if total else 0
    shut = int(naval.closed_ports_against(world, target)) if target else 0
    return {"shut": shut, "needed": needed, "total": total, "gone": int(target is None)}


def terms_met(world, lord: str, court: str) -> Tuple[bool, str]:
    """2.2 / 2.4: is the court brought to terms — an unbroken latch in
    `state.terms`, a subjugation standing, or the moderate peace followed by
    her alliance inside the window. Returns (met, manner)."""
    rec = (_state(world).get("terms") or {}).get(court) or {}
    if not rec or rec.get("broken"):
        return False, ""
    manner = str(rec.get("manner") or "")
    if manner == MANNER_SUBJUGATION:
        return _top(world, court) == lord or _gone(world, court), manner
    if manner == MANNER_PARTITION:
        return True, manner
    if manner == MANNER_MODERATE:
        if rec.get("allied_turn", -1) >= 0:
            return True, manner
        return False, manner
    return False, manner


def design_reading(world, d: Dict[str, Any]) -> Dict[str, Any]:
    """One design's live reading: held / required / met, and its rows."""
    lord = owner(world)
    dtype = str(d.get("type") or "")
    out: Dict[str, Any] = {"id": d.get("id"), "type": dtype, "met": False,
                           "held": 0, "required": 0}
    if dtype == TYPE_CLIENTS:
        rows = client_rows(world, lord, d.get("courts") or [])
        need = int(d.get("need", 3) or 3)
        held = sum(1 for r in rows if r["member"])
        out.update(rows=rows, held=held, required=need, met=held >= need)
    elif dtype in (TYPE_TITLED, TYPE_TITLED_AND_TERMS):
        from backend.game_logic.game_end import province_title_kind
        provinces = [str(p) for p in (d.get("provinces") or [])]
        kinds = {p: province_title_kind(world, p, lord) for p in provinces}
        held = sum(1 for k in kinds.values() if k in ("homeland", "treaty", "conquest"))
        out.update(provinces=kinds, held=held, required=len(provinces),
                   met=bool(provinces) and held == len(provinces))
        if dtype == TYPE_TITLED_AND_TERMS:
            courts = [str(c) for c in (d.get("courts") or [])]
            terms = {c: terms_met(world, lord, c) for c in courts}
            out["terms"] = {c: {"met": m, "manner": mn} for c, (m, mn) in terms.items()}
            out["met"] = out["met"] and any(m for m, _mn in terms.values())
    elif dtype == TYPE_BROUGHT_TO_TERMS:
        courts = [str(c) for c in (d.get("courts") or [])]
        terms = {c: terms_met(world, lord, c) for c in courts}
        out.update(terms={c: {"met": m, "manner": mn} for c, (m, mn) in terms.items()},
                   held=sum(1 for m, _mn in terms.values() if m), required=1,
                   met=any(m for m, _mn in terms.values()))
    elif dtype == TYPE_SHUT_PORTS:
        p = ports_reading(world, lord)
        out.update(ports=p, held=p["shut"], required=p["needed"],
                   met=bool(p["gone"]) or (p["needed"] > 0 and p["shut"] >= p["needed"]))
    elif dtype == TYPE_BRITAIN_SIGNS:
        signed = _state(world).get("britain_signed") or {}
        out.update(held=int(bool(signed.get("qualified"))), required=1,
                   met=bool(signed.get("qualified")), signed=dict(signed))
    return out


def gate_met(world, road_row: Dict[str, Any]) -> bool:
    gate = road_row.get("gate") or {}
    lord = owner(world)
    gtype = str(gate.get("type") or "")
    court = str(gate.get("court") or "")
    if gtype == GATE_ALLY_OR_VASSAL:
        return bool(court) and (world.are_allies(lord, court) or _top(world, court) == lord)
    if gtype == GATE_VASSAL:
        return bool(court) and court != lord and _top(world, court) == lord
    if gtype == GATE_AT_WAR_WITH_TRADE_DOMINANCE:
        from backend.game_logic import naval
        target = naval.trade_dominance_nation(world)
        return bool(target) and bool(world.is_at_war(lord, target))
    return False


def _hold_needed(d: Dict[str, Any]) -> int:
    dtype = str(d.get("type") or "")
    default = {TYPE_CLIENTS: CLIENTS_HOLD_DEFAULT, TYPE_SHUT_PORTS: PORTS_HOLD_DEFAULT,
               TYPE_TITLED: TITLED_HOLD_DEFAULT}.get(dtype, 1)
    return max(1, int(d.get("hold", default) or default))


# ════════════════════════════════════════════════════════════════════════
# The proclamation (the core; the verb and the Cabinet page are part 2's)
# ════════════════════════════════════════════════════════════════════════

def proclaim_refusal(world, road_id: str, nation: Optional[str] = None) -> Optional[str]:
    """The ONE predicate the executor, the road page's row and the counsel
    ask (the record §3). None when the proclamation may be made."""
    if not armed(world):
        return "The Empire has no road to proclaim."
    lord = owner(world)
    if nation is not None and nation != lord:
        return f"{nation} proclaims no design of the Empire's."
    row = road(world, road_id)
    if row is None:
        return f"No road of the Empire is named {road_id!r}."
    state = _state(world)
    if state.get("road"):
        chosen = road(world, state["road"]) or {}
        return (f"The Emperor proclaimed {chosen.get('proclamation') or chosen.get('title')} "
                f"on turn {int(state.get('proclaimed_turn', 0))}; the choice cannot be undone.")
    from backend.game_logic import fall, game_end
    if game_end.terminal_ending(world) is not None:
        return "The reign has ended."
    capital = world.get_nation_capital(lord) or ""
    region = (getattr(world, "regions", {}) or {}).get(capital)
    if region is not None and region.controller != lord:
        return f"{capital} is lost; no design is proclaimed from exile."
    sov = fall.sovereign_of(world, lord)
    if sov is not None and getattr(sov, "captured_by", ""):
        return "The Emperor is a prisoner; no design is proclaimed in chains."
    if _top(world, lord) != lord:
        return "France is another court's vassal."
    if not gate_met(world, row):
        return f"{row.get('title')}: {(row.get('gate') or {}).get('reason') or 'its gate is closed'}."
    return None


def price_refusal(world, road_id: str) -> Optional[str]:
    """The proclamation's WHOLE refusal, in the order the player meets it —
    the ONE predicate the road page's button, the counsel and the executor's
    own pre-gates read (shown = applied). The shared executor refuses an
    administrative order with no action left before the verb runs, so that
    comes first; then `proclaim_refusal`; then the diplomatic points."""
    if not armed(world):
        return proclaim_refusal(world, road_id)
    if int(getattr(world, "admin_actions_remaining", 0) or 0) < PROCLAIM_ADMIN_COST:
        return "No administrative actions remaining this turn."
    refusal = proclaim_refusal(world, road_id)
    if refusal:
        return refusal
    dp = int(getattr(world, "diplomatic_points", 0) or 0)
    if dp < PROCLAIM_DP_COST:
        return (f"The proclamation takes {PROCLAIM_DP_COST} diplomatic points — "
                f"the Cabinet holds {dp}.")
    return None


def resolve_road(world, words: str) -> str:
    """The road a typed or clicked line names — its id, its title, its
    proclamation or a plain word of either ("the Rhine", "Italy", "the
    Continental System"). "" when none, or more than one, is named."""
    import re as _re
    text = _re.sub(r"\s+", " ", str(words or "").lower()).strip()
    text = _re.sub(r"\bconfirm(?:ed)?\s*$", "", text).strip()
    text = _re.sub(r"^(?:the\s+)?(?:road\s+of\s+)?", "", text).strip()
    if not text:
        return ""
    hits = []
    for r in roads(world):
        names = [str(r.get("id") or ""), str(r.get("title") or ""),
                 str(r.get("proclamation") or "")]
        names += [str(a) for a in (r.get("aliases") or [])]
        forms = set()
        for n in names:
            n = n.lower().strip()
            if not n:
                continue
            forms.add(n)
            if n.startswith("the "):
                forms.add(n[4:])
        if text in forms or any(text == f or (len(text) >= 4 and text in f) for f in forms):
            hits.append(str(r.get("id")))
    return hits[0] if len(set(hits)) == 1 else ""


def proclaim(world, road_id: str) -> Dict[str, Any]:
    """Proclaim a road (irreversible): the state written once and the
    proclamation's teeth applied (the record §2 per road; §8). Returns
    {success, message, road}. The executor (part 2) prices the actions and
    DP before it calls this."""
    refusal = proclaim_refusal(world, road_id)
    if refusal:
        return {"success": False, "message": refusal}
    row = road(world, road_id) or {}
    state = _state(world)
    state["road"] = road_id
    state["proclaimed_turn"] = _turn(world)
    _apply_teeth(world, row.get("teeth_proclaim") or {}, source=str(row.get("alarm_source") or road_id))
    _log(world, "proclaimed", road=road_id,
         title=str(row.get("proclamation") or row.get("title") or road_id))
    return {"success": True, "road": road_id,
            "message": f"{row.get('proclamation') or row.get('title')} is proclaimed."}


def _apply_teeth(world, teeth: Dict[str, Any], source: str) -> None:
    lord = owner(world)
    alarm = int(teeth.get("alarm", 0) or 0)
    if alarm:
        try:
            from backend.game_logic.coalition import add_threat
            add_threat(world, alarm, source)
        except Exception as exc:
            report(exc, "imperial_designs._apply_teeth: coalition.add_threat")
    for court, delta in sorted((teeth.get("relations") or {}).items()):
        if court and court != lord and int(delta or 0):
            world.modify_nation_relation(lord, str(court), int(delta))


# ════════════════════════════════════════════════════════════════════════
# The terms latch — `note_ratification`, called by game_end.note_ratification
# (the ONE chokepoint both top-level ratifiers pass) for every treaty
# ════════════════════════════════════════════════════════════════════════

def _homeland(world, nation: str) -> set:
    return set((getattr(world, "nation_starting_regions", {}) or {}).get(nation, []) or [])


def manner_for_terms(world, victor: str, court: str,
                     terms: Iterable[Dict[str, Any]]) -> str:
    """The manner a war-ending treaty brings `court` to terms in, read off the
    treaty's own terms after its clauses applied — "" for none (a status quo,
    an indemnity). Nation-parameterized; precedence `MANNERS`. Ruling C's two
    Pressburgs and ruling J stand unchanged: the cession list is netted by
    `compensation_offsets` exactly as the Revanche line nets it, so the
    manner and `revanche_line_for_terms` can never disagree — PARTITION is
    the punitive record (two homeland provinces or the capital, net),
    MODERATE a cession compensated below it."""
    from backend.game_logic.compensation import compensation_offsets, net_of_compensation
    terms = [t for t in (terms or []) if isinstance(t, dict)]
    if court != victor and _top(world, court) == victor:
        return MANNER_SUBJUGATION
    home = _homeland(world, court)
    ceded: List[str] = []
    for t in terms:
        ttype = str(t.get("type") or "")
        if str(t.get("from") or t.get("from_nation") or "") != court:
            continue
        if ttype in ("territory_cede", "territory"):
            receiver = str(t.get("to") or t.get("to_nation") or "")
            if not receiver or _top(world, receiver) != victor:
                continue
            regions = list(t.get("regions") or ([t.get("region")] if t.get("region") else []))
        elif ttype == "create_client":
            regions = list(t.get("provinces") or [])
        else:
            continue
        ceded.extend(str(r) for r in regions if str(r) in home)
    if not ceded:
        return ""
    capital = world.get_nation_capital(court) or ""
    offset = int(compensation_offsets(terms).get(court, 0) or 0)
    net = net_of_compensation(world, court, sorted(set(ceded)), offset)
    if len(set(net)) >= PARTITION_MIN_PROVINCES or (capital and capital in net):
        return MANNER_PARTITION
    if offset and len(set(ceded)) >= MODERATE_MIN_CESSIONS:
        return MANNER_MODERATE
    return ""


def seal_courts(world) -> List[str]:
    """The courts a road's seal brings to terms (2.2, 2.4) — the ones a
    peace's manner is read for."""
    out: List[str] = []
    for r in roads(world):
        for d in designs_of(r):
            if d.get("type") in (TYPE_BROUGHT_TO_TERMS, TYPE_TITLED_AND_TERMS):
                out += [str(c) for c in (d.get("courts") or []) if str(c) not in out]
    return out


def manner_line(world, court: str, clauses) -> str:
    """VP1-X7: the manner of THIS peace with a seal's court, read off the
    clause list the ratifier builds (`treaty_clauses_of` / the table's
    settlement terms) by the same reading the terms latch applies
    (`manner_for_terms`, the homeland guard) — shown = applied. '' for a
    court no seal names, and where no designs are authored."""
    if not armed(world) or owner(world) != getattr(world, "player_nation", None):
        return ""
    if court not in seal_courts(world):
        return ""
    from backend.display_names import humanize_entity_name as _h
    lord = owner(world)
    who = _h(court)
    manner = manner_for_terms(world, lord, court, list(clauses or []))
    if manner and not _guard_homeland_whole(world, lord, court):
        return (f"The manner of this peace: {MANNER_WORDS[manner]} — but while {who}'s bloc "
                f"holds French soil, the Emperor's designs record nothing of it.")
    if manner == MANNER_PARTITION:
        return f"The manner of this peace: a partition — it brings {who} to terms."
    if manner == MANNER_SUBJUGATION:
        return f"The manner of this peace: subjugation — {who} is brought to terms as the Emperor's vassal."
    if manner == MANNER_MODERATE:
        return (f"The manner of this peace: the moderate peace — {who} is brought to terms "
                f"once she allies with the Emperor within {VOLTE_FACE_WINDOW} turns.")
    return (f"The manner of this peace: none — it brings {who} to no terms the Emperor's "
            f"designs read (two of her own provinces or her capital, her vassalage, or a "
            f"compensated cession).")


MANNER_WORDS = {MANNER_PARTITION: "a partition", MANNER_SUBJUGATION: "subjugation",
                MANNER_MODERATE: "the moderate peace"}


def peace_lines(world, court: str, clauses) -> Dict[str, str]:
    """The bilateral surfaces' pair (VP1-X7): the manner and the Revanche,
    from ONE clause list."""
    from backend.game_logic.emergent_designs import revanche_line_for_terms
    clauses = list(clauses or [])
    manner = (manner_for_terms(world, owner(world), court, clauses)
              if armed(world) and court in seal_courts(world) else "")
    return {"manner": manner, "manner_line": manner_line(world, court, clauses),
            "revanche_line": revanche_line_for_terms(world, clauses)}


def table_manner_lines(world, covered, terms) -> List[Dict[str, str]]:
    """The table's per-court manner lines, for the seal courts it covers."""
    out = []
    for court in sorted(str(c) for c in (covered or [])):
        line = manner_line(world, court, terms)
        if line:
            out.append({"court": court, "line": line})
    return out


def _guard_homeland_whole(world, lord: str, court: str) -> bool:
    """No province of the lord's opening homeland stands in the court's bloc."""
    regions = getattr(world, "regions", {}) or {}
    for name in _homeland(world, lord):
        region = regions.get(name)
        holder = getattr(region, "controller", None) if region is not None else None
        if holder and _top(world, holder) == _top(world, court) and holder != lord \
                and _top(world, holder) != lord:
            return False
    return True


def note_ratification(world, *, terms: Iterable[Dict[str, Any]],
                      counterparts: Iterable[str], war_ending: bool) -> None:
    """Record the owner's terms with each counterpart court — a FACT, written
    before any proclamation (the record §3: a Pressburg on turn 7 seals the
    road proclaimed on turn 8) — and the trade-dominance court's qualifying
    signature for 2.6. Called by `game_end.note_ratification`, which passes
    counterparts only for a treaty the player signed (both top-level
    ratifiers), so an AI–AI treaty never reaches the owner's state."""
    if not armed(world) or not war_ending:
        return
    lord = owner(world)
    if lord != getattr(world, "player_nation", None):
        return
    parties = [str(c) for c in (counterparts or []) if c and str(c) != lord]
    if not parties:
        return
    terms = [dict(t) for t in (terms or []) if isinstance(t, dict)]
    state = _state(world)
    turn = _turn(world)
    for court in parties:
        manner = manner_for_terms(world, lord, court, terms)
        if manner and _guard_homeland_whole(world, lord, court):
            state["terms"][court] = {"manner": manner, "turn": turn, "broken": False,
                                     "allied_turn": -1}
    for court in parties:
        if court in PROLOGUE_COURTS:
            _maybe_prologue(world, court)
            break
    from backend.game_logic import naval
    target = naval.trade_dominance_nation(world)
    if target and target in parties and is_fulfilled(world, _construction_of(world, ROAD_SYSTEM)):
        lifted = any(t.get("type") == "continental_system_lifted" for t in terms)
        majors = _system_great_powers(world, lord)
        whole = _homeland_whole(world, lord)
        state["britain_signed"] = {"turn": turn, "members": sorted(majors),
                                   "lifted": bool(lifted), "homeland_whole": bool(whole),
                                   "qualified": bool(majors) and not lifted and whole}


def note_war(world, a: str, b: str) -> None:
    """A new war between the lord and a court breaks that court's terms latch."""
    if not armed(world):
        return
    lord = owner(world)
    other = b if a == lord else a if b == lord else ""
    if not other:
        return
    rec = (_state(world).get("terms") or {}).get(other)
    if rec and not rec.get("broken"):
        rec["broken"] = True
        rec["broken_turn"] = _turn(world)


def _system_great_powers(world, lord: str) -> List[str]:
    from backend.game_logic.coalition import _CANONICAL_MAJORS
    members = list(getattr(world, "continental_system_members", []) or [])
    return [m for m in members
            if m in _CANONICAL_MAJORS and m != lord and _top(world, m) != lord]


def _homeland_whole(world, lord: str) -> bool:
    regions = getattr(world, "regions", {}) or {}
    for name in _homeland(world, lord):
        region = regions.get(name)
        if region is None:
            continue
        if region.controller != lord and _top(world, str(region.controller or "")) != lord:
            return False
    return True


def _construction_of(world, road_id: str) -> str:
    for d in designs_of(road(world, road_id)):
        if d.get("role") == ROLE_CONSTRUCTION:
            return str(d.get("id"))
    return ""


def _seal_of(world, road_id: str) -> str:
    for d in designs_of(road(world, road_id)):
        if d.get("role") == ROLE_SEAL:
            return str(d.get("id"))
    return ""


# ════════════════════════════════════════════════════════════════════════
# The tick — holds, latches, lapses, rewards (game_end.process_end_of_turn)
# ════════════════════════════════════════════════════════════════════════

def _log(world, phase: str, **fields) -> None:
    """The designs' one chronicle row (`imperial_design`, by phase) — the
    log, the front page and Le Moniteur read it."""
    if not hasattr(world, "log_event"):
        return
    event = {"type": "imperial_design", "phase": phase, "nation": owner(world)}
    event.update({k: v for k, v in fields.items() if v is not None})
    world.log_event(event)


def prologue_court(world) -> str:
    """The court whose capital stands in the owner's bloc (the prologue's
    second trigger, read at the tick) — "" for none."""
    lord = owner(world)
    for court in PROLOGUE_COURTS:
        capital = world.get_nation_capital(court) or ""
        region = (getattr(world, "regions", {}) or {}).get(capital)
        holder = str(getattr(region, "controller", "") or "") if region is not None else ""
        if holder and holder != court and _top(world, holder) == lord:
            return court
    return ""


def _maybe_prologue(world, court: str = "") -> None:
    """THE SUN OF AUSTERLITZ (the record §3, copy only): the first war-ending
    peace with Austria or Russia (`court`, from the ratification note), or
    her capital taken (read at the tick), while no road is proclaimed — once
    (`state.prologue_turn`, across a load). No reward."""
    state = _state(world)
    if int(state.get("prologue_turn", -1)) >= 0 or state.get("road"):
        return
    if owner(world) != getattr(world, "player_nation", None):
        return
    court = court or prologue_court(world)
    if not court:
        return
    state["prologue_turn"] = _turn(world)
    rec = (state.get("terms") or {}).get(court) or {}
    _log(world, "prologue", court=court, manner=str(rec.get("manner") or ""))


def prologue_counsel(world, court: str, manner: str) -> str:
    """Talleyrand's road counsel on the prologue: which seal the peace
    already satisfies, read off the roads (a reading, not a lookup)."""
    from backend.display_names import humanize_entity_name as _h
    sealed = []
    for r in roads(world):
        for d in designs_of(r):
            if d.get("role") == ROLE_SEAL and court in [str(c) for c in (d.get("courts") or [])]:
                sealed.append(str(r.get("title") or r.get("id")))
    who = _h(court)
    if manner and sealed:
        roads_named = " and ".join(sealed)
        return (f"Talleyrand: \"The peace with {who} brings her to terms ({manner}) — "
                f"{roads_named} would count it as {'its' if len(sealed) == 1 else 'their'} "
                f"seal's, Sire, if you proclaim one. The roads wait in the Cabinet "
                f"({DESIGNS_CONTROL}).\"")
    return (f"Talleyrand: \"{who} has bent, Sire — now say what the Empire is for. "
            f"The roads wait in the Cabinet ({DESIGNS_CONTROL}).\"")


def _note_alliances(world) -> None:
    """The moderate peace's second half: her alliance with the lord inside
    `VOLTE_FACE_WINDOW` turns of the peace (the volte-face's own chokepoint
    lands an ALLIANCE state; this reads it)."""
    lord = owner(world)
    turn = _turn(world)
    for court, rec in (_state(world).get("terms") or {}).items():
        if rec.get("broken") or rec.get("manner") != MANNER_MODERATE:
            continue
        if int(rec.get("allied_turn", -1)) >= 0:
            continue
        if turn - int(rec.get("turn", 0)) > VOLTE_FACE_WINDOW:
            continue
        if world.get_diplomatic_state(lord, court) == "ALLIANCE":
            rec["allied_turn"] = turn


def tick(world, turn_ended: int) -> List[Dict[str, Any]]:
    """Advance the holds of the proclaimed road's designs, latch, mark lapses
    and pay the one-shot rewards. Returns the fulfilment events of this tick
    (the dispatch beats are part 2's). Pure no-op unarmed or unproclaimed."""
    if not armed(world):
        return []
    state = _state(world)
    _note_alliances(world)
    _maybe_prologue(world)
    road_id = state.get("road") or ""
    if not road_id:
        return []
    events: List[Dict[str, Any]] = []
    for d in designs_of(road(world, road_id)):
        did = str(d.get("id"))
        reading = design_reading(world, d)
        if did in state["fulfilled"]:
            continue
        if reading["met"]:
            state["hold"][did] = int(state["hold"].get(did, 0)) + 1
        else:
            state["hold"][did] = 0
        if state["hold"][did] >= _hold_needed(d):
            state["fulfilled"][did] = int(turn_ended)
            events.append({"type": "design_fulfilled", "design": did,
                           "road": road_id, "turn": int(turn_ended)})
            _pay_one_shot(world, d)
            _apply_teeth(world, d.get("teeth_fulfil") or {},
                         source=str(d.get("alarm_source") or did))
            _log(world, "fulfilled", road=road_id, design=did,
                 title=str(d.get("title") or did), role=str(d.get("role") or ""))
    return events


def holds(world, design_id: str) -> bool:
    """A latched design's live reading still holds (False: it reads lapsed)."""
    if not is_fulfilled(world, design_id):
        return False
    d = design(world, design_id)
    return bool(d) and bool(design_reading(world, d)["met"])


def _pay_one_shot(world, d: Dict[str, Any]) -> None:
    reward = d.get("reward") or {}
    state = _state(world)
    if reward.get("type") != "authority" or d.get("id") in state["rewarded"]:
        return
    tracker = getattr(world, "authority_tracker", None)
    if tracker is not None:
        tracker.modify_authority(int(reward.get("amount", NAPLES_AUTHORITY) or NAPLES_AUTHORITY))
    state["rewarded"].append(d.get("id"))


# ── The live-gated reward seams (held down by the series arms) ─────────────

def _live_reward(world, road_id: str, reward_type: str) -> Optional[Dict[str, Any]]:
    if road_state(world, road_id) != ROAD_STATE_PROCLAIMED:
        return None
    for d in designs_of(road(world, road_id)):
        if d.get("role") == ROLE_CONSTRUCTION and (d.get("reward") or {}).get("type") == reward_type:
            return d if holds(world, str(d.get("id"))) else None
    return None


def drift_suspended(world, nation: str) -> bool:
    """2.1's reward (A3): a Confederation member's downward autonomy drift is
    suspended while the Rhine construction holds. Read by
    `vassal.process_vassal_loyalty` at its drift term."""
    if not armed(world):
        return False
    d = _live_reward(world, ROAD_RHINE, "drift_shield")
    if d is None:
        return False
    return nation in [str(c) for c in (d.get("courts") or [])] and _top(world, nation) == owner(world)


def order_decay(world, nation: str) -> int:
    """2.5's reward: the owner's alarm decays `CS_ORDER_DECAY` more each turn
    while the Blockade holds. Read by `coalition._calculate_threat_decay`."""
    if not armed(world) or nation != owner(world):
        return 0
    d = _live_reward(world, ROAD_SYSTEM, "order_decay")
    if d is None:
        return 0
    return int((d.get("reward") or {}).get("amount", CS_ORDER_DECAY) or CS_ORDER_DECAY)


# ════════════════════════════════════════════════════════════════════════
# THE DECISIVE PEACE — the rule (the record §4); the stamp is part 3's
# ════════════════════════════════════════════════════════════════════════

DECISIVE_PEACE_SOURCE = "decisive_peace"
# The treaty each sealing court signs (the record §4), named by its court.
TREATY_NAMES = {"Austria": "the Peace of Pressburg", "Prussia": "the Peace of Tilsit"}
SYSTEM_TREATY = "the Peace of the Continent"


def decisive_peace_released() -> bool:
    """The stamp's seam: released by S14b part 3 (the record §9) — the rule
    computed from part 1, the stamp, the fifth register and the arms. A
    FUNCTION seam, never a module lever (the code-health ratchet): the series
    attribution holds it down with `--seam … =False`."""
    return True


def treaty_name(road_id: str, court: str) -> str:
    """The treaty that seals a road: "the Peace of Pressburg" (Austria),
    "the Peace of Tilsit" (Prussia), "the Peace of the Continent" (the
    System's)."""
    if road_id == ROAD_SYSTEM:
        return SYSTEM_TREATY
    if court in TREATY_NAMES:
        return TREATY_NAMES[court]
    from backend.display_names import humanize_entity_name as _h
    return f"the peace with {_h(court)}" if court else "the decisive peace"


def stamp_decisive_peace(world, turn_ended: int) -> Optional[Dict[str, Any]]:
    """THE DECISIVE PEACE (the record §4) — the ONE place the cause is
    stamped, called by `game_end.process_end_of_turn` right after `tick` (a
    design that latched this tick completes it the same turn) and before the
    Verdict (which grades its +2). Once per campaign, the owner the player,
    all six conditions holding. The reward: Europe's alarm −15, never below
    the Armed Peace's watch (45). Mark and continue. Returns the record."""
    if not decisive_peace_released() or not armed(world) or not proclaimed_road(world):
        return None
    if owner(world) != getattr(world, "player_nation", None):
        return None
    from backend.game_logic import game_end
    if (game_end.has_ending(world, game_end.CAUSE_DECISIVE_PEACE)
            or game_end.terminal_ending(world) is not None):
        return None
    reading = decisive_peace_reading(world)
    if not reading["ready"]:
        return None
    road_id = proclaimed_road(world)
    row = road(world, road_id) or {}
    state = _state(world)
    lord = owner(world)
    court = str(reading.get("court") or "")
    from backend.game_logic import coalition as _co
    before = int((getattr(world, "threat_by_target", {}) or {}).get(lord, 0) or 0)
    cut = min(int(DECISIVE_PEACE_ALARM), max(0, before - int(_co.ARMED_PEACE_WATCH)))
    detail = {
        "route": road_id, "numeral": _ROAD_NUMERALS.get(road_id, ""),
        "road_title": str(row.get("title") or road_id),
        "court": court, "manner": str(reading.get("manner") or ""),
        "treaty": treaty_name(road_id, court),
        "designs": [{"id": str(d.get("id")), "title": str(d.get("title") or d.get("id")),
                     "role": str(d.get("role") or ""),
                     "fulfilled_turn": int((state.get("fulfilled") or {}).get(str(d.get("id")), -1))}
                    for d in designs_of(row)],
        "proclaimed_turn": int(state.get("proclaimed_turn", -1)),
        "turn": int(turn_ended),
        "alarm_from": before, "alarm_to": before - cut,
    }
    record = game_end.record_ending(world, "victory", game_end.CAUSE_DECISIVE_PEACE,
                                    detail=detail, turn=int(turn_ended))
    if record is None:
        return None
    if cut > 0:
        _co.reduce_threat(world, cut, DECISIVE_PEACE_SOURCE)
    return record


def decisive_record(world) -> Optional[Dict[str, Any]]:
    """The stamped DECISIVE PEACE, or None (VP1-X20: every surface that spoke
    of it as ahead reads it once it is made)."""
    from backend.game_logic import game_end
    return next((r for r in game_end.endings(world)
                 if r.get("cause") == game_end.CAUSE_DECISIVE_PEACE), None)


def decisive_made_line(world) -> str:
    """"THE DECISIVE PEACE was made on turn 5 — the Peace of Pressburg; the
    Congress of Paris still waits." — or "" before the stamp."""
    rec = decisive_record(world)
    if rec is None:
        return ""
    treaty = str((rec.get("detail") or {}).get("treaty") or "the decisive peace")
    return (f"THE DECISIVE PEACE was made on turn {int(rec.get('turn', 0) or 0)} — {treaty}; "
            f"the Congress of Paris still waits.")


def cause_line(detail: Optional[Dict[str, Any]]) -> str:
    """The end screen's lead sentence for THE DECISIVE PEACE
    (`game_end._cause_line`) — from the stamp's own detail only."""
    from backend.display_names import humanize_entity_name as _h
    detail = detail or {}
    treaty = str(detail.get("treaty") or "the decisive peace")
    treaty = treaty[0].upper() + treaty[1:]
    court = str(detail.get("court") or "")
    numeral = str(detail.get("numeral") or "")
    road_title = _mid(str(detail.get("road_title") or "the road"))
    title = f"Road {numeral}, {road_title}," if numeral else road_title
    if detail.get("route") == ROAD_SYSTEM:
        return (f"{treaty}: {_h(court) if court else 'Britain'} signs, and the Continent "
                f"stays shut — {title} is sealed.")
    manner = MANNER_WORDS.get(str(detail.get("manner") or ""), "")
    construction = next((str(d.get("title") or "") for d in detail.get("designs") or []
                         if d.get("role") == ROLE_CONSTRUCTION), "")
    how = f" by {manner}" if manner else ""
    holds = f", and {_mid(construction)} holds" if construction else ""
    return f"{treaty}: {_h(court)} is brought to terms{how}{holds} — {title} is sealed."


def summary_block(detail: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """THE DECISIVE PEACE's card block (`build_campaign_summary`) — the road,
    its two designs and the treaty, from the ending's OWN detail (the summary
    is persisted at the stamp; the live road moves on)."""
    detail = detail or {}
    numeral = str(detail.get("numeral") or "")
    proclaimed = int(detail.get("proclaimed_turn", -1))
    road_line = (f"Road {numeral}, {detail.get('road_title') or ''}"
                 + (f" — proclaimed on turn {proclaimed}" if proclaimed >= 0 else ""))
    rows = []
    for d in detail.get("designs") or []:
        turn = int(d.get("fulfilled_turn", -1))
        rows.append({"id": str(d.get("id") or ""),
                     "line": (f"{d.get('title')} — fulfilled on turn {turn}" if turn >= 0
                              else str(d.get("title") or ""))})
    alarm_from, alarm_to = int(detail.get("alarm_from", 0) or 0), int(detail.get("alarm_to", 0) or 0)
    alarm = (f"Europe's alarm cools from {alarm_from} to {alarm_to}" if alarm_from > alarm_to
             else f"Europe's alarm holds at {alarm_to}")
    return {"route": str(detail.get("route") or ""), "road_line": road_line, "designs": rows,
            "treaty_line": (f"{alarm}; the Verdict of History counts the decisive peace. "
                            f"The Congress of Paris still waits.")}


def decisive_headline_line(detail: Optional[Dict[str, Any]]) -> str:
    """The morning's front page on the stamp (the dispatch's `decisive_peace`
    class) — the cause line and what it is a waypoint to."""
    return (f"THE DECISIVE PEACE — {cause_line(detail)} The reign goes on: the "
            f"Congress of Paris still waits.")


def moniteur_caption(detail: Optional[Dict[str, Any]]) -> str:
    """Le Moniteur's special on the stamp — "THE PEACE OF PRESSBURG" (a
    `gazette._SPECIAL_WEIGHTS` key per treaty)."""
    treaty = str((detail or {}).get("treaty") or "")
    if treaty in TREATY_NAMES.values() or treaty == SYSTEM_TREATY:
        return treaty.upper()
    return "THE DECISIVE PEACE"


def decisive_peace_reading(world) -> Dict[str, Any]:
    """The six conditions of §4, each named — `ready` when all hold."""
    out: Dict[str, Any] = {"ready": False, "conditions": {}, "court": "", "manner": ""}
    if not armed(world):
        return out
    lord = owner(world)
    road_id = proclaimed_road(world)
    conds: Dict[str, bool] = {"proclaimed": bool(road_id)}
    construction, seal = _construction_of(world, road_id), _seal_of(world, road_id)
    conds["both_latched"] = bool(construction) and bool(seal) and \
        is_fulfilled(world, construction) and is_fulfilled(world, seal)
    if road_id == ROAD_SYSTEM:
        signed = _state(world).get("britain_signed") or {}
        members = [m for m in (signed.get("members") or [])
                   if m in (getattr(world, "continental_system_members", []) or [])]
        conds["construction_holds"] = bool(members)
        from backend.game_logic import naval
        court = str(naval.trade_dominance_nation(world) or "")
        manner = "the_continent"
    else:
        conds["construction_holds"] = holds(world, construction)
        court, manner = _sealing_court(world, seal)
    out["court"], out["manner"] = court, manner
    state_with = world.get_diplomatic_state(lord, court) if court else ""
    conds["sealing_court_at_peace"] = bool(court) and (
        state_with not in ("WAR", "ARMISTICE") or _gone(world, court)
        or _top(world, court) == lord)
    from backend.game_logic import fall, game_end
    capital = world.get_nation_capital(lord) or ""
    region = (getattr(world, "regions", {}) or {}).get(capital)
    sov = fall.sovereign_of(world, lord)
    clocks = getattr(world, "fall_clock", {}) or {}
    conds["realm_free"] = (region is None or region.controller == lord) \
        and not (sov is not None and getattr(sov, "captured_by", "")) \
        and _top(world, lord) == lord \
        and not any(int((v or {}).get("turns", 0) or 0) > 0 for v in clocks.values()
                    if isinstance(v, dict)) \
        and not game_end.has_ending(world, game_end.CAUSE_HUMBLED)
    conds["homeland_whole"] = _homeland_held_against(world, lord, court)
    out["conditions"] = conds
    out["ready"] = all(conds.values())
    return out


def _sealing_court(world, seal_id: str) -> Tuple[str, str]:
    lord = owner(world)
    d = design(world, seal_id) or {}
    for court in [str(c) for c in (d.get("courts") or [])]:
        met, manner = terms_met(world, lord, court)
        if met:
            return court, manner
    return "", ""


def _homeland_held_against(world, lord: str, court: str) -> bool:
    """No province of the lord's opening homeland held by the sealing court's
    bloc or by a court at war with the lord."""
    regions = getattr(world, "regions", {}) or {}
    for name in _homeland(world, lord):
        region = regions.get(name)
        holder = str(getattr(region, "controller", "") or "") if region is not None else ""
        if not holder or holder == lord or _top(world, holder) == lord:
            continue
        if court and _top(world, holder) == _top(world, court):
            return False
        if world.is_at_war(lord, holder):
            return False
    return True


# ════════════════════════════════════════════════════════════════════════
# The Acts of the Empire (the record §5 — SF-ECON-1 absorbed): `decree_act`,
# a peace-road gold sink on the proclaimed road. Each one-shot, gold and one
# administrative action, one refusal and one price; effects from a closed set
# (authority, relation, client_loyalty); alarm through `add_threat`. Never
# income, never war score, never a design completed alone.
# ════════════════════════════════════════════════════════════════════════

ACT_ALARM_SOURCE = "acts_of_the_empire"
ACT_ANY_ROAD = "any"
ACT_EFFECT_TYPES = ("authority", "relation", "client_loyalty")
ACT_PRECONDITION_TYPES = ("vassal", "great_power_beaten")


def acts(world) -> List[Dict[str, Any]]:
    return [a for a in ((_store(world).get("block") or {}).get("acts") or [])
            if isinstance(a, dict)]


def act(world, act_id: str) -> Optional[Dict[str, Any]]:
    return next((a for a in acts(world) if str(a.get("id")) == act_id), None)


def act_decreed_turn(world, act_id: str) -> int:
    value = (_state(world).get("acts") or {}).get(act_id)
    return int(value) if isinstance(value, int) and not isinstance(value, bool) else -1


def decree_command(a: Dict[str, Any]) -> str:
    """The line the road page's Decree button sends."""
    return f"decree {a.get('title')}"


def resolve_act(world, words: str) -> str:
    """The Act a line names — its id, its title or an alias (a leading
    "the", the case, an apostrophe and the confirm marker ignored). "" for
    none, or more than one."""
    import re as _re

    def _norm(text: str) -> str:
        text = _re.sub(r"\s+", " ", str(text or "").lower().replace("’", "'")).strip()
        text = _re.sub(r"\bconfirm(?:ed)?\s*$", "", text).strip()
        text = _re.sub(r"^(?:the\s+)", "", text).strip()
        return text.replace("'", "")

    want = _norm(words)
    if not want:
        return ""
    hits = []
    for a in acts(world):
        names = {_norm(a.get("id") or "").replace("_", " "), _norm(a.get("title") or "")}
        names |= {_norm(x) for x in (a.get("aliases") or []) if isinstance(x, str)}
        if want in names or want.replace("_", " ") in names:
            hits.append(str(a.get("id")))
    return hits[0] if len(hits) == 1 else ""


def _is_client(world, court: str) -> bool:
    row = (getattr(world, "vassals", {}) or {}).get(court) or {}
    return bool(court) and court != owner(world) and row.get("lord") == owner(world)


def act_beaten_court(world, a: Dict[str, Any]) -> str:
    """The Raft's court: the first of its courts at war with the owner whom
    the owner has beaten — a province of her homeland in the owner's bloc, or
    her war score against him at or below the act's line. "" for none."""
    pre = a.get("precondition") or {}
    if pre.get("type") != "great_power_beaten":
        return ""
    lord = owner(world)
    line = int(pre.get("war_score", -25) or -25)
    from backend.game_logic.diplomacy import live_war_score_for
    for court in [str(c) for c in (pre.get("courts") or [])]:
        if _gone(world, court) or not world.is_at_war(lord, court):
            continue
        if any(_bloc_holds(world, lord, prov) for prov in sorted(_homeland(world, court))):
            return court
        if int(live_war_score_for(world, court, lord)) <= line:
            return court
    return ""


def act_precondition_reason(world, a: Dict[str, Any]) -> str:
    """The board-won precondition, in words — "" when it holds or none."""
    from backend.display_names import humanize_entity_name as _h
    from backend.campaign_log import and_join
    pre = a.get("precondition") or {}
    kind = pre.get("type")
    courts = [str(c) for c in (pre.get("courts") or [])]
    if kind == "vassal":
        missing = [c for c in courts if not _is_client(world, c)]
        if missing:
            return (f"{a.get('title')} needs {and_join([_h(c) for c in missing])} as the "
                    f"Emperor's vassal first.")
    elif kind == "great_power_beaten" and not act_beaten_court(world, a):
        names = [_h(c) for c in courts]
        either = (", ".join(names[:-1]) + " or " + names[-1]) if len(names) > 1 else "".join(names)
        return (f"{a.get('title')} needs a great power at war with the Empire beaten first "
                f"({either}): a province of hers held, or her war score driven to "
                f"{int(pre.get('war_score', -25) or -25)}.")
    return ""


def act_price(world, a: Dict[str, Any]) -> int:
    """The Act's ONE price — gold, no arrears (the quote, the row and the
    charge read it)."""
    return int(a.get("price", 0) or 0)


def act_refusal(world, act_id: str, admin_actions: Optional[int] = None) -> Optional[str]:
    """The Act's WHOLE refusal, in the order the player meets it — the shared
    executor's administrative pre-gate first (`price_refusal`'s idiom), then
    once-only, the road, the board's precondition and the gold. The ONE
    predicate the verb, the road page's Decree row and the morning's sink
    read (shown = applied). None when it can be decreed."""
    if not armed(world):
        return "There are no Acts of the Empire in this campaign, Sire."
    a = act(world, act_id)
    if a is None:
        return "There is no such Act of the Empire, Sire."
    admin = (int(getattr(world, "admin_actions_remaining", 0) or 0)
             if admin_actions is None else int(admin_actions))
    if admin < ACT_ADMIN_COST:
        return "No administrative actions remaining this turn."
    title = str(a.get("title") or act_id)
    turn = act_decreed_turn(world, act_id)
    if turn >= 0:
        return f"{title} was decreed on turn {turn} — an Act of the Empire is decreed once."
    chosen = proclaimed_road(world)
    want = str(a.get("road") or ACT_ANY_ROAD)
    if not chosen:
        return (f"{title} serves a road of the Empire, Sire — proclaim one first "
                f"({DESIGNS_CONTROL}).")
    if want != ACT_ANY_ROAD and road_state(world, want) == ROAD_STATE_FORSWORN:
        mine, other = road(world, want) or {}, road(world, chosen) or {}
        return (f"{title} belongs to Road {_ROAD_NUMERALS.get(want, '')}, {mine.get('title')} — "
                f"forsworn when the Emperor proclaimed {other.get('title')}.")
    reason = act_precondition_reason(world, a)
    if reason:
        return reason
    price = act_price(world, a)
    chest = int((getattr(world, "nation_gold", {}) or {}).get(owner(world), 0) or 0)
    if chest < price:
        return f"{title} costs {price:,} gold; the treasury holds {chest:,}."
    return None


def act_effect_lines(world, a: Dict[str, Any]) -> List[str]:
    """The Act's effects in words, as `decree` applies them."""
    from backend.display_names import humanize_entity_name as _h
    out: List[str] = []
    for e in a.get("effects") or []:
        if not isinstance(e, dict):
            continue
        kind, amount = e.get("type"), int(e.get("amount", 0) or 0)
        if kind == "authority":
            out.append(f"authority +{amount}")
        elif kind == "relation":
            if e.get("pick") == "beaten":
                court = act_beaten_court(world, a)
                out.append(f"relations with {_h(court)} +{amount}" if court
                           else f"relations +{amount} with the great power beaten")
            else:
                courts = [str(c) for c in (e.get("courts") or []) if not _gone(world, str(c))]
                if courts:
                    out.append("relations: " + ", ".join(f"{_h(c)} +{amount}" for c in courts))
        elif kind == "client_loyalty":
            held = [str(c) for c in (e.get("courts") or []) if _is_client(world, str(c))]
            out.append(("loyalty: " + ", ".join(f"{_h(c)} +{amount}" for c in held)) if held
                       else f"loyalty +{amount} for the Emperor's vassals among them (none yet)")
    alarm = int(a.get("alarm", 0) or 0)
    if alarm:
        out.append(f"Europe's alarm +{alarm}")
    return out


def decree(world, act_id: str) -> Dict[str, Any]:
    """The ONE mutation (shown = applied): the gold the quote names leaves the
    chest, the effects apply, Europe's alarm rises, the turn is recorded."""
    a = act(world, act_id) or {}
    lord = owner(world)
    price = act_price(world, a)
    lines = act_effect_lines(world, a)
    beaten = act_beaten_court(world, a)
    world.nation_gold[lord] = int(world.nation_gold.get(lord, 0) or 0) - price
    if hasattr(world, "record_gold_spent"):
        world.record_gold_spent(lord, price)
    for e in a.get("effects") or []:
        if not isinstance(e, dict):
            continue
        kind, amount = e.get("type"), int(e.get("amount", 0) or 0)
        if kind == "authority":
            tracker = getattr(world, "authority_tracker", None)
            if tracker is not None:
                tracker.modify_authority(amount)
        elif kind == "relation":
            courts = [beaten] if e.get("pick") == "beaten" else [str(c) for c in (e.get("courts") or [])]
            for court in courts:
                if court and court != lord and not _gone(world, court):
                    world.modify_nation_relation(lord, court, amount)
        elif kind == "client_loyalty":
            from backend.game_logic.vassal import LOYALTY_MAX
            for court in [str(c) for c in (e.get("courts") or [])]:
                if _is_client(world, court):
                    row = world.vassals[court]
                    row["loyalty"] = int(min(LOYALTY_MAX, int(row.get("loyalty", 0) or 0) + amount))
    alarm = int(a.get("alarm", 0) or 0)
    if alarm:
        try:
            from backend.game_logic.coalition import add_threat
            add_threat(world, alarm, ACT_ALARM_SOURCE)
        except Exception as exc:
            report(exc, "imperial_designs.decree: coalition.add_threat")
    _state(world)["acts"][act_id] = _turn(world)
    _log(world, "decreed", act=act_id, title=str(a.get("title") or act_id), price=price)
    return {"price": price, "lines": lines, "title": str(a.get("title") or act_id)}


def act_rows(world) -> List[Dict[str, Any]]:
    """The road page's Decree rows — every Act with its price, effects, the
    Charges' relief, and the executor's own refusal as its disabled reason."""
    out: List[Dict[str, Any]] = []
    lord = owner(world)
    chosen = proclaimed_road(world)
    for a in acts(world):
        aid = str(a.get("id"))
        want = str(a.get("road") or ACT_ANY_ROAD)
        price = act_price(world, a)
        refusal = act_refusal(world, aid)
        relief = (int(world.charges_relief(lord, price))
                  if price > 0 and hasattr(world, "charges_relief") else 0)
        out.append({
            "id": aid, "title": str(a.get("title") or aid), "date": str(a.get("date") or ""),
            "says": str(a.get("says") or ""), "road": want,
            "road_numeral": "" if want == ACT_ANY_ROAD else _ROAD_NUMERALS.get(want, ""),
            "price": price, "admin_cost": int(ACT_ADMIN_COST), "relief": relief,
            "effects_line": "; ".join(act_effect_lines(world, a)),
            "decreed_turn": act_decreed_turn(world, aid),
            "forsworn": want != ACT_ANY_ROAD and road_state(world, want) == ROAD_STATE_FORSWORN,
            "available": refusal is None, "disabled_reason": refusal or "",
            "command": decree_command(a),
        })
    return out


def act_sink(world, nation: str) -> Optional[Dict[str, Any]]:
    """The morning's peace-road sink once no law is left to buy (the record
    §5; `reforms.peace_sink_law`'s idiom): at peace — no war, no truce — the
    first Act the chest can decree, its administrative term set aside (the
    morning reads it before the day's first order). None otherwise."""
    if world is None or nation != getattr(world, "player_nation", None) or nation != owner(world):
        return None
    if not proclaimed_road(world):
        return None
    for key, dstate in (getattr(world, "diplomatic_states", None) or {}).items():
        if dstate in ("WAR", "ARMISTICE") and nation in str(key).split("|"):
            return None
    for a in acts(world):
        if act_refusal(world, str(a.get("id")), admin_actions=ACT_ADMIN_COST) is None:
            return {"act": str(a.get("id")), "title": str(a.get("title")), "price": act_price(world, a)}
    return None


def act_sink_line(world, nation: str) -> str:
    """The dispatch's treasury note — "the chest could decree the Temple of
    Glory — 8,000g" — or ""."""
    sink = act_sink(world, nation)
    if sink is None:
        return ""
    return f"the chest could decree {_mid(sink['title'])} — {sink['price']:,}g"


def progress_line(world, reading: Dict[str, Any]) -> str:
    """One design's progress in its own nouns — the held / required shape of
    `formations.format_progress`, worded per type (courts, provinces, ports,
    a court brought to terms, a signature)."""
    from backend.display_names import humanize_entity_name as _h
    held, need = int(reading.get("held", 0)), int(reading.get("required", 0))
    dtype = reading.get("type")
    if dtype == TYPE_CLIENTS:
        return f"{held} of {need} courts under the Emperor's protection"
    if dtype == TYPE_TITLED:
        noun = "province" if need == 1 else "provinces"
        return f"{held} of {need} {noun} titled to the Empire"
    if dtype == TYPE_SHUT_PORTS:
        from backend.game_logic import naval
        from backend.display_names import display_nation
        p = reading.get("ports") or {}
        target = naval.trade_dominance_nation(world)
        whom = display_nation(target) if target else "the mistress of the seas"
        return (f"{int(p.get('shut', 0))} of {int(p.get('total', 0))} ports shut to {whom}"
                f" — {int(p.get('needed', 0))} needed")
    terms = reading.get("terms") or {}
    met = [f"{_h(c)} ({t['manner']})" for c, t in sorted(terms.items()) if t.get("met")]
    if dtype == TYPE_BROUGHT_TO_TERMS:
        return ("brought to terms: " + ", ".join(met)) if met else "no crown brought to terms yet"
    if dtype == TYPE_TITLED_AND_TERMS:
        courts = ", ".join(_h(c) for c in sorted(terms)) or "the court"
        tail = (f" · {courts} brought to terms" if met else f" · {courts} not yet brought to terms")
        return f"{held} of {need} provinces titled to the Empire{tail}"
    if dtype == TYPE_BRITAIN_SIGNS:
        from backend.game_logic import naval
        from backend.display_names import display_nation
        target = naval.trade_dominance_nation(world)
        whom = display_nation(target) if target else "The mistress of the seas"
        return f"{whom} has signed the peace" if reading.get("met") else f"{whom} has not signed"
    return f"{held} of {need}"


# ════════════════════════════════════════════════════════════════════════
# The payload — built on every read (no cache: it reads a handful of courts,
# at most three provinces and the port list, never a scan of the regions, and
# a mid-turn treaty or a new satellite must show on the same turn)
# ════════════════════════════════════════════════════════════════════════

_ROAD_NUMERALS = {ROAD_RHINE: "I", ROAD_CROWNS: "II", ROAD_SYSTEM: "III"}


def proclaim_command(road_row: Dict[str, Any]) -> str:
    """The line the road page's Proclaim button sends (the executor parses
    it to `proclaim_design`; the quote answers it first)."""
    return f"proclaim {str(road_row.get('title') or road_row.get('id') or '')}"


def teeth_line(world, teeth: Dict[str, Any]) -> str:
    """The teeth in words — the alarm and each court's relation, as applied."""
    from backend.display_names import humanize_entity_name as _h
    parts = []
    alarm = int((teeth or {}).get("alarm", 0) or 0)
    if alarm:
        parts.append(f"Europe's alarm {alarm:+d}")
    rel = [f"{_h(court)} {int(delta):+d}".replace("-", "−")
           for court, delta in sorted(((teeth or {}).get("relations") or {}).items())
           if int(delta or 0)]
    if rel:
        parts.append("relations: " + ", ".join(rel))
    return "; ".join(parts)


def reward_line(d: Dict[str, Any]) -> str:
    reward = d.get("reward") or {}
    rtype = reward.get("type")
    if rtype == "drift_shield":
        return ("While it holds, the Protector's shield: a member's autonomy drift "
                "is suspended.")
    if rtype == "order_decay":
        amount = int(reward.get("amount", CS_ORDER_DECAY) or CS_ORDER_DECAY)
        return (f"While it holds, the Continent's order: Europe's alarm cools "
                f"{amount} more a turn.")
    if rtype == "authority":
        amount = int(reward.get("amount", NAPLES_AUTHORITY) or NAPLES_AUTHORITY)
        return f"Once: +{amount} authority."
    if d.get("role") == ROLE_SEAL:
        return "With its construction holding: the decisive peace."
    return ""


def _links(world, d: Dict[str, Any], reading: Dict[str, Any]) -> List[Dict[str, str]]:
    """The courts each hint names — a deep link to the court's own Cabinet
    page (the controls live there), never a typed line."""
    from backend.display_names import humanize_entity_name as _h
    dtype = reading.get("type")
    courts: List[str] = []
    if dtype == TYPE_CLIENTS:
        courts = [r["court"] for r in (reading.get("rows") or [])
                  if not r.get("member") and not r.get("gone")]
    elif dtype in (TYPE_BROUGHT_TO_TERMS, TYPE_TITLED_AND_TERMS, TYPE_TITLED):
        lord = owner(world)
        for prov, kind in (reading.get("provinces") or {}).items():
            region = (getattr(world, "regions", {}) or {}).get(prov)
            holder = str(getattr(region, "controller", "") or "") if region is not None else ""
            if not kind and holder and _top(world, holder) != lord and holder not in courts:
                courts.append(holder)
        courts += [c for c, t in (reading.get("terms") or {}).items()
                   if not t.get("met") and c not in courts]
    elif dtype == TYPE_SHUT_PORTS:
        # The courts whose ports stand open, the most ports first — a peace's
        # Continental System clause, a war or a satellite shuts them.
        from backend.game_logic import naval
        target = naval.trade_dominance_nation(world)
        if target:
            open_rows = sorted(((n, int(ports)) for n, ports, closed
                                in naval.ports_by_court_against(world, target) if not closed),
                               key=lambda kv: (-kv[1], kv[0]))
            courts = [n for n, _ports in open_rows]
    elif dtype == TYPE_BRITAIN_SIGNS:
        from backend.game_logic import naval
        target = naval.trade_dominance_nation(world)
        courts = [str(target)] if target else []
    active = set(world.get_active_nations()) if hasattr(world, "get_active_nations") else None
    out = []
    for court in courts:
        if active is not None and court not in active:
            continue
        out.append({"court": court, "label": _h(court)})
    return out[:4]


def _hold_line(d: Dict[str, Any], hold: int, need: int, fulfilled: int, lapsed: bool,
               met: bool) -> str:
    if fulfilled >= 0:
        return (f"fulfilled on turn {fulfilled} — lapsed: it no longer holds" if lapsed
                else f"fulfilled on turn {fulfilled}")
    if need > 1:
        return f"held {hold} of {need} end turns" if met or hold else f"to be held {need} end turns"
    return ""


def build_designs_payload(world) -> Optional[Dict[str, Any]]:
    """The ONE payload every surface reads (the record §6) — ints, strings and
    bools only, None on an unarmed world."""
    if not armed(world):
        return None
    state = _state(world)
    chosen = state.get("road") or ""
    chosen_row = road(world, chosen) if chosen else None
    out_roads = []
    for r in roads(world):
        rid = str(r.get("id"))
        designs = []
        for d in designs_of(r):
            did = str(d.get("id"))
            reading = design_reading(world, d)
            hold = int(state["hold"].get(did, 0))
            need = int(_hold_needed(d))
            fulfilled = int(state["fulfilled"].get(did, -1))
            lapsed = did in state["fulfilled"] and not reading["met"]
            status = ("lapsed" if lapsed else "fulfilled" if fulfilled >= 0
                      else "met" if reading["met"] else "open")
            designs.append({
                "id": did, "title": str(d.get("title") or did),
                "role": str(d.get("role") or ""),
                "role_display": "the construction" if d.get("role") == ROLE_CONSTRUCTION else "the seal",
                "held": int(reading["held"]), "required": int(reading["required"]),
                "progress": progress_line(world, reading),
                "met": bool(reading["met"]),
                "hold": hold, "hold_needed": need,
                "hold_line": _hold_line(d, hold, need, fulfilled, lapsed, bool(reading["met"])),
                "fulfilled_turn": fulfilled,
                "lapsed": lapsed, "status": status,
                "hint": str(d.get("hint") or ""),
                "control": str(d.get("control") or ""),
                "reward_line": reward_line(d),
                "links": _links(world, d, reading),
            })
        proclaimed = road_state(world, rid) == ROAD_STATE_PROCLAIMED
        forsworn = road_state(world, rid) == ROAD_STATE_FORSWORN
        refusal = proclaim_refusal(world, rid) or ""
        disabled = "" if (proclaimed or forsworn) else (price_refusal(world, rid) or "")
        gate = r.get("gate") or {}
        out_roads.append({
            "id": rid, "numeral": _ROAD_NUMERALS.get(rid, ""),
            "title": str(r.get("title") or rid),
            "proclamation": str(r.get("proclamation") or ""),
            "gate_met": bool(gate_met(world, r)),
            "gate_reason": str(gate.get("reason") or ""),
            "teeth_line": teeth_line(world, r.get("teeth_proclaim") or {}),
            "proclaimed": proclaimed,
            "forsworn": forsworn,
            "forsworn_line": (f"Forsworn when the Emperor proclaimed "
                              f"{str((chosen_row or {}).get('proclamation') or chosen)} "
                              f"on turn {int(state.get('proclaimed_turn', 0))}."
                              if forsworn else ""),
            "refusal": refusal,
            "available": not (proclaimed or forsworn) and not disabled,
            "disabled_reason": disabled,
            "command": proclaim_command(r),
            "dp_cost": int(PROCLAIM_DP_COST), "admin_cost": int(PROCLAIM_ADMIN_COST),
            "designs": designs,
        })
    if chosen_row:
        headline = (f"{str(chosen_row.get('proclamation') or chosen_row.get('title'))} "
                    f"was proclaimed on turn {int(state.get('proclaimed_turn', 0))}: "
                    f"{str(chosen_row.get('title'))}.")
        made = decisive_made_line(world)        # VP1-X20
        if made:
            headline += " " + made
    else:
        headline = ("No road is proclaimed. Three roads — one proclamation, and it "
                    "cannot be undone.")
    payload = {"owner": owner(world), "road": chosen,
               "proclaimed_turn": int(state.get("proclaimed_turn", -1)),
               "headline": headline, "condition_c": CONDITION_C,
               "control": DESIGNS_CONTROL,
               "dp_available": int(getattr(world, "diplomatic_points", 0) or 0),
               "admin_available": int(getattr(world, "admin_actions_remaining", 0) or 0),
               "roads": out_roads,
               # S14b part 3: the Acts of the Empire — the page's Decree rows.
               "acts": act_rows(world)}
    return payload


def wizard_row(world) -> Optional[Dict[str, Any]]:
    """The Cabinet's step-1 row: one line, read off the payload."""
    payload = build_designs_payload(world)
    if payload is None:
        return None
    chosen = next((r for r in payload["roads"] if r["proclaimed"]), None)
    if chosen is None:
        line = "no road proclaimed — three roads, one choice that cannot be undone"
    else:
        line = f"Road {chosen['numeral']}, {chosen['title']}: " + "; ".join(
            f"{d['title']} — {d['progress']}" for d in chosen["designs"])
    return {"line": line, "road": payload["road"], "control": DESIGNS_CONTROL}


def designs_clock(world) -> Optional[Dict[str, Any]]:
    """The dispatch's clock (beside the Congress's): printed once a road is
    proclaimed — each design's progress and its hold, read off the payload."""
    payload = build_designs_payload(world)
    if payload is None or not payload["road"]:
        return None
    chosen = next((r for r in payload["roads"] if r["proclaimed"]), None)
    if chosen is None:
        return None
    parts = []
    severity = "gate"
    for d in chosen["designs"]:
        tail = f" ({d['hold_line']})" if d["hold_line"] else ""
        mark = "✓" if d["status"] == "fulfilled" else "✗" if d["status"] == "lapsed" else "•"
        parts.append(f"{mark} {d['title']}: {d['progress']}{tail}")
        if d["status"] == "lapsed":
            severity = "warning"
    return {"line": f"Road {chosen['numeral']}, {chosen['title']} — " + " · ".join(parts),
            "severity": severity, "road": chosen["id"]}


def realm_reading(world) -> Dict[str, Any]:
    """What the dispatch remembers each morning of the proclaimed road (the
    `headline_lead_memory["designs"]` key — the extra-keys idiom): each
    design's held count, its hold and its status. {} before a proclamation,
    so an unproclaimed world writes nothing (and builds no payload)."""
    if not proclaimed_road(world):
        return {}
    payload = build_designs_payload(world)
    chosen = next((r for r in (payload or {}).get("roads") or [] if r["proclaimed"]), None)
    if chosen is None:
        return {}
    return {d["id"]: {"held": int(d["held"]), "hold": int(d["hold"]), "status": str(d["status"])}
            for d in chosen["designs"]}


def realm_line(world, told: Optional[Dict[str, Any]]) -> str:
    """The quiet morning's realm line (the record §6.3, `realm_designs`):
    the proclaimed design whose count moved since the last morning, one that
    lapsed, or one a single end turn from holding — read off the payload, in
    the progress line's own nouns. '' when nothing moved (a fulfilment is
    event news of its own, and the first morning after the proclamation has
    nothing told to move from)."""
    if not isinstance(told, dict) or not told:
        return ""
    payload = build_designs_payload(world)
    chosen = next((r for r in (payload or {}).get("roads") or [] if r["proclaimed"]), None)
    if chosen is None:
        return ""
    for d in chosen["designs"]:
        was = told.get(d["id"])
        if not isinstance(was, dict) or d["status"] == "fulfilled":
            continue
        title = _mid(d["title"])
        if d["status"] == "lapsed" and was.get("status") != "lapsed":
            return (f"{title} no longer holds — {d['progress']}; its reward waits "
                    f"until it holds again")
        held, was_held = int(d["held"]), int(was.get("held", 0))
        if held != was_held:
            moved = "up" if held > was_held else "down"
            return (f"{title} stands at {d['progress']} — {moved} from {was_held}"
                    f" (Road {chosen['numeral']}, {chosen['title']})")
        need, hold = int(d["hold_needed"]), int(d["hold"])
        if need > 1 and d["met"] and hold == need - 1 and int(was.get("hold", 0)) != hold:
            return (f"{title} has held {hold} of {need} end turns — one more and it is "
                    f"fulfilled (Road {chosen['numeral']}, {chosen['title']})")
    return ""


_STATE_WORDS = {"alliance": "an ally, not a satellite", "defensive_alliance": "an ally, not a satellite",
                "peace": "at peace with us", "war": "at war with us", "armistice": "under a truce with us",
                "open_borders": "our friend, not a satellite", "non_aggression": "at peace with us"}


def _mid(title: str) -> str:
    """A title mid-sentence: "the Confederation of the Rhine"."""
    return ("the " + title[4:]) if title.startswith("The ") else title


def court_line(world, court: str) -> str:
    """Talleyrand's reading of a court on the Emperor's road (the record
    §6.6; ruling K: a reading, not a lookup) — where the court stands on the
    proclaimed road (or, before a proclamation, which roads name her), read
    off her live state: her row on a construction, her terms on a seal. ''
    when the court stands on no road, or no designs are authored."""
    if not armed(world) or not court or court == owner(world):
        return ""
    from backend.display_names import humanize_entity_name as _h
    chosen = proclaimed_road(world)
    who = _h(court)
    rows = []
    for r in roads(world):
        rid = str(r.get("id"))
        if road_state(world, rid) == ROAD_STATE_FORSWORN:
            continue
        for d in designs_of(r):
            courts = [str(c) for c in (d.get("courts") or [])]
            provinces = [str(p) for p in (d.get("provinces") or [])]
            holders = {str(getattr((getattr(world, "regions", {}) or {}).get(p), "controller", "") or "")
                       for p in provinces}
            if d.get("type") in (TYPE_SHUT_PORTS, TYPE_BRITAIN_SIGNS):
                from backend.game_logic import naval
                holders.add(str(naval.trade_dominance_nation(world) or ""))
            if court not in courts and court not in holders:
                continue
            rows.append((r, d))
    if not rows:
        return ""
    if not chosen:
        named = "; ".join(f"{r.get('title')} ({d.get('title')})" for r, d in rows)
        return (f"Talleyrand: \"{who} stands on the Emperor's roads, Sire — {named}. "
                f"Proclaim one in the Cabinet ({DESIGNS_CONTROL}).\"")
    r, d = rows[0]
    reading = design_reading(world, d)
    dtype = reading.get("type")
    design_t = _mid(str(d.get("title") or ""))
    if dtype == TYPE_CLIENTS:
        row = next((x for x in (reading.get("rows") or []) if x.get("court") == court), {})
        if row.get("member"):
            state = "she stands under the Emperor's protection"
        elif row.get("gone"):
            state = str(row.get("why") or "gone")
        elif str(row.get("why") or "").startswith("loyalty"):
            state = f"France's satellite, but at {row.get('why')} — Invest in Vassal raises it"
        else:
            state = (f"not yet ours — {_STATE_WORDS.get(str(row.get('why') or ''), 'outside the Empire')}; "
                     f"Propose Vassal (or Subjugate at war) on her page")
        return (f"Talleyrand: \"{who} is one of {design_t}'s courts, Sire: {state}. "
                f"{progress_line(world, reading)[0].upper()}{progress_line(world, reading)[1:]}.\"")
    if dtype in (TYPE_BROUGHT_TO_TERMS, TYPE_TITLED_AND_TERMS):
        met, manner = terms_met(world, owner(world), court)
        if met:
            return (f"Talleyrand: \"{who} is brought to terms ({manner}), Sire — "
                    f"{design_t} reads her peace as its own.\"")
        rec = (_state(world).get("terms") or {}).get(court) or {}
        if rec.get("manner") == MANNER_MODERATE and not rec.get("broken"):
            return (f"Talleyrand: \"{who} signed the moderate peace, Sire; her alliance "
                    f"within {VOLTE_FACE_WINDOW} turns of it brings her to terms.\"")
        return (f"Talleyrand: \"{who} is a crown the road of {_mid(str(r.get('title') or ''))} "
                f"must bring to terms, Sire: "
                f"two of her own provinces or her capital ceded to the Empire (a "
                f"partition), her vassalage, or a compensated peace and then her "
                f"alliance.\"")
    return (f"Talleyrand: \"{who} stands on the road of {_mid(str(r.get('title') or ''))}, "
            f"Sire — {design_t}: {progress_line(world, reading)}.\"")


def door_line(world) -> str:
    """The first morning's door to the road page (the TODAY block) — '' when
    unarmed or a road is proclaimed. Names the control, never a typed line."""
    payload = build_designs_payload(world)
    if payload is None or payload["road"]:
        return ""
    titles = ", ".join(f"{r['numeral']} {r['title']}" for r in payload["roads"])
    return (f"The Emperor's Designs — {titles}: one proclamation decides what the "
            f"Empire is for, and it cannot be undone. In the Cabinet: {DESIGNS_CONTROL}.")


def goal_clause(world) -> str:
    """The desk's goal answer's head (the record §6.6): condition (c), the
    door, then the proclaimed road's two designs — or the three roads and
    that the choice cannot be undone. '' when unarmed (every answer on the
    bare flag world and the tutorial stays byte-unchanged)."""
    payload = build_designs_payload(world)
    if payload is None:
        return ""
    chosen = next((r for r in payload["roads"] if r["proclaimed"]), None)
    if chosen is None:
        roads_named = "; ".join(f"{r['numeral']} {r['title']} ({r['proclamation']})"
                                for r in payload["roads"])
        road_part = (f"No road is proclaimed yet: {roads_named}. One proclamation, "
                     f"in the Cabinet ({DESIGNS_CONTROL}), and it cannot be undone.")
    else:
        designs = "; ".join(f"{d['title']} — {d['progress']}"
                            + (f" ({d['hold_line']})" if d["hold_line"] else "")
                            for d in chosen["designs"])
        road_part = (f"Road {chosen['numeral']}, {chosen['title']}, is proclaimed: "
                     f"{designs}. The road page: {DESIGNS_CONTROL}.")
    decisive = (decisive_made_line(world)           # VP1-X20: once made, in the past tense
                or ("Both of a road's designs latched, its construction holding and the "
                    "sealing court at peace: THE DECISIVE PEACE, a waypoint on the road to "
                    "the Congress."))
    return f"{CONDITION_C} {road_part} {decisive} "


def designs_answer(world) -> str:
    """The `designs` help kind: each design ✓ / ✗, read off the payload."""
    payload = build_designs_payload(world)
    if payload is None:
        return ("There are no designs of the Empire authored in this campaign, Sire. "
                "Nothing has been relayed.")
    lines = [payload["headline"]]
    for r in payload["roads"]:
        state = ("proclaimed" if r["proclaimed"] else "forsworn" if r["forsworn"]
                 else "open" if r["available"] else (r["disabled_reason"] or "shut"))
        lines.append(f"Road {r['numeral']}, {r['title']} ({state}):")
        for d in r["designs"]:
            mark = "✓" if d["status"] in ("fulfilled", "met") else "✗"
            lines.append(f"  {mark} {d['title']} — {d['progress']}"
                         + (f" ({d['hold_line']})" if d["hold_line"] else ""))
    lines.append(f"The road page: {DESIGNS_CONTROL}. Nothing has been relayed.")
    return "\n".join(lines)
