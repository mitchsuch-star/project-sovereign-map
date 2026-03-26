# Systems Audit V3 — Deep Exploration + Continuous Playtesting
**Started:** 2026-03-25
**Scope:** Godot deep dive, backend integration seams, cross-cutting concerns, simulated playtests
**Prior audits:** V1 (275 findings, all fixed), V2 (99 findings, all fixed)
**Purpose:** Explore untouched areas, stress-test integration points, simulate real gameplay to find logical gaps

---

## Phase 1: UNEXPLORED TERRITORY — Godot Deep Dive

### [1A-1] [WAR_DETAIL_POPUP] Tug-of-war bar side labels are swapped
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** war_detail_popup.gd:239-258
- **Description:** The "FR" (France) label is placed at position x=3 (LEFT edge) and the enemy abbreviation is placed at position bar_width-22 (RIGHT edge). But the fill logic places France's blue fill to the RIGHT of center and enemy's red fill to the LEFT of center. This means the labels are on the opposite side from their corresponding fill colors, creating a confusing visual where France's label is on the enemy's side of the bar and vice versa.
- **Evidence:**
  ```gdscript
  # Fill logic: France fills RIGHT, enemy fills LEFT
  if normalized > 0:  # France winning
      fill.position = Vector2(int(half_w), 0)  # Starts at center, goes RIGHT
  elif normalized < 0:  # Enemy winning
      fill.position = Vector2(int(half_w) - fill_width, 0)  # LEFT of center
  # Labels: France LEFT, enemy RIGHT (SWAPPED!)
  france_lbl.position = Vector2(3, 0)  # LEFT edge
  enemy_lbl.position = Vector2(bar_width - 22, 0)  # RIGHT edge
  ```
- **Proposed Fix:** Swap the label positions so FR is on the right (matching blue fill direction) and enemy abbreviation is on the left.

### [1A-2] [ALLIANCE_PARADOX_POPUP] No button disabling on click allows double-fire
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** alliance_paradox_popup.gd:52-59
- **Description:** Unlike every other choice popup (incoming_proposal, talleyrand_objection, sabotage_discovery, vassal_rebellion, talleyrand_redemption), the alliance_paradox_popup does not disable its buttons when a choice is made. The `_on_honor_pressed` and `_on_break_pressed` handlers call `hide()` and `emit()` but never disable buttons. Fast double-click fires the signal twice, causing the backend to receive two dialogue responses.
- **Proposed Fix:** Add `_disable_buttons()` method matching the pattern of other popups.

### [1A-3] [INCOMING_PROPOSAL_POPUP] Raw internal proposal_type shown instead of display name
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** incoming_proposal_popup.gd:41
- **Description:** The popup displays `proposal_type.replace("_", " ").capitalize()` which produces poorly formatted names like "Non aggression" instead of the proper display names "Non-Aggression Pact". Backend has `PROPOSAL_TYPE_DISPLAY` with proper names but doesn't include them in popup data.
- **Proposed Fix:** Add `proposal_type_display` to backend popup data dict and use it in the popup.

### [1A-4] [COALITION_DECLARATION_POPUP] No button disabling on Continue allows double-fire
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** coalition_declaration_popup.gd:49-51
- **Description:** The Continue button is not disabled after being pressed. Double-click fires `dismissed` twice, causing duplicate "The coalition has declared war on France" message in terminal.
- **Proposed Fix:** Disable `continue_btn` before `hide()`.

### [1A-5] [INCOMING_PROPOSAL_POPUP] Empty parentheses shown when diplomat_personality is empty
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** incoming_proposal_popup.gd:40
- **Description:** If `diplomat_personality` is empty string, popup displays `"An envoy () of Unknown"` with empty parentheses.
- **Proposed Fix:** Conditionally include personality parentheses.

### [1A-6] [COALITION_DECLARATION_POPUP] Empty "Members:" section shown when members list is empty
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** coalition_declaration_popup.gd:35-41
- **Description:** If `members` array is empty, popup displays "Members:" with nothing listed.
- **Proposed Fix:** Guard with `if not members.is_empty()`.

### [1A-7] [INTERRUPT_POPUP] No button disabling on option selection allows double-fire
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** interrupt_popup.gd:84-87
- **Description:** Same pattern as alliance_paradox_popup. No button disabling before hide/emit.
- **Proposed Fix:** Disable all buttons before hiding.

### [1A-8] [CLARIFICATION_POPUP] No button disabling on option selection allows double-fire
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** clarification_popup.gd:88-94
- **Description:** Same pattern. Double-fire of `clarification_choice` would cause two commands sent for one clarification.
- **Proposed Fix:** Disable all buttons before hiding.

### [1B-1] [MAP] Capital gold border hardcoded to Paris only
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** map.gd:222-224
- **Description:** The gold capital border is hardcoded to only draw for Paris. The game has 5 capitals (Paris, Netherlands, Berlin, Vienna, Dresden per `NATION_CAPITALS` in region.py), but only Paris gets the visual indicator. The color uses `COLORS["Austria"]` (gold) which is misleading for non-Austrian capitals.
- **Proposed Fix:** Add `const CAPITAL_REGIONS` set mirroring all 5 capitals and check membership. Use explicit gold constant.

### [1B-2] [MAP] No tooltip off-screen clamping
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** map.gd:374,682,1018,1086
- **Description:** All four tooltip functions position at `mouse_position + Vector2(15, 15)` without clamping to viewport bounds. When mouse is near right/bottom edge, tooltip renders off-screen. Especially problematic for tall marshal tooltips (300+ pixels).
- **Proposed Fix:** Clamp tooltip position against viewport size.

### [1B-3] [MAP] Debug print statements fire every frame on hover over fortified marshal
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** map.gd:546-548,587-589,595
- **Description:** Six `print()` calls fire on every `_draw()` invocation when hovering over a fortified player marshal. Pollutes console and causes minor performance overhead.
- **Proposed Fix:** Remove debug prints or guard behind `const DEBUG_TOOLTIPS = false`.

### [1B-4] [MAP] Dead debug code checks wrong data path for fortify state
- **Severity:** NOTE
- **Category:** NEW_BUG
- **File:** map.gd:546-548
- **Description:** Debug block checks `hovered_marshal.get("fortified", false)` at top-level but `fortified` is nested under `tactical_state`. Dead code that never fires.
- **Proposed Fix:** Remove dead debug block.

### [1B-5] [MAP] `update_region()` has type mismatch — latent crash
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** map.gd:1282-1292
- **Description:** `update_region()` stores a String into `region_marshals[region_name]`, but `_draw_marshal_icons()` expects an Array. If ever called, `.get("name")` on a String crashes. Currently dead code (no callers).
- **Proposed Fix:** Remove `update_region()` as dead code.

### [1B-6] [MAP] Region click handler is a no-op (TODO stub)
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** map.gd:504-508
- **Description:** `_on_region_clicked()` only prints to console with a TODO comment. No signal emitted, no interaction on click.
- **Proposed Fix:** Implement signal emission or remove print.

### [1B-7] [MAP] Watchtower data sent by backend but never displayed on map
- **Severity:** MINOR
- **Category:** INTEGRATION
- **File:** map.gd (missing), world_state.py:3283-3285
- **Description:** Backend includes `watchtower` and `watchtower_turns_remaining` in region data. Godot never reads or displays it. Players can't see which regions have active watchtowers from the map view.
- **Proposed Fix:** Add watchtower indicator to `_draw_region_tooltip()`.

### [1B-8] [MAP] Connection deduplication uses O(n) Array lookup
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** map.gd:182-198
- **Description:** Uses Array with `in` operator for deduplication (O(n) per lookup). Minor at 35 edges but Dictionary would be O(1).
- **Proposed Fix:** Change to Dictionary. Low priority.

### [1B-9] [MAP] Marshal tooltip height overestimates by ~8px
- **Severity:** NOTE
- **Category:** NEW_BUG
- **File:** map.gd:670
- **Description:** Height formula uses `extra_spacing * 2` = 16px but rendering only adds `+4` per line = 8px total. 8px empty gap at bottom of every marshal tooltip.
- **Proposed Fix:** Align formula with rendering constants.

### [1B-10] [MAP] Fogged/region tooltips also have minor height miscalculations
- **Severity:** NOTE
- **Category:** NEW_BUG
- **File:** map.gd:372,1016,1082
- **Description:** Similar height formula mismatches in fogged and region tooltips. Cosmetic (slightly too-tall).
- **Proposed Fix:** Audit all tooltip height formulas. Low priority.

### [1C-2] [STRATEGIC_LEDGER / DIPLOMATIC_LEDGER] Scroll position not reset on tab switch
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** strategic_ledger.gd:141-146, diplomatic_ledger.gd:154-159
- **Description:** When switching sub-tabs, scroll position persists. If player scrolled down on long tab and switches to short tab, they see blank space. The `diplomacy_wizard.gd` correctly resets `scroll_container.scroll_vertical = 0`.
- **Proposed Fix:** Add `scroll_container.scroll_vertical = 0` after `_render_current_tab()`.

### [1C-3] [WAR_STATUS_PANEL / WAR_DETAIL_POPUP] queue_free() without remove_child() causes frame-flicker
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** war_status_panel.gd:126-128, war_detail_popup.gd:155-157,370-372
- **Description:** When rebuilding, `queue_free()` is called on old children without `remove_child()` first. Since `queue_free()` is deferred, old and new children both appear for one frame. `campaign_log.gd` explicitly documents the correct pattern.
- **Proposed Fix:** Use `remove_child(child)` before `child.queue_free()`.

### [1C-4] [STRATEGIC_LEDGER] Docstring says "1-5" but code handles keys 1-6
- **Severity:** NOTE
- **Category:** NEW_BUG
- **File:** strategic_ledger.gd:77
- **Description:** Docstring says "Handle number keys 1-5" but code handles KEY_1 through KEY_6.
- **Proposed Fix:** Update docstring.

### [1C-5] [CAMPAIGN_LOG] No scroll-to-top on re-open
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** campaign_log.gd:88-141
- **Description:** Opening campaign log doesn't reset scroll position. Over 40 turns, player may not see most recent expanded turn without scrolling.
- **Proposed Fix:** Add `scroll_container.scroll_vertical = 0` after building turns.

### [1C-6] [TOP_BAR] Threat pulse timer continues when hidden
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** top_bar.gd:281-301
- **Description:** Threat pulse timer keeps running even during modal dialogs. Unnecessary processing.
- **Proposed Fix:** Stop timer when not visible. Low priority.

### [1C-7] [PAUSE_MENU] Save signal emits after menu close signal — potential race
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** pause_menu.gd:39-41
- **Description:** `close_menu()` emits `closed` before `save_requested` emits. Fragile ordering.
- **Proposed Fix:** No action needed currently. Document ordering.

### [1C-8] [MARSHAL_MANAGEMENT] Hardcoded 320px scroll target may misalign
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** marshal_management.gd:70-72
- **Description:** Number key scroll jumps use hardcoded `index * 320`. Cards with many relationships/abilities are taller, causing misalignment.
- **Proposed Fix:** Already documented as tech debt.

### [1C-9] [DIPLOMATIC_LEDGER] Duplicate color constant
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** diplomatic_ledger.gd:36
- **Description:** `COLOR_GREEN = "8fbc8f"` duplicates `COLOR_SUCCESS = "8fbc8f"`.
- **Proposed Fix:** Use one name. Low priority.

### [1D-1] [DIPLOMACY] NameError in acceptance_preview: `target` instead of `target_nation`
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** backend/game_logic/diplomacy.py:2856
- **Description:** The acceptance preview code references undefined variable `target` instead of `target_nation` when calling `get_war_score_for()`. This NameError is silently caught by try/except, causing `acceptance_preview` to always be `None` for armistice proposals. The wizard's "KEY FACTORS" section never renders for nations at war, depriving the player of the most strategically important acceptance breakdown.
- **Evidence:**
  ```python
  "propose_armistice": "armistice_winning" if (get_war_score_for(world, player, target) > 0) else "armistice_losing",
  ```
- **Proposed Fix:** Change `target` to `target_nation`.

### [1D-2] [DIPLOMACY_WIZARD] Back button visible but non-functional after Step 2 error
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** diplomacy_wizard.gd:197
- **Description:** When `_show_error()` is called during Step 2, it resets `_current_step` to 1 but does NOT hide the back button. Player sees error + visible Back button that does nothing.
- **Proposed Fix:** Add `back_button.visible = false` to `_show_error()`.

### [1D-3] [DIPLOMACY_WIZARD] Stale response errors bypass staleness check
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** diplomacy_wizard.gd:172-184
- **Description:** Error paths (HTTP error, parse failure, `success: false`) return before reaching the staleness check. Stale error could overwrite current loading state.
- **Proposed Fix:** Move stale check above error handling.

### [1D-4] [DIPLOMACY_WIZARD] DP label shows stale value during loading
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** diplomacy_wizard.gd:75-88
- **Description:** `dp_label` not reset on open. Retains previous value during loading. Also .tscn default "DP: 0/3" doesn't match runtime format "DP: X".
- **Proposed Fix:** Reset dp_label in `open()`.

### [1D-5] [DIPLOMACY] Hardcoded "Vienna" in peace_wary assessment template
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** backend/game_logic/diplomacy.py:2376
- **Description:** Template uses "Vienna watches our moves with calculating eyes" for ALL nations, not just Austria. Breaks immersion for Prussia/Britain.
- **Proposed Fix:** Replace "Vienna" with generic reference.

### [1D-6] [DIPLOMACY_WIZARD] Dialogue_pending auto-close provides no user feedback
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** diplomacy_wizard.gd:218-221
- **Description:** When wizard opens and dialogue is pending, it sets assessment text then immediately closes — player sees wizard briefly flash then close with no explanation.
- **Proposed Fix:** Show terminal message before closing.

---

## Phase 1 Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| MAJOR | 5 |
| MINOR | 12 |
| NOTE | 16 |
| **TOTAL** | **33** |

**Top 5 most impactful findings:**
1. **1D-1** — NameError silently breaks acceptance preview for armistice proposals (MAJOR)
2. **1A-1** — War score bar labels swapped, actively misleading players (MAJOR)
3. **1B-1** — Only Paris gets capital gold border, 4 other capitals invisible (MAJOR)
4. **1B-2** — Tooltips render off-screen at viewport edges (MAJOR)
5. **1A-2** — Alliance paradox popup double-fire sends duplicate backend requests (MAJOR)

---

## Phase 2: UNEXPLORED TERRITORY — Backend Integration Seams

### [2A-1] [FOG] Enemy phase summary leaks fogged action information
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** main.py:276
- **Description:** `_filter_enemy_phase_by_visibility()` filters individual enemy actions by fog visibility, but passes the unfiltered `summary` list through unchanged. The summary is generated from ALL enemy actions regardless of visibility, leaking info about enemy operations in fogged regions.
- **Proposed Fix:** Regenerate summary from only filtered actions after filtering.

### [2A-2] [WAR_PANEL] Missing active_wars data when enemy_phase is present
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** main.py:1008
- **Description:** When `/command` response includes `enemy_phase`, `_include_popup_passthroughs()` is skipped (to defer diplomatic popups), but this also skips adding `active_wars`. The war status panel shows stale data after turns with visible enemy actions — exactly when wars are most likely to change.
- **Proposed Fix:** Add `active_wars` independently when enemy_phase is present.

### [2A-3] [DISPLAY] Talleyrand mission summary shows raw internal type names
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** main.py:127-129
- **Description:** `_get_talleyrand_mission_summary()` passes raw type (e.g., "IMPROVE_RELATIONS") to top bar instead of display name. Produces "IMPROVE_RELATIONS → Prussia" instead of "Improve Relations → Prussia".
- **Proposed Fix:** Add display name mapping.

### [2A-4] [ORDERS_TAB] cancel_order endpoint bypasses diplomatic dialogue guard
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** main.py:1942-1947
- **Description:** `/cancel_order` calls `executor._execute_cancel()` directly, bypassing the diplomatic dialogue guard. Allows AP consumption during dialogue state.
- **Proposed Fix:** Add dialogue guard before executing cancel.

### [2A-5] [DEBUG] Unconditional verbose debug prints on every turn end
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** main.py:937-966
- **Description:** Multiple verbose `print()` statements in enemy phase processing run unconditionally, producing significant console noise in production.
- **Proposed Fix:** Gate behind `DEBUG_MODE` or remove.

### [2A-6] [INTERRUPT] Strategic interrupt name matching includes enemy marshals
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** main.py:544-556
- **Description:** Interrupt routing guard checks against ALL marshal names (player + enemy). "Attack Wellington" matches "Wellington" (enemy), incorrectly clearing player interrupt. Behavior is acceptable but logic should use player marshals only.
- **Proposed Fix:** Filter to player nation marshals only.

### [2A-7] [SAVE] Save endpoint missing error handling wrapper
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** main.py:1696-1701
- **Description:** `/save` endpoint lacks try/except wrapper unlike all other POST endpoints. Disk errors return raw 500 instead of clean JSON error.
- **Proposed Fix:** Add try/except wrapper.

### [2B-1] [SAVE/LOAD] Mid-turn per-turn state not cleared on load
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** save_manager.py:120-123
- **Description:** `load_game()` clears `battles_this_turn` and `in_combat_this_turn` but NOT other per-turn transient state: `objection_popups_this_turn`, `mild_concerns_this_turn`, `gold_spent_this_turn`, `diplomatic_trust_applied`, `threat_sources_this_turn`, `attacks_this_turn`. Mid-turn save + reload preserves stale data causing blocked objections, trust cap carryover, and undeserved flanking bonuses.
- **Proposed Fix:** Clear all per-turn transient state in `load_game()`.

### [2B-2] [MARSHAL] Morale default mismatch between __init__ and from_dict
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** marshal.py:1225
- **Description:** `__init__` sets `morale = 100`, `from_dict` defaults to `70`. Missing morale key would load at 70 instead of 100.
- **Proposed Fix:** Change from_dict default to 100.

### [2B-3] [SAVE/LOAD] Shallow copy of active_treaties shares nested clauses
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** world_state.py:2803
- **Description:** `to_dict()` uses shallow `.copy()` on treaty dicts, sharing nested `clauses` list. Harmless due to synchronous serialization.
- **Proposed Fix:** Use `copy.deepcopy` for defense-in-depth.

### [2B-4] [SAVE/LOAD] Shallow copy of previous_treaties shares nested data
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** world_state.py:2793
- **Description:** Same shallow copy pattern as 2B-3 for previous_treaties.
- **Proposed Fix:** Use `copy.deepcopy`.

### [2B-5] [SAVE/LOAD] Shallow copy of last_morning_dispatch shares nested structures
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** world_state.py:2770
- **Description:** Dispatch is write-once, never mutated after creation. Shared references harmless.

### [2B-6] [SAVE/LOAD] Popup/dialogue fields stored as direct references
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** world_state.py:2797-2801
- **Description:** Multiple Optional[Dict] fields stored without copy. Harmless due to synchronous JSON serialization.

### [2B-7] [SAVE/LOAD] active_battles and battle_history are dead serialized fields
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** world_state.py:259-261
- **Description:** Both fields initialized, serialized, and deserialized but never populated. Dead code adding ~2 lines to every save.
- **Proposed Fix:** Remove dead fields.

### [2C-1] [MODDING] Validator missing terrain validation
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** backend/modding/validator.py
- **Description:** Region validator doesn't validate `terrain` field. Mod with `"terrain": "swamp"` passes validation but crashes `from_scenario()` with ValueError.
- **Proposed Fix:** Add terrain validation against VALID_TERRAINS set.

### [2C-2] [MODDING] Validator missing region_type validation
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** backend/modding/validator.py
- **Description:** Same gap for `region_type`. Mod with `"region_type": "fortress"` passes validation but crashes on load.
- **Proposed Fix:** Add region_type validation against VALID_REGION_TYPES set.

### [2C-3] [MODDING] VALID_NATIONS missing Saxony, includes unused nations
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** backend/modding/validator.py:68
- **Description:** `VALID_NATIONS` includes Russia/Spain (not active) but omits Saxony (active enemy nation). Saxony mods get spurious warnings.
- **Proposed Fix:** Update to include Saxony, optionally keep Russia/Spain.

### [2C-4] [MODDING] from_scenario() does not call validate_scenario()
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** world_state.py:3097-3158
- **Description:** `from_scenario()` loads JSON and passes to `from_dict()` without calling validator. All validation checks bypassed. Invalid mods silently load.
- **Proposed Fix:** Add validate_scenario() call before from_dict().

### [2C-5] [MODDING] Marshal strength not int-cast in from_dict
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** marshal.py:1206
- **Description:** `from_dict()` uses `strength=data["strength"]` without `int()`. Validator allows floats. Mod with `50000.5` loads as float, violating Golden Rule #2.
- **Proposed Fix:** Add `int()` cast.

### [2C-6] [MODDING] Validator does not check for extremely large values
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** backend/modding/validator.py:122-129
- **Description:** No upper bounds on numeric fields. Mod with `strength: 999999999` passes validation.
- **Proposed Fix:** Add warnings for extreme values.

### [2D-1] [CAMPAIGN_LOG] event_log has no size cap — unbounded memory growth
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** world_state.py:570-577
- **Description:** event_log grows indefinitely (unlike command_history capped at 50). In a 40-turn game, 800+ events accumulate, each battle event including full battle_report dicts. Significant memory growth and serialization cost.
- **Proposed Fix:** Add rolling cap or strip battle_report from logged events.

### [2D-2] [CAMPAIGN_LOG] battle_report nested objects waste memory in event_log
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** combat.py:852
- **Description:** Full battle_report dicts stored in event_log but stripped by campaign log endpoint. Wasted space in memory and saves for 50+ battles.
- **Proposed Fix:** Don't include battle_report in log_battle_event dict.

### [2D-3] [CAMPAIGN_LOG] nation_eliminated event type missing from whitelist
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** campaign_log.py:83-116
- **Description:** `nation_eliminated` logged but not in `CAMPAIGN_LOG_TYPES`. Nation eliminations silently filtered from campaign log.
- **Proposed Fix:** Add to whitelist and CATEGORY_MAP.

### [2D-4] [CAMPAIGN_LOG] vassal_auto_join_war missing from whitelist
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** campaign_log.py:83-116
- **Description:** `vassal_auto_join_war` logged but filtered. Significant diplomatic event invisible to player.
- **Proposed Fix:** Add to whitelist.

### [2D-5] [CAMPAIGN_LOG] coalition_member_left missing from whitelist
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** campaign_log.py:83-116
- **Description:** Member departures not whitelisted, though formation/dissolution are. Incomplete coalition narrative.
- **Proposed Fix:** Add to whitelist.

### [2D-6] [INTEL_REPORT] FULL-visibility regions without enemies silently omitted
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** intel_report.py:87-91
- **Description:** FULL visibility regions with no enemies don't appear in any report section. Can't distinguish "confirmed empty" vs "no intel."
- **Proposed Fix:** Consider "clear regions" section.

### [2D-7] [CAMPAIGN_LOG] diplomatic_downgrade and auto_downgrade not in whitelist
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** campaign_log.py:83-116
- **Description:** Automatic diplomatic degradation events filtered. May overlap with treaty_broken.
- **Proposed Fix:** Consider adding diplomatic_downgrade.

---

## Phase 3: CROSS-CUTTING CONCERNS

### [3A-1] [MAIN] No concurrency protection on global world state
- **Severity:** MAJOR
- **Category:** DESIGN
- **File:** main.py:45-46
- **Description:** Global `world` accessed by all request handlers. Sync endpoints run in thread pool. No lock. Rapid double-clicks could dispatch two `/command` POSTs that both read same `actions_remaining`, spending 1 AP for 2 actions.
- **Proposed Fix:** Add `threading.Lock` around state-mutating endpoints, or convert all to `async def`.

### [3A-2] [MAIN] Async/sync endpoint inconsistency creates confusing execution semantics
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** main.py (various)
- **Description:** Some mutating endpoints are sync (execute_command), others doing similar work are async (cancel_order). Creates confusing thread-pool vs event-loop execution mix.
- **Proposed Fix:** Make all state-mutating endpoints consistently sync or async.

### [3B-1] [WORLD_STATE] Bare `except:` clause swallows SystemExit/KeyboardInterrupt
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** world_state.py:2643
- **Description:** Bare `except:` catches everything including SystemExit. Could prevent graceful shutdown.
- **Proposed Fix:** Change to `except Exception:`.

### [3B-2] [DISPATCH] Silent `except Exception: pass` hides acceptance formula errors
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** dispatch.py:666-667
- **Description:** Acceptance threshold detection silently swallows all errors. Formula bugs invisible.
- **Proposed Fix:** Log the exception.

### [3B-3] [EXECUTOR] Confrontation/redemption exception handlers clear dialogue silently
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** executor.py:12945-12949, 12969-12973
- **Description:** Exception handlers return `"success": True` with "The matter has been resolved" when the error actually prevented resolution. Misleading + hides bugs.
- **Proposed Fix:** Return `"success": False` and log the traceback.

### [3B-4] [MARSHAL] Assert statement could crash production server
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** marshal.py:231
- **Description:** `assert not (cavalry and artillery)` raises unhandled AssertionError on corrupted save/mod data. Not caught anywhere.
- **Proposed Fix:** Replace with explicit `if` check and `ValueError`.

### [3B-5] [MAIN] Exception error messages expose internal details
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** main.py (multiple)
- **Description:** `f"Error: {str(e)}"` returned to frontend. Acceptable for local game.

### [3D-1] [MAIN] No input length limit on command text
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** main.py:501
- **Description:** `CommandRequest.command` has no `max_length`. Multi-megabyte commands passed to parser and stored in history.
- **Proposed Fix:** Add `max_length=500` to Pydantic model.

### [3D-2] [SAVE] Save filename not validated — path traversal possible
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** main.py:1697-1701, save_manager.py:68-71
- **Description:** `/save` doesn't call `_validate_save_filename()` unlike `/load` and `/delete_save`. Sanitization handles separators but asymmetry is a code smell.
- **Proposed Fix:** Add filename validation to save endpoint.

### [3D-3] [MAIN] API key prefix logged to stdout
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** main.py:38
- **Description:** First 10 chars of API key logged on startup. Reveals 3 chars beyond the `sk-ant-` prefix.
- **Proposed Fix:** Log only presence/absence.

### [3D-4] [MAIN] Cheat commands available without DEBUG_MODE in mock mode
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** executor.py:14370-14376
- **Description:** Cheats pass through in mock LLM mode regardless of DEBUG_MODE. By design for testing.

### [3D-5] [MAIN] CORS allows all origins
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** main.py:415-420
- **Description:** `allow_origins=["*"]`. Acceptable for local game server.

### [3D-6] [SAVE] No type validation on deserialized save data
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** save_manager.py:91-135
- **Description:** `from_dict()` trusts all data types from JSON. General exception handler catches type errors gracefully.

---

## Phase 2+3 Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| MAJOR | 9 |
| MINOR | 18 |
| NOTE | 14 |
| **TOTAL** | **41** |

**Top findings:**
1. **2A-1** — Enemy phase summary leaks fogged action information (MAJOR fog leak)
2. **2A-2** — War panel shows stale data after turns with visible enemy actions (MAJOR)
3. **2B-1** — Mid-turn save/load preserves transient state that should be cleared (MAJOR)
4. **2C-4** — from_scenario() never calls validator (MAJOR modding gap)
5. **2D-1** — Unbounded event_log growth with heavy battle_report payloads (MAJOR)
6. **3A-1** — No concurrency protection on global world state (MAJOR race condition)

---

## Phase 4: CONTINUOUS SIMULATED PLAYTESTS

### [4A-1] [COMBAT/EXECUTOR] Attack auto-move bypasses `_execute_move()` — artillery can attack after moving
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** executor.py:3718-3724
- **Description:** When attack auto-moves a marshal to an adjacent region, it calls `marshal.move_to()` directly instead of `_execute_move()`. This bypasses artillery `moved_this_turn` flag, movement attrition, fog refresh, diplomatic territory entry checks, idle_turns reset, and square formation auto-break. Drouot (artillery) can auto-move then bombard on the same turn.
- **Proposed Fix:** Route auto-move through `_execute_move()` or at minimum set `moved_this_turn = True` for artillery.

### [4A-2] [DIPLOMACY/EXECUTOR] `find_nearest_enemy()` ignores war state — auto-targets nations at peace
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** world_state.py:2025-2051, executor.py:3657-3662
- **Description:** `find_nearest_enemy()` uses `get_enemy_marshals()` which returns ALL non-player marshals regardless of war state. Auto-targeting from Milan returns ArchdukeCharles (Austria, at PEACE, distance 1) instead of Gneisenau (Prussia, at WAR, distance 2). The attack path then auto-declares war.
- **Proposed Fix:** Add war-state filter to the auto-targeting call.

### [4A-3] [EXECUTOR] Fortify engagement check ignores war state — allied marshals block fortification
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** executor.py:8602-8607
- **Description:** Fortify engagement check uses `m.nation != marshal.nation` without `is_at_war()`. Saxony marshals with OPEN_BORDERS in same region block French fortification with "cannot fortify while engaged with enemy forces." The move check (line 6736) and drill check correctly use `is_at_war`.
- **Proposed Fix:** Add `world.is_at_war(marshal.nation, m.nation)` to the filter.

### [4A-4] [WORLD_STATE] Threat assessment and retreat paths ignore war state
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** world_state.py:1507, 1581-1582
- **Description:** `get_threatening_enemies()` treats neutral/allied marshals as threats. `get_safe_retreat_destination()` excludes regions with non-hostile marshals. Austria at PEACE incorrectly counted as threat.
- **Proposed Fix:** Add `is_at_war` to both functions.

### [4A-5] [EXECUTOR] Diplomatic proposal fallback uses hardcoded state descriptions
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** executor.py:11456-11463
- **Description:** Fallback popup when no target_nation specified hardcodes "Currently at war." / "At peace." without reading actual diplomatic state. Shows stale info after signing peace.
- **Proposed Fix:** Dynamically generate from `world.get_diplomatic_state()`.

### [4B-1] [COMBAT] Auto-charge skips Win/Loss Relationship processing
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** world_state.py:5260-5676
- **Description:** Reckless cavalry auto-charge resolves combat but never calls `process_battle_relationships()`. Co-located marshals' relationships never update from auto-charge battles. Both `_execute_attack` and `_execute_glorious_charge` call it.
- **Proposed Fix:** Add `process_battle_relationships()` call after auto-charge combat resolution.

### [4B-2] [DIPLOMACY/DIALOGUE] Sabotage discovery overwrites already-popped dialogue from queue
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** dispatch.py:820
- **Description:** `_check_talleyrand_session6()` sets `world.pending_diplomatic_dialogue = confrontation` without checking if a dialogue was already popped from queue. If vassal rebellion was popped first, it gets permanently lost. The redemption check (line 882) correctly guards with `if not world.pending_diplomatic_dialogue`.
- **Proposed Fix:** Queue the sabotage confrontation or re-queue existing dialogue before overwriting.

### [4B-3] [COMBAT] Auto-charge does not increment marshal exhaustion counter
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** world_state.py:5260-5676
- **Description:** Auto-charge path doesn't call `marshal.increment_attacks_this_turn()`. Regular attacks do. Reckless cavalry gets a "free" attack not counted toward exhaustion.
- **Proposed Fix:** Add `marshal.increment_attacks_this_turn()` after auto-charge combat.

### [4B-4] [DIPLOMACY/AI] Brewing coalition nations can propose trade deals
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** ai_diplomacy.py:700-708
- **Description:** No check for brewing coalition membership before P7 trade proposals. Nation about to join coalition war can propose trade upgrade same turn.
- **Proposed Fix:** Consider adding coalition brewing guard to P7.

### [4C-1] [FRONTEND] Game over screen never shows marshal status
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** main.gd:1636
- **Description:** Checks `game_state.has("player_marshals")` but backend returns key as `"marshals"`. Condition always false, Marshal Status section never appears on victory/defeat screen.
- **Proposed Fix:** Change `"player_marshals"` to `"marshals"`.

### [4C-2] [DISPATCH] Turn limit warning off-by-one
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** dispatch.py:540-551
- **Description:** Warnings shifted one turn early. At turn 39 (remaining=1), says "FINAL TURN" but turn 40 is the actual last playable turn. At turn 40 (remaining=0), says "campaign has concluded" but player still has actions.
- **Proposed Fix:** Shift thresholds by one.

### [4C-3] [DISPATCH] Turn limit warning and other sections not rendered in terminal
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** main.gd:1389-1566
- **Description:** Backend builds `turn_limit_warning`, `talleyrand_report`, `coalition_status` but terminal only renders `turn`, `situation`, `marshals`, `intelligence`, `turn_events`, `berthier_note`. Rich context lost.
- **Proposed Fix:** Add rendering for missing dispatch sections.

### [4C-4] [DISPATCH] Berthier note missing near-victory awareness
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** dispatch.py:445-502
- **Description:** No Berthier comment at 13/14 required regions. Missed narrative moment at most exciting part of game.
- **Proposed Fix:** Add victory-proximity priority check to `_pick_berthier_note()`.

### [4C-5] [EXECUTOR] Explicit end_turn path missing top-level game_over/victory keys
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** executor.py:1018-1062
- **Description:** Auto-advance path adds `game_over`/`victory` to result dict. Explicit `_execute_end_turn` doesn't. Inconsistent response shape.
- **Proposed Fix:** Add victory check extraction to `_execute_end_turn`.

### [4C-6] [DESIGN] No capital-loss defeat condition
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** turn_manager.py:800-851
- **Description:** Losing Paris doesn't cause defeat. Design decision, not a bug.

### [4C-7] [DESIGN] No victory progress indicator in dispatch situation
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** dispatch.py:108-160
- **Description:** Dispatch shows region count but never compares to victory threshold. Player must remember thresholds.
- **Proposed Fix:** Add `victory_threshold` and `regions_to_victory` fields.

### [4D-2] [AI] Enemy AI stance changes fail due to player AP check
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** executor.py:9947
- **Description:** `_execute_stance_change()` has internal AP check that always checks PLAYER's action pool. The outer `execute()` correctly skips AP for enemy AI, but this inner check uses the wrong pool. Since player typically has 0 AP during enemy phase, **ALL enemy AI stance changes silently fail every turn**.
- **Proposed Fix:** Add `is_player = marshal.nation == world.player_nation` guard before AP check.

### [4D-3] [AI] Enemy AI defend/fortify auto-stance blocked by player AP
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** executor.py:5281, 8639
- **Description:** Same root cause as 4D-2. Both `_execute_defend` and `_execute_fortify` perform internal AP checks against player's pool. Enemy AI defend/fortify orders from wrong stance fail silently.
- **Proposed Fix:** Add `is_player` guard to both internal AP checks.

### [4D-4] [UX] Attacking own marshal silently redirects to nearest enemy
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** executor.py:3654-3733
- **Description:** "Ney attack Davout" parses with target=None (own marshal ignored), then auto-targets nearest enemy. No feedback about invalid target.
- **Proposed Fix:** Add warning message when intended target matched a friendly marshal.

### [4E-1] [AI] `decide_single_action` missing per-turn tracking set initialization — autonomous marshals crash silently
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** enemy_ai.py:509-534
- **Description:** `decide_single_action()` (autonomous player marshals) calls `_evaluate_marshal()` without initializing tracking sets (`_unfortified_this_turn`, `_threat_responder_assigned`, `_recapture_targets_claimed`, etc.). Six+ code paths directly access these, causing `AttributeError` caught by silent try/except. Autonomous marshals' actions silently fail.
- **Proposed Fix:** Add full tracking set initialization to `decide_single_action()`.

### [4E-2] [AI] P6.5 supply awareness hardcodes `world.player_nation`
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** enemy_ai.py:1600
- **Description:** Supply relocation skips regions controlled by `world.player_nation`. For autonomous player marshals, this blocks relocation to own territory (the best option). Can only relocate to Neutral regions.
- **Proposed Fix:** Replace with `world.is_at_war(nation, adj_region.controller)` check.

### [4E-3] [AI] CHECK 1 in fortification opportunity missing `is_at_war` check
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** enemy_ai.py:4049-4064
- **Description:** CHECK 1 looks for undefended adjacent regions to capture but doesn't check war state. AI wastes action unfortifying for non-war captures. CHECK 0, 2, 3, and P4.5 all correctly check `is_at_war`.
- **Proposed Fix:** Add `is_at_war` check after controller skip.

---

## Phase 4 Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| MAJOR | 11 |
| MINOR | 10 |
| NOTE | 3 |
| **TOTAL** | **24** |

**Top playtest findings:**
1. **4D-2/4D-3** — ALL enemy AI stance changes silently fail (player AP check) — fundamentally broken AI feature
2. **4E-1** — Autonomous marshals crash silently due to missing initialization
3. **4A-1** — Artillery can attack after auto-move, bypassing restrictions
4. **4A-2** — Auto-targeting ignores war state, can trigger unintended wars
5. **4B-2** — Sabotage discovery overwrites queued dialogues, permanently losing them
6. **4C-1** — Game over screen never shows marshal status (wrong key name)
7. **4C-2** — Turn limit warnings off by one turn

**Emerging patterns:**
- **War-state ignorance**: 5 findings (4A-2, 4A-3, 4A-4, 4E-2, 4E-3) where code checks `nation != marshal.nation` without `is_at_war()`. The diplomacy system introduced ally/neutral states that legacy code doesn't respect.
- **Auto-action bypasses**: 3 findings (4A-1, 4B-1, 4B-3) where auto-charge/auto-move skip steps that manual actions perform.
- **Internal AP checks**: 2 findings (4D-2, 4D-3) where internal AP validation duplicates the outer check but always uses player's pool.

---

## Phase 5: TARGETED FOLLOW-UP PLAYTESTS

### Phase 5A: Systematic `is_at_war()` Gap Audit

**ROOT CAUSE:** The diplomacy system (Phase 8) added ally/neutral diplomatic states, but legacy code across the entire codebase uses `m.nation != marshal.nation` as a proxy for "is enemy." Only ~40% of instances have been updated with `is_at_war()` checks.

**33 new instances found** across executor.py, world_state.py, disobedience.py, objection_v2.py, personality.py, strategic_parser.py, turn_manager.py, enemy_ai.py:

| ID | Severity | File | Issue |
|----|----------|------|-------|
| 5A-1 | MAJOR | executor.py:468-474 | Reinforcement engagement treats allies as blocking |
| 5A-2 | MAJOR | executor.py:682-692 | Overwatch counts allied artillery as enemy |
| 5A-3 | MAJOR | executor.py:3931-3937 | Bombardment targets allied marshals |
| 5A-4 | MAJOR | executor.py:3963-3965 | Undefended-region check counts allies as defenders |
| 5A-5 | MAJOR | executor.py:4178-4181 | Cavalry charge leapfrog treats allies as blockers |
| 5A-6 | MAJOR | executor.py:4403-4406, 4873-4876 | Post-battle remaining-defenders blocks conquest from allied presence |
| 5A-7 | MAJOR | executor.py:3570-3572 | Reckless charge alternatives include allied marshals |
| 5A-8 | MAJOR | executor.py:8131-8132 | Garrison validation treats allies as enemies |
| 5A-11 | MAJOR | executor.py:10188, 10198 | Glorious charge targets allied marshals |
| 5A-15 | MAJOR | world_state.py:1119-1124 | **Core method** `get_enemy_marshals()` returns ALL non-player marshals |
| 5A-16 | MAJOR | world_state.py:1126-1131 | **Core method** `get_enemy_by_name()` returns allied marshals |
| 5A-20 | MAJOR | disobedience.py:99,112,172,332 | 4 instances: move validation, drilling, engagement detection |
| 5A-9 | MINOR | executor.py:7012-7013 | Move capture hints count allies as defenders |
| 5A-10 | MINOR | executor.py:7097-7099 | Scout reports allies as enemies |
| 5A-12 | MINOR | executor.py:10252-10255 | Glorious charge leapfrog treats allies as blockers |
| 5A-13 | MINOR | executor.py:10407-10410 | Glorious charge remaining-defenders blocks capture |
| 5A-14 | MINOR | executor.py:10603 | Post-objection charge target lacks war check |
| 5A-17 | MINOR | world_state.py:1756-1763 | `is_enemy_nearby()` counts allies |
| 5A-18 | MINOR | world_state.py:5759-5760 | `_find_retreat_destination()` treats allies as blocking |
| 5A-19 | MINOR | world_state.py:5513-5516 | Auto-charge remaining defenders counts allies |
| 5A-21 | MINOR | disobedience.py:2197 | Aggressive fallback targets allies |
| 5A-22 | MINOR | disobedience.py:1163 | Objection ratio targets allies |
| 5A-23 | MINOR | objection_v2.py:530,597,731,1012 | 4 instances: visible enemies, engagement, path crossing |
| 5A-24 | MINOR | personality.py:324,342,411 | Adjacent enemy check, strength ratio count allies |
| 5A-25 | MINOR | strategic_parser.py:438-439 | SUPPORT/PURSUE target misclassifies allies |
| 5A-26 | MINOR | turn_manager.py:774-777 | Capital proximity alert on allies |
| 5A-27 | MINOR | enemy_ai.py:4761 | Cavalry threat detection counts allies |
| 5A-28 | MINOR | enemy_ai.py:4825 | Artillery position scoring penalizes allied cavalry |
| 5A-29 | MINOR | enemy_ai.py:4091-4092,4107,4142 | CHECK 2 fortification counts allies |
| 5A-30 | MINOR | enemy_ai.py:2803-2808,2839-2844 | P3 ally support counts allies as enemies |
| 5A-31 | MINOR | enemy_ai.py:2465-2466,2511-2512 | P4.5 recapture counts allies as defenders |
| 5A-32 | MINOR | enemy_ai.py:2591-2592 | P4.5 capture opportunity counts allies |
| 5A-33 | NOTE | enemy_ai.py:2288-2293 | Artillery density counts allies |

**Recommendation:** Fix the 2 core methods first (5A-15, 5A-16) then cascade through callers.

### Phase 5B: Internal AP Check Audit

**No new findings.** Exhaustive search of all 37 `actions_remaining` accesses and 10 `use_action` calls in executor.py confirmed the 3 already-reported bugs (4D-2, 4D-3) are the complete set. All other instances are correctly guarded, player-only code paths, or display-only.

### Phase 5C: Auto-Action Bypass Audit

**12 new findings** where auto-action paths skip processing steps that manual actions perform:

| ID | Severity | System | Missing Steps |
|----|----------|--------|---------------|
| 5C-1 | MAJOR | Auto-bombardment kill | Skips ALL 12+ post-combat steps (relationships, authority, coalition, battle recording, exhaustion, war damage) |
| 5C-2 | MAJOR | Reckless auto-move | Bypasses fog visibility refresh |
| 5C-3 | MAJOR | Reckless auto-move | Bypasses diplomatic territory entry check |
| 5C-4 | MINOR | Reckless auto-move | Bypasses movement attrition |
| 5C-5 | MINOR | Auto-charge advance | Skips movement attrition |
| 5C-6 | MINOR | Garrison combat | Skips fog/intel update |
| 5C-7 | MINOR | Garrison combat | Skips coalition threat/war exhaustion |
| 5C-8 | MINOR | Garrison combat | Skips campaign log event + cannon fire recording |
| 5C-9 | MINOR | Garrison combat | Skips authority modifier |
| 5C-10 | MINOR | Auto-bombardment kill | Skips war damage to region |
| 5C-11 | MINOR | Garrison combat | Skips war damage to region |
| 5C-12 | NOTE | Auto-charge advance | Skips fog refresh (low impact) |

### Phase 5D: Combat and Formation Deep Dive

| ID | Severity | Issue |
|----|----------|-------|
| 5D-1 | MAJOR | Coordinated battle mutual_destruction gives zero morale loss (combat.py:1055-1059) — normal path gives -20 |
| 5D-2 | MAJOR | Coordinated pursuit damage heals sub-1000 defenders (executor.py:4571-4577) — `max(1000, 500-5000) = 1000` |
| 5D-3 | MINOR | Glorious charge bypasses entire coordination system — may be intentional |
| 5D-4-8 | NOTE | Verified safe: fort degradation floors at 0, retreat/broken system sound, casualty distribution correct, terrain balance adequate |

---

## Phase 5 Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| MAJOR | 17 |
| MINOR | 27 |
| NOTE | 3 |
| **TOTAL** | **47** |

**The `is_at_war()` gap is the single largest systemic bug in the codebase.** 33 instances across 8 files where allied/neutral nations are treated as enemies. Two core methods (`get_enemy_marshals`, `get_enemy_by_name`) propagate the pattern to all callers.

---

## Phase 6: DEEP FOLLOW-UP PLAYTESTS

### Phase 6A: Notification + Dispatch System

| ID | Severity | Issue |
|----|----------|-------|
| 6A-1 | MAJOR | Enemy tactical events (drill_complete, fortify_strengthened, broken_recovered, garrison_regen, construction_complete) leak to player dispatch — no nation filter on events without nation field (dispatch.py:418-421, world_state.py:4650-4657) |
| 6A-2 | MAJOR | `nation_eliminated` dispatch event has no template — shows "Diplomatic event: nation_eliminated" raw to player (dispatch.py:974-1008) |
| 6A-3 | MINOR | Talleyrand Trigger 4 fires on PROXIMITY to threshold not CROSSING — false alerts every 5 turns at stable relations (dispatch.py:729-748) |
| 6A-4 | NOTE | Comment misclassifies `reckless_no_target` severity |
| 6A-5 | NOTE | Dead code: `is_player_marshal` computed but never used in `_process_tactical_states` |
| 6A-6 | NOTE | Comment says "MEDIUM" priority but enum only has NORMAL/HIGH/CRITICAL |
| 6A-7 | NOTE | `from_list` deserialization bypasses notification cap enforcement |
| 6A-8 | NOTE | `diplomatic_continental_system` template exists but never queued |

### Phase 6B: Economy + Manpower System

| ID | Severity | Issue |
|----|----------|-------|
| 6B-1 | MAJOR | Strategic ledger net income missing admin bonus, treaty gold/turn, vassal tribute, CS penalty — player's financial planning tool off by 200+ gold/turn (ledger.py:216) |
| 6B-3 | MAJOR | Vassal tribute uses flat 50/region instead of actual region income — tribute 45% less than spec (vassal.py:608, diplomacy.py:2831) |
| 6B-2 | MINOR | Infantry recruit error message uses static regen rate, ignoring war exhaustion — shows wrong recovery estimate (executor.py:7931) |
| 6B-4 | MINOR | Continental System never removes AUTONOMOUS vassals — they keep paying -75g/turn penalty (diplomacy.py:2274-2281) |
| 6B-5 | NOTE | Stale TODO about trade income being deferred (world_state.py:2130) |

### Phase 6C: Trust + Defiance + Vindication System

| ID | Severity | Issue |
|----|----------|-------|
| 6C-1 | MAJOR | Defiance gate excludes MODERATE concerns, contrary to spec — MODERATE never triggers defiance roll despite 5% base chance (executor.py:13691, 10921) |
| 6C-2 | MINOR | Vindication decay timer not reset by defiance or defensive vindication — premature decay possible (defiance.py:268, turn_manager.py:725) |
| 6C-3 | NOTE | V2B spec contradicts itself on defiance AP cost (line 103 vs line 700) |

### Phase 6D: LLM Parsing + Prompt Builder

| ID | Severity | Issue |
|----|----------|-------|
| 6D-1 | MAJOR | Enemy marshals (Gneisenau, Schwarzenberg, Reynier) hijack marshal slot as targets — "attack Reynier" returns error instead of attacking (llm_client.py:562-584) |
| 6D-2 | MINOR | "fall back to [region]" parsed as retreat instead of strategic move — "withdraw to" correctly handled but not "fall back to" (llm_client.py:685) |
| 6D-3 | MINOR | Prompt builder lists "dig in" as HOLD keyword but it's actually tactical fortify (prompt_builder.py:371) |
| 6D-4 | MINOR | "wait" action blocked at 0 AP despite being designed as free — missing from free_actions set (executor.py:1494) |
| 6D-5 | MINOR | Strategic action names (pursue/support/reinforce/march) in VALID_ACTIONS but unreachable by executor (validation.py:38-41) |
| 6D-6 | NOTE | `_clean_target_text` doesn't strip trailing punctuation (strategic_parser.py:387) |

---

## Phase 6 Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| MAJOR | 6 |
| MINOR | 8 |
| NOTE | 8 |
| **TOTAL** | **22** |

---

## Phase 7: CONTINUED PLAYTESTING

### Phase 7A: Strategic Orders System

| ID | Severity | Issue |
|----|----------|-------|
| 7A-1 | MAJOR | Broken marshal can issue and execute strategic orders — broken state check skipped for strategic commands (executor.py:5515) |
| 7A-2 | MAJOR | `holding_position` not cleared in 12+ order-cancellation paths — permanent +15% defense bonus leak (strategic.py multiple, executor.py:8734) |
| 7A-3 | MAJOR | `until_battle_won` condition never fires from normal combat — `last_combat_result` only set in strategic.py, never by executor attack (strategic.py:1999-2012) |
| 7A-4 | MINOR | Cautious initial pathfinding is omniscient, ignoring fog of war — leaks enemy positions (executor.py:5709-5712) |
| 7A-5 | MINOR | Literal first-step reroute is omniscient — same fog leak (executor.py:6592-6595) |
| 7A-6 | MINOR | `_auto_break_square` clears strategic order without clearing HOLD state (executor.py:8734) |
| 7A-7 | NOTE | HOLD timed expiry check duplicated in 3 places, 1 is dead code |
| 7A-8 | MINOR | Dead marshal cleanup doesn't clear `pending_interrupt` (strategic.py:93-96) |

### Phase 7B: Multi-Marshal Coordination System

| ID | Severity | Issue |
|----|----------|-------|
| 7B-1 | MINOR | Artillery reinforcements excluded from relationship processing — take casualties but never develop relationships (relationship.py:124, executor.py:4288) |
| 7B-2 | NOTE | Remainder overflow causes significant casualty loss with artillery-heavy compositions — W-2 documented, by design |
| 7B-3 | NOTE | Gneisenau "Staff Work" ability still unwired despite Phase 7 completion |

---

## Phase 7 Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| MAJOR | 3 |
| MINOR | 6 |
| NOTE | 3 |
| **TOTAL** | **12** |

---

## Phase 8: FINAL FOLLOW-UP

*(Findings will be appended by subagents)*

