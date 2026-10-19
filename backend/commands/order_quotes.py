"""CC-2 "March here" (row CC, Pre-Deploy S13c part 1, October 2026).

The QUOTE of a click order: what `<Marshal>, march to <Province>` — or
`support <ally>`, or an attack on a sighted enemy — would do if it were sent
now: taken or refused (in the probe's own words), its price in actions, its
clock in turns, the road, the standing order it would silently replace, and
whether the marshal may object. The province panel's March here rows and the
map's select-then-click card (CC-3) render it; nothing in the client
re-derives a rule.

Read from the SAME pure readers the order's own road walks — never a copy:

* the state: `state_probe.order_state_refusal` (the probe every other chip
  already dims by — the executor's gates in its order);
* the road: `strategic.march_road` (CRT-4's ONE issuance reader: the weighted
  road, the cautious man's avoid-set, `plot_route`'s lawful-first ladder, the
  closed frontier);
* the clock: `strategic.march_turns` (the march's own arrival law);
* the price: `Marshal.strategic_order_ap(order_type=...)` — by KEYWORD:
  positionally the first argument is `auto_upgrade`, which prices every
  order at 1;
* the objection: the pure concern evaluators of `objection_v2` (a "possible"
  is never a promise — mood and the one-popup-a-turn cap still decide).

`tests/test_cc2_march_here.py` drift-pins every field the panel prints
against what POST /command then does on a fresh board. PURE: reads the
world, writes nothing — the route is a GET that touches no popup queue.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from backend.display_names import humanize_entity_name
from backend.errors import report


def visible_foe_on_road(world, player: str, road) -> Optional[Tuple[Any, str]]:
    """The first enemy corps standing on `road` in a province we SEE
    (FULL or PARTIAL) — `(marshal, province)` — or None. The question desk's
    reach answer and the march quote read the same scan."""
    from backend.models.intel import FULL, PARTIAL
    for region in road:
        try:
            seen = world.get_region_intel(region).visibility in (FULL, PARTIAL)
        except Exception as exc:
            report(exc, "order_quotes.visible_foe_on_road: world.get_region_intel")
            seen = False
        if not seen:
            continue
        foes = [m for m in world.get_enemies_in_region(region, player)
                if getattr(m, "strength", 0) > 0]
        if foes:
            return foes[0], region
    return None


def _replaces(marshal) -> str:
    """The standing order a new one would REPLACE (the executor cancels the
    old order without a word) — said on the chip, so a click never silently
    unmakes an order the player gave."""
    order = getattr(marshal, "strategic_order", None)
    if order is None:
        return ""
    kind = str(getattr(order, "command_type", "") or "")
    target = humanize_entity_name(str(getattr(order, "target", "") or ""))
    if kind == "SUPPORT" and getattr(order, "standing_follow", False):
        return f"his march with {target}"
    return {
        "MOVE_TO": f"his march to {target}",
        "PURSUE": f"his pursuit of {target}",
        "HOLD": f"his hold at {target}",
        "SUPPORT": f"his support of {target}",
    }.get(kind, "his standing order")


def _without_spending_the_dice(fn):
    """Run an evaluator that may roll `random` (the mood variance) and put
    the generator back as it was: a quote is a GET, and a GET that advanced
    the game's random stream would change the next battle. NONE never
    promotes and a concern never drops to NONE, so the "none / possible"
    the quote reads is the same whatever the roll."""
    import random
    saved = random.getstate()
    try:
        return fn()
    finally:
        random.setstate(saved)


def _strategic_objection(world, marshal, order_type: str, target: str, road) -> str:
    """"possible" when the strategic concern evaluator reads any concern —
    the same evaluator the order's objection stage calls, with its bypasses
    (the sovereign, a recovering corps, a foreign one)."""
    if (getattr(marshal, "is_sovereign", False)
            or marshal.nation != world.player_nation
            or int(getattr(marshal, "retreat_recovery", 0) or 0) > 0):
        return "none"
    from backend.commands.objection_v2 import ConcernLevel, evaluate_strategic_situation
    try:
        concern = _without_spending_the_dice(lambda: evaluate_strategic_situation(
            marshal, order_type, target, list(road or []), {"world": world}))
    except Exception as exc:
        report(exc, "order_quotes._strategic_objection: evaluate_strategic_situation")
        return "none"
    return "none" if concern == ConcernLevel.NONE else "possible"


def _tactical_objection(world, marshal, action: str, target: str) -> str:
    if (getattr(marshal, "is_sovereign", False)
            or marshal.nation != world.player_nation):
        return "none"
    from backend.commands.objection_v2 import ConcernLevel, evaluate_situation
    try:
        concern = _without_spending_the_dice(lambda: evaluate_situation(
            marshal, action, {"action": action, "target": target, "marshal": marshal.name},
            {"world": world}))
    except Exception as exc:
        report(exc, "order_quotes._tactical_objection: evaluate_situation")
        return "none"
    return "none" if concern == ConcernLevel.NONE else "possible"


def _blank(kind: str, marshal, dest: str, command: str) -> Dict[str, Any]:
    return {
        "kind": kind,
        "marshal": marshal.name,
        "shown": humanize_entity_name(marshal.name),
        "dest": dest,
        "command": command,
        "ok": False,
        "ap": 0,
        "turns": 0,
        "road": [],
        "refusal": "",
        "replaces": "",
        "objection": "none",
        "note": "",
        "contact": "",
        "already": False,
    }


def _contact_line(q: Dict[str, Any], marshal, foe, region: str, dest: str) -> str:
    """What the march's FIRST step does on meeting a corps we can see —
    `_handle_first_step_blocked`'s arms, in its order (1 action is charged at
    once on every arm)."""
    shown = q["shown"]
    name = humanize_entity_name(foe.name)
    where = (f"{name} holds {region}" if region == dest
             else f"{name} blocks the road at {region}")
    if q["kind"] == "support" and region == dest:
        return f"{where} — {shown} halts at the approach and joins the next attack there (1 action now)."
    personality = str(getattr(marshal, "personality", "balanced") or "balanced")
    if personality == "literal":
        return f"{where} — {shown} halts at the approach and reports (1 action now)."
    if personality == "aggressive":
        return (f"{where} — {shown} attacks him at once if the numbers favour him, "
                f"else asks your orders (1 action now).")
    return f"{where} — {shown} stops there and asks your orders (1 action now)."


def _seen_enemy_regions(world, nation: str, memo: Optional[dict]) -> List[str]:
    """The provinces where we SEE an enemy corps (FULL or PARTIAL) — read
    once per quote set (the memo), never per destination (Rule 8)."""
    key = ("seen_enemy_regions", nation)
    if memo is not None and key in memo:
        return memo[key]
    from backend.commands import strategic as road_law
    seen = list(road_law.enemy_occupied_regions(world, nation, fog_aware=True) or [])
    if memo is not None:
        memo[key] = seen
    return seen


def literal_detour(world, marshal, dest: str, order_type: str, blocked: str,
                   memo: Optional[dict] = None) -> Optional[List[str]]:
    """CC-X14 (CC-5's sibling sweep): the LITERAL arm of the executor's
    `_handle_first_step_blocked` — a corps met on the first step is GONE
    ROUND, the road re-plotted around every enemy-held province by
    `plot_route`'s reroute ladder (`avoid_is_law=True`: a reroute must still
    avoid what it fled; weighted for a march or a hold) — unless the corps
    stands on the destination itself (the order ends at the approach: None
    here, `_contact_line` says it). Returns the detour road, ``[]`` when no
    road goes round (the order breaks), or None when the arm does not apply.

    FOG: the quote goes round the provinces where we SEE a corps; the
    executor's reroute avoids the unseen too — a surprise the quote must not
    name (the drift census's `fog_surprise`)."""
    if str(getattr(marshal, "personality", "") or "") != "literal" or blocked == dest:
        return None
    from backend.commands import strategic as road_law
    road, _verdict = road_law.plot_route(
        world, marshal, dest, use_weighted=order_type in ("MOVE_TO", "HOLD"),
        avoid_regions=_seen_enemy_regions(world, marshal.nation, memo), avoid_is_law=True)
    return list(road) if road else []


def _road(world, marshal, dest: str, order_type: str, memo: Optional[dict]):
    key = (marshal.name, dest, order_type)
    if memo is not None and key in memo:
        return memo[key]
    from backend.commands import strategic as road_law
    got = road_law.march_road(world, marshal, dest, order_type)
    if memo is not None:
        memo[key] = got
    return got


def _standing_quote(world, marshal, dest: str, order_type: str, target: str,
                    probe_verb: str, q: Dict[str, Any], memo: Optional[dict],
                    standing_follow: Optional[bool] = None,
                    arrival: Optional[dict] = None) -> Dict[str, Any]:
    """The standing-order arms common to a march and a support: the state,
    the identical order (a no-op the executor takes at 0 AP), the road, the
    price, the clock. `standing_follow` (AO) tells a follow from a support
    when the identical order is read."""
    from backend.commands import strategic as road_law
    from backend.commands.state_probe import order_state_refusal
    state = order_state_refusal(world, marshal, probe_verb)
    if state:
        q["refusal"] = state
        return q
    order = getattr(marshal, "strategic_order", None)
    if (order is not None and not getattr(order, "condition", None)
            and getattr(order, "command_type", None) == order_type
            and str(getattr(order, "target", "") or "").lower() == str(target).lower()
            and (standing_follow is None
                 or bool(getattr(order, "standing_follow", False)) == bool(standing_follow))
            # CC-X20: the executor's own rule — what it does on arrival too.
            and road_law.order_arrival_matches(order, arrival)):
        q.update(ok=True, already=True,
                 note=f"{q['shown']} is already carrying out that order.")
        return q
    if order_type == "SUPPORT" and dest == marshal.location:
        # Already beside his friend: the order is taken with no road
        # (`_strategic_first_step`'s SUPPORT arm).
        road, refusal = [], None
    else:
        road, refusal, _kind = _road(world, marshal, dest, order_type, memo)
    if refusal is not None:
        q["refusal"] = str(refusal.get("message") or "the order is refused.")
        return q
    road = list(road or [])
    q.update(
        ok=True,
        ap=int(marshal.strategic_order_ap(order_type=order_type)),
        turns=int(road_law.march_turns(len(road), getattr(marshal, "movement_range", 1))),
        road=road,
        replaces=_replaces(marshal),
        objection=_strategic_objection(world, marshal, order_type, target, road),
    )
    # The first step is taken at once (`_strategic_first_step`): a corps we
    # SEE in the road's FIRST province meets the order now — the personality
    # arm, 1 action; one met deeper within a cavalryman's reach halts the
    # march before him this turn, at the full price. An unseen corps is a
    # surprise the quote must not name (fog).
    contact = visible_foe_on_road(world, world.player_nation, road[:1])
    if contact is not None:
        # CC-X14: a literal man does not halt there — he goes round (the
        # order keeps its own price, and the road and the clock are the
        # detour's).
        detour = literal_detour(world, marshal, dest, order_type, contact[1], memo)
        if detour is not None:
            if not detour:
                q.update(ok=False, ap=0, turns=0, road=[], replaces="", objection="none",
                         refusal=f"Path blocked at {contact[1]}, no alternate route.")
                return q
            q.update(road=detour, turns=int(road_law.march_turns(
                len(detour), getattr(marshal, "movement_range", 1))))
            q["contact"] = (f"{humanize_entity_name(contact[0].name)} blocks the road at "
                            f"{contact[1]} — {q['shown']} goes round him by {detour[0]}, "
                            f"to the letter of the order.")
            return q
        q["contact"] = _contact_line(q, marshal, contact[0], contact[1], dest)
        q["ap"] = 1
        return q
    reach = max(1, int(getattr(marshal, "movement_range", 1) or 1))
    halt = visible_foe_on_road(world, world.player_nation, road[1:reach])
    if halt is not None:
        q["contact"] = (f"{humanize_entity_name(halt[0].name)} stands at {halt[1]} — "
                        f"the march halts before him this turn.")
    return q


def march_quote(world, marshal, dest: str, *, then_attack: str = "",
                memo: Optional[dict] = None) -> Dict[str, Any]:
    """`<Marshal>, march to <dest>` (and `then attack <enemy>` when named —
    the CR-7 arrival tail, paid once with the march)."""
    shown = humanize_entity_name(marshal.name)
    command = f"{shown}, march to {dest}"
    if then_attack:
        command += f" then attack {humanize_entity_name(then_attack)}"
    q = _blank("march_attack" if then_attack else "march", marshal, dest, command)
    q = _standing_quote(world, marshal, dest, "MOVE_TO", dest, "march", q, memo,
                        arrival={"attack_on_arrival": bool(then_attack),
                                 "arrival_target": then_attack or None})
    if q["ok"] and not q["already"]:
        foe = visible_foe_on_road(world, world.player_nation, q["road"])
        if q["contact"]:
            q["note"] = q["contact"]
        elif foe is not None and foe[1] == dest:
            q["note"] = (f"{humanize_entity_name(foe[0].name)} holds {dest} — "
                         f"the march ends in contact.")
        elif foe is not None:
            q["note"] = (f"{humanize_entity_name(foe[0].name)} stands on the road at "
                         f"{foe[1]} — the march will meet him there.")
    return q


def march_reach(world, marshal) -> Dict[str, Any]:
    """CC-3 "Select, click, Enter": where `<marshal>, march to <P>` would be
    TAKEN, for every province P, and in how many turns — the map's ETA tint
    for a selected corps (`GET /march_reach`). The same readers as
    `march_quote`, in its order: the state probe, the identical standing
    order (taken at 0 AP), the road law — read for every province at once
    (`strategic.march_roads`: one pathfinding pass per rung of the ladder,
    the cautious avoid-set computed once — Rule 8), the arrival law. A
    province is in `reach` exactly when its `march_quote` is `ok`, with the
    quote's own road and turns (pinned). PURE."""
    from backend.commands import strategic as road_law
    from backend.commands.state_probe import order_state_refusal
    reach_range = max(1, int(getattr(marshal, "movement_range", 1) or 1))
    out: Dict[str, Any] = {
        "success": True,
        "marshal": marshal.name,
        "shown": humanize_entity_name(marshal.name),
        "location": marshal.location,
        "ap": int(marshal.strategic_order_ap(order_type="MOVE_TO")),
        "range": reach_range,
        "ok": False,
        "refusal": "",
        "reach": {},
    }
    state = order_state_refusal(world, marshal, "march")
    if state:
        out["refusal"] = state
        return out
    order = getattr(marshal, "strategic_order", None)
    already = ""
    if (order is not None and not getattr(order, "condition", None)
            and getattr(order, "command_type", None) == "MOVE_TO"
            and road_law.order_arrival_matches(order, None)):   # CC-X20: a plain march
        already = str(getattr(order, "target", "") or "").lower()
    reach: Dict[str, Any] = {}
    roads = road_law.march_roads(world, marshal, "MOVE_TO")
    detours = _literal_detours(world, marshal, roads)
    for dest, (road, refusal, _kind) in roads.items():
        if already and dest.lower() == already:
            # `_standing_quote`'s identical order: taken at 0 AP, whatever
            # the road reads today.
            reach[dest] = {"turns": int(road_law.march_turns(len(road or []), reach_range)),
                           "road": list(road or []), "already": True}
            continue
        if refusal is not None or not road:
            continue
        if dest in detours:
            road = detours[dest]   # CC-X14: a literal man goes round
            if not road:
                continue           # no road round him: the march is refused
        reach[dest] = {"turns": int(road_law.march_turns(len(road), reach_range)),
                       "road": list(road)}
    out["ok"] = True
    out["reach"] = reach
    return out


def _literal_detours(world, marshal, roads) -> Dict[str, List[str]]:
    """`literal_detour` for every destination at once (Rule 8): the first
    steps that meet a corps we see, read once, and the reroute ladder run
    as ONE pathfinding pass per rung (`weighted_paths_from`, pinned equal to
    `find_weighted_path`) — avoid + lawful, then avoid + terrain-only, as
    `plot_route(avoid_is_law=True)` climbs it. ``{dest: detour}`` for the
    destinations whose road meets such a corps on its first step and does
    not end there ([] where no road goes round); {} for any man but a
    literal one."""
    if str(getattr(marshal, "personality", "") or "") != "literal":
        return {}
    player = world.player_nation
    firsts = {road[0] for road, refusal, _kind in roads.values() if road and refusal is None}
    contacts = {f for f in firsts if visible_foe_on_road(world, player, [f]) is not None}
    if not contacts:
        return {}
    here = marshal.location
    seen = _seen_enemy_regions(world, marshal.nation, None)
    pf = marshal.nation if marshal.nation == player else None
    rungs = [world.weighted_paths_from(here, avoid_regions=seen, passable_for=pf)]
    if pf:
        rungs.append(world.weighted_paths_from(here, avoid_regions=seen))
    out: Dict[str, List[str]] = {}
    for dest, (road, refusal, _kind) in roads.items():
        if refusal is not None or not road or road[0] not in contacts or road[0] == dest:
            continue
        path = None
        for rung in rungs:
            path = rung.get(dest)
            if path:
                break
        out[dest] = [r for r in path if r != here] if path else []
    return out


def support_quote(world, marshal, ally, *, memo: Optional[dict] = None) -> Dict[str, Any]:
    """`<Marshal>, support <ally>` — a friendly, free corps; SUPPORT's own
    price (1 action for every marshal, SR-2e)."""
    shown_ally = humanize_entity_name(ally.name)
    q = _blank("support", marshal, ally.location,
               f"{humanize_entity_name(marshal.name)}, support {shown_ally}")
    if ally.name == marshal.name:
        q["refusal"] = "a marshal cannot support himself"
        return q
    if ally.nation != marshal.nation or getattr(ally, "captured_by", "") \
            or int(getattr(ally, "strength", 0) or 0) <= 0:
        q["refusal"] = f"{shown_ally} has no corps of ours in the field to support"
        return q
    return _standing_quote(world, marshal, ally.location, "SUPPORT", ally.name,
                           "support", q, memo, standing_follow=False)


def follow_quote(world, marshal, ally, *, memo: Optional[dict] = None) -> Dict[str, Any]:
    """AO: `<Marshal>, follow <ally>` — the SUPPORT that stands (marches where
    he marches, turn after turn, and to his guns; never lapses on "secure").
    SUPPORT's own price."""
    shown_ally = humanize_entity_name(ally.name)
    q = _blank("follow", marshal, ally.location,
               f"{humanize_entity_name(marshal.name)}, follow {shown_ally}")
    if ally.name == marshal.name:
        q["refusal"] = "a marshal cannot follow himself"
        return q
    if ally.nation != marshal.nation or getattr(ally, "captured_by", "") \
            or int(getattr(ally, "strength", 0) or 0) <= 0:
        q["refusal"] = f"{shown_ally} has no corps of ours in the field to follow"
        return q
    return _standing_quote(world, marshal, ally.location, "SUPPORT", ally.name,
                           "follow", q, memo, standing_follow=True)


def army_quote(world, region: str, *, memo: Optional[dict] = None) -> Dict[str, Any]:
    """AO (`REFORMS_SPEC.md` §5a): `the army, march to <region>` — ONE order
    at the Staff's price for every corps of the Emperor's column, or the
    reason there is no army order today (the Staff not in force, no Emperor
    in the field, authority below the gate, the pool, no corps in reach)."""
    from backend.commands import group_orders as G
    q: Dict[str, Any] = {
        "kind": "army", "marshal": "", "shown": "The army", "dest": region,
        "command": f"the army, march to {region}", "ok": False, "ap": int(G.ARMY_ORDER_AP),
        "turns": 0, "road": [], "refusal": "", "replaces": "", "objection": "none",
        "note": "", "contact": "", "already": False, "corps": [], "beyond": [],
    }
    if not G.army_order_available(world):
        q["refusal"] = ("the Grand Quartier Général is not in force — the Laws, under the "
                        "ledger, make the army one column")
        return q
    sovereign = G._sovereign(world)
    if sovereign is None:
        q["refusal"] = "no Emperor stands at the army's head"
        return q
    authority = G.authority_of(world)
    if authority < G.ARMY_AUTHORITY_HEARD:
        q["refusal"] = (f"authority {authority} — the marshals march only on your own word, "
                        f"one by one")
        return q
    if int(getattr(world, "actions_remaining", 0) or 0) < G.ARMY_ORDER_AP:
        q["refusal"] = f"needs {G.ARMY_ORDER_AP} actions"
        return q
    memo = {} if memo is None else memo
    corps, beyond, refused, doubters = [], [], [], []
    for m in _field_marshals(world):
        if m.location == region:
            continue
        try:
            dist = int(world.get_distance(m.location, sovereign.location))
        except Exception as exc:
            report(exc, "order_quotes.army_quote: world.get_distance")
            dist = 999
        if dist > G.ARMY_COLUMN_REACH:
            beyond.append(humanize_entity_name(m.name))
            continue
        mq = march_quote(world, m, region, memo=memo)
        if not mq["ok"]:
            refused.append(f"{mq['shown']} ({mq['refusal']})")
            continue
        if mq["objection"] == "possible":
            doubters.append(mq["shown"])
        corps.append({"marshal": m.name, "shown": mq["shown"], "turns": int(mq["turns"]),
                      "objection": mq["objection"]})
        q["turns"] = max(int(q["turns"]), int(mq["turns"]))
    q["corps"], q["beyond"] = corps, beyond
    if not corps:
        q["refusal"] = ("no corps of the column can march there"
                        + (": " + "; ".join(refused) if refused else ""))
        return q
    q["ok"] = True
    notes = [f"{len(corps)} corps march: " + ", ".join(c["shown"] for c in corps)]
    if doubters:
        if authority >= G.ARMY_AUTHORITY_CARRIES:
            notes.append("the Staff's order carries " + ", ".join(doubters) + " past their doubts")
        else:
            notes.append(", ".join(doubters) + f" would refuse the Staff's word (authority {authority})")
    if refused:
        notes.append("left to their own orders: " + "; ".join(refused))
    if beyond:
        notes.append("beyond the Emperor's reach: " + ", ".join(beyond))
    q["note"] = " · ".join(notes)
    return q


def attack_quote(world, marshal, enemy, *, memo: Optional[dict] = None) -> Dict[str, Any]:
    """An attack on a sighted enemy: `attack <enemy>` when he stands within
    the marshal's reach (the attack's own range rule — distance against
    `movement_range`), else the march that carries the attack there."""
    from backend.commands.state_probe import order_state_refusal
    distance = world.get_distance(marshal.location, enemy.location)
    if distance is None or distance < 0 or distance > int(getattr(marshal, "movement_range", 1) or 1):
        return march_quote(world, marshal, enemy.location, then_attack=enemy.name, memo=memo)
    shown_enemy = humanize_entity_name(enemy.name)
    q = _blank("attack", marshal, enemy.location,
               f"{humanize_entity_name(marshal.name)}, attack {shown_enemy}")
    state = order_state_refusal(world, marshal, "attack")
    if state:
        q["refusal"] = state
        return q
    ap = 0 if getattr(marshal, "has_counter_punch", lambda: False)() else int(world.get_action_cost("attack"))
    q.update(ok=True, ap=ap, turns=0, road=[enemy.location],
             objection=_tactical_objection(world, marshal, "attack", enemy.name))
    return q


def group_march_quotes(world, names: List[str], dest: str) -> Dict[str, Any]:
    """CC-5 group orders: `<member>, march to <dest>` for every corps of a
    Ctrl-click group, in the group's order, with ONE memo (the roads and the
    seen avoid-set read once) — the group card's lines, each the very
    `march_quote` the single card and the panel carry. A member standing on
    `dest` is named ("already at …"), never quoted; a name that is no corps of
    ours in the field is refused. The card sums the taken lines' `ap` against
    `ap_left`; nothing here is sent. PURE (`GET /march_quotes?marshals=…`)."""
    memo: dict = {}
    field = {m.name: m for m in _field_marshals(world)}
    quotes: List[Dict[str, Any]] = []
    for name in names:
        m = field.get(name)
        if m is None:
            shown = humanize_entity_name(name)
            quotes.append({"kind": "march", "marshal": name, "shown": shown, "dest": dest,
                           "command": "", "ok": False, "ap": 0, "turns": 0, "road": [],
                           "refusal": f"no corps of ours in the field named {shown}",
                           "replaces": "", "objection": "none", "note": "", "contact": "",
                           "already": False})
            continue
        if m.location == dest:
            q = _blank("march", m, dest, f"{humanize_entity_name(m.name)}, march to {dest}")
            q["refusal"] = f"already at {dest}"
            q["here"] = True
            quotes.append(q)
            continue
        quotes.append(march_quote(world, m, dest, memo=memo))
    return {"success": True, "dest": dest,
            "ap_left": int(getattr(world, "actions_remaining", 0) or 0), "quotes": quotes}


def _sort_key(q: Dict[str, Any]):
    return (0 if q["ok"] else 1, int(q["turns"]), int(q["ap"]), q["shown"])


def _field_marshals(world) -> List[Any]:
    return [m for m in world.get_player_marshals()
            if int(getattr(m, "strength", 0) or 0) > 0 and not getattr(m, "captured_by", "")]


def march_quotes_for_region(world, region: str) -> Dict[str, Any]:
    """Every click order the province panel offers at `region`, quoted:
    `march` (each corps of ours standing elsewhere), `support` (one row per
    corps of ours standing here) and `attack` (one row per enemy corps we see
    here, at war with us). One GET when the panel opens — never per response
    (Rule 8) — with the roads memoised within the call."""
    player = world.player_nation
    memo: dict = {}
    field = _field_marshals(world)
    here = [m for m in field if m.location == region]
    away = [m for m in field if m.location != region]
    march = sorted((march_quote(world, m, region, memo=memo) for m in away), key=_sort_key)
    support = []
    follow = []
    for ally in here:
        quotes = sorted((support_quote(world, m, ally, memo=memo) for m in away), key=_sort_key)
        support.append({"ally": ally.name, "ally_shown": humanize_entity_name(ally.name),
                        "quotes": quotes})
        # AO: the SUPPORT that stands, one row per corps of ours standing here.
        fq = sorted((follow_quote(world, m, ally, memo=memo) for m in away), key=_sort_key)
        follow.append({"ally": ally.name, "ally_shown": humanize_entity_name(ally.name),
                       "quotes": fq})
    attack = []
    seen_names = set()
    for row in world.get_visible_enemies_in_region(region, player):
        name = row.get("name") if isinstance(row, dict) else getattr(row, "name", "")
        enemy = world.get_marshal(name) if name else None
        if (enemy is None or name in seen_names or int(getattr(enemy, "strength", 0) or 0) <= 0
                or not world.is_at_war(player, enemy.nation)):
            continue
        seen_names.add(name)
        quotes = sorted((attack_quote(world, m, enemy, memo=memo) for m in away), key=_sort_key)
        attack.append({"enemy": enemy.name, "enemy_shown": humanize_entity_name(enemy.name),
                       "quotes": quotes})
    return {
        "success": True,
        "region": region,
        "ap_left": int(getattr(world, "actions_remaining", 0) or 0),
        "march": march,
        "support": support,
        "follow": follow,
        # AO: the Staff's one order for the Emperor's column — quoted, or the
        # reason there is none today (a dimmed chip that teaches the reform).
        "army": army_quote(world, region, memo=memo),
        "attack": attack,
    }
