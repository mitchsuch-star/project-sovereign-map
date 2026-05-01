"""Imperial Settlement / Ally Participation foundation helpers (Slice A1).

This module hosts pure helpers consumed across slices A2, A3, B, C, and D.
Slice A1 is foundation-only: no behavioral settlement logic ships here.
The current surface is the war-instance invariant assertion described in
`WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §7.2 and §7.4 footnotes.

Spec contract for `assert_war_instance_invariants`:

- Every `diplomatic_states[diplo_key] == "WAR"` MUST appear in exactly one
  active `war_instance.active_diplo_keys` with
  `diplo_key_meta[diplo_key]["pair_status"] == "war"`.
- No active `war_instance` may claim a non-`WAR` pair as
  `pair_status == "war"`.
- `side_by_nation` MUST agree with `attackers` / `defenders` membership and
  no nation may appear on both sides of the same active `war_instance`.

A3 promotes this to an always-on post-merge assertion; A2 already needs it
to guard direct-entry / cascade attachment. A1 ships the helper so slices
B, C, and D can build their fixtures against a stable invariant API.
"""

from __future__ import annotations

from typing import Any, Iterable, List, Optional


def _is_active_instance(instance: Any) -> bool:
    return isinstance(instance, dict) and instance.get("ended_turn") is None


def _iter_active_war_instances(world: Any) -> Iterable:
    instances = getattr(world, "war_instances", None) or {}
    for war_id, instance in instances.items():
        if _is_active_instance(instance):
            yield war_id, instance


class WarInstanceInvariantError(AssertionError):
    """Raised when `assert_war_instance_invariants` finds a violation.

    Inherits from `AssertionError` so existing test/debug paths that catch
    `AssertionError` continue to work; downstream load-repair tooling can
    catch this specific class to downgrade to a structured repair report
    per spec §7.2 ("only explicit load-repair/debug-import tooling may
    downgrade it to a structured repair report").
    """

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

    Parameters
    ----------
    world : WorldState-like
        Object exposing `war_instances` and `diplomatic_states`.
    context : str
        Caller-supplied label (e.g. ``"post_merge"``, ``"declaration"``,
        ``"load"``). Used in the violation message to make the failing seam
        legible. Slice A1 calls this with ``"general"`` (empty world / 20-
        instance fixture); A2/A3/B/C/D add their own context labels.

    Raises
    ------
    WarInstanceInvariantError
        On any invariant violation. The exception message lists every
        violation found (the helper does not short-circuit on the first
        finding so test output is actionable).

    Notes
    -----
    Slice A1 only invokes this against an empty world and the synthetic
    20-instance fixture. The invariant must therefore be tolerant of
    `war_instances == {}` and the absence of a `diplomatic_states` map.
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

        # Side-disjointness invariant.
        attackers = set(instance.get("attackers") or [])
        defenders = set(instance.get("defenders") or [])
        overlap = attackers & defenders
        if overlap:
            violations.append(
                f"war_instance {war_id!r} has nation(s) on both sides: "
                f"{sorted(overlap)}"
            )

        # `side_by_nation` agreement.
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

        # Active pair ownership and pair_status agreement.
        for pair in active_pairs:
            pair_status = (meta.get(pair) or {}).get("pair_status")
            if pair_status == "war":
                # Duplicate active ownership across war_instances.
                if pair in pair_owners:
                    violations.append(
                        f"diplo_key {pair!r} is claimed by both "
                        f"war_instance {pair_owners[pair]!r} and {war_id!r}"
                    )
                else:
                    pair_owners[pair] = war_id
                # Must correspond to a WAR pair in diplomatic_states.
                if diplomatic_states and pair not in war_pairs:
                    violations.append(
                        f"war_instance {war_id!r} claims pair {pair!r} as "
                        f"pair_status='war' but diplomatic_states does not "
                        f"have it as WAR"
                    )
            elif pair_status == "armistice":
                # ARMISTICE pairs stay in active_diplo_keys per §7.3 but
                # do not contend for the WAR ownership invariant. Still
                # accumulate ownership so we can detect duplicates if they
                # ever resume.
                pass
            elif pair_status == "resolved":
                violations.append(
                    f"war_instance {war_id!r} keeps resolved pair {pair!r} "
                    f"in active_diplo_keys; resolved pairs must move to "
                    f"resolved_diplo_keys per spec §7.3"
                )

    # Every WAR pair must be owned by exactly one active war_instance with
    # pair_status='war'.
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


__all__ = [
    "WarInstanceInvariantError",
    "assert_war_instance_invariants",
]


# Type-checker friendly re-export for downstream slices that prefer typing.
Optional  # noqa: F401 - kept for stable module surface across slices
