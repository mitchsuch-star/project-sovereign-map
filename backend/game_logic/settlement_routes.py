"""Settlement routing, reopen, and recovery primitives (CH-1 split, layer 0).

Route minting/resolution, reopen-attempt bookkeeping, archived/known war
checks, War Detail actionability, and the safe-reopen recovery responses.
Split from settlement_preview.py (CH-1); imports nothing from the other
settlement_* modules — this is the bottom layer of the settlement package.
"""

from __future__ import annotations

from backend.display_names import (
    SETTLEMENT_DISABLED_REASON_DISPLAY,
    settlement_disabled_reason_display,
)
from backend.game_logic.diplomatic_templates import resolve_settlement_voice_line
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
)


# G2-Slice-3 SC-14b: stale-recovery reopen cap per (war_id, turn). Attempts
# 1..MAX may reopen when the target is valid; attempt MAX+1 returns
# `must_reopen=False` with the SC-14b choose-from-war-detail copy.
SETTLEMENT_REOPEN_MAX_ATTEMPTS = 3


# G2-Slice-3 SC-14c: route id namespace + format
#   `settlement:{war_id}:{turn}:{seq}` where `seq` is a per-(war_id, turn)
# monotonic counter starting at 1, persisted on
# `world.settlement_route_seq[war_id][turn]`.
SETTLEMENT_ROUTE_NAMESPACE = "settlement"


SETTLEMENT_FAMILY_DIALOGUE_TYPES = frozenset(
    {
        "settlement_confirm",
        "incoming_settlement_offer",
        "settlement_scope_replace_confirm",
        # G4F-8 — the pair-substitute confirm chooser.
        "settlement_pair_substitute_confirm",
    }
)

# FA slice 10 (FA-4 / FA-N15 / FA-N17 / FA-N18 / FA-N4): AN INCOMING OFFER IS
# MAIL, NEVER A DRAFT.
#
# SC-26's collision protection asks "is a settlement already on the table?".
# The FAMILY set answers that question with a letter the enemy sent us, so
# three readers that must agree read an `incoming_settlement_offer` as OUR
# mounted draft:
#
#   * `_mounted_settlement_dialogue` — the cross-war collision AND the
#     same-war refresh/scope-replace arm in `stage_settlement_confirm`;
#   * `_settlement_dialogue_active` — the second gate, inside
#     `evaluate_open_settlement_eligibility` (current AND queue);
#   * the staging tail's replace-vs-preempt choice.
#
# Measured on the committed t20 fixture: accepting Britain's offer popped it,
# the pop PROMOTED a queued offer for another war, and the collision arm
# refused the accept — destroying the letter the player had just clicked and
# naming a war they had never seen. Opening Settlement over a standing offer
# read the ENEMY's terms as our draft and raised a chooser whose two scope
# strings were the identical string.
#
# A DRAFT is a surface WE authored or staged. The family set keeps its name
# (the defensive cross-war guards still want it); the three readers above
# take the narrower set.
SETTLEMENT_DRAFT_DIALOGUE_TYPES = frozenset(
    SETTLEMENT_FAMILY_DIALOGUE_TYPES - {"incoming_settlement_offer"}
)

# Flip lever: False restores the pre-slice-10 reading (an offer counts as a
# mounted draft) at all three readers at once.
OFFER_IS_MAIL_NEVER_A_DRAFT = True


def settlement_draft_dialogue_types() -> frozenset:
    """The dialogue types SC-26 counts as a mounted DRAFT.

    Read through a function, not a module constant, so the flip lever is
    honoured by every reader at call time (an importer that bound the set at
    import time would not see the flip).
    """
    return (
        SETTLEMENT_DRAFT_DIALOGUE_TYPES
        if OFFER_IS_MAIL_NEVER_A_DRAFT
        else SETTLEMENT_FAMILY_DIALOGUE_TYPES
    )


SETTLEMENT_ERROR_DISPLAY = SETTLEMENT_DISABLED_REASON_DISPLAY


def _error_display(code: str) -> str:
    return settlement_disabled_reason_display(code)


def _war_label(war_id: str, war_instance: Mapping[str, Any]) -> str:
    attackers = list(war_instance.get("attackers") or [])
    defenders = list(war_instance.get("defenders") or [])
    if attackers and defenders:
        return f"{attackers[0]} vs {defenders[0]}"
    return war_id or "Settlement"


def _reopen_target(war_id: str, dialogue: Mapping[str, Any]) -> Dict[str, Any]:
    preview = dialogue.get("settlement_preview") or {}
    covered = list(dialogue.get("covered_enemy_participants") or preview.get("covered_enemy_participants") or [])
    selected = str(dialogue.get("selected_target_nation") or "")
    if not selected and covered:
        selected = covered[0]
    diagnostic_fallback = not bool(dialogue.get("selected_target_nation"))
    result: Dict[str, Any] = {
        "surface": "settlement_review",
        "target": "settlement_review",
        "war_id": war_id,
        "nation": selected,
        "target_nation": selected,
        "proposer_side": str(dialogue.get("proposer_side") or preview.get("proposer_side") or ""),
    }
    if diagnostic_fallback and selected:
        result["diagnostic_fallback_target"] = True
        result["error_display"] = "This settlement lost its selected court. Reopen from war detail."
    return result


def _normalize_nation_list(values: Optional[Iterable[str]]) -> List[str]:
    if values is None:
        return []
    return sorted({str(value) for value in values if str(value or "").strip()})


def _settlement_dialogue_active(world: Any, war_id: str) -> bool:
    current = getattr(world, "pending_diplomatic_dialogue", None)
    dm = getattr(world, "dialogue_manager", None)
    queued = list(dm.iter_queue()) if dm is not None and hasattr(dm, "iter_queue") else []
    # FA slice 10: the SECOND gate. It refused an open on a war whose only
    # settlement surface was the enemy's own letter — "Resolve the current
    # settlement review first." about a review that did not exist. A letter
    # standing in the mailbox is not a review in progress.
    _draft_types = settlement_draft_dialogue_types()
    for dialogue in ([current] if current else []) + queued:
        if not isinstance(dialogue, Mapping):
            continue
        if dialogue.get("type") not in _draft_types:
            continue
        if str(dialogue.get("war_id") or "") == str(war_id):
            return True
    return False


def _settlement_history_route(
    *,
    war_id: str,
    route_id: str = "",
    reason: str = "",
) -> Dict[str, Any]:
    route = {
        "surface": "settlement_history",
        "target": "settlement_history",
        "war_id": str(war_id or ""),
        "route_id": str(route_id or ""),
    }
    if reason:
        route["reason"] = reason
    return route


def _war_detail_recovery_route(
    *,
    war_id: str,
    selected_target_nation: str = "",
    covered_enemy_participants: Optional[Iterable[str]] = None,
    source_route_id: str = "",
    reason: str = "",
) -> Dict[str, Any]:
    route = {
        "surface": "war_detail",
        "target": "war_detail",
        "war_id": str(war_id or ""),
        "selected_target_nation": str(selected_target_nation or ""),
        "target_nation": str(selected_target_nation or ""),
        "nation": str(selected_target_nation or ""),
        "covered_enemy_participants": list(covered_enemy_participants or []),
        "source_route_id": str(source_route_id or ""),
    }
    if reason:
        route["reason"] = reason
    return route


def _terminal_recovery_copy(war_id: str = "") -> str:
    return resolve_settlement_voice_line(
        "settlement_no_alternative_route_chancery",
        war_label=str(war_id or "this war"),
    ) or (
        "This settlement cannot currently be recovered from the existing "
        "surfaces. Close this review and reassess the war next turn."
    )


def evaluate_war_detail_actionability(
    world: Any,
    *,
    war_id: str,
    selected_target_nation: Optional[str] = None,
    covered_enemy_participants: Optional[Iterable[str]] = None,
    source_route_id: str = "",
    actor_nation: Optional[str] = None,
) -> Dict[str, Any]:
    """SC-10b: decide whether blocked review may show Open War Detail.

    This helper deliberately answers only whether War Detail is a real
    recovery surface for the selected live pair. It does not expose direct
    pair-substitute actions from settlement_confirm; War Detail remains the
    owner of bilateral peace / armistice controls.
    """
    war_id_str = str(war_id or "")
    actor = str(actor_nation or getattr(world, "player_nation", "France") or "France")
    selected = str(selected_target_nation or "").strip()
    covered = _normalize_nation_list(covered_enemy_participants)

    def _blocked(code: str, **extra: Any) -> Dict[str, Any]:
        display = _error_display(code)
        return {
            "actionable": False,
            "war_id": war_id_str,
            "selected_target_nation": selected,
            "covered_enemy_participants": covered,
            "refusal_code": code,
            "refusal_code_display": display,
            "error": code,
            "error_display": display,
            "peace_seeking_controls": [],
            **extra,
        }

    if not war_id_str:
        return _blocked("malformed_route")
    instance = (getattr(world, "war_instances", {}) or {}).get(war_id_str)
    if not isinstance(instance, Mapping):
        if is_war_archived(world, war_id_str):
            return _blocked(
                "war_archived",
                recovery_route=_settlement_history_route(
                    war_id=war_id_str,
                    route_id=source_route_id,
                    reason="war_archived",
                ),
            )
        return _blocked("war_archived" if is_war_known(world, war_id_str) else "malformed_route")
    if instance.get("ended_turn") is not None:
        return _blocked(
            "war_archived",
            recovery_route=_settlement_history_route(
                war_id=war_id_str,
                route_id=source_route_id,
                reason="war_archived",
            ),
        )
    mounted = _mounted_settlement_dialogue(world)
    if mounted is not None and str(mounted.get("war_id") or "") not in ("", war_id_str):
        return _blocked("settlement_collision_active")
    if not selected:
        return _blocked("selected_pair_missing")

    side_by_nation = instance.get("side_by_nation") or {}
    actor_side = side_by_nation.get(actor)
    selected_side = side_by_nation.get(selected)
    if not actor_side or not selected_side or actor_side == selected_side:
        return _blocked("selected_pair_missing")

    pair = world._make_diplo_key(actor, selected) if hasattr(world, "_make_diplo_key") else "|".join(sorted([actor, selected]))
    meta = instance.get("diplo_key_meta") or {}
    pair_meta = meta.get(pair) or {}
    resolved_pairs = set(instance.get("resolved_diplo_keys") or [])
    if pair in resolved_pairs or pair_meta.get("pair_status") == "resolved":
        return _blocked("pair_already_resolved")
    active_pairs = set(instance.get("active_diplo_keys") or [])
    if pair not in active_pairs:
        return _blocked("selected_pair_missing")
    if pair_meta.get("pair_status", "war") != "war":
        return _blocked("pair_not_at_war")
    if (getattr(world, "diplomatic_states", {}) or {}).get(pair) != "WAR":
        return _blocked("pair_not_at_war")

    route = _war_detail_recovery_route(
        war_id=war_id_str,
        selected_target_nation=selected,
        covered_enemy_participants=covered,
        source_route_id=source_route_id,
        reason="blocked_settlement_recovery",
    )
    return {
        "actionable": True,
        "war_id": war_id_str,
        "selected_target_nation": selected,
        "covered_enemy_participants": covered,
        "refusal_code": "",
        "refusal_code_display": "",
        "peace_seeking_controls": ["negotiate_peace"],
        "recovery_route": route,
    }


def evaluate_request_terms_affordance(world: Any, war_id: str) -> Dict[str, Any]:
    """SC-30 / Slice G1 — the Request Terms affordance for one war.

    Closed-enum contract (the cleanup-spec no-false-affordance rule —
    "a click-only polite refusal is forbidden"):

    - ``{"state": "available"}`` — the lifecycle can advance; render enabled.
    - ``{"state": "disabled", "reason": <temporal code>, "reason_display"}``
      ONLY for deterministic temporal blocks, each naming its clock:
      ``request_pending`` (an answer arrives with the next AI phase),
      ``request_cooldown`` (N turns remaining), ``war_too_young`` (war age
      grows monotonically toward the producer's minimum).
    - ``{"state": "absent", "reason": <structural code>}`` — the AI side
      cannot create or advance the lifecycle (one-to-one war, no opposing
      leader, war archived, an offer already on the desk, ...); the
      control must NOT render.
    """
    # Function-level import — ai_diplomacy sits above the settlement
    # package (the established cycle-break pattern).
    from backend.game_logic.ai_diplomacy import (
        SETTLEMENT_OFFER_MIN_WAR_DURATION_TURNS,
        _settlement_offer_already_pending,
        _settlement_offer_already_promoted,
        _settlement_offer_eligible_for_war,
    )

    war_id_str = str(war_id or "")
    current_turn = int(getattr(world, "current_turn", 0) or 0)
    player = str(getattr(world, "player_nation", "France"))
    war = (getattr(world, "war_instances", {}) or {}).get(war_id_str)
    if not isinstance(war, dict):
        return {"state": "absent", "reason": "war_unknown"}

    requests = getattr(world, "settlement_terms_requests", None) or {}
    entry = requests.get(war_id_str)
    if isinstance(entry, dict):
        if entry.get("status") == "requested":
            return {
                "state": "disabled",
                "reason": "request_pending",
                "reason_display": (
                    "Terms already requested, Sire — an answer is expected "
                    "with the next dispatches."
                ),
            }
        cooldown_until = int(entry.get("cooldown_until_turn") or 0)
        if current_turn < cooldown_until:
            remaining = cooldown_until - current_turn
            return {
                "state": "disabled",
                "reason": "request_cooldown",
                "reason_display": (
                    f"The court was asked recently, Sire. "
                    f"({remaining} turn{'s' if remaining != 1 else ''} "
                    f"remaining.)"
                ),
            }

    # One-active-offer guard FIRST: the eligibility function returns its
    # FIRST refusal, so the producer's periodic `cooldown_active` (which a
    # direct request bypasses) can mask an offer already on the desk.
    pending = getattr(world, "pending_settlement_dialogues", None) or []
    if _settlement_offer_already_pending(pending, war_id=war_id_str) or (
        _settlement_offer_already_promoted(world, war_id=war_id_str)
    ):
        return {"state": "absent", "reason": "offer_already_pending"}

    structural = _settlement_offer_eligible_for_war(
        world, war, player=player, current_turn=current_turn,
    )
    if structural == "war_too_young":
        created_turn = int(war.get("created_turn") or current_turn)
        ready_turn = created_turn + SETTLEMENT_OFFER_MIN_WAR_DURATION_TURNS
        remaining = max(1, ready_turn - current_turn)
        return {
            "state": "disabled",
            "reason": "war_too_young",
            "reason_display": (
                f"No court names terms this early in a war, Sire. "
                f"({remaining} turn{'s' if remaining != 1 else ''} "
                f"remaining.)"
            ),
        }
    if structural in ("offer_already_pending", "offer_already_promoted"):
        # Not temporal — the offer on the desk IS the affordance now.
        return {"state": "absent", "reason": structural}
    if structural not in (None, "cooldown_active"):
        # The producer's periodic `cooldown_active` clock does NOT gate a
        # direct request (the request cooldown above is the request's own
        # clock); every other refusal is structural — the control is absent.
        return {"state": "absent", "reason": structural}
    return {"state": "available", "reason": ""}


# ---------------------------------------------------------------------------
# SC-29 / G2-Slice-7: pair-scoped peace substitute CTAs
# ---------------------------------------------------------------------------


def _mounted_settlement_dialogue(world: Any) -> Optional[Mapping[str, Any]]:
    """Return the *current* mounted settlement DRAFT, or None.

    SC-14 / SC-26 mounted means the current hard-stop dialogue. Queued or
    dismissed settlement-family items don't count for live-route precedence
    or collision protection.

    FA slice 10: nor does an `incoming_settlement_offer`, which is mail — a
    soft-stop persistent mailbox item the player may hold for turns. The
    docstring above said "the current HARD-STOP dialogue" and the code
    admitted the whole family; the two now agree.
    """
    current = getattr(world, "pending_diplomatic_dialogue", None)
    if not isinstance(current, Mapping):
        return None
    if current.get("type") not in settlement_draft_dialogue_types():
        return None
    return current


def mint_settlement_route_id(
    world: Any,
    *,
    war_id: str,
    turn: Optional[int] = None,
) -> str:
    """SC-14c: mint a unique `settlement:{war_id}:{turn}:{seq}` route id.

    `seq` is a per-(war_id, turn) monotonic counter starting at 1, persisted
    on `world.settlement_route_seq[war_id][turn]` so two settlement events
    in the same turn do not collide. The staged dialogue owns the id; every
    downstream consumer (reaction event, dispatch, ledger, notification,
    result feedback) reads the staged value verbatim and never recomputes.
    """
    if turn is None:
        turn = int(getattr(world, "current_turn", 0) or 0)
    else:
        turn = int(turn)
    store = getattr(world, "settlement_route_seq", None)
    if store is None:
        world.settlement_route_seq = {}
        store = world.settlement_route_seq
    per_war = store.setdefault(str(war_id), {})
    last = int(per_war.get(turn, 0) or 0)
    seq = last + 1
    per_war[turn] = seq
    return f"{SETTLEMENT_ROUTE_NAMESPACE}:{war_id}:{turn}:{seq}"


def _reopen_attempt_store(world: Any) -> Dict[str, Dict[int, int]]:
    store = getattr(world, "settlement_reopen_attempts", None)
    if store is None:
        world.settlement_reopen_attempts = {}
        store = world.settlement_reopen_attempts
    return store


def get_reopen_attempts(world: Any, *, war_id: str) -> int:
    """Read the SC-14b reopen attempt count for the current `(war_id, turn)`."""
    if not war_id:
        return 0
    turn = int(getattr(world, "current_turn", 0) or 0)
    return int((_reopen_attempt_store(world).get(str(war_id)) or {}).get(turn, 0))


def record_reopen_attempt(world: Any, *, war_id: str) -> int:
    """SC-14b: increment + return the per-(war_id, turn) reopen attempt count.

    Attempt 1..SETTLEMENT_REOPEN_MAX_ATTEMPTS may reopen when the target is
    valid; the next attempt must return `must_reopen=False` with the
    `reopen_attempt_cap_exceeded` SC-14b choose-from-war-detail copy.
    """
    if not war_id:
        return 0
    turn = int(getattr(world, "current_turn", 0) or 0)
    store = _reopen_attempt_store(world)
    per_war = store.setdefault(str(war_id), {})
    per_war[turn] = int(per_war.get(turn, 0) or 0) + 1
    return int(per_war[turn])


def reopen_attempt_cap_exceeded(world: Any, *, war_id: str) -> bool:
    """True when a further reopen for this `(war_id, turn)` must NOT fire."""
    return get_reopen_attempts(world, war_id=war_id) >= SETTLEMENT_REOPEN_MAX_ATTEMPTS


def is_war_archived(world: Any, war_id: str) -> bool:
    """SC-14/14d/14e: the war is archived (or no longer active) right now.

    Click-time check: an active `war_instance` with no `ended_turn` is
    live; anything else (ended, missing, or in `archived_war_instances`)
    must route to the archived ledger row.
    """
    if not war_id:
        return False
    instances = getattr(world, "war_instances", {}) or {}
    instance = instances.get(str(war_id))
    if isinstance(instance, Mapping):
        if instance.get("ended_turn") is not None:
            return True
        return False
    archived = getattr(world, "archived_war_instances", None) or []
    for entry in archived:
        if isinstance(entry, Mapping) and str(entry.get("war_id") or "") == str(war_id):
            return True
    return False


def is_war_known(world: Any, war_id: str) -> bool:
    """True if `war_id` resolves to either an active or archived instance."""
    if not war_id:
        return False
    instances = getattr(world, "war_instances", {}) or {}
    if str(war_id) in instances:
        return True
    archived = getattr(world, "archived_war_instances", None) or []
    return any(
        isinstance(entry, Mapping) and str(entry.get("war_id") or "") == str(war_id)
        for entry in archived
    )


def derive_settlement_review_target(world: Any, *, war_id: str) -> str:
    """SC-14/14d/14e click-time re-resolution.

    Returns the canonical review-target string to use *now*, regardless of
    what was rendered into a notification, dispatch, or result feedback row
    when it was first emitted. Active war -> live settlement review surface;
    archived (ended/no longer in `war_instances`) -> archived ledger row.
    """
    from backend.game_logic.settlement_presentation import (
        SETTLEMENT_REVIEW_TARGET_ACTIVE,
        SETTLEMENT_REVIEW_TARGET_ARCHIVED,
    )

    if is_war_archived(world, war_id):
        return SETTLEMENT_REVIEW_TARGET_ARCHIVED
    return SETTLEMENT_REVIEW_TARGET_ACTIVE


def resolve_settlement_route_click(
    world: Any,
    *,
    war_id: str,
    route_id: Optional[str] = None,
    recent_window_route_ids: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """SC-14/14d/14e: re-resolve a settlement route click against live state.

    Returns a structured payload describing what the click should do *now*:

    - `available=True, review_target="settlement_review", war_id=...` for
      live wars (route the click into an in-flight active surface).
    - `available=True, review_target="ledger_settlements", war_id=..., route_id=...`
      for archived rows still inside the recent-settlement window.
    - `available=False, error="settlement_no_longer_in_recent_window"` when
      `recent_window_route_ids` is supplied and the route id is no longer
      present (SC-14e aged-out dispatch link).
    - `available=False, error="invalid_war_id"` for unknown wars.

    Callers pass `recent_window_route_ids` (the route ids visible in the
    current recent-settlement window) when they care about aged-out
    routing; callers that don't care (live result feedback) leave it
    None and just get archived/active routing.
    """
    from backend.game_logic.settlement_presentation import (
        SETTLEMENT_REVIEW_TARGET_ACTIVE,
        SETTLEMENT_REVIEW_TARGET_ARCHIVED,
    )

    war_id_str = str(war_id or "")
    if not war_id_str or not is_war_known(world, war_id_str):
        return {
            "available": False,
            "war_id": war_id_str,
            "route_id": str(route_id or ""),
            "review_target": "",
            "error": "invalid_war_id",
            "error_display": _error_display("invalid_war_id"),
        }
    archived = is_war_archived(world, war_id_str)
    if archived and recent_window_route_ids is not None:
        window = {str(r or "") for r in recent_window_route_ids if r is not None}
        if route_id and str(route_id) not in window:
            return {
                "available": False,
                "war_id": war_id_str,
                "route_id": str(route_id or ""),
                "review_target": SETTLEMENT_REVIEW_TARGET_ARCHIVED,
                "error": "settlement_no_longer_in_recent_window",
                "error_display": _error_display(
                    "settlement_no_longer_in_recent_window"
                ),
            }
    return {
        "available": True,
        "war_id": war_id_str,
        "route_id": str(route_id or ""),
        "review_target": (
            SETTLEMENT_REVIEW_TARGET_ARCHIVED
            if archived
            else SETTLEMENT_REVIEW_TARGET_ACTIVE
        ),
        "war_archived": bool(archived),
    }


def _no_reopen_target_payload(
    war_id: str,
    *,
    error: str = "no_reopen_target_available",
) -> Dict[str, Any]:
    """SC-13 / SC-14b / SC-7b dual-empty / cap-exceeded fallback payload.

    Returns the structured response fields used when reopen cannot be
    safely fired and the player must be redirected to war detail. The
    caller is responsible for adding success/dialogue_type/action.
    """
    payload = {
        "must_reopen": False,
        "reopen_target": {
            "surface": "war_detail",
            "target": "war_detail",
            "war_id": war_id,
            "nation": "",
            "target_nation": "",
        },
        "error": error,
        "error_display": _error_display(error),
    }
    if error == "reopen_attempt_cap_exceeded":
        payload["talleyrand_text"] = resolve_settlement_voice_line(
            "settlement_reopen_cap_exhausted_talleyrand",
            war_label=war_id or "this war",
        )
    return payload


def _safe_reopen_response(
    world: Any,
    *,
    war_id: str,
    dialogue: Mapping[str, Any],
    fallback_error: str = "no_reopen_target_available",
) -> Dict[str, Any]:
    """Build the SC-2/SC-3/SC-13 reopen payload with the SC-14b cap applied.

    Honors SC-7b (no `must_reopen=True` with empty target), SC-13
    (dual-empty fallback) and SC-14b (per-(war_id, turn) attempt cap).
    The caller then merges this payload into its action result.
    """
    selected = str(dialogue.get("selected_target_nation") or "")
    covered = list(dialogue.get("covered_enemy_participants") or [])
    has_target = bool(selected) or bool(covered)
    if not has_target:
        return _no_reopen_target_payload(war_id, error=fallback_error)
    if reopen_attempt_cap_exceeded(world, war_id=war_id):
        actionability = evaluate_war_detail_actionability(
            world,
            war_id=war_id,
            selected_target_nation=selected or (str(covered[0]) if covered else ""),
            covered_enemy_participants=covered,
            source_route_id=str(dialogue.get("route_id") or ""),
        )
        payload = {
            "must_reopen": False,
            "error": "reopen_attempt_cap_exceeded",
            "error_display": _error_display("reopen_attempt_cap_exceeded"),
            "war_detail_actionability": actionability,
            "talleyrand_text": resolve_settlement_voice_line(
                "settlement_reopen_cap_exhausted_talleyrand",
                war_label=war_id or "this war",
            ),
        }
        if actionability.get("actionable"):
            route = dict(actionability.get("recovery_route") or {})
            payload["recovery_route"] = route
            payload["reopen_target"] = route
        else:
            payload["terminal_recovery_copy"] = _terminal_recovery_copy(war_id)
            payload["reopen_target"] = {
                "surface": "blocked_terminal",
                "target": "blocked_terminal",
                "war_id": war_id,
                "nation": selected,
                "target_nation": selected,
            }
        return payload
    record_reopen_attempt(world, war_id=war_id)
    return {
        "must_reopen": True,
        "reopen_target": _reopen_target(war_id, dialogue),
    }


# ---------------------------------------------------------------------------
# G2-Slice-3 SC-26: same-war / cross-war collision support
# ---------------------------------------------------------------------------
