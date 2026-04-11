"""Helpers for mailbox proposal popup payloads.

Keeps the popup shape in one place so queued mailbox items can carry
their own payload instead of relying on a single global popup cache.
"""

from typing import Dict, Optional, Tuple


def build_proposal_popup_clauses(terms: Dict, *, include_base: bool = True) -> list[str]:
    """Build incoming_proposal_popup.gd-compatible clause strings."""
    from backend.display_names import PROPOSAL_TYPE_DISPLAY

    clause_type_display = {
        "gold_lump": "Gold payment",
        "gold_per_turn": "Gold per turn",
        "territory_cede": "Territory cession",
        "territory_return": "Territory return",
        "action_point": "Action point concession",
        "unit_trade": "Military units",
    }

    clauses = []
    proposal_type_key = terms.get("type", "unknown")
    if include_base:
        base_label = PROPOSAL_TYPE_DISPLAY.get(
            proposal_type_key, proposal_type_key.replace("_", " ").title()
        )
        clauses.append(f"Proposal: {base_label}")

    for demand in terms.get("demands", []):
        dtype = demand.get("type", "unknown")
        label = clause_type_display.get(dtype, dtype.replace("_", " ").title())
        clauses.append(f"Demand: {label} - {demand.get('value', '')}")

    for sweetener in terms.get("sweeteners", []):
        stype = sweetener.get("type", "unknown")
        label = clause_type_display.get(stype, stype.replace("_", " ").title())
        clauses.append(f"Offer: {label} - {sweetener.get('value', '')}")

    if not clauses:
        clauses.append("Diplomatic proposal")

    return clauses


def build_acceptance_hints(acceptance: Dict) -> Tuple[str, str]:
    """Translate acceptance components into Godot-friendly hint strings."""
    from backend.display_names import FEEDBACK_STRINGS

    components = acceptance.get("components", {})
    factors = sorted(
        [{"reason": key, "value": value} for key, value in components.items() if value != 0],
        key=lambda factor: abs(factor.get("value", 0)),
        reverse=True,
    )
    positive_factors = [factor for factor in factors if factor.get("value", 0) > 0]
    negative_factors = [factor for factor in factors if factor.get("value", 0) < 0]

    if positive_factors:
        best_key = positive_factors[0].get("reason", "")
        acceptance_hint = FEEDBACK_STRINGS.get(best_key, {}).get(
            "positive", "complex diplomatic factors"
        )
    else:
        acceptance_hint = "No strong positives identified"

    if negative_factors:
        worst_key = negative_factors[0].get("reason", "")
        rejection_hint = FEEDBACK_STRINGS.get(worst_key, {}).get(
            "negative", "complex diplomatic factors"
        )
    else:
        rejection_hint = "No major obstacles identified"

    return acceptance_hint, rejection_hint


def build_pending_envoy_popup_from_terms(
    world,
    *,
    nation: str,
    terms: Dict,
    assessment: str = "",
    is_counter_offer: bool = False,
    acceptance: Optional[Dict] = None,
    acceptance_score: Optional[int] = None,
) -> Dict:
    """Build the popup payload shape incoming_proposal_popup.gd expects."""
    from backend.display_names import PERSONALITY_DISPLAY

    diplomats = getattr(world, "diplomats", {})
    diplomat = diplomats.get(nation)
    diplomat_name = diplomat.name if diplomat else f"the {nation} ambassador"
    personality_raw = (
        diplomat.personality.value if diplomat and hasattr(diplomat.personality, "value")
        else str(diplomat.personality) if diplomat
        else "balanced"
    )

    if acceptance is not None:
        acceptance_hint, rejection_hint = build_acceptance_hints(acceptance)
    elif acceptance_score is not None:
        acceptance_hint = f"Acceptance score: {int(acceptance_score)}%"
        rejection_hint = ""
    else:
        acceptance_hint = ""
        rejection_hint = ""

    return {
        "from_nation": nation,
        "diplomat_name": diplomat_name,
        "diplomat_personality": PERSONALITY_DISPLAY.get(personality_raw, personality_raw),
        "proposal_type": terms.get("type", "unknown"),
        "clauses": build_proposal_popup_clauses(
            terms, include_base=not is_counter_offer
        ),
        "talleyrand_assessment": assessment or "Talleyrand has no assessment.",
        "acceptance_hint": acceptance_hint,
        "rejection_hint": rejection_hint,
        "is_counter_offer": bool(is_counter_offer),
    }
