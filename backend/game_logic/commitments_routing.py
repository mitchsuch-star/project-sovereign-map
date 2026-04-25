"""Single-source presentation routing for commitments notice families.

The rows here mirror COMMITMENTS_PRESENTATION_SPEC section 8.1 for the
commitments event families that are live in backend code. Backend dispatch,
campaign log, notifications, and Godot tests read these values instead of
copying labels and template keys in each surface.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping


COMMITMENTS_ROUTES: Dict[str, Dict[str, str]] = {
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
        "speaker": "foreign_office_chancery",
        "review_target": "ledger_commitments",
        "review_label": "Open Ledger",
    },
}


COMMITMENTS_NOTICE_TEMPLATES: Dict[str, str] = {
    "balance_of_europe_shifted": (
        "{label} commands {share_pct}% of Continental power. {counterplay_hint}"
    ),
    "witness_strike_recorded": (
        "{witness_nation} has taken note of {perpetrator_nation}'s conduct "
        "toward {victim_nation}."
    ),
    "call_to_arms_refused_offensive": (
        "{breaker} has refused the offensive call from {victim}."
    ),
    "call_to_arms_refused_defensive": (
        "{breaker} has refused the defensive call from {victim}."
    ),
    "call_to_arms_honored_costly": (
        "{honorer} has honored a costly defensive call from {victim}."
    ),
}


class _SafeFormatDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def commitments_route(event_type: str) -> Dict[str, str]:
    """Return a copy of the routing row for an event type."""
    return dict(COMMITMENTS_ROUTES.get(event_type, {}))


def commitments_priority(event_type: str, data: Mapping[str, Any] | None = None) -> str:
    """Return the route priority, including band-sensitive Balance beats."""
    route = COMMITMENTS_ROUTES.get(event_type, {})
    if event_type == "balance_of_europe_shifted":
        band = int((data or {}).get("band", 0) or 0)
        return "CRITICAL" if band >= 2 else "NORMAL"
    return route.get("priority", "MEDIUM")


def commitments_label(event_type: str) -> str:
    route = COMMITMENTS_ROUTES.get(event_type, {})
    return route.get("label", event_type.replace("_", " ").title())


def commitments_template_key(event_type: str) -> str:
    route = COMMITMENTS_ROUTES.get(event_type, {})
    return route.get("template", event_type)


def commitments_notice_details(
    event_type: str,
    data: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Details payload shared by notification rail and UI review actions."""
    route = commitments_route(event_type)
    details: Dict[str, Any] = {
        "event_type": event_type,
        "template_key": route.get("template", event_type),
        "icon": route.get("icon", ""),
        "label": route.get("label", commitments_label(event_type)),
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
    template = COMMITMENTS_NOTICE_TEMPLATES.get(
        event_type,
        "{event_type}",
    )
    return template.format_map(values).strip()
