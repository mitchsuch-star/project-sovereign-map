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

import types
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
        # BA2-X21 (row BA, BA-4): what the order's FIRST march costs in men —
        # a standing order sets off at once, and the march rule is exact
        # (`movement_executor.march_attrition_reading`). "" when it costs
        # nothing or the first step is no march.
        "march_cost": "",
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


_A_SUPPORT_ORDER = types.SimpleNamespace(command_type="SUPPORT")


def _halts_at_the_approach(world, ally, region: str, dest: str) -> bool:
    """The SUPPORT order's approach arm as the EXECUTOR reads it — the one
    predicate, `strategic.support_stands_at_approach`: the foe on the friend's
    own province (DDB-20), or within the friend's reach (row BA, BA-4 — the
    approach rule). The order then stands, raises no question, and the corps
    joins the friend's next attack from where he is. A follow is a SUPPORT
    order too (it only stands longer), so its quote reads the same arm."""
    if ally is None:
        return region == dest
    from backend.commands import strategic as road_law
    return bool(road_law.support_stands_at_approach(_A_SUPPORT_ORDER, ally, region, world))


def _contact_line(q: Dict[str, Any], marshal, foe, region: str, dest: str,
                  world=None, ally=None) -> str:
    """What the march's FIRST step does on meeting a corps we can see —
    `_handle_first_step_blocked`'s arms, in its order (1 action is charged at
    once on every arm). S14E-D1 re-ruled (October 25, 2026): the aggressive
    man fights at once at favourable odds, as his line says."""
    shown = q["shown"]
    name = humanize_entity_name(foe.name)
    where = (f"{name} holds {region}" if region == dest
             else f"{name} blocks the road at {region}")
    if q["kind"] in ("support", "follow") and _halts_at_the_approach(world, ally, region, dest):
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


def _state_refusal(world, marshal, verb: str, word) -> str:
    """The order's state refusal. For a WORD of an open day (BA3-X5) it is
    read without the turn's action pool — a word costs no action
    (`battle_day.quoting_a_word`); every other test stands."""
    from backend.commands.state_probe import order_state_refusal
    if word is None:
        return order_state_refusal(world, marshal, verb)
    from backend.game_logic import battle_day as _day
    with _day.quoting_a_word():
        return order_state_refusal(world, marshal, verb)


def _standing_quote(world, marshal, dest: str, order_type: str, target: str,
                    probe_verb: str, q: Dict[str, Any], memo: Optional[dict],
                    standing_follow: Optional[bool] = None,
                    arrival: Optional[dict] = None, word=None) -> Dict[str, Any]:
    """The standing-order arms common to a march and a support: the state,
    the identical order (a no-op the executor takes at 0 AP), the road, the
    price, the clock. `standing_follow` (AO) tells a follow from a support
    when the identical order is read."""
    from backend.commands import strategic as road_law
    from backend.game_logic.naval import camp_leave_line
    state = _state_refusal(world, marshal, probe_verb, word)
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
        # Row FUN, FUN-1 (November 25, 2026): what the card can offer as the
        # way through — the court whose closed border stops the road (its
        # open-borders proposal), the sea leg a landing would cross.
        if refusal.get("blocked_diplomatic") and road_law.border_can_be_opened(refusal.get("blocked_state")):
            # (the review, lane B: open borders is proposed from PEACE only —
            # an armistice's closed border offers no such button)
            from backend.display_names import display_nation_in_sentence
            q["closed_to"] = str(refusal["blocked_diplomatic"])
            q["closed_to_shown"] = display_nation_in_sentence(q["closed_to"])
        leg = refusal.get("naval_leg")
        if leg and len(leg) == 2 and leg[1]:
            q["crossing"] = {"from": str(leg[0]), "to": str(leg[1]),
                             "verdict": str(refusal.get("naval_verdict") or "")}
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
        # Row BA, BA-4: the SUPPORT order's approach arm comes BEFORE every
        # personality arm in the executor (`_handle_first_step_blocked`) — a
        # literal man too halts at the approach where the foe stands within
        # his friend's reach, and goes round nothing.
        ally = world.get_marshal(target) if order_type == "SUPPORT" else None
        halts = ally is not None and _halts_at_the_approach(world, ally, contact[1], dest)
        # CC-X14: a literal man does not halt there — he goes round (the
        # order keeps its own price, and the road and the clock are the
        # detour's).
        detour = (None if halts
                  else literal_detour(world, marshal, dest, order_type, contact[1], memo))
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
            # BA2-X21: the detour is the road walked — its first march's cost.
            q["march_cost"] = march_cost_line(world, marshal, _first_march(world, marshal, q))
            return q
        q["contact"] = _contact_line(q, marshal, contact[0], contact[1], dest,
                                     world=world, ally=ally)
        q["ap"] = 1
        if halts:
            # Row BA, BA-4: the order stands at the approach — the road and
            # its clock are not walked this turn; the card's clock says so
            # ("halts at the approach", where it said "joins him in N turns").
            q["halts"] = True
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
    # BA2-X21: what the first march — taken the moment the order is — costs in men.
    q["march_cost"] = march_cost_line(world, marshal, _first_march(world, marshal, q))
    return q


# ═══ Row PW "Plain Words" (November 18, 2026 — the first playtest) ═══════════
#
# "clicking on genral and sending them somewhere is bad ux and it almosyt
# always costs 2 eeven if next to them". Measured on the player's own record:
# every click order in his history is `<Marshal>, march to <Province>` — the
# standing order, 2 actions — while the same step typed as `move to` is the
# plain move, 1 action, he arrives now. The click road quoted ONE verb for
# every distance.
#
# THE MOVE WITHIN REACH: a destination the plain move's own law takes — within
# his `movement_range`, the state probe clear, `move_refusal_probe` silent, a
# connector open for a two-province hop — is quoted as `<Marshal>, move to
# <dest>` at the move's price, arriving now. Everything else (further off, an
# enemy in the way, a closed frontier) is the march, as before, in its own
# words. The EXECUTOR is untouched (GR5: the AI's road is byte-identical) —
# only what the click road asks for changes; the typed verbs mean what they
# always meant. The drift census (`tests/test_pw_plain_words.py`) sends every
# quoted move and compares what `/command` then does, field for field.

def a_move_in_reach_is_a_move() -> bool:
    """The seam (one line to reverse). Down (False): every click order to a
    province is the march, as CC-2 landed it."""
    return True


def move_quote(world, marshal, dest: str, *, memo: Optional[dict] = None
               ) -> Optional[Dict[str, Any]]:
    """`<Marshal>, move to <dest>` when the plain move takes it — else None,
    and the march quote speaks (its refusals are the road's own sentences)."""
    if not a_move_in_reach_is_a_move():
        return None
    region = world.get_region(dest) if dest else None
    if region is None or dest == marshal.location:
        return None
    reach = max(1, int(getattr(marshal, "movement_range", 1) or 1))
    try:
        distance = world.get_distance(marshal.location, dest)
    except Exception as exc:
        report(exc, "order_quotes.move_quote: world.get_distance")
        return None
    if distance is None or not (0 < int(distance) <= reach):
        return None
    order = getattr(marshal, "strategic_order", None)
    if (order is not None and getattr(order, "command_type", None) == "MOVE_TO"
            and str(getattr(order, "target", "") or "").lower() == str(dest).lower()):
        return None   # the identical standing order: the march quote's "already" arm
    from backend.commands import strategic as road_law
    from backend.commands.movement_executor import (
        MovementExecutor, campaign_pay_line, departure_note, front_line, two_province_hop)
    from backend.game_logic.naval import camp_leave_line
    shown = humanize_entity_name(marshal.name)
    q = _blank("move", marshal, dest, f"{shown}, move to {dest}")
    state = _state_refusal(world, marshal, "move", None)
    if state:
        q["refusal"] = state
        return q
    if MovementExecutor.move_refusal_probe(world, marshal, region, dest) is not None:
        return None
    road = [dest]
    if int(distance) == 2:
        connector, _refusal = two_province_hop(world, marshal, dest)
        if not connector:
            return None
        road = [connector, dest]
    q.update(
        ok=True,
        ap=int(world.get_action_cost("move")),
        turns=0,
        road=road,
        replaces=_replaces(marshal),
        objection=_tactical_objection(world, marshal, "move", dest),
    )
    q["pay"] = campaign_pay_line(world, marshal, dest)
    guard = road_law.march_guard_reading(world, marshal, dest, road, "MOVE_TO")
    if guard is not None:
        q["guard"] = road_law.march_guard_sentence(guard)
    q["front"] = front_line(world, marshal, dest)
    q["camp"] = camp_leave_line(world, marshal, road)
    q["departs"] = departure_note(marshal, quote=True)
    q["march_cost"] = march_cost_line(world, marshal, road, first=False)
    return q


def _with_ground(world, marshal, q: Dict[str, Any]) -> Dict[str, Any]:
    """Row PW: what the order does to the province it ends in (`ground`,
    `backend/commands/ground.py`) and whether the click road should stop and
    ASK before it sends (`confirm`). A plain move or march goes at once — the
    tag by the cursor has already said its price and its end; the card is
    kept for what is rare and costly: an order the game refuses (the card
    says why), an attack, a road that meets a corps, guarded ground or an
    ally's front, and a province he would enter WITHOUT taking where an order
    exists that would take it."""
    from backend.commands import ground
    if not ground.the_ground_is_read_before_the_order():
        return q
    kind = str(q.get("kind") or "")
    if kind in ("move", "march", "march_attack"):
        try:
            q["ground"] = ground.entering(world, marshal, str(q.get("dest") or ""))
        except Exception as exc:
            report(exc, "order_quotes._with_ground: ground.entering")
            q["ground"] = {}
    reading = q.get("ground") or {}
    try:
        q["tag"] = tag_lines(world, marshal, q)
    except Exception as exc:
        report(exc, "order_quotes._with_ground: tag_lines")
        q["tag"] = []
    if q.get("already"):
        q["confirm"] = False      # the order already stands: nothing to ask
        return q
    q["confirm"] = bool(
        not q.get("ok")
        or kind not in ("move", "march")
        or q.get("contact") or q.get("guard") or q.get("front") or q.get("note")
        or (reading.get("takes") is not True and reading.get("remedy_command")))
    return q


def _moves_in_reach(world, marshal) -> Dict[str, Dict[str, Any]]:
    """Every province the plain move takes from where he stands (`move_quote`
    ok), for the reach's tint: a handful of neighbours, never the map."""
    out: Dict[str, Dict[str, Any]] = {}
    if not a_move_in_reach_is_a_move():
        return out
    here = world.get_region(marshal.location)
    if here is None:
        return out
    reach = max(1, int(getattr(marshal, "movement_range", 1) or 1))
    ring = list(getattr(here, "adjacent_regions", []) or [])
    seen = set(ring)
    if reach >= 2:
        for name in list(ring):
            neighbour = world.get_region(name)
            for further in (getattr(neighbour, "adjacent_regions", []) or []) if neighbour else []:
                if further not in seen and further != marshal.location:
                    seen.add(further)
                    ring.append(further)
    for dest in ring:
        try:
            q = move_quote(world, marshal, dest)
        except Exception as exc:
            report(exc, "order_quotes._moves_in_reach: move_quote")
            q = None
        if q is not None and q.get("ok"):
            out[dest] = q
    return out


def take_quote(world, marshal, target: str = "") -> Dict[str, Any]:
    """Row PW ("i had 3 people in colinia and no one could take it"): the order
    that TAKES a province — `<Marshal>, attack <Province>`, the attack road's
    own exits, quoted: taken now where nothing holds it, the garrison's storm
    with its reckoning, the works' siege. The province he STANDS in (`target`
    empty: `ground.standing`), or one within his reach that he would only
    enter by marching (`ground.entering` — the card's "storm it instead").
    Refused in plain words when nothing would take it (a corps of his still in
    the field — that is an attack on HIM — or no war, or too few men)."""
    from backend.commands import ground
    here = str(marshal.location or "")
    name = str(target or here)
    shown = humanize_entity_name(marshal.name)
    reading = (ground.standing(world, marshal) if name == here
               else ground.entering(world, marshal, name))
    q = _blank("take", marshal, name, f"{shown}, attack {name}")
    q["ground"] = reading
    q["confirm"] = True
    # Row IC, Session 2b (the review): a man on his task to prove himself
    # takes no orders — said FIRST, before anything about the ground (the
    # quote read "Mack stands there — he must be beaten first" of a man who
    # can be sent at nobody).
    from backend.commands.state_probe import trial_reason as _trial_reason
    _on_task = _trial_reason(marshal)
    if _on_task:
        q["refusal"] = _on_task
        return q
    code = str(reading.get("code") or "")
    takeable = ("open", "garrison", "fort") if name == here else (
        "garrison", "garrison_unsure", "fort", "takes", "takes_if_open", "liberates")
    if code not in takeable:
        q["refusal"] = str(reading.get("line") or f"{name} is not to be taken.")
        return q
    if name != here:
        reach = max(1, int(getattr(marshal, "movement_range", 1) or 1))
        try:
            distance = world.get_distance(here, name)
        except Exception as exc:
            report(exc, "order_quotes.take_quote: world.get_distance")
            distance = None
        if distance is None or int(distance) > reach:
            q["refusal"] = f"{name} is out of {shown}'s reach — march him beside it first."
            return q
        # The review (PW-R3): the attack road's own sea gate (`crossing_check_
        # reach`, NV-9) — a strait an enemy fleet covers refuses the order, and
        # the quote said "ok" over it.
        try:
            from backend.game_logic.naval import crossing_check_reach
            cross = crossing_check_reach(world, marshal.nation, here, name, int(marshal.strength))
            if not cross.get("allowed", True):
                q["refusal"] = str(cross.get("message") or f"The sea bars the way to {name}.")
                return q
        except Exception as exc:
            report(exc, "order_quotes.take_quote: crossing_check_reach")
    state = _state_refusal(world, marshal, "attack", None)
    if state:
        q["refusal"] = state
        return q
    q.update(ok=True, ap=int(world.get_action_cost("attack")), turns=0,
             replaces=_replaces(marshal),
             objection=_tactical_objection(world, marshal, "attack", name))
    region = world.get_region(name)
    if code in ("garrison", "garrison_unsure") and region is not None:
        try:
            from backend.game_logic.garrison_report import assault_forecast_text
            q["muster"] = assault_forecast_text(world, world.player_nation, marshal, region)
        except Exception as exc:
            report(exc, "order_quotes.take_quote: assault_forecast_text")
    elif code == "fort":
        # The works' rule (`_capture_or_besiege`: one turn held; the turn's end
        # counts it, and a corps that leaves or is driven off loses the siege).
        q["note"] = (f"{name} is fortified: {shown} lays siege, and it falls when the turn "
                     f"ends if he still stands there. If he leaves or is driven off, the "
                     f"siege is lost.")
    elif name == here:
        q["confirm"] = False     # nothing holds it: one click takes it
    return q


def march_quote(world, marshal, dest: str, *, then_attack: str = "",
                memo: Optional[dict] = None, click: bool = False) -> Dict[str, Any]:
    """`<Marshal>, march to <dest>` (and `then attack <enemy>` when named —
    the CR-7 arrival tail, paid once with the march).

    Row PW: on the CLICK road (`click=True`: a province clicked or dropped
    on, a row of the province panel) a destination the plain move takes is
    quoted as the MOVE (`move_quote`). A reader of a TYPED march — the
    readback under the line, Berthier's "what if he marches to …", a group's
    march, the army's — asks about the march and is answered about the march
    (the typed verbs mean what they always meant). Every quote carries
    `ground` and `confirm`."""
    if click and not then_attack:
        moved = move_quote(world, marshal, dest, memo=memo)
        if moved is not None:
            return _with_ground(world, marshal, moved)
    return _with_ground(world, marshal, _march_quote(world, marshal, dest,
                                                     then_attack=then_attack, memo=memo))


def _march_quote(world, marshal, dest: str, *, then_attack: str = "",
                 memo: Optional[dict] = None) -> Dict[str, Any]:
    """The march itself (CC-2), as it stood before row PW."""
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
    # Row PW: the provinces the plain move takes are in reach at the MOVE's
    # price ("ap", "kind" on their rows) — also when the march itself is
    # refused (one action left buys a move next door, never a march).
    moves = _moves_in_reach(world, marshal)
    # Each row carries its tag's lines (`tag_lines` — what the order does to
    # the province, what the march costs in men), so the tag by the cursor is
    # whole the moment the cursor rests, before any quote is fetched: a click
    # that sends at once must never outrun what it costs.
    move_rows = {dest: {"turns": 0, "road": list(q["road"]), "ap": int(q["ap"]),
                        "kind": "move",
                        "tag": list(_with_ground(world, marshal, q).get("tag") or [])}
                 for dest, q in moves.items()}
    if state:
        if move_rows:
            out["ok"] = True
            out["reach"] = move_rows
            out["march_refusal"] = state
            return out
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
    tag_cache: dict = {}
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
        planned = list(road)
        if dest in detours:
            road = detours[dest]   # CC-X14: a literal man goes round
            if not road:
                continue           # no road round him: the march is refused
        reach[dest] = {"turns": int(road_law.march_turns(len(road), reach_range)),
                       "road": list(road)}
        if dest not in move_rows:
            reach[dest]["tag"] = _reach_tag(world, marshal, dest, planned, list(road), tag_cache)
            if dest not in detours and tag_cache.get(("first", planned[0])) is not None:
                # The first step meets a corps we see: 1 action now, whatever
                # the march's price (`_standing_quote`'s contact arm).
                reach[dest]["ap"] = 1
    reach.update(move_rows)   # row PW: a move within reach is the move
    out["ok"] = True
    out["reach"] = reach
    return out


def _reach_tag(world, marshal, dest: str, planned: List[str], road: List[str],
               cache: dict) -> List[str]:
    """`tag_lines` for a MARCH row of the reach, from the light readers — the
    corps we see in the road's first province (`planned`: the road before a
    literal man's detour) or within a cavalryman's reach, else the ground's
    line; then the first march's cost in men. Pinned equal to the exact
    quote's `tag` for every province of the reach (`tests/test_pw_plain_words`).
    `cache` holds what many destinations share (the first step, the walk)."""
    from backend.commands import ground
    if not ground.the_ground_is_read_before_the_order():
        return []
    player = world.player_nation
    lines: List[str] = []
    first_key = ("first", planned[0] if planned else "")
    if first_key not in cache:
        cache[first_key] = visible_foe_on_road(world, player, planned[:1])
    contact = cache[first_key]
    if contact is not None:
        name = humanize_entity_name(contact[0].name)
        lines.append(f"{name} holds {contact[1]}" if contact[1] == dest
                     else f"{name} blocks the road at {contact[1]}")
    else:
        reach = max(1, int(getattr(marshal, "movement_range", 1) or 1))
        halt = visible_foe_on_road(world, player, road[1:reach]) if reach > 1 else None
        if halt is not None:
            lines.append(f"{humanize_entity_name(halt[0].name)} stands at {halt[1]}")
        else:
            try:
                said = str(ground.entering(world, marshal, dest).get("line") or "")
            except Exception as exc:
                report(exc, "order_quotes._reach_tag: ground.entering")
                said = ""
            if said:
                lines.append(said)
    reach_n = max(1, int(getattr(marshal, "movement_range", 1) or 1))
    walk_key = ("walk", tuple(road[:reach_n]))
    if walk_key not in cache:
        walked = _first_march(world, marshal, {"road": road})
        cache[walk_key] = _men_clause(*march_cost_reading(world, marshal, walked))
    if cache[walk_key]:
        lines.append(cache[walk_key])
    return lines


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
    # BA2-X10: `plot_route`'s own gate — a road round keeps to open frontiers,
    # so the lawful rung stands alone and no terrain-only rung follows it.
    from backend.commands import strategic as road_law
    lawful_only = road_law.a_road_round_keeps_to_open_frontiers()
    rungs = [world.weighted_paths_from(here, avoid_regions=seen,
                                       passable_for=mover if lawful_only else pf,
                                       mover_nation=mover)]
    if pf and not lawful_only:
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


def _the_days_word(world, marshal_name: str, action: str, target: str,
                   strategic_type: str = "") -> Optional[dict]:
    """BA3-X5 (row BA, BA-4): the ONE source of a word's price for every
    quote — `battle_day.quoted_word`, which is `classify_word`'s own verdict
    for the order the quote names. None: an ordinary order."""
    from backend.game_logic import battle_day as _day
    try:
        return _day.quoted_word(world, marshal_name, action, target, strategic_type)
    except Exception as exc:
        report(exc, "order_quotes._the_days_word: battle_day.quoted_word")
        return None


def _price_in_points(q: Dict[str, Any], word: dict) -> None:
    """A quote that is a word of an open day: no action, its price in the
    day's points — `points`, `word` (the kind) and `price` (the sentence) are
    on the quote ONLY then, so every other quote is as it was."""
    from backend.game_logic import battle_day as _day
    q["ap"] = 0
    q["points"] = int(word.get("price", 0) or 0)
    q["word"] = str(word.get("kind") or "")
    q["price"] = _day.price_line(word)
    if q.get("contact"):
        # "(1 action now)" was the contact arm's price; a word's is the day's.
        q["contact"] = str(q["contact"]).replace("(1 action now)", f"({q['price']})")


def _a_word_of_the_day(q: Dict[str, Any], word) -> Dict[str, Any]:
    """BA3-X5: a SUPPORT order for the lead of an open day is the day's
    "a corps is brought up" — a point, never an action. The quote (and the
    plan's `bring` row, which is this quote) says so."""
    if word is not None and q.get("ok") and not q.get("already"):
        _price_in_points(q, word)
    return q


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
    word = _the_days_word(world, marshal.name, "support", ally.name, "SUPPORT")
    return _a_word_of_the_day(_standing_quote(
        world, marshal, ally.location, "SUPPORT", ally.name, "support", q, memo,
        standing_follow=False, word=word), word)


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
    word = _the_days_word(world, marshal.name, "support", ally.name, "SUPPORT")
    return _a_word_of_the_day(_standing_quote(
        world, marshal, ally.location, "SUPPORT", ally.name, "follow", q, memo,
        standing_follow=True, word=word), word)


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
                      "guard": mq["guard"], "front": mq["front"],
                      # BA2-X21: the men its first march costs, on its row too.
                      "march_cost": mq.get("march_cost", "")})
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


def a_cards_men_are_men_in_reach() -> bool:
    """Row BA, session BA-6 seam (BA5-X17, found by BA-5's third blind
    reading): the figure a press card - and the attack card's force bar -
    gives as OURS is the men in reach (the lead and the corps that would
    answer the guns), never the muster's effective weight. Down (False): the
    weight, as before ("105,039 on 30,557" with 94,512 on the field)."""
    return True


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
        weight = int(marshal.strength) + int(float(odds.get("committed_attacker", 0.0) or 0.0))
        ours = weight
        if a_cards_men_are_men_in_reach():
            # BA5-X17: the muster's committed term is an arrival-weighted,
            # morale- and temper-scaled WEIGHT; printed beside the foe's true
            # men it read "105,039 on 30,557" with 94,512 on the field. The
            # card's figure is men in reach - the lead and the corps that
            # would answer the guns - as men; the odds word stays the muster's
            # and the great-battle forecast keeps reading the weight.
            joining = [world.marshals.get(n) for n in (odds.get("joining") or [])]
            ours = int(marshal.strength) + sum(
                int(m.strength) for m in joining if m is not None and int(m.strength) > 0)
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
        from backend.display_names import odds_plain
        return {"ours": ours, "ours_weight": int(weight), "theirs_low": int(low),
                "theirs_high": int(high), "theirs_label": label, "odds": word,
                # Row PW: the band word said as what to expect ("" with no word).
                "expect": odds_plain(word),
                # Row MC: the corps the muster says would answer the guns, by
                # name - the court line reads who would serve under the lead.
                "joining": [str(n) for n in (odds.get("joining") or [])]}
    except Exception as exc:
        report(exc, "order_quotes._force_block: muster_odds / _fog_banded_strength")
        return None


def attack_quote(world, marshal, enemy, *, memo: Optional[dict] = None) -> Dict[str, Any]:
    """An attack on a sighted enemy: `attack <enemy>` when he stands within
    the marshal's reach (the attack's own range rule — distance against
    `movement_range`), else the march that carries the attack there."""
    distance = world.get_distance(marshal.location, enemy.location)
    if distance is None or distance < 0 or distance > int(getattr(marshal, "movement_range", 1) or 1):
        return march_quote(world, marshal, enemy.location, then_attack=enemy.name, memo=memo)
    shown_enemy = humanize_entity_name(enemy.name)
    q = _blank("attack", marshal, enemy.location,
               f"{humanize_entity_name(marshal.name)}, attack {shown_enemy}")
    # BA3-X5: an attack on the enemy of an open day is a WORD of that day — it
    # costs the day's points and no action, and the quote says so.
    word = _the_days_word(world, marshal.name, "attack", enemy.name)
    state = _state_refusal(world, marshal, "attack", word)
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
    if word is not None:
        ap = 0
        _price_in_points(q, word)
    q.update(ok=True, ap=ap, turns=0, road=[enemy.location],
             objection=_tactical_objection(world, marshal, "attack", enemy.name),
             muster=_muster_line(world, marshal, enemy),
             alarm=_alarm_line(world, marshal, enemy),
             bring=bring_quotes(world, marshal, enemy, memo=memo, attack_ap=ap))
    force = _force_block(world, marshal, enemy)
    if force is not None:
        q["force"] = force
        # Row MC: the court beforehand - a senior who will resent serving
        # under the lead, a hostile or devoted marshal among the corps that
        # would answer the guns (`precedence.order_card_line`).
        from backend.game_logic import precedence as _court
        court = _court.order_card_line(
            world, marshal, [world.marshals.get(n) for n in force.get("joining") or ()])
        if court:
            q["note"] = " · ".join(part for part in (str(q.get("note") or ""), court) if part)
        # Row BA (BA-3): the attack card says beforehand when the battle it
        # opens would be a great one and the points its commander brings —
        # read off the force bar's own figures (his LEAST strength under fog:
        # "great" is never promised on men we cannot see).
        from backend.game_logic import battle_day as _day
        great = _day.forecast(world, marshal,
                              int(force.get("ours_weight", force["ours"])) + int(force["theirs_low"]),
                              foe=enemy)
        # No forecast while the day against him is ALREADY open: the card said
        # "A great battle — Ney commands the day: 2 points" over a day whose
        # purse stood at one (the day's own block tells it, on the table and
        # at the head of the province's panel).
        if great is not None and _day.day_against(world, enemy.name) is None:
            held = _day.the_day_he_holds(world, marshal.name)
            if held is None:
                q["day"] = great
            else:
                # The session's review (lane 3): one day a lead — the card
                # says what the rule will do with a second battle of his.
                said = (f"{q['shown']}'s day against "
                        f"{humanize_entity_name(str(held.get('enemy') or ''))} is still open — "
                        f"a battle here would be a single clash, with no day of its own.")
                if _day.a_lead_holds_his_day_as_the_battle_began():
                    # BA5-X1 (ruling 9's card, pressed): and what winning it
                    # does to the day he holds — he advances, and has left it
                    said += " Should he win it and advance, that day ends where it stands."
                q["note"] = " · ".join(part for part in (str(q.get("note") or ""), said) if part)
    # Row PW: the map tag's line under "Attack <him>" — what to expect.
    q["tag"] = tag_lines(world, marshal, q)
    return q


# The muster's reasons a WRITTEN ORDER answers — the three its own hint names
# (`combat_executor.muster_row_hint`): the literal man who awaits orders, the
# eye on a crown, the corps holding a position.
BROUGHT_BY_AN_ORDER = ("literal_awaits_orders", "eyes_on_a_crown", "holding_position")
# A corps that would come anyway is offered the order only when it lifts his
# odds by this much — the muster's own bar for naming the lever
# (`CombatExecutor._arrival_odds_row`).
BRING_ODDS_GAIN = 15


def _first_march(world, marshal, q: Dict[str, Any]) -> List[str]:
    """The provinces a standing order's FIRST march walks this turn — the
    order is taken and he sets off at once (`_strategic_first_step`): as far
    along the quote's road as he ranges, short of a corps we see on it (one in
    the road's first province meets the order where he stands) and short of a
    frontier he may not cross — the move's own rule, `can_enter_territory`
    (BA2-X10). [] when the first step is no march. An unseen corps is a
    surprise no quote may name."""
    from backend.game_logic.diplomacy import can_enter_territory
    walked: List[str] = []
    here = marshal.location
    reach = max(1, int(getattr(marshal, "movement_range", 1) or 1))
    for province in list(q.get("road") or [])[:reach]:
        if visible_foe_on_road(world, world.player_nation, [province]) is not None:
            break
        region = world.get_region(province)
        holder = getattr(region, "controller", None) if region is not None else None
        if holder and holder != marshal.nation and not can_enter_territory(
                world, marshal.nation, holder, mover_location=here):
            break
        walked.append(province)
        here = province
    return walked


def _stop_this_turn(world, marshal, q: Dict[str, Any]) -> str:
    """Where a standing order's FIRST march leaves him this turn
    (`_first_march`'s last province) — his own province when it walks none: a
    literal man's road ROUND a corps could be plotted through a neutral's shut
    frontier, that march is refused and he stands where he was (BA2-X10)."""
    walked = _first_march(world, marshal, q)
    return walked[-1] if walked else marshal.location


def march_cost_line(world, marshal, walked: List[str], *, first: bool = True) -> str:
    """BA2-X21 (row BA, BA-4): what the first march costs in MEN, said before
    the order is given. A standing order's first march is taken the moment the
    order is — Soult, 30,000 strong, ordered from Swabia over the mountain
    road to Munich, lost 1,800 men and read it in the order's reply, after the
    action was spent. The quote named the price in actions, the road, the
    detour, the guard, the pay — and not the men.

    The march rule is exact (`movement_executor.march_attrition_reading`, the
    very function the mover applies), walked one province at a time on a copy
    of the corps, as the first step walks them. Exact on our own, an ally's
    and a neutral's ground. A stop held by a court AT WAR with the marcher is
    told as "about N men, more if its works harass him": the march there may
    take the province (the rule then reads our own new soil) and an enemy's
    fort or detachment adds its toll — which the quote may not name without
    showing works the fog hides. "" when the march costs nothing."""
    lost, unsure = march_cost_reading(world, marshal, walked)
    # Row PW: a plain move is the whole march, not the first of several.
    the_march = "The first march" if first else "The march"
    if unsure:
        return (f"{the_march} costs about {lost:,} men, more if {unsure}'s works harass him."
                if lost > 0 else
                f"{the_march} is onto {unsure}: its works may harass him.")
    return f"{the_march} costs {lost:,} men." if lost > 0 else ""


def march_cost_reading(world, marshal, walked: List[str]) -> Tuple[int, str]:
    """`march_cost_line`'s two facts: the men the walk costs (the march rule,
    read one province at a time on a copy of the corps) and the hostile
    province whose works may add to it ("" for none). (0, "") for no walk."""
    if not walked:
        return 0, ""
    import copy
    from backend.commands.movement_executor import march_attrition_reading
    ghost = copy.copy(marshal)
    lost, unsure = 0, ""
    for province in walked:
        region = world.get_region(province)
        holder = getattr(region, "controller", None) if region is not None else None
        hostile = bool(holder and holder != marshal.nation
                       and world.is_at_war(marshal.nation, holder))
        reading = march_attrition_reading(world, ghost, province)
        step = int(reading["march_losses"] if hostile else reading["total_losses"])
        if hostile:
            unsure = province
        lost += step
        ghost.strength = max(0, int(ghost.strength) - step)
    return int(lost), unsure


def tag_lines(world, marshal, q: Dict[str, Any]) -> List[str]:
    """Row PW "Plain Words": the lines UNDER an order's tag on the map — what
    the player must know before a click that sends at once, each short enough
    for a badge at the head of the road:

    * what happens FIRST — a corps we see in the road (the quote's `contact`,
      its own first clause), else what the order does to the province it ends
      in (`ground.entering`'s line: "takes the province", "enters only — a
      garrison of 12,500 holds it");
    * what the march costs in MEN this turn (`march_cost_reading`, the mover's
      own rule) — a move next door through the mountains cost Massena 2,520
      of 42,000, read until now only in the reply;
    * for an attack, what to expect of the odds (`display_names.odds_plain`,
      on an exact sighting only — the force bar's own fog rule).

    [] for an order that is refused or already stands. The reach's rows carry
    the same lines for a province (`_reach_tag`), pinned equal."""
    if not q.get("ok") or q.get("already"):
        return []
    kind = str(q.get("kind") or "")
    if kind == "attack":
        from backend.display_names import odds_plain
        expect = odds_plain((q.get("force") or {}).get("odds"))
        return [expect] if expect else []
    lines: List[str] = []
    contact = str(q.get("contact") or "").strip()
    reading = q.get("ground") or {}
    if contact:
        lines.append(contact.split(" — ")[0])
    elif reading.get("line"):
        lines.append(str(reading["line"]))
    if kind in ("move", "march", "march_attack", "support", "follow"):
        walked = (list(q.get("road") or []) if kind == "move"
                  else _first_march(world, marshal, q))
        men = _men_clause(*march_cost_reading(world, marshal, walked))
        if men:
            lines.append(men)
    return lines


def _men_clause(lost: int, unsure: str) -> str:
    if lost <= 0:
        return ""
    return (f"about {lost:,} men lost on the march" if unsure
            else f"{lost:,} men lost on the march")


def _first_step_asks(world, q: Dict[str, Any], dest: str, ally=None) -> bool:
    """A corps we SEE in the road's first province, and that province not the
    friend's own: the order's first step is then no march — the aggressive man
    fights at once if the numbers favour him, every other asks the Emperor's
    orders (`_contact_line`'s personality arms; a literal man's quote already
    carries his road ROUND the foe). Of the question's four answers one keeps
    the order ("Go Around"), one sends him in alone and two abandon it, the
    action spent: an order that asks is not an order that brings.

    Row BA, BA-4 (the approach rule): never where the SUPPORT order's approach
    arm takes the step (`ally` in hand) — the corps the friend can strike bars
    the road, the order halts before it and asks nothing: it BRINGS him."""
    first = list(q.get("road") or [])[:1]
    if not (first and first[0] != dest
            and visible_foe_on_road(world, world.player_nation, first) is not None):
        return False
    return not (ally is not None and _halts_at_the_approach(world, ally, first[0], dest))


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


def what_the_order_delivers(world, lead, m, battle_region: str, beside, reader,
                            will_join: bool, odds_now: int, *,
                            memo: Optional[dict] = None) -> Dict[str, Any]:
    """BA2-X7 (row BA, BA-4): what `'<m>, support <lead>'` DELIVERS to a battle
    at `battle_region` — the ONE reading the plan's chips (`bring_quotes`) and
    the muster's two lever sentences (`combat_executor.muster_row_hint`,
    `_arrival_odds_row`) share, so Berthier never again names an order the
    chips will not offer. Read from where the order's first march LEAVES the
    corps, never from where he stands.

    → ``{quote, brings, odds_with, stop, why_not}``: `brings` is True when the
    order is taken without a question, leaves him on the field or beside it
    with odds above nothing and — for a man who would come anyway — at least
    `BRING_ODDS_GAIN` better than now; `why_not` says which test failed
    (`refused`, `already`, `asks`, `asks_first`, `marches_away`, `no_odds`,
    `no_gain`). The order's PRICE is not weighed here (the chips weigh it:
    BA2-X8). PURE; it never builds the muster preview."""
    q = support_quote(world, m, lead, memo=memo)
    out: Dict[str, Any] = {"quote": q, "brings": False, "odds_with": -1,
                           "stop": m.location, "why_not": ""}
    if not q["ok"]:
        out["why_not"] = "refused"
        return out
    if q["already"]:
        out["why_not"] = "already"
        return out
    if _first_step_asks(world, q, lead.location, ally=lead):
        out["why_not"] = "asks"           # the order would raise his question, or his own fight
        return out
    if q.get("detour") or q.get("guard"):
        out["why_not"] = "asks_first"     # the order would ask the Emperor first (BA2-X9)
        return out
    stop = out["stop"] = _stop_this_turn(world, m, q)
    if stop != battle_region and stop not in beside:
        out["why_not"] = "marches_away"   # the order's first march takes him out of reach
        return out
    odds_with = out["odds_with"] = 100 if stop == battle_region else _odds_under_the_order(
        reader, lead, m, stop, battle_region, world)
    if odds_with <= 0:
        out["why_not"] = "no_odds"
    elif will_join and odds_with < odds_now + BRING_ODDS_GAIN:
        out["why_not"] = "no_gain"
    else:
        out["brings"] = True
    return out


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
        reader = _MUSTER_READER.get("combat")
        if reader is None:
            from backend.commands.executor import CommandExecutor
            reader = _MUSTER_READER["combat"] = CommandExecutor()._combat
        battle_region = answering_defender(world, enemy).location
        if attack_ap is None:
            # the attack's own price: nothing for a counter-punch, and nothing
            # where the attack is a word of an open day (BA3-X5)
            attack_ap = 0 if (getattr(lead, "has_counter_punch", lambda: False)()
                              or _the_days_word(world, lead.name, "attack", enemy.name) is not None) \
                else int(world.get_action_cost("attack"))
        actions_left = int(getattr(world, "actions_remaining", 0) or 0)
        region = world.get_region(battle_region)
        beside = set(region.adjacent_regions) if region is not None else set()
        for m in _field_marshals(world):
            q = _bring_row(world, lead, m, battle_region, beside, reader, memo=memo)
            if q is None:
                continue
            if q["ok"] and actions_left < int(attack_ap) + int(q.get("ap") or 0):
                continue          # its price is the action the attack needs (BA2-X8)
            out.append(q)
    except Exception as exc:
        report(exc, "order_quotes.bring_quotes: the muster ladder")
        return []
    return sorted(out, key=_sort_key)


def _bring_row(world, lead, m, battle_region: str, beside, reader, *,
               memo: Optional[dict] = None) -> Optional[Dict[str, Any]]:
    """ONE corps' row of the plan (`bring_quotes`), or None: he stands on the
    field or beside it, the muster says he will not come or may not, and the
    order the game already has would bring him (`what_the_order_delivers`). A
    row whose order would be REFUSED is still a row (`ok` False, its refusal
    on it — the chip is shown dimmed). The order's price is the caller's to
    weigh. The ONE reading the plan's chips and the day's taker share
    (`the_order_brings`)."""
    from backend.display_names import MUSTER_REASON_DISPLAY
    if m.name == lead.name:
        return None
    if m.location != battle_region and m.location not in beside:
        return None
    will_join, code = reader._muster_reason(m, lead, battle_region, lead.nation, world)
    odds_now = -1
    if will_join:
        if code == "has_support_order" or m.location == battle_region:
            return None
        odds_now = int(reader._arrival_odds_row(
            lead, m, battle_region, world, code).get("arrival_odds", 0))
    elif code not in BROUGHT_BY_AN_ORDER:
        return None
    # BA2-X7: the one reading the muster's lever sentences share.
    delivered = what_the_order_delivers(world, lead, m, battle_region, beside, reader,
                                        bool(will_join), odds_now, memo=memo)
    q = delivered["quote"]
    odds_with = -1
    if q["ok"]:
        if not delivered["brings"]:
            return None           # asks, marches him out of reach, or gains nothing
        odds_with = int(delivered["odds_with"])
    if will_join:
        why = f"about {odds_now}% to make it in time"
    else:
        why = str(MUSTER_REASON_DISPLAY.get(code, "") or "will not march unordered")
    if odds_with >= 0:
        why += f"; about {odds_with}% under a written order"
    q.update(why=why, code=str(code), odds_now=odds_now, odds_with=odds_with)
    return q


def the_order_brings(world, lead, enemy, m) -> bool:
    """Row BA, BA-4 (the sibling of BA2-X7 on the day's own door): would
    `'<m>, support <lead>'` bring `m` to `lead`'s battle with `enemy` — is it
    the order the plan's "Bring up" chip offers? `_bring_row`'s own verdict,
    for the day's taker (`battle_day.classify_word`): the day takes as "a
    corps is brought up" exactly the order its table offers. PURE."""
    try:
        from backend.commands.combat_executor import answering_defender
        reader = _MUSTER_READER.get("combat")
        if reader is None:
            from backend.commands.executor import CommandExecutor
            reader = _MUSTER_READER["combat"] = CommandExecutor()._combat
        battle_region = answering_defender(world, enemy).location
        region = world.get_region(battle_region)
        beside = set(region.adjacent_regions) if region is not None else set()
        row = _bring_row(world, lead, m, battle_region, beside, reader)
        return bool(row is not None and row.get("ok") and row.get("command"))
    except Exception as exc:
        report(exc, "order_quotes.the_order_brings: the muster ladder")
        return False


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


# ═══════════════════════════════════════════════════════════════════════════
# Row IC, Session 2 (IC-7) — A BUTTON FOR EVERY SIMPLE ORDER: the choices
# BESIDE the one a card quotes.
#
# The card that opens on an enemy quoted the attack and nothing else: a
# pursuit, the guns' bombardment, a horseman's charge and an attack held back
# from it could only be typed. The card that opens on a province quoted the
# march: what he does on arrival could only be typed. A province gave no way
# to say "look into it". These are the rows of those buttons. Each row is the
# order's own LINE read through the read-back's reader (`read` — the route
# hands in `parse_preview.read_one`), so a button is priced, greyed and
# worded exactly as the typed line would be, and what it sends is that line.
# PURE: a reading spends nothing.
# ═══════════════════════════════════════════════════════════════════════════
ENEMY_ALTS = (
    # (id, the button's words, the verb its line gives)
    ("pursue", "Chase him", "pursue"),
    ("bombard", "Bombard", "bombard"),
    ("charge", "Charge him", "charge"),
    ("held_back", "Attack, held back", "attack"),
)
MARCH_THENS = (
    ("hold", "then hold"), ("fortify", "then dig in"), ("drill", "then drill"),
    ("defend", "then stand"),
)
LOOK_ROWS_MAX = 4
# A locked choice's reason, in the plainest words, where the read-back's own
# are short for a line being typed and read as a riddle on a card (the blind
# reading, three readers of three: "one victory as the attacker arms the
# charge"). The read-back's words are older rows' and stay as they are.
PLAIN_REFUSALS = {
    "one victory as the attacker arms the charge": "he needs one victory as the attacker first",
}


def _alt_row(key: str, label: str, command: str, read) -> Dict[str, Any]:
    """One alternative as the read-back reads its line: ``{id, label, command,
    ok, ap, turns, refusal, note}`` — `refusal` the SHORT reason when the
    line would be refused (the marshal's own name taken off its head)."""
    reading = read(command) or {}
    parts = [p for p in (reading.get("parts") or []) if isinstance(p, dict)]
    ok = reading.get("kind") == "order" and bool(reading.get("ok"))
    refusal = ""
    if not ok:
        refusal = str(reading.get("refusal") or "") or next(
            (str(p.get("text") or "") for p in parts if p.get("role") in ("bad", "head")), "")
        shown = str(reading.get("marshal") or "")
        for lead in ((shown + " — ", shown + " ") if shown else ()):
            if refusal.startswith(lead):
                refusal = refusal[len(lead):]
                break
        refusal = refusal.strip() or "the order would be refused"
        refusal = PLAIN_REFUSALS.get(refusal, refusal)
    notes = [str(p.get("text") or "") for p in parts if p.get("role") in ("warn", "taken")]
    return {"id": key, "label": label, "command": command, "ok": bool(ok),
            "ap": int(reading.get("ap", 0) or 0), "turns": int(reading.get("turns", 0) or 0),
            "refusal": refusal, "note": " · ".join(n for n in notes if n)}


def enemy_alts(world, marshal, enemy, read) -> List[Dict[str, Any]]:
    """The other simple orders against an enemy in sight: "Chase him" for any
    corps; "Bombard" for a gun corps; "Charge him" for horse; "Attack, held
    back" where his attack would ask "charge or restrain?" (a reckless
    horseman at `tactical_executor.RESTRAIN_AT`). A row that would be refused
    is kept, with its reason — a greyed button says why."""
    from backend.commands.tactical_executor import RESTRAIN_AT
    who = humanize_entity_name(marshal.name)
    foe = humanize_entity_name(enemy.name)
    rows = []
    for key, label, verb in ENEMY_ALTS:
        if key == "bombard" and not getattr(marshal, "artillery", False):
            continue
        if key == "charge" and not getattr(marshal, "cavalry", False):
            continue
        if key == "held_back" and not (
                getattr(marshal, "is_reckless_cavalry", False)
                and int(getattr(marshal, "recklessness", 0) or 0) == RESTRAIN_AT):
            continue
        if key == "held_back":
            from backend.commands.tactical_executor import restrain_refusal
            row = _alt_row(key, label, f"{who}, attack {foe}, held back", read)
            short = restrain_refusal(world, marshal, enemy.name)[1]
            if short and row["ok"]:
                row.update(ok=False, refusal=short)
            rows.append(row)
            continue
        rows.append(_alt_row(key, label, f"{who}, {verb} {foe}", read))
    return rows


def landing_alts(world, marshal, shore: str, read) -> List[Dict[str, Any]]:
    """Row FUN, FUN-1 (November 25, 2026): a march refused at a sea crossing
    offers the order that crosses it — a landing on the far `shore` by a corps
    the transports can lift (`naval.landing_corps_for`: the selected corps when
    he fits, else the largest that may sail), read by the typed-order reader so
    its price and any refusal are the order's own. The landing's own card then
    quotes the odds before anything sails. When no corps can go, his own
    landing stands DIMMED with why (`naval.landing_blocker_line`: the Emperor
    stays, too many men, or the nearest shore he can sail from) — a greyed
    button that says why, never a silent absence. [] when the shore takes no
    landing at all."""
    from backend.game_logic.naval import landing_blocker_line, landing_corps_for, landing_shore_ok
    if not landing_shore_ok(world, marshal.nation, shore):
        return []   # (the review, lane B: no fleet, no coast, or no consent — no landing to offer)
    names = landing_corps_for(world, marshal.nation, shore, prefer=marshal.name)
    place = humanize_entity_name(shore)
    if names:
        who = humanize_entity_name(names[0])
        # (the review, lane B: another corps than the one ordered says so)
        lead = "Land" if names[0] == marshal.name else "Instead, land"
        return [_alt_row("land", f"{lead} {who} in {place} by sea", f"land {who} in {place}", read)]
    why = landing_blocker_line(world, marshal)
    if not why:
        return []
    who = humanize_entity_name(marshal.name)
    return [{"id": "land", "label": f"Land {who} in {place} by sea", "command": f"land {who} in {place}",
             "ok": False, "ap": 0, "turns": 0, "refusal": why, "note": ""}]


def march_thens(world, marshal, dest: str, read) -> List[Dict[str, Any]]:
    """What he may do on arrival — today's four arrival verbs — each the
    march's own line with "then …" behind it, free with the march."""
    who = humanize_entity_name(marshal.name)
    place = humanize_entity_name(dest)
    return [_alt_row("then:" + verb, label, f"{who}, march to {place} then {verb}", read)
            for verb, label in MARCH_THENS]


def look_rows(world, region: str) -> List[Dict[str, Any]]:
    """Our field corps that can LOOK into `region` from where they stand —
    within `movement_executor.scout_range`, nearest first — each with the
    scout's price and the reason his state refuses it (`state_probe`, the
    executor's own gates). A corps standing IN the province has slot 4."""
    from backend.commands import state_probe as sp
    from backend.commands.movement_executor import scout_range
    rows = []
    place = humanize_entity_name(region)
    for marshal in world.get_field_marshals():
        if marshal.nation != world.player_nation or int(getattr(marshal, "strength", 0) or 0) <= 0:
            continue
        gap = world.get_distance(marshal.location, region)
        if not isinstance(gap, int) or gap < 1 or gap > int(scout_range(marshal)):
            continue
        shown = humanize_entity_name(marshal.name)
        refusal = sp.order_state_refusal(world, marshal, "scout")
        rows.append((gap, shown, {
            "marshal": marshal.name, "shown": shown, "command": f"{shown}, scout {place}",
            "label": f"{shown}: look at {place}", "ok": not refusal,
            "ap": int(sp.order_price(world, marshal, "scout")), "refusal": str(refusal or ""),
            "from": humanize_entity_name(marshal.location), "marches": int(gap)}))
    return [row for _gap, _shown, row in sorted(rows, key=lambda r: (r[0], r[1]))][:LOOK_ROWS_MAX]


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
    march = sorted((march_quote(world, m, region, memo=memo, click=True) for m in away), key=_sort_key)
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
    # Row PW: a corps of ours standing on ground that is not ours — why it is
    # not, and the order that takes it (`take_quote`), one row per corps here.
    take = []
    here_region = world.get_region(region)
    if (here_region is not None and here and here_region.controller
            and here_region.controller != player):
        from backend.commands import ground as _ground
        if _ground.the_ground_is_read_before_the_order():
            # only where there is something to say: ground we are at war
            # for, or ground a peace has just closed under him
            take = [q for q in (take_quote(world, m) for m in here)
                    if str((q.get("ground") or {}).get("code") or "") in _ground.SAID_ON_THE_PANEL]
    return {
        "success": True,
        "region": region,
        "ap_left": int(getattr(world, "actions_remaining", 0) or 0),
        "take": take,
        "march": march,
        "support": support,
        "follow": follow,
        # AO: the Staff's one order for the Emperor's column — quoted, or the
        # reason there is none today (a dimmed chip that teaches the reform).
        "army": army_quote(world, region, memo=memo),
        "attack": attack,
    }
