"""
Strategic Command Execution for Phase 5.2-C

Handles multi-turn strategic orders: MOVE_TO, PURSUE, HOLD, SUPPORT
Called from turn_manager.py at START of player's turn (BEFORE advance_turn).

TIMING: Runs after enemy AI phase so battles_this_turn is populated
for cannon fire detection. advance_turn() clears battles afterward.

IMPORTANT PATTERNS:
- Cavalry (movement_range=2) moves 2 regions per turn
- Infantry (movement_range=1) moves 1 region per turn
- _strategic_execution=True skips action cost + objections in executor
- _sortie=True prevents advancing on victory (HOLD sally mechanic)
- LITERAL personality NEVER interrupts for cannon fire (THE GROUCHY MOMENT)

All actions go through executor.execute() with _strategic_execution=True
to maintain the Building Blocks principle.
"""

from typing import Dict, List, Optional, Tuple

# NP-V: who SAYS an interrupt line — the marshal himself, or Berthier when
# the marshal is the sovereign (the Emperor never addresses the player).
from backend.game_logic.marshal_voice import interrupt_speaker


def _strategic_command_flavor(cmd_type: str) -> str:
    """Convert internal command type to player-facing flavor text."""
    return {
        "MOVE_TO": "his march",
        "PURSUE": "the pursuit",
        "HOLD": "his position",
        "SUPPORT": "reinforcement orders",
    }.get(cmd_type, "his orders")


# Aug 8 2026 tutorial live report (TUT-F4a): interrupts raised BY a strategic
# order are meaningless once that order is gone, and a stale one hijacks the
# player's next command — the School of War's own "attack that name" advice
# was consumed as a cannon_fire answer and refused with "no active strategic
# order". The executor's override-cancel clears these WITH the order it kills;
# `last_stand` and `muster_confirm` are standalone player decisions and are
# NEVER cleared this way (dropping them strands the marshal / the attack).
ORDER_BOUND_INTERRUPT_TYPES = frozenset({
    "contact", "contact_bad_odds", "cannon_fire",
    "destination_blocked", "combat_stalemate",
})

# The complement: a decision the player owes a marshal that no order raised
# and no order can retire. `last_stand` (W6-7) and `muster_confirm` (W6-4).
STANDALONE_DECISION_TYPES = frozenset({"last_stand", "muster_confirm"})

# FA-16 (slice 2, Sept 4 2026) flip lever — the HOST_RULE_ACTIVE idiom.
# False reproduces the pre-slice behaviour byte-for-byte: an order-free
# parked decision is invisible to the end-turn processor, never re-validated,
# and a fresh order to the cornered marshal simply executes over it.
STANDALONE_DECISION_LIVENESS_ACTIVE = True

# FA-16 review round (Sept 4 2026, reviews R1-F3 / R2-F1 / R3): the verbs
# that may reach a marshal whose last stand is unanswered. `cancel` names
# the question (FA-N13's graceful arm); the rest are not orders at all.
STANDING_DECISION_EXEMPT_ACTIONS = frozenset(
    {"cancel", "status", "help", "unknown", "debug", "cheat"})

# The P4 rung's futility brake has always been the literal 3; P0 reads it
# too now (FA-N72's non-stub half), so the number lives in one place.
ATTACK_FUTILITY_LIMIT = 3


# ── FA-49: what each button on an interrupt popup COSTS ────────────────────
#
# The cautious cannon-fire ask offers three buttons and states no price, and
# two of them are charged: continuing the order costs 2 trust, abandoning it
# to hold costs 3, and running for the guns is free. Measured over the
# archived campaigns the ask fires 19 times, every other turn per marshal,
# so a player who answers it a dozen times has paid up to 36 trust without a
# figure ever appearing on screen.
#
# ⚠ DERIVED, never a static table. The blocked-path family charges
# `0 if is_first_step else -3` (below), and the three builders that set
# `is_first_step: True` live in `strategic_executor.py` — a hard-coded table
# emitted from this file alone would have printed "−3" on an interrupt that
# charges nothing, which is a NEW shown-vs-applied of exactly the class the
# row exists to close.
CANNON_FIRE_CONTINUE_TRUST = -2   # non-literal acting literal
CANNON_FIRE_HOLD_TRUST = -3       # abandoning the order to stand still
BLOCKED_PATH_ABANDON_TRUST = -3   # …and 0 when the order has not begun


def interrupt_option_costs(interrupt: Optional[Dict]) -> Dict[str, int]:
    """The trust price of each option on ONE interrupt, derived from the
    interrupt's own fields.

    Reads `interrupt_type` and `is_first_step` off the dict the builders
    already produce, so it cannot drift from them the way a table beside
    them would. Options that cost nothing are OMITTED rather than reported
    as 0 — a free button should say nothing, not "(trust 0)".
    """
    if not isinstance(interrupt, dict):
        return {}
    kind = str(interrupt.get("interrupt_type") or "")
    options = [str(o) for o in (interrupt.get("options") or [])
               if isinstance(o, (str, bytes))]
    first_step = bool(interrupt.get("is_first_step"))
    costs: Dict[str, int] = {}
    if kind == "cannon_fire":
        costs["continue_order"] = CANNON_FIRE_CONTINUE_TRUST
        costs["hold_position"] = CANNON_FIRE_HOLD_TRUST
    elif kind in ("blocked_path", "enemy_contact", "attack_on_arrival"):
        if not first_step:
            for option in ("hold_position", "cancel_order"):
                costs[option] = BLOCKED_PATH_ABANDON_TRUST
    return {k: v for k, v in costs.items() if k in options and v}


def last_stand_question_line(marshal) -> str:
    """The ONE sentence every surface uses to name the two answers."""
    return (f"{marshal.name} is cornered at {marshal.location} and awaits "
            f"your word, Sire — 'fight to the last' or 'attempt a breakout'.")


def standing_last_stand_refusal(marshal, action: Optional[str] = None) -> Optional[Dict]:
    """FA-16: the free refusal for ANY order to a marshal whose last stand
    is unanswered, or None when nothing is parked / the verb is exempt /
    the lever is down.

    Review round (Sept 4 2026). Slice 2 sited this refusal under the
    executor's `should_check_objection`, whose predicate excludes strategic
    commands — the very `march`/`hold`/`pursue` the landing record named as
    its measured defect — and whose action list omits `charge`/`bombard`/
    `garrison`/`unfortify`. Three reviewers reproduced the bypass
    independently: a march overwrote the ask with a `contact_bad_odds`
    question and orphaned the rail row; a co-located pursue ran the attack
    at once and FA-1's "no word came" resolution fired in the PLAYER phase
    on the player's own typed order. The refusal is now one function, read
    by the executor ABOVE the objection predicate for every marshal-bearing
    verb, by the un-addressed general retreat / bare attack / auto-scout
    rosters, and by Berthier's parse-recovery line.
    """
    if not STANDALONE_DECISION_LIVENESS_ACTIVE or marshal is None:
        return None
    if action in STANDING_DECISION_EXEMPT_ACTIONS:
        return None
    pending = standalone_decision(marshal)
    if not pending or pending.get("interrupt_type") != "last_stand":
        return None
    return {
        "success": False,
        "no_action_cost": True,
        "last_stand_pending": True,
        "message": (last_stand_question_line(marshal)
                    + " No other order can reach him until you decide."),
    }


def pending_marshal_decisions(world) -> List[str]:
    """Names of the player's marshals whose last stand is unanswered — the
    question the enemy phase decides FOR him if the turn ends (FA-1).

    Review round (R1-F5): UX23 built the end-turn soft-stop for envoys;
    the marshal had none. Rides beside `pending_lapsing_count` on every
    response so the client can warn before sending `end turn`.
    """
    if not STANDALONE_DECISION_LIVENESS_ACTIVE:
        return []
    names: List[str] = []
    for marshal in world.get_player_marshals():
        pending = standalone_decision(marshal)
        if (pending and pending.get("interrupt_type") == "last_stand"
                and marshal.strength > 0
                and not getattr(marshal, "captured_by", "")):
            names.append(marshal.name)
    return sorted(names)


def _province_seen(world, location: str) -> bool:
    """PARTIAL-or-better in the player's intel store (the `get_visible_enemies`
    rule), so a retirement reason never names an unscouted province."""
    try:
        from backend.models.intel import PARTIAL
        return bool(world.get_region_intel(location).visibility_at_least(PARTIAL))
    except Exception:
        return False


def current_besieger(marshal, world, exclude: str = ""):
    """The at-war corps ON or NEXT to `marshal` that the player can see —
    co-located first, then the strongest — or None.

    Review round (R1-F4): a last stand is "fight or break out", not "fight
    MACK". When the man who asked it has drawn off and another stands on
    the marshal, the question is still exactly as live; keying liveness to
    the named enemy retired it, discarded the player's word, and the next
    defeat re-asked — or decided — the identical question.
    """
    region = world.get_region(marshal.location)
    adjacent = set(getattr(region, "adjacent_regions", None) or []) if region else set()
    best = None
    for enemy in world.get_visible_enemies(marshal.nation):
        if enemy.name == exclude:
            continue
        # (`get_visible_enemies` already restricts to courts AT WAR with
        # the marshal's nation and to living corps; only the ground is
        # checked here.)
        if getattr(enemy, "captured_by", ""):
            continue
        if enemy.location != marshal.location and enemy.location not in adjacent:
            continue
        key = (enemy.location == marshal.location, int(enemy.strength), enemy.name)
        if best is None or key > best[0]:
            best = (key, enemy)
    return best[1] if best else None


def muster_is_live(marshal, world, pending: Optional[Dict] = None) -> Tuple[bool, str]:
    """Is a parked muster still the question it was when it was asked?

    Review round (R2-F5): the record said the muster "re-validates itself"
    through the re-issued attack. Half true — a target who marched away
    answered `attack_anyway` with a pursuit refusal ("No intelligence on
    Mack's position"), and a DESTROYED target answered it with an objection
    about a man who no longer exists (objection runs before target
    validation on the re-issue). Same shape as `last_stand_is_live`, same
    retirement copy. A REGION target (a garrison assault) is left to the
    re-issue's own validation.
    """
    from backend.display_names import humanize_entity_name as _hum

    pending = pending or standalone_decision(marshal)
    if not pending or pending.get("interrupt_type") != "muster_confirm":
        return False, "no muster is pending"
    if marshal.strength <= 0 or getattr(marshal, "captured_by", ""):
        return False, f"{marshal.name} no longer stands in the field"
    target_key = pending.get("target") or ""
    target = world.get_marshal(target_key) if target_key else None
    if target is None and target_key and world.get_region(target_key) is not None:
        return True, ""
    label = _hum(target_key) if target_key else "the enemy"
    if (target is None or getattr(target, "strength", 0) <= 0
            or getattr(target, "captured_by", "")):
        return False, f"{label} no longer stands in the field"
    if not world.is_at_war(marshal.nation, target.nation):
        return False, f"we are no longer at war with {target.nation}"
    region = world.get_region(marshal.location)
    adjacent = set(getattr(region, "adjacent_regions", None) or []) if region else set()
    if target.location != marshal.location and target.location not in adjacent:
        # Fog-honest: name the province only if the player can see it.
        if _province_seen(world, target.location):
            return False, f"{label} has marched to {target.location}"
        return False, f"{label} has slipped out of contact"
    if target.name not in {m.name for m in world.get_visible_enemies(marshal.nation)}:
        return False, f"{label} has slipped out of contact"
    return True, ""


def standalone_decision(marshal) -> Optional[Dict]:
    """The parked player decision on `marshal`, or None.

    A decision is the interrupt dict itself when its type is standalone
    (never order-bound). Order-bound interrupts return None here: they are
    `clear_order_bound_interrupt`'s business, not this seam's.
    """
    pending = getattr(marshal, "pending_interrupt", None)
    if (isinstance(pending, dict)
            and pending.get("interrupt_type") in STANDALONE_DECISION_TYPES):
        return pending
    return None


def last_stand_is_live(marshal, world, pending: Optional[Dict] = None) -> Tuple[bool, str]:
    """Is a parked last stand still the question it was when it was asked?

    FA-16 (slice 2, Sept 4 2026). The ask is raised at one moment — beaten,
    cornered at a province, by a named enemy — and it used to be answered
    whenever the player got round to it, against whatever that enemy was
    doing by then. Measured: Ney's turn-16 question was answered on turn 22
    with "fight to the last", and `_resolve_last_stand_fight` bled Archduke
    Charles by 7,500 men from Milan — NOT adjacent to Ney — before taking
    Ney prisoner in a province the enemy had long since left.

    A question stays live only while every premise holds: the marshal still
    stands, at the province he was cornered in; the enemy who cornered him
    still stands, is still an enemy, and is still ON him or NEXT to him.
    When any premise fails the caller retires the question with the reason,
    and the marshal simply awaits orders — the road opened by itself.

    Returns (live, reason) where `reason` is the player-facing clause
    explaining why the question is overtaken (empty when live).
    """
    from backend.display_names import humanize_entity_name as _hum

    pending = pending or standalone_decision(marshal)
    if not pending or pending.get("interrupt_type") != "last_stand":
        return False, "no last stand is pending"
    if marshal.strength <= 0 or getattr(marshal, "captured_by", ""):
        return False, f"{marshal.name} no longer stands in the field"
    asked_at = pending.get("location")
    if asked_at and asked_at != marshal.location:
        return False, f"{marshal.name} has marched clear of {asked_at}"
    enemy_key = pending.get("enemy") or ""
    enemy = world.get_marshal(enemy_key) if enemy_key else None
    enemy_label = _hum(enemy_key) if enemy_key else "the enemy"
    region = world.get_region(marshal.location)
    adjacent = set(getattr(region, "adjacent_regions", None) or []) if region else set()
    reason = ""
    if (enemy is None or getattr(enemy, "strength", 0) <= 0
            or getattr(enemy, "captured_by", "")):
        reason = f"{enemy_label} no longer stands in the field"
    elif not world.is_at_war(marshal.nation, enemy.nation):
        reason = f"we are no longer at war with {enemy.nation}"
    elif enemy.location != marshal.location and enemy.location not in adjacent:
        # Fog-honest (review round): `get_marshal` is omniscient, and the
        # reason used to name a province the player had never scouted.
        reason = (f"{enemy_label} has drawn off to {enemy.location}"
                  if _province_seen(world, enemy.location)
                  else f"{enemy_label} has drawn off out of sight")
    if not reason:
        return True, ""
    # Review round (R1-F4): the man who asked it is gone, but the question
    # is about the marshal's OWN fate — if another at-war corps stands on
    # or beside him, it is exactly as live, keyed to that corps now.
    besieger = current_besieger(marshal, world, exclude=enemy_key)
    if besieger is not None:
        pending["enemy"] = besieger.name
        pending["enemy_nation"] = besieger.nation
        return True, ""
    return False, reason


def pursue_known_location(world, marshal, enemy):
    """NPC-5: where the ORDER-GIVER believes the quarry is.

    Fog for the player, live truth for the AI. The gate on `player_nation`
    is load-bearing, not a courtesy: enemy planners are deliberately
    omniscient throughout, and routing them through the PLAYER's intel store
    would both blind them and make an AI's pursuit depend on what France
    happens to have scouted.

    Returns None when the player has never seen him.

    THE SINGLE SOURCE, and it lives here rather than on the executor for the
    reason NPC-2 already made about `clear_order_bound_interrupt`: the first
    cut of this fix corrected ONE of five destination-resolution sites, and
    the four it missed are all in this module's per-turn processor — the
    HOTTER path, run on every turn of a pursuit. Measured before the lift: a
    player's pursuit was re-plotted to a province his intel called
    `unknown`, because the reroute read the quarry's true location. Five
    copies of a rule is how the rule dies.
    """
    if enemy is None:
        return None
    if marshal.nation != getattr(world, "player_nation", None):
        return enemy.location
    known = world.get_last_known_location(enemy.name)
    return known[0] if known else None


# ── FA slice 5 "The Road Law" (September 4, 2026) ─────────────────────────
# Four marching verbs × two seams (issuance in strategic_executor.py, the
# per-turn tick here) each owned a private copy of route-plotting, and only
# the per-turn `_get_personality_aware_path` obeyed the movement law (PF-8's
# `passable_for`). Measured on the shipped board: issuance plotted the
# terrain-cheapest road through a neutral's closed frontier, charged 2 AP and
# refused the first hop silently (FA-13); a route whose last leg the Royal
# Navy holds SHUT was accepted with a route and no warning (FA-46); HOLD
# re-plotted raw every turn, discarding every reroute (FA-N11) and dying
# "Cannot reach X" past a closed border with a legal all-French corridor on
# the map (FA-N12/FA-N49); SUPPORT re-stalled "could not move toward" forever
# (FA-N41). `plot_route` is the ONE ladder every seam plots by;
# `issuance_road_refusal` reads its verdict before an AP is charged;
# `_stall_verdict` is PF-8's stall idiom, one copy for MOVE_TO/HOLD/SUPPORT.
# Each lever False reproduces the prior behaviour byte-for-byte.
ROAD_LAW_AT_ISSUANCE = True      # issuance plots lawful-first, refuses at 0 AP
ROAD_LAW_ON_REPLOT = True        # the three re-plots + the compromise obey it
ROAD_LAW_ONE_SEAM = True         # `_get_personality_aware_path` delegates
HOLD_KEEPS_ITS_ROAD = True       # HOLD keeps `order.path`; its stall speaks
SUPPORT_STALL_SPEAKS = True      # SUPPORT reroutes-or-breaks with the reason
STALE_ROAD_REPLOTS = True        # a road whose first step is not adjacent re-plots
STRATEGIC_STEP_NEVER_UPGRADES = True  # a per-hop step never mints a NEW order


def region_is_adjacent(world, here: str, there: str) -> bool:
    """One road-step: `there` is walkable from `here` (sea links included —
    the registry's `adjacent` IS walkability)."""
    region = world.get_region(here) if here else None
    return bool(region) and there in (getattr(region, "adjacent_regions", None) or [])


def enemy_occupied_regions(world, nation: str, marshal=None,
                           fog_aware: bool = False) -> List[str]:
    """Provinces with an enemy of `nation` standing on them — fog-honest for
    the player (PARTIAL+ only), omniscient for the AI (Session 34B). ONE
    source: the processor's cautious avoid-set and the executor's issuance
    scan (which used to duplicate this loop inline) both read it."""
    from backend.models.intel import FULL, PARTIAL
    if marshal is not None and not fog_aware:
        fog_aware = (marshal.nation == world.player_nation)
    found = []
    for region_name in world.regions:
        if fog_aware:
            intel = world.get_region_intel(region_name)
            if intel.visibility not in (FULL, PARTIAL):
                continue
        if world.get_enemies_in_region(region_name, nation):
            found.append(region_name)
    return found


def plot_route(world, marshal, destination: str, *, use_weighted: bool,
               avoid_regions=None, avoid_is_law: bool = False,
               want_verdict: bool = False):
    """THE road-plotting seam. Returns ``(path_without_start, verdict)``.

    The ladder — a PLAYER corps prefers a corridor it may lawfully walk (own,
    allied, open-border or at-war soil, `_region_passable_for`); the AI keeps
    omniscient routing (`passable_for=None`, `_pf` is None):

        avoid + lawful → lawful → terrain-only            (avoid_is_law False)
        avoid + lawful → avoid + terrain-only             (avoid_is_law True:
                                                           a REROUTE must still
                                                           avoid what it fled)

    The terrain-only fallback keeps PF-8's contract — the order still forms
    and the stall seam says why — and is what `issuance_road_refusal` reads
    to refuse BEFORE an AP is charged. `verdict` (player only, on request)
    describes the road actually returned, so shown = applied:

        legal · blocker_region / blocker_controller (the first closed
        intermediate) · closed_destination · naval_leg / naval_check (the
        first sea leg `crossing_check` refuses — SHUT, or NV-4's defended
        shore; the pathfinders are edge-blind to sail).
    """
    pathfinder = world.find_weighted_path if use_weighted else world.find_path
    player = marshal.nation == world.player_nation
    _pf = marshal.nation if player else None
    avoid = list(avoid_regions or [])
    path = None
    if avoid:
        path = pathfinder(marshal.location, destination,
                          avoid_regions=avoid, passable_for=_pf)
    if not path and not avoid_is_law:
        path = pathfinder(marshal.location, destination, passable_for=_pf)
    if not path and _pf:
        if avoid_is_law:
            path = pathfinder(marshal.location, destination, avoid_regions=avoid)
        else:
            path = pathfinder(marshal.location, destination)
    if not path:
        return None, None
    road = [r for r in path if r != marshal.location]
    if not want_verdict or not player:
        return road, None
    nation, here = marshal.nation, marshal.location
    blocker = next((r for r in road[:-1]
                    if not world._region_passable_for(
                        r, nation, mover_location=here)), None)
    blocker_region = world.regions.get(blocker) if blocker else None
    naval_leg = None
    naval_check = None
    if getattr(world, "fleets", None):
        from backend.game_logic.naval import crossing_check, is_sea_link
        prev = here
        for step in road:
            if is_sea_link(world, prev, step):
                check = crossing_check(
                    world, nation, prev, step,
                    mover_strength=int(getattr(marshal, "strength", 0) or 0))
                if not check.get("allowed", True):
                    naval_leg, naval_check = (prev, step), check
                    break
            prev = step
    # A march to where a VISIBLE enemy stands is an attack in the making, not
    # an entry — the first-step-blocked flow owns it (aggressive fights,
    # cautious asks), whatever flag flies over the province. Fog decides
    # visibility (`get_visible_enemies_in_region`, PARTIAL+): an unseen enemy
    # on closed soil neither opens the road nor leaks by opening it.
    closed_destination = (
        not world._region_passable_for(destination, nation, mover_location=here)
        and not world.get_visible_enemies_in_region(destination, nation))
    verdict = {
        "legal": blocker is None,
        "blocker_region": blocker,
        "blocker_controller": ((blocker_region.controller if blocker_region else None)
                               or "neutral"),
        "closed_destination": closed_destination,
        "naval_leg": naval_leg,
        "naval_check": naval_check,
    }
    return road, verdict


def issuance_road_refusal(world, marshal, destination: str, strategic_type: str,
                          verdict) -> Optional[Dict]:
    """Read `plot_route`'s verdict at ISSUANCE and refuse, at 0 AP, what the
    per-turn march would only have stalled on a turn later (player only):

    * a MOVE_TO/HOLD whose DESTINATION is closed soil (the tactical `move`
      already refused this — the strategic verb accepted it, marched a turn
      and died "Cannot reach X");
    * no lawful corridor at all (S5-D2's own refusal, in its own words);
    * a sea leg the crossing gate refuses (FA-46 — a route "→ London" with
      the Royal Navy at 1.9× used to be announced with no naval word in it).
    """
    if verdict is None or marshal.nation != world.player_nation:
        return None
    if strategic_type in ("MOVE_TO", "HOLD") and verdict.get("closed_destination"):
        region = world.regions.get(destination)
        controller = (getattr(region, "controller", None) or "neutral")
        state = world.get_diplomatic_state(marshal.nation, controller)
        return {
            "success": False,
            "message": (
                f"Cannot enter {destination}, Sire — it is controlled by "
                f"{controller} (diplomatic state: {state}). Secure open "
                f"borders or declare war to pass."
            ),
            "blocked_diplomatic": controller,
            "blocked_state": state,
            "variable_action_cost": 0,
        }
    if not verdict.get("legal", True):
        blocker = verdict.get("blocker_region")
        blk_ctrl = verdict.get("blocker_controller") or "neutral"
        return {
            "success": False,
            "message": (
                f"There is no open road to {destination}, Sire — every "
                f"route crosses {blk_ctrl}'s closed frontier at "
                f"{blocker}. Secure passage (open borders, or "
                f"war) or name a province we can reach."
            ),
            "variable_action_cost": 0,
        }
    check = verdict.get("naval_check")
    if check is not None:
        leg = verdict.get("naval_leg") or ("", "")
        return {
            "success": False,
            "message": check.get("message") or (
                f"The crossing from {leg[0]} to {leg[1]} is barred by "
                f"hostile sail — the road to {destination} runs over water "
                f"we do not command."),
            "blocked_naval": check.get("coverer"),
            "naval_ratio": check.get("ratio"),
            "variable_action_cost": 0,
        }
    return None


def resolve_order_destination(world, marshal, order):
    """The destination a standing order should aim at, fog included.

    Shared by the four `_handle_blocked_path` personality arms and the
    `go_around` response handler. An ALLY's position is our own
    intelligence, so SUPPORT keeps the direct read; an enemy's is not.
    """
    destination = order.target_snapshot_location or order.target
    if destination and destination not in world.regions:
        target_marshal = world.get_marshal(destination)
        if target_marshal:
            if target_marshal.nation == marshal.nation:
                destination = target_marshal.location
            else:
                destination = pursue_known_location(
                    world, marshal, target_marshal)
    return destination


def _combat_carry(result) -> Dict:
    """WO-33 (slice 12): the keys a strategic-report row carries for the
    battle it reports — Berthier's `battle_report` and the executor's
    cleaned result as `battle_details` (the HOLD sally's own key), with
    `new_state` stripped (the standing serialization rule: it holds the
    WorldState and would drop the whole report on the wire)."""
    if not isinstance(result, dict):
        return {"battle_report": None, "battle_details": None}
    cleaned = {k: v for k, v in result.items() if k != "new_state"}
    return {"battle_report": cleaned.get("battle_report"),
            "battle_details": cleaned,
            # FA-N10 (slice 3, Sept 4 2026): the ONE key both strategic-report
            # renderers actually print (`main.gd::_show_strategic_reports`,
            # `strategic_report_popup.gd::_format_report`). Neither reads
            # `battle_report` or `battle_details`, so a battle fought under a
            # standing order reached the player with no casualties at all.
            "battle_message": cleaned.get("message", ""),
            # FA slice 3 review round (R2-F2/F7): the tableau and the
            # war-purpose triad live at the ROW level too — the client's
            # diorama stash and the deferred-dialogue raise read the row,
            # not `battle_details` (which no renderer reads).
            **{k: cleaned[k] for k in ("battle_diorama", "diplomatic_dialogue",
                                        "awaiting_diplomatic_response",
                                        "war_purpose_popup")
               if cleaned.get(k) is not None}}


# ═══════════════════════════════════════════════════════════════════════════
# FA slice 3 (September 4, 2026) — "THE ORDER TELLS THE TRUTH"
#
# Eleven sites in this file and strategic_executor.py execute an attack for
# a standing order, and exactly ONE of them (`_execute_hold_bombardment`)
# read the executor's answer before narrating it. The other ten narrated
# whatever came back — so an attack the executor REFUSED (the NV-4 crossing
# gate is the reachable one: an enemy on the far shore of the Channel) was
# reported as "the battle was inconclusive" with a stalemate interrupt
# (FA-14/15/19), as "sallies forth to attack Moore" every turn with the
# refusal printed underneath (FA-N40/N26), as "attacks Moore … Assault
# failed — orders cancelled" (the answered contact), as "Moore spotted at
# London! Engaging!" over a PURSUE left standing (the FA-20 family), and as a
# pursuit COMPLETED "— and I trust the next order has more fire in it". One
# predicate, read at every one of them.
# ═══════════════════════════════════════════════════════════════════════════

# FA slice 3 REVIEW ROUND (Sept 4 2026) — flip levers, the HOST_RULE_ACTIVE
# idiom. False reproduces the slice-3 behaviour byte-for-byte.
#   CANNON_FIRE_READS_THE_ANSWER — the two cannon-fire arms act with the
#     order STANDING and abandon it only for a battle fought or a march made
#     (R1-F1/F2, R2-F3: a refused attack destroyed a live order for nothing,
#     and a recklessness-3 cavalryman armed a charge popup nothing could
#     answer);
#   ANSWERED_CONTACT_READS_THE_BOARD — the answered contact is re-validated,
#     keyed on a fought battle, and never minted into a pursuit (R1-F3/F4,
#     R2-F4).
CANNON_FIRE_READS_THE_ANSWER = True
ANSWERED_CONTACT_READS_THE_BOARD = True


def fought_battle_victor(result, marshal_name: str) -> Optional[str]:
    """The victor a FOUGHT battle in `result` names: the winner's name, ""
    for a battle with no victor (a stalemate), None when no battle was
    fought at all — a refusal, a staged dialogue, a minted order.

    Review round (R1-F3/F4): the answered contact read `success` alone and
    called a war-purpose staging and a PURSUE it had just minted "Assault
    failed — orders cancelled".
    """
    if not isinstance(result, dict):
        return None
    for event in result.get("events") or []:
        if not isinstance(event, dict):
            continue
        if event.get("type") == "battle":
            return str(event.get("victor") or "")
        if event.get("type") == "glorious_charge":
            return marshal_name if event.get("attacker_won") else ""
    br = result.get("battle_result")
    if isinstance(br, dict):
        return str(br.get("victor") or "")
    return None


def contact_is_live(marshal, world, pending: Dict) -> Tuple[bool, str]:
    """Is an order-bound contact question still the question it was?

    Review round (R1-F3/F4): the order-bound asks (`contact`,
    `contact_bad_odds`, `destination_blocked`) had no liveness check and
    `end turn` never required them answered, so the question survived the
    enemy phase that moved the blocker away — and the answer `attack`
    then fought a man two provinces off (through the executor's
    attack-to-pursuit upgrade) or a court France had made peace with. The
    named enemy must still stand, at war with us, on or beside the marshal.
    """
    from backend.display_names import humanize_entity_name as _hum

    enemy_key = pending.get("enemy") or ""
    enemy = world.get_marshal(enemy_key) if enemy_key else None
    label = _hum(enemy_key) if enemy_key else "the enemy"
    if (enemy is None or getattr(enemy, "strength", 0) <= 0
            or getattr(enemy, "captured_by", "")):
        return False, f"{label} no longer stands in the field"
    if not world.is_at_war(marshal.nation, enemy.nation):
        return False, f"we are no longer at war with {enemy.nation}"
    region = world.get_region(marshal.location)
    adjacent = set(getattr(region, "adjacent_regions", None) or []) if region else set()
    if enemy.location != marshal.location and enemy.location not in adjacent:
        if _province_seen(world, enemy.location):
            return False, f"{label} has marched to {enemy.location}"
        return False, f"{label} has slipped out of contact"
    return True, ""


def retract_order_log(world, marshal_name: str, order_type: str) -> bool:
    """Review round (R1-F6): a first step refused at 0 AP leaves no order —
    and no campaign-log row saying one was given. Pops the most recent
    `strategic_order` event this turn for this marshal and order type."""
    log = getattr(world, "event_log", None)
    if not isinstance(log, list):
        return False
    turn = getattr(world, "current_turn", None)
    for i in range(len(log) - 1, -1, -1):
        ev = log[i]
        if (isinstance(ev, dict) and ev.get("type") == "strategic_order"
                and ev.get("marshal") == marshal_name
                and ev.get("order_type") == order_type
                and ev.get("turn") == turn):
            del log[i]
            return True
    return False


def attack_was_refused(result) -> bool:
    """True when the executor REFUSED a strategic attack — no battle happened.

    A refusal is `success: False` with no battle of any shape: no `battle` or
    `glorious_charge` event and no `battle_result`. A FOUGHT battle that was
    lost is `success: True` with events, and the FA-N3 fixtures that call
    `_handle_combat_result` with event-only dicts carry no `success` key at
    all — so the test is `is False`, never `not success` (the filed FA-14
    fix_shape, which reds six green pins).
    """
    if not isinstance(result, dict) or result.get("success") is not False:
        return False
    events = result.get("events") or []
    if isinstance(events, dict):
        events = [events]
    for event in events:
        if (isinstance(event, dict)
                and event.get("type") in ("battle", "glorious_charge")):
            return False
    if result.get("battle_result"):
        return False
    return True


def refusal_reason(result) -> str:
    """The executor's own sentence for a refusal, never a battle word."""
    message = ""
    if isinstance(result, dict):
        message = str(result.get("message") or "").strip()
    return message or "the attack could not be made"


def refusal_keys(result) -> Dict:
    """The structured refusal keys a report row carries so the client and the
    digest can tell a barred crossing from a closed border."""
    keys: Dict = {}
    if isinstance(result, dict):
        for key in ("blocked_naval", "naval_ratio", "blocked_diplomatic"):
            if result.get(key) is not None:
                keys[key] = result[key]
    return keys


def strike_crossing_verdict(world, marshal, region: str):
    """The executor's OWN crossing predicate, asked BEFORE an order commits
    to a fight across water: `crossing_check_reach`, exactly as
    `_execute_attack` asks it. Returns the blocking verdict dict when the
    strike would be refused, None when it may proceed (or there is no naval
    layer). Both contact producers and the HOLD sally read this, so an
    enemy standing on the far shore of a SHUT crossing is never offered as
    something to attack, ask about, or sally against.
    """
    if not getattr(world, "fleets", None) or not region:
        return None
    if region == getattr(marshal, "location", None):
        return None
    from backend.game_logic.naval import crossing_check_reach
    verdict = crossing_check_reach(
        world, marshal.nation, marshal.location, region,
        int(getattr(marshal, "strength", 0) or 0))
    if verdict.get("allowed", True):
        return None
    return verdict


def verdict_as_refusal(verdict) -> Dict:
    """Shape a crossing verdict like the executor's own refusal dict."""
    return {
        "success": False,
        "message": verdict.get("message", "the crossing is barred"),
        "blocked_naval": verdict.get("coverer"),
        "naval_ratio": verdict.get("ratio"),
    }


def clear_order_bound_interrupt(marshal) -> bool:
    """NPC-2: the question dies with the order that raised it.

    TUT-F4a wrote this rule, but only as an inline block inside
    `executor.py`'s objection branch — which is gated on
    `should_check_objection`, and that predicate EXCLUDES
    `is_strategic_command`. So the rule was unreachable for exactly the
    commands that raise these interrupts: issuing a fresh strategic order
    left the old order's question armed, and `main.py`'s interrupt router
    then answered the NEXT line naming that marshal with it. Measured:
    after `Ney, march to Frankfurt` replaced a Swabia order,
    `strategic_order.target == "Frankfurt"` while `pending_interrupt` still
    held `{contact_bad_odds, enemy: Mack, location: Swabia}` — which both
    froze the new order at step 0a and was the ammunition NPC-1 needed to
    fight the wrong enemy.

    One helper, called at every seam that ends an order's life, rather than
    a widened gate — a gate is what drifted. Standalone DECISIONS
    (`last_stand`, `muster_confirm`) are never dropped: they are not bound
    to an order, and discarding one strands the marshal.

    Returns True when something was cleared (for callers that log).
    """
    pending = getattr(marshal, "pending_interrupt", None)
    if pending and pending.get("interrupt_type") in ORDER_BOUND_INTERRUPT_TYPES:
        marshal.pending_interrupt = None
        return True
    return False


# F1b fix: the strategic "attack anyway" interrupt handler rebuilds a fresh result
# dict and previously surfaced only `message`, silently dropping the top-level combat
# fields the direct /command attack path preserves. Carry the player-facing extras
# (reinforcement narration, battle report, capture prompt) onto the returned dict so
# the interrupt path is as legible as a direct attack.
_COMBAT_PASSTHROUGH_FIELDS = (
    "reinforcement_messages",
    "reinforcement_results",
    "coordination_tutorial",
    "battle_report",
    "bombardment_advisory",
    "pending_capture_choice",
    "capture_data",
    # Slice-9 review R1-3: a failed reinforcer's redemption question staged
    # on the inner attack result (FA-N1) was dropped by this allowlist on
    # the PURSUE first step and every interrupt-resolved battle — latched
    # and invisible until the next turn's poll. The key rides; main.py
    # stamps the state at the boundary (never `state` itself, which a
    # capture prompt would misroute).
    "redemption_event",
    # ────────────────────────────────────────────────────────────────────
    # CA8-25 (creative audit, Aug 4 2026): the diorama was BUILT AND THEN
    # DISCARDED on the interrupt-resolved routes.
    #
    # The audit filed this as "no diorama is built" for the `press on`
    # resolution — the played campaign's LARGEST battle, 82,072 men massed.
    # That is not what happens: every `attack_anyway` arm re-enters
    # `_execute_attack`, which sets `battle_diorama` on its result exactly
    # as it does for a normal attack. The `muster_confirm` route returns
    # that result verbatim and the payload survives; the blocked-path arms
    # here rebuild a FRESH dict through this allowlist — which deliberately
    # rewrites `message`/`order_cleared`, so returning the inner result raw
    # is not an option — and the allowlist simply never carried it.
    #
    # One tuple entry, no new machinery: the biggest battle a player can
    # fight stops being the one battle they cannot look at.
    # ────────────────────────────────────────────────────────────────────
    "battle_diorama",
    # ────────────────────────────────────────────────────────────────────
    # FA-N42 + FA-N48 (slice 3, Sept 4 2026): the first-step auto-attack's
    # success branch rebuilt a FRESH dict and dropped every one of these.
    # `events` is what `_build_result_response` pops to the top level (no
    # battle event → no diorama stash, no campaign-log row); the war-purpose
    # triad is the HARD STOP `_attach_staged_war_purpose` stamps — dropped
    # here, the client never rendered the question and the next `end turn`
    # was refused with "nothing was relayed". The copy-only-non-None rule
    # keeps every battle that stages no dialogue byte-identical.
    # ────────────────────────────────────────────────────────────────────
    "events",
    "diplomatic_dialogue",
    "awaiting_diplomatic_response",
    "war_purpose_popup",
)


def _carry_combat_fields(out: dict, inner: dict) -> dict:
    """Copy allowlisted top-level combat fields from an inner attack result."""
    if isinstance(inner, dict):
        for key in _COMBAT_PASSTHROUGH_FIELDS:
            if inner.get(key) is not None:
                out[key] = inner[key]
    return out


class StrategicOrderProcessor:
    """
    Executes strategic orders during turn processing.

    Usage:
        processor = StrategicOrderProcessor(command_executor)
        reports = processor.process_strategic_orders(world, game_state)
    """

    def __init__(self, command_executor):
        """
        Args:
            command_executor: CommandExecutor instance for action execution
        """
        self.executor = command_executor

    @staticmethod
    def _attach_redemption_if_needed(result: Dict, marshal, world) -> Dict:
        """Check redemption threshold after a trust penalty and attach to result."""
        if not (marshal and world and hasattr(world, 'disobedience_system')):
            return result
        event = world.disobedience_system.check_redemption_threshold(marshal, world)
        if event:
            result["redemption_event"] = event
            result["state"] = "awaiting_redemption_choice"
        return result

    def process_strategic_orders(self, world, game_state: Dict) -> List[Dict]:
        """
        Process strategic orders for all player marshals.

        Called at START of player's turn, AFTER enemy phase, BEFORE advance_turn().
        This timing ensures we can see battles_this_turn for cannon fire detection.

        Returns:
            List of reports for UI display
        """
        from backend.display_names import (
            humanize_entity_name as _hum,
        )

        reports = []

        print(f"[STRATEGIC] Processing orders for turn {world.current_turn}")

        # Process in deterministic order (alphabetical by name)
        marshals_with_orders = sorted(
            [m for m in world.marshals.values()
             if m.nation == world.player_nation and m.in_strategic_mode],
            key=lambda m: m.name
        )

        # Two-pass processing to prevent alphabetical starvation:
        # Pass 1: Execute all non-interrupting orders (movement, holds, etc.)
        # Pass 2: Check for interrupts and present the first one
        deferred_marshals = []

        for marshal in marshals_with_orders:
            order = marshal.strategic_order

            # ═══════════════════════════════════════════════════════════
            # PHASE M: Skip dead marshals and clear their orders
            # ═══════════════════════════════════════════════════════════
            if marshal.strength <= 0:
                marshal.strategic_order = None
                # [7A-2] Clear holding state on dead marshal
                marshal.holding_position = False
                marshal.hold_region = ""
                # [7A-8] Clear pending interrupt on dead marshal
                marshal.pending_interrupt = None
                print(f"[STRATEGIC] {marshal.name}: SKIP - marshal defeated, order cleared")
                continue

            print(f"[STRATEGIC] {marshal.name}: {order.command_type} -> {order.target} "
                  f"(issued turn {getattr(order, 'issued_turn', '?')})")

            # Skip orders issued THIS turn — first step already executed by executor.py
            issued = getattr(order, 'issued_turn', None)
            if issued is not None and issued == world.current_turn:
                print(f"[STRATEGIC] {marshal.name}: SKIP - order issued this turn")
                # Emit a status report so the player knows the order is active
                remaining = len(order.path) if order.path else 0

                # Context-appropriate message based on order type and position
                if order.command_type == "HOLD":
                    if marshal.location == order.target or not order.target:
                        msg = f"{marshal.name} is holding position at {marshal.location}."
                    else:
                        msg = f"{marshal.name} is marching to hold {order.target} ({remaining} turn(s) remaining)."
                elif order.command_type == "PURSUE":
                    # N27 (CA9): `order.target` is a raw marshal KEY, so
                    # this printed the camelCase key rather than the man.
                    # Same family as the already-filed N42 / S5-2.
                    msg = (f"{marshal.name} is pursuing "
                           f"{_hum(order.target)} "
                           f"({remaining} turn(s) remaining).")
                elif order.command_type == "SUPPORT":
                    msg = (f"{marshal.name} is moving to support "
                           f"{_hum(order.target)} "
                           f"({remaining} turn(s) remaining).")
                else:  # MOVE_TO
                    msg = f"{marshal.name} is marching to {order.target} ({remaining} turn(s) remaining)."

                reports.append({
                    "marshal": marshal.name,
                    "command": order.command_type,
                    "order_status": "active",
                    "destination": order.target,
                    "turns_remaining": int(remaining),
                    "message": msg,
                })
                continue

            # Check if this marshal would trigger an interrupt (new or pending)
            has_pending = getattr(marshal, 'pending_interrupt', None)
            new_interrupt = self._check_interrupts(marshal, world)
            if has_pending or new_interrupt:
                # Defer interrupt processing — execute non-interrupting marshals first
                deferred_marshals.append(marshal)
                continue

            report = self._execute_strategic_turn(marshal, world, game_state)
            if report:
                reports.append(report)

        # Pass 2: Process deferred marshals with interrupts.
        # FA-68 (slice 3, Sept 4 2026): this used to `break` after the first
        # report that required input, so a SECOND marshal raising a question
        # in the same end turn was never executed — no movement, no row, no
        # `pending_interrupt` stored — and the cannon fire he heard was gone
        # by next turn (`clear_turn_battles`). `_check_interrupts` is pure
        # and idempotent (probed), each marshal's step 2 latches his OWN
        # question, and the client queues every `requires_input` row, so the
        # break protected nothing.
        for marshal in deferred_marshals:
            report = self._execute_strategic_turn(marshal, world, game_state)
            if report:
                reports.append(report)

        # Pass 3 (FA-16): the decisions no order raised.
        reports.extend(self._standalone_decision_rows(world))

        return reports

    def _standalone_decision_rows(self, world) -> List[Dict]:
        """FA-16 (slice 2, Sept 4 2026): surface, or retire, the parked
        decision of every ORDER-FREE player marshal.

        The processor's roster is `in_strategic_mode` marshals only, so a
        marshal whose last stand was parked by tactical combat with no
        standing order never reached step 0a — the filed fix at `if not
        order: return None` was unreachable by construction (measured: the
        ask surfaced only on the SECOND end turn after the player happened
        to give him a strategic order). And nothing ever asked whether the
        question was still true: Ney's turn-16 question was answered on turn
        22 against an enemy three provinces away.

        A live question rides the same `requires_input` row shape step 0a
        emits — the client's report flow queues it, `main.py` promotes it
        for headless clients, the driver answers it — so no `.gd` changes.
        A dead one is retired here with its reason, and the rail row goes
        with it (FA-N68's helper). `muster_confirm` is re-validated the
        same way (review round R2-F5 — the first cut said its answer
        "re-validates itself", and it did not: see `muster_is_live`).
        """
        rows: List[Dict] = []
        if not STANDALONE_DECISION_LIVENESS_ACTIVE:
            return rows
        from backend.notifications import dismiss_marshal_ask
        for marshal in sorted(world.get_player_marshals(), key=lambda m: m.name):
            if marshal.in_strategic_mode:
                continue  # step 0a owns the order-bound roster
            pending = standalone_decision(marshal)
            if not pending:
                continue
            if marshal.strength <= 0 or getattr(marshal, "captured_by", ""):
                # Hazard-4 idiom (PC15-4): nobody can act on a question
                # about a man who no longer stands.
                marshal.pending_interrupt = None
                dismiss_marshal_ask(world, marshal.name)
                continue
            kind = pending.get("interrupt_type")
            if kind == "last_stand":
                live, reason = last_stand_is_live(marshal, world, pending)
                if not live:
                    marshal.pending_interrupt = None
                    dismiss_marshal_ask(world, marshal.name)
                    print(f"[STRATEGIC] {marshal.name}: last stand retired — {reason}")
                    rows.append({
                        "marshal": marshal.name,
                        "command": "Last stand",
                        "order_status": "retired",
                        "decision_retired": True,
                        "message": (f"{marshal.name}'s question is overtaken, "
                                    f"Sire — {reason}. He awaits new orders."),
                    })
                    continue
            elif kind == "muster_confirm":
                live, reason = muster_is_live(marshal, world, pending)
                if not live:
                    marshal.pending_interrupt = None
                    print(f"[STRATEGIC] {marshal.name}: muster retired — {reason}")
                    rows.append({
                        "marshal": marshal.name,
                        "command": "Muster",
                        "order_status": "retired",
                        "decision_retired": True,
                        "message": (f"{marshal.name}'s muster is overtaken, "
                                    f"Sire — {reason}. He stands down."),
                    })
                    continue
            rows.append({
                "marshal": marshal.name,
                "command": "Last stand" if kind == "last_stand" else "Muster",
                "order_status": "awaiting_response",
                "requires_input": True,
                "interrupt_type": kind,
                "message": (pending.get("message")
                            or f"{marshal.name} awaits your word, Sire."),
                "options": list(pending.get("options") or []),
                "pending_interrupt": pending,
            })
        return rows

    # ══════════════════════════════════════════════════════════════════════════
    # INTERRUPT RESPONSE HANDLING (Phase D)
    # ══════════════════════════════════════════════════════════════════════════

    def handle_response(self, marshal_name: str, response_type: str,
                        choice: str, world, game_state: Dict) -> Dict:
        """
        Process player's response to a strategic interrupt.

        Args:
            marshal_name: Name of the marshal with pending interrupt
            response_type: "cannon_fire", "blocked_path", "ally_moving"
            choice: Player's chosen option
            world: WorldState
            game_state: Game state dict

        Returns:
            Result dict with action taken, trust changes, order state
        """
        marshal = world.get_marshal(marshal_name)
        if not marshal:
            return {"success": False, "message": f"Marshal '{marshal_name}' not found."}

        pending = getattr(marshal, 'pending_interrupt', None)
        if not pending:
            return {"success": False,
                    "message": f"{marshal_name} has no pending interrupt."}

        # ════════════════════════════════════════════════════════════
        # W6-4 MUSTER CONFIRM (EXP-C1 + E-CA-4): a gated DIRECT attack —
        # no strategic order exists, so this branch runs BEFORE the
        # order requirement below. attack_anyway re-issues the same
        # attack with the confirmed flag (normal AP charge applies on
        # the resolved attack); cancel stands the marshal down free.
        # ════════════════════════════════════════════════════════════
        if pending.get("interrupt_type") == "muster_confirm":
            valid = pending.get("options", [])
            if choice not in valid:
                return {"success": False,
                        "message": f"Invalid choice '{choice}'. Valid: {', '.join(valid)}"}
            # Review round (R2-F5): the target may have marched, died or
            # slipped out of sight since the muster was read — retire the
            # question with the reason rather than re-issue an attack that
            # objects about a ghost.
            if STANDALONE_DECISION_LIVENESS_ACTIVE:
                live, reason = muster_is_live(marshal, world, pending)
                if not live:
                    marshal.pending_interrupt = None
                    return {"success": True, "no_action_cost": True,
                            "decision_retired": True,
                            "message": (f"{marshal.name}'s muster is overtaken, "
                                        f"Sire — {reason}. He stands down.")}
            marshal.pending_interrupt = None
            attack_target = pending.get("target", "")
            if choice == "cancel_order":
                return {
                    "success": True,
                    "no_action_cost": True,
                    "message": (
                        f"{marshal.name} stands down, Sire — the attack on "
                        f"{attack_target} is called off."
                    ),
                }
            # attack_anyway — the player has seen the muster and commits.
            return self.executor.execute(
                {"success": True,
                 "command": {"marshal": marshal.name, "action": "attack",
                             "target": attack_target,
                             "_muster_confirmed": True}},
                game_state)

        # ════════════════════════════════════════════════════════════
        # W6-7 LAST STAND (EXP-M1): a cornered aggressive marshal awaits
        # the player's word — fight to the last (one final defense at
        # +25%, the pursuit halted, survivors captured after) or attempt
        # a breakout (the escape roll at −10%). No strategic order is
        # involved, so this branch runs BEFORE the order requirement.
        # ════════════════════════════════════════════════════════════
        if pending.get("interrupt_type") == "last_stand":
            valid = pending.get("options", [])
            if choice not in valid:
                return {"success": False,
                        "message": f"Invalid choice '{choice}'. Valid: {', '.join(valid)}"}
            from backend.notifications import dismiss_marshal_ask
            # FA-16 (slice 2): the question is answered against the enemy
            # who asked it, where he asked it — or not at all. A stale ask
            # is retired here rather than fought through.
            if STANDALONE_DECISION_LIVENESS_ACTIVE:
                live, reason = last_stand_is_live(marshal, world, pending)
                if not live:
                    marshal.pending_interrupt = None
                    dismiss_marshal_ask(world, marshal.name)
                    return {"success": True, "no_action_cost": True,
                            "decision_retired": True,
                            "message": (f"{marshal.name}'s question is overtaken, "
                                        f"Sire — {reason}. He awaits new orders.")}
            marshal.pending_interrupt = None
            # PC-9: the rail notice exists only to make an UNANSWERED last
            # stand visible. It was never retired when the player answered,
            # so a turn-3 alert was still sitting in the tray at turn 42 —
            # for a marshal whose fate had been decided 39 turns earlier.
            # FA-N68: one helper now, shared with every other road a
            # question can end on.
            dismiss_marshal_ask(world, marshal.name)
            enemy = world.get_marshal(pending.get("enemy", ""))
            combat = self.executor._combat
            if choice == "fight_to_the_last":
                msg = combat._resolve_last_stand_fight(marshal, enemy, world)
                return {"success": True, "no_action_cost": True,
                        "message": msg}
            # attempt_breakout — the escape roll at −10%.
            import random
            escape_chance = (combat.MARSHAL_FATE_ESCAPE_CHANCE
                             - combat.LAST_STAND_BREAKOUT_PENALTY)
            if random.random() < escape_chance:
                # NP-4 (NAPOLEON_SPEC §7.0): the Emperor's breakout is the
                # Guard's — success still burns GUARD_ESCAPE_TOLL of the
                # corps. The squares die so the berline gets out.
                toll_note = ""
                if getattr(marshal, "is_sovereign", False):
                    toll = int(marshal.strength * combat.GUARD_ESCAPE_TOLL)
                    if toll > 0:
                        marshal.take_casualties(toll)
                    toll_note = (f" The Guard bought the road with its own "
                                 f"ranks — {toll:,} men fall covering the "
                                 f"escape.")
                # Aug 30, 2026 review: NOT `_apply_forced_retreat_or_break`.
                # This interrupt is only ever raised for an ENCIRCLED marshal
                # (the producer sets it when `get_safe_retreat_destination`
                # returns None), so that call asked the same question again,
                # got the same None, and shattered the army to 3-10% — a won
                # roll paying the toll AND the rout, under the words "cuts his
                # way out".
                msg = combat.apply_successful_breakout(marshal, enemy, world)
                return {"success": True, "no_action_cost": True,
                        "message": (f"{marshal.name} cuts his way out!"
                                    f"{toll_note} {msg}")}
            msg = combat._capture_marshal(
                marshal, getattr(enemy, "nation", "") or
                pending.get("enemy_nation", ""), world,
                context="failed_breakout")
            return {"success": True, "no_action_cost": True,
                    "message": (f"The breakout fails — {msg}")}

        order = marshal.strategic_order
        if not order:
            marshal.pending_interrupt = None
            return {"success": False,
                    "message": f"{marshal_name} has no active strategic order."}

        # Validate choice against stored options
        valid_options = pending.get("options", [])
        if choice not in valid_options:
            return {"success": False,
                    "message": f"Invalid choice '{choice}'. Valid: {', '.join(valid_options)}"}

        # Clear pending interrupt before processing
        marshal.pending_interrupt = None

        # Route to appropriate handler
        interrupt_type = pending.get("interrupt_type", response_type)

        if interrupt_type == "cannon_fire":
            return self._respond_cannon_fire(marshal, order, choice, pending, world, game_state)
        elif interrupt_type in ("contact", "contact_bad_odds", "destination_blocked"):
            return self._respond_blocked_path(marshal, order, choice, pending, world, game_state)
        elif interrupt_type == "ally_moving":
            return self._respond_ally_moving(marshal, order, choice, pending, world, game_state)
        elif interrupt_type in ("combat_stalemate", "repeated_combat"):
            return self._respond_combat_stalemate(marshal, order, choice, pending, world, game_state)
        else:
            return {"success": False,
                    "message": f"Unknown interrupt type: {interrupt_type}"}

    @staticmethod
    def _abandon_for_the_guns(marshal) -> None:
        """The cannon-fire abandonment, taken only once the guns were
        actually answered (review round R1-F1)."""
        marshal.strategic_order = None
        clear_order_bound_interrupt(marshal)  # NPC-2
        marshal.holding_position = False
        marshal.hold_region = ""

    def _respond_cannon_fire(self, marshal, order, choice, pending,
                             world, game_state) -> Dict:
        """Handle player response to cannon fire interrupt."""
        battle_location = pending.get("battle_location", "unknown")
        trust_change = 0

        if choice == "investigate":
            # Cancel current order, attack or move toward battle
            cmd_flavor = _strategic_command_flavor(order.command_type)
            # FA slice 3 review round (R1-F1): abandoned only for a battle
            # fought or a march made — see `_abandon_for_the_guns`.
            if not CANNON_FIRE_READS_THE_ANSWER:
                marshal.strategic_order = None
                # [7A-2] Clear holding state
                marshal.holding_position = False
                marshal.hold_region = ""

            # Distance-based: attack if adjacent with enemy, otherwise move
            is_cavalry = getattr(marshal, 'cavalry', False)
            attack_range = getattr(marshal, 'movement_range', 1) if is_cavalry else 1
            path_to_battle = world.find_path(marshal.location, battle_location)
            distance = len(path_to_battle) - 1 if path_to_battle else 999

            enemies_at_battle = [
                m for m in world.get_enemies_of_nation(marshal.nation)
                if m.location == battle_location and m.strength > 0
            ]

            print(f"[CANNON FIRE INVESTIGATE] {marshal.name}: distance={distance}, "
                  f"attack_range={attack_range}, enemies={[e.name for e in enemies_at_battle]}")
            print(f"[CANNON FIRE INVESTIGATE] {marshal.name}: Location BEFORE = {marshal.location}")

            if distance <= attack_range and enemies_at_battle:
                # Within range — attack!
                action_result = self.executor.execute(
                    {"command": {
                        "marshal": marshal.name,
                        "action": "attack",
                        "target": enemies_at_battle[0].name,
                        "_strategic_execution": True
                    }},
                    game_state
                )
                action_msg = action_result.get("message", "")
                print(f"[CANNON FIRE INVESTIGATE] {marshal.name}: Location AFTER = {marshal.location}")
                if CANNON_FIRE_READS_THE_ANSWER and attack_was_refused(action_result):
                    return {
                        "success": True,
                        "no_action_cost": True,
                        "message": (f"{marshal.name} cannot reach the guns at "
                                    f"{battle_location} — {refusal_reason(action_result)} "
                                    f"{cmd_flavor.capitalize()} continues."),
                        "order_cleared": False,
                        "trust_change": trust_change,
                        "action_taken": "attack_refused",
                        **refusal_keys(action_result),
                    }
                if CANNON_FIRE_READS_THE_ANSWER:
                    self._abandon_for_the_guns(marshal)
                return _carry_combat_fields({
                    "success": True,
                    "message": f"{marshal.name} abandons {cmd_flavor} and "
                               f"charges into battle at {battle_location}! {action_msg}".strip(),
                    "order_cleared": True,
                    "trust_change": trust_change,
                    "action_taken": "attack",
                    "action_events": action_result.get("events", []),
                }, action_result)
            else:
                # Too far to attack — move step-by-step toward battle
                steps = min(attack_range, distance) if distance < 999 else 0
                moved_to = None
                for i in range(steps):
                    if not path_to_battle or len(path_to_battle) < 2:
                        break
                    next_step = path_to_battle[1 + i]
                    # Check for enemies blocking the step
                    enemies_blocking = world.get_enemies_in_region(next_step, marshal.nation)
                    if enemies_blocking:
                        break
                    move_result = self.executor.execute(
                        {"command": {
                            "marshal": marshal.name,
                            "action": "move",
                            "target": next_step,
                            "_strategic_execution": True
                        }},
                        game_state
                    )
                    if move_result.get("success"):
                        moved_to = next_step
                    else:
                        break

                print(f"[CANNON FIRE INVESTIGATE] {marshal.name}: Location AFTER = {marshal.location}")
                if moved_to:
                    if CANNON_FIRE_READS_THE_ANSWER:
                        self._abandon_for_the_guns(marshal)
                    msg = (f"{marshal.name} abandons {cmd_flavor} and "
                           f"rushes toward the guns at {battle_location}! "
                           f"Moved to {moved_to}.")
                elif CANNON_FIRE_READS_THE_ANSWER:
                    # No step could be made: the order stands.
                    return {
                        "success": True,
                        "no_action_cost": True,
                        "message": (f"{marshal.name} turns toward {battle_location} but "
                                    f"cannot advance — {cmd_flavor.capitalize()} continues."),
                        "order_cleared": False,
                        "trust_change": trust_change,
                        "action_taken": "investigate_refused",
                    }
                else:
                    msg = (f"{marshal.name} abandons {cmd_flavor} and "
                           f"turns toward {battle_location}, but cannot advance yet.")
                return {
                    "success": True,
                    "message": msg,
                    "order_cleared": True,
                    "trust_change": trust_change,
                    "action_taken": "investigate"
                }

        elif choice == "continue_order":
            # Resume strategic order — marshal ignores cannon fire
            trust_change = -2  # Non-literal acting literal
            if hasattr(marshal, 'trust'):
                marshal.trust.modify(trust_change)

            # Suppress cannon fire re-trigger for 1 turn (prevents infinite loop)
            marshal.cannon_fire_ignored_turn = world.current_turn

            # Execute one movement step so the marshal actually progresses
            move_result = self._execute_movement_step(marshal, world, game_state)
            move_msg = move_result.get("message", "") if move_result else ""

            return self._attach_redemption_if_needed({
                "success": True,
                # FA-52: "continues the march" regardless of the order.
                # This was the ONLY arm in the function that did not call
                # `_strategic_command_flavor` — measured, a marshal under a
                # HOLD was told he "reluctantly continues the march" and
                # then, in the same sentence, that he fortified where he
                # stood.
                "message": f"{marshal.name} reluctantly "
                           f"{_strategic_command_flavor(order.command_type)}, "
                           f"ignoring cannon fire at {battle_location}. "
                           f"{move_msg}".strip(),
                "order_cleared": False,
                "trust_change": trust_change,
                "action_taken": "continue_order",
                "movement_executed": bool(move_result and move_result.get("success"))
            }, marshal, world)

        elif choice == "hold_position":
            # Cancel order, stay put
            cmd_flavor = _strategic_command_flavor(order.command_type)
            marshal.strategic_order = None
            # [7A-2] Clear holding state
            marshal.holding_position = False
            marshal.hold_region = ""
            trust_change = -3
            if hasattr(marshal, 'trust'):
                marshal.trust.modify(trust_change)
            return self._attach_redemption_if_needed({
                "success": True,
                "message": f"{marshal.name} halts and holds position, "
                           f"abandoning {cmd_flavor}.",
                "order_cleared": True,
                "trust_change": trust_change,
                "action_taken": "hold_position"
            }, marshal, world)

        return {"success": False, "message": f"Unknown cannon_fire choice: {choice}"}

    def _respond_blocked_path(self, marshal, order, choice, pending,
                              world, game_state) -> Dict:
        """Handle player response to blocked path (enemy contact)."""
        enemy_name = pending.get("enemy", "unknown")
        blocked_region = pending.get("location", "unknown")
        trust_change = 0

        if choice in ("attack", "attack_anyway"):
            # FA slice 3 review round (R1-F3/F4): the question may be STALE
            # — the enemy phase moved the blocker, or a peace was signed —
            # and the answer used to fight whoever the executor could find.
            if ANSWERED_CONTACT_READS_THE_BOARD:
                live, reason = contact_is_live(marshal, world, pending)
                if not live:
                    return {
                        "success": True,
                        "no_action_cost": True,
                        "decision_retired": True,
                        "message": (f"{marshal.name}'s contact is overtaken, Sire — "
                                    f"{reason}. "
                                    f"{_strategic_command_flavor(order.command_type).capitalize()} "
                                    f"continues."),
                        "order_cleared": False,
                        "trust_change": 0,
                        "action_taken": "contact_retired",
                    }
            # Attack the blocking enemy
            result = self.executor.execute(
                {"command": {
                    "marshal": marshal.name,
                    "action": "attack",
                    "target": enemy_name,
                    "_strategic_execution": True
                }},
                game_state
            )
            if attack_was_refused(result):
                # FA-15 (slice 3): the answered 'attack' the executor REFUSED
                # read "Davout attacks Moore. <barred>. Assault failed —
                # orders cancelled" — a battle that never happened, charged a
                # failed attempt. The refusal ends the order, says why, and
                # touches no combat record.
                marshal.strategic_order = None
                clear_order_bound_interrupt(marshal)  # NPC-2
                marshal.holding_position = False
                marshal.hold_region = ""
                return {
                    "success": True,
                    "message": (f"{marshal.name} cannot attack {enemy_name} — "
                                f"{refusal_reason(result)} "
                                f"{_strategic_command_flavor(order.command_type).capitalize()} "
                                f"ends; he awaits new orders."),
                    "order_cleared": True,
                    "trust_change": 0,
                    "action_taken": "attack_refused",
                    **refusal_keys(result),
                }

            combat_success = result.get("success", False)
            combat_msg = result.get("message", "")
            cmd_flavor = _strategic_command_flavor(order.command_type)

            if ANSWERED_CONTACT_READS_THE_BOARD:
                victor = fought_battle_victor(result, marshal.name)
                if victor is None:
                    # Not an assault at all — a staged dialogue, a minted
                    # order. The executor's own sentence; the order stands;
                    # no attempt is charged.
                    return _carry_combat_fields({
                        "success": True,
                        "no_action_cost": True,
                        "message": (f"{marshal.name} cannot bring {enemy_name} to "
                                    f"battle — {combat_msg}").strip(),
                        "order_cleared": False,
                        "trust_change": 0,
                        "action_taken": "attack_not_made",
                    }, result)
                if victor == "":
                    # A stalemate: the FA-34 ruling — the order stands, one
                    # attempt charged, the next contact asks again (R2-F4:
                    # this arm used to cancel where `continue_order` kept).
                    order.combat_attempts = getattr(order, 'combat_attempts', 0) + 1
                    order.last_combat_enemy = enemy_name
                    order.last_combat_turn = world.current_turn
                    return _carry_combat_fields({
                        "success": True,
                        "message": (f"{marshal.name} attacks {enemy_name}. {combat_msg} "
                                    f"The assault was inconclusive — {cmd_flavor} continues."),
                        "order_cleared": False,
                        "trust_change": 0,
                        "action_taken": "attack",
                    }, result)
                battle_victor = victor
            else:
                # Check victory: victor is in events[0] or battle_result
                battle_victor = ""
                events = result.get("events", [])
                if events and isinstance(events, list) and len(events) > 0:
                    battle_victor = events[0].get("victor", "")
                if not battle_victor:
                    battle_victor = result.get("battle_result", {}).get("victor", "")
            if combat_success and battle_victor == marshal.name:
                # Victory — reset attempts, continue order
                order.combat_attempts = 0
                return _carry_combat_fields({
                    "success": True,
                    "message": f"{marshal.name} attacks {enemy_name} and wins! "
                               f"Continuing {_strategic_command_flavor(order.command_type)}. {combat_msg}",
                    "order_cleared": False,
                    "trust_change": 0,
                    "action_taken": "attack"
                }, result)
            else:
                # Loss or stalemate — increment attempts, break order
                order.combat_attempts = getattr(order, 'combat_attempts', 0) + 1
                order.last_combat_enemy = enemy_name
                order.last_combat_turn = world.current_turn
                marshal.strategic_order = None
                # [7A-2] Clear holding state
                marshal.holding_position = False
                marshal.hold_region = ""
                return _carry_combat_fields({
                    "success": True,
                    "message": f"{marshal.name} attacks {enemy_name}. {combat_msg} "
                               f"Assault failed — orders cancelled, marshal awaits new instructions.",
                    "order_cleared": True,
                    "trust_change": 0,
                    "action_taken": "attack"
                }, result)

        elif choice == "go_around":
            # Recalculate path avoiding ALL enemy regions (not just the one)
            # NPC-5 (review round): ONE source, shared with the
            # executor's first-step copy — see `resolve_order_destination`.
            destination = resolve_order_destination(world, marshal, order)
            enemy_regions = self._get_enemy_occupied_regions(
                marshal.nation, world, marshal=marshal)
            # MOVE_TO and HOLD use weighted pathfinding for terrain-aware rerouting
            use_weighted = (order.command_type in ("MOVE_TO", "HOLD"))
            if ROAD_LAW_ON_REPLOT:
                # FA slice 5: a reroute prefers a lawful corridor and must
                # still AVOID what it fled (it used to be terrain-only).
                new_path, _ = plot_route(
                    world, marshal, destination, use_weighted=use_weighted,
                    avoid_regions=enemy_regions, avoid_is_law=True)
            else:
                pathfinder = world.find_weighted_path if use_weighted else world.find_path
                new_path = pathfinder(
                    marshal.location, destination,
                    avoid_regions=enemy_regions
                )
                new_path = ([r for r in new_path if r != marshal.location]
                            if new_path else None)
            if new_path:
                order.path = list(new_path)
                # Execute one movement step along the new path
                move_result = self._execute_movement_step(marshal, world, game_state)
                move_msg = move_result.get("message", "") if move_result else ""
                return {
                    "success": True,
                    "message": f"{marshal.name} reroutes around {blocked_region}. {move_msg}".strip(),
                    "order_cleared": False,
                    "trust_change": 0,
                    "action_taken": "go_around",
                    "movement_executed": bool(move_result and move_result.get("success"))
                }
            else:
                # No safe path exists — break order
                marshal.strategic_order = None
                # [7A-2] Clear holding state
                marshal.holding_position = False
                marshal.hold_region = ""
                return {
                    "success": True,
                    "message": f"No safe route around {blocked_region}. "
                               f"Orders cancelled.",
                    "order_cleared": True,
                    "trust_change": 0,
                    "action_taken": "go_around_failed"
                }

        elif choice == "hold_position":
            marshal.strategic_order = None
            # [7A-2] Clear holding state
            marshal.holding_position = False
            marshal.hold_region = ""
            # First-step cancel = 0 trust penalty (order never really started)
            is_first_step = pending.get("is_first_step", False)
            trust_change = 0 if is_first_step else -3
            if trust_change != 0 and hasattr(marshal, 'trust'):
                marshal.trust.modify(trust_change)
            return self._attach_redemption_if_needed({
                "success": True,
                "message": f"{marshal.name} holds position, "
                           f"abandoning {_strategic_command_flavor(order.command_type)}.",
                "order_cleared": True,
                "trust_change": trust_change,
                "action_taken": "hold_position"
            }, marshal, world)

        elif choice == "cancel_order":
            marshal.strategic_order = None
            # [7A-2] Clear holding state
            marshal.holding_position = False
            marshal.hold_region = ""
            # First-step cancel = 0 trust penalty (order never really started)
            is_first_step = pending.get("is_first_step", False)
            trust_change = 0 if is_first_step else -3
            if trust_change != 0 and hasattr(marshal, 'trust'):
                marshal.trust.modify(trust_change)
            return self._attach_redemption_if_needed({
                "success": True,
                "message": f"{marshal.name} cancels {_strategic_command_flavor(order.command_type)}.",
                "order_cleared": True,
                "trust_change": trust_change,
                "action_taken": "cancel_order"
            }, marshal, world)

        return {"success": False, "message": f"Unknown blocked_path choice: {choice}"}

    def _respond_ally_moving(self, marshal, order, choice, pending,
                             world, game_state) -> Dict:
        """Handle player response to supported ally moving."""
        ally_name = pending.get("ally", order.target)
        trust_change = 0

        if choice == "follow":
            # Update path to ally's new location and execute movement
            ally = world.get_marshal(ally_name)
            if ally:
                new_path = self._get_personality_aware_path(
                    marshal, ally.location, world)
                if new_path:
                    order.path = new_path
                    # Execute one movement step along the new path
                    move_result = self._execute_movement_step(marshal, world, game_state)
                    move_msg = move_result.get("message", "") if move_result else ""
                    return {
                        "success": True,
                        "message": f"{marshal.name} adjusts course to follow "
                                   f"{ally_name} to {ally.location}. {move_msg}".strip(),
                        "order_cleared": False,
                        "trust_change": 0,
                        "action_taken": "follow",
                        "movement_executed": bool(move_result and move_result.get("success"))
                    }
            return {
                "success": True,
                "message": f"{marshal.name} cannot reach {ally_name}. "
                           f"Holding position.",
                "order_cleared": False,
                "trust_change": 0,
                "action_taken": "follow_failed"
            }

        elif choice == "hold_current":
            # Pause — wait for ally to return or new orders
            return {
                "success": True,
                "message": f"{marshal.name} holds current position, "
                           f"awaiting {ally_name}'s return.",
                "order_cleared": False,
                "trust_change": 0,
                "action_taken": "hold_current"
            }

        elif choice == "cancel_support":
            marshal.strategic_order = None
            # [7A-2] Clear holding state
            marshal.holding_position = False
            marshal.hold_region = ""
            trust_change = -3
            if hasattr(marshal, 'trust'):
                marshal.trust.modify(trust_change)
            return self._attach_redemption_if_needed({
                "success": True,
                "message": f"{marshal.name} abandons reinforcement orders for {ally_name}.",
                "order_cleared": True,
                "trust_change": trust_change,
                "action_taken": "cancel_support"
            }, marshal, world)

        return {"success": False, "message": f"Unknown ally_moving choice: {choice}"}

    def _respond_combat_stalemate(self, marshal, order, choice, pending,
                                   world, game_state) -> Dict:
        """Handle player response to combat stalemate or repeated combat interrupt."""
        enemy_name = pending.get("enemy", pending.get("target", order.target))

        if choice in ("continue_order", "attack_again"):
            # FA-34 (slice 3, Sept 4 2026): the client labels this button
            # "Continue as Ordered" and it CANCELLED the order — the one
            # free-looking answer was the one that threw the march away
            # (measured: the same "march to London" re-issued three turns
            # later created a fresh order). The order now STANDS; the loop
            # guard it was pretending to be already exists —
            # `order.combat_attempts` + `_should_auto_attack` stop a free
            # re-attack on the same man, and the next contact asks with the
            # "Previous assault was inconclusive" copy.
            return {
                "success": True,
                "message": (f"{marshal.name} presses on — "
                            f"{_strategic_command_flavor(order.command_type)} "
                            f"continues."),
                "order_cleared": False,
                "trust_change": 0,
                "action_taken": choice
            }

        elif choice == "hold_position":
            marshal.strategic_order = None
            # [7A-2] Clear holding state
            marshal.holding_position = False
            marshal.hold_region = ""
            trust_change = -3
            if hasattr(marshal, 'trust'):
                marshal.trust.modify(trust_change)
            return self._attach_redemption_if_needed({
                "success": True,
                "message": f"{marshal.name} holds position after the engagement with {enemy_name}.",
                "order_cleared": True,
                "trust_change": trust_change,
                "action_taken": "hold_position"
            }, marshal, world)

        elif choice == "cancel_order":
            marshal.strategic_order = None
            # [7A-2] Clear holding state
            marshal.holding_position = False
            marshal.hold_region = ""
            trust_change = -3
            if hasattr(marshal, 'trust'):
                marshal.trust.modify(trust_change)
            return self._attach_redemption_if_needed({
                "success": True,
                "message": f"{marshal.name} abandons the order and awaits new instructions.",
                "order_cleared": True,
                "trust_change": trust_change,
                "action_taken": "cancel_order"
            }, marshal, world)

        return {"success": False, "message": f"Unknown combat_stalemate choice: {choice}"}

    # ══════════════════════════════════════════════════════════════════════════
    # CORE EXECUTION FLOW
    # ══════════════════════════════════════════════════════════════════════════

    def _retire_dead_decision(self, marshal, world, order) -> Optional[Dict]:
        """Step 0a's liveness arm for a standalone decision parked on an
        ORDERED marshal: retire a dead one with its reason (the order
        stands and resumes next turn), or None when it is live / absent /
        the lever is down."""
        if not STANDALONE_DECISION_LIVENESS_ACTIVE:
            return None
        pending = standalone_decision(marshal)
        if not pending:
            return None
        # `standalone_decision` guarantees one of the two standalone types
        # (an order-bound interrupt returns None above) — the sweep found
        # a third arm here unreachable, so there is none.
        kind = pending.get("interrupt_type")
        if kind == "last_stand":
            live, reason = last_stand_is_live(marshal, world, pending)
            noun = "question"
        else:
            live, reason = muster_is_live(marshal, world, pending)
            noun = "muster"
        if live:
            return None
        from backend.notifications import dismiss_marshal_ask
        marshal.pending_interrupt = None
        if kind == "last_stand":
            dismiss_marshal_ask(world, marshal.name)
        print(f"[STRATEGIC] {marshal.name}: {kind} retired under a standing order — {reason}")
        return {
            "marshal": marshal.name,
            "command": order.command_type,
            "order_status": "retired",
            "decision_retired": True,
            "message": (f"{marshal.name}'s {noun} is overtaken, Sire — {reason}. "
                        f"His standing order resumes next turn."),
        }

    def _execute_strategic_turn(self, marshal, world, game_state) -> Optional[Dict]:
        """Execute one turn of a marshal's strategic order."""
        order = marshal.strategic_order
        if not order:
            return None

        # 0a. If marshal has a pending interrupt awaiting player response, skip execution
        if getattr(marshal, 'pending_interrupt', None):
            # Review round (R1-F3 / R2-F4): an ORDERED marshal's parked
            # decision was re-surfaced here every turn and never
            # re-validated — pass 3 skips him (`in_strategic_mode`), so a
            # dead question froze a live order behind a stale popup. The
            # standalone types take the same liveness pass 3 runs.
            retired = self._retire_dead_decision(marshal, world, order)
            if retired is not None:
                return retired
            return {
                "marshal": marshal.name,
                "command": order.command_type,
                "order_status": "awaiting_response",
                "requires_input": True,
                "interrupt_type": marshal.pending_interrupt.get("interrupt_type"),
                # FA-N60 (slice 3): the question's OWN line when the stored
                # ask carries one — the popup body is what the marshal said,
                # not a placeholder.
                "message": (marshal.pending_interrupt.get("message")
                            or f"{marshal.name} awaits your orders."),
                "options": marshal.pending_interrupt.get("options", []),
                "pending_interrupt": marshal.pending_interrupt,
            }

        # 0b. Block execution during retreat recovery (MOVE_TO always allowed — movement isn't blocked)
        recovery = getattr(marshal, 'retreat_recovery', 0)
        if recovery > 0:
            should_pause = True
            if order.command_type in ("MOVE_TO", "SUPPORT"):
                should_pause = False  # Movement-based orders continue during recovery
                print(f"[STRATEGIC] {marshal.name}: {order.command_type} continues despite recovery (movement allowed)")
            # PURSUE and HOLD pause (need to attack/fortify)

            if should_pause:
                print(f"[STRATEGIC] {marshal.name}: PAUSED - retreat recovery ({recovery} turns left)")
                return {
                    "marshal": marshal.name,
                    "command": order.command_type,
                    "order_status": "paused",
                    "message": f"{marshal.name} is recovering from retreat "
                               f"({recovery} turn(s) remaining). Order paused."
                }

        # [7A-7] Removed dead code: aggressive HOLD expiry was duplicated here
        # and in _execute_hold(). The _execute_hold handler handles all personalities.

        # 1b. Check conditions first (until_arrives, until_relieved, etc.)
        if order.condition:
            met, reason = self._check_condition(marshal, order.condition, world)
            if met:
                return self._complete_order(marshal, world, reason)

        # 2. Check for interrupts (cannon fire — LITERAL NEVER INTERRUPTS)
        interrupt = self._check_interrupts(marshal, world)
        if interrupt:
            response = self._handle_interrupt(marshal, interrupt, world, game_state)
            if response:
                # Store pending interrupt if it requires player input
                # Only set if handler didn't already set it (e.g., _handle_combat_result sets it directly)
                if response.get("requires_input") and not getattr(marshal, 'pending_interrupt', None):
                    marshal.pending_interrupt = response
                return response

        # 3. Execute command-specific logic
        handlers = {
            "MOVE_TO": self._execute_move_to,
            "PURSUE": self._execute_pursue,
            "HOLD": self._execute_hold,
            "SUPPORT": self._execute_support,
        }

        handler = handlers.get(order.command_type)
        if handler:
            result = handler(marshal, world, game_state)
            # Store pending interrupt if handler result requires player input
            # Only set if handler didn't already set it (e.g., _handle_combat_result sets it directly)
            if result and result.get("requires_input") and not getattr(marshal, 'pending_interrupt', None):
                marshal.pending_interrupt = result
            return result

        return {
            "marshal": marshal.name,
            "command": order.command_type,
            "order_status": "error",
            "message": f"Unknown strategic command: {order.command_type}"
        }

    # ══════════════════════════════════════════════════════════════════════════
    # MOVE_TO HANDLER
    # ══════════════════════════════════════════════════════════════════════════

    def _execute_move_to(self, marshal, world, game_state) -> Dict:
        """
        Execute one turn of MOVE_TO.

        Moves marshal along path toward destination.
        Cavalry moves 2 regions/turn, infantry moves 1.
        """
        order = marshal.strategic_order

        # Determine destination (marshal snapshot or region)
        destination = order.target_snapshot_location or order.target

        # Check arrival
        if marshal.location == destination:
            return self._handle_move_to_arrival(marshal, world, game_state)

        # Check if engaged with enemy in CURRENT region (e.g., after advancing into enemy on victory)
        enemies_here = world.get_enemies_in_region(marshal.location, marshal.nation)
        if enemies_here:
            return self._handle_blocked_path(
                marshal, enemies_here, marshal.location, world, game_state)

        # Ensure path exists (calculate or recalculate if empty)
        if not order.path or order.path[0] == marshal.location:
            # Strip current location from path if present
            while order.path and order.path[0] == marshal.location:
                order.path.pop(0)

            if not order.path:
                new_path = self._get_personality_aware_path(
                    marshal, destination, world, use_weighted=True)
                if new_path:
                    order.path = new_path
                else:
                    return self._break_order(marshal, world,
                                             f"No path to {destination}")

        if (STALE_ROAD_REPLOTS and order.path
                and not region_is_adjacent(world, marshal.location, order.path[0])):
            # FA slice 5: a road whose first step is not one march away is
            # STALE (a forced retreat, a stored reroute from another province)
            # — handing it to `move` used to reach the auto-upgrade, which
            # minted a NEW order to path[0] and silently lost the destination.
            new_path = self._get_personality_aware_path(
                marshal, destination, world, use_weighted=True)
            if new_path:
                order.path = new_path
            else:
                return self._break_order(marshal, world,
                                         f"No path to {destination}")

        if not order.path:
            return self._break_order(marshal, world, f"No path to {destination}")

        # Move up to movement_range regions
        regions_to_move = getattr(marshal, 'movement_range', 1)
        moves_made = []
        last_fail = None  # PF-8: remember why the last step failed (for feedback)
        print(f"[STRATEGIC MOVE] {marshal.name}: {marshal.location} -> {destination}, "
              f"cavalry={getattr(marshal, 'cavalry', False)}, "
              f"movement_range={regions_to_move}, path={order.path}")

        for _ in range(regions_to_move):
            if not order.path:
                break

            if marshal.location == destination:
                break

            next_region = order.path[0]

            # Check for enemies blocking the next region
            enemies = world.get_enemies_in_region(next_region, marshal.nation)
            if enemies:
                if not moves_made:  # First move blocked
                    blocked_result = self._handle_blocked_path(
                        marshal, enemies, next_region, world, game_state)
                    # If literal reroute, try to move on the new path this turn
                    if blocked_result and blocked_result.get("action") == "reroute":
                        if order.path:
                            rerouted_next = order.path[0]
                            rerouted_enemies = world.get_enemies_in_region(
                                rerouted_next, marshal.nation)
                            if not rerouted_enemies:
                                move_result = self.executor.execute(
                                    {"command": {
                                        "marshal": marshal.name,
                                        "action": "move",
                                        "target": rerouted_next,
                                        "_strategic_execution": True
                                    }}, game_state)
                                if move_result.get("success"):
                                    order.path.pop(0)
                                    moves_made.append(rerouted_next)
                                    blocked_result["message"] += (
                                        f" Moves to {rerouted_next}.")
                                    blocked_result["regions_moved"] = moves_made
                    return blocked_result
                else:
                    break  # Moved some, stop at blockage

            # Execute move through executor (skip objections + action cost)
            result = self.executor.execute(
                {"command": {
                    "marshal": marshal.name,
                    "action": "move",
                    "target": next_region,
                    "_strategic_execution": True
                }},
                game_state
            )

            if result.get("success"):
                order.path.pop(0)
                moves_made.append(next_region)
                print(f"[STRATEGIC] {marshal.name}: moved -> {next_region} "
                      f"(path remaining: {order.path})")
            else:
                last_fail = result  # PF-8: preserve the reason (e.g. diplomatic block)
                break

        # Transit intel: regions passed through but not ended at get PARTIAL
        if len(moves_made) > 1 and marshal.nation == world.player_nation:
            for transit_region in moves_made[:-1]:
                world.update_intel_from_transit(transit_region, world.current_turn)

        # Check if we arrived after moving
        if marshal.location == destination:
            return self._handle_move_to_arrival(marshal, world, game_state)

        if moves_made:
            remaining = len(order.path)
            return {
                "marshal": marshal.name,
                "command": "MOVE_TO",
                "order_status": "continues",
                "regions_moved": moves_made,
                "destination": destination,
                "turns_remaining": int(remaining),
                "message": f"{marshal.name} marches to {moves_made[-1]}. "
                           f"{remaining} region(s) to {destination}."
            }

        # PF-8: a stall on a DIPLOMATIC block used to return a content-free
        # "could not advance" and re-stall silently every turn. Say why — and
        # stop the eternal re-stall. First try one passability-aware reroute; if
        # that still can't take a first step, break the order with the reason.
        # DEF-5 naval §4.1 (the same idiom): a march stalled at a covered
        # strait breaks with the honest naval reason. FA slice 5: ONE copy,
        # `_stall_verdict`, shared with HOLD and SUPPORT.
        stalled = self._stall_verdict(
            marshal, order, world, last_fail, destination,
            verb="MOVE_TO", allow_reroute=True, use_weighted=True)
        if stalled is not None:
            return stalled

        return {
            "marshal": marshal.name,
            "command": "MOVE_TO",
            "order_status": "error",
            "message": f"{marshal.name} could not advance toward {destination}."
        }

    def _stall_verdict(self, marshal, order, world, last_fail, destination,
                       *, verb: str, allow_reroute: bool, use_weighted: bool,
                       toward: str = None, lapse_note: str = "") -> Optional[Dict]:
        """PF-8's stall idiom — ONE copy for MOVE_TO, HOLD and SUPPORT (FA
        slice 5). A step refused on a DIPLOMATIC block tries one lawful
        reroute, else BREAKS the order naming the reason; a step refused at a
        covered strait breaks at the water's edge (the pathfinders are
        edge-blind, so a reroute would plan the same crossing again). Returns
        None when the stall was neither — the caller keeps its own fallback.
        `lapse_note` lets SUPPORT say that its march-to-the-guns
        authorization lapses with the order. MOVE_TO's output is byte-for-
        byte what its inline copy produced."""
        toward = toward or destination
        if last_fail is not None and last_fail.get("blocked_diplomatic"):
            if allow_reroute:
                reroute = self._get_personality_aware_path(
                    marshal, destination, world, use_weighted=use_weighted)
                if reroute and len(reroute) > 1:
                    first_step = reroute[1] if reroute[0] == marshal.location else reroute[0]
                    if not world.get_enemies_in_region(first_step, marshal.nation) \
                            and world._region_passable_for(
                                first_step, marshal.nation,
                                mover_location=marshal.location):
                        order.path = reroute[1:] if reroute[0] == marshal.location else reroute
                        return {
                            "marshal": marshal.name,
                            "command": verb,
                            "order_status": "continues",
                            "destination": destination,
                            "message": (f"{marshal.name} reroutes around "
                                        f"{last_fail.get('blocked_diplomatic')} territory "
                                        f"toward {toward}."),
                        }
            reason = last_fail.get("message") or (
                f"the road to {toward} is blocked by "
                f"{last_fail.get('blocked_diplomatic')} territory")
            return self._break_order(
                marshal, world,
                f"{marshal.name}'s march halts — {reason} "
                f"Secure open borders or declare war to pass.{lapse_note}")

        if last_fail is not None and last_fail.get("blocked_naval"):
            reason = last_fail.get("message") or (
                f"hostile sail command the crossing toward {toward}")
            return self._break_order(
                marshal, world,
                f"{marshal.name}'s march halts at the water's edge — {reason}{lapse_note}")
        return None

    def _inferred_attack_gate(self, marshal, target, game_state,
                              allow_reroute=False):
        """CR-5 Phase 3 (COMMAND_ROBUSTNESS_SPEC §6.3c, "TWO SEAMS, not one"):
        for a DELEGATION-INFERRED order, block a fortification-blind auto-attack
        on a dug-in superior force behind the SAME one-modal bad-odds confirm the
        adjacent first-step case uses. Returns an interrupt result dict (and
        latches ``marshal.pending_interrupt`` so the per-turn processor surfaces
        it) when the gate fires; None otherwise.

        ``allow_reroute``: whether "go_around" is offered. At a co-located /
        attack-ON-arrival seam the marshal is ALREADY at the target's location,
        so rerouting "around" it is nonsensical (an empty reroute that loops back
        into this very gate) — those callers leave it False; only the mid-path
        blocked seam (marshal still en route) passes True.

        Explicitly-typed orders are NEVER gated — the player named the attack.
        Single source for every attack-on-arrival seam in this processor."""
        order = marshal.strategic_order
        if order is None or not getattr(order, "delegation_inferred", False):
            return None
        from backend.commands.objection_v2 import inferred_attack_favorable
        if inferred_attack_favorable(marshal, target, game_state):
            return None
        from backend.commands.delegation import describe_inferred_bad_odds
        # Track contact so _handle_blocked_path's top-level same-enemy suppression
        # (which prevents an infinite interrupt loop when a persistent enemy
        # blocks the path) also covers a gate-produced interrupt.
        world = game_state.get("world") if isinstance(game_state, dict) else None
        if world is not None:
            order.last_contact_enemy = target.name
            order.last_contact_turn = world.current_turn
        if allow_reroute:
            options = ["attack_anyway", "go_around", "hold_position",
                       "cancel_order"]
        else:
            options = ["attack_anyway", "hold_position", "cancel_order"]
        # PC-8: the marshal's read stays solo; Berthier names the muster.
        gate_msg = describe_inferred_bad_odds(
            marshal.name, target.name,
            self.executor._combat._bad_odds_muster_note(
                marshal, target, world))
        marshal.pending_interrupt = {
            # The frontend interrupt popup answers via /strategic_response, which
            # needs the marshal name; the SYNCHRONOUS response.pending_interrupt
            # path (main.gd) reads it from this stored dict (the enemy-phase
            # report list carries it at top level). Without it the popup sends
            # the literal "Marshal" and handle_response 404s. Serialized with the
            # dict, so a save/load mid-interrupt keeps it.
            "marshal": marshal.name,
            "interrupt_type": "contact_bad_odds",
            "enemy": target.name,
            "location": marshal.location,
            "is_first_step": False,
            "options": options,
            # FA-N60 (slice 3): the popup reads THIS dict on the synchronous
            # route and after /load — without the line it rendered "Awaiting
            # your orders, Sire." while the marshal's real sentence was
            # thrown away.
            "message": gate_msg,
        }
        return {
            "marshal": marshal.name,
            "command": order.command_type,
            "order_status": "awaiting_response",
            "requires_input": True,
            "interrupt_type": "contact_bad_odds",
            "enemy": target.name,
            "location": marshal.location,
            "message": gate_msg,
            "options": options,
        }

    def _handle_move_to_arrival(self, marshal, world, game_state) -> Dict:
        """Handle arrival at MOVE_TO destination."""
        order = marshal.strategic_order

        # Check attack_on_arrival
        if order.attack_on_arrival:
            enemies = world.get_enemies_in_region(marshal.location, marshal.nation)
            if enemies:
                target = enemies[0]
                # CR-5 Phase 3: an inferred attack-on-arrival into a fortified
                # superior force routes through the one-modal confirm before it
                # commits (§6.3c). Explicit orders fall straight through.
                gate = self._inferred_attack_gate(marshal, target, game_state)
                if gate is not None:
                    return gate
                result = self.executor.execute(
                    {"command": {
                        "marshal": marshal.name,
                        "action": "attack",
                        "target": target.name,
                        "_strategic_execution": True
                    }},
                    game_state
                )

                if attack_was_refused(result):
                    # FA slice 3 review round (R3-S1): the THIRTEENTH
                    # order-driven attack seam, unread by slice 3 and filed by
                    # its own census among the "answer arms". Fed a refusal it
                    # narrated "arrives at X and attacks Y!" and consumed the
                    # order — FA-14 exactly. `attack_on_arrival` is stamped by
                    # the typed out-of-range `attack <marshal>` route, so this
                    # is a player path. The refusal breaks the order with its
                    # reason, like every other seam.
                    broken = self._break_order(
                        marshal, world,
                        f"{marshal.name} arrives at {marshal.location} but cannot "
                        f"attack {target.name} — {refusal_reason(result)}")
                    broken.update({"action": "attack_refused", **refusal_keys(result)})
                    return broken
                msg = f"{marshal.name} arrives at {marshal.location} and attacks {target.name}!"
                self._complete_order(marshal, world, msg)
                # Strip new_state to avoid circular reference in JSON serialization
                cleaned_result = {k: v for k, v in result.items() if k != "new_state"} if result else None
                return {
                    "marshal": marshal.name,
                    "command": "MOVE_TO",
                    "action": "attack_on_arrival",
                    "target": target.name,
                    "combat_result": cleaned_result,
                    "order_status": "completed",
                    "message": msg,
                    # R2-F7: the fought battle's tableau and report ride the row.
                    **_combat_carry(result),
                }

        # Check if this was a marshal target
        if order.target_type == "marshal" and order.target_snapshot_location:
            target_marshal = world.get_marshal(order.target)
            if target_marshal and target_marshal.location == marshal.location:
                message = (f"{marshal.name} arrives at {marshal.location}. "
                           f"{order.target} is here.")
            else:
                current = target_marshal.location if target_marshal else "unknown"
                message = (f"{marshal.name} arrives at {marshal.location}. "
                           f"{order.target} has moved on - now at {current}.")
        else:
            message = f"{marshal.name} arrives at {order.target}."

        return self._complete_order(marshal, world, message)

    # ══════════════════════════════════════════════════════════════════════════
    # PURSUE HANDLER
    # ══════════════════════════════════════════════════════════════════════════

    def _pursuit_engagement(self, marshal, world, target, result) -> Dict:
        """FA slice 3: the four PURSUE attack seams completed the pursuit with
        whatever the executor said — a REFUSED attack (the crossing gate)
        "completed" it with the refusal as the reason and the aggressive
        completion line appended: "…barred… 'Done — and I trust the next order
        has more fire in it.'" A refusal ends the pursuit with its reason
        instead; a fought battle completes it as it always did."""
        if attack_was_refused(result):
            reason = refusal_reason(result)
            if result.get("blocked_naval"):
                text = (f"{marshal.name}'s pursuit halts at the water's edge — "
                        f"{reason}")
            else:
                text = f"{marshal.name} cannot engage {target.name} — {reason}"
            broken = self._break_order(marshal, world, text)
            broken.update({"action": "attack_refused", "target": target.name,
                           **refusal_keys(result)})
            return broken
        combat_msg = result.get("message", f"Engaged {target.name}")
        return self._complete_order(marshal, world, combat_msg)

    def _execute_pursue(self, marshal, world, game_state) -> Dict:
        """
        Execute one turn of PURSUE.

        Dynamically tracks enemy each turn (recalculates path).
        Attacks when in same region. Completes when target destroyed.

        FOG OF WAR (Session 34B): PURSUE reads the target's location from the
        intel store (last known position), NOT from raw marshal data. This is
        the core fog change. Pathfinding heads toward last known location.
        Physical co-location checks (same region) use real data because the
        marshal is physically there — that's a discovery, not intelligence.
        """
        from backend.display_names import humanize_entity_name

        order = marshal.strategic_order
        target = world.get_marshal(order.target)

        # ═══════════════════════════════════════════════════════════
        # FOG OF WAR: Resolve target location from intel store
        # Real target object used for co-location and combat only
        # ═══════════════════════════════════════════════════════════
        is_player_marshal = (marshal.nation == world.player_nation)
        if is_player_marshal:
            last_known = world.get_last_known_location(order.target)
        else:
            # AI is omniscient (spec §9.1)
            last_known = (target.location, world.current_turn, "full") if target and target.strength > 0 else None

        # ═══════════════════════════════════════════════════════════
        # PHASE M: Cautious PURSUE ratio check
        # Auto-cancel if odds drop below threshold
        # Uses real data — this is a MECHANIC decision, not display
        # ═══════════════════════════════════════════════════════════
        if order.condition and order.condition.auto_cancel_below_ratio:
            if target and target.strength > 0:
                ratio = marshal.strength / max(target.strength, 1)
                threshold = order.condition.auto_cancel_below_ratio
                if ratio < threshold:
                    marshal.strategic_order = None
                    # [7A-2] Clear holding state
                    marshal.holding_position = False
                    marshal.hold_region = ""
                    return {
                        "success": True,
                        "marshal": marshal.name,
                        "order_status": "cancelled",
                        "message": f"{marshal.name} breaks off pursuit of {order.target} — the odds have turned against us.",
                        "ratio_cancelled": True,
                    }

        # Fix 13: Break PURSUE if peace signed with target's nation
        if target and not world.is_at_war(marshal.nation, target.nation):
            return self._break_order(marshal, world,
                                     f"Peace with {target.nation} — pursuit cancelled")

        # Target destroyed — or TAKEN. Aug 30, 2026 review: `strength <= 0`
        # is satisfied by two different fates, and the project distinguishes
        # them everywhere else — a W6-7 prisoner stays in `world.marshals` at
        # strength 0 with `captured_by` set. So a marshal who ran his quarry
        # down and captured him was told the man was "destroyed", and the
        # sentence interpolated `order.target`, which is the raw scenario KEY
        # ("ArchdukeCharles"), the exact NPC-12 shape.
        if not target or target.strength <= 0:
            from backend.display_names import humanize_entity_name
            _quarry = humanize_entity_name(
                getattr(target, "name", None) or str(order.target))
            _fate = "destroyed"
            if target is not None and getattr(target, "captured_by", ""):
                _fate = "taken prisoner"
            return self._complete_order(marshal, world,
                                        f"{_quarry} {_fate}")

        # ═══════════════════════════════════════════════════════════
        # FOG OF WAR: No intelligence on target -> reject PURSUE
        # Player marshal with zero intel cannot pursue
        # ═══════════════════════════════════════════════════════════
        if is_player_marshal and not last_known:
            return self._break_order(marshal, world,
                # N27 (CA9), unfiled sibling found while pinning the
                # PURSUE prose: this is the line the player actually
                # meets, and it named the raw key —
                # "No intelligence on ArchdukeCharles's position, Sire."
                f"No intelligence on "
                f"{humanize_entity_name(str(order.target))}'s position, "
                f"Sire.")

        # Same region? Engage and complete (physical encounter — real data).
        if marshal.location == target.location:
            # Already fought this target recently — order is done
            if not self._should_auto_attack(marshal, target, world):
                return self._complete_order(marshal, world,
                    f"{marshal.name} engaged {target.name} — pursuit complete")

            # CR-5 Phase 3: gate an inferred assault on a fortified superior
            # force behind the one-modal confirm (§6.3c).
            gate = self._inferred_attack_gate(marshal, target, game_state)
            if gate is not None:
                return gate

            result = self.executor.execute(
                {"command": {
                    "marshal": marshal.name,
                    "action": "attack",
                    "target": target.name,
                    "_strategic_execution": True
                }},
                game_state
            )

            # Combat happened — pursuit is complete regardless of outcome
            # (a REFUSED attack is not combat — see the helper).
            return self._pursuit_engagement(marshal, world, target, result)

        # Check if engaged with a different enemy in current region
        enemies_here = world.get_enemies_in_region(marshal.location, marshal.nation)
        if enemies_here:
            # Filter out the pursuit target — we handle that above
            non_target_enemies = [e for e in enemies_here if e.name != order.target]
            if non_target_enemies:
                return self._handle_blocked_path(
                    marshal, non_target_enemies, marshal.location, world, game_state)

        # ═══════════════════════════════════════════════════════════
        # FOG OF WAR: Pathfind toward last known location (not real location)
        # Player marshals head toward intel; AI uses real position
        # ═══════════════════════════════════════════════════════════
        pursue_destination = last_known[0] if last_known else target.location
        path = self._get_personality_aware_path(marshal, pursue_destination, world)
        if path:
            order.path = list(path)  # Persist for ledger display
        if not path:
            return self._break_order(marshal, world,
                                     f"Cannot reach {order.target}")

        # Move up to movement_range
        regions_to_move = getattr(marshal, 'movement_range', 1)
        moves_made = []
        last_fail = None  # PF-8: remember why the last pursue step failed

        for _ in range(regions_to_move):
            if not path:
                break

            next_region = path[0]

            # Check for enemies blocking the path (omniscient — physical encounter)
            enemies = world.get_enemies_in_region(next_region, marshal.nation)
            blocking = [e for e in enemies if e.name != order.target]

            # If this is the target's REAL region, don't treat other enemies as blockers
            is_target_region = (next_region == target.location)

            if blocking and not is_target_region:
                if not moves_made:
                    blocked_result = self._handle_blocked_path(
                        marshal, blocking, next_region, world, game_state)
                    # If literal reroute, try to move on the new path this turn
                    if blocked_result and blocked_result.get("action") == "reroute":
                        if order.path:
                            rerouted_next = order.path[0]
                            rerouted_enemies = world.get_enemies_in_region(
                                rerouted_next, marshal.nation)
                            if not rerouted_enemies:
                                move_result = self.executor.execute(
                                    {"command": {
                                        "marshal": marshal.name,
                                        "action": "move",
                                        "target": rerouted_next,
                                        "_strategic_execution": True
                                    }}, game_state)
                                if move_result.get("success"):
                                    order.path.pop(0)
                                    moves_made.append(rerouted_next)
                                    blocked_result["message"] += (
                                        f" Moves to {rerouted_next}.")
                                    blocked_result["regions_moved"] = moves_made
                    return blocked_result
                break

            # Target's region — pursuit complete, attack if personality allows
            if is_target_region and enemies:
                personality = getattr(marshal, 'personality', 'balanced')
                attack_on_arrival = getattr(order, 'attack_on_arrival', False)
                if personality == "aggressive" or attack_on_arrival:
                    # CR-5 Phase 3: gate an inferred assault on a fortified
                    # superior force behind the one-modal confirm (§6.3c).
                    gate = self._inferred_attack_gate(marshal, target, game_state)
                    if gate is not None:
                        return gate
                    attack_result = self.executor.execute(
                        {"command": {
                            "marshal": marshal.name,
                            "action": "attack",
                            "target": target.name,
                            "_strategic_execution": True
                        }},
                        game_state
                    )
                    return self._pursuit_engagement(marshal, world, target, attack_result)
                else:
                    # Cautious/literal: found the enemy, pursuit complete
                    return self._complete_order(marshal, world,
                        f"{marshal.name} has located {target.name} at {next_region} and awaits orders")

            result = self.executor.execute(
                {"command": {
                    "marshal": marshal.name,
                    "action": "move",
                    "target": next_region,
                    "_strategic_execution": True
                }},
                game_state
            )

            if result.get("success"):
                path.pop(0)
                moves_made.append(next_region)

                # Did we catch up? Physical encounter — real data.
                if marshal.location == target.location:
                    if self._should_auto_attack(marshal, target, world):
                        # CR-5 Phase 3: gate an inferred assault (§6.3c).
                        gate = self._inferred_attack_gate(marshal, target, game_state)
                        if gate is not None:
                            return gate
                        attack_result = self.executor.execute(
                            {"command": {
                                "marshal": marshal.name,
                                "action": "attack",
                                "target": target.name,
                                "_strategic_execution": True
                            }},
                            game_state
                        )
                        return self._pursuit_engagement(marshal, world, target, attack_result)
                    # Already fought recently — pursuit still complete
                    return self._complete_order(marshal, world,
                        f"{marshal.name} has engaged {target.name} — pursuit complete")
            else:
                # Move failed — if target is in this region, pursuit complete
                if next_region == target.location:
                    personality = getattr(marshal, 'personality', 'balanced')
                    attack_on_arrival = getattr(order, 'attack_on_arrival', False)
                    if personality == "aggressive" or attack_on_arrival:
                        if self._should_auto_attack(marshal, target, world):
                            # CR-5 Phase 3: gate an inferred assault (§6.3c).
                            gate = self._inferred_attack_gate(marshal, target, game_state)
                            if gate is not None:
                                return gate
                            attack_result = self.executor.execute(
                                {"command": {
                                    "marshal": marshal.name,
                                    "action": "attack",
                                    "target": target.name,
                                    "_strategic_execution": True
                                }},
                                game_state
                            )
                            return self._pursuit_engagement(marshal, world, target, attack_result)
                    # Found target — pursuit complete
                    return self._complete_order(marshal, world,
                        f"{marshal.name} has located {target.name} at {next_region} and awaits orders")
                last_fail = result  # PF-8: preserve the reason (e.g. diplomatic block)
                break

        # Transit intel: regions passed through but not ended at get PARTIAL
        if len(moves_made) > 1 and marshal.nation == world.player_nation:
            for transit_region in moves_made[:-1]:
                world.update_intel_from_transit(transit_region, world.current_turn)

        # ═══════════════════════════════════════════════════════════
        # FOG OF WAR: Empty arrival — target not at last known location
        # Marshal arrived at the intel destination but target moved
        # ═══════════════════════════════════════════════════════════
        if moves_made and is_player_marshal and marshal.location == pursue_destination:
            # Arrived at last-known position but target isn't here
            if marshal.location != target.location:
                # Check adjacent for enemies (physical presence = mini-refresh)
                region = world.get_region(marshal.location)
                enemies_adjacent = []
                if region:
                    for adj in region.adjacent_regions:
                        adj_enemies = world.get_enemies_in_region(adj, marshal.nation)
                        enemies_adjacent.extend(adj_enemies)

                intel_age = world.current_turn - last_known[1] if last_known else 0

                if not enemies_adjacent:
                    # No enemies nearby — auto-cancel, log target_not_found
                    target_not_found_event = {
                        "type": "target_not_found",
                        "marshal": marshal.name,
                        "target": order.target,
                        "region": marshal.location,
                        "intel_age": int(intel_age),
                    }
                    if hasattr(world, '_last_tactical_events'):
                        world._last_tactical_events.append(target_not_found_event)
                    return self._break_order(marshal, world,
                        f"{marshal.name} arrives at {marshal.location} but finds no sign of "
                        f"{order.target}. Last intelligence was {intel_age} turn(s) old. "
                        f"Awaiting orders, Sire.")
                # Enemies adjacent — existing personality contact vectors handle
                # The marshal stays in position; PURSUE continues with fresh intel next turn

        if moves_made:
            # Use pursue_destination for distance (what the marshal is heading toward)
            distance = world.get_distance(marshal.location, pursue_destination)
            return {
                "marshal": marshal.name,
                "command": "PURSUE",
                "order_status": "continues",
                "regions_moved": moves_made,
                "target": order.target,
                "target_location": pursue_destination,
                "distance": int(distance),
                "message": f"{marshal.name} pursues {order.target}. "
                           f"{distance} region(s) away."
            }

        # PF-8: a PURSUE stalled on a DIPLOMATIC block used to return a
        # content-free "could not advance" and re-stall silently every turn. Say
        # why and break the order (mirrors the MOVE_TO stall-feedback). Pursuit
        # doesn't pick scenic reroutes, so there is no reroute step here — a
        # closed border simply ends the chase with a clear reason.
        if last_fail is not None and last_fail.get("blocked_diplomatic"):
            reason = last_fail.get("message") or (
                f"the road to {order.target} is blocked by "
                f"{last_fail.get('blocked_diplomatic')} territory")
            return self._break_order(
                marshal, world,
                f"{marshal.name}'s pursuit halts — {reason} "
                f"Secure open borders or declare war to pass.")

        # DEF-5 naval §4.1: a pursuit ends at a covered strait with the
        # honest reason (the quarry has the sea at its back).
        if last_fail is not None and last_fail.get("blocked_naval"):
            reason = last_fail.get("message") or (
                f"hostile sail command the crossing toward {order.target}")
            return self._break_order(
                marshal, world,
                f"{marshal.name}'s pursuit halts at the water's edge — {reason}")

        return {
            "marshal": marshal.name,
            "command": "PURSUE",
            "order_status": "error",
            "message": f"{marshal.name} could not advance toward {order.target}."
        }

    # ══════════════════════════════════════════════════════════════════════════
    # HOLD HANDLER
    # ══════════════════════════════════════════════════════════════════════════

    def _execute_hold(self, marshal, world, game_state) -> Dict:
        """
        Execute one turn of HOLD.

        Personality-specific behavior:
        - AGGRESSIVE: Sally out to attack adjacent enemies, RETURN after
        - CAUTIOUS: Auto-fortify, passive defense
        - LITERAL: Immovable (+15% defense via holding_position), NEVER leaves
        - SOVEREIGN: holds, and only holds — see below.
        """
        order = marshal.strategic_order
        personality = marshal.personality
        hold_position = order.target

        # ═══════════════════════════════════════════════════════════
        # PHASE M: Timed HOLD expiry check
        # Auto-expire after max_turns (compromise from objection)
        # ═══════════════════════════════════════════════════════════
        if order.condition and order.condition.max_turns:
            issued_turn = order.issued_turn or order.started_turn
            turns_elapsed = world.current_turn - issued_turn
            if turns_elapsed >= order.condition.max_turns:
                marshal.strategic_order = None
                marshal.holding_position = False
                marshal.hold_region = ""
                # Personality-appropriate expiry message
                if personality == "aggressive":
                    msg = f"{marshal.name} grows restless and abandons the position at {hold_position}."
                elif personality == "cautious":
                    msg = f"{marshal.name} has held {hold_position} for the agreed duration. Awaiting new orders."
                elif personality == "literal":
                    msg = f"{marshal.name} reports: Hold order complete. {order.condition.max_turns} turns elapsed at {hold_position}."
                else:
                    msg = f"{marshal.name} completes the timed hold at {hold_position}. Ready for new orders."
                return {
                    "success": True,
                    "marshal": marshal.name,
                    "order_status": "expired",
                    "message": msg,
                    "timed_expiry": True,
                }

        # Not at hold position yet? Move there first
        if marshal.location != hold_position:
            # Check if engaged with enemy in current region
            enemies_here = world.get_enemies_in_region(marshal.location, marshal.nation)
            if enemies_here:
                return self._handle_blocked_path(
                    marshal, enemies_here, marshal.location, world, game_state)

            # Use weighted pathfinding — march to hold position avoids expensive terrain
            last_fail = None  # FA slice 5: the step's refusal, for the stall verdict
            if HOLD_KEEPS_ITS_ROAD:
                # FA slice 5 (FA-N11/N12/N49): HOLD used to re-plot its road
                # from scratch every turn, terrain-only — every reroute a
                # literal marshal made was thrown away on the next tick and a
                # lawful corridor was never chosen. Keep `order.path`; re-plot
                # (lawful-first, cautious fog-aware — the MOVE_TO idiom) only
                # when it is empty or its first step is not one march away.
                path = list(order.path or [])
                while path and path[0] == marshal.location:
                    path.pop(0)
                if not path or not region_is_adjacent(world, marshal.location, path[0]):
                    path = self._get_personality_aware_path(
                        marshal, hold_position, world, use_weighted=True) or []
            else:
                path = world.find_weighted_path(marshal.location, hold_position)
                path = [r for r in path if r != marshal.location] if path else []
            if path:
                order.path = path  # Persist path on order for UI/reroute
                if path:
                    # Move up to movement_range (cavalry moves 2, infantry 1)
                    regions_to_move = getattr(marshal, 'movement_range', 1)
                    moves_made = []

                    for _ in range(regions_to_move):
                        if not path:
                            break
                        if marshal.location == hold_position:
                            break

                        next_region = path[0]
                        enemies = world.get_enemies_in_region(next_region, marshal.nation)
                        if enemies:
                            if not moves_made:
                                return self._handle_blocked_path(
                                    marshal, enemies, next_region, world, game_state)
                            break

                        result = self.executor.execute(
                            {"command": {
                                "marshal": marshal.name,
                                "action": "move",
                                "target": next_region,
                                "_strategic_execution": True
                            }},
                            game_state
                        )

                        if result.get("success"):
                            path.pop(0)
                            moves_made.append(next_region)
                        else:
                            last_fail = result  # FA slice 5: keep the reason
                            break

                    if marshal.location == hold_position:
                        # Arrived, will execute hold behavior next turn
                        return {
                            "marshal": marshal.name,
                            "command": "HOLD",
                            "action": "arriving",
                            "location": marshal.location,
                            "order_status": "continues",
                            "message": f"{marshal.name} arrives at {hold_position} to hold."
                        }
                    elif moves_made:
                        distance = world.get_distance(marshal.location, hold_position)
                        return {
                            "marshal": marshal.name,
                            "command": "HOLD",
                            "action": "moving_to_position",
                            "order_status": "continues",
                            "message": f"{marshal.name} moves toward {hold_position}. "
                                       f"{distance} region(s) away."
                        }

            if HOLD_KEEPS_ITS_ROAD:
                # FA-N12/N49: a stall at a closed border reroutes once or
                # breaks WITH its reason — never the bare "Cannot reach".
                stalled = self._stall_verdict(
                    marshal, order, world, last_fail, hold_position,
                    verb="HOLD", allow_reroute=True, use_weighted=True)
                if stalled is not None:
                    return stalled
            return self._break_order(marshal, world,
                                     f"Cannot reach {hold_position}")

        # ═══════════════════════════════════════════════════════════════
        # AT HOLD POSITION — Check unit type first
        # ═══════════════════════════════════════════════════════════════

        # Artillery HOLD: auto-bombard adjacent enemies instead of sally/fortify
        if getattr(marshal, 'artillery', False):
            return self._execute_hold_bombardment(marshal, world, game_state)

        # ═══════════════════════════════════════════════════════════════
        # AT HOLD POSITION — Personality-specific behavior
        # ═══════════════════════════════════════════════════════════════

        if personality == "literal":
            # IMMOVABLE: +15% defense, never leaves, never sallies
            marshal.holding_position = True
            marshal.hold_region = marshal.location
            return {
                "marshal": marshal.name,
                "command": "HOLD",
                "action": "hold_immovable",
                "location": marshal.location,
                "order_status": "continues",
                "message": f"{marshal.name} holds {marshal.location} with iron discipline. "
                           f"[Immovable: +15% defense]"
            }

        elif personality == "cautious":
            # Auto-fortify if not already at max
            if not getattr(marshal, 'fortified', False):
                self.executor.execute(
                    {"command": {
                        "marshal": marshal.name,
                        "action": "fortify",
                        "_strategic_execution": True
                    }},
                    game_state
                )

            return {
                "marshal": marshal.name,
                "command": "HOLD",
                "action": "hold_fortify",
                "location": marshal.location,
                "order_status": "continues",
                "message": f"{marshal.name} fortifies {marshal.location}."
            }

        elif getattr(marshal, "is_sovereign", False):
            # ⚠ NP promise audit (Aug 15, 2026). Before this arm the
            # sovereign fell through to the `else:  # aggressive` branch
            # below and SALLIED OUT unordered: reproduced through the real
            # player path — "Napoleon, hold Paris" answered "Holding
            # position", and the next turn reported *"Napoleon sallies
            # forth to attack Mack, then returns to Paris!"* with the Guard
            # down 10,000 → 9,737. The Emperor committed his army to a
            # battle the player never ordered, on a verb whose whole
            # meaning is "stay put", and the loss path from there runs into
            # §7's capture machinery.
            #
            # This is exactly the class §3.1's mandated sweep exists to
            # find — an `else:` arm authored for another personality that a
            # sovereign silently executes. He is the player's own hand
            # (§2 pillar 1): HOLD means hold. He keeps the ordinary
            # defensive posture without the literal's Immovable bonus,
            # which is a marshal's trait, not a rule of the game.
            return {
                "marshal": marshal.name,
                "command": "HOLD",
                "action": "hold_position",
                "location": marshal.location,
                "order_status": "continues",
                "message": (f"The Emperor holds {marshal.location}. "
                            f"He will not move until you say so.")
            }

        else:  # aggressive (and balanced/loyal)
            # Evaluate ALL adjacent enemies to find best sally target
            # Priority: best strength ratio → lowest morale (tiebreaker)
            region = world.get_region(marshal.location)
            sally_candidates = []
            if region:
                for adj_name in region.adjacent_regions:
                    for enemy in world.get_enemies_in_region(adj_name, marshal.nation):
                        ratio = marshal.strength / max(1, enemy.strength)
                        if (ratio >= 1.0
                                and self._should_auto_attack(marshal, enemy, world)
                                # FA-N40 (slice 3): a shore the executor will
                                # refuse is not a sally target — the same
                                # predicate `_execute_attack` applies, asked
                                # first, so the sortie is never re-attempted
                                # every turn against the Royal Navy.
                                and strike_crossing_verdict(world, marshal, adj_name) is None):
                            sally_candidates.append((enemy, adj_name, ratio))

            if sally_candidates:
                # Best ratio first (easiest kill), then lowest morale (most likely to break)
                sally_candidates.sort(key=lambda c: (-c[2], c[0].morale))
                enemy, adj_name, ratio = sally_candidates[0]

                # SALLY: Attack adjacent enemy directly, then return if advanced.
                #
                # IMPORTANT: Do NOT try move→attack→return pattern here!
                # The executor blocks move() into enemy-occupied regions, so
                # the move always fails silently, combat_result stays None,
                # and battle details never reach the frontend. This bug was
                # found 4 times before the root cause was identified.
                # The executor's _execute_attack() already handles attacking
                # adjacent enemies from the marshal's current position.
                combat_result = self.executor.execute(
                    {"command": {
                        "marshal": marshal.name,
                        "action": "attack",
                        "target": enemy.name,
                        "_strategic_execution": True,
                        "_sortie": True
                    }},
                    game_state
                )

                if attack_was_refused(combat_result):
                    # FA-N40 / FA-N26 (slice 3): a REFUSED sortie was narrated
                    # "sallies forth to attack Moore, then returns to
                    # Normandy!" every turn, with the refusal printed under
                    # it as the battle line. The artillery twin
                    # (`_execute_hold_bombardment`) had the honest arm;
                    # this is that arm.
                    return {
                        "marshal": marshal.name,
                        "command": "HOLD",
                        "action": "hold_active",
                        "location": marshal.location,
                        "order_status": "continues",
                        "message": (f"{marshal.name} holds {marshal.location} — "
                                    f"{refusal_reason(combat_result)}"),
                        **refusal_keys(combat_result),
                    }

                # Step 3: Return to hold position
                if marshal.location != hold_position:
                    self.executor.execute(
                        {"command": {
                            "marshal": marshal.name,
                            "action": "move",
                            "target": hold_position,
                            "_strategic_execution": True
                        }},
                        game_state
                    )

                # Extract combat details for UI display
                # CRITICAL: Strip new_state from combat_result — contains circular
                # references (WorldState) that crash JSON serialization and silently
                # drop the entire strategic_reports from the API response.
                sally_outcome = ""
                battle_message = ""
                cleaned_combat = None
                is_glorious_charge = False
                if combat_result:
                    cleaned_combat = {k: v for k, v in combat_result.items() if k != "new_state"}
                    is_glorious_charge = cleaned_combat.get("glorious_charge", False)
                    for evt in cleaned_combat.get("events", []):
                        if evt.get("type") == "battle":
                            sally_outcome = evt.get("outcome", "")
                            break
                        elif evt.get("type") == "glorious_charge":
                            sally_outcome = "victory" if evt.get("attacker_won") else "defeat"
                            break
                    battle_message = cleaned_combat.get("message", "")

                sally_action = "glorious_charge_sally" if is_glorious_charge else "sally"
                sally_msg = (f"{marshal.name} leads a GLORIOUS CHARGE against "
                             f"{enemy.name}, then returns to {hold_position}!"
                             if is_glorious_charge else
                             f"{marshal.name} sallies forth to attack "
                             f"{enemy.name}, then returns to {hold_position}!")

                return {
                    "marshal": marshal.name,
                    "command": "HOLD",
                    "action": sally_action,
                    "target": enemy.name,
                    "outcome": sally_outcome,
                    "battle_message": battle_message,
                    "battle_details": cleaned_combat,
                    # WO-33: uniform with the combat rows.
                    "battle_report": (cleaned_combat or {}).get("battle_report"),
                    "glorious_charge": is_glorious_charge,
                    "returned_to": hold_position,
                    "order_status": "continues",
                    "message": sally_msg
                }

            # No sally opportunity — hold actively
            return {
                "marshal": marshal.name,
                "command": "HOLD",
                "action": "hold_active",
                "location": marshal.location,
                "order_status": "continues",
                "message": f"{marshal.name} holds {marshal.location}, ready to strike."
            }

    # ══════════════════════════════════════════════════════════════════════════
    # ARTILLERY HOLD BOMBARDMENT
    # ══════════════════════════════════════════════════════════════════════════

    def _execute_hold_bombardment(self, marshal, world, game_state) -> Dict:
        """
        Artillery-specific HOLD: auto-bombard adjacent enemies.

        Replaces personality-specific HOLD behavior for artillery marshals.
        Fires once per turn (cautious), free (strategic execution), picks
        target by personality-based priority.

        See BOMBARDMENT_SPEC.md §9.
        """
        order = marshal.strategic_order
        hold_position = order.target or marshal.location
        personality = getattr(marshal, 'personality', 'cautious')

        # Check if enemy is in same region — HOLD breaks
        enemies_here = world.get_enemies_in_region(marshal.location, marshal.nation)
        if enemies_here:
            enemy_names = ", ".join(e.name for e in enemies_here[:3])
            marshal.strategic_order = None
            marshal.holding_position = False
            marshal.hold_region = ""
            return {
                "marshal": marshal.name,
                "command": "HOLD",
                "action": "hold_broken_contact",
                "order_status": "cancelled",
                "message": f"{marshal.name} reports: enemy forces ({enemy_names}) have "
                           f"entered {marshal.location}! Requesting orders."
            }

        # Check if already fired max this turn (strategic + manual share limit)
        if getattr(marshal, 'bombardments_this_turn', 0) >= 2:
            return {
                "marshal": marshal.name,
                "command": "HOLD",
                "action": "hold_artillery_spent",
                "order_status": "continues",
                "message": f"{marshal.name}'s guns have already fired today. Maintaining position at {hold_position}."
            }

        # Find adjacent enemies
        region = world.get_region(marshal.location)
        if not region:
            return self._hold_no_targets(marshal, hold_position)

        targets = []
        for adj_name in region.adjacent_regions:
            for enemy in world.get_enemies_in_region(adj_name, marshal.nation):
                if enemy.strength > 0 and not getattr(enemy, 'broken', False) and not getattr(enemy, 'retreating', False):
                    targets.append(enemy)

        if not targets:
            return self._hold_no_targets(marshal, hold_position)

        # Select target by personality
        if personality == "cautious":
            # Crack forts first, then biggest army
            targets.sort(key=lambda t: (-getattr(t, 'defense_bonus', 0), -t.strength))
        elif personality == "aggressive":
            # Finish the weak first
            targets.sort(key=lambda t: t.strength)
        else:  # literal
            # Same target as last time if possible
            locked = getattr(order, 'bombardment_target', None)
            if locked:
                locked_targets = [t for t in targets if t.name == locked]
                if locked_targets:
                    targets = locked_targets

        target = targets[0]

        # Store target lock for consistency
        order.bombardment_target = target.name

        # Fire via executor (strategic execution = free, no AP cost)
        result = self.executor.execute(
            {"command": {
                "marshal": marshal.name,
                "action": "attack",
                "target": target.name,
                "_strategic_execution": True,
            }},
            game_state
        )

        # Build report — strip new_state to prevent serialization crash
        cleaned = {k: v for k, v in result.items() if k != "new_state"} if result else {}

        # Check if executor succeeded (could fail if marshal is broken, acted, etc.)
        if not cleaned.get("success"):
            return {
                "marshal": marshal.name,
                "command": "HOLD",
                "action": "hold_artillery_ready",
                "order_status": "continues",
                "message": f"{marshal.name} maintains readiness at {hold_position}. "
                           f"{cleaned.get('message', 'Unable to fire.')}",
            }

        # Extract bombardment details for the strategic report
        bombardment_result = cleaned.get("bombardment_result")
        bombardment_advisory = cleaned.get("bombardment_advisory")
        battle_message = cleaned.get("message", "")

        report = {
            "marshal": marshal.name,
            "command": "HOLD",
            "action": "hold_bombardment",
            "target": target.name,
            "order_status": "continues",
            "battle_details": cleaned,
            # WO-33: uniform with the combat rows.
            "battle_report": cleaned.get("battle_report"),
            "message": f"{marshal.name}'s guns bombard {target.name}'s position from {hold_position}. {battle_message}".strip(),
        }

        # Pass through bombardment_result and advisory for frontend
        if bombardment_result:
            report["bombardment_result"] = bombardment_result
        if bombardment_advisory:
            report["bombardment_advisory"] = bombardment_advisory

        return report

    def _hold_no_targets(self, marshal, hold_position: str) -> Dict:
        """Return status when artillery HOLD has no valid targets."""
        return {
            "marshal": marshal.name,
            "command": "HOLD",
            "action": "hold_artillery_ready",
            "order_status": "continues",
            "message": f"{marshal.name} maintains readiness at {hold_position}. No targets in range."
        }

    # ══════════════════════════════════════════════════════════════════════════
    # SUPPORT HANDLER
    # ══════════════════════════════════════════════════════════════════════════

    def _execute_support(self, marshal, world, game_state) -> Dict:
        """
        Execute one turn of SUPPORT.

        Moves to ally's location. Follows if ally moves.
        Cautious asks before following a moving ally.
        Completes when ally is safe or battle won.
        """
        order = marshal.strategic_order
        ally = world.get_marshal(order.target)

        # Fix 13: Break SUPPORT if war declared with ally's nation
        if ally and world.is_at_war(marshal.nation, ally.nation):
            return self._break_order(marshal, world,
                                     f"War with {ally.nation} — support cancelled")

        # Ally destroyed?
        if not ally or ally.strength <= 0:
            return self._break_order(marshal, world,
                                     f"{order.target} has fallen")

        # With ally?
        if marshal.location == ally.location:
            # Record arrival turn for timed SUPPORT (so timer counts from arrival, not issuance)
            if order.arrived_turn is None:
                order.arrived_turn = world.current_turn

            # Check if battle_won condition met
            if order.condition and order.condition.until_battle_won:
                if getattr(ally, 'last_combat_result', None) == "victory":
                    return self._complete_order(marshal, world,
                                                f"{ally.name} won the battle!")

            # Check if ally is safe (no adjacent enemies the player can see)
            # FOG OF WAR (Session 34B): Only report enemies the player can see.
            # If enemies are hidden in fog, SUPPORT cannot assess safety.
            # Fog filters information, not mechanics.
            ally_safe = True
            is_player_support = (marshal.nation == world.player_nation)
            region = world.get_region(ally.location)
            if region:
                for adj in region.adjacent_regions:
                    if is_player_support:
                        if world.get_visible_enemies_in_region(adj, ally.nation):
                            ally_safe = False
                            break
                    else:
                        if world.get_enemies_in_region(adj, ally.nation):
                            ally_safe = False
                            break
                # Also check current region
                if is_player_support:
                    if world.get_visible_enemies_in_region(ally.location, ally.nation):
                        ally_safe = False
                else:
                    if world.get_enemies_in_region(ally.location, ally.nation):
                        ally_safe = False

            # Only auto-complete on ally_safe if no explicit max_turns set.
            # When player said "support for N turns", honor the full duration.
            has_explicit_duration = (order.condition and order.condition.max_turns)
            if ally_safe and not has_explicit_duration:
                return self._complete_order(marshal, world,
                                            f"{ally.name} is secure")

            # Stay with ally
            return {
                "marshal": marshal.name,
                "command": "SUPPORT",
                "action": "supporting",
                "ally": ally.name,
                "location": marshal.location,
                "order_status": "continues",
                "message": f"{marshal.name} supports {ally.name} at {ally.location}."
            }

        # Not with ally — move toward them

        # Check if engaged with enemy in current region
        enemies_here = world.get_enemies_in_region(marshal.location, marshal.nation)
        if enemies_here:
            return self._handle_blocked_path(
                marshal, enemies_here, marshal.location, world, game_state)

        # Auto-follow: when ally is moving, SUPPORT silently follows.
        # No popup — supporting marshal just tracks ally's position each turn.
        # This replaces the old cautious "ally_moving" interrupt that created
        # annoying repeated popups every turn.

        # Move toward ally
        path = self._get_personality_aware_path(marshal, ally.location, world)
        if not path:
            return self._break_order(marshal, world,
                                     f"Cannot reach {ally.name}")

        order.path = path  # Fix 1: Persist path on order for UI/reroute
        regions_to_move = getattr(marshal, 'movement_range', 1)
        moves_made = []
        last_fail = None  # FA slice 5 (FA-N41): the step's refusal, kept

        for _ in range(regions_to_move):
            if not path:
                break

            next_region = path[0]
            enemies = world.get_enemies_in_region(next_region, marshal.nation)

            if enemies:
                if not moves_made:
                    return self._handle_blocked_path(
                        marshal, enemies, next_region, world, game_state)
                break

            result = self.executor.execute(
                {"command": {
                    "marshal": marshal.name,
                    "action": "move",
                    "target": next_region,
                    "_strategic_execution": True
                }},
                game_state
            )

            if result.get("success"):
                order.path.pop(0)
                path = order.path  # Keep local ref in sync
                moves_made.append(next_region)

                if marshal.location == ally.location:
                    break
            else:
                last_fail = result  # FA slice 5 (FA-N41): keep the reason
                break

        # Transit intel: regions passed through but not ended at get PARTIAL
        if len(moves_made) > 1 and marshal.nation == world.player_nation:
            for transit_region in moves_made[:-1]:
                world.update_intel_from_transit(transit_region, world.current_turn)

        if moves_made:
            # Record arrival if we reached the ally this turn
            if marshal.location == ally.location and order.arrived_turn is None:
                order.arrived_turn = world.current_turn

            distance = world.get_distance(marshal.location, ally.location)
            return {
                "marshal": marshal.name,
                "command": "SUPPORT",
                "order_status": "continues",
                "regions_moved": moves_made,
                "ally": ally.name,
                "distance": int(distance),
                "message": f"{marshal.name} moves to support {ally.name}. "
                           f"{distance} region(s) away."
            }

        if SUPPORT_STALL_SPEAKS:
            # FA-N41: PF-8's stall idiom never reached SUPPORT — a first step
            # refused at a closed border or a covered strait re-stalled
            # "could not move toward" every turn, for ever, the order (and
            # the W6-4 march-to-the-guns authorization it carries) standing.
            stalled = self._stall_verdict(
                marshal, order, world, last_fail, ally.location,
                verb="SUPPORT", allow_reroute=True, use_weighted=False,
                toward=ally.name,
                lapse_note=(f" The standing authorization to march to "
                            f"{ally.name}'s guns lapses with it."))
            if stalled is not None:
                return stalled
        return {
            "marshal": marshal.name,
            "command": "SUPPORT",
            "order_status": "error",
            "message": f"{marshal.name} could not move toward {ally.name}."
        }

    # ══════════════════════════════════════════════════════════════════════════
    # MOVEMENT HELPER (used by interrupt response handlers)
    # ══════════════════════════════════════════════════════════════════════════

    def _execute_movement_step(self, marshal, world, game_state) -> Optional[Dict]:
        """
        Execute one movement step for a marshal's current strategic order.

        Called after interrupt responses (continue_order, go_around) to ensure
        the marshal actually progresses rather than staying stuck in place.
        Returns the movement handler result with "success" key normalized.
        """
        order = marshal.strategic_order
        if not order:
            return None

        handlers = {
            "MOVE_TO": self._execute_move_to,
            "PURSUE": self._execute_pursue,
            "HOLD": self._execute_hold,
            "SUPPORT": self._execute_support,
        }
        handler = handlers.get(order.command_type)
        if handler:
            result = handler(marshal, world, game_state)
            if result:
                # Normalize: strategic handlers use order_status, not success
                status = result.get("order_status", "")
                if "success" not in result:
                    result["success"] = status in ("continues", "completed")
            return result
        return None

    # ══════════════════════════════════════════════════════════════════════════
    # INTERRUPT SYSTEM (Cannon Fire Detection)
    # ══════════════════════════════════════════════════════════════════════════

    def _check_interrupts(self, marshal, world) -> Optional[Dict]:
        """
        Check for events that interrupt strategic execution.

        ═══════════════════════════════════════════════════════════════════
        THE GROUCHY MOMENT: Literal personality NEVER interrupts
        This is THE defining characteristic — he follows orders EXACTLY.
        Even when cannon fire is heard 2 regions away at Waterloo...
        ═══════════════════════════════════════════════════════════════════
        """
        personality = marshal.personality

        # LITERAL NEVER GETS INTERRUPTED BY CANNON FIRE
        if personality == "literal":
            return None

        # Skip cannon fire if marshal recently chose "continue" (suppress for 1 turn)
        ignored_turn = getattr(marshal, 'cannon_fire_ignored_turn', None)
        if ignored_turn is not None and ignored_turn >= world.current_turn - 1:
            return None

        # Check for nearby battles (cannon fire)
        nearby_battles = world.get_battles_within_range(marshal.location, 2)

        for battle in nearby_battles:
            # Skip battles we're involved in
            if (battle.get("attacker") == marshal.name or
                    battle.get("defender") == marshal.name):
                continue

            if personality == "aggressive":
                # Aggressive rushes toward battle
                return {
                    "type": "cannon_fire",
                    "action": "redirect",
                    "battle_location": battle["location"],
                    "message": f"Cannon fire at {battle['location']}! "
                               f"Rushing to join!"
                }
            else:
                # Cautious (and balanced/loyal) asks player
                return {
                    "type": "cannon_fire",
                    "action": "ask",
                    "battle_location": battle["location"],
                    "message": f"Cannon fire heard from {battle['location']}. "
                               f"Investigate?"
                }

        return None

    def _handle_interrupt(self, marshal, interrupt, world, game_state) -> Optional[Dict]:
        """Handle an interrupt event."""
        if interrupt["type"] == "cannon_fire":
            order = marshal.strategic_order

            if interrupt["action"] == "redirect":
                # Aggressive auto-redirects — cancel current order, move/attack toward battle
                battle_loc = interrupt["battle_location"]
                cmd_type = order.command_type if order else "unknown"
                # FA slice 3 review round (R1-F1/F2, R2-F3): the order is
                # no longer cleared HERE. Clearing it before the attack meant
                # a REFUSED attack (an engaged corps, a shut crossing) destroyed
                # a live order for nothing — and, with `in_strategic_mode`
                # False, a recklessness-3 cavalryman armed a CHARGE popup the
                # end-turn wire cannot carry (WO-25's shape). The order stands
                # while the executor answers; it is abandoned below only for a
                # battle actually fought or a march actually made.
                if not CANNON_FIRE_READS_THE_ANSWER:
                    marshal.strategic_order = None
                    # [7A-2] Clear holding state
                    marshal.holding_position = False
                    marshal.hold_region = ""

                # Distance-based response: attack if in range, otherwise move toward
                is_cavalry = getattr(marshal, 'cavalry', False)
                attack_range = getattr(marshal, 'movement_range', 1) if is_cavalry else 1
                path_to_battle = world.find_path(marshal.location, battle_loc)
                distance = len(path_to_battle) - 1 if path_to_battle else 999

                enemies_at_battle = [
                    m for m in world.get_enemies_of_nation(marshal.nation)
                    if m.location == battle_loc and m.strength > 0
                ]

                print(f"[STRATEGIC INTERRUPT] {marshal.name}: Cannon fire at {battle_loc}")
                print(f"[STRATEGIC INTERRUPT]   Distance={distance}, cavalry={is_cavalry}, "
                      f"attack_range={attack_range}")
                print(f"[STRATEGIC INTERRUPT]   Enemies present={bool(enemies_at_battle)}")

                action_taken = "redirect"
                action_result = {}

                if distance <= attack_range and enemies_at_battle:
                    # Within attack range AND enemy present — ATTACK
                    print(f"[STRATEGIC INTERRUPT] {marshal.name}: Within attack range, attacking!")
                    action_taken = "attack"
                    action_result = self.executor.execute(
                        {"command": {
                            "action": "attack",
                            "marshal": marshal.name,
                            "target": enemies_at_battle[0].name,
                            "_strategic_execution": True,
                        }},
                        game_state
                    )
                elif distance > 0 and path_to_battle and len(path_to_battle) > 1:
                    # Move toward battle (one step for infantry, up to movement_range for cavalry)
                    steps = min(attack_range, len(path_to_battle) - 1)
                    print(f"[STRATEGIC INTERRUPT] {marshal.name}: Rushing toward battle "
                          f"({distance} away, {steps} step(s))")
                    action_taken = "move"
                    for i in range(steps):
                        next_region = path_to_battle[1 + i]
                        step_result = self.executor.execute(
                            {"command": {
                                "marshal": marshal.name,
                                "action": "move",
                                "target": next_region,
                                "_strategic_execution": True,
                            }},
                            game_state
                        )
                        if not step_result.get("success"):
                            break
                        action_result = step_result

                # Extract only safe serializable fields from action result
                action_success = action_result.get("success", False)
                action_events = action_result.get("events", [])
                action_msg = action_result.get("message", "")

                if CANNON_FIRE_READS_THE_ANSWER:
                    flavor = _strategic_command_flavor(cmd_type) if order else "his orders"
                    answered = ((action_taken == "attack"
                                 and not attack_was_refused(action_result))
                                or (action_taken == "move" and action_success))
                    if not answered:
                        # The guns go unanswered; the order STANDS.
                        reason = (refusal_reason(action_result) if action_result
                                  else "no road leads there.")
                        return {
                            "marshal": marshal.name,
                            "command": cmd_type,
                            "interrupt": "cannon_fire",
                            "interrupt_type": "cannon_fire",
                            "action_taken": ("attack_refused" if action_taken == "attack"
                                             else "redirect_refused"),
                            "action_success": False,
                            "action_events": [],
                            "battle_location": battle_loc,
                            "to": battle_loc,
                            "order_status": "continues",
                            "message": (f"{marshal.name} hears cannon fire at {battle_loc} "
                                        f"but cannot answer it — {reason} "
                                        f"{flavor.capitalize()} continues."),
                            **refusal_keys(action_result),
                        }
                    # The abandonment is real: a battle fought or a march made.
                    marshal.strategic_order = None
                    clear_order_bound_interrupt(marshal)  # NPC-2
                    marshal.holding_position = False
                    marshal.hold_region = ""
                    row = {
                        "marshal": marshal.name,
                        "command": cmd_type,
                        "interrupt": "cannon_fire",
                        "interrupt_type": "cannon_fire",
                        "action_taken": action_taken,
                        "action_success": action_success,
                        "action_events": action_events,
                        "battle_location": battle_loc,
                        "to": battle_loc,
                        "order_status": "interrupted",
                        "message": f"{marshal.name} hears cannon fire! "
                                   f"Abandoning orders — rushing to {battle_loc}! "
                                   f"{action_msg}".strip(),
                    }
                    if action_taken == "attack":
                        # R2-F3: the fighting redirect carried only
                        # `action_events` — no report, no tableau.
                        row.update(_combat_carry(action_result))
                    return row

                return {
                    "marshal": marshal.name,
                    "command": cmd_type,
                    "interrupt": "cannon_fire",
                    "interrupt_type": "cannon_fire",
                    "action_taken": action_taken,
                    "action_success": action_success,
                    "action_events": action_events,
                    "battle_location": battle_loc,
                    "to": battle_loc,
                    "order_status": "interrupted",
                    "message": f"{marshal.name} hears cannon fire! "
                               f"Abandoning orders — rushing to {battle_loc}! "
                               f"{action_msg}".strip(),
                }
            else:
                # Cautious asks player
                return {
                    "marshal": marshal.name,
                    "command": order.command_type if order else "unknown",
                    "interrupt": "cannon_fire",
                    "requires_input": True,
                    "interrupt_type": "cannon_fire",
                    "battle_location": interrupt["battle_location"],
                    "message": f"{interrupt_speaker(marshal)}: 'Cannon fire at "
                               f"{interrupt['battle_location']}, Sire. Investigate?'",
                    "options": ["investigate", "continue_order", "hold_position"]
                }

        return None

    # ══════════════════════════════════════════════════════════════════════════
    # CONDITION CHECKING
    # ══════════════════════════════════════════════════════════════════════════

    def _check_condition(self, marshal, condition, world) -> Tuple[bool, str]:
        """Check if strategic condition is met."""
        order = marshal.strategic_order

        if condition.max_turns is not None:
            # SUPPORT: count from arrival at ally, not from issuance
            # (travel time shouldn't eat into the "3 turns of support" the player agreed to)
            if order.command_type == "SUPPORT":
                if order.arrived_turn is None:
                    # Haven't reached ally yet — timer hasn't started
                    turns_active = 0
                else:
                    turns_active = world.current_turn - order.arrived_turn
            else:
                turns_active = world.current_turn - order.started_turn
            if turns_active >= condition.max_turns:
                # Personality-appropriate completion message for HOLD
                if order.command_type == "HOLD":
                    personality = getattr(marshal, 'personality', 'balanced')
                    location = order.target or marshal.location
                    if personality == "aggressive":
                        msg = f"{marshal.name} grows restless and abandons {location}."
                    elif personality == "cautious":
                        msg = f"{marshal.name} has held {location} for the agreed duration. Awaiting new orders."
                    elif personality == "literal":
                        msg = f"{marshal.name} reports: Hold order complete. {condition.max_turns} turns elapsed at {location}."
                    else:
                        msg = f"{marshal.name} completes the timed hold at {location}."
                    return (True, msg)
                return (True,
                        f"Order complete after {condition.max_turns} turn(s)")

        if condition.until_marshal_arrives:
            target = world.get_marshal(condition.until_marshal_arrives)
            if target and target.location == marshal.location:
                personality = getattr(marshal, 'personality', 'balanced')
                ally_name = condition.until_marshal_arrives
                if personality == "aggressive":
                    msg = f"Finally! {ally_name} has arrived. Now we can take the fight to them!"
                elif personality == "cautious":
                    msg = f"{ally_name} has arrived. Position secured, Sire."
                elif personality == "literal":
                    msg = f"{marshal.name} reports: {ally_name} arrived as specified. Hold order complete."
                else:
                    msg = f"{ally_name} has arrived. {marshal.name} awaits new orders."
                return (True, msg)

        if condition.until_marshal_destroyed:
            target = world.get_marshal(condition.until_marshal_destroyed)
            if not target or target.strength <= 0:
                personality = getattr(marshal, 'personality', 'balanced')
                enemy_name = condition.until_marshal_destroyed
                if personality == "aggressive":
                    msg = f"{enemy_name} is finished! The hunt was glorious!"
                elif personality == "cautious":
                    msg = f"{enemy_name} has been eliminated. Threat neutralized."
                elif personality == "literal":
                    msg = f"{marshal.name} reports: Target ({enemy_name}) destroyed. Order complete."
                else:
                    msg = f"{enemy_name} destroyed. {marshal.name} awaits new orders."
                return (True, msg)

        if condition.until_relieved:
            marshals_here = world.get_marshals_in_region(marshal.location)
            allies = [m for m in marshals_here
                      if m.nation == marshal.nation and m.name != marshal.name]
            if allies:
                personality = getattr(marshal, 'personality', 'balanced')
                relief_name = allies[0].name
                if personality == "aggressive":
                    msg = f"About time! {relief_name} takes over. Free to hunt!"
                elif personality == "cautious":
                    msg = f"Relieved by {relief_name}. Orderly handover complete."
                elif personality == "literal":
                    msg = f"{marshal.name} reports: Relieved by {relief_name}. Awaiting new orders."
                else:
                    msg = f"Relieved by {relief_name}. {marshal.name} ready for new orders."
                return (True, msg)

        if condition.until_battle_won:
            battle_ending_results = ("victory", "stalemate")
            combat_result = getattr(marshal, 'last_combat_result', None)
            if combat_result in battle_ending_results:
                label = "Victory achieved!" if combat_result == "victory" else "Battle concluded (stalemate)."
                return (True, label)
            # For SUPPORT, also check ally's combat
            if order.command_type == "SUPPORT":
                ally = world.get_marshal(order.target)
                if ally:
                    ally_result = getattr(ally, 'last_combat_result', None)
                    if ally_result in battle_ending_results:
                        label = f"{ally.name} won the battle!" if ally_result == "victory" else f"Battle at {ally.location} concluded."
                        return (True, label)

        return (False, "")

    # ══════════════════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ══════════════════════════════════════════════════════════════════════════

    def _complete_order(self, marshal, world, reason: str) -> Dict:
        """Complete a strategic order successfully."""
        order = marshal.strategic_order
        cmd_type = order.command_type if order else "unknown"
        target = order.target if order else ""
        print(f"[STRATEGIC] {marshal.name}: ORDER COMPLETE - {reason}")
        marshal.strategic_order = None

        # Clear holding_position if HOLD order completes
        if cmd_type == "HOLD":
            marshal.holding_position = False
            marshal.hold_region = ""

        # Literal gets trust bonus for completing orders precisely
        is_literal = marshal.personality == "literal"
        completion_msg = reason
        if is_literal:
            marshal.trust.modify(5)
            # W6-5 §7.2.2: the completion report quotes the order's own
            # words — "The order was 'march to Swabia'. Swabia is reached."
            original = getattr(order, "original_command", "") if order else ""
            if original:
                from backend.game_logic.marshal_voice import literal_completion
                completion_msg = literal_completion(
                    original, reason, marshal.name, int(world.current_turn))
        elif getattr(marshal, 'nation', '') == getattr(world, 'player_nation',
                                                       'France'):
            # Marshal Voice Tier 1: aggressive/cautious completion reports
            # carry one register line after the plain reason (GR6,
            # display-only; unknown personalities pass through unchanged).
            from backend.game_logic.marshal_voice import personality_completion
            completion_msg = personality_completion(
                marshal.personality, reason, marshal.name,
                int(world.current_turn))

        # Notification: strategic order complete (player marshals only)
        if getattr(marshal, 'nation', '') == getattr(world, 'player_nation', 'France'):
            from backend.notifications import (
                create_notification, NotificationPriority, STRATEGIC_ORDER_COMPLETE,
            )
            world.notifications.add(create_notification(
                notification_type=STRATEGIC_ORDER_COMPLETE,
                priority=NotificationPriority.HIGH,
                title=f"{marshal.name} arrived",
                message=f"{marshal.name} has completed their {cmd_type} order — arrived at {marshal.location}.",
                turn_created=int(world.current_turn),
                details={"marshal": marshal.name, "order_type": cmd_type, "target": target},
            ))

        return {
            "marshal": marshal.name,
            "command": cmd_type,
            "order_status": "completed",
            "reason": reason,
            "message": completion_msg,
            "precision_bonus": is_literal
        }

    def _break_order(self, marshal, world, reason: str) -> Dict:
        """Break a strategic order (could not complete)."""
        order = marshal.strategic_order
        cmd_type = order.command_type if order else "unknown"
        print(f"[STRATEGIC] {marshal.name}: ORDER CANCELLED - {reason}")
        marshal.strategic_order = None

        # Clear holding_position if HOLD order breaks
        if cmd_type == "HOLD":
            marshal.holding_position = False
            marshal.hold_region = ""

        return {
            "marshal": marshal.name,
            "command": cmd_type,
            "order_status": "breaks",
            "reason": reason,
            "message": f"Order cancelled: {reason}"
        }

    def _handle_blocked_path(self, marshal, enemies, blocked_region,
                             world, game_state) -> Dict:
        """Handle enemy blocking the path.

        IMPORTANT: If the player already responded to this same enemy blocking
        this same turn (or the previous turn), don't re-ask — just hold.
        Without this, contact interrupts loop infinitely every turn when
        a persistent enemy blocks a SUPPORT/MOVE_TO path.

        Session 36: Fog-discovery messages. When blocked region is below FULL
        visibility, use discovery language ("Enemy forces discovered ahead!")
        instead of standard language ("Enemy at region"). This makes existing
        contact interrupts feel like genuine discoveries in fog.
        """
        from backend.models.intel import FULL as FULL_VIS

        personality = marshal.personality
        enemy = enemies[0]
        order = marshal.strategic_order

        # Session 36: Check if this is a fog discovery (region below FULL visibility)
        is_fog_discovery = False
        if hasattr(world, 'get_region_intel'):
            region_intel = world.get_region_intel(blocked_region)
            is_fog_discovery = (region_intel.visibility != FULL_VIS)

        # Suppress re-asking about the same enemy (prevents infinite interrupt loop)
        last_contact_enemy = getattr(order, 'last_contact_enemy', None)
        last_contact_turn = getattr(order, 'last_contact_turn', None)
        if (last_contact_enemy == enemy.name and
                last_contact_turn is not None and
                world.current_turn - last_contact_turn <= 1):
            return {
                "marshal": marshal.name,
                "command": order.command_type,
                "order_status": "continues",
                "action": "blocked",
                "message": f"{marshal.name} holds position — {enemy.name} "
                           f"still blocks the path at {blocked_region}."
            }

        # FA-15 (slice 3, Sept 4 2026): an enemy on the FAR SHORE of a shut
        # crossing used to reach the personality arms below — the aggressive
        # arm attacked across the water (refused, then narrated as a battle),
        # the cautious arm ASKED and offered a dead 'attack'. The honest
        # `blocked_naval` break in `_execute_move_to` was unreachable
        # whenever an enemy held the far shore, which for London is always.
        # The executor's own predicate, asked first: a shore it will refuse
        # is never attacked, asked about, or rerouted around.
        _verdict = strike_crossing_verdict(world, marshal, blocked_region)
        if _verdict is not None:
            _refusal = verdict_as_refusal(_verdict)
            broken = self._break_order(
                marshal, world,
                f"{marshal.name}'s {_strategic_command_flavor(order.command_type)} "
                f"halts at the water's edge — {refusal_reason(_refusal)}")
            broken.update({"action": "attack_refused", **refusal_keys(_refusal)})
            return broken

        if personality == "literal":
            # NPC-5 (review round): ONE source, shared with the
            # executor's first-step copy — see `resolve_order_destination`.
            destination = resolve_order_destination(world, marshal, order)

            # Session 37: If enemy is AT the destination, don't reroute — halt
            # and report. Rerouting around the destination itself is nonsensical.
            if blocked_region == destination:
                order.last_contact_enemy = enemy.name
                order.last_contact_turn = world.current_turn
                if is_fog_discovery:
                    msg = (f"{interrupt_speaker(marshal)}: 'Enemy forces discovered at "
                           f"{blocked_region}! Cannot proceed to destination. "
                           f"Awaiting orders.'")
                else:
                    msg = (f"{interrupt_speaker(marshal)}: 'Enemy forces hold {blocked_region} "
                           f"— destination blocked. Awaiting orders.'")
                return {
                    "marshal": marshal.name,
                    "command": order.command_type,
                    "order_status": "awaiting_response",
                    "requires_input": True,
                    "interrupt_type": "destination_blocked",
                    "enemy": enemy.name,
                    "location": blocked_region,
                    "fog_discovery": is_fog_discovery,
                    "message": msg,
                    "options": ["attack", "go_around", "hold_position",
                                "cancel_order"]
                }

            # Reroute silently around ALL enemy regions (mid-path only)
            enemy_regions = self._get_enemy_occupied_regions(
                marshal.nation, world, marshal=marshal)
            # Always include the just-discovered blocked region even if fog
            # doesn't reflect it yet (physical encounter is authoritative)
            if blocked_region not in enemy_regions:
                enemy_regions.append(blocked_region)
            # MOVE_TO and HOLD use weighted pathfinding for terrain-aware rerouting
            use_weighted = (order.command_type in ("MOVE_TO", "HOLD"))
            if ROAD_LAW_ON_REPLOT:
                # FA slice 5: a reroute prefers a lawful corridor and must
                # still AVOID what it fled (it used to be terrain-only).
                new_path, _ = plot_route(
                    world, marshal, destination, use_weighted=use_weighted,
                    avoid_regions=enemy_regions, avoid_is_law=True)
            else:
                pathfinder = world.find_weighted_path if use_weighted else world.find_path
                new_path = pathfinder(
                    marshal.location, destination,
                    avoid_regions=enemy_regions
                )
                new_path = ([r for r in new_path if r != marshal.location]
                            if new_path else None)
            if new_path:
                order.path = list(new_path)
                # Session 36: Discovery vs standard reroute message
                if is_fog_discovery:
                    msg = (f"{marshal.name} discovers enemy forces and adjusts "
                           f"route to avoid {blocked_region}.")
                else:
                    msg = (f"{marshal.name} adjusts route to avoid "
                           f"enemy at {blocked_region}.")
                return {
                    "marshal": marshal.name,
                    "command": order.command_type,
                    "action": "reroute",
                    "avoiding": blocked_region,
                    "order_status": "continues",
                    "fog_discovery": is_fog_discovery,
                    "message": msg,
                }
            return self._break_order(marshal, world,
                                     f"Path blocked at {blocked_region}, no alternate route")

        elif personality == "aggressive":
            # NPC-5 (review round): ONE source, shared with the
            # executor's first-step copy — see `resolve_order_destination`.
            destination = resolve_order_destination(world, marshal, order)

            # Session 37: If enemy is AT the destination, auto-attack or
            # ask player without go_around (can't reroute around destination)
            if blocked_region == destination:
                # CR-5 Phase 3: an INFERRED order uses fortification/terrain-
                # aware odds so it cannot silently assault a dug-in superior
                # force at the destination; explicit orders keep the raw ratio.
                # go_around is not valid at a destination, so this keeps the
                # destination_blocked interrupt rather than the generic gate.
                inferred = getattr(order, "delegation_inferred", False)
                if inferred:
                    from backend.commands.objection_v2 import inferred_attack_favorable
                    favorable = inferred_attack_favorable(marshal, enemy, game_state)
                else:
                    favorable = (marshal.strength / max(1, enemy.strength)) >= 0.7
                if favorable and self._should_auto_attack(marshal, enemy, world):
                    result = self.executor.execute(
                        {"command": {
                            "marshal": marshal.name,
                            "action": "attack",
                            "target": enemy.name,
                            "_strategic_execution": True
                        }},
                        game_state
                    )
                    return self._handle_combat_result(
                        marshal, enemy, result, world, game_state)
                # Bad odds at destination — ask without go_around. An inferred
                # order names the marshal's reading (§6.3c legibility, Acc #7).
                order.last_contact_enemy = enemy.name
                order.last_contact_turn = world.current_turn
                if inferred:
                    from backend.commands.delegation import describe_inferred_bad_odds
                    # PC-8: solo read, mustered addendum.
                    msg = describe_inferred_bad_odds(
                        marshal.name, enemy.name,
                        self.executor._combat._bad_odds_muster_note(
                            marshal, enemy, world))
                elif getattr(order, "combat_attempts", 0) > 0:
                    # FA slice 3 review round (R1-F5): after `continue_order`
                    # this arm said "Odds unfavorable" at 6:1 — only the
                    # mid-path twin carried the inconclusive-assault copy.
                    msg = (f"{interrupt_speaker(marshal)}: '{enemy.name} still holds "
                           f"{blocked_region}. Previous assault was inconclusive. "
                           f"Orders?'")
                elif is_fog_discovery:
                    msg = (f"{interrupt_speaker(marshal)}: 'Enemy forces discovered at "
                           f"{blocked_region}! Destination held by {enemy.name}. "
                           f"Odds unfavorable — awaiting orders.'")
                else:
                    msg = (f"{interrupt_speaker(marshal)}: '{enemy.name} holds {blocked_region} "
                           f"— destination blocked. Odds unfavorable.'")
                return {
                    "marshal": marshal.name,
                    "command": order.command_type,
                    "order_status": "awaiting_response",
                    "requires_input": True,
                    "interrupt_type": "destination_blocked",
                    "enemy": enemy.name,
                    "location": blocked_region,
                    "fog_discovery": is_fog_discovery,
                    "message": msg,
                    "options": ["attack_anyway", "hold_position",
                                "cancel_order"]
                }

            # CR-5 Phase 3: an inferred order's assault on a fortified superior
            # force routes through the one-modal confirm (§6.3c) before the
            # fortification-blind raw ratio below can auto-commit it. Explicit
            # orders keep the raw-ratio path. The marshal is still en route here
            # (blocked mid-path, not at the destination), so go_around is valid.
            gate = self._inferred_attack_gate(marshal, enemy, game_state,
                                              allow_reroute=True)
            if gate is not None:
                return gate
            ratio = marshal.strength / max(1, enemy.strength)
            if ratio >= 0.7 and self._should_auto_attack(marshal, enemy, world):
                # Auto-attack — favorable enough odds
                result = self.executor.execute(
                    {"command": {
                        "marshal": marshal.name,
                        "action": "attack",
                        "target": enemy.name,
                        "_strategic_execution": True
                    }},
                    game_state
                )
                return self._handle_combat_result(
                    marshal, enemy, result, world, game_state)

            # Bad odds or previous failed attempt — ask player
            if order.combat_attempts > 0:
                msg = (f"{interrupt_speaker(marshal)}: '{enemy.name} still blocks the path. "
                       f"Previous assault was inconclusive. Orders?'")
            else:
                # Session 36: Discovery prefix for fogged regions
                if is_fog_discovery:
                    msg = (f"{interrupt_speaker(marshal)}: 'Enemy forces discovered ahead! "
                           f"{enemy.name} blocks the path at {blocked_region}. "
                           f"Odds unfavorable.'")
                else:
                    msg = (f"{interrupt_speaker(marshal)}: '{enemy.name} blocks the path. "
                           f"Odds unfavorable.'")
            # Track contact to prevent infinite interrupt loop next turn
            order.last_contact_enemy = enemy.name
            order.last_contact_turn = world.current_turn
            return {
                "marshal": marshal.name,
                "command": order.command_type,
                "order_status": "awaiting_response",
                "requires_input": True,
                "interrupt_type": "contact_bad_odds",
                "enemy": enemy.name,
                "location": blocked_region,
                "fog_discovery": is_fog_discovery,
                "message": msg,
                "options": ["attack_anyway", "go_around", "hold_position",
                            "cancel_order"]
            }

        else:  # cautious (and balanced/loyal) — always ask
            # NPC-5 (review round): ONE source, shared with the
            # executor's first-step copy — see `resolve_order_destination`.
            destination = resolve_order_destination(world, marshal, order)

            # Track contact to prevent infinite interrupt loop next turn
            order.last_contact_enemy = enemy.name
            order.last_contact_turn = world.current_turn

            # Session 37: If enemy is AT the destination, no go_around option
            if blocked_region == destination:
                if getattr(order, "combat_attempts", 0) > 0:
                    # FA slice 3 review round (R1-F5): the cautious twin of
                    # the inconclusive-assault copy.
                    msg = (f"{interrupt_speaker(marshal)}: '{enemy.name} still holds "
                           f"{blocked_region}. Previous assault was inconclusive. "
                           f"How shall I proceed?'")
                elif is_fog_discovery:
                    msg = (f"{interrupt_speaker(marshal)}: 'Enemy forces discovered at "
                           f"{blocked_region}! Destination held. "
                           f"How shall I proceed?'")
                else:
                    msg = (f"{interrupt_speaker(marshal)}: 'Enemy holds {blocked_region} "
                           f"— destination blocked. How shall I proceed?'")
                return {
                    "marshal": marshal.name,
                    "command": order.command_type,
                    "order_status": "awaiting_response",
                    "requires_input": True,
                    "interrupt_type": "destination_blocked",
                    "enemy": enemy.name,
                    "location": blocked_region,
                    "fog_discovery": is_fog_discovery,
                    "message": msg,
                    "options": ["attack", "hold_position",
                                "cancel_order"]
                }

            # Session 36: Discovery vs standard contact message
            if is_fog_discovery:
                msg = (f"{interrupt_speaker(marshal)}: 'Enemy forces discovered at "
                       f"{blocked_region}! How shall I proceed?'")
            else:
                msg = (f"{interrupt_speaker(marshal)}: 'Enemy at {blocked_region}. "
                       f"How shall I proceed?'")
            return {
                "marshal": marshal.name,
                "command": order.command_type,
                "order_status": "awaiting_response",
                "requires_input": True,
                "interrupt_type": "contact",
                "enemy": enemy.name,
                "location": blocked_region,
                "fog_discovery": is_fog_discovery,
                "message": msg,
                "options": ["attack", "go_around", "hold_position",
                            "cancel_order"]
            }

    def _handle_combat_result(self, marshal, enemy, result,
                              world, game_state) -> Dict:
        """Handle combat result during strategic execution.

        WO-33 (slice 12): every row this returns carries the battle it
        reports — `battle_report` (Berthier's after-action report) and
        `battle_details` (the executor's cleaned result) — the same keys
        the HOLD sally and the artillery HOLD already ship. The pursue arms
        kept only the message, so a real battle fought during end-turn
        strategic processing reached the client and every digest reader
        with no report at any depth (the CA8-25 class, one seam over).
        """
        order = marshal.strategic_order
        if attack_was_refused(result):
            # FA-14 / FA-19 (slice 3, Sept 4 2026): the executor REFUSED the
            # attack — no battle, nobody lost a man — and this function used
            # to fall into its stalemate arm: "attacked Moore during march
            # but the battle was inconclusive", a `combat_stalemate`
            # interrupt, `combat_attempts` charged, `in_combat_this_turn`
            # and `last_combat_result` overwritten. None of that now: the
            # refusal ends the order with the executor's own reason (the
            # PF-8 / DEF-5 water's-edge idiom — the pathfinder is edge-blind,
            # a reroute would plan the same crossing), and touches no combat
            # record.
            reason = refusal_reason(result)
            if not order:
                return {
                    "marshal": marshal.name,
                    "command": "unknown",
                    "action": "attack_refused",
                    "order_status": "breaks",
                    "message": f"{marshal.name} cannot attack {enemy.name} — {reason}",
                    **refusal_keys(result),
                }
            flavor = _strategic_command_flavor(order.command_type)
            if result.get("blocked_naval"):
                text = f"{marshal.name}'s {flavor} halts at the water's edge — {reason}"
            else:
                text = f"{marshal.name} cannot attack {enemy.name} — {reason}"
            broken = self._break_order(marshal, world, text)
            broken.update({"action": "attack_refused", "target": enemy.name,
                           **refusal_keys(result)})
            return broken

        carry = _combat_carry(result)
        if not order:
            # Order was cleared (e.g., by break during combat)
            return {
                "marshal": marshal.name,
                "command": "unknown",
                "action": "combat",
                "order_status": "breaks",
                "message": f"{marshal.name} engaged {enemy.name}.",
                **carry,
            }

        # ══════════════════════════════════════════════════════════════
        # FA-N3 — DERIVE THE OUTCOME FROM THE VICTOR, NOT FROM A WORD
        # NOTHING EVER WRITES.
        #
        # Both prior reads were production-dead, so EVERY battle fought
        # under a standing strategic order fell through to the stalemate
        # arm below:
        #
        #   (a) `events[0]["outcome"]` — `combat.py` assigns exactly six
        #       outcome words (`attacker_victory`, `defender_victory`,
        #       `attacker_tactical_victory`, `defender_tactical_victory`,
        #       `mutual_destruction`, `stalemate`). None of them is the
        #       literal "victory" or "defeat" the arms below compare
        #       against, so the read could never satisfy them.
        #   (b) `result["battle_result"]` — `_execute_attack` returns no
        #       such top-level key. Measured: its result keys are
        #       action_info / action_summary / battle_diorama / battle_name
        #       / battle_report / events / message / reinforcement_* /
        #       success.
        #
        # Measured on the shipped 1805 boot: Ney with a standing MOVE_TO
        # ANNIHILATED Mack at Frankfurt — defender strength 0,
        # `enemy_destroyed`, event outcome `attacker_victory`, victor
        # `Ney` — and this function reported "the battle was inconclusive.
        # Continue move to?", mounted a `combat_stalemate` interrupt, and
        # charged the order a failed `combat_attempts` for a total
        # victory. The core multi-turn loop of the game ("march to Vienna
        # and fight through whatever stands in the way") could not report
        # its own outcome.
        #
        # `_respond_blocked_path` reads the victor rather than the outcome
        # word, and this is that idiom in the one place that lacked it —
        # though not a claim that the sibling is complete: it handles
        # neither no-victor shape, and closing that gap is FA-14's slice.
        # The marshal is always the ATTACKER here — both callers
        # execute `action: attack` for him — so victor == his name is a
        # win, a different victor is a defeat, and no victor (stalemate or
        # mutual destruction) is a draw.
        #
        # The scan looks for the battle event rather than trusting index
        # 0, and honours the `glorious_charge` event's own `attacker_won`
        # flag the way the HOLD sally arm above already does — a charge
        # names a winner, not a victor.
        # ══════════════════════════════════════════════════════════════
        outcome = "unknown"
        events = result.get("events", [])
        if not isinstance(events, list):
            events = [events] if events else []
        victor = ""
        outcome_word = ""
        for event in events:
            if not isinstance(event, dict):
                continue
            if event.get("type") == "glorious_charge":
                outcome = "victory" if event.get("attacker_won") else "defeat"
                break
            if event.get("type") == "battle" or "victor" in event:
                victor = str(event.get("victor") or "")
                outcome_word = str(event.get("outcome") or "")
                break
        if outcome == "unknown":
            if not victor:
                victor = str((result.get("battle_result") or {}).get("victor") or "")
            if victor and victor == marshal.name:
                outcome = "victory"
            elif victor:
                outcome = "defeat"
            elif outcome_word:
                # A battle event that names its outcome but NOT its victor.
                # There is exactly one such shape and the first cut of this
                # fix missed it: `combat_executor`'s `auto_kill_event` (the
                # auto-bombardment kill) is `type: "battle"`,
                # `outcome: "attacker_victory"`, and carries no `victor` key
                # at all — so a corps annihilated by artillery under a
                # standing order still reported a draw. The marshal is
                # always the ATTACKER at this seam, so the attacker/defender
                # half of combat.py's vocabulary IS the answer.
                if outcome_word.startswith("attacker"):
                    outcome = "victory"
                elif outcome_word.startswith("defender"):
                    outcome = "defeat"
                else:  # stalemate, mutual_destruction
                    outcome = "stalemate"
            else:
                # No battle at all. This is an attack the executor REFUSED —
                # reachable, e.g. through the NV-4 crossing gate — and it is
                # narrated below as an inconclusive battle, which is a lie.
                # That lie is FA-14's row (its `not result.get("success")`
                # guard belongs at the head of this function) with FA-N26 and
                # FA-N40 as its narration siblings; it is UNCHANGED here, and
                # named rather than silently inherited.
                outcome = "stalemate"

        # Record combat for loop prevention
        order.last_combat_enemy = enemy.name
        order.last_combat_turn = world.current_turn
        order.last_combat_result = outcome

        # Track failed attempts — stalemate increments, victory resets
        if outcome == "victory":
            order.combat_attempts = 0
        elif outcome != "defeat":  # stalemate/unknown
            order.combat_attempts = getattr(order, 'combat_attempts', 0) + 1

        # Update marshal tracking
        marshal.in_combat_this_turn = True
        marshal.last_combat_turn = world.current_turn
        marshal.last_combat_location = marshal.location

        if outcome == "victory":
            marshal.last_combat_result = "victory"
            return {
                "marshal": marshal.name,
                "command": order.command_type,
                "action": "combat",
                "target": enemy.name,
                "outcome": "victory",
                "order_status": "continues",
                "message": f"{marshal.name} defeats {enemy.name}! Continuing.",
                **carry,
            }

        elif outcome == "defeat":
            marshal.last_combat_result = "defeat"
            broken = self._break_order(marshal, world,
                                       f"Defeated by {enemy.name}")
            broken.update({"action": "combat", "target": enemy.name,
                           "outcome": "defeat", **carry})
            return broken

        else:  # stalemate / unknown
            marshal.last_combat_result = "stalemate"
            # FA-34 (slice 3): "Continue move to?" was the raw enum; the
            # flavor helper the answer arms already use says "his march".
            stalemate_msg = (
                f"{marshal.name} attacked {enemy.name} during "
                f"{_strategic_command_flavor(order.command_type)} but the "
                f"battle was inconclusive. Continue "
                f"{_strategic_command_flavor(order.command_type)}?")
            marshal.pending_interrupt = {
                # See the contact_bad_odds builder above — the popup needs the
                # marshal name to answer via /strategic_response.
                "marshal": marshal.name,
                "interrupt_type": "combat_stalemate",
                "enemy": enemy.name,
                "location": marshal.location,
                "is_first_step": False,
                "options": ["continue_order", "hold_position", "cancel_order"],
                # FA-N60: the popup renders THIS dict's message on the
                # synchronous route and after /load.
                "message": stalemate_msg,
            }
            return {
                "marshal": marshal.name,
                "command": order.command_type,
                "action": "combat",
                "target": enemy.name,
                "outcome": "stalemate",
                "requires_input": True,
                "pending_interrupt": marshal.pending_interrupt,
                "interrupt_type": "combat_stalemate",
                "message": stalemate_msg,
                "options": ["continue_order", "hold_position", "cancel_order"],
                **carry,
            }

    def _should_auto_attack(self, marshal, enemy, world) -> bool:
        """Combat loop prevention: Don't auto-attack same enemy after failed attempt."""
        order = marshal.strategic_order
        if not order:
            return True

        # After any failed auto-attack (stalemate), stop auto-attacking this enemy
        # Player must explicitly choose to re-engage via the interrupt popup
        if (order.last_combat_enemy == enemy.name and
                order.combat_attempts > 0):
            return False

        if (order.last_combat_enemy == enemy.name and
                order.last_combat_turn is not None and
                world.current_turn - order.last_combat_turn <= 1):
            return False
        return True

    def _get_enemy_occupied_regions(self, nation: str, world,
                                     fog_aware: bool = False,
                                     marshal=None) -> List[str]:
        """Get list of regions with enemies (for cautious pathfinding).

        FOG OF WAR (Session 34B): When fog_aware=True, only includes regions
        where the player has PARTIAL+ visibility confirming enemy presence.
        Cautious marshals can only avoid enemies they know about.
        When fog_aware=False (default), omniscient — used by AI.

        If marshal is provided and fog_aware is not explicitly set by caller,
        fog_aware is derived automatically: True for player marshals, False for AI.
        This prevents callers from forgetting to pass fog_aware.
        """
        if ROAD_LAW_ONE_SEAM:
            return enemy_occupied_regions(world, nation, marshal=marshal,
                                          fog_aware=fog_aware)
        from backend.models.intel import FULL, PARTIAL

        # Auto-derive fog_aware from marshal if provided and caller didn't override
        if marshal is not None and not fog_aware:
            fog_aware = (marshal.nation == world.player_nation)

        enemy_regions = []
        for region_name in world.regions:
            if fog_aware:
                intel = world.get_region_intel(region_name)
                if intel.visibility not in (FULL, PARTIAL):
                    continue  # Can't see enemies here — skip
            if world.get_enemies_in_region(region_name, nation):
                enemy_regions.append(region_name)
        return enemy_regions

    def _get_personality_aware_path(self, marshal, destination, world,
                                     use_weighted: bool = False) -> Optional[List[str]]:
        """
        Shared pathfinding helper — personality determines route strategy.

        - Cautious: Avoids enemy-occupied regions
        - Literal: Direct path (blocked path handled by _handle_blocked_path reroute)
        - Aggressive: Direct path (will fight through blockages)

        FOG OF WAR (Session 34B): Cautious player marshals only avoid
        VISIBLE enemies (PARTIAL+). If an enemy is fogged, the cautious
        marshal doesn't know to avoid it — walking into a trap is a fog moment.
        AI marshals use omniscient pathfinding (fog_aware=False).

        Args:
            use_weighted: If True, use Dijkstra (terrain-aware) instead of BFS.
                          Used by MOVE_TO for attrition-optimized routes.
                          PURSUE stays on BFS (chasing doesn't pick scenic routes).

        Returns path excluding start location, or None if no path exists.
        """
        personality = getattr(marshal, 'personality', 'balanced')
        if ROAD_LAW_ONE_SEAM:
            # FA slice 5: ONE ladder (`plot_route`) — the arm below is the
            # prior inline copy it reproduces byte-for-byte (pinned).
            avoid = None
            if personality == "cautious":
                avoid = self._get_enemy_occupied_regions(
                    marshal.nation, world, marshal=marshal)
            road, _ = plot_route(world, marshal, destination,
                                 use_weighted=use_weighted, avoid_regions=avoid)
            return road or None
        pathfinder = world.find_weighted_path if use_weighted else world.find_path
        # PF-8: a PLAYER march prefers a passable (own/allied/open-border/at-war)
        # corridor over impassable neutral land; the AI keeps omniscient routing.
        # If no passable route exists, fall back so the order still forms and the
        # stall-feedback path reports why (rather than silently vanishing).
        _pf = marshal.nation if marshal.nation == world.player_nation else None

        if personality == "cautious":
            enemy_regions = self._get_enemy_occupied_regions(
                marshal.nation, world, marshal=marshal)
            path = pathfinder(marshal.location, destination,
                              avoid_regions=enemy_regions, passable_for=_pf)
            if not path:
                # No safe route — fall back to direct path. The marshal will
                # NOT walk through enemies: the movement loop (line 466-468)
                # blocks entry and triggers _handle_blocked_path(), which asks
                # the player before proceeding. This is intentional UX — the
                # marshal starts moving and reports contact when it happens.
                path = pathfinder(marshal.location, destination, passable_for=_pf)
        else:
            # Aggressive/literal/balanced: direct path. Movement loop at
            # _execute_move_to line 466 still blocks entry into enemy regions
            # and triggers _handle_blocked_path() for interrupt/reroute.
            path = pathfinder(marshal.location, destination, passable_for=_pf)

        if not path and _pf:
            # PF-8 fallback: no passable corridor — form the terrain-only path so
            # the march begins and stalls at the closed border with a reason.
            path = pathfinder(marshal.location, destination)

        if not path:
            return None

        # Strip start location (find_weighted_path/find_path returns start-inclusive)
        return [r for r in path if r != marshal.location]
