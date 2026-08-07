"""Settlement baseline generation and acceptance computation (CH-1 split, layer 2).

Concession/demand baseline generation (compute_settlement_baseline — the ONE
baseline generator since CH-4 deleted the legacy single-court author; the
losing-side payload adapter is compute_concession_baseline_payload),
surrender/recurring-gold presets, treasury line, guided candidate prefills,
per-court direction, and compute_per_court_acceptance. Split from
settlement_preview.py (CH-1); may import settlement_routes /
settlement_validation.
"""

from __future__ import annotations

from backend.display_names import (
    acceptance_band_display,
    acceptance_band_phrase,
    acceptance_component_display,
)
from backend.game_logic.diplomatic_templates import (
    calculate_raw_treaty_harshness,
    resolve_settlement_voice_line,
)
from backend.game_logic import settlement_scoring
from backend.game_logic.settlement_scoring import (
    ACCEPTANCE_THRESHOLD,
    GOLD_PER_TURN_MAX_TURNS,
    GOLD_PER_TURN_MIN_AMOUNT,
    GOLD_PER_TURN_MIN_TURNS,
    HARD_STOP_NO_DIRECT_WAR_SCORE,
    MAX_SETTLEMENT_CLAUSE_COUNT,
    NEAR_ACCEPTANCE_FLOOR,
    SETTLEMENT_LIVE_CLAUSE_TYPES,
    # NOTE: calculate_common_peace_acceptance is deliberately NOT imported by
    # name — every call must resolve late via the settlement_scoring module
    # attribute so test patches at the scorer seam land (audit 2026-07-09).
    compute_direct_scores_by_enemy,
    compute_settlement_package_raw_harshness,
    compute_side_pressure_score,
    project_balance_after_settlement,
    select_direct_score,
)
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
)
from backend.game_logic.settlement_validation import (
    LOSING_SIDE_PRESSURE_THRESHOLD,
    _clause_touches_court,
    _estimate_payer_net_income_per_turn,
    evaluate_subjugation_eligibility,
    evaluate_vassalage_eligibility,
    validate_settlement_terms,
)


def _enrich_acceptance_display(acceptance: Mapping[str, Any]) -> Dict[str, Any]:
    enriched = dict(acceptance or {})
    band = str(enriched.get("band") or enriched.get("verdict") or "")
    enriched["band"] = band
    enriched["band_display"] = acceptance_band_display(band)
    enriched["band_phrase"] = acceptance_band_phrase(band)
    top_components = []
    for item in enriched.get("feedback") or []:
        if not isinstance(item, Mapping):
            continue
        component = str(item.get("component") or "")
        value = item.get("value")
        top_components.append({
            **dict(item),
            "component_display": acceptance_component_display(component),
            "value_display": f"{int(value):+d}" if isinstance(value, (int, float)) else str(value or ""),
        })
    enriched["top_components"] = top_components[:3]
    if top_components:
        enriched["top_blocker_display"] = top_components[0]["component_display"]
        enriched["top_blocker_value_display"] = top_components[0]["value_display"]
        # CA8-17 (close-out gate 10.3): the raw component KEY rides beside
        # the label so the table voice can speak it instead of quoting it.
        enriched["top_blocker_component"] = str(
            top_components[0].get("component") or "")
    return enriched


CONCESSION_BASELINE_TREASURY_RESERVE = 500


CONCESSION_BASELINE_GOLD_HARD_CAP = 1500


CONCESSION_BASELINE_GOLD_FLOOR = 300


# EC-W4 "Peace with Teeth" (memo ECON_WAR_COUPLING_RESEARCH_2026_07_17 §3):
# a demanded indemnity scales with the paying court's purse instead of the
# flat 300g floor — a rich loser can finally be dunned at all. Still
# capacity-capped by `court_balance - RESERVE` and self-limited by the
# `_stays_acceptable` gate, so the ask never exceeds what the court would
# actually sign. Sweep-tunable.
CONCESSION_BASELINE_TREASURY_FRACTION = 0.25


CONCESSION_BASELINE_BFS_MAX_DEPTH = 6


# Re-front Slice 1: a strong-lead threshold for authoring a TERRITORY demand,
# mirroring `generate_suggested_terms`' bilateral demand stage (which demands a
# border region at `war_score > 30`). Below this but above the direction margin
# the baseline demands gold only (a lighter ask); inside the margin it is a
# neutral peace.
DEMAND_TERRITORY_DIRECT_SCORE = 30


# Re-front Slice 1 / spec §8 OQ#5: per-court baseline DIRECTION dead-band.
# This thresholds a single court's raw `direct_score` (the int half of
# `select_direct_score(direct_scores[court])`, on the [-100, 100] war-score
# scale) to choose demand vs concede vs neutral-peace. It is deliberately a
# DISTINCT constant from `LOSING_SIDE_PRESSURE_THRESHOLD`: that one thresholds
# the power-weighted *side-pressure* scalar (a different scale/quantity), and
# reusing it here would re-introduce the scale conflation the spec's pressure
# model note exists to prevent. France clearly leads a court at
# `direct_score > +MARGIN` (demand), is clearly pressured by it at
# `direct_score < -MARGIN` (concede), and is in a neutral dead-band in between
# (white-peace floor).
DIRECT_SCORE_DIRECTION_MARGIN = 10


# Re-front Slice 2 / spec §11.3 + OQ#7: Tier-2 intent dials adjust MAGNITUDE at
# the court level (harsher = press the court / larger demands + smaller
# concessions; generous = ease the court / smaller demands + larger
# concessions). Each click steps gold by this amount and adds/removes whole
# clauses by COUNT — it NEVER swaps the requested region or payer IDENTITY (that
# is a Tier-3 request). Gold magnitude is bounded by the same hard cap the
# concession baseline uses so a runaway dial cannot author an absurd indemnity.
SETTLEMENT_DIAL_GOLD_STEP = 100


# Slice H D-H1 (approved July 3, 2026): clause provenances the dial sweep
# treats as protected — never silently dropped, gold shrinks only to the
# step floor. `player` = hand-authored guided verbs; `ally_petition` =
# clauses granted from a Slice H ally petition (un-rewarding an ally must
# take a deliberate per-row Remove, which re-opens the petition surface
# after its cooldown).
SETTLEMENT_DIAL_PROTECTED_AUTHORS = frozenset({"player", "ally_petition"})


def _concession_baseline_payer_balance(world: Any, nation: str) -> int:
    """Return the payer nation's available gold balance (int)."""
    gold_map = getattr(world, "nation_gold", None)
    if isinstance(gold_map, Mapping):
        try:
            return int(gold_map.get(nation, 0) or 0)
        except (TypeError, ValueError):
            return 0
    return 0


def _proposer_paid_gold_committed(
    settlement_terms: Iterable[Mapping[str, Any]],
    proposer_side_leader: str,
) -> int:
    """Total gold the proposer leader pays across the staged package —
    lump indemnities at face value, recurring obligations at
    ``amount × turns`` (the same total-obligation basis the solvency
    check projects)."""
    leader = str(proposer_side_leader or "")
    if not leader:
        return 0
    committed = 0
    for term in settlement_terms or []:
        if not isinstance(term, Mapping):
            continue
        if str(term.get("from") or "") != leader:
            continue
        ttype = str(term.get("type") or "")
        try:
            amount = int(term.get("amount", 0) or 0)
        except (TypeError, ValueError):
            amount = 0
        if amount <= 0:
            continue
        if ttype in ("gold_indemnity", "gold_lump"):
            committed += amount
        elif ttype == "gold_per_turn":
            try:
                turns = int(term.get("turns", 0) or 0)
            except (TypeError, ValueError):
                turns = 0
            committed += amount * max(0, turns)
    return int(committed)


def compute_settlement_treasury_line(
    world: Any,
    *,
    proposer_side_leader: str,
    settlement_terms: Iterable[Mapping[str, Any]],
) -> Dict[str, int]:
    """Guided Terms §3.4 (GT-A1) — ONE treasury, many courts.

    Multiple courts can take the proposer's gold but the treasury is one
    pool: two individually-affordable offers can jointly overdraw it and
    die at the table-level solvency check (`gold_payment_budget_conflict`).
    This block makes the shared budget visible while authoring, so the
    guided flow never re-creates that over-commit with the player driving.

    Returns ``{"treasury", "committed", "reserve", "remaining"}`` — all
    ``int()`` (Golden Rule #2):

    - ``treasury`` — the proposer leader's current gold balance;
    - ``committed`` — gold the leader pays across the staged package
      (lump at face value, recurring at ``amount × turns``);
    - ``reserve`` — the concession-baseline hold-back, shrunk to what is
      actually left after commitments (``min(RESERVE, treasury −
      committed)``, floored at 0 — a fully-committed treasury shows
      ``reserve 0 / remaining 0``, per the spec's probe example);
    - ``remaining`` — what suggestion defaults may still spend:
      ``max(0, treasury − committed − reserve)``.
    """
    treasury = _concession_baseline_payer_balance(world, str(proposer_side_leader or ""))
    committed = _proposer_paid_gold_committed(settlement_terms, proposer_side_leader)
    reserve = min(
        CONCESSION_BASELINE_TREASURY_RESERVE, max(0, treasury - committed)
    )
    remaining = max(0, treasury - committed - reserve)
    return {
        "treasury": int(treasury),
        "committed": int(committed),
        "reserve": int(reserve),
        "remaining": int(remaining),
    }


def _promised_regions_in_terms(
    settlement_terms: Iterable[Mapping[str, Any]],
) -> Set[str]:
    """Regions already promised by ANY ``territory_cede`` clause in the
    staged package (V1 is table-scoped: one region, one clause —
    regardless of which court the clause touches)."""
    promised: Set[str] = set()
    for term in settlement_terms or []:
        if not isinstance(term, Mapping):
            continue
        if str(term.get("type") or "") != "territory_cede":
            continue
        region = str(term.get("region") or "")
        if region:
            promised.add(region)
    return promised


def _guided_gold_offer_default(
    world: Any,
    *,
    proposer_side_leader: str,
    settlement_terms: Iterable[Mapping[str, Any]],
) -> int:
    """Guided Terms §3.4 — the default magnitude for a France-pays gold
    offer authored from a court row, capped at the TABLE-scoped
    ``remaining`` budget (never the row-local balance). 0 means the
    treasury has nothing left to offer (the add verb rejects cleanly)."""
    line = compute_settlement_treasury_line(
        world,
        proposer_side_leader=proposer_side_leader,
        settlement_terms=settlement_terms,
    )
    return int(min(CONCESSION_BASELINE_GOLD_FLOOR, line["remaining"]))


def _guided_region_offer_candidate(
    world: Any,
    *,
    court: str,
    proposer_side_participants: Iterable[str],
    settlement_terms: Iterable[Mapping[str, Any]],
) -> str:
    """Guided Terms §3.4 — the default region for a France-cedes offer on a
    court row: the settlement concede-side selector with the staged
    package's promised regions excluded (table-scoped V1, the same
    exclusion PF-1 threads through the baseline loop). Empty string when
    nothing transferable remains."""
    region = _concession_baseline_select_transferable_region(
        world,
        proposer_side_participants=proposer_side_participants,
        accepting_leader=str(court or ""),
        excluded_regions=_promised_regions_in_terms(settlement_terms),
    )
    return str(region or "")


# Guided Terms §4 — the `gold_per_turn` PRE-FILL horizon. The live recurring
# preset (`_compute_recurring_gold_preset`) drafts 3 turns by default; the
# guided suggestion uses the same opening horizon, clamped to the validator
# bounds.
_GOLD_PER_TURN_PREFILL_TURNS = 3


def _payer_net_income_estimate(world: Any, payer: str) -> int:
    """Per-turn net income estimate via the CACHED ``get_nation_regions``
    lookup (Golden Rule #8 — the validator's `_estimate_payer_net_income_per_turn`
    scans every region, which is fine once per restage but not per court per
    suggestion build). Same semantics: sum of `get_effective_income()` over
    the payer's controlled regions, clamped at 0. Falls back to the
    full-scan estimator for thin world stubs without the cached helper.
    """
    regions = getattr(world, "regions", None) or {}
    names: Optional[List[str]] = None
    if hasattr(world, "get_nation_regions"):
        try:
            names = list(world.get_nation_regions(payer))
        except Exception:
            names = None
    if names is None:
        return _estimate_payer_net_income_per_turn(world, payer)
    income = 0
    for name in names:
        region = regions.get(name) if isinstance(regions, Mapping) else None
        if region is None:
            continue
        try:
            income += int(region.get_effective_income())
        except Exception:
            continue
    return max(0, int(income))


def _gold_per_turn_prefill(
    world: Any,
    *,
    payer: str,
    settlement_terms: Iterable[Mapping[str, Any]],
    income_per_turn: int,
    cap_total: Optional[int] = None,
) -> Optional[Dict[str, int]]:
    """Guided Terms §4 — the capacity-bounded ``gold_per_turn`` pre-fill.

    Capacity rule (mirrors `_check_gold_payment_budget_conflict`):
    ``capacity = current_gold + max(0, net_income) × turns``, NET of the
    payer's existing `recurring_settlement_payments` obligations AND the
    gold the payer already owes inside the staged package (lump at face
    value, recurring at amount × turns). Conservative by construction: the
    horizon is the pre-fill's own ``turns`` (the validator widens capacity
    to the longest recurring clause in the package, so a pre-fill that fits
    this tighter bound always validates).

    The rate caps at `SETTLEMENT_DIAL_GOLD_STEP` (the live per-click gold
    step — a sane opening rate, never an absurd auto-drafted tribute) and
    must clear `GOLD_PER_TURN_MIN_AMOUNT`; ``cap_total`` (the §3.4 shared-
    treasury ``remaining``, for France-paid offers) bounds the TOTAL
    obligation. Returns ``{"amount", "turns"}`` (both int) or ``None`` when
    no valid pre-fill exists — the suggestion is then simply not offered
    (valid-by-construction: ineligible options never render).
    """
    payer = str(payer or "")
    if not payer:
        return None
    turns = max(
        GOLD_PER_TURN_MIN_TURNS,
        min(GOLD_PER_TURN_MAX_TURNS, _GOLD_PER_TURN_PREFILL_TURNS),
    )
    current_gold = _concession_baseline_payer_balance(world, payer)
    capacity = current_gold + max(0, int(income_per_turn)) * turns
    existing = 0
    for entry in getattr(world, "recurring_settlement_payments", None) or []:
        if not isinstance(entry, Mapping):
            continue
        if str(entry.get("from") or "") != payer:
            continue
        existing += int(entry.get("amount_per_turn", 0) or 0) * int(
            entry.get("turns_remaining", 0) or 0
        )
    staged = 0
    for term in settlement_terms or []:
        if not isinstance(term, Mapping):
            continue
        if str(term.get("from") or "") != payer:
            continue
        ttype = str(term.get("type") or "")
        amount = int(term.get("amount", 0) or 0)
        if amount <= 0:
            continue
        if ttype in ("gold_indemnity", "gold_lump"):
            staged += amount
        elif ttype == "gold_per_turn":
            staged += amount * max(0, int(term.get("turns", 0) or 0))
    budget = capacity - existing - staged
    if cap_total is not None:
        budget = min(budget, int(cap_total))
    rate = min(int(SETTLEMENT_DIAL_GOLD_STEP), budget // turns)
    if rate < GOLD_PER_TURN_MIN_AMOUNT:
        return None
    return {"amount": int(rate), "turns": int(turns)}


def _concession_baseline_bfs_distance(
    world: Any,
    *,
    origin_region: str,
    target_region: str,
    max_depth: int = CONCESSION_BASELINE_BFS_MAX_DEPTH,
) -> Optional[int]:
    """Bounded BFS over `region.adjacent_regions` for capital-distance sort.

    Returns the shortest hop count from `origin_region` to `target_region`,
    or None when the target is unreachable inside `max_depth`. Spec §"Concession
    And Treaty Conversation Contract" line 284: regions unreachable inside the
    bound fall through to the lower priority sort keys rather than being
    excluded.
    """
    if not origin_region or not target_region:
        return None
    if origin_region == target_region:
        return 0
    regions = getattr(world, "regions", None)
    if not isinstance(regions, Mapping):
        return None
    if origin_region not in regions or target_region not in regions:
        return None
    visited = {origin_region}
    frontier = [origin_region]
    for depth in range(1, max_depth + 1):
        next_frontier: List[str] = []
        for current in frontier:
            region = regions.get(current)
            adjacent = (
                getattr(region, "adjacent_regions", None) or []
                if region is not None
                else []
            )
            for neighbour in adjacent:
                if neighbour in visited:
                    continue
                if neighbour == target_region:
                    return depth
                visited.add(neighbour)
                next_frontier.append(neighbour)
        frontier = next_frontier
        if not frontier:
            break
    return None


def _concession_baseline_transferable_candidates(
    world: Any,
    *,
    proposer_side_participants: Iterable[str],
    accepting_leader: str,
    excluded_regions: Optional[Iterable[str]] = None,
) -> List[str]:
    """Ranked list of concession-region candidates per the spec algorithm.

    Sort key: (BFS distance from the accepting leader's world-scoped capital
    (`world.get_nation_capital`) when
    reachable inside `CONCESSION_BASELINE_BFS_MAX_DEPTH`, else a sentinel
    above all real depths), then economic income value (low first), then
    region name. Eligible regions are currently controlled by a proposer-side
    participant, not a capital, and not the historical home of any proposer-
    side participant (so a captured rival region returns to the accepting
    leader rather than the proposer ceding home territory).

    ``excluded_regions`` (PF-1 / D1): regions already promised to another
    covered court in the same generated package are ineligible, so a
    multi-court concession baseline can never double-promise one region
    (V1 ``region_double_promised``).

    Guided Terms §8 OQ-1: the per-court rows render the FULL valid set as
    a dropdown, so this returns the whole ranked pool; the single-pick
    selector below takes the head.

    Historical home lookup goes through the world's own starting-controller
    map (`world._starting_controllers`, legacy helper as fallback) because
    the Region instance carries the live `controller` field only — it does
    not retain the starting controller after init.
    """
    proposer_set = {str(n) for n in proposer_side_participants if n}
    if not proposer_set:
        return []
    from backend.models.region import get_starting_controllers

    # World-scoped capital + starting map (1805 pre-slice item 7 family): the
    # legacy globals miss Europe courts/provinces, degrading the BFS anchor
    # and the historical-home exclusion. Attribute-fallback idiom because
    # scorer tests drive this with shim worlds lacking the accessor.
    from backend.models.region import NATION_CAPITALS
    _capitals = getattr(world, "nation_capitals", None) or NATION_CAPITALS
    target_region = _capitals.get(accepting_leader)
    regions = getattr(world, "regions", None)
    if not isinstance(regions, Mapping):
        return []
    starting_controllers = (
        getattr(world, "_starting_controllers", None) or get_starting_controllers()
    )

    # Golden Rule 8: iterate per-participant via the cached
    # `world.get_nation_regions(...)` lookup and union the results
    # rather than scanning every region in the world. The pattern
    # mirrors `settlement_scoring._project_balance_after_settlement`
    # line 1589 and scales to the 1805 Europe map.
    candidate_names: set[str] = set()
    if hasattr(world, "get_nation_regions"):
        for participant in proposer_set:
            try:
                candidate_names.update(world.get_nation_regions(participant))
            except Exception:
                continue
    else:
        # Defensive fallback for tests that build a thin world stub
        # without the cached lookup helper. Behaviour matches the
        # original full scan.
        for name, region in regions.items():
            if str(getattr(region, "controller", "") or "") in proposer_set:
                candidate_names.add(name)

    excluded = {str(r) for r in (excluded_regions or []) if r}
    candidates: List[Tuple[int, int, str]] = []
    unreachable_sentinel = CONCESSION_BASELINE_BFS_MAX_DEPTH + 1
    for name in candidate_names:
        if str(name) in excluded:
            continue
        region = regions.get(name)
        if region is None:
            continue
        if bool(getattr(region, "is_capital", False)):
            continue
        starting = str(starting_controllers.get(name, "") or "")
        if starting in proposer_set:
            continue
        distance = (
            _concession_baseline_bfs_distance(
                world,
                origin_region=str(target_region or ""),
                target_region=str(name),
            )
            if target_region
            else None
        )
        if distance is None:
            distance = unreachable_sentinel
        income_value = int(getattr(region, "income_value", 100) or 100)
        candidates.append((distance, income_value, str(name)))
    candidates.sort()
    return [name for _, _, name in candidates]


def _concession_baseline_select_transferable_region(
    world: Any,
    *,
    proposer_side_participants: Iterable[str],
    accepting_leader: str,
    excluded_regions: Optional[Iterable[str]] = None,
) -> Optional[str]:
    """Pick the deterministic concession region — the head of the ranked
    candidate pool (see `_concession_baseline_transferable_candidates`)."""
    candidates = _concession_baseline_transferable_candidates(
        world,
        proposer_side_participants=proposer_side_participants,
        accepting_leader=accepting_leader,
        excluded_regions=excluded_regions,
    )
    return candidates[0] if candidates else None


def _join_reasoning_phrases(phrases: List[str]) -> str:
    if len(phrases) <= 1:
        return phrases[0] if phrases else ""
    if len(phrases) == 2:
        return " and ".join(phrases)
    return ", ".join(phrases[:-1]) + ", and " + phrases[-1]


def _format_concession_reasoning(
    *,
    proposer_leader: str,
    terms: Iterable[Mapping[str, Any]],
) -> str:
    """Humanized one-line rationale for the baseline draft.

    May 24, 2026 audit punch list Tier 2: the final reasoning string
    routes through `settlement_concession_authored_talleyrand` (Voice
    Bible §16.1) instead of returning a hard-coded f-string. CH-4: the
    summary is built from the authored material clauses themselves (the
    per-court ``compute_settlement_baseline`` output), so one formatter
    covers the single-court degenerate case ("France would pay Britain
    500 gold") and the multi-court split, including demand-direction
    slices on courts France leads.
    """
    phrases: List[str] = []
    counterparts: List[str] = []

    def _note_counterpart(nation: Any) -> None:
        name = str(nation or "")
        if name and name != proposer_leader and name not in counterparts:
            counterparts.append(name)

    for term in terms or []:
        if not isinstance(term, Mapping):
            continue
        ttype = str(term.get("type") or "")
        if ttype == "peace":
            continue
        payer = str(term.get("from") or "")
        payee = str(term.get("to") or "")
        if ttype == "gold_indemnity":
            amount = int(term.get("amount", 0) or 0)
            if payer == proposer_leader:
                phrases.append(f"pay {payee} {amount} gold")
                _note_counterpart(payee)
            else:
                phrases.append(f"take {amount} gold of {payer}")
                _note_counterpart(payer)
        elif ttype == "gold_per_turn":
            amount = int(term.get("amount", 0) or 0)
            turns = int(term.get("turns", 0) or 0)
            if payer == proposer_leader:
                phrases.append(f"pay {payee} {amount} gold a turn for {turns} turns")
                _note_counterpart(payee)
            else:
                phrases.append(
                    f"take {amount} gold a turn for {turns} turns of {payer}"
                )
                _note_counterpart(payer)
        elif ttype == "territory_cede":
            region = str(term.get("region") or "")
            if payer == proposer_leader:
                phrases.append(f"cede {region} to {payee}")
                _note_counterpart(payee)
            else:
                phrases.append(f"take {region} from {payer}")
                _note_counterpart(payer)
        else:
            label = ttype.replace("_", " ")
            phrases.append(f"settle {label} with {payer or payee}")
            _note_counterpart(payer or payee)
    if not phrases:
        return ""
    summary = f"{proposer_leader} would " + _join_reasoning_phrases(phrases)
    accepting_label = _join_reasoning_phrases(counterparts) or "the covered courts"
    return resolve_settlement_voice_line(
        "settlement_concession_authored_talleyrand",
        summary=summary,
        accepting_leader=accepting_label,
    ) or ("Talleyrand's draft: " + summary + " to improve acceptance.")


# SC-31 / G2-Slice-8 - Dependency clause eligibility helpers.
#
# These helpers are the source of truth for whether a vassalage /
# subjugation / liberation clause can be authored. They are reused by
# the POST preview validator, the surrender-preset algorithm, and by
# the SC-31 behavior tests so a single closed taxonomy of refusal codes
# governs both editor visibility and submit-time rejection.


def _compute_surrender_preset(
    world: Any,
    *,
    war_id: str,
    war_instance: Mapping[str, Any],
    proposer_side: str,
    accepting_side: str,
    accepting_leader: str,
    proposer_side_leader: Optional[str],
    covered_enemy_participants: Iterable[str],
    side_pressure_score: Optional[int],
) -> Dict[str, Any]:
    """SC-31 / G2-Slice-8 surrender-preset algorithm.

    Deterministic ``[peace, dependency]`` preset where ``dependency`` is
    the harshest legal clause in the order
    ``subjugation -> vassalage`` against the accepting leader. The
    accepting leader is the prospective lord because surrender is the
    losing-side player handing dependency authority to the winning
    leader. Liberation is never authored by this preset (it is owned by
    the editor's standalone liberation control).

    Visibility reuses the concession-baseline losing-side predicate
    (``side_pressure_score <= LOSING_SIDE_PRESSURE_THRESHOLD``) AND
    requires at least one material dependency to be legal under the
    accepting leader's power cap. When the predicate passes but no
    legal dependency clause can be authored — the most common cause
    being the accepting leader being too small under POWER_CAP_RATIO —
    the affordance is hidden, not disabled, per the Disabled vs Hidden
    Affordance Policy at spec §"Disabled vs Hidden Affordance Policy".

    Result shape:

    - ``{"losing_for_surrender_preset": bool,
        "surrender_preset_visible": bool,
        "surrender_preset": {"terms": List[Clause], "reasoning": str,
                              "dependency_kind": str} | None,
        "surrender_preset_reason": str}``
    """
    if side_pressure_score is None:
        return {
            "losing_for_surrender_preset": False,
            "surrender_preset_visible": False,
            "surrender_preset": None,
            "surrender_preset_reason": "no_side_pressure_score",
        }
    losing = int(side_pressure_score) <= LOSING_SIDE_PRESSURE_THRESHOLD
    if not losing:
        return {
            "losing_for_surrender_preset": False,
            "surrender_preset_visible": False,
            "surrender_preset": None,
            "surrender_preset_reason": "not_losing_side",
        }
    if not proposer_side_leader or not accepting_leader:
        return {
            "losing_for_surrender_preset": True,
            "surrender_preset_visible": False,
            "surrender_preset": None,
            "surrender_preset_reason": "missing_leaders",
        }
    covered = {str(n) for n in (covered_enemy_participants or []) if n}
    if accepting_leader not in covered:
        # Spec line 277 requires clause targets to lie in
        # `covered_enemy_participants`; if the accepting leader is not
        # covered, dependency cannot legally beneficiary-route.
        return {
            "losing_for_surrender_preset": True,
            "surrender_preset_visible": False,
            "surrender_preset": None,
            "surrender_preset_reason": "accepting_leader_not_covered",
        }
    subjugation = evaluate_subjugation_eligibility(
        world,
        war_instance=war_instance,
        lord_nation=accepting_leader,
        target_nation=proposer_side_leader,
    )
    dependency_kind: Optional[str] = None
    if subjugation.get("eligible"):
        dependency_kind = "subjugation"
    else:
        vassalage = evaluate_vassalage_eligibility(
            world,
            war_instance=war_instance,
            lord_nation=accepting_leader,
            target_nation=proposer_side_leader,
        )
        if vassalage.get("eligible"):
            dependency_kind = "vassalage"
    if not dependency_kind:
        return {
            "losing_for_surrender_preset": True,
            "surrender_preset_visible": False,
            "surrender_preset": None,
            "surrender_preset_reason": "no_legal_dependency_clause",
        }
    preset_terms: List[Dict[str, Any]] = [
        {"type": "peace"},
        {
            "type": dependency_kind,
            "from": proposer_side_leader,
            "to": accepting_leader,
        },
    ]
    vassal_kind = "conquest vassal" if dependency_kind == "subjugation" else "treaty vassal"
    # May 24, 2026 audit punch list Tier 2: route the surrender preset
    # reasoning through `settlement_surrender_preset_authored_talleyrand`
    # (Voice Bible §16.1) instead of the prior hard-coded f-string. The
    # template ships the deliberate-surrender framing; the inline string
    # remains as the fallback when the template is missing/disabled.
    reasoning = resolve_settlement_voice_line(
        "settlement_surrender_preset_authored_talleyrand",
        war_label=str(war_id or "this war"),
        vassal_kind=vassal_kind,
        proposer_leader=str(proposer_side_leader),
        accepting_leader=str(accepting_leader),
    ) or (
        f"Talleyrand's draft: {proposer_side_leader} submits to {accepting_leader} "
        f"as a {vassal_kind} in exchange for ending the war."
    )
    return {
        "losing_for_surrender_preset": True,
        "surrender_preset_visible": True,
        "surrender_preset": {
            "terms": preset_terms,
            "reasoning": reasoning,
            "dependency_kind": dependency_kind,
        },
        "surrender_preset_reason": "material_dependency_available",
    }


def _compute_recurring_gold_preset(
    world: Any,
    *,
    war_instance: Mapping[str, Any],
    proposer_side_leader: Optional[str],
    accepting_leader: str,
    covered_enemy_participants: Iterable[str],
    side_pressure_score: Optional[int],
) -> Dict[str, Any]:
    """SC-33 / G2-Slice-9 recurring-gold draft for the settlement popup.

    The action exposes payer, recipient, amount, and duration in the
    staged payload and authors a legal finite `gold_per_turn` draft using
    the fixture-provided smoke values when present and otherwise the
    SC-33 validator minimums.
    """
    if "gold_per_turn" not in SETTLEMENT_LIVE_CLAUSE_TYPES:
        return {
            "losing_for_recurring_gold_preset": False,
            "recurring_gold_preset_visible": False,
            "recurring_gold_preset": None,
            "recurring_gold_preset_reason": "gold_per_turn_not_live",
        }
    if side_pressure_score is None:
        return {
            "losing_for_recurring_gold_preset": False,
            "recurring_gold_preset_visible": False,
            "recurring_gold_preset": None,
            "recurring_gold_preset_reason": "no_side_pressure_score",
        }
    losing = int(side_pressure_score) <= LOSING_SIDE_PRESSURE_THRESHOLD
    if not losing:
        return {
            "losing_for_recurring_gold_preset": False,
            "recurring_gold_preset_visible": False,
            "recurring_gold_preset": None,
            "recurring_gold_preset_reason": "not_losing_side",
        }
    if not proposer_side_leader or not accepting_leader:
        return {
            "losing_for_recurring_gold_preset": True,
            "recurring_gold_preset_visible": False,
            "recurring_gold_preset": None,
            "recurring_gold_preset_reason": "missing_leaders",
        }
    covered = {str(n) for n in (covered_enemy_participants or []) if n}
    if accepting_leader not in covered:
        return {
            "losing_for_recurring_gold_preset": True,
            "recurring_gold_preset_visible": False,
            "recurring_gold_preset": None,
            "recurring_gold_preset_reason": "accepting_leader_not_covered",
        }

    fixture = getattr(world, "settlement_smoke_fixture", None)
    fixture_meta = fixture if isinstance(fixture, Mapping) else {}

    def _bounded_int(raw: Any, default: int, *, low: int, high: int) -> int:
        try:
            value = int(raw)
        except (TypeError, ValueError):
            value = int(default)
        return max(low, min(high, value))

    amount = _bounded_int(
        fixture_meta.get("expected_recurring_amount_min"),
        GOLD_PER_TURN_MIN_AMOUNT,
        low=GOLD_PER_TURN_MIN_AMOUNT,
        high=10_000,
    )
    turns = _bounded_int(
        fixture_meta.get("expected_recurring_turns_min"),
        3,
        low=GOLD_PER_TURN_MIN_TURNS,
        high=GOLD_PER_TURN_MAX_TURNS,
    )
    preset_terms: List[Dict[str, Any]] = [
        {"type": "peace"},
        {
            "type": "gold_per_turn",
            "from": str(proposer_side_leader),
            "to": str(accepting_leader),
            "amount": int(amount),
            "turns": int(turns),
        },
    ]
    validation = validate_settlement_terms(
        preset_terms,
        world=world,
        war_instance=war_instance,
    )
    if not validation.get("valid"):
        return {
            "losing_for_recurring_gold_preset": True,
            "recurring_gold_preset_visible": False,
            "recurring_gold_preset": None,
            "recurring_gold_preset_reason": str(
                validation.get("error") or "recurring_gold_preset_invalid"
            ),
        }
    # May 24, 2026 audit punch list Tier 2: route the recurring-gold
    # preset reasoning through `settlement_recurring_gold_authored_talleyrand`
    # (Voice Bible §16.1) instead of the prior hard-coded f-string. The
    # template ships the projected-total framing ("ties the treasury for
    # years") that the f-string omitted.
    projected_total = int(amount) * int(turns)
    reasoning = resolve_settlement_voice_line(
        "settlement_recurring_gold_authored_talleyrand",
        payer=str(proposer_side_leader),
        amount_per_turn=str(int(amount)),
        recipient=str(accepting_leader),
        turns=str(int(turns)),
        projected_total=str(projected_total),
    ) or (
        f"Talleyrand's draft: {proposer_side_leader} would pay {accepting_leader} "
        f"{amount} gold per turn for {turns} turns ({projected_total} gold in total)."
    )
    return {
        "losing_for_recurring_gold_preset": True,
        "recurring_gold_preset_visible": True,
        "recurring_gold_preset": {
            "terms": preset_terms,
            "reasoning": reasoning,
            "amount": int(amount),
            "turns": int(turns),
            "payer": str(proposer_side_leader),
            "recipient": str(accepting_leader),
        },
        "recurring_gold_preset_reason": "finite_recurring_gold_available",
    }


def compute_concession_baseline_payload(
    world: Any,
    *,
    war_id: str,
    war_instance: Mapping[str, Any],
    proposer_side: str,
    accepting_side: str,
    proposer_side_leader: Optional[str],
    covered_enemy_participants: Iterable[str],
    side_pressure_score: Optional[int],
    near_acceptance_floor: int = NEAR_ACCEPTANCE_FLOOR,
) -> Dict[str, Any]:
    """Return the deterministic losing-side concession baseline payload.

    Result shape (the G2-Slice-W1 presentation contract, unchanged):

    - ``{"losing_for_concession_baseline": bool, "concession_baseline_visible":
      bool, "concession_baseline": {"terms": List[Clause], "reasoning": str} |
      None, "concession_baseline_reason": str}``

    CH-4 (Gate-4 pre-flight audit §9): the legacy single-court authoring
    path is deleted — the terms come from ``compute_settlement_baseline``,
    the SAME per-court generator the PROPOSE front door mounts, so the
    "Re-author with concessions" rail seeds exactly the baseline the front
    door would author (n=1 is the degenerate case the re-front spec
    promises; the cross-court treasury split and promised-region threading
    are PF-1's, for free). Visibility keeps the package-level losing gate
    (``side_pressure_score <= LOSING_SIDE_PRESSURE_THRESHOLD``) in
    conjunction with the generator authoring at least one material clause.
    When the predicate passes but no material concession is possible,
    ``concession_baseline_visible`` is False and ``concession_baseline``
    is None per spec §"Concession And Treaty Conversation Contract".
    """
    if side_pressure_score is None:
        return {
            "losing_for_concession_baseline": False,
            "concession_baseline_visible": False,
            "concession_baseline": None,
            "concession_baseline_reason": "no_side_pressure_score",
        }
    losing = int(side_pressure_score) <= LOSING_SIDE_PRESSURE_THRESHOLD
    if not losing:
        return {
            "losing_for_concession_baseline": False,
            "concession_baseline_visible": False,
            "concession_baseline": None,
            "concession_baseline_reason": "not_losing_side",
        }
    if not proposer_side_leader:
        return {
            "losing_for_concession_baseline": True,
            "concession_baseline_visible": False,
            "concession_baseline": None,
            "concession_baseline_reason": "missing_leaders",
        }
    baseline = compute_settlement_baseline(
        world,
        war_id=war_id,
        war_instance=war_instance,
        proposer_side=proposer_side,
        accepting_side=accepting_side,
        proposer_side_leader=proposer_side_leader,
        covered_enemy_participants=covered_enemy_participants,
        near_acceptance_floor=near_acceptance_floor,
    )
    draft_terms = [dict(t) for t in (baseline.get("settlement_terms") or [])]
    material_terms = [t for t in draft_terms if t.get("type") != "peace"]
    if not material_terms:
        return {
            "losing_for_concession_baseline": True,
            "concession_baseline_visible": False,
            "concession_baseline": None,
            "concession_baseline_reason": "no_material_concession_available",
        }
    reasoning = _format_concession_reasoning(
        proposer_leader=str(proposer_side_leader),
        terms=material_terms,
    )
    return {
        "losing_for_concession_baseline": True,
        "concession_baseline_visible": True,
        "concession_baseline": {
            "terms": draft_terms,
            "reasoning": reasoning,
        },
        "concession_baseline_reason": "material_concession_available",
    }


def _demand_baseline_region_candidates(
    world: Any,
    *,
    court: str,
    proposer_side_participants: Iterable[str],
    excluded_regions: Optional[Iterable[str]] = None,
) -> List[str]:
    """Ranked list of demand-region candidates a winning court would cede.

    Mirrors the bilateral demand-stage selection in
    ``generate_suggested_terms`` (border regions the enemy holds adjacent to
    the demanding side, excluding the enemy's capital — see
    ``diplomatic_templates.py`` stage 2b). The court keeps its capital; a
    border province changes hands. Deterministic tie-break is (income value
    low-first, region name) so the baseline regenerates identically across
    reruns. The border pool takes precedence — non-border holdings appear
    only when NO border province exists (the same either/or the single-pick
    selector always had, so head-of-list semantics are unchanged). Empty
    when the court holds only its capital (no transferable region).

    ``excluded_regions`` (Guided Terms §3.4, mirroring the concede-side
    selector's PF-1 param): regions already promised elsewhere in the
    staged package are ineligible, so a guided demand default can never
    double-promise a region (table-scoped V1).

    Guided Terms §8 OQ-1: the per-court rows render the FULL valid set as
    a dropdown, so this returns the whole ranked pool; the single-pick
    selector below takes the head.

    Golden Rule #8: holdings come from the cached
    ``world.get_nation_regions(...)`` lookups, not a full ``world.regions``
    scan.
    """
    regions = getattr(world, "regions", None)
    if not isinstance(regions, Mapping):
        return []
    excluded = {str(r) for r in (excluded_regions or []) if r}
    # World-scoped (item 7 family): Europe courts' capitals must stay
    # excluded from demand candidates. Attribute-fallback idiom (shim-safe).
    from backend.models.region import NATION_CAPITALS
    _capitals = getattr(world, "nation_capitals", None) or NATION_CAPITALS
    court_capital = _capitals.get(court)
    try:
        court_regions = list(world.get_nation_regions(court))
    except Exception:
        court_regions = []
    if not court_regions:
        return []
    proposer_holdings: set[str] = set()
    for participant in proposer_side_participants:
        if not participant:
            continue
        try:
            proposer_holdings.update(world.get_nation_regions(participant))
        except Exception:
            continue
    border: List[Tuple[int, str]] = []
    fallback: List[Tuple[int, str]] = []
    for rname in court_regions:
        if rname == court_capital:
            continue
        if str(rname) in excluded:
            continue
        region = regions.get(rname)
        if region is None:
            continue
        if bool(getattr(region, "is_capital", False)):
            continue
        income_value = int(getattr(region, "income_value", 100) or 100)
        fallback.append((income_value, str(rname)))
        adjacent = getattr(region, "adjacent_regions", None) or []
        if any(adj in proposer_holdings for adj in adjacent):
            border.append((income_value, str(rname)))
    pool = border or fallback
    pool.sort()
    return [name for _, name in pool]


def _demand_baseline_select_region(
    world: Any,
    *,
    court: str,
    proposer_side_participants: Iterable[str],
    excluded_regions: Optional[Iterable[str]] = None,
) -> Optional[str]:
    """Pick the deterministic demand region — the head of the ranked
    candidate pool (see `_demand_baseline_region_candidates`)."""
    candidates = _demand_baseline_region_candidates(
        world,
        court=court,
        proposer_side_participants=proposer_side_participants,
        excluded_regions=excluded_regions,
    )
    return candidates[0] if candidates else None


def _score_court_for_baseline(
    world: Any,
    *,
    war_id: str,
    war_instance: Mapping[str, Any],
    proposer_side: str,
    accepting_side: str,
    court: str,
    proposer_side_leader: Optional[str],
    covered: Iterable[str],
    settlement_terms: Iterable[Mapping[str, Any]],
    side_pressure_result: Optional[Mapping[str, Any]],
    direct_scores: Optional[Mapping[str, Mapping[str, int]]],
) -> Optional[int]:
    """Score ``court``'s acceptance of a candidate baseline package.

    Shares the package-level ``side_pressure_result`` / ``direct_scores``
    pass (both term-independent) so the baseline build does not re-walk war
    scores per candidate; ``raw_total_harshness`` is recomputed per call
    because it depends on the candidate terms. Returns the int score or None
    on a scorer hard stop.
    """
    result = settlement_scoring.calculate_common_peace_acceptance(
        world,
        war_id=war_id,
        war_instance=war_instance,
        proposer_side=proposer_side,
        accepting_side=accepting_side,
        accepting_leader=court,
        proposer_side_leader=proposer_side_leader,
        covered_enemy_participants=list(covered),
        settlement_terms=[dict(t) for t in settlement_terms],
        side_pressure_result=side_pressure_result,
        direct_scores=direct_scores,
    )
    score = result.get("score")
    return int(score) if score is not None else None


def _relax_baseline_demands_for_package_harshness(
    world: Any,
    *,
    war_id: str,
    war_instance: Mapping[str, Any],
    proposer_side: str,
    accepting_side: str,
    proposer_side_leader: Optional[str],
    covered: List[str],
    combined_terms: List[Dict[str, Any]],
    per_court_baseline: Dict[str, Any],
    side_pressure_result: Optional[Mapping[str, Any]],
    direct_scores: Optional[Mapping[str, Mapping[str, int]]],
    near_acceptance_floor: int,
) -> List[Dict[str, Any]]:
    """Reconcile the per-court demand build with the WHOLE-package score.

    ``_demand_terms_for_court`` floor-checks each court against only that
    court's OWN slice of harshness, but the live surface
    (``compute_per_court_acceptance``) scores every covered court against the
    WHOLE package's ``raw_total_harshness`` (package-level, shared across
    courts). So in a multi-court demand a court can pass its slice floor yet
    land far below it once the table's combined harshness applies — a winning
    multilateral that should carry opens deeply rejected instead (the Gate-4
    smoke surfaced France-vs-Britain+Prussia opening at 5/50 with both courts
    holding out despite a decisive lead).

    Strip demand clauses — one per pass, from the worst demand-direction court
    still below the floor under the FULL package — until every demand court
    clears ``near_acceptance_floor``, or no demand clause remains for it (a
    genuine holdout at peace). Concessions are never stripped (they only raise
    the accepting court's acceptance, so stripping them would deepen a reject).
    Deterministic (sorted courts, territory-before-gold, then highest index);
    only REMOVES clauses, so the package stays valid-by-construction and within
    the clause cap. ``per_court_baseline`` terms are kept in lockstep so the
    display matches the scored package.
    """
    covered_set = {str(c) for c in covered}
    sorted_covered = sorted(covered_set)

    def _is_demand_clause(clause: Any, court: str) -> bool:
        return (
            isinstance(clause, Mapping)
            and clause.get("type") != "peace"
            and str(clause.get("from") or "") == court
        )

    terms = [dict(t) for t in combined_terms]
    # Bounded: at most one demand clause is removed per pass.
    for _ in range(len(terms) + 1):
        below: List[tuple] = []
        for court in sorted_covered:
            entry = per_court_baseline.get(court) or {}
            if entry.get("direction") != "demand":
                continue
            if not any(_is_demand_clause(c, court) for c in terms):
                continue  # nothing left to relax for this court
            score = _score_court_for_baseline(
                world, war_id=war_id, war_instance=war_instance,
                proposer_side=proposer_side, accepting_side=accepting_side,
                court=court, proposer_side_leader=proposer_side_leader,
                covered=sorted_covered, settlement_terms=terms,
                side_pressure_result=side_pressure_result, direct_scores=direct_scores,
            )
            if score is not None and int(score) < int(near_acceptance_floor):
                below.append((int(score), court))
        if not below:
            break
        below.sort()  # lowest score first; court name breaks ties
        worst = below[0][1]
        worst_idxs = [i for i, c in enumerate(terms) if _is_demand_clause(c, worst)]
        # Territory cession is the harshest lever — drop it before gold.
        territory_idxs = [
            i for i in worst_idxs if terms[i].get("type") == "territory_cede"
        ]
        drop_idx = (territory_idxs or worst_idxs)[-1]
        dropped = terms.pop(drop_idx)
        entry = per_court_baseline.get(worst)
        if isinstance(entry, dict):
            kept: List[Dict[str, Any]] = []
            removed = False
            for t in entry.get("terms") or []:
                if not removed and t == dropped:
                    removed = True
                    continue
                kept.append(t)
            entry["terms"] = kept
            entry["relaxed_for_package_harshness"] = True
    return terms


def _degrade_generated_baseline_to_valid(
    world: Any,
    *,
    war_instance: Mapping[str, Any],
    proposer_side: str,
    covered: List[str],
    combined_terms: List[Dict[str, Any]],
    per_court_baseline: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """PF-1 / D1 — never return an invalid generated baseline.

    Runs ``validate_settlement_terms`` on the assembled package. While the
    package fails validation, the LAST covered court (reverse sorted order —
    the courts authored latest are "the unaffordable remainder") that still
    holds material clauses is degraded to the shared ``{"type": "peace"}``
    floor and the package is re-validated. Bounded, deterministic, and never
    raises; the worst case is the bare shared-peace package. With the
    cross-court budget/region threading upstream this pass is defense in
    depth — it exists so no caller can ever stage a generated draft the
    player-authoring gates would reject (DC-1: validity is a property of the
    draft store, not of the author).
    """
    terms = [dict(t) for t in combined_terms]
    covered_sorted = sorted({str(c) for c in covered if c})
    for _ in range(len(covered_sorted) + 1):
        validation = validate_settlement_terms(
            terms,
            proposer_side=proposer_side,
            covered_enemy_participants=covered_sorted,
            world=world,
            war_instance=war_instance,
        )
        if validation.get("valid"):
            return terms
        stripped = False
        for court in reversed(covered_sorted):
            material_idxs = [
                i for i, t in enumerate(terms) if _clause_touches_court(t, court)
            ]
            if not material_idxs:
                continue
            for i in reversed(material_idxs):
                terms.pop(i)
            entry = per_court_baseline.get(court)
            if isinstance(entry, dict):
                entry["terms"] = []
                entry["degraded_to_peace_floor"] = True
            stripped = True
            break
        if not stripped:
            break
    return terms


def compute_settlement_baseline(
    world: Any,
    *,
    war_id: str,
    war_instance: Mapping[str, Any],
    proposer_side: str,
    accepting_side: str,
    proposer_side_leader: Optional[str],
    covered_enemy_participants: Iterable[str],
    direct_scores: Optional[Mapping[str, Mapping[str, int]]] = None,
    side_pressure_result: Optional[Mapping[str, Any]] = None,
    accept_threshold: int = ACCEPTANCE_THRESHOLD,
    near_acceptance_floor: int = NEAR_ACCEPTANCE_FLOOR,
) -> Dict[str, Any]:
    """Re-front Slice 1 / spec §8 OQ#5 — the multi-party, per-court baseline.

    The ONE baseline generator (CH-4 deleted the legacy single-losing-side
    author): a per-court draft that chooses DIRECTION per covered court from
    *that court's* direct war score, not the package-level side-pressure
    scalar (which cannot express per-court direction). For each covered
    court:

    - ``select_direct_score(direct_scores[court])`` returns a
      ``(direct_score, source)`` tuple, or ``None`` when the court has no
      active cross-side pair. A ``None`` court is surfaced as a per-court
      **hard stop** (matching the scorer's ``HARD_STOP_NO_DIRECT_WAR_SCORE``)
      — it is NOT neutral-floored.
    - ``direct_score > +DIRECT_SCORE_DIRECTION_MARGIN`` → **demand** (France
      leads the court): author a border-region cession + a modest affordable
      indemnity *from the court*, each kept only while the court stays at/above
      the **near-acceptance floor** (so a suggested demand never pushes a
      winning court into outright reject). If even white peace for the court is
      below the floor — the shared package-level ``base_side_pressure``
      dominates — no demand is suggested and the court eases/drops in the
      conversation.
    - ``direct_score < -DIRECT_SCORE_DIRECTION_MARGIN`` → **concede** (France
      is pressured by the court): the existing peace→gold→territory
      escalation paid *by* the proposer leader, escalated only until the
      court reaches the near-acceptance floor.
    - inside the dead-band → ``{"type": "peace"}`` neutral floor.

    Returns ``{"settlement_terms": [...], "per_court_baseline": {court: {...}},
    "hard_stop_courts": [...], "covered_enemy_participants": [...]}``. The
    combined ``settlement_terms`` is one shared ``{"type": "peace"}`` plus each
    court's material slice, capped at ``MAX_SETTLEMENT_CLAUSE_COUNT``. The
    draft is deterministic (sorted court order, no RNG — OQ#6) and
    valid-by-construction.
    """
    covered = sorted({str(n) for n in (covered_enemy_participants or []) if n})
    proposer_participants = [
        str(n) for n in (war_instance.get(proposer_side) or []) if n
    ]
    if direct_scores is None:
        direct_scores = compute_direct_scores_by_enemy(
            world,
            war_instance,
            proposer_side=proposer_side,
            covered_enemy_participants=covered,
        )
    if side_pressure_result is None:
        side_pressure_result = compute_side_pressure_score(
            world,
            war_instance,
            proposer_side=proposer_side,
            covered_enemy_participants=covered,
            direct_scores=direct_scores,
        )

    combined_terms: List[Dict[str, Any]] = [{"type": "peace"}]
    per_court_baseline: Dict[str, Any] = {}
    hard_stop_courts: List[str] = []

    # PF-1 / D1 cross-court state: the per-court loop below used to size each
    # concede court against the FULL treasury and pick its region with no
    # knowledge of the other courts, so a two-concede-court table could
    # double-spend gold (2×(T−reserve) > T) and double-promise the one prime
    # cedeable region. Pre-compute each court's direction once, split the ONE
    # affordable treasury evenly across the concede-direction courts (the
    # player redistributes via dials / Tier 3), and thread a running
    # promised-region set through the region selector.
    selections: Dict[str, Optional[Tuple[int, str]]] = {
        court: select_direct_score(direct_scores.get(court) or {})
        for court in covered
    }
    concede_courts = [
        court for court in covered
        if selections[court] is not None
        and selections[court][0] < -DIRECT_SCORE_DIRECTION_MARGIN
    ]
    concession_gold_share: Optional[int] = None
    if proposer_side_leader and concede_courts:
        payer_balance = _concession_baseline_payer_balance(
            world, proposer_side_leader
        )
        affordable = payer_balance - CONCESSION_BASELINE_TREASURY_RESERVE
        concession_gold_share = max(0, affordable) // len(concede_courts)
    promised_regions: set = set()

    for court in covered:
        selection = selections[court]
        if selection is None:
            hard_stop_courts.append(court)
            per_court_baseline[court] = {
                "direction": "hard_stop",
                "direct_score": None,
                "terms": [],
                "reason": HARD_STOP_NO_DIRECT_WAR_SCORE,
            }
            continue
        direct_score, _source = selection
        budget_remaining = MAX_SETTLEMENT_CLAUSE_COUNT - len(combined_terms)
        court_terms: List[Dict[str, Any]] = []

        if direct_score > DIRECT_SCORE_DIRECTION_MARGIN:
            direction = "demand"
            # Author demands on a court France leads, mirroring
            # `generate_suggested_terms`' bilateral demand stage (border-region
            # demand at a strong lead + a modest affordable indemnity). The
            # helper is FLOOR-AWARE: it keeps a demand clause only while the
            # court stays at/above the near-acceptance floor, and suggests
            # nothing when even white peace for the court is below the floor
            # (`base_side_pressure` is package-level — §11.2 — so a led court can
            # share a negative package pressure). So a suggested demand never
            # pushes a winning court into outright reject (§8 OQ#5). Suggestions,
            # not impositions — the player can press harder or replace them in
            # Tier 3.
            court_terms = _demand_terms_for_court(
                world, war_id=war_id, war_instance=war_instance,
                proposer_side=proposer_side, accepting_side=accepting_side,
                court=court, proposer_side_leader=proposer_side_leader,
                proposer_side_participants=proposer_participants,
                covered=covered, side_pressure_result=side_pressure_result,
                direct_scores=direct_scores, direct_score=int(direct_score),
                near_acceptance_floor=near_acceptance_floor,
                budget_remaining=budget_remaining,
            )
        elif direct_score < -DIRECT_SCORE_DIRECTION_MARGIN:
            direction = "concede"
            court_terms = _concession_terms_for_court(
                world, war_id=war_id, war_instance=war_instance,
                proposer_side=proposer_side, accepting_side=accepting_side,
                court=court, proposer_side_leader=proposer_side_leader,
                covered=covered, side_pressure_result=side_pressure_result,
                direct_scores=direct_scores, near_acceptance_floor=near_acceptance_floor,
                budget_remaining=budget_remaining,
                gold_budget_cap=concession_gold_share,
                promised_regions=promised_regions,
            )
        else:
            direction = "peace"

        per_court_baseline[court] = {
            "direction": direction,
            "direct_score": int(direct_score),
            "terms": [dict(t) for t in court_terms],
            "reason": direction,
        }
        for term in court_terms:
            if len(combined_terms) >= MAX_SETTLEMENT_CLAUSE_COUNT:
                break
            combined_terms.append(term)

    # Each court's demand slice was floor-checked against its OWN harshness, but
    # the surface scores every court against the WHOLE package's harshness; relax
    # over-demanded courts so the assembled table clears the near-acceptance
    # floor it was built to (no spurious all-holdout opening on a winning war).
    combined_terms = _relax_baseline_demands_for_package_harshness(
        world,
        war_id=war_id,
        war_instance=war_instance,
        proposer_side=proposer_side,
        accepting_side=accepting_side,
        proposer_side_leader=proposer_side_leader,
        covered=covered,
        combined_terms=combined_terms,
        per_court_baseline=per_court_baseline,
        side_pressure_result=side_pressure_result,
        direct_scores=direct_scores,
        near_acceptance_floor=near_acceptance_floor,
    )

    # PF-1 / DC-1: a GENERATED baseline is held to the same validity bar as a
    # player-authored package — validate the assembled table and degrade the
    # unaffordable remainder to the shared peace floor rather than ever
    # returning an invalid draft (never stage invalid; never crash).
    combined_terms = _degrade_generated_baseline_to_valid(
        world,
        war_instance=war_instance,
        proposer_side=proposer_side,
        covered=covered,
        combined_terms=combined_terms,
        per_court_baseline=per_court_baseline,
    )

    return {
        "settlement_terms": combined_terms,
        "per_court_baseline": per_court_baseline,
        "hard_stop_courts": hard_stop_courts,
        "covered_enemy_participants": covered,
    }


def _concession_terms_for_court(
    world: Any,
    *,
    war_id: str,
    war_instance: Mapping[str, Any],
    proposer_side: str,
    accepting_side: str,
    court: str,
    proposer_side_leader: Optional[str],
    covered: Iterable[str],
    side_pressure_result: Optional[Mapping[str, Any]],
    direct_scores: Optional[Mapping[str, Mapping[str, int]]],
    near_acceptance_floor: int,
    budget_remaining: int,
    gold_budget_cap: Optional[int] = None,
    promised_regions: Optional[set] = None,
) -> List[Dict[str, Any]]:
    """Author proposer-side concessions (gold, then territory) that move a
    losing-direction ``court`` toward the near-acceptance floor.

    The peace→gold→territory escalation, scoped to one court and sharing
    the memoized package-level score inputs. Returns the
    material clauses the proposer leader pays/cedes to the court (no
    ``{"type": "peace"}`` — the caller owns the shared package peace).

    PF-1 / D1 cross-court state: ``gold_budget_cap`` is this court's share of
    the ONE treasury (the caller splits ``payer_balance - reserve`` across all
    concede-direction courts so the assembled table never commits more gold
    than the proposer holds), and ``promised_regions`` is the running set of
    regions already ceded to other courts in this package (mutated in place
    when this court takes a region) so one region is never promised twice.
    """
    if not proposer_side_leader or budget_remaining <= 0:
        return []
    terms: List[Dict[str, Any]] = []
    peace_score = _score_court_for_baseline(
        world, war_id=war_id, war_instance=war_instance,
        proposer_side=proposer_side, accepting_side=accepting_side,
        court=court, proposer_side_leader=proposer_side_leader,
        covered=covered, settlement_terms=[{"type": "peace"}],
        side_pressure_result=side_pressure_result, direct_scores=direct_scores,
    )
    if peace_score is not None and peace_score >= near_acceptance_floor:
        return []
    # Gold escalation: smallest strictly positive of (treasury - reserve,
    # hard cap, gap * 100), affordability-gated. The cross-court budget cap
    # bounds this court's draw on the shared treasury.
    payer_balance = _concession_baseline_payer_balance(world, proposer_side_leader)
    treasury_candidate = payer_balance - CONCESSION_BASELINE_TREASURY_RESERVE
    if gold_budget_cap is not None:
        treasury_candidate = min(treasury_candidate, int(gold_budget_cap))
    acceptance_gap = max(0, int(near_acceptance_floor) - int(peace_score or 0))
    gap_candidate = max(CONCESSION_BASELINE_GOLD_FLOOR, acceptance_gap * 100)
    if treasury_candidate > 0:
        positive = [
            c for c in (treasury_candidate, CONCESSION_BASELINE_GOLD_HARD_CAP, gap_candidate)
            if c > 0
        ]
        gold_amount = int(min(positive)) if positive else None
    else:
        gold_amount = None
    if gold_amount is not None and len(terms) < budget_remaining:
        terms.append({
            "type": "gold_indemnity",
            "from": proposer_side_leader,
            "to": court,
            "amount": int(gold_amount),
        })
    gold_score = _score_court_for_baseline(
        world, war_id=war_id, war_instance=war_instance,
        proposer_side=proposer_side, accepting_side=accepting_side,
        court=court, proposer_side_leader=proposer_side_leader,
        covered=covered, settlement_terms=[{"type": "peace"}] + terms,
        side_pressure_result=side_pressure_result, direct_scores=direct_scores,
    )
    escalate_to_territory = (
        gold_score is None or int(gold_score) < int(near_acceptance_floor)
    )
    if escalate_to_territory and len(terms) < budget_remaining:
        region = _concession_baseline_select_transferable_region(
            world,
            proposer_side_participants=list(war_instance.get(proposer_side) or []),
            accepting_leader=court,
            excluded_regions=promised_regions,
        )
        if region:
            terms.append({
                "type": "territory_cede",
                "from": proposer_side_leader,
                "to": court,
                "region": region,
            })
            if promised_regions is not None:
                promised_regions.add(str(region))
    return terms


def _demand_terms_for_court(
    world: Any,
    *,
    war_id: str,
    war_instance: Mapping[str, Any],
    proposer_side: str,
    accepting_side: str,
    court: str,
    proposer_side_leader: Optional[str],
    proposer_side_participants: Iterable[str],
    covered: Iterable[str],
    side_pressure_result: Optional[Mapping[str, Any]],
    direct_scores: Optional[Mapping[str, Mapping[str, int]]],
    direct_score: int,
    near_acceptance_floor: int,
    budget_remaining: int,
) -> List[Dict[str, Any]]:
    """Author demands (territory, then gold) on a court France leads, keeping
    that court at/above the near-acceptance floor.

    Mirrors `generate_suggested_terms`' bilateral demand stage (border-region
    demand at a strong lead + a modest affordable indemnity) but is
    **floor-aware**: a candidate clause is kept only when the court still
    scores at/above ``near_acceptance_floor`` with it (spec §8 OQ#5 — "never
    suggest a demand that makes a court outright reject"). Because
    ``base_side_pressure`` is package-level (§11.2), a court France leads can
    share a middling/negative package pressure; if even white peace for the
    court is below the floor, NO demand is suggested (the court is an
    ease/drop holdout regardless of terms, not a court the demand should push
    further down). Returns the kept demand clauses (no ``{"type": "peace"}`` —
    the caller owns the shared package peace).
    """
    if not proposer_side_leader or budget_remaining <= 0:
        return []
    peace_score = _score_court_for_baseline(
        world, war_id=war_id, war_instance=war_instance,
        proposer_side=proposer_side, accepting_side=accepting_side,
        court=court, proposer_side_leader=proposer_side_leader,
        covered=covered, settlement_terms=[{"type": "peace"}],
        side_pressure_result=side_pressure_result, direct_scores=direct_scores,
    )
    if peace_score is None or int(peace_score) < int(near_acceptance_floor):
        # Shared package pressure already rejects this court at white peace; a
        # demand can only make it worse. Suggest nothing — never push below the
        # floor (the court eases/drops in the conversation).
        return []
    kept: List[Dict[str, Any]] = []

    def _stays_acceptable(candidate: List[Dict[str, Any]]) -> bool:
        score = _score_court_for_baseline(
            world, war_id=war_id, war_instance=war_instance,
            proposer_side=proposer_side, accepting_side=accepting_side,
            court=court, proposer_side_leader=proposer_side_leader,
            covered=covered, settlement_terms=[{"type": "peace"}] + candidate,
            side_pressure_result=side_pressure_result, direct_scores=direct_scores,
        )
        return score is not None and int(score) >= int(near_acceptance_floor)

    # Border-region cession — strong lead only, mirroring the bilateral demand
    # stage (`war_score > 30`). Kept only if the court stays acceptable.
    if direct_score > DEMAND_TERRITORY_DIRECT_SCORE and len(kept) < budget_remaining:
        region = _demand_baseline_select_region(
            world,
            court=court,
            proposer_side_participants=proposer_side_participants,
        )
        if region:
            candidate = kept + [{
                "type": "territory_cede",
                "from": court,
                "to": proposer_side_leader,
                "region": region,
            }]
            if _stays_acceptable(candidate):
                kept = candidate
    # Affordable indemnity from the court, priced to its purse (EC-W4 —
    # was a flat CONCESSION_BASELINE_GOLD_FLOOR cap regardless of wealth).
    # Kept only if acceptable.
    court_balance = _concession_baseline_payer_balance(world, court)
    gold_candidate = min(
        court_balance - CONCESSION_BASELINE_TREASURY_RESERVE,
        max(
            CONCESSION_BASELINE_GOLD_FLOOR,
            int(court_balance * CONCESSION_BASELINE_TREASURY_FRACTION),
        ),
    )
    if gold_candidate > 0 and len(kept) < budget_remaining:
        candidate = kept + [{
            "type": "gold_indemnity",
            "from": court,
            "to": proposer_side_leader,
            "amount": int(gold_candidate),
        }]
        if _stays_acceptable(candidate):
            kept = candidate
        else:
            # EC-W4 (review finding #10h): the purse-scaled ask can exceed
            # what a marginal court tolerates — retry at the pre-EC-W4 floor
            # so a rich-but-reluctant court still yields the modest indemnity
            # it always did, instead of all-or-nothing dropping to zero.
            floor_amount = min(
                court_balance - CONCESSION_BASELINE_TREASURY_RESERVE,
                CONCESSION_BASELINE_GOLD_FLOOR,
            )
            if 0 < floor_amount < gold_candidate:
                fallback = kept + [{
                    "type": "gold_indemnity",
                    "from": court,
                    "to": proposer_side_leader,
                    "amount": int(floor_amount),
                }]
                if _stays_acceptable(fallback):
                    kept = fallback
    return kept


def _court_direction_from_selection(
    selection: Optional[Tuple[int, str]],
) -> str:
    """Map a ``select_direct_score`` result to the baseline direction enum.

    The SAME dead-band rule ``compute_settlement_baseline`` applies:
    ``demand`` above +margin, ``concede`` below -margin, ``peace`` inside the
    band, ``hard_stop`` when the court has no active cross-side pair
    (``selection is None`` — the tuple-or-``None`` contract).
    """
    if selection is None:
        return "hard_stop"
    score = int(selection[0])
    if score > DIRECT_SCORE_DIRECTION_MARGIN:
        return "demand"
    if score < -DIRECT_SCORE_DIRECTION_MARGIN:
        return "concede"
    return "peace"


def _court_direction_summary(
    court: str,
    proposer_side_leader: Optional[str],
    settlement_terms: Iterable[Mapping[str, Any]],
) -> str:
    """Humanize one court's slice of the package for the PROPOSE per-court row.

    Reads the clauses that touch ``court`` and renders a one-line
    "Demanded: <region> + <amount>g" / "Conceded: <region> + <amount>g" /
    "White peace" summary. Presentation only; never feeds the scored result.
    """
    demanded_regions: List[str] = []
    conceded_regions: List[str] = []
    demanded_gold = 0
    conceded_gold = 0
    for term in settlement_terms:
        if not isinstance(term, Mapping):
            continue
        ttype = term.get("type")
        frm = str(term.get("from") or "")
        to = str(term.get("to") or "")
        if ttype == "territory_cede":
            if frm == court:
                demanded_regions.append(str(term.get("region") or ""))
            elif to == court:
                conceded_regions.append(str(term.get("region") or ""))
        elif ttype in ("gold_indemnity", "gold_lump", "gold_per_turn"):
            amount = int(term.get("amount", 0) or 0)
            if frm == court:
                demanded_gold += amount
            elif to == court:
                conceded_gold += amount
    demand_parts: List[str] = []
    demand_parts.extend(r for r in demanded_regions if r)
    if demanded_gold > 0:
        demand_parts.append(f"{demanded_gold}g")
    concede_parts: List[str] = []
    concede_parts.extend(r for r in conceded_regions if r)
    if conceded_gold > 0:
        concede_parts.append(f"{conceded_gold}g")
    if demand_parts and concede_parts:
        return f"Demanded: {' + '.join(demand_parts)}; Conceded: {' + '.join(concede_parts)}"
    if demand_parts:
        return f"Demanded: {' + '.join(demand_parts)}"
    if concede_parts:
        return f"Conceded: {' + '.join(concede_parts)}"
    return "White peace"


# ---------------------------------------------------------------------------
# Guided Terms GT-Slice-2 — per-court suggestion payload (spec §3/§4/§9)
# ---------------------------------------------------------------------------


def _acceptance_component_breakdown(
    components: Mapping[str, Any],
) -> List[Dict[str, Any]]:
    """REFRONT-9 (Guided Terms OQ-5 / GT-A4) — the full component table for
    one court's score, display-ready for the expanded per-court row.

    Derived from the scorer's already-computed ``components`` map (free data
    — no extra score pass; the focus trigger stays presentation-only).
    Ordered by absolute magnitude descending (the biggest factors first),
    tie-broken by component name for determinism (Golden Rule #6). All
    values ``int()`` (Golden Rule #2).
    """
    rows: List[Dict[str, Any]] = []
    for component, value in (components or {}).items():
        try:
            value_int = int(value)
        except (TypeError, ValueError):
            continue
        rows.append({
            "component": str(component),
            "value": value_int,
            "component_display": acceptance_component_display(str(component)),
            "value_display": f"{value_int:+d}",
        })
    rows.sort(key=lambda r: (-abs(r["value"]), r["component"]))
    return rows


def compute_per_court_acceptance(
    world: Any,
    *,
    war_id: str,
    war_instance: Mapping[str, Any],
    proposer_side: str,
    accepting_side: str,
    proposer_side_leader: Optional[str],
    covered_enemy_participants: Iterable[str],
    settlement_terms: Iterable[Mapping[str, Any]],
    accept_threshold: int = ACCEPTANCE_THRESHOLD,
    direct_scores: Optional[Mapping[str, Mapping[str, int]]] = None,
    side_pressure_result: Optional[Mapping[str, Any]] = None,
    raw_total_harshness: Optional[float] = None,
    balance_projection: Optional[Mapping[str, Any]] = None,
    previous_bands: Optional[Mapping[str, str]] = None,
) -> Dict[str, Any]:
    """Re-front Slice 1 / spec §11.2 — the per-court acceptance aggregator.

    One ``calculate_common_peace_acceptance`` call per covered court over a
    single shared score pass (``direct_scores`` + ``side_pressure_result`` +
    ``raw_total_harshness`` are package-level and computed once — Golden Rule
    #8). Each call VARIES ``accepting_leader=<that court>`` while HOLDING
    ``covered_enemy_participants=<the full covered set>`` constant, so every
    court's burden / abandonment components still reflect the whole table
    (principle 5 — Talleyrand reasons across the table).

    Re-front Slice 2 / spec §15 F-5 — the balance projection
    (``project_balance_after_settlement``) is also package-level (independent
    of ``accepting_leader``), so the aggregator computes it ONCE for the whole
    covered loop and injects it into each scorer call via ``balance_projection``
    rather than letting the scorer recompute it per court (O(N) projections).
    A caller may pass a pre-computed ``balance_projection`` (one dial/coverage
    action shares it across re-scores); when ``None`` it is computed once here.

    A covered court with no active cross-side pair (``select_direct_score``
    returns ``None``) is surfaced as a per-court hard-stop row (``total=null``)
    rather than poisoning the shared side-pressure for the scoreable courts.

    ``overall_acceptance.carries`` is True iff *every* covered court has a
    non-null ``total`` at/above the accept threshold AND no per-court
    ``hard_stops`` (spec §11.4 — the per-covered-court ratification gate).
    """
    covered = sorted({str(n) for n in (covered_enemy_participants or []) if n})
    terms = [dict(t) for t in (settlement_terms or []) if isinstance(t, Mapping)]
    if direct_scores is None:
        direct_scores = compute_direct_scores_by_enemy(
            world,
            war_instance,
            proposer_side=proposer_side,
            covered_enemy_participants=covered,
        )
    selections = {
        court: select_direct_score(direct_scores.get(court) or {})
        for court in covered
    }
    scoreable = [court for court in covered if selections[court] is not None]
    if side_pressure_result is None:
        # Compute pressure over the scoreable subset so a no-direct-score
        # court does not bubble a hard stop that poisons every scorer call.
        side_pressure_result = compute_side_pressure_score(
            world,
            war_instance,
            proposer_side=proposer_side,
            covered_enemy_participants=scoreable,
            direct_scores={c: dict(direct_scores.get(c) or {}) for c in scoreable},
        )
    if raw_total_harshness is None:
        # G4F-1: package harshness prices the accepting-side burden terms
        # only (the scorer's own direction partition) — memoized here once
        # for the whole per-court loop.
        raw_total_harshness = compute_settlement_package_raw_harshness(
            terms,
            proposer_side_participants=list(
                war_instance.get(proposer_side) or []
            ),
        )
    if balance_projection is None and scoreable:
        # Slice 2 / §15 F-5: the projection is package-level (no leader arg),
        # so compute it ONCE for the whole per-court loop and inject it into
        # each scorer call instead of letting the scorer recompute it per
        # court. A hard-stop-only covered set (no scoreable court) needs no
        # projection.
        balance_projection = project_balance_after_settlement(
            world, war_id=war_id, settlement_terms=terms,
        )

    per_court: List[Dict[str, Any]] = []
    holdout_courts: List[str] = []
    carries = True
    previous_bands = previous_bands or {}

    for court in covered:
        # PF-1 / D6: each row carries the court's war-score DIRECTION (the
        # same dead-band rule the baseline generator uses) so presentation
        # consumers — the targeted-posture advisory, the budget-bound carry
        # hint — never recommend pressing a court France is losing to.
        direction = _court_direction_from_selection(selections[court])
        # Guided Terms §8 OQ-6: each row carries the selected raw
        # `direct_score` (the int half of the tuple-or-None contract) so
        # the budget-bound recommendation can tie-break deterministically
        # on `abs(direct_score)` without re-walking war scores. None on a
        # hard-stop row (no cross-side pair selects a score).
        selection = selections[court]
        row_direct_score = int(selection[0]) if selection is not None else None
        if court not in scoreable:
            band = "reject"
            per_court.append({
                "nation": court,
                "band": band,
                "band_display": acceptance_band_display(band),
                "total": None,
                "threshold": int(accept_threshold),
                "verdict": "reject",
                "direction": direction,
                "direct_score": row_direct_score,
                "top_blocker_display": acceptance_band_display(band),
                "direction_summary": _court_direction_summary(
                    court, proposer_side_leader, terms,
                ),
                "previous_band": previous_bands.get(court),
                "delta_display": None,
                # REFRONT-9: a hard-stopped court has no score pass, so it
                # has no component table to expand.
                "component_breakdown": [],
                "hard_stops": [
                    {"reason": HARD_STOP_NO_DIRECT_WAR_SCORE, "enemy": court}
                ],
            })
            carries = False
            holdout_courts.append(court)
            continue
        result = settlement_scoring.calculate_common_peace_acceptance(
            world,
            war_id=war_id,
            war_instance=war_instance,
            proposer_side=proposer_side,
            accepting_side=accepting_side,
            accepting_leader=court,
            proposer_side_leader=proposer_side_leader,
            covered_enemy_participants=covered,
            settlement_terms=terms,
            side_pressure_result=side_pressure_result,
            direct_scores=direct_scores,
            raw_total_harshness=raw_total_harshness,
            balance_projection=balance_projection,
        )
        enriched = _enrich_acceptance_display(result)
        total = result.get("score")
        band = str(enriched.get("band") or result.get("verdict") or "reject")
        hard_stops = list(result.get("hard_stops") or [])
        court_passes = (
            total is not None and int(total) >= int(accept_threshold) and not hard_stops
        )
        below_threshold = total is None or int(total) < int(accept_threshold)
        top_blocker = enriched.get("top_blocker_display") if below_threshold else None
        previous_band = previous_bands.get(court)
        delta_display = None
        if previous_band and previous_band != band:
            delta_display = (
                f"{court} {acceptance_band_display(previous_band)} "
                f"→ {acceptance_band_display(band)}"
            )
        per_court.append({
            "nation": court,
            "band": band,
            "band_display": acceptance_band_display(band),
            "total": int(total) if total is not None else None,
            "threshold": int(accept_threshold),
            "verdict": result.get("verdict"),
            "direction": direction,
            "direct_score": row_direct_score,
            "top_blocker_display": top_blocker,
            # CA8-17: the component KEY beside the label, same gating —
            # the table voice speaks it; the table itself keeps the label.
            "top_blocker_component": (
                enriched.get("top_blocker_component")
                if below_threshold else None),
            "direction_summary": _court_direction_summary(
                court, proposer_side_leader, terms,
            ),
            "previous_band": previous_band,
            "delta_display": delta_display,
            # REFRONT-9 (Guided Terms OQ-5 / GT-A4): the full component
            # table for the expanded per-court row — derived from the score
            # pass already in hand, so the focus trigger stays
            # presentation-only (no re-score on expand).
            "component_breakdown": _acceptance_component_breakdown(
                result.get("components") or {},
            ),
            "hard_stops": hard_stops,
        })
        if not court_passes:
            carries = False
            holdout_courts.append(court)

    if not covered:
        carries = False
    if carries:
        summary_display = "This peace carries."
    elif len(holdout_courts) == 1:
        summary_display = f"{holdout_courts[0]} is the holdout."
    elif holdout_courts:
        summary_display = f"{len(holdout_courts)} courts hold out."
    else:
        summary_display = "No covered courts."
    # G4F-7 (Gate-4 smoke): the ONE full-deal fact — carries iff EVERY
    # covered court reaches the threshold — stated with per-court score
    # attribution ("Britain 44/50"), so the table's per-court integers can
    # never again read as an aggregate "high acceptance". Rendered by the
    # popup HEADER (above the scroll), not just the below-the-fold summary.
    holdout_set = set(holdout_courts)

    def _holdout_score_label(row: Mapping[str, Any]) -> str:
        nation = str(row.get("nation") or "?")
        total = row.get("total")
        if total is None:
            return f"{nation} (no terms can move them)"
        return f"{nation} {int(total)}/{int(row.get('threshold') or accept_threshold)}"

    if carries:
        carry_verdict_display = (
            "Will carry as drafted — every court at or above "
            f"{int(accept_threshold)}."
        )
    elif holdout_courts:
        carry_verdict_display = (
            f"Will NOT carry as drafted — every court must reach "
            f"{int(accept_threshold)}. Holding out: "
            + ", ".join(
                _holdout_score_label(r)
                for r in per_court
                if r.get("nation") in holdout_set
            )
            + "."
        )
    else:
        carry_verdict_display = "No covered courts."
    return {
        "per_court_acceptance": per_court,
        "overall_acceptance": {
            "carries": bool(carries),
            "holdout_courts": holdout_courts,
            "summary_display": summary_display,
            "carry_verdict_display": carry_verdict_display,
        },
    }
