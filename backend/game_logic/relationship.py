"""
Win/Loss Relationship Formula (Session 64).

After a shared battle with 2+ same-nation participants, each ordered pair
(A, B) rolls independently to check if A's opinion of B changes.

Key rules (from PHASE7_SPEC_AMENDMENTS):
- D4: Ordered pairs via itertools.permutations — 3 marshals = 6 calls.
       Cooldown is per-direction (A→B independent of B→A).
- M1: Hostile WIN max = 35, Devoted WIN max = 35 — NEVER reach threshold.
- M2: Threshold is strict > 50 (NOT >= 50). Hostile LOSS max = exactly 50.
"""

import random
from itertools import permutations


def calculate_battle_severity(winner_casualties, loser_casualties):
    """Decisive / standard / narrow based on casualty exchange ratio.

    ratio = winner_casualties / loser_casualties
    - ratio < 0.5  → decisive  (winner took much less)
    - 0.5 <= ratio <= 0.8 → standard
    - ratio > 0.8  → narrow   (nearly even)
    """
    if loser_casualties <= 0:
        return "decisive"
    ratio = winner_casualties / max(loser_casualties, 1)
    if ratio < 0.5:
        return "decisive"
    elif ratio > 0.8:
        return "narrow"
    else:
        return "standard"


def check_shared_battle_relationship(marshal_a, marshal_b, battle_result, won, world):
    """Check if shared battle changes A's relationship with B.

    Args:
        marshal_a: Marshal whose opinion may change.
        marshal_b: Marshal who A fought alongside.
        battle_result: Dict from resolve_battle().
        won: True if their side won the battle.
        world: WorldState (for current_turn / cooldown).

    Returns:
        int: Change applied (-1, 0, or +1).
    """
    current_rel = marshal_a.get_relationship(marshal_b.name)

    # Range check — can't improve above +2 or degrade below -2
    if won and current_rel >= 2:
        return 0
    if not won and current_rel <= -2:
        return 0

    # Cooldown check — per-direction (D4)
    last_turn = marshal_a.last_relationship_change_turn.get(marshal_b.name, -99)
    if world.current_turn - last_turn < 3:
        return 0

    # Determine winner/loser casualties for severity
    # Casualties are nested: battle_result["attacker"]["casualties"]
    # (both normal and deferred paths in combat.py use this structure)
    attacker_info = battle_result.get("attacker", {})
    defender_info = battle_result.get("defender", {})
    attacker_cas = attacker_info.get("casualties", 0) if isinstance(attacker_info, dict) else 0
    defender_cas = defender_info.get("casualties", 0) if isinstance(defender_info, dict) else 0

    # victor is a string (marshal name) or None
    victor = battle_result.get("victor")
    attacker_name = attacker_info.get("name") if isinstance(attacker_info, dict) else None

    # Assign winner/loser casualties based on who won
    if victor and attacker_name and victor != attacker_name:
        # Defender won
        winner_cas, loser_cas = defender_cas, attacker_cas
    else:
        # Attacker won (or stalemate — attacker cas as "winner" for ratio)
        winner_cas, loser_cas = attacker_cas, defender_cas

    severity = calculate_battle_severity(winner_cas, loser_cas)

    # WIN formula: base 30
    # LOSS formula: base 15
    if won:
        base = 30
        sev_bonus = {"decisive": 15, "standard": 0, "narrow": -10}[severity]
        rel_mod = {-2: -20, -1: 0, 0: 0, 1: -10, 2: -20}[current_rel]
    else:
        base = 15
        sev_bonus = {"decisive": 10, "standard": 0, "narrow": -5}[severity]
        rel_mod = {-2: 15, -1: 5, 0: 0, 1: 0, 2: 0}[current_rel]

    variance = random.randint(-10, 10)
    score = base + sev_bonus + rel_mod + variance

    # Threshold: strict > 50 (NOT >= 50) — M2
    if score > 50:
        change = 1 if won else -1
        marshal_a.modify_relationship(marshal_b.name, change)
        marshal_a.last_relationship_change_turn[marshal_b.name] = world.current_turn
        return change

    return 0


def get_battle_participants(primary, battle_region, nation, world):
    """Get all participating same-nation marshals in battle region.

    Includes:
    - The primary combatant (always, even if destroyed)
    - Same-nation allies in region who are alive and not broken/retreating

    Excludes:
    - Hostile marshals without a SUPPORT order targeting primary (Non-Participating)
    """
    participants = [primary]

    for m in world.marshals.values():
        if m.name == primary.name:
            continue
        if m.location != battle_region or m.nation != nation:
            continue
        if m.strength <= 0:
            continue
        if getattr(m, 'broken', False):
            continue
        if getattr(m, 'retreated_this_turn', False):
            continue
        if getattr(m, 'retreat_recovery', 0) > 0:
            continue

        # Hostile without SUPPORT = Non-Participating (spec D4/A-D4)
        rel = m.get_relationship(primary.name)
        if rel == -2:
            order = getattr(m, 'strategic_order', None)
            has_support = (
                order is not None
                and getattr(order, 'command_type', None) == "SUPPORT"
                and getattr(order, 'target', None) == primary.name
            )
            if not has_support:
                continue

        participants.append(m)

    return participants


def process_battle_relationships(attacker_marshal, defender_marshal, battle_result,
                                 battle_region, world,
                                 attacker_artillery=None, defender_artillery=None):
    """Process relationship changes for all participants on both sides.

    Uses ordered pairs (permutations) per D4.

    Args:
        attacker_artillery: List of artillery marshals that reinforced from adjacent regions
        defender_artillery: List of artillery marshals that reinforced from adjacent regions

    Returns:
        list of dicts with keys: marshal, toward, change, new_value, nation
    """
    changes = []

    victor = battle_result.get("victor")
    attacker_won = (victor == attacker_marshal.name)
    defender_won = (victor == defender_marshal.name)

    # Attacker side
    attacker_participants = get_battle_participants(
        attacker_marshal, battle_region, attacker_marshal.nation, world)
    # [7B-1] Include artillery that reinforced from adjacent regions
    if attacker_artillery:
        for art in attacker_artillery:
            if art not in attacker_participants:
                attacker_participants.append(art)

    if len(attacker_participants) >= 2:
        for a, b in permutations(attacker_participants, 2):
            # A8 (CA9 row 3): capture the STORED value across the call.
            # `Marshal.modify_relationship` reads the DERIVED value and
            # writes stored, so for a pair carrying a live grievance a `+1`
            # computes new = (stored - 1) + 1 = stored, writes stored, and
            # still RETURNS +1. The change was reported and never landed —
            # and Berthier congratulated the player on a thaw on the very
            # battle where the grievance penalty applied.
            _stored_before = a.relationships.get(b.name, 0)
            change = check_shared_battle_relationship(
                a, b, battle_result, attacker_won, world)
            if change != 0:
                direction = "improved" if change > 0 else "degraded"
                label = a.get_relationship_label(a.get_relationship(b.name))
                changes.append({
                    "marshal": a.name,
                    "toward": b.name,
                    "change": change,
                    "new_value": a.get_relationship(b.name),
                    "new_label": label,
                    "direction": direction,
                    "nation": a.nation,
                    # Did anything a mechanic can read actually move?
                    # Consumers that narrate a THAW must check this. Fixed
                    # here rather than at the writer per the Q5 ruling (c):
                    # repairing `modify_relationship` was MEASURED to
                    # diverge BASELINE_SERIES at index 20.
                    "stored_moved": a.relationships.get(b.name, 0) != _stored_before,
                })

    # Defender side
    defender_participants = get_battle_participants(
        defender_marshal, battle_region, defender_marshal.nation, world)
    # [7B-1] Include artillery that reinforced from adjacent regions
    if defender_artillery:
        for art in defender_artillery:
            if art not in defender_participants:
                defender_participants.append(art)

    if len(defender_participants) >= 2:
        for a, b in permutations(defender_participants, 2):
            # A8 (CA9 row 3): capture the STORED value across the call.
            # `Marshal.modify_relationship` reads the DERIVED value and
            # writes stored, so for a pair carrying a live grievance a `+1`
            # computes new = (stored - 1) + 1 = stored, writes stored, and
            # still RETURNS +1. The change was reported and never landed —
            # and Berthier congratulated the player on a thaw on the very
            # battle where the grievance penalty applied.
            _stored_before = a.relationships.get(b.name, 0)
            change = check_shared_battle_relationship(
                a, b, battle_result, defender_won, world)
            if change != 0:
                direction = "improved" if change > 0 else "degraded"
                label = a.get_relationship_label(a.get_relationship(b.name))
                changes.append({
                    "marshal": a.name,
                    "toward": b.name,
                    "change": change,
                    "new_value": a.get_relationship(b.name),
                    "new_label": label,
                    "direction": direction,
                    "nation": a.nation,
                    # Did anything a mechanic can read actually move?
                    # Consumers that narrate a THAW must check this. Fixed
                    # here rather than at the writer per the Q5 ruling (c):
                    # repairing `modify_relationship` was MEASURED to
                    # diverge BASELINE_SERIES at index 20.
                    "stored_moved": a.relationships.get(b.name, 0) != _stored_before,
                })

    return changes
