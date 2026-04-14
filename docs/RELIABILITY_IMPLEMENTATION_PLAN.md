# Reliability + Commitments - Implementation Plan

> **Spec:** `docs/RELIABILITY_COMMITMENTS_SPEC.md` (v0.8)
> **Created:** April 13, 2026
> **Sessions:** 9 named slices, ~7 effective on the critical path
> **Est. Tests:** ~140
> **Scope note:** `D1` remains a deferred follow-up, not part of the v0.1 commitments ship target.

---

## Slice A: Foundations

### A1. Data model + serialization

**Files:** `backend/models/world_state.py`, `docs/SAVE_FORMAT_REFERENCE.md`

- Add `betrayal_history: Dict[str, Dict]` to WorldState (directional key `from|to`, value: `{strikes, categories, last_turn, decays_on_turn}`)
- Add `nation_rivalries: Dict[str, Dict]` to WorldState (diplo_key, value: `{intensity, source, weight, started_turn, last_changed_turn}`)
- Add `diplomatic_commitments: Dict[str, Dict]` to WorldState for `war_bargain` records
- Add `next_commitment_id: int` to WorldState
- Clarify `diplomatic_reliability` docstring as nation-keyed reputation
- Initialize 3 starting rivalries: France<->Britain `primary active`, Prussia<->Austria `primary active`, Prussia<->Saxony `secondary cold`
- Add cached helpers for rivalry lookups, live-bargain lookups, and same-region contradiction checks
- Wire `to_dict()` / `from_dict()` with `.get()` defaults
- Update `SAVE_FORMAT_REFERENCE.md`
- Add a save-migration regression test using a real pre-commitments fixture save
- ~15 tests (serialization round-trip, starting state, helper lookups, contradiction index reads, migration load)

### A2. Ledger + preview scaffolding

**Files:** `backend/game_logic/diplomatic_ledger.py`, `backend/game_logic/diplomatic_dialogue.py`, `backend/main.py`, `backend/display_names.py`, `godot-client/project-sovereign/scripts/diplomatic_ledger.gd`, `godot-client/project-sovereign/scripts/proposal_confirm_popup.gd`, `godot-client/project-sovereign/scripts/main.gd`

- Add display-name maps for rivalry intensity, betrayal severity, bargain status, and warning categories before Slice C depends on them
- Add rivalry display to diplomatic ledger Nations tab
- Add reliability descriptor + bilateral betrayal warning to Talleyrand tab
- Add live bargain section (empty at first, ready for Slice C)
- Add canonical `warnings[]` / Political Context preview payload scaffolding
- Debug endpoint for rivalry / betrayal / bargain state inspection
- ~10 tests (ledger formatting, preview payload shape, display-name wiring)

---

## Slice B: Rivalry Pressure

### B1. Acceptance formula modifiers

**Files:** `backend/game_logic/diplomacy.py`, `backend/display_names.py`

- Add exact numeric values for `direct_rivalry_mod`, `rival_conflict_mod`, `bilateral_betrayal_mod`, and treaty-time `bargain_value_mod`
- Add `direct_rivalry_mod` to `calculate_acceptance()` with primary vs secondary weighting
- Add `rival_conflict_mod` for existing rival alignment and live-bargain conflict
- Add `bilateral_betrayal_mod` using `betrayal_history`
- Add `bargain_value_mod` for valid `war_bargain` clauses
- Group all under `political_commitment_mod`
- Cap `political_commitment_mod` floor at `-40`
- Preserve old static sweeteners only when a tracked `war_bargain` clause is not present
- Wire debug breakdown output and acceptance feedback strings
- Add regression tests that compare representative pre-change proposal scores against expected tolerance bands
- ~24 tests (primary vs secondary values, capped stacking, bargain replacement rule, edge cases, regression coverage)

### B2a. Third-party anger + betrayal recording

**Files:** `backend/models/world_state.py`, `backend/game_logic/diplomacy.py`, `backend/game_logic/dispatch.py`

- On treaty ratification: compute rival anger and apply relation penalties per spec, including explicit `VASSAL` anger
- Apply `they_chose_us = +8` on ratified side-taking events
- Record betrayal events on treaty break and bargain breach
- Tag French-engineered treaty auto-decay as constructive breach rather than void
- Dispatch entries for rivalry escalation, betrayal recorded, reliability change
- ~14 tests (anger calc, they_chose_us, betrayal record creation, constructive-breach routing, dispatch entries)

### B2b. Witness scoping + episode cap + redemption + hard-reject

**Files:** `backend/models/world_state.py`, `backend/game_logic/diplomacy.py`, `backend/game_logic/dispatch.py`

- Witness penalty logic: only allies of victim, active rivals of betrayer, and directly implicated bargain/claim observers sharing the same named enemy or region
- Define and enforce episode boundaries across one player command or one `advance_turn()` processing step
- Enforce per-episode victim strike cap of 2 across all consequences from that trigger
- Redemption tick in `advance_turn()`: +3 reliability per 5 honored turns, severity-scaled bilateral strike decay
- Pause bilateral strike decay during `WAR` / `ARMISTICE`, resume on restored non-war treaty
- Hard-reject behavior: 3 victim-side strikes -> hard resist deep treaties except for the narrow shared-enemy survival exception
- Prussia<->Saxony hardcoded escalation: direct war or France vassalizes Saxony -> escalate to `active`
- ~14 tests (witness scoping, strike cap boundaries, redemption pause/resume, hard-reject posture, escalation triggers)

### B3. Commitment paradox

**Files:** `backend/commands/diplomatic_executor.py`, `backend/models/dialogue_manager.py`, `backend/models/cooldown_manager.py`, `backend/main.py`, `godot-client/project-sovereign/scripts/main.gd`, `godot-client/project-sovereign/scripts/alliance_paradox_popup.gd`, `godot-client/project-sovereign/scenes/alliance_paradox_popup.tscn`

- New `commitment_paradox` dialogue type in `HARD_STOP_TYPES`
- Paradox check at ratification: new `DEFENSIVE_ALLIANCE` / `ALLIANCE` may not span both sides of active rival pair
- New handler methods in `diplomatic_executor.py`
- Reuse the existing paradox popup component if possible for the base rivalry-only paradox flow
- Register in dialog manager, popup queue, `build_base_response()`, and client popup routing
- Show deterministic downgrade fallout available before bargains exist (old treaty outcome, offended-rival hit when knowable)
- Defer attached bargain-breach / reliability fallout preview to Slice C once bargain data exists
- ~12 tests (trigger detection, popup passthrough, option routing, downgrade execution, base consequence preview)

---

## Slice C: War Bargains

### C1a. Clause type + validation + creation

**Files:** `backend/models/world_state.py`, `backend/game_logic/diplomacy.py`, `backend/commands/diplomatic_executor.py`, `backend/display_names.py`, `backend/main.py`

- Add new `war_bargain` clause type
- User-facing wording: named-enemy alignment + French claim priority while backend key remains `war_bargain`
- Support both AI-proposed and limited player-authored bargain construction
- Validate named enemy, claim region holder, French strategic interest, beneficiary participation feasibility, caps, cooldowns, and contradiction guards
- Add hard-stop preview for bargain creation when France must first downgrade an existing deep treaty; include total estimated pivot cost
- Commitment creation on ratification: create tracked record with `target_enemy`, `claim_region`, `claim_holder`, `status`, `source_treaty`, `source_pair`, `cooldown_until_turn`
- No `deadline_turn`, no `suspended_turns`, no timer warnings
- ~16 tests (creation, validation, contradiction hard stops, hard-stop previews, metadata shape)

### C1b. Lifecycle: fulfillment + breach + void + cancellation

**Files:** `backend/models/world_state.py`, `backend/game_logic/diplomacy.py`, `backend/commands/diplomatic_executor.py`, `backend/game_logic/dispatch.py`, `backend/campaign_log.py`

- Status transitions: `active` -> `triggered` -> `fulfilled` / `void` / `breached` / `cancelled`
- Fulfillment check in `advance_turn()`: bargain is `triggered`, France controls the claimed region from the named enemy while the bargain remains valid, source military treaty still stands, and beneficiary co-belligerence still holds through war resolution
- Breach detection: source treaty break, voluntary downgrade below `DEFENSIVE_ALLIANCE`, constructive breach via French-engineered auto-decay, contradictory alignment with named enemy / holder, contradictory bargain, intentionally withholding an eligible beneficiary's ally-entry opportunity once no hard block exists
- Void detection: beneficiary breaks first, non-French auto-decay, beneficiary enters `NON_AGGRESSION` or deeper with the named enemy first, beneficiary joins a coalition against France first, beneficiary refuses bargain-backed ally-entry request, beneficiary fails a non-blocked defensive honor call, claim basis disappears externally, third-party cascade creates contrary war
- Keep `fulfilled` terminal; do not retroactively reopen on later territory loss
- Cancellation flow state + same pair / same enemy cooldown
- Apply beneficiary-refusal void cooldown for same pair + same enemy
- Emit dispatch + campaign log events with required metadata
- ~18 tests (status transitions, same-turn downgrade exploit guard, constructive breach, void reasons, cooldowns, terminal fulfillment, metadata shape)

### C2. War-entry integration + surfaces + AI rules

**Files:** `backend/game_logic/diplomatic_templates.py`, `backend/commands/diplomatic_executor.py`, `backend/game_logic/diplomatic_dialogue.py`, `backend/game_logic/diplomatic_ledger.py`, `backend/campaign_log.py`, `backend/main.py`, `backend/models/dialogue_manager.py`, `godot-client/project-sovereign/scripts/diplomacy_wizard.gd`, `godot-client/project-sovereign/scripts/proposal_confirm_popup.gd`, `godot-client/project-sovereign/scripts/diplomatic_ledger.gd`, `godot-client/project-sovereign/scripts/campaign_log.gd`, `godot-client/project-sovereign/scripts/main.gd`

- Add visible structured bargain picker to the existing diplomacy wizard for eligible military treaties
- Add mandatory Bargain Review stage inside the existing proposal-confirm flow with exact beneficiary, named enemy, claim region, holder, source treaty, contradiction warnings, and total pivot-cost preview
- Add pre-war warning when France declares on the named enemy while a live bargain exists
- Replace offensive silent cascade with a player-visible ally-entry evaluation in declaration preview
- Add or reserve a later explicit in-war ally-entry request surface so temporarily blocked bargains do not strand
- Split war-entry handling into defensive honor calls, offensive ally requests, and coalition-overlap hard blocks
- Add `war_entry_counter_bargain` flow for military allies who did not bargain at alliance time but demand terms at the same-turn ally-entry decision for a specific war
- Add dedicated `war_entry_counter_bargain` dialogue type to `HARD_STOP_TYPES`, but render it through the existing proposal-confirm popup component by extending `PROPOSAL_CONFIRM_DIALOGUE_TYPES`
- Counter-bargains use an immediate blocking confirm flow, not mailbox deferral
- Counter-bargains only apply to offensive ally requests; defensive honor calls do not bargain
- Enforce structural bargain caps instead of a global French bargain cap:
  - one live bargain per beneficiary + named enemy pair
  - one live bargain per claim region
  - one bargain generated from a single treaty package or ally-entry decision
- Add deterministic same-turn request memory so same ally + same enemy + same request type reuses the same ask unless a material state change occurs
- Add explicit hard-block reason surfacing (armistice, contrary war state, coalition conflict, no route, etc.)
- Add dedicated `war_entry_score` with explicit inputs, `50+` join threshold, `25-49` offensive counter-bargain band, and defensive-duty floor
- Add hard breach route if France intentionally withholds an eligible bargain beneficiary's ally-entry opportunity once no hard block exists
- Apply explicit `+25` war-entry acceptance bonus when a valid bargain targets the named enemy
- Add current anti-France coalition overlap hooks:
  - coalition membership can hard-block French ally-entry requests
  - joining a coalition against France voids contradictory French bargains
- Extend the paradox popup in this slice to surface attached bargain-breach / reliability fallout once bargain records exist
- Ledger: live bargains with named enemy, claim region, holder, status, and cooldown
- Campaign log event types: `bargain_ratified`, `bargain_triggered`, `bargain_fulfilled`, `bargain_breached`, `bargain_voided`, `bargain_cancelled`
- Campaign log stores full bargain metadata but renders compact one-line summaries
- AI bargain generation stub with feasibility gates:
  - current rival or current war enemy only
  - claim region held by that enemy or subject
  - beneficiary has plausible participation access
  - beneficiary has at least one active marshal and either front access or >=25% of France's active field strength
  - there is room under the pair + enemy and same-region structural caps
  - no same-region contradiction
  - no same pair / same enemy cooldown
- AI anti-spam rules: no repeated bargain offers while one is live or cooling down
- Counter-bargain timing: score `50+` joins for free, `25-49` may counter-bargain, `<25` refuses
- Use existing downgrade / auto-downgrade behavior as the normal fallout path when rivalry anger drives relation collapse; do not add forced instant-break logic as part of the bargain slice
- ~24 tests (wizard review surface, pre-war warnings, war-entry bonus, ally-entry breach, counter-bargain hard-stop flow, AI gating, hard-block messaging, deterministic rerolls, coalition-overlap voids, compact log rendering, rivalry-hit downgrade interaction, paradox-bargain preview integration)

---

## Slice D: Deferred Follow-up

### D1. Advisory-first strategic focus + deeper AI integration

**Files:** `ai_diplomacy.py`, `enemy_ai.py`

- Strategic-focus layer for AI phrasing + Talleyrand recommendations
- Dynamic power scoring and tiers
- Richer rival-aware agenda logic
- Smarter bargain planning beyond the v0.1 feasibility filters
- Performance: no new per-region scans, use cached rivalry and bargain lookups
- Not counted in the v0.1 commitments session budget

### D2. Coalition buildout and generalization

**Files:** `backend/game_logic/coalition.py`, `backend/game_logic/diplomacy.py`, `backend/game_logic/ai_diplomacy.py`, `backend/ai/enemy_ai.py`, `backend/game_logic/war_status.py`, relevant ledger / popup / log surfaces

- Lift current anti-France coalition assumptions into generic coalition identity / target tracking
- Define coalition-vs-alliance overlap hooks for powers other than France
- Keep coalition loyalty / separate-peace logic distinct from treaty acceptance and bargain sweetening
- Revisit war-entry scoring once generalized coalition targets exist
- Not counted in the v0.1 commitments session budget

---

## Execution Order

```text
A1 -> A2
A1 -> B1
A1 -> B2a -> B2b
A1 + A2 -> B3
A1 + B1 -> C1a
C1a + B2b -> C1b -> C2
```

Recommended playtest gates:

- **After A2:** verify rivalry display plus empty betrayal / bargain scaffolding appear correctly in ledger / preview
- **After B2b:** verify anger fires on deepening, betrayal records correctly, episode cap holds at 2, and redemption pause / resume works
- **After B3:** verify the base commitment paradox popup fires and resolves correctly with rivalry-only downgrade fallout
- **After C1a:** partial bargain testing recommended - verify creation, validation, contradiction hard stops, and pivot-cost preview before UI wiring
- **After C2:** verify end-to-end bargain loop: author / accept -> review -> war-entry bonus -> trigger -> fulfill / void / breach / cancel, and verify counter-bargain hard-stop routing plus paradox-bargain preview integration

Slice D stays deferred unless playtesting proves the narrowed commitments pass still lacks enough political texture or coalition overlap remains too muddy in play.

---

## Key Dependencies

| Session | Depends On | Why |
|---------|-----------|-----|
| A2 | A1 | Ledger reads new data fields |
| B1 | A1 | Acceptance reads rivalry + betrayal + bargain stores |
| B2a | A1 | Anger / betrayal writes new stores and dispatch events |
| B2b | B2a | Episode cap, witness scoping, decay, and hard-reject extend betrayal records |
| B3 | A1, A2 | Paradox checks rivalry data + treaty depth and needs routed popup plumbing |
| C1a | A1, B1 | Bargain creation needs data model, contradiction helpers, and acceptance-facing values |
| C1b | C1a, B2b | Lifecycle uses betrayal recording, constructive-breach routing, and cooldown rules |
| C2 | C1b, B3 | Review / war-entry logic operates on commitments created by C1b and extends the existing paradox / popup routing |
| D1 | A1, B1, B2b, C1b | Deferred follow-up only |
| D2 | C2, D1 | Deferred coalition generalization should build on the finalized ally-entry / bargain overlap contract |
