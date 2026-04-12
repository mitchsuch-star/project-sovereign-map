# Deep Audit Report — Ink & Iron
**Started:** 2026-03-23
**Base audit:** audit-report.md (72 findings)
**Purpose:** Verify, deepen, and extend base audit findings

---

## Pass 1: Verify Existing Findings

All CRITICAL and key MAJOR findings from the base audit have been verified against the current codebase. Every finding checked is CONFIRMED still present.

### [PASS-1] VASSAL State Handling — All 3 Bugs Confirmed
- **Severity:** CRITICAL
- **Files:** diplomacy.py:34-37, diplomacy.py:246-250, diplomacy.py:1945-1952, diplomacy.py:65-72
- **Description:** Three interrelated VASSAL bugs all confirmed:
  1. VASSAL missing from `_DOWNGRADE_ORDER` (line 34-37) — auto-downgrade silently skips VASSAL states, `execute_downgrade()` returns "Cannot downgrade from VASSAL"
  2. `post_break_map` maps VASSAL→NON_AGGRESSION (line 1951) but `validate_transition()` only allows VASSAL→WAR or PEACE (line 249-250) — state machine contradiction
  3. VASSAL missing from `STATE_RELATION_REQUIREMENTS` (line 65-72) — no explicit relation threshold
- **Test Coverage:** Partial. `test_vassal_post_break_map()` tests break but NOT validation conflict. Zero tests for VASSAL auto-downgrade.
- **Proposed Fix 1:** Add VASSAL to _DOWNGRADE_ORDER: `["ALLIANCE", "DEFENSIVE_ALLIANCE", "NON_AGGRESSION", "OPEN_BORDERS", "VASSAL", "PEACE"]`
- **Proposed Fix 2:** Update validate_transition: `return target_state in ("WAR", "PEACE", "NON_AGGRESSION")`
- **Proposed Fix 3:** Add to STATE_RELATION_REQUIREMENTS: `"VASSAL": None`

### [PASS-1] Popup Passthrough Gaps — 14 Endpoints, 42+ Missing Returns
- **Severity:** CRITICAL
- **File:** main.py (multiple locations)
- **Description:** 14 of 15 POST endpoints (93%) have return paths missing `_include_popup_passthroughs()`. 42+ distinct return statements affected. Patterns:
  - `/save`, `/load`, `/delete_save`, `/notifications/dismiss` — ZERO passthroughs on any path
  - 9 "respond_to_*" endpoints — early returns (game_over, validation) skip passthroughs
  - 4 debug endpoints — all returns unprotected
- **Evidence:** `/notifications/dismiss` (line 1933) returns on lines 1939, 1942, 1944 — none call passthrough. `/cancel_order` has 4 early returns (lines 1872-1892) all missing.
- **Test Coverage:** No test validates popup preservation across early return paths.
- **Proposed Fix:** Add `_include_popup_passthroughs(response, world)` before every return in every POST endpoint. Ideally refactor into a decorator/middleware.

### [PASS-1] Coalition Cooldown Override During Brewing — Confirmed
- **Severity:** CRITICAL (downgraded to MEDIUM by edge-case rarity)
- **File:** coalition.py:967-1082
- **Description:** Cooldown override (threat >= 90) is in `elif not world.active_coalition` block (line 1025-1029). During brewing phase (line 967-1022), `form_coalition()` sets `active_coalition`, making the `elif` false. Override never fires during brewing.
- **Test Coverage:** No test for "brewing at 90+ threat" scenario.
- **Proposed Fix:** Move cooldown override check to run BEFORE the brewing/threshold blocks.

### [PASS-1] Coalition Leader Selection Empty String — Confirmed
- **Severity:** CRITICAL (downgraded to LOW — guarded by form_coalition validation)
- **File:** coalition.py:221-236
- **Description:** `select_coalition_leader([])` returns `""`. However, `form_coalition()` guards with `len(all_members) < 2` before calling, so direct manifestation requires bypassing the guard.
- **Proposed Fix:** `if not members: raise ValueError("Cannot select leader from empty member list")`

### [PASS-1] Vassal Release Cooldown Off-By-One — Confirmed
- **Severity:** CRITICAL
- **File:** vassal.py:875-882
- **Description:** Identifies expired cooldowns (`<= 1`) BEFORE decrementing. Cooldowns at value 1 are marked expired and deleted, but were never decremented to 0. 5-turn cooldowns last 6 turns.
- **Evidence:**
  ```python
  expired_r = [n for n in release_cds if release_cds[n] <= 1]  # identifies <= 1
  for n in release_cds:
      if n not in expired_r:
          release_cds[n] -= 1  # only decrements > 1
  for n in expired_r:
      del release_cds[n]  # deletes the <= 1 entries
  ```
- **Proposed Fix:** Decrement ALL first, then identify <= 0:
  ```python
  for n in list(release_cds):
      release_cds[n] -= 1
  expired_r = [n for n in release_cds if release_cds[n] <= 0]
  for n in expired_r:
      del release_cds[n]
  ```

### [PASS-1] Gold Lump Sum Bankruptcy — Confirmed
- **Severity:** CRITICAL
- **File:** world_state.py:4298-4302
- **Description:** `gold_lump` clauses subtract directly: `self.nation_gold[from_nation] -= int(amount)` with no guard. Per-turn transfers properly use `min(amount, max(0, available))`.
- **Proposed Fix:**
  ```python
  available = max(0, self.nation_gold.get(from_nation, 0))
  transfer = min(int(amount), available)
  self.nation_gold[from_nation] -= transfer
  self.nation_gold[to_nation] += transfer
  ```

### [PASS-1] AI Counter-Offer DP Not Refunded — Confirmed
- **Severity:** CRITICAL
- **File:** executor.py:13282-13312
- **Description:** Player DP deducted at line 13287 (`world.diplomatic_points -= 1`) before `generate_counter_offer()` runs. If counter returns None, DP is lost. No refund path.
- **Additional Issue:** AI counter-offers deduct DP inside `generate_counter_offer()` (ai_diplomacy.py:1038-1045), creating two separate DP deduction paths. Inconsistent architecture.
- **Proposed Fix:** Move DP deduction after success check, or add refund: `if counter_terms is None: world.diplomatic_points += 1`

### [PASS-1] AI-AI Alliance Conflict Bypass — Confirmed
- **Severity:** MAJOR
- **File:** world_state.py:4210-4223
- **Description:** `_ratify_treaty()` has inline alliance conflict check for AI-AI that duplicates but is LESS complete than `check_alliance_conflict()` function. Player treaties use the full function (executor.py:13175).
- **Proposed Fix:** Call `check_alliance_conflict()` for AI-AI treaties too, removing inline duplicate.

### [PASS-1] AI-AI Relation Requirements Skipped — Confirmed
- **Severity:** MAJOR
- **File:** world_state.py:4189-4198
- **Description:** `if is_player_treaty:` guard wraps relation requirement check. AI-AI treaties bypass entirely — can form ALLIANCE at any relation level.
- **Proposed Fix:** Move relation check outside the `is_player_treaty` guard.

### [PASS-1] Trade Income Not in Strategic Ledger — Confirmed
- **Severity:** CRITICAL (integration gap)
- **File:** world_state.py:2252-2255
- **Description:** `calculate_turn_income()` has explicit `# TODO: Trade income (deferred to Session 2)`. `process_trade_income()` exists and works. Players see gold change but no breakdown.
- **Proposed Fix:** Wire `process_trade_income()` results into `calculate_turn_income()` breakdown dict.

### Pass 1 Summary
**Findings verified:** 11 (all confirmed still present)
**CRITICAL confirmed:** 8
**MAJOR confirmed:** 3
**New sub-issues discovered:** 2 (AI DP deduction path inconsistency, popup passthrough count higher than originally reported — 42+ vs 13+)

---

## Pass 2: Line-by-Line Critical File Review

### diplomacy.py — 7 NEW Issues Found

### [PASS-2] [DIPLOMACY] Raw war score sign flip in get_diplomatic_preview
- **Severity:** MAJOR
- **File:** diplomacy.py:2681
- **Description:** `get_diplomatic_preview` reads raw war score keyed by alphabetically-sorted diplo_key. If player ("France") is alphabetically second (e.g., "Austria|France"), a positive score means Austria is winning, but code treats it as player winning. Produces wrong armistice proposal type in diplomacy wizard.
- **Evidence:** `"propose_armistice": "armistice_winning" if (getattr(world, 'war_scores', {}).get(diplo_key, 0) > 0) else "armistice_losing"`
- **Proposed Fix:** Replace with `get_war_score_for(world, player, target_nation) > 0`
- **Test Coverage:** No

### [PASS-2] [DIPLOMACY] break_treaty adds coalition threat even when AI breaks treaty
- **Severity:** MAJOR
- **File:** diplomacy.py:1938-1940
- **Description:** Coalition threat is France-specific (how threatening France is). When an AI nation breaks a treaty with France, `add_threat()` still fires, adding threat to France. Compare with `declare_war` (line 970) which correctly gates on `aggressor == world.player_nation`.
- **Evidence:** `add_threat(world, threat_amount, f"broke_{treaty_type}")` — no breaker_nation check
- **Proposed Fix:** Wrap in `if breaker_nation == world.player_nation:` guard
- **Test Coverage:** No

### [PASS-2] [DIPLOMACY] check_auto_downgrade does not remove active treaty
- **Severity:** MAJOR
- **File:** diplomacy.py:1330
- **Description:** Manual `execute_downgrade()` removes active treaty (line 1255-1256: `active_treaties.pop(diplo_key, None)`). Auto-downgrade in `check_auto_downgrade()` changes diplomatic state WITHOUT removing the corresponding active treaty. Leaves stale treaty object referencing a state that no longer exists.
- **Proposed Fix:** Add `active_treaties = getattr(world, 'active_treaties', {}); active_treaties.pop(diplo_key, None)` after state transition.
- **Test Coverage:** No

### [PASS-2] [DIPLOMACY] _process_relation_decay skips ALL pairs involving any vassal
- **Severity:** MINOR
- **File:** diplomacy.py:2050-2052
- **Description:** `if nation_a in vassals or nation_b in vassals: continue` — skips decay for vassal-to-third-party pairs, not just vassal-lord pairs. A vassal's relations with non-lord nations never decay, leaving artificially frozen relations.
- **Proposed Fix:** Only skip when one is vassal and the other is its lord.
- **Test Coverage:** No

### [PASS-2] [DIPLOMACY] process_trade_income only applies to nations already in nation_gold
- **Severity:** MINOR
- **File:** diplomacy.py:1637-1639
- **Description:** `if nation in world.nation_gold:` guard silently drops trade income for any nation not pre-initialized in `nation_gold`. Other income sources use `.get()` with defaults.
- **Proposed Fix:** Use `world.nation_gold[nation] = world.nation_gold.get(nation, 0) + int(income)`
- **Test Coverage:** No

### [PASS-2] [DIPLOMACY] armistice_turns counter not cleared on war restart
- **Severity:** MINOR
- **File:** diplomacy.py:1662-1664
- **Description:** If a pair goes ARMISTICE (3 turns) → WAR → ARMISTICE, the counter resumes at 3 not 0, causing early armistice expiration. `cleanup_war_end` doesn't clear `armistice_turns`.
- **Proposed Fix:** Reset `armistice_turns[diplo_key] = 0` in WAR→ARMISTICE transition handler.
- **Test Coverage:** No

### [PASS-2] [DIPLOMACY] continental_system_members not cleaned up on vassal release
- **Severity:** MINOR
- **File:** diplomacy.py:2107-2108
- **Description:** Released vassals stay in `continental_system_members` forever. No cleanup when vassal is removed from `world.vassals`.
- **Proposed Fix:** Remove released vassals from members list in vassal release handler.
- **Test Coverage:** No

---

### coalition.py — 3 NEW Issues Found

### [PASS-2] [COALITION] Wedge penalty halving rounds wrong direction
- **Severity:** MAJOR
- **File:** coalition.py:456
- **Description:** `penalty = penalty // 2` — Python `//` rounds toward negative infinity. For -15: `-15 // 2 = -8`. But COALITION_SPEC §6c says "halved (-7 instead of -15)", expecting truncation toward zero (-7).
- **Evidence:** `penalty = penalty // 2  # Halve (rounds toward zero)` — comment is wrong
- **Proposed Fix:** `penalty = int(penalty / 2)  # Truncate toward zero`
- **Test Coverage:** No

### [PASS-2] [COALITION] _we_dispatched_thresholds not serialized — lost on save/load
- **Severity:** MINOR
- **File:** coalition.py:481, 490
- **Description:** `_we_dispatched_thresholds` dict is dynamically attached to WorldState via `setattr` but never in `__init__`, `to_dict()`, or `from_dict()`. After save/load, dict resets to `{}` and WE threshold dispatches re-fire.
- **Proposed Fix:** Add to WorldState serialization, or accept as soft state.
- **Test Coverage:** No

### [PASS-2] [COALITION] Brewing instant-override failure leaves brewing in limbo
- **Severity:** MINOR
- **File:** coalition.py:987-994
- **Description:** If threat >= 80 during brewing AND `form_coalition()` returns failure (e.g., < 2 members), brewing persists forever with `turns_remaining` going negative. Notifications show negative turn counts.
- **Proposed Fix:** Cancel brewing on form_coalition failure.
- **Test Coverage:** No

---

### vassal.py — 7 NEW Issues Found

### [PASS-2] [VASSAL] Conquest vassalization skips release cooldown check
- **Severity:** MAJOR
- **File:** vassal.py:122-171
- **Description:** `create_vassal_treaty()` checks `vassal_release_cooldowns` (R14 anti-exploit, line 76-82). `create_vassal_conquest()` skips it entirely. A recently-released nation can be immediately re-vassalized through conquest.
- **Proposed Fix:** Add same cooldown check from lines 76-82 to `create_vassal_conquest`.
- **Test Coverage:** No

### [PASS-2] [VASSAL] Battle victor lookup counts unfindable marshal as loss
- **Severity:** MINOR
- **File:** vassal.py:272-276
- **Description:** If `world.get_marshal(victor)` returns None (marshal killed/captured after battle), code falls to `else` and counts it as a loss. A win becomes a loss, causing -2 loyalty swing per affected battle.
- **Proposed Fix:** Store victor's nation in battle record, or check `battle.get("victor_nation")`.
- **Test Coverage:** No

### [PASS-2] [VASSAL] garrison_vassal_rebellion succeeds on removed vassal
- **Severity:** MINOR
- **File:** executor.py:12919
- **Description:** If vassal was removed between popup display and player response, `world.vassals.get(vassal_name, {})` returns empty dict. Code writes loyalty=10 to throwaway dict, reports success, deducts 2 AP.
- **Proposed Fix:** Add existence check: `if vassal_name not in world.vassals: return failure`
- **Test Coverage:** No

### [PASS-2] [VASSAL] invest_in_vassal uses player DP regardless of lord nation
- **Severity:** MINOR
- **File:** vassal.py:626, 642
- **Description:** Always deducts from `world.diplomatic_points` (player DP pool). If called for AI-lorded vassal, would deduct player DP. Currently no trigger path, but function doesn't validate lord.
- **Proposed Fix:** Add guard: `if lord != world.player_nation: return failure`
- **Test Coverage:** No

### [PASS-2] [VASSAL] release_vassal doesn't clear stale rebellion popup/dialogue
- **Severity:** MINOR
- **File:** vassal.py:802-855
- **Description:** Releasing a vassal doesn't clear `world.vassal_rebellion_imminent_popup` or `world.pending_diplomatic_dialogue` if they reference the released vassal. Could cause softlock if rebellion popup was active.
- **Proposed Fix:** Clear popup/dialogue for released vassal in `release_vassal()`.
- **Test Coverage:** No

### [PASS-2] [VASSAL] Multi-rebellion cascade can zero vassals without same-turn rebellion
- **Severity:** MINOR
- **File:** vassal.py:440-443
- **Description:** Rebellion cascade applies -10 loyalty to all other vassals. Multiple rebellions in same turn stack cascades. A vassal at loyalty 15 drops to 0 but won't rebel until next turn.
- **Test Coverage:** No

### [PASS-2] [VASSAL] Popup text still promises +15 loyalty/+5 relations vs actual +10/+0
- **Severity:** MAJOR (confirmed — re-verified from base audit)
- **File:** vassal.py:326, 341 vs vassal.py:35, 645
- **Description:** Popup says "+15 loyalty, relations +5" but `INVEST_LOYALTY_GAIN = 10` and no relation bonus exists. Player-facing text does not match mechanics.
- **Proposed Fix:** Change popup text to "+10 loyalty" and remove "relations +5".
- **Test Coverage:** No

---

### executor.py (Diplomatic) — 6 NEW Issues Found

### [PASS-2] [EXECUTOR] Glorious Charge missing record_diplo_battle
- **Severity:** MAJOR
- **File:** executor.py:10300-10305
- **Description:** `_execute_glorious_charge` calls `world.record_battle()` but never calls `record_diplo_battle()`. In contrast, `_execute_attack` calls both. Glorious Charge victories/defeats don't affect war score. A decisive cavalry charge has zero diplomatic weight.
- **Proposed Fix:** Add `record_diplo_battle()` call after combat resolution in glorious charge.
- **Test Coverage:** No

### [PASS-2] [EXECUTOR] Ultimatum accepted bypasses state machine side effects
- **Severity:** MAJOR
- **File:** executor.py:11757-11765
- **Description:** Accepted ultimatum directly sets `world.diplomatic_states[diplo_key]` to "PEACE" without going through normal state transition machinery. Skips: war end recording, active treaty removal, armistice cooldown, relation improvement, dispatch event, log event.
- **Proposed Fix:** Use `_ratify_treaty()` or manually replicate critical side effects.
- **Test Coverage:** No

### [PASS-2] [EXECUTOR] Alliance paradox "honor defender" doesn't deduct DP
- **Severity:** MAJOR
- **File:** executor.py:12959-12972
- **Description:** `honor_defender` calls `declare_war()` which returns DP cost but doesn't deduct. Normal war declaration (`_execute_diplomatic_declare_war`) deducts at line 11648. Paradox gives free war declaration.
- **Proposed Fix:** Add `world.diplomatic_points -= 1` or document as intentional waiver.
- **Test Coverage:** No

### [PASS-2] [EXECUTOR] Alliance paradox "break defender" stacks full downgrade penalties
- **Severity:** MAJOR
- **File:** executor.py:12986-12990
- **Description:** Break handler loops `execute_downgrade()` from ALLIANCE to PEACE. Each call applies full relation penalties + threat increases. Cumulative: -60 relation with target, -10 with all others, +13 threat. Extremely punitive for a forced-choice scenario.
- **Proposed Fix:** Use `break_treaty()` for single set of penalties, or apply penalties only once.
- **Test Coverage:** No

### [PASS-2] [EXECUTOR] Treaty acceptance paths missing trust reactions (dead code)
- **Severity:** MINOR
- **File:** executor.py:13208, 12845
- **Description:** Trust reaction table has entries for "treaty_signed" and "alliance_formed" but these are never triggered by any acceptance path. Dead code in trust reaction table.
- **Test Coverage:** No

### [PASS-2] [EXECUTOR] Hardcoded nation list in no-target proposal fallback
- **Severity:** MINOR
- **File:** executor.py:11249-11264
- **Description:** No-target fallback lists 4 hardcoded nations (Britain, Prussia, Austria, Saxony) with static descriptions that don't reflect actual game state. Mod-unfriendly.
- **Proposed Fix:** Build dynamically from `get_known_nations(world)`.
- **Test Coverage:** No

---

### ai_diplomacy.py — 6 NEW Issues Found

### [PASS-2] [AI-DIPLO] Territory sweetener inflated from 1 to 5 regions by max(5, ...)
- **Severity:** MAJOR
- **File:** ai_diplomacy.py:1183-1184
- **Description:** `max(5, int(desire.get("value", 0)))` was designed for gold floors but applies to territory too. A 1-region offer becomes 5 regions, scored as `8 * 5 = 40` acceptance points instead of `8 * 1 = 8`. AI counter-offers with territory are wildly overpowered.
- **Evidence:** `sweetener_value = max(5, int(desire.get("value", 0)))` — no type check
- **Proposed Fix:** Only apply max(5,...) to gold types: `if dtype in ("gold_lump", "gold_per_turn"): sweetener_value = max(5, ...) elif dtype == "territory": sweetener_value = max(1, ...)`
- **Test Coverage:** No

### [PASS-2] [AI-DIPLO] Proposal metadata updated for failed proposals, suppressing urgent re-proposals
- **Severity:** MINOR
- **File:** ai_diplomacy.py:759-764
- **Description:** `_make_proposal` updates `ai_proposal_metadata` war_score before viability check (score < 20). Failed attempts refresh the war_score reference, preventing urgency delta from reaching 20 for re-proposals.
- **Proposed Fix:** Move metadata recording to after viability check.
- **Test Coverage:** No

### [PASS-2] [AI-DIPLO] Urgency bypass fires incorrectly for peacetime proposals
- **Severity:** MINOR
- **File:** ai_diplomacy.py:222-239
- **Description:** A nation that had a war proposal rejected can bypass cooldown for unrelated peacetime alliance proposals, because urgency check compares old war_score (positive) with peacetime war_score (0), producing delta >= 20.
- **Proposed Fix:** Add war-state check in `_is_situation_urgent`: only return True if at war.
- **Test Coverage:** No

### [PASS-2] [AI-DIPLO] Stalemate counter persists across wars
- **Severity:** MINOR
- **File:** ai_diplomacy.py:360-371
- **Description:** `ai_stalemate_counters` keyed by nation is never cleared when war ends. New war starts with residual count, potentially triggering premature stalemate proposal.
- **Proposed Fix:** Clear stalemate counter on war end.
- **Test Coverage:** No

### [PASS-2] [AI-DIPLO] _process_ai_ai_rivalry doesn't filter eliminated nations
- **Severity:** MINOR
- **File:** ai_diplomacy.py:1300
- **Description:** Unlike `process_ai_ai_diplomatic_phase` (line 1420), rivalry function iterates all `enemy_nations` including eliminated ones. Wasteful and fragile.
- **Proposed Fix:** Add same filter: `[n for n in enemy_nations if not _is_nation_eliminated(world, n)]`
- **Test Coverage:** No

### [PASS-2] [AI-DIPLO] Zero-income nations can't sweeten proposals
- **Severity:** MINOR
- **File:** ai_diplomacy.py:412-414
- **Description:** R113 cap `max_per_turn = income // 2` suppresses sweeteners entirely for devastated nations (income=0). Makes peace harder when most desperate.
- **Proposed Fix:** Set minimum floor: `max_per_turn = max(10, income // 2)`
- **Test Coverage:** No

---

### diplomatic_defiance.py + diplomatic_templates.py — 7 NEW Issues Found

### [PASS-2] [DEFIANCE] War score sign may be wrong in evaluate_pre_proposal_objection
- **Severity:** MAJOR
- **File:** diplomatic_defiance.py:660-665
- **Description:** Manual sign-flip logic instead of using `get_war_score_for()`. Same pattern as diplomacy.py:2681 preview bug. Fragile and may produce wrong sign.
- **Proposed Fix:** Replace with `get_war_score_for(world, "France", target_nation)`
- **Test Coverage:** No

### [PASS-2] [DEFIANCE] "stalled" sabotage type has no actual effect
- **Severity:** MAJOR
- **File:** diplomatic_defiance.py:235-237
- **Description:** `stalled` branch sets defiance_type but makes NO modifications to proposal. Original and modified proposals are identical. Triggers confrontation dialogue showing "sabotage" with no visible change.
- **Proposed Fix:** Implement delivery delay or add minor modification.
- **Test Coverage:** No

### [PASS-2] [DEFIANCE] War declaration objection fires STRONG for all non-WAR states
- **Severity:** MINOR
- **File:** diplomatic_defiance.py:649
- **Description:** STRONG objection for declaring war on an ally gets same strength as declaring war on a hostile nation at NON_AGGRESSION. No gradation based on existing relationship.
- **Test Coverage:** No

### [PASS-2] [DEFIANCE] Territory sabotage can leave empty regions list
- **Severity:** MINOR
- **File:** diplomatic_defiance.py:211-214
- **Description:** If territory demand has exactly 1 region, sabotage produces demand with `regions: []`. Not cleaned up.
- **Proposed Fix:** Remove entire demand if regions list becomes empty.
- **Test Coverage:** No

### [PASS-2] [TEMPLATES] resolve_template_text war_score sign not adjusted for France
- **Severity:** MAJOR
- **File:** diplomatic_templates.py:1159
- **Description:** Same raw war_score sign bug. `slots["war_score"]` uses raw `world.war_scores.get(diplo_key, 0)` without France-perspective adjustment.
- **Proposed Fix:** Use `get_war_score_for(world, "France", target_nation)`
- **Test Coverage:** No

### [PASS-2] [TEMPLATES] Coalition template T29 {turns_remaining} slot no auto-fill
- **Severity:** MINOR
- **File:** diplomatic_templates.py:891
- **Description:** `resolve_coalition_template` only auto-fills `threat_level`. `{turns_remaining}` must be explicitly passed; if forgotten, literal slot name appears in output.
- **Test Coverage:** No

### [PASS-2] [TEMPLATES] calculate_treaty_harshness vs calculate_proposal_harshness use different field names
- **Severity:** MINOR
- **File:** diplomatic_templates.py:1726-1740 vs diplomatic_defiance.py:132-162
- **Description:** Treaty harshness reads `clauses`/`amount`; proposal harshness reads `demands`/`value`. If wrong function called on wrong structure, silently returns 0.0.
- **Test Coverage:** No

### Pass 2 Summary
**New findings:** 36 (7 diplomacy + 3 coalition + 7 vassal + 6 executor + 6 ai_diplomacy + 7 defiance/templates)
**MAJOR:** 14
**MINOR:** 22
**Key patterns discovered:**
1. **War score sign bug is systemic** — appears in 4 separate locations (diplomacy preview, defiance objection, template resolution, and potentially elsewhere). All use raw war_scores dict instead of `get_war_score_for()`.
2. **Stale state after transitions** — auto-downgrade doesn't clean active treaties, ultimatum acceptance skips side effects, released vassals leave stale popups/members.
3. **AI counter-offer territory inflation** — max(5,...) floor designed for gold accidentally inflates territory offers 5x.

---

## Pass 3: Data Flow Tracing

### War Declaration Flow — 4 NEW Issues

### [PASS-3] [WAR-DECL] Talleyrand objection popup field names don't match Godot expectations
- **Severity:** MAJOR
- **File:** executor.py:11628-11636 vs talleyrand_objection_popup.gd:36-39
- **Description:** War declaration Talleyrand objection sets `"severity"` and `"message"` fields, but Godot popup reads `"concern_level"` and `"objection_text"`. Actual objection message is never displayed. Player sees default placeholder text. Same bug at ultimatum objection (line 11697-11705).
- **Proposed Fix:** Rename fields to match Godot: `"concern_level"` instead of `"severity"`, `"objection_text"` instead of `"message"`.
- **Test Coverage:** No

### [PASS-3] [WAR-DECL] "Proceed" from war objection misroutes to proposal flow
- **Severity:** MAJOR
- **File:** main.gd:2793, executor.py:11625-11641
- **Description:** When player clicks "Proceed" on war declaration objection, Godot sends `"Talleyrand, proceed with the proposal"` which mock parser routes to `diplomatic_proposal`, NOT `diplomatic_declare_war`. War declaration is lost; player enters proposal flow instead.
- **Proposed Fix:** Send action-specific command or use a POST endpoint that carries the original action type.
- **Test Coverage:** No

### [PASS-3] [WAR-DECL] War declaration objection infinitely re-triggers
- **Severity:** MAJOR
- **File:** executor.py:11625-11641
- **Description:** Every call to `_execute_diplomatic_declare_war` when `threat_level > 50` fires objection (checks `not world.diplomatic_objection_popup`). After popup is cleared by passthrough, next war declaration attempt re-triggers. No mechanism tracks that player already overrode this objection. Currently masked by the misrouting bug above.
- **Proposed Fix:** Add a `war_declaration_objection_overridden` flag or check `pending_diplomatic_dialogue`.
- **Test Coverage:** No

### [PASS-3] [WAR-DECL] /respond_to_diplomatic_dialogue missing top-bar state fields
- **Severity:** MINOR
- **File:** main.py:1161-1166
- **Description:** After `force_declare_war` (deducts 1 DP, adds +20 threat), response lacks `diplomatic_points`, `threat_level`, etc. Godot top bar won't update until next `/command` call.
- **Test Coverage:** No

---

### Turn Pipeline Flow — 4 NEW Issues

### [PASS-3] [TURN] battles_this_turn cleared before vassal loyalty reads it
- **Severity:** MAJOR
- **File:** world_state.py:3670 vs 3833, vassal.py:262
- **Description:** `clear_turn_battles()` at line 3670 empties `battles_this_turn`. Vassal loyalty processing at line 3833 reads it. The "Lord winning/losing battles" modifier (+1 per win max +3, -2 per loss max -6) is DEAD CODE — never fires because battles are always empty by the time vassal loyalty processes.
- **Proposed Fix:** Move `clear_turn_battles()` to after vassal processing (after line 3837), or save battles before clearing.
- **Test Coverage:** No

### [PASS-3] [TURN] Armistice expiration events not reported in Morning Dispatch
- **Severity:** MINOR
- **File:** diplomacy.py:1680-1696, dispatch.py
- **Description:** Armistice expiration events (`armistice_expired_peace`, `armistice_expired_war`) not in `_DISPATCH_EVENT_TYPES` whitelist and have no `queue_dispatch_event` call. Player never told when armistice expires.
- **Test Coverage:** No

### [PASS-3] [TURN] Downgrade warning events silently lost
- **Severity:** MINOR
- **File:** diplomacy.py:1312
- **Description:** `check_auto_downgrade` emits `downgrade_warning` event 2 turns before auto-downgrade. Not in dispatch whitelist, no `queue_dispatch_event` call. Player gets no advance warning.
- **Test Coverage:** No

### [PASS-3] [TURN] Mission cancellation (nation eliminated) not dispatched
- **Severity:** MINOR
- **File:** diplomacy.py:1869-1885
- **Description:** `_check_mission_target_eliminated` returns event but doesn't call `queue_dispatch_event`. Contrast with DP-paused cancellation which does call it. Player not told if Talleyrand's mission auto-cancels.
- **Test Coverage:** No

---

### Battle → War Score Flow — 3 NEW Issues

### [PASS-3] [BATTLE] Coordinated battles record ZERO casualties for war score
- **Severity:** CRITICAL
- **File:** executor.py:4706-4707, combat.py:1174
- **Description:** Coordinated multi-marshal battles use `apply_casualties=False`, returning `attacker_raw_casualties`/`defender_raw_casualties` keys. Executor reads `attacker_casualties`/`defender_casualties` which defaults to 0. These battles NEVER pass the 1000-casualty threshold in `record_battle()`, making the game's largest engagements **completely invisible to the war score system**.
- **Evidence:** `.get("attacker_casualties", 0)` on a dict that has `attacker_raw_casualties` instead
- **Proposed Fix:** Use `battle_result.get("attacker_casualties", 0) or battle_result.get("attacker_raw_casualties", 0)` or set `attacker_casualties` after distribution.
- **Test Coverage:** No

### [PASS-3] [BATTLE] Garrison combat not recorded for war score
- **Severity:** MINOR
- **File:** executor.py:2697-2846
- **Description:** `_resolve_garrison_combat()` never calls `record_diplo_battle()`. Capital assault casualties invisible to war score (though capital occupation does contribute via capital component).
- **Test Coverage:** No

### [PASS-3] [BATTLE] Glorious Charge not recorded for war score (confirmed from Pass 2)
- **Severity:** MAJOR (re-confirmed via independent data flow trace)
- **File:** executor.py:10300-10305

---

### Vassal Creation + Tribute Flow — 5 NEW Issues

### [PASS-3] [VASSAL] _ratify_treaty does NOT call create_vassal_treaty for vassalage proposals
- **Severity:** CRITICAL
- **File:** world_state.py:4144-4426
- **Description:** `_ratify_treaty` sets diplomatic state to "VASSAL" (line 4227) but NEVER calls `create_vassal_treaty()` from vassal.py. Result: `world.vassals` dict is never populated, no loyalty tracking, no tribute, no marshal assimilation. The diplomatic state says VASSAL but the vassal system is completely unaware. Only the direct `_execute_make_vassal` path (executor.py:14062) correctly calls `create_vassal_treaty`.
- **Proposed Fix:** Add `create_vassal_treaty(world, target_nation, proposer)` call in `_ratify_treaty` when target_state is "VASSAL".
- **Test Coverage:** No (this is a fundamental integration gap)

### [PASS-3] [VASSAL] vassal_tribute field in diplomatic preview always shows 0
- **Severity:** MAJOR
- **File:** diplomacy.py:2657
- **Description:** Preview reads `v.get("tribute_income", 0)` but vassal dict has no `tribute_income` field. Fields are: lord, loyalty, autonomy, path, created_turn, tribute_rate, carved_from, regions. Tribute calculated in `process_vassal_tribute` but never stored back.
- **Proposed Fix:** Either store calculated tribute on the dict, or compute it live in preview.
- **Test Coverage:** No

### [PASS-3] [VASSAL] vassal_rebellion_imminent_popup never cleared after player responds
- **Severity:** MAJOR
- **File:** executor.py:12891-12947
- **Description:** Rebellion response handlers clear `pending_diplomatic_dialogue` but not `world.vassal_rebellion_imminent_popup`. Stale data persists and serializes into save files.
- **Proposed Fix:** Add `world.vassal_rebellion_imminent_popup = None` in each response handler.
- **Test Coverage:** No

### [PASS-3] [VASSAL] Voluntary release doesn't clean relationship_with_lord on marshals
- **Severity:** MINOR
- **File:** vassal.py:816-820
- **Description:** `release_vassal()` clears `original_nation` but leaves `relationship_with_lord` as stale attribute. Rebellion handler (line 437-438) does clean it with `delattr`.
- **Test Coverage:** No

### [PASS-3] [VASSAL] Tribute not shown in Strategic Ledger or Morning Dispatch
- **Severity:** MINOR
- **File:** ledger.py, dispatch.py
- **Description:** Neither references tribute. `process_vassal_tribute` silently transfers gold but no income breakdown shows it. Players can't see tribute income source.
- **Test Coverage:** No

### Pass 3 Summary
**New findings:** 16 (4 war declaration + 4 turn pipeline + 3 battle/war score + 5 vassal)
**CRITICAL:** 2 (coordinated battle casualties invisible to war score, _ratify_treaty doesn't create vassal)
**MAJOR:** 8
**MINOR:** 6
**Key patterns discovered:**
1. **Vassal treaty creation via _ratify_treaty is fundamentally broken** — diplomatic state set to VASSAL but no vassal dict entry created. This is arguably the single most impactful bug found.
2. **Coordinated battles invisible to war score** — the game's largest engagements don't affect diplomacy at all, due to mismatched casualty field names.
3. **battles_this_turn cleared too early** — vassal loyalty battle modifier is dead code.
4. **War declaration Talleyrand objection flow is broken at 3 levels** — wrong field names, misrouted proceed, infinite re-trigger.

---

## Pass 4: Edge Case Hunting

### Zero/Negative/Extreme Value Bugs — 2 Found

### [PASS-4] [COALITION] Floor division on negative weighted_sum biases coalition war score
- **Severity:** MINOR
- **File:** coalition.py:269
- **Description:** `int(weighted_sum // total_weight)` — Python `//` floors toward -infinity. When France is winning (weighted_sum negative), score is off by -1. Can cross posture thresholds. Same `//` pattern as wedge penalty (Pass 2).
- **Proposed Fix:** `int(weighted_sum / total_weight)` (truncate toward zero)
- **Test Coverage:** No

### [PASS-4] [DIPLOMACY] Missing sweetener value key zeros out flat-rate bonuses
- **Severity:** MINOR
- **File:** diplomacy.py:634, 649
- **Description:** For flat-rate sweeteners (open_borders rate=3, protection rate=5), if dict lacks `"value"` key, defaults to 0 via `.get("value", 0)`. Then `rate * 0 = 0` instead of the flat `rate`. Currently all AI code passes `value: 1` but fragile for future additions.
- **Proposed Fix:** `svalue = s.get("value") or 1` for flat types
- **Test Coverage:** No

### Duplicate/Simultaneous Operations — 4 NEW Issues

### [PASS-4] [STATE-MACHINE] Stale AI proposal acceptance bypasses WAR→ARMISTICE→PEACE adjacency
- **Severity:** CRITICAL
- **File:** executor.py:13203-13208, world_state.py:4178-4227
- **Description:** If AI sends peace proposal, then coalition declares war on that nation before player responds, clicking "Accept" on stale popup ratifies WAR→PEACE directly, skipping ARMISTICE. `_handle_accept_ai_proposal` has no state freshness check. `_ratify_treaty` only checks upgrade order (PEACE is "higher" than WAR), not adjacency. Same bug on `accept_counter_offer` (executor.py:12833-12845).
- **Proposed Fix:** Add state freshness check before `_ratify_treaty`: verify current diplomatic state is compatible with proposal type. Add adjacency validation in `_ratify_treaty`.
- **Test Coverage:** No

### [PASS-4] [STATE-MACHINE] "Accepted" message emitted even when _ratify_treaty fails
- **Severity:** MAJOR
- **File:** world_state.py:4015-4030
- **Description:** `_process_proposal_in_transit` emits "they have accepted our proposal!" message regardless of whether `_ratify_treaty` actually succeeded. If treaty ratification returns failure dict, the success message still shows.
- **Proposed Fix:** Check `treaty_event` for failure before emitting success message.
- **Test Coverage:** No

### [PASS-4] [DIPLOMACY] break_treaty doesn't void proposal_in_transit targeting affected nation
- **Severity:** MAJOR
- **File:** diplomacy.py:1888-2000
- **Description:** If AI breaks treaty while Talleyrand is en route with proposal to same nation, proposal still resolves next turn against changed diplomatic state. Player sees rejection with no context about the treaty break.
- **Proposed Fix:** In `break_treaty()`, clear `proposal_in_transit` and reset `talleyrand_state` to IDLE if targeting affected nation.
- **Test Coverage:** No

### [PASS-4] [DIPLOMACY] break_treaty doesn't clear pending_diplomatic_dialogue about same treaty
- **Severity:** MINOR
- **File:** diplomacy.py:1888-2000
- **Description:** If pending dialogue references the treaty being broken, dialogue persists referencing stale state.
- **Test Coverage:** No

### Cross-System Consistency — War Score Sign Bug is SYSTEMIC (4 locations)

### [PASS-4] [WAR-SCORE] Raw war_scores access without sign adjustment — 4 confirmed locations
- **Severity:** CRITICAL (systemic)
- **Files:**
  1. diplomatic_dialogue.py:355 — context snapshot for dialogue
  2. diplomatic_dialogue.py:825 — advisory dialogue context
  3. diplomatic_templates.py:1159 — template slot resolver
  4. diplomacy.py:2681 — armistice winning/losing determination
- **Description:** All 4 read `world.war_scores.get(diplo_key, 0)` without sign adjustment. War scores are stored from alphabetically-first nation's perspective. For France vs Austria/Britain (alphabetically before France), positive raw = opponent winning, but code treats as France winning. **Result: France gets "winning" armistice terms when actually losing against Austria/Britain. Dialogue text shows inverted war score. Template text shows wrong sign.**
- **Proposed Fix:** Replace all 4 with `get_war_score_for(world, "France", target_nation)` (or `player_nation` equivalent).
- **Test Coverage:** No

### Cross-System Consistency — Static Nation Lists (3 locations)

### [PASS-4] [NATIONS] Hardcoded nation lists instead of dynamic
- **Severity:** MINOR
- **Files:**
  1. dispatch.py:541 — `known_nations = ["Britain", "Prussia", "Austria", "Saxony"]`
  2. diplomatic_advisory.py:700 — uses static `KNOWN_NATIONS` set
  3. main.py:2285 — `all_nations = ["France", "Britain", "Prussia", "Austria", "Saxony"]`
- **Description:** Should use `get_known_nations(world)` or `world.enemy_nations` for mod compatibility.
- **Test Coverage:** N/A

### Cross-System Consistency — getattr Defaults Inconsistency

### [PASS-4] [DEFAULTS] talleyrand_state defaults inconsistent across codebase
- **Severity:** MINOR
- **Files:** Multiple (diplomacy.py, executor.py use `'IDLE'`; coalition.py, diplomacy.py:1761 use `''`)
- **Description:** Functionally equivalent currently, but maintenance hazard if `== 'IDLE'` check added where `''` is default.
- **Test Coverage:** N/A

### Pass 4 Summary
**New findings:** 12
**CRITICAL:** 2 (stale proposal bypasses adjacency, war score sign systemic)
**MAJOR:** 2 (accepted message on ratify failure, break_treaty doesn't void proposal)
**MINOR:** 8
**Positive finding:** No division-by-zero bugs found. Codebase has good guards for zero values. int() wrapping is comprehensive for Godot.

---

## Pass 5: Test Gap Analysis

### Critical Untested Functions

| Function | File | Status | Missing Coverage |
|----------|------|--------|-----------------|
| `_is_situation_urgent` | ai_diplomacy.py | **ZERO tests** | Controls AI cooldown bypass for urgent re-proposals |
| `check_sabotage_discovery_deterministic` | diplomatic_defiance.py | **ZERO refs** | Completely unreferenced anywhere |
| `break_treaty` on VASSAL state | diplomacy.py | Partial | VASSAL→NON_AGGRESSION post_break_map path untested |
| `check_vassal_rebellion` cascade | vassal.py | No | -10 loyalty cascade to other vassals untested |
| `record_battle` <1000 casualty filter | diplomacy.py | No | Threshold boundary untested |
| `process_coalition_turn` passive threat | coalition.py | No | Region control 60/70/80% thresholds untested |
| `process_coalition_turn` member friction | coalition.py | No | -2/turn inter-member relation decay untested |
| `_execute_diplomatic_ultimatum` accepted outcome | executor.py | No | WAR→PEACE vs non-WAR→NON_AGGRESSION branching untested |
| `process_trade_income` vassal exclusion | diplomacy.py | No | Vassals should get 0 trade — not verified |
| `_execute_glorious_charge` diplo recording | executor.py | No | War score impact of cavalry charges untested |

### Highest-Priority Test Proposals

1. **Stale proposal acceptance** — Accept AI peace proposal after coalition declares war. Verify WAR→PEACE is blocked.
2. **Coordinated battle war score** — Run coordinated multi-marshal battle, verify casualties appear in war_scores.
3. **Vassal loyalty from battles** — Win a battle, advance turn, verify vassal loyalty increases (currently dead code).
4. **War score sign for Austria** — Calculate war score for France vs Austria, verify sign is correct from France's perspective in all 4 locations.
5. **Territory sweetener inflation** — AI counter-offer with territory, verify `max(5,...)` doesn't inflate 1→5 regions.

---

## Pass 6: Serialization & Dead Code

### Serialization Gaps

| Field | In __init__ | In to_dict | In from_dict | Status |
|-------|-------------|------------|--------------|--------|
| `ai_stalemate_counters` | Yes (L420) | Yes (L2899) | Yes (L3111) | OK |
| `ai_proposal_metadata` | Yes (L424) | Yes (L2900) | Yes (L3112) | OK |
| `vassal_release_cooldowns` | Yes (L437) | Yes (L2909) | Yes (L3121) | OK |
| `threat_sources_this_turn` | Yes (L453) | Yes (L2921) | Yes (L3135) | OK |
| `_we_dispatched_thresholds` | **NO** | **NO** | **NO** | **GAP** — lost on save/load, causes duplicate WE dispatches |
| `_relation_deltas_this_turn` | **NO** | **NO** | **NO** | Ephemeral (cleared per turn) — acceptable |
| `_prev_war_exhaustion` | **NO** | **NO** | **NO** | Ephemeral (set per turn) — acceptable |

### [PASS-6] [SERIALIZATION] _we_dispatched_thresholds lost on save/load
- **Severity:** MINOR
- **File:** coalition.py:481, 490, 742
- **Description:** Tracks which WE thresholds (20/40/60/80) have dispatched per nation. Dynamically attached via setattr, not in WorldState __init__/to_dict/from_dict. After save/load, duplicate threshold notifications re-fire.
- **Proposed Fix:** Add to WorldState serialization or accept as soft state.

### Dead Code Found

### [PASS-6] [DEAD-CODE] Entire diplomatic defiance pipeline has no production entry point
- **Severity:** MAJOR
- **File:** diplomatic_defiance.py:31, 90, 132, 165, 287
- **Description:** 5 functions have ZERO production callers:
  - `calculate_diplomatic_defiance_chance()` (line 31)
  - `calculate_diplomatic_defiance_chance_deterministic()` (line 90)
  - `calculate_proposal_harshness()` (line 132)
  - `apply_diplomatic_sabotage()` (line 165)
  - `check_sabotage_discovery_deterministic()` (line 287) — zero refs anywhere
- The defiance chance calculation and sabotage application pipeline is orphaned from production. Only referenced from tests. The downstream functions (confrontation, redemption, objection) DO have production callers, but the entry points are dead.
- **Impact:** Talleyrand sabotage may never actually trigger during gameplay. The feature appears unwired.

### [PASS-6] [DEAD-CODE] diplomacy.py utility functions test-only
- **Severity:** MINOR
- **File:** diplomacy.py:902, 2161, 2219
- **Description:** `modify_nation_authority()`, `get_likelihood_descriptor()`, `get_assessment_text()` — zero production callers, only test callers.

### [PASS-6] [DEAD-CODE] vassal.py get_vassal_warnings unused
- **Severity:** MINOR
- **File:** vassal.py:762
- **Description:** Intended for dispatch/notification integration that was never wired.

---

## Pass 7: Architecture Review

### Top 10 Longest Functions

| Lines | Function | File | Assessment |
|------:|----------|------|------------|
| 1762 | `_execute_attack` | executor.py:3419 | **URGENT split** — 8+ distinct phases (combat init, coalition, borders, coordination, retreat, resolution, diplo recording, cascade) |
| 1100 | `execute` | executor.py:1377 | Giant router — dispatch table pattern would help |
| 1066 | `_process_dialogue_choice` | executor.py:11950 | Each dialogue type could be separate handler |
| 867 | `_execute_debug` | executor.py:8957 | Could be separate module |
| 786 | `_execute_strategic_command` | executor.py:5528 | Complex but cohesive |
| 540 | `execute_command` | main.py:475 | Main POST handler, many branches |
| 491 | `_actions_match` | executor.py:1986 | Action validation |
| 480 | `_process_tactical_states` | world_state.py:4562 | Many independent per-turn steps |
| 424 | `WorldState.__init__` | world_state.py:75 | Large but necessary |
| 394 | `handle_objection_response` | executor.py:13360 | Could be split by objection type |

### Code Duplication

| Pattern | Instances | Impact |
|---------|-----------|--------|
| `_make_diplo_key` / `_get_diplo_key` | 2 definitions, 68 call sites | Should be one shared utility |
| War score sign-flip logic | 5 manual flip sites (only 1 uses `get_war_score_for()`) | Fragile convention, 4 bugs found |
| `max_cede` threshold | 2 identical lines (executor.py:12332, diplomatic_templates.py:1505) | Minor duplication |
| `getattr(world, 'player_nation', 'France')` | 40 unnecessary calls (field always initialized) | Noise, not a bug |

### Import Architecture

- **80+ inside-function imports** across the backend — working but tangled
- **Mutual dependencies:** diplomacy↔coalition (6 deferred imports), diplomacy↔vassal (6 deferred imports)
- **executor.py → diplomacy.py:** 23 deferred imports (one-way but excessive)
- **Root cause:** diplomacy, coalition, vassal are mutually dependent systems. A shared `diplomacy_common.py` for constants and pure functions would eliminate most deferred imports.

---

## Cumulative Summary

### Total Findings by Pass

| Pass | Focus | New Findings | CRITICAL | MAJOR | MINOR |
|------|-------|-------------|----------|-------|-------|
| 1 | Verify existing | 11 | 8 | 3 | 0 |
| 2 | Line-by-line review | 36 | 0 | 14 | 22 |
| 3 | Data flow tracing | 16 | 2 | 8 | 6 |
| 4 | Edge cases + consistency | 12 | 2 | 2 | 8 |
| 5 | Test gaps | 10 gaps | — | — | — |
| 6 | Serialization + dead code | 5 | 0 | 1 | 4 |
| 7 | Architecture | 6 patterns | — | — | — |
| **Total** | | **~96** | **12** | **28** | **40** |

---

## Pass 9: Deep Dives on Top Findings

### [PASS-9] [DEFIANCE] Talleyrand Sabotage Pipeline — CONFIRMED UNWIRED
- **Severity:** MAJOR (feature gap, not crash bug)
- **Files:** diplomatic_defiance.py, executor.py (~line 12032, ~12798)
- **Description:** The sabotage system is HALF-BUILT. The downstream pipeline (discovery, confrontation, redemption) is fully wired. But the **entry point** — where sabotage actually triggers — is never called.
  - **Expected flow:** Player sends proposal → defiance chance calculated → if sabotage rolls, proposal modified in transit → discovery check each turn → confrontation
  - **What's missing:** In executor.py at both proposal-sending locations (lines ~12032 and ~12798), code goes straight from DP deduction to setting `proposal_in_transit` with the ORIGINAL proposal. No call to `calculate_diplomatic_defiance_chance()` or `apply_diplomatic_sabotage()`.
  - **Infrastructure that works but never triggers:** `world.pending_talleyrand_sabotage` field (serialized, tick-processed), `world.talleyrand_defiance_cooldown` (serialized, decremented), `check_sabotage_discovery()` (called in dispatch.py:721 but input always None)
  - **Pre-proposal objection IS wired** — Talleyrand warns BEFORE sending. But post-send sabotage is dead.
- **Proposed Fix:** Add defiance chance roll and sabotage application between DP deduction and `proposal_in_transit` assignment at both sending sites in executor.py.

### [PASS-9] [VASSAL] _ratify_treaty VASSAL gap — CONFIRMED CRITICAL with full impact analysis
- **Severity:** CRITICAL
- **File:** world_state.py:4144-4410, vassal.py:50-119
- **Description:** Vassalage IS player-proposable from OPEN_BORDERS, NON_AGGRESSION, and DEFENSIVE_ALLIANCE states (diplomacy.py lines 2542, 2566, 2590). When target accepts, `_ratify_treaty()` sets diplomatic state to "VASSAL" but never calls `create_vassal_treaty()`. Result: **Ghost vassal state** — diplomatic state says VASSAL but entire vassal subsystem is unaware.
- **What's missing vs. create_vassal_treaty:**
  1. `world.vassals[nation]` dict (loyalty, autonomy, tribute_rate, regions) — never created
  2. Coalition threat +5 — never applied
  3. `_reconcile_vassal_diplomacy()` — never called (conflicting alliances persist)
  4. Dispatch event — never queued
  5. Release cooldown check — never verified
  6. Marshal assimilation — never triggered
- **Gameplay impact:**
  - No tribute income from treaty vassals
  - No loyalty tracking, no rebellion, no investment options
  - Diplomacy wizard shows foreign affairs (not vassal management) for the "vassal"
  - Other nations' alliances with the vassal remain active (should be dissolved)
- **Proposed Fix:** In `_ratify_treaty()`, when target_state == "VASSAL", call `create_vassal_treaty(world, target_nation, proposer_nation)` and `assimilate_vassal_marshals(world, target_nation)`.

### [PASS-9] [BATTLE] Coordinated battle casualty key mismatch — CONFIRMED with exact fix
- **Severity:** CRITICAL
- **File:** executor.py:4420-4546 (coordinated path), executor.py:4706-4707 (diplo recording)
- **Description:** When `is_coordinated_battle=True`, `resolve_battle()` is called with `apply_casualties=False`. The deferred result dict uses keys `attacker_raw_casualties`/`defender_raw_casualties` (combat.py:1174-1175). After `_distribute_casualties()` splits the totals, no one sets top-level `attacker_casualties`/`defender_casualties` on the result dict. At line 4706-4707, `record_diplo_battle` reads `.get("attacker_casualties", 0)` → gets 0.
- **Note:** The `outcome` key IS present (combat.py:1122), so the battle IS recorded for diplomacy — just with 0 casualties. This means it never passes the 1000-casualty threshold in `record_battle()` and is invisible to war score.
- **Exact fix location:** After line 4546 (distribution block), add:
  ```python
  battle_result["attacker_casualties"] = int(battle_result["attacker_raw_casualties"])
  battle_result["defender_casualties"] = int(battle_result["defender_raw_casualties"])
  ```

---

## Pass 10: Spec Compliance (DIPLOMACY_SPEC vs Implementation)

### [PASS-10] [SPEC] SWEETENER_CAP: Spec says 40, code says 60
- **Severity:** MAJOR (formula divergence)
- **File:** diplomacy.py:221 vs DIPLOMACY_SPEC.md line 934
- **Description:** Spec R146 says "+40 maximum" sweetener cap. Code: `SWEETENER_CAP = 60` with comment "R146: was 30, raised to 60". Either code was buffed beyond spec or spec was not updated.
- **Impact:** Sweeteners can contribute up to 60 points to acceptance instead of the spec's 40, making generous offers more powerful than designed.

### [PASS-10] [SPEC] AP per turn sweetener: Spec says +8, code says +18
- **Severity:** MAJOR (formula divergence)
- **File:** diplomacy.py:215 vs DIPLOMACY_SPEC.md line 954
- **Description:** Spec: "+8 per AP/turn offered". Code: `"ap_per_turn": 18`. The TALLEYRAND_SMART_SUGGESTIONS_SPEC acknowledges "recently buffed from +8" but DIPLOMACY_SPEC never updated.
- **Impact:** AP sweeteners are 2.25x more powerful than documented.

### [PASS-10] [SPEC] Armistice duration: Spec says 3 turns, code says 5
- **Severity:** MAJOR (gameplay divergence)
- **File:** diplomacy.py:1666 vs DIPLOMACY_SPEC.md lines 695, 1270, 1909
- **Description:** Spec references "3-turn minimum" armistice multiple times. Code: `if turns < 5: continue`. Refinement R5a changed to 5 turns but DIPLOMACY_SPEC still says 3.
- **Impact:** Armistices last 67% longer than documented.

### [PASS-10] [SPEC] Relation modifier peacetime cap: Spec uncapped, code caps at ±30
- **Severity:** MINOR
- **File:** diplomacy.py:598 vs DIPLOMACY_SPEC.md line 918
- **Description:** Spec: `relation / 2` with no cap. Code: `max(-30, min(30, relation / 2))`. For extreme relations (±80+), code is less impactful than spec.

### [PASS-10] [SPEC] Diplomat skill bonus: Spec uncapped, code floors at -8
- **Severity:** MINOR
- **File:** diplomacy.py:675 vs DIPLOMACY_SPEC.md lines 974-980
- **Description:** Spec has no floor. Code floors at `max(-8, ...)`. Asymmetric — positive side uncapped.

### [PASS-10] [SPEC] military_pressure component: Not in spec
- **Severity:** MINOR
- **File:** diplomacy.py:702-707
- **Description:** A third situational component (`min(15, war_score * 0.15)`) competes with military_supremacy and battlefield_diplomacy via `max()`. Added by R8 but never documented in DIPLOMACY_SPEC.

### [PASS-10] [SPEC] Armistice cooldown blocks war declaration (not just re-armistice)
- **Severity:** MINOR
- **File:** diplomacy.py:934-940 vs DIPLOMACY_SPEC.md §5b.2
- **Description:** Spec says cooldown prevents "another armistice" during cooldown period. Code (R99) blocks war DECLARATION during cooldown too. If armistice expired to PEACE, player can't re-declare war for cooldown duration.

### [PASS-10] [SPEC] Defensive alliance base disposition (25): Not in spec
- **Severity:** MINOR
- **File:** diplomacy.py:111
- **Description:** Code defines `"defensive_alliance": 25` base disposition. DIPLOMACY_SPEC's base disposition table has no defensive_alliance entry.

### [PASS-10] [SPEC] Worked example wrong after R141 wartime dampening
- **Severity:** MINOR (documentation only)
- **File:** DIPLOMACY_SPEC.md lines 1001-1014
- **Description:** Example uses `relation / 2 = -30` but R141 changed WAR relation formula to `relation / 4` capped at ±10. Example should show -10 instead of -30.

---

## Pass 11: Godot Popup Field Audit

### [PASS-11] [GODOT] diplomatic_objection_popup field mismatch (war/ultimatum objections)
- **Severity:** MAJOR (confirmed from Pass 3 with full field comparison)
- **Files:** executor.py:11628-11636 and :11697-11705 vs talleyrand_objection_popup.gd:36-39
- **Description:** Two creation sites for this popup:
  - **diplomatic_dialogue.py** (proposal objections) — CORRECT: uses `concern_level`, `objection_text`, `defiance_risk`, `proposal_summary`
  - **executor.py** (war/ultimatum objections) — WRONG: uses `severity`, `message`, `type`, `action`

  Godot expects: `concern_level`, `objection_text`, `defiance_risk`, `proposal_summary`

  | Godot reads | executor.py sets | Result |
  |-------------|-----------------|--------|
  | `concern_level` | `severity` | Falls back to "MODERATE" (should be "STRONG") |
  | `objection_text` | `message` | Falls back to "Sire, I have concerns." |
  | `defiance_risk` | (missing) | Falls back to "Medium" |
  | `proposal_summary` | (missing) | Falls back to "" |

- **Other 5 popup types all MATCH perfectly** — coalition, incoming_proposal, vassal_rebellion, sabotage_discovery, talleyrand_redemption.

### [PASS-11] [GODOT] Non-command Godot handlers ignore popup passthrough data
- **Severity:** MAJOR
- **Files:** main.gd response handlers for objection, capture, redemption, glorious charge, strategic response
- **Description:** Backend correctly includes all 7 popup fields via `_include_popup_passthroughs()` in ALL POST endpoints. But Godot handlers for non-command endpoints do NOT check for these fields:
  - `_on_objection_response` — only checks `redemption_event` and `pending_interrupt`
  - `_on_capture_choice_response` — no popup processing
  - `_on_redemption_response` — no popup processing
  - `_on_glorious_charge_response` — no popup processing
  - `_on_interrupt_response` — no popup processing

  If a diplomatic popup fires during any of these resolution flows, the popup data is returned by backend but **silently ignored by Godot**.

### [PASS-11] [GODOT] Diplomatic top-bar fields missing from all non-command endpoints
- **Severity:** MINOR (Godot handlers don't read them anyway)
- **File:** main.py (all non-/command POST endpoints)
- **Description:** `diplomatic_points`, `max_diplomatic_points`, `threat_level`, `talleyrand_mission_summary`, `coalition_brewing`, `pending_envoy_count` are only included in `/command` responses. After actions that change DP/threat (objection → war declaration → +20 threat, -1 DP), top bar stays stale until next typed command.

---

## Pass 12: Treaty Processing Deep Dive

### [PASS-12] [TREATY] ap_per_turn clause cumulatively destroys nation actions
- **Severity:** MAJOR
- **File:** world_state.py:4467-4472
- **Description:** `_process_treaty_clauses()` reduces `self.nation_actions[from_nation]` each turn, but `nation_actions` is NEVER reset during `_advance_turn_internal()`. A 1 AP/turn clause drains a 4-AP nation to 1 AP after 3 turns and it stays at 1 forever (even after treaty breaks). The clause intends to cap AP, not drain cumulatively.
- **Evidence:** `self.nation_actions[from_nation] = max(1, current_actions - int(amount))`
- **Proposed Fix:** Store base nation_actions values and re-apply AP penalties from active treaties each turn, or reset before applying clauses.
- **Test Coverage:** No

### [PASS-12] [TREATY] Counter-offer Talleyrand state overridden by mission restore
- **Severity:** MAJOR
- **File:** world_state.py:4102 vs 4133-4137
- **Description:** When counter-offer generated, line 4102 sets `talleyrand_state = "IDLE"` so player can respond. But unconditional "Restore Talleyrand state" block at lines 4133-4137 runs for ALL outcomes including COUNTER_OFFER, overriding IDLE back to ON_MISSION if active_diplomatic_mission exists. Player's counter-offer response is then blocked by "Talleyrand is on a mission" guard.
- **Proposed Fix:** Skip Talleyrand restore block when outcome is COUNTER_OFFER and counter_terms exist.
- **Test Coverage:** No

### [PASS-12] [TREATY] Auto-downgrade doesn't remove active treaty — per-turn clauses keep running
- **Severity:** MAJOR (expanded from Pass 2 finding)
- **File:** diplomacy.py check_auto_downgrade() + world_state.py _process_treaty_clauses()
- **Description:** When auto-downgrade transitions ALLIANCE→NON_AGGRESSION, the ALLIANCE treaty stays in `active_treaties` with its gold_per_turn and ap_per_turn clauses continuing to execute every turn. Compare with break_treaty() and declare_war() which both call `active_treaties.pop()`.
- **Impact:** Gold/AP transfers from a downgraded treaty continue indefinitely.
- **Test Coverage:** No

### [PASS-12] [TREATY] Armistice expiration to WAR doesn't remove active treaty
- **Severity:** MAJOR
- **File:** diplomacy.py:1685-1696
- **Description:** When armistice expires back to WAR (relations < -60), `diplomatic_states[diplo_key] = "WAR"` is set but armistice treaty stays in `active_treaties`. Armistice reparation clauses continue running during renewed war.
- **Test Coverage:** No

### [PASS-12] [TREATY] Free gold creation when from_nation not in nation_gold
- **Severity:** MINOR
- **File:** world_state.py:4454-4455
- **Description:** In `_process_treaty_clauses()`, if `from_nation` not in `nation_gold` (eliminated nation), `elif` still credits `to_nation` with full amount. Gold created from nothing.
- **Test Coverage:** No

### [PASS-12] [TREATY] Negative amount in treaty clause reverses transfer direction
- **Severity:** MINOR
- **File:** world_state.py:4245, 4257, 4433
- **Description:** `int(s.get("value", 0))` stored as `amount` with no `abs()` or `max(0,...)` guard. Negative value reverses from/to direction.
- **Test Coverage:** No

---

## Pass 13: Fog of War Leaks

### [PASS-13] [FOG] Coalition member treasury gold exposed in Morning Dispatch
- **Severity:** MAJOR
- **File:** dispatch.py:855
- **Description:** `_build_coalition_section()` exposes `int(world.nation_gold.get(member, 0))` for coalition members. Enemy treasury should NEVER be visible — no visibility tier in the spec supports showing national gold. Player gets perfect knowledge of enemy finances for timing attacks/proposals.
- **Proposed Fix:** Remove gold field entirely from coalition dispatch section.
- **Test Coverage:** No

### [PASS-13] [FOG] Coalition member exact troop strength in Morning Dispatch
- **Severity:** MAJOR
- **File:** dispatch.py:854
- **Description:** `_build_coalition_section()` sums exact marshal strengths with no fog filtering. Should use `_format_army_strength` with visibility bands like war_status.py and diplomatic_ledger.py do.
- **Proposed Fix:** Import and use fog-filtered strength display.
- **Test Coverage:** No

### [PASS-13] [FOG] Coalition member war exhaustion in dispatch + diplomatic_ledger (no PARTIAL+ check)
- **Severity:** MINOR
- **File:** dispatch.py:853, diplomatic_ledger.py:440-452
- **Description:** War exhaustion shown for coalition members without PARTIAL+ visibility check. war_status.py correctly gates WE behind PARTIAL+. Inconsistency.
- **Proposed Fix:** Add same PARTIAL+ check.
- **Test Coverage:** No

### Fog Areas That Passed Clean
- diplomatic_ledger.py Nations tab — correctly filtered
- war_status.py — all data gated by visibility
- intel_report.py — properly filtered
- main.py game_state_summary — correctly filtered
- main.py enemy phase — correctly redacted
- diplomacy.py formulas — backend mechanics, not exposed to player

---

## Pass 14: Save/Load Round-Trip Audit

**Result: CLEAN — no fields lost on save/load.**

All 100+ public `__init__` fields on WorldState are in both `to_dict()` and `from_dict()`. All diplomacy fields (proposal_in_transit, pending_diplomatic_dialogue, talleyrand_state, all popup fields, war_scores, diplomatic_states, active_treaties, etc.) survive round-trip. All `from_dict()` calls use `.get(key, default)` for backward compatibility.

Two minor serialization enforcement gaps:
- `DiplomaticRepresentative` not in `SERIALIZABLE_CLASSES` test — new fields on diplomats wouldn't be caught
- `NotificationCollector` not in `SERIALIZABLE_CLASSES` test — same gap

The `_we_dispatched_thresholds` field (identified in Pass 6) remains the only field lost on save/load (dynamically attached, never in __init__/to_dict/from_dict).

---

## Pass 15: Enemy AI Diplomatic Decisions

### [PASS-15] [AI] _find_ally_support_opportunity counts non-enemies as threats
- **Severity:** MAJOR
- **File:** enemy_ai.py:2788-2793, 2796-2801, 2849-2854, 2885-2890
- **Description:** Function identifies threats to allies by checking `m.nation != nation and m.strength > 0` but omits `world.is_at_war(nation, m.nation)`. Nations at PEACE or ARMISTICE are counted as "enemies" threatening allies. AI wastes actions rushing to support against non-threats. Could generate attack action against peaceful nation (executor rejects but AP wasted).
- **Evidence:** Compare with `_find_defensive_reinforcement_position` (lines 4234-4242) which correctly includes `is_at_war`.
- **Proposed Fix:** Add `and world.is_at_war(nation, m.nation)` to four enemy-filtering comprehensions.
- **Test Coverage:** No

### [PASS-15] [AI] Vassal courting runs for eliminated nations
- **Severity:** MINOR
- **File:** turn_manager.py:293, vassal.py:905
- **Description:** Vassal courting iterates all `enemy_nations` without filtering eliminated ones. Unlike `process_diplomatic_phase` which checks `_is_nation_eliminated`, vassal courting does not. An eliminated nation (0 regions, 0 marshals) retains phantom DP and could spend it courting vassals.
- **Proposed Fix:** Add `_is_nation_eliminated` check before vassal courting loop.
- **Test Coverage:** No

### Areas That Passed Clean
- Enemy AI correctly uses `is_at_war` for all P4/P5 attack targeting
- Coalition target filtering works correctly (P4 lines 2124-2147)
- AI proposals cost 0 DP by spec design — properly gated
- Fog of war correctly not applied to AI (by design)
- Armistice cooldowns enforced through diplomacy.py
- Vassal territory handled via `is_at_war` correctly

---

## Pass 16: Mock Parser & Validation Audit

### [PASS-16] [PARSER] release_vassal missing from VALID_ACTIONS
- **Severity:** MAJOR
- **File:** validation.py:21-66, parser.py:44-81
- **Description:** `release_vassal` is handled by executor (line 2271) and mock parser (llm_client.py:778), but is NOT in VALID_ACTIONS or parser.py valid_actions. If real LLM returns "release_vassal", validation rejects it. Mock parser bypasses validation, so this works in mock mode by accident.
- **Proposed Fix:** Add `"release_vassal"` to VALID_ACTIONS and parser.py valid_actions.
- **Test Coverage:** No

### Parser areas that passed clean:
- Keyword ordering correct ("build " before "train", "charge" before "attack", "unfortify" before "fortify")
- All diplomatic actions parse correctly
- No None/crash-prone paths found
- Fuzzy matching handles edge cases safely

---

## Pass 17: Notification System Completeness

### [PASS-17] [NOTIFICATIONS] Armistice expiration has NO notification or dispatch
- **Severity:** MAJOR
- **File:** diplomacy.py:1644-1702
- **Description:** When armistice expires after 5 turns, two things can happen: (a) peace declared, (b) war resumes. NEITHER creates a notification or dispatch event. War can resume silently without the player knowing.
- **Proposed Fix:** Add `notifications.add()` and `queue_dispatch_event()` for both armistice_expired_peace and armistice_expired_war.
- **Test Coverage:** No

### [PASS-17] [NOTIFICATIONS] Marshal army destroyed has no persistent notification
- **Severity:** MINOR
- **File:** combat.py:940-945, executor.py:4710-4714
- **Description:** When a marshal's army is destroyed (especially during enemy phase), only inline battle report text is shown. No persistent notification. Player could miss annihilation of their marshal by clicking through enemy phase.
- **Test Coverage:** No

### [PASS-17] [NOTIFICATIONS] Vassal release has no notification or dispatch
- **Severity:** MINOR
- **File:** vassal.py:802-855
- **Description:** Player-initiated action, so less likely to be missed, but no persistent record of the release event.
- **Test Coverage:** No

### Notification areas that passed clean:
- Vassal rebellion: fully covered (notification + dispatch)
- Treaty break: fully covered
- Auto-downgrade: notification + dispatch (warning event lacks notification but is low priority)
- Coalition dissolution: fully covered
- War declaration: fully covered
- Alliance cascade: fully covered
- Treaty signing: fully covered

---

## Pass 18: Comprehensive War Score Sign Bug Search

**Result: CONFIRMED — exactly 4 broken locations, no additional ones found.**

All `war_scores` raw dict accesses across the entire backend have been checked. The 4 previously identified locations (diplomacy.py:2681, diplomatic_dialogue.py:355, diplomatic_dialogue.py:825, diplomatic_templates.py:1159) are the COMPLETE set of sign bugs.

All other war_score access points either use `get_war_score_for()` (15+ locations), `calculate_war_score()` directly (3 locations), manual sign-flip (5 locations, all correct), or operate symmetrically (decay, serialization).

---

## Pass 19: Diplomatic Dialogue State Machine

### [PASS-19] [DIALOGUE] Vassalage DP cost shown as 1 instead of 3
- **Severity:** MAJOR
- **File:** diplomatic_dialogue.py:473, diplomacy.py:880
- **Description:** `dp_action = f"propose_{proposal_type}"` produces `"propose_vassalage"`, but `base_costs` in diplomacy.py uses `"demand_vassalage": 3`. Since `propose_vassalage` is not in base_costs, `get_dp_cost` falls back to default 1. Player sees "1 DP" but vassalage should cost 3. Same bug at executor.py:12008 — actual cost charged is also wrong.
- **Proposed Fix:** Add `"propose_vassalage": 3` to base_costs, or map `vassalage` → `demand_vassalage` before key construction.
- **Test Coverage:** No

### [PASS-19] [DIALOGUE] Executor _state_map missing vassalage→VASSAL mapping
- **Severity:** MAJOR
- **File:** executor.py:12010-12011
- **Description:** `_state_map` in proposal handler lacks `"vassalage": "VASSAL"`. When `proposal_type == "vassalage"`, `.get("vassalage", "PEACE")` returns "PEACE". Then `get_transition_dp_cost(current_diplo, "PEACE")` computes wrong jump cost.
- **Proposed Fix:** Add `"vassalage": "VASSAL"` to _state_map.
- **Test Coverage:** No

### [PASS-19] [DIALOGUE] _base_descriptions missing armistice_stalemate variant
- **Severity:** MINOR
- **File:** diplomatic_dialogue.py:489-499
- **Description:** `_base_descriptions` has `armistice`, `armistice_losing`, `armistice_winning` but not `armistice_stalemate`. Fallback produces "Armistice Stalemate" instead of expected description.
- **Test Coverage:** No

### [PASS-19] [DIALOGUE] Raw internal proposal type in objection popup summary
- **Severity:** MINOR
- **File:** diplomatic_dialogue.py:615
- **Description:** `proposal_summary = f"{proposal.get('type', 'unknown')} with ..."` shows raw type (e.g., "non_aggression") instead of display name. `_display_proposal_type()` function exists for this.
- **Test Coverage:** No

---

## Pass 20: Strategic Orders + Diplomacy Interaction

### [PASS-20] [MOVEMENT] Engagement check treats allied marshals as enemies
- **Severity:** MAJOR
- **File:** executor.py:6749 and 6768
- **Description:** `_execute_move()` engagement check uses `m.nation != marshal.nation` without `is_at_war()` check. Allied/neutral marshals sharing a region block movement as if they were enemies. A French marshal with an allied Bavarian marshal in the same region would be "engaged" and unable to move.
- **Evidence:**
  ```python
  # Line 6749 — WRONG
  enemies_here = [m for m in marshals_here if m.nation != marshal.nation]
  # Should be:
  enemies_here = [m for m in marshals_here if m.nation != marshal.nation and world.is_at_war(marshal.nation, m.nation)]
  ```
  Same issue at line 6768 for destination engagement.
- **Proposed Fix:** Add `and world.is_at_war(marshal.nation, m.nation)` to both filters.
- **Test Coverage:** No

### [PASS-20] [STRATEGIC] Armistice expiration timing gap with strategic orders
- **Severity:** MINOR
- **File:** turn_manager.py:154-165
- **Description:** Strategic orders execute at step 3 (line 154-156), but armistice expirations happen inside `advance_turn()` at step 4 (line 165). A PURSUE could execute one final attack against a nation that just transitioned to PEACE, or a MOVE_TO could cross territory of a nation that just returned to WAR.
- **Test Coverage:** No

### Strategic areas that passed clean:
- PURSUE auto-cancels when target nation signs peace (cleanup_war_end handles it)
- SUPPORT gracefully handles destroyed target marshal
- AP costs properly skipped via `_strategic_execution` flag
- Marshal destruction cleanup correct (strategic.py:88-91)

---

## Pass 21: Manpower & Recruitment

### [PASS-21] [MANPOWER] nation_manpower is undefined — manpower treaty clauses crash
- **Severity:** CRITICAL
- **File:** world_state.py:4456-4466
- **Description:** `manpower_per_turn` treaty clause handler references `self.nation_manpower` which DOES NOT EXIST on WorldState. Actual pools are `self.manpower_pools`. Any treaty with a manpower_per_turn clause will raise `AttributeError: 'WorldState' object has no attribute 'nation_manpower'`. Latent crash if no such treaty exists yet.
- **Evidence:** Lines 4458-4465 all reference `self.nation_manpower.get(...)` — should be `self.manpower_pools.get(...)`
- **Proposed Fix:** Replace all `self.nation_manpower` with `self.manpower_pools`.
- **Test Coverage:** No

### [PASS-21] [AI] P7 rebuild cost check ignores artillery marshals
- **Severity:** MAJOR
- **File:** enemy_ai.py:4494-4496
- **Description:** P7 low-priority rebuild only checks `cavalry` flag, not `artillery`. Artillery marshals costed at infantry rate (200g) but executor charges 400g. If AI has 200-399g, recruit attempt fails and AP wasted, blocking all subsequent recruits for that cycle.
- **Proposed Fix:** Add artillery check before cavalry: `is_artillery = getattr(rebuild_target, 'artillery', False)`
- **Test Coverage:** No

### Manpower areas that passed clean:
- Pools cannot go negative (hard guard at executor:7937)
- Cavalry/artillery pool types correctly selected
- Bankruptcy check via gold guard (not explicit but effective)
- int() wrapping correct for Godot
- Desertion asymptotically approaches 0, never destroys marshal

---

## Pass 22: Region & Territory System

### [PASS-22] [TERRITORY] Coalition threat uses full clause region count, not actual transfers
- **Severity:** MAJOR
- **File:** world_state.py:4314-4321
- **Description:** territory_cede handler skips invalid/uncontrolled regions with `continue`, but threat calculation uses `len(regions)` (full list). If 3 regions listed but only 1 actually transferred, threat = `8 * 3 = 24` instead of correct `8 * 1 = 8`.
- **Proposed Fix:** Track actually-transferred count and use that for threat math.
- **Test Coverage:** No

### [PASS-22] [TERRITORY] Britain's capital (Netherlands) missing is_capital flag
- **Severity:** MAJOR
- **File:** region.py:347-355, NATION_CAPITALS line 505
- **Description:** `NATION_CAPITALS` maps Britain→Netherlands, but Netherlands has `is_capital: False` in REGIONS_DATA. Result: no starting garrison for Britain's capital, no garrison regeneration, enemy AI never detects Britain losing its capital (checks `region.is_capital`). War score capital component still works (uses NATION_CAPITALS).
- **Proposed Fix:** Set `"is_capital": True` for Netherlands in REGIONS_DATA.
- **Test Coverage:** No

### [PASS-22] [TERRITORY] No guard against ceding capital regions via treaty
- **Severity:** MINOR
- **File:** world_state.py:4303-4313
- **Description:** Treaty territory_cede can transfer a nation's capital. Garrison regen then benefits new owner. No fallback capital mechanic for the now-capitalless nation.
- **Test Coverage:** No

### [PASS-22] [TERRITORY] War damage ignored in manpower regen calculation
- **Severity:** MINOR
- **File:** world_state.py:2366-2395
- **Description:** `get_manpower_regen_rates()` ignores `war_damage` on controlled regions. A devastated region provides full cavalry/artillery regen bonuses. War damage only affects income.
- **Test Coverage:** No

### [PASS-22] [TERRITORY] Treaty cession doesn't clear garrison/buildings
- **Severity:** MINOR
- **File:** world_state.py:4313
- **Description:** Treaty cession sets stability=50 but doesn't clear garrison or buildings. Military capture goes through plunder/secure logic. Ceded regions retain all infrastructure intact for new owner.
- **Test Coverage:** No

---

## Pass 23: Coalition Spec Compliance (COALITION_SPEC.md vs coalition.py)

### [P23-1] Spec Self-Contradiction: Decisive Battle Casualty Threshold
- **Severity:** MINOR (spec-only)
- **Files:** docs/COALITION_SPEC.md §2a (line 56) vs §6b (line 416)
- **Description:** §2a says decisive battle threshold is "total casualties > 10,000" but §6b says "> 5000". Code correctly implements 10,000 (diplomacy.py:1424, executor.py:4959/4983).
- **Impact:** Spec readers get conflicting information. Code is correct.
- **Proposed Fix:** Update §6b line 416 to match §2a: "> 10,000"

### [P23-2] War Exhaustion Per-Turn Rate: Spec Says +5, Code Does +8
- **Severity:** MAJOR
- **Files:** docs/COALITION_SPEC.md §10a (line 635), coalition.py:938
- **Description:** Spec documents "+5 per turn while at war with France" but code applies +8. Changed per R11 in DIPLO_REFINEMENT.md but COALITION_SPEC never updated.
- **Impact:** Coalition members deteriorate 60% faster than documented. Players consulting spec will misjudge timing.
- **Proposed Fix:** Update spec §10a to "+8 per turn" with note "Adjusted per R11 balance pass"

### [P23-3] Missing Coalition Shock Bonus for Defeated Member
- **Severity:** MAJOR
- **Files:** docs/COALITION_SPEC.md §6b (lines 418-419), coalition.py:496-509
- **Description:** Spec says defeated coalition member gets "+15 (standard) + +5 coalition shock bonus". Code's `add_coalition_shock()` explicitly skips the defeated nation (`if member == defeated_nation: continue`). Defeated member gets only casualty-based WE, not the +5 shock.
- **Impact:** Coalition members harder to split diplomatically than intended — missing the +5 psychological shock makes them reach high exhaustion slower.
- **Proposed Fix:** Add +5 to defeated nation in `add_coalition_shock()` before the skip

### [P23-4] Undocumented -2/Turn Coalition Relation Friction
- **Severity:** MAJOR
- **Files:** coalition.py:944-949 (code exists), COALITION_SPEC.md (no mention)
- **Description:** Coalition members' relations with each other decrease by -2 per turn during active coalition war. This affects friction multiplier thresholds (§5c) and wedge diplomacy (§6c). Documented only in DIPLO_REFINEMENT.md R11, not in COALITION_SPEC.
- **Impact:** Significant emergent mechanic invisible to spec readers. Coalition self-destruct timer effectively shorter than documented.
- **Proposed Fix:** Add §3c.5 to COALITION_SPEC documenting the -2/turn inter-member relation decay

### [P23-5] §6b "+15 (standard)" Misleading Phrasing
- **Severity:** MINOR
- **Files:** docs/COALITION_SPEC.md §6b (line 418)
- **Description:** Spec says "+15 (standard)" suggesting fixed value, but actual formula is `casualties // 1000` (variable, capped at +20). The "15" is a worked example (15k casualties), not a constant.
- **Impact:** Spec readers may implement/expect fixed +15 instead of casualty-proportional formula.
- **Proposed Fix:** Rephrase to "+casualties_thousands (e.g., 15k casualties = +15)"

---

## Pass 24: Tactical Triangle Spec Compliance

### [P24-1] Missing "Square Broke Cavalry AND Shelled" Observation
- **Severity:** MAJOR
- **Files:** docs/TACTICAL_TRIANGLE_SPEC.md §187, battle_report.py (missing)
- **Description:** Spec requires observation `square_broke_cavalry_and_shelled` for the Napoleonic dilemma scenario (square successfully repels cavalry, then suffers artillery). No such observation exists in battle_report.py.
- **Impact:** Missing narrative for one of the game's core tactical dilemmas. Square-vs-combined-arms has no flavor text.
- **Proposed Fix:** Add combined observation template and trigger logic to battle_report.py

### [P24-2] Overwatch Observation Wrong Artillery Name in Failure Case
- **Severity:** MAJOR
- **Files:** battle_report.py:695-697
- **Description:** Overwatch observation condition handles two cases: `(we_won and not we_are_attacker)` OR `(we_lost and we_are_attacker)`. Both pass `artillery="our artillery"`. Second case is WRONG — when attacker loses to enemy overwatch, should reference enemy artillery.
- **Impact:** Incorrect flavor text: says "our artillery" when enemy artillery caused the repulse.
- **Proposed Fix:** Pass enemy artillery name when `we_lost and we_are_attacker`

### [P24-3] All Other Tactical Triangle Features Verified CORRECT
- Square +5% defense, cavalry -40%, artillery +50%, bombardment +50%/-15 morale ✓
- Auto-break on all active actions, NOT on form/break/wait/end_turn ✓
- Form square cancels strategic orders, breaks fortify ✓
- Break square free (0 AP), form square 1 AP ✓
- Overwatch cap at 3 = -9%, constraints enforced ✓
- AI P2.5 square logic + anti-oscillation cooldown ✓
- Serialization of square_formation ✓

---

## Pass 25: Godot Script Deep Audit

### [P25-1] Missing active_wars Processing After Diplomatic Popup Early Returns
- **Severity:** CRITICAL
- **Files:** main.gd:760-825 (all diplomatic popup early returns)
- **Description:** When diplomatic popups (coalition_declaration, incoming_proposal, diplomatic_objection, talleyrand_objection, etc.) trigger, function returns BEFORE reaching `_process_active_wars(response)` at ~line 943. War status panel never updates while diplomacy popups are shown.
- **Impact:** User sees stale war data during diplomacy popups. Multiple turns can pass without HUD refresh. War detail popup displays outdated scores/trends.
- **Proposed Fix:** Call `_process_active_wars(response)` before each early return in _on_command_result, or refactor to process it once at the top

### [P25-2] Null Pointer Dereference on Popup Show Without Validation
- **Severity:** CRITICAL
- **Files:** main.gd:773, 795
- **Description:** `coalition_declaration_popup.show_coalition(response.coalition_popup)` and `incoming_proposal_popup.show_proposal(response.incoming_proposal)` — no null check that popup node itself loaded successfully. If scene fails to load (main.gd:256-267), these calls crash.
- **Impact:** Game crash with "Attempt to call function on null" instead of graceful degradation.
- **Proposed Fix:** Add `if popup_node:` guard before all popup.show() calls

### [P25-3] Race Condition With Stale Wizard Responses
- **Severity:** MAJOR
- **Files:** diplomacy_wizard.gd:154-175
- **Description:** If user opens wizard for Nation A, hits back before response, immediately opens for Nation B, Nation A's response can arrive and render briefly before Nation B's data overwrites it.
- **Impact:** Visual flash of wrong nation data, confusing UX.
- **Proposed Fix:** Clear rendered content on new request start, not just on response

### [P25-4] War Detail Popup Silent Closure When War Ends Mid-Read
- **Severity:** MAJOR
- **Files:** main.gd:3015-3016, war_detail_popup.gd:105-106
- **Description:** `refresh_if_open()` searches for current war in updated wars array. If war ended, not found, `found=false`, popup closes while user is reading.
- **Impact:** Popup disappears mid-read with no explanation. Feels like crash.
- **Proposed Fix:** Show "This war has ended" message instead of silently closing

### [P25-5] Float→Int Conversion Missing in War Status/Detail Panels
- **Severity:** MAJOR
- **Files:** war_status_panel.gd:90-111, war_detail_popup.gd:155-159
- **Description:** Duration and war_exhaustion fields from backend might arrive as floats (Python's default). `int(we)` on a string crashes, `int(75.5)` truncates.
- **Impact:** Godot crash on float-to-int conversion or silent truncation.
- **Proposed Fix:** Ensure backend sends all numbers as int() (Golden Rule #2) + add defensive int(float()) on Godot side

### [P25-6] Diplomatic Ledger Threat Tier Color — No Default Case
- **Severity:** MAJOR
- **Files:** diplomatic_ledger.gd:415-424
- **Description:** `match threat_tier:` handles "LOW", "MODERATE", "HIGH", "CRITICAL" but has no default/fallback. Unknown tier (e.g., "MAXIMUM") leaves `tier_color` undefined, injecting empty BBCode `[color=#]`.
- **Impact:** Broken BBCode rendering, uncolored text.
- **Proposed Fix:** Add `_:` default case with neutral color

### [P25-7] Wizard Error State Terminal — Back Button Non-Functional
- **Severity:** MODERATE
- **Files:** diplomacy_wizard.gd:140-152, 111
- **Description:** HTTP failure calls `_show_error()` but `_current_step` stays = 1. Back button checks `if _current_step == 2:` — false, so button does nothing.
- **Impact:** User stuck in error state, must close and reopen wizard.
- **Proposed Fix:** Reset `_current_step` in error handler, or let back button work from step 1

### [P25-8] Diplomatic Ledger Tab Switching With Pending HTTP
- **Severity:** MODERATE
- **Files:** diplomatic_ledger.gd:154-160
- **Description:** Rapid tab switching queues multiple HTTP requests. Each `.request()` cancels previous. If user switches tabs before first response, wrong data briefly renders.
- **Impact:** Brief wrong-data flash on rapid tab switching.

### [P25-9] BBCode Injection Via Dynamic Location Names
- **Severity:** MODERATE
- **Files:** war_detail_popup.gd:166-173
- **Description:** Location names from backend are inserted directly into BBCode without escaping. A location containing "[" or "]" would corrupt BBCode parser.
- **Impact:** Garbled text or blank battle list if location names contain special characters.

### [P25-10] No Global Popup Z-Order Management
- **Severity:** MINOR (architectural)
- **Description:** Each popup uses hardcoded CanvasLayer values (25, 30, 50, 100). No central management. Modal stacking depends on load order, not logical priority.

### [P25-11] Color Constants Duplicated Across 4+ Files
- **Severity:** MINOR
- **Files:** war_status_panel.gd:20-32, war_detail_popup.gd:24-31, diplomacy_wizard.gd:36-47, diplomatic_ledger.gd:26-36
- **Description:** Each file defines own COLOR_GOLD, COLOR_RED, etc. Palette change requires editing 4+ files.

---

## Pass 26: Combat System Edge Cases

### [P26-1] Defense Modifier Applied as Inverted Divisor
- **Severity:** CRITICAL
- **Files:** combat.py:422
- **Description:** `defense_multiplier = (1.0 - defense_bonus) / defender_stance_modifier`. Division by stance modifier INCREASES defense_multiplier instead of decreasing it. Example: defense_skill=10 (bonus=0.5) + defensive stance (1.15) → multiplier = 0.435 instead of intended ~0.24. Defender takes ~95% MORE casualties than intended.
- **Evidence:** Division inverts the modifier logic. Should be multiplication.
- **Impact:** Defensive stance makes defender TAKE MORE damage. Core combat mechanic is inverted.
- **Proposed Fix:** Change to `defense_multiplier = (1.0 - defense_bonus) * (1.0 / defender_stance_modifier)` or restructure formula
- **Test Coverage:** None testing stance + defense interaction specifically

### [P26-2] Shock Multiplier Stacking Uncapped
- **Severity:** MAJOR
- **Files:** combat.py:286-342
- **Description:** Multiple multiplicative stacks without overflow cap: cavalry + recklessness (1.5) × stance (1.15) × terrain (1.2) × counter-artillery (1.30) could reach ~2.8x damage. No explicit cap defined.
- **Impact:** Extreme damage spikes possible in specific compositions. May be intentional but undocumented.
- **Proposed Fix:** Add `shock_multiplier = min(shock_multiplier, 2.5)` cap or document intentional uncapped design

### [P26-3] Casualty Rate 60% Cap Not Enforced in Coordinated Battles
- **Severity:** MAJOR
- **Files:** combat.py:878 (base cap), executor.py:760-820 (distribution)
- **Description:** Base calculation caps casualty_rate at 60%. But `_distribute_casualties()` assigns proportional shares without per-recipient cap. Individual marshals in coordinated battles can lose >60% in single engagement.
- **Impact:** Violates game invariant "max 60% per battle per marshal".
- **Proposed Fix:** Add per-recipient 60% cap in `_distribute_casualties()`

### [P26-4] Glorious Charge Can Produce >60% Casualties
- **Severity:** MODERATE
- **Files:** combat.py:447-448
- **Description:** Base casualties capped at 60%, then glorious charge multiplies by 2. Result can be 120% — effectively army destruction guaranteed.
- **Impact:** May be intentional (high-risk charge) but breaches stated 60% cap. At minimum needs documentation.

### [P26-5] Deferred Result Dict Key Mismatch: raw_outcome vs outcome
- **Severity:** MAJOR
- **Files:** combat.py:1000-1080 (returns `raw_outcome`), executor.py:4437 (reads `raw_outcome`)
- **Description:** Deferred path returns `raw_outcome`, normal path returns `outcome`. If refactored to use same code path, KeyError occurs.
- **Impact:** Fragile to refactoring. Code works now but naming inconsistency is a maintenance hazard.

### [P26-6] Attacker/Defender Defense Calculation Asymmetry
- **Severity:** MODERATE
- **Files:** combat.py:427 vs 422
- **Description:** Attacker casualty reduction: `1.0 - (attacker_defense / 20.0)` (direct, no stance). Defender: `(1.0 - defense_bonus) / stance_modifier` (includes stance, inverted per P26-1). Same defense value protects differently for attacker vs defender.
- **Impact:** Unintended asymmetric survivability, compounded by P26-1 division bug.

### [P26-7] Fort Degradation Timing Discrepancy in Deferred Path
- **Severity:** MODERATE
- **Files:** combat.py:199-210 (snapshot before battle), 1051-1067 (deferred path degrades after)
- **Description:** Battle report snapshots modifiers BEFORE resolution, but deferred path degrades fort AFTER snapshot. Report shows undegraded fort value.
- **Impact:** Minor — report cosmetic only. Code comment acknowledges this as expected (line 1001).

### [P26-8] Engagement Check Treats Allies as Enemies
- **Severity:** MODERATE (already in base audit, confirmed)
- **Files:** executor.py:6768
- **Description:** `enemies_at_dest = [m for m in marshals_at_dest if m.nation != marshal.nation]` — blocks MOVE for any non-nation marshal, regardless of alliance status.
- **Impact:** Allied marshals block movement. Previously noted in base audit.

---

## Pass 27: Fog of War Spec Compliance

### [P27-1] Strength Band Display Names: "force" vs "army"
- **Severity:** MINOR (documentation)
- **Files:** docs/FOG_OF_WAR_SPEC.md §2.1, intel.py:42-48
- **Description:** Spec says "a substantial army" / "a large army" / "a massive army". Code uses "substantial force" / "large force" / "massive force". Consistent throughout codebase but diverges from spec wording.
- **Impact:** Documentation-only. No functional bug.

### [P27-2] All Other Fog Rules Verified CORRECT
- 24 fog mechanics checked. All implemented correctly including:
  - Visibility levels (FULL, PARTIAL, STALE, LAST_KNOWN, UNKNOWN) ✓
  - Intel decay (FULL→STALE→LAST_KNOWN at 2, 3-4, 5+ turns) ✓
  - Scout persistence, watchtower synergy ✓
  - PURSUE/SUPPORT fog validation ✓
  - Enemy phase filtering ✓
  - Campaign log fog filtering ✓
  - Diplomatic ledger fog-aware strength ✓
  - AI omniscience (correct — AI sees all, players don't) ✓

---

## Pass 28: V2B Defiance Spec Compliance

### [P28-1] Vindication Decay Interval: Spec Says 3 Turns, Code Uses 5
- **Severity:** MAJOR
- **Files:** docs/V2B_DEFIANCE_SPEC.md §2 (line 158), world_state.py:5060, vindication.py:248
- **Description:** Spec says "-1 per 3 turns of no objection activity". Both world_state.py and vindication.py use 5-turn interval.
- **Impact:** Vindication decays ~40% slower than designed. Score of +3 takes 15 turns to decay instead of 9.
- **Proposed Fix:** Change `turns_idle >= 5` to `turns_idle >= 3` in both files

### [P28-2] Dual Vindication Decay Methods — Potential Double-Fire
- **Severity:** MAJOR
- **Files:** world_state.py:5042-5076, vindication.py:227-253
- **Description:** Both files have vindication decay methods with identical logic. If both called during turn processing, vindication decays twice per cycle. `vindication.py:apply_decay()` appears to have no production callers.
- **Impact:** If both fire, vindication decays at double rate. Currently only world_state version runs.
- **Proposed Fix:** Remove `vindication.py:apply_decay()` or verify it's never called

### [P28-3] Defensive Vindication — 40% Implemented
- **Severity:** MAJOR
- **Files:** vindication.py (pending_defensive_vindication scaffold), world_state.py:5068-5076 (staleness clearing)
- **Description:** Spec §2.3 defines complete defensive vindication system: creation on "trust" choice, resolution on enemy attack, staleness clearing. Only staleness clearing is implemented. Creation trigger and resolution wiring are missing.
- **Impact:** Defensive vindication entries are cleared as stale but never created. Feature is dead code.

### [P28-4] Missing Fog-of-War Migration for Objection Helpers
- **Severity:** MINOR
- **Files:** objection_v2.py (helpers), V2B_DEFIANCE_SPEC.md §4
- **Description:** Spec §4 says 8+ objection_v2.py helpers should use fog-filtered data. Not implemented — helpers still use raw world.marshals access.
- **Impact:** Objections fire based on omniscient information rather than fog-filtered view. Design intent is foggy objections.

### [P28-5] Missing Relationship-Based SUPPORT Objection
- **Severity:** MINOR
- **Files:** objection_v2.py, strategic.py, V2B_DEFIANCE_SPEC.md §5
- **Description:** Spec says hostile/rival relationship should trigger SUPPORT objections. Not implemented.
- **Impact:** Marshals never object to supporting rivals — missing personality expression.

### [P28-6] All Other V2b Features Verified CORRECT
- Defiance chance formula (all 3 ConcernLevels + modifiers + 40% hard cap) ✓
- Fallback table (all personalities, artillery routing) ✓
- Defiance success evaluation (battle outcomes, pyrrhic checks) ✓
- Outcome table (right/wrong/inconclusive/failed — trust, vindication, authority, cooldown) ✓
- Authority tracker (10-turn window, 80%/65% thresholds) ✓
- Berthier flavor text (all 8 templates) ✓
- Serialization (all V2b fields) ✓

---

## Pass 29: Save/Load Deep Edge Cases

### [P29-1] Coalition from_dict Uses Shallow Copy vs to_dict's Deep Copy
- **Severity:** MAJOR
- **Files:** world_state.py:2922-2923 (to_dict uses deepcopy), world_state.py:3137-3139 (from_dict uses .copy())
- **Description:** `to_dict()` does `copy.deepcopy(self.active_coalition)` but `from_dict()` does `raw_coalition.copy()`. Coalition dicts contain nested structures (members list, etc.). Shallow copy shares references with source dict.
- **Impact:** Mutating loaded coalition could corrupt original dict. Subtle reference-sharing bugs.
- **Proposed Fix:** Use `copy.deepcopy()` in from_dict() too

### [P29-2] Garrison Detachment Backward-Compat Logic Bug
- **Severity:** MAJOR
- **Files:** region.py:306
- **Description:** `garrison_detachment = data.get("garrison_detachment", False) or data.get("garrison_player_placed", False)`. Uses `or` which returns first truthy value. If both keys exist with conflicting values, old key wins when True regardless of new key's value.
- **Impact:** Save migration may lose data when both old and new field names coexist.
- **Proposed Fix:** Use proper fallback: `data.get("garrison_detachment") if "garrison_detachment" in data else data.get("garrison_player_placed", False)`

### [P29-3] Enum Deserialization Crashes on Corrupt Values
- **Severity:** MODERATE
- **Files:** marshal.py:1246
- **Description:** `marshal.stance = Stance(data.get("stance", "neutral"))` — if save has `"stance": null` or typo like `"cautious"`, Stance() raises ValueError with no try-catch.
- **Impact:** Corrupted save crashes on load instead of graceful fallback.
- **Proposed Fix:** Wrap in try-except, fallback to Stance.NEUTRAL

### [P29-4] world_state from_dict() Missing int() Casts on Numeric Fields
- **Severity:** MODERATE
- **Files:** world_state.py:2961-2962, 2994-2998, 3001, 3040-3052
- **Description:** Fields like `current_turn`, `max_turns`, `max_actions_per_turn` loaded directly from JSON without int() cast. If save has string values (user-edited JSON), these will be strings at runtime.
- **Impact:** Crashes on arithmetic operations with string values. ~30 lines affected.
- **Proposed Fix:** Wrap all numeric from_dict loads with int()

### [P29-5] All Other Save/Load Checks Verified
- Circular references: CLEAN ✓
- New field backward compat (.get with defaults): WELL COVERED ✓
- None vs missing key: MOSTLY CORRECT ✓
- Float defense_bonus: Safe (converted to int before Godot) ✓
- JSON corruption: Caught by json.JSONDecodeError ✓

---

## Pass 30: LLM Integration Audit

### [P30-1] release_vassal Missing from VALID_ACTIONS
- **Severity:** MAJOR
- **Files:** validation.py:21-66, executor.py:14103, llm_client.py:778
- **Description:** `release_vassal` action is implemented in executor and recognized by mock parser, but missing from VALID_ACTIONS set. LLM mode validation rejects it as "Unknown action".
- **Impact:** Real LLM mode cannot execute release_vassal commands.
- **Proposed Fix:** Add `"release_vassal"` to VALID_ACTIONS

### [P30-2] 5 Diplomatic Actions Missing from VALID_ACTIONS
- **Severity:** MAJOR
- **Files:** validation.py:21-66 (missing), executor.py:11194-11458 (implemented), llm_client.py:922-924 (parsed)
- **Description:** `diplomatic_proposal`, `diplomatic_mission`, `diplomatic_feasibility`, `diplomatic_advisory`, `diplomatic_error` — all parsed by mock, executed by executor, but missing from VALID_ACTIONS.
- **Impact:** Real LLM mode rejects all diplomatic commands. Only mock parser works because it bypasses validation.
- **Proposed Fix:** Add all 5 to VALID_ACTIONS

### [P30-3] All Other LLM Checks Verified
- Keyword ordering (build/train, restrain/drill, cancel): ALL CORRECT ✓
- API key handling: SECURE (not logged, BYOK support) ✓
- LLM response injection: SAFE (structured ParseResult, no eval/exec) ✓
- Error handling: EXCELLENT (fallback to mock, graceful degradation) ✓
- Fuzzy matching: SAFE (context-aware thresholds, short name exact match) ✓
- Strategic parser: CORRECT (multi-word first, word boundary regex) ✓
- No retry on rate limit: Intentional design (game asks player to retry) ✓

---

## Pass 31: Multi-Marshal Spec Compliance

### [P31-1] Square Formation Incorrectly Blocks Coordination Bonuses
- **Severity:** MAJOR
- **Files:** executor.py:262, 265, 306
- **Description:** Square-formation marshals are excluded from contributing attack coordination (line 265: `if not is_fortified_non_artillery and not is_in_square`) and from adjacent ally count (line 306: `and not getattr(m, 'square_formation', False)`). MULTI_MARSHAL_SPEC makes NO exception for square formation in coordination or adjacency — only fortified non-artillery is excluded.
- **Impact:** Square-formation marshals lose all coordination bonuses they should provide. Defensive posture incorrectly penalizes allied coordination.
- **Proposed Fix:** Remove `and not is_in_square` from line 265, remove square check from line 306

### [P31-2] All Other Multi-Marshal Features Verified CORRECT
- Combined arms detection (3-type/2-type bonuses, fortified inclusion) ✓
- Per-ally coordination (relationship scaling, base values) ✓
- Dedicated bonus (Path A co-location, Path B SUPPORT, Path B2 arrival) ✓
- Adjacent support (+2% per ally, attack-only) ✓
- Casualty distribution (proportional, artillery 50% reduction) ✓
- Win/Loss relationship formula (severity, ordered pairs, cooldown) ✓
- Reinforcement system (all 11 eligibility rules, Grouchy rule, arrival scoring) ✓
- Transient field cleanup ✓
- Modifier application (single source in marshal.py) ✓
- Serialization (co_location_turns, last_relationship_change_turn) ✓

---

## Pass 32: Vassal System Deep Audit

### [P32-1] Battle Field Mismatch in Vassal Loyalty Calculation
- **Severity:** CRITICAL
- **Files:** vassal.py:262-276
- **Description:** `process_vassal_loyalty()` reads from `world.battles_this_turn` using field names `victor`, `attacker_nation`, `defender_nation` — but `battles_this_turn` has fields `result`, `attacker`, `defender`. All reads return empty strings, so `wins` and `losses` always = 0.
- **Impact:** Lord's battle performance NEVER affects vassal loyalty. The "lord battle" modifier is permanently dead code. (Confirms base audit finding from Pass 3.)
- **Proposed Fix:** Use correct field names from battles_this_turn structure, or use diplomacy.py's battle_records which has correct fields

### [P32-2] Trust Field Encapsulation Violation in Marshal Assimilation
- **Severity:** MAJOR
- **Files:** vassal.py:750
- **Description:** `marshal.trust._value = ASSIMILATION_TRUST` — accesses private field `_value` directly instead of using `marshal.trust.modify()`. Condition checks `hasattr(marshal.trust, 'value')` (public property) but sets private field.
- **Impact:** May work if Trust class uses `_value` internally, but violates encapsulation. Trust change won't trigger any side effects that `modify()` might have.
- **Proposed Fix:** Use `marshal.trust.modify(ASSIMILATION_TRUST - marshal.trust.value)` for relative change

### [P32-3] Release Cooldown Off-By-One (5→4 Turns Actual)
- **Severity:** MAJOR
- **Files:** vassal.py:874-882
- **Description:** Cooldown set to 5 but decrement logic identifies expired BEFORE decrementing: `expired_r = [n for n in release_cds if release_cds[n] <= 1]`. Sequence: 5→4→3→2→1→expired = 4 blocking turns, not 5.
- **Impact:** Treaty re-vassalization possible 1 turn earlier than intended. (Confirms base audit finding.)

### [P32-4] Investment Cooldown Off-By-One (3→2 Turns Actual)
- **Severity:** MAJOR
- **Files:** vassal.py:862-872
- **Description:** Same decrement logic bug as P32-3. INVEST_COOLDOWN = 3 but provides only 2 turns of blocking.
- **Impact:** Players can invest in vassals every 2 turns instead of 3, loyalty recovery faster than designed.
- **Proposed Fix:** Either set cooldowns to N+1, or change expired check to `<= 0` after decrementing

---

## Pass 33: Diplomatic Templates Audit

### [P33-1] Gold Tag Fires When No Gold Sweeteners Offered
- **Severity:** MINOR
- **Files:** diplomatic_templates.py:1404-1405
- **Description:** When `gold_pref == "high"`, `context_tags.append("gold_for_poor")` fires even when there are no gold sweeteners in base terms. Commentary says "even modest gold buys eternal gratitude" but no gold is offered.
- **Impact:** Misleading Talleyrand commentary — player told gold matters when no gold is in the proposal.
- **Proposed Fix:** Guard tag append with `if has_gold_sweetener:`

### [P33-2] Gold Reduction Not Tagged in "Low" Preference Path
- **Severity:** MINOR
- **Files:** diplomatic_templates.py:1418-1420
- **Description:** When `gold_pref == "low"` and gold sweeteners are reduced 50%, no context tag is appended. Commentary falls back to generic neutral deal instead of acknowledging the gold reduction.
- **Impact:** Talleyrand misses opportunity to comment on strategic gold reduction.

### [P33-3] All Other Template Features Verified CORRECT
- All 34 templates (T1-T34) grammar-correct and contextually appropriate ✓
- NATION_DESIRE_PROFILES complete for all 4 nations ✓
- TALLEYRAND_COMMENTARY complete (46 entries with fallback) ✓
- 5-stage pipeline correctly implemented ✓
- Economic feasibility validation (caps, int() forcing) ✓
- Dialogue enrichment wiring ✓
- War score signs correct throughout ✓

---

## Pass 34: Enemy AI Decision Tree Audit

### [P34-1] AI Fog of War Leak — get_enemies_of_nation() Unfiltered
- **Severity:** CRITICAL
- **Files:** enemy_ai.py:1779, 1832, 1957, 2034, 3275
- **Description:** `get_enemies_of_nation()` returns ALL enemies regardless of fog of war visibility. AI uses this for attack targets, threat checks, rescue targets, garrison attacks. AI sees enemies in fogged regions.
- **Impact:** AI cheats by attacking unseen targets, moving toward hidden marshals, discovering positions before scouts. Violates FOG_OF_WAR_SPEC §5.
- **Note:** Per FOG_OF_WAR_SPEC §5.0, "Fog filters information, not mechanics." The spec says "AI sees all" as intentional design. However, `strategic.py` specifically implements fog-aware pathfinding for player vs AI. This suggests TACTICAL fog was intentionally omitted for AI, but target SELECTION should still be fog-filtered for fairness.
- **Proposed Fix:** Create `get_visible_enemies_of_nation()` and use for AI target selection

### [P34-2] All Other AI Features Verified CORRECT
- Priority ordering P1-P8 complete and correctly sequenced ✓
- P1 retreat when broken: handles all broken states ✓
- P2 defensive positioning: terrain awareness, capital defense ✓
- P3 attack opportunities: strength ratio, target selection ✓
- P4 garrison defense: capital garrison logic ✓
- P5 strategic movement: pathfinding, objective selection ✓
- P6 recruitment: manpower awareness, timing ✓
- P7 rebuild: artillery cost issue (already in audit) ✓
- P8 diplomatic AI: proposal generation, acceptance logic ✓
- Building Blocks principle (same executor as player) ✓
- Action economy: respects AP limits, enemy doesn't consume player budget ✓
- Anti-stagnation system ✓
- Attack futility tracker ✓
- Wait spam prevention ✓
- Fortify/unfortify oscillation guard ✓

---

## Pass 35: Notification System Audit

### [P35-1] Three Notification Types Defined But Not Fired
- **Severity:** MINOR
- **Files:** notifications.py:25, 38, 57
- **Description:** STRATEGIC_ORDER_COMPLETE, VASSAL_LOYALTY_CRITICAL, and DEFECTION_CASCADE are defined as notification types but have no fire points in production code. Strategic order completion uses Morning Dispatch instead; vassal loyalty warnings use dispatch triggers; defection cascade not yet implemented.
- **Impact:** Dead constants. No functional impact.

### [P35-2] COALITION_BREWING Not Dismissed When Coalition Disperses
- **Severity:** MINOR
- **Files:** coalition.py (brewing→declared auto-dismisses ✓, but dispersal path missing)
- **Description:** When coalition brewing is cancelled (player improves relations below threshold), stale COALITION_BREWING notification persists. Brewing→declared transition correctly calls `dismiss_by_type(COALITION_BREWING)`, but dispersal doesn't.
- **Impact:** Stale "coalition brewing" notification after threat dissipates.

### [P35-3] Notification Duplication on Double-Click
- **Severity:** MINOR
- **Files:** executor.py (dismiss-before-create pattern)
- **Description:** Actions that dismiss old notifications before creating new ones can create duplicates if the action fires twice (e.g., double-click). Defensive but not idempotent.
- **Impact:** Duplicate notifications in edge cases. Low probability.

### [P35-4] POST /notifications/dismiss Missing World State Guard
- **Severity:** MINOR
- **Files:** main.py:1933-1944
- **Description:** POST dismiss endpoint doesn't check if world state exists before calling `world.notifications.dismiss()`. GET endpoint has this guard, POST doesn't.
- **Impact:** Crash if dismiss called before game starts. Low probability.

---

## Pass 36: Turn Processing Order Audit

### [P36-0] Turn Processing Order Verified CORRECT
- **Description:** Complete 40-step advance_turn sequence reviewed. No dependency violations found. Key correct orderings:
  - Strategic orders execute BEFORE advance_turn (enemy phase timing correct)
  - battles_this_turn cleared AFTER strategic orders consume it
  - Supply attrition and manpower regen operate on different systems (no conflict)
  - Bankruptcy desertion uses PREVIOUS turn counter (correct)
  - Diplomacy processing before income (correct for trade income reflection)
  - Fog of war recalculated LAST (clean player view at turn start)
  - Turn counter increment position is fragile but currently safe across all 35+ checks

---

## Pass 37: Diplomatic State Machine Audit

### [P37-1] break_treaty() Missing WAR/ARMISTICE in post_break_map — No Cleanup
- **Severity:** CRITICAL
- **Files:** diplomacy.py:1945-1955
- **Description:** `post_break_map` has no entries for "WAR" or "ARMISTICE". Both fall through to default "PEACE". But `break_treaty()` doesn't call `cleanup_war_end()` — only `_ratify_treaty()` does. Result: breaking a treaty while in WAR/ARMISTICE transitions to PEACE without clearing battle records, war exhaustion, cascade markers, or strategic orders targeting that nation.
- **Impact:** Orphaned war state data persists. War exhaustion never resets. Cascade markers remain, potentially triggering false cascades later.
- **Proposed Fix:** Add `"WAR": "ARMISTICE"` and `"ARMISTICE": "PEACE"` to post_break_map. Call `cleanup_war_end()` in break_treaty when exiting WAR state.

### [P37-2] VASSAL→PEACE DP Cost Falls Through to Default 1
- **Severity:** MAJOR
- **Files:** diplomacy.py:281-314
- **Description:** `get_transition_dp_cost()` has no explicit case for VASSAL exits. VASSAL→PEACE falls through to default return value of 1 DP. VASSAL creation costs 3 DP but releasing only costs 1 — asymmetric pricing.
- **Impact:** Vassal release significantly cheaper than creation. May be intentional but undocumented.
- **Proposed Fix:** Add explicit VASSAL exit cost or document as intentional

### [P37-3] Armistice Cooldown Only Blocks declare_war, Not Other Transitions
- **Severity:** MAJOR
- **Files:** diplomacy.py:934-940
- **Description:** Armistice cooldown check only blocks `declare_war()`. A player could potentially propose treaty transitions to nations under armistice cooldown through the wizard, bypassing the cooldown spirit.
- **Impact:** Cooldown enforcement incomplete — may allow diplomatic manipulation around armistice windows.
- **Proposed Fix:** Add cooldown check to transition validation or proposal acceptance

### [P37-4] All Other State Machine Transitions Verified
- All 64 state pairs (8×8) checked. Valid transitions:
  - Any→WAR: Always allowed (cost 1 DP)
  - WAR→ARMISTICE→PEACE→OPEN_BORDERS→NON_AGGRESSION→DEFENSIVE_ALLIANCE→ALLIANCE: Upgrade path correct with cumulative DP
  - ALLIANCE→DEFENSIVE_ALLIANCE→NON_AGGRESSION→OPEN_BORDERS→PEACE: Downgrade path correct with penalties
  - 5 states→VASSAL entry, VASSAL→{WAR, PEACE} exit: Correct
  - Auto-downgrade (5-turn relation threshold): Correct for 4 applicable states
  - Post-break map: 6 entries cover all non-WAR treaty states

---

## Pass 38: Manpower/Economy Audit

### [P38-1] nation_manpower Attribute Doesn't Exist — Confirmed CRITICAL
- **Severity:** CRITICAL (confirms P22/deep audit finding)
- **Files:** world_state.py:4458-4466
- **Description:** Treaty clause "manpower_per_turn" references `self.nation_manpower` (5 occurrences) but correct attribute is `self.manpower_pools`. Any treaty with manpower transfer clause crashes with AttributeError.
- **Impact:** Manpower transfer treaties completely non-functional.
- **Proposed Fix:** Replace all 5 occurrences of `self.nation_manpower` with `self.manpower_pools`

### [P38-2] All Other Economy/Manpower Systems Verified CORRECT
- Gold income: All 6 sources (regions, naval, trade, subsidy, treaties, tribute) correct ✓
- Gold expenditure: Recruitment, building, treaties all tracked and int()-wrapped ✓
- Bankruptcy system: Escalation (upkeep halved → warnings → 5% desertion) correct ✓
- Manpower regen rates: Match documented values (5000/500/300 base + territory bonuses) ✓
- Manpower pool caps: Enforced correctly (100k/30k/20k) ✓
- Supply system: Capacity formula and attrition scaling correct ✓
- Trade income: Diminishing returns per partner correct ✓
- AP economy: Base AP, costs, admin AP, diplomatic clauses all correct ✓
- All values to Godot: int()-wrapped throughout ✓

---

## Pass 39: Diplomatic Advisory Audit

### [P39-1] Static KNOWN_NATIONS Used Instead of get_known_nations(world)
- **Severity:** CRITICAL
- **Files:** diplomatic_advisory.py:700
- **Description:** `_get_nation_summary()` loops over hardcoded `KNOWN_NATIONS` set instead of `get_known_nations(world)`. All other functions in the same file (lines 252, 507) correctly use the dynamic version. Vassals and dynamically created nations are excluded from alliance checking.
- **Impact:** Advisory gives incomplete alliance information once vassals exist.
- **Proposed Fix:** Change `for other in KNOWN_NATIONS:` to `for other in get_known_nations(world):`

### [P39-2] Empty threat_entries List Causes IndexError
- **Severity:** MAJOR
- **Files:** diplomatic_advisory.py:282
- **Description:** `top_threat = threat_entries[0]` accessed without checking if list is empty. If `get_known_nations(world)` returns empty set (unlikely but possible during initialization), IndexError crashes.
- **Impact:** Advisory system crash. 500 error to Godot.
- **Proposed Fix:** Add guard: `if not threat_entries: return _diplomatic_overview(world)`

### [P39-3] Vassal Summary Lacks Loyalty/Rebellion Context
- **Severity:** MINOR
- **Files:** diplomatic_advisory.py:713
- **Description:** VASSAL state always returns "Subordinate to our will" with no loyalty or rebellion risk information. Advisory knows about `world.vassals` but doesn't use it.
- **Impact:** Player misled about vassal stability. Talleyrand seems less competent.

### [P39-4] All Other Advisory Features Verified CORRECT
- Threat assessment formula: correct signs and weights ✓
- Fog of war: all strength displays use fogged estimates ✓
- No internal keys leaked to player ✓
- War score sign correct throughout ✓
- Integration with dialogue state machine correct ✓
- All edge cases (0 strength, eliminated nations, all at war) handled ✓

---

## Pass 40: Campaign Log + Dispatch + War Status Audit

### [P40-1] War Status Panel Trend Sign Flip Asymmetric
- **Severity:** MAJOR
- **Files:** war_status.py:71-80
- **Description:** Trend calculation flips `prev` score sign when France is second in diplo_key, but `score` is already correct (from `get_war_score_for()`). Both are compared, but they're now in different perspectives if the flip is applied to only one.
- **Impact:** Trend arrows may show opposite direction for some nation pairs.
- **Proposed Fix:** Ensure prev_scores are stored in same perspective as get_war_score_for() output

### [P40-2] Dispatch Fog Filter Missing "aggressor" Nation Key
- **Severity:** MAJOR
- **Files:** dispatch.py:994-998
- **Description:** Fog filtering for diplomatic events checks `("nation", "nation_a", "nation_b", "target")` but war declaration events use `"aggressor"` field. Missing key means aggressor nation's visibility isn't checked.
- **Impact:** War declarations by fogged nations may leak through fog filter.
- **Proposed Fix:** Add `"aggressor"` to the nations_to_check loop

### [P40-3] Dispatch Hardcoded known_nations List
- **Severity:** MAJOR
- **Files:** dispatch.py:541
- **Description:** Talleyrand Report builder uses `known_nations = ["Britain", "Prussia", "Austria", "Saxony"]` — static list that breaks with vassals or mods.
- **Impact:** New nations invisible in Talleyrand briefing.
- **Proposed Fix:** Use `get_known_nations(world)` or world.enemy_nations

### [P40-4] Coalition Leader Can Be None in War Status Response
- **Severity:** MINOR
- **Files:** war_status.py:193
- **Description:** `coalition.get("leader")` can return None if coalition dict lacks "leader" key. Response sends `"leader": None` which Godot may not handle.
- **Proposed Fix:** Use `coalition.get("leader") or ""`

### [P40-5] Campaign Log OR-Logic for Diplomatic Event Visibility
- **Severity:** MINOR
- **Files:** campaign_log.py:271-293
- **Description:** Shows diplomatic event if ANY relevant nation is visible (PARTIAL+). Should arguably require ALL nations to be visible to avoid leaking information about unknown nations' diplomatic actions.
- **Impact:** Minor fog leak — treaty between unknown nations shown if one is known.

### [P40-6] Strategic Order Destination Empty String Not Distinguished from Missing
- **Severity:** MINOR
- **Files:** campaign_log.py:438-441
- **Description:** Empty string destination treated same as present destination. HOLD orders with no destination show ambiguously.
- **Impact:** Minor display issue in campaign log.

---

## Pass 41: Executor Completeness Audit

### [P41-0] Executor Verified CLEAN
- All 52 _execute_* handlers reachable from main dispatch ✓
- All handlers return consistent {success, message} format ✓
- Bypass hierarchy (pre-validation → objection → execution) correct everywhere ✓
- is_player_action correctly blocks AP consumption for enemy marshals ✓
- Free actions correctly skip AP cost ✓
- Post-objection handler covers all objection-able actions ✓
- State clearing follows Golden Rule 4 ✓
- No orphaned handlers ✓
- Minor: is_player_action calculated twice (lines 1502, 2305) — identical logic, low risk

---

## Pass 42: Godot main.gd Deep Audit

### [P42-1] War Panel HUD Skipped When Diplomatic Popups Show
- **Severity:** MAJOR (confirms P25-1)
- **Files:** main.gd:942-943 vs 770-825 (early returns)
- **Description:** `_process_active_wars(response)` at line 943 never executes when modal diplomatic popups trigger early returns (coalition_declaration, incoming_proposal, etc.). War status panel shows stale data.
- **Impact:** N4 War Status Panel feature broken during diplomacy flows.

### [P42-2] Morning Dispatch Lost After Enemy Phase Redemption
- **Severity:** MAJOR
- **Files:** main.gd:2207-2212
- **Description:** When redemption_event exists post-enemy-phase, `_show_pending_dispatch()` called but pending_dispatch_data may already be overwritten. Redemption dialog return doesn't restore dispatch.
- **Impact:** Morning Dispatch lost silently during redemption events.

### [P42-3] Talleyrand Objection "Modify" Choice Input Race
- **Severity:** MAJOR
- **Files:** main.gd:2794-2797
- **Description:** When player chooses "modify", input re-enabled before popup hidden. Player can send command while objection popup still visible.
- **Impact:** Two commands execute simultaneously — state corruption risk.

### [P42-4] Glorious Charge Response Doesn't Update War Panel
- **Severity:** MAJOR
- **Files:** main.gd:2467-2509
- **Description:** After glorious charge choice, `_process_active_wars(response)` never called. If charge triggers war state change, HUD stale.
- **Impact:** War panel not updated after cavalry action.

### [P42-5] Clarification Cancel Doesn't Refresh War Panel
- **Severity:** MAJOR
- **Files:** main.gd:2715-2719
- **Description:** When player cancels clarification, input re-enabled without updating game state or war panel.
- **Impact:** Stale UI if clarification would have changed war state.

### [P42-6] Pending Response Cleared Prematurely in Strategic Report Dismiss
- **Severity:** MINOR
- **Files:** main.gd:2589-2590
- **Description:** If no strategic reports exist, both pending responses nulled before being used.
- **Impact:** Edge case — may lose response data on fast dismiss.

### [P42-7] Diplomacy Wizard ESC Handling Inconsistent
- **Severity:** MINOR
- **Files:** main.gd:587, 2868-2869
- **Description:** ESC calls `top_bar.close_all_screens()` but doesn't check diplomacy_wizard. Wizard listed in `_is_modal_dialog_open()` but not handled by ESC key.
- **Impact:** ESC doesn't close wizard, confusing UX.

### [P42-8] Empty Command Silently Accepted
- **Severity:** MINOR
- **Files:** main.gd:691-697
- **Description:** Empty enter key produces no feedback. Command added to history check (internal guard) but no message to player.
- **Impact:** Minor UX — player confusion on empty input.

---

## Pass 43: Dialogue State Machine Deep Audit

### [P43-1] War Score Sign Inverted in Template Slot Resolution (Confirmed)
- **Severity:** CRITICAL (confirms P4/P18 war score sign findings)
- **Files:** diplomatic_templates.py:1159
- **Description:** `slots["war_score"] = str(int(world.war_scores.get(diplo_key, 0)))` uses raw diplo_key score instead of `get_war_score_for()`. Shows inverted sign when France is alphabetically second (France vs Britain/Austria/Prussia).
- **Impact:** All templates using {war_score} show wrong sign for 4 of 4 enemy nations.

### [P43-2] get_game_bucket() War Score Sign Logic Inverted
- **Severity:** MAJOR
- **Files:** diplomatic_dialogue.py:267-272
- **Description:** Manual sign flip checks `parts[0] == target_nation` but should check `parts[0] != "France"`. Logic is inverted for nation pairs where target is alphabetically after France (only Saxony). Accidentally correct for Britain/Austria/Prussia but wrong reasoning.
- **Impact:** Game bucket classification may be wrong for France-Saxony pair. "winning_comfortably" shown as "losing_badly" or vice versa.

### [P43-3] Non-Blocking Dialogue Auto-Dismiss Doesn't Clear Popup
- **Severity:** MAJOR
- **Files:** world_state.py:3859-3862
- **Description:** When non-blocking dialogue auto-dismisses after 1 turn, `pending_diplomatic_dialogue` cleared but `incoming_proposal_popup` NOT cleared. The blocking timeout case (line 3876) correctly clears both. Inconsistency.
- **Impact:** Stale popup data persists after dialogue timeout, causing duplicate popup displays.
- **Proposed Fix:** Add `self.incoming_proposal_popup = None` to line 3862

### [P43-4] DP Cost in Feasibility Uses Hardcoded Skill=10
- **Severity:** MINOR
- **Files:** diplomatic_dialogue.py:802
- **Description:** Feasibility DP cost display uses `get_dp_cost(f"propose_{proposal_type}", 10)` with hardcoded skill=10 instead of actual Talleyrand skill.
- **Impact:** Displayed DP cost may not match actual charge. UX confusion.

### [P43-5] All Other Dialogue Features Verified CORRECT
- No stuck states possible (auto-dismiss + force-clear safety valve) ✓
- All dialogue keywords routed correctly in main.py ✓
- Counter-offer flow properly creates new dialogue state ✓
- Multiple dialogues prevented (only one pending at a time) ✓
- Post-objection handler covers all objection-able actions ✓

---

## Pass 44: Region/Terrain System Audit

### [P44-1] Britain's Capital (Netherlands) Missing is_capital Flag (Confirmed)
- **Severity:** CRITICAL (confirms base audit finding)
- **Files:** region.py:347-355, 503-509
- **Description:** `NATION_CAPITALS["Britain"] = "Netherlands"` but `REGIONS_DATA["Netherlands"]["is_capital"]` is False. All other 4 nations have is_capital=True on their capitals. Comment says "Proxy — no London on map" but flag inconsistency remains.
- **Impact:** Code checking `region.is_capital` treats Netherlands differently from other capitals.

### [P44-2] All Other Region/Terrain Features Verified CORRECT
- All 19 regions defined with consistent data ✓
- All adjacencies bidirectional (fully connected graph) ✓
- All 6 terrain types distributed and mapped to combat bonuses ✓
- Charge blocking terrain list consistent with cavalry effectiveness ✓
- Supply capacity by region type matches constants ✓
- Grid positions unique (no overlaps) ✓
- Building system valid (capital 2 slots, city/major_city 1, town/rural 0) ✓
- Serialization complete (16 fields round-trip) ✓

---

## Pass 45: Performance Hotspot Analysis

### Performance Patterns Identified (Not Bugs — Design Notes)

1. **calculate_visibility() — O(regions×marshals)**: Called every turn, iterates 19 regions × all marshals. Could cache `friendly_marshal_regions` set. Estimated 570+ operations/turn.

2. **advance_turn() — 25+ Sequential Steps**: Each step iterates full marshal/region sets. Could batch per-marshal resets into single loop and add early exits for no-ops (no vassals → skip vassal processing).

3. **event_log Grows Unbounded**: Accumulates ~50 events/turn. By turn 40, 2000+ entries. `get_events_since_turn()` requires list scan. Could use dict-by-turn indexing.

4. **Enemy AI — O(nations×marshals×actions)**: 4 nations × 3 marshals × 10 actions × scoring = 320+ evaluations per enemy phase. Could cache marshal priorities once per nation turn.

**Assessment:** None of these are blocking at current scale (19 regions, ~10 marshals, 40-turn game). Would matter for modded games with larger maps/more nations.

---

## Pass 46: Test Coverage Gap Analysis

### Critical Bugs With NO Test Coverage

| Bug | Finding | Test Status |
|-----|---------|-------------|
| Vassal cooldown off-by-one | P32-3, P32-4 | **NO TEST** — duration not verified |
| Conquest bypasses release cooldown | P2 base audit | **NO TEST** — conquest+cooldown combo untested |
| Glorious charge missing record_diplo_battle | P2 base audit | **NO TEST** — charge→war score link untested |
| Auto-downgrade doesn't remove active treaty | P2 base audit | **NO TEST** — treaty cleanup untested |
| break_treaty threat when AI breaks | P2 base audit | **1 TEST** — direction not gated |

### Critical Bugs With WEAK Test Coverage

| Bug | Finding | Coverage Gap |
|-----|---------|-------------|
| Popup passthroughs (42+ returns) | P1 base audit | Tests check feature works, not that ALL 42 returns call it |
| Ultimatum bypasses state machine | P2 base audit | Cooldown tested, full side effects not |
| Honor defender DP deduction | P2 base audit | Paradox scenarios tested, DP deduction not isolated |

### Missing Integration Test Categories
- End-to-end diplomatic flow (proposal→response→counter→acceptance)
- Popup chain preservation across endpoints
- Vassal loyalty + rebellion + cascade interaction
- Multi-turn state re-entry (WAR→ARMISTICE→WAR)
- Coalition brewing at 90+ threat override

---

## Cumulative Summary (FINAL)

### Total Findings by Pass

| Pass | Focus | New Findings | CRITICAL | MAJOR | MINOR |
|------|-------|-------------|----------|-------|-------|
| 1 | Verify existing | 11 | 8 | 3 | 0 |
| 2 | Line-by-line review | 36 | 0 | 14 | 22 |
| 3 | Data flow tracing | 16 | 2 | 8 | 6 |
| 4 | Edge cases + consistency | 12 | 2 | 2 | 8 |
| 5 | Test gaps | 10 gaps | — | — | — |
| 6 | Serialization + dead code | 5 | 0 | 1 | 4 |
| 7 | Architecture | 6 patterns | — | — | — |
| 9 | Deep dives | 3 confirmed | 2 | 1 | 0 |
| 10 | Spec compliance | 9 | 0 | 3 | 6 |
| 11 | Godot popup audit | 3 | 0 | 2 | 1 |
| 12 | Treaty processing | 6 | 0 | 4 | 2 |
| 13 | Fog of war leaks | 3 | 0 | 2 | 1 |
| 14 | Save/load audit | 0 (clean) | 0 | 0 | 0 |
| 15 | Enemy AI decisions | 2 | 0 | 1 | 1 |
| 16 | Mock parser audit | 1 | 0 | 1 | 0 |
| 17 | Notification completeness | 3 | 0 | 1 | 2 |
| 18 | War score sign search | 0 (confirmed 4) | 0 | 0 | 0 |
| 19 | Diplomatic dialogue | 4 | 0 | 2 | 2 |
| 20 | Strategic orders | 2 | 0 | 1 | 1 |
| 23 | Coalition spec compliance | 5 | 0 | 3 | 2 |
| 24 | Tactical Triangle spec | 2 | 0 | 2 | 0 |
| 25 | Godot script deep audit | 11 | 2 | 4 | 3 |
| 26 | Combat edge cases | 8 | 1 | 4 | 3 |
| 27 | Fog of war spec | 1 | 0 | 0 | 1 |
| 28 | V2B defiance spec | 5 | 0 | 3 | 2 |
| 29 | Save/load edge cases | 4 | 0 | 2 | 2 |
| 30 | LLM integration | 2 | 0 | 2 | 0 |
| 31 | Multi-marshal spec | 1 | 0 | 1 | 0 |
| 32 | Vassal system deep | 4 | 1 | 3 | 0 |
| 33 | Diplomatic templates | 2 | 0 | 0 | 2 |
| 34 | Enemy AI decision tree | 1 | 1 | 0 | 0 |
| 35 | Notification system | 4 | 0 | 0 | 4 |
| 36 | Turn processing order | 0 (clean) | 0 | 0 | 0 |
| 37 | Diplomatic state machine | 3 | 1 | 2 | 0 |
| 38 | Manpower/economy | 1 (confirmed) | 1 | 0 | 0 |
| 39 | Diplomatic advisory | 3 | 1 | 1 | 1 |
| 40 | Campaign log + dispatch | 6 | 0 | 3 | 3 |
| 41 | Executor completeness | 0 (clean) | 0 | 0 | 0 |
| 42 | Godot main.gd deep | 8 | 0 | 5 | 3 |
| 43 | Dialogue state machine | 4 | 1 | 2 | 1 |
| 44 | Region/terrain system | 1 (confirmed) | 1 | 0 | 0 |
| 45 | Performance hotspots | 4 patterns | — | — | — |
| 46 | Test coverage gaps | 8 gaps | — | — | — |
| 47 | Acceptance formula | 3 | 1 | 1 | 1 |
| 48 | Popup data flow | 3 | 2 | 1 | 0 |
| 49 | Authority/trust | 2 | 0 | 1 | 1 |
| 50 | War declaration cascade | 5 | 2 | 3 | 0 |
| 51 | DIPLOMACY_SPEC formulas | 3 | 2 | 1 | 0 |
| 52 | Cheat/debug security | 7 | 2 | 4 | 1 |
| 53 | Save format migration | 5 | 0 | 3 | 2 |
| 54 | Cross-system interactions | 7 | 1 | 5 | 1 |
| 55 | Godot popup scripts | 8 | 2 | 4 | 2 |
| 56 | Modding system validation | 19 | 3 | 6 | 10 |
| 57 | Diplomatic dialogue deep | 3 | 2 | 1 | 0 |
| 58 | Notification system | 6 | 0 | 4 | 2 |
| 59 | Smart suggestions pipeline | 8 | 2 | 2 | 4 |
| 60 | Mock parser completeness | 8 | 4 | 2 | 2 |
| 61 | Economy/gold system | 4 | 1 | 3 | 0 |
| 62 | Fog of war completeness | 4 | 1 | 2 | 1 |
| 63 | Executor bypass hierarchy | 3 | 0 | 1 | 2 |
| 64 | Battle report accuracy | 5 | 0 | 0 | 5 |
| 65 | Diplomatic advisory | 3 | 0 | 1 | 2 |
| 66 | Turn processing order | 0 (clean) | 0 | 0 | 0 |
| 67 | Coordinate/grid system | 3 | 1 | 2 | 0 |
| 68 | Diplomatic transitions | 9 | 3 | 3 | 3 |
| 69 | Godot API response contract | 5 | 1 | 3 | 1 |
| 70 | Enemy AI decision tree deep | 3 | 1 | 1 | 1 |
| 71 | Manpower/recruitment | 3 | 0 | 1 | 2 |
| 72 | Strategic order edge cases | 6 | 1 | 4 | 1 |
| 73 | Trust/relationship formula | 5 | 1 | 2 | 2 |
| 74 | Cavalry/artillery mechanics | 0 (clean) | 0 | 0 | 0 |
| 75 | Vindication/authority system | 2 | 1 | 0 | 1 |
| 76 | LLM integration | 3 | 0 | 2 | 1 |
| 77 | Godot popup flow deep | 10 | 1 | 6 | 3 |
| 78 | Constructor/init audit | 0 (clean) | 0 | 0 | 0 |
| 79 | Diplomacy wizard integration | 4 | 1 | 3 | 0 |
| 80 | Error message quality | 3 | 1 | 2 | 0 |
| 81 | Supply/attrition | 1 | 0 | 0 | 1 |
| 82 | Occupation/fortification | 4 | 2 | 0 | 2 |
| 83 | Dead code identification | 16 | 0 | 6 | 10 |
| 84 | Test coverage cross-reference | 20 gaps | -- | -- | -- |
| 85 | Godot .tscn scene validation | 0 (clean) | 0 | 0 | 0 |
| 86 | DIPLOMACY_SPEC formula compliance | 7 | 0 | 3 | 4 |
| 87 | Cross-system stress scenarios | 1 | 0 | 1 | 0 |
| 88 | Race conditions/state consistency | 9 | 0 | 1 | 8 |
| 89 | Personality system completeness | 10 | 0 | 0 | 10 |
| 90 | Integer overflow/bounds/numeric | 4 | 0 | 1 | 3 |
| 91 | COALITION_SPEC formula compliance | 3 | 0 | 2 | 1 |
| 92 | V2B_DEFIANCE_SPEC compliance | 5 | 0 | 0 | 5 |
| 93 | Endpoint security/input validation | 6 | 1 | 2 | 3 |
| 94 | Morning dispatch/campaign log | 10 | 0 | 3 | 7 |
| 95 | Event log/notification completeness | 9 | 0 | 0 | 9 |
| 96 | Vassal system spec compliance | 7 | 0 | 3 | 4 |
| 97 | Diplomatic dialogue state machine | 4 | 0 | 0 | 4 |
| 98 | AI diplomacy decision making | 6 | 0 | 1 | 5 |
| 99 | Save format migration | 6 | 0 | 0 | 6 |
| 100 | Godot response handling | 8 | 2 | 3 | 3 |
| 101 | Hotkey/input handling | 3 | 0 | 1 | 2 |
| 102 | Template/display strings | 2 | 0 | 0 | 2 |
| 103 | MULTI_MARSHAL_SPEC compliance | 1 | 0 | 0 | 1 |
| 104 | Action economy/AP system | 4 | 1 | 1 | 2 |
| **Total** | | **~508** | **67** | **193** | **236** |

### Top 15 Most Critical Findings (NEW — not in base audit)

| # | Finding | Pass | Severity | Impact |
|---|---------|------|----------|--------|
| 1 | **_ratify_treaty doesn't call create_vassal_treaty** — vassalage via peace treaty creates no actual vassal | 3/9 | CRITICAL | Entire vassal-via-diplomacy feature is broken |
| 2 | **Coordinated battles record 0 casualties** — game's largest engagements invisible to war score | 3/9 | CRITICAL | War score ignores multi-marshal battles |
| 3 | **Defense modifier inverted by division** — defensive stance makes defender take MORE damage | 26 | CRITICAL | Core combat mechanic broken — ~95% more casualties than intended |
| 4 | **Stale proposal acceptance bypasses WAR→ARMISTICE→PEACE** — accept peace during war skips armistice | 4 | CRITICAL | State machine violation |
| 5 | **War score sign bug systemic** — 4 locations show inverted score for Austria/Britain | 4 | CRITICAL | Wrong armistice terms, wrong dialogue text |
| 6 | **Godot: active_wars never updates during diplomacy popups** — war panel stale | 25 | CRITICAL | War HUD shows outdated data across multiple turns |
| 7 | **battles_this_turn cleared before vassal loyalty** — "lord battle" modifier is dead code | 3 | MAJOR | Vassal loyalty never reflects battle outcomes |
| 8 | **Diplomatic defiance pipeline orphaned** — sabotage entry points have no production callers | 6/9 | MAJOR | Talleyrand sabotage never triggers in gameplay |
| 9 | **Territory sweetener inflated 5x** — max(5,...) designed for gold applies to territory | 2 | MAJOR | AI counter-offers with territory wildly overpowered |
| 10 | **War declaration Talleyrand objection broken at 3 levels** — wrong fields, misrouted proceed, infinite loop | 3/11 | MAJOR | War declaration objection flow completely non-functional |
| 11 | **Ultimatum acceptance bypasses state machine** — raw state set, no side effects | 2 | MAJOR | No armistice cooldown, no war end cleanup |
| 12 | **Vassal battle field mismatch** — loyalty reads `victor`/`attacker_nation` but dict has `result`/`attacker` | 32 | CRITICAL | Lord's combat performance never affects vassal loyalty |
| 13 | **break_treaty missing WAR/ARMISTICE cleanup** — war data orphaned on treaty break | 37 | CRITICAL | War exhaustion, cascade markers never cleared |
| 14 | **AI fog leak via get_enemies_of_nation()** — AI sees all enemies regardless of visibility | 34 | CRITICAL | AI cheats through fog of war |
| 15 | **AP sweetener value 18 vs spec's 8** — 125% inflation in counter-offer acceptance | 47 | CRITICAL | AI counter-offers far too generous |
| 16 | **Talleyrand objection popup field mismatch** — backend/Godot key names don't match | 48 | CRITICAL | Popup displays empty or crashes |
| 17 | **Alliance paradox popup has no Godot handler** — data sent, silently ignored | 48/50 | CRITICAL | Alliance paradox invisible to player |
| 18 | **Alliance paradox honor/break free (no DP cost)** — paradox path bypasses DP deduction | 50 | CRITICAL | War via paradox is free vs normal cost |
| 19 | **No self-war prevention** — declare_war() allows nation vs itself | 50 | CRITICAL | Could corrupt diplomatic state |
| 20 | **defiance_succeeded() reads non-existent "won" field** — defiant attacks ALWAYS fail | 75 | CRITICAL | Entire defiance reward mechanic inverted |
| 21 | **Fortified marshals can move/attack via strategic execution** — _strategic_execution bypasses fortify block | 82 | CRITICAL | Fortification state meaningless for strategic orders |
| 22 | **Wizard double-open during HTTP request** — no guard against concurrent opens | 79 | CRITICAL | Duplicate HTTP requests, state corruption |
| 23 | **"Game state error" messages — zero diagnostic value** — 3+ endpoints return generic errors | 80 | CRITICAL | Impossible to diagnose production failures |
| 24 | **AP clause cumulative permanent reduction** — nation_actions drained to 1 AP in a few turns | 104 | CRITICAL | AP treaty clauses devastatingly overpowered vs AI |
| 25 | **Path traversal in /load and /delete_save** — no filename sanitization against ../ | 93 | HIGH | Arbitrary file deletion outside saves directory |
| 26 | **Bare response.message in ~12 Godot error paths** — crashes on missing key | 100 | HIGH | Any backend response without message key crashes Godot |

---

## Pass 47: Acceptance Formula Deep Dive

### Finding 47-1: AP Sweetener Value Inflated 125%
- **Severity:** CRITICAL
- **File:** `backend/game_logic/diplomacy.py:215`
- **Description:** AP sweetener clause valued at 18 acceptance points, but DIPLOMACY_SPEC S7 specifies 8. This 125% inflation makes AP clauses dramatically over-weighted in counter-offers.
- **Evidence:** Code: `"AP": 18` in sweetener value table vs spec value of 8.
- **Proposed Fix:** Change AP sweetener value from 18 to 8.
- **Test Coverage:** No test validates sweetener values against spec.

### Finding 47-2: Sweetener Cap 50% Over Spec
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomacy.py:221`
- **Description:** Total sweetener acceptance cap is 60, but spec says 40. Combined with Finding 47-1, AI counter-offers are far more generous than designed.
- **Evidence:** Code: `min(total_sweetener, 60)` vs spec: "capped at 40 total sweetener points."
- **Proposed Fix:** Change cap from 60 to 40.
- **Test Coverage:** No test validates cap against spec.

### Finding 47-3: Base DP Generation Rate Discrepancy
- **Severity:** MINOR
- **File:** `backend/game_logic/diplomacy.py`
- **Description:** Base DP generation is 3/turn; spec may intend 2. Needs spec cross-reference to confirm.
- **Evidence:** Code generates 3 DP per turn for all nations.
- **Proposed Fix:** Verify against DIPLOMACY_SPEC and adjust if needed.
- **Test Coverage:** Tested functionally but not validated against spec value.

---

## Pass 48: Popup Data Flow Audit

### Finding 48-1: Talleyrand Objection Popup Field Mismatch
- **Severity:** CRITICAL
- **File:** `backend/commands/executor.py` to `godot-client/project-sovereign/scripts/talleyrand_objection_popup.gd`
- **Description:** Backend sends `{type, severity, message, action, target_nation}` but Godot popup expects `{concern_level, objection_text, defiance_risk, proposal_summary}`. Fields don't match -- popup would display empty or crash.
- **Evidence:** Executor builds dict with `type`/`severity`/`message` keys; Godot `.gd` reads `concern_level`/`objection_text`/`defiance_risk`.
- **Proposed Fix:** Align backend output keys with Godot expectations (or add translation layer in main.py).
- **Test Coverage:** No integration test validates popup data shape.

### Finding 48-2: Alliance Paradox Popup Has No Godot Handler
- **Severity:** CRITICAL
- **File:** `backend/main.py:158`, `godot-client/project-sovereign/scripts/main.gd`
- **Description:** Backend generates `alliance_paradox_popup` data and has a TODO comment at line 158, but no Godot script handles this popup type. The data is sent but silently ignored by the frontend.
- **Evidence:** `main.py` line 158: `# TODO: alliance paradox popup handler`. No `.gd` file references `alliance_paradox_popup`.
- **Proposed Fix:** Implement alliance paradox popup in Godot (new scene + script) or route through existing popup.
- **Test Coverage:** None.

### Finding 48-3: Four POST Endpoints Missing Popup Passthroughs
- **Severity:** MAJOR
- **File:** `backend/main.py`
- **Description:** `/save`, `/load`, `/delete_save`, `/notifications/dismiss` POST endpoints never call `_include_popup_passthroughs()`. Any diplomatic popups queued during these operations are silently lost.
- **Evidence:** These 4 endpoints return responses directly without passthrough call.
- **Proposed Fix:** Add `_include_popup_passthroughs(response, world)` to all 4 endpoints.
- **Test Coverage:** No test checks passthrough on these endpoints.

---

## Pass 49: Authority and Trust System Audit

### Finding 49-1: Excessive Trust Threshold Off-by-One
- **Severity:** MAJOR
- **File:** `backend/models/authority.py:309,311`
- **Description:** Excessive trust check uses `>` instead of `>=`. A marshal with exactly 80 trust does NOT trigger "excessive trust" effects, despite 80 being the threshold boundary.
- **Evidence:** Code: `if marshal.trust.value > 80:` -- should be `>= 80` per threshold design intent.
- **Proposed Fix:** Change `>` to `>=` at lines 309 and 311.
- **Test Coverage:** No test checks the exact boundary value of 80.

### Finding 49-2: Strategic Paths Bypass Redemption Flag
- **Severity:** MINOR
- **File:** `backend/commands/strategic.py`
- **Description:** Strategic order execution calls `marshal.trust.modify()` directly instead of `marshal.modify_trust()`, which bypasses the redemption event flag check. Trust changes from strategic orders won't trigger redemption events.
- **Evidence:** Direct `.trust.modify()` calls skip the marshal-level wrapper that checks redemption state.
- **Proposed Fix:** Route through `marshal.modify_trust()` instead.
- **Test Coverage:** No test validates redemption interaction with strategic orders.

---

## Pass 50: War Declaration Cascade Audit

### Finding 50-1: Alliance Paradox Honor/Break Does Not Deduct DP
- **Severity:** CRITICAL
- **File:** `backend/commands/executor.py:12952-13005`
- **Description:** When player chooses to honor or break an alliance paradox, the handler doesn't deduct diplomatic points. War declarations via normal path cost DP, but the paradox path is free.
- **Evidence:** Neither `honor_alliance_paradox` nor `break_alliance_paradox` handlers contain any DP deduction logic.
- **Proposed Fix:** Add DP deduction matching normal war declaration cost.
- **Test Coverage:** No test checks DP after paradox resolution.

### Finding 50-2: No Self-War Prevention in declare_war()
- **Severity:** CRITICAL
- **File:** `backend/game_logic/diplomacy.py:915`
- **Description:** `declare_war()` has no guard against a nation declaring war on itself. If called with `from_nation == target_nation` (e.g., via bug in AI or cascade), it would create a self-referential war entry.
- **Evidence:** No `if from_nation == target_nation: return` guard at function entry.
- **Proposed Fix:** Add early return guard.
- **Test Coverage:** No test attempts self-war.

### Finding 50-3: cascade_triggered Field Is Dead Code
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomacy.py`
- **Description:** The `cascade_triggered` field on war entries is set during cascade processing but never read anywhere in the codebase. It's serialized and persisted but serves no purpose.
- **Evidence:** Grep for `cascade_triggered` shows only write sites, no read sites outside serialization.
- **Proposed Fix:** Remove field or implement intended cascade-tracking behavior.
- **Test Coverage:** N/A -- dead code.

### Finding 50-4: Vassal Auto-Join in Cascade Never Called
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomacy.py`, `backend/game_logic/vassal.py`
- **Description:** Offensive cascade logic explicitly skips vassals ("vassals handle separately"), but the separate vassal auto-join-war function is never called from the cascade path. Vassals of a warring lord don't automatically join wars.
- **Evidence:** Cascade code skips vassals; no call to vassal auto-join from declare_war or cascade handlers.
- **Proposed Fix:** Add vassal auto-join call in the cascade path after lord enters war.
- **Test Coverage:** No test verifies vassal behavior during cascade.

### Finding 50-5: Cascade Events Use Partial Visibility Check
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomacy.py`
- **Description:** Cascade war declarations are filtered through fog of war. If the player has limited visibility of a cascading nation, they won't be notified that a new war started -- even if they're affected by it.
- **Evidence:** Cascade event notifications pass through fog filter before reaching player.
- **Proposed Fix:** War declarations affecting the player or their allies should bypass fog filter for the declaration notification.
- **Test Coverage:** No test checks fog interaction with cascade notifications.

---

## Pass 51: DIPLOMACY_SPEC Formula-by-Formula Compliance

### Finding 51-1: Base DP Generation 3 vs Spec's 2
- **Severity:** CRITICAL
- **File:** `backend/game_logic/diplomacy.py:859`
- **Spec:** S4a line 615 — "Base DP per turn: 2"
- **Actual:** `base = 3`
- **Impact:** All nations generate 50% more DP than designed. Over 25 turns, France accumulates ~25 extra DP — enough for 2-3 extra diplomatic actions. Compounds across all 6 AI nations.

### Finding 51-2: DP Skill Bonus Threshold Too Low
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomacy.py:860`
- **Spec:** S4a lines 617-620 — "Skill 10 (Talleyrand): +1 bonus DP; Skill 7-9: +0"
- **Actual:** `skill_bonus = 1 if diplomat and diplomat.skill >= 8 else 0`
- **Impact:** Diplomats with skill 8-9 get +1 DP when spec says they should get +0. Metternich (skill 9) and potentially Castlereagh get bonus DP they shouldn't.

### Finding 51-3: War Exhaustion Per-Turn Rate +8 vs Spec +5 (Confirmed)
- **Severity:** CRITICAL
- **File:** `backend/game_logic/coalition.py:938`
- **Spec:** COALITION_SPEC S10a line 635 — "+5 per turn while at war"
- **Actual:** `new_we = min(current_we + 8, WAR_EXHAUSTION_MAX)` with comment "R11: was +5"
- **Impact:** Coalition members burn out 60% faster. After 20 turns: WE=160 vs spec's 100. Drastically changes coalition durability and peace acceptance timing.

---

## Pass 52: Cheat/Debug Command Security Audit

### Finding 52-1: Cheats Bypass DEBUG_MODE in Mock LLM Mode
- **Severity:** CRITICAL
- **File:** `backend/commands/executor.py:14150`
- **Description:** Cheat gate checks `llm_mode != "mock" and not debug_mode`. In mock mode (default for development), cheats are ALWAYS available regardless of DEBUG_MODE setting.
- **Evidence:** `if llm_mode != "mock" and not debug_mode:` — mock mode short-circuits the check.
- **Impact:** If deployed with LLM_MODE=mock (the default .env value), all cheat commands are accessible.

### Finding 52-2: /debug_marshal Endpoint Missing DEBUG_MODE Guard
- **Severity:** CRITICAL
- **File:** `backend/main.py:1505-1557`
- **Description:** The `/debug_marshal/{marshal_name}` endpoint exposes trust, vindication, authority data without checking DEBUG_MODE. All other debug endpoints have this guard.
- **Evidence:** No `if not DEBUG_MODE:` guard at entry, unlike `/debug/marshal_status` (line 2006) and `/debug/status` (line 2042).
- **Impact:** In production, attackers can read any marshal's trust value, vindication score, and authority level.

### Finding 52-3: set_diplo_state Cheat Bypasses State Validation
- **Severity:** MAJOR
- **File:** `backend/commands/executor.py:14213-14225`
- **Description:** `cheat set_diplo_state` directly assigns diplomatic state without calling `validate_transition()`. Can create impossible state transitions and arbitrary invalid strings.
- **Evidence:** Line 14221: `world.diplomatic_states[key] = state` — direct assignment, no validation.
- **Impact:** Can corrupt diplomatic state machine, break war tracking.

### Finding 52-4: Multiple Cheat Commands Missing Nation Validation
- **Severity:** MAJOR
- **File:** `backend/commands/executor.py:14172-14246`
- **Description:** `set_diplo_state`, `set_relation`, `set_war_exhaustion`, `create_vassal` all accept arbitrary nation names without validation.
- **Evidence:** `nation = cheat_args[0]` with no existence check.
- **Impact:** Creates orphaned state entries for non-existent nations.

### Finding 52-5: set_talleyrand_trust No Bounds Check
- **Severity:** MAJOR
- **File:** `backend/commands/executor.py:14249-14258`
- **Description:** `cheat set_talleyrand_trust` assigns trust without bounds checking. Can set negative or extreme values.
- **Evidence:** `talleyrand.trust = int(cheat_args[0])` — no min/max.
- **Impact:** Extreme trust values cause undefined behavior in defiance calculations.

### Finding 52-6: queue_ai_proposal Creates Incomplete Proposal
- **Severity:** MAJOR
- **File:** `backend/commands/executor.py:14261-14288`
- **Description:** `cheat queue_ai_proposal` creates proposal with minimal fields — missing from_nation, to_nation, acceptance_chance, cooldown_turns, diplomatic_points_cost.
- **Evidence:** Lines 14267-14278 show incomplete proposal construction.
- **Impact:** Frontend crash when rendering incomplete proposal.

### Finding 52-7: /debug/set_trust Bypasses Trust.modify()
- **Severity:** MINOR
- **File:** `backend/main.py:1985`
- **Description:** Debug endpoint directly modifies `marshal.trust._value` bypassing `Trust.modify()` side effects.
- **Evidence:** `marshal.trust._value = max(0, min(100, int(trust_value)))`. Comment acknowledges this.
- **Impact:** Debug trust changes skip normal pipeline.

---

## Pass 53: Save Format Migration Audit

### Finding 53-1: DiplomaticRepresentative Missing from Serialization Enforcement Test
- **Severity:** MAJOR
- **File:** `tests/test_serialization_enforcement.py:619-634`
- **Description:** `DiplomaticRepresentative` has `to_dict()`/`from_dict()` but is NOT in `SERIALIZABLE_CLASSES`. Future field additions won't be caught by CI.
- **Evidence:** SERIALIZABLE_CLASSES lists 9 classes; DiplomaticRepresentative missing.
- **Impact:** Silent data loss if diplomat fields are added without serialization.

### Finding 53-2: No Atomic Writes in save_manager.py
- **Severity:** MAJOR
- **File:** `backend/save_manager.py:72-73`
- **Description:** Save uses `open(filepath, 'w')` directly. Crash mid-write corrupts save file permanently. No temp-file + atomic-rename pattern.
- **Evidence:** `with open(filepath, 'w') as f: json.dump(save_data, f, indent=2)`
- **Impact:** Unrecoverable save data loss on crash during save.

### Finding 53-3: Morale Default Mismatch (100 vs 70)
- **Severity:** MINOR
- **File:** `backend/models/marshal.py:280` vs `marshal.py:1177`
- **Description:** Marshal morale initializes to 100 in `__init__` but `from_dict()` defaults to 70. Old saves restore at 70 instead of 100.
- **Evidence:** `self.morale = 100` vs `data.get("morale", 70)`.
- **Impact:** Subtle behavior change on loading old saves.

### Finding 53-4: No world_data Structure Validation After JSON Load
- **Severity:** MAJOR
- **File:** `backend/save_manager.py:105-108`
- **Description:** Only checks `world_data is not None`. Empty dict `{}` passes but crashes in `from_dict()`.
- **Evidence:** `if world_data is None: return error` then `WorldState.from_dict(world_data)`.
- **Impact:** Cryptic crashes on corrupted saves instead of graceful errors.

### Finding 53-5: Exception Handling Too Broad in Load
- **Severity:** MINOR
- **File:** `backend/save_manager.py:124-125`
- **Description:** Catch-all `except Exception` swallows all errors into "Load failed". Can't distinguish OS errors from serialization bugs.
- **Impact:** Real bugs hidden behind generic error messages.

---

## Pass 54: Cross-System Interaction Audit

### Finding 54-1: Offensive Cascade Does Not Skip Vassals
- **Severity:** CRITICAL
- **File:** `backend/game_logic/diplomacy.py:1169-1220`
- **Description:** Defensive cascade skips vassals (line 1174), but offensive cascade has NO vassal check. Vassals independently cascade into offensive wars.
- **Evidence:** Defensive: `if nation in vassals: continue`. Offensive loop processes ALL nations.
- **Impact:** War scores double-counted, diplomatic state inconsistent.

### Finding 54-2: Vassal Rebellion Does Not Trigger War Cascade
- **Severity:** MAJOR
- **File:** `backend/game_logic/vassal.py:407-476`
- **Description:** Rebellion sets `diplomatic_states[key] = "WAR"` but never calls `_process_war_cascade()`. Vassal's allies won't cascade to defend.
- **Evidence:** vassal.py:423-428 sets WAR directly; diplomacy.py `_process_war_cascade()` never called.
- **Impact:** Rebellions don't trigger allied responses.

### Finding 54-3: Coalition Auto-Adds Vassals Without Loyalty Check
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomacy.py:2100-2108`
- **Description:** Coalition formation auto-adds vassals without checking loyalty, strength, or consent.
- **Evidence:** Auto-adds PUPPET/SATELLITE vassals; qualification checks not applied.
- **Impact:** Vassals drafted into unpopular wars, war exhaustion triggers rebellion cascade.

### Finding 54-4: Coalition Loyalty Penalty Not Applied to Vassal Loyalty
- **Severity:** MAJOR
- **File:** `backend/game_logic/vassal.py:204-285`
- **Description:** `process_vassal_loyalty()` omits coalition penalty from `get_coalition_loyalty_penalty()`.
- **Evidence:** No coalition import or check in vassal loyalty modifiers.
- **Impact:** Vassal loyalty stays artificially high during coalition wars.

### Finding 54-5: PURSUE/SUPPORT Orders Don't Re-Validate War State
- **Severity:** MAJOR
- **File:** `backend/commands/strategic.py:859-938`
- **Description:** PURSUE/SUPPORT don't re-check `is_at_war()` before per-turn execution. Peace signed mid-turn doesn't stop the order from attacking.
- **Evidence:** strategic.py PURSUE resolves target without war status check; contrast executor.py normal attack.
- **Impact:** Marshal attacks nation it just made peace with.

### Finding 54-6: Cascade Notifications Leak Fogged Nations
- **Severity:** MINOR
- **File:** `backend/game_logic/diplomacy.py:1147-1163`
- **Description:** Cascade notifications sent regardless of fog visibility. Reveals hidden nations' diplomatic moves.
- **Evidence:** Notifications at 1147-1163 created without fog checks.
- **Impact:** Information leak through fog of war.

### Finding 54-7: Enemy AI Ignores Vassal Loyalty in Target Selection
- **Severity:** MINOR
- **File:** `backend/ai/enemy_ai.py:1250-1400`
- **Description:** AI P4 target evaluation doesn't consider vassal status or loyalty.
- **Evidence:** P4 scoring loop has no vassal check.
- **Impact:** Slightly suboptimal AI targeting.

---

## Pass 55: Godot Popup/Dialog Script Audit

### Finding 55-1: diplomatic_ledger.gd Null Crash on History Type
- **Severity:** CRITICAL
- **File:** `godot-client/project-sovereign/scripts/diplomatic_ledger.gd:689`
- **Description:** Calls `.to_lower()` on `h_type` derived from `entry.get("type", "?")`. If backend sends `type: null`, GDScript `.to_lower()` on null crashes the Talleyrand tab.
- **Evidence:** `var h_type = str(entry.get("type", "?"))` then `if "accept" in h_type.to_lower():`
- **Impact:** Entire Talleyrand tab crashes, all subsequent history entries lost.

### Finding 55-2: talleyrand_redemption_popup.gd Chained Null Crash
- **Severity:** CRITICAL
- **File:** `godot-client/project-sovereign/scripts/talleyrand_redemption_popup.gd:31-33`
- **Description:** Reads nested option fields via chained `.get()`. If backend sends `option_apologize: null` instead of a dict, `null.get("effect", ...)` crashes.
- **Evidence:** `data.get("option_apologize", {}).get("effect", "Trust +15")` — safe only if outer .get returns dict, not null.
- **Impact:** Redemption popup crashes, blocking all further player actions.

### Finding 55-3: coalition_declaration_popup.gd Type Coercion Crash
- **Severity:** MAJOR
- **File:** `godot-client/project-sovereign/scripts/coalition_declaration_popup.gd:41`
- **Description:** Uses `%d` format for war_exhaustion. If backend sends war_exhaustion as string, GDScript format crashes.
- **Evidence:** `"War Exhaustion: %d/100" % [nation, strength, we]` — %d requires int.
- **Impact:** Coalition declaration popup fails to render.

### Finding 55-4: incoming_proposal_popup.gd Displays "Null" for Missing Type
- **Severity:** MAJOR
- **File:** `godot-client/project-sovereign/scripts/incoming_proposal_popup.gd:41`
- **Description:** If `proposal_type` is null, `str(null)` produces literal "Null" displayed to player.
- **Evidence:** `proposal_type.replace("_", " ").capitalize()` shows "Null" if backend value is null.
- **Impact:** Unprofessional UI, confusing player display.

### Finding 55-5: Stale Coalition Data on Header Click
- **Severity:** MAJOR
- **File:** `godot-client/project-sovereign/scripts/main.gd:2972-2976`
- **Description:** `_on_coalition_header_clicked()` uses `_cached_coalition_data` which may be from a previous turn. If coalition dissolved between cache and click, player sees stale data.
- **Evidence:** Cache checked for null but not for staleness.
- **Impact:** Player sees disbanded coalition as still active.

### Finding 55-6: war_detail_popup.gd Missing weak_link Fallback
- **Severity:** MAJOR
- **File:** `godot-client/project-sovereign/scripts/war_detail_popup.gd:214-216`
- **Description:** `weak_link` field silently omitted if backend doesn't send it. No fallback text or warning.
- **Impact:** Player missing strategic information about which coalition member to target.

### Finding 55-7: incoming_proposal_popup.gd Empty Clauses Display
- **Severity:** MINOR
- **File:** `godot-client/project-sovereign/scripts/incoming_proposal_popup.gd:44-45`
- **Description:** If `clauses: []`, displays "Terms:" header with nothing below it.
- **Impact:** Confusing UI when backend fails to populate clauses.

### Finding 55-8: sabotage_discovery_popup.gd Silent Default Values
- **Severity:** MINOR
- **File:** `godot-client/project-sovereign/scripts/sabotage_discovery_popup.gd:27-31`
- **Description:** Trust penalty defaults to 10 if missing from backend, without warning the player.
- **Impact:** Minor — defaults are sensible but hide backend bugs.

---

## Pass 56: Modding System Validation Audit

### Finding 56-1: Strength Field Accepts Floats (Godot Crash)
- **Severity:** CRITICAL
- **File:** `backend/modding/validator.py:124`
- **Description:** Validator accepts `isinstance(data["strength"], (int, float))`. Floats pass validation but crash Godot (violates Golden Rule #2).
- **Impact:** Modded marshal strength as float crashes game.

### Finding 56-2: spawn_location Not Validated Against Region List
- **Severity:** CRITICAL
- **File:** `backend/modding/validator.py:88-203`
- **Description:** `spawn_location` accepted but never cross-validated against regions. A mod can set non-existent location.
- **Evidence:** Line 74: listed in MARSHAL_OPTIONAL_FIELDS. Lines 370-377: only `location` cross-validated, not `spawn_location`.
- **Impact:** Broken marshals can't respawn — game breaks mid-play.

### Finding 56-3: Controller Nation Not Validated Against Known Nations
- **Severity:** CRITICAL
- **File:** `backend/modding/validator.py:262-265`
- **Description:** Region `controller` only checked as string type, not validated against valid nations. "RandomEvilNation" passes.
- **Impact:** Invalid controller corrupts AI decision-making, diplomacy, and economy.

### Finding 56-4: No current_turn <= max_turns Validation
- **Severity:** MAJOR
- **File:** `backend/modding/validator.py:400-406`
- **Description:** A mod can set `current_turn: 50, max_turns: 5`. Game starts past completion.
- **Impact:** Undefined turn processing behavior.

### Finding 56-5: Terrain Type Not Validated
- **Severity:** MAJOR
- **File:** `backend/modding/validator.py:210-274`
- **Description:** Region `terrain` field never validated against VALID_TERRAINS. Invalid terrain causes KeyError in combat.
- **Impact:** Combat crashes on modded regions with unknown terrain.

### Finding 56-6: Region Type Not Validated
- **Severity:** MAJOR
- **File:** `backend/modding/validator.py:210-274`
- **Description:** `region_type` never validated. Invalid types cause KeyError in income calculations.
- **Impact:** Economy breaks on modded regions.

### Finding 56-7: Personality/Stance Case-Sensitive Validation
- **Severity:** MAJOR
- **File:** `backend/modding/validator.py:132-137`
- **Description:** "Aggressive" (capital A) passes validation but won't match game logic checking "aggressive".
- **Impact:** Marshal with unrecognized personality bypasses objection/AI logic.

### Finding 56-8: Morale/Tactical_Skill Are Warnings Not Errors
- **Severity:** MAJOR
- **File:** `backend/modding/validator.py:162,195`
- **Description:** Out-of-range morale (500) and tactical_skill (1000) produce warnings only. Mod passes validation but breaks game logic.
- **Impact:** Extreme values break combat calculations.

### Finding 56-9: No Upper Bounds on Strength
- **Severity:** MAJOR
- **File:** `backend/modding/validator.py:126-127`
- **Description:** Only checks `strength < 0`. No upper cap. `strength: 99999999` passes.
- **Impact:** Balance destruction.

### Finding 56-10 through 56-19: Various Moderate/Minor Validation Gaps
- Ability field validation incomplete (validator.py:178-184)
- Adjacent_regions bidirectionality only warns (validator.py:389-398)
- Marshal names not checked for uniqueness (validator.py:329-343)
- player_nation not validated against defined nations (validator.py:318-321)
- Location not trimmed like name (validator.py:117-120)
- doc_generator check_docs_current() stubbed (doc_generator.py:177-192)
- No validation of war_damage range, buildings array, stability range
- No caps on gold, income_value, actions_remaining

---

## Pass 57: Diplomatic Dialogue Deep Audit

### Finding 57-1: Sabotage Handler Field Name Typo (State Never Cleared)
- **Severity:** CRITICAL
- **File:** `backend/commands/executor.py:12718`
- **Description:** After handling sabotage discovery (confront/overlook), code sets `world.diplomatic_sabotage = None`. Correct field is `world.diplomatic_sabotage_popup`. Popup persists in responses until overwritten.
- **Evidence:** `world.diplomatic_sabotage = None` — field doesn't exist; should be `diplomatic_sabotage_popup`.
- **Impact:** Sabotage popup keeps reappearing in every subsequent response.

### Finding 57-2: Redemption Handler Field Name Typo (State Never Cleared)
- **Severity:** CRITICAL
- **File:** `backend/commands/executor.py:12742`
- **Description:** Same pattern as 57-1: `world.talleyrand_redemption = None` instead of `world.talleyrand_redemption_popup = None`.
- **Evidence:** Typo in field name — correct field is `talleyrand_redemption_popup`.
- **Impact:** Redemption popup keeps reappearing.

### Finding 57-3: Missing proposal_type When target_nation Is Falsy
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomatic_dialogue.py:676-678`
- **Description:** If `target_nation` is empty/None, `suggested_terms` becomes `{}` (falsy), so `proposal_type` is never added to it. Executor falls back to default "peace".
- **Evidence:** `suggested_terms["proposal_type"] = proposal_type` only runs inside `if suggested_terms:` block.
- **Impact:** Suggested terms missing proposal type for edge-case empty nations.

---

## Pass 58: Notification System Deep Audit

### Finding 58-1: GET Endpoints Don't Return Notifications
- **Severity:** MAJOR
- **File:** `backend/main.py:1014,1696,1730,1744,1758,1855,1919`
- **Description:** Seven GET endpoints (/status, /campaign_log, /dispatch, /ledger, /diplomatic_preview, /diplomatic_ledger, /marshal_overview) don't include notifications. If player opens screens between commands, queued notifications stay hidden.
- **Impact:** Coalition threats, vassal warnings, and diplomatic events invisible until next POST command.

### Finding 58-2: Early Returns in /command Skip Notification Check
- **Severity:** MAJOR
- **File:** `backend/main.py:490-502`
- **Description:** Game-over and empty-command early returns don't include notifications. Notifications created during turn processing are lost if next request triggers early return.
- **Impact:** Notifications silently dropped on error/empty command paths.

### Finding 58-3: No Notification Queue Size Limit
- **Severity:** MAJOR
- **File:** `backend/notifications.py:94`
- **Description:** `NotificationCollector.add()` has no size cap. Over a long game without dismissals, hundreds of notifications accumulate, causing O(n log n) sort overhead on every `get_pending()` call.
- **Impact:** Performance degradation in long games.

### Finding 58-4: Notification Sort Tiebreaker Missing
- **Severity:** MAJOR
- **File:** `backend/notifications.py:103-107`
- **Description:** Sort key `(priority, turn_created)` has no tiebreaker for same-priority same-turn notifications. Order within a batch is undefined.
- **Impact:** Coalition notifications may appear in arbitrary order within same turn.

### Finding 58-5: Dismiss Response Redundant Fields
- **Severity:** MINOR
- **File:** `backend/main.py:1943-1944`
- **Description:** Returns both `{"success": dismissed, "dismissed": 1 if dismissed else 0}` — redundant.
- **Impact:** Minor API inconsistency.

### Finding 58-6: No Explicit Notification Lifecycle Documentation
- **Severity:** MINOR
- **File:** `backend/notifications.py`
- **Description:** No docstring documents when notifications are created, persisted, returned, or cleared. Asymmetric inclusion across endpoints makes future bugs likely.
- **Impact:** Maintenance burden.

---

## Pass 59: Smart Suggestions Pipeline Audit

### Finding 59-1: Missing proposal_type Handler "armistice_stalemate"
- **Severity:** CRITICAL
- **File:** `backend/game_logic/diplomatic_templates.py:1543`
- **Description:** `_build_base_terms()` handles "armistice", "armistice_losing", "armistice_winning" but NOT "armistice_stalemate". `ai_diplomacy.py` lines 421/670 generate this type. Falls through with empty sweeteners/demands.
- **Impact:** AI armistice_stalemate proposals generate bland terms with no strategic substance.

### Finding 59-2: Missing proposal_type Handler "opportunistic"
- **Severity:** CRITICAL
- **File:** `backend/game_logic/diplomatic_templates.py:1543`
- **Description:** `_build_base_terms()` doesn't handle "opportunistic". `ai_diplomacy.py` lines 460/707 generate this type.
- **Impact:** Opportunistic non-aggression proposals have no strategic terms.

### Finding 59-3: Economic Feasibility Forces Minimum Gold Offers Beyond Treasury
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomatic_templates.py:1578,1580`
- **Description:** Uses `max(50, ...)` and `max(25, ...)` forcing minimum gold offers even when France has 0 gold and 0 income. Creates unfulfillable diplomatic obligations.
- **Evidence:** `int(min(s["value"], max(50, int(player_gold * gold_cap_pct))))` — offers 50 lump gold even if bankrupt.
- **Impact:** AI and player trapped offering terms they cannot fulfill.

### Finding 59-4: NATION_DESIRE_PROFILES Self-Referential (Nations Covet Own Regions)
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomatic_templates.py:1209-1242`
- **Description:** Austria covets Bavaria/Tyrol/Bohemia (already controls all three). Britain covets Netherlands/Hanover (controls both). Saxony covets Saxony/Dresden (controls both). The "coveted_territory_offered" tag can never trigger.
- **Impact:** These nations never receive tailored commentary about desired territory.

### Finding 59-5: No Fallback for Unrecognized Proposal Types
- **Severity:** MINOR
- **File:** `backend/game_logic/diplomatic_templates.py:1465-1566`
- **Description:** `_build_base_terms()` has no default/else case. New proposal types silently return empty terms.
- **Impact:** Future proposal types will generate ineffective terms without developer warning.

### Finding 59-6: Stage 2 Documentation Mismatch
- **Severity:** MINOR
- **File:** `backend/game_logic/diplomatic_templates.py:1320`
- **Description:** Docstring claims "personality adjustment" but implementation only does nation-desire injection. No personality modulation of suggested terms.
- **Impact:** Misleading documentation.

### Finding 59-7: Saxony Profile Is Degenerate
- **Severity:** MINOR
- **File:** `backend/game_logic/diplomatic_templates.py:1235`
- **Description:** Saxony's covets_regions = own capital and only other region. Commentary about "returning" territory irrelevant.
- **Impact:** Saxony never gets specialized diplomatic commentary.

### Finding 59-8: resolve_template_text Silently Masks Unresolved Slots
- **Severity:** MINOR
- **File:** `backend/game_logic/diplomatic_templates.py:1134-1189`
- **Description:** `_SafeFormatMap` returns `{key}` for unresolved slots instead of logging a warning. Typos in template slots produce literal `{unresolved_slot}` in player-visible text.
- **Impact:** Template typos silently reach the UI.

---

## Pass 60: Mock Parser Completeness Audit

### Finding 60-1: release_vassal Not in VALID_ACTIONS
- **Severity:** CRITICAL
- **File:** `backend/ai/validation.py` (missing), `backend/ai/llm_client.py:775-778`
- **Description:** Mock parser returns `action="release_vassal"` but this action is NOT in validation.py VALID_ACTIONS. Validation rejects it as unknown action.
- **Impact:** Vassal release command broken — players can never release vassals via command.

### Finding 60-2: Three Diplomatic Actions Missing from VALID_ACTIONS
- **Severity:** CRITICAL
- **File:** `backend/ai/validation.py` (missing), `backend/ai/llm_client.py:985,987,989`
- **Description:** `diplomatic_mission`, `diplomatic_feasibility`, `diplomatic_advisory` returned by parser but not in VALID_ACTIONS.
- **Impact:** Three diplomatic commands fail validation — features unreachable.

### Finding 60-3: diplomatic_error Not in VALID_ACTIONS or META_ACTIONS
- **Severity:** CRITICAL
- **File:** `backend/ai/validation.py` (missing), `backend/ai/llm_client.py:966`
- **Description:** Parser returns `action="diplomatic_error"` for misdirected military commands but validation rejects it.
- **Impact:** Error handling flow broken — error message never reaches player.

### Finding 60-4: Cheats Bypass DEBUG_MODE in Mock Mode (Confirmed from Pass 52)
- **Severity:** CRITICAL
- **File:** `backend/commands/executor.py:14150`
- **Description:** Already reported as 52-1. Confirmation: "cheat" and "meta_command" actions also not in VALID_ACTIONS or META_ACTIONS.

### Finding 60-5: "stand down" Keyword Ambiguity
- **Severity:** MAJOR
- **File:** `backend/ai/llm_client.py:644,798`
- **Description:** "stand down" appears in both cancel keywords (line 644) and stance-change neutral keywords (line 798). Cancel check runs first, so "stand down" always triggers cancel, never stance change.
- **Impact:** Players cannot use "stand down" to change stance to neutral.

### Finding 60-6: Four Strategic Actions Unreachable from Parser
- **Severity:** MAJOR
- **File:** `backend/ai/validation.py:38-41`, `backend/ai/llm_client.py:661-694`
- **Description:** `pursue`, `support`, `reinforce`, `march` are in VALID_ACTIONS but mock parser returns base actions (attack/move) instead. Strategic parser upgrades them later, but VALID_ACTIONS listing is misleading.
- **Impact:** Code smell — actions appear valid but are never directly returned by parser.

### Finding 60-7: "status" Action Not Parsed by Mock Parser
- **Severity:** MINOR
- **File:** `backend/ai/llm_client.py` (missing)
- **Description:** Executor has `_execute_status()` but mock parser has no keyword for "status".
- **Impact:** Status command unreachable in mock LLM mode.

### Finding 60-8: Parser/Validation Redundancy
- **Severity:** MINOR
- **File:** `backend/commands/parser.py:44-81`, `backend/ai/validation.py:69-85`
- **Description:** parser.py valid_actions duplicates META_ACTIONS entries (help, end_turn, debug).
- **Impact:** Redundant definitions, confusing source of truth.

---

## Pass 61: Economy/Gold System Audit

### Finding 61-1: Vassal Tribute Hardcoded 50g Per Region
- **Severity:** CRITICAL
- **File:** `backend/game_logic/vassal.py:568-572`
- **Description:** `process_vassal_tribute()` calculates income as flat 50g per controlled region, ignoring actual region income (capital=300, major_city=200, city=150, town=100, rural=50) and modifiers (stability, war damage).
- **Evidence:** `vassal_income += 50  # Base region income` — hardcoded regardless of region type.
- **Impact:** Vassals pay 1/6th to 1/18th of actual tribute. Player has minimal economic incentive to vassalize.

### Finding 61-2: Sweetener Components Dict Contains Floats
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomacy.py:631-780`
- **Description:** `sweetener_total` accumulates as float, `deal_balance` (float) is included in `components` dict sent to frontend. Only `raw_score` is cast to int at end. The components dict exposes floats to Godot.
- **Evidence:** `sweetener_total = 0.0`, `deal_balance = sweetener_total + demand_total` — floats in component breakdown.
- **Impact:** Godot may crash on float components; acceptance formula debugging shows imprecise values.

### Finding 61-3: Continental System Double-Penalizes Both Parties
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomacy.py:2121-2124`
- **Description:** `apply_continental_system()` deducts blocked trade income from BOTH the member nation AND Britain. Continental System is a trade embargo — should only reduce member's income from British trade, not also subtract from Britain's treasury.
- **Evidence:** Both `world.nation_gold[member] -= blocked` and `world.nation_gold["Britain"] -= blocked` applied.
- **Impact:** Britain's gold is artificially suppressed beyond design. Double cost breaks economic balance.

### Finding 61-4: Vassal Tribute Failure Is Silent
- **Severity:** MAJOR
- **File:** `backend/game_logic/vassal.py:579-581`
- **Description:** Tribute capped at vassal's current gold (preventing negative), but no dispatch event alerts the player when tribute is underpaid. Treaty gold_per_turn clause does fire such events.
- **Evidence:** `actual_tribute = min(tribute_amount, max(0, vassal_gold))` — silent cap, no notification.
- **Impact:** Player doesn't know why tribute is lower than expected; inconsistent with treaty payment failure handling.

---

## Pass 62: Fog of War Completeness Audit

### Finding 62-1: Dispatch Talleyrand Suggestions Leak All Nations
- **Severity:** CRITICAL
- **File:** `backend/game_logic/dispatch.py:541-660`
- **Description:** Talleyrand's proactive suggestions use hardcoded `known_nations = ["Britain", "Prussia", "Austria", "Saxony"]` and access exact diplomatic states/relations for all of them regardless of fog visibility. Player can infer nation existence and diplomatic attitudes even with zero intel.
- **Evidence:** Line 541: hardcoded list. Lines 543-660: full diplomatic state access, relation scores for all nations.
- **Impact:** Fog of war bypassed — player learns diplomatic relations with all nations from Talleyrand's Report.

### Finding 62-2: Coalition Members Strength/Gold Unfogged in Dispatch
- **Severity:** MAJOR
- **File:** `backend/game_logic/dispatch.py:843-856`
- **Description:** Coalition section of morning dispatch returns exact troop counts and gold for all coalition members without any fog filtering or banding.
- **Evidence:** `member_strength = sum(m.strength ...)` and `"gold": int(world.nation_gold.get(member, 0))` — raw values.
- **Impact:** Player learns exact military/economic capacity of coalition members without needing scouts.

### Finding 62-3: AI-AI Diplomatic States Leak via Ledger
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomatic_ledger.py:198-218`
- **Description:** Diplomatic Ledger reveals exact AI-AI diplomatic states if player has PARTIAL+ visibility on EITHER nation in the pair. Scouting Austria reveals Austria's relationship with every other nation.
- **Evidence:** `if nation_vis_priority >= partial_priority or other_vis_priority >= partial_priority:` — OR condition too permissive.
- **Impact:** Scouting one nation reveals entire diplomatic network.

### Finding 62-4: Qualifying Coalition Nations Unfogged in Dispatch/Ledger
- **Severity:** MINOR
- **File:** `backend/game_logic/dispatch.py:838`
- **Description:** When coalition is brewing, dispatch reveals exactly which nations will join (qualifying_nations list) without fog filter.
- **Impact:** Player can pre-emptively target qualifying nations before coalition forms.

---

## Pass 63: Executor Bypass Hierarchy Audit

### Finding 63-1: DEFEND No-Op Checked AFTER Objection
- **Severity:** MAJOR
- **File:** `backend/commands/executor.py:5218-5226`
- **Description:** When marshal is already fortified in defensive stance, the "no further action needed" check happens inside `_execute_defend()` — AFTER objection could have fired. Player sees objection, proceeds, then gets "no action needed" failure.
- **Evidence:** Lines 5220-5226 check `getattr(marshal, 'fortified', False)` inside execute handler, not in pre-validation.
- **Impact:** Player wastes turn on objection for impossible action.

### Finding 63-2: Recruit Fallback Location Silently Succeeds at Wrong Place
- **Severity:** MINOR
- **File:** `backend/commands/executor.py:7850-7875`
- **Description:** When player specifies recruit location in enemy territory, code finds nearest marshal and uses THAT marshal's location instead. Region control check at 7920-7924 runs after location resolution, masking the intent mismatch.
- **Evidence:** Lines 7850-7861 resolve marshal/location, then 7912-7924 check control. No warning that target location was rejected.
- **Impact:** Player intent subverted silently — recruits at wrong location.

### Finding 63-3: Dead Marshal Target Vague Error
- **Severity:** MINOR
- **File:** `backend/commands/executor.py:4048-4052`
- **Description:** When targeting a specific marshal at 0 strength, error message "Cannot find living enemy" doesn't indicate the marshal exists elsewhere but is too weak.
- **Impact:** Ambiguous error message in edge case.

### Pass 63 Assessment: Bypass Hierarchy Largely Correct
- Pre-validation (1542-1898): All major state checks run BEFORE objection. CORRECT.
- AP check (1534-1540, 1876-1897): Happens BEFORE objection. CORRECT.
- Objection (1902-2080): Deterministic trigger. CORRECT.
- Strategic execution correctly skips objections and AP checks. CORRECT.
- Gap: DEFEND's internal state check should move to pre-validation.

---

## Pass 64: Battle Report Accuracy Audit

### Finding 64-1: Dormant Ranged Bombardment Check (Dead Code)
- **Severity:** MINOR
- **File:** `backend/game_logic/battle_report.py:109-114`
- **Description:** Snapshot checks for "Ranged bombardment" when attacker is artillery AND locations differ. But resolve_battle() only handles same-location combat. This condition never fires.
- **Impact:** Dead code — ranged bombardment is handled by executor's _execute_bombardment(), not resolve_battle().

### Finding 64-2: Coordination Bonus Omitted from Attacker Snapshot (By Design)
- **Severity:** MINOR
- **File:** `backend/game_logic/battle_report.py:131-138`
- **Description:** Attacker modifier snapshot intentionally omits coordination bonuses. Comment documents this is by design (shown in Berthier observations instead). Snapshot is technically incomplete.
- **Impact:** Battle report modifier breakdown doesn't show coordination bonuses that did affect damage.

### Finding 64-3: Overwatch Penalty Staleness Risk
- **Severity:** MINOR
- **File:** `backend/game_logic/battle_report.py:125-129`
- **Description:** Overwatch penalty is a transient field. If not cleared between battles in same turn, snapshot could capture stale data.
- **Impact:** Potential for incorrect overwatch penalty in report after multiple same-turn battles.

### Finding 64-4: Square Formation Report Doesn't Show Unit-Type Variance
- **Severity:** MINOR
- **File:** `backend/game_logic/battle_report.py:217`
- **Description:** Reports square as generic +5% defense. Actual combat effect varies: -40% for cavalry attacker, +50% for artillery attacker. Report doesn't capture this.
- **Impact:** Player sees simplified modifier that doesn't reflect actual combat impact.

### Finding 64-5: Defender Coordination Bonus Also Omitted
- **Severity:** MINOR
- **File:** `backend/game_logic/battle_report.py:219-220`
- **Description:** Same as 64-2 but for defender side. Intentionally omitted per comment.
- **Impact:** Minor completeness gap in defender modifier display.

### Pass 64 Assessment: Battle Report Is Functionally Accurate
No CRITICAL or MAJOR bugs found. All reported modifiers match actual calculations. Issues are completeness/documentation only.

---

## Pass 65: Diplomatic Advisory System Audit

### Finding 65-1: Threat Score Double-Counting Military Strength
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomatic_advisory.py:266-269`
- **Description:** Two non-exclusive `if` statements for military strength scoring. A nation with 1.2x France's strength gets +40 (same as 1.5x). Should use `elif`.
- **Evidence:** `if strength > france_strength * 0.5: +20` and `if strength > france_strength: +20` — both fire for strong nations.
- **Impact:** Threat ranking incorrectly equates moderately stronger opponents with overwhelming ones.

### Finding 65-2: Empty Region Confidence Defaults to "medium"
- **Severity:** MINOR
- **File:** `backend/game_logic/diplomatic_advisory.py:154-155`
- **Description:** Conquered nation with zero regions gets "medium" confidence instead of "low". No intel available but confidence says "medium".
- **Impact:** Misleading confidence for nations with no intelligence coverage.

### Finding 65-3: Unused War Score Calculation in Peace State
- **Severity:** MINOR
- **File:** `backend/game_logic/diplomatic_advisory.py:373`
- **Description:** `france_war_score` calculated unconditionally but only used inside `if state == "WAR"` block. Wasted function call for peace states.
- **Impact:** Minor performance — unnecessary function call.

### Pass 65 Assessment: Advisory System Fog Checks Are Correct
- Fog of war properly applied in threat/strength calculations. VERIFIED.
- Attack recommendations correctly gated by WAR state. VERIFIED.
- Division by zero protected. VERIFIED.
- None/empty handling correct. VERIFIED.

---

## Pass 66: Turn Processing Order Audit

### Pass 66 Assessment: CLEAN — No Bugs Found

The turn processing pipeline is well-engineered:
- **All 40+ processing steps verified** in correct dependency order
- **All cooldowns decremented** — 12 cooldown types confirmed
- **All per-turn state reset** — 12 flag types confirmed
- **No double processing** between advance_turn and enemy phase
- **No state pollution** from enemy AI to player
- **End-of-game check** runs after all processing
- **Key dependency chain verified:**
  - Income BEFORE gold-based checks
  - Treaty clauses AFTER income
  - Manpower regen BEFORE action reset
  - Tactical states AFTER enemy phase
  - Fog recalculation AFTER all events

---

## Pass 67: Coordinate/Grid System Audit

### Finding 67-1: Britain Capital (Netherlands) Missing is_capital Flag (Confirmed)
- **Severity:** CRITICAL
- **File:** `backend/models/region.py:347-354`
- **Description:** `NATION_CAPITALS['Britain'] = 'Netherlands'` but `REGIONS_DATA['Netherlands']['is_capital'] = False`. AI's `_is_capital_lost()` always returns False for Britain.
- **Evidence:** Netherlands has `is_capital: False` and `region_type: 'rural'` instead of `'capital'`.
- **Impact:** Britain's entire homeland defense mechanic (P2 priority) disabled. AI can never trigger capital recapture for Britain.

### Finding 67-2: Netherlands Supply Capacity Undersized (Rural Instead of Capital)
- **Severity:** MAJOR
- **File:** `backend/models/region.py:347-354`
- **Description:** Netherlands has `region_type='rural'` giving 15,000 supply capacity vs 50,000 for capitals. As Britain's capital, this creates a 35,000 troop deficit.
- **Evidence:** `SUPPLY_BY_TYPE['rural'] = 15000` vs `SUPPLY_BY_TYPE['capital'] = 50000`.
- **Impact:** Britain's capital can only support 15k troops — severe geometric disadvantage vs other nations.

### Finding 67-3: Dresden Region Type Mismatch (Town Instead of Capital)
- **Severity:** MAJOR
- **File:** `backend/models/region.py:473-481`
- **Description:** Dresden has `is_capital=True` (correct) but `region_type='town'` (wrong). Supply capacity 25,000 vs expected 50,000 for capitals.
- **Evidence:** `region_type: 'town'` but `is_capital: True` — inconsistent.
- **Impact:** Saxony's capital has 27,500 troop deficit vs expected capital supply.

### Pass 67 Assessment: Adjacency, Grid, Terrain All Verified Correct
- All 19 regions have symmetric adjacency. VERIFIED.
- All 19 regions have unique grid positions. VERIFIED.
- All regions reachable via BFS. VERIFIED.
- All 6 terrain types have complete modifier coverage (defense, movement, cavalry, bombardment). VERIFIED.
- All starting controllers are valid nations. VERIFIED.

---

## Pass 68: Diplomatic State Transition Audit

### Finding 68-1: Ultimatum WAR-to-PEACE Violates Adjacency
- **Severity:** CRITICAL
- **File:** `backend/commands/executor.py:11761`
- **Description:** Ultimatum acceptance directly transitions WAR to PEACE without going through ARMISTICE. Hierarchy states WAR to ARMISTICE to PEACE, but executor bypasses this.
- **Evidence:** `world.diplomatic_states[diplo_key] = "PEACE"` when `current == "WAR"`.
- **Impact:** Bypasses armistice cooldown and war cleanup. Battle records and war exhaustion not cleared.

### Finding 68-2: ARMISTICE Missing from _DOWNGRADE_ORDER
- **Severity:** CRITICAL
- **File:** `backend/game_logic/diplomacy.py:34-37`
- **Description:** `_DOWNGRADE_ORDER` only lists ALLIANCE through PEACE. ARMISTICE and WAR are missing, making them impossible to manually downgrade.
- **Impact:** Player cannot downgrade ARMISTICE treaties. Trapped state for manual treaty management.

### Finding 68-3: post_break_map Missing ARMISTICE and WAR Entries
- **Severity:** CRITICAL
- **File:** `backend/game_logic/diplomacy.py:1945-1952`
- **Description:** `post_break_map` has no entries for ARMISTICE or WAR. Both fall through to default "PEACE" via `.get(current_state, "PEACE")`.
- **Impact:** Breaking armistice defaults to PEACE without documented design intent. Breaking WAR (nonsensical) silently succeeds.

### Finding 68-4: Vassal Conquest No Pre-State Validation
- **Severity:** MAJOR
- **File:** `backend/game_logic/vassal.py:122-153`
- **Description:** `create_vassal_conquest()` doesn't validate current diplomatic state before creating vassal. `create_vassal_treaty()` does (lines 61-67 check VASSAL_MIN_STATES).
- **Impact:** Conquest vassalage can be created from any diplomatic state, including PEACE or ALLIANCE.

### Finding 68-5: Vassal Reconciliation Forces Invalid Downgrade
- **Severity:** MAJOR
- **File:** `backend/game_logic/vassal.py:195-197`
- **Description:** `_reconcile_vassal_diplomacy()` directly sets DEFENSIVE_ALLIANCE to PEACE, violating adjacency (should go through NON_AGGRESSION, OPEN_BORDERS).
- **Impact:** Vassal diplomacy creates non-adjacent state transitions.

### Finding 68-6: Armistice Expiry to WAR Skips cleanup_war_end
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomacy.py:1686-1691`
- **Description:** When armistice expires and reverts to WAR (low relations), no `cleanup_war_end()` is called. But when it expires to PEACE, cleanup IS called (line 1678). Inconsistent cleanup.
- **Impact:** Resuming war from expired armistice leaves stale battle records and war data intact.

### Finding 68-7: Vassal Rebellion/Release State Transitions Not Validated
- **Severity:** MINOR
- **File:** `backend/game_logic/vassal.py:424,846`
- **Description:** Rebellion (VASSAL to WAR) and release (VASSAL to PEACE) set states directly without calling `validate_transition()`. Transitions are valid per rules but bypass the validator.
- **Impact:** Inconsistent pattern — other transitions call validator.

### Finding 68-8: Nation Dissolution Sets All States to PEACE Without Cleanup
- **Severity:** MINOR
- **File:** `backend/models/world_state.py:1445-1448`
- **Description:** Dissolving a nation sets all its diplomatic states to PEACE without calling `cleanup_war_end()` for any WAR states. Battle records and war data left intact.
- **Impact:** Minor — nation is dissolved anyway.

### Finding 68-9: Cheat set_diplomatic_state Bypasses All Validation (Confirmed from Pass 52)
- **Severity:** MINOR
- **File:** `backend/commands/executor.py:14221`
- **Description:** Already reported as 52-3. Direct state set without validate_transition().

---

## Pass 69: Godot API Response Contract Audit

### Finding 69-1: /strategic_response Missing Popup Passthroughs
- **Severity:** CRITICAL
- **File:** `backend/main.py:1392-1435`
- **Description:** POST `/strategic_response` endpoint returns response without calling `_include_popup_passthroughs()`. Any diplomatic popups queued during strategic response are silently lost.
- **Impact:** Popup data lost on strategic command responses.

### Finding 69-2: GET /diplomatic_ledger Missing Popup Passthroughs and active_wars
- **Severity:** MAJOR
- **File:** `backend/main.py:1855-1865`
- **Description:** GET endpoint doesn't call `_include_popup_passthroughs()`. Missing popup keys and active_wars data. Player opening diplomatic ledger won't receive pending popups or war panel updates.
- **Impact:** Silent popup loss when player opens diplomatic ledger.

### Finding 69-3: GET /marshal_overview Missing Popup Passthroughs and active_wars
- **Severity:** MAJOR
- **File:** `backend/main.py:1919-1926`
- **Description:** Same as 69-2 but for marshal overview. GET endpoint missing all popup and war data.
- **Impact:** Silent popup loss when player opens marshal management.

### Finding 69-4: GET /ledger, /dispatch, /campaign_log Missing Popup Passthroughs
- **Severity:** MAJOR
- **File:** `backend/main.py:1696,1730,1744`
- **Description:** Three additional GET endpoints don't call `_include_popup_passthroughs()`. Any pending popups are invisible during these screens.
- **Impact:** Popup data lost when player views ledger, dispatch, or campaign log screens.

### Finding 69-5: Float Risk in get_filtered_game_state_summary
- **Severity:** MINOR
- **File:** `backend/models/world_state.py`
- **Description:** Need to verify `get_filtered_game_state_summary()` wraps all numeric fields with `int()`. CLAUDE.md Rule 2 requires all numbers to Godot as int().
- **Impact:** Potential Godot crash if any float leaks through.

---

## Pass 70: Enemy AI Decision Tree Deep Audit

### Finding 70-1: Ally Support Missing Diplomatic Checks (4 Locations)
- **Severity:** CRITICAL
- **File:** `backend/ai/enemy_ai.py:2788-2890`
- **Description:** `_find_ally_support_opportunity()` counts ALL non-same-nation marshals as enemies without checking `world.is_at_war()`. Neutral and allied nation marshals treated as threats.
- **Evidence:** Lines 2788-2793, 2796-2801, 2849-2854, 2885-2890 all filter `m.nation != nation` without `and world.is_at_war(nation, m.nation)`. Correct pattern exists at lines 4234-4242.
- **Impact:** AI sends support against neutral/allied marshals. Inflates threat assessment. Wastes AP on unnecessary repositioning.

### Finding 70-2: Division by Zero Risk in Ally Support Strength
- **Severity:** MINOR
- **File:** `backend/ai/enemy_ai.py:2820-2821`
- **Description:** `total_adjacent_threat` comparison assumes enemies_adjacent_to_ally is non-empty when condition evaluates. Edge case if list modified between check and use.
- **Impact:** Low actual risk (controlled flow), but defensive check missing.

### Finding 70-3: Random State Fragility in Mood Threshold
- **Severity:** MINOR
- **File:** `backend/ai/enemy_ai.py:482-483`
- **Description:** `_get_mood_adjusted_threshold()` uses `random.uniform()` without seeding protection. In future multi-threaded execution, random state could diverge.
- **Impact:** Currently single-threaded (no bug), but fragile design.

### Pass 70 Assessment: Core AI Decision Tree Is Sound
- Priority chain P0-P8 all correctly evaluate. VERIFIED.
- Division by zero protected throughout with `max(x, 1)` guards. VERIFIED.
- Retreat destinations validated (friendly, enemy-free). VERIFIED.
- Manpower checks before recruiting. VERIFIED.
- Artillery handling correct. VERIFIED.
- Wait spam limited to 2 consecutive waits. VERIFIED.
- Dead marshal filtering (strength <= 0) consistent. VERIFIED.

---

## Pass 71: Manpower/Recruitment System Audit

### Finding 71-1: Inconsistent Pool Key Access in _process_manpower_regen
- **Severity:** MAJOR
- **File:** `backend/models/world_state.py:2340-2342`
- **Description:** Infantry and cavalry pool access uses direct `pool["infantry"]` (crashes on missing key), while artillery uses safe `pool.get("artillery", 0)`. Inconsistent defensive coding.
- **Evidence:** Lines 2340-2341: direct access. Line 2342: `.get()` with default.
- **Impact:** Game crashes during end-of-turn regen if pool keys are missing due to corruption or backward compatibility.

### Finding 71-2: Morale Dilution Float Leakage Risk
- **Severity:** MINOR
- **File:** `backend/commands/executor.py:7997-8000`
- **Description:** Morale dilution formula uses integer division but inputs not explicitly cast to int. If `marshal.strength` or `marshal.morale` contain floats, weighted average could produce incorrect results.
- **Impact:** Potential Godot crash if float leaks through morale calculation.

### Finding 71-3: No Division-by-Zero Guard on Regen Rate
- **Severity:** MINOR
- **File:** `backend/commands/executor.py:7944`
- **Description:** `turns_until` calculation divides by `regen_rate` without asserting non-zero. Currently safe (constants are positive) but not defensively coded.
- **Impact:** Future crash risk if regen rates are ever made configurable.

### Pass 71 Assessment: Core Recruitment Logic Is Sound
- Player/AI race condition: None (single-threaded, sequential turns). VERIFIED.
- Pool capping: All types have MAX caps. VERIFIED.
- Negative pool prevention: Validation before subtraction. VERIFIED.
- AI pool checks before recruitment: Correct. VERIFIED.
- Serialization: Pools properly serialized/deserialized. VERIFIED.

---

## Pass 72: Strategic Order Edge Cases Audit

### Finding 72-1: PURSUE Path Not Persisted to order.path
- **Severity:** CRITICAL
- **File:** `backend/commands/strategic.py:953,981-994`
- **Description:** PURSUE handler recalculates path with fog-aware destination into a LOCAL `path` variable but never updates `order.path`. Stale path used for rerouting. Save/load restores wrong path.
- **Evidence:** Line 953 creates local `path`; `order.path` never assigned. Compare MOVE_TO at line 705 which correctly updates `order.path = new_path`.
- **Impact:** State corruption — stale path causes incorrect movement after save/load. Rerouting uses wrong path data.

### Finding 72-2: SUPPORT Path Not Persisted to order.path
- **Severity:** MAJOR
- **File:** `backend/commands/strategic.py:1609-1641`
- **Description:** Same pattern as 72-1. SUPPORT handler calculates local `path`, moves marshal, pops from local variable — never updates `order.path`.
- **Impact:** Save/load restores original pre-calculated path. UI "turns_remaining" incorrect after turn 1.

### Finding 72-3: HOLD Path Not Persisted to order.path
- **Severity:** MAJOR
- **File:** `backend/commands/strategic.py:1194-1214`
- **Description:** Same pattern. HOLD handler uses local `path` variable for movement, `order.path` remains stale.
- **Impact:** Identical to 72-2 — save/load corruption, incorrect UI display.

### Finding 72-4: issued_turn vs started_turn Inconsistency
- **Severity:** MAJOR
- **File:** `backend/commands/strategic.py:98,611,1162,1884`
- **Description:** Inconsistent field usage for order age. Lines 611, 1162 use `issued_turn or started_turn` fallback. Line 1884 uses ONLY `started_turn`. Two fields documenting the same concept.
- **Impact:** Off-by-one in timer calculations. SUPPORT orders may expire at wrong turn.

### Finding 72-5: last_contact_enemy/turn Not Serialized
- **Severity:** MAJOR
- **File:** `backend/commands/strategic.py` (set in _handle_blocked_path), `backend/models/marshal.py` (StrategicOrder)
- **Description:** `last_contact_enemy` and `last_contact_turn` fields are set during blocked path handling but NOT included in StrategicOrder's `to_dict()`/`from_dict()`. Lost on save/load.
- **Impact:** Save/load loses blocked-path contact state. Marshal may repeat failed path after load.

### Finding 72-6: MOVE_TO Path Recalculation Inefficiency
- **Severity:** MINOR
- **File:** `backend/commands/strategic.py:696-705`
- **Description:** Modifies `order.path` in-place (pop) before checking if empty and recalculating. Correct but inefficient mutation pattern.
- **Impact:** No functional bug, minor code quality.

---

## Pass 73: Trust/Relationship Formula Audit

### Finding 73-1: Direct trust._value Access (Encapsulation Violation)
- **Severity:** CRITICAL
- **File:** `backend/game_logic/vassal.py:750`, `backend/main.py:1985,2072`
- **Description:** Three code paths directly assign to `trust._value`, bypassing Trust.modify() and any side effects (redemption_pending flag clearing). Vassal assimilation (line 750) is production code, not just debug.
- **Evidence:** `marshal.trust._value = ASSIMILATION_TRUST` bypasses clamping, side effects.
- **Impact:** Redemption events never triggered for vassal-assimilated marshals. Future Trust side effects bypassed.

### Finding 73-2: Inconsistent Trust Modification Patterns (3 Different APIs)
- **Severity:** MAJOR
- **File:** Multiple files
- **Description:** Three patterns exist: (A) `trust.modify()` — most files, (B) `marshal.modify_trust()` — disobedience only, (C) direct `_value` — vassal/debug. Only pattern B handles redemption side effects. 14 of 17 trust modifications use wrong pattern.
- **Impact:** Maintenance risk. Redemption flag only handled in disobedience path, not combat/strategic.

### Finding 73-3: Missing Self-Relationship Guard
- **Severity:** MAJOR
- **File:** `backend/models/marshal.py:549-573`
- **Description:** `set_relationship()` and `modify_relationship()` don't prevent self-relationships. `ney.set_relationship("Ney", 2)` succeeds and pollutes the relationships dict.
- **Evidence:** No `if other_name == self.name: return` guard in either method.
- **Impact:** Data pollution if any caller accidentally passes self-name.

### Finding 73-4: Relationship Formula Variance Asymmetry
- **Severity:** MINOR
- **File:** `backend/game_logic/relationship.py:85-97`
- **Description:** WIN formula base (30) vs LOSS formula base (15) means variance [-10,+10] has different impact. LOSS needs variance > 25 to reach threshold 50 — almost impossible.
- **Impact:** Relationship changes from losses are extremely rare. May be intentional but undocumented.

### Finding 73-5: Dead Defensive Code in Trust Type Check
- **Severity:** MINOR
- **File:** `backend/commands/executor.py:9488`
- **Description:** `old_trust = marshal.trust.value if hasattr(marshal.trust, 'value') else marshal.trust` — fallback unreachable since Trust always has `.value`.
- **Impact:** Dead code — confusing but harmless.

---

## Pass 74: Cavalry/Artillery Mechanics Audit

### Pass 74 Assessment: CLEAN — No Bugs Found

All cavalry and artillery mechanics verified correct:
- Terrain charge blocking enforced at all 3 points (glorious charge, reckless auto-charge, reckless popup). VERIFIED.
- Cavalry limits (3-turn defensive cap) with trust penalties. VERIFIED.
- Artillery movement flag lifecycle (set on move, cleared at turn start, blocks attacks). VERIFIED.
- Bombardment damage includes all modifiers (terrain, square, skill). VERIFIED.
- 50% casualty reduction correctly applies only with non-artillery allies. VERIFIED.
- Square formation interactions (+50% vs artillery, -40% vs cavalry). VERIFIED.
- Movement ranges (cavalry 2, artillery 1, infantry 1). VERIFIED.
- Overwatch penalty (3% per enemy artillery). VERIFIED.
- All serialization requirements met. VERIFIED.
- Auto-bombardment eligibility checks comprehensive. VERIFIED.

---

## Pass 75: Vindication/Authority System Audit

### Finding 75-1: defiance_succeeded() Reads Non-Existent "won" Field
- **Severity:** CRITICAL
- **File:** `backend/commands/defiance.py:141`
- **Description:** `defiance_succeeded()` reads `battle_result.get("attacker", {}).get("won", False)` but combat.py's resolve_combat() never sets a "won" field. The .get() default is always False, meaning **defiant attacks always evaluate as "marshal was wrong"**.
- **Evidence:** combat.py:733-746 defines result with `casualties`, `remaining`, `morale`, `forced_retreat` — no "won" field.
- **Impact:** Defiance attacks can NEVER succeed via this function. Marshals who defy to attack always receive the "Wrong" outcome (trust -5, vindication reset, authority +3). Inverts the entire defiance reward mechanic.

### Finding 75-2: Authority Threshold Inconsistency Between Functions
- **Severity:** MINOR
- **File:** `backend/models/authority.py:309,149-151`
- **Description:** `check_excessive_trust()` uses 0.80/0.65 thresholds while `get_trust_gain_modifier()` uses 0.80/0.60 thresholds. At exactly 0.60 ratio: no penalty in excessive trust, but 0.75x modifier in gain. Inconsistent boundary semantics.
- **Impact:** Edge case at exactly 60% trust ratio gets different treatment between the two functions.

### Pass 75 Assessment: Defiance Chance Formula and Fallback Table Verified Correct
- Base chances: MODERATE 5%, STRONG 15%, EXTREME 35%. VERIFIED.
- Personality and authority modifiers applied correctly. VERIFIED.
- Fallback table entries all reachable. VERIFIED.
- Vindication serialization complete. VERIFIED.

---

## Pass 76: LLM Integration Audit

### Finding 76-1: No Per-Session Cost Cap for LLM Calls
- **Severity:** MAJOR
- **File:** `backend/ai/providers.py:274-279`
- **Description:** Cost estimation documented (~$0.0004/parse) but no implementation to track cumulative costs, rate-limit by cost, or reject after budget threshold. Player spam could incur uncapped API costs.
- **Impact:** No cost control in production deployment. Mitigated by fast parser handling 90%+ of commands.

### Finding 76-2: No Input Length Validation Before LLM Call
- **Severity:** MAJOR
- **File:** `backend/ai/llm_client.py:149`
- **Description:** Player commands not validated for length before LLM API call. Extremely long commands waste tokens/API costs.
- **Impact:** Token waste and potential prompt overflow (though Claude's context is 200k).

### Finding 76-3: User Input Directly Interpolated into LLM Prompt
- **Severity:** MINOR
- **File:** `backend/ai/prompt_builder.py:448`
- **Description:** Player command text (`raw_input`) directly interpolated into prompt without sanitization. Prompt injection mitigated by validation layer catching hallucinated actions/marshals, plus mock parser fallback.
- **Impact:** Low in practice — validation layer catches hallucinations. But input should be JSON-escaped.

### Pass 76 Assessment: LLM Security Overall Good
- API key properly isolated from responses. VERIFIED.
- 5-second timeout configured. VERIFIED.
- All API errors gracefully degrade to fast parser. VERIFIED.
- 429 rate limiting handled (falls back to fast parser). VERIFIED.
- Parse result validation catches hallucinated actions/marshals. VERIFIED.

---

## Pass 77: Godot Popup Flow Deep Audit

### Finding 77-1: Diplomatic Popup Early Returns Skip ALL State Updates
- **Severity:** CRITICAL
- **File:** `godot-client/project-sovereign/scripts/main.gd:786-841`
- **Description:** When diplomatic popups (incoming_proposal, diplomatic_objection, sabotage_discovery, talleyrand_redemption, vassal_rebellion) are shown, the function returns immediately WITHOUT updating gold, manpower, map, notifications, or active_wars. Normal flow at lines 862-943 handles all these updates.
- **Evidence:** 5 separate early return points (lines 787-790, 793-796, 826-829, 832-835, 838-841) all skip lines 866-943.
- **Impact:** Player sees stale state (gold, territory, notifications, war panel) until popup is dismissed. Data consistency broken.

### Finding 77-2: Proposal Confirm Popup Missing State Updates
- **Severity:** MAJOR
- **File:** `godot-client/project-sovereign/scripts/main.gd:800-813`
- **Description:** Proposal confirm popup also returns without state updates. Same pattern as 77-1.
- **Impact:** Stale UI during proposal confirmation flow.

### Finding 77-3: Glorious Charge Dialog State Loss
- **Severity:** MAJOR
- **File:** `godot-client/project-sovereign/scripts/main.gd:763-768`
- **Description:** Glorious charge dialog returns without state updates. Gold, manpower, map, notifications, active_wars all stale.
- **Impact:** War panel not initialized if attack triggers coalition.

### Finding 77-4: Capture Choice Dialog State Loss
- **Severity:** MAJOR
- **File:** `godot-client/project-sovereign/scripts/main.gd:777-779`
- **Description:** Capture choice dialog (plunder/secure) returns without state updates.
- **Impact:** Capture conquest not reflected in UI until choice made.

### Finding 77-5: Clarification/Interrupt Popups Skip War Panel Update
- **Severity:** MAJOR
- **File:** `godot-client/project-sovereign/scripts/main.gd:815-823`
- **Description:** Clarification and strategic interrupt popups return without calling `_process_active_wars()`.
- **Impact:** War panel stale during clarification flows.

### Finding 77-6: war_detail_popup Missing from _is_modal_dialog_open()
- **Severity:** MAJOR
- **File:** `godot-client/project-sovereign/scripts/main.gd:2831-2870`
- **Description:** Modal dialog check includes 17 popup types but omits `war_detail_popup`. Player can open diplomacy wizard (F1) or marshal management (G) while examining war details.
- **Impact:** Popup layering and state confusion.

### Finding 77-7: Coalition Popup Dismissal Doesn't Refresh War Panel
- **Severity:** MAJOR
- **File:** `godot-client/project-sovereign/scripts/main.gd:2726-2730`
- **Description:** Coalition declaration popup dismissal handler doesn't call `_process_active_wars()`.
- **Impact:** War panel not refreshed after coalition declared.

### Finding 77-8: Active Wars Null Chain Risk
- **Severity:** MINOR
- **File:** `godot-client/project-sovereign/scripts/main.gd:2999-3018`
- **Description:** If backend sends `"wars": null` instead of `[]`, `_cached_wars.is_empty()` at line 3012 crashes.
- **Impact:** Low risk — default `[]` protects unless backend explicitly sends null.

### Finding 77-9: War Detail Refresh Without Data Validation
- **Severity:** MINOR
- **File:** `godot-client/project-sovereign/scripts/main.gd:3014-3016`
- **Description:** `war_detail_popup.refresh_if_open(active_wars_data)` called without verifying data structure validity.
- **Impact:** Could show stale data if structure malformed.

### Finding 77-10: Input State Race on Rapid Popup Dismissals
- **Severity:** MINOR
- **File:** `godot-client/project-sovereign/scripts/main.gd` (multiple)
- **Description:** No input state guard during rapid popup chains. set_input_enabled(true/false) calls can interleave unpredictably.
- **Impact:** Very unlikely due to HTTP request-response ordering.

---

## Pass 78: Constructor/Init Audit

### Pass 78 Assessment: CLEAN — No Bugs Found

All model class constructors verified correct:
- **Marshal.__init__:** 95+ fields, all serialized. VERIFIED.
- **WorldState.__init__:** 90+ fields, all persistent fields serialized. VERIFIED.
- **Region.__init__:** 13 fields, complete coverage. VERIFIED.
- **DiplomaticRepresentative.__init__:** 6 fields, complete. VERIFIED.
- **RegionIntel.__init__:** 10 fields, complete. VERIFIED.
- No mutable defaults used as function parameters. VERIFIED.
- All transient fields accessed with safe `getattr()` defaults. VERIFIED.
- Serialization enforcement tests: 16/16 passing. VERIFIED.


---

## Pass 47: Acceptance Formula Deep Dive

### Finding 47-1: AP Sweetener Value Inflated 125%
- **Severity:** CRITICAL
- **File:** `backend/game_logic/diplomacy.py:215`
- **Description:** AP sweetener clause valued at 18 acceptance points, but DIPLOMACY_SPEC §7 specifies 8. This 125% inflation makes AP clauses dramatically over-weighted in counter-offers.
- **Evidence:** Code: `"AP": 18` in sweetener value table vs spec value of 8.
- **Proposed Fix:** Change AP sweetener value from 18 to 8.
- **Test Coverage:** No test validates sweetener values against spec.

### Finding 47-2: Sweetener Cap 50% Over Spec
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomacy.py:221`
- **Description:** Total sweetener acceptance cap is 60, but spec says 40. Combined with Finding 47-1, AI counter-offers are far more generous than designed.
- **Evidence:** Code: `min(total_sweetener, 60)` vs spec: "capped at 40 total sweetener points."
- **Proposed Fix:** Change cap from 60 to 40.
- **Test Coverage:** No test validates cap against spec.

### Finding 47-3: Base DP Generation Rate Discrepancy
- **Severity:** MINOR
- **File:** `backend/game_logic/diplomacy.py`
- **Description:** Base DP generation is 3/turn; spec may intend 2. Needs spec cross-reference to confirm.
- **Evidence:** Code generates 3 DP per turn for all nations.
- **Proposed Fix:** Verify against DIPLOMACY_SPEC and adjust if needed.
- **Test Coverage:** Tested functionally but not validated against spec value.

---

## Pass 48: Popup Data Flow Audit

### Finding 48-1: Talleyrand Objection Popup Field Mismatch
- **Severity:** CRITICAL
- **File:** `backend/commands/executor.py` → `godot-client/project-sovereign/scripts/talleyrand_objection_popup.gd`
- **Description:** Backend sends `{type, severity, message, action, target_nation}` but Godot popup expects `{concern_level, objection_text, defiance_risk, proposal_summary}`. Fields don't match — popup would display empty or crash.
- **Evidence:** Executor builds dict with `type`/`severity`/`message` keys; Godot `.gd` reads `concern_level`/`objection_text`/`defiance_risk`.
- **Proposed Fix:** Align backend output keys with Godot expectations (or add translation layer in main.py).
- **Test Coverage:** No integration test validates popup data shape.

### Finding 48-2: Alliance Paradox Popup Has No Godot Handler
- **Severity:** CRITICAL
- **File:** `backend/main.py:158`, `godot-client/project-sovereign/scripts/main.gd`
- **Description:** Backend generates `alliance_paradox_popup` data and has a TODO comment at line 158, but no Godot script handles this popup type. The data is sent but silently ignored by the frontend.
- **Evidence:** `main.py` line 158: `# TODO: alliance paradox popup handler`. No `.gd` file references `alliance_paradox_popup`.
- **Proposed Fix:** Implement alliance paradox popup in Godot (new scene + script) or route through existing popup.
- **Test Coverage:** None.

### Finding 48-3: Four POST Endpoints Missing Popup Passthroughs
- **Severity:** MAJOR
- **File:** `backend/main.py`
- **Description:** `/save`, `/load`, `/delete_save`, `/notifications/dismiss` POST endpoints never call `_include_popup_passthroughs()`. Any diplomatic popups queued during these operations are silently lost.
- **Evidence:** These 4 endpoints return responses directly without passthrough call.
- **Proposed Fix:** Add `_include_popup_passthroughs(response, world)` to all 4 endpoints.
- **Test Coverage:** No test checks passthrough on these endpoints.

---

## Pass 49: Authority & Trust System Audit

### Finding 49-1: Excessive Trust Threshold Off-by-One
- **Severity:** MAJOR
- **File:** `backend/models/authority.py:309,311`
- **Description:** Excessive trust check uses `>` instead of `>=`. A marshal with exactly 80 trust does NOT trigger "excessive trust" effects, despite 80 being the threshold boundary.
- **Evidence:** Code: `if marshal.trust.value > 80:` — should be `>= 80` per threshold design intent.
- **Proposed Fix:** Change `>` to `>=` at lines 309 and 311.
- **Test Coverage:** No test checks the exact boundary value of 80.

### Finding 49-2: Strategic Paths Bypass Redemption Flag
- **Severity:** MINOR
- **File:** `backend/commands/strategic.py`
- **Description:** Strategic order execution calls `marshal.trust.modify()` directly instead of `marshal.modify_trust()`, which bypasses the redemption event flag check. Trust changes from strategic orders won't trigger redemption events.
- **Evidence:** Direct `.trust.modify()` calls skip the marshal-level wrapper that checks redemption state.
- **Proposed Fix:** Route through `marshal.modify_trust()` instead.
- **Test Coverage:** No test validates redemption interaction with strategic orders.

---

## Pass 50: War Declaration Cascade Audit

### Finding 50-1: Alliance Paradox Honor/Break Doesn't Deduct DP
- **Severity:** CRITICAL
- **File:** `backend/commands/executor.py:12952-13005`
- **Description:** When player chooses to honor or break an alliance paradox, the handler doesn't deduct diplomatic points. War declarations via normal path cost DP, but the paradox path is free.
- **Evidence:** Neither `honor_alliance_paradox` nor `break_alliance_paradox` handlers contain any DP deduction logic.
- **Proposed Fix:** Add DP deduction matching normal war declaration cost.
- **Test Coverage:** No test checks DP after paradox resolution.

### Finding 50-2: No Self-War Prevention in declare_war()
- **Severity:** CRITICAL
- **File:** `backend/game_logic/diplomacy.py:915`
- **Description:** `declare_war()` has no guard against a nation declaring war on itself. If called with `from_nation == target_nation` (e.g., via bug in AI or cascade), it would create a self-referential war entry.
- **Evidence:** No `if from_nation == target_nation: return` guard at function entry.
- **Proposed Fix:** Add early return guard: `if from_nation == target_nation: return {"success": False, "message": "Cannot declare war on self"}`.
- **Test Coverage:** No test attempts self-war.

### Finding 50-3: cascade_triggered Field Is Dead Code
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomacy.py`
- **Description:** The `cascade_triggered` field on war entries is set during cascade processing but never read anywhere in the codebase. It's serialized and persisted but serves no purpose.
- **Evidence:** Grep for `cascade_triggered` shows only write sites, no read sites outside serialization.
- **Proposed Fix:** Remove field or implement intended cascade-tracking behavior.
- **Test Coverage:** N/A — dead code.

### Finding 50-4: Vassal Auto-Join in Cascade Never Called
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomacy.py`, `backend/game_logic/vassal.py`
- **Description:** Offensive cascade logic explicitly skips vassals ("vassals handle separately"), but the separate vassal auto-join-war function is never called from the cascade path. Vassals of a warring lord don't automatically join wars.
- **Evidence:** Cascade code skips vassals; no call to vassal auto-join from declare_war or cascade handlers.
- **Proposed Fix:** Add vassal auto-join call in the cascade path after lord enters war.
- **Test Coverage:** No test verifies vassal behavior during cascade.

### Finding 50-5: Cascade Events Use Partial Visibility Check
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomacy.py`
- **Description:** Cascade war declarations are filtered through fog of war. If the player has limited visibility of a cascading nation, they won't be notified that a new war started — even if they're affected by it.
- **Evidence:** Cascade event notifications pass through fog filter before reaching player.
- **Proposed Fix:** War declarations affecting the player or their allies should bypass fog filter for the declaration notification.
- **Test Coverage:** No test checks fog interaction with cascade notifications.

---

## Pass 79: Diplomacy Wizard Integration Audit

### Finding 79-1: Wizard Can Be Opened While Already Processing HTTP Request
- **Severity:** CRITICAL
- **File:** `godot-client/project-sovereign/scripts/diplomacy_wizard.gd`
- **Description:** No guard prevents opening the wizard while an HTTP request is already in flight. F1 pressed twice rapidly or F1 during war panel handoff creates duplicate HTTPRequest calls. Second response overwrites first, corrupting wizard state.
- **Impact:** Duplicate commands sent, state corruption, potential crash on response handling.

### Finding 79-2: Wizard Doesn't Check pending_diplomatic_dialogue Before Opening
- **Severity:** MAJOR
- **File:** `godot-client/project-sovereign/scripts/diplomacy_wizard.gd`
- **Description:** Wizard opens without checking if a diplomatic dialogue is pending on the backend. If Talleyrand is mid-conversation, wizard commands will be blocked by the dialogue guard in executor.py, showing confusing "Talleyrand awaiting response" errors.
- **Impact:** Poor UX — player enters wizard, selects action, gets cryptic error.

### Finding 79-3: War Panel Handoff (open_for_nation) Doesn't Check Dialogue Pending State
- **Severity:** MAJOR
- **File:** `godot-client/project-sovereign/scripts/diplomacy_wizard.gd`, `war_detail_popup.gd`
- **Description:** `open_for_nation()` called from war detail popup doesn't verify dialogue state. Same issue as 79-2 but triggered from war panel negotiate button.
- **Impact:** Negotiate button in war panel leads to blocked commands.

### Finding 79-4: Input Re-Enable Timing After Wizard Command Execution
- **Severity:** MAJOR
- **File:** `godot-client/project-sovereign/scripts/diplomacy_wizard.gd`
- **Description:** After wizard sends command to main.gd via handoff, input is re-enabled before the command response returns. Player can type new commands while wizard's command is still processing.
- **Impact:** Race condition — player input interleaves with wizard command response.

---

## Pass 80: Error Message Quality Audit

### Finding 80-1: "Game state error" Messages With Zero Diagnostic Value
- **Severity:** CRITICAL
- **File:** `backend/main.py` (multiple endpoints)
- **Description:** At least 3 POST endpoint handlers return generic "Game state error" when world state is None. No indication of which endpoint, what operation was attempted, or recovery steps.
- **Impact:** Production debugging impossible — all failures look identical.
- **Proposed Fix:** Include endpoint name and context: `f"Game state error: no active game in /{endpoint_name}. Start or load a game first."`

### Finding 80-2: 14+ "No world state" Vague Internal Errors Exposed to Players
- **Severity:** MAJOR
- **File:** `backend/main.py` (14+ locations)
- **Description:** Internal "No world state" error message leaked directly to frontend. Players see developer jargon instead of actionable guidance. Same message for GET and POST endpoints despite different contexts.
- **Impact:** Poor player experience. "No world state" is meaningless to non-developers.

### Finding 80-3: "paradox data missing" / "proposal data missing" Internal Jargon Exposed
- **Severity:** MAJOR
- **File:** `backend/main.py` (respond_to_* endpoints)
- **Description:** Error responses contain internal field names like "paradox data missing", "proposal data missing", "no pending objection". These are developer-facing error descriptions exposed raw to the player.
- **Impact:** Confusing player-facing error messages with internal terminology.

---

## Pass 81: Supply/Attrition System Audit

### Finding 81-1: Misleading Comment in enemy_ai.py
- **Severity:** MINOR
- **File:** `backend/ai/enemy_ai.py`
- **Description:** Comment claims "5% attrition tier" when actual supply attrition rate at that tier is 0.75% per turn. Misleading documentation could cause incorrect future modifications.
- **Impact:** Code comprehension — no gameplay effect.

### Pass 81 Assessment: Supply System CLEAN
- All supply capacity calculations verified correct. VERIFIED.
- Attrition tiers correctly graduated (0%, 0.5%, 0.75%, 1.5%, 3%). VERIFIED.
- Enemy AI correctly accounts for supply in movement scoring. VERIFIED.
- No integer overflow or float leak risks in attrition math. VERIFIED.

---

## Pass 82: Occupation/Fortification System Audit

### Finding 82-1: Fortified Marshals Can Move Via Strategic Execution Bypass
- **Severity:** CRITICAL
- **File:** `backend/commands/executor.py:1675`
- **Description:** Fortification movement block checks `if marshal.is_fortified` but strategic order execution sets `command["_strategic_execution"] = True` which bypasses this check. A fortified marshal with a pending MOVE_TO order will move, silently losing fortification without the expected "break fortification" confirmation.
- **Evidence:** `_strategic_execution` flag bypasses multiple pre-validation checks including the fortify block.
- **Impact:** Fortification state becomes meaningless for marshals with strategic orders. Player builds fortification expecting to hold position, but strategic order silently moves them.

### Finding 82-2: Fortified Marshals Can Attack Via Strategic Execution Bypass
- **Severity:** CRITICAL
- **File:** `backend/commands/executor.py`
- **Description:** Same bypass as 82-1 but for attack actions. PURSUE strategic order can trigger attack on arrival, bypassing fortify block.
- **Impact:** Fortification doesn't prevent combat engagement via strategic paths.

### Finding 82-3: No Occupation Check in Fortification Logic
- **Severity:** MODERATE
- **File:** `backend/commands/executor.py`
- **Description:** A marshal can fortify while occupying a region (occupation + fortification simultaneously). These are conceptually conflicting states — fortification implies defensive preparation while occupation implies active control assertion.
- **Impact:** Minor gameplay inconsistency. Both states provide defensive bonuses that stack.

### Finding 82-4: Fortification State Not Fully Cleared on Capture Completion
- **Severity:** MODERATE
- **File:** `backend/commands/executor.py`
- **Description:** When a marshal completes capture of a region, fortification state from the previous position is not explicitly cleared. Relies on implicit state management rather than explicit cleanup.
- **Impact:** Edge case — fortification should be cleared on any position change.

---

## Pass 83: Dead Code Identification

### Finding 83-1: Three Orphaned Battle Tracking Methods in WorldState
- **Severity:** MAJOR
- **File:** `backend/models/world_state.py:1296,1347,1380`
- **Description:** `start_or_continue_battle()`, `end_battle_if_needed()`, and `get_battle_name()` form a complete battle naming/tracking subsystem (~90 lines) but are never called. Combat system handles battles without these methods.
- **Evidence:** Grep for all three method names returns only definitions. `active_battles` and `battle_history` dicts initialized but never populated through these methods.

### Finding 83-2: Three Orphaned Pathfinding/Threat Methods in WorldState
- **Severity:** MAJOR
- **File:** `backend/models/world_state.py:1763,1793,1820`
- **Description:** `_get_regions_within_range()`, `_has_valid_path()`, and `_region_is_threatened()` are defined but never called. Early-phase infrastructure superseded by enemy_ai.py implementations.
- **Evidence:** Grep returns only definitions -- zero call sites.

### Finding 83-3: `_find_best_action` in EnemyAI Is Dead Code
- **Severity:** MAJOR
- **File:** `backend/ai/enemy_ai.py:1058`
- **Description:** 36-line method superseded by `_select_next_marshal_action()`. Never called.
- **Evidence:** Grep returns only the definition.

### Finding 83-4: `defender_coord` Computed But Never Used in `_execute_attack`
- **Severity:** MAJOR
- **File:** `backend/commands/executor.py:4238`
- **Description:** `defender_coord` assigned from `_calculate_coordination_context()` (expensive call iterating marshals) but never read. Only `attacker_coord` is used. Wasted computation on every attack.
- **Evidence:** Grep for `defender_coord` in executor.py returns only the assignment.

### Finding 83-5: `resolve_battle_vindication` on CommandExecutor Is Orphaned
- **Severity:** MAJOR
- **File:** `backend/commands/executor.py:13970`
- **Description:** Wraps `world.vindication_tracker.resolve_battle()` but never called. Dead wrapper.
- **Evidence:** Grep returns only definition.

### Finding 83-6: `VindicationTracker.apply_decay()` Is Dead
- **Severity:** MAJOR
- **File:** `backend/commands/vindication.py:227`
- **Description:** `apply_decay()` defined but never called. WorldState has `_process_vindication_decay()` called from `advance_turn()` -- a duplicate implementation.
- **Evidence:** Grep for `apply_decay` finds only the definition.

### Finding 83-7: Three Flavor Text Functions in enemy_ai.py Never Called
- **Severity:** MINOR
- **File:** `backend/ai/enemy_ai.py:5477,5505,5531`
- **Description:** `get_casualty_description()`, `get_victory_description()`, `get_morale_flavor()` -- ~70 lines. Battle reporting handled by `battle_report.py` instead.

### Finding 83-8: `get_ambiguity_behavior` and `should_skip_validation` Never Called
- **Severity:** MINOR
- **File:** `backend/ai/validation.py:186,209`
- **Description:** Two utility functions with zero call sites.

### Finding 83-9: `_get_stalemate_turns` in ai_diplomacy.py Never Called
- **Severity:** MINOR
- **File:** `backend/game_logic/ai_diplomacy.py:354`
- **Description:** Getter superseded by direct `_update_stalemate_counter()` access.

### Finding 83-10: `get_stance_display` on Marshal Never Called
- **Severity:** MINOR
- **File:** `backend/models/marshal.py:946`
- **Description:** Returns formatted stance string but frontend builds its own display.

### Finding 83-11: `full_game.py` Is an Entire Dead File
- **Severity:** MINOR
- **File:** `backend/full_game.py`
- **Description:** Early-phase `CommandExecutor` class (16 lines), never imported. Leftover prototype.

### Finding 83-12: `test_new_features.py` in commands/ Is Dead Test File in Production Code
- **Severity:** MINOR
- **File:** `backend/commands/test_new_features.py`
- **Description:** Test/demo file placed in production `backend/commands/` directory. Never imported.

### Finding 83-13: `defiant_command` Assigned But Never Used (Two Locations)
- **Severity:** MINOR
- **File:** `backend/commands/executor.py:10763,13479`
- **Description:** In two objection handlers, `defiant_command` dict constructed but never used. Leftover from earlier implementation.

### Finding 83-14: `_get_fogged_strength_display` in diplomatic_advisory.py Never Called
- **Severity:** MINOR
- **File:** `backend/game_logic/diplomatic_advisory.py:610`
- **Description:** Fog-filtered strength display helper, superseded by numeric version `_get_fogged_strength`.

### Finding 83-15: `get_coalition_template` and `resolve_coalition_template` Never Called
- **Severity:** MINOR
- **File:** `backend/game_logic/diplomatic_templates.py:940,945`
- **Description:** Two accessor functions for `COALITION_TEMPLATES` dict, both dead.

### Finding 83-16: `get_valid_actions` and `find_action_in_valid` in disobedience.py Never Called
- **Severity:** MINOR
- **File:** `backend/commands/disobedience.py:335,468`
- **Description:** V1 disobedience infrastructure (130+ lines) superseded by V2 objection system.

---

## Pass 84: Test Coverage vs Critical Findings Cross-Reference

### Summary: 14 of 20 Critical Findings Have Zero Test Coverage

| Status | Count | Findings |
|--------|-------|----------|
| **Zero coverage** | 14 | 1, 2, 3, 4, 5, 7, 8, 11, 12, 13, 14, 15, 16, 20 |
| **Tests encode current (possibly wrong) values** | 2 | 9, 10 |
| **Partial coverage** | 1 | 18 |
| **Tests exist but miss integration path** | 1 | 6 |
| **Untestable in Python** | 1 | 17 (Godot GDScript) |
| **Has functional test but masks bug** | 1 | 19 |

### Detailed Results

| Finding | Bug | Has Test? | Gap |
|---------|-----|-----------|-----|
| 1 | VASSAL missing from _DOWNGRADE_ORDER | NO | Need downgrade-from-VASSAL test |
| 2 | Coordinated battles record 0 casualties | NO | Need integration test with non-zero casualties |
| 3 | Defense modifier inverted by division | NO | Need test: higher stance modifier reduces casualties |
| 4 | _ratify_treaty skips create_vassal_treaty | NO | Need _ratify_treaty with vassalage proposal |
| 5 | nation_manpower undefined | NO | Need test exercising wrong-attribute path |
| 6 | defiance_succeeded() reads "won" field | PARTIAL | Tests use synthetic dicts with "won" -- masks bug |
| 7 | Fortified marshal moves via strategic | NO | Need _strategic_execution=True on fortified marshal |
| 8 | PURSUE path not persisted | NO | Need order.path assertion after PURSUE |
| 9 | AP sweetener 18 vs spec 8 | YES* | Test encodes 18, spec says 8 |
| 10 | Sweetener cap 60 vs spec 40 | YES* | Test encodes 60, spec says 40 |
| 11 | Alliance paradox free (no DP) | NO | Need DP check after paradox resolution |
| 12 | No self-war prevention | NO | Need declare_war(nation, nation) test |
| 13 | AI fog leak get_enemies_of_nation | NO | Need fog-aware AI decision test |
| 14 | Vassal battle field mismatch | NO | Need record_battle -> vassal loyalty test |
| 15 | /strategic_response missing passthroughs | NO | Need endpoint test with pending popup |
| 16 | Britain Netherlands missing is_capital | NO | Need Netherlands.is_capital assertion |
| 17 | Godot popup early returns skip updates | N/A | Godot-side, untestable in Python |
| 18 | Missing armistice_stalemate handler | PARTIAL | AI generation tested, template lookup not |
| 19 | release_vassal missing from VALID_ACTIONS | NO | Need VALID_ACTIONS membership assertion |
| 20 | Modding validator accepts float strength | NO | Need float strength validation test |

---

## Pass 85: Godot .tscn Scene Tree Validation

### Pass 85 Assessment: CLEAN -- No Findings

Audit scope: 28 .tscn scene files, 30 .gd scripts, 155+ @onready node paths, 80+ signal connections, 28 load() scene references.

- **Node paths:** All 155+ @onready references match .tscn scene trees. VERIFIED.
- **Signal connections:** All 80+ .connect() calls reference existing methods. VERIFIED.
- **Scene references:** All 28 load("res://scenes/...") paths exist on disk. VERIFIED.
- **CanvasLayer ordering:** No conflicts. Hierarchy: 25 -> 30 -> 50 -> 75 -> 100 -> 101. VERIFIED.

---

## Pass 86: DIPLOMACY_SPEC Formula Compliance (Remaining Sections)

### Finding 86-1: Post-Break State Map Drops Two Levels Instead of One
- **Severity:** MAJOR
- **Spec reference:** S7d -- "Breaking a treaty returns to the state one level below the broken treaty."
- **Code reference:** `backend/game_logic/diplomacy.py:1946-1948`
- **Description:** ALLIANCE breaks to NON_AGGRESSION (should be DEFENSIVE_ALLIANCE). DEFENSIVE_ALLIANCE breaks to OPEN_BORDERS (should be NON_AGGRESSION). Both drop two levels instead of one.
- **Impact:** Treaty breaks more punishing than designed. Gradual degradation eliminated.

### Finding 86-2: Casus Belli Does Not Halve Threat on War Declaration
- **Severity:** MAJOR
- **Spec reference:** S5c -- "If target broke treaty/attacked ally/controls core territory, threat +10 instead of +20."
- **Code reference:** `backend/game_logic/diplomacy.py:969-972` -- `add_threat(world, 20, "war_declaration")` unconditional.
- **Description:** `declare_war()` correctly halves relation penalties with casus_belli but always applies full +20 threat. Spec says +10 with casus belli.
- **Impact:** Justified wars generate same coalition threat as unprovoked aggression.

### Finding 86-3: Vassal Garrison Loyalty Bonus -- Base 2 Instead of Spec 5
- **Severity:** MAJOR
- **Spec reference:** S8b -- "Garrison in vassal capital: +5" + "Garrison strength bonus: +min(garrison_troops // 5000, 3)" (max +8)
- **Code reference:** `backend/game_logic/vassal.py:239` -- `garrison_bonus = min(4, 2 + min(garrison_troops // 5000, 3))`
- **Description:** Spec: base +5, cap +8. Code: base +2, cap +4. Maximum garrison loyalty is half spec value.
- **Impact:** SATELLITE vassals with garrisons drift toward instability instead of being stable as designed.

### Finding 86-4: DP Skill Bonus Threshold -- Code Uses >= 8 Instead of Spec 10
- **Severity:** MINOR
- **Spec reference:** S4a -- "Skill 10 (Talleyrand): +1 bonus DP"
- **Code reference:** `backend/game_logic/diplomacy.py:860` -- `skill_bonus = 1 if diplomat and diplomat.skill >= 8 else 0`
- **Description:** Spec says only skill 10 gets +1 DP. Code gives +1 to skill >= 8, including Metternich (9). Austria gets 4 DP/turn instead of spec 2.
- **Impact:** Austria diplomatically twice as strong as designed.

### Finding 86-5: Diplomat Skill Bonus Has Undocumented -8 Floor Cap
- **Severity:** MINOR
- **Spec reference:** S6b -- "(proposer_skill - target_skill) * 2" with no floor
- **Code reference:** `backend/game_logic/diplomacy.py:675` -- `max(-8, (proposer_skill - target_skill) * 2)`
- **Description:** Code caps skill penalty at -8 minimum. Spec has no such floor.
- **Impact:** Low-skill diplomats less penalized than intended.

### Finding 86-6: Rebellion Imminent Popup Shows "+15 Loyalty" But Invest Gives +10
- **Severity:** MINOR
- **Spec reference:** S8b -- "Invest in vassal: +10 loyalty"
- **Code reference:** `backend/game_logic/vassal.py:326,341` (popup) vs `vassal.py:645` (function)
- **Description:** Popup displays "Loyalty +15" but `invest_in_vassal()` uses `INVEST_LOYALTY_GAIN = 10`. Display-only bug.
- **Impact:** Players see +15 promise but receive +10.

### Finding 86-7: Continental System Reduces Trade Income Instead of Naval Income
- **Severity:** MINOR
- **Spec reference:** S5d -- "British naval income: reduced by 75g per nation participating."
- **Code reference:** `backend/game_logic/diplomacy.py:2110-2125`
- **Description:** Spec targets Britain 300g/turn naval income. Code targets bilateral trade income. If members at WAR with Britain (0 trade), system blocks nothing.
- **Impact:** Continental System ineffective when members already at war with Britain.

---

## Pass 87: Cross-System Stress Scenarios

### Scenario 1: Coalition + Vassal + Cascade — VASSAL Not Treated as Alliance for Cascade
- **Severity:** MAJOR
- **Systems:** `coalition.py`, `diplomacy.py`, `vassal.py`
- **File:** `backend/game_logic/diplomacy.py:1113-1115,1169-1174`
- **Description:** When coalition declares war on France, vassal Saxony is NOT automatically brought into the war. The `_process_war_cascade()` only triggers on DEFENSIVE_ALLIANCE and ALLIANCE states -- VASSAL is not matched. Offensive cascade explicitly skips vassals with `if nation in getattr(world, 'vassals', {}): continue`. No separate lord-defends-vassal or vassal-joins-lord mechanism exists. `_reconcile_vassal_diplomacy` only runs at vassalization time, not on subsequent war declarations.
- **Impact:** Vassals provide no military value in coalition wars. Lords provide no protection to vassals. Breaks core vassal value proposition.

### Scenario 2: Fog + Strategic Orders + Turn Processing — Working Correctly
- **Severity:** LOW
- **Description:** PURSUE to fogged location works correctly. Marshal follows last known location, arrives, breaks order with "Cannot reach" if target not there. Correct behavior but misleading message (should be "trail gone cold"). No infinite loop or stuck state.

### Scenario 3: Defiance + Multi-Marshal Coordination — Arguable Design Choice
- **Severity:** LOW
- **Description:** Defiant-fortified marshal still participates in casualty distribution for allied attacks (present in region = in the fight). Coordination bonuses for remaining attackers work correctly. Not a bug per se -- physically reasonable.

### Scenario 4: Diplomatic Dialogue + End Turn + Popups — Working as Designed
- **Severity:** NONE
- **Description:** Dialogue guard at executor.py:1428 correctly blocks end turn when dialogue is pending. Both guard layers (main + _execute_end_turn) work.

### Scenario 5: Save/Load + Strategic Orders + Fog — Working Correctly
- **Severity:** NONE
- **Description:** PURSUE recalculates path each turn from fresh intel. calculate_visibility() called after load. No stale path issues.

---

## Pass 88: Race Conditions and State Consistency

### Finding 88-1: Sync Endpoints Run in Threadpool Alongside Async Endpoints
- **Severity:** MAJOR (theoretical), LOW (practical)
- **File:** `backend/main.py:475`
- **Description:** `/command` is sync `def` (dispatched to threadpool) while `/respond_to_*`, `/save`, `/load` are `async def` (event loop). Both mutate the global `world` object without locking. A sync endpoint in threadpool could race with an async endpoint.
- **Impact:** Unlikely from game client (Godot serializes requests), but debug tools or curl could trigger.

### Finding 88-2: Global Mutable State Without Request Isolation
- **Severity:** INFO
- **File:** `backend/main.py:45-46`
- **Description:** Entire game state lives in two module-level globals: `world` and `game_state`. No per-request snapshot, no locking. Acceptable for single-player single-client.

### Finding 88-3: Godot api_client Single-HTTPRequest Guard (Effective)
- **Severity:** LOW
- **File:** `godot-client/project-sovereign/scripts/api_client.gd:5-12`
- **Description:** Single HTTPRequest node + pending_callback pattern + set_input_enabled(false) effectively prevents concurrent requests. ERR_BUSY return not explicitly handled -- could leave UI disabled permanently on error.

### Finding 88-4: Diplomacy Wizard Has Own HTTPRequest -- Can Race With api_client
- **Severity:** MODERATE
- **File:** `godot-client/project-sovereign/scripts/diplomacy_wizard.gd:9,26-27`
- **Description:** Wizard creates own HTTPRequest to avoid ERR_BUSY. GET /diplomatic_preview can fire while api_client has in-flight request. Read-only so no corruption, but could show inconsistent state.

### Finding 88-5: Popup Queue Read-Then-Clear Is Not Atomic
- **Severity:** MODERATE (theoretical), LOW (practical)
- **File:** `backend/main.py:161-175`
- **Description:** `_include_popup_passthroughs` reads popup, copies to response, then clears from world. Not atomic. Two concurrent requests could both read same popup.
- **Impact:** Prevented by single HTTPRequest guard in practice.

### Finding 88-6: Turn Counter Double-Trigger Prevented by UI Guard
- **Severity:** LOW (mitigated)
- **File:** `godot-client/project-sovereign/scripts/main.gd:647-649`
- **Description:** E hotkey checks `not end_turn_button.disabled`. set_input_enabled(false) fires immediately. Double-trigger effectively prevented.

### Finding 88-7: /load Endpoint Replaces Global world Reference Mid-Request
- **Severity:** MODERATE
- **File:** `backend/main.py:1660-1675`
- **Description:** `/load` replaces module-level `world` with new object. If a sync endpoint holds old reference in threadpool, its mutations are silently discarded.
- **Impact:** Loading while command processing = lost command effects. Unlikely from game client.

### Finding 88-9: pending_callback Overwrite Silently Drops Callbacks
- **Severity:** LOW
- **File:** `godot-client/project-sovereign/scripts/api_client.gd:12`
- **Description:** Every API call overwrites `pending_callback` before request. If ERR_BUSY returned, old callback is already overwritten. First request response would route to wrong handler.
- **Impact:** Prevented by set_input_enabled pattern in practice.

---

## Pass 89: Personality System Completeness

### Finding 89-1: V2 Objection Evaluators Missing balanced and loyal
- **Severity:** LOW
- **File:** `backend/commands/objection_v2.py:1094-1098`
- **Description:** PERSONALITY_EVALUATORS only has aggressive/cautious/literal. balanced/loyal return ConcernLevel.NONE. Acknowledged as intentional deferral.

### Finding 89-2: Strategic Evaluators Missing balanced and loyal
- **Severity:** LOW
- **File:** `backend/commands/objection_v2.py:1441-1445`
- **Description:** Same pattern as 89-1 for strategic commands.

### Finding 89-3: Combat Personality Modifiers Missing balanced and loyal
- **Severity:** LOW
- **File:** `backend/models/personality_modifiers.py:98-103`
- **Description:** Only aggressive/cautious/literal have entries. balanced/loyal return empty dict (neutral modifiers).

### Finding 89-4: Marshal Overview Descriptions Missing balanced and loyal
- **Severity:** LOW
- **File:** `backend/game_logic/marshal_overview.py:30-43`
- **Description:** UI personality descriptions only have 3 types. balanced/loyal show blank description.

### Finding 89-5: FORTIFY_DECAY_CONFIG Missing loyal
- **Severity:** LOW
- **File:** `backend/models/world_state.py:29-34`
- **Description:** Has aggressive/balanced/cautious/literal but not loyal. Falls to default (balanced behavior).

### Finding 89-7: Defiance Action Table Logic Hole for balanced/loyal
- **Severity:** LOW
- **File:** `backend/commands/defiance.py:86-122`
- **Description:** `calculate_defiance_chance()` only blocks literal (returns 0). balanced/loyal can have non-zero defiance chance. But `get_defiant_action()` returns None for them -- chance says "could defy" but no action is defined.
- **Impact:** Potential logic hole if balanced/loyal marshals added without fixing both functions.

### Finding 89-8: Pervasive String Comparison Instead of Enum
- **Severity:** MINOR
- **File:** Multiple files (defiance.py, objection_v2.py, enemy_ai.py, combat.py, etc.)
- **Description:** marshal.personality is stored as plain string, compared with raw strings everywhere. Typo or case mismatch would silently fail. Most paths use .lower() but not all.

### Finding 89-9: No Default/Else in Several Personality Switch Blocks
- **Severity:** MINOR
- **File:** `strategic.py`, `enemy_ai.py`, `combat.py` (multiple locations)
- **Description:** if/elif chains for personality-specific messages have no else clause. balanced/loyal get no flavor text.

### Finding 89-10: Loyal Personality Should Resist Defiance But Does Not
- **Severity:** LOW
- **File:** `backend/commands/defiance.py:42-44`
- **Description:** Only literal is blocked from defying. Loyal ("deeply loyal, follows dangerous orders") uses same defiance formula as aggressive/cautious.

---

## Pass 90: Integer Overflow, Bounds Checking, and Numeric Safety

### Finding 90-1: Gold Lump Treaty Clause Can Drive nation_gold Negative
- **Severity:** MAJOR
- **File:** `backend/models/world_state.py:4298-4302`
- **Description:** `gold_lump` clause subtracts full amount without floor guard. Unlike `gold_per_turn` (line 4438) which checks available and transfers only what is affordable, gold_lump directly decrements, allowing negative gold.
- **Evidence:** `self.nation_gold[from_nation] -= int(amount)` with no `max(0, ...)` guard.

### Finding 90-2: DP Refund in Coalition Formation Has No Upper Cap
- **Severity:** MINOR
- **File:** `backend/game_logic/coalition.py:566`
- **Description:** When coalition voids a proposal, DP refunded without capping at max_diplomatic_points. Could push DP above max (5) for remainder of turn.

### Finding 90-3: Float Values in Debug Acceptance Endpoint
- **Severity:** LOW
- **File:** `backend/game_logic/diplomacy.py:774-780`
- **Description:** `calculate_acceptance()` returns components with `round(x, 1)` floats. Debug endpoint passes through without int() wrapping. Not Godot-facing in production.

### Finding 90-4: Decisive Battle Ratio Stored as Float in World State
- **Severity:** LOW
- **File:** `backend/game_logic/diplomacy.py:1434`
- **Description:** `ratio: round(ratio, 1)` stored as float in `world.decisive_battles`. Currently not sent to Godot but persisted in save files.

### Pass 90 Assessment: Numeric Safety Generally Good
- All Godot-facing response builders wrap numbers in int(). VERIFIED.
- Division by zero guarded in all combat and ratio calculations. VERIFIED.
- Manpower pools have MAX caps. VERIFIED.
- Gold, DP, threat all handled correctly in main paths. VERIFIED.
- Main fix needed: gold_lump floor guard (Finding 90-1).

---

## Pass 91: COALITION_SPEC v1.1 Formula Compliance

### Finding 91-1: Decisive Battle Casualty Threshold Inconsistency Between Spec Sections
- **Severity:** LOW
- **Spec reference:** S6b says >5,000; S2a says >10,000
- **Code reference:** `backend/commands/executor.py:4959,4983` -- uses 10,000
- **Description:** Spec defines "decisive battle" with different thresholds in two sections. Code follows S2a (10,000). If S6b (5,000) was intended for coalition shock, some battles that should trigger it are missed.

### Finding 91-2: Coalition Shock Bonus Missing for Defeated Member
- **Severity:** MINOR
- **Spec reference:** S6b -- defeated member gets standard WE + 5 coalition shock bonus
- **Code reference:** `backend/game_logic/coalition.py:496-509` -- skips defeated_nation
- **Description:** `add_coalition_shock` explicitly skips the defeated nation and only applies +5 to OTHER members. Defeated member misses the +5 shock bonus per spec.

### Finding 91-3: United Cause Relation Bonus Applied to All Members Not Just New Belligerents
- **Severity:** MINOR
- **Spec reference:** S3e -- "Each new belligerent's relation with other coalition members: +10"
- **Code reference:** `backend/game_logic/coalition.py:568-571`
- **Description:** Code applies +10 to ALL member pairs including those already at war. Spec says only new entrants get the bonus.

---

## Pass 92: V2B_DEFIANCE_SPEC Compliance

### Finding 92-1: Spec Pseudocode Missing MODERATE Base Rate
- **Severity:** LOW
- **Description:** Spec prose says MODERATE=5% but pseudocode omits MODERATE branch. Code correctly implements all three (5%/15%/35%).

### Finding 92-2: Vindication Decay Period -- Spec Says 3 Turns, Code Uses 5
- **Severity:** LOW
- **Code reference:** `backend/models/world_state.py:5052` -- comment "R58: 5-turn interval, was 3"
- **Description:** R58 refinement changed decay from 3 to 5 turns. Spec not updated.

### Finding 92-3: defend/fortify Defiance Always Returns Inconclusive Instead of Spec Boolean
- **Severity:** MEDIUM
- **Spec reference:** S1 -- defend/fortify should immediately evaluate based on is_broken/is_retreating
- **Code reference:** `backend/commands/defiance.py:158-162`
- **Description:** Code returns None (inconclusive) instead of spec True/False. Defiant cautious marshals always get 0 trust/0 vindication/0 authority outcome instead of potentially being vindicated.

### Finding 92-5: VindicationTracker.apply_decay() Dead Code (Confirmed from Pass 83)
- **Severity:** LOW
- **Description:** Already identified as dead code. WorldState._process_vindication_decay() is the active implementation.

### Finding 92-6: Vindication Decay Reference Field Differs from Spec
- **Severity:** LOW
- **Description:** Spec uses marshal.last_objection_turn; code uses max(last_change_turn, last_objection_turn). Functionally similar but different mechanism.

---

## Pass 93: Endpoint Security and Input Validation

### Finding 93-1: Path Traversal in Load/Delete Endpoints
- **Severity:** HIGH
- **File:** `backend/main.py:1664,1688`
- **Description:** `/load` and `/delete_save` construct file path from user-supplied filename via `Path("saves") / request.filename`. No validation against `..` sequences. `/delete_save` calls `filepath.unlink()` -- attacker can delete files outside saves directory. `/load` error message leaks resolved filepath.
- **Proposed Fix:** Reject filenames containing `..`, `/`, or `\`. Or resolve path and verify it starts with saves directory.

### Finding 93-2: Exception Messages Leak Internal Details
- **Severity:** MEDIUM
- **File:** `backend/main.py` (8+ except blocks)
- **Description:** Every `except Exception as e` returns `f"Error: {str(e)}"` to client. Python exceptions can include file paths, class names, library internals.

### Finding 93-3: /respond_to_diplomatic_dialogue Accepts Raw Dict Without Validation
- **Severity:** MEDIUM
- **File:** `backend/main.py:1148`
- **Description:** Accepts `request: dict` instead of Pydantic model. `choice` field extracted without type checking.

### Finding 93-5: CORS Allows All Origins
- **Severity:** LOW
- **File:** `backend/main.py:389-394`
- **Description:** `allow_origins=["*"]`. Any website can make cross-origin requests. Low risk for localhost, HIGH if server exposed on network.

### Finding 93-6: API Key Partial Disclosure in Server Startup Log
- **Severity:** LOW
- **File:** `backend/main.py:38`
- **Description:** Logs first 10 chars of API key on startup. Key prefix `sk-ant-` plus 4 chars of actual key exposed.

### Finding 93-9: Save Name Not Length-Limited
- **Severity:** LOW
- **File:** `backend/main.py:1652-1657`
- **Description:** SaveRequest.save_name has no max length. Extremely long names processed through sanitization loop in memory.

---

## Pass 94: Morning Dispatch and Campaign Log Deep Audit

### Finding 94-1: Coalition Section Leaks Exact Enemy Strength/Gold/WE Through Fog
- **Severity:** MAJOR
- **File:** `backend/game_logic/dispatch.py:846-856`
- **Description:** `_build_coalition_section` reads raw world state values for coalition members (exact troop sums, gold, war exhaustion) bypassing fog of war entirely. Player sees "Austria: 45,000 troops, 1,200g" regardless of visibility.

### Finding 94-2: Hardcoded Nation List in Talleyrand Report Ignores Dynamic Nations
- **Severity:** MINOR
- **File:** `backend/game_logic/dispatch.py:541`
- **Description:** Uses `known_nations = ["Britain", "Prussia", "Austria", "Saxony"]` instead of `world.get_known_nations()`. Carved vassals never get Talleyrand suggestions.

### Finding 94-3: Campaign Log Event Type Mismatch -- War Declarations Never Appear
- **Severity:** MAJOR
- **File:** `backend/campaign_log.py:83-110` vs `diplomacy.py:985`
- **Description:** Campaign log expects `"diplomatic_war_declared"` but diplomacy.py logs as `"war_declaration"`. String mismatch means war declarations are silently filtered out of campaign log. Similarly, cascades logged as `"defensive_cascade"` / `"offensive_cascade"` but log expects `"diplomatic_alliance_cascade"`.

### Finding 94-4: Coalition Events Never Appear in Campaign Log
- **Severity:** MAJOR
- **File:** `backend/campaign_log.py:83-110` vs `coalition.py`
- **Description:** Coalition events logged as `"coalition_declared"`, `"coalition_dissolved"` etc. None of these types in CAMPAIGN_LOG_TYPES. Coalition formation/dissolution leaves no trace in persistent history.

### Finding 94-5: Diplomatic Discrepancy Event Logged but Never Displayed
- **Severity:** MINOR
- **File:** `backend/game_logic/dispatch.py:778-783`
- **Description:** Talleyrand sabotage discovery event type `"diplomatic_discrepancy"` not in CAMPAIGN_LOG_TYPES.

### Finding 94-6: Vassal Rebellion Events Never Logged to event_log
- **Severity:** MINOR
- **File:** `backend/game_logic/vassal.py`
- **Description:** Vassal system never calls `world.log_event()`. Campaign log has `"diplomatic_vassal_rebellion"` in whitelist and formatter, but no code ever logs that event type. Dead code in campaign log.

### Finding 94-7: _format_dispatch_event_text Returns Raw Template on KeyError
- **Severity:** LOW
- **File:** `backend/game_logic/dispatch.py:1035-1037`
- **Description:** KeyError fallback returns raw template with unfilled `{nation}`, `{treaty_type}` placeholders to player.

### Finding 94-8: enemy_regions Count Bypasses Fog of War
- **Severity:** LOW
- **File:** `backend/game_logic/dispatch.py:103-108`
- **Description:** Counts all non-player regions regardless of fog visibility, giving exact enemy region count.

### Finding 94-10: Relation Change Events Skip Fog Filtering
- **Severity:** LOW
- **File:** `backend/game_logic/dispatch.py:1040-1052`
- **Description:** AI-AI relation changes shown to player without fog check. Any nation pair with abs(delta) >= 10 appears in dispatch.

---

## Pass 95: Event Log and Notification Completeness

### Finding 95-1: Armistice Expiry Has No log_event and No Notification
- **Severity:** MEDIUM
- **File:** `backend/game_logic/diplomacy.py:1644-1702`
- **Description:** Armistice-to-war and armistice-to-peace transitions generate dispatch events but never call log_event() or add notification. War resumption especially needs HIGH-priority notification.

### Finding 95-2: Strategic Order Broken Has No log_event
- **Severity:** LOW
- **File:** `backend/commands/strategic.py:2011-2029`
- **Description:** _break_order() clears strategic order but never calls log_event(). Completions are logged but failures are not.

### Finding 95-3: Vassal Creation Has No log_event
- **Severity:** LOW
- **File:** `backend/game_logic/vassal.py:50-119,122-171`
- **Description:** create_vassal_treaty() and create_vassal_conquest() generate dispatch events but never call log_event().

### Finding 95-4: Vassal Creation Has No Notification
- **Severity:** LOW
- **File:** `backend/game_logic/vassal.py:50-119,122-171`
- **Description:** No notification fired for vassal creation despite rebellion getting CRITICAL notification.

### Finding 95-5: Building Completion Has No Notification
- **Severity:** LOW
- **File:** `backend/models/world_state.py:2533-2573`
- **Description:** Building completion calls log_event() and dispatch but no notification. Easy to miss 2-3 turn completions.

### Finding 95-6: Bankruptcy Escalation Notifications Never Auto-Dismissed
- **Severity:** MEDIUM
- **File:** `backend/models/world_state.py:2607-2611`
- **Description:** When bankruptcy ends (bt==0), resets tier counter but never dismisses BANKRUPTCY_ESCALATION notifications. Stale "Treasury in deficit" persists after recovery. Manpower system correctly auto-dismisses -- established pattern not followed.

### Finding 95-7: Player Proposal Rejection/Counter-Offer Has No log_event
- **Severity:** LOW
- **File:** `backend/models/world_state.py:3993-4142`
- **Description:** ACCEPT path logs diplomatic_treaty_signed but REJECT and failed-counter paths only generate dispatch events.

### Finding 95-8: VASSAL_LOYALTY_CRITICAL Notification Type Defined But Never Used
- **Severity:** TRIVIAL
- **File:** `backend/notifications.py:38`
- **Description:** Dead constant. Actual low-loyalty uses VASSAL_REBELLION_IMMINENT at loyalty <= 10.

### Finding 95-9: Region Capture Has No Notification
- **Severity:** LOW
- **File:** `backend/commands/executor.py:10982,11007,11112`
- **Description:** Territory capture/loss logged via log_event() but no notification. Enemy captures during enemy phase easy to miss.

---

## Pass 96: Vassal System Spec Compliance

### Finding 96-1: Continental System Ignores AUTONOMOUS Vassals Entirely
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomacy.py:2101-2108`
- **Description:** Per spec, AUTONOMOUS vassals should independently choose to join Continental System based on relation criteria. Code only auto-joins PUPPET/SATELLITE. AUTONOMOUS vassals are completely skipped.

### Finding 96-2: Continental System Never Ejects Non-Vassal Members Who Fail Participation Check
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomacy.py:2087-2127`
- **Description:** Per spec S5d, per-turn participation check should remove members whose relations no longer meet criteria (relation_with_france > +10 AND relation_with_britain < +30 AND NOT at_war_with_france). Code never removes members from continental_system_members list.

### Finding 96-3: Defection Cascade Reduces Loyalty Instead of Triggering Immediate Rebellion
- **Severity:** MAJOR
- **File:** `backend/game_logic/vassal.py:527-532`
- **Description:** Per spec S8d, failed cascade tipping point should trigger immediate rebellion. Code only reduces loyalty by 20. Vassal with loyalty 30 drops to 10 instead of rebelling. Spec says "rebels immediately regardless of current loyalty."

### Finding 96-4: Voluntary Vassal Release Missing Relation Bonuses
- **Severity:** MODERATE
- **File:** `backend/game_logic/vassal.py:845-850`
- **Description:** Per spec S5b, voluntary release should grant +20 relation with former vassal, +5 with all nations, -5 threat. Code only applies threat reduction (-8 from COALITION_SPEC). Both relation bonuses missing.

### Finding 96-5: Autonomy Change Does Not Trigger Marshal Assimilation/Release
- **Severity:** MODERATE
- **File:** `backend/commands/executor.py:14057-14060`
- **Description:** PUPPET/SATELLITE have marshals under lord control. AUTONOMOUS keeps own marshals. Autonomy change doesn't transfer marshals in either direction.

### Finding 96-6: Autonomy Change Takes Effect Immediately Instead of Next Turn
- **Severity:** MINOR
- **File:** `backend/game_logic/vassal.py:690-693`
- **Description:** Spec says "takes effect next turn." Code applies new autonomy level and tribute rate immediately.

### Finding 96-7: Cross-Doc Inconsistency -- Voluntary Release Threat -5 vs -8
- **Severity:** MINOR
- **File:** `docs/DIPLOMACY_SPEC.md:723` vs `docs/COALITION_SPEC.md:76`
- **Description:** DIPLOMACY_SPEC says -5 threat for release, COALITION_SPEC says -8. Code follows -8.

---

## Pass 97: Diplomatic Dialogue State Machine Deep Audit

### Finding 97-1: Enemy Response Templates Are Dead Code
- **Severity:** LOW
- **File:** `backend/game_logic/diplomatic_templates.py:1662-1730`
- **Description:** T24-T27 personality-flavored response templates with review_counter options (~70 lines) never called. Counter-offer dialogue built directly in world_state.py.

### Finding 97-2: Executor Guard Makes Non-Blocking Dialogues Effectively Blocking
- **Severity:** LOW
- **File:** `backend/commands/executor.py:1428`
- **Description:** Guard blocks ALL commands when any dialogue is set, regardless of blocking field. Non-blocking dialogues still prevent all player commands until dismissed.

### Finding 97-3: Keyword "no" in Dialogue Routing Matches Common Word Substrings
- **Severity:** LOW
- **File:** `backend/main.py:602`
- **Description:** Substring match for "no" catches "know", "not", "nothing", "north", "cannot", etc. Same issue for "more" matching "moreover", "anymore". Could inadvertently route normal commands to dialogue handler.

### Finding 97-4: accept_counter_offer and reject_counter_offer Missing from action_map
- **Severity:** LOW
- **File:** `backend/commands/executor.py:11905-11928`
- **Description:** Counter-offer actions not in keyword->action map. Work via fragile label matching fallback. Future label changes could break counter-offer flow.

---

## Pass 98: AI Diplomacy Decision Making Deep Audit

### Finding 98-1: AI-AI Alliance Proposals Skip Alliance Conflict Check
- **Severity:** MINOR
- **File:** `backend/game_logic/ai_diplomacy.py:1430-1451`
- **Description:** AI-AI defensive_alliance proposals go to _ratify_treaty without calling check_alliance_conflict. Two AI nations could ally despite conflicting war obligations.

### Finding 98-2: AI-AI Rivalry Downgrade Skips relation_all Penalty
- **Severity:** MINOR
- **File:** `backend/game_logic/ai_diplomacy.py:1382-1386`
- **Description:** AI-AI downgrades apply relation_target but skip relation_all broadcast. Asymmetric with canonical downgrade path.

### Finding 98-3: AI Proposals Don't Pre-Check Alliance Conflicts Before Proposing
- **Severity:** LOW
- **File:** `backend/game_logic/ai_diplomacy.py:675-695`
- **Description:** AI proposes alliances without checking if target is at war with AI's existing ally. Proposal impossible to accept, wastes cooldown slot.

### Finding 98-5: Stalemate Counter Not Reset When War Ends
- **Severity:** LOW
- **File:** `backend/game_logic/ai_diplomacy.py:360-371`
- **Description:** Stalemate counter persists through peace/new wars. A nation re-entering war could trigger immediate stalemate proposal from old counter value.

### Finding 98-7: AI-AI Proposals Don't Check DP Availability
- **Severity:** LOW
- **File:** `backend/game_logic/ai_diplomacy.py:1438-1451`
- **Description:** AI-AI treaty ratification never checks or deducts DP. AI can form unlimited treaties without spending diplomatic points.

### Finding 98-9: Armistice Cooldown Check Blocks All Proposal Types
- **Severity:** LOW
- **File:** `backend/game_logic/ai_diplomacy.py:641-644`
- **Description:** During armistice, AI cannot propose peace (blocked by cooldown check). Player must initiate peace after armistice.

---

## Pass 99: Save Format Migration and Backward Compatibility

### Finding 99-1: StrategicOrder.from_dict Uses Direct Dict Access for 5 Required Fields
- **Severity:** MEDIUM
- **File:** `backend/models/marshal.py:161-165`
- **Description:** Uses bare `data["key"]` for command_type, target, target_type, started_turn, original_command. Missing key = KeyError crash on load. Convention elsewhere is .get(key, default).

### Finding 99-2: Region.from_dict Uses Direct Dict Access for name and adjacent_regions
- **Severity:** LOW
- **File:** `backend/models/region.py:297-298`
- **Description:** Bare data["name"] and data["adjacent_regions"]. Identity fields but breaks defensive convention.

### Finding 99-3: Marshal.from_dict Uses Direct Dict Access for name, location, strength
- **Severity:** LOW
- **File:** `backend/models/marshal.py:1156-1158`
- **Description:** Bare data["name"], data["location"], data["strength"] in constructor. All other fields use .get().

### Finding 99-4: Coalition Dicts Use Shallow Copy Despite Nested Lists
- **Severity:** LOW
- **File:** `backend/models/world_state.py:3137,3139`
- **Description:** from_dict() uses .copy() (shallow) while to_dict() uses deepcopy(). Mutations to loaded coalition members list could affect source dict.

### Finding 99-5: Stance Enum Deserialization Has No Error Handling
- **Severity:** MEDIUM
- **File:** `backend/models/marshal.py:1246`
- **Description:** `Stance(data.get("stance", "neutral"))` raises ValueError on invalid stance string. No try/except with fallback to NEUTRAL.

### Finding 99-6: No Format Version Migration Path for Future Schema Changes
- **Severity:** LOW
- **File:** `backend/save_manager.py:98-103`, `backend/models/world_state.py:2786`
- **Description:** FORMAT_VERSION = 2 but only migration is "reject v1." No incremental migration framework. WorldState writes orphaned "format_version": "1.0" that nothing reads.

---

## Pass 100: Godot Response Handling Deep Audit

### Finding 100-1: Bare response.message Access in ~12 Error Paths
- **Severity:** HIGH
- **File:** `godot-client/project-sovereign/scripts/main.gd:940,1928,2011,2118,2126,2132,2136,2140,2294,2301,2506,2643`
- **Description:** At least 12 locations use bare `response.message` on error paths without .get("message", "Error"). api_client injects message for HTTP failures, but backend 200 responses returning {success: false} without message key crash Godot.
- **Proposed Fix:** Convert all to `response.get("message", "An error occurred")`.

### Finding 100-2: _display_result Accesses response.message Without Safety Check
- **Severity:** HIGH
- **File:** `godot-client/project-sovereign/scripts/main.gd:952`
- **Description:** `var message = response.message` -- bare access. Called from multiple places. Crashes if message key missing.

### Finding 100-5: Enemy Phase Dict Passed to Dialog Without Structural Validation
- **Severity:** MEDIUM
- **File:** `godot-client/project-sovereign/scripts/main.gd:2160`
- **Description:** response.enemy_phase passed directly to enemy_phase_dialog. Main.gd only checks key exists, not that it has required sub-fields.

### Finding 100-6: response.strategic_reports.is_empty() Crashes If Value Is Null
- **Severity:** LOW
- **File:** `godot-client/project-sovereign/scripts/main.gd:924`
- **Description:** .has() check passes but .is_empty() on null value crashes. Pattern `response.has("key") and response.key.method()` unsafe when value is null.

### Finding 100-7: _cached_wars Could Become Null If wars Key Exists as Null
- **Severity:** LOW
- **File:** `godot-client/project-sovereign/scripts/main.gd:3010-3012`
- **Description:** .get("wars", []) returns null if key exists with null value. _cached_wars.is_empty() would then crash. CLAUDE.md troubleshooting note documents this exact pattern.

### Finding 100-9: Diplomatic Dialogue Dict Passed to Popup Without Field Validation
- **Severity:** MEDIUM
- **File:** `godot-client/project-sovereign/scripts/main.gd:800-813`
- **Description:** dialogue dict passed to proposal_confirm_popup.show_dialogue() without validating required fields (options, target_nation, summary).

### Finding 100-12: Coalition Popup Data Not Validated Before Showing
- **Severity:** MEDIUM
- **File:** `godot-client/project-sovereign/scripts/main.gd:771-774`
- **Description:** coalition_popup passed directly to show_coalition() without checking for coalition_name, members, leader fields.

### Finding 100-16: .get() With Defaults Does Not Protect Against Explicit Null Values
- **Severity:** LOW
- **File:** `godot-client/project-sovereign/scripts/main.gd:1691-1696`
- **Description:** response.get("diplomatic_points", 0) returns null (not 0) if key exists with null value. Per CLAUDE.md: ".get() default only applies for MISSING keys, not None values."

### Pass 100 Assessment: Godot Generally Well-Coded
- .has() used extensively and correctly. VERIFIED.
- .get("key", default) used in display functions. VERIFIED.
- Null checks on dialog objects before calling methods. VERIFIED.
- Type checking in _process_active_wars. VERIFIED.
- Primary systemic risk: bare response.message on ~12 error paths.

---

## Pass 101: Hotkey and Input Handling Audit

### Finding 101-1: F1 in gui_input Bypasses Modal Dialog Check
- **Severity:** MEDIUM
- **File:** `godot-client/project-sovereign/scripts/main.gd:509-514`
- **Description:** gui_input handler fires F1 without checking _is_modal_dialog_open(). The wizard's internal check prevents actual opening, but the event is consumed (accept_event()) even during modals.

### Finding 101-2: Tab Key Not Blocked by Modal Dialogs
- **Severity:** LOW
- **File:** `godot-client/project-sovereign/scripts/main.gd:652-655`
- **Description:** Tab (toggle terminal) only checks command_input.has_focus(), not _is_modal_dialog_open(). Player can toggle terminal visibility while modal popup is displayed.

### Finding 101-7: Modal Popups Do Not Grab Keyboard Focus
- **Severity:** LOW
- **File:** Multiple popup .gd scripts
- **Description:** None of the modal popups call grab_focus() on their buttons when shown. Rely on set_input_enabled(false) instead. Keyboard events may flow to unfocused command_input's gui_input handler.

### Pass 101 Assessment: Hotkey System Well-Structured
- No hotkey collisions. VERIFIED.
- Screen mutual exclusion properly enforced via top_bar.toggle_screen(). VERIFIED.
- All set_input_enabled(false) paths have matching re-enable. VERIFIED.
- Only finding: Tab key + modal popup cosmetic interaction.

---

## Pass 102: Template and Display String Audit

### Finding 102-1: harsh_peace Missing from PROPOSAL_TYPE_DISPLAY
- **Severity:** LOW
- **File:** `backend/game_logic/diplomatic_dialogue.py:81-93`
- **Description:** AI generates harsh_peace proposals but type not in PROPOSAL_TYPE_DISPLAY. Fallback produces acceptable text but Godot popup formats inconsistently ("Harsh peace" vs "Harsh Peace").

### Finding 102-2: incoming_proposal_popup Uses Ad-Hoc Formatting Instead of Backend Display Name
- **Severity:** LOW
- **File:** `godot-client/project-sovereign/scripts/incoming_proposal_popup.gd:41`
- **Description:** Uses `.replace("_", " ").capitalize()` instead of backend-provided display name. Multi-word types get wrong capitalization. proposal_confirm_popup correctly uses backend field.

### Finding 102-4: Templates T11-T27 Are Dead Code (~560 Lines)
- **Severity:** INFO
- **File:** `backend/game_logic/diplomatic_templates.py:315-871`
- **Description:** 17 template categories defined but never looked up. All relevant scenarios build text directly via f-strings. Templates contain unresolvable slots.

### Pass 102 Assessment: Display String Safety Good
- FEEDBACK_STRINGS complete for all 15 acceptance components. VERIFIED.
- BBCode injection risk negligible (no user input in template slots). VERIFIED.
- NATION_DESIRE_PROFILES/TALLEYRAND_COMMENTARY have _default fallbacks. VERIFIED.

---

## Pass 103: MULTI_MARSHAL_SPEC Compliance Audit

### Finding 103-1: Casualty Remainder Assignment Differs from Spec
- **Severity:** LOW
- **Spec reference:** S8 -- "Last marshal gets remainder"
- **Code reference:** `backend/commands/executor.py:806-810`
- **Description:** Code assigns remainder to strongest non-artillery marshal (better design). Spec says last in iteration order. Difference is 1-3 troops.

### Finding 103-3: Spec Transient Field Architecture Contradicts Its Own Hard Cap
- **Severity:** INFO
- **Description:** Spec Section 2 applies combined_arms multiplicatively per-field. Section 1 hard caps ALL sources at +25%/+20%. Code correctly sums all, caps, applies once.

### Pass 103 Assessment: Multi-Marshal System Verified Correct
- Combined arms bonuses exact match (1/2/3 types). VERIFIED.
- Per-ally coordination with relationship scaling exact match. VERIFIED.
- Hard cap +25% atk / +20% def correctly applied. VERIFIED.
- Win/Loss relationship formula (severity, cooldown, range) all match. VERIFIED.
- Ordered pairs (itertools.permutations). VERIFIED.
- Artillery 50% casualty reduction correct. VERIFIED.
- Dedicated coordination Paths A/B correct. VERIFIED.
- Fortification rule correct. VERIFIED.

---

## Pass 104: Action Economy and AP System Audit

### Finding 104-1: AP Clause Causes Cumulative Permanent Reduction
- **Severity:** CRITICAL
- **File:** `backend/models/world_state.py:4467-4472`
- **Description:** `ap_per_turn` treaty clause reduces `nation_actions[nation]` cumulatively each turn. Never resets to base. A 1 AP/turn clause drains any AI nation to 1 AP within a few turns. Should compute base minus clause each turn, not mutate stored base.
- **Impact:** AP clauses are devastatingly overpowered against AI. Any AP treaty permanently cripples the target nation.

### Finding 104-2: AP Clause Against Player Nation (France) Is Silently Ignored
- **Severity:** MAJOR
- **File:** `backend/models/world_state.py:4470`
- **Description:** `nation_actions` dict only contains enemy nations. France not in dict. If AI demands AP concessions from player in peace treaty, clause is stored but never enforced. Player's AP pool is independent.
- **Impact:** AP clauses are asymmetrically broken: devastating vs AI, non-functional vs player.

### Finding 104-3: Several Actions Missing from _action_costs Dict
- **Severity:** LOW
- **File:** `backend/models/world_state.py:162-175`
- **Description:** 11 actions rely on default=1 instead of explicit entries. Fragile if new 2-AP action added.

### Finding 104-5: Cheat Commands Consume AP
- **Severity:** LOW
- **File:** `backend/commands/executor.py:1492`
- **Description:** `cheat` not in free_actions list. Debug/test commands consume game resources.

### Pass 104 Assessment: Core AP System Sound, Treaty Clause System Broken
- Turn start reset correct (base 4 + bonus_actions). VERIFIED.
- Strategic execution flag not injectable from client. VERIFIED.
- Enemy AI reads and decrements AP correctly per turn. VERIFIED.
- Treaty AP clause system has 2 critical flaws (cumulative + player-immune).
