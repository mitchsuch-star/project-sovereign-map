"""
Marshal Overview — backend builder for Marshal Management UI (Phase 6.5)

Builds a list of player marshal dicts for the Godot Marshal Management screen.
All values int()-wrapped per CLAUDE.md rule: "All numbers to Godot: int()".
Player marshals only — enemy intel is on the Ledger's Intelligence tab.

Pattern follows ledger.py.
"""

from typing import Dict, Any, List

from backend.models.marshal import Marshal
from backend.display_names import PERSONALITY_DISPLAY, STANCE_DISPLAY

# Relationship value → display label
_RELATIONSHIP_LABELS = {
    -2: "Hostile",
    -1: "Rival",
    0: "Professional",
    1: "Friendly",
    2: "Devoted",
}

# Marshals whose unique abilities are actively wired (mechanically functional).
# When adding a new wired ability, add the marshal name here AND follow the full
# checklist in docs/ADDING_CONTENT.md → "Wiring a Special Ability" section.
_WIRED_ABILITY_MARSHALS = {"Ney", "Davout", "Drouot", "Wellington", "Blucher", "Uxbridge"}

# Gameplay descriptions for each personality type
_PERSONALITY_DESCRIPTIONS = {
    "aggressive": (
        "Aggressive: +15% attack, +5% more in aggressive stance. "
        "Fortify capped at 10%. Grows restless if idle too long."
    ),
    "cautious": (
        "Cautious: +20% defense in defensive stance, +10% when outnumbered. "
        "Fortify up to 20%. Hesitant to attack at bad odds."
    ),
    "literal": (
        # W6-5 The Literal Doctrine (§7.1) — the doctrine, stated on the card.
        "Literal: Executes orders to the letter — no improvisation, no "
        "initiative, no objection. Cheaper to command (strategic orders "
        "cost 1 AP, not 2), immovable on the defense (+15% when holding), "
        "and utterly predictable. He will never march to the sound of the "
        "guns without your written word ('support X' authorizes him)."
    ),
}

# Gameplay descriptions for each unit type
_UNIT_TYPE_DESCRIPTIONS = {
    "Infantry": (
        "Infantry: Standard movement range of 1. Reliable in all terrain. "
        "No special restrictions."
    ),
    "Cavalry": (
        "Cavalry: Movement range of 2 — can strike deep. "
        "Fortify bonus decays after 3 turns. Recklessness builds when attacking repeatedly."
    ),
    "Artillery": (
        "Artillery: Can bombard adjacent regions without entering battle (2 per turn). "
        "Cannot attack after moving. Does not advance into enemy territory on victory."
    ),
}


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

        # ═══════ ES-7 ESTATES & EXPECTATION (Economy Revisit S7) ═══════
        **_build_estates(marshal, world),

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
    unit_type = _derive_unit_type(marshal)
    return {
        "name": marshal.name,
        "nation": marshal.nation,
        "personality": PERSONALITY_DISPLAY.get(marshal.personality, marshal.personality.capitalize()),
        "personality_description": _PERSONALITY_DESCRIPTIONS.get(
            marshal.personality, ""
        ),
        "unit_type": unit_type,
        "unit_type_description": _UNIT_TYPE_DESCRIPTIONS.get(unit_type, ""),
        "movement_range": int(marshal.movement_range),
        "biography": marshal.biography,
    }


def _build_ability(marshal: Marshal) -> Dict[str, Any]:
    """Signature ability section. Only includes ability data for wired abilities."""
    ability = marshal.ability or {}
    ability_name = ability.get("name") or ""
    # MC-0: gate on a REAL ability, not just the marshal's name. Scenario
    # marshals boot with ability {"name": "None"} (create_marshal_from_data),
    # so 1805 Ney/Davout are in _WIRED_ABILITY_MARSHALS but carry no ability —
    # they must NOT report an active ability literally named "None". (The
    # underlying combat wiring keys off the ability name too, so False here
    # matches the mechanics: no name -> no effect.)
    is_active = (marshal.name in _WIRED_ABILITY_MARSHALS
                 and ability_name not in ("", "None"))
    if is_active:
        return {
            "ability_name": ability_name,
            "ability_description": ability.get("description", ""),
            "ability_trigger": ability.get("trigger", ""),
            "ability_effect": ability.get("effect", ""),
            "ability_active": True,
        }
    # No active ability — omit ability fields entirely
    return {
        "ability_name": "",
        "ability_description": "",
        "ability_trigger": "",
        "ability_effect": "",
        "ability_active": False,
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


def _build_estates(marshal: Marshal, world) -> Dict[str, Any]:
    """ES-7 estate/expectation section (Economy Revisit S7, spec §0.6.2).

    Expectation and estate income are in the same gold/turn units — the
    number IS the explanation, no opaque penalty. `eligible_estates` powers
    the card's Endow affordance (the typed command is the input surface;
    the card names the exact provinces so the player never guesses).
    Empty/zero on the legacy fixture world (ES-7 is Europe-scoped).
    """
    from backend.game_logic.dotation import (
        derive_title, get_expectation, get_satisfaction, is_dotation_world,
        is_eroding, list_eligible_estates,
    )

    if not is_dotation_world(world):
        return {
            "expectation": 0,
            "estate_income": 0,
            "expectation_shortfall": 0,
            "is_eroding": False,
            "estate_regions": [],
            "estate_title": "",
            "eligible_estates": [],
        }

    expectation = get_expectation(marshal)
    satisfaction = get_satisfaction(marshal, world)
    shortfall = max(0, expectation - satisfaction)
    estates = list(marshal.dotation_regions)
    # Title derives from the FIRST (founding) estate — flavor only (GR6).
    title = derive_title(estates[0]) if estates else ""
    eligible = []
    if shortfall > 0:
        eligible = list_eligible_estates(world, marshal.nation)[:4]

    return {
        "expectation": int(expectation),
        "estate_income": int(satisfaction),
        "expectation_shortfall": int(shortfall),
        "is_eroding": bool(is_eroding(marshal, world)),
        "estate_regions": estates,
        "estate_title": title,
        "eligible_estates": eligible,
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
        "stance": STANCE_DISPLAY.get(marshal.stance.value, marshal.stance.value.capitalize()),
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
        "square_formation": bool(marshal.square_formation),
    }


def _build_unit_specifics(marshal: Marshal) -> Dict[str, Any]:
    """Cavalry/Artillery specifics."""
    return {
        "cavalry": bool(marshal.cavalry),
        "counter_punch_available": bool(marshal.counter_punch_available),
        "counter_punch_turns": int(marshal.counter_punch_turns),
        "counter_punch_ready": bool(marshal.counter_punch_ready),
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
