"""
Jealousy System v3.2 — marshal grievances, the glory ladder, and the crown.

Spec: docs/JEALOUSY_SPEC.md (v3.1 body BLESSED July 11, 2026; §0 build
record is authoritative where it amends the body).

"Jealousy makes marshals self-serving, not passive." Every marshal tracks a
rolling GLORY score from his battles; each looks one rung UP the nation's
glory ladder and — when the gap crosses his relationship-scaled threshold —
develops a grievance against the man above him. The grievance is a DERIVED
temporary -1 relationship (Marshal.get_relationship, never mutated) plus a
personality expression:

  aggressive -> autonomous glory-attack (warned one turn ahead, +15% solo)
  cautious   -> withholds coordination (the derived -1 does the work)
  literal    -> the Vindicated Garrison: sidelining trigger, obsessive
                patrols (intel enhancement), reassignment briefing

Enemy marshals run the same mechanical core (Building Blocks, spec §9b) —
no popups, no Berthier warnings, faction authority proxy (EC-M).

Evaluation runs ONCE per turn from TurnManager.end_turn(), AFTER strategic
orders and BEFORE advance_turn — every battle of the cycle (player, enemy
phase, strategic, sally) has resolved and per-turn action flags are still
live. The reckless auto-charge (inside advance_turn) records glory at
battle time and is picked up next evaluation.

Golden rules honored: modifiers live in marshal.py (GR1); this module never
writes stored relationships except tier-2 escalation's PERMANENT damage
(via modify_relationship); the AI shares every formula (GR5); marshal-count
loops only (GR8).
"""

import random
from typing import Dict, List, Optional, Tuple

from backend.game_logic import dotation
# One grip = one module (VS-R gate Open Q#5): the shared authority breakpoints
# live in the leaf so jealousy AND vassal anchor on the SAME two lines. Used
# below at _threshold_for; re-exported here for backward compat (J.AUTHORITY_*).
from backend.models.authority import (  # noqa: F401
    AUTHORITY_ACCELERATE_BELOW,
    AUTHORITY_SUPPRESS_ABOVE,
)

# ═══════════════════ BLESSED CONSTANTS (in-band tunable) ═══════════════════

GLORY_WINDOW = 8                    # rolling window (turns) for glory scores
#   DR-2 (Phase 3, spec §3.2): lengthened 5 -> 8 so occasional deeds accrete
#   into a ladder gap instead of evaporating before ambition can form. The
#   window is the ONLY glory-decay lever; nothing else changed.

STALEMATE_GLORY = 1                 # DR-1 (Phase 3): partial glory for a
#   hard-fought inconclusive battle where one side out-bleeds the other >=2:1,
#   or for taking a province without a clean field victory. Feeds the ladder
#   before a decisive rout — the "ground them down over six assaults" campaign
#   the Field Review saw earns laurels. Symmetric (GR5).

# Trigger thresholds by relationship with the target (spec §1).
# None = immune. Hostile additionally requires idle >= HOSTILE_IDLE_TURNS.
THRESHOLDS = {2: None, 1: 4, 0: 2, -1: 1, -2: 1}
HOSTILE_IDLE_TURNS = 2
IDLE_ACCELERATION_TURNS = 3         # idle >= 3 -> threshold -1 (min 1)

# Authority polarity (spec §1, AMENDED at build — §0.2 landing note):
# authority > 70 (AUTHORITY_SUPPRESS_ABOVE) DAMPENS (+1 to every threshold)
# rather than suppressing outright. Boot authority is 100; full immunity would
# leave the system dormant for any winning campaign, contradicting the crown's
# own "reward for excellence creates friction" design (the marshals feuded at
# the height of empire — Auerstedt was 1806). The death-spiral acceleration
# below 30 (AUTHORITY_ACCELERATE_BELOW) is unchanged; capital-threatened remains
# a full suppression (survival overrides pettiness).
# NOTE: both breakpoints now live in backend/models/authority.py (single source,
# imported at the top of this module) so VS-R's satellite coupling anchors on the
# identical lines — crossing 70/30 lights up the marshal board AND the satellite
# board as one felt moment.

DURATION_MIN = 2                    # duration = 2 + (delta - threshold), 2..5
DURATION_MAX = 5

MAX_FIRES_PER_NATION_TURN = 2       # rate limit (spec §1), per nation

LITERAL_HOLD_TRIGGER = 3            # consecutive sidelined turns (spec §3)
LITERAL_RESTLESS_AT = 2             # pre-warning at 2 (spec §5)

AGGRESSIVE_RESOLUTION_RATIO = 0.70  # enemy >= 70% of own strength (EC-K, raw)
CAUTIOUS_ALLY_RESOLUTION = 3        # 3+ same-nation participants incl. self

ESCALATION_LIFETIME_FIRES = 3       # 3rd lifetime fire between a pair
ESCALATION_PERMANENT_LEVEL = 2      # tier 2: permanent -1 both directions
ESCALATION_MUTUAL_LEVEL = 3         # tier 3: mutual spiral

# ESP-1 Fontainebleau (spec §0.3): >=3 player marshals eroding at once.
FONTAINEBLEAU_MIN_ERODING = 3
FONTAINEBLEAU_COOLDOWN = 8          # turns between petitions
FONTAINEBLEAU_CONCEDE_TRUST = 2
FONTAINEBLEAU_REFUSE_TRUST = -8
FONTAINEBLEAU_PROMISE_GRACE = 3     # extra grace turns
FONTAINEBLEAU_PROMISE_AUTHORITY = -2

# ESP-2 war-weary (spec §0.3): fully-met expectation at/above this floor
# turns a marshal into the peace party on NEW player war declarations.
WAR_WEARY_EXPECTATION_FLOOR = 160
WAR_WEARY_MARCH_TRUST = -4
WAR_WEARY_HEED_TRUST = 3

# Confrontation popup (spec §6)
CONFRONT_PROMISE_AP = 1
CONFRONT_PROMISE_DURATION_CUT = 2
CONFRONT_REBUKE_TRUST = -5
CONFRONT_REBUKE_DURATION_CUT = 1


# ═══════════════════════════ GLORY SCORING ═══════════════════════════════

def get_glory_score(marshal, current_turn: int) -> int:
    """Sum of glory points within the rolling window, floored at 0 (spec §1)."""
    total = 0
    for event in getattr(marshal, "glory_events", []):
        if current_turn - int(event.get("turn", 0)) < GLORY_WINDOW:
            total += int(event.get("points", 0))
    return max(0, total)


def prune_glory_events(marshal, current_turn: int) -> None:
    """Drop events older than the window (bounded list, GR8-safe)."""
    marshal.glory_events = [
        e for e in getattr(marshal, "glory_events", [])
        if current_turn - int(e.get("turn", 0)) < GLORY_WINDOW
    ]


def _append_glory(marshal, turn: int, points: int) -> None:
    if marshal is None or points == 0:
        return
    marshal.glory_events.append({"turn": int(turn), "points": int(points)})


def _victory_points(casualties_own: int, casualties_enemy: int,
                    conquered: bool, outnumbered: bool,
                    is_garrison_stomp: bool) -> int:
    """Glory for a victory (spec §1). Garrison stomps earn nothing."""
    if is_garrison_stomp:
        return 0
    points = 1
    if casualties_own > 0 and casualties_enemy >= 2 * casualties_own:
        points += 1          # decisive win (>= 2:1 in your favor)
    elif casualties_own == 0 and casualties_enemy > 0:
        points += 1          # flawless counts as decisive
    if conquered:
        points += 1          # territory taken
    if outnumbered:
        points += 1          # won against the odds
    return points


def _out_bled(own_casualties: int, enemy_casualties: int) -> bool:
    """True when this side inflicted >=2x the losses it took (DR-1, spec §3.2).
    A flawless exchange (took nothing, dealt something) counts."""
    if own_casualties <= 0:
        return enemy_casualties > 0
    return enemy_casualties >= 2 * own_casualties


def _defeat_points(casualties_own: int, casualties_enemy: int,
                   territory_lost: bool, outnumbered: bool) -> int:
    """Glory lost on a defeat (spec §1 v3.1). Outnumbered losses carry no
    stigma — the shame is in losing battles you should have won."""
    if outnumbered:
        return 0
    points = -1
    if casualties_enemy > 0 and casualties_own >= 2 * casualties_enemy:
        points -= 1          # decisive loss — humiliation
    if territory_lost:
        points -= 1
    return points


def record_battle_glory(world, attacker, defender, attacker_won: bool,
                        defender_won: bool, attacker_casualties: int,
                        defender_casualties: int, conquered: bool,
                        is_garrison: bool, pre_attacker_strength: int,
                        pre_defender_strength: int,
                        attacker_participants: Optional[List] = None,
                        defender_participants: Optional[List] = None) -> None:
    """Record glory for a resolved battle. Runs AFTER the Win/Loss
    relationship step (EC-F ordering) from every combat path.

    Primaries score the full formula; non-primary participants
    (coordination/reinforcement) record base +/-1 only (spec §0.2 item 4).
    Defensive victories score normally (EC-A); the garrison-stomp exemption
    applies only to an attacker beating a garrison (is_garrison ctx).
    """
    turn = int(world.current_turn)
    atk_outnumbered = pre_attacker_strength < pre_defender_strength
    def_outnumbered = pre_defender_strength < pre_attacker_strength

    if attacker is not None:
        if attacker_won:
            _append_glory(attacker, turn, _victory_points(
                attacker_casualties, defender_casualties,
                conquered, atk_outnumbered, is_garrison))
        elif defender_won:
            _append_glory(attacker, turn, _defeat_points(
                attacker_casualties, defender_casualties,
                territory_lost=False, outnumbered=atk_outnumbered))

    if defender is not None:
        if defender_won:
            _append_glory(defender, turn, _victory_points(
                defender_casualties, attacker_casualties,
                conquered=False, outnumbered=def_outnumbered,
                is_garrison_stomp=False))
        elif attacker_won:
            _append_glory(defender, turn, _defeat_points(
                defender_casualties, attacker_casualties,
                territory_lost=conquered, outnumbered=def_outnumbered))

    # DR-1 (Phase 3, spec §3.2): a hard-fought INCONCLUSIVE battle still feeds
    # the ladder. Neither primary achieved a decisive result, but the commander
    # who out-bled the other >=2:1 — or who took the province off an uncontested
    # occupation — earns partial glory. Symmetric (GR5): whichever side
    # dominated the exchange is rewarded. This is what breaks lock 1 of the
    # triple lock (stalemate == zero glory) so a grinding campaign accretes.
    if not attacker_won and not defender_won:
        if attacker is not None and (
                conquered
                or _out_bled(attacker_casualties, defender_casualties)):
            _append_glory(attacker, turn, STALEMATE_GLORY)
        elif defender is not None and _out_bled(defender_casualties,
                                                attacker_casualties):
            _append_glory(defender, turn, STALEMATE_GLORY)

    # Non-primary participants: base +/-1 (shared the field, not the command).
    for participant in (attacker_participants or []):
        if attacker is not None and participant.name == attacker.name:
            continue
        if attacker_won:
            _append_glory(participant, turn, 1)
        elif defender_won:
            _append_glory(participant, turn, -1)
    for participant in (defender_participants or []):
        if defender is not None and participant.name == defender.name:
            continue
        if defender_won:
            _append_glory(participant, turn, 1)
        elif attacker_won:
            _append_glory(participant, turn, -1)


# ═══════════════════════════ THE LADDER ═══════════════════════════════════

def get_nation_ladder(world, nation: str) -> List[Tuple[object, int]]:
    """(marshal, glory) for a nation's standing marshals, highest first.
    Ties keep dict order (stable)."""
    entries = []
    for marshal in world.marshals.values():
        if marshal.nation != nation or marshal.strength <= 0:
            continue
        if getattr(marshal, "captured_by", ""):
            continue
        entries.append((marshal, get_glory_score(marshal, world.current_turn)))
    entries.sort(key=lambda pair: -pair[1])
    return entries


def find_jealousy_target(marshal, world):
    """The marshal ONE RUNG ABOVE on the glory ladder (spec §1 v3).

    Ties on the ladder never trigger each other; a marshal below a tie
    targets the tied marshal he has the WORSE relationship with, then
    alphabetical (spec §1 Ties).
    """
    my_glory = get_glory_score(marshal, world.current_turn)
    target = None
    target_glory = None
    for other in world.marshals.values():
        if (other.nation != marshal.nation or other.name == marshal.name
                or other.strength <= 0
                or getattr(other, "captured_by", "")
                or getattr(other, "broken", False)
                or getattr(other, "retreated_this_turn", False)):
            continue
        other_glory = get_glory_score(other, world.current_turn)
        if other_glory <= my_glory:
            continue
        if target_glory is None or other_glory < target_glory:
            target, target_glory = other, other_glory
        elif other_glory == target_glory:
            # worse relationship wins the tiebreak, then alphabetical
            cur = marshal.get_relationship(target.name)
            new = marshal.get_relationship(other.name)
            if new < cur or (new == cur and other.name < target.name):
                target = other
    return target


def recompute_crowns(world) -> List[Dict]:
    """Crowned with Glory (spec §1 + §0.2 item 1): the #1 marshal per
    nation (glory > 0) carries +1 shock/defense/administration. Returns
    change events for the player's own nation."""
    events = []
    nations = {m.nation for m in world.marshals.values()}
    for nation in nations:
        ladder = get_nation_ladder(world, nation)
        holder = None
        if ladder and ladder[0][1] > 0:
            # a tie for the top leaves the crown vacant — no one is
            # "the most celebrated" while two men share the laurels
            if len(ladder) == 1 or ladder[0][1] > ladder[1][1]:
                holder = ladder[0][0]
        for marshal in world.marshals.values():
            if marshal.nation != nation:
                continue
            was = bool(getattr(marshal, "glory_crowned", False))
            now = holder is not None and marshal.name == holder.name
            if was == now:
                continue
            marshal.glory_crowned = now
            if marshal.nation == world.player_nation:
                if now:
                    events.append({
                        "type": "glory_crowned",
                        "message": (
                            f"Berthier notes that {marshal.name}'s recent "
                            f"victories have made him the most celebrated "
                            f"commander in the army. (+1 shock, +1 defense, "
                            f"+1 administration while he holds the laurels)"),
                        "nation": marshal.nation,
                        "marshal": marshal.name,
                    })
                    world.log_event({
                        "type": "glory_crowned",
                        "marshal": marshal.name,
                        "nation": marshal.nation,
                    })
                else:
                    events.append({
                        "type": "glory_crown_lost",
                        "message": (
                            f"{marshal.name} is no longer the army's most "
                            f"celebrated commander — the laurels have passed."),
                        "nation": marshal.nation,
                        "marshal": marshal.name,
                    })
    return events


# ═══════════════════════ AUTHORITY & SUPPRESSION ══════════════════════════

def get_authority_proxy(world, nation: str) -> int:
    """Player: the real tracker. Enemy: the EC-M faction proxy —
    capital + majority of home regions = 75 (suppresses), lost capital or
    majority = 25 (accelerates), otherwise 50. Reconstructed from
    nation_starting_regions, never serialized."""
    if nation == world.player_nation:
        return int(world.authority_tracker.authority)
    home = list(world.nation_starting_regions.get(nation, []) or [])
    if not home:
        return 50
    capital = world.get_nation_capital(nation)
    capital_region = world.regions.get(capital) if capital else None
    capital_held = bool(capital_region and capital_region.controller == nation)
    held = 0
    for region_name in home:
        region = world.regions.get(region_name)
        if region is not None and region.controller == nation:
            held += 1
    majority = held * 2 > len(home)
    if capital_held and majority:
        return 75
    if (not capital_held) or (held * 2 < len(home)):
        return 25
    return 50


def is_capital_threatened(world, nation: str) -> bool:
    """An at-war enemy marshal stands in or adjacent to the nation's
    capital — survival overrides pettiness (spec §1, EC-H)."""
    capital = world.get_nation_capital(nation)
    region = world.regions.get(capital) if capital else None
    if region is None:
        return False
    adjacent = set(getattr(region, "adjacent_regions", []) or [])
    for marshal in world.marshals.values():
        if marshal.strength <= 0 or getattr(marshal, "captured_by", ""):
            continue
        if marshal.nation == nation:
            continue
        if not world.is_at_war(nation, marshal.nation):
            continue
        if marshal.location == capital or marshal.location in adjacent:
            return True
    return False


def _is_standing(marshal) -> bool:
    return (marshal.strength > 0
            and not getattr(marshal, "captured_by", "")
            and not getattr(marshal, "broken", False)
            and not getattr(marshal, "retreating", False))


# ═══════════════════════ TRIGGER EVALUATION ═══════════════════════════════

def _threshold_for(marshal, target, authority: int) -> Optional[Tuple[int, bool]]:
    """(threshold, requires_idle) for this pair, or None when immune.
    Relationship-scaled (spec §1), idle-accelerated, authority-shaped."""
    rel = marshal.get_relationship(target.name)
    base = THRESHOLDS.get(rel, 2)
    if base is None:
        return None                      # Devoted — immune
    requires_idle = (rel <= -2)
    if authority < AUTHORITY_ACCELERATE_BELOW:
        # Losing breeds infighting: every threshold collapses to 1 and the
        # hostile idle gate is waived (§0 build decision — acceleration
        # never ADDS gates).
        return 1, False
    # DR-3 (Phase 3, spec §3.2): the "first rung" is exempt from the winning
    # calm. A marshal who ALREADY resents the celebrated man — a Rival (-1) or
    # Hostile (-2), relationship-base threshold 1 — keeps his hair-trigger edge
    # even at the height of empire; his ambition is not anesthetized by the
    # Emperor's success (the marshals feuded through the victories — Auerstedt
    # was 1806). Only the neutral/friendly professionals (rung >= 2) are calmed.
    # Exemption is keyed on the RELATIONSHIP base, before idle acceleration, so
    # an idle professional turned hair-trigger is still dampened while winning.
    hair_trigger = base == 1
    if getattr(marshal, "idle_turns", 0) >= IDLE_ACCELERATION_TURNS:
        base = max(1, base - 1)
    if authority > AUTHORITY_SUPPRESS_ABOVE and not hair_trigger:
        # Winning calms the professionals (+1 to their threshold) — it does not
        # anesthetize the army (§0.2 build amendment, DR-3 refinement).
        base += 1
    return base, requires_idle


def update_literal_hold_counters(world) -> None:
    """The Literal sidelining counter (spec §3): consecutive turns on
    HOLD/no-order while at least one same-nation peer is actively engaged
    (non-HOLD strategic order OR fought/moved this turn — EC-D: if ALL are
    idle, nobody is being singled out). Runs for every nation (GR5)."""
    by_nation: Dict[str, List] = {}
    for marshal in world.marshals.values():
        if _is_standing(marshal):
            by_nation.setdefault(marshal.nation, []).append(marshal)
    for nation, marshals in by_nation.items():
        def _engaged(m) -> bool:
            order = getattr(m, "strategic_order", None)
            if order is not None and getattr(order, "command_type", "HOLD") != "HOLD":
                return True
            if getattr(m, "attacks_this_turn", 0):
                return True
            if getattr(m, "moved_this_turn", False):
                return True
            return bool(getattr(m, "in_combat_this_turn", False))

        engaged_names = {m.name for m in marshals if _engaged(m)}
        for marshal in marshals:
            if marshal.personality != "literal":
                marshal.consecutive_hold_turns = 0
                continue
            order = getattr(marshal, "strategic_order", None)
            sidelined = (order is None
                         or getattr(order, "command_type", "") == "HOLD")
            if marshal.name in engaged_names:
                sidelined = False
            others_engaged = bool(engaged_names - {marshal.name})
            if sidelined and others_engaged:
                marshal.consecutive_hold_turns += 1
            else:
                marshal.consecutive_hold_turns = 0


def _literal_trigger_ready(marshal) -> bool:
    return (marshal.personality == "literal"
            and marshal.consecutive_hold_turns >= LITERAL_HOLD_TRIGGER)


def _duration_for(delta: int, threshold: int) -> int:
    return max(DURATION_MIN, min(DURATION_MAX,
                                 DURATION_MIN + (delta - threshold)))


# ═══════════════════════ APPLY / CLEAR / ESCALATE ═════════════════════════

def _pair_key(name_a: str, name_b: str) -> str:
    return "|".join(sorted([name_a, name_b]))


def get_escalation_level(marshal, target_name: str) -> int:
    levels = getattr(marshal, "jealousy_history", {}).get("__levels__", {})
    return int(levels.get(target_name, 0))


def _set_escalation_level(marshal, target_name: str, level: int) -> None:
    levels = marshal.jealousy_history.setdefault("__levels__", {})
    levels[target_name] = int(level)


def _lifetime_fires(marshal, target_name: str) -> int:
    fires = getattr(marshal, "jealousy_history", {}).get(target_name, [])
    return len(fires)


def apply_jealousy(world, marshal, target, delta: int, threshold: int,
                   events: List[Dict], forced: bool = False) -> None:
    """Set the grievance: fields, history, escalation, expression setup,
    dispatch/campaign-log events. The -1 relationship is DERIVED from
    jealous_of (spec §0.2 item 2) — nothing to mutate here."""
    turn = int(world.current_turn)
    marshal.jealous_of = target.name
    marshal.jealousy_turns_remaining = _duration_for(delta, threshold)
    marshal.jealousy_history.setdefault(target.name, []).append(turn)

    is_player = marshal.nation == world.player_nation
    expression = {
        "aggressive": "restless for glory",
        "cautious": "grown cold and withholding",
        "literal": "thrown himself into his post with obsessive diligence",
    }.get(marshal.personality, "resentful")

    world.log_event({
        "type": "jealousy_fired",
        "marshal": marshal.name,
        "target": target.name,
        "nation": marshal.nation,
        "personality": marshal.personality,
    })
    if is_player:
        events.append({
            "type": "jealousy_fired",
            "message": (
                f"Berthier reports that {marshal.name} appears envious of "
                f"{target.name}'s laurels — he has {expression}."),
            "nation": marshal.nation,
            "marshal": marshal.name,
            "target": target.name,
        })
        # Target notification (spec §5 v3) — informational, no penalty.
        events.append({
            "type": "jealousy_target_notice",
            "message": (
                f"Berthier notes that {target.name}'s recent victories have "
                f"attracted... attention among the marshals. {marshal.name} "
                f"in particular seems restless."),
            "nation": marshal.nation,
            "marshal": target.name,
        })

    _check_escalation(world, marshal, target, events, forced=forced)

    # First-time confrontation popup (spec §6) — player pairs only, one
    # petition slot at a time; unseen pairs retry on later turns.
    if is_player and not forced:
        seen = set(getattr(world, "jealousy_confrontations_seen", []) or [])
        key = _pair_key(marshal.name, target.name)
        if key not in seen and getattr(world, "pending_marshal_petition", None) is None:
            queue_confrontation_petition(world, marshal, target)
            seen.add(key)
            world.jealousy_confrontations_seen = sorted(seen)


def _check_escalation(world, marshal, target, events: List[Dict],
                      forced: bool = False) -> None:
    """Escalation (spec §10): qualifying fire = stored relationship already
    Rival-or-worse OR 3rd lifetime fire. Levels advance 1 -> 2 -> 3."""
    stored_rel = marshal.relationships.get(target.name, 0)
    fires = _lifetime_fires(marshal, target.name)
    qualifies = stored_rel <= -1 or fires >= ESCALATION_LIFETIME_FIRES
    if not qualifies:
        return
    level = min(ESCALATION_MUTUAL_LEVEL,
                max(get_escalation_level(marshal, target.name),
                    get_escalation_level(target, marshal.name)) + 1)
    _set_escalation_level(marshal, target.name, level)
    _set_escalation_level(target, marshal.name, level)

    is_player = marshal.nation == world.player_nation
    if level == 1 and is_player:
        events.append({
            "type": "jealousy_escalation",
            "message": (
                f"Sire, the rivalry between {marshal.name} and {target.name} "
                f"has become a matter of concern among the general staff. "
                f"Their cooperation cannot be relied upon."),
            "nation": marshal.nation,
            "marshal": marshal.name,
            "target": target.name,
        })
    elif level == ESCALATION_PERMANENT_LEVEL:
        # Permanent -1 both directions (does NOT restore on resolution).
        change_a = marshal.modify_relationship(target.name, -1)
        change_b = target.modify_relationship(marshal.name, -1)
        if is_player:
            events.append({
                "type": "jealousy_escalation",
                "message": (
                    f"The rivalry between {marshal.name} and {target.name} "
                    f"has become entrenched. The wound will not close on "
                    f"its own."),
                "nation": marshal.nation,
                "marshal": marshal.name,
                "target": target.name,
            })
        if change_a or change_b:
            check_rivalry_transitions(world, [
                {"marshal": marshal.name, "toward": target.name,
                 "change": change_a,
                 "new_value": marshal.relationships.get(target.name, 0),
                 "nation": marshal.nation},
                {"marshal": target.name, "toward": marshal.name,
                 "change": change_b,
                 "new_value": target.relationships.get(marshal.name, 0),
                 "nation": target.nation},
            ])
    elif level >= ESCALATION_MUTUAL_LEVEL and not forced:
        # Mutual spiral: the target automatically resents him right back,
        # target override (spec §10 tier 3), full expression.
        if _is_standing(target) and getattr(target, "jealous_of", None) != marshal.name:
            apply_jealousy(world, target, marshal,
                           delta=1, threshold=1, events=events, forced=True)
            if is_player:
                events.append({
                    "type": "jealousy_escalation",
                    "message": (
                        f"The feud between {marshal.name} and {target.name} "
                        f"is now mutual — each schemes against the other. "
                        f"Separate them, Sire, or accept the friction."),
                    "nation": marshal.nation,
                    "marshal": marshal.name,
                    "target": target.name,
                })
    world.log_event({
        "type": "jealousy_escalation",
        "marshal": marshal.name,
        "target": target.name,
        "nation": marshal.nation,
        "level": get_escalation_level(marshal, target.name),
    })


def clear_jealousy(world, marshal, resolved_by_action: bool,
                   events: Optional[List[Dict]] = None,
                   reason: str = "") -> None:
    """Clear the grievance. Action resolutions grant the 1-turn surge
    (spec §4); timer expiry grants nothing. The derived -1 restores
    itself the moment jealous_of clears."""
    target_name = marshal.jealous_of
    marshal.jealous_of = None
    marshal.jealousy_turns_remaining = 0
    marshal.jealousy_autonomous_warned = False
    if resolved_by_action:
        marshal.jealousy_surge_turns = 1
    is_player = marshal.nation == world.player_nation
    world.log_event({
        "type": "jealousy_resolved",
        "marshal": marshal.name,
        "target": target_name,
        "nation": marshal.nation,
        "by_action": bool(resolved_by_action),
        "reason": reason,
    })
    if is_player and events is not None:
        if resolved_by_action:
            surge_note = {
                "aggressive": "He fights with renewed purpose (+10% attack this turn).",
                "cautious": "He holds with renewed purpose (+10% defense this turn).",
                "literal": "His patrols keep their edge one turn more.",
            }.get(marshal.personality, "")
            events.append({
                "type": "jealousy_resolved",
                "message": (
                    f"{marshal.name}'s grievance is satisfied — "
                    f"{reason or 'he has proven himself'}. {surge_note}"),
                "nation": marshal.nation,
                "marshal": marshal.name,
            })
        else:
            events.append({
                "type": "jealousy_resolved",
                "message": (
                    f"{marshal.name}'s resentment of {target_name} has "
                    f"cooled with time."),
                "nation": marshal.nation,
                "marshal": marshal.name,
            })


# ═══════════════════ BATTLE-TIME RESOLUTION (spec §3) ═════════════════════

def check_battle_resolution(world, attacker, defender, attacker_won: bool,
                            defender_won: bool, pre_attacker_strength: int,
                            pre_defender_strength: int,
                            attacker_participants: Optional[List] = None,
                            defender_participants: Optional[List] = None,
                            defender_broken: bool = False) -> None:
    """Per-personality action resolution, checked at battle time BEFORE the
    Win/Loss relationship step (EC-F: the derived -1 restores before the
    battle's relationship processing when the battle itself resolves the
    grievance).

    aggressive: win where enemy raw strength >= 70% of yours (EC-K,
                primary-vs-primary pre-battle strengths, no stomps)
    cautious:   shared victory with the target, OR a winning battle with
                3+ same-nation participants (EC-L)
    literal:    enemy contact — any battle participation (attack, defense
                survived unbroken, strategic-order battle)
    """
    events = _pending_events(world)

    winning_side = []
    if attacker_won:
        winning_side = [attacker] + [
            p for p in (attacker_participants or [])
            if attacker is None or p.name != attacker.name]
        qualifying = (pre_attacker_strength > 0 and
                      pre_defender_strength >= AGGRESSIVE_RESOLUTION_RATIO
                      * pre_attacker_strength)
    elif defender_won:
        winning_side = [defender] + [
            p for p in (defender_participants or [])
            if defender is None or p.name != defender.name]
        qualifying = (pre_defender_strength > 0 and
                      pre_attacker_strength >= AGGRESSIVE_RESOLUTION_RATIO
                      * pre_defender_strength)
    else:
        qualifying = False

    winning_side = [m for m in winning_side if m is not None]
    winner_names = {m.name for m in winning_side}

    for marshal in winning_side:
        if not getattr(marshal, "jealous_of", None):
            continue
        if marshal.personality == "aggressive" and qualifying:
            clear_jealousy(world, marshal, resolved_by_action=True,
                           events=events,
                           reason="a victory against a worthy foe")
        elif marshal.personality == "cautious":
            shared = marshal.jealous_of in winner_names
            team = len([m for m in winning_side
                        if m.nation == marshal.nation])
            if shared or team >= CAUTIOUS_ALLY_RESOLUTION:
                clear_jealousy(world, marshal, resolved_by_action=True,
                               events=events,
                               reason="a victory won shoulder to shoulder")

    # Literal: enemy contact resolves regardless of outcome — attacking,
    # or defending without breaking (the enemy validated his post).
    for marshal, participants, was_defender in (
            (attacker, attacker_participants, False),
            (defender, defender_participants, True)):
        side = ([marshal] if marshal is not None else []) + list(participants or [])
        for m in side:
            if m is None or not getattr(m, "jealous_of", None):
                continue
            if m.personality != "literal":
                continue
            if was_defender and defender_broken and marshal is not None \
                    and m.name == marshal.name:
                continue        # broken on defense — no vindication
            clear_jealousy(world, m, resolved_by_action=True, events=events,
                           reason="meaningful contact with the enemy")


# ═══════════════════ RIVALRY CONFRONTATION (§6b) ══════════════════════════

def check_rivalry_transitions(world, changes: Optional[List[Dict]]) -> None:
    """§6b: a PLAYER pair's stored relationship transitioned DOWNWARD to
    Rival (-1) or Hostile (-2) — queue the rivalry confrontation event,
    once per transition per pair (world.rivalry_transitions_seen)."""
    if not changes:
        return
    for change in changes:
        if not isinstance(change, dict):
            continue
        if int(change.get("change", 0)) >= 0:
            continue
        new_value = int(change.get("new_value", 0))
        if new_value not in (-1, -2):
            continue
        name_a = change.get("marshal")
        name_b = change.get("toward")
        marshal = world.marshals.get(name_a)
        other = world.marshals.get(name_b)
        if marshal is None or other is None:
            continue
        if marshal.nation != world.player_nation \
                or other.nation != world.player_nation:
            continue
        seen = set(getattr(world, "rivalry_transitions_seen", []) or [])
        key = f"{_pair_key(name_a, name_b)}@{new_value}"
        if key in seen:
            continue
        if getattr(world, "pending_marshal_petition", None) is not None:
            continue            # one petition at a time; transition stays unseen
        seen.add(key)
        world.rivalry_transitions_seen = sorted(seen)
        queue_rivalry_petition(world, marshal, other, new_value)


# ═══════════════════ PETITION CHANNEL (spec §0.2 item 10) ═════════════════
#
# ONE popup pipeline serves the jealousy confrontation (§6), the rivalry
# confrontation (§6b), the Fontainebleau petition (ESP-1), and the
# war-weary petition (ESP-2): world.pending_marshal_petition +
# a marshal_petition PopupQueue entry + POST /marshal_petition_response +
# one Godot scene with dynamic option buttons.


def _player_ap(world) -> int:
    return int(getattr(world, "actions_remaining", 0))


def _spend_player_ap(world, amount: int) -> bool:
    current = int(getattr(world, "actions_remaining", 0))
    if current < amount:
        return False
    world.actions_remaining = current - amount
    return True


def _push_petition(world, petition: Dict) -> None:
    world.pending_marshal_petition = petition
    queue = getattr(world, "_popup_queue", None)
    if queue is not None:
        queue.push("pending_marshal_petition", petition)


def queue_confrontation_petition(world, marshal, target) -> None:
    """First-time jealousy confrontation (spec §6)."""
    ap = _player_ap(world)
    if marshal.personality == "aggressive":
        body = (f"Sire, {marshal.name} has expressed... displeasure about "
                f"{target.name}'s recent recognition. He requests a command "
                f"worthy of his talents.")
        promise_label = "Promise Glory"
        rebuke_rider = ("He will not act on his own this cycle — he "
                        "respects the Emperor's anger, briefly.")
    elif marshal.personality == "literal":
        body = (f"Sire, {marshal.name}'s dispatches have become unusually "
                f"detailed — obsessively so. Staff report he feels his "
                f"current assignment is... beneath his abilities.")
        promise_label = "Reassign"
        rebuke_rider = "His patrols pause a turn in reluctant compliance."
    else:
        body = (f"Sire, {marshal.name} has expressed reservations about the "
                f"recognition afforded to {target.name}. He requests that "
                f"his contributions be... noted.")
        promise_label = "Promise Glory"
        rebuke_rider = ""
    _push_petition(world, {
        "kind": "jealousy_confrontation",
        "title": f"Marshal {marshal.name} seeks an audience",
        "body": body,
        "speaker": marshal.name,
        "options": [
            {"id": "acknowledge", "label": "Acknowledge",
             "detail": "The grievance runs its course.", "cost_note": "",
             "enabled": True},
            {"id": "promise", "label": promise_label,
             "detail": f"His patience is bought — the grievance shortens by "
                       f"{CONFRONT_PROMISE_DURATION_CUT} turns.",
             "cost_note": f"{CONFRONT_PROMISE_AP} AP",
             "enabled": ap >= CONFRONT_PROMISE_AP},
            {"id": "rebuke", "label": "Rebuke",
             "detail": (f"Trust {CONFRONT_REBUKE_TRUST}. The grievance "
                        f"shortens by {CONFRONT_REBUKE_DURATION_CUT} turn. "
                        + rebuke_rider).strip(),
             "cost_note": "", "enabled": True},
        ],
        "context": {"marshal": marshal.name, "target": target.name},
        "turn": int(world.current_turn),
    })


def queue_rivalry_petition(world, marshal, other, new_value: int) -> None:
    """§6b rivalry confrontation on a downward transition."""
    ap = _player_ap(world)
    if new_value == -1:
        body = (f"Sire, harsh words were exchanged between {marshal.name} "
                f"and {other.name} before the general staff.")
        options = [
            {"id": "let_be", "label": "Let Them Sort It Out",
             "detail": "Most likely they simmer; it may yet escalate — or mend.",
             "cost_note": "", "enabled": True},
            {"id": "mediate", "label": "Mediate",
             "detail": "Your authority decides whether they listen.",
             "cost_note": "1 AP", "enabled": ap >= 1},
            {"id": "reprimand", "label": "Reprimand Both",
             "detail": "Trust -3 on both — anger redirected at you may mend the breach.",
             "cost_note": "", "enabled": True},
        ]
    else:
        body = (f"Sire, {marshal.name} has refused to attend council where "
                f"{other.name} is present. The breach may be beyond repair.")
        options = [
            {"id": "accept_breach", "label": "Accept the Breach",
             "detail": "They settle into cold war; one may turn openly discontent.",
             "cost_note": "", "enabled": True},
            {"id": "force_reconciliation", "label": "Force Reconciliation",
             "detail": "A public gamble on your authority.",
             "cost_note": "2 AP", "enabled": ap >= 2},
            {"id": "separate", "label": "Separate Them",
             "detail": ("Not a fix — Berthier will warn you whenever their "
                        "commands stand together."),
             "cost_note": "", "enabled": True},
        ]
    _push_petition(world, {
        "kind": "rivalry_confrontation",
        "title": "A rivalry among the marshals",
        "body": body,
        "speaker": marshal.name,
        "options": options,
        "context": {"marshal": marshal.name, "other": other.name,
                    "new_value": int(new_value)},
        "turn": int(world.current_turn),
    })


def queue_fontainebleau_petition(world, eroding: List) -> None:
    """ESP-1: the collective petition — the moment the parallel silent
    trust bleeds find one voice."""
    names = [m.name for m in eroding]
    roll = ", ".join(names[:-1]) + f" and {names[-1]}" if len(names) > 1 else names[0]
    total_shortfall = sum(dotation.get_shortfall(m, world) for m in eroding)
    rente_bill = sum(dotation.get_rente_cost(dotation.get_shortfall(m, world))
                     for m in eroding)
    _push_petition(world, {
        "kind": "fontainebleau",
        "title": "The marshals petition the Emperor",
        "body": (f"Sire, the marshals come together: {roll} stand unrewarded "
                 f"while the Empire feeds on their victories. They ask for "
                 f"estates, rentes, or peace — {total_shortfall}g/turn of "
                 f"expectation stands unmet. The army does not march on "
                 f"glory alone."),
        "speaker": names[0],
        "options": [
            {"id": "concede", "label": "\"I will find the means\"",
             "detail": (f"Every petitioner receives a rente at his shortfall "
                        f"(+{FONTAINEBLEAU_CONCEDE_TRUST} trust each). The "
                        f"treasury will carry ~{rente_bill}g/turn."),
             "cost_note": "", "enabled": True},
            {"id": "refuse", "label": "\"The Empire does not beg\"",
             "detail": f"Trust {FONTAINEBLEAU_REFUSE_TRUST} on every "
                       f"petitioner. The erosion continues.",
             "cost_note": "", "enabled": True},
            {"id": "promise", "label": "\"The next conquest is yours\"",
             "detail": (f"Their patience extends {FONTAINEBLEAU_PROMISE_GRACE} "
                        f"turns; the court hears you buy time with words "
                        f"(authority {FONTAINEBLEAU_PROMISE_AUTHORITY})."),
             "cost_note": "", "enabled": True},
        ],
        "context": {"marshals": names},
        "turn": int(world.current_turn),
    })
    world.log_event({
        "type": "fontainebleau_petition",
        "marshals": names,
        "nation": world.player_nation,
    })


def check_fontainebleau(world, events: List[Dict]) -> None:
    """ESP-1 trigger: >=3 player marshals eroding on the same tick.
    Latched — re-arms only after the eroding count drops below the
    threshold — plus a hard cooldown."""
    if not dotation.is_dotation_world(world):
        return
    eroding = [m for m in world.marshals.values()
               if m.nation == world.player_nation
               and m.strength > 0
               and not getattr(m, "captured_by", "")
               and dotation.is_eroding(m, world)]
    armed = bool(getattr(world, "_fontainebleau_armed", True))
    if len(eroding) < FONTAINEBLEAU_MIN_ERODING:
        world._fontainebleau_armed = True
        return
    last = int(getattr(world, "fontainebleau_last_turn", -999))
    if not armed or world.current_turn - last < FONTAINEBLEAU_COOLDOWN:
        return
    if getattr(world, "pending_marshal_petition", None) is not None:
        return
    world.fontainebleau_last_turn = int(world.current_turn)
    world._fontainebleau_armed = False
    queue_fontainebleau_petition(world, eroding)
    events.append({
        "type": "fontainebleau_petition",
        "message": ("The marshals have come together, Sire — a collective "
                    "petition awaits your answer."),
        "nation": world.player_nation,
    })


def find_war_weary_objector(world):
    """ESP-2: the highest-expectation marshal whose expectation is fully
    met AND large — the man with the duchy who wants no new war."""
    best = None
    for marshal in world.marshals.values():
        if marshal.nation != world.player_nation or marshal.strength <= 0:
            continue
        if getattr(marshal, "captured_by", ""):
            continue
        expectation = dotation.get_expectation(marshal)
        if expectation < WAR_WEARY_EXPECTATION_FLOOR:
            continue
        if dotation.get_satisfaction(marshal, world) < expectation:
            continue
        if best is None or expectation > dotation.get_expectation(best):
            best = marshal
    return best


def queue_war_weary_petition(world, marshal, target_nation: str,
                             original_command: Dict) -> Dict:
    """ESP-2 petition, returned into the command result (the declare-war
    command does not execute until answered)."""
    title = dotation.derive_title(marshal.dotation_regions[0]) \
        if getattr(marshal, "dotation_regions", []) else "his rente"
    petition = {
        "kind": "war_weary",
        "title": f"Marshal {marshal.name} counsels peace",
        "body": (f"Sire, {marshal.name} — {title} secured, his household "
                 f"provided for — begs you reconsider this war with "
                 f"{target_nation}: \"I have my duchy, Sire. Why do we "
                 f"march again?\""),
        "speaker": marshal.name,
        "options": [
            {"id": "march_anyway", "label": "\"We march\"",
             "detail": f"The war is declared. {marshal.name} obeys — "
                       f"trust {WAR_WEARY_MARCH_TRUST}.",
             "cost_note": "", "enabled": True},
            {"id": "stand_down", "label": "Heed him",
             "detail": f"No war is declared. {marshal.name}'s counsel is "
                       f"honored — trust +{WAR_WEARY_HEED_TRUST}.",
             "cost_note": "", "enabled": True},
        ],
        "context": {"marshal": marshal.name, "target_nation": target_nation,
                    "original_command": original_command or {}},
        "turn": int(world.current_turn),
    }
    _push_petition(world, petition)
    return petition


def handle_petition_response(world, choice: str, executor=None,
                             game_state=None) -> Dict:
    """Apply a marshal-petition answer. ONE dispatch point for all four
    petition kinds (spec §0.2 item 10). Returns a result dict for
    build_base_response."""
    petition = getattr(world, "pending_marshal_petition", None)
    if not petition:
        return {"success": False,
                "message": "No marshal petition awaits an answer."}
    option_ids = {o.get("id") for o in petition.get("options", [])}
    if choice not in option_ids:
        return {"success": False,
                "message": f"Unknown answer '{choice}'.",
                "marshal_petition": petition}
    kind = petition.get("kind")
    context = petition.get("context", {}) or {}
    world.pending_marshal_petition = None
    queue = getattr(world, "_popup_queue", None)
    if queue is not None:
        queue.set("pending_marshal_petition", None)

    if kind == "jealousy_confrontation":
        return _apply_confrontation_choice(world, choice, context)
    if kind == "rivalry_confrontation":
        return _apply_rivalry_choice(world, choice, context)
    if kind == "fontainebleau":
        return _apply_fontainebleau_choice(world, choice, context)
    if kind == "war_weary":
        return _apply_war_weary_choice(world, choice, context,
                                       executor=executor,
                                       game_state=game_state)
    return {"success": False, "message": f"Unknown petition kind '{kind}'."}


def _apply_confrontation_choice(world, choice: str, context: Dict) -> Dict:
    marshal = world.marshals.get(context.get("marshal"))
    if marshal is None:
        return {"success": True, "message": "The moment has passed."}
    if choice == "promise":
        if not _spend_player_ap(world, CONFRONT_PROMISE_AP):
            return {"success": False,
                    "message": "Not enough action points to promise glory."}
        marshal.jealousy_turns_remaining = max(
            0, marshal.jealousy_turns_remaining - CONFRONT_PROMISE_DURATION_CUT)
        if marshal.jealousy_turns_remaining == 0 and marshal.jealous_of:
            clear_jealousy(world, marshal, resolved_by_action=False,
                           events=_pending_events(world),
                           reason="the Emperor's promise")
        message = (f"{marshal.name} bows. \"I will hold you to it, Sire.\" "
                   f"His grievance shortens.")
    elif choice == "rebuke":
        marshal.modify_trust(CONFRONT_REBUKE_TRUST)
        marshal.jealousy_turns_remaining = max(
            0, marshal.jealousy_turns_remaining - CONFRONT_REBUKE_DURATION_CUT)
        if marshal.personality == "aggressive":
            marshal.jealousy_autonomous_warned = False
            marshal._jealousy_rebuked_cycle = True
        if marshal.personality == "literal":
            marshal._literal_intel_paused_turn = int(world.current_turn) + 1
        if marshal.jealousy_turns_remaining == 0 and marshal.jealous_of:
            clear_jealousy(world, marshal, resolved_by_action=False,
                           events=_pending_events(world),
                           reason="the Emperor's rebuke")
        message = (f"{marshal.name} stiffens under the rebuke "
                   f"({CONFRONT_REBUKE_TRUST} trust).")
    else:
        message = f"{marshal.name}'s grievance runs its course."
    world.log_event({
        "type": "jealousy_confrontation",
        "marshal": marshal.name,
        "target": context.get("target"),
        "nation": marshal.nation,
        "choice": choice,
    })
    return {"success": True, "message": message}


def _apply_rivalry_choice(world, choice: str, context: Dict) -> Dict:
    """§6b outcome tables — randomness on every option, authority-gated
    mediation, personality-weighted escalation."""
    marshal = world.marshals.get(context.get("marshal"))
    other = world.marshals.get(context.get("other"))
    if marshal is None or other is None:
        return {"success": True, "message": "The moment has passed."}
    new_value = int(context.get("new_value", -1))
    authority = int(world.authority_tracker.authority)
    roll = random.random()

    def _restore(to_value: int) -> None:
        marshal.set_relationship(other.name, to_value)
        other.set_relationship(marshal.name, to_value)

    outcome: str
    if new_value == -1:
        if choice == "let_be":
            simmer, escalate = (0.80, 0.15) if marshal.personality == "cautious" \
                else (0.50, 0.40) if marshal.personality == "aggressive" \
                else (0.70, 0.20)
            if roll < simmer:
                outcome = "They simmer down. The rivalry stands."
            elif roll < simmer + escalate:
                marshal.modify_relationship(other.name, -1)
                other.modify_relationship(marshal.name, -1)
                outcome = ("It escalates without you — the breach deepens "
                           "to open hostility.")
            else:
                _restore(0)
                outcome = "Against the odds, they work it out themselves."
        elif choice == "mediate":
            if not _spend_player_ap(world, 1):
                return {"success": False,
                        "message": "Not enough action points to mediate."}
            if authority >= 70:
                if roll < 0.70:
                    _restore(0)
                    outcome = "Your word carries. The breach is mended."
                else:
                    outcome = "They listen politely. Nothing changes."
            elif authority >= 40:
                if roll < 0.40:
                    _restore(0)
                    outcome = "A grudging peace is brokered."
                elif roll < 0.90:
                    outcome = "They nod and change nothing."
                else:
                    marshal.modify_trust(-3)
                    other.modify_trust(-3)
                    outcome = "They resent your interference (trust -3 both)."
            else:
                if roll < 0.20:
                    _restore(0)
                    outcome = "Somehow, it lands. The breach is mended."
                elif roll < 0.60:
                    outcome = "They ignore you. Nothing changes."
                else:
                    world.authority_tracker.modify_authority(-3)
                    outcome = ("They ignore you PUBLICLY — the court "
                               "noticed (authority -3).")
        else:  # reprimand
            marshal.modify_trust(-3)
            other.modify_trust(-3)
            if roll < 0.60:
                _restore(0)
                outcome = ("Their anger redirects at you — and the breach "
                           "closes (trust -3 both).")
            elif roll < 0.90:
                outcome = "Now they resent you AND each other (trust -3 both)."
            else:
                sufferer = marshal if marshal.personality == "aggressive" else other
                sufferer.modify_trust(-5)
                outcome = (f"{sufferer.name} took the reprimand personally "
                           f"(extra trust -5).")
    else:  # -2 transition
        if choice == "accept_breach":
            if roll < 0.80:
                outcome = "They settle into cold war."
            else:
                sufferer = marshal if marshal.personality == "aggressive" else other
                sufferer.defiance_cooldown_until = 0
                sufferer.modify_trust(-3)
                outcome = (f"{sufferer.name} turns openly discontent "
                           f"(trust -3; expect defiance).")
        elif choice == "force_reconciliation":
            if not _spend_player_ap(world, 2):
                return {"success": False,
                        "message": "Not enough action points to force a reconciliation."}
            if authority >= 80:
                if roll < 0.50:
                    _restore(-1)
                    outcome = "Under your eye they shake hands. Barely."
                else:
                    outcome = "Cold correctness. Nothing more."
            elif authority >= 60:
                if roll < 0.30:
                    _restore(-1)
                    outcome = "A stiff, public handshake. It holds — for now."
                elif roll < 0.80:
                    outcome = "Neither yields. The breach stands."
                else:
                    world.authority_tracker.modify_authority(-3)
                    outcome = "The failure was public (authority -3)."
            else:
                if roll < 0.10:
                    _restore(-1)
                    outcome = "A miracle of protocol. It holds — for now."
                elif roll < 0.40:
                    outcome = "Neither yields. The breach stands."
                else:
                    world.authority_tracker.modify_authority(-5)
                    outcome = ("The Emperor begged, and they refused "
                               "(authority -5).")
        else:  # separate
            marshal.separation_flagged[other.name] = True
            other.separation_flagged[marshal.name] = True
            outcome = ("Noted. Berthier will warn you whenever their "
                       "commands stand together.")
    world.log_event({
        "type": "rivalry_confrontation",
        "marshal": marshal.name,
        "other": other.name,
        "nation": marshal.nation,
        "choice": choice,
    })
    return {"success": True,
            "message": f"{marshal.name} and {other.name}: {outcome}"}


def _apply_fontainebleau_choice(world, choice: str, context: Dict) -> Dict:
    names = context.get("marshals", []) or []
    marshals = [world.marshals.get(n) for n in names]
    marshals = [m for m in marshals if m is not None]
    if not marshals:
        return {"success": True, "message": "The petitioners have dispersed."}
    if choice == "concede":
        granted = []
        for marshal in marshals:
            face = dotation.compute_rente_face(marshal, world)
            if face <= 0:
                continue
            marshal.pension = int(face)
            marshal.expectation_grace_turn = -1
            marshal.modify_trust(FONTAINEBLEAU_CONCEDE_TRUST)
            granted.append(f"{marshal.name} ({face}g/turn)")
            world.log_event({
                "type": "rente_granted",
                "marshal": marshal.name,
                "nation": marshal.nation,
                "face": int(face),
                "cost": int(dotation.get_rente_cost(face)),
                "source": "fontainebleau",
            })
        message = ("\"I will find the means.\" Rentes are granted: "
                   + "; ".join(granted) + ". The treasury will feel it.")
    elif choice == "refuse":
        for marshal in marshals:
            marshal.modify_trust(FONTAINEBLEAU_REFUSE_TRUST)
        message = ("\"The Empire does not beg.\" The marshals withdraw in "
                   f"silence (trust {FONTAINEBLEAU_REFUSE_TRUST} each). "
                   "The erosion continues.")
    else:  # promise
        for marshal in marshals:
            marshal.expectation_grace_turn = int(world.current_turn) \
                + FONTAINEBLEAU_PROMISE_GRACE
        world.authority_tracker.modify_authority(FONTAINEBLEAU_PROMISE_AUTHORITY)
        message = ("\"The next conquest is yours.\" Their patience extends "
                   f"{FONTAINEBLEAU_PROMISE_GRACE} turns — but the court "
                   "heard you buy time with words.")
    world.log_event({
        "type": "fontainebleau_petition",
        "marshals": names,
        "nation": world.player_nation,
        "choice": choice,
    })
    return {"success": True, "message": message}


def _apply_war_weary_choice(world, choice: str, context: Dict,
                            executor=None, game_state=None) -> Dict:
    marshal = world.marshals.get(context.get("marshal"))
    target_nation = context.get("target_nation", "")
    if choice == "march_anyway":
        if marshal is not None:
            marshal.modify_trust(WAR_WEARY_MARCH_TRUST)
        # The petition stored the ASSEMBLED diplomatic_data (with
        # _war_weary_resolved set) — re-enter the declare-war flow exactly
        # where it paused, the same direct-reinvoke pattern the Talleyrand
        # and ally-entry resolutions use.
        stored = context.get("original_command") or {}
        diplomatic = getattr(executor, "_diplomatic", None)
        if diplomatic is not None and stored:
            result = diplomatic._execute_diplomatic_declare_war(stored, world)
            if isinstance(result, dict):
                result.setdefault("message", "")
                result["message"] = (
                    f"{marshal.name if marshal else 'The marshal'} bows his "
                    f"head. \"Then we march.\" ({WAR_WEARY_MARCH_TRUST} "
                    f"trust)\n" + result["message"])
                return result
        return {"success": True,
                "message": "The order stands — reissue the declaration."}
    # stand down
    if marshal is not None:
        marshal.modify_trust(WAR_WEARY_HEED_TRUST)
    return {"success": True,
            "message": (f"You heed {marshal.name if marshal else 'the marshal'}"
                        f" — no war is declared against {target_nation} "
                        f"(+{WAR_WEARY_HEED_TRUST} trust).")}


# ═══════════════════════ THE MASTER TURN PASS ═════════════════════════════

def _pending_events(world) -> List[Dict]:
    events = getattr(world, "_pending_jealousy_turn_events", None)
    if events is None:
        events = []
        world._pending_jealousy_turn_events = events
    return events


def process_turn(world) -> List[Dict]:
    """The once-per-turn jealousy pass (TurnManager.end_turn, after
    strategic orders, before advance_turn — spec §0.2 item 5).

    Order: timers -> ladder-shift resolutions -> literal counters ->
    trigger evaluation (EC-J snapshot, rate-limited) -> restlessness
    pre-warnings -> autonomous-attack warnings -> crowns -> separation
    warnings -> Fontainebleau check. Returns dispatch events (also stashed
    on world._pending_jealousy_turn_events for advance_turn to collect).
    """
    if getattr(world, "_jealousy_processed_turn", None) == world.current_turn:
        return []
    world._jealousy_processed_turn = world.current_turn
    events = _pending_events(world)
    turn = int(world.current_turn)

    # An unanswered petition re-surfaces each turn (the popup queue pops
    # one winner per response cycle; the pending slot is the durable state).
    if getattr(world, "pending_marshal_petition", None):
        _push_petition(world, world.pending_marshal_petition)

    # 0) prune glory windows (bounded lists)
    for marshal in world.marshals.values():
        prune_glory_events(marshal, turn)
        # surge decays here (it was granted at battle time or last turn)
        if getattr(marshal, "jealousy_surge_turns", 0) > 0:
            marshal.jealousy_surge_turns -= 1

    # 1) timers + ladder-shift resolution for live grievances
    for marshal in list(world.marshals.values()):
        target_name = getattr(marshal, "jealous_of", None)
        if not target_name:
            continue
        target = world.marshals.get(target_name)
        if target is None or not _is_standing(target) \
                or target.nation != marshal.nation:
            clear_jealousy(world, marshal, resolved_by_action=False,
                           events=events, reason="the rival is gone")
            continue
        # Ladder shift (spec §2): passing the target resolves with surge.
        if get_glory_score(marshal, turn) > get_glory_score(target, turn):
            clear_jealousy(world, marshal, resolved_by_action=True,
                           events=events,
                           reason=f"he has surpassed {target_name} in glory")
            if marshal.nation == world.player_nation:
                events.append({
                    "type": "jealousy_ladder_shift",
                    "message": (f"{marshal.name} has proven himself beyond "
                                f"{target_name}. The grievance fades."),
                    "nation": marshal.nation,
                    "marshal": marshal.name,
                })
            continue
        marshal.jealousy_turns_remaining -= 1
        if marshal.jealousy_turns_remaining <= 0:
            clear_jealousy(world, marshal, resolved_by_action=False,
                           events=events, reason="time")

    # 2) literal sidelining counters (uses live per-turn flags)
    update_literal_hold_counters(world)

    # 3) trigger evaluation — snapshot first (EC-J), then rate-limit apply
    candidates: List[Tuple[object, object, int, int]] = []
    for marshal in world.marshals.values():
        if getattr(marshal, "jealous_of", None):
            continue
        if not _is_standing(marshal):
            continue
        if marshal.personality not in ("aggressive", "cautious", "literal"):
            continue
        authority = get_authority_proxy(world, marshal.nation)
        if is_capital_threatened(world, marshal.nation):
            continue

        if marshal.personality == "literal":
            # Sidelining resentment (spec §3) — target = the most actively
            # celebrated peer (one rung above on the ladder, or the top).
            if not _literal_trigger_ready(marshal):
                continue
            target = find_jealousy_target(marshal, world)
            if target is None:
                ladder = get_nation_ladder(world, marshal.nation)
                peers = [m for m, _ in ladder if m.name != marshal.name]
                target = peers[0] if peers else None
            if target is None:
                continue
            if marshal.get_relationship(target.name) >= 2:
                continue
            candidates.append((marshal, target, 1, 1))
            continue

        target = find_jealousy_target(marshal, world)
        if target is None:
            continue
        gate = _threshold_for(marshal, target, authority)
        if gate is None:
            continue
        threshold, requires_idle = gate
        if requires_idle and getattr(marshal, "idle_turns", 0) < HOSTILE_IDLE_TURNS:
            continue
        delta = get_glory_score(target, turn) - get_glory_score(marshal, turn)
        if delta >= threshold:
            candidates.append((marshal, target, delta, threshold))

    # most aggrieved first, per-nation rate limit (spec §1 v3)
    candidates.sort(key=lambda c: -(c[2] - c[3]))
    fired_per_nation: Dict[str, int] = {}
    for marshal, target, delta, threshold in candidates:
        if fired_per_nation.get(marshal.nation, 0) >= MAX_FIRES_PER_NATION_TURN:
            continue
        fired_per_nation[marshal.nation] = fired_per_nation.get(marshal.nation, 0) + 1
        apply_jealousy(world, marshal, target, delta, threshold, events)

    # 4) restlessness pre-warnings (spec §5) — player only, threshold-1
    warned = 0
    for marshal in world.marshals.values():
        if warned >= 1:
            break
        if marshal.nation != world.player_nation or not _is_standing(marshal):
            continue
        if getattr(marshal, "jealous_of", None):
            continue
        if marshal.personality == "literal":
            if marshal.consecutive_hold_turns == LITERAL_RESTLESS_AT:
                events.append({
                    "type": "jealousy_restlessness",
                    "message": (f"Berthier notes that {marshal.name} has been "
                                f"holding position for some time while others "
                                f"receive commands. He may begin to feel... "
                                f"overlooked."),
                    "nation": marshal.nation,
                    "marshal": marshal.name,
                })
                warned += 1
            continue
        target = find_jealousy_target(marshal, world)
        if target is None:
            continue
        authority = get_authority_proxy(world, marshal.nation)
        gate = _threshold_for(marshal, target, authority)
        if gate is None:
            continue
        threshold, requires_idle = gate
        if requires_idle and getattr(marshal, "idle_turns", 0) < HOSTILE_IDLE_TURNS:
            continue
        delta = get_glory_score(target, turn) - get_glory_score(marshal, turn)
        if delta == threshold - 1:
            events.append({
                "type": "jealousy_restlessness",
                "message": (f"Berthier notes that {marshal.name} has grown "
                            f"restless — he has not seen laurels while "
                            f"{target.name} wins them. I recommend giving "
                            f"him meaningful orders soon."),
                "nation": marshal.nation,
                "marshal": marshal.name,
            })
            warned += 1

    # 5) aggressive autonomous-attack warnings (spec §7) — player side gets
    # the one-turn dispatch warning; max 1 new warning per turn.
    warning_given = False
    for marshal in world.marshals.values():
        if marshal.nation != world.player_nation:
            continue
        if not getattr(marshal, "jealous_of", None) \
                or marshal.personality != "aggressive":
            continue
        if getattr(marshal, "_jealousy_rebuked_cycle", False):
            continue
        if not _is_standing(marshal):
            marshal.jealousy_autonomous_warned = False
            continue
        if marshal.jealousy_autonomous_warned or warning_given:
            continue
        target_region = find_autonomous_attack_target(world, marshal)
        if target_region is None:
            continue
        enemy, region_name = target_region
        marshal.jealousy_autonomous_warned = True
        warning_given = True
        events.append({
            "type": "jealousy_autonomous_warning",
            "message": (f"{marshal.name} is eyeing {enemy.name}'s position "
                        f"at {region_name}. I cannot guarantee he will wait "
                        f"for orders, Sire — any command would restrain him."),
            "nation": marshal.nation,
            "marshal": marshal.name,
        })

    # 6) crowns
    events.extend(recompute_crowns(world))

    # 7) §6b separation warnings
    for marshal in world.marshals.values():
        if marshal.nation != world.player_nation:
            continue
        for other_name, flagged in getattr(marshal, "separation_flagged", {}).items():
            if not flagged or marshal.name > other_name:
                continue        # one warning per pair
            other = world.marshals.get(other_name)
            if other is None or not _is_standing(other) or not _is_standing(marshal):
                continue
            region = world.regions.get(marshal.location)
            adjacent = set(getattr(region, "adjacent_regions", []) or []) \
                if region else set()
            if other.location == marshal.location or other.location in adjacent:
                events.append({
                    "type": "jealousy_separation_warning",
                    "message": (f"Berthier reminds you: {marshal.name} and "
                                f"{other_name} now stand within reach of "
                                f"each other. You asked to be warned."),
                    "nation": marshal.nation,
                    "marshal": marshal.name,
                })

    # 8) ESP-1 Fontainebleau
    check_fontainebleau(world, events)

    # clear the per-cycle rebuke latch
    for marshal in world.marshals.values():
        if getattr(marshal, "_jealousy_rebuked_cycle", False) \
                and not getattr(marshal, "jealous_of", None):
            marshal._jealousy_rebuked_cycle = False

    return events


# ═══════════════ AUTONOMOUS ATTACK (spec §7 + §0.2 item 7) ════════════════

def find_autonomous_attack_target(world, marshal):
    """Glory-seeking target priority: the WEAKEST adjacent at-war enemy
    (desperate, not smart). Returns (enemy_marshal, region_name) or None."""
    region = world.regions.get(marshal.location)
    if region is None:
        return None
    reachable = {marshal.location} | set(
        getattr(region, "adjacent_regions", []) or [])
    best = None
    for enemy in world.marshals.values():
        if enemy.nation == marshal.nation or enemy.strength <= 0:
            continue
        if getattr(enemy, "captured_by", ""):
            continue
        if not world.is_at_war(marshal.nation, enemy.nation):
            continue
        if enemy.location not in reachable:
            continue
        if best is None or enemy.strength < best.strength:
            best = enemy
    if best is None:
        return None
    return best, best.location


def process_autonomous_attacks(world, executor, game_state) -> List[Dict]:
    """Fire warned autonomous attacks for PLAYER-nation jealous aggressive
    marshals (TurnManager.end_turn, before the enemy phase). Any player
    order to the marshal during the turn cleared the warning (executor
    hook). No AP, no objection (_strategic_execution), physical gates
    still apply. Suppressed while the capital is threatened (EC-H)."""
    results = []
    if is_capital_threatened(world, world.player_nation):
        return results
    for marshal in list(world.marshals.values()):
        if marshal.nation != world.player_nation:
            continue
        if not getattr(marshal, "jealousy_autonomous_warned", False):
            continue
        marshal.jealousy_autonomous_warned = False
        if not getattr(marshal, "jealous_of", None) or not _is_standing(marshal):
            continue
        if marshal.personality != "aggressive":
            continue
        target_info = find_autonomous_attack_target(world, marshal)
        if target_info is None:
            continue
        enemy, _region = target_info
        # He acts on his own initiative — clears any standing order (EC-B).
        marshal.strategic_order = None
        marshal.holding_position = False
        marshal.hold_region = ""
        command = {
            "command": {
                "marshal": marshal.name,
                "action": "attack",
                "target": enemy.name,
                "_strategic_execution": True,
                "_jealousy_autonomous": True,
            }
        }
        result = executor.execute(command, game_state)
        events = _pending_events(world)
        events.append({
            "type": "jealousy_autonomous_attack",
            "message": (f"{marshal.name}, hungry for glory, has attacked "
                        f"{enemy.name} on his own initiative."),
            "nation": marshal.nation,
            "marshal": marshal.name,
        })
        world.log_event({
            "type": "jealousy_autonomous",
            "marshal": marshal.name,
            "target": enemy.name,
            "nation": marshal.nation,
        })
        if isinstance(result, dict):
            result["jealousy_autonomous"] = marshal.name
            results.append(result)
    return results


def cancel_autonomous_warning_on_order(world, marshal) -> Optional[str]:
    """Called by the executor when the player successfully issues ANY
    command to a warned marshal — the attack is called off this cycle
    (jealousy persists). Returns a note for the command result."""
    if getattr(marshal, "jealousy_autonomous_warned", False) \
            and marshal.nation == world.player_nation:
        marshal.jealousy_autonomous_warned = False
        return (f"({marshal.name} stands down from his intended attack — "
                f"your orders reached him in time.)")
    return None


# ═══════════════════ SURFACES: CARD + DISPATCH HELPERS ════════════════════

def any_player_grievance(world) -> bool:
    for marshal in world.marshals.values():
        if marshal.nation == world.player_nation \
                and getattr(marshal, "jealous_of", None):
            return True
    return False


def build_glory_card_fields(marshal, world) -> Dict:
    """Marshal-card payload block (marshal_overview) — shown = applied."""
    turn = int(world.current_turn)
    glory = get_glory_score(marshal, turn)
    ladder = get_nation_ladder(world, marshal.nation)
    position = 0
    for index, (m, _score) in enumerate(ladder):
        if m.name == marshal.name:
            position = index + 1
            break
    fields = {
        "glory": glory,
        "glory_rank": position,
        "glory_roster": len(ladder),
        "glory_crowned": bool(getattr(marshal, "glory_crowned", False)),
        "jealous_of": getattr(marshal, "jealous_of", None),
        "jealousy_turns_remaining": int(getattr(marshal, "jealousy_turns_remaining", 0)),
        "jealousy_surge": int(getattr(marshal, "jealousy_surge_turns", 0)) > 0,
        "jealousy_warned": bool(getattr(marshal, "jealousy_autonomous_warned", False)),
        "feuds": sorted([
            name for name, level in
            (getattr(marshal, "jealousy_history", {}) or {}).get("__levels__", {}).items()
            if int(level) >= ESCALATION_PERMANENT_LEVEL
        ]),
        "separations": sorted([
            name for name, flagged in
            (getattr(marshal, "separation_flagged", {}) or {}).items() if flagged
        ]),
    }
    return fields


def build_glory_ladder_payload(world) -> List[Dict]:
    """The player's glory ladder for the Generals screen header."""
    ladder = get_nation_ladder(world, world.player_nation)
    payload = []
    for marshal, score in ladder:
        payload.append({
            "name": marshal.name,
            "glory": int(score),
            "crowned": bool(getattr(marshal, "glory_crowned", False)),
            "jealous_of": getattr(marshal, "jealous_of", None),
            "personality": marshal.personality,
        })
    return payload
