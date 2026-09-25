"""VP-M1 "The Fortunes of War" — the generals' mortality.

GE-D1 (`DESIGN_REFINEMENT.md`), RULED September 25, 2026 under the user's
delegated grant during GE-V ("make these decisions"): **(a) YES, bounded.**
A general has never had a personal death roll — he fell only when his
corps was ground below the 50-man rubble floor or his court was
eliminated (the memo `docs/audits/GENERALS_DEATH_ODDS_2026_09_25.md`: 884
battles, 11 field deaths, all of them remnants finished off). This module
is the one roll:

* **Who:** only the LEADING marshal of the LOSING side of a real battle
  (`battle_scale.is_a_battle`), whose corps lost at least `LOSS_SHARE` of
  what it brought. Winners and stalemates never roll. The sovereign never
  rolls here — GE-1's "The Eagle Falls" owns him at the removal seam.
* **The draw:** one deterministic draw through the campaign seed
  (`campaign_variance.seeded_int`, the `sovereign_death_roll` idiom — the
  historical seed still ROLLS; no module RNG is consumed, so M1–M7 and the
  test files that depend on the RNG's draw order are untouched):
  killed `KILLED_PCT`, wounded `WOUNDED_PCT`, in-band tunable.
* **A wound** puts him out `WOUND_TURNS` turns on ONE serialized field,
  `Marshal.wounded_until_turn`: his corps stays, defends and moves, but he
  cannot attack, charge, bombard, pursue or take a strategic order.
* **A death** keeps the corps: its men pass to the nearest friendly corps
  within three regions (the dismissal transfer) or disperse, and the
  tombstone cause is `killed_in_action` — through `WorldState.destroy_marshal`,
  the ONE removal seam, so the reward rows, the ask, the totals and the
  chronicle line all follow.
* **GR5:** one roll on both boards — an Austrian lead beaten by Ney rolls
  the same odds.

Expected per French campaign: about one wound and 0.13 deaths, which is
history's roughly 1.5% per marshal-year. `THE_GENERALS_ARE_MORTAL` is the
flip lever; `BASELINE_SERIES` was re-recorded once with it attributed.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

THE_GENERALS_ARE_MORTAL = True
KILLED_PCT = 1
WOUNDED_PCT = 8
WOUND_TURNS = 3
LOSS_SHARE = 0.25
CAUSE_KILLED = "killed_in_action"
TRANSFER_RANGE = 3


def is_wounded(marshal, world_or_turn) -> bool:
    """A man is wounded while the campaign turn has not reached the turn
    his wound heals. Reads the ONE field; never raises."""
    try:
        until = int(getattr(marshal, "wounded_until_turn", 0) or 0)
    except (TypeError, ValueError):
        return False
    if until <= 0:
        return False
    turn = world_or_turn
    if not isinstance(turn, int):
        turn = int(getattr(world_or_turn, "current_turn", 0) or 0)
    return turn < until


def wound_refusal(marshal, world, verb: str = "attack") -> Optional[str]:
    """The sentence the executor answers an order a wounded man cannot
    carry out, or None when he can."""
    if not is_wounded(marshal, world):
        return None
    until = int(getattr(marshal, "wounded_until_turn", 0) or 0)
    turn = int(getattr(world, "current_turn", 0) or 0)
    left = max(1, until - turn)
    from backend.display_names import plural
    return (f"{marshal.name} is WOUNDED and cannot {verb} — "
            f"{plural(left, 'turn')} until he is fit to lead again "
            f"(his corps stands, defends and marches).")


def losing_lead(battle_result: Dict[str, Any], attacker, defender):
    """(loser, winner, side) for a decided battle; (None, None, "") for a
    stalemate or a missing side."""
    if not isinstance(battle_result, dict) or attacker is None or defender is None:
        return None, None, ""
    if battle_result.get("attacker_won"):
        return defender, attacker, "defender"
    if battle_result.get("defender_won"):
        return attacker, defender, "attacker"
    return None, None, ""


def roll(world, battle_result: Dict[str, Any], attacker, defender, *,
         field: str = "") -> Optional[Dict[str, Any]]:
    """The one roll, at the post-battle seam both combat copies share
    (`_handle_forced_retreat`). Returns the outcome record — {"outcome":
    "wounded"|"killed", "marshal", "message", ...} — or None. Never raises
    (a roll is never a reason for a battle to fail)."""
    if not THE_GENERALS_ARE_MORTAL:
        return None
    try:
        loser, winner, side = losing_lead(battle_result, attacker, defender)
        if loser is None:
            return None
        if getattr(loser, "is_sovereign", False):
            return None
        marshals = getattr(world, "marshals", {}) or {}
        if marshals.get(loser.name) is not loser:
            return None
        if int(getattr(loser, "strength", 0) or 0) <= 0:
            return None
        if getattr(loser, "captured_by", ""):
            return None
        other = "attacker" if side == "defender" else "defender"
        lost = int((battle_result.get(side) or {}).get("casualties", 0) or 0)
        inflicted = int((battle_result.get(other) or {}).get("casualties", 0) or 0)
        from backend.game_logic import battle_scale
        if not battle_scale.is_a_battle(lost + inflicted):
            return None
        before = int(loser.strength) + lost
        if before <= 0 or lost < LOSS_SHARE * before:
            return None
        from backend.game_logic.campaign_variance import seeded_int
        seed = str(getattr(world, "campaign_seed", "historical") or "historical")
        turn = int(getattr(world, "current_turn", 0) or 0)
        nth = len(getattr(world, "battles_this_turn", []) or [])
        namespace = f"fortunes::{turn}::{loser.name}::{nth}"
        draw = seeded_int(seed, namespace, 0, 99)
        where = str(field or getattr(loser, "location", "") or "")
        if draw < int(KILLED_PCT):
            return _kill(world, loser, winner, where)
        if draw < int(KILLED_PCT) + int(WOUNDED_PCT):
            return _wound(world, loser, winner, where)
        return None
    except Exception:
        return None


def _wound(world, loser, winner, where: str) -> Dict[str, Any]:
    turn = int(getattr(world, "current_turn", 0) or 0)
    loser.wounded_until_turn = turn + int(WOUND_TURNS)
    victor = str(getattr(winner, "nation", "") or "")
    try:
        world.log_event({
            "type": "marshal_wounded",
            "marshal": loser.name,
            "nation": loser.nation,
            "location": where,
            "victor": victor,
            "until_turn": int(loser.wounded_until_turn),
            "turn": turn,
        })
    except Exception:
        pass
    message = (f"{loser.name} is WOUNDED at {where} — carried from the field, "
               f"out {int(WOUND_TURNS)} turns; his corps stands under its "
               f"colonels.")
    return {"outcome": "wounded", "marshal": loser.name, "message": message,
            "until_turn": int(loser.wounded_until_turn)}


def _kill(world, loser, winner, where: str) -> Dict[str, Any]:
    men = int(getattr(loser, "strength", 0) or 0)
    men_to = ""
    distance = 0
    try:
        found = world.find_nearest_marshal_within_range(
            from_location=str(getattr(loser, "location", "") or ""),
            nation=loser.nation, max_distance=int(TRANSFER_RANGE),
            exclude_marshal=loser.name)
    except Exception:
        found = None
    if found:
        nearest, distance = found
        try:
            nearest.add_troops(men)
            men_to = nearest.name
        except Exception:
            men_to = ""
    loser.strength = 0
    victor = str(getattr(winner, "nation", "") or "")
    removed = world.destroy_marshal(loser, cause=CAUSE_KILLED, victor=victor,
                                    location=where)
    stone = (getattr(world, "fallen_marshals", {}) or {}).get(loser.name)
    if isinstance(stone, dict):
        stone["men"] = int(men)
        stone["men_to"] = men_to
    if men_to:
        passage = (f"{men:,} men pass to {men_to}"
                   + (f", {distance} region{'s' if distance != 1 else ''} away" if distance else "")
                   + ".")
    else:
        passage = f"{men:,} men disperse — no corps of theirs within {TRANSFER_RANGE} regions."
    message = (f"{loser.name} is KILLED at {where} — struck down at the head "
               f"of his corps. {passage}")
    return {"outcome": "killed", "marshal": loser.name, "message": message,
            "removed": bool(removed), "men": men, "men_to": men_to}
