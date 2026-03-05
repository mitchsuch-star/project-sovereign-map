# Diplomacy Refinement & Cleanup

> **Created:** March 4, 2026
> **Status:** IN PROGRESS — Design phase
> **Source:** `docs/DIPLOMACY_CREATIVE_AUDIT.md` (5-agent creative audit, 7.8/10 overall) + code audit (March 5, 2026)
> **Process:** Design gate approval -> Implementation (possibly multi-session)
> **Next phase:** "Finish Design on Diplo Refinement & Cleanup" -> then implementation sessions

---

## How This Works

1. Items marked **NEEDS DESIGN** require user approval before coding
2. Items marked **DONE** were fixed during the audit session
3. Items organized by type: Bugs -> Balance -> Missing Commands -> Features
4. Within each type, ordered by severity/priority
5. `[NEW]` = Found in March 5 code audit (not in original creative audit)

## Bug Cross-Reference (Audit -> Refinement)

| Audit Bug | Severity | Refinement Item | Status |
|-----------|----------|-----------------|--------|
| BUG-1: War score decay no-op | CRITICAL | R1a | NEEDS DESIGN |
| BUG-2: Battle records persist across wars | CRITICAL | R1b | NEEDS DESIGN |
| BUG-3: Counter-offer treated as rejection | CRITICAL | R2 | NEEDS DESIGN |
| BUG-4: Armistice expiration unimplemented | HIGH | R5a | NEEDS DESIGN |
| BUG-5: Armistice cooldowns never written | HIGH | R5b | NEEDS DESIGN |
| BUG-6: Treaty clause gold unenforced | HIGH | R3 | NEEDS DESIGN |
| BUG-7: Treaty clause gold no floor | MEDIUM | R3 (included) | NEEDS DESIGN |
| BUG-8: Defensive alliance base disposition | MEDIUM | R7 | NEEDS DESIGN |
| BUG-9: Talleyrand sabotage/redemption popups unresolvable | CRITICAL | R37 | NEEDS DESIGN |
| BUG-10: Talleyrand proposal terms show "war score 0" | MEDIUM | R38 | NEEDS DESIGN |
| BUG-11: DP not visibly displayed in game | INVESTIGATION | R39 | NEEDS DESIGN |
| [NEW] BUG-12: Coalition loyalty penalty inverted | CRITICAL | R40 | NEEDS DESIGN |
| [NEW] BUG-13: Sabotage/redemption actions unwired in executor | CRITICAL | R41 | NEEDS DESIGN |
| [NEW] BUG-14: Pre-proposal objection overrides unwired | CRITICAL | R42 | NEEDS DESIGN |
| [NEW] BUG-15: AI-AI proposal spam (no per-pair cooldown) | CRITICAL | R43 | NEEDS DESIGN |
| [NEW] BUG-16: AI nation DP never stored | HIGH | R44 | NEEDS DESIGN |
| [NEW] BUG-17: Downgrade doesn't clean active_treaties | HIGH | R45 | NEEDS DESIGN |
| [NEW] BUG-18: Vassal rebellion doesn't clean active_treaties | HIGH | R46 | NEEDS DESIGN |
| [NEW] BUG-19: Strategic orders not cancelled on peace | HIGH | R47 | NEEDS DESIGN |
| [NEW] BUG-20: Vassal relations with non-lord nations unhandled | HIGH | R48 | NEEDS DESIGN |
| [NEW] BUG-21: War exhaustion not reset on peace | MEDIUM | R49 | NEEDS DESIGN |
| [NEW] BUG-22: Continental System membership not cleaned on vassal release | MEDIUM | R50 | NEEDS DESIGN |
| [NEW] BUG-23: Pending dialogue not voided when coalition forms | MEDIUM | R51 | NEEDS DESIGN |
| [NEW] BUG-24: Duplicate Continental System implementations | MEDIUM | R52 | NEEDS DESIGN |
| [NEW] BUG-25: Sweetener values round to 0 for small amounts | MEDIUM | R53 | NEEDS DESIGN |
| [NEW] BUG-26: War score sign convention scattered across 5 files | MEDIUM | R54 | NEEDS DESIGN |
| [NEW] BUG-27: Dialogue guard keyword list incomplete | MEDIUM | R55 | NEEDS DESIGN |
| [NEW] BUG-28: modify_nation_relation has no self-guard | MEDIUM | R56 | NEEDS DESIGN |
| [NEW] BUG-29: Threat field in dialogue context always 0 | LOW | R57 | NEEDS DESIGN |
| [NEW] BUG-30: Vindication tracker decay never implemented | LOW | R58 | NEEDS DESIGN |
| [NEW] BUG-31: Literal personality triggers never fire | LOW | R59 | NEEDS DESIGN |
| [NEW] BUG-32: Double-vassalization edge case | LOW | R60 | NEEDS DESIGN |

---

## DONE (Fixed During Audit Session)

| # | Item | What Was Done |
|---|------|---------------|
| GAP-3 | **Player treaty cancellation command** | Wired `break_treaty()` to executor, parser, mock parser, validation. Keywords: "break treaty", "cancel treaty", "renounce treaty", "end treaty", "abrogate". 1 DP cost. |
| GAP-5 | **Player voluntary downgrade command** | Wired `execute_downgrade()` to executor, parser, mock parser, validation. Keywords: "downgrade", "reduce commitment", "step down", "withdraw from", "lower relations", "cool relations". 1 DP cost. |
| GAP-6 | **AI-AI diplomatic states in ledger** | Added `ai_relations` field to each nation in diplomatic ledger nations tab. Shows AI-AI states fog-filtered (PARTIAL+ intel on either nation). |

All 5290 tests pass after changes. 5 files modified, 106 lines added.

---

---

# PART A: BUGS (Broken Code)

Items that are demonstrably broken — code that crashes, produces wrong results, or is completely non-functional. Ordered by severity.

---

## CRITICAL BUGS

### R1a: War Score Decay No-Op — NEEDS DESIGN

**Problem:** `recalculate_war_scores()` overwrites decay every turn. Battle records from turn 5 still contribute +3 at turn 50.

**Proposed fix:** Prune battle records older than 10 turns in `apply_war_score_decay()`. Records older than 10 turns are removed from `world.battle_records[diplo_key]`. This makes the battle component time-sensitive — recent victories matter, old ones fade.

**Alternative:** Apply a decay multiplier — records from N turns ago contribute `3 * max(0, 1 - (age / 15))` instead of flat 3. Gradual fade vs hard cutoff.

**Example:**
```
Turn 5: Win battle vs Prussia (+3 battle score)
Turn 10: Still contributing +3 (5 turns old, under 10)
Turn 16: Pruned (11 turns old, over 10). Battle score drops.
Decisive battles: same 10-turn pruning (no special exemption)
```

### R1b: Battle Records Persist Across Wars — NEEDS DESIGN

**Problem:** Peace -> re-declare war -> start with old battle score banked.

**Proposed fix:** Clear `battle_records[diplo_key]` and `decisive_battles[diplo_key]` when transitioning OUT of WAR state (in `_ratify_treaty()` or `diplomacy.py` state transition code).

**Example:**
```
Turn 5: France wins 4 battles vs Prussia (+12 battle score)
Turn 8: Peace signed. battle_records["France|Prussia"] cleared.
Turn 12: War re-declared. War score starts at 0. Fresh war, fresh scorecard.
```

### R2: Player Counter-Offer Treated as Rejection — NEEDS DESIGN

**Problem:** Acceptance scores 30-49 are stubbed as REJECT. The most interesting diplomatic outcome (negotiation) is completely broken.

**Proposed fix (two-part):**

**Part A — Backend:** When `calculate_acceptance()` returns score 30-49, run the M3 counter-offer algorithm (`generate_counter_offer()` already exists in `ai_diplomacy.py`). Return the modified terms in the dialogue popup data so the player sees: "Original terms vs. Their counter-terms."

**Part B — Player choice:** The popup offers:
- **[Accept Counter]** — Ratify their version (0 DP, per spec S2d)
- **[Reject]** — Walk away (relation -5, cooldown starts)
- **[Renegotiate]** — Costs 1 DP, Talleyrand departs again with player's original terms adjusted

This matches the existing spec S2d exactly — the code just never implemented it.

**Stretch (GAP-1):** Let the player specify counter-offer terms manually instead of re-sending originals. Opens clause-selection in the renegotiate path. Much harder — requires a new command flow.

### R37: Sabotage Discovery & Redemption Popups Cannot Be Resolved — NEEDS DESIGN

**Problem:** When Talleyrand's sabotage is discovered (or redemption triggers), the popup NEVER appears. Instead, the content dumps into the chat log as plain text. The player cannot interact with it (no Confront/Overlook/Apologize/Replace/Continue buttons), making the sabotage/redemption system completely non-functional. Additionally, the executor has no handlers for these actions even if the popup were shown.

**Root cause (3 layers):**

1. **Popup never triggers in Godot**: The sabotage/redemption data reaches the API response but Godot renders it as chat text instead of triggering the dedicated popup scenes (`sabotage_discovery_popup.gd`, `talleyrand_redemption_popup.gd`). Either `main.gd` doesn't check for the popup fields in the response, or the check runs after the text is already rendered to chat.

2. **Missing action map entries** (`executor.py`, `_process_dialogue_choice()`): Even if the popup were shown, the `action_map` dict has NO entries for sabotage/redemption actions. Keywords "confront", "overlook", "apologize", "replace", "continue" are in `_DIALOGUE_RESPONSE_KEYWORDS` but the executor doesn't know what to do with `confront_sabotage`, `overlook_sabotage`, `redemption_apologize`, `redemption_replace`, or `redemption_continue` actions.

3. **Missing handler functions**: No `_handle_confront_sabotage()`, `_handle_overlook_sabotage()`, etc. exist in the executor. The logic EXISTS in `diplomatic_defiance.py` (`resolve_confrontation()` at line ~416, `apply_redemption_choice()` at line ~544) but is never wired. On failure, `pending_diplomatic_dialogue` is NOT cleared -> stuck state.

**Proposed fix:**

1. **Fix popup triggering in Godot**: Ensure `main.gd` checks for `diplomatic_sabotage` / `talleyrand_redemption` fields in the response and calls the popup BEFORE rendering chat text. Verify popup scene nodes are connected in the scene tree.

2. Add entries to `action_map` in `_process_dialogue_choice()`:
   ```python
   "confront": "confront_sabotage",
   "overlook": "overlook_sabotage",
   "apologize": "redemption_apologize",
   "replace": "redemption_replace",
   "continue": "redemption_continue",
   ```

3. Implement handler functions that call existing `diplomatic_defiance.py` logic:
   - `_handle_confront_sabotage()` -> calls `resolve_confrontation()`
   - `_handle_overlook_sabotage()` -> calls `resolve_confrontation()`
   - `_handle_redemption_*()` -> calls `apply_redemption_choice()`

4. Each handler must clear: `world.pending_diplomatic_dialogue = None`, `world.diplomatic_sabotage_popup = None` / `world.talleyrand_redemption_popup = None`

5. Add failure fallback: if action lookup fails, still clear `pending_diplomatic_dialogue` to prevent stuck state

**Priority:** CRITICAL — sabotage/redemption system entirely non-functional. Should be fixed before any balance work.

### R40: [NEW] Coalition Loyalty Penalty Formula Inverted — NEEDS DESIGN

**Problem:** `coalition.py:449` — `penalty = min(COALITION_LOYALTY_BASE + we // 10, 0)`. The `COALITION_LOYALTY_BASE` is -15. As war exhaustion (WE) rises, `we // 10` adds a positive number, making the penalty LESS negative. At WE=150, the penalty becomes `min(-15 + 15, 0) = 0` — the penalty **vanishes** when it should be strongest.

**Root cause:** `min()` should be `max()` — and the WE component should subtract, not add.

**Example:**
```python
# CURRENT (broken):
# WE=0:   min(-15 + 0, 0)  = -15  (correct at start)
# WE=100: min(-15 + 10, 0) = -5   (penalty shrinks — WRONG)
# WE=150: min(-15 + 15, 0) = 0    (penalty gone — WRONG)

# FIXED:
# penalty = max(COALITION_LOYALTY_BASE - we // 10, -30)  # grows with WE, capped at -30
# WE=0:   max(-15 - 0, -30)  = -15
# WE=100: max(-15 - 10, -30) = -25
# WE=150: max(-15 - 15, -30) = -30  (capped)
```

**File:** `backend/game_logic/coalition.py:449`

### R41: [NEW] Sabotage/Redemption Dialogue Actions Unwired in Executor — NEEDS DESIGN

**Problem:** `_process_dialogue_choice()` in `executor.py` has an `action_map` dict that maps dialogue keywords to handler functions. The sabotage actions (`confront_sabotage`, `overlook_sabotage`) and redemption actions (`redemption_apologize`, `redemption_replace`, `redemption_continue`) have NO entries. When a player clicks [Confront] or [Apologize], the executor returns "Unknown dialogue action."

**Note:** This overlaps with R37 (layers 2-3). R37 is the full 3-layer bug. R41 specifically tracks the executor wiring.

**Root cause:** `resolve_confrontation()` and `apply_redemption_choice()` exist in `diplomatic_defiance.py` but were never called from the executor action map.

**Proposed fix:** Add to `action_map` in `_process_dialogue_choice()`:
```python
"confront_sabotage": lambda: resolve_confrontation(world, "confront"),
"overlook_sabotage": lambda: resolve_confrontation(world, "overlook"),
"redemption_apologize": lambda: apply_redemption_choice(world, "apologize"),
"redemption_replace": lambda: apply_redemption_choice(world, "replace"),
"redemption_continue": lambda: apply_redemption_choice(world, "continue"),
```
Then clear `pending_diplomatic_dialogue` after each handler.

**File:** `backend/commands/executor.py` (`_process_dialogue_choice`)

### R42: [NEW] Pre-Proposal Objection Override Actions Unwired — NEEDS DESIGN

**Problem:** When Talleyrand objects to a proposal (`_merge_pre_proposal_objection()` in `diplomatic_defiance.py`), the popup offers [Proceed] / [Modify] / [Cancel]. The "Proceed" button generates action string `send_override` and "Modify" generates `send_suggested`. Neither action string has a handler in the executor.

**Root cause:** `_merge_pre_proposal_objection()` at ~line 252 creates these actions but `_process_dialogue_choice()` has no entries for them.

**Example flow:**
```
1. Player: "Talleyrand, propose alliance with Prussia"
2. Talleyrand objects: "This risks a coalition, Sire"
3. Popup: [Proceed Anyway] [Modify Terms] [Cancel]
4. Player clicks [Proceed Anyway]
5. Executor receives action "send_override" -> "Unknown dialogue action"
6. Dialogue state is now stuck
```

**Proposed fix:** Add handlers:
- `send_override` -> re-invoke proposal with original terms, bypassing objection
- `send_suggested` -> re-invoke with modified terms from objection data
- Both must clear `pending_diplomatic_dialogue`

**File:** `backend/commands/executor.py` (`_process_dialogue_choice`)

### R43: [NEW] AI-AI Proposal Spam — No Per-Pair Cooldown — NEEDS DESIGN

**Problem:** `_ratify_ai_ai_treaty()` in `ai_diplomacy.py:1127` ratifies treaties but never sets any cooldown. The same pair (e.g. Austria-Prussia) can upgrade their relationship every single turn: PEACE -> OPEN_BORDERS -> NON_AGGRESSION -> DEFENSIVE_ALLIANCE -> ALLIANCE in 4 turns.

The per-turn cap (`_AI_AI_MAX_TREATIES_PER_TURN = 2`) only limits total treaties across ALL pairs, not repeated upgrades by the same pair.

**Root cause:** No equivalent of `world.proposal_cooldowns[diplo_key] = N` after AI-AI ratification.

**Example:**
```
Turn 10: Austria + Prussia sign Open Borders
Turn 11: Austria + Prussia sign Non-Aggression  (no cooldown!)
Turn 12: Austria + Prussia sign Defensive Alliance
Turn 13: Austria + Prussia sign Alliance
# 4-turn pipeline from PEACE to ALLIANCE
```

**Proposed fix:** After `_ratify_ai_ai_treaty()`, set `world.proposal_cooldowns[diplo_key] = 3` (same cooldown as player proposals). Check cooldown at start of `_evaluate_ai_ai_proposal()`.

**File:** `backend/game_logic/ai_diplomacy.py:1127-1203`

---

## HIGH BUGS

### R3: Treaty Clause Gold/Turn Never Transfers — NEEDS DESIGN

**Problem:** `# TODO: Session 3` — gold-per-turn treaty clauses are stored but never enforced. Every financial clause is meaningless.

**Proposed fix:** In `advance_turn()`, after trade income processing, iterate `world.active_treaties` and transfer gold-per-turn amounts between nations. Add gold floor check (nation gold cannot go below 0 from treaty obligations — if can't pay, treaty violation event fires).

**Example:**
```python
# In advance_turn, after trade income:
for treaty in world.active_treaties:
    for clause in treaty.get("clauses", []):
        if clause["type"] == "gold_per_turn":
            from_nation = clause["from"]
            to_nation = clause["to"]
            amount = int(clause["amount"])
            available = max(0, world.nation_gold.get(from_nation, 0))
            transfer = min(amount, available)
            world.nation_gold[from_nation] -= transfer
            world.nation_gold[to_nation] += transfer
            if transfer < amount:
                # Treaty violation -- can't pay
                queue_dispatch_event(world, "treaty_obligation_failed", ...)
```

Also add gold floor: `world.nation_gold[nation] = max(0, ...)` in `_process_treaty_clauses`.

### R5a: Armistice Expiration — NEEDS DESIGN

**Problem:** `_process_armistice_expiration()` returns `[]`. Armistices never expire.

**Proposed fix:** Track `armistice_turns[diplo_key]` counting turns in ARMISTICE state. After minimum 3 turns, transition to PEACE automatically (per spec S5b). Generate dispatch event: "The armistice with Prussia has concluded. A fragile peace takes hold." If relations < -60, transition to WAR instead of PEACE (armistice collapses).

**File:** `backend/game_logic/diplomacy.py:1157-1162`

### R5b: Armistice Cooldowns — NEEDS DESIGN

**Problem:** Cooldowns initialized but never set.

**Proposed fix:** In `_ratify_treaty()`, when transitioning TO ARMISTICE: `world.armistice_cooldowns[diplo_key] = 5`. Block new armistice proposals when cooldown > 0. Decrement in `_decrement_cooldowns()` (already called in advance_turn).

### R44: [NEW] AI Nation DP Never Stored — NEEDS DESIGN

**Problem:** `_process_dp_regen()` in `diplomacy.py:1107-1132` calculates DP for all nations including AI, but only stores it for the player nation. The AI branch has a comment `# AI nations: store in nation_dp dict for future use` but no actual storage code. AI diplomatic actions that check DP cost will either skip the check or use a default value.

**Example:**
```python
# diplomacy.py:1128-1131
if nation == world.player_nation:
    world.diplomatic_points = int(dp)
# AI nations: store in nation_dp dict for future use
# (AI diplomatic actions handled in Session 4)
# ^^^ This comment was never followed up -- no storage code
```

**Proposed fix:** Add `world.nation_dp[nation] = int(dp)` for AI nations. Initialize `nation_dp = {}` on WorldState. Deduct DP when AI nations make proposals.

**File:** `backend/game_logic/diplomacy.py:1128-1132`

### R45: [NEW] Downgrade Doesn't Clean active_treaties — NEEDS DESIGN

**Problem:** `execute_downgrade()` in `diplomacy.py:854` changes `diplomatic_states[diplo_key]` to the lower state but never removes the old treaty from `world.active_treaties`. Result: treaty clauses (gold/turn, AP penalties, Continental System) continue executing for a treaty that no longer exists.

**Example:**
```
Turn 10: France-Austria ALLIANCE. active_treaties has {"type": "alliance", "clauses": [{"gold_per_turn": 50}]}
Turn 15: France downgrades to DEFENSIVE_ALLIANCE. diplomatic_states updated.
Turn 16: active_treaties STILL has the alliance treaty -> gold transfer continues (if R3 is fixed)
```

**Proposed fix:** In `execute_downgrade()`, after changing state, remove the old treaty from `active_treaties`:
```python
world.active_treaties = [t for t in world.active_treaties
                         if not (t.get("nations") == {nation_a, nation_b}
                                 and t.get("state") == current_state)]
```

**File:** `backend/game_logic/diplomacy.py:854`

### R46: [NEW] Vassal Rebellion Doesn't Clean active_treaties — NEEDS DESIGN

**Problem:** `check_vassal_rebellion()` in `vassal.py:341-369` deletes the vassal from `world.vassals` and sets diplomatic state to WAR, but never removes the vassal treaty from `world.active_treaties`. Treaty clauses (tribute, AP penalty) continue executing for a nation that just rebelled.

**Example:**
```
Turn 10: Saxony is French vassal. active_treaties has vassal treaty with tribute clause.
Turn 15: Saxony rebels! vassal dict entry deleted. State set to WAR.
Turn 16: advance_turn processes active_treaties -> Saxony still paying tribute to France while at war
```

**Proposed fix:** In `check_vassal_rebellion()`, after `del world.vassals[vassal_name]`, also clean:
```python
world.active_treaties = [t for t in world.active_treaties
                         if not (vassal_name in t.get("nations", set())
                                 and "vassal" in t.get("type", ""))]
```

**File:** `backend/game_logic/vassal.py:350`

### R47: [NEW] Strategic Orders Not Cancelled on Peace — NEEDS DESIGN

**Problem:** When transitioning from WAR to PEACE/ARMISTICE, marshals with PURSUE orders targeting the now-peaceful nation's marshals continue pursuing. The movement is blocked by the peace check, but the order wastes the marshal's turn and doesn't auto-cancel.

**Note:** Overlaps with R30 (which describes this as a feature request). This is also a bug — the marshal gets stuck in a PURSUE loop consuming action economy.

**Proposed fix:** In `_ratify_treaty()`, when transitioning from WAR to non-WAR:
```python
for marshal in world.marshals.values():
    if hasattr(marshal, 'strategic_order') and marshal.strategic_order:
        order = marshal.strategic_order
        if order.order_type == "PURSUE":
            target_marshal = world.marshals.get(order.target)
            if target_marshal and target_marshal.nation in [nation_a, nation_b]:
                marshal.strategic_order = None  # Cancel
```

**File:** `backend/models/world_state.py` (in `_ratify_treaty` or called from it)

### R48: [NEW] Vassal Relations With Non-Lord Nations Unhandled — NEEDS DESIGN

**Problem:** When a nation becomes a vassal, its relations with OTHER nations (not the lord) are left unchanged but diplomatically inconsistent. If Saxony (at war with Austria) becomes France's vassal while France is allied with Austria, the Saxony-Austria war state persists alongside the France-Austria alliance. No cascade, no forced peace.

**Example:**
```
France + Austria: ALLIANCE
Saxony + Austria: WAR
France vassalizes Saxony
-> Saxony is now France's vassal but still at war with France's ally Austria
-> No resolution of this contradiction
```

**Proposed fix:** On vassalization, force-resolve conflicts:
- If vassal is at war with lord's allies -> auto-armistice with those allies
- If vassal has alliances with lord's enemies -> auto-break those alliances

**File:** `backend/game_logic/vassal.py:92` (in `create_vassal` or wrapper)

---

## MEDIUM BUGS

### R7: Defensive Alliance Uses Alliance Base Disposition — NEEDS DESIGN

**Problem:** No `"defensive_alliance"` entry in `BASE_DISPOSITION`. Uses 20 (same as ALLIANCE).

**Proposed fix:** Add `"defensive_alliance": 25` to `BASE_DISPOSITION` dict. Defensive alliances are lesser commitments — should be slightly easier to achieve.

### R12: Alliance Paradox — Silent Breaking — NEEDS DESIGN

**Problem:** Allied with Austria + Saxony. Austria attacks Saxony. France-Austria alliance silently broken. No popup, no choice.

**Proposed fix:** When war cascade would force player into war against an allied nation, show popup: "Austria has attacked your ally Saxony. Honor your alliance with Saxony? [Yes -- war with Austria] [No -- break alliance with Saxony]"

### R38: Talleyrand's Terms Show "War Score: 0" — NEEDS DESIGN

**Problem:** Template T6 (`diplomatic_templates.py:176-179`) shows "War score: 0" for peacetime proposals. Slot resolver defaults to 0. Mechanical phrasing reads like debug output.

**Proposed fix:**
- **(A) Conditional display:** Only show war score when AT_WAR
- **(C) Move numbers to ledger:** Talleyrand gives qualitative assessment, raw numbers in Diplomatic Ledger

### R39: DP Display Investigation — NEEDS DESIGN

**Problem:** User reports DP not visible. Backend is fully wired (6 layers verified). Likely Godot scene tree mismatch or label hidden/overlapped. Needs in-game investigation.

### R49: [NEW] War Exhaustion Not Reset on Peace — NEEDS DESIGN

**Problem:** `world.war_exhaustion[nation]` accumulates during coalition wars but is never reset when peace is achieved. If a second coalition forms, nations start with leftover war exhaustion from the first coalition, making them immediately push for separate peace.

**Example:**
```
Coalition War 1: Austria reaches WE=80, signs separate peace
Coalition War 2 forms: Austria starts at WE=80 instead of 0
-> Austria immediately wants peace, coalition is non-functional
```

**Proposed fix:** Reset war exhaustion for a nation when it transitions from WAR to PEACE/ARMISTICE. Or reset all WE when a coalition dissolves.

**File:** `backend/game_logic/coalition.py` (in dissolution/peace code)

### R50: [NEW] Continental System Membership Not Cleaned on Vassal Release — NEEDS DESIGN

**Problem:** `release_vassal()` in `vassal.py` removes the vassal from `world.vassals` but doesn't remove it from `world.continental_system_members`. The released nation continues suffering CS trade penalties as if still in the French system.

**Example:**
```
Turn 10: Saxony is vassal + in Continental System. Britain trade blocked.
Turn 15: France releases Saxony. vassal removed.
Turn 16: Saxony still in continental_system_members -> trade with Britain still blocked
```

**Proposed fix:** In `release_vassal()`, add: `world.continental_system_members.discard(vassal_name)`

**File:** `backend/game_logic/vassal.py` (in `release_vassal`)

### R51: [NEW] Pending Diplomatic Dialogue Not Voided When Coalition Forms — NEEDS DESIGN

**Problem:** If a player is mid-diplomatic-dialogue with a nation (e.g., proposing alliance with Austria) and a coalition forms that includes Austria, the dialogue continues as if nothing happened. The proposal can be accepted even though Austria just joined a coalition against France.

**Example:**
```
Turn 10: Player starts COURT_NATION Austria dialogue
Turn 10: Coalition forms with Austria as member (from threat spike)
Turn 11: Dialogue still active, player can "finalize" the proposal
-> Austria ratifies alliance while simultaneously in anti-France coalition
```

**Proposed fix:** In `form_coalition()`, check for and void any `pending_diplomatic_dialogue` targeting coalition members. Set `world.pending_diplomatic_dialogue = None` and queue a dispatch event: "Coalition formation has disrupted ongoing negotiations."

**File:** `backend/game_logic/coalition.py` (in `form_coalition`)

### R52: [NEW] Duplicate Continental System Implementations — NEEDS DESIGN

**Problem:** `apply_continental_system()` exists in BOTH `diplomacy.py` and `vassal.py`. The vassal version appears to be dead code (never called), but if both were called, CS effects would be doubled.

**Proposed fix:** Remove the duplicate from `vassal.py`. Ensure only `diplomacy.py` version is used. Grep codebase for callers to verify.

**File:** `backend/game_logic/vassal.py` (dead code removal)

### R53: [NEW] Sweetener Values Round to 0 for Small Amounts — NEEDS DESIGN

**Problem:** Counter-offer sweeteners (gold adjustments to improve acceptance) use integer division. For small nation gold pools, the sweetener calculation can round to 0, making the counter-offer identical to the original proposal.

**Example:**
```python
# In generate_counter_offer():
sweetener = int(nation_gold * 0.05)  # Saxony with 80 gold -> sweetener = 4
# After rounding and min/max: sweetener = 0 (below threshold)
# Counter-offer has same terms as original -> guaranteed re-rejection
```

**Proposed fix:** Set minimum sweetener floor: `sweetener = max(10, int(nation_gold * 0.05))`.

**File:** `backend/game_logic/ai_diplomacy.py` (in `generate_counter_offer`)

### R54: [NEW] War Score Sign Convention Scattered Across 5 Files — NEEDS DESIGN

**Problem:** War score is stored with alphabetically-first nation as reference (positive = first nation winning). This convention is implemented independently in 5 files: `diplomacy.py`, `ai_diplomacy.py`, `coalition.py`, `vassal.py`, `diplomatic_advisory.py`. Each file has its own sign-flip logic. Some flip correctly, some have edge cases where the sign is wrong for certain nation pairs.

**Example:**
```python
# diplomacy.py — correct:
score = world.war_scores.get(diplo_key, 0)
if nations[0] != proposer:
    score = -score

# ai_diplomacy.py — potentially wrong for AI-AI:
# Uses proposer/target but AI-AI pairs may not match the stored key order
```

**Proposed fix:** Create a single helper function `get_war_score_for(world, nation_a, nation_b)` that always returns the score from nation_a's perspective. Replace all 5 inline implementations with calls to this helper.

**File:** `backend/game_logic/diplomacy.py` (add helper, then update all callers)

### R55: [NEW] Dialogue Guard Keyword List Incomplete — NEEDS DESIGN

**Problem:** `_DIALOGUE_RESPONSE_KEYWORDS` in `main.py` gates which commands are routed to the dialogue handler vs the normal executor. New response types added in later sessions (e.g., specific sabotage/redemption keywords, counter-offer responses) may not be in this list. When a valid dialogue response isn't in the keyword list, it goes to the normal executor which returns "Unknown command."

**Proposed fix:** Audit `_DIALOGUE_RESPONSE_KEYWORDS` against all action strings generated by diplomatic dialogues. Add missing entries. Consider making the guard check `pending_diplomatic_dialogue` state instead of keyword matching for robustness.

**File:** `backend/main.py` (`_DIALOGUE_RESPONSE_KEYWORDS`)

### R56: [NEW] modify_nation_relation Has No Self-Guard — NEEDS DESIGN

**Problem:** `world.modify_nation_relation(nation, nation, amount)` can be called with the same nation for both arguments. This sets a nation's relation with itself, which wastes memory and could cause formula bugs if self-relation is accidentally read.

**Example:**
```python
# In war cascade code, if nation_a == nation_b due to edge case:
world.modify_nation_relation("France", "France", -20)
# Creates nation_relations["France|France"] = -20
# Any formula iterating nation_relations now has a self-entry
```

**Proposed fix:** Add early return: `if nation_a == nation_b: return`

**File:** `backend/models/world_state.py` (`modify_nation_relation`)

---

## LOW BUGS

### R57: [NEW] Threat Field in Dialogue Context Always 0 — NEEDS DESIGN

**Problem:** When building dialogue context for diplomatic conversations, the `threat` field is populated from `world.coalition_threat` but always reads as 0 because the lookup key doesn't match how threat is stored. Talleyrand never mentions current threat level in his advice.

**Proposed fix:** Verify the threat lookup key matches storage convention. Currently: `world.coalition_threat.get("France", 0)` — check if threat is stored under "France" or uses a different key scheme.

### R58: [NEW] Vindication Tracker Decay Never Implemented — NEEDS DESIGN

**Problem:** Vindication points are earned when a defiant marshal's action succeeds, but there's no decay mechanism. Old vindication points persist forever, never expiring. Over a long game, vindication accumulates without limit.

**Impact:** Low — vindication is a flavor/feedback system, not a core mechanic. But infinite accumulation means the tracker's value as a signal degrades over time.

**Proposed fix:** Add vindication decay of -1 per 5 turns, or set vindication entries to expire after 15 turns.

### R59: [NEW] Literal Personality Triggers Never Fire — NEEDS DESIGN

**Problem:** Marshals with `PersonalityType.LITERAL` have special diplomatic triggers defined in the personality system, but the trigger check function either doesn't match the personality type correctly or the triggers are gated behind conditions that never occur.

**Impact:** Low — literal marshals still function normally, they just miss some personality-flavored diplomatic events.

**Proposed fix:** Audit literal personality trigger conditions and fix matching logic.

### R60: [NEW] Double-Vassalization Edge Case — NEEDS DESIGN

**Problem:** If nation A vassalizes nation B, and then nation C conquers nation B's last region, there's no guard against nation C also trying to vassalize nation B. Could result in one nation being listed as vassal to two lords.

**Impact:** Low — the scenario requires very specific circumstances (active war, last region captured by a third party).

**Proposed fix:** In `create_vassal()`, check if target is already a vassal: `if vassal_name in world.vassals: return error`

**File:** `backend/game_logic/vassal.py` (in `create_vassal`)

---

---

# PART B: BALANCE ISSUES (Working But Imbalanced)

Items that function correctly but produce degenerate gameplay. Ordered by impact.

---

### R4a: No Relation Decay — NEEDS DESIGN

**Problem:** Relations never drift. Once at +100, stays forever. Zero-maintenance diplomacy after turn 10.

**Proposed fix:** Add passive relation decay of -1/turn toward 0 for relations > +10 or < -10. Skip pairs where an active diplomatic mission targets them. Skip vassal pairs (vassal loyalty is separate).

**Example:**
```
France-Austria at +50, no active mission -> +49 next turn
France-Austria at +50, IMPROVE_RELATIONS targeting Austria -> stays +50 (mission counteracts)
France-Prussia at -40, no mission -> -39 next turn (drift toward 0)
```

This means alliances require ongoing diplomatic attention — REASSURE_ALLY mission (1 DP/turn, +3 relation) becomes essential to maintain high relations.

### R4b: COURT_NATION Too Fast — NEEDS DESIGN

**Problem:** +12 relation/turn with Talleyrand. Austria flips in 6 turns.

**Proposed fix options (pick one):**

**(A) Reduce base effect:** COURT_NATION base +5/turn (from +8). With skill 10: +8/turn (from +12). Austria takes 9 turns instead of 6. Simplest fix.

**(B) Diminishing returns:** Each consecutive COURT_NATION turn on the SAME target gives -1 cumulative. Turn 1: +12, Turn 2: +11, Turn 3: +10... floor at +4. Switching targets resets the counter. Encourages rotating diplomatic attention.

**(C) Rival jealousy (pairs well with decay):** When France's relation with nation A improves, nations HOSTILE to A (at WAR or relation < -20) get -2 toward France. Courting Austria makes Britain angrier. Forces diplomatic tradeoffs.

**Recommendation:** (A) + R4a decay together. Simple, effective, breaks the exploit.

### R6: Trade Income Snowball — NEEDS DESIGN

**Problem:** ALLIANCE = 200g/turn bilateral. 4 alliances = 800g/turn. Nearly doubles France's income.

**Proposed fix — Diminishing returns per nation:**
```
1st trade partner:  full income (200g for ALLIANCE)
2nd trade partner:  75% income (150g)
3rd trade partner:  50% income (100g)
4th trade partner:  25% income (50g)
```

Total max from 4 ALLIANCE partners: 200+150+100+50 = 500g (vs current 800g). Still strong but not game-breaking. Partners sorted by state level (highest-value first gets full rate).

**Alternative:** Hard cap at 400g total trade income per nation.

### R8: Relation Penalty Dominates Wartime Proposals — NEEDS DESIGN

**Problem:** France-Prussia relation -40 = permanent -20 acceptance penalty. Military victories don't offset this. Even crushing military dominance can't force peace without sweeteners.

**Proposed fix:** Add "military pressure" modifier to acceptance formula:
```
military_pressure = max(0, war_score * 0.15) when proposer is winning
```
Up to +15 at war_score 100. Partially offsets relation penalty during active wars. Does NOT stack with Military Supremacy modifier — use whichever is higher.

**Example:** France-Prussia war, score +60, relation -40:
- Current: relation_mod = -20, total acceptance suffers
- With fix: military_pressure = +9, partially offsetting the -20

### R9: Small Battle War Score Farming — NEEDS DESIGN

**Problem:** Every battle win = +3 regardless of scale. 500-casualty skirmish counts same as Austerlitz.

**Proposed fix:** Minimum casualty threshold of 2000 total for `record_battle()` to count toward war score:
```python
def record_battle(...):
    total = attacker_casualties + defender_casualties
    if total < 2000:
        return  # Skirmish -- no diplomatic impact
```

### R11: Coalition Stalemates Last Too Long — NEEDS DESIGN

**Problem:** War exhaustion +5/turn -> 30 turns to reach separate-peace threshold.

**Proposed fix options:**
- **(A)** Increase passive WE to +8/turn (19 turns instead of 30)
- **(B)** Add stalemate auto-armistice: war score stays -10 to +10 for 8+ consecutive turns -> coalition offers armistice automatically
- **(C)** Add coalition internal friction: members lose -2 mutual relation/turn (historical infighting eventually breaks alliances)

**Recommendation:** (A) + (C) together. Faster WE + internal friction creates coalition lifecycle of ~12-15 turns instead of 30.

### R14: Vassal Release/Re-Vassalize Threat Exploit — NEEDS DESIGN

**Problem:** Vassalize (+5 threat) -> Release (-8 threat) = net -3 per cycle.

**Proposed fix:** Add per-nation `vassal_release_cooldown`: cannot re-vassalize a nation for 5 turns after release. Track in `world.vassal_release_cooldowns`.

### R15: AI-AI Diplomacy Never Degrades — NEEDS DESIGN

**Problem:** By turn 20, all AI nations are allied with each other. No betrayals, no downgrades.

**Proposed fix:** Add two AI-AI triggers:
- **Rivalry:** If two AI nations border the same uncontrolled/contested region AND both have relation > 0, -3 relation/turn (competing over territory)
- **Opportunistic downgrade:** If nation A military > 2x nation B AND relation < +30, consider downgrade one step (the strong bully the weak)

### R16: Infinite Slow Expansion via Threat Sweet Spot — NEEDS DESIGN

**Problem:** 1 battle every 2 turns = below threat decay rate. Indefinite expansion.

**Proposed fix:** Add +2 threat per region captured (new controller != starting controller). Currently only passive thresholds at 60/70/80%. Per-capture threat closes the sweet spot.

### R18: Continental System Too Weak for Its Cost — NEEDS DESIGN

**Problem:** 2 DP/turn for modest gold reduction. Always worse than COURT_NATION.

**Proposed fix options:**
- **(A)** Reduce CS cost to 1 DP/turn (half the investment, same return)
- **(B)** Add diplomatic blocking: CS members apply -10 acceptance to British proposals (prevents British alliance-building)
- **(C)** Add coalition delay: CS with 2+ members slows coalition formation by 1 extra turn

### R20: Minor Nation Skill Penalty Too Harsh — NEEDS DESIGN

**Problem:** Saxony (skill 4) vs France (skill 10): -12 acceptance penalty. Minor nation proposals always fail.

**Proposed fix:** Cap skill differential penalty at -8: `diplomat_skill_bonus = max(-8, (proposer_skill - target_skill) * 2)`.

---

---

# PART C: MISSING COMMANDS & FEATURES

Items that represent unimplemented player actions, UI improvements, or entirely new features. Ordered by value.

---

## Missing Commands

### R10: No War Declaration via Talleyrand — NEEDS DESIGN

**Problem:** `declare_war()` exists but no player command. Can only declare war by attacking.

**Proposed fix:** Wire similar to break_treaty/downgrade:
- Keywords: "declare war on", "war against", "attack nation" (when targeting a nation, not a marshal)
- Cost: 1 DP (per spec S5c)
- Talleyrand objects (STRONG) if target is neutral and threat > 50
- Calls `declare_war()` with full relation/threat penalties

### R30: Strategic Order Auto-Cancel on Peace — NEEDS DESIGN

**Problem:** S5b.4 specifies auto-cancellation of PURSUE/MOVE_TO orders against now-peaceful nations. Not implemented. Movement restriction compensates but marshal wastes a turn.

**Note:** See also R47 (HIGH BUG) — the same issue from the bug perspective (marshal stuck in loop).

**Proposed fix:** In `_ratify_treaty()`, when transitioning from WAR to non-WAR: iterate marshals, cancel PURSUE orders targeting the now-peaceful nation's marshals, cancel MOVE_TO with attack_on_arrival targeting their regions.

## Ledger & UI Improvements

### R17: Various Ledger Improvements — NEEDS DESIGN

Bundle of easy additions to diplomatic ledger:

| Sub-item | Description |
|----------|-------------|
| R17a | **War score components** — Show territory/battle/decisive/capital breakdown |
| R17b | **Proposal cooldowns** — Show remaining turns before can propose to each nation |
| R17c | **Treaty ongoing costs** — Show gold/turn breakdown per treaty |
| R17d | **DP generation factors** — Show what contributes to DP rate |
| R17e | **Relation trend** — Arrow up/down/stable based on last turn's change |
| R17f | **Mission progress projection** — "5 more turns to reach NON_AGGRESSION threshold" |

### R29: Diplomatic History in Ledger — NEEDS DESIGN

**Problem:** After 20 turns, player can't review past diplomatic interactions. No proposal history.

**Proposed fix:** Track `world.diplomatic_history` list: `[{"turn": 5, "type": "proposal", "from": "France", "to": "Prussia", "proposal_type": "peace", "outcome": "REJECT"}, ...]`. Display in Talleyrand tab or new Tab 5 in diplomatic ledger. Most recent first, max 20 entries.

### R31: Acceptance Score Preview — NEEDS DESIGN

**Problem:** Player can't see estimated acceptance for a specific proposal config before spending DP. Feasibility gives qualitative tiers only.

**Proposed fix:** Enhance feasibility response to include numerical breakdown when player asks about a specific proposal type + target: "Talleyrand estimates: base 30, relations -20, war score +9, skill +8, personality -5 = **22** (REJECT). Key obstacle: relations." Show components, not just tier.

## AI Behavior

### R19: Deferred AI Triggers P3/P5 — NEEDS DESIGN

**Problem:** AI nations don't seek alliances when threatened (P3) or negotiate when broke (P5).

**Proposed fix:** Implement the P3 and P5 triggers from the spec's decision tree. P3: when threat > 60, AI seeks non-aggression/alliance with other anti-France nations. P5: when gold < 200, AI proposes trade deals or tribute offers.

### R34: AI Diplomatic Memory / Trust History — NEEDS DESIGN

**Problem:** If the player always breaks treaties with a nation, that nation treats next proposal identically. No "fool me twice" mechanic.

**Proposed fix:** Track per-nation `diplomatic_reliability` score: +5 for honoring treaty 10+ turns, -10 for breaking a treaty. Feed into acceptance formula as +/-10 max modifier.

## Feature Proposals (New Mechanics)

### R13: No Nation Elimination — NEEDS DESIGN

**Problem:** Nation with 0 regions, 0 army continues processing. Zombie marshals, infinite negative gold.

**Proposed fix:** In `advance_turn`, if nation has 0 regions AND total army strength = 0:
- Mark eliminated (`eliminated_nations.add(nation)`)
- Skip AI/diplomacy processing
- Disband stranded marshals
- Floor nation gold at 0
- Dispatch: "{nation} has been eliminated as a political entity."

### R21: Ultimatums / Coercive Diplomacy — NEEDS DESIGN

**Problem:** No "accept peace or I declare war" mechanic. Napoleon used coercive diplomacy constantly. All proposals are neutral requests.

**Proposed design:** New command type: "Talleyrand, deliver ultimatum to Prussia: accept peace or face war."
- Cost: 2 DP (major diplomatic action)
- Acceptance formula gets a `military_threat` bonus: +15 when player has marshals adjacent to target's territory, +10 otherwise
- Relation hit regardless of outcome: -10 (ultimatums are aggressive)
- If REJECTED: player gets a casus belli (halved war declaration penalties per S5c)
- Talleyrand objects (STRONG) if threat > 50 — "Ultimatums are how coalitions are born, Sire"
- Keywords: "ultimatum", "demand... or else", "threaten", "final offer"

### R22: Marriage Alliances — NEEDS DESIGN

**Problem:** Napoleon's marriage to Marie Louise of Austria (1810) was perhaps the most consequential diplomatic act of his reign, securing 3 years of peace. This system has no personal diplomacy at all.

**Proposed design:** One-shot diplomatic action, not an ongoing system. Marriage is a special clause in alliance proposals.
- Command: "Talleyrand, propose marriage alliance with Austria"
- Prerequisite: PEACE or above with target nation. Target must have a royal family (Austria, Prussia, Saxony — not Britain).
- Cost: 3 DP (major commitment)
- Acceptance formula bonus: +20
- Effects: Auto-upgrades to ALLIANCE, Relation +30, 5-turn "honeymoon" immunity (no war/downgrade), Threat -10, Coalition brewing pauses 3 turns
- Limit: ONE marriage alliance active at a time. Divorce costs -50 relation with target, -20 with ALL nations, +25 threat.

### R23: Marshal Morale from Diplomacy — NEEDS DESIGN

**Problem:** Declaring war, signing peace, making vassals — zero impact on marshal trust or morale. Cross-system blind spot.

**Proposed design:** Personality-based trust reactions to diplomatic events:

| Event | Aggressive Marshal | Cautious Marshal | Literal Marshal |
|-------|-------------------|-----------------|-----------------|
| War declared | +3 trust | -3 trust | 0 (follows orders) |
| Peace signed (winning) | -2 trust ("why stop?") | +2 trust | 0 |
| Peace signed (losing) | -5 trust ("coward!") | +3 trust ("wise") | 0 |
| Alliance formed | 0 | +2 trust | 0 |
| Vassal acquired (conquest) | +3 trust | -2 trust | 0 |
| Treaty broken | +2 trust ("bold") | -3 trust ("dishonorable") | 0 |

Capped at +/-5 trust per turn from diplomatic events.

### R24: Treaty Signing Ceremonies — NEEDS DESIGN

**Problem:** After turns of negotiation, the result is "Treaty ratified" — a notification. No ceremony, no drama.

**Proposed design:** When a major treaty is ratified (PEACE, ALLIANCE, VASSAL), generate a ceremony template. 3-4 templates per diplomat personality x proposal type. ~20 new templates total.

### R25: Vassal Personality Events — NEEDS DESIGN

**Problem:** Vassal management is numbers-only. No personality, no unique events. Rebellion is a threshold, not a story.

**Proposed design:** 4-5 vassal event types based on loyalty thresholds (60+, 40-59, 20-39, <20). Max 1 event per vassal per 5 turns.

### R26: Continental System Drama — NEEDS DESIGN

**Problem:** CS is "spend DP, reduce a gold counter." Should generate stories.

**Proposed design:** Smuggling events (1 per 3 turns), British countermeasures, economic hardship (-5 relation/turn after 5+ turns of CS).

### R27: Secret Treaties — NEEDS DESIGN

**Problem:** All treaties are public. Tilsit's secret articles can't happen. Reduces diplomatic intrigue.

**Proposed design:** New clause type with discovery mechanic. 20% leak chance/turn. -15 relation with all nations on discovery.

### R28: Template Variety Expansion — NEEDS DESIGN

**Problem:** ~56 unique text blocks. Noticeable repetition by turn 25.

**Proposed fix:** Add 15-20 new templates: VAGUE+WAR, VAGUE+PEACE variants, counter-offer variants per personality, historical references, seasonal flavor.

### R32: Multi-Party Peace Conferences — NEEDS DESIGN

**Problem:** All diplomacy is bilateral. No Congress of Vienna mechanic.

**Proposed design:** Special 4 DP action convening all warring parties. Conference produces bundled peace addressing all parties. Hard difficulty.

### R33: Dynastic Succession / Puppet Rulers — NEEDS DESIGN

**Problem:** Can't install family members as puppet rulers (Joseph, Louis, Jerome, Murat historically).

**Proposed design:** +1 DP on vassalization. +15 starting loyalty, +1/turn passive. -10 relation with ALL nations, +5 threat. Max 2 Bonaparte rulers at once.

### R35: Player-Specified Counter-Offer Terms — NEEDS DESIGN

**Problem:** When responding to AI proposals, "Counter-offer" runs M3 algorithm — player gets no input on terms. Stretch goal of R2.

**Proposed fix:** When player selects [Renegotiate], open clause-selection interface. Hard difficulty.

### R36: Personal Summits — NEEDS DESIGN

**Problem:** No "raft on the Niemen" moments. No face-to-face negotiation.

**Proposed design:** 2 DP + 1 turn transit. +20 acceptance bonus during summit. Risk: if authority < 40, backfires. One per nation per game.

---

## Audit Pattern Summary

The March 5 code audit found bugs using these pattern categories (from the original creative audit):

| Pattern | Count | Examples |
|---------|-------|----------|
| **Stub/TODO code** | 3 | R5a armistice expiration, R44 AI DP never stored, R3 gold clauses |
| **Code exists but never wired** | 3 | R41 sabotage handlers, R42 objection overrides, R37 popup routing |
| **Missing validation** | 3 | R56 self-relation, R60 double-vassal, R48 vassal-ally conflict |
| **Formula errors** | 3 | R40 coalition penalty inverted, R53 sweetener rounding, R54 war score sign |
| **Missing state cleanup** | 5 | R45 downgrade treaties, R46 rebellion treaties, R49 war exhaustion, R50 CS membership, R47 strategic orders |
| **Exploit loops** | 1 | R43 AI-AI spam (no cooldown) |
| **Missing decay/drift** | 1 | R58 vindication decay |
| **Display issues** | 2 | R57 threat always 0, R55 keyword list incomplete |
| **Unreachable triggers** | 1 | R59 literal personality |
| **Cross-state conflicts** | 1 | R51 dialogue vs coalition |
| **Dead code** | 1 | R52 duplicate CS |

**Total items:** 60 (R1a-R60), of which 3 DONE, 23 NEW from code audit, 34 from original creative audit.
