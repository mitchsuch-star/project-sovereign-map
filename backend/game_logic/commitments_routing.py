"""Single-source presentation routing for commitments notice families.

The rows here mirror COMMITMENTS_PRESENTATION_SPEC section 8.1 for the
commitments event families that are live in backend code. Backend dispatch,
campaign log, notifications, and Godot tests read these values instead of
copying labels and template keys in each surface.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping


COMMITMENTS_ROUTES: Dict[str, Dict[str, str]] = {
    "commitment_paradox": {
        "priority": "HARD_STOP",
        "icon": "icon_paradox",
        "label": "Conflicting Oaths",
        "template": "commitments_notice_paradox",
        "speaker": "talleyrand",
        "review_target": "ledger_commitments",
        "review_label": "Open Ledger",
    },
    "balance_of_europe_shifted": {
        "priority": "NORMAL",
        "critical_priority_rule": "band>=2",
        "icon": "icon_balance_of_europe",
        "label": "Balance of Europe Shifts",
        "template": "commitments_notice_balance_of_europe_shifted",
        "speaker": "envoy_then_talleyrand_then_foreign_office",
        "review_target": "ledger_commitments",
        "review_label": "Open Ledger",
    },
    "witness_strike_recorded": {
        "priority": "NORMAL",
        "icon": "icon_witness_strike",
        "label": "Europe Is Aware",
        "template": "commitments_notice_witness_strike",
        "speaker": "system_or_foreign_office",
        "review_target": "",
        "review_label": "",
    },
    "amends_offered": {
        "priority": "NORMAL",
        "icon": "icon_amends_offered",
        "label": "Amends Offered",
        "template": "commitments_notice_amends_offered",
        "speaker": "envoy_to_target_diplomat",
        "review_target": "ledger_commitments",
        "review_label": "Open Ledger",
    },
    "hard_reject_posture_triggered": {
        "priority": "CRITICAL",
        "icon": "icon_hard_reject",
        "label": "The Chancery Shut",
        "template": "commitments_notice_hard_reject_triggered",
        "speaker": "foreign_office_chancery",
        "review_target": "ledger_commitments",
        "review_label": "Open Ledger",
    },
    "hard_reject_posture_cleared": {
        "priority": "NORMAL",
        "icon": "icon_chancery_reopened",
        "label": "The Chancery Reopens",
        "template": "commitments_notice_hard_reject_cleared",
        "speaker": "foreign_office_chancery",
        "review_target": "ledger_commitments",
        "review_label": "Open Ledger",
    },
    "diplomatic_treaty_broken": {
        "priority": "NORMAL",
        "icon": "icon_treaty_dragged",
        "label": "Treaty Dragged Apart",
        "template": "commitments_notice_breach_other",
        "speaker": "foreign_office_context_nation",
        "review_target": "ledger_commitments",
        "review_label": "Open Ledger",
    },
    "commitment_paradox_resolved": {
        "priority": "NORMAL",
        "icon": "icon_paradox_resolved",
        "label": "The Wound Chosen",
        "template": "commitments_notice_paradox_resolved",
        "speaker": "talleyrand_notice_or_system_log",
        "review_target": "",
        "review_label": "",
    },
    "call_to_arms_refused_offensive": {
        "priority": "CRITICAL",
        "icon": "icon_call_refused_offensive",
        "label": "Pact Dishonoured",
        "template": "commitments_notice_call_refused_offensive",
        "speaker": "envoy_to_victim_diplomat",
        "review_target": "ledger_commitments",
        "review_label": "Open Ledger",
    },
    "call_to_arms_refused_defensive": {
        "priority": "CRITICAL",
        "icon": "icon_call_refused_defensive",
        "label": "Ally Abandoned",
        "template": "commitments_notice_call_refused_defensive",
        "speaker": "envoy_to_victim_diplomat",
        "review_target": "ledger_commitments",
        "review_label": "Open Ledger",
    },
    "call_to_arms_honored_costly": {
        "priority": "CRITICAL",
        "icon": "icon_call_honored_costly",
        "label": "Oath Kept",
        "template": "commitments_notice_call_honored_costly",
        "speaker": "foreign_office_chancery_france",
        "review_target": "ledger_commitments",
        "review_label": "Open Ledger",
    },
}

_TREATY_BROKEN_FRENCH_BREACH_ROUTE: Dict[str, str] = {
    "priority": "CRITICAL",
    "icon": "icon_treaty_broken",
    "label": "Word Broken",
    "template": "commitments_notice_breach_french",
    "speaker": "envoy_to_injured_diplomat",
    "review_target": "ledger_commitments",
    "review_label": "Review the broken treaty",
}


COMMITMENTS_NOTICE_TEMPLATES: Dict[str, str] = {
    "commitment_paradox": (
        "France is bound to both {attacker} and {defender}; one oath must give way."
    ),
    "balance_of_europe_shifted": (
        "{label} commands {share_pct}% of Continental power. {counterplay_hint}"
    ),
    "witness_strike_recorded": (
        "{witness_nation} has taken note of {perpetrator_nation}'s conduct "
        "toward {victim_nation}."
    ),
    "amends_offered": (
        "{actor_nation} offered amends to {target_nation} ({gold_spent}g, {dp_spent} DP)."
    ),
    "hard_reject_posture_triggered": (
        "The Chancery of {victim_nation} has shut the chancery to {perpetrator_nation} "
        "after repeated betrayals."
    ),
    "hard_reject_posture_cleared": (
        "The Chancery of {victim_nation} has reopened deeper diplomacy with "
        "{perpetrator_nation}."
    ),
    "diplomatic_treaty_broken": (
        "{breaker} has broken the {treaty_type_display} with {injured_party} {reason_phrase}."
    ),
    "commitment_paradox_resolved": (
        "In a crisis of commitments, {player_nation} chose {chosen_nation} "
        "over {spurned_nation}."
    ),
    "call_to_arms_refused_offensive": (
        "{breaker} has refused the offensive call from {victim}."
    ),
    "call_to_arms_refused_defensive": (
        "{breaker} has refused the defensive call from {victim}."
    ),
    "call_to_arms_honored_costly": (
        "The Chancery of France records that {honorer} honored a costly "
        "defensive call from {victim}."
    ),
}


class _SafeFormatDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def _is_french_breach(data: Mapping[str, Any] | None = None) -> bool:
    return str((data or {}).get("end_reason_family", "")) == "french_breach"


def commitments_route(
    event_type: str,
    data: Mapping[str, Any] | None = None,
) -> Dict[str, str]:
    """Return a copy of the routing row for an event type."""
    if event_type == "diplomatic_treaty_broken" and _is_french_breach(data):
        return dict(_TREATY_BROKEN_FRENCH_BREACH_ROUTE)
    return dict(COMMITMENTS_ROUTES.get(event_type, {}))


def commitments_priority(event_type: str, data: Mapping[str, Any] | None = None) -> str:
    """Return the route priority, including band-sensitive Balance beats."""
    route = COMMITMENTS_ROUTES.get(event_type, {})
    if event_type == "balance_of_europe_shifted":
        band = int((data or {}).get("band", 0) or 0)
        return "CRITICAL" if band >= 2 else "NORMAL"
    if event_type == "diplomatic_treaty_broken" and _is_french_breach(data):
        return "CRITICAL"
    return route.get("priority", "MEDIUM")


def commitments_label(
    event_type: str,
    data: Mapping[str, Any] | None = None,
) -> str:
    route = commitments_route(event_type, data)
    return route.get("label", event_type.replace("_", " ").title())


def commitments_template_key(
    event_type: str,
    data: Mapping[str, Any] | None = None,
) -> str:
    route = commitments_route(event_type, data)
    return route.get("template", event_type)


def commitments_notice_details(
    event_type: str,
    data: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Details payload shared by notification rail and UI review actions."""
    route = commitments_route(event_type, data)
    details: Dict[str, Any] = {
        "event_type": event_type,
        "template_key": route.get("template", event_type),
        "icon": route.get("icon", ""),
        "label": route.get("label", commitments_label(event_type, data)),
        "speaker": route.get("speaker", ""),
        "review_target": route.get("review_target", ""),
        "review_label": route.get("review_label", ""),
    }
    if data:
        details.update(dict(data))
    return details


def format_commitments_notice(
    event_type: str,
    data: Mapping[str, Any] | None = None,
) -> str:
    """Format the committed fallback notice body for a commitments event."""
    values = _SafeFormatDict(data or {})
    values.setdefault("player_nation", "France")
    if event_type == "balance_of_europe_shifted":
        values.setdefault(
            "label",
            values.get("bloc_label")
            or values.get("descriptive_label")
            or values.get("hegemon")
            or "The leading alignment",
        )
        share = values.get("share", 0)
        if "share_pct" not in values:
            try:
                values["share_pct"] = int(round(float(share) * 100))
            except (TypeError, ValueError):
                values["share_pct"] = 0
        values.setdefault("counterplay_hint", "")
    elif event_type == "amends_offered":
        values.setdefault("actor_nation", "France")
        values.setdefault("target_nation", values.get("nation", "Unknown"))
        values.setdefault("gold_spent", 0)
        values.setdefault("dp_spent", 0)
        if str(values.get("amends_variant", "")).lower() == "grievance":
            return (
                f"{values['actor_nation']} offered amends to "
                f"{values['target_nation']} for the abandoned alliance "
                f"({values['gold_spent']}g, {values['dp_spent']} DP)"
            )
    elif event_type == "diplomatic_treaty_broken":
        breaker = values.get("breaker") or values.get("nation") or "Unknown"
        injured = (
            values.get("injured_party")
            or values.get("other")
            or values.get("target")
            or "Unknown"
        )
        treaty = (
            values.get("treaty_type_display")
            or str(values.get("treaty_type", "treaty")).replace("_", " ")
        )
        reason = str(values.get("reason_phrase", "") or "").strip()
        family = str(values.get("end_reason_family", "") or "")
        if family == "obsolescence_or_external":
            return (
                f"{breaker} was forced to break the {treaty} with {injured} "
                "(cascade)."
            )
        if family == "counterparty_reversal":
            return (
                f"Treaty broken by counterparty: {injured} - {treaty} "
                f"with {breaker}"
            )
        suffix = f" {reason}" if reason else ""
        return f"{breaker} has broken the {treaty} with {injured}{suffix}."
    elif event_type == "commitment_paradox_resolved":
        values.setdefault("chosen_nation", "Unknown")
        values.setdefault("spurned_nation", "Unknown")
        before = values.get("reliability_before")
        after = values.get("reliability_after")
        if before is not None and after is not None:
            return (
                f"In a crisis of commitments, {values['player_nation']} chose "
                f"{values['chosen_nation']} over {values['spurned_nation']} "
                f"({before} -> {after} reliability)."
            )
    template = COMMITMENTS_NOTICE_TEMPLATES.get(
        event_type,
        "{event_type}",
    )
    return template.format_map(values).strip()
