# Diplomatic Ledger Fixes Spec

**Date:** 2026-04-04 (updated 2026-04-05)
**Scope:** 8 bugs/improvements found during playtest + code audit
**Files affected:** `diplomatic_ledger.py`, `diplomatic_executor.py`, `diplomacy.py`, `diplomatic_dialogue.py`, `diplomatic_ledger.gd`, `ai_diplomacy.py`, `enemy_ai.py`

---

## DLF-1: Vassalizable Icon Shows Ineligible Nations

**Bug:** The vassalizable icon in the Nations tab shows for any nation with `relation < -10 OR at_war`, ignoring whether the diplomatic state actually permits vassalization. Result: almost every nation shows the icon (France typically has negative relations with most), while Saxony (friendly) does not — giving the misleading impression that vassalization is broadly available.

**Root cause:** `diplomatic_ledger.py:192` checks relation/war but not `VASSAL_MIN_STATES`. The actual proposal requires `VASSAL_MIN_STATES = {"WAR", "OPEN_BORDERS", "NON_AGGRESSION", "DEFENSIVE_ALLIANCE", "ALLIANCE"}` (defined in `diplomacy.py:77`).

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

Additionally, the mission only stores a single `target` nation, but the design requires targeting a *pair* of nations whose alliance should be weakened.

### Design: Conversational Target Selection

When the player initiates an UNDERMINE_ALLIANCE mission (via wizard or command), the flow is:

1. **Player selects UNDERMINE_ALLIANCE** targeting a nation (e.g., "Talleyrand, undermine Prussia")
2. **Backend looks up that nation's alliances** — finds all nations where the diplomatic state with the target is ALLIANCE or DEFENSIVE_ALLIANCE
3. **If multiple allies exist:** Use the existing `_build_*_step()` → `dialogue_manager.replace()` pattern to push a follow-up dialogue: "Undermine Prussia's alliance with whom?" presenting allied nations as numbered options
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

**Serialization:** `active_diplomatic_mission` is stored/loaded as a raw dict in `world_state.py` `to_dict()`/`from_dict()` — no special handling needed. The new `target_pair` key will serialize automatically. Older saves without the key load safely via `.get("target_pair", [])` in processing code.

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
| `backend/commands/diplomatic_executor.py` | Add ally-selection dialogue step for UNDERMINE_ALLIANCE in `start_mission` action, using existing `_build_*_step()` + `dialogue_manager.replace()` pattern |
| `backend/game_logic/diplomacy.py` | Replace stub with per-turn effect + auto-cancel |
| `backend/game_logic/diplomatic_ledger.py` | Update mission tracker to show pair |

### Tests

- Mission creation stores `target_pair`
- Per-turn processing reduces pair relation by -3 (×skill multiplier)
- Auto-cancels when alliance breaks (state drops below DEFENSIVE_ALLIANCE)
- Rejects if target has no alliances
- Auto-selects if target has exactly one ally
- Dialogue prompt if target has multiple allies
- Mission tracker shows both nations
- Save/load round-trip preserves `target_pair`

---

## DLF-3: AI-AI Relations Display Scaling

**Problem:** Each nation card in the Nations tab lists every other nation's relation as a comma-separated inline string. With 5 nations this is manageable (4 entries per card). With 15+ nations on a full Europe map, each card would have 14+ entries — an unreadable wall of text.

### Design: Significant Relations Only

Filter `ai_relations` to only show relations where the diplomatic state is notable:

**Show:** `WAR`, `ALLIANCE`, `DEFENSIVE_ALLIANCE`, `OPEN_BORDERS`, `NON_AGGRESSION`
**Hide:** `PEACE` (the default/uninteresting state)

At game start only 1 of 10 AI-AI pairs is NON_AGGRESSION (Austria|Britain), so this isn't overly inclusive. Over time, nations transition through these states naturally, and those transitions are exactly what the player cares about.

### Backend Change

In `diplomatic_ledger.py`, filter the `ai_relations` list before appending:

```python
# Only include notable relations (not default PEACE)
NOTABLE_STATES = {"WAR", "ALLIANCE", "DEFENSIVE_ALLIANCE", "OPEN_BORDERS", "NON_AGGRESSION"}
if ai_state in NOTABLE_STATES:
    ai_relations.append({...})
```

### Frontend Change

In `diplomatic_ledger.gd`, update the label from "AI Relations:" to "Relations:" and handle the empty case:

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

## DLF-4: COURT_NATION Blowback Is Stubbed

**Bug:** COURT_NATION costs 2 DP/turn (double IMPROVE_RELATIONS) because it's supposed to carry risk: a 20% chance per turn of -3 relation blowback. The blowback is defined in `MISSION_EFFECTS` but never processed — making COURT_NATION a strictly worse IMPROVE_RELATIONS (same +5/turn, double the cost, zero risk).

**Root cause:** `diplomacy.py:1948` — `"COURT_NATION undermine chance: stub"`. The `undermine_chance` and `undermine_amount` fields in `MISSION_EFFECTS` are never read during `_process_mission_effects()`.

**Design note on skill multiplier:** The existing skill multiplier (1.5x at skill 10, 0.75x at skill 4-6) applies only to `relation_change`, not to blowback. This is correct — high-skill Talleyrand gets better positive returns (+7.5 vs +5) while blowback stays fixed at -3. High skill = better risk/reward ratio, not more risk.

**Fix:** After the relation_change block in `_process_mission_effects()`, add blowback processing. The blowback amount is NOT scaled by skill multiplier (fixed penalty):

```python
# COURT_NATION blowback: chance of negative relation hit
undermine_chance = effects.get("undermine_chance", 0)
undermine_amount = effects.get("undermine_amount", 0)
if undermine_chance and undermine_amount:
    import random
    if random.random() < undermine_chance:
        # Blowback is a fixed penalty — NOT scaled by skill multiplier
        world.modify_nation_relation(player_nation, target, int(undermine_amount))
        events.append({
            "type": "diplomatic_mission_blowback",
            "target": target,
            "mission_type": mission_type,
            "message": f"Talleyrand's aggressive courting of {target} has caused a diplomatic incident. Relations damaged.",
        })
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "diplomatic_mission_blowback",
                            {"nation": target}, "player_mission")
```

**Files:** `backend/game_logic/diplomacy.py`
**Tests:**
- Blowback applies -3 (fixed, not scaled) when RNG triggers
- Blowback generates event + dispatch
- No blowback for non-COURT missions (e.g., IMPROVE_RELATIONS has no undermine_chance)
- Positive relation gain still scales with skill (verify +7.5 at skill 10)
- Mock random to test both trigger and non-trigger paths

---

## DLF-5: GATHER_INTEL Completes But Reveals Nothing

**Bug:** GATHER_INTEL auto-completes after 3 turns with "Talleyrand has completed his intelligence gathering on {target}" but returns zero information. The player spends 3 DP for a congratulatory message.

**Root cause:** `diplomacy.py:1945` — `"Stub: no intel revealed yet (Session 4+)"`. The duration-based completion works, but no payload is delivered.

### Design: Reveal Exact Army Strength

Diplomacy has no fog of war, so all diplomatic info is already visible. However, **military fog does apply to the diplomatic ledger's army strength display**. The ledger uses `_get_nation_visibility()` to fog-filter enemy troop numbers through 5 tiers:

| Visibility | Display |
|------------|---------|
| FULL | "23,847 men" (exact) |
| PARTIAL | "~25,000 men" (rounded to nearest 5k) |
| STALE | "Considerable" (qualitative band) |
| LAST_KNOWN | "Minor Force" (old band) |
| UNKNOWN | "Unknown" |

GATHER_INTEL should grant **temporary FULL visibility** on the target nation's army strength for a number of turns after completion, bypassing the fog filter.

### Implementation

**New field on WorldState:** `intel_grants: Dict[str, Dict]` — tracks active intel grants by nation.

```python
# Grant structure
self.intel_grants = {}  # Serialized in to_dict/from_dict
# Example: {"Prussia": {"visibility": "FULL", "expires_turn": 15}}
```

**On mission completion** (in `_process_mission_effects()`):
```python
if duration and mission.get("turns_active", 0) >= duration:
    # Existing completion logic...

    # Grant intel on target nation
    intel_grants = getattr(world, 'intel_grants', {})
    intel_grants[target] = {
        "visibility": "FULL",
        "granted_turn": int(world.current_turn),
        "expires_turn": int(world.current_turn + 5),  # 5 turns of visibility
    }
    world.intel_grants = intel_grants
```

**In `_get_nation_visibility()`** (diplomatic_ledger.py), check grants before regional visibility:
```python
# Check intel grants first
intel_grants = getattr(world, 'intel_grants', {})
grant = intel_grants.get(nation_name)
if grant and grant.get("expires_turn", 0) > world.current_turn:
    return grant.get("visibility", UNKNOWN)
# ... existing regional visibility logic ...
```

**In `advance_turn()`**, expire old grants:
```python
intel_grants = getattr(world, 'intel_grants', {})
world.intel_grants = {
    k: v for k, v in intel_grants.items()
    if v.get("expires_turn", 0) > world.current_turn
}
```

**Button/UI text:** The mission description should clearly state what it does. Update `MISSION_DESCRIPTIONS` and ledger effect text:
```python
MISSION_DESCRIPTIONS["GATHER_INTEL"] = "gather intelligence on"
# In _MISSION_EFFECT_TEXT:
"GATHER_INTEL": "Reveals exact army strength for 5 turns after completion (3 turn mission)",
```

### Serialization

Add `intel_grants` to `WorldState.to_dict()` and `from_dict()` with `.get("intel_grants", {})` default.

### Files

| File | Change |
|------|--------|
| `backend/game_logic/diplomacy.py` | Grant intel on mission completion |
| `backend/game_logic/diplomatic_ledger.py` | Check intel_grants in `_get_nation_visibility()` |
| `backend/game_logic/war_status.py` | Same `_get_nation_visibility()` check (if it has its own copy) |
| `backend/models/world_state.py` | Add `intel_grants` field, serialization, expiry in `advance_turn()` |
| `backend/game_logic/diplomatic_dialogue.py` | Update MISSION_DESCRIPTIONS text |

### Tests

- Mission completion grants FULL visibility on target nation
- Grant expires after 5 turns
- `_get_nation_visibility()` returns FULL when grant active
- `_get_nation_visibility()` falls through to regional visibility when grant expired
- Army strength shows exact numbers during grant period
- Save/load preserves intel_grants
- Multiple sequential GATHER_INTEL missions refresh the grant

---

## DLF-6: AI Doesn't Check Diplomatic State Before Move Selection

**Bug:** AI pathfinding in `enemy_ai.py` (P7 strategic movement) selects adjacent regions purely by distance to the nearest enemy. It never calls `can_enter_territory()` to check whether the AI nation has diplomatic permission to enter the region. The movement executor in `movement_executor.py:196` correctly rejects the illegal move, but the AI wastes its action for the turn.

This same gap exists in **AI retreat logic** (`_find_retreat_destination()` ~line 3770) — retreating AI marshals can attempt to retreat into diplomatically blocked regions.

With 5 nations and a small map this is minor. With 15+ nations and complex border arrangements, AI marshals will frequently get stuck or waste actions on impossible moves.

**Root cause:** `enemy_ai.py` P7 movement (aggressive ~line 3414, cautious ~line 3460, stagnation fallback ~line 3556) and retreat logic (`_find_retreat_destination` ~line 3770) filter for enemy occupation and visited regions but never check `can_enter_territory()`.

**Fix:** Add a diplomatic state check in all movement candidate loops:

```python
from backend.game_logic.diplomacy import can_enter_territory

for adj_name in marshal_region.adjacent_regions:
    adj_region = world.get_region(adj_name)
    # Skip regions we can't diplomatically enter
    if adj_region.controller and adj_region.controller != nation:
        if not can_enter_territory(world, nation, adj_region.controller):
            continue
    # ... existing distance/enemy checks ...
```

Apply to:
1. P7 aggressive path (~line 3414)
2. P7 cautious path (~line 3460)
3. P7 stagnation fallback (~line 3556)
4. `_find_retreat_destination()` (~line 3770) — both preferred and fallback loops

**Files:** `backend/ai/enemy_ai.py`
**Tests:**
- AI skips regions controlled by nations at PEACE
- AI can move through OPEN_BORDERS+ territories
- AI can move through WAR territories (for attack positioning)
- AI doesn't get stuck when surrounded by diplomatically blocked regions (falls through to HOLD)
- AI retreat doesn't target diplomatically blocked regions

---

## DLF-7: Eliminated Nations Included in War Cascades

**Bug:** `_process_war_cascade()` in `diplomacy.py:1182` iterates all nations without filtering eliminated ones (0 regions, 0 living marshals). Dead nations can be pulled into new wars via defensive cascade, creating phantom war states.

**Root cause:** `_is_nation_eliminated()` exists and is used in `process_ai_ai_diplomatic_phase()` but not in `_process_war_cascade()`.

**Fix:** Filter eliminated nations at the top of the cascade loop:

```python
for nation in all_nations:
    if nation in processed:
        continue
    if _is_nation_eliminated(world, nation):
        continue
    # ... existing cascade logic ...
```

**Files:** `backend/game_logic/diplomacy.py`
**Tests:**
- Eliminated nation is not pulled into defensive cascade
- Eliminated nation is not pulled into offensive cascade
- Non-eliminated nations still cascade normally

---

## DLF-8: Opportunistic Downgrade Doesn't Exclude VASSAL State

**Bug:** `_process_ai_ai_rivalry()` in `ai_diplomacy.py:1381` excludes PEACE/WAR/ARMISTICE from opportunistic downgrade but not VASSAL. When an AI lord has 2x troops of its vassal (common), the code enters the downgrade path, fails to find VASSAL in `_DOWNGRADE_ORDER`, and silently exits. Harmless now but fragile — if `_DOWNGRADE_ORDER` is ever extended to include VASSAL transitions, this becomes a real bug.

**Root cause:** Incomplete exclusion list in the state filter.

**Fix:** Add VASSAL to the exclusion:

```python
if not both_at_war and relation < 30 and state not in ("PEACE", "WAR", "ARMISTICE", "VASSAL"):
```

**Files:** `backend/game_logic/ai_diplomacy.py`
**Tests:**
- Vassal state is not subject to opportunistic downgrade
- Other states (ALLIANCE, DEFENSIVE_ALLIANCE, etc.) still downgrade normally

---

## Scaling Notes (Not Bugs — Future Work)

These are not bugs in the current 5-nation game but will need attention for the full Europe map:

- **NATION_DESIRE_PROFILES + TALLEYRAND_COMMENTARY** in `diplomatic_templates.py` are hardcoded for 4 nations. New nations fall back to generic defaults. Needs a data-driven system (YAML/JSON per-nation config).
- **O(n²) adjacency rivalry + relation drift** in `ai_diplomacy.py` and `diplomacy.py` runs every turn for all nation pairs. ~10 pairs at 5 nations, ~105 pairs at 15 nations, with nested region adjacency checks. Will need caching or batching.
- **CONTINENTAL_SYSTEM mission** is defined in `MISSION_DP_COSTS` only — no keywords, no effects, no description. Pure skeleton. Implement or remove.
- **Auto-downgrade + opportunistic downgrade race condition** — both `check_auto_downgrade()` (diplomacy.py) and `_process_ai_ai_rivalry()` (ai_diplomacy.py) can target the same AI-AI pair in the same turn, potentially double-downgrading. Low risk at 5 nations but worth auditing when scaling.

---

## Implementation Order

**Session 1 — Quick fixes (DLF-1, DLF-3, DLF-7, DLF-8):**
All small, independent, backend-only (DLF-3 has a minor Godot change). ~8 tests.

**Session 2 — Mission fixes (DLF-4, DLF-5):**
Both in `_process_mission_effects()`. DLF-4 is RNG + events. DLF-5 is new `intel_grants` field + visibility integration. ~12 tests.

**Session 3 — AI + dialogue (DLF-6, DLF-2):**
DLF-6 is enemy_ai.py border checks (4 code paths). DLF-2 is the largest item: dialogue follow-up, target_pair storage, per-turn processing, tracker display. ~15 tests.

**Estimated total: ~35 new tests across 3 sessions.**
