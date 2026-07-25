"""The War Council — AI-3, the Decision for War (docs/AI_INTENT_SPEC.md
§4.3, §4.3a, §13.1 AI-3c; gate record §16; landing record §17).

The missing first link the phase exists to fix (§0): before this module no
AI nation could ever DECIDE to go to war — the coalition was a global
anti-France threat scalar, not a decision. The war council gives a court
with a live acquire design, an exhausted ladder, favourable force and a
justification the ability to enter a war for itself — fore-warned, priced,
courtable, and (via AI-4b) endable.

Contracts honoured here:

- **No new PEACE→WAR edge** (§0.1 Correction A): the council calls
  `diplomacy.declare_war` — the same function `combat_executor.py`'s seam
  calls — at the ANNOUNCEMENT, so the seam's own declaration later finds
  the war live and is a no-op (§4.3a-1).
- **The ladder must have been climbed** (§5 pin 8): declaration requires
  prior refused asks / a refused coercive demand on the SERIALIZED
  `diplomatic_refusals` record — or a §3.3 renege grievance, which may
  skip rungs (Schönbrunn → Jena). No cold-open wars.
- **Fore-warning before war, always** (§4.3): a crisis is opened (beat 2,
  The Brewing Crisis), coerces (beat 3's AI-AI arm, the coercive demand),
  and only then declares — never earlier than `CRISIS_FOREWARN_TURNS`
  turns of FOREGROUNDED tenure. One foregrounded crisis world-wide (the
  §4.6a tempo rule); background crises climb silently and surface when
  the foreground clears.
- **Every foregrounded crisis ends on screen** (§5 pin 21): exactly one of
  two beats — the fore-warned war, or The Crisis Passes (beat 7) with its
  cause named and the instrument credited (§12.1's taxonomy: satisfied /
  bought off / deterred / starved).
- **AI-vs-AI only in v1** (§16.2): a player-targeted design expresses
  `coerce` through the NA-5 ultimatum and `fight` through the coalition
  machinery — the campaign's central pressure — never a unilateral
  declaration (the NA-5 pin stands).
- **D1's cap** (§6, re-confirmed §16.1-1): at most `MAX_SIMULTANEOUS_AI_WARS`
  live AI-initiated wars world-wide.
- **Pin 15**: the council never fore-warns a crisis whose declaration
  predicate is already refused (`can_declare_war` is the shared preview,
  §4.3a-4), and the combat seams abort on a refused declaration.
- **Deckless-neutral** (§5 pin 18): no deck → no intent → no crisis; the
  bare suite world and the legacy fixture world never enter this module's
  behaviour (process returns [] with `war_intents` empty).

Serialized state: ONE new world field — `world.war_intents`
(coveter → crisis record). Everything else is derived per turn or rides
already-serialized containers (`war_instances` records gain
`ai_initiated` / `design_id` / `stated_reason` keys; `war_objectives`
records gain `design` and design-scoped `target_regions` — reuse, not a
new war-goal system).
"""

from typing import Dict, List, Optional

# ── Blessed numbers (in-band tunable; shape changes escalate) ──────────
MAX_SIMULTANEOUS_AI_WARS = 2       # D1, re-confirmed at the §16 re-check
CRISIS_FOREWARN_TURNS = 2          # foregrounded tenure before declaration
CRISIS_REFUSALS_REQUIRED = 2       # ladder gate: refused asks on record
AI_WAR_FORCE_RATIO = 1.25          # the NA-5 strength idiom
AI_WAR_TREASURY_FLOOR = 500        # no bankrupt adventures
CRISIS_HARD_STALL_TURNS = 4        # preview-refused predicate → starved
CRISIS_SOFT_STALL_TURNS = 8        # ladder/restraints/cap blocked → starved
COERCIVE_DEMAND_TYPE = "coercive_demand"

# The §12.1 cause taxonomy for beat 7 (display strings composed backend-side, R7)
_CRISIS_CAUSE_COPY = {
    "satisfied": "the design is satisfied — the want is won",
    "bought_off": "the design was bought off — compensation stands",
    "deterred": "the guarantee raised the price past reach",
    "starved": "the moment passed — opportunism decayed",
}


def _standing_strength(world, nation: str) -> int:
    return sum(int(m.strength) for m in world.marshals.values()
               if getattr(m, "nation", None) == nation and m.strength > 0)


def count_ai_initiated_wars(world) -> int:
    """Live wars the war council opened (D1's cap denominator).

    Review fix [r2 HIGH]: a war whose loser was ELIMINATED never receives
    `ended_turn` (elimination bypasses the settlement path by design), so
    counting on `ended_turn` alone jammed the cap permanently after two
    successful minor-conquests — the feature's own happy path. A war is
    LIVE for the cap only while it still has two standing sides.
    """
    count = 0
    for war in (getattr(world, "war_instances", {}) or {}).values():
        if not war.get("ai_initiated") or war.get("ended_turn") is not None:
            continue
        if len(war.get("active_participants") or []) < 2:
            continue  # decided by elimination — no longer a live war
        count += 1
    return count


def can_declare_war(world, aggressor: str, target: str,
                    war_objective: str = "conquest") -> Dict:
    """§4.3a-4: the shared declaration preview — armistice cooldown,
    objective validity and availability, war-instance side conflict, and
    the treaty-in-the-way state — so a refused declaration is a fail-safe
    rather than the normal path, and a fore-warned crisis never dies
    silently. Read-only.
    """
    from backend.game_logic.diplomacy import (
        OFFENSIVE_OBJECTIVE_TYPES,
        OPEN_MOVEMENT_STATES,
        _get_objective_availability,
    )
    from backend.game_logic.settlement_helpers import validate_war_declaration

    if not aggressor or not target or aggressor == target:
        return {"ok": False, "reason": "self_war"}
    state = world.get_diplomatic_state(aggressor, target)
    if state == "WAR":
        return {"ok": False, "reason": "already_at_war"}
    diplo_key = world._make_diplo_key(aggressor, target)
    if int((getattr(world, "armistice_cooldowns", {}) or {}).get(diplo_key, 0)) > 0:
        return {"ok": False, "reason": "armistice_cooldown"}
    if war_objective not in OFFENSIVE_OBJECTIVE_TYPES:
        return {"ok": False, "reason": "invalid_objective"}
    availability = _get_objective_availability(world, aggressor, target, war_objective)
    if availability and not availability.get("available", True):
        return {"ok": False, "reason": "objective_unavailable"}
    validation = validate_war_declaration(
        world, aggressor, target,
        entry_path="war_declaration", reason="war_council_preview",
    )
    if not validation.get("ok") and not validation.get("merge_required"):
        return {"ok": False, "reason": "war_instance_side_conflict"}
    if state in OPEN_MOVEMENT_STATES:
        # §4.3a-2: a coveter holding an open-movement treaty must break it
        # first — a visible ladder step between coerce and fight.
        return {"ok": False, "reason": "treaty_in_the_way"}
    return {"ok": True, "reason": ""}


def exit_shared_wars_for_defection(world, defector: str, new_enemy: str,
                                   reason: str = "coalition_defection") -> Dict:
    """§4.3a's mainline blocked case, lifted from the VS-6 side-exit idiom
    (vassal.py): a co-belligerent cannot declare on a nation that shares
    its war sides — peace out the defector's WAR pairs first, then the
    caller declares. Used by scripted defection paths (the DoD betrayal
    reachability); organic use belongs to AI-5b(ii), the volte-face.
    """
    from backend.game_logic.diplomacy import (
        cleanup_war_end,
        set_diplomatic_state,
    )
    exited = []
    for other in list(world.get_active_nations()):
        if other in (defector, new_enemy):
            continue
        if world.get_diplomatic_state(defector, other) == "WAR":
            set_diplomatic_state(world, defector, other, "PEACE", reason)
            cleanup_war_end(
                world,
                world._make_diplo_key(defector, other),
                conclude_objectives=True,
            )
            exited.append(other)
    return {"success": True, "exited": exited}


# ── Crisis lifecycle ────────────────────────────────────────────────────


def get_war_intent(world, nation: str) -> Optional[Dict]:
    return (getattr(world, "war_intents", {}) or {}).get(nation)


def _crisis_cause_of_death(world, coveter: str, record: Dict) -> Optional[str]:
    """None while the crisis lives; else the §12.1 cause. Derived per turn
    — `price` is a reading, never a latch (§3.1a)."""
    from backend.game_logic.agendas import get_active_agenda
    from backend.game_logic.instruments import design_suspended
    from backend.game_logic.intent import get_nation_intent

    target = record.get("target")
    design_id = record.get("design_id")

    # (b) bought off — the compensation record suspends the design.
    if design_suspended(world, coveter, design_id):
        return "bought_off"

    agenda = get_active_agenda(coveter, world)
    if agenda is None or agenda.id != design_id or agenda.survival:
        # The deck moved on: satisfied, superseded, or survival override.
        return "satisfied"

    view = get_nation_intent(coveter, world)
    if view.against != target:
        return "satisfied"  # the obstacle changed — this quarrel is over
    if view.price == "fight":
        return None  # still live

    # The rung fell below fight: name why (§12.1's taxonomy).
    for guarantee in getattr(world, "diplomatic_guarantees", []) or []:
        if (guarantee.get("protected") == target
                and guarantee.get("guarantor") != coveter):
            return "deterred"
    return "starved"


def _emit_crisis_passed(world, coveter: str, record: Dict, cause: str,
                        events: List[Dict]) -> None:
    """Beat 7 — The Crisis Passes (§12.1, pin 21). Only a FOREGROUNDED
    crisis owes the player an ending; background coolings stay quiet
    (pin 13 untouched)."""
    if not record.get("foregrounded"):
        return
    from backend.display_names import humanize_entity_name
    from backend.game_logic.dispatch import queue_dispatch_event
    coveter_display = humanize_entity_name(coveter)
    target_display = humanize_entity_name(str(record.get("target") or ""))
    cause_copy = _CRISIS_CAUSE_COPY.get(cause, _CRISIS_CAUSE_COPY["starved"])
    event = {
        "type": "crisis_passed",
        "nation": coveter,
        "target": record.get("target"),
        "design_id": record.get("design_id"),
        "cause": cause,
        "message": (f"{coveter_display} stands down over "
                    f"{target_display} — {cause_copy}."),
    }
    world.log_event(dict(event))
    events.append(event)
    queue_dispatch_event(world, "crisis_passed", {
        "nation": coveter_display,
        "target": target_display,
        "cause": cause_copy,
    }, "always")


def _emit_crisis_brewing(world, coveter: str, record: Dict,
                         events: List[Dict]) -> None:
    """Beat 2 — The Brewing Crisis: the fore-warning, with the instruments
    that would defuse it listed and HONESTLY gated (the /formables
    honest-availability contract applied to diplomacy)."""
    from backend.display_names import humanize_entity_name
    from backend.game_logic.dispatch import queue_dispatch_event
    from backend.game_logic.instruments import compute_buyoff_price

    coveter_display = humanize_entity_name(coveter)
    target_display = humanize_entity_name(str(record.get("target") or ""))

    # Honest availability: name each instrument WITH the player's real gate.
    player = getattr(world, "player_nation", "France")
    treasury = int((getattr(world, "nation_gold", {}) or {}).get(player, 0))
    dp = int(getattr(world, "diplomatic_points", 0) or 0)
    price = compute_buyoff_price(world, coveter)
    instruments = []
    if price is not None:
        afford = "you can afford it" if treasury >= price else \
            f"the treasury holds {treasury:,}"
        instruments.append(f"compensate ({price:,}g — {afford})")
    instruments.append(
        f"guarantee {target_display} (1 DP — {dp} in hand)"
        if dp >= 1 else "guarantee (needs 1 DP — none in hand)")
    instruments.append("or let the war come, having been asked")

    event = {
        "type": "crisis_brewing",
        "nation": coveter,
        "target": record.get("target"),
        "design_id": record.get("design_id"),
        "reason_title": record.get("want_title"),
        "message": (f"{coveter_display} will move on {target_display} — "
                    f"{record.get('want_title') or 'a design of state'}. "
                    f"You may {'; '.join(instruments)}."),
    }
    world.log_event(dict(event))
    events.append(event)
    queue_dispatch_event(world, "crisis_brewing", {
        "nation": coveter_display,
        "target": target_display,
        "instruments": "; ".join(instruments),
    }, "always")


def _emit_coercive_demand(world, coveter: str, record: Dict,
                          events: List[Dict]) -> None:
    """Beat 3's AI-AI arm: the coercive demand — the ladder step between
    the refused asks and the declaration, refused on the record (the
    holder does not yield its own homeland, the design_ask idiom)."""
    from backend.display_names import humanize_entity_name
    from backend.game_logic.ai_diplomacy import record_diplomatic_refusal
    from backend.game_logic.dispatch import queue_dispatch_event

    target = str(record.get("target") or "")
    record_diplomatic_refusal(world, coveter, target, COERCIVE_DEMAND_TYPE)
    coveter_display = humanize_entity_name(coveter)
    target_display = humanize_entity_name(target)
    event = {
        "type": "coercive_demand",
        "nation": coveter,
        "target": target,
        "design_id": record.get("design_id"),
        "message": (f"{coveter_display} delivers a final demand to "
                    f"{target_display} — it is refused."),
    }
    world.log_event(dict(event))
    events.append(event)
    if record.get("foregrounded"):
        queue_dispatch_event(world, "coercive_demand", {
            "nation": coveter_display,
            "target": target_display,
        }, "always")


def _ladder_climbed(world, coveter: str, target: str) -> bool:
    """§5 pin 8: prior refused asks/coercion on the serialized record — or
    a §3.3 renege grievance, the strongest casus belli, which may skip
    rungs entirely."""
    from backend.game_logic.ai_diplomacy import get_refused_asks
    from backend.game_logic.instruments import has_renege_grievance
    if has_renege_grievance(world, coveter, target):
        return True
    return len(get_refused_asks(world, coveter, target)) >= CRISIS_REFUSALS_REQUIRED


def _restraints_hold(world, coveter: str, target: str) -> bool:
    """§4.3's restraint gates: force ratio, treasury, existing war load."""
    if world.get_nations_at_war_with(coveter):
        return False  # a court already at war opens no second design war
    treasury = int((getattr(world, "nation_gold", {}) or {}).get(coveter, 0))
    if treasury < AI_WAR_TREASURY_FLOOR:
        return False
    own = _standing_strength(world, coveter)
    theirs = _standing_strength(world, target)
    # Alliance webs: a defender's guarantors stand in the scale too.
    for guarantee in getattr(world, "diplomatic_guarantees", []) or []:
        if (guarantee.get("protected") == target
                and guarantee.get("guarantor") not in (coveter, target)):
            theirs += _standing_strength(world, str(guarantee.get("guarantor")))
    if theirs > 0 and own < AI_WAR_FORCE_RATIO * theirs:
        return False
    if theirs == 0 and own <= 0:
        return False
    return True


def _declare_design_war(world, coveter: str, record: Dict,
                        events: List[Dict]) -> bool:
    """§4.3a-1: the council owns the declaration, at the announcement."""
    from backend.game_logic.agendas import get_agenda_military_targets
    from backend.game_logic.diplomacy import declare_war
    from backend.game_logic.instruments import has_renege_grievance

    target = str(record.get("target") or "")
    casus = has_renege_grievance(world, coveter, target)
    result = declare_war(world, coveter, target,
                         casus_belli=casus, war_objective="conquest")
    if not result.get("success"):
        # The fail-safe arm — preview said yes, the authority said no.
        # The crisis stays open; the preview re-runs next turn (a crisis
        # whose predicate goes permanently refused passes as starved).
        return False

    war_id = str(result.get("war_id") or "")
    war = (getattr(world, "war_instances", {}) or {}).get(war_id)
    if isinstance(war, dict):
        # Reuse, not a new war-goal system (§4.3): the instance carries
        # the design and the STATED REASON the ledger renders (pin 4).
        war["ai_initiated"] = True
        war["design_id"] = record.get("design_id")
        war["stated_reason"] = record.get("want_title")

    # Pin 4 ("no unexplained war"): ride the stated reason on the
    # war_declaration event declare_war just logged, so the dispatch
    # headline can render it. Single writer, same turn — the event is
    # the last matching entry by construction.
    for logged in reversed(getattr(world, "event_log", []) or []):
        if (logged.get("type") == "war_declaration"
                and logged.get("aggressor") == coveter
                and logged.get("target") == target):
            logged["stated_reason"] = record.get("want_title")
            break

    # The objective record carries the design's own provinces instead of
    # [capital] — AI-initiated design wars ONLY (§4.3: the player's War
    # Purpose numbers stay byte-identical).
    design_regions = get_agenda_military_targets(coveter, world)
    if design_regions:
        diplo_key = world._make_diplo_key(coveter, target)
        objective = ((getattr(world, "war_objectives", {}) or {})
                     .get(diplo_key, {}) or {}).get(coveter)
        if isinstance(objective, dict):
            objective["target_regions"] = list(design_regions)
            objective["design"] = record.get("design_id")

    from backend.display_names import humanize_entity_name
    events.append({
        "type": "ai_war_declared",
        "aggressor": coveter,
        "target": target,
        "war_id": war_id,
        "stated_reason": record.get("want_title"),
        "message": (f"{humanize_entity_name(coveter)} declares war on "
                    f"{humanize_entity_name(target)} — "
                    f"{record.get('want_title') or 'conquest'}."),
    })

    # The join arm (AI-2d / D5-3 enforcement made real): an AI guarantor
    # of the target honours its pledge at the declaration — or the
    # instruments pass brands it within the grace window. France's own
    # pledge is the player's choice; the ward's plea reaches the dispatch.
    _honour_guarantees(world, coveter, target, war_id, events)
    return True


def _honour_guarantees(world, coveter: str, target: str, war_id: str,
                       events: List[Dict]) -> None:
    from backend.display_names import humanize_entity_name
    from backend.game_logic.diplomacy import declare_war
    from backend.game_logic.dispatch import queue_dispatch_event
    player = getattr(world, "player_nation", "France")
    for guarantee in list(getattr(world, "diplomatic_guarantees", []) or []):
        if guarantee.get("protected") != target:
            continue
        guarantor = str(guarantee.get("guarantor") or "")
        if not guarantor or guarantor in (coveter, target):
            continue
        if guarantor == player:
            # Player agency: the ward pleads; the abandonment clock
            # (instruments' grace) is the honest consequence machinery.
            queue_dispatch_event(world, "guarantee_called", {
                "ward": humanize_entity_name(target),
                "aggressor": humanize_entity_name(coveter),
            }, "always")
            continue
        if world.get_diplomatic_state(guarantor, coveter) == "WAR":
            continue
        join = declare_war(world, guarantor, coveter, casus_belli=True)
        if join.get("success"):
            # Review fix [r8 LOW]: the join war's headline reason is the
            # guarantee, not bare "conquest" — patch the just-logged
            # declaration event the same way the design war does (pin 4).
            for logged in reversed(getattr(world, "event_log", []) or []):
                if (logged.get("type") == "war_declaration"
                        and logged.get("aggressor") == guarantor
                        and logged.get("target") == coveter):
                    logged["stated_reason"] = (
                        f"honouring the guarantee of "
                        f"{humanize_entity_name(target)}")
                    break
            event = {
                "type": "guarantee_honored",
                "guarantor": guarantor,
                "ward": target,
                "aggressor": coveter,
                "message": (f"{humanize_entity_name(guarantor)} honours its "
                            f"guarantee of {humanize_entity_name(target)} — "
                            f"war on {humanize_entity_name(coveter)}."),
            }
            world.log_event(dict(event))
            events.append(event)


def _run_ai_instrument_producers(world, coveter: str, record: Dict,
                                 events: List[Dict]) -> None:
    """The Stage C deferral this stage owns (§15 → AI-3): AI courts
    PRODUCING guarantees and compensation, where the choice has stakes —
    a live foregrounded crisis. At most one AI guarantee world-wide per
    turn; a folds-statecraft holder may buy the coveter off once."""
    from backend.game_logic.instruments import (
        compute_buyoff_price,
        create_compensation_bargain,
        pledge_guarantee,
    )
    player = getattr(world, "player_nation", "France")
    target = str(record.get("target") or "")

    # (a) The holder folds: buy the design off (§3.1a descent (b) for
    # AI-AI crises — beat 7's "bought off" cause needs a producer).
    if not record.get("buyoff_attempted"):
        record["buyoff_attempted"] = True
        statecraft = world.get_statecraft(target) if target != player else {}
        if statecraft.get("coercion") == "folds":
            price = compute_buyoff_price(world, coveter)
            gold = getattr(world, "nation_gold", {}) or {}
            if price is not None and int(gold.get(target, 0)) >= price:
                gold[target] = int(gold.get(target, 0)) - int(price)
                gold[coveter] = int(gold.get(coveter, 0)) + int(price)
                # Review fix [r2 LOW]: the SAME granted shape the player
                # verb mints ({"gold": N}) — one record schema, GR5.
                create_compensation_bargain(
                    world, payer=target, recipient=coveter,
                    design_id=str(record.get("design_id") or ""),
                    granted={"gold": int(price)},
                )
                from backend.display_names import humanize_entity_name
                event = {
                    "type": "design_bought_off",
                    "payer": target,
                    "recipient": coveter,
                    "design_id": record.get("design_id"),
                    "message": (f"{humanize_entity_name(target)} buys off "
                                f"{humanize_entity_name(coveter)}'s design "
                                f"for {int(price):,} gold."),
                }
                world.log_event(dict(event))
                events.append(event)
                return  # the crisis will pass at the next poll

    # (b) A protector steps forward: one AI guarantee per turn world-wide.
    if record.get("guarantee_considered"):
        return
    record["guarantee_considered"] = True
    if getattr(world, "_ai_guarantee_this_turn", -1) == int(world.current_turn):
        return
    for candidate in world.get_active_nations():
        if candidate in (coveter, target, player):
            continue
        if candidate in (getattr(world, "vassals", {}) or {}):
            continue
        statecraft = world.get_statecraft(candidate)
        reaches = tuple(statecraft.get("reaches_first") or ())
        if "sponsor" not in reaches and "align" not in reaches:
            continue
        if world.get_nations_at_war_with(candidate):
            continue
        rel_target = int(world.nation_relations.get(
            world._make_diplo_key(candidate, target), 0) or 0)
        rel_coveter = int(world.nation_relations.get(
            world._make_diplo_key(candidate, coveter), 0) or 0)
        if rel_target < 40 or rel_coveter > 0:
            continue
        pledge = pledge_guarantee(world, guarantor=candidate, protected=target)
        if pledge.get("success", True) and pledge.get("id"):
            world._ai_guarantee_this_turn = int(world.current_turn)
            from backend.display_names import humanize_entity_name
            event = {
                "type": "guarantee_pledged",
                "guarantor": candidate,
                "protected": target,
                "message": (f"{humanize_entity_name(candidate)} guarantees "
                            f"{humanize_entity_name(target)} against "
                            f"{humanize_entity_name(coveter)}'s design."),
            }
            world.log_event(dict(event))
            events.append(event)
            break


# ── AI-3c: the army agrees with the ledger (§13.1) ─────────────────────


def get_intent_frontier(world, nation: str) -> List[str]:
    """Regions `nation` can lawfully stand in that border its design's
    unmet targets — the massing bias's destination set. Empty without a
    live crisis (deckless-neutral; released the same turn a crisis cools
    — no latch). Cached per turn (GR8)."""
    cache = getattr(world, "_intent_frontier_cache", None)
    cache_turn = getattr(world, "_intent_frontier_cache_turn", -1)
    if cache is None or cache_turn != int(world.current_turn):
        cache = {}
        world._intent_frontier_cache = cache
        world._intent_frontier_cache_turn = int(world.current_turn)
    if nation in cache:
        return cache[nation]

    frontier: List[str] = []
    record = get_war_intent(world, nation)
    if record:
        # The design's own unmet provinces are the anchors: the P7 mover
        # paths toward the nearest one and the existing _can_ai_move_to
        # gate stalls every corps at the last lawful region — the massing
        # EMERGES from the same movement rules every marshal obeys (GR5).
        # Enterable border regions ride along as nearer anchors.
        from backend.game_logic.agendas import get_agenda_military_targets
        from backend.game_logic.diplomacy import can_enter_territory
        targets = [t for t in get_agenda_military_targets(nation, world)
                   if t in world.regions]
        frontier.extend(targets)
        seen = set(targets)
        for target_name in targets:
            region = world.regions.get(target_name)
            if region is None:
                continue
            for adjacent in getattr(region, "adjacent_regions", []) or []:
                if adjacent in seen:
                    continue
                seen.add(adjacent)
                neighbour = world.regions.get(adjacent)
                if neighbour is None:
                    continue
                controller = getattr(neighbour, "controller", None)
                if controller and (controller == nation or can_enter_territory(
                        world, nation, controller)):
                    frontier.append(adjacent)
    cache[nation] = frontier
    return frontier


# ── The per-turn pass ───────────────────────────────────────────────────


def process_war_council(world) -> List[Dict]:
    """The once-per-turn decision pass (sited after the AI-AI diplomatic
    phase in `_advance_turn_internal`). Deckless worlds: `war_intents`
    stays empty and this returns [] — byte-identical (pin 18)."""
    events: List[Dict] = []
    store = getattr(world, "war_intents", None)
    if store is None:
        store = {}
        world.war_intents = store

    player = getattr(world, "player_nation", "France")
    turn = int(getattr(world, "current_turn", 0))

    # ── 1. Poll open crises: pass, escalate, or declare ──
    for coveter in sorted(store.keys()):
        record = store[coveter]
        cause = _crisis_cause_of_death(world, coveter, record)
        if cause is not None:
            _emit_crisis_passed(world, coveter, record, cause, events)
            del store[coveter]
            continue

        preview = can_declare_war(world, coveter, str(record.get("target")))
        if not preview["ok"]:
            if (preview["reason"] == "treaty_in_the_way"
                    and not record.get("treaty_broken_turn")):
                # §4.3a-2: break it first — a visible ladder step. The
                # break is this turn's step; declaration waits.
                from backend.game_logic.diplomacy import break_treaty
                pair_key = world._make_diplo_key(
                    coveter, str(record.get("target")))
                break_result = break_treaty(pair_key, coveter, world)
                if break_result.get("success"):
                    record["treaty_broken_turn"] = turn
                    continue
            # A refused predicate — armistice signed mid-crisis, side
            # conflict, an unbreakable open-movement state (no treaty
            # record / no DP / a second treaty tier under the first) —
            # stalls the crisis; a stall that persists cools it on
            # screen as starved (pin 21 forbids a foregrounded crisis
            # that never ends).
            record["stall_turns"] = int(record.get("stall_turns", 0)) + 1
            if record["stall_turns"] >= CRISIS_HARD_STALL_TURNS:
                _emit_crisis_passed(world, coveter, record, "starved", events)
                del store[coveter]
            continue

        if not record.get("coerce_recorded_turn"):
            if record.get("foregrounded") and turn > int(record.get("opened_turn", turn)):
                _emit_coercive_demand(world, coveter, record, events)
                record["coerce_recorded_turn"] = turn
            continue

        # Declaration gate: foregrounded tenure, ladder, restraints, D1, preview.
        foregrounded_turn = record.get("foregrounded_turn")
        if not record.get("foregrounded") or foregrounded_turn is None:
            continue
        if turn - int(foregrounded_turn) < CRISIS_FOREWARN_TURNS:
            continue
        target = str(record.get("target") or "")
        if (count_ai_initiated_wars(world) >= MAX_SIMULTANEOUS_AI_WARS
                or not _ladder_climbed(world, coveter, target)
                or not _restraints_hold(world, coveter, target)):
            # Review fix [r2 MEDIUM]: the SOFT gates (cap / ladder /
            # restraints) also carry pin 21's termination guarantee — a
            # fully fore-warned crisis that cannot fire for a long spell
            # (the holder permanently at war, an empty chest, a jammed
            # cap) cools on screen instead of freezing the world-wide
            # foreground slot forever. Longer window than the hard
            # predicate: these gates legitimately clear within a few
            # turns (treasuries refill, wars end).
            record["soft_stall_turns"] = int(record.get("soft_stall_turns", 0)) + 1
            if record["soft_stall_turns"] >= CRISIS_SOFT_STALL_TURNS:
                _emit_crisis_passed(world, coveter, record, "starved", events)
                del store[coveter]
            continue
        record["soft_stall_turns"] = 0
        if _declare_design_war(world, coveter, record, events):
            del store[coveter]

    # ── 2. Foreground promotion: one crisis on stage world-wide ──
    if not any(r.get("foregrounded") for r in store.values()):
        waiting = sorted(
            (int(r.get("opened_turn", 0)), coveter)
            for coveter, r in store.items()
        )
        if waiting:
            _, promoted = waiting[0]
            record = store[promoted]
            record["foregrounded"] = True
            record["foregrounded_turn"] = turn
            _emit_crisis_brewing(world, promoted, record, events)

    # ── 3. Open new crises ──
    if getattr(world, "sovereign_map", "legacy") == "europe":
        from backend.game_logic.intent import get_nation_intent
        vassals = set((getattr(world, "vassals", {}) or {}).keys())
        for nation in sorted(world.get_active_nations()):
            if nation == player or nation in vassals or nation in store:
                continue
            view = get_nation_intent(nation, world)
            if (view.price != "fight" or view.survival
                    or view.want_type != "acquire_regions"):
                continue
            target = view.against
            # v1 (§16.2): AI-vs-AI only — a player-targeted design coerces
            # through NA-5 and fights through the coalition, never here.
            if not target or target == player or target in vassals:
                continue
            if world.is_at_war(nation, target):
                continue
            preview = can_declare_war(world, nation, target)
            if not preview["ok"] and preview["reason"] != "treaty_in_the_way":
                continue  # pin 15: never fore-warn a refused predicate
            if not _ladder_climbed(world, nation, target):
                continue
            foreground_free = not any(
                r.get("foregrounded") for r in store.values())
            record = {
                "coveter": nation,
                "target": target,
                "design_id": view.want_id,
                "want_title": view.want_title,
                "opened_turn": turn,
                "foregrounded": bool(foreground_free),
                "foregrounded_turn": turn if foreground_free else None,
                "coerce_recorded_turn": None,
                "treaty_broken_turn": None,
            }
            store[nation] = record
            if foreground_free:
                _emit_crisis_brewing(world, nation, record, events)

    # ── 4. AI instrument producers on the foregrounded crisis ──
    for coveter, record in list(store.items()):
        if record.get("foregrounded"):
            _run_ai_instrument_producers(world, coveter, record, events)

    return events
