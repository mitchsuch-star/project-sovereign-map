# Systems & Design Audit Report — Ink & Iron
**Started:** 2026-03-23
**Scope:** All non-diplomacy systems + game design + code quality + player experience
**Excluded:** Diplomacy engine internals (audited 3x previously)
**Purpose:** Find bugs, design flaws, elegance issues, fun gaps, and cross-system failures

---

## Pass 1: COMBAT — DOES FIGHTING FEEL RIGHT?

### [P1-1] [COMBAT] Glorious Charge Missing 13+ Post-Combat Systems — Broken Combat Path
- **Severity:** CRITICAL
- **Category:** BUG
- **File:** executor.py:10217-10427
- **Description:** `_execute_glorious_charge()` bypasses nearly ALL post-combat processing: forced retreat, destroyed marshal removal, territory conquest, relationship processing, coordination context, flanking, authority tracker, coalition threat/war exhaustion, vindication, auto-bombardment, reinforcement, and idle tracking. Dead marshals with 0 strength remain in the world permanently. Won battles never capture territory.
- **Evidence:** Function is ~210 lines vs `_execute_attack`'s ~1600 lines. Post-combat blocks between lines 4660-5200 (attack) have no equivalent in charge path.
- **Proposed Fix:** Refactor to route through `_execute_attack` with `glorious_charge=True` flag, or extract shared `_post_combat_processing()`.
- **Test Coverage:** Partial — needs tests for forced retreat, cleanup, territory capture after charge.

### [P1-2] [COMBAT] Coalition Threat/War Exhaustion From Battles Always Zero — Wrong Dict Key
- **Severity:** MAJOR
- **Category:** BUG
- **File:** executor.py:4995-4996
- **Description:** Coalition threat reads `battle_result.get("attacker_casualties", 0)` but the actual key path is `battle_result["attacker"]["casualties"]`. Both `atk_cas` and `def_cas` are always 0, so decisive victory detection, war exhaustion from battle, and coalition shock never fire.
- **Evidence:** combat.py returns casualties at `result["attacker"]["casualties"]` (line 735), not `result["attacker_casualties"]`.
- **Proposed Fix:** `atk_cas = int(battle_result.get("attacker", {}).get("casualties", 0))`
- **Test Coverage:** No — needs test verifying coalition threat increases after decisive battle.

### [P1-3] [COMBAT] Advance-Toward-Enemy Bypasses move_to() — State Leak
- **Severity:** MAJOR
- **Category:** BUG
- **File:** executor.py:3733
- **Description:** When a non-literal marshal's target is out of range, `marshal.location = best_next` is used instead of `marshal.move_to()`. Bypasses cavalry defensive tracking reset, Grouchy HOLD clearing, `moved_this_turn` flag, movement attrition, and engagement checks. Artillery could fire after this implicit move.
- **Evidence:** Line 3733: `marshal.location = best_next` vs all other movement paths using `marshal.move_to()`.
- **Proposed Fix:** Replace with `marshal.move_to(best_next)` + `_calculate_movement_attrition()`.
- **Test Coverage:** No

### [P1-4] [COMBAT] Glorious Charge Missing Engagement Check — Can Teleport Past Enemies
- **Severity:** MAJOR
- **Category:** BUG
- **File:** executor.py:10217-10316
- **Description:** No engagement check exists in `_execute_glorious_charge()`. A cavalry marshal with enemies in their region can still charge a distant target, effectively teleporting past engaged enemies.
- **Evidence:** Compare with `_execute_attack()` lines 3889-3908 which has engagement check.
- **Proposed Fix:** Add engagement check before range check in charge path.
- **Test Coverage:** No

### [P1-5] [COMBAT] Bombardment Collateral Can Resurrect Dead Marshals With 1000 Troops
- **Severity:** MINOR
- **Category:** BUG
- **File:** executor.py:3282-3283
- **Description:** Collateral targets with `strength <= 0` are passed to `_apply_forced_retreat_or_break()`, which gives `max(1000, int(0 * survival_rate))` = 1000 survivors. A marshal killed by collateral gets resurrected as a zombie with 1000 troops.
- **Evidence:** Line 3282: `if force.strength <= 0 and force.name in world.marshals:` calls retreat, which floors at 1000.
- **Proposed Fix:** Add guard: if strength <= 0, pop from world.marshals instead of retreating.
- **Test Coverage:** No

### [P1-6] [COMBAT] get_attack_modifier() / get_defense_modifier() Have Side Effects — Non-Idempotent
- **Severity:** MAJOR
- **Category:** ARCHITECTURE
- **File:** marshal.py:819,841,889
- **Description:** These methods consume one-shot bonuses (`strategic_combat_bonus`, `counter_punch_ready`, `strategic_defense_bonus`) as side effects. Calling twice gives different results. Battle report snapshots work around this by capturing BEFORE the call, but any future preview/display code will silently eat bonuses.
- **Evidence:** Line 819: `self.strategic_combat_bonus = 0`. Line 841: `self.counter_punch_ready = False`. Line 889: `self.strategic_defense_bonus = 0`.
- **Proposed Fix:** Separate consumption into `consume_attack_bonuses()` / `consume_defense_bonuses()` called after modifier calculation. Or add prominent docstring warning.
- **Test Coverage:** Yes — snapshot tests work, but no test validates idempotency.

### [P1-7] [COMBAT] Wellington/Habsburg Resolve Defense Abilities Missing From Battle Report Snapshots
- **Severity:** MAJOR
- **Category:** BUG
- **File:** battle_report.py:143-222
- **Description:** `snapshot_defender_modifiers()` never captures "Reverse Slope Defense" (+5%) or "Habsburg Resolve" (+3%), which are applied in `marshal.py:914-924`. Players see these affect outcomes but the modifier breakdown never shows them — invisible modifiers.
- **Evidence:** marshal.py applies both abilities in `get_defense_modifier()`. battle_report.py has no check for either ability name.
- **Proposed Fix:** Add snapshot blocks for both abilities after the personality modifier section.
- **Test Coverage:** No

### [P1-8] [COMBAT] Square Formation Is Dominated — Artillery +50% Double-Dip
- **Severity:** MAJOR
- **Category:** BALANCE
- **File:** combat.py:336-342, executor.py:3160-3163
- **Description:** Square vs artillery gives +50% melee damage AND +50% bombardment damage AND -15 bombardment morale. The enemy can always respond to square by switching to artillery. Square is only correct when you KNOW only cavalry is coming and no artillery exists. In mixed-arms scenarios, it's a trap option.
- **Evidence:** combat.py:341 `shock_multiplier *= 1.50` + executor.py:3162 `square_bombardment_bonus = 1.50` = double-dip.
- **Proposed Fix:** Reduce artillery melee bonus to +25%, or make square reactive (only activates vs cavalry charges), or block bombardment targeting of squared units (historical: squares could move to dead ground).
- **Test Coverage:** Yes for mechanics, no for balance validation.

### [P1-9] [COMBAT] Mutual Destruction Skips Morale and Battle Counters
- **Severity:** MINOR
- **Category:** BUG
- **File:** combat.py:499-501, 1015-1019
- **Description:** When both armies are destroyed, neither `adjust_morale`, `battles_won`, nor `battles_lost` is called. In multi-marshal battles (deferred path), surviving participants get zero morale change despite witnessing catastrophic destruction.
- **Evidence:** Lines 499-501: mutual destruction path has no morale/counter updates.
- **Proposed Fix:** Apply negative morale deltas (e.g., -20 both sides) in deferred path. Add `battles_lost += 1` for both marshals in normal path.
- **Test Coverage:** No

### [P1-10] [COMBAT] Zero Casualty Stalemate Possible With Tiny Armies
- **Severity:** MINOR
- **Category:** BUG
- **File:** combat.py:858-882
- **Description:** `_calculate_casualties()` returns `int(army_size * casualty_rate)`. With 1-5 troops: `int(1 * 0.15)` = 0 casualties. Creates permanent stalemate.
- **Evidence:** `casualties = int(army_size * casualty_rate)` with no minimum floor.
- **Proposed Fix:** `return max(1, casualties) if army_size > 0 else 0`
- **Test Coverage:** No

### [P1-11] [COMBAT] FORCED_RETREAT_THRESHOLD Duplicated as Magic Number in Two Files
- **Severity:** MINOR
- **Category:** ARCHITECTURE
- **File:** combat.py:614, executor.py:4542
- **Description:** `FORCED_RETREAT_THRESHOLD = 25` defined as local variable in both files. Changing one without the other causes silent behavior divergence.
- **Proposed Fix:** Define once as module-level constant in combat.py, import in executor.py.
- **Test Coverage:** Partial

### [P1-12] [COMBAT] Exhaustion Penalty Message Uses Hardcoded Map Instead of Reading Actual Penalty
- **Severity:** MINOR
- **Category:** BUG
- **File:** combat.py:227-234
- **Description:** Display message uses `penalty_map = {1: 10, 2: 20}` with default 30, while actual penalty in marshal.py:706-713 uses `{1: 0.10, 2: 0.20, 3+: 0.30}`. They happen to align now but could drift.
- **Proposed Fix:** Read actual penalty from marshal and multiply by 100 for display.
- **Test Coverage:** Partial

### [P1-13] [COMBAT] Drill State Cleared Inside combat.py — Golden Rule #1 Boundary Violation
- **Severity:** MINOR
- **Category:** ARCHITECTURE
- **File:** combat.py:279-284
- **Description:** Drill state (`shock_bonus`, `drilling`, `drilling_locked`, `drill_complete_turn`) is cleared directly in combat.py. State mutations should live in marshal.py per Golden Rule #1.
- **Proposed Fix:** Add `clear_drill_state()` method on Marshal, call from combat.py.
- **Test Coverage:** Yes

### [P1-14] [COMBAT] Ney "Bravest of the Brave" Applied in combat.py Not marshal.py
- **Severity:** MINOR
- **Category:** ARCHITECTURE
- **File:** combat.py:191-194
- **Description:** Ney's +2 Shock is applied directly in combat.py (`attacker_shock += 2`). This modifies a skill rather than a modifier, so it's a defensible exception to Golden Rule #1, but it means combat balance comes from two files.
- **Proposed Fix:** Either move into `get_effective_skill("shock")` method or document as intentional exception.
- **Test Coverage:** Yes

### [P1-15] [COMBAT] Form Square Missing retreat_recovery Check
- **Severity:** MINOR
- **Category:** BUG
- **File:** executor.py:8804-8899
- **Description:** `_execute_form_square()` checks `broken` and `retreating` but not `retreat_recovery > 0`. A recovering marshal could form square during recovery.
- **Proposed Fix:** Add `if getattr(marshal, 'retreat_recovery', 0) > 0: return error`.
- **Test Coverage:** No

### [P1-16] [COMBAT] Bombardment Return Fire Has No Minimum — Can Be Zero
- **Severity:** MINOR
- **Category:** BUG
- **File:** executor.py:3151-3167
- **Description:** Unlike garrison combat which has `max(losses, int(strength * 0.02))`, bombardment has no minimum casualty floor. Small targets with terrain cover can produce 0 damage.
- **Proposed Fix:** `defender_casualties = max(1, int(raw_damage * variance))`
- **Test Coverage:** No

### [P1-17] [COMBAT] Flawless Victory Gets Generic "Standard Affair" Observation
- **Severity:** MINOR
- **Category:** DESIGN / UX
- **File:** battle_report.py:717, 442-748
- **Description:** A battle won with zero player casualties (flawless victory) falls through to the default "standard affair, nothing unusual" observation. The most impressive outcome gets the least impressive commentary.
- **Proposed Fix:** Add "won_flawless" template before "won_decisively" at Priority 8.5.
- **Test Coverage:** No

### [P1-18] [COMBAT] Relationship Change Observations Buried at Priority 15 — Nearly Unreachable
- **Severity:** MINOR
- **Category:** UX
- **File:** battle_report.py:737-745
- **Description:** Relationship shift observations are at Priority 15, below almost everything. A rare meaningful narrative moment is almost always overshadowed by higher-priority observations (terrain, stance, drill, casualties).
- **Proposed Fix:** Promote to Priority 4.5 or add as secondary observation appended to primary.
- **Test Coverage:** No

### [P1-19] [COMBAT] Devoted Ally Synergy Can Never Fire During Stalemates
- **Severity:** MINOR
- **Category:** BUG
- **File:** battle_report.py:722, 731-735
- **Description:** Stalemate observation fires at Priority 10. Devoted synergy is Priority 13. If devoted allies fight together in a stalemate, generic "inconclusive affair" overrides the devoted ally narrative.
- **Proposed Fix:** Move devoted_allies check above stalemate (Priority ~9.5).
- **Test Coverage:** No

### [P1-20] [COMBAT] Player Cavalry Crushing Enemy Artillery Gets No Narrative Observation
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** battle_report.py:654-656
- **Description:** Cavalry overrunning artillery observation only fires for defender perspective (we are the artillery that got overrun). Player cavalry successfully overrunning enemy artillery — a satisfying moment — gets no specific commentary.
- **Proposed Fix:** Add attacker-side cavalry counter observation.
- **Test Coverage:** No

### [P1-21] [COMBAT] Tactical Prefix String Building Duplicated Between Normal and Deferred Combat Paths
- **Severity:** MINOR
- **Category:** ARCHITECTURE
- **File:** combat.py:563-608, 1076-1117
- **Description:** Tactical prefix string building (stance, personality, drill, fortify, terrain, cavalry, square, combined arms messages) is duplicated nearly identically between normal and deferred paths. New message types must be manually added to both.
- **Proposed Fix:** Extract `_build_tactical_prefix()` method.
- **Test Coverage:** N/A

### [P1-22] [COMBAT] Bombardment Result Contains Unwrapped Floats for Godot
- **Severity:** MINOR
- **Category:** BUG
- **File:** executor.py:3447-3450
- **Description:** `terrain_modifier`, `fort_old`, `fort_new` sent as raw floats to Godot, violating Golden Rule #2.
- **Proposed Fix:** Wrap with `int()` (send as percentage integers).
- **Test Coverage:** No

### [P1-23] [COMBAT] Balanced and Loyal Personalities Have Zero Combat Modifiers
- **Severity:** DESIGN
- **Category:** DESIGN
- **File:** personality_modifiers.py:88-103
- **Description:** Only aggressive, cautious, and literal have combat modifiers. Balanced and Loyal return empty dicts — no mechanical distinction in combat. Only 3 of 5 personality types create distinct gameplay experiences.
- **Proposed Fix:** Design combat modifiers for Balanced (flexibility, moderate multi-situation bonuses) and Loyal (trust-based attack bonus, morale resistance).
- **Test Coverage:** No

### [P1-24] [COMBAT] Critical Hit/Miss Have No Special Mechanical Effect
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** combat.py:77-83
- **Description:** Critical success (natural 12) and critical failure (natural 2) are detected and tracked but produce no mechanical effect beyond normal roll. They only affect narrative text selection.
- **Proposed Fix:** Consider adding critical bonus: +10% damage and +5 morale for crits, -10% and -5 for crit fails.
- **Test Coverage:** Yes for detection, no mechanical effect exists.

### [P1-25] [COMBAT] Defender Has Massive Structural Advantage — ~2x Troops Needed to Attack
- **Severity:** DESIGN
- **Category:** BALANCE
- **File:** combat.py:33, 128-136
- **Description:** Base +20% defender bonus stacks multiplicatively with terrain (+15%), fortification (+20%), personality (up to +30%), fortify action (+20%). Davout in hills with fortification can reach ~2.47x effective multiplier. Game heavily rewards turtling.
- **Proposed Fix:** Design question. Consider: initiative bonus for first attack in a war, reduced base defender bonus to +15%, or siege attrition weakening long-term defenders. Current system creates interesting defense decisions but fewer interesting attack decisions.
- **Test Coverage:** N/A

### [P1-26] [COMBAT] Magic Numbers Throughout Combat System — No Named Constants
- **Severity:** MINOR
- **Category:** ARCHITECTURE
- **File:** combat.py (multiple), marshal.py (multiple)
- **Description:** ~25+ combat-relevant magic numbers scattered as inline literals. Base casualty rate (0.15), defender bonus (0.2), cavalry counter (1.30), square penalties (0.60/1.50), glorious charge (2x), etc.
- **Proposed Fix:** Create named constants module or class-level constants. Improves readability and balance tuning.
- **Test Coverage:** N/A

---

### Pass 1 Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 1 (P1-1: glorious charge broken) |
| MAJOR | 5 (P1-2 coalition threat zero, P1-3 move_to bypass, P1-4 charge teleport, P1-6 side effects, P1-7 missing snapshots) |
| MINOR | 14 |
| NOTE | 1 |
| DESIGN | 4 |

**Key patterns:**
- Glorious charge is a second-class combat path missing critical post-combat processing
- Coalition threat from battles is silently broken (always 0)
- Magic numbers and code duplication between normal/deferred paths
- Battle report observations have priority ordering issues that suppress meaningful narrative moments
- Only 3 of 5 personality types mechanically differentiated in combat

**Deeper investigation needed:**
- Cross-system: How does the coalition threat bug affect the diplomacy/coalition system overall?
- Cross-system: Do other executor paths besides attack/charge have similar post-combat gaps?
- Balance: With defender advantage + broken charge, is attacking ever the right choice?

---

## Pass 2: ENEMY AI — IS THIS OPPONENT INTERESTING?

### [P2-1] [AI] Spectacular Autonomy Authority Bonus Writes to Wrong Attribute — Always Lost
- **Severity:** CRITICAL
- **Category:** BUG
- **File:** turn_manager.py:449
- **Description:** `_end_autonomy` writes `self.world.authority = ... + 10` but WorldState has no `authority` attribute. Real authority is at `self.world.authority_tracker.authority`. Creates a spurious attribute that is never read, never serialized, and has zero gameplay effect. The test validates the broken codepath, so it passes despite the bug.
- **Evidence:** `getattr(self.world, 'authority', 50)` always returns 50 (default). Real authority initialized at 100 via `authority_tracker`.
- **Proposed Fix:** Change to `self.world.authority_tracker.modify_authority(+10)`. Update test.
- **Test Coverage:** Yes, but test validates broken path.

### [P2-2] [AI] Missing is_at_war Filter in 7+ AI Decision Locations
- **Severity:** MAJOR
- **Category:** BUG
- **File:** enemy_ai.py:2477, 2603, 3260, 4071, 4103, 4118, 4154
- **Description:** Multiple defender/enemy-presence checks filter by `m.nation != nation` but don't check `world.is_at_war()`. AI treats neutral/allied marshals as blockers: won't recapture homeland if neutral standing there, won't garrison if ally adjacent, won't fortify near neutral borders.
- **Evidence:** Line 2477: `defenders = [m for m in world.marshals.values() if m.location == best_target and m.strength > 0 and m.nation != nation]` — no war check.
- **Proposed Fix:** Add `and world.is_at_war(nation, m.nation)` to all filter comprehensions.
- **Test Coverage:** No

### [P2-3] [AI] Zero Error Handling in Enemy Phase — Single Crash Aborts Entire Turn
- **Severity:** MAJOR
- **Category:** ARCHITECTURE
- **File:** turn_manager.py:485-608
- **Description:** No try/except blocks in `_process_enemy_turns` or `_process_autonomous_marshals`. A single exception in any AI action (KeyError, AttributeError, division by zero) propagates to the API endpoint, leaving game state partially mutated. Player is stuck.
- **Evidence:** 4 nations × 6 max actions = 24 iterations, each involving complex decision trees with pathfinding and combat resolution. Zero error recovery.
- **Proposed Fix:** Wrap each nation's processing with try/except, logging errors and continuing.
- **Test Coverage:** No

### [P2-4] [AI] 2-AP Stance Transitions Not Accounted For in AI Planning
- **Severity:** MAJOR
- **Category:** BUG
- **File:** enemy_ai.py:2337-2342
- **Description:** AI returns `stance_change -> aggressive` expecting 1 AP cost, but Def→Agg costs 2 AP via executor. AI plans stance change (2 AP) + attack (1 AP) = 3 AP minimum, but budget may only be 3 AP total, leaving no margin for error. In many cases the stance change eats the budget intended for the attack.
- **Evidence:** P4 lines 2337-2342: returns stance change before attack without checking AP cost.
- **Proposed Fix:** Before returning stance change, calculate actual cost. If Def↔Agg would cost 2 AP, either skip the stance change or verify remaining budget supports stance + attack.
- **Test Coverage:** No

### [P2-5] [AI] Cooldown Decrements Run Per-Nation Not Per-Turn — 3x Too Fast
- **Severity:** MINOR
- **Category:** BUG
- **File:** enemy_ai.py:521-538, 652, 655-661
- **Description:** `_decrement_cooldowns` and `ai_refortify_cooldown` decrement run inside `process_nation_turn`. With 3 enemy nations, cooldowns tick down 3x per game turn. A 2-turn cooldown effectively lasts ~0.67 turns.
- **Evidence:** Line 652: `self._decrement_cooldowns(world)` inside per-nation loop.
- **Proposed Fix:** Move cooldown decrement to turn_manager.py before nation loop, or track last-decrement turn number.
- **Test Coverage:** No

### [P2-6] [AI] Overwatch Penalty Self-Counts Target Artillery
- **Severity:** MINOR
- **Category:** BUG
- **File:** enemy_ai.py:1893-1907
- **Description:** `_evaluate_target_ratio` overwatch calculation counts the target marshal as their own overwatch unit. Missing `m.name != target.name` exclusion.
- **Evidence:** Filter at line 1895 has no name exclusion. Artillery target counts against itself as overwatch.
- **Proposed Fix:** Add `and m.name != target.name` to filter.
- **Test Coverage:** No

### [P2-7] [AI] Homeland Defense Uses Raw Personality Instead of Effective Personality
- **Severity:** MINOR
- **Category:** BUG
- **File:** enemy_ai.py:2498-2500
- **Description:** Uses `getattr(marshal, 'personality_type', None)` instead of `_get_effective_personality()`. Literal marshals don't get converted to cautious for homeland defense decisions.
- **Proposed Fix:** Replace with `self._get_effective_personality(marshal, world)`.
- **Test Coverage:** No

### [P2-8] [AI] AI_DEBUG = True Hardcoded in Production
- **Severity:** MINOR
- **Category:** UX
- **File:** enemy_ai.py:114
- **Description:** `AI_DEBUG = True` hardcoded, flooding stdout with hundreds of debug messages every AI turn.
- **Proposed Fix:** Set to False by default, or use `os.getenv("AI_DEBUG", "false")`.
- **Test Coverage:** N/A

### [P2-9] [AI] Vassal Courting Events Silently Discarded
- **Severity:** MINOR
- **Category:** BUG
- **File:** turn_manager.py:291-296
- **Description:** Vassal courting events are generated and debug-printed but never returned or stored. UI has no way to display "Austria is courting your vassal."
- **Proposed Fix:** Return courting events alongside proposal, or store on world for dispatch.
- **Test Coverage:** No

### [P2-10] [AI] Capital Proximity Alert Fires Every Turn — No Deduplication
- **Severity:** MINOR
- **Category:** UX
- **File:** turn_manager.py:700-731
- **Description:** Same alert every turn if enemy parks near capital. 10 turns of "Enemy forces spotted near Paris!" is noise.
- **Proposed Fix:** Track previously-fired (enemy, capital) pairs and skip duplicates.
- **Test Coverage:** No dedup test

### [P2-11] [AI] _last_enemy_phase_results Written But Never Read — Dead State
- **Severity:** MINOR
- **Category:** ARCHITECTURE
- **File:** turn_manager.py:112
- **Description:** `world._last_enemy_phase_results` is set but never read anywhere. Not serialized.
- **Proposed Fix:** Remove field, or add TODO for planned use.
- **Test Coverage:** No

### [P2-12] [AI] start_turn() Method Is Dead Code
- **Severity:** MINOR
- **Category:** ARCHITECTURE
- **File:** turn_manager.py:45-67
- **Description:** Only called in `__main__` test block at bottom of file. Never called in production. Income is handled by `_advance_turn_internal()`.
- **Proposed Fix:** Remove or mark as unused.
- **Test Coverage:** No

### [P2-13] [AI] No Nation-Level Strategic Identity
- **Severity:** DESIGN
- **Category:** DESIGN
- **File:** enemy_ai.py (entire file)
- **Description:** Nation differentiation is entirely driven by marshal personality types. Austria plays identically to any nation with the same personality mix. Britain doesn't prioritize defense, Prussia doesn't pursue maneuver warfare. No nation-level doctrines or objectives.
- **Proposed Fix:** Add small nation-level modifiers: Britain +0.1 attack threshold (more defensive), Prussia -0.1 (more aggressive).
- **Test Coverage:** N/A

### [P2-14] [AI] Always Attacks Weakest/Nearest — Predictable After 5 Games
- **Severity:** DESIGN
- **Category:** DESIGN
- **File:** enemy_ai.py:2317-2322
- **Description:** Aggressive AI picks weakest target, non-aggressive picks nearest. No surprise target selection. Experienced players will easily predict AI behavior.
- **Proposed Fix:** Add 10-20% chance of sub-optimal target selection for variety.
- **Test Coverage:** N/A

### [P2-15] [AI] No Feint/Diversion Behavior
- **Severity:** DESIGN
- **Category:** DESIGN
- **File:** enemy_ai.py (entire file)
- **Description:** AI never creates diversions — threatening one region while attacking another. Each marshal independently picks best action. Makes AI honest but transparent.
- **Proposed Fix:** Simple heuristic: "if 2+ marshals target same region, redirect one to adjacent."
- **Test Coverage:** N/A

### [P2-16] [AI] AI Never Issues Strategic Orders (MOVE_TO, PURSUE, HOLD, SUPPORT)
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** enemy_ai.py (entire file)
- **Description:** AI makes single-action decisions, never multi-turn strategic orders. Can't pursue fleeing enemies across map. Documented as future improvement.
- **Test Coverage:** N/A
- -THIS IS INTENTIONAL IGNORE

### [P2-17] [AI] Mood Variance Creates Genuine Unpredictability (POSITIVE)
- **Severity:** NOTE
- **Category:** ELEGANCE
- **File:** enemy_ai.py:457-490
- **Description:** ±8-15% mood variance by personality creates genuine unpredictability. Player can't perfectly predict Blucher's attack timing. Personality crossover ranges create "bad days" and "feeling bold" moments that feel human. Excellent design.
- **Test Coverage:** Yes

### [P2-18] [AI] Counter-Punch and Artillery Positioning Create Memorable Moments (POSITIVE)
- **Severity:** NOTE
- **Category:** ELEGANCE
- **File:** enemy_ai.py:1437-1448, 4785-4888
- **Description:** Counter-punch gives cautious AI dramatic defensive reversals. Artillery scoring creates visible combined-arms behavior (park behind infantry, bombard fortifications). Both generate memorable "Wellington at Waterloo" and "Grand Battery" moments.
- **Test Coverage:** Yes

---

### Pass 2 Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 1 (P2-1: authority bonus lost) |
| MAJOR | 3 (P2-2 war filter missing, P2-3 no error handling, P2-4 2-AP stance) |
| MINOR | 8 |
| NOTE | 3 |
| DESIGN | 3 |

**Key patterns:**
- Missing `is_at_war` checks cause AI to treat allies/neutrals as enemies (7+ locations)
- Zero error handling in turn processing — any exception kills the turn
- AI is competent but predictable: always weakest/nearest target, no feints or strategic orders
- Cooldown system undermined by per-nation decrement (3x too fast)
- Positive: mood variance, counter-punch, and artillery positioning create good moments

**Deeper investigation needed:**
- How does the authority bug (P2-1) interact with the defiance system?
- Do the missing war filters cause visible gameplay issues in multi-nation diplomatic scenarios?
- How many other per-nation vs per-turn timing bugs exist?

---

## Pass 3: STRATEGIC COMMANDS — DOES THE CAMPAIGN LAYER WORK?

### [P3-1] [STRATEGIC] StrategicOrder Missing Serialization for last_contact Fields — Infinite Interrupt Loop After Load
- **Severity:** MAJOR
- **Category:** BUG
- **File:** strategic.py:2071-2097, marshal.py StrategicOrder dataclass
- **Description:** `_handle_blocked_path` sets `order.last_contact_enemy` and `order.last_contact_turn` dynamically. These fields prevent infinite interrupt loops (if same enemy within 1 turn, suppress re-ask). NOT declared as dataclass fields, NOT in to_dict(), NOT in from_dict(). Lost on save/load. After loading, blocked-path interrupts fire every turn forever.
- **Evidence:** `getattr(order, 'last_contact_enemy', None)` at line 2071 uses getattr precisely because field may not exist.
- **Proposed Fix:** Add `last_contact_enemy: Optional[str] = None` and `last_contact_turn: Optional[int] = None` to StrategicOrder dataclass + serialization.
- **Test Coverage:** No — serialization enforcement test only checks fields on test instance.

### [P3-2] [STRATEGIC] HOLD March Ignores Cavalry movement_range — Single Step Per Turn
- **Severity:** MAJOR
- **Category:** BUG
- **File:** strategic.py:1190-1243
- **Description:** HOLD march-to-position moves only 1 region/turn. MOVE_TO, PURSUE, and SUPPORT all use `getattr(marshal, 'movement_range', 1)` for cavalry 2-region movement. Cavalry ordered to "hold Vienna" takes twice as long as MOVE_TO to same destination.
- **Evidence:** `_execute_hold` line 1204: `next_region = path[0]` (single move). Compare `_execute_move_to` line 714: `regions_to_move = getattr(marshal, 'movement_range', 1)`.
- **Proposed Fix:** Add movement loop matching MOVE_TO/PURSUE/SUPPORT pattern.
- **Test Coverage:** No

### [P3-3] [STRATEGIC] resolve_direction Hardcodes "Paris" as Capital
- **Severity:** MINOR
- **Category:** BUG
- **File:** strategic_parser.py:104-112
- **Description:** `resolve_direction()` hardcodes `capital = "Paris"` for "back/rear/home" keywords. Non-French AI marshals ordered to "fall back" would path toward Paris instead of their own capital.
- **Proposed Fix:** Use `NATION_CAPITALS.get(marshal.nation, "Paris")`.
- **Test Coverage:** No

### [P3-4] [STRATEGIC] PURSUE Path Never Stored on order.path — UI Shows "0 Turns Remaining"
- **Severity:** MINOR
- **Category:** BUG / UX
- **File:** strategic.py:958-1039
- **Description:** PURSUE recalculates path into local variable each turn, never stores on `order.path`. Strategic Ledger always shows 0 turns remaining for PURSUE orders.
- **Proposed Fix:** Set `order.path` after recalculating for UI display.
- **Test Coverage:** No

### [P3-5] [STRATEGIC] Triple-Redundant HOLD max_turns Expiry Check
- **Severity:** MINOR
- **Category:** ARCHITECTURE
- **File:** strategic.py:606-625, 1166-1188, 1887-1913
- **Description:** HOLD expiry checked in three places with slightly different field usage (`issued_turn` vs `started_turn`). If expiry logic changes, three sites must update.
- **Proposed Fix:** Consolidate to `_check_condition` as single authority.
- **Test Coverage:** Yes

### [P3-6] [STRATEGIC] Alphabetical Processing Starvation — One Marshal's Interrupt Blocks All Others
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** strategic.py:130-136
- **Description:** When a marshal's strategic order produces a `requires_input` interrupt, processing stops (`break`). Marshals processed alphabetically, so "Davout" consistently blocking means "Ney" never gets strategic orders processed. Code acknowledges with TODO comment.
- **Proposed Fix:** Process all non-interrupting marshals first, then present interrupts.
- **Test Coverage:** No

### [P3-7] [STRATEGIC] _extract_target_text Uses Substring While _detect_strategic_type Uses Regex
- **Severity:** MINOR
- **Category:** BUG
- **File:** strategic_parser.py:308-321, 324-365
- **Description:** Type detection uses word-boundary regex; target extraction uses plain `if keyword in cleaned`. Inconsistency can cause edge case mismatches.
- **Proposed Fix:** Use same matching strategy in both.
- **Test Coverage:** Unlikely to cover edge cases

### [P3-8] [STRATEGIC] Timed HOLD Uses issued_turn vs started_turn Inconsistently
- **Severity:** MINOR
- **Category:** BUG
- **File:** strategic.py:611, 1167, 1897
- **Description:** Checks 1 and 3 use `issued_turn or started_turn`, but `_check_condition` uses just `started_turn`. Could produce different expiry timings if fields diverge.
- **Proposed Fix:** Standardize on one field.
- **Test Coverage:** No

### [P3-9] [STRATEGIC] SUPPORT Auto-Completes on "Ally Safe" Even With max_turns Condition
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** strategic.py:1566-1593
- **Description:** "Support Ney for 3 turns" completes instantly if no enemies nearby on arrival. The "ally safe" check fires before max_turns condition can prevent it.
- **Proposed Fix:** Don't auto-complete on "ally safe" when max_turns condition is present.
- **Test Coverage:** Unclear

### [P3-10] [STRATEGIC] Cannon Fire "continue_order" Costs -2 Trust — Punishes Player Command Authority
- **Severity:** NOTE
- **Category:** BALANCE
- **File:** strategic.py:288-309
- **Description:** Telling marshal to continue march (ignore cannon fire) costs -2 trust. But the player IS exercising command authority — the penalty punishes them for commanding. Meanwhile canceling costs -3, making both options negative.
- **Proposed Fix:** Consider no trust penalty for "continue" (player's prerogative).
- **Test Coverage:** Unknown

### [P3-11] [STRATEGIC] Design Quality: 7-8/10 — Strong Campaign Feel
- **Severity:** NOTE
- **Category:** DESIGN
- **Description:** Strategic orders successfully create campaign-level tension. Cannon fire interrupts are the crown jewel. Personality-driven behavior (literal never interrupts for cannon fire, aggressive sallies from HOLD) creates distinct experiences. HOLD is the richest order type (8/10). PURSUE handles fog well (7/10). SUPPORT feels thin — auto-completes too aggressively (6/10). Missing: supply lines, march fatigue, coordinated orders.
- **Test Coverage:** N/A

---

### Pass 3 Summary

| Severity | Count |
|----------|-------|
| MAJOR | 2 (P3-1 serialization, P3-2 cavalry speed) |
| MINOR | 6 |
| NOTE | 3 |

---

## Pass 4: DISOBEDIENCE & PERSONALITY — DO MARSHALS FEEL ALIVE?

### [P4-1] [PERSONALITY] Grouchy (Literal) Has Zero Functional Triggers — Completely Silent
- **Severity:** MAJOR
- **Category:** DESIGN
- **File:** personality.py:159-163, objection_v2.py:1074-1090
- **Description:** Literal personality has triggers defined (`ambiguous_order`, `contradictory_orders`, `change_of_plans`) but ALL are TODO Phase 3. `evaluate_literal()` unconditionally returns `ConcernLevel.NONE`. `calculate_defiance_chance()` returns 0.0 for literal. Grouchy never objects, never defies, never has a personality moment. He is a stat block, not a character. The player will not develop feelings about Grouchy over 30 turns.
- **Evidence:** objection_v2.py:1090: `return ConcernLevel.NONE` for ALL actions, ALL situations.
- **Proposed Fix:** Implement "change_of_plans" trigger (detectable from order history). Give Grouchy a unique "painful literalism" model: asks clarifying questions, follows letter not spirit, creates HOLD-too-long notifications.
- **Test Coverage:** Tests confirm literal never objects (which is the problem)

### [P4-2] [PERSONALITY] Balanced and Loyal Have No V2 Evaluator — Personality-Dead
- **Severity:** MAJOR
- **Category:** DESIGN
- **File:** objection_v2.py:1094-1098, 1138-1141
- **Description:** `PERSONALITY_EVALUATORS` only maps aggressive, cautious, literal. Balanced and Loyal hit `return ConcernLevel.NONE`. Any future marshal with these personalities will have zero personality interactions.
- **Proposed Fix:** Implement balanced evaluator (objects to suicide attacks) and loyal evaluator (objects only to treasonous orders).
- **Test Coverage:** No

### [P4-3] [PERSONALITY] Vindication last_change_turn Always Records 0
- **Severity:** MINOR
- **Category:** BUG
- **File:** vindication.py:176-177
- **Description:** `getattr(pending.get('original_order', {}), 'turn_recorded', None)` — dicts don't have attributes via getattr. Always evaluates to None, so `last_change_turn` is always 0. Decay timing works around this via `max(last_change, last_obj)`.
- **Proposed Fix:** Use `pending.get('original_order', {}).get('turn_recorded', 0)`.
- **Test Coverage:** No direct test

### [P4-4] [PERSONALITY] Failed Defiance Roll Resets ALL Vindication — Punishes Self-Control
- **Severity:** MINOR
- **Category:** BALANCE
- **File:** defiance.py:251-253
- **Description:** Marshal who considers defiance but obeys (failed_roll) loses entire vindication score. Marshal didn't do anything wrong — they obeyed. Combined with -3 trust, this punishes the "correct" outcome.
- **Evidence:** Line 252: `marshal.vindication_score = 0` on failed roll.
- **Proposed Fix:** Remove vindication reset on failed roll. The -3 trust is sufficient consequence.
- **Test Coverage:** Yes (confirms current behavior, not desired)

### [P4-5] [PERSONALITY] V1/V2 Dual Objection Systems Coexist — Maintenance Risk
- **Severity:** MINOR
- **Category:** ARCHITECTURE
- **File:** disobedience.py:652-711 (V1), objection_v2.py (V2)
- **Description:** Two complete objection systems fully implemented. V1 severity.py still used for strategic objections via `check_strategic_objection()`. V2 used for tactical objections via executor. Creates confusion about which path is active.
- **Proposed Fix:** Consolidate strategic path to V2. Mark V1 as deprecated.
- **Test Coverage:** Both have tests

### [P4-6] [PERSONALITY] _exposes_capital Hardcodes "Paris"
- **Severity:** MINOR
- **Category:** BUG
- **File:** personality.py:408
- **Description:** Same pattern as P3-3. `capital = "Paris"` hardcoded instead of using world.player_capital or NATION_CAPITALS.
- **Proposed Fix:** Use `NATION_CAPITALS.get(nation, "Paris")`.
- **Test Coverage:** No

### [P4-7] [PERSONALITY] Defiance Cooldown Asymmetry: Failed Roll Vindication Reset Too Harsh
- **Severity:** MINOR
- **Category:** BALANCE
- **File:** defiance.py:246, 271
- **Description:** Failed roll (marshal obeyed) gets 1-turn cooldown AND vindication reset. Inconclusive (marshal defied, nothing happened) gets 3-turn cooldown but no reset. A marshal who defied and achieved nothing is treated more gently than one who obeyed. Perverse incentive.
- **Proposed Fix:** Failed roll: keep 1-turn cooldown, remove vindication reset.
- **Test Coverage:** Yes

### [P4-8] [PERSONALITY] Defensive Vindication Never Resolves If Enemy Doesn't Attack — Narrative Dead End
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** defiance.py:158-162, world_state.py:4946-4954
- **Description:** Marshal defiantly fortifies, enemy never comes, entry silently cleaned up after 5 turns. No narrative closure. Player never knows if the fortification was wise or wasted.
- **Proposed Fix:** Generate Berthier observation on stale cleanup: "Ney's defiant fortification went untested."
- **Test Coverage:** Partial

### [P4-9] [PERSONALITY] _is_fortified Checks Region Not Marshal — Always Returns False for Attacks
- **Severity:** MINOR
- **Category:** BUG
- **File:** personality.py:385-397
- **Description:** V1 `_is_fortified(target, game_state)` uses target (marshal name) as region key. No region named "Wellington" exists. Always returns False. Superseded by V2 evaluator.
- **Proposed Fix:** Deprecate V1 path or fix lookup.
- **Test Coverage:** No (V2 has tests)

### [P4-10] [PERSONALITY] Trust Is a Well-Designed Relationship System (POSITIVE)
- **Severity:** NOTE
- **Category:** ELEGANCE
- **Description:** Rubber-band effect (HOSTILE tier = 1.5x gains), authority anti-exploit (>65% trust ratio = -2 authority), vindication memory, and redemption threshold create genuine management challenge. The "always trust" and "always insist" strategies both fail — the sweet spot requires reading each situation. This IS good design.
- **Test Coverage:** Yes (extensive)

### [P4-11] [PERSONALITY] Defiance Creates Genuine Drama (POSITIVE)
- **Severity:** NOTE
- **Category:** ELEGANCE
- **Description:** Berthier flavor texts for defiance outcomes are among the best writing in the codebase. 4-outcome table (right/wrong/inconclusive/failed) with asymmetric trust/authority consequences makes defiance feel consequential. When Ney charges without orders and wins, it creates a memorable narrative moment.
- **Test Coverage:** Yes

### [P4-12] [PERSONALITY] Authority Anti-Exploit Design Is Elegant (POSITIVE)
- **Severity:** NOTE
- **Category:** ELEGANCE
- **Description:** Three reinforcing mechanisms prevent "always trust" exploit: excessive trust penalty (-2/-3 authority), reduced trust gains (0.5x at 80%+), and threshold events. Creates genuine tension between individual relationships and overall command authority.
- **Test Coverage:** Yes

### [P4-13] [PERSONALITY] 30-Turn Marshal Bonding Assessment
- **Severity:** DESIGN
- **Category:** DESIGN
- **Description:** Would players develop feelings about their marshals over 30 turns?
  - **Ney (Aggressive):** YES — rich objection templates, dramatic defiance moments, recklessness integration, 15+ unique dialogue lines. Players will remember Ney.
  - **Davout (Cautious):** PROBABLY — players learn to trust his judgment. But bland dialogue templates ("The odds are not in our favor") reduce emotional connection. Needs richer voice.
  - **Grouchy (Literal):** NO — zero personality interactions. Follows orders silently. Players will forget he has a personality.
  - **Balanced/Loyal:** Cannot assess — no implementation.
- **Proposed Fix:** Priority: (1) Give Grouchy literalism interactions, (2) Enrich Davout's voice, (3) Add trust tier transition notifications, (4) Add vindication milestone observations.
- **Test Coverage:** N/A

---

### Pass 4 Summary

| Severity | Count |
|----------|-------|
| MAJOR | 2 (P4-1 Grouchy silent, P4-2 balanced/loyal empty) |
| MINOR | 7 |
| NOTE | 3 (all positive) |
| DESIGN | 1 |

**Key patterns:**
- Literal personality is completely non-functional — biggest soul deficit
- V1/V2 dual system creates maintenance confusion
- Defiance system is well-designed but vindication is under-communicated
- Failed defiance roll punishes self-control (vindication reset too harsh)
- Trust system is genuinely well-designed as a management challenge

---

## Pass 5: FOG OF WAR — DOES UNCERTAINTY CREATE TENSION?

### [P5-1] [FOG] LLM Prompt Builder Receives Unfiltered Enemy Data
- **Severity:** MAJOR
- **Category:** EXPLOIT
- **File:** main.py:70-78
- **Description:** `get_llm_game_state()` passes raw enemy marshal data (exact locations, troop counts) to LLM prompt. In `LLM_MODE=anthropic`, LLM sees all enemies regardless of fog and could mention them in response text, leaking fogged information.
- **Evidence:** Lines 70-78: `enemies` dict uses `world.get_enemy_marshals()` with no fog filter. Meanwhile `get_filtered_game_state_summary()` (for Godot) properly filters.
- **Proposed Fix:** Filter enemies through `get_region_intel()` — only include PARTIAL+ visibility.
- **Test Coverage:** No

### [P5-2] [FOG] Campaign Log Missing Fog Filter for 5 Deep-Audit Event Types
- **Severity:** MAJOR
- **Category:** BUG
- **File:** campaign_log.py:283-312
- **Description:** `war_declaration`, `defensive_cascade`, `offensive_cascade`, `coalition_declared`, `coalition_dissolved` have no fog-filter branch in `filter_campaign_log()`. For AI-AI events, they silently drop. Coalition events' fields don't match `_is_player_event()` checks.
- **Proposed Fix:** Add fog-filter branch. Coalition events should always show (target France). War/cascade events need PARTIAL+ visibility check.
- **Test Coverage:** No

### [P5-3] [FOG] Ledger Intel Tab Shows "last seen: 0" for Decayed PARTIAL Intel
- **Severity:** MINOR
- **Category:** BUG
- **File:** ledger.py:285-287
- **Description:** Decayed PARTIAL → STALE snapshots have `band` but no `strength`. Ledger does `km.get("strength", 0)` → displays "last seen: 0". Should display band text instead.
- **Proposed Fix:** Check `km.get("band")` first; if present and strength missing, show band.
- **Test Coverage:** No

### [P5-4] [FOG] Dispatch Hardcodes Player Nation as "France"
- **Severity:** NOTE
- **Category:** ARCHITECTURE
- **File:** dispatch.py:50
- **Description:** `player_nation = "France"` hardcoded with TODO comment. All other fog consumers use `world.player_nation`.
- **Proposed Fix:** Replace with `world.player_nation`.
- **Test Coverage:** N/A (not currently a bug)

### [P5-5] [FOG] Fog System Is Well-Designed — Creates Genuine Uncertainty (POSITIVE)
- **Severity:** NOTE
- **Category:** DESIGN
- **Description:** 5-tier visibility hierarchy is clear. Decay timeline (FULL→STALE at turn 3, →LAST_KNOWN at turn 5) creates meaningful uncertainty on 19 regions. Player with 4 marshals sees ~8-10 regions, leaving ~9-11 unknown. Scout action creates meaningful cost/benefit trade-off. Watchtower synergy rewards infrastructure. Players can feel SMART for reading fog correctly (STALE intel + empty regions = inference). All API endpoints properly fog-filtered (except P5-1). No helplessness: own regions always PARTIAL+, controller always visible, all commands into fog legal.
- **Test Coverage:** Comprehensive

---

### Pass 5 Summary

| Severity | Count |
|----------|-------|
| MAJOR | 2 (P5-1 LLM leak, P5-2 missing fog filters) |
| MINOR | 1 |
| NOTE | 2 (1 positive) |

---

## Pass 6: TURN FLOW & GAME PACING

### [P6-1] [PACING] Player AP Treaty Clause Overwritten Each Turn — Treaty Penalties Have No Effect
- **Severity:** MAJOR
- **Category:** BUG
- **File:** world_state.py:3724, 3739
- **Description:** `_process_treaty_clauses()` reduces `max_actions_per_turn` at line 3724, but `calculate_max_actions()` at line 3739 resets it to `4+bonus` a few lines later. AI nations are handled correctly (reset BEFORE treaty clauses), but the player reduction is immediately discarded. AP penalty treaty clauses against France have zero effect.
- **Evidence:** Line 3724: treaty clause modifies `max_actions_per_turn`. Line 3739: `self.max_actions_per_turn = self.calculate_max_actions()` overwrites.
- **Proposed Fix:** Move `calculate_max_actions()` call to BEFORE `_process_treaty_clauses()`, or have treaty clauses apply a modifier rather than a direct override.
- **Test Coverage:** No

### [P6-2] [PACING] Admin AP → Gold Exploit — 2 Unused Admin = 150g/Turn Free Income
- **Severity:** MAJOR
- **Category:** EXPLOIT
- **File:** world_state.py:3741-3744
- **Description:** `_process_admin_ap_income()` converts unused admin AP to gold (75g per unused admin AP). With 2 admin AP per turn and few admin actions worth taking early game, a player who never uses admin actions gets 150g/turn free. This is ~30% of France's base income (~500g). Optimal play is to avoid admin actions entirely.
- **Evidence:** Lines 3741-3744: `unused = admin_ap - used_admin; gold += unused * 75`.
- **Proposed Fix:** Reduce conversion rate (50g), cap to 1 unused AP, or remove the conversion entirely and increase base income.
- **Test Coverage:** Unknown

### [P6-3] [PACING] Victory Threshold Inconsistency — world_state.py vs turn_manager.py
- **Severity:** MAJOR
- **Category:** BUG
- **File:** world_state.py:3805, turn_manager.py:766
- **Description:** world_state uses `ceil(19*0.75)=15 regions` for turn-40 time victory check. turn_manager uses `int(19*0.77)=14 regions` for the same condition. Different thresholds for what should be the same check.
- **Proposed Fix:** Consolidate to single constant. Use same threshold in both files.
- **Test Coverage:** Likely

### [P6-4] [PACING] No Escalating Pressure — Passive France Can Turtle Indefinitely
- **Severity:** MAJOR
- **Category:** BALANCE
- **File:** world_state.py (advance_turn), enemy_ai.py
- **Description:** No growing external threat punishes passivity. A fortified France with economic surplus faces no escalation. The 40-turn limit is the only constraint. The coalition system adds pressure but coalition threat accumulates from aggression, not passivity.
- **Proposed Fix:** Add escalating pressure: (1) AI nations grow stronger over time (recruitment ramp), (2) coalition forms against stalemate (not just aggression), (3) event system with crises that demand response.
- **Test Coverage:** N/A

### [P6-5] [PACING] CLAUDE.md Says "3 AP" But Actual Is 4 Military + 2 Admin
- **Severity:** MINOR
- **Category:** UX
- **File:** CLAUDE.md
- **Description:** CLAUDE.md multiple references to "3 AP per turn" are outdated. Actual system is 4 military AP + 2 admin AP.
- **Proposed Fix:** Update CLAUDE.md references.
- **Test Coverage:** N/A

### [P6-6] [PACING] Infantry Manpower Regen Trivializes Losses — 5k/Turn Recovery
- **Severity:** MINOR
- **Category:** BALANCE
- **File:** world_state.py manpower regen
- **Description:** France regenerates ~5k infantry manpower per turn across controlled regions. With 4 marshals at ~15k average, total infantry is ~60k. 5k/turn = 8.3% recovery. A 10k casualty battle is replaced in 2 turns. This makes infantry losses trivially recoverable, reducing combat consequence.
- **Proposed Fix:** Reduce regen rate, or add war exhaustion modifier that reduces regen during prolonged wars.
- **Test Coverage:** N/A

### [P6-7] [PACING] Supply Attrition Caps at 3% — Stacking Armies Has Minimal Cost
- **Severity:** MINOR
- **Category:** BALANCE
- **File:** world_state.py supply attrition
- **Description:** Even extreme overcrowding (3x supply capacity) only causes 3% attrition. Stacking 5 marshals in one region for a deathball strategy costs almost nothing in attrition.
- **Proposed Fix:** Increase cap to 5-8% or add progressive scaling.
- **Test Coverage:** N/A

### [P6-8] [PACING] British Naval Income Is 300g Flat Regardless of Territory
- **Severity:** MINOR
- **Category:** BALANCE
- **File:** world_state.py
- **Description:** Britain gets 300g/turn naval income even if they control zero land regions. They cannot be economically defeated short of total conquest.
- **Proposed Fix:** Scale naval income with number of coastal regions controlled or overall strategic position.
- **Test Coverage:** N/A

### [P6-9] [PACING] TurnManager.start_turn() Is Dead Code — Latent Double-Income Risk
- **Severity:** MINOR
- **Category:** ARCHITECTURE
- **File:** turn_manager.py:45-67
- **Description:** `start_turn()` applies income but is never called in production. Only called in the inline `__main__` test block. If ever called in production alongside `advance_turn()`, income would double.
- **Proposed Fix:** Remove or clearly mark as deprecated/test-only.
- **Test Coverage:** No

---

### Pass 6 Summary

| Severity | Count |
|----------|-------|
| MAJOR | 4 (P6-1 AP overwrite, P6-2 admin exploit, P6-3 victory threshold, P6-4 no pressure) |
| MINOR | 5 |

**Key patterns:**
- Economy favors passivity (admin→gold exploit, trivial manpower recovery, low attrition)
- Treaty AP clauses against France are silently broken
- No escalating pressure mechanism creates turtle-and-blitz optimal strategy

---

## Pass 7: GODOT FRONTEND — DOES IT FEEL GOOD?

### [P7-1] [GODOT] api_client.gd: Single HTTPRequest — Race Condition on Rapid Requests
- **Severity:** MAJOR
- **Category:** BUG
- **File:** api_client.gd:12
- **Description:** Single `HTTPRequest` node with single `pending_callback`. If second request fires before first completes, first callback silently lost. Second callback receives first response's data. The diplomacy wizard already works around this with its own `_http` node.
- **Proposed Fix:** Use request queue with paired callbacks, or create new HTTPRequest per request.
- **Test Coverage:** N/A

### [P7-2] [GODOT] main.gd: _trim_old_messages Strips BBCode Formatting
- **Severity:** MINOR
- **Category:** BUG
- **File:** main.gd:1823-1837
- **Description:** `_trim_old_messages()` uses `get_parsed_text()` (strips BBCode), then re-appends plain lines. After trimming, all remaining messages lose color formatting.
- **Proposed Fix:** Use `output_display.text` (preserves BBCode) instead.
- **Test Coverage:** N/A

### [P7-3] [GODOT] main.gd: Diplomatic Top Bar Not Updated in 5+ Response Handlers
- **Severity:** MINOR
- **Category:** BUG
- **File:** main.gd:2774, 1914, 2513, 2324, 2126
- **Description:** `_on_coalition_popup_dismissed`, `_on_objection_response`, `_on_glorious_charge_response`, `_on_capture_choice_response`, `_on_redemption_response` — none call `_update_diplomatic_top_bar(response)`. DP counter, threat indicator, Talleyrand status become stale after these interactions.
- **Proposed Fix:** Add the call to all response handlers that update game state.
- **Test Coverage:** N/A

### [P7-4] [GODOT] main.gd: _on_load_result Doesn't Restore War Panel or Diplomatic State
- **Severity:** MINOR
- **Category:** BUG
- **File:** main.gd:2378-2412
- **Description:** After loading saved game, war status panel and diplomatic top bar show data from previous game state. Missing calls to `_update_diplomatic_top_bar`, `_process_active_wars`.
- **Proposed Fix:** Add these calls after load, matching `_on_connection_test` pattern.
- **Test Coverage:** N/A

### [P7-5] [GODOT] map.gd: Tooltip Can Extend Off-Screen
- **Severity:** MINOR
- **Category:** UX
- **File:** map.gd:682
- **Description:** Tooltip positioned at `mouse + Vector2(15,15)` with no bounds checking. Tall tooltips near screen edge clip.
- **Proposed Fix:** Clamp position against viewport rect. Flip to left/above when near edges.
- **Test Coverage:** N/A

### [P7-6] [GODOT] map.gd: REGION_CONNECTIONS/POSITIONS Hardcoded — Must Sync With Backend
- **Severity:** NOTE
- **Category:** ARCHITECTURE
- **File:** map.gd:4-47
- **Description:** Region adjacencies and positions duplicated as Godot constants. Must manually sync with backend/models/region.py. No validation check.
- **Proposed Fix:** Add startup validation or serve from backend.
- **Test Coverage:** N/A

### [P7-7] [GODOT] main.gd: Excessive Debug Prints in Production
- **Severity:** MINOR
- **Category:** ELEGANCE
- **File:** main.gd:744-788, map.gd:586-595
- **Description:** 15+ verbose debug print statements throughout ("GLORIOUS_CHARGE CHECK:", "REDEMPTION EVENT detected"). Spams Godot Output panel.
- **Proposed Fix:** Remove or gate behind `const DEBUG = false`.
- **Test Coverage:** N/A

### [P7-8] [GODOT] Terminal Interface Is Charming But Dense (DESIGN)
- **Severity:** NOTE
- **Category:** DESIGN
- **Description:** BBCode terminal with gold/cream/red palette is thematically excellent. But 40+ lines per turn output (battle report + Berthier + dispatch + coordination). Consider collapsible sections or condensed mode.

### [P7-9] [GODOT] War Status Panel + Diplomacy Wizard Flow Is Well-Designed (POSITIVE)
- **Severity:** NOTE
- **Category:** DESIGN
- **Description:** 3-layer war system (HUD → detail popup → wizard handoff) is clean. Compact HUD with tug-of-war meters provides at-a-glance status. Click-to-expand detail. Negotiate/target buttons hand off to wizard cleanly. Panel auto-hides during modals.

---

### Pass 7 Summary

| Severity | Count |
|----------|-------|
| MAJOR | 1 (P7-1 race condition) |
| MINOR | 5 |
| NOTE | 3 (1 positive) |

---

## Pass 8: PARSER & NATURAL LANGUAGE — DOES COMMANDING FEEL NATURAL?

### [P8-1] [PARSER] "invest in " and "release " Keywords Too Broad — Hijack Non-Vassal Commands
- **Severity:** MAJOR
- **Category:** BUG
- **File:** llm_client.py:767, 777
- **Description:** `"invest in "` matches "invest in defenses", "invest in training". `"release "` matches "release Ney from orders", "release prisoners". Both route to vassal actions incorrectly.
- **Evidence:** `elif any(kw in command_lower for kw in ["invest in vassal", "invest vassal", "invest in ",])` — bare "invest in " is too broad.
- **Proposed Fix:** Remove bare keywords. Keep specific variants. Add vassal nation name matching.
- **Test Coverage:** No

### [P8-2] [PARSER] "help" Keyword Matches Any Command Containing "help"
- **Severity:** MINOR
- **Category:** BUG
- **File:** llm_client.py:636
- **Description:** `"help" in command_lower` matches "Ney, help Davout" — routes to help screen instead of support/reinforce.
- **Proposed Fix:** Use word boundary check + guard against marshal names following.
- **Test Coverage:** No

### [P8-3] [PARSER] "withdraw to" Parsed as Retreat Before Strategic MOVE_TO
- **Severity:** MINOR
- **Category:** BUG
- **File:** llm_client.py:680
- **Description:** "withdraw" hits retreat check before "withdraw to" can be caught as MOVE_TO. Strategic parser rescues this, but without world context (world=None), it stays as bare retreat.
- **Proposed Fix:** Check "withdraw to" and "fall back to" (with preposition) BEFORE bare "withdraw"/"fall back".
- **Test Coverage:** Partial

### [P8-4] [PARSER] parser.py valid_actions List Out of Sync With VALID_ACTIONS
- **Severity:** NOTE
- **Category:** ARCHITECTURE
- **File:** parser.py:44-81 vs validation.py:21-74
- **Description:** parser.py maintains its own `valid_actions` list instead of importing from `validation.py`. Missing ~9 entries (pursue, reinforce, march, release_vassal, diplomatic_*).
- **Proposed Fix:** Import `VALID_ACTIONS` from validation.py. Single source of truth.
- **Test Coverage:** No

### [P8-5] [PARSER] known_enemies List Hardcoded and Incomplete
- **Severity:** MINOR
- **Category:** BUG
- **File:** parser.py:91
- **Description:** `known_enemies = ["Wellington", "Uxbridge", "Blucher", "Gneisenau"]` — missing ArchdukeCharles, Schwarzenberg, Reynier. Fuzzy matching for these names won't work.
- **Proposed Fix:** Derive dynamically from world state.
- **Test Coverage:** No

### [P8-6] [PARSER] "shell " Requires Trailing Space — Misses End-of-String
- **Severity:** MINOR
- **Category:** BUG
- **File:** llm_client.py:659
- **Description:** `"shell "` won't match "Drouot, shell" (no trailing space). Trailing space prevents matching "Marshall" but breaks end-of-input.
- **Proposed Fix:** Use `re.search(r'\bshell\b', command_lower)`.
- **Test Coverage:** No

### [P8-7] [PARSER] "Prussians"/"British" Set as Target But Are Not Valid — Silently Cleared
- **Severity:** MINOR
- **Category:** BUG
- **File:** llm_client.py:817-820
- **Description:** Mock parser extracts nationality words as target ("Prussians"), but validation clears them (not valid marshal/region). "Attack the Prussians" loses its targeting.
- **Proposed Fix:** Resolve nationality to nearest enemy marshal of that nation.
- **Test Coverage:** Partial

### [P8-8] [PARSER] Command Vocabulary Discovery Is Poor for New Players
- **Severity:** DESIGN
- **Category:** UX
- **File:** parser.py:556-580
- **Description:** Help screen shows raw action names (`form_square`, `invest_vassal`) instead of natural language examples. Rich vocabulary (bombard, cannonade, dig in, entrench) is non-discoverable.
- **Proposed Fix:** Restructure help into categories with natural language examples. Hide raw action names.
- **Test Coverage:** N/A

### [P8-9] [PARSER] Napoleonic Voice Partially Achieved — Success Path Is Silent
- **Severity:** DESIGN
- **Category:** ELEGANCE
- **Description:** Berthier error recovery is genuinely charming and in-character. But 90%+ of commands succeed and get zero character interaction from parser. Even a one-line template per personality on success ("At once, Sire!") would dramatically improve immersion.
- **Test Coverage:** N/A

### [P8-10] [PARSER] resolve_direction Hardcodes "Paris" (Duplicate of P3-3, P4-6)
- **Severity:** MINOR
- **Category:** BUG
- **File:** strategic_parser.py:104-112
- **Description:** Third instance of hardcoded "Paris" capital. Non-French marshals with "fall back" orders path toward Paris.
- **Proposed Fix:** Use `NATION_CAPITALS.get(marshal.nation, "Paris")`.
- **Test Coverage:** No

---

### Pass 8 Summary

| Severity | Count |
|----------|-------|
| MAJOR | 1 (P8-1 broad keywords) |
| MINOR | 6 |
| NOTE | 1 |
| DESIGN | 2 |

**Key patterns:**
- Mock parser keyword ordering creates subtle mis-routing bugs
- Broad vassal keywords hijack unrelated commands
- Command vocabulary is rich but non-discoverable
- Success path has no Napoleonic voice — only errors feel immersive

---

## Pass 9: CODE ELEGANCE & ARCHITECTURE

**Scope:** 10 largest backend files (~38,000 lines), overall architecture assessment

### [P9-01] [ARCHITECTURE] executor.py is a 14,410-line God Object with 52 _execute_ methods
- **Severity:** MAJOR
- **Category:** ARCHITECTURE
- **File:** executor.py (entire file)
- **Description:** `CommandExecutor` is a single class containing 52 `_execute_*` methods spanning military actions, diplomacy, debug commands, vassal management, objection handling, strategic commands, and capture mechanics. At 14,410 lines, it is impossible for a new developer to understand in 30 minutes. Method count by domain: Military ~15, Economy ~6, Strategic ~4, Diplomacy ~14, Debug ~1 (867 lines), Capture ~4, Objection ~3, Vassal ~4.
- **Proposed Fix:** Extract into domain-specific executor modules: `military_executor.py`, `economy_executor.py`, `diplomatic_executor.py`, `debug_executor.py`. Keep `executor.py` as the router/orchestrator. StrategicExecutor (P9-18) already proves this pattern works.

### [P9-02] [ARCHITECTURE] _execute_attack is 1,763 lines — the longest function in the codebase
- **Severity:** MAJOR
- **Category:** ARCHITECTURE
- **File:** executor.py:3468-5231
- **Description:** `_execute_attack` handles drill cancellation, artillery checks, cavalry recklessness, terrain blocking, target resolution, garrison combat, alliance paradox, fog move-into-combat, coordination, reinforcements, battle resolution, casualty distribution, pursuit damage, forced retreat, region capture, victory checks, and more. A single function should not handle 20+ distinct concerns.
- **Proposed Fix:** Split into `_validate_attack_preconditions()`, `_resolve_attack_target()`, `_execute_combat_resolution()`, `_process_attack_aftermath()`.

### [P9-03] [ELEGANCE] Drill state check copy-pasted 3 times in executor.py
- **Severity:** MINOR
- **Category:** ELEGANCE
- **File:** executor.py:3505, 5248, 6757
- **Description:** The drill cancellation check (drilling → drilling_locked error or cancel) is copy-pasted identically in `_execute_attack`, `_execute_defend`, and `_execute_move`.
- **Proposed Fix:** Extract to `_check_and_cancel_drill(self, marshal, action_name)`.

### [P9-04] [ARCHITECTURE] Auto-end-turn logic duplicated between execute() and _execute_end_turn()
- **Severity:** MINOR
- **Category:** ARCHITECTURE
- **File:** executor.py:2406-2499 and executor.py:885-1057
- **Description:** The auto-end-turn block in `execute()` manually replicates financial summary, morning dispatch, autosave, capture choice, victory check, and tactical event hoisting from `_execute_end_turn()`. Any change to one must be mirrored in the other.
- **Proposed Fix:** Extract shared turn-end processing into `_build_turn_end_result()`.

### [P9-05] [ARCHITECTURE] _process_dialogue_choice is 1,098 lines — a state machine encoded as if/elif
- **Severity:** MAJOR
- **Category:** ARCHITECTURE
- **File:** executor.py:12030-13128
- **Description:** Handles every diplomatic dialogue action via a 1,098-line chain of `elif action == "..."` blocks with 30+ branches.
- **Proposed Fix:** Refactor into a dispatch table: `_DIALOGUE_HANDLERS = {"dismiss": self._handle_dismiss, ...}` with each handler as a focused 30-80 line method.

### [P9-06] [ARCHITECTURE] _execute_debug is 867 lines — should be a separate module
- **Severity:** MINOR
- **Category:** ELEGANCE
- **File:** executor.py:9007-9874
- **Description:** Debug command handler is 867 lines of if/elif parsing for 30+ debug subcommands. Pure developer tooling cluttering the production executor class.
- **Proposed Fix:** Extract to `commands/debug_commands.py`.

### [P9-07] [ARCHITECTURE] enemy_ai.py _evaluate_marshal is 624 lines
- **Severity:** MINOR
- **Category:** ARCHITECTURE
- **File:** enemy_ai.py:1067-1691
- **Description:** P1-P8 decision tree as a single 624-line function. Each priority level is 30-80 lines that could be separate methods.
- **Proposed Fix:** Extract each priority as a method. Main `_evaluate_marshal` becomes a clean pipeline of ~30 lines.

### [P9-08] [ARCHITECTURE] WorldState.__init__ is 424 lines of field initialization
- **Severity:** MINOR
- **Category:** ARCHITECTURE
- **File:** world_state.py:74-498
- **Description:** Initializes ~100 fields spanning military, economy, diplomacy, fog, AI tracking, notifications, vassal, coalition, and popup state. Hard to scan.
- **Proposed Fix:** No code change recommended — risk/benefit too low. Add a table-of-contents comment listing field groups with line numbers.

### [P9-09] [ARCHITECTURE] _process_tactical_states is 480 lines in WorldState — game logic in model class
- **Severity:** MINOR
- **Category:** ARCHITECTURE
- **File:** world_state.py:4440-4920
- **Description:** Handles per-turn processing for drilling, fortification decay, retreat recovery, broken marshal respawn, cavalry recklessness, and overwatch. This is game logic, not state management.
- **Proposed Fix:** Move to `game_logic/tactical_states.py` as standalone function.

### [P9-10] [ELEGANCE] resolve_battle is 725 lines — mixes calculation with message generation
- **Severity:** MINOR
- **Category:** ELEGANCE
- **File:** combat.py:95-820
- **Description:** Combat math and narrative message generation are interleaved throughout. Ability triggers for 6+ marshals are inline.
- **Proposed Fix:** Separate into `_resolve_combat_math()` and `_build_battle_narrative()`.

### [P9-11] [ELEGANCE] Magic number 50000 for "major battle" threshold
- **Severity:** NOTE
- **Category:** ELEGANCE
- **File:** executor.py:2579
- **Description:** `is_major = combined >= 50000` — no named constant.
- **Proposed Fix:** Add `MAJOR_BATTLE_THRESHOLD = 50000`.

### [P9-12] [ELEGANCE] Magic number 15000 for garrison strength cap appears 3 times
- **Severity:** NOTE
- **Category:** ELEGANCE
- **File:** world_state.py:952, 3559, 3561
- **Description:** Garrison cap `15000` and regen `2000` hardcoded with no named constant.
- **Proposed Fix:** Add `GARRISON_MAX_STRENGTH = 15000` and `GARRISON_REGEN_PER_TURN = 2000`.

### [P9-13] [ELEGANCE] 125 inline imports scattered through executor.py
- **Severity:** NOTE
- **Category:** ELEGANCE
- **File:** executor.py (throughout)
- **Description:** Only 8 imports at file top; 117 are inline inside methods to avoid circular dependencies. Symptom of God Object (P9-01).
- **Proposed Fix:** Splitting executor.py would resolve most circular imports.

### [P9-14] [ARCHITECTURE] enemy_ai.py hand-rolls "enemies in region" queries 43 times
- **Severity:** MINOR
- **Category:** ELEGANCE
- **File:** enemy_ai.py (throughout)
- **Description:** 43 instances of `[m for m in world.marshals.values() ...]` that could use `world.get_enemies_in_region()` and similar existing methods.
- **Proposed Fix:** Replace hand-rolled comprehensions with existing WorldState helper methods.

### [P9-15] [ARCHITECTURE] Data flow direction is clean — models never import game_logic
- **Severity:** NOTE (positive finding)
- **Category:** ARCHITECTURE
- **Description:** Import dependency graph follows clean layering: `models/ → game_logic/ → commands/ → main.py`. No upward dependencies.
- **Proposed Fix:** None — good architecture.

### [P9-16] [ARCHITECTURE] Diplomacy engine files have clean module boundaries
- **Severity:** NOTE (positive finding)
- **Category:** ARCHITECTURE
- **Description:** diplomacy.py, coalition.py, vassal.py, ai_diplomacy.py, diplomatic_dialogue.py, diplomatic_templates.py each have clear single responsibility and clean function boundaries. This is the model for how to decompose executor.py.
- **Proposed Fix:** None — use as template.

### [P9-17] [ELEGANCE] Recruit cost calculation duplicated between executor.py and enemy_ai.py
- **Severity:** MINOR
- **Category:** ELEGANCE
- **File:** executor.py:7847-7860, enemy_ai.py:4356-4379, 4462-4476
- **Description:** Recruit gold cost formula (capital discount, settling premium) appears in 3 places.
- **Proposed Fix:** Extract shared function `calculate_recruit_cost()`.

### [P9-18] [ARCHITECTURE] strategic.py is well-structured — good example of domain extraction
- **Severity:** NOTE (positive finding)
- **Category:** ARCHITECTURE
- **File:** strategic.py
- **Description:** `StrategicExecutor` is a separate class delegating to `CommandExecutor`. Clean constructor, clear entry point, per-order-type methods. This is exactly the pattern to apply elsewhere.
- **Proposed Fix:** None — use as template for P9-01.

### [P9-19] [ELEGANCE] main.py execute_command is 540 lines with deeply nested routing
- **Severity:** MINOR
- **Category:** ELEGANCE
- **File:** main.py:475-1015
- **Description:** Single HTTP endpoint handler doing game-over guard, parsing, dialogue routing, Berthier recovery, executor delegation, result post-processing, and response formatting.
- **Proposed Fix:** Extract routing phases into helper functions.

### [P9-20] [ELEGANCE] getattr(marshal, 'drilling', False) used despite 'drilling' being guaranteed
- **Severity:** NOTE
- **Category:** ELEGANCE
- **File:** executor.py (12 occurrences), enemy_ai.py (18 occurrences)
- **Description:** `drilling` and other fields are defined in `Marshal.__init__` and guaranteed to exist, yet accessed with defensive `getattr()` 30+ times.
- **Proposed Fix:** Replace with direct attribute access for fields guaranteed by `__init__`.

### [P9-21] [ARCHITECTURE] Function naming is descriptive and consistent across all 10 files
- **Severity:** NOTE (positive finding)
- **Category:** ELEGANCE
- **Description:** Method names are universally descriptive. A new developer can understand what each function does from its name alone.

### [P9-22] [ARCHITECTURE] marshal.py get_attack/defense_modifier upholds Golden Rule 1
- **Severity:** NOTE (positive finding)
- **Category:** ARCHITECTURE
- **Description:** Combat modifiers single source in marshal.py is perfectly maintained. combat.py reads the modifier result and never recalculates.

### [P9-23] [ELEGANCE] Bug fix history comments in enemy_ai.py (lines 62-111) belong in git history
- **Severity:** NOTE
- **Category:** ELEGANCE
- **File:** enemy_ai.py:62-111
- **Description:** 50 lines of "BUG FIX HISTORY" with commit hashes from January 2026. Belongs in git log, not source code.
- **Proposed Fix:** Move to `docs/archive/ENEMY_AI_BUG_HISTORY.md`.

### [P9-24] [ELEGANCE] Error handling uses consistent dict-return pattern
- **Severity:** NOTE (positive finding)
- **Category:** ELEGANCE
- **Description:** All files use `return {"success": False, "message": "..."}`. 158 such returns in executor.py alone. Consistent, reliable, no exceptions through the stack.

### [P9-25] [ARCHITECTURE] CLAUDE.md provides clear beginner's path — but executor.py defeats it
- **Severity:** NOTE
- **Category:** ARCHITECTURE
- **Description:** CLAUDE.md is exceptionally well-organized. But once a developer opens executor.py (directed there for 10+ concerns), they face 14,410 lines. Decomposing executor.py (P9-01) would make the beginner's path work end-to-end.

---

### Pass 9 Summary

| Category | MAJOR | MINOR | NOTE | Total |
|----------|-------|-------|------|-------|
| ARCHITECTURE | 3 | 5 | 7 | 15 |
| ELEGANCE | 0 | 4 | 6 | 10 |
| **Total** | **3** | **9** | **13** | **25** |

**Key patterns:**
- executor.py God Object is the single biggest architectural issue (14,410 lines, 52 methods, 125 imports)
- Six functions exceed 500 lines; `_execute_attack` at 1,763 is worst
- Code duplication in drill checks, auto-end-turn, recruit costs (~200 lines)
- **Positive:** Import layering is clean, function naming is excellent, error handling is consistent, diplomacy subsystem is well-decomposed, Golden Rule 1 is perfectly maintained

---

## Pass 10: GAME DESIGN COHERENCE — THE BIG PICTURE

### [P10-01] [CORE LOOP] The 40-Turn Horizon Creates a Ticking Clock Without Dramatic Pacing
- **Severity:** MAJOR
- **Category:** DESIGN
- **Description:** Hard-caps at 40 turns with binary victory (15/19 regions). No mid-game narrative arc, no escalation phases, no "point of no return." Turn 5 feels the same as turn 35. Coalition threshold (60) is the only escalation.
- **Proposed Fix:** Introduce 2-3 "era" markers: Expansion (turns 1-12), Resistance (13-25), Endgame (26-40). Each era triggers a dispatch event and modifies mechanics.

### [P10-02] [VICTORY] Victory Conditions Are Purely Territorial — No Diplomatic Victory
- **Severity:** MAJOR
- **Category:** DESIGN
- **Description:** Despite rich diplomacy (7 treaty states, vassals, alliances, coalition system), victory is exclusively measured by region control. No diplomatic hegemony, survival, or graduated victory. Diplomacy has zero bearing on winning.
- **Proposed Fix:** Add victory tiers: Military (18/19), Hegemonic (15+ regions + 2 vassals + Continental System), Diplomatic (12+ regions + 2 alliances + no wars). Score as Decisive/Standard/Pyrrhic.

### [P10-03] [PERSONALITY] The Aggressive/Cautious/Literal Triangle Is the Game's Greatest Strength
- **Severity:** NOTE
- **Category:** DESIGN
- **Description:** Ney refusing to defend, Davout objecting to suicidal attacks, Grouchy following bad orders — these are historically resonant moments no other strategy game delivers. The personality system makes marshals feel like characters, not units. This IS the game.

### [P10-04] [PERSONALITY] Literal Personality Is Mechanically Hollow
- **Severity:** MAJOR
- **Category:** DESIGN
- **Description:** Grouchy's Literal personality is the game's most compelling concept (the historical Grouchy Moment — following orders while Waterloo happens nearby) but has zero working triggers. `personality.py:505-510` — all three triggers are TODO. The "game's signature dramatic beat" (VISION.md) does not exist in code.
- **Proposed Fix:** Top implementation priority for Pre-EA. Minimum: when battle occurs in adjacent region and Grouchy has HOLD/MOVE_TO order, he continues current orders instead of responding.

### [P10-05] [ECONOMY] Economy Is Simple but Functionally Invisible
- **Severity:** MINOR
- **Category:** BALANCE
- **Description:** France starts with 800g, earns ~1100g/turn, spends ~865g on upkeep. Surplus is enormous. Recruitment costs (200-400g) are cheap. Building costs are one-time. The player never feels "I cannot afford this war."
- **Proposed Fix:** Increase upkeep to create meaningful tradeoffs (e.g., 8g/1000 would put France near break-even), or accept economy as background resource.

### [P10-06] [DIPLOMACY] The Diplomacy System Is Rich but Strategically Optional
- **Severity:** MAJOR
- **Category:** DESIGN
- **Description:** A player who ignores diplomacy and simply attacks with Ney and Davout can conquer 15/19 regions by turn 25. The 7 treaty states, 4 DP/turn, acceptance formula, Talleyrand defiance, vassal loyalty — all impressive but the game never forces the player to use them.
- **Proposed Fix:** (1) Make starting military position harder (France at war with coalition-like block, diplomacy needed to fracture alliances). (2) Add "war weariness" after 15+ turns of continuous war.

### [P10-07] [COALITION] Coalition System Creates Authentic Napoleonic Drama
- **Severity:** NOTE
- **Category:** DESIGN
- **Description:** Three-tier warning (murmurs/brewing/instant), threat from conquests mirroring historical dynamic, "breaking the coalition" mechanics, ordinal naming — all well-designed.

### [P10-08] [VASSAL] Vassal System Is Over-Engineered for 19-Region Map
- **Severity:** MINOR
- **Category:** DESIGN
- **Description:** 3 autonomy levels, tribute, loyalty (6+ modifiers), rebellion cascade, investment, marshal assimilation, Continental System enforcement — built for 1805 80-province map but only 2 nations (Saxony, possibly Austria) are realistic vassalization targets with 19 regions.
- **Proposed Fix:** Accept as "pre-built for scale." Simplify UX to 2 autonomy levels for EA.

### [P10-09] [COMBAT] Combat Resolution Creates Genuine Uncertainty Without Randomness Theater
- **Severity:** NOTE
- **Category:** DESIGN
- **Description:** 2d6 system with skill modifiers (0.85x to 1.20x) creates meaningful variance without making superior play pointless. Modifier stacking rewards preparation without guaranteeing outcomes.

### [P10-10] [FOG] Fog of War Creates Authentic Command Uncertainty
- **Severity:** NOTE
- **Category:** DESIGN
- **Description:** 5-tier visibility with intel aging creates "knowing roughly where the enemy is but not exactly." Strength bands ("substantial force") feel thematically right. Scouting as deliberate action creates real opportunity cost.

### [P10-11] [SYSTEMS] advance_turn() Processes 20+ Systems Sequentially — Fragile Ordering
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** world_state.py:3468-3760
- **Description:** 300+ lines of sequential processing with comments noting ordering requirements. Fragile to additions.
- **Proposed Fix:** Consider a TurnPhaseProcessor with explicit dependency ordering for future-proofing.

### [P10-12] [AI] Enemy AI Is Competent but Not Personality-Driven Enough
- **Severity:** MINOR
- **Category:** DESIGN
- **Description:** Priority system produces reasonable behavior. But Wellington behaves like "cautious bot" not "the Duke." Blucher like "aggressive bot" not "Marshal Forwards." AI should make characteristically bad decisions.
- **Proposed Fix:** Add 1-2 personality-specific AI behaviors per character.

### [P10-13] [THEME] The Game Feels Like Being Napoleon — Most of the Time
- **Severity:** NOTE
- **Category:** DESIGN
- **Description:** "Marshal Ney, attack Wellington" creates the right fantasy. Morning dispatch reinforces HQ atmosphere. Objection system creates the central tension. Thematic core is strong. Biggest gap: the player never hears Napoleon's own voice.

### [P10-14] [TALLEYRAND] Talleyrand Is the Most Interesting Advisor Design in Strategy Gaming
- **Severity:** NOTE
- **Category:** DESIGN
- **Description:** An advisor who is competent but unreliable, might sabotage proposals (2-30% chance), has confrontation and redemption arcs, creates real "keep vs replace" choices. Genuinely innovative. Needs more personality in dialogue.

### [P10-15] [COMPLEXITY] 35+ Mechanical Systems Approaching Comprehension Ceiling
- **Severity:** MAJOR
- **Category:** UX
- **Description:** Combat, stances, drill/fortify, personalities, trust, authority, vindication, defiance, strategic commands (4), coordination (5 sources), relationships, fog (5 levels), economy, manpower (3 pools), supply attrition, buildings (5), garrisons, diplomacy (7 states), DP, war score, acceptance formula, treaties (13 clauses), vassal (loyalty/autonomy/tribute/rebellion), coalition (threat/brewing/formation/dissolution), Talleyrand defiance, Continental System, tactical triangle, cavalry recklessness, artillery bombardment, notifications (20+ types), dispatch, campaign log. ~35 systems for 19 regions and 11 marshals.
- **Proposed Fix:** Complexity gate for EA: unlock systems as player progresses. Turns 1-5: combat+movement+personalities. Turns 6-10: economy+fog. Turns 11+: diplomacy+coalition.

### [P10-16] [REPLAY] Replay Variety Is Currently Low — Fixed Starting Conditions
- **Severity:** MINOR
- **Category:** DESIGN
- **Description:** Every game starts identically. No scenario selection, no randomized enemy disposition. The personality system creates procedural drama, but opening 5 turns play similarly each game.
- **Proposed Fix:** Low priority for EA. Post-EA: add 2-3 scenarios (1805, 1812, 1813).

### [P10-17] [CONTINENTAL SYSTEM] Continental System Is Mechanically Vestigial
- **Severity:** MINOR
- **Category:** DESIGN
- **Description:** Implemented as -75g/turn trade cap with Britain (max 200g across all members). Britain's 300g naval income is unaffected. The mechanic that caused the Spanish Ulcer and Russian campaign should be more consequential.
- **Proposed Fix:** Make it reduce British naval income by 30%, or create diplomatic tension (nations forced in lose 5 relation/turn with France).

### [P10-18] [CORE LOOP] The Objection System Is the Primary "One More Turn" Engine
- **Severity:** NOTE
- **Category:** DESIGN
- **Description:** Issue order → Marshal objects → Trust/Insist/Compromise → See consequences. This creates narrative threads ("Ney charged without orders, now I need to rescue him"). Vindication tracking who was right and trust spirals are the primary engagement engine.

### [P10-19] [CUTTING] If You Cut 30% — What Survives?
- **Severity:** DESIGN
- **Category:** DESIGN
- **Description:** Irreducible core: (1) Natural language commands, (2) 3 personality types + objection system, (3) Combat with modifiers, (4) Map with movement/fog, (5) Coalition as escalation, (6) Morning dispatch as information delivery. For cuts: remove vassal system (merge into diplomacy), simplify economy, remove Continental System, collapse 7 diplomatic states to 4, remove artillery as separate unit type, remove buildings. ~35 systems → ~20.

### [P10-20] [MISSING] Most Impactful Addition: Named "Grand Battles"
- **Severity:** DESIGN
- **Category:** DESIGN
- **Description:** When total troops > 80k, or capital at stake, or 3+ marshals per side: pre-battle Berthier assessment, per-participant casualty breakdown, permanent campaign log entry, +5 coalition threat. All ingredients already exist — battle naming, Berthier observations, coordination. Just need a ceremonial wrapper.

---

### Pass 10 Summary

| Severity | Count |
|----------|-------|
| MAJOR | 5 (pacing, victory, literal personality, diplomacy optional, complexity ceiling) |
| MINOR | 5 |
| NOTE | 7 |
| DESIGN | 3 |

**Fun Verdict:** A game you'd want to play for 15-20 turns. The "talk to your generals" fantasy works. To reach 30+ turns, needs era pacing and diplomatic victory so late game differs from early game.

**Most Fun Moment:** Ney defies retreat, charges Wellington, wins — trust soars. Three turns later he charges into a trap, 20k lost. Vindication tracks it all.

**Most Frustrating Moment:** Turn 25, control 14/19 regions, nothing can stop you, but must grind 6 more for 77% threshold. No diplomatic shortcut.

**Design Tightness: 7/10.** Combat, personality, trust, coordination form tight core. Diplomacy/vassal run parallel rather than intersecting. Continental System most "bolted on."

---

## Pass 11: DEGENERATE STRATEGIES & EXPLOIT HUNTING

### [P11-01] [COMBAT] Deathball Stacking Is Viable but Mitigated
- **Severity:** DESIGN
- **Category:** BALANCE
- **Description:** All 4 French marshals (173k total) in one region steamroll any single defender. Coordination caps at +25%/+20%, supply attrition at max 3%/turn is mild. Paris holds 60k (50k * 1.2 urban). The deathball works.
- **Evidence:** Supply attrition formula `min(0.03, excess_ratio * 0.015)` is gentle. Coordination caps at executor.py:368-369.
- **Proposed Fix:** Add stacking penalty beyond 3 marshals (e.g., command confusion: -5% per extra marshal). Or increase supply attrition scaling.

### [P11-02] [MAP] Belgium Chokepoint — Dominant Opening Rush
- **Severity:** MAJOR
- **Category:** BALANCE
- **Description:** Belgium is adjacent to Netherlands (Britain capital), Waterloo (Wellington), Rhineland (Prussia). Ney starts in Belgium with cavalry movement range 2. Turn 1: Ney + Davout = 120k on Waterloo (52k Wellington in hills). A Belgium-first opening threatening British capital within 2 turns is the clear dominant strategy.
- **Evidence:** region.py Belgium adjacency includes Netherlands, Waterloo, Rhineland, Paris. Ney starts there with movement_range=2.
- **Proposed Fix:** Historically correct (real Waterloo campaign). Consider British naval reinforcements or move Wellington to Netherlands so capital has a strong defender.

### [P11-03] [AP ECONOMY] Player Can Optimize AP Perfectly — No Waste
- **Severity:** MINOR
- **Category:** DESIGN
- **Description:** 4 CP + 2 Admin AP per turn. Pools are independent — spending CP never affects admin. A skilled player never wastes AP.
- **Proposed Fix:** Consider cross-pool tension: certain high-impact actions cost from both pools.

### [P11-04] [RECRUITMENT] Infinite Recruitment Cycling Is Manpower-Gated
- **Severity:** NOTE
- **Category:** DESIGN
- **Description:** Recruitment gated by nation manpower pools (France 80k infantry, regen 5k/turn), not per-region cooldowns. Well-designed. Late-game cavalry regen from many plains regions could become too easy.

### [P11-05] [TRUST] Trust Farming via "Always Agree" Is Self-Limiting
- **Severity:** NOTE
- **Category:** DESIGN
- **Description:** Agreeing with objections means NOT executing desired actions. Trust gains diminish at DEVOTED tier (0.7x). System inherently prevents farming.

### [P11-06] [STRATEGIC] Strategic Orders Cannot Be Exploited for Impossible Movement
- **Severity:** NOTE
- **Category:** DESIGN
- **Description:** MOVE_TO/PURSUE use pathfinding respecting adjacency and movement range. Each step individually validated through executor. `_strategic_execution=True` only skips AP and objections, not movement validation.

### [P11-07] [DIPLOMACY] Pure Military Always Beats Pure Diplomacy
- **Severity:** MAJOR
- **Category:** BALANCE
- **Description:** Victory requires 15/19 regions. Diplomacy cannot directly capture territory — only request in peace deals (requires winning a war first). DP resets each turn (no accumulation). France's starting economy and manpower are sufficient without trade income.
- **Proposed Fix:** Add diplomatic victory condition. Or make diplomatic income more impactful.

### [P11-08] [AI] AI Does Not Punish Deathball — No Deep Strike Behavior
- **Severity:** MAJOR
- **Category:** BALANCE
- **Description:** If player stacks 4 marshals in Belgium, French south (Lyon, Marseille, Bordeaux, Brittany) is undefended. AI's P4.5 captures adjacent undefended, but there is no "opportunistic deep strike" to send marshals 3+ regions behind the front.
- **Proposed Fix:** Add P4.6+ "Deep Raid" priority — when AI sees 2+ undefended homeland regions reachable in 2-3 turns, advance to claim them. Make AI aware of force concentration.

### [P11-09] [COMBAT] Artillery Exhaustion Exemption Enables Bombardment Spam
- **Severity:** MINOR
- **Category:** EXPLOIT
- **File:** marshal.py:700-703
- **Description:** Drouot exempt from exhaustion penalty (-10/-20/-30% for 2nd/3rd/4th attacks). Can bombard same target 4 times at full effectiveness. AP cost (1/attack) provides natural cap.
- **Proposed Fix:** Verify bombardments_this_turn has meaningful cap. Low severity since AP gates total actions.

### [P11-10] [ECONOMY] France's Starting Economy Is Self-Sustaining — No Tradeoffs
- **Severity:** DESIGN
- **Category:** BALANCE
- **Description:** 1100g income, 865g upkeep = +235g/turn surplus. Can recruit once from capital and still net +85g. Never faces "guns vs butter" tradeoff.
- **Proposed Fix:** Increase upkeep rate or add gold-draining mechanics.

### [P11-11] [TURTLING] Davout Fortify + HOLD Creates Impregnable Defensive Position
- **Severity:** MAJOR
- **Category:** EXPLOIT
- **Description:** Davout (cautious) fortifies +3%/turn to 20% max, +15% defensive stance, HOLD order bypasses fortify decay. On urban terrain (Paris, +20%), effective defense ~79k from 48k base. No single AI marshal can break this. HOLD decay immunity allows permanent turtling.
- **Evidence:** personality_modifiers.py:213-214 cautious max_fortify=0.20. world_state.py:4596-4601 Davout-hold immunity.
- **Proposed Fix:** Cap HOLD immunity at 10 turns. Or add player stagnation pressure matching the AI stagnation system.

### [P11-12] [COMBAT] Ney Cavalry Charge Dominance in Plains
- **Severity:** MINOR
- **Category:** BALANCE
- **Description:** Ney on plains with aggressive stance (+15%), personality mod (+15%), recklessness (5-15%), drill (+20%), Glorious Charge (2x) can hit 3.4x effective damage. 72k starting strength makes 2x-taken-casualties survivable.
- **Proposed Fix:** Consider reducing Ney starting strength to 60k to make charges riskier.

### [P11-13] [MAP] Dead Zones — Brittany, Tyrol, Bordeaux Strategically Irrelevant
- **Severity:** MINOR
- **Category:** DESIGN
- **Description:** Brittany is a dead-end (2 adjacencies, 50g). Tyrol requires going through Bavaria. Bordeaux is economically weak. Battles rarely happen there.
- **Proposed Fix:** Add strategic value (port buildings, mountain pass mechanic) or accept as economic backwater.

### [P11-14] [ECONOMY] Britain's Naval Income Is Unconditional Free Money
- **Severity:** MINOR
- **Category:** BALANCE
- **Description:** 300g/turn regardless of regions controlled. Even with 0 regions, bankrupt Britain with halved upkeep nets +110g/turn from naval income alone.
- **Proposed Fix:** Make naval income conditional on controlling at least 1 region.

### [P11-15] [TURTLING] Player Can Avoid Losing by Running Out Clock at 8 Regions
- **Severity:** MAJOR
- **Category:** EXPLOIT
- **Description:** No early defeat condition. Game only ends at turn 40. Player can fortify all marshals and stall for 40 turns without consequences.
- **Proposed Fix:** Add early game-over triggers: lose Paris = defeat (or 3-turn countdown). After turn 20 without new captures, trigger stagnation warning.

### [P11-16] [DIPLOMACY] DP Non-Accumulation Limits Strategy Depth
- **Severity:** DESIGN
- **Category:** BALANCE
- **Description:** DP resets each turn (3-4). No "save up for big play" strategy. Most proposals cost 1-2 DP. Diplomacy feels procedural rather than strategic.
- **Proposed Fix:** Allow partial DP carry-over (up to 2 unused DP, cap at max+2).

### [P11-17] [COMBAT] Counter-Punch Mastery Enables Perpetual Free Defense
- **Severity:** MINOR
- **Category:** BALANCE
- **Description:** Davout gets free counter-attack after being attacked. Combined with fortress turtle (P11-11), wait for AI to attack, get free counter-punch at +20% bonus. AI futility only triggers after 3 failed attacks.
- **Proposed Fix:** Limit counter-punch to once per 2 turns, or make AI futility trigger at 2 failures against fortified positions.

### [P11-18] [AI] AI Nations Do Not Coordinate Against Player
- **Severity:** DESIGN
- **Category:** BALANCE
- **Description:** Each AI nation acts independently. Britain and Prussia won't deliberately pincer. Coalition sets postures but doesn't coordinate tactical movement. Player can defeat nations sequentially.
- **Proposed Fix:** When 2+ nations at war with player, prefer attacking same region where another nation's marshal is adjacent (converging attack).

---

### Pass 11 Summary

| Severity | Count |
|----------|-------|
| MAJOR | 5 (Belgium rush, military > diplomacy, no deathball punishment, Davout turtle, clock running) |
| MINOR | 5 |
| DESIGN | 4 |
| NOTE | 4 |

**Top 3 Most Exploitable Strategies:**
1. **Davout Paris Turtle** (P11-11 + P11-15 + P11-17): Fortify at Paris with HOLD, never attack, run out clock. Impossible for AI to break.
2. **Belgium Deathball Rush** (P11-01 + P11-02 + P11-08): Stack 4 marshals in Belgium turn 1, smash Waterloo turn 1-2, Netherlands turn 2-3. AI can't punish undefended south.
3. **Sequential Elimination** (P11-18 + P11-07): Fight one nation at a time. AI never coordinates joint attacks.

---

## Pass 12: CROSS-SYSTEM INTEGRATION — THE SEAMS

### [P12-01] [COMBAT/RECKLESS] Reckless Cavalry Auto-Charge Bypasses Forced Retreat Handling
- **Severity:** MAJOR
- **Category:** BUG
- **File:** world_state.py:5074-5250
- **Description:** `_process_reckless_cavalry_turn_start()` calls `CombatResolver.resolve_battle()` directly, bypassing the executor. If the reckless cavalry charges and loses badly (morale < 25%), no forced retreat or broken state is applied. The marshal remains in place after defeat.
- **Evidence:** Line 5176 only checks `attacker_won` and `marshal.strength > 0` for advance, zero handling for forced retreat. Compare executor.py:4777 which calls `_handle_forced_retreat`.
- **Proposed Fix:** After combat, check `combat_result.get("attacker", {}).get("forced_retreat", False)` and apply retreat/broken state. Or route auto-charge through executor with special flag.
- **Test Coverage:** No

### [P12-02] [COMBAT/RECKLESS] Reckless Auto-Charge Skips Coalition Threat and War Score
- **Severity:** MAJOR
- **Category:** BUG
- **File:** world_state.py:5074-5250
- **Description:** Auto-charge bypasses `record_diplo_battle()`, `add_threat()`, and `add_war_exhaustion_from_battle()` from executor.py:4986-5036. A France reckless cavalry win does not increase threat level, and war scores ignore the battle.
- **Proposed Fix:** Add coalition threat + war score recording after auto-charge combat.
- **Test Coverage:** No

### [P12-03] [COMBAT/RECKLESS] Reckless Auto-Charge Skips Relationship Processing
- **Severity:** MINOR
- **Category:** BUG
- **File:** world_state.py:5074-5250
- **Description:** Auto-charge never calls `process_battle_relationships()`. If marshals share the battle region, win/loss relationship changes are skipped.
- **Proposed Fix:** Call `process_battle_relationships` after auto-charge if 2+ same-nation marshals present.
- **Test Coverage:** No

### [P12-04] [COMBAT/RECKLESS] Reckless Auto-Charge Does Not Remove Destroyed Enemies
- **Severity:** MINOR
- **Category:** BUG
- **File:** world_state.py:5185-5188
- **Description:** When enemy is destroyed (strength <= 0) by auto-charge, code generates message but never calls `world.marshals.pop()`. Destroyed marshal remains as zombie entry.
- **Proposed Fix:** Add `self.marshals.pop(enemy.name, None)` after detecting destruction.
- **Test Coverage:** No

### [P12-05] [TRUST/COMBAT] Trust Has No Mechanical Effect on Combat Performance
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** marshal.py:789-933
- **Description:** Neither `get_attack_modifier()` nor `get_defense_modifier()` reference `self.trust`. Trust is one-directional: combat outcomes → trust (via vindication), but trust → combat never. A marshal at trust 10 fights identically to trust 100.
- **Proposed Fix:** Consider small morale penalty at very low trust (trust < 20 = -5% effectiveness).
- **Test Coverage:** N/A

### [P12-06] [FOG/STRATEGIC] PURSUE Into Fogged Region Correctly Uses Intel Store
- **Severity:** NOTE
- **Category:** ARCHITECTURE
- **File:** strategic.py:859-1143
- **Description:** PURSUE handler correctly reads from intel store for player marshals, uses real position for AI. Empty arrival at last-known handled with break-order or continuation. Fog/strategic seam is clean.
- **Test Coverage:** Yes

### [P12-07] [OBJECTION/STRATEGIC] Strategic Objection Uses Separate Field Correctly
- **Severity:** NOTE
- **Category:** ARCHITECTURE
- **Description:** Tactical objections use `pending_objection`, strategic uses `pending_strategic_objection`. Strategic execution bypasses both. Routing is correct.
- **Test Coverage:** Yes

### [P12-08] [ECONOMY/RECRUIT] France Has Structural Manpower Advantage
- **Severity:** NOTE
- **Category:** DESIGN
- **Description:** France 80k infantry pool vs Britain 50k, Prussia 60k, Austria 40k, Saxony 20k. Same batch sizes and regen. Balanced by France facing 4 nations simultaneously.
- **Test Coverage:** Indirectly

### [P12-09] [TURN/STATE] Advance Turn Step Ordering Is Correct but Fragile
- **Severity:** NOTE
- **Category:** ARCHITECTURE
- **File:** world_state.py:3461-3810
- **Description:** ~25 subsystems in specific order with explicit dependency comments. Ordering is correct but fragile to future additions.
- **Proposed Fix:** Consider ordering contract document or DAG for future-proofing.
- **Test Coverage:** Partially

### [P12-10] [SAVE/LOAD] Dynamic Diplomatic Trust Attributes Accumulate Without Serialization
- **Severity:** MINOR
- **Category:** BUG
- **File:** executor.py:11915-11937
- **Description:** `_apply_diplomatic_trust_reaction` creates dynamic attributes `f"_diplomatic_trust_this_turn_{world.current_turn}"` on marshal objects. Never cleaned up, never serialized. Creates new key each turn, slow memory growth. Mid-turn save/load resets cap, allowing double-application.
- **Proposed Fix:** Use a single field `_diplomatic_trust_applied_turn` reset at turn start.
- **Test Coverage:** No

### [P12-11] [SAVE/LOAD] All Persistent Marshal and WorldState Fields Properly Serialized
- **Severity:** NOTE
- **Category:** ARCHITECTURE
- **Description:** Cross-referenced `Marshal.__init__` with `to_dict`/`from_dict`: every persistent field appears in both. WorldState similarly complete. Transient per-turn fields correctly excluded.
- **Test Coverage:** Yes (test_serialization_enforcement.py)

### [P12-12] [AI PARITY] Enemy AI Uses Same Executor for All Actions
- **Severity:** NOTE
- **Category:** ARCHITECTURE
- **Description:** Golden Rule #5 respected. All three AI execute paths go through `CommandExecutor.execute()`. AI does NOT use strategic orders (by design — makes per-turn tactical decisions).
- **Test Coverage:** Indirectly

### [P12-13] [COMBAT/RECKLESS] Reckless Auto-Charge Skips Region Conquest
- **Severity:** MAJOR
- **Category:** BUG
- **File:** world_state.py:5176-5183
- **Description:** When reckless cavalry wins and advances into enemy's region, no conquest check occurs. Only `marshal.move_to()` is called — never `_attempt_region_capture()`. Territory remains under old controller despite occupation by attacker.
- **Evidence:** Lines 5176-5183: only `move_to()`, no capture logic. Compare executor.py:4878-4901.
- **Proposed Fix:** After advancing, add region conquest check and transfer control.
- **Test Coverage:** No

### [P12-14] [VINDICATION/TRUST] Vindication Trust Changes Correctly Wired
- **Severity:** NOTE
- **Category:** ARCHITECTURE
- **Description:** Combat→Trust works through vindication: after battle with pending objection, trust changes apply correctly (+3 vindicated, -5 insist+defeat, etc.). Normal wins/losses without objections don't change trust — intentional design.
- **Test Coverage:** Yes

---

### Pass 12 Summary

| Severity | Count |
|----------|-------|
| MAJOR | 3 (auto-charge: no retreat, no threat/score, no conquest) |
| MINOR | 3 (auto-charge: no relationships, no cleanup; diplomatic trust leak) |
| NOTE | 8 (5 positive/clean seams) |

**Key Pattern:** The reckless cavalry auto-charge in `_process_reckless_cavalry_turn_start()` is the single biggest integration gap. It bypasses 5 critical post-combat systems: forced retreat (P12-01), coalition threat/war score (P12-02), relationship processing (P12-03), enemy cleanup (P12-04), and region conquest (P12-13). Root cause: only combat path that calls `resolve_battle()` directly without executor. Fix: route through executor with special flag, or replicate the 5 missing blocks.

---

## FULL AUDIT SUMMARY (Passes 1-12)

### Finding Counts

| Pass | CRITICAL | MAJOR | MINOR | NOTE | DESIGN | Total |
|------|----------|-------|-------|------|--------|-------|
| P1 (Combat) | 1 | 5 | 5 | 2 | 2 | 15 |
| P2 (Enemy AI) | 1 | 3 | 6 | 5 | 2 | 17 |
| P3 (Strategic) | 0 | 2 | 3 | 3 | 0 | 8 |
| P4 (Disobedience) | 0 | 1 | 3 | 3 | 2 | 9 |
| P5 (Fog of War) | 0 | 2 | 5 | 3 | 1 | 11 |
| P6 (Turn Flow) | 0 | 3 | 2 | 1 | 1 | 7 |
| P7 (Godot Frontend) | 0 | 1 | 5 | 3 | 1 | 10 |
| P8 (Parser) | 0 | 1 | 6 | 1 | 2 | 10 |
| P9 (Code Elegance) | 0 | 3 | 9 | 13 | 0 | 25 |
| P10 (Game Design) | 0 | 5 | 5 | 7 | 3 | 20 |
| P11 (Exploits) | 0 | 5 | 5 | 4 | 4 | 18 |
| P12 (Cross-System) | 0 | 3 | 3 | 8 | 0 | 14 |
| **TOTAL** | **2** | **34** | **57** | **53** | **18** | **164** |

### Cross-Cutting Patterns

1. **Reckless Auto-Charge Bypass** (P1-1, P12-01 through P12-04, P12-13): The auto-charge code path bypasses ALL executor post-combat processing. 5 distinct bugs from one root cause.

2. **Deathball + No Punishment** (P11-01, P11-02, P11-08, P11-18): Player can stack forces with impunity because AI has no deep raid, no converging attack coordination, and mild supply attrition.

3. **Turtle Forever** (P11-11, P11-15, P11-17): Davout HOLD immunity + no early defeat + counter-punch = unbreakable defense with no game pressure to attack.

4. **Diplomacy Is Optional** (P10-02, P10-06, P11-07, P10-17): No diplomatic victory, no forced diplomatic engagement, Continental System vestigial, DP non-accumulating.

5. **Hardcoded "Paris"** (P3-3, P4-6, P8-10): Three locations assume French capital. Non-French marshals path toward Paris.

6. **God Object** (P9-01, P9-02, P9-05, P9-06, P9-13, P9-25): executor.py 14,410 lines with 52 methods is the architectural bottleneck. StrategicExecutor proves decomposition works.

7. **Literal Personality Hollow** (P10-04): The game's signature dramatic beat (Grouchy Moment) is unimplemented.

---

## TARGETED DEEP DIVES (Passes 13-15)

Based on cross-cutting patterns from Passes 1-12, three areas warranted deeper investigation.

---

## Pass 13: Deep Dive — Reckless Auto-Charge & Glorious Charge Bypass

**Root Cause:** There are 4 production calls to `CombatResolver.resolve_battle()`. Two (in `_execute_attack`) have full post-combat processing (~620 lines). Two bypass paths skip all of it:
- **Bypass #1:** `_process_reckless_cavalry_turn_start()` in world_state.py:5074
- **Bypass #2:** `_execute_glorious_charge()` in executor.py:10217

### [P13-01] Missing Forced Retreat Processing
- **Severity:** CRITICAL
- **Category:** BUG
- **File:** world_state.py:5074-5287 (auto-charge), executor.py:10217-10427 (glorious charge)
- **Description:** Neither bypass calls `_handle_forced_retreat()`. When a combatant drops below 25% morale, they should retreat or become BROKEN (teleported to capital with 3-10% strength, 4-turn recovery). Instead, broken armies stay in place. Particularly impactful because glorious charges deal 2x damage, making forced retreats MORE likely.
- **Test Coverage:** No

### [P13-02] Missing Destroyed Marshal Cleanup
- **Severity:** CRITICAL
- **Category:** BUG
- **File:** world_state.py:5185-5189 (auto-charge), executor.py:10396-10404 (glorious charge)
- **Description:** Neither bypass removes destroyed marshals (strength=0) from `world.marshals`. Dead marshals persist as zombies, corrupting AI targeting and serialization. `_execute_attack` calls `world.marshals.pop()` at line 4764; neither bypass does.
- **Test Coverage:** No

### [P13-03] Missing Diplomatic War Score Recording (Auto-Charge Only)
- **Severity:** CRITICAL
- **Category:** BUG
- **File:** world_state.py:5074-5287
- **Description:** Auto-charge never calls `diplomacy.record_battle()`. Battles are invisible to diplomacy — no war score, no decisive battle detection. (Glorious charge DOES record at line 10358.)
- **Test Coverage:** No

### [P13-04] Missing Coalition Threat/Exhaustion/Shock
- **Severity:** CRITICAL
- **Category:** BUG
- **File:** world_state.py:5074-5287 (auto-charge), executor.py:10217-10427 (glorious charge)
- **Description:** Neither bypass calls `add_threat()`, `add_war_exhaustion_from_battle()`, or `add_coalition_shock()`. Reckless cavalry victories are invisible to the coalition system. With 2x charge damage, decisive victories that should trigger coalition shock generate zero threat.
- **Test Coverage:** No

### [P13-05] Missing Win/Loss Relationship Processing
- **Severity:** MAJOR
- **Category:** BUG
- **Description:** Neither bypass calls `process_battle_relationships()`. Co-located marshals in charge battles get no relationship updates.

### [P13-06] Missing Authority Tracker Updates
- **Severity:** MAJOR
- **Category:** BUG
- **Description:** Neither bypass calls `world.authority_tracker.modify_authority()`. Major victories/defeats from charges never affect authority.

### [P13-07] Missing Vindication Resolution
- **Severity:** MAJOR
- **Category:** BUG
- **Description:** Neither bypass calls `vindication_tracker.resolve_battle()`. Pending vindication events become permanently stuck after charge battles.

### [P13-08] Missing Region Conquest Logic
- **Severity:** MAJOR
- **Category:** BUG
- **Description:** Neither bypass calls `_attempt_region_capture()`. Winning and advancing never captures territory.

### [P13-09] Missing Square Formation Auto-Break (Auto-Charge Only)
- **Severity:** MAJOR
- **Category:** BUG
- **Description:** Auto-charge never calls `_auto_break_square()`. (Glorious charge does at line 10228.)

### [P13-10] Missing Overwatch Penalty Calculation
- **Severity:** MAJOR
- **Category:** BUG
- **Description:** Neither bypass calls `_calculate_overwatch()`. Charging cavalry is immune to enemy artillery suppression (-3% per artillery, cap -9%).

### [P13-11] Missing Flanking System
- **Severity:** MAJOR
- **Category:** BUG
- **Description:** Neither bypass calls `record_attack()` or `calculate_flanking_bonus()`. Charges neither benefit from nor contribute to flanking.

### [P13-12] Missing Coordination System
- **Severity:** MAJOR
- **Category:** BUG
- **Description:** Neither bypass calls `_calculate_coordination_context()` or `_distribute_casualties()`. Co-located allies provide no coordination bonus, and the charger takes all casualties alone.

### [P13-13] Missing Reinforcement System
- **Severity:** MAJOR
- **Category:** BUG
- **Description:** Neither bypass calls `_calculate_reinforcements()`. Adjacent allies on SUPPORT orders never join charge battles.

### [P13-14] Missing Support Auto-Bombardment
- **Severity:** MAJOR
- **Category:** BUG
- **Description:** Neither bypass triggers support auto-bombardment. Friendly artillery on SUPPORT sits idle while their supported marshal charges alone.

### [P13-15] Missing Fortification Bonus (Auto-Charge Only)
- **Severity:** MAJOR
- **Category:** BUG
- **Description:** Auto-charge passes no `fortification_bonus` to `resolve_battle()`. Star fort +25% defense is ignored. (Glorious charge reads fort bonus at line 10324.)

### [P13-16] Missing Exhaustion Tracking
- **Severity:** MINOR
- **Category:** BUG
- **Description:** Neither bypass calls `increment_attacks_this_turn()`. Charges don't count toward attack spam exhaustion.

### [P13-17] Missing Idle Turn Reset
- **Severity:** MINOR
- **Category:** BUG
- **Description:** Neither bypass sets `idle_turns=0` or `_acted_this_turn=True`. Charging marshals may trigger idle-tracking V2a penalties.

### [P13-18] Missing Building Damage (Auto-Charge Only)
- **Severity:** MINOR
- **Category:** BUG
- **Description:** Auto-charge applies basic war damage but not `_apply_battle_effects_to_region()` — buildings and watchtowers escape damage.

### [P13-19] No Broken/Retreating/Drilling Marshal Guard (Auto-Charge)
- **Severity:** MAJOR
- **Category:** BUG
- **File:** world_state.py:5095-5101
- **Description:** Auto-charge only checks `is_reckless_cavalry` and `recklessness >= 4`. A broken marshal at 3% strength could auto-charge. A drilling marshal could charge mid-drill.
- **Proposed Fix:** Skip auto-charge if `broken`, `retreat_recovery > 0`, `retreated_this_turn`, `drilling`, or `drilling_locked`.

### [P13-20] Strategic Order HOLD Conflict (Auto-Charge)
- **Severity:** MAJOR
- **Category:** BUG
- **Description:** Auto-charge never checks for active strategic orders. A marshal on HOLD silently charges despite being ordered to hold position. Design decision: should recklessness override strategic orders?

### [P13-21] Two Reckless Cavalry in Same Region
- **Severity:** MINOR
- **Category:** BUG
- **Description:** Two reckless marshals in the same region fight the same enemy separately (two 1v1s). Second charge may fight a zombie (P13-02 — destroyed marshals not cleaned up between iterations).

### [P13-22] to [P13-25] Minor Missing Systems
- **Severity:** MINOR
- **Category:** BUG
- **Description:** Berthier observation re-pick missing, combat notifications missing, ally-covers-retreat missing, cavalry leapfrog check missing (2-region charge can skip over blocking enemies).

### Proposed Fix Architecture

**Option A + B (Recommended):**
1. Extract all post-combat processing from `_execute_attack` (lines 4608-5229) into a shared `_process_post_combat()` method. Have both `_execute_attack` and `_execute_glorious_charge` call it.
2. Route `_process_reckless_cavalry_turn_start()` auto-charges through the executor instead of calling `resolve_battle()` directly.

**Key principle:** Every `resolve_battle()` call site must share the same post-combat processing pipeline. Currently one is well-maintained; two diverged months ago and missed every subsequent system addition.

### Pass 13 Summary: 5 CRITICAL, 13 MAJOR, 8 MINOR = 26 findings from one root cause

---

## Pass 14: Deep Dive — Glorious Charge Complete Checklist

Full line-by-line comparison of `_execute_glorious_charge` vs `_execute_attack` post-combat systems:

| # | System | In _execute_attack | In glorious_charge | Status |
|---|--------|-------------------|-------------------|--------|
| 1 | Auto-break square | Line 3480 | Line 10228 | PRESENT |
| 2 | Artillery blocking | Line 3522 | Line 10231 | PRESENT |
| 3 | Engagement check | Lines 3889-3908 | — | MISSING |
| 4 | Auto war declaration | Lines 3926-3934 | — | MISSING |
| 5 | Coalition member attack prevention | Lines 3776-3784 | — | MISSING |
| 6 | Flanking system | Lines 4162-4170 | — | MISSING |
| 7 | Cavalry transit intel | Lines 4207-4208 | — | MISSING |
| 8 | Reinforcement calculation | Lines 4232-4237 | — | MISSING |
| 9 | Coordination context | Lines 4283-4290 | — | MISSING |
| 10 | Casualty distribution | Lines 4296-4307 | — | MISSING |
| 11 | Artillery overwatch | Lines 4326-4327 | — | MISSING |
| 12 | Support auto-bombardment | Lines 4340-4390 | — | MISSING |
| 13 | resolve_battle call | Lines 4470-4606 | Line 10332 | PRESENT |
| 14 | Berthier observation re-pick | Lines 4692-4714 | — | MISSING |
| 15 | Log battle event | Line 4656 | Line 10341 | PRESENT |
| 16 | Combat notifications | Line 4659 | — | MISSING |
| 17 | Win/loss relationships | Lines 4668-4683 | — | MISSING |
| 18 | Fog battle intel | Line 4727 | Line 10344 | PRESENT |
| 19 | War damage to region | Lines 4730-4733 | Lines 10347-10349 | PRESENT |
| 20 | Idle tracking reset | Lines 4736-4737 | — | MISSING |
| 21 | Cannon fire detection | Lines 4740-4741 | Lines 10352-10355 | PRESENT |
| 22 | Diplomatic war score | Lines 4744-4758 | Lines 10358-10372 | PRESENT |
| 23 | Destroyed enemy cleanup | Lines 4762-4766 | — | **MISSING** |
| 24 | Destroyed attacker cleanup | Lines 4769-4770 | — | **MISSING** |
| 25 | Forced retreat | Lines 4777-4821 | — | **MISSING** |
| 26 | Territory capture | Lines 4878-4901 | — | **MISSING** |
| 27 | Vindication | Lines 4923-4930 | — | **MISSING** |
| 28 | Authority tracker | Lines 4941-4983 | — | **MISSING** |
| 29 | Coalition threat | Lines 4991-5036 | — | **MISSING** |
| 30 | Counter-punch for defender | Lines 4522-4532 | — | **MISSING** |
| 31 | Exhaustion tracking | Line 5202 | — | MISSING |
| 32 | Covering ally system | Lines 4127-4154 | — | MISSING |

**Confirmed CORRECT:** 2x damage multiplier applied to final casualties (combat.py:446-448). Square formation interaction correct (-40% to cavalry stacks with 2x = 1.2x net). Terrain modifiers correctly passed.

**Attacker death not handled (P14-20):** When charger dies (strength=0 from 2x taken), marshal never removed. Result says "success: True" with dead marshal.

**Mutual destruction not handled (P14-21):** Both sides at 0 strength — neither cleaned up.

### Pass 14 Summary: 3 CRITICAL (forced retreat, destroyed cleanup, territory capture), 8 MAJOR, 9 MINOR

---

## Pass 15: Deep Dive — Turtle Exploit & Balance Math

### [P15-01] Davout Paris Turtle: Permanent Invincible Fortress
- **Severity:** CRITICAL
- **Category:** EXPLOIT

**Maximum defense calculation — Davout at Paris with HOLD:**
- Base: 48,000 troops
- Defender bonus: +20% (combat.py)
- Defensive stance: +15% (marshal.py:875)
- Cautious personality defensive bonus: +5% (personality_modifiers.py:184)
- Max fortification (cautious): +20% (personality_modifiers.py:53)
- Outnumbered defense: +10% (personality_modifiers.py:188)
- Urban terrain: +20% (region.py:20)
- HOLD order: permanent fortification immunity (world_state.py:4601)
- Paris garrison: 15,000 + 2,000 regen/turn

**Combined multiplier:** 1.20 × 1.2075 × 1.20 × 1.10 × 1.20 = **~2.30x**
**Effective defense:** 48,000 × 2.30 = **110,400 equivalent troops**

No single AI marshal (max: Wellington 52k) can break this. Even combined 226k all-enemy-marshals would struggle. After 3 failed attacks, AI futility filter permanently stops trying. Player can turtle indefinitely.

**Supply:** Paris has 60k effective capacity (50k × 1.2 urban); Davout at 48k < 60k → zero attrition.

### [P15-02] Deathball Belgium Rush: Stack 4 Marshals, Roll Europe
- **Severity:** MAJOR
- **Category:** EXPLOIT

**Turn-by-turn simulation:**
- Turn 1: Davout+Drouot (Paris→Belgium), Ney already there. 145k in Belgium. Grouchy: Lyon→Paris.
- Turn 2: Grouchy→Belgium. 173k total. Attack Waterloo (Wellington 52k in hills).
- Turn 3-4: Netherlands (British capital, 15k garrison). Britain eliminated.
- Turn 5+: Pivot east toward Prussia.

**Supply attrition:** Belgium capacity 37,500 (home bonus). 173k troops → 3% cap attrition = ~5,190/turn per marshal. Easily replaced by recruitment (10k per recruit at 200g).

**AI response to undefended French south:** Austria and Saxony are NOT at war with France at start — cannot capture. Prussia's marshals are on the northern front (Rhineland, Berlin). No AI marshal reaches undefended Lyon/Marseille/Bordeaux.

### [P15-03] No Early Defeat: France Cannot Lose Before Turn 40
- **Severity:** MAJOR
- **Category:** BALANCE

**Defeat conditions (turn_manager.py:733-784):**
1. All marshals destroyed (strength=0) — extremely rare
2. Turn 40 expiration without 77% control

**Missing:** No capital-loss defeat. No region-count threshold. No surrender. Player can lose Paris, lose 15/19 regions, and game continues as long as one marshal has troops > 0.

### [P15-04] HOLD Decay Immunity Is Cautious-Exclusive
- **Severity:** MAJOR
- **Category:** BALANCE
- **File:** world_state.py:4596-4601
- **Description:** Only `personality == "cautious"` with HOLD gets decay immunity. Davout is the only French marshal who can create a permanent fortress. All other personalities (including literal Grouchy with HOLD) still decay.
- **Proposed Fix:** HOLD should slow decay for all (halve rate), not grant immunity to one personality.

### [P15-05] AI Futility Filter Creates Permanent Safe Zone
- **Severity:** MAJOR
- **Category:** BALANCE
- **File:** enemy_ai.py:2183-2201
- **Description:** After 3 failed attacks on a fortified target, AI permanently stops attacking that target. The `ai_attack_futility` dict has no reset mechanism — the counter only ever increments. Combined with P15-01, the AI gives up on Paris after 3 attempts. Forever.
- **Proposed Fix:** Add decay (reduce by 1 every 3 turns), reset on defender weakness (below 50% strength), coalition override (ignore futility during coalition war).

### [P15-06] Supply Attrition Cap Too Low for Deathball Prevention
- **Severity:** MAJOR
- **Category:** BALANCE
- **File:** world_state.py:2316
- **Description:** 3% cap regardless of excess ratio. 173k in Belgium (37.5k capacity) = max 3% loss = ~5,190/turn. Trivially replaced. Historical campaigns saw 10-40% attrition from force concentration.
- **Proposed Fix:** Raise cap to 8%, or add per-marshal stacking penalty (+2% per marshal beyond 2 in region).

### Pass 15 Summary

| Finding | Severity | Category |
|---------|----------|----------|
| P15-01 Davout Paris Turtle | CRITICAL | EXPLOIT |
| P15-02 Deathball Belgium Rush | MAJOR | EXPLOIT |
| P15-03 No Early Defeat | MAJOR | BALANCE |
| P15-04 HOLD Decay Cautious-Only | MAJOR | BALANCE |
| P15-05 AI Futility Permanent | MAJOR | BALANCE |
| P15-06 Supply Attrition Cap | MAJOR | BALANCE |

---

## GRAND TOTAL (Passes 1-15)

| Pass | CRITICAL | MAJOR | MINOR | NOTE | DESIGN | Total |
|------|----------|-------|-------|------|--------|-------|
| P1-P12 (initial) | 2 | 34 | 57 | 53 | 18 | 164 |
| P13 (auto-charge) | 4 | 13 | 8 | 0 | 0 | 25 |
| P14 (glorious charge) | 3 | 8 | 9 | 3 | 0 | 23 |
| P15 (turtle/balance) | 1 | 5 | 0 | 0 | 0 | 6 |
| P16 (test coverage) | 0 | 6 | 0 | 12 | 0 | 18 |
| P17 (turn ordering) | 0 | 1 | 1 | 0 | 0 | 2 |
| P18 (economy) | 0 | 1 | 0 | 0 | 10 | 11 |
| **GRAND TOTAL** | **10** | **68** | **75** | **56** | **28** | **249** |

**Note:** Many P13/P14 findings overlap (both identify the same missing systems in different bypass paths). Unique root-cause bugs after deduplication: ~140-150.

---

## Pass 16: Test Coverage Gap Analysis

### [P16-01] Auto-Charge Missing War Score Recording
- **Bug Refs:** P12-01, P13-03
- **Current Coverage:** None. `test_cavalry_recklessness.py` tests triggers and recklessness reset but never checks `record_diplo_battle()`.
- **Proposed Test:** `test_auto_charge_records_war_score` — verify war score updates after auto-charge win.

### [P16-02] Auto-Charge Missing Territory Capture
- **Bug Refs:** P12-02, P13-08
- **Current Coverage:** None. No test checks `region.controller` changes after auto-charge victory.
- **Proposed Test:** `test_auto_charge_captures_territory` — sole defender region, verify controller changed.

### [P16-03] Auto-Charge Missing Forced Retreat
- **Bug Refs:** P12-03, P13-01
- **Current Coverage:** None. No test checks losing side enters retreat/broken state.
- **Proposed Test:** `test_auto_charge_loser_retreats` — defender with low morale enters broken state.

### [P16-04] Auto-Charge Missing Destroyed Marshal Cleanup
- **Bug Refs:** P12-04, P13-02
- **Current Coverage:** None. Destroyed marshals remain as ghosts.
- **Proposed Test:** `test_auto_charge_removes_destroyed_marshal` — enemy destroyed, assert popped from world.marshals.

### [P16-05] Auto-Charge Missing Coalition Threat
- **Bug Refs:** P12-05, P13-04
- **Current Coverage:** None. No integration test anywhere verifies threat_level increases after any combat through executor.
- **Proposed Test:** `test_auto_charge_generates_coalition_threat` — verify threat_level increased by 3+.

### [P16-06] Glorious Charge Missing Territory Capture
- **Bug Refs:** P14-03
- **Current Coverage:** None.
- **Proposed Test:** `test_glorious_charge_captures_territory`.

### [P16-07] Glorious Charge Missing Forced Retreat
- **Bug Refs:** P14-01
- **Current Coverage:** None.
- **Proposed Test:** `test_glorious_charge_forces_retreat`.

### [P16-08] Glorious Charge Missing Destroyed Marshal Cleanup
- **Bug Refs:** P14-02
- **Current Coverage:** None.
- **Proposed Test:** `test_glorious_charge_removes_destroyed_enemy`.

### [P16-09] Glorious Charge Missing Coalition Threat
- **Bug Refs:** P14-04
- **Current Coverage:** None.
- **Proposed Test:** `test_glorious_charge_adds_coalition_threat`.

### [P16-10] Glorious Charge Missing Relationship Processing
- **Bug Refs:** P14-06
- **Current Coverage:** None.
- **Proposed Test:** `test_glorious_charge_updates_relationships`.

### [P16-11] Glorious Charge Missing Authority Tracking
- **Bug Refs:** P14-05
- **Current Coverage:** None.
- **Proposed Test:** `test_glorious_charge_major_victory_authority`.

### [P16-12] Glorious Charge Missing Vindication
- **Bug Refs:** P14-07
- **Current Coverage:** None.
- **Proposed Test:** `test_glorious_charge_resolves_vindication`.

### [P16-13] Coalition Threat Integration Test Gap
- **Bug Refs:** P1-2
- **Current Coverage:** `test_session7_coalition.py` tests `add_threat()` standalone. NO test executes an attack through executor and verifies threat_level changed.
- **Proposed Test:** `test_attack_integration_increases_coalition_threat`.

### [P16-14] Fortification Decay Zero Tests
- **Bug Refs:** P15-01, P15-04
- **Current Coverage:** None. The entire fortification decay mechanic in `_process_tactical_states()` has no dedicated tests. Fort degradation tests exist but test a different system (combat-based).
- **Proposed Tests:** `test_fortification_growth_over_turns`, `test_fortification_decay_after_threshold`, `test_cavalry_auto_unfortify`.

### [P16-15] Davout HOLD Immunity — No Test
- **Bug Refs:** P15-04
- **Current Coverage:** None.
- **Proposed Tests:** `test_davout_hold_order_prevents_decay`, `test_non_cautious_hold_still_decays`.

### [P16-16] AI Futility Filter — Zero Tests
- **Bug Refs:** P15-05
- **Current Coverage:** None. `ai_attack_futility` completely untested.
- **Proposed Tests:** `test_futility_counter_increments`, `test_futility_filter_removes_target_after_3`, `test_futility_resets_on_success`.

### [P16-17] Save/Load Roundtrip Thin for Diplomacy
- **Bug Refs:** P12-10
- **Current Coverage:** `test_serialization_enforcement.py` catches missing to_dict/from_dict. Save/load roundtrip only checks current_turn and nation_gold.
- **Proposed Test:** `test_save_load_roundtrip_diplomacy_state` — treaties, wars, vassals, threat, DP.

### [P16-18] No Full Post-Combat Pipeline Integration Test
- **Bug Refs:** Systemic (P12, P13, P14)
- **Current Coverage:** Individual systems tested but no single test verifies: combat → forced retreat → territory capture → relationship → coalition threat → authority → war score → vindication.
- **Proposed Test:** `test_attack_full_post_combat_pipeline`.

### Pass 16 Summary: 18 test gap findings — 12 are live bugs exposed by missing tests, 6 are pure coverage gaps.

---

## Pass 17: advance_turn() Ordering Audit

### [P17-01] Player AP Treaty Penalty Overwritten by Action Reset
- **Severity:** MAJOR
- **Category:** BUG
- **File:** world_state.py:3724, 3739
- **Description:** `_process_treaty_clauses()` (step 25) applies AP penalties via `self.max_actions_per_turn = max(1, self.max_actions_per_turn - int(amount))`. But step 28 immediately overwrites with `self.max_actions_per_turn = int(self.calculate_max_actions())`, which ignores treaty penalties. Any AP clause against France has NO EFFECT because the reset discards it.
- **Evidence:** `calculate_max_actions()` returns `4 + bonus_actions` with no awareness of treaty AP clauses. Existing unit tests test `_process_treaty_clauses()` in isolation, never through full advance_turn().
- **Proposed Fix:** Move player action reset (step 28) BEFORE treaty clause processing (step 25). Or have treaty clauses apply AFTER the action reset.
- **Test Coverage:** Tests exist for treaty clauses in isolation (test_deep_audit_session4.py:340-371) but not through advance_turn() flow.

### [P17-02] Newly Ratified Treaty Clauses Apply Same Turn
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** world_state.py:3603, 3724
- **Description:** `_process_proposal_in_transit()` (step 13) can ratify a treaty. Then `_process_treaty_clauses()` (step 25) processes it the same turn. Gold/manpower/AP clauses apply immediately on ratification turn, not next turn. May be intentional.
- **Proposed Fix:** If unintended, add `signed_turn` check to skip treaties where `signed_turn == current_turn`.

### [P17-03] Bankruptcy Check Runs Before Trade Income (Confirmed by P18-08)
- **Severity:** MINOR
- **Category:** BUG
- **Description:** Income phase at step 21 checks bankruptcy. Trade income at step 22 arrives after. Continental System at step 23 arrives after. A nation can be flagged bankrupt even when end-of-turn gold is positive.

### Pass 17 Summary: 1 MAJOR (AP treaty penalty overwrite), 1 MINOR (same-turn ratification), plus ordering documentation notes.

---

## Pass 18: Economy & Manpower Deep Dive

### Starting Economy by Nation (with Trade Income)

| Nation | Regions | Region Income | Trade Income | Upkeep | **Net/Turn** | Start Gold |
|--------|---------|-------------|-------------|--------|------------|-----------|
| France | 8 | 1,100 | 137 | 865 | **+372** | 800 |
| Britain | 3 | 500 | 337 | 380 | **+457** | 1,500 |
| Prussia | 2 | 400 | 337 | 360 | **+377** | 800 |
| Austria | 4 | 650 | 299 | 300 | **+649** | 600 |
| Saxony | 2 | 250 | 174 | 90 | **+334** | 200 |

**Key finding:** Britain actually has higher net income than France when trade income is included. Austria is the hidden economic powerhouse at +649g/turn.

### [P18-01] Trade Income Is Invisible to the Player
- **Severity:** MAJOR
- **Category:** UX
- **File:** world_state.py:3694-3701
- **Description:** Trade income (137-337g/turn per nation) is applied AFTER the income phase reports its numbers. The Morning Dispatch shows "+235 net" for France when actual gain is +372. Players have no idea diplomacy generates income — contributing to "economy feels invisible" (P10-05).
- **Proposed Fix:** Include trade income in the income phase summary, or add a separate trade line to the turn report.

### [P18-02] Bankruptcy Check Runs Before Trade/Continental System
- **Severity:** MINOR
- **Category:** BUG
- **File:** world_state.py:2229 vs 3701
- **Description:** `_update_bankruptcy()` runs inside `process_income_phase()` (step 21). Trade income is added at step 22. Continental System deductions at step 23. A nation can be flagged bankrupt when end-of-turn gold is positive, or pass bankruptcy check then go negative from Continental System.
- **Proposed Fix:** Move bankruptcy check to after all income sources are applied.

### [P18-03] Economy Creates No Meaningful Decisions
- **Severity:** DESIGN
- **Category:** DESIGN
- **Description:** All nations start with positive net income. Admin AP bonus (+150g/turn for doing nothing) ensures permanent solvency. Trade income is substantial but invisible. No nation faces economic pressure without first losing territory. The economy is structurally incapable of creating tension.
- **Evidence:** France break-even at ~250k troops (77k headroom above starting 173k). Admin AP bonus alone covers 1.5 recruits/turn. Britain bankruptcy-proof via 300g hardcoded naval income.
- **Proposed Fix Options:** (1) Raise upkeep 5→8g/1000 troops. (2) Add military supply costs scaling with combat activity. (3) Create economic events (crop failures, trade disruptions). (4) Make territory capture provide less income initially.

### [P18-04] Anti-France Trade Imbalance
- **Severity:** DESIGN
- **Category:** BALANCE
- **Description:** France starts at WAR with 2/4 nations, getting 137g trade income. Britain/Prussia get 337g each from ALLIANCE trade. Britain's total net (+457) exceeds France's (+372). France's economic dominance is an illusion when trade is factored in. May be intentional (France is the aggressor).

### [P18-05] Austria Hidden Economic Powerhouse
- **Severity:** NOTE
- **Category:** BALANCE
- **Description:** Austria: 650g region + 299g trade - 300g upkeep = +649g net. Highest in the game. By turn 10, Austria has ~7,090g treasury. Can rapidly recruit to match France in army size.

### [P18-06] Admin AP Gold Bonus Overpowered
- **Severity:** DESIGN
- **Category:** BALANCE
- **Description:** +75g per unused admin AP, +150g/turn for doing nothing. Takes France from +235 to +385 net (64% increase). AI frequently saves AP as gold too. Makes economy trivially forgiving.

### [P18-07] Market ROI Excellent but Not Communicated
- **Severity:** NOTE
- **Category:** UX
- **Description:** Market on Paris: 350g cost, +75g/turn. Break-even: 6.7 turns. Over 33 turns = +2,475g profit. Best investment in the game. Player has no way to know this — no tooltip or ROI indicator.

### Pass 18 Summary: 1 MAJOR (invisible trade income), 1 MINOR (bankruptcy timing), 5 DESIGN notes, 2 balance NOTEs.

---

## UPDATED GRAND TOTAL (Passes 1-18)

| Pass | CRITICAL | MAJOR | MINOR | NOTE | DESIGN | Total |
|------|----------|-------|-------|------|--------|-------|
| P1-P12 (initial) | 2 | 34 | 57 | 53 | 18 | 164 |
| P13 (auto-charge) | 4 | 13 | 8 | 0 | 0 | 25 |
| P14 (glorious charge) | 3 | 8 | 9 | 3 | 0 | 23 |
| P15 (turtle/balance) | 1 | 5 | 0 | 0 | 0 | 6 |
| P16 (test coverage) | 0 | 6 | 0 | 12 | 0 | 18 |
| P17 (turn ordering) | 0 | 1 | 1 | 0 | 0 | 2 |
| P18 (economy) | 0 | 1 | 1 | 2 | 7 | 11 |
| P19 (popups/notifs) | 0 | 0 | 0 | 2 | 11 | 13 |
| P20 (save/load) | 0 | 1 | 1 | 2 | 1 | 5 |
| P21 (fog leaks) | 0 | 2 | 4 | 0 | 0 | 6 |
| P22 (AI parity) | 1 | 0 | 0 | 1 | 0 | 2 |
| **GRAND TOTAL** | **11** | **71** | **81** | **75** | **37** | **275** |

---

## Pass 19: Notifications & Popup Integrity

### [P19-01] No Notification Cap — Infinite Accumulation Possible
- **Severity:** MODERATE
- **Category:** UX
- **File:** notifications.py
- **Description:** `NotificationCollector.add()` unconditionally appends with no upper bound. In a 50+ turn game, dozens of undismissed notifications accumulate. `get_pending()` sorts all pending notifications O(n log n) on every POST response. Save file bloat from serialized notification list.
- **Proposed Fix:** Add cap of 50 notifications max. Auto-dismiss oldest NORMAL-priority when exceeded.

### [P19-02] Popups Deferred During Enemy Phase Delayed by One Player Action
- **Severity:** MODERATE
- **Category:** UX
- **File:** main.py:982, main.gd:2226-2267
- **Description:** When `/command` response contains `enemy_phase`, popup passthrough is intentionally skipped. Popups remain on `world` for next request. But the Godot enemy phase dismiss flow goes: mild dispatches → game over → strategic reports → morning dispatch → re-enable input. No check for deferred popups. Player types first command of new turn, THEN sees the deferred popup from last turn.
- **Proposed Fix:** After enemy phase dismissal in Godot, fire a lightweight GET request to check for pending popups before re-enabling input.

### [P19-03] to [P19-11] Minor Popup/Notification Findings
- **Severity:** LOW/INFO
- **Description:** (9 findings) Missing popup passthroughs on error paths in `/save`, `/load`, `/delete_save`, `/respond_to_redemption`, `/cancel_order`, and game-over guards. No duplicate notification prevention. Inconsistent ESC key handling across 8 popup scripts (only war_detail_popup supports ESC). Dynamic button lambda captures in war_detail_popup.gd. All low risk — popups deferred by one request cycle at worst.

### Pass 19 Summary: 2 MODERATE (notification cap, deferred popup timing), 6 LOW, 5 INFO.

---

## Pass 20: Save/Load Roundtrip Deep Dive

### [P20-01] Dynamic `_diplomatic_trust_this_turn_N` Attributes Leak Memory & Bypass Cap on Load
- **Severity:** MAJOR
- **Category:** BUG
- **File:** executor.py:11915-11937
- **Description:** `_apply_diplomatic_trust_reaction` creates `setattr(marshal, f"_diplomatic_trust_this_turn_{current_turn}", ...)` — one new attribute per turn per marshal. By turn 40, each marshal has 40 extra attributes. These are never cleaned up (memory leak) and never serialized. After mid-turn save/load, the per-turn ±5 trust cap resets to 0, allowing double-dipping on diplomatic trust changes. The `_` prefix means serialization enforcement test is blind to this.
- **Proposed Fix:** Replace with single `_diplomatic_trust_this_turn: int = 0` field in `__init__`, serialize it, reset at turn start.
- **Test Coverage:** No

### [P20-02] `_we_dispatched_thresholds` Not Serialized — War Exhaustion Notifications Re-fire After Load
- **Severity:** MINOR
- **Category:** BUG
- **File:** coalition.py:481-490
- **Description:** Tracks which war exhaustion thresholds (20/40/60/80) triggered notifications. Set via `world._we_dispatched_thresholds`. Not in WorldState `__init__`, `to_dict()`, or `from_dict()`. After load, thresholds re-fire.
- **Proposed Fix:** Add to WorldState init/serialization.
- **Test Coverage:** No

### [P20-03] Serialization Enforcement Test Blind Spot: All `_`-Prefixed Attributes Excluded
- **Severity:** MODERATE
- **Category:** ARCHITECTURE
- **File:** tests/test_serialization_enforcement.py:40
- **Description:** `get_instance_attributes()` filters `k.startswith('_')`, making the test blind to ALL `_`-prefixed dynamic attributes — including P20-01 (`_diplomatic_trust_this_turn_N`), P20-02 (`_we_dispatched_thresholds`), and `_acted_this_turn`, `_debug_frozen`, `_last_tactical_events`. Any attribute needing persistence that uses `_` prefix is invisible.
- **Proposed Fix:** Add a known-`_`-fields allowlist to the test: verify that `_recovery_destination`, `_diplomatic_trust_this_turn`, etc. survive roundtrip.

### [P20-04] WorldState Roundtrip Test Only Covers Economy — Diplomacy/AI State Untested
- **Severity:** MODERATE
- **Category:** ARCHITECTURE
- **File:** tests/test_serialization_enforcement.py:415-433
- **Description:** `test_world_state_roundtrip_preserves_economy_fields` only checks `nation_gold`, `nation_bankruptcy_turns`, `admin_actions_remaining`, `gold_spent_this_turn`, `current_turn`. The 50+ diplomacy fields (`diplomatic_states`, `nation_relations`, `war_scores`, `active_coalition`, `vassals`, `threat_level`, etc.) and AI fields (`ai_stagnation_turns`, `ai_attack_futility`, `nation_actions`) have no roundtrip assertions.
- **Proposed Fix:** Add comprehensive roundtrip test asserting all diplomacy and AI fields survive save/load.

### [P20-05] WorldState `from_dict` Runs Full `__init__` Then Overwrites — Triple Visibility Calculation
- **Severity:** NOTE
- **Category:** ARCHITECTURE
- **File:** world_state.py:2766
- **Description:** `from_dict` calls `cls()` (running full `__init__` with region setup, marshal creation, visibility calculation), then overwrites everything with save data, then `save_manager.py:128` recalculates visibility. Three visibility calculations where only the last matters. Pure waste, not a bug.

### Pass 20 Summary: 1 MAJOR (dynamic trust attrs), 1 MINOR (WE thresholds), 2 MODERATE (test gaps), 1 NOTE.

---

## Pass 21: Fog of War Leak Sweep

### [P21-01] LLM Prompt Leaks All Enemy Positions and Exact Strengths
- **Severity:** MAJOR
- **Category:** BUG
- **File:** main.py:49-98
- **Description:** `get_llm_game_state()` iterates ALL enemy marshals with exact `location`, `strength`, `nation` — completely bypassing fog. Passed to `prompt_builder.py` which formats as "Wellington (British) at Waterloo, 65K troops" in the LLM prompt. Live LLM could mention fogged enemy data in dialogue. (Duplicate of P5-1 — remains unfixed.)
- **Proposed Fix:** Fog-filter `get_llm_game_state()`. Only include enemies at PARTIAL+ visibility, use strength bands.

### [P21-02] Battle Report Reveals Exact Enemy Pre/Post-Battle Strength
- **Severity:** MAJOR
- **Category:** BUG
- **File:** battle_report.py:789-793, main.py:875-876
- **Description:** After combat, `build_battle_report()` returns `defender_original` and `defender_remaining` as exact numbers. Passed unfiltered to Godot. Attacking into a fogged region reveals "Original: 45,000, Remaining: 32,400" — defeating fog at the moment it matters most.
- **Proposed Fix:** Check fog visibility for enemy region. Below FULL, replace exact numbers with strength bands.

### [P21-03] `/marshal_trust/{name}` Endpoint Returns Data for Enemy Marshals
- **Severity:** MINOR
- **Category:** BUG
- **File:** main.py:1473-1502
- **Description:** Accepts any marshal name including enemies. Returns trust, vindication, personality, recent battles/overrides. Not gated by DEBUG_MODE.
- **Proposed Fix:** Add nation check — reject non-player marshals.

### [P21-04] Strategic Ledger Intel Shows Exact Strength at STALE Visibility
- **Severity:** MINOR
- **Category:** BUG
- **File:** ledger.py:285-287
- **Description:** At STALE, shows "last seen: 45,000" — exact frozen number. Inconsistent with dispatch (which uses tilde prefix) and diplomatic ledger (which uses named bands).
- **Proposed Fix:** Use `get_strength_band(frozen)` for STALE.

### [P21-05] Dispatch Intelligence Shows ~Exact Strength at STALE
- **Severity:** MINOR
- **Category:** BUG
- **File:** dispatch.py:333-335
- **Description:** At STALE with strength key (no band), shows "~45,000" — tilde-prefixed exact number is more precise than intended.
- **Proposed Fix:** Use `get_strength_band()`.

### [P21-06] Ledger Nation Summary Aggregates Exact STALE Strengths
- **Severity:** MINOR
- **Category:** BUG
- **File:** ledger.py:336-340
- **Description:** Aggregates exact frozen strength values from STALE intel into nation "Estimated Strength" totals.
- **Proposed Fix:** Use band midpoints instead of exact frozen numbers.

### Verified Clean Systems
Morning dispatch, strategic ledger (non-intel), marshal overview, diplomatic ledger, war status panel, intel report, campaign log, diplomatic advisory, all debug endpoints — all properly fog-filtered. (10 systems verified.)

### Pass 21 Summary: 2 MAJOR (LLM prompt, battle report), 4 MINOR (trust endpoint, 3 STALE consistency issues).

---

## Pass 22: AI Parity Verification

### [P22-01] `decide_single_action` Sends Wrong Command Format to Executor — Autonomous Marshals Silently Fail
- **Severity:** CRITICAL
- **Category:** BUG
- **File:** enemy_ai.py:580-587
- **Description:** `decide_single_action()` builds a flat command dict `{"command_type": "specific", "marshal": ..., "action": ..., "target": ...}`. But `executor.execute()` expects nested format: `{"command": {"marshal": ..., "action": ..., "type": "specific"}}`. The executor reads `parsed_command.get("command", {})` which returns `{}`, so action = "unknown", marshal = None. Every autonomous player marshal action silently fails.
- **Evidence:** Contrast with `_execute_action` (line 5388) which uses the correct nested format. Test `test_decide_single_action_returns_result` checks `"result" in result` but never checks `result["result"]["success"]`.
- **Proposed Fix:** Change command dict to nested format matching `_execute_action`.
- **Test Coverage:** Test exists but masked — doesn't verify success.

### [P22-02] All Other AI Actions Use Correct Executor Path (Verified)
- **Severity:** NOTE (positive finding)
- **Category:** ARCHITECTURE
- **Description:** All AI actions (attack, move, defend, recruit, build, fortify, retreat, wait, form_square, break_square, stance_change, garrison, unfortify) use the correct nested command format and go through `executor.execute()`. Same AP costs, same combat modifiers, same movement restrictions. Objection checks correctly skipped for non-player nations. No direct state bypasses found. No impossible game states possible through AI actions.

### Pass 22 Summary: 1 CRITICAL (autonomous marshal broken), 1 positive verification note.

---

## FINAL GRAND TOTAL (Passes 1-22)

| Pass | CRITICAL | MAJOR | MINOR | NOTE | DESIGN | Total |
|------|----------|-------|-------|------|--------|-------|
| P1-P12 (initial) | 2 | 34 | 57 | 53 | 18 | 164 |
| P13 (auto-charge) | 4 | 13 | 8 | 0 | 0 | 25 |
| P14 (glorious charge) | 3 | 8 | 9 | 3 | 0 | 23 |
| P15 (turtle/balance) | 1 | 5 | 0 | 0 | 0 | 6 |
| P16 (test coverage) | 0 | 6 | 0 | 12 | 0 | 18 |
| P17 (turn ordering) | 0 | 1 | 1 | 0 | 0 | 2 |
| P18 (economy) | 0 | 1 | 1 | 2 | 7 | 11 |
| P19 (popups/notifs) | 0 | 0 | 0 | 2 | 11 | 13 |
| P20 (save/load) | 0 | 1 | 1 | 2 | 1 | 5 |
| P21 (fog leaks) | 0 | 2 | 4 | 0 | 0 | 6 |
| P22 (AI parity) | 1 | 0 | 0 | 1 | 0 | 2 |
| **GRAND TOTAL** | **11** | **71** | **81** | **75** | **37** | **275** |

### Top Priority Fixes (Final)

**Code bugs (fix immediately):**
1. **Extract shared post-combat processing** (P13+P14) — single root cause, 48 findings
2. **Fix coalition threat dict key** (P1-2) — `result["attacker_casualties"]` → `result["attacker"]["casualties"]`
3. **Fix autonomous marshal command format** (P22-01) — all autonomous actions silently fail
4. **Fix AP treaty penalty overwrite** (P17-01) — swap ordering in advance_turn
5. **Fix bankruptcy check timing** (P18-02) — move after all income sources
6. **Replace dynamic trust attrs** (P20-01) — memory leak + cap bypass on load
7. **Fog-filter LLM prompt** (P21-01) — leaks all enemy positions/strengths
8. **Fog-filter battle report** (P21-02) — reveals exact enemy strength on attack

**Balance/exploit fixes (design review needed):**
9. **Add early defeat condition** (P15-03) — capital loss = game over
10. **Remove permanent HOLD fortification immunity** (P15-04) — enables turtle exploit
11. **Add AI futility decay** (P15-05) — prevents permanent AI surrender
12. **Increase supply attrition cap** (P15-06) — prevents deathball exploit
13. **Show trade income in UI** (P18-01) — 137-337g/turn invisible

**Design priorities (game quality):**
14. **Implement Literal personality triggers** (P10-04) — game's USP unimplemented
15. **Add diplomatic victory condition** (P10-02) — diplomacy has no bearing on winning
16. **Add era pacing** (P10-01) — no mid-game arc or escalation structure
17. **Add AI deep raid behavior** (P11-08) — AI doesn't punish deathball
18. **Add notification cap** (P19-01) — infinite accumulation in long games

---

## AUDIT CLOSURE

**Completed:** 22 passes (12 initial + 10 targeted deep dives)
**Total findings:** 275 (11 CRITICAL, 71 MAJOR, 81 MINOR, 75 NOTE, 37 DESIGN)
**Unique root-cause bugs after deduplication:** ~140-150
**Not reached:** Pass 23 (Godot frontend deep dive) and Pass 24 (parser robustness) — subagents hit rate limits.

### Areas Covered
- Combat resolution, Tactical Triangle, coordination, pursuit, retreat (P1)
- Enemy AI decision tree, scoring, personality (P2)
- Strategic commands, pathfinding, conditions (P3)
- Disobedience, trust, vindication, authority, defiance (P4)
- Fog of war consumers, intel decay, visibility tiers (P5, P21)
- Turn flow, economy, manpower, AP system (P6, P17, P18)
- Godot frontend popups, signals, hotkeys (P7, P19)
- Parser, mock LLM, command vocabulary (P8)
- Code architecture, God Objects, duplication (P9)
- Game design coherence, fun analysis, thematic review (P10)
- Degenerate strategies, exploits, balance math (P11, P15)
- Cross-system integration, seam bugs (P12)
- Reckless auto-charge complete breakdown (P13)
- Glorious charge complete breakdown (P14)
- Test coverage gap analysis (P16)
- Save/load roundtrip, serialization (P20)
- AI parity verification (P22)

### Areas for Future Audit
- Godot frontend comprehensive code review (main.gd ~2800 lines, api_client.gd race conditions)
- Parser edge cases and keyword collision matrix
- Modding system validation pipeline
- Performance profiling under long-game conditions (40+ turns)
- Accessibility review (color contrast, screen reader compatibility)

