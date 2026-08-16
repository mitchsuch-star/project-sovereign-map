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
# MC-1 (July 10, 2026 gate): the ten blessed 1805-roster abilities. A name here
# with no authored ability block stays inactive (MC-0 gates on a real name),
# so entries may land ahead of their JSON/mechanic slice.
_WIRED_ABILITY_MARSHALS = {
    # 1805 roster (MC-1)
    "Ney", "Davout", "Soult", "Lannes", "Murat", "Massena", "Bernadotte",
    "ArchdukeCharles", "Kutuzov", "Moore",
    # NP-V (NAPOLEON_SPEC §6.5): The Presence is REAL — the aura is
    # stamped by _calculate_coordination_context and read in
    # get_attack_modifier/get_defense_modifier — so his card must show
    # the ability as active, not greyed.
    "Napoleon",
    # Legacy Waterloo roster
    "Drouot", "Wellington", "Blucher", "Uxbridge",
}

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
    # NP-V (adversarial review, CONFIRMED across three lenses): the apex
    # card rendered NO personality line at all, because the sovereign had
    # no row here — the one card that should explain the game's most
    # unusual commander explained nothing. Every clause is a shipped
    # mechanic (NAPOLEON_SPEC §4.2/§5.1/§5.2/§6.2/§8).
    "sovereign": (
        "Sovereign: You, in the field. He never objects and never asks — "
        "his orders are your own will, and cost 1 AP, not 2. Where he "
        "stands, every corps of his nation fights +10% harder on attack "
        "and defence, and enemy commanders will not accept odds against "
        "him that they would take against any marshal. But victories won "
        "under his eye are HIS: marshals beside him earn half the glory, "
        "so ambition needs a command of its own. He holds no rank on the "
        "ladder, expects no reward, and cannot be replaced."
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

# MC-2 (July 10, 2026): what each displayed skill DOES, at its wired seam —
# shown = applied. Numbers derive from the live formulas: tactical -> combat
# dice (+1 per 3 pts, combat.py), shock -> damage multiplier 1 + skill/20,
# defense -> damage reduction skill/20, logistics -> muster score +5/pt
# (combat_executor._calculate_arrival_score), command -> The Rally tiers
# (marshal.py RALLY_FAST_COMMAND / RALLY_POOR_COMMAND). Administration is
# deliberately ABSENT until MC-2b wires it (gate Q3).
_SKILL_DESCRIPTIONS = {
    "tactical": "combat dice (+1 per 3 pts)",
    "shock": "attack damage (+5%/pt)",
    "defense": "damage resistance (-5%/pt)",
    "logistics": "answers the guns (+5 muster/pt)",
    "administration": "recruit pricing (thrifty 8+, wasteful 3-)",
    "command": "rally & recovery (fast 8+, poor 3-)",
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
        card = _build_marshal_card(marshal, world)
        # NP-3 (NAPOLEON_SPEC §6.5): the sovereign's card is the apex
        # variant — the .gd renders "THE EMPEROR" above the ladder, no
        # glory bar, no rank, no envy arrow, and the Reward chip becomes
        # the stated refusal. Flag follows the W6-7 captured idiom.
        if getattr(marshal, "is_sovereign", False):
            card["sovereign"] = True
            card["sovereign_note"] = "The Empire is his estate."
        # W6-7: a captured marshal's card names his fate front and center.
        if getattr(marshal, "captured_by", ""):
            card["captured"] = True
            card["captured_by"] = marshal.captured_by
            card["status"] = "captured"
            card["status_note"] = (
                f"PRISONER of {marshal.captured_by} since "
                f"T{int(marshal.captured_turn)}."
            )
        result.append(card)

    return result


def _build_marshal_card(marshal: Marshal, world) -> Dict[str, Any]:
    """Build a complete data card for one marshal."""
    return {
        # ═══════ IDENTITY CARD ═══════
        **_build_identity(marshal),

        # ═══════ SIGNATURE ABILITY ═══════
        **_build_ability(marshal),

        # ═══════ COMBAT STATS ═══════
        **_build_combat_stats(marshal, world),

        # ═══════ TRUST & STANDING ═══════
        **_build_trust_standing(marshal, world),

        # ═══════ ES-7 ESTATES & EXPECTATION (Economy Revisit S7) ═══════
        **_build_estates(marshal, world),

        # ═══════ JEALOUSY v3.2 — GLORY & GRIEVANCES (shown = applied) ═══════
        **_build_glory(marshal, world),

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


def _build_glory(marshal: Marshal, world) -> Dict[str, Any]:
    """Jealousy v3.2 card block — glory score, ladder rank, crown,
    grievance state, feuds, separations (jealousy.build_glory_card_fields
    is the single source; shown = applied)."""
    from backend.game_logic.jealousy import build_glory_card_fields
    return build_glory_card_fields(marshal, world)


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


def _build_combat_stats(marshal: Marshal, world=None) -> Dict[str, Any]:
    """Combat stats section."""
    # MC-2: The Rally tier + note, derived from the marshal's OWN methods and
    # constants (single source marshal.py — the card never re-implements the
    # thresholds; Godot renders these strings verbatim, Q3 pattern).
    if marshal.get_rally_stages_per_turn() >= 2:
        rally_tier = "fast"
        rally_note = (
            "The Rally: reforms beaten armies at double pace — "
            "retreat and broken recovery advance 2 stages/turn."
        )
    elif marshal.skills.get("command", 5) <= Marshal.RALLY_POOR_COMMAND:
        rally_tier = "poor"
        p = [int(round(marshal.get_retreat_stage_penalty(s) * 100))
             for s in (0, 1, 2)]
        rally_note = (
            f"The Rally: holds beaten armies together poorly — retreat "
            f"recovery runs -{p[0]}/-{p[1]}/-{p[2]}% effective."
        )
    else:
        rally_tier = "standard"
        rally_note = ""

    # MC-2b (July 11, 2026): administration is wired — The Intendance prices
    # the recruit seam, Europe-scoped (see marshal.get_recruit_cost_modifier).
    # The card row and its note display exactly where the mechanic is live
    # (shown = applied); in the legacy rollback world the row stays hidden,
    # the pre-MC-2b state (GR9: no advertised stat that does nothing).
    intendance_live = (
        getattr(world, "sovereign_map", "legacy") == "europe"
        if world is not None else False
    )
    admin_tier = "standard"
    admin_note = ""
    if intendance_live:
        swing = int(round(Marshal.INTENDANCE_COST_SWING * 100))
        mod = marshal.get_recruit_cost_modifier()
        if mod < 1.0:
            admin_tier = "thrifty"
            admin_note = (
                f"The Intendance: raises recruits {swing}% under "
                f"standard cost."
            )
        elif mod > 1.0:
            admin_tier = "wasteful"
            admin_note = (
                f"The Intendance: levies run {swing}% over cost "
                f"under his hand."
            )

    skill_notes = dict(_SKILL_DESCRIPTIONS)
    if not intendance_live:
        skill_notes.pop("administration", None)

    return {
        "strength": int(marshal.strength),
        "starting_strength": int(marshal.starting_strength),
        "morale": int(marshal.morale),
        "skills": {k: int(v) for k, v in marshal.skills.items()
                   if k != "administration" or intendance_live},
        # MC-2: per-skill mechanic hints for the card (wired seams only).
        "skill_notes": skill_notes,
        "rally_tier": rally_tier,
        "rally_note": rally_note,
        "admin_tier": admin_tier,
        "admin_note": admin_note,
        "tactical_skill": int(marshal.tactical_skill),
    }


def _build_trust_standing(marshal: Marshal, world) -> Dict[str, Any]:
    """Trust and standing section."""
    return {
        "trust_value": int(marshal.trust.value),
        "trust_label": marshal.trust.get_label(),
        "vindication_score": int(marshal.vindication_score),
        # Aug 2026 health-check audit: the tracker lives on the WORLD, not
        # the marshal — the old hasattr(marshal, ...) read was permanently
        # False. Same computation the map payload already uses.
        "has_pending_vindication": bool(
            world.vindication_tracker.has_pending(marshal.name)
        ),
        "orders_overridden": int(marshal.orders_overridden),
        "battles_won": int(marshal.battles_won),
        "battles_lost": int(marshal.battles_lost),
    }


def _build_estates(marshal: Marshal, world) -> Dict[str, Any]:
    """ES-7 estate/expectation section (Economy Revisit S7, spec §0.6.2 +
    §0.6.8 second pass).

    Expectation and estate income are in the same gold/turn units — the
    number IS the explanation, no opaque penalty. `eligible_estates` powers
    the card's Endow affordance; `reward_options` (§0.6.8 item 6) powers
    the Reward dialog's buttons — structured estate rows with incomes, the
    rente offer with its true treasury cost, and the Steward tier, so every
    option can explain its instrument. Empty/zero on the legacy fixture
    world (ES-7 is Europe-scoped).
    """
    from backend.game_logic.dotation import (
        build_rente_offer, compute_investiture_fee, derive_title,
        get_estate_income, get_expectation, get_rente_cost,
        estate_yield, get_satisfaction, is_dotation_world, is_eroding,
        list_eligible_estates,
    )

    if not is_dotation_world(world):
        return {
            "is_dotation_world": False,
            "expectation": 0,
            "estate_income": 0,
            "expectation_shortfall": 0,
            "is_eroding": False,
            "estate_regions": [],
            "estate_title": "",
            "eligible_estates": [],
            "pension": 0,
            "pension_cost": 0,
            "rente_offer": {"face": 0, "cost": 0},
            "investiture_fee": 0,
            "eligible_estate_details": [],
            "steward_tier": "",
            "steward_note": "",
        }

    expectation = get_expectation(marshal)
    satisfaction = get_satisfaction(marshal, world)
    estate_income = get_estate_income(marshal, world)
    shortfall = max(0, expectation - satisfaction)
    estates = list(marshal.dotation_regions)
    # Title derives from the FIRST (founding) estate — flavor only (GR6).
    title = derive_title(estates[0]) if estates else ""
    # W6-7 / review fix: a PRISONER cannot be rewarded — the grant executors
    # refuse him, so the card must offer no reward options (no rente offer,
    # no eligible estates, and the .gd side hides the [Reward…] link).
    is_captured = bool(getattr(marshal, "captured_by", ""))
    eligible = []
    details = []
    if shortfall > 0 and not is_captured:
        full = list_eligible_estates(world, marshal.nation)
        eligible = full[:4]
        for region_name in full[:5]:
            region = world.regions.get(region_name)
            if region is None:
                continue
            row_income = estate_yield(world, region_name)
            # XR-4 + review [4]: the two 0g causes carry DIFFERENT
            # recovery mechanisms and must not share a sentence — a
            # DISRUPTED estate pays nothing until the hostile army is
            # driven off (and its stability is FALLING −2/turn), while a
            # war-torn one recovers as stability grows.
            row_disrupted = region_name in world.get_disrupted_regions()
            details.append({
                "region": region_name,
                # CA8 sweep 4 review: `get_effective_income` carries the
                # stability term but NOT the EC-W1 disruption term, so a
                # province with a hostile army standing on it was priced at
                # its full 200g/turn on the button that endows it, and paid 0.
                # `estate_yield` is the same predicate the payer uses.
                "income": row_income,
                # XR-4 (Econ Balance EB-3): the pre-flight warning — a
                # 0g estate is a legal grant but the option must state the
                # true recovery mechanism BEFORE the player commits.
                "war_torn": bool(row_income <= 0 and not row_disrupted),
                "occupied": bool(row_income <= 0 and row_disrupted),
            })

    # The Steward (§0.6.8 item 2): decision-relevant BEFORE endowing —
    # land appreciates under an able lord, rots under a wasteful one.
    steward_bonus = int(marshal.get_estate_stability_bonus())
    if steward_bonus > 0:
        steward_tier = "prosperous"
        steward_note = (f"An able administrator — his estates gain "
                        f"+{steward_bonus} stability/turn and their revenues "
                        f"rise with them.")
    elif steward_bonus < 0:
        steward_tier = "wasteful"
        steward_note = (f"A wasteful lord — his estates recover "
                        f"{-steward_bonus} stability/turn slower; land "
                        f"placed in his hands appreciates poorly.")
    else:
        steward_tier = ""
        steward_note = ""

    pension = 0 if is_captured else int(getattr(marshal, "pension", 0))
    rente_offer = ({"face": 0, "cost": 0} if is_captured
                   else build_rente_offer(marshal, world))

    return {
        "is_dotation_world": True,
        "expectation": int(expectation),
        # §0.6.8: estates ONLY — the rente rides its own keys below, so the
        # card can show the portfolio, not a blended number.
        "estate_income": int(estate_income),
        "expectation_shortfall": int(shortfall),
        "is_eroding": bool(is_eroding(marshal, world)),
        "estate_regions": estates,
        "estate_title": title,
        "eligible_estates": eligible,
        "pension": pension,
        "pension_cost": int(get_rente_cost(pension)),
        "rente_offer": rente_offer,
        "investiture_fee": int(compute_investiture_fee(marshal)),
        "eligible_estate_details": details,
        "steward_tier": steward_tier,
        "steward_note": steward_note,
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
        # MC-1c Iron Resolve — derived bonus % ships with the count so the
        # card renders backend numbers (shown = applied; 0 for non-carriers)
        "iron_resolve_stacks": int(getattr(marshal, 'iron_resolve_stacks', 0)),
        "iron_resolve_bonus_pct": int(round(
            getattr(marshal, 'iron_resolve_stacks', 0)
            * Marshal.IRON_RESOLVE_BONUS_PER_STACK * 100)),
        "iron_resolve_max_stacks": int(Marshal.IRON_RESOLVE_MAX_STACKS),
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
    for other_name in list(marshal.relationships.keys()):
        # Filter: other marshal must exist in world.marshals AND be alive
        other = world.marshals.get(other_name)
        if other is None or other.strength <= 0:
            continue
        # A11 (CA9 row 3): read the DERIVED value, not the stored int.
        # A live grievance is a derived -1 toward its target that is never
        # written into the stored dict, so this card printed "Ney:
        # Professional" two lines under its own "GRIEVANCE: envious of
        # Ney" — the card contradicting the engine on the same screen,
        # while every mechanical seam (coordination, SUPPORT objections,
        # reinforcement, the muster preview) already reads the getter.
        value = int(marshal.get_relationship(other_name))
        relationships.append({
            "name": other_name,
            "value": value,
            "label": _RELATIONSHIP_LABELS.get(value, "Professional"),
        })
    return relationships
