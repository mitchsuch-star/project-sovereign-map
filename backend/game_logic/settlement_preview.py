"""Public door for the settlement package (CH-1 split).

The former 11.6k-line god module is split into seven layered modules; this
module re-exports the PUBLIC settlement API so external callers and tests
have one stable import surface. Production code imports true homes; new
settlement code should too. The layers (each imports only lower ones):

    settlement_routes.py      L0  routing / reopen / recovery / actionability
    settlement_validation.py  L1  primitives + eligibility + validate_settlement_terms
    settlement_baseline.py    L2  baseline generation + presets + per-court acceptance
    settlement_staging.py     L3  draft stores + confirm build + stage + guided payload
    settlement_ratify.py      L4  apply / ratify / replacement staging
    settlement_actions.py     L5  dialogue-action dispatch + handler arms (CH-2 target)
    settlement_offers.py      L6  incoming offers + ally petitions + recurring payments

Two documented lazy edges run upward (stage_settlement_confirm ->
settlement_offers petition queueing) via function-level imports — the
established settlement cycle-break pattern. The scorer patch seam for tests
is backend.game_logic.settlement_scoring.calculate_common_peace_acceptance
(all raw call sites resolve it late through the module attribute).

Internal (underscore) helpers are NOT re-exported — import them from their
true home; patch them on the namespace that consumes them.
"""

from backend.game_logic.settlement_routes import (
    SETTLEMENT_ERROR_DISPLAY,
    SETTLEMENT_FAMILY_DIALOGUE_TYPES,
    SETTLEMENT_REOPEN_MAX_ATTEMPTS,
    SETTLEMENT_ROUTE_NAMESPACE,
    derive_settlement_review_target,
    evaluate_war_detail_actionability,
    get_reopen_attempts,
    is_war_archived,
    is_war_known,
    mint_settlement_route_id,
    record_reopen_attempt,
    reopen_attempt_cap_exceeded,
    resolve_settlement_route_click,
)
from backend.game_logic.settlement_validation import (
    LOSING_SIDE_PRESSURE_THRESHOLD,
    PAIR_SUBSTITUTE_ACTIONS,
    PAIR_SUBSTITUTE_REFUSAL_CODES,
    PAIR_SUBSTITUTE_TEMPORAL_REFUSAL_CODES,
    RATIFY_LEGACY_APPLY_CLAUSE_TYPES,
    VALID_SIDES,
    evaluate_liberation_eligibility,
    evaluate_open_settlement_eligibility,
    evaluate_pair_peace_substitute_eligibility,
    evaluate_subjugation_eligibility,
    evaluate_vassalage_eligibility,
    get_coverable_enemy_participants,
    is_common_settlement_worth_showing,
    validate_settlement_terms,
)
from backend.game_logic.settlement_baseline import (
    CONCESSION_BASELINE_BFS_MAX_DEPTH,
    CONCESSION_BASELINE_GOLD_FLOOR,
    CONCESSION_BASELINE_GOLD_HARD_CAP,
    CONCESSION_BASELINE_TREASURY_RESERVE,
    DEMAND_TERRITORY_DIRECT_SCORE,
    DIRECT_SCORE_DIRECTION_MARGIN,
    SETTLEMENT_DIAL_GOLD_STEP,
    compute_per_court_acceptance,
    compute_settlement_baseline,
    compute_settlement_treasury_line,
)
from backend.game_logic.settlement_staging import (
    SETTLEMENT_COOLDOWN_TURNS,
    SETTLEMENT_EDITOR_CALLER_KIND,
    build_settlement_confirm_dialogue,
    build_settlement_preview,
    compute_settlement_draft_key,
    discard_scoped_settlement_draft,
    load_scoped_settlement_draft,
    revalidate_staged_settlement,
    save_scoped_settlement_draft,
    stage_settlement_confirm,
)
from backend.game_logic.settlement_ratify import (
    ratify_settlement_confirm,
)
from backend.game_logic.settlement_actions import (
    SETTLEMENT_DEMAND_VERB_ACTION_IDS,
    handle_settlement_dialogue_action,
)
from backend.game_logic.settlement_offers import (
    ALLY_SETTLEMENT_PETITION_ACK_ACTION,
    ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE,
    ALLY_SETTLEMENT_PETITION_REQUEST_OPEN,
    ALLY_SETTLEMENT_PETITION_SHIPPED_TYPES,
    ALLY_SETTLEMENT_PETITION_SOLICITED_TRIGGERS,
    ALLY_SETTLEMENT_PETITION_WARN_SELLOUT,
    INCOMING_OFFERS_DEFERRED,
    build_ally_settlement_petition_dialogue,
    build_ally_settlement_petition_popup,
    build_incoming_settlement_offer_popup,
    handle_ally_settlement_petition_action,
    handle_incoming_settlement_offer_action,
    process_recurring_settlement_payments,
    promote_pending_settlement_offers,
    queue_ally_settlement_petitions_for_player_action,
)

__all__ = [
    "ALLY_SETTLEMENT_PETITION_ACK_ACTION",
    "ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE",
    "ALLY_SETTLEMENT_PETITION_REQUEST_OPEN",
    "ALLY_SETTLEMENT_PETITION_SHIPPED_TYPES",
    "ALLY_SETTLEMENT_PETITION_SOLICITED_TRIGGERS",
    "ALLY_SETTLEMENT_PETITION_WARN_SELLOUT",
    "CONCESSION_BASELINE_BFS_MAX_DEPTH",
    "CONCESSION_BASELINE_GOLD_FLOOR",
    "CONCESSION_BASELINE_GOLD_HARD_CAP",
    "CONCESSION_BASELINE_TREASURY_RESERVE",
    "DEMAND_TERRITORY_DIRECT_SCORE",
    "DIRECT_SCORE_DIRECTION_MARGIN",
    "INCOMING_OFFERS_DEFERRED",
    "LOSING_SIDE_PRESSURE_THRESHOLD",
    "PAIR_SUBSTITUTE_ACTIONS",
    "PAIR_SUBSTITUTE_REFUSAL_CODES",
    "PAIR_SUBSTITUTE_TEMPORAL_REFUSAL_CODES",
    "RATIFY_LEGACY_APPLY_CLAUSE_TYPES",
    "SETTLEMENT_COOLDOWN_TURNS",
    "SETTLEMENT_DEMAND_VERB_ACTION_IDS",
    "SETTLEMENT_DIAL_GOLD_STEP",
    "SETTLEMENT_EDITOR_CALLER_KIND",
    "SETTLEMENT_ERROR_DISPLAY",
    "SETTLEMENT_FAMILY_DIALOGUE_TYPES",
    "SETTLEMENT_REOPEN_MAX_ATTEMPTS",
    "SETTLEMENT_ROUTE_NAMESPACE",
    "VALID_SIDES",
    "build_ally_settlement_petition_dialogue",
    "build_ally_settlement_petition_popup",
    "build_incoming_settlement_offer_popup",
    "build_settlement_confirm_dialogue",
    "build_settlement_preview",
    "compute_per_court_acceptance",
    "compute_settlement_baseline",
    "compute_settlement_draft_key",
    "compute_settlement_treasury_line",
    "derive_settlement_review_target",
    "discard_scoped_settlement_draft",
    "evaluate_liberation_eligibility",
    "evaluate_open_settlement_eligibility",
    "evaluate_pair_peace_substitute_eligibility",
    "evaluate_subjugation_eligibility",
    "evaluate_vassalage_eligibility",
    "evaluate_war_detail_actionability",
    "get_coverable_enemy_participants",
    "get_reopen_attempts",
    "handle_ally_settlement_petition_action",
    "handle_incoming_settlement_offer_action",
    "handle_settlement_dialogue_action",
    "is_common_settlement_worth_showing",
    "is_war_archived",
    "is_war_known",
    "load_scoped_settlement_draft",
    "mint_settlement_route_id",
    "process_recurring_settlement_payments",
    "promote_pending_settlement_offers",
    "queue_ally_settlement_petitions_for_player_action",
    "ratify_settlement_confirm",
    "record_reopen_attempt",
    "reopen_attempt_cap_exceeded",
    "resolve_settlement_route_click",
    "revalidate_staged_settlement",
    "save_scoped_settlement_draft",
    "stage_settlement_confirm",
    "validate_settlement_terms",
]
