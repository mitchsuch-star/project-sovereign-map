# Reliability + Commitments — Implementation Plan

> **Spec:** `docs/RELIABILITY_COMMITMENTS_SPEC.md` (v0.5)
> **Created:** April 13, 2026
> **Sessions:** 8 (A1-A2, B1-B3, C1-C2, D1)
> **Est. Tests:** ~128

---

## Slice A: Foundations

### A1. Data model + serialization

**Files:** `world_state.py`, `SAVE_FORMAT_REFERENCE.md`

- Add `betrayal_history: Dict[str, Dict]` to WorldState (directional key `from|to`, value: `{strikes, categories, last_turn, decays_on_turn}`)
- Add `nation_rivalries: Dict[str, Dict]` to WorldState (diplo_key, value: `{intensity, source, started_turn, last_changed_turn}`)
- Add `diplomatic_commitments: Dict[str, Dict]` to WorldState (commitment id key, tracked promise record)
- Add `next_commitment_id: int` to WorldState
- Add `trusted_partners: Dict[str, Dict]` to WorldState (diplo_key, value: `{status, earned_turn, clean_turns}`)
- Clarify `diplomatic_reliability` docstring as nation-keyed reputation (not pair-keyed)
- Initialize 3 starting rivalries: France<->Britain `active`, Prussia<->Austria `active`, Prussia<->Saxony `cold`
- Add cached `get_rivalries_for_nation()` and `get_rival_pairs()` helpers
- Wire `to_dict()` / `from_dict()` with `.get()` defaults
- Update `SAVE_FORMAT_REFERENCE.md`
- ~12 tests (serialization round-trip, helper lookups, starting state)

### A2. Ledger + debug surfacing

**Files:** `diplomatic_ledger.py`, `main.py`

- Add rivalry display to diplomatic ledger Nations tab
- Add reliability descriptor + bilateral betrayal warning to Talleyrand tab
- Add trusted-partner status surfacing
- Add active commitments section (empty for now, ready for Slice C)
- Debug endpoint for rivalry/betrayal state inspection
- ~6 tests (ledger output formatting)

---

## Slice B: Rivalry Pressure

### B1. Acceptance formula modifiers

**Files:** `diplomacy.py`

- Add `direct_rivalry_mod` to `calculate_acceptance()` - negative for deeper treaties with direct rivals
- Add `rival_conflict_mod` - negative when target knows France is aligned with its rival
- Add `bilateral_betrayal_mod` - reads `betrayal_history`, ~2x weight of global reliability
- Add `trusted_partner_mod` - modest positive for long-honored alliances
- Group all under `political_commitment_mod` composite in formula breakdown
- Wire debug breakdown output
- ~20 tests (acceptance with/without rivalry, cold vs active constants, trusted partner, stacking, edge cases)

### B2. Third-party anger + betrayal recording

**Files:** `world_state.py`, `diplomacy.py`, `dispatch.py`

- On treaty ratification (`_ratify_treaty`): compute rival anger, apply relation penalties per spec $7.4B table
- Apply `they_chose_us` relation bonus to the side France visibly backed
- Record betrayal events on treaty break - victim gets strikes, witnesses get scoped penalties
- Witness penalty logic: only allies of victim + nations with active rivalry against betrayer; witnesses do not get victim-grade strikes
- Redemption tick in `advance_turn()`: +3 reliability per 5 honored turns, severity-scaled bilateral strike decay
- Hard-reject behavior: 3 victim-side strikes -> hard resist deep treaties (exception paths still allowed)
- Trusted-partner earn / lose logic (10 clean alliance turns, removed on betrayal)
- Prussia<->Saxony hardcoded escalation: direct war or France vassalizes Saxony -> escalate to `active`
- Dispatch entries for: rivalry escalation, betrayal recorded, reliability change
- ~25 tests (anger calc, they_chose_us, betrayal recording, witness scoping, hard-reject posture, trusted partner, redemption, escalation triggers)

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
- Commitment creation on ratification: create tracked record with `deadline_turn`, `suspended_turns`, status, regions, beneficiary
- Fulfillment check in `advance_turn()`: beneficiary controls region + France still holds DEFENSIVE_ALLIANCE/ALLIANCE at fulfillment time
- Failure detection: deadline expiry, source treaty break (immediate + stacks with treaty-break penalties), rival alignment, French vassalization / self-keeping of promised target
- Penalty/reward application: fulfillment (+4 reliability, relation bonus), passive failure (-15 relation, +1 strike, -6 reliability), active sabotage uses stronger penalties
- `promise_value_mod` acceptance modifier - replaces `SPECIAL_BONUSES` when tracked `territorial_promise` clause present (no double-counting)
- Urgency warnings in dispatch at 50% / 75% / 3-turns-remaining of effective deadline
- Suspension logic: direct war with beneficiary increments `suspended_turns`, bad-faith settlement during suspension = breach, 5-turn direct-enemy status auto-voids promise
- Source treaty interaction: France breaks source treaty = immediate promise failure; beneficiary breaks = void no penalty; natural downgrade = promise survives
- ~28 tests (creation, fulfillment, passive vs active failure, suspension, auto-void, deadline math, warning timing, source treaty interactions)

### C2. Renegotiation + AI stub + surfaces

**Files:** `diplomatic_templates.py`, `diplomatic_executor.py`, `parser.py`, `validation.py`, `llm_client.py`, `prompt_builder.py`, `diplomatic_ledger.py`, `campaign_log.py`, `display_names.py`

- New `renegotiate_promise` action — add to `VALID_ACTIONS`, `valid_actions` list, `_action_costs`, mock parser keywords, `ACTION_DISPLAY`
- HARD_STOP dialogue flow: two branches (downgrade scope / cancel with light penalty at -5 relation, -3 reliability, no strike)
- AI refusal path if beneficiary rejects renegotiation
- Minimal AI promise generation stub in `generate_suggested_terms()` stage 2 - gated on `covets_regions` matching region controlled by France or by that nation's rival, excluding France's primary rival cases where promise logic would read as nonsense
- Ledger: active commitments with deadline, status, fulfillment progress in Treaties or Talleyrand tab
- Campaign log event types: `promise_fulfilled`, `promise_broken`, `promise_renegotiated` in `CAMPAIGN_LOG_TYPES` + `format_event_oneliner()`
- `_DEFIANCE_DISPLAY` + `_OBJECTION_DISPLAY` entries in `campaign_log.py` if applicable
- ~14 tests (renegotiation flow, AI stub generation, cost model, ledger output)

---

## Slice D: AI Integration (can defer)

### D1. Advisory-first strategic focus + deeper AI integration

**Files:** `ai_diplomacy.py`, `enemy_ai.py`

- Strategic-focus layer for AI phrasing + Talleyrand recommendations: major powers expose concern/counterweight, minors expose feared rival/protector
- Derive `nation_power_scores` / `nation_power_tiers` from controlled regions, army strength, manpower depth, and vassal weight with hysteresis
- AI proposal generation considers rivalries: exclusivity offers ("ally us, not our rival"), promise-based courtship
- AI escalation behavior: repeated rival-camp alignment -> downgrade treaties, hostility pivot
- Optional later: general dynamic rivalry formation system (beyond Prussia-Saxony hardcoded triggers from B2)
- Performance: no new per-region scans, use cached rivalry lookups
- ~16 tests (power-tier derivation, hysteresis, focus surfacing, rival-aware proposals, escalation behavior)

---

## Execution Order

```
A1 -> A2 -> B1 -> B2 -> B3 -> C1 -> C2 -> D1
```

Each session is self-contained and testable independently. Recommended playtest gates:

- **After A2:** Verify rivalries appear in ledger, starting state is correct
- **After B2:** Verify rivalry pressure affects acceptance, anger fires on treaty deepening, betrayal records
- **After B3:** Verify commitment paradox popup fires and resolves correctly
- **After C2:** Full territorial promise loop testable end-to-end with AI stub

Slice D can be deferred entirely if static rivalries + hardcoded triggers feel good enough in playtesting.

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
| D1 | A1, B1, B2, C1 | AI reads all new stores and surfaces trusted/focus state |
