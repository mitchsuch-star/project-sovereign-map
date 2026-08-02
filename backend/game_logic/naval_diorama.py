"""NV-7 — THE NAVAL DIORAMA (DEF-5, docs/NAVAL_SPEC.md §10 row NV-D4,
re-opened and built at the August 2, 2026 user gate: "a battle screen like
for battles?").

A fleet action was, until now, one line of terminal text — which is a poor
fate for the only battle in this game that can end a war in an afternoon.
This builds the same tableau the land battles get (`battle_diorama.py`),
in the same payload shape, so the SAME scene renders it: contingents on a
baize, figures that fall, an odometer, a locket for the flag officer, a
verdict typed last.

The mapping is not a metaphor, it is the model:

  * A CONTINGENT is a pooled navy. §4.4's resolver already bleeds every
    fleet that pooled on a side (`_apply_side_losses` — the Combined Fleet
    bled together at Trafalgar, H6), so its own per-nation loss dict IS the
    order of battle. France and Spain stand side by side and strike
    together, which is the historical picture exactly.
  * COMMITTED is sail of the line, CASUALTIES are ships taken or sunk,
    REMAINING is what came home.
  * The ARM is `ship` — the fourth war-table piece, carved in the same
    timber as the other three.

Display-only (Golden Rule 6): every figure here is already on the fleet-
action event surface or derived from it, and nothing in this module is
read back by any rule.
"""
from typing import Dict, List, Optional

from backend.game_logic import naval

# A side's line is capped like the land tableau's, for the same reason.
MAX_SQUADRONS_PER_SIDE = 4

# Above this share of a squadron's sail lost, the piece topples: she was
# not merely mauled, she struck. Purely a rendering threshold.
STRUCK_LOSS_FRACTION = 0.34


def _squadron(nation: str, before: int, lost: int, lead: bool,
              admiral: str) -> dict:
    remaining = max(0, before - lost)
    if before <= 0:
        status = "failed_arrive"
    elif remaining <= 0:
        status = "destroyed"
    elif lost >= before * STRUCK_LOSS_FRACTION:
        status = "routed"          # struck her colours — the piece falls
    else:
        status = "engaged"
    entry = {
        "name": admiral or nation,
        "nation": nation,
        "arm": "ship",
        "committed": int(before),
        "casualties": int(max(0, lost)),
        "remaining": int(remaining),
        "status": status,
        "lead": bool(lead),
        "crowned": False,
    }
    return entry


def _side(world, principal: str, enemy: str, losses: Dict[str, int]) -> dict:
    """Every fleet that pooled on this side, the flag first. Ship counts are
    reconstructed as (live + lost), because the resolver has already applied
    the losses by the time this runs — the pre-battle line of battle is what
    the tableau must show."""
    # NV-9: seed from the LOSSES dict, which is §4.4's own record of who
    # bled on this side and is therefore the order of battle itself.
    # `iter_fleets` yields only ships > 0, so a squadron ANNIHILATED in
    # the action vanished from the line entirely — its dead uncounted,
    # `casualties_total` under the Admiralty's own figure on the same
    # screen. The pooled scan still runs, for a partner who fought and
    # lost nothing.
    members = [principal]
    for member in sorted(losses):
        if member != principal:
            members.append(member)
    members += sorted(
        partner for partner, _rec in naval.iter_fleets(world)
        if partner != principal and partner not in losses
        and naval._is_pooled_partner(world, principal, partner, enemy))
    contingents: List[dict] = []
    for member in members:
        rec = naval.get_fleet(world, member) or {}
        lost = int(losses.get(member, 0))
        before = int(rec.get("ships", 0) or 0) + lost
        if before <= 0:
            continue
        contingents.append(_squadron(
            member, before, lost, member == principal,
            str(rec.get("admiral", "") or "")))
    shown = contingents[:MAX_SQUADRONS_PER_SIDE]
    return {
        "nation": principal,
        "contingents": shown,
        "reserve_count": int(len(contingents) - len(shown)),
        "casualties_total": int(sum(c["casualties"] for c in contingents)),
        "committed_total": int(sum(c["committed"] for c in contingents)),
    }


def _observation(result: dict, player_side: Optional[str]) -> str:
    """The Admiralty's verdict, typed last like Berthier's. States what the
    action COST in the currency the player spends — hulls and the sea."""
    winner, loser = result["winner"], result["loser"]
    from backend.display_names import display_nation, nation_adjective
    w_lost = sum((result["losses"].get(winner) or {}).values())
    l_lost = sum((result["losses"].get(loser) or {}).values())
    if result["decisive"]:
        head = (f"{display_nation(winner)} holds the sea. The "
                f"{nation_adjective(loser)} line is broken and scattered")
    else:
        head = (f"{display_nation(winner)} has the better of it, but the "
                f"{nation_adjective(loser)} squadrons draw off in order")
    tail = f" — {l_lost} sail lost against {w_lost}."
    if player_side is None:
        return head + tail
    if (player_side == "winner"):
        return head + tail + " The seaways are ours to use."
    return head + tail + (
        " Until the fleet is rebuilt, our coasts and our crossings are at "
        "their pleasure.")


def build_naval_diorama(world, result: dict) -> Optional[dict]:
    """Assemble the payload for one §4.4 fleet action, or None when this
    world has no naval layer. Fog: fleet counts and postures are PUBLIC by
    the §9 recorded ruling (period newspapers printed orders of battle), so
    a third-party action is watchable — in the `observer` register."""
    if not naval.has_naval_layer(world) or not result:
        return None
    player = getattr(world, "player_nation", None)
    winner, loser = result["winner"], result["loser"]
    attacker, defender = result["attacker"], result["defender"]
    losses = result.get("losses") or {}

    player_side = None
    if player == attacker:
        player_side = "attacker"
    elif player == defender:
        player_side = "defender"

    if player_side is None:
        register = "observer"
    elif player == winner:
        register = "triumph"
    elif result["decisive"]:
        register = "defeat"
    else:
        register = "grim"

    attacker_side = _side(world, attacker, defender, losses.get(attacker) or {})
    defender_side = _side(world, defender, attacker, losses.get(defender) or {})

    # The land tableau reads `outcome` to decide who won; keep its grammar.
    outcome = ("attacker_victory" if winner == attacker
               else "defender_victory")

    from backend.display_names import display_nation
    return {
        "naval": True,
        "battle_name": _action_name(result),
        "region": "",
        "waters": str(result.get("battle_name", "")),
        "turn": int(getattr(world, "current_turn", 0)),
        "outcome": outcome,
        "victor": winner,
        "attacker_nation": attacker,
        "defender_nation": defender,
        "player_side": player_side,
        "register": register,
        "decisive": bool(result["decisive"]),
        # A fleet action is never routine: there are exactly two ways to
        # cause one (§4.4) and both are a player or an AI staking a
        # campaign on it. Both surfaces open.
        "significant": True,
        "dramatic": True,
        "great_battle": bool(result["decisive"]),
        "region_conquered": False,
        "attacker": attacker_side,
        "defender": defender_side,
        "observation": _observation(
            result,
            None if player_side is None else
            ("winner" if player == winner else "loser")),
        "context": str(result.get("context", "action")),
        "loser_admiral": str(result.get(
            "defender_admiral" if loser == defender else "attacker_admiral", "")),
        "winner_admiral": str(result.get(
            "attacker_admiral" if winner == attacker else "defender_admiral", "")),
        "_display_winner": display_nation(winner),
    }


def _action_name(result: dict) -> str:
    """The plate. The WATERS ride the subtitle (there are no sea zones on
    this map — §4.4 names an action by its combatants), so the name itself
    must not repeat them: "The Great Fleet Action — the France–Britain
    action" said "action" twice."""
    return "The Great Fleet Action" if result["decisive"] else "A Fleet Action"
