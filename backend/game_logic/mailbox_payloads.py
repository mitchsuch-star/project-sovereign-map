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


# ══════════════════════════════════════════════════════════════════════
# IQ-7 review round (September 18, 2026) — INTERFACE A, read through ONE
# adapter. `vassal.py` exports `reprice_petition`,
# `petition_grant_availability` and `lapsing_petitions`; every read seam
# below resolves them HERE so a renamed function fails in one place. (The
# build's parallel-phase fallback shims — a second copy of the lapse price
# line, a DP-only availability read — were retired by the integrator once
# A's names landed: one arithmetic, one vocabulary, never two.)
# ══════════════════════════════════════════════════════════════════════

def _interface_a():
    from backend.game_logic import vassal as V

    return V


def reprice_petition(world, lord: str, vassal_tag: str, petition: Dict) -> Optional[Dict]:
    """R4: ONE re-pricer on the STORED subject (never the ladder). Returns
    the re-priced petition dict, or None = withdraw (`vassal.reprice_petition`)."""
    return _interface_a().reprice_petition(world, lord, vassal_tag, petition)


def petition_grant_availability(world, lord: str, vassal_tag: str,
                                petition: Dict) -> Tuple[bool, str]:
    """R2: honest availability of the Grant option, derived at READ time —
    `(enabled, reason)` from the same verdict the grant applies
    (`vassal.petition_grant_availability`)."""
    enabled, reason = _interface_a().petition_grant_availability(
        world, lord, vassal_tag, petition)
    return bool(enabled), str(reason or "")


def lapsing_petitions(world, lord: str) -> list:
    """R8(d): every pending petition of `lord`'s that would lapse this turn,
    each with its priced line (`vassal.lapsing_petitions` / `lapse_forecast`)."""
    return list(_interface_a().lapsing_petitions(world, lord) or [])


def petition_availability_keys(world, terms: Dict) -> Dict:
    """R2: the display keys that carry the Grant option's honest
    availability on a petition payload — `grant_enabled` / `grant_reason`
    and an `options` mirror the popup can read. Derived from the terms the
    payload was built from, at the moment of the READ (never baked at
    issue: the petition is issued right after `_process_dp_regen`, so a
    flag baked then would read "available" for the whole turn — IGR-2)."""
    petition = terms.get("petition") if isinstance(terms, dict) else None
    petition = petition if isinstance(petition, dict) else {}
    lord = str(terms.get("target_nation")
               or getattr(world, "player_nation", "France"))
    vassal = str(terms.get("proposer_nation") or petition.get("vassal") or "")
    enabled, reason = petition_grant_availability(world, lord, vassal, petition)
    return {
        "grant_enabled": bool(enabled),
        "grant_reason": str(reason or ""),
        "options": [
            {"label": "Grant the petition", "action": "accept_ai_proposal",
             "enabled": bool(enabled), "reason": str(reason or "")},
            {"label": "Refuse the petition", "action": "reject_ai_proposal",
             "enabled": True, "reason": ""},
        ],
    }


def refresh_client_petition_dialogue(world, dialogue: Dict) -> Optional[Dict]:
    """R4 / R2: re-price a client petition's STORED subject from live state
    and write the result back everywhere the quote is rendered — the
    dialogue's `context.proposal.petition`, its `popup_payload` (clauses,
    Talleyrand's line, the availability keys), `talleyrand_text` and the
    option descriptions — so the typed terminal, the popup, the mailbox
    activation and the answer handler read ONE dict (shown = applied).

    Returns the refreshed popup payload (a copy, stamped with the
    dialogue's id), or None when the dialogue is not a client petition.
    When the re-pricer says withdraw (None), the READ seams never retire the
    dialogue — the answer handler does, through `grant_petition` /
    `refuse_petition`'s own re-validation. Pass 2 (P4-1): on that arm the
    availability keys are the ones derived on THIS read (never the last
    read's stored dict) and the verdict's own sentence leads the clauses,
    the Grant option's description and the terminal text — the press
    retires the petition free, and every surface says so first. Pass 3
    (R3-4): on that arm the stored REFUSE and LAPSE lines go too whenever
    `vassal.lapse_forecast` says the refusal is free (every reachable moot
    arm), replaced by the forecast's own price line — a moot petition quotes
    no price it will not charge.
    """
    V = _interface_a()
    if not isinstance(dialogue, dict) or not V.is_client_petition(dialogue):
        return None
    context = dialogue.get("context") or {}
    terms = context.get("proposal") or {}
    if not isinstance(terms, dict):
        return None
    petition = terms.get("petition") if isinstance(terms.get("petition"), dict) else {}
    lord = str(terms.get("target_nation") or getattr(world, "player_nation", "France"))
    vassal = str(terms.get("proposer_nation") or context.get("source_nation")
                 or dialogue.get("target_nation") or petition.get("vassal") or "")
    repriced = reprice_petition(world, lord, vassal, petition) if petition else None
    if isinstance(repriced, dict) and repriced:
        petition = dict(repriced)
        terms["petition"] = petition
    # P4-1: did THIS read re-price the petition? (None = the verdict is
    # `withdrawn`: the petition is moot and the stored dict is the last
    # successful read's.)
    fresh = isinstance(repriced, dict) and bool(repriced)
    lines =list(petition.get("clauses") or []) if isinstance(petition.get("clauses"), list) else []
    lines = [str(line).strip() for line in lines if str(line).strip()]
    if not lines:
        lines = client_petition_clauses(terms)
    assessment = client_petition_assessment(terms)
    availability = petition_availability_keys(world, terms)
    stored = petition.get("availability")
    # Pass 2 (P4-1): the STORED availability is the re-pricer's own verdict
    # only when THIS read produced it. When the re-pricer says withdraw
    # (None) the stored dict is the LAST successful read's — measured, it
    # overwrote the honest "Switzerland pays no tribute now — … the petition
    # is withdrawn" with `{enabled: True, reason: ''}` under a clause still
    # quoting "225g a turn … (1800g forgone)", and the press withdrew it.
    # Reachable in play through the player's own `release switzerland` with
    # its petition on the desk. On that arm the freshly derived keys stand
    # and the verdict's line leads the clauses.
    if fresh and isinstance(stored, dict) and "enabled" in stored:
        # A's re-pricer carries the same verdict; one dict, one answer.
        availability["grant_enabled"] = bool(stored.get("enabled"))
        availability["grant_reason"] = str(stored.get("reason") or "")
        for option in availability["options"]:
            if option.get("action") == "accept_ai_proposal":
                option["enabled"] = availability["grant_enabled"]
                option["reason"] = availability["grant_reason"]
    moot_line = ""
    refusal_is_free = False
    forecast: Dict = {}
    if not fresh and petition:
        moot_line = str(availability.get("grant_reason") or "").strip()
        if moot_line:
            # The verdict leads, and the last read's GRANT quote goes: the
            # press no longer does what that line says.
            stale_grant = str(petition.get("grant_line") or "").strip()
            lines = [moot_line] + [
                line for line in lines
                if line != moot_line and line != stale_grant]
            # Pass 3 (R3-4, V2-5): A MOOT PETITION QUOTES NO PRICE IT WILL
            # NOT CHARGE. Pass 2 kept the stored refuse and lapse lines here
            # ("`refuse_petition` prices a relief of nothing as it prices
            # any refusal") — true for that one arm only, which pass 1
            # measured NOT organically reachable. On both reachable moot
            # arms (Milan falls after a prior read; the player's own
            # `release switzerland`) the popup still read "Refuse it, and
            # … loses 10 loyalty" and "a lapse is a refusal" while the
            # Refuse press and the lapse were measured FREE. The forecast
            # is the lapse's own read (`vassal.lapse_forecast` — what
            # `refuse_petition` would do): when it is not penalised the
            # stored refuse / lapse lines go and its price line stands in;
            # they stay only when the forecast says refused.
            forecast = V.lapse_forecast(world, vassal, lord, petition)
            refusal_is_free = not bool(forecast.get("penalised"))
            if refusal_is_free:
                stale_priced = {
                    str(petition.get(key) or "").strip()
                    for key in ("refuse_line", "lapse_line", "lapse_price_line")}
                stale_priced.discard("")
                free_line = str(forecast.get("price_line") or "").strip()
                # The verdict line above already names the CAUSE; when the
                # forecast's line opens with the same cause ("Tyrol no
                # longer adjoins … — a lapse withdraws the petition; nothing
                # is charged") the clause keeps only what is new.
                cause = moot_line.split(" — ", 1)[0]
                free_clause = free_line
                if cause and free_line.startswith(f"{cause} — "):
                    tail = free_line[len(cause) + 3:].strip()
                    free_clause = tail[:1].upper() + tail[1:]
                lines = [line for line in lines
                         if line not in stale_priced
                         and line not in (free_line, free_clause)]
                if free_clause:
                    lines.append(free_clause)

    payload = dialogue.get("popup_payload")
    if not isinstance(payload, dict) or not payload:
        payload = build_pending_envoy_popup_from_terms(
            world, nation=vassal, terms=terms, assessment="",
            decision_reason=str(context.get("decision_reason") or ""))
        dialogue["popup_payload"] = payload
    payload["clauses"] = list(lines)
    payload["talleyrand_assessment"] = assessment
    payload.update(availability)
    payload["is_petition"] = True

    # The typed terminal renders the dialogue's own text and options.
    grant_line = str(petition.get("grant_line") or "")
    refuse_line = str(petition.get("refuse_line") or "")
    if moot_line:
        # P4-1: the press retires a moot petition, free — the last read's
        # grant quote must not sit beside the option.
        grant_line = moot_line
        if refusal_is_free:
            # R3-4: …and neither must the last read's refusal price sit
            # beside Refuse, which is measured free on this arm.
            refuse_line = (str(forecast.get("price_line") or "").strip()
                           or moot_line)
    for option in dialogue.get("options") or []:
        if not isinstance(option, dict):
            continue
        action = str(option.get("action") or "")
        if action == "accept_ai_proposal":
            if grant_line:
                option["description"] = grant_line
            option["enabled"] = availability["grant_enabled"]
            option["reason"] = availability["grant_reason"]
        elif action == "reject_ai_proposal":
            if refuse_line:
                option["description"] = refuse_line
            option["enabled"] = True
            option["reason"] = ""
    # P4-1: the stored `talleyrand_text` is the last successful re-price's;
    # on the moot arm the body is rebuilt from the lines the payload carries
    # (the verdict's line first), so the typed terminal reads what the popup
    # reads.
    repriced_text = (str(petition.get("talleyrand_text") or "").strip()
                     if not moot_line else "")
    text = dialogue.get("talleyrand_text")
    if repriced_text:
        dialogue["talleyrand_text"] = repriced_text
    elif isinstance(text, str) and "\n\n" in text:
        head = text.split("\n\n", 1)[0]
        body = "\n".join(f"  {line}" for line in lines)
        dialogue["talleyrand_text"] = f"{head}\n\n{body}\n\n{assessment}"

    popup = copy.deepcopy(payload)
    if dialogue.get("dialogue_id") is not None:
        popup["dialogue_id"] = dialogue["dialogue_id"]
    return popup


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

    # LV-6 (row EP F2, Sept 25 2026): this builder shapes the popup for an
    # INCOMING envoy — the other court's offer, or its counter to ours —
    # and the acceptance hints it carried were the FEEDBACK_STRINGS written
    # from France-as-proposer's viewpoint ("Key obstacle: their diplomat
    # outmaneuvered us" on Prussia's own open-borders offer, when Talleyrand
    # had outclassed theirs). Both hints are blanked here, the way the
    # client-petition arm below already blanks them; the player's OWN
    # previews (`main.py`'s acceptance-hint route) keep theirs. The
    # `acceptance` argument is still accepted (callers pass it) and still
    # unused for display.
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

    # LV-3 (row EP F2): the terminal's echo ("Responding to Ottoman's
    # proposal: accept") is composed by the client from `from_nation` and
    # the choice TOKEN. The backend owns the article (the client's prose
    # repair deliberately skips "Ottoman"), so the payload carries the
    # printed form and a label per answer the popup can send.
    from backend.display_names import with_definite_article
    from backend.game_logic.formations import formed_display_name
    from_nation_display = with_definite_article(formed_display_name(world, nation))
    choice_display = {
        "accept": "accepted",
        "reject": "declined",
        "counter": "countered",
        "dismiss": "set aside",
        "grant": "granted",
        "refuse": "refused",
        "yield": "yielded to",
        "defy": "defied",
    }
    payload = {
        "from_nation": nation,
        "from_nation_display": from_nation_display,
        "choice_display": choice_display,
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
        # IQ-7 review [23]: with `diplomat_line` blank, the popup printed
        # "Court rationale: Client Petition." (the raw key title-cased) —
        # and blanking only the display half would have printed "Court
        # motive: client_petition" (the raw key bare). A petition carries no
        # court motive; both halves go.
        payload["decision_reason"] = ""
        payload["decision_reason_display"] = ""
        # R2: the Grant option's honest availability, derived at THIS read.
        payload.update(petition_availability_keys(world, terms))
        # A vassal without a diplomat record would fall back to
        # "the {tag} ambassador" above — the raw tag, which R7 forbids.
        if diplomat is None:
            from backend.display_names import with_definite_article
            from backend.game_logic.formations import formed_display_name
            payload["diplomat_name"] = (
                f"the envoy of "
                f"{with_definite_article(formed_display_name(world, nation))}")
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
                incoming=True,
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
