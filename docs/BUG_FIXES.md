# Bug Fixes

> **Consolidated bug tracker.** All open bugs from playtest reviews, audits, and design fixes live here.
> Iterate sessions until clean, then move to `DESIGN_REFINEMENT.md`.
>
> **Last Updated:** April 7, 2026 (Session 12 follow-up — 2 new bugs from ultimatum playtest)

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
| **P1 — CRITICAL** | **1** | **PL-15 OPEN — ultimatum popup shows no demands + no demand customization** |
| **P2 — UX** | **1** | **PL-16 OPEN (absorbed into PL-15) — Harsher Demands too aggressive; replaced by wizard** |
| **Total** | **2 OPEN (1 fix — PL-16 absorbed into PL-15)** | |

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

- **Est. Tests:** ~12-15

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
    "gold_amount": default_gold,
    "manpower_amount": 0,
}
```

**Empty demands guard:** If `approved_demands` is empty at the confirm step (player skipped all steps AND gating excluded territory/manpower), inject the gold floor demand: `{"type": "gold_lump", "value": 100}`. Talleyrand message: "We must demand something, Sire — at minimum a symbolic tribute." This matches the `generate_ultimatum_terms()` fallback (line 1373).

**§3. Gold step** — `_build_ultimatum_gold_step()`

Modeled on `_build_gold_step()` (line 2238). Calculates suggested gold from target income (same as `generate_ultimatum_terms` gold logic).

**Gold source logic:** If `target_income > 0`, demand `gold_per_turn` (capped at 50% of income, range 50-300). If `target_income == 0` but `target_gold > 0`, demand `gold_lump` (30% of gold, range 50-500). If both are 0, offer floor of 50 `gold_lump` ("symbolic tribute").

```
"Talleyrand: How much gold should we demand per turn, Sire?"
[Demand {X} gold]  [Demand more]  [Demand less]  [Skip gold]
```

Actions: `ultimatum_gold_accept`, `ultimatum_gold_more` (1.5x), `ultimatum_gold_less` (0.7x), `ultimatum_gold_skip`.

Gold floor: 25. Gold cap: 300 for per-turn, 500 for lump (same as `generate_ultimatum_terms`). More/less multipliers match armistice wizard (1.5x/0.7x).

**§4. Territory step** — `_build_ultimatum_territory_step()`

Only offered if France has military superiority (>1.2x, same threshold as `generate_ultimatum_terms`). If not, skip to manpower.

Modeled on armistice territory picker (lines 1498-1568). Picks from target's non-capital regions adjacent to France-controlled territory.

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

Default: `int(troop_advantage * 0.1)`, capped at 5000.

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

"Deliver Ultimatum" action = `execute_ultimatum` with the wizard-built terms (same handler that exists today).
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
- **Nation eliminated mid-wizard:** Target eliminated before confirm → guard with error message, pop dialogue
- **Remove tests:** Delete/update `TestModifyHarshUltimatum` tests (handler removed)
- **curl test:** `curl -X POST http://127.0.0.1:8005/command -H "Content-Type: application/json" -d '{"command": "send ultimatum to Prussia"}' | python -m json.tool` — verify new dialogue structure
- **Godot visual:** Popup shows demands, splash damage, threat warning, acceptance estimate, harshness label

---

### PL-16: Harsher Demands Multiplier Too Aggressive — ABSORBED INTO PL-15
- **Source:** Playtest (Apr 7, Session 12 follow-up)
- **Priority:** P2 — UX (gameplay balance)
- **Status:** Absorbed into PL-15. The demand wizard eliminates `modify_harsh_ultimatum` entirely — the player picks their own demand amounts instead of blind escalation. No separate fix needed.
