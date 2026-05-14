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

# SC-4: canonical hard-stop codes. Unknown codes fail closed.
SETTLEMENT_HARD_STOP_CODES = frozenset({
    HARD_STOP_NO_COVERED_ENEMY,
    HARD_STOP_NO_DIRECT_WAR_SCORE,
})

# SC-1: canonical clause types and required keys per spec table.
CANONICAL_CLAUSE_TYPES = {
    "peace": {"required": {"type"}, "optional": set()},
    "territory_cede": {"required": {"type", "from", "to", "region"}, "optional": set()},
    "gold_indemnity": {"required": {"type", "from", "to", "amount"}, "optional": set()},
    "gold_per_turn": {"required": {"type", "from", "to", "amount", "turns"}, "optional": set()},
    "forced_alliance": {"required": {"type", "from", "to"}, "optional": {"includes_continental_system"}},
    "vassalage": {"required": {"type", "from", "to"}, "optional": set()},
    "subjugation": {"required": {"type", "from", "to"}, "optional": set()},
    "liberation": {"required": {"type", "vassal_nation", "lord_nation", "liberator"}, "optional": set()},
}

# G2-Slice-1 live MVP clause types.
SETTLEMENT_MVP_CLAUSE_TYPES = frozenset({
    "peace", "territory_cede", "gold_indemnity", "forced_alliance",
})

CLAUSE_CONTROL_SCHEMA = {
    clause_type: {
        "type": clause_type,
        "required_keys": sorted(spec["required"]),
        "optional_keys": sorted(spec["optional"]),
        "enabled": clause_type in SETTLEMENT_MVP_CLAUSE_TYPES,
        "visibility": "live" if clause_type in SETTLEMENT_MVP_CLAUSE_TYPES else "hidden",
    }
    for clause_type, spec in CANONICAL_CLAUSE_TYPES.items()
}

MAX_SETTLEMENT_CLAUSE_COUNT = 8

# SC-1: clause conflict matrix. Each entry is (type_a, type_b, match_keys)
# where the pair conflicts when both exist and the match_keys values agree.
CLAUSE_CONFLICT_MATRIX = [
    ("vassalage", "forced_alliance", ("from", "to")),
    ("vassalage", "subjugation", ("from", "to")),
    ("subjugation", "forced_alliance", ("from", "to")),
]

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
    for enemy in sorted({str(n) for n in covered_enemy_participants}):
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
    covered = sorted({str(n) for n in covered_enemy_participants})
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


# ===========================================================================
# Slice C1b — Common-peace acceptance formula
# ===========================================================================
#
# `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §6.acceptance lines 1095-1147.
# C1b layers the acceptance formula on top of the C1a side-pressure helpers
# above. It is intentionally pure: no mutation of `world` / `war_instance`,
# no ratification, no live wiring into `diplomacy.py` or
# `diplomatic_templates.py`. C2 (endpoints / dialogue / Godot routing)
# wires preview / confirm against this helper.
#
# Component pipeline (spec line 1097-1107) — note that CLAUDE.md "Up Next"
# names eight components, but the spec lists nine including
# `settlement_tier_legitimacy` (line 1099, 1114). The Pressburg worked
# example at line 1162 totals 58 only when tier legitimacy is included
# (`46 + 10 - 11 + 0 - 10 + 15 - 5 + 13 + 0 = 58`), so C1b ships the full
# nine-component spec table and uses the existing
# `diplomacy.get_settlement_tier()` to classify the package by
# `abs(side_pressure_score)`.
#
# Performance: every component reads cached helpers
# (`get_nation_regions`, `get_bloc_members`, `get_active_nations`,
# `get_power_tier`) and reuses the C1a-memoized `direct_scores` map.
# `project_balance_after_settlement()` deep-copies projection scratch dicts
# only for the affected nations and never iterates `world.regions.values()`
# (CLAUDE.md golden rule 8).

# --- Component constants (spec §6.acceptance line 1109-1147) -----------------

BASE_SIDE_PRESSURE_SCALE = 0.65                     # spec line 1113
BASE_SIDE_PRESSURE_CLAMP = (-50, 60)

HARSHNESS_NORMALIZATION_CEILING = 1.5               # spec line 1115
HARSHNESS_PENALTY_MAX = 45

# Settlement-tier legitimacy (spec line 1114, 1188-1196).
TIER_LEGITIMACY_BASE: Dict[str, int] = {
    "total_victory": 15,
    "harsh_peace": 10,
    "dictated_terms": 5,
    "favorable_terms": 0,
    "white_peace": -10,
}
TIER_HARSHNESS_CEILING: Dict[str, float] = {
    "white_peace": 0.10,
    "favorable_terms": 0.25,
    "dictated_terms": 0.45,
    "harsh_peace": 0.70,
    "total_victory": 1.00,
}
TIER_LEGITIMACY_MISMATCH = -10
TIER_LEGITIMACY_CLAMP = (-20, 15)

# Leader own losses (spec line 1117 + line 1186 mapped-holdings amendment).
LEADER_LOSS_PER_REGION = -5
LEADER_LOSS_CAPITAL = -15
LEADER_KEEPS_ALL_BONUS = 5
LEADER_LOST_MAPPED_HOLDING_PER = -5
LEADER_LOST_MAPPED_HOLDING_CAP = -10
LEADER_OWN_LOSSES_CLAMP = (-25, 5)

# Burdened non-leader penalty (spec lines 1116, 1127-1141, 1223-1234).
BURDEN_PENALTY_NEGATIVE_DIRECT = -30
BURDEN_PENALTY_LOW_DIRECT = -15
BURDEN_PENALTY_MAJOR_EXTRA = -10
BURDEN_PENALTY_AGGREGATE_FLOOR = -60
BURDEN_DIRECT_LOW_THRESHOLD = 20

# Projected hegemony (spec line 1119, 1200-1217).
HEGEMONY_BAND_60_MOD = -20
HEGEMONY_BAND_50_MOD = -10
HEGEMONY_BAND_33_MOD = -5
HEGEMONY_DE_ESCALATION_MOD = 10
HEGEMONY_MOD_CLAMP = (-20, 10)

# War-objective alignment (spec line 1118, 1174-1183).
ALIGN_SATISFY = 15
ALIGN_PARTIAL = 5
ALIGN_UNRELATED_HARSH = -15
ALIGN_CONTRADICT = -20
ALIGN_CLAMP = (-20, 15)
WPS_OBJECTIVE_PRIORITY = (
    "subjugation",
    "forced_alliance",
    "conquest",
    "liberation",
    "defense",
)

# War-exhaustion (spec line 1120 — intentional floor division).
WAR_EXHAUSTION_DIVISOR = 3
WAR_EXHAUSTION_CLAMP = (0, 20)
WAR_EXHAUSTION_UNRELATED_DIVISOR = 10  # only used if relevance cap adopted

# Abandoned-by-ally (spec line 1121, 786-793).
ABANDONED_PER_DEFECTOR = 5
ABANDONED_LOOKBACK_TURNS = 3
ABANDONED_CAP = 15

# Final aggregate clamp (spec line 1184).
ACCEPTANCE_FINAL_CLAMP = (-100, 100)

# Acceptance bands (spec lines 1145-1147).
ACCEPTANCE_THRESHOLD = 50
NEAR_ACCEPTANCE_FLOOR = 35

# Forced-alliance threat preview (spec line 1273 — `+15` per clause).
FORCED_ALLIANCE_THREAT_PER_CLAUSE = 15
COALITION_THRESHOLD_BREWING = 60   # `COALITION_SPEC` brewing
COALITION_THRESHOLD_INSTANT = 80   # instant-declaration
COALITION_THRESHOLD_OVERRIDE = 90  # cooldown-override

# Term type sets used across components.
_TERRITORY_TERM_TYPES = ("territory", "territory_cede", "territory_return")
_BURDEN_TERM_TYPES = (
    "territory",
    "territory_cede",
    "forced_alliance",
    "liberation",
    "vassalage",
    "subjugation",
)


# --- Term-iteration helpers --------------------------------------------------


def _iter_terms(settlement_terms: Optional[Iterable[Mapping[str, Any]]]) -> List[Dict[str, Any]]:
    """Coerce input to a stable list of dict terms; unknown shapes ignored."""
    if not settlement_terms:
        return []
    out: List[Dict[str, Any]] = []
    for t in settlement_terms:
        if isinstance(t, Mapping):
            out.append(dict(t))
    return out


def _term_from_nation(term: Mapping[str, Any]) -> Optional[str]:
    return term.get("from_nation") or term.get("from")


def _term_to_nation(term: Mapping[str, Any]) -> Optional[str]:
    return term.get("to_nation") or term.get("to")


def _term_regions(term: Mapping[str, Any]) -> List[str]:
    regions = term.get("regions")
    if isinstance(regions, (list, tuple)) and regions:
        return [str(r) for r in regions]
    region = str(term.get("region") or "")
    if region:
        return [region]
    return []


def _has_non_trivial_terms(terms: Iterable[Mapping[str, Any]]) -> bool:
    """Spec line 1114: white_peace + any non-trivial term exceeds ceiling."""
    for t in terms:
        ttype = t.get("type", "")
        if ttype in _TERRITORY_TERM_TYPES and _term_regions(t):
            return True
        if ttype in ("forced_alliance", "liberation", "vassalage", "subjugation"):
            return True
        # Any concrete numeric demand counts as non-trivial.
        if t.get("amount") or t.get("value"):
            return True
    return False


def _clamp(value: int, bounds: Tuple[int, int]) -> int:
    lo, hi = bounds
    return max(lo, min(hi, value))


# --- Component helpers -------------------------------------------------------


def calculate_base_side_pressure(side_pressure_score: int) -> Dict[str, Any]:
    """Spec §6.acceptance line 1113: `round(score * 0.65)` clamped `[-50, 60]`.

    Half-away-from-zero rounding (reuses C1a `_round_half_away_from_zero`).
    Returns a debug dict so the acceptance pipeline can name the inputs.
    """
    raw_int = _round_half_away_from_zero(int(side_pressure_score) * BASE_SIDE_PRESSURE_SCALE)
    score = _clamp(raw_int, BASE_SIDE_PRESSURE_CLAMP)
    return {
        "score": score,
        "raw_score": raw_int,
        "side_pressure_score": int(side_pressure_score),
        "scale": BASE_SIDE_PRESSURE_SCALE,
    }


def calculate_term_harshness_penalty(raw_total_harshness: float) -> Dict[str, Any]:
    """Spec §6.acceptance line 1115:
    `-min(45, round((min(raw_total_harshness, 1.5) / 1.5) * 45))`.

    Half-away-from-zero rounding at the component boundary, then negate,
    then floor at `-45`. Returns a debug dict including the
    1.5-normalized intermediate so settlement reviews can show it.
    """
    raw = max(0.0, float(raw_total_harshness or 0.0))
    capped = min(HARSHNESS_NORMALIZATION_CEILING, raw)
    normalized = capped / HARSHNESS_NORMALIZATION_CEILING
    magnitude = _round_half_away_from_zero(normalized * HARSHNESS_PENALTY_MAX)
    penalty = -min(HARSHNESS_PENALTY_MAX, magnitude)
    return {
        "score": int(penalty),
        "raw_total_harshness": raw,
        "capped_at_ceiling": capped,
        "normalized": normalized,
        "magnitude": int(magnitude),
        "ceiling": HARSHNESS_NORMALIZATION_CEILING,
    }


def calculate_settlement_tier_legitimacy(
    side_pressure_score: int,
    raw_total_harshness: float,
    settlement_terms: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Spec §6.acceptance line 1114, 1188-1196.

    Tier comes from the existing `diplomacy.get_settlement_tier()` helper,
    which keys off `abs(side_pressure_score)` and the
    `[(80, total_victory), (60, harsh_peace), (40, dictated_terms),
    (20, favorable_terms), (0, white_peace)]` ladder. The tier base is
    `+15 / +10 / +5 / 0 / -10`. If the package's raw harshness exceeds the
    tier ceiling (line 1188-1196), subtract another `-10`. White peace +
    any non-trivial term is automatically over-ceiling. Final clamp
    `[-20, 15]`.
    """
    from backend.game_logic.diplomacy import get_settlement_tier

    terms_list = _iter_terms(settlement_terms)
    tier = get_settlement_tier(int(side_pressure_score))
    base = TIER_LEGITIMACY_BASE.get(tier, 0)
    ceiling = TIER_HARSHNESS_CEILING.get(tier, 1.0)
    raw_h = max(0.0, float(raw_total_harshness or 0.0))

    mismatch = 0
    exceeded_ceiling = False
    if tier == "white_peace":
        if _has_non_trivial_terms(terms_list):
            mismatch = TIER_LEGITIMACY_MISMATCH
            exceeded_ceiling = True
    else:
        # Strict `>` so harsh_peace at exactly 0.70 is within ceiling.
        if raw_h > ceiling:
            mismatch = TIER_LEGITIMACY_MISMATCH
            exceeded_ceiling = True

    raw_score = base + mismatch
    score = _clamp(raw_score, TIER_LEGITIMACY_CLAMP)
    return {
        "score": int(score),
        "raw_score": int(raw_score),
        "tier": tier,
        "tier_base": int(base),
        "ceiling": ceiling,
        "exceeded_ceiling": exceeded_ceiling,
        "mismatch_penalty": int(mismatch),
        "raw_total_harshness": raw_h,
    }


def _accepting_leader_ceded_regions(
    accepting_leader: str,
    settlement_terms: Iterable[Mapping[str, Any]],
) -> List[str]:
    """Distinct regions ceded by the accepting leader via territory terms."""
    seen: Dict[str, None] = {}
    for term in settlement_terms:
        if term.get("type") not in _TERRITORY_TERM_TYPES:
            continue
        if _term_from_nation(term) != accepting_leader:
            continue
        for region in _term_regions(term):
            if region not in seen:
                seen[region] = None
    return list(seen.keys())


def _accepting_leader_forced_aligned(
    accepting_leader: str,
    settlement_terms: Iterable[Mapping[str, Any]],
) -> bool:
    """True if any forced_alliance term forces the accepting leader into
    alliance with another nation (capital-equivalent sovereignty loss per
    spec line 1117)."""
    for term in settlement_terms:
        if term.get("type") != "forced_alliance":
            continue
        if _term_from_nation(term) == accepting_leader and _term_to_nation(term) and _term_to_nation(term) != accepting_leader:
            return True
    return False


def calculate_leader_own_losses(
    world: Any,
    *,
    accepting_leader: str,
    settlement_terms: Iterable[Mapping[str, Any]],
    accepting_leader_regions_at_evaluation: Optional[Iterable[str]] = None,
    accepting_leader_mapped_holdings_at_entry: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """Spec §6.acceptance line 1117 + line 1186 mapped-holdings amendment.

    Sums sub-components BEFORE clamping to `[-25, 5]`. Lost-mapped-holdings
    is internally capped at `-10` (spec line 1186) and then summed into
    the raw total — never clamp individual sub-components except for that
    internal cap.

    Sub-components:
    - `regions_ceded`: `LEADER_LOSS_PER_REGION (-5)` per accepting-leader-
      controlled region ceded by a `territory*` term where `from_nation`
      is the accepting leader.
    - `capital_loss`: `LEADER_LOSS_CAPITAL (-15)` if the leader's
      `get_settlement_home_capital()` is in the ceded set OR a
      `forced_alliance` term forces the leader into alliance with a
      non-leader (capital-equivalent sovereignty loss). Returns 0 when
      `get_settlement_home_capital()` returns None (spec line 1117 —
      "skip the capital-loss subcomponent rather than crashing or
      inferring separate nation status").
    - `kept_all_bonus`: `LEADER_KEEPS_ALL_BONUS (+5)` only if leader has
      at least one controlled region at evaluation AND no terms cede /
      forced-align them. Zero-region accepting leader = 0 (spec line 1186).
    - `lost_mapped_holdings`: For each holding the leader had at war
      entry that is permanently ceded / forced-aligned / recognized lost
      by the package, add `LEADER_LOST_MAPPED_HOLDING_PER (-5)`, with the
      sub-total floored at `LEADER_LOST_MAPPED_HOLDING_CAP (-10)`.

    Returns the canonical debug dict; `score` is the post-clamp final
    value, `raw_score` is the pre-clamp sum so settlement reviews can
    show why the clamp triggered.
    """
    terms_list = _iter_terms(settlement_terms)
    ceded_regions = _accepting_leader_ceded_regions(accepting_leader, terms_list)
    forced_aligned = _accepting_leader_forced_aligned(accepting_leader, terms_list)

    home_capital_getter = getattr(world, "get_settlement_home_capital", None)
    home_capital = (
        home_capital_getter(accepting_leader) if callable(home_capital_getter) else None
    )

    capital_lost = False
    if home_capital is not None:
        if home_capital in ceded_regions or forced_aligned:
            capital_lost = True

    if accepting_leader_regions_at_evaluation is None:
        try:
            current_regions = list(world.get_nation_regions(accepting_leader))
        except Exception:
            current_regions = []
    else:
        current_regions = list(accepting_leader_regions_at_evaluation)

    has_regions_at_eval = bool(current_regions)
    cedes_any_owned_region = any(r in current_regions for r in ceded_regions)
    keeps_all = (
        has_regions_at_eval and not cedes_any_owned_region and not forced_aligned
    )

    if accepting_leader_mapped_holdings_at_entry is None:
        mapped_holdings = []
    else:
        mapped_holdings = list(accepting_leader_mapped_holdings_at_entry)

    lost_mapped_holdings_raw = 0
    if mapped_holdings:
        ceded_set = set(ceded_regions)
        for holding in mapped_holdings:
            if holding in ceded_set:
                lost_mapped_holdings_raw += 1
            elif forced_aligned:
                # Forced alliance over the leader implicitly compromises
                # the holding. Spec line 1186 lists "forced-aligns" as a
                # qualifying loss.
                lost_mapped_holdings_raw += 1
    lost_mapped_holdings_subtotal = max(
        LEADER_LOST_MAPPED_HOLDING_CAP,
        LEADER_LOST_MAPPED_HOLDING_PER * lost_mapped_holdings_raw,
    )

    components = {
        "regions_ceded": len(ceded_regions) * LEADER_LOSS_PER_REGION,
        "capital_loss": LEADER_LOSS_CAPITAL if capital_lost else 0,
        "kept_all_bonus": LEADER_KEEPS_ALL_BONUS if keeps_all else 0,
        "lost_mapped_holdings": lost_mapped_holdings_subtotal,
    }
    raw_score = sum(components.values())
    score = _clamp(raw_score, LEADER_OWN_LOSSES_CLAMP)
    return {
        "score": int(score),
        "raw_score": int(raw_score),
        "regions_ceded_count": len(ceded_regions),
        "ceded_regions": list(ceded_regions),
        "capital_lost": capital_lost,
        "home_capital": home_capital,
        "kept_all_with_holdings": keeps_all,
        "has_regions_at_evaluation": has_regions_at_eval,
        "lost_mapped_holdings_count": lost_mapped_holdings_raw,
        "lost_mapped_holdings_subtotal": int(lost_mapped_holdings_subtotal),
        "forced_aligned_against_leader": forced_aligned,
        "components": components,
        "clamp": LEADER_OWN_LOSSES_CLAMP,
    }


def _enemy_pays_burden_term(
    enemy: str,
    terms: Iterable[Mapping[str, Any]],
) -> List[str]:
    """Return the burden-term types a non-leader enemy actually pays."""
    paid: List[str] = []
    for term in terms:
        ttype = term.get("type", "")
        if ttype not in _BURDEN_TERM_TYPES:
            continue
        # The enemy is paying when they are the `from_nation` for territory /
        # vassalage / subjugation / forced_alliance, or the `from_nation`
        # for liberation (a vassal liberation pulls from the overlord —
        # treat as "paid by overlord").
        if _term_from_nation(term) == enemy:
            paid.append(ttype)
    return paid


def _capital_occupied_by_proposer_side(
    world: Any,
    enemy: str,
    proposer_side_participants: Iterable[str],
) -> bool:
    """Best-effort check used by the burden major-power exception."""
    home_capital_getter = getattr(world, "get_settlement_home_capital", None)
    capital = home_capital_getter(enemy) if callable(home_capital_getter) else None
    if not capital:
        return False
    regions = getattr(world, "regions", None)
    if not regions or capital not in regions:
        return False
    region_obj = regions[capital]
    occupier = getattr(region_obj, "controller", None)
    if occupier is None:
        return False
    return occupier in set(proposer_side_participants)


def _term_matches_objective(
    enemy: str,
    objective_record: Mapping[str, Any],
    settlement_terms: Iterable[Mapping[str, Any]],
) -> bool:
    """Heuristic: the package contains a term that aligns with the
    proposer-side objective against this enemy."""
    if not objective_record:
        return False
    target_regions = set(objective_record.get("target_regions") or [])
    obj_type = objective_record.get("type", "")
    for term in settlement_terms:
        ttype = term.get("type", "")
        if ttype in _TERRITORY_TERM_TYPES:
            if _term_from_nation(term) == enemy and target_regions:
                if any(r in target_regions for r in _term_regions(term)):
                    return True
            elif obj_type == "conquest":
                if _term_from_nation(term) == enemy:
                    return True
        elif ttype == "forced_alliance" and obj_type == "forced_alliance":
            if _term_from_nation(term) == enemy:
                return True
        elif ttype in ("vassalage", "subjugation") and obj_type == "subjugation":
            if _term_from_nation(term) == enemy or _term_to_nation(term) == enemy:
                return True
        elif ttype == "liberation" and obj_type == "liberation":
            return True
    return False


def calculate_burdened_participant_penalty(
    world: Any,
    *,
    accepting_leader: str,
    proposer_side_participants: Iterable[str],
    covered_enemy_participants: Iterable[str],
    settlement_terms: Iterable[Mapping[str, Any]],
    direct_scores: Mapping[str, Mapping[str, int]],
    war_objectives_by_enemy: Optional[Mapping[str, Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    """Spec §6.acceptance lines 1116, 1127-1141, 1223-1234.

    Burdened non-leader = covered enemy that is NOT the accepting leader
    AND pays a territory / vassalage / forced_alliance / liberation cost.
    The accepting leader's own losses are owned by `leader_own_losses`
    (spec line 1125 — explicit "do not double-charge the leader").

    Per-burdened computation:
        score = max(direct_scores[burdened])  # via select_direct_score()
        if score < 0: penalty -= 30
        elif score < 20: penalty -= 15
        if power_tier(burdened) == "major":
            unless capital_occupied_by_proposer OR term matches war objective:
                penalty -= 10  # stacks even when direct_score >= 20

    Aggregate cap:
        cap = -30 * min(burdened_count, 2)        # -30 for 1, -60 for 2+
        final = max(penalty, cap, -60)             # never below -60
    """
    terms_list = _iter_terms(settlement_terms)
    proposer_set = set(proposer_side_participants)
    covered = [str(e) for e in covered_enemy_participants if e != accepting_leader]

    objectives = dict(war_objectives_by_enemy or {})

    per_burden: List[Dict[str, Any]] = []
    raw_penalty = 0
    burdened_count = 0

    for enemy in covered:
        burden_types = _enemy_pays_burden_term(enemy, terms_list)
        if not burden_types:
            continue
        burdened_count += 1
        per_member = direct_scores.get(enemy) or {}
        selection = select_direct_score(per_member)
        if selection is None:
            # No active proposer-side war pair for this enemy — they
            # cannot be coherently scored as burdened. Spec already
            # surfaces this as a `no_direct_war_score_for_covered_enemy`
            # hard stop; treat as direct_score=-inf and apply the worst
            # branch so the burden penalty is conservative.
            direct_score = -1
            source = None
        else:
            direct_score, source = selection
        reasons: List[str] = []
        sub_penalty = 0
        if direct_score < 0:
            sub_penalty += BURDEN_PENALTY_NEGATIVE_DIRECT
            reasons.append("direct_score_negative")
        elif direct_score < BURDEN_DIRECT_LOW_THRESHOLD:
            sub_penalty += BURDEN_PENALTY_LOW_DIRECT
            reasons.append("direct_score_low")
        # Major-power burden exception (spec line 1229).
        tier_getter = getattr(world, "get_power_tier", None)
        tier = tier_getter(enemy) if callable(tier_getter) else None
        if tier == "major":
            capital_occupied = _capital_occupied_by_proposer_side(
                world, enemy, proposer_set,
            )
            objective = objectives.get(enemy)
            term_matches = bool(objective) and _term_matches_objective(
                enemy, objective, terms_list,
            )
            if not capital_occupied and not term_matches:
                sub_penalty += BURDEN_PENALTY_MAJOR_EXTRA
                reasons.append("major_uncovered")
        per_burden.append({
            "enemy": enemy,
            "direct_score": int(direct_score),
            "direct_score_source": source,
            "tier": tier,
            "burden_types": list(burden_types),
            "penalty": int(sub_penalty),
            "reasons": reasons,
        })
        raw_penalty += sub_penalty

    aggregate_cap = -30 * min(burdened_count, 2)
    floor = BURDEN_PENALTY_AGGREGATE_FLOOR
    score = max(raw_penalty, aggregate_cap, floor)
    return {
        "score": int(score),
        "raw_penalty": int(raw_penalty),
        "burdened_count": burdened_count,
        "per_burden": per_burden,
        "aggregate_cap": int(aggregate_cap),
        "applied_floor": int(floor),
    }


def _select_relevant_objective(
    world: Any,
    *,
    proposer_side_participants: Iterable[str],
    proposer_side_leader: Optional[str],
    accepting_leader: str,
    covered_enemy_participants: Iterable[str],
    settlement_terms: Iterable[Mapping[str, Any]],
) -> Optional[Tuple[str, str, Dict[str, Any]]]:
    """Spec §6.acceptance line 1174 selection chain.

    Returns `(declaring_nation, target_nation, objective_record)` or None.
    """
    war_objectives = getattr(world, "war_objectives", None) or {}
    proposers = list(proposer_side_participants)
    if not proposers:
        return None

    # Identify the harshest-term target = the covered enemy paying the most
    # raw harshness in the package.
    enemy_costs: Dict[str, float] = {e: 0.0 for e in covered_enemy_participants}
    for term in settlement_terms:
        from_n = _term_from_nation(term)
        if from_n in enemy_costs:
            ttype = term.get("type", "")
            if ttype in _TERRITORY_TERM_TYPES:
                enemy_costs[from_n] += 0.3 * len(_term_regions(term))
            elif ttype == "forced_alliance":
                enemy_costs[from_n] += 0.4
            elif ttype == "liberation":
                enemy_costs[from_n] += 0.3
            elif ttype == "vassalage" or ttype == "subjugation":
                enemy_costs[from_n] += 0.5
    harshest_target: Optional[str]
    if any(v > 0 for v in enemy_costs.values()):
        harshest_target = max(enemy_costs.items(), key=lambda kv: (kv[1], kv[0]))[0]
    else:
        harshest_target = None

    leader = proposer_side_leader or (proposers[0] if proposers else None)

    def _objective_at(declarer: str, target: str) -> Optional[Dict[str, Any]]:
        try:
            diplo_key = world._make_diplo_key(declarer, target)
        except Exception:
            diplo_key = "|".join(sorted([declarer, target]))
        record = war_objectives.get(diplo_key, {}).get(declarer)
        if not record:
            return None
        if record.get("concluded_turn") is not None:
            return None
        return record

    # 1. Side leader's objective against accepting leader / harshest target.
    if leader:
        for primary in (accepting_leader, harshest_target):
            if not primary or primary == leader:
                continue
            obj = _objective_at(leader, primary)
            if obj:
                return (leader, primary, obj)
    # 2. Other covered enemies in term order.
    seen_targets = set()
    ordered_targets: List[str] = []
    for term in settlement_terms:
        from_n = _term_from_nation(term)
        if from_n in covered_enemy_participants and from_n not in seen_targets:
            seen_targets.add(from_n)
            ordered_targets.append(from_n)
    for target in ordered_targets:
        if leader and target != leader:
            obj = _objective_at(leader, target)
            if obj:
                return (leader, target, obj)
    # 3. WPS priority order over all proposer participants vs covered.
    candidates: List[Tuple[str, str, Dict[str, Any]]] = []
    for declarer in proposers:
        for target in covered_enemy_participants:
            if declarer == target:
                continue
            obj = _objective_at(declarer, target)
            if obj:
                candidates.append((declarer, target, obj))
    if not candidates:
        return None

    def _priority(record: Dict[str, Any]) -> int:
        try:
            return WPS_OBJECTIVE_PRIORITY.index(record.get("type", ""))
        except ValueError:
            return len(WPS_OBJECTIVE_PRIORITY)

    candidates.sort(
        key=lambda x: (_priority(x[2]), int(x[2].get("created_turn", 0)), x[0], x[1]),
    )
    return candidates[0]


def _classify_objective_alignment(
    objective_type: str,
    objective_record: Mapping[str, Any],
    target: str,
    settlement_terms: Iterable[Mapping[str, Any]],
) -> Tuple[int, str]:
    """Spec §6.acceptance line 1176-1183 table evaluation.

    Returns `(score, label)` where label ∈ {'satisfies', 'partial',
    'unrelated_harsh', 'contradicts', 'no_objective'}.
    """
    target_regions = set(objective_record.get("target_regions") or [])
    has_objective_concession = False
    has_unrelated_harsh = False
    contradicts = False

    for term in settlement_terms:
        ttype = term.get("type", "")
        from_n = _term_from_nation(term)
        to_n = _term_to_nation(term)
        regions = set(_term_regions(term))

        if objective_type == "conquest":
            if ttype in _TERRITORY_TERM_TYPES and from_n == target:
                if not target_regions or regions & target_regions:
                    has_objective_concession = True
                else:
                    has_objective_concession = True
            elif ttype in _TERRITORY_TERM_TYPES and to_n == target:
                # Returns the objective region or strengthens the target.
                if regions & target_regions or not target_regions:
                    contradicts = True
            elif ttype == "forced_alliance" and from_n == target:
                has_objective_concession = True
            elif ttype in _BURDEN_TERM_TYPES and from_n != target:
                has_unrelated_harsh = True
        elif objective_type == "subjugation":
            if ttype in ("vassalage", "subjugation") and to_n == target:
                has_objective_concession = True
            elif ttype == "forced_alliance" and from_n == target:
                has_objective_concession = True
            elif ttype == "liberation" and to_n == target:
                contradicts = True
            elif ttype in _BURDEN_TERM_TYPES and from_n != target:
                has_unrelated_harsh = True
        elif objective_type == "forced_alliance":
            if ttype == "forced_alliance" and from_n == target:
                has_objective_concession = True
            elif ttype == "liberation" and to_n == target:
                contradicts = True
            elif ttype in _BURDEN_TERM_TYPES and from_n != target:
                has_unrelated_harsh = True
        elif objective_type == "defense":
            # Defense partial vs satisfies is decided after the loop.
            # Track only contradictions / unrelated-harsh signals here.
            if ttype in _TERRITORY_TERM_TYPES and from_n == objective_record.get("declaring_nation"):
                if regions & target_regions:
                    contradicts = True
            elif ttype in _BURDEN_TERM_TYPES and from_n != target:
                # Defender ceding non-objective regions or harsh terms on
                # unrelated targets only counts as unrelated_harsh when
                # not also restoring objective regions.
                has_unrelated_harsh = True
        elif objective_type == "liberation":
            if ttype == "liberation":
                has_objective_concession = True
            elif ttype in ("vassalage", "subjugation") and to_n == target:
                contradicts = True
            elif ttype in _BURDEN_TERM_TYPES and from_n != target:
                has_unrelated_harsh = True

    # Defense-specific partial vs satisfies (spec line 1181):
    # +15 ALL named occupied core regions restored;
    # +5 SOME but not all restored.
    if objective_type == "defense" and target_regions and not contradicts:
        restored: set = set()
        for term in settlement_terms:
            ttype = term.get("type", "")
            if ttype not in _TERRITORY_TERM_TYPES:
                continue
            if _term_to_nation(term) != objective_record.get("declaring_nation"):
                continue
            restored.update(set(_term_regions(term)) & target_regions)
        if restored == target_regions:
            return ALIGN_SATISFY, "satisfies"
        if restored:
            return ALIGN_PARTIAL, "partial"
        if has_unrelated_harsh:
            return ALIGN_UNRELATED_HARSH, "unrelated_harsh"
        return ALIGN_PARTIAL, "partial"

    if contradicts:
        return ALIGN_CONTRADICT, "contradicts"
    if has_objective_concession:
        # Treat conquest/subjugation/forced_alliance/liberation as
        # "satisfied" when ANY matching concession exists; partial credit
        # is reserved for defense (above) per spec table.
        return ALIGN_SATISFY, "satisfies"
    if has_unrelated_harsh:
        return ALIGN_UNRELATED_HARSH, "unrelated_harsh"
    return ALIGN_PARTIAL, "partial"


def calculate_war_objective_alignment(
    world: Any,
    *,
    war_id: Optional[str],
    proposer_side_leader: Optional[str],
    proposer_side_participants: Iterable[str],
    accepting_leader: str,
    covered_enemy_participants: Iterable[str],
    settlement_terms: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Spec §6.acceptance lines 1118, 1174-1183 — 5-objective table.

    Selects the relevant proposer-side WPS objective per spec line 1174
    and evaluates the package against the per-type table.

    No live objective record => `score=0` (spec line 1174 — "score this
    component as `0` rather than guessing from terms").
    """
    terms_list = _iter_terms(settlement_terms)
    selection = _select_relevant_objective(
        world,
        proposer_side_participants=proposer_side_participants,
        proposer_side_leader=proposer_side_leader,
        accepting_leader=accepting_leader,
        covered_enemy_participants=covered_enemy_participants,
        settlement_terms=terms_list,
    )
    if selection is None:
        return {
            "score": 0,
            "selected_objective": None,
            "alignment_label": "no_objective",
            "war_id": war_id,
        }
    declarer, target, record = selection
    score, label = _classify_objective_alignment(
        record.get("type", ""), record, target, terms_list,
    )
    score = _clamp(int(score), ALIGN_CLAMP)
    try:
        diplo_key = world._make_diplo_key(declarer, target)
    except Exception:
        diplo_key = "|".join(sorted([declarer, target]))
    return {
        "score": int(score),
        "selected_objective": {
            "diplo_key": diplo_key,
            "declaring_nation": declarer,
            "target_nation": target,
            "objective_type": record.get("type", ""),
            "target_regions": list(record.get("target_regions") or []),
            "created_turn": int(record.get("created_turn", 0)),
        },
        "alignment_label": label,
        "war_id": war_id,
    }


def calculate_war_exhaustion_component(
    world: Any,
    *,
    accepting_leader: str,
    war_id: Optional[str] = None,
    covered_enemy_participants: Optional[Iterable[str]] = None,
    apply_relevance_cap: bool = False,
) -> Dict[str, Any]:
    """Spec §6.acceptance line 1120: `min(20, war_exhaustion // 3)`.

    INTENTIONAL floor division per spec — every other component uses
    `round()` at boundary; this one does not. Always exposes raw +
    relevance-split inputs in debug output (plan line 222) so the
    war-exhaustion exploit fixture can prove whether the relevance cap
    needs to be adopted.

    `apply_relevance_cap=False` (default for C1b ship): use the existing
    per-nation `world.war_exhaustion[accepting_leader]` directly (spec
    line 1120 + plan line 218 — "may adopt the spec's relevance cap only
    if the multi-war exploit fixture proves unrelated cheap wars make
    settlements absurdly cheap").

    `apply_relevance_cap=True` (only set if exploit fixture forces it):
        score = min(20, relevant // 3 + unrelated // 10)
    Per spec line 1123: document the change in tests, implementation
    notes, AND `SYSTEMS_REFERENCE.md`.
    """
    raw_we = int(getattr(world, "war_exhaustion", {}).get(accepting_leader, 0))
    raw_we = max(0, raw_we)

    relevant_we = None
    unrelated_we = None
    if covered_enemy_participants is not None and war_id is not None:
        # Heuristic split: the spec defers the precise definition until
        # the exploit fixture proves a cap is needed. For now, treat
        # `relevant` as the full per-nation exhaustion (no split) when
        # the leader has any active war against a covered enemy; that
        # mirrors v0.1's per-nation cumulative model.
        try:
            covered = set(covered_enemy_participants)
            has_active = any(
                world.is_at_war(accepting_leader, e) for e in covered
            )
        except Exception:
            has_active = False
        if has_active:
            relevant_we = raw_we
            unrelated_we = 0
        else:
            relevant_we = 0
            unrelated_we = raw_we

    if apply_relevance_cap and relevant_we is not None and unrelated_we is not None:
        score = min(
            WAR_EXHAUSTION_CLAMP[1],
            relevant_we // WAR_EXHAUSTION_DIVISOR
            + unrelated_we // WAR_EXHAUSTION_UNRELATED_DIVISOR,
        )
    else:
        score = min(WAR_EXHAUSTION_CLAMP[1], raw_we // WAR_EXHAUSTION_DIVISOR)
    score = _clamp(int(score), WAR_EXHAUSTION_CLAMP)
    return {
        "score": int(score),
        "raw_per_nation_exhaustion": int(raw_we),
        "relevant_exhaustion": relevant_we,
        "unrelated_exhaustion": unrelated_we,
        "applied_relevance_cap": bool(apply_relevance_cap),
    }


def calculate_abandoned_by_ally_mod(
    war_instance: Mapping[str, Any],
    *,
    accepting_side: str,
    current_turn: int,
) -> Dict[str, Any]:
    """Spec §6.acceptance line 1121, definition lines 786-793.

    Counts records in `war_instance["separate_peaced"]` where:
    - `record["side"] == accepting_side` (same side as accepting leader),
    - `current_turn - record["exited_turn"] <= ABANDONED_LOOKBACK_TURNS`.
    """
    if accepting_side not in _VALID_SIDES:
        raise ValueError(
            f"accepting_side must be 'attackers' or 'defenders', got {accepting_side!r}"
        )
    defectors: List[str] = []
    for record in war_instance.get("separate_peaced") or []:
        if not isinstance(record, Mapping):
            continue
        if record.get("side") != accepting_side:
            continue
        try:
            exited = int(record.get("exited_turn") or 0)
        except (TypeError, ValueError):
            exited = 0
        if int(current_turn) - exited > ABANDONED_LOOKBACK_TURNS:
            continue
        nation = record.get("nation")
        if nation:
            defectors.append(str(nation))
    raw_score = ABANDONED_PER_DEFECTOR * len(defectors)
    score = min(ABANDONED_CAP, raw_score)
    return {
        "score": int(score),
        "raw_score": int(raw_score),
        "recent_defectors": sorted(set(defectors)),
        "applied_cap": raw_score > ABANDONED_CAP,
        "lookback_turns": ABANDONED_LOOKBACK_TURNS,
    }


# --- Projected balance after settlement -------------------------------------


def _share_band(share: float) -> int:
    """Mirror of `coalition.py::_hegemony_signal_band`. Pure: 0/1/2/3 by
    33% / 50% / 60% thresholds. Duplicated here so the projection helper
    has no live coalition.py dependency for read-only band classification.
    """
    if share < 0.33:
        return 0
    if share < 0.50:
        return 1
    if share < 0.60:
        return 2
    return 3


def _band_to_threshold_label(band: int) -> Optional[int]:
    """Return the 33/50/60 label for a band index, or None for the safe band."""
    if band == 1:
        return 33
    if band == 2:
        return 50
    if band == 3:
        return 60
    return None


def _projected_max_bloc_share(
    world: Any,
    nation_regions_proj: Dict[str, set],
    alignments_proj: Dict[Tuple[str, str], str],
    vassal_of_proj: Dict[str, str],
    actives: List[str],
) -> Tuple[Optional[str], float]:
    """Re-run the `_identify_max_bloc_share` algorithm against projected
    state. Pure — never reads live `world.diplomatic_states` or
    `world.vassals`; always reads the in-memory snapshot dicts.
    """
    if not actives:
        return (None, 0.0)
    from backend.nation_config import _POWER_TIER_DEFAULT

    tier_weights = POWER_TIER_WEIGHTS

    def _power_score_proj(nation: str) -> int:
        regions = nation_regions_proj.get(nation, set())
        tier_getter = getattr(world, "get_power_tier", None)
        tier = tier_getter(nation) if callable(tier_getter) else None
        weight = tier_weights.get(
            tier or _POWER_TIER_DEFAULT, tier_weights[_POWER_TIER_DEFAULT]
        )
        return int(len(regions) * weight)

    def _top_overlord_proj(nation: str) -> str:
        seen = {nation}
        cur = nation
        while cur in vassal_of_proj:
            lord = vassal_of_proj[cur]
            if not lord or lord in seen:
                return cur
            seen.add(lord)
            cur = lord
        return cur

    def _bloc_members_proj(leader: str) -> List[str]:
        members = {leader}
        for vassal in vassal_of_proj:
            if _top_overlord_proj(vassal) == leader:
                members.add(vassal)
        for other in actives:
            if other == leader:
                continue
            pair = tuple(sorted([leader, other]))
            if alignments_proj.get(pair) in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
                members.add(other)
        return sorted(members)

    european_power = sum(_power_score_proj(n) for n in actives)
    if european_power == 0:
        return (None, 0.0)
    tier_getter = getattr(world, "get_power_tier", None)
    majors = [
        n for n in actives
        if (tier_getter(n) if callable(tier_getter) else None) == "major"
    ]
    if not majors:
        majors = list(actives)
    bloc_shares = {}
    for leader in majors:
        bloc_pwr = sum(_power_score_proj(m) for m in _bloc_members_proj(leader))
        bloc_shares[leader] = bloc_pwr / european_power if european_power else 0.0
    if not bloc_shares:
        return (None, 0.0)
    ordered = sorted(
        bloc_shares.items(),
        key=lambda kv: (
            -kv[1],
            -sum(_power_score_proj(m) for m in _bloc_members_proj(kv[0])),
            kv[0],
        ),
    )
    return (ordered[0][0], float(ordered[0][1]))


def project_balance_after_settlement(
    world: Any,
    *,
    war_id: Optional[str],
    settlement_terms: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Spec §6.acceptance lines 1200-1217 — pure projection helper.

    Reads cached `get_active_nations()`, `get_nation_regions()`,
    `get_diplomatic_state()`, `world.vassals`, `get_power_tier()`. Builds
    in-memory mutable copies for affected nations only and applies term
    deltas in this deterministic order:

    1. `liberation` — release vassal back to independence
    2. `forced_alliance` — set ALLIANCE pair
    3. `territory*` — move regions between nations
    4. `vassalage` / `subjugation` — set vassal_of

    Returns the canonical settlement-preview shape (spec line 1203):

        {
            "pre_hegemon": str | None,
            "post_hegemon": str | None,
            "pre_share": float,
            "post_share": float,
            "crossed_band": None | 33 | 50 | 60,
            "deepened_band": None | 33 | 50 | 60,
            "hegemon_swap": bool,
            "modifier": int,    # clamped [-20, 10]
        }

    NEVER mutates `world.regions`, `world.diplomatic_states`,
    `world.vassals`, or any live cache. Add a no-mutation regression
    test (plan line 228).
    """
    actives = list(world.get_active_nations()) if hasattr(world, "get_active_nations") else []
    if not actives:
        return {
            "pre_hegemon": None,
            "post_hegemon": None,
            "pre_share": 0.0,
            "post_share": 0.0,
            "crossed_band": None,
            "deepened_band": None,
            "hegemon_swap": False,
            "modifier": 0,
        }

    # Snapshot region ownership.
    nation_regions: Dict[str, set] = {}
    for n in actives:
        try:
            nation_regions[n] = set(world.get_nation_regions(n))
        except Exception:
            nation_regions[n] = set()

    # Snapshot alliance / defensive_alliance pairs (read-only).
    alignments: Dict[Tuple[str, str], str] = {}
    for i, n in enumerate(actives):
        for m in actives[i + 1:]:
            try:
                state = world.get_diplomatic_state(n, m)
            except Exception:
                state = None
            if state in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
                alignments[tuple(sorted([n, m]))] = state

    # Snapshot direct vassal_of relationships.
    vassal_of: Dict[str, str] = {}
    for vassal_name, vassal_data in (getattr(world, "vassals", None) or {}).items():
        if not isinstance(vassal_data, Mapping):
            continue
        lord = vassal_data.get("lord")
        if lord:
            vassal_of[str(vassal_name)] = str(lord)

    # Pre-projection bloc state.
    pre_hegemon, pre_share = _projected_max_bloc_share(
        world, nation_regions, alignments, vassal_of, actives,
    )

    terms_list = _iter_terms(settlement_terms)

    # Step 1: liberation (release vassal).
    for term in terms_list:
        if term.get("type") != "liberation":
            continue
        target = _term_to_nation(term) or term.get("vassal") or term.get("nation")
        if target and target in vassal_of:
            del vassal_of[str(target)]

    # Step 2: forced_alliance.
    for term in terms_list:
        if term.get("type") != "forced_alliance":
            continue
        a, b = _term_from_nation(term), _term_to_nation(term)
        if a and b and a != b:
            alignments[tuple(sorted([str(a), str(b)]))] = "ALLIANCE"

    # Step 3: territory transfers.
    for term in terms_list:
        if term.get("type") not in _TERRITORY_TERM_TYPES:
            continue
        from_n = _term_from_nation(term)
        to_n = _term_to_nation(term)
        regions = _term_regions(term)
        if not regions or not to_n:
            continue
        for r in regions:
            if from_n and from_n in nation_regions:
                nation_regions[from_n].discard(r)
            nation_regions.setdefault(str(to_n), set()).add(r)

    # Step 4: vassalage / subjugation.
    for term in terms_list:
        if term.get("type") not in ("vassalage", "subjugation"):
            continue
        vassal = _term_to_nation(term) or term.get("vassal")
        lord = _term_from_nation(term) or term.get("lord")
        if vassal and lord and str(vassal) != str(lord):
            vassal_of[str(vassal)] = str(lord)

    post_hegemon, post_share = _projected_max_bloc_share(
        world, nation_regions, alignments, vassal_of, actives,
    )

    pre_band = _share_band(pre_share)
    post_band = _share_band(post_share)
    crossed_band: Optional[int] = None
    deepened_band: Optional[int] = None
    if post_band > pre_band:
        crossed_band = _band_to_threshold_label(post_band)
    elif post_band == pre_band and post_band > 0 and post_share > pre_share:
        deepened_band = _band_to_threshold_label(post_band)

    if crossed_band == 60 or deepened_band == 60:
        modifier = HEGEMONY_BAND_60_MOD
    elif crossed_band == 50 or deepened_band == 50:
        modifier = HEGEMONY_BAND_50_MOD
    elif crossed_band == 33 or deepened_band == 33:
        modifier = HEGEMONY_BAND_33_MOD
    elif post_band < pre_band and pre_band > 0:
        modifier = HEGEMONY_DE_ESCALATION_MOD
    else:
        modifier = 0
    modifier = _clamp(int(modifier), HEGEMONY_MOD_CLAMP)

    return {
        "pre_hegemon": pre_hegemon,
        "post_hegemon": post_hegemon,
        "pre_share": float(pre_share),
        "post_share": float(post_share),
        "crossed_band": crossed_band,
        "deepened_band": deepened_band,
        "hegemon_swap": pre_hegemon != post_hegemon,
        "modifier": int(modifier),
    }


# --- Forced-alliance threat preview -----------------------------------------


def compute_forced_alliance_threat_preview(
    world: Any,
    *,
    settlement_terms: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Spec §6.acceptance line 1273: project per-clause threat delta.

    Each `forced_alliance` clause adds `+15` threat. Settlement preview
    must aggregate the projected delta and name any crossed coalition
    thresholds (`60` brewing / `80` instant / `90` cooldown override per
    `COALITION_SPEC.md`) so the player sees the imperial cost before
    confirmation.
    """
    forced_clauses = sum(
        1 for t in _iter_terms(settlement_terms)
        if t.get("type") == "forced_alliance"
    )
    delta = forced_clauses * FORCED_ALLIANCE_THREAT_PER_CLAUSE

    # Read current threat for the proposer side from coalition state if
    # available; default 0 when no coalition system is active.
    current_threat = 0
    coalition = getattr(world, "coalition_state", None)
    if coalition:
        try:
            current_threat = int(coalition.get("threat_level", 0))
        except Exception:
            current_threat = 0
    elif hasattr(world, "threat_level"):
        try:
            current_threat = int(world.threat_level or 0)
        except Exception:
            current_threat = 0

    projected = current_threat + delta
    crossed: List[int] = []
    for thr in (
        COALITION_THRESHOLD_BREWING,
        COALITION_THRESHOLD_INSTANT,
        COALITION_THRESHOLD_OVERRIDE,
    ):
        if current_threat < thr <= projected:
            crossed.append(thr)
    return {
        "forced_alliance_clauses": int(forced_clauses),
        "projected_threat_delta": int(delta),
        "current_threat": int(current_threat),
        "projected_threat": int(projected),
        "crossed_thresholds": crossed,
    }


# --- Pipeline composer ------------------------------------------------------


def calculate_common_peace_acceptance(
    world: Any,
    *,
    war_id: str,
    war_instance: Mapping[str, Any],
    proposer_side: str,
    accepting_side: str,
    accepting_leader: str,
    covered_enemy_participants: Iterable[str],
    settlement_terms: Iterable[Mapping[str, Any]],
    proposer_side_leader: Optional[str] = None,
    side_pressure_result: Optional[Mapping[str, Any]] = None,
    direct_scores: Optional[Mapping[str, Mapping[str, int]]] = None,
    raw_total_harshness: Optional[float] = None,
    accepting_leader_regions_at_evaluation: Optional[Iterable[str]] = None,
    accepting_leader_mapped_holdings_at_entry: Optional[Iterable[str]] = None,
    apply_war_exhaustion_relevance_cap: bool = False,
    current_turn: Optional[int] = None,
) -> Dict[str, Any]:
    """Spec §6.acceptance lines 1095-1147 — full common-peace acceptance.

    Pipeline (deterministic order):

    1. Build / accept memoized `direct_scores` (C1a contract).
    2. Compute `side_pressure_result` if not supplied (C1a helper). Hard
       stop bubble-up returns early with `score=None`.
    3. `base_side_pressure` — clamped round.
    4. `settlement_tier_legitimacy` — tier from `get_settlement_tier()`.
    5. `term_harshness_penalty` — raw from `calculate_raw_treaty_harshness`.
    6. `leader_own_losses` — sub-components summed BEFORE clamp.
    7. `burdened_participant_penalty` — uses memoized direct_scores.
    8. `projected_hegemony_mod` — from `project_balance_after_settlement()`.
    9. `war_objective_alignment` — from WPS objective table.
    10. `war_exhaustion` — floor division (spec line 1120).
    11. `abandoned_by_ally_acceptance_mod`.
    12. Sum 9 components → `raw_total` → clamp `[-100, 100]` → `score`.
    13. Verdict: `accept` (>=50) / `near_acceptable` (35-49) / `reject`.
    14. Build `feedback`: top 1-2 components by absolute negative magnitude.
    15. Compute forced-alliance threat preview.

    Returns the canonical settlement-preview shape (see module docstring).

    Hard stops bubble up from C1a `compute_side_pressure_score`. Any
    hard stop returns `score=None`, `verdict="reject"`, and
    `hard_stops` list with no further computation.
    """
    from backend.game_logic.diplomatic_templates import calculate_raw_treaty_harshness

    proposer_side = str(proposer_side)
    accepting_side = str(accepting_side)
    if proposer_side not in _VALID_SIDES:
        raise ValueError(f"proposer_side must be 'attackers' or 'defenders', got {proposer_side!r}")
    if accepting_side not in _VALID_SIDES:
        raise ValueError(f"accepting_side must be 'attackers' or 'defenders', got {accepting_side!r}")

    covered = sorted({str(n) for n in covered_enemy_participants})
    proposer_participants = list(_proposer_side_members(war_instance, proposer_side))
    accepting_participants = list(_proposer_side_members(war_instance, accepting_side))

    # Step 1-2: memoize direct_scores + side pressure with hard-stop bubble.
    if side_pressure_result is None:
        side_pressure_result = compute_side_pressure_score(
            world,
            war_instance,
            proposer_side=proposer_side,
            covered_enemy_participants=covered,
            direct_scores=direct_scores,
        )
    direct_scores_map = side_pressure_result.get("direct_scores") or {}

    if side_pressure_result.get("hard_stops") or side_pressure_result.get("score") is None:
        return {
            "score": None,
            "verdict": "reject",
            "components": {},
            "component_debug": {},
            "side_pressure_score": side_pressure_result.get("score"),
            "side_pressure_result": dict(side_pressure_result),
            "direct_scores": direct_scores_map,
            "direct_score_sources": side_pressure_result.get("direct_score_sources") or {},
            "hard_stops": list(side_pressure_result.get("hard_stops") or []),
            "feedback": [],
            "raw_total": None,
            "near_acceptable_threshold": NEAR_ACCEPTANCE_FLOOR,
            "accept_threshold": ACCEPTANCE_THRESHOLD,
        }

    side_pressure_score = int(side_pressure_result["score"])

    # Step 3: base_side_pressure.
    base_debug = calculate_base_side_pressure(side_pressure_score)

    # Step 4-5: tier legitimacy + harshness penalty share raw harshness.
    if raw_total_harshness is None:
        raw_total_harshness = calculate_raw_treaty_harshness(
            {"clauses": [], "demands": list(_iter_terms(settlement_terms))}
        )
    tier_debug = calculate_settlement_tier_legitimacy(
        side_pressure_score, raw_total_harshness, settlement_terms,
    )
    harshness_debug = calculate_term_harshness_penalty(raw_total_harshness)

    # Step 6: leader_own_losses.
    leader_loss_debug = calculate_leader_own_losses(
        world,
        accepting_leader=accepting_leader,
        settlement_terms=settlement_terms,
        accepting_leader_regions_at_evaluation=accepting_leader_regions_at_evaluation,
        accepting_leader_mapped_holdings_at_entry=accepting_leader_mapped_holdings_at_entry,
    )

    # Step 7: burdened participant penalty (collect war objectives by enemy).
    war_objectives_by_enemy: Dict[str, Dict[str, Any]] = {}
    war_objectives_global = getattr(world, "war_objectives", {}) or {}
    for declarer in proposer_participants:
        for enemy in covered:
            if enemy == declarer:
                continue
            try:
                key = world._make_diplo_key(declarer, enemy)
            except Exception:
                key = "|".join(sorted([declarer, enemy]))
            obj = war_objectives_global.get(key, {}).get(declarer)
            if obj and obj.get("concluded_turn") is None:
                war_objectives_by_enemy.setdefault(enemy, obj)

    burden_debug = calculate_burdened_participant_penalty(
        world,
        accepting_leader=accepting_leader,
        proposer_side_participants=proposer_participants,
        covered_enemy_participants=covered,
        settlement_terms=settlement_terms,
        direct_scores=direct_scores_map,
        war_objectives_by_enemy=war_objectives_by_enemy,
    )

    # Step 8: projected hegemony.
    hegemony_debug = project_balance_after_settlement(
        world,
        war_id=war_id,
        settlement_terms=settlement_terms,
    )

    # Step 9: war objective alignment.
    alignment_debug = calculate_war_objective_alignment(
        world,
        war_id=war_id,
        proposer_side_leader=proposer_side_leader or (proposer_participants[0] if proposer_participants else None),
        proposer_side_participants=proposer_participants,
        accepting_leader=accepting_leader,
        covered_enemy_participants=covered,
        settlement_terms=settlement_terms,
    )

    # Step 10: war exhaustion (floor division per spec line 1120).
    exhaustion_debug = calculate_war_exhaustion_component(
        world,
        accepting_leader=accepting_leader,
        war_id=war_id,
        covered_enemy_participants=covered,
        apply_relevance_cap=apply_war_exhaustion_relevance_cap,
    )

    # Step 11: abandoned by ally.
    if current_turn is None:
        try:
            current_turn = int(getattr(world, "current_turn", 0) or 0)
        except Exception:
            current_turn = 0
    abandoned_debug = calculate_abandoned_by_ally_mod(
        war_instance,
        accepting_side=accepting_side,
        current_turn=int(current_turn),
    )

    # Step 12: aggregate.
    components = {
        "base_side_pressure": int(base_debug["score"]),
        "settlement_tier_legitimacy": int(tier_debug["score"]),
        "term_harshness_penalty": int(harshness_debug["score"]),
        "leader_own_losses": int(leader_loss_debug["score"]),
        "burdened_participant_penalty": int(burden_debug["score"]),
        "projected_hegemony_mod": int(hegemony_debug["modifier"]),
        "war_objective_alignment": int(alignment_debug["score"]),
        "war_exhaustion": int(exhaustion_debug["score"]),
        "abandoned_by_ally_acceptance_mod": int(abandoned_debug["score"]),
    }
    raw_total = sum(components.values())
    score = _clamp(int(raw_total), ACCEPTANCE_FINAL_CLAMP)

    # Step 13: verdict.
    if score >= ACCEPTANCE_THRESHOLD:
        verdict = "accept"
    elif score >= NEAR_ACCEPTANCE_FLOOR:
        verdict = "near_acceptable"
    else:
        verdict = "reject"

    # Step 14: feedback (top 1-2 components by absolute negative magnitude).
    feedback: List[Dict[str, Any]] = []
    if verdict in ("near_acceptable", "reject"):
        negatives = [
            (k, v) for k, v in components.items() if v < 0
        ]
        negatives.sort(key=lambda kv: (kv[1], kv[0]))
        for name, value in negatives[:2]:
            feedback.append({
                "component": name,
                "value": int(value),
                "magnitude": abs(int(value)),
            })

    # Step 15: forced-alliance threat preview.
    threat_preview = compute_forced_alliance_threat_preview(
        world, settlement_terms=settlement_terms,
    )

    component_debug = {
        "base_side_pressure": dict(base_debug),
        "settlement_tier_legitimacy": dict(tier_debug),
        "term_harshness_penalty": dict(harshness_debug),
        "leader_own_losses": dict(leader_loss_debug),
        "burdened_participant_penalty": dict(burden_debug),
        "projected_hegemony": dict(hegemony_debug),
        "projected_forced_alliance_threat_delta": int(threat_preview["projected_threat_delta"]),
        "crossed_coalition_thresholds": list(threat_preview["crossed_thresholds"]),
        "forced_alliance_threat_preview": dict(threat_preview),
        "war_objective_alignment": dict(alignment_debug),
        "war_exhaustion": dict(exhaustion_debug),
        "abandoned_by_ally": dict(abandoned_debug),
    }

    return {
        "score": int(score),
        "verdict": verdict,
        "components": components,
        "component_debug": component_debug,
        "side_pressure_score": side_pressure_score,
        "side_pressure_result": dict(side_pressure_result),
        "direct_scores": direct_scores_map,
        "direct_score_sources": side_pressure_result.get("direct_score_sources") or {},
        "hard_stops": list(side_pressure_result.get("hard_stops") or []),
        "feedback": feedback,
        "raw_total": int(raw_total),
        "raw_total_harshness": float(raw_total_harshness or 0.0),
        "near_acceptable_threshold": NEAR_ACCEPTANCE_FLOOR,
        "accept_threshold": ACCEPTANCE_THRESHOLD,
        "proposer_side": proposer_side,
        "accepting_side": accepting_side,
        "accepting_leader": accepting_leader,
        "proposer_side_participants": proposer_participants,
        "accepting_side_participants": accepting_participants,
        "covered_enemy_participants": list(covered),
        "current_turn": int(current_turn),
    }
