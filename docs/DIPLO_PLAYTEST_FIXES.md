# Diplomacy Playtest Fix Plan

**Created:** April 4, 2026
**Source:** Manual diplomacy playtesting (April 2026)
**Priority:** Blocks Diplomacy Refinement Phase 5 and all further diplomacy work.

> **Sequencing:** UI testing and playtest fixes come BEFORE any Diplomacy Refinement Phase 5 work. The refinement items assume a working UI — these bugs prove the UI has gaps that must be closed first.

---

## Phase 1: Two bugs, one session

| ID | Title | Severity | Scope |
|----|-------|----------|-------|
| DPF-1 | AI-AI relations missing from Diplomatic Ledger | Major | Backend + Godot |
| DPF-2 | Mission cancel UI missing + no progress tracking | Major | Backend + Godot |

**Estimated scope:** ~80 lines backend, ~40 lines Godot, ~15 tests.

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
- Import `get_relation_descriptor` at module level (currently inline at line 251)

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

Update the `_render_nations()` AI-AI relations block to show relation value + descriptor alongside the state label.

Before: `Austria [WAR]`
After: `Austria [WAR] -45 (Hostile)`

Color the relation value like the player relation display (green if positive, red if negative).

### Tests (5)

1. `test_ai_relations_include_relation_value` — entries have `relation` and `relation_descriptor`
2. `test_ai_relations_no_fog_gate` — AI-AI relations visible even with UNKNOWN visibility
3. `test_ai_relations_negative_descriptor` — negative relation shows correct descriptor
4. `test_ai_relations_default_zero` — missing relation key defaults to 0
5. `test_ai_relations_int_wrapped` — all relation values are int (Godot safety)

---

## DPF-2: Mission Cancel + Progress Tracking

### Problem

DP-per-turn missions (IMPROVE_RELATIONS, COURT_NATION, UNDERMINE_ALLIANCE, etc.) have three gaps:

1. **No cancel UI.** The only way to cancel is typing "Talleyrand, cancel mission" in the terminal. There is no button or hint this is possible. The Diplomacy Wizard (F1) shows mission actions but no cancel option.
2. **No progress tracking.** Player cannot see cumulative effect of the mission (e.g., "Relations improved +16 over 3 turns"). The `active_diplomatic_mission` dict tracks `turns_active` but not `started_turn` or `initial_relation`.
3. **Ledger Tab 4 shows duration but not delta.** Shows "Duration: 3 turns" but not "Relations: -30 → -14".

### Design

**Cancel goes in the F1 Diplomacy Wizard** (not the Ledger):
- Ledger stays read-only (consistent — it's an information screen)
- Wizard is the action menu — cancel belongs with other actions
- When player opens F1 → selects the nation with an active mission → sees a "Cancel Mission" action in the list alongside other diplomatic actions
- Cancel is 0 DP cost (per spec §4b)

**Progress tracking goes in both places:**
- **Ledger Tab 4:** Shows relation delta since mission start ("Relations: -30 → -14, +16 over 3 turns")
- **F1 Wizard Step 1:** Already shows `[MISSION]` tag — no change needed
- **F1 Wizard Step 2:** The cancel action button shows enough context: "Cancel Mission: Improve Relations (+16 over 3 turns)"

### Implementation

**Step 1: Backend — Track mission start state**

File: `backend/commands/diplomatic_executor.py` (mission creation in `_execute_diplomatic_mission`)

When creating the `active_diplomatic_mission` dict, add two new fields:
```python
"started_turn": world.current_turn,
"initial_relation": world.nation_relations.get(
    world._make_diplo_key(player, mission_target), 0
) or 0,
```

These are stored inside the existing `active_diplomatic_mission` dict, which is already serialized as-is in `world_state.py to_dict()/from_dict()`. No new serialization code needed — dict keys are passthrough. Old saves with active missions will have these fields missing; use `.get("started_turn", None)` defensively.

**Step 2: Backend — Add cancel action to wizard**

File: `backend/game_logic/diplomacy.py` (`get_available_diplomatic_actions`)

When building the actions list, check if `world.active_diplomatic_mission` exists and targets this nation. If so, add:
```python
{
    "action": "cancel_mission",
    "display_name": "Cancel Mission",
    "dp_cost": 0,
    "gold_cost": 0,
    "available": True,
    "disabled_reason": "",
    "effect_text": f"Cancel {mission_type.replace('_', ' ').title()} mission",
    "likelihood": "",
}
```

Also include progress info in the action for the wizard to display:
```python
"mission_progress": {
    "type": mission_type,
    "target": mission_target,
    "turns_active": turns_active,
    "relation_delta": current_relation - initial_relation,
}
```

**Step 3: Backend — Add progress data to ledger**

File: `backend/game_logic/diplomatic_ledger.py` (`_build_talleyrand`)

In the `active_mission` dict, add:
```python
"started_turn": int(mission.get("started_turn") or 0),
"initial_relation": int(mission.get("initial_relation") or 0),
"current_relation": int(current_relation),
"relation_delta": int(current_relation - initial_relation),
```

Where `current_relation` is read from `world.nation_relations` for the player-target pair.

**Step 4: Godot — Wire cancel in wizard**

File: `godot-client/project-sovereign/scripts/diplomacy_wizard.gd`

Add to `_build_command()`:
```gdscript
"cancel_mission":
    return "cancel mission with " + nation
```

Verify the mock parser in `llm_client.py` handles "cancel mission" — it may need a keyword entry to route to `diplomatic_mission` with `mission_type: "CANCEL"`. Check and add if missing.

**Step 5: Godot — Show progress in Ledger Tab 4**

File: `godot-client/project-sovereign/scripts/diplomatic_ledger.gd` (`_render_talleyrand`)

After mission type/target/duration line, add progress display:
```
Relations with Austria: -30 → -14 (+16 over 3 turns)
```

Use green for positive delta, red for negative. Handle missing `initial_relation` (old saves) by showing "N/A".

### Parser Verification

The mock parser in `llm_client.py` needs to handle "cancel mission" distinctly from strategic "cancel" (which cancels MOVE_TO/PURSUE/HOLD/SUPPORT orders). Check the keyword order:
- "cancel mission" should match before bare "cancel"
- Route to `{"action": "diplomatic_mission", "mission_type": "CANCEL", "target_nation": extracted_nation}`

### Tests (10)

1. `test_mission_tracks_started_turn` — field present at creation
2. `test_mission_tracks_initial_relation` — field present at creation with correct value
3. `test_ledger_shows_relation_delta` — `relation_delta` computed correctly
4. `test_cancel_action_in_wizard_when_mission_active` — cancel appears in action list
5. `test_cancel_action_absent_without_mission` — no cancel when no active mission
6. `test_cancel_action_absent_for_wrong_nation` — cancel only for mission target nation
7. `test_cancel_action_zero_dp` — dp_cost is 0
8. `test_cancel_command_parses_correctly` — mock parser routes "cancel mission with Austria"
9. `test_mission_progress_survives_save_load` — started_turn + initial_relation round-trip
10. `test_ledger_handles_missing_initial_relation` — old save without field shows gracefully

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| "cancel mission" keyword collides with strategic "cancel" in parser | Medium | Check keyword order in mock parser; "cancel mission" must match before bare "cancel" |
| Old saves with active missions lack new fields | Low | `.get("started_turn", None)` — Godot shows "N/A" if missing |
| `get_relation_descriptor` circular import at module level | Low | Already imported inline at line 251; verify no circular dep when moved to top |
| Cancel from wizard while dialogue is pending | Low | Wizard already checks `dialogue_pending` and closes if true (line 211) |

---

## Files Touched Summary

| File | Changes |
|------|---------|
| `backend/game_logic/diplomatic_ledger.py` | DPF-1: remove fog gate, add relation fields. DPF-2: add progress fields to mission |
| `godot-client/.../diplomatic_ledger.gd` | DPF-1: render relation values. DPF-2: render progress delta |
| `backend/commands/diplomatic_executor.py` | DPF-2: add started_turn + initial_relation to mission dict |
| `backend/game_logic/diplomacy.py` | DPF-2: add cancel_mission action to wizard action list |
| `godot-client/.../diplomacy_wizard.gd` | DPF-2: add cancel_mission to _build_command() |
| `backend/ai/llm_client.py` | DPF-2: verify/add "cancel mission" keyword (if needed) |
| `tests/test_diplo_playtest_fixes.py` | New test file, ~15 tests |
