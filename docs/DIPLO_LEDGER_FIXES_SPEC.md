# Diplomatic Ledger Fixes Spec

**Date:** 2026-04-04
**Scope:** 8 bugs/improvements found during playtest + code audit
**Files affected:** `diplomatic_ledger.py`, `diplomatic_executor.py`, `diplomacy.py`, `diplomatic_dialogue.py`, `diplomatic_ledger.gd`, `ai_diplomacy.py`, `enemy_ai.py`

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

## DLF-4: COURT_NATION Blowback Is Stubbed

**Bug:** COURT_NATION costs 2 DP/turn (double IMPROVE_RELATIONS) because it's supposed to carry risk: a 20% chance per turn of -3 relation blowback. The blowback is defined in `MISSION_EFFECTS` but never processed — making COURT_NATION a strictly worse IMPROVE_RELATIONS (same +5/turn, double the cost, zero risk).

**Root cause:** `diplomacy.py:1948` — `"COURT_NATION undermine chance: stub"`. The `undermine_chance` and `undermine_amount` fields in `MISSION_EFFECTS` are never read during `_process_mission_effects()`.

**Fix:** After the relation_change block in `_process_mission_effects()`, add blowback processing:

```python
# COURT_NATION blowback: chance of negative relation hit
undermine_chance = effects.get("undermine_chance", 0)
undermine_amount = effects.get("undermine_amount", 0)
if undermine_chance and undermine_amount:
    import random
    if random.random() < undermine_chance:
        world.modify_nation_relation(player_nation, target, int(round(undermine_amount * multiplier)))
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
- Blowback applies -3 (×skill) when RNG triggers
- Blowback generates event + dispatch
- No blowback for non-COURT missions
- Skill multiplier affects blowback magnitude (high skill = worse blowback, risk/reward)

---

## DLF-5: GATHER_INTEL Completes But Reveals Nothing (DESIGN GATE)

**Bug:** GATHER_INTEL auto-completes after 3 turns with "Talleyrand has completed his intelligence gathering on {target}" but returns zero information. The player spends 3 DP for a congratulatory message.

**Root cause:** `diplomacy.py:1945` — `"Stub: no intel revealed yet (Session 4+)"`. The duration-based completion works, but no payload is delivered.

**Complication:** Diplomacy has no fog of war. The original design assumed an intel system that was never built and is now deferred (R14). Since all diplomatic info is already visible to the player, the mission's original purpose (reveal hidden diplomatic state) is moot.

### DESIGN GATE REQUIRED

This mission needs a redesign before implementation. The question is: **what should GATHER_INTEL reveal that the player can't already see?**

Possible directions:

**A) AI Intentions** — Reveal what the AI is planning next turn (e.g., "Prussia is considering an alliance with Austria" or "Austria is preparing to attack Saxony"). This is genuinely hidden from the player and strategically valuable.

**B) Hidden Modifiers** — Reveal the exact acceptance formula breakdown for a nation (what terms they'd accept, what they covet, their diplomatic priorities). Currently the player sees relation descriptors but not the math.

**C) Army Composition Details** — Reveal marshal strengths, locations, and unit types for the target nation. This overlaps with military fog but could be scoped to diplomatic context.

**D) Relation Network** — Reveal the exact relation values between AI nations (currently shown as descriptors like "Friendly" but not numbers). Less impactful since DLF-3 already shows states.

**E) Remove the Mission** — If no good design fits, remove GATHER_INTEL from the available missions rather than leaving a broken stub. Can re-add when there's real hidden information to reveal.

**Recommendation:** Option A (AI Intentions) is the most interesting and unique. It gives Talleyrand a scouting role that no other mechanic covers. But this requires exposing AI decision-tree outputs, which is a non-trivial backend change.

**Action:** Do not implement until a design direction is approved. Remove from the spec's implementation sessions or mark as blocked.

**Files (once designed):** `backend/game_logic/diplomacy.py`, `backend/game_logic/diplomatic_ledger.py`, potentially `backend/ai/enemy_ai.py` or `backend/game_logic/ai_diplomacy.py`

---

## DLF-6: AI Doesn't Check Diplomatic State Before Move Selection

**Bug:** AI pathfinding in `enemy_ai.py` (P7 strategic movement) selects adjacent regions purely by distance to the nearest enemy. It never calls `can_enter_territory()` to check whether the AI nation has diplomatic permission to enter the region. The movement executor in `movement_executor.py:196` correctly rejects the illegal move, but the AI wastes its action for the turn.

With 5 nations and a small map this is minor. With 15+ nations and complex border arrangements, AI marshals will frequently get stuck bumping into borders they can't cross, wasting turns.

**Root cause:** `enemy_ai.py` P7 movement logic (aggressive ~line 3414, cautious ~line 3460, stagnation fallback ~line 3556) filters for enemy occupation and visited regions but never checks `can_enter_territory()`.

**Fix:** Add a diplomatic state check in the P7 movement candidate loop:

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

Apply to all three P7 paths (aggressive, cautious, stagnation fallback).

**Files:** `backend/ai/enemy_ai.py`
**Tests:**
- AI skips regions controlled by nations at PEACE
- AI can move through OPEN_BORDERS+ territories
- AI can move through WAR territories (for attack positioning)
- AI doesn't get stuck when surrounded by diplomatically blocked regions (falls through to HOLD)

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

---

## Implementation Order

1. **DLF-1** (vassalizable icon) — 1 line backend + tests
2. **DLF-3** (relations filter) — small backend + Godot change + tests
3. **DLF-8** (VASSAL exclusion) — 1 line fix + tests
4. **DLF-7** (eliminated nations cascade) — small fix + tests
5. **DLF-4** (COURT_NATION blowback) — medium: RNG, events, dispatch + tests
6. **DLF-6** (AI border check) — medium: 3 code paths in enemy_ai.py + tests
7. **DLF-2** (undermine alliance) — largest: dialogue flow, mission storage, per-turn processing, tracker display + tests
8. **DLF-5** (GATHER_INTEL) — **BLOCKED on design gate.** Do not implement until direction approved.

**Estimated tests:** ~30-35 new tests across DLF-1 through DLF-8 (excluding DLF-5).
