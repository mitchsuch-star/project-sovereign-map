# Deep Audit Fix Plan

**Source:** `audit-report-deep.md` (508 raw findings, ~300 unique after dedup)
**Created:** March 23, 2026
**Audit quality:** 8/10 — thorough, evidence-based, ~15-20 findings with inflated severity

## Decisions

- **Spec divergences:** Code is correct (intentional balance refinements R5a/R11/R58/R141-R150). Update spec docs to match code.
- **AI fog omniscience:** By design per FOG_OF_WAR_SPEC §9.1. Toggle point exists (`get_visible_enemies_near()`). Deferred to 80+ region map (EA 1805). Noted in Session 9.
- **Dead code:** Clean up in Session 9 (low risk, high hygiene value).
- **Treaty break drop:** Keep current 2-level drop (ALLIANCE→NON_AGGRESSION). Update spec to match code. More punishing = better for gameplay weight.
- **Personality placeholders (balanced/loyal):** Keep in enum (serialization + modding safety). No marshal uses them. Jealousy system is the natural time to fill or remove. Leave alone for now.

## Severity Re-Classification

Some audit findings re-classified after review:
- P34-1 (AI fog): CRITICAL → DEFERRED (by design)
- P44-1 (coalition cooldown override edge): CRITICAL → LOW (guarded by rarity)
- P1 (coalition leader empty string): CRITICAL → LOW (guarded by form_coalition)
- P56-* (modding validator): CRITICAL → MAJOR (enhancement, not crash in normal gameplay)
- P89-* (personality completeness): LOW → DEFERRED (balanced/loyal are intentionally deferred)

---

## Session 1: Core Combat & War Score — COMPLETE

**Theme:** The biggest gameplay-impacting bugs. Combat math and war score recording.
**Status:** 9 fixes applied, 21 new tests (`test_deep_audit_session1.py`), 2 existing tests updated. 6550 total passing.

| # | Finding | Status | Notes |
|---|---------|--------|-------|
| 1 | **P26-1: Defense modifier inverted by division** | **FALSE POSITIVE** | Division by >1 correctly reduces damage. `get_defense_modifier()` returns 1.15 for DEFENSIVE stance; dividing makes multiplier smaller → fewer casualties. Tests confirm correct behavior. |
| 2 | **P3/P9: ALL battle casualties = 0 for war score** | **FIXED** | `battle_result.get("attacker", {}).get("casualties", 0)` — casualties nested under attacker/defender dicts. 3 tests. |
| 3 | **P75-1: defiance_succeeded() reads non-existent "won" field** | **FIXED** | Changed to `battle_result.get("attacker_won", False)` — correct top-level key from combat.py:760. 3 tests + 1 existing test updated. |
| 4 | **P26-3: 60% casualty cap** | **SKIPPED** | Cap exists only in unused legacy `_calculate_casualties()`, not in main `resolve_battle()` path. N/A. |
| 5 | **P31-1: Square formation blocks coordination** | **FIXED** | Removed `is_in_square` from attack coordination and adjacent ally filters. 2 tests + 1 existing test updated. |
| 6 | **P2: Glorious charge missing record_diplo_battle** | **FIXED** | Added war score recording after `world.record_battle()`. 2 tests. |
| 7 | **P3: Garrison combat not recorded for war score** | **FIXED** | Added `record_diplo_battle()` to both garrison-falls and garrison-holds paths. 2 tests. |
| 8 | **P20: Movement engagement treats allies as enemies** | **FIXED** | Added `world.is_at_war()` check to `enemies_here` and `enemies_at_dest` filters. 3 tests. |
| 9 | **P82-1/2: Fortified marshals move/attack via strategic** | **FIXED** | Added separate fortified check before objection block (runs for strategic execution). Also removed `not is_strategic_execution` from existing check. 2 tests. |
| 10 | **P63-1: DEFEND no-op checked after objection** | **FIXED** | Added pre-validation check for defensive+fortified before objection block. 1 test. |
| — | **Dead code: defender_coord unused variable** | **FIXED** | Removed assignment, kept function call (has side effects). 0 tests (style only). |

---

## Session 2: Vassal System — COMPLETE

**Theme:** Vassal creation, loyalty, cooldowns, and cleanup are broken at multiple levels.
**Status:** 18 fixes applied (Fix 5 confirmed false positive), 27 new tests (`test_deep_audit_session2.py`), 5 existing tests updated. 6577 total passing.

| # | Finding | Status | Notes |
|---|---------|--------|-------|
| 1 | **P3/P9: _ratify_treaty doesn't call create_vassal_treaty** | **FIXED** | Call `create_vassal_treaty()` + `assimilate_vassal_marshals()` BEFORE state transition. 2 tests. |
| 2 | **P32-1: Battle field mismatch in vassal loyalty** | **FIXED** | Use correct field names from `record_battle()`: `attacker`/`defender`/`result`. 2 tests + 2 existing updated. |
| 3 | **P3: battles_this_turn cleared before vassal loyalty** | **FIXED** | Moved `clear_turn_battles()` to after vassal processing. 1 test. |
| 4 | **P1/P32-3: Release cooldown off-by-one (5→4 turns)** | **FIXED** | Decrement ALL first, then remove expired (<= 0). 2 tests. |
| 5 | **P32-4: Investment cooldown off-by-one (3→2 turns)** | **FALSE POSITIVE** | Code already decrements first then checks `<= 0`. Correct. |
| 6 | **P2: Conquest vassalization skips release cooldown** | **FIXED** | Added cooldown check matching treaty path. 1 test. |
| 7 | **P2: Popup text says +15 loyalty, actual +10** | **FIXED** | Updated popup and dialogue text to "+10". 1 test. |
| 8 | **P2: release_vassal doesn't clear stale popup/dialogue** | **FIXED** | Clears matching popup/dialogue on release. 2 tests. |
| 9 | **P3: Voluntary release doesn't clean relationship_with_lord** | **FIXED** | Added `delattr` for `relationship_with_lord`. 1 test. |
| 10 | **P32-2: Trust encapsulation violation in assimilation** | **FIXED** | Uses `marshal.trust.modify()` instead of `_value`. 1 test. |
| 11 | **P2: garrison_vassal_rebellion on removed vassal** | **FIXED** | Added existence check before garrison. 1 test. |
| 12 | **P2: invest_in_vassal uses player DP regardless of lord** | **FIXED** | Added lord validation guard. 1 test. |
| 13 | **P68-4: Vassal conquest no pre-state validation** | **FIXED** | Requires WAR state. 2 tests + 3 existing updated. |
| 14 | **P3: vassal_rebellion_imminent_popup not cleared after response** | **FIXED** | All 3 handlers clear popup. 3 tests. |
| 15 | **P3: Vassal tribute preview always shows 0** | **FIXED** | Computes tribute live from `tribute_rate * regional_income`. 1 test. |
| 16 | **P54-2: Vassal rebellion doesn't trigger war cascade** | **FIXED** | Calls `_process_war_cascade()` after WAR state set. 1 test. |
| 17 | **P54-4: Coalition loyalty penalty not in vassal loyalty** | **FIXED** | Applies `get_coalition_loyalty_penalty()` as modifier 7. 1 test. |
| 18 | **P96-3: Defection cascade reduces loyalty instead of immediate rebellion** | **FIXED** | Sets loyalty to `LOYALTY_MIN` (0) per spec. 1 test. |
| 19 | **P86-3: Vassal garrison loyalty bonus base 2 vs spec 5** | **FIXED** | Base 5, cap 8 matching spec. 3 tests + 2 existing updated. |

---

## Session 3: Diplomatic State Machine & War Score Sign — COMPLETE

**Theme:** State transition bugs and the systemic war score sign issue.
**Status:** 13 fixes applied (4 false positives, 1 subsumed, 1 doc-only), 25 new tests (`test_deep_audit_session3.py`), 1 existing test updated. 6602 total passing.

| # | Finding | Status |
|---|---------|--------|
| 1 | **War score sign bug (5 locations)** — `get_war_score_for()` replaces raw `war_scores.get()` | FIXED |
| 2 | **Stale proposal bypasses state changes** — upgrade-order validation before acceptance | FIXED |
| 3 | **break_treaty missing WAR/ARMISTICE cleanup** — `post_break_map` + `cleanup_war_end()` | FIXED |
| 4 | **Ultimatum acceptance bypasses state machine** — `cleanup_war_end()` + treaty cleanup | FIXED |
| 5 | **Auto-downgrade doesn't remove active treaty** — `active_treaties.pop()` | FIXED |
| 6 | **Armistice→WAR doesn't remove active treaty** — `active_treaties.pop()` | FIXED |
| 7 | **No self-war prevention** — early guard in `declare_war()` | FIXED |
| 8 | **get_game_bucket() manual sign logic** — subsumed by Fix 1 | SUBSUMED |
| 9 | **AI break_treaty adds coalition threat** — player-only guard | FIXED |
| 10 | **ARMISTICE missing from _DOWNGRADE_ORDER** — intentional, added comment | DOC-ONLY |
| 11 | **"Accepted" message when _ratify_treaty fails** — check result before success msg | FIXED |
| 12 | **break_treaty doesn't void proposal_in_transit** — clear matching proposals | FIXED |
| 13 | **VASSAL missing from _DOWNGRADE_ORDER** | FALSE POSITIVE |
| 14 | **VASSAL→NON_AGGRESSION not in validate_transition** — added to exit states | FIXED |
| 15 | **_process_relation_decay skips ALL vassal pairs** — now only skips lord-vassal | FIXED |
| 16 | **Offensive cascade doesn't skip vassals** | FALSE POSITIVE |
| 17 | **Casus belli doesn't halve coalition threat** — `threat = 10 if casus_belli else 20` | FIXED |
| 18 | **Continental system cleanup on vassal release** | FALSE POSITIVE (fixed in Session 2) |
| 19 | **Armistice_turns not cleared on war restart** | FALSE POSITIVE (already `.pop()`) |

---

## Session 4: DP, AP, Gold & Economy — COMPLETE

**Theme:** Economy-breaking bugs in treaty clauses, DP costs, and gold handling.
**Status:** 9 fixes applied, 6 false positives confirmed, 16 new tests (`test_deep_audit_session4.py`), 1 existing test updated. 6618 total passing.

| # | Finding | Status | Notes |
|---|---------|--------|-------|
| 1 | **P104-1: AP clause cumulative permanent reduction** | **FIXED** | Reset nation_actions to base values before `_process_treaty_clauses()` in `advance_turn()`. 2 tests. |
| 2 | **P21/P38: nation_manpower doesn't exist** | **FIXED** | Replaced all 5 `self.nation_manpower` → `self.manpower_pools`. 1 test. |
| 3 | **P1: Gold lump sum bankruptcy** | **FIXED** | Added floor check + nested credit inside debit. 2 tests. |
| 4 | **P1: AI counter-offer DP not refunded** | **FALSE POSITIVE** | Each action has own DP cost — working correctly. |
| 5 | **P50-1: Alliance paradox honor/break free DP** | **FALSE POSITIVE** | Reactive system, no DP cost by design. |
| 6 | **P19-1: Vassalage DP cost shown as 1 instead of 3** | **FIXED** | Added `"propose_vassalage": 3` to `base_costs` dict. 2 tests. |
| 7 | **P19-2: _state_map missing vassalage→VASSAL** | **FALSE POSITIVE** | Already present at line 4219. |
| 8 | **P12: Counter-offer Talleyrand state overridden** | **FIXED** | Guard restore block with `outcome != "COUNTER_OFFER"`. 2 tests. |
| 9 | **P2: Territory sweetener inflated 5x** | **FIXED** | `max(1,...)` for territory, `max(5,...)` for gold only. 2 tests. |
| 10 | **P61-1: Vassal tribute hardcoded 50g** | **FALSE POSITIVE** | Simplified by design. |
| 11 | **P61-3: Continental System double-penalizes** | **FALSE POSITIVE** | Both parties lose trade — correct. |
| 12 | **P12: Negative treaty clause amount reverses transfer** | **FIXED** | Added `abs()` on amount in both one-time and per-turn clause loops. 2 tests. |
| 13 | **P12: Free gold creation when from_nation eliminated** | **FIXED** | Nested credit inside debit (Fix 3) + removed else branch in per-turn. 1 test. |
| 14 | **P104-2: AP clause against France silently ignored** | **FIXED** | Apply to `max_actions_per_turn` when `from_nation == player_nation`. 2 tests. |
| 15 | **P1: Trade income not in strategic ledger** | **FALSE POSITIVE** | Documented deferral (TODO comment). |

---

## Session 5: AI, Parser & Strategic Orders — COMPLETE

**Theme:** AI decision-making bugs, missing VALID_ACTIONS, and strategic order persistence.
**Status:** 13 fixes applied (6 false positives removed), 31 new tests (`test_deep_audit_session5.py`), 2 existing tests updated. 6649 total passing.

**Fixes applied:**
1. SUPPORT path persisted on `order.path` (strategic.py)
2. HOLD path persisted on `order.path` (strategic.py)
3. AI ally support only targets nations at war (enemy_ai.py)
4. `release_vassal` added to VALID_ACTIONS + META_ACTIONS (validation.py)
5. 5 diplomatic actions added to VALID_ACTIONS + META_ACTIONS (validation.py)
6. Diplomatic defiance pipeline wired between DP deduction and transit (executor.py)
7. Stalemate counter already cleared (verified — was in Session 4 fix R110)
8. Zero-income nations skip income cap for sweeteners (ai_diplomacy.py)
9. "stand down" routes to stance_change neutral, not cancel (llm_client.py)
10. P7 artillery rebuild uses correct cost base (enemy_ai.py)
11. AI proposal metadata only recorded after acceptance check passes (ai_diplomacy.py)
12. Vassal auto-joins lord's offensive war in cascade (diplomacy.py)
13. PURSUE breaks on peace, SUPPORT breaks on war with ally (strategic.py)

**False positives (6):** P72-1 (PURSUE recalculates by design), P72-4 (issued_turn low priority), P72-5 (already serialized), P2-8/P2-9 (AI-AI bypass by design), P59 (handled in ai_diplomacy.py:421).

---

## Session 6: Popups, Passthroughs & Security

**Theme:** Popup field mismatches, passthrough gaps, and the one real security issue.

| # | Finding | File | Fix |
|---|---------|------|-----|
| 1 | **P3/P11/P48: War declaration Talleyrand objection wrong fields** | executor.py:11628-11636 | Rename to `concern_level`, `objection_text`, `defiance_risk`, `proposal_summary` |
| 2 | **P3: War declaration objection "Proceed" misroutes** | main.gd:2793 | Send action-specific command, not generic "proceed with proposal" |
| 3 | **P3: War declaration objection infinite re-trigger** | executor.py:11625-11641 | Add override flag or check pending_diplomatic_dialogue |
| 4 | **P57-1: Sabotage handler field name typo** | executor.py:12718 | `world.diplomatic_sabotage_popup = None` (not `diplomatic_sabotage`) |
| 5 | **P57-2: Redemption handler field name typo** | executor.py:12742 | `world.talleyrand_redemption_popup = None` (not `talleyrand_redemption`) |
| 6 | **P48-2: Alliance paradox popup has no Godot handler** | main.gd | Implement popup scene or route through existing dialog |
| 7 | **P1: Popup passthrough gaps (42+ missing returns)** | main.py | Add `_include_popup_passthroughs()` to all POST endpoint return paths |
| 8 | **P43-3: Non-blocking dialogue doesn't clear popup** | world_state.py:3859-3862 | Add `self.incoming_proposal_popup = None` |
| 9 | **P93-1: Path traversal in /load and /delete_save** | main.py:1664,1688 | Reject filenames containing `..`, `/`, `\`; verify resolved path starts with saves dir |
| 10 | **P80-1: "Game state error" zero diagnostic value** | main.py | Include endpoint name and context in error messages |
| 11 | **P52-2: /debug_marshal missing DEBUG_MODE guard** | main.py:1505-1557 | Add guard |
| 12 | **P17: Armistice expiration no notification/dispatch** | diplomacy.py:1644-1702 | Add `notifications.add()` + `queue_dispatch_event()` for both paths |
| 13 | **P2: "stalled" sabotage type has no effect** | diplomatic_defiance.py:235-237 | Implement delivery delay (add 1 turn) |
| 14 | **P2: Territory sabotage leaves empty regions list** | diplomatic_defiance.py:211-214 | Remove demand if regions becomes empty |

**Tests:** ~20 new tests.

---

## Session 7: Fog of War, Dispatch & Region Fixes

**Theme:** Information leaks, dispatch display bugs, campaign log gaps, and region data fixes.

| # | Finding | File | Fix |
|---|---------|------|-----|
| 1 | **P13/P94-1: Coalition member strength/gold exposed** | dispatch.py:846-856 | Use fog-filtered strength display, remove gold field |
| 2 | **P62-1: Talleyrand suggestions leak all nations** | dispatch.py:541-660 | Replace hardcoded list with `get_known_nations(world)`, add visibility check |
| 3 | **P62-3: AI-AI diplomatic states leak via ledger** | diplomatic_ledger.py:198-218 | Require BOTH nations visible (AND not OR) |
| 4 | **P40-2: Dispatch fog filter missing "aggressor" key** | dispatch.py:994-998 | Add `"aggressor"` to nations_to_check |
| 5 | **P40-3: Hardcoded known_nations in dispatch** | dispatch.py:541 | Use `get_known_nations(world)` |
| 6 | **P94-3: Campaign log event type mismatch** | campaign_log.py:83-110 | Add `"war_declaration"`, `"defensive_cascade"`, `"offensive_cascade"` to types |
| 7 | **P94-4: Coalition events never appear in campaign log** | campaign_log.py | Add `"coalition_declared"`, `"coalition_dissolved"` to CAMPAIGN_LOG_TYPES |
| 8 | **P39-1: Static KNOWN_NATIONS in diplomatic_advisory** | diplomatic_advisory.py:700 | Use `get_known_nations(world)` |
| 9 | **P67-1/P44-1: Britain Netherlands missing is_capital** | region.py:347-355 | Set `"is_capital": True` |
| 10 | **P67-2: Netherlands supply capacity (rural→capital)** | region.py:347-355 | Set `"region_type": "capital"` |
| 11 | **P67-3: Dresden region type (town→capital)** | region.py:473-481 | Set `"region_type": "capital"` |
| 12 | **P22: Coalition threat uses full clause count** | world_state.py:4314-4321 | Track actually-transferred count for threat math |
| 13 | **P13: Coalition member WE without PARTIAL+ check** | dispatch.py:853, diplomatic_ledger.py:440-452 | Add visibility check |
| 14 | **P39-2: Empty threat_entries IndexError** | diplomatic_advisory.py:282 | Add `if not threat_entries: return` guard |
| 15 | **P65-1: Threat score double-counting military strength** | diplomatic_advisory.py:266-269 | Change `if` to `elif` |

**Tests:** ~15 new tests.

---

## Session 8: Godot Frontend Fixes

**Theme:** Godot-side bugs. No Python tests (GDScript only). Manual test verification.

| # | Finding | File | Fix |
|---|---------|------|-----|
| 1 | **P25-1/P77-1: Popup early returns skip ALL state updates** | main.gd:786-841 | Call `_process_active_wars()` + state update before each early return |
| 2 | **P25-6: Diplomatic ledger threat tier no default** | diplomatic_ledger.gd:415-424 | Add `_:` default with neutral color |
| 3 | **P25-5: Float→Int in war status panels** | war_status_panel.gd, war_detail_popup.gd | Add defensive `int(float())` casts |
| 4 | **P77-6: war_detail_popup missing from _is_modal_dialog_open()** | main.gd:2831-2870 | Add to modal check list |
| 5 | **P77-7: Coalition popup dismissal no war panel refresh** | main.gd:2726-2730 | Call `_process_active_wars()` |
| 6 | **P100-1/2: Bare response.message in ~12 error paths** | main.gd | Convert to `.get("message", "An error occurred")` |
| 7 | **P25-7: Wizard error state back button broken** | diplomacy_wizard.gd:140-152 | Reset `_current_step` in error handler |
| 8 | **P79-1: Wizard double-open during HTTP** | diplomacy_wizard.gd | Add `_request_in_flight` guard |
| 9 | **P42-3: Talleyrand objection "Modify" input race** | main.gd:2794-2797 | Hide popup before re-enabling input |
| 10 | **P25-4: War detail popup silent closure** | war_detail_popup.gd:105-106 | Show "This war has ended" message |
| 11 | **P42-7: Diplomacy wizard ESC handling** | main.gd:587 | Add wizard to ESC close handler |
| 12 | **P55-1: diplomatic_ledger.gd null crash on history type** | diplomatic_ledger.gd:689 | Null check before `.to_lower()` |
| 13 | **P55-3: Coalition declaration popup type coercion** | coalition_declaration_popup.gd:41 | Cast to int before %d format |
| 14 | **P79-2: Wizard doesn't check pending_diplomatic_dialogue** | diplomacy_wizard.gd | Check backend state before opening |

---

## Session 9: Spec Docs, Dead Code & Polish

**Theme:** Update spec docs to match code, remove dead code, minor hardening.

### Spec Doc Updates (code is correct, update docs)

| Spec | Section | Current Doc | Actual Code | Action |
|------|---------|-------------|-------------|--------|
| DIPLOMACY_SPEC | S7 sweetener values | AP: +8 | AP: +18 | Update spec "Buffed per R141-R150" |
| DIPLOMACY_SPEC | R146 sweetener cap | 40 | 60 | Update spec "Raised per R146 balance pass" |
| DIPLOMACY_SPEC | §5b armistice duration | 3 turns | 5 turns | Update spec "Extended per R5a" |
| DIPLOMACY_SPEC | S4a base DP | 2/turn | 3/turn | Update spec |
| DIPLOMACY_SPEC | S4a skill bonus | skill 10 only | skill >= 8 | Update spec |
| DIPLOMACY_SPEC | worked example | relation/2 = -30 | relation/4 capped ±10 | Update example per R141 |
| COALITION_SPEC | §10a WE per-turn | +5 | +8 | Update spec "Per R11" |
| COALITION_SPEC | §6b decisive battle | >5000 | >10000 | Update §6b to match §2a and code |
| V2B_DEFIANCE_SPEC | §2 vindication decay | 3 turns | 5 turns | Update spec "Per R58" |
| COALITION_SPEC | §6b shock bonus | +5 to defeated member | skips defeated | Document as design choice |
| DIPLOMACY_SPEC | §5c casus belli threat | +10 with casus belli | Always +20 | Add TODO or implement |
| DIPLOMACY_SPEC | §7d post-break drop | 1 level | 2 levels | Update spec — 2-level drop is better for gameplay weight |

### Dead Code Removal (Pass 83)

| # | Item | File | Lines |
|---|------|------|-------|
| 1 | Orphaned battle tracking (3 methods) | world_state.py:1296,1347,1380 | ~90 lines |
| 2 | Orphaned pathfinding/threat (3 methods) | world_state.py:1763,1793,1820 | ~80 lines |
| 3 | `_find_best_action` | enemy_ai.py:1058 | ~36 lines |
| 4 | `defender_coord` (computed, never read) | executor.py:4238 | ~5 lines |
| 5 | `resolve_battle_vindication` wrapper | executor.py:13970 | ~8 lines |
| 6 | `VindicationTracker.apply_decay()` | vindication.py:227 | ~26 lines |
| 7 | Flavor text functions (3) | enemy_ai.py:5477,5505,5531 | ~70 lines |
| 8 | `get_ambiguity_behavior` + `should_skip_validation` | validation.py:186,209 | ~30 lines |
| 9 | `_get_stalemate_turns` | ai_diplomacy.py:354 | ~8 lines |
| 10 | `get_stance_display` | marshal.py:946 | ~10 lines |
| 11 | `full_game.py` (entire file) | backend/full_game.py | ~16 lines |
| 12 | `test_new_features.py` in commands/ | backend/commands/test_new_features.py | whole file |
| 13 | `defiant_command` assigned never used (2 loc) | executor.py:10763,13479 | ~10 lines |
| 14 | `_get_fogged_strength_display` | diplomatic_advisory.py:610 | ~15 lines |
| 15 | V1 disobedience dead functions (2) | disobedience.py:335,468 | ~130 lines |
| 16 | Coalition template accessors (2) | diplomatic_templates.py:940,945 | ~10 lines |

### Minor Hardening

| # | Finding | Fix |
|---|---------|-----|
| 1 | P53-2: No atomic writes in save_manager | Use temp-file + rename pattern |
| 2 | P29-3: Enum deserialization crash on corrupt values | Wrap Stance() in try-except |
| 3 | P29-1: Coalition from_dict shallow copy | Use `copy.deepcopy()` |
| 4 | P53-1: DiplomaticRepresentative missing from serialization test | Add to SERIALIZABLE_CLASSES |
| 5 | P6: _we_dispatched_thresholds not serialized | Add to WorldState serialization |
| 6 | P73-1: Direct trust._value access (3 locations) | Route through `trust.modify()` |
| 7 | P73-3: Missing self-relationship guard | Add `if other_name == self.name: return` |

### AI Fog of War (DEFERRED — noted for future)

Per FOG_OF_WAR_SPEC §9.1: AI omniscience is by design at 19 regions. Toggle point exists: `get_visible_enemies_near()` in `objection_v2.py`. When 80+ region map ships (EA 1805):
- Switch `enemy_ai.py` target selection to use `get_visible_enemies_near()` (4 call sites in `_find_ally_support_opportunity`, plus P4/P5 targeting)
- Give AI bonuses (wider adjacency, faster intel updates) per §9.5
- Add fog-filtered objection helpers per V2B_DEFIANCE_SPEC §4

---

## Items NOT Fixed (Intentional Deferrals)

| Finding | Reason |
|---------|--------|
| P89-*: balanced/loyal personality completeness | Intentionally deferred — Jealousy system will add personality expression |
| P45-*: Performance hotspots | Not blocking at 19 regions. Monitor for EA 1805 |
| P7: Architecture (function length, imports) | Refactoring out of scope for bugfix sessions |
| P88-*: Race conditions | Single-player single-client; Godot serializes requests |
| P102-4: Templates T11-T27 dead code (~560 lines) | Low priority; may be used for LLM integration later |
| P97-*: Dialogue state machine edge cases | LOW severity, working in practice |
| P2: Multi-rebellion cascade stacking | Minor edge case, by-turn design handles it |
| P56-*: Most modding validator improvements | Enhancement, not bug. Fix top 3 (float strength, terrain, region type) in Session 9 hardening |

---

## Estimated Totals

| Session | Fixes | New Tests | Focus |
|---------|-------|-----------|-------|
| 1 | ~10 | ~30 | Combat & war score |
| 2 | ~19 | ~30 | Vassal system |
| 3 | ~19 | ~30 | Diplomatic state machine |
| 4 | ~15 | ~20 | Economy (DP/AP/gold) |
| 5 | ~19 | ~25 | AI, parser, strategic orders |
| 6 | ~14 | ~20 | Popups, passthroughs, security |
| 7 | ~15 | ~15 | Fog leaks, dispatch, regions |
| 8 | ~14 | 0 (Godot) | Frontend fixes |
| 9 | ~30 | ~10 | Spec docs, dead code, polish |
| **Total** | **~155** | **~180** | |

Remaining ~145 findings are: duplicates across passes (~40), informational/architectural notes (~20), intentional deferrals (~20), LOW severity items (~35), or items implicitly fixed by related changes (~30).
