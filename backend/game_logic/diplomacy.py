"""
Diplomacy Engine — Phase 8 Session 2

All functions are pure/deterministic — no LLM calls.
Single source of truth for diplomatic mechanics:
  - State transitions & validation
  - War score calculation
  - Acceptance formula
  - DP economy
  - War declaration & cascade
  - Downgrade transitions
"""

import copy
import random  # noqa: F401 — used in _process_mission_effects
from typing import Dict, List, Mapping, Optional

from backend.display_names import (
    FEEDBACK_STRINGS,
    STATE_DISPLAY as _STATE_DISPLAY_NAMES,
    proposal_display_name as _proposal_display_name,
)
from backend.game_logic.settlement_helpers import (
    CascadeContext,
    WAR_INSTANCE_MERGE_REQUIRED,
    WAR_INSTANCE_SIDE_CONFLICT,
    attach_pair_to_war_instance,
    attach_participant_to_war_instance,
    ensure_war_instance_for_pair,
    mark_pair_armistice,
    resolve_pair_to_resolved,
    validate_war_declaration,
)

# ═══════ DIPLOMATIC STATE HIERARCHY ═══════
# Upgrade path (adjacency enforced):
# WAR → ARMISTICE → PEACE → OPEN_BORDERS → NON_AGGRESSION → DEFENSIVE_ALLIANCE → ALLIANCE
#                                                                                       ↓
#                                                                                    VASSAL

DIPLOMATIC_STATES = [
    "WAR", "ARMISTICE", "PEACE", "OPEN_BORDERS",
    "NON_AGGRESSION", "DEFENSIVE_ALLIANCE", "ALLIANCE", "VASSAL"
]

# Upgrade adjacency (index in list → next valid state)
_UPGRADE_ORDER = [
    "WAR", "ARMISTICE", "PEACE", "OPEN_BORDERS",
    "NON_AGGRESSION", "DEFENSIVE_ALLIANCE", "ALLIANCE"
]

# Downgrade adjacency
# Note: ARMISTICE and VASSAL intentionally excluded — ARMISTICE auto-expires via
# _process_armistice_turns(), VASSAL exits via release_vassal() or rebellion.
_DOWNGRADE_ORDER = [
    "ALLIANCE", "DEFENSIVE_ALLIANCE", "NON_AGGRESSION",
    "OPEN_BORDERS", "PEACE"
]

# States that allow movement through territory
OPEN_MOVEMENT_STATES = {"OPEN_BORDERS", "NON_AGGRESSION", "DEFENSIVE_ALLIANCE", "ALLIANCE", "VASSAL"}

# ═══════ TRADE INCOME TABLE (§7e) ═══════
TRADE_INCOME = {
    "PEACE": 50,
    "OPEN_BORDERS": 100,
    "NON_AGGRESSION": 150,
    "DEFENSIVE_ALLIANCE": 150,
    "ALLIANCE": 200,
}
# WAR, ARMISTICE: 0. VASSAL: 0 (tribute replaces trade, Session 5)

# ═══════ TRANSITION COSTS & REQUIREMENTS ═══════
TRANSITION_RULES = {
    # (from, to): {"dp_cost": int, "relation_req": int or None}
    ("WAR", "ARMISTICE"): {"dp_cost": 1, "relation_req": None},
    ("ARMISTICE", "PEACE"): {"dp_cost": 2, "relation_req": -60},
    ("PEACE", "OPEN_BORDERS"): {"dp_cost": 1, "relation_req": -20},
    ("OPEN_BORDERS", "NON_AGGRESSION"): {"dp_cost": 1, "relation_req": 0},
    ("NON_AGGRESSION", "DEFENSIVE_ALLIANCE"): {"dp_cost": 2, "relation_req": 20},
    ("DEFENSIVE_ALLIANCE", "ALLIANCE"): {"dp_cost": 2, "relation_req": 40},
}

# ═══════ STATE-LEVEL RELATION REQUIREMENTS (R98: jumps) ═══════
# For non-adjacent upward jumps, the TARGET state's relation requirement applies.
STATE_RELATION_REQUIREMENTS = {
    "ARMISTICE": None,
    "PEACE": -60,
    "OPEN_BORDERS": -20,
    "NON_AGGRESSION": 0,
    "DEFENSIVE_ALLIANCE": 20,
    "ALLIANCE": 40,
}

# Vassal: requires WAR (dictated peace) or OPEN_BORDERS+
VASSAL_MIN_STATES = {"WAR", "OPEN_BORDERS", "NON_AGGRESSION", "DEFENSIVE_ALLIANCE", "ALLIANCE"}
VASSAL_DP_COST = 3

# War declaration
WAR_DP_COST = 1

# ═══════ DOWNGRADE PENALTIES ═══════
DOWNGRADE_PENALTIES = {
    ("ALLIANCE", "DEFENSIVE_ALLIANCE"): {
        "dp_cost": 1, "relation_target": -15, "relation_all": -5, "threat": 5
    },
    ("DEFENSIVE_ALLIANCE", "NON_AGGRESSION"): {
        "dp_cost": 1, "relation_target": -20, "relation_all": -5, "threat": 5
    },
    ("NON_AGGRESSION", "OPEN_BORDERS"): {
        "dp_cost": 1, "relation_target": -15, "relation_all": 0, "threat": 3
    },
    ("OPEN_BORDERS", "PEACE"): {
        "dp_cost": 1, "relation_target": -10, "relation_all": 0, "threat": 0
    },
}

# Auto-downgrade thresholds (§5b.1)
STATE_RELATION_THRESHOLDS = {
    "ALLIANCE": 40,
    "DEFENSIVE_ALLIANCE": 20,
    "NON_AGGRESSION": 0,
    "OPEN_BORDERS": -20,
}

# ═══════ BASE DISPOSITION BY PROPOSAL TYPE ═══════
BASE_DISPOSITION = {
    "armistice_losing": 40,
    "armistice_winning": 20,
    "peace": 30,
    "alliance": 20,
    "defensive_alliance": 25,
    "vassalage": 10,
    "open_borders": 35,
    "non_aggression": 30,
    "ultimatum_demand": 20,
}

# ═══════ PERSONALITY MODIFIERS ═══════
# {personality: (peace_alliance_mod, harsh_demands_mod)}
PERSONALITY_MODIFIERS = {
    "dove": (10, -10),
    "hawk": (-5, 5),
    "loyalist": (0, 0),
    "schemer": (5, 5),
}

# ═══════ SPECIAL ACCEPTANCE BONUSES (§6d) ═══════
# Checked against proposal clauses
SPECIAL_BONUSES = {
    "Prussia": {"territory_saxony": 10},
    "Austria": {"territory_bavaria": 8},
    "Britain": {"continental_system_lifted": 15},
    "Saxony": {"protection_promised": 10},
}

# ═══════ SWEETENER / DEMAND VALUES ═══════
SWEETENER_VALUES = {
    "gold_lump": 1 / 100,         # +1 per 100g (R145: was 1/200)
    "gold_per_turn": 3 / 100,     # +3 per 100g/turn
    "manpower_per_turn": 2 / 2000, # +2 per 2000 infantry/turn
    "infantry_manpower": 2 / 5000, # +2 per 5000
    "cavalry_manpower": 4 / 2500,  # +4 per 2500
    "artillery_manpower": 5 / 1500, # +5 per 1500
    "unit_swap": 3,                # +3 per favorable trade
    "ap_per_turn": 18,             # +18 per AP (1 AP/turn is an entire extra action — worth more than territory)
    "territory": 8,                # +8 per region (R144: was 5)
    "territory_cede": 8,           # +8 per region (alias for ratification path)
    "open_borders": 3,             # +3 flat
    "protection": 5,               # +5 flat
}
SWEETENER_CAP = 60                 # R146: was 30, raised to 60 so escalated offers improve acceptance

DEMAND_VALUES = {
    "gold_per_turn": -5 / 100,     # -5 per 100g/turn demanded (PL-12-E: was -2)
    "gold_lump": -3 / 100,         # -3 per 100g lump demanded (PL-18)
    "manpower_per_turn": -3 / 2000, # -3 per 2000 infantry/turn demanded
    "manpower_infantry": -3 / 2000, # -3 per 2000 infantry demanded (PL-18)
    "manpower_cavalry": -5 / 2000,  # -5 per 2000 cavalry demanded (PL-18, scarcer)
    "manpower_artillery": -8 / 2000, # -8 per 2000 artillery demanded (PL-18, rarest)
    "manpower": -3 / 2000,         # backward compat alias → infantry rate (PL-18)
    "territory": -5,                # -5 per region demanded
    "territory_cede": -5,           # alias for ratification path
    "ap_per_turn": -25,             # -25 per AP demanded (extreme)
    "unit_swap": -2,                # -2 per unfavorable trade
    "forced_alliance": -20,         # WPS-C §9.1: significant demand
    "liberation": -15,              # WPS-C §10.5: per vassal liberated
}

# Commitment-bearing states. Breaking out of one of these should produce a
# remembered political breach, not just a generic state flip.
COMMITMENT_STATES = {
    "OPEN_BORDERS",
    "NON_AGGRESSION",
    "DEFENSIVE_ALLIANCE",
    "ALLIANCE",
    "VASSAL",
}

_BREACH_SEVERITY_BY_TREATY = {
    "open_borders": "low",
    "non_aggression": "medium",
    "defensive_alliance": "high",
    "alliance": "high",
    "vassal": "high",
}

# RELIABILITY_COMMITMENTS_SPEC §9.9 fault families.
# `french_breach`: actor voluntarily ruptured a commitment (perpetrator at fault).
# `counterparty_reversal`: the counterparty reversed first (no perpetrator penalty).
# `obsolescence_or_external`: basis disappeared / external cascade (no perpetrator penalty).
# `defensive_refusal_termination`: §8.8.7a — a `call_to_arms_refused_defensive`
#     episode that also auto-terminates an existing ALLIANCE / DEFENSIVE_ALLIANCE
#     between breaker and victim. Parallel to `french_breach` but distinct: the
#     refusal episode itself carries the reliability/strike/grievance fault,
#     so this termination event adds no strike of its own (§8.8.7a "cascade
#     interaction" clause).
END_REASON_FAMILY_FRENCH_BREACH = "french_breach"
END_REASON_FAMILY_COUNTERPARTY_REVERSAL = "counterparty_reversal"
END_REASON_FAMILY_OBSOLESCENCE_OR_EXTERNAL = "obsolescence_or_external"
END_REASON_FAMILY_DEFENSIVE_REFUSAL_TERMINATION = "defensive_refusal_termination"

# `end_reason_action` = what the actor did (the old substrate enum).
# Split from `end_reason_family` (who is at fault) so presentation can stage
# "France abandoned" vs "France forced into rupture" distinctly per §9.9.
_REASON_ACTION_PHRASES = {
    "manual_break": "without seeking release",
    "war_declaration": "by declaring war",
    "paradox_choice": "to resolve a diplomatic paradox",
    "cascade_forced": "when dragged into war by an ally",
    # B-B4 §8.8.7a: the refusal-event-as-repudiation phrasing. Used on
    # `diplomatic_treaty_broken` events emitted by
    # `emit_call_to_arms_refused_defensive` so the campaign log / dispatch
    # reads "Russia has broken the alliance with Austria by refusing the
    # defensive call" rather than the generic `manual_break` wording.
    "defensive_refusal": "by refusing the defensive call",
}

# Per-witness scope reason (RELIABILITY_COMMITMENTS_SPEC §8.4 precedence).
# `ally`     : witness has DEFENSIVE_ALLIANCE/ALLIANCE with the injured party
# `rival`    : witness has an active rivalry against the breaker
# `shared_enemy`  : witness shares a current enemy with the injured party
# `region_observer`: witness has a live bargain over the claim region (deferred;
#                    bargain store does not yet exist in this substrate)
WITNESS_SCOPE_ALLY = "ally"
WITNESS_SCOPE_RIVAL = "rival"
WITNESS_SCOPE_SHARED_ENEMY = "shared_enemy"
WITNESS_SCOPE_REGION_OBSERVER = "region_observer"
# B-B4 §8.8.3 — DG-4 defensive-refusal wider witness scope. Any nation
# holding an active treaty with the breaker qualifies as a witness when
# the ally / rival roles don't already apply. Only used by the DG-4
# episodes (`call_to_arms_refused_defensive`, `call_to_arms_honored_costly`).
WITNESS_SCOPE_TREATY_PARTNER_OF_BREAKER = "treaty_partner_of_breaker"
WITNESS_SCOPE_TREATY_PARTNER_OF_HONORER = "treaty_partner_of_honorer"

WITNESS_SCOPE_PRECEDENCE = (
    WITNESS_SCOPE_ALLY,
    WITNESS_SCOPE_RIVAL,
    WITNESS_SCOPE_SHARED_ENEMY,
    WITNESS_SCOPE_REGION_OBSERVER,
)

# B-B4 §8.8.3 — DG-4 defensive-refusal precedence inserts
# `treaty_partner_of_breaker` between `rival` and `shared_enemy`. Used
# only when resolving witnesses for DG-4 episodes; legacy treaty-breach
# resolution keeps the narrower `WITNESS_SCOPE_PRECEDENCE`.
DG4_WITNESS_SCOPE_PRECEDENCE = (
    WITNESS_SCOPE_ALLY,
    WITNESS_SCOPE_RIVAL,
    WITNESS_SCOPE_TREATY_PARTNER_OF_BREAKER,
    WITNESS_SCOPE_SHARED_ENEMY,
    WITNESS_SCOPE_REGION_OBSERVER,
)

# B-B4 §8.8.3 — "active treaty" for the wider DG-4 witness scope.
# Excludes WAR (not a treaty) and PEACE (the default absent state).
# ARMISTICE is belligerent-adjacent and deliberately excluded; it is
# treated like WAR for this check to avoid counting a ceasefire signatory
# as a witness-scope treaty partner.
_ACTIVE_TREATY_STATES_FOR_DG4_WITNESS = frozenset({
    "OPEN_BORDERS",
    "NON_AGGRESSION",
    "DEFENSIVE_ALLIANCE",
    "ALLIANCE",
    "VASSAL",
})

WARNING_SEVERITY_ORDINAL = {
    "critical": 3,
    "high": 2,
    "medium": 1,
    "low": 0,
}

WARNING_CATEGORY_ORDER = {
    "paradox": 0,
    "hard_reject": 1,
    "bargain": 2,
    "betrayal": 3,
    "hegemony": 4,
    "concern": 4,  # legacy alias for pre-v2.4 hegemony warnings
    "peace_conflict": 5,
    "rivalry": 5,  # legacy alias for old war-joiner preview warnings
}

_BETRAYAL_DECAY_BY_SEVERITY = {
    "low": 6,
    "medium": 8,
    "high": 10,
}

_DEEP_TREATY_TYPES = {"defensive_alliance", "alliance"}
_NON_WAR_TREATY_STATES = {
    "PEACE",
    "OPEN_BORDERS",
    "NON_AGGRESSION",
    "DEFENSIVE_ALLIANCE",
    "ALLIANCE",
    "VASSAL",
}

DG4_EVENT_REFUSED_OFFENSIVE = "call_to_arms_refused_offensive"
DG4_EVENT_REFUSED_DEFENSIVE = "call_to_arms_refused_defensive"
DG4_EVENT_HONORED_COSTLY = "call_to_arms_honored_costly"

DG4_DEFENSIVE_REFUSAL_SEVERITY_MULTIPLIER = 1.75
DG4_COSTLY_HONOR_POWER_RATIO = 1.8
DG4_IMPOSSIBLE_POWER_RATIO = 2.5
DG4_OATHBREAKER_REFUSALS_REQUIRED = 2
DG4_OATHBREAKER_WINDOW_TURNS = 15
DG4_OATHBREAKER_AUTO_REJECT_TURNS = 10
DG4_LOYALTY_BOND_TURNS = 30
DG4_LOYALTY_BOND_RELATION_DELTA = 10

DG4_EPISODE_EFFECTS = {
    DG4_EVENT_REFUSED_OFFENSIVE: {
        "reliability_delta": -6,
        "victim_strikes": 1,
        "witness_relation_delta": -2,
        "severity_multiplier": 1.0,
    },
    DG4_EVENT_REFUSED_DEFENSIVE: {
        "reliability_delta": -10,
        "victim_strikes": 2,
        "witness_relation_delta": -3,
        "severity_multiplier": DG4_DEFENSIVE_REFUSAL_SEVERITY_MULTIPLIER,
    },
    DG4_EVENT_HONORED_COSTLY: {
        "reliability_delta": 5,
        "victim_strikes": 0,
        "witness_relation_delta": 2,
        "severity_multiplier": 1.0,
    },
}


def _sort_structured_warnings(warnings: List[Dict]) -> List[Dict]:
    """Apply the shared commitments warning ordering contract."""
    return sorted(
        warnings,
        key=lambda warning: (
            -WARNING_SEVERITY_ORDINAL.get(str(warning.get("severity", "low")), 0),
            WARNING_CATEGORY_ORDER.get(str(warning.get("category", "")), 99),
            str(warning.get("text", "")),
        ),
    )


def _betrayal_key(actor: str, victim: str) -> str:
    return f"{actor}|{victim}"


def _get_active_betrayal_strikes(world, actor: str, victim: str) -> List[Dict]:
    """Return the still-active bilateral strikes for actor -> victim."""
    history = getattr(world, "betrayal_history", {}) or {}
    record = history.get(_betrayal_key(actor, victim), {}) or {}
    current_turn = int(getattr(world, "current_turn", 0))
    active = []
    for strike in record.get("strikes", []) or []:
        decays_on_turn = int(strike.get("decays_on_turn", current_turn + 1) or current_turn + 1)
        if decays_on_turn > current_turn:
            active.append({
                "severity": str(strike.get("severity", "")),
                "turn": int(strike.get("turn", 0)),
                "episode_id": str(strike.get("episode_id", "")),
                "decays_on_turn": decays_on_turn,
            })
    return active


def _get_active_betrayal_strike_count(world, actor: str, victim: str) -> int:
    return int(len(_get_active_betrayal_strikes(world, actor, victim)))


# ────────────────────────────────────────────────────────────────────────────
# B-B4 / §8.8.4 — victim-grade grievance flags on betrayal_history pair entries
# ────────────────────────────────────────────────────────────────────────────
# The grievance flag is the durable half of a defensive-refusal episode. The
# underlying `+2` victim strike decays under §8.6 rules; the flag does NOT.
# The flag is removable only through Make Amends (grievance variant, §8.6.1a).
#
# Storage: each flag is a dict on `record["grievance_flags"]` with keys:
#   - `grievance_type`  : e.g. "defensive_call_refused"  (extensible)
#   - `episode_id`      : root-cause episode id
#   - `turn`            : creation turn (FIFO order for Make Amends removal)
#   - `source_episode_type` : e.g. "call_to_arms_refused_defensive"
#
# Stacking cap: all flags are retained in storage so the ledger can surface
# "4+ grievances" distinctly. `grievance_modifier` (§8.8.9 / §9.3) caps its
# penalty input at 3 flags per pair. Ordering is by creation turn; ties are
# broken by episode_id lexicographic order so FIFO removal is deterministic
# even if two grievances land on the same turn.

_GRIEVANCE_STACKING_CAP_FOR_MODIFIER = 3


def _get_grievance_flags(world, breaker: str, victim: str) -> List[Dict]:
    """Return the persistent grievance-flag list for breaker -> victim.

    Flags do not decay under §8.6 passive rules; the list is exactly what is
    stored on the pair record. Callers must not mutate the returned list.
    """
    history = getattr(world, "betrayal_history", {}) or {}
    record = history.get(_betrayal_key(breaker, victim), {}) or {}
    return list(record.get("grievance_flags", []) or [])


def _get_active_grievance_flag_count(world, breaker: str, victim: str) -> int:
    """Active grievance count for the pair (no decay; 0 when pair is clean)."""
    return int(len(_get_grievance_flags(world, breaker, victim)))


def _get_capped_grievance_flag_count(world, breaker: str, victim: str) -> int:
    """Grievance count capped at the acceptance-formula stacking cap (§8.8.4).

    Cap is exposed as a helper so `grievance_modifier` and debug surfaces
    agree on saturation: the capped value drives the penalty, the raw value
    drives the ledger row.
    """
    return min(
        _GRIEVANCE_STACKING_CAP_FOR_MODIFIER,
        _get_active_grievance_flag_count(world, breaker, victim),
    )


def _add_grievance_flag(
    world,
    *,
    breaker: str,
    victim: str,
    grievance_type: str,
    episode_id: str,
    source_episode_type: str,
) -> Dict:
    """Append a durable grievance flag to the breaker -> victim pair.

    Returns the freshly recorded flag dict. Updates `last_turn` on the
    record to match the new strike-alignment bookkeeping; creates an
    empty strike list if the pair is otherwise fresh (grievance-only
    state is legal after the originating +2 strike has decayed).
    """
    current_turn = int(getattr(world, "current_turn", 0))
    history = getattr(world, "betrayal_history", {}) or {}
    key = _betrayal_key(breaker, victim)
    record = history.get(key) or {
        "strikes": [],
        "categories": [],
        "last_turn": 0,
        "grievance_flags": [],
    }
    flags = list(record.get("grievance_flags", []) or [])
    flag = {
        "grievance_type": str(grievance_type),
        "episode_id": str(episode_id),
        "turn": current_turn,
        "source_episode_type": str(source_episode_type),
    }
    flags.append(flag)
    record["grievance_flags"] = flags
    categories = set(record.get("categories", []) or [])
    categories.add("grievance")
    record["categories"] = sorted(categories)
    record["last_turn"] = current_turn
    history[key] = record
    world.betrayal_history = history
    return flag


def _remove_oldest_grievance_flag(
    world, breaker: str, victim: str,
) -> Optional[Dict]:
    """FIFO remove the oldest grievance flag for breaker -> victim.

    Ordering: (`turn`, `episode_id`) ascending — matches §8.6.1a "oldest
    grievance by grievance-creation turn" with a deterministic episode_id
    tie-break.

    Returns the removed flag dict, or None if the pair has no flags.
    Prunes the pair record entirely if no strikes + no grievance flags
    remain (matches §8.6.1 strike-removal cleanup so the pair reads as a
    clean slate once repaired).
    """
    history = getattr(world, "betrayal_history", {}) or {}
    key = _betrayal_key(breaker, victim)
    record = history.get(key)
    if not record:
        return None
    flags = list(record.get("grievance_flags", []) or [])
    if not flags:
        return None
    oldest = min(
        flags,
        key=lambda f: (int(f.get("turn", 0) or 0), str(f.get("episode_id", ""))),
    )
    flags.remove(oldest)
    if flags:
        record["grievance_flags"] = flags
        history[key] = record
    else:
        record["grievance_flags"] = []
        if not record.get("strikes"):
            history.pop(key, None)
        else:
            # B-B4 — when the final grievance flag clears but strikes
            # remain, drop the `grievance` category so downstream
            # routing (ledger rows, C3 notice filtering) reflects the
            # live-flag state rather than the pair's historical record.
            # Strike-only pairs after a repair should not surface under
            # grievance queries.
            categories = set(record.get("categories", []) or [])
            categories.discard("grievance")
            record["categories"] = sorted(categories)
            history[key] = record
    world.betrayal_history = history
    return oldest


def grievance_modifier(asker: str, target: str, world) -> int:
    """Acceptance-formula penalty from victim-side durable grievances (§8.8.9).

    Target holds one or more grievance flags against asker (asker is the
    breaker, target is the abandoned victim). Penalty is `-30` per active
    flag, saturating at the `_GRIEVANCE_STACKING_CAP_FOR_MODIFIER` limit
    (`-90` maximum per pair). Rationale: §8.8.4 cap — "history never made
    a sixth betrayal score worse than the third."

    Returns 0 whenever:
    - asker == target or either is falsy
    - target holds no grievance flag against asker

    The raw active flag count (uncapped) surfaces separately in debug /
    ledger output so the player can distinguish "3 flags" from "4+ flags"
    visually; only the capped count drives the formula.
    """
    if not asker or not target or asker == target:
        return 0
    active = _get_capped_grievance_flag_count(world, asker, target)
    return -30 * active


# ────────────────────────────────────────────────────────────────────────────
# B-B4 / §8.8.7a — call-to-arms refused (defensive) episode emitter
# ────────────────────────────────────────────────────────────────────────────


def emit_call_to_arms_refused_defensive(
    world,
    *,
    breaker: str,
    victim: str,
    severity: str = "high",
    call_context: Optional[Dict] = None,
    episode_id: Optional[str] = None,
) -> Dict:
    """Emit a `call_to_arms_refused_defensive` episode + fold-through effects.

    Per spec §§8.8.1–8.8.7a. This is the substrate-level programmatic seam
    the DG-4 decision path will route through once the three-path resolver
    lands. Ships in B-B4 with an internal entry point so acceptance-formula
    and Make Amends regressions can be pinned before the UI seams exist.

    Effects (in order):
    1. Record a `+2` victim-side betrayal strike under `severity` (default
       "high" for §8.3 decay bucket alignment; matures in 10 turns).
    2. Record a durable victim-grade grievance flag
       (`grievance_type="defensive_call_refused"`).
    3. Apply `-10` to breaker's reliability (clamped to [-100, 100]).
    4. If breaker/victim currently share ALLIANCE or DEFENSIVE_ALLIANCE,
       terminate it to PEACE in the same call (§8.8.7a) and emit
       `diplomatic_treaty_broken` with
       `end_reason_family = "defensive_refusal_termination"`. Bloc cache
       is invalidated by `set_diplomatic_state`, so later same-turn
       `get_bloc_members` reads the post-termination geometry.
    5. Log + queue the `call_to_arms_refused_defensive` event.

    No-op-return fields make the emitter safe to call whether or not a
    binding alliance currently exists between the pair.

    Args:
        world: WorldState.
        breaker: the nation refusing the call.
        victim: the calling principal (the abandoned ally).
        severity: strike severity for §8.3 decay tables (default "high").
        call_context: optional snapshot of the refused call (defensive /
            offensive flag, principal power-ratio at call moment, etc.).
        episode_id: optional pre-allocated id so multi-victim refusals in
            the same turn can share bookkeeping.

    Returns:
        Dict with episode_id, grievance flag payload, alliance termination
        flag, strike record, and reliability delta for callers that want to
        pin the result in tests or dispatch UI.
    """
    if not breaker or not victim or breaker == victim:
        raise ValueError(
            "emit_call_to_arms_refused_defensive requires distinct "
            "breaker and victim nations"
        )
    episode_id = episode_id or _allocate_episode_id(world, prefix="call")
    current_turn = int(getattr(world, "current_turn", 0))
    honor_bias = _get_honor_bias(world, breaker)
    call_context = dict(call_context or {})
    reliability_delta = _scaled_dg4_delta(
        world, breaker, DG4_EVENT_REFUSED_DEFENSIVE, "reliability_delta",
        call_context=call_context,
    )
    witness_relation_delta = _scaled_dg4_delta(
        world, breaker, DG4_EVENT_REFUSED_DEFENSIVE, "witness_relation_delta",
        call_context=call_context,
    )
    severity_factors = _dg4_scale_components(world, breaker, call_context)
    severity_factors["defensive_refusal_severity_multiplier"] = float(
        _defensive_refusal_severity_multiplier(world)
    )

    # ── 1. Betrayal strike (+2 victim-grade, severity "high" by default) ──
    strike_record = _record_betrayal_strikes(
        world,
        actor=breaker,
        victim=victim,
        severity=severity,
        episode_id=episode_id,
        count=int(DG4_EPISODE_EFFECTS[DG4_EVENT_REFUSED_DEFENSIVE]["victim_strikes"]),
        decay_multiplier=honor_bias,
    )

    # ── 2. Durable grievance flag (§8.8.4 — does not decay) ──
    grievance = _add_grievance_flag(
        world,
        breaker=breaker,
        victim=victim,
        grievance_type="defensive_call_refused",
        episode_id=episode_id,
        source_episode_type="call_to_arms_refused_defensive",
    )

    # ── 3. Reliability penalty on breaker (-10 per §8.8.2 severity table) ──
    reliability_before, reliability_after = _apply_reliability_delta(
        world, breaker, reliability_delta,
    )

    # ── 4. Alliance termination §8.8.7a (same-turn, only if binding exists) ──
    alliance_terminated = False
    previous_alliance_state = world.get_diplomatic_state(breaker, victim)
    if previous_alliance_state in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
        pair_key = world._make_diplo_key(breaker, victim)
        existing_treaty = getattr(world, "active_treaties", {}).get(pair_key)
        breach_preview = get_treaty_breach_preview(
            world,
            breaker,
            victim,
            treaty=existing_treaty,
            end_reason_action="defensive_refusal",
            fault_nation=breaker,
            episode_id=episode_id,
        )
        # Force the state transition first; `set_diplomatic_state` handles
        # bloc-cache invalidation + hegemony band-crossing notification.
        set_diplomatic_state(
            world, breaker, victim, "PEACE", "defensive_refusal_termination",
        )
        # Then record the breach event on the normal channel. The refusal
        # episode carries the strike + grievance + reliability penalty
        # already, so the breach event itself adds no new strike
        # (`_record_treaty_breach` gates strike recording on FRENCH_BREACH,
        # and defensive_refusal_termination is a distinct family).
        _record_treaty_breach(
            world,
            breach_preview,
            new_state="PEACE",
            trigger_context={
                "refusal_episode_id": episode_id,
                "refusal_episode_type": "call_to_arms_refused_defensive",
                "breaker": breaker,
                "victim": victim,
            },
        )
        alliance_terminated = True

    # ── 5. Witness scope (§8.8.3) + witness_strike_recorded dispatch per witness ──
    # The wider DG-4 scope is computed AFTER the same-turn alliance
    # termination so `treaty_partner_of_breaker` reflects post-termination
    # geometry (the abandoned victim is already the `victim`, not a
    # witness; `set_diplomatic_state` above has already downgraded any
    # existing ALLIANCE to PEACE so the former ally won't accidentally
    # qualify as its own witness through a stale ALLIANCE edge).
    witness_scope = _get_dg4_refused_defensive_witness_scope(
        world, breaker, victim,
    )
    coalition_snapshot = _snapshot_defensive_refusal_coalition_partners(
        world, breaker, victim,
    )

    # ── 6. Anti-renewal cooldown (§8.8.7) — applies regardless of whether
    # an existing alliance was terminated. A refusal alone earns the pair a
    # cooldown before new ALLIANCE / DEFENSIVE_ALLIANCE ratification.
    anti_renewal_expires_on_turn = _set_anti_renewal_cooldown(
        world, breaker, victim,
    )
    anti_renewal_cooldown_turns = _anti_renewal_window_turns(world)

    # ── 7. Emit the refusal episode on campaign log, notification, and dispatch ──
    from backend.game_logic.dispatch import queue_dispatch_event
    coalition_threat_expires_on_turn = current_turn + max(
        1,
        int(round(_BETRAYAL_DECAY_BY_SEVERITY.get(severity, 8) * honor_bias)),
    )

    refusal_payload = {
        "type": "call_to_arms_refused_defensive",
        "episode_id": episode_id,
        "breaker": breaker,
        "victim": victim,
        "severity": str(severity),
        "strike_recorded": bool(strike_record.get("recorded")),
        "grievance_flag": grievance,
        "alliance_terminated": alliance_terminated,
        "previous_alliance_state": previous_alliance_state
        if alliance_terminated
        else "",
        "reliability_before": reliability_before,
        "reliability_after": reliability_after,
        "reliability_delta": reliability_after - reliability_before,
        "resolved_reliability_delta": int(reliability_delta),
        "honor_bias": float(honor_bias),
        "witness_relation_delta": int(witness_relation_delta),
        "severity_factors": severity_factors,
        "victim_strikes": int(strike_record.get("strikes_added", 0) or 0),
        "witnesses": list(witness_scope["witnesses"]),
        "coalition_threat_partners_at_refusal": list(coalition_snapshot),
        "witness_dominant_scope": witness_scope["dominant_scope"],
        "witness_scope_label": witness_scope["label"],
        "witness_count": witness_scope["count"],
        "anti_renewal_expires_on_turn": int(anti_renewal_expires_on_turn),
        "anti_renewal_cooldown_turns": int(anti_renewal_cooldown_turns),
        "coalition_threat_expires_on_turn": int(coalition_threat_expires_on_turn),
        "call_context": dict(call_context),
        "turn": current_turn,
        "speaker_attribution": "envoy",
        "speaker_target_nation": victim,
    }
    world.log_event(refusal_payload)
    _emit_commitments_notification(
        world,
        DG4_EVENT_REFUSED_DEFENSIVE,
        refusal_payload,
    )
    queue_dispatch_event(
        world,
        "call_to_arms_refused_defensive",
        {
            "episode_id": episode_id,
            "breaker": breaker,
            "victim": victim,
            "severity": str(severity),
            "alliance_terminated": alliance_terminated,
            "reliability_before": reliability_before,
            "reliability_after": reliability_after,
            "reliability_delta": reliability_after - reliability_before,
            "resolved_reliability_delta": int(reliability_delta),
            "witness_relation_delta": int(witness_relation_delta),
            "severity_factors": severity_factors,
            "witness_count": witness_scope["count"],
            "witness_dominant_scope": witness_scope["dominant_scope"],
            "anti_renewal_cooldown_turns": int(anti_renewal_cooldown_turns),
            "turn": current_turn,
            "speaker_attribution": "envoy",
            "speaker_target_nation": victim,
        },
        "partial_on_nation",
    )

    # ── 8. Per-witness relation effects and dispatch events so the
    # presentation layer can collapse same-episode witness reactions.
    _queue_dg4_witness_events(
        world,
        episode_id=episode_id,
        event_type=DG4_EVENT_REFUSED_DEFENSIVE,
        actor=breaker,
        victim=victim,
        witnesses=witness_scope["witnesses"],
        relation_delta=witness_relation_delta,
    )
    if strike_record.get("triggered_hard_reject"):
        _emit_hard_reject_posture_triggered(
            world, perpetrator=breaker, victim=victim, episode_id=episode_id,
        )
    _record_oathbreaker_refusal(world, breaker, episode_id)

    return {
        "episode_id": episode_id,
        "strike_record": strike_record,
        "grievance_flag": grievance,
        "alliance_terminated": alliance_terminated,
        "previous_alliance_state": previous_alliance_state
        if alliance_terminated
        else "",
        "reliability_before": reliability_before,
        "reliability_after": reliability_after,
        "reliability_delta": reliability_after - reliability_before,
        "resolved_reliability_delta": int(reliability_delta),
        "witness_relation_delta": int(witness_relation_delta),
        "severity_factors": severity_factors,
        "victim_strikes": int(strike_record.get("strikes_added", 0) or 0),
        "witnesses": list(witness_scope["witnesses"]),
        "coalition_threat_partners_at_refusal": list(coalition_snapshot),
        "witness_count": witness_scope["count"],
        "witness_dominant_scope": witness_scope["dominant_scope"],
        "anti_renewal_expires_on_turn": int(anti_renewal_expires_on_turn),
        "anti_renewal_cooldown_turns": int(anti_renewal_cooldown_turns),
        "coalition_threat_expires_on_turn": int(coalition_threat_expires_on_turn),
    }


def emit_call_to_arms_refused_offensive(
    world,
    *,
    breaker: str,
    victim: str,
    severity: str = "medium",
    call_context: Optional[Dict] = None,
    episode_id: Optional[str] = None,
) -> Dict:
    """Emit attacker-side offensive call refusal memory."""
    if not breaker or not victim or breaker == victim:
        raise ValueError(
            "emit_call_to_arms_refused_offensive requires distinct "
            "breaker and victim nations"
        )
    episode_id = episode_id or _allocate_episode_id(world, prefix="call")
    current_turn = int(getattr(world, "current_turn", 0))
    honor_bias = _get_honor_bias(world, breaker)
    call_context = dict(call_context or {})
    reliability_delta = _scaled_dg4_delta(
        world, breaker, DG4_EVENT_REFUSED_OFFENSIVE, "reliability_delta",
        call_context=call_context,
    )
    witness_relation_delta = _scaled_dg4_delta(
        world, breaker, DG4_EVENT_REFUSED_OFFENSIVE, "witness_relation_delta",
        call_context=call_context,
    )
    severity_factors = _dg4_scale_components(world, breaker, call_context)
    strike_record = _record_betrayal_strikes(
        world,
        actor=breaker,
        victim=victim,
        severity=severity,
        episode_id=episode_id,
        count=int(DG4_EPISODE_EFFECTS[DG4_EVENT_REFUSED_OFFENSIVE]["victim_strikes"]),
        decay_multiplier=honor_bias,
    )
    reliability_before, reliability_after = _apply_reliability_delta(
        world, breaker, reliability_delta,
    )
    witness_scope = _get_dg4_refused_offensive_witness_scope(world, breaker, victim)

    from backend.game_logic.dispatch import queue_dispatch_event

    payload = {
        "type": DG4_EVENT_REFUSED_OFFENSIVE,
        "episode_id": episode_id,
        "breaker": breaker,
        "victim": victim,
        "severity": str(severity),
        "strike_recorded": bool(strike_record.get("recorded")),
        "victim_strikes": int(strike_record.get("strikes_added", 0) or 0),
        "reliability_before": reliability_before,
        "reliability_after": reliability_after,
        "reliability_delta": reliability_after - reliability_before,
        "resolved_reliability_delta": int(reliability_delta),
        "honor_bias": float(honor_bias),
        "witness_relation_delta": int(witness_relation_delta),
        "severity_factors": severity_factors,
        "witnesses": list(witness_scope["witnesses"]),
        "witness_dominant_scope": witness_scope["dominant_scope"],
        "witness_scope_label": witness_scope["label"],
        "witness_count": witness_scope["count"],
        "call_context": dict(call_context),
        "turn": current_turn,
        "speaker_attribution": "envoy",
        "speaker_target_nation": victim,
    }
    world.log_event(payload)
    _emit_commitments_notification(
        world,
        DG4_EVENT_REFUSED_OFFENSIVE,
        payload,
    )
    queue_dispatch_event(
        world,
        DG4_EVENT_REFUSED_OFFENSIVE,
        {
            "episode_id": episode_id,
            "breaker": breaker,
            "victim": victim,
            "severity": str(severity),
            "reliability_delta": reliability_after - reliability_before,
            "witness_relation_delta": int(witness_relation_delta),
            "severity_factors": severity_factors,
            "witness_count": witness_scope["count"],
            "turn": current_turn,
            "speaker_attribution": "envoy",
            "speaker_target_nation": victim,
        },
        "partial_on_nation",
    )
    _queue_dg4_witness_events(
        world,
        episode_id=episode_id,
        event_type=DG4_EVENT_REFUSED_OFFENSIVE,
        actor=breaker,
        victim=victim,
        witnesses=witness_scope["witnesses"],
        relation_delta=witness_relation_delta,
    )
    if strike_record.get("triggered_hard_reject"):
        _emit_hard_reject_posture_triggered(
            world, perpetrator=breaker, victim=victim, episode_id=episode_id,
        )
    return {
        "episode_id": episode_id,
        "strike_record": strike_record,
        "reliability_before": reliability_before,
        "reliability_after": reliability_after,
        "reliability_delta": reliability_after - reliability_before,
        "witnesses": list(witness_scope["witnesses"]),
        "witness_count": witness_scope["count"],
        "witness_relation_delta": int(witness_relation_delta),
        "severity_factors": severity_factors,
    }


def emit_call_to_arms_honored_costly(
    world,
    *,
    honorer: str,
    victim: str,
    severity: str = "high",
    call_context: Optional[Dict] = None,
    episode_id: Optional[str] = None,
) -> Dict:
    """Emit the positive DG-4 costly-honor episode."""
    if not honorer or not victim or honorer == victim:
        raise ValueError(
            "emit_call_to_arms_honored_costly requires distinct "
            "honorer and victim nations"
        )
    episode_id = episode_id or _allocate_episode_id(world, prefix="call")
    current_turn = int(getattr(world, "current_turn", 0))
    honor_bias = _get_honor_bias(world, honorer)
    call_context = dict(call_context or {})
    reliability_delta = _scaled_dg4_delta(
        world, honorer, DG4_EVENT_HONORED_COSTLY, "reliability_delta",
        call_context=call_context,
    )
    witness_relation_delta = _scaled_dg4_delta(
        world, honorer, DG4_EVENT_HONORED_COSTLY, "witness_relation_delta",
        call_context=call_context,
    )
    severity_factors = _dg4_scale_components(world, honorer, call_context)
    reliability_before, reliability_after = _apply_reliability_delta(
        world, honorer, reliability_delta,
    )
    relation_after = world.modify_nation_relation(
        honorer, victim, DG4_LOYALTY_BOND_RELATION_DELTA,
    )
    pair_key = world._make_diplo_key(honorer, victim)
    bond = {
        "episode_id": episode_id,
        "honorer": honorer,
        "victim": victim,
        "turn": current_turn,
        "expires_on_turn": current_turn + DG4_LOYALTY_BOND_TURNS,
        "relation_delta": DG4_LOYALTY_BOND_RELATION_DELTA,
    }
    bonds = dict(getattr(world, "call_to_arms_loyalty_bonds", {}) or {})
    bonds.setdefault(pair_key, []).append(bond)
    world.call_to_arms_loyalty_bonds = bonds
    witness_scope = _get_dg4_honored_costly_witness_scope(world, honorer, victim)
    cleared_oathbreaker = _clear_oathbreaker_posture(
        world, honorer, episode_id=episode_id, reason=DG4_EVENT_HONORED_COSTLY,
    )

    from backend.game_logic.dispatch import queue_dispatch_event

    payload = {
        "type": DG4_EVENT_HONORED_COSTLY,
        "episode_id": episode_id,
        "honorer": honorer,
        "victim": victim,
        "severity": str(severity),
        "reliability_before": reliability_before,
        "reliability_after": reliability_after,
        "reliability_delta": reliability_after - reliability_before,
        "resolved_reliability_delta": int(reliability_delta),
        "honor_bias": float(honor_bias),
        "victim_relation_after": int(relation_after),
        "loyalty_bond": bond,
        "witness_relation_delta": int(witness_relation_delta),
        "severity_factors": severity_factors,
        "witnesses": list(witness_scope["witnesses"]),
        "witness_dominant_scope": witness_scope["dominant_scope"],
        "witness_scope_label": witness_scope["label"],
        "witness_count": witness_scope["count"],
        "cleared_oathbreaker": bool(cleared_oathbreaker),
        "call_context": dict(call_context),
        "turn": current_turn,
        "speaker_attribution": "foreign_office",
        "speaker_target_nation": getattr(world, "player_nation", "France"),
    }
    world.log_event(payload)
    _emit_commitments_notification(
        world,
        DG4_EVENT_HONORED_COSTLY,
        payload,
    )
    queue_dispatch_event(
        world,
        DG4_EVENT_HONORED_COSTLY,
        {
            "episode_id": episode_id,
            "honorer": honorer,
            "victim": victim,
            "severity": str(severity),
            "reliability_delta": reliability_after - reliability_before,
            "loyalty_bond_turns": DG4_LOYALTY_BOND_TURNS,
            "witness_relation_delta": int(witness_relation_delta),
            "severity_factors": severity_factors,
            "witness_count": witness_scope["count"],
            "turn": current_turn,
            "speaker_attribution": "foreign_office",
            "speaker_target_nation": getattr(world, "player_nation", "France"),
        },
        "partial_on_nation",
    )
    _queue_dg4_witness_events(
        world,
        episode_id=episode_id,
        event_type=DG4_EVENT_HONORED_COSTLY,
        actor=honorer,
        victim=victim,
        witnesses=witness_scope["witnesses"],
        relation_delta=witness_relation_delta,
    )
    return {
        "episode_id": episode_id,
        "reliability_before": reliability_before,
        "reliability_after": reliability_after,
        "reliability_delta": reliability_after - reliability_before,
        "loyalty_bond": bond,
        "witnesses": list(witness_scope["witnesses"]),
        "witness_count": witness_scope["count"],
        "witness_relation_delta": int(witness_relation_delta),
        "severity_factors": severity_factors,
        "cleared_oathbreaker": bool(cleared_oathbreaker),
    }


def _shared_enemy_exists(world, nation_a: str, nation_b: str) -> bool:
    """Check whether two nations currently fight a common enemy."""
    for other in world.get_active_nations():
        if other in (nation_a, nation_b):
            continue
        if world.is_at_war(nation_a, other) and world.is_at_war(nation_b, other):
            return True
    return False


def has_hard_reject_posture(world, actor: str, victim: str) -> bool:
    """Public helper for pair-specific hard-reject posture."""
    return _get_active_betrayal_strike_count(world, actor, victim) >= 3


def hegemony_target_mod(asker: str, target: str, world) -> int:
    """Per-pair acceptance friction from the hegemon bloc pressing outward.

    Per RELIABILITY_COMMITMENTS_SPEC v2.4.3 §9.1. Reads the shared
    `_identify_max_bloc_share` helper so the 30-33% pre-noticed zone
    produces real cross-bloc friction while `_calculate_hegemony_pressure`
    keeps passive threat accrual gated at 33%+.

    Formula: `max(-20, -int((share - 0.30) * 60))`:
    - 0 at exactly 30% (formula floor, integer truncation)
    - -1 at 33%, -12 at 50%, -18 at 60%, -20 clamp at ~63.34%+

    Returns 0 when any gate fails:
    - asker == target or either is falsy
    - no hegemon (no active nations / zero european_power)
    - share < 0.30
    - asker NOT in hegemon's bloc (non-bloc askers don't carry the tax)
    - target IN hegemon's bloc (intra-bloc proposals are frictionless)
    """
    if not asker or not target or asker == target:
        return 0
    from backend.game_logic.coalition import _identify_max_bloc_share
    hegemon, share = _identify_max_bloc_share(world)
    if hegemon is None or share < 0.30:
        return 0
    try:
        members = set(world.get_bloc_members(hegemon))
    except AttributeError:
        return 0
    if asker not in members:
        return 0
    if target in members:
        return 0
    # Stabilize exact-threshold buckets against binary float drift.
    # This preserves the spec's truncation contract (0.33 -> -1, 1/3 -> -2,
    # 0.6333... -> -20) without switching to rounding.
    raw = int(((share - 0.30) * 60) + 1e-9)
    return max(-20, -raw)


def bilateral_betrayal_mod(asker: str, target: str, world) -> int:
    """Per-pair acceptance penalty from remembered betrayals.

    Per RELIABILITY_COMMITMENTS_SPEC v2.4.3 §9.2. Flat `-6` per active
    victim-side strike. No stacking cap — the 3-strike hard-reject posture
    is the door-shut mechanic and composes on top of this for deep-treaty
    proposals via `has_hard_reject_posture` + the `-100` score clamp in
    `calculate_acceptance`.

    `_get_active_betrayal_strike_count` arg order is `(world, actor, victim)`
    so asker=actor, target=victim.
    """
    if not asker or not target or asker == target:
        return 0
    return -6 * _get_active_betrayal_strike_count(world, asker, target)


def _record_betrayal_strike(
    world,
    *,
    actor: str,
    victim: str,
    severity: str,
    episode_id: str,
    decay_multiplier: float = 1.0,
) -> Dict:
    """Persist one remembered bilateral betrayal strike."""
    current_turn = int(getattr(world, "current_turn", 0))
    history = getattr(world, "betrayal_history", {}) or {}
    key = _betrayal_key(actor, victim)
    record = history.get(key) or {"strikes": [], "categories": [], "last_turn": 0}
    active_before = _get_active_betrayal_strike_count(world, actor, victim)

    active_same_episode = [
        strike
        for strike in _get_active_betrayal_strikes(world, actor, victim)
        if strike.get("episode_id") == episode_id
    ]
    if len(active_same_episode) >= 2:
        return {
            "recorded": False,
            "active_before": active_before,
            "active_after": active_before,
            "triggered_hard_reject": False,
        }

    decay_turns = _BETRAYAL_DECAY_BY_SEVERITY.get(severity, 8)
    try:
        decay_turns = max(1, int(round(decay_turns * float(decay_multiplier or 1.0))))
    except (TypeError, ValueError):
        decay_turns = _BETRAYAL_DECAY_BY_SEVERITY.get(severity, 8)
    record.setdefault("strikes", []).append({
        "severity": severity,
        "turn": current_turn,
        "episode_id": episode_id,
        "decays_on_turn": current_turn + decay_turns,
    })
    categories = set(record.get("categories", []) or [])
    categories.add("treaty_breach")
    record["categories"] = sorted(categories)
    record["last_turn"] = current_turn
    history[key] = record
    world.betrayal_history = history

    active_after = _get_active_betrayal_strike_count(world, actor, victim)
    return {
        "recorded": True,
        "active_before": active_before,
        "active_after": active_after,
        "triggered_hard_reject": active_before < 3 <= active_after,
    }


def _record_betrayal_strikes(
    world,
    *,
    actor: str,
    victim: str,
    severity: str,
    episode_id: str,
    count: int,
    decay_multiplier: float = 1.0,
) -> Dict:
    """Persist a DG-4 victim-strike bundle without changing the public shape."""
    active_before = _get_active_betrayal_strike_count(world, actor, victim)
    added = 0
    triggered = False
    last_record = {
        "recorded": False,
        "active_before": active_before,
        "active_after": active_before,
        "triggered_hard_reject": False,
    }
    for _ in range(max(0, int(count))):
        last_record = _record_betrayal_strike(
            world,
            actor=actor,
            victim=victim,
            severity=severity,
            episode_id=episode_id,
            decay_multiplier=decay_multiplier,
        )
        if last_record.get("recorded"):
            added += 1
        triggered = triggered or bool(last_record.get("triggered_hard_reject"))
    active_after = _get_active_betrayal_strike_count(world, actor, victim)
    return {
        "recorded": added > 0,
        "strikes_added": int(added),
        "active_before": int(active_before),
        "active_after": int(active_after),
        "triggered_hard_reject": bool(triggered),
        "last_record": last_record,
    }


def _emit_hard_reject_posture_triggered(
    world,
    *,
    perpetrator: str,
    victim: str,
    episode_id: str,
) -> None:
    """Emit the hard-reject transition once a strike bundle crosses 3."""
    from backend.game_logic.dispatch import queue_dispatch_event

    payload = {
        "perpetrator_nation": perpetrator,
        "victim_nation": victim,
        "trigger_strike_episode_id": episode_id,
        "episode_id": episode_id,
        "turn": int(world.current_turn),
        "speaker_attribution": "foreign_office",
    }
    queue_dispatch_event(
        world, "hard_reject_posture_triggered", payload, "partial_on_nation",
    )
    event = dict(payload)
    event["type"] = "hard_reject_posture_triggered"
    world.log_event(event)
    _emit_commitments_notification(
        world, "hard_reject_posture_triggered", payload,
    )


def _process_betrayal_decay(world) -> None:
    """Decay matured bilateral betrayal strikes once a non-war treaty exists."""
    from backend.game_logic.dispatch import queue_dispatch_event

    history = getattr(world, "betrayal_history", {}) or {}
    if not history:
        return

    current_turn = int(getattr(world, "current_turn", 0))
    updated = {}
    for key, record in history.items():
        actor, victim = key.split("|", 1)
        strikes = list(record.get("strikes", []) or [])
        active_before = len([
            strike for strike in strikes
            if int(strike.get("decays_on_turn", current_turn + 1) or current_turn + 1) >= current_turn
        ])
        if world.get_diplomatic_state(actor, victim) in _NON_WAR_TREATY_STATES:
            matured = [
                strike for strike in strikes
                if int(strike.get("decays_on_turn", current_turn + 1) or current_turn + 1) <= current_turn
            ]
            if matured:
                oldest = min(matured, key=lambda strike: int(strike.get("decays_on_turn", current_turn)))
                strikes.remove(oldest)
        if strikes:
            record["strikes"] = strikes
            updated[key] = record
        elif record.get("grievance_flags"):
            # B-B4 grievance flags do not decay with their originating
            # strikes. Keep a grievance-only record until the grievance
            # variant of Make Amends removes the final flag.
            record["strikes"] = []
            record["grievance_flags"] = list(
                record.get("grievance_flags", []) or []
            )
            categories = set(record.get("categories", []) or [])
            categories.discard("treaty_breach")
            categories.add("grievance")
            record["categories"] = sorted(categories)
            updated[key] = record
        active_after = len([
            strike for strike in strikes
            if int(strike.get("decays_on_turn", current_turn + 1) or current_turn + 1) > current_turn
        ])
        if active_before >= 3 and active_after <= 2:
            episode_id = ""
            if strikes:
                episode_id = str(strikes[-1].get("episode_id", ""))
            payload = {
                "type": "hard_reject_posture_cleared",
                "perpetrator_nation": actor,
                "victim_nation": victim,
                "episode_id": episode_id,
                "turn": current_turn,
                "speaker_attribution": "foreign_office",
            }
            world.log_event(payload)
            queue_dispatch_event(world, "hard_reject_posture_cleared", {
                "perpetrator_nation": actor,
                "victim_nation": victim,
                "episode_id": episode_id,
                "turn": current_turn,
                "speaker_attribution": "foreign_office",
            }, "partial_on_nation")
            _emit_commitments_notification(
                world, "hard_reject_posture_cleared", payload,
            )
    world.betrayal_history = updated


def _get_actor_personality(world, nation: str) -> str:
    """Best-effort diplomatic personality for the actor's court."""
    diplomats = getattr(world, 'diplomats', {})
    diplomat = diplomats.get(nation)
    if diplomat is None:
        return ""
    return str(getattr(diplomat, 'personality', "") or "")


def _classify_witness_scope(world, witness: str, breaker: str, injured_party: str) -> str:
    """Resolve a single witness's scope_reason using §8.4 precedence.

    Returns one of WITNESS_SCOPE_* constants, or empty string if the nation
    is not positioned to react politically to the rupture. The first matching
    role in precedence order wins (ally > rival > shared_enemy > region_observer).
    """
    # ally: military alliance with the injured party
    if world.get_diplomatic_state(witness, injured_party) in ("DEFENSIVE_ALLIANCE", "ALLIANCE"):
        return WITNESS_SCOPE_ALLY

    # rival: currently at war with the breaker (v0.1 proxy)
    if world.is_at_war(witness, breaker):
        return WITNESS_SCOPE_RIVAL

    # shared_enemy: witness is at war with a nation the injured party is also at war with
    for other in world.get_active_nations():
        if other in (witness, breaker, injured_party):
            continue
        if world.is_at_war(witness, other) and world.is_at_war(injured_party, other):
            return WITNESS_SCOPE_SHARED_ENEMY

    for b in _get_live_bargains(world):
        if (
            _live_bargain_matches_breach_context(world, b, breaker, injured_party)
            and (b.get("beneficiary") == witness or b.get("promiser") == witness)
        ):
            return WITNESS_SCOPE_REGION_OBSERVER

    return ""


def _get_breach_witness_scope(world, breaker_nation: str, injured_party: str) -> Dict:
    """Resolve the witness set for a rupture with per-witness scope_reasons.

    Returns:
        {
            "witnesses": [{"nation": str, "scope_reason": str}, ...],
            "dominant_scope": str,            # first role present in precedence order
            "label": str,                     # audience-size flavor label
            "count": int,
            "sample": [str, ...],             # legacy flat nation list (back-compat)
        }
    """
    witnesses = []  # list of {"nation", "scope_reason"}
    for nation in world.get_active_nations():
        if nation in (breaker_nation, injured_party):
            continue
        scope_reason = _classify_witness_scope(world, nation, breaker_nation, injured_party)
        if scope_reason:
            witnesses.append({"nation": nation, "scope_reason": scope_reason})

    # Dominant scope follows the spec precedence (ally > rival > shared_enemy > region_observer).
    dominant_scope = ""
    for role in WITNESS_SCOPE_PRECEDENCE:
        if any(w["scope_reason"] == role for w in witnesses):
            dominant_scope = role
            break

    # Audience-size label kept for flavor; no longer overloaded as scope_reason.
    player_nation = getattr(world, 'player_nation', 'France')
    if breaker_nation == player_nation or injured_party == player_nation or len(witnesses) >= 3:
        label = "continental"
    elif witnesses:
        label = "aligned courts"
    else:
        label = "private court"

    return {
        "witnesses": witnesses,
        "dominant_scope": dominant_scope,
        "label": label,
        "count": int(len(witnesses)),
        "sample": [w["nation"] for w in witnesses[:4]],
    }


# ────────────────────────────────────────────────────────────────────────────
# B-B4 / §8.8.3 — DG-4 defensive-refusal witness scope (wider than §8.4)
# ────────────────────────────────────────────────────────────────────────────


def _classify_dg4_refused_defensive_witness_scope(
    world, witness: str, breaker: str, victim: str,
) -> str:
    """Resolve a single witness's scope_reason for a DG-4 defensive refusal.

    Precedence per §8.8.3: `ally > rival > treaty_partner_of_breaker >
    shared_enemy > region_observer`. The `ally` / `rival` / `shared_enemy`
    predicates are reused from the base `_classify_witness_scope`; only
    the new `treaty_partner_of_breaker` predicate is introduced here.

    Returns a WITNESS_SCOPE_* constant, or empty string when the witness
    has no qualifying role. Single-reason rule: the first matching role
    in precedence order wins — no witness appears twice in the scope list.
    """
    # ally: military alliance with the injured party (highest precedence)
    if world.get_diplomatic_state(witness, victim) in (
        "DEFENSIVE_ALLIANCE", "ALLIANCE",
    ):
        return WITNESS_SCOPE_ALLY

    # rival: currently at war with the breaker (v0.1 proxy)
    if world.is_at_war(witness, breaker):
        return WITNESS_SCOPE_RIVAL

    # treaty_partner_of_breaker: any active treaty with the breaker
    # (§8.8.3 "wider scope" insertion).
    breaker_state = world.get_diplomatic_state(witness, breaker)
    if breaker_state in _ACTIVE_TREATY_STATES_FOR_DG4_WITNESS:
        return WITNESS_SCOPE_TREATY_PARTNER_OF_BREAKER

    # shared_enemy: witness + victim share an active enemy
    for other in world.get_active_nations():
        if other in (witness, breaker, victim):
            continue
        if world.is_at_war(witness, other) and world.is_at_war(victim, other):
            return WITNESS_SCOPE_SHARED_ENEMY

    for b in _get_live_bargains(world):
        if (
            _live_bargain_matches_breach_context(world, b, breaker, victim)
            and (b.get("beneficiary") == witness or b.get("promiser") == witness)
        ):
            return WITNESS_SCOPE_REGION_OBSERVER

    return ""


def _get_dg4_refused_defensive_witness_scope(
    world, breaker: str, victim: str,
) -> Dict:
    """Resolve the witness set for a `call_to_arms_refused_defensive` episode.

    Parallel to `_get_breach_witness_scope` but uses the DG-4 precedence
    from §8.8.3 (see `DG4_WITNESS_SCOPE_PRECEDENCE`). The shape matches
    `_get_breach_witness_scope` so downstream consumers (dispatch emit,
    C3 presentation) can treat the two as interchangeable payloads.

    Witness count growth (§7.7 / §8.8.3 scale note): at 13 nations the
    wider scope lifts typical witness lists from ~2-4 to ~6-9. Callers
    that loop over witnesses must stay O(active_nations).
    """
    witnesses = []
    for nation in world.get_active_nations():
        if nation in (breaker, victim):
            continue
        scope_reason = _classify_dg4_refused_defensive_witness_scope(
            world, nation, breaker, victim,
        )
        if scope_reason:
            witnesses.append({"nation": nation, "scope_reason": scope_reason})

    dominant_scope = ""
    for role in DG4_WITNESS_SCOPE_PRECEDENCE:
        if any(w["scope_reason"] == role for w in witnesses):
            dominant_scope = role
            break

    player_nation = getattr(world, 'player_nation', 'France')
    if breaker == player_nation or victim == player_nation or len(witnesses) >= 3:
        label = "continental"
    elif witnesses:
        label = "aligned courts"
    else:
        label = "private court"

    return {
        "witnesses": witnesses,
        "dominant_scope": dominant_scope,
        "label": label,
        "count": int(len(witnesses)),
        "sample": [w["nation"] for w in witnesses[:4]],
    }


def _get_dg4_refused_offensive_witness_scope(
    world, breaker: str, victim: str,
) -> Dict:
    """Resolve offensive-refusal witnesses from treaty partners of either side."""
    witnesses = []
    for nation in world.get_active_nations():
        if nation in (breaker, victim):
            continue
        scope_reason = ""
        if (
            world.get_diplomatic_state(nation, victim) in ("DEFENSIVE_ALLIANCE", "ALLIANCE")
            or world.get_diplomatic_state(nation, breaker) in ("DEFENSIVE_ALLIANCE", "ALLIANCE")
        ):
            scope_reason = WITNESS_SCOPE_ALLY
        else:
            scope_reason = _classify_witness_scope(world, nation, breaker, victim)
        if scope_reason:
            witnesses.append({"nation": nation, "scope_reason": scope_reason})

    dominant_scope = ""
    for role in WITNESS_SCOPE_PRECEDENCE:
        if any(w["scope_reason"] == role for w in witnesses):
            dominant_scope = role
            break

    player_nation = getattr(world, 'player_nation', 'France')
    if breaker == player_nation or victim == player_nation or len(witnesses) >= 3:
        label = "continental"
    elif witnesses:
        label = "aligned courts"
    else:
        label = "private court"
    return {
        "witnesses": witnesses,
        "dominant_scope": dominant_scope,
        "label": label,
        "count": int(len(witnesses)),
        "sample": [w["nation"] for w in witnesses[:4]],
    }


def _classify_dg4_honored_costly_witness_scope(
    world, witness: str, honorer: str, victim: str,
) -> str:
    """Resolve one witness for a positive costly-honor episode."""
    if world.get_diplomatic_state(witness, victim) in (
        "DEFENSIVE_ALLIANCE", "ALLIANCE",
    ):
        return WITNESS_SCOPE_ALLY

    # rival: currently at war with the honorer (v0.1 proxy)
    if world.is_at_war(witness, honorer):
        return WITNESS_SCOPE_RIVAL

    honorer_state = world.get_diplomatic_state(witness, honorer)
    if honorer_state in _ACTIVE_TREATY_STATES_FOR_DG4_WITNESS:
        return WITNESS_SCOPE_TREATY_PARTNER_OF_HONORER

    for other in world.get_active_nations():
        if other in (witness, honorer, victim):
            continue
        if world.is_at_war(witness, other) and world.is_at_war(victim, other):
            return WITNESS_SCOPE_SHARED_ENEMY
    return ""


def _get_dg4_honored_costly_witness_scope(
    world, honorer: str, victim: str,
) -> Dict:
    """Resolve the wider witness set for `call_to_arms_honored_costly`."""
    witnesses = []
    for nation in world.get_active_nations():
        if nation in (honorer, victim):
            continue
        scope_reason = _classify_dg4_honored_costly_witness_scope(
            world, nation, honorer, victim,
        )
        if scope_reason:
            witnesses.append({"nation": nation, "scope_reason": scope_reason})

    precedence = (
        WITNESS_SCOPE_ALLY,
        WITNESS_SCOPE_RIVAL,
        WITNESS_SCOPE_TREATY_PARTNER_OF_HONORER,
        WITNESS_SCOPE_SHARED_ENEMY,
        WITNESS_SCOPE_REGION_OBSERVER,
    )
    dominant_scope = ""
    for role in precedence:
        if any(w["scope_reason"] == role for w in witnesses):
            dominant_scope = role
            break

    player_nation = getattr(world, 'player_nation', 'France')
    if honorer == player_nation or victim == player_nation or len(witnesses) >= 3:
        label = "continental"
    elif witnesses:
        label = "aligned courts"
    else:
        label = "private court"

    return {
        "witnesses": witnesses,
        "dominant_scope": dominant_scope,
        "label": label,
        "count": int(len(witnesses)),
        "sample": [w["nation"] for w in witnesses[:4]],
    }


def _get_honor_bias(world, nation: str) -> float:
    getter = getattr(world, "get_honor_bias", None)
    if callable(getter):
        try:
            return float(getter(nation) or 1.0)
        except (TypeError, ValueError):
            return 1.0
    return 1.0


def _cascade_profile(world) -> Dict:
    profile = getattr(world, "cascade_profile", None)
    return dict(profile or {})


def _cascade_float(world, key: str, default: float) -> float:
    try:
        return float(_cascade_profile(world).get(key, default))
    except (TypeError, ValueError):
        return float(default)


def _cascade_int(world, key: str, default: int) -> int:
    try:
        return int(_cascade_profile(world).get(key, default))
    except (TypeError, ValueError):
        return int(default)


def _cascade_nested_float(
    world,
    section: str,
    key: str,
    default: float,
) -> float:
    try:
        data = _cascade_profile(world).get(section, {}) or {}
        return float(data.get(key, default))
    except (AttributeError, TypeError, ValueError):
        return float(default)


def _cascade_nested_int(
    world,
    section: str,
    key: str,
    default: int,
) -> int:
    try:
        data = _cascade_profile(world).get(section, {}) or {}
        return int(data.get(key, default))
    except (AttributeError, TypeError, ValueError):
        return int(default)


def _defensive_refusal_severity_multiplier(world) -> float:
    return _cascade_float(
        world,
        "defensive_refusal_severity_multiplier",
        DG4_DEFENSIVE_REFUSAL_SEVERITY_MULTIPLIER,
    )


def _anti_renewal_window_turns(world) -> int:
    return max(
        1,
        _cascade_int(world, "anti_renewal_window_turns", ANTI_RENEWAL_COOLDOWN_TURNS),
    )


def _oathbreaker_window_turns(world) -> int:
    return max(
        1,
        _cascade_nested_int(
            world, "oathbreaker_posture", "window_turns",
            DG4_OATHBREAKER_WINDOW_TURNS,
        ),
    )


def _oathbreaker_refusals_required(world) -> int:
    return max(
        1,
        _cascade_nested_int(
            world, "oathbreaker_posture", "refusals_required",
            DG4_OATHBREAKER_REFUSALS_REQUIRED,
        ),
    )


def _oathbreaker_auto_reject_turns(world) -> int:
    return max(
        1,
        _cascade_nested_int(
            world, "oathbreaker_posture", "auto_reject_ally_proposals_turns",
            DG4_OATHBREAKER_AUTO_REJECT_TURNS,
        ),
    )


def _impossibility_power_ratio(world) -> float:
    return _cascade_nested_float(
        world,
        "impossibility_threshold",
        "power_ratio",
        DG4_IMPOSSIBLE_POWER_RATIO,
    )


def _impossibility_losing_war_floor(world) -> int:
    return _cascade_nested_int(
        world,
        "impossibility_threshold",
        "losing_war_score_floor",
        -40,
    )


def _impossibility_capital_threat_enabled(world) -> bool:
    data = _cascade_profile(world).get("impossibility_threshold", {}) or {}
    return bool(data.get("capital_threat_auto_impossible", True))


def _dg4_scale_components(
    world,
    nation: str,
    call_context: Optional[Dict] = None,
) -> Dict[str, float]:
    """Resolve DG-4 severity scale factors from authored and call-context data."""
    call_context = dict(call_context or {})
    honor_bias = _get_honor_bias(world, nation)

    tier_nation = (
        call_context.get("enemy")
        or call_context.get("aggressor")
        or call_context.get("caller")
        or ""
    )
    tier_getter = getattr(world, "get_power_tier", None)
    tier = "secondary"
    if callable(tier_getter) and tier_nation:
        tier = tier_getter(str(tier_nation)) or "secondary"
    power_tier_multiplier = {
        "major": 1.15,
        "secondary": 1.0,
        "minor": 0.9,
    }.get(str(tier), 1.0)

    exposure_multiplier = 1.0
    ratio = float(call_context.get("aggressor_power_ratio", 0) or 0)
    if ratio >= 2.0:
        exposure_multiplier += 0.15
    elif ratio >= 1.25:
        exposure_multiplier += 0.08
    if call_context.get("capital_threat"):
        exposure_multiplier += 0.15
    if call_context.get("losing_other_war"):
        exposure_multiplier += 0.10
    exposure_multiplier = min(1.35, exposure_multiplier)

    return {
        "honor_bias": float(honor_bias),
        "power_tier_multiplier": float(power_tier_multiplier),
        "war_exposure_multiplier": float(exposure_multiplier),
        "total_multiplier": float(
            honor_bias * power_tier_multiplier * exposure_multiplier
        ),
    }


def _scaled_dg4_delta(
    world,
    nation: str,
    event_type: str,
    effect_key: str,
    call_context: Optional[Dict] = None,
) -> int:
    effects = DG4_EPISODE_EFFECTS.get(event_type, {})
    base = int(effects.get(effect_key, 0) or 0)
    multiplier = float(effects.get("severity_multiplier", 1.0) or 1.0)
    if event_type == DG4_EVENT_REFUSED_DEFENSIVE:
        multiplier = _defensive_refusal_severity_multiplier(world)
    scale = _dg4_scale_components(world, nation, call_context)
    return int(round(base * multiplier * scale["total_multiplier"]))


def _snapshot_defensive_refusal_coalition_partners(
    world,
    breaker: str,
    victim: str,
) -> List[str]:
    """Snapshot victim treaty partners at the moment of a defensive refusal."""
    partners: List[str] = []
    qualifying_states = {
        "OPEN_BORDERS",
        "NON_AGGRESSION",
        "DEFENSIVE_ALLIANCE",
        "ALLIANCE",
        "VASSAL",
    }
    active_treaties = getattr(world, "active_treaties", {}) or {}
    for nation in world.get_active_nations():
        if nation in (breaker, victim):
            continue
        pair_key = world._make_diplo_key(nation, victim)
        has_treaty = pair_key in active_treaties
        state = world.get_diplomatic_state(nation, victim)
        if has_treaty or state in qualifying_states:
            partners.append(nation)
    return sorted(partners)


def _emit_commitments_notification(world, event_type: str, payload: Dict) -> None:
    """Emit the commitments notice rail event from the shared routing table."""
    try:
        from backend.game_logic.commitments_routing import (
            commitments_label,
            commitments_notice_details,
            commitments_priority,
            format_commitments_notice,
        )
        from backend.notifications import create_notification, NotificationPriority

        priority_name = commitments_priority(event_type, payload)
        priority = getattr(NotificationPriority, priority_name, NotificationPriority.NORMAL)
        world.notifications.add(create_notification(
            event_type,
            priority,
            commitments_label(event_type, payload),
            format_commitments_notice(event_type, payload),
            int(getattr(world, "current_turn", 0)),
            details=commitments_notice_details(event_type, payload),
        ))
    except Exception:
        return


def _apply_reliability_delta(world, nation: str, delta: int) -> tuple[int, int]:
    reliability = getattr(world, "diplomatic_reliability", {}) or {}
    before = int(reliability.get(nation, 0) or 0)
    after = max(-100, min(100, before + int(delta)))
    reliability[nation] = after
    world.diplomatic_reliability = reliability
    return before, after


def _queue_dg4_witness_events(
    world,
    *,
    episode_id: str,
    event_type: str,
    actor: str,
    victim: str,
    witnesses: List[Dict],
    relation_delta: int,
) -> None:
    """Apply and dispatch per-witness DG-4 relation effects."""
    from backend.game_logic.dispatch import queue_dispatch_event

    for witness in witnesses:
        witness_nation = witness["nation"]
        if relation_delta:
            world.modify_nation_relation(witness_nation, actor, relation_delta)
        queue_dispatch_event(
            world,
            "witness_strike_recorded",
            {
                "episode_id": episode_id,
                "victim_nation": victim,
                "perpetrator_nation": actor,
                "witness_nation": witness_nation,
                "scope_reason": witness["scope_reason"],
                "relation_delta": int(relation_delta),
                "reliability_delta": 0,
                "source_episode_type": event_type,
                "turn": int(world.current_turn),
            },
            "partial_on_nation",
        )


# ────────────────────────────────────────────────────────────────────────────
# B-B4 / §8.8.7 — anti-renewal cooldown after a defensive refusal
# ────────────────────────────────────────────────────────────────────────────
# A defensive refusal blocks new ALLIANCE / DEFENSIVE_ALLIANCE ratification
# between the refuser-victim pair for an authored window. The gate is
# mechanical (not advisory) — the acceptance-formula score is clamped to
# reject so the proposal is blocked outright. NON_AGGRESSION / OPEN_BORDERS
# / PEACE remain available during the window per §8.8.7.

ANTI_RENEWAL_COOLDOWN_TURNS = 15  # §8.8.7 candidate authored window


def _set_anti_renewal_cooldown(world, nation_a: str, nation_b: str) -> int:
    """Arm the anti-renewal cooldown for the (nation_a, nation_b) pair.

    Sets the pair expiry from the authored cascade profile window.
    Returns the expiry turn for caller bookkeeping.
    """
    pair_key = world._make_diplo_key(nation_a, nation_b)
    expiry = int(getattr(world, "current_turn", 0)) + _anti_renewal_window_turns(world)
    cooldown = dict(getattr(world, "anti_renewal_cooldown", {}) or {})
    cooldown[pair_key] = expiry
    world.anti_renewal_cooldown = cooldown
    return expiry


def is_anti_renewal_active(world, nation_a: str, nation_b: str) -> bool:
    """True when the (nation_a, nation_b) pair is within an anti-renewal window.

    Used by `calculate_acceptance` to gate deep-treaty proposals between
    the refuser and the abandoned victim. Self-pair always returns False.
    """
    if not nation_a or not nation_b or nation_a == nation_b:
        return False
    pair_key = world._make_diplo_key(nation_a, nation_b)
    expiry = int(
        (getattr(world, "anti_renewal_cooldown", {}) or {}).get(pair_key, 0) or 0
    )
    return expiry > int(getattr(world, "current_turn", 0))


def get_anti_renewal_turns_remaining(world, nation_a: str, nation_b: str) -> int:
    """Return turns remaining on an anti-renewal window (0 when inactive).

    Exposed for UI copy so the proposal flow can surface the remaining
    turns per §8.8.7 "the UI surfaces the remaining turns."
    """
    if not nation_a or not nation_b or nation_a == nation_b:
        return 0
    pair_key = world._make_diplo_key(nation_a, nation_b)
    expiry = int(
        (getattr(world, "anti_renewal_cooldown", {}) or {}).get(pair_key, 0) or 0
    )
    remaining = expiry - int(getattr(world, "current_turn", 0))
    return max(0, remaining)


def has_oathbreaker_posture(world, nation: str) -> bool:
    """True while a nation is in DG-4 habitual-refusal posture."""
    record = (getattr(world, "oathbreaker_posture", {}) or {}).get(nation, {})
    expires = int(record.get("expires_on_turn", 0) or 0)
    return expires > int(getattr(world, "current_turn", 0))


def is_oathbreaker_auto_reject_active(world, nation: str) -> bool:
    """True while oathbreaker posture mechanically blocks deep-treaty proposals."""
    record = (getattr(world, "oathbreaker_posture", {}) or {}).get(nation, {})
    until = int(record.get("auto_reject_until_turn", 0) or 0)
    return until > int(getattr(world, "current_turn", 0))


def get_oathbreaker_turns_remaining(world, nation: str) -> int:
    record = (getattr(world, "oathbreaker_posture", {}) or {}).get(nation, {})
    until = int(record.get("auto_reject_until_turn", 0) or 0)
    return max(0, until - int(getattr(world, "current_turn", 0)))


def _emit_oathbreaker_event(
    world,
    event_type: str,
    *,
    nation: str,
    episode_id: str,
    reason: str = "",
    record: Dict = None,
) -> None:
    from backend.game_logic.dispatch import queue_dispatch_event

    payload = {
        "nation": nation,
        "episode_id": episode_id,
        "reason": reason,
        "turn": int(world.current_turn),
        "speaker_attribution": "foreign_office",
    }
    if record:
        payload.update({
            "expires_on_turn": int(record.get("expires_on_turn", 0) or 0),
            "auto_reject_until_turn": int(
                record.get("auto_reject_until_turn", 0) or 0
            ),
            "refusal_episode_ids": list(record.get("refusal_episode_ids", []) or []),
        })
    event = dict(payload)
    event["type"] = event_type
    world.log_event(event)
    queue_dispatch_event(world, event_type, payload, "partial_on_nation")


def _recent_defensive_refusal_episode_ids(world, nation: str) -> List[str]:
    current_turn = int(getattr(world, "current_turn", 0))
    earliest = current_turn - _oathbreaker_window_turns(world)
    ids = []
    for event in getattr(world, "event_log", []) or []:
        if event.get("type") != DG4_EVENT_REFUSED_DEFENSIVE:
            continue
        if event.get("breaker") != nation:
            continue
        turn = int(event.get("turn", 0) or 0)
        if turn >= earliest:
            ids.append(str(event.get("episode_id", "") or ""))
    return [eid for eid in ids if eid]


def _record_oathbreaker_refusal(world, breaker: str, episode_id: str) -> None:
    """Trigger or extend oathbreaker posture after habitual defensive refusals."""
    recent_ids = _recent_defensive_refusal_episode_ids(world, breaker)
    if episode_id not in recent_ids:
        recent_ids.append(episode_id)
    refusals_required = _oathbreaker_refusals_required(world)
    if len(recent_ids) < refusals_required:
        return

    current_turn = int(getattr(world, "current_turn", 0))
    posture = dict(getattr(world, "oathbreaker_posture", {}) or {})
    was_active = has_oathbreaker_posture(world, breaker)
    record = {
        "triggered_turn": int(
            (posture.get(breaker) or {}).get("triggered_turn", current_turn)
        ),
        "expires_on_turn": current_turn + _oathbreaker_window_turns(world),
        "auto_reject_until_turn": current_turn + _oathbreaker_auto_reject_turns(world),
        "last_refusal_turn": current_turn,
        "refusal_episode_ids": recent_ids[-refusals_required:],
    }
    posture[breaker] = record
    world.oathbreaker_posture = posture
    if not was_active:
        _emit_oathbreaker_event(
            world,
            "oathbreaker_posture_triggered",
            nation=breaker,
            episode_id=episode_id,
            reason="habitual_defensive_refusal",
            record=record,
        )


def _clear_oathbreaker_posture(
    world,
    nation: str,
    *,
    episode_id: str,
    reason: str,
) -> bool:
    posture = dict(getattr(world, "oathbreaker_posture", {}) or {})
    if nation not in posture:
        return False
    posture.pop(nation, None)
    world.oathbreaker_posture = posture
    _emit_oathbreaker_event(
        world,
        "oathbreaker_posture_cleared",
        nation=nation,
        episode_id=episode_id,
        reason=reason,
    )
    return True


def _process_oathbreaker_decay(world) -> None:
    posture = dict(getattr(world, "oathbreaker_posture", {}) or {})
    if not posture:
        return
    current_turn = int(getattr(world, "current_turn", 0))
    for nation, record in list(posture.items()):
        expires = int(record.get("expires_on_turn", 0) or 0)
        if expires <= current_turn:
            _clear_oathbreaker_posture(
                world,
                nation,
                episode_id=str((record.get("refusal_episode_ids") or [""])[-1]),
                reason="window_elapsed",
            )


def _allocate_episode_id(world, prefix: str = "ep") -> str:
    """Mint a fresh deterministic episode_id for a root-cause diplomatic trigger.

    Used to group consequences of one explicit action (declare_war + cascaded
    breaches, paradox resolution + forced downgrade, etc.) under a single key
    for C3 aftermath callbacks and witness-strike collapse (RELIABILITY_COMMITMENTS_SPEC §6.5).
    """
    counter = int(getattr(world, 'next_episode_id', 1) or 1)
    world.next_episode_id = counter + 1
    return f"{prefix}_{int(world.current_turn)}_{counter:04d}"


def _resolve_end_reason(end_reason_action: str, fault_nation: str, breaker_nation: str) -> str:
    """Derive end_reason_family from action + fault attribution (§9.9)."""
    if fault_nation and fault_nation != breaker_nation:
        # Someone other than the breaker is at fault -> no perpetrator penalty.
        return END_REASON_FAMILY_OBSOLESCENCE_OR_EXTERNAL
    if end_reason_action == "cascade_forced":
        # Cascade is external to the cascaded nation's choice -> no penalty.
        return END_REASON_FAMILY_OBSOLESCENCE_OR_EXTERNAL
    if end_reason_action == "defensive_refusal":
        # §8.8.7a: the refusal episode carries the fault attribution (strike +
        # grievance + reliability penalty land on the episode itself). The
        # parallel `diplomatic_treaty_broken` event emitted for UI / cascade
        # plumbing rides its own dedicated family so presentation can tell
        # "refused and thereby ended the alliance" apart from a generic
        # voluntary breach.
        return END_REASON_FAMILY_DEFENSIVE_REFUSAL_TERMINATION
    return END_REASON_FAMILY_FRENCH_BREACH


def get_treaty_breach_preview(
    world,
    breaker_nation: str,
    other_nation: str,
    treaty: Dict = None,
    reason_family: str = None,              # accepted as end_reason_family OR action for back-compat
    end_reason_action: str = None,
    fault_nation: str = None,
    episode_id: str = None,
) -> Dict:
    """Build deterministic breach metadata before the state changes.

    Args:
        reason_family: legacy argument — accepts either an end_reason_action value
            (`manual_break`, `war_declaration`, `paradox_choice`, `cascade_forced`)
            or an explicit end_reason_family value. For back-compat, action-shaped
            values are promoted to end_reason_action and family is re-derived.
        end_reason_action: explicit action axis (what the actor did).
        fault_nation: who the rupture should be blamed on (defaults to breaker).
        episode_id: root-cause identifier for this rupture (generated if absent).
    """
    # Normalize the split: callers that still pass `reason_family` as an action label
    # get routed into end_reason_action; the family is derived from action + fault.
    action = end_reason_action or reason_family or "manual_break"
    if action not in _REASON_ACTION_PHRASES:
        action = "manual_break"
    effective_fault = fault_nation or breaker_nation
    family = _resolve_end_reason(action, effective_fault, breaker_nation)

    pair_key = world._make_diplo_key(breaker_nation, other_nation)
    treaty_data = treaty or getattr(world, 'active_treaties', {}).get(pair_key, {})
    current_state = world.get_diplomatic_state(breaker_nation, other_nation)
    treaty_type = str(
        treaty_data.get("type")
        or current_state.lower()
        or "treaty"
    )
    turn_signed = int(treaty_data.get("turn_signed") or 0)
    turns_honored = max(0, int(world.current_turn) - turn_signed) if turn_signed else 0

    reliability = getattr(world, 'diplomatic_reliability', {})
    reliability_before = int(reliability.get(breaker_nation, 0))

    # Reliability penalty applies only on perpetrator-fault ruptures.
    intended_delta = -10 if family == END_REASON_FAMILY_FRENCH_BREACH else 0
    reliability_after = max(-100, reliability_before + intended_delta)
    applied_delta = reliability_after - reliability_before

    witness_scope = _get_breach_witness_scope(world, breaker_nation, other_nation)
    active_betrayal_strikes_before = _get_active_betrayal_strike_count(
        world,
        breaker_nation,
        other_nation,
    )
    active_betrayal_strikes_after = active_betrayal_strikes_before
    if family == END_REASON_FAMILY_FRENCH_BREACH:
        active_betrayal_strikes_after += 1
    would_trigger_hard_reject = (
        family == END_REASON_FAMILY_FRENCH_BREACH
        and active_betrayal_strikes_before < 3 <= active_betrayal_strikes_after
    )

    return {
        "pair_key": pair_key,
        "breaker": breaker_nation,
        "injured_party": other_nation,
        "fault_nation": effective_fault,
        "episode_id": episode_id or _allocate_episode_id(world),
        "treaty_type": treaty_type,
        "treaty_type_display": _proposal_display_name(treaty_type),
        "previous_state": current_state,
        "turn_signed": turn_signed,
        "turns_honored": int(turns_honored),
        "reliability_before": reliability_before,
        "reliability_after": reliability_after,
        "intended_reliability_delta": int(intended_delta),
        "applied_reliability_delta": int(applied_delta),
        "witnesses": witness_scope["witnesses"],
        "dominant_witness_scope": witness_scope["dominant_scope"],
        "witness_scope_label": witness_scope["label"],
        "witness_scope": witness_scope["label"],  # legacy alias (M-6 back-compat)
        "witness_count": witness_scope["count"],
        "witness_sample": witness_scope["sample"],
        "actor_personality": _get_actor_personality(world, breaker_nation),
        "end_reason_family": family,
        "end_reason_action": action,
        "reason_phrase": _REASON_ACTION_PHRASES.get(action, "under pressure"),
        "breach_severity": _BREACH_SEVERITY_BY_TREATY.get(treaty_type, "medium"),
        "active_betrayal_strikes_before": int(active_betrayal_strikes_before),
        "active_betrayal_strikes_after": int(active_betrayal_strikes_after),
        "would_trigger_hard_reject": bool(would_trigger_hard_reject),
        "hard_reject_target_nation": other_nation,
    }


def preview_war_declaration(
    world,
    aggressor: str,
    target: str,
    casus_belli: bool = False,
    episode_id: str = None,
) -> Dict:
    """Forecast the political consequences of declaring war without mutating state."""
    penalty_factor = 0.5 if casus_belli else 1.0
    defensive_joiners = []
    offensive_joiners = []
    for nation in world.get_active_nations():
        if nation in (aggressor, target):
            continue
        if world.get_diplomatic_state(nation, target) in ("DEFENSIVE_ALLIANCE", "ALLIANCE"):
            if not world.is_at_war(nation, aggressor):
                defensive_joiners.append(nation)
        if world.get_diplomatic_state(nation, aggressor) == "ALLIANCE":
            if not world.is_at_war(nation, target):
                offensive_joiners.append(nation)

    pair_key = world._make_diplo_key(aggressor, target)
    treaty = getattr(world, 'active_treaties', {}).get(pair_key)
    current_state = world.get_diplomatic_state(aggressor, target)
    breach_preview = None
    if treaty or current_state in COMMITMENT_STATES:
        breach_preview = get_treaty_breach_preview(
            world,
            aggressor,
            target,
            treaty=treaty,
            end_reason_action="war_declaration",
            fault_nation=aggressor,
            episode_id=episode_id,
        )

    return {
        "direct_relation_penalty": int(-30 * penalty_factor),
        "indirect_relation_penalty": int(-15 * penalty_factor),
        "war_threat": 10 if casus_belli else 20,
        "breach_preview": breach_preview,
        "defensive_joiners": defensive_joiners,
        "offensive_joiners": offensive_joiners,
    }


def _build_breach_warnings(breach_preview: Dict, war_preview: Dict = None) -> List[Dict]:
    """Emit a structured `warnings[]` list per RELIABILITY_COMMITMENTS_SPEC §12.2.

    Presentation consumes these sorted by severity (critical>high>medium>low)
    with the stable category tie-break order:
    paradox>hard_reject>bargain>betrayal>hegemony>peace_conflict.
    """
    warnings: List[Dict] = []
    if not breach_preview:
        return warnings

    severity = "high" if breach_preview.get("breach_severity") == "high" else "medium"
    warnings.append({
        "severity": severity,
        "category": "betrayal",
        "text": (
            f"Reliability would fall from {breach_preview['reliability_before']} "
            f"to {breach_preview['reliability_after']}."
        ),
    })

    if breach_preview.get("would_trigger_hard_reject"):
        target = breach_preview.get("hard_reject_target_nation", breach_preview.get("injured_party", "this court"))
        warnings.append({
            "severity": "critical",
            "category": "hard_reject",
            "text": (
                f"{target} would mark this as a third remembered betrayal and close the door "
                "to deep treaties."
            ),
        })

    if war_preview:
        defensive_joiners = war_preview.get("defensive_joiners", [])
        if defensive_joiners:
            warnings.append({
                "severity": "medium",
                "category": "peace_conflict",
                "text": f"Likely defenders: {', '.join(defensive_joiners)}.",
            })
        offensive_joiners = war_preview.get("offensive_joiners", [])
        if offensive_joiners:
            warnings.append({
                "severity": "medium",
                "category": "peace_conflict",
                "text": f"Likely co-belligerents: {', '.join(offensive_joiners)}.",
            })

    return _sort_structured_warnings(warnings)


def _record_treaty_breach(
    world,
    breach_preview: Dict,
    new_state: str,
    trigger_context: Dict = None,
    suppress_notification: bool = False,
    suppress_dispatch_event: bool = False,
) -> None:
    """Emit the remembered political event for a treaty breach.

    Args:
        suppress_notification: skip the TREATY_BROKEN notification when the
            caller is already emitting a louder one (e.g. WAR_DECLARED).
            Spec §8.4 no-duplicate-surface rule.
        suppress_dispatch_event: skip the `diplomatic_treaty_broken` dispatch
            event when the caller will emit `diplomatic_war_declared` with
            `breached_treaty` in the same episode.
    """
    from backend.game_logic.dispatch import queue_dispatch_event
    from backend.game_logic.commitments_routing import (
        commitments_label,
        commitments_notice_details,
        commitments_priority,
        format_commitments_notice,
    )
    from backend.notifications import (
        create_notification, NotificationPriority, TREATY_BROKEN,
    )

    breaker_nation = breach_preview["breaker"]
    injured_party = breach_preview["injured_party"]
    treaty_type_display = breach_preview["treaty_type_display"]
    reason_phrase = breach_preview["reason_phrase"]
    episode_id = breach_preview.get("episode_id") or _allocate_episode_id(world)
    speaker_attribution = (
        "envoy"
        if breach_preview.get("end_reason_family") == END_REASON_FAMILY_FRENCH_BREACH
        else "foreign_office"
    )
    breach_preview["episode_id"] = episode_id

    world.log_event({
        "type": "diplomatic_treaty_broken",
        "breaker": breaker_nation,
        "other": injured_party,
        "injured_party": injured_party,
        "victim_nation": injured_party,
        "fault_nation": breach_preview["fault_nation"],
        "episode_id": episode_id,
        "treaty_type": breach_preview["treaty_type"],
        "treaty_type_display": treaty_type_display,
        "previous_state": breach_preview["previous_state"],
        "new_state": new_state,
        "turns_honored": breach_preview["turns_honored"],
        "reliability_before": breach_preview["reliability_before"],
        "reliability_after": breach_preview["reliability_after"],
        "intended_reliability_delta": breach_preview["intended_reliability_delta"],
        "applied_reliability_delta": breach_preview["applied_reliability_delta"],
        "witnesses": list(breach_preview["witnesses"]),
        "dominant_witness_scope": breach_preview["dominant_witness_scope"],
        "witness_scope_label": breach_preview["witness_scope_label"],
        "witness_scope": breach_preview["witness_scope"],  # legacy alias
        "witness_count": breach_preview["witness_count"],
        "witness_sample": breach_preview["witness_sample"],
        "actor_personality": breach_preview["actor_personality"],
        "end_reason_family": breach_preview["end_reason_family"],
        "end_reason_action": breach_preview["end_reason_action"],
        "reason_phrase": reason_phrase,
        "breach_severity": breach_preview["breach_severity"],
        "active_betrayal_strikes_before": int(breach_preview.get("active_betrayal_strikes_before", 0)),
        "active_betrayal_strikes_after": int(breach_preview.get("active_betrayal_strikes_after", 0)),
        "would_trigger_hard_reject": bool(breach_preview.get("would_trigger_hard_reject")),
        "trigger_context": trigger_context or {},
        "speaker_attribution": speaker_attribution,
    })

    if not suppress_notification:
        notice_payload = {
            "breaker": breaker_nation,
            "nation": breaker_nation,
            "other": injured_party,
            "injured_party": injured_party,
            "victim_nation": injured_party,
            "target": injured_party,
            "fault_nation": breach_preview["fault_nation"],
            "episode_id": episode_id,
            "treaty_type": breach_preview["treaty_type"],
            "treaty_type_display": treaty_type_display,
            "previous_state": breach_preview["previous_state"],
            "new_state": new_state,
            "reason_phrase": reason_phrase,
            "end_reason_family": breach_preview["end_reason_family"],
            "end_reason_action": breach_preview["end_reason_action"],
            "speaker_attribution": speaker_attribution,
            "speaker_target_nation": injured_party,
        }
        priority_name = commitments_priority(
            "diplomatic_treaty_broken", notice_payload,
        )
        world.notifications.add(create_notification(
            TREATY_BROKEN,
            getattr(NotificationPriority, priority_name, NotificationPriority.NORMAL),
            commitments_label("diplomatic_treaty_broken", notice_payload),
            format_commitments_notice("diplomatic_treaty_broken", notice_payload),
            int(world.current_turn),
            details=commitments_notice_details(
                "diplomatic_treaty_broken", notice_payload,
            ),
        ))

    if not suppress_dispatch_event:
        queue_dispatch_event(world, "diplomatic_treaty_broken", {
            "nation": breaker_nation,
            "target": injured_party,
            "victim_nation": injured_party,
            "treaty_type": treaty_type_display,
            "reason_phrase": reason_phrase,
            "episode_id": episode_id,
            "witness_scope": breach_preview["witness_scope"],
            "dominant_witness_scope": breach_preview["dominant_witness_scope"],
            "end_reason_family": breach_preview["end_reason_family"],
            "end_reason_action": breach_preview["end_reason_action"],
            "reliability_before": breach_preview["reliability_before"],
            "reliability_after": breach_preview["reliability_after"],
            "applied_reliability_delta": breach_preview["applied_reliability_delta"],
            "speaker_attribution": speaker_attribution,
        }, "partial_on_nation")

    # One witness_strike_recorded dispatch per witness (§C3 B2a cross-cutting
    # addition). Pre-strike-store: no relation_delta applied yet; payload is
    # emitted so C3 presentation can render witness-scoped reactions.
    #
    # B-B4 §8.8.7a cascade gate: when this breach is the termination cascade
    # driven by a `call_to_arms_refused_defensive` episode, the refusal emit
    # already produced per-witness events under its wider DG-4 scope
    # (§8.8.3). Emitting again here would duplicate witnesses on the same
    # `episode_id`. The refusal is the authoritative owner — skip cascade-
    # side emission. `_record_treaty_breach` for any *other* breach family
    # continues to emit per the existing §C3 contract.
    refusal_cascade = bool(
        trigger_context
        and trigger_context.get("refusal_episode_type") == "call_to_arms_refused_defensive"
    ) or (
        breach_preview.get("end_reason_family")
        == END_REASON_FAMILY_DEFENSIVE_REFUSAL_TERMINATION
    )
    if not refusal_cascade:
        for witness in breach_preview["witnesses"]:
            queue_dispatch_event(world, "witness_strike_recorded", {
                "episode_id": episode_id,
                "victim_nation": injured_party,
                "perpetrator_nation": breaker_nation,
                "witness_nation": witness["nation"],
                "scope_reason": witness["scope_reason"],
                "relation_delta": 0,
                "reliability_delta": 0,
                "turn": int(world.current_turn),
            }, "partial_on_nation")

    # Apply reliability penalty only when actor is at fault.
    # `applied_reliability_delta` is authoritative; for cascade / counterparty-
    # reversal / obsolescence it is 0 by construction.
    applied_delta = breach_preview.get("applied_reliability_delta", 0)
    if applied_delta != 0:
        reliability = getattr(world, 'diplomatic_reliability', {})
        reliability[breaker_nation] = breach_preview["reliability_after"]
        world.diplomatic_reliability = reliability

    if breach_preview.get("end_reason_family") == END_REASON_FAMILY_FRENCH_BREACH:
        betrayal_record = _record_betrayal_strike(
            world,
            actor=breaker_nation,
            victim=injured_party,
            severity=str(breach_preview.get("breach_severity", "medium")),
            episode_id=episode_id,
        )
        if betrayal_record.get("triggered_hard_reject"):
            _emit_hard_reject_posture_triggered(
                world,
                perpetrator=breaker_nation,
                victim=injured_party,
                episode_id=episode_id,
            )

    diplomatic_history = getattr(world, 'diplomatic_history', [])
    diplomatic_history.append({
        "turn": int(world.current_turn),
        "type": "treaty_broken",
        "nation": breaker_nation,
        "target": injured_party,
        "treaty_type": breach_preview["treaty_type"],
        "detail": breach_preview["end_reason_action"],
        "fault_family": breach_preview["end_reason_family"],
        "episode_id": episode_id,
    })
    if len(diplomatic_history) > 20:
        diplomatic_history[:] = diplomatic_history[-20:]
    world.diplomatic_history = diplomatic_history


# ═══════════════════════════════════════════════════════
# CENTRALIZED DIPLOMATIC STATE SETTER (R2)
# ═══════════════════════════════════════════════════════

def set_diplomatic_state(world, nation_a: str, nation_b: str,
                         new_state: str, reason: str = "") -> str:
    """Centralized diplomatic state change with automatic bookkeeping.

    Handles:
    - war_start_turns tracking (set on WAR entry, clear on WAR exit)
    - armistice_turns / armistice_cooldowns cleanup (clear when leaving ARMISTICE)
    - Active treaty removal on WAR declaration
    - Debug logging of all state transitions

    Does NOT handle domain-specific side effects (relation penalties,
    coalition threat, cascades, notifications). Those stay at call sites.

    Returns: previous state
    """
    from backend.utils.debug import debug_print

    key = world._make_diplo_key(nation_a, nation_b)
    old_state = world.diplomatic_states.get(key, "PEACE")

    if old_state == "WAR" and new_state != "WAR":
        _record_bargain_cobelligerent_war_end(world, nation_a, nation_b)

    # Set new state
    world.diplomatic_states[key] = new_state

    # War start tracking
    if new_state == "WAR" and old_state != "WAR":
        war_start_turns = getattr(world, 'war_start_turns', {})
        war_start_turns[key] = int(world.current_turn)
        world.war_start_turns = war_start_turns
    elif new_state == "WAR" and old_state == "WAR":
        # Ensure war_start_turns is set even for redundant WAR→WAR (e.g. cheat fix-up)
        war_start_turns = getattr(world, 'war_start_turns', {})
        if key not in war_start_turns:
            war_start_turns[key] = int(world.current_turn)
            world.war_start_turns = war_start_turns
    elif new_state != "WAR" and old_state == "WAR":
        war_start_turns = getattr(world, 'war_start_turns', {})
        war_start_turns.pop(key, None)
        world.war_start_turns = war_start_turns

    # Armistice cleanup when leaving ARMISTICE
    if old_state == "ARMISTICE" and new_state != "ARMISTICE":
        armistice_turns = getattr(world, 'armistice_turns', {})
        armistice_turns.pop(key, None)
        world.armistice_turns = armistice_turns
        armistice_cooldowns = getattr(world, 'armistice_cooldowns', {})
        armistice_cooldowns.pop(key, None)
        world.armistice_cooldowns = armistice_cooldowns

    # Active treaty removal on WAR declaration
    if new_state == "WAR" and old_state != "WAR":
        active_treaties = getattr(world, 'active_treaties', {})
        active_treaties.pop(key, None)

    # WPS-C §9.5: Clear forced alliance origin when state leaves ALLIANCE,
    # enters WAR, or becomes VASSAL.
    _ALLIANCE_ORIGIN_CLEAR_STATES = {"WAR", "VASSAL", "PEACE", "ARMISTICE",
                                      "NON_AGGRESSION", "OPEN_BORDERS",
                                      "DEFENSIVE_ALLIANCE"}
    if new_state in _ALLIANCE_ORIGIN_CLEAR_STATES and old_state == "ALLIANCE":
        alliance_origins = getattr(world, 'alliance_origins', {})
        alliance_origins.pop(key, None)
        world.alliance_origins = alliance_origins

    debug_print(f"DIPLO STATE: {nation_a}-{nation_b}: {old_state} -> {new_state}"
                f"{' (' + reason + ')' if reason else ''}")

    # B-Hegemony: centralized seam for ratification / war declaration /
    # peace / vassalage / cascade / armistice / treaty break. Bloc geometry
    # may have changed; invalidate cache + check for band crossing. If the
    # state didn't actually change, skip (avoid spurious cache churn + beats).
    if old_state != new_state:
        world.invalidate_bloc_members_cache()
        if int(getattr(world, "_defer_hegemony_signal_checks", 0) or 0) > 0:
            world._hegemony_signal_dirty = True
        else:
            try:
                from backend.game_logic.coalition import _check_hegemony_band_crossing
                _check_hegemony_band_crossing(world, caller=f"set_diplomatic_state:{reason or 'unknown'}")
            except Exception as exc:
                debug_print(
                    f"[HEGEMONY] band-crossing check failed after "
                    f"{nation_a}-{nation_b} {old_state}->{new_state} "
                    f"({reason or 'unknown'}): {exc}"
                )

    return old_state


def _begin_hegemony_signal_defer(world) -> None:
    depth = int(getattr(world, "_defer_hegemony_signal_checks", 0) or 0)
    world._defer_hegemony_signal_checks = depth + 1


def _flush_hegemony_signal_defer(world, caller: str) -> None:
    from backend.utils.debug import debug_print

    depth = max(0, int(getattr(world, "_defer_hegemony_signal_checks", 0) or 0) - 1)
    world._defer_hegemony_signal_checks = depth
    if depth > 0 or not bool(getattr(world, "_hegemony_signal_dirty", False)):
        return
    world._hegemony_signal_dirty = False
    try:
        from backend.game_logic.coalition import _check_hegemony_band_crossing
        _check_hegemony_band_crossing(world, caller=caller)
    except Exception as exc:
        debug_print(f"[HEGEMONY] deferred band-crossing check failed after {caller}: {exc}")


# ═══════════════════════════════════════════════════════
# STATE TRANSITION VALIDATION
# ═══════════════════════════════════════════════════════

def validate_transition(current_state: str, target_state: str) -> bool:
    """Check if a diplomatic state transition is valid (adjacency only, no relation check)."""
    if current_state == target_state:
        return False

    # Any state → WAR (war declaration) — always valid
    if target_state == "WAR":
        return True

    # VASSAL transitions
    if target_state == "VASSAL":
        return current_state in VASSAL_MIN_STATES
    if current_state == "VASSAL":
        return target_state in ("WAR", "PEACE", "NON_AGGRESSION")  # Deep audit fix 14: post_break_map uses NON_AGGRESSION

    # Upgrade path: any upward jump allowed (R98 — cumulative DP cost)
    if current_state in _UPGRADE_ORDER and target_state in _UPGRADE_ORDER:
        curr_idx = _UPGRADE_ORDER.index(current_state)
        tgt_idx = _UPGRADE_ORDER.index(target_state)
        if tgt_idx > curr_idx:
            return True

    # Downgrade path: must be adjacent in _DOWNGRADE_ORDER
    if current_state in _DOWNGRADE_ORDER and target_state in _DOWNGRADE_ORDER:
        curr_idx = _DOWNGRADE_ORDER.index(current_state)
        tgt_idx = _DOWNGRADE_ORDER.index(target_state)
        if tgt_idx == curr_idx + 1:
            return True

    return False


def check_relation_requirement(current_state: str, target_state: str, relation: int) -> bool:
    """Check if relation meets the requirement for an upgrade transition.

    R98: Uses target state's relation requirement (supports jumps).
    Returns True if requirement is met or no requirement exists.
    """
    req = STATE_RELATION_REQUIREMENTS.get(target_state)
    if req is None:
        return True
    return relation >= req


def get_transition_dp_cost(current_state: str, target_state: str) -> int:
    """Get DP cost for a transition.

    R98: For upward jumps, sums all intermediate step DP costs.
    E.g. PEACE→ALLIANCE = 1+1+2+2 = 6 DP.
    """
    if target_state == "WAR":
        return WAR_DP_COST
    if target_state == "VASSAL":
        return VASSAL_DP_COST

    # Adjacent upgrade (exact match in TRANSITION_RULES)
    rule = TRANSITION_RULES.get((current_state, target_state))
    if rule:
        return rule["dp_cost"]

    # Non-adjacent upward jump: sum intermediate costs
    if current_state in _UPGRADE_ORDER and target_state in _UPGRADE_ORDER:
        curr_idx = _UPGRADE_ORDER.index(current_state)
        tgt_idx = _UPGRADE_ORDER.index(target_state)
        if tgt_idx > curr_idx:
            total = 0
            for i in range(curr_idx, tgt_idx):
                step_from = _UPGRADE_ORDER[i]
                step_to = _UPGRADE_ORDER[i + 1]
                step_rule = TRANSITION_RULES.get((step_from, step_to))
                total += step_rule["dp_cost"] if step_rule else 1
            return total

    # Downgrade
    penalty = DOWNGRADE_PENALTIES.get((current_state, target_state))
    if penalty:
        return penalty["dp_cost"]
    return 1  # Default


# ═══════════════════════════════════════════════════════
# WAR SCORE CALCULATION (§6e)
# ═══════════════════════════════════════════════════════

def _decay_battle_score(raw_score: int, records: List[Dict], current_turn: int) -> int:
    """Apply quiet-turn decay to the battle component only."""
    if raw_score == 0 or not records:
        return 0

    last_battle_turn = max(int(record.get("turn", current_turn) or current_turn) for record in records)
    quiet_turns = max(0, int(current_turn) - last_battle_turn)
    if quiet_turns < 3:
        return raw_score

    decay_amount = (quiet_turns - 2) * 2
    if raw_score > 0:
        return max(0, raw_score - decay_amount)
    return min(0, raw_score + decay_amount)


def calculate_war_score(nation_a: str, nation_b: str, world, return_components: bool = False):
    """Calculate war score between two nations. Positive = nation_a winning.

    Components: territory (±40), battles (±30), decisive (±20),
    capital (±30), ticking objective score. Total capped at ±100.

    If return_components=True, returns {"total": int, "territory": int,
    "battles": int, "decisive": int, "capital": int, "ticking": int}
    instead of int.
    """
    from backend.models.region import NATION_CAPITALS

    # Territory score (cap ±40)
    territory_score = 0
    a_starting = set(world.nation_starting_regions.get(nation_a, []))
    b_starting = set(world.nation_starting_regions.get(nation_b, []))
    for region_name in b_starting:
        region = world.regions.get(region_name)
        if region and region.controller == nation_a:
            territory_score += 5  # A holds B's starting region
    for region_name in a_starting:
        region = world.regions.get(region_name)
        if region and region.controller == nation_b:
            territory_score -= 5  # B holds A's starting region
    territory_score = max(-40, min(40, territory_score))

    # Battle score (cap ±30). Quiet-turn decay applies to this component only.
    battle_score = 0
    diplo_key = world._make_diplo_key(nation_a, nation_b)
    records = getattr(world, 'battle_records', {}).get(diplo_key, [])
    for record in records:
        if record.get("winner") == nation_a:
            battle_score += 3
        elif record.get("winner") == nation_b:
            battle_score -= 3
    battle_score = max(-30, min(30, battle_score))
    battle_score = _decay_battle_score(int(battle_score), records, world.current_turn)

    # Decisive battle bonus (cap ±20)
    decisive_score = 0
    decisive_records = getattr(world, 'decisive_battles', {}).get(diplo_key, [])
    for d in decisive_records:
        if d.get("winner") == nation_a:
            decisive_score += 10
        elif d.get("winner") == nation_b:
            decisive_score -= 10
    decisive_score = max(-20, min(20, decisive_score))

    # Capital score (cap ±30)
    capital_score = 0
    a_capital = NATION_CAPITALS.get(nation_a)
    b_capital = NATION_CAPITALS.get(nation_b)

    if b_capital and b_capital in world.regions:
        b_cap_region = world.regions[b_capital]
        if b_cap_region.controller == nation_a:
            capital_score += 20
        elif any(m.nation == nation_a and m.location == b_capital
                 for m in world.marshals.values()):
            capital_score += 10  # Contested
    if a_capital and a_capital in world.regions:
        a_cap_region = world.regions[a_capital]
        if a_cap_region.controller == nation_b:
            capital_score -= 20
        elif any(m.nation == nation_b and m.location == a_capital
                 for m in world.marshals.values()):
            capital_score -= 10  # Contested
    capital_score = max(-30, min(30, capital_score))

    # WPS-A: Ticking score (5th component)
    ticking_score = 0
    war_obj = getattr(world, 'war_objectives', {}).get(diplo_key, {})
    ticking_a = war_obj.get(nation_a, {}).get("accumulated_ticking", 0)
    ticking_b = war_obj.get(nation_b, {}).get("accumulated_ticking", 0)
    ticking_score = int(ticking_a - ticking_b)

    total = territory_score + battle_score + decisive_score + capital_score + ticking_score
    total = int(max(-100, min(100, total)))

    if return_components:
        return {
            "total": total,
            "territory": int(territory_score),
            "battles": int(battle_score),
            "decisive": int(decisive_score),
            "capital": int(capital_score),
            "ticking": int(ticking_score),
        }
    return total


def apply_war_score_decay(world, *, recalculate: bool = True) -> None:
    """Apply battle-score decay and prune stale battle records.

    Decisive bonuses, territory, capital control, and future ticking score do
    not decay. This function never subtracts from the stored total directly;
    it prunes stale battle records and recomputes active war scores from their
    components.
    """
    battle_records = getattr(world, 'battle_records', {})

    # R1a: Prune battle records older than 10 turns
    for diplo_key in list(battle_records.keys()):
        records = battle_records[diplo_key]
        battle_records[diplo_key] = [
            r for r in records
            if world.current_turn - r.get("turn", 0) <= 10
        ]

    if recalculate:
        recalculate_war_scores(world)


def recalculate_war_scores(world) -> None:
    """Recalculate war scores for all active wars."""
    war_scores = getattr(world, 'war_scores', {})
    for diplo_key, state in world.diplomatic_states.items():
        if state == "WAR":
            parts = diplo_key.split("|")
            if len(parts) == 2:
                score = calculate_war_score(parts[0], parts[1], world)
                war_scores[diplo_key] = int(score)
    world.war_scores = war_scores


def get_war_score_for(world, nation: str, opponent: str) -> int:
    """Get war score from a specific nation's perspective.

    Positive = nation is winning, negative = nation is losing.
    The stored war_score is from alphabetically-first nation's perspective.
    Canonical helper — all callers should use this instead of manual flipping.
    """
    diplo_key = world._make_diplo_key(nation, opponent)
    raw_score = getattr(world, 'war_scores', {}).get(diplo_key, 0)

    # If nation is alphabetically second, flip the sign
    parts = diplo_key.split("|")
    if len(parts) == 2 and parts[0] != nation:
        raw_score = -raw_score

    return int(raw_score)


# ═══════════════════════════════════════════════════════
# DIPLOMACY HELPERS
# ═══════════════════════════════════════════════════════

def get_relation(world, nation_a: str, nation_b: str) -> int:
    """Return the canonical unordered bilateral relation for two nations."""
    if not nation_a or not nation_b:
        return 0
    if nation_a == nation_b:
        return 100
    make_key = getattr(world, "_make_diplo_key", None)
    if callable(make_key):
        key = make_key(nation_a, nation_b)
    else:
        key = "|".join(sorted([nation_a, nation_b]))
    try:
        return int(getattr(world, "nation_relations", {}).get(key, 0) or 0)
    except (TypeError, ValueError):
        return 0


# ═══════════════════════════════════════════════════════
# WPS-A: WAR OBJECTIVES + TICKING SCORE
# ═══════════════════════════════════════════════════════

OBJECTIVE_TYPES = {"conquest", "subjugation", "forced_alliance", "defense", "liberation"}
OFFENSIVE_OBJECTIVE_TYPES = {"conquest", "subjugation", "forced_alliance"}
TICKING_RATES = {
    "conquest": 2,
    "subjugation": 3,
    "forced_alliance": 2,
    "defense": 1,
    "liberation": 1,
}
TICKING_CAP = 25

SETTLEMENT_TIERS = [
    (80, "total_victory"),
    (60, "harsh_peace"),
    (40, "dictated_terms"),
    (20, "favorable_terms"),
    (0, "white_peace"),
]

SETTLEMENT_TIER_DISPLAY = {
    "total_victory": "Total Victory",
    "harsh_peace": "Harsh Peace",
    "dictated_terms": "Dictated Terms",
    "favorable_terms": "Favorable Terms",
    "white_peace": "White Peace",
}

OBJECTIVE_TYPE_DISPLAY = {
    "conquest": "Conquest",
    "subjugation": "Subjugation",
    "forced_alliance": "Forced Alliance",
    "defense": "Defense",
    "liberation": "Liberation",
}


BRITISH_NAVAL_INCOME_POWER = 300
POWER_CAP_RATIO = 2

LEGACY_COASTAL_REGIONS_FOR_POWER = frozenset({
    "Netherlands", "Normandy", "Brittany", "Bordeaux", "Marseille",
})


def _region_is_coastal_for_power(region_name: str, region) -> bool:
    return bool(getattr(region, "is_coastal", region_name in LEGACY_COASTAL_REGIONS_FOR_POWER))


def _regions_for_controller(
    nation: str,
    world,
    *,
    controller_override: dict = None,
    controller_regions_override: dict = None,
) -> list:
    if controller_regions_override is not None:
        return list(controller_regions_override.get(nation, []))
    if controller_override is None:
        return world.get_nation_regions(nation)

    controlled = []
    for rname, region in world.regions.items():
        ctrl = controller_override.get(rname, region.controller)
        if ctrl == nation:
            controlled.append(rname)
    return controlled


def calculate_national_power(nation: str, world, *,
                             controller_override: dict = None,
                             controller_regions_override: dict = None) -> int:
    """Calculate national power from controlled regions and vassal contribution.

    Evaluated at proposal/objective-validation time, not per-turn hot path.
    ``controller_override`` lets callers project post-cession power without
    mutating WorldState (see ``project_power_after_terms``).
    """
    if controller_override is None and controller_regions_override is None:
        vassal_signature = tuple(
            sorted(
                (str(vassal), str(data.get("lord") or data.get("lord_nation") or ""))
                for vassal, data in getattr(world, "vassals", {}).items()
            )
        )
        cache_key = (int(world.current_turn), nation, vassal_signature)
        power_cache = getattr(world, "_national_power_cache", None)
        if power_cache is None:
            world._national_power_cache = {}
            power_cache = world._national_power_cache
        if cache_key in power_cache:
            return int(power_cache[cache_key])
    else:
        cache_key = None
        power_cache = None

    power = 0
    nation_regions = _regions_for_controller(
        nation,
        world,
        controller_override=controller_override,
        controller_regions_override=controller_regions_override,
    )

    for rname in nation_regions:
        region = world.regions.get(rname)
        if region:
            power += region.income_value

    for vassal_nation, vassal_data in getattr(world, 'vassals', {}).items():
        if (vassal_data.get("lord") or vassal_data.get("lord_nation")) == nation:
            for rname in _regions_for_controller(
                vassal_nation,
                world,
                controller_override=controller_override,
                controller_regions_override=controller_regions_override,
            ):
                region = world.regions.get(rname)
                if region:
                    power += region.income_value // 2

    if nation == "Britain" and len(nation_regions) > 0:
        coastal_count = sum(
            1 for rname in nation_regions
            if (region := world.regions.get(rname)) and _region_is_coastal_for_power(rname, region)
        )
        power += min(BRITISH_NAVAL_INCOME_POWER, 150 + 50 * coastal_count)

    if power_cache is not None and cache_key is not None:
        power_cache[cache_key] = int(power)
    return int(power)


def project_power_after_terms(world, terms: list, proposer: str,
                              target: str) -> dict:
    """Project national power after applying territory-transfer terms.

    Returns ``{proposer: int, target: int}`` without mutating WorldState.
    Territory cessions may arrive as raw proposal terms, normalized treaty
    clauses, or the spec's ``territory_cession`` shape. Invalid or duplicate
    transfers are silently skipped.
    """
    controller_map = {}
    for rname, region in world.regions.items():
        controller_map[rname] = region.controller

    seen_regions = set()

    def _terms_to_scan(raw_terms):
        if isinstance(raw_terms, dict):
            for term in raw_terms.get("sweeteners", []):
                yield term, proposer, target
            for term in raw_terms.get("demands", []):
                yield term, target, proposer
            for term in raw_terms.get("clauses", []):
                if isinstance(term, dict):
                    yield term, target, proposer
            return

        for term in (raw_terms or []):
            if isinstance(term, dict):
                yield term, target, proposer

    def _term_regions(term: dict) -> list:
        regions = term.get("regions")
        if isinstance(regions, str):
            return [regions]
        if isinstance(regions, list):
            return list(regions)
        region = term.get("region")
        if region:
            return [region]
        value = term.get("value")
        if isinstance(value, str):
            return [value]
        return []

    for term, default_from, default_to in _terms_to_scan(terms):
        ttype = term.get("type", "")
        if ttype not in ("territory_cession", "territory_cede", "territory"):
            continue
        from_nation = term.get("from") or term.get("from_nation") or default_from
        to_nation = term.get("to") or term.get("to_nation") or default_to
        if not to_nation:
            continue
        for region_name in _term_regions(term):
            if not region_name or region_name not in controller_map:
                continue
            if region_name in seen_regions:
                continue
            if from_nation and controller_map[region_name] != from_nation:
                continue
            controller_map[region_name] = to_nation
            seen_regions.add(region_name)

    controller_regions_map = {}
    for rname, controller in controller_map.items():
        controller_regions_map.setdefault(controller, []).append(rname)

    return {
        proposer: calculate_national_power(
            proposer,
            world,
            controller_override=controller_map,
            controller_regions_override=controller_regions_map,
        ),
        target: calculate_national_power(
            target,
            world,
            controller_override=controller_map,
            controller_regions_override=controller_regions_map,
        ),
    }


def check_vassalage_power_cap(world, lord: str, target: str, *,
                              terms: list = None) -> dict:
    """Check whether target is below the vassalage power cap.

    If ``terms`` is provided, power is projected after territory transfers.
    Returns ``{allowed: bool, lord_power: int, target_power: int, pct: int,
               reason: str}``.
    """
    if terms:
        projected = project_power_after_terms(world, terms, lord, target)
        lord_power = projected[lord]
        target_power = projected[target]
    else:
        lord_power = calculate_national_power(lord, world)
        target_power = calculate_national_power(target, world)

    pct = int((target_power * 100) // lord_power) if lord_power > 0 else 100
    allowed = target_power <= lord_power // POWER_CAP_RATIO

    reason = ""
    if lord == target:
        allowed = False
        reason = f"{target} cannot be vassalized by itself"
    elif lord_power <= 0:
        allowed = False
        reason = f"{lord} lacks the national power to vassalize {target}"
    elif target_power <= 0:
        allowed = False
        reason = f"{target} has no national power to vassalize"
    elif not allowed:
        reason = (f"{target} is too powerful to vassalize "
                  f"(power: {pct}% of {lord})")

    return {
        "allowed": allowed,
        "lord_power": int(lord_power),
        "target_power": int(target_power),
        "pct": int(pct),
        "reason": reason,
    }


def create_war_objective(
    objective_type: str,
    declaring_nation: str,
    target_nation: str,
    target_regions: list,
    current_turn: int,
    vassal_nations: list = None,
) -> Dict:
    """Build a war objective record per WPS spec §6.4."""
    obj = {
        "type": objective_type,
        "declaring_nation": declaring_nation,
        "target_nation": target_nation,
        "target_regions": list(target_regions),
        "accumulated_ticking": 0,
        "created_turn": int(current_turn),
        "ticking_active": False,
        "objective_met_turn": None,
    }
    if objective_type == "liberation":
        obj["vassal_nations"] = list(vassal_nations or [])
    return obj


def get_available_war_objectives(world, aggressor: str, target: str) -> list:
    """Return available objectives for the War Purpose popup."""
    from backend.models.region import NATION_CAPITALS

    target_capital = NATION_CAPITALS.get(target)
    objectives = []

    objectives.append({
        "type": "conquest",
        "label": "Conquest",
        "description": f"Seize {target_capital or 'the capital'}. +2/turn while held.",
        "available": True,
        "ticking_rate": 2,
    })

    objectives.append({
        "type": "forced_alliance",
        "label": "Forced Alliance",
        "description": f"Force {target} into alliance. +2/turn while {target_capital or 'capital'} held.",
        "available": True,
        "ticking_rate": 2,
    })

    cap = check_vassalage_power_cap(world, aggressor, target)
    subjugation_available = cap["allowed"]

    objectives.append({
        "type": "subjugation",
        "label": "Subjugation",
        "description": f"Total defeat — vassalize {target}. +3/turn while {target_capital or 'capital'} held.",
        "available": subjugation_available,
        "ticking_rate": 3,
        "reason": None if subjugation_available else f"{target} is too powerful to subjugate ({cap['pct']}% of {aggressor})",
        "power_pct": cap["pct"],
    })

    return objectives


def _get_objective_availability(world, aggressor: str, target: str,
                                objective_type: str) -> Dict:
    """Return the availability record for an offensive objective."""
    for obj in get_available_war_objectives(world, aggressor, target):
        if obj.get("type") == objective_type:
            return obj
    return {}


def get_settlement_tier(war_score: int) -> str:
    """Map a war score to a settlement tier name."""
    abs_score = abs(war_score)
    for threshold, tier in SETTLEMENT_TIERS:
        if abs_score >= threshold:
            return tier
    return "white_peace"


CLAUSE_MINIMUM_TIER = {
    "forced_alliance": "harsh_peace",
    "liberation": "dictated_terms",
    "ap_per_turn": "harsh_peace",
}

TIER_ORDER = ["white_peace", "favorable_terms", "dictated_terms", "harsh_peace", "total_victory"]


def _tier_rank(tier: str) -> int:
    try:
        return TIER_ORDER.index(tier)
    except ValueError:
        return 0


def _territory_term_count(term: Dict) -> int:
    regions = term.get("regions", [])
    if isinstance(regions, list) and regions:
        return len(regions)
    value = term.get("value", term.get("amount", 0))
    try:
        count = int(value or 0)
    except (TypeError, ValueError):
        count = 0
    return max(1, count)


def get_tier_mismatch_warnings(war_score: int, terms: Dict) -> List[Dict]:
    """WPS-D §11.4: Detect when proposed terms exceed the current settlement tier."""
    current_tier = get_settlement_tier(war_score)
    current_rank = _tier_rank(current_tier)
    warnings = []

    all_clauses = []
    for c in terms.get("clauses", []):
        if isinstance(c, dict):
            all_clauses.append(c.get("clause_type") or c.get("type", ""))
        elif isinstance(c, str):
            all_clauses.append(c)

    for d in terms.get("demands", []):
        dtype = d.get("type", "")
        if dtype:
            all_clauses.append(dtype)

    territory_demand_count = sum(
        _territory_term_count(d)
        for d in terms.get("demands", [])
        if isinstance(d, dict) and d.get("type", "") in ("territory", "territory_cede")
    )

    if territory_demand_count >= 4:
        needed = "harsh_peace"
    elif territory_demand_count >= 2:
        needed = "dictated_terms"
    else:
        needed = None

    if needed and _tier_rank(needed) > current_rank:
        display = (
            f"Your war score ({war_score:+d}) may not support demanding "
            f"{territory_demand_count} regions. "
            f"{SETTLEMENT_TIER_DISPLAY.get(needed, needed)} ({TIER_ORDER.index(needed) * 20:+d}) "
            f"typically required."
        )
        warnings.append({
            "warning_type": "tier_mismatch",
            "current_tier": current_tier,
            "demanded_tier": needed,
            "severity": "WARNING",
            "text": display,
            "display": display,
        })

    for clause_key in all_clauses:
        min_tier = CLAUSE_MINIMUM_TIER.get(clause_key)
        if min_tier and _tier_rank(min_tier) > current_rank:
            clause_display = clause_key.replace("_", " ").title()
            display = (
                f"Your war score ({war_score:+d}) may not support these terms. "
                f"{clause_display} typically requires "
                f"{SETTLEMENT_TIER_DISPLAY.get(min_tier, min_tier)} "
                f"({TIER_ORDER.index(min_tier) * 20:+d})."
            )
            warnings.append({
                "warning_type": "tier_mismatch",
                "current_tier": current_tier,
                "demanded_tier": min_tier,
                "severity": "WARNING",
                "text": display,
                "display": display,
            })

    return warnings


def _auto_assign_defense_objective(world, defender: str, aggressor: str, diplo_key: str) -> None:
    """Auto-assign a defense objective to the attacked nation."""
    target_regions = list(
        getattr(world, 'nation_starting_regions', {}).get(defender, [])
    )

    if diplo_key not in world.war_objectives:
        world.war_objectives[diplo_key] = {}

    world.war_objectives[diplo_key][defender] = create_war_objective(
        objective_type="defense",
        declaring_nation=defender,
        target_nation=aggressor,
        target_regions=target_regions,
        current_turn=world.current_turn,
    )


def _get_liberation_targets(world, occupying_nation: str) -> tuple:
    """Return French-held vassal capitals that a coalition can liberate."""
    from backend.models.region import NATION_CAPITALS

    target_regions = []
    vassal_nations = []
    for vassal_nation, vassal_data in getattr(world, 'vassals', {}).items():
        if vassal_data.get("lord") != occupying_nation:
            continue
        capital = NATION_CAPITALS.get(vassal_nation)
        if not capital or capital not in world.regions:
            continue
        if world.regions[capital].controller == occupying_nation:
            target_regions.append(capital)
            vassal_nations.append(vassal_nation)
    return target_regions, vassal_nations


def assign_coalition_war_objective(world, coalition_member: str,
                                   target_nation: str) -> bool:
    """Assign the coalition member's automatic WPS-A objective.

    Coalition wars use liberation if the target controls vassal capitals;
    otherwise they use the defensive homeland objective.
    """
    diplo_key = world._make_diplo_key(coalition_member, target_nation)
    if world.diplomatic_states.get(diplo_key) != "WAR":
        return False

    if diplo_key not in world.war_objectives:
        world.war_objectives[diplo_key] = {}

    existing = world.war_objectives[diplo_key].get(coalition_member)
    target_regions, vassal_nations = _get_liberation_targets(world, target_nation)
    objective_type = "liberation" if target_regions else "defense"
    if objective_type == "defense":
        target_regions = list(
            getattr(world, 'nation_starting_regions', {}).get(coalition_member, [])
        )
        vassal_nations = []

    if existing and existing.get("concluded_turn") is None:
        if existing.get("type") != "defense" or objective_type == "defense":
            return False

    world.war_objectives[diplo_key][coalition_member] = create_war_objective(
        objective_type=objective_type,
        declaring_nation=coalition_member,
        target_nation=target_nation,
        target_regions=target_regions,
        current_turn=world.current_turn,
        vassal_nations=vassal_nations,
    )
    world.log_event({
        "type": "war_objective_declared",
        "declaring_nation": coalition_member,
        "target_nation": target_nation,
        "objective_type": objective_type,
        "target_regions": target_regions,
        "turn": int(world.current_turn),
    })
    return True


def accumulate_war_objective_ticking(world) -> List[Dict]:
    """Accumulate ticking for all active war objectives. Called in process_diplomacy_turn."""
    events = []

    for diplo_key, nation_objectives in list(world.war_objectives.items()):
        diplo_state = world.diplomatic_states.get(diplo_key, "PEACE")

        if diplo_state == "ARMISTICE":
            continue

        if diplo_state != "WAR":
            continue

        for nation, obj in nation_objectives.items():
            if obj.get("concluded_turn") is not None:
                continue

            obj_type = obj.get("type", "")
            prev_ticking = obj.get("accumulated_ticking", 0)

            if prev_ticking >= TICKING_CAP:
                continue

            rate = TICKING_RATES.get(obj_type, 0)
            gained = 0

            if obj_type in ("conquest", "subjugation", "forced_alliance"):
                for target_region in obj.get("target_regions", []):
                    if target_region in world.regions:
                        if world.regions[target_region].controller == nation:
                            gained += rate
            elif obj_type == "defense":
                for target_region in obj.get("target_regions", []):
                    if target_region in world.regions:
                        if world.regions[target_region].controller != nation:
                            gained += 1
            elif obj_type == "liberation":
                for target_region in obj.get("target_regions", []):
                    if target_region in world.regions:
                        target_nation = obj.get("target_nation", "")
                        if world.regions[target_region].controller == target_nation:
                            gained += 1

            if gained > 0:
                new_total = min(prev_ticking + gained, TICKING_CAP)
                obj["accumulated_ticking"] = int(new_total)
                obj["ticking_active"] = True

                if prev_ticking == 0:
                    events.append({
                        "type": "war_objective_ticking_started",
                        "declaring_nation": nation,
                        "target_nation": obj.get("target_nation", ""),
                        "objective_type": obj_type,
                        "target_region": obj.get("target_regions", [""])[0],
                        "accumulated_ticking": int(new_total),
                        "rate": rate if obj_type not in ("defense", "liberation") else gained,
                        "turn": int(world.current_turn),
                    })

                if new_total >= TICKING_CAP and obj.get("objective_met_turn") is None:
                    obj["objective_met_turn"] = int(world.current_turn)

    return events


def _conclude_war_objectives(world, diplo_key: str) -> None:
    """Mark objectives as concluded when a war ends."""
    objectives = world.war_objectives.get(diplo_key)
    if not objectives:
        return
    for nation, obj in objectives.items():
        if obj.get("concluded_turn") is None:
            obj["concluded_turn"] = int(world.current_turn)


def _cleanup_old_war_objectives(world) -> None:
    """Remove concluded war objectives older than 10 turns."""
    for diplo_key in list(world.war_objectives.keys()):
        nation_objs = world.war_objectives[diplo_key]
        all_concluded = True
        for nation, obj in list(nation_objs.items()):
            concluded = obj.get("concluded_turn")
            if concluded is None:
                all_concluded = False
            elif world.current_turn - concluded > 10:
                del nation_objs[nation]
        if all_concluded and not nation_objs:
            del world.war_objectives[diplo_key]


# ═══════════════════════════════════════════════════════
# BPH-B: WAR CONTEXT SNAPSHOT
# ═══════════════════════════════════════════════════════

PEACE_CLASS_ACTIONS = frozenset({
    "propose_armistice", "propose_peace",
})

ARMISTICE_DURATION = 5

HARSHNESS_LABELS = [
    (0.10, "generous"),
    (0.25, "balanced"),
    (0.50, "harsh"),
    (1.01, "punitive"),
]


def get_harshness_label(harshness: float) -> str:
    for threshold, label in HARSHNESS_LABELS:
        if harshness < threshold:
            return label
    return "punitive"


def _normalize_acceptance_preview_outcome(outcome: str) -> str:
    """Map internal acceptance outcomes to the BPH-B preview contract."""
    if outcome == "COUNTER_OFFER":
        return "COUNTER"
    if outcome in ("ACCEPT", "COUNTER", "REJECT"):
        return outcome
    return "REJECT"


def _score_from_player_perspective(diplo_key: str, player_nation: str, score: int) -> int:
    parts = diplo_key.split("|")
    if len(parts) == 2 and parts[0] != player_nation:
        return -int(score)
    return int(score)


def _get_war_score_trend(world, diplo_key: str, player_nation: str, war_score: int) -> str:
    """Return rising/falling/stagnant using the last up-to-3 stored snapshots."""
    history = getattr(world, 'war_score_history', {}).get(diplo_key, [])
    comparison_score = None
    if history:
        comparison_score = _score_from_player_perspective(
            diplo_key, player_nation, int(history[0]),
        )
    else:
        previous_scores = getattr(world, 'previous_war_scores', {})
        if diplo_key in previous_scores:
            comparison_score = _score_from_player_perspective(
                diplo_key, player_nation, int(previous_scores.get(diplo_key, 0)),
            )

    if comparison_score is None:
        return "stagnant"

    score_delta = int(war_score) - int(comparison_score)
    if score_delta > 2:
        return "rising"
    if score_delta < -2:
        return "falling"
    return "stagnant"


def build_war_context_snapshot(
    world, player_nation: str, target_nation: str, proposal_type: str,
    terms: Dict = None,
) -> Dict:
    """Build the frozen war-context snapshot for a peace-class preview (BPH-B §8.1).

    Returns a dict with war score components, battle stats, casualties,
    regions held, acceptance preview, and harshness assessment.
    All values are int() for Godot safety.
    """
    diplo_key = world._make_diplo_key(player_nation, target_nation)
    current_state = world.diplomatic_states.get(diplo_key, "PEACE")

    # War score + components (from player's perspective)
    components = calculate_war_score(player_nation, target_nation, world, return_components=True)
    war_score = int(components["total"])

    # War duration
    war_start = world.war_start_turns.get(diplo_key, world.current_turn)
    war_duration = int(max(0, world.current_turn - war_start))

    # Battle stats from records
    records = getattr(world, 'battle_records', {}).get(diplo_key, [])
    decisive_records = getattr(world, 'decisive_battles', {}).get(diplo_key, [])

    battles_won = 0
    battles_lost = 0
    french_casualties = 0
    enemy_casualties = 0
    for r in records:
        winner = r.get("winner", "")
        if winner == player_nation:
            battles_won += 1
        elif winner == target_nation:
            battles_lost += 1
        if r.get("attacker") == player_nation:
            french_casualties += int(r.get("attacker_casualties", 0))
            enemy_casualties += int(r.get("defender_casualties", 0))
        else:
            french_casualties += int(r.get("defender_casualties", 0))
            enemy_casualties += int(r.get("attacker_casualties", 0))

    decisive_victories = sum(
        1 for d in decisive_records if d.get("winner") == player_nation
    )
    decisive_defeats = sum(
        1 for d in decisive_records if d.get("winner") == target_nation
    )

    # Regions held by each side (enemy starting regions France holds, and vice versa)
    player_starting = set(world.nation_starting_regions.get(player_nation, []))
    enemy_starting = set(world.nation_starting_regions.get(target_nation, []))
    regions_held_by_player = [
        r.name for r in world.regions.values()
        if r.name in enemy_starting and r.controller == player_nation
    ]
    regions_held_by_enemy = [
        r.name for r in world.regions.values()
        if r.name in player_starting and r.controller == target_nation
    ]

    war_score_trend = _get_war_score_trend(world, diplo_key, player_nation, war_score)

    # Acceptance preview
    from backend.game_logic.diplomatic_templates import (
        annotate_peace_terms, calculate_treaty_harshness, generate_suggested_terms,
    )
    effective_terms = copy.deepcopy(terms) if terms else None
    if not effective_terms:
        effective_terms = generate_suggested_terms(target_nation, proposal_type, world)
    effective_terms = copy.deepcopy(effective_terms)
    harshness_terms = dict(effective_terms)
    harshness_terms["clauses"] = [
        c if isinstance(c, dict) else {"type": c}
        for c in effective_terms.get("clauses", [])
    ]
    harshness = calculate_treaty_harshness(harshness_terms)

    proposal_for_calc = {
        "type": effective_terms.get("type", proposal_type),
        "proposer_nation": player_nation,
        "target_nation": target_nation,
        "sweeteners": effective_terms.get("sweeteners", []),
        "demands": effective_terms.get("demands", []),
        "clauses": effective_terms.get("clauses", []),
    }
    try:
        acceptance_result = calculate_acceptance(proposal_for_calc, world)
        acceptance_score = int(max(0, min(100, acceptance_result["score"])))
        acceptance_outcome = _normalize_acceptance_preview_outcome(
            acceptance_result.get("outcome", "REJECT"),
        )
        acc_components = acceptance_result.get("components", {})
        largest_pos_key, largest_pos_val = "", 0
        largest_neg_key, largest_neg_val = "", 0
        for k, v in acc_components.items():
            if v > largest_pos_val:
                largest_pos_key, largest_pos_val = k, v
            if v < largest_neg_val:
                largest_neg_key, largest_neg_val = k, v
        # G4F-13: a COUNTER verdict only reads "expected" when the real
        # generator can construct one (dry run — no DP charge).
        acceptance_outcome_display = ""
        if acceptance_outcome == "COUNTER":
            from backend.game_logic.ai_diplomacy import generate_counter_offer
            _counter_ok = generate_counter_offer(
                proposal_for_calc, world, dry_run=True
            ) is not None
            acceptance_outcome_display = (
                "COUNTER expected"
                if _counter_ok
                else "REJECT likely — no workable counter"
            )
    except Exception:
        acceptance_score = 0
        acceptance_outcome = "REJECT"
        acceptance_outcome_display = ""
        largest_pos_key = ""
        largest_neg_key = ""

    acceptance_preview = {
        "score": int(acceptance_score),
        "outcome": acceptance_outcome,
        "outcome_display": acceptance_outcome_display,
        "largest_positive": largest_pos_key.replace("_", " ").title() if largest_pos_key else "",
        "largest_negative": largest_neg_key.replace("_", " ").title() if largest_neg_key else "",
    }

    # Annotated terms
    annotated = annotate_peace_terms(effective_terms, player_nation, target_nation)

    proposed_state = "ARMISTICE" if "armistice" in proposal_type else "PEACE"
    fallout_warnings = []
    if proposed_state == "PEACE":
        fallout_warnings = get_separate_peace_fallout_warnings(
            world, player_nation, target_nation, harshness,
        )

    snapshot = {
        "target_nation": target_nation,
        "current_state": current_state,
        "proposed_state": proposed_state,
        "war_score": int(war_score),
        "war_score_components": {
            "territory": int(components["territory"]),
            "battle": int(components["battles"]),
            "decisive_battle": int(components["decisive"]),
            "capital": int(components["capital"]),
            "ticking": int(components["ticking"]),
        },
        "war_score_trend": war_score_trend,
        "war_duration_turns": int(war_duration),
        "battles_fought": int(battles_won + battles_lost),
        "battles_won": int(battles_won),
        "battles_lost": int(battles_lost),
        "decisive_victories": int(decisive_victories),
        "decisive_defeats": int(decisive_defeats),
        "french_casualties_total": int(french_casualties),
        "enemy_casualties_total": int(enemy_casualties),
        "regions_held_by_france": regions_held_by_player,
        "regions_held_by_enemy": regions_held_by_enemy,
        "france_relation": int(world.nation_relations.get(diplo_key, 0)),
        "acceptance_preview": acceptance_preview,
        "harshness": round(harshness, 2),
        "harshness_label": get_harshness_label(harshness),
        "proposal_terms": effective_terms,
        "annotated_terms": annotated,
        "fallout_warnings": fallout_warnings,
        "commitment_conflicts": get_peace_commitment_conflicts(
            world, player_nation, target_nation, effective_terms.get("clauses", []),
        ),
    }

    # Strategic order cancellation preview
    order_cancellations = _get_order_cancellation_preview(world, player_nation, target_nation)
    if order_cancellations:
        snapshot["fallout_warnings"].append(order_cancellations)

    # WPS-D §14.3: War objective + settlement tier + tier mismatch warnings
    war_obj_data = getattr(world, 'war_objectives', {}).get(diplo_key, {})
    player_obj = war_obj_data.get(player_nation, {})
    if player_obj and player_obj.get("concluded_turn") is None:
        obj_type = player_obj.get("type", "")
        snapshot["war_objective"] = {
            "type": obj_type,
            "target_regions": player_obj.get("target_regions", []),
            "accumulated_ticking": int(player_obj.get("accumulated_ticking", 0)),
            "ticking_active": bool(player_obj.get("ticking_active", False)),
        }
    else:
        snapshot["war_objective"] = None

    tier = get_settlement_tier(war_score)
    snapshot["settlement_tier"] = tier
    snapshot["settlement_tier_display"] = SETTLEMENT_TIER_DISPLAY.get(tier, tier)
    snapshot["tier_mismatch_warnings"] = get_tier_mismatch_warnings(war_score, effective_terms)

    # Armistice-specific fields
    if current_state == "ARMISTICE":
        armistice_elapsed = int(world.armistice_turns.get(diplo_key, 0))
        snapshot["armistice_remaining_turns"] = int(max(0, ARMISTICE_DURATION - armistice_elapsed))
        cooldown = world.armistice_cooldowns.get(diplo_key, 0)
        snapshot["armistice_cooldown_active"] = bool(cooldown > 0)

    return snapshot


def get_separate_peace_fallout_warnings(
    world, proposer: str, target: str, harshness: float,
) -> List[Dict]:
    """BPH-C §9.2: Compute ally fallout warnings for a separate peace proposal.

    Returns structured warnings for each ally that is still at war with the target.
    """
    warnings: List[Dict] = []
    all_nations = world.get_active_nations()
    for nation in all_nations:
        if nation == proposer or nation == target:
            continue
        ally_key = world._make_diplo_key(proposer, nation)
        ally_state = world.diplomatic_states.get(ally_key, "PEACE")
        if ally_state not in ("DEFENSIVE_ALLIANCE", "ALLIANCE"):
            continue
        target_key = world._make_diplo_key(nation, target)
        target_state = world.diplomatic_states.get(target_key, "PEACE")
        if target_state != "WAR":
            continue

        ally_war_score = get_war_score_for(world, nation, target)
        ally_relation = int(world.nation_relations.get(ally_key, 0))
        war_start = world.war_start_turns.get(target_key, world.current_turn)
        ally_war_turns = int(max(0, world.current_turn - war_start))
        records = getattr(world, 'battle_records', {}).get(target_key, [])
        ally_casualties = 0
        for r in records:
            if r.get("attacker") == nation:
                ally_casualties += int(r.get("attacker_casualties", 0))
            elif r.get("defender") == nation:
                ally_casualties += int(r.get("defender_casualties", 0))

        penalty = _compute_separate_peace_penalty(
            ally_war_score, ally_war_turns, ally_casualties, harshness,
        )
        if ally_war_score > 20:
            severity = "MINOR"
        elif ally_war_turns >= 5 and ally_casualties > 5000:
            severity = "SEVERE"
        else:
            severity = "MAJOR"

        score_str = f"+{ally_war_score}" if ally_war_score > 0 else str(int(ally_war_score))
        display = (
            f"{nation} is still at war with {target} (war score: {score_str}). "
            f"Making separate peace will anger {nation} ({penalty} relation)."
        )
        warnings.append({
            "warning_type": "separate_peace_ally",
            "ally": nation,
            "ally_state_vs_target": target_state,
            "ally_war_score_vs_target": int(ally_war_score),
            "ally_relation_with_proposer": int(ally_relation),
            "predicted_relation_change": int(penalty),
            "severity": severity,
            "display": display,
        })
    return warnings


def _compute_separate_peace_penalty(
    ally_war_score: int, ally_war_turns: int,
    ally_casualties: int, harshness: float,
) -> int:
    """BPH-C §9.3: Compute the one-time relation penalty for a separate peace."""
    base_penalty = -5
    if ally_war_score <= 20:
        base_penalty = -10
    if ally_war_turns >= 5 and ally_casualties > 5000:
        base_penalty = -15
    if harshness < 0.2:
        base_penalty *= 2
    return int(base_penalty)


def apply_separate_peace_penalties(
    world, proposer: str, target: str, harshness: float,
) -> List[Dict]:
    """BPH-C §9.3: Apply relation penalties on ratification of a separate peace.

    Returns list of applied penalties for the ratification summary.
    """
    warnings = get_separate_peace_fallout_warnings(world, proposer, target, harshness)
    applied = []
    for w in warnings:
        ally = w["ally"]
        penalty = w["predicted_relation_change"]
        world.modify_nation_relation(proposer, ally, penalty)
        applied.append({
            "ally": ally,
            "relation_change": int(penalty),
            "severity": w["severity"],
            "display": f"{ally} views this separate peace unfavorably ({penalty} relation)",
        })
    return applied


def _capture_pre_cleanup_war_data(world, proposer: str, target_nation: str) -> Dict:
    """Snapshot war data that cleanup_war_end will clear.

    Must be called BEFORE cleanup_war_end so the ratification summary
    can reference casualties, war score, and war duration.
    """
    player = world.player_nation
    diplo_key = world._make_diplo_key(proposer, target_nation)

    war_start = world.war_start_turns.get(diplo_key, world.current_turn)
    war_duration = int(max(0, world.current_turn - war_start))

    raw_score = int(getattr(world, 'war_scores', {}).get(diplo_key, 0))
    parts = diplo_key.split("|")
    war_score = -raw_score if len(parts) == 2 and parts[0] != player else raw_score

    records = list(getattr(world, 'battle_records', {}).get(diplo_key, []))
    french_casualties = 0
    enemy_casualties = 0
    for r in records:
        if r.get("attacker") == player:
            french_casualties += int(r.get("attacker_casualties", 0))
            enemy_casualties += int(r.get("defender_casualties", 0))
        else:
            french_casualties += int(r.get("defender_casualties", 0))
            enemy_casualties += int(r.get("attacker_casualties", 0))

    return {
        "war_duration": war_duration,
        "war_score": war_score,
        "french_casualties": french_casualties,
        "enemy_casualties": enemy_casualties,
    }


def build_peace_ratification_summary(
    world, proposer: str, target_nation: str,
    treaty: Dict, annotated_terms: List[Dict],
    applied_penalties: List[Dict],
    cancelled_orders: List[Dict],
    pre_cleanup_data: Dict,
) -> Dict:
    """BPH-D §11.1: Build the peace ratification summary returned on successful peace.

    ``pre_cleanup_data`` comes from ``_capture_pre_cleanup_war_data`` called
    before ``cleanup_war_end`` clears battle records and war scores.
    """
    from backend.models.region import NATION_CAPITALS

    player = world.player_nation
    war_duration = int(pre_cleanup_data.get("war_duration", 0))
    war_score = int(pre_cleanup_data.get("war_score", 0))
    french_casualties = int(pre_cleanup_data.get("french_casualties", 0))
    enemy_casualties = int(pre_cleanup_data.get("enemy_casualties", 0))

    # Territory and gold from treaty clauses
    territory_gained = []
    territory_lost = []
    gold_received = 0
    gold_paid = 0
    for clause in treaty.get("clauses", []):
        ctype = clause.get("type", "")
        if ctype == "territory_cede":
            regions = clause.get("regions", [])
            if clause.get("to") == player:
                territory_gained.extend(regions)
            elif clause.get("from") == player:
                territory_lost.extend(regions)
        elif ctype == "gold_lump":
            amount = abs(int(clause.get("amount", 0)))
            if clause.get("to") == player:
                gold_received += amount
            elif clause.get("from") == player:
                gold_paid += amount

    # §11.2 War outcome classification
    any_territory_changed = bool(territory_gained or territory_lost)
    any_gold_exchanged = bool(gold_received > 0 or gold_paid > 0)
    if war_score >= 30:
        war_outcome = "french_victory"
    elif war_score <= -30:
        war_outcome = "enemy_victory"
    elif any_territory_changed or any_gold_exchanged:
        war_outcome = "stalemate"
    else:
        war_outcome = "white_peace"

    # Ratified term display labels. BPH-A annotations use display_label;
    # older preview/fallout helpers may still pass display.
    terms_ratified = []
    for term in annotated_terms:
        label = term.get("display_label") or term.get("display") or ""
        if label:
            terms_ratified.append(label)

    # Political aftermath
    political_aftermath = []
    for p in applied_penalties:
        political_aftermath.append(p.get("display", ""))
    for c in cancelled_orders:
        name = c.get("marshal", "")
        target = c.get("target", "")
        if c.get("order_type") == "PURSUE":
            political_aftermath.append(f"{name}'s pursuit of {target} has been cancelled")
        else:
            political_aftermath.append(f"{name}'s march on {target} has been cancelled")

    target_state = treaty.get("state_transition", "").split("_TO_")[-1] if treaty.get("state_transition") else "PEACE"
    previous_state = treaty.get("state_transition", "").split("_TO_")[0] if treaty.get("state_transition") else "WAR"

    # Capital name for dispatch treaty name
    target_capital = NATION_CAPITALS.get(target_nation, target_nation)

    return {
        "target_nation": target_nation,
        "previous_state": previous_state,
        "new_state": target_state,
        "turn": int(world.current_turn),
        "war_duration_turns": int(war_duration),
        "war_outcome": war_outcome,
        "territory_gained": territory_gained,
        "territory_lost": territory_lost,
        "gold_received": int(gold_received),
        "gold_paid": int(gold_paid),
        "casualties_france": int(french_casualties),
        "casualties_enemy": int(enemy_casualties),
        "final_war_score": int(war_score),
        "terms_ratified": terms_ratified,
        "political_aftermath": [a for a in political_aftermath if a],
        "target_capital": target_capital,
    }


def get_peace_commitment_conflicts(
    world, proposer: str, target: str, clauses: List[Dict],
) -> List[Dict]:
    """BPH-C §10.1: Check for commitment conflicts created by a peace proposal.

    v0.1 conflict types:
      - paradox: alliance with a nation still at war with the target
      - bloc_opposition: proposer and target on opposing sides of hegemony geometry
    """
    conflicts: List[Dict] = []

    # Paradox: proposer allied with nation X, and X is at war with target
    all_nations = world.get_active_nations()
    for nation in all_nations:
        if nation == proposer or nation == target:
            continue
        ally_key = world._make_diplo_key(proposer, nation)
        ally_state = world.diplomatic_states.get(ally_key, "PEACE")
        if ally_state not in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
            continue
        target_key = world._make_diplo_key(nation, target)
        if world.diplomatic_states.get(target_key, "PEACE") != "WAR":
            continue
        conflicts.append({
            "conflict_type": "paradox",
            "severity": "HARD_STOP",
            "affected_entity": nation,
            "display": (
                f"Making peace with {target} while allied with {nation} "
                f"(who is still at war with {target}) creates a diplomatic contradiction."
            ),
            "detail": {
                "ally": nation,
                "ally_state_vs_target": "WAR",
            },
        })

    # Bloc-opposition: hegemony geometry check
    try:
        from backend.game_logic.coalition import _identify_max_bloc_share
        hegemon, share = _identify_max_bloc_share(world)
        if hegemon and share >= 0.30:
            proposer_members = set(world.get_bloc_members(hegemon))
            if proposer in proposer_members and target not in proposer_members:
                conflicts.append({
                    "conflict_type": "bloc_opposition",
                    "severity": "INFO",
                    "affected_entity": target,
                    "display": (
                        f"{target} sits outside your bloc. Peace normalizes relations "
                        f"with a nation resisting your European influence."
                    ),
                    "detail": {
                        "hegemon": hegemon,
                        "bloc_share": round(share, 2),
                    },
                })
    except (ImportError, AttributeError):
        pass

    # War bargain breach warning: proposer making peace/armistice with a named
    # enemy can breach a live bargain unless the terms resolve the claim.
    for bargain in _get_live_bargains(world):
        if bargain.get("promiser") != proposer or bargain.get("target_enemy") != target:
            continue
        claim_region = bargain.get("claim_term", {}).get("claim_region", "")
        if _peace_terms_transfer_claim_to_promiser(clauses, bargain):
            continue
        conflicts.append({
            "conflict_type": "bargain_breach",
            "severity": "WARNING",
            "affected_entity": bargain.get("beneficiary", ""),
            "display": (
                f"Peace with {target} would breach the bargain with "
                f"{bargain.get('beneficiary', 'the beneficiary')} over {claim_region}."
            ),
            "detail": {
                "bargain_id": bargain.get("id"),
                "beneficiary": bargain.get("beneficiary", ""),
                "target_enemy": target,
                "claim_region": claim_region,
            },
        })

    return conflicts


def _peace_terms_transfer_claim_to_promiser(clauses: List[Dict], bargain: Dict) -> bool:
    promiser = bargain.get("promiser", "")
    target_enemy = bargain.get("target_enemy", "")
    claim_region = bargain.get("claim_term", {}).get("claim_region", "")
    if not claim_region:
        return False
    for clause in clauses or []:
        if clause.get("type") != "territory_cede":
            continue
        if claim_region not in (clause.get("regions", []) or []):
            continue
        cede_to = clause.get("to", "") or clause.get("to_nation", "")
        cede_from = clause.get("from", "") or clause.get("from_nation", "")
        if cede_to and cede_to != promiser:
            continue
        if cede_from and cede_from != target_enemy:
            continue
        return True
    return False


def _collect_peace_order_cancellations(world, actor: str, counterpart: str) -> List[Dict]:
    """Return actor orders invalidated when actor and counterpart leave WAR."""
    cancelled = []
    target_marshals = {
        m.name for m in world.marshals.values() if m.nation == counterpart
    }
    target_regions = {
        name for name, region in getattr(world, "regions", {}).items()
        if getattr(region, "controller", "") == counterpart
    }
    target_regions.update(world.nation_starting_regions.get(counterpart, []))

    for marshal in world.marshals.values():
        if marshal.nation != actor:
            continue
        order = getattr(marshal, 'strategic_order', None)
        if not order:
            continue
        cmd_type = getattr(order, 'command_type', '')
        target_type = getattr(order, 'target_type', '')
        target_name = getattr(order, 'target', '')
        if cmd_type == "PURSUE" and target_type == "marshal" and target_name in target_marshals:
            cancelled.append({
                "marshal": marshal.name,
                "order_type": cmd_type,
                "target": target_name,
            })
        elif cmd_type == "MOVE_TO" and target_type == "marshal" and target_name in target_marshals:
            cancelled.append({
                "marshal": marshal.name,
                "order_type": cmd_type,
                "target": target_name,
            })
        elif cmd_type == "MOVE_TO" and target_type == "region" and target_name in target_regions:
            cancelled.append({
                "marshal": marshal.name,
                "order_type": cmd_type,
                "target": target_name,
            })
    return cancelled


def _get_order_cancellation_preview(world, proposer: str, target: str) -> Optional[Dict]:
    """BPH-C §9.4: List strategic orders that will be cancelled on peace ratification."""
    cancelled = _collect_peace_order_cancellations(world, proposer, target)

    if not cancelled:
        return None

    parts = []
    for c in cancelled:
        name = c["marshal"]
        if c["order_type"] == "PURSUE":
            parts.append(f"{name}'s pursuit of {c['target']}")
        else:
            parts.append(f"{name}'s march on {c['target']}")

    display = f"Peace with {target} will cancel " + " and ".join(parts) + "."
    return {
        "warning_type": "order_cancellation",
        "orders": cancelled,
        "severity": "INFO",
        "display": display,
    }


def _force_retreat_displaced_marshals(world, nation_a: str, nation_b: str) -> None:
    """Force-retreat marshals stranded in hostile territory after war ends.

    When an armistice/peace is signed, any marshal from nation_a in nation_b's
    territory (or vice versa) must be relocated to their nearest friendly region.
    Without this, stranded marshals create engagement deadlocks (C1 bug).
    """

    for marshal in list(world.marshals.values()):
        if marshal.strength <= 0:
            continue

        region = world.get_region(marshal.location)
        if not region:
            continue

        # Check if marshal is in hostile territory of the now-peaceful nation
        is_nation_a_in_b_territory = (
            marshal.nation == nation_a and region.controller == nation_b
        )
        is_nation_b_in_a_territory = (
            marshal.nation == nation_b and region.controller == nation_a
        )

        if not (is_nation_a_in_b_territory or is_nation_b_in_a_territory):
            continue

        # Find nearest friendly region via BFS
        retreat_to = _find_friendly_retreat(world, marshal)
        if retreat_to:
            marshal.move_to(retreat_to)
            # Cancel any strategic orders (they're now invalid)
            if getattr(marshal, 'strategic_order', None):
                marshal.strategic_order = None


def _find_friendly_retreat(world, marshal) -> str:
    """BFS to find nearest region controlled by marshal's nation."""
    from collections import deque

    start_region = world.get_region(marshal.location)
    if not start_region:
        return ""

    visited = {marshal.location}
    queue = deque()

    # Seed with adjacent regions
    for adj_name in start_region.adjacent_regions:
        if adj_name not in visited:
            visited.add(adj_name)
            queue.append(adj_name)

    while queue:
        region_name = queue.popleft()
        region = world.get_region(region_name)
        if not region:
            continue

        if region.controller == marshal.nation:
            return region_name

        for adj_name in region.adjacent_regions:
            if adj_name not in visited:
                visited.add(adj_name)
                queue.append(adj_name)

    # Fallback: capital
    from backend.models.region import NATION_CAPITALS
    capital = NATION_CAPITALS.get(marshal.nation, "")
    if capital and world.get_region(capital):
        return capital

    return ""


def cleanup_war_end(world, diplo_key: str, *,
                    conclude_objectives: bool = True) -> None:
    """Clean up war-related data when a war ends (R1b, R49, R47/R30).

    Called on WAR→ARMISTICE/PEACE transitions.
    - Clears battle_records, decisive_battles, war_scores for the pair
    - Resets war_exhaustion for both nations to 0
    - Cancels PURSUE/MOVE_TO strategic orders targeting the now-peaceful nation's marshals
    """
    # R1b: Clear war data
    battle_records = getattr(world, 'battle_records', {})
    decisive_battles = getattr(world, 'decisive_battles', {})
    war_scores = getattr(world, 'war_scores', {})
    war_score_history = getattr(world, 'war_score_history', {})

    battle_records.pop(diplo_key, None)
    decisive_battles.pop(diplo_key, None)
    war_scores.pop(diplo_key, None)
    war_score_history.pop(diplo_key, None)
    world.war_score_history = war_score_history

    # WPS-A: Conclude objectives only when the war is actually over.
    # ARMISTICE pauses ticking but must allow objectives to resume if war resumes.
    if conclude_objectives:
        _conclude_war_objectives(world, diplo_key)

    # R49: Reset war_exhaustion only for nations with no other active wars
    parts = diplo_key.split("|")
    war_exhaustion = getattr(world, 'war_exhaustion', {})
    if len(parts) == 2:
        for nation in parts:
            has_other_war = False
            for other_key, other_state in world.diplomatic_states.items():
                if other_key == diplo_key:
                    continue
                if other_state == "WAR" and nation in other_key.split("|"):
                    has_other_war = True
                    break
            if not has_other_war:
                war_exhaustion.pop(nation, None)

    # R142: Clear war start turn
    war_start_turns = getattr(world, 'war_start_turns', {})
    war_start_turns.pop(diplo_key, None)
    world.war_start_turns = war_start_turns

    # R69: Clear cascade_triggered entries for this war pair
    cascade_triggered = getattr(world, 'cascade_triggered', set())
    to_remove = {key for key in cascade_triggered if diplo_key in key}
    cascade_triggered -= to_remove
    world.cascade_triggered = cascade_triggered

    # R110: Clear stalemate counters for the war pair nations
    stalemate_counters = getattr(world, 'ai_stalemate_counters', {})
    if len(parts) == 2:
        stalemate_counters.pop(parts[0], None)
        stalemate_counters.pop(parts[1], None)
    world.ai_stalemate_counters = stalemate_counters

    # Force-retreat displaced marshals from hostile territory (C1 armistice deadlock fix)
    if len(parts) == 2:
        nation_a, nation_b = parts
        _force_retreat_displaced_marshals(world, nation_a, nation_b)

    # R47/R30 + BPH-C §9.4: Cancel orders targeting the now-peaceful nation
    if len(parts) == 2:
        nation_a, nation_b = parts
        cancellations = (
            _collect_peace_order_cancellations(world, nation_a, nation_b)
            + _collect_peace_order_cancellations(world, nation_b, nation_a)
        )
        for cancellation in cancellations:
            marshal = world.marshals.get(cancellation["marshal"])
            if marshal is not None:
                marshal.strategic_order = None

    # Slice B3 §7.5: a peace outcome resolves the bilateral pair on its
    # owning war_instance and (via the B3 lifecycle hooks inside
    # `resolve_pair_to_resolved`) closes contribution episodes for any
    # participants whose last active pair just disappeared. Armistice
    # outcomes leave the pair active (paused, not exited) so the helper is
    # only invoked when ``conclude_objectives`` is True.
    #
    # Idempotent against the existing armistice-expiration call site
    # (`_process_armistice_expiration` runs `resolve_pair_to_resolved`
    # before `cleanup_war_end`); the second invocation no-ops with
    # ``error="pair_not_owned"``.
    if conclude_objectives:
        resolve_pair_to_resolved(world, diplo_key)


# ═══════════════════════════════════════════════════════
# TERRITORY DEMAND ANALYSIS (PL-19/PL-20 shared helper)
# ═══════════════════════════════════════════════════════

def analyze_territory_demands(demands: list, target_nation: str, world) -> Dict:
    """Analyze territory demands for cost scaling and penalty calculations.

    Shared by PL-19 (relation penalty) and PL-20 (acceptance formula).
    Returns analysis dict with demanded regions, counts, income weights,
    escalating costs, and elimination status.
    """
    from backend.models.region import NATION_CAPITALS

    target_regions = world.get_nation_regions(target_nation)
    target_capital = NATION_CAPITALS.get(target_nation)

    # Collect all demanded territory regions, handling both formats
    demanded_regions_raw = []
    territory_demand_count_fallback = 0
    for d in demands:
        dtype = d.get("type", "")
        if dtype not in ("territory_cede", "territory"):
            continue
        regions_list = d.get("regions")
        if regions_list is not None:  # AM-20.6: empty [] is valid, distinct from None
            demanded_regions_raw.extend(regions_list)
        else:
            # Old saves / AI proposals with value-only (no regions list)
            territory_demand_count_fallback += int(d.get("value", 0) or 0)

    # AM-20.7: Dedup while preserving first occurrence
    valid_demanded = list(dict.fromkeys(
        r for r in demanded_regions_raw if r in target_regions
    ))

    demanded_count = len(valid_demanded) + territory_demand_count_fallback
    remaining = len(target_regions) - demanded_count
    is_annex = remaining <= 0 and demanded_count > 0
    is_rump = remaining == 1 and demanded_count > 0

    # Income weights and capital detection
    region_income_weights = {}
    capital_regions = set()
    regions_map = getattr(world, 'regions', {})
    for r in valid_demanded:
        region = regions_map.get(r)
        income = getattr(region, 'income_value', 100) if region else 100
        region_income_weights[r] = max(0.5, income / 100)
        if r == target_capital:
            capital_regions.add(r)

    # Sort by income ascending for deterministic escalation (cheapest first = hardest total)
    sorted_demanded = sorted(valid_demanded, key=lambda r: region_income_weights.get(r, 1.0))

    # PL-20 §A: Compute escalating costs per region
    # Base: -5, -8, -11, -14... (+3 per region), × income_weight, × 2 if capital
    escalating_costs = []
    for idx, r in enumerate(sorted_demanded):
        escalation = -5 - (3 * idx)
        weight = region_income_weights.get(r, 1.0)
        cost = escalation * weight
        if r in capital_regions:
            cost *= 2
        escalating_costs.append((r, cost))

    # Fallback escalating costs for value-only demands (no region identity)
    fallback_escalating_costs = []
    for i in range(territory_demand_count_fallback):
        idx = len(sorted_demanded) + i
        escalation = -5 - (3 * idx)
        fallback_escalating_costs.append(escalation)

    return {
        "demanded_regions": sorted_demanded,
        "demanded_count": demanded_count,
        "remaining": remaining,
        "is_annex": is_annex,
        "is_rump": is_rump,
        "region_income_weights": region_income_weights,
        "capital_regions": capital_regions,
        "escalating_costs": escalating_costs,
        "fallback_escalating_costs": fallback_escalating_costs,
        "territory_demand_count_fallback": territory_demand_count_fallback,
    }


# ═══════════════════════════════════════════════════════
# WAR BARGAINS — WB-A (data model + creation + validation)
# ═══════════════════════════════════════════════════════


BARGAIN_ARCHIVE_GRACE_TURNS = 10


def _mark_live_bargain_indexes_dirty(world) -> None:
    world._live_bargain_indexes_dirty = True


def _ensure_live_bargain_indexes(world) -> None:
    if not getattr(world, "_live_bargain_indexes_dirty", True):
        return

    live = []
    by_promiser = {}
    by_target_enemy = {}
    by_claim_region = {}

    for bargain in getattr(world, "diplomatic_commitments", {}).values():
        if not _is_bargain_live(bargain):
            continue
        live.append(bargain)
        promiser = bargain.get("promiser", "")
        target_enemy = bargain.get("target_enemy", "")
        claim_region = bargain.get("claim_term", {}).get("claim_region", "")
        if promiser:
            by_promiser.setdefault(promiser, []).append(bargain)
        if target_enemy:
            by_target_enemy.setdefault(target_enemy, []).append(bargain)
        if claim_region:
            by_claim_region.setdefault(claim_region, []).append(bargain)

    world._live_bargains_cache = live
    world._live_bargains_by_promiser = by_promiser
    world._live_bargains_by_target_enemy = by_target_enemy
    world._live_bargains_by_claim_region = by_claim_region
    world._live_bargain_indexes_dirty = False


def _get_live_bargains(world) -> list:
    """Return all bargains with status 'active' or 'triggered'."""
    _ensure_live_bargain_indexes(world)
    return [
        bargain for bargain in getattr(world, "_live_bargains_cache", [])
        if _is_bargain_live(bargain)
    ]


def _get_live_bargains_by_promiser(world, promiser: str) -> list:
    _ensure_live_bargain_indexes(world)
    return [
        bargain
        for bargain in getattr(world, "_live_bargains_by_promiser", {}).get(promiser, [])
        if _is_bargain_live(bargain)
    ]


def _archive_concluded_bargains(world, *, grace_turns: int = BARGAIN_ARCHIVE_GRACE_TURNS) -> int:
    """Move old terminal bargains out of the hot commitment store."""
    commitments = getattr(world, "diplomatic_commitments", {})
    if not commitments:
        return 0

    archived = getattr(world, "archived_diplomatic_commitments", None)
    if archived is None:
        world.archived_diplomatic_commitments = []
        archived = world.archived_diplomatic_commitments

    archived_count = 0
    current_turn = int(getattr(world, "current_turn", 0))
    for cid, bargain in list(commitments.items()):
        if _is_bargain_live(bargain):
            continue
        ended_turn = int(bargain.get("ended_turn") or 0)
        if not ended_turn or current_turn - ended_turn < grace_turns:
            continue
        archived_record = copy.deepcopy(bargain)
        archived_record["archived_turn"] = current_turn
        archived_record["archived_commitment_id"] = str(cid)
        archived.append(archived_record)
        del commitments[cid]
        archived_count += 1

    if archived_count:
        _mark_live_bargain_indexes_dirty(world)
    return archived_count


def _get_bargain_subject_lords(world) -> dict:
    """Return vassal -> lord mapping for bargain holder checks."""
    return {
        v.get("vassal_nation", ""): v.get("lord_nation", "")
        for v in getattr(world, "vassals", {}).values()
    } if hasattr(world, "vassals") else {}


def _region_is_held_by_enemy_or_subject(world, region_name: str, enemy: str) -> bool:
    region_obj = world.regions.get(region_name)
    holder = getattr(region_obj, "controller", "") if region_obj else ""
    return holder == enemy or _get_bargain_subject_lords(world).get(holder) == enemy


def _has_bargain_strategic_interest(world, promiser: str, claim_region: str) -> bool:
    """True when the claim has a minimal authored/positional basis."""
    if claim_region in getattr(world, "nation_starting_regions", {}).get(promiser, []):
        return True

    region_obj = world.regions.get(claim_region)
    if not region_obj:
        return False

    for adjacent_name in getattr(region_obj, "adjacent_regions", []):
        adjacent = world.regions.get(adjacent_name)
        if adjacent and getattr(adjacent, "controller", "") == promiser:
            return True

    try:
        from backend.game_logic.diplomatic_templates import NATION_DESIRE_PROFILES
    except Exception:
        NATION_DESIRE_PROFILES = {}
    for profile in NATION_DESIRE_PROFILES.values():
        if claim_region in profile.get("covets_regions", []):
            return True

    return False


def _bargain_controller_can_be_route_step(world, controller: str, promiser: str, beneficiary: str) -> bool:
    if not controller or controller in (promiser, beneficiary):
        return True
    return (
        world.get_diplomatic_state(controller, promiser) in ("DEFENSIVE_ALLIANCE", "ALLIANCE")
        or world.get_diplomatic_state(controller, beneficiary) in ("DEFENSIVE_ALLIANCE", "ALLIANCE")
    )


def _has_bargain_participation_access(
    world, promiser: str, beneficiary: str, target_enemy: str,
) -> bool:
    """Minimal WB-A access heuristic: direct border or 2-hop friendly/neutral route."""
    enemy_regions = {
        r_name for r_name in world.regions
        if _region_is_held_by_enemy_or_subject(world, r_name, target_enemy)
    }
    if not enemy_regions:
        return False

    starts = set(world.get_nation_regions(beneficiary))
    if not starts:
        return False

    frontier = [(r_name, 0) for r_name in starts if r_name in world.regions]
    visited = set(starts)
    while frontier:
        r_name, depth = frontier.pop(0)
        region_obj = world.regions.get(r_name)
        if not region_obj:
            continue
        for adjacent_name in getattr(region_obj, "adjacent_regions", []):
            if adjacent_name in enemy_regions:
                return True
            if depth >= 2 or adjacent_name in visited:
                continue
            adjacent = world.regions.get(adjacent_name)
            if not adjacent:
                continue
            controller = getattr(adjacent, "controller", "") or ""
            if _bargain_controller_can_be_route_step(
                world, controller, promiser, beneficiary,
            ):
                visited.add(adjacent_name)
                frontier.append((adjacent_name, depth + 1))

    return False


def _live_bargain_matches_breach_context(world, bargain: Dict, breaker: str, injured_party: str) -> bool:
    cr = bargain.get("claim_term", {}).get("claim_region", "")
    if not cr:
        return False
    region_obj = world.regions.get(cr)
    return bool(region_obj and getattr(region_obj, "controller", "") in (breaker, injured_party))


def get_bargain_opposition_pairs(world, promiser: str, beneficiary: str = "") -> set:
    """Derive valid (target_enemy) set for war bargain proposals.

    Sources: WAR states, active coalition members, live bargain conflicts.
    Does NOT read nation_rivalries or authored rivalry seed data.
    """
    opposition = set()
    for nation in world.get_active_nations():
        if nation == promiser or nation == beneficiary:
            continue
        if world.is_at_war(promiser, nation):
            opposition.add(nation)
        if beneficiary and world.is_at_war(beneficiary, nation):
            opposition.add(nation)

    coalition = getattr(world, "active_coalition", None)
    if coalition and coalition.get("target_nation") in (promiser, beneficiary):
        for member in coalition.get("members", []):
            if member != promiser and member != beneficiary:
                opposition.add(member)
    if coalition and (promiser in coalition.get("members", [])
                      or beneficiary in coalition.get("members", [])):
        target_nation = coalition.get("target_nation", "")
        if target_nation and target_nation not in (promiser, beneficiary):
            opposition.add(target_nation)

    for b in _get_live_bargains(world):
        if b.get("target_enemy") == promiser:
            ben = b.get("beneficiary", "")
            if ben and ben != promiser and ben != beneficiary:
                opposition.add(ben)
        if b.get("promiser") == promiser and b.get("beneficiary", "") != beneficiary:
            te = b.get("target_enemy", "")
            if te:
                opposition.add(te)

    opposition.discard(promiser)
    if beneficiary:
        opposition.discard(beneficiary)
    return opposition


def validate_war_bargain(
    world, promiser: str, beneficiary: str,
    target_enemy: str, claim_region: str,
    *,
    source_state: str = "",
) -> tuple:
    """Validate a war bargain. Returns (ok: bool, reason: str)."""
    state = source_state or world.get_diplomatic_state(promiser, beneficiary)
    if state not in ("DEFENSIVE_ALLIANCE", "ALLIANCE"):
        return (False, "Source treaty must be DEFENSIVE_ALLIANCE or ALLIANCE")

    opposition = get_bargain_opposition_pairs(world, promiser, beneficiary)
    if target_enemy not in opposition:
        return (False, f"{target_enemy} is not a valid opposition target")

    region_obj = world.regions.get(claim_region)
    if region_obj is None:
        return (False, f"Region {claim_region} does not exist")
    holder = getattr(region_obj, "controller", "")

    ally_state = world.get_diplomatic_state(promiser, holder)
    if holder and holder != target_enemy and ally_state in ("DEFENSIVE_ALLIANCE", "ALLIANCE"):
        return (False, f"Cannot bargain over ally-held region ({holder})")

    vassal_lords = _get_bargain_subject_lords(world)
    is_enemy_or_subject = (
        holder == target_enemy
        or vassal_lords.get(holder) == target_enemy
    )
    if not is_enemy_or_subject:
        return (False, f"{claim_region} is not held by {target_enemy} or its subject")

    if not _has_bargain_strategic_interest(world, promiser, claim_region):
        return (False, f"{claim_region} has no plausible strategic interest for {promiser}")

    if not _has_bargain_participation_access(world, promiser, beneficiary, target_enemy):
        return (False, f"{beneficiary} has no plausible participation access against {target_enemy}")

    live = _get_live_bargains(world)

    for b in live:
        if b.get("beneficiary") == beneficiary and b.get("target_enemy") == target_enemy:
            return (False, f"Already have a live bargain with {beneficiary} against {target_enemy}")

    for b in live:
        if b.get("claim_term", {}).get("claim_region") == claim_region:
            return (False, f"Already have a live bargain claiming {claim_region}")

    for b in live:
        if (b.get("promiser") == promiser
                and b.get("beneficiary") == target_enemy
                and b.get("target_enemy") == beneficiary):
            return (False, f"Contradictory bargain: already promised {target_enemy} against {beneficiary}")

    cooldown_key = f"{promiser}|{beneficiary}::{target_enemy}"
    for b in getattr(world, "diplomatic_commitments", {}).values():
        if b.get("cooldown_key") == cooldown_key:
            cu = b.get("cooldown_until_turn", 0)
            if cu and int(cu) > int(world.current_turn):
                return (False, f"Cooldown active until turn {cu}")

    return (True, "")


def _resolve_bargain_war_context(
    world, promiser: str, target_enemy: str,
) -> tuple:
    """Resolve the (war_id, side_at_creation, side_leader_at_creation) tuple
    for a bargain about to be created against `target_enemy` from `promiser`.

    Per spec §11.3 line 1573, these three fields snapshot the war-instance
    context at bargain creation. `war_id` may be rewritten on later merges
    (`_rewrite_absorbed_war_id_in_bargains`), but the side / side-leader
    context stays fixed for fulfillment / breach classification.

    Returns ``(war_id_or_None, side_or_None, side_leader_or_None)``. Any
    field is ``None`` when no active war_instance covers the (promiser,
    target_enemy) pair (typical for forward-bargains attached pre-WAR via
    the WB-C ally-entry review).
    """
    if not promiser or not target_enemy:
        return (None, None, None)
    instances = getattr(world, "war_instances", None) or {}
    if not instances:
        return (None, None, None)
    for war_id, instance in instances.items():
        if not isinstance(instance, dict):
            continue
        if instance.get("ended_turn") is not None:
            continue
        side_by_nation = instance.get("side_by_nation") or {}
        promiser_side = side_by_nation.get(promiser)
        target_side = side_by_nation.get(target_enemy)
        if not promiser_side or not target_side:
            continue
        if promiser_side == target_side:
            continue  # Both on same side -- not a war between them.
        leader_key = (
            "attacker_leader" if promiser_side == "attackers" else "defender_leader"
        )
        side_leader = instance.get(leader_key) or None
        return (war_id, promiser_side, side_leader)
    return (None, None, None)


def create_war_bargain_commitment(
    world, promiser: str, beneficiary: str,
    target_enemy: str, claim_region: str,
    origin_mode: str, source_treaty_key: str,
    *,
    validate: bool = True,
    source_state: str = "",
) -> Dict:
    """Create and store a war bargain commitment record."""
    if validate:
        ok, reason = validate_war_bargain(
            world, promiser, beneficiary, target_enemy, claim_region,
            source_state=source_state,
        )
        if not ok:
            raise ValueError(reason)

    region_obj = world.regions.get(claim_region)
    claim_holder = getattr(region_obj, "controller", target_enemy) if region_obj else target_enemy

    cid = int(getattr(world, "next_commitment_id", 1) or 1)
    world.next_commitment_id = cid + 1

    # A3 §11.3 / §7.6: snapshot war-instance attachment context at creation.
    # `war_id` is rewritten on merge (Step 6 / `_rewrite_absorbed_war_id_in_bargains`),
    # but `side_at_creation` / `side_leader_at_creation` are PRESERVED through
    # merges -- they record the bargain's promise context, not live state.
    war_id_at_creation, side_at_creation, side_leader_at_creation = (
        _resolve_bargain_war_context(world, promiser, target_enemy)
    )

    record = {
        "id": cid,
        "type": "war_bargain",
        "promiser": promiser,
        "beneficiary": beneficiary,
        "origin_mode": origin_mode,
        "target_enemy": target_enemy,
        "entry_term": {"named_enemy": target_enemy},
        "claim_term": {
            "claimant": promiser,
            "claim_region": claim_region,
            "claim_holder": claim_holder,
        },
        "created_turn": int(world.current_turn),
        "triggered_turn": None,
        "ended_turn": None,
        "status": "active",
        "source_treaty": source_treaty_key,
        "source_pair": f"{promiser}|{beneficiary}",
        "cooldown_key": f"{promiser}|{beneficiary}::{target_enemy}",
        "cooldown_until_turn": 0,
        "end_reason": None,
        "end_reason_family": None,
        "fault_nation": None,
        "trigger_context": None,
        "fulfillment_snapshot": None,
        "zombie_clock_turns_elapsed": 0,
        "dormant_notice_fired": False,
        "war_id": war_id_at_creation,
        "side_at_creation": side_at_creation,
        "side_leader_at_creation": side_leader_at_creation,
    }

    if not hasattr(world, "diplomatic_commitments"):
        world.diplomatic_commitments = {}
    world.diplomatic_commitments[str(cid)] = record
    _mark_live_bargain_indexes_dirty(world)
    _emit_bargain_event(world, record, "bargain_ratified")
    return record


# ═══════════════════════════════════════════════════════
# WB-B: WAR BARGAIN LIFECYCLE (§8.8 / §8.9)
# ═══════════════════════════════════════════════════════

BARGAIN_BREACH_COOLDOWN_TURNS = 6
BARGAIN_VOID_COOLDOWN_TURNS = 4
BARGAIN_ZOMBIE_VOID_THRESHOLD = 5
BARGAIN_FULFILLMENT_RELIABILITY_DELTA = 4
BARGAIN_FULFILLMENT_RELATION_DELTA = 6
BARGAIN_BREACH_RELIABILITY_DELTA = -6
BARGAIN_BREACH_RELATION_DELTA = -10
BARGAIN_FULFILLMENT_PAIR_COOLDOWN_TURNS = 10


def _is_bargain_live(bargain: Dict) -> bool:
    return bargain.get("status") in ("active", "triggered")


def _get_source_treaty_state(world, bargain: Dict) -> str:
    promiser = bargain.get("promiser", "")
    beneficiary = bargain.get("beneficiary", "")
    if not promiser or not beneficiary:
        return "PEACE"
    return world.get_diplomatic_state(promiser, beneficiary)


def _source_treaty_valid(world, bargain: Dict) -> bool:
    return _get_source_treaty_state(world, bargain) in ("DEFENSIVE_ALLIANCE", "ALLIANCE")


def _claim_basis_valid(world, bargain: Dict) -> bool:
    """Claim region still held by named enemy or its subject."""
    cr = bargain.get("claim_term", {}).get("claim_region", "")
    enemy = bargain.get("target_enemy", "")
    if not cr or not enemy:
        return False
    return _region_is_held_by_enemy_or_subject(world, cr, enemy)


def _are_cobelligerents(world, nation_a: str, nation_b: str, against: str) -> bool:
    """Both nations at WAR with the target enemy."""
    return (
        world.is_at_war(nation_a, against)
        and world.is_at_war(nation_b, against)
    )


def _bargain_key(bargain: Dict) -> str:
    return str(bargain.get("id", ""))


def _record_bargain_cobelligerent_war_end(world, nation_a: str, nation_b: str) -> None:
    """Remember triggered bargains whose named war ended after valid co-belligerence."""
    ended_pair = {nation_a, nation_b}
    snapshots = dict(getattr(world, "_bargain_cobelligerent_war_end_turns", {}) or {})

    for bargain in _get_live_bargains(world):
        if bargain.get("status") != "triggered":
            continue
        promiser = bargain.get("promiser", "")
        beneficiary = bargain.get("beneficiary", "")
        target_enemy = bargain.get("target_enemy", "")
        if target_enemy not in ended_pair:
            continue
        if promiser not in ended_pair and beneficiary not in ended_pair:
            continue
        if _are_cobelligerents(world, promiser, beneficiary, target_enemy):
            key = _bargain_key(bargain)
            if key:
                snapshots[key] = int(world.current_turn)

    world._bargain_cobelligerent_war_end_turns = snapshots


def _had_bargain_cobelligerent_war_end_this_turn(world, bargain: Dict) -> bool:
    snapshots = getattr(world, "_bargain_cobelligerent_war_end_turns", {}) or {}
    turn = snapshots.get(_bargain_key(bargain))
    return turn is not None and int(turn) == int(world.current_turn)


def process_bargain_lifecycle(world) -> List[Dict]:
    """Per-turn bargain lifecycle processing per §8.8 turn-order rule.

    Called from process_diplomacy_turn AFTER war-state/region mutations.
    Returns events for dispatch/campaign log.
    """
    events = []
    commitments = getattr(world, "diplomatic_commitments", {})
    if not commitments:
        return events

    for bargain in _get_live_bargains(world):
        if not _is_bargain_live(bargain):
            continue

        promiser = bargain.get("promiser", "")
        beneficiary = bargain.get("beneficiary", "")
        target_enemy = bargain.get("target_enemy", "")

        # §8.8 Triggering: active → triggered when co-belligerents
        if bargain["status"] == "active":
            if _are_cobelligerents(world, promiser, beneficiary, target_enemy):
                bargain["status"] = "triggered"
                bargain["triggered_turn"] = int(world.current_turn)
                ev = _emit_bargain_event(world, bargain, "bargain_triggered")
                events.append(ev)

        # §8.8 Fulfillment check (only on triggered)
        if bargain["status"] == "triggered":
            if _check_bargain_fulfillment(world, bargain):
                _fulfill_bargain(world, bargain)
                ev = _emit_bargain_event(world, bargain, "bargain_fulfilled")
                events.append(ev)
                continue

        # §8.8 Inconclusive war reactivation: triggered → active
        if bargain["status"] == "triggered":
            if not _are_cobelligerents(world, promiser, beneficiary, target_enemy):
                if _source_treaty_valid(world, bargain) and _claim_basis_valid(world, bargain):
                    bargain["status"] = "active"
                    bargain["dormant_notice_fired"] = False
                    bargain["_reactivated_turn"] = int(world.current_turn)

        # §8.9.B Void detection
        void_reason = _detect_void(world, bargain)
        if void_reason:
            _void_bargain(world, bargain, void_reason)
            ev = _emit_bargain_event(world, bargain, "bargain_voided")
            events.append(ev)
            continue

        # Zombie clock processing (§8.9.B)
        _process_zombie_clock(world, bargain)
        if bargain.get("status") == "void":
            ev = _emit_bargain_event(world, bargain, "bargain_voided")
            events.append(ev)
            continue

        # Dormant notice (§10.2): 8+ turns active without triggering
        if bargain["status"] == "active" and not bargain.get("dormant_notice_fired"):
            base_turn = bargain.get("_reactivated_turn") or bargain.get("created_turn", 0)
            turns_active = int(world.current_turn) - int(base_turn)
            if turns_active >= 8:
                bargain["dormant_notice_fired"] = True
                _emit_bargain_dormant_notice(world, bargain, turns_active)

    _archive_concluded_bargains(world)
    return events


def _check_bargain_fulfillment(world, bargain: Dict) -> bool:
    """§8.8: All five conditions must hold at end of turn."""
    if bargain.get("status") != "triggered":
        return False

    promiser = bargain.get("promiser", "")
    beneficiary = bargain.get("beneficiary", "")
    target_enemy = bargain.get("target_enemy", "")
    claim_region = bargain.get("claim_term", {}).get("claim_region", "")

    if not claim_region:
        return False

    # 2. France controls the claimed region
    region_obj = world.regions.get(claim_region)
    if not region_obj or getattr(region_obj, "controller", "") != promiser:
        return False

    # 4. Source treaty still valid
    if not _source_treaty_valid(world, bargain):
        return False

    # 5. Co-belligerents, or the named war just ended this turn after co-belligerence.
    if not (
        _are_cobelligerents(world, promiser, beneficiary, target_enemy)
        or _had_bargain_cobelligerent_war_end_this_turn(world, bargain)
    ):
        return False

    return True


def _fulfill_bargain(world, bargain: Dict) -> None:
    """Mark bargain fulfilled and apply rewards."""
    bargain["status"] = "fulfilled"
    bargain["ended_turn"] = int(world.current_turn)
    _mark_live_bargain_indexes_dirty(world)

    promiser = bargain.get("promiser", "")
    beneficiary = bargain.get("beneficiary", "")

    # §8.8 Reward: +4 reliability, capped per (promiser, beneficiary) per 10 turns
    reliability_delta = BARGAIN_FULFILLMENT_RELIABILITY_DELTA
    intended_delta = reliability_delta
    reward_reduced = "none"

    fulfillment_log = getattr(world, "_bargain_fulfillment_log", {})
    pair_key = f"{promiser}|{beneficiary}"
    last_fulfilled_turn = fulfillment_log.get(pair_key, 0)
    if last_fulfilled_turn and (int(world.current_turn) - int(last_fulfilled_turn)) < BARGAIN_FULFILLMENT_PAIR_COOLDOWN_TURNS:
        reliability_delta = 0
        reward_reduced = "full"

    if not hasattr(world, "_bargain_fulfillment_log"):
        world._bargain_fulfillment_log = {}
    world._bargain_fulfillment_log[pair_key] = int(world.current_turn)

    # Apply reliability
    reliability = getattr(world, "diplomatic_reliability", {})
    old_rel = reliability.get(promiser, 0)
    new_rel = max(-100, min(100, old_rel + reliability_delta))
    reliability[promiser] = new_rel
    if not hasattr(world, "diplomatic_reliability"):
        world.diplomatic_reliability = reliability

    # +6 relation with beneficiary
    relation_delta = BARGAIN_FULFILLMENT_RELATION_DELTA
    world.modify_nation_relation(promiser, beneficiary, relation_delta)

    bargain["fulfillment_snapshot"] = {
        "claim_region": bargain.get("claim_term", {}).get("claim_region", ""),
        "beneficiary": beneficiary,
        "target_enemy": bargain.get("target_enemy", ""),
        "fulfilled_turn": int(world.current_turn),
        "reliability_delta": reliability_delta,
        "relation_delta": relation_delta,
        "reward_reduced": reward_reduced,
        "intended_reliability_delta": intended_delta,
        "witness_nations_at_fulfillment": _get_bargain_witnesses(world, bargain),
        "trigger_context": bargain.get("trigger_context"),
    }


def breach_bargain(world, bargain: Dict, end_reason: str, *, episode_id: str = None) -> Dict:
    """Mark a live bargain as breached and apply penalties.

    Called from explicit breach actions (repudiate_bargain, source treaty break,
    normalization with named enemy, etc.). Returns event metadata.
    """
    if not _is_bargain_live(bargain):
        return {}

    episode_id = episode_id or _allocate_episode_id(world, prefix="bargain")
    bargain["status"] = "breached"
    bargain["ended_turn"] = int(world.current_turn)
    _mark_live_bargain_indexes_dirty(world)
    bargain["end_reason"] = end_reason
    bargain["end_reason_family"] = "french_breach"
    bargain["fault_nation"] = bargain.get("promiser", "France")
    bargain["breach_episode_id"] = episode_id

    promiser = bargain.get("promiser", "")
    beneficiary = bargain.get("beneficiary", "")
    target_enemy = bargain.get("target_enemy", "")

    # Cooldown: 6 turns
    bargain["cooldown_until_turn"] = int(world.current_turn) + BARGAIN_BREACH_COOLDOWN_TURNS

    # Reliability loss: -6
    reliability = getattr(world, "diplomatic_reliability", {})
    old_rel = reliability.get(promiser, 0)
    new_rel = max(-100, min(100, old_rel + BARGAIN_BREACH_RELIABILITY_DELTA))
    reliability[promiser] = new_rel
    if not hasattr(world, "diplomatic_reliability"):
        world.diplomatic_reliability = reliability

    # Relation penalty: -10
    world.modify_nation_relation(promiser, beneficiary, BARGAIN_BREACH_RELATION_DELTA)

    # Betrayal strike: +1 unless same episode already spent 2-strike cap
    _record_bargain_breach_strike(world, promiser, beneficiary, episode_id)

    ev = _emit_bargain_event(world, bargain, "bargain_breached")
    return ev


def _record_bargain_breach_strike(world, promiser: str, beneficiary: str, episode_id: str = None):
    """Record +1 betrayal strike for bargain breach, respecting 2-strike-per-episode cap."""
    betrayal_history = getattr(world, "betrayal_history", {})
    diplo_key = _betrayal_key(promiser, beneficiary)
    record = betrayal_history.get(diplo_key)
    if record is None:
        record = {"strikes": [], "categories": [], "grievance_flags": [], "last_turn": 0}
        betrayal_history[diplo_key] = record
    if not hasattr(world, "betrayal_history"):
        world.betrayal_history = betrayal_history

    if episode_id:
        active_episode_strikes = sum(
            1 for s in _get_active_betrayal_strikes(world, promiser, beneficiary)
            if s.get("episode_id") == episode_id
        )
        if active_episode_strikes >= 2:
            return

    record["strikes"].append({
        "severity": "medium",
        "turn": int(world.current_turn),
        "source": "bargain_breach",
        "episode_id": episode_id or "",
        "decays_on_turn": int(world.current_turn) + 20,
    })
    categories = set(record.get("categories", []) or [])
    categories.add("bargain_breach")
    record["categories"] = sorted(categories)
    record["last_turn"] = int(world.current_turn)
    betrayal_history[diplo_key] = record
    world.betrayal_history = betrayal_history


def _void_bargain(world, bargain: Dict, void_info: Dict) -> None:
    """Mark bargain as void without French penalty."""
    bargain["status"] = "void"
    bargain["ended_turn"] = int(world.current_turn)
    _mark_live_bargain_indexes_dirty(world)
    bargain["end_reason"] = void_info.get("reason", "external")
    bargain["end_reason_family"] = void_info.get("family", "obsolescence_or_external")
    bargain["fault_nation"] = void_info.get("fault_nation")
    if void_info.get("decision_reason"):
        bargain["decision_reason"] = void_info.get("decision_reason")

    # Cooldown: 4 turns
    bargain["cooldown_until_turn"] = int(world.current_turn) + BARGAIN_VOID_COOLDOWN_TURNS


def _detect_void(world, bargain: Dict) -> Optional[Dict]:
    """Detect void conditions per §8.9.B. Returns void info dict or None."""
    if not _is_bargain_live(bargain):
        return None

    promiser = bargain.get("promiser", "")
    beneficiary = bargain.get("beneficiary", "")
    target_enemy = bargain.get("target_enemy", "")

    # Counterparty reversal: beneficiary breaks source treaty
    source_state = _get_source_treaty_state(world, bargain)
    if source_state not in ("DEFENSIVE_ALLIANCE", "ALLIANCE"):
        return {
            "reason": "source_treaty_lost",
            "family": "counterparty_reversal",
            "fault_nation": beneficiary,
        }

    # Counterparty reversal: beneficiary aligned with named enemy
    ben_enemy_state = world.get_diplomatic_state(beneficiary, target_enemy)
    if ben_enemy_state in ("NON_AGGRESSION", "OPEN_BORDERS", "DEFENSIVE_ALLIANCE", "ALLIANCE"):
        return {
            "reason": "beneficiary_aligned_with_enemy",
            "family": "counterparty_reversal",
            "fault_nation": beneficiary,
        }

    # Counterparty reversal: beneficiary joins anti-promiser coalition
    coalition = getattr(world, "active_coalition", None)
    if coalition and coalition.get("target_nation") == promiser:
        if beneficiary in coalition.get("members", []):
            return {
                "reason": "beneficiary_joined_anti_promiser_coalition",
                "family": "counterparty_reversal",
                "fault_nation": beneficiary,
            }

    # Obsolescence: claim basis gone (enemy no longer holds region)
    if not _claim_basis_valid(world, bargain):
        return {
            "reason": "claim_basis_lost",
            "family": "obsolescence_or_external",
            "fault_nation": None,
        }

    # Obsolescence: promiser and beneficiary now direct enemies through external cause
    if world.is_at_war(promiser, beneficiary):
        return {
            "reason": "parties_at_war",
            "family": "obsolescence_or_external",
            "fault_nation": None,
        }

    return None


def _process_zombie_clock(world, bargain: Dict) -> None:
    """§8.9.B: Zombie clock increments when both sides at ARMISTICE+ with enemy."""
    if not _is_bargain_live(bargain):
        return

    promiser = bargain.get("promiser", "")
    beneficiary = bargain.get("beneficiary", "")
    target_enemy = bargain.get("target_enemy", "")

    promiser_state = world.get_diplomatic_state(promiser, target_enemy)
    beneficiary_state = world.get_diplomatic_state(beneficiary, target_enemy)

    armistice_or_higher = ("ARMISTICE", "PEACE", "NON_AGGRESSION", "OPEN_BORDERS",
                           "DEFENSIVE_ALLIANCE", "ALLIANCE")

    # Reset if either side is at WAR
    if promiser_state == "WAR" or beneficiary_state == "WAR":
        bargain["zombie_clock_turns_elapsed"] = 0
        return

    # Increment if both sides at ARMISTICE or higher
    if promiser_state in armistice_or_higher and beneficiary_state in armistice_or_higher:
        bargain["zombie_clock_turns_elapsed"] = int(bargain.get("zombie_clock_turns_elapsed", 0)) + 1

    # Void at threshold
    if int(bargain.get("zombie_clock_turns_elapsed", 0)) >= BARGAIN_ZOMBIE_VOID_THRESHOLD:
        _void_bargain(world, bargain, {
            "reason": "zombie_lapse",
            "family": "obsolescence_or_external",
            "fault_nation": None,
        })


def _get_bargain_witnesses(world, bargain: Dict) -> List[Dict[str, str]]:
    """Get scope-classified witness nations for a bargain event.

    Returns list of {"nation": str, "scope_reason": str} dicts, reusing the
    existing witness scope classification from the commitments substrate.
    """
    promiser = bargain.get("promiser", "")
    beneficiary = bargain.get("beneficiary", "")
    witnesses: List[Dict[str, str]] = []
    for nation in world.get_active_nations():
        if nation in (promiser, beneficiary):
            continue
        scope_reason = _classify_witness_scope(world, nation, promiser, beneficiary)
        if scope_reason:
            witnesses.append({"nation": nation, "scope_reason": scope_reason})
    return witnesses


def _get_bargain_dominant_witness_scope(witnesses: List[Dict[str, str]]) -> str:
    """Return the dominant witness scope from a classified witness list."""
    for role in WITNESS_SCOPE_PRECEDENCE:
        if any(w.get("scope_reason") == role for w in witnesses):
            return role
    return ""


def _emit_bargain_event(world, bargain: Dict, event_type: str) -> Dict:
    """Emit campaign log + dispatch + notification for a bargain state change."""
    promiser = bargain.get("promiser", "")
    beneficiary = bargain.get("beneficiary", "")
    target_enemy = bargain.get("target_enemy", "")
    claim_region = bargain.get("claim_term", {}).get("claim_region", "")

    witnesses = _get_bargain_witnesses(world, bargain)
    dominant_scope = _get_bargain_dominant_witness_scope(witnesses)

    event = {
        "type": event_type,
        "turn": int(world.current_turn),
        "bargain_id": bargain.get("id"),
        "promiser": promiser,
        "beneficiary": beneficiary,
        "target_enemy": target_enemy,
        "claim_region": claim_region,
        "status": bargain.get("status"),
        "end_reason": bargain.get("end_reason"),
        "end_reason_family": bargain.get("end_reason_family"),
        "fault_nation": bargain.get("fault_nation"),
        "decision_reason": bargain.get("decision_reason", ""),
        "episode_id": bargain.get("breach_episode_id", ""),
        "actor_nation": promiser,
        "target_nation": beneficiary,
        "dominant_witness_scope": dominant_scope,
        "witnesses": witnesses,
    }

    world.log_event(event)

    from backend.game_logic.dispatch import queue_dispatch_event
    fog_rule = "always" if event_type != "bargain_voided" else "partial_on_nation"

    from backend.game_logic.diplomatic_templates import resolve_named_diplomat
    injured_diplomat = resolve_named_diplomat("envoy", beneficiary, world)

    dispatch_vars = {
        "promiser": promiser,
        "beneficiary": beneficiary,
        "target_enemy": target_enemy,
        "claim_region": claim_region,
        "end_reason": bargain.get("end_reason", ""),
        "end_reason_family": bargain.get("end_reason_family", ""),
        "fault_nation": bargain.get("fault_nation", ""),
        "decision_reason": bargain.get("decision_reason", ""),
        "episode_id": bargain.get("breach_episode_id", ""),
        "actor_nation": promiser,
        "target_nation": beneficiary,
        "dominant_witness_scope": dominant_scope,
        "injured_diplomat": injured_diplomat,
        "review_nation": beneficiary,
    }
    queue_dispatch_event(world, event_type, dispatch_vars, fog_rule)

    _emit_bargain_notification(world, event_type, dispatch_vars)

    return event


def _emit_bargain_notification(world, event_type: str, template_vars: Dict) -> None:
    """Emit persistent notification for terminal bargain states."""
    from backend.notifications import (
        create_notification, NotificationPriority,
        BARGAIN_FULFILLED, BARGAIN_BREACHED, BARGAIN_VOIDED,
    )
    from backend.game_logic.commitments_routing import (
        commitments_label, format_commitments_notice, commitments_notice_details,
        commitments_priority,
    )

    notification_map = {
        "bargain_fulfilled": (BARGAIN_FULFILLED, NotificationPriority.HIGH),
        "bargain_breached": (BARGAIN_BREACHED, NotificationPriority.CRITICAL),
        "bargain_voided": (BARGAIN_VOIDED, NotificationPriority.NORMAL),
    }

    entry = notification_map.get(event_type)
    if not entry:
        return

    notif_type, priority = entry
    routed_priority = commitments_priority(event_type, template_vars)
    if routed_priority == "NORMAL":
        priority = NotificationPriority.NORMAL
    elif routed_priority == "CRITICAL":
        priority = NotificationPriority.CRITICAL

    title = commitments_label(event_type, template_vars)
    message = format_commitments_notice(event_type, template_vars)
    details = commitments_notice_details(event_type, template_vars)

    world.notifications.add(create_notification(
        notif_type,
        priority,
        title,
        message,
        int(getattr(world, "current_turn", 1)),
        details=details,
    ))


def _emit_bargain_dormant_notice(world, bargain: Dict, turns_active: int) -> None:
    from backend.game_logic.dispatch import queue_dispatch_event

    queue_dispatch_event(world, "bargain_dormant_notice", {
        "promiser": bargain.get("promiser", ""),
        "beneficiary": bargain.get("beneficiary", ""),
        "target_enemy": bargain.get("target_enemy", ""),
        "claim_region": bargain.get("claim_term", {}).get("claim_region", ""),
        "turns_active": int(turns_active),
    }, "always")


def detect_bargain_breach_on_treaty_change(
    world, breaker: str, other_nation: str, new_state: str, *,
    episode_id: str = None,
) -> List[Dict]:
    """Check if a diplomatic state change breaches any live bargain.

    Called from explicit treaty break, downgrade, and ratification paths.
    Returns list of breach events.
    """
    events = []

    for bargain in _get_live_bargains_by_promiser(world, breaker):
        if not _is_bargain_live(bargain):
            continue

        promiser = bargain.get("promiser", "")
        beneficiary = bargain.get("beneficiary", "")
        target_enemy = bargain.get("target_enemy", "")

        # Source treaty break/downgrade by promiser
        if breaker == promiser and other_nation == beneficiary:
            if new_state not in ("DEFENSIVE_ALLIANCE", "ALLIANCE"):
                episode_id = episode_id or _allocate_episode_id(world, prefix="bargain")
                ev = breach_bargain(world, bargain, "source_treaty_downgrade", episode_id=episode_id)
                if ev:
                    events.append(ev)
                continue

        # Normalization with named enemy or claim holder
        if breaker == promiser and other_nation == target_enemy:
            if new_state in ("NON_AGGRESSION", "OPEN_BORDERS", "DEFENSIVE_ALLIANCE", "ALLIANCE"):
                episode_id = episode_id or _allocate_episode_id(world, prefix="bargain")
                ev = breach_bargain(world, bargain, "normalization_with_enemy", episode_id=episode_id)
                if ev:
                    events.append(ev)
                continue

        # Check claim holder normalization
        claim_region = bargain.get("claim_term", {}).get("claim_region", "")
        if claim_region and breaker == promiser:
            region_obj = world.regions.get(claim_region)
            holder = getattr(region_obj, "controller", "") if region_obj else ""
            if holder == other_nation and holder != target_enemy:
                if new_state in ("NON_AGGRESSION", "OPEN_BORDERS", "DEFENSIVE_ALLIANCE", "ALLIANCE"):
                    episode_id = episode_id or _allocate_episode_id(world, prefix="bargain")
                    ev = breach_bargain(world, bargain, "normalization_with_holder", episode_id=episode_id)
                    if ev:
                        events.append(ev)

    return events


def detect_bargain_breach_on_peace(
    world, nation_a: str, nation_b: str, *, episode_id: str = None,
) -> List[Dict]:
    """Check if peace/armistice with named enemy breaches a live bargain.

    Called from peace ratification paths.
    """
    events = []
    candidates = []
    seen = set()
    for promiser in (nation_a, nation_b):
        for bargain in _get_live_bargains_by_promiser(world, promiser):
            bid = id(bargain)
            if bid not in seen:
                candidates.append(bargain)
                seen.add(bid)

    for bargain in candidates:
        if not _is_bargain_live(bargain):
            continue

        promiser = bargain.get("promiser", "")
        target_enemy = bargain.get("target_enemy", "")
        if _check_bargain_fulfillment(world, bargain):
            continue

        if promiser == nation_a and target_enemy == nation_b:
            episode_id = episode_id or _allocate_episode_id(world, prefix="bargain")
            ev = breach_bargain(world, bargain, "peace_with_named_enemy", episode_id=episode_id)
            if ev:
                events.append(ev)
        elif promiser == nation_b and target_enemy == nation_a:
            episode_id = episode_id or _allocate_episode_id(world, prefix="bargain")
            ev = breach_bargain(world, bargain, "peace_with_named_enemy", episode_id=episode_id)
            if ev:
                events.append(ev)

    return events


# ═══════════════════════════════════════════════════════
# WAR BARGAINS — WB-C (war-entry integration + ally entry)
# ═══════════════════════════════════════════════════════

WAR_ENTRY_BASE = 20
WAR_ENTRY_TREATY_BONUS = {"DEFENSIVE_ALLIANCE": 10, "ALLIANCE": 18}
WAR_ENTRY_DEFENSIVE_HONOR_BONUS = 18
WAR_ENTRY_OPPOSITION_PAIR_BONUS = 6
WAR_ENTRY_BARGAIN_BONUS = 25
WAR_ENTRY_BETRAYAL_PENALTY_PER_STRIKE = -8
WAR_ENTRY_BETRAYAL_CAP = -24
WAR_ENTRY_WAR_LOAD_ONE = -8
WAR_ENTRY_WAR_LOAD_MULTI = -18
WAR_ENTRY_WAR_EXHAUSTION_THRESHOLD = 60
WAR_ENTRY_JOIN_THRESHOLD = 50
WAR_ENTRY_COUNTER_BARGAIN_THRESHOLD = 25


def _count_betrayal_strikes_against(world, victim: str, breaker: str) -> int:
    """Count active strikes where breaker hurt victim. Delegates to the
    canonical _get_active_betrayal_strike_count (actor=breaker, victim=victim)."""
    return _get_active_betrayal_strike_count(world, breaker, victim)


def _count_active_wars(world, nation: str) -> int:
    """Count how many nations this nation is at WAR with."""
    count = 0
    for other in world.get_active_nations():
        if other != nation and world.is_at_war(nation, other):
            count += 1
    return count


def _get_war_exhaustion(world, nation: str) -> int:
    """Get war exhaustion for a nation."""
    return int(getattr(world, "war_exhaustion", {}).get(nation, 0))


def compute_war_entry_score(
    world,
    promiser: str,
    beneficiary: str,
    named_enemy: str,
    *,
    is_defensive: bool = False,
) -> Dict:
    """Dedicated war-entry score per §9.4.

    Returns {"score": int, "band": str, "components": dict}
    where band is "join" / "counter_bargain" / "refuse".
    """
    components = {}

    # Base
    score = WAR_ENTRY_BASE
    components["base"] = WAR_ENTRY_BASE

    # Treaty depth
    treaty_state = world.get_diplomatic_state(promiser, beneficiary)
    treaty_bonus = WAR_ENTRY_TREATY_BONUS.get(treaty_state, 0)
    score += treaty_bonus
    components["treaty_depth"] = treaty_bonus

    # Defensive honor bonus
    defense_bonus = WAR_ENTRY_DEFENSIVE_HONOR_BONUS if is_defensive else 0
    score += defense_bonus
    components["defensive_honor"] = defense_bonus

    # Hostility toward named enemy
    enemy_relation = world.nation_relations.get(
        world._make_diplo_key(beneficiary, named_enemy), 0
    )
    hostility = max(-10, min(10, (-enemy_relation) // 5))
    score += hostility
    components["hostility_to_enemy"] = hostility

    # Opposition pair bonus
    opposition_pairs = get_bargain_opposition_pairs(world, promiser, beneficiary)
    opp_bonus = WAR_ENTRY_OPPOSITION_PAIR_BONUS if named_enemy in opposition_pairs else 0
    score += opp_bonus
    components["opposition_pair"] = opp_bonus

    # France-beneficiary relation
    france_relation = world.nation_relations.get(
        world._make_diplo_key(promiser, beneficiary), 0
    )
    relation_mod = max(-12, min(12, france_relation // 5))
    score += relation_mod
    components["france_relation"] = relation_mod

    # Bilateral betrayal strikes
    strike_count = _count_betrayal_strikes_against(world, beneficiary, promiser)
    betrayal_mod = max(WAR_ENTRY_BETRAYAL_CAP, strike_count * WAR_ENTRY_BETRAYAL_PENALTY_PER_STRIKE)
    score += betrayal_mod
    components["betrayal_strikes"] = betrayal_mod

    # Promiser global reliability
    reliability = int(getattr(world, "diplomatic_reliability", {}).get(promiser, 50))
    reliability_mod = max(-6, min(6, reliability // 10))
    score += reliability_mod
    components["reliability"] = reliability_mod

    # Matching live bargain
    has_bargain = False
    for b in _get_live_bargains(world):
        if (b.get("beneficiary") == beneficiary
                and b.get("target_enemy") == named_enemy
                and b.get("promiser") == promiser):
            has_bargain = True
            break
    bargain_bonus = WAR_ENTRY_BARGAIN_BONUS if has_bargain else 0
    score += bargain_bonus
    components["matching_bargain"] = bargain_bonus

    # Other-war load
    war_count = _count_active_wars(world, beneficiary)
    we = _get_war_exhaustion(world, beneficiary)
    if war_count >= 2 or we >= WAR_ENTRY_WAR_EXHAUSTION_THRESHOLD:
        war_load = WAR_ENTRY_WAR_LOAD_MULTI
    elif war_count == 1:
        war_load = WAR_ENTRY_WAR_LOAD_ONE
    else:
        war_load = 0
    score += war_load
    components["war_load"] = war_load

    # Determine band
    if score >= WAR_ENTRY_JOIN_THRESHOLD:
        band = "join"
    elif score >= WAR_ENTRY_COUNTER_BARGAIN_THRESHOLD:
        band = "counter_bargain"
    else:
        band = "refuse"

    return {"score": int(score), "band": band, "components": components}


def get_ally_entry_hard_blocks(
    world,
    promiser: str,
    beneficiary: str,
    named_enemy: str,
    *,
    is_offensive: bool = True,
) -> List[str]:
    """Return list of hard-block reasons preventing ally entry. Empty = no blocks."""
    blocks = []

    # Armistice/cooldown with named enemy
    diplo_key = world._make_diplo_key(beneficiary, named_enemy)
    arm_cd = getattr(world, "armistice_cooldowns", {}).get(diplo_key, 0)
    if arm_cd > 0:
        blocks.append(f"armistice_cooldown_with_{named_enemy}")

    # Already on enemy side of that war
    if world.is_at_war(beneficiary, promiser):
        blocks.append(f"at_war_with_{promiser}")

    # Direct enemy of promiser
    if beneficiary != promiser and world.get_diplomatic_state(beneficiary, promiser) == "WAR":
        blocks.append(f"direct_enemy_of_{promiser}")

    # Active anti-promiser coalition membership
    coalition = getattr(world, "active_coalition", None)
    if coalition and coalition.get("target_nation") == promiser:
        if beneficiary in coalition.get("members", []):
            blocks.append("anti_promiser_coalition_member")

    # hard_reject_posture (offensive only)
    if is_offensive:
        if _count_betrayal_strikes_against(world, beneficiary, promiser) >= 3:
            blocks.append("hard_reject_posture")

    # No plausible participation path
    if not _has_bargain_participation_access(world, promiser, beneficiary, named_enemy):
        blocks.append("no_participation_path")

    return blocks


def build_join_opportunity(
    world,
    beneficiary: str,
    named_enemy: str,
    request_type: str,
    *,
    promiser: str = "",
    origin_episode_id: str = "",
) -> Dict:
    """Create a join_opportunity record per §8.7."""
    promiser = promiser or getattr(world, "player_nation", "France")
    turn = int(world.current_turn)
    opp_id = int(getattr(world, "_next_join_opportunity_id", 1))
    world._next_join_opportunity_id = opp_id + 1

    is_defensive = request_type == "defensive_honor_call"
    hard_blocks = get_ally_entry_hard_blocks(
        world, promiser, beneficiary, named_enemy,
        is_offensive=(not is_defensive),
    )

    reroll_key = f"{beneficiary}|{named_enemy}|{request_type}|{turn}"

    entry_score = compute_war_entry_score(
        world, promiser, beneficiary, named_enemy,
        is_defensive=is_defensive,
    )

    return {
        "id": opp_id,
        "beneficiary": beneficiary,
        "named_enemy": named_enemy,
        "request_type": request_type,
        "surfaced_turn": turn,
        "hard_blocks": hard_blocks,
        "origin_episode_id": origin_episode_id,
        "reroll_key": reroll_key,
        "war_entry_score": entry_score,
        "promiser": promiser,
        "resolved": False,
        "resolution": None,
    }


def resolve_join_opportunity(
    world,
    opportunity: Dict,
    resolution: str,
) -> Dict:
    """Resolve a join opportunity. resolution: 'accept' / 'reject' / 'back_out'."""
    opportunity["resolved"] = True
    opportunity["resolution"] = resolution

    beneficiary = opportunity.get("beneficiary", "")
    named_enemy = opportunity.get("named_enemy", "")
    promiser = opportunity.get("promiser", "") or getattr(world, "player_nation", "France")
    request_type = opportunity.get("request_type", "")

    result = {
        "success": True,
        "beneficiary": beneficiary,
        "resolution": resolution,
        "joined": False,
    }

    if resolution == "accept":
        hard_blocks = opportunity.get("hard_blocks", [])
        if hard_blocks:
            result["success"] = False
            result["message"] = f"{beneficiary} cannot join: {hard_blocks[0]}"
            return result

        if not world.is_at_war(beneficiary, named_enemy):
            attach_result = ensure_war_instance_for_pair(
                world,
                beneficiary,
                named_enemy,
                entry_path="ally_entry",
                root_episode_id=opportunity.get("origin_episode_id", ""),
                reason="resolve_join_opportunity accept",
            )
            if not attach_result.get("ok"):
                result["success"] = False
                result["message"] = (
                    f"{beneficiary} cannot join: "
                    f"{attach_result.get('error')} "
                    f"({attach_result.get('details', {}).get('reason', '')})"
                )
                result["error"] = attach_result.get("error")
                return result
            set_diplomatic_state(world, beneficiary, named_enemy, "WAR", "ally_entry")
            world.modify_nation_relation(beneficiary, named_enemy, -20)
            result["war_id"] = attach_result.get("war_id")

        result["joined"] = True
        result["message"] = f"{beneficiary} enters the war against {named_enemy}."
        if world.is_at_war(promiser, named_enemy):
            _trigger_matching_war_entry_bargains(
                world,
                promiser,
                beneficiary,
                named_enemy,
                resolution_path="offensive_free_join",
                was_bargain_decisive=False,
            )

        _append_war_entry(
            getattr(world, "_current_war_entry_entries", None),
            nation=beneficiary,
            path="honored" if request_type != "defensive_honor_call" else "honored",
            side="attacker" if request_type == "offensive_ally_request" else "defender",
            reason=f"accepted {request_type}",
            treaty_state=world.get_diplomatic_state(promiser, beneficiary),
        )

    elif resolution == "reject":
        result["message"] = f"{beneficiary} refuses to join the war against {named_enemy}."
        if request_type == "offensive_ally_request":
            emit_call_to_arms_refused_offensive(
                world,
                breaker=beneficiary,
                victim=promiser,
                call_context={
                    "side": "attacker",
                    "caller": promiser,
                    "callee": beneficiary,
                    "enemy": named_enemy,
                },
            )

    elif resolution == "back_out":
        result["message"] = "Declaration cancelled."
        result["backed_out"] = True
        world.log_event({
            "type": "declaration_backed_out",
            "turn": int(world.current_turn),
            "promiser": promiser,
            "beneficiary": beneficiary,
            "named_enemy": named_enemy,
        })

    else:
        result["success"] = False
        result["message"] = f"Unknown ally-entry resolution: {resolution}."

    return result


def build_declaration_preview(
    world,
    aggressor: str,
    target: str,
    *,
    episode_id: str = "",
) -> Dict:
    """Build an enriched declaration preview with bargain + ally-entry info.

    Returns the standard preview_war_declaration data PLUS:
    - ally_entry_opportunities: list of join_opportunity dicts
    - bargain_warnings: list of active bargains affected
    """
    base_preview = preview_war_declaration(
        world, aggressor, target, episode_id=episode_id,
    )

    opportunities = []
    bargain_warnings = []

    # Offensive ally requests — nations with ALLIANCE with aggressor
    for nation in world.get_active_nations():
        if nation in (aggressor, target):
            continue
        state = world.get_diplomatic_state(nation, aggressor)
        if state == "ALLIANCE":
            if not world.is_at_war(nation, target):
                opp = build_join_opportunity(
                    world, nation, target, "offensive_ally_request",
                    promiser=aggressor, origin_episode_id=episode_id,
                )
                opportunities.append(opp)
        elif state == "DEFENSIVE_ALLIANCE":
            for b in _get_live_bargains(world):
                if (b.get("beneficiary") == nation
                        and b.get("target_enemy") == target
                        and b.get("promiser") == aggressor):
                    if not world.is_at_war(nation, target):
                        opp = build_join_opportunity(
                            world, nation, target, "offensive_ally_request",
                            promiser=aggressor, origin_episode_id=episode_id,
                        )
                        opportunities.append(opp)
                    break

    # Pre-war bargain warnings
    for b in _get_live_bargains(world):
        if b.get("promiser") == aggressor and b.get("target_enemy") == target:
            bargain_warnings.append({
                "bargain_id": b.get("id"),
                "beneficiary": b.get("beneficiary", ""),
                "claim_region": b.get("claim_term", {}).get("claim_region", ""),
                "warning": f"Active bargain with {b.get('beneficiary', '')} targets {target}",
            })

    base_preview["ally_entry_opportunities"] = opportunities
    base_preview["bargain_warnings"] = bargain_warnings
    return base_preview


def build_peace_bargain_warnings(
    world,
    nation_a: str,
    nation_b: str,
) -> List[Dict]:
    """Check if normalizing with nation_b would affect live bargains."""
    warnings = []
    for b in _get_live_bargains(world):
        if b.get("promiser") == nation_a and b.get("target_enemy") == nation_b:
            warnings.append({
                "bargain_id": b.get("id"),
                "beneficiary": b.get("beneficiary", ""),
                "claim_region": b.get("claim_term", {}).get("claim_region", ""),
                "warning": f"Peace with {nation_b} will breach bargain with {b.get('beneficiary', '')} "
                           f"(claim on {b.get('claim_term', {}).get('claim_region', '')})",
                "severity": "critical",
            })
    return warnings


def build_bargain_review(world, bargain_clause: Dict, proposal: Dict) -> Dict:
    """Build a Bargain Review payload for proposal_confirm per §10.1."""
    beneficiary = bargain_clause.get("beneficiary", "") or proposal.get("target_nation", "")
    named_enemy = bargain_clause.get("named_enemy", "")
    claim_region = bargain_clause.get("claim_region", "")
    promiser = proposal.get("proposer_nation", "") or getattr(world, "player_nation", "France")

    region_obj = world.regions.get(claim_region)
    current_holder = getattr(region_obj, "controller", "") if region_obj else ""

    source_treaty = world.get_diplomatic_state(promiser, beneficiary)

    entry_score = compute_war_entry_score(
        world, promiser, beneficiary, named_enemy,
    )
    band = entry_score.get("band", "refuse")
    band_display = {
        "join": "Join (will enter war without additional terms)",
        "counter_bargain": "Counter-bargain likely (may demand terms before joining)",
        "refuse": "Refuse (unlikely to join even with terms)",
    }.get(band, band)

    existing_bargains = [
        b for b in _get_live_bargains(world)
        if b.get("beneficiary") == beneficiary and b.get("promiser") == promiser
    ]
    is_decisive = band == "counter_bargain" and entry_score.get("score", 0) + WAR_ENTRY_BARGAIN_BONUS >= WAR_ENTRY_JOIN_THRESHOLD

    contradiction_warnings = []
    for existing in existing_bargains:
        if existing.get("target_enemy") != named_enemy:
            contradiction_warnings.append(
                f"Existing bargain targets {existing.get('target_enemy', '')}, new targets {named_enemy}"
            )

    strike_count = _count_betrayal_strikes_against(world, beneficiary, promiser)
    would_trigger_hard_reject = strike_count >= 2

    return {
        "beneficiary": beneficiary,
        "named_enemy": named_enemy,
        "claim_region": claim_region,
        "current_holder": current_holder,
        "source_treaty": source_treaty,
        "war_entry_forecast_band": band,
        "war_entry_forecast_display": band_display,
        "war_entry_score": entry_score.get("score", 0),
        "is_decisive": is_decisive,
        "would_trigger_hard_reject": would_trigger_hard_reject,
        "contradiction_warnings": contradiction_warnings,
    }


def generate_counter_bargain(
    world,
    promiser: str,
    beneficiary: str,
    named_enemy: str,
    *,
    reroll_key: str = "",
) -> Optional[Dict]:
    """Generate a counter-bargain demand from an ally in the 25-49 band.

    Returns None if no valid counter-bargain or ally outside range.
    Returns a counter_bargain_context dict otherwise.
    """
    # Check reroll memory
    reroll_memory = getattr(world, "_war_entry_reroll_memory", {})
    if reroll_key and reroll_key in reroll_memory:
        cached = reroll_memory[reroll_key]
        if cached.get("score_inputs_hash") == _hash_war_entry_inputs(world, promiser, beneficiary, named_enemy):
            return cached.get("counter_bargain")

    entry_score = compute_war_entry_score(
        world, promiser, beneficiary, named_enemy,
    )
    score = entry_score.get("score", 0)
    if score >= WAR_ENTRY_JOIN_THRESHOLD or score < WAR_ENTRY_COUNTER_BARGAIN_THRESHOLD:
        return None

    # Find a valid claim region for the counter-bargain
    enemy_regions = [
        r_name for r_name in world.regions
        if _region_is_held_by_enemy_or_subject(world, r_name, named_enemy)
    ]
    if not enemy_regions:
        return None

    # Pick region with strategic interest for beneficiary, or closest
    best_region = None
    for r_name in enemy_regions:
        if _has_bargain_strategic_interest(world, beneficiary, r_name):
            valid, _ = validate_war_bargain(
                world, promiser, beneficiary, named_enemy, r_name,
                source_state=world.get_diplomatic_state(promiser, beneficiary),
            )
            if valid:
                best_region = r_name
                break

    if not best_region:
        for r_name in enemy_regions:
            valid, _ = validate_war_bargain(
                world, promiser, beneficiary, named_enemy, r_name,
                source_state=world.get_diplomatic_state(promiser, beneficiary),
            )
            if valid:
                best_region = r_name
                break

    if not best_region:
        return None

    counter = {
        "type": "war_entry_counter_bargain",
        "beneficiary": beneficiary,
        "named_enemy": named_enemy,
        "demanded_region": best_region,
        "promiser": promiser,
        "war_entry_score": entry_score,
        "reroll_key": reroll_key,
    }

    # Cache for reroll determinism
    if reroll_key:
        if not hasattr(world, "_war_entry_reroll_memory"):
            world._war_entry_reroll_memory = {}
        world._war_entry_reroll_memory[reroll_key] = {
            "counter_bargain": counter,
            "score_inputs_hash": _hash_war_entry_inputs(world, promiser, beneficiary, named_enemy),
        }

    return counter


def _hash_war_entry_inputs(world, promiser: str, beneficiary: str, named_enemy: str) -> str:
    """Snapshot key inputs for reroll determinism comparison."""
    treaty_state = world.get_diplomatic_state(promiser, beneficiary)
    relation = world.nation_relations.get(world._make_diplo_key(promiser, beneficiary), 0)
    enemy_relation = world.nation_relations.get(world._make_diplo_key(beneficiary, named_enemy), 0)
    war_count = _count_active_wars(world, beneficiary)
    war_exhaustion = _get_war_exhaustion(world, beneficiary)
    strikes = _count_betrayal_strikes_against(world, beneficiary, promiser)
    reliability = int(getattr(world, "diplomatic_reliability", {}).get(promiser, 50))
    opposition = ",".join(sorted(get_bargain_opposition_pairs(world, promiser, beneficiary)))
    participation = int(_has_bargain_participation_access(world, promiser, beneficiary, named_enemy))
    enemy_regions = ",".join(sorted(
        r_name for r_name in world.regions
        if _region_is_held_by_enemy_or_subject(world, r_name, named_enemy)
    ))
    coalition = getattr(world, "active_coalition", None)
    coalition_key = ""
    if coalition:
        coalition_key = f"{coalition.get('target_nation', '')}|{','.join(sorted(coalition.get('members', [])))}"
    return (
        f"{treaty_state}|{relation}|{enemy_relation}|{war_count}|{war_exhaustion}|"
        f"{strikes}|{reliability}|{opposition}|{participation}|{enemy_regions}|{coalition_key}"
    )


def accept_counter_bargain(
    world,
    counter: Dict,
    *,
    join_war: bool = True,
) -> Dict:
    """Accept a counter-bargain — creates a triggered war_bargain and ally joins."""
    promiser = counter.get("promiser", "")
    beneficiary = counter.get("beneficiary", "")
    named_enemy = counter.get("named_enemy", "")
    claim_region = counter.get("demanded_region", "")
    source_treaty_key = world._make_diplo_key(promiser, beneficiary)

    joined = False
    war_id_attached: Optional[str] = None
    attach_result: Optional[Dict] = None
    if join_war and beneficiary and named_enemy and not world.is_at_war(beneficiary, named_enemy):
        attach_result = ensure_war_instance_for_pair(
            world,
            beneficiary,
            named_enemy,
            entry_path="counter_bargain_ally_entry",
            reason="accept_counter_bargain",
        )
        if not attach_result.get("ok"):
            return {
                "success": False,
                "bargain": None,
                "joined": False,
                "error": attach_result.get("error"),
                "message": (
                    f"Counter-bargain blocked: {attach_result.get('error')} "
                    f"({attach_result.get('details', {}).get('reason', '')})"
                ),
            }

    bargain = create_war_bargain_commitment(
        world, promiser, beneficiary, named_enemy, claim_region,
        "counter_bargain", source_treaty_key,
    )
    bargain["status"] = "triggered"
    bargain["triggered_turn"] = int(world.current_turn)
    bargain["trigger_context"] = {
        "resolution_path": "offensive_counter_bargain_accept",
        "was_bargain_decisive": True,
        "counter_bargain_context": copy.deepcopy(counter),
    }
    _emit_bargain_event(world, bargain, "bargain_triggered")

    if attach_result:
        set_diplomatic_state(world, beneficiary, named_enemy, "WAR", "counter_bargain_ally_entry")
        world.modify_nation_relation(beneficiary, named_enemy, -20)
        joined = True
        war_id_attached = attach_result.get("war_id")

    return {
        "success": True,
        "bargain": bargain,
        "joined": joined,
        "war_id": war_id_attached,
        "message": f"{beneficiary} demands recognition of their claim to {claim_region}. Bargain accepted — {beneficiary} joins the war.",
    }


def repudiate_bargain(world, bargain_id: str, *, episode_id: str = None) -> Dict:
    """Explicitly repudiate a live bargain per §8.9.C.

    Routes into WB-B breach_bargain with French-fault penalties.
    """
    commitments = getattr(world, "diplomatic_commitments", {})
    bargain = commitments.get(str(bargain_id))
    if not bargain:
        return {"success": False, "message": "No such bargain exists."}
    if not _is_bargain_live(bargain):
        return {"success": False, "message": "That bargain is no longer active."}

    episode_id = episode_id or _allocate_episode_id(world, prefix="bargain")
    ev = breach_bargain(world, bargain, "explicit_repudiation", episode_id=episode_id)

    return {
        "success": True,
        "message": f"The bargain with {bargain.get('beneficiary', '')} regarding {bargain.get('claim_term', {}).get('claim_region', '')} has been repudiated.",
        "breach_event": ev,
    }


def get_live_bargains_for_ledger(world) -> List[Dict]:
    """Return formatted live bargains for the diplomatic ledger."""
    result = []
    for b in _get_live_bargains(world):
        cooldown_remaining = max(0, int(b.get("cooldown_until_turn", 0)) - int(world.current_turn))
        result.append({
            "bargain_id": b.get("id"),
            "promiser": b.get("promiser", ""),
            "beneficiary": b.get("beneficiary", ""),
            "named_enemy": b.get("target_enemy", ""),
            "claim_region": b.get("claim_term", {}).get("claim_region", ""),
            "status": b.get("status", ""),
            "source_treaty": b.get("source_treaty", ""),
            "created_turn": int(b.get("created_turn", 0) or 0),
            "cooldown_remaining": cooldown_remaining,
        })
    return result


_BARGAIN_BADGE_MAP = {
    "fulfilled": "honoured",
    "breached": "broken",
    "void": "lapsed",
}


def get_all_bargains_for_ledger(world) -> List[Dict]:
    """Return all bargains (live + completed) for the diplomatic ledger.

    WB-D: completed bargains include a badge field for emphasis.
    """
    result = get_live_bargains_for_ledger(world)
    commitments = getattr(world, "diplomatic_commitments", {})
    for b in commitments.values():
        status = b.get("status", "")
        if status in ("active", "triggered"):
            continue
        badge = _BARGAIN_BADGE_MAP.get(status, "")
        cooldown_remaining = max(0, int(b.get("cooldown_until_turn", 0)) - int(world.current_turn))
        result.append({
            "bargain_id": b.get("id"),
            "promiser": b.get("promiser", ""),
            "beneficiary": b.get("beneficiary", ""),
            "named_enemy": b.get("target_enemy", ""),
            "claim_region": b.get("claim_term", {}).get("claim_region", ""),
            "status": status,
            "source_treaty": b.get("source_treaty", ""),
            "created_turn": int(b.get("created_turn", 0) or 0),
            "ended_turn": int(b.get("ended_turn", 0) or 0),
            "badge": badge,
            "end_reason": b.get("end_reason", ""),
            "cooldown_remaining": cooldown_remaining,
        })
    return result


# ═══════════════════════════════════════════════════════
# AI WAR BARGAIN RULES — WB-C (§11)
# ═══════════════════════════════════════════════════════

def _trigger_matching_war_entry_bargains(
    world,
    promiser: str,
    beneficiary: str,
    named_enemy: str,
    *,
    resolution_path: str,
    was_bargain_decisive: bool = False,
) -> List[Dict]:
    """Mark live bargains triggered once the ally actually enters the named war."""
    events = []
    for bargain in _get_live_bargains(world):
        if bargain.get("status") != "active":
            continue
        if not (
            bargain.get("promiser") == promiser
            and bargain.get("beneficiary") == beneficiary
            and bargain.get("target_enemy") == named_enemy
        ):
            continue
        bargain["status"] = "triggered"
        bargain["triggered_turn"] = int(world.current_turn)
        bargain["trigger_context"] = {
            "resolution_path": resolution_path,
            "was_bargain_decisive": bool(was_bargain_decisive),
        }
        events.append(_emit_bargain_event(world, bargain, "bargain_triggered"))
    return events


BARGAIN_AI_COOLDOWN_TURNS = 5
BARGAIN_AI_DECISION_REASONS = {
    "claim_trade", "counterparty_reversal", "claim_obsolete",
    "strategic_interest", "no_valid_region", "participation_blocked",
    "anti_spam", "cooldown_active", "no_feasible_target",
    "strength_insufficient", "contradiction", "hard_blocked",
}


def ai_should_propose_bargain(
    world,
    proposer: str,
    target_nation: str,
    named_enemy: str,
) -> Dict:
    """Check if AI should propose a war bargain per §11.1 feasibility gates.

    Returns {"feasible": bool, "decision_reason": str, "claim_region": str|None}
    """
    # Anti-spam: no bargain if already live with this nation
    for b in _get_live_bargains(world):
        if b.get("promiser") == proposer and b.get("beneficiary") == target_nation:
            return {"feasible": False, "decision_reason": "anti_spam", "claim_region": None}

    # Cooldown check
    cooldown_key = f"{proposer}|{target_nation}::{named_enemy}"
    for b in getattr(world, "diplomatic_commitments", {}).values():
        if b.get("cooldown_key") == cooldown_key:
            if int(b.get("cooldown_until_turn", 0)) > int(world.current_turn):
                return {"feasible": False, "decision_reason": "cooldown_active", "claim_region": None}

    # Named enemy must be opposition
    opposition = get_bargain_opposition_pairs(world, proposer, target_nation)
    if named_enemy not in opposition:
        return {"feasible": False, "decision_reason": "no_feasible_target", "claim_region": None}

    # WB-C hard blocks: armistice, enemy-side war state, anti-coalition,
    # hard-reject, and participation access all gate bargain feasibility.
    hard_blocks = get_ally_entry_hard_blocks(
        world,
        proposer,
        target_nation,
        named_enemy,
        is_offensive=True,
    )
    if hard_blocks:
        if "hard_reject_posture" in hard_blocks:
            return {"feasible": False, "decision_reason": "counterparty_reversal", "claim_region": None}
        if "no_participation_path" in hard_blocks:
            return {"feasible": False, "decision_reason": "participation_blocked", "claim_region": None}
        return {"feasible": False, "decision_reason": "hard_blocked", "claim_region": None}

    # Target must have at least one marshal and sufficient strength
    target_marshals = [
        m for m in getattr(world, "marshals", {}).values()
        if getattr(m, "nation", "") == target_nation and getattr(m, "alive", True)
    ]
    if not target_marshals:
        return {"feasible": False, "decision_reason": "strength_insufficient", "claim_region": None}

    target_strength = sum(getattr(m, "troops", 0) for m in target_marshals)
    proposer_marshals = [
        m for m in getattr(world, "marshals", {}).values()
        if getattr(m, "nation", "") == proposer and getattr(m, "alive", True)
    ]
    proposer_strength = sum(getattr(m, "troops", 0) for m in proposer_marshals)
    if proposer_strength > 0 and target_strength < proposer_strength * 0.25:
        if not _has_bargain_participation_access(world, proposer, target_nation, named_enemy):
            return {"feasible": False, "decision_reason": "strength_insufficient", "claim_region": None}

    # Betrayal memory refusal
    if _count_betrayal_strikes_against(world, target_nation, proposer) >= 3:
        return {"feasible": False, "decision_reason": "counterparty_reversal", "claim_region": None}

    # Find valid claim region
    enemy_regions = [
        r_name for r_name in world.regions
        if _region_is_held_by_enemy_or_subject(world, r_name, named_enemy)
    ]
    best_region = None
    for r_name in enemy_regions:
        valid, _ = validate_war_bargain(
            world, proposer, target_nation, named_enemy, r_name,
            source_state=world.get_diplomatic_state(proposer, target_nation),
        )
        if valid:
            if _has_bargain_strategic_interest(world, proposer, r_name):
                best_region = r_name
                break
            if not best_region:
                best_region = r_name

    if not best_region:
        return {"feasible": False, "decision_reason": "no_valid_region", "claim_region": None}

    return {
        "feasible": True,
        "decision_reason": "claim_trade",
        "claim_region": best_region,
    }


def ai_evaluate_war_entry(
    world,
    promiser: str,
    beneficiary: str,
    named_enemy: str,
) -> Dict:
    """AI evaluates whether to join a war per §11.4.

    Returns {"join": bool, "counter_bargain": bool, "decision_reason": str, "score": dict}
    """
    hard_blocks = get_ally_entry_hard_blocks(
        world, promiser, beneficiary, named_enemy,
        is_offensive=True,
    )
    if hard_blocks:
        return {
            "join": False,
            "counter_bargain": False,
            "decision_reason": "hard_blocked",
            "hard_blocks": hard_blocks,
            "score": {},
        }

    entry_score = compute_war_entry_score(
        world, promiser, beneficiary, named_enemy,
    )
    band = entry_score.get("band", "refuse")

    if band == "join":
        return {
            "join": True,
            "counter_bargain": False,
            "decision_reason": "claim_trade" if entry_score["components"].get("matching_bargain", 0) > 0 else "strategic_interest",
            "score": entry_score,
        }
    elif band == "counter_bargain":
        return {
            "join": False,
            "counter_bargain": True,
            "decision_reason": "claim_trade",
            "score": entry_score,
        }
    else:
        # Check if refusal should void a bargain
        for b in _get_live_bargains(world):
            if (b.get("beneficiary") == beneficiary
                    and b.get("target_enemy") == named_enemy
                    and b.get("promiser") == promiser):
                _void_bargain(world, b, {
                    "reason": "ai_refusal",
                    "family": "counterparty_reversal",
                    "fault_nation": beneficiary,
                    "decision_reason": "counterparty_reversal",
                })
                _emit_bargain_event(world, b, "bargain_voided")
        return {
            "join": False,
            "counter_bargain": False,
            "decision_reason": "counterparty_reversal" if entry_score["components"].get("betrayal_strikes", 0) < -16 else "claim_obsolete",
            "score": entry_score,
        }


# ═══════════════════════════════════════════════════════
# ACCEPTANCE FORMULA (§6)
# ═══════════════════════════════════════════════════════

def calculate_acceptance(proposal: Dict, world) -> Dict:
    """Calculate acceptance score for a diplomatic proposal.

    Args:
        proposal: {
            "type": str (peace/alliance/vassalage/armistice_losing/armistice_winning/
                         open_borders/non_aggression),
            "proposer_nation": str,
            "target_nation": str,
            "sweeteners": list of {"type": str, "value": int/float},
            "demands": list of {"type": str, "value": int/float},
            "clauses": list of str (special clause keys),
        }
        world: WorldState

    Returns:
        {"score": int, "outcome": str, "components": dict, "feedback": str}
    """
    proposal_type = proposal.get("type", "peace")
    proposer = proposal.get("proposer_nation", "France")
    target = proposal.get("target_nation", "")

    # G4F-14: resolve generic "armistice" to its war-score variant AT THE
    # SCORING SEAM. BASE_DISPOSITION only carries armistice_losing (40) /
    # armistice_winning (20); a generic string silently fell to the default
    # 30, so a preview scored on terms["type"] (variant, from
    # _build_base_terms) and a send scored on terms["proposal_type"]
    # (generic) disagreed by ±10 base points — enough to cross both verdict
    # thresholds. Same losing-rule as _build_base_terms: proposer losing →
    # armistice_losing.
    if proposal_type == "armistice" and target:
        _ws_for_variant = get_war_score_for(world, proposer, target)
        proposal_type = (
            "armistice_losing" if _ws_for_variant < 0 else "armistice_winning"
        )

    # Get diplomats
    diplomats = getattr(world, 'diplomats', {})
    proposer_diplomat = diplomats.get(proposer)
    target_diplomat = diplomats.get(target)

    proposer_skill = proposer_diplomat.skill if proposer_diplomat else 5
    target_skill = target_diplomat.skill if target_diplomat else 5
    target_personality = target_diplomat.personality if target_diplomat else "loyalist"

    # ── Base Disposition ──
    base = BASE_DISPOSITION.get(proposal_type, 30)

    # WPS-C §9.3: Forced alliance clause overrides base disposition to -15.
    _has_forced_alliance_clause = any(
        (isinstance(d, dict) and d.get("type") == "forced_alliance")
        for d in proposal.get("demands", [])
    )
    if _has_forced_alliance_clause:
        base = -15

    # ── War Score Modifier ──
    diplo_key = world._make_diplo_key(proposer, target)
    war_score = getattr(world, 'war_scores', {}).get(diplo_key, 0)
    # Positive war_score means first-alphabetically nation is winning
    # Adjust sign so positive = proposer winning
    parts = diplo_key.split("|")
    if len(parts) == 2 and parts[0] == target:
        war_score = -war_score  # Flip: target is first in key, so proposer winning = negative in storage
    war_score_mod = war_score * 0.3

    # ── Relation Modifier (R141: dampened during WAR) ──
    relation = world.nation_relations.get(diplo_key, 0)
    current_diplo_state = world.diplomatic_states.get(diplo_key, "PEACE")
    if current_diplo_state == "WAR":
        relation_mod = max(-10, min(10, relation / 4))  # -40 rel → -10 (was -20)
    else:
        relation_mod = max(-30, min(30, relation / 2))   # unchanged for peacetime

    # ── War Weariness (R142: +2/turn at war, cap +20) ──
    war_weariness_mod = 0
    if current_diplo_state == "WAR":
        war_start = getattr(world, 'war_start_turns', {}).get(diplo_key, world.current_turn)
        turns_at_war = max(0, int(world.current_turn) - int(war_start))
        war_weariness_mod = min(20, turns_at_war * 2)

    # ── Stalemate Duration (R143: +1/stalemate turn, cap +15) ──
    stalemate_duration_mod = 0
    if current_diplo_state == "WAR":
        stalemate_counters = getattr(world, 'ai_stalemate_counters', {})
        target_stalemate = stalemate_counters.get(target, 0)
        stalemate_duration_mod = min(15, target_stalemate)

    # ── Hegemony Target Modifier (v2.4.3 §9.1) ──
    # Per-pair cross-bloc friction starting at 30% share, independent of
    # the 33%+ passive threat accrual owned by _calculate_hegemony_pressure.
    hegemony_target = hegemony_target_mod(proposer, target, world)

    # ── Bilateral Betrayal Modifier (v2.4.3 §9.2) ──
    bilateral_betrayal = bilateral_betrayal_mod(proposer, target, world)

    # ── Grievance Modifier (B-B4 §8.8.9 + §9.3) ──
    # -30 per active durable grievance flag held by the target against
    # the asker, saturating at 3 flags per pair (max -90). The raw
    # uncapped count surfaces as `grievance_flag_count_raw` on
    # `components` so the ledger can distinguish "3 grievances" from
    # "4+ grievances" distinctly without re-deriving it.
    grievance = grievance_modifier(proposer, target, world)
    grievance_flag_count_raw = int(
        _get_active_grievance_flag_count(world, proposer, target)
    )

    # ── War Bargain Modifiers (WB-A §9.1 / §9.2) ──
    bargain_value_mod = 0
    bargain_conflict_penalty = 0
    for clause in proposal.get("sweeteners", []) + proposal.get("demands", []):
        if clause.get("type") == "war_bargain":
            if proposal_type == "defensive_alliance":
                bargain_value_mod = 10
            elif proposal_type == "alliance":
                bargain_value_mod = 15
            break
    live_bargains = _get_live_bargains(world)
    for b in live_bargains:
        if b.get("promiser") == proposer and b.get("target_enemy") == target:
            bargain_conflict_penalty = -8
            break
    if bargain_conflict_penalty == 0:
        for b in live_bargains:
            cr = b.get("claim_term", {}).get("claim_region", "")
            if cr and b.get("promiser") == proposer:
                region_obj = world.regions.get(cr)
                if region_obj and getattr(region_obj, "controller", "") == target:
                    bargain_conflict_penalty = -8
                    break

    # ── Deal Balance ──
    from backend.models.region import NATION_CAPITALS
    _all_capitals = set(NATION_CAPITALS.values())

    sweetener_total = 0.0
    for s in proposal.get("sweeteners", []):
        stype = s.get("type", "")
        svalue = s.get("value", 0)
        rate = SWEETENER_VALUES.get(stype, 0)
        if stype in ("territory_cede", "territory"):
            # Capital regions worth double (+16 vs +8)
            regions = s.get("regions", [])
            if not regions and svalue is None:
                # value=None with no regions — flat rate fallback (1 region implied)
                sweetener_total += rate
            else:
                capital_count = sum(1 for r in regions if r in _all_capitals)
                normal_count = max(0, (svalue or 0) - capital_count)
                sweetener_total += rate * normal_count + rate * 2 * capital_count
        elif isinstance(rate, (int, float)) and rate < 1:
            sweetener_total += (svalue * rate) if svalue is not None else 0
        else:
            sweetener_total += rate * svalue if svalue is not None else rate
    sweetener_total = min(SWEETENER_CAP, sweetener_total)

    # PL-20 §A: Escalating territory cost (replaces flat -5/region)
    import math
    territory_analysis = analyze_territory_demands(
        proposal.get("demands", []), target, world
    )
    territory_penalty = 0.0
    # Sum escalating costs from analyzed regions
    for _r, cost in territory_analysis["escalating_costs"]:
        territory_penalty += cost
    # Backward compat fallback for value-only demands (no regions list)
    for fallback_cost in territory_analysis["fallback_escalating_costs"]:
        territory_penalty += fallback_cost
    # Elimination guards (stack with escalating cost)
    if territory_analysis["is_annex"]:
        territory_penalty -= 60
    elif territory_analysis["is_rump"]:
        territory_penalty -= 30
    territory_penalty = math.floor(territory_penalty)

    demand_total = 0.0
    for d in proposal.get("demands", []):
        dtype = d.get("type", "")
        dvalue = d.get("value", 0)
        rate = DEMAND_VALUES.get(dtype, 0)
        if dtype in ("territory_cede", "territory"):
            continue  # Handled by territory_penalty above
        elif isinstance(rate, (int, float)) and abs(rate) < 1:
            demand_total += (dvalue * rate) if dvalue is not None else 0
        else:
            demand_total += rate * dvalue if dvalue is not None else rate
    demand_total += territory_penalty

    deal_balance = sweetener_total + demand_total

    # ── Diplomat Skill Bonus ──
    diplomat_skill_bonus = max(-8, min(12, (proposer_skill - target_skill) * 2))

    # ── Personality Modifier ──
    peace_mod, harsh_mod = PERSONALITY_MODIFIERS.get(target_personality, (0, 0))
    is_harsh = proposal_type in ("vassalage",)
    # Also check if demands outweigh sweeteners significantly
    if demand_total < -3:  # PL-12-C: was -10 (100g demand = -5 now triggers)
        is_harsh = True
    personality_mod = harsh_mod if is_harsh else peace_mod

    # ── Military Supremacy (§6b.1) ──
    military_supremacy = 0
    from backend.models.region import NATION_CAPITALS
    target_capital = NATION_CAPITALS.get(target)
    if war_score >= 70 and target_capital:
        cap_region = world.regions.get(target_capital)
        if cap_region and cap_region.controller == proposer:
            military_supremacy = 25

    # ── Battlefield Diplomacy (COALITION_SPEC R3) ──
    battlefield_diplomacy = 0
    if (war_score > 20
            and proposal_type in ("peace", "armistice_losing", "armistice_winning")
            and military_supremacy == 0):  # Does NOT stack with Military Supremacy
        battlefield_diplomacy = 10

    # R8: Military pressure from war score
    military_pressure = 0
    if war_score > 0:
        military_pressure = int(min(15, war_score * 0.15))

    # Use whichever is higher (they don't stack)
    situational_bonus = max(military_supremacy, battlefield_diplomacy, military_pressure)

    # ── Special Desire Bonus (§6d) ──
    # Nation-specific acceptance bonuses when proposal addresses core interests
    special_desire_bonus = 0
    clauses = proposal.get("clauses", [])
    target_specials = SPECIAL_BONUSES.get(target, {})
    # Check both string clauses and dict clauses
    for clause in clauses:
        if isinstance(clause, str):
            if clause in target_specials:
                special_desire_bonus += target_specials[clause]
        elif isinstance(clause, dict):
            # Handle structured clause dicts: {"type": "territory", "region": "Saxony"}
            ctype = clause.get("type", "")
            cregion = clause.get("region", "")
            # Match territory_X patterns
            clause_key = f"{ctype}_{cregion.lower()}" if cregion else ctype
            if clause_key in target_specials:
                special_desire_bonus += target_specials[clause_key]
            elif ctype in target_specials:
                special_desire_bonus += target_specials[ctype]

    # ── Current Proposal Harshness Penalty (PL-12-A) ──
    from backend.game_logic.diplomatic_templates import calculate_treaty_harshness
    harshness_terms = {
        "clauses": [c if isinstance(c, dict) else {"type": c} for c in proposal.get("clauses", [])],
        "demands": proposal.get("demands", []),
    }
    current_harshness = calculate_treaty_harshness(harshness_terms)
    harshness_penalty = -min(40, max(0, int((current_harshness - 0.2) * 150)))

    # ── Escalating Harshness (DD8-4) ──
    harshness_bonus = 0
    prev_treaties = getattr(world, 'previous_treaties', {}).get(diplo_key, [])
    for treaty in prev_treaties:
        if treaty.get("harshness", 0) > 0.3:
            harshness_bonus = -5  # PL-12-D: was +5 (harsh history breeds resentment)
            break

    # ── Diplomatic Reliability (v2.4.3 §9.2 — narrowed from R34) ──
    # Narrowed to // 10 capped +/-6 so bilateral betrayal memory dominates
    # cross-pair reliability averages per spec §9.2.
    reliability = getattr(world, 'diplomatic_reliability', {})
    proposer_reliability = reliability.get(proposer, 0)
    reliability_modifier = max(-6, min(6, proposer_reliability // 10))

    # ── Ultimatum Military Threat Bonus (PL-14 §5) ──
    ultimatum_bonus = 0
    if proposal_type == "ultimatum_demand":
        ultimatum_bonus = 10  # base military threat
        # +15 if any proposer marshal adjacent to target marshal
        adjacency_bonus = 0
        territory_bonus = 0
        marshals = getattr(world, 'marshals', {})
        regions = getattr(world, 'regions', {})
        for m_name, m_obj in marshals.items():
            if m_obj.nation == proposer and m_obj.strength > 0:
                m_region = regions.get(m_obj.location)
                if not m_region:
                    continue
                # +5 per proposer marshal in target territory (cap +15)
                if m_region.controller == target:
                    territory_bonus = min(15, territory_bonus + 5)
                # +15 if adjacent to any target marshal
                if adjacency_bonus == 0:
                    for e_name, e_obj in marshals.items():
                        if e_obj.nation == target and e_obj.location in getattr(m_region, 'adjacent_regions', []):
                            adjacency_bonus = 15
                            break
        ultimatum_bonus += adjacency_bonus + territory_bonus

    # ── Composite floor (B-B4 §9.3 with-DG-4 clause) ──
    # With `grievance_modifier` live in the formula, the three political-
    # pressure terms combined can reach -128 raw (-20 hegemony + -18
    # betrayal + -90 grievance). §9.3 clamps that political subtotal at
    # -60 so the §8.7 survival-exception path stays playable. The floor
    # is a synthetic debug row; raw term values are preserved in
    # `components` for legibility.
    political_subtotal_raw = (
        int(hegemony_target) + int(bilateral_betrayal) + int(grievance)
        + int(bargain_value_mod) + int(bargain_conflict_penalty)
    )
    political_subtotal_clamped = max(-60, political_subtotal_raw)
    composite_floor_applied = political_subtotal_clamped > political_subtotal_raw
    composite_floor_adjustment = political_subtotal_clamped - political_subtotal_raw
    composite_floor_value = -60 if composite_floor_applied else 0

    # ── Settlement gratitude (WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC §14.3) ──
    # +5 acceptance bonus when the proposer has rewarded the target via
    # settlement (`settlement_gratitude` memory active) and the proposal
    # is in the deep-treaty / war-entry / war-bargain / ally-entry
    # families. Per spec line 1482 this rides OUTSIDE
    # `political_subtotal_clamped` and BEFORE `deal_balance`, and never
    # bypasses hard posture gates (those clamp `score` after this sum).
    try:
        from backend.game_logic.settlement_reactions import (
            settlement_gratitude_mod as _settlement_gratitude_mod,
        )
        settlement_gratitude_value = int(
            _settlement_gratitude_mod(world, proposer, target, proposal_type)
        )
    except Exception:
        settlement_gratitude_value = 0

    # ── Sum ──
    raw_score = (
        base
        + war_score_mod
        + relation_mod
        + war_weariness_mod
        + stalemate_duration_mod
        + political_subtotal_clamped
        + settlement_gratitude_value
        + deal_balance
        + diplomat_skill_bonus
        + personality_mod
        + situational_bonus
        + special_desire_bonus
        + harshness_penalty
        + harshness_bonus
        + reliability_modifier
        + ultimatum_bonus
    )

    score = int(round(raw_score))
    hard_reject_posture = 0
    if proposal_type in _DEEP_TREATY_TYPES and has_hard_reject_posture(world, proposer, target):
        if _shared_enemy_exists(world, proposer, target) and not world.is_at_war(proposer, target):
            hard_reject_posture = -20
            score += hard_reject_posture
        else:
            hard_reject_posture = -100
            score = min(score, 0)

    # ── Anti-renewal cooldown gate (B-B4 §8.8.7) ──
    # A recent `call_to_arms_refused_defensive` episode blocks new
    # ALLIANCE / DEFENSIVE_ALLIANCE ratification between the refuser
    # and the abandoned victim for `ANTI_RENEWAL_COOLDOWN_TURNS` turns.
    # Mirrors the `hard_reject_posture` score-clamp pattern so the gate
    # fires uniformly on player, AI-player, and AI-AI proposal paths
    # that all route through `calculate_acceptance`. No survival-
    # exception branch per §8.8.7 "Blocking is mechanical, not advisory".
    oathbreaker_posture = 0
    oathbreaker_turns_remaining = 0
    oathbreaker_active = False
    if proposal_type in _DEEP_TREATY_TYPES and is_oathbreaker_auto_reject_active(
        world, target,
    ):
        oathbreaker_active = True
        oathbreaker_turns_remaining = get_oathbreaker_turns_remaining(world, target)
        oathbreaker_posture = -100
        score = min(score, 0)

    anti_renewal_block = 0
    anti_renewal_turns_remaining = 0
    anti_renewal_active = False
    if proposal_type in _DEEP_TREATY_TYPES and is_anti_renewal_active(
        world, proposer, target,
    ):
        anti_renewal_active = True
        anti_renewal_turns_remaining = get_anti_renewal_turns_remaining(
            world, proposer, target,
        )
        anti_renewal_block = -100
        score = min(score, 0)

    if score >= 50:
        outcome = "ACCEPT"
    elif score >= 30:
        outcome = "COUNTER_OFFER"
    else:
        outcome = "REJECT"

    # Build components dict for debugging/display.
    # Raw term values are preserved so the ledger can render
    # "hegemony -20, betrayal -18, grievance -90, composite floor applied
    # at -60" per spec §9.3 "Floor exposure" clause.
    components = {
        "base_disposition": base,
        "war_score_modifier": round(war_score_mod, 1),
        "relation_modifier": round(relation_mod, 1),
        "war_weariness": int(war_weariness_mod),
        "stalemate_duration": int(stalemate_duration_mod),
        "hegemony_target_mod": int(hegemony_target),
        "bilateral_betrayal_mod": int(bilateral_betrayal),
        "grievance_modifier": int(grievance),
        "bargain_value_mod": int(bargain_value_mod),
        "bargain_conflict_penalty": int(bargain_conflict_penalty),
        "grievance_flag_count_raw": grievance_flag_count_raw,
        "composite_floor": int(composite_floor_value),
        "composite_floor_applied": bool(composite_floor_applied),
        "composite_floor_adjustment": int(composite_floor_adjustment),
        "settlement_gratitude_mod": int(settlement_gratitude_value),
        "deal_balance": round(deal_balance, 1),
        "diplomat_skill_bonus": diplomat_skill_bonus,
        "personality_modifier": personality_mod,
        "military_supremacy": military_supremacy,
        "battlefield_diplomacy": battlefield_diplomacy,
        "military_pressure": military_pressure,
        "special_desire_bonus": special_desire_bonus,
        "harshness_penalty": harshness_penalty,
        "harshness_bonus": harshness_bonus,
        "reliability_modifier": reliability_modifier,
        "ultimatum_bonus": ultimatum_bonus,
        "territory_escalation": int(territory_penalty),
        "hard_reject_posture": int(hard_reject_posture),
        # B-B4 §8.8.7 — anti-renewal cooldown gate. `anti_renewal_block`
        # mirrors the `hard_reject_posture` convention (negative score
        # clamp; neither is in `_generate_feedback` trackable). The
        # `_active` / `_turns_remaining` keys surface the state for
        # ledger / UI without re-reading the cooldown map.
        "oathbreaker_posture": int(oathbreaker_posture),
        "oathbreaker_active": bool(oathbreaker_active),
        "oathbreaker_turns_remaining": int(oathbreaker_turns_remaining),
        "anti_renewal_block": int(anti_renewal_block),
        "anti_renewal_active": bool(anti_renewal_active),
        "anti_renewal_turns_remaining": int(anti_renewal_turns_remaining),
    }

    # ── Feedback (§6f) ──
    feedback = _generate_feedback(outcome, components)

    return {
        "score": int(score),
        "outcome": outcome,
        "components": components,
        "feedback": feedback,
    }


def _generate_feedback(outcome: str, components: Dict) -> str:
    """Generate natural-language feedback based on formula components."""
    # Find largest positive and negative components
    trackable = {
        "base_disposition", "war_score_modifier", "relation_modifier",
        "war_weariness", "stalemate_duration",
        "deal_balance", "diplomat_skill_bonus",
        "personality_modifier", "special_desire_bonus",
        "hegemony_target_mod", "bilateral_betrayal_mod",
        "grievance_modifier",
        "settlement_gratitude_mod",
        "bargain_value_mod", "bargain_conflict_penalty",
        "harshness_penalty", "harshness_bonus", "reliability_modifier",
        "military_supremacy", "battlefield_diplomacy", "military_pressure",
        "ultimatum_bonus",
    }

    largest_positive = ("", 0)
    largest_negative = ("", 0)
    second_negative = ("", 0)

    for key in trackable:
        val = components.get(key, 0)
        if val > largest_positive[1]:
            largest_positive = (key, val)
        if val < largest_negative[1]:
            second_negative = largest_negative
            largest_negative = (key, val)
        elif val < second_negative[1]:
            second_negative = (key, val)

    proposer_name = "Talleyrand"  # Default for player feedback

    if outcome == "REJECT":
        key = largest_negative[0]
        phrase = FEEDBACK_STRINGS.get(key, {}).get("negative", "unknown factors")
        return f"{proposer_name} reports the key obstacle was {phrase}."
    elif outcome == "COUNTER_OFFER":
        key = second_negative[0] if second_negative[0] else largest_negative[0]
        phrase = FEEDBACK_STRINGS.get(key, {}).get("negative", "unresolved concerns")
        return f"The sticking point appears to be {phrase}."
    else:  # ACCEPT
        key = largest_positive[0]
        phrase = FEEDBACK_STRINGS.get(key, {}).get("positive", "favorable conditions")
        return f"The decisive factor was {phrase}."


def build_proposal_commitment_warnings(
    world,
    proposer_nation: str,
    target_nation: str,
    proposal_type: str,
) -> List[Dict]:
    """Build structured commitments warnings for proposal preview surfaces.

    Warning categories in scope here (sorted via WARNING_CATEGORY_ORDER):
    - `hard_reject`: deep-treaty proposal into a 3-strike victim (critical)
    - `betrayal`: 1-2 active bilateral strikes against the target (v2.4.3 §9.2)
    - `hegemony`: per-pair cross-bloc friction from the hegemon bloc pressing
      outward (v2.4.3 §9.1; gates identical to `hegemony_target_mod`)
    """
    warnings: List[Dict] = []
    if proposal_type in _DEEP_TREATY_TYPES and is_anti_renewal_active(
        world, proposer_nation, target_nation,
    ):
        turns = get_anti_renewal_turns_remaining(
            world, proposer_nation, target_nation,
        )
        warnings.append({
            "severity": "critical",
            "category": "hard_reject",
            "text": (
                f"Anti-renewal cooldown blocks a {_proposal_display_name(proposal_type)} "
                f"for {turns} more turn{'' if turns == 1 else 's'}."
            ),
        })
    if proposal_type in _DEEP_TREATY_TYPES and is_oathbreaker_auto_reject_active(
        world, target_nation,
    ):
        turns = get_oathbreaker_turns_remaining(world, target_nation)
        warnings.append({
            "severity": "critical",
            "category": "hard_reject",
            "text": (
                f"{target_nation}'s oathbreaker posture blocks new deep treaties "
                f"for {turns} more turn{'' if turns == 1 else 's'}."
            ),
        })
    betrayal_strikes = _get_active_betrayal_strike_count(world, proposer_nation, target_nation)
    if betrayal_strikes >= 3 and proposal_type in _DEEP_TREATY_TYPES:
        warnings.append({
            "severity": "critical",
            "category": "hard_reject",
            "text": (
                f"{target_nation} is in hard-reject posture after repeated betrayals and will resist "
                f"a {_proposal_display_name(proposal_type)}."
            ),
        })
    elif betrayal_strikes > 0:
        # TODO(post-B-B1-lite): cite one remembered referent from
        # commitment_event_metadata when episode-metadata plumbing lands.
        # Strike records currently carry only severity/turn/episode_id —
        # no named-nation / broken-treaty / witness-context surface yet.
        severity = "high" if betrayal_strikes >= 2 else "medium"
        warnings.append({
            "severity": severity,
            "category": "betrayal",
            "text": (
                f"{target_nation} still remembers {betrayal_strikes} broken commitment"
                f"{'' if betrayal_strikes == 1 else 's'} from {proposer_nation}."
            ),
        })

    hegemony_warning = _build_hegemony_preview_warning(world, proposer_nation, target_nation)
    if hegemony_warning is not None:
        warnings.append(hegemony_warning)

    return _sort_structured_warnings(warnings)


def _build_hegemony_preview_warning(
    world,
    proposer_nation: str,
    target_nation: str,
) -> Dict:
    """Cross-bloc `hegemony` category warning per spec §9.1 + §11.2.

    Gates identical to `hegemony_target_mod` — modifier-and-warning
    symmetry prevents warning-without-modifier feedback-loop confusion.

    Band-aware text via `_hegemony_signal_band(share)`; always reads live
    share via `_identify_max_bloc_share`, NOT the sticky
    `hegemony_signal_high_water` field (which is asymmetric for the
    passive-threat ratchet and would lag previews after de-escalation).

    Returns None when gates fail. Otherwise returns a structured warning:
    - 30-33% (pre-noticed): label-free, no proper noun, severity=low
    - 33-49% (band 1 noticed): descriptive_label, severity=medium
    - 50-59% (band 2 alarming): bloc_label (proper noun), severity=high
    - 60%+ (band 3 crisis): bloc_label, severity=critical
    """
    if not proposer_nation or not target_nation or proposer_nation == target_nation:
        return None
    from backend.game_logic.coalition import (
        _hegemony_signal_band,
        _identify_max_bloc_share,
        _pick_counterplay_hint,
        describe_hegemon_bloc,
    )
    hegemon, share = _identify_max_bloc_share(world)
    if hegemon is None or share < 0.30:
        return None
    try:
        members = set(world.get_bloc_members(hegemon))
    except AttributeError:
        return None
    if proposer_nation not in members or target_nation in members:
        return None

    band = _hegemony_signal_band(share)
    if band == 0:
        # 30-33% pre-noticed: label-free, private.
        text = (
            "European courts are quietly tallying allies; cross-bloc proposals "
            "will meet unspoken resistance."
        )
        severity = "low"
    else:
        bloc = describe_hegemon_bloc(world, hegemon, share)
        label = bloc.get("bloc_label") or bloc.get("descriptive_label") or hegemon
        if band == 1:
            severity = "medium"
            text = (
                f"{target_nation}'s court sees the {label} consolidating across "
                f"Europe and will resist a cross-bloc agreement."
            )
        elif band == 2:
            severity = "high"
            text = (
                f"{target_nation} hardens against {label} — every cross-bloc "
                f"proposal now costs more."
            )
        else:  # band == 3
            severity = "critical"
            text = (
                f"{target_nation} treats {label} as a continental emergency; "
                f"cross-bloc agreements have grown nearly unreachable."
            )
        # Counter-play hint — only when the asker is the hegemon and a
        # legible lever exists. `_pick_counterplay_hint` returns "" for
        # non-hegemon askers, so restrict to asker == hegemon to avoid
        # routing France-specific advice through non-hegemon bloc members.
        if proposer_nation == hegemon:
            hint = _pick_counterplay_hint(world, hegemon, share, band)
            if hint:
                text = f"{text} {hint}"

    return {
        "severity": severity,
        "category": "hegemony",
        "text": text,
    }


def determine_ai_offer_decision_reason(
    nation: str,
    proposal_type: str,
    world,
) -> str:
    """Deterministic reason enum for AI-authored offers in the current substrate."""
    player = getattr(world, "player_nation", "France")
    if proposal_type in ("armistice_losing", "armistice", "peace", "harsh_peace"):
        return "war_overload"
    if _shared_enemy_exists(world, nation, player):
        return "shared_enemy_survival"
    wars_against_player = sum(
        1 for other in getattr(world, "enemy_nations", [])
        if world.is_at_war(player, other)
    )
    if int(getattr(world, "threat_level", 0)) > 60 or wars_against_player >= 2:
        return "hegemony_pressure"
    return "unknown_baseline"


def determine_counterparty_decision_reason(
    proposal: Dict,
    world,
    acceptance_result: Dict = None,
    *,
    stale: bool = False,
) -> str:
    """Deterministic reason enum for AI responses to player proposals."""
    proposer = proposal.get("proposer_nation", getattr(world, "player_nation", "France"))
    target = proposal.get("target_nation", "")
    proposal_type = proposal.get("type", "")

    if stale:
        return "route_blocked"
    components = (acceptance_result or {}).get("components", {}) or {}
    if bool(components.get("anti_renewal_active")):
        return "anti_renewal_active"
    if int(components.get("oathbreaker_posture", 0) or 0) < 0:
        return "distrust_promiser"
    if proposal_type in _DEEP_TREATY_TYPES and has_hard_reject_posture(world, proposer, target):
        return "distrust_promiser"

    if int(components.get("hegemony_target_mod", 0) or 0) < 0:
        return "hegemony_pressure"
    if int(components.get("war_weariness", 0) or 0) <= -10:
        return "war_overload"
    if int(components.get("hard_reject_posture", 0) or 0) < 0:
        return "distrust_promiser"
    if _shared_enemy_exists(world, proposer, target):
        return "shared_enemy_survival"
    return "hegemony_pressure"


# ═══════════════════════════════════════════════════════
# DP ECONOMY (§4)
# ═══════════════════════════════════════════════════════

def calculate_dp(diplomat, authority: int, controls_capital: bool) -> int:
    """Calculate DP generation for a nation.

    Args:
        diplomat: DiplomaticRepresentative (or None)
        authority: Nation's authority level (0-100)
        controls_capital: Whether nation controls its capital

    Returns:
        DP per turn (1-5)
    """
    base = 3
    skill_bonus = 1 if diplomat and diplomat.skill >= 8 else 0
    authority_bonus = 1 if authority >= 60 else (-1 if authority < 30 else 0)
    capital_penalty = -1 if not controls_capital else 0
    return max(1, min(5, base + skill_bonus + authority_bonus + capital_penalty))


def get_dp_cost(action_type: str, diplomat_skill: int = 10, transition_base: int = 0) -> int:
    """Get DP cost for a diplomatic action, adjusted for skill.

    Base costs from §4b. Skill penalty: +1 if skill 4-6, +2 if skill < 4.
    transition_base: if provided, use the higher of table cost and cumulative
    jump cost (from get_transition_dp_cost). This ensures multi-step jumps
    (e.g. PEACE→ALLIANCE) charge the full intermediate cost.
    """
    base_costs = {
        "propose_peace": 2,
        "propose_alliance": 2,
        "propose_non_aggression": 1,
        "propose_open_borders": 1,
        "propose_downgrade": 1,
        "demand_vassalage": 3,
        "propose_vassalage": 3,  # Fix 4: dialogue builds this key, not demand_vassalage
        "offer_trade": 1,
        "respond": 0,
        "cancel_treaty": 1,
        "invest_vassal": 1,
        "declare_war": 1,
    }
    base = max(base_costs.get(action_type, 1), transition_base)

    # Skill penalty
    if diplomat_skill < 4:
        base += 2
    elif diplomat_skill <= 6:
        base += 1

    return base


# ═══════════════════════════════════════════════════════
# NATION AUTHORITY (AI nations)
# ═══════════════════════════════════════════════════════

def modify_nation_authority(world, nation: str, delta: int) -> int:
    """Modify a nation's authority. Clamped 0-100."""
    auth = getattr(world, 'nation_authority', {})
    current = auth.get(nation, 60)
    new_val = max(0, min(100, current + delta))
    auth[nation] = new_val
    return new_val


def _get_call_to_arms_override(
    world,
    *,
    side: str,
    caller: str,
    callee: str,
    enemy: str,
) -> str:
    """Read an explicit test/UI call-to-arms decision override if present."""
    overrides = getattr(world, "call_to_arms_decisions", {}) or {}
    keys = (
        (side, caller, callee, enemy),
        f"{side}|{caller}|{callee}|{enemy}",
        f"{side}|{caller}|{callee}",
        callee,
    )
    for key in keys:
        if key in overrides:
            return str(overrides[key] or "").lower()
    return ""


def _call_side_power(world, principal: str, side: str) -> int:
    """Approximate call-moment side power from direct-only treaty geometry."""
    from backend.game_logic.coalition import power_score

    members = {principal}
    for nation in world.get_active_nations():
        if nation == principal:
            continue
        state = world.get_diplomatic_state(nation, principal)
        if side == "defender" and state in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
            members.add(nation)
        elif side == "attacker" and state == "ALLIANCE":
            members.add(nation)
    return int(sum(power_score(n, world) for n in members))


def _defensive_call_context(world, *, aggressor: str, victim: str, callee: str) -> Dict:
    """Snapshot DG-4 defensive-call impossibility/costliness inputs."""
    aggressor_power = max(1, _call_side_power(world, aggressor, "attacker"))
    defender_power = max(1, _call_side_power(world, victim, "defender"))
    power_ratio = aggressor_power / defender_power

    capital_threat = False
    try:
        from backend.models.region import NATION_CAPITALS
        capital = NATION_CAPITALS.get(callee)
        region = getattr(world, "regions", {}).get(capital) if capital else None
        if region and getattr(region, "controller", callee) not in (callee, ""):
            capital_threat = True
    except Exception:
        capital_threat = False

    losing_other_war = False
    for other in world.get_active_nations():
        if other in (callee, aggressor):
            continue
        if (
            world.is_at_war(callee, other)
            and get_war_score_for(world, callee, other)
            <= _impossibility_losing_war_floor(world)
        ):
            losing_other_war = True
            break

    impossible = (
        power_ratio >= _impossibility_power_ratio(world)
        or (capital_threat and _impossibility_capital_threat_enabled(world))
        or losing_other_war
    )
    costly = impossible or power_ratio >= DG4_COSTLY_HONOR_POWER_RATIO
    return {
        "side": "defender",
        "caller": victim,
        "callee": callee,
        "enemy": aggressor,
        "aggressor_power": int(aggressor_power),
        "defender_power": int(defender_power),
        "aggressor_power_ratio": round(power_ratio, 2),
        "capital_threat": bool(capital_threat),
        "losing_other_war": bool(losing_other_war),
        "impossible": bool(impossible),
        "costly": bool(costly),
    }


def _resolve_defensive_call_path(
    world,
    *,
    aggressor: str,
    victim: str,
    callee: str,
) -> Dict:
    context = _defensive_call_context(
        world, aggressor=aggressor, victim=victim, callee=callee,
    )
    override = _get_call_to_arms_override(
        world, side="defender", caller=victim, callee=callee, enemy=aggressor,
    )
    if world.is_at_war(callee, victim):
        return {**context, "path": "hard_illegal", "reason": f"already at war with {victim}"}
    if override in ("refuse", "refused", "decline"):
        return {**context, "path": "refused_discretionary", "reason": f"refused {context['side']} call"}
    if override in ("honor", "honour", "honored", "honour_costly", "honor_costly"):
        path = "honored_costly" if context["costly"] else "honored"
        return {**context, "path": path, "reason": f"honored {context['side']} call"}
    if context["impossible"]:
        return {
            **context,
            "path": "impossible_auto_declined",
            "reason": f"aggressor_power_ratio={context['aggressor_power_ratio']}",
        }
    path = "honored_costly" if context["costly"] else "honored"
    return {**context, "path": path, "reason": f"honored {context['side']} call"}


def _resolve_offensive_call_path(
    world,
    *,
    aggressor: str,
    target: str,
    callee: str,
) -> Dict:
    override = _get_call_to_arms_override(
        world, side="attacker", caller=aggressor, callee=callee, enemy=target,
    )
    context = {
        "side": "attacker",
        "caller": aggressor,
        "callee": callee,
        "enemy": target,
    }
    if world.is_at_war(callee, aggressor):
        return {**context, "path": "hard_illegal", "reason": f"already at war with {aggressor}"}
    if override in ("refuse", "refused", "decline"):
        return {**context, "path": "refused_discretionary", "reason": "refused attacker call"}
    return {**context, "path": "honored", "reason": "ALLIANCE with attacker"}


def _append_war_entry(
    entries: Optional[List[Dict]],
    *,
    nation: str,
    path: str,
    side: str,
    reason: str,
    treaty_state: str = "",
    refusal_episode_id: str = "",
    honor_episode_id: str = "",
) -> None:
    if entries is None:
        return
    entry = {
        "nation": nation,
        "path": path,
        "side": side,
        "reason": reason,
    }
    if treaty_state:
        entry["treaty_state"] = treaty_state
    if refusal_episode_id:
        entry["refusal_episode_id"] = refusal_episode_id
    if honor_episode_id:
        entry["honor_episode_id"] = honor_episode_id
    entries.append(entry)


# ═══════════════════════════════════════════════════════
# WAR DECLARATION & CASCADE
# ═══════════════════════════════════════════════════════

def declare_war(
    world,
    aggressor: str,
    target: str,
    casus_belli: bool = False,
    origin_episode_id: str = None,
    war_objective: str = None,
    ally_entry_decisions: Optional[Dict[str, Dict]] = None,
    suppress_unresolved_offensive_cascade: bool = False,
) -> Dict:
    """Declare war: transition to WAR, apply penalties, handle cascade.

    Args:
        world: WorldState
        aggressor: Nation declaring war
        target: Nation being declared upon
        casus_belli: If True, halve relation penalties (R21 ultimatum rejection)
        war_objective: Optional objective type (conquest/subjugation/forced_alliance)

    Returns:
        {"success": bool, "message": str, "cascade": list of cascade entries,
         "dp_cost": int, "relation_changes": list}
    """
    # Deep audit fix 7: Prevent self-war
    if aggressor == target:
        return {"success": False, "message": "A nation cannot declare war on itself."}

    diplo_key = world._make_diplo_key(aggressor, target)
    current_state = world.diplomatic_states.get(diplo_key, "PEACE")

    if current_state == "WAR":
        return {"success": False, "message": f"{aggressor} is already at war with {target}."}

    if war_objective:
        if war_objective not in OFFENSIVE_OBJECTIVE_TYPES:
            return {
                "success": False,
                "message": f"Invalid offensive war objective: {war_objective}.",
            }
        availability = _get_objective_availability(
            world, aggressor, target, war_objective
        )
        if availability and not availability.get("available", False):
            return {
                "success": False,
                "message": availability.get("reason")
                or f"{war_objective.replace('_', ' ').title()} is not available.",
            }
    elif (aggressor != getattr(world, 'player_nation', None)
          and target != getattr(world, 'player_nation', None)):
        # WPS-A: future AI-AI/opportunistic wars default to conquest.
        war_objective = "conquest"

    # R99: Block war declaration during armistice cooldown
    armistice_cooldown = getattr(world, 'armistice_cooldowns', {}).get(diplo_key, 0)
    if armistice_cooldown > 0:
        return {
            "success": False,
            "message": f"Armistice cooldown in effect with {target} ({armistice_cooldown} turns remaining). War cannot be declared."
        }

    # Allocate a single root-cause episode_id for this declaration and thread
    # it through the primary breach record (if any), the cascade, and all
    # dispatch/log emits so C3 can collapse the resulting consequences under
    # one political moment (RELIABILITY_COMMITMENTS_SPEC §6.5).
    episode_id = origin_episode_id or _allocate_episode_id(world)

    war_preview = preview_war_declaration(
        world,
        aggressor,
        target,
        casus_belli=casus_belli,
        episode_id=episode_id,
    )
    breach_preview = war_preview.get("breach_preview")
    if breach_preview is not None:
        breach_preview["episode_id"] = episode_id

    # War declarations are compound state transitions: the root WAR edge,
    # direct-only call-to-arms cascade, and direct vassal joins all describe
    # one final diplomatic geometry. Defer Balance-of-Europe beats until the
    # cascade settles so the rail does not narrate impossible intermediate
    # bloc leaders.
    _begin_hegemony_signal_defer(world)

    # Slice A2 §"Creation seam": validate side assignment + allocate or reuse
    # the active war_instance BEFORE mutating diplomatic_states. A
    # `war_instance_side_conflict` must hard-stop pre-commit; A2 also stops
    # on `war_instance_merge_required` so callers can fix the seam before
    # A3 lands the connected-component merge transaction.
    war_instance_result = ensure_war_instance_for_pair(
        world,
        aggressor,
        target,
        entry_path="war_declaration",
        root_episode_id=episode_id,
        reason="player/AI war declaration",
    )
    if not war_instance_result.get("ok"):
        _flush_hegemony_signal_defer(world, "declare_war_validation_failed")
        return {
            "success": False,
            "message": (
                f"Cannot declare war: {war_instance_result.get('error')} "
                f"({war_instance_result.get('details', {}).get('reason', '')})"
            ),
            "error": war_instance_result.get("error"),
            "error_details": war_instance_result.get("details", {}),
        }
    war_id = war_instance_result["war_id"]

    # Transition to WAR (R2: centralized setter handles war_start_turns + treaty removal)
    set_diplomatic_state(world, aggressor, target, "WAR", "war_declaration")

    # Penalties (halved with casus belli from rejected ultimatum)
    penalty_factor = 0.5 if casus_belli else 1.0
    relation_changes = []
    direct_penalty = int(-30 * penalty_factor)
    world.modify_nation_relation(aggressor, target, direct_penalty)
    relation_changes.append({"nations": (aggressor, target), "delta": direct_penalty})

    # Penalty with ALL other nations (also halved with casus belli)
    indirect_penalty = int(-15 * penalty_factor)
    all_nations = world.get_active_nations()  # DLF-11
    for nation in all_nations:
        if nation != aggressor and nation != target:
            world.modify_nation_relation(aggressor, nation, indirect_penalty)
            relation_changes.append({"nations": (aggressor, nation), "delta": indirect_penalty})

    # Coalition threat: +20 for France declaring war, halved with casus belli (§2a, S5c)
    if aggressor == world.player_nation:
        from backend.game_logic.coalition import add_threat
        threat = 10 if casus_belli else 20
        add_threat(world, threat, "war_declaration")

    # Authority changes for AI nations
    nation_auth = getattr(world, 'nation_authority', {})
    if target in nation_auth:
        # Being attacked doesn't change authority directly
        pass

    if breach_preview:
        # Suppress the TREATY_BROKEN notification and dispatch entry: the
        # WAR_DECLARED notification + `diplomatic_war_declared` dispatch event
        # below carry the "shattering" phrasing and breach metadata, so
        # surfacing both would violate the §8.4 no-duplicate-surface rule.
        # The episode_id is threaded into both so presentation can still
        # reconstruct the witness set and reliability delta.
        _record_treaty_breach(
            world,
            breach_preview,
            new_state="WAR",
            suppress_notification=True,
            suppress_dispatch_event=True,
            trigger_context={
                "aggressor": aggressor,
                "target": target,
                "casus_belli": bool(casus_belli),
                "defensive_joiners": war_preview["defensive_joiners"],
                "offensive_joiners": war_preview["offensive_joiners"],
                "episode_id": episode_id,
            },
        )

    # WPS-A: Create war objectives
    diplo_key_obj = world._make_diplo_key(aggressor, target)
    if war_objective and war_objective in OFFENSIVE_OBJECTIVE_TYPES:
        from backend.models.region import NATION_CAPITALS as _NATION_CAPITALS
        target_capital = _NATION_CAPITALS.get(target)
        target_regions = [target_capital] if target_capital else []

        if diplo_key_obj not in world.war_objectives:
            world.war_objectives[diplo_key_obj] = {}

        world.war_objectives[diplo_key_obj][aggressor] = create_war_objective(
            objective_type=war_objective,
            declaring_nation=aggressor,
            target_nation=target,
            target_regions=target_regions,
            current_turn=world.current_turn,
        )

        world.log_event({
            "type": "war_objective_declared",
            "declaring_nation": aggressor,
            "target_nation": target,
            "objective_type": war_objective,
            "target_regions": target_regions,
            "turn": int(world.current_turn),
        })

    _auto_assign_defense_objective(world, target, aggressor, diplo_key_obj)

    # DP cost: 1
    dp_cost = WAR_DP_COST

    # Log event
    world.log_event({
        "type": "war_declaration",
        "aggressor": aggressor,
        "target": target,
        "previous_state": current_state,
        "episode_id": episode_id,
        "war_objective": war_objective or "",
        "breached_treaty": breach_preview["treaty_type_display"] if breach_preview else "",
        "breach_reason_family": breach_preview["end_reason_family"] if breach_preview else "",
        "breach_reason_action": breach_preview["end_reason_action"] if breach_preview else "",
        "reliability_before": breach_preview["reliability_before"] if breach_preview else None,
        "reliability_after": breach_preview["reliability_after"] if breach_preview else None,
        "applied_reliability_delta": breach_preview["applied_reliability_delta"] if breach_preview else 0,
        "defensive_joiners": war_preview["defensive_joiners"],
        "offensive_joiners": war_preview["offensive_joiners"],
    })

    # ── R12: ALLIANCE PARADOX CHECK (must run BEFORE cascade) ──
    # If both aggressor and target are allied with the player, the player
    # faces a paradox: honoring one alliance means breaking the other.
    # The cascade must skip the player so the player can choose.
    has_paradox = False
    player = world.player_nation
    if aggressor != player and target != player:
        aggressor_state = world.get_diplomatic_state(player, aggressor)
        target_state = world.get_diplomatic_state(player, target)
        alliance_states = ("ALLIANCE", "DEFENSIVE_ALLIANCE")
        if aggressor_state in alliance_states and target_state in alliance_states:
            has_paradox = True
            paradox_episode_id = _allocate_episode_id(world)
            # Preview both branches of the paradox using one durable
            # origin_episode_id so the hard-stop survives save/load and the
            # eventual choice can log one coherent remembered political moment.
            attacker_treaty = getattr(world, 'active_treaties', {}).get(
                world._make_diplo_key(player, aggressor)
            )
            defender_treaty = getattr(world, 'active_treaties', {}).get(
                world._make_diplo_key(player, target)
            )
            attacker_breach_preview = get_treaty_breach_preview(
                world,
                player,
                aggressor,
                treaty=attacker_treaty,
                end_reason_action="paradox_choice",
                fault_nation=player,
                episode_id=paradox_episode_id,
            )
            defender_breach_preview = get_treaty_breach_preview(
                world,
                player,
                target,
                treaty=defender_treaty,
                end_reason_action="paradox_choice",
                fault_nation=player,
                episode_id=paradox_episode_id,
            )
            attacker_paradox_warnings = _build_breach_warnings(attacker_breach_preview)
            defender_paradox_warnings = _build_breach_warnings(defender_breach_preview)
            paradox_msg = (
                f"Sire, a crisis! {aggressor} has declared war on {target}. "
                f"We are allied with both nations. We must choose a side."
            )
            preview_lines = []
            if attacker_paradox_warnings:
                preview_lines.append(
                    "Honor "
                    + target
                    + ": "
                    + " ".join(w["text"] for w in attacker_paradox_warnings)
                )
            if defender_paradox_warnings:
                preview_lines.append(
                    "Side with "
                    + aggressor
                    + ": "
                    + " ".join(w["text"] for w in defender_paradox_warnings)
                )
            if preview_lines:
                paradox_msg += "\n\n" + "\n".join(preview_lines)
            ally_preview = {
                "honor_defender": attacker_breach_preview,
                "break_defender_alliance": defender_breach_preview,
            }
            diplomats = getattr(world, "diplomats", {}) or {}
            attacker_diplomat = getattr(diplomats.get(aggressor), "name", "")
            defender_diplomat = getattr(diplomats.get(target), "name", "")
            world.commitment_paradox_popup = {
                "episode_id": paradox_episode_id,
                "primary_nation": aggressor,
                "secondary_nation": target,
                "attacker": aggressor,
                "defender": target,
                "attacker_diplomat": attacker_diplomat,
                "defender_diplomat": defender_diplomat,
                "ally": player,
                "attacker_alliance": aggressor_state,
                "defender_alliance": target_state,
                "message": paradox_msg,
                "origin_episode_id": paradox_episode_id,  # legacy alias
                "attacker_preview": attacker_breach_preview,
                "defender_preview": defender_breach_preview,
                "ally_preview": ally_preview,
                "honor_defender_preview": attacker_breach_preview,
                "break_defender_preview": defender_breach_preview,
            }
            # V2-89 → R12C: push() auto-queues if another dialogue is active
            world.dialogue_manager.push({
                "type": "commitment_paradox",
                "target_nation": "",
                "talleyrand_text": paradox_msg,
                "episode_id": paradox_episode_id,
                "origin_episode_id": paradox_episode_id,
                "primary_nation": aggressor,
                "secondary_nation": target,
                "attacker": aggressor,
                "defender": target,
                "attacker_diplomat": attacker_diplomat,
                "defender_diplomat": defender_diplomat,
                "ally": player,
                "attacker_preview": attacker_breach_preview,
                "defender_preview": defender_breach_preview,
                "ally_preview": ally_preview,
                "breach_preview": defender_breach_preview,  # legacy alias: "side with aggressor"
                "warnings": defender_paradox_warnings,  # legacy alias for current UI consumers
                "honor_defender_preview": attacker_breach_preview,
                "honor_defender_warnings": attacker_paradox_warnings,
                "break_defender_preview": defender_breach_preview,
                "break_defender_warnings": defender_paradox_warnings,
                "options": [
                    {
                        "label": f"Honor alliance with {target}",
                        "description": f"Go to war with {aggressor} in defense of {target}.",
                        "action": "honor_defender",
                        "terms": {"attacker": aggressor, "defender": target},
                    },
                    {
                        "label": f"Side with {aggressor}",
                        "description": f"Break our alliance with {target}.",
                        "action": "break_defender_alliance",
                        "terms": {"attacker": aggressor, "defender": target},
                    },
                ],
                "context": {"attacker": aggressor, "defender": target},
                "turn_created": int(world.current_turn),
                "blocking": True,
            })

    # ── DEFENSIVE_ALLIANCE CASCADE ──
    # If paradox detected, exclude the player from cascade (player must choose)
    cascade_skip = {aggressor, target, player} if has_paradox else None
    war_entry_entries: List[Dict] = []
    cascade_ctx = CascadeContext(
        war_id=war_id,
        root_episode_id=episode_id,
        root_aggressor=aggressor,
        war_entry_entries=war_entry_entries,
        ally_entry_decisions=ally_entry_decisions or {},
        suppress_unresolved_offensive_cascade=suppress_unresolved_offensive_cascade,
    )
    cascade = _process_war_cascade(
        world,
        aggressor,
        target,
        processed=cascade_skip,
        ctx=cascade_ctx,
    )
    _flush_hegemony_signal_defer(world, "declare_war")
    world.log_event({
        "type": "war_entry_ledger",
        "episode_id": episode_id,
        "war_id": war_id,
        "aggressor": aggressor,
        "target": target,
        "entries": war_entry_entries,
        "turn": int(world.current_turn),
    })

    # Notification: war declared (Session 8C)
    from backend.notifications import (
        create_notification, NotificationPriority, WAR_DECLARED,
    )
    war_message = f"{aggressor} has declared war on {target}."
    if breach_preview:
        war_message = (
            f"{aggressor} has declared war on {target}, shattering the "
            f"{breach_preview['treaty_type_display']}."
        )
    world.notifications.add(create_notification(
        WAR_DECLARED,
        NotificationPriority.HIGH,
        f"War with {target}!" if aggressor == world.player_nation else f"{aggressor} Declares War!",
        war_message,
        int(world.current_turn),
    ))

    # Dispatch event (Session 8D)
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, "diplomatic_war_declared",
                        {
                            "nation": aggressor,
                            "target": target,
                            "episode_id": episode_id,
                            "breached_treaty": breach_preview["treaty_type_display"] if breach_preview else "",
                            "end_reason_family": breach_preview["end_reason_family"] if breach_preview else "",
                            "defensive_joiner_count": len(war_preview["defensive_joiners"]),
                            "offensive_joiner_count": len(war_preview["offensive_joiners"]),
                        },
                        "partial_on_nation")

    # R29: Log to diplomatic history
    diplomatic_history = getattr(world, 'diplomatic_history', [])
    diplomatic_history.append({
        "turn": int(world.current_turn),
        "type": "war_declared",
        "nation": aggressor,
        "target": target,
        "detail": breach_preview["treaty_type"] if breach_preview else "",
    })
    if len(diplomatic_history) > 20:
        diplomatic_history[:] = diplomatic_history[-20:]
    world.diplomatic_history = diplomatic_history

    if breach_preview:
        messages = [
            f"{aggressor} declares war on {target}, shattering the {breach_preview['treaty_type_display']}!"
        ]
    else:
        messages = [f"{aggressor} declares war on {target}!"]
    for c in cascade:
        cascade_type = c.get("cascade_type")
        if cascade_type == "offensive":
            messages.append(
                f"{c['attacker_ally']} enters the war against {c['target']}, "
                f"honoring alliance with {c['aggressor']}!"
            )
        elif cascade_type in (
            "vassal_defensive_auto_join",
            "vassal_offensive_auto_join",
            "vassal_auto_join",
        ):
            messages.append(
                f"{c['vassal']} follows {c['lord']} into the war against "
                f"{c['target']}!"
            )
        else:
            messages.append(
                f"{c['defender']} enters the war against {aggressor} "
                f"in defense of {c['ally']}!"
            )

    return {
        "success": True,
        "message": " ".join(messages),
        "cascade": cascade,
        "war_entry_ledger": war_entry_entries,
        "war_id": war_id,
        "dp_cost": dp_cost,
        "relation_changes": relation_changes,
    }


def _process_war_cascade(
    world,
    aggressor: str,
    target: str,
    processed: set = None,
    *,
    ctx: Optional[CascadeContext] = None,
    root_episode_id: str = None,
    root_aggressor: str = None,
    war_entry_entries: Optional[List[Dict]] = None,
    ally_entry_decisions: Optional[Dict[str, Dict]] = None,
    suppress_unresolved_offensive_cascade: bool = False,
) -> List[Dict]:
    """Process DG-4 direct-only call-to-arms when war is declared.

    Defensive: Nations with DA/ALLIANCE with the TARGET join against the aggressor.
    Offensive: Nations with ALLIANCE (not DA) with the AGGRESSOR join against the target.
    Direct vassals of either principal auto-join their lord's side.

    Slice A2: every cascaded pair attaches to the root war's
    `ctx.war_id`. Callers that pass legacy keyword args still work — a
    `CascadeContext` is synthesized when ``ctx`` is None — but new
    callers should construct the context once and pass it through.

    Cascade-forced ruptures are classified `obsolescence_or_external` (§9.9.B):
    the cascaded nation did not voluntarily break its treaty, so fault is
    attributed to the root aggressor and no reliability penalty is applied
    to the cascaded party.

    DG-4 forbids transitive propagation: allies of joiners and vassals of
    joiners are not called by this root war.
    """
    if processed is None:
        processed = {aggressor, target}

    if ctx is None:
        ctx = CascadeContext(
            war_id="",
            root_episode_id=root_episode_id,
            root_aggressor=root_aggressor,
            war_entry_entries=war_entry_entries,
            ally_entry_decisions=ally_entry_decisions or {},
            suppress_unresolved_offensive_cascade=suppress_unresolved_offensive_cascade,
        )
    else:
        # Honor legacy positional kwargs only if the context did not set them.
        if root_episode_id is not None and ctx.root_episode_id is None:
            ctx.root_episode_id = root_episode_id
        if root_aggressor is not None and ctx.root_aggressor is None:
            ctx.root_aggressor = root_aggressor
        if war_entry_entries is not None and ctx.war_entry_entries is None:
            ctx.war_entry_entries = war_entry_entries
        if ally_entry_decisions:
            for k, v in ally_entry_decisions.items():
                ctx.ally_entry_decisions.setdefault(k, v)
        if suppress_unresolved_offensive_cascade:
            ctx.suppress_unresolved_offensive_cascade = True

    war_entry_entries = ctx.war_entry_entries
    ally_entry_decisions = ctx.ally_entry_decisions or {}
    suppress_unresolved_offensive_cascade = bool(ctx.suppress_unresolved_offensive_cascade)

    def _attach_cascade_pair(attacker_nation: str, defender_nation: str, entry_path: str) -> Dict:
        cascade_war_id = ctx.war_id or ""
        if not cascade_war_id:
            return {"ok": True, "war_id": ""}
        result = attach_pair_to_war_instance(
            world,
            cascade_war_id,
            attacker_nation,
            defender_nation,
            entry_path=entry_path,
        )
        if result.get("ok"):
            returned_war_id = result.get("war_id") or ""
            if returned_war_id and returned_war_id != ctx.war_id:
                ctx.war_id = returned_war_id
            return result
        blocked = {
            "type": "war_cascade_blocked",
            "entry_path": entry_path,
            "war_id": cascade_war_id,
            "attacker": attacker_nation,
            "defender": defender_nation,
            "error": result.get("error"),
            "details": result.get("details", {}),
            "turn": int(getattr(world, "current_turn", 0) or 0),
        }
        if hasattr(world, "log_event"):
            world.log_event(blocked)
        _append_war_entry(
            war_entry_entries,
            nation=defender_nation,
            path="war_instance_blocked",
            side="blocked",
            reason=str(result.get("error") or "war_instance_attach_failed"),
            treaty_state=world.get_diplomatic_state(attacker_nation, defender_nation),
        )
        return result

    # Fault for any rupture caused by the cascade is the root aggressor, not
    # whichever nation's treaty happens to flip in a recursive step.
    fault_aggressor = ctx.root_aggressor or aggressor
    root_episode_id = ctx.root_episode_id

    cascade = []
    all_nations = world.get_active_nations()  # DLF-11

    for nation in all_nations:
        if nation in processed:
            continue

        # Check if this nation has DEFENSIVE_ALLIANCE or ALLIANCE with the target
        state = world.get_diplomatic_state(nation, target)
        if state in ("DEFENSIVE_ALLIANCE", "ALLIANCE"):
            # Check if already at war with aggressor
            if not world.is_at_war(nation, aggressor):
                decision = _resolve_defensive_call_path(
                    world, aggressor=aggressor, victim=target, callee=nation,
                )
                if decision["path"] == "hard_illegal":
                    _append_war_entry(
                        war_entry_entries,
                        nation=nation,
                        path="hard_illegal",
                        side="defender",
                        reason=decision["reason"],
                        treaty_state=state,
                    )
                    continue
                if decision["path"] == "impossible_auto_declined":
                    _append_war_entry(
                        war_entry_entries,
                        nation=nation,
                        path="impossible_auto_declined",
                        side="defender",
                        reason=decision["reason"],
                        treaty_state=state,
                    )
                    continue
                if decision["path"] == "refused_discretionary":
                    refusal = emit_call_to_arms_refused_defensive(
                        world,
                        breaker=nation,
                        victim=target,
                        call_context=decision,
                    )
                    _append_war_entry(
                        war_entry_entries,
                        nation=nation,
                        path="refused_discretionary",
                        side="defender",
                        reason=decision["reason"],
                        treaty_state=state,
                        refusal_episode_id=refusal["episode_id"],
                    )
                    continue
                honor_episode_id = ""
                if decision["path"] == "honored_costly":
                    honor = emit_call_to_arms_honored_costly(
                        world,
                        honorer=nation,
                        victim=target,
                        call_context=decision,
                    )
                    honor_episode_id = honor["episode_id"]
                existing_treaty = getattr(world, 'active_treaties', {}).get(
                    world._make_diplo_key(nation, aggressor)
                )
                breach_preview = None
                if existing_treaty or world.get_diplomatic_state(nation, aggressor) in COMMITMENT_STATES:
                    breach_preview = get_treaty_breach_preview(
                        world,
                        nation,
                        aggressor,
                        treaty=existing_treaty,
                        end_reason_action="cascade_forced",
                        fault_nation=fault_aggressor,
                        episode_id=root_episode_id,
                    )
                # Force WAR — bypasses armistice cooldowns (R2: centralized setter)
                attach_result = _attach_cascade_pair(aggressor, nation, "defensive_cascade")
                if not attach_result.get("ok"):
                    continue
                _append_war_entry(
                    war_entry_entries,
                    nation=nation,
                    path=decision["path"],
                    side="defender",
                    reason=decision["reason"],
                    treaty_state=state,
                    honor_episode_id=honor_episode_id,
                )
                set_diplomatic_state(world, nation, aggressor, "WAR", "defensive_cascade")
                processed.add(nation)
                if breach_preview:
                    _record_treaty_breach(
                        world,
                        breach_preview,
                        new_state="WAR",
                        trigger_context={
                            "cascade_type": "defensive",
                            "ally": target,
                            "aggressor": aggressor,
                            "root_aggressor": fault_aggressor,
                            "root_episode_id": root_episode_id,
                        },
                    )

                # R100: Apply relation penalty for cascaded war
                world.modify_nation_relation(aggressor, nation, -20)

                cascade.append({
                    "defender": nation,
                    "ally": target,
                    "previous_state": state,
                })

                world.log_event({
                    "type": "defensive_cascade",
                    "defender": nation,
                    "ally": target,
                    "against": aggressor,
                })

                # Notification: alliance cascade (Session 8C)
                from backend.notifications import (
                    create_notification, NotificationPriority, ALLIANCE_CASCADE_WAR,
                )
                world.notifications.add(create_notification(
                    ALLIANCE_CASCADE_WAR,
                    NotificationPriority.HIGH,
                    f"{nation} Enters War!",
                    f"{nation} enters the war via alliance with {target}.",
                    int(world.current_turn),
                ))

                # Dispatch event (Session 8D)
                from backend.game_logic.dispatch import queue_dispatch_event
                queue_dispatch_event(world, "diplomatic_alliance_cascade",
                                    {"nation": nation, "ally": target},
                                    "partial_on_nation")

    # ── OFFENSIVE CASCADE: Aggressor's ALLIANCE partners join against target ──
    for nation in all_nations:
        if nation in processed:
            continue
        if nation in getattr(world, 'vassals', {}):
            continue  # Vassals handled in vassal auto-join block below

        state_with_aggressor = world.get_diplomatic_state(nation, aggressor)
        if state_with_aggressor == "ALLIANCE":
            if not world.is_at_war(nation, target):
                entry_decision = ally_entry_decisions.get(nation, {})
                if suppress_unresolved_offensive_cascade and not entry_decision:
                    _append_war_entry(
                        war_entry_entries,
                        nation=nation,
                        path="not_requested",
                        side="attacker",
                        reason="offensive ally entry requires explicit resolution",
                        treaty_state=state_with_aggressor,
                    )
                    continue

                if entry_decision:
                    resolution = str(entry_decision.get("resolution", "reject"))
                    if resolution in ("reject", "refuse", "blocked"):
                        path = "hard_illegal" if resolution == "blocked" else "refused_free_join"
                        reason = entry_decision.get("reason", "ally entry declined")
                        _append_war_entry(
                            war_entry_entries,
                            nation=nation,
                            path=path,
                            side="attacker",
                            reason=reason,
                            treaty_state=state_with_aggressor,
                        )
                        continue
                    decision = {
                        "side": "attacker",
                        "caller": aggressor,
                        "callee": nation,
                        "enemy": target,
                        "path": "honored",
                        "reason": entry_decision.get("reason", "accepted offensive ally-entry request"),
                    }
                else:
                    decision = _resolve_offensive_call_path(
                        world, aggressor=aggressor, target=target, callee=nation,
                    )

                if decision["path"] == "hard_illegal":
                    _append_war_entry(
                        war_entry_entries,
                        nation=nation,
                        path="hard_illegal",
                        side="attacker",
                        reason=decision["reason"],
                        treaty_state=state_with_aggressor,
                    )
                    continue
                if decision["path"] == "refused_discretionary":
                    refusal = emit_call_to_arms_refused_offensive(
                        world,
                        breaker=nation,
                        victim=aggressor,
                        call_context=decision,
                    )
                    _append_war_entry(
                        war_entry_entries,
                        nation=nation,
                        path="refused_discretionary",
                        side="attacker",
                        reason=decision["reason"],
                        treaty_state=state_with_aggressor,
                        refusal_episode_id=refusal["episode_id"],
                    )
                    continue
                resolution_path = entry_decision.get("resolution_path", "offensive_free_join")
                ledger_path = "honored"
                if resolution_path == "offensive_counter_bargain_accept":
                    ledger_path = "offensive_counter_bargain_accept"
                elif resolution_path == "offensive_bargain_helped":
                    ledger_path = "offensive_bargain_helped"
                existing_treaty = getattr(world, 'active_treaties', {}).get(
                    world._make_diplo_key(nation, target)
                )
                breach_preview = None
                if existing_treaty or world.get_diplomatic_state(nation, target) in COMMITMENT_STATES:
                    breach_preview = get_treaty_breach_preview(
                        world,
                        nation,
                        target,
                        treaty=existing_treaty,
                        end_reason_action="cascade_forced",
                        fault_nation=fault_aggressor,
                        episode_id=root_episode_id,
                    )
                attach_result = _attach_cascade_pair(nation, target, "offensive_cascade")
                if not attach_result.get("ok"):
                    continue
                _append_war_entry(
                    war_entry_entries,
                    nation=nation,
                    path=ledger_path,
                    side="attacker",
                    reason=decision["reason"],
                    treaty_state=state_with_aggressor,
                )
                set_diplomatic_state(world, nation, target, "WAR", "offensive_cascade")
                processed.add(nation)
                if breach_preview:
                    _record_treaty_breach(
                        world,
                        breach_preview,
                        new_state="WAR",
                        trigger_context={
                            "cascade_type": "offensive",
                            "aggressor": aggressor,
                            "target": target,
                            "root_aggressor": fault_aggressor,
                            "root_episode_id": root_episode_id,
                        },
                    )
                world.modify_nation_relation(nation, target, -20)
                _trigger_matching_war_entry_bargains(
                    world,
                    aggressor,
                    nation,
                    target,
                    resolution_path=resolution_path,
                    was_bargain_decisive=bool(entry_decision.get("was_bargain_decisive", False)),
                )

                cascade.append({
                    "attacker_ally": nation,
                    "aggressor": aggressor,
                    "target": target,
                    "cascade_type": "offensive",
                })

                world.log_event({
                    "type": "offensive_cascade",
                    "attacker_ally": nation,
                    "aggressor": aggressor,
                    "against": target,
                })

                from backend.notifications import (
                    create_notification, NotificationPriority, ALLIANCE_CASCADE_WAR,
                )
                world.notifications.add(create_notification(
                    ALLIANCE_CASCADE_WAR,
                    NotificationPriority.HIGH,
                    f"{nation} Joins Offensive!",
                    f"{nation} enters the war against {target}, honoring alliance with {aggressor}.",
                    int(world.current_turn),
                ))

                from backend.game_logic.dispatch import queue_dispatch_event
                queue_dispatch_event(world, "diplomatic_offensive_cascade",
                                    {"nation": nation, "aggressor": aggressor, "target": target},
                                    "partial_on_nation")

    # VASSAL AUTO-JOIN: DG-4 only calls direct vassals of root principals.
    vassals = getattr(world, 'vassals', {})
    for vassal_nation, vassal_data in vassals.items():
        if vassal_nation in processed:
            continue
        lord = vassal_data.get("lord", "")
        if lord == target and not world.is_at_war(vassal_nation, aggressor):
            attach_result = _attach_cascade_pair(aggressor, vassal_nation, "vassal_defensive_auto_join")
            if not attach_result.get("ok"):
                continue
            set_diplomatic_state(
                world, vassal_nation, aggressor, "WAR", "vassal_auto_join",
            )
            processed.add(vassal_nation)
            _append_war_entry(
                war_entry_entries,
                nation=vassal_nation,
                path="honored",
                side="defender_vassal",
                reason=f"vassal of {lord}",
                treaty_state="VASSAL",
            )

            cascade.append({
                "vassal": vassal_nation,
                "lord": lord,
                "target": aggressor,
                "cascade_type": "vassal_defensive_auto_join",
            })

            world.log_event({
                "type": "vassal_auto_join_war",
                "vassal": vassal_nation,
                "lord": lord,
                "against": aggressor,
            })
            continue
        if lord == aggressor:
            # Direct attacker vassal follows the root aggressor.
            if not world.is_at_war(vassal_nation, target):
                attach_result = _attach_cascade_pair(vassal_nation, target, "vassal_offensive_auto_join")
                if not attach_result.get("ok"):
                    continue
                set_diplomatic_state(world, vassal_nation, target, "WAR", "vassal_auto_join")
                processed.add(vassal_nation)
                _append_war_entry(
                    war_entry_entries,
                    nation=vassal_nation,
                    path="honored",
                    side="attacker_vassal",
                    reason=f"vassal of {lord}",
                    treaty_state="VASSAL",
                )

                cascade.append({
                    "vassal": vassal_nation,
                    "lord": lord,
                    "target": target,
                    "cascade_type": "vassal_offensive_auto_join",
                })

                world.log_event({
                    "type": "vassal_auto_join_war",
                    "vassal": vassal_nation,
                    "lord": lord,
                    "against": target,
                })

    return cascade


# ═══════════════════════════════════════════════════════
# DOWNGRADE TRANSITIONS (§5b.1)
# ═══════════════════════════════════════════════════════

def execute_downgrade(world, nation_a: str, nation_b: str) -> Dict:
    """Execute a one-step downgrade between two nations.

    Returns:
        {"success": bool, "message": str, "new_state": str, "dp_cost": int}
    """
    diplo_key = world._make_diplo_key(nation_a, nation_b)
    current_state = world.diplomatic_states.get(diplo_key, "PEACE")

    # Find next downgrade step
    if current_state not in _DOWNGRADE_ORDER:
        return {"success": False, "message": f"Cannot downgrade from {current_state}."}

    idx = _DOWNGRADE_ORDER.index(current_state)
    if idx >= len(_DOWNGRADE_ORDER) - 1:
        return {"success": False, "message": f"Already at minimum downgradable state ({current_state})."}

    new_state = _DOWNGRADE_ORDER[idx + 1]
    penalties = DOWNGRADE_PENALTIES.get((current_state, new_state))
    if not penalties:
        return {"success": False, "message": f"No downgrade path from {current_state} to {new_state}."}

    # Apply (R2: centralized setter; treaty removal handled separately for non-WAR downgrades)
    set_diplomatic_state(world, nation_a, nation_b, new_state, "diplomatic_downgrade")
    bargain_breach_events = detect_bargain_breach_on_treaty_change(
        world, nation_a, nation_b, new_state,
    )

    # R45: Remove active treaty on downgrade (treaty was for the old state)
    active_treaties = getattr(world, 'active_treaties', {})
    active_treaties.pop(diplo_key, None)

    # Relation penalties
    world.modify_nation_relation(nation_a, nation_b, penalties["relation_target"])
    all_nations = world.get_active_nations()  # DLF-11
    if penalties["relation_all"] != 0:
        for nation in all_nations:
            if nation != nation_a and nation != nation_b:
                world.modify_nation_relation(nation_a, nation, penalties["relation_all"])

    # Coalition threat from downgrade (§2a)
    threat_amount = penalties.get("threat", 0)
    if threat_amount > 0 and nation_a == world.player_nation:
        from backend.game_logic.coalition import add_threat
        add_threat(world, threat_amount, "diplomatic_downgrade")

    world.log_event({
        "type": "diplomatic_downgrade",
        "from_state": current_state,
        "to_state": new_state,
        "nation_a": nation_a,
        "nation_b": nation_b,
    })

    return {
        "success": True,
        "message": f"Diplomatic relations between {nation_a} and {nation_b} downgraded: {_STATE_DISPLAY_NAMES.get(current_state, current_state)} → {_STATE_DISPLAY_NAMES.get(new_state, new_state)}.",
        "new_state": new_state,
        "dp_cost": penalties["dp_cost"],
        "bargain_breach_events": bargain_breach_events,
    }


def _process_forced_alliance_drift(world) -> List[Dict]:
    """WPS-C §9.5: Apply -10/turn relation drift for forced alliances.

    Runs before auto-downgrade check so the downgrade reads post-drift relation.
    """
    events = []
    alliance_origins = getattr(world, 'alliance_origins', {})
    for diplo_key, origin in list(alliance_origins.items()):
        if origin != "forced":
            continue
        current_state = world.diplomatic_states.get(diplo_key, "PEACE")
        if current_state != "ALLIANCE":
            alliance_origins.pop(diplo_key, None)
            continue
        parts = diplo_key.split("|")
        if len(parts) == 2:
            world.modify_nation_relation(parts[0], parts[1], -10)
    world.alliance_origins = alliance_origins
    return events


def check_auto_downgrade(world) -> List[Dict]:
    """Check for automatic downgrades when relations stay 30+ below threshold for 5 turns.

    Returns list of downgrade events for Morning Dispatch.
    """
    turns_below = getattr(world, 'turns_below_threshold', {})
    events = []

    for diplo_key, state in list(world.diplomatic_states.items()):
        threshold = STATE_RELATION_THRESHOLDS.get(state)
        if threshold is None:
            # State not subject to auto-downgrade
            turns_below.pop(diplo_key, None)
            continue

        relation = world.nation_relations.get(diplo_key, 0)
        gap = threshold - relation  # Positive = below threshold

        if gap >= 30:
            turns_below[diplo_key] = turns_below.get(diplo_key, 0) + 1

            # Warn at turn 3 (2 turns before downgrade)
            if turns_below[diplo_key] == 3:
                parts = diplo_key.split("|")
                events.append({
                    "type": "downgrade_warning",
                    "nations": parts,
                    "state": state,
                    "turns_remaining": 2,
                    "message": f"Relations between {parts[0]} and {parts[1]} are deteriorating. "
                               f"{_STATE_DISPLAY_NAMES.get(state, state)} may collapse in 2 turns.",
                })

            # Auto-downgrade at turn 5
            if turns_below[diplo_key] >= 5:
                parts = diplo_key.split("|")
                # Apply half penalties
                idx = _DOWNGRADE_ORDER.index(state) if state in _DOWNGRADE_ORDER else -1
                if idx >= 0 and idx < len(_DOWNGRADE_ORDER) - 1:
                    new_state = _DOWNGRADE_ORDER[idx + 1]
                    penalties = DOWNGRADE_PENALTIES.get((state, new_state))
                    if penalties:
                        set_diplomatic_state(world, parts[0], parts[1], new_state, "auto_downgrade")
                        # Deep audit fix 5: Clear active treaty on auto-downgrade
                        active_treaties = getattr(world, 'active_treaties', {})
                        active_treaties.pop(diplo_key, None)
                        # Half penalties
                        world.modify_nation_relation(
                            parts[0], parts[1], penalties["relation_target"] // 2)
                        turns_below[diplo_key] = 0  # Reset counter

                        events.append({
                            "type": "auto_downgrade",
                            "nations": parts,
                            "from_state": state,
                            "to_state": new_state,
                            "message": f"Relations between {parts[0]} and {parts[1]} have collapsed: "
                                       f"{_STATE_DISPLAY_NAMES.get(state, state)} → {_STATE_DISPLAY_NAMES.get(new_state, new_state)}.",
                        })

                        world.log_event({
                            "type": "auto_downgrade",
                            "from_state": state,
                            "to_state": new_state,
                            "nation_a": parts[0],
                            "nation_b": parts[1],
                        })

                        # R80: Dispatch event + notification for auto-downgrade
                        from backend.game_logic.dispatch import queue_dispatch_event
                        queue_dispatch_event(world, "diplomatic_auto_downgrade", {
                            "nation_a": parts[0],
                            "nation_b": parts[1],
                            "from_state": state,
                            "to_state": new_state,
                        }, "always")

                        from backend.notifications import (
                            create_notification, NotificationPriority, DIPLO_AUTO_DOWNGRADE,
                        )
                        world.notifications.add(create_notification(
                            DIPLO_AUTO_DOWNGRADE,
                            NotificationPriority.NORMAL,
                            "Relations Deteriorated",
                            f"{parts[0]}-{parts[1]}: {_STATE_DISPLAY_NAMES.get(state, state)} → {_STATE_DISPLAY_NAMES.get(new_state, new_state)}.",
                            int(world.current_turn),
                        ))
        else:
            # Above threshold or gap < 30 — reset counter
            turns_below.pop(diplo_key, None)

    world.turns_below_threshold = turns_below
    return events


# ═══════════════════════════════════════════════════════
# BATTLE RECORDING
# ═══════════════════════════════════════════════════════

def record_battle(world, attacker_nation: str, defender_nation: str,
                  winner_nation: str, attacker_casualties: int,
                  defender_casualties: int, location: str = "",
                  *,
                  war_id: Optional[str] = None,
                  attacker_participants: Optional[List[str]] = None,
                  defender_participants: Optional[List[str]] = None,
                  nation_theater_strength: Optional[Mapping[str, int]] = None) -> None:
    """Record a battle result for war score calculation.

    Also checks for decisive battle (casualty ratio > 2:1 AND total > 10,000).
    Max 2 decisive bonuses per war.

    Imperial Settlement B2: settlement contribution accrual MUST run before the
    1000-casualty war-score early return (spec §9.4 line 713: sub-1000 battles
    still accrue settlement contribution). The ordering is pinned by tests in
    `tests/test_war_contribution_scores.py` — moving the accrual call below
    the gate breaks the ordering guard.

    Theater fields (`war_id`, `attacker_participants`, `defender_participants`,
    `nation_theater_strength`) are forwarded into `accrue_battle_contribution()`
    when the caller supplies them. Callers without theater context (or with
    legacy single-attacker / single-defender shape) leave them ``None`` and
    the legacy adapter (spec §9.6) fills the theater shape with single-nation
    participation.
    """
    if not world.is_at_war(attacker_nation, defender_nation):
        return  # Only record battles between nations at war

    diplo_key = world._make_diplo_key(attacker_nation, defender_nation)

    # Ensure data structures exist
    if not hasattr(world, 'battle_records'):
        world.battle_records = {}
    if not hasattr(world, 'decisive_battles'):
        world.decisive_battles = {}

    if diplo_key not in world.battle_records:
        world.battle_records[diplo_key] = []
    if diplo_key not in world.decisive_battles:
        world.decisive_battles[diplo_key] = []

    # Imperial Settlement B2: accrue settlement contribution BEFORE the
    # 1000-casualty war-score gate. Callers with theater context (post-B2
    # emitter wiring) pass `attacker_participants` / `defender_participants` /
    # `nation_theater_strength` derived from one-hop adjacency. Legacy callers
    # leave them None and the §9.6 adapter fills single-nation defaults.
    from backend.game_logic.war_contribution import accrue_battle_contribution
    accrue_battle_contribution(
        world,
        attacker_nation=attacker_nation,
        defender_nation=defender_nation,
        winner_nation=winner_nation,
        attacker_casualties=int(attacker_casualties),
        defender_casualties=int(defender_casualties),
        location=location,
        war_id=war_id,
        attacker_participants=attacker_participants,
        defender_participants=defender_participants,
        nation_theater_strength=nation_theater_strength,
        turn=getattr(world, "current_turn", None),
    )

    # R9: Only battles with >= 1000 total casualties count for war score
    total_casualties = attacker_casualties + defender_casualties
    if total_casualties < 1000:
        return

    record = {
        "turn": world.current_turn,
        "winner": winner_nation,
        "attacker": attacker_nation,
        "defender": defender_nation,
        "attacker_casualties": int(attacker_casualties),
        "defender_casualties": int(defender_casualties),
        "location": location,
    }
    world.battle_records[diplo_key].append(record)

    # Check for decisive battle (total_casualties already computed above)
    if total_casualties > 10000:
        if attacker_casualties > 0 and defender_casualties > 0:
            ratio = max(attacker_casualties, defender_casualties) / min(attacker_casualties, defender_casualties)
            if ratio > 2.0:
                # Max 2 decisive bonuses per war
                if len(world.decisive_battles[diplo_key]) < 2:
                    world.decisive_battles[diplo_key].append({
                        "turn": world.current_turn,
                        "winner": winner_nation,
                        "total_casualties": int(total_casualties),
                        "ratio": round(ratio, 1),
                    })


# ═══════════════════════════════════════════════════════
# MOVEMENT VALIDATION HELPERS
# ═══════════════════════════════════════════════════════

def can_enter_territory(world, marshal_nation: str, region_controller: str) -> bool:
    """Check if a nation's marshal can enter territory controlled by another nation.

    Returns True if movement is allowed.
    """
    if not region_controller:
        return True  # Unclaimed territory
    if marshal_nation == region_controller:
        return True  # Own territory

    state = world.get_diplomatic_state(marshal_nation, region_controller)

    # WAR — can enter (but must attack if enemies present)
    if state == "WAR":
        return True

    # OPEN_BORDERS and above — can enter
    if state in OPEN_MOVEMENT_STATES:
        return True

    # PEACE, ARMISTICE — cannot enter
    return False


# ═══════════════════════════════════════════════════════
# ADVANCE_TURN DIPLOMATIC PROCESSING (§7f)
# ═══════════════════════════════════════════════════════

def process_diplomacy_turn(world) -> List[Dict]:
    """Process diplomatic events during advance_turn.

    Implements §7f processing order (items this session covers):
    1. DP regeneration
    4. War score recalculation
    5-7. Vassal defection, loyalty, and rebellion checks
    8. Armistice expiration (minimum 5 turns)
    9. Cooldown decrements
    10. Trade income (handled separately in income phase)
    13. Automatic downgrade check

    Returns list of diplomatic events for Morning Dispatch.
    """
    events = []

    # ── 1. DP regeneration ──
    _process_dp_regen(world)

    # ── 1b. R90: Auto-cancel mission if target nation eliminated ──
    mission_cancel_events = _check_mission_target_eliminated(world)
    events.extend(mission_cancel_events)

    # ── 2. Mission DP deduction (Session 3) ──
    mission_events = _process_mission_dp(world)
    events.extend(mission_events)

    # ── 3. Mission effects (Session 3) ──
    effect_events = _process_mission_effects(world)
    events.extend(effect_events)

    # ── 4. War score battle-record pruning / battle-only decay prep ──
    apply_war_score_decay(world, recalculate=False)

    # ── 4a. War objective ticking (WPS-A) ──
    ticking_events = accumulate_war_objective_ticking(world)
    for te in ticking_events:
        world.log_event(te)
    events.extend(ticking_events)

    # Recalculate once after ticking so stored war_scores include the 5th component.
    recalculate_war_scores(world)

    # ── 4b. Cleanup old concluded war objectives ──
    _cleanup_old_war_objectives(world)

    # ── 4c. Relation decay (R4a) ──
    _process_relation_decay(world)

    # 5-7: Vassal processing must run after war score/ticking and before
    # armistice expiration or diplomatic normalization. This lets war outcomes
    # shake vassal loyalty before an expiring ceasefire can settle the pair.
    if getattr(world, "vassals", None):
        from backend.game_logic.vassal import (
            check_defection_cascade,
            check_vassal_rebellion,
            process_vassal_loyalty,
        )
        events.extend(check_defection_cascade(world))
        events.extend(process_vassal_loyalty(world))
        events.extend(check_vassal_rebellion(world))

    # ── 7b. Per-turn staying-power accrual (Slice B3, spec §9.2 line 612) ──
    # Walks every active war_instance once and adds +5 raw points per
    # active episode per turn, capped at 10 qualifying turns per episode.
    # Placed BEFORE the armistice-expiration step so episodes that close on
    # this turn (ARMISTICE → PEACE) still capture the turn's staying power
    # under the inclusive `event.turn <= exited_turn` boundary (spec §9.5).
    from backend.game_logic.war_contribution import accrue_staying_power_all_wars
    accrue_staying_power_all_wars(
        world, current_turn=int(getattr(world, "current_turn", 0) or 0),
    )

    # ── 8. Armistice expiration ──
    armistice_events = _process_armistice_expiration(world)
    events.extend(armistice_events)

    # ── 9. Cooldown decrements ──
    _decrement_cooldowns(world)
    from backend.game_logic.vassal import decrement_vassal_cooldowns
    decrement_vassal_cooldowns(world)

    # 9a-9d: Coalition processing (war exhaustion, threat accumulation/decay, coalition check) — implemented in coalition.py, wired in advance_turn()

    # 10. Trade income — handled in process_trade_income() called from advance_turn income phase

    # 11-12: Treaty obligations + Continental System — implemented in diplomacy.py (process_treaty_obligations, apply_continental_system), wired in advance_turn()

    # ── 12a. Forced-alliance relation drift (WPS-C §9.5) ──
    forced_drift_events = _process_forced_alliance_drift(world)
    events.extend(forced_drift_events)

    # ── 13. Automatic downgrade check ──
    downgrade_events = check_auto_downgrade(world)
    events.extend(downgrade_events)

    # ── 13a. War bargain lifecycle (WB-B §8.8/§8.9) ──
    bargain_events = process_bargain_lifecycle(world)
    events.extend(bargain_events)

    # ── 14. Diplomatic reliability (R34) ──
    _process_diplomatic_reliability(world)

    # ── Nation authority changes ──
    _process_nation_authority(world)

    return events


def _is_nation_eliminated(world, nation: str) -> bool:
    """R81: Check if a nation is eliminated (0 regions).

    Marshals are guaranteed removed by _eliminate_nation(), so region check suffices.

    Imperial Settlement A1: read through the per-turn `get_nation_regions(...)`
    cache instead of scanning `world.regions.values()` raw. `get_active_nations()`
    is the foundational caller of this helper and is itself part of the
    settlement substrate's caller graph; per-turn cache reuse keeps elimination
    detection off hot per-turn region scans at full-Europe scale.
    """
    return not world.get_nation_regions(nation)


def _process_dp_regen(world) -> None:
    """Regenerate DP for all nations. DP does NOT accumulate — reset each turn."""
    from backend.models.region import NATION_CAPITALS
    diplomats = getattr(world, 'diplomats', {})
    nation_auth = getattr(world, 'nation_authority', {})

    all_nations = [world.player_nation] + list(getattr(world, 'enemy_nations', []))
    for nation in all_nations:
        # R81: Skip eliminated nations (0 regions + 0 marshals)
        if nation != world.player_nation and _is_nation_eliminated(world, nation):
            continue
        diplomat = diplomats.get(nation)
        if nation == world.player_nation:
            authority = world.authority_tracker.authority if hasattr(world, 'authority_tracker') else 60
        else:
            authority = nation_auth.get(nation, 60)

        capital = NATION_CAPITALS.get(nation)
        controls_capital = False
        if capital and capital in world.regions:
            controls_capital = world.regions[capital].controller == nation

        dp = calculate_dp(diplomat, authority, controls_capital)

        if nation == world.player_nation:
            world.diplomatic_points = int(dp)
            # S1: Queue DP breakdown for morning dispatch
            from backend.game_logic.dispatch import queue_dispatch_event
            parts = ["base 3"]
            if diplomat and diplomat.skill >= 8:
                parts.append("+1 skill")
            if authority >= 60:
                parts.append("+1 authority")
            elif authority < 30:
                parts.append("-1 low authority")
            if not controls_capital:
                parts.append("-1 no capital")
            breakdown_str = ", ".join(parts)
            queue_dispatch_event(world, "diplomatic_dp_regen",
                                {"dp": int(dp), "breakdown": breakdown_str}, "always")
        else:
            # Store AI DP for AI diplomacy consumption
            if not hasattr(world, 'nation_dp'):
                world.nation_dp = {}
            world.nation_dp[nation] = int(dp)


def calculate_trade_income(world) -> Dict[str, int]:
    """Calculate trade income from diplomatic states (read-only, no side effects).

    R6: Diminishing returns — partners sorted by state level (best first),
    rates [1.0, 0.75, 0.50, 0.25]. 5th+ partners get 0.25.

    Returns dict of {nation: trade_income}.
    """
    _DIMINISHING_RATES = [1.0, 0.75, 0.50, 0.25]
    _STATE_PRIORITY = {"ALLIANCE": 0, "DEFENSIVE_ALLIANCE": 1, "NON_AGGRESSION": 2,
                       "OPEN_BORDERS": 3, "PEACE": 4}

    # Collect trade partners per nation: {nation: [(partner, trade_amount, state)]}
    partners_by_nation: Dict[str, list] = {}
    for pair_key, state in world.diplomatic_states.items():
        trade = TRADE_INCOME.get(state, 0)
        if trade > 0:
            parts = pair_key.split("|")
            if len(parts) == 2:
                nation_a, nation_b = parts
                # Skip vassals — tribute replaces trade
                if nation_a in getattr(world, 'vassals', {}) or nation_b in getattr(world, 'vassals', {}):
                    continue
                partners_by_nation.setdefault(nation_a, []).append((nation_b, trade, state))
                partners_by_nation.setdefault(nation_b, []).append((nation_a, trade, state))

    # Apply diminishing returns per nation
    trade_by_nation = {}
    for nation, partners in partners_by_nation.items():
        # Sort by state priority (best first), tiebreak alphabetical
        partners.sort(key=lambda p: (_STATE_PRIORITY.get(p[2], 5), p[0]))
        total = 0
        for i, (partner, trade_amount, state) in enumerate(partners):
            rate = _DIMINISHING_RATES[min(i, len(_DIMINISHING_RATES) - 1)]
            total += int(trade_amount * rate)
        trade_by_nation[nation] = total

    return trade_by_nation


def process_trade_income(world) -> Dict[str, int]:
    """Calculate and apply trade income from diplomatic states.

    Returns dict of {nation: trade_income} for display.
    """
    trade_by_nation = calculate_trade_income(world)

    # Apply to nation_gold
    for nation, income in trade_by_nation.items():
        if nation in world.nation_gold:
            world.nation_gold[nation] += int(income)

    return trade_by_nation


def _process_armistice_expiration(world) -> List[Dict]:
    """Handle armistice expirations (R5a).

    Tracks turns in ARMISTICE state. After 5 turns:
    - If relations >= -60: transition to PEACE, call cleanup_war_end
    - If relations < -60: transition back to WAR

    Returns list of dispatch events.
    """
    events = []
    armistice_turns = getattr(world, 'armistice_turns', {})

    for diplo_key, state in list(world.diplomatic_states.items()):
        if state != "ARMISTICE":
            # Not in armistice — remove tracking if present
            armistice_turns.pop(diplo_key, None)
            continue

        # Increment turn counter
        armistice_turns[diplo_key] = armistice_turns.get(diplo_key, 0) + 1
        turns = armistice_turns[diplo_key]

        if turns < 5:
            continue

        # Armistice expired — check relations to determine outcome
        parts = diplo_key.split("|")
        if len(parts) != 2:
            continue
        nation_a, nation_b = parts
        relation = world.nation_relations.get(diplo_key, 0)

        if relation >= -60:
            # Transition to PEACE (R2: setter handles armistice cleanup).
            # Slice A2 §7.3: ARMISTICE -> PEACE moves the pair to
            # resolved_diplo_keys with pair_status='resolved'.
            resolve_pair_to_resolved(world, diplo_key)
            set_diplomatic_state(world, nation_a, nation_b, "PEACE", "armistice_expired_peace")
            cleanup_war_end(world, diplo_key)
            events.append({
                "type": "armistice_expired_peace",
                "nations": [nation_a, nation_b],
                "message": f"The armistice between {nation_a} and {nation_b} has concluded. Peace declared.",
            })
            # Fix 12: Notification + dispatch for armistice expiration (peace)
            from backend.notifications import create_notification, NotificationPriority
            world.notifications.add(create_notification(
                "armistice_expired", NotificationPriority.HIGH,
                "Armistice Concluded",
                f"The armistice with {nation_b if nation_a == world.player_nation else nation_a} has concluded. Peace declared.",
                int(world.current_turn),
            ))
            from backend.game_logic.dispatch import queue_dispatch_event
            queue_dispatch_event(world, "diplomatic_armistice_expired_peace",
                                {"nation_a": nation_a, "nation_b": nation_b}, "always")
        else:
            # Relations too hostile — back to WAR (R2: setter handles war_start + armistice cleanup + treaty).
            # Slice A2 §7.3: ARMISTICE -> WAR reuses the same war_id; if no
            # war_instance currently owns the pair (e.g. from a save where
            # the original war ended before A1 landed), allocate one so the
            # invariant remains satisfiable.
            war_instance_result = ensure_war_instance_for_pair(
                world,
                nation_a,
                nation_b,
                entry_path="armistice_expired_war",
                reason="armistice collapse",
            )
            if not war_instance_result.get("ok"):
                blocked = {
                    "type": "armistice_expired_war_blocked",
                    "nations": [nation_a, nation_b],
                    "error": war_instance_result.get("error"),
                    "details": war_instance_result.get("details", {}),
                    "message": (
                        f"The armistice between {nation_a} and {nation_b} "
                        f"could not collapse: {war_instance_result.get('error')}."
                    ),
                }
                events.append(blocked)
                if hasattr(world, "log_event"):
                    world.log_event(blocked)
                continue
            set_diplomatic_state(world, nation_a, nation_b, "WAR", "armistice_expired_war")
            events.append({
                "type": "armistice_expired_war",
                "nations": [nation_a, nation_b],
                "message": f"The armistice between {nation_a} and {nation_b} has collapsed. War resumes.",
            })
            # Fix 12: Notification + dispatch for armistice expiration (war)
            from backend.notifications import create_notification, NotificationPriority
            world.notifications.add(create_notification(
                "armistice_expired", NotificationPriority.CRITICAL,
                "Armistice Collapsed",
                f"The armistice with {nation_b if nation_a == world.player_nation else nation_a} has collapsed. War resumes!",
                int(world.current_turn),
            ))
            from backend.game_logic.dispatch import queue_dispatch_event
            queue_dispatch_event(world, "diplomatic_armistice_expired_war",
                                {"nation_a": nation_a, "nation_b": nation_b}, "always")

        # Clear tracking
        armistice_turns.pop(diplo_key, None)

    world.armistice_turns = armistice_turns
    return events


def _decrement_cooldowns(world) -> None:
    """Decrement armistice cooldowns by 1 per turn. Remove expired ones."""
    cooldowns = getattr(world, 'armistice_cooldowns', {})
    expired = []
    for key in cooldowns:
        cooldowns[key] -= 1
        if cooldowns[key] <= 0:
            expired.append(key)
    for key in expired:
        del cooldowns[key]
    world.armistice_cooldowns = cooldowns


def _process_mission_dp(world) -> List[Dict]:
    """Deduct DP for active diplomatic mission. Pause if insufficient."""
    events = []
    mission = getattr(world, 'active_diplomatic_mission', None)
    if not mission or mission.get("completed"):
        return events

    from backend.game_logic.diplomatic_dialogue import MISSION_DP_COSTS
    cost = MISSION_DP_COSTS.get(mission["type"], 1)

    if mission.get("paused"):
        # Already paused — check if we can resume
        if world.diplomatic_points >= cost:
            # Resume
            mission["paused"] = False
            mission["paused_turns"] = 0
            world.diplomatic_points -= cost
            mission["turns_active"] = mission.get("turns_active", 0) + 1
        else:
            # Still can't afford — increment paused turns
            mission["paused_turns"] = mission.get("paused_turns", 0) + 1
    elif world.diplomatic_points >= cost:
        world.diplomatic_points -= cost
        mission["turns_active"] = mission.get("turns_active", 0) + 1
        mission["paused_turns"] = 0
    else:
        mission["paused"] = True
        mission["paused_turns"] = mission.get("paused_turns", 0) + 1
        events.append({
            "type": "diplomatic_mission_paused",
            "target": mission.get("target", ""),
            "message": "Talleyrand's diplomatic efforts curtailed — insufficient resources.",
        })
        # Dispatch event (Session 8D)
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "diplomatic_mission_paused",
                            {"nation": mission.get("target", "")}, "player_mission")

    # Auto-cancel after 3+ consecutive paused turns
    paused_turns = mission.get("paused_turns", 0)
    if paused_turns >= 3:
        target = mission.get("target", "unknown")
        world.active_diplomatic_mission = None
        if getattr(world, 'talleyrand_state', '') == "ON_MISSION":
            world.talleyrand_state = "IDLE"
        events.append({
            "type": "diplomatic_mission_cancelled",
            "target": target,
            "message": f"Talleyrand's mission to {target} has collapsed after prolonged inactivity.",
        })
        # Dispatch event (Session 8D)
        from backend.game_logic.dispatch import queue_dispatch_event as _qde
        _qde(world, "diplomatic_mission_cancelled",
             {"nation": target}, "player_mission")

    return events


def _process_mission_effects(world) -> List[Dict]:
    """Apply per-turn mission effects."""
    events = []
    mission = getattr(world, 'active_diplomatic_mission', None)
    if not mission or mission.get("paused") or mission.get("completed"):
        return events

    from backend.game_logic.diplomatic_dialogue import MISSION_EFFECTS
    mission_type = mission.get("type", "")
    effects = MISSION_EFFECTS.get(mission_type, {})
    target = mission.get("target", "")

    if not target:
        return events

    # Get Talleyrand skill for bonus calculation
    player_nation = getattr(world, 'player_nation', 'France')
    diplomats = getattr(world, 'diplomats', {})
    talleyrand = diplomats.get(player_nation)  # Player's diplomat
    skill = talleyrand.skill if talleyrand else 5

    # Skill multiplier: 10 → 1.5x, 4-6 → 0.75x, else → 1.0x
    if skill >= 10:
        multiplier = 1.5
    elif 4 <= skill <= 6:
        multiplier = 0.75
    else:
        multiplier = 1.0

    # Apply relation change
    relation_change = effects.get("relation_change", 0)
    if relation_change:
        scaled = int(round(relation_change * multiplier))
        world.modify_nation_relation(player_nation, target, scaled)
        # Dispatch event (Session 8D)
        diplo_key = world._make_diplo_key(player_nation, target)
        current_relation = world.nation_relations.get(diplo_key, 0)
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "diplomatic_mission_progress",
                            {"nation": target, "value": int(current_relation)},
                            "player_mission")

    # GATHER_INTEL: auto-complete after duration turns
    duration = effects.get("duration")
    if duration and mission.get("turns_active", 0) >= duration:
        mission["completed"] = True
        world.talleyrand_state = "IDLE"
        events.append({
            "type": "diplomatic_mission_completed",
            "target": target,
            "mission_type": mission_type,
            "message": f"Talleyrand has completed his intelligence gathering on {target}.",
        })
        # R92: Dispatch event for mission completion
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "diplomatic_mission_completed",
                            {"nation": target}, "player_mission")

        # DLF-5: Grant FULL visibility on target nation's regions for 5 turns
        if mission_type == "GATHER_INTEL":
            grant_expiry = int(world.current_turn) + 5
            target_regions = [
                r.name for r in world.regions.values()
                if r.controller == target
            ]
            for region_name in target_regions:
                world.update_intel_from_scout(region_name, int(world.current_turn))
                world.intel_grants[region_name] = grant_expiry
            events[-1]["regions_revealed"] = len(target_regions)
            events[-1]["message"] = (
                f"Talleyrand has completed his intelligence gathering on {target}. "
                f"{len(target_regions)} region{'s' if len(target_regions) != 1 else ''} revealed for 5 turns."
            )

    # DLF-4: COURT_NATION blowback — 20% chance of -3 relation (fixed, not skill-scaled)
    undermine_chance = effects.get("undermine_chance", 0)
    if undermine_chance > 0:
        if random.random() < undermine_chance:
            undermine_amount = effects.get("undermine_amount", 0)
            world.modify_nation_relation(player_nation, target, undermine_amount)
            diplo_key_bl = world._make_diplo_key(player_nation, target)
            current_relation_bl = int(world.nation_relations.get(diplo_key_bl, 0) or 0)
            events.append({
                "type": "diplomatic_mission_blowback",
                "target": target,
                "mission_type": mission_type,
                "delta": int(undermine_amount),
                "message": f"Diplomatic blowback! {target} discovered our scheming. ({int(undermine_amount)} relation)",
            })
            from backend.game_logic.dispatch import queue_dispatch_event
            queue_dispatch_event(world, "diplomatic_mission_blowback",
                                {"nation": target, "delta": int(undermine_amount),
                                 "value": current_relation_bl},
                                "player_mission")

    # DLF-2: UNDERMINE_ALLIANCE per-turn effect
    if mission_type == "UNDERMINE_ALLIANCE":
        target_ally = mission.get("target_ally", "")
        if target_ally:
            pair_change = effects.get("target_pair_relation_change", 0)
            if pair_change:
                scaled_pair = int(round(pair_change * multiplier))
                world.modify_nation_relation(target, target_ally, scaled_pair)
                from backend.game_logic.dispatch import queue_dispatch_event
                queue_dispatch_event(world, "diplomatic_mission_progress",
                                    {"nation": target, "ally": target_ally,
                                     "delta": int(scaled_pair)},
                                    "player_mission")
                # Auto-cancel if alliance broke
                if not world.are_allies(target, target_ally):
                    mission["completed"] = True
                    world.talleyrand_state = "IDLE"
                    events.append({
                        "type": "diplomatic_mission_completed",
                        "target": target,
                        "mission_type": mission_type,
                        "message": f"The alliance between {target} and {target_ally} has collapsed! Mission complete.",
                    })
                    queue_dispatch_event(world, "diplomatic_mission_completed",
                                        {"nation": target, "ally": target_ally},
                                        "player_mission")

    return events


def _check_mission_target_eliminated(world) -> List[Dict]:
    """R90: Auto-cancel active diplomatic mission if target nation is eliminated.

    A nation is eliminated when it has 0 regions AND 0 living marshals.
    Called early in process_diplomacy_turn before mission DP deduction.

    Returns list of events (0 or 1 cancellation event).
    """
    events = []
    mission = getattr(world, 'active_diplomatic_mission', None)
    if not mission or mission.get("completed"):
        return events

    target = mission.get("target", "")
    if not target:
        return events

    # Check if target nation has 0 regions
    has_regions = any(
        getattr(r, 'controller', '') == target
        for r in world.regions.values()
    )
    # Check if target nation has 0 living marshals
    has_marshals = any(
        m.nation == target and m.strength > 0
        for m in world.marshals.values()
    )

    if not has_regions and not has_marshals:
        # Nation eliminated — cancel mission
        world.active_diplomatic_mission = None
        if getattr(world, 'talleyrand_state', '') == "ON_MISSION":
            world.talleyrand_state = "IDLE"
        events.append({
            "type": "diplomatic_mission_cancelled",
            "target": target,
            "reason": "nation_eliminated",
            "message": f"Talleyrand's mission to {target} cancelled — the nation no longer exists.",
        })
        world.log_event({
            "type": "diplomatic_mission_cancelled_eliminated",
            "target": target,
        })

    return events


def break_treaty(
    pair_key: str,
    breaker_nation: str,
    world,
    origin_episode_id: str = None,
) -> Dict:
    """Break an active treaty. Costs 1 DP.

    Returns:
        {"success": bool, "message": str, "relation_changes": list}
    """
    active_treaties = getattr(world, 'active_treaties', {})
    treaty = active_treaties.get(pair_key)
    if not treaty:
        return {"success": False, "message": "No active treaty to break."}

    # R101: Validate breaker is party to the treaty
    treaty_nations = treaty.get("nations", [])
    if treaty_nations and breaker_nation not in treaty_nations:
        return {"success": False, "message": f"{breaker_nation} is not a party to this treaty."}

    # Cost: 1 DP — use player DP for player, nation_dp for AI
    player_nation = getattr(world, 'player_nation', 'France')
    if breaker_nation == player_nation:
        if world.diplomatic_points < 1:
            return {"success": False, "message": "Insufficient DP to break treaty (costs 1 DP)."}
        world.diplomatic_points -= 1
    else:
        nation_dp = getattr(world, 'nation_dp', {})
        if nation_dp.get(breaker_nation, 0) < 1:
            return {"success": False, "message": f"{breaker_nation} has insufficient DP to break treaty."}
        nation_dp[breaker_nation] = nation_dp.get(breaker_nation, 0) - 1
        world.nation_dp = nation_dp

    treaty_type = treaty.get("type", "peace")
    nations = treaty.get("nations", [])
    other_nation = [n for n in nations if n != breaker_nation]
    other = other_nation[0] if other_nation else ""
    if not other:
        parts = pair_key.split("|")
        if len(parts) == 2:
            other = parts[1] if parts[0] == breaker_nation else parts[0]
    breach_preview = get_treaty_breach_preview(
        world,
        breaker_nation,
        other,
        treaty=treaty,
        end_reason_action="manual_break",
        fault_nation=breaker_nation,
        episode_id=origin_episode_id,
    )

    # Relation penalties
    relation_changes = []

    # Target: -30 (or -40 for alliance/defensive_alliance)
    penalty = -40 if treaty_type in ("alliance", "defensive_alliance") else -30
    world.modify_nation_relation(breaker_nation, other, penalty)
    relation_changes.append({"nations": (breaker_nation, other), "delta": penalty})

    # ALL nations: -10
    all_nations = world.get_active_nations()  # DLF-11
    for nation in all_nations:
        if nation != breaker_nation and nation != other:
            world.modify_nation_relation(breaker_nation, nation, -10)
            relation_changes.append({"nations": (breaker_nation, nation), "delta": -10})

    # Deep audit fix 9: Only add threat when PLAYER breaks treaty (threat tracks France's aggression)
    if breaker_nation == world.player_nation:
        from backend.game_logic.coalition import add_threat
        threat_amount = 25 if treaty_type in ("alliance", "defensive_alliance") else 15
        add_threat(world, threat_amount, f"broke_{treaty_type}")

    # Post-break state: one level below broken treaty (E11)
    # IMPORTANT: Must include ALL diplomatic states. If you add a new
    # state to the diplomacy chain, add it here too. (Audit fix L-4)
    post_break_map = {
        "ALLIANCE": "NON_AGGRESSION",
        "DEFENSIVE_ALLIANCE": "OPEN_BORDERS",
        "NON_AGGRESSION": "PEACE",
        "OPEN_BORDERS": "PEACE",
        "PEACE": "PEACE",
        "VASSAL": "NON_AGGRESSION",  # Audit fix L-4
        "WAR": "PEACE",  # Deep audit fix 3
        "ARMISTICE": "PEACE",  # Deep audit fix 3
    }
    current_state = world.diplomatic_states.get(pair_key, "PEACE")
    new_state = post_break_map.get(current_state, "PEACE")
    set_diplomatic_state(world, breaker_nation, other, new_state, "treaty_break")

    # Deep audit fix 3: Clean up war data if breaking from WAR/ARMISTICE
    if current_state in ("WAR", "ARMISTICE"):
        cleanup_war_end(world, pair_key)

    # Remove treaty
    del active_treaties[pair_key]

    # Deep audit fix 12: Void any proposal_in_transit for this nation pair
    pit = getattr(world, 'proposal_in_transit', None)
    if pit:
        pit_target = pit.get("target", "")
        pit_proposer = pit.get("proposal", {}).get("proposer_nation", "")
        if pit_target and pit_proposer:
            pit_key = world._make_diplo_key(pit_proposer, pit_target)
            if pit_key == pair_key:
                world.proposal_in_transit = None

    _record_treaty_breach(
        world,
        breach_preview,
        new_state=new_state,
        trigger_context={
            "breaker": breaker_nation,
            "other": other,
            "treaty_type": treaty_type,
            "mode": "manual_break",
        },
    )
    bargain_breach_events = detect_bargain_breach_on_treaty_change(
        world,
        breaker_nation,
        other,
        new_state,
        episode_id=breach_preview.get("episode_id"),
    )

    return {
        "success": True,
        "message": (
            f"{breaker_nation} has broken the {breach_preview['treaty_type_display']} "
            f"with {other} {breach_preview['reason_phrase']}! Relations plummet."
        ),
        "new_state": new_state,
        "relation_changes": relation_changes,
        "treaty_broken_event": treaty_type,  # R23: signal for trust reactions
        "bargain_breach_events": bargain_breach_events,
    }


def _process_nation_authority(world) -> None:
    """Update AI nation authority based on events.

    Authority changes:
    - Losing battle: -3
    - Losing region: -5
    - Breaking treaty: -10
    - Winning battle: +2
    - Favorable treaty: +5

    Actual tracking of these events is done at the point they happen
    (combat resolution, territory changes, etc.) via modify_nation_authority().
    This function is a placeholder for any per-turn authority processing.
    """
    pass  # Authority changes happen at event time, not during turn processing


def _process_relation_decay(world) -> None:
    """R4a: Relations drift toward +-10 band each turn.

    Skip pairs that are: vassals, at WAR, in ARMISTICE, or targeted by COURT_NATION mission.
    Above +10: -1/turn. Below -10: +1/turn.
    """
    all_nations = world.get_active_nations()  # DLF-11

    # Check for active COURT_NATION mission target (player-side only)
    court_target = None
    mission = getattr(world, 'active_diplomatic_mission', None)
    if mission and mission.get("type") == "COURT_NATION":
        court_target = mission.get("target")

    vassals = getattr(world, 'vassals', {})

    for i, nation_a in enumerate(all_nations):
        for nation_b in all_nations[i + 1:]:
            # Deep audit fix 15: Skip vassal-lord pairs only, not vassal-third-party
            if nation_a in vassals and vassals[nation_a].get("lord") == nation_b:
                continue
            if nation_b in vassals and vassals[nation_b].get("lord") == nation_a:
                continue

            diplo_key = world._make_diplo_key(nation_a, nation_b)
            state = world.diplomatic_states.get(diplo_key, "PEACE")

            # Skip WAR and ARMISTICE pairs
            if state in ("WAR", "ARMISTICE"):
                continue

            # Skip if COURT_NATION targets either nation in the pair
            if court_target and court_target in (nation_a, nation_b):
                continue

            relation = world.nation_relations.get(diplo_key, 0)
            if relation > 10:
                world.modify_nation_relation(nation_a, nation_b, -1)
            elif relation < -10:
                world.modify_nation_relation(nation_a, nation_b, 1)


# ═══════════════════════════════════════════════════════
# AP/TURN CLAUSE VALIDATION (Phase 8 Session 5)
# ═══════════════════════════════════════════════════════

def validate_ap_clause(world, target: str) -> bool:
    """Validate that AP/turn demand is allowed. Requires war_score > 80."""
    player = getattr(world, 'player_nation', 'France')
    war_score = get_war_score_for(world, player, target)
    return war_score > 80


# ═══════════════════════════════════════════════════════
# CONTINENTAL SYSTEM (Phase 8 Session 5 §5d)
# ═══════════════════════════════════════════════════════

def apply_continental_system(world) -> None:
    """
    Apply Continental System trade penalties during income phase.

    Members: -75g/turn trade income cap with Britain.
    Total cap: 200g/turn across all members.
    PUPPET/SATELLITE vassals auto-join if lord runs system.
    """
    members = getattr(world, 'continental_system_members', [])
    if not members:
        return

    lord = getattr(world, 'player_nation', 'France')

    # Auto-join PUPPET/SATELLITE vassals
    from backend.game_logic.vassal import AUTONOMY_PUPPET, AUTONOMY_SATELLITE
    for vassal_name, state in world.vassals.items():
        if state["lord"] == lord:
            autonomy = state.get("autonomy", AUTONOMY_SATELLITE)
            if autonomy in (AUTONOMY_PUPPET, AUTONOMY_SATELLITE):
                if vassal_name not in members:
                    members.append(vassal_name)
                    # 6A-8: Queue dispatch event for newly auto-joined vassals
                    from backend.game_logic.dispatch import queue_dispatch_event
                    queue_dispatch_event(world, "diplomatic_continental_system",
                                         {"nation": vassal_name, "action": "joined"}, "always")

    # Remove AUTONOMOUS vassals from CS (they are independent)
    from backend.game_logic.vassal import AUTONOMY_AUTONOMOUS
    for vassal_name, state in world.vassals.items():
        if state["lord"] == lord:
            autonomy = state.get("autonomy", AUTONOMY_SATELLITE)
            if autonomy == AUTONOMY_AUTONOMOUS and vassal_name in members:
                members.remove(vassal_name)

    # Cap trade income between Britain and members
    total_blocked = 0
    max_total_cap = 200
    for member in members:
        if total_blocked >= max_total_cap:
            break
        # Check trade income between member and Britain
        member_state = world.get_diplomatic_state(member, "Britain")
        trade = TRADE_INCOME.get(member_state, 0)
        if trade > 0:
            blocked = min(75, trade, max_total_cap - total_blocked)
            if member in world.nation_gold:
                world.nation_gold[member] = max(0, world.nation_gold[member] - int(blocked))
            if "Britain" in world.nation_gold:
                world.nation_gold["Britain"] = max(0, world.nation_gold["Britain"] - int(blocked))
            total_blocked += blocked

    world.continental_system_members = members


# ═══════════════════════════════════════════════════════
# DIPLOMATIC RELIABILITY (R34)
# ═══════════════════════════════════════════════════════

def _process_diplomatic_reliability(world) -> None:
    """R34: Increase diplomatic reliability for nations honoring treaties for 10+ turns.

    Each active treaty that has been honored for 10+ turns grants +5 reliability
    to each nation in the treaty, capped at 100.
    """
    active_treaties = getattr(world, 'active_treaties', {})
    reliability = getattr(world, 'diplomatic_reliability', {})

    for pair_key, treaty in active_treaties.items():
        turn_signed = treaty.get("turn_signed", 0)
        turns_honored = world.current_turn - turn_signed

        if turns_honored >= 10 and turns_honored % 10 == 0:
            # Award reliability every 10 turns of honoring
            nations = treaty.get("nations", [])
            for nation in nations:
                current = reliability.get(nation, 0)
                reliability[nation] = min(100, current + 5)

    world.diplomatic_reliability = reliability
    _process_betrayal_decay(world)
    _process_oathbreaker_decay(world)


# ═══════════════════════════════════════════════════════
# DIPLOMACY BUTTON — PREVIEW HELPERS (Phase 5)
# ═══════════════════════════════════════════════════════

def get_likelihood_descriptor(score: int) -> str:
    """Map acceptance score to a thematic likelihood word (§3a).

    Single source of truth for all likelihood displays:
    wizard, R118 preview, any future acceptance display.
    """
    if score >= 70:
        return "Almost Certain"
    elif score >= 50:
        return "Favorable"
    elif score >= 40:
        # G4F-13: the closer the score sits to the sign bar, the cheaper a
        # counter is to construct — the 40s read "likely", the 30s "may".
        # The exact promise lives on the proposal preview itself
        # (counter_constructible), which dry-runs the real generator.
        return "Uncertain — a counter is likely"
    elif score >= 30:
        return "Doubtful — may counter"
    elif score >= 15:
        return "Unlikely"
    else:
        return "Hopeless"


def get_relation_descriptor(relation: int) -> str:
    """Map relation score to descriptor word (§2a)."""
    if relation >= 60:
        return "Loyal"
    elif relation >= 30:
        return "Friendly"
    elif relation >= 0:
        return "Neutral"
    elif relation >= -29:
        return "Wary"
    else:
        return "Hostile"


# ═══════ ASSESSMENT TEMPLATES (§3f) ═══════
_ASSESSMENT_TEMPLATES = {
    "war_winning": "{nation} falters, Your Excellency. Our armies press the advantage — an armistice now would be accepted from a position of strength.",
    "war_losing": "The campaign goes poorly against {nation}. An armistice may be wise — though they will sense our weakness and demand terms.",
    "war_stalemate": "The war with {nation} grinds on without decisive result. Both sides bleed. An armistice may find receptive ears.",
    "armistice_wary": "The guns are silent, but the wound festers. Peace may be achievable with {nation}, though they will demand terms.",
    "armistice_neutral": "The armistice holds. {nation} appears open to permanent peace — the moment may be favorable.",
    "peace_hostile": "Relations with {nation} remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes.",
    "peace_wary": "{nation} maintains a cautious distance. Their diplomats watch our moves with calculating eyes. Open borders would test their appetite.",
    "peace_neutral": "{nation} is neither friend nor foe. Opportunity exists for closer ties — open borders would be a natural first step.",
    "peace_friendly": "{nation} is well-disposed toward us. The time is ripe for open borders, perhaps more.",
    "open_borders_neutral": "Our borders with {nation} are open, but trust remains shallow. A non-aggression pact would formalize the thaw.",
    "open_borders_friendly": "{nation} trades freely with us. The foundation is strong — a non-aggression pact or deeper ties are within reach.",
    "non_aggression_to_alliance": "We have {nation}'s word they will not strike. A defensive alliance would bind us closer — if the relation bears it.",
    "alliance_stable": "Our alliance with {nation} stands firm. There is little to gain from change, and much to lose.",
    "alliance_strained": "Our alliance with {nation} holds, but the bond frays. Tread carefully — a break now would cost us dearly.",
    "vassal_loyal": "{nation} serves faithfully. Tribute flows, the garrison keeps order. A reliable vassal.",
    "vassal_restless": "Unrest simmers in {nation}. The burden of tribute grows heavy — investment would forestall rebellion.",
    "vassal_rebellious": "{nation} teeters on the edge of rebellion, Your Excellency. Urgent investment or increased autonomy may be our only recourse.",
}

_ASSESSMENT_FALLBACK = "Talleyrand considers the situation with {nation}."


def get_assessment_text(world, target_nation: str) -> str:
    """Get Talleyrand's assessment template for a nation (§3f)."""
    player = getattr(world, 'player_nation', 'France')
    diplo_key = world._make_diplo_key(player, target_nation)
    state = world.diplomatic_states.get(diplo_key, "PEACE")
    relation = world.nation_relations.get(diplo_key, 0)

    # Vassal check
    vassals = getattr(world, 'vassals', {})
    if target_nation in vassals:
        loyalty = vassals[target_nation].get("loyalty", 50)
        if loyalty >= 50:
            key = "vassal_loyal"
        elif loyalty >= 25:
            key = "vassal_restless"
        else:
            key = "vassal_rebellious"
        template = _ASSESSMENT_TEMPLATES.get(key, _ASSESSMENT_FALLBACK)
        return template.format(nation=target_nation)

    if state == "WAR":
        war_score = get_war_score_for(world, player, target_nation)
        if war_score > 20:
            key = "war_winning"
        elif war_score < -20:
            key = "war_losing"
        else:
            key = "war_stalemate"
    elif state == "ARMISTICE":
        key = "armistice_wary" if relation < 0 else "armistice_neutral"
    elif state == "PEACE":
        if relation < -29:
            key = "peace_hostile"
        elif relation < 0:
            key = "peace_wary"
        elif relation < 30:
            key = "peace_neutral"
        else:
            key = "peace_friendly"
    elif state == "OPEN_BORDERS":
        key = "open_borders_neutral" if relation < 30 else "open_borders_friendly"
    elif state == "NON_AGGRESSION":
        key = "non_aggression_to_alliance"
    elif state in ("DEFENSIVE_ALLIANCE", "ALLIANCE"):
        key = "alliance_stable" if relation >= 50 else "alliance_strained"
    else:
        key = None

    if key and key in _ASSESSMENT_TEMPLATES:
        return _ASSESSMENT_TEMPLATES[key].format(nation=target_nation)
    return _ASSESSMENT_FALLBACK.format(nation=target_nation)


def get_available_diplomatic_actions(world, target_nation: str) -> List[Dict]:
    """Build available action list for the diplomacy wizard (§2b/2c/2d).

    Returns list of action dicts with dp_cost, available, disabled_reason,
    likelihood (for proposals), likelihood_score.
    """
    # Block diplomacy while hard-stops, current-turn offers, or local planning active
    dm = world.dialogue_manager
    if dm.is_hard_stop() or dm.has_current_turn_offers() or dm.is_local_planning():
        return []

    player = getattr(world, 'player_nation', 'France')
    diplo_key = world._make_diplo_key(player, target_nation)
    state = world.diplomatic_states.get(diplo_key, "PEACE")
    dp = int(getattr(world, 'diplomatic_points', 0))
    gold = int(world.nation_gold.get(player, 0)) if hasattr(world, 'nation_gold') else 0
    vassals = getattr(world, 'vassals', {})

    # Talleyrand skill for DP cost adjustment
    diplomats = getattr(world, 'diplomats', {})
    talleyrand = diplomats.get(player)
    tal_skill = talleyrand.skill if talleyrand else 5

    actions = []
    active_treaties = getattr(world, 'active_treaties', {})

    # ── VASSAL MANAGEMENT (§2c) ──
    if target_nation in vassals:
        vassal_state = vassals[target_nation]
        autonomy = vassal_state.get("autonomy", 1)

        # Invest in Vassal
        invest_available = True
        invest_reason = ""
        invest_cooldowns = getattr(world, 'vassal_investment_cooldowns', {})
        if target_nation in invest_cooldowns and invest_cooldowns[target_nation] > 0:
            invest_available = False
            invest_reason = f"Cooldown: {invest_cooldowns[target_nation]} turns"
        elif dp < 1:
            invest_available = False
            invest_reason = "Insufficient DP"
        elif gold < 200:
            invest_available = False
            invest_reason = "Insufficient Gold"
        actions.append({
            "action": "invest_vassal",
            "display_name": "Invest in Vassal",
            "dp_cost": 1,
            "gold_cost": 200,
            "available": invest_available,
            "disabled_reason": invest_reason,
        })

        # Increase Autonomy
        from backend.game_logic.vassal import AUTONOMY_AUTONOMOUS
        inc_available = autonomy < AUTONOMY_AUTONOMOUS
        inc_reason = "" if inc_available else "Already at maximum autonomy"
        if inc_available and dp < 1:
            inc_available = False
            inc_reason = "Insufficient DP"
        actions.append({
            "action": "increase_autonomy",
            "display_name": "Increase Autonomy",
            "dp_cost": 1,
            "available": inc_available,
            "disabled_reason": inc_reason,
        })

        # Decrease Autonomy
        from backend.game_logic.vassal import AUTONOMY_PUPPET
        dec_available = autonomy > AUTONOMY_PUPPET
        dec_reason = "" if dec_available else "Already at minimum autonomy"
        if dec_available and dp < 1:
            dec_available = False
            dec_reason = "Insufficient DP"
        actions.append({
            "action": "decrease_autonomy",
            "display_name": "Decrease Autonomy",
            "dp_cost": 1,
            "available": dec_available,
            "disabled_reason": dec_reason,
        })

        # Release Vassal
        release_available = True
        release_reason = ""
        if dp < 1:
            release_available = False
            release_reason = "Insufficient DP"
        actions.append({
            "action": "release_vassal",
            "display_name": "Release Vassal",
            "dp_cost": 1,
            "available": release_available,
            "disabled_reason": release_reason,
        })

        return actions

    # ── FOREIGN AFFAIRS (§2b) ──
    cooldowns = getattr(world, 'player_proposal_cooldowns', {})
    armistice_cooldowns = getattr(world, 'armistice_cooldowns', {})
    ultimatum_global_cd = getattr(world, 'ultimatum_global_cooldown', 0)
    relation = world.nation_relations.get(diplo_key, 0)

    def _proposal_action(action_key: str, display: str, target_state: str):
        base_cost = get_transition_dp_cost(state, target_state)
        cost = get_dp_cost(action_key, tal_skill, transition_base=base_cost)
        available = True
        reason = ""

        # Cooldown check
        if target_nation in cooldowns and cooldowns[target_nation] > 0:
            available = False
            reason = f"Cooldown: {cooldowns[target_nation]} turns"
        type_key = f"{target_nation}_{target_state.lower()}"
        if type_key in cooldowns and cooldowns[type_key] > 0:
            available = False
            reason = f"Cooldown: {cooldowns[type_key]} turns"

        # U2: Armistice cooldown check (prioritize over DP)
        arm_cd = armistice_cooldowns.get(diplo_key, 0)
        if arm_cd > 0 and target_state not in ("PEACE", "OPEN_BORDERS", "NON_AGGRESSION",
                                                 "DEFENSIVE_ALLIANCE", "ALLIANCE", "VASSAL"):
            available = False
            reason = f"Armistice: {arm_cd} turns remaining"

        # Relation requirement
        req = STATE_RELATION_REQUIREMENTS.get(target_state)
        if req is not None and relation < req:
            available = False
            reason = "Relations too low"

        if target_state in ("DEFENSIVE_ALLIANCE", "ALLIANCE"):
            if is_anti_renewal_active(world, player, target_nation):
                available = False
                turns = get_anti_renewal_turns_remaining(world, player, target_nation)
                reason = f"Anti-renewal: {turns} turns remaining"
            elif is_oathbreaker_auto_reject_active(world, target_nation):
                available = False
                turns = get_oathbreaker_turns_remaining(world, target_nation)
                reason = f"Oathbreaker posture: {turns} turns remaining"

        if target_state == "VASSAL" and available:
            cap = check_vassalage_power_cap(world, player, target_nation)
            if not cap["allowed"]:
                available = False
                reason = cap["reason"]

        # DP check
        if available and dp < cost:
            available = False
            reason = "Insufficient DP"

        # Calculate likelihood
        likelihood_score = 0
        likelihood = ""
        if (
            available
            or reason in ("Insufficient DP", "Relations too low")
            or reason.startswith("Anti-renewal")
            or reason.startswith("Oathbreaker")
        ):
            try:
                _type_map = {
                    "ARMISTICE": "armistice_winning",
                    "PEACE": "peace",
                    "OPEN_BORDERS": "open_borders",
                    "NON_AGGRESSION": "non_aggression",
                    "DEFENSIVE_ALLIANCE": "defensive_alliance",
                    "ALLIANCE": "alliance",
                    "VASSAL": "vassalage",
                }
                ptype = _type_map.get(target_state, "peace")
                if target_state == "ARMISTICE":
                    ws = get_war_score_for(world, player, target_nation)
                    ptype = "armistice_winning" if ws > 0 else "armistice_losing"
                proposal = {
                    "type": ptype,
                    "proposer_nation": player,
                    "target_nation": target_nation,
                    "sweeteners": [],
                    "demands": [],
                    "clauses": [],
                }
                result = calculate_acceptance(proposal, world)
                likelihood_score = int(result.get("score", 0))
                likelihood = get_likelihood_descriptor(likelihood_score)
            except Exception:
                likelihood_score = 0
                likelihood = "Hopeless"

        return {
            "action": action_key,
            "display_name": display,
            "dp_cost": int(cost),
            "available": available,
            "disabled_reason": reason,
            "likelihood": likelihood,
            "likelihood_score": int(likelihood_score),
        }

    # ── MISSION HELPERS ──
    from backend.game_logic.diplomatic_dialogue import MISSION_DP_COSTS
    active_mission = getattr(world, 'active_diplomatic_mission', None)
    tal_state = getattr(world, 'talleyrand_state', 'IDLE')

    # W5: Mission effect text mapping
    _MISSION_EFFECT_SHORT = {
        "IMPROVE_RELATIONS": "+5 relation/turn",
        "COURT_NATION": "+5 relation/turn, 20% blowback",
        "GATHER_INTEL": "3-turn full intel",
        "UNDERMINE_ALLIANCE": "-3 relation between targets/turn",
        "REASSURE_ALLY": "+3 relation/turn",
    }

    def _mission_action(action_key: str, display: str, mission_type: str):
        cost = MISSION_DP_COSTS.get(mission_type, 1)
        available = True
        reason = ""
        if tal_state == "IN_TRANSIT":
            available = False
            reason = "Talleyrand in transit"
        elif active_mission is not None:
            available = False
            reason = "Mission already active"
        elif dp < cost:
            available = False
            reason = "Insufficient DP"
        return {
            "action": action_key,
            "display_name": display,
            "dp_cost": int(cost),
            "available": available,
            "disabled_reason": reason,
            "effect_text": _MISSION_EFFECT_SHORT.get(mission_type, ""),
        }

    if state == "WAR":
        actions.append(_proposal_action("propose_armistice", "Propose Armistice", "ARMISTICE"))
        settlement_war_id = None
        multi_war_ambiguity = False
        available_wars = []
        try:
            player_wars = set(world.get_war_instances_by_participant(player))
            target_wars = set(world.get_war_instances_by_participant(target_nation))
            common_wars = sorted(player_wars & target_wars)
            if len(common_wars) == 1:
                settlement_war_id = common_wars[0]
            elif len(common_wars) > 1:
                multi_war_ambiguity = True
                available_wars = list(common_wars)
        except Exception:
            settlement_war_id = None
        if multi_war_ambiguity:
            from backend.display_names import settlement_disabled_reason_display
            settlement_eligibility = {
                "available": False,
                "error": "multi_war_ambiguity",
                "error_display": settlement_disabled_reason_display("multi_war_ambiguity"),
                "disabled_reason_display": settlement_disabled_reason_display("multi_war_ambiguity"),
                "available_wars": available_wars,
            }
        elif settlement_war_id:
            try:
                from backend.game_logic.settlement_validation import (
                    evaluate_open_settlement_eligibility,
                )
                settlement_eligibility = evaluate_open_settlement_eligibility(
                    world, war_id=settlement_war_id, actor_nation=player,
                )
            except Exception:
                settlement_eligibility = {
                    "available": False,
                    "error": "inactive_war_instance",
                }
        else:
            from backend.display_names import settlement_disabled_reason_display
            settlement_eligibility = {
                "available": False,
                "error": "one_to_one_war",
                "error_display": settlement_disabled_reason_display("one_to_one_war"),
                "disabled_reason_display": settlement_disabled_reason_display("one_to_one_war"),
            }
            if world.diplomatic_states.get(diplo_key) == "WAR":
                settlement_eligibility = {
                    "available": False,
                    "war_id": "",
                    "would_backfill": False,
                    "error": "one_to_one_war",
                    "error_display": settlement_disabled_reason_display("one_to_one_war"),
                    "disabled_reason_display": settlement_disabled_reason_display("one_to_one_war"),
                    "proposer_side": "",
                    "accepting_side": "",
                    "coverable_enemy_participants": [target_nation],
                    "display_reason": (
                        settlement_disabled_reason_display("one_to_one_war")
                    ),
                }
        settlement_available = bool(settlement_eligibility.get("available"))
        if settlement_eligibility.get("available"):
            settlement_disabled_reason = ""
            settlement_disabled_reason_label = ""
        else:
            settlement_disabled_reason = settlement_eligibility.get(
                "display_reason",
                settlement_eligibility.get(
                    "error_display",
                    str(settlement_eligibility.get("error", "")).replace("_", " ").title(),
                ),
            )
            settlement_disabled_reason_label = settlement_eligibility.get(
                "disabled_reason_display",
                settlement_disabled_reason,
            )
        actions.append({
            "action": "open_settlement",
            "display_name": "Open Settlement",
            "dp_cost": 0,
            "available": settlement_available,
            "disabled_reason": settlement_disabled_reason,
            "disabled_reason_display": settlement_disabled_reason_label,
            "war_id": settlement_war_id,
            "eligibility": settlement_eligibility,
        })
        # SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1 White Peace
        # Affordance: distinct CTA next to Open Settlement, sharing the
        # same eligibility gate so the wizard never offers a labeled
        # white peace when settlement entry itself is blocked. The
        # structured payload key is `propose_white_peace`; backend
        # routes through `_execute_propose_white_peace` and stages a
        # `settlement_confirm` dialogue with `white_peace=True`.
        actions.append({
            "action": "propose_white_peace",
            "display_name": "Propose White Peace",
            "dp_cost": 0,
            "available": settlement_available,
            "disabled_reason": settlement_disabled_reason,
            "disabled_reason_display": settlement_disabled_reason_label,
            "war_id": settlement_war_id,
            "eligibility": settlement_eligibility,
            "white_peace": True,
        })
        actions.append(_mission_action("mission_gather_intel", "Gather Intel", "GATHER_INTEL"))
        actions.append(_mission_action("mission_undermine", "Undermine Alliances", "UNDERMINE_ALLIANCE"))

    elif state == "ARMISTICE":
        actions.append(_proposal_action("propose_peace", "Propose Peace", "PEACE"))
        actions.append(_mission_action("mission_improve_relations", "Improve Relations", "IMPROVE_RELATIONS"))
        actions.append(_mission_action("mission_court", "Court Nation", "COURT_NATION"))
        actions.append(_mission_action("mission_gather_intel", "Gather Intel", "GATHER_INTEL"))
        actions.append(_mission_action("mission_undermine", "Undermine Alliances", "UNDERMINE_ALLIANCE"))

    elif state == "PEACE":
        actions.append(_proposal_action("propose_open_borders", "Propose Open Borders", "OPEN_BORDERS"))
        war_available = True
        war_reason = ""
        arm_cd = armistice_cooldowns.get(diplo_key, 0)
        if arm_cd > 0:
            war_available = False
            war_reason = f"Armistice: {arm_cd} turns remaining"
        elif dp < 1:
            war_available = False
            war_reason = "Insufficient DP"
        actions.append({"action": "declare_war", "display_name": "Declare War", "dp_cost": 1, "available": war_available, "disabled_reason": war_reason})
        ult_available = True
        ult_reason = ""
        ult_cd = ultimatum_global_cd
        if ult_cd > 0:
            ult_available = False
            ult_reason = f"Cooldown: {ult_cd} turns"
        elif dp < 2:
            ult_available = False
            ult_reason = "Insufficient DP"
        actions.append({"action": "send_ultimatum", "display_name": "Send Ultimatum", "dp_cost": 2, "available": ult_available, "disabled_reason": ult_reason})
        actions.append(_mission_action("mission_improve_relations", "Improve Relations", "IMPROVE_RELATIONS"))
        actions.append(_mission_action("mission_court", "Court Nation", "COURT_NATION"))
        actions.append(_mission_action("mission_gather_intel", "Gather Intel", "GATHER_INTEL"))
        actions.append(_mission_action("mission_undermine", "Undermine Alliances", "UNDERMINE_ALLIANCE"))

    elif state == "OPEN_BORDERS":
        actions.append(_proposal_action("propose_non_aggression", "Propose Non-Aggression", "NON_AGGRESSION"))
        actions.append(_proposal_action("propose_vassal", "Propose Vassal", "VASSAL"))
        actions.append({"action": "declare_war", "display_name": "Declare War", "dp_cost": 1, "available": dp >= 1, "disabled_reason": "" if dp >= 1 else "Insufficient DP"})
        has_treaty = diplo_key in active_treaties
        bt_available = dp >= 1 and has_treaty
        bt_reason = "" if bt_available else ("No active treaty" if not has_treaty else "Insufficient DP")
        actions.append({"action": "break_treaty", "display_name": "Break Treaty", "dp_cost": 1, "available": bt_available, "disabled_reason": bt_reason})
        actions.append({"action": "downgrade", "display_name": "Downgrade", "dp_cost": 1, "available": dp >= 1, "disabled_reason": "" if dp >= 1 else "Insufficient DP"})
        ult_available = True
        ult_reason = ""
        ult_cd = ultimatum_global_cd
        if ult_cd > 0:
            ult_available = False
            ult_reason = f"Cooldown: {ult_cd} turns"
        elif dp < 2:
            ult_available = False
            ult_reason = "Insufficient DP"
        actions.append({"action": "send_ultimatum", "display_name": "Send Ultimatum", "dp_cost": 2, "available": ult_available, "disabled_reason": ult_reason})
        actions.append(_mission_action("mission_improve_relations", "Improve Relations", "IMPROVE_RELATIONS"))
        actions.append(_mission_action("mission_court", "Court Nation", "COURT_NATION"))
        actions.append(_mission_action("mission_gather_intel", "Gather Intel", "GATHER_INTEL"))
        actions.append(_mission_action("mission_undermine", "Undermine Alliances", "UNDERMINE_ALLIANCE"))

    elif state == "NON_AGGRESSION":
        actions.append(_proposal_action("propose_defensive_alliance", "Propose Defensive Alliance", "DEFENSIVE_ALLIANCE"))
        actions.append(_proposal_action("propose_vassal", "Propose Vassal", "VASSAL"))
        actions.append({"action": "declare_war", "display_name": "Declare War", "dp_cost": 1, "available": dp >= 1, "disabled_reason": "" if dp >= 1 else "Insufficient DP"})
        has_treaty = diplo_key in active_treaties
        bt_available = dp >= 1 and has_treaty
        bt_reason = "" if bt_available else ("No active treaty" if not has_treaty else "Insufficient DP")
        actions.append({"action": "break_treaty", "display_name": "Break Treaty", "dp_cost": 1, "available": bt_available, "disabled_reason": bt_reason})
        actions.append({"action": "downgrade", "display_name": "Downgrade", "dp_cost": 1, "available": dp >= 1, "disabled_reason": "" if dp >= 1 else "Insufficient DP"})
        ult_available = True
        ult_reason = ""
        ult_cd = ultimatum_global_cd
        if ult_cd > 0:
            ult_available = False
            ult_reason = f"Cooldown: {ult_cd} turns"
        elif dp < 2:
            ult_available = False
            ult_reason = "Insufficient DP"
        actions.append({"action": "send_ultimatum", "display_name": "Send Ultimatum", "dp_cost": 2, "available": ult_available, "disabled_reason": ult_reason})
        actions.append(_mission_action("mission_improve_relations", "Improve Relations", "IMPROVE_RELATIONS"))
        actions.append(_mission_action("mission_court", "Court Nation", "COURT_NATION"))
        actions.append(_mission_action("mission_gather_intel", "Gather Intel", "GATHER_INTEL"))
        actions.append(_mission_action("mission_undermine", "Undermine Alliances", "UNDERMINE_ALLIANCE"))

    elif state == "DEFENSIVE_ALLIANCE":
        actions.append(_proposal_action("propose_alliance", "Propose Alliance", "ALLIANCE"))
        actions.append(_proposal_action("propose_vassal", "Propose Vassal", "VASSAL"))
        actions.append({"action": "declare_war", "display_name": "Declare War", "dp_cost": 1, "available": dp >= 1, "disabled_reason": "" if dp >= 1 else "Insufficient DP"})
        has_treaty = diplo_key in active_treaties
        bt_available = dp >= 1 and has_treaty
        bt_reason = "" if bt_available else ("No active treaty" if not has_treaty else "Insufficient DP")
        actions.append({"action": "break_treaty", "display_name": "Break Treaty", "dp_cost": 1, "available": bt_available, "disabled_reason": bt_reason})
        actions.append({"action": "downgrade", "display_name": "Downgrade", "dp_cost": 1, "available": dp >= 1, "disabled_reason": "" if dp >= 1 else "Insufficient DP"})
        actions.append(_mission_action("mission_improve_relations", "Improve Relations", "IMPROVE_RELATIONS"))
        actions.append(_mission_action("mission_reassure", "Reassure Ally", "REASSURE_ALLY"))
        actions.append(_mission_action("mission_gather_intel", "Gather Intel", "GATHER_INTEL"))
        actions.append(_mission_action("mission_undermine", "Undermine Alliances", "UNDERMINE_ALLIANCE"))
        # PL-14: Ultimatums available for any non-war, non-vassal target
        ult_available = True
        ult_reason = ""
        ult_cd = ultimatum_global_cd
        if ult_cd > 0:
            ult_available = False
            ult_reason = f"Cooldown: {ult_cd} turns"
        elif dp < 2:
            ult_available = False
            ult_reason = "Insufficient DP"
        actions.append({"action": "send_ultimatum", "display_name": "Send Ultimatum", "dp_cost": 2, "available": ult_available, "disabled_reason": ult_reason})

    elif state == "ALLIANCE":
        actions.append({"action": "declare_war", "display_name": "Declare War", "dp_cost": 1, "available": dp >= 1, "disabled_reason": "" if dp >= 1 else "Insufficient DP"})
        has_treaty = diplo_key in active_treaties
        bt_available = dp >= 1 and has_treaty
        bt_reason = "" if bt_available else ("No active treaty" if not has_treaty else "Insufficient DP")
        actions.append({"action": "break_treaty", "display_name": "Break Treaty", "dp_cost": 1, "available": bt_available, "disabled_reason": bt_reason})
        actions.append({"action": "downgrade", "display_name": "Downgrade", "dp_cost": 1, "available": dp >= 1, "disabled_reason": "" if dp >= 1 else "Insufficient DP"})
        actions.append(_mission_action("mission_reassure", "Reassure Ally", "REASSURE_ALLY"))
        actions.append(_mission_action("mission_gather_intel", "Gather Intel", "GATHER_INTEL"))
        actions.append(_mission_action("mission_undermine", "Undermine Alliances", "UNDERMINE_ALLIANCE"))
        # PL-14: Ultimatums available for any non-war, non-vassal target
        ult_available = True
        ult_reason = ""
        ult_cd = ultimatum_global_cd
        if ult_cd > 0:
            ult_available = False
            ult_reason = f"Cooldown: {ult_cd} turns"
        elif dp < 2:
            ult_available = False
            ult_reason = "Insufficient DP"
        actions.append({"action": "send_ultimatum", "display_name": "Send Ultimatum", "dp_cost": 2, "available": ult_available, "disabled_reason": ult_reason})

    # DPF-2: Cancel mission — only if active mission targets THIS nation
    if active_mission and active_mission.get("target") == target_nation:
        initial = int(active_mission.get("initial_relation") or 0)
        current_rel = int(world.nation_relations.get(
            world._make_diplo_key(player, target_nation), 0
        ) or 0)
        delta = current_rel - initial
        turns = int(active_mission.get("turns_active") or 0)
        mission_type_raw = active_mission.get("type", "")

        initial_desc = get_relation_descriptor(initial)
        current_desc = get_relation_descriptor(current_rel)

        if initial_desc != current_desc:
            progress_text = f"{initial_desc} \u2192 {current_desc} ({'+' if delta >= 0 else ''}{delta}, {turns} turns)"
        else:
            progress_text = f"{current_desc} ({'+' if delta >= 0 else ''}{delta} over {turns} turns)"

        actions.append({
            "action": "cancel_mission",
            "display_name": f"Cancel: {mission_type_raw.replace('_', ' ').title()}",
            "dp_cost": 0,
            "gold_cost": 0,
            "available": True,
            "disabled_reason": "",
            "effect_text": progress_text,
            "likelihood": "",
        })

    return actions


def get_diplomatic_preview(world, target_nation: str) -> Dict:
    """Build the full diplomatic preview response for a nation (§3c)."""
    player = getattr(world, 'player_nation', 'France')
    diplo_key = world._make_diplo_key(player, target_nation)
    state = world.diplomatic_states.get(diplo_key, "PEACE")
    relation = world.nation_relations.get(diplo_key, 0)
    dp = int(getattr(world, 'diplomatic_points', 0))
    vassals = getattr(world, 'vassals', {})
    is_vassal = target_nation in vassals

    dm = world.dialogue_manager
    dialogue_pending = dm.is_hard_stop() or dm.has_current_turn_offers() or dm.is_local_planning()
    # PL-30: Distinguish blocking dialogue from deferred proposal result
    has_deferred_result = world.proposal_result_popup is not None
    talleyrand_state = getattr(world, 'talleyrand_state', 'IDLE')

    response = {
        "nation": target_nation,
        "state": state,  # Bug 7 fix: alias for wizard consistency with Step 1
        "current_state": state,
        "current_state_display": _STATE_DISPLAY_NAMES.get(state, state),
        "relation": int(relation),
        "relation_descriptor": get_relation_descriptor(relation),
        "dp_available": int(dp),
        "dialogue_pending": dialogue_pending,
        "has_deferred_result": has_deferred_result,
        "talleyrand_in_transit": talleyrand_state == "IN_TRANSIT",
        "is_vassal": is_vassal,
    }

    if is_vassal:
        from backend.game_logic.vassal import AUTONOMY_NAMES, AUTONOMY_DRIFT
        v = vassals[target_nation]
        loyalty = v.get("loyalty", 50)
        autonomy = v.get("autonomy", 1)
        drift = AUTONOMY_DRIFT.get(autonomy, 0)
        if drift > 0:
            trend = "rising"
        elif drift < 0:
            trend = "falling"
        else:
            trend = "stable"
        response["vassal_loyalty"] = int(loyalty)
        response["vassal_autonomy"] = AUTONOMY_NAMES.get(autonomy, "Satellite")
        response["vassal_loyalty_trend"] = trend
        tribute_rate = v.get("tribute_rate", 0.5)
        vassal_income = sum(50 for r in world.regions.values() if getattr(r, 'controller', '') == target_nation)
        response["vassal_tribute"] = int(vassal_income * tribute_rate)
        response["section"] = "vassal_management"
    else:
        response["section"] = "foreign_affairs"

    response["assessment"] = get_assessment_text(world, target_nation)
    actions = get_available_diplomatic_actions(world, target_nation)
    response["actions"] = actions
    response["recommendation"] = _build_recommendation(world, target_nation, actions, dp, is_vassal, vassals)

    # W3: Acceptance preview — top 3 positive/negative factors for best proposal
    acceptance_preview = None
    best_proposal_action = None
    best_score = -999
    for a in actions:
        if a.get("available") and a["action"].startswith("propose_"):
            score = a.get("likelihood_score", 0)
            if score > best_score:
                best_score = score
                best_proposal_action = a
    if best_proposal_action:
        try:
            # Build a mock proposal to get components
            action_to_type = {
                "propose_armistice": "armistice_winning" if (get_war_score_for(world, player, target_nation) > 0) else "armistice_losing",
                "propose_peace": "peace",
                "propose_open_borders": "open_borders",
                "propose_non_aggression": "non_aggression",
                "propose_defensive_alliance": "defensive_alliance",
                "propose_alliance": "alliance",
                "propose_vassal": "vassalage",
            }
            ptype = action_to_type.get(best_proposal_action["action"], "peace")
            mock_proposal = {
                "type": ptype,
                "proposer_nation": player,
                "target_nation": target_nation,
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            }
            result = calculate_acceptance(mock_proposal, world)
            components = result.get("components", {})

            # Human-readable labels for components
            _COMPONENT_LABELS = {
                "base_disposition": "Base willingness",
                "war_score_modifier": "Our military dominance",
                "relation_modifier": "Current relations",
                "war_weariness": "Exhaustion from prolonged conflict",
                "stalemate_duration": "Stalemate weariness",
                "hegemony_target_mod": "Hegemon bloc pressure",
                "bilateral_betrayal_mod": "Remembered betrayals",
                "deal_balance": "Deal terms",
                "diplomat_skill_bonus": "Diplomatic skill advantage",
                "personality_modifier": "Diplomat personality",
                "military_supremacy": "Military supremacy",
                "battlefield_diplomacy": "Battlefield diplomacy",
                "military_pressure": "Military pressure",
                "special_desire_bonus": "Appeals to core interests",
                "harshness_bonus": "Previous treaty precedent",
                "reliability_modifier": "Our diplomatic reputation",
            }

            positives = []
            negatives = []
            for key, val in components.items():
                if not val:
                    continue
                label = _COMPONENT_LABELS.get(key, key.replace("_", " ").title())
                entry = {"key": key, "label": label, "value": int(round(val or 0))}
                if val > 0:
                    positives.append(entry)
                else:
                    negatives.append(entry)

            # Sort by magnitude, take top 3
            positives.sort(key=lambda x: x["value"], reverse=True)
            negatives.sort(key=lambda x: x["value"])
            acceptance_preview = {
                "positive": positives[:3],
                "negative": negatives[:3],
            }
        except Exception:
            acceptance_preview = None
    response["acceptance_preview"] = acceptance_preview

    # BPH-B: Attach war context snapshots for peace-class actions
    if state in ("WAR", "ARMISTICE"):
        peace_snapshots = {}
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        for a in actions:
            action_id = a.get("action", "")
            if action_id in PEACE_CLASS_ACTIONS and a.get("available"):
                ptype_map = {
                    "propose_armistice": "armistice_winning" if get_war_score_for(world, player, target_nation) > 0 else "armistice_losing",
                    "propose_peace": "peace",
                }
                ptype = ptype_map.get(action_id, "peace")
                try:
                    terms = generate_suggested_terms(target_nation, ptype, world)
                    snapshot = build_war_context_snapshot(
                        world, player, target_nation, ptype, terms=terms,
                    )
                    peace_snapshots[action_id] = snapshot
                except Exception:
                    pass
        if peace_snapshots:
            response["war_context_snapshots"] = peace_snapshots

    return response


def _build_recommendation(world, target_nation: str, actions: List[Dict],
                          dp: int, is_vassal: bool, vassals: dict) -> str:
    """Build Talleyrand's recommendation (§3f tiers)."""
    if dp <= 0:
        return "Our diplomatic reserves are spent. We must wait."

    if is_vassal:
        v = vassals.get(target_nation, {})
        loyalty = v.get("loyalty", 50)
        if loyalty < 25:
            return "Talleyrand recommends: Invest to strengthen loyalty"
        return "No urgent action needed"

    best_proposal = None
    best_score = -999
    for a in actions:
        if not a.get("available"):
            continue
        score = a.get("likelihood_score", 0)
        if a["action"].startswith("propose_"):
            if score > best_score:
                best_score = score
                best_proposal = a

    if best_proposal and best_score >= 40:
        return f"Talleyrand recommends: {best_proposal['display_name']}"

    # W6: When all proposals are hopeless, suggest improve relations mission if available
    if best_score < 40:
        for a in actions:
            if a.get("available") and a["action"] == "mission_improve_relations":
                return "No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate."

    return "Relations must improve before proposals will find purchase. A battlefield victory would change their calculus."
