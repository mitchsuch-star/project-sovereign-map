# Bug Fixes

> **Consolidated bug tracker.** All open bugs from playtest reviews, audits, and design fixes live here.
> Iterate sessions until clean, then move to `DESIGN_REFINEMENT.md`.
>
> **Last Updated:** April 10, 2026 (Diplomacy modal/queue audit folded in. 1 new bug: PL-34. PL-27/PL-32 deepened.)

---

## Summary

| Priority | ID | Status | Description |
|----------|-----|--------|-------------|
| P1 — CRASH | PL-30 | OPEN | Godot null instance crash on diplomacy button after missed proposal result |
| P1 — DESIGN | PL-31 | **NEW** | Capital-loss instant defeat still live + broken regression test |
| P2 — UX | PL-26 | OPEN | Combat feels hopeless, no clear path to winning battles |
| P2 — UX | PL-27 | OPEN | AI proposal spam blocks all commands (GPT audit confirms: make non-blocking) |
| P2 — UX | PL-28 | OPEN | No warning before defeat, sudden game over |
| P2 — UX | PL-32 | **NEW** | Raw diplomacy labels can leak into popups (display split risk) |
| P2 — UX | PL-33 | **NEW** | "status" command falls through to Berthier recovery (first-hour UX) |
| P3 — QOL | PL-29 | OPEN | No new game / restart endpoint |
| P2 - UX | PL-34 | NEW | Queued diplomatic proposals can expire unseen behind blockers |
| **Total** | | **9 OPEN** | |

---

## Fixed Bugs Archive

28 bugs fixed across playtest Sessions 1-12, Session A, Session B, Session C. 8,093 tests total.

| ID | Summary | Fixed In |
|----|---------|----------|
| PL-1 to PL-4 | Early combat/display bugs | Sessions 1-6 |
| PL-5 | Proposal race condition + no feedback popup | Sessions 7-8 |
| PL-6 | "Harsher" terms on friendship pacts demand territory | Session 7 |
| PL-7 | Counter-offer accept/reject missing AI cooldowns | Session 7 |
| PL-8 | Counter-offer popup looks like unsolicited AI proposal | Session 9 |
| PL-9 | Acceptance mismatch — displayed % doesn't match resolution | Session 10 |
| PL-10 | "More generous" downgrades proposal type | Session 10 |
| PL-11 | Incoming AI proposals hijack player diplomatic commands (API-only) | Session 10 |
| PL-12 | Harsher terms INCREASE acceptance estimate (inverted harshness) | Session 11 |
| PL-13 | Viable proposal falsely rejected as "surpassed" | Session 11 |
| PL-14 | "Send ultimatum" — reworked as coercive diplomatic tool | Session 12 |
| PL-15 | Ultimatum demand wizard (replaces blind escalation) | Session A |
| PL-16 | Harsher demands multiplier too aggressive (absorbed into PL-15) | Session A |
| PL-17 | Manpower demand has zero acceptance penalty (absorbed into PL-18) | Session A |
| PL-18 | Typed manpower demands + DEMAND_VALUES key fixes | Session A |
| PL-19 | Dynamic ultimatum relation penalty (scales with demand severity) | Session B |
| PL-20 | EU4-style escalating territory cost + elimination guards | Session B |
| PL-21 | Phantom `connections` attribute — adjacency checks dead | Fixed in code |
| PL-22 | Phantom `income` attribute — income-weighted costs dead | Fixed in code |
| PL-23 | Authority-driven pushback, pen nudge, trust removal | Session C |
| PL-24 | Harshness scoring for all demand types | Session C |
| PL-25 | Term novelty: jitter, personality nudge, desire bias, flavor | Session C |

---

## Implementation Plan

### Session E — P1 Fixes (PL-30, PL-31)

**PL-30 (crash):** Investigate Godot null instance. Trace `add_output` call, check popup queue consumption when higher-priority popup masks result. Fix: null guard or ensure popup data persists until displayed.

**PL-31 (capital defeat):** Decision needed — remove instant capital-loss defeat or fix the test. Either way, fix regression test to target `Paris` not `Ile-de-France`. Update STATUS.md "ALL CLEAR" claim.

### Session F — P2 UX Cluster (PL-26, PL-27, PL-28, PL-33)

These four are interrelated — PL-27 (blocking proposals) compounds PL-26 (combat frustration) and PL-28 (sudden defeat). PL-33 is likely a PL-27 duplicate.

**PL-27 (blocking proposals):** Split dialogue guard into hard-stop (objections) and soft-stop (AI proposals). Make AI proposals non-blocking/dismissible with 1-turn auto-reject. Increase rejection cooldowns to 3-5 turns. This alone fixes PL-33.

**PL-28 (defeat warning):** Add defeat-imminent notification when France controls < threshold+2 regions. Morning dispatch warning. Depends on PL-31 decision (which defeat rules survive).

**PL-26 (combat balance):** Analyze defender bonus stacking. Surface counters earlier (bombardment, coordination). Consider starting situation rebalance. GPT audit says teaching problem > balance problem.

### Session G — P2 Polish + P3 (PL-32, PL-29)

**PL-32 (display labels):** Consolidate diplomacy display strings to backend only. Remove Godot-side duplicate maps. Add regression test for raw underscore tokens in popup payloads.

**PL-29 (new game):** Add `POST /new_game` endpoint. Optional autosave clear. Godot pause menu button.

### Session F/G Addendum - Diplomacy Modal / Queue Audit

The current ordering still works, but the new audit sharpens the scope:

- Treat PL-27 as the contract/interrupt root issue, not just "AI proposal spam." The fix now needs three parts in one session: hard-stop vs soft-stop taxonomy, typed popup-response migration, and proposal frequency tuning.
- Fold PL-34 into the same cluster as PL-27. Hidden expiry is the queue/timeout version of the same design bug: proposals are still being governed by blockers and parser round-trips instead of explicit player choice.
- Expand PL-32 beyond the Godot duplicate map. The counter-offer popup path in `world_state.py` and the sabotage/proposal fallback formatters also need to move onto the shared backend display helpers.
- Keep Session G after the PL-27/PL-34 work. Display cleanup should land after the typed response paths are stable, not before.

### Architecture Hardening (needs separate plan)

GPT audit identified 6 pre-expansion blockers (see STATUS.md §2). These need a consolidated sequencing plan before full-map work begins. Starting point: `docs/GPT_AUDIT_PLAN_RESULTS.md` §Priority Roadmap + existing `docs/ARCHITECTURE_REFACTORING_PLAN.md`.

---

## Open Bugs

### PL-30: Godot crash — null instance on diplomacy button after missed proposal result

**Priority:** P1 — CRASH
**Source:** Playtest Session D (Apr 10, 2026)

#### Reproduction

1. Propose non-aggression pact with Saxony, send it
2. End turn — Saxony's reply arrives but another popup (e.g. incoming AI proposal) takes priority
3. Next turn, click Diplomacy button (F1 wizard)
4. Godot crashes: `attempt to call function add_output on a base null instance`

#### Problem

When a proposal result arrives but is masked by a higher-priority popup, the result data may be consumed/cleared before the player sees it. Opening the diplomacy wizard then triggers a call to `add_output` on a null node reference.

#### Needs Analysis

- Which script has the `add_output` call? (`main.gd`, `diplomacy_wizard.gd`, or a popup script?)
- Is the null node the terminal RichTextLabel, or a popup-internal node?
- Does the proposal result get cleared by `_include_popup_passthroughs()` even when never displayed?
- Is this a scene tree ordering issue (`@onready` node path mismatch)?
- Related to PL-27 — blocking popup prevents result popup, stale state causes crash

#### Files to investigate
1. `main.gd` — `add_output` function, `_on_command_result()` popup routing
2. `diplomacy_wizard.gd` — does `open_for_nation()` assume terminal node exists?
3. `dialog_manager.gd` — modal popup priority, does consuming one popup clear data needed by another?
4. `cooldown_manager.py` / `world_state.py` — popup queue priority ordering

---

### PL-31: Capital-loss instant defeat still live + broken regression test

**Priority:** P1 — DESIGN
**Source:** GPT Audit (Apr 10, 2026) — confirmed via direct reproduction

#### Problem

Capital capture still causes instant defeat despite docs and a regression test claiming the rule was removed.

**Evidence (GPT audit verified):**
- `backend/game_logic/turn_manager.py:836-845` — capital-capture defeat branch is live code
- `tests/test_playtest_bugfixes.py:52-74` — regression test targets `Ile-de-France` (not a real region key), so it passes vacuously while `Paris` still triggers defeat
- Direct reproduction: setting `world.regions["Paris"].controller = "Prussia"` returns `{"game_over": True, "result": "defeat", "reason": "Your capital has fallen!"}`
- `docs/STATUS.md` calls bug-fix status "ALL CLEAR" — false on this core rule

#### Why this matters

- Contradicts diplomacy design where land can change hands through treaties
- Unfair: player can lose to a single AI flanking move with no recovery chance
- The regression test is a false negative — it tests a nonexistent region key

#### Relationship to PL-28

PL-28 is about missing *warning* before defeat. PL-31 is about whether capital-loss defeat should exist *at all*. They're related but independent:
- If capital-loss defeat stays: PL-28 still needs a warning system
- If capital-loss defeat is removed: PL-28 shifts to region-threshold defeat warnings

#### Proposed fix (short-term consistency)

1. **Option A (remove):** Delete the capital-capture defeat branch in `turn_manager.py`. Replace with softer consequences (morale penalty, authority drop, coalition threat).
2. **Option B (keep but fix test):** If the rule stays, fix the regression test to target `Paris` and update docs to stop claiming it was removed.
3. **Either way:** Fix `tests/test_playtest_bugfixes.py` to use `Paris` (valid region key), not `Ile-de-France`.

**GPT audit recommendation:** Remove instant capital-loss defeat. It contradicts the game's identity as a strategic/diplomatic game where setbacks are recoverable.

#### Files
- `backend/game_logic/turn_manager.py` (lines 836-845 — defeat branch)
- `tests/test_playtest_bugfixes.py` (lines 52-74 — broken test)
- `docs/STATUS.md` (false "ALL CLEAR" claim)

---

### PL-26: Combat feels hopeless — no clear path to winning battles

**Priority:** P2 — UX / BALANCE
**Source:** Playtest Session D (Apr 10, 2026)

#### Problem

4 consecutive attacks with Ney (72k troops, aggressive +15%) against Wellington (53k troops) all resulted in "defender tactical victory." Player never won a single battle across two full sessions. Wellington's defensive stance (+15%) + Hills terrain (+15%) + cautious personality (+10% outnumbered) stack to near-invincibility on defense.

No clear path to winning: attacking repeatedly bleeds troops until forced retreat, then 3-turn recovery. By recovery, enemy AI has retaken territory.

#### GPT audit corroboration

GPT audit Finding #7 confirms this is a **teaching/setup problem, not a pure balance problem**:
- Combat system IS deep — bombardment, coordination, and setup play exist
- The common "Ney attacks Wellington" opener commits the player before the game teaches the counters
- The obvious early action is punishing before the player learns alternatives

**GPT recommendation:** Keep combat depth. Surface likely outcomes and key counters earlier. Ensure at least one obvious early French preparation line is visibly better than the naive opener.

#### Needs Analysis

- Are defender bonuses stacking correctly or too generous?
- Is attacker getting appropriate bonuses for numerical superiority?
- Should the player be coached toward flanking / multi-marshal coordination / bombardment?
- Is the starting situation (Ney alone vs Wellington on Hills) a balance trap?

#### Files to investigate
1. `combat.py` — `resolve_combat()`, terrain bonuses, defender advantage
2. `combat_executor.py` — attack execution, coordination bonuses
3. `marshal.py` — `get_attack_modifier()`, `get_defense_modifier()`
4. `enemy_ai.py` — does AI stack advantages unfairly?
5. `region.py` — terrain modifier values

---

### PL-27: AI proposal spam blocks all commands

**Priority:** P2 — UX
**Source:** Playtest Session D (Apr 10, 2026)

#### Problem

Every turn, AI nations send diplomatic proposals that block ALL other commands until the player responds. Player cannot even type "status" without getting "I don't understand that choice, Sire." During playtest, 5+ proposals arrived in 7 turns, several from the same nation after rejection.

#### GPT audit corroboration

GPT audit Finding #3 + Follow-up #2 confirm this and provide architectural analysis:

**Root cause (GPT audit):** Two separate issues compounding:
1. **Frequency:** AI proposals generate too aggressively relative to cooldowns
2. **Blocking:** The command guard blocks on ANY pending diplomatic dialogue, not only blocking ones (`executor.py:460-478`, `main.py:605-620`)

**GPT structural recommendation:**
- Keep marshal objections blocking (true decision points)
- Make incoming AI proposals **non-blocking and dismissible**
- If ignored, auto-reject or expire them after one turn instead of freezing the command loop
- The dialogue lifecycle already supports non-blocking expiry (`dialogue_manager.py:78-97`) — the guards just need to stop treating every pending dialogue as blocking
- Route dialogue/interrupt responses BEFORE parser invocation to reduce brittleness (`main.py:578-638` — parser-first routing adds friction)

**Evidence:**
- Objection hard-stop: `executor.py:427-433`
- AI proposals explicitly blocking: `ai_diplomacy.py:823-855`
- Command guard blocks all dialogues: `executor.py:460-478`
- Parser-side guard: `main.py:605-620`
- 7-turn passive probe still produced 3 incoming AI proposals (confirmed during GPT audit)

#### Proposed fix (two-part)

**(A) Reduce frequency:** Longer rejection cooldowns (currently 1-2 turns, should be 3-5). Check anti-spam logic in `ai_diplomacy.py` P1-P7 triggers.

**(B) Non-blocking proposals:** Split dialogue guard into hard-stop (objections) and soft-stop (AI proposals). Soft-stop dialogues show as notifications, player responds when ready. If ignored for 1 turn, auto-reject with standard cooldown.

**Concrete UX direction:** Introduce a persistent diplomacy "desk" / "mailbox" for soft-stop items. Incoming proposals, counter-offers, and similar non-urgent diplomatic messages should land there instead of freezing the command loop. The player can open the desk from the HUD or by command, review pending items, and answer them through typed option ids. Hard-stop crises still interrupt immediately.

#### Files to investigate
1. `ai_diplomacy.py` — proposal generation frequency, cooldown checks
2. `executor.py` — dialogue guard (lines 460-478)
3. `main.py` — command routing when incoming proposal pending (lines 578-638)
4. `dialogue_manager.py` — non-blocking expiry support (lines 78-97)
5. `turn_manager.py` — enemy phase proposal generation
6. `cooldown_manager.py` — proposal cooldown durations

#### Modal/queue follow-up (Apr 10 addendum)

The deeper modal audit tightened this further:

- The real bug is broader than AI proposal frequency. `executor.py` and `main.py` still hard-stop on any pending diplomatic dialogue, even though `meta_executor.py` already distinguishes blocking vs non-blocking on `end_turn`.
- The remaining popup handlers in `main.gd` still leak back through `send_command` for incoming proposals, sabotage confrontation, vassal rebellion, and diplomatic objections. Alliance paradox is already on the typed endpoint; the rest should match it.
- Recommended hard-stop taxonomy:
  - Hard-stop: treaty-break confirmation, alliance paradox.
  - Soft-stop: incoming proposal, counter-offer, conflict alert.
  - Hybrid: sabotage confrontation and vassal rebellion should not freeze normal commands, but they should auto-default or force resolution by end-turn.
- Best-fit UX pattern: a Talleyrand "desk" / diplomatic mailbox that accumulates soft-stop items until the player opens them. That gives proposals a visible home, avoids silent expiry, and prevents the terminal from being hijacked by low-urgency interruptions.

That means PL-27 should now be treated as the umbrella "diplomacy interrupt contract" fix, not just a cooldown tweak.

---

### PL-28: No warning before defeat — sudden game over

**Priority:** P2 — UX
**Source:** Playtest Session D (Apr 10, 2026)

#### Problem

Game ended at turn 7 with "The war is over" and `victory: defeat`. Player went from 8 to 5 regions with no warning that defeat was imminent. No "you are about to lose" notification, no last-stand mechanic, no chance to react.

#### GPT audit corroboration

GPT audit Finding #1 and Follow-up #1 confirm defeat-state is inconsistent:
- Capital-loss defeat is still live (see PL-31)
- Region-threshold defeat also exists
- Code, tests, and docs disagree about what the defeat rules are
- **GPT recommendation:** Make defeat-state truth consistent NOW. Align code, tests, and docs on what causes defeat before any larger victory redesign.

#### Needs Analysis

- What is the exact defeat condition? (Region count? Capital lost? Both?)
- Should there be a 1-2 turn warning ("France is on the verge of collapse")?
- Should the notification system flag critical territory loss?
- Is the threshold too aggressive for early game?
- EU4 comparison: war exhaustion, stability, surrender conditions are all visible

#### Files to investigate
1. `world_state.py` — game over / defeat condition check
2. `turn_manager.py` — end-of-turn defeat evaluation (lines 803-845)
3. `notifications.py` — add defeat-imminent notification type
4. `dispatch.py` — morning dispatch could warn about critical territory loss

---

### PL-32: Raw diplomacy labels can leak into popups

**Priority:** P2 — UX
**Source:** GPT Audit Follow-up #3 (Apr 10, 2026)

#### Problem

Diplomacy display formatting is split across backend and Godot with duplicated display maps, creating risk of raw internal labels (e.g. `Open_borders`, `NON_AGGRESSION`) leaking into player-facing popups.

**Evidence (GPT audit):**
- Backend proposal display map: `display_names.py:125-139`
- Incoming popup keeps its own separate display map: `incoming_proposal_popup.gd:18-28`
- Backend fallback formats proposal clauses ad hoc: `main.py:233-269`
- Proposal term display rebuilt separately in dialogue helpers: `diplomatic_dialogue.py:633-705`

GPT audit did not reproduce a literal raw label during testing, but confirmed the structure is brittle enough that raw enum/action-style labels can leak through fallback paths.

#### Proposed fix

- Make backend the single owner of diplomacy display strings
- Send only final human-readable proposal/term labels to Godot
- Add a regression test that fails if popup payload text contains raw underscore tokens or enum-style treaty names

#### Files
- `backend/display_names.py` (single source — extend coverage)
- `godot-client/project-sovereign/scripts/incoming_proposal_popup.gd` (remove duplicate display map, read from backend)
- `backend/main.py` (lines 233-269 — ad hoc formatting)
- `backend/game_logic/diplomatic_dialogue.py` (lines 633-705 — separate display rebuilding)

#### Modal/queue follow-up (Apr 10 addendum)

The new audit found two more live leak paths:

- `backend/models/world_state.py:4521-4531` builds counter-offer popup clauses directly from raw clause ids, making it the strongest current leak path.
- `backend/commands/diplomatic_defiance.py:379-403` and `backend/game_logic/ai_diplomacy.py:883-904` still own separate proposal/clause formatting logic instead of reusing the backend display helpers.

So PL-32 is no longer just "remove the Godot duplicate map." It now needs a full backend-owned proposal/clause formatter that feeds incoming proposal popups, counter-offer popups, and sabotage summaries from one contract.

---

### PL-33: "status" command falls through to Berthier recovery

**Priority:** P2 — UX
**Source:** GPT Audit Follow-up (Apr 10, 2026) — manual probe

#### Problem

Typing "status" — arguably the most natural first command a new player would try — falls through to Berthier's recovery message instead of producing a game status overview. The `help` command works well and returns a strong reference, but "status" is the intuitive first-hour command that fails.

**GPT audit context:** This was noted during manual command probes. "status" fell through and hit Berthier recovery. The game has a status action (`_execute_status` in `meta_executor.py`) but the parser may not be routing "status" correctly, or a dialogue guard may be intercepting it.

#### Analysis

Mock parser DOES recognize "status" (`llm_client.py:641` — exact match `command_lower.strip() == "status"`). Parser routes it correctly. GPT audit likely hit this while a dialogue guard was active (PL-27 — incoming proposal blocking all commands). If PL-27 is fixed (non-blocking proposals), this may resolve automatically.

**Verify:** Reproduce with no pending dialogues. If "status" works cleanly with no dialogue active, this is a duplicate of PL-27 and can be closed.

#### Files to investigate
1. `executor.py` — dialogue guard may block before parsing
2. `llm_client.py:641` — mock parser handles "status" correctly
3. `meta_executor.py` — `_execute_status()` exists and should be reachable

---

### PL-34: Queued diplomatic proposals can expire unseen behind blockers

**Priority:** P2 — UX / CONTRACT
**Source:** GPT Audit Modal/Queue Addendum (Apr 10, 2026)

#### Problem

When one blocking diplomatic dialogue sits unanswered, later proposals can queue and then expire before the player ever sees them. That means stacked diplomacy is being resolved by hidden timers and queue drops, not by explicit player choice.

**Evidence (GPT audit):**
- Queue expiry removes items after 3 turns: `ai_diplomacy.py:304-312`
- Queue overflow keeps only the best 3 priorities: `ai_diplomacy.py:315-349`
- Queued delivery expires old items before attempting delivery: `ai_diplomacy.py:1009-1024`
- Blocking dialogues only clear on the stale-dialogue path: `dialogue_manager.py:78-97`, `world_state.py:4149-4151`
- Source-level audit reproduction: a turn-5 Austria proposal stayed blocking through turns 6-7; a same-turn queued Prussian proposal expired on turn 8 before delivery, so it was never shown

#### Why this matters

- Hidden expiry makes diplomacy feel inconsistent and unfair.
- It undermines the whole "respond later" direction for soft-stop proposals.
- It also makes bug reports harder to reason about, because the player never sees the proposal that was silently dropped.

#### Proposed fix

- Make incoming proposals and counter-offers soft-stop rather than true blockers
- Base expiry on turns visible, or auto-reject with a notification/log entry instead of silently dropping hidden proposals
- Add regression tests for hidden-expiry, stacked queue, and queue overflow behavior
- Preferred UX: queued soft-stop items should live in a visible diplomacy mailbox/desk with badge count, not in an invisible timeout queue

#### Files
1. `backend/game_logic/ai_diplomacy.py` — queue expiry, enqueue/dequeue, queued delivery
2. `backend/models/dialogue_manager.py` — stale clearing timing
3. `backend/models/world_state.py` — paired popup clearing at turn advance
4. `backend/game_logic/turn_manager.py` — when queued proposals are eligible to surface
5. `godot-client/project-sovereign/scripts/main.gd` / top-bar HUD — mailbox entry point and pending-count presentation
6. `tests/test_dialogue_manager.py` / new integration tests — hidden-expiry and stacked queue coverage

---

### PL-29: No new game / restart endpoint

**Priority:** P3 — QOL
**Source:** Playtest Session D (Apr 10, 2026)

#### Problem

No way to start a new game without killing and restarting the server. `/save` and `/load` exist but no `/new_game` or `/restart`. During playtesting: manual process kills + autosave deletion needed. Autosave persists defeated game state, so restarting sometimes loads the old game.

#### Proposed fix

- Add `POST /new_game` endpoint that reinitializes `WorldState`
- Optionally clear autosave on new game
- Godot: "New Game" button in pause menu

#### Files
1. `main.py` — add `/new_game` endpoint
2. `save_manager.py` — optional autosave clearing
3. `pause_menu.gd` — "New Game" button

---

## GPT Audit — Architecture Notes (Not Bugs)

The GPT audit (Apr 10, 2026) identified several architecture/scaling concerns. These are not bugs but inform future work. Full details in `docs/GPT_AUDIT_PLAN_RESULTS.md`.

| Finding | Category | Summary | Where It Lives |
|---------|----------|---------|---------------|
| Map renderer is prototype | Scaling | Circle-based 19-region renderer won't scale to 80-100 provinces | ROADMAP.md (art-blocked) |
| `/command` bypasses `build_base_response()` | Architecture | Main command path assembles response manually | ARCHITECTURE_REFACTORING_PLAN.md |
| AI uses omniscient queries | Scaling | `get_enemies_of_nation()` fine at 19 regions, unfair at 80+ | ARCHITECTURE_REFACTORING_PLAN.md |
| Hardcoded nation defaults | Scaling | Inline nation dicts in world_state.py won't scale | ARCHITECTURE_REFACTORING_PLAN.md |
| Diplomacy lacks rivalry pressure | Design | Alliance building too cheap, no forced choice | DESIGN_REFINEMENT.md (R160) |
| `main.gd` popup routing chain | Architecture | Real modal ordering in early-return chain, not registry | ARCHITECTURE_REFACTORING_PLAN.md |
| Remaining popup handlers still synthesize English commands | Architecture | Incoming proposal / sabotage / vassal / objection buttons still route through `send_command` | GPT_AUDIT_PLAN_RESULTS.md |
| Blocking taxonomy not enforced | Architecture | `executor.py` and `main.py` still treat any pending dialogue as a hard stop | GPT_AUDIT_PLAN_RESULTS.md |
| Historical audit docs stale | Docs | ARCHITECTURE_AUDIT_REPORT.md describes old state | Low priority cleanup |
