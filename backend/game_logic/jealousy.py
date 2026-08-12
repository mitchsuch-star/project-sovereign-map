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

from backend.display_names import humanize_entity_name
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
# Q3(b) (CA9 row 3): a stored RIVAL pair needs its quarrel to RECUR before
# the staff start speaking of it openly; a stored HOSTILE pair escalates on
# sight, because those men already have a history. Before this, 14 of the
# 18 authored French edges reached escalation 1 on their FIRST fire and the
# mild register was unreachable.
ESCALATION_RIVAL_FIRES = 2          # stored -1: the SECOND fire qualifies
ESCALATION_IMMEDIATE_RELATIONSHIP = -2   # stored -2 or worse: on sight
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
# Q1(b) (CA9 row 3 ruling): how long the Emperor's promise holds the pair's
# escalation level. In-band tunable. This is what the 1 AP now buys that
# nothing else on the card can: the quarrel cannot get WORSE while it stands.
# Before it, `promise` was strictly DOMINATED — it shortened a timer and, by
# clearing with `resolved_by_action=False`, forfeited the +10% surge the free
# battle path grants, so paying was worse than ignoring the popup.
CONFRONT_PROMISE_HOLD_TURNS = 6
# A9 (CA9 row 3): turns between §6b "Separate Them" proximity warnings for a
# pair. In-band tunable. The first proximity always warns; this only stops the
# per-turn nag that made the one honest arm of the rivalry modal a punishment
# for using it.
SEPARATION_WARNING_COOLDOWN = 4
CONFRONT_REBUKE_DURATION_CUT = 1

# CA8-D3 (gate held Aug 8, 2026, delegated — record: spec §0.5): THE RIVAL IS
# A PERSON. The audit measured Murat's rival changing four times in twelve
# turns because targeting recomputed from the rolling window alone; with
# memory, envy RE-FIXES on the man it has already fired on whenever he still
# stands above. The flag exists for the flip-experiment discipline (disable →
# prior behaviour reproduces byte-identically), not as a config surface.
JEALOUSY_RIVAL_MEMORY = True

# A12 (CA9 row 3, Aug 9 2026): A PAIR THAT COOLED THIS PASS DOES NOT RE-FIRE
# IN THE SAME PASS. `clear_jealousy` writes no "cooled this turn" marker, so
# a marshal cleared in step 1 reads `jealous_of is None` in step 3 and rival
# memory hands him back the SAME man — measured on 20 of 40 ambient turns,
# and the briefing then carried "his resentment has cooled" and "he resents
# him, for the fourth time" on one page.
#
# Deliberately NOT applied to `forced=True` fires: the level-3 mutual spiral
# writes `jealous_of` on the TARGET through `_check_escalation`'s reciprocity
# arm, and suppressing that would break the ladder rather than de-duplicate
# a sentence.
#
# This is the arm that moves BASELINE_SERIES (it changes which marshals hold
# a grievance, which the combat coordination chokepoint reads, on BOTH
# boards). The flag exists for the flip-experiment discipline — disable and
# the prior series reproduces byte-identically — not as a config surface.
JEALOUSY_SUPPRESS_SAME_PASS_REFIRE = True


def jealousy_dormant(world) -> bool:
    """TUT-F5 (Aug 8, 2026 tutorial live report): the School of War keeps the
    marshals' drama out of the classroom. On the lesson world no grievance
    ever fires and no marshal petition of ANY kind queues — the live report
    measured five Soult confrontations in three lesson turns, each a modal
    the twelve-turn syllabus never explains. Glory itself still accrues (the
    Generals screen stays honest); the guard is world-scoped, so both sides
    go quiet together (GR5). Same discriminator as the TUT-F2 autosave guard."""
    return getattr(world, "scenario_name", "") == "tutorial"


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
                    conquered: bool, outnumbered: bool) -> int:
    """Glory for a victory (spec §1).

    CA8-19(ii): the `is_garrison_stomp` parameter is GONE. Spec §1's
    "Garrison stomp: +0" is now enforced structurally, one layer up, by the
    `not is_garrison` term on the pipeline's glory step — a garrison assault
    never reaches this function at all. The parameter could never be True in
    production (the garrison path passes `battle_result: None`, which the same
    guard already excluded), so it was a rule the caller had to remember
    rather than one the engine held.
    """
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
                        pre_attacker_strength: int,
                        pre_defender_strength: int,
                        attacker_participants: Optional[List] = None,
                        defender_participants: Optional[List] = None) -> None:
    """Record glory for a resolved battle. Runs AFTER the Win/Loss
    relationship step (EC-F ordering) from every combat path.

    Primaries score the full formula; non-primary participants
    (coordination/reinforcement) record base +/-1 only (spec §0.2 item 4).
    Defensive victories score normally (EC-A).

    CA8-19(ii): garrison assaults never arrive here. Spec §1's garrison-stomp
    exemption used to ride an `is_garrison` argument that no production caller
    could set; it is now the `not is_garrison` term on the pipeline's glory
    step, so the ladder excludes garrison combat in both directions.
    """
    turn = int(world.current_turn)
    atk_outnumbered = pre_attacker_strength < pre_defender_strength
    def_outnumbered = pre_defender_strength < pre_attacker_strength

    if attacker is not None:
        if attacker_won:
            _append_glory(attacker, turn, _victory_points(
                attacker_casualties, defender_casualties,
                conquered, atk_outnumbered))
        elif defender_won:
            _append_glory(attacker, turn, _defeat_points(
                attacker_casualties, defender_casualties,
                territory_lost=False, outnumbered=atk_outnumbered))

    if defender is not None:
        if defender_won:
            _append_glory(defender, turn, _victory_points(
                defender_casualties, attacker_casualties,
                conquered=False, outnumbered=def_outnumbered))
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
    """The marshal's envy object (spec §1 v3, amended by CA8-D3 — spec §0.5).

    CA8-D3 Q1 (rival memory): among peers STRICTLY ABOVE on the ladder, a man
    this marshal's envy has already fired on (any recorded fire in
    `jealousy_history`, which is already serialized) is preferred over the
    rung rule — most lifetime fires first, ties by worse relationship then
    alphabetical. The rival stays a PERSON while he outshines the marshal,
    instead of being re-cast every time the rolling window reshuffles the
    rungs. First acquisition (no history above) keeps the one-rung-up rule
    byte-identically; passing the remembered rival still resolves with surge
    via the ladder-shift path, and a fallen rival who RISES again re-fixes
    the old feud.

    Ties on the ladder never trigger each other; a marshal below a tie
    targets the tied marshal he has the WORSE relationship with, then
    alphabetical (spec §1 Ties).
    """
    my_glory = get_glory_score(marshal, world.current_turn)
    candidates = []
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
        candidates.append((other, other_glory))
    if not candidates:
        return None

    if JEALOUSY_RIVAL_MEMORY:
        remembered = None
        remembered_fires = 0
        for other, _glory in candidates:
            fires = _lifetime_fires(marshal, other.name)
            if fires <= 0:
                continue
            if marshal.get_relationship(other.name) >= 2:
                # A remembered rival repaired to Devoted is immune
                # (THRESHOLDS None) — returning him would SHADOW a fresh
                # non-immune rung target and make old friendship suppress
                # all new envy. The feud is over; the ladder resumes.
                continue
            if remembered is None or fires > remembered_fires:
                remembered, remembered_fires = other, fires
            elif fires == remembered_fires:
                cur = marshal.get_relationship(remembered.name)
                new = marshal.get_relationship(other.name)
                if new < cur or (new == cur and other.name < remembered.name):
                    remembered = other
        if remembered is not None:
            return remembered

    target = None
    target_glory = None
    for other, other_glory in candidates:
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


# ════════════════════════════════════════════════════════════════════════
# CA8-8 (creative audit, Aug 4 2026): EVERY GRIEVANCE WAS BYTE-IDENTICAL
# TO THE LAST, AND NOTHING SIGNALLED RECURRENCE.
#
# Measured over one played campaign: "appears envious of" x9, "has not seen
# laurels while" x6, "cooled with time" x6 — because there were exactly
# three expression strings, keyed on personality, so an aggressive marshal
# ALWAYS said "grown restless for glory".
#
# Worse, one dispatch printed, in this order:
#   [good]    Murat's resentment of Davout has cooled with time.
#   [warning] ...Murat appears envious of Davout's laurels...
#   [warning] The rivalry ... has become entrenched.
# That state is LEGAL — step 1 expires the timer and clears `jealous_of`,
# step 3's only exclusion is `if marshal.jealous_of: continue`, so the man
# just cleared is re-evaluated in the same pass and may re-fire. The defect
# is that no template carried a recurrence register: nothing said "again",
# so a legal escalation was indistinguishable from a state bug on the page.
#
# THIS IS A DISPLAY FIX ONLY. No trigger, ordering, rate limit or timer is
# touched — those feed `jealous_of`, which M7 and the AI-intent
# BASELINE_SERIES both read through combat's reinforcement/coordination
# math. The register is derived from `jealousy_history[target]`, a list of
# fire TURNS that is already serialized and already read by
# `_lifetime_fires`. Zero new fields.
# ════════════════════════════════════════════════════════════════════════
# Every entry fills the slot "he has {expression}", so every entry must be
# a past participle — pinned by
# test_creative_audit_2026_07_19::test_every_jealousy_expression_fits_the_
# he_has_slot, which the July 19 audit landed after the live line "he has
# restless for glory" reached a player.
_JEALOUSY_EXPRESSIONS: Dict[str, List[str]] = {
    "aggressive": [
        "grown restless for glory",
        "grown loud at the staff table about who is given the honours",
        "grown impatient for something worth the doing",
    ],
    "cautious": [
        "grown cold and withholding",
        "grown careful about what he commits to paper",
        "grown quiet in the way the staff have learned to read",
    ],
    "literal": [
        "thrown himself into his post with obsessive diligence",
        "thrown himself at his returns and his pickets like a man proving "
        "a point",
        "grown scrupulous to the point of reproach",
    ],
}
_JEALOUSY_EXPRESSION_DEFAULT = "grown resentful"


def _expression_for(world, marshal, target_name: str, fires: int) -> str:
    """Pick the grievance expression. Deterministic and RNG-free — keyed on
    the campaign seed plus the pair and which recurrence this is, so the
    same quarrel does not use the same words twice and two different
    quarrels do not sound like one man."""
    bank = _JEALOUSY_EXPRESSIONS.get(marshal.personality)
    if not bank:
        return _JEALOUSY_EXPRESSION_DEFAULT
    try:
        from backend.game_logic.campaign_variance import seeded_int
        seed = str(getattr(world, "campaign_seed", "") or "historical")
        idx = seeded_int(
            seed, f"jealousy_expression::{marshal.name}::{target_name}"
                  f"::{max(1, int(fires))}", 0, len(bank) - 1)
    except Exception:
        idx = max(0, (int(fires) - 1)) % len(bank)
    return bank[idx % len(bank)]


_ORDINALS = {2: "second", 3: "third", 4: "fourth", 5: "fifth"}


def _recurrence_clause(marshal, target_name: str, turn: int) -> str:
    """The register that says this has happened before — derived entirely
    from the already-serialized list of fire turns. Empty on a first fire,
    which is the only case that may read as fresh news.

    ════════════════════════════════════════════════════════════════════════
    CA8-9/CA8-8 REVIEW FIX — the interval is FIRE-TO-FIRE, and the first
    draft called it "turns after it cooled".

    `jealousy_history` records fire turns and nothing else, so no
    cooled-to-refire interval is derivable without new state, which this
    slice's zero-new-fields contract forbids. A grievance stands for
    `_duration_for()` = 2-5 turns before the timer can expire, so the
    printed figure overstated the true time-since-cooling by exactly the
    duration on the timer path — and by however long it stood on the early
    paths (ladder shift, battle resolution, confrontation cuts). There was
    NO reachable case in which it was correct, and in the marquee scenario
    it printed "again, 2 turns after it cooled" directly beneath the line
    saying it had just cooled. The noun is now the one the data supports.

    The dropped `gap == 1` arm was doubly wrong: a one-turn fire gap means
    the grievance was cleared EARLY, i.e. by action, so it had not "cooled"
    at all.
    ════════════════════════════════════════════════════════════════════════
    """
    history = [int(t) for t in
               getattr(marshal, "jealousy_history", {}).get(target_name, [])]
    fires = len(history)
    if fires <= 1:
        return ""
    gap = turn - history[-2]
    if gap <= 0:
        # Cleared and re-fired inside one council. Reachable via the tier-3
        # mutual spiral: it sets a pair's grievance mid-loop while that
        # marshal's own snapshotted candidate fires again the same turn,
        # because the apply loop never re-checks `jealous_of`.
        return " once more, the same day it was set aside"
    if fires >= 3:
        return f" for the {_ORDINALS.get(fires, f'{fires}th')} time"
    # N25 (CA9): "again, 1 turns after the last". This is NOT the arm the
    # CA8 sweep dropped — that one made a claim about COOLING the data
    # cannot support. This says only what `gap` means: fire to fire.
    if gap == 1:
        return " again, the very next turn"
    return f" again, {gap} turns after the last"


def apply_jealousy(world, marshal, target, delta: int, threshold: int,
                   events: List[Dict], forced: bool = False) -> None:
    """Set the grievance: fields, history, escalation, expression setup,
    dispatch/campaign-log events. The -1 relationship is DERIVED from
    jealous_of (spec §0.2 item 2) — nothing to mutate here."""
    if jealousy_dormant(world):
        return
    turn = int(world.current_turn)
    marshal.jealous_of = target.name
    marshal.jealousy_turns_remaining = _duration_for(delta, threshold)
    marshal.jealousy_history.setdefault(target.name, []).append(turn)

    is_player = marshal.nation == world.player_nation
    # CA8-8: the expression is drawn from a per-personality bank (see
    # `_JEALOUSY_EXPRESSIONS`) instead of being one fixed string per
    # personality. Every entry is still a past participle filling
    # "he has {expression}" — the July 19 2026 pin holds over the whole bank.
    _fires = _lifetime_fires(marshal, target.name)
    expression = _expression_for(world, marshal, target.name, _fires)
    # CA8-8: "again", "for the third time", "the same day it was set aside".
    _recur = _recurrence_clause(marshal, target.name, turn)

    world.log_event({
        "type": "jealousy_fired",
        "marshal": marshal.name,
        "target": target.name,
        "nation": marshal.nation,
        "personality": marshal.personality,
        # CA8-8: the campaign log composes its OWN sentence from these
        # structured fields (it never reads `message`), so it needs the
        # recurrence count to avoid the identical monoculture the dispatch
        # had. New key on an existing type — no CAMPAIGN_LOG_TYPES change.
        "fires": _lifetime_fires(marshal, target.name),
    })
    if is_player:
        _envious = humanize_entity_name(marshal.name)
        _envied = humanize_entity_name(target.name)
        # Creative audit July 19 2026: this fired alongside a
        # `jealousy_target_notice` that restated the SAME grievance from the
        # target's side, so one grievance cost the dispatch two near-identical
        # lines — with 2-3 live grievances the briefing was 6+ lines of the
        # same news. The target's perspective (spec §5 v3, informational only)
        # is folded into this one line: it already names both men and who
        # holds the laurels, which is all the notice ever carried.
        # CA8-8: a first grievance may read as fresh news; a recurrence must
        # say so, or a legal re-fire looks like the game repeating itself.
        if _recur:
            _line = (f"Berthier reports that {_envious} resents {_envied}'s "
                     f"laurels{_recur} — he has {expression}.")
        else:
            _line = (f"Berthier reports that {_envious} appears envious of "
                     f"{_envied}'s laurels — he has {expression}.")
        events.append({
            "type": "jealousy_fired",
            "message": _line,
            "nation": marshal.nation,
            "marshal": marshal.name,
            "target": target.name,
        })

    # A12: `is_player` is exactly the condition under which the fire line
    # above was appended, so the escalation arm can tell whether the player
    # has ALREADY been told about this trigger on this page.
    _check_escalation(world, marshal, target, events, forced=forced,
                      fire_announced=bool(is_player))

    # Confrontation popup (spec §6, amended by CA8-D3 Q2 — spec §0.5):
    # player pairs only, one petition slot at a time; unseen keys retry on
    # later turns. The latch is per (pair, ESCALATION LEVEL) — the audit
    # measured one confrontation per pair per CAMPAIGN, fired on turn 1,
    # while every later escalation of the same feud passed without an
    # audience. Each level speaks once: levels 0..3 bound the channel at
    # four confrontations per pair for a whole campaign. A legacy bare pair
    # key (pre-CA8-D3 saves) reads as "level 0 seen".
    if is_player and not forced:
        seen = set(getattr(world, "jealousy_confrontations_seen", []) or [])
        pair = _pair_key(marshal.name, target.name)
        level = get_escalation_level(marshal, target.name)
        key = f"{pair}@L{level}"
        already = key in seen or (level == 0 and pair in seen)
        if not already and getattr(world, "pending_marshal_petition", None) is None:
            queue_confrontation_petition(world, marshal, target, level)
            seen.add(key)
            world.jealousy_confrontations_seen = sorted(seen)


def _check_escalation(world, marshal, target, events: List[Dict],
                      forced: bool = False,
                      fire_announced: bool = False) -> None:
    """Escalation (spec §10): qualifying fire = stored relationship already
    Rival-or-worse OR 3rd lifetime fire. Levels advance 1 -> 2 -> 3."""
    stored_rel = marshal.relationships.get(target.name, 0)
    fires = _lifetime_fires(marshal, target.name)
    # ══════════════════════════════════════════════════════════════════
    # Q3(b) (CA9 row 3 ruling): A FIRST GRIEVANCE GETS A FIRST ACT.
    #
    # This was `stored_rel <= -1 or fires >= 3`. On the authored 1805
    # board 14 of 18 directed French edges sit at Rival or worse, so the
    # player's very FIRST card on those pairs opened at escalation 1 —
    # "the staff now speak of the quarrel openly; this is no longer a
    # passing mood" — about a resentment one turn old. There was no mild
    # register, because the mild register was never reachable.
    #
    # A stored HOSTILE pair (-2) still escalates on sight: those men have
    # a history the campaign did not invent. A stored RIVAL pair (-1) now
    # needs a second fire — the quarrel has to actually recur.
    #
    # `jealousy_history` is appended by `apply_jealousy` BEFORE this runs,
    # so fire 1 already reads `_lifetime_fires == 1`; "the second fire" is
    # therefore `>= 2`. (This is also why the memo's rejected variant —
    # gating the level-1 ANNOUNCEMENT on `fires >= 2` — is inert: the
    # count is already 1 when the announcement is decided.)
    #
    # One predicate moves all three surfaces together, which is what the
    # ruling required: the level, the card's escalation register (read
    # from the level), and the `pair@L{level}` petition latch (keyed on
    # the level AFTER this call). No separate wiring.
    # ══════════════════════════════════════════════════════════════════
    if stored_rel <= ESCALATION_IMMEDIATE_RELATIONSHIP:
        qualifies = True
    elif stored_rel == -1:
        qualifies = fires >= ESCALATION_RIVAL_FIRES
    else:
        qualifies = fires >= ESCALATION_LIFETIME_FIRES
    if not qualifies:
        return
    # ══════════════════════════════════════════════════════════════════
    # Q1(b) (CA9 row 3 ruling): the Emperor's promise HOLDS the line.
    #
    # This is the ONE seam that writes escalation, which is exactly why no
    # petition arm could previously change any outcome: whatever the player
    # answered, the pair marched to permanent -2 on schedule. A hold cannot
    # un-write history — it only stops the next rung — which is why the
    # ruling chose it over buying a rung back.
    #
    # Checked in BOTH directions: `_set_escalation_level` writes the pair
    # together, so a promise given to one man must not be defeated by his
    # rival's fire arriving first.
    #
    # `forced` bypasses it deliberately — the mutual-spiral path and the
    # test hooks that pass forced=True are asserting the ladder itself.
    # ══════════════════════════════════════════════════════════════════
    if not forced:
        _now = int(getattr(world, "current_turn", 0) or 0)
        _held_until = max(
            int(marshal.jealousy_escalation_hold.get(target.name, -1)),
            int(target.jealousy_escalation_hold.get(marshal.name, -1)),
        )
        if _held_until >= _now:
            if marshal.nation == world.player_nation:
                events.append({
                    "type": "jealousy_escalation",
                    "message": (
                        f"{marshal.name} presses his grievance against "
                        f"{target.name} again — but he holds to the "
                        f"Emperor's word, and the quarrel goes no further "
                        f"for now."),
                    "nation": marshal.nation,
                    "marshal": marshal.name,
                    "target": target.name,
                    # The level did NOT move; consumers that render an
                    # escalation register must not claim it did.
                    "level": get_escalation_level(marshal, target.name),
                    "held": True,
                })
            return
    _mutual_applied = False
    level = min(ESCALATION_MUTUAL_LEVEL,
                max(get_escalation_level(marshal, target.name),
                    get_escalation_level(target, marshal.name)) + 1)
    _set_escalation_level(marshal, target.name, level)
    _set_escalation_level(target, marshal.name, level)

    is_player = marshal.nation == world.player_nation
    if level == 1 and is_player and not fire_announced:
        # A12: this arm used to co-emit with the `jealousy_fired` line that
        # caused it — one trigger, two bullets on the same page, saying the
        # same news at two registers ("X appears envious of Y's laurels" /
        # "the rivalry between X and Y has become a matter of concern").
        # The fire line already names both men and the resentment, so when
        # it was shown, this adds nothing. Levels 2 and 3 still announce:
        # "entrenched" and "mutual" are genuinely new facts, and level 2
        # additionally applies a permanent -1 in both directions.
        events.append({
            "type": "jealousy_escalation",
            "message": (
                f"Sire, the rivalry between {marshal.name} and {target.name} "
                f"has become a matter of concern among the general staff. "
                f"Their cooperation cannot be relied upon."),
            "nation": marshal.nation,
            "marshal": marshal.name,
            "target": target.name,
            # A13: the cap exempts escalation-to-PERMANENT, not every
            # escalation, so the level has to ride the event.
            "level": 1,
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
                "level": ESCALATION_PERMANENT_LEVEL,
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
            # CA8-8 review fix: the campaign log rendered "each schemes
            # against the other" off `level` alone, but the level advances
            # to 3 whether or not this guard passes — a target who is
            # `retreating` fails `_is_standing`, so the reciprocity is
            # SKIPPED while the log still announced a mutual feud, on a
            # marshal with no grievance, no derived -1 and no withholding
            # effect. One reviewer saw the false line on eight consecutive
            # turns. The producer knows; now it says so.
            _mutual_applied = True
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
        # Whether the tier-3 reciprocity actually APPLIED (see above). New
        # key on an existing type — no CAMPAIGN_LOG_TYPES change.
        "mutual": bool(_mutual_applied),
    })


# A2 (CA9 row 3): the four `reason=` strings the non-action branch can be
# handed, mapped to the clause that names the cause. Keyed on the literal
# strings the call sites pass (`jealousy.py` promise/rebuke arms, the
# rival-gone sweep) so an unrecognised or absent reason falls through to the
# unchanged "cooled with time" wording — which is what keeps `reason="time"`
# and every legacy caller byte-identical.
#
# Deliberately NOT a personality bank: this states what the EMPEROR did, and
# it reads the same in any register. Voice for the marshal himself is A14.
_COOLING_CAUSE = {
    "the Emperor's promise": "He holds you to your word.",
    "the Emperor's rebuke": "He has swallowed the rebuke.",
    "the rival is gone": "There is no one left to envy.",
    # Q4(a): the §6b mend arms. Before this they charged AP, printed a
    # handshake and moved nothing a mechanic reads.
    "the Emperor forced the reconciliation":
        "They shook hands before the staff, and it held.",
    "the Emperor's mediation": "Your word carried between them.",
}


def _action_resolution_event(record: Dict) -> Dict:
    """The dispatch bullet for an EARNED resolution.

    A7 (CA9 row 3): single source, because it is now built in two places —
    here at clear time, and again by `emit_unreported_resolutions` when a
    battle-time resolution could not be reported at the battle surface.
    Two copies of this sentence is how the surfaces drift apart.
    """
    surge_note = {
        "aggressive": "He fights with renewed purpose (+10% attack this turn).",
        "cautious": "He holds with renewed purpose (+10% defense this turn).",
        "literal": "His patrols keep their edge one turn more.",
    }.get(record.get("personality", ""), "")
    return {
        "type": "jealousy_resolved",
        "message": (
            f"{record['marshal']}'s grievance is satisfied — "
            f"{record.get('reason') or 'he has proven himself'}. "
            f"{surge_note}"),
        "nation": record.get("nation", ""),
        "marshal": record["marshal"],
        # See the sibling branch: A13's discriminator. THIS is the
        # beat a narration cap must never collapse.
        "by_action": True,
    }


def clear_jealousy(world, marshal, resolved_by_action: bool,
                   events: Optional[List[Dict]] = None,
                   reason: str = "") -> Optional[Dict]:
    """Clear the grievance. Action resolutions grant the 1-turn surge
    (spec §4); timer expiry grants nothing. The derived -1 restores
    itself the moment jealous_of clears.

    A7 (CA9 row 3): RETURNS the resolution record. Everything the battle
    surface needs to name what happened is known here and was previously
    thrown away — which is why the battle note had to INFER a resolution
    from `jealousy_surge_turns > 0 and not jealous_of`, a heuristic that
    is wrong in three ways (it claims a settlement for a surge granted by
    last turn's ladder shift, it repeats itself on a marshal's second
    battle in a turn, and it cannot see a PARTICIPANT's resolution at
    all). Additive: no caller is obliged to read it.
    """
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
    record = {
        "marshal": marshal.name,
        "target": target_name,
        "nation": marshal.nation,
        "personality": marshal.personality,
        "by_action": bool(resolved_by_action),
        "reason": reason,
        "is_player": bool(is_player),
    }
    if is_player and events is not None:
        if resolved_by_action:
            events.append(_action_resolution_event(record))
        else:
            # ────────────────────────────────────────────────────────────
            # CA8-8: "cooled with time" was told the same way whether this
            # was the first quarrel or the fourth, and — worse — it was told
            # about a pair the game had already announced as permanent:
            # "The wound will not close on its own" (tier 2, which also
            # applies a permanent -1 both directions), then two turns later
            # the wound closes on its own, in front of the player.
            #
            # Both sentences were true of DIFFERENT things: the grievance
            # timer expires, the standing between the two men does not. The
            # fix is to say which one cooled.
            # ────────────────────────────────────────────────────────────
            # `_set_escalation_level` writes both directions together, so
            # this marshal's own entry is the pair's level.
            _level = get_escalation_level(marshal, target_name)
            _times = _lifetime_fires(marshal, target_name)
            # ────────────────────────────────────────────────────────────
            # A2 (CA9 row 3, Aug 9 2026): say WHY it cooled.
            #
            # `reason` was accepted by this function, documented, and then
            # read on the action branch only — so a grievance ended by the
            # Emperor's paid 1-AP promise, by a rebuke that cost 5 trust,
            # and by the rival being ridden down ALL printed "cooled with
            # time". That single sentence is a large part of why the channel
            # reads as inert: the player spends an action point and the game
            # reports patience.
            #
            # Threaded as a CLAUSE INSIDE the existing three-variant ladder
            # rather than as a fourth variant, because both CA8-8 pins must
            # keep holding: entrenched still outranks everything (its "has
            # not been" clause is the load-bearing half), and `reason="time"`
            # must still render "cooled with time" verbatim on an ordinary
            # pair. Only a NAMED cause changes the wording.
            # ────────────────────────────────────────────────────────────
            _cause = _COOLING_CAUSE.get(str(reason or ""), "")
            if _level >= ESCALATION_PERMANENT_LEVEL:
                _msg = (f"{marshal.name}'s resentment of {target_name} has "
                        f"cooled for now. What was settled between them at "
                        f"the staff table has not been.")
            elif _times >= 3:
                # CA8-8 review fix: `_lifetime_fires` counts FIRES, not
                # coolings. `clear_jealousy` writes nothing to that list on
                # either branch, and an action resolution takes the surge
                # branch above ("grievance is satisfied") — a different word,
                # a different event and a +10% surge. So "It has cooled 3
                # times" was false whenever any earlier episode was settled
                # by a victory, and it contradicted the game's own earlier
                # lines. The number is now named for what it counts.
                _msg = (f"{marshal.name}'s resentment of {target_name} has "
                        f"cooled. The quarrel has flared {_times} times.")
            elif _cause:
                # A named cause did the work, so "with time" would be a lie.
                _msg = (f"{marshal.name}'s resentment of {target_name} is "
                        f"set aside.")
            else:
                _msg = (f"{marshal.name}'s resentment of {target_name} has "
                        f"cooled with time.")
            if _cause:
                _msg = f"{_msg} {_cause}"
            events.append({
                "type": "jealousy_resolved",
                "message": _msg,
                "nation": marshal.nation,
                "marshal": marshal.name,
                # A13's prerequisite, added here because this is the seam
                # that knows: an EARNED resolution and a timer expiry are
                # both `jealousy_resolved` with no discriminator, so a
                # narration cap could not exempt one and collapse the other.
                # A key on the existing event, not a new log type.
                "by_action": False,
            })
    return record


# ═══════════════════ BATTLE-TIME RESOLUTION (spec §3) ═════════════════════


def compose_battle_jealousy_note(world, primaries, resolutions):
    """Berthier's line about jealous conduct on the field (spec §11, GR6).

    A7 (CA9 row 3). Returns `(sentence, reported_names)` — the sentence for
    the battle report, and the marshals whose RESOLUTION it named, so the
    caller can suppress the duplicate next-morning bullet for exactly those
    men (N36) and leave every non-battle resolution's bullet alone.

    Display-only. The settled arm is driven by the resolver's own records
    rather than by `jealousy_surge_turns`, which fixes three lies the
    heuristic told — see `clear_jealousy`'s docstring.
    """
    notes: List[str] = []
    reported: List[str] = []
    settled = {r["marshal"]: r for r in (resolutions or [])
               if r.get("is_player") and r.get("by_action")}
    seen = set()

    def _settled_line(name: str) -> str:
        return (f"{name} fought like a man with something to "
                f"prove — and proved it. His grievance is settled.")

    # The two primaries first, in their historical order, so the copy for
    # the ordinary one-primary battle is byte-identical to the pre-A7 note.
    for m in (primaries or []):
        if m is None or m.nation != world.player_nation:
            continue
        if m.name in seen:
            continue
        seen.add(m.name)
        if m.name in settled:
            notes.append(_settled_line(m.name))
            reported.append(m.name)
        elif getattr(m, "jealous_of", None):
            if m.personality == "aggressive":
                notes.append(
                    f"{m.name} fought with particular ferocity — "
                    f"though one wonders if it was for France or for "
                    f"himself.")
            elif m.personality == "cautious":
                notes.append(
                    f"{m.name}'s commitment was... measured. His "
                    f"grievance against {m.jealous_of} shows in "
                    f"the field.")
            else:
                notes.append(
                    f"{m.name} fought with an intensity "
                    f"suggesting something to prove.")

    # Then the PARTICIPANTS who settled a grievance in this battle. The
    # resolver has always cleared these (cautious "shoulder to shoulder",
    # literal contact); no surface has ever said so.
    for r in (resolutions or []):
        if not r.get("is_player") or not r.get("by_action"):
            continue
        if r["marshal"] in seen:
            continue
        seen.add(r["marshal"])
        notes.append(_settled_line(r["marshal"]))
        reported.append(r["marshal"])

    return " ".join(notes), reported


def emit_unreported_resolutions(world, resolutions, reported) -> None:
    """Append the next-morning bullet for battle resolutions the battle
    surface did NOT name (A7 / N36).

    The battle surface owns the report when it exists; this is the
    belt-and-braces arm for a path that resolved a grievance without a
    `battle_report` to write on. Non-battle resolutions never come through
    here, so A2's cause-naming and A13's `by_action` discriminator are
    untouched.
    """
    if not resolutions:
        return
    events = _pending_events(world)
    named = set(reported or [])
    for record in resolutions:
        if not record.get("is_player") or not record.get("by_action"):
            continue
        if record["marshal"] in named:
            continue
        events.append(_action_resolution_event(record))

def check_battle_resolution(world, attacker, defender, attacker_won: bool,
                            defender_won: bool, pre_attacker_strength: int,
                            pre_defender_strength: int,
                            attacker_participants: Optional[List] = None,
                            defender_participants: Optional[List] = None,
                            defender_broken: bool = False,
                            defer_dispatch: bool = False) -> List[Dict]:
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

    A7 (CA9 row 3): RETURNS the resolution records so the caller can name
    them at the battle surface.

    `defer_dispatch=True` withholds the next-morning bullet, which the
    caller then owes to `emit_unreported_resolutions` for anything the
    battle note could not carry. It defaults to FALSE deliberately: a
    caller that forgets keeps today's behaviour (a duplicated line) rather
    than silently losing the beat entirely.
    """
    events = None if defer_dispatch else _pending_events(world)
    records: List[Dict] = []

    def _clear(m, reason: str) -> None:
        rec = clear_jealousy(world, m, resolved_by_action=True,
                             events=events, reason=reason)
        if rec is not None:
            records.append(rec)

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
            _clear(marshal, "a victory against a worthy foe")
        elif marshal.personality == "cautious":
            shared = marshal.jealous_of in winner_names
            team = len([m for m in winning_side
                        if m.nation == marshal.nation])
            if shared or team >= CAUTIOUS_ALLY_RESOLUTION:
                _clear(marshal, "a victory won shoulder to shoulder")

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
            _clear(m, "meaningful contact with the enemy")
    return records


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
        # ══════════════════════════════════════════════════════════════
        # A8 (CA9 row 3): queue from the man who is ACTUALLY aggrieved.
        #
        # `Marshal.modify_relationship` reads the DERIVED value and writes
        # stored, so for a marshal carrying a live grievance the returned
        # change is 0 — and the loop above skips non-negative changes. The
        # envious man's own transition therefore never reached here and the
        # petition was built from his TARGET's change instead. Measured on
        # the 1805 boot: *"Sire, Ney has refused to attend council where
        # Murat is present"* while `Murat.jealous_of == 'Ney'` and
        # `Ney.jealous_of is None`. The flagship modal named the wrong man
        # as the sulker, and every arm then acted on him.
        #
        # Fixed HERE and not at the writer, per the Q5 ruling (option c):
        # a refuter MEASURED that repairing `modify_relationship` diverges
        # `BASELINE_SERIES` at index 20 with 21 of 41 readings changed and
        # the tail collapsing to 0 — a balance change in the flatter
        # direction, on the slice immediately before the playtest that is
        # meant to judge this row. This swap touches no relationship value,
        # no combat path and no harness; `_pair_key` is symmetric so the
        # seen-key is unaffected.
        # ══════════════════════════════════════════════════════════════
        if (getattr(other, "jealous_of", None) == marshal.name
                and getattr(marshal, "jealous_of", None) != other.name):
            marshal, other = other, marshal
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


# ═══════════════════ Q2(a): THE COUNCIL COMMAND ══════════════════════════
#
# CA9 row 3, ruling Q2(a). `JEALOUSY_SPEC.md` deferred a "council command
# ('to my tent')" arm with NO owner row — a GR9 orphan — while the
# confrontation body has always asked for exactly that: "He requests a
# command worthy of his talents."
#
# Every other arm writes `jealousy_turns_remaining` and nothing else, so
# the three of them cannot differ in KIND, only in price. This one is
# different in kind: it gives him a named objective, and the grievance
# then ends the way the system says grievances end — through
# `check_battle_resolution`'s per-personality predicate, on the field.
#
# It issues an EXISTING strategic order (PURSUE) through the shared
# executor at that order's own AP price. No new verb, no parser row, no
# `VALID_ACTIONS` entry, no campaign-log type: this is a dialogue option
# id, the same class as the NA-5 ultimatum arms.
COMMAND_ARM_ID = "command"
COMMAND_ARM_AP = 2          # a strategic order's own price...
COMMAND_ARM_AP_LITERAL = 1  # ...which the literal pays at half, as always


def command_arm_availability(world, marshal):
    """Can the Emperor give this man a command right now?

    Returns `(enabled, reason, quarry)` where `quarry` is the
    `(enemy, region)` the order would name.

    Re-derived at BOTH build time and ANSWER time — the A3 discipline.
    Every gate below MIRRORS a refusal `_execute_strategic_command` will
    itself raise, so the card can never offer something the executor is
    about to decline (and, worse, charge for). They are checked in the
    executor's own order.
    """
    if marshal is None:
        return False, "", None
    if int(getattr(marshal, "retreat_recovery", 0) or 0) > 0:
        return (False, f"{marshal.name} is still reforming after the retreat.",
                None)
    if getattr(marshal, "broken", False):
        return (False, f"{marshal.name}'s army is broken — rally it first.",
                None)
    if getattr(marshal, "artillery", False):
        return (False, f"{marshal.name}'s guns cannot pursue.", None)

    quarry = find_autonomous_attack_target(world, marshal)
    if quarry is None:
        return (False, "There is no enemy within his reach to send him "
                       "against.", None)
    enemy, region = quarry

    # F10: an identical standing order is a documented NO-OP that returns
    # success and charges nothing. Offering it would be the exact CA9
    # shape — a surface promising what the executor will not do.
    existing = getattr(marshal, "strategic_order", None)
    if (existing is not None
            and getattr(existing, "command_type", None) == "PURSUE"
            and str(getattr(existing, "target", "") or "").lower()
            == enemy.name.lower()
            and not getattr(existing, "condition", None)):
        return (False, f"{marshal.name} is already marching on "
                       f"{enemy.name}.", None)

    # The executor refuses a strategic march by an ENGAGED marshal unless
    # the quarry is one of the enemies standing on him.
    here = world.get_enemies_in_region(marshal.location, marshal.nation)
    if here and not any(e.name == enemy.name for e in here):
        return (False, f"{marshal.name} is already engaged at "
                       f"{marshal.location}.", None)

    # A first step INTO a contested province raises a `pending_interrupt`
    # that no `objection_response` can suppress — a second modal stacked
    # on this one. A co-located quarry never takes that path (the pursue
    # is handled in place) and an adjacent one filters the quarry itself
    # out of the blocking set, so the only opening left is a THIRD army
    # standing where we are sending him. Refuse it, with the reason said.
    if enemy.location != marshal.location:
        others = [e for e in world.get_enemies_in_region(
            region, marshal.nation) if e.name != enemy.name]
        if others:
            return (False, f"{region} is held in force — sending him there "
                           f"needs an order of its own.", None)
    return True, "", quarry


# ── A14 (CA9 row 3): the modal renders the MARSHAL ───────────────────────
#
# The backend has set a `speaker` on every petition since v3.2 and ZERO
# `.gd` files ever read it, so the flagship drama card was an unsigned
# staff memo. `war_weary` is the only petition that reads as drama, and
# the reason is one clause: *"I have my duchy, Sire. Why do we march
# again?"* — the man speaks.
#
# Authored HERE, not in `marshal_voice.py`, whose banks are keyed to five
# BATTLE situations with no consumer joining them to a petition.
# Deterministic (GR6), indexed by the pair's lifetime fires so a second
# audience does not repeat the first word for word.
_PETITION_VOICE = {
    "aggressive": (
        "\"Sire — I have earned better than to watch {target} take the "
        "field while I hold a road.\"",
        "\"Am I to be a garrison officer, Sire? Give me the enemy and I "
        "will give you {target}'s laurels twice over.\"",
        "\"I ask once more, Sire. A command. Any command.\"",
    ),
    "cautious": (
        "\"I do not complain, Sire. I observe that {target}'s despatches "
        "are read first, and mine are read after.\"",
        "\"My corps is in good order, Sire. It has been in good order for "
        "some time now.\"",
        "\"I have said my piece before. I will not say it a third time "
        "unless you wish it.\"",
    ),
    "literal": (
        "\"My orders have been carried out exactly, Sire. I note that "
        "{target} was given orders worth carrying out.\"",
        "\"I have made a full report of the patrols, Sire. There were "
        "eleven. There was nothing in any of them.\"",
        "\"I request reassignment, Sire. I will state the reason if it is "
        "required of me.\"",
    ),
}


def petition_speaker_line(marshal, target_name: str = "") -> str:
    """The marshal's own words for the petition header (display only)."""
    bank = _PETITION_VOICE.get(getattr(marshal, "personality", ""), ())
    if not bank:
        return ""
    fires = max(0, _lifetime_fires(marshal, target_name) - 1)
    line = bank[min(fires, len(bank) - 1)]
    return line.format(target=humanize_entity_name(target_name or "him"))


def _command_arm_ap(marshal) -> int:
    return (COMMAND_ARM_AP_LITERAL
            if getattr(marshal, "personality", "") == "literal"
            else COMMAND_ARM_AP)


def _command_option(world, marshal) -> Dict:
    """The Q2(a) option, with its availability already derived."""
    enabled, reason, quarry = command_arm_availability(world, marshal)
    cost = _command_arm_ap(marshal)
    if not enabled:
        # PT-A1: `available` is the NON-AP verdict, and it is what makes
        # this refusal survive delivery. `enabled` alone cannot carry it:
        # the builder runs during the turn pass, before `advance_turn`
        # refills AP, so IGR-1's refresher must be free to re-enable an
        # arm that only zero-AP had shut — and it cannot tell the two
        # cases apart from a bare `False`.
        return {"id": COMMAND_ARM_ID, "label": "Give him a command",
                "detail": reason, "unavailable_reason": reason,
                "cost_note": f"{cost} AP", "ap_cost": cost,
                "available": False,
                "enabled": False}
    enemy, region = quarry
    where = ("where he stands" if region == marshal.location
             else f"into {region}")
    return {
        "id": COMMAND_ARM_ID,
        "label": "Give him a command",
        "detail": (f"Send him against {enemy.name} {where}. A grievance "
                   f"ends on the field, not at the table — if he makes "
                   f"good on it, it ends for good. Giving the order may "
                   f"bring on a battle at once."),
        "cost_note": f"{cost} AP",
        "ap_cost": cost,
        "available": True,
        "enabled": _player_ap(world) >= cost,
    }


def _push_petition(world, petition: Dict) -> None:
    # TUT-F5 belt: EVERY petition kind passes through here — the lesson world
    # never shows one, whatever produced it (apply_jealousy is gated too, but
    # rivalry/Fontainebleau/war-weary producers live elsewhere).
    if jealousy_dormant(world):
        return
    world.pending_marshal_petition = petition
    queue = getattr(world, "_popup_queue", None)
    if queue is not None:
        queue.push("pending_marshal_petition", petition)


def refresh_petition_affordability(petition: Dict, world) -> Dict:
    """Re-derive each option's `enabled` against the player's CURRENT AP.

    In-game review July 25, 2026. Petitions are BUILT inside the turn pass
    (`turn_manager.process_turn` runs the jealousy pass BEFORE
    `world.advance_turn()`, which is what refills `actions_remaining`), so a
    petition assembled at the end of a spent turn baked `enabled: ap >= cost`
    against ZERO AP and was then shown to a player holding a full 4/4. Every
    priced arm — Promise Glory, Reassign, Mediate, Force Reconciliation —
    arrived permanently greyed, silently, with no reason given: the paid half
    of the marshal-petition channel was unreachable in ordinary play.

    `ap_cost` is authored on the option; affordability is decided HERE, at the
    moment the petition is handed to the client. Options that carry no
    `ap_cost` keep whatever `enabled` they were authored with.

    ══════════════════════════════════════════════════════════════════════
    PT-A1 — THE DELIVERY SEAM IS SUBTRACTIVE.

    The July-25 fix above over-corrected. It wrote `enabled = ap >= cost`
    *unconditionally*, so an arm `_command_option` had honestly refused —
    "There is no enemy within his reach to send him against." — arrived
    at the player ENABLED with its reason popped. Measured over a 19-turn
    campaign: 6 of 10 petitions shipped the `command` arm that way, and
    pressing it returned `success: False`, charged 0 AP, and destroyed the
    petition.

    Affordability is ONE gate among several, and it is the only one this
    function knows about. It may therefore only ever take an option AWAY.

    The verdict it must not overturn is `available` — the builder's NON-AP
    gate. A bare `enabled: False` cannot serve, because the builder bakes
    build-time AP into it too, and re-enabling exactly that case is what
    IGR-1 landed this function to do. So: options carrying
    `available: False` stay shut with their own reason; options with no
    `available` key (every arm that has no gate but its price) are
    governed by AP alone, exactly as before.

    This function is PURE — it copies the petition and every option, and
    never mutates its input, so the stored petition keeps the builder's
    verdict and every re-delivery re-derives from it.
    ══════════════════════════════════════════════════════════════════════
    """
    if not isinstance(petition, dict):
        return petition
    options = petition.get("options")
    if not isinstance(options, list):
        return petition
    ap = _player_ap(world)
    refreshed = []
    for option in options:
        if not isinstance(option, dict):
            refreshed.append(option)
            continue
        cost = option.get("ap_cost")
        if cost is None:
            refreshed.append(option)
            continue
        gate_open = option.get("available")
        gate_open = True if gate_open is None else bool(gate_open)
        authored_reason = option.get("unavailable_reason")
        option = dict(option)
        cost = int(cost)
        affordable = ap >= cost
        option["enabled"] = gate_open and affordable
        if not gate_open:
            # Shut for a reason that has nothing to do with action points.
            # Say THAT reason — AP is not why he cannot go.
            if authored_reason is not None:
                option["unavailable_reason"] = authored_reason
        elif not affordable:
            # Never grey a choice silently — say what it would take.
            option["unavailable_reason"] = (
                f"Needs {cost} action point{'s' if cost != 1 else ''} — "
                f"you have {ap}."
            )
        else:
            option.pop("unavailable_reason", None)
        refreshed.append(option)
    petition = dict(petition)
    petition["options"] = refreshed
    return petition


def _standing_cost_detail(marshal, target) -> str:
    """§3 (CA9 row 3): what letting the grievance stand actually costs, in
    men and turns rather than in adjectives.

    The magnitude comes from the same rule the combat math uses — an
    aggressive marshal withholds ENTIRELY, anyone else brings about half —
    so the modal cannot promise a different number from the one the battle
    resolves on. (`CombatExecutor._pair_contribution_scale` owns the rule;
    this reads its two thresholds, which are personality-only and need no
    executor instance.)
    """
    turns = int(getattr(marshal, "jealousy_turns_remaining", 0) or 0)
    plural = "s" if turns != 1 else ""
    men = int(getattr(marshal, "strength", 0) or 0)
    if getattr(marshal, "personality", "") == "aggressive":
        weight = (f"he brings NONE of his {men:,} men to any battle "
                  f"{target.name} leads")
    else:
        weight = (f"he brings about half the weight of his {men:,} men to "
                  f"any battle {target.name} leads")
    return (f"Free, and it fixes nothing. For {turns} more turn{plural} "
            f"{weight}, and the quarrel may harden further.")


def queue_confrontation_petition(world, marshal, target, level: int = 0) -> None:
    """Jealousy confrontation (spec §6; CA8-D3 Q2 re-fires it once per
    escalation level, so `level` >= 1 carries the escalation register —
    the audience must hear that this is the SAME feud, grown worse)."""
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
    escalation_clause = {
        1: (" The staff now speak of the quarrel openly — this is no "
            "longer a passing mood."),
        2: (" The breach between them has become entrenched; he presses "
            "the point with unusual heat."),
        3: (f" The feud with {target.name} is now mutual and the army "
            f"knows it. He asks, plainly, where the Emperor stands."),
    }.get(int(level), "")
    body += escalation_clause
    _push_petition(world, {
        "kind": "jealousy_confrontation",
        "title": f"Marshal {marshal.name} seeks an audience",
        "body": body,
        "speaker": marshal.name,
        # A14: the man says something. `speaker` has been set since v3.2
        # and read by nothing.
        "speaker_line": petition_speaker_line(marshal, target.name),
        "options": [
            # ════════════════════════════════════════════════════════
            # §3 (CA9 row 3): the user's own observation — "acknowledge
            # seems to do nothing". It does nothing, by design since v2,
            # and the Aug-8 fix made the copy honest without making the
            # option a choice.
            #
            # RENAMED, not deleted and not given a fourth price. Deleting
            # it makes Rebuke the only free arm and coerces a -5 trust hit
            # at 0 AP; a fourth price on a card whose problem was that all
            # prices bought the same outcome makes it worse.
            # "Let it stand" is the system's own vocabulary (§6b already
            # ships "Let Them Sort It Out") and, unlike "Acknowledge" —
            # which is the DISMISS verb everywhere else in the client
            # (proclamation_popup, notification_bar) — it is honest about
            # being a refusal to act.
            #
            # And the price is now stated in the units the player feels.
            # "Souring his ties and coordination" is not a decision; "he
            # brings none of his 24,000 men to any battle Davout leads" is.
            # Read off `_pair_contribution_scale`'s own thresholds so the
            # sentence cannot drift from the combat math.
            # ════════════════════════════════════════════════════════
            {"id": "acknowledge", "label": "Let it stand",
             "detail": _standing_cost_detail(marshal, target),
             "cost_note": "Free", "enabled": True},
            # Q1(b): the arm now buys something no other arm can — the
            # quarrel cannot HARDEN while your word stands. Said out loud,
            # because a mechanic the player cannot see is not a decision;
            # the old detail named only the timer, which is why paying read
            # as worse than ignoring the card.
            {"id": "promise", "label": promise_label,
             "detail": (f"His patience is bought — the grievance shortens by "
                        f"{CONFRONT_PROMISE_DURATION_CUT} turns, and for "
                        f"{CONFRONT_PROMISE_HOLD_TURNS} turns the quarrel "
                        f"cannot harden further."),
             "cost_note": f"{CONFRONT_PROMISE_AP} AP",
             "ap_cost": CONFRONT_PROMISE_AP,
             "enabled": ap >= CONFRONT_PROMISE_AP},
            {"id": "rebuke", "label": "Rebuke",
             "detail": (f"Trust {CONFRONT_REBUKE_TRUST}. The grievance "
                        f"shortens by {CONFRONT_REBUKE_DURATION_CUT} turn. "
                        + rebuke_rider).strip(),
             "cost_note": "", "enabled": True},
            # Q2(a): he asked for a command. This is the arm that gives him
            # one — and the only arm whose outcome is not a number on a
            # hidden timer. Honest availability: when the executor would
            # refuse, the button says so instead of failing after the click.
            _command_option(world, marshal),
        ],
        "context": {"marshal": marshal.name, "target": target.name,
                    "escalation_level": int(level)},
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
             "cost_note": "1 AP", "ap_cost": 1, "enabled": ap >= 1},
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
             "cost_note": "2 AP", "ap_cost": 2, "enabled": ap >= 2},
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
        "speaker_line": petition_speaker_line(marshal, other.name),
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
    armed = bool(getattr(world, "fontainebleau_armed", True))
    if len(eroding) < FONTAINEBLEAU_MIN_ERODING:
        world.fontainebleau_armed = True
        return
    last = int(getattr(world, "fontainebleau_last_turn", -999))
    if not armed or world.current_turn - last < FONTAINEBLEAU_COOLDOWN:
        return
    if getattr(world, "pending_marshal_petition", None) is not None:
        return
    world.fontainebleau_last_turn = int(world.current_turn)
    world.fontainebleau_armed = False
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
                 f"{target_nation}."),
        "speaker": marshal.name,
        # A14: this petition was ALREADY the only one that read as drama,
        # and the reason was this clause. Lifted out of the staff prose
        # into the field the modal speaks, so every kind works the same
        # way rather than this one being accidentally good.
        "speaker_line": ("\"I have my duchy, Sire. Why do we march "
                         "again?\""),
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

    # ══════════════════════════════════════════════════════════════════
    # PT-A1 — A REFUSAL MUST NOT DESTROY THE DECISION.
    #
    # The pop used to run HERE, before the arm was tried. So every
    # `success: False` an arm can return — no legal target, not enough
    # AP, the executor declining — silently deleted the petition: the
    # player was told "no", charged nothing, and never offered the card
    # again. Measured live on the `command` arm, which PT-A1's other half
    # had been mis-enabling in the first place.
    #
    # The petition is now retired by SUCCESS. Two details are load-bearing:
    #   * the retirement is IDENTITY-checked, because an arm may push a
    #     NEW petition (escalation) and that one must survive;
    #   * a failed answer re-attaches the card to the result, so the
    #     client re-renders the decision it still has to make. (The turn
    #     pass also re-pushes an unanswered petition, `:2523` — this is
    #     the same-response half of that promise.)
    # ══════════════════════════════════════════════════════════════════
    if kind == "jealousy_confrontation":
        # Q2(a): the command arm needs the executor, exactly as the
        # war-weary arm already does for its declare-war command.
        result = _apply_confrontation_choice(world, choice, context,
                                             executor=executor,
                                             game_state=game_state)
    elif kind == "rivalry_confrontation":
        result = _apply_rivalry_choice(world, choice, context)
    elif kind == "fontainebleau":
        result = _apply_fontainebleau_choice(world, choice, context)
    elif kind == "war_weary":
        result = _apply_war_weary_choice(world, choice, context,
                                         executor=executor,
                                         game_state=game_state)
    else:
        result = {"success": False,
                  "message": f"Unknown petition kind '{kind}'."}

    if not isinstance(result, dict):
        return result
    if result.get("success"):
        if getattr(world, "pending_marshal_petition", None) is petition:
            world.pending_marshal_petition = None
            queue = getattr(world, "_popup_queue", None)
            if queue is not None:
                queue.set("pending_marshal_petition", None)
    else:
        result.setdefault("marshal_petition", petition)
    return result


def _apply_command_choice(world, marshal, executor, game_state) -> Dict:
    """Q2(a): the Emperor gives him the command he asked for.

    Issues an EXISTING strategic order (PURSUE) through the shared
    executor. Deliberate details, each one a defect avoided:

    * availability is RE-DERIVED here, not trusted from the card — the
      card may be several turns old (A3's discipline);
    * `objection_response="proceed"` with `v2_insist_penalty=0` suppresses
      the strategic objection that would otherwise stack a second modal on
      this one. Any other string returns "Unknown objection response";
      omitting the penalty key costs a real -10 trust;
    * the AP charge reads `result.get("variable_action_cost")` with a
      default. On the objection return that key is ABSENT, not zero, so a
      subscript is a KeyError -> a blanket except -> the player sees
      "Error: 'variable_action_cost'" AFTER the petition has been popped
      and the world mutated;
    * `delegation_inferred` is never set, which keeps the CR-5 inferred
      first-step gate structurally dead on this path;
    * `cancel_autonomous_warning_on_order` is called explicitly — it
      normally rides `executor.execute`, which this path bypasses, and a
      marshal who has just been GIVEN an objective must not still launch
      the attack he was warned about.
    """
    if executor is None or game_state is None:
        return {"success": False,
                "message": "There is no staff to carry the order."}
    enabled, reason, quarry = command_arm_availability(world, marshal)
    if not enabled:
        return {"success": False,
                "message": reason or "He cannot take the field just now."}
    enemy, region = quarry

    cost = _command_arm_ap(marshal)
    if _player_ap(world) < cost:
        return {"success": False,
                "message": "Not enough action points to give the order."}

    phrase = f"{marshal.name}, deal with {enemy.name}"
    result = executor._execute_strategic_command(
        {"strategic_type": "PURSUE", "raw_input": phrase},
        {"marshal": marshal.name, "target": enemy.name,
         "target_type": "marshal",
         "objection_response": "proceed", "v2_insist_penalty": 0},
        game_state) or {}

    if not result.get("success"):
        return {"success": False,
                "message": result.get("message")
                or "The order could not be carried."}

    spent = int(result.get("variable_action_cost") or 0)
    if spent:
        _spend_player_ap(world, spent)
    cancel_autonomous_warning_on_order(world, marshal)

    world.log_event({
        "type": "jealousy_confrontation",
        "marshal": marshal.name,
        "target": getattr(marshal, "jealous_of", None),
        "nation": marshal.nation,
        "choice": COMMAND_ARM_ID,
    })
    message = (f"\"{enemy.name}, then.\" {marshal.name} takes the command "
               f"and goes. {result.get('message', '')}").strip()
    out = {"success": True, "message": message}
    # Carry whatever the first step produced — the order can bring on a
    # battle immediately, and the card must not swallow it.
    for key in ("battle_report", "pending_interrupt", "requires_input",
                "first_step_interrupt", "path", "strategic_type"):
        if key in result:
            out[key] = result[key]
    return out


def _apply_confrontation_choice(world, choice: str, context: Dict,
                                executor=None, game_state=None) -> Dict:
    marshal = world.marshals.get(context.get("marshal"))
    if marshal is None:
        return {"success": True, "message": "The moment has passed."}
    # ══════════════════════════════════════════════════════════════════
    # A3 (CA9 row 3) — the stale-answer guard. CA9-N4's fixable half.
    #
    # The petition never expired and never re-validated, so a card queued
    # on turn 11 and answered on turn 16 was applied to LIVE state:
    # measured, `promise` spent 1 AP and reported "His grievance shortens"
    # against `jealous_of = None`, and `rebuke` applied a real -5 trust to
    # a marshal whose quarrel was already over. Charging for a quarrel
    # that has ended and reporting success is the exact "the surface tells
    # the player something the state does not support" shape CA9 filed.
    #
    # Scoped to `jealousy_confrontation` DELIBERATELY. `war_weary` carries
    # the assembled declare-war command in its context
    # (`diplomatic_executor._apply_war_weary_choice`), so retiring one of
    # those on a mismatch would silently cancel a war declaration — a
    # worse bug than the one being fixed. The other two kinds have no
    # single-marshal target to re-validate against.
    #
    # The card is RETIRED rather than re-served: it was already popped
    # from the queue by `handle_petition_response` above, and re-pushing a
    # card whose subject has changed is how the turn-4-to-41 zombie in the
    # memo happened.
    # ══════════════════════════════════════════════════════════════════
    _asked_about = context.get("target")
    if _asked_about and marshal.jealous_of != _asked_about:
        return {
            "success": True,
            "message": (
                f"The moment has passed — {marshal.name}'s quarrel with "
                f"{_asked_about} is already behind him. Nothing was spent."),
        }
    if choice == COMMAND_ARM_ID:
        return _apply_command_choice(world, marshal, executor, game_state)
    if choice == "promise":
        if not _spend_player_ap(world, CONFRONT_PROMISE_AP):
            return {"success": False,
                    "message": "Not enough action points to promise glory."}
        marshal.jealousy_turns_remaining = max(
            0, marshal.jealousy_turns_remaining - CONFRONT_PROMISE_DURATION_CUT)
        # Q1(b): the promise HOLDS the line. Written both directions, because
        # `_set_escalation_level` advances the pair together and a promise to
        # one man must not be defeated by his rival's fire landing first.
        _hold_until = int(world.current_turn) + CONFRONT_PROMISE_HOLD_TURNS
        _target_name = context.get("target")
        if _target_name:
            marshal.jealousy_escalation_hold[_target_name] = _hold_until
            _other = world.marshals.get(_target_name)
            if _other is not None:
                _other.jealousy_escalation_hold[marshal.name] = _hold_until
        if marshal.jealousy_turns_remaining == 0 and marshal.jealous_of:
            clear_jealousy(world, marshal, resolved_by_action=False,
                           events=_pending_events(world),
                           reason="the Emperor's promise")
        message = (f"{marshal.name} bows. \"I will hold you to it, Sire.\" "
                   f"His grievance shortens, and while your word stands the "
                   f"quarrel will go no further.")
    elif choice == "rebuke":
        marshal.modify_trust(CONFRONT_REBUKE_TRUST)
        marshal.jealousy_turns_remaining = max(
            0, marshal.jealousy_turns_remaining - CONFRONT_REBUKE_DURATION_CUT)
        if marshal.personality == "aggressive":
            marshal.jealousy_autonomous_warned = False
            marshal.jealousy_rebuked_cycle = True
        if marshal.personality == "literal":
            marshal.literal_intel_paused_turn = int(world.current_turn) + 1
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
        """§6b mend. Q4(a) (CA9 row 3 ruling) makes two things explicit.

        THE TRAPDOOR IS INTENDED. At stored -2 a shared victory maxes at 35
        against `relationship.py`'s strict `> 50`, so Hostile does not heal
        through play, and the §6b escape only ever queues on a DOWNWARD
        transition — so the pairs authored at -2 in the scenario (Davout and
        Bernadotte's Auerstedt no-show) can never produce one. That is
        deliberate authored character, not a gap, and it is stated here
        because two lenses read it as a bug.

        Which is also why a mend must never raise a pair whose escalation
        the game has already called PERMANENT. The entrenchment is a record;
        a handshake may stop the bleeding, it may not erase the wound. The
        clamp keeps a free 60%-chance arm from laundering authored hostility
        into neutrality.
        """
        # A CEILING, not a floor: the clamp limits how HIGH a mend may lift
        # an entrenched pair, so `min` is correct here and `max` would be a
        # no-op (max(-1, 0) == 0). Stated because the first cut got it
        # backwards and the pin caught it.
        _entrenched = max(get_escalation_level(marshal, other.name),
                          get_escalation_level(other, marshal.name)) \
            >= ESCALATION_PERMANENT_LEVEL
        _value = min(int(to_value), -1) if _entrenched else int(to_value)
        marshal.set_relationship(other.name, _value)
        other.set_relationship(marshal.name, _value)

    def _mend_grievance(reason: str) -> None:
        """Q4(a): a SUCCESSFUL mend must move something a mechanic reads.

        `_restore` writes STORED, but `get_relationship` subtracts 1 for a
        live grievance — so `force_reconciliation` charged 2 AP, printed
        "Under your eye they shake hands", and left the derived value
        exactly where it was. A second inert paid arm, on top of the promise
        arm the audit found strictly dominated. The ruling's option: clear
        the grievance on success, so the handshake is real.
        """
        for a, b in ((marshal, other), (other, marshal)):
            if getattr(a, "jealous_of", None) == b.name:
                clear_jealousy(world, a, resolved_by_action=False,
                               events=_pending_events(world), reason=reason)

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
                    _mend_grievance("the Emperor's mediation")
                    outcome = "Your word carries. The breach is mended."
                else:
                    outcome = "They listen politely. Nothing changes."
            elif authority >= 40:
                if roll < 0.40:
                    _restore(0)
                    _mend_grievance("the Emperor's mediation")
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
                    _mend_grievance("the Emperor forced the reconciliation")
                    outcome = "Under your eye they shake hands. Barely."
                else:
                    outcome = "Cold correctness. Nothing more."
            elif authority >= 60:
                if roll < 0.30:
                    _restore(-1)
                    _mend_grievance("the Emperor forced the reconciliation")
                    outcome = "A stiff, public handshake. It holds — for now."
                elif roll < 0.80:
                    outcome = "Neither yields. The breach stands."
                else:
                    world.authority_tracker.modify_authority(-3)
                    outcome = "The failure was public (authority -3)."
            else:
                if roll < 0.10:
                    _restore(-1)
                    _mend_grievance("the Emperor forced the reconciliation")
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

# ── A13 (CA9 row 3): the narration cap, AI-6 shape ───────────────────────
#
# The audit measured ~15 marshal-drama lines per answerable decision, 48
# lines in 12 turns, and a peak of 10-12 in a single briefing — against
# `INTENT_DISPATCH_CAP = 2` for intent narration and 3 for marshal arcs.
# Jealousy capped FIRES only, never LINES.
#
# Deliberately built LAST (memo §6 #3): half the volume was duplication
# and self-contradiction, and a cap applied first would have preserved
# the wrongness and collapsed the correct lines. A12 removed the
# duplication; this bounds what remains.
#
# The cap lives in the PRODUCER so it governs routine movement only. The
# BEATS are exempt by type — and, for `jealousy_resolved`, by
# `by_action`, because an earned resolution and a timer expiry share a
# type and are told apart only by A13's own prerequisite (landed in A2).
# AI-6's exemption could be purely structural because its beats are
# produced elsewhere; this one cannot, which is exactly why that key had
# to exist first.
JEALOUSY_DISPATCH_CAP = 3          # routine drama lines per dispatch

JEALOUSY_NARRATION_EXEMPT = (
    "glory_crowned",                 # the crown changes heads
    "glory_crown_lost",
    "jealousy_autonomous_warning",   # the fore-warning and its counter-lever
    "jealousy_autonomous_attack",    # ...and the attack actually landing
    "jealousy_separation_warning",   # the one arm the player OPTED INTO
    "fontainebleau_petition",        # a petition arriving
    "marshal_commissioned",
)

# `jealousy_escalation` is NOT exempt wholesale — the memo's list says
# escalation-to-PERMANENT, and it is right. "The wound will not close on
# its own" (level 2) and the mutual spiral (level 3) are beats; "has
# become a matter of concern" (level 1) is routine movement, and so is
# the held-promise line, which repeats for as long as the promise stands.
JEALOUSY_EXEMPT_ESCALATION_LEVEL = ESCALATION_PERMANENT_LEVEL


def _drama_rank(world, event: Dict):
    """Which routine lines survive the cap: the deepest quarrel first.

    Same severity vocabulary as A12's rung-3.5 ranking, so the briefing's
    closing note and its event list cannot disagree about which quarrel
    matters most.
    """
    marshal = world.marshals.get(event.get("marshal") or "")
    target = event.get("target") or (
        getattr(marshal, "jealous_of", None) if marshal else None) or ""
    if marshal is None:
        return (0, 0, str(event.get("marshal") or ""))
    return (-int(get_escalation_level(marshal, target)),
            -int(_lifetime_fires(marshal, target)),
            marshal.name)


def _cap_routine_drama(world, events: List[Dict], start: int) -> None:
    """Bound the routine lines this pass added; never touch a beat."""
    added = events[start:]
    if not added:
        return
    routine, keep = [], []
    for event in added:
        etype = str(event.get("type", ""))
        if etype in JEALOUSY_NARRATION_EXEMPT:
            keep.append(event)
        elif etype == "jealousy_resolved" and event.get("by_action"):
            # An EARNED resolution is the payoff beat of the whole system.
            keep.append(event)
        elif (etype == "jealousy_escalation"
                and not event.get("held")
                and int(event.get("level") or 0)
                >= JEALOUSY_EXEMPT_ESCALATION_LEVEL):
            keep.append(event)
        else:
            routine.append(event)
    if len(routine) <= JEALOUSY_DISPATCH_CAP:
        return
    routine.sort(key=lambda e: _drama_rank(world, e))
    shown = routine[:JEALOUSY_DISPATCH_CAP]
    overflow = len(routine) - JEALOUSY_DISPATCH_CAP
    nation = (shown[0].get("nation") if shown else world.player_nation)
    tail = {
        "type": "jealousy_drama_tail",
        "message": (
            f"The staff report {overflow} further matter"
            f"{'' if overflow == 1 else 's'} among the marshals — the "
            f"Generals screen has the particulars."),
        "nation": nation,
        "count": int(overflow),
    }
    # Rebuild in place: the caller holds a reference to this list, and
    # `advance_turn` drains the same object.
    events[start:] = keep + shown + [tail]


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
    # A13: the cap governs what THIS pass adds. Anything already stashed
    # (battle-time hooks, autonomous attacks) has its own surface and its
    # own rate limits, and is left alone.
    _cap_from = len(events)
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
    #
    # A12: every pair cooled HERE is remembered for the rest of this pass,
    # so step 3 cannot hand the same man straight back. See
    # `JEALOUSY_SUPPRESS_SAME_PASS_REFIRE`.
    cooled_this_pass = set()
    for marshal in list(world.marshals.values()):
        target_name = getattr(marshal, "jealous_of", None)
        if not target_name:
            continue
        target = world.marshals.get(target_name)
        if target is None or not _is_standing(target) \
                or target.nation != marshal.nation:
            clear_jealousy(world, marshal, resolved_by_action=False,
                           events=events, reason="the rival is gone")
            cooled_this_pass.add((marshal.name, target_name))
            continue
        # Ladder shift (spec §2): passing the target resolves with surge.
        if get_glory_score(marshal, turn) > get_glory_score(target, turn):
            clear_jealousy(world, marshal, resolved_by_action=True,
                           events=events,
                           reason=f"he has surpassed {target_name} in glory")
            cooled_this_pass.add((marshal.name, target_name))
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
            cooled_this_pass.add((marshal.name, target_name))

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
        # A12: the pair cooled earlier in THIS pass — a resentment cannot
        # cool and flare on the same page. Sited at the CANDIDATE gate, not
        # at the apply loop, so the suppressed man does not consume one of
        # his nation's two fire slots (`MAX_FIRES_PER_NATION_TURN`); the
        # slot goes to the next-most-aggrieved marshal instead, which is
        # the behaviour the rate limit was written for.
        if JEALOUSY_SUPPRESS_SAME_PASS_REFIRE \
                and (marshal.name, target.name) in cooled_this_pass:
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
        if getattr(marshal, "jealousy_rebuked_cycle", False):
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
            "message": (f"{humanize_entity_name(marshal.name)} is eyeing "
                        f"{humanize_entity_name(enemy.name)}'s position "
                        f"at {region_name}. I cannot guarantee he will wait "
                        f"for orders, Sire — any command would restrain him."),
            "nation": marshal.nation,
            "marshal": marshal.name,
        })

    # 6) crowns
    events.extend(recompute_crowns(world))

    # ══════════════════════════════════════════════════════════════════
    # 7) §6b separation warnings
    #
    # A9 (CA9 row 3): this was a permanent, un-cancellable subscription
    # with a per-turn nag. `separation_flagged` was set True in exactly one
    # place and False in NO place anywhere in `backend/`, so the one arm of
    # the §6b modal that honestly described itself ("Not a fix — Berthier
    # will warn you whenever their commands stand together") became the
    # most annoying thing the channel does, forever, for a rivalry the
    # player may have long since mended.
    #
    # Two fixes, both here:
    #   * RETIREMENT — the flag watches a rivalry. When the rivalry is gone
    #     (the pair's stored standing is no longer negative) the
    #     subscription retires itself, both directions. `set_relationship`
    #     is not used: this only ever deletes the watcher, never touches
    #     the authored relationship (Q4 rules that mend arms must not
    #     launder authored character).
    #   * COOLDOWN — `SEPARATION_WARNING_COOLDOWN` turns between warnings
    #     for a pair. The FIRST proximity always warns (an absent entry
    #     means never warned), which is what `test_jealousy_v32.py`'s
    #     presence pin asserts.
    # ══════════════════════════════════════════════════════════════════
    _turn_now = int(getattr(world, "current_turn", 0) or 0)
    for marshal in world.marshals.values():
        if marshal.nation != world.player_nation:
            continue
        # Iterate a snapshot: the retirement arm mutates the dict.
        for other_name, flagged in list(
                getattr(marshal, "separation_flagged", {}).items()):
            if not flagged or marshal.name > other_name:
                continue        # one warning per pair
            other = world.marshals.get(other_name)
            if other is None or not _is_standing(other) or not _is_standing(marshal):
                continue
            # Retirement: the quarrel this watches is over.
            #
            # Reads the STORED value, not `get_relationship`. The derived
            # getter subtracts 1 for a live grievance, so a marshal with any
            # active envy toward his old rival would read as still-hostile
            # and the file would never close. What this watches is the §6b
            # RIVALRY, and a successful `mediate` writes stored 0 through
            # `set_relationship` — so the file closes exactly when the
            # player's mediation actually worked.
            if marshal.relationships.get(other_name, 0) >= 0:
                marshal.separation_flagged.pop(other_name, None)
                marshal.separation_warned_turn.pop(other_name, None)
                other.separation_flagged.pop(marshal.name, None)
                other.separation_warned_turn.pop(marshal.name, None)
                events.append({
                    "type": "jealousy_separation_warning",
                    "message": (f"Berthier closes the file on {marshal.name} "
                                f"and {other_name}: whatever stood between "
                                f"them is settled. You will not be warned "
                                f"about them again."),
                    "nation": marshal.nation,
                    "marshal": marshal.name,
                })
                continue
            region = world.regions.get(marshal.location)
            adjacent = set(getattr(region, "adjacent_regions", []) or []) \
                if region else set()
            if other.location == marshal.location or other.location in adjacent:
                _last = marshal.separation_warned_turn.get(other_name)
                if (_last is not None
                        and _turn_now - int(_last) < SEPARATION_WARNING_COOLDOWN):
                    continue
                marshal.separation_warned_turn[other_name] = _turn_now
                other.separation_warned_turn[marshal.name] = _turn_now
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
        if getattr(marshal, "jealousy_rebuked_cycle", False) \
                and not getattr(marshal, "jealous_of", None):
            marshal.jealousy_rebuked_cycle = False

    _cap_routine_drama(world, events, _cap_from)
    return events


# ═══════════════ AUTONOMOUS ATTACK (spec §7 + §0.2 item 7) ════════════════

def find_autonomous_attack_target(world, marshal):
    """Glory-seeking target priority: the WEAKEST adjacent at-war enemy
    (desperate, not smart). Returns (enemy_marshal, region_name) or None.

    AI-5 (§4.5, the jealousy wire): the EC-M proxy finally has a real
    faction to serve — when the marshal's OWN COURT holds a live acquire
    design, an enemy standing on one of its unmet target provinces
    outranks a merely weaker one (Bernadotte hunts his glory where the
    Emperor wants the map redrawn). Preference only, never eligibility:
    with no design overlap among the reachable enemies, the weakest-first
    behaviour is byte-identical."""
    region = world.regions.get(marshal.location)
    if region is None:
        return None
    reachable = {marshal.location} | set(
        getattr(region, "adjacent_regions", []) or [])
    from backend.game_logic.agendas import get_agenda_military_targets
    design_frontier = set(
        get_agenda_military_targets(marshal.nation, world))
    best = None
    best_key = None
    for enemy in world.marshals.values():
        if enemy.nation == marshal.nation or enemy.strength <= 0:
            continue
        if getattr(enemy, "captured_by", ""):
            continue
        if not world.is_at_war(marshal.nation, enemy.nation):
            continue
        if enemy.location not in reachable:
            continue
        # Sort key: design-frontier enemies first (0 < 1), weakest within
        # each band — so a court with no design keeps today's pure
        # weakest-first ordering byte-identically.
        key = (0 if enemy.location in design_frontier else 1,
               enemy.strength)
        if best is None or key < best_key:
            best = enemy
            best_key = key
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
            "message": (f"{humanize_entity_name(marshal.name)}, hungry for "
                        f"glory, has attacked "
                        f"{humanize_entity_name(enemy.name)} on his own "
                        f"initiative."),
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
