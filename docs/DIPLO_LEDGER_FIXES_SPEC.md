# Diplomatic Ledger Fixes Spec

**Date:** 2026-04-04
**Scope:** 3 bugs/improvements found during playtest
**Files affected:** `diplomatic_ledger.py`, `diplomatic_executor.py`, `diplomacy.py`, `diplomatic_dialogue.py`, `diplomatic_ledger.gd`

---

## DLF-1: Vassalizable Icon Shows Ineligible Nations

**Bug:** The vassalizable icon in the Nations tab shows for any nation with `relation < -10 OR at_war`, ignoring whether the diplomatic state actually permits vassalization. Result: almost every nation shows the icon (since France typically has negative relations with most), while Saxony (friendly) does not — giving the misleading impression that vassalization is available when it isn't.

**Root cause:** `diplomatic_ledger.py:192` checks relation/war but not `VASSAL_MIN_STATES`.

**Fix:** Add `VASSAL_MIN_STATES` check to the eligibility condition:

```python
from backend.game_logic.diplomacy import VASSAL_MIN_STATES
vassal_eligible = (
    not is_vassal
    and (relation < -10 or at_war)
    and nation != player
    and diplomatic_state in VASSAL_MIN_STATES
)
```

**Files:** `backend/game_logic/diplomatic_ledger.py`
**Tests:** 1-2 tests verifying icon only shows when state is in VASSAL_MIN_STATES.

---

## DLF-2: UNDERMINE_ALLIANCE Mission Has No Effect

**Bug:** UNDERMINE_ALLIANCE mission accepts commands, deducts 2 DP/turn, shows in mission tracker, but the per-turn effect (-3 relation between target pair) is never applied. The processing in `diplomacy.py:1947` is a stub comment.

Additionally, the mission only stores a single `target` nation, but the spec requires targeting a *pair* of nations whose alliance should be weakened.

### Design: Conversational Target Selection

When the player initiates an UNDERMINE_ALLIANCE mission (via wizard or command), the flow is:

1. **Player selects UNDERMINE_ALLIANCE** targeting a nation (e.g., "Talleyrand, undermine Prussia")
2. **Backend looks up that nation's alliances** — finds all nations where the diplomatic state with the target is ALLIANCE or DEFENSIVE_ALLIANCE
3. **If multiple allies exist:** Push a dialogue choice — "Undermine Prussia's alliance with whom?" presenting a list of allied nations as numbered options
4. **If exactly one ally:** Auto-select that ally, skip the prompt
5. **If no allies:** Reject with message: "Prussia has no alliances to undermine, Sire."
6. **Mission created** with `target_pair: [nation_a, nation_b]` (sorted alphabetically for consistent diplo_key generation)

### Mission Storage

```python
world.active_diplomatic_mission = {
    "type": "UNDERMINE_ALLIANCE",
    "target": primary_nation,           # The nation the player targeted
    "target_pair": [nation_a, nation_b], # NEW: both nations in the alliance
    "turns_active": 0,
    "paused": False,
    "paused_turns": 0,
    "started_turn": int(current_turn),
    "initial_relation": int(relation_between_pair),  # Relation between the PAIR, not player-target
}
```

**Serialization:** `target_pair` is a list of 2 strings. Add to `to_dict`/`from_dict` via `.get("target_pair", [])`.

### Per-Turn Processing

In `_process_mission_effects()`, replace the stub at line 1947:

```python
# UNDERMINE_ALLIANCE: reduce relation between target pair
pair_change = effects.get("target_pair_relation_change")
if pair_change:
    target_pair = mission.get("target_pair", [])
    if len(target_pair) == 2:
        scaled = int(round(pair_change * multiplier))
        world.modify_nation_relation(target_pair[0], target_pair[1], scaled)

        # Check if alliance broke — auto-cancel if so
        pair_key = world._make_diplo_key(target_pair[0], target_pair[1])
        pair_state = world.diplomatic_states.get(pair_key, "PEACE")
        if pair_state not in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
            mission["completed"] = True
            world.talleyrand_state = "IDLE"
            events.append({
                "type": "diplomatic_mission_completed",
                "target": mission.get("target", ""),
                "mission_type": "UNDERMINE_ALLIANCE",
                "message": f"The alliance between {target_pair[0]} and {target_pair[1]} has fractured. Talleyrand's work is done.",
            })
        else:
            # Dispatch progress event
            pair_relation = world.nation_relations.get(pair_key, 0)
            from backend.game_logic.dispatch import queue_dispatch_event
            queue_dispatch_event(world, "diplomatic_mission_progress",
                                {"nation": mission.get("target", ""), "value": int(pair_relation)},
                                "player_mission")
```

### Mission Tracker Display

In `diplomatic_ledger.py`, the mission status section should show both target nations:

```
Mission: Undermine Alliance
Target: Prussia ↔ Austria
Effect: -3 relation between targets per turn
Progress: Friendly (15) → Wary (-5) [Δ-20]
```

The `initial_relation` and `current_relation` track the pair's relation, not player-target.

### Files

| File | Change |
|------|--------|
| `backend/commands/diplomatic_executor.py` | Add ally-selection dialogue for UNDERMINE_ALLIANCE in `start_mission` action |
| `backend/game_logic/diplomacy.py` | Replace stub with per-turn effect + auto-cancel |
| `backend/game_logic/diplomatic_ledger.py` | Update mission tracker to show pair |
| `backend/game_logic/diplomatic_dialogue.py` | No changes needed (keywords, cost, effects already defined) |

### Tests

- Mission creation stores `target_pair`
- Per-turn processing reduces pair relation by -3 (×skill multiplier)
- Auto-cancels when alliance breaks (state drops below DEFENSIVE_ALLIANCE)
- Rejects if target has no alliances
- Auto-selects if target has exactly one ally
- Dialogue prompt if target has multiple allies
- Mission tracker shows both nations

---

## DLF-3: AI-AI Relations Display Scaling

**Problem:** Each nation card in the Nations tab lists every other nation's relation as a comma-separated inline string. With 5 nations this is manageable (4 entries per card). With 15+ nations on a full Europe map, each card would have 14+ entries — an unreadable wall of text.

### Design: Significant Relations Only

Filter `ai_relations` to only show relations where the diplomatic state is notable:

**Show:** `WAR`, `ALLIANCE`, `DEFENSIVE_ALLIANCE`, `OPEN_BORDERS`, `NON_AGGRESSION`
**Hide:** `PEACE` (the default/uninteresting state)

This keeps the per-nation card structure intact and requires minimal code changes. Most nation pairs are at PEACE, so this dramatically reduces clutter.

### Backend Change

In `diplomatic_ledger.py`, filter the `ai_relations` list before appending:

```python
# Only include notable relations (not default PEACE)
NOTABLE_STATES = {"WAR", "ALLIANCE", "DEFENSIVE_ALLIANCE", "OPEN_BORDERS", "NON_AGGRESSION"}
if ai_state in NOTABLE_STATES:
    ai_relations.append({...})
```

### Frontend Change

In `diplomatic_ledger.gd`, update the label from "AI Relations:" to "Notable Relations:" (or just "Relations:") and handle the empty case:

```gdscript
if ai_relations.size() > 0:
    # ... existing rendering ...
    bbcode += "  Relations: " + ...
else:
    bbcode += "  Relations: [color=#grey]At peace with all[/color]\n"
```

### Files

| File | Change |
|------|--------|
| `backend/game_logic/diplomatic_ledger.py` | Filter ai_relations to NOTABLE_STATES |
| `godot-client/.../diplomatic_ledger.gd` | Update label, add empty-state text |

### Tests

- Nations at PEACE are excluded from ai_relations
- Nations at WAR/ALLIANCE/etc. are included
- Empty ai_relations returns empty list (not omitted)

---

## Implementation Order

1. **DLF-1** (vassalizable icon) — 1 line backend + tests
2. **DLF-3** (relations filter) — small backend + Godot change + tests
3. **DLF-2** (undermine alliance) — largest: dialogue flow, mission storage, per-turn processing, tracker display, tests

**Estimated tests:** ~15-20 new tests across all three fixes.
