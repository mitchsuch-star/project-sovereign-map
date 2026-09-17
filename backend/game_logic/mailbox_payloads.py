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


def terms_are_a_client_petition(terms: Optional[Dict]) -> bool:
    """IQ-7: True when a terms dict is a client petition (a loyal satellite
    asking its lord for a province or for relief from tribute).

    Keyed on the terms TYPE, which for this family is the stable P-rule
    label itself (`vassal.CLIENT_PETITION_TYPE`) — a petition's type is never
    rewritten downstream the way `harsh_peace` → `peace` is. The dialogue-
    level predicate is `vassal.is_client_petition`; this is its terms-level
    sibling for the surfaces that hold terms and no dialogue.
    """
    if not isinstance(terms, dict):
        return False
    from backend.game_logic.vassal import CLIENT_PETITION_TYPE

    return terms.get("type") == CLIENT_PETITION_TYPE


def client_petition_clauses(terms: Dict) -> list[str]:
    """IQ-7: the clause lines of a client petition — the ONE list the popup,
    the mailbox row and the typed terminal all render.

    Every line comes from `vassal.petition_terms` (the single source for what
    the petition shows and applies): the design note first when the province
    belongs to the satellite's own authored design, then the grant line, the
    refuse line and the lapse rule. No acceptance formula applies (France
    decides), so no hint line is composed here. Falls back to the generic
    clause builder only if the petition carries no lines at all.
    """
    petition = terms.get("petition") if isinstance(terms, dict) else None
    petition = petition if isinstance(petition, dict) else {}
    lines = [
        str(petition.get(key) or "").strip()
        for key in ("design_note", "grant_line", "refuse_line", "lapse_line")
    ]
    lines = [line for line in lines if line]
    if lines:
        return lines
    return build_proposal_popup_clauses(terms)


def client_petition_assessment(terms: Dict) -> str:
    """IQ-7: Talleyrand's one line on a client petition, in his register.

    The PRICES live in the clauses (`client_petition_clauses`), so his line
    speaks to what the petition MEANS — a client that asks still counts
    itself ours, and the standing it spends to ask does not come back on a
    refusal. Deterministic, display-only (GR6).
    """
    petition = terms.get("petition") if isinstance(terms, dict) else None
    petition = petition if isinstance(petition, dict) else {}
    if str(petition.get("subject") or "") == "province":
        return (
            "Talleyrand: \"A client that asks for land still counts itself "
            "ours, Sire. Grant it and the bond deepens; refuse it and the "
            "standing it spent to ask does not return.\""
        )
    return (
        "Talleyrand: \"A client that asks for relief is naming its own drift, "
        "Sire, while it still has the standing to ask. Grant it and the bond "
        "deepens; refuse it and that standing is spent.\""
    )


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

    # IQ-7 "The Client's Petition": its own register on the popup. The
    # clauses are the petition's own lines (grant / refuse / lapse / design
    # note, from `vassal.petition_terms`), Talleyrand speaks to the meaning
    # rather than repeating the prices, and the acceptance hints are
    # SUPPRESSED — France decides, no acceptance formula applies, and the
    # W6-10 diplomat line (composed for treaty asks) would voice a treaty
    # motive the petition does not carry. `is_petition` is what
    # incoming_proposal_popup.gd branches on (Counter hidden, the petition
    # header) — the same shape `is_ultimatum` takes.
    if terms_are_a_client_petition(terms):
        payload["is_petition"] = True
        payload["clauses"] = client_petition_clauses(terms)
        payload["talleyrand_assessment"] = (
            assessment or client_petition_assessment(terms))
        payload["acceptance_hint"] = ""
        payload["rejection_hint"] = ""
        payload["diplomat_line"] = ""
        # A vassal without a diplomat record would fall back to
        # "the {tag} ambassador" above — the raw tag, which R7 forbids.
        if diplomat is None:
            from backend.game_logic.formations import formed_display_name
            payload["diplomat_name"] = (
                f"the envoy of {formed_display_name(world, nation)}")
        return payload

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
            # FA-N43 (slice 10): the popup's "Assessment" line.
            #
            # `build_war_context_snapshot`'s `harshness` is, by its OUTGOING
            # definition, the burden on the ENEMY — what the other side is
            # asked to bear. The mirror terms above preserve that definition,
            # which is why the fallout warnings that consume the same number
            # are right today and must not move. But the popup prints it as
            # "Assessment", which a player reads as the burden on FRANCE —
            # so an AI demand for 405 gold rendered GENEROUS and an AI gift
            # of 300 gold a turn rendered HARSH.
            #
            # Two different questions, two numbers. The label is recomputed
            # here, on the UN-oriented demands, and nothing else moves.
            if INCOMING_ASSESSMENT_READS_OUR_BURDEN:
                from backend.game_logic.diplomacy import get_harshness_label
                from backend.game_logic.diplomatic_templates import (
                    calculate_treaty_harshness,
                )
                _our_burden = calculate_treaty_harshness({
                    "clauses": [],
                    "demands": list(terms.get("demands") or []),
                })
                snapshot["harshness"] = round(_our_burden, 2)
                snapshot["harshness_label"] = get_harshness_label(_our_burden)
                payload["harshness"] = snapshot["harshness"]
                payload["harshness_label"] = snapshot["harshness_label"]
        except Exception:
            payload["annotated_terms"] = []

    return payload


# FA-N43 (slice 10) flip lever: False restores the pre-slice-10 reading, in
# which the incoming popup's Assessment quoted the burden on the SENDER.
INCOMING_ASSESSMENT_READS_OUR_BURDEN = True


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
