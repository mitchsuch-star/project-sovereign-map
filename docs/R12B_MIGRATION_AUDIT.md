# R12B Migration Audit: diplomatic_executor.py

**Created:** March 28, 2026 (Phase 0 pre-migration audit)
**Purpose:** Line-by-line classification of all 73 `pending_diplomatic_dialogue` operations for migration to DialogueManager API. This file is the single source of truth for the migration — any new context/session should read this + grep for remaining operations.

**Design Decision:** ALL 22 SETs use `replace()`, not `push()`. Rationale: every SET in diplomatic_executor.py is a synchronous response to player input (either a fresh command or a dialogue step progression). The player expects to see the result immediately. `push()` would queue behind existing dialogue — wrong UX. `replace()` matches old overwrite behavior exactly. `push()` semantics are reserved for async/external sources (AI proposals, vassal popups) in 12C.

## Progress Tracking

```bash
# Run this to see remaining unmigrated operations:
grep -n "pending_diplomatic_dialogue\s*=" backend/commands/diplomatic_executor.py

# Target: 0 lines returned
```

---

## Classification Key

| Pattern | Old Code | New Code | When |
|---------|----------|----------|------|
| **replace** | `world.pending_diplomatic_dialogue = dict` | `world.dialogue_manager.replace(dict)` | All SETs — replaces current slot |
| **delete** | `world.pending_diplomatic_dialogue = None` (before SET in same path) | DELETE the line | Pattern 3: the following replace() handles it |
| **pop** | `world.pending_diplomatic_dialogue = None` (then return) | `world.dialogue_manager.pop()` | Dialogue resolved/dismissed |
| **read** | `world.pending_diplomatic_dialogue` used in condition/return | No change | Works through transparent property getter |

---

## SETs → `replace()` (22 sites)

| # | Line | Method | Context |
|---|------|--------|---------|
| S1 | 103-120 | `_execute_diplomatic_proposal` | Nation picker (no target specified) |
| S2 | 198 | `_execute_diplomatic_proposal` | Generated dialogue (target specified) |
| S3 | 221 | `_execute_diplomatic_mission` | Mission dialogue (no args) |
| S4 | 261 | `_execute_diplomatic_mission` | Mission confirmation (with args) |
| S5 | 281 | `_execute_diplomatic_feasibility` | Feasibility dialogue |
| S6 | 338 | `_execute_diplomatic_advisory` | Advisory dialogue |
| S7 | 475-488 | `_execute_diplomatic_declare_war` | Treaty warning confirmation (blocking) |
| S8 | 1078 | `_process_dialogue_choice` (modify_harsh) | Enriched proposal replaces current |
| S9 | 1176 | `_process_dialogue_choice` (modify_generous) | Enriched proposal replaces current |
| S10 | 1209 | `_process_dialogue_choice` (expand_options) | New dialogue after Pattern 3 clear (paired with C7 DELETE at line 1203) |
| S11 | 1278 | `_process_dialogue_choice` (adjust_terms) | Terms guidance step 1 |
| S12 | 1314 | `_process_dialogue_choice` (territory_yes) | Region pick step |
| S13 | 1361 | `_process_dialogue_choice` (offer_region) | Next region step |
| S14 | 1397 | `_process_dialogue_choice` (skip_region) | Next candidate step |
| S15 | 1422 | `_process_dialogue_choice` (skip_region exhausted) | No more candidates — fallback options |
| S16 | 1569 | `_process_dialogue_choice` (expand_to_proposal) | New dialogue after Pattern 3 clear (paired with C14 DELETE at line 1563) |
| S17 | 1619 | `_process_dialogue_choice` (review_counter) | Counter-offer review confirmation |
| S18 | 2000 | `_build_gold_step` | Gold offering step |
| S19 | 2027 | `_build_ap_step` | AP offering step |
| S20 | 2089 | `_build_confirm_step` | Final confirm step |
| S21 | 2122-2141 | `_handle_accept_ai_proposal` | Alliance conflict alert (blocking) |
| S22 | 2270-2297 | `_handle_counter_ai_proposal` | Counter-offer presentation (blocking) |

---

## CLEARs → `pop()` or DELETE (43 sites)

| # | Line | Method / Action | Context | Classification |
|---|------|-----------------|---------|----------------|
| C1 | 869 | dismiss | Dialogue dismissed | **pop** |
| C2 | 873 | reconsider | Player reconsidering | **pop** |
| C3 | 879 | force_declare_war | War confirmed, dialogue done | **pop** |
| C4 | 924 | execute_proposal (insufficient DP) | Error exit | **pop** |
| C5 | 990 | execute_proposal (success) | Proposal sent | **pop** |
| C6 | 1188 | expand_options (no target) | Error exit | **pop** |
| C7 | **1203** | expand_options (before reroute) | Followed by SET on line 1209 | **DELETE** |
| C8 | 1487 | start_mission (no target) | Error exit | **pop** |
| C9 | 1493 | start_mission (insufficient DP) | Error exit | **pop** |
| C10 | 1517 | start_mission (success) | Mission started | **pop** |
| C11 | 1526 | cancel_mission (no mission) | Error exit | **pop** |
| C12 | 1531 | cancel_mission (success) | Mission cancelled | **pop** |
| C13 | 1550 | expand_to_proposal (no target) | Error exit | **pop** |
| C14 | **1563** | expand_to_proposal (before reroute) | Followed by SET on line 1569 | **DELETE** |
| C15 | 1589 | review_counter (no terms) | Error exit | **pop** |
| C16 | 1637 | confront/overlook (no talleyrand) | Error exit | **pop** |
| C17 | 1644 | sabotage confrontation (error) | Exception handler | **pop** |
| C18 | 1646 | sabotage confrontation (success) | Resolved | **pop** |
| C19 | 1663 | redemption (no talleyrand) | Error exit | **pop** |
| C20 | 1670 | redemption (error) | Exception handler | **pop** |
| C21 | 1672 | redemption (success) | Resolved | **pop** |
| C22 | 1715 | send_override/suggested (insufficient DP) | Error exit | **pop** |
| C23 | 1757 | send_override/suggested (success) | Proposal sent | **pop** |
| C24 | 1775 | accept_counter_offer (missing data) | Error exit | **pop** |
| C25 | 1783 | accept_counter_offer (success) | Ratified | **pop** |
| C26 | 1810 | reject_counter_offer | Rejected | **pop** |
| C27 | 1832 | invest_vassal_rebellion (no vassal) | Error exit | **pop** |
| C28 | 1836 | invest_vassal_rebellion (success) | Resolved | **pop** |
| C29 | 1847 | garrison_vassal_rebellion (no vassal) | Error exit | **pop** |
| C30 | 1851 | garrison_vassal_rebellion (removed) | Vassal gone | **pop** |
| C31 | 1856 | garrison_vassal_rebellion (insufficient AP) | Error exit | **pop** |
| C32 | 1865 | garrison_vassal_rebellion (success) | Resolved | **pop** |
| C33 | 1879 | accept_vassal_rebellion | Accepted risk | **pop** |
| C34 | 1902 | honor_defender (missing data) | Error exit | **pop** |
| C35 | 1907 | honor_defender (success) | War declared | **pop** |
| C36 | 1924 | break_defender_alliance (missing data) | Error exit | **pop** |
| C37 | 1939 | break_defender_alliance (success) | Alliance broken | **pop** |
| C38 | 1953 | unknown action (else) | Fallback exit | **pop** |
| C39 | 2109 | _handle_accept_ai_proposal (missing) | Error exit | **pop** |
| C40 | 2154 | _handle_accept_ai_proposal (success) | Treaty ratified | **pop** |
| C41 | 2192 | _handle_reject_ai_proposal | Rejected | **pop** |
| C42 | 2223 | _handle_counter_ai_proposal (missing) | Error exit | **pop** |
| C43 | 2240 | _handle_counter_ai_proposal (failed) | Counter rejected | **pop** |

---

## READs → No Change (8 sites)

| # | Line | Method | Code |
|---|------|--------|------|
| R1 | 123 | `_execute_diplomatic_proposal` | `world.pending_diplomatic_dialogue["talleyrand_text"]` |
| R2 | 124 | `_execute_diplomatic_proposal` | `"diplomatic_dialogue": world.pending_diplomatic_dialogue` |
| R3 | 776 | `handle_diplomatic_dialogue_response` | `if world.pending_diplomatic_dialogue is None:` |
| R4 | 779 | `handle_diplomatic_dialogue_response` | `dialogue = world.pending_diplomatic_dialogue` |
| R5 | 491 | `_execute_diplomatic_declare_war` | `world.pending_diplomatic_dialogue["message"]` |
| R6 | 492 | `_execute_diplomatic_declare_war` | `"diplomatic_dialogue": world.pending_diplomatic_dialogue` |
| R7 | 2145 | `_handle_accept_ai_proposal` | `"diplomatic_dialogue": world.pending_diplomatic_dialogue` |
| R8 | 2301-2302 | `_handle_counter_ai_proposal` | `["talleyrand_text"]` + `"diplomatic_dialogue": ...` |

---

## Paired Popup Clears (preserve alongside pop)

These clear companion popup fields and MUST stay inline next to their `pop()`:

| pop() site | Next line | Field cleared |
|------------|-----------|---------------|
| C25 (1783) | 1784 | `world.incoming_proposal_popup = None` |
| C26 (1810) | 1811 | `world.incoming_proposal_popup = None` |
| C28 (1836) | 1837 | `world.vassal_rebellion_imminent_popup = None` |
| C30 (1851) | 1852 | `world.vassal_rebellion_imminent_popup = None` |
| C32 (1865) | 1866 | `world.vassal_rebellion_imminent_popup = None` |
| C33 (1879) | 1880 | `world.vassal_rebellion_imminent_popup = None` |
| C35 (1907) | 1908 | `world.alliance_paradox_popup = None` |
| C37 (1939) | 1940 | `world.alliance_paradox_popup = None` |
| C18 (1646) | 1647 | `world.diplomatic_sabotage = None` |
| C21 (1672) | 1673 | `world.talleyrand_redemption = None` |

---

## Summary

| Type | Count | Action |
|------|-------|--------|
| SETs → `replace()` | 22 | `world.dialogue_manager.replace(dialogue)` |
| CLEARs → `pop()` | 41 | `world.dialogue_manager.pop()` |
| CLEARs → DELETE | 2 | Lines 1203, 1563 (Pattern 3 clear-before-set) |
| READs → no change | 8 | Work through property getter |
| **Total** | **73** | **65 lines changed/deleted** |

## Migration Order (method-by-method, test after each)

1. `_execute_diplomatic_proposal` (S1, S2, R1, R2) — 2 replaces, 2 reads
2. `_execute_diplomatic_mission` (S3, S4) — 2 replaces
3. `_execute_diplomatic_feasibility` (S5) — 1 replace
4. `_execute_diplomatic_advisory` (S6) — 1 replace
5. `_execute_diplomatic_declare_war` (S7, R5, R6) — 1 replace, 2 reads
6. `_process_dialogue_choice` — the big one (S8-S17, C1-C38) — 10 replaces, 2 deletes, 36 pops
7. `_build_gold_step` (S18) — 1 replace
8. `_build_ap_step` (S19) — 1 replace
9. `_build_confirm_step` (S20) — 1 replace
10. `_handle_accept_ai_proposal` (S21, C39-C40, R7) — 1 replace, 2 pops, 1 read
11. `_handle_reject_ai_proposal` (C41) — 1 pop
12. `_handle_counter_ai_proposal` (S22, C42-C43, R8) — 1 replace, 2 pops, 2 reads
