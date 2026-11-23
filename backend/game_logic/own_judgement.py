"""Row IC, Session 4b (IC4-D3) — HIS OWN JUDGEMENT: the decision tree of a
marshal on his own.

The user's ruling (November 22, 2026), verbatim: "orders shlould beguiding ai
that has its own actions and does its own thing you get it" — and his
correction opening Session 4b (November 23): "thats not true either its just
these are autonomous armies napoleons orders guiode them, they still work under
ai with goals set that impact their decision tree!!"

At the start of each turn (his "He moves at turn start") a man on his own
weighs EVERY act open to him and does the one that weighs most:

* GOAL   — your task's own step: your aim itself when it is in his hands (100),
           a step on the road to it (60), back to the ground you told him to
           hold (70);
* CHANCE — an enemy France sees within his reach that he beats at his own odds,
           anywhere around him; an enemy province within a march that France
           sees whole. A chance weighs more on our soil or when it threatens a
           friend, and less for every march it takes him off your road or the
           ground you named — never more than one;
* SEEK   — find the enemy (or your war goal): only with no task, or when your
           aim gives him nothing to do and is not a hold;
* WAIT   — scout, probe, dig in, fall back to better ground, keep his post or
           rest — each a real choice, said with the reason he chose it.

Your orders are GOALS that weigh in this choice: they never fence it and never
force it. His NATURE decides how he weighs — a bold man takes chances readily
at his own odds; a careful man only at good odds, or to strike what threatens
a friend or our soil, and he values good ground.

PURE: no write, no die, France's own sight. Every weight lives in ONE table
(`WEIGHTS`); the reading carries a short list of what he weighed (`weighed`)
for the measure and for "why?".
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from backend.errors import report

# ═══════════════════════════ the one table ══════════════════════════════════
# Placeholders settled by the rules written before the data (the spec's §13:
# R-INITIATIVE, R-ACTS, R-BAND) — integers, so a reading is reproducible.
WEIGHTS: Dict[str, Any] = {
    "goal_aim": 100,          # your aim itself is in his hands this turn
    "goal_march": 60,         # a step on the road to your aim
    "goal_return": 70,        # back to the ground you told him to hold
    "join": 70,               # a higher man has the enemy of your aim: he stands by him
    "guns": 65,               # Lannes's own line: up beside a friend facing an enemy
    "chance": {"bold": 58, "careful": 30},   # round 2: bold 55 → 58 ("takes chances readily at his own odds")
    "margin_per": 3,          # per tenth of the odds above his own figure ...
    "margin_cap": 27,         # ... up to this much (round 2: 30 → 27 — your aim in reach still weighs most)
    "our_soil": 15,           # the enemy stands on our soil (or a client's)
    "covers": {"bold": 10, "careful": 20},   # the enemy threatens a friend beside it
    "resolve": 25,            # Iron Resolve full: Davout strikes (his ability)
    "beat_off": 20,           # a careful man counter-attacks a force he has just beaten off
    "take": {"bold": 35, "careful": 25},     # an enemy province within a march
    "off_road": 12,           # per march a chance takes him off your road
    "off_held": 12,           # ... or off the ground you told him to hold — the plan's ONE price
                              # ("off your road, or off the ground you told him to hold"; "he strikes
                              # what comes within reach of it"): the build had doubled it (24), a
                              # reading of mine; put back after round 2 broke the band (for your word)
    "risk_step": 10,          # "boldly" / "carefully": chances weigh this much more / less
    "seek_enemy": {"bold": 50, "careful": 35},
    "seek_goal": {"bold": 45, "careful": 40},
    "seek_place": {"bold": 40, "careful": 30},
    "dig_in": {"bold": 10, "careful": 35},
    "probe": {"bold": 30, "careful": 25},
    "look": {"bold": 30, "careful": 25},
    "look_first": 2,          # the province nearer a seen enemy is looked into first
    "look_horse": 5,          # a horseman's way of waiting
    "fall_back": 45,          # a careful man, outmatched, to better ground in his area
    "stay": 5,
    "rest": 10,               # a corps at half strength or less rests (round 1: 30 → 10 — rest
                              # restores no men; a weak corps rested turn after turn, off your aim)
    "post": 15,               # keeping the ground you told him to hold
    "again": 8,               # a march on toward last turn's mark: he finishes what he started
    "turn_back": 20,          # a move that only retraces his last step weighs this much less
}
KINDS = ("goal", "join", "chance", "seek", "wait")
AIM_ACTS = frozenset({"attack", "strike", "storm", "besiege", "take"})
MOVE_ACTS = frozenset({"march", "probe", "fall_back", "move_up", "take", "join"})
SEEK_RANGE = 4               # marches he will go to find the enemy
MOST_OFF = 1                 # a chance never takes him more than one march off your road
WEIGHED_SHOWN = 5


def _O():
    from backend.game_logic import own_order
    return own_order


def _opt(kind: str, reading: Dict[str, Any], weight: int, why: str) -> Dict[str, Any]:
    return {"kind": kind, "reading": reading, "weight": int(weight), "why": why,
            "act": str(reading.get("act") or ""), "place": str(reading.get("place") or ""),
            "target": str(reading.get("target") or "")}


def _rank(o: Dict[str, Any]) -> Tuple:
    return (-int(o["weight"]), KINDS.index(o["kind"]), o["act"], o["place"], o["target"])


def _moves_to(reading: Dict[str, Any]) -> str:
    moves = [str(step.get("target") or "") for step in (reading.get("do") or [])
             if (step or {}).get("action") == "move" and step.get("target")]
    return moves[-1] if moves else ""


# ═══════════════════════════ what he stands on ══════════════════════════════

def _capitals(world) -> set:
    try:
        return {str(v) for v in (getattr(world, "nation_capitals", None) or {}).values() if v}
    except Exception as exc:
        report(exc, "own_judgement._capitals")
        return set()


def _war_goal_place(world) -> str:
    """Where your war goal stands, if you named one France can find: the
    place, or the army's province while France sees him. ("" when none.)"""
    try:
        from backend.game_logic import war_goals as _wg
        if not _wg.a_war_has_a_goal():
            return ""
        nation = str(getattr(world, "player_nation", "") or "")
        seen = {e.name: e for e in (world.get_visible_enemies(nation) or [])}
        for court in sorted(_wg.store(world)):
            goal = _wg.store(world).get(court) or {}
            if _wg.status(world, court, goal) != "open":
                continue
            target = str(goal.get("target") or "")
            if str(goal.get("kind")) == "army":
                man = seen.get(target)
                if man is not None and getattr(man, "location", None):
                    return str(man.location)
                continue
            if world.get_region(target) is not None:
                return target
    except Exception as exc:
        report(exc, "own_judgement._war_goal_place")
    return ""


def _goal_place(world, marshal, spec: Dict[str, Any]) -> str:
    task = str(spec.get("task") or "")
    target = str(spec.get("target") or "")
    if task == "take":
        return target
    if task == "hold":
        area = [p for p in (spec.get("area") or [target]) if p]
        return area[0] if area else ""
    if task == "pursue":
        quarry = world.get_marshal(target) if target else None
        nation = str(getattr(marshal, "nation", "") or "")
        if quarry is not None and quarry in (world.get_visible_enemies(nation) or []):
            return str(quarry.location or "")
        return str(spec.get("last_seen") or "")
    if task == "support":
        friend = world.get_marshal(target) if target else None
        return str(getattr(friend, "location", "") or "") if friend is not None else ""
    return ""


def _soil(world, place: str, marshal) -> str:
    """"our soil" / "<client>'s soil" when the province is ours or a client's."""
    region = world.get_region(place)
    holder = str(getattr(region, "controller", "") or "") if region is not None else ""
    if not holder:
        return ""
    if holder == str(getattr(marshal, "nation", "") or ""):
        return "our soil"
    try:
        row = (getattr(world, "vassals", None) or {}).get(holder)
        if isinstance(row, dict) and str(row.get("lord") or "") == marshal.nation:
            return f"{_O()._court_name(holder)}'s soil"
    except Exception as exc:
        report(exc, "own_judgement._soil")
    return ""


def _friends(world, marshal) -> List[Any]:
    O = _O()
    out = []
    for other in world.get_player_marshals():
        if other.name == marshal.name or int(getattr(other, "strength", 0) or 0) <= 0:
            continue
        if getattr(other, "captured_by", "") or O._hates(marshal, other.name):
            continue
        out.append(other)
    return out


def _threatened(world, place: str, friends: List[Any], here: str) -> str:
    """The friend (weakest first) the enemy at `place` stands next to."""
    O = _O()
    near = set(O._near(world, place)) | {place}
    rows = sorted((int(getattr(f, "strength", 0) or 0), f.name) for f in friends
                  if str(getattr(f, "location", "") or "") in near
                  and str(getattr(f, "location", "") or "") != here)
    return rows[0][1] if rows else ""


def _nearest_enemy_ground(world, marshal, capitals: set) -> str:
    """The nearest province France sees that a court at war with us holds —
    a bounded walk over the map's own neighbours (golden rule 8), never a
    capital, never further than SEEK_RANGE."""
    O = _O()
    nation = str(getattr(marshal, "nation", "") or "")
    start = str(marshal.location or "")
    seen = {start}
    layer = [start]
    for _depth in range(SEEK_RANGE):
        nxt = []
        for place in layer:
            for beside in O._near(world, place):
                if beside not in seen:
                    seen.add(beside)
                    nxt.append(beside)
        for place in sorted(nxt):
            if place in capitals or not O._visible(world, place):
                continue
            region = world.get_region(place)
            holder = str(getattr(region, "controller", "") or "") if region is not None else ""
            if holder and holder != nation and world.is_at_war(nation, holder):
                return place
        layer = nxt
    return ""


def _context(world, marshal, spec: Dict[str, Any], rec: Dict[str, Any]) -> Dict[str, Any]:
    O = _O()
    here = str(marshal.location or "")
    task = str(spec.get("task") or "")
    area = [p for p in (spec.get("area") or []) if p] if task == "hold" else []
    anchor = None
    off_cost = 0
    aim = ""
    if task in ("take", "pursue", "support", "hold"):
        dest = _goal_place(world, marshal, spec)
        road: List[str] = []
        if task != "hold" and dest and dest != here:
            road = list(O._road(world, marshal, dest, avoid_foes=(task == "support")) or [])[:4]
        anchor = {here} | set(road) | set(area)
        off_cost = WEIGHTS["off_held"] if task == "hold" else WEIGHTS["off_road"]
        aim = dest or str(spec.get("target") or "")
    turn = O._turn(world)
    acts = [a for a in (rec.get("acts") or []) if isinstance(a, (list, tuple)) and len(a) >= 3]
    last = acts[-1] if acts else None
    came_from = ""
    last_mark = ""
    if last is not None and int(last[2] or 0) == turn - 1:
        if len(last) >= 4 and str(last[0]) in MOVE_ACTS:
            came_from = str(last[3] or "")
        if len(last) >= 5:
            last_mark = str(last[4] or "")
    strength = int(getattr(marshal, "strength", 0) or 0)
    start = int(getattr(marshal, "starting_strength", 0) or 0)
    return {"here": here, "task": task, "area": area, "anchor": anchor, "off_cost": off_cost,
            "aim": aim, "came_from": came_from, "last_mark": last_mark, "turn": turn,
            "on_post": bool(area) and here in area,
            "keeping": (bool(area) and here in area) or _by_his_friend(world, marshal, spec),
            "weak": bool(start) and strength * 2 <= start,
            "named": {p for p in (aim, str(spec.get("target") or ""), _war_goal_place(world)) if p},
            "too_strong": ""}


def _by_his_friend(world, marshal, spec: Dict[str, Any]) -> bool:
    """A support task met: the friend he supports stands within a march. That
    aim still gives him something to do — keep by him — so he keeps by him as
    a man keeps his post (the plan: he seeks the enemy only "when your aim
    gives him nothing to do"; Session 4b's measure: a man beside the friend he
    supported walked off to find the enemy, and back)."""
    if str(spec.get("task") or "") != "support":
        return False
    friend = world.get_marshal(str(spec.get("target") or ""))
    if friend is None or int(getattr(friend, "strength", 0) or 0) <= 0 or getattr(friend, "captured_by", ""):
        return False
    d = _O()._distance(world, str(marshal.location or ""), str(friend.location or ""))
    return d is not None and d <= 1


def _off(world, ctx: Dict[str, Any], place: str) -> int:
    """Marches from `place` to your road or the ground you named (0 with no task)."""
    anchor = ctx.get("anchor")
    if not anchor or place in anchor:
        return 0
    O = _O()
    best = None
    for spot in anchor:
        d = O._distance(world, place, spot)
        if d is not None and (best is None or d < best):
            best = d
    return int(best if best is not None else 9)


def _tail(ctx: Dict[str, Any], place: str, off: int, bits: List[str]) -> str:
    O = _O()
    parts: List[str] = []
    task = ctx["task"]
    if task == "hold":
        parts.append("next to the ground he holds" if off else "on the ground he holds")
    elif task in ("take", "pursue", "support") and ctx.get("aim"):
        parts.append(f"beside his road to {O._shown(ctx['aim'])}" if off else
                     f"on his road to {O._shown(ctx['aim'])}")
    parts += bits
    return ("; " + ", ".join(parts)) if parts else ""


# ═══════════════════════════ the options ════════════════════════════════════

def _goal_option(world, marshal, spec, goal: Dict[str, Any], ctx) -> Dict[str, Any]:
    act = str(goal.get("act") or "")
    if act in AIM_ACTS:
        return _opt("goal", goal, WEIGHTS["goal_aim"], "your aim is in his hands")
    if ctx["task"] == "hold" and ctx["area"] and ctx["here"] not in ctx["area"]:
        return _opt("goal", goal, WEIGHTS["goal_return"], "back to the ground you told him to hold")
    weight = WEIGHTS["goal_march"]
    if ctx["last_mark"] and ctx["last_mark"] == str(goal.get("target") or ""):
        weight += WEIGHTS["again"]
    return _opt("goal", goal, weight, "on the road to your aim")


def _chances(world, marshal, spec, need, rec, taken, ctx, nature, goal) -> List[Dict[str, Any]]:
    O = _O()
    from backend.commands import if_thens as _it
    out: List[Dict[str, Any]] = []
    here = ctx["here"]
    goal_keys = ({str(goal.get("target") or ""), str(goal.get("place") or "")} - {""}
                 if goal is not None and str(goal.get("act") or "") in AIM_ACTS else set())
    risk = max(-1, min(1, int(spec.get("risk", 0) or 0)))
    capitals = _capitals(world)
    friends = _friends(world, marshal)
    resolve_full = nature == "careful" and O._has_resolve(marshal) and int(
        getattr(marshal, "iron_resolve_stacks", 0) or 0) >= 3
    beat_off = nature == "careful" and rec.get("last") == "won" and bool(rec.get("held"))
    struck = set()
    for place in _it.reach(world, marshal):
        if not O._foes_at(world, marshal, place):
            continue
        if place in capitals and place != here and place not in ctx["named"]:
            continue        # a war-ending place: only as your named aim
        off = _off(world, ctx, place)
        if off > MOST_OFF:
            continue
        hit, why = O._attack_choice(world, marshal, place, need, taken, verb="strikes")
        if hit is None:
            if why and not why.startswith("taken:") and not ctx["too_strong"]:
                ctx["too_strong"] = why
            continue
        if str(hit.get("target") or "") in goal_keys or place in goal_keys:
            continue        # it IS your aim's own step
        foe = world.get_marshal(str(hit.get("target") or ""))
        odds = O.odds_against(world, marshal, foe) if foe is not None else None
        if foe is None or odds is None:
            continue
        margin = max(0.0, float(odds["ratio"]) * 10.0 - float(need["needed"]))
        weight = WEIGHTS["chance"][nature] + min(WEIGHTS["margin_cap"], int(margin * WEIGHTS["margin_per"]))
        bits: List[str] = []
        soil = _soil(world, place, marshal)
        if soil:
            weight += WEIGHTS["our_soil"]
            bits.append(f"on {soil}")
        friend = _threatened(world, place, friends, here)
        if friend:
            weight += WEIGHTS["covers"][nature]
            bits.append(f"a threat to {O._shown(friend)}")
        if resolve_full:
            weight += WEIGHTS["resolve"]
            bits.append("Iron Resolve is full")
        elif beat_off:
            weight += WEIGHTS["beat_off"]
            bits.append("he beat them off last time")
        weight -= off * ctx["off_cost"]
        weight += risk * WEIGHTS["risk_step"]
        hit = dict(hit)
        hit["act"] = "strike"
        hit["chance"] = True
        hit["off"] = int(off)
        hit["line"] = O.attack_line(marshal, "strikes", foe, place, odds, need,
                                    hit.get("with") or "", bool(hit.get("may_day")),
                                    _tail(ctx, place, off, bits))
        out.append(_opt("chance", hit, weight, "a chance beside him"))
        struck.add(place)
    # an enemy province he stands on, or one within a march that France sees whole
    for place in [here] + O._near(world, here):
        if place in struck or place in goal_keys:
            continue
        if place in capitals and place not in ctx["named"]:
            continue
        if place != here and not O._full(world, place):
            continue        # never into the unseen for a chance
        off = _off(world, ctx, place)
        if off > MOST_OFF:
            continue
        reading, _why = O._take_place(world, marshal, place, need, taken)
        if reading is None or str(reading.get("act") or "") == "attack":
            continue
        weight = WEIGHTS["take"][nature] - off * ctx["off_cost"] + risk * WEIGHTS["risk_step"]
        if " frees " in str(reading.get("line") or ""):
            weight += WEIGHTS["our_soil"]        # an ally's ground freed
        reading = dict(reading)
        reading["chance"] = True
        reading["off"] = int(off)
        reading["line"] = str(reading.get("line") or "") + _tail(ctx, place, off, [])
        out.append(_opt("chance", reading, weight, "an enemy province within a march"))
    return out


def _seek(world, marshal, spec, need, taken, ctx, nature) -> List[Dict[str, Any]]:
    """Find the enemy: the nearest corps France sees that he beats at his own
    odds, else your war goal, else the nearest province a court at war with us
    holds — one march on the road there."""
    O = _O()
    here = ctx["here"]
    capitals = _capitals(world)
    nation = str(getattr(marshal, "nation", "") or "")
    careful = nature == "careful"
    best = None
    for enemy in world.get_visible_enemies(nation) or []:
        if int(getattr(enemy, "strength", 0) or 0) <= 0 or getattr(enemy, "captured_by", ""):
            continue
        if not world.is_at_war(nation, enemy.nation):
            continue
        where = str(getattr(enemy, "location", "") or "")
        d = O._distance(world, here, where)
        if d is None or d < 2 or d > SEEK_RANGE:
            continue        # within a march he is a chance, not a search
        if where in capitals and where not in ctx["named"]:
            continue
        odds = O.odds_against(world, marshal, enemy)
        if odds is None or float(odds["ratio"]) * 10.0 + 1e-9 < float(need["needed"]):
            continue
        row = (d, -O._known(world, enemy), enemy.name)
        if best is None or row < best[0]:
            best = (row, enemy, where)
    if best is not None:
        _row, enemy, where = best
        reading, _why = O._march_toward(world, marshal, where, need, taken,
                                        purpose=f"to find {O._shown(enemy.name)}", stop_short=1,
                                        avoid_foes=careful)
        if reading is not None:
            weight = WEIGHTS["seek_enemy"][nature]
            if ctx["last_mark"] == enemy.name:
                weight += WEIGHTS["again"]
            reading["target"] = enemy.name
            return [_opt("seek", reading, weight, f"he goes to find {O._shown(enemy.name)}")]
    goal_place = _war_goal_place(world)
    if goal_place and goal_place != here:
        reading, _why = O._march_toward(world, marshal, goal_place, need, taken,
                                        purpose=f"toward your war goal, {O._shown(goal_place)}",
                                        avoid_foes=careful)
        if reading is not None:
            weight = WEIGHTS["seek_goal"][nature]
            if ctx["last_mark"] == goal_place:
                weight += WEIGHTS["again"]
            reading["target"] = goal_place
            return [_opt("seek", reading, weight, "your war goal")]
    place = _nearest_enemy_ground(world, marshal, capitals)
    if place:
        reading, _why = O._march_toward(world, marshal, place, need, taken,
                                        purpose=f"toward {O._shown(place)}, which the enemy holds",
                                        avoid_foes=careful)
        if reading is not None:
            weight = WEIGHTS["seek_place"][nature]
            if ctx["last_mark"] == place:
                weight += WEIGHTS["again"]
            reading["target"] = place
            return [_opt("seek", reading, weight, "the nearest ground the enemy holds")]
    return []


def _stay(world, marshal, spec, ctx, nature, reason_blocked: str) -> Dict[str, Any]:
    """Holding where he stands, said with the reason his judgement chose it —
    never "nothing to do"."""
    O = _O()
    shown = O._shown(marshal.name)
    here = ctx["here"]
    if getattr(marshal, "fortified", False):
        words = f"{shown} keeps to his works at {O._shown(here)}"
        if O._has_resolve(marshal):
            words += f" — Iron Resolve {int(getattr(marshal, 'iron_resolve_stacks', 0) or 0)} of 3"
    elif ctx.get("keeping") and ctx["task"] == "support":
        words = f"{shown} stays by {O._shown(str(spec.get('target') or ''))}"
    elif ctx["on_post"]:
        words = f"{shown} keeps {O._shown(here)}"
    else:
        words = f"{shown} stays at {O._shown(here)}"
    if ctx.get("keeping") and ctx["task"] == "support":
        reason = "as you asked — nothing within reach is worth leaving him for"
    elif ctx["on_post"]:
        reason = "as you asked — nothing within reach is worth leaving it for"
    elif ctx["weak"]:
        reason = "his corps is at half strength or less, and he rests it"
    elif reason_blocked:
        reason = reason_blocked
    elif ctx["too_strong"]:
        reason = ctx["too_strong"]
    elif O._at_war(world):
        reason = "nothing within his reach that he can beat at his own odds"
    else:
        reason = "the country is at peace"
    out = O._reading(marshal, "stay", f"{words} — {reason}", place=here, why=reason)
    return out


def _waits(world, marshal, spec, need, rec, taken, ctx, nature, reason_blocked: str) -> List[Dict[str, Any]]:
    O = _O()
    out: List[Dict[str, Any]] = []
    horse = bool(getattr(marshal, "cavalry", False))
    first_look = True
    for row in O._waiting_options(world, marshal, spec, need, rec, taken):
        act = str(row.get("act") or "")
        if act == "dig_in":
            weight = WEIGHTS["dig_in"][nature]
        elif act == "look":
            weight = WEIGHTS["look"][nature] + (WEIGHTS["look_horse"] if horse else 0)
            if first_look:
                weight += WEIGHTS["look_first"]
                first_look = False
        elif act == "probe":
            weight = WEIGHTS["probe"][nature]
        elif act == "fall_back":
            weight = WEIGHTS["fall_back"]
        else:
            weight = 0
        if ctx["on_post"] and act in ("dig_in", "look"):
            weight += WEIGHTS["post"]
        if reason_blocked and not str(row.get("line") or "").endswith(f"({reason_blocked})"):
            row = dict(row)
            row["line"] = f"{row['line']} ({reason_blocked})"
            row["why"] = reason_blocked
        out.append(_opt("wait", row, weight, act))
    weight = (WEIGHTS["stay"] + (WEIGHTS["post"] if ctx["on_post"] else 0)
              + (WEIGHTS["rest"] if ctx["weak"] else 0))
    out.append(_opt("wait", _stay(world, marshal, spec, ctx, nature, reason_blocked), weight, "stay"))
    return out


# ═══════════════════════════ the choice ═════════════════════════════════════

def _settle(opts: List[Dict[str, Any]], rec: Dict[str, Any], ctx: Dict[str, Any]
            ) -> Tuple[Dict[str, Any], List[Dict[str, Any]], bool]:
    """The one that weighs most — a move that only retraces his last step
    weighs less, and no act at the same place a third turn running while
    another sensible one exists (§6.7.4, now for every act he chooses)."""
    acts = [tuple(a[:2]) for a in (rec.get("acts") or []) if isinstance(a, (list, tuple)) and len(a) >= 2]
    last_two = acts[-2:]
    for o in opts:
        dest = _moves_to(o["reading"])
        if (o["kind"] != "goal" and ctx["came_from"] and dest
                and dest == ctx["came_from"]):
            o["weight"] -= WEIGHTS["turn_back"]
        # (keeping the ground you told him to hold is YOUR order, which he may
        # keep turn after turn; every other stay — resting a weak corps, staying
        # where he is — is a way of waiting like the rest: never a third turn
        # running while another sensible act exists. The play-out, Nov 23: a
        # half-strength corps rested five turns running, though rest restores
        # no men in this game.)
        if (o["kind"] in ("wait", "seek") and not (o["act"] == "stay" and ctx.get("on_post"))
                and len(last_two) == 2
                and all(x == (o["act"], o["place"]) for x in last_two)):
            o["dropped"] = True
    ranked_all = sorted(opts, key=_rank)
    live = [o for o in ranked_all if not o.get("dropped")]
    if live:
        chosen = live[0]
        changed = chosen is not ranked_all[0]
        return chosen, live, changed
    chosen = dict(ranked_all[0])
    reading = dict(chosen["reading"])
    reading["line"] = str(reading.get("line") or "") + " again — nothing has changed"
    reading["again"] = True
    reading["visible"] = False
    chosen["reading"] = reading
    return chosen, ranked_all, False


def move_is_open(world, marshal, dest: str) -> bool:
    """The executor's own answer to his move onto `dest`, read BEFORE he
    chooses it: his state (a broken corps or one locked in drill moves not; a
    corps in its works is let out by the step before the move) and the move's
    target (`MovementExecutor.move_refusal_probe`: an enemy in his own province
    lets him march only onto French soil, the crossing the enemy's fleet
    shuts, a seen enemy at the destination, the law of nations). PURE."""
    from backend.commands.movement_executor import MovementExecutor
    from backend.commands.state_probe import FORTIFIED_FIRST, order_state_refusal
    says = order_state_refusal(world, marshal, "move", free=True)   # (his own move costs no action)
    if says and says != FORTIFIED_FIRST:      # (his acts leave the works first)
        return False
    region = world.get_region(dest)
    if region is None:
        return False
    try:
        return MovementExecutor.move_refusal_probe(world, marshal, region, dest) is None
    except Exception as exc:
        report(exc, "own_judgement.move_is_open")
        return False


def _open_to_him(world, marshal, opts: List[Dict[str, Any]], here: str) -> List[Dict[str, Any]]:
    """Only the acts the game will carry out (Session 4b's measure: turns lost
    to "could not carry out his move" — a charge through a held province, an
    attack elsewhere while an enemy stands beside him, a march off a field he
    is engaged on, works begun beside an enemy). Every move is read through
    the executor's own probe (`move_is_open`); while an enemy stands in his own
    province he attacks only that enemy. Staying is always open."""
    O = _O()
    engaged = bool(O._engaged_by(world, marshal))
    out = []
    for o in opts:
        dest = _moves_to(o["reading"])
        if dest and dest != here and not move_is_open(world, marshal, dest):
            continue
        if engaged and o["act"] in AIM_ACTS and o["place"] and o["place"] != here:
            continue
        out.append(o)
    return out or opts


def judge(world, marshal, spec: Dict[str, Any], need: Dict[str, Any], rec: Dict[str, Any],
          taken: Dict[str, str], *, goal: Optional[Dict[str, Any]] = None, goal_why: str = "",
          join: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """His act this turn — PURE. `goal` / `goal_why`: your task's own step (or
    why it gives none); `join`: standing by a higher man who has the enemy of
    your aim."""
    O = _O()
    nature = O._nature(marshal)
    if nature not in ("bold", "careful"):
        nature = "careful"
    task = str(spec.get("task") or "")
    ctx = _context(world, marshal, spec, rec)
    blocked = goal_why.split(":", 1)[1] if goal_why.startswith("road_barred:") else goal_why
    if blocked.startswith("taken:"):
        blocked = ""
    opts: List[Dict[str, Any]] = []
    if goal is not None:
        opts.append(_goal_option(world, marshal, spec, goal, ctx))
    if join is not None:
        opts.append(_opt("join", join, WEIGHTS["join"], "he stands by the man who has your aim's enemy"))
    aim_in_hand = goal is not None and str(goal.get("act") or "") in AIM_ACTS
    if not aim_in_hand and task != "support":
        guns = O._lannes_to_the_guns(world, marshal, taken)
        if guns is not None:
            step = _moves_to(guns)
            off = _off(world, ctx, step) if step else 0
            opts.append(_opt("join", guns, WEIGHTS["guns"] - off * ctx["off_cost"],
                             "to the guns — a friend faces the enemy"))
    opts += _chances(world, marshal, spec, need, rec, taken, ctx, nature, goal)
    keeping = ctx["keeping"]          # on the ground you named, or beside the friend he supports
    if task == "free" or (goal is None and join is None and task != "hold" and not keeping):
        opts += _seek(world, marshal, spec, need, taken, ctx, nature)
    opts += _waits(world, marshal, spec, need, rec, taken, ctx, nature, blocked)
    opts = _open_to_him(world, marshal, opts, ctx["here"])
    chosen, ranked, changed = _settle(opts, rec, ctx)
    reading = dict(chosen["reading"])
    reading["kind"] = chosen["kind"]
    reading["weighed"] = [{"kind": o["kind"], "act": o["act"], "place": o["place"],
                           "target": o["target"], "weight": int(o["weight"]), "why": o["why"]}
                          for o in ranked[:WEIGHED_SHOWN]]
    if changed:
        reading["changed"] = True
    if goal is None and join is None:
        if goal_why.startswith("road_barred:"):
            reading["barred"] = True
            reading.setdefault("why", blocked)
        elif blocked and task in ("take", "pursue"):
            reading["stuck"] = True
            if not reading.get("why"):
                reading["why"] = blocked
    reading["help"] = O._friend_line(world, marshal)
    return reading
