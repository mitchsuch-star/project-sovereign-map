# Audit Report: Phase 8 Sessions 2+3

**Date:** March 4, 2026
**Scope:** Diplomatic States, Acceptance Formula, Diplomat Class (Session 2), Talleyrand Commands + Conversational Dialogue Foundation (Session 3)
**Spec:** `docs/DIPLOMACY_SPEC.md` v2.3, `docs/CONVERSATIONAL_DIPLOMACY_DESIGN.md` v1.2

---

## Structural Checks

| ID | Check | Result | Notes |
|----|-------|--------|-------|
| 1A | Acceptance formula components match §6c | **PASS** | 7 components + military supremacy + battlefield diplomacy |
| 1B | Sweetener cap enforced | **PASS** | SWEETENER_CAP = 25 applied |
| 1C | War score component caps (±40/±30/±20/±30) | **PASS** | Territory/battle/decisive/capital caps match spec |
| 1D | DP generation formula matches §4a | **PASS** | `2 + skill//3 + authority//20 + capital_bonus` |
| 1E | Trade income matches §1d for all 5 nations | **PASS** | Starting trade verified in tests |
| 1F | `/respond_to_diplomatic_dialogue` is POST route | **PASS** | `@app.post("/respond_to_diplomatic_dialogue")` at main.py:877 |
| 1I | Diplomatic dialogue check ordering in executor | **PASS** | Order: pending_objection → pending_capture_choice → pending_diplomatic_dialogue. No bypass possible — objections always caught first. |
| 1J | advance_turn diplomatic processing matches §7f | **PASS** | Steps 1-4, 8, 9, 13 in process_diplomacy_turn(). Steps 10-11 in _advance_turn_internal after diplomacy. Minor deviation: auto-downgrade (step 13) runs inside process_diplomacy_turn() before income (step 10), but auto-downgrade only reads `turns_below_threshold` counters — no dependency on current turn income. Not a bug. |

## Formula Checks

| ID | Check | Result | Notes |
|----|-------|--------|-------|
| 2A | Acceptance formula worked example | **PASS** | Deviation: threat=0 (stubbed, not wired until Session 7). Code gives 18 vs spec's 6 — difference is exactly the threat component (-12). |
| 2B | Sweetener cap limits total sweetener bonus to 25 | **PASS** | |
| 2C | Military supremacy + battlefield diplomacy don't stack | **PASS** | max() used, not sum |
| 2D | War score caps per component | **PASS** | ±40/±30/±20/±30, total ±100 |
| 2E | War score decay formula | **PASS** | 10%/turn toward 0, int() rounded |

## State Machine Checks

| ID | Check | Result | Notes |
|----|-------|--------|-------|
| 3A | Transition adjacency enforced | **PASS** | TRANSITION_RULES defines valid (from, to) pairs |
| 3B | WAR declaration DP cost = 1 | **PASS** | WAR_DP_COST = 1 |
| 3C | DEFENSIVE_ALLIANCE cascade on war declaration | **PASS** | Tested: attack Austria → Prussia enters WAR |
| 3D | Downgrade penalties (relation + threat) | **PASS** | 4 downgrade paths with penalties |
| 3E | Auto-downgrade after 5 turns below threshold | **PASS** | turns_below_threshold tracking |

## Parser + Dialogue Checks

| ID | Check | Result | Notes |
|----|-------|--------|-------|
| 4A | Nation name resolution (exact + aliases) | **PASS** | 14 aliases → 5 canonical names |
| 4B | Proposal type keyword extraction | **PASS** | 6 types with multiple keywords each |
| 4C | Mission type keyword extraction | **PASS** | 5 mission types |
| 4D | Game bucket classification (WAR 5 buckets, PEACE 3) | **PASS** | War score thresholds: >30/0/-10/-30 |
| 4E | Template fallback chain (5 steps) | **PASS** | Exact → wildcard → WAR similar → PEACE neutral→hostile → FALLBACK → ultimate |
| 4F | End-turn diplomatic block | **PASS** | Note: unreachable in practice — general pending_diplomatic_dialogue check in executor fires first. Not a bug. |

## Edge Cases

| ID | Check | Result | Notes |
|----|-------|--------|-------|
| 5A | Proposal type propagated through fallback chain | **PASS** | _proposal_type field set at all fallback levels |
| 5B | Suggested terms: peace winning = gold demand | **PASS** | war_score > 20 → gold_per_turn demand |
| 5C | Suggested terms: peace losing = gold sweetener | **PASS** | war_score < -20 → gold_per_turn sweetener |
| 5D | Non-blocking dialogue auto-dismiss on turn advance | **PASS** | turn_created < current_turn check |
| 5E | Template text slot resolution safety | **PASS** | _SafeFormatMap returns {key} for missing slots |
| 5F | Backward compat: missing Session 2+3 fields | **PASS** | from_dict uses .get() defaults for all 15 fields |
| 5G | Backward compat: advance_turn survives stripped save | **PASS** | All fields popped → still runs |
| 5H | Serialization round-trip for all Session 2+3 fields | **PASS** | to_dict → from_dict preserves all fields |

## Cross-Reference Checks

| ID | Check | Result | Notes |
|----|-------|--------|-------|
| 6A | Diplomat starting values match §2e | **PASS** | 5 diplomats verified |
| 6B | Starting diplomatic states match §1e | **PASS** | France WAR with Britain+Prussia, others PEACE |
| 6C | Diplomat table in SYSTEMS_REFERENCE.md §16 | **PASS** | Added this audit session |
| 6D | DIPLOMACY_SPEC §7f processing order matches code | **PASS** | See 1J notes |

---

## Summary

| Metric | Value |
|--------|-------|
| **Bugs found** | 0 critical, 0 major |
| **Tests before audit** | 4625 |
| **Tests after audit** | 4654 (+29 new coverage gap tests) |
| **Coverage improvements** | diplomatic_templates.py: 63% → ~80% (fallback chain, suggested terms, resolve_with_type). diplomatic_dialogue.py: 90% → ~95% (resolve_nation_name, get_game_bucket branches). diplomacy.py: 94% → ~96% (get_transition_dp_cost paths). |
| **Deviations noted** | 1 minor: auto-downgrade runs before income in code (no functional impact). 1 expected: threat=0 stub (Session 7 scope). |

**Verdict: PASS — ready for Session 4.**
