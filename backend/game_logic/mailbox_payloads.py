"""Helpers for mailbox proposal popup payloads.

Keeps the popup shape in one place so queued mailbox items can carry
their own payload instead of relying on a single global popup cache.
"""
import copy

from typing import Dict, Optional, Tuple


_PEACE_PROPOSAL_TYPES = {"peace", "armistice", "armistice_losing", "armistice_winning"}


def build_proposal_popup_clauses(terms: Dict, *, include_base: bool = True) -> list[str]:
    """Build incoming_proposal_popup.gd-compatible clause strings."""
    from backend.display_names import build_proposal_popup_clauses as _build

    return _build(terms, include_base=include_base)


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
    decision_reason: str = "",
) -> Dict:
    """Build the popup payload shape incoming_proposal_popup.gd expects."""
    from backend.display_names import (
        PERSONALITY_DISPLAY,
        diplomatic_decision_reason_display,
        proposal_display_name,
    )

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

    # W6-10 (E-CA-6): the diplomat SPEAKS the proposal and its motive in
    # his Voice Bible register — the decision_reason rendered in-character,
    # not as a tag. Deterministic bank (GR6); resolves through
    # resolve_named_diplomat per the Voice Bible rule.
    from backend.game_logic.diplomatic_templates import (
        compose_incoming_diplomat_line,
    )
    diplomat_line = compose_incoming_diplomat_line(
        world,
        nation=nation,
        proposal_type=terms.get("type", "unknown"),
        decision_reason=decision_reason,
    )

    payload = {
        "from_nation": nation,
        "diplomat_name": diplomat_name,
        "diplomat_personality": PERSONALITY_DISPLAY.get(personality_raw, personality_raw),
        "proposal_type": terms.get("type", "unknown"),
        "proposal_type_display": proposal_display_name(terms.get("type", "unknown")),
        "clauses": build_proposal_popup_clauses(
            terms, include_base=not is_counter_offer
        ),
        "talleyrand_assessment": assessment or "Talleyrand has no assessment.",
        "acceptance_hint": acceptance_hint,
        "rejection_hint": rejection_hint,
        "is_counter_offer": bool(is_counter_offer),
        "decision_reason": decision_reason,
        "decision_reason_display": diplomatic_decision_reason_display(decision_reason),
        "diplomat_line": diplomat_line,
    }

    proposal_type = terms.get("type", "unknown")
    if proposal_type in _PEACE_PROPOSAL_TYPES:
        player_nation = getattr(world, "player_nation", "France")
        preview_terms = _orient_incoming_terms_for_player(terms, player_nation, nation)
        try:
            from backend.game_logic.diplomacy import build_war_context_snapshot
            snapshot = build_war_context_snapshot(
                world,
                player_nation,
                nation,
                proposal_type,
                terms=preview_terms,
            )
            payload["war_context_snapshot"] = snapshot
            payload["annotated_terms"] = snapshot.get("annotated_terms", [])
            payload["fallout_warnings"] = snapshot.get("fallout_warnings", [])
            payload["commitment_conflicts"] = snapshot.get("commitment_conflicts", [])
        except Exception:
            payload["annotated_terms"] = []

    return payload


def _orient_incoming_terms_for_player(terms: Dict, player_nation: str, source_nation: str) -> Dict:
    """Return incoming AI terms in France-to-source form for player previews."""
    oriented = copy.deepcopy(terms)
    proposer = terms.get("proposer_nation") or terms.get("proposer") or source_nation
    target = terms.get("target_nation") or terms.get("target") or player_nation
    if proposer != player_nation and target == player_nation:
        oriented["sweeteners"] = copy.deepcopy(terms.get("demands", []))
        oriented["demands"] = copy.deepcopy(terms.get("sweeteners", []))
    oriented["proposer_nation"] = player_nation
    oriented["target_nation"] = source_nation
    return oriented
