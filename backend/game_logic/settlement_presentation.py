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
# Spec §16.2 line 1620 — advisory standing/contribution row cap.
SETTLEMENT_STANDING_ROW_CAP = 5
# Spec §16.3 line 1660 — top warnings rendered inline after hard stops.
SETTLEMENT_INLINE_WARNING_CAP = 2

# Spec §11.6 line 1287 — event family + review-target taxonomy.
SETTLEMENT_EVENT_FAMILY = "settlement"
SETTLEMENT_REVIEW_TARGET_ACTIVE = "settlement_review"
SETTLEMENT_REVIEW_TARGET_ARCHIVED = "diplomatic_ledger"


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
) -> str:
    """Return the review target for a settlement event payload.

    Spec §11.6 line 1287 — `review_target="settlement_review"` while the
    war is active; switches to `"diplomatic_ledger"` once the war
    archives. The settlement event payload carries `route.review_target`
    (canonical) and `war_ended` (fallback).
    """
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
    review_target = settlement_review_target(event)
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


def compose_summary_oneliner(
    event: Mapping[str, Any], *, world: Any | None = None,
) -> str:
    """Render the one-liner per spec §11.6 line 1287.

    Format: "Settlement of {war_name}: {terms_summary[0]}; {p1}, {p2},
    {p3}{+N more} react." Caps named participants at three; the rest
    are rolled into ``+N more``.
    """
    war_id = str(event.get("war_id", "") or "")
    war_label = _war_label(world, war_id) if world is not None else (war_id or "war")
    terms = list(event.get("terms_summary") or [])
    head_term = terms[0] if terms else "settlement ratified"
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
        who = "no participant reactions"
    return f"Settlement of {war_label}: {head_term}; {who} react."


def compose_digest_oneliner(event: Mapping[str, Any]) -> str:
    """Spec §11.6 line 1288 digest one-liner."""
    hidden = int(event.get("hidden_reaction_count", 0) or 0)
    war_id = str(event.get("war_id", "") or "war")
    return (
        f"{hidden} additional courts register the settlement aftermath "
        f"({war_id})."
    )


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

    terms_inline, terms_overflow = _slice_for_density(
        terms, density, _DENSITY_TERMS,
    )
    allies_inline, allies_overflow = _slice_for_density(
        allies, density, _DENSITY_ALLIES,
    )
    warning_cap = 1 if density == "compact" else SETTLEMENT_INLINE_WARNING_CAP
    warning_split = apply_warning_cap(
        warnings,
        inline_warning_cap=warning_cap,
    )

    acceptance_payload: Dict[str, Any] = {}
    if acceptance and isinstance(acceptance, Mapping):
        acceptance_payload = {
            "total": int(acceptance.get("total", 0) or 0),
            "band": str(acceptance.get("band", "near_acceptable")),
            "top_components": list(acceptance.get("top_components") or [])[:3],
        }
        if density == "verbose":
            acceptance_payload["debug_components"] = list(
                acceptance.get("debug_components") or []
            )

    return {
        "war_id": war_id,
        "war_label": war_label,
        "proposer_side": proposer_side,
        "accepting_side": accepting_side,
        "covered_enemy_participants": list(covered_enemy_participants or []),
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
    }


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
        review_target = settlement_review_target(event)
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
            "terms_summary": list(event.get("terms_summary") or []),
            "covered_enemy_participants": list(
                event.get("covered_enemy_participants") or []
            ),
            "named_reactions": named,
            "additional_reaction_count": more,
            "war_ended": bool(event.get("war_ended", False)),
            "review_target": review_target,
            "route_id": str((event.get("route") or {}).get("route_id", "") or ""),
            "awe_tags": list(event.get("awe_tags") or []),
        })
        if len(out) >= limit:
            break
    return out


# ---------------------------------------------------------------------------
# War status panel — contribution share rows (spec §16.2 line 1629)
# ---------------------------------------------------------------------------


def build_contribution_share_rows(
    world: Any, war_id: str, *,
    cap: int = SETTLEMENT_STANDING_ROW_CAP,
) -> Dict[str, Any]:
    """Top-N contribution share rows for a war_instance.

    Returns ``{rows, overflow_count}``. Rows are ordered by descending
    contribution share (`material_share` then `support_share`).
    Overflow is the count of participants beyond the cap. When
    contribution data is missing (early war / pre-Slice B), returns an
    empty `rows` list with overflow=0.
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
            "standing": standing,
            "material_share": float(inputs.get("material_share", 0.0) or 0.0),
            "support_share": float(inputs.get("support_share", 0.0) or 0.0),
            "is_leader": (
                nation == war.get("attacker_leader")
                or nation == war.get("defender_leader")
            ),
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
    "recent_settlement_summaries",
    "build_contribution_share_rows",
    "is_material_loss_term",
]
