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
        # S14E-13: what the march takes out of the Descent camp ("" when nothing).
        "camp": "",
        # S14E-13's sweep: what the march costs the corps as it stands — Iron
        # Resolve stacks, a formed square, a turn-1 drill ("" when nothing).
        "departs": "",
        # S14E-X67: the campaign pay the destination draws ("" when none).
        "pay": "",
        # S14E-22: the detour round a shut direct road ("" when none).
        "detour": "",
        # S14G-11: the guarded ground the road crosses - the Ansbach trap's
        # price in the order's own words ("" when none).
        "guard": "",
        # S14G-7: the front the destination is - an ally's province whose war
        # a truce of ours leaves running ("" when it is none).
        "front": "",
        # S14E-24: an attack's muster in one line - who answers the guns and
        # the band they make together ("" for every other order).
        "muster": "",
        # S14G-X165 (Pre-Deploy S14h part 2, October 26, 2026): what a win adds to
        # Europe's alarm - the muster's own alarm sentence, on the attack quote
        # alone ("" for every other order and for a field that is our own soil).
        "alarm": "",
        # S14G-2 / S14G-3 (Pre-Deploy S14h part 1): what the STANDING order does
        # once taken, in the order's own words (`standing_terms`: a support's
        # lapse, an aggressive man's interrupt) - "" when it has nothing to say.
        "terms": "",
        "already": False,
        # BA-2: an attack's plan, orderable — the orders the game already has
        # that would bring a corps standing by (`bring_quotes`; [] for every
        # other order).
        "bring": [],
    }


def standing_terms(world, marshal, order_type: str, target: str,
                   standing_follow: Optional[bool] = None) -> str:
    """S14G-2 / S14G-3: the terms of a standing order, said BEFORE it is given
    - the very sentences the order's reply prints
    (`strategic.support_terms_clause`, `strategic.aggressive_interrupt_clause`),
    so what the quote says is what the reply says. A plain SUPPORT: goes now,
    lapses of itself. An aggressive man: drops the order for a battle in a war
    of ours (a NEW order is never a road-home order). A FOLLOW has no support
    clause (it stays). "" when there is nothing to say."""
    from backend.commands import strategic as road_law
    parts = []
    if order_type == "SUPPORT" and not standing_follow:
        parts.append(road_law.support_terms_clause(
            marshal.name, target, timed=False).strip())
    parts.append(road_law.aggressive_interrupt_clause(world, marshal, None).strip())
    return " ".join(p for p in parts if p)


_MUSTER_READER: Dict[str, Any] = {}


def _muster_line(world, marshal, enemy) -> str:
    """S14E-24: Berthier's one-line muster for an attack - who answers the
    guns, the force they make and the band - the very sentence the contact
    ask carries (`CombatExecutor._contact_muster_note`: the muster ladder,
    the fog-banded enemy figure; "" for any corps but the player's). PURE: it
    prices the attack, it does not stage it."""
    try:
        reader = _MUSTER_READER.get("combat")
        if reader is None:
            from backend.commands.executor import CommandExecutor
            reader = _MUSTER_READER["combat"] = CommandExecutor()._combat
        return str(reader._contact_muster_note(marshal, enemy, world) or "").strip()
    except Exception as exc:
        report(exc, "order_quotes._muster_line: CombatExecutor._contact_muster_note")
        return ""


def _alarm_line(world, marshal, enemy) -> str:
    """S14G-X165 (Pre-Deploy S14h part 2, October 26, 2026): the map attack
    card's alarm clause - `A win here adds +3 to Europe's alarm (+5 more if
    decisive; none on your own soil) - now N/100.` - the very sentence the
    attack's muster preview prints (`CombatExecutor._muster_alarm_note`, S14G-M3),
    read at the field the attack would be fought on (the enemy's province).
    The one-line muster (`_muster_line`) carried the odds and none of this, so
    the card that sends at once priced the battle and not its alarm. PURE; ""
    for any corps but the player's and for our own soil."""
    try:
        from backend.commands.combat_executor import CombatExecutor
        return str(CombatExecutor._muster_alarm_note(world, marshal, enemy.location) or "").strip()
    except Exception as exc:
        report(exc, "order_quotes._alarm_line: CombatExecutor._muster_alarm_note")
        return ""


def _contact_line(q: Dict[str, Any], marshal, foe, region: str, dest: str) -> str:
    """What the march's FIRST step does on meeting a corps we can see —
    `_handle_first_step_blocked`'s arms, in its order (1 action is charged at
    once on every arm). S14E-D1 re-ruled (October 25, 2026): the aggressive
    man fights at once at favourable odds, as his line says."""
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
    from backend.game_logic.naval import camp_leave_line
    state = order_state_refusal(world, marshal, probe_verb)
    if state:
        q["refusal"] = state
        return q
    # S14G-4 (Pre-Deploy S14h part 1, October 26, 2026): the province he already
    # stands in is not a destination - the typed order refuses it free
    # (`_strategic_path`, the same sentence) and the quote said "ok" once a
    # standing order to it existed (the identical-order arm below). A march
    # that carries a verb for its arrival keeps the verb's business.
    if (order_type == "MOVE_TO" and dest == marshal.location
            and not (arrival and (arrival.get("attack_on_arrival")
                                  or arrival.get("arrival_verb")))):
        q["refusal"] = road_law.own_province_march_refusal(marshal, dest)
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
        terms=standing_terms(world, marshal, order_type, target, standing_follow),
    )
    # S14E-X67: the campaign pay the destination draws; S14E-22: the detour
    # round a shut direct road — both read off the order's own readers
    # (`campaign_pay_at`, `march_detour_reading`), before the first step's
    # contact arms so every return below carries them.
    from backend.commands.movement_executor import campaign_pay_line
    q["pay"] = campaign_pay_line(world, marshal, dest)
    # S14E-X87: a support and a follow ask in the same words, over the
    # breadth-first road the reading plots by the order's type.
    reading = road_law.march_detour_reading(world, marshal, dest, road, order_type)
    if reading is not None:
        q["detour"] = road_law.march_detour_sentence(dest, reading)
    # S14G-11: the guarded ground the road crosses (the typed order's free ask
    # and its reply print the same sentence); S14G-7: the front the
    # destination is (`movement_executor.front_line`, the reply's own words).
    from backend.commands.movement_executor import front_line
    guard = road_law.march_guard_reading(world, marshal, dest, road, order_type)
    if guard is not None:
        q["guard"] = road_law.march_guard_sentence(guard)
    q["front"] = front_line(world, marshal, dest)
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
                         terms="",
                         refusal=f"Path blocked at {contact[1]}, no alternate route.")
                return q
            q.update(road=detour, turns=int(road_law.march_turns(
                len(detour), getattr(marshal, "movement_range", 1))))
            # S14G-11: the literal man's road round the foe is the road walked -
            # the guarded ground is read off IT, not the road he did not take.
            _g = road_law.march_guard_reading(world, marshal, dest, detour, order_type)
            q["guard"] = road_law.march_guard_sentence(_g) if _g is not None else ""
            q["contact"] = (f"{humanize_entity_name(contact[0].name)} blocks the road at "
                            f"{contact[1]} — {q['shown']} goes round him by {detour[0]}, "
                            f"to the letter of the order.")
            q["camp"] = camp_leave_line(world, marshal, detour)   # S14E-13
            from backend.commands.movement_executor import departure_note
            q["departs"] = departure_note(marshal, quote=True)
            return q
        q["contact"] = _contact_line(q, marshal, contact[0], contact[1], dest)
        q["ap"] = 1
        return q
    reach = max(1, int(getattr(marshal, "movement_range", 1) or 1))
    halt = visible_foe_on_road(world, world.player_nation, road[1:reach])
    # S14E-13: the stop the turn's end finds him at — a halt before a seen foe
    # keeps him on the road's earlier stop; a road that leaves the Descent
    # camp's provinces says what that takes out of the camp.
    camp_road = road
    if halt is not None:
        q["contact"] = (f"{humanize_entity_name(halt[0].name)} stands at {halt[1]} — "
                        f"the march halts before him this turn.")
        camp_road = road[:road.index(halt[1])]
    q["camp"] = camp_leave_line(world, marshal, camp_road)
    from backend.commands.movement_executor import departure_note
    q["departs"] = departure_note(marshal, quote=True)
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
    if q["ok"] and then_attack:
        # S14E-4's sweep: the march's arrival attack on a sheltered corps
        # would be refused — the "march & attack" chip says so now.
        sheltered = _peace_soil_refusal_line(world, marshal, world.get_marshal(then_attack))
        if sheltered:
            q.update(ok=False, refusal=sheltered, terms="")
            return q
    if q["ok"] and then_attack and not q["already"]:
        # S14E-X81: the muster is read where the corps ARRIVES, not here --
        # a muster read now (the plain attack card's real line) would price a
        # field the corps has not reached and the allies it has not yet
        # drawn. The card says when it will be read.
        q["muster"] = f"On arrival Berthier will read the muster at {dest}."
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
        # S14G-4: the province he stands in is no destination, even one a
        # standing order still names (`_standing_quote` refuses it first).
        if already and dest.lower() == already and dest != marshal.location:
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
    # S14G-X159: `plot_route`'s mover on every rung (the same tie rule).
    mover = marshal.nation
    rungs = [world.weighted_paths_from(here, avoid_regions=seen, passable_for=pf,
                                       mover_nation=mover)]
    if pf:
        rungs.append(world.weighted_paths_from(here, avoid_regions=seen, mover_nation=mover))
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


def detour_count_clause(detoured: int, total: int) -> str:
    """S14E-X88 / S14E-X134: how many of `total` corps would be ASKED about
    their road — the one sentence the army quote's note (`army_quote`) and the
    typed Staff order's head line (`group_orders._head_line`) both print, so
    what the card counted is what the order says. '' when none would."""
    if detoured == 1:
        return f"1 of {total} corps takes a long or foreign road — his card says which"
    if detoured:
        return f"{detoured} of {total} corps take a long or foreign road — their cards say which"
    return ""


def column_detours(world, names: List[str], strategic_type: Optional[str], target: str,
                   *, memo: Optional[dict] = None) -> int:
    """S14E-X134: how many of the named corps' roads for a typed army order
    (`strategic_type` ∈ MOVE_TO / SUPPORT / PURSUE, `target` the province or
    the marshal it names) carry a `detour` rider - read through the very
    readers the corps' own cards print (`march_quote` / `support_quote`, and
    `march_detour_reading` over the pursuit's breadth-first road), so the head
    line and the cards cannot disagree. PURE; 0 for any road it cannot read."""
    from backend.commands import strategic as road_law
    count = 0
    for name in names:
        marshal = world.get_marshal(name)
        if marshal is None or not target:
            continue
        if strategic_type == "MOVE_TO":
            count += 1 if march_quote(world, marshal, target, memo=memo)["detour"] else 0
        elif strategic_type == "SUPPORT":
            ally = world.get_marshal(target)
            # a follow is the same standing SUPPORT over the same road
            if ally is not None and support_quote(world, marshal, ally, memo=memo)["detour"]:
                count += 1
        elif strategic_type == "PURSUE":
            foe = world.get_marshal(target)
            if foe is None:
                continue
            road, refusal, _kind = _road(world, marshal, foe.location, "PURSUE", memo)
            if (refusal is None and road
                    and road_law.march_detour_reading(world, marshal, foe.location, road, "PURSUE")):
                count += 1
    return count


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
        # S14E-X88: each corps row carries the march card's `detour` rider.
        corps.append({"marshal": m.name, "shown": mq["shown"], "turns": int(mq["turns"]),
                      "objection": mq["objection"], "detour": mq["detour"],
                      # S14G-2: an aggressive corps' interrupt, said on its row too.
                      "terms": mq["terms"],
                      # S14G-11 / S14G-7: the guarded ground its road crosses and
                      # the front it marches to, said on its row too.
                      "guard": mq["guard"], "front": mq["front"]})
        q["turns"] = max(int(q["turns"]), int(mq["turns"]))
    q["corps"], q["beyond"] = corps, beyond
    if not corps:
        q["refusal"] = ("no corps of the column can march there"
                        + (": " + "; ".join(refused) if refused else ""))
        return q
    q["ok"] = True
    notes = [f"{len(corps)} corps march: " + ", ".join(c["shown"] for c in corps)]
    # S14E-X88: how many of them would be ASKED about their road (the same
    # reading the typed order and each corps' own card print).
    detoured = sum(1 for c in corps if c["detour"])
    if detoured:
        notes.append(detour_count_clause(detoured, len(corps)))   # S14E-X134: one sentence, two surfaces
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


def _peace_soil_refusal_line(world, marshal, enemy) -> str:
    """S14E-4's sweep: the executor's own refusal of a field on peace soil
    (`world_state.reckless_charge_peace_owner`, drift-pinned to the guard;
    `combat_executor.peace_soil_refusal`'s one sentence), '' when the
    attack is lawful or the marshal is a gun (it fires from where it stands)."""
    if getattr(marshal, "artillery", False) or enemy is None:
        return ""
    from backend.models.world_state import reckless_charge_peace_owner
    owner = reckless_charge_peace_owner(world, marshal, enemy)
    if owner is None:
        return ""
    from backend.commands.combat_executor import peace_soil_refusal
    return str(peace_soil_refusal(marshal, enemy, {"owner": owner}, world)["message"])


def _band_range(label: str) -> Tuple[int, int]:
    """The (low, high) men a strength-band label spans (`intel.STRENGTH_BANDS`).
    The open-ended top band ("massive force") has no ceiling: its high is 0
    (UI-5 review — it read as an exact figure), and the card shows its words."""
    from backend.models.intel import STRENGTH_BANDS
    low = 0
    for threshold, band in STRENGTH_BANDS:
        if band == label:
            return int(low), int(threshold - 1) if threshold is not None else 0
        if threshold is not None:
            low = threshold
    return 0, 0


def _force_block(world, marshal, enemy) -> Optional[Dict[str, Any]]:
    """UI-5: the attack card's force bar - ours (the lead plus the corps that
    would answer the guns, `muster_odds`' committed term) against the foe
    through the ONE fog-banded helper (`_fog_banded_strength`): exact at FULL
    (low == high), the intel band's range otherwise, 0/0 "strength unknown"
    with no intel. `odds` is the muster's band word, given only on an exact
    sighting (a band word on a fogged foe would read his true strength back).
    None (the quote carries no `force`) when the reading fails. PURE."""
    try:
        from backend.commands.combat_executor import answering_defender
        from backend.commands.executor import CommandExecutor
        reader = _MUSTER_READER.get("combat")
        if reader is None:
            reader = _MUSTER_READER["combat"] = CommandExecutor()._combat
        if marshal.nation != getattr(world, "player_nation", None):
            return None
        label = str(reader._fog_banded_strength(answering_defender(world, enemy), world))
        odds = reader.muster_odds(marshal, enemy, world)
        ours = int(marshal.strength) + int(float(odds.get("committed_attacker", 0.0) or 0.0))
        if label.endswith(" men"):
            figure = int(label.replace(" men", "").replace(",", ""))
            low = high = figure
            word = str(odds.get("band") or "")
        elif label == "strength unknown":
            low = high = 0
            word = ""
        else:
            low, high = _band_range(label)
            word = ""
            if high == 0 and low > 0:
                label = f"{label} ({low:,}+)"
        return {"ours": ours, "theirs_low": int(low), "theirs_high": int(high),
                "theirs_label": label, "odds": word}
    except Exception as exc:
        report(exc, "order_quotes._force_block: muster_odds / _fog_banded_strength")
        return None


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
    # S14E-4's sweep (the province panel's chip): a corps sheltered on peace
    # soil — the typed order is refused at no cost (PT-F1's neutral arm, the
    # player's lead, a gun excepted), so the chip dims with the reason
    # instead of quoting `ok`.
    sheltered = _peace_soil_refusal_line(world, marshal, enemy)
    if sheltered:
        q["refusal"] = sheltered
        return q
    ap = 0 if getattr(marshal, "has_counter_punch", lambda: False)() else int(world.get_action_cost("attack"))
    q.update(ok=True, ap=ap, turns=0, road=[enemy.location],
             objection=_tactical_objection(world, marshal, "attack", enemy.name),
             muster=_muster_line(world, marshal, enemy),
             alarm=_alarm_line(world, marshal, enemy),
             bring=bring_quotes(world, marshal, enemy, memo=memo, attack_ap=ap))
    force = _force_block(world, marshal, enemy)
    if force is not None:
        q["force"] = force
        # Row BA (BA-3): the attack card says beforehand when the battle it
        # opens would be a great one and the points its commander brings —
        # read off the force bar's own figures (his LEAST strength under fog:
        # "great" is never promised on men we cannot see).
        from backend.game_logic import battle_day as _day
        great = _day.forecast(world, marshal, int(force["ours"]) + int(force["theirs_low"]),
                              foe=enemy)
        # No forecast while the day against him is ALREADY open: the card said
        # "A great battle — Ney commands the day: 2 points" over a day whose
        # purse stood at one (the day's own block tells it, on the table and
        # at the head of the province's panel).
        if great is not None and _day.day_against(world, enemy.name) is None:
            q["day"] = great
    return q


# The muster's reasons a WRITTEN ORDER answers — the three its own hint names
# (`combat_executor.muster_row_hint`): the literal man who awaits orders, the
# eye on a crown, the corps holding a position.
BROUGHT_BY_AN_ORDER = ("literal_awaits_orders", "eyes_on_a_crown", "holding_position")
# A corps that would come anyway is offered the order only when it lifts his
# odds by this much — the muster's own bar for naming the lever
# (`CombatExecutor._arrival_odds_row`).
BRING_ODDS_GAIN = 15


def _stop_this_turn(world, marshal, q: Dict[str, Any]) -> str:
    """Where a standing order's FIRST march leaves him this turn — the order
    is taken and he sets off at once (`_strategic_first_step`): as far along
    the quote's road as he ranges, short of a corps we see on it (one in the
    road's first province meets the order where he stands) and short of a
    frontier he may not cross — the move's own rule, `can_enter_territory`: a
    literal man's road ROUND a corps can be plotted through a neutral's shut
    frontier, that march is refused and he stands where he was (BA2-X10).
    His own province when the road is empty. An unseen corps is a surprise no
    quote may name."""
    from backend.game_logic.diplomacy import can_enter_territory
    walked = marshal.location
    reach = max(1, int(getattr(marshal, "movement_range", 1) or 1))
    for province in list(q.get("road") or [])[:reach]:
        if visible_foe_on_road(world, world.player_nation, [province]) is not None:
            break
        region = world.get_region(province)
        holder = getattr(region, "controller", None) if region is not None else None
        if holder and holder != marshal.nation and not can_enter_territory(
                world, marshal.nation, holder, mover_location=walked):
            break
        walked = province
    return walked


def _first_step_asks(world, q: Dict[str, Any], dest: str) -> bool:
    """A corps we SEE in the road's first province, and that province not the
    friend's own: the order's first step is then no march — the aggressive man
    fights at once if the numbers favour him, every other asks the Emperor's
    orders (`_contact_line`'s personality arms; a literal man's quote already
    carries his road ROUND the foe). Of the question's four answers one keeps
    the order ("Go Around"), one sends him in alone and two abandon it, the
    action spent: an order that asks is not an order that brings."""
    first = list(q.get("road") or [])[:1]
    return (bool(first) and first[0] != dest
            and visible_foe_on_road(world, world.player_nation, first) is not None)


def _odds_under_the_order(reader, lead, marshal, stop: str, battle_region: str, world) -> int:
    """His odds of answering these guns once the order is written, read from
    where its first march leaves him (the departing ground is part of the roll:
    from the mountains at Munich, Bernadotte's 47 % at Franconia is nothing).
    A copy stands at `stop`; the corps itself is not moved."""
    import copy
    ghost = copy.copy(marshal)
    ghost.location = stop
    row = reader._arrival_odds_row(lead, ghost, battle_region, world, "x")
    return int(row.get("arrival_odds_with_support", 0))


def bring_quotes(world, lead, enemy, *, memo: Optional[dict] = None,
                 attack_ap: Optional[int] = None) -> List[Dict[str, Any]]:
    """Row BA, BA-2 (BATTLE_DIORAMA_SPEC §15.5.5): the plan of battle,
    orderable at the attack row. For an attack by `lead` on `enemy`: every
    corps of ours standing by that the muster says will NOT come, or may not,
    and that the order the game already has would bring — THAT order, quoted
    at its own price (`support_quote`), with the reason and the odds before
    and after. No new order and no new number: the muster ladder as
    `CombatExecutor.muster_odds` walks it, the odds `_arrival_odds_row` prints.

    **It promises only what the order delivers.** A SUPPORT order marches the
    corps toward the lead at once, so the odds "under a written order" are
    read from where that first march leaves him (`_stop_this_turn`,
    `_odds_under_the_order`), and a row is offered only when he will still
    stand on the field or beside it with odds above nothing — and, for a man
    who would come anyway, `BRING_ODDS_GAIN` better than he has now. Nor is a
    row offered when the order's first step meets a corps we see on his road
    (`_first_step_asks`): he would fight at once on his own, or ask — on the
    opening board Murat, whose road to Ney runs through Mack. Nor when the
    order would first ASK the Emperor — a road round a neutral's shut
    frontier, guarded ground: the quote's `detour` and `guard`, the
    executor's "support, or cancel?" (BA2-X9) — nor when its price is the
    action the attack itself needs (`attack_ap`, the attack's own price: the
    corps would be ordered to a battle that cannot then be fought this turn;
    BA2-X8).

    PURE: it prices the plan, it does not stage it (never
    `_build_muster_preview`, which spends the one-time muster hint). Each row
    is a `support_quote` plus `why`, `code`, `odds_now` (percent; −1 for a man
    who will not march unordered) and `odds_with` (percent, under the order;
    −1 for an order that would be refused)."""
    out: List[Dict[str, Any]] = []
    if lead.nation != world.player_nation:
        return out
    try:
        from backend.commands.combat_executor import answering_defender
        from backend.display_names import MUSTER_REASON_DISPLAY
        reader = _MUSTER_READER.get("combat")
        if reader is None:
            from backend.commands.executor import CommandExecutor
            reader = _MUSTER_READER["combat"] = CommandExecutor()._combat
        battle_region = answering_defender(world, enemy).location
        if attack_ap is None:
            attack_ap = 0 if getattr(lead, "has_counter_punch", lambda: False)() \
                else int(world.get_action_cost("attack"))
        actions_left = int(getattr(world, "actions_remaining", 0) or 0)
        region = world.get_region(battle_region)
        beside = set(region.adjacent_regions) if region is not None else set()
        for m in _field_marshals(world):
            if m.name == lead.name:
                continue
            if m.location != battle_region and m.location not in beside:
                continue
            will_join, code = reader._muster_reason(m, lead, battle_region, lead.nation, world)
            odds_now = -1
            if will_join:
                if code == "has_support_order" or m.location == battle_region:
                    continue
                odds_now = int(reader._arrival_odds_row(
                    lead, m, battle_region, world, code).get("arrival_odds", 0))
            elif code not in BROUGHT_BY_AN_ORDER:
                continue
            q = support_quote(world, m, lead, memo=memo)
            odds_with = -1
            if q["ok"]:
                if q["already"]:
                    continue
                if _first_step_asks(world, q, lead.location):
                    continue          # the order would raise his question, or his own fight
                if q.get("detour") or q.get("guard"):
                    continue          # the order would ask the Emperor first (BA2-X9)
                if actions_left < int(attack_ap) + int(q.get("ap") or 0):
                    continue          # its price is the action the attack needs (BA2-X8)
                stop = _stop_this_turn(world, m, q)
                if stop != battle_region and stop not in beside:
                    continue          # the order's first march takes him out of reach
                odds_with = 100 if stop == battle_region else _odds_under_the_order(
                    reader, lead, m, stop, battle_region, world)
                if odds_with <= 0 or (will_join and odds_with < odds_now + BRING_ODDS_GAIN):
                    continue
            if will_join:
                why = f"about {odds_now}% to make it in time"
            else:
                why = str(MUSTER_REASON_DISPLAY.get(code, "") or "will not march unordered")
            if odds_with >= 0:
                why += f"; about {odds_with}% under a written order"
            q.update(why=why, code=str(code), odds_now=odds_now, odds_with=odds_with)
            out.append(q)
    except Exception as exc:
        report(exc, "order_quotes.bring_quotes: the muster ladder")
        return []
    return sorted(out, key=_sort_key)


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
    here, at war with us; `quotes` the corps standing away, `here` those
    already in the province - S14E-X79). One GET when the panel opens — never per response
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
        # S14E-X79: the corps already standing in this province are quoted too
        # (the same `attack_quote`, muster and all): the panel's Attack chips in
        # a marshal's own row send at once and read their muster from here.
        here_quotes = sorted((attack_quote(world, m, enemy, memo=memo) for m in here),
                             key=_sort_key)
        attack.append({"enemy": enemy.name, "enemy_shown": humanize_entity_name(enemy.name),
                       "quotes": quotes, "here": here_quotes})
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
