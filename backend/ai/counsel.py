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

# ═══════════════════════════════════════════════════════════════════════════
# CRT-7 — the counsel reads the action pools and CN-4's refusals (Score
# Mandate Chunk 3, SR-3a part (ii), September 26, 2026). Measured at the
# real `POST /command` on the shipped boot before a line was written:
#   DESK-9   at 0 military actions `what can I do` offered four orders the
#            game refuses and never named `end turn`;
#   DESK-16  the boot's first reply offered `Ney, drill`, which the game
#            refuses ("cannot drill with enemy forces nearby") — the counsel
#            never asked `tactical_executor.drill_refusal` / `fortify_refusal`;
#   DESK-13  the counsel named ONE corps of eight, and marched a marshal who
#            had already moved back the way he came;
#   AAR-19   `Marmont, attack Moore` across a SHUT crossing — the counsel
#            never asked the crossing gate the attack itself asks;
#   DESK-6   `_is_free_to_order` read `is_drilling`, a flag no Marshal has.
# Each behind its own lever whose down arm reproduces the row.
THE_COUNSEL_READS_THE_ACTION_POINTS = True     # DESK-9
THE_COUNSEL_READS_THE_REFUSALS = True          # DESK-16 (+ DESK-6's flag)
THE_COUNSEL_SPREADS_THE_ORDERS = True          # DESK-13
THE_COUNSEL_READS_THE_CROSSING = True          # AAR-19
# DESK-2's counsel half: the levy line quoted the ledger's 654g for 10,000
# where the order raised 3,000 for 647 — it reads `recruit_quote` now.
THE_LEVY_LINE_IS_THE_QUOTE = True
# DESK-9's copy: what the counsel says when the day's military actions are
# spent. A typed order, like every other line the counsel prints.
END_TURN_LINE = "end turn — no military actions remain today"

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
    if THE_COUNSEL_READS_THE_REFUSALS:
        # DESK-6: the flags a Marshal actually carries. `drilling` is turn N
        # of a drill (the executor refuses an attack, a fortify and a second
        # drill to him); `drilling_locked` is turn N+1, when he takes no
        # order at all.
        if getattr(marshal, "drilling", False) or getattr(marshal, "drilling_locked", False):
            return False
    elif getattr(marshal, "is_drilling", False):
        return False
    if getattr(marshal, "administrative", False):
        return False
    return True


def _military_actions_left(world) -> int:
    try:
        return int(getattr(world, "actions_remaining", 0) or 0)
    except Exception:
        return 0


def _admin_actions_left(world) -> int:
    try:
        return int(getattr(world, "admin_actions_remaining", 0) or 0)
    except Exception:
        return 0


def _crossing_open(world, nation: str, marshal, destination: str) -> bool:
    """AAR-19: the attack's own crossing gate (`naval.crossing_check_reach`,
    the single source every ranged strike reads). True when there is no
    naval layer, or the water is open to this corps."""
    if not THE_COUNSEL_READS_THE_CROSSING:
        return True
    if not getattr(world, "fleets", None):
        return True
    try:
        from backend.game_logic.naval import crossing_check_reach
        verdict = crossing_check_reach(world, nation, marshal.location,
                                       destination, int(marshal.strength))
        return bool(verdict.get("allowed", True))
    except Exception:
        return False


def _attack_candidates(world, nation: str, marshals, enemies_here):
    """Every (marshal, enemy) pair the ATTACK would take: co-located or
    adjacent, a court we are at war with, the crossing open (AAR-19).
    Co-located pairs first, then adjacent, in roster order — the order the
    counsel has always used, so the boot's first line stays the one every
    first-contact surface quotes. The odds are the muster's business (the
    what-if answers them); the counsel offers what the executor TAKES."""
    co_located, adjacent = [], []
    for marshal in marshals:
        region = world.get_region(marshal.location)
        for enemy in enemies_here.get(marshal.location, []):
            if _at_war_with(world, nation, getattr(enemy, "nation", "")):
                co_located.append((marshal, enemy))
        for neighbour in (getattr(region, "adjacent_regions", None) or []):
            for enemy in enemies_here.get(neighbour, []):
                if not _at_war_with(world, nation, getattr(enemy, "nation", "")):
                    continue
                if not _crossing_open(world, nation, marshal, neighbour):
                    continue
                adjacent.append((marshal, enemy))
    return co_located + adjacent


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
    # DESK-9: no military action left, no military order offered — every
    # line below is refused at the AP gate before the marshal is asked.
    is_player = nation == getattr(world, "player_nation", None)
    actions_left = _military_actions_left(world) if is_player else 99
    if THE_COUNSEL_READS_THE_ACTION_POINTS and actions_left <= 0:
        return []
    lines: List[str] = []
    seen_verbs = set()
    # DESK-13: one corps per line where the roster allows — a marshal named
    # for the attack is not the one named for the march, the works or the
    # drill, so the counsel reads as an army and not as one man's day.
    used: set = set()

    def _pick(candidates):
        if not THE_COUNSEL_SPREADS_THE_ORDERS:
            return list(candidates)
        fresh = [m for m in candidates if m.name not in used]
        return fresh + [m for m in candidates if m.name in used]

    try:
        marshals = [m for m in world.get_player_marshals() if _is_free_to_order(m)]
    except Exception:
        return []
    enemies_here = _visible_enemy_map(world, nation)

    # 1. A battle the player can actually fight — co-located first, then
    #    adjacent, and only against a court we are AT WAR with (FA-80(c)'s
    #    rule, which the diplomatic templates never inherited); the crossing
    #    open (AAR-19); the pair the muster's own band most favours first.
    #
    #    ⚠ The at-war test is REDUNDANT TODAY and is kept deliberately.
    #    `get_visible_enemies` reads `get_enemies_of_nation`, which is
    #    already at-war scoped, so a court at peace cannot reach this loop
    #    through it — measured, and the mutation sweep found the first pin on
    #    this line INERT for exactly that reason. It stays because what this
    #    function produces is a target the player is TOLD to attack, and the
    #    cost of an upstream widening is the game proposing a war on a
    #    neutral. It is pinned at the function instead of at the board.
    for marshal, enemy in _attack_candidates(world, nation, marshals, enemies_here):
        lines.append(f"{_display(marshal.name)}, attack {_display(enemy.name)}")
        seen_verbs.add("attack")
        used.add(marshal.name)
        break

    # 2. A march the movement law would ALLOW — asked of the executor's own
    #    pure refusal probe, so the counsel can never propose a road the
    #    order would be refused on (the PF-4 idiom). DESK-13: a corps that
    #    has marched today is not marched again, and among the lawful roads
    #    the one that closes on the nearest enemy we can see is named, not
    #    the one that leads back where he came from.
    enemy_places = list(enemies_here.keys())
    for marshal in _pick(marshals):
        if THE_COUNSEL_SPREADS_THE_ORDERS and getattr(marshal, "moved_this_turn", False):
            continue
        region = world.get_region(marshal.location)
        roads = [n for n in (getattr(region, "adjacent_regions", None) or [])[:8]
                 if not _move_would_be_refused(world, marshal, n)]
        if not roads:
            continue
        if THE_COUNSEL_SPREADS_THE_ORDERS and enemy_places:
            def _closing(name):
                best = None
                for place in enemy_places:
                    try:
                        d = world.get_distance(name, place)
                    except Exception:
                        d = None
                    if d is not None and d >= 0 and (best is None or d < best):
                        best = d
                return best if best is not None else 999
            roads.sort(key=_closing)
        lines.append(f"{_display(marshal.name)}, march to {roads[0]}")
        seen_verbs.add("move")
        used.add(marshal.name)
        break

    # 3. The stance verbs, which are what an idle corps is actually for —
    #    DESK-16: asked of CN-4's single-source refusals first, so the
    #    counsel never offers a drill beside the enemy or works to a man
    #    already engaged; a fortify from NEUTRAL needs two actions (the
    #    executor's own auto-shift) and is not offered on one.
    from backend.commands.tactical_executor import drill_refusal, fortify_refusal
    for marshal in _pick(marshals):
        if len(lines) >= limit:
            break
        if getattr(marshal, "fortified", False):
            if "unfortify" not in seen_verbs:
                lines.append(f"{_display(marshal.name)}, unfortify")
                seen_verbs.add("unfortify")
                used.add(marshal.name)
        elif "fortify" not in seen_verbs:
            if THE_COUNSEL_READS_THE_REFUSALS:
                if fortify_refusal(world, marshal) != ("", ""):
                    continue
                stance = getattr(getattr(marshal, "stance", None), "name", "")
                if stance == "NEUTRAL" and is_player and actions_left < 2:
                    continue
            lines.append(f"{_display(marshal.name)}, fortify")
            seen_verbs.add("fortify")
            used.add(marshal.name)
    for marshal in _pick(marshals):
        if "drill" in seen_verbs or len(lines) >= limit:
            break
        if getattr(marshal, "fortified", False):
            continue
        if THE_COUNSEL_READS_THE_REFUSALS and drill_refusal(world, marshal) != ("", ""):
            continue
        lines.append(f"{_display(marshal.name)}, drill")
        seen_verbs.add("drill")
        used.add(marshal.name)
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
    # DESK-9: the purse's orders are ADMINISTRATIVE actions (`recruit`,
    # `build`, `repair` — `meta_executor.ADMIN_ACTIONS`); none is offered
    # when the day's administrative actions are spent.
    if (THE_COUNSEL_READS_THE_ACTION_POINTS
            and nation == getattr(world, "player_nation", None)
            and _admin_actions_left(world) <= 0):
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
    pricing it).

    DESK-2 (CRT-7): the figures are `economy_executor.recruit_quote`'s — the
    recipient, the men after the field cap, the gold the executor charges —
    not the ledger's headline levy (measured: the line quoted 654g for
    10,000 where the order raised 3,000 for 647). Only an order the quote
    says WILL be made is offered.
    """
    if THE_LEVY_LINE_IS_THE_QUOTE:
        try:
            from backend.commands.economy_executor import recruit_quote
        except Exception:
            return None
        seen = set()
        best = None
        try:
            marshals = list(world.get_player_marshals())
        except Exception:
            return None
        for marshal in marshals:
            if int(getattr(marshal, "strength", 0) or 0) <= 0:
                continue
            if getattr(marshal, "captured_by", ""):
                continue
            where = marshal.location
            if where in seen or where not in getattr(world, "regions", {}):
                continue
            seen.add(where)
            try:
                quote = recruit_quote(world, where, "infantry", nation)
            except Exception:
                continue
            if quote.get("ok") and (best is None
                                    or int(quote["price"]) < int(best[1]["price"])):
                best = (where, quote)
        if best is None:
            return None
        where, quote = best
        return (f"recruit infantry in {where} — {int(quote['price']):,}g for "
                f"{int(quote['amount']):,} men under {_display(str(quote['recipient']))}")
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
    # GE-3: the summons LEADS when it would be carried out — it is the win.
    lines = congress_counsel(world, nation)
    lines.extend(military_counsel(world, nation,
                                  limit=max(1, limit - 2 - len(lines))))
    lines.extend(economy_counsel(world, nation, limit=2))
    # DESK-9: with the military actions spent, the order that would be
    # carried out is `end turn` — named, as the first line when nothing
    # military survives (the purse's lines may still follow it).
    if (THE_COUNSEL_READS_THE_ACTION_POINTS
            and nation == getattr(world, "player_nation", None)
            and _military_actions_left(world) <= 0):
        lines.insert(0, END_TURN_LINE)
    return lines[:limit]


def congress_counsel(world, nation: str) -> List[str]:
    """GE-3 "The Congress of Paris": `summon the congress — …`, only when
    the summons would be carried out THIS morning — every gate term met,
    the administrative action and the two diplomatic points included — read
    off the executor's own refusal (`congress.summon_refusal`), so the
    counsel can never offer a summons the executor would refuse. Empty on a
    world whose scenario arms no Congress, and for any nation but the one
    that summons (GR5: the Congress is the player's verb)."""
    if not COUNSEL_IS_DERIVED_FROM_THE_BOARD or world is None:
        return []
    try:
        from backend.game_logic import congress
        if nation != getattr(world, "player_nation", None):
            return []
        if not congress.armed(world):
            return []
        if congress.summon_refusal(world, skip_admin=False) is not None:
            return []
        from backend.display_names import plural
        return [f"{congress.SUMMON_COMMAND} — "
                f"{plural(congress.SUMMON_DP_COST, 'diplomatic point')} and "
                f"1 administrative action; it cannot be undone"]
    except Exception:
        # The counsel must never break the surface that calls it.
        return []


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
    # GE-3: the Congress of Paris — the table of the great powers' answers,
    # their reasons and their prices (ENDGAME_PLAN §4).
    "congress": ("the Diplomatic Ledger's Congress tab", "press D, then 7"),
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
