# Reliability + Commitments - Implementation Plan

> **Spec:** `docs/RELIABILITY_COMMITMENTS_SPEC.md` (v0.7)
> **Created:** April 13, 2026
> **Sessions:** 7 (A1-A2, B1-B3, C1-C2)
> **Est. Tests:** ~120
> **Scope note:** `D1` remains a deferred follow-up, not part of the v0.1 commitments ship target.

---

## Slice A: Foundations

### A1. Data model + serialization

**Files:** `world_state.py`, `SAVE_FORMAT_REFERENCE.md`

- Add `betrayal_history: Dict[str, Dict]` to WorldState (directional key `from|to`, value: `{strikes, categories, last_turn, decays_on_turn}`)
- Add `nation_rivalries: Dict[str, Dict]` to WorldState (diplo_key, value: `{intensity, source, weight, started_turn, last_changed_turn}`)
- Add `diplomatic_commitments: Dict[str, Dict]` to WorldState for `war_bargain` records
- Add `next_commitment_id: int` to WorldState
- Clarify `diplomatic_reliability` docstring as nation-keyed reputation
- Initialize 3 starting rivalries: France<->Britain `primary active`, Prussia<->Austria `primary active`, Prussia<->Saxony `secondary cold`
- Add cached helpers for rivalry lookups, active bargain lookups, and same-region contradiction checks
- Wire `to_dict()` / `from_dict()` with `.get()` defaults
- Update `SAVE_FORMAT_REFERENCE.md`
- ~14 tests (serialization round-trip, starting state, helper lookups, contradiction index reads)

### A2. Ledger + preview scaffolding

**Files:** `diplomatic_ledger.py`, `diplomatic_dialogue.py`, `main.py`, `proposal_confirm_popup.gd`

- Add rivalry display to diplomatic ledger Nations tab
- Add reliability descriptor + bilateral betrayal warning to Talleyrand tab
- Add active bargain section (empty at first, ready for Slice C)
- Add canonical `warnings[]` / Political Context preview payload scaffolding
- Debug endpoint for rivalry / betrayal / bargain state inspection
- ~8 tests (ledger formatting, preview payload shape)

---

## Slice B: Rivalry Pressure

### B1. Acceptance formula modifiers

**Files:** `diplomacy.py`

- Add `direct_rivalry_mod` to `calculate_acceptance()` with primary vs secondary weighting
- Add `rival_conflict_mod` for existing rival alignment and active bargain conflict
- Add `bilateral_betrayal_mod` using `betrayal_history`
- Add `bargain_value_mod` for valid `war_bargain` clauses
- Group all under `political_commitment_mod`
- Cap `political_commitment_mod` floor at `-40`
- Preserve old static sweeteners only when a tracked `war_bargain` clause is not present
- Wire debug breakdown output
- ~20 tests (primary vs secondary values, capped stacking, bargain replacement rule, edge cases)

### B2. Third-party anger + betrayal recording

**Files:** `world_state.py`, `diplomacy.py`, `dispatch.py`

- On treaty ratification: compute rival anger and apply relation penalties per spec
- Apply `they_chose_us = +8` on ratified side-taking events
- Record betrayal events on treaty break and bargain breach
- Witness penalty logic: only allies of victim, active rivals of betrayer, and directly implicated bargain/claim observers
- Enforce per-episode victim strike cap of 2
- Redemption tick in `advance_turn()`: +3 reliability per 5 honored turns, severity-scaled bilateral strike decay
- Hard-reject behavior: 3 victim-side strikes -> hard resist deep treaties
- Prussia<->Saxony hardcoded escalation: direct war or France vassalizes Saxony -> escalate to `active`
- Dispatch entries for rivalry escalation, betrayal recorded, reliability change
- ~24 tests (anger calc, they_chose_us, strike cap, witness scoping, hard-reject posture, redemption, escalation triggers)

### B3. Commitment paradox

**Files:** `diplomatic_executor.py`, `dialogue_manager.py`, Godot popup files

- New `commitment_paradox` dialogue type in `HARD_STOP_TYPES`
- Paradox check at ratification: new `DEFENSIVE_ALLIANCE` / `ALLIANCE` may not span both sides of active rival pair
- New handler methods in `diplomatic_executor.py`
- New `commitment_paradox_popup.gd` + `.tscn`
- Register in dialog manager and client popup routing
- ~10 tests (trigger detection, option routing, downgrade execution)

---

## Slice C: War Bargains

### C1. Clause type + validation + lifecycle

**Files:** `world_state.py`, `diplomacy.py`, `diplomatic_executor.py`, `display_names.py`, `dispatch.py`

- Add new `war_bargain` clause type
- User-facing wording: named-enemy alignment + French claim priority while backend key remains `war_bargain`
- Support both AI-proposed and limited player-authored bargain construction
- Validate named enemy, claim region holder, French strategic interest, beneficiary participation feasibility, caps, cooldowns, and contradiction guards
- Commitment creation on ratification: create tracked record with `target_enemy`, `claim_region`, `claim_holder`, `status`, `source_treaty`, `source_pair`, `cooldown_until_turn`
- Status transitions: `active` -> `triggered` -> `fulfilled` / `void` / `breached` / `cancelled`
- No `deadline_turn`, no `suspended_turns`, no timer warnings
- Fulfillment check in `advance_turn()`: France controls claimed region from named enemy while bargain still valid and source military treaty still stands
- Breach detection: source treaty break, voluntary downgrade below `DEFENSIVE_ALLIANCE`, contradictory alignment with named enemy / holder, contradictory bargain, declaring on named enemy without calling eligible beneficiary
- Void detection: beneficiary breaks first, source treaty auto-decays without explicit French downgrade, beneficiary allies named enemy first, beneficiary refuses bargain-backed call, claim basis disappears externally, third-party cascade creates contrary war
- Cancellation flow state + same pair / same enemy cooldown
- Emit dispatch + campaign log events with required metadata
- ~30 tests (creation, validation, contradiction hard stops, status transitions, same-turn downgrade exploit guard, auto-decay and cascade voids, cooldowns, metadata shape)

### C2. War-entry integration + surfaces + AI rules

**Files:** `diplomatic_templates.py`, `diplomatic_executor.py`, `diplomacy_wizard.gd`, `proposal_confirm_popup.gd`, `diplomatic_ledger.py`, `campaign_log.py`, war-declaration / call-to-arms files

- Add visible structured bargain picker to the existing diplomacy wizard for eligible military treaties
- Add mandatory Bargain Review stage with exact beneficiary, named enemy, claim region, holder, source treaty, and contradiction warnings
- Add pre-war warning when France declares on the named enemy while a live bargain exists
- Add hard breach route if France intentionally skips calling an eligible bargain beneficiary
- Apply major war-entry acceptance bonus when a valid bargain targets the named enemy
- Ledger: active bargains with named enemy, claim region, holder, status, and cooldown
- Campaign log event types: `bargain_ratified`, `bargain_triggered`, `bargain_fulfilled`, `bargain_breached`, `bargain_voided`, `bargain_cancelled`
- AI bargain generation stub with feasibility gates:
  - current rival or current war enemy only
  - claim region held by that enemy or subject
  - beneficiary has plausible participation access
  - France below bargain cap
  - no same-region contradiction
  - no same pair / same enemy cooldown
- AI anti-spam rules: no repeated bargain offers while one is active or cooling down
- ~14 tests (wizard review surface, pre-war warnings, war-entry bonus, eligible-call breach, AI gating, anti-spam behavior)

---

## Slice D: AI Integration (deferred follow-up only)

### D1. Advisory-first strategic focus + deeper AI integration

**Files:** `ai_diplomacy.py`, `enemy_ai.py`

- Strategic-focus layer for AI phrasing + Talleyrand recommendations
- Dynamic power scoring and tiers
- Richer rival-aware agenda logic
- Smarter bargain planning beyond the v0.1 feasibility filters
- Performance: no new per-region scans, use cached rivalry and bargain lookups
- Not counted in the v0.1 commitments session budget

---

## Execution Order

```text
A1 -> A2 -> B1 -> B2 -> B3 -> C1 -> C2
```

Recommended playtest gates:

- **After A2:** verify rivalries and betrayal context appear correctly in ledger / preview
- **After B2:** verify rivalry pressure affects acceptance, anger fires on deepening, betrayal records cap correctly
- **After B3:** verify commitment paradox popup fires and resolves correctly
- **After C2:** verify end-to-end bargain loop: author / accept -> review -> war-entry bonus -> trigger -> fulfill / void / breach / cancel

Slice D stays deferred unless playtesting proves the narrowed commitments pass still lacks enough political texture.

---

## Key Dependencies

| Session | Depends On | Why |
|---------|-----------|-----|
| A2 | A1 | Ledger reads new data fields |
| B1 | A1 | Acceptance reads rivalry + betrayal + bargain stores |
| B2 | A1, B1 | Anger writes to stores that B1 reads; betrayal feeds acceptance |
| B3 | A1, B1 | Paradox checks rivalry data + treaty depth |
| C1 | A1, B1, B2 | Bargains use betrayal recording, rivalry checks, and contradiction helpers |
| C2 | C1 | Review / war-entry logic operates on commitments created by C1 |
| D1 | A1, B1, B2, C1 | Deferred follow-up only |
