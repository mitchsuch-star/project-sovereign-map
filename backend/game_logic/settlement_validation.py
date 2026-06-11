"""Settlement term validation and eligibility (CH-1 split, layer 1).

Side/term primitives, clause-role helpers, the V1-V5 cross-court validator
(validate_settlement_terms), subjugation/vassalage/liberation eligibility,
pair-substitute eligibility, and open-settlement eligibility.
Split from settlement_preview.py (CH-1); may import settlement_routes only.
"""

from __future__ import annotations

from backend.game_logic.diplomatic_templates import resolve_settlement_voice_line
from backend.game_logic.settlement_scoring import (
    CANONICAL_CLAUSE_TYPES,
    CLAUSE_CONFLICT_MATRIX,
    GOLD_PER_TURN_MAX_TURNS,
    GOLD_PER_TURN_MIN_AMOUNT,
    GOLD_PER_TURN_MIN_TURNS,
    MAX_SETTLEMENT_CLAUSE_COUNT,
)
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Set,
)
from backend.game_logic.settlement_routes import (
    _error_display,
    _mounted_settlement_dialogue,
    _settlement_dialogue_active,
    is_war_archived,
)


VALID_SIDES = {"attackers", "defenders"}


def _blocked_payload(code: str, **extra: Any) -> Dict[str, Any]:
    display = _error_display(code)
    payload = {
        "available": False,
        "error": code,
        "error_display": display,
        "disabled_reason_display": display,
        "display_reason": display,
        **extra,
    }
    if code == "settlement_dialogue_active":
        payload["talleyrand_text"] = resolve_settlement_voice_line(
            "settlement_collision_active_review_talleyrand",
            active_war_label=str(extra.get("war_id") or "the active war"),
            blocked_war_label=str(extra.get("war_id") or "this war"),
        )
    return payload


# ---------------------------------------------------------------------------
# SC-33 / G2-Slice-9 - Recurring gold payment helpers
# ---------------------------------------------------------------------------


def _estimate_payer_net_income_per_turn(world: Any, payer: str) -> int:
    """Non-mutating per-turn net income estimate for `payer`.

    Sums region income for regions controlled by `payer` (the closest
    existing non-mutating income projection — `process_income_phase`
    debits upkeep and admin bonuses, which we avoid because they are
    not idempotent). Clamped at 0 because the validator capacity rule
    uses `max(0, expected_net_income_per_turn)`.

    Falls back to 0 when `world.regions` is unavailable so legacy
    schema-only callers degrade safely.
    """
    regions = getattr(world, "regions", None) or {}
    income = 0
    for region in regions.values():
        if getattr(region, "controller", None) != payer:
            continue
        try:
            income += int(region.get_effective_income())
        except Exception:
            continue
    return max(0, int(income))


def _check_gold_payment_budget_conflict(
    world: Any,
    terms: List[Mapping[str, Any]],
) -> Optional[Dict[str, Any]]:
    """SC-1 / SC-33 budget conflict: combined gold obligations versus
    projected solvency, per the cleanup spec.

    Formula (per implementation directive May 14, 2026):

        payer_new_obligation =
            lump_sum_gold_due_now + sum(amount * turns) over submitted
            `gold_per_turn` clauses authored by the payer
        payer_existing_obligation =
            sum of (amount_per_turn * turns_remaining) over the payer's
            existing `world.recurring_settlement_payments`
        capacity =
            current_gold
            + max(0, expected_net_income_per_turn)
              * max_turns_in_submitted_terms

    Rejects with `gold_payment_budget_conflict` when
    `payer_new_obligation + payer_existing_obligation > capacity`. The
    rejection names the offending clause index so the editor can focus
    the budget conflict on the recurring entry.
    """
    nation_gold = getattr(world, "nation_gold", None) or {}
    payer_obligations: Dict[str, Dict[str, Any]] = {}
    max_turns = 0
    for idx, clause in enumerate(terms):
        ctype = clause.get("type")
        if ctype not in ("gold_indemnity", "gold_lump", "gold_per_turn"):
            continue
        payer = str(clause.get("from") or "")
        if not payer:
            continue
        amount = int(clause.get("amount", 0) or 0)
        record = payer_obligations.setdefault(
            payer,
            {"lump": 0, "recurring": 0, "max_turns": 0, "last_recurring_idx": None},
        )
        if ctype == "gold_per_turn":
            turns = int(clause.get("turns", 0) or 0)
            if turns <= 0 or amount <= 0:
                continue
            record["recurring"] += amount * turns
            record["max_turns"] = max(record["max_turns"], turns)
            record["last_recurring_idx"] = idx
            max_turns = max(max_turns, turns)
        else:
            record["lump"] += abs(amount)
    if not payer_obligations:
        return None

    existing = getattr(world, "recurring_settlement_payments", None) or []
    for payer, data in payer_obligations.items():
        existing_obligation = 0
        for entry in existing:
            if not isinstance(entry, Mapping):
                continue
            if str(entry.get("from") or "") != payer:
                continue
            existing_obligation += int(
                int(entry.get("amount_per_turn", 0) or 0)
                * int(entry.get("turns_remaining", 0) or 0)
            )
        current_gold = int(nation_gold.get(payer, 0) or 0)
        net_income = _estimate_payer_net_income_per_turn(world, payer)
        capacity = current_gold + max(0, net_income) * max(0, data["max_turns"])
        new_obligation = int(data["lump"]) + int(data["recurring"])
        if new_obligation + existing_obligation > capacity:
            error_index = data["last_recurring_idx"]
            if error_index is None:
                # Lump-sum-only budget conflict: focus the first lump-sum
                # clause for this payer.
                for jdx, clause in enumerate(terms):
                    if clause.get("type") in ("gold_indemnity", "gold_lump") and (
                        str(clause.get("from") or "") == payer
                    ):
                        error_index = jdx
                        break
            return {
                "valid": False,
                "error": "gold_payment_budget_conflict",
                "error_index": error_index,
                "disabled_reason_display": _error_display(
                    "gold_payment_budget_conflict"
                ),
            }
    return None


def compute_gold_payer_budgets(
    world: Any,
    terms: Iterable[Mapping[str, Any]],
    extra_payers: Iterable[str] = (),
) -> Dict[str, int]:
    """Per-payer TOTAL gold capacity for a candidate package — the clamp-side
    mirror of ``_check_gold_payment_budget_conflict`` (Gate-4 G4F-2 / DC-1).

    Same capacity formula the validator enforces: current gold plus
    ``max(0, net income) * the payer's longest submitted gold_per_turn
    stream``, minus the payer's existing ``recurring_settlement_payments``
    obligations. The Tier-2 dial and the guided magnitude verbs consume this
    budget line by line so a system-authored mutation can never produce a
    package the restage validator would bounce with
    ``gold_payment_budget_conflict`` — valid-by-construction applies to the
    author, not just the player (pre-flight audit DC-1).

    ``extra_payers`` adds payers with no gold line yet (the focused-dial
    seed's court / the proposer leader) so the seed can be budget-checked.
    Returned budgets are floored at 0.
    """
    term_list = [t for t in (terms or []) if isinstance(t, Mapping)]
    payers: Set[str] = {str(n) for n in (extra_payers or []) if n}
    max_turns_by_payer: Dict[str, int] = {}
    for clause in term_list:
        if clause.get("type") not in ("gold_indemnity", "gold_lump", "gold_per_turn"):
            continue
        payer = str(clause.get("from") or "")
        if not payer:
            continue
        payers.add(payer)
        if clause.get("type") == "gold_per_turn":
            turns = int(clause.get("turns", 0) or 0)
            if turns > 0:
                max_turns_by_payer[payer] = max(
                    max_turns_by_payer.get(payer, 0), turns
                )
    nation_gold = getattr(world, "nation_gold", None) or {}
    existing = getattr(world, "recurring_settlement_payments", None) or []
    budgets: Dict[str, int] = {}
    for payer in payers:
        existing_obligation = 0
        for entry in existing:
            if not isinstance(entry, Mapping):
                continue
            if str(entry.get("from") or "") != payer:
                continue
            existing_obligation += int(
                int(entry.get("amount_per_turn", 0) or 0)
                * int(entry.get("turns_remaining", 0) or 0)
            )
        current_gold = int(nation_gold.get(payer, 0) or 0)
        net_income = _estimate_payer_net_income_per_turn(world, payer)
        capacity = current_gold + max(0, net_income) * max(
            0, max_turns_by_payer.get(payer, 0)
        )
        budgets[payer] = max(0, int(capacity) - existing_obligation)
    return budgets


def _other_side(side: str) -> str:
    return "defenders" if side == "attackers" else "attackers"


def _side_leader(war_instance: Mapping[str, Any], side: str) -> Optional[str]:
    if side == "attackers":
        return war_instance.get("attacker_leader")
    if side == "defenders":
        return war_instance.get("defender_leader")
    return None


def _side_for_nation(war_instance: Mapping[str, Any], nation: str) -> Optional[str]:
    nation_name = str(nation or "")
    if nation_name in set(war_instance.get("attackers") or []):
        return "attackers"
    if nation_name in set(war_instance.get("defenders") or []):
        return "defenders"
    side_by_nation = war_instance.get("side_by_nation") or {}
    side = str(side_by_nation.get(nation_name) or "")
    return side if side in VALID_SIDES else None


def _pair_nations(pair: str) -> List[str]:
    return [p for p in str(pair).split("|") if p]


def _active_cross_side_pairs(
    war_instance: Mapping[str, Any],
    proposer_side: str,
) -> List[str]:
    proposers = set(war_instance.get(proposer_side) or [])
    enemies = set(war_instance.get(_other_side(proposer_side)) or [])
    meta = war_instance.get("diplo_key_meta") or {}
    pairs: List[str] = []
    for pair in war_instance.get("active_diplo_keys") or []:
        pair_meta = meta.get(pair) or {}
        if pair_meta.get("pair_status", "war") not in ("war", "armistice"):
            continue
        nations = _pair_nations(pair)
        if len(nations) != 2:
            continue
        a, b = nations
        if (a in proposers and b in enemies) or (b in proposers and a in enemies):
            pairs.append(pair)
    return sorted(pairs)


PAIR_SUBSTITUTE_ACTIONS = frozenset({"seek_armistice_instead", "seek_bilateral_peace"})


PAIR_SUBSTITUTE_TEMPORAL_REFUSAL_CODES = frozenset({"cooldown_active"})


PAIR_SUBSTITUTE_REFUSAL_CODES = frozenset({
    "already_at_peace",
    "already_in_armistice",
    "pair_not_at_war",
    "war_archived",
    "actor_not_at_war_with_target",
    "target_not_selected_pair",
    "target_not_in_war",
    "settlement_collision_active",
    "cooldown_active",
    "insufficient_resources",
    "malformed_route",
})


def evaluate_pair_peace_substitute_eligibility(
    world: Any,
    *,
    war_id: str,
    actor_nation: str,
    target_nation: str,
    action: str,
) -> Dict[str, Any]:
    """SC-29 / G2-Slice-7: decide whether a rejected settlement popup may
    expose `Seek Armistice Instead` or `Seek Bilateral Peace` for the
    selected actor/target pair.

    Returns a dict whose shape is pinned by the spec
    "Pair substitute eligibility helper schema":

        {
            "eligible": bool,
            "refusal_code": str | null,
            "disabled_reason_display": str | null,
            "selected_pair": {
                "actor": str,
                "target": str,
                "war_id": str,
            },
        }

    The refusal taxonomy is closed (see `PAIR_SUBSTITUTE_REFUSAL_CODES`).
    Only `cooldown_active` is a temporal disabled state per spec
    "Disabled vs Hidden Affordance Policy"; every other code hides the
    substitute action rather than rendering it disabled.
    """
    war_id_str = str(war_id or "")
    actor = str(actor_nation or "").strip()
    target = str(target_nation or "").strip()
    action_str = str(action or "").strip()

    selected_pair = {"actor": actor, "target": target, "war_id": war_id_str}

    def _refused(code: str) -> Dict[str, Any]:
        return {
            "eligible": False,
            "refusal_code": code,
            "disabled_reason_display": _error_display(code),
            "selected_pair": selected_pair,
        }

    if action_str not in PAIR_SUBSTITUTE_ACTIONS:
        return _refused("malformed_route")
    if not war_id_str or not actor or not target:
        return _refused("malformed_route")
    if actor == target:
        return _refused("malformed_route")

    instance = (getattr(world, "war_instances", {}) or {}).get(war_id_str)
    if not isinstance(instance, Mapping):
        if is_war_archived(world, war_id_str):
            return _refused("war_archived")
        return _refused("malformed_route")
    if instance.get("ended_turn") is not None:
        return _refused("war_archived")

    side_by_nation = instance.get("side_by_nation") or {}
    actor_side = side_by_nation.get(actor)
    target_side = side_by_nation.get(target)
    if not actor_side:
        return _refused("actor_not_at_war_with_target")
    if not target_side:
        return _refused("target_not_in_war")
    if actor_side == target_side:
        return _refused("target_not_selected_pair")

    pair = (
        world._make_diplo_key(actor, target)
        if hasattr(world, "_make_diplo_key")
        else "|".join(sorted([actor, target]))
    )
    pair_state = (getattr(world, "diplomatic_states", {}) or {}).get(pair)
    if pair_state == "PEACE":
        return _refused("already_at_peace")
    if pair_state == "ARMISTICE":
        if action_str == "seek_armistice_instead":
            return _refused("already_in_armistice")
    if pair_state not in ("WAR", "ARMISTICE"):
        return _refused("actor_not_at_war_with_target")

    meta = instance.get("diplo_key_meta") or {}
    pair_meta = meta.get(pair) or {}
    resolved_pairs = set(instance.get("resolved_diplo_keys") or [])
    if pair in resolved_pairs or pair_meta.get("pair_status") == "resolved":
        return _refused("pair_not_at_war")
    active_pairs = set(instance.get("active_diplo_keys") or [])
    if pair not in active_pairs:
        return _refused("target_not_selected_pair")
    pair_status = pair_meta.get("pair_status", "war")
    if pair_status == "armistice" and action_str == "seek_armistice_instead":
        return _refused("already_in_armistice")
    if pair_status not in ("war", "armistice"):
        return _refused("pair_not_at_war")
    if action_str == "seek_bilateral_peace" and pair_state == "WAR" and pair_status != "war":
        # State and pair_status disagree — fail safe so we never advertise
        # a substitute action on a stale view.
        return _refused("pair_not_at_war")

    mounted = _mounted_settlement_dialogue(world)
    if mounted is not None and str(mounted.get("war_id") or "") not in ("", war_id_str):
        return _refused("settlement_collision_active")

    cooldowns = getattr(world, "player_proposal_cooldowns", None) or {}
    proposal_type = "armistice" if action_str == "seek_armistice_instead" else "peace"
    type_key = f"{target}_{proposal_type}"
    if isinstance(cooldowns, Mapping):
        if cooldowns.get(target, 0) > 0:
            return _refused("cooldown_active")
        if cooldowns.get(type_key, 0) > 0:
            return _refused("cooldown_active")

    # DP cost is computed via the same helper the proposal executor uses,
    # so the substitute CTA never advertises a proposal the player cannot
    # actually send.
    try:
        from backend.game_logic.diplomacy import get_dp_cost, get_transition_dp_cost
    except Exception:  # pragma: no cover - defensive import guard
        get_dp_cost = None
        get_transition_dp_cost = None
    if get_dp_cost is not None and get_transition_dp_cost is not None:
        _state_map = {
            "peace": "PEACE",
            "armistice": "ARMISTICE",
        }
        try:
            current_diplo = world.get_diplomatic_state(actor, target)
        except Exception:  # pragma: no cover - defensive
            current_diplo = pair_state or "WAR"
        target_diplo = _state_map.get(proposal_type, "PEACE")
        jump_cost = get_transition_dp_cost(current_diplo, target_diplo)
        try:
            from backend.nation_config import get_player_diplomat
            talleyrand = get_player_diplomat(world)
            skill = int(getattr(talleyrand, "skill", 5)) if talleyrand else 5
        except Exception:  # pragma: no cover - defensive
            skill = 5
        cost = get_dp_cost(f"propose_{proposal_type}", skill, transition_base=jump_cost)
        if float(getattr(world, "diplomatic_points", 0) or 0) < float(cost):
            return _refused("insufficient_resources")

    return {
        "eligible": True,
        "refusal_code": None,
        "disabled_reason_display": None,
        "selected_pair": selected_pair,
    }


# ---------------------------------------------------------------------------
# G2-Slice-3 helpers: route id, collision, reopen cap, active-vs-archived
# ---------------------------------------------------------------------------


def _terms_equal(a: Mapping[str, Any], b: Mapping[str, Any]) -> bool:
    """Strict equality for clause merge conflict detection.

    Two same-key clauses are equal only when every field matches. Same
    region with different gold amounts conflicts; same region with
    identical fields is a duplicate (the merge ignores duplicates).
    """
    keys = set(a.keys()) | set(b.keys())
    for key in keys:
        if a.get(key) != b.get(key):
            return False
    return True


def _territory_term_regions(term: Mapping[str, Any]) -> List[str]:
    regions = term.get("regions")
    if isinstance(regions, (list, tuple)) and regions:
        return [str(r) for r in regions if str(r)]
    region = str(term.get("region") or "")
    return [region] if region else []


def _normalize_staged_terms_for_validation(
    settlement_terms: Iterable[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    """Return a canonical-shaped COPY of staged settlement terms for the
    ratify-time defense-in-depth revalidation (the mutation path keeps
    consuming the originals — this never mutates ``settlement_terms``).

    Staged packages may carry two apply-format variances that the canonical
    ``validate_settlement_terms`` schema would otherwise reject (the legacy
    ratification fixtures + historical drafts the type-only guard tolerates):

    - ``gold_lump`` (``RATIFY_LEGACY_APPLY_CLAUSE_TYPES``) → ``gold_indemnity``.
    - ``territory_cede`` carrying a plural ``regions`` list → one canonical
      single-``region`` clause per region (mirrors ``_territory_term_regions``).

    Every other clause passes through untouched, so any genuinely-malformed
    staged clause still fails revalidation (defense in depth, not laundering).
    """
    normalized: List[Dict[str, Any]] = []
    for term in settlement_terms or []:
        if not isinstance(term, Mapping):
            # Leave non-mappings for the validator to reject.
            normalized.append(term)  # type: ignore[arg-type]
            continue
        clause = dict(term)
        if clause.get("type") == "gold_lump":
            clause["type"] = "gold_indemnity"
        if clause.get("type") == "territory_cede" and isinstance(
            clause.get("regions"), (list, tuple)
        ):
            regions = [str(r) for r in (clause.get("regions") or []) if str(r)]
            base = {k: v for k, v in clause.items() if k not in ("regions", "region")}
            if not regions:
                # No usable region — keep one clause so the schema check still
                # surfaces the missing `region` rather than silently dropping it.
                normalized.append(base)
            else:
                for region in regions:
                    single = dict(base)
                    single["region"] = region
                    normalized.append(single)
            continue
        normalized.append(clause)
    return normalized


def _has_material_concession_terms(terms: Iterable[Mapping[str, Any]]) -> bool:
    return any(
        isinstance(term, Mapping) and term.get("type") != "peace"
        for term in (terms or [])
    )


def _term_lists_equal(
    left: Iterable[Mapping[str, Any]],
    right: Iterable[Mapping[str, Any]],
) -> bool:
    left_terms = [dict(t) for t in (left or []) if isinstance(t, Mapping)]
    right_terms = [dict(t) for t in (right or []) if isinstance(t, Mapping)]
    if len(left_terms) != len(right_terms):
        return False
    return all(_terms_equal(a, b) for a, b in zip(left_terms, right_terms))


def _infer_actor_side(
    war_instance: Mapping[str, Any],
    actor_nation: str,
    proposer_side: Optional[str],
) -> Optional[str]:
    if proposer_side in VALID_SIDES:
        return proposer_side
    side_by_nation = war_instance.get("side_by_nation") or {}
    side = side_by_nation.get(actor_nation)
    if side in VALID_SIDES:
        return side
    for candidate in ("attackers", "defenders"):
        if actor_nation in (war_instance.get(candidate) or []):
            return candidate
    return None


def get_coverable_enemy_participants(
    war_instance: Mapping[str, Any],
    proposer_side: str,
) -> List[str]:
    """Return opposing-side participants with active unresolved cross-pairs."""
    accepting_side = _other_side(proposer_side)
    enemies = set(war_instance.get(accepting_side) or [])
    pairs = _active_cross_side_pairs(war_instance, proposer_side)
    coverable = set()
    for pair in pairs:
        for nation in _pair_nations(pair):
            if nation in enemies:
                coverable.add(nation)
    leader = _side_leader(war_instance, accepting_side)
    if leader in enemies:
        coverable.add(str(leader))
    return sorted(coverable)


def is_common_settlement_worth_showing(war_instance: Mapping[str, Any]) -> bool:
    """Return True when common peace adds value over bilateral peace."""
    if not isinstance(war_instance, Mapping):
        return False
    attackers = list(war_instance.get("attackers") or [])
    defenders = list(war_instance.get("defenders") or [])
    return len(set(attackers + defenders)) > 2


# SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1 Concession Baseline.
# Spec §"Concession And Treaty Conversation Contract" pins the deterministic
# normal-gameplay algorithm: losing-side predicate uses
# `side_pressure_score <= LOSING_SIDE_PRESSURE_THRESHOLD`, gold candidate is
# the smallest strictly positive of (treasury - reserve, hard cap, acceptance
# gap * 100), and territory escalation uses BFS distance from the accepting
# leader's capital with deterministic tie-breaking.
LOSING_SIDE_PRESSURE_THRESHOLD = -20


def _resolve_war_sides(
    war_instance: Mapping[str, Any], nation: str
) -> Optional[str]:
    """Return ``"attackers"`` / ``"defenders"`` for ``nation`` on a war."""
    for side in VALID_SIDES:
        if nation in (war_instance.get(side) or []):
            return side
    return None


def _dependency_eligibility_payload(
    eligible: bool,
    *,
    refusal_code: str = "",
    extra: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    if eligible:
        payload: Dict[str, Any] = {"eligible": True, "refusal_code": None, "disabled_reason_display": None}
    else:
        payload = {
            "eligible": False,
            "refusal_code": refusal_code or "dependency_invalid",
            "disabled_reason_display": _error_display(refusal_code or "dependency_invalid"),
        }
    if extra:
        payload.update(dict(extra))
    return payload


def _check_vassalage_state(
    world: Any,
    *,
    war_instance: Mapping[str, Any],
    lord_nation: str,
    target_nation: str,
) -> Dict[str, Any]:
    """Shared pre-checks for vassalage / subjugation.

    Returns an eligible payload OR a refusal payload from the closed
    taxonomy ``dependency_*``. Power-cap is checked separately so
    callers can branch on `dependency_power_cap_blocked` independently.
    """
    if not lord_nation or not target_nation or lord_nation == target_nation:
        return _dependency_eligibility_payload(False, refusal_code="dependency_direction_invalid")
    lord_side = _resolve_war_sides(war_instance, lord_nation)
    target_side = _resolve_war_sides(war_instance, target_nation)
    if lord_side is None or target_side is None or lord_side == target_side:
        return _dependency_eligibility_payload(False, refusal_code="dependency_target_not_in_war")
    pair_key = world._make_diplo_key(lord_nation, target_nation)
    meta = (war_instance.get("diplo_key_meta") or {}).get(pair_key) or {}
    pair_status = str(meta.get("pair_status") or "")
    if pair_status not in ("war", "armistice"):
        return _dependency_eligibility_payload(False, refusal_code="dependency_target_not_in_war")
    vassals = getattr(world, "vassals", {}) or {}
    if target_nation in vassals:
        return _dependency_eligibility_payload(False, refusal_code="dependency_target_already_vassal")
    return _dependency_eligibility_payload(True)


def evaluate_subjugation_eligibility(
    world: Any,
    *,
    war_instance: Mapping[str, Any],
    lord_nation: str,
    target_nation: str,
) -> Dict[str, Any]:
    """Whether a ``subjugation`` clause may target ``target_nation``.

    Direction is canonical: ``target_nation`` is the prospective vassal
    (clause ``from``); ``lord_nation`` is the prospective lord (clause
    ``to``). Power-cap is enforced through `check_vassalage_power_cap`
    so a defeated giant cannot be forcibly vassalized by a smaller
    coalition member.
    """
    state = _check_vassalage_state(
        world,
        war_instance=war_instance,
        lord_nation=lord_nation,
        target_nation=target_nation,
    )
    if not state.get("eligible"):
        return state
    from backend.game_logic.diplomacy import check_vassalage_power_cap
    cap = check_vassalage_power_cap(world, lord_nation, target_nation)
    if not cap.get("allowed"):
        return _dependency_eligibility_payload(
            False,
            refusal_code="dependency_power_cap_blocked",
            extra={
                "lord_power": int(cap.get("lord_power", 0) or 0),
                "target_power": int(cap.get("target_power", 0) or 0),
                "power_pct": int(cap.get("pct", 0) or 0),
            },
        )
    return _dependency_eligibility_payload(
        True,
        extra={
            "lord_power": int(cap.get("lord_power", 0) or 0),
            "target_power": int(cap.get("target_power", 0) or 0),
            "power_pct": int(cap.get("pct", 0) or 0),
        },
    )


def evaluate_vassalage_eligibility(
    world: Any,
    *,
    war_instance: Mapping[str, Any],
    lord_nation: str,
    target_nation: str,
) -> Dict[str, Any]:
    """Whether a ``vassalage`` (treaty path) clause may target ``target_nation``.

    Treaty vassalization shares the same pre-checks as subjugation —
    direction, war state, not-already-vassal, and the power cap.
    """
    return evaluate_subjugation_eligibility(
        world,
        war_instance=war_instance,
        lord_nation=lord_nation,
        target_nation=target_nation,
    )


def evaluate_liberation_eligibility(
    world: Any,
    *,
    war_instance: Mapping[str, Any],
    vassal_nation: str,
    lord_nation: str,
    liberator: str,
) -> Dict[str, Any]:
    """Whether a ``liberation`` clause may free ``vassal_nation``.

    Liberation requires (a) the target is currently someone's vassal,
    (b) the declared ``lord_nation`` matches the current lord, and
    (c) the ``liberator`` is a recognized nation different from the
    current lord. The pair (lord vs liberator) must also currently be
    on opposite sides of the war so the clause has cross-side authority.
    """
    if not vassal_nation:
        return _dependency_eligibility_payload(
            False, refusal_code="liberation_target_not_vassal"
        )
    vassals = getattr(world, "vassals", {}) or {}
    state = vassals.get(vassal_nation)
    if not isinstance(state, Mapping):
        return _dependency_eligibility_payload(
            False, refusal_code="liberation_target_not_vassal"
        )
    current_lord = str(state.get("lord") or state.get("lord_nation") or "")
    if not current_lord or current_lord != lord_nation:
        return _dependency_eligibility_payload(
            False, refusal_code="liberation_lord_mismatch",
            extra={"current_lord": current_lord},
        )
    if not liberator or liberator == current_lord or liberator == vassal_nation:
        return _dependency_eligibility_payload(
            False, refusal_code="liberation_invalid_liberator"
        )
    # Liberator must be a known nation in the world; reject typos.
    known_nations: Set[str] = set()
    diplomatic_states = getattr(world, "diplomatic_states", {}) or {}
    for key in diplomatic_states:
        for part in str(key).split("|"):
            if part:
                known_nations.add(part)
    if liberator not in known_nations:
        return _dependency_eligibility_payload(
            False, refusal_code="liberation_invalid_liberator"
        )
    lord_side = _resolve_war_sides(war_instance, current_lord)
    liberator_side = _resolve_war_sides(war_instance, liberator)
    if lord_side is None or liberator_side is None or lord_side == liberator_side:
        return _dependency_eligibility_payload(
            False, refusal_code="liberation_invalid_liberator"
        )
    return _dependency_eligibility_payload(
        True, extra={"current_lord": current_lord},
    )


def _clause_touches_court(clause: Any, court: str) -> bool:
    """True when a material clause names ``court`` on either side."""
    if not isinstance(clause, Mapping) or clause.get("type") == "peace":
        return False
    return court in (
        str(clause.get("from") or ""),
        str(clause.get("to") or ""),
    )


def evaluate_open_settlement_eligibility(
    world: Any,
    *,
    war_id: str,
    actor_nation: Optional[str] = None,
    proposer_side: Optional[str] = None,
    ignore_active_dialogue: bool = False,
) -> Dict[str, Any]:
    """Spec §10.3 Open Settlement eligibility / grey-out rules."""
    actor = actor_nation or getattr(world, "player_nation", "France")
    instance = (getattr(world, "war_instances", {}) or {}).get(war_id)
    if not instance:
        return _blocked_payload("invalid_war_id", war_id=war_id)
    if instance.get("ended_turn") is not None:
        return _blocked_payload("inactive_war_instance", war_id=war_id)
    if not is_common_settlement_worth_showing(instance):
        return _blocked_payload("one_to_one_war", war_id=war_id)

    side = _infer_actor_side(instance, actor, proposer_side)
    if side not in VALID_SIDES:
        return _blocked_payload("not_side_leader", war_id=war_id)
    if _side_leader(instance, side) != actor:
        return _blocked_payload("not_side_leader", war_id=war_id, proposer_side=side)

    pairs = _active_cross_side_pairs(instance, side)
    if not pairs:
        return _blocked_payload("no_unresolved_hostile_pairs", war_id=war_id, proposer_side=side)
    if len(pairs) == 1:
        return _blocked_payload("one_to_one_war", war_id=war_id, proposer_side=side)

    coverable = get_coverable_enemy_participants(instance, side)
    if not coverable:
        return _blocked_payload("no_coverable_enemy", war_id=war_id, proposer_side=side)

    if not ignore_active_dialogue and _settlement_dialogue_active(world, war_id):
        return _blocked_payload("settlement_dialogue_active", war_id=war_id, proposer_side=side)

    accepting_side = _other_side(side)
    return {
        "available": True,
        "war_id": war_id,
        "proposer_side": side,
        "accepting_side": accepting_side,
        "proposer_leader": _side_leader(instance, side),
        "accepting_leader": _side_leader(instance, accepting_side),
        "active_diplo_keys": pairs,
        "coverable_enemy_participants": coverable,
    }


# Re-front Slice 3 §12 V3: clause types that move value across the war and so
# must bind two participants on OPPOSITE war sides (demand burdens the accepting
# side; concession burdens the proposer side — either way `from`/`to` straddle
# the line). Dependency clauses (vassalage/subjugation/liberation) carry their
# own cross-side eligibility checks and are excluded here.
_CROSS_SIDE_TRANSFER_CLAUSE_TYPES = frozenset(
    {"territory_cede", "gold_indemnity", "gold_per_turn", "forced_alliance"}
)


def _clause_role_nations(clause: Mapping[str, Any]) -> List[str]:
    """Enemy/proposer courts a clause binds, for the V2 coverage check.

    Every clause binds ``from``/``to`` except ``liberation``, which binds
    its ``lord_nation`` (the covered enemy losing the vassal) and
    ``liberator`` (a proposer-side participant). ``vassal_nation`` is
    deliberately excluded: it is the freed party, not a court bound into
    the settlement, and ``evaluate_liberation_eligibility`` (§12 V4) never
    requires it to be a war participant — so checking it here would
    over-reject valid liberations of a non-participant vassal. ``peace``
    binds nothing.
    """
    if str(clause.get("type") or "") == "liberation":
        keys = ("lord_nation", "liberator")
    else:
        keys = ("from", "to")
    return [
        str(clause.get(k)).strip()
        for k in keys
        if str(clause.get(k) or "").strip()
    ]


def validate_settlement_terms(
    terms: Any,
    *,
    actor_nation: Optional[str] = None,
    player_nation: Optional[str] = None,
    proposer_side: Optional[str] = None,
    actor_side_in_war: Optional[str] = None,
    covered_enemy_participants: Optional[Iterable[str]] = None,
    world: Any = None,
    war_instance: Optional[Mapping[str, Any]] = None,
    enforce_solvency: bool = True,
) -> Dict[str, Any]:
    """SC-1 POST preview clause validation.

    Returns {"valid": True} or {"valid": False, "error": ..., "error_index": ...,
    "disabled_reason_display": ...}.

    SC-31 / G2-Slice-8: when ``world`` and ``war_instance`` are supplied,
    dependency-clause direction, target eligibility, and power-cap legality
    are additionally enforced. Hidden clause types are never live in
    `CLAUSE_CONTROL_SCHEMA`, but illegal-by-state dependency clauses
    submitted via tampered payloads return canonical error codes:

    - ``dependency_direction_invalid`` — vassalage / subjugation use
      ``from = vassal/subjugated, to = lord``; the validator rejects
      reversed projections.
    - ``dependency_target_not_in_war`` — vassalage / subjugation target
      must currently be at WAR or ARMISTICE with the lord on the war
      instance.
    - ``dependency_target_already_vassal`` — vassalage / subjugation
      target is already someone's vassal.
    - ``dependency_power_cap_blocked`` — lord power is not at least
      ``POWER_CAP_RATIO`` × target power.
    - ``liberation_target_not_vassal`` — liberation target is not
      currently a vassal of any lord.
    - ``liberation_lord_mismatch`` — declared ``lord_nation`` does not
      match the current lord of ``vassal_nation``.
    - ``liberation_invalid_liberator`` — ``liberator`` is missing,
      equal to the current lord, or not a recognized nation.

    Re-front Slice 3 §12 multi-party cross-court validity rules (defense in
    depth at POST-preview, Submit revalidation, and dial/coverage restage):

    - ``region_double_promised`` — the same region appears in more than one
      ``territory_cede`` clause (V1). Always enforced (structural).
    - ``clause_target_uncovered`` — a clause names a court that is neither
      proposer-side nor in ``covered_enemy_participants`` (V2). Enforced when
      ``war_instance`` is supplied and a ``covered_enemy_participants`` /
      ``proposer_side`` context lets the allowed set be derived.
    - ``clause_side_mismatch`` — a value-transfer clause's ``from`` and ``to``
      are not on opposite, known war sides (V3). Enforced when ``war_instance``
      is supplied.

    ``enforce_solvency`` gates only the authoring-time gold budget/solvency
    check (``_check_gold_payment_budget_conflict``). It is ``True`` for every
    authoring caller (POST-preview / Submit / restage). The ratify-time
    defense-in-depth revalidation passes ``False`` because the apply path
    *clamps* a gold transfer to the payer's available balance rather than
    blocking it (a winning settlement is never voided by a payer who has since
    spent down), so re-running the solvency gate there would wrongly reject a
    clamp-valid package. Every other rule — structural (V1), coverage (V2),
    war-side (V3), self-reference/dependency eligibility (V4) — still runs.
    """
    if actor_nation and player_nation and actor_nation != player_nation:
        return {
            "valid": False,
            "error": "unauthorized_actor",
            "disabled_reason_display": _error_display("unauthorized_actor"),
        }
    if proposer_side and actor_side_in_war and proposer_side != actor_side_in_war:
        return {
            "valid": False,
            "error": "proposer_side_mismatch",
            "disabled_reason_display": _error_display("proposer_side_mismatch"),
        }
    if not isinstance(terms, list):
        return {
            "valid": False,
            "error": "invalid_clause_schema",
            "disabled_reason_display": _error_display("invalid_clause_schema"),
        }
    if not terms:
        return {
            "valid": False,
            "error": "empty_authored_draft",
            "disabled_reason_display": _error_display("empty_authored_draft"),
        }
    if len(terms) > MAX_SETTLEMENT_CLAUSE_COUNT:
        return {
            "valid": False,
            "error": "max_clause_count_exceeded",
            "error_index": MAX_SETTLEMENT_CLAUSE_COUNT,
            "disabled_reason_display": _error_display("max_clause_count_exceeded"),
        }
    for idx, clause in enumerate(terms):
        if not isinstance(clause, Mapping):
            return {
                "valid": False,
                "error": "invalid_clause_schema",
                "error_index": idx,
                "disabled_reason_display": _error_display("invalid_clause_schema"),
            }
        ctype = clause.get("type")
        if ctype not in CANONICAL_CLAUSE_TYPES:
            return {
                "valid": False,
                "error": "invalid_clause_type",
                "error_index": idx,
                "disabled_reason_display": _error_display("invalid_clause_type"),
            }
        spec = CANONICAL_CLAUSE_TYPES[ctype]
        required = set(spec["required"])
        optional = set(spec.get("optional") or set())
        clause_keys = set(clause.keys())
        missing = required - clause_keys
        if missing:
            return {
                "valid": False,
                "error": "invalid_clause_schema",
                "error_index": idx,
                "missing_keys": sorted(missing),
                "disabled_reason_display": _error_display("invalid_clause_schema"),
            }
        unknown = clause_keys - required - optional
        if unknown:
            return {
                "valid": False,
                "error": "invalid_clause_schema",
                "error_index": idx,
                "unknown_keys": sorted(unknown),
                "disabled_reason_display": _error_display("invalid_clause_schema"),
            }
    for type_a, type_b, match_keys in CLAUSE_CONFLICT_MATRIX:
        clauses_a = [c for c in terms if c.get("type") == type_a]
        clauses_b = [c for c in terms if c.get("type") == type_b]
        for ca in clauses_a:
            for cb in clauses_b:
                if all(ca.get(k) == cb.get(k) for k in match_keys):
                    return {
                        "valid": False,
                        "error": "duplicate_or_conflicting_clauses",
                        "error_index": terms.index(cb),
                        "conflicting_index": terms.index(ca),
                        "disabled_reason_display": _error_display("duplicate_or_conflicting_clauses"),
                    }

    # Re-front Slice 3 §12 V1: no region promised to two courts. Each region may
    # appear in at most one `territory_cede` clause regardless of from/to. This
    # is structural (no world/war_instance needed) so it always runs.
    seen_regions: Dict[str, int] = {}
    for idx, clause in enumerate(terms):
        if clause.get("type") != "territory_cede":
            continue
        region = str(clause.get("region") or "")
        if not region:
            continue
        if region in seen_regions:
            return {
                "valid": False,
                "error": "region_double_promised",
                "error_index": idx,
                "conflicting_index": seen_regions[region],
                "disabled_reason_display": _error_display("region_double_promised"),
            }
        seen_regions[region] = idx

    # Re-front Slice 3 §12 V2/V3: cross-court binding + war-side validity. Both
    # need the live `war_instance` to resolve sides; bare schema-only callers
    # (no war_instance) skip them, matching the dependency-clause gate below.
    if isinstance(war_instance, Mapping) and war_instance:
        covered_set = {
            str(n).strip()
            for n in (covered_enemy_participants or [])
            if str(n).strip()
        }
        ps = str(proposer_side or "")
        proposer_participants: Set[str] = (
            {
                str(n).strip()
                for n in (war_instance.get(ps) or [])
                if str(n).strip()
            }
            if ps in VALID_SIDES
            else set()
        )
        # V2: every clause role nation must be proposer-side or covered. Only
        # enforced when BOTH the proposer side and the covered set are known, so
        # a partial-context caller is never over-constrained.
        if proposer_participants and covered_set:
            allowed = proposer_participants | covered_set
            for idx, clause in enumerate(terms):
                for role_nation in _clause_role_nations(clause):
                    if role_nation not in allowed:
                        return {
                            "valid": False,
                            "error": "clause_target_uncovered",
                            "error_index": idx,
                            "uncovered_nation": role_nation,
                            "disabled_reason_display": _error_display(
                                "clause_target_uncovered"
                            ),
                        }
        # V3: value-transfer clauses must straddle opposite, known war sides.
        for idx, clause in enumerate(terms):
            if clause.get("type") not in _CROSS_SIDE_TRANSFER_CLAUSE_TYPES:
                continue
            frm = str(clause.get("from") or "")
            to = str(clause.get("to") or "")
            from_side = _side_for_nation(war_instance, frm) if frm else None
            to_side = _side_for_nation(war_instance, to) if to else None
            if from_side is None or to_side is None or from_side == to_side:
                return {
                    "valid": False,
                    "error": "clause_side_mismatch",
                    "error_index": idx,
                    "disabled_reason_display": _error_display("clause_side_mismatch"),
                }

    # SC-33 / G2-Slice-9: per-clause amount + duration bounds for
    # `gold_per_turn` clauses (no silent clamping — submitted values are
    # rejected with humanized copy if out of range).
    for idx, clause in enumerate(terms):
        if clause.get("type") != "gold_per_turn":
            continue
        amount = int(clause.get("amount", 0) or 0)
        turns = int(clause.get("turns", 0) or 0)
        if amount < GOLD_PER_TURN_MIN_AMOUNT:
            return {
                "valid": False,
                "error": "gold_per_turn_amount_too_small",
                "error_index": idx,
                "disabled_reason_display": _error_display(
                    "gold_per_turn_amount_too_small"
                ),
            }
        if turns < GOLD_PER_TURN_MIN_TURNS or turns > GOLD_PER_TURN_MAX_TURNS:
            return {
                "valid": False,
                "error": "gold_per_turn_duration_out_of_range",
                "error_index": idx,
                "disabled_reason_display": _error_display(
                    "gold_per_turn_duration_out_of_range"
                ),
            }

    # SC-33 / G2-Slice-9: projected-solvency budget conflict. Combines all
    # lump-sum + recurring gold obligations the same payer is committing
    # to in this draft, plus their existing recurring settlement
    # obligations, against `current_gold + max(0, expected_net_income) *
    # max_turns_in_submitted_terms`. Rejects when the combined obligation
    # exceeds capacity. Skipped when `world` is unavailable (legacy
    # schema-only callers).
    if world is not None and enforce_solvency:
        conflict = _check_gold_payment_budget_conflict(world, terms)
        if conflict is not None:
            return conflict

    # SC-31 / G2-Slice-8: dependency-clause eligibility uses world state.
    # When called without a `world`+`war_instance` context (legacy callers
    # / pure schema validation), the dependency-state checks are skipped.
    if world is not None and isinstance(war_instance, Mapping):
        for idx, clause in enumerate(terms):
            ctype = clause.get("type")
            if ctype in ("vassalage", "subjugation"):
                # Canonical direction: from = vassal/subjugated, to = lord.
                vassal_nation = str(clause.get("from") or "")
                lord_nation = str(clause.get("to") or "")
                if not vassal_nation or not lord_nation or vassal_nation == lord_nation:
                    return {
                        "valid": False,
                        "error": "dependency_direction_invalid",
                        "error_index": idx,
                        "disabled_reason_display": _error_display(
                            "dependency_direction_invalid"
                        ),
                    }
                eligibility = (
                    evaluate_subjugation_eligibility
                    if ctype == "subjugation"
                    else evaluate_vassalage_eligibility
                )(
                    world,
                    war_instance=war_instance,
                    lord_nation=lord_nation,
                    target_nation=vassal_nation,
                )
                if not eligibility.get("eligible"):
                    return {
                        "valid": False,
                        "error": str(eligibility.get("refusal_code") or "dependency_invalid"),
                        "error_index": idx,
                        "disabled_reason_display": eligibility.get("disabled_reason_display")
                        or _error_display(
                            str(eligibility.get("refusal_code") or "dependency_invalid")
                        ),
                    }
            elif ctype == "liberation":
                vassal_nation = str(clause.get("vassal_nation") or "")
                lord_nation = str(clause.get("lord_nation") or "")
                liberator = str(clause.get("liberator") or "")
                eligibility = evaluate_liberation_eligibility(
                    world,
                    war_instance=war_instance,
                    vassal_nation=vassal_nation,
                    lord_nation=lord_nation,
                    liberator=liberator,
                )
                if not eligibility.get("eligible"):
                    return {
                        "valid": False,
                        "error": str(eligibility.get("refusal_code") or "liberation_invalid"),
                        "error_index": idx,
                        "disabled_reason_display": eligibility.get("disabled_reason_display")
                        or _error_display(
                            str(eligibility.get("refusal_code") or "liberation_invalid")
                        ),
                    }
    return {"valid": True}


# SC-5R-1 pre-ratification clause-type guard allowlist for legacy aliases
# the apply path still tolerates (`gold_lump` is a pre-cleanup alias for
# `gold_indemnity` recognized by `_apply_settlement_terms` at line ~3877).
# Cut clause types (e.g. clause types removed by a SC-32 / D-series
# product decision) do not appear here and are rejected by the guard.
RATIFY_LEGACY_APPLY_CLAUSE_TYPES = frozenset({"gold_lump"})
