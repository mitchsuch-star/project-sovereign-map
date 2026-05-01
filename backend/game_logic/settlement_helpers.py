"""Imperial Settlement / Ally Participation foundation helpers.

Slice A1 shipped the war-instance invariant assertion. Slice A2 adds the
war-entry plumbing every WAR seam must use to allocate, reuse, and attach
to `war_instance` records:

- `CascadeContext` — transaction object that travels through
  `_process_war_cascade()` so the cascade signature does not grow past
  nine positional arguments.
- `validate_war_declaration(...)` — pre-commit check that fails fast with
  `war_instance_side_conflict` or `war_instance_merge_required` before
  `set_diplomatic_state(..., "WAR", ...)` mutates state.
- `ensure_war_instance_for_pair(...)` — owns declaration / cascade
  creation. Either creates a skeleton instance, reuses a compatible
  active instance, or returns a hard stop.
- `attach_pair_to_war_instance(...)` and
  `attach_participant_to_war_instance(...)` — narrower helpers used by
  direct-entry seams (cascade attachment, ally entry, counter bargain,
  armistice resumption, vassal rebellion).
- `resolve_pair_to_resolved(...)` and `mark_pair_armistice(...)` —
  pair-status transitions for `ARMISTICE -> PEACE` and `WAR -> ARMISTICE`
  paths.

Per `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.24 §7.2 / §7.3 these
helpers must be empty-safe (work on a world with `war_instances == {}`
or no live diplomatic_states), idempotent (re-attaching the same pair is
a no-op), and they must invalidate the lazy
`war_instances_by_leader` / `war_instances_by_participant` indexes after
mutation.

Slice A3 promotes `assert_war_instance_invariants` into an always-on
post-merge assertion and adds connected-component merge support; A2
deliberately stops short of merge — both nations already living in
distinct active `war_instance` records is treated as a hard-stop
diagnostic so callers can fix the seam before A3.
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

    if violations:
        raise WarInstanceInvariantError(
            "assert_war_instance_invariants failed in context "
            f"{context!r}: {len(violations)} violation(s):\n  - "
            + "\n  - ".join(violations),
            context=context,
            violations=violations,
        )


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
        ``{"ok": True, "war_id": existing_or_None}`` on success, where
        ``war_id`` is set when the pair is already owned by an active
        instance and reuse is appropriate. Otherwise
        ``{"ok": False, "error": ..., "details": {...}}`` with one of:
        ``war_instance_side_conflict`` (sides cannot be reconciled) or
        ``war_instance_merge_required`` (both nations already live in
        DIFFERENT active `war_instance` records and connecting the new
        pair would require an A3 merge transaction).
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
            "ok": False,
            "error": WAR_INSTANCE_MERGE_REQUIRED,
            "details": {
                "attacker_war_ids": sorted(attacker_war_ids),
                "defender_war_ids": sorted(defender_war_ids),
                "attacker": attacker,
                "defender": defender,
                "entry_path": entry_path,
                "reason": (
                    f"{attacker} and {defender} are active in different "
                    f"war_instance records; A2 hard-stops, A3 implements "
                    f"the connected-component merge"
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

    Spec §7.2 ownership rules:

    1. If the pair is already in an active instance, reuse it. Restore
       `pair_status="war"` if it was suspended at `armistice`.
    2. If both nations live in the same active instance with compatible
       sides (attacker on ``attackers`` and defender on ``defenders``),
       attach the new pair to it.
    3. If exactly one nation lives in an active instance whose existing
       side matches what this pair needs, attach to it (concurrent fronts
       under the same political conflict).
    4. If both nations live in different active instances, return a
       ``war_instance_merge_required`` hard stop — A3 implements merge.
    5. Otherwise allocate a fresh `war_instance` with the originator on
       the attackers side and the origin target on the defenders side.

    The validation step inside ``validate_war_declaration`` decides
    whether reuse / attach is safe BEFORE any state mutation.
    """
    validation = validate_war_declaration(
        world, attacker, defender, entry_path=entry_path, reason=reason,
    )
    if not validation.get("ok"):
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


__all__ = [
    "WAR_INSTANCE_MERGE_REQUIRED",
    "WAR_INSTANCE_SIDE_CONFLICT",
    "CascadeContext",
    "WarInstanceInvariantError",
    "assert_war_instance_invariants",
    "attach_pair_to_war_instance",
    "attach_participant_to_war_instance",
    "ensure_war_instance_for_pair",
    "mark_pair_armistice",
    "resolve_pair_to_resolved",
    "validate_war_declaration",
]


# Type-checker friendly re-export retained from Slice A1 module surface.
Optional  # noqa: F401 - kept for stable module surface across slices
