#!/bin/bash
# WB-B Audit Prompt — pipe this to Codex or paste into a code review AI
# Usage: cat tools/run_audit_wb_b.sh | codex
#    OR: copy the PROMPT section below into your review tool

cat <<'AUDIT_PROMPT'
You are a senior backend engineer reviewing a pull request for a Napoleonic strategy game.

## Task
Review the WB-B (War Bargain Lifecycle) implementation for correctness, spec compliance, and architectural soundness. The implementation adds fulfillment, breach, void, and zombie-clock mechanics to the existing war bargain data model.

## Spec Requirements (condensed from WAR_BARGAIN_SPEC.md §8.6–§8.9)

**Statuses:** active → triggered → fulfilled/breached/void. triggered → active (inconclusive war reactivation).

**Triggering:** active → triggered when promiser + beneficiary are both at WAR with named enemy.

**Fulfillment (§8.8):** All must hold: (1) status=triggered, (2) France controls claim region, (3) source treaty valid (DEF_ALLIANCE/ALLIANCE), (4) co-belligerents against named enemy. Reward: +4 reliability (10-turn pair cap), +6 relation. Terminal.

**Breach (§8.9.A):** France-caused: source treaty break/downgrade, normalization with enemy (NON_AGG+), peace with named enemy, contradictory bargain. Penalty: -6 reliability, -10 relation, +1 betrayal strike (2-per-episode cap), 6-turn cooldown.

**Void (§8.9.B):** Two families:
- counterparty_reversal: beneficiary breaks treaty, aligns with enemy, joins anti-France coalition
- obsolescence_or_external: claim basis lost, parties at war, zombie lapse
No French penalty, 4-turn cooldown.

**Zombie clock:** Cumulative counter. Increments when BOTH sides at ARMISTICE+ with enemy. Resets only on WAR. Voids at 5.

**Dormant notice:** One-time at 8+ turns active. Resets on triggered→active reactivation. Clock restarts from reactivation turn.

## Files to Review

Review these specific changes:

1. `backend/game_logic/diplomacy.py` — search for "WB-B: WAR BARGAIN LIFECYCLE" section (~lines 4591-4920)
2. `backend/campaign_log.py` — 4 new event types in CAMPAIGN_LOG_TYPES + CATEGORY_MAP + format_event_oneliner
3. `backend/game_logic/dispatch.py` — 4 new templates + priorities
4. `backend/models/world_state.py` — `_bargain_fulfillment_log` field + to_dict/from_dict
5. `tests/test_wb_b_lifecycle.py` — 42 tests

## Review Criteria

### Critical (must fix before merge)
- Spec violations (wrong penalties, missing conditions, wrong status transitions)
- Data loss (fields not serialized that should be)
- Hot-path per-region scans (Golden Rule 8 violation)
- Race conditions in lifecycle ordering (fulfill vs void vs breach priority)

### Important (should fix)
- Missing edge cases in tests
- Breach detection hooks not wired into callsites (are they standalone or integrated?)
- Dormant notice clock base correctness after multiple reactivation cycles

### Nice to have
- Code style consistency with the rest of the codebase
- Whether `_reactivated_turn` should be serialized or is safely transient

## Specific Questions

1. The `_bargain_fulfillment_log` is now serialized. Is the key format ("promiser|beneficiary") stable across save/load? Should it use the canonical `_make_diplo_key` ordering instead?

2. `detect_bargain_breach_on_treaty_change()` and `detect_bargain_breach_on_peace()` are standalone functions. They must be called from the appropriate diplomatic executor paths (treaty break, peace ratification). Are these callsites wired, or is this deferred to WB-C?

3. The lifecycle processes fulfillment BEFORE void detection. This means if France captures the claim region but also loses the source treaty in the same turn, fulfillment check fails (treaty invalid) and void fires. Is this the intended behavior per the same-turn downgrade exploit guard?

4. The void detection checks conditions in priority order: source_treaty_lost → beneficiary_aligned_with_enemy → anti_coalition → claim_basis_lost → parties_at_war. If multiple void conditions are true simultaneously, only the first one labels the event. Is this acceptable or should all conditions be reported?

5. `_record_bargain_breach_strike` reads `record["strikes"]` to check the episode cap. The existing B-B4 code uses `_get_active_betrayal_strikes` which filters by decay. Should bargain breach respect the same active-only filter, or is reading all strikes (including decayed) correct for the episode cap?

## Output Format

Provide your review as:
- **CRITICAL**: Issues that must be fixed before merge
- **IMPORTANT**: Issues that should be addressed
- **MINOR**: Style/consistency suggestions
- **QUESTIONS**: Answers to the 5 specific questions above
- **VERDICT**: APPROVE / REQUEST CHANGES / NEEDS DISCUSSION
AUDIT_PROMPT
