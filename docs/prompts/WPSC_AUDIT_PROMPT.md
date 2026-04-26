# WPS-C Forced Alliance + Liberation — Code Review Audit Prompt

**Commit:** `7a22b6f` (Implement WPS-C: Forced alliance + liberation clause types)
**Spec:** `docs/WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md` §9 (Forced Alliance) and §10 (Liberation)
**Test file:** `tests/test_wpsc_forced_alliance.py` (26 tests)

---

## What was implemented

WPS-C adds two new treaty clause types to the peace deal system:

1. **Forced Alliance** — victor imposes ALLIANCE + Continental System on defeated nation. Starts relation at 0, applies -10/turn drift, generates +15 coalition threat. Acceptance formula overrides base_disposition from 30 to -15 and adds -20 demand penalty.

2. **Liberation** — coalition releases a French vassal via `release_vassal()`, creates DEFENSIVE_ALLIANCE with liberator, adjusts relations (-20 with France, +30 with liberator), reduces threat by 8.

New serialized field: `alliance_origins` (Dict[str, str]) tracks "forced" vs "voluntary" origin per alliance pair.

---

## Files changed (review these)

| File | Lines added | What changed |
|------|-------------|-------------|
| `backend/models/world_state.py` | +73 | `alliance_origins` field + serialization, demand→clause extra field carry-over (`vassal_nation`, `lord_nation`, `liberator`), forced_alliance ratification block (sets ALLIANCE, resets relation, adds Continental System, sets origin, +15 threat, logs event), liberation ratification block (release_vassal, DEFENSIVE_ALLIANCE, relation adjustments, -8 threat, logs event) |
| `backend/game_logic/diplomacy.py` | +45 | DEMAND_VALUES entries (-20 forced_alliance, -15 liberation), base_disposition override to -15 when forced_alliance clause present, `_process_forced_alliance_drift()` (-10/turn for forced origins, clears origin on state drop), step 12a call in `process_diplomacy_turn`, `alliance_origins` cleanup in `set_diplomatic_state` |
| `backend/game_logic/diplomatic_templates.py` | +6 | Harshness entries (forced_alliance 0.4, liberation 0.3), display label templates |
| `backend/campaign_log.py` | +30 | `forced_alliance_imposed` and `vassal_liberated` event types, CATEGORY_MAP entries, oneliner formatters, fog filtering (visible when involved nation has PARTIAL+ visibility) |
| `docs/SAVE_FORMAT_REFERENCE.md` | +3 | `alliance_origins` field documentation |
| `tests/test_bph_a_term_ownership.py` | 1 line | Campaign log type count 66→68 |
| `tests/test_campaign_log.py` | 2 lines | Campaign log type count 66→68, updated docstring |
| `tests/test_wpsc_forced_alliance.py` | +489 (new) | 26 tests across 6 classes |

---

## Audit checklist

### 1. Spec compliance (§9 Forced Alliance)

- [ ] **§9.2 Mechanical effect:** Ratification sets ALLIANCE state, adds to continental_system_members, resets relation to 0, ends war states. Verify `cleanup_war_end()` fires BEFORE setting ALLIANCE state.
- [ ] **§9.3 Acceptance formula:** base_disposition overrides to -15 (not additive). DEMAND_VALUES["forced_alliance"] = -20. Verify the override detects forced_alliance in demands (not clauses).
- [ ] **§9.5 Forced alliance stability:** alliance_origins tracks "forced". Drift is -10/turn. Origin clears when state drops below ALLIANCE or pair enters WAR. Drift only applies while state == ALLIANCE and origin == "forced".
- [ ] **§9.6 Threat:** +15 coalition threat on ratification.

### 2. Spec compliance (§10 Liberation)

- [ ] **§10.4 Mechanical effect:** `release_vassal()` fires, DEFENSIVE_ALLIANCE with coalition leader (not ALLIANCE), relation -20 with France, +30 with liberator, threat -8.
- [ ] **§10.5 Acceptance:** DEMAND_VALUES["liberation"] = -15.

### 3. Serialization

- [ ] `alliance_origins` added to `__init__`, `to_dict()`, `from_dict()` with `.get()` default.
- [ ] Round-trip test exists and passes.
- [ ] `SAVE_FORMAT_REFERENCE.md` updated.
- [ ] `test_serialization_enforcement.py` still passes (confirmed).

### 4. Demand→clause field carry-over

- [ ] The `_ratify_treaty` method converts demands to clause dicts. Extra keys (`vassal_nation`, `lord_nation`, `liberator`) must be carried over. Verify the carry-over loop is placed correctly in the conversion.
- [ ] No other clause types rely on extra fields that might be dropped by the same conversion.

### 5. Process ordering in diplomacy turn

- [ ] Forced alliance drift (step 12a) runs BEFORE auto-downgrade check (step 13) in `process_diplomacy_turn`. This ensures drift can push relations below threshold, and the auto-downgrade then acts on it.

### 6. Campaign log integration

- [ ] Both event types in CAMPAIGN_LOG_TYPES and CATEGORY_MAP (category: "diplomacy").
- [ ] Oneliners produce readable English with correct field extraction.
- [ ] Fog filtering: events visible when the involved nation (forced nation / liberated nation) has PARTIAL+ visibility.

### 7. Edge cases to verify

- [ ] Forced alliance on a nation already in Continental System — no duplicate add?
- [ ] Liberation of a nation that was already released (vassal no longer exists) — graceful handling?
- [ ] Forced alliance drift when relation is already very negative — does it keep drifting below -100 or is there a floor?
- [ ] Multiple forced_alliance clauses in same treaty (different nations) — each processed independently?
- [ ] `alliance_origins` cleanup: verify it fires in `set_diplomatic_state` for ALL transitions away from ALLIANCE, not just specific ones.

### 8. Golden rule compliance

- [ ] No per-region scans in hot paths (drift processes per-key in alliance_origins, not per-region).
- [ ] All numbers to Godot: `int()` — verify any numeric values that reach the frontend.
- [ ] State clearing AFTER reading — verify no premature clears.
- [ ] Single source of truth: combat modifiers untouched (this is diplomacy-only).

### 9. Test coverage gaps

- [ ] Are there tests for the edge cases in §7 above?
- [ ] Is the `_process_forced_alliance_drift` function tested for the case where multiple forced alliances exist simultaneously?
- [ ] Is there a test for the interaction between forced alliance and existing Continental System membership?

---

## How to run

```bash
# WPS-C tests only
".venv\Scripts\python.exe" -m pytest tests/test_wpsc_forced_alliance.py -v

# Full suite
".venv\Scripts\python.exe" -m pytest tests/ -v --tb=no -q

# Serialization enforcement
".venv\Scripts\python.exe" -m pytest tests/test_serialization_enforcement.py -v
```

## Key codebase rules (from CLAUDE.md)

- Combat modifiers: SINGLE SOURCE in `marshal.py` — do NOT touch for diplomacy features
- Serialization: every new field must be in `to_dict()` + `from_dict()` + `SAVE_FORMAT_REFERENCE.md`
- `set_diplomatic_state` is the canonical state transition function — all state changes must go through it
- `cleanup_war_end()` handles war state teardown (scores, records, decisive battles, strategic orders)
- DEMAND_VALUES in `diplomacy.py` is the acceptance formula's demand penalty source
