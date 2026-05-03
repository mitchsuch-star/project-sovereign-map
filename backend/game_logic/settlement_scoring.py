"""Imperial Settlement common-peace scoring (Slice C1a foundation).

This module owns the pure side-pressure helpers consumed by common-peace
acceptance, direct-score gates, territory legitimacy `weak_pressure_penalty`
checks, and advisory rows per `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md`
§6.3 / §12.2 and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md`
Slice C1.

C1a foundation (this commit) ships the reusable building blocks before the
full common-peace acceptance formula lands in C1b:

- `compute_direct_scores_by_enemy(...)` builds the
  `{covered_enemy: {proposer_side_member: war_score}}` map once per
  settlement evaluation. Settlement preview / confirm callers MUST build
  this map before any `max()` call (spec §6.3 line 237). Pairs that are not
  currently `WAR` per `world.is_at_war(...)` are excluded — this matches
  the spec's `if world.is_at_war(side_member, enemy)` filter.

- `select_direct_score(...)` chooses each covered enemy's `direct_score`
  via `max(active_pairs)` with a deterministic alphabetical tie-break and
  reports the chosen `direct_score_source` (the proposer-side member whose
  war score was selected) so debug output names the source per spec line
  243.

- `compute_side_pressure_score(...)` is the spec §6.3 power-weighted
  average. It accepts a pre-computed `direct_scores` map so settlement
  preview / confirm can memoize once per
  `(war_id, proposer_side, covered_enemy_participants, current_turn,
  draft_terms_hash)` evaluation per spec line 238. When `direct_scores` is
  not supplied the helper computes the map itself for ad-hoc callers
  (tests, advisory previews against synthetic war_instances).

The C1b sub-gate will layer the common-peace acceptance formula
(`base_side_pressure`, `term_harshness_penalty`, leader-own-loss clamp,
burdened-participant penalty, projected-hegemony / forced-alliance threat,
war-objective alignment, war exhaustion, abandoned-by-ally) on top of
these helpers. The C1a helpers are intentionally pure: no mutation of
world state, no ratification, no side-effects. They never call into
diplomacy ratification paths.

Spec hard stops surfaced here:

- `no_covered_enemy_participants` — empty covered enemy set is invalid
  before scoring (spec §6.3 line 235 / §10.4 confirm revalidation).
- `no_direct_war_score_for_covered_enemy` — a covered enemy with no
  active proposer-side war pair is a hard stop for that enemy
  (spec §6.3 line 237).

Performance: every helper is O(|proposer_side| * |covered_enemies|) with
no per-region scans, no `world.regions.values()` walks, and no repeated
`get_war_score_for(...)` calls inside the same evaluation when callers
pass the memoized `direct_scores` map.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


# ===========================================================================
# Spec constants (§6.3)
# ===========================================================================

# Power-tier weights for the side-pressure power-weighted average.
POWER_TIER_WEIGHTS: Dict[str, int] = {
    "major": 3,
    "secondary": 2,
    "minor": 1,
}

# Spec §0 / §6.3 power-tier fallback. `world.get_power_tier(nation)` returns
# `None` for nations without authored scenario data; callers downstream of
# `get_power_tier()` apply this default per `docs/SCALE_READINESS_PLAN.md`
# §"Phase 0 Cross-Cutting Taxonomy".
DEFAULT_POWER_TIER = "secondary"

# War score range per `backend/game_logic/diplomacy.py::calculate_war_score`.
WAR_SCORE_MIN = -100
WAR_SCORE_MAX = 100

# Hard-stop reasons (spec §6.3 / §10.4)
HARD_STOP_NO_COVERED_ENEMY = "no_covered_enemy_participants"
HARD_STOP_NO_DIRECT_WAR_SCORE = "no_direct_war_score_for_covered_enemy"

# Recognized side strings on `war_instance` records.
_VALID_SIDES = {"attackers", "defenders"}


# ===========================================================================
# Public helpers
# ===========================================================================


def power_tier_weight(world: Any, nation: str) -> int:
    """Return the spec §6.3 power-tier weight for `nation`.

    Falls back to ``DEFAULT_POWER_TIER`` (secondary, weight 2) when
    ``world.get_power_tier(...)`` returns ``None`` or an unrecognized tier
    string. Matches `(world.get_power_tier(n) or "secondary")` convention
    from `world_state.py::get_power_tier` docstring.
    """
    tier_getter = getattr(world, "get_power_tier", None)
    tier = tier_getter(nation) if callable(tier_getter) else None
    return POWER_TIER_WEIGHTS.get(tier or DEFAULT_POWER_TIER, POWER_TIER_WEIGHTS[DEFAULT_POWER_TIER])


def _proposer_side_members(
    war_instance: Mapping[str, Any],
    proposer_side: str,
) -> List[str]:
    if proposer_side not in _VALID_SIDES:
        raise ValueError(
            f"proposer_side must be 'attackers' or 'defenders', got {proposer_side!r}"
        )
    members = war_instance.get(proposer_side) or []
    return [str(n) for n in members]


def compute_direct_scores_by_enemy(
    world: Any,
    war_instance: Mapping[str, Any],
    *,
    proposer_side: str,
    covered_enemy_participants: Iterable[str],
) -> Dict[str, Dict[str, int]]:
    """Build the canonical ``{enemy: {side_member: war_score}}`` map.

    Spec §6.3 contract:

    - Iterates only proposer-side participants currently at WAR with each
      covered enemy (`world.is_at_war(side_member, enemy)`); ARMISTICE,
      PEACE, ALLIANCE, and any non-WAR pairs are excluded.
    - The returned map is keyed by every requested covered enemy, even
      when the inner dict is empty. Callers detect the
      ``no_direct_war_score_for_covered_enemy`` hard stop by checking for
      an empty inner dict — this keeps the spec's "build before max()"
      ordering (line 237) explicit at the call site.
    - Scores are returned as raw `get_war_score_for(...)` integers; the
      side-pressure aggregator clamps the rounded average to
      ``[WAR_SCORE_MIN, WAR_SCORE_MAX]``.

    The helper is pure: no mutation of `world`, no mutation of
    `war_instance`, no `world.war_scores` writes.
    """
    from backend.game_logic.diplomacy import get_war_score_for

    side_members = _proposer_side_members(war_instance, proposer_side)
    direct_scores: Dict[str, Dict[str, int]] = {}
    for enemy in covered_enemy_participants:
        enemy_str = str(enemy)
        per_member: Dict[str, int] = {}
        for member in side_members:
            if member == enemy_str:
                # A nation cannot pressure itself; skip without raising so
                # malformed callers (same nation in both sets) are simply
                # excluded rather than crashing the preview.
                continue
            try:
                at_war = bool(world.is_at_war(member, enemy_str))
            except Exception:
                at_war = False
            if not at_war:
                continue
            score = int(get_war_score_for(world, member, enemy_str))
            per_member[member] = score
        direct_scores[enemy_str] = per_member
    return direct_scores


def select_direct_score(
    direct_scores_for_enemy: Mapping[str, int],
) -> Optional[Tuple[int, str]]:
    """Return ``(direct_score, direct_score_source)`` per spec §6.3 line 243.

    The selected score is ``max(active_pairs)``; ties break alphabetically
    on the proposer-side member name so debug output is deterministic and
    settlement reviews regenerate identically across reruns.

    Returns ``None`` when the inner map is empty so callers can surface
    the ``no_direct_war_score_for_covered_enemy`` hard stop without
    inventing a score.
    """
    if not direct_scores_for_enemy:
        return None
    # Sort by (-score, name) so highest score wins; alphabetical tie-break.
    best = min(
        direct_scores_for_enemy.items(),
        key=lambda kv: (-int(kv[1]), str(kv[0])),
    )
    name, score = best
    return int(score), str(name)


def _round_half_away_from_zero(value: float) -> int:
    """Spec §6.3 ``round()`` — Python's banker's rounding deviates from
    most spec-author intuition for ``.5`` cases. Side-pressure aggregation
    uses traditional half-away-from-zero rounding so the worked Pressburg
    example in spec line 1153 reproduces exactly.
    """
    if value >= 0:
        return int(value + 0.5)
    return -int(-value + 0.5)


def compute_side_pressure_score(
    world: Any,
    war_instance: Mapping[str, Any],
    *,
    proposer_side: str,
    covered_enemy_participants: Iterable[str],
    direct_scores: Optional[Mapping[str, Mapping[str, int]]] = None,
) -> Dict[str, Any]:
    """Spec §6.3 power-weighted-average side-pressure score.

    Returns a dict with the canonical settlement-preview shape:

        {
            "score": int | None,
            "hard_stops": List[{"reason": str, "enemy": str | None}],
            "direct_scores": {enemy: {side_member: score}},
            "direct_score_sources": {
                enemy: {"score": int, "source": str, "weight": int},
            },
            "pressure_terms": [(score, weight), ...],
        }

    On hard stop the ``score`` field is ``None`` and ``hard_stops`` lists
    every detected reason in the order they were detected. Callers that
    want a fail-fast contract should check ``hard_stops`` before reading
    ``score``.

    When ``direct_scores`` is provided the helper trusts the caller's
    memoized map and does NOT recompute via `get_war_score_for`. This is
    the path used by settlement preview/confirm so a single evaluation
    walks war scores at most once per
    ``(war_id, proposer_side, covered_enemy_participants, current_turn,
    draft_terms_hash)`` per spec §6.3 line 238.

    The score is rounded with traditional half-away-from-zero and clamped
    to ``[WAR_SCORE_MIN, WAR_SCORE_MAX]`` per spec §6.3 line 239.
    """
    covered = [str(n) for n in covered_enemy_participants]
    hard_stops: List[Dict[str, Any]] = []

    if not covered:
        hard_stops.append({"reason": HARD_STOP_NO_COVERED_ENEMY, "enemy": None})
        return {
            "score": None,
            "hard_stops": hard_stops,
            "direct_scores": {},
            "direct_score_sources": {},
            "pressure_terms": [],
        }

    if direct_scores is None:
        direct_scores_map = compute_direct_scores_by_enemy(
            world,
            war_instance,
            proposer_side=proposer_side,
            covered_enemy_participants=covered,
        )
    else:
        # Trust caller-supplied map but coerce to the canonical shape so
        # downstream pressure-term aggregation reads consistently.
        direct_scores_map = {
            str(enemy): {str(k): int(v) for k, v in (per_member or {}).items()}
            for enemy, per_member in direct_scores.items()
        }
        # Make sure every covered enemy has at least an empty inner map so
        # the hard-stop scan below names the missing enemy explicitly.
        for enemy in covered:
            direct_scores_map.setdefault(enemy, {})

    direct_score_sources: Dict[str, Dict[str, Any]] = {}
    pressure_terms: List[Tuple[int, int]] = []

    for enemy in covered:
        per_member = direct_scores_map.get(enemy) or {}
        selection = select_direct_score(per_member)
        if selection is None:
            hard_stops.append(
                {"reason": HARD_STOP_NO_DIRECT_WAR_SCORE, "enemy": enemy}
            )
            continue
        direct_score, source = selection
        weight = power_tier_weight(world, enemy)
        direct_score_sources[enemy] = {
            "score": direct_score,
            "source": source,
            "weight": weight,
        }
        pressure_terms.append((direct_score, weight))

    if hard_stops or not pressure_terms:
        return {
            "score": None,
            "hard_stops": hard_stops,
            "direct_scores": direct_scores_map,
            "direct_score_sources": direct_score_sources,
            "pressure_terms": pressure_terms,
        }

    weighted_sum = sum(score * weight for score, weight in pressure_terms)
    weight_sum = sum(weight for _, weight in pressure_terms)
    raw_average = weighted_sum / weight_sum
    rounded = _round_half_away_from_zero(raw_average)
    clamped = max(WAR_SCORE_MIN, min(WAR_SCORE_MAX, rounded))

    return {
        "score": int(clamped),
        "hard_stops": hard_stops,
        "direct_scores": direct_scores_map,
        "direct_score_sources": direct_score_sources,
        "pressure_terms": pressure_terms,
    }
