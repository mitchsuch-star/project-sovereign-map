# Reliability + Commitments - Implementation Plan

> **Spec:** `docs/RELIABILITY_COMMITMENTS_SPEC.md` (v0.9)
> **Created:** April 13, 2026
> **Sessions:** 8 named slices, ~7 effective on the critical path
> **Est. Tests:** ~140
> **Scope note:** `D1` remains a deferred follow-up, not part of the v0.1 commitments ship target.

---

## Slice A: Foundations

### A1. Data model + serialization

**Files:** `backend/models/world_state.py`, `docs/SAVE_FORMAT_REFERENCE.md`

- Add `betrayal_history: Dict[str, Dict]` to WorldState (directional key `from|to`, value: `{strikes: List[StrikeRecord], categories: Set[str], last_turn: int}`); each `StrikeRecord` is `{severity, turn, episode_id, decays_on_turn}` so episode-cap queries and severity-scaled decay can run off a single authoritative list
- Add `nation_rivalries: Dict[str, Dict]` to WorldState (diplo_key, value: `{intensity, source, weight, started_turn, last_changed_turn}`)
- Add `diplomatic_commitments: Dict[str, Dict]` to WorldState for `war_bargain` records
- Add `next_commitment_id: int` to WorldState
- Add root-cause `episode_id` plumbing for diplomatic consequence application (generated on root trigger; any pending dialogue or delayed decay state that may emit later consequences must serialize the originating lineage)
- Clarify `diplomatic_reliability` docstring as nation-keyed reputation
- Initialize 3 starting rivalries: France<->Britain `primary active`, Prussia<->Austria `primary active`, Prussia<->Saxony `secondary cold`
- Seed a generic `war_bloc` interface over the existing serialized `active_coalition` record shape with `target_nation`; do not add a second stored structure
- Add cached helpers for rivalry lookups, opposition-pair reads, live-bargain lookups, same-region contradiction checks, and fulfillment-reward gating by beneficiary
- Wire `to_dict()` / `from_dict()` with `.get()` defaults
- Update `SAVE_FORMAT_REFERENCE.md`
- Add a save-migration regression test using a real pre-commitments fixture save
- ~18 tests (serialization round-trip, starting state, episode-id plumbing, opposition graph helpers, contradiction index reads, migration load)

### A2. Ledger + preview scaffolding

**Files:** `backend/game_logic/diplomatic_ledger.py`, `backend/game_logic/diplomatic_dialogue.py`, `backend/main.py`, `backend/display_names.py`, `godot-client/project-sovereign/scripts/diplomatic_ledger.gd`, `godot-client/project-sovereign/scripts/proposal_confirm_popup.gd`, `godot-client/project-sovereign/scripts/main.gd`

- Add display-name maps for rivalry intensity, betrayal severity, bargain status, and warning categories before Slice C depends on them
- Add rivalry display to diplomatic ledger Nations tab
- Add reliability descriptor + bilateral betrayal warning to Talleyrand tab
- Add live bargain section (empty at first, ready for Slice C)
- Add canonical `warnings[]` / Political Context preview payload scaffolding
- Define warning severity ordinals and stable category ordering in one shared formatter contract
- Debug endpoint for rivalry / betrayal / bargain state inspection
- ~12 tests (ledger formatting, preview payload shape, display-name wiring, warning ordering)

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
- Record betrayal events on treaty break and bargain breach
- Tag French-engineered treaty auto-decay as constructive breach rather than void
- Dispatch entries for rivalry escalation, betrayal recorded, reliability change
- ~12 tests (anger calc, betrayal record creation, constructive-breach routing, dispatch entries)

### B2b. Witness scoping + episode cap + redemption + hard-reject

**Files:** `backend/models/world_state.py`, `backend/game_logic/diplomacy.py`, `backend/game_logic/dispatch.py`

- Witness penalty logic: only allies of victim, active rivals of betrayer, and directly implicated bargain/claim observers sharing the same named enemy or region
- Define and enforce episode boundaries by root-cause `episode_id`, not by whole `advance_turn()`
- Enforce per-episode victim strike cap of 2 across all consequences from that trigger
- Redemption tick in `advance_turn()`: +3 reliability per 5 honored turns, severity-scaled bilateral strike decay
- Strike age continues to mature during `WAR` / `ARMISTICE`; actual bilateral strike removal only occurs while a non-war treaty is restored
- Gate fulfilled-bargain reliability gain to once per beneficiary per 10 turns
- Hard-reject behavior: 3 victim-side strikes -> hard resist deep treaties except for the narrow shared-enemy survival exception
- Prussia<->Saxony hardcoded escalation: direct war or France vassalizes Saxony -> escalate to `active`
- ~20 tests (witness scoping, strike cap boundaries, multi-episode turn batching, cross-perpetrator single-victim episode cap, per-severity decay with mixed-severity strikes, redemption maturation, hard-reject posture, escalation triggers, fulfillment reward gating)

### B3. Commitment paradox

**Files:** `backend/commands/diplomatic_executor.py`, `backend/models/dialogue_manager.py`, `backend/models/cooldown_manager.py`, `backend/main.py`, `godot-client/project-sovereign/scripts/main.gd`, `godot-client/project-sovereign/scripts/alliance_paradox_popup.gd`, `godot-client/project-sovereign/scenes/alliance_paradox_popup.tscn`

- New `commitment_paradox` dialogue type in `HARD_STOP_TYPES`
- Paradox check at ratification: the ratifying nation may not hold `DEFENSIVE_ALLIANCE` / `ALLIANCE` with both sides of an active opposition pair (rule body written generically; v0.1 ratifier is always France)
- Read paradox input from shared opposition-pair helpers so later coalition target pairs can plug in without rewriting the flow
- Implement `ConflictResolutionPass` that collects all opposition-pair and legacy war-cross conflicts introduced by a single ratification, renders one consolidated resolution dialogue, re-evaluates after each chosen downgrade, and rejects the ratification if any conflict remains
- `commitment_paradox` preempts the old conflicting-alliance flow for same-ratification opposition-pair conflicts; the older flow remains only for later war-declaration or legacy conflicts not caught at ratification
- New handler methods in `diplomatic_executor.py`
- Reuse the existing paradox popup component if possible for the base rivalry-only paradox flow
- Register in dialog manager, popup queue, `build_base_response()`, and client popup routing
- Show deterministic downgrade fallout available before bargains exist (old treaty outcome, offended-rival hit when knowable)
- Defer attached bargain-breach / reliability fallout preview to Slice C once bargain data exists
- ~14 tests (trigger detection, popup passthrough, option routing, downgrade execution, base consequence preview, multi-conflict ratification consolidated pass, mixed opposition + legacy conflict single-dialogue resolution)

---

## Slice C: War Bargains

### C1a. Clause type + validation + creation

**Files:** `backend/models/world_state.py`, `backend/game_logic/diplomacy.py`, `backend/commands/diplomatic_executor.py`, `backend/display_names.py`, `backend/main.py`

- Add new `war_bargain` clause type
- User-facing wording: named-enemy alignment + French claim priority while backend key remains `war_bargain`
- Represent each bargain record as one object with linked `entry_term` + `claim_term`
- Support both AI-proposed and limited player-authored bargain construction
- Validate named enemy, claim region holder, French strategic interest, beneficiary participation feasibility, caps, cooldowns, and contradiction guards
- Add hard-stop preview for bargain creation when France must first downgrade an existing deep treaty; include total estimated pivot cost
- Commitment creation on ratification: create tracked record with `origin_mode`, `target_enemy`, `entry_term`, `claim_term`, `status`, `source_treaty`, `source_pair`, `cooldown_key`, `cooldown_until_turn`, `end_reason`, `fulfillment_snapshot`
- No `deadline_turn`, no `suspended_turns`, no timer warnings, and no bargain-only cancellation action
- This slice must land together with lifecycle hooks below; do not ship creation without transition handling
- ~18 tests (creation, validation, contradiction hard stops, hard-stop previews, metadata shape)

### C1b. Lifecycle: fulfillment + breach + void (same implementation session as C1a)

**Files:** `backend/models/world_state.py`, `backend/game_logic/diplomacy.py`, `backend/commands/diplomatic_executor.py`, `backend/game_logic/dispatch.py`, `backend/campaign_log.py`

- Status transitions: `active` -> `triggered` -> `fulfilled` / `void` / `breached`
- Add zombie-bargain void: 5 continuous turns of `PEACE`-or-higher between the promiser and the named enemy AND between the beneficiary and the named enemy, with no re-declaration, voids the bargain with no penalty and the standard 4-turn cooldown
- Fulfillment check in `advance_turn()`: bargain is `triggered`, France controls the claimed region from the named enemy while the bargain remains valid, source military treaty still stands, and beneficiary co-belligerence still holds through war resolution
- On fulfillment, write `fulfillment_snapshot` with claim region, beneficiary, target enemy, fulfilled turn, and reward deltas
- If the named war ends inconclusively while the source treaty and claim basis still stand, transition `triggered` back to `active`; do not leave it stuck live-occupied forever
- Breach detection: source treaty break, voluntary downgrade below `DEFENSIVE_ALLIANCE`, constructive breach via French-engineered auto-decay, contradictory alignment with named enemy / holder, contradictory bargain, later explicit French claim renunciation once peace hardening exists
- Void detection: beneficiary breaks first, non-French auto-decay, beneficiary enters `NON_AGGRESSION` or deeper with the named enemy first, beneficiary joins a coalition against France first, beneficiary refuses bargain-backed ally-entry request, claim basis disappears externally, third-party cascade creates contrary war
- Keep `fulfilled` terminal; do not retroactively reopen on later territory loss
- Apply 6-turn same pair + named enemy cooldown on breach
- Apply 4-turn same pair + named enemy cooldown on void
- Emit dispatch + campaign log events with required metadata
- ~26 tests (status transitions, same-turn downgrade exploit guard, constructive breach, inconclusive-war reactivation, void reasons, zombie-bargain void path, cooldowns, terminal fulfillment, fulfillment snapshot shape including `reward_capped` / `intended_reliability_delta`, metadata shape)

### C2. War-entry integration + surfaces + AI rules

**Files:** `backend/game_logic/diplomatic_templates.py`, `backend/commands/diplomatic_executor.py`, `backend/game_logic/diplomatic_dialogue.py`, `backend/game_logic/diplomatic_ledger.py`, `backend/campaign_log.py`, `backend/main.py`, `backend/models/dialogue_manager.py`, `godot-client/project-sovereign/scripts/diplomacy_wizard.gd`, `godot-client/project-sovereign/scripts/proposal_confirm_popup.gd`, `godot-client/project-sovereign/scripts/diplomatic_ledger.gd`, `godot-client/project-sovereign/scripts/campaign_log.gd`, `godot-client/project-sovereign/scripts/main.gd`

- Add visible structured bargain picker to the existing diplomacy wizard for eligible military treaties
- Add mandatory Bargain Review stage inside the existing proposal-confirm flow with exact beneficiary, named enemy, claim region, holder, source treaty, contradiction warnings, and total pivot-cost preview
- Add pre-war warning when France declares on the named enemy while a live bargain exists
- Replace offensive silent cascade with a surfaced `join_opportunity` / `AllyEntryPipeline` in declaration preview
- Offensive declaration preview must be transactional: no offensive war-state mutation commits until surfaced ally-entry / counter-bargain resolution finishes
- Add or reserve a later explicit in-war ally-entry request surface so temporarily blocked bargains do not strand
- Split war-entry handling into defensive honor calls, offensive ally requests, and coalition-overlap hard blocks
- Add `war_entry_counter_bargain` flow for military allies who did not bargain at alliance time but demand terms at the same-turn ally-entry decision for a specific war
- Render counter-bargains through the existing proposal-confirm popup with `counter_bargain_context`; do not add a second dialogue family for same-turn war entry
- In counter-bargain mode, suppress standard `proposal_confirm` affordances that leak envoy semantics: Renegotiate / counter-offer chain, envoy-in-transit status, DP cost display and DP spend, mailbox deferral, and dismiss / never-mind — only `Accept`, `Reject`, and `Back Out` remain terminal
- Counter-bargains use an immediate blocking confirm flow, not mailbox deferral
- Serialize the staged offensive declaration inside pending dialogue context as primitive `pending_declaration` payload keyed by `declaration_transaction_id`; do not rely on an ID with no restorable staged action
- Counter-bargains only apply to offensive ally requests; defensive honor calls auto-resolve as join after hard-block checks
- `Reject` on a counter-bargain continues the declaration / war action without that ally if otherwise legal; `Back Out` cancels the pending declaration preview transaction before war-state mutation
- Commitments-layer hard blocks override the old defensive-cascade armistice bypass where the two rules would conflict
- Enforce structural bargain caps instead of a global French bargain cap:
  - one live bargain per beneficiary + named enemy pair
  - one live bargain per claim region
  - one bargain generated from a single treaty package or ally-entry decision
- Add deterministic same-turn request memory so same ally + same enemy + same request type reuses the same ask unless one of the spec-listed material changes occurs:
  - France-beneficiary treaty depth
  - France-beneficiary relation
  - beneficiary war load
  - coalition / bloc status involving the beneficiary or named enemy
  - route-feasibility changes caused by beneficiary / named-enemy territorial, treaty, or war-state changes
  - bargain-region availability changes caused by beneficiary / named-enemy war resolution
- Add explicit hard-block reason surfacing (armistice, contrary war state, coalition conflict, no route, etc.)
- Add dedicated `war_entry_score` with explicit inputs, `50+` join threshold, `25-49` offensive counter-bargain band, and hard defensive-honor auto-join after block checks
- Absence of a surfaced `join_opportunity`, or a blocked request path, must not create breach by itself
- Apply explicit `+25` war-entry acceptance bonus when a valid bargain targets the named enemy
- Add current anti-France coalition overlap hooks:
  - `war_bloc.target_nation`-aware coalition membership can hard-block French ally-entry requests
  - joining a coalition against France voids contradictory French bargains
- Extend the paradox popup in this slice to surface attached bargain-breach / reliability fallout once bargain records exist
- Ledger: live bargains with named enemy, claim region, holder, status, and cooldown
- Campaign log event types: `bargain_ratified`, `bargain_triggered`, `bargain_fulfilled`, `bargain_breached`, `bargain_voided`
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
- ~36 tests (wizard review surface, pre-war warnings, AllyEntryPipeline routing, transactional declaration ordering, pending-declaration save/load resume, pending-declaration cancel/continue semantics, war-entry bonus, counter-bargain flow, AI gating, hard-block messaging, deterministic rerolls, unrelated-route non-rerolls, coalition-overlap voids, compact log rendering, rivalry-hit downgrade interaction, paradox-bargain preview integration, defensive-honor-vs-armistice arbitration, M5-vs-paradox arbitration, save/load reroll identity, save/load `origin_episode_id` persistence)

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
- Build on the seeded `target_nation` / opposition-graph seams from Slice A rather than adding a second coalition representation
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
A1 + B1 -> C1a -> C1b
C1b + B2b -> C2
C2 -> C3 (Commitments Presentation Pass) -> Bilateral Peace Hardening
```

`C3` is the commitments presentation pass (see `docs/COMMITMENTS_PRESENTATION_SPEC.md`). It lands after `C2` and before `Bilateral Peace Hardening`, and depends on the emit and contract additions filed against `C1b`, `C2`, and `B2a`/`B2b` below.

Recommended playtest gates:

- **After A2:** verify rivalry display plus empty betrayal / bargain scaffolding appear correctly in ledger / preview
- **After B2b:** verify anger fires on deepening, betrayal records correctly, episode cap holds at 2, and redemption pause / resume works
- **After B3:** verify the base commitment paradox popup fires and resolves correctly with rivalry-only downgrade fallout
- **After C1a:** partial bargain testing recommended - verify creation, validation, contradiction hard stops, and pivot-cost preview before UI wiring
- **After C2:** verify end-to-end bargain loop: author / accept -> review -> join opportunity -> war-entry bonus -> trigger -> fulfill / void / breach, and verify counter-bargain routing plus paradox-bargain preview integration
- **After C3:** verify commitments presentation pass routes spotlights, notices, ledger emphasis, and campaign-log events per `COMMITMENTS_PRESENTATION_SPEC.md`

Slice D stays deferred unless playtesting proves the narrowed commitments pass still lacks enough political texture or coalition overlap remains too muddy in play.

---

## C3 Cross-Cutting Contract Additions

These additions are filed against existing slices to unblock the `C3` commitments presentation pass. They do not add new slices; they tighten contracts the presentation layer reads.

### Against `B2a`

- Emit a `witness_strike_recorded` dispatch event as part of witness-scoped betrayal recording. Payload carries `episode_id`, `victim_nation`, `perpetrator_nation`, `witness_nation`, `scope_reason` (one of `ally` / `rival` / `shared_enemy` / `region_observer`), `relation_delta`, `reliability_delta`, `turn`. Distinct from the generic "betrayal recorded" dispatch entry.

### Against `B2b`

- Emit a `hard_reject_posture_triggered` dispatch event on the **first** threshold crossing per `(victim_nation, perpetrator_nation)` pair. Payload: `victim_nation`, `perpetrator_nation`, `trigger_strike_episode_id`, `turn`. Subsequent turns in the same posture do not re-emit; emission is first-cross-only.

### Against `C1b` (`fulfillment_snapshot` extension)

- Extend the `fulfillment_snapshot` contract with narrative-ready fields beyond the mechanical snapshot:
  - `witness_nations_at_fulfillment` — list of `{nation, scope_reason}` captured at the fulfillment instant
  - `relation_delta` — applied reward delta
  - `reliability_delta` — applied reward delta
- These fields feed `C3` spotlight templates directly and are also the source for `relation_delta` / `reliability_delta` in the `C3` surface payload.

### Against `C2` (`pending_declaration` enumeration)

The `pending_declaration` primitive payload keyed by `declaration_transaction_id` carries, at minimum:

- `declaration_transaction_id`
- `aggressor_nation`
- `target_nation`
- `pending_ally_invites` — list of `{nation, bargain_draft}`
- `staged_war_state_snapshot` — primitive, restorable staged action state
- `turn_created`

**Back Out semantics:** `Back Out` cancels the `pending_declaration` transaction, refunds DP and AP spent to stage the declaration, and is **not re-entrant within the same turn**. The rendering of Back Out is owned by `C3` (see `COMMITMENTS_PRESENTATION_SPEC.md` §12.4); the semantics are owned here.

**`hard_reject_posture_triggered` rendering dependency:** `C3` spotlight rendering consumes this first-time-threshold-crossing emit. `C3` is blocked on the emit contract above landing.

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
| C1b | C1a, B2b | Lifecycle uses betrayal recording, constructive-breach routing, fulfillment snapshots, and cooldown rules |
| C2 | C1b, B3 | Review / war-entry logic operates on commitments created by C1b and extends the existing paradox / popup routing |
| D1 | A1, B1, B2b, C1b | Deferred follow-up only |
| D2 | C2, D1 | Deferred coalition generalization should build on the finalized ally-entry / bargain overlap contract |
