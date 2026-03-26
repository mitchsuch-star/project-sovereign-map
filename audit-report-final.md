# Final Audit — Integration + Live Playtest
**Started:** 2026-03-26
**Method:** Live curl playtest + cross-system code review + adversarial testing
**Prior audits:** V1 (~148), Deep (43), Diplomacy (43), V2 (56), V3 (~110+) = ~320 bugs fixed
**Tests before:** 7,232
**Purpose:** Cross-system integration, real HTTP playtest, endgame validation, frontend contract verification

---

## Phase 1: Code Review Findings

### [FINAL-1] [DIPLOMACY] Coalition Proposal Void Never Refunds DP — dp_cost Not Stored
- **Severity:** MAJOR
- **Category:** INTEGRATION / MONEY BUG
- **File:** backend/game_logic/coalition.py:562-565, backend/commands/executor.py:12482-12486
- **Description:** When a coalition forms and voids a player's proposal_in_transit, it tries to refund DP via `pit.get("proposal", {}).get("dp_cost", 0)`. However, dp_cost is NEVER stored in the proposal dict. The proposal dict only contains: `type`, `proposer_nation`, `target_nation`, `sweeteners`, `demands`, `clauses`. And the proposal_in_transit dict only contains: `target`, `proposal`, `turn_sent`. Result: refund is always 0 — player permanently loses their DP when coalition voids their in-transit proposal.
- **Evidence:**
  ```python
  # executor.py:12482-12486 — proposal_in_transit creation (NO dp_cost field)
  world.proposal_in_transit = {
      "target": target_nation,
      "proposal": proposal,       # proposal dict has no dp_cost
      "turn_sent": turn_sent,
  }

  # coalition.py:562-565 — refund attempt (always gets 0)
  dp_cost = pit.get("proposal", {}).get("dp_cost", 0)  # Always 0!
  if dp_cost > 0:
      world.diplomatic_points = getattr(world, 'diplomatic_points', 0) + int(dp_cost)
  ```
- **Proposed Fix:** Store dp_cost in proposal_in_transit when created:
  ```python
  # executor.py: add dp_cost to pit
  world.proposal_in_transit = {
      "target": target_nation,
      "proposal": proposal,
      "turn_sent": turn_sent,
      "dp_cost": cost,  # Store for refund on void
  }
  # coalition.py: read from pit directly
  dp_cost = pit.get("dp_cost", 0)
  ```
- **Test Coverage:** Needs new test — "DP refunded when coalition voids in-transit proposal"

---

### [FINAL-2] [DIPLOMACY] Vassal Rebellion Cascade Can Break Armistice Lock
- **Severity:** MAJOR
- **Category:** CASCADE / STATE PARADOX
- **File:** backend/game_logic/vassal.py → backend/game_logic/diplomacy.py (_process_war_cascade)
- **Description:** When a vassal rebels and check_vassal_rebellion() triggers _process_war_cascade(), the cascade forces WAR state between nations. However, the cascade doesn't check if the pair is currently in ARMISTICE (which has a 5-turn lock). A vassal rebellion at armistice turn 2 can force-break the armistice early, violating the diplomatic contract.
- **Evidence:** In _process_war_cascade, war is declared via `world.diplomatic_states[war_key] = "WAR"` without checking current state for armistice lock.
- **Proposed Fix:** In _process_war_cascade, skip pairs in ARMISTICE state, or add an armistice-aware path that respects the lock period.
- **Test Coverage:** Needs new test — "Vassal rebellion respects armistice lock"

---

### [FINAL-3] [COMBAT] Modifier Application Order: Exhaustion Before Coordination
- **Severity:** MINOR
- **Category:** INTEGRATION / MODIFIER STACKING
- **File:** backend/models/marshal.py:890-902
- **Description:** In get_attack_modifier(), exhaustion_penalty is applied BEFORE coordination_attack_bonus. This means coordination doesn't fully offset exhaustion: `(1.0 - 0.10) * 1.15 = 1.035` instead of `(1.0 * 1.15) - 0.10 = 1.05`. Multi-marshal combos are slightly weaker on repeated attacks than intended.
- **Evidence:**
  ```python
  # marshal.py:890-902
  exhaustion_penalty = self._get_exhaustion_penalty()
  if exhaustion_penalty > 0:
      modifier *= (1.0 - exhaustion_penalty)      # Line 894 — applied first
  modifier *= (1.0 + getattr(self, 'total_coordination_attack_bonus', 0.0))  # Line 897 — after
  ```
- **Proposed Fix:** Either swap order (coordination before exhaustion) or document as intentional balance design.
- **Test Coverage:** Needs numeric test verifying stacking order

---

### [FINAL-4] [DIPLOMACY] Coalition Formation Can Invalidate Pending Dialogue
- **Severity:** MAJOR
- **Category:** CASCADE / DIALOGUE STATE
- **File:** backend/game_logic/coalition.py:605-607
- **Description:** When coalition forms, it filters pending_dialogue_queue by target_nation. But it doesn't check if `pending_diplomatic_dialogue` (the CURRENT blocking dialogue) references a voided proposal or involved nation. If the player is mid-dialogue about proposing to nation X, and X joins coalition, the dialogue remains blocking but its context is invalid.
- **Evidence:**
  ```python
  # coalition.py:605-607 — only filters queue, not current dialogue
  if hasattr(world, 'pending_dialogue_queue'):
      world.pending_dialogue_queue = [
          d for d in world.pending_dialogue_queue
          if d.get("target_nation") not in all_members
      ]
  # pending_diplomatic_dialogue NOT checked!
  ```
- **Proposed Fix:** After filtering queue, also check and clear pending_diplomatic_dialogue if its target_nation joined the coalition:
  ```python
  if world.pending_diplomatic_dialogue:
      dialog_target = world.pending_diplomatic_dialogue.get("target_nation", "")
      if dialog_target in all_members:
          world.pending_diplomatic_dialogue = None
          world.awaiting_diplomatic_response = False
  ```
- **Test Coverage:** Needs new test — "Coalition formation clears stale dialogue"

---

### ~~[FINAL-5] [ECONOMY] Continental System Gold Can Go Negative~~
- **Severity:** ~~MAJOR~~ → **FALSE POSITIVE** (downgraded after verification)
- **Category:** INTEGRATION
- **File:** backend/game_logic/diplomacy.py:2308-2310
- **Description:** Continental System already uses `max(0, ...)` floor at lines 2308-2310. Gold CAN go negative from regular upkeep (income phase at world_state.py:2322), but this is by design — the bankruptcy system handles it. All other gold deductions (treaty clauses, vassal tribute, British subsidy) have pre-checks or floor guards. **Not a bug.**

---

### [FINAL-6] [CONTRACT] Save/Load Endpoints Missing active_wars in Response
- **Severity:** MINOR
- **Category:** CONTRACT
- **File:** backend/main.py:1731-1762
- **Description:** POST /save and POST /load don't call `_include_popup_passthroughs()`. While save/load don't run executor code that would SET new popups, the /load endpoint returns game_state without active_wars data. After loading a game mid-war, the war status panel won't update until the next /command call.
- **Evidence:** Lines 1737, 1757-1761 return response without calling `_include_popup_passthroughs(response, world)`.
- **Proposed Fix:** Add `_include_popup_passthroughs(response, world)` to /load success path (lines 1757-1761). This also ensures any pending popups from the loaded save state are delivered immediately.
- **Test Coverage:** Needs test — "Load during active war includes war status data"

---

## Phase 2: Live HTTP Playtest Findings

### [FINAL-7] [FOG] Turn-End Events Leak Enemy Marshal Activity
- **Severity:** MAJOR
- **Category:** PLAYTEST / FOG LEAK
- **File:** backend/commands/executor.py (_execute_end_turn) + backend/models/world_state.py (advance_turn)
- **Description:** The turn-end events array contains enemy marshal activity that should be fog-filtered:
  - `fortify_strengthened` events for enemy marshals (Gneisenau, ArchdukeCharles, Reynier) — reveals exact defense bonus percentages
  - `supply_attrition` events for enemy marshals (Wellington, Uxbridge) — reveals exact troop losses
  These are consistently leaked every turn. The player should NOT see "Gneisenau's fortifications strengthen: +12% defense" or "Wellington loses 1,691 troops" unless they have FULL visibility.
- **Evidence:** Confirmed across 6 consecutive turns:
  ```
  Turn 4: Enemy events leaked: 3 (fortify_strengthened x2, supply_attrition x1)
  Turn 5: Enemy events leaked: 3 (same)
  Turn 6: Enemy events leaked: 3 (same)
  ```
- **Proposed Fix:** Filter `tactical_events` in advance_turn() before returning, removing events for non-player marshals unless the region has PARTIAL+ visibility. Or filter in main.py before including events in the response.
- **Test Coverage:** Needs new test — "Turn events fog-filtered for enemy marshals"

---

### [FINAL-8] [CONTRACT] fortification_old/new Are Floats — Golden Rule #2 Violation
- **Severity:** MAJOR
- **Category:** PLAYTEST / CONTRACT
- **File:** backend/game_logic/combat.py:816-817, 854-855, 1180-1181, 1207-1208; backend/commands/executor.py:5240-5241
- **Description:** `fortification_old` and `fortification_new` are initialized as `0.0` (float) in combat.py and passed through to the event dict in executor.py without `int()` wrapping. These floats reach Godot, which can crash on float values (Golden Rule #2).
- **Evidence:** Live playtest confirmed:
  ```
  Fort old: 0.0 <class 'float'>
  Fort new: 0.0 <class 'float'>
  ```
  Source: `combat.py:753-754: fortification_old = 0.0; fortification_new = 0.0`
- **Proposed Fix:** Wrap in `int()` at the return point in combat.py:
  ```python
  "fortification_old": int(fortification_old * 100),
  "fortification_new": int(fortification_new * 100),
  ```
  Or at executor.py:5240-5241:
  ```python
  "fortification_old": int(battle_result.get("fortification_old", 0) * 100),
  "fortification_new": int(battle_result.get("fortification_new", 0) * 100),
  ```
- **Test Coverage:** Needs test — "Battle event fortification values are integers"

---

### [FINAL-9] [ENDGAME] Lost Capital (Paris) Does Not Trigger Defeat
- **Severity:** CRITICAL
- **Category:** ENDGAME
- **File:** backend/game_logic/turn_manager.py:801-852
- **Description:** `_check_victory_conditions()` only checks "all marshals destroyed" for defeat. There is NO check for the player's capital (Paris) being captured by an enemy. France can lose Paris and continue playing indefinitely, creating an unlosable state.
- **Evidence:**
  ```python
  # Only defeat check (lines 815-821):
  if not player_marshals or all(m.strength <= 0 for m in player_marshals):
      return {"game_over": True, "result": "defeat", "reason": "All armies destroyed!"}
  # No capital loss check exists
  ```
- **Proposed Fix:** Add capital loss check after the marshal check:
  ```python
  from backend.models.region import NATION_CAPITALS
  player_capital = NATION_CAPITALS.get(self.world.player_nation)
  if player_capital:
      capital_region = self.world.get_region(player_capital)
      if capital_region and capital_region.controller != self.world.player_nation:
          return {"game_over": True, "result": "defeat",
                  "reason": f"Your capital {player_capital} has fallen!"}
  ```
- **Test Coverage:** Needs new test — "Defeat triggered on capital loss"

---

### [FINAL-10] [ENDGAME] Turn 41 Off-By-One — Game Gives 41 Turns Instead of 40
- **Severity:** MINOR
- **Category:** ENDGAME
- **File:** backend/game_logic/turn_manager.py:832
- **Description:** The time-limit check uses `>` instead of `>=`: `if self.world.current_turn > self.world.max_turns`. This means turn 40 doesn't trigger the check (40 > 40 = False), and the game continues to turn 41 before checking (41 > 40 = True). Players get 41 playable turns.
- **Evidence:** Line 832: `if self.world.current_turn > self.world.max_turns:`
- **Proposed Fix:** Change to `>=`: `if self.world.current_turn >= self.world.max_turns:`
- **Test Coverage:** Needs test — "Game ends at turn 40, not 41"

---

### [FINAL-11] [ENDGAME] No Victory on Total Enemy Elimination
- **Severity:** MAJOR
- **Category:** ENDGAME
- **File:** backend/game_logic/turn_manager.py:801-852
- **Description:** There is no check for all enemy nations being completely eliminated (all marshals destroyed AND all regions lost). A player who eliminates every enemy marshal and captures every region except one non-enemy neutral region won't trigger victory until the region count threshold is met. The game can't recognize "all enemies defeated" as a win.
- **Proposed Fix:** Add enemy elimination check:
  ```python
  # After region-count victory check:
  enemy_nations = set(m.nation for m in self.world.marshals.values()
                      if m.nation != self.world.player_nation)
  all_enemies_gone = all(
      all(m.strength <= 0 for m in self.world.marshals.values() if m.nation == nation)
      for nation in enemy_nations
  )
  if all_enemies_gone and not any(
      r.controller in enemy_nations for r in self.world.regions.values()
  ):
      return {"game_over": True, "result": "victory", "reason": "All enemies defeated!"}
  ```
- **Test Coverage:** Needs new test — "Victory on total enemy elimination"

---

## Phase 3: Fog of War Audit

### [FINAL-12] [FOG] Strategic Ledger STALE Intel Shows "No Forces" Instead of Last-Known Band
- **Severity:** MAJOR
- **Category:** INTEGRATION / DATA DISPLAY
- **File:** backend/game_logic/ledger.py:318-319
- **Description:** When displaying STALE (3-5 turn old) intelligence in the Strategic Ledger's Intel tab, the code reads `km.get("strength")` from the frozen snapshot. But PARTIAL-origin snapshots only contain a `"band"` field, not `"strength"`. This causes `km.get("strength", 0)` to return 0, producing `get_strength_band(0)` = "no forces" — incorrectly showing empty when the marshal actually had troops.
- **Evidence:**
  ```python
  # ledger.py:318-319
  elif intel.visibility == STALE:
      frozen = km.get("strength", 0)  # BUG: "strength" never exists for PARTIAL→STALE
      strength_display = f"last seen: {get_strength_band(frozen)}"  # Shows "no forces"
  ```
- **Proposed Fix:** Check for "band" field first:
  ```python
  elif intel.visibility == STALE:
      if "band" in km:
          strength_display = f"last seen: {km['band']}"
      else:
          frozen = km.get("strength", 0)
          strength_display = f"last seen: {get_strength_band(frozen)}"
  ```
- **Test Coverage:** Needs test — "STALE intel displays band correctly for PARTIAL-origin snapshots"

---

## Phase 4: Frontend Contract Audit

### [FINAL-13] [CONTRACT] Missing "is_counter_offer" Field in Incoming Proposal Popup
- **Severity:** MAJOR
- **Category:** CONTRACT
- **File:** backend/game_logic/ai_diplomacy.py (~line 917), backend/main.py:233-242
- **Description:** Godot's `incoming_proposal_popup.gd` expects an `is_counter_offer` boolean to control the [Counter] button visibility. This field is never included in the initial popup creation in `format_incoming_proposal()` or in the safety valve fallback in `_include_popup_passthroughs()`. The executor sets it ad-hoc after creation, but only for counter-offer responses — normal incoming proposals from AI are missing it entirely.
- **Proposed Fix:** Add `"is_counter_offer": False` to `format_incoming_proposal()` in ai_diplomacy.py.
- **Test Coverage:** Needs test — "Incoming proposal popup always has is_counter_offer field"

---

## Phase 5: Serialization Audit

### [FINAL-14] [SERIALIZATION] _intel_events_this_turn Not Serialized
- **Severity:** MINOR
- **Category:** INTEGRATION
- **File:** backend/models/world_state.py:500 (init), missing from to_dict/from_dict
- **Description:** Field `_intel_events_this_turn` is initialized in `__init__()` at line 500 but is NOT included in `to_dict()` or `from_dict()`. On game load, this field will be missing (set to [] by __init__ default, which is acceptable since it's per-turn state). However, if the game is saved mid-turn and loaded, any accumulated intel events are lost.
- **Evidence:** Field `self._intel_events_this_turn = []` at line 500, not found in to_dict (lines 2708-2887) or from_dict (lines 2891-3116).
- **Proposed Fix:** Add to both to_dict and from_dict, or document as intentionally transient (reset per turn).
- **Test Coverage:** Serialization enforcement test skips `_` prefixed fields — needs explicit coverage.

---

## Phase 6: Campaign Log Fog Leaks

### [FINAL-15] [FOG] Campaign Log Shows Enemy Construction/Recruitment at PARTIAL Visibility
- **Severity:** MAJOR
- **Category:** PLAYTEST / FOG LEAK
- **File:** backend/campaign_log.py:279-289
- **Description:** Economy events (construction_started, building_completed, recruitment) for enemy nations are shown when the region has PARTIAL visibility. PARTIAL means "we can see forces there from adjacent scouting" — it does NOT mean we can see their internal economic activity. Construction and recruitment should require FULL visibility (marshal present in region).
- **Evidence:** Live playtest showed:
  ```
  Turn 5: "Construction started: Watchtower in Netherlands" (British territory, PARTIAL vis)
  Turn 4: "Construction complete: Supply Depot in Netherlands" (same)
  Turn 2: "Uxbridge (Britain) recruited 5,000 cavalry" (enemy marshal at PARTIAL)
  Turn 2: "Construction complete: Market in Netherlands" (same)
  ```
  Code at line 285: `if intel.visibility in (FULL, PARTIAL):` — too permissive for economy events.
- **Proposed Fix:** Change line 285 to require FULL only:
  ```python
  if intel.visibility == FULL:  # Construction/recruitment only visible with full intel
      filtered.append(event)
  ```
- **Test Coverage:** Needs test — "Enemy construction not visible at PARTIAL"

---

### [FINAL-16] [FOG] Campaign Log Retreat Events Leak Destination Region
- **Severity:** MAJOR
- **Category:** PLAYTEST / FOG LEAK
- **File:** backend/campaign_log.py:254-263, 425-433
- **Description:** Retreat events are filtered by SOURCE region visibility (line 259-262) but the event includes both `from` and `to` fields. The formatter at line 425-433 displays both: "Uxbridge retreated from Waterloo to Hanover". The destination (Hanover, UNKNOWN visibility) is leaked because only the source is checked.
- **Evidence:** Live playtest:
  ```
  Turn 3: "Uxbridge (Britain) retreated from Waterloo to Hanover"
  ```
  Waterloo is PARTIAL (adjacent to player), Hanover is UNKNOWN. Player should NOT see retreat destination.
  Code at lines 259-262 only checks source region, not destination.
- **Proposed Fix:** For retreat events with only PARTIAL source visibility, strip the `to` field before appending:
  ```python
  if event_type == "retreat" and intel.visibility == PARTIAL:
      event = {**event, "to": ""}  # Hide destination for fogged retreats
  ```
- **Test Coverage:** Needs test — "Retreat destination hidden when destination region fogged"

---

## Phase 7: Extended Playtest — Endgame Validation

### [FINAL-9 UPDATE] [ENDGAME] CONFIRMED: 0 Regions, Capital Lost, Game Continues
- **Severity:** CRITICAL → **CRITICAL+** (worse than initially reported)
- **Category:** ENDGAME / PLAYTEST
- **File:** backend/game_logic/turn_manager.py:801-852
- **Description:** Extended playtest to turn 15 confirmed the WORST-CASE endgame scenario:
  - France controls **0 regions** (all 8+ lost to enemies)
  - **Paris captured by Britain** (Paris controller: Britain)
  - Player has 2 surviving marshals (Davout: 2,752 troops, Drouot: 278 troops)
  - **Game is NOT over** (game_over: False)
  - Player is trapped in enemy territory with no friendly regions to retreat to
  - Player can still receive diplomatic dialogue popups despite having no territory
  - **The game enters a zombie state** — unwinnable but not recognized as defeat
- **Evidence:** Live curl verification:
  ```
  France regions (0): []
  Paris controller: Britain
  Game over: False
  Davout: 2752 troops at Netherlands
  Drouot: 278 troops at Netherlands
  ```
- **Proposed Fix:** Add MULTIPLE defeat conditions:
  1. Capital loss: if Paris controller != France → defeat
  2. Total territory loss: if France controls 0 regions → defeat
  3. Combined: if both capital lost AND < 2 regions → defeat (allow temporary loss during reconquest)
- **Test Coverage:** CRITICAL — needs test covering all three scenarios

---

### [FINAL-17] [ENDGAME] Diplomatic Dialogues Continue After Effective Defeat
- **Severity:** MINOR
- **Category:** ENDGAME / UX
- **File:** backend/game_logic/ai_diplomacy.py (AI proposal generation)
- **Description:** Even with 0 regions and the capital lost, AI nations continue sending diplomatic proposals to France. At turn 15, Prussia sent a proposal requiring Talleyrand dialogue response. This creates a bizarre game state where a defeated nation is negotiating treaties.
- **Evidence:** At turn 15 with 0 French regions, `respond_to_diplomatic_dialogue` was still being triggered by AI proposals.
- **Proposed Fix:** AI proposal generation should check if the target nation has been effectively defeated (0 regions or capital lost) and skip proposals to them.
- **Test Coverage:** Needs test — "AI doesn't propose to eliminated nations"

---

## Summary Table

| # | System | Severity | Category | Description |
|---|--------|----------|----------|-------------|
| 1 | Diplomacy | MAJOR | INTEGRATION | Coalition proposal void never refunds DP |
| 2 | Diplomacy | MAJOR | CASCADE | Vassal rebellion can break armistice lock |
| 3 | Combat | MINOR | INTEGRATION | Exhaustion applied before coordination modifier |
| 4 | Diplomacy | MAJOR | CASCADE | Coalition formation invalidates pending dialogue |
| ~~5~~ | ~~Economy~~ | ~~MAJOR~~ | ~~INTEGRATION~~ | ~~Continental System gold~~ — FALSE POSITIVE |
| 6 | Contract | MINOR | CONTRACT | Save/Load missing active_wars + popup passthroughs |
| 7 | Fog | MAJOR | PLAYTEST | Turn-end events leak enemy marshal activity |
| 8 | Contract | MAJOR | PLAYTEST | fortification_old/new are floats (Golden Rule #2) |
| 9 | Endgame | **CRITICAL** | ENDGAME+PLAYTEST | **Capital lost + 0 regions + game continues** |
| 10 | Endgame | MINOR | ENDGAME | Turn 41 off-by-one |
| 11 | Endgame | MAJOR | ENDGAME | No victory on total enemy elimination |
| 12 | Fog | MAJOR | INTEGRATION | STALE intel shows "no forces" incorrectly |
| 13 | Contract | MAJOR | CONTRACT | Missing is_counter_offer in proposal popup |
| 14 | Serialization | MINOR | INTEGRATION | _intel_events_this_turn not serialized |
| 15 | Fog | MAJOR | PLAYTEST | Campaign log leaks enemy construction/recruitment at PARTIAL |
| 16 | Fog | MAJOR | PLAYTEST | Campaign log leaks retreat destination |
| 17 | Endgame | MINOR | ENDGAME | Diplomatic dialogues continue after effective defeat |
| 18 | AI | MAJOR | CRASH | Division-by-zero in attack opportunity evaluation |
| 19 | AI | MAJOR | CRASH | min() on empty list in stagnation handler |
| 20 | AI | MAJOR | STATE | Enemy AI doesn't check armistice before targeting |
| 21 | Parser | MINOR | INTEGRATION | Diplomatic commands without target parse as None |

## Phase 8: Enemy AI Audit

### [FINAL-18] [AI] Division-by-Zero Crash in Attack Opportunity Evaluation
- **Severity:** MAJOR
- **Category:** INTEGRATION / CRASH
- **File:** backend/ai/enemy_ai.py:2158
- **Description:** In `_find_attack_opportunity()`, line 2158 divides by `enemy.strength` without a zero guard: `base_ratio = combined_strength / enemy.strength`. While enemies are filtered at collection time (line 2135: `enemy.strength > 0`), strength could theoretically reach 0 between filter and division if a multi-step evaluation occurs. Compare with line 2038 which correctly uses `if enemy.strength > 0 else 999`.
- **Proposed Fix:** `base_ratio = combined_strength / max(enemy.strength, 1)`
- **Test Coverage:** Needs test — "AI attack evaluation with 0-strength target doesn't crash"

---

### [FINAL-19] [AI] min() on Empty List Crash in Stagnation Handler
- **Severity:** MAJOR
- **Category:** INTEGRATION / CRASH
- **File:** backend/ai/enemy_ai.py:2932
- **Description:** In `_get_stagnation_action()`, line 2932 calls `min(enemies, ...)` where `enemies` could be empty if all enemy nations are eliminated. `min([])` raises ValueError.
- **Proposed Fix:** Guard: `if not enemies: return None`
- **Test Coverage:** Needs test — "AI stagnation with no enemies doesn't crash"

---

### [FINAL-20] [AI] Enemy AI Doesn't Check Armistice Before Targeting
- **Severity:** MAJOR
- **Category:** INTEGRATION / STATE
- **File:** backend/ai/enemy_ai.py:2125-2158
- **Description:** `_find_attack_opportunity()` filters enemies via `get_enemies_of_nation()` but never checks for active armistice. AI can target nations it has an armistice with, violating the 5-turn armistice lock.
- **Proposed Fix:** Add armistice check: `if world.get_diplomatic_state(nation, enemy.nation) == "ARMISTICE": continue`
- **Test Coverage:** Needs test — "AI respects armistice in attack targeting"

---

## Phase 9: Parser Audit

### [FINAL-21] [PARSER] Diplomatic Commands Without Target Nation Parse as None
- **Severity:** MINOR
- **Category:** INTEGRATION
- **File:** backend/ai/llm_client.py:930
- **Description:** Commands like "Talleyrand, propose peace" (no nation) parse successfully with `target_nation=None`. Downstream dialogue generation doesn't reject None targets, potentially causing NoneType errors in diplomacy.py functions that expect a string.
- **Proposed Fix:** Reject diplomatic commands without a recognized target nation at parse time.
- **Test Coverage:** Needs test — "Diplomatic command without nation returns helpful error"

---

**Totals: 1 CRITICAL, 12 MAJOR, 6 MINOR, 1 FALSE POSITIVE = 20 confirmed findings**

---

## Verification

- **Test suite:** 7,232 tests all passing (0 failures)
- **Live playtest:** 15+ turns played via HTTP curl
- **Debug endpoints:** Properly gated by debug_mode
- **Save/load round-trip:** All core state survives correctly
- **Diplomatic ledger fog filtering:** Working correctly for army strength (FULL/PARTIAL/STALE tiers)
- **Popup passthrough system:** Working correctly on all POST /command paths

---

## Priority Fix Order

### P0 — Critical (game-breaking)
1. **FINAL-9:** Endgame defeat conditions (capital loss, 0 regions, zombie state)

### P1 — Major (gameplay-affecting)
2. **FINAL-7:** Turn-end events fog leak (enemy fortify/attrition visible every turn)
3. **FINAL-8:** fortification_old/new float leak (Golden Rule #2 / potential Godot crash)
4. **FINAL-15:** Campaign log construction/recruitment fog leak
5. **FINAL-16:** Campaign log retreat destination fog leak
6. **FINAL-18:** AI division-by-zero crash risk
7. **FINAL-19:** AI min() crash on empty list
8. **FINAL-20:** AI armistice targeting gap
9. **FINAL-1:** Coalition proposal void DP refund broken
10. **FINAL-4:** Coalition formation stale dialogue
11. **FINAL-11:** No victory on enemy elimination
12. **FINAL-12:** STALE intel "no forces" display bug
13. **FINAL-13:** Missing is_counter_offer field

### P2 — Minor (polish/edge cases)
14. **FINAL-2:** Vassal rebellion armistice lock
15. **FINAL-3:** Modifier application order
16. **FINAL-6:** Load endpoint missing active_wars
17. **FINAL-10:** Turn 41 off-by-one
18. **FINAL-14:** _intel_events_this_turn serialization
19. **FINAL-17:** Diplomatic dialogues after effective defeat
20. **FINAL-21:** Parser diplomatic command without target
