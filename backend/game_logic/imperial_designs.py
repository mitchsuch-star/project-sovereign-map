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
False / 0 and nothing is shown (the bare flag world, the tutorial, and — until
S14b part 2 — the shipped 1805 boot). Every predicate is nation-parameterized
on the block's authored `owner`; the roads are player CONTENT (an asymmetry of
content, as the minors have no laws), never of code.

The seams the series attribution holds down (`tools/_vp1_series_arms.py`):
`note_ratification` (the terms latch), `drift_suspended` (the Rhine's shield),
`order_decay` (the Continent's order) and `decisive_peace_released` (the
stamp, held off until part 3).
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
    if proclaimed_road(world) != road_id:
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

def decisive_peace_released() -> bool:
    """The stamp's seam: False until S14b part 3 lands the register, the
    client and the arms (the record §9) — the rule is computed and pinned
    from part 1, nothing is stamped."""
    return False


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

def build_designs_payload(world) -> Optional[Dict[str, Any]]:
    """The ONE payload every surface reads (the record §6) — ints only, None
    on an unarmed world."""
    if not armed(world):
        return None
    state = _state(world)
    chosen = state.get("road") or ""
    out_roads = []
    for r in roads(world):
        rid = str(r.get("id"))
        designs = []
        for d in designs_of(r):
            did = str(d.get("id"))
            reading = design_reading(world, d)
            designs.append({
                "id": did, "title": str(d.get("title") or did),
                "role": str(d.get("role") or ""),
                "held": int(reading["held"]), "required": int(reading["required"]),
                "progress": progress_line(world, reading),
                "met": bool(reading["met"]),
                "hold": int(state["hold"].get(did, 0)), "hold_needed": int(_hold_needed(d)),
                "fulfilled_turn": int(state["fulfilled"].get(did, -1)),
                "lapsed": did in state["fulfilled"] and not reading["met"],
            })
        out_roads.append({
            "id": rid, "title": str(r.get("title") or rid),
            "proclamation": str(r.get("proclamation") or ""),
            "gate_met": bool(gate_met(world, r)),
            "proclaimed": rid == chosen,
            "forsworn": bool(chosen) and rid != chosen,
            "refusal": proclaim_refusal(world, rid) or "",
            "designs": designs,
        })
    payload = {"owner": owner(world), "road": chosen,
               "proclaimed_turn": int(state.get("proclaimed_turn", -1)),
               "roads": out_roads}
    return payload
