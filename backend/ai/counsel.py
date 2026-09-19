"""CX-2 — "WHAT CAN I DO", the one board-derived source for counsel.

WHY THIS MODULE EXISTS
======================
Three surfaces answer the question *"what can I do right now?"* and each
answered it from its own hardcoded list:

* **The Berthier shrug** (`llm_client._berthier_mock_response`) — what the
  player reads at the exact moment the parser has failed them. Its third
  template hardcodes ``'declare war on Prussia'`` and ``'propose peace with
  Austria'``, by name. On the shipped 1805 boot **France is at PEACE with
  Prussia**, so the game's recovery advice is an act of war against a
  neutral — fifty-two lines below `_hostile_first`, the guard added by
  FA-80(c) to stop precisely that for the ATTACK templates and never
  extended to the diplomatic ones. And both sentences name a road the
  shipped client *redirects*: `main.gd::_redirect_diplomatic_command`
  intercepts the whole diplomatic family (user ruling G1), so the recovery
  text teaches a sentence that cannot be sent.
* **The COMMAND REFERENCE** — 12,717 characters with no world-derived
  content at all (no ``{`` placeholder anywhere in its 216 lines). It is a
  manual, not an answer, and it is what ten of the twelve questions a player
  actually asks returned.
* **The region panel's chips** — which DO know the board, and which is why
  they win: *the chips are priced, and the typed verbs are blind.*

This module is the third one's knowledge, made available to the first two and
to the question desk, from the seams the mechanics themselves read — the move
refusal probe, the build gate, the levy pricer — so a quoted figure is the
applied figure and the two cannot drift.

FOG
===
Enemies come from `world.get_visible_enemies` (Golden Rule 5), never the
omniscient roster. Province NAMES are public — the map paints every one — so
a destination may be named; what is never named is who stands there.

GOLDEN RULE 8
=============
Every entry point here is reached by a TYPED QUESTION or by a parse failure,
never per-turn and never per-marshal in a loop, so the region walk it does is
not a hot path. It still uses the cached helpers where they exist.
"""
from __future__ import annotations

from typing import Dict, List, Optional

# Flip lever: False makes every function here return an empty list, and each
# consumer keeps the hardcoded copy it had before CX-2.
COUNSEL_IS_DERIVED_FROM_THE_BOARD = True

# The Cabinet is the door (user ruling G1): a diplomatic verb is never
# offered as a sentence to type, because the client redirects it. The counsel
# names the surface instead.
CABINET_LINE = "For any matter of state, press F1 for the Cabinet."


def _display(name: str) -> str:
    from backend.display_names import humanize_entity_name
    return humanize_entity_name(name)


def _is_free_to_order(marshal) -> bool:
    """A corps that can receive an order at all — the states the executor
    refuses outright, read from the marshal rather than re-derived."""
    if marshal is None or int(getattr(marshal, "strength", 0) or 0) <= 0:
        return False
    if getattr(marshal, "captured_by", None):
        return False
    if getattr(marshal, "is_drilling", False):
        return False
    if getattr(marshal, "administrative", False):
        return False
    return True


def _visible_enemy_map(world, nation: str) -> Dict[str, List]:
    """region -> [visible enemy marshals]. Fog-honest by construction."""
    out: Dict[str, List] = {}
    try:
        for enemy in world.get_visible_enemies(nation):
            if int(getattr(enemy, "strength", 0) or 0) <= 0:
                continue
            out.setdefault(enemy.location, []).append(enemy)
    except Exception:
        return {}
    return out


def _at_war_with(world, nation: str, other: str) -> bool:
    try:
        return bool(world.is_at_war(nation, other))
    except Exception:
        return False


def military_counsel(world, nation: str, limit: int = 4) -> List[str]:
    """Typed orders for the army that are legal RIGHT NOW, most useful first.

    Ordered attack → move → fortify/unfortify → drill, because that is the
    order a player needs them in when they are stuck: the thing that wins the
    turn first, the thing that fills it last.
    """
    if not COUNSEL_IS_DERIVED_FROM_THE_BOARD or world is None:
        return []
    lines: List[str] = []
    seen_verbs = set()
    try:
        marshals = [m for m in world.get_player_marshals() if _is_free_to_order(m)]
    except Exception:
        return []
    enemies_here = _visible_enemy_map(world, nation)

    # 1. A battle the player can actually fight — co-located first, then
    #    adjacent, and only against a court we are AT WAR with (FA-80(c)'s
    #    rule, which the diplomatic templates never inherited).
    #
    #    ⚠ The at-war test is REDUNDANT TODAY and is kept deliberately.
    #    `get_visible_enemies` reads `get_enemies_of_nation`, which is
    #    already at-war scoped, so a court at peace cannot reach this loop
    #    through it — measured, and the mutation sweep found the first pin on
    #    this line INERT for exactly that reason. It stays because what this
    #    function produces is a target the player is TOLD to attack, and the
    #    cost of an upstream widening is the game proposing a war on a
    #    neutral. It is pinned at the function instead of at the board.
    for marshal in marshals:
        for enemy in enemies_here.get(marshal.location, []):
            if _at_war_with(world, nation, getattr(enemy, "nation", "")):
                lines.append(f"{_display(marshal.name)}, attack "
                             f"{_display(enemy.name)}")
                seen_verbs.add("attack")
                break
        if "attack" in seen_verbs:
            break
    if "attack" not in seen_verbs:
        for marshal in marshals:
            region = world.get_region(marshal.location)
            for neighbour in (getattr(region, "adjacent_regions", None) or []):
                hostile = [e for e in enemies_here.get(neighbour, [])
                           if _at_war_with(world, nation, getattr(e, "nation", ""))]
                if hostile:
                    lines.append(f"{_display(marshal.name)}, attack "
                                 f"{_display(hostile[0].name)}")
                    seen_verbs.add("attack")
                    break
            if "attack" in seen_verbs:
                break

    # 2. A march the movement law would ALLOW — asked of the executor's own
    #    pure refusal probe, so the counsel can never propose a road the
    #    order would be refused on (the PF-4 idiom).
    for marshal in marshals:
        region = world.get_region(marshal.location)
        for neighbour in (getattr(region, "adjacent_regions", None) or [])[:8]:
            if _move_would_be_refused(world, marshal, neighbour):
                continue
            lines.append(f"{_display(marshal.name)}, march to {neighbour}")
            seen_verbs.add("move")
            break
        if "move" in seen_verbs:
            break

    # 3. The stance verbs, which are what an idle corps is actually for.
    for marshal in marshals:
        if getattr(marshal, "fortified", False):
            if "unfortify" not in seen_verbs:
                lines.append(f"{_display(marshal.name)}, unfortify")
                seen_verbs.add("unfortify")
        elif "fortify" not in seen_verbs:
            lines.append(f"{_display(marshal.name)}, fortify")
            seen_verbs.add("fortify")
        if len(lines) >= limit:
            break
    for marshal in marshals:
        if "drill" in seen_verbs or len(lines) >= limit:
            break
        if not getattr(marshal, "fortified", False):
            lines.append(f"{_display(marshal.name)}, drill")
            seen_verbs.add("drill")
    return lines[:limit]


def _move_would_be_refused(world, marshal, destination: str) -> bool:
    """True when `_execute_move` would refuse this step — asked of the ONE
    pure probe the objection battery already consults, never re-derived.

    Signature is `move_refusal_probe(world, marshal, target_region,
    target_name)` (a staticmethod); it returns the refusal dict or None.
    """
    try:
        from backend.commands.movement_executor import MovementExecutor
        region = world.get_region(destination)
        if region is None:
            return True
        return bool(MovementExecutor.move_refusal_probe(
            world, marshal, region, destination))
    except Exception:
        # The counsel must never break the surface that calls it; a probe we
        # cannot run means we do not offer the march.
        return True


def economy_counsel(world, nation: str, limit: int = 3) -> List[str]:
    """Typed economy orders that are legal now — AND PRICED.

    The price is the whole point. Every CLICK-WINS verdict in the row's
    two-road measurement was won on information rather than on clicks: the
    chip carries the levy's live price and the building's delivered yield and
    the typed verb carries nothing. These lines carry the same figures, read
    from the same pricers.
    """
    if not COUNSEL_IS_DERIVED_FROM_THE_BOARD or world is None:
        return []
    lines: List[str] = []
    levy = _levy_terms(world, nation)
    if levy:
        lines.append(levy)
    lines.extend(_build_terms(world, nation, limit=max(0, limit - len(lines))))
    return lines[:limit]


def _levy_terms(world, nation: str) -> Optional[str]:
    """`recruit infantry in <Region> — Ng for N men`, on a province where a
    corps of ours actually stands (which is the backend's own condition for
    pricing it)."""
    try:
        from backend.game_logic.ledger import _build_economy
        levy = (_build_economy(world, nation) or {}).get("levy") or {}
    except Exception:
        return None
    if not levy.get("recipient_in_range"):
        return None
    region = levy.get("region") or _first_own_region_with_a_corps(world, nation)
    if not region:
        return None
    price = int(levy.get("infantry_price") or 0)
    amount = int(levy.get("infantry_amount") or 0)
    if not price or not amount:
        return f"recruit infantry in {region}"
    return (f"recruit infantry in {region} — {price:,}g for "
            f"{amount:,} men")


def _first_own_region_with_a_corps(world, nation: str) -> Optional[str]:
    try:
        for marshal in world.get_player_marshals():
            if int(getattr(marshal, "strength", 0) or 0) <= 0:
                continue
            region = world.get_region(marshal.location)
            if region is not None and getattr(region, "controller", None) == nation:
                return marshal.location
    except Exception:
        return None
    return None


def _build_terms(world, nation: str, limit: int = 2) -> List[str]:
    """`build <thing> in <Region> — Ng`, gated by the SINGLE build gate
    (`region.can_build`), so the counsel and the executor agree by
    construction."""
    if limit <= 0:
        return []
    out: List[str] = []
    try:
        from backend.models.region import BUILDING_TYPES, can_build
    except Exception:
        return []
    region_name = _first_own_region_with_a_corps(world, nation)
    if not region_name:
        return []
    region = world.get_region(region_name)
    if region is None:
        return []
    for key, spec in BUILDING_TYPES.items():
        try:
            ok = can_build(world, region, key, nation)
        except Exception:
            continue
        allowed = ok[0] if isinstance(ok, (tuple, list)) else bool(ok)
        if not allowed:
            continue
        word = key.replace("_", " ")
        out.append(f"build {word} in {region_name} — "
                   f"{int(spec.get('gold_cost') or 0):,}g")
        if len(out) >= limit:
            break
    return out


def what_can_i_do(world, nation: Optional[str] = None,
                  limit: int = 6) -> List[str]:
    """The whole counsel: army, purse, and the door to the Cabinet.

    This is the answer to the typed question *"what can I do"*, the body of
    Berthier's shrug, and the honest tail of an answer the desk cannot give.
    One source, so the three can never disagree.
    """
    if not COUNSEL_IS_DERIVED_FROM_THE_BOARD or world is None:
        return []
    nation = nation or getattr(world, "player_nation", None)
    if not nation:
        return []
    lines = military_counsel(world, nation, limit=max(1, limit - 2))
    lines.extend(economy_counsel(world, nation, limit=2))
    return lines[:limit]


# ───────────────────────────────────────────────────────────────────────────
# THE ROUTER — what to say when the desk cannot answer
# ───────────────────────────────────────────────────────────────────────────
# Every question the desk cannot answer returned the 12,717-character COMMAND
# REFERENCE, which does not contain the words `status`, `where is`, `who
# holds` or `how many men` even once. A player who asks a question the game
# holds the answer to on a SCREEN should be sent to that screen by name, not
# handed a manual.
_SURFACE_FOR_KIND = {
    "economy": ("the Strategic Ledger's Economy tab", "press T, then 3"),
    "forces": ("the Strategic Ledger's Forces tab", "press T"),
    "orders": ("the Strategic Ledger's Orders tab", "press T, then 6"),
    "admiralty": ("THE ADMIRALTY", "press T, then 7"),
    "marshals": ("the Generals screen", "press G"),
    "diplomacy": ("the Cabinet", "press F1"),
    "courts": ("the Diplomatic Ledger", "press D"),
    "war": ("the war banner on the left", "click the war"),
    "gazette": ("Le Moniteur", "press N"),
    "log": ("the campaign log", "press L"),
    "dispatch": ("this morning's dispatch", "press R"),
}


def surface_pointer(kind: str) -> Optional[str]:
    """`"the Strategic Ledger's Economy tab (press T, then 3)"`, or None."""
    entry = _SURFACE_FOR_KIND.get(kind)
    if not entry:
        return None
    name, how = entry
    return f"{name} ({how})"
