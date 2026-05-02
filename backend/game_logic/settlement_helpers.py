"""Imperial Settlement / Ally Participation foundation helpers.

Slice A1 shipped the war-instance invariant assertion. Slice A2 added the
war-entry plumbing every WAR seam must use to allocate, reuse, and attach
to `war_instance` records. Slice A3 adds the merge / archive / leader
substrate that the rest of the Imperial Settlement system builds on:

- `CascadeContext` — transaction object that travels through
  `_process_war_cascade()` so the cascade signature does not grow past
  nine positional arguments.
- `validate_war_declaration(...)` — pre-commit check that returns either
  `merge_required=True` (A3 will consolidate) or
  `war_instance_side_conflict` (a real hard stop).
- `ensure_war_instance_for_pair(...)` — owns declaration / cascade
  creation. Reuses compatible active instances; runs `merge_war_instances`
  when both nations are active in distinct instances; allocates a fresh
  skeleton otherwise.
- `attach_pair_to_war_instance(...)` and
  `attach_participant_to_war_instance(...)` — narrower helpers used by
  direct-entry seams. `attach_pair_to_war_instance` triggers a merge if
  the pair is already owned by a different active instance and retargets
  the survivor.
- `resolve_pair_to_resolved(...)` / `mark_pair_armistice(...)` —
  pair-status transitions; `resolve_pair_to_resolved` stamps `ended_turn`
  / `end_reason="all_pairs_resolved"` when the last active pair resolves.
- `merge_war_instances(...)` — Slice A3 transitive merge transaction
  per spec §7.6.
- `mark_participant_eliminated_in_all_wars(...)` — Slice A3 elimination
  exit per spec §7.4 (no separate-peace reaction).
- `archive_terminal_war_instances(...)` — Slice A3 archive compaction
  per spec §7.5 (10-turn retention window).
- `war_leader_score(...)` — Slice A3 settlement-specific leader score
  per spec §7.4 (used by non-coalition leader replacement; coalition
  leader wars use `coalition.select_coalition_leader(...)`).
- `assert_war_instance_invariants(world, *, context="post_merge")` —
  Slice A3 promoted this to an always-on post-merge assertion that also
  catches dangling absorbed `war_id` references in
  `diplomatic_commitments`, `pending_dispatch_events`, and any optional
  Slice B/C containers (`war_contribution_scores`,
  `pending_settlement_dialogues`, `settlement_route_payloads`).

Per `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §7.2 / §7.3 / §7.6 these
helpers are empty-safe, idempotent, and invalidate the lazy
`war_instances_by_leader` / `war_instances_by_participant` indexes after
mutation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


# ===========================================================================
# Invariant assertion (Slice A1)
# ===========================================================================


def _is_active_instance(instance: Any) -> bool:
    return isinstance(instance, dict) and instance.get("ended_turn") is None


def _iter_active_war_instances(world: Any) -> Iterable:
    instances = getattr(world, "war_instances", None) or {}
    for war_id, instance in instances.items():
        if _is_active_instance(instance):
            yield war_id, instance


class WarInstanceInvariantError(AssertionError):
    """Raised when `assert_war_instance_invariants` finds a violation."""

    def __init__(self, message: str, *, context: str, violations: List[str]):
        super().__init__(message)
        self.context = context
        self.violations = list(violations)


def assert_war_instance_invariants(
    world: Any,
    *,
    context: str = "general",
) -> None:
    """Validate war-instance ownership against live diplomatic state.

    Spec contract (§7.2 / §7.4):

    - Every `diplomatic_states[diplo_key] == "WAR"` MUST appear in exactly
      one active `war_instance.active_diplo_keys` with
      `diplo_key_meta[diplo_key]["pair_status"] == "war"`.
    - No active `war_instance` may claim a non-`WAR` pair as
      `pair_status == "war"`.
    - `side_by_nation` MUST agree with `attackers` / `defenders` membership
      and no nation may appear on both sides of the same active
      `war_instance`.
    """
    violations: List[str] = []

    diplomatic_states = getattr(world, "diplomatic_states", None) or {}
    war_pairs = {
        str(pair) for pair, state in diplomatic_states.items() if state == "WAR"
    }

    pair_owners: dict = {}
    for war_id, instance in _iter_active_war_instances(world):
        active_pairs = instance.get("active_diplo_keys") or []
        meta = instance.get("diplo_key_meta") or {}

        attackers = set(instance.get("attackers") or [])
        defenders = set(instance.get("defenders") or [])
        overlap = attackers & defenders
        if overlap:
            violations.append(
                f"war_instance {war_id!r} has nation(s) on both sides: "
                f"{sorted(overlap)}"
            )

        side_by_nation = instance.get("side_by_nation") or {}
        for nation, side in side_by_nation.items():
            if side == "attackers" and nation not in attackers:
                violations.append(
                    f"war_instance {war_id!r} side_by_nation says {nation!r} is "
                    f"attacker but attackers list disagrees"
                )
            elif side == "defenders" and nation not in defenders:
                violations.append(
                    f"war_instance {war_id!r} side_by_nation says {nation!r} is "
                    f"defender but defenders list disagrees"
                )
            elif side not in {"attackers", "defenders"}:
                violations.append(
                    f"war_instance {war_id!r} side_by_nation has unknown side "
                    f"{side!r} for {nation!r}"
                )

        for pair in active_pairs:
            pair_status = (meta.get(pair) or {}).get("pair_status")
            if pair_status == "war":
                if pair in pair_owners:
                    violations.append(
                        f"diplo_key {pair!r} is claimed by both "
                        f"war_instance {pair_owners[pair]!r} and {war_id!r}"
                    )
                else:
                    pair_owners[pair] = war_id
                if diplomatic_states and pair not in war_pairs:
                    violations.append(
                        f"war_instance {war_id!r} claims pair {pair!r} as "
                        f"pair_status='war' but diplomatic_states does not "
                        f"have it as WAR"
                    )
            elif pair_status == "armistice":
                pass
            elif pair_status == "resolved":
                violations.append(
                    f"war_instance {war_id!r} keeps resolved pair {pair!r} "
                    f"in active_diplo_keys; resolved pairs must move to "
                    f"resolved_diplo_keys per spec §7.3"
                )

    for pair in war_pairs:
        if pair not in pair_owners:
            violations.append(
                f"diplomatic_states has {pair!r} as WAR but no active "
                f"war_instance claims it with pair_status='war'"
            )

    if context == "post_merge":
        violations.extend(_post_merge_violations(world))

    if violations:
        raise WarInstanceInvariantError(
            "assert_war_instance_invariants failed in context "
            f"{context!r}: {len(violations)} violation(s):\n  - "
            + "\n  - ".join(violations),
            context=context,
            violations=violations,
        )


def _known_war_ids(world: Any) -> set:
    """Set of all `war_id` strings currently resolvable in world state.

    Includes both active and terminal-but-not-yet-archived instances
    (per spec §7.5 retention window), plus archived instances (which are
    legitimate references for ledger / log readers). An `absorbed` `war_id`
    -- one that the merge transaction folded into a survivor -- will NOT
    appear here.
    """
    known = set((getattr(world, "war_instances", None) or {}).keys())
    archived = getattr(world, "archived_war_instances", None) or []
    for record in archived:
        if isinstance(record, dict):
            war_id = record.get("war_id")
            if war_id:
                known.add(war_id)
    return known


def _post_merge_violations(world: Any) -> List[str]:
    """Walk live + optional containers to catch dangling absorbed war_ids.

    Spec line 113: "no absorbed `war_id` remains in live
    `diplomatic_commitments`, optional `war_contribution_scores`, optional
    `pending_settlement_dialogues`, dispatch route payloads, or ledger
    payloads". Optional Slice B/C containers are checked only if present
    on `world` (no-op-safe before they land).
    """
    out: List[str] = []
    known = _known_war_ids(world)

    def _check(label: str, war_id_value: Any) -> None:
        if war_id_value and isinstance(war_id_value, str) and war_id_value not in known:
            out.append(
                f"{label} references absorbed war_id {war_id_value!r} "
                f"that no longer resolves to any active or archived war_instance"
            )

    commitments = getattr(world, "diplomatic_commitments", None) or {}
    for cid, record in commitments.items():
        if isinstance(record, dict):
            _check(f"diplomatic_commitments[{cid!r}].war_id", record.get("war_id"))

    events = getattr(world, "pending_dispatch_events", None) or []
    for idx, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        _check(f"pending_dispatch_events[{idx}].war_id", event.get("war_id"))
        template_vars = event.get("template_vars")
        if isinstance(template_vars, dict):
            _check(
                f"pending_dispatch_events[{idx}].template_vars.war_id",
                template_vars.get("war_id"),
            )

    contribution = getattr(world, "war_contribution_scores", None)
    if isinstance(contribution, dict):
        for war_id in contribution.keys():
            _check(f"war_contribution_scores[{war_id!r}]", war_id)

    dialogues = getattr(world, "pending_settlement_dialogues", None)
    if isinstance(dialogues, dict):
        for key, entry in dialogues.items():
            if isinstance(entry, dict):
                _check(f"pending_settlement_dialogues[{key!r}].war_id", entry.get("war_id"))
    elif isinstance(dialogues, list):
        for idx, entry in enumerate(dialogues):
            if isinstance(entry, dict):
                _check(f"pending_settlement_dialogues[{idx}].war_id", entry.get("war_id"))

    routes = getattr(world, "settlement_route_payloads", None)
    if isinstance(routes, dict):
        for key, entry in routes.items():
            if isinstance(entry, dict):
                _check(f"settlement_route_payloads[{key!r}].war_id", entry.get("war_id"))
    elif isinstance(routes, list):
        for idx, entry in enumerate(routes):
            if isinstance(entry, dict):
                _check(f"settlement_route_payloads[{idx}].war_id", entry.get("war_id"))

    # Future hook (load-repair / debug-import): downgrade these violations
    # to a structured repair report. A3 leaves a comment marker; out of scope.

    return out


# ===========================================================================
# Slice A2: war-instance entry plumbing
# ===========================================================================


WAR_INSTANCE_SIDE_CONFLICT = "war_instance_side_conflict"
WAR_INSTANCE_MERGE_REQUIRED = "war_instance_merge_required"


@dataclass
class CascadeContext:
    """Transaction object threaded through `_process_war_cascade()`.

    Created at the root WAR seam (player/AI declaration, vassal rebellion,
    coalition declaration, paradox outcome, scripted/debug entry,
    combat-triggered auto-war fallback) before the cascade walk runs.
    Carries the allocated `war_id` plus the existing root-episode and
    war-entry-ledger transaction state. The dataclass keeps the cascade
    signature short — adding a new transaction-shaped value here is far
    safer than tacking it onto the cascade as a positional arg.
    """

    war_id: str = ""
    root_episode_id: Optional[str] = None
    root_aggressor: Optional[str] = None
    war_entry_entries: Optional[List[Dict[str, Any]]] = None
    ally_entry_decisions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    suppress_unresolved_offensive_cascade: bool = False


def _make_pair_key(nation_a: str, nation_b: str) -> str:
    return "|".join(sorted((nation_a, nation_b)))


def _find_active_war_instance_for_pair(world: Any, pair: str) -> Optional[str]:
    """Return the war_id of the active instance containing `pair`, or None."""
    for war_id, instance in _iter_active_war_instances(world):
        if pair in (instance.get("active_diplo_keys") or []):
            meta = (instance.get("diplo_key_meta") or {}).get(pair) or {}
            if meta.get("pair_status") in ("war", "armistice"):
                return war_id
    return None


def _active_war_ids_for_nation(world: Any, nation: str) -> List[str]:
    """Return war_ids of active instances where `nation` is an active participant."""
    out: List[str] = []
    for war_id, instance in _iter_active_war_instances(world):
        if nation in (instance.get("active_participants") or []):
            out.append(war_id)
    return out


def _instance_side(instance: Dict[str, Any], nation: str) -> Optional[str]:
    return (instance.get("side_by_nation") or {}).get(nation)


def _now_turn(world: Any) -> int:
    return int(getattr(world, "current_turn", 0) or 0)


def validate_war_declaration(
    world: Any,
    attacker: str,
    defender: str,
    *,
    entry_path: str,
    reason: str = "",
) -> Dict[str, Any]:
    """Pre-commit validation per spec §7.2 "Creation seam".

    Returns:
        ``{"ok": True, "war_id": existing_or_None, "merge_required": False}``
        on the simple success path, where ``war_id`` is set when the pair
        is already owned by an active instance and reuse is appropriate.

        ``{"ok": True, "war_id": None, "merge_required": True,
        "merge_candidates": [...], "details": {...}}`` when both nations
        already live in DIFFERENT active `war_instance` records. The
        caller (typically `ensure_war_instance_for_pair`) must invoke
        `merge_war_instances(...)` against the candidate ids before
        retrying validation.

        ``{"ok": False, "error": "war_instance_side_conflict",
        "details": {...}}`` when the proposed pair cannot be reconciled
        with existing side membership (e.g. self-war, or both nations on
        the same side of an existing instance). This stays a hard stop
        in A3 -- merge cannot fix sides that are intrinsically in
        conflict.
    """
    if not attacker or not defender or attacker == defender:
        return {
            "ok": False,
            "error": WAR_INSTANCE_SIDE_CONFLICT,
            "details": {
                "reason": "self_war",
                "entry_path": entry_path,
                "attacker": attacker,
                "defender": defender,
            },
        }

    pair = _make_pair_key(attacker, defender)
    existing_war_id = _find_active_war_instance_for_pair(world, pair)

    if existing_war_id is not None:
        # Pair already owned by an active instance: the existing instance's
        # side mapping is authoritative. Callers that re-trigger the same
        # pair (e.g. ARMISTICE -> WAR resumption, idempotent re-invocation)
        # may pass attacker/defender in either order; we only need to
        # confirm the two nations are on opposite sides of the existing
        # war_instance.
        instance = world.war_instances[existing_war_id]
        a_side = _instance_side(instance, attacker)
        d_side = _instance_side(instance, defender)
        if a_side and d_side and a_side != d_side:
            return {"ok": True, "war_id": existing_war_id, "merge_required": False}
        if a_side == d_side and a_side is not None:
            return {
                "ok": False,
                "error": WAR_INSTANCE_SIDE_CONFLICT,
                "details": {
                    "war_id": existing_war_id,
                    "attacker": attacker,
                    "attacker_side": a_side,
                    "defender": defender,
                    "defender_side": d_side,
                    "entry_path": entry_path,
                    "reason": (
                        f"both {attacker} and {defender} live on side "
                        f"{a_side!r} of war_instance {existing_war_id!r}"
                    ),
                },
            }
        # Side data is incomplete; trust the original pair_meta attacker/defender.
        return {"ok": True, "war_id": existing_war_id, "merge_required": False}

    attacker_war_ids = _active_war_ids_for_nation(world, attacker)
    defender_war_ids = _active_war_ids_for_nation(world, defender)
    common = set(attacker_war_ids) & set(defender_war_ids)

    if common:
        # Both nations already live in the SAME active instance, just not as
        # this pair. Side compatibility decides whether attaching is safe.
        for war_id in sorted(common):
            instance = world.war_instances[war_id]
            a_side = _instance_side(instance, attacker)
            d_side = _instance_side(instance, defender)
            if a_side == "attackers" and d_side == "defenders":
                return {"ok": True, "war_id": war_id, "merge_required": False}
            return {
                "ok": False,
                "error": WAR_INSTANCE_SIDE_CONFLICT,
                "details": {
                    "war_id": war_id,
                    "attacker": attacker,
                    "attacker_side": a_side,
                    "defender": defender,
                    "defender_side": d_side,
                    "entry_path": entry_path,
                    "reason": (
                        f"both nations live in war_instance {war_id!r} but "
                        f"the proposed (attacker={attacker!r}, "
                        f"defender={defender!r}) sides do not match"
                    ),
                },
            }

    if attacker_war_ids and defender_war_ids:
        return {
            "ok": True,
            "war_id": None,
            "merge_required": True,
            "merge_candidates": sorted(set(attacker_war_ids) | set(defender_war_ids)),
            "details": {
                "attacker_war_ids": sorted(attacker_war_ids),
                "defender_war_ids": sorted(defender_war_ids),
                "attacker": attacker,
                "defender": defender,
                "entry_path": entry_path,
                "reason": (
                    f"{attacker} and {defender} are active in different "
                    f"war_instance records; merge_war_instances() will "
                    f"consolidate before pair attachment"
                ),
            },
        }

    return {"ok": True, "war_id": None, "merge_required": False}


def _allocate_new_war_id(world: Any) -> tuple:
    next_id = int(getattr(world, "next_war_instance_id", 1) or 1)
    war_id = f"war_{next_id}"
    world.next_war_instance_id = next_id + 1
    return war_id, next_id


def _create_skeleton_instance(
    world: Any,
    attacker: str,
    defender: str,
    *,
    entry_path: str,
    root_episode_id: str,
) -> Dict[str, Any]:
    war_id, sequence = _allocate_new_war_id(world)
    pair = _make_pair_key(attacker, defender)
    turn = _now_turn(world)
    instance: Dict[str, Any] = {
        "war_id": war_id,
        "created_turn": turn,
        "created_sequence": sequence,
        "originator": attacker,
        "origin_target": defender,
        "origin_diplo_key": pair,
        "origin_episode_id": root_episode_id or "",
        "origin_entry_path": entry_path,
        "objective_keys": [pair],
        "active_diplo_keys": [pair],
        "resolved_diplo_keys": [],
        "diplo_key_meta": {
            pair: {
                "attacker": attacker,
                "defender": defender,
                "joined_turn": turn,
                "pair_status": "war",
                "resolved_turn": None,
                "entry_path": entry_path,
            },
        },
        "attacker_leader": attacker,
        "defender_leader": defender,
        "leader_source_by_side": {
            "attackers": "originator",
            "defenders": "origin_target",
        },
        "attackers": [attacker],
        "defenders": [defender],
        "side_by_nation": {attacker: "attackers", defender: "defenders"},
        "active_participants": [attacker, defender],
        "participant_meta": {
            attacker: {
                "side": "attackers",
                "joined_turn": turn,
                "exited_turn": None,
                "entry_path": entry_path,
            },
            defender: {
                "side": "defenders",
                "joined_turn": turn,
                "exited_turn": None,
                "entry_path": entry_path,
            },
        },
        "separate_peaced": [],
        "war_bargains": [],
        "ended_turn": None,
        "end_reason": None,
    }
    if not getattr(world, "war_instances", None):
        world.war_instances = {}
    world.war_instances[war_id] = instance
    if hasattr(world, "invalidate_war_instance_indexes"):
        world.invalidate_war_instance_indexes()
    return instance


def ensure_war_instance_for_pair(
    world: Any,
    attacker: str,
    defender: str,
    *,
    entry_path: str,
    root_episode_id: str = "",
    reason: str = "",
) -> Dict[str, Any]:
    """Allocate or reuse a `war_instance` for the (attacker, defender) pair.

    Spec §7.2 / §7.6 ownership rules:

    1. If the pair is already in an active instance, reuse it. Restore
       `pair_status="war"` if it was suspended at `armistice`.
    2. If both nations live in the same active instance with compatible
       sides (attacker on ``attackers`` and defender on ``defenders``),
       attach the new pair to it.
    3. If exactly one nation lives in an active instance whose existing
       side matches what this pair needs, attach to it (concurrent fronts
       under the same political conflict).
    4. If both nations live in *different* active instances, run the
       Slice A3 transitive merge transaction (`merge_war_instances`) to
       consolidate, then re-validate; the surviving instance becomes the
       reuse target.
    5. Otherwise allocate a fresh `war_instance` with the originator on
       the attackers side and the origin target on the defenders side.

    The validation step inside ``validate_war_declaration`` decides
    whether reuse / merge / fresh allocation is required BEFORE any state
    mutation. Side conflict (a nation that would land on both sides)
    remains a hard stop -- merge cannot reconcile incompatible sides.
    """
    validation = validate_war_declaration(
        world, attacker, defender, entry_path=entry_path, reason=reason,
    )
    if not validation.get("ok"):
        return validation

    # A3 §7.6: when both nations live in distinct active instances, run the
    # transitive merge transaction first, then re-validate. Side conflict
    # remains a hard stop.
    if validation.get("merge_required"):
        merge_result = merge_war_instances(
            world,
            candidate_war_ids=validation.get("merge_candidates") or [],
        )
        if not merge_result.get("ok"):
            return merge_result
        validation = validate_war_declaration(
            world, attacker, defender, entry_path=entry_path, reason=reason,
        )
        if not validation.get("ok") or validation.get("merge_required"):
            return validation

    pair = _make_pair_key(attacker, defender)
    turn = _now_turn(world)

    # 1. Reuse-by-pair (including ARMISTICE -> WAR resumption).
    existing_war_id = _find_active_war_instance_for_pair(world, pair)
    if existing_war_id is not None:
        instance = world.war_instances[existing_war_id]
        meta = instance.setdefault("diplo_key_meta", {}).setdefault(pair, {})
        prior_status = meta.get("pair_status")
        meta["pair_status"] = "war"
        meta["resolved_turn"] = None
        if hasattr(world, "invalidate_war_instance_indexes"):
            world.invalidate_war_instance_indexes()
        return {
            "ok": True,
            "war_id": existing_war_id,
            "instance": instance,
            "created_new": False,
            "reused": True,
            "armistice_resumed": prior_status == "armistice",
        }

    # 2. Both nations in the same active instance — just attach the pair.
    attacker_war_ids = _active_war_ids_for_nation(world, attacker)
    defender_war_ids = _active_war_ids_for_nation(world, defender)
    common = sorted(set(attacker_war_ids) & set(defender_war_ids))
    if common:
        war_id = common[0]
        attach_result = attach_pair_to_war_instance(
            world,
            war_id,
            attacker,
            defender,
            entry_path=entry_path,
            joined_turn=turn,
        )
        if not attach_result.get("ok"):
            return attach_result
        return {
            "ok": True,
            "war_id": war_id,
            "instance": world.war_instances[war_id],
            "created_new": False,
            "reused": True,
        }

    # 3. One-nation reuse: attach the new pair to the existing war if the
    #    side fits. Otherwise fall through to allocation (concurrent war).
    candidate_war_id: Optional[str] = None
    if attacker_war_ids and not defender_war_ids:
        for war_id in sorted(attacker_war_ids):
            instance = world.war_instances[war_id]
            if _instance_side(instance, attacker) == "attackers":
                candidate_war_id = war_id
                break
    elif defender_war_ids and not attacker_war_ids:
        for war_id in sorted(defender_war_ids):
            instance = world.war_instances[war_id]
            if _instance_side(instance, defender) == "defenders":
                candidate_war_id = war_id
                break

    if candidate_war_id is not None:
        attach_result = attach_pair_to_war_instance(
            world,
            candidate_war_id,
            attacker,
            defender,
            entry_path=entry_path,
            joined_turn=turn,
        )
        if attach_result.get("ok"):
            return {
                "ok": True,
                "war_id": candidate_war_id,
                "instance": world.war_instances[candidate_war_id],
                "created_new": False,
                "reused": True,
            }
        # Side conflict on attach — fall through to allocation, since the
        # nation's existing side cannot host this pair.

    # 4. Allocate a new war_instance.
    instance = _create_skeleton_instance(
        world,
        attacker,
        defender,
        entry_path=entry_path,
        root_episode_id=root_episode_id,
    )
    return {
        "ok": True,
        "war_id": instance["war_id"],
        "instance": instance,
        "created_new": True,
        "reused": False,
    }


def attach_pair_to_war_instance(
    world: Any,
    war_id: str,
    attacker: str,
    defender: str,
    *,
    entry_path: str,
    joined_turn: Optional[int] = None,
) -> Dict[str, Any]:
    """Attach a single bilateral pair to an existing active war_instance.

    Used by direct-entry seams (cascade attachment, ally entry, counter
    bargain acceptance, armistice resumption). Idempotent: re-attaching
    a pair that already has ``pair_status="war"`` is a no-op aside from
    refreshing the index dirty flag.

    A3: if the pair is already owned by a *different* active
    `war_instance`, the helper runs ``merge_war_instances(...)`` against
    the two candidates and retargets ``war_id`` to the survivor before
    completing the attachment. The result dict's ``war_id`` reflects the
    surviving id so cascade callers can update ``CascadeContext.war_id``.
    """
    if not war_id or war_id not in (getattr(world, "war_instances", None) or {}):
        return {"ok": False, "error": "unknown_war_id", "war_id": war_id}
    instance = world.war_instances[war_id]
    if instance.get("ended_turn") is not None:
        return {"ok": False, "error": "instance_ended", "war_id": war_id}
    if attacker == defender:
        return {
            "ok": False,
            "error": WAR_INSTANCE_SIDE_CONFLICT,
            "war_id": war_id,
            "details": {"reason": "self_war"},
        }

    pair = _make_pair_key(attacker, defender)
    turn = int(joined_turn if joined_turn is not None else _now_turn(world))
    existing_owner = _find_active_war_instance_for_pair(world, pair)
    if existing_owner is not None and existing_owner != war_id:
        # A3 §7.6: pair owned by a different active instance -- merge the two
        # connected components, retarget `war_id` to the survivor, and retry.
        merge_result = merge_war_instances(
            world,
            candidate_war_ids=[war_id, existing_owner],
        )
        if not merge_result.get("ok"):
            return merge_result
        surviving = merge_result.get("surviving_war_id") or war_id
        if surviving != war_id:
            war_id = surviving
            instance = world.war_instances.get(war_id)
            if instance is None or instance.get("ended_turn") is not None:
                return {"ok": False, "error": "instance_ended", "war_id": war_id}
        # After the merge, the pair is owned by the survivor. Continue with
        # the normal attach path so participant_meta / pair_status / index
        # invalidation all run as usual.

    side_by_nation = instance.setdefault("side_by_nation", {})
    attackers_list = instance.setdefault("attackers", [])
    defenders_list = instance.setdefault("defenders", [])
    active_pairs = instance.setdefault("active_diplo_keys", [])
    meta = instance.setdefault("diplo_key_meta", {})
    active_participants = instance.setdefault("active_participants", [])
    participant_meta = instance.setdefault("participant_meta", {})

    a_side = side_by_nation.get(attacker, "attackers")
    d_side = side_by_nation.get(defender, "defenders")
    if a_side == d_side:
        return {
            "ok": False,
            "error": WAR_INSTANCE_SIDE_CONFLICT,
            "war_id": war_id,
            "details": {
                "attacker": attacker,
                "attacker_side": a_side,
                "defender": defender,
                "defender_side": d_side,
                "reason": (
                    f"{attacker} and {defender} would both be on side "
                    f"{a_side!r} of war_instance {war_id!r}"
                ),
            },
        }

    side_by_nation[attacker] = a_side
    side_by_nation[defender] = d_side

    if a_side == "attackers" and attacker not in attackers_list:
        attackers_list.append(attacker)
    elif a_side == "defenders" and attacker not in defenders_list:
        defenders_list.append(attacker)
    if d_side == "defenders" and defender not in defenders_list:
        defenders_list.append(defender)
    elif d_side == "attackers" and defender not in attackers_list:
        attackers_list.append(defender)

    for nation, side in ((attacker, a_side), (defender, d_side)):
        if nation not in active_participants:
            active_participants.append(nation)
        participant_meta.setdefault(
            nation,
            {
                "side": side,
                "joined_turn": turn,
                "exited_turn": None,
                "entry_path": entry_path,
            },
        )

    if pair not in active_pairs:
        active_pairs.append(pair)
    # Restamp pair meta — handles ARMISTICE -> WAR resumption and ensures
    # joined_turn / pair_status reflect the live transition.
    existing_meta = meta.get(pair, {})
    meta[pair] = {
        "attacker": attacker,
        "defender": defender,
        "joined_turn": int(existing_meta.get("joined_turn", turn) or turn),
        "pair_status": "war",
        "resolved_turn": None,
        "entry_path": existing_meta.get("entry_path", entry_path),
    }

    if hasattr(world, "invalidate_war_instance_indexes"):
        world.invalidate_war_instance_indexes()
    return {"ok": True, "war_id": war_id, "instance": instance}


def attach_participant_to_war_instance(
    world: Any,
    war_id: str,
    nation: str,
    *,
    side: str,
    entry_path: str,
    joined_turn: Optional[int] = None,
) -> Dict[str, Any]:
    """Attach a nation as participant on a side without adding a new pair.

    Use when a nation joins a war without immediately adding a new
    bilateral pair (rare — most direct-entry seams attach a pair too).
    """
    if not war_id or war_id not in (getattr(world, "war_instances", None) or {}):
        return {"ok": False, "error": "unknown_war_id", "war_id": war_id}
    if side not in ("attackers", "defenders"):
        return {"ok": False, "error": "invalid_side", "war_id": war_id}
    instance = world.war_instances[war_id]
    if instance.get("ended_turn") is not None:
        return {"ok": False, "error": "instance_ended", "war_id": war_id}

    turn = int(joined_turn if joined_turn is not None else _now_turn(world))

    side_by_nation = instance.setdefault("side_by_nation", {})
    attackers_list = instance.setdefault("attackers", [])
    defenders_list = instance.setdefault("defenders", [])
    active_participants = instance.setdefault("active_participants", [])
    participant_meta = instance.setdefault("participant_meta", {})

    existing_side = side_by_nation.get(nation)
    if existing_side and existing_side != side:
        return {
            "ok": False,
            "error": WAR_INSTANCE_SIDE_CONFLICT,
            "war_id": war_id,
            "details": {
                "nation": nation,
                "existing_side": existing_side,
                "requested_side": side,
                "reason": (
                    f"{nation} already on {existing_side!r} side of "
                    f"war_instance {war_id!r}; cannot reassign"
                ),
            },
        }

    side_by_nation[nation] = side
    target_list = attackers_list if side == "attackers" else defenders_list
    if nation not in target_list:
        target_list.append(nation)
    if nation not in active_participants:
        active_participants.append(nation)
    participant_meta.setdefault(
        nation,
        {
            "side": side,
            "joined_turn": turn,
            "exited_turn": None,
            "entry_path": entry_path,
        },
    )

    if hasattr(world, "invalidate_war_instance_indexes"):
        world.invalidate_war_instance_indexes()
    return {"ok": True, "war_id": war_id, "instance": instance}


def resolve_pair_to_resolved(
    world: Any,
    pair: str,
    *,
    resolved_turn: Optional[int] = None,
) -> Dict[str, Any]:
    """Move ``pair`` from ``active_diplo_keys`` to ``resolved_diplo_keys``.

    Use for ``ARMISTICE -> PEACE`` and (eventually in Slice C) common-peace
    ratification. Stamps ``pair_status = "resolved"`` and ``resolved_turn``.
    Returns ``{"ok": True, "war_id": <id>}`` on success.
    """
    turn = int(resolved_turn if resolved_turn is not None else _now_turn(world))
    for war_id, instance in _iter_active_war_instances(world):
        active_pairs = instance.setdefault("active_diplo_keys", [])
        meta = instance.setdefault("diplo_key_meta", {})
        if pair in active_pairs:
            active_pairs.remove(pair)
            resolved_pairs = instance.setdefault("resolved_diplo_keys", [])
            if pair not in resolved_pairs:
                resolved_pairs.append(pair)
            pair_meta = meta.setdefault(pair, {})
            pair_meta["pair_status"] = "resolved"
            pair_meta["resolved_turn"] = turn
            # Spec §7.5: stamp ended_turn/end_reason when the last active pair
            # resolves. Other end_reasons (common_peace, separate_peace_finalized)
            # land in Slices C/D.
            if not active_pairs and instance.get("ended_turn") is None:
                instance["ended_turn"] = turn
                instance["end_reason"] = WAR_END_REASON_ALL_PAIRS_RESOLVED
            if hasattr(world, "invalidate_war_instance_indexes"):
                world.invalidate_war_instance_indexes()
            return {"ok": True, "war_id": war_id}
    return {"ok": False, "war_id": None, "error": "pair_not_owned"}


def mark_pair_armistice(
    world: Any,
    pair: str,
    *,
    suspended_turn: Optional[int] = None,
) -> Dict[str, Any]:
    """Set ``pair_status = "armistice"`` while keeping the pair active.

    Per spec §7.3 the pair stays in ``active_diplo_keys`` and the same
    ``war_id`` until it is later resolved or the armistice collapses
    back to WAR.
    """
    turn = int(suspended_turn if suspended_turn is not None else _now_turn(world))
    for war_id, instance in _iter_active_war_instances(world):
        meta = instance.setdefault("diplo_key_meta", {})
        active_pairs = instance.setdefault("active_diplo_keys", [])
        if pair in active_pairs and pair in meta:
            pair_meta = meta[pair]
            pair_meta["pair_status"] = "armistice"
            pair_meta["armistice_turn"] = turn
            if hasattr(world, "invalidate_war_instance_indexes"):
                world.invalidate_war_instance_indexes()
            return {"ok": True, "war_id": war_id}
    return {"ok": False, "war_id": None, "error": "pair_not_owned"}


# ===========================================================================
# Slice A3: merge / archive / leader / elimination
# ===========================================================================


_POWER_TIER_SCORE = {"major": 30, "secondary": 15, "minor": 5}
_DEFAULT_TIER_SCORE = _POWER_TIER_SCORE["secondary"]
WAR_END_REASON_ALL_PAIRS_RESOLVED = "all_pairs_resolved"
ARCHIVE_RETENTION_TURNS = 10


def war_leader_score(world: Any, nation: str, *, war_id: str, side: str) -> int:
    """Settlement-specific leader score per spec §7.4.

    Used for non-coalition leader replacement. Coalition-leader wars use
    `coalition.select_coalition_leader(...)` instead.

    Components, all null-safe:
    - power_tier weight (major=30, secondary=15, minor=5).
    - Contribution percentage on this `war_id` × 50, read from the optional
      Slice B `war_contribution_scores` container — defaults to 0 until
      Slice B lands.
    - Ally seat / consult / beneficiary flags from `participant_meta[nation]`
      contribute small additive bonuses (5 each).

    The score is the comparable signal; tie-break is owned by the caller
    (`_choose_leader_for_side` preserves current leader if eligible, else
    alphabetical stable nation id).
    """
    if not nation:
        return 0
    tier_getter = getattr(world, "get_power_tier", None)
    tier = tier_getter(nation) if callable(tier_getter) else None
    score = int(_POWER_TIER_SCORE.get(tier or "", _DEFAULT_TIER_SCORE))

    # Contribution percentage on this war_id (Slice B; null-safe before B).
    contribution_scores = getattr(world, "war_contribution_scores", None) or {}
    war_scores = contribution_scores.get(war_id) or {}
    contribution_pct = war_scores.get(nation)
    if isinstance(contribution_pct, (int, float)):
        score += int(contribution_pct * 50)

    # Ally seat / consult / beneficiary flags from participant_meta.
    instance = (getattr(world, "war_instances", None) or {}).get(war_id) or {}
    participant_meta = (instance.get("participant_meta") or {}).get(nation) or {}
    if participant_meta.get("ally_seat"):
        score += 5
    if participant_meta.get("consult"):
        score += 5
    if participant_meta.get("beneficiary"):
        score += 5

    return int(score)


def _side_members(instance: Dict[str, Any], side: str) -> List[str]:
    if side == "attackers":
        return list(instance.get("attackers") or [])
    if side == "defenders":
        return list(instance.get("defenders") or [])
    return []


def _choose_leader_for_side(
    world: Any,
    instance: Dict[str, Any],
    side: str,
) -> str:
    """Pick a leader for `side` of `instance` per spec §7.4.

    Side-scoped: each side reads its own `leader_source_by_side[side]`
    metadata. Coalition-source sides use `coalition.select_coalition_leader`;
    non-coalition sides use `war_leader_score()`. Tie-break: preserve the
    current leader if still an eligible same-side active participant; else
    choose the alphabetically earliest stable nation id.
    """
    members = _side_members(instance, side)
    if not members:
        return ""
    war_id = instance.get("war_id", "")
    leader_key = "attacker_leader" if side == "attackers" else "defender_leader"
    current_leader = instance.get(leader_key, "")

    if current_leader and current_leader in members:
        # Preserve current leader when still eligible (spec §7.4 tie-break).
        return current_leader

    source = (instance.get("leader_source_by_side") or {}).get(side, "")
    if source == "coalition_leader":
        try:
            from backend.game_logic.coalition import select_coalition_leader
        except Exception:
            select_coalition_leader = None  # type: ignore
        if callable(select_coalition_leader):
            picked = select_coalition_leader(members, world)
            if picked:
                return picked
        # Fall through to non-coalition scoring if coalition picker is unavailable.

    scored = [
        (-war_leader_score(world, nation, war_id=war_id, side=side), nation)
        for nation in members
    ]
    scored.sort()
    return scored[0][1] if scored else ""


def _rewrite_absorbed_war_id_in_bargains(
    world: Any,
    absorbed: Iterable[str],
    surviving: str,
) -> int:
    """Rewrite `bargain["war_id"]` from any absorbed id to `surviving`.

    Per spec §11.3 line 1573, `side_at_creation` and `side_leader_at_creation`
    are NOT rewritten — bargain promise context survives merges intact.
    Returns the count of rewritten records.
    """
    if not surviving:
        return 0
    absorbed_set = {a for a in absorbed if a and a != surviving}
    if not absorbed_set:
        return 0
    commitments = getattr(world, "diplomatic_commitments", None) or {}
    rewritten = 0
    for record in commitments.values():
        if not isinstance(record, dict):
            continue
        existing = record.get("war_id")
        if existing in absorbed_set:
            record["war_id"] = surviving
            rewritten += 1
    return rewritten


def _rewrite_absorbed_war_id_in_dispatch_events(
    world: Any,
    absorbed: Iterable[str],
    surviving: str,
) -> int:
    """Defensive walker for `pending_dispatch_events`.

    Dispatch events do not currently store `war_id` directly (per A3
    exploration); this walker rewrites any future `event["war_id"]` or
    `event["template_vars"]["war_id"]` field referencing absorbed ids so
    that future event types do not need a separate retrofit.
    """
    if not surviving:
        return 0
    absorbed_set = {a for a in absorbed if a and a != surviving}
    if not absorbed_set:
        return 0
    events = getattr(world, "pending_dispatch_events", None) or []
    rewritten = 0
    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get("war_id") in absorbed_set:
            event["war_id"] = surviving
            rewritten += 1
        template_vars = event.get("template_vars")
        if isinstance(template_vars, dict) and template_vars.get("war_id") in absorbed_set:
            template_vars["war_id"] = surviving
            rewritten += 1
    return rewritten


def _rewrite_absorbed_war_id_in_contribution(
    world: Any,
    absorbed: Iterable[str],
    surviving: str,
) -> int:
    """No-op-safe hook for the future Slice B `war_contribution_scores` container.

    Walks `world.war_contribution_scores` only if it exists; silently
    no-ops otherwise. When Slice B lands, post-merge standing uses the
    merged current-episode side denominator (spec line 101) — A3 only owns
    the `war_id` rewrite, not contribution accrual.
    """
    if not surviving:
        return 0
    absorbed_set = {a for a in absorbed if a and a != surviving}
    if not absorbed_set:
        return 0
    container = getattr(world, "war_contribution_scores", None)
    if not isinstance(container, dict):
        return 0
    rewritten = 0
    for absorbed_id in list(absorbed_set):
        if absorbed_id in container:
            absorbed_scores = container.pop(absorbed_id) or {}
            surviving_scores = container.setdefault(surviving, {})
            for nation, value in absorbed_scores.items():
                surviving_scores[nation] = (surviving_scores.get(nation) or 0) + (value or 0)
            rewritten += 1
    return rewritten


def _rewrite_absorbed_war_id_in_settlement_dialogues(
    world: Any,
    absorbed: Iterable[str],
    surviving: str,
) -> int:
    """No-op-safe hook for the future Slice C `pending_settlement_dialogues` container.

    Walks the container only if it exists. Slice C owns settlement dialogue
    creation / acceptance; A3 only rewrites the `war_id` reference.
    """
    if not surviving:
        return 0
    absorbed_set = {a for a in absorbed if a and a != surviving}
    if not absorbed_set:
        return 0
    container = getattr(world, "pending_settlement_dialogues", None)
    if container is None:
        return 0
    rewritten = 0
    if isinstance(container, dict):
        for entry in container.values():
            if isinstance(entry, dict) and entry.get("war_id") in absorbed_set:
                entry["war_id"] = surviving
                rewritten += 1
    elif isinstance(container, list):
        for entry in container:
            if isinstance(entry, dict) and entry.get("war_id") in absorbed_set:
                entry["war_id"] = surviving
                rewritten += 1
    return rewritten


def _rewrite_absorbed_war_id_in_route_payloads(
    world: Any,
    absorbed: Iterable[str],
    surviving: str,
) -> int:
    """No-op-safe hook for future Slice C settlement route payloads.

    Walks `world.settlement_route_payloads` only if it exists. Future
    settlement route payloads (e.g. `settlement_confirm` route data) may
    snapshot a `war_id`; this hook lets A3 rewrite them without inventing
    Slice C behavior.
    """
    if not surviving:
        return 0
    absorbed_set = {a for a in absorbed if a and a != surviving}
    if not absorbed_set:
        return 0
    container = getattr(world, "settlement_route_payloads", None)
    if container is None:
        return 0
    rewritten = 0
    if isinstance(container, dict):
        iterable = container.values()
    elif isinstance(container, list):
        iterable = container
    else:
        return 0
    for entry in iterable:
        if isinstance(entry, dict) and entry.get("war_id") in absorbed_set:
            entry["war_id"] = surviving
            rewritten += 1
    return rewritten


def _connected_component_war_ids(
    world: Any,
    seed_war_ids: Iterable[str],
) -> List[str]:
    """Expand `seed_war_ids` into all transitively connected active instances.

    Two active instances are connected if they share at least one active
    participant. The merge transaction operates on the full connected
    component so multi-instance chains collapse into one survivor.
    """
    instances = getattr(world, "war_instances", None) or {}
    queue = [w for w in seed_war_ids if w in instances and _is_active_instance(instances[w])]
    seen: set = set()
    while queue:
        war_id = queue.pop()
        if war_id in seen:
            continue
        seen.add(war_id)
        instance = instances.get(war_id) or {}
        participants = set(instance.get("active_participants") or [])
        for other_id, other_instance in instances.items():
            if other_id in seen or not _is_active_instance(other_instance):
                continue
            other_participants = set(other_instance.get("active_participants") or [])
            if participants & other_participants:
                queue.append(other_id)
    return sorted(seen)


def _pick_surviving_war_id(world: Any, candidate_ids: List[str]) -> str:
    """Pick the oldest war_id (smallest created_sequence; tie-break created_turn, war_id)."""
    instances = getattr(world, "war_instances", None) or {}
    def _key(war_id: str):
        instance = instances.get(war_id) or {}
        return (
            int(instance.get("created_sequence") or 0),
            int(instance.get("created_turn") or 0),
            war_id,
        )
    return sorted(candidate_ids, key=_key)[0]


def _validate_merged_sides(
    world: Any,
    component_ids: List[str],
) -> Dict[str, Any]:
    """Build a unified side_by_nation across all candidate instances; detect conflicts.

    Returns ``{"ok": True, "side_by_nation": {...}}`` if every nation lands
    on a single side across all instances, else
    ``{"ok": False, "error": WAR_INSTANCE_SIDE_CONFLICT, "details": {...}}``.

    Pure: NO mutation of world state.
    """
    instances = getattr(world, "war_instances", None) or {}
    unified: Dict[str, str] = {}
    conflicts: List[Dict[str, str]] = []
    for war_id in component_ids:
        instance = instances.get(war_id) or {}
        side_by_nation = instance.get("side_by_nation") or {}
        for nation, side in side_by_nation.items():
            if side not in ("attackers", "defenders"):
                continue
            existing = unified.get(nation)
            if existing is None:
                unified[nation] = side
            elif existing != side:
                conflicts.append({
                    "nation": nation,
                    "side_a": existing,
                    "side_b": side,
                    "war_id": war_id,
                })
    if conflicts:
        return {
            "ok": False,
            "error": WAR_INSTANCE_SIDE_CONFLICT,
            "details": {
                "conflicts": conflicts,
                "candidate_war_ids": list(component_ids),
                "reason": (
                    f"merge would put nation(s) on both sides: "
                    f"{', '.join(c['nation'] for c in conflicts)}"
                ),
            },
        }
    return {"ok": True, "side_by_nation": unified}


def _merge_instance_data(
    survivor: Dict[str, Any],
    absorbed: Dict[str, Any],
) -> None:
    """Fold `absorbed`'s state into `survivor` in-place.

    Survivor keeps its `war_id`, `created_sequence`, `created_turn`,
    `originator`, `origin_target`, `origin_diplo_key`, `origin_episode_id`,
    `origin_entry_path`, and `leader_source_by_side`. All other state is
    unioned (per spec §7.2 line 333: union of objective_keys, never one
    dominant).
    """
    for list_key in ("attackers", "defenders", "active_participants",
                     "active_diplo_keys", "resolved_diplo_keys",
                     "objective_keys", "separate_peaced", "war_bargains"):
        survivor_list = list(survivor.get(list_key) or [])
        seen = set(survivor_list)
        for item in absorbed.get(list_key) or []:
            if item not in seen:
                survivor_list.append(item)
                seen.add(item)
        survivor[list_key] = survivor_list

    survivor_side_by_nation = dict(survivor.get("side_by_nation") or {})
    for nation, side in (absorbed.get("side_by_nation") or {}).items():
        survivor_side_by_nation.setdefault(nation, side)
    survivor["side_by_nation"] = survivor_side_by_nation

    survivor_meta = dict(survivor.get("diplo_key_meta") or {})
    for pair, meta in (absorbed.get("diplo_key_meta") or {}).items():
        survivor_meta.setdefault(pair, dict(meta))
    survivor["diplo_key_meta"] = survivor_meta

    survivor_pmeta = dict(survivor.get("participant_meta") or {})
    for nation, meta in (absorbed.get("participant_meta") or {}).items():
        survivor_pmeta.setdefault(nation, dict(meta))
    survivor["participant_meta"] = survivor_pmeta


def merge_war_instances(
    world: Any,
    *,
    candidate_war_ids: Iterable[str],
    ctx: Optional[CascadeContext] = None,
) -> Dict[str, Any]:
    """Transitive merge transaction per spec §7.6.

    Steps (all-or-nothing — no partial state visible to readers):

    1. Compute the connected component over `candidate_war_ids`.
    2. Validate side assignments without mutation. Side conflict aborts
       with `war_instance_side_conflict`.
    3. Choose the oldest surviving `war_id` (smallest `created_sequence`).
    4. Merge participant / pair / episode data into a working copy.
    5. Choose leaders per side (`_choose_leader_for_side`).
    6. Rewrite absorbed `war_id` references on live containers.
    7. Run no-op-safe rewrite hooks for absent Slice B/C containers.
    8. Atomically replace survivor + remove absorbed instances.
    9. Invalidate `war_instances_by_leader` / `war_instances_by_participant`.
    10. Run `assert_war_instance_invariants(world, context="post_merge")`
        before returning.

    If `ctx` is provided and its `war_id` was absorbed, it is rewritten
    in-place to the surviving `war_id` so the cascade continues against
    the merged record.
    """
    seeds = [w for w in candidate_war_ids if w]
    if not seeds:
        return {"ok": True, "surviving_war_id": "", "absorbed_war_ids": [], "noop": True}

    component = _connected_component_war_ids(world, seeds)
    if not component:
        return {"ok": True, "surviving_war_id": "", "absorbed_war_ids": [], "noop": True}
    if len(component) == 1:
        return {
            "ok": True,
            "surviving_war_id": component[0],
            "absorbed_war_ids": [],
            "noop": True,
        }

    # Step 2: validate without mutation.
    validation = _validate_merged_sides(world, component)
    if not validation.get("ok"):
        return validation

    # Step 3: pick survivor.
    surviving_id = _pick_surviving_war_id(world, component)
    absorbed_ids = [w for w in component if w != surviving_id]

    # Step 4: merge into a working copy.
    instances = world.war_instances
    survivor_working = dict(instances[surviving_id])
    for absorbed_id in absorbed_ids:
        _merge_instance_data(survivor_working, instances[absorbed_id])

    # Step 5: choose leaders side-by-side.
    for side in ("attackers", "defenders"):
        leader_key = "attacker_leader" if side == "attackers" else "defender_leader"
        # Stage the working copy on world.war_instances so leader scoring
        # functions that read it observe the merged side rosters.
        instances[surviving_id] = survivor_working
        survivor_working[leader_key] = _choose_leader_for_side(world, survivor_working, side)

    # Step 6: rewrite live containers.
    _rewrite_absorbed_war_id_in_bargains(world, absorbed_ids, surviving_id)
    _rewrite_absorbed_war_id_in_dispatch_events(world, absorbed_ids, surviving_id)

    # Step 7: no-op-safe hooks for Slice B/C containers.
    _rewrite_absorbed_war_id_in_contribution(world, absorbed_ids, surviving_id)
    _rewrite_absorbed_war_id_in_settlement_dialogues(world, absorbed_ids, surviving_id)
    _rewrite_absorbed_war_id_in_route_payloads(world, absorbed_ids, surviving_id)

    # Step 8: atomic swap.
    instances[surviving_id] = survivor_working
    for absorbed_id in absorbed_ids:
        instances.pop(absorbed_id, None)

    # Step 9: invalidate indexes.
    if hasattr(world, "invalidate_war_instance_indexes"):
        world.invalidate_war_instance_indexes()

    # Cascade-context drift: rewrite ctx.war_id if it was absorbed.
    if ctx is not None and ctx.war_id in absorbed_ids:
        ctx.war_id = surviving_id

    # Step 10: post-merge invariant.
    assert_war_instance_invariants(world, context="post_merge")

    return {
        "ok": True,
        "surviving_war_id": surviving_id,
        "absorbed_war_ids": absorbed_ids,
        "noop": False,
    }


def mark_participant_eliminated_in_all_wars(
    world: Any,
    nation: str,
) -> Dict[str, Any]:
    """Spec §7.4 elimination exit.

    For every active war_instance the nation participates in, stamp
    `participant_meta[nation]["exited_turn"] = current_turn` and
    `["exit_path"] = "eliminated"`, remove the nation from `attackers` /
    `defenders` / `active_participants` / `side_by_nation`, and re-pick the
    side leader if the nation was a leader. NO separate-peace reaction is
    emitted (per spec line 107).
    """
    if not nation:
        return {"ok": True, "war_ids_touched": []}
    instances = getattr(world, "war_instances", None) or {}
    turn = _now_turn(world)
    touched: List[str] = []
    for war_id, instance in list(instances.items()):
        if not _is_active_instance(instance):
            continue
        participants = instance.get("active_participants") or []
        if nation not in participants:
            continue

        participant_meta = instance.setdefault("participant_meta", {})
        meta = participant_meta.setdefault(nation, {})
        meta["exited_turn"] = turn
        meta["exit_path"] = "eliminated"

        for list_key in ("attackers", "defenders", "active_participants"):
            if nation in (instance.get(list_key) or []):
                instance[list_key] = [n for n in instance[list_key] if n != nation]

        side_by_nation = instance.setdefault("side_by_nation", {})
        side_by_nation.pop(nation, None)

        for leader_key, side in (("attacker_leader", "attackers"),
                                 ("defender_leader", "defenders")):
            if instance.get(leader_key) == nation:
                instance[leader_key] = _choose_leader_for_side(world, instance, side)

        touched.append(war_id)

    if touched and hasattr(world, "invalidate_war_instance_indexes"):
        world.invalidate_war_instance_indexes()

    return {"ok": True, "war_ids_touched": touched}


def archive_terminal_war_instances(world: Any) -> Dict[str, Any]:
    """Spec §7.5 archive compaction.

    Move every `war_instance` whose `(current_turn - ended_turn) >=
    ARCHIVE_RETENTION_TURNS` from `world.war_instances` into
    `world.archived_war_instances`. The terminal record stays queryable
    while `current_turn - ended_turn < 10` so contribution / settlement /
    dispatch / ledger readers can resolve recent references.
    """
    instances = getattr(world, "war_instances", None) or {}
    archive_list = getattr(world, "archived_war_instances", None)
    if archive_list is None:
        world.archived_war_instances = []
        archive_list = world.archived_war_instances
    turn = _now_turn(world)
    archived_ids: List[str] = []
    for war_id in list(instances.keys()):
        instance = instances[war_id]
        ended_turn = instance.get("ended_turn")
        if ended_turn is None:
            continue
        if turn - int(ended_turn) >= ARCHIVE_RETENTION_TURNS:
            from copy import deepcopy
            archive_list.append(deepcopy(instance))
            del instances[war_id]
            archived_ids.append(war_id)
    if archived_ids and hasattr(world, "invalidate_war_instance_indexes"):
        world.invalidate_war_instance_indexes()
    return {"ok": True, "archived_war_ids": archived_ids}


__all__ = [
    "ARCHIVE_RETENTION_TURNS",
    "WAR_END_REASON_ALL_PAIRS_RESOLVED",
    "WAR_INSTANCE_MERGE_REQUIRED",
    "WAR_INSTANCE_SIDE_CONFLICT",
    "CascadeContext",
    "WarInstanceInvariantError",
    "archive_terminal_war_instances",
    "assert_war_instance_invariants",
    "attach_pair_to_war_instance",
    "attach_participant_to_war_instance",
    "ensure_war_instance_for_pair",
    "mark_pair_armistice",
    "mark_participant_eliminated_in_all_wars",
    "merge_war_instances",
    "resolve_pair_to_resolved",
    "validate_war_declaration",
    "war_leader_score",
]


# Type-checker friendly re-export retained from Slice A1 module surface.
Optional  # noqa: F401 - kept for stable module surface across slices
