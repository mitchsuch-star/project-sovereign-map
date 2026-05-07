"""Slice E settlement presentation surface (spec §11.6 / §14 / §16).

This module owns the *presentation* contract for Imperial Settlement
events. The mechanical work (memory writes, grievance flags, bargain
breaches, cross-war scans, dispatch event emission) lives in
``settlement_reactions.py``. Slice E surfaces those events into:

- Dispatch (`backend/game_logic/dispatch.py`): fog-filtered one-liner
  + digest overflow, top-four primary settlement beats per ratification.
- Campaign log (`backend/campaign_log.py`): one `settlement_summary`
  entry per ratified common peace, with structured
  ``participant_reactions`` already shipped on the event payload.
- Diplomatic ledger (`backend/game_logic/diplomatic_ledger.py`): recent
  settlement summaries with route metadata (`settlement_review` while
  the war is active, `diplomatic_ledger` after the war archives).
- Notification rail (`notification_bar.gd` via `_on_notification_review_requested`):
  spotlight metadata for major outcomes only.
- Settlement review (Godot `diplomatic_ledger.gd::open_to_settlements`):
  sectioned payload (Terms / Allies / Warnings / Acceptance) at
  compact / medium / verbose density per spec §16.2.

Settlement route metadata is intentionally **separate** from
``COMMITMENTS_ROUTES`` (spec §11.6 line 1290): bargain events keep their
existing WB-D routing; settlement-summary / settlement-digest /
settlement-spotlight events use ``SETTLEMENT_ROUTES`` here.

Spec gates honored in this slice:
- §11.6 line 1279 — primary-beat cap (4) + digest overflow.
- §11.6 line 1287 — event payload minimums + one-liner shape.
- §11.6 line 1287 — fog rule: visible to France, or to any court that
  can see at least one covered participant, resulting territorial /
  alignment change, or participant reaction involving itself.
- §16.2 line 1636 — sectioned settlement review (Terms / Allies /
  Warnings / Acceptance).
- §16.2 line 1647 — compact / medium / verbose density fallbacks.
- §16.3 line 1655 — warning cap: hard stops inline; top 2 warnings
  inline; the rest behind "View all concerns".
- §20.8 line 2174 — awe set-piece tagging.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from backend.display_names import clause_display_name, side_label_display

from backend.models.intel import FULL, PARTIAL, VISIBILITY_PRIORITY


# ---------------------------------------------------------------------------
# Spec constants
# ---------------------------------------------------------------------------


# Spec §11.6 line 1279.
SETTLEMENT_PRIMARY_BEAT_CAP = 4
# Settlement summary one-liner shows at most this many named participants.
SETTLEMENT_ONELINER_PARTICIPANT_CAP = 3
# Default ledger overview row cap.
SETTLEMENT_LEDGER_DEFAULT_ROWS = 5
# SC-23: combined cap for the merged PEACE & SETTLEMENT HISTORY surface.
# Common-peace settlement and bilateral peace ratification rows share a
# single reverse-chronological surface; per-war dedup is OFF, each
# ratification event is its own row.
PEACE_HISTORY_DEFAULT_ROWS = 5
# SC-23: bilateral peace history route-id namespace.
# Settlement rows use `settlement:{war_id}:{turn}:{seq}` (SC-14c); bilateral
# peace rows use `peace:{participants_signature}:{turn}:{seq}` so focus
# ids cannot collide.
PEACE_HISTORY_BILATERAL_NAMESPACE = "peace"
PEACE_HISTORY_SETTLEMENT_NAMESPACE = "settlement"
# Spec §16.2 line 1620 — advisory standing/contribution row cap.
SETTLEMENT_STANDING_ROW_CAP = 5
# Spec §16.3 line 1660 — top warnings rendered inline after hard stops.
SETTLEMENT_INLINE_WARNING_CAP = 2

STANDING_DISPLAY = {
    "leader": "War leader",
    "seat": "Seat at settlement",
    "consult": "Consulted ally",
    "beneficiary_only": "Named beneficiary",
    "no_standing": "No settlement standing",
}

WARNING_CODE_DISPLAY = {
    "ally_shut_out": "Ally shut out",
    "enemy_sold_out": "Enemy ally sold out",
    "bargain_breach_at_settlement": "Bargain at risk",
    "cross_war_rival_strengthened": "Rival strengthened",
    "hard_stop": "Settlement blocked",
    "acceptance_component": "Acceptance concern",
}

ACCEPTANCE_BAND_DISPLAY = {
    "accept": "Acceptable",
    "acceptable": "Acceptable",
    "near_acceptable": "Near acceptable",
    "unlikely": "Unlikely",
    "blocked": "Blocked",
    "reject": "Likely rejected",
    "counter": "Likely counter-offer",
}

AWE_TAG_DISPLAY = {
    "triple_forced_alignment": "Triple forced alignment",
    "tilsit_bargain_and_betrayal": "Tilsit-style settlement",
    "defensive_coalition_preservation": "Defensive coalition preserved",
    "balance_of_europe_crossing": "Balance of Europe shifts",
}

# Spec §11.6 line 1287 — event family + review-target taxonomy.
# F1 fix: archived settlements deep-link to the Recent Settlements block
# in the Treaties tab via `ledger_settlements` rather than landing on the
# generic `diplomatic_ledger` Nations tab. The frontend `main.gd` notice
# router treats `ledger_settlements` as the canonical settlement deep-link
# for both active and archived events.
SETTLEMENT_EVENT_FAMILY = "settlement"
SETTLEMENT_REVIEW_TARGET_ACTIVE = "settlement_review"
SETTLEMENT_REVIEW_TARGET_ARCHIVED = "ledger_settlements"


# Spec §11.6 line 1290 — settlement events use their own route metadata,
# distinct from `COMMITMENTS_ROUTES`. Only major outcomes feed the
# notification rail; the dispatch/campaign-log render path uses the
# `event_family="settlement"` umbrella regardless.
SETTLEMENT_ROUTES: Dict[str, Dict[str, str]] = {
    "settlement_summary": {
        "priority": "HIGH",
        "icon": "icon_settlement_summary",
        "label": "Settlement Ratified",
        "speaker": "talleyrand",
        "review_label": "Review settlement",
        "event_family": SETTLEMENT_EVENT_FAMILY,
        "rail_spotlight": "yes",
    },
    "settlement_digest": {
        "priority": "NORMAL",
        "icon": "icon_settlement_digest",
        "label": "Settlement Aftermath",
        "speaker": "talleyrand",
        "review_label": "View settlement aftermath",
        "event_family": SETTLEMENT_EVENT_FAMILY,
        "rail_spotlight": "no",  # rail spotlights only major outcomes
    },
}


# ---------------------------------------------------------------------------
# Route helpers
# ---------------------------------------------------------------------------


def is_settlement_event_type(event_type: str) -> bool:
    """Whether `event_type` belongs to the settlement family."""
    return event_type in SETTLEMENT_ROUTES


def settlement_route(event_type: str) -> Dict[str, str]:
    """Return a copy of the route row for a settlement event type."""
    return dict(SETTLEMENT_ROUTES.get(event_type, {}))


def settlement_priority(
    event_type: str, data: Mapping[str, Any] | None = None,
) -> str:
    """Return the route priority for a settlement event.

    Spec §11.6 + §16.2 — `settlement_digest` defaults to NORMAL because
    overflow is by definition the secondary beat. `settlement_summary`
    rises to CRITICAL when the payload tags a major beat (bargain
    breach, major-power humiliation, balance-of-power crossing) so the
    rail does not silently swallow it.
    """
    base = SETTLEMENT_ROUTES.get(event_type, {}).get("priority", "MEDIUM")
    if event_type != "settlement_summary" or data is None:
        return base
    awe = list((data or {}).get("awe_tags") or [])
    if awe:
        return "CRITICAL"
    reactions = list((data or {}).get("participant_reactions") or [])
    for reaction in reactions:
        if not isinstance(reaction, Mapping):
            continue
        kind = reaction.get("kind", "")
        if kind == "bargain_breach_at_settlement":
            return "CRITICAL"
        if kind == "ally_shut_out":
            severity = str(reaction.get("severity", ""))
            if severity == "major_shut_out":
                return "CRITICAL"
        if kind == "enemy_sold_out":
            return "CRITICAL"
    return base


def settlement_review_target(
    event: Mapping[str, Any] | None,
    *,
    world: Any | None = None,
) -> str:
    """Return the review target for a settlement event payload.

    Spec §11.6 line 1287 — `review_target="settlement_review"` while the
    war is active; switches to `"diplomatic_ledger"` once the war
    archives. The settlement event payload carries `route.review_target`
    (canonical) and `war_ended` (fallback).

    G2-Slice-3 SC-14/SC-14d/SC-14e: when ``world`` is supplied, the live
    war state wins over the route metadata so a row rendered while the
    war was active opens the archived ledger row if the war archived
    between render and click. Callers that have access to live world
    state (notification rail, dispatch click handlers, result feedback
    re-emit) MUST pass ``world``; callers without world state (pure
    payload renderers) keep the legacy stamped behavior.
    """
    if world is not None and isinstance(event, Mapping):
        from backend.game_logic.settlement_preview import (
            derive_settlement_review_target,
            is_war_known,
        )
        war_id = str(event.get("war_id") or "")
        if war_id and is_war_known(world, war_id):
            return derive_settlement_review_target(world, war_id=war_id)
    if not event:
        return SETTLEMENT_REVIEW_TARGET_ACTIVE
    route = event.get("route") if isinstance(event, Mapping) else None
    if isinstance(route, Mapping):
        target = str(route.get("review_target", "") or "")
        if target:
            return target
    if event.get("war_ended"):
        return SETTLEMENT_REVIEW_TARGET_ARCHIVED
    return SETTLEMENT_REVIEW_TARGET_ACTIVE


def settlement_notification_meta(
    event: Mapping[str, Any],
    *,
    world: Any | None = None,
) -> Dict[str, Any]:
    """Notification rail spotlight metadata for a settlement event.

    Spec §16.2 line 1632 — major events only spotlight the rail. The
    callers (dispatch + main.py rail collector) check
    ``rail_spotlight`` before pushing to the rail, so digest events
    return metadata but with ``rail_spotlight="no"`` to keep them off
    the rail.
    """
    if not isinstance(event, Mapping):
        return {}
    event_type = str(event.get("type", "") or "")
    route = settlement_route(event_type)
    if not route:
        return {}
    review_target = settlement_review_target(event, world=world)
    payload = {
        "event_type": event_type,
        "event_family": route.get("event_family", SETTLEMENT_EVENT_FAMILY),
        "priority": settlement_priority(event_type, event),
        "icon": route.get("icon", ""),
        "label": route.get("label", "Settlement"),
        "speaker": route.get("speaker", "talleyrand"),
        "review_target": review_target,
        "review_label": route.get("review_label", "Review settlement"),
        "rail_spotlight": route.get("rail_spotlight", "no"),
        "war_id": str(event.get("war_id", "") or ""),
        "turn": int(event.get("turn", 0) or 0),
        "route_id": str(
            (event.get("route") or {}).get("route_id", "") or ""
        ),
    }
    awe = list(event.get("awe_tags") or [])
    if awe:
        payload["awe_tags"] = list(awe)
    return payload


# ---------------------------------------------------------------------------
# Fog filter (spec §11.6 line 1287)
# ---------------------------------------------------------------------------


def _settlement_visible_nations(event: Mapping[str, Any]) -> List[str]:
    """Collect every nation a settlement event mentions for fog purposes."""
    out: List[str] = []
    for key in ("proposer_side", "accepting_side"):
        # Side names ("attackers"/"defenders") are not nation labels — skip.
        _ = event.get(key)
    for nation in event.get("covered_enemy_participants", []) or []:
        if isinstance(nation, str) and nation:
            out.append(nation)
    for clause in event.get("applied_clauses", []) or []:
        if not isinstance(clause, Mapping):
            continue
        for field in ("from", "to", "beneficiary", "lord_nation",
                      "vassal_nation", "liberator", "liberator_nation"):
            value = clause.get(field)
            if isinstance(value, str) and value:
                out.append(value)
    for term in event.get("terms_summary", []) or []:
        # Format "type: from→to" — skip parsing; clauses already cover it.
        _ = term
    for reaction in event.get("participant_reactions", []) or []:
        if not isinstance(reaction, Mapping):
            continue
        for field in ("ally", "burdened_participant", "victim",
                      "breaker", "leader", "recipient", "beneficiary",
                      "promiser"):
            value = reaction.get(field)
            if isinstance(value, str) and value:
                out.append(value)
        for region in reaction.get("rival_strengthened", []) or []:
            if isinstance(region, str) and region:
                out.append(region)
    return out


def is_settlement_event_visible(
    event: Mapping[str, Any], world: Any, player_nation: str,
) -> bool:
    """Spec §11.6 line 1287 fog rule for settlement events.

    Visible to France, or to any court that can see at least one covered
    participant, resulting territorial / alignment change, or
    participant reaction involving itself. France always sees its own
    settlements (proposer or accepting side).

    A digest event filters down to courts that can see at least one
    hidden reaction — the same fog logic applies because the digest
    event includes the war_id and any reaction families that were
    rolled into it; we surface the digest if any of the same nations
    that fed the parent summary are visible.
    """
    if not isinstance(event, Mapping):
        return False
    event_type = str(event.get("type", "") or "")
    if not is_settlement_event_type(event_type):
        return False
    nations = _settlement_visible_nations(event)
    # Digest events have minimal payload; fall back to the parent summary's
    # covered participants the orchestrator should preserve when emitting.
    if event_type == "settlement_digest":
        for nation in event.get("covered_enemy_participants", []) or []:
            if isinstance(nation, str) and nation and nation not in nations:
                nations.append(nation)
    # France always sees its own settlement involvement.
    proposer_members = list(event.get("proposer_members") or [])
    accepting_members = list(event.get("accepting_members") or [])
    if (
        player_nation in proposer_members
        or player_nation in accepting_members
        or player_nation in nations
    ):
        return True
    if not nations:
        # No nation context — event is structurally incomplete; default
        # to visible so we do not silently drop debug data, but flag it
        # for tests.
        return True
    # Late-bound import to avoid circular dependency.
    from backend.game_logic.diplomatic_ledger import _get_nation_visibility
    partial_priority = VISIBILITY_PRIORITY.get(PARTIAL, 3)
    for nation in nations:
        if nation == player_nation:
            return True
        vis = _get_nation_visibility(nation, world)
        vis_priority = VISIBILITY_PRIORITY.get(vis, 0)
        if vis_priority >= partial_priority:
            return True
    return False


# ---------------------------------------------------------------------------
# One-liner formatting (spec §11.6 line 1287)
# ---------------------------------------------------------------------------


def _war_label(world: Any, war_id: str) -> str:
    """Return a short war label, falling back to the raw war id."""
    if not war_id:
        return "settlement"
    instances = getattr(world, "war_instances", None) or {}
    war = instances.get(war_id) or {}
    if isinstance(war, Mapping):
        attackers = list(war.get("attackers") or [])
        defenders = list(war.get("defenders") or [])
        if attackers and defenders:
            return f"{attackers[0]} vs {defenders[0]}"
    return str(war_id)


def _participant_display(reaction: Mapping[str, Any]) -> str:
    return str(
        reaction.get("ally")
        or reaction.get("burdened_participant")
        or reaction.get("victim")
        or reaction.get("recipient")
        or reaction.get("beneficiary")
        or ""
    )


def _humanize_term(term_str: str) -> str:
    """Render a `terms_summary` row in player-facing prose.

    SC-17: Type labels delegate to ``clause_display_name(ttype)`` so the
    dispatch one-liner uses the canonical clause display ("Territory
    cession") rather than a raw underscore-stripped enum
    ("territory cede"). Only the unknown-type path falls back to
    underscore-stripping per the SC-17 amendment.
    """
    if not term_str:
        return "settlement ratified"
    if ": " not in term_str:
        # No `type: rest` shape — leave string-only payloads to the
        # underscore-strip fallback.
        return term_str.replace("_", " ")
    ttype, _, rest = term_str.partition(": ")
    raw = str(ttype or "").strip()
    if not raw:
        return rest
    display = clause_display_name(raw)
    fallback = raw.replace("_", " ").title()
    if display and display.lower() != "unknown clause" and display != fallback:
        # `clause_display_name` returned a registered display token —
        # use it verbatim instead of stripping underscores.
        return f"{display}: {rest}"
    # Unknown clause type — preserve the SC-17 underscore-strip fallback
    # so unknown enums still render as "territory cede: ..." instead of
    # leaking `territory_cede`.
    return f"{raw.replace('_', ' ')}: {rest}"


def _display_from_raw(raw: str, fallback: str = "") -> str:
    raw = str(raw or "")
    if not raw:
        return fallback
    return raw.replace("_", " ").title()


def _standing_display(standing: str) -> str:
    return STANDING_DISPLAY.get(str(standing or ""), _display_from_raw(standing, "Standing"))


def _warning_code_display(code: str) -> str:
    return WARNING_CODE_DISPLAY.get(str(code or ""), _display_from_raw(code, "Concern"))


def _acceptance_band_display(band: str) -> str:
    return ACCEPTANCE_BAND_DISPLAY.get(str(band or ""), _display_from_raw(band, "Acceptance"))


def _awe_tag_display(tag: str) -> str:
    return AWE_TAG_DISPLAY.get(str(tag or ""), _display_from_raw(tag, "Settlement"))


def _term_display(term: Mapping[str, Any]) -> str:
    label = str(term.get("display_label", "") or term.get("label", "") or "")
    if label:
        return label
    ttype = str(term.get("type", "") or "")
    if not ttype:
        return "End hostilities"
    base = clause_display_name(ttype)
    t_from = str(term.get("from", "") or term.get("payer", "") or term.get("vassal_nation", "") or "")
    t_to = str(term.get("to", "") or term.get("recipient", "") or term.get("overlord", "") or "")
    region = str(term.get("region", "") or term.get("claim_region", "") or "")
    if region and t_from and t_to:
        return f"{base}: {region} from {t_from} to {t_to}"
    if t_from and t_to:
        return f"{base}: {t_from} to {t_to}"
    if region:
        return f"{base}: {region}"
    return base


def _enrich_term_row(term: Mapping[str, Any]) -> Dict[str, Any]:
    row = dict(term)
    ttype = str(row.get("type", "") or "")
    row.setdefault("type_display", clause_display_name(ttype) if ttype else "Settlement term")
    row.setdefault("display_label", _term_display(row))
    return row


def _enrich_ally_row(ally: Mapping[str, Any]) -> Dict[str, Any]:
    row = dict(ally)
    standing = str(row.get("standing", "") or "")
    row.setdefault("standing_display", _standing_display(standing))
    share = float(row.get("material_share", 0.0) or 0.0)
    row.setdefault("standing_phrase", f"{_standing_display(standing)}; {round(share * 100):.0f}% material share")
    return row


def _enrich_warning_row(warning: Mapping[str, Any]) -> Dict[str, Any]:
    row = dict(warning)
    code = str(row.get("code", "") or row.get("category", "") or "")
    row.setdefault("code", code)
    row.setdefault("code_display", _warning_code_display(code))
    if not row.get("detail"):
        items = row.get("items")
        if isinstance(items, Sequence) and not isinstance(items, (str, bytes)):
            row["detail"] = ", ".join(_display_from_raw(str(i)) for i in items)
        elif row.get("component"):
            row["detail"] = _display_from_raw(str(row.get("component")))
    return row


def _voice_summary_template_key(event: Mapping[str, Any]) -> str:
    """Pick the Talleyrand advisory family for a summary one-liner.

    Spec §16.1 line 1600 — defender-side common peace uses the
    defensive register so the line does not dress necessity as
    conquest. Everything else uses the common-peace register.
    """
    proposer_side = str(event.get("proposer_side", "") or "")
    if proposer_side == "defenders":
        return "settlement_advisory_defensive_talleyrand"
    return "settlement_advisory_common_peace_talleyrand"


def compose_summary_oneliner(
    event: Mapping[str, Any], *, world: Any | None = None,
) -> str:
    """Render the one-liner per spec §11.6 line 1287.

    Routes through the Voice Bible §16.1
    `settlement_advisory_common_peace_talleyrand` /
    `settlement_advisory_defensive_talleyrand` family when the template
    is available; falls back to a generic templated string otherwise.
    The fallback still humanizes the term identifier so the player
    never sees `territory_cede:` style raw keys.
    """
    war_id = str(event.get("war_id", "") or "")
    payload_label = str(event.get("war_label", "") or "")
    war_label = (
        payload_label
        or (_war_label(world, war_id) if world is not None else (war_id or "war"))
    )
    terms = list(event.get("terms_summary") or [])
    head_term = _humanize_term(terms[0]) if terms else "settlement ratified"
    reactions = list(event.get("participant_reactions") or [])
    named: List[str] = []
    for reaction in reactions:
        if not isinstance(reaction, Mapping):
            continue
        name = _participant_display(reaction)
        if name and name not in named:
            named.append(name)
        if len(named) >= SETTLEMENT_ONELINER_PARTICIPANT_CAP:
            break
    more = max(0, len(reactions) - len(named))
    if named and more:
        who = f"{', '.join(named)} +{more} more"
    elif named:
        who = ", ".join(named)
    else:
        who = ""
    fallback = (
        f"Settlement of {war_label}: {head_term}; {who} react."
        if who
        else f"Settlement of {war_label}: {head_term}."
    )
    if not reactions:
        return fallback

    # Voice Bible §16.1 — wrap the dispatch one-liner in the Talleyrand
    # advisory register when the template is available. Late-bound
    # import so this module stays usable without diplomatic_templates
    # in lighter test contexts.
    try:
        from backend.game_logic.diplomatic_templates import (
            resolve_settlement_voice_line,
        )
    except Exception:
        return fallback
    awe_tags = list(event.get("awe_tags") or [])
    # `standing_summary` keeps the "+N more" overflow signal so the
    # presentation cap on named participants survives the Voice Bible
    # rewrap.
    standing_summary = who
    contribution_summary = f"reactions from {len(reactions)} courts" if reactions else ""
    top_blocker = head_term if not awe_tags else (
        f"{head_term} ({', '.join(_awe_tag_display(t) for t in awe_tags)})"
    )
    template_key = _voice_summary_template_key(event)
    voiced = resolve_settlement_voice_line(
        template_key,
        war_label=war_label,
        standing_summary=standing_summary,
        contribution_summary=contribution_summary,
        top_blocker=top_blocker,
        restored_claim=head_term,
        limited_concession=head_term,
    )
    return voiced or fallback


def compose_digest_oneliner(event: Mapping[str, Any]) -> str:
    """Spec §11.6 line 1288 digest one-liner.

    Routes through the Voice Bible §16.1
    `settlement_aftermath_digest_talleyrand` template when available.
    Falls back to a generic templated string. The fallback no longer
    leaks the raw `war_id` to the player; it uses the event's
    `war_label` when populated.
    """
    hidden = int(event.get("hidden_reaction_count", 0) or 0)
    war_id = str(event.get("war_id", "") or "war")
    war_label = str(event.get("war_label", "") or war_id)
    fallback = (
        f"{hidden} additional courts register the settlement aftermath "
        f"({war_label})."
    )
    try:
        from backend.game_logic.diplomatic_templates import (
            resolve_settlement_voice_line,
        )
    except Exception:
        return fallback
    voiced = resolve_settlement_voice_line(
        "settlement_aftermath_digest_talleyrand",
        hidden_count=hidden,
        war_label=war_label,
    )
    return voiced or fallback


# ---------------------------------------------------------------------------
# Top-N cap + digest overflow
# ---------------------------------------------------------------------------


def cap_settlement_dispatch_lines(
    rendered_lines: Sequence[Mapping[str, Any]],
    *,
    cap: int = SETTLEMENT_PRIMARY_BEAT_CAP,
) -> Tuple[List[Dict[str, Any]], int]:
    """Apply the spec §11.6 line 1279 top-four cap to settlement-family
    dispatch lines.

    Input is the already-rendered settlement lines (each shape
    `{type, text, priority, ...}`). Returns ``(kept, hidden_count)``
    where `kept` is at most `cap` lines and `hidden_count` is the
    number of lines that overflowed. Caller (dispatch.py) uses
    ``hidden_count`` to either upgrade the digest's
    ``hidden_reaction_count`` or to drop a generated overflow line.
    Non-settlement lines are passed through unchanged at the caller.
    """
    if cap < 0:
        cap = 0
    lines = [dict(line) for line in rendered_lines if isinstance(line, Mapping)]
    if len(lines) <= cap:
        return lines, 0
    return lines[:cap], len(lines) - cap


# ---------------------------------------------------------------------------
# Warning cap (spec §16.3)
# ---------------------------------------------------------------------------


_WARNING_SEVERITY_RANK = {
    "HARD_STOP": 0,
    "WARNING": 1,
    "INFO": 2,
}


def _warning_sort_key(warning: Mapping[str, Any]) -> Tuple[int, int, str]:
    severity = str(warning.get("severity", "INFO")).upper()
    salience = int(warning.get("salience", 0) or 0)
    code = str(warning.get("code", "") or "")
    # Sort: severity rank ascending, salience descending, code ascending.
    return (_WARNING_SEVERITY_RANK.get(severity, 99), -salience, code)


def apply_warning_cap(
    warnings: Sequence[Mapping[str, Any]],
    *,
    inline_warning_cap: int = SETTLEMENT_INLINE_WARNING_CAP,
) -> Dict[str, List[Dict[str, Any]]]:
    """Spec §16.3 — split warnings into inline + overflow.

    All HARD_STOP warnings are inline (not capped). The next
    ``inline_warning_cap`` WARNING-severity rows go inline. Everything
    else (additional WARNINGs and all INFO rows) goes behind "View all
    concerns".
    """
    sorted_warnings = sorted(
        (dict(w) for w in warnings or [] if isinstance(w, Mapping)),
        key=_warning_sort_key,
    )
    inline: List[Dict[str, Any]] = []
    overflow: List[Dict[str, Any]] = []
    warning_count = 0
    for w in sorted_warnings:
        severity = str(w.get("severity", "INFO")).upper()
        if severity == "HARD_STOP":
            inline.append(w)
            continue
        if severity == "WARNING" and warning_count < inline_warning_cap:
            inline.append(w)
            warning_count += 1
            continue
        overflow.append(w)
    return {"inline": inline, "overflow": overflow}


# ---------------------------------------------------------------------------
# Awe set-piece tagging (spec §20.8)
# ---------------------------------------------------------------------------


_AWE_TRIPLE_FORCED_THRESHOLD = 3
_AWE_BIG_FORCED_THREAT_DELTA = 30


def detect_awe_set_pieces(
    *,
    settlement_terms: Sequence[Mapping[str, Any]],
    participant_reactions: Sequence[Mapping[str, Any]],
    balance_projection: Mapping[str, Any] | None = None,
    proposer_side: str = "",
) -> List[str]:
    """Tag a ratification with awe set pieces per spec §20.8.

    Returns a list of tag strings; multiple tags can apply to a single
    ratification. The tags are presentation-only — they let dispatch /
    campaign log / notification rail decide whether to upgrade priority
    or call out the moment with copy.
    """
    tags: List[str] = []
    forced_alliance_count = 0
    bargain_fulfilled = False
    bargain_breached = False
    rewarded = False
    shut_out_major = False
    territory_returns = 0
    forced_threat_delta = 0
    crossed_threshold = False

    for term in settlement_terms or []:
        if not isinstance(term, Mapping):
            continue
        ttype = term.get("type")
        if ttype == "forced_alliance":
            forced_alliance_count += 1
            forced_threat_delta += int(
                term.get("projected_threat_delta", 15) or 15
            )
        elif ttype == "territory_return" or ttype == "occupation_return":
            territory_returns += 1
        elif ttype == "bargain_fulfilled" or ttype == "bargain_claim_awarded":
            bargain_fulfilled = True

    for reaction in participant_reactions or []:
        if not isinstance(reaction, Mapping):
            continue
        kind = reaction.get("kind", "")
        if kind == "ally_rewarded":
            rewarded = True
        elif kind == "ally_shut_out":
            severity = str(reaction.get("severity", ""))
            if severity == "major_shut_out":
                shut_out_major = True
        elif kind == "bargain_breach_at_settlement":
            bargain_breached = True
        elif kind == "bargain_fulfilled_at_settlement":
            bargain_fulfilled = True

    if balance_projection and isinstance(balance_projection, Mapping):
        crossed = balance_projection.get("crossed_thresholds")
        if isinstance(crossed, Iterable):
            for threshold in crossed:
                if threshold:
                    crossed_threshold = True
                    break

    if (
        forced_alliance_count >= _AWE_TRIPLE_FORCED_THRESHOLD
        or forced_threat_delta >= _AWE_BIG_FORCED_THREAT_DELTA
    ):
        tags.append("triple_forced_alignment")
        if crossed_threshold:
            tags.append("balance_of_europe_crossing")

    if bargain_fulfilled and (rewarded or shut_out_major):
        tags.append("tilsit_bargain_and_betrayal")
    if bargain_breached and shut_out_major:
        tags.append("tilsit_bargain_and_betrayal")

    if proposer_side == "defenders" and territory_returns > 0:
        tags.append("defensive_coalition_preservation")

    return tags


# ---------------------------------------------------------------------------
# SC-15 / SC-16: live preview enrichment helpers
# ---------------------------------------------------------------------------


def build_applied_clauses_preview(
    settlement_terms: Sequence[Mapping[str, Any]] | None,
) -> List[Dict[str, Any]]:
    """SC-15 mutation preview: structurally equal to the actual ratification
    mutation set per clause.

    Each row carries clause type, clause-specific value fields (region,
    payer, recipient, amount, turns, includes_continental_system,
    forced-alliance imposer/target, vassalage lord/vassal, liberation
    target), and a humanized display label. The frontend renders this
    list so the player can read what will mutate before pressing Ratify.

    The preview is structurally aligned with `_apply_settlement_terms`
    in `settlement_preview.py`; consumers MUST treat clause-specific
    value fields as load-bearing (a SC-15 test asserts equality with
    the post-ratification `applied_clauses` list).
    """
    rows: List[Dict[str, Any]] = []
    for term in settlement_terms or []:
        if not isinstance(term, Mapping):
            continue
        ttype = str(term.get("type") or "")
        row: Dict[str, Any] = {
            "type": ttype,
            "type_display": clause_display_name(ttype) if ttype else "Settlement term",
            "display_label": _term_display(term),
        }
        # Clause-specific value fields. The set of carried fields per
        # clause type matches the SC-15 amendment list: clause, region,
        # payer, recipient, dependency target, amount, turns,
        # includes_continental_system, threat delta, pair-state
        # transition.
        if ttype == "territory_cede":
            row["from"] = str(term.get("from") or "")
            row["to"] = str(term.get("to") or "")
            row["regions"] = list(term.get("regions") or [])
        elif ttype == "gold_lump" or ttype == "gold_indemnity":
            row["from"] = str(term.get("from") or term.get("payer") or "")
            row["to"] = str(term.get("to") or term.get("recipient") or "")
            row["amount"] = int(term.get("amount") or 0)
        elif ttype == "gold_per_turn":
            row["from"] = str(term.get("from") or term.get("payer") or "")
            row["to"] = str(term.get("to") or term.get("recipient") or "")
            row["amount"] = int(term.get("amount") or 0)
            row["turns"] = int(term.get("turns") or 0)
        elif ttype == "forced_alliance":
            row["from"] = str(term.get("from") or "")
            row["to"] = str(term.get("to") or "")
            row["includes_continental_system"] = bool(
                term.get("includes_continental_system", True)
            )
            row["projected_threat_delta"] = int(
                term.get("projected_threat_delta", 15) or 15
            )
            row["pair_state_transition"] = "WAR -> ALLIANCE"
        elif ttype == "vassalage" or ttype == "subjugation":
            row["vassal"] = str(term.get("vassal_nation") or term.get("from") or "")
            row["overlord"] = str(term.get("overlord") or term.get("to") or "")
            row["from"] = row["vassal"]
            row["to"] = row["overlord"]
            row["pair_state_transition"] = "WAR -> VASSALAGE"
        elif ttype == "liberation":
            row["target"] = str(term.get("target") or term.get("vassal_nation") or term.get("from") or "")
            row["vassal_nation"] = row["target"]
            row["lord"] = str(term.get("lord") or term.get("overlord") or term.get("lord_nation") or term.get("to") or "")
            row["lord_nation"] = row["lord"]
            row["liberator"] = str(term.get("liberator") or term.get("to") or "")
            row["pair_state_transition"] = "VASSALAGE -> SOVEREIGN"
        elif ttype == "peace":
            row["pair_state_transition"] = "WAR -> PEACE"
        else:
            # Unknown / future canonical types — keep raw fields so
            # diagnostic display never silently drops data.
            for key in ("from", "to", "amount", "turns", "regions"):
                if key in term:
                    row[key] = term[key]
        rows.append(row)
    return rows


def build_beneficiaries_preview(
    contribution_rows: Sequence[Mapping[str, Any]] | None,
    applied_clauses_preview: Sequence[Mapping[str, Any]] | None,
    proposer_side: str = "",
    accepting_side: str = "",
) -> List[Dict[str, Any]]:
    """SC-15: explicit beneficiaries of the settlement with reason.

    A nation is a beneficiary if (a) the contribution-share ledger
    flagged it as `is_beneficiary=True` (rewarded standing), or (b) any
    applied clause names it as recipient (gold), to-side of a territory
    cede, overlord of a new vassalage, or imposer of a forced alliance.
    The reason captures the clause type / contribution standing so the
    player can read who gained and why before ratification.
    """
    by_nation: Dict[str, Dict[str, Any]] = {}

    def _record(nation: str, reason: str) -> None:
        n = str(nation or "").strip()
        if not n:
            return
        entry = by_nation.setdefault(n, {"nation": n, "reasons": []})
        if reason and reason not in entry["reasons"]:
            entry["reasons"].append(reason)

    for row in contribution_rows or []:
        if not isinstance(row, Mapping):
            continue
        nation = str(row.get("nation") or "")
        if not nation:
            continue
        if bool(row.get("is_beneficiary") or False):
            standing = str(row.get("standing") or row.get("standing_display") or "rewarded")
            _record(nation, f"Rewarded ({standing})")

    for clause in applied_clauses_preview or []:
        if not isinstance(clause, Mapping):
            continue
        ttype = str(clause.get("type") or "")
        if ttype == "territory_cede":
            _record(clause.get("to", ""), "Receives ceded territory")
        elif ttype in ("gold_lump", "gold_indemnity", "gold_per_turn"):
            _record(clause.get("to", ""), "Receives gold")
        elif ttype == "forced_alliance":
            _record(clause.get("to", ""), "Imposes forced alliance")
        elif ttype in ("vassalage", "subjugation"):
            _record(clause.get("overlord", ""), "Gains vassal")
        elif ttype == "liberation":
            _record(clause.get("target", "") or clause.get("vassal_nation", ""), "Liberated from vassalage")
    return list(by_nation.values())


def build_shut_out_allies_preview(
    contribution_rows: Sequence[Mapping[str, Any]] | None,
    warnings: Sequence[Mapping[str, Any]] | None,
    proposer_side: str = "",
) -> List[Dict[str, Any]]:
    """SC-15: explicit shut-out / ignored coalition members preview.

    A same-side ally is shut out when the contribution ledger marks
    `standing == "no_standing"` (or equivalent ignored token) while
    `contribution > 0`, OR a warning of kind `ally_shut_out` already
    fired during preview. The preview is a player-readable list of
    nation + standing + contribution summary; downstream presentation
    uses it to render an `Ignored allies` chip group.
    """
    rows: List[Dict[str, Any]] = []
    seen: set = set()
    for row in contribution_rows or []:
        if not isinstance(row, Mapping):
            continue
        nation = str(row.get("nation") or "")
        if not nation or nation in seen:
            continue
        if proposer_side and str(row.get("side") or "") != proposer_side:
            continue
        if bool(row.get("is_leader") or False) or bool(row.get("is_beneficiary") or False):
            continue
        standing = str(row.get("standing") or "")
        contribution_share = float(row.get("contribution_share") or row.get("contribution") or 0)
        if standing in ("no_standing", "ignored", "shut_out") and contribution_share > 0:
            rows.append({
                "nation": nation,
                "standing": standing,
                "standing_display": _standing_display(standing),
                "contribution_share": contribution_share,
                "reason_display": "Shut out after contribution",
            })
            seen.add(nation)
    for warning in warnings or []:
        if not isinstance(warning, Mapping):
            continue
        kind = str(warning.get("kind") or warning.get("category") or "")
        if kind != "ally_shut_out":
            continue
        nation = str(warning.get("nation") or warning.get("ally") or "")
        if not nation or nation in seen:
            continue
        if proposer_side and str(warning.get("side") or warning.get("ally_side") or proposer_side) != proposer_side:
            continue
        rows.append({
            "nation": nation,
            "standing": "shut_out",
            "standing_display": _standing_display("shut_out"),
            "contribution_share": float(warning.get("contribution_share") or 0),
            "reason_display": str(warning.get("detail") or "Shut out at settlement"),
        })
        seen.add(nation)
    return rows


def build_third_party_reaction_preview(
    settlement_terms: Sequence[Mapping[str, Any]] | None,
    shut_out_allies: Sequence[Mapping[str, Any]] | None,
    forced_alliance_threat_preview: Mapping[str, Any] | None,
) -> List[Dict[str, Any]]:
    """SC-15 third-party reaction preview.

    Surfaces *projected* commitment grievances, shut-out ally grievance
    notices, threat deltas, and notification beats that the player
    should expect to fire AFTER ratification. The preview is a
    deterministic projection — callers must not rely on it to mutate
    state. Each row carries `kind` and a humanized `display` so the
    popup, dispatch preview, and ledger preview all read the same
    contract.
    """
    rows: List[Dict[str, Any]] = []
    for ally in shut_out_allies or []:
        if not isinstance(ally, Mapping):
            continue
        nation = str(ally.get("nation") or "")
        if not nation:
            continue
        rows.append({
            "kind": "shut_out_ally_grievance",
            "nation": nation,
            "display": f"{nation} will record a shut-out grievance",
        })
    for term in settlement_terms or []:
        if not isinstance(term, Mapping):
            continue
        ttype = str(term.get("type") or "")
        if ttype == "forced_alliance":
            target = str(term.get("from") or "")
            imposer = str(term.get("to") or "")
            if target and imposer:
                rows.append({
                    "kind": "forced_alliance_grievance_projection",
                    "nation": target,
                    "display": (
                        f"{target} will resent the forced alliance imposed by {imposer}"
                    ),
                })
    if forced_alliance_threat_preview and isinstance(forced_alliance_threat_preview, Mapping):
        delta = int(forced_alliance_threat_preview.get("projected_threat_delta") or 0)
        crossed = list(forced_alliance_threat_preview.get("crossed_thresholds") or [])
        if delta:
            rows.append({
                "kind": "coalition_threat_delta",
                "delta": delta,
                "display": (
                    f"Coalition threat shifts by {delta:+d} after ratification"
                ),
            })
        for threshold in crossed:
            if not threshold:
                continue
            display = str(threshold).replace("_", " ").capitalize()
            rows.append({
                "kind": "coalition_threat_threshold_crossed",
                "threshold": str(threshold),
                "display": (
                    f"Coalition threshold crossed: {display}"
                ),
            })
    return rows


def build_forced_alliance_threat_preview_display(
    threat_preview: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    """SC-16: humanize the `compute_forced_alliance_threat_preview`
    output for popup / tooltip / ledger consumers.

    Returns the same numeric shape (forced_alliance_clauses, current_
    threat, projected_threat, projected_threat_delta, crossed_thresholds)
    plus a `display` string and a `crossed_threshold_displays` list so
    the player surface never re-renders raw threshold tokens.
    """
    if not threat_preview or not isinstance(threat_preview, Mapping):
        return {}
    clauses = int(threat_preview.get("forced_alliance_clauses") or 0)
    delta = int(threat_preview.get("projected_threat_delta") or 0)
    current = int(threat_preview.get("current_threat") or 0)
    projected = int(threat_preview.get("projected_threat") or 0)
    crossed_raw = list(threat_preview.get("crossed_thresholds") or [])
    crossed_display = [
        str(t).replace("_", " ").capitalize() for t in crossed_raw if t
    ]
    if clauses == 0:
        return {
            "forced_alliance_clauses": 0,
            "current_threat": current,
            "projected_threat": projected,
            "projected_threat_delta": 0,
            "crossed_thresholds": [],
            "crossed_threshold_displays": [],
            "display": "",
        }
    base = (
        f"Forced alliance: coalition threat {current} → {projected} ({delta:+d})"
    )
    if crossed_display:
        base += f"; crosses {', '.join(crossed_display)}"
    return {
        "forced_alliance_clauses": clauses,
        "current_threat": current,
        "projected_threat": projected,
        "projected_threat_delta": delta,
        "crossed_thresholds": crossed_raw,
        "crossed_threshold_displays": crossed_display,
        "display": base,
    }


# ---------------------------------------------------------------------------
# Sectioned settlement review payload (spec §16.2)
# ---------------------------------------------------------------------------


_DENSITY_TERMS = {
    "compact": 3,
    "medium": 5,
    "verbose": -1,  # unlimited
}
_DENSITY_ALLIES = {
    "compact": 3,
    "medium": SETTLEMENT_STANDING_ROW_CAP,
    "verbose": -1,
}


def _slice_for_density(
    rows: Sequence[Mapping[str, Any]], density: str, density_table: Mapping[str, int],
) -> Tuple[List[Dict[str, Any]], int]:
    cap = density_table.get(density, density_table.get("medium", 5))
    rows_list = [dict(r) for r in rows or [] if isinstance(r, Mapping)]
    if cap < 0 or len(rows_list) <= cap:
        return rows_list, 0
    return rows_list[:cap], len(rows_list) - cap


def build_settlement_review(
    *,
    war_id: str,
    war_label: str,
    proposer_side: str,
    accepting_side: str,
    covered_enemy_participants: Sequence[str],
    terms: Sequence[Mapping[str, Any]],
    allies: Sequence[Mapping[str, Any]],
    warnings: Sequence[Mapping[str, Any]],
    acceptance: Mapping[str, Any] | None,
    density: str = "compact",
    awe_tags: Sequence[str] = (),
    forced_alliance_threat_preview: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Sectioned settlement review payload per spec §16.2 line 1636.

    Sections: Terms / Allies / Warnings / Acceptance. Each section is
    independently renderable so the Godot surface can split into tabs,
    segmented controls, or stacked collapsible sections without forcing
    the renderer to flatten a 6-8 participant payload into one wall of
    text. Density=`compact` is the first attempt for 6+ participants;
    fall back to `medium` if compact hides too much; `verbose` is the
    debug/reviewer expansion.
    """
    if density not in _DENSITY_TERMS:
        density = "compact"

    enriched_terms = [_enrich_term_row(t) for t in terms]
    if not enriched_terms:
        enriched_terms = [{"type": "peace", "type_display": "Peace", "display_label": "End hostilities"}]
    enriched_allies = [_enrich_ally_row(a) for a in allies]
    enriched_warnings = [_enrich_warning_row(w) for w in warnings]
    terms_inline, terms_overflow = _slice_for_density(enriched_terms, density, _DENSITY_TERMS)
    allies_inline, allies_overflow = _slice_for_density(enriched_allies, density, _DENSITY_ALLIES)
    warning_cap = 1 if density == "compact" else SETTLEMENT_INLINE_WARNING_CAP
    warning_split = apply_warning_cap(
        enriched_warnings,
        inline_warning_cap=warning_cap,
    )

    acceptance_payload: Dict[str, Any] = {}
    if acceptance and isinstance(acceptance, Mapping):
        band_code = str(acceptance.get("band", acceptance.get("verdict", "near_acceptable"))).lower()
        # SC-15b: structurally blocked acceptance must omit numeric
        # total/threshold so popup, tooltip, ledger, and dispatch never
        # render `0 / 50 - Blocked` (which reads like a tunable score
        # gap rather than a hard impossibility). Every surface reads the
        # same payload contract.
        if band_code == "blocked":
            acceptance_payload = {
                "total": None,
                "threshold": None,
                "band": "blocked",
                "top_components": list(acceptance.get("top_components") or [])[:3],
            }
        else:
            acceptance_payload = {
                "total": int(acceptance.get("total", acceptance.get("score", 0)) or 0),
                "threshold": int(acceptance.get("threshold", 50) or 50),
                "band": band_code,
                "top_components": list(acceptance.get("top_components") or [])[:3],
            }
        acceptance_payload["band_display"] = _acceptance_band_display(acceptance_payload["band"])
        # SC-15b: surface a humanized blocker display alongside the
        # band_display=Blocked tag so popup/tooltip/ledger/dispatch can
        # show the reason without re-rendering numeric copy.
        if band_code == "blocked":
            blocker_display = ""
            hard_stops = list(acceptance.get("hard_stops") or [])
            if hard_stops:
                first = hard_stops[0]
                if isinstance(first, Mapping):
                    blocker_display = str(first.get("display") or first.get("detail") or first.get("code") or "")
                else:
                    blocker_display = str(first or "")
            if not blocker_display:
                feedback = list(acceptance.get("feedback") or [])
                if feedback:
                    head = feedback[0]
                    blocker_display = str(head.get("display", "") if isinstance(head, Mapping) else head or "")
            acceptance_payload["blocker_display"] = blocker_display or "A hard condition blocks this settlement."
        if not acceptance_payload["top_components"] and acceptance.get("feedback"):
            acceptance_payload["top_components"] = list(acceptance.get("feedback") or [])[:3]
        if density == "verbose":
            acceptance_payload["debug_components"] = list(
                acceptance.get("debug_components") or []
            )

    # Compute uncovered enemy participants — opposing-side allies that
    # this settlement does NOT resolve. Surfaced as "Still at war: …" in
    # the confirm popup so multi-enemy partial settlements show who
    # remains hostile after ratification.
    covered_set = {str(n) for n in (covered_enemy_participants or []) if n}
    uncovered_chips: List[str] = []
    for ally in enriched_allies:
        if not isinstance(ally, Mapping):
            continue
        nation = str(ally.get("nation", "") or "")
        ally_side = str(ally.get("side", "") or "")
        if not nation or nation in covered_set:
            continue
        if accepting_side and ally_side and ally_side != accepting_side:
            continue
        uncovered_chips.append(nation)

    # SC-15 / SC-16: live preview enrichment. Each helper returns a
    # structurally stable list; callers (popup, dispatch preview,
    # ledger, tooltips) read from the same payload contract.
    applied_clauses_preview = build_applied_clauses_preview(terms)
    beneficiaries_preview = build_beneficiaries_preview(
        contribution_rows=allies,
        applied_clauses_preview=applied_clauses_preview,
        proposer_side=proposer_side,
        accepting_side=accepting_side,
    )
    shut_out_allies_preview = build_shut_out_allies_preview(
        contribution_rows=allies,
        warnings=warnings,
        proposer_side=proposer_side,
    )
    forced_alliance_threat_display = build_forced_alliance_threat_preview_display(
        forced_alliance_threat_preview,
    )
    third_party_reaction_preview = build_third_party_reaction_preview(
        settlement_terms=terms,
        shut_out_allies=shut_out_allies_preview,
        forced_alliance_threat_preview=forced_alliance_threat_preview,
    )

    return {
        "war_id": war_id,
        "war_label": war_label,
        "proposer_side": proposer_side,
        "accepting_side": accepting_side,
        "covered_enemy_participants": list(covered_enemy_participants or []),
        "covered_enemy_display_chips": list(covered_enemy_participants or []),
        "uncovered_enemy_display_chips": uncovered_chips,
        "coverage_scope_display": (
            "Whole-war settlement" if len(covered_enemy_participants or []) > 1
            else "Separate settlement"
        ),
        "war_scope_display": (
            "Whole war" if len(covered_enemy_participants or []) > 1 else "Bilateral war"
        ),
        "density": density,
        "sections": {
            "terms": {
                "rows": terms_inline,
                "overflow_count": terms_overflow,
            },
            "allies": {
                "rows": allies_inline,
                "overflow_count": allies_overflow,
            },
            "warnings": {
                "inline": warning_split["inline"],
                "overflow": warning_split["overflow"],
            },
            "acceptance": acceptance_payload,
        },
        "awe_tags": list(awe_tags),
        "awe_tag_displays": [_awe_tag_display(tag) for tag in awe_tags],
        # SC-15: structural mutation preview + beneficiaries + shut-out
        # allies + third-party reaction preview. SC-16: forced-alliance
        # threat projection display sits next to the threat data so the
        # popup never has to re-call the helper itself.
        "applied_clauses_preview": applied_clauses_preview,
        "beneficiaries_preview": beneficiaries_preview,
        "shut_out_allies_preview": shut_out_allies_preview,
        "third_party_reaction_preview": third_party_reaction_preview,
        "forced_alliance_threat_preview": forced_alliance_threat_display,
    }


# ---------------------------------------------------------------------------
# F2: Event → sectioned review (Slice E gate line 392)
# ---------------------------------------------------------------------------


# Spec §11.6 — participant_reaction kinds that surface as warnings on the
# sectioned settlement review. `ally_shut_out` with `severity="major"` is
# escalated to HARD_STOP so the warning cap inlines it unconditionally.
_REVIEW_WARNING_KINDS: frozenset = frozenset({
    "ally_shut_out",
    "enemy_sold_out",
    "bargain_breach_at_settlement",
    "cross_war_rival_strengthened",
})

_POLITICAL_WARNING_SALIENCE: Dict[str, int] = {
    "bargain_breach_at_settlement": 100,
    "enemy_sold_out": 90,
    "ally_shut_out": 85,
    "cross_war_rival_strengthened": 70,
}


_REACTION_NATION_FIELDS: Tuple[str, ...] = (
    "nation",
    "burdened_participant",
    "victim",
    "ally",
    "breaker",
    "recipient",
    "beneficiary",
    "promiser",
)


def _reaction_nation(reaction: Mapping[str, Any]) -> str:
    """First non-empty nation-bearing field on a reaction record."""
    for field in _REACTION_NATION_FIELDS:
        value = reaction.get(field)
        if isinstance(value, str) and value:
            return value
    return ""


def _reaction_warning_detail(kind: str, reaction: Mapping[str, Any]) -> str:
    """Player-facing one-clause description for a reaction warning row.

    Pulls from kind-specific fields so the inline expansion names *who*
    and *what*, not just the reaction code. Falls back to any
    pre-populated `detail` string the orchestrator wrote.
    """
    pre = str(reaction.get("detail", "") or "")
    if pre:
        return pre
    nation = _reaction_nation(reaction)
    if kind == "enemy_sold_out":
        burdens = list(reaction.get("burdens") or [])
        leader = str(reaction.get("leader", "") or "")
        burden_str = ", ".join(b.replace("_", " ") for b in burdens) if burdens else "the terms"
        if leader and nation:
            return f"{nation} burdened with {burden_str} by {leader}"
        if nation:
            return f"{nation} burdened with {burden_str}"
        return burden_str
    if kind == "ally_shut_out":
        leader = str(reaction.get("leader", "") or "")
        if leader and nation:
            return f"{nation} shut out by {leader}"
        if nation:
            return f"{nation} shut out of settlement"
        return "ally shut out of settlement"
    if kind == "bargain_breach_at_settlement":
        breaker = str(reaction.get("breaker", "") or "")
        promiser = str(reaction.get("promiser", "") or "")
        actor = breaker or promiser
        if actor and nation:
            return f"{actor} breached bargain owed to {nation}"
        if nation:
            return f"bargain owed to {nation} breached"
        return "bargain breached at settlement"
    if kind == "cross_war_rival_strengthened":
        rivals = list(reaction.get("rival_strengthened") or [])
        if nation and rivals:
            return f"{nation} sees rival strengthened: {', '.join(rivals)}"
        if nation:
            return f"{nation} sees rival strengthened"
        return "rival strengthened by settlement"
    return nation or kind.replace("_", " ")


def _warning_severity_for_reaction(_reaction: Mapping[str, Any]) -> str:
    """Map a reaction record onto §16.3 severity (HARD_STOP/WARNING/INFO).

    These are post-ratification political consequences, not validity
    blockers. Spec §16.4 reserves HARD_STOP for impossible/contradictory
    settlement shapes; reaction rows stay WARNING and rely on salience to
    keep promise breach / major fallout ahead of generic concerns.
    """
    return "WARNING"


def _warning_salience_for_reaction(reaction: Mapping[str, Any]) -> int:
    kind = str(reaction.get("kind", ""))
    base = _POLITICAL_WARNING_SALIENCE.get(kind, 50)
    score = reaction.get("severity_score")
    try:
        if score is not None:
            base += min(10, max(0, int(score)))
    except (TypeError, ValueError):
        pass
    explicit = str(reaction.get("severity", "")).lower()
    if explicit in {"major", "major_shut_out"}:
        base += 10
    raw = reaction.get("salience")
    try:
        if raw is not None:
            base = max(base, int(raw))
    except (TypeError, ValueError):
        pass
    return min(100, base)


def build_settlement_review_from_event(
    event: Mapping[str, Any],
    *,
    density: str = "compact",
    world: Any | None = None,
) -> Dict[str, Any]:
    """Reconstruct a sectioned settlement review from a logged event.

    Bridges the post-ratification `settlement_summary` event into the
    spec §16.2 Terms / Allies / Warnings / Acceptance section payload so
    the diplomatic ledger Recent Settlements block can render an inline
    deep-link expansion. The acceptance score is not preserved on the
    event log, so the acceptance section returns empty for archived
    events; live `/diplomatic_preview` callers should keep using
    `build_settlement_review` directly with the live preview's
    acceptance payload.

    `world` is consumed only to derive a friendly war label when the
    event payload is missing one (older events from before the
    presentation hardening).
    """
    if not isinstance(event, Mapping):
        return {}
    if str(event.get("type", "")) != "settlement_summary":
        return {}

    proposer_members = list(event.get("proposer_members") or [])
    accepting_members = list(event.get("accepting_members") or [])
    participant_reactions = list(event.get("participant_reactions") or [])
    proposer_leader = str(event.get("proposer_leader", "") or "")
    accepting_leader = str(event.get("accepting_leader", "") or "")
    attacker_leader = str(event.get("attacker_leader", "") or "")
    defender_leader = str(event.get("defender_leader", "") or "")
    leader_set: set = {
        n for n in (proposer_leader, accepting_leader,
                    attacker_leader, defender_leader) if n
    }

    rewarded: set = set()
    for reaction in participant_reactions:
        if not isinstance(reaction, Mapping):
            continue
        if str(reaction.get("kind", "")) != "ally_rewarded":
            continue
        nation = _reaction_nation(reaction)
        if nation:
            rewarded.add(nation)

    proposer_members_set: set = {n for n in proposer_members if isinstance(n, str)}
    allies: List[Dict[str, Any]] = []
    seen: set = set()
    for nation in proposer_members + accepting_members:
        if not isinstance(nation, str) or not nation or nation in seen:
            continue
        seen.add(nation)
        side = "attackers" if nation in proposer_members_set and event.get("proposer_side") == "attackers" else (
            "defenders" if nation in proposer_members_set and event.get("proposer_side") == "defenders" else (
                "defenders" if event.get("proposer_side") == "attackers" else "attackers"
            )
        )
        allies.append({
            "nation": nation,
            "side": side,
            "side_label": side_label_display(side),
            "standing": "leader" if nation in leader_set else "consult",
            "material_share": 0.0,
            "is_leader": nation in leader_set,
            "is_beneficiary": nation in rewarded,
        })

    warnings: List[Dict[str, Any]] = []
    for reaction in participant_reactions:
        if not isinstance(reaction, Mapping):
            continue
        kind = str(reaction.get("kind", ""))
        if kind not in _REVIEW_WARNING_KINDS:
            continue
        severity = _warning_severity_for_reaction(reaction)
        warnings.append({
            "severity": severity,
            "code": kind,
            "salience": _warning_salience_for_reaction(reaction),
            "nation": _reaction_nation(reaction),
            "detail": _reaction_warning_detail(kind, reaction),
        })

    war_id = str(event.get("war_id", "") or "")
    war_label = str(event.get("war_label", "") or "")
    if not war_label:
        war_label = _war_label(world, war_id) if world is not None else (war_id or "war")

    return build_settlement_review(
        war_id=war_id,
        war_label=war_label,
        proposer_side=str(event.get("proposer_side", "") or ""),
        accepting_side=str(event.get("accepting_side", "") or ""),
        covered_enemy_participants=list(
            event.get("covered_enemy_participants") or []
        ),
        terms=list(event.get("applied_clauses") or []),
        allies=allies,
        warnings=warnings,
        acceptance=event.get("acceptance_snapshot") or None,
        density=density,
        awe_tags=list(event.get("awe_tags") or []),
    )


# ---------------------------------------------------------------------------
# Recent settlement summaries (ledger view)
# ---------------------------------------------------------------------------


def recent_settlement_summaries(
    world: Any,
    player_nation: str,
    *,
    limit: int = SETTLEMENT_LEDGER_DEFAULT_ROWS,
) -> List[Dict[str, Any]]:
    """Return the most recent fog-visible `settlement_summary` events.

    Used by the diplomatic ledger to render a "Recent Settlements"
    section. Each row carries the route metadata so the ledger can
    deep-link into a settlement review when the war is still active.
    """
    out: List[Dict[str, Any]] = []
    event_log = list(getattr(world, "event_log", []) or [])
    for event in reversed(event_log):
        if not isinstance(event, Mapping):
            continue
        if str(event.get("type", "")) != "settlement_summary":
            continue
        if not is_settlement_event_visible(event, world, player_nation):
            continue
        review_target = settlement_review_target(event, world=world)
        reactions = list(event.get("participant_reactions") or [])
        named: List[str] = []
        for reaction in reactions:
            if not isinstance(reaction, Mapping):
                continue
            name = _participant_display(reaction)
            if name and name not in named:
                named.append(name)
            if len(named) >= SETTLEMENT_ONELINER_PARTICIPANT_CAP:
                break
        more = max(0, len(reactions) - len(named))
        out.append({
            "war_id": str(event.get("war_id", "") or ""),
            "turn": int(event.get("turn", 0) or 0),
            "headline": compose_summary_oneliner(event, world=world),
            "terms_summary": [
                _humanize_term(str(term))
                for term in list(event.get("terms_summary") or [])
            ],
            "covered_enemy_participants": list(
                event.get("covered_enemy_participants") or []
            ),
            "named_reactions": named,
            "additional_reaction_count": more,
            "war_ended": bool(event.get("war_ended", False)),
            "review_target": review_target,
            "route_id": str((event.get("route") or {}).get("route_id", "") or ""),
            "awe_tags": list(event.get("awe_tags") or []),
            "awe_tag_displays": [
                _awe_tag_display(tag)
                for tag in list(event.get("awe_tags") or [])
            ],
            # F2: sectioned Terms/Allies/Warnings/Acceptance payload for
            # the inline expansion in the Recent Settlements block. Empty
            # acceptance section is expected since the post-ratification
            # event does not preserve the acceptance score.
            "review_sections": build_settlement_review_from_event(
                event, density="compact", world=world,
            ),
        })
        if len(out) >= limit:
            break
    return out


# ---------------------------------------------------------------------------
# SC-23: Merged PEACE & SETTLEMENT HISTORY surface
# ---------------------------------------------------------------------------


def _participants_signature(*nations: str) -> str:
    cleaned = sorted({str(n) for n in nations if n})
    return "-".join(cleaned) if cleaned else "unknown"


def _bilateral_peace_route_id(entry: Mapping[str, Any], seq: int) -> str:
    target = str(entry.get("target_nation") or "")
    proposer = str(entry.get("actor_nation") or entry.get("proposer_nation") or "France")
    turn = int(entry.get("turn", 0) or 0)
    sig = _participants_signature(target, proposer)
    return f"{PEACE_HISTORY_BILATERAL_NAMESPACE}:{sig}:{turn}:{seq}"


def build_peace_settlement_history(
    world: Any,
    player_nation: str,
    *,
    limit: int = PEACE_HISTORY_DEFAULT_ROWS,
) -> List[Dict[str, Any]]:
    """SC-23: merged reverse-chronological PEACE & SETTLEMENT HISTORY.

    Returns one mixed list of common-peace `settlement_summary` rows and
    bilateral peace ratification rows ordered by turn (descending), then
    seq within turn. Per-war dedup is OFF — every ratification event is
    its own row. Settlement rows preserve `settlement:{...}` route ids;
    bilateral peace rows mint `peace:{participants_signature}:{turn}:{seq}`
    ids so route focus cannot collide.

    Each row carries a `row_type` tag (`"settlement"` / `"bilateral_peace"`)
    so the diplomatic ledger and dispatch can render type pills without
    re-classifying the rows themselves.
    """
    rows: List[Dict[str, Any]] = []

    entries = list(getattr(world, "peace_ratification_log", []) or [])
    settlement_rows = recent_settlement_summaries(
        world, player_nation, limit=max(limit, limit + len(entries)),
    )
    for row in settlement_rows:
        merged = dict(row)
        merged["row_type"] = "settlement"
        merged["row_type_display"] = "Settlement"
        merged["headline"] = row.get("headline") or "Settlement"
        merged["sort_turn"] = int(row.get("turn", 0) or 0)
        rows.append(merged)

    # Bilateral peace ratifications. The producer remains
    # `_ratify_treaty(...)` / `cleanup_war_end(...)` — see
    # `_build_recent_peace_ratifications` for the field contract.
    bilateral_seq_by_turn: Dict[int, int] = {}
    for entry in reversed(entries):
        if not isinstance(entry, Mapping):
            continue
        if entry.get("new_state", "PEACE") != "PEACE":
            continue
        target = str(entry.get("target_nation", "Unknown"))
        turn = int(entry.get("turn", 0) or 0)
        bilateral_seq_by_turn.setdefault(turn, 0)
        bilateral_seq_by_turn[turn] += 1
        seq = bilateral_seq_by_turn[turn]
        route_id = _bilateral_peace_route_id(entry, seq)
        rows.append({
            "row_type": "bilateral_peace",
            "row_type_display": "Bilateral peace",
            "war_id": str(entry.get("war_id") or ""),
            "turn": turn,
            "sort_turn": turn,
            "headline": (
                f"Treaty with {target} (Turn {turn})"
            ),
            "target_nation": target,
            "war_outcome": str(entry.get("war_outcome", "white_peace") or "white_peace"),
            "route_id": route_id,
            "review_target": "ledger_settlements",
            "war_ended": True,
        })

    # Reverse-chronological order. Settlement rows already arrive newest
    # first; bilateral rows are appended newest-first too. Sorting by
    # (turn desc, row_type secondary) avoids mixing same-turn ordering
    # surprises while preserving original arrival order within a type.
    rows.sort(key=lambda r: (-int(r.get("sort_turn") or 0), r.get("row_type", "")))
    return rows[:limit]


# ---------------------------------------------------------------------------
# War status panel — contribution share rows (spec §16.2 line 1629)
# ---------------------------------------------------------------------------


def _beneficiaries_from_terms(terms: Iterable[Mapping[str, Any]]) -> set:
    """Return participant nations whose interests are advanced by `terms`.

    Used to set `is_beneficiary` on live preview rows so the confirm popup
    can stamp "rewarded" alongside leader / standing labels. Mirrors the
    archived event path's `ally_rewarded` reaction (build_settlement_review_from_event).
    """
    beneficiaries: set = set()
    for term in terms or []:
        if not isinstance(term, Mapping):
            continue
        ttype = str(term.get("type", "") or "")
        if ttype in ("territory_cede", "liberation"):
            recipient = str(term.get("to", "") or term.get("recipient", "") or "")
            if recipient:
                beneficiaries.add(recipient)
        elif ttype in ("vassalage", "subjugation"):
            lord = str(term.get("to", "") or term.get("lord_nation", "") or "")
            if lord:
                beneficiaries.add(lord)
        elif ttype == "forced_alliance":
            imposer = str(term.get("to", "") or "")
            if imposer:
                beneficiaries.add(imposer)
        elif ttype in ("gold_payment", "manpower_transfer"):
            recipient = str(term.get("to", "") or term.get("recipient", "") or "")
            if recipient:
                beneficiaries.add(recipient)
    return beneficiaries


def build_contribution_share_rows(
    world: Any, war_id: str, *,
    cap: int = SETTLEMENT_STANDING_ROW_CAP,
    settlement_terms: Optional[Iterable[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    """Top-N contribution share rows for a war_instance.

    Returns ``{rows, overflow_count}``. Rows are ordered by descending
    contribution share (`material_share` then `support_share`).
    Overflow is the count of participants beyond the cap. When
    contribution data is missing (early war / pre-Slice B), returns an
    empty `rows` list with overflow=0.

    `settlement_terms` is consumed only to stamp `is_beneficiary` on rows
    whose nation is named as the beneficiary of any clause (territory
    cede recipient, forced-alliance imposer, vassalage lord, etc.). The
    flag is read by the confirm popup's stamps row alongside `is_leader`.
    """
    instances = getattr(world, "war_instances", None) or {}
    war = instances.get(war_id)
    if not isinstance(war, Mapping):
        return {"rows": [], "overflow_count": 0}

    participants: List[str] = []
    for nation in (war.get("attackers") or []) + (war.get("defenders") or []):
        if isinstance(nation, str) and nation and nation not in participants:
            participants.append(nation)

    rows: List[Dict[str, Any]] = []
    try:
        from backend.game_logic.war_contribution import (
            compute_standing_inputs,
            standing_for_participant,
        )
    except Exception:
        return {"rows": [], "overflow_count": 0}

    beneficiaries = _beneficiaries_from_terms(settlement_terms or [])

    for nation in participants:
        side = "attackers" if nation in (war.get("attackers") or []) else (
            "defenders" if nation in (war.get("defenders") or []) else ""
        )
        if not side:
            continue
        try:
            inputs = compute_standing_inputs(world, war_id, nation, side=side)
            standing = standing_for_participant(
                world, war_id, nation, side=side,
            )
        except Exception:
            inputs = {}
            standing = "no_standing"
        rows.append({
            "nation": nation,
            "side": side,
            "side_label": side_label_display(side),
            "standing": standing,
            "standing_display": _standing_display(standing),
            "material_share": float(inputs.get("material_share", 0.0) or 0.0),
            "support_share": float(inputs.get("support_share", 0.0) or 0.0),
            "is_leader": (
                nation == war.get("attacker_leader")
                or nation == war.get("defender_leader")
            ),
            "is_beneficiary": nation in beneficiaries,
        })

    rows.sort(
        key=lambda r: (
            -r["material_share"], -r["support_share"], r["nation"],
        )
    )
    overflow = max(0, len(rows) - cap) if cap >= 0 else 0
    if cap >= 0:
        rows = rows[:cap]
    return {"rows": rows, "overflow_count": overflow}


# ---------------------------------------------------------------------------
# Spec §11.6 / Slice B — material-loss term spec for awe & dispatch tagging
# ---------------------------------------------------------------------------


def is_material_loss_term(term: Mapping[str, Any]) -> bool:
    """Helper mirroring `settlement_reactions._MATERIAL_LOSS_TYPES`.

    Slice E presentation only inspects `term["type"]`; structural
    material-loss detection lives in settlement_reactions for the
    sold-out-by-leader pipeline. This helper is kept here so dispatch /
    notification surfaces can independently decide whether to spotlight
    a term without importing reaction internals.
    """
    if not isinstance(term, Mapping):
        return False
    return term.get("type") in {
        "territory_cede",
        "vassalage",
        "subjugation",
        "forced_alliance",
        "liberation",
        "continental_system_join",
    }


__all__ = [
    "SETTLEMENT_PRIMARY_BEAT_CAP",
    "SETTLEMENT_ONELINER_PARTICIPANT_CAP",
    "SETTLEMENT_LEDGER_DEFAULT_ROWS",
    "SETTLEMENT_STANDING_ROW_CAP",
    "SETTLEMENT_INLINE_WARNING_CAP",
    "SETTLEMENT_EVENT_FAMILY",
    "SETTLEMENT_REVIEW_TARGET_ACTIVE",
    "SETTLEMENT_REVIEW_TARGET_ARCHIVED",
    "SETTLEMENT_ROUTES",
    "is_settlement_event_type",
    "settlement_route",
    "settlement_priority",
    "settlement_review_target",
    "settlement_notification_meta",
    "is_settlement_event_visible",
    "compose_summary_oneliner",
    "compose_digest_oneliner",
    "cap_settlement_dispatch_lines",
    "apply_warning_cap",
    "detect_awe_set_pieces",
    "build_settlement_review",
    "build_settlement_review_from_event",
    "recent_settlement_summaries",
    "build_contribution_share_rows",
    "is_material_loss_term",
]
