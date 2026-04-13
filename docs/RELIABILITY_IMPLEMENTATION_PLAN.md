# Reliability + Commitments — Implementation Plan

> **Spec:** `docs/RELIABILITY_COMMITMENTS_SPEC.md` (v0.6)
> **Created:** April 13, 2026
> **Sessions:** 7 (A1-A2, B1-B3, C1-C2)
> **Est. Tests:** ~110
> **Scope note:** `D1` remains a deferred follow-up, not part of the v0.1 commitments ship target.

---

## Slice A: Foundations

### A1. Data model + serialization

**Files:** `world_state.py`, `SAVE_FORMAT_REFERENCE.md`

- Add `betrayal_history: Dict[str, Dict]` to WorldState (directional key `from|to`, value: `{strikes, categories, last_turn, decays_on_turn}`)
- Add `nation_rivalries: Dict[str, Dict]` to WorldState (diplo_key, value: `{intensity, source, started_turn, last_changed_turn}`)
- Add `diplomatic_commitments: Dict[str, Dict]` to WorldState (commitment id key, tracked promise record)
- Add `next_commitment_id: int` to WorldState
- Clarify `diplomatic_reliability` docstring as nation-keyed reputation (not pair-keyed)
- Initialize 3 starting rivalries: France<->Britain `active`, Prussia<->Austria `active`, Prussia<->Saxony `cold`
- Add cached `get_rivalries_for_nation()` and `get_rival_pairs()` helpers
- Wire `to_dict()` / `from_dict()` with `.get()` defaults
- Update `SAVE_FORMAT_REFERENCE.md`
- ~12 tests (serialization round-trip, helper lookups, starting state)

### A2. Ledger + preview surfacing groundwork

**Files:** `diplomatic_ledger.py`, `diplomatic_dialogue.py`, `main.py`, `proposal_confirm_popup.gd`

- Add rivalry display to diplomatic ledger Nations tab
- Add reliability descriptor + bilateral betrayal warning to Talleyrand tab
- Add active commitments section (empty for now, ready for Slice C)
- Add canonical `warnings[]` / Political Context preview payload scaffolding so commitment warnings have a stable surface before promise logic lands
- Debug endpoint for rivalry/betrayal state inspection
- ~8 tests (ledger formatting, preview payload shape)

---

## Slice B: Rivalry Pressure

### B1. Acceptance formula modifiers

**Files:** `diplomacy.py`

- Add `direct_rivalry_mod` to `calculate_acceptance()` - negative for deeper treaties with direct rivals
- Add `rival_conflict_mod` - negative when target knows France is aligned with its rival
- Add `bilateral_betrayal_mod` - reads `betrayal_history`, ~2x weight of global reliability
- Add `promise_value_mod` for tracked territorial promises
- Group all under `political_commitment_mod` composite in formula breakdown
- Cap `political_commitment_mod` floor at `-40` so the composite cannot hard-lock diplomacy by itself
- Wire debug breakdown output
- ~18 tests (acceptance with/without rivalry, cold vs active constants, capped stacking, edge cases)

### B2. Third-party anger + betrayal recording

**Files:** `world_state.py`, `diplomacy.py`, `dispatch.py`

- On treaty ratification (`_ratify_treaty`): compute rival anger, apply relation penalties per spec $7.4B table
- Do **not** apply great-power bloc anger in v0.1
- Apply `they_chose_us` relation bonus to the side France visibly backed
- Record betrayal events on treaty break - victim gets strikes, witnesses get scoped penalties
- Witness penalty logic: only allies of victim + nations with active rivalry against betrayer; witnesses do not get victim-grade strikes
- Redemption tick in `advance_turn()`: +3 reliability per 5 honored turns, severity-scaled bilateral strike decay with alliance-break decay capped at 10 turns and active-sabotage at 12
- Hard-reject behavior: 3 victim-side strikes -> hard resist deep treaties (exception paths still allowed)
- Prussia<->Saxony hardcoded escalation: direct war or France vassalizes Saxony -> escalate to `active`
- Dispatch entries for: rivalry escalation, betrayal recorded, reliability change
- ~22 tests (anger calc, they_chose_us, betrayal recording, witness scoping, hard-reject posture, redemption, escalation triggers)

### B3. Commitment paradox

**Files:** `diplomatic_executor.py`, `dialogue_manager.py`, + Godot popup files

- New `commitment_paradox` dialogue type in `HARD_STOP_TYPES` (priority 1, between alliance_paradox at 0 and others)
- Paradox check at ratification: if new DEFENSIVE_ALLIANCE/ALLIANCE would span both sides of active rival pair
- New handler methods in `diplomatic_executor.py` (sibling pattern to existing `alliance_paradox` at lines 2630-2671)
- New `commitment_paradox_popup.gd` + `.tscn` (CanvasLayer 101-118 range, 2 options: reject new treaty / downgrade existing alignment)
- Register in `dialog_manager.gd` via `dialog_manager.register()`, add to `main.gd` dtype whitelist (line ~697)
- ~10 tests (trigger detection, option routing, downgrade execution)

---

## Slice C: Territorial Promises

### C1. Clause type + lifecycle

**Files:** `world_state.py`, `diplomacy.py`, `diplomatic_executor.py`, `display_names.py`, `dispatch.py`

- New `territorial_promise` clause type - wire into 4 state maps in `diplomatic_executor.py`, `display_names.py`, keywords, harshness/acceptance
- User-facing wording: "support claim" / "settlement guarantee" strings while backend key remains `territorial_promise`
- Commitment creation on ratification: create tracked record with `deadline_turn`, `suspended_turns`, status, **single region**, beneficiary
- Fulfillment check in `advance_turn()`: evaluate after treaty/war resolution using the final state for the turn; beneficiary controls region + France still holds DEFENSIVE_ALLIANCE/ALLIANCE in that final state
- Failure detection: deadline expiry, source treaty break (immediate + stacks with treaty-break penalties), direct voluntary rival-backing, French vassalization / self-keeping of promised target
- Penalty/reward application: fulfillment (+4 reliability, relation bonus), passive failure (-15 relation, +1 strike, -6 reliability), active sabotage uses stronger penalties
- `promise_value_mod` acceptance modifier - replaces `SPECIAL_BONUSES` when tracked `territorial_promise` clause present (no double-counting)
- Urgency warnings in dispatch at 50% / 75% / 3-turns-remaining of effective deadline
- Suspension logic: France-caused direct war = immediate failure, beneficiary-caused direct war = void with no French penalty, only unattributed edge cases increment `suspended_turns`; no free 5-turn auto-void
- Source treaty interaction: France breaks source treaty = immediate promise failure; beneficiary breaks = void no penalty; natural downgrade = promise survives
- Emit one-time dispatch updates for promise suspension / resumption
- ~26 tests (creation, fulfillment, passive vs active failure, narrowed suspension, deadline math, warning timing, source treaty interactions)

### C2. Renegotiation + AI stub + surfaces

**Files:** `diplomatic_templates.py`, `diplomatic_executor.py`, `diplomacy_wizard.gd`, `proposal_confirm_popup.gd`, `diplomatic_ledger.py`, `campaign_log.py`, `display_names.py`

- Add visible `Renegotiate Promise` action to the existing nation-scoped diplomacy flow when the selected nation is beneficiary to an active French promise
- HARD_STOP dialogue flow: two branches (deadline extension / cancel with light penalty at -5 relation, -3 reliability, no strike)
- AI refusal path if beneficiary rejects a deadline extension
- Promise review stage in the wizard / proposal preview with exact region, deadline, source treaty, and likely political loser
- Canonical `warnings[]` / Political Context surfacing for promise review, with urgency warnings capped at 1 per turn per promise and 2 per dispatch page
- Warning text must include the exact visible action path for renegotiation; a terminal alias is optional follow-up, not required scope
- Minimal AI promise generation stub in `generate_suggested_terms()` stage 2 - gated on `covets_regions` matching region controlled by France or by that nation's rival, plus a current-holder / current-ally filter so AI does not propose obvious nonsense promises
- Ledger: active commitments with deadline, status, fulfillment progress in Treaties or Talleyrand tab
- Campaign log event types: `promise_fulfilled`, `promise_broken`, `promise_renegotiated` in `CAMPAIGN_LOG_TYPES` + `format_event_oneliner()`
- `_DEFIANCE_DISPLAY` + `_OBJECTION_DISPLAY` entries in `campaign_log.py` if applicable
- ~18 tests (renegotiation flow, AI stub generation, capped warnings, review surface, ledger output)

---

## Slice D: AI Integration (deferred follow-up only)

### D1. Advisory-first strategic focus + deeper AI integration

**Files:** `ai_diplomacy.py`, `enemy_ai.py`

- Strategic-focus layer for AI phrasing + Talleyrand recommendations: major powers expose concern/counterweight, minors expose feared rival/protector
- Great-power advisory logic should treat peer blocs as soft camps, not hard ally slots; no numeric cap, but deeper rival-camp alignment should visibly raise warning weight
- Derive `nation_power_scores` / `nation_power_tiers` from controlled regions, army strength, manpower depth, and vassal weight with hysteresis
- AI proposal generation considers rivalries: exclusivity offers ("ally us, not our rival"), promise-based courtship
- AI escalation behavior: repeated rival-camp alignment -> downgrade treaties, hostility pivot
- Optional later: general dynamic rivalry formation system (beyond Prussia-Saxony hardcoded triggers from B2)
- Performance: no new per-region scans, use cached rivalry lookups
- Not counted in the v0.1 commitments session budget

---

## Execution Order

```
A1 -> A2 -> B1 -> B2 -> B3 -> C1 -> C2
```

Each session is self-contained and testable independently. Recommended playtest gates:

- **After A2:** Verify rivalries appear in ledger, starting state is correct
- **After B2:** Verify rivalry pressure affects acceptance, anger fires on treaty deepening, betrayal records
- **After B3:** Verify commitment paradox popup fires and resolves correctly
- **After C2:** Full territorial promise loop testable end-to-end with AI stub and visible renegotiation/warning surfaces

Slice D stays deferred unless playtesting proves the narrowed commitments pass still lacks political texture.

---

## Key Dependencies

| Session | Depends On | Why |
|---------|-----------|-----|
| A2 | A1 | Ledger reads new data fields |
| B1 | A1 | Acceptance reads rivalry + betrayal stores |
| B2 | A1, B1 | Anger writes to stores that B1 reads; betrayal feeds acceptance |
| B3 | A1, B1 | Paradox checks rivalry data + acceptance context |
| C1 | A1, B1, B2 | Promise lifecycle uses betrayal recording + acceptance modifiers |
| C2 | C1 | Renegotiation operates on commitments created by C1 |
| D1 | A1, B1, B2, C1 | Deferred follow-up only; AI reads new stores after the core loop ships |
