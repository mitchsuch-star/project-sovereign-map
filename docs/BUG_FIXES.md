# Bug Fixes

> **Consolidated bug tracker.** All open bugs from playtest reviews, audits, and design fixes live here.
> Iterate sessions until clean, then move to `DESIGN_REFINEMENT.md`.
>
> **Last Updated:** April 8, 2026 (Session A: PL-15 + PL-18 FIXED. PL-16→PL-15, PL-17→PL-18. 33 new tests, 8015 total.)

---

## Summary

| Priority | Count | Status |
|----------|-------|--------|
| P1 — MAJOR | 0 | PL-9 FIXED (Session 10) — acceptance mismatch |
| P2 — MINOR | 0 | PL-10 FIXED (Session 10) — "more generous" downgrades proposal type |
| P3 — API-ONLY | 0 | PL-11 FIXED (Session 10) — incoming proposals hijack commands |
| P1 — MAJOR | 1 | PL-5 Part A FIXED (Session 8) |
| P1 — MAJOR | 1 | PL-5 Part B+C FIXED (Session 7), PL-6 FIXED (Session 7) |
| P2 — MINOR | 0 | PL-8 (counter-offer UX) FIXED (Session 9) |
| P2 — MINOR | 0 | PL-7 FIXED (Session 7, as PL-5 Part C) |
| P1 — MAJOR | 1 | PL-12 FIXED (Session 11) — harshness increases acceptance |
| P1 — MAJOR | 1 | PL-13 FIXED (Session 11) — viable proposal falsely rejected as "surpassed" |
| P2 — UX | 0 | PL-14 FIXED (Session 12) — ultimatum rework: conversational flow, preview, splash damage |
| P1 — CRITICAL | 0 | PL-15 FIXED (Session A) — ultimatum demand wizard replaces blind escalation |
| P2 — UX | 0 | PL-16 FIXED (absorbed into PL-15) — Harsher Demands replaced by wizard |
| P2 — BALANCE | 0 | PL-17 FIXED (absorbed into PL-18) — manpower key mismatch resolved |
| P2 — BALANCE | 0 | PL-18 FIXED (Session A) — typed manpower demands + DEMAND_VALUES key fixes |
| **P2 — BALANCE** | **1** | **PL-19 OPEN — ultimatum relation penalty is flat -10 regardless of demands** |
| **P2 — BALANCE** | **1** | **PL-20 OPEN — no guard against diplomatic elimination (last territory demand)** |
| P1 — MAJOR | 0 | PL-21 FIXED (code) — `region.connections` phantom attribute |
| P1 — MAJOR | 0 | PL-22 FIXED (code) — `region.income` phantom attribute |
| **P2 — GAMEPLAY** | **1** | **PL-23 OPEN — pre-proposal objection doesn't re-evaluate after term modification** |
| **P1 — MECHANICS** | **1** | **PL-24 OPEN — territory demands from modify_harsh score zero harshness** |
| **P2 — GAMEPLAY** | **1** | **PL-25 OPEN — R155-lite: diplomatic term novelty (companion to PL-23)** |
| **Total** | **5 OPEN (PL-19, PL-20, PL-23, PL-24, PL-25).** | |

**Session A (Apr 8):** PL-15 + PL-18 FIXED. 33 new tests (8015 total). PL-15: Full demand wizard (gold → territory → manpower → confirm) replaces blind `modify_harsh_ultimatum`. Wizard reuses armistice `terms_guidance` pattern with `ultimatum_` prefixed actions. Godot popup fixed: dedicated `_build_ultimatum_content()` reads `demands_display` (not `proposal_terms_summary`), renders splash damage, maps "Coercive" to red. AM-15.1 treaty merge, AM-15.2 ARMISTICE block, AM-15.7 `get_nation_regions()`. PL-18: 4 new DEMAND_VALUES keys (`gold_lump`, `manpower_infantry`/`cavalry`/`artillery`), typed manpower wizard with type picker + amount scaler, `_apply_ultimatum_demands()` dispatches to correct pool, `calculate_treaty_harshness()` covers all new types, backward compat for bare `"manpower"` demands.

**Prior bugs:** 28 bugs fixed across Sessions 1-6 (~163 tests). All P0/P1/P2/P3 resolved before these new findings.

**Session 12 (Apr 7):** PL-14 FIXED. 23 new tests (7980 total). Ultimatum rework: (A) full conversational dialogue flow — push ultimatum state, `_enrich_ultimatum_dialogue` preview with acceptance estimate, deliver/escalate/reconsider choice; (B) `modify_harsh_ultimatum` handler capped at 2 escalation rounds; (C) `generate_ultimatum_terms()` produces gold-only demands with cap, no AP clauses, no sweeteners; (D) `ultimatum_bonus` component added to `calculate_acceptance()`; (E) splash relation damage to bystanders (OPEN_BORDERS+ toward target take -5 to -15 toward France); (F) `ultimatum_cooldown` migrated from per-nation dict to scalar; (G) `proposal_result_popup` passthrough for Godot display.

**Session 11 (Apr 7):** PL-12 + PL-13 FIXED. 13 new tests (7951 total). PL-12: 5-part fix — (A) new `harshness_penalty` component in `calculate_acceptance` based on `calculate_treaty_harshness`, (B) extended `calculate_treaty_harshness` to score demands not just clauses, (C) lowered `is_harsh` threshold from -10 to -3, (D) inverted `harshness_bonus` from +5 to -5, (E) increased `DEMAND_VALUES["gold_per_turn"]` from -0.02 to -0.05. PL-13: 4-part fix — (A) snapshot `diplomatic_state_at_send` in `proposal_in_transit`, surpassed check uses snapshot, (B) dual-key normalization in `_enrich_proposal_summary` + defensive fallback in `execute_proposal`, (C) diagnostic logging, (D) `_build_base_terms` now sets both `type` and `proposal_type`.

**Session 10 (Apr 6):** All 3 remaining bugs FIXED. 13 new tests (7938 total). PL-9: Two-part fix — (A) warning text for borderline 50-75% proposals in `_enrich_proposal_summary`, (B) acceptance snapshot stored at send time + tolerance band (reject only if score drops >15 from snapshot) in `_process_proposal_in_transit`. PL-10: Force proposal type preservation in `modify_generous` and `modify_harsh` — `suggested["type"] = proposal_type` instead of `.get()` fallback that allowed `generate_suggested_terms` to override. PL-11: Improved dialogue guard error message with nation name and `/respond_to_diplomatic_dialogue` API hint.

**Session 9 (Apr 6):** Counter-offer UX COMPLETE. Visual differentiation in `incoming_proposal_popup.gd`: distinct "COUNTER-OFFER" header (blue), context line ("In response to your X proposal..."), steel-blue border, adapted button labels. Redundant assessment text removed from backend. Counter-offer logic audited — M3 algorithm confirmed solid (score 30-49 triggers counter, removes worst clause, adds nation-specific sweeteners). No new backend bugs found.

**Session 7 (Apr 6):** Backend cooldown fixes COMPLETE. 16 new tests (7915 total). Fixed: AI dedup gap, cooldowns in all 4 resolution paths (+1 decrement timing compensation), game-over guard, counter-offer accept/reject cooldowns, type-aware modify_harsh (friendship vs war/coercive).

**Spec review (Apr 6):** Deep code analysis verified all root causes. PL-5 redesigned: keep 1-turn deferral (thematic), add result popup + AI dedup + cooldown fixes. Found additional sub-bugs: accept-path cooldown gap (c), AI dedup gap (e), reject_counter_offer missing AI cooldown, cooldown-decrement timing in advance_turn, failed counter-offer cooldown gap (f), stale rejection missing all cooldowns (g), game-over leakage (h). All line numbers verified against code.

---

## Implementation Plan

### Session 7 — Backend Cooldown Fixes (PL-5 Part B + C, PL-6, PL-7) ✓ COMPLETE
Pure Python, all testable with pytest. Fixed the race condition and gameplay bugs.
- **PL-5 Part B:** Dedup guard in `_has_pending_proposal_from`, cooldowns in all 4 resolution paths (ACCEPT/REJECT/failed-counter/stale), game-over guard, +1 cooldown compensation for decrement timing
- **PL-5 Part C / PL-7:** `accept_counter_offer` + `reject_counter_offer` cooldown wiring in `diplomatic_executor.py`
- **PL-6:** Type-aware `modify_harsh` — split friendship vs war resolution vs coercive categories
- **Files:** `world_state.py`, `ai_diplomacy.py`, `diplomatic_executor.py`
- **Tests:** 16 new (tests/test_bugfix_session7.py), 2 existing updated

### Session 8 — Proposal Result Popup (PL-5 Part A)
Crosses backend/frontend. UX improvement — popup so results aren't buried in dispatch.
- **Backend:** New `proposal_result_popup` in PopupQueue (PRIORITY_ORDER + RESPONSE_KEYS), WorldState property + serialization, set popup in all 4 resolution paths
- **Frontend:** New `proposal_result_popup.gd` + `.tscn` (extends PopupBase, [Continue] button), register in `main.gd`, wire in `_on_command_result()`
- **Files:** `cooldown_manager.py`, `world_state.py`, `main.gd`, new Godot scene + script
- **Est. Tests:** ~4 + manual verification

**Priority:** Session 7 is higher — eliminates the race condition and nonsensical demands. Session 8 is polish. If Session 7 ships alone, the game is correct even if results are still only in dispatch text.

### Session 11 — Acceptance Formula + Surpassed Check (PL-12, PL-13)
Pure Python, all testable with pytest. Fixes the two core diplomacy formula bugs.
- **PL-12:** Add harshness penalty to `calculate_acceptance()`, extend `calculate_treaty_harshness()` to include demands, lower `is_harsh` threshold, invert `harshness_bonus`, increase gold demand impact
- **PL-13:** Snapshot diplomatic state at send time, normalize dual-key proposal type, add defensive fallback chain in `execute_proposal`
- **Files:** `diplomacy.py`, `diplomatic_templates.py`, `display_names.py`, `diplomatic_executor.py`, `world_state.py`, `diplomatic_dialogue.py`
- **Est. Tests:** ~12

### Session 12 — Ultimatum Rework (PL-14) ✓ COMPLETE
Conversational diplomacy flow replacing blind one-shot. 23 new tests. See session summary above.

---

## P1 — MAJOR

### PL-9: Acceptance Mismatch — Displayed % Doesn't Match Resolution ✓ FIXED (Session 10)
- **Source:** Playtest (Apr 6)
- **Summary:** Player sees 67-72% acceptance when reviewing a proposal, but the proposal is rejected because acceptance is recalculated at resolution time with changed world state. Player gets "Saxony agreed in principle, but the diplomatic situation has changed" despite high displayed odds.
- **Root cause:** Acceptance is calculated twice — once at proposal review time (`diplomatic_dialogue.py:427`) for display, and again at turn resolution (`world_state.py:4392` inside `_process_proposal_in_transit`). Between these two calculations, `advance_turn` runs: relations decay (`diplomacy.py:2226`, ±1/turn), war scores recalculate (`diplomacy.py:437`), war weariness accumulates (+2/turn). A 67% score can easily drop below 50 after these changes.
- **Reproduction:** Propose alliance to Saxony at 67-72% displayed acceptance with default relations (~40). End turn. Proposal rejected.
- **Design note:** The recalculation is arguably correct — conditions DO change while Talleyrand travels. The real problem is player expectation: a displayed 72% that fails feels like a lie. Two-part fix:
- **Proposed fix — Part A (UX mitigation):** Add Talleyrand warning text to the proposal confirmation screen. When acceptance is in the borderline range (50-75%), Talleyrand says something like: *"This estimate reflects current conditions, Sire. Much may change during my journey — a battle lost, a relation soured. I would counsel a wider margin if you wish certainty."* This sets player expectations that the % is a snapshot, not a guarantee. Add `acceptance_warning` field to dialogue data in `_enrich_proposal_summary` when score is 50-75%.
- **Proposed fix — Part B (tolerance band):** Reduce the volatility gap. Options (pick one):
  - (i) Snapshot: store `acceptance_score` in `proposal_in_transit` at send time, use it at resolution instead of recalculating. Displayed % = actual %. Simple but removes the "things changed" dynamic entirely.
  - (ii) Tolerance band: at resolution, reject only if recalculated score drops below `displayed_score - 15` (i.e., a 67% proposal needs to drop to 52 to actually fail). Preserves dynamism but prevents marginal rejections.
  - (iii) Weighted average: resolve with `0.7 * snapshot + 0.3 * recalculated`. Mostly honors the displayed score while allowing extreme changes to matter.
- **Recommendation:** Part A (warning text) is quick, thematic, and always valuable. Part B option (ii) tolerance band is the best gameplay fix — keeps the system dynamic while preventing frustrating near-miss rejections.
- **Files:** `diplomatic_dialogue.py` (warning text in `_enrich_proposal_summary`), `diplomatic_executor.py` (store snapshot), `world_state.py` (`_process_proposal_in_transit` — tolerance band)
- **Est. Tests:** ~5

### PL-10: "More Generous" Downgrades Proposal Type ✓ FIXED (Session 10)
- **Source:** Playtest (Apr 6)
- **Summary:** Making a vassalage or alliance proposal "more generous" converts it to a Peace Treaty — a LOWER diplomatic state than the current relationship. E.g., player has Open Borders with Saxony, proposes Alliance, clicks "more generous", proposal becomes Peace Treaty with gold sweetener. Since Peace < Open Borders, Saxony rejects with "current relations have already surpassed the proposed terms."
- **Root cause:** The generous handler (`diplomatic_executor.py:1103-1112`) adds sweeteners but the proposal type downgrades. The `modify_generous` logic likely rebuilds the proposal using `generate_suggested_terms` or similar, which picks a "safer" proposal type at generous harshness levels. The resulting proposal type doesn't respect the floor of the current diplomatic state.
- **Reproduction:** With Saxony at Open Borders (or higher), propose alliance. Click "More generous" once. Observe proposal type changes from "Full Alliance" to "Peace Treaty."
- **Proposed fix:** In `modify_generous`, never downgrade proposal type below the current diplomatic state. If the player proposed alliance, generous terms should add sweeteners (gold, protection) while keeping the alliance type. Clamp `proposal_type` to be >= current diplomatic state in the hierarchy.
- **Files:** `diplomatic_executor.py` (modify_generous handler), `diplomatic_dialogue.py` (generate_dialogue)
- **Est. Tests:** ~4

### PL-14: "Send Ultimatum" — Rework as Coercive Diplomatic Tool ✓ FIXED (Session 12)
- **Source:** Playtest A3 (Apr 7) — typed "send ultimatum" in terminal
- **Summary:** "Send ultimatum to X" fires immediately with no preview, no terms selection, no acceptance estimate, and no explanation of what's being demanded. The player has no idea what the ultimatum contains. Compare to `diplomatic_proposal` which has a full wizard flow (terms, harshness, sweeteners, acceptance %). The ultimatum is a blind one-shot action.
- **Root cause (code-verified):**
  - `_execute_diplomatic_ultimatum()` (diplomatic_executor.py:540-690) is a self-contained action that skips the conversational diplomacy system entirely. No dialogue, no wizard, no preview.
  - It hardcodes the outcome: if accepted → NON_AGGRESSION (or PEACE if at war) (line 648-654). Player cannot choose what they're demanding.
  - Acceptance is calculated using a blank `"type": "peace"` proposal (line 621-628) + military threat bonus (+10 or +15 adjacency). This means the acceptance % has nothing to do with the actual terms imposed.
  - Costs 2 DP, -10 relation immediately (line 613), 5-turn cooldown per target (line 666).
  - If rejected, grants casus belli (line 660) — this is the only strategic value, but the player doesn't know the acceptance odds beforehand.
- **Priority:** P2 (UX rework). Action is functional but opaque. Rework into a proper coercive diplomatic tool with preview, terms, and geopolitical consequences.

#### Ultimatum Rework Design

**Design Goal:** Ultimatums are pure coercive extortion — "give me what I want or else." They are fundamentally different from proposals: **no diplomatic state change, only demands.** They resolve instantly, let the player choose what to demand, and carry severe geopolitical consequences.

**Key distinction:**
- **Proposals** = "let's upgrade our relationship" (state change + optional terms)
- **Ultimatums** = "give me what I want or else" (demands only, no state change, any target)

**§1 Core Flow — Conversational Diplomacy Without State Change**

Route through the existing conversational diplomacy system but as a demands-only action:

1. Player types "ultimatum X" → push `ultimatum_confirm` dialogue with:
   - Pre-filled demands based on military advantage (via `generate_ultimatum_terms()`)
   - Acceptance estimate with military threat bonus visible
   - Rejection consequences (casus belli, further relation hit) shown upfront
   - Diplomatic cost preview: DP cost, relation penalty to target, splash damage to bystanders
   - Options: [Deliver Ultimatum] [Harsher Demands] [Reconsider]
2. Player can modify demands using existing "Harsher Demands" flow (modify_harsh)
3. Player confirms → **immediate resolution** (no transit — backed by military force, not Talleyrand)
   - Accepted: target pays up (gold, territory, manpower transferred). **No state change.** Relations stay as-is (already tanked by -10).
   - Rejected: casus belli granted, further -5 relation hit

**§2 Terms — Pure Demands, Any Non-War Target**

`generate_ultimatum_terms(target, world)` builds coercive demands based on military advantage:
- **No proposal type / state change.** Ultimatums don't propose a diplomatic upgrade — they extort resources.
- **Any non-war, non-vassal nation can be targeted** (at peace, allied — though allying someone you're extorting is a bold move). War targets blocked (use harsh peace instead). Own vassals blocked (use invest/autonomy).
- Auto-filled demands proportional to military advantage:
  - Gold per turn: `min(300, max(50, income * 0.5))` — capped at 50% of target income. If income <= 0, skip; use gold_lump instead: `min(500, nation_gold * 0.3)`. If 0 gold AND 0 income, only territory/manpower.
  - Territory: coveted regions if France controls adjacent territory and has military superiority
  - Manpower: `min(5000, troop_advantage * 0.1)` if target has significantly fewer troops
  - **No AP demands** — AP-per-turn requires war_score > 80 which is impossible in peacetime
- **No sweeteners ever** — ultimatums demand, they don't offer
- Player can escalate via dedicated `modify_harsh_ultimatum` handler (NOT the proposal `modify_harsh` — see §8)
- Acceptance uses full 14-component formula + ultimatum military threat bonus

**§3 Geopolitical Consequences — The Diplomatic Price**

Ultimatums are powerful but diplomatically toxic:

**(a) Relation damage to target:** -10 immediate (on delivery), -5 additional if rejected

**(b) Splash relation damage to bystanders:** Every nation with OPEN_BORDERS or better with the target takes a relation hit toward France:
- ALLIANCE with target: -15 relation with France
- DEFENSIVE_ALLIANCE with target: -12 relation with France
- NON_AGGRESSION with target: -8 relation with France
- OPEN_BORDERS with target: -5 relation with France
- Formula: `for nation in bystanders: world.modify_nation_relation("France", nation, -penalty)`

**(c) Coalition threat increase:** Issuing an ultimatum adds flat +15 threat (regardless of outcome). Acceptance adds another +5. This makes ultimatums a fast track to coalition formation — the player trades diplomatic standing for immediate concessions.

**(d) No counter-offer:** Ultimatums are take-it-or-leave-it. Acceptance formula uses thresholds: score >= 50 → ACCEPT, else → REJECT. No COUNTER_OFFER outcome.

**§4 Global Cooldown**

- **1 ultimatum per 5 turns across ALL nations** (not per-target). Field: `world.ultimatum_global_cooldown` (int, decremented in `_cooldown_manager`)
- This prevents ultimatum spam and forces the player to pick their target carefully
- Displayed in the preview dialogue: "Next ultimatum available in X turns"

**§5 Acceptance Formula Integration**

Add `ultimatum_bonus` component to `calculate_acceptance()`:
- +10 base military threat
- +15 if any French marshal is adjacent to any target marshal
- +5 per French marshal in target territory (capped at +15)
- Component exposed in acceptance breakdown so player sees why odds are what they are

**§6 On Acceptance — Resource Transfer**

When the target accepts, demands are applied immediately:
- Gold per turn: added to `world.active_treaties` as ongoing obligation (same mechanism as existing treaty gold)
- Territory: regions transfer control to France via existing `transfer_region()` path
- Manpower: deducted from target pool, added to France pool
- No diplomatic state change — the relationship stays exactly where it was

**§7 Scope Exclusions**

- **No AI ultimatums** in this implementation. AI coercion expressed through coalitions, war declarations, harsh counter-offers. AI-to-player ultimatums deferred to R162 in DESIGN_REFINEMENT.md.
- **No Talleyrand sabotage** — ultimatums resolve instantly (no transit). Skip defiance check.
- **No special marshal displacement** on territory transfer — reuses existing `territory_cede` handling.
- **No AP demands:** AP-per-turn requires war_score > 80 which is impossible in peacetime.

**§8 Implementation Guide — Step by Step**

This section is the authoritative reference. Where §1-§7 conflict with §8, §8 wins.

**Step 1: `world_state.py` — Cooldown migration**
- Replace `register_dict("ultimatum")` with `register_scalar("ultimatum_global")` in `__init__`
- Replace `ultimatum_cooldowns` property (dict→`_cooldown_manager.get_dict`) with `ultimatum_global_cooldown` property (int→`get_scalar("ultimatum_global")`/`set_scalar`)
- Pattern to copy: `talleyrand_defiance_cooldown` property (scalar cooldown, same file)
- `to_dict`: change `"ultimatum_cooldowns": {dict}` → `"ultimatum_global_cooldown": int(self.ultimatum_global_cooldown)`
- `from_dict`: read new int format. Migration: `if "ultimatum_cooldowns" in data and "ultimatum_global_cooldown" not in data: world.ultimatum_global_cooldown = max(data["ultimatum_cooldowns"].values(), default=0)`
- Update `docs/SAVE_FORMAT_REFERENCE.md`

**Step 2: `diplomacy.py` — Acceptance formula**
- Add `"ultimatum_demand": 20` to `BASE_DISPOSITION` dict (~line 109). **IMPORTANT:** the fallback `BASE_DISPOSITION.get(proposal_type, 30)` at line 659 means forgetting this silently gives 30 — test that it's 20.
- Add `ultimatum_bonus` component to `calculate_acceptance()` (~line 823, before the `raw_score` sum):
  ```python
  ultimatum_bonus = 0
  if proposal_type == "ultimatum_demand":
      ultimatum_bonus = 10  # base military threat
      # +15 if any proposer marshal adjacent to target marshal
      # +5 per proposer marshal in target territory (cap +15)
      # (same adjacency logic as current _execute_diplomatic_ultimatum lines 598-610)
  ```
- Add `ultimatum_bonus` to the `raw_score` sum and to the `components` dict
- Add `"ultimatum_bonus"` to `FEEDBACK_STRINGS` in `display_names.py`: `{"positive": "military threat backs demands", "negative": ""}`

**Step 3: `diplomatic_templates.py` — New `generate_ultimatum_terms()`**
- New function: `generate_ultimatum_terms(target_nation, world) -> Dict`
- Returns: `{"demands": [...], "sweeteners": [], "clauses": [], "type": "ultimatum_demand"}`
- Demand generation: gold (§2 formula), territory (adjacent + military superiority), manpower (troop advantage). No AP.
- **No `proposal_type` key** — ultimatums use `"type": "ultimatum_demand"` only. No dual-key fragility.

**Step 4: `diplomatic_executor.py` — Replace `_execute_diplomatic_ultimatum` body**

Replace the entire method body. New flow:
1. Pre-validate: target exists, not WAR (message: "Use a peace proposal with harsh demands instead"), not own vassal (message: "Use investment or autonomy changes"), global cooldown check, DP check (2 DP), Talleyrand threat>50 objection (keep existing)
2. **DO NOT deduct DP or apply relation penalty here** — that happens on delivery (step 6)
3. Build terms via `generate_ultimatum_terms(target, world)`
4. Build splash damage preview: iterate `world.get_active_nations()`, check each nation's state with target, compute penalty per §3(b) tier. Store as list of `{nation, treaty_with_target, relation_penalty}`.
5. Push `ultimatum_confirm` dialogue via `world.dialogue_manager.push(...)`:
   ```python
   {
       "type": "ultimatum_confirm",
       "target_nation": target_nation,
       "prompt": "Talleyrand presents the ultimatum terms...",
       "options": [
           {"label": "Deliver Ultimatum", "action": "execute_ultimatum", "terms": terms},
           {"label": "Harsher Demands", "action": "modify_harsh_ultimatum"},
           {"label": "Reconsider", "action": "reconsider"},
       ],
       "terms": terms,
       "splash_damage_preview": splash_preview,
       "threat_increase_preview": "+15 threat, +5 if accepted",
       "cooldown_remaining": int(world.ultimatum_global_cooldown),
   }
   ```
6. Call `_enrich_ultimatum_dialogue()` (see step 5) on the dialogue before returning
7. Return dialogue result (same pattern as `_execute_diplomatic_proposal` pushing a `proposal_confirm`)

**Step 5: `diplomatic_dialogue.py` — New `_enrich_ultimatum_dialogue()` function**

**DO NOT modify `_enrich_proposal_summary()`.** That function assumes proposal-style terms (proposal_type→state map, transition DP cost, `generate_suggested_terms` fallback). Instead, create a new function:

```python
def _enrich_ultimatum_dialogue(dialogue: Dict, target_nation: str, world) -> Dict:
    """Add acceptance estimate and consequence preview to ultimatum dialogue."""
```

This function:
- Reads terms from `dialogue["terms"]`
- Builds acceptance proposal: `{"type": "ultimatum_demand", "proposer_nation": "France", "target_nation": target, "sweeteners": [], "demands": terms["demands"], "clauses": []}`
- Calls `calculate_acceptance(proposal, world)` → sets `dialogue["acceptance_estimate"]`, `dialogue["acceptance_outcome"]`, `dialogue["acceptance_hint"]`
- Sets `dialogue["dp_cost"] = 2` (flat, not transition-based)
- Sets `dialogue["harshness_label"] = "Coercive"` (ultimatums are always coercive)
- Passes through `splash_damage_preview` and `threat_increase_preview` already on the dialogue

**Step 6: `diplomatic_executor.py` — Add handlers in `_process_dialogue_choice`**

Add two new `elif` blocks in `_process_dialogue_choice` (near `execute_proposal`, ~line 895):

**(a) `elif action == "execute_ultimatum":`**
1. Deduct 2 DP (check sufficient first, pop dialogue + return error if not)
2. Apply -10 relation to target: `world.modify_nation_relation(player, target_nation, -10)`
3. Apply splash damage: iterate bystander nations per §3(b), call `world.modify_nation_relation("France", nation, -penalty)` for each
4. Add coalition threat: `add_threat(world, 15, "ultimatum_issued")`
5. Calculate acceptance: build proposal dict with `"type": "ultimatum_demand"`, call `calculate_acceptance()`, threshold >= 50 = ACCEPT
6. **If ACCEPTED:**
   - Apply demands via `_apply_ultimatum_demands()` (new helper, see step 7)
   - Add +5 threat: `add_threat(world, 5, "ultimatum_accepted")`
   - Set `world.ultimatum_global_cooldown = 5`
   - Grant NO state change
7. **If REJECTED:**
   - Apply -5 additional relation
   - Grant casus belli: `world.casus_belli[diplo_key] = True`
   - Set `world.ultimatum_global_cooldown = 5`
8. Pop dialogue, log to diplomatic_history, apply marshal trust reactions, log campaign event
9. Return result dict with outcome message

**(b) `elif action == "modify_harsh_ultimatum":`**

**DO NOT reuse the proposal `modify_harsh` handler.** That handler is deeply proposal-specific (reads `proposal_type`, classifies friendship/war/coercive, uses `generate_suggested_terms`, rebuilds as `"proposal_confirm"`). Create a dedicated handler:

1. Read current terms from `selected.get("terms", {})`
2. Read `modify_count` from dialogue context (default 0)
3. If `modify_count >= 2`: return message "Cannot escalate further, Sire."
4. Escalation logic (ultimatum-specific):
   - Round 1: multiply all existing demand values by 1.5, add territory demand if not present and France controls adjacent region
   - Round 2: multiply by 1.5 again, add manpower demand if not present
   - **Territory guard (PL-20 §B):** When adding territory demands during escalation, apply the same elimination guard as auto-generation: filter out regions that would leave the target with ≤1 region. Use `target_regions = world.get_nation_regions(target_nation)` and only add regions where `len(target_regions) - len(already_demanded) - 1 > 1`. This prevents escalation from proposing rump/annex-level demands.
5. Rebuild `ultimatum_confirm` dialogue with updated terms (same structure as step 4)
6. Call `_enrich_ultimatum_dialogue()` to recalculate acceptance with new terms
7. Increment `modify_count` in dialogue context

**Step 7: `diplomatic_executor.py` — New `_apply_ultimatum_demands()` helper**

**DO NOT use `_ratify_treaty()`.** That function assumes a state transition, stores in `active_treaties`, checks relation requirements, and logs `"diplomatic_treaty_signed"`. All wrong for ultimatums. Instead, create a focused helper:

```python
def _apply_ultimatum_demands(self, demands: list, target_nation: str, world) -> list:
    """Apply ultimatum demands immediately. Returns list of transfer descriptions."""
```

Process each demand:
- `gold_lump`: transfer from target's `nation_gold` to France (same logic as `_ratify_treaty` lines 4760-4767, with floor check)
- `gold_per_turn`: store as ultimatum tribute in `active_treaties`:
  ```python
  diplo_key = world._make_diplo_key("France", target_nation)
  world.active_treaties[diplo_key] = {
      "nations": ["France", target_nation],
      "type": "ultimatum_tribute",
      "is_ultimatum_tribute": True,
      "clauses": [{"type": "gold_per_turn", "from": target_nation, "to": "France", "amount": int(value)}],
      "turn_signed": int(world.current_turn),
      "harshness": 1.0,
  }
  ```
  **NOTE:** This overwrites any existing treaty for this pair. If they already have a treaty, the gold_per_turn replaces it. Check if this is acceptable or if clauses should be appended.
- `territory_cede`: set `region.controller = "France"`, `region.stability = 50`, call `invalidate_active_nations_cache()`, add threat per region (+8 via `add_threat(world, 8 * count, "ultimatum_annex")`)
- `manpower`: deduct from `world.nation_manpower[target]`, add to `world.nation_manpower["France"]` (floor at 0)

**Step 8: `_process_treaty_income()` — Gold per turn processing**

Verify that `_process_treaty_income()` in `world_state.py` already handles `gold_per_turn` clauses generically from `active_treaties`. If it iterates `active_treaties` and processes `"gold_per_turn"` clause types, ultimatum tribute works automatically. If it only processes specific treaty types, add `"ultimatum_tribute"` to the check. The `is_ultimatum_tribute` flag exists for ledger display differentiation, not for processing gating.

**Step 9: `display_names.py` — Add entries**
- `ACTION_DISPLAY["diplomatic_ultimatum"] = "delivers ultimatum to"`
- `PROPOSAL_TYPE_DISPLAY["ultimatum_demand"] = "Ultimatum"`
- `FEEDBACK_STRINGS["ultimatum_bonus"] = {"positive": "military threat backs demands", "negative": ""}`

**Step 10: `campaign_log.py` — Add entries**
- Add `"ultimatum_issued"`, `"ultimatum_accepted"`, `"ultimatum_rejected"` to `CAMPAIGN_LOG_TYPES`
- Add `_DEFIANCE_DISPLAY["diplomatic_ultimatum"] = "issuing ultimatum"` and `_OBJECTION_DISPLAY["diplomatic_ultimatum"] = "issuing ultimatum"`
- Add formatting in `format_event_oneliner()` for each event type

**Step 11: `main.py` — Dialogue keyword routing**
- Add `"deliver"` and `"ultimatum"` to `_DIALOGUE_RESPONSE_KEYWORDS` (~line 617) so terminal input "deliver ultimatum" routes to dialogue handler instead of falling through to executor

**Step 12: `coalition.py` — No changes needed**
- Threat accumulation is called via `add_threat()` from the executor (step 6). No new function in coalition.py.

**Step 13: `validation.py` / `parser.py` / `llm_client.py` — No changes needed**
- `diplomatic_ultimatum` already exists in all three. Parser already routes "ultimatum X" correctly.

**Step 14: Tests (~12)**
- Ultimatum dialogue push (terms generated, preview fields present)
- Vassal target blocked
- War target blocked
- Global cooldown blocks second ultimatum
- Acceptance formula: BASE_DISPOSITION = 20, ultimatum_bonus applied
- Accepted: gold transferred, territory transferred, threat +20, no state change
- Rejected: casus belli granted, relation -15 total, threat +15
- Splash damage: bystander allies get relation penalty
- modify_harsh_ultimatum: demands escalate, acceptance decreases
- modify_harsh_ultimatum: capped at 2 rounds
- Gold cap: gold_per_turn capped at 50% income
- Zero-income target: gold_lump fallback
- Cooldown migration: old dict format → new int
- `_process_treaty_income()` processes ultimatum tribute gold_per_turn correctly
- Ultimatum against nation with no adjacent French territory: gold/manpower-only demands (no territory)
- modify_harsh_ultimatum: territory escalation respects elimination guard (PL-20 §B)

- **Est. Tests:** ~15-18

---

### PL-13: Viable Proposal Falsely Rejected as "Surpassed"
- **Source:** Playtest A3 (Apr 7) — Proposal result popup after end turn
- **Summary:** Player proposes Non-Aggression to Saxony (currently at OPEN_BORDERS) with 76% acceptance estimate. Next turn, proposal resolves as REJECTED with message: "The diplomatic situation with Saxony has changed — our proposal is no longer viable" and "The current relations have already surpassed the proposed terms." But Saxony is still at OPEN_BORDERS — relations did NOT surpass Non-Aggression level.
- **Repro:** F1 → Saxony → Propose Non-Aggression → send terms → end turn → PROPOSAL REJECTED popup with false "surpassed" reason
- **Root cause (deep analysis, Apr 7):**
  - The surpassed check at `world_state.py:4354-4357` compares `_UPGRADE_ORDER` indices: `if tgt_idx <= curr_idx` → reject. Uses `_proposal_to_state` mapping (line 4346-4352) to convert proposal type to state.
  - `_UPGRADE_ORDER` in `diplomacy.py:29-32`: WAR(0)→ARMISTICE(1)→PEACE(2)→OPEN_BORDERS(3)→NON_AGGRESSION(4)→DEFENSIVE_ALLIANCE(5)→ALLIANCE(6). Higher index = better.
  - For OPEN_BORDERS(3)→NON_AGGRESSION(4): `4 <= 3` = FALSE. **The comparison logic itself is correct and should NOT reject.**
  - **advance_turn ordering verified** — nothing between send and resolution can upgrade France-Saxony state:
    - Line 4023: `current_turn += 1`
    - Line 4080: `process_diplomacy_turn()` — missions change relations only (`_process_mission_effects` line 1918-1922), auto-downgrade only downgrades (line 1409), armistice expiration only handles ARMISTICE→PEACE/WAR (line 1601)
    - Line 4088: `_process_proposal_in_transit()` — proposal resolves HERE
    - Line 4142: `process_ai_ai_diplomatic_phase()` — runs AFTER proposal resolution; also excludes France from AI-AI pairs (`ai_diplomacy.py:1427` "excluding France")
    - `_process_ai_diplomatic_phase()` (turn_manager.py:145) — AI→player proposals are delivered as popups, not auto-resolved
  - **Root cause: proposal type corruption via dual-key fragility.** The system uses TWO different keys for proposal type:
    - `terms["type"]` — used by `_enrich_proposal_summary` for acceptance calculation (`diplomatic_dialogue.py:419`)
    - `terms["proposal_type"]` — used by `execute_proposal` for the stored proposal (`diplomatic_executor.py:897`)
    - If `terms["proposal_type"]` is missing or lost during the dialogue round-trip, it falls back to `"peace"` (line 897 default). A `"peace"` proposal (PEACE, index 2) to a nation at OPEN_BORDERS (index 3) would be rejected as surpassed: `2 <= 3 = TRUE`.
    - The PL-10 fix (line 1016, 1063) ensured both keys are set in `modify_harsh`/`modify_generous`, but the initial unmodified flow relies on `generate_suggested_terms` setting `type` and the template resolver setting `proposal_type` — a fragile dual-key system.
  - **Connection to PL-12:** This bug occurred in the same playtest session as PL-12 (clicking "Even Harsher"). If the modify_harsh flow somehow failed to propagate `proposal_type` correctly before the PL-10 fix was applied, or if an edge case bypasses it, the type would corrupt.
- **Proposed fix (four-part):**
  - **(A) Snapshot diplomatic state at send time** — In `diplomatic_executor.py`, where `proposal_in_transit` is built (~line 962, the dict literal), add a new field: `"sent_diplomatic_state": world.get_diplomatic_state(world.player_nation, target_nation)`. This stores the string state name (e.g., `"OPEN_BORDERS"`). At resolution in `world_state.py` `_process_proposal_in_transit` (~line 4344, before the surpassed check): if `proposal_in_transit.get("sent_diplomatic_state")` exists, compare the proposal's target state against the *snapshot* instead of the current state. If the proposal was valid when sent (target_state index > snapshot index), skip the surpassed rejection even if the current state has since changed.
  - **(B) Normalize dual-key to single key** — in `_enrich_proposal_summary` (`diplomatic_dialogue.py:392-393`), always set BOTH `terms["type"]` and `terms["proposal_type"]` to `proposal_type`. Add defensive normalization in `execute_proposal` (`diplomatic_executor.py:897`): `proposal_type = terms.get("proposal_type") or terms.get("type") or "peace"`.
  - **(C) Add diagnostic logging** — temporary log in `_process_proposal_in_transit` before the surpassed check: print `proposal.get("type")`, `current_state`, `target_state`, `curr_idx`, `tgt_idx`. This confirms root cause on next occurrence.
  - **(D) Fix `generate_suggested_terms` at the source** — In `diplomatic_templates.py`, function `_build_base_terms()`: after the `terms = { "type": proposal_type, ... }` dict is constructed (the closing `}` is ~6 lines after the opening), add `terms["proposal_type"] = proposal_type` as the next line. This ensures the function returns terms with BOTH keys, eliminating the need for every caller to manually add `proposal_type`.
- **Related dual-key instances found (Apr 7 audit):**
  - `diplomatic_dialogue.py:814-820` — `generate_feasibility_assessment()` creates terms with `proposal_type` but no `type` key. Safe because `execute_proposal` (line 897) reads `proposal_type` first, but inconsistent.
  - `diplomatic_executor.py:1620` — counter_terms handler uses defensive fallback: `counter_terms.get("type", counter_terms.get("proposal_type", "peace"))`. Shows developer awareness of the fragility.
  - `diplomatic_dialogue.py:392-393` and `676-678` — callers of `generate_suggested_terms` always manually add `proposal_type`. Fix D eliminates this boilerplate.
- **Priority:** P1 (MAJOR). 76% acceptance proposals should not be auto-rejected. Core diplomacy loop is broken — player invests DP, waits a turn, gets false rejection.
- **Files:** `world_state.py` (_process_proposal_in_transit lines 4342-4389), `diplomatic_executor.py` (line 897, line 962), `diplomatic_dialogue.py` (line 392-393, 814-820), `diplomatic_templates.py` (line 1472)
- **Est. Tests:** ~5

---

### PL-12: Harsher Terms INCREASE Acceptance Estimate (Inverted Harshness)
- **Source:** Playtest A3 (Apr 7) — Godot diplomacy wizard, proposal to Saxony
- **Summary:** Clicking "Even Harsher" in the proposal confirm popup raises acceptance from 72% to 76%. Harsher terms should DECREASE acceptance, not increase it.
- **Repro:** F1 → Saxony → Propose Non-Aggression → click "Even Harsher" → acceptance estimate goes UP
- **Root cause (deep analysis, Apr 7) — 4-layer formula gap:**
  - **Layer 1 — `calculate_treaty_harshness()` is cosmetic only:** `diplomatic_templates.py:1722-1736` correctly computes harshness 0.0-1.0 from clauses. Called ONLY in `_enrich_proposal_summary()` (`diplomatic_dialogue.py:406-407`) for display labels ("Low"/"Moderate"/"High"). **Never imported or called in `calculate_acceptance()`** (`diplomacy.py:627-839`). Verified via grep — zero references in diplomacy.py.
  - **Layer 2 — Gold demands have near-zero formula impact:** `DEMAND_VALUES["gold_per_turn"] = -0.02` per gold (`diplomacy.py:159`). `modify_harsh` adds 100 gold/turn for friendship types (`diplomatic_executor.py:1029`) → **-2 deal_balance**. Removing initial sweeteners costs -5 to -15 more. Total swing: -7 to -17, often offset by other components.
  - **Layer 3 — `is_harsh` personality trigger doesn't fire:** `diplomacy.py:758-762` — `is_harsh = True` only when `demand_total < -10`. A 100 gold demand produces `demand_total = -2`, so `is_harsh` stays False. Saxony's dove diplomat gets `peace_mod = +10` (`diplomacy.py:123`, `PERSONALITY_MODIFIERS["dove"] = (10, -10)`) instead of `harsh_mod = -10`. The personality modifier is **+10 in BOTH** the initial and harsh proposals — a 20-point swing that's invisible.
  - **Layer 4 — `harshness_bonus` rewards past harshness:** `diplomacy.py:809-815` — if ANY previous treaty had `harshness > 0.3`, adds **+5** to acceptance. Display text (`display_names.py:211-214`): *"prior harsh terms make them more pliable."* This is constant and adds to acceptance regardless of current proposal harshness.
  - **Why acceptance goes UP:** Initial terms may include sweeteners valued at < net 0 due to formula weighting. `modify_harsh` removes them + adds a -2 gold demand. Personality stays +10 (dove). Net: acceptance barely changes or increases slightly. **The formula has no mechanism to penalize current proposal harshness.**
  - **`calculate_treaty_harshness()` also ignores demands:** It only scores `clauses`, not `demands` (`diplomatic_templates.py:1726-1735`). Even if it were wired into acceptance, it would score a 100g/turn demand at 0.0 harshness.
- **Priority:** P1 (MAJOR). Core diplomacy mechanic is inverted. Player feedback loop is wrong — encourages harsher terms instead of creating a risk/reward tradeoff.
- **Proposed fix (5 parts):**
  - **(A) Add harshness penalty to `calculate_acceptance()`** (`diplomacy.py`, inside `calculate_acceptance` before the `raw_score` sum at ~line 824):
    - Import `calculate_treaty_harshness` from `diplomatic_templates`
    - Build a dict from the proposal: `{"clauses": proposal.get("clauses", []), "demands": proposal.get("demands", [])}`
    - Call `calculate_treaty_harshness()` on it → returns 0.0-1.0
    - Compute penalty: `harshness_penalty = -min(40, max(0, int((harshness - 0.2) * 150)))` — **this is a negative number** (penalty, not bonus)
    - Add `harshness_penalty` to the `raw_score` sum (line ~824) as a separate addend alongside the existing `harshness_bonus`. They are independent: `harshness_bonus` is from *prior treaties*, `harshness_penalty` is from *current proposal terms*.
    - Add `"harshness_penalty"` to the `components` dict so it shows in breakdown
  - **(B) Extend `calculate_treaty_harshness()` to include demands** (`diplomatic_templates.py`, function at ~line 1722): Currently iterates ONLY `treaty.get("clauses", [])`. **Must also iterate `treaty.get("demands", [])`.** Add a second loop after the clauses loop:
    ```python
    for d in treaty.get("demands", []):
        dtype = d.get("type", "") if isinstance(d, dict) else ""
        dvalue = abs(d.get("value", 0)) if isinstance(d, dict) else 0
        if dtype == "gold_per_turn":
            harshness += 0.1 * (dvalue / 100)  # +0.1 per 100g
        elif dtype == "territory_cede":
            harshness += 0.2 * max(1, dvalue)   # +0.2 per region
        elif dtype == "ap_per_turn":
            harshness += 0.3 * max(1, dvalue)   # +0.3 per AP
    ```
    Without this, `calculate_treaty_harshness` returns 0.0 for proposals with demands but no clauses — and fix (A) would be a no-op.
  - **(C) Lower `is_harsh` threshold** (`diplomacy.py:760`): Change `demand_total < -10` to `demand_total < -3`. A 100g gold demand (-2) + any other demand would then trigger `harsh_mod` personality, flipping Saxony's dove from +10 to -10.
  - **(D) Invert `harshness_bonus`** (`diplomacy.py:809-815`): Change `harshness_bonus = 5` to `harshness_bonus = -5`. Nations with history of harsh treaties are resistant, not pliable. Update `display_names.py` `FEEDBACK_STRINGS["harshness_bonus"]`: change `"positive"` text from "prior harsh terms make them more pliable" to "prior harsh terms breed resentment", change `"negative"` text to "no history of harsh terms".
  - **(E) Update `DEMAND_VALUES["gold_per_turn"]`** (`diplomacy.py:159`): Change from -0.02 to -0.05. Makes 100g = -5 deal_balance (meaningful) instead of -2 (negligible).
- **Files:** `diplomacy.py` (calculate_acceptance, harshness_bonus, DEMAND_VALUES, is_harsh threshold), `diplomatic_templates.py` (calculate_treaty_harshness), `display_names.py` (harshness_bonus strings)
- **Est. Tests:** ~7

---

### PL-11: Incoming AI Proposals Hijack Player Diplomatic Commands (API-Only) ✓ FIXED (Session 10)
- **Source:** Playtest (Apr 6) — curl/API playtest, NOT Godot
- **Summary:** When player sends a diplomatic command via `/command` API while an AI incoming_proposal is pending in the dialogue queue, the dialogue guard blocks the command and returns the AI proposal instead.
- **Godot impact: NONE.** Verified that Godot handles this correctly:
  - Incoming proposals arrive as **modal popups** (`incoming_proposal_popup.gd`) that block input until dismissed
  - The **diplomacy wizard** (`diplomacy_wizard.gd:210-216`) checks `dialogue_pending` flag from `/diplomatic_preview` and **gracefully closes** before issuing commands
  - Player input is **disabled** during popup display (`main.gd` line 2770)
  - The dialogue guard in `executor.py:461` only triggers via raw API calls that bypass Godot's popup system
- **Root cause:** The executor dialogue guard (`executor.py:460-470`) blocks ALL `/command` calls when `pending_diplomatic_dialogue` exists. This is correct safety behavior for the API, but confusing when using curl.
- **Priority:** P3 (API-only). No gameplay impact. Only affects automated testing and curl playtesting.
- **Proposed fix (low priority):** Improve the error message to say "An incoming proposal from {nation} requires your attention first. Use /respond_to_diplomatic_dialogue to handle it." Currently the message is generic and doesn't explain why the player's intended action was blocked.
- **Files:** `executor.py` (improve guard message)
- **Est. Tests:** ~2

---

### PL-5: Player Proposal — No Feedback Popup, Race Condition with AI
- **Source:** Playtest (Apr 6)
- **Summary:** Player sends a diplomatic proposal (e.g., non-aggression to Saxony). Gets "Expect a response by next turn." Result is buried in morning dispatch (easily missed). Meanwhile, the AI generates its OWN proposal of the same type on the same end-turn, creating a confusing race condition where Saxony rejects the player's harsh terms then immediately proposes a clean non-aggression pact.
- **Root cause:** `execute_proposal` (diplomatic_executor.py:895-994) sets `proposal_in_transit` and `talleyrand_state = "IN_TRANSIT"`. Resolution deferred to `_process_proposal_in_transit()` (world_state.py:4300-4493) which runs inside `advance_turn`. AI proposal generation runs BEFORE `advance_turn` (turn_manager.py:124-129), so AI generates proposals with no awareness that the player's proposal is pending.
- **Execution order (root of race):**
  1. Turn N: Player sends proposal → `proposal_in_transit = {turn_sent: N}`
  2. End turn: AI diplomatic phase runs (turn_manager.py:129) → AI proposes same type
  3. `advance_turn()` runs (turn_manager.py:151) → increments turn to N+1
  4. `_process_proposal_in_transit()` runs inside advance_turn (world_state.py:4066) → resolves player proposal
  5. Player sees both rejection AND the AI's new proposal — confusing
- **Sub-bugs:**
  - (a) No popup feedback: result is only in morning dispatch text, easily missed. Should be a popup like other diplomatic events.
  - (b) AI cooldown gap on rejection: when player's proposal is rejected, `player_proposal_cooldowns` blocks the *player* from re-proposing, but the AI's `_is_on_cooldown` (ai_diplomacy.py:222-239) only checks `ai_proposal_cooldowns` — AI immediately re-proposes same type
  - (c) AI cooldown gap on acceptance: when player's proposal is ACCEPTED in `_process_proposal_in_transit` (world_state.py:4355-4381), NO cooldown is set at all — not `player_proposal_cooldowns`, not `ai_proposal_cooldowns`. AI can propose next upgrade immediately
  - (d) `accept_counter_offer` path (diplomatic_executor.py:1773) doesn't call `apply_acceptance_cooldown` — this is PL-7
  - (e) AI dedup gap: `_has_pending_proposal_from` (ai_diplomacy.py:267-286) checks dialogues and queue but does NOT check `proposal_in_transit`. AI can propose to a nation the player already has a proposal in transit to.
  - (f) Failed counter-offer cooldown gap: when counter-offer generation fails (world_state.py:4454-4465), `player_proposal_cooldowns` set but NO `ai_proposal_cooldowns`. AI can immediately re-propose.
  - (g) Stale rejection cooldown gap: when proposal rejected as stale (world_state.py:4331-4346), NO cooldowns set at all — neither player nor AI. Both can immediately re-propose.
  - (h) Game-over leakage: `_process_proposal_in_transit` has no `game_over` guard — proposal resolves and queues a popup after victory/defeat screen.
- **Design decision:** Keep 1-turn deferral (Talleyrand "travels" to deliver — thematic). Fix the race via dedup + cooldowns. Add a popup so the result is unmissable.
- **Proposed fix — 3 parts:**
  - **Part A — Proposal result popup:** When `_process_proposal_in_transit` resolves (ACCEPT or REJECT), set a new `proposal_result_popup` on WorldState with the outcome. This popup fires on the next turn start via the existing PopupQueue priority system (`build_base_response` → `_include_popup_passthroughs`). Counter-offers already have a popup (incoming_proposal_popup with `is_counter_offer: true`) — no change needed for that path.
    - New popup type: `proposal_result_popup` — add to `PopupQueue.PRIORITY_ORDER` (below `incoming_proposal_popup`) and `RESPONSE_KEYS`
    - New WorldState property: `proposal_result_popup` (get/set via `_popup_queue`, same pattern as other popups)
    - Add to `to_dict`/`from_dict` for serialization
    - New Godot scene: `proposal_result_popup.tscn` + `proposal_result_popup.gd` — extends `PopupBase`, informational [Continue] button, same pattern as `coalition_declaration_popup.gd`
    - Popup data: `{ "target_nation": str, "proposal_type": str, "outcome": "ACCEPT"|"REJECT", "message": str, "feedback": str }`
    - Set in `_process_proposal_in_transit` after ACCEPT (line 4377), REJECT (line 4474), failed counter-offer (line 4460), AND stale rejection (line 4336) paths — all four resolution outcomes need the popup
    - Register in `main.gd` `_ready()` via `dialog_manager.register()`, wire in `_on_command_result()`
    - Dispatch events (`queue_dispatch_event`) stay as-is — dispatch is a text log, popup is the unmissable notification. No double-report concern since they serve different purposes.
  - **Part B — AI dedup + cooldowns:** Prevent the race condition.
    - `_has_pending_proposal_from` (ai_diplomacy.py:267): Add check — if `world.proposal_in_transit` exists and `proposal_in_transit["target"] == nation`, return True. Prevents AI from proposing to a nation the player already has a proposal targeting.
    - `_process_proposal_in_transit` ACCEPT path (world_state.py:4355-4381): Add `apply_acceptance_cooldown(target, self)` after `_ratify_treaty`. Uses the existing `ai_proposal_cooldowns` system so AI's `_is_on_cooldown` sees it.
    - `_process_proposal_in_transit` REJECT path (world_state.py:4468-4481): Already sets `player_proposal_cooldowns`. Additionally add AI cooldown: call `apply_rejection_cooldowns(target, ptype, self)` so the AI can't immediately re-propose the same type.
    - `_process_proposal_in_transit` failed counter-offer path (world_state.py:4454-4465): When counter-offer generation fails (counter_terms is None), the fallback treats it as rejection and sets `player_proposal_cooldowns` but NOT `ai_proposal_cooldowns`. Add `apply_rejection_cooldowns(target, ptype, self)` after line 4465 — same pattern as full REJECT.
    - `_process_proposal_in_transit` stale rejection path (world_state.py:4331-4346): When proposal is rejected as stale (diplomatic state changed during transit), NO cooldowns are set at all — neither player nor AI. Add `self.player_proposal_cooldowns[target] = 3` and `apply_rejection_cooldowns(target, proposal.get("type", ""), self)` before the early return at line 4346. Without this, the player can immediately re-propose and the AI can spam-propose to France after a stale rejection.
    - Both cooldown functions already exist in `ai_diplomacy.py` (lines 242-264) — just need to import and call them.
  - **Part C — PL-7 fix:** `accept_counter_offer` (diplomatic_executor.py:1785) — add `apply_acceptance_cooldown(source_nation, world)`. See PL-7 entry.
- **Edge cases:**
  - Popup priority: If proposal resolves on the same turn as a coalition declaration or sabotage discovery, the higher-priority popup shows first. The proposal result stays queued and shows on the next response cycle. This is correct — coalition is more urgent.
  - Stalled sabotage: Still defers by +1 turn (diplomatic_executor.py:952-955). Dedup check in Part B prevents AI from proposing during the extended transit. Popup fires when it finally resolves.
  - Counter-offer path: Already uses `incoming_proposal_popup` with `is_counter_offer: true` (world_state.py:4441-4451) and pushes a blocking dialogue (line 4403). No new popup needed — counter-offers already have proper UI.
  - Counter-offer rejected by player → then what? `reject_counter_offer` (diplomatic_executor.py:1802) sets `player_proposal_cooldowns`. Should also set AI cooldown. Add `apply_rejection_cooldowns(source_nation, ptype, world)` in `reject_counter_offer` handler.
  - Cooldown timing: Cooldowns set during `advance_turn` (inside `_process_proposal_in_transit`) are decremented in the SAME `advance_turn` call at line 4074 (`decrement_all`). So NATION_ACCEPTANCE_COOLDOWN=2 effectively becomes 1 turn of protection. Check: does `_process_proposal_in_transit` (line 4066) run BEFORE `decrement_all` (line 4074)? Yes — so cooldown is set to 2, then decremented to 1 in the same call. Effective protection = 1 turn. This may be too short — consider setting NATION_ACCEPTANCE_COOLDOWN=3 for the deferred path to get 2 effective turns. Or move decrement before proposal resolution. Simpler: just set cooldown to `NATION_ACCEPTANCE_COOLDOWN + 1` in the deferred path to compensate.
  - Stale proposal check (lines 4311-4346): Already handled — if diplomatic state changed during the deferred turn, proposal is rejected as stale. Popup fires for stale rejections too (player needs to know why their proposal failed). Cooldowns set in stale path (Part B) prevent immediate re-proposal.
  - Failed counter-offer (lines 4454-4465): When counter-offer generation fails, treated as rejection. Popup fires (Part A) and AI cooldowns set (Part B) so the AI can't immediately re-propose.
  - Proposal result popup vs morning dispatch: Both fire. Dispatch is the text log ("Talleyrand returns from Saxony..."), popup is the unmissable modal. Different purposes — no conflict.
  - Game-over state: If `world.game_over = True` during `advance_turn`, `_process_proposal_in_transit` still runs (no guard). A proposal could resolve and queue a popup after victory/defeat. Add `if self.game_over: self.proposal_in_transit = None; return []` as the first guard in `_process_proposal_in_transit` — discard in-transit proposals on game end, player won't need them.
  - PopupQueue serialization: `PopupQueue.to_dict()`/`from_dict()` serialize the entire `_queue` dict generically. Adding `proposal_result_popup` to `PRIORITY_ORDER` and `RESPONSE_KEYS` is sufficient — no separate serialization code needed.
  - Save/load mid-transit: `proposal_in_transit` serialized in `to_dict()` (line 3097) and `from_dict()` (line 3333). If player saves mid-transit and loads, proposal stays in transit and resolves normally on next end-turn. No bug.
- **Files:**
  - `world_state.py` — new `proposal_result_popup` property, set in ALL FOUR `_process_proposal_in_transit` resolution paths (ACCEPT/REJECT/failed-counter/stale), add cooldown calls in all four paths, game-over early return guard, to_dict/from_dict
  - `ai_diplomacy.py` — `_has_pending_proposal_from` dedup fix (add `proposal_in_transit` check)
  - `diplomatic_executor.py` — `accept_counter_offer` add acceptance cooldown, `reject_counter_offer` add AI rejection cooldown
  - `cooldown_manager.py` — add `proposal_result_popup` to PopupQueue PRIORITY_ORDER + RESPONSE_KEYS
  - `main.py` — no change needed (build_base_response handles popup passthrough automatically via R4)
  - `main.gd` — register new popup, wire in `_on_command_result`
  - New: `proposal_result_popup.gd` + `proposal_result_popup.tscn` (extends PopupBase, [Continue] button)
- **Scope:** Medium — no core flow changes. New popup + cooldown wiring + dedup guard.
- **Est. Tests:** ~12 new + ~4 existing tests updated

### PL-6: "Harsher" Terms on Friendship Pacts Demand Territory — Nonsensical
- **Source:** Playtest (Apr 6)
- **Summary:** Player proposes non-aggression pact to friendly Saxony (OPEN_BORDERS state, positive relations). Clicks "harsher" twice. System demands 150g/turn gold AND 1 territory cession from Saxony — for a *non-aggression pact*. This is extortion, not diplomacy. Saxony reasonably rejects. Player perceives acceptance odds barely changing because demand impact is tiny relative to base disposition.
- **Root cause:** `modify_harsh` handler (diplomatic_executor.py:996-1060) is proposal-type-blind. It extracts `proposal_type` at line 999 but never uses it for any type-aware logic. Lines 1015-1025 blindly add `gold_per_turn` (100g) and `territory_cede` (1 region on round 2) regardless of proposal type. The demand value rates in `DEMAND_VALUES` (diplomacy.py:158) are also weak: gold_per_turn = -0.02/gold (100g = -2 acceptance points), territory_cede = -5/region. Two rounds of escalation only subtract ~7 points from a base of ~30-50, barely perceptible.
- **Sub-bugs:**
  - (a) Type-blind escalation: territory demands make no thematic sense for non_aggression, open_borders, defensive_alliance, or alliance proposals
  - (b) Weak demand impact: 100g gold demand = -2 acceptance points. Player clicks "harsher" and sees acceptance barely move. 300g + 2 territory = -16 points — actually significant.
- **Proposal type categories:**
  - Friendship types: `non_aggression`, `open_borders`, `defensive_alliance`, `alliance` — demands are signing conditions, not reparations
  - War resolution types: `peace`, `armistice`, `armistice_losing`, `armistice_winning` — demands are war reparations, territory + gold make sense
  - Coercive types: `vassalage` — demands are subjugation terms, gold + territory make sense
- **Proposed fix:** Split `modify_harsh` by proposal type category (lines 1010-1025):
  - **Friendship types:** Round 1: add modest gold demand (100g). Round 2: BLOCKED — hide "Even harsher" button after round 1 (change `modify_count < 2` to `modify_count < 1` for friendship types), show message "A {proposal_type} cannot bear heavier demands, Sire." NO territory demands ever — strip any `territory_cede` from demands list as safety.
  - **War resolution types:** Round 1: add gold demand 300g (up from 100g). Round 2: add territory_cede value 2 (up from 1). 1.5x escalation of existing demands stays.
  - **Vassalage:** Same as war resolution (territory + gold are thematic for subjugation).
- **Pattern to follow:** `modify_generous` handler (lines 1103-1112) already type-checks proposal_type — uses `gold_per_turn` for war types and `gold_lump` for friendship types. Same pattern applies here.
- **Edge cases:**
  - `modify_count` is shared between harsh and generous directions. If player clicks generous then harsh, they hit the cap with fewer harsh rounds. Acceptable — 2 total modifications regardless of direction.
  - `_build_base_terms` for friendship types adds NO demands (confirmed: non_aggression is `pass`, alliance/defensive_alliance/open_borders add only `open_borders` clause). So the only demands for friendship types come from `modify_harsh` — clean separation.
  - `territory_cede` demand with no territory to cede: `_ratify_treaty` silently skips transfer if target doesn't control the region (lines 4666-4679). No crash, but confusing. Mitigated by not allowing territory demands on friendship types.
  - Acceptance formula `harshness_bonus` (+5 at line 837): applies when demands are detected. For friendship types with a 100g gold demand, the +5 bonus could counteract the -2 demand penalty, making harsh terms paradoxically better. Acceptable — the bonus represents intimidation factor, it's a design feature not a bug.
- **Files:** `diplomatic_executor.py` (modify_harsh handler lines 996-1060)
- **Est. Tests:** ~5

---

## P2 — MINOR

### PL-7: Counter-Offer Accept/Reject Missing AI Cooldowns
- **Source:** Playtest (Apr 6)
- **Summary:** When player accepts an AI counter-offer via `accept_counter_offer` (diplomatic_executor.py:1773), no `apply_acceptance_cooldown` is called. When player rejects via `reject_counter_offer` (line 1802), no AI cooldown is set either. The AI has no cooldown preventing it from immediately proposing again.
- **Root cause:** The `accept_ai_proposal` path (line 2163) correctly calls `apply_acceptance_cooldown(source_nation, world)`, but the `accept_counter_offer` path (line 1785) only calls `_ratify_treaty` without setting any AI cooldown. The `reject_counter_offer` path sets `player_proposal_cooldowns` but not `ai_proposal_cooldowns`.
- **Fix:**
  - `accept_counter_offer` (line ~1786): Add `apply_acceptance_cooldown(source_nation, world)`. Same pattern as `_handle_accept_ai_proposal` line 2164.
  - `reject_counter_offer` (line ~1815): Add `apply_rejection_cooldowns(source_nation, ptype, world)` so the AI can't immediately re-propose the same type. Counter-offers originate from the AI, so rejection should cool down the AI.
- **Edge cases:**
  - `source_nation` comes from `context.get("source_nation", target_nation)` — set correctly at `_process_proposal_in_transit` line 4424 (`"source_nation": target`), always the AI nation.
  - If `_ratify_treaty` returns a failure event, should cooldown still apply? Yes — match `_handle_accept_ai_proposal` which applies cooldown unconditionally. Prevents spam even on failed ratification.
  - No other acceptance paths are missing cooldowns: `accept_with_conflict` (line 1629) routes through `_handle_accept_ai_proposal` which has the cooldown. Verified all 3 acceptance paths.
  - This is also PL-5 Part C — the cooldown gaps feed into the race condition.
- **Files:** `diplomatic_executor.py` (lines ~1786 and ~1815, inside counter-offer handlers)
- **Est. Tests:** ~3

### PL-8: Counter-Offer Popup Looks Like Unsolicited AI Proposal ✓ FIXED (Session 9)
- **Source:** Playtest (Apr 6)
- **Summary:** When the player sends a proposal and the AI counter-offers, the result appears via `incoming_proposal_popup` — visually identical to an unsolicited AI proposal.
- **Fix (Session 9):** Visual differentiation in `incoming_proposal_popup.gd`:
  - Header: "[color=#7eb8da]COUNTER-OFFER[/color]" (blue) instead of "DIPLOMATIC ENVOY"
  - Context: "In response to your {type} proposal, {nation} offers modified terms:"
  - Border: Steel-blue (#7eb8da) instead of default gold
  - Labels: "Revised Terms" instead of "Terms", "Accept Terms"/"Reject Terms" buttons
  - Counter button hidden (no counter-counter — already worked)
  - Backend: Removed redundant "This is a counter-proposal..." from assessment text (popup itself now communicates this)
- **Counter-offer logic audit:** M3 algorithm confirmed working correctly. Score 30-49 triggers counter. Removes clause AI hates most, adds nation-specific sweeteners from NATION_DESIRES. Personality thresholds modify behavior (hawk stricter, dove lenient). Failed counters fall through to rejection with proper cooldowns. No bugs found.

---

### PL-15: Ultimatum Demand Wizard (CRITICAL) — OPEN
- **Source:** Playtest (Apr 7, Session 12 follow-up)
- **Priority:** P1 — CRITICAL (player cannot see or customize demands)
- **Absorbs PL-16** — Harsher Demands multiplier bug is eliminated by the wizard (no more blind escalation)

#### Symptoms
1. **No demands visible:** When "send ultimatum to X" fires, `proposal_confirm_popup` shows acceptance estimate but NOT the actual demands. Player blindly clicks "Deliver Ultimatum."
2. **No demand customization:** `generate_ultimatum_terms()` auto-generates demands. Player can only "Harsher Demands" (blind 1.5x multiplier) or "Reconsider." No way to pick what to demand.
3. **(PL-16) Harsher Demands too aggressive:** 1.5x multiplier + territory addition on Round 1 drops acceptance ~40% instead of ~10-15%.

#### Root Causes

**Popup key mismatch (symptom 1):**
- `_enrich_ultimatum_dialogue()` (`diplomatic_dialogue.py:440`) sets **`demands_display`**
- `proposal_confirm_popup.gd:_build_content()` (line 72) reads **`proposal_terms_summary`** — different key
- `ultimatum_confirm` dtype has no dedicated renderer — falls to `_:` default (`_build_content`), designed for proposals
- Header says "DIPLOMATIC PROPOSAL" (line 69) instead of "ULTIMATUM"
- `splash_damage_preview` and `threat_increase_preview` in dialogue dict but never rendered

**No wizard (symptoms 2 + 3):**
- Armistice/peace proposals have a full `terms_guidance` wizard: territory (region-by-region pick) → gold (more/less/skip) → AP → confirm (~300 lines, 12 action branches, 3 builder helpers)
- Ultimatums have nothing equivalent — just auto-generate + blind escalation
- The `modify_harsh_ultimatum` handler compounds a 1.5x multiplier AND adds new demand types simultaneously, which is why acceptance craters

#### Fix Plan: Ultimatum Demand Wizard

Model on the existing `terms_guidance` armistice wizard (`diplomatic_executor.py:1465-1728`). Same UX pattern, inverted direction: player builds **demands** (what target gives France) instead of **sweeteners** (what France offers target).

**§1. Entry point — replace current `_execute_diplomatic_ultimatum` flow**

Current flow: `_execute_diplomatic_ultimatum` → `generate_ultimatum_terms()` → push `ultimatum_confirm` dialogue with auto-generated terms + [Deliver | Harsher Demands | Reconsider].

New flow: `_execute_diplomatic_ultimatum` → push `ultimatum_confirm` dialogue with [Customize Demands | Use Suggested | Reconsider]. Suggested terms still come from `generate_ultimatum_terms()` as a default, but now they're a starting point, not the only option.

```
dialogue = {
    "type": "ultimatum_confirm",
    "target_nation": target_nation,
    "prompt": "What shall we demand of {target}, Sire?",
    "options": [
        {"label": "Customize Demands", "action": "adjust_ultimatum_terms"},
        {"label": "Use Suggested Terms", "action": "execute_ultimatum", "terms": auto_terms},
        {"label": "Reconsider", "action": "reconsider"},
    ],
    "terms": auto_terms,  # pre-calculated for display
    "splash_damage_preview": splash_preview,
    "threat_increase_preview": "+15 threat on delivery, +5 if accepted",
    "context": {"target_nation": target_nation},
    "blocking": True,  # prevent clear_stale dismissal mid-wizard
    "turn_created": int(world.current_turn),
}
```

Enrich with `_enrich_ultimatum_dialogue()` so the "Use Suggested" path still shows acceptance estimate.

**§2. Wizard state machine — `adjust_ultimatum_terms` entry**

New action handler in `_process_dialogue_choice`. Context tracks:
```python
context = {
    "target_nation": target_nation,
    "guidance_state": "gold",  # gold → territory → manpower → confirm
    "approved_demands": [],     # list of demand dicts {type, value, regions?} — same schema as generate_ultimatum_terms() output
    "gold_amount": 0,           # set by _build_ultimatum_gold_step() from gold source logic
    "gold_type": "gold_per_turn",  # or "gold_lump" — set by gold step based on target income
    "manpower_amount": 0,
}
```

**Empty demands guard:** If `approved_demands` is empty at the confirm step (player skipped all steps AND gating excluded territory/manpower), inject the gold floor demand: `{"type": "gold_lump", "value": 100}`. Talleyrand message: "We must demand something, Sire — at minimum a symbolic tribute." This matches the `generate_ultimatum_terms()` fallback (line 1373).

**§3. Gold step** — `_build_ultimatum_gold_step()`

Modeled on `_build_gold_step()` (line 2238). Calculates suggested gold from target income (same as `generate_ultimatum_terms` gold logic).

**Gold source logic:** If `target_income > 0`, demand `gold_per_turn` (capped at 50% of income, range 50-300). If `target_income == 0` but `target_gold > 0`, demand `gold_lump` (30% of gold, range 50-500). If both are 0, offer floor of 50 `gold_lump` ("symbolic tribute").

```
If gold_per_turn: "Talleyrand: How much gold should we demand per turn, Sire?"
If gold_lump:     "Talleyrand: How much gold should we demand as a one-time tribute, Sire?"
[Demand {X} gold]  [Demand more]  [Demand less]  [Skip gold]
```

Actions: `ultimatum_gold_accept`, `ultimatum_gold_more` (1.5x), `ultimatum_gold_less` (0.7x), `ultimatum_gold_skip`.

Gold floor: 25. Gold cap: 300 for per-turn, 500 for lump (same as `generate_ultimatum_terms`). More/less multipliers match armistice wizard (1.5x/0.7x).

**§4. Territory step** — `_build_ultimatum_territory_step()`

Only offered if France has military superiority (>1.2x, same threshold as `generate_ultimatum_terms`). If not, skip to manpower.

Modeled on armistice territory picker (setup lines 1498-1509, handlers 1540-1678). Picks from target's non-capital regions adjacent to France-controlled territory. Max 1 region if superiority < 2.0x, max 2 if >= 2.0x (scales with dominance).

```
"Shall we demand territory, Sire?"
[Yes, show me options]  [No, move to manpower]
```

Then region-by-region: "I suggest demanding {region}."
[Demand this region]  [Not this one]  [That's enough territory]

Actions: `ultimatum_territory_yes`, `ultimatum_offer_region`, `ultimatum_skip_region`, `ultimatum_enough_territory`, `ultimatum_territory_skip`.

Write new `rank_ultimatum_territory_candidates(world, player_nation, target_nation)` using the territory selection logic from `generate_ultimatum_terms()` (lines 1348-1363) as the base, extended with scoring for income and buildings (same factors as `rank_cession_candidates`). Ranks TARGET's non-capital regions by strategic value to France: adjacency to France-controlled territory, region income, buildings. Cannot reuse `rank_cession_candidates()` directly — it ranks PLAYER regions for cession, not target regions for seizure.

**§5. Manpower step** — `_build_ultimatum_manpower_step()`

Only offered if troop advantage > 5000 (same threshold as `generate_ultimatum_terms`).

```
"Shall we demand conscripts, Sire? Their army is weakened."
[Demand {X} manpower]  [Demand more]  [Demand less]  [Skip manpower]
```

Actions: `ultimatum_manpower_accept`, `ultimatum_manpower_more` (1.5x), `ultimatum_manpower_less` (0.7x), `ultimatum_manpower_skip`.

Default: `int(troop_advantage * 0.1)`, floor 500, cap 5000 (same bounds as `generate_ultimatum_terms`).

**§6. Confirm step** — `_build_ultimatum_confirm_step()`

Assembles final demands from `context["approved_demands"]`. Shows full preview:

```
"Here are our demands for {target}:"
  - 150 gold per turn
  - Cede Silesia
  - 2000 manpower
Acceptance estimate: ~45% (UNCERTAIN)
Splash damage: Austria (ALLIANCE): -15 relations
Threat: +15 on delivery
[Deliver Ultimatum]  [Start Over]  [Reconsider]
```

Calls `_enrich_ultimatum_dialogue()` on the assembled terms for acceptance calculation.

"Deliver Ultimatum" = `{"action": "execute_ultimatum", "terms": wizard_terms}` — terms embedded in option dict (same pattern as armistice `execute_proposal`, line 2348). Existing `execute_ultimatum` handler reads `selected.get("terms", {})`.
"Start Over" = `adjust_ultimatum_terms` (re-enter wizard).
"Reconsider" = pop dialogue (same as today).

**§7. Remove `modify_harsh_ultimatum`**

Delete the `modify_harsh_ultimatum` handler (lines 1259-1331). The wizard replaces it entirely — the player now has full control over demand amounts. No need for blind escalation.

Keep `generate_ultimatum_terms()` as-is — it provides the "Use Suggested Terms" default and can be used by AI ultimatums (R162) in the future.

**§8. Godot popup — dedicated ultimatum renderer**

Add `"ultimatum_confirm"` case to `proposal_confirm_popup.gd` match block (line 27):

```gdscript
"ultimatum_confirm":
    bbcode = _build_ultimatum_content(data)
```

New `_build_ultimatum_content(data)` reads:
- Header: `[b][color=#e09040]ULTIMATUM — {target}[/color][/b]`
- `demands_display` (list of strings) — demand line items
- `harshness_label` — always "Coercive" for ultimatums (color-coded red)
- `acceptance_estimate`, `acceptance_outcome`, `acceptance_hint` — same as proposals
- `splash_damage_preview` — format each `{nation, treaty_with_target, relation_penalty}`
- `threat_increase_preview` — string
- `talleyrand_text` OR `prompt` — Talleyrand commentary (entry-point dialogue uses `prompt`, wizard builders use `talleyrand_text`; renderer should read both with fallback: `data.get("talleyrand_text", data.get("prompt", ""))`)
- `dp_cost` — always 2

**Wizard step rendering:** The `terms_guidance` dtype wizard steps render through the `_:` default path (talleyrand_text + options only, no terms to display). Only the final `ultimatum_confirm` needs the dedicated renderer.

**Blocking:** All wizard step dialogues use `blocking: True` to prevent `clear_stale` from dismissing the wizard if the player ends a turn mid-wizard. The entry-point `ultimatum_confirm` dialogue also uses `blocking: True`.

#### Building Blocks Reuse

| Existing | Reused for |
|----------|-----------|
| `_build_gold_step()` (line 2238) | Pattern for `_build_ultimatum_gold_step()` — same more/less/skip UX |
| `_build_ap_step()` (line 2278) | Pattern for `_build_ultimatum_manpower_step()` — same accept/skip UX |
| `_build_confirm_step()` (line 2305) | Pattern for `_build_ultimatum_confirm_step()` — assemble + enrich + preview |
| `_copy_guidance_context()` (line 2232) | Reuse directly — same deep-copy of context dict |
| Territory picker (lines 1540-1678) | Pattern for `ultimatum_offer_region`/`skip_region` — same region-by-region flow |
| `generate_ultimatum_terms()` territory logic (lines 1348-1363) | Base for new `rank_ultimatum_territory_candidates()` — adjacency + capital exclusion. Extended with income/building scoring from `rank_cession_candidates` |
| `generate_ultimatum_terms()` | Kept for "Use Suggested" default + future AI ultimatums (R162) |
| `_enrich_ultimatum_dialogue()` | Reuse directly on confirm step — acceptance calculation |

#### Effort Estimate

- **~150-200 new lines** in `diplomatic_executor.py`: 3 builder helpers + ~10 action handler branches + empty demands guard
- **~30 lines** in `diplomatic_templates.py`: new `rank_ultimatum_territory_candidates()` helper
- **~50 lines** in `proposal_confirm_popup.gd`: dedicated ultimatum renderer
- **Delete ~70 lines**: `modify_harsh_ultimatum` handler
- **Net: ~160-210 lines added**
- **No new files, no new scenes** — reuses existing `proposal_confirm_popup` and `terms_guidance` dtype

#### Files to Modify
- `backend/commands/diplomatic_executor.py` — wizard handlers + builder helpers, remove `modify_harsh_ultimatum`
- `backend/game_logic/diplomatic_dialogue.py` — no changes (enrichment function already works)
- `backend/game_logic/diplomatic_templates.py` — add `rank_ultimatum_territory_candidates()` helper (keep `generate_ultimatum_terms` for defaults)
- `godot-client/project-sovereign/scripts/proposal_confirm_popup.gd` — add `_build_ultimatum_content()`, add match case

#### Test Plan
- **Backend wizard flow:** Test each wizard step transitions (gold → territory → manpower → confirm)
- **Gold more/less:** Assert 1.5x/0.7x scaling, floor 25, cap 300 (per-turn) / 500 (lump)
- **Territory gating:** Assert territory step only offered with >1.2x military superiority
- **Region pick:** Assert only non-capital adjacent regions offered
- **Manpower gating:** Assert manpower step only offered with >5000 troop advantage
- **Confirm step:** Assert `_enrich_ultimatum_dialogue()` called, acceptance estimate present
- **"Use Suggested":** Assert `generate_ultimatum_terms()` default still works as fast path
- **Execute:** Assert wizard-built terms pass through to existing `execute_ultimatum` handler
- **Empty demands guard:** Skip gold + territory gated out + manpower gated out → confirm step injects gold floor demand (100 gold_lump). Delivery still works.
- **Cooldown blocking:** Assert `ultimatum_global_cooldown > 0` prevents entering wizard (error returned before dialogue push)
- **Concurrent dialogue:** AI proposal arrives mid-wizard → queued. Wizard completes → AI proposal auto-promotes via `promote_if_empty()`
- **Gold_lump fallback:** Target with 0 income but positive gold → wizard offers gold_lump instead of gold_per_turn
- **Remove tests:** Delete/update `TestModifyHarshUltimatum` tests (handler removed)
- **curl test:** `curl -X POST http://127.0.0.1:8005/command -H "Content-Type: application/json" -d '{"command": "send ultimatum to Prussia"}' | python -m json.tool` — verify new dialogue structure
- **Godot visual:** Popup shows demands, splash damage, threat warning, acceptance estimate, harshness label
- **PL-18 integration:** Wizard manpower step shows typed pools (infantry/cavalry/artillery), generates typed demand keys, acceptance scales by scarcity
- **PL-19 integration:** Wizard confirm step shows dynamic diplomatic cost preview with severity label (mild/moderate/severe/extreme)
- **Note:** Mid-wizard state changes (elimination, cooldown expiry, vassal change) are impossible — wizard dialogue is blocking, turn cannot advance. No guards needed.

#### Audit Amendments (Apr 8, adversarial audit)

**AM-15.1 (FAIL-3): Treaty overwrite — gold_per_turn demand destroys existing treaty.**
`_apply_ultimatum_demands()` line 689 does `world.active_treaties[diplo_key] = {...}`, silently replacing any pre-existing ALLIANCE/trade treaty with the ultimatum tribute dict. All prior clauses (AP, gold_per_turn, manpower_per_turn) are lost.
- **Fix:** Before overwriting, check for existing treaty. If one exists, append the ultimatum gold clause to the existing treaty's `clauses` list instead of replacing. If no existing treaty, create the new `ultimatum_tribute` entry as before.
- **Alternative:** Use a separate key: `diplo_key + "_ultimatum_tribute"`. Requires `_process_treaty_clauses` to iterate both keys. Simpler but creates dual-treaty complexity.
- **Recommendation:** Append clauses to existing treaty. Simpler for the processing path.
- **Test:** Create world with existing ALLIANCE treaty between France and target (with gold_per_turn clause). Issue ultimatum with gold_per_turn demand. Verify original alliance clauses preserved AND ultimatum tribute clause added.

**AM-15.2 (FAIL-4): ARMISTICE state not blocked for ultimatums.**
Pre-validation blocks WAR and vassal but NOT ARMISTICE. An armistice means both sides just agreed to peace — delivering an ultimatum is diplomatically incoherent. War declaration during armistice IS blocked (line 456-462).
- **Fix:** Add `if current_state == "ARMISTICE": return error("Cannot issue ultimatum during armistice — honor the peace agreement first")` after the WAR check in `_execute_diplomatic_ultimatum`.
- **Test:** Set diplomatic state to ARMISTICE between France and target. Attempt ultimatum. Assert blocked with appropriate message.

**AM-15.3 (FAIL-11): PL-15 gold_lump floor demand has zero acceptance penalty until PL-18 lands.**
The empty-demands guard (§2) injects `{"type": "gold_lump", "value": 100}`. But `DEMAND_VALUES` has no `"gold_lump"` key until PL-18 adds it. If PL-15 ships before PL-18, the floor demand is cosmetic-only in the acceptance formula.
- **Fix:** Bundle the `DEMAND_VALUES` additions from PL-18 §A into PL-15 as a prerequisite. At minimum, add `"gold_lump": -3 / 100` to `DEMAND_VALUES` in the PL-15 implementation. The remaining PL-18 typed manpower keys can land later.
- **Implementation order:** PL-18 §A (DEMAND_VALUES) → PL-15 wizard → PL-18 §B-H (typed manpower). Or: fold `gold_lump` key into PL-15 directly.

**AM-15.4 (W-11): Popup key mismatch — `demands_display` vs `proposal_terms_summary`.**
Already documented in §8 Godot popup section. Confirming: the dedicated `_build_ultimatum_content()` renderer in §8 reads `demands_display` correctly. The `_:` default path (for proposals) reads `proposal_terms_summary`. As long as the `ultimatum_confirm` match case is added, this is resolved. **No additional fix needed — §8 already covers this.**

**AM-15.5 (W-12): `"Coercive"` harshness label shows as green in popup.**
`proposal_confirm_popup.gd:80-89` maps "Moderate"=yellow, "High"=orange, "Very High"=red. Default=green. "Coercive" falls to green.
- **Fix:** Add `"Coercive"` to the match block in `_build_ultimatum_content()` (§8). Map to red (`#e04040`). This is already covered by §8's dedicated renderer — just ensure the color mapping is included.

**AM-15.6 (FAIL-12): Wizard has no state machine for PL-18 multi-type manpower selection.**
PL-15 §5 designs a single manpower step. PL-18 adds infantry/cavalry/artillery type picking + multiple demands. No state machine changes specified.
- **Fix:** PL-15 implements a single manpower step as designed (generates `"manpower_infantry"` by default). PL-18 upgrades the manpower step to show type selection: sub-states within the manpower step (`manpower_type_pick` → `manpower_amount` → `manpower_another?`). PL-18 §G should include explicit state machine pseudocode for the type picker. See PL-18 amendments.

**AM-15.7 (W-16): `generate_ultimatum_terms()` scans all regions — Golden Rule 8 violation.**
Line 1325-1327 iterates `world.regions.values()` to compute `target_income`. Should use `world.get_nation_regions(target_nation)` for cached lookup.
- **Fix:** Replace `for region in getattr(world, 'regions', {}).values(): if region.controller == target_nation:` with `for name in world.get_nation_regions(target_nation): region = world.regions.get(name); if region:`. Same for `france_regions` and `target_regions` below. Note: this is a pre-existing issue, not introduced by PL-15.

---

### PL-16: Harsher Demands Multiplier Too Aggressive — ABSORBED INTO PL-15
- **Source:** Playtest (Apr 7, Session 12 follow-up)
- **Priority:** P2 — UX (gameplay balance)
- **Status:** Absorbed into PL-15. The demand wizard eliminates `modify_harsh_ultimatum` entirely — the player picks their own demand amounts instead of blind escalation. No separate fix needed.

---

### PL-17: Manpower demand has zero acceptance penalty — ABSORBED INTO PL-18
- **Source:** PL-15 audit (Apr 7, 2026)
- **Priority:** P2 — gameplay balance
- **Status:** Absorbed into PL-18. The key mismatch fix (`DEMAND_VALUES` missing `"manpower"`) is inseparable from PL-18's typed demand keys — PL-18 supersedes the simple 1-line fix with per-type keys that also resolve the mismatch. See PL-18 §A for details.

---

### PL-18: Typed manpower demands + DEMAND_VALUES key fixes — OPEN (absorbs PL-17)
- **Source:** PL-15 audit (Apr 7, 2026). Upgraded Apr 8 — user wants player to choose manpower type. Absorbs PL-17 after Apr 8 audit found the two are inseparable.
- **Priority:** P2 — gameplay balance
- **Summary:** Three problems: (1) **PL-17 bug:** `DEMAND_VALUES` uses key `"manpower_per_turn"` but ultimatums use `"manpower"` — manpower demands have zero acceptance penalty. (2) **Same bug for gold_lump:** `DEMAND_VALUES` has `"gold_per_turn"` but not `"gold_lump"` — lump-sum gold demands also have zero acceptance penalty. (3) Manpower demands only transfer infantry silently — player should choose unit type with scarcity-appropriate acceptance costs.

- **Root cause:** Key mismatches in `DEMAND_VALUES` (`diplomacy.py:159`). The dict was written for treaty clauses (ongoing `"manpower_per_turn"`, `"gold_per_turn"`), but ultimatum demands use different keys (`"manpower"`, `"gold_lump"`). Additionally, `_apply_ultimatum_demands()` in `diplomatic_executor.py:713-724` hardcodes infantry transfers, and `calculate_treaty_harshness()` in `diplomatic_templates.py:1826` only checks `"manpower_per_turn"`, missing `"manpower"` entirely.

- **Design decision (resolved Apr 8 audit):** Use **typed demand keys** for manpower (`"manpower_infantry"`, `"manpower_cavalry"`, `"manpower_artillery"`), NOT a nested `unit_type` field. Rationale: matches existing pattern where `"gold_per_turn"` and `"gold_lump"` are separate keys, not `"gold"` with a `subtype` field. Keeps `DEMAND_VALUES` lookup simple — `DEMAND_VALUES.get(dtype, 0)` works without special-casing. Acceptance formula, harshness calc, and PL-19 relation penalty all read dtype directly.

- **Proposed fix:**

  **(A) DEMAND_VALUES — fix all missing keys** (`diplomacy.py:159`):
  ```python
  DEMAND_VALUES = {
      "gold_per_turn": -5 / 100,           # -5 per 100g/turn (existing, for treaties)
      "gold_lump": -3 / 100,               # -3 per 100g lump (NEW — was missing)
      "manpower_per_turn": -3 / 2000,      # -3 per 2000/turn (existing, for treaties)
      "manpower_infantry": -3 / 2000,      # -3 per 2000 infantry (NEW)
      "manpower_cavalry": -5 / 2000,       # -5 per 2000 cavalry (NEW — scarcer)
      "manpower_artillery": -8 / 2000,     # -8 per 2000 artillery (NEW — rarest)
      "territory": -5,                     # -5 per region (existing)
      "territory_cede": -5,                # alias (existing)
      "ap_per_turn": -25,                  # -25 per AP (existing)
      "unit_swap": -2,                     # -2 per trade (existing)
  }
  ```
  Keep `"manpower_per_turn"` for treaty clauses (different system). Add backward-compat fallback: legacy `"manpower"` demands (from old saves) should be handled in acceptance calc as `"manpower_infantry"` rate.

  **(B) Demand structure — typed keys:**
  ```python
  # New demand format:
  {"type": "manpower_infantry", "value": 2000}
  {"type": "manpower_cavalry", "value": 1000}
  {"type": "manpower_artillery", "value": 500}
  {"type": "gold_lump", "value": 300}   # already uses this key, now has penalty
  ```

  **(C) Auto-generation — `generate_ultimatum_terms()` in `diplomatic_templates.py:1365-1370`:**
  - Change `{"type": "manpower", "value": N}` to `{"type": "manpower_infantry", "value": N}` (default auto-generated demand stays infantry — most common, largest pools).
  - Wizard step (PL-15) lets player swap type or split across types.
  - Cap per type based on target's actual pool: `min(demand, target_pool[unit_type])`. Don't offer cavalry if target has <500 cavalry, don't offer artillery if <300.

  **(D) Application — `_apply_ultimatum_demands()` in `diplomatic_executor.py:713-724`:**
  ```python
  elif dtype.startswith("manpower"):
      # Extract unit type from demand key: "manpower_infantry" → "infantry"
      unit_type = dtype.split("_", 1)[1] if "_" in dtype else "infantry"
      from_pool = world.manpower_pools.get(target_nation, {})
      to_pool = world.manpower_pools.get(player, {})
      transfer = min(int(value), from_pool.get(unit_type, 0))
      if transfer > 0 and target_nation in world.manpower_pools:
          world.manpower_pools[target_nation][unit_type] = max(
              0, from_pool.get(unit_type, 0) - transfer)
      if transfer > 0 and player in world.manpower_pools:
          world.manpower_pools[player][unit_type] = (
              to_pool.get(unit_type, 0) + transfer)
      if transfer > 0:
          type_label = {"infantry": "infantry conscripts",
                        "cavalry": "cavalry mounts",
                        "artillery": "artillery batteries"}.get(unit_type, "conscripts")
          descriptions.append(f"{transfer} {type_label}")
  ```
  Backward compat: bare `"manpower"` (no underscore) falls through to `"infantry"` default.

  **(E) Harshness calculation — `calculate_treaty_harshness()` in `diplomatic_templates.py:1826`:**
  Add entries for new keys:
  ```python
  elif dtype == "manpower_infantry":
      harshness += 0.10
  elif dtype == "manpower_cavalry":
      harshness += 0.15
  elif dtype == "manpower_artillery":
      harshness += 0.20
  elif dtype == "gold_lump":
      harshness += 0.05 * max(1, int(value) // 100)
  ```

  **(F) Display — `_enrich_ultimatum_dialogue()` in `diplomatic_dialogue.py:424-440`:**
  - Map typed keys to display: `"manpower_infantry"` → "2,000 infantry conscripts", `"manpower_cavalry"` → "1,000 cavalry mounts", `"manpower_artillery"` → "500 artillery batteries".

  **(G) Wizard integration (PL-15):**
  - Demand wizard manpower step shows target's available pools: "Infantry: 20,000 | Cavalry: 3,000 | Artillery: 2,000"
  - Player picks type and amount (preset options: 500 / 1,000 / 2,000 / 5,000)
  - Multiple manpower demands allowed (e.g., `manpower_infantry` + `manpower_cavalry`)
  - Don't show types with pool < 300 (not worth demanding)
  - Acceptance estimate updates as player adjusts

  **(H) Acceptance calc backward compat** (`diplomacy.py`, `calculate_acceptance()`):
  - In the demand iteration loop (~line 736), add fallback: if `dtype == "manpower"`, treat as `"manpower_infantry"` for DEMAND_VALUES lookup. Handles old saves gracefully.

- **Files:** `backend/game_logic/diplomacy.py` (DEMAND_VALUES + acceptance fallback), `backend/game_logic/diplomatic_templates.py` (generate_ultimatum_terms, harshness calc), `backend/commands/diplomatic_executor.py` (_apply_ultimatum_demands), `backend/game_logic/diplomatic_dialogue.py` (_enrich_ultimatum_dialogue)
- **Est. Tests:** 12 — (1) manpower_infantry demand reduces acceptance, (2) manpower_cavalry costs more than infantry, (3) manpower_artillery costs most, (4) gold_lump demand now reduces acceptance, (5) bare "manpower" backward compat defaults to infantry rate, (6) infantry transfers from infantry pool, (7) cavalry transfers from cavalry pool, (8) artillery transfers from artillery pool, (9) demand capped at target pool size, (10) display strings show correct type labels, (11) harshness calc includes typed manpower + gold_lump, (12) wizard doesn't offer types with pool < 300
- **Implement with:** PL-15 wizard session (Session A). DEMAND_VALUES keys must land first, then wizard generates typed demands, then display/application code handles them.

#### Audit Amendments (Apr 8, adversarial audit)

**AM-18.1 (FAIL-5 partial): `calculate_treaty_harshness()` ignores bare `"manpower"` demands.**
Current harshness calc (diplomatic_templates.py:1812-1828) handles `"manpower_per_turn"` but NOT bare `"manpower"` (the key used by existing ultimatums). PL-18 §E adds entries for the new typed keys but not bare `"manpower"`.
- **Fix:** Add backward compat in §E: `elif dtype == "manpower": harshness += 0.10` (same as infantry). This handles old saves and the transition period.

**AM-18.2 (FAIL-12): Wizard manpower type selection needs state machine design.**
PL-15 §5 has a single manpower step. PL-18 §G says "wizard step shows typed pools" and "multiple manpower demands allowed" but gives no state machine.
- **Fix:** Add explicit sub-state flow to §G:
  1. Entry: `ultimatum_manpower_type` — "What type of conscripts, Sire?" [Infantry: {pool}] [Cavalry: {pool}] [Artillery: {pool}] [Skip manpower]. Hide types with pool < 300.
  2. After type pick: `ultimatum_manpower_amount` — "How many {type}?" [Demand {suggested}] [More] [Less] [Skip]. Same more/less logic as §5.
  3. After amount: `ultimatum_manpower_another` — "Demand another type?" [Yes, show types] [No, continue to confirm]. Filter out already-demanded types.
  4. Loop back to step 1 (filtered) or proceed to confirm step.
- **Context fields:** Add `manpower_demands: list` to context (accumulates `{type, value}` dicts). Replace single `manpower_amount`.

**AM-18.3 (W-14): New demand keys undocumented in SAVE_FORMAT_REFERENCE.md.**
`"manpower_infantry"`, `"manpower_cavalry"`, `"manpower_artillery"`, `"gold_lump"` can appear in dialogue state (demands list) and `diplomatic_history`. Save format reference doesn't document valid demand type values.
- **Fix:** Add a "Demand Types" subsection to SAVE_FORMAT_REFERENCE.md listing all valid demand `type` values with descriptions.

**AM-18.4 (W-17): Negative demand values produce positive acceptance contribution.**
Main acceptance formula at diplomacy.py:748 computes `DEMAND_VALUES.get(dtype, 0) * value`. If value is negative (corrupted save, mod), this produces a positive contribution. PL-19 uses `abs(value)` but the main acceptance loop doesn't.
- **Fix:** Add to §H (acceptance backward compat): in the demand iteration loop, use `abs(value)` for all demand types, matching PL-19's approach: `dvalue = abs(d.get("value", 0))`.

---

### PL-19: Ultimatum relation penalty is flat regardless of demands — OPEN
- **Source:** PL-15 balance review (Apr 8, 2026)
- **Priority:** P2 — gameplay balance
- **Summary:** Delivering an ultimatum always costs exactly -10 relation to the target, whether you demand 100 gold or annex their capital + half their army. This makes aggressive demands too cheap diplomatically. Taking land via ultimatum (-10) costs less than declaring war with casus belli (-15), which is backwards.
- **Current behavior:** `_execute_diplomatic_ultimatum()` in `diplomatic_executor.py:1161` applies flat `-10` on delivery, flat `-5` on rejection. Splash damage to bystanders is also flat (tiers of -5 to -15 based on their relation to target, not demand severity).

- **Comparison table (why -10 is wrong):**

  | Action | Relation hit to target | Relation hit to bystanders |
  |--------|----------------------|---------------------------|
  | Ultimatum (any demands) | -10 (flat) | -5 to -15 (flat tiers) |
  | War declaration (with CB) | -15 | -15 (all) |
  | War declaration (no CB) | -30 | -15 (all) |
  | Treaty breaking (alliance) | -40 | -10 (all) |

  Demanding territory via ultimatum should be diplomatically comparable to war, not trivially cheap.

- **Proposed fix:**

  **(A) Dynamic base penalty — scale with demand severity:**
  Use the existing `DEMAND_VALUES` weights (already negative) to compute demand severity, then add to the base penalty. **Depends on PL-18** — typed manpower keys (`manpower_infantry` etc.) and `gold_lump` must exist in DEMAND_VALUES first. The `startswith("manpower")` pattern handles all typed keys automatically.

  ```python
  # In _execute_diplomatic_ultimatum(), replace flat -10:
  base_penalty = -10
  demand_penalty = 0
  for d in demands:
      dtype = d.get("type", "")
      value = d.get("value", 0)
      if dtype in ("territory_cede", "territory"):
          # Income-weighted cost per region (flat -5 × weight, NOT PL-20's
          # escalating formula — PL-19 §C multiplier handles count scaling
          # separately via demanded_count/remaining amplifiers).
          regions = d.get("regions", [])
          for r in regions:
              region = world.regions.get(r)
              income = getattr(region, 'income', 100) if region else 100
              income_weight = max(0.5, income / 100)
              region_cost = -5 * income_weight
              if r == NATION_CAPITALS.get(target_nation):
                  region_cost *= 2
              demand_penalty += region_cost
      else:
          rate = DEMAND_VALUES.get(dtype, 0)
          demand_penalty += rate * abs(value)   # scaled by amount
  
  # base_penalty is -10, demand_penalty ≤ 0, so sum is always ≤ -10.
  # Clamp to [-60, -10] range (no separate -5 floor needed).
  total_penalty = max(-60, int(base_penalty + demand_penalty))
  world.modify_nation_relation(player, target_nation, total_penalty)
  ```

  **Example outcomes (income-weighted):**
  - 100 gold/turn only: -10 base + (-5) = **-15**
  - 1 rural province (50 income): -10 + (-2.5) = **-13**
  - 1 town (100 income): -10 + (-5) = **-15**
  - 1 city (150 income): -10 + (-7.5) = **-18**
  - Vienna (capital, 300 income): -10 + (-30) = **-40**
  - 2 towns + 5,000 infantry: -10 + -10 + -7.5 = **-28**
  - Vienna + gold + AP: -10 + -30 + -5 + -25 = **-60** (cap)
  - Minimum (zero demand penalty): **-10** (base_penalty alone, demand_penalty = 0)
  - Minimum (tiny gold demand): **-13** (base + small demand_penalty, after rounding)
  - Maximum: capped at **-60** (raised from -50 to accommodate income-weighted territory)

  **(B) Rejection penalty also scales:**
  Replace flat `-5` on rejection with `-5 + int(demand_penalty * 0.3)`. Rejecting outrageous demands adds more bitterness. Minimum -5, maximum -15.

  **(C) Splash damage scales with severity:**
  Current splash multiplier is 1.0 (flat). Scale by demand severity:
  ```python
  splash_multiplier = max(1.0, min(2.5, abs(total_penalty) / 10))
  ```
  So a -10 penalty → 1.0x splash (unchanged), -25 penalty → 2.5x splash (allies of target are much more alarmed). Example: ALLIANCE splash goes from flat -15 to -15 × 2.5 = -37 for outrageous demands.

  **(D) Acceptance hint integration:**
  The acceptance estimate in `_enrich_ultimatum_dialogue()` already shows what the AI thinks. Add a "diplomatic cost" line to the wizard preview: "Diplomatic cost: -20 relation (moderate)" / "Diplomatic cost: -45 relation (severe — allies will react strongly)"

  **Severity labels:**
  - -10 to -15: "mild" (routine demand)
  - -16 to -25: "moderate" (notable diplomatic cost)
  - -26 to -40: "severe" (will strain all relationships)
  - -41 to -60: "extreme" (near-war diplomatic damage)

  **(E) Threat scaling (optional, recommend):**
  Current: flat +15 threat on delivery, +5 on acceptance, +8/region annexed. Recommend also scaling delivery threat with demand severity: `threat = max(10, min(30, 15 + abs(demand_penalty) // 3))`. Light demands → 10-15 threat, heavy demands → 25-30 threat.

- **Design rationale:** The relationship scale is -100 to +100. France starts at -30 with Austria, -40 with Prussia, -80 with Britain. A flat -10 for any ultimatum means you can strip territory from a neutral nation and still only drop 10 points. With dynamic scaling, demanding territory (-20) puts you firmly into hostile range, which feels right — you just threatened to take their land. But it's still less than war declaration (-30 no CB), rewarding the "diplomacy before violence" path.

- **Files:** `backend/commands/diplomatic_executor.py` (_execute_diplomatic_ultimatum lines 1157-1213, splash damage 1163-1178), `backend/game_logic/diplomatic_dialogue.py` (_enrich_ultimatum_dialogue — add cost preview), `backend/game_logic/diplomacy.py` (DEMAND_VALUES import)
- **Est. Tests:** 10 — (1) gold-only demand ≈ -15 relation, (2) territory demand scales with income weight, (3) capital territory gets ×2 (double weight), (4) multi-demand stacks correctly, (5) clamped at -60 floor, (6) minimum penalty is -10 (base_penalty alone, no demand cost), (7) rejection penalty scales with demand_penalty, (8) splash multiplier scales with severity (1.0× at -10, 2.5× at -25+), (9) §C amplifier: ×2.5 annex / ×2.0 rump / ×1.5 for 4+ / ×1.2 for 2-3, (10) territory penalty uses flat income-weighted cost (not PL-20 escalation)
- **Depends on:** PL-18 (typed DEMAND_VALUES keys must exist for penalty calc to work correctly)
- **Implement with:** Session B (after PL-15 + PL-18 are stable). Backend calculation can land first, then display wiring. Wizard preview (PL-15 confirm step) should show the dynamic cost — see PL-15 test plan "PL-19 integration" note.

#### Audit Amendments (Apr 8, adversarial audit)

**AM-19.1 (FAIL-7): Spec examples use wrong rounding — `int(-12.5)` = -12, not -13.**
Python `int()` truncates toward zero: `int(-12.5) = -2` (WRONG — should be -12, and spec says -13). The spec examples show rounded values, but `int()` truncates, not rounds. "1 rural province (50 income): -10 + (-2.5) = -13" — actually `int(-12.5) = -12`.
- **Fix:** Use `math.floor()` instead of `int()` for negative penalty calculations. `math.floor(-12.5) = -13`. Update formula: `total_penalty = max(-60, math.floor(base_penalty + demand_penalty))`. All spec examples then match implementation.
- **Applies to:** §A `total_penalty`, §B `rejection_penalty`. Both should use `math.floor()`.
- **Test:** Assert `total_penalty` for rural province (income 50) is -13, not -12.

**AM-19.2 (FAIL-8): Splash multiplier produces float relation changes.**
`splash_multiplier = max(1.0, min(2.5, abs(total_penalty) / 10))`. ALLIANCE splash: `-15 * 2.5 = -37.5`. Violates Golden Rule 2 (all numbers to Godot: `int()`). `modify_nation_relation` may not handle floats.
- **Fix:** Wrap splash result: `int(math.floor(-penalty * splash_multiplier))`. Apply `int()` wrapping to all relation change calls in the splash loop.
- **Test:** Assert splash damage for ALLIANCE at max multiplier is -37 (int), not -37.5 (float).

**AM-19.3 (W-8): Cumulative splash damage can be extreme (-112.5 across 3 allies).**
If 3 nations are allied with the target, total splash = 3 × -37 = -111 relation points. A single ultimatum can demolish France's entire diplomatic position.
- **Acknowledged:** This is intentional — aggressive ultimatums SHOULD have severe consequences. No cap on cumulative splash. The player can see the splash preview in the wizard (PL-15 §6) and decide if it's worth it. **No fix needed**, but add a test verifying multi-bystander splash accumulates correctly.

**AM-19.4 (W-10): Acceptance calculated AFTER -10 relation applied — double-dip.**
The execute_ultimatum handler applies relation penalty (line 1161) BEFORE calculating acceptance (line 1183). Since acceptance reads `nation_relations`, the -10 hit double-dips as both consequence AND acceptance penalty.
- **Fix:** Calculate acceptance BEFORE applying the relation penalty. Move the `calculate_acceptance()` call to before the `modify_nation_relation()` call in the execute_ultimatum handler. The relation penalty is a consequence of delivery, not a factor in the target's decision.
- **Test:** Assert acceptance score is the same regardless of when relation penalty is applied (calculate before apply).

**AM-19.5: `income` → `income_value` in territory penalty formula.**
§A uses `getattr(region, 'income', 100)`. Region class uses `income_value`. **PL-22 fixes the pre-existing code bug. Spec must match.**
- **Fix:** Change all `getattr(region, 'income', 100)` to `getattr(region, 'income_value', 100)` in §A.

---

### PL-20: No guard against diplomatic elimination — last territory demand — OPEN
- **Source:** Balance review (Apr 8, 2026). Inspired by EU4 aggressive expansion / full annexation mechanics.
- **Priority:** P2 — gameplay balance
- **Summary:** Two problems: (1) No code path prevents demanding a nation's last territory via ultimatum or treaty, diplomatically eliminating them — no extra penalty, no warning. (2) The flat per-region acceptance cost (-5 each) doesn't escalate — demanding 10 regions costs only -50, which is achievable with military dominance (~105 max bonus). In EU4, province war score cost limits you to a handful of provinces per war even from a huge empire. Here, you could take 67% of Russia in a single peace deal. Fix: escalating per-region cost (-5, -8, -11, -14, ...) so each additional region is harder, plus elimination guards for rump/annex states.

- **Current behavior — no guards on any path:**

  | Path | Capital protected? | Last-territory guard? | Fraction guard? | Extra cost? |
  |------|-------------------|----------------------|----------------|-------------|
  | Ultimatum auto-generation | Yes (skipped in `generate_ultimatum_terms()` line 1355) | **No** | **No** | **No** |
  | Ultimatum application | N/A (applied blindly) | **No** — `_apply_ultimatum_demands()` line 699 transfers without checking | **No** | **No** |
  | Treaty cession | No (capital gets 2x acceptance penalty) | **No** — `world_state.py` line 4784 applies then eliminates at 4817 | **No** | **No** |
  | Acceptance formula | Capital gets 2x weight | **No** elimination-threatening modifier | **No** — linear -5/region only | **No** |
  | Combat capture | N/A | **No** (correctly triggers elimination — military conquest is fine) | N/A | N/A |

  **Vulnerable nations (current map):** Saxony (2 regions), Prussia (2 regions) — one demand from rump state. Austria (4), Britain (3) — somewhat safer.

  **Scaling concern (1805 Europe):** Map is scaling to full 1805 Europe with many more regions. Per-region cost (-5) alone isn't enough — demanding 10 of 15 regions (-50 penalty) is still achievable with military dominance (max acceptance bonus ~105). A percentage-based penalty is needed so large nations can't lose most of their territory in a single diplomatic action.

  **Math showing the gap (demand_total is UNCAPPED):**

  | Scenario | Regions demanded | demand_total | Max positive bonus | Net | Result |
  |----------|-----------------|-------------|-------------------|-----|--------|
  | 2 of 2 (Saxony full annex) | 2 | -10 | ~105 | 95 | ACCEPT trivially |
  | 4 of 4 (Austria full annex) | 4 | -20 | ~105 | 85 | ACCEPT easily |
  | 10 of 15 (Russia 67%) | 10 | -50 | ~105 | 55 | ACCEPT with dominance |
  | 15 of 15 (Russia full annex) | 15 | -75 | ~105 | 30 | REJECT |
  | 8 of 12 (large nation 67%) | 8 | -40 | ~105 | 65 | ACCEPT with dominance |

- **Proposed fix:**

  **(A) Escalating per-region acceptance penalty — absolute count, not fraction:**
  In EU4, you can't take half of a huge empire in one war — even with 100% war score, the province cost limits you to a handful of provinces. Our system should mirror this: the per-region penalty must **escalate** with each additional region demanded, not stay flat at -5. Taking 1 region is routine. Taking 3 is a major war demand. Taking 6+ is near-impossible in a single diplomatic action regardless of how big the target is.

  In `calculate_acceptance()` (`diplomacy.py`), replace the flat -5/region with escalating cost, plus elimination guards:

  ```python
  # Replace flat DEMAND_VALUES territory scoring (~line 737-746) with escalating cost:
  target_regions = world.get_nation_regions(target_nation)
  demanded_regions = []
  territory_demand_count_fallback = 0  # backward compat for demands without "regions" list
  for d in proposal.get("demands", []):
      if d.get("type") in ("territory", "territory_cede"):
          regions_list = d.get("regions", [])
          if regions_list:
              demanded_regions.extend(regions_list)
          else:
              # Old saves / AI proposals may use {"type": "territory_cede", "value": 2}
              # without a regions list. Count via value field as fallback.
              territory_demand_count_fallback += int(d.get("value", 0) or 0)
  valid_demanded = [r for r in demanded_regions if r in target_regions]
  demanded_count = len(valid_demanded) + territory_demand_count_fallback
  total_regions = len(target_regions)
  remaining = total_regions - demanded_count

  # ── Income-weighted escalating per-region cost (replaces flat -5) ──
  # Formula: income_weight = max(0.5, region.income / 100).
  # Escalating base: -5 for 1st region, -8 for 2nd, -11 for 3rd, etc. (+3 per region).
  # Region cost = escalating_base × income_weight. Capital bonus: ×2 on top.
  # IMPORTANT: sort demanded regions by income ASCENDING before calculating.
  # This makes the cost deterministic (cheapest regions get lowest escalation,
  # expensive regions get highest — maximally restrictive ordering).
  territory_penalty = 0

  # Sort valid demanded regions by income ascending (cheapest first = hardest total)
  def _region_sort_key(r):
      reg = world.regions.get(r)
      return getattr(reg, 'income', 100) if reg else 100
  sorted_demanded = sorted(valid_demanded, key=_region_sort_key)

  region_index = 0
  for r in sorted_demanded:
      region = world.regions.get(r)
      income = getattr(region, 'income', 100) if region else 100
      income_weight = max(0.5, income / 100)    # 0.5 to 3.0
      escalation = -5 - (3 * region_index)      # -5, -8, -11, -14, ...
      base_cost = escalation * income_weight
      if r == NATION_CAPITALS.get(target_nation):
          base_cost *= 2                         # capitals always double
      territory_penalty += base_cost
      region_index += 1

  # Backward compat fallback: demands with value-only (no regions list)
  # use flat -5 per region (no income weighting possible without region identity)
  for _ in range(territory_demand_count_fallback):
      escalation = -5 - (3 * region_index)
      territory_penalty += escalation            # weight 1.0 assumed
      region_index += 1

  # ── Elimination guard (stacks with escalating cost) ──
  if remaining == 0:
      territory_penalty -= 60    # full annexation — blocked for all practical purposes
  elif remaining == 1:
      territory_penalty -= 30    # rump state — extremely hard

  demand_total += territory_penalty
  # NOTE: territory_penalty REPLACES the flat DEMAND_VALUES territory scoring.
  # Remove "territory"/"territory_cede" from the DEMAND_VALUES loop above,
  # handle them here instead.
  ```

  **IMPORTANT — applies to ALL proposal types:** This escalating cost runs inside `calculate_acceptance()`, which is called for regular peace proposals, AI proposals, armistice terms, and ultimatums. This is intentional — diplomatic elimination guards should protect against all diplomatic paths, not just ultimatums. Impact on regular proposals: 1 region costs the same (-5 for a town), 2+ regions escalate slightly faster than the old flat rate. AI self-corrects via `_reduce_p8_demands()`.

  **Region ordering is deterministic:** Regions are sorted by income ascending before calculating. Cheapest regions get the lowest escalation multiplier, expensive regions get the highest. This produces the maximally restrictive (hardest for the demander) total cost, and prevents players from gaming the system by reordering demands.

  **Income weight formula (map-agnostic — scales automatically with new regions):**

  ```
  income_weight = max(0.5, region.income / 100)
  if region is target's capital (NATION_CAPITALS): weight *= 2
  ```

  | income | weight | capital effective weight | Typical region_type |
  |--------|--------|-------------------------|---------------------|
  | 50 | 0.5 | 1.0 | rural |
  | 100 | 1.0 | 2.0 | town |
  | 150 | 1.5 | 3.0 | city |
  | 200 | 2.0 | 4.0 | major_city |
  | 300 | 3.0 | 6.0 | capital |

  No hardcoded region names — the formula reads `region.income` from REGIONS_DATA. New regions added during map expansion automatically get correct weights. The `max(0.5, ...)` floor handles modded regions with income=0.

  **NOTE:** Capital bonus is determined by `NATION_CAPITALS` dict (the nation's political capital), NOT by `region_type == "capital"`. A region can have `region_type: "capital"` (high-value urban terrain) without being a nation's political capital, and vice versa (e.g., a proxy capital with low income). The 2× multiplier only applies when demanding the target nation's actual capital.

  **Escalating cost examples (regions sorted by income ascending — deterministic):**

  | Demand | Escalation | Income weight | Capital? | Region cost | Cumulative |
  |--------|-----------|--------------|----------|-------------|-----------|
  | 1st: rural (income 50) | -5 | ×0.5 | no | **-2.5** | **-3** |
  | 1st: town (income 100) | -5 | ×1.0 | no | **-5** | **-5** |
  | 1st: city (income 150) | -5 | ×1.5 | no | **-7.5** | **-8** |
  | 1st: major_city (income 200) | -5 | ×2.0 | no | **-10** | **-10** |
  | 1st: capital (income 300) | -5 | ×3.0 ×2 | yes | **-30** | **-30** |
  | 2nd: town after rural | -8 | ×1.0 | no | **-8** | **-11** |
  | 2nd: capital (300) after town | -8 | ×3.0 ×2 | yes | **-48** | **-53** |

  **Realistic scenario math (max acceptance bonus ~105, regions auto-sorted by income ascending):**

  | Scenario | Regions (income, sorted asc) | Cost | Guard | Total | Net | Result |
  |----------|------------------------------|------|-------|-------|-----|--------|
  | 1 rural | (50) | -3 | 0 | -3 | 102 | ACCEPT (easy) |
  | 1 town | (100) | -5 | 0 | -5 | 100 | ACCEPT |
  | 1 city | (150) | -8 | 0 | -8 | 97 | ACCEPT |
  | 1 capital | (300, cap) | -30 | 0 | -30 | 75 | ACCEPT (hard) |
  | 2 towns | (100, 100) | -5, -8 = -13 | 0 | -13 | 92 | ACCEPT |
  | 3 mixed | (100, 100, 150) | -5, -8, -17 = -30 | 0 | -30 | 75 | ACCEPT (hard) |
  | 4 mixed | (100, 100, 100, 150) | -5, -8, -11, -21 = -45 | 0 | -45 | 60 | ACCEPT (very hard) |
  | 5 mixed | (100×4, 150) | -5, -8, -11, -14, -25.5 = -64 | 0 | -64 | 41 | REJECT |
  | capital + 2 towns | (100, 100, 300cap) | -5, -8, -66 = -79 | 0 | -79 | 26 | REJECT |
  | 1 of 2 (city non-cap) | (150) | -8 | -30 (rump) | -38 | 67 | ACCEPT (hard) |
  | 2 of 2 (city + cap) | (150, 100cap) | -8, -16 = -24 | -60 (annex) | -84 | 21 | REJECT |
  | 3 of 4 (cheapest 3) | (100, 100, 150) | -5, -8, -17 = -30 | -30 (rump) | -60 | 45 | REJECT |
  | Low-income capital alone | (50, cap) | -5 | 0 | -5 | 100 | ACCEPT |

  **NOTE on "capital + 2 towns" row:** With deterministic ascending sort, the capital (income 300) lands at the HIGHEST index (index 2), getting escalation -11 × 3.0 × 2 = -66. This is significantly more expensive than if the capital were first (-30). The ascending sort is intentionally restrictive — it prevents players from gaming demand order.

  **Key design outcomes (scale-independent — holds for any map size):**
  - **Cheap frontier provinces (rural, income 50):** Easy to demand at -3 each. Backwater provinces are cheap, matching EU4.
  - **Cities (income 150-200):** Significantly more costly — a major city alone is -10. Demanding 2-3 cities gets expensive fast with escalation.
  - **Capitals (income 300, ×2 bonus):** -30 EACH as first demand. With ascending sort, a capital demanded alongside other regions lands at the highest index, making it even more expensive. Demanding a capital + anything else is extremely hard.
  - **Large nations (10+ regions, mixed income):** Can take 3-4 cheap frontier regions with military dominance. Taking rich cities or the capital is much harder. Taking 5+ is blocked. Multiple wars needed to carve up a large empire — scales correctly as map expands.
  - **Medium nations (3-4 regions, valuable):** 2 towns = -13 (achievable). 3 regions = rump guard kicks in (-30 extra). Full annexation impossible via diplomacy.
  - **Small nations (2 regions):** Taking 1 non-capital = -8 + rump(-30) = -38 (hard but possible). Full annex: -24 + annex(-60) = -84, blocked.
  - **Income-weighted means:** A single capital (-30) costs more than 3-4 rural frontier provinces. Rich, developed regions are worth fighting harder to keep.

  The `remaining` and `demanded_count` variables are also used by §C, §D, and §E for relation/threat/warning scaling.

  **(B) Ultimatum generation guard — never auto-generate elimination demands:**
  In `generate_ultimatum_terms()` (`diplomatic_templates.py:1348-1363`), after selecting adjacent targets, filter out regions that would leave the target with ≤1 region:

  ```python
  # After building adjacent_targets list (~line 1362):
  target_regions = [r for r, reg in world.regions.items() if reg.controller == target_nation]
  # Don't auto-suggest demands that would eliminate or reduce to capital
  safe_targets = [r for r in adjacent_targets
                  if len(target_regions) - 1 > 1]  # must leave >1 region
  if safe_targets:
      demands.append({"type": "territory_cede", "value": 1, "regions": safe_targets[:1]})
  ```

  The wizard (PL-15) can still let the player manually demand elimination-level territory — but the auto-suggestion won't propose it, and the acceptance penalty (§A) makes it very unlikely to succeed.

  **(C) PL-19 relation penalty amplifier — territory component only (see AM-20.4):**
  In PL-19's dynamic penalty calculation, multiply only the **territory** portion of demand_penalty by an amplifier based on region count and elimination status (uses `demanded_count` and `remaining` from §A). Gold/manpower penalties are NOT amplified — those systems are independent of territorial aggression.

  ```python
  # PL-19 §A tracks two accumulators:
  territory_demand_penalty = 0   # from territory loop
  other_demand_penalty = 0       # from DEMAND_VALUES loop (gold, manpower, etc.)

  # Amplifier — territory only:
  if remaining == 0:
      territory_demand_penalty *= 2.5   # full annexation
  elif remaining == 1:
      territory_demand_penalty *= 2.0   # rump state
  elif demanded_count >= 4:
      territory_demand_penalty *= 1.5   # 4+ regions
  elif demanded_count >= 2:
      territory_demand_penalty *= 1.2   # 2-3 regions

  demand_penalty = territory_demand_penalty + other_demand_penalty
  total_penalty = max(-60, math.floor(base_penalty + demand_penalty))
  # NOTE: raise cap from -50 to -60 to accommodate amplified territory demands
  ```

  Examples with PL-19 base scaling (territory amplified, gold/manpower unchanged):
  - 2 of 2 from Saxony (full annex): base -10 + territory(-10 × 2.5 = -25) = **-35**
  - 2 of 2 from Saxony (full annex) + 100 gold: base -10 + territory -25 + gold -5 = **-40**
  - 1 of 2 from Saxony (rump): base -10 + territory(-5 × 2.0 = -10) = **-20**
  - 3 of 4 from Austria (rump): base -10 + territory(-15 × 2.0 = -30) = **-40**
  - 4 of 15 from Russia: base -10 + territory(-20 × 1.5 = -30) = **-40**
  - 2 of 15 from Russia: base -10 + territory(-10 × 1.2 = -12) = **-22**
  - 2 of 15 from Russia + 100 gold: base -10 + territory -12 + gold -5 = **-27**

  **(D) Threat amplifier — scales with region count + elimination risk:**
  Add bonus threat based on absolute region count and elimination status (on top of existing +8/region):

  ```python
  # In _execute_diplomatic_ultimatum(), after apply:
  if remaining == 0:
      add_threat(world, 25, "ultimatum_annex_attempt")
  elif remaining == 1:
      add_threat(world, 18, "ultimatum_rump_state")
  elif demanded_count >= 4:
      add_threat(world, 12, "ultimatum_major_territorial")
  elif demanded_count >= 2:
      add_threat(world, 5, "ultimatum_significant_territorial")
  ```

  Example threat totals (delivery + per-region + count bonus):
  - 1 region from Russia: 15 + 8 + 0 = **+23 threat**
  - 3 regions from Russia: 15 + 24 + 5 = **+44 threat** (coalition tension)
  - 5 regions from Russia: 15 + 40 + 12 = **+67 threat** (coalition brewing)
  - Full annex of Saxony (2 of 2): 15 + 16 + 25 = **+56 threat**
  - 4 regions from anyone: 15 + 32 + 12 = **+59 threat** (near brewing)

  **(E) Wizard warning — Talleyrand warns based on count + elimination risk:**
  In the PL-15 wizard confirm step, show count-appropriate warnings:

  For full annexation (remaining == 0):
  ```
  "Sire, demanding all of their territory would erase them from the map entirely.
  Every nation in Europe will view this as an existential threat. The acceptance
  chance is near zero, and the diplomatic cost would be catastrophic."
  ```

  For rump state (remaining == 1):
  ```
  "Reducing them to their capital alone would make them desperate — and their allies furious.
  Expect heavy diplomatic consequences and a near-certain rejection."
  ```

  For 4+ regions:
  ```
  "Demanding four or more regions is an extraordinary claim, Sire. Even after a decisive
  victory, such vast territorial concessions are rarely accepted. All of Europe will take notice."
  ```

  For 2-3 regions:
  ```
  "A substantial territorial demand. The diplomatic cost will be significant."
  ```

  **(F) Treaty cession guard — same logic for peace deals:**
  In `world_state.py` treaty ratification (~line 4784), apply the same remaining-region check before executing cessions. If a treaty would eliminate a nation, require war_score > 90 (near-total military victory). This prevents weird edge cases where a minor war score leads to full annexation.

- **Design rationale (EU4 parallel):**
  In EU4, province war score cost depends on both province count AND province development (base tax, production, manpower). Rich capitals cost 20-30+ war score; backwater provinces cost 3-5. You can't take half of Russia in one peace deal. Our system mirrors this with two mechanisms:

  1. **Income-weighted cost.** Each region's acceptance penalty scales with its income (the data already exists on every region). Rural frontier (50 income, weight 0.5) costs half as much as a town (100 income, weight 1.0). Capitals (300 income, weight 3.0 × 2 capital bonus = 6.0 effective) cost 6-12x more than a rural province. Demanding Paris alone (-30) is as expensive as demanding 3-4 frontier towns.

  2. **Escalating per-region cost.** Each additional region costs +3 more than the last (base: -5, -8, -11, -14...), multiplied by income weight. This means you can take 1-2 cheap provinces easily, 2-3 mixed-value provinces with military dominance, but 4+ is very hard and 5+ is blocked. Napoleon's post-Austerlitz Treaty of Pressburg took 3 regions from Austria — that's the right feel.

  Together: a player with total military dominance (~105 max bonus) could take a capital alone (-30), or 3-4 frontier towns, or 2 towns + 1 city. But NOT a capital + 3 towns. Multiple wars required for large conquests, exactly like EU4. The formula reads `region.income` dynamically — new regions added during map expansion automatically get correct weights without code changes.

  Combat elimination is deliberately unguarded — if you conquer their last territory in battle, that's a legitimate military outcome. The guards are only for diplomatic paths (ultimatums + treaties).

- **Files:** `backend/game_logic/diplomacy.py` (calculate_acceptance — §A), `backend/game_logic/diplomatic_templates.py` (generate_ultimatum_terms — §B), `backend/commands/diplomatic_executor.py` (relation/threat amplifier — §C/D), `backend/game_logic/diplomatic_dialogue.py` (wizard warning — §E), `backend/models/world_state.py` (treaty guard — §F)
- **Est. Tests:** 21 — (1) rural region (income 50): cost = -3 (weight 0.5 × -5), (2) town region (income 100): cost = -5 (weight 1.0 × -5), (3) city region (income 150): cost = -8 (weight 1.5 × -5), (4) capital region (income 300): cost = -30 (weight 3.0 × 2 capital × -5), (5) 2nd region escalates (+3 base), (6) 3 mixed-income regions: cumulative matches expected, (7) full annexation gets -60 elimination guard on top, (8) rump state (remaining=1) gets -30 guard, (9) auto-generation skips elimination/rump demands, (10) PL-19 relation penalty ×2.5 for annex, ×2.0 for rump, ×1.5 for 4+, (11) threat amplifier fires at count tiers, (12) treaty cession blocked below war_score 90 if would eliminate, (13) wizard shows appropriate Talleyrand warning, (14) large nation (15 regions): max ~3-4 regions with military dominance, (15) capital alone (-30) costs more than 3 rural provinces (-11), (16) income_weight defaults to 1.0 if region has no income field, (17) region sort order is deterministic (ascending income) — same regions in any demand order produce same cost, (18) backward compat: territory demand with value-only (no regions list) uses flat -5/region fallback, (19) modify_harsh_ultimatum respects elimination guard (doesn't add territory that would leave ≤1 region), (20) AI proposal with 2+ territory demands self-corrects via _reduce_p8_demands under escalating costs, (21) low-income capital (income 50, proxy) gets correct weight (0.5 × 2 = 1.0 effective)
- **Depends on:** PL-19 (relation penalty scaling — §C multiplier applies to PL-19's demand_penalty)
- **Implement with:** Session B (alongside PL-19). The acceptance penalty (§A) and auto-gen guard (§B) can land independently; the relation/threat amplifiers (§C/D) require PL-19's dynamic penalty to exist first.

#### Audit Amendments (Apr 8, adversarial audit)

**AM-20.1 (FAIL-5): `calculate_treaty_harshness()` uses flat 0.2/region — not income-weighted.**
PL-20 fixes `calculate_acceptance()` with income-weighted escalating territory costs, but `calculate_treaty_harshness()` (diplomatic_templates.py:1808-1823) still uses flat `0.2 * len(regions)`. Harshness feeds into acceptance via `harshness_penalty`, so undervaluing expensive regions in harshness weakens the acceptance penalty.
- **Fix:** Add §G to PL-20: update `calculate_treaty_harshness()` territory scoring to use income-weighted cost. Replace `harshness += 0.2 * count` with `harshness += sum(0.2 * max(0.5, getattr(world.regions.get(r), 'income_value', 100) / 100) for r in regions)`. Requires passing `world` to the function (currently takes only `treaty` dict). Alternative: use a flat 0.3 per region (higher than 0.2 but still flat) as a simpler fix that increases harshness without needing region data.
- **Recommendation:** Simpler flat increase (0.3/region) for now. Income-weighted harshness can be a future refinement. The escalating acceptance cost in §A is the primary guard.

**AM-20.2 (FAIL-6): No application-side guard against nation elimination via ultimatum.**
`_apply_ultimatum_demands()` (diplomatic_executor.py:699-711) blindly transfers all demanded regions. PL-20 §A guards at acceptance level (escalating costs + elimination penalty), but there's no safety net if acceptance is circumvented (debug, rounding edge case, future AI ultimatums).
- **Fix:** Add hard guard in `_apply_ultimatum_demands()`: before transferring territory, check `len(world.get_nation_regions(target_nation)) - len(demanded_regions) >= 1`. If transfer would eliminate the nation, skip territory demands and log a warning. This is a safety net, not the primary mechanism (§A is).
- **Test:** Set up world where target has 1 region. Inject territory demand for that region. Assert `_apply_ultimatum_demands` refuses the transfer.

**AM-20.3 (FAIL-9): §B `safe_targets` filter is a constant — doesn't depend on `r`.**
`safe_targets = [r for r in adjacent_targets if len(target_regions) - 1 > 1]` — the condition is invariant across the loop. Works by accident for single demands (`[:1]` limit is the real protection) but logically wrong.
- **Fix:** Replace with: `safe_targets = [r for r in adjacent_targets if len(target_regions) - len([d for d in demands if d.get("type") in ("territory", "territory_cede")]) - 1 > 1]`. Or simpler (since auto-gen only ever adds 1 territory demand): `if len(target_regions) > 2: safe_targets = adjacent_targets else: safe_targets = []`. The `[:1]` slice at line 1194 still limits to 1 region regardless. Document the invariant: "auto-generation demands at most 1 region."

**AM-20.4 (FAIL-10): §C amplifier multiplies ALL demand components, not just territory.**
`demand_penalty *= 2.5` multiplies gold and manpower penalties too, not just territory. A "take 1 territory + 100 gold/turn" demand against a 2-region nation gets the gold penalty (-5) multiplied by 2.5 as well (-12.5). Gold/manpower demands should cost the same regardless of what territorial demands accompany them — the systems should be independent.
- **Fix (APPROVED):** Split `demand_penalty` into `territory_demand_penalty` and `other_demand_penalty` in PL-19 §A. Apply the §C amplifier only to `territory_demand_penalty`. Then combine: `total_demand_penalty = (territory_demand_penalty * amplifier) + other_demand_penalty`. Full annexation is already prohibitively expensive via PL-20 §A escalating costs + elimination guard (-60). The amplifier doesn't need to infect non-territory demands.
- **Implementation in PL-19 §A:** Track two accumulators in the demand loop:
  ```python
  territory_demand_penalty = 0
  other_demand_penalty = 0
  for d in demands:
      dtype = d.get("type", "")
      if dtype in ("territory_cede", "territory"):
          # income-weighted region cost → territory_demand_penalty
      else:
          rate = DEMAND_VALUES.get(dtype, 0)
          other_demand_penalty += rate * abs(value)

  # PL-20 §C amplifier — territory only
  if remaining == 0:
      territory_demand_penalty *= 2.5
  elif remaining == 1:
      territory_demand_penalty *= 2.0
  elif demanded_count >= 4:
      territory_demand_penalty *= 1.5
  elif demanded_count >= 2:
      territory_demand_penalty *= 1.2

  demand_penalty = territory_demand_penalty + other_demand_penalty
  total_penalty = max(-60, math.floor(base_penalty + demand_penalty))
  ```
- **Test:** Annex Saxony (2 of 2) + 100 gold/turn. Assert gold component is -5 (not -12.5). Assert territory component is amplified by 2.5x. Assert total = base(-10) + territory(-25) + gold(-5) = -40.

**AM-20.5: `income` → `income_value` throughout §A.**
§A uses `getattr(region, 'income', 100)` and `getattr(reg, 'income', 100)`. Region class uses `income_value`. **PL-22 fixes the pre-existing code bug. Spec must match.**
- **Fix:** Change all `getattr(region, 'income', 100)` and `getattr(reg, 'income', 100)` to `getattr(region, 'income_value', 100)` / `getattr(reg, 'income_value', 100)` in §A. Also update the design rationale text: "The formula reads `region.income_value` dynamically" (not `region.income`).

**AM-20.6 (W-9): Empty regions list `[]` is falsy — fallback fires incorrectly.**
In §A: `if regions_list:` — empty list `[]` is falsy in Python, so `{"type": "territory_cede", "regions": [], "value": 2}` falls through to the fallback path, adding 2 to `territory_demand_count_fallback` despite having an explicit (empty) regions list.
- **Fix:** Change `if regions_list:` to `if regions_list is not None:`. An explicit empty list means "no regions specified" and should contribute 0, not fall to fallback.

**AM-20.7 (W-19): Duplicate regions in demands list double-counted.**
`valid_demanded` has no deduplication. If same region appears twice, it gets counted twice in escalating cost.
- **Fix:** Deduplicate: `valid_demanded = list(dict.fromkeys(r for r in demanded_regions if r in target_regions))`. Preserves order, removes duplicates.

**AM-20.8 (W-18): §F treaty cession guard has no implementation pseudocode or failure UX.**
§F says "require war_score > 90" but doesn't specify: where exactly in `_ratify_treaty()`, what to do when blocked (reject whole treaty? remove territory clauses only?), or how to notify the player.
- **Fix:** Add pseudocode to §F:
  ```python
  # In _ratify_treaty(), before territory cession loop:
  if territory_clauses and would_eliminate(target):
      war_score = get_war_score_for(proposer, target, world)
      if war_score < 90:
          # Remove territory clauses that would cause elimination
          # Keep non-territory clauses (gold, AP, etc.)
          territory_clauses = [c for c in territory_clauses
                               if not _would_leave_zero_regions(c, target, world)]
  ```
  Failure mode: silently remove the offending territory clause(s), keep the rest of the treaty. Log a campaign event: "Treaty terms regarding {region} could not be enforced — {target} retains their last territories."
- **Test:** Create treaty with territory clause that would eliminate target. Set war_score to 50. Assert territory clause is stripped but other clauses (gold) are applied.

**AM-20.9: Update cumulative cost examples to use `math.floor()` rounding.**
Per AM-19.1, the rounding strategy changes from `int()` (truncate toward zero) to `math.floor()` (floor toward negative infinity). Update the cumulative column in the examples table to reflect this. E.g., rural (income 50): region cost = -2.5, cumulative = `math.floor(-2.5)` = **-3** (matches spec). City (income 150): -7.5, cumulative = **-8** (matches spec). The examples were already correct assuming floor rounding.

---

### PL-21: Phantom `connections` attribute — adjacency checks dead ✓ FIXED (code)
- **Source:** Adversarial audit (Apr 8, 2026)
- **Priority:** P1 — MAJOR (three files affected, territory demands completely non-functional)
- **Status:** **FIXED in code** — attribute renamed in 3 locations. Test suite passes (7982 tests).

#### Problem
Region class (`backend/models/region.py:128`) stores adjacency as `self.adjacent_regions`. Three files use `getattr(region, 'connections', [])` which silently returns `[]` because `connections` does not exist on Region:

1. `backend/game_logic/diplomacy.py:853` — `calculate_acceptance()` ultimatum adjacency bonus (+15) NEVER fires
2. `backend/game_logic/diplomatic_templates.py:1359` — `generate_ultimatum_terms()` NEVER finds adjacent targets, so territory demands are NEVER auto-generated
3. `backend/commands/diplomatic_executor.py:1290` — `modify_harsh_ultimatum` Round 1 NEVER adds territory via adjacency check

#### Impact
All territory-related ultimatum features were dead code. The adjacency bonus (+15 acceptance) never applied. Auto-generated ultimatums were gold/manpower-only. Escalation Round 1 never added territory.

#### Fix Applied
Changed `getattr(region, 'connections', [])` → `getattr(region, 'adjacent_regions', [])` in all 3 locations. Existing test `test_zero_income_fallback_to_gold_lump` updated (was inadvertently testing broken behavior).

#### Tests
- Existing: `test_bugfix_session12.py` — all pass after fix
- Additional tests needed at implementation time: (1) `generate_ultimatum_terms` with military superiority produces territory demand, (2) `calculate_acceptance` adjacency bonus fires when proposer marshal is adjacent to target marshal, (3) `modify_harsh_ultimatum` Round 1 adds territory for adjacent regions

---

### PL-22: Phantom `income` attribute — income-weighted costs dead ✓ FIXED (code)
- **Source:** Adversarial audit (Apr 8, 2026)
- **Priority:** P1 — MAJOR (4 locations affected, income-weighted formulas produce default values)
- **Status:** **FIXED in code** — 1 location fixed (diplomatic_templates.py:1327). 3 spec locations amended (PL-19 §A, PL-20 §A — spec text, not code yet).

#### Problem
Region class (`backend/models/region.py:129`) stores income as `self.income_value`. Code and specs use `getattr(region, 'income', X)` which silently returns the default because `income` does not exist on Region:

1. **Code (FIXED):** `backend/game_logic/diplomatic_templates.py:1327` — `generate_ultimatum_terms()` `target_income` always 0, so `gold_per_turn` demands never generate (always falls to `gold_lump` fallback). Fixed: `income` → `income_value`.
2. **Spec:** PL-19 §A (BUG_FIXES.md line 958) — `getattr(region, 'income', 100)` in territory penalty formula. All regions would get default weight 1.0 (Paris = village). **See AM-19.5.**
3. **Spec:** PL-20 §A (BUG_FIXES.md lines 1084, 1090) — same issue in escalating cost formula. **See AM-20.5.**
4. **Spec:** PL-20 design rationale (line 1367) — text says "reads `region.income`" should say `region.income_value`. **See AM-20.5.**

#### Impact
- **Code fix:** `generate_ultimatum_terms()` now correctly calculates target income. Gold_per_turn demands will generate for nations with income > 0 (previously always fell to gold_lump).
- **Spec:** PL-19/PL-20 income-weighted territory formulas would have used flat weight 1.0 for all regions if implemented from spec text verbatim. Amendments AM-19.5 and AM-20.5 correct this.

#### Fix Applied
- `diplomatic_templates.py:1327`: `getattr(region, 'income', 0)` → `getattr(region, 'income_value', 0)`
- Test `test_bugfix_session12.py:366`: `region.income = 0` → `region.income_value = 0`
- Spec amendments added to PL-19 (AM-19.5) and PL-20 (AM-20.5)

---

### PL-23: Pre-proposal objection doesn't re-evaluate after term modification — OPEN

**Source:** Wizard flow audit (Apr 8, 2026)
**Priority:** P2 — GAMEPLAY
**Status:** OPEN — design approved, ready for implementation

#### Summary
Talleyrand's pre-proposal objection evaluates harshness at **dialogue creation time** (when the player first opens a proposal), not when the player actually sends it. The player can click "Harsher terms" / "More generous" multiple times to radically change demands, but the objection check never re-fires. This means:

1. **Vanilla proposals almost never trigger objection** — vassalage starts at 0.3 harshness, threshold for STRONG is 0.7. Only war declarations reliably trigger STRONG.
2. **Modified terms bypass objection entirely** — player can stack heavy gold + territory + manpower demands via the wizard, pushing harshness well above 0.7, and the "Send" button (`execute_proposal`) sends without any re-check.
3. **Mild concern is invisible** — MILD triggers (generous terms while winning) fire at creation but the player never sees them if they modify terms afterward.

#### Root Cause
`_merge_pre_proposal_objection` (diplomatic_dialogue.py:708-854) calls `evaluate_pre_proposal_objection` with a **lightweight proposal stub** built from the parsed command — empty demands and sweeteners. The harshness score is calculated once and baked into the dialogue. When the player modifies terms via `modify_harsh`/`modify_generous`/ultimatum wizard steps, no code path re-evaluates the objection.

The `execute_proposal` handler (diplomatic_executor.py:968-1017) sends the proposal directly without checking `evaluate_pre_proposal_objection` against the final terms.

#### Key Files to Research

| File | Lines | What to Look At |
|------|-------|-----------------|
| `backend/game_logic/diplomatic_dialogue.py` | 708-854 | `_merge_pre_proposal_objection` — where objection fires at creation time |
| `backend/commands/diplomatic_defiance.py` | 622-673 | `evaluate_pre_proposal_objection` — harshness thresholds (STRONG >0.7 + trust <40, MODERATE >0.7 + trust ≥40, MILD = generous while winning) |
| `backend/commands/diplomatic_defiance.py` | 132-162 | `calculate_proposal_harshness` — scoring formula (0.0-1.0 scale, vassalage +0.3 baseline) |
| `backend/commands/diplomatic_executor.py` | 968-1017 | `execute_proposal` — where objection SHOULD re-fire before sending |
| `backend/commands/diplomatic_executor.py` | 1080-1085 | `modify_harsh` — builds new confirm dialogue without re-evaluating objection |
| `backend/commands/diplomatic_executor.py` | 1463-1471 | `modify_generous` — same issue as modify_harsh |

#### Approved Design v2 (Apr 9, 2026)

**Core insight:** Talleyrand is already drafting the terms — the player says "harsher" or "I want territory" and Talleyrand writes it up. Pushback isn't a separate gate or popup; it's Talleyrand responding *as part of the drafting conversation*. When Napoleon is strong, Talleyrand writes what he's told. When Napoleon is weakening, Talleyrand starts shaping the terms himself — just like the real Talleyrand, who conducted his own diplomacy when Napoleon's grip loosened post-1809.

**Pattern:** Mirrors V2b combat defiance (probability curve, authority-driven, variance band). NOT a deterministic threshold — Talleyrand's independence is probabilistic, unpredictable, and tied to Napoleon's power.

##### When to evaluate

At each term modification step: `modify_harsh`, `modify_generous`, and the ultimatum wizard confirm step (`_build_ultimatum_confirm_step`). These are the moments Talleyrand is actively drafting — he reacts to what the player is asking him to write. No re-evaluation at `execute_proposal` (by then the conversation is over, terms are finalized).

##### Probability curve

Recalculate harshness from the current terms via `calculate_proposal_harshness()`, then roll:

```
Base chance (from harshness):
  harshness ≤ 0.4  →  0%   (reasonable terms, Talleyrand has no issue)
  harshness 0.4-0.7 →  5%  (pushing it — he occasionally editorializes)
  harshness > 0.7  → 15%   (extreme — serious creative differences)

Authority modifier (sole driver — see §Talleyrand trust removal below):
  ≥ 80  → -10%  (Napoleon at height of power, Talleyrand obeys)
  < 50  → +10%  (weakening grip, Talleyrand freelances)
  else  →   0%

Variance: ±5% (prevents memorized thresholds)
Cap: 30% (matches diplomatic defiance cap)
Floor: 2% schemer floor (when harshness > 0.4)
Loyalist personality: always 0%
```

##### What happens when the roll fires

Talleyrand doesn't block the proposal or show a popup — he **drafts different terms than requested** and tells the player what he did. This is part of the wizard conversation, not a separate event. The player gave direction; Talleyrand interpreted it his way.

The confirm dialogue shows Talleyrand's modified terms with text like:
- *"I have drafted the terms, Sire — though I took the liberty of... adjusting certain impractical demands. The essence of your position is preserved."*
- *"You wished for territory? I have asked for trade access instead. They will actually agree to this."*

Options: **[Accept his version] / [Insist on original] / [Cancel]**

- **[Accept his version]** — sends Talleyrand's softened terms. Talleyrand applied a pen nudge: reduce the harshest numeric demand by 20%, or swap a territory demand for a gold sweetener. The player sees exactly what changed in the term summary.
- **[Insist on original]** — sends the player's exact terms. Authority -3 (you overruled your diplomat openly, same weight as insisting on a marshal objection). No further re-roll on this proposal — one conversation per proposal.
- **[Cancel]** — abort, return to term modification.

**Pen nudge rules** (deterministic, no randomness in the nudge itself):
1. Find the demand with the highest harshness contribution
2. If numeric (gold/units): reduce value by 20% (round to int)
3. If territory: remove the last-added region from the demand
4. If only AP demands remain: add one minor sweetener (100 gold/turn to target)
5. Recalculate and show the updated term summary so the player sees what changed

##### What happens when the roll doesn't fire

Normal confirm dialogue. Talleyrand drafts exactly what the player asked. If harshness > 0.7 he may add a flavor line (*"Bold terms, Sire. I shall present them as instructed."*) but no mechanical effect — he wrote what he was told.

##### Generous direction

When the player clicks "More generous" and harshness drops, the roll becomes less likely to fire (lower base chance). No special handling — the curve naturally produces fewer interventions on reasonable terms.

##### Interaction with existing defiance/sabotage (§3a)

**Mutually exclusive per proposal.** If PL-23's roll fired during drafting (regardless of whether the player accepted or insisted), skip the §3a defiance roll at `execute_proposal` send time. Rationale: Talleyrand already expressed his opinion in the conversation. Sabotage (§3a) is for when he acts *behind your back* — he doesn't do both. One interaction per proposal.

Implementation: set `context["objection_resolved"] = True` on the dialogue context when PL-23 fires. `execute_proposal` checks this flag and skips the defiance pipeline.

##### DP timing fix

DP is deducted only when the proposal actually departs — at the end of `execute_proposal` after all conversation is resolved, not before. If the player cancels at any point (including after PL-23 pushback), no DP is spent. Move the DP deduction block in `execute_proposal` to after the defiance check, just before setting Talleyrand in transit.

##### Talleyrand trust removal

**Decision:** Remove Talleyrand's personal trust stat entirely. Use authority as the sole driver for all Talleyrand behavior (PL-23 pushback, §3a defiance).

**Rationale:** Talleyrand's character is defined by serving power, not personal loyalty. When Napoleon was strong, Talleyrand obeyed. When Napoleon weakened, Talleyrand freelanced. That's authority, not trust. The trust stat only moved through the sabotage pipeline (confront -10 / overlook +3), giving the player no proactive way to build it — a dead stat measuring the same thing authority already measures.

**Migration:**

| Current (trust-based) | New (authority-only) |
|----------------------|---------------------|
| §3a defiance: base + authority_mod + trust_mod + variance | §3a defiance: base + authority_mod + variance |
| PL-23 pushback: authority primary, trust secondary | PL-23 pushback: authority only (curve above) |
| Confront sabotage: trust -10, authority +5 | Confront sabotage: authority +5 only |
| Overlook sabotage: trust +3 | Overlook sabotage: authority -3 (letting it slide shows weakness) |

**What gets removed:**
- `trust` field on `DiplomaticRepresentative` (diplomat.py)
- Trust modifier block in `calculate_diplomatic_defiance_chance()` (diplomatic_defiance.py:69-77)
- Trust modifier block in `calculate_diplomatic_defiance_chance_deterministic()` (diplomatic_defiance.py:115-123)
- Trust reads/writes in confrontation, overlook, and redemption handlers
- Any UI display of Talleyrand trust (diplomatic ledger Talleyrand tab)
- **Talleyrand redemption event entirely** (see below)

**What stays:** Authority is already well-sourced (battles ±5, marshal objection responses, defiance outcomes ±3/5, combat captures, balanced leadership +1/turn). The player has clear, varied ways to manage it through normal gameplay.

##### Talleyrand redemption — CUT

**Decision:** Remove the Talleyrand redemption event (`check_talleyrand_redemption`, `build_redemption_dialogue`, `apply_redemption_choice` in diplomatic_defiance.py:474-615).

**Rationale:** Marshal redemption fires at trust ≤ 20 — a personal relationship breakdown. Trust is the right trigger because the player has direct, varied ways to build or burn marshal trust (trust/insist on objections, battle outcomes, vindication). Authority is the wrong trigger for a redemption event because:
1. Authority ≤ 30 already fires the "Emperor in Name Only" threshold event (authority.py:48-53) — same threshold, same narrative beat, two popups on the same turn is redundant.
2. Redemption implies repairing a personal relationship. Talleyrand doesn't have a personal relationship with Napoleon — he serves power. When authority drops, Talleyrand freelances more (the defiance curve at authority < 40 gives +15% base). When authority recovers, he falls in line. The curve IS the redemption path — it's continuous, not event-driven.
3. The three options (Apologize/Replace/Continue) were designed around trust as a lever to pull. With authority-only, "apologize to your diplomat for being weak" doesn't fit Napoleon's character.
4. Replace-with-Loyalist is interesting but better suited as a design refinement item — a crisis event at sustained low authority, not a redemption screen.

**What gets removed:**
- `check_talleyrand_redemption()` (diplomatic_defiance.py:474-498)
- `build_redemption_dialogue()` (diplomatic_defiance.py:501-550)
- `apply_redemption_choice()` (diplomatic_defiance.py:553-615)
- `last_redemption_turn` field on WorldState
- Redemption popup in Godot (`talleyrand_redemption_popup.gd`)
- Redemption wiring in diplomatic_executor.py / main.gd

**Deferred to design refinement:** "Replace Talleyrand" as a crisis event (sustained authority < 30 for 5+ turns). Would be a separate R-item, not part of PL-23.

##### [Cancel] return target

When PL-23's roll fires and the player picks [Cancel], the dialogue must return to the **same confirm step with the same context** (including `modify_count`). Do NOT pop the dialogue back to wizard start — that would reset modify_count and let the player re-roll indefinitely. Implementation: [Cancel] replaces the pushback dialogue with the pre-pushback confirm dialogue (terms unchanged, modify_count preserved).

##### Stress-test findings (Apr 9, 2026)

| # | Finding | Severity | Resolution |
|---|---------|----------|------------|
| S1 | Authority spiral amplifies both Talleyrand + marshal insubordination below 50 | Low | Intentional dramatic tension. No proactive recovery path exists beyond balanced objection responses (+1/turn) — acceptable since authority is meant to be hard to recover |
| S2 | Overlook sabotage is strictly negative (authority -3, no upside) | Medium | By design — both choices cost something (same as marshal trust/insist). Confrontation narrative should hint whether Talleyrand's judgment was sound (R129 covers dispatch feedback next turn). No code change needed |
| S3 | Pen nudge on AP-only demand: AP survives unchanged + sweetener added = proposal more attractive | Low | Working as designed. Player sees the change and can [Insist on original]. Document in pen nudge rules |
| S4 | War declarations exempt from PL-23 (separate path at line 428-534) | None | Correct. War declarations have no modifiable terms. Existing threat-based STRONG check is sufficient |
| S5 | `gold_lump` demand type not scored in harshness formula | Medium | Fix in PL-24 alongside territory bug |
| S6 | `ap_per_turn` and `unit_trade` are flat-scored (don't scale with value) | Medium | Fix in PL-24 — scale with value like gold_per_turn |
| S7 | Talleyrand redemption collides with "Emperor in Name Only" at authority ≤ 30 | Resolved | Redemption event CUT entirely (see above) |

##### Files requiring changes

1. `diplomatic_defiance.py` — Replace `evaluate_pre_proposal_objection()` with `roll_drafting_pushback()` (authority-only probability curve). Add `apply_pen_nudge()` (deterministic term softening). Remove trust modifiers from `calculate_diplomatic_defiance_chance()`. Update confrontation/overlook to authority-only. Remove redemption functions entirely. Keep `calculate_proposal_harshness()` as-is (fix territory bug separately in PL-24).
2. `diplomatic_executor.py` — Call `roll_drafting_pushback()` in `modify_harsh`, `modify_generous`, and `_build_ultimatum_confirm_step`. On fire: build [Accept/Insist/Cancel] dialogue with nudged terms. On insist: authority -3, set `objection_resolved` flag. [Cancel]: replace with pre-pushback confirm (preserve modify_count). Move DP deduction in `execute_proposal` to after defiance check. Check `objection_resolved` to skip §3a defiance. Remove redemption wiring.
3. `diplomatic_dialogue.py` — Remove `_merge_pre_proposal_objection()` (creation-time evaluation no longer needed; evaluation happens during drafting steps).
4. `diplomat.py` — Remove `trust` field from `DiplomaticRepresentative`. Update `to_dict`/`from_dict`.
5. `diplomatic_ledger.py` — Remove trust display from Talleyrand tab, replace with authority reference.
6. `world_state.py` — Remove `last_redemption_turn` field.
7. `talleyrand_redemption_popup.gd` — Delete (no longer needed).
8. `main.gd` — Remove redemption popup registration and wiring.
9. Tests — Probability curve unit tests, pen nudge deterministic tests, mutual exclusion integration tests, DP-on-cancel tests, serialization update tests, redemption removal regression tests.

#### Reproduction
1. Start game, open F1 wizard, select nation, propose vassalization
2. On confirm dialogue, click "Harsher terms" 3+ times (add gold, territory, manpower)
3. Click "Send" — proposal sends without Talleyrand objecting despite extreme harshness
4. Compare: declare war via wizard — Talleyrand objects immediately (STRONG fires at creation because war declaration is special-cased)

### PL-24: Territory demands from modify_harsh score zero harshness — OPEN

**Priority:** P1 — MECHANICS  
**Source:** PL-23 design review (Apr 9, 2026)  
**Blocks:** PL-23 (re-evaluation depends on accurate harshness scoring)

#### Description

`calculate_proposal_harshness()` in `diplomatic_defiance.py:132-162` computes territory harshness as `+0.2 * len(demand.get("regions", []))`. But `modify_harsh` in `diplomatic_executor.py:1119` adds territory demands as `{"type": "territory_cede", "value": 2}` — no `regions` list, just a numeric `value`.

Result: territory demands added through the wizard contribute **zero** to the harshness score. A player can stack multiple territory cessions via "Harsher terms" and the proposal reads as mild.

This is pre-existing but becomes critical with PL-23, since re-evaluation depends on harshness accurately reflecting current terms.

#### Root Cause

Two code paths produce territory demands in different shapes:
- `generate_suggested_terms` → `{"type": "territory_cede", "regions": ["Bavaria", "Saxony"]}` (list of region names)
- `modify_harsh` → `{"type": "territory_cede", "value": 2}` (numeric count, no regions)

`calculate_proposal_harshness` only handles the first shape.

#### Fix — territory shape

`calculate_proposal_harshness` should handle both shapes:
```python
if dtype == "territory_cede":
    regions = demand.get("regions", [])
    if regions:
        harshness += 0.2 * len(regions)
    else:
        harshness += 0.2 * max(1, demand.get("value", 1))
```

#### Additional harshness gaps (found during PL-23 stress-test, Apr 9 2026)

These are pre-existing but become critical with PL-23's re-evaluation:

| Demand Type | Current Scoring | Problem | Fix |
|-------------|----------------|---------|-----|
| `territory_cede` (value shape) | +0.0 | `modify_harsh` uses `{"value": 2}` not `{"regions": [...]}` | Handle both shapes (above) |
| `gold_lump` | Not scored | Lump-sum gold demands contribute zero harshness | Add `+0.1 * (value / 500)` (lower weight than per-turn since one-time) |
| `ap_per_turn` | +0.3 flat | 1 AP/turn = 3 AP/turn = same harshness | Scale: `+0.3 * max(1, value)` |
| `unit_trade` | +0.15 flat | 500 units = 5000 units = same harshness | Scale: `+0.15 * (value / 1000)` with floor of 0.15 |

#### Files
- `backend/commands/diplomatic_defiance.py` — `calculate_proposal_harshness` (lines 132-162)

---

### PL-25: R155-lite — Diplomatic term novelty (companion to PL-23) — OPEN

**Priority:** P2 — GAMEPLAY
**Source:** PL-23 stress-test review (Apr 9, 2026)
**Companion to:** PL-23 (implement together or immediately after)

#### Problem

PL-23 makes Talleyrand an active character who pushes back and rewrites terms. But if his baseline suggestions are purely formulaic (same inputs = same terms every time), the pushback feels mechanical. The pen nudge is a flat 20% reduction on a deterministic base — doubly predictable.

Current `_build_base_terms()` in `diplomatic_templates.py` ignores: diplomat personality, nation desire profiles, recent events, and any randomization. All data sources exist (`NATION_DESIRE_PROFILES`, `TALLEYRAND_COMMENTARY`, diplomat personality field) but none feed into term generation.

#### Design — R155-lite scope

Three changes to `_build_base_terms()` / `generate_suggested_terms()`, all small-medium effort:

##### 1. Amount jitter (±20%)
Add `random.uniform(0.8, 1.2)` multiplier to gold/manpower demand values. Terms will vary between proposals even for identical game states. Deterministic mode uses fixed 1.0 for testing.

##### 2. Personality-biased pen nudge direction
When PL-23's pen nudge fires, Talleyrand's personality shapes HOW he softens:
- **Schemer:** Swaps demand types (territory → gold, AP → sweetener). "They'll agree to gold, Sire. Land they'll fight for."
- **Loyalist:** Straight 20% reduction on largest demand. "I have moderated the terms as a precaution, Sire."

This replaces the flat 20% rule for schemer personality only. Loyalist keeps the simple reduction (loyalist is the "boring but reliable" replacement diplomat).

##### 3. Nation desire profile bias
Read `NATION_DESIRE_PROFILES[target_nation]` in `_build_base_terms()`. If Saxony's profile says they want protection, Talleyrand biases sweetener selection toward protection offers. If Prussia's profile says they fear territorial loss, territory demands get higher harshness weight in Talleyrand's internal assessment (he's more likely to push back on them).

This makes Talleyrand's pushback *nation-aware* — he doesn't just react to harshness, he reacts to whether the terms are *smart* for the target.

##### 4. Situational flavor line
One context-aware Talleyrand comment per proposal based on recent events:
- Recent battle victory over target: "They are weakened, Sire. Now is the time to press."
- Target just lost an ally: "They stand alone. A generous offer now buys loyalty cheaply."
- High threat level: "The courts watch us, Sire. Moderation may serve us better than force."
- Default: standard commentary from `TALLEYRAND_COMMENTARY`

Read from `world.turn_events` or `world.diplomatic_history`. 4-6 condition checks, one line of flavor. No new systems.

#### Files
1. `diplomatic_templates.py` — `_build_base_terms()` (jitter, desire profile bias), `generate_suggested_terms()` (situational line)
2. `diplomatic_defiance.py` — `apply_pen_nudge()` (personality-biased direction, added in PL-23)
3. Tests — Jitter bounds tests, personality nudge direction tests, desire profile coverage tests
