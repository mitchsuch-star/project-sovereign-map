"""Row IC, Session 4 — IC-15: WHAT FRANCE HAS LEARNED of the enemy's plans.

`docs/INDEPENDENT_COMMAND_SPEC.md` §10.2 ("what you can learn"), §10.3 (what
the enemy learns of you), §12 ("The enemy"), §13 (captured orders stay good
until the next step, two turns at most); the rules `SYSTEMS_REFERENCE.md` §235.

Position and strength are the fog's business. A marshal's NATURE is public
(`display_names.NATURE_WORDS`). What a court has WRITTEN for its
letter-following marshals, and the province its corps favour, are learned —
two ways, and no other:

  * THE SPY — the mission the player already has ("Gather Intel"), when it
    completes: each letter-following marshal's orders of that court, wherever
    he stands, and its favoured province (`from_spy`);
  * CAPTURED ORDERS — when a French corps routs a corps of a court it is at
    war with: the orders of the letter-following marshal nearest the routed
    corps; where the court has none, its favoured province (`a_rout`). A
    court whose orders are taken moves to its next step within two turns
    (`war_plans.compromise`).

ONE MODULE, ONE STORE: `world.learned = {"marshals": {name: {...}}, "courts":
{court: {...}}}` — the WORDS as they stood when they were learned, and the
turn. It is kept apart from the enemy's live state: nothing here is read back
from a plan after the fact, so knowledge AGES BY TIME ONLY ("learned 4 turns
ago") and the player is never told that orders changed. Nothing is shown that
was not learned; no court ever plants a false order (the words are copied from
the orders that stand).

The store is written by the spy's completion (as a turn ends) and by a
battle's own rout (a battle is never taken back) — never by an order. It is
saved only while it holds something. The other half of the same battle hook is
§10.3: a French marshal ON HIS OWN who is routed gives his task away
(`war_plans.learns_of`).
"""
from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional

from backend.errors import report

SPY = "spy"
CAPTURED = "captured"


# ═══════════════════════════ the store ═══════════════════════════════════════

def from_block(raw: Any) -> Dict[str, Any]:
    """`world.learned` from a save's key ({} for an old save, or nothing learned)."""
    if not isinstance(raw, dict):
        return {}
    out: Dict[str, Any] = {}
    for part in ("marshals", "courts"):
        rows = raw.get(part)
        if isinstance(rows, dict) and rows:
            out[part] = {str(k): copy.deepcopy(v) for k, v in rows.items() if isinstance(v, dict)}
    return out


def _store(world) -> Dict[str, Any]:
    held = getattr(world, "learned", None)
    if not isinstance(held, dict):
        held = {}
        world.learned = held
    return held


def _turn(world) -> int:
    return int(getattr(world, "current_turn", 0) or 0)


def _player(world) -> str:
    return str(getattr(world, "player_nation", "") or "")


def of_marshal(world, name: str) -> Optional[Dict[str, Any]]:
    """What France has learned of this marshal's orders, or None. PURE."""
    row = ((getattr(world, "learned", None) or {}).get("marshals") or {}).get(str(name))
    return row if isinstance(row, dict) else None


def of_court(world, court: str) -> Optional[Dict[str, Any]]:
    """What France has learned of the province this court's corps favour, or None. PURE."""
    row = ((getattr(world, "learned", None) or {}).get("courts") or {}).get(str(court))
    return row if isinstance(row, dict) else None


# ═══════════════════════════ learning ════════════════════════════════════════

def _planned_men(world, court: str) -> List[Any]:
    from backend.game_logic import war_plans as _plans
    return [m for m in world.get_marshals_by_nation(court)
            if int(getattr(m, "strength", 0) or 0) > 0 and _plans.planned(world, m)]


def _note_marshal(world, man, how: str, where: str = "") -> Dict[str, Any]:
    from backend.game_logic import war_plans as _plans
    row = {"court": str(man.nation), "orders": list(_plans.orders_in_words(world, man)),
           "turn": _turn(world), "how": how, **({"where": where} if where else {})}
    _store(world).setdefault("marshals", {})[str(man.name)] = row
    return row


def _note_court(world, court: str, how: str) -> Optional[Dict[str, Any]]:
    """The province the court's corps favour TONIGHT, as its plan stands — ""
    is knowledge too ("its corps favour no province"). None where the court
    holds no plan at all (there is nothing to learn)."""
    from backend.game_logic import war_plans as _plans
    state = _plans.state_of(world, court)
    if not state:
        return None
    # what its corps REALLY lean toward tonight (`war_plans.favoured`: a
    # priority among the court's own aims) — never the plan's written word
    # where that word pulls nobody.
    state_favour = _plans._favour_of(world, court, state.get("favour"))
    favour = ""
    if (_plans.a_plan_names_a_favoured_province() and not state.get("done")
            and court not in (state.get("torn") or ())):
        favour = str(state_favour or "")
    row = {"favour": favour, "turn": _turn(world), "how": how}
    _store(world).setdefault("courts", {})[str(court)] = row
    return row


def from_spy(world, court: str) -> Dict[str, Any]:
    """The spy's report on a court: each of its letter-following marshals'
    orders, wherever he stands, and the province its corps favour. What it
    learned — `{"marshals": [names], "favour": str | None}` — for the mission's
    own words. Nothing is forced on the court: a spy is not noticed."""
    from backend.game_logic import war_plans as _plans
    learned: Dict[str, Any] = {"marshals": [], "favour": None}
    if not _plans.the_courts_follow_a_plan() or not _plans.sets(world):
        return learned
    for man in _planned_men(world, court):
        _note_marshal(world, man, SPY)
        learned["marshals"].append(str(man.name))
    row = _note_court(world, court, SPY)
    if row is not None:
        learned["favour"] = row["favour"]
    return learned


def from_rout(world, routed, victor) -> Optional[Dict[str, Any]]:
    """CAPTURED ORDERS: a French corps routed `routed`. The orders of the
    letter-following marshal of his court NEAREST the routed corps (the routed
    man himself, if he is one); where the court has none under orders, its
    favoured province. The court's step then ends within two turns. What was
    taken — `{"court", "marshal" | None, "orders", "favour" | None}` — or None
    when the court had nothing written to take."""
    from backend.game_logic import war_plans as _plans
    court = str(getattr(routed, "nation", "") or "")
    if not court or not _plans.the_courts_follow_a_plan() or not _plans.sets(world):
        return None
    if _plans.state_of(world, court) is None:
        return None
    here = str(getattr(routed, "location", "") or "")
    men = _planned_men(world, court)
    taken: Dict[str, Any] = {"court": court, "marshal": None, "orders": [], "favour": None,
                             "where": here}
    if men:
        def far(man) -> tuple:
            distance = world.get_distance(here, str(man.location or "")) if here else None
            return (0 if man is routed else 1, int(distance if distance is not None else 99), str(man.name))
        nearest = min(men, key=far)
        row = _note_marshal(world, nearest, CAPTURED, here)
        taken.update({"marshal": str(nearest.name), "orders": list(row["orders"])})
    else:
        row = _note_court(world, court, CAPTURED)
        if row is None:
            return None
        taken["favour"] = row["favour"]
    _plans.compromise(world, court)
    return taken


def a_rout(world, routed, victor) -> Optional[Dict[str, Any]]:
    """The battle's own hook — the head of `CombatExecutor._apply_forced_
    retreat_or_break`, the one road out of every lost field, BEFORE the routed
    man's order is wiped:

    * a corps of a court at war with France, routed by a French corps: its
      orders are taken (`from_rout`) — returned for the battle's telling;
    * a French marshal ON HIS OWN, routed by a court: it learns his task
      (§10.3, `war_plans.learns_of`).

    Never raises into a battle."""
    try:
        player = _player(world)
        if routed is None or victor is None or not player:
            return None
        if routed.nation != player and victor.nation == player:
            if world.is_at_war(player, routed.nation):
                return from_rout(world, routed, victor)
            return None
        if routed.nation == player and victor.nation != player:
            from backend.game_logic import own_order as _own
            from backend.game_logic import war_plans as _plans
            task = _own.own(routed)
            if isinstance(task, dict):
                _plans.learns_of(world, str(victor.nation), task)
        return None
    except Exception as exc:
        report(exc, "learned.a_rout")
        return None


def tidy(world) -> None:
    """As a turn ends: what was learned of a man who has left the field, or of
    a court France is no longer at war with, is put away. (Age is never a
    reason: knowledge ages by time only.) Touches nothing — not even an empty
    dict — where nothing was learned."""
    held = getattr(world, "learned", None)
    if not isinstance(held, dict) or not held:
        return
    player = _player(world)
    men = held.get("marshals") or {}
    for name in list(men):
        man = world.get_marshal(name)
        if (man is None or int(getattr(man, "strength", 0) or 0) <= 0
                or not world.is_at_war(player, str(man.nation))):
            del men[name]
    courts = held.get("courts") or {}
    for court in list(courts):
        if not world.is_at_war(player, court):
            del courts[court]
    for part in ("marshals", "courts"):
        if part in held and not held[part]:
            del held[part]


# ═══════════════════════════ telling ═════════════════════════════════════════

def age_words(world, row: Dict[str, Any]) -> str:
    """"learned this turn" / "learned last turn" / "learned 4 turns ago"."""
    age = max(0, _turn(world) - int(row.get("turn", 0) or 0))
    if age == 0:
        return "learned this turn"
    if age == 1:
        return "learned last turn"
    return f"learned {age} turns ago"


def how_words(row: Dict[str, Any]) -> str:
    if row.get("how") == CAPTURED:
        where = str(row.get("where") or "")
        return f"from orders captured at {where}" if where else "from captured orders"
    return "from your spy's report"


def favour_words(court_shown: str, row: Dict[str, Any]) -> str:
    place = str(row.get("favour") or "")
    return (f"{court_shown}'s corps lean toward {place}" if place
            else f"{court_shown}'s corps favour no province")


def spy_words(world, court: str, report_: Dict[str, Any]) -> str:
    """The spy's report in plain words, for the mission's completion — each
    marshal's orders as he carries them, then the favoured province. "" where
    the court had nothing written (the mission's own words stand alone)."""
    from backend.display_names import display_nation as _court
    parts: List[str] = []
    for name in report_.get("marshals") or ():
        row = of_marshal(world, name)
        if row and row.get("orders"):
            parts.append(" ".join(row["orders"]))
    if report_.get("favour") is not None:
        row = of_court(world, court)
        if row is not None:
            parts.append(favour_words(_court(court), row) + ".")
    if not parts:
        return ""
    return "His report on their written orders: " + " ".join(parts)


def taken_words(world, taken: Dict[str, Any]) -> str:
    """Captured orders in plain words, for the battle's telling."""
    from backend.display_names import display_nation as _court
    from backend.display_names import humanize_entity_name as _shown
    court = str(taken.get("court") or "")
    if taken.get("marshal"):
        # The court's own heading (`own_voice.COURTS` — its register, IC-13),
        # then the plain reading beside it (golden rule 11).
        from backend.game_logic import own_voice as _voice
        head = _voice.court_head(world, court, _shown(str(taken["marshal"])))
        return (f"Among the baggage: {_court(court)}'s written orders for {_shown(str(taken['marshal']))}. "
                + (f"“{head}” " if head else "")
                + " ".join(taken.get("orders") or []))
    row = of_court(world, court)
    if row is None:
        return ""
    return f"Among the baggage: {_court(court)}'s dispatches. " + favour_words(_court(court), row) + "."


def payload(world) -> Dict[str, Any]:
    """What the screens show of it — ONLY what was learned, each with its age
    and how it was learned. {} where nothing was."""
    held = getattr(world, "learned", None)
    if not isinstance(held, dict) or not held:
        return {}
    from backend.display_names import humanize_entity_name as _shown
    out: Dict[str, Any] = {}
    for name, row in (held.get("marshals") or {}).items():
        out.setdefault("marshals", {})[name] = {
            "name": _shown(name), "court": str(row.get("court") or ""),
            "orders": list(row.get("orders") or []),
            "learned": age_words(world, row), "how": how_words(row),
            "turn": int(row.get("turn", 0) or 0)}
    for court, row in (held.get("courts") or {}).items():
        out.setdefault("courts", {})[court] = {
            "favour": str(row.get("favour") or ""),
            "words": favour_words(_shown(court), row),
            "learned": age_words(world, row), "how": how_words(row),
            "turn": int(row.get("turn", 0) or 0)}
    return out
