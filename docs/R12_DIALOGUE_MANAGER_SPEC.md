# R12 DialogueManager Spec

**Root Cause:** RC-8 Dialogue State Machine Chaos
**Priority:** MAJOR | **Risk:** HIGH (~118 ops across 13 files)
**Dependencies:** R11 complete (diplomatic_executor separated)

## Problem

`pending_diplomatic_dialogue` and `pending_dialogue_queue` are raw fields on WorldState with ~30 SETs, ~48 CLEARs, ~32 READs, and 4 queue appends scattered across 13 backend files. Consequences:

1. **Duplicate auto-pop logic** — identical priority-sort-then-pop in both `main.py:282-295` and `turn_manager.py:254-272`, with duplicated priority dicts
2. **No queue cap** — unbounded append during advance_turn
3. **Timeout logic in wrong place** — non-blocking auto-dismiss + blocking safety valve live in `world_state.py:advance_turn()` instead of dialogue system
4. **Paired popup clearing scattered** — 5 places manually clear `incoming_proposal_popup` alongside dialogue (diplomatic_executor 2, world_state 2, executor 1)
5. **No enforcement** — any file can overwrite active dialogue without queueing
6. **Latent overwrite bug** — `world_state.py:4341` (`_process_proposal_in_transit`) can overwrite an active blocking dialogue during advance_turn

**Note:** Operation counts are approximate. Each migration phase must run `grep 'pending_diplomatic_dialogue\s*=' backend/` to verify all sites are found.

### Operation Breakdown by File

| File | SETs | CLEARs | READs | Queue | Total |
|------|------|--------|-------|-------|-------|
| diplomatic_executor.py | 22 | 43 | 9 | 0 | 74 |
| world_state.py | 3 | 2 | 4 | 0 | 9 |
| main.py | 1 | 0 | 7 | 0 | 8 |
| dispatch.py | 2 | 0 | 2 | 1 | 5 |
| turn_manager.py | 1 | 0 | 3 | 0 | 4 |
| vassal.py | 0 | 2 | 2 | 1 | 5 |
| ai_diplomacy.py | 0 | 0 | 3 | 1 | 4 |
| coalition.py | 0 | 2 | 1 | 0 | 3 |
| executor.py | 0 | 1 | 3 | 0 | 4 |
| diplomacy.py | 0 | 0 | 1 | 1 | 2 |
| diplomatic_defiance.py | 0 | 0 | 0 | 0 | 0 (factory only) |
| diplomatic_dialogue.py | 0 | 0 | 0 | 0 | 0 (factory only) |
| diplomatic_advisory.py | 0 | 0 | 0 | 0 | 0 (factory only) |
| **TOTAL** | **~29** | **~50** | **~35** | **4** | **~118** |

---

## Design: DialogueManager

**File:** `backend/models/dialogue_manager.py`

```python
class DialogueManager:
    QUEUE_CAP = 20
    BLOCKING_TIMEOUT_TURNS = 2   # Match existing safety valve (turn_created + 2 < current)

    # Single source of truth for dialogue priority (consolidates 2 duplicates)
    # Unlisted types (counter_offer_response, advisory, etc.) default to 99 (lowest)
    DIALOGUE_PRIORITY = {
        "alliance_paradox": 0,
        "vassal_rebellion_imminent": 1,
        "sabotage_confrontation": 2,
        "talleyrand_redemption": 3,
        "incoming_proposal": 4,
    }

    def __init__(self):
        self._current: Optional[Dict] = None
        self._queue: List[Dict] = []
```

### Core API

| Method | Purpose | When to use |
|--------|---------|-------------|
| `push(dialogue)` | Set current if empty, queue if occupied (respects cap) | New dialogue from any source |
| `replace(dialogue)` | Overwrite current regardless of state | Enrichment, modification, or clear-then-set patterns |
| `pop()` | Clear current, auto-promote highest-priority from queue | Dialogue resolved or dismissed |
| `peek()` | Read current without side effects | Guard checks, response embedding |
| `is_blocking()` | Check if current dialogue blocks commands | Pre-validation guards |
| `clear_stale(current_turn)` | Auto-dismiss expired dialogues (non-blocking + blocking timeout) | Called in advance_turn |
| `promote_if_empty()` | If current is None and queue has items, promote highest-priority | Turn-start queue drain |
| `remove_matching(predicate)` | Filter queue items by predicate, also checks current | Coalition/vassal cleanup |
| `to_dict()` / `from_dict()` | Serialization (uses `copy.deepcopy` for nested dicts) | Save/load |

### Four Write Patterns

The audit identified four distinct write patterns. Each maps to one API method:

```python
# Pattern 1: NEW DIALOGUE — slot may be empty or occupied
# Before: world.pending_diplomatic_dialogue = dialogue_dict
# After:  world.dialogue_manager.push(dialogue_dict)
#   → If empty: sets current. If occupied: queues.
# Sites: ~15 (confirmed empty-slot SETs)

# Pattern 2: ENRICHMENT — replace active dialogue in-place
# Before: world.pending_diplomatic_dialogue = enriched_dialogue
# After:  world.dialogue_manager.replace(enriched_dialogue)
#   → Always overwrites current. Does NOT queue old dialogue.
# Sites: 3 (line 1078, 1176, 1619 in diplomatic_executor.py)

# Pattern 3: CLEAR-THEN-SET — replace current with entirely new dialogue
# Before: world.pending_diplomatic_dialogue = None; ...; world.pending_diplomatic_dialogue = new
# After:  world.dialogue_manager.replace(new_dialogue)
#   → CANNOT use pop() + push() — pop() auto-promotes from queue,
#     then push() would queue the new dialogue behind the promoted item.
#   → replace() overwrites directly, preserving intent.
# Sites: ~4 (e.g. line 1203-1209 in diplomatic_executor.py)

# Pattern 4: RESOLVE/DISMISS — dialogue completed or cancelled
# Before: world.pending_diplomatic_dialogue = None
# After:  world.dialogue_manager.pop()
#   → Clears current. Auto-promotes next from queue by priority.
# Sites: ~48 CLEARs
```

**IMPORTANT — Pattern 3 vs Pattern 4:** During migration, every `= None` site must be classified as either Pattern 3 (clear-before-replace, use `replace()`) or Pattern 4 (resolve/dismiss, use `pop()`). The distinction: if a SET follows the CLEAR in the same code path, it's Pattern 3. If the code returns after clearing, it's Pattern 4.

### Auto-Promote on Pop

`pop()` consolidates the duplicate auto-pop logic currently in `main.py:282-295` and `turn_manager.py:254-272`:

```python
def pop(self) -> Optional[Dict]:
    result = self._current
    self._current = None
    if self._queue:
        self._queue.sort(
            key=lambda d: self.DIALOGUE_PRIORITY.get(d.get("type", ""), 99)
        )
        self._current = self._queue.pop(0)
    return result
```

### Promote If Empty

Replaces `turn_manager._pop_dialogue_queue()` for the turn-start case where current is None but queue has items from a prior turn:

```python
def promote_if_empty(self) -> bool:
    """Promote highest-priority queue item to current if slot is empty.
    Returns True if promotion occurred."""
    if self._current is not None or not self._queue:
        return False
    self._queue.sort(
        key=lambda d: self.DIALOGUE_PRIORITY.get(d.get("type", ""), 99)
    )
    self._current = self._queue.pop(0)
    return True
```

**Why this is needed:** After 12C removes `_pop_dialogue_queue()`, queue items from prior turns need a promotion point. `pop()` auto-promotes but only fires when something is cleared. `promote_if_empty()` handles the case where current was already None (e.g., player ignored a non-blocking dialogue that expired, items remain queued). Called at the turn-start position where `_pop_dialogue_queue()` used to be.

### Stale Dialogue Clearing

`clear_stale()` consolidates the two timeout blocks currently in `world_state.py:4048-4068`:

```python
def clear_stale(self, current_turn: int) -> Optional[Dict]:
    """Returns cleared dialogue if any, for logging. Auto-promotes from queue."""
    if not self._current:
        return None
    turn_created = self._current.get("turn_created", 0)
    is_blocking = self._current.get("blocking", False)

    # Non-blocking: dismiss if older than current turn
    if not is_blocking and turn_created < current_turn:
        return self.pop()

    # Blocking: safety valve after BLOCKING_TIMEOUT_TURNS
    if is_blocking and turn_created + self.BLOCKING_TIMEOUT_TURNS < current_turn:
        return self.pop()

    return None
```

**Timing note:** `clear_stale()` calls `pop()` which auto-promotes. In the current code, stale clearing (`= None`) and queue promotion (`_pop_dialogue_queue`) are separate steps. With `clear_stale()`, promotion happens immediately on clear. This means items pushed to queue AFTER `clear_stale()` runs (but during the same advance_turn) won't compete with the already-promoted item — they'll be queued behind it. A characterization test must verify this timing doesn't change which dialogue surfaces.

### Queue Filtering

`remove_matching()` consolidates the queue filter patterns in `coalition.py` and `vassal.py`:

```python
def remove_matching(self, predicate) -> int:
    """Remove queue items (and current if matched) by predicate. Returns count removed.
    Note: does NOT clear paired popups (incoming_proposal_popup) — caller's responsibility."""
    removed = 0
    # Filter queue
    before = len(self._queue)
    self._queue = [d for d in self._queue if not predicate(d)]
    removed += before - len(self._queue)
    # Check current
    if self._current and predicate(self._current):
        self._current = None
        removed += 1
        # Auto-promote after removing current
        if self._queue:
            self._queue.sort(
                key=lambda d: self.DIALOGUE_PRIORITY.get(d.get("type", ""), 99)
            )
            self._current = self._queue.pop(0)
    return removed
```

---

## Integration: WorldState

### 12A — Transparent Wrapper (backward compat)

Properties bypass manager logic, directly mirror old behavior:

```python
def __init__(self):
    self._dialogue_manager = DialogueManager()

@property
def pending_diplomatic_dialogue(self):
    return self._dialogue_manager._current

@pending_diplomatic_dialogue.setter
def pending_diplomatic_dialogue(self, value):
    self._dialogue_manager._current = value   # Direct set, no push/pop logic

@property
def pending_dialogue_queue(self):
    return self._dialogue_manager._queue

@pending_dialogue_queue.setter
def pending_dialogue_queue(self, value):
    self._dialogue_manager._queue = list(value) if value else []

@property
def dialogue_manager(self):
    return self._dialogue_manager
```

**Why direct access:** The setter must reproduce exact current behavior — overwrite on set, clear on None, no auto-promote. All 7,707 tests pass unchanged.

### 12C — Read-Only Property (final state)

```python
@property
def pending_diplomatic_dialogue(self):
    return self._dialogue_manager.peek()

# Setter REMOVED — forces all writes through dialogue_manager API
# Queue property REMOVED — use dialogue_manager.push() which auto-queues

@property
def dialogue_manager(self):
    return self._dialogue_manager
```

### Serialization Integration

```python
# to_dict() — delegate to manager (uses deepcopy for nested dicts)
"dialogue_manager": self._dialogue_manager.to_dict(),
# Remove: "pending_diplomatic_dialogue" and "pending_dialogue_queue" keys

# from_dict() — backward-compat for old saves
if "dialogue_manager" in data:
    world._dialogue_manager = DialogueManager.from_dict(data["dialogue_manager"])
else:
    # Legacy save format
    dm = DialogueManager()
    pending = data.get("pending_diplomatic_dialogue")
    if pending:
        dm._current = copy.deepcopy(pending)
    dm._queue = [copy.deepcopy(d) for d in data.get("pending_dialogue_queue", [])]
    world._dialogue_manager = dm
```

---

## Phase Plan

### 12A — Foundation (LOW risk)

**Goal:** DialogueManager exists, is tested, is wired in. Zero external behavior change.

**Steps:**
1. Write characterization tests pinning current dialogue behavior (before any code changes)
2. Create `backend/models/dialogue_manager.py` with full API
3. Unit test all DialogueManager methods in isolation
4. Wire into WorldState with transparent property wrappers
5. Update `to_dict()`/`from_dict()` with legacy compat
6. Run full suite — must be 7,707 green

**Characterization tests (pin before touching anything):**
- Dialogue set overwrites current
- Dialogue `= None` clears current
- Queue append queues
- Auto-pop promotes by priority (turn_manager path)
- Auto-pop promotes by priority (main.py path)
- Blocking prevents end-turn
- Non-blocking auto-dismisses on advance_turn
- Blocking safety valve clears after 2 turns
- Serialization round-trip preserves dialogue + queue
- Paired popup clears with dialogue (5 sites)
- Dispatch conditional queue-vs-set pattern (if occupied → queue, else → set)
- Overwrite-after-promote: dispatch SET after turn_manager pop (pre-existing behavior, pin it)
- Stale clear + same-turn push: verify which dialogue surfaces when clear_stale and push happen during same advance_turn

**Manager unit tests:**
- push to empty → sets current
- push when occupied → queues
- push respects QUEUE_CAP
- replace overwrites current
- replace when empty sets current
- pop returns current and auto-promotes
- pop from empty returns None
- peek returns current without removing
- peek empty returns None
- is_blocking true/false
- clear_stale non-blocking dismiss
- clear_stale blocking timeout
- clear_stale keeps fresh dialogues
- clear_stale auto-promotes from queue
- promote_if_empty promotes when current is None
- promote_if_empty no-ops when current exists
- promote_if_empty no-ops when queue empty
- remove_matching filters queue
- remove_matching clears current if matched + auto-promotes
- priority ordering correct (5 types + default 99)
- serialization round-trip (empty, with current, with queue, nested dicts)
- from_dict legacy format

**Commit gate:** Full suite green, zero external files changed except `world_state.py` (properties + serialization).

---

### 12B — Core Migration: diplomatic_executor.py (MEDIUM risk)

**Goal:** Migrate the biggest file (~74 ops, ~63%) to explicit manager API.

**Pre-migration step:** Run `grep -n 'pending_diplomatic_dialogue\s*=' backend/commands/diplomatic_executor.py` to get exact line numbers. Audit each site against the four patterns.

**Migration rules:**
```
= None (followed by return)             → world.dialogue_manager.pop()         [Pattern 4]
= None (followed by new SET)            → skip — the SET becomes replace()     [Pattern 3]
= dialogue_dict (enrichment of current) → world.dialogue_manager.replace(d)    [Pattern 2]
= dialogue_dict (clear preceded it)     → world.dialogue_manager.replace(d)    [Pattern 3]
= dialogue_dict (slot was empty)        → world.dialogue_manager.push(d)       [Pattern 1]
world.incoming_proposal_popup = None    → keep inline (paired clearing stays)
```

**Approach:** Top-to-bottom, one method at a time. Run full suite after each method's migration. The transparent property setter means partially-migrated state is safe — unmigrated code (in other files) still works through properties.

**12B is safe during partial migration:** Migrated code calls `pop()` (auto-promotes). External auto-pop in `main.py:282-295` then sees `pending_diplomatic_dialogue is not None` and skips (no-op). No double-promote.

**Known enrichment sites (use `replace`):**
- Line 1078: `_process_dialogue_choice` modify action — enriched proposal summary
- Line 1176: `_process_dialogue_choice` modify_generous — enriched proposal summary
- Line 1619: `_handle_incoming_ai_counter_offer` — enriched counter-offer review

**Known clear-then-set sites (use `replace`, delete the preceding `= None`):**
- Line 1203-1209: expand proposal — clear current then generate new dialogue
- (Audit may reveal more — verify each `= None` that is NOT followed by a return)

**All other SETs use `push()`. All standalone CLEARs use `pop()`.**

**Commit gate:** Full suite green. `grep -c 'pending_diplomatic_dialogue\s*=' backend/commands/diplomatic_executor.py` returns 0.

---

### 12C — Consolidation + Lock Down (MEDIUM risk)

**Goal:** Migrate remaining 12 files, eliminate duplicate logic, remove property setter.

**Pre-migration step:** Run `grep -rn 'pending_diplomatic_dialogue\s*=' backend/ --include='*.py'` and `grep -rn 'pending_dialogue_queue' backend/ --include='*.py'` to get exact remaining sites.

**Step 1 — Migrate peripheral backend files:**

| File | Ops | Migration |
|------|-----|-----------|
| world_state.py | 9 | Init creates manager. `clear_stale()` replaces advance_turn timeout blocks (lines 4048-4068). Line 4341 counter-offer SET → `push()` (fixes latent overwrite bug). Serialization delegates to manager. |
| main.py | 8 | Remove duplicate auto-pop (lines 282-295). Keep READs via property. |
| dispatch.py | 5 | READs stay (property). Conditional queue-vs-set (lines 829-833) → `push()` (handles both cases). Redemption SET → `push()`. |
| turn_manager.py | 4 | Replace `_pop_dialogue_queue()` call (line 160) with `world.dialogue_manager.promote_if_empty()`. Delete `_DIALOGUE_TYPE_PRIORITY` dict + `_pop_dialogue_queue()` method (lines 245-272). |
| vassal.py | 5 | Queue append → `push()`. Queue filter → `remove_matching()`. Clear → `pop()`. |
| ai_diplomacy.py | 4 | Queue append → `push()` (auto-queues when occupied). READs stay. |
| coalition.py | 3 | Clear → `pop()`. Queue filter → `remove_matching()`. |
| executor.py | 4 | Clear → `pop()`. READs stay. |
| diplomacy.py | 2 | Queue append → `push()`. READ stays. |

**Step 2 — Consolidate timeout logic:**
- Replace `world_state.py:4048-4068` (non-blocking + blocking safety valve) with:
  ```python
  cleared = self._dialogue_manager.clear_stale(self.current_turn)
  if cleared:
      self.incoming_proposal_popup = None  # Paired clearing
  ```
- Verify characterization tests for timing still pass

**Step 3 — Lock down properties:**
- **PREREQUISITE:** `grep -c 'pending_diplomatic_dialogue\s*=' backend/` returns 0 (no setter calls remain in production code)
- Remove `pending_diplomatic_dialogue` setter
- Remove `pending_dialogue_queue` property entirely
- Keep `pending_diplomatic_dialogue` getter (read-only, returns `peek()`) — ~35 READ sites unchanged
- `dialogue_manager` property already exposed from 12A

**Step 4 — Update test files:**
- ~28 test files, ~193 setter operations to migrate
- Mechanical replacements:
  - `world.pending_diplomatic_dialogue = {...}` → `world.dialogue_manager.replace({...})` (test setup = replace, not push)
  - `world.pending_diplomatic_dialogue = None` → `world.dialogue_manager.pop()`
  - `world.pending_dialogue_queue.append(...)` → `world.dialogue_manager.push(...)`
  - `world.pending_dialogue_queue = [...]` → `world.dialogue_manager._queue = [...]` (direct setup in tests is acceptable)
- Consider a regex-assist script for bulk replacement

**Commit gate:** Full suite green. `grep 'pending_diplomatic_dialogue\s*=' backend/` returns 0. `grep 'pending_diplomatic_dialogue\s*=' tests/` returns 0. Property setter removed.

---

## Edge Cases

### In-Place Modification
Some code modifies the dialogue dict after reading:
```python
dialogue = world.pending_diplomatic_dialogue
dialogue["talleyrand_text"] = "updated"
```
This works because `peek()` and the property getter return the dict reference. Mutations are visible through the manager. **No change needed.**

### Paired Popup Clearing
5 sites manually clear `incoming_proposal_popup` when clearing dialogue (diplomatic_executor ×2, world_state ×2, executor ×1). During 12B, these stay inline alongside `pop()` calls. In 12C, `clear_stale()` handles the advance_turn case with paired clearing. For manual `pop()` calls, the caller remains responsible for clearing the popup (same as current — no regression). `remove_matching()` also does NOT clear paired popups — matches existing behavior in coalition.py and vassal.py.

**Future consideration:** A `resolve_dialogue()` convenience method on WorldState that does `pop() + clear popup` could eliminate this scattering, but it's not in scope for R12.

### Queue During Advance Turn
Multiple systems (dispatch, vassal, ai_diplomacy, coalition) can append dialogues during advance_turn. With `push()`, these auto-queue if a dialogue is already active. After `clear_stale()` auto-promotes (via `pop()`), items pushed later in the same advance_turn queue behind the promoted item. This is a minor timing change from current behavior (where promotion happens later via `_pop_dialogue_queue()`). Characterization tests pin which dialogue surfaces in this scenario.

### Turn-Start Queue Drain
After 12C removes `_pop_dialogue_queue()`, the replacement is `world.dialogue_manager.promote_if_empty()` at the same call site. This handles the case where queue items exist from a prior turn but current is None (e.g., non-blocking dialogue expired, items queued but never promoted). Without this call, those items would never surface.

### Legacy Save Format
Old saves have `pending_diplomatic_dialogue` and `pending_dialogue_queue` as top-level keys. `from_dict()` detects the format and loads into manager with `deepcopy`. New saves use `dialogue_manager` key. **Backward compatible.**

### Pre-Existing Overwrite Bug
`world_state.py:4341` (`_process_proposal_in_transit`) runs BEFORE stale clearing (line 4048) during advance_turn. If a blocking dialogue exists, the counter-offer overwrites it silently. Converting to `push()` in 12C fixes this — the counter-offer will queue instead. A characterization test pins the current (buggy) behavior before migration.

### Cheat Commands
`executor.py:6143` clears dialogue before post-objection execution. This becomes `world.dialogue_manager.pop()`. Cheat bypass guards in `main.py:681` and `executor.py:783` are READ-only — no change.

---

## Validation Criteria

### Per-Phase Gates
- **12A:** 7,707+ tests green. Changes only in `dialogue_manager.py` + `world_state.py` + new test file.
- **12B:** 7,707+ tests green. `grep -c 'pending_diplomatic_dialogue\s*=' backend/commands/diplomatic_executor.py` returns 0.
- **12C:** 7,707+ tests green. `grep 'pending_diplomatic_dialogue\s*=' backend/` returns 0. `grep 'pending_diplomatic_dialogue\s*=' tests/` returns 0. Property setter removed. Duplicate auto-pop deleted. `_pop_dialogue_queue` replaced with `promote_if_empty()`.

### Behavioral Invariants (must hold across all phases)
1. Dialogue set when slot empty → becomes current
2. Dialogue set when slot occupied → queues (not lost)
3. Dialogue cleared → next highest-priority auto-promotes
4. Non-blocking dialogue auto-dismisses after 1 turn
5. Blocking dialogue force-clears after 2 turns
6. Queue respects priority: alliance_paradox > vassal > sabotage > redemption > proposal
7. Queue capped at 20
8. Save/load round-trip preserves dialogue + queue state (including nested dicts)
9. Blocking dialogue prevents end-turn
10. Cheat commands bypass dialogue guard

### Phase Boundary Safety
- **12A is independently shippable.** Zero behavior change.
- **12B is independently shippable.** Transparent setter keeps unmigrated files working.
- **12C steps must be done in order.** Step 3 (lock down) requires Step 1 (migrate all backend files) and Step 4 (migrate tests) complete. DO NOT remove property setter until grep confirms zero setter calls remain.

---

## Files

### Created
- `backend/models/dialogue_manager.py` (~150 lines)
- `tests/test_dialogue_manager.py` (~400 lines: characterization + unit)

### Modified
- `backend/models/world_state.py` — DialogueManager integration, properties, serialization
- `backend/commands/diplomatic_executor.py` — ~74 ops migrated (12B)
- `backend/main.py` — duplicate auto-pop removed (12C)
- `backend/game_logic/turn_manager.py` — `_pop_dialogue_queue` → `promote_if_empty()` (12C)
- `backend/game_logic/dispatch.py` — 5 ops migrated (12C)
- `backend/game_logic/vassal.py` — 5 ops migrated (12C)
- `backend/game_logic/ai_diplomacy.py` — 4 ops migrated (12C)
- `backend/game_logic/coalition.py` — 3 ops migrated (12C)
- `backend/commands/executor.py` — 4 ops migrated (12C)
- `backend/game_logic/diplomacy.py` — 2 ops migrated (12C)
- ~28 test files — ~193 setter calls updated (12C Step 4)
- `docs/SAVE_FORMAT_REFERENCE.md` — new dialogue_manager format
