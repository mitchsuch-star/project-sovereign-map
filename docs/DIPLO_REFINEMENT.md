# Diplomacy Refinement & Cleanup

> **Created:** March 4, 2026
> **Status:** R1-R60 APPROVED (design gate March 5). R61-R114 APPROVED (deep audit II gate March 2026).
> **Source:** Creative audit (7.8/10) + code audit (March 5) + deep audit II (6-agent, March 2026)
> **Process:** Implement Phases 1-4 -> UI test -> then decide on deferred features

---

## Implementation Plan

6 phases of bug fixes, cleanup, balance, and QoL. Phase 2 split into 2A (diplomacy core) and 2B (vassal + AI-AI + war transitions). After all phases + UI testing, a separate design session will evaluate deferred features.

**114 total items.** 25 DONE (incl. 5 from Phase 2B+ and 4 confidence follow-up sub-fixes), 73 APPROVED, 16 DEFERRED.

| Phase | Focus | Items | Scope |
|-------|-------|-------|-------|
| **Phase 1** | Critical wiring | R37/R41, R42, R40, R43, R2, R55, R61-R66, R74, R75, R96, R109 | ~16 fixes |
| **Phase 2A** | State cleanup — diplomacy core | R1a/b, R3, R5a/b, R44, R45, R47/R30, R48, R49, R51, R52/R64, R53, R54, R56, R57, R7, R67, R80, R82, R83 | ~19 fixes |
| **Phase 2B** | State cleanup — vassal, AI-AI, war | R46, R50, R60, R68-R73, R81, R97-R102, R105, R107-R108, R110-R111, R113-R114 | ~23 fixes |
| **Phase 3** | Balance tuning | R4a/b, R6, R8, R9, R11, R14-R16, R18, R20, R104, R106 | ~13 changes |
| **Phase 4** | Commands, QoL, Popup architecture | R10, R21, R23, R29, R31, R34, R38, R17a-c, R12, R76-R79, R84, R87-R95, R103, R112 | ~27 fixes |
| **UI Test** | Manual playtest in Godot | R39, R85, R86, verify all fixes | Godot session |
| **Future** | Deferred features | R22, R24-R28, R32-R33, R35-R36, R17d-f, R58-R59 | TBD |

---

## How This Works

1. Items marked **APPROVED** have passed the design gate and are ready to code
2. Items marked **APPROVED (MODIFIED)** were approved with changes noted below
3. Items marked **DEFERRED** are postponed to a future design session after UI testing
4. Items marked **MERGED** are tracked under another item
5. Items marked **DONE** were fixed during the audit session
6. `[NEW]` = Found in March 5 code audit (not in original creative audit)
7. `[DA2]` = Found in Deep Audit II (6-agent deep dive, March 2026)

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

# PHASE 1: CRITICAL WIRING (Highest ROI) — COMPLETE

16 fixes implemented Mar 5, 2026. 37 new tests. 5327 total tests passing.
Non-functional systems that have code but are never reached. Fixing these "turns on" sabotage, redemption, counter-offers, and objection overrides.

---

### R37/R41: Sabotage Discovery & Redemption Popups + Executor Wiring — DONE

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

### R42: Pre-Proposal Objection Override Actions Unwired — DONE

**Problem:** [Proceed Anyway] / [Modify Terms] / [Cancel] buttons on Talleyrand objection popup generate `send_override` / `send_suggested` — neither has a handler.

**Fix:**
- `send_override` -> re-invoke proposal with original terms, bypassing objection
- `send_suggested` -> re-invoke with modified terms from objection data
- Both clear `pending_diplomatic_dialogue`

**File:** `executor.py` (`_process_dialogue_choice`)

### R40: [NEW] Coalition Loyalty Penalty Formula Inverted — DONE

**Problem:** `min()` should be `max()`, WE component should subtract not add. Penalty vanishes when it should be strongest.

**Fix:**
```python
# BEFORE: penalty = min(COALITION_LOYALTY_BASE + we // 10, 0)
# AFTER:  penalty = max(COALITION_LOYALTY_BASE - we // 10, -30)
```

**File:** `coalition.py:449`

### R43: [NEW] AI-AI Proposal Spam — No Per-Pair Cooldown — DONE

**Problem:** Same AI pair can upgrade every turn: PEACE -> ALLIANCE in 4 turns.

**Fix:** After `_ratify_ai_ai_treaty()`, set `world.proposal_cooldowns[diplo_key] = 5` (modified from proposed 3 — AI pairs should upgrade slower than player proposals). Check cooldown at start of `_evaluate_ai_ai_proposal()`.

**File:** `ai_diplomacy.py:1127-1203`

### R2: Player Counter-Offer Treated as Rejection — DONE (Core only, Renegotiate deferred)

**Problem:** Acceptance scores 30-49 stubbed as REJECT. Negotiation completely broken.

**Fix:**
- **Part A:** When `calculate_acceptance()` returns 30-49, run `generate_counter_offer()`. Return modified terms in popup data.
- **Part B:** Popup offers [Accept Counter] (0 DP) / [Reject] (relation -5, cooldown) / [Renegotiate] (1 DP, re-send)
- **GAP-1 (player-specified terms) DEFERRED** to R35

**Files:** `diplomacy.py`, `executor.py`, `main.py`, Godot popup

### R55: [NEW] Dialogue Guard Keyword List Incomplete — DONE

**Problem:** `_DIALOGUE_RESPONSE_KEYWORDS` in `main.py` missing entries for sabotage/redemption/counter-offer responses. Valid responses go to normal executor -> "Unknown command."

**Fix:** Audit keyword list against all action strings from diplomatic dialogues. Add missing entries. Keep keyword-based routing (don't refactor to state-based — too risky for working flows).

**File:** `main.py`

---

# PHASE 2A: DIPLOMACY CORE CLEANUP — COMPLETE

17 fixes implemented Mar 6, 2026. 69 new tests (`test_phase2a_batch1-5.py`). 5396 total tests passing.
2 new serialized fields: `nation_dp`, `armistice_turns`.

---

### R1a: War Score Decay No-Op — DONE

**Problem:** `recalculate_war_scores()` overwrites decay. Old battles contribute forever.

**Fix:** Hard cutoff — prune battle records older than 10 turns from `world.battle_records[diplo_key]`. No gradual decay (simpler, easier to debug).

**File:** `diplomacy.py` (`apply_war_score_decay`)

### R1b: Battle Records Persist Across Wars — DONE

**Problem:** Peace -> re-declare -> old battle score banked.

**Fix:** Clear `battle_records[diplo_key]` and `decisive_battles[diplo_key]` when transitioning OUT of WAR state.

**File:** `diplomacy.py` (state transition code)

### R3: Treaty Clause Gold/Turn Never Transfers — DONE

**Problem:** `# TODO: Session 3` — gold-per-turn clauses stored but never enforced.

**Fix:** In `advance_turn()` after trade income, iterate `active_treaties`, transfer gold amounts. Add gold floor (can't go below 0). On inability to pay, fire treaty violation dispatch event.

**File:** `world_state.py` (`advance_turn`)

### R5a: Armistice Expiration — DONE

**Problem:** `_process_armistice_expiration()` returns `[]`. Armistices never expire.

**Fix:** Track `armistice_turns[diplo_key]`. After **5 turns** (modified from proposed 3 — too short), transition to PEACE. If relations < -60, collapse to WAR instead. Dispatch event on transition.

**File:** `diplomacy.py:1157-1162`

### R5b: Armistice Cooldowns — DONE

**Problem:** Cooldowns initialized but never set.

**Fix:** On transition TO ARMISTICE: `world.armistice_cooldowns[diplo_key] = 5`. Block new proposals when > 0. Decrement in `_decrement_cooldowns()`.

**File:** `diplomacy.py`

### R44: [NEW] AI Nation DP Never Stored — DONE

**Problem:** DP calculated for AI but only stored for player. AI diplomatic costs meaningless.

**Fix:** Add `world.nation_dp[nation] = int(dp)` for AI nations. Initialize `nation_dp = {}` on WorldState. Serialize.

**File:** `diplomacy.py:1128-1132`, `world_state.py`

### R45: [NEW] Downgrade Doesn't Clean active_treaties — DONE

**Problem:** Downgrade changes state but old treaty persists. Clauses keep executing.

**Fix:** In `execute_downgrade()`, remove old treaty from `active_treaties`. Remove only — downgrade is termination, not replacement.

**File:** `diplomacy.py:854`

### R46: [NEW] Vassal Rebellion Doesn't Clean active_treaties — APPROVED

**Problem:** Rebellion deletes vassal entry but treaty persists. Tribute continues during war.

**Fix:** In `check_vassal_rebellion()`, after deleting vassal, also remove vassal treaty from `active_treaties`.

**File:** `vassal.py:350`

### R47/R30: Strategic Orders Not Cancelled on Peace — DONE

**Problem:** PURSUE orders targeting now-peaceful nation's marshals continue wasting turns. R30 described this as a feature request; R47 is the bug perspective.

**Fix:** In `_ratify_treaty()`, when WAR -> non-WAR: cancel PURSUE + MOVE_TO orders targeting the now-peaceful nation's marshals. Dispatch: "Marshal X's pursuit orders cancelled — armistice in effect."

**File:** `world_state.py` or `diplomacy.py`

### R48: [NEW] Vassal Relations With Non-Lord Nations Unhandled — DONE

**Problem:** Vassal at war with lord's ally = contradiction. No cascade, no forced peace.

**Fix:** On vassalization: auto-armistice with lord's allies, auto-break alliances with lord's enemies.

**File:** `vassal.py:92`

### R49: [NEW] War Exhaustion Not Reset on Peace — DONE

**Problem:** WE accumulates across coalition wars. Second coalition starts with leftover WE.

**Fix:** Reset per-nation WE when transitioning WAR -> PEACE/ARMISTICE.

**File:** `coalition.py`

### R50: [NEW] Continental System Membership Not Cleaned on Vassal Release — DONE

**Problem:** Released vassal stays in CS, trade still blocked.

**Fix:** In `release_vassal()`: `world.continental_system_members.discard(vassal_name)`

**File:** `vassal.py`

### R51: [NEW] Pending Dialogue Not Voided When Coalition Forms — DONE

**Problem:** Mid-dialogue with a nation that just joined a coalition against you.

**Fix:** In `form_coalition()`, void `pending_diplomatic_dialogue` targeting coalition members. Dispatch: "Coalition formation has disrupted ongoing negotiations."

**File:** `coalition.py`

### R52: [NEW] Duplicate Continental System Implementations — APPROVED

**Problem:** `apply_continental_system()` in both `diplomacy.py` and `vassal.py`. Vassal version is dead code.

**Fix:** Grep callers, verify, delete `vassal.py` duplicate.

**File:** `vassal.py`

### R53: [NEW] Sweetener Values Round to 0 — DONE

**Problem:** Small nation gold pools produce 0 sweetener. Counter-offer identical to original.

**Fix:** `sweetener = max(5, int(nation_gold * 0.05))` (modified from proposed 10 — 5 gold is enough to be non-zero without being a free gift).

**File:** `ai_diplomacy.py` (`generate_counter_offer`)

### R54: [NEW] War Score Sign Convention Scattered — DONE

**Problem:** Sign-flip logic independently implemented in 5 files. Edge cases for certain nation pairs.

**Fix:** Create `get_war_score_for(world, nation_a, nation_b)` helper. Single source of truth. Replace all 5 inline implementations.

**File:** `diplomacy.py` (add helper), then update `ai_diplomacy.py`, `coalition.py`, `vassal.py`, `diplomatic_advisory.py`

### R56: [NEW] modify_nation_relation Has No Self-Guard — DONE

**Problem:** `modify_nation_relation("France", "France", -20)` creates self-entry.

**Fix:** `if nation_a == nation_b: return`

**File:** `world_state.py`

### R57: [NEW] Threat Field in Dialogue Context Always 0 — DONE

**Problem:** Threat lookup key doesn't match storage convention. Talleyrand never mentions threat.

**Fix:** Verify key mismatch, fix lookup.

**File:** `diplomatic_dialogue.py` or `diplomatic_defiance.py`

### R60: [NEW] Double-Vassalization Edge Case — APPROVED

**Problem:** Nation can end up vassal to two lords.

**Fix:** `if vassal_name in world.vassals: return error`

**File:** `vassal.py` (`create_vassal`)

### R7: Defensive Alliance Uses Alliance Base Disposition — DONE

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
| BUG-1: War score decay no-op | CRITICAL | R1a | 2A | DONE |
| BUG-2: Battle records persist across wars | CRITICAL | R1b | 2A | DONE |
| BUG-3: Counter-offer treated as rejection | CRITICAL | R2 | 1 | APPROVED |
| BUG-4: Armistice expiration unimplemented | HIGH | R5a | 2A | DONE |
| BUG-5: Armistice cooldowns never written | HIGH | R5b | 2A | DONE |
| BUG-6: Treaty clause gold unenforced | HIGH | R3 | 2A | DONE |
| BUG-7: Treaty clause gold no floor | MEDIUM | R3 (included) | 2A | DONE |
| BUG-8: Defensive alliance base disposition | MEDIUM | R7 | 2A | DONE |
| BUG-9: Talleyrand sabotage/redemption popups unresolvable | CRITICAL | R37 | 1 | APPROVED |
| BUG-10: Talleyrand proposal terms show "war score 0" | MEDIUM | R38 | 4 | APPROVED (MODIFIED) |
| BUG-11: DP not visibly displayed in game | INVESTIGATION | R39 | UI Test | DEFERRED |
| [NEW] BUG-12: Coalition loyalty penalty inverted | CRITICAL | R40 | 1 | APPROVED |
| [NEW] BUG-13: Sabotage/redemption actions unwired in executor | CRITICAL | R41 | 1 | MERGED (R37) |
| [NEW] BUG-14: Pre-proposal objection overrides unwired | CRITICAL | R42 | 1 | APPROVED |
| [NEW] BUG-15: AI-AI proposal spam (no per-pair cooldown) | CRITICAL | R43 | 1 | APPROVED (MODIFIED) |
| [NEW] BUG-16: AI nation DP never stored | HIGH | R44 | 2A | DONE |
| [NEW] BUG-17: Downgrade doesn't clean active_treaties | HIGH | R45 | 2A | DONE |
| [NEW] BUG-18: Vassal rebellion doesn't clean active_treaties | HIGH | R46 | 2 | APPROVED |
| [NEW] BUG-19: Strategic orders not cancelled on peace | HIGH | R47 | 2A | DONE |
| [NEW] BUG-20: Vassal relations with non-lord nations unhandled | HIGH | R48 | 2A | DONE |
| [NEW] BUG-21: War exhaustion not reset on peace | MEDIUM | R49 | 2A | DONE |
| [NEW] BUG-22: Continental System membership not cleaned on vassal release | MEDIUM | R50 | 2A | DONE |
| [NEW] BUG-23: Pending dialogue not voided when coalition forms | MEDIUM | R51 | 2A | DONE |
| [NEW] BUG-24: Duplicate Continental System implementations | MEDIUM | R52 | 2 | APPROVED |
| [NEW] BUG-25: Sweetener values round to 0 for small amounts | MEDIUM | R53 | 2A | DONE |
| [NEW] BUG-26: War score sign convention scattered across 5 files | MEDIUM | R54 | 2A | DONE |
| [NEW] BUG-27: Dialogue guard keyword list incomplete | MEDIUM | R55 | 1 | APPROVED |
| [NEW] BUG-28: modify_nation_relation has no self-guard | MEDIUM | R56 | 2A | DONE |
| [NEW] BUG-29: Threat field in dialogue context always 0 | LOW | R57 | 2A | DONE |
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

**R1-R60 subtotal:** 60 items. 3 DONE, 41 APPROVED, 16 DEFERRED. (23 from code audit, 34 from creative audit.)

---

# DEEP AUDIT II — March 2026

> **Method:** 6 parallel deep-dive agents across diplomacy.py, ai_diplomacy.py, coalition.py, vassal.py, executor.py, main.py, all Godot popup scripts, dispatch.py, dialogue/templates/advisory/ledger, and cross-system interactions.
> **Status:** APPROVED — all 54 items (R61-R114) approved March 2026.
> **Result:** 54 new findings. 9 HIGH, 27 MEDIUM, 18 LOW.

## Trend Analysis — What This Audit Revealed

### Trend 1: Vassal System Is the Most Under-Wired Subsystem (11 findings)

The vassal system (Session 5) never received a wiring audit comparable to what core diplomacy got. Findings span:
- Marshal assimilation not serialized (R61) — **save/load data loss**
- Rebellion doesn't inverse assimilation (R62)
- Vassal commands cost military AP on top of DP (R72)
- Vassal rebellion popup completely non-functional (R74 + R75)
- Coalition member not removed on vassalization (R68)
- cascade_triggered never cleared (R69)
- CS membership not removed on autonomy change (R70)
- Hardcoded nation lists (R71)

**Conclusion:** The vassal system needs a focused "Vassal Wiring Pass" — recommend expanding Phase 1 or adding Phase 1.5.

### Trend 2: Popup Early-Return Cascade Is a Systemic Design Flaw (9 findings)

Godot's `_on_command_result()` returns early on EVERY popup display. This drops:
- All other popups in the same response (R76 — data permanently lost)
- Treasury, AP, map updates (R77)
- Diplomatic top bar updates (R78)
- Morning dispatch data (R79)
- 6 non-diplomatic early returns also skip popup pass-throughs (R87)

This is not individual bugs — it's an architectural pattern. A popup queue + deferred response processing pattern is needed. Recommend grouping into a single "Popup Architecture" fix in Phase 4 or a dedicated sub-phase.

### Trend 3: Dispatch Event Coverage Has Holes (4 findings)

Systems added after the dispatch builder was written don't fire dispatch events:
- Auto-downgrade: no dispatch, no notification (R80)
- Coalition transitions: zero dispatch calls (R83)
- Mission completion: no dispatch event (R92)
- player_mission fog rule reads wrong key, hiding all mission events (R66)

### Trend 4: Continental System Is Entirely Dead (expands R52)

Not just duplicated code (R52) or weak balance (R18) — `apply_continental_system()` is **never called from the turn loop**. The entire subsystem is non-functional during gameplay. Tests call it directly, masking the problem. R64 upgrades this from "dead code" to "dead subsystem."

### Trend 5: State Cleanup on Transitions Remains the #1 Failure Mode

Adding R62, R68, R69, R70, R80 to the existing R45/R46/R47/R49/R50 brings the total to **10+ state cleanup bugs**. Every state transition path (peace, war, rebellion, vassalization, autonomy change, coalition dissolution) has at least one field that isn't properly cleaned up.

### Trend 6: Fog of War Has 2 Confirmed Leak Points

- R65: Advisory gives exact enemy army strength ratios (no fog filtering)
- R66: Dispatch fog rule reads `target_nation` but field is stored as `target`

---

## Phase Assignment for New Findings

| Phase | New Items | Count |
|-------|-----------|-------|
| **Phase 1** (Critical wiring) | R61-R66, R74, R75, R96, R109 | +10 |
| **Phase 2A** (Diplomacy core cleanup) | R67, R80, R82, R83 | +4 |
| **Phase 2B** (Vassal, AI-AI, war cleanup) | R68-R73, R81, R97-R102, R105, R107-R108, R110-R111, R113-R114 | +20 |
| **Phase 3** (Balance) | R104, R106 | +2 |
| **Phase 4** (Commands & QoL) | R76-R79, R84, R87-R95, R103, R112 | +16 |
| **UI Test** | R85, R86 | +2 |
| **Future** | Deferred features | R22, R24-R28, R32-R33, R35-R36, R17d-f, R58-R59 | TBD |

---

# DEEP AUDIT II — PHASE 1 ADDITIONS (Critical Wiring)

---

### R61: [NEW] original_nation Not Serialized — Save/Load Data Loss — DONE

**Problem:** `assimilate_vassal_marshals()` sets `marshal.original_nation` to track which marshals to transfer back on rebellion/release. This field is NOT in `Marshal.to_dict()` or `from_dict()`. After save/load, ALL assimilated marshals lose their origin — rebellion transfers nothing back.

**Fix:**
1. Add `original_nation` to `Marshal.__init__()` (default `None`)
2. Add to `to_dict()`: `"original_nation": self.original_nation`
3. Add to `from_dict()`: `marshal.original_nation = data.get("original_nation", None)`
4. Run `test_serialization_enforcement.py`
5. Update `SAVE_FORMAT_REFERENCE.md`

**Files:** `marshal.py`
**Severity:** HIGH (serialization violation — data loss on save/load)

### R62: [NEW] Rebellion Doesn't Clear original_nation or Reset Trust — DONE

**Problem:** When a vassal rebels, marshals are transferred back (nation changed) but:
1. `original_nation` is NOT cleared (compare `release_vassal()` which does `delattr`)
2. Trust is NOT reset (stays at assimilation value of 40 — meaningless for an enemy marshal)
3. `relationship_with_lord` not cleared

If re-vassalized later, `assimilate_vassal_marshals()` finds marshals with stale `original_nation`.

**Fix:**
1. In `check_vassal_rebellion()` after transfer: `delattr(marshal, 'original_nation')`
2. Reset `marshal.trust = Trust()` for transferred marshals
3. Clean up `relationship_with_lord` if it exists

**File:** `vassal.py:357-361`
**Severity:** HIGH (state corruption — incomplete inverse of assimilation)

### R63: [NEW] break_treaty() Never Adds Threat — TODO Never Wired — DONE

**Problem:** `diplomacy.py:1332-1333` has `# TODO: wire threat system in Session 7` with a comment specifying +15/+25 threat for treaty breaking. The `add_threat()` call was never added. Breaking alliances is a significant aggressive action with zero coalition consequence.

**Fix:** Add threat increase after treaty break: `+15` base, `+25` if breaking ALLIANCE.

**File:** `diplomacy.py:1332`
**Severity:** HIGH (missing threat accumulation — exploit vector)

### R64: [NEW] Continental System Never Called From Turn Loop — DONE

**Problem:** `apply_continental_system()` exists in both `diplomacy.py:1429` and `vassal.py:791`, but NEITHER is called from `process_diplomacy_turn()` or `_advance_turn_internal()`. The TODO at `diplomacy.py:1092-1093` was never resolved. Tests call it directly, masking the problem. **The entire Continental System is non-functional during gameplay.**

**Fix:**
1. Delete `vassal.py` duplicate (already R52)
2. Call `apply_continental_system(self)` in `world_state.py _advance_turn_internal()` after trade income
3. Verify correct ordering: trade income → CS reduction → tribute

**Expands:** R52 (was "duplicate code" → now "dead subsystem")
**Files:** `diplomacy.py`, `world_state.py`
**Severity:** HIGH (entire subsystem dead)

### R65: [NEW] Advisory Leaks Exact Enemy Strength Through Fog — DONE

**Problem:** `diplomatic_advisory.py:588-620` — `_get_nation_total_strength()` reads `marshal.strength` directly for all enemy marshals with NO fog filtering. Player can ask "Talleyrand, assess Prussia" to learn exact force ratios that the diplomatic ledger properly hides behind fog bands.

**Fix:** Use the same fog-filtering logic as `diplomatic_ledger.py` — check `get_nation_visibility()` and apply strength bands (Unknown/Stale/~5k/exact) instead of raw values.

**File:** `diplomatic_advisory.py:588-620`
**Severity:** HIGH (fog of war violation)

### R66: [NEW] Dispatch Fog Rule "player_mission" Reads Wrong Key — DONE

**Problem:** `dispatch.py:957` reads `mission.get("target_nation", "")` but the mission dict stores the target as `"target"` (set in `executor.py:11735`). Key mismatch means `"target_nation"` always returns `""`, and the fog comparison fails. **All dispatch events using the `player_mission` fog rule are silently hidden** — mission progress, paused, and cancelled events never appear in Morning Dispatch.

**Fix:** Change `mission.get("target_nation", "")` to `mission.get("target", "")`.

**File:** `dispatch.py:957`
**Severity:** HIGH (all mission dispatch events invisible)

### R74: [NEW] Vassal Rebellion Popup Never Sets pending_diplomatic_dialogue — DONE

**Problem:** When vassal rebellion is imminent, `vassal.py:278-288` sets `world.vassal_rebellion_imminent_popup` but does NOT set `world.pending_diplomatic_dialogue`. When Godot sends back the popup choice (e.g., "Talleyrand, invest regarding Saxony rebellion"), the routing guard in `main.py:538` checks `pending_diplomatic_dialogue` — it's None, so the entire dialogue routing block is skipped. The command goes to normal parsing, which fails or produces unintended behavior.

**Fix:** Either:
- (A) Create a `pending_diplomatic_dialogue` entry with invest/garrison/accept options and add handlers to `_process_dialogue_choice()`, OR
- (B) Create a dedicated `/respond_to_vassal_rebellion` endpoint

Option A is consistent with existing popup patterns.

**Files:** `vassal.py:278`, `executor.py` (add handlers)
**Severity:** CRITICAL (vassal rebellion popup buttons completely non-functional)

### R75: [NEW] Vassal Rebellion Popup Choices Intercepted by Dialogue Routing — DONE

**Problem:** Even if R74 is fixed, the rebellion popup buttons send commands like "Talleyrand, invest regarding Saxony rebellion". The keyword "invest" is in `_DIALOGUE_RESPONSE_KEYWORDS`. If a DIFFERENT `pending_diplomatic_dialogue` exists simultaneously (AI proposal arrived same turn as rebellion warning), the keyword matching intercepts the command and routes it to the wrong dialogue handler.

**Fix:** Depends on R74 fix approach. If using dedicated endpoint (R74-B), this is automatically resolved. If using dialogue pattern (R74-A), ensure vassal rebellion dialogue is mutually exclusive with proposal dialogues (rebellion popup has priority, proposal queued).

**Files:** `main.py:540-556`, `main.gd:2683-2689`
**Severity:** CRITICAL (popup collision when two events fire same turn — compounds R74)

---

# DEEP AUDIT II — PHASE 2A/2B ADDITIONS (State Cleanup)

---

### R67: [NEW] Shallow Copy of active_coalition/brewing Loses Nested Lists — DONE

**Problem:** `world_state.py:2796-2797` uses `.copy()` (shallow) for `active_coalition` and `coalition_brewing`. The `"members"` list is shared between serialized output and live state. `remove_coalition_member()` mutates the list in-place via `.remove()`, corrupting previously-captured serialization snapshots.

**Fix:** Use `copy.deepcopy()` or manually copy nested structures:
```python
"active_coalition": copy.deepcopy(self.active_coalition) if self.active_coalition else None,
```

**File:** `world_state.py:2796-2797`
**Severity:** MEDIUM (serialization corruption on coalition member removal)

### R68: [NEW] Vassalizing Coalition Member Skips remove_coalition_member() — APPROVED

**Problem:** `create_vassal_conquest()` sets diplomatic state to VASSAL but never calls `remove_coalition_member()`. The nation remains in `coalition["members"]`. Betrayal penalty (-15 relation), leader transition, and notification are all skipped. Compare with peace-transition path in `world_state.py:4042-4046` which properly calls it.

**Fix:** In `create_vassal_conquest()`, after setting VASSAL state, check `world.active_coalition` and call `remove_coalition_member()` if target was a member.

**File:** `vassal.py:110-156`
**Severity:** MEDIUM (cross-system gap — coalition stale after vassalization)

### R69: [NEW] cascade_triggered Never Cleared on Peace — APPROVED

**Problem:** `vassal.py:416-472` — `cascade_triggered` set tracks `"vassal_name|diplo_key"` entries, meant to fire "at most once per war." But the set is never cleared when war ends. If the same war reignites (peace → re-declare), the cascade is permanently blocked for that pair. Spec says "once per war" but implementation is "once per game."

**Fix:** Clear `world.cascade_triggered` entries for the relevant `diplo_key` when transitioning WAR → PEACE/ARMISTICE.

**File:** `vassal.py`, `diplomacy.py` (state transition code)
**Severity:** MEDIUM (missing state cleanup — once-per-game instead of once-per-war)

### R70: [NEW] Autonomy Change to AUTONOMOUS Doesn't Remove From CS — APPROVED

**Problem:** `apply_continental_system()` auto-joins PUPPET/SATELLITE vassals to CS. But `change_vassal_autonomy()` doesn't remove a nation from `continental_system_members` when upgrading to AUTONOMOUS. Distinct from R50 (vassal release) — this is about autonomy level change within existing vassalage.

**Fix:** In `change_vassal_autonomy()`, if new level is AUTONOMOUS: `world.continental_system_members.discard(vassal_name)`.

**File:** `vassal.py:592-640`
**Severity:** MEDIUM (CS membership stale after autonomy change)

### R71: [NEW] Hardcoded Nation List in Vassal Functions — APPROVED

**Problem:** `process_vassal_loyalty()` and `check_defection_cascade()` (vassal.py:211, 427) use `all_nations = ["France", "Britain", "Prussia", "Austria", "Saxony"]` instead of deriving from world state. Inconsistent with `coalition.py` and `diplomacy.py` which use `world.enemy_nations`.

**Fix:** Replace with `[world.player_nation] + list(world.enemy_nations)`.

**File:** `vassal.py:211, 427`
**Severity:** MEDIUM (breaks modding, inconsistent pattern)

### R72: [NEW] Vassal Commands Consume Military AP — APPROVED

**Problem:** `invest_vassal`, `change_autonomy`, `make_vassal` are NOT in `free_actions` (executor.py:1471) and NOT in `ADMIN_ACTIONS`. They consume 1 military Command Point on success, on top of their DP/gold costs. All other diplomatic actions are correctly in `free_actions`.

**Fix:** Add `"invest_vassal"`, `"change_autonomy"`, `"make_vassal"` to `free_actions` list.

**File:** `executor.py:1471`
**Severity:** MEDIUM (AP/DP double-cost inconsistency)

### R73: [NEW] /respond_to_diplomatic_dialogue Endpoint Missing Popup Pass-Throughs — APPROVED

**Problem:** `main.py:1048-1083` builds response without calling `_include_popup_passthroughs()`. Accepting a treaty can trigger coalition formation (sets `coalition_popup`), but the popup is not included in the response. It persists until next `/command` request.

**Fix:** Add `_include_popup_passthroughs(response, world)` before return.

**File:** `main.py:1048-1083`
**Severity:** MEDIUM (popup delivery delay — coalition popup after treaty acceptance)

### R80: [NEW] Auto-Downgrade Has No Dispatch Event or Notification — DONE

**Problem:** `check_auto_downgrade()` (diplomacy.py:886-949) fires `log_event()` but never calls `queue_dispatch_event()` and never creates a notification. Event type `"auto_downgrade"` absent from `_DISPATCH_EVENT_TYPES` and `_DIPLOMATIC_EVENT_TEMPLATES`. Alliance collapses happen with zero player visibility.

**Fix:**
1. Add `queue_dispatch_event()` call in `check_auto_downgrade()`
2. Add `"auto_downgrade"` to `_DISPATCH_EVENT_TYPES` and `_DIPLOMATIC_EVENT_TEMPLATES` in dispatch.py
3. Add notification via `world.notifications.add()`

**Files:** `diplomacy.py:886-949`, `dispatch.py`
**Severity:** MEDIUM (invisible state change — player has no warning)

### R81: [NEW] Ghost Nation Still Processes Diplomacy — DONE (Phase 2B+)

**Problem:** Eliminated nations (0 regions, 0 armies) still get DP regenerated (diplomacy.py:1107-1132), receive trade income (diplomacy.py:1134-1155), and participate in AI-AI diplomacy (ai_diplomacy.py:1014). No eliminated check anywhere in the diplomacy loop.

**Fix:** Add early-continue for nations with 0 regions + 0 marshals in `_process_dp_regen()`, `process_trade_income()`, and `process_ai_ai_diplomatic_phase()`.

**Confidence follow-up:** `_eliminate_nation()` now calls `remove_coalition_member()` to remove eliminated nations from active coalitions. 2 new tests.

**Files:** `diplomacy.py`, `ai_diplomacy.py`, `world_state.py:_eliminate_nation`
**Severity:** MEDIUM (ghost nations accumulate gold/DP, propose treaties with 0 armies)

### R82: [NEW] {rejection_reaction} Template Slot Never Resolved — DONE

**Problem:** T18 `proposal_rejected` templates use `{rejection_reaction}` which is never populated by `resolve_template_text()` or its callers. `_SafeFormatMap` returns the literal `{rejection_reaction}` string. Player sees: "Castlereagh receives your rejection with {rejection_reaction}."

**Fix:** Add `"rejection_reaction"` to template context. Value based on relation level: "cold fury" (<-40), "barely concealed displeasure" (-40 to 0), "diplomatic composure" (0+).

**File:** `diplomatic_templates.py:554-575`, template resolver
**Severity:** MEDIUM (visible placeholder text in player-facing dialogue)

### R83: [NEW] Coalition Events Have Zero Dispatch Calls — DONE

**Problem:** `coalition.py` has zero calls to `queue_dispatch_event()`. Coalition formation, dissolution, brewing-start, and cooldown-end never appear in Morning Dispatch. `dispatch.py` has `_build_coalition_section()` showing current STATE, but specific transition EVENTS are invisible.

**Fix:** Add `queue_dispatch_event()` calls in `form_coalition()`, `dissolve_coalition()`, and brewing-start logic.

**Files:** `coalition.py`, `dispatch.py` (add event templates)
**Severity:** MEDIUM (coalition transitions invisible in dispatch)

---

# DEEP AUDIT II — PHASE 4 ADDITIONS (Commands & QoL)

---

### R76: [NEW] Multiple Popups in Same Response Lose Second Popup — APPROVED

**Problem:** `_include_popup_passthroughs()` reads ALL popup fields from `world` and clears them. If both `coalition_popup` and `incoming_proposal` have data, both are included in the response, both cleared from world. Godot checks in priority order — first popup fires and returns early. Second popup data exists in response but is never read. Since it was cleared from world, it's **permanently lost**.

**Fix:** Implement popup priority queue:
1. Backend: only include highest-priority popup in response, leave others on world
2. OR Godot: store full response, process remaining popups after dismissal

**Files:** `main.py` (_include_popup_passthroughs), `main.gd` (_on_command_result)
**Severity:** MEDIUM (rare but unrecoverable data loss — lost proposals, sabotage events)

### R77: [NEW] Coalition Popup Dismissal Skips State Display Update — APPROVED

**Problem:** Coalition popup returns early at `main.gd:714`, skipping AP, gold, map, and notification updates. The `_on_coalition_popup_dismissed` handler only adds a log message and re-enables input. Unlike other popups whose follow-up command refreshes state, coalition popup sends no follow-up.

**Fix:** Store response data on popup show, process after dismissal (similar to `pending_enemy_phase_response` pattern).

**File:** `main.gd:710-714, 2639-2643`
**Severity:** MEDIUM (stale display until next command)

### R78: [NEW] Popup Early Returns Skip _update_diplomatic_top_bar — APPROVED

**Problem:** All 6 diplomatic popup early returns (main.gd:714, 730, 736, 752, 758, 764) skip `_update_diplomatic_top_bar(response)` at line 794. DP remaining, threat level, coalition status in top bar show stale data.

**Fix:** Call `_update_diplomatic_top_bar(response)` before each popup early return.

**File:** `main.gd:710-764`
**Severity:** MEDIUM (stale top bar data)

### R79: [NEW] Sabotage Popup Early Return Drops Morning Dispatch — APPROVED

**Problem:** Sabotage discovery popup fires during turn-end processing. The early return at main.gd:752 drops the entire turn-end response including morning dispatch data. Dispatch is never stored in `pending_dispatch_data`.

**Fix:** Store morning dispatch data before showing popup, display after dismissal.

**File:** `main.gd:748-752`
**Severity:** MEDIUM (morning dispatch lost when sabotage discovered)

### R84: [NEW] Threat Tier Notifications Not Dismissed on Form/Dissolve — APPROVED

**Problem:** TENSION/MURMURS notifications persist alongside COALITION_DECLARED. When coalition dissolves, old threat-tier notifications aren't dismissed. Stale "European Courts Concerned" appears alongside coalition warnings.

**Fix:** Dismiss threat-tier notifications when coalition forms; dismiss coalition notifications when coalition dissolves.

**File:** `coalition.py:697-737, 1032-1033`
**Severity:** LOW (stale notifications)

### R87: [NEW] 6 Non-Diplomatic Early Returns in /command Skip Popup Pass-Throughs — APPROVED

**Problem:** Tactical objection, strategic objection, clarification, glorious charge, strategic interrupt, and capture choice early returns (main.py:625-690, 504-509) don't call `_include_popup_passthroughs()`. If a popup was deferred from a previous turn, it stays on world until a non-early-return command is processed. Chained objections/charges can delay popups indefinitely.

**Fix:** Add `_include_popup_passthroughs(cleaned, world)` to each early return block.

**File:** `main.py:625-690, 504-509`
**Severity:** LOW (popup delivery delay, not data loss)

### R88: [NEW] /respond_to_objection Missing Popup Pass-Throughs — APPROVED

**Problem:** `/respond_to_objection` endpoint (main.py:970-1045) doesn't call `_include_popup_passthroughs()`. If insisting on an attack triggers combat → war declaration → diplomatic popup, it's not delivered in the response.

**Fix:** Add `_include_popup_passthroughs(response, world)` before return.

**File:** `main.py:970-1045`
**Severity:** LOW (popup delivery delay)

### R89: [NEW] Counter-Offer DP Failure Doesn't Re-Send Dialogue — APPROVED

**Problem:** `_handle_counter_ai_proposal` DP failure (executor.py:11934-11938) returns error without `diplomatic_dialogue` or `awaiting_diplomatic_response`. The dialogue is still blocking on world but no popup is re-shown. Player must type numbered choices without visible popup.

**Fix:** Include `"diplomatic_dialogue": world.pending_diplomatic_dialogue` and `"awaiting_diplomatic_response": True` in the DP failure return.

**File:** `executor.py:11934-11938`
**Severity:** LOW (UI confusion — popup disappears but dialogue still blocking)

### R90: [NEW] Mission Against Eliminated Nation Never Auto-Cancels — APPROVED

**Problem:** If Talleyrand is on a mission and the target nation is eliminated, the mission continues: spending DP each turn, modifying relations with a ghost nation, potentially "completing" against zero-region state.

**Fix:** In `_process_mission_effects()`, check if target nation has 0 regions → auto-cancel mission with dispatch event.

**File:** `diplomacy.py:1190-1290`
**Severity:** LOW (wastes DP on ghost nation)

### R91: [NEW] Dispatch Trigger 1 Proposes Wrong Type for Existing States — APPROVED

**Problem:** `dispatch.py:535-560` — Trigger 1 ("acceptance crossed 50") always proposes `"non_aggression"` regardless of current state. When state is already NON_AGGRESSION: proposes same state. When state is ALLIANCE: proposes downgrade. Should propose next upgrade tier.

**Fix:** Map current state → next upgrade type. Skip if already at ALLIANCE.

**File:** `dispatch.py:535-560`
**Severity:** LOW (misleading dispatch suggestion)

### R92: [NEW] Mission Completion Has No Dispatch Event — APPROVED

**Problem:** Mission completion (diplomacy.py:1275-1290) calls `log_event()` but not `queue_dispatch_event()`. No `diplomatic_mission_complete` template exists. The payoff of a multi-turn DP investment is invisible in Morning Dispatch.

**Fix:** Add `queue_dispatch_event()` and template for mission completion.

**Files:** `diplomacy.py:1275-1290`, `dispatch.py`
**Severity:** LOW (invisible milestone)

### R93: [NEW] KNOWN_NATIONS Hardcoded, Excludes Carved Vassals — APPROVED

**Problem:** `diplomatic_dialogue.py:36` — `KNOWN_NATIONS = {"Britain", "Prussia", "Austria", "Saxony"}` is hardcoded. Carved vassals (e.g., "Confederation of the Rhine") are never added. Discussing carved vassals with Talleyrand hits the unknown_nation handler.

**Fix:** Dynamically include vassals from `world.vassals` or `world.enemy_nations`.

**File:** `diplomatic_dialogue.py:36`
**Severity:** LOW (carved vassals can't be discussed)

### R94: [NEW] int(null) Crash Risk in Diplomatic Ledger — APPROVED

**Problem:** `diplomatic_ledger.gd:142+` uses `int(data.get("key", 0))`. If backend sends `null` value (key present but null), `.get()` returns null and `int(null)` crashes Godot. CLAUDE.md pattern warning applies.

**Fix:** Use `int(data.get("key", 0) if data.get("key", 0) != null else 0)` or backend-side null→0 coercion.

**File:** `diplomatic_ledger.gd:142+` (multiple lines)
**Severity:** LOW (defensive — backend currently sends integers)

### R95: [NEW] _on_critical_pulse Is a No-Op Stub — APPROVED

**Problem:** `diplomatic_ledger.gd:522-525` — `_on_critical_pulse()` has `pass` body. Timer fires every 0.4 seconds when threat is CRITICAL but does nothing. Appears to be an unfinished pulse animation.

**Fix:** Either implement pulse animation (color flash on threat label) or remove timer.

**File:** `diplomatic_ledger.gd:522-525`
**Severity:** LOW (cosmetic feature missing)

---

# DEEP AUDIT II — UI TEST ADDITIONS

---

### R85: [NEW] Coalition Leader Never Re-Evaluated Per-Turn — APPROVED

**Problem:** If the coalition leader's armies are destroyed, they retain leadership despite zero military contribution. Re-election only happens via `remove_coalition_member()` (separate peace). A crippled leader influences posture through personality indefinitely.

**Fix:** Add periodic leader re-evaluation in `process_coalition_turn()` when leader's strength drops below 50% of next-strongest member.

**File:** `coalition.py:1036-1039`
**Severity:** LOW (rare edge case — requires specific combat outcome)

### R86: [NEW] relationship_with_lord Dead Assignment — APPROVED

**Problem:** `vassal.py:680` sets `marshal.relationship_with_lord = "Professional"` — never declared in `__init__`, never serialized, never read. Dead code.

**Fix:** Remove the assignment. If future use intended, add to `__init__`, `to_dict()`, `from_dict()`.

**File:** `vassal.py:680`
**Severity:** LOW (dead code — cleanup item)

---

## Deep Audit II Bug Cross-Reference

| Audit Finding | Severity | Refinement Item | Phase | Status |
|---------------|----------|-----------------|-------|--------|
| original_nation not serialized | HIGH | R61 | 1 | APPROVED |
| Rebellion doesn't clear original_nation | HIGH | R62 | 1 | APPROVED |
| break_treaty() never adds threat | HIGH | R63 | 1 | APPROVED |
| Continental System never called from turn loop | HIGH | R64 | 1 | APPROVED |
| Advisory leaks exact enemy strength through fog | HIGH | R65 | 1 | APPROVED |
| Dispatch fog rule reads wrong key | HIGH | R66 | 1 | APPROVED |
| Shallow copy serialization for coalition | MEDIUM | R67 | 2A | DONE |
| Vassalizing coalition member skips cleanup | MEDIUM | R68 | 2 | APPROVED |
| cascade_triggered never cleared on peace | MEDIUM | R69 | 2 | APPROVED |
| Autonomy change doesn't remove from CS | MEDIUM | R70 | 2 | APPROVED |
| Hardcoded nation list in vassal | MEDIUM | R71 | 2 | APPROVED |
| Vassal commands consume military AP | MEDIUM | R72 | 2 | APPROVED |
| /respond_to_diplomatic_dialogue missing popups | MEDIUM | R73 | 2 | APPROVED |
| Vassal rebellion popup never sets dialogue | MEDIUM | R74 | 1 | APPROVED |
| Vassal rebellion choices intercepted by routing | MEDIUM | R75 | 1 | APPROVED |
| Multiple popups lose second popup data | MEDIUM | R76 | 4 | APPROVED |
| Coalition popup skips state display update | MEDIUM | R77 | 4 | APPROVED |
| Popup early returns skip top bar update | MEDIUM | R78 | 4 | APPROVED |
| Sabotage popup drops morning dispatch | MEDIUM | R79 | 4 | APPROVED |
| Auto-downgrade no dispatch/notification | MEDIUM | R80 | 2A | DONE |
| Ghost nation processes diplomacy | MEDIUM | R81 | 2 | APPROVED |
| {rejection_reaction} never resolved | MEDIUM | R82 | 2A | DONE |
| Coalition events zero dispatch calls | MEDIUM | R83 | 2A | DONE |
| Threat notifications not dismissed | LOW | R84 | 4 | APPROVED |
| Coalition leader never re-evaluated | LOW | R85 | UI | APPROVED |
| relationship_with_lord dead code | LOW | R86 | UI | APPROVED |
| 6 early returns skip popup pass-throughs | LOW | R87 | 4 | APPROVED |
| /respond_to_objection missing popups | LOW | R88 | 4 | APPROVED |
| Counter-offer DP fail no re-send | LOW | R89 | 4 | APPROVED |
| Mission vs eliminated nation | LOW | R90 | 4 | APPROVED |
| Trigger 1 wrong proposal type | LOW | R91 | 4 | APPROVED |
| Mission complete no dispatch | LOW | R92 | 4 | APPROVED |
| KNOWN_NATIONS excludes vassals | LOW | R93 | 4 | APPROVED |
| int(null) ledger crash risk | LOW | R94 | 4 | APPROVED |
| _on_critical_pulse no-op | LOW | R95 | 4 | APPROVED |

---

## Deep Audit II Pattern Summary

| Pattern | Count | Examples |
|---------|-------|----------|
| **Missing serialization** | 2 | R61 original_nation, R67 shallow copy |
| **Code exists but never wired** | 4 | R63 threat on break, R64 CS turn loop, R74 rebellion dialogue, R75 rebellion routing |
| **Missing state cleanup** | 5 | R62 rebellion cleanup, R68 coalition+vassal, R69 cascade_triggered, R70 CS on autonomy, R84 notifications |
| **Fog of war leaks** | 2 | R65 advisory strength, R66 dispatch key mismatch |
| **Popup architecture** | 6 | R76 multi-popup loss, R77/R78/R79 early return drops, R87/R88 endpoint gaps |
| **Missing dispatch events** | 4 | R80 auto-downgrade, R83 coalition events, R92 mission complete, R66 (hidden by wrong key) |
| **AP/DP cost errors** | 2 | R72 vassal AP, R89 counter DP re-send |
| **Display/template issues** | 3 | R82 rejection_reaction, R91 trigger type, R95 pulse stub |
| **Ghost nation** | 2 | R81 ghost processing, R90 ghost mission |
| **Hardcoded constants** | 2 | R71 nation list, R93 KNOWN_NATIONS |
| **Dead code** | 1 | R86 relationship_with_lord |

**Total new items:** 35 (R61-R95). 6 HIGH, 17 MEDIUM, 12 LOW.
---

# DEEP AUDIT II — LATE FINDINGS (diplomacy.py deep pass)

### R96: [NEW] VASSAL Not in OPEN_MOVEMENT_STATES — Lord Can't Traverse Vassal Territory — DONE

**Problem:** `diplomacy.py:40` — `OPEN_MOVEMENT_STATES = {"OPEN_BORDERS", "DEFENSIVE_ALLIANCE", "ALLIANCE"}` does not include `"VASSAL"`. `can_enter_territory()` returns `False` for lord→vassal movement. Player marshals cannot move through vassal territory, and vassal marshals cannot move through lord territory. Fundamentally breaks vassal integration.

**Fix:** Add `"VASSAL"` to `OPEN_MOVEMENT_STATES`.

**File:** `diplomacy.py:40`
**Severity:** HIGH (vassal territory inaccessible to lord)
**Phase:** 1

### R97: [NEW] declare_war() and Cascade Don't Clean active_treaties — APPROVED

**Problem:** `declare_war()` (diplomacy.py:680-761) transitions to WAR but does not remove the pair's entry from `active_treaties`. An ALLIANCE treaty with gold/turn and AP/turn clauses continues executing during wartime. `_process_war_cascade()` (line 764) has the same gap for cascading nations. R45 covers `execute_downgrade`, R46 covers rebellion — but declare_war and cascade are separate uncovered paths.

**Fix:** In `declare_war()` and `_process_war_cascade()`, remove `active_treaties[diplo_key]` after state transition.

**File:** `diplomacy.py:680-761, 764-824`
**Severity:** HIGH (alliance clauses execute during war — gold/AP flow to enemy)
**Phase:** 2

### R98: [NEW] 4 Public Functions Never Called From Production Code — DONE (Phase 2B+, jump transitions)

**Problem:** Four functions are defined with tests but never invoked during gameplay:
1. `check_relation_requirement()` (line 220) — relation gate for upgrades never enforced
2. `get_transition_dp_cost()` (line 234) — transition-specific DP costs unused (executor uses `get_dp_cost()`)
3. `modify_nation_authority()` (line 667) — AI nation authority never changes during gameplay
4. `validate_ap_clause()` (line 1409) — AP demands never validated against war_score > 80

Items 1 and 4 represent missing validation that should be wired. Items 2 and 3 represent dead/unreachable logic.

**Fix:** Wire #1 into treaty ratification (upgrades require relation threshold). Wire #4 into proposal processing. Evaluate #2/#3 — either wire or remove.

**Confidence follow-up:** `get_transition_dp_cost()` now wired into executor at all 3 DP-check sites via `transition_base` param on `get_dp_cost()`. Jump transitions (e.g. PEACE→ALLIANCE) correctly charge cumulative 6 DP instead of flat 2 DP. 5 new tests.

**File:** `diplomacy.py:220, 234, 667, 1409`, `executor.py` (3 DP-check sites)
**Severity:** MEDIUM (missing validation — upgrades/demands not properly gated)
**Phase:** 2

### R99: [NEW] declare_war() Doesn't Check Armistice Cooldowns — APPROVED

**Problem:** `declare_war()` only checks `if current_state == "WAR"` before proceeding. Even after R5b is implemented (armistice cooldowns set), `declare_war()` will bypass them entirely. Player can declare war during armistice cooldown period.

**Fix:** Add armistice cooldown check: `if world.armistice_cooldowns.get(diplo_key, 0) > 0: return error`.

**File:** `diplomacy.py:680-691`
**Severity:** MEDIUM (armistice cooldown bypass)
**Phase:** 2

### R100: [NEW] War Cascade Skips Relation Penalties — APPROVED

**Problem:** `_process_war_cascade()` (line 764-824) transitions cascading nations to WAR but applies no relation penalty. Compare `declare_war()` which applies -30 to target, -15 to others. A cascaded nation enters war with no relation change, creating nonsensical state (at WAR with positive relations → favorable acceptance formula for peace).

**Fix:** Apply -20 relation penalty between aggressor and each cascading nation.

**File:** `diplomacy.py:764-824`
**Severity:** MEDIUM (cascaded wars have no relation impact)
**Phase:** 2

### R101: [NEW] break_treaty() Doesn't Validate Breaker Is Party to Treaty — APPROVED

**Problem:** `break_treaty(pair_key, breaker_nation, world)` never validates that `breaker_nation` is in the treaty's nations list. If called with a non-party breaker, `other_nation` extraction goes wrong and relation penalties apply to wrong nations. Empty string fallback on line 1315 could trigger `modify_nation_relation` with `""`.

**Fix:** `if breaker_nation not in treaty.get("nations", []): return error`.

**File:** `diplomacy.py:1296-1315`
**Severity:** MEDIUM (missing input validation)
**Phase:** 2

### R102: [NEW] Stale war_scores Entries Never Removed — APPROVED

**Problem:** When war ends, `war_scores[diplo_key]` is never deleted. `apply_war_score_decay()` iterates ALL keys including ended wars, slowly decaying toward 0 but never removing. Dict grows unboundedly across multiple wars.

**Fix:** Delete `war_scores[diplo_key]` when transitioning OUT of WAR state (alongside R1b battle_records cleanup).

**File:** `diplomacy.py:332-372`
**Severity:** LOW (memory waste + serialization bloat)
**Phase:** 2

### R103: [NEW] Feedback Missing coalition_penalty and harshness_bonus — APPROVED

**Problem:** `_generate_feedback()` (line 576-580) `trackable` set omits `"coalition_penalty"` and `"harshness_bonus"`. If coalition penalty is the dominant negative factor, feedback reports a less impactful component as "key obstacle."

**Fix:** Add both to `trackable` set. Add corresponding entries to `FEEDBACK_STRINGS`.

**File:** `diplomacy.py:576-580`
**Severity:** LOW (misleading feedback text)
**Phase:** 4

### R104: [NEW] Sweetener/Demand Value 0 Treated as Flat Rate — APPROVED

**Problem:** `diplomacy.py:444-448` — `sweetener_total += rate * svalue if svalue else rate`. When `svalue=0` (falsy), falls back to `rate` instead of `0`. A sweetener `{"type": "territory", "value": 0}` adds +5 instead of 0.

**Fix:** Use `svalue if svalue is not None else 1` or explicit None check.

**File:** `diplomacy.py:444-448, 456-459`
**Severity:** LOW (formula edge case — 0-value sweeteners inflated)
**Phase:** 3

### R105: [NEW] _process_mission_effects Hardcodes "France" — APPROVED

**Problem:** `diplomacy.py:1268` — `world.modify_nation_relation("France", target, scaled)` hardcodes "France" instead of `world.player_nation`. Same on line 1253 with `diplomats.get("France")`. Inconsistent with rest of file which uses `world.player_nation`.

**Fix:** Replace with `world.player_nation`.

**File:** `diplomacy.py:1268, 1253`
**Severity:** LOW (modding-breaking hardcode)
**Phase:** 2

---

## Deep Audit II Late Findings Cross-Reference

| Finding | Severity | Item | Phase | Status |
|---------|----------|------|-------|--------|
| VASSAL not in OPEN_MOVEMENT_STATES | HIGH | R96 | 1 | APPROVED |
| declare_war doesn't clean active_treaties | HIGH | R97 | 2 | APPROVED |
| 4 functions never called from production | MEDIUM | R98 | 2 | APPROVED |
| declare_war bypasses armistice cooldowns | MEDIUM | R99 | 2 | APPROVED |
| Cascade skips relation penalties | MEDIUM | R100 | 2 | APPROVED |
| break_treaty no party validation | MEDIUM | R101 | 2 | APPROVED |
| Stale war_scores never removed | LOW | R102 | 2 | APPROVED |
| Feedback missing components | LOW | R103 | 4 | APPROVED |
| Sweetener 0 = flat rate | LOW | R104 | 3 | APPROVED |
| Mission hardcodes "France" | LOW | R105 | 2 | APPROVED |

### R106: [NEW] P3 AI Trigger Deferred Despite Threat System Being Complete — APPROVED

**Problem:** `ai_diplomacy.py:511-512` — P3 ("Threat > 60 AND not allied → seek alliance") is stubbed with comment "Returns None — wired when threat system is implemented (Session 7)." The threat system IS implemented (coalition.py, Session 7+8). P3 was never wired. AI nations don't proactively seek alliances when coalition threat rises — they wait passively until coalition forms.

**Fix:** Implement P3: when `world.threat_level > 60` and nation is not allied with France (state < DEFENSIVE_ALLIANCE), propose DEFENSIVE_ALLIANCE or ALLIANCE. Check cooldowns. High priority (priority 3).

**File:** `ai_diplomacy.py:511-512`
**Severity:** MEDIUM (AI behavior gap — nations should react to rising threat)
**Phase:** 3

### R107: [NEW] AI-AI Diplomacy Skips Transition Validation — States Can Jump — DONE (Phase 2B+, unified ratification)

**Problem:** `_ratify_ai_ai_treaty()` (ai_diplomacy.py:1174) sets `world.diplomatic_states[diplo_key] = target_state` directly without calling `validate_transition()`. AI-AI Trigger 1 proposes DEFENSIVE_ALLIANCE for nations at PEACE — jumping 3 intermediate states (OPEN_BORDERS, NON_AGGRESSION). Player diplomacy must follow step-by-step transitions, but AI-AI bypasses this entirely.

**Fix:** Either:
- (A) Add `validate_transition()` check before ratification (consistent with player path), or
- (B) Allow multi-step jumps for AI-AI (faster, arguably appropriate since AI-AI is simplified) but document the design decision

Option A recommended for consistency.

**Confidence follow-up (R107):** No-downgrade guard now returns error dict for player treaties (with message) instead of silent None. AI-AI path unchanged. Redundant ternary (sweetener_from/sweetener_to) simplified. 3 new tests.

**File:** `ai_diplomacy.py:1127-1174`, `world_state.py:_ratify_treaty`
**Severity:** MEDIUM (inconsistent rules — AI-AI gets shortcuts player doesn't)
**Phase:** 2

### R108: [NEW] AI-AI Ratification Doesn't Create active_treaties Entry — DONE (Phase 2B+, unified ratification)

**Problem:** `_ratify_ai_ai_treaty()` changes diplomatic state and improves relations, but never creates an `active_treaties[diplo_key]` entry. Consequences:
1. AI-AI alliances produce no trade income (process_trade_income reads active_treaties)
2. AI-AI treaties can't be found by `break_treaty()` (returns "No active treaty to break")
3. No treaty clause effects (gold/turn, AP/turn) ever apply to AI-AI treaties
4. Diplomatic ledger Treaties tab won't show AI-AI treaties

**Fix:** Create a basic treaty entry in `active_treaties` with state, parties, and creation turn. No complex clauses needed for AI-AI.

**File:** `ai_diplomacy.py:1173-1203`
**Severity:** MEDIUM (AI-AI treaties are stateless — no income, no breakability, invisible in ledger)
**Phase:** 2

### R109: [NEW] defensive_alliance Proposal Type Overwritten to "alliance" — Skips Tier — DONE

**Problem:** `ai_diplomacy.py:383` — `_build_proposal_terms` sets `terms["type"] = "alliance"` when handling `"defensive_alliance"` proposals. This was meant to reuse the alliance acceptance formula, but it destroys the proposal type. When ratified, `_ratify_treaty` maps `"alliance"` → `"ALLIANCE"`, skipping DEFENSIVE_ALLIANCE entirely. P4's correct determination of `"defensive_alliance"` via `_determine_upgrade_type()` is silently overwritten.

**Fix:** Keep original type: `terms["type"] = "defensive_alliance"`. Ensure acceptance formula handles the type (R7 adds BASE_DISPOSITION entry).

**File:** `ai_diplomacy.py:383`
**Severity:** HIGH (AI proposals skip a diplomatic tier — DEFENSIVE_ALLIANCE is unreachable via AI proposals)
**Phase:** 1

### R110: [NEW] Stalemate Counter Not Reset When War Ends — APPROVED

**Problem:** `ai_diplomacy.py:299-316` — `ai_stalemate_counters` tracks consecutive stalemate turns but is never cleared when war ends. On re-declaration, counter resumes from stale value. Since new wars start at war_score=0 (in stalemate range), P2 fires immediately, causing AI to propose armistice before any battles occur.

**Fix:** Clear `world.ai_stalemate_counters[diplo_key]` when transitioning OUT of WAR state (alongside R1b/R102 war-end cleanup).

**File:** `ai_diplomacy.py:299-316`, `diplomacy.py` (state transition)
**Severity:** MEDIUM (instant armistice proposal on war re-declaration)
**Phase:** 2

### R111: [NEW] AI-AI Trigger 3 "armistice" Type Not in Ratification state_map — APPROVED

**Problem:** `_evaluate_ai_ai_proposal` Trigger 3 (line 1087-1095) can generate `{"type": "armistice"}` when two AI nations at war should negotiate. But `_ratify_ai_ai_treaty`'s `state_map` (line 1139-1145) doesn't include `"armistice"`. The proposal is silently discarded. AI nations at war with each other can never negotiate peace via AI-AI diplomacy.

**Fix:** Add `"armistice": "ARMISTICE"` to `state_map` in `_ratify_ai_ai_treaty`.

**File:** `ai_diplomacy.py:1139-1145`
**Severity:** MEDIUM (AI-AI wars are permanent — no negotiation possible)
**Phase:** 2

### R112: [NEW] Incoming Proposal Popup Hints Always Show Generic Text — APPROVED

**Problem:** `ai_diplomacy.py:670` — `factors = acceptance.get("factors", [])`. But `calculate_acceptance()` returns key `"components"`, not `"factors"`. Wrong key → always empty list → hints always say "No strong positives identified" / "No major obstacles identified". The actual acceptance data is computed but never shown.

**Fix:** Change `"factors"` to `"components"` on line 670. Adapt the positive/negative factor extraction to read component dict entries.

**File:** `ai_diplomacy.py:670-674`
**Severity:** MEDIUM (player sees useless generic text instead of actual acceptance factors)
**Phase:** 4

### R113: [NEW] Counter-Offer Gold Sweetener Not Validated Against Treasury — DONE (Phase 2B+, income validation)

**Problem:** `ai_diplomacy.py:899-937` — `_try_add_desired_clauses` adds gold lump-sum sweeteners without checking whether the AI nation has enough gold. If accepted, `_ratify_treaty` subtracts the gold → nation treasury goes negative.

**Fix:** Add `if world.nation_gold.get(nation, 0) >= amount` guard before adding gold sweetener clauses.

**File:** `ai_diplomacy.py:899-937`
**Severity:** MEDIUM (AI nations can go to negative gold via counter-offer acceptance)
**Phase:** 2

### R114: [NEW] check_alliance_conflict Only Checks One Direction — APPROVED

**Problem:** `ai_diplomacy.py:944-1004` — Player-facing alliance conflict check verifies if the proposed nation's allies are at war with France, but NOT the reverse (if France's allies are at war with the proposed nation). Compare `_ratify_ai_ai_treaty` (line 1155-1171) which correctly checks both directions.

**Fix:** Add reverse check: for each of France's allies, check if they're at war with the proposed nation.

**File:** `ai_diplomacy.py:944-1004`
**Severity:** LOW (edge case — partially mitigated by defensive cascade)
**Phase:** 2

---

## Deep Audit II — ai_diplomacy.py Late Findings Cross-Reference

| Finding | Severity | Item | Phase | Status |
|---------|----------|------|-------|--------|
| defensive_alliance overwritten to alliance | HIGH | R109 | 1 | APPROVED |
| Stalemate counter not reset on peace | MEDIUM | R110 | 2 | APPROVED |
| AI-AI "armistice" not in state_map | MEDIUM | R111 | 2 | APPROVED |
| Proposal popup hints use wrong key | MEDIUM | R112 | 4 | APPROVED |
| Counter-offer gold not treasury-validated | MEDIUM | R113 | 2 | APPROVED |
| Alliance conflict one-direction only | LOW | R114 | 2 | APPROVED |

**Grand total:** 114 items (R1-R114). 20 DONE, 78 APPROVED, 16 DEFERRED.
