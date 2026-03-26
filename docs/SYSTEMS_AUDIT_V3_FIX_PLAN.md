# Systems Audit V3 — Fix Plan

**Created:** 2026-03-25
**Source:** `audit-report-systems-v3.md` (179 findings across 7 phases)
**Verification:** Key findings verified against live code. All checked findings confirmed TRUE.

---

## Scope

179 audit findings: 51 MAJOR, 81 MINOR, 47 NOTE.
**~158 actionable items** across 10 required sessions + 1 optional polish session.
~19 items explicitly skipped (by design / no action needed).
11 concerns resolved by user review (see §Resolved Decisions).

---

## Resolved Decisions (User Review Complete)

| Item | Decision | Rationale |
|------|----------|-----------|
| **5A-15/16 approach** | Add NEW `get_hostile_marshals()`/`get_hostile_by_name()` variants | Existing methods have legitimate callers (map, LLM, fuzzy match). Leave originals intact. |
| **3A-1 concurrency** | **Option C: `threading.Lock`** | Game will eventually be live. Lock serializes state-mutating requests. ~15 lines, production-ready. |
| **5D-3 coordination** | **FIX — add coordination to glorious charges** | Fairness: enemy coordination already applies against charger. Either both use it or neither. Both is fairer. |
| **4B-4 brewing trade** | **SKIP** | EU4-style: players can still do diplomacy with brewing coalition members (potentially break them out). Working as intended. |
| **6D-5 VALID_ACTIONS** | **SKIP** | All four (pursue, support, reinforce, march) are real strategic actions translated by strategic parser. Not dead entries. |
| **7B-3 Gneisenau** | **SKIP** | Not adding enemy abilities until real map. |
| **4C-4 Berthier victory** | **SKIP** | Save for real map phase. Added to roadmap for new win conditions. |
| **4C-7 victory progress** | **SKIP** | Not worth it for current map. |
| **2D-6 clear regions** | **SKIP** | Map already shows this visually. New feature, not a fix. |
| **6A-8 CS template** | **Wire it up** | Add to Session 6 — trigger notification when Continental System activates. |
| **3A-2 async/sync mix** | **SKIP** | Code style, not a bug. |

### Technical Notes

**5A-15/16 (core method approach):** Verified that `get_enemy_marshals()` callers include map rendering, LLM prompt building, fuzzy match, and debug output — all legitimately need ALL non-player marshals. War-state filtering must happen at caller level or via new helpers, not by changing the accessor.

**3A-1 (threading.Lock):** `async def` won't work because command handler does blocking LLM calls. A `threading.Lock` around state-mutating POST endpoints is the simplest production-ready approach. Serializes requests (fine for turn-based game), prevents corruption from network retries, multiple tabs, or rapid clicking.

**5D-3 (coordination):** If glorious charge ignores coordination but the defending side gets coordination bonuses, the charger faces an asymmetric penalty. Fix: include coordination bonuses for the charging marshal's allies in the same region.

---

## Skipped Items (No Action Needed)

| ID | Reason |
|----|--------|
| 1C-7 | Signal ordering — audit says "no action needed" |
| 1C-8 | Hardcoded scroll target — documented tech debt, needs dynamic measurement |
| 2B-5 | Shallow dispatch copy — write-once, never mutated |
| 2B-6 | Popup field refs — synchronous serialization makes this harmless |
| 2D-6 | Clear regions in intel — new feature, map already shows this visually |
| 3A-2 | Async/sync mix — code style, not a bug |
| 3B-5 | Exception messages expose internals — acceptable for local game |
| 3D-3 | API key prefix logged — only 3 chars beyond `sk-ant-`, local only |
| 3D-4 | Cheats in mock mode — by design for testing |
| 3D-5 | CORS allows all — acceptable for local game server |
| 3D-6 | No type validation on save — has exception handler |
| 4B-4 | Brewing coalition trade — EU4-style, working as intended |
| 4C-4 | Berthier near-victory note — save for real map phase |
| 4C-6 | No capital-loss defeat — design decision |
| 4C-7 | Victory progress indicator — skip for current map |
| 6C-3 | Spec contradicts on defiance AP cost — spec issue, not code fix |
| 6D-5 | Strategic VALID_ACTIONS aliases — all real actions, translated by strategic parser |
| 7B-2 | Remainder overflow — documented by design |
| 7B-3 | Gneisenau unwired — feature gap, deferred to real map phase |

---

## Root Cause Patterns

### Pattern 1: War-State Ignorance (38 findings)
Legacy code uses `nation != marshal.nation` as a proxy for "is enemy." The diplomacy system (Phase 8) added ally/neutral states, but ~60% of enemy checks were never updated. Two core accessor methods propagate the bug to all callers.
**Bugs:** 4A-2, 4A-3, 4A-4, 5A-1 through 5A-33, 4E-2, 4E-3

### Pattern 2: Auto-Action Bypass (15 findings)
Auto-charge, auto-move, auto-bombardment, and garrison combat each inline their own combat resolution, skipping 5-12+ post-combat steps that the manual paths perform. Same root cause as V2's Pattern 1 but in different code paths.
**Bugs:** 4A-1, 4B-1, 4B-3, 5C-1 through 5C-12

### Pattern 3: Internal AP Check Duplication (3 findings)
Individual `_execute_*` methods perform their own AP checks that always read the player's pool, even when called for enemy AI. The outer executor correctly guards this, but inner checks duplicate it incorrectly.
**Bugs:** 4D-2, 4D-3 (stance + defend/fortify)

### Pattern 4: Campaign Log Whitelist Gaps (4 findings)
New event types added to the event log but never added to the campaign log whitelist. Nation eliminations, vassal joins, coalition departures invisible to players.
**Bugs:** 2D-3, 2D-4, 2D-5, 2D-7

---

## Session Plan

---

### Session 1: War-State Foundation + Critical AI Bugs [P0]

**8 bugs. Foundation for Sessions 2-3. Highest priority.**

| Bug | Sev | File | Fix |
|-----|-----|------|-----|
| 5A-15 | MAJOR | world_state.py:1119 | Add `get_hostile_marshals(nation)` — returns marshals of nations at war with `nation`. Leave `get_enemy_marshals()` intact |
| 5A-16 | MAJOR | world_state.py:1126 | Add `get_hostile_by_name(name, nation)` — war-aware variant of `get_enemy_by_name()` |
| 4A-2 | MAJOR | world_state.py:2025 / executor.py:3657 | `find_nearest_enemy()`: filter to hostile nations, or add war-state param |
| 4A-3 | MAJOR | executor.py:8602 | Fortify engagement: add `world.is_at_war(marshal.nation, m.nation)` |
| 4A-4 | MINOR | world_state.py:1507,1581 | `get_threatening_enemies()` + `get_safe_retreat_destination()`: add `is_at_war` filter |
| 4D-2 | MAJOR | executor.py:9947 | `_execute_stance_change()`: wrap internal AP check with `if marshal.nation == world.player_nation` |
| 4D-3 | MAJOR | executor.py:5281,8639 | `_execute_defend()` + `_execute_fortify()`: same player-nation guard on AP checks |
| 4E-1 | MAJOR | enemy_ai.py:509 | `decide_single_action()`: initialize all 6+ tracking sets before `_evaluate_marshal()` |

**Tests:** ~25 new tests. Verify hostile marshal filtering, fortify with allies, enemy AI stance/defend/fortify execution, autonomous marshal initialization.

**Files touched:** `world_state.py`, `executor.py`, `enemy_ai.py`

---

### Session 2: War-State Cascade — Executor [P0]

**14 bugs. All same pattern: add `is_at_war` checks in executor.py.**

| Bug | Sev | Description |
|-----|-----|-------------|
| 5A-1 | MAJOR | Reinforcement engagement treats allies as blocking (line 468) |
| 5A-2 | MAJOR | Overwatch counts allied artillery as enemy (line 682) |
| 5A-3 | MAJOR | Bombardment targets allied marshals (line 3931) |
| 5A-4 | MAJOR | Undefended-region check counts allies as defenders (line 3963) |
| 5A-5 | MAJOR | Cavalry charge leapfrog treats allies as blockers (line 4178) |
| 5A-6 | MAJOR | Post-battle remaining-defenders blocks conquest from allied presence (line 4403, 4873) |
| 5A-7 | MAJOR | Reckless charge alternatives include allied marshals (line 3570) |
| 5A-8 | MAJOR | Garrison validation treats allies as enemies (line 8131) |
| 5A-11 | MAJOR | Glorious charge targets allied marshals (line 10188) |
| 5A-9 | MINOR | Move capture hints count allies as defenders (line 7012) |
| 5A-10 | MINOR | Scout reports allies as enemies (line 7097) |
| 5A-12 | MINOR | Glorious charge leapfrog treats allies as blockers (line 10252) |
| 5A-13 | MINOR | Glorious charge remaining-defenders blocks capture (line 10407) |
| 5A-14 | MINOR | Post-objection charge target lacks war check (line 10603) |

**Pattern:** Each fix adds `and world.is_at_war(marshal.nation, m.nation)` (or equivalent) to an existing nation check. Use `get_hostile_marshals()` from Session 1 where a filtered list is needed.

**Tests:** ~20 new tests. One per bug: set up allied/neutral marshals, verify they're excluded from targeting/blocking/engagement.

**Files touched:** `executor.py`

---

### Session 3: War-State Cascade — World State, AI & Support Files [P0]

**19 bugs across 6 files. Same is_at_war pattern.**

| Bug | Sev | File | Description |
|-----|-----|------|-------------|
| 5A-17 | MINOR | world_state.py:1756 | `is_enemy_nearby()` counts allies |
| 5A-18 | MINOR | world_state.py:5759 | `_find_retreat_destination()` treats allies as blocking |
| 5A-19 | MINOR | world_state.py:5513 | Auto-charge remaining defenders counts allies |
| 5A-20 | MAJOR | disobedience.py:99,112,172,332 | 4 instances: move validation, drilling, engagement detection |
| 5A-21 | MINOR | disobedience.py:2197 | Aggressive fallback targets allies |
| 5A-22 | MINOR | disobedience.py:1163 | Objection ratio targets allies |
| 5A-23 | MINOR | objection_v2.py:530,597,731,1012 | 4 instances: visible enemies, engagement, path crossing |
| 5A-24 | MINOR | personality.py:324,342,411 | Adjacent enemy check, strength ratio count allies |
| 5A-25 | MINOR | strategic_parser.py:438 | SUPPORT/PURSUE target misclassifies allies |
| 5A-26 | MINOR | turn_manager.py:774 | Capital proximity alert on allies |
| 5A-27 | MINOR | enemy_ai.py:4761 | Cavalry threat detection counts allies |
| 5A-28 | MINOR | enemy_ai.py:4825 | Artillery position scoring penalizes allied cavalry |
| 5A-29 | MINOR | enemy_ai.py:4091 | CHECK 2 fortification counts allies |
| 5A-30 | MINOR | enemy_ai.py:2803 | P3 ally support counts allies as enemies |
| 5A-31 | MINOR | enemy_ai.py:2465 | P4.5 recapture counts allies as defenders |
| 5A-32 | MINOR | enemy_ai.py:2591 | P4.5 capture opportunity counts allies |
| 5A-33 | NOTE | enemy_ai.py:2288 | Artillery density counts allies |
| 4E-2 | MINOR | enemy_ai.py:1600 | P6.5 supply hardcodes player_nation |
| 4E-3 | MINOR | enemy_ai.py:4049 | CHECK 1 fortification missing is_at_war |

**Tests:** ~20 new tests. Focus on disobedience (5A-20, highest sev), objection_v2, and AI decision paths.

**Files touched:** `world_state.py`, `disobedience.py`, `objection_v2.py`, `personality.py`, `strategic_parser.py`, `turn_manager.py`, `enemy_ai.py`

---

### Session 4: Auto-Action Bypasses [P1]

**15 bugs. Fix auto-action paths that skip processing steps.**

| Bug | Sev | System | Fix |
|-----|-----|--------|-----|
| 4A-1 | MAJOR | Attack auto-move | Route through `_execute_move()` or set `moved_this_turn`, apply attrition, refresh fog, break square, check diplomacy |
| 4B-1 | MAJOR | Auto-charge | Add `process_battle_relationships()` call after combat resolution |
| 4B-3 | MINOR | Auto-charge | Add `marshal.increment_attacks_this_turn()` |
| 5C-1 | MAJOR | Auto-bombardment kill | Add missing 12+ post-combat steps (relationships, authority, coalition, battle recording, exhaustion, war damage) |
| 5C-2 | MAJOR | Reckless auto-move | Add fog visibility refresh after move |
| 5C-3 | MAJOR | Reckless auto-move | Add diplomatic territory entry check |
| 5C-4 | MINOR | Reckless auto-move | Add movement attrition |
| 5C-5 | MINOR | Auto-charge advance | Add movement attrition |
| 5C-6 | MINOR | Garrison combat | Add fog/intel update after garrison battle |
| 5C-7 | MINOR | Garrison combat | Add coalition threat + war exhaustion recording |
| 5C-8 | MINOR | Garrison combat | Add campaign log event + cannon fire recording |
| 5C-9 | MINOR | Garrison combat | Add authority modifier |
| 5C-10 | MINOR | Auto-bombardment kill | Add war damage to region |
| 5C-11 | MINOR | Garrison combat | Add war damage to region |
| 5C-12 | NOTE | Auto-charge advance | Add fog refresh (low impact) |

**Key approach:** For 5C-1 (auto-bombardment kill, 12+ missing steps), consider extracting a `_post_combat_processing()` helper from `_execute_attack` and calling it from all combat paths. This prevents the Pattern 2 root cause from recurring.

**Tests:** ~20 new tests. Verify relationships processed, exhaustion incremented, fog refreshed, attrition applied, authority updated after each auto-action path.

**Files touched:** `executor.py`, `world_state.py`, `combat.py`

---

### Session 5: Strategic Orders + Combat [P1]

**12 bugs across strategic orders, coordination, and combat.**

| Bug | Sev | File | Fix |
|-----|-----|------|-----|
| 7A-1 | MAJOR | executor.py:5515 | Add broken-state check before strategic command execution |
| 7A-2 | MAJOR | strategic.py (multiple) + executor.py:8734 | Clear `holding_position` in all 12+ cancellation paths |
| 7A-3 | MAJOR | strategic.py:1999 | Set `last_combat_result` in executor's `_execute_attack` after combat resolves |
| 5D-1 | MAJOR | combat.py:1055 | Coordinated mutual_destruction: add -20 morale penalty (matching normal path) |
| 5D-2 | MAJOR | executor.py:4571 | Coordinated pursuit: fix `max(1000, new_strength)` → `min(remaining, new_strength)` to prevent healing |
| 5D-3 | MINOR | executor.py | Glorious charge: add coordination bonuses (enemy coordination already applies against charger — fairness requires both sides use it) |
| 7A-4 | MINOR | executor.py:5709 | Cautious pathfinding: use fog-aware path (only visible regions) |
| 7A-5 | MINOR | executor.py:6592 | Literal reroute: same fog-aware pathfinding |
| 7A-6 | MINOR | executor.py:8734 | `_auto_break_square`: clear HOLD state + `holding_position` |
| 7A-8 | MINOR | strategic.py:93 | Dead marshal cleanup: clear `pending_interrupt` |
| 7A-7 | NOTE | strategic.py | Remove duplicated HOLD expiry dead code |
| 7B-1 | MINOR | relationship.py:124 | Include artillery reinforcements in relationship processing |

**Tests:** ~22 new tests. Broken marshal strategic orders, holding_position leak, until_battle_won trigger, mutual destruction morale, pursuit healing, glorious charge coordination.

**Files touched:** `executor.py`, `strategic.py`, `combat.py`, `relationship.py`

---

### Session 6: Fog, Dispatch & Backend Integration [P1]

**11 bugs. Fog leaks, stale data, and integration seams.**

| Bug | Sev | File | Fix |
|-----|-----|------|-----|
| 2A-1 | MAJOR | main.py:276 | Regenerate `summary` from filtered actions only, not original list |
| 2A-2 | MAJOR | main.py:1008 | Add `active_wars` independently when `enemy_phase` present (outside popup passthrough) |
| 6A-1 | MAJOR | dispatch.py:418 / world_state.py:4650 | Filter events by nation — skip enemy tactical events in player dispatch |
| 6A-2 | MAJOR | dispatch.py:974 | Add `nation_eliminated` template to dispatch event formatting |
| 2A-3 | MINOR | main.py:127 | Add display name mapping for Talleyrand mission types |
| 2A-4 | MINOR | main.py:1942 | Add diplomatic dialogue guard before cancel_order execution |
| 6A-3 | MINOR | dispatch.py:729 | Trigger 4: track last threshold state, fire only on CROSSING not proximity |
| 6A-8 | MINOR | notifications.py + diplomacy.py | Wire `diplomatic_continental_system` template — queue notification when CS activates |
| 2A-5 | NOTE | main.py:937 | Gate enemy phase debug prints behind `DEBUG_MODE` |
| 2A-6 | NOTE | main.py:544 | Filter interrupt name matching to player nation marshals |
| 2A-7 | NOTE | main.py:1696 | Add try/except wrapper to save endpoint |

**Tests:** ~16 new tests. Fog leak verification, war panel presence with enemy phase, dispatch filtering, template coverage, CS notification.

**Files touched:** `main.py`, `dispatch.py`, `world_state.py`, `notifications.py`, `diplomacy.py`

---

### Session 7: Diplomacy, Dialogue & Economy [P1]

**13 bugs across diplomacy wizard, dialogue system, and economy.**

| Bug | Sev | File | Fix |
|-----|-----|------|-----|
| 1D-1 | MAJOR | diplomacy.py:2856 | Change `target` → `target_nation` in acceptance_preview |
| 6B-1 | MAJOR | ledger.py:216 | Add admin bonus, treaty gold/turn, vassal tribute, CS penalty to net income |
| 6B-3 | MAJOR | vassal.py:608 + diplomacy.py:2831 | Use `region.get_effective_income()` instead of flat 50 |
| 4B-2 | MAJOR | dispatch.py:820 | Check `pending_diplomatic_dialogue` before overwriting; queue or re-queue existing |
| 4A-5 | MINOR | executor.py:11456 | Generate proposal fallback state from `world.get_diplomatic_state()` dynamically |
| 6B-2 | MINOR | executor.py:7931 | Use actual regen rate (accounting for war exhaustion) in recruit error message |
| 6B-4 | MINOR | diplomacy.py:2274 | Continental System: handle AUTONOMOUS vassals (remove from penalty) |
| 1D-2 | MINOR | diplomacy_wizard.gd:197 | Add `back_button.visible = false` in `_show_error()` |
| 1D-3 | MINOR | diplomacy_wizard.gd:172 | Move stale response check above error handling |
| 1D-4 | NOTE | diplomacy_wizard.gd:75 | Reset `dp_label` text in `open()` |
| 1D-5 | NOTE | diplomacy.py:2376 | Replace hardcoded "Vienna" with generic diplomatic reference |
| 1D-6 | NOTE | diplomacy_wizard.gd:218 | Show terminal message before auto-close on dialogue_pending |
| 6B-5 | NOTE | world_state.py:2130 | Remove stale TODO comment |

**Tests:** ~18 new tests. Acceptance preview for armistice, ledger net income accuracy, vassal tribute against actual income, dialogue queue preservation.

**Files touched:** `diplomacy.py`, `ledger.py`, `vassal.py`, `dispatch.py`, `executor.py`, `world_state.py`, `diplomacy_wizard.gd`

---

### Session 8: Save/Load, Modding & Campaign Log [P2]

**14 bugs across persistence, validation, and logging.**

| Bug | Sev | File | Fix |
|-----|-----|------|-----|
| 2B-1 | MAJOR | save_manager.py:120 | Clear ALL per-turn transient state on load: `objection_popups_this_turn`, `mild_concerns_this_turn`, `gold_spent_this_turn`, `diplomatic_trust_applied`, `threat_sources_this_turn`, `attacks_this_turn` |
| 2C-1 | MAJOR | validator.py | Add terrain validation against VALID_TERRAINS set from region.py |
| 2C-2 | MAJOR | validator.py | Add region_type validation against VALID_REGION_TYPES set from region.py |
| 2C-4 | MAJOR | world_state.py:3097 | Call `validate_scenario()` before `from_dict()` in `from_scenario()` |
| 2D-1 | MAJOR | world_state.py:570 | Add rolling cap on event_log (e.g., 500 events) or strip battle_report on insert |
| 2B-2 | MINOR | marshal.py:1225 | Change `from_dict` morale default from 70 → 100 to match `__init__` |
| 2B-3 | MINOR | world_state.py:2803 | Use `copy.deepcopy` for active_treaties in `to_dict()` |
| 2B-4 | MINOR | world_state.py:2793 | Use `copy.deepcopy` for previous_treaties in `to_dict()` |
| 2C-3 | MINOR | validator.py:68 | Add Saxony to VALID_NATIONS |
| 2C-5 | MINOR | marshal.py:1206 | Add `int()` cast to strength in `from_dict()` |
| 2D-2 | MINOR | combat.py:852 | Strip battle_report from event_log dict before insertion |
| 2D-3 | MINOR | campaign_log.py:83 | Add `nation_eliminated` to CAMPAIGN_LOG_TYPES + CATEGORY_MAP |
| 2D-4 | MINOR | campaign_log.py:83 | Add `vassal_auto_join_war` to whitelist |
| 2D-5 | MINOR | campaign_log.py:83 | Add `coalition_member_left` to whitelist |

**Also:** 3D-2 (save filename validation), 2C-6 (extreme value warnings), 2B-7 (dead fields), 2D-7 (diplomatic_downgrade whitelist).

**Tests:** ~20 new tests. Save/load transient state clearing, modding validator gaps, event_log capping, campaign log type coverage.

**Files touched:** `save_manager.py`, `validator.py`, `world_state.py`, `marshal.py`, `combat.py`, `campaign_log.py`, `main.py`

---

### Session 9: Parsing, Trust, Error Handling & Hardening [P2]

**13 bugs across LLM parsing, defiance, and error handling.**

| Bug | Sev | File | Fix |
|-----|-----|------|-----|
| 6D-1 | MAJOR | llm_client.py:562 | Fix enemy marshal names hijacking marshal slot — check player marshals first, then treat name as target |
| 6C-1 | MAJOR | executor.py:13691,10921 | Change defiance gate from `>= STRONG` to `>= MODERATE` per spec |
| 6D-2 | MINOR | llm_client.py:685 | Add "fall back to" as retreat/strategic move keyword |
| 6D-3 | MINOR | prompt_builder.py:371 | Fix "dig in" description: tactical fortify, not HOLD |
| 6D-4 | MINOR | executor.py:1494 | Add "wait" to `free_actions` set |
| 6C-2 | MINOR | defiance.py:268 + turn_manager.py:725 | Reset vindication decay timer on defiance/defensive vindication |
| 3B-1 | MINOR | world_state.py:2643 | Change bare `except:` to `except Exception:` |
| 3B-2 | MINOR | dispatch.py:666 | Log the exception instead of `pass` |
| 3B-3 | MINOR | executor.py:12945,12969 | Return `success: False` and log traceback for confrontation/redemption errors |
| 3B-4 | MINOR | marshal.py:231 | Replace `assert` with `if` check + `ValueError` |
| 3D-1 | MINOR | main.py:501 | Add `max_length=500` to CommandRequest.command |
| 3D-2 | MINOR | main.py:1697 | Add filename validation to save endpoint |
| 3A-1 | MAJOR | main.py:45 | Add `threading.Lock` around all state-mutating POST endpoints. Production-ready for eventual live play. |

**Tests:** ~15 new tests. Parser enemy name handling, MODERATE defiance triggering, vindication decay reset, error handling returns, input validation.

**Files touched:** `llm_client.py`, `executor.py`, `defiance.py`, `turn_manager.py`, `world_state.py`, `dispatch.py`, `marshal.py`, `main.py`, `prompt_builder.py`

---

### Session 10: Godot UI + Endgame Flow [P2]

**22 bugs. Mostly GDScript (no pytest). Manual verification via curl + Godot.**

| Bug | Sev | File | Fix |
|-----|-----|------|-----|
| 1A-1 | MAJOR | war_detail_popup.gd:239 | Swap FR/enemy label positions to match fill direction |
| 1A-2 | MAJOR | alliance_paradox_popup.gd:52 | Add `_disable_buttons()` on choice |
| 1B-1 | MAJOR | map.gd:222 | Add all 5 capitals from NATION_CAPITALS, use explicit gold constant |
| 1B-2 | MAJOR | map.gd:374,682,1018,1086 | Clamp tooltip position against viewport bounds |
| 4C-1 | MAJOR | main.gd:1636 | Change `"player_marshals"` → `"marshals"` |
| 4C-2 | MAJOR | dispatch.py:540 | Shift turn limit warning thresholds by one |
| 1A-3 | MINOR | incoming_proposal_popup.gd:41 + main.py | Add `proposal_type_display` to backend popup data, use in popup |
| 1A-4 | MINOR | coalition_declaration_popup.gd:49 | Disable Continue button before hide |
| 1A-7 | MINOR | interrupt_popup.gd:84 | Disable all buttons before hiding |
| 1A-8 | MINOR | clarification_popup.gd:88 | Disable all buttons before hiding |
| 1B-3 | MINOR | map.gd:546 | Remove debug print statements |
| 1B-5 | MINOR | map.gd:1282 | Remove dead `update_region()` method |
| 1B-6 | MINOR | map.gd:504 | Remove debug print from click handler (keep handler for future use) |
| 1B-7 | MINOR | map.gd | Add watchtower indicator to region tooltip |
| 1C-2 | MINOR | strategic_ledger.gd:141 + diplomatic_ledger.gd:154 | Add `scroll_container.scroll_vertical = 0` on tab switch |
| 1C-3 | MINOR | war_status_panel.gd:126 + war_detail_popup.gd:155,370 | Add `remove_child()` before `queue_free()` |
| 4C-3 | MINOR | main.gd:1389 | Add rendering for `turn_limit_warning`, `talleyrand_report`, `coalition_status` dispatch sections |
| 4C-5 | MINOR | executor.py:1018 | Add `game_over`/`victory` keys to explicit `_execute_end_turn` result |
| 4D-4 | MINOR | executor.py:3654 | Add warning when intended target matched a friendly marshal |
| 1A-5 | NOTE | incoming_proposal_popup.gd:40 | Guard personality parentheses for empty string |
| 1A-6 | NOTE | coalition_declaration_popup.gd:35 | Guard empty members list |
| 1C-5 | NOTE | campaign_log.gd:88 | Add `scroll_container.scroll_vertical = 0` on re-open |

**Tests:** Backend-side tests for 4C-2, 4C-5, 4D-4 (~8 tests). GDScript changes verified manually.

**Files touched:** Multiple .gd files, `executor.py`, `dispatch.py`, `main.py`

---

### Session 11 (Optional): Remaining NOTEs & Polish [P3]

**~15 items. Trivial cleanups, dead code, cosmetics.**

| Bug | Sev | Description |
|-----|-----|-------------|
| 1B-4 | NOTE | Remove dead debug block (wrong data path) |
| 1B-8 | NOTE | Dedup Array → Dictionary (optional perf) |
| 1B-9 | NOTE | Tooltip height overestimates 8px |
| 1B-10 | NOTE | Fogged/region tooltip height mismatches |
| 1C-4 | NOTE | Docstring "1-5" → "1-6" |
| 1C-6 | NOTE | Stop threat pulse timer when hidden |
| 1C-9 | NOTE | Merge duplicate COLOR_GREEN/COLOR_SUCCESS |
| 2A-5 | NOTE | Gate debug prints (if not done in S6) |
| 6A-4 | NOTE | Fix comment severity misclassification |
| 6A-5 | NOTE | Remove dead `is_player_marshal` variable |
| 6A-6 | NOTE | Fix comment "MEDIUM" → "NORMAL" |
| 6A-7 | NOTE | Enforce notification cap in `from_list` |
| 6A-8 | — | *(Moved to Session 6 — wire up CS notification)* |
| 6D-6 | NOTE | Strip trailing punctuation in `_clean_target_text` |
| 2D-7 | NOTE | Add `diplomatic_downgrade` to campaign log whitelist |

**No tests required.** Pure cleanup.

---

## Session Summary

| Session | Priority | Bugs | Theme | Key Files |
|---------|----------|------|-------|-----------|
| **S1** | P0 | 8 | War-state foundation + critical AI | world_state, executor, enemy_ai |
| **S2** | P0 | 14 | War-state cascade (executor) | executor |
| **S3** | P0 | 19 | War-state cascade (other files) | 6 files |
| **S4** | P1 | 15 | Auto-action bypasses | executor, world_state |
| **S5** | P1 | 12 | Strategic orders + combat | executor, strategic, combat |
| **S6** | P1 | 11 | Fog, dispatch & integration | main, dispatch, notifications |
| **S7** | P1 | 13 | Diplomacy, dialogue & economy | diplomacy, ledger, vassal |
| **S8** | P2 | 14+ | Save/load, modding & campaign log | save_manager, validator, campaign_log |
| **S9** | P2 | 13 | Parsing, trust & error handling | llm_client, executor, defiance |
| **S10** | P2 | 22 | Godot UI + endgame flow | multiple .gd files |
| **S11** | P3 | ~14 | Optional polish & NOTEs | various |

**Total:** ~158 actionable audit items across 10 required sessions + 1 optional.
**Estimated new tests:** ~185 (backend) + manual verification (Godot).
