# Diplomacy Refinement & Cleanup

> **Created:** March 4, 2026
> **Status:** DESIGN GATE COMPLETE — Ready for implementation
> **Source:** `docs/DIPLOMACY_CREATIVE_AUDIT.md` (5-agent creative audit, 7.8/10 overall) + code audit (March 5, 2026)
> **Design gate:** March 5, 2026 — all 57 items reviewed, approved/modified/deferred
> **Process:** Implement Phases 1-4 -> UI test -> then decide on deferred features

---

## Implementation Plan

4 phases of bug fixes, cleanup, and balance. After all 4 phases + UI testing, a separate design session will evaluate deferred features (marriages, secret treaties, conferences, etc).

| Phase | Focus | Items | Est. Scope |
|-------|-------|-------|------------|
| **Phase 1** | Critical wiring (highest ROI) | R37/R41, R42, R40, R43, R2, R55 | ~6 fixes |
| **Phase 2** | State cleanup sweep | R1a/b, R3, R5a/b, R44, R45, R46, R47/R30, R48, R49, R50, R51, R52, R53, R54, R56, R57, R60, R7 | ~18 fixes |
| **Phase 3** | Balance tuning | R4a, R4b, R6, R8, R9, R11, R14, R15, R16, R18, R20 | ~11 balance changes |
| **Phase 4** | Commands & QoL | R10, R21, R23, R31, R34, R17a-c, R29, R12, R38 | ~11 features/commands |
| **UI Test** | Manual playtest in Godot | R39 (DP display investigation), verify all fixes | Godot session |
| **Future** | Deferred features (post-UI-test design session) | R22, R24-R28, R32, R33, R35, R36, R17d-f, R58, R59 | TBD |

---

## How This Works

1. Items marked **APPROVED** have passed the design gate and are ready to code
2. Items marked **APPROVED (MODIFIED)** were approved with changes noted below
3. Items marked **DEFERRED** are postponed to a future design session after UI testing
4. Items marked **MERGED** are tracked under another item
5. Items marked **DONE** were fixed during the audit session
6. `[NEW]` = Found in March 5 code audit (not in original creative audit)

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

# PHASE 1: CRITICAL WIRING (Highest ROI)

Non-functional systems that have code but are never reached. Fixing these "turns on" sabotage, redemption, counter-offers, and objection overrides.

---

### R37/R41: Sabotage Discovery & Redemption Popups + Executor Wiring — APPROVED

**Problem:** Sabotage/redemption system entirely non-functional. 3-layer bug: (1) Godot doesn't trigger popup, (2) executor action_map missing entries, (3) no handler functions wired.

**Fix:**
1. Godot: `main.gd` checks for `diplomatic_sabotage` / `talleyrand_redemption` fields BEFORE rendering chat text, triggers popup scenes
2. Add to `action_map` in `_process_dialogue_choice()`:
   - `confront_sabotage` -> `resolve_confrontation(world, "confront")`
   - `overlook_sabotage` -> `resolve_confrontation(world, "overlook")`
   - `redemption_apologize` -> `apply_redemption_choice(world, "apologize")`
   - `redemption_replace` -> `apply_redemption_choice(world, "replace")`
   - `redemption_continue` -> `apply_redemption_choice(world, "continue")`
3. Each handler clears `pending_diplomatic_dialogue` + popup fields
4. Failure fallback: always clear `pending_diplomatic_dialogue` to prevent stuck state

**Files:** `executor.py`, `main.gd`

### R42: Pre-Proposal Objection Override Actions Unwired — APPROVED

**Problem:** [Proceed Anyway] / [Modify Terms] / [Cancel] buttons on Talleyrand objection popup generate `send_override` / `send_suggested` — neither has a handler.

**Fix:**
- `send_override` -> re-invoke proposal with original terms, bypassing objection
- `send_suggested` -> re-invoke with modified terms from objection data
- Both clear `pending_diplomatic_dialogue`

**File:** `executor.py` (`_process_dialogue_choice`)

### R40: [NEW] Coalition Loyalty Penalty Formula Inverted — APPROVED

**Problem:** `min()` should be `max()`, WE component should subtract not add. Penalty vanishes when it should be strongest.

**Fix:**
```python
# BEFORE: penalty = min(COALITION_LOYALTY_BASE + we // 10, 0)
# AFTER:  penalty = max(COALITION_LOYALTY_BASE - we // 10, -30)
```

**File:** `coalition.py:449`

### R43: [NEW] AI-AI Proposal Spam — No Per-Pair Cooldown — APPROVED (MODIFIED)

**Problem:** Same AI pair can upgrade every turn: PEACE -> ALLIANCE in 4 turns.

**Fix:** After `_ratify_ai_ai_treaty()`, set `world.proposal_cooldowns[diplo_key] = 5` (modified from proposed 3 — AI pairs should upgrade slower than player proposals). Check cooldown at start of `_evaluate_ai_ai_proposal()`.

**File:** `ai_diplomacy.py:1127-1203`

### R2: Player Counter-Offer Treated as Rejection — APPROVED (Core only, stretch deferred)

**Problem:** Acceptance scores 30-49 stubbed as REJECT. Negotiation completely broken.

**Fix:**
- **Part A:** When `calculate_acceptance()` returns 30-49, run `generate_counter_offer()`. Return modified terms in popup data.
- **Part B:** Popup offers [Accept Counter] (0 DP) / [Reject] (relation -5, cooldown) / [Renegotiate] (1 DP, re-send)
- **GAP-1 (player-specified terms) DEFERRED** to R35

**Files:** `diplomacy.py`, `executor.py`, `main.py`, Godot popup

### R55: [NEW] Dialogue Guard Keyword List Incomplete — APPROVED

**Problem:** `_DIALOGUE_RESPONSE_KEYWORDS` in `main.py` missing entries for sabotage/redemption/counter-offer responses. Valid responses go to normal executor -> "Unknown command."

**Fix:** Audit keyword list against all action strings from diplomatic dialogues. Add missing entries. Keep keyword-based routing (don't refactor to state-based — too risky for working flows).

**File:** `main.py`

---

# PHASE 2: STATE CLEANUP SWEEP

Bugs where state isn't cleaned up properly — stale treaties, missing resets, formula errors. Mostly straightforward fixes with clear before/after behavior.

---

### R1a: War Score Decay No-Op — APPROVED

**Problem:** `recalculate_war_scores()` overwrites decay. Old battles contribute forever.

**Fix:** Hard cutoff — prune battle records older than 10 turns from `world.battle_records[diplo_key]`. No gradual decay (simpler, easier to debug).

**File:** `diplomacy.py` (`apply_war_score_decay`)

### R1b: Battle Records Persist Across Wars — APPROVED

**Problem:** Peace -> re-declare -> old battle score banked.

**Fix:** Clear `battle_records[diplo_key]` and `decisive_battles[diplo_key]` when transitioning OUT of WAR state.

**File:** `diplomacy.py` (state transition code)

### R3: Treaty Clause Gold/Turn Never Transfers — APPROVED

**Problem:** `# TODO: Session 3` — gold-per-turn clauses stored but never enforced.

**Fix:** In `advance_turn()` after trade income, iterate `active_treaties`, transfer gold amounts. Add gold floor (can't go below 0). On inability to pay, fire treaty violation dispatch event.

**File:** `world_state.py` (`advance_turn`)

### R5a: Armistice Expiration — APPROVED (MODIFIED)

**Problem:** `_process_armistice_expiration()` returns `[]`. Armistices never expire.

**Fix:** Track `armistice_turns[diplo_key]`. After **5 turns** (modified from proposed 3 — too short), transition to PEACE. If relations < -60, collapse to WAR instead. Dispatch event on transition.

**File:** `diplomacy.py:1157-1162`

### R5b: Armistice Cooldowns — APPROVED

**Problem:** Cooldowns initialized but never set.

**Fix:** On transition TO ARMISTICE: `world.armistice_cooldowns[diplo_key] = 5`. Block new proposals when > 0. Decrement in `_decrement_cooldowns()`.

**File:** `diplomacy.py`

### R44: [NEW] AI Nation DP Never Stored — APPROVED

**Problem:** DP calculated for AI but only stored for player. AI diplomatic costs meaningless.

**Fix:** Add `world.nation_dp[nation] = int(dp)` for AI nations. Initialize `nation_dp = {}` on WorldState. Serialize.

**File:** `diplomacy.py:1128-1132`, `world_state.py`

### R45: [NEW] Downgrade Doesn't Clean active_treaties — APPROVED

**Problem:** Downgrade changes state but old treaty persists. Clauses keep executing.

**Fix:** In `execute_downgrade()`, remove old treaty from `active_treaties`. Remove only — downgrade is termination, not replacement.

**File:** `diplomacy.py:854`

### R46: [NEW] Vassal Rebellion Doesn't Clean active_treaties — APPROVED

**Problem:** Rebellion deletes vassal entry but treaty persists. Tribute continues during war.

**Fix:** In `check_vassal_rebellion()`, after deleting vassal, also remove vassal treaty from `active_treaties`.

**File:** `vassal.py:350`

### R47/R30: Strategic Orders Not Cancelled on Peace — APPROVED (MERGED)

**Problem:** PURSUE orders targeting now-peaceful nation's marshals continue wasting turns. R30 described this as a feature request; R47 is the bug perspective.

**Fix:** In `_ratify_treaty()`, when WAR -> non-WAR: cancel PURSUE + MOVE_TO orders targeting the now-peaceful nation's marshals. Dispatch: "Marshal X's pursuit orders cancelled — armistice in effect."

**File:** `world_state.py` or `diplomacy.py`

### R48: [NEW] Vassal Relations With Non-Lord Nations Unhandled — APPROVED

**Problem:** Vassal at war with lord's ally = contradiction. No cascade, no forced peace.

**Fix:** On vassalization: auto-armistice with lord's allies, auto-break alliances with lord's enemies.

**File:** `vassal.py:92`

### R49: [NEW] War Exhaustion Not Reset on Peace — APPROVED

**Problem:** WE accumulates across coalition wars. Second coalition starts with leftover WE.

**Fix:** Reset per-nation WE when transitioning WAR -> PEACE/ARMISTICE.

**File:** `coalition.py`

### R50: [NEW] Continental System Membership Not Cleaned on Vassal Release — APPROVED

**Problem:** Released vassal stays in CS, trade still blocked.

**Fix:** In `release_vassal()`: `world.continental_system_members.discard(vassal_name)`

**File:** `vassal.py`

### R51: [NEW] Pending Dialogue Not Voided When Coalition Forms — APPROVED

**Problem:** Mid-dialogue with a nation that just joined a coalition against you.

**Fix:** In `form_coalition()`, void `pending_diplomatic_dialogue` targeting coalition members. Dispatch: "Coalition formation has disrupted ongoing negotiations."

**File:** `coalition.py`

### R52: [NEW] Duplicate Continental System Implementations — APPROVED

**Problem:** `apply_continental_system()` in both `diplomacy.py` and `vassal.py`. Vassal version is dead code.

**Fix:** Grep callers, verify, delete `vassal.py` duplicate.

**File:** `vassal.py`

### R53: [NEW] Sweetener Values Round to 0 — APPROVED (MODIFIED)

**Problem:** Small nation gold pools produce 0 sweetener. Counter-offer identical to original.

**Fix:** `sweetener = max(5, int(nation_gold * 0.05))` (modified from proposed 10 — 5 gold is enough to be non-zero without being a free gift).

**File:** `ai_diplomacy.py` (`generate_counter_offer`)

### R54: [NEW] War Score Sign Convention Scattered — APPROVED

**Problem:** Sign-flip logic independently implemented in 5 files. Edge cases for certain nation pairs.

**Fix:** Create `get_war_score_for(world, nation_a, nation_b)` helper. Single source of truth. Replace all 5 inline implementations.

**File:** `diplomacy.py` (add helper), then update `ai_diplomacy.py`, `coalition.py`, `vassal.py`, `diplomatic_advisory.py`

### R56: [NEW] modify_nation_relation Has No Self-Guard — APPROVED

**Problem:** `modify_nation_relation("France", "France", -20)` creates self-entry.

**Fix:** `if nation_a == nation_b: return`

**File:** `world_state.py`

### R57: [NEW] Threat Field in Dialogue Context Always 0 — APPROVED

**Problem:** Threat lookup key doesn't match storage convention. Talleyrand never mentions threat.

**Fix:** Verify key mismatch, fix lookup.

**File:** `diplomatic_dialogue.py` or `diplomatic_defiance.py`

### R60: [NEW] Double-Vassalization Edge Case — APPROVED

**Problem:** Nation can end up vassal to two lords.

**Fix:** `if vassal_name in world.vassals: return error`

**File:** `vassal.py` (`create_vassal`)

### R7: Defensive Alliance Uses Alliance Base Disposition — APPROVED

**Problem:** No `"defensive_alliance"` entry in `BASE_DISPOSITION`. Defaults to 20.

**Fix:** Add `"defensive_alliance": 25`.

**File:** `diplomacy.py`

---

# PHASE 3: BALANCE TUNING

Working systems that produce degenerate gameplay. Each change is independently testable.

---

### R4a: No Relation Decay — APPROVED

**Problem:** Relations never drift. Zero-maintenance diplomacy after turn 10.

**Fix:** -1/turn toward 0 for relations > +10 or < -10. Skip active mission pairs. Skip vassal pairs.

### R4b: COURT_NATION Too Fast — APPROVED (MODIFIED)

**Problem:** +12 relation/turn flips Austria in 6 turns.

**Fix:** Option A — reduce base to +5/turn (from +8). With skill 10: +8/turn. Combined with R4a decay, effective rate is +7/turn. Simple, testable.

### R6: Trade Income Snowball — APPROVED

**Problem:** 4 alliances = 800g/turn. Nearly doubles income.

**Fix:** Diminishing returns per partner: 100%/75%/50%/25%. Max from 4 ALLIANCE partners: 500g. Partners sorted by state level (highest first).

### R8: Relation Penalty Dominates Wartime Proposals — APPROVED

**Problem:** Military victories can't offset relation penalty. Crushing dominance can't force peace.

**Fix:** `military_pressure = max(0, war_score * 0.15)` up to +15. Doesn't stack with Military Supremacy — use whichever is higher.

### R9: Small Battle War Score Farming — APPROVED (MODIFIED)

**Problem:** Every battle = +3 regardless of scale. 500-casualty skirmish = Austerlitz.

**Fix:** Minimum **1000 total casualties** (modified from proposed 2000 — too high for minor nation battles) for `record_battle()` to count toward war score.

### R11: Coalition Stalemates Last Too Long — APPROVED (MODIFIED)

**Problem:** WE +5/turn = 30 turns to separate peace threshold.

**Fix:** Options A+C together. +8/turn passive WE AND -2/turn mutual coalition member relation friction. Creates ~15-turn coalition lifecycle. No auto-armistice (option B too mechanical).

### R14: Vassal Release/Re-Vassalize Threat Exploit — APPROVED

**Problem:** Vassalize/release cycle = net -3 threat per cycle.

**Fix:** `vassal_release_cooldowns[nation]` — cannot re-vassalize for 5 turns after release.

### R15: AI-AI Diplomacy Never Degrades — APPROVED

**Problem:** By turn 20, all AI nations are allied. No betrayals.

**Fix:** Two triggers:
- **Rivalry:** Two AI nations bordering same contested region AND relation > 0 → -3 relation/turn
- **Opportunistic downgrade:** Nation A military > 2x Nation B AND relation < +30 → consider downgrade

### R16: Infinite Slow Expansion via Threat Sweet Spot — APPROVED

**Problem:** 1 battle every 2 turns = below threat decay. Indefinite expansion.

**Fix:** +2 threat per region captured (new controller != starting controller).

### R18: Continental System Too Weak — APPROVED (MODIFIED)

**Problem:** 2 DP/turn for modest gold reduction. Always worse than COURT_NATION.

**Fix:** Option A — reduce CS cost to 1 DP/turn. If still weak after testing, revisit option B (diplomatic blocking).

### R20: Minor Nation Skill Penalty Too Harsh — APPROVED

**Problem:** Saxony proposals always fail due to -12 skill differential.

**Fix:** Cap at -8: `diplomat_skill_bonus = max(-8, (proposer_skill - target_skill) * 2)`

---

# PHASE 4: COMMANDS & QoL

Missing player commands, UI improvements, and lightweight new features.

---

### R10: War Declaration via Talleyrand — APPROVED

**Problem:** `declare_war()` exists but no player command. Can only declare war by attacking.

**Fix:** Keywords: "declare war on", "war against". 1 DP. Talleyrand objects (STRONG) if target neutral and threat > 50. Calls `declare_war()`.

### R21: Ultimatums / Coercive Diplomacy — APPROVED

**Problem:** No "accept or face war" mechanic. Napoleon used this constantly.

**Fix:**
- 2 DP cost
- `military_threat` acceptance bonus: +15 (adjacent marshals) / +10 (otherwise)
- Relation hit: -10 regardless of outcome
- On rejection: casus belli (halved war declaration penalties)
- Talleyrand objects (STRONG) if threat > 50
- Keywords: "ultimatum", "demand", "threaten", "final offer"

### R23: Marshal Morale from Diplomacy — APPROVED

**Problem:** Diplomatic events have zero impact on marshal trust.

**Fix:** Personality-based trust reactions:

| Event | Aggressive | Cautious | Literal |
|-------|-----------|----------|---------|
| War declared | +3 | -3 | 0 |
| Peace (winning) | -2 | +2 | 0 |
| Peace (losing) | -5 | +3 | 0 |
| Alliance formed | 0 | +2 | 0 |
| Vassal acquired | +3 | -2 | 0 |
| Treaty broken | +2 | -3 | 0 |

Capped at +/-5 trust/turn from diplomatic events.

### R31: Acceptance Score Preview — APPROVED

**Problem:** Player can't see estimated acceptance before spending DP.

**Fix:** Enhanced feasibility response with numerical breakdown: base, relations, war score, skill, personality = total. Show components + key obstacle.

### R34: AI Diplomatic Memory / Trust History — APPROVED

**Problem:** Infinite treaty-breaking has no consequences. No "fool me twice."

**Fix:** Per-nation `diplomatic_reliability`: +5 for honoring treaty 10+ turns, -10 for breaking. Feed into acceptance formula as +/-10 max modifier.

### R17a-c: Ledger Improvements (Subset) — APPROVED

| Sub-item | Description |
|----------|-------------|
| R17a | War score components in ledger (territory/battle/decisive/capital breakdown) |
| R17b | Proposal cooldowns (remaining turns before can propose to each nation) |
| R17c | Treaty ongoing costs (gold/turn per treaty) |

R17d-f (DP factors, relation trends, mission projections) **DEFERRED** to post-UI-test.

### R29: Diplomatic History in Ledger — APPROVED

**Problem:** After 20 turns, no record of past proposals.

**Fix:** `world.diplomatic_history` list, max 20 entries. Display in Talleyrand tab or Tab 5. Most recent first.

### R12: Alliance Paradox — Silent Breaking — APPROVED

**Problem:** Allied with A + B. A attacks B. Player alliance silently broken. No popup, no choice.

**Fix:** Popup: "Austria attacked your ally Saxony. {Honor alliance — war with Austria} {Break alliance with Saxony}"

### R38: Talleyrand's Terms Show "War Score: 0" — APPROVED (MODIFIED)

**Problem:** Template T6 shows "War score: 0" for peacetime proposals.

**Fix:** Conditional display — only show war score when AT_WAR. Keep numbers inline (don't move to ledger).

---

# DEFERRED (Post-UI-Test Design Session)

These items are postponed. After Phases 1-4 are implemented and UI tested, a separate design session will evaluate which (if any) to build.

---

| # | Item | Reason for Deferral |
|---|------|---------------------|
| R22 | **Marriage Alliances** | Beautiful design but adds complexity to an already deep system. Fix bugs first. |
| R24 | **Treaty Signing Ceremonies** | Pure flavor content. Write templates when system is stable. |
| R25 | **Vassal Personality Events** | Flavor before stability is backwards. |
| R26 | **Continental System Drama** | Depends on CS being mechanically meaningful first (R18). |
| R27 | **Secret Treaties** | Complex implementation (fog interaction, discovery, UI). Dedicated session. |
| R28 | **Template Variety Expansion** | Content expansion. Easy to batch later. |
| R32 | **Multi-Party Peace Conferences** | Hard difficulty. Much later session. |
| R33 | **Dynastic Succession / Puppet Rulers** | Overlaps with vassal system. Needs careful design to avoid redundancy. |
| R35 | **Player-Specified Counter-Offer Terms** | Hard, requires new UI flow. R2 basic counter-offer is enough for now. |
| R36 | **Personal Summits** | Cool but not essential. One-per-nation-per-game makes it niche. |
| R17d | **DP generation factors in ledger** | Nice-to-have. Not needed for core gameplay. |
| R17e | **Relation trend arrows in ledger** | Nice-to-have. |
| R17f | **Mission progress projection** | Nice-to-have. |
| R39 | **DP Display Investigation** | Needs in-game Godot debugging, not backend work. Tagged for UI test session. |
| R58 | **Vindication Tracker Decay** | Low-impact flavor system. |
| R59 | **Literal Personality Triggers** | Low-impact flavor. |

---

## Bug Cross-Reference (Audit -> Refinement)

| Audit Bug | Severity | Refinement Item | Phase | Status |
|-----------|----------|-----------------|-------|--------|
| BUG-1: War score decay no-op | CRITICAL | R1a | 2 | APPROVED |
| BUG-2: Battle records persist across wars | CRITICAL | R1b | 2 | APPROVED |
| BUG-3: Counter-offer treated as rejection | CRITICAL | R2 | 1 | APPROVED |
| BUG-4: Armistice expiration unimplemented | HIGH | R5a | 2 | APPROVED (MODIFIED) |
| BUG-5: Armistice cooldowns never written | HIGH | R5b | 2 | APPROVED |
| BUG-6: Treaty clause gold unenforced | HIGH | R3 | 2 | APPROVED |
| BUG-7: Treaty clause gold no floor | MEDIUM | R3 (included) | 2 | APPROVED |
| BUG-8: Defensive alliance base disposition | MEDIUM | R7 | 2 | APPROVED |
| BUG-9: Talleyrand sabotage/redemption popups unresolvable | CRITICAL | R37 | 1 | APPROVED |
| BUG-10: Talleyrand proposal terms show "war score 0" | MEDIUM | R38 | 4 | APPROVED (MODIFIED) |
| BUG-11: DP not visibly displayed in game | INVESTIGATION | R39 | UI Test | DEFERRED |
| [NEW] BUG-12: Coalition loyalty penalty inverted | CRITICAL | R40 | 1 | APPROVED |
| [NEW] BUG-13: Sabotage/redemption actions unwired in executor | CRITICAL | R41 | 1 | MERGED (R37) |
| [NEW] BUG-14: Pre-proposal objection overrides unwired | CRITICAL | R42 | 1 | APPROVED |
| [NEW] BUG-15: AI-AI proposal spam (no per-pair cooldown) | CRITICAL | R43 | 1 | APPROVED (MODIFIED) |
| [NEW] BUG-16: AI nation DP never stored | HIGH | R44 | 2 | APPROVED |
| [NEW] BUG-17: Downgrade doesn't clean active_treaties | HIGH | R45 | 2 | APPROVED |
| [NEW] BUG-18: Vassal rebellion doesn't clean active_treaties | HIGH | R46 | 2 | APPROVED |
| [NEW] BUG-19: Strategic orders not cancelled on peace | HIGH | R47 | 2 | APPROVED (MERGED R30) |
| [NEW] BUG-20: Vassal relations with non-lord nations unhandled | HIGH | R48 | 2 | APPROVED |
| [NEW] BUG-21: War exhaustion not reset on peace | MEDIUM | R49 | 2 | APPROVED |
| [NEW] BUG-22: Continental System membership not cleaned on vassal release | MEDIUM | R50 | 2 | APPROVED |
| [NEW] BUG-23: Pending dialogue not voided when coalition forms | MEDIUM | R51 | 2 | APPROVED |
| [NEW] BUG-24: Duplicate Continental System implementations | MEDIUM | R52 | 2 | APPROVED |
| [NEW] BUG-25: Sweetener values round to 0 for small amounts | MEDIUM | R53 | 2 | APPROVED (MODIFIED) |
| [NEW] BUG-26: War score sign convention scattered across 5 files | MEDIUM | R54 | 2 | APPROVED |
| [NEW] BUG-27: Dialogue guard keyword list incomplete | MEDIUM | R55 | 1 | APPROVED |
| [NEW] BUG-28: modify_nation_relation has no self-guard | MEDIUM | R56 | 2 | APPROVED |
| [NEW] BUG-29: Threat field in dialogue context always 0 | LOW | R57 | 2 | APPROVED |
| [NEW] BUG-30: Vindication tracker decay never implemented | LOW | R58 | — | DEFERRED |
| [NEW] BUG-31: Literal personality triggers never fire | LOW | R59 | — | DEFERRED |
| [NEW] BUG-32: Double-vassalization edge case | LOW | R60 | 2 | APPROVED |

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

**Total items:** 60 (R1a-R60), of which 3 DONE, 41 APPROVED, 16 DEFERRED, 23 [NEW] from code audit, 34 from original creative audit.
