"""
Coalition System — Phase 8 Session 7 (COALITION_SPEC v1.1)

The coalition system creates the core Napoleonic strategic puzzle: the better
you play, the harder Europe pushes back. Threat accumulates from aggressive
actions, triggers brewing warnings, and eventually causes multi-nation
coalition wars.

All coalition logic lives in this file. Functions are called from:
  - executor.py (after battles, captures, vassalization → add_threat)
  - world_state.py advance_turn (process_coalition_turn)
  - diplomacy.py (acceptance formula → get_coalition_loyalty_penalty)
  - enemy_ai.py (convergence bias, friction, is_coalition_member)
"""

from typing import Dict, List, Optional

from backend.notifications import (
    create_notification, NotificationPriority,
    COALITION_THREAT_TENSION, COALITION_MURMURS, COALITION_BREWING,
    COALITION_DECLARED, COALITION_MEMBER_PEACED, COALITION_DISSOLVED,
    COALITION_COOLDOWN_ENDED,
)

# ════════════════════════════════════════════════════════════════
# CONSTANTS
# ════════════════════════════════════════════════════════════════

PEACEFUL_STATES = ("PEACE", "NON_AGGRESSION", "OPEN_BORDERS",
                   "DEFENSIVE_ALLIANCE", "ALLIANCE")

# Threat thresholds (§3a)
THREAT_CALM_MAX = 29
THREAT_TENSION_MIN = 30
THREAT_MURMURS_MIN = 40
THREAT_BREWING_MIN = 60
THREAT_INSTANT_MIN = 80
THREAT_OVERRIDE_COOLDOWN_MIN = 90

# Brewing cancellation floor (§3c momentum rule)
BREWING_CANCEL_THRESHOLD = 40

# Coalition dissolution threat floor (§7a)
DISSOLUTION_THREAT_THRESHOLD = 20

# Post-dissolution cooldown (§7c)
COALITION_COOLDOWN_TURNS = 5

# Brewing countdown (§3c)
BREWING_COUNTDOWN = 3

# Decay cap (§2b)
DECAY_CAP = 3

# War exhaustion caps
WAR_EXHAUSTION_MAX = 200
WAR_EXHAUSTION_BATTLE_CAP = 20

# Coalition loyalty penalty base (§6a)
COALITION_LOYALTY_BASE = -15

# Coalition ordinal names
_ORDINALS = {1: "First", 2: "Second", 3: "Third", 4: "Fourth", 5: "Fifth",
             6: "Sixth", 7: "Seventh"}


# ════════════════════════════════════════════════════════════════
# HELPER: Get all nations from world
# ════════════════════════════════════════════════════════════════

def _get_all_nations(world) -> List[str]:
    """Return all nations (player + enemy). Consistent with diplomacy.py pattern."""
    return [world.player_nation] + list(getattr(world, 'enemy_nations', []))


def _get_diplo_key(a: str, b: str) -> str:
    """Alphabetically sorted nation pair key."""
    return "|".join(sorted([a, b]))


def _get_relation(world, a: str, b: str) -> int:
    """Get relation between two nations."""
    return world.nation_relations.get(_get_diplo_key(a, b), 0) or 0


def _get_diplo_state(world, a: str, b: str) -> str:
    """Get diplomatic state between two nations."""
    return world.diplomatic_states.get(_get_diplo_key(a, b), "PEACE")


# ════════════════════════════════════════════════════════════════
# §2a. THREAT ACCUMULATION
# ════════════════════════════════════════════════════════════════

def add_threat(world, amount: int, source_key: str) -> int:
    """Add threat from an aggressive action (§2a).

    Args:
        world: WorldState
        amount: Positive int to add
        source_key: e.g. "battle_win", "capital_capture", "war_declaration"

    Returns:
        New threat_level (clamped 0-100)
    """
    if amount <= 0:
        return int(world.threat_level)
    old = world.threat_level
    world.threat_level = int(min(100, max(0, world.threat_level + amount)))
    world.threat_sources_this_turn.append({
        "source": source_key,
        "amount": int(amount),
    })
    return int(world.threat_level)


def reduce_threat(world, amount: int, source_key: str) -> int:
    """Reduce threat from voluntary concessions (§2b voluntary).

    For things like releasing vassals or returning territory — NOT per-turn decay.

    Returns:
        New threat_level (clamped 0-100)
    """
    if amount <= 0:
        return int(world.threat_level)
    world.threat_level = int(min(100, max(0, world.threat_level - amount)))
    world.threat_sources_this_turn.append({
        "source": source_key,
        "amount": int(-amount),
    })
    return int(world.threat_level)


# ════════════════════════════════════════════════════════════════
# §2b. THREAT DECAY
# ════════════════════════════════════════════════════════════════

def _calculate_threat_decay(world) -> int:
    """Calculate per-turn threat decay (§2b).

    Formula: 1 base + 1 per peaceful non-vassal nation (cap 3) + CS bonus.
    """
    france = world.player_nation
    vassals = set(getattr(world, 'vassals', {}).keys())

    peace_nations = []
    for n in _get_all_nations(world):
        if n == france:
            continue  # Self-exclusion (§2b IMPORTANT note)
        if n in vassals:
            continue
        state = _get_diplo_state(world, france, n)
        if state in PEACEFUL_STATES:
            peace_nations.append(n)

    raw_decay = 1 + len(peace_nations)
    decay = min(raw_decay, DECAY_CAP)

    # Continental System bonus — separate, not subject to cap (§2b)
    cs_members = getattr(world, 'continental_system_members', [])
    if len(cs_members) >= 2:
        decay += 1

    return int(decay)


# ════════════════════════════════════════════════════════════════
# §3b. QUALIFYING NATIONS
# ════════════════════════════════════════════════════════════════

def qualifies_for_coalition(nation: str, world) -> bool:
    """Check if a nation qualifies for coalition membership (§3b).

    Qualifies if: relation < -10, not vassal, not already at war with France.
    """
    france = world.player_nation
    if nation == france:
        return False
    relation = _get_relation(world, france, nation)
    is_vassal = nation in getattr(world, 'vassals', {})
    already_at_war = _get_diplo_state(world, france, nation) == "WAR"
    return relation < -10 and not is_vassal and not already_at_war


def get_qualifying_nations(world) -> List[str]:
    """Get all nations that qualify for coalition membership."""
    return [n for n in _get_all_nations(world) if qualifies_for_coalition(n, world)]


def get_nations_at_war_with_france(world) -> List[str]:
    """Get all non-vassal nations currently at war with France."""
    france = world.player_nation
    vassals = set(getattr(world, 'vassals', {}).keys())
    result = []
    for n in _get_all_nations(world):
        if n == france or n in vassals:
            continue
        if _get_diplo_state(world, france, n) == "WAR":
            result.append(n)
    return result


# ════════════════════════════════════════════════════════════════
# §4a. LEADER SELECTION
# ════════════════════════════════════════════════════════════════

def coalition_leadership_score(nation: str, world) -> int:
    """Calculate leadership score for a nation (§4a).

    Score = military//1000 + hostility + authority
    """
    france = world.player_nation
    military = sum(m.strength for m in world.marshals.values()
                   if m.nation == nation and m.strength > 0) // 1000
    hostility = abs(_get_relation(world, france, nation))
    authority = getattr(world, 'nation_authority', {}).get(nation, 60)
    return int(military + hostility + authority)


def select_coalition_leader(members: List[str], world) -> str:
    """Select coalition leader from members (§4a).

    Highest leadership score. Tiebreak: most marshals, then alphabetical.
    """
    if not members:
        return ""

    def _sort_key(nation):
        score = coalition_leadership_score(nation, world)
        marshal_count = sum(1 for m in world.marshals.values()
                           if m.nation == nation and m.strength > 0)
        # Negative for descending sort, nation for ascending alpha tiebreak
        return (-score, -marshal_count, nation)

    return sorted(members, key=_sort_key)[0]


# ════════════════════════════════════════════════════════════════
# §4c. STRATEGIC POSTURE
# ════════════════════════════════════════════════════════════════

def calculate_coalition_war_score(world) -> int:
    """Calculate weighted-average coalition war score (§4c).

    Weighted by each member's current army size.
    """
    coalition = world.active_coalition
    if not coalition:
        return 0

    france = world.player_nation
    members = coalition.get("members", [])
    total_weight = 0
    weighted_sum = 0

    for member in members:
        army_size = sum(m.strength for m in world.marshals.values()
                        if m.nation == member and m.strength > 0)
        from backend.game_logic.diplomacy import get_war_score_for
        france_ws = get_war_score_for(world, france, member)
        # Coalition wants NEGATIVE France scores (positive = coalition winning)
        weighted_sum += (-france_ws) * army_size
        total_weight += army_size

    if total_weight == 0:
        return 0

    return int(weighted_sum // total_weight)


def get_coalition_posture(world) -> str:
    """Determine coalition strategic posture (§4c).

    Returns: "aggressive", "defensive", or "cautious"
    """
    coalition = world.active_coalition
    if not coalition:
        return "defensive"

    coalition_ws = calculate_coalition_war_score(world)
    leader = coalition.get("leader", "")

    # Get leader personality from their diplomat
    leader_personality = _get_leader_personality(leader, world)

    # Leader personality overrides (§4c)
    if leader_personality in ("aggressive", "reckless"):
        # Aggressive leader: stays aggressive until war score < -20
        if coalition_ws >= -20:
            return "aggressive"
        else:
            return "cautious"
    elif leader_personality in ("cautious", "professional"):
        # Cautious leader: needs war score > +30 for aggressive
        if coalition_ws > 30:
            return "aggressive"
        elif coalition_ws >= -10:
            return "defensive"
        else:
            return "cautious"

    # Default thresholds
    if coalition_ws > 10:
        return "aggressive"
    elif coalition_ws >= -10:
        return "defensive"
    else:
        return "cautious"


def _get_leader_personality(nation: str, world) -> str:
    """Get the diplomatic personality of a nation's representative."""
    diplomats = getattr(world, 'diplomats', {})
    diplomat = diplomats.get(nation)
    if diplomat:
        return getattr(diplomat, 'personality', 'loyalist')
    return "loyalist"


# ════════════════════════════════════════════════════════════════
# §4e. BRITISH SUBSIDY
# ════════════════════════════════════════════════════════════════

def get_british_subsidy_recipient(world) -> Optional[str]:
    """Find the coalition partner to receive British subsidy (§4e).

    Lowest relation to Britain, minimum > -20, Britain gold > 500.
    Returns nation name or None.
    """
    coalition = world.active_coalition
    if not coalition:
        return None

    members = coalition.get("members", [])
    if "Britain" not in members:
        return None

    # Check Britain has enough gold
    britain_gold = world.nation_gold.get("Britain", 0)
    if britain_gold <= 500:
        return None

    # Find partner with lowest relation to Britain (min > -20)
    best = None
    best_relation = 200  # Higher than any possible relation

    for member in members:
        if member == "Britain":
            continue
        rel = _get_relation(world, "Britain", member)
        if rel > -20 and rel < best_relation:
            best = member
            best_relation = rel

    return best


def _process_british_subsidy(world) -> List[Dict]:
    """Process British subsidy payment (§4e). 200g/turn to lowest-relation partner."""
    events = []
    recipient = get_british_subsidy_recipient(world)
    if not recipient:
        return events

    subsidy = 200
    britain_gold = world.nation_gold.get("Britain", 0)
    if britain_gold < subsidy:
        return events

    world.nation_gold["Britain"] = int(britain_gold - subsidy)
    recipient_gold = world.nation_gold.get(recipient, 0)
    world.nation_gold[recipient] = int(recipient_gold + subsidy)

    # +5 relation between Britain and recipient
    world.modify_nation_relation("Britain", recipient, 5)

    events.append({
        "type": "british_subsidy",
        "recipient": recipient,
        "amount": int(subsidy),
        "message": f"Britain subsidizes {recipient} with {subsidy} gold.",
    })
    return events


# ════════════════════════════════════════════════════════════════
# §5b. CONVERGENCE BIAS
# ════════════════════════════════════════════════════════════════

def get_convergence_bias(posture: str) -> int:
    """Get convergence bias for P7 movement scoring (§5b).

    Returns score bonus for regions adjacent to French territory.
    """
    if posture == "aggressive":
        return 12
    elif posture == "defensive":
        return 4
    elif posture == "cautious":
        return 0
    return 8  # Default


# ════════════════════════════════════════════════════════════════
# §5c. HISTORICAL FRICTION
# ════════════════════════════════════════════════════════════════

def get_coalition_friction(nation_a: str, nation_b: str, world) -> float:
    """Get friction multiplier between coalition members (§5c).

    Returns 1.0 (full coordination) to 0.25 (near-hostile allies).
    Caller must int() the final result per Golden Rule #2.
    """
    if nation_a == nation_b:
        return 1.0

    mutual_relation = _get_relation(world, nation_a, nation_b)
    if mutual_relation >= 30:
        return 1.0
    elif mutual_relation >= 0:
        return 0.75
    elif mutual_relation >= -20:
        return 0.5
    else:
        return 0.25


# ════════════════════════════════════════════════════════════════
# §6a. COALITION LOYALTY PENALTY
# ════════════════════════════════════════════════════════════════

def get_coalition_loyalty_penalty(nation: str, world) -> int:
    """Get coalition loyalty penalty for acceptance formula (§6a).

    penalty = min(-15 + war_exhaustion // 10, 0)
    If target's relation with coalition leader < +10: halved (§6c wedge).

    Returns negative int (0 or less).
    """
    coalition = world.active_coalition
    if not coalition:
        return 0

    if nation not in coalition.get("members", []):
        return 0

    we = world.war_exhaustion.get(nation, 0)
    penalty = min(COALITION_LOYALTY_BASE + we // 10, 0)

    # §6c: Diplomatic wedge — halve penalty if target dislikes leader
    leader = coalition.get("leader", "")
    if leader and leader != nation:
        leader_relation = _get_relation(world, nation, leader)
        if leader_relation < 10:
            penalty = penalty // 2  # Halve (rounds toward zero)

    return int(penalty)


# ════════════════════════════════════════════════════════════════
# §6b. WAR EXHAUSTION FROM BATTLE
# ════════════════════════════════════════════════════════════════

def add_war_exhaustion_from_battle(nation: str, casualties: int, world) -> int:
    """Add war exhaustion from battle casualties (§10a).

    +casualties // 1000, capped at +20 per battle.
    Returns new war exhaustion for the nation.
    """
    we_gain = min(casualties // 1000, WAR_EXHAUSTION_BATTLE_CAP)
    if we_gain <= 0:
        return world.war_exhaustion.get(nation, 0)

    current = world.war_exhaustion.get(nation, 0)
    new_val = min(current + we_gain, WAR_EXHAUSTION_MAX)
    world.war_exhaustion[nation] = int(new_val)

    # S4: Dispatch when WE crosses thresholds
    _WE_THRESHOLDS = [20, 40, 60, 80]
    dispatched = world.we_dispatched_thresholds
    last_threshold = dispatched.get(nation, 0)
    for threshold in _WE_THRESHOLDS:
        if new_val >= threshold > current and threshold > last_threshold:
            from backend.game_logic.dispatch import queue_dispatch_event
            queue_dispatch_event(world, "diplomatic_we_threshold",
                                {"nation": nation, "we": int(new_val), "threshold": threshold},
                                "always")
            dispatched[nation] = threshold
            break

    return int(new_val)


def add_coalition_shock(defeated_nation: str, world) -> None:
    """Add +5 WE to other coalition members when one is defeated (§6b)."""
    coalition = world.active_coalition
    if not coalition:
        return

    if defeated_nation not in coalition.get("members", []):
        return

    for member in coalition["members"]:
        if member == defeated_nation:
            continue
        current = world.war_exhaustion.get(member, 0)
        world.war_exhaustion[member] = int(min(current + 5, WAR_EXHAUSTION_MAX))


# ════════════════════════════════════════════════════════════════
# §3e. COALITION FORMATION
# ════════════════════════════════════════════════════════════════

def form_coalition(qualifying_nations: List[str], world) -> Dict:
    """Form a coalition against France (§3e).

    qualifying_nations: Nations that meet §3b criteria (will declare war).
    Nations already at war join automatically.

    Returns dict with coalition info and events.
    """
    france = world.player_nation

    # 1. Identify all members
    already_at_war = get_nations_at_war_with_france(world)
    new_belligerents = [n for n in qualifying_nations if n not in already_at_war]
    all_members = list(set(already_at_war + qualifying_nations))

    # Must have at least 1 qualifying nation (not already at war)
    # AND at least 2 total members
    if not qualifying_nations or len(all_members) < 2:
        return {"success": False, "message": "Insufficient nations for coalition."}

    # 2. Apply war declarations for new belligerents (lazy import to avoid circular)
    from backend.game_logic.diplomacy import declare_war
    war_events = []
    for nation in new_belligerents:
        result = declare_war(world, nation, france)
        if result.get("success"):
            war_events.append(result)

    # Coalition wars don't add threat — declare_war only adds threat
    # when France is the aggressor, and here the coalition members declare.

    # EC-2: Void any in-transit proposal to a nation joining the coalition
    pit = getattr(world, 'proposal_in_transit', None)
    voided_proposal_nation = None
    if pit:
        pit_target = pit.get("target", "")
        if pit_target in all_members:
            voided_proposal_nation = pit_target
            world.proposal_in_transit = None
            # Restore Talleyrand if he was carrying this proposal
            if getattr(world, 'talleyrand_state', '') == "IN_TRANSIT":
                mission = getattr(world, 'active_diplomatic_mission', None)
                if mission and not mission.get("completed"):
                    world.talleyrand_state = "ON_MISSION"
                    mission["paused"] = False
                else:
                    world.talleyrand_state = "IDLE"
            # Refund DP spent on the voided proposal
            dp_cost = pit.get("proposal", {}).get("dp_cost", 0)
            if dp_cost > 0:
                world.diplomatic_points = getattr(world, 'diplomatic_points', 0) + int(dp_cost)

    # 3. United cause: +10 relation between all coalition members
    for i, m1 in enumerate(all_members):
        for m2 in all_members[i + 1:]:
            world.modify_nation_relation(m1, m2, 10)

    # 4. Select leader and determine posture
    leader = select_coalition_leader(all_members, world)
    world.coalition_count += 1

    # 5. Build coalition name (§3f)
    ordinal = _ORDINALS.get(world.coalition_count, f"{world.coalition_count}th")
    if world.coalition_count == 1:
        name = f"The {leader} Coalition"
    else:
        name = f"The {ordinal} {leader} Coalition"

    # 6. Set active coalition
    world.active_coalition = {
        "id": f"coalition_{world.current_turn}",
        "name": name,
        "leader": leader,
        "members": sorted(all_members),
        "formed_turn": int(world.current_turn),
        "strategic_posture": "defensive",  # Will be updated immediately
        "posture_last_updated": int(world.current_turn),
    }

    # Clear brewing state
    world.coalition_brewing = None

    # R51: Void pending diplomatic dialogue if target is a coalition member
    pending_dialogue = getattr(world, 'pending_diplomatic_dialogue', None)
    if pending_dialogue:
        dialogue_target = pending_dialogue.get("target_nation", "")
        if dialogue_target in all_members:
            world.pending_diplomatic_dialogue = None

    # V2-89: Also clear matching items from dialogue queue
    if hasattr(world, 'pending_dialogue_queue'):
        world.pending_dialogue_queue = [
            d for d in world.pending_dialogue_queue
            if d.get("target_nation", "") not in all_members
        ]

    # Update posture based on current war scores
    posture = get_coalition_posture(world)
    world.active_coalition["strategic_posture"] = posture
    world.active_coalition["posture_last_updated"] = int(world.current_turn)

    # 7. Calculate combined strength for popup
    combined_strength = sum(
        m.strength for m in world.marshals.values()
        if m.nation in all_members and m.strength > 0
    )

    # R84: Dismiss superseded TENSION/MURMURS notifications on coalition formation
    world.notifications.dismiss_by_type(COALITION_THREAT_TENSION)
    world.notifications.dismiss_by_type(COALITION_MURMURS)

    # 8. Notification
    world.notifications.add(create_notification(
        COALITION_DECLARED,
        NotificationPriority.CRITICAL,
        f"{name} Declared!",
        f"{name} has declared war. Leader: {leader}. "
        f"Members: {', '.join(sorted(all_members))}. "
        f"Combined strength: {int(combined_strength):,}.",
        int(world.current_turn),
        details={
            "coalition_name": name,
            "leader": leader,
            "members": sorted(all_members),
            "posture": posture,
            "combined_strength": int(combined_strength),
        },
    ))

    # 9. Log event
    world.log_event({
        "type": "coalition_declared",
        "coalition_name": name,
        "leader": leader,
        "members": sorted(all_members),
        "posture": posture,
        "threat_level": int(world.threat_level),
    })

    # R83: Dispatch event for coalition formation
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, "diplomatic_coalition_formed", {
        "member_list": ", ".join(sorted(all_members)),
    }, "always")

    # EC-2: Log voided proposal
    if voided_proposal_nation:
        world.log_event({
            "type": "proposal_voided_by_coalition",
            "target": voided_proposal_nation,
            "message": f"Envoy to {voided_proposal_nation} recalled — they joined the coalition.",
        })

    # 10. Set coalition popup on world state (Session 8C)
    member_details = []
    for m in sorted(all_members):
        m_strength = sum(
            marshal.strength for marshal in world.marshals.values()
            if marshal.nation == m and marshal.strength > 0
        )
        m_we = int(world.war_exhaustion.get(m, 0))
        member_details.append({
            "nation": m,
            "strength_display": f"{int(m_strength):,}",
            "war_exhaustion": int(m_we),
        })
    world.coalition_popup = {
        "coalition_name": name,
        "leader": leader,
        "posture": posture,
        "members": member_details,
        "combined_strength_display": f"{int(combined_strength):,}",
        "threat_level": int(world.threat_level),
    }

    result = {
        "success": True,
        "coalition_name": name,
        "leader": leader,
        "members": sorted(all_members),
        "posture": posture,
        "combined_strength": int(combined_strength),
        "new_belligerents": new_belligerents,
        "war_events": war_events,
        "coalition_popup": world.coalition_popup,
    }
    if voided_proposal_nation:
        result["voided_proposal"] = voided_proposal_nation
    return result


# ════════════════════════════════════════════════════════════════
# §7. DISSOLUTION
# ════════════════════════════════════════════════════════════════

def check_dissolution(world) -> Optional[str]:
    """Check if active coalition should dissolve (§7a).

    Returns dissolution reason string, or None if coalition persists.
    """
    coalition = world.active_coalition
    if not coalition:
        return None

    france = world.player_nation
    members = coalition.get("members", [])

    # Check: < 2 members
    active_members = [m for m in members if _get_diplo_state(world, france, m) == "WAR"]
    if len(active_members) < 2:
        return "insufficient_members"

    # Check: threat below 20
    if world.threat_level < DISSOLUTION_THREAT_THRESHOLD:
        return "low_threat"

    return None


def dissolve_coalition(world, reason: str) -> List[Dict]:
    """Dissolve the active coalition (§7b).

    Returns list of tactical events.
    """
    events = []
    coalition = world.active_coalition
    if not coalition:
        return events

    name = coalition.get("name", "The Coalition")

    # Clear coalition state
    world.active_coalition = None
    world.we_dispatched_thresholds = {}

    # R84: Dismiss superseded COALITION_DECLARED notification on dissolution
    world.notifications.dismiss_by_type(COALITION_DECLARED)

    # Start cooldown (§7c)
    world.coalition_cooldown = COALITION_COOLDOWN_TURNS

    # Notification
    world.notifications.add(create_notification(
        COALITION_DISSOLVED,
        NotificationPriority.NORMAL,
        "Coalition Dissolved",
        f"{name} has dissolved. {reason.replace('_', ' ').title()}.",
        int(world.current_turn),
    ))

    # Log event
    world.log_event({
        "type": "coalition_dissolved",
        "coalition_name": name,
        "reason": reason,
    })

    events.append({
        "type": "coalition_dissolved",
        "message": f"{name} has dissolved.",
        "reason": reason,
    })

    # R83: Dispatch event for coalition dissolution
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, "diplomatic_coalition_dissolved", {}, "always")

    return events


def remove_coalition_member(nation: str, world) -> List[Dict]:
    """Remove a nation from the active coalition (e.g., separate peace).

    Handles leader transition (§4b) and dissolution check.
    Returns list of tactical events.
    """
    events = []
    coalition = world.active_coalition
    if not coalition:
        return events

    members = coalition.get("members", [])
    if nation not in members:
        return events

    # Remove member
    members.remove(nation)
    coalition["members"] = members

    # Notification
    world.notifications.add(create_notification(
        COALITION_MEMBER_PEACED,
        NotificationPriority.NORMAL,
        f"{nation} Left Coalition",
        f"{nation} has signed a separate peace and left {coalition.get('name', 'the coalition')}.",
        int(world.current_turn),
    ))

    # §4b: -15 relation with remaining members ("betrayal")
    for member in members:
        world.modify_nation_relation(nation, member, -15)

    # Log event
    world.log_event({
        "type": "coalition_member_left",
        "nation": nation,
        "coalition_name": coalition.get("name", ""),
    })

    events.append({
        "type": "coalition_member_left",
        "message": f"{nation} has left the coalition.",
        "nation": nation,
    })

    # §4b: Leader transition
    if nation == coalition.get("leader") and members:
        new_leader = select_coalition_leader(members, world)
        coalition["leader"] = new_leader
        # New leader sets posture
        posture = get_coalition_posture(world)
        coalition["strategic_posture"] = posture
        coalition["posture_last_updated"] = int(world.current_turn)
        # -5 relation between remaining members ("alliance frays")
        for i, m1 in enumerate(members):
            for m2 in members[i + 1:]:
                world.modify_nation_relation(m1, m2, -5)
        events.append({
            "type": "coalition_leader_changed",
            "message": f"{new_leader} now leads the coalition.",
            "new_leader": new_leader,
        })

    # Check dissolution
    reason = check_dissolution(world)
    if reason:
        events.extend(dissolve_coalition(world, reason))

    return events


# ════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════

def is_coalition_member(nation: str, world) -> bool:
    """Check if a nation is in the active coalition."""
    coalition = world.active_coalition
    if not coalition:
        return False
    return nation in coalition.get("members", [])


def is_coalition_active(world) -> bool:
    """Check if any coalition is currently active."""
    return world.active_coalition is not None


def get_threat_tier(threat_level: int) -> str:
    """Get the threat tier name for a given threat level."""
    if threat_level >= THREAT_BREWING_MIN:
        return "Brewing"
    elif threat_level >= THREAT_MURMURS_MIN:
        return "Murmurs"
    elif threat_level >= THREAT_TENSION_MIN:
        return "Tension"
    else:
        return "Calm"


# ════════════════════════════════════════════════════════════════
# MASTER PER-TURN FUNCTION
# ════════════════════════════════════════════════════════════════

def process_coalition_turn(world) -> List[Dict]:
    """Master per-turn coalition processing (§3c processing order).

    Called from WorldState.advance_turn() after vassal processing,
    before income phase.

    Processing order:
    1. Passive threat from region control
    2. Threat decay
    3. War exhaustion per-turn changes
    4. British subsidy
    5. Cooldown decrement
    6. If brewing: decrement countdown, check cancel/expiry/instant
    7. If not brewing: check threshold (≥60 → brew, ≥80 → instant, ≥90 → override cooldown)
    8. Update posture if coalition active
    9. Dissolution check

    Returns list of tactical events.
    """
    events = []
    france = world.player_nation

    # ────────── 1. Passive threat from region control (§2a) ──────────
    france_regions = sum(1 for r in world.regions.values()
                        if r.controller == france)
    total_regions = len(world.regions)

    if total_regions > 0:
        control_pct = france_regions / total_regions
        if control_pct > 0.80:
            add_threat(world, 3, "region_control_80")
        elif control_pct > 0.70:
            add_threat(world, 2, "region_control_70")
        elif control_pct > 0.60:
            add_threat(world, 1, "region_control_60")

    # ────────── 2. Threat decay (§2b) ──────────
    decay = _calculate_threat_decay(world)
    if decay > 0:
        old_threat = world.threat_level
        world.threat_level = int(max(0, world.threat_level - decay))
        actual_decay = old_threat - world.threat_level
        if actual_decay > 0:
            world.threat_sources_this_turn.append({
                "source": "decay",
                "amount": int(-actual_decay),
            })

    # ────────── 3. War exhaustion per-turn (§10a) ──────────
    for nation in _get_all_nations(world):
        if nation == france:
            continue
        state = _get_diplo_state(world, france, nation)
        current_we = world.war_exhaustion.get(nation, 0)
        if state == "WAR":
            new_we = min(current_we + 8, WAR_EXHAUSTION_MAX)  # R11: was +5
        else:
            new_we = max(current_we - 5, 0)
        if new_we != current_we:
            world.war_exhaustion[nation] = int(new_we)

    # ────────── 3b. Coalition member relation friction (R11) ──────────
    if world.active_coalition:
        members = world.active_coalition.get("members", [])
        for i, member_a in enumerate(members):
            for member_b in members[i + 1:]:
                world.modify_nation_relation(member_a, member_b, -2)

    # ────────── 4. British subsidy (§4e) ──────────
    subsidy_events = _process_british_subsidy(world)
    events.extend(subsidy_events)

    # ────────── 5. Cooldown decrement (§7c) ──────────
    if world.coalition_cooldown > 0:
        world.coalition_cooldown -= 1
        if world.coalition_cooldown == 0:
            world.notifications.add(create_notification(
                COALITION_COOLDOWN_ENDED,
                NotificationPriority.NORMAL,
                "Coalition Cooldown Ended",
                "A new coalition may form if threat remains high.",
                int(world.current_turn),
            ))

    # ────────── 6. Brewing check (§3c) ──────────
    if world.coalition_brewing and not world.active_coalition:
        brewing = world.coalition_brewing
        qualifying = get_qualifying_nations(world)

        # Check cancellation (momentum rule §3c)
        if world.threat_level < BREWING_CANCEL_THRESHOLD or len(qualifying) == 0:
            world.coalition_brewing = None
            world.notifications.dismiss_by_type(COALITION_BREWING)
            events.append({
                "type": "coalition_brewing_cancelled",
                "message": "The coalition effort has collapsed.",
            })
            world.log_event({"type": "coalition_brewing_cancelled"})
        else:
            # Decrement countdown
            brewing["turns_remaining"] = brewing.get("turns_remaining", 1) - 1
            brewing["qualifying_nations"] = qualifying

            # Check instant override (§3d: threat ≥80 during brewing)
            if world.threat_level >= THREAT_INSTANT_MIN:
                result = form_coalition(qualifying, world)
                if result.get("success"):
                    events.append({
                        "type": "coalition_declared",
                        "message": f"{result['coalition_name']} declared! (Instant — threat {world.threat_level})",
                        "coalition": result,
                    })
            elif brewing["turns_remaining"] <= 0:
                # Countdown expired — declare
                result = form_coalition(qualifying, world)
                if result.get("success"):
                    events.append({
                        "type": "coalition_declared",
                        "message": f"{result['coalition_name']} declared!",
                        "coalition": result,
                    })
                else:
                    # Not enough nations — cancel
                    world.coalition_brewing = None
                    world.notifications.dismiss_by_type(COALITION_BREWING)
            else:
                # Update notification with remaining turns
                world.notifications.dismiss_by_type(COALITION_BREWING)
                world.notifications.add(create_notification(
                    COALITION_BREWING,
                    NotificationPriority.CRITICAL,
                    f"Coalition Brewing — {int(brewing['turns_remaining'])} turn(s)",
                    f"Nations consulting: {', '.join(qualifying)}. "
                    f"{int(brewing['turns_remaining'])} turns until declaration.",
                    int(world.current_turn),
                    details={
                        "qualifying_nations": qualifying,
                        "turns_remaining": int(brewing["turns_remaining"]),
                    },
                ))

    # ────────── 7. Threshold check (if not brewing, no active coalition) ──────────
    elif not world.active_coalition:
        threat = world.threat_level

        # §7c: Cooldown override at 90+
        if threat >= THREAT_OVERRIDE_COOLDOWN_MIN and world.coalition_cooldown > 0:
            world.coalition_cooldown = 0  # Override

        # Can only form if no cooldown
        if world.coalition_cooldown <= 0:
            qualifying = get_qualifying_nations(world)

            if threat >= THREAT_INSTANT_MIN and qualifying:
                # §3d: Instant declaration at 80+
                result = form_coalition(qualifying, world)
                if result.get("success"):
                    events.append({
                        "type": "coalition_declared",
                        "message": f"{result['coalition_name']} declared! (Instant — threat {threat})",
                        "coalition": result,
                    })
            elif threat >= THREAT_BREWING_MIN and qualifying:
                # §3c: Start brewing at 60+
                world.coalition_brewing = {
                    "qualifying_nations": qualifying,
                    "turns_remaining": BREWING_COUNTDOWN,
                    "started_turn": int(world.current_turn),
                    "threat_at_start": int(threat),
                }
                world.notifications.add(create_notification(
                    COALITION_BREWING,
                    NotificationPriority.CRITICAL,
                    f"Coalition Brewing — {BREWING_COUNTDOWN} turns",
                    f"A coalition is brewing against France. "
                    f"Nations consulting: {', '.join(qualifying)}. "
                    f"{BREWING_COUNTDOWN} turns until declaration.",
                    int(world.current_turn),
                    details={
                        "qualifying_nations": qualifying,
                        "turns_remaining": BREWING_COUNTDOWN,
                    },
                ))
                world.log_event({
                    "type": "coalition_brewing_started",
                    "qualifying_nations": qualifying,
                    "threat_level": int(threat),
                })
                events.append({
                    "type": "coalition_brewing_started",
                    "message": f"A coalition is brewing! {', '.join(qualifying)} are consulting.",
                    "qualifying_nations": qualifying,
                    "turns_remaining": BREWING_COUNTDOWN,
                })

                # R83: Dispatch event for coalition brewing
                from backend.game_logic.dispatch import queue_dispatch_event
                queue_dispatch_event(world, "diplomatic_coalition_brewing", {}, "always")

        # Threat tier notifications (regardless of cooldown)
        _check_threat_notifications(world)

    # ────────── 8. Update posture if coalition active (§4c) ──────────
    if world.active_coalition:
        posture = get_coalition_posture(world)
        world.active_coalition["strategic_posture"] = posture
        world.active_coalition["posture_last_updated"] = int(world.current_turn)

    # ────────── 9. Dissolution check (§7a) ──────────
    if world.active_coalition:
        reason = check_dissolution(world)
        if reason:
            events.extend(dissolve_coalition(world, reason))

    return events


def _check_threat_notifications(world) -> None:
    """Emit threat tier notifications when thresholds are crossed."""
    threat = world.threat_level

    if threat >= THREAT_MURMURS_MIN:
        # Dismiss tension, add murmurs (persistent until < 30)
        world.notifications.dismiss_by_type(COALITION_THREAT_TENSION)
        # Only add if not already present
        existing = [n for n in world.notifications.get_pending()
                    if n.get("type") == COALITION_MURMURS]
        if not existing:
            world.notifications.add(create_notification(
                COALITION_MURMURS,
                NotificationPriority.HIGH,
                "European Courts Concerned",
                f"Threat level: {int(threat)}. The courts of Europe grow restless.",
                int(world.current_turn),
            ))
    elif threat >= THREAT_TENSION_MIN:
        # Dismiss murmurs if threat dropped
        world.notifications.dismiss_by_type(COALITION_MURMURS)
        existing = [n for n in world.notifications.get_pending()
                    if n.get("type") == COALITION_THREAT_TENSION]
        if not existing:
            world.notifications.add(create_notification(
                COALITION_THREAT_TENSION,
                NotificationPriority.HIGH,
                "Diplomatic Tension",
                f"Threat level: {int(threat)}. The courts are uneasy.",
                int(world.current_turn),
            ))
    else:
        # Calm — dismiss all threat notifications
        world.notifications.dismiss_by_type(COALITION_THREAT_TENSION)
        world.notifications.dismiss_by_type(COALITION_MURMURS)
