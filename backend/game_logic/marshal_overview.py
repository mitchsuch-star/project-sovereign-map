"""
Marshal Overview — backend builder for Marshal Management UI (Phase 6.5)

Builds a list of player marshal dicts for the Godot Marshal Management screen.
All values int()-wrapped per CLAUDE.md rule: "All numbers to Godot: int()".
Player marshals only — enemy intel is on the Ledger's Intelligence tab.

Pattern follows ledger.py.
"""

from typing import Dict, Any, List

from backend.models.marshal import Marshal

# Relationship value → display label
_RELATIONSHIP_LABELS = {
    -2: "Hostile",
    -1: "Rival",
    0: "Professional",
    1: "Friendly",
    2: "Devoted",
}

# TODO (Phase 7b or Pre-EA): Replace hardcoded ability_active check with proper
# Marshal.ability_wired field. Currently derived from marshal name since the set
# of wired abilities is static (Ney, Drouot, Wellington, Blucher, Uxbridge).
_WIRED_ABILITY_MARSHALS = {"Ney", "Drouot", "Wellington", "Blucher", "Uxbridge"}


def build_marshal_overview(world) -> List[Dict[str, Any]]:
    """
    Build the marshal overview list for Godot rendering.

    Args:
        world: WorldState instance

    Returns:
        List of dicts, one per player marshal. All numeric values int()-wrapped.
    """
    player = world.player_nation
    result = []

    for marshal in world.marshals.values():
        if marshal.nation != player:
            continue
        result.append(_build_marshal_card(marshal, world))

    return result


def _build_marshal_card(marshal: Marshal, world) -> Dict[str, Any]:
    """Build a complete data card for one marshal."""
    return {
        # ═══════ IDENTITY CARD ═══════
        **_build_identity(marshal),

        # ═══════ SIGNATURE ABILITY ═══════
        **_build_ability(marshal),

        # ═══════ COMBAT STATS ═══════
        **_build_combat_stats(marshal),

        # ═══════ TRUST & STANDING ═══════
        **_build_trust_standing(marshal),

        # ═══════ CURRENT STATUS ═══════
        **_build_current_status(marshal),

        # ═══════ CAVALRY/ARTILLERY SPECIFICS ═══════
        **_build_unit_specifics(marshal),

        # ═══════ RELATIONSHIPS ═══════
        "relationships": _build_relationships(marshal, world),
    }


def _derive_unit_type(marshal: Marshal) -> str:
    """Derive display unit type from marshal flags."""
    if marshal.artillery:
        return "Artillery"
    if marshal.cavalry:
        return "Cavalry"
    return "Infantry"


def _build_identity(marshal: Marshal) -> Dict[str, Any]:
    """Identity card section."""
    return {
        "name": marshal.name,
        "nation": marshal.nation,
        "personality": marshal.personality,
        "unit_type": _derive_unit_type(marshal),
        "movement_range": int(marshal.movement_range),
        "biography": marshal.biography,
    }


def _build_ability(marshal: Marshal) -> Dict[str, Any]:
    """Signature ability section."""
    return {
        "ability_name": marshal.ability.get("name", "None"),
        "ability_description": marshal.ability.get("description", ""),
        "ability_trigger": marshal.ability.get("trigger", ""),
        "ability_effect": marshal.ability.get("effect", ""),
        "ability_active": marshal.name in _WIRED_ABILITY_MARSHALS,
    }


def _build_combat_stats(marshal: Marshal) -> Dict[str, Any]:
    """Combat stats section."""
    return {
        "strength": int(marshal.strength),
        "starting_strength": int(marshal.starting_strength),
        "morale": int(marshal.morale),
        "skills": {k: int(v) for k, v in marshal.skills.items()},
        "tactical_skill": int(marshal.tactical_skill),
    }


def _build_trust_standing(marshal: Marshal) -> Dict[str, Any]:
    """Trust and standing section."""
    return {
        "trust_value": int(marshal.trust.value),
        "trust_label": marshal.trust.get_label(),
        "vindication_score": int(marshal.vindication_score),
        "has_pending_vindication": bool(
            hasattr(marshal, 'vindication_tracker')
            and marshal.vindication_tracker is not None
        ),
        "orders_overridden": int(marshal.orders_overridden),
        "battles_won": int(marshal.battles_won),
        "battles_lost": int(marshal.battles_lost),
    }


def _build_current_status(marshal: Marshal) -> Dict[str, Any]:
    """Current status section."""
    # Strategic order
    strategic_order = None
    if marshal.strategic_order is not None:
        order = marshal.strategic_order
        strategic_order = {
            "command_type": order.command_type,
            "target": order.target,
        }

    return {
        "location": marshal.location,
        "stance": marshal.stance.value,
        "strategic_order": strategic_order,
        "is_fortified": bool(marshal.fortified),
        "defense_bonus": int(marshal.defense_bonus * 100),
        "is_drilling": bool(marshal.drilling or marshal.drilling_locked),
        "drilling_locked": bool(marshal.drilling_locked),
        "shock_bonus": int(marshal.shock_bonus),
        "is_retreating": bool(marshal.retreating),
        "retreat_recovery": int(marshal.retreat_recovery),
        "is_broken": bool(marshal.broken),
        "broken_recovery": int(marshal.broken_recovery),
        "idle_turns": int(marshal.idle_turns),
        "is_autonomous": bool(marshal.autonomous),
        "autonomy_reason": marshal.autonomy_reason,
    }


def _build_unit_specifics(marshal: Marshal) -> Dict[str, Any]:
    """Cavalry/Artillery specifics."""
    return {
        "cavalry": bool(marshal.cavalry),
        "counter_punch_available": bool(marshal.counter_punch_available),
        "counter_punch_turns": int(marshal.counter_punch_turns),
        "holding_position": bool(marshal.holding_position),
        "artillery": bool(marshal.artillery),
        "bombardments_this_turn": int(marshal.bombardments_this_turn),
        "moved_this_turn": bool(marshal.moved_this_turn),
    }


def _build_relationships(marshal: Marshal, world) -> List[Dict[str, Any]]:
    """Build relationship list, filtered to living marshals in world."""
    relationships = []
    for other_name, value in marshal.relationships.items():
        # Filter: other marshal must exist in world.marshals AND be alive
        other = world.marshals.get(other_name)
        if other is None or other.strength <= 0:
            continue
        relationships.append({
            "name": other_name,
            "value": int(value),
            "label": _RELATIONSHIP_LABELS.get(value, "Professional"),
        })
    return relationships
