# WB-B Code Review Audit Prompt

> Paste this into Codex or another AI review tool to get a code review of the WB-B (War Bargain Lifecycle) implementation.

---

## Context

This is a Napoleonic strategy game (Godot 4 frontend, FastAPI backend). The "War Bargain" mechanic is a political-promise layer where France makes a bilateral commitment to an ally (beneficiary) against a named enemy, claiming priority over one enemy-held region.

**WB-A** (data model + creation + validation) was already implemented. **WB-B** adds the lifecycle: fulfillment, breach, void, and zombie-clock mechanics.

## Spec Summary (from `docs/WAR_BARGAIN_SPEC.md` §8.6–§8.9)

### Status lifecycle:
- `active` → `triggered` (co-belligerents against named enemy)
- `triggered` → `fulfilled` (France captures claim region while all 5 conditions hold)
- `triggered` → `active` (inconclusive war, source treaty + claim still valid)
- `active`/`triggered` → `breached` (France-caused: treaty break, normalization with enemy, etc.)
- `active`/`triggered` → `void` (counterparty reversal OR obsolescence/external)

### Fulfillment conditions (§8.8):
1. Bargain is `triggered`
2. France controls the claimed region
3. Region changed from enemy to France while bargain valid
4. Source treaty (DEF_ALLIANCE/ALLIANCE) still valid with beneficiary
5. Still co-belligerents against named enemy

### Fulfillment rewards:
- `+4` diplomatic reliability (capped per promiser/beneficiary pair per 10 turns)
- `+6` relation with beneficiary

### Breach penalties (§8.9.A):
- `-6` diplomatic reliability
- `-10` relation with beneficiary
- `+1` betrayal strike (2-per-episode cap)
- 6-turn cooldown on same pair+enemy

### Void conditions (§8.9.B):
- **Counterparty reversal**: beneficiary breaks treaty, aligns with enemy, joins anti-France coalition
- **Obsolescence/external**: claim basis lost, parties at war externally, zombie lapse
- No French penalty; 4-turn cooldown

### Zombie clock:
- Increments each turn both sides at ARMISTICE+ with named enemy
- Resets only on actual WAR state
- Voids at 5 accumulated turns

### Same-turn downgrade exploit guard:
- Voluntary source treaty downgrade on the same turn fulfillment would occur = breach, not passive failure

## Files Changed

1. **`backend/game_logic/diplomacy.py`** — Added ~300 lines after `create_war_bargain_commitment()`:
   - Constants: `BARGAIN_BREACH_COOLDOWN_TURNS`, `BARGAIN_VOID_COOLDOWN_TURNS`, `BARGAIN_ZOMBIE_VOID_THRESHOLD`, reward/penalty deltas
   - `process_bargain_lifecycle(world)` — per-turn lifecycle entry point
   - `_check_bargain_fulfillment()`, `_fulfill_bargain()` — fulfillment logic + snapshot
   - `breach_bargain()` — breach with penalties + strike recording
   - `_void_bargain()`, `_detect_void()` — void detection + classification
   - `_process_zombie_clock()` — cumulative armistice counter
   - `detect_bargain_breach_on_treaty_change()` — hook for state-change-triggered breach
   - `detect_bargain_breach_on_peace()` — hook for peace-triggered breach
   - `_emit_bargain_event()` — campaign log + dispatch event emission
   - Wired into `process_diplomacy_turn()` as step 13a (after auto-downgrade, before reliability processing)

2. **`backend/campaign_log.py`** — Added 4 event types to `CAMPAIGN_LOG_TYPES` + `CATEGORY_MAP` + one-liner formatters in `format_event_oneliner()`

3. **`backend/game_logic/dispatch.py`** — Added 4 dispatch templates + priorities

4. **`tests/test_wb_b_lifecycle.py`** — 42 tests covering all lifecycle paths

5. **`tests/test_campaign_log.py`** + **`tests/test_bph_a_term_ownership.py`** — Count updates (68 → 72)

## Review Checklist

Please evaluate the implementation against these criteria:

### 1. Spec Compliance
- [ ] All status transitions match §8.6 lifecycle
- [ ] Fulfillment conditions match §8.8 (all 5 checks)
- [ ] Breach triggers match §8.9.A (source treaty break, normalization with enemy/holder, peace with enemy, contradictory bargain)
- [ ] Void families correctly classified: `counterparty_reversal` vs `obsolescence_or_external` per §8.9.B
- [ ] Zombie clock uses cumulative counting (not continuous), resets only on WAR, voids at 5
- [ ] Fulfillment reward: +4 reliability (10-turn pair cap), +6 relation
- [ ] Breach penalty: -6 reliability, -10 relation, +1 strike (2-per-episode cap), 6-turn cooldown
- [ ] Void: no French penalty, 4-turn cooldown
- [ ] Dormant notice fires once at 8+ turns active, resets on reactivation (per §10.2)
- [ ] `fulfilled` is terminal — no retroactive reopen
- [ ] Same-turn downgrade exploit guard (voluntary downgrade = breach per §8.8)

### 2. Golden Rules Compliance
- [ ] No per-region scans in hot paths (Rule 8)
- [ ] All numbers to Godot as int() (Rule 2)
- [ ] State clearing AFTER reading (Rule 4)
- [ ] LLM never affects mechanics (Rule 6)

### 3. Architecture
- [ ] `process_bargain_lifecycle()` placement in turn order: AFTER war-state/region mutations, AFTER auto-downgrade (correct ordering per §8.8 turn-order rule)
- [ ] No circular imports
- [ ] Helpers are private (underscore prefix) except public API surfaces
- [ ] Episode-ID propagation through breach paths respects 2-strike cap
- [ ] Campaign log events have correct fog rules (`always` for public events, `partial_on_nation` for voided)

### 4. Serialization
- [ ] `_reactivated_turn` field: is it serialized? Should it be? (It's transient within-turn state only, recomputed each lifecycle pass — should be fine without serialization if the only use is dormant-clock base)
- [ ] `_bargain_fulfillment_log` field: is it serialized? (Currently transient — should it persist across save/load for the 10-turn reward cap?)

### 5. Edge Cases
- [ ] What happens if multiple bargains exist and one voids mid-iteration? (iterating over `list(commitments.items())` — safe)
- [ ] What if beneficiary and France are both co-belligerents AND claim basis is lost in same turn? (fulfillment check runs before void check — correct: if France captured it, it's France-held now)
- [ ] Self-referential bargain (promiser == beneficiary)? (Prevented by WB-A validation, not re-checked here — acceptable)
- [ ] Reliability clamped to [-100, 100]? (Yes, via `max(-100, min(100, ...))`)

### 6. Missing Items (Spec coverage gaps)
- [ ] Constructive breach via French-engineered auto-decay (§8.9.A: ratifying NON_AGGRESSION+ with opposed nation, attacking ally of beneficiary, contradictory bargain) — is `detect_bargain_breach_on_treaty_change` sufficient or does it need integration at the ratification callsite?
- [ ] `repudiate_bargain` explicit action — spec says it ships in WB-B but the action wiring (parser, VALID_ACTIONS, executor) is assigned to WB-C. Is this intentional deferral or a gap?
- [ ] Peace-conflict warning surfacing BEFORE breach — the spec says breach triggers "after a surfaced `peace_conflict` warning." Currently `detect_bargain_breach_on_peace` fires unconditionally. Is the warning-first gate deferred to WB-C?

### 7. Test Coverage
- [ ] Are there missing edge cases? (e.g., bargain where promiser is NOT France — spec says v0.1 is France-only but code is parameterized)
- [ ] Serialization round-trip test for the new transient fields?
- [ ] Integration with `advance_turn()` — does a full turn cycle trigger bargain lifecycle correctly?

## How to Run

```bash
cd "C:\Users\User\PycharmProjects\project-sovereign-map"
".venv\Scripts\python.exe" -m pytest tests/test_wb_b_lifecycle.py -v
".venv\Scripts\python.exe" -m pytest tests/ -q --tb=no  # Full suite: 9154 passed
ruff check backend/game_logic/diplomacy.py backend/campaign_log.py backend/game_logic/dispatch.py tests/test_wb_b_lifecycle.py
```

## Key Questions for the Reviewer

1. Should `_bargain_fulfillment_log` be serialized (persisted across save/load) to enforce the 10-turn reward cap durably? Currently it's in-memory only.
2. Is the breach detection hookpoint placement correct? Currently it's standalone functions that must be called from ratification/peace paths — should we wire them directly into `set_diplomatic_state()` or leave that for WB-C integration?
3. The void detection checks `source_treaty_lost` before `parties_at_war` — this means setting France+beneficiary to WAR voids as `counterparty_reversal` (treaty loss) rather than `obsolescence_or_external` (at war). Is this the correct precedence?
