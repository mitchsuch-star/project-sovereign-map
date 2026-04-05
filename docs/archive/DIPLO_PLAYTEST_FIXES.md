# Diplomacy Playtest Fix Plan

**Created:** April 4, 2026
**Source:** Manual diplomacy playtesting (April 2026)
**Priority:** Blocks Diplomacy Refinement Phase 5 and all further diplomacy work.

> **Sequencing:** UI testing and playtest fixes come BEFORE any Diplomacy Refinement Phase 5 work. The refinement items assume a working UI — these bugs prove the UI has gaps that must be closed first.

---

## Phase 1: Three bugs, one session

| ID | Title | Severity | Scope |
|----|-------|----------|-------|
| DPF-1 | AI-AI relations missing from Diplomatic Ledger | Major | Backend + Godot |
| DPF-2 | Mission cancel UI missing + no progress tracking | Major | Backend + Godot (parser, wizard, ledger) |
| DPF-3 | Ledger "paused" status display broken (wrong key) | Minor | Godot |

**Estimated scope:** ~100 lines backend, ~60 lines Godot, ~20 tests.

---

## DPF-1: AI-AI Relations Incomplete

### Problem

The Diplomatic Ledger Tab 1 (Nations) shows France's relationship with each nation, but AI-AI relations only show diplomatic STATE (WAR, ALLIANCE, etc.) — not the numeric relation value or descriptor. The `nation_relations` dict tracks all pairs and the `ai_relations` field already exists in both backend and Godot, but only contains `nation` and `state`.

Additionally, the existing code fog-gates AI-AI relations behind PARTIAL+ visibility on BOTH nations in the pair. This is historically inaccurate — in the Napoleonic era, diplomatic relationships between nations were public knowledge. Ambassadors reported openly, treaties were announced formally, wars were declared publicly. Any competent diplomatic corps (i.e., Talleyrand) would know the state of European affairs regardless of military visibility.

### Design Decision: No Fog on Diplomatic Relations

- **Diplomatic states** (WAR, ALLIANCE, PEACE, etc.): Always visible. Public facts.
- **Relation values** (numeric -100 to +100): Always visible. Represents court gossip, ambassador reports, and general sentiment — information a diplomatic corps tracks as a matter of course.
- **Remove the fog gate** from `ai_relations` in `diplomatic_ledger.py` (lines 200-212).
- If secret treaties are ever added (future feature), those would have their own separate fog rules.

### Implementation

**File 1: `backend/game_logic/diplomatic_ledger.py` (lines 198-218)**

Current code builds `ai_relations` with fog gating and only includes `nation` + `state`. Change to:
- Remove fog visibility checks (the `nation_vis_priority >= partial_priority` guard)
- Add `relation` (int) and `relation_descriptor` (string) to each entry
- Read `nation_relations` for the AI-AI pair key
- Import `get_relation_descriptor` at module level (currently inline at line 251; verify no circular dependency — `diplomatic_ledger.py` already imports from `diplomacy.py` at file level, so this should be safe)

Before:
```python
ai_relations = []
nation_vis = _get_nation_visibility(nation, world)
nation_vis_priority = VISIBILITY_PRIORITY.get(nation_vis, 0)
partial_priority = VISIBILITY_PRIORITY.get(PARTIAL, 3)

for other_ai in all_nations:
    if other_ai == nation:
        continue
    other_vis = _get_nation_visibility(other_ai, world)
    other_vis_priority = VISIBILITY_PRIORITY.get(other_vis, 0)

    if nation_vis_priority >= partial_priority and other_vis_priority >= partial_priority:
        ai_diplo_key = world._make_diplo_key(nation, other_ai)
        ai_state = world.diplomatic_states.get(ai_diplo_key, "PEACE")
        ai_relations.append({
            "nation": other_ai,
            "state": ai_state,
        })
```

After:
```python
ai_relations = []
for other_ai in all_nations:
    if other_ai == nation:
        continue
    ai_diplo_key = world._make_diplo_key(nation, other_ai)
    ai_state = world.diplomatic_states.get(ai_diplo_key, "PEACE")
    ai_relation_value = world.nation_relations.get(ai_diplo_key, 0) or 0
    ai_relations.append({
        "nation": other_ai,
        "state": ai_state,
        "relation": int(ai_relation_value),
        "relation_descriptor": get_relation_descriptor(ai_relation_value),
    })
```

**File 2: `godot-client/project-sovereign/scripts/diplomatic_ledger.gd` (lines 271-287)**

Update the `_render_nations()` AI-AI relations block to show relation descriptor + value alongside the state label.

Before: `Austria [WAR]`
After: `Austria [WAR] — Hostile (-45)`

Descriptor-first, number as supplement. Color the descriptor (green if positive, red if negative, grey if zero). This keeps immersion while still giving the player precision.

### Tests (5)

1. `test_ai_relations_include_relation_value` — entries have `relation` and `relation_descriptor`
2. `test_ai_relations_no_fog_gate` — AI-AI relations visible even with UNKNOWN visibility
3. `test_ai_relations_negative_descriptor` — negative relation shows correct descriptor (e.g., "Hostile")
4. `test_ai_relations_default_zero` — missing relation key defaults to 0
5. `test_ai_relations_int_wrapped` — all relation values are int (Godot safety)

---

## DPF-2: Mission Cancel + Progress Tracking

### Problem

DP-per-turn missions (IMPROVE_RELATIONS, COURT_NATION, UNDERMINE_ALLIANCE, etc.) have three gaps:

1. **No cancel UI.** The only way to cancel is typing "Talleyrand, cancel mission" in the terminal. There is no button or hint this is possible. The Diplomacy Wizard (F1) shows mission actions but no cancel option.
2. **No progress tracking.** Player cannot see cumulative effect of the mission (e.g., "Austrian sentiment warming — from Hostile to Cold"). The `active_diplomatic_mission` dict tracks `turns_active` but not `started_turn` or `initial_relation`.
3. **Ledger Tab 4 shows duration but not delta.** Shows "Duration: 3 turns" but not the relation change.

### Design: Cancel Goes in the F1 Diplomacy Wizard

**Why wizard, not ledger:**
- Ledger stays read-only (consistent — it's an information screen)
- Wizard is the action menu — cancel belongs with other actions
- Cancel is mission-specific: player sees WHAT they are cancelling ("Cancel: Improve Relations with Austria, Friendly → Neutral, +16 over 3 turns") before confirming

**Wizard cancel flow (full trace):**

```
Player presses F1
  → Step 1: Nation list. Nations with active mission show [MISSION] tag (existing)
  → Player selects the nation that has the active mission
  → Step 2: Action list for that nation
    → Normal mission actions greyed out ("Mission already active") — existing behavior
    → NEW: "Cancel Mission" action appears at TOP of mission section
      → Shows: mission type, relation progress, turns active
      → 0 DP cost
  → Player clicks "Cancel Mission"
  → _build_command() → "Talleyrand, cancel mission with {nation}"
  → Sent to /command endpoint
  → Mock parser: "Talleyrand" detected → _parse_diplomatic_command()
    → extract_mission_type() matches "cancel mission" → returns "CANCEL"
    → action = "diplomatic_mission", mission_type = "CANCEL"
  → Executor: _execute_diplomatic_mission(mission_type="CANCEL")
    → Clears world.active_diplomatic_mission = None
    → Sets world.talleyrand_state = "IDLE"
  → Response: "Talleyrand's mission to Austria has been cancelled."
```

**Critical routing detail:** The wizard command string MUST include "Talleyrand" as a prefix. Without it, "cancel mission with Austria" hits the mock parser's `"cancel "` substring match at `llm_client.py:642` and routes to strategic cancel (MOVE_TO/PURSUE/HOLD cancel). The `"Talleyrand"` prefix triggers `_parse_diplomatic_command()` at line 530, which calls `extract_mission_type()` — this function already handles "cancel mission" at `diplomatic_dialogue.py:186` and returns `"CANCEL"`.

**Existing executor handler:** `_execute_diplomatic_mission` at `diplomatic_executor.py:226` already handles `mission_type == "CANCEL"`. No executor changes needed for the cancel action itself.

### Implementation

**Step 1: Backend — Track mission start state**

File: `backend/commands/diplomatic_executor.py` (mission creation in `_execute_diplomatic_mission`)

When creating the `active_diplomatic_mission` dict, add two new fields:
```python
"started_turn": world.current_turn,
"initial_relation": int(world.nation_relations.get(
    world._make_diplo_key(world.player_nation, mission_target), 0
) or 0),
```

These are stored inside the existing `active_diplomatic_mission` dict, which is already serialized as-is in `world_state.py to_dict()/from_dict()`. No new serialization code needed — dict keys are passthrough. Old saves with active missions will have these fields missing; use `.get("started_turn", None)` defensively.

**Step 2: Backend — Add cancel action to wizard action list**

File: `backend/game_logic/diplomacy.py` (`get_available_diplomatic_actions`)

The cancel action must be added **outside** the `_mission_action()` helper. That helper marks ALL mission actions as unavailable when `active_mission is not None` (line 2625). Cancel is the opposite — only available WHEN a mission is active AND targets this nation.

After the mission action block, add:
```python
# Cancel mission — only if active mission targets THIS nation
active_mission = getattr(world, 'active_diplomatic_mission', None)
if active_mission and active_mission.get("target") == target_nation:
    initial = int(active_mission.get("initial_relation") or 0)
    current_rel = int(world.nation_relations.get(
        world._make_diplo_key(world.player_nation, target_nation), 0
    ) or 0)
    delta = current_rel - initial
    turns = int(active_mission.get("turns_active") or 0)
    mission_type_raw = active_mission.get("type", "")

    # Descriptor-based progress text for immersion
    from backend.game_logic.diplomacy import get_relation_descriptor
    initial_desc = get_relation_descriptor(initial)
    current_desc = get_relation_descriptor(current_rel)

    if initial_desc != current_desc:
        progress_text = f"{initial_desc} → {current_desc} ({'+' if delta >= 0 else ''}{delta}, {turns} turns)"
    else:
        progress_text = f"{current_desc} ({'+' if delta >= 0 else ''}{delta} over {turns} turns)"

    actions.append({
        "action": "cancel_mission",
        "display_name": f"Cancel: {mission_type_raw.replace('_', ' ').title()}",
        "dp_cost": 0,
        "gold_cost": 0,
        "available": True,
        "disabled_reason": "",
        "effect_text": progress_text,
        "likelihood": "",
    })
```

**Step 3: Backend — Add progress data to ledger**

File: `backend/game_logic/diplomatic_ledger.py` (`_build_talleyrand`)

In the `active_mission` dict (around line 580), add progress fields:
```python
"started_turn": int(mission.get("started_turn") or 0),
"initial_relation": int(mission.get("initial_relation") or 0),
"current_relation": int(current_relation),
"relation_delta": int(current_relation - initial_relation),
"initial_descriptor": get_relation_descriptor(initial_relation),
"current_descriptor": get_relation_descriptor(current_relation),
```

Where `current_relation` is read from `world.nation_relations` for the player-target pair. `initial_relation` is `.get("initial_relation") or 0` from the mission dict.

**Step 4: Godot — Wire cancel in wizard**

File: `godot-client/project-sovereign/scripts/diplomacy_wizard.gd`

Add to `_build_command()`:
```gdscript
"cancel_mission":
    return "Talleyrand, cancel mission with " + nation
```

The `"Talleyrand, "` prefix is **mandatory** — it routes through `_parse_diplomatic_command()` → `extract_mission_type()` → `"CANCEL"` → `_execute_diplomatic_mission`. Without it, the bare `"cancel "` substring match in the mock parser routes to strategic order cancel.

**Step 5: Godot — Show progress in Ledger Tab 4**

File: `godot-client/project-sovereign/scripts/diplomatic_ledger.gd` (`_render_talleyrand`)

Replace the current mission duration line (around line 591) with descriptor-based progress:
```
Improve Relations → Austria
  Wary → Neutral (+16 over 3 turns)
  Status: Active, Cost: 1 DP/turn
  Completes in 2 turn(s)
```

Use `initial_descriptor` and `current_descriptor` from backend. Color the arrow green if `relation_delta > 0`, red if negative. If `initial_relation` is missing (old save), show "Progress: N/A (mission predates tracking)".

### Parser Verification

No parser changes needed. The routing already works end-to-end:

1. Wizard emits `"Talleyrand, cancel mission with Austria"`
2. Mock parser detects `"talleyrand"` at `llm_client.py:527` → calls `_parse_diplomatic_command()`
3. `_parse_diplomatic_command()` calls `extract_mission_type()` at `diplomatic_dialogue.py:186`
4. `extract_mission_type()` matches `"cancel mission"` → returns `"CANCEL"`
5. Back in `_parse_diplomatic_command()`: `mission_type` is truthy → `action = "diplomatic_mission"` (line 1018)
6. Executor dispatches to `_execute_diplomatic_mission(mission_type="CANCEL")` at `diplomatic_executor.py:226`
7. Existing handler clears mission and returns success message

**No changes to `llm_client.py` keyword lists or ordering required.** The "Talleyrand" prefix bypasses the general action matching entirely.

### Tests (12)

1. `test_mission_tracks_started_turn` — field present at creation
2. `test_mission_tracks_initial_relation` — field present at creation with correct value
3. `test_mission_initial_relation_int_wrapped` — initial_relation is int (Godot safety)
4. `test_ledger_shows_relation_delta` — `relation_delta` computed correctly
5. `test_ledger_shows_descriptors` — `initial_descriptor` and `current_descriptor` present
6. `test_cancel_action_in_wizard_when_mission_active` — cancel appears in action list for target nation
7. `test_cancel_action_absent_without_mission` — no cancel when no active mission
8. `test_cancel_action_absent_for_wrong_nation` — cancel only for mission target nation, not other nations
9. `test_cancel_action_zero_dp` — dp_cost is 0
10. `test_cancel_action_shows_progress` — effect_text includes descriptor-based progress
11. `test_mission_progress_survives_save_load` — started_turn + initial_relation round-trip
12. `test_ledger_handles_missing_initial_relation` — old save without field shows gracefully

---

## DPF-3: Ledger Paused Status Display (Pre-existing Bug)

### Problem

`diplomatic_ledger.gd:587` reads `mission.get("progress", false)` but the backend sends the key `"paused"`. The paused/active status display has been silently broken — missions always show "Active" even when paused.

### Fix

File: `godot-client/project-sovereign/scripts/diplomatic_ledger.gd` (line 587)

Before:
```gdscript
var m_paused = mission.get("progress", false)
```

After:
```gdscript
var m_paused = mission.get("paused", false)
```

### Tests (1)

1. `test_ledger_mission_paused_key` — verify backend `active_mission` dict uses `"paused"` key (backend-side confirmation that the key name is correct)

---

## Immersion Notes

### Relation Display Philosophy

Raw numbers (`+5 relation per turn`, `Relations: -30 → -14`) break immersion. The game has `get_relation_descriptor()` which maps values to thematic labels: Loyal, Friendly, Neutral, Wary, Hostile. All player-facing relation displays should use **descriptors first, numbers as supplement**:

| Context | Display Format |
|---------|---------------|
| Ledger Tab 1 AI-AI | `Austria [WAR] — Hostile (-45)` |
| Ledger Tab 4 mission progress | `Wary → Neutral (+16 over 3 turns)` |
| Wizard cancel button | `Cancel: Improve Relations (Wary → Neutral, +16, 3 turns)` |
| Mission effect text (existing) | `+5 relation per turn` — acceptable here, this is the mechanical tooltip |

### Mission Type Display

`diplomatic_ledger.gd:591` uses `m_type.replace("_", " ").capitalize()` which produces "Improve relations" from "IMPROVE_RELATIONS". This is acceptable for now — these are the same strings the wizard uses and they read naturally. If `display_names.py` gets diplomatic mission entries later, switch to those.

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Wizard cancel command missing "Talleyrand" prefix → routes to strategic cancel | Critical | `_build_command()` MUST emit `"Talleyrand, cancel mission with {nation}"`. Verified: "Talleyrand" triggers `_parse_diplomatic_command()` which calls `extract_mission_type()` which already returns `"CANCEL"` |
| Cancel action blocked by `_mission_action()` "Mission already active" guard | Major | Cancel is appended directly to `actions` list, NOT through `_mission_action()` helper |
| Old saves with active missions lack `started_turn`/`initial_relation` | Low | `.get("started_turn", None)` — Godot shows "N/A" if missing. No crash path |
| `get_relation_descriptor` circular import at module level in `diplomatic_ledger.py` | Low | `diplomatic_ledger.py` already imports from `diplomacy.py` at file level; adding one more function to the import is safe |
| Cancel shows for wrong nation (mission targets Austria, player selects Prussia) | Low | Guard: `active_mission.get("target") == target_nation` — cancel only appears for the mission's target nation |

---

## Files Touched Summary

| File | Changes |
|------|---------|
| `backend/game_logic/diplomatic_ledger.py` | DPF-1: remove fog gate, add relation + descriptor fields. DPF-2: add progress fields to mission. DPF-3: N/A (backend key is correct) |
| `godot-client/.../diplomatic_ledger.gd` | DPF-1: render relation descriptors. DPF-2: render descriptor-based progress. DPF-3: fix `"progress"` → `"paused"` key |
| `backend/commands/diplomatic_executor.py` | DPF-2: add `started_turn` + `initial_relation` to mission dict at creation |
| `backend/game_logic/diplomacy.py` | DPF-2: add `cancel_mission` action to wizard action list (outside `_mission_action()` helper) |
| `godot-client/.../diplomacy_wizard.gd` | DPF-2: add `cancel_mission` → `"Talleyrand, cancel mission with {nation}"` to `_build_command()` |
| `tests/test_diplo_playtest_fixes.py` | New test file, ~18 tests |

## End-to-End Flow Verification Checklist

Before marking DPF-2 complete, manually verify:

- [ ] F1 → select nation with active mission → "Cancel: Improve Relations" action visible
- [ ] F1 → select nation WITHOUT active mission → no cancel action
- [ ] F1 → select DIFFERENT nation than mission target → no cancel action
- [ ] Click cancel → terminal shows `► Talleyrand, cancel mission with Austria`
- [ ] Response: "Talleyrand's mission to Austria has been cancelled."
- [ ] After cancel → Ledger Tab 4 shows "Idle — no active diplomatic mission"
- [ ] After cancel → F1 on same nation → mission actions available again (no longer greyed out)
- [ ] Ledger Tab 4 during active mission → shows descriptor progress (e.g., "Wary → Neutral")
- [ ] Type "Talleyrand, cancel mission" in terminal directly → still works (existing path)
- [ ] Type "cancel" in terminal (no Talleyrand) → cancels strategic order, NOT mission
