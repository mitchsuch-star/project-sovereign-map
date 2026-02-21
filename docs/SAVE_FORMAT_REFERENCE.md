# Save Format Reference

## Overview

This document defines the serialization format for all game objects in Project Sovereign.
A future save/load system should use this as the specification.

**Serialization validation:** All roundtrip tests pass (33 tests in `tests/test_serialization.py`).

## Version

- **Format version:** 1.0
- **Last updated:** 2026-02-18
- **Compatible with:** Phase 6.5 Session 51 (Bombardment Part 4)

## Top-Level Structure (WorldState)

```json
{
  "format_version": "1.0",

  "player_nation": "France",
  "current_turn": 1,
  "max_turns": 40,
  "gold": 600,
  "nation_gold": {"France": 600, "Britain": 800, "Prussia": 300},
  "manpower_pools": {
    "France": {"infantry": 80000, "cavalry": 15000, "artillery": 10000},
    "Britain": {"infantry": 50000, "cavalry": 8000, "artillery": 5000},
    "Prussia": {"infantry": 60000, "cavalry": 10000, "artillery": 5000}
  },
  "game_over": false,
  "victory": null,

  "max_actions_per_turn": 4,
  "actions_remaining": 4,
  "bonus_actions": 0,
  "admin_actions_remaining": 2,
  "max_admin_actions": 2,

  "nation_bankruptcy_turns": {"France": 0, "Britain": 0},
  "gold_spent_this_turn": {"France": 0, "Britain": 0, "Prussia": 0},

  "regions": { ... },
  "marshals": { ... },

  "authority_tracker": { ... },
  "vindication_tracker": { ... },
  "pending_objection": null,
  "pending_redemption": null,
  "pending_capture_choice": null,

  "mild_concerns_this_turn": [],
  "objection_popups_this_turn": [],

  "enemy_nations": ["Britain", "Prussia"],
  "nation_actions": {"Britain": 4, "Prussia": 4},
  "active_battles": {},
  "battle_history": [],

  "battles_this_turn": [],
  "command_history": [],

  "event_log": [],

  "notifications": [],

  "intel": {
    "Paris": { ... },
    "Belgium": { ... }
  }
}
```

### WorldState Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `format_version` | string | "1.0" | Save format version for compatibility |
| `player_nation` | string | "France" | Nation controlled by player |
| `current_turn` | int | 1 | Current turn number |
| `max_turns` | int | 40 | Maximum turns before game ends |
| `gold` | int | 600 | Player's treasury (backward compat, reads from nation_gold) |
| `nation_gold` | dict | {"France": 600, ...} | Per-nation treasury |
| `manpower_pools` | dict | DEFAULT_MANPOWER_POOLS | Per-nation infantry/cavalry/artillery reserve pools |
| `game_over` | bool | false | Whether game has ended |
| `victory` | string\|null | null | "victory", "defeat", or null |
| `max_actions_per_turn` | int | 4 | Base actions per turn |
| `actions_remaining` | int | 4 | Actions left this turn |
| `bonus_actions` | int | 0 | Extra actions from admin role |
| `admin_actions_remaining` | int | 2 | Admin actions left this turn (Phase 6.2.B) |
| `max_admin_actions` | int | 2 | Max admin actions per turn (Phase 6.2.B) |
| `nation_bankruptcy_turns` | dict | {} | Per-nation bankruptcy counter {nation: int} (Phase 6.2.B) |
| `gold_spent_this_turn` | dict | {} | Per-nation gold spending tracker for turn summary. Records all gold spent this turn (recruit, build, repair). Reset at start of each turn. |
| `regions` | dict | {} | Map of region_name -> Region |
| `marshals` | dict | {} | Map of marshal_name -> Marshal |
| `authority_tracker` | dict | {} | AuthorityTracker state |
| `vindication_tracker` | dict | {} | VindicationTracker state |
| `pending_objection` | dict\|null | null | Objection awaiting response |
| `pending_redemption` | dict\|null | null | Redemption event awaiting response |
| `pending_capture_choice` | dict\|null | null | Plunder/secure choice awaiting response: `{region, capturer, previous_controller}` (Phase 6.2.E) |
| `mild_concerns_this_turn` | list | [] | V2a: MILD concerns for turn log (cleared each turn) |
| `objection_popups_this_turn` | list | [] | V2a: Per-marshal popup cap tracking (cleared each turn) |
| `ai_failed_action_cooldowns` | dict | {} | AI failed action retry cooldowns {marshal: {action: turns}} |
| `ai_refortify_cooldown` | dict | {} | Per-marshal re-fortify cooldown turns {marshal_name: int}. Set to 2 when stagnation forces unfortify, decremented each turn. Blocks P5/P8 fortify while active. |
| `enemy_nations` | list | ["Britain", "Prussia"] | AI-controlled nations |
| `nation_actions` | dict | {} | Actions per nation |
| `active_battles` | dict | {} | Currently ongoing battles |
| `battle_history` | list | [] | Completed battle records |
| `battles_this_turn` | list | [] | Battles this turn (Phase 5.2) |
| `command_history` | list | [] | LLM command context |
| `event_log` | list | [] | Structured game event history. Each entry is a dict with `type`, `turn`, and event-specific fields. Accumulates across full game, never cleared. Used by Campaign Log, Gazette. |
| `notifications` | list | [] | Pending notification alerts. Each entry: `{id, type, priority, title, message, turn_created, details}`. Persists until player dismisses. Serialized via `NotificationCollector.to_list()/from_list()`. |
| `intel` | dict | {} | Map of region_name -> RegionIntel. Fog of war intel store. Empty dict for backward compat (old saves populate via `calculate_visibility()` on load). |

---

## Marshal Format

```json
{
  "name": "Ney",
  "location": "Belgium",
  "strength": 72000,
  "starting_strength": 72000,
  "personality": "aggressive",
  "nation": "France",
  "spawn_location": "Paris",
  "movement_range": 2,
  "tactical_skill": 8,

  "skills": {
    "tactical": 7,
    "shock": 9,
    "defense": 4,
    "logistics": 5,
    "administration": 4,
    "command": 8
  },

  "ability": {
    "name": "Bravest of the Brave",
    "description": "...",
    "trigger": "when_attacking",
    "effect": "+2 Shock skill when attacking"
  },

  "morale": 100,
  "orders_overridden": 0,
  "battles_won": 0,
  "battles_lost": 0,

  "trust": {"value": 75},
  "vindication_score": 0,
  "recent_battles": [],
  "recent_overrides": [],

  "autonomous": false,
  "autonomy_turns": 0,
  "autonomy_reason": "",
  "redemption_pending": false,
  "autonomous_battles_won": 0,
  "autonomous_battles_lost": 0,
  "autonomous_regions_captured": 0,
  "trust_warning_shown": false,

  "relationships": {"Davout": -2, "Grouchy": 0},

  "drilling": false,
  "drilling_locked": false,
  "drill_complete_turn": -1,
  "shock_bonus": 0,
  "strategic_combat_bonus": 0,
  "strategic_defense_bonus": 0,

  "precision_execution_active": false,
  "precision_execution_turns": 0,

  "strategic_order": null,
  "pending_interrupt": null,

  "in_combat_this_turn": false,
  "last_combat_turn": null,
  "last_combat_result": null,
  "last_combat_location": null,

  "fortified": false,
  "defense_bonus": 0.0,

  "retreating": false,
  "retreat_recovery": 0,
  "retreated_this_turn": false,
  "_recovery_destination": null,

  "broken": false,
  "broken_recovery": 0,

  "stance": "neutral",

  "cavalry": true,
  "artillery": false,
  "moved_this_turn": false,
  "turns_in_defensive_stance": 0,
  "turns_fortified": 0,

  "counter_punch_available": false,
  "counter_punch_turns": 0,

  "holding_position": false,
  "hold_region": "",

  "recklessness": 0,
  "pending_glorious_charge": false,
  "pending_charge_target": "",

  "attacks_this_turn": 0,

  "last_bombardment_target": null,
  "bombardment_streak": 0,
  "bombardments_this_turn": 0,

  "idle_turns": 0,

  "occupation_region": null,
  "occupation_turns_held": 0,
  "occupation_turns_required": 0
}
```

### Marshal Fields Reference

#### Core Identity
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Marshal's name |
| `location` | string | Current region name |
| `strength` | int | Current army size |
| `starting_strength` | int | Original army size |
| `personality` | string | "aggressive", "cautious", "literal", "balanced" |
| `nation` | string | "France", "Britain", "Prussia" |
| `spawn_location` | string | Capital/respawn region |
| `movement_range` | int | 1 (infantry) or 2 (cavalry) |
| `tactical_skill` | int | Legacy skill rating 0-12 |
| `cavalry` | bool | Whether marshal commands cavalry |
| `artillery` | bool | Whether marshal commands artillery (mutually exclusive with cavalry) |
| `moved_this_turn` | bool | Whether artillery moved this turn (blocks attack, -25% defense) |

#### Skills (6-Skill System)
| Skill | Range | Description |
|-------|-------|-------------|
| `tactical` | 1-10 | Combat rolls, flanking bonuses |
| `shock` | 1-10 | Attack damage, pursuit effectiveness |
| `defense` | 1-10 | Defender bonus, retreat casualties |
| `logistics` | 1-10 | Supply range, attrition resistance |
| `administration` | 1-10 | Recruitment speed, desertion prevention |
| `command` | 1-10 | Morale management, discipline |

#### Game State
| Field | Type | Description |
|-------|------|-------------|
| `morale` | int | 0-100, affects combat effectiveness |
| `orders_overridden` | int | Times player insisted over objections |
| `battles_won` | int | Victories counter |
| `battles_lost` | int | Defeats counter |

#### Disobedience System
| Field | Type | Description |
|-------|------|-------------|
| `trust` | dict | {"value": 0-100} Trust object |
| `vindication_score` | int | -5 to +5, affects objection boldness |
| `recent_battles` | list | Last 3 battle results |
| `recent_overrides` | list | Last 5 override events (bool) |

#### Autonomy System
| Field | Type | Description |
|-------|------|-------------|
| `autonomous` | bool | Marshal acting independently |
| `autonomy_turns` | int | Turns remaining in autonomy |
| `autonomy_reason` | string | "redemption", "communication_cut" |
| `redemption_pending` | bool | Redemption event triggered |
| `autonomous_battles_won` | int | Wins during autonomy |
| `autonomous_battles_lost` | int | Losses during autonomy |
| `autonomous_regions_captured` | int | Captures during autonomy |
| `trust_warning_shown` | bool | Warning shown at trust < 40 |

#### Tactical State
| Field | Type | Description |
|-------|------|-------------|
| `drilling` | bool | Currently drilling (turn N) |
| `drilling_locked` | bool | Locked in drill (turn N+1) |
| `drill_complete_turn` | int | Turn when drill completes |
| `shock_bonus` | int | +2 = +20% attack from drill |
| `fortified` | bool | Currently fortified |
| `defense_bonus` | float | 0.0-0.20, decimal (0.16 = 16%) |

#### Strategic Order System (Phase 5.2)
| Field | Type | Description |
|-------|------|-------------|
| `strategic_order` | dict\|null | StrategicOrder if active |
| `pending_interrupt` | dict\|null | Interrupt awaiting response |
| `strategic_combat_bonus` | int | % bonus from inspiring commands |
| `strategic_defense_bonus` | int | % bonus from clear orders |
| `precision_execution_active` | bool | +1 to all skills active |
| `precision_execution_turns` | int | Countdown (3 turns) |

#### Combat Tracking
| Field | Type | Description |
|-------|------|-------------|
| `in_combat_this_turn` | bool | Fought this turn |
| `last_combat_turn` | int\|null | Turn of last combat |
| `last_combat_result` | string\|null | "victory", "defeat", "stalemate" |
| `last_combat_location` | string\|null | Region of last combat |

#### Retreat/Broken State
| Field | Type | Description |
|-------|------|-------------|
| `retreating` | bool | In retreat recovery |
| `retreat_recovery` | int | 0-3 recovery stage |
| `retreated_this_turn` | bool | Retreated this turn (ally cover) |
| `_recovery_destination` | str/null | AI retreat destination cache |
| `broken` | bool | Army shattered |
| `broken_recovery` | int | 0-4 recovery stage |

#### Stance System
| Field | Type | Valid Values |
|-------|------|-------------|
| `stance` | string | "neutral", "defensive", "aggressive" |

#### Cavalry Limits
| Field | Type | Description |
|-------|------|-------------|
| `turns_in_defensive_stance` | int | Counter (triggers at 3) |
| `turns_fortified` | int | Counter (triggers at 3) |

#### Ability State
| Field | Type | Description |
|-------|------|-------------|
| `counter_punch_available` | bool | Davout free attack earned |
| `counter_punch_turns` | int | Turns to use counter-punch |
| `holding_position` | bool | Grouchy Immovable active |
| `hold_region` | string | Region where holding |

#### Recklessness System
| Field | Type | Description |
|-------|------|-------------|
| `recklessness` | int | 0-4, builds from wins |
| `pending_glorious_charge` | bool | Popup pending |
| `pending_charge_target` | string | Target of pending charge |

#### Exhaustion
| Field | Type | Description |
|-------|------|-------------|
| `attacks_this_turn` | int | Attacks made this turn |

#### Bombardment Tracking (Sessions 2, 48)
| Field | Type | Description |
|-------|------|-------------|
| `last_bombardment_target` | string\|null | Region of last bombardment target (null if never bombarded or after move) |
| `bombardment_streak` | int | Consecutive attacks on same target (resets on move or target change) |
| `bombardments_this_turn` | int | Number of bombardments fired this turn (max 2, reset at turn start) |

#### Idle Tracking (V2a)
| Field | Type | Description |
|-------|------|-------------|
| `idle_turns` | int | Consecutive turns without attack or move (V2b: triggers idle objections) |

#### Contested Capture (Phase 6.2.F)
| Field | Type | Description |
|-------|------|-------------|
| `occupation_region` | string\|null | Region being occupied (null if not occupying) |
| `occupation_turns_held` | int | Turns held so far |
| `occupation_turns_required` | int | Turns needed to complete capture (1 = ungarrisoned, 2 = garrisoned) |

---

## StrategicOrder Format

```json
{
  "command_type": "MOVE_TO",
  "target": "Belgium",
  "target_type": "region",
  "started_turn": 3,
  "original_command": "march to Belgium",
  "path": ["Paris", "Belgium"],
  "follow_if_moves": true,
  "join_combat": true,
  "target_snapshot_location": null,
  "attack_on_arrival": false,
  "condition": null,
  "last_combat_enemy": null,
  "last_combat_turn": null,
  "last_combat_result": null
}
```

### StrategicOrder Fields

| Field | Type | Description |
|-------|------|-------------|
| `command_type` | string | "MOVE_TO", "PURSUE", "HOLD", "SUPPORT" |
| `target` | string | Region name, marshal name, or "generic" |
| `target_type` | string | "region", "marshal", "battle", "generic" |
| `started_turn` | int | Turn when order was issued |
| `original_command` | string | Raw command text |
| `path` | list | Planned route as region names |
| `follow_if_moves` | bool | (SUPPORT) Follow if ally moves |
| `join_combat` | bool | (SUPPORT) Join ally's combat |
| `target_snapshot_location` | string\|null | For "Move to Ney" - where Ney was |
| `attack_on_arrival` | bool | (MOVE_TO) Attack on reaching destination |
| `condition` | dict\|null | StrategicCondition if set |
| `last_combat_enemy` | string\|null | Combat loop prevention |
| `last_combat_turn` | int\|null | Combat loop prevention |
| `last_combat_result` | string\|null | "victory", "defeat", "stalemate" |
| `bombardment_target` | string\|null | Locked target for artillery HOLD |

---

## StrategicCondition Format

```json
{
  "max_turns": 10,
  "until_marshal_arrives": "Davout",
  "until_marshal_destroyed": null,
  "until_battle_won": true,
  "until_relieved": false
}
```

### StrategicCondition Fields

| Field | Type | Description |
|-------|------|-------------|
| `max_turns` | int\|null | Maximum turns for order |
| `until_marshal_arrives` | string\|null | End when marshal arrives |
| `until_marshal_destroyed` | string\|null | End when enemy destroyed |
| `until_battle_won` | bool | End when battle won (or stalemate) |
| `until_relieved` | bool | End when relieved by ally |

---

## Region Format

```json
{
  "name": "Paris",
  "adjacent_regions": ["Belgium", "Lyon", "Brittany", "Waterloo"],
  "income_value": 300,
  "is_capital": true,
  "terrain": "urban",
  "region_type": "capital",
  "controller": "France",
  "garrison_strength": 0,
  "garrison_detachment": false,
  "stability": 100,
  "war_damage": 0.0,
  "plundered": false,
  "buildings": [{"type": "supply_depot", "damaged": false}],
  "building_under_construction": null,
  "watchtower": "none",
  "watchtower_turns_remaining": 0
}
```

### Region Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Region name |
| `adjacent_regions` | list | Names of bordering regions |
| `income_value` | int | Gold per turn when controlled |
| `is_capital` | bool | Whether this is a capital |
| `terrain` | string | Terrain type: plains, forest, hills, mountains, urban, river_crossing. Default "plains" for backward compat. |
| `region_type` | string | Region type: capital, major_city, city, town, rural. Default "town" for backward compat. |
| `controller` | string\|null | Nation controlling region |
| `garrison_strength` | int | Garrison troops (capital: 15k start, player-placed: 3k detachment) |
| `garrison_detachment` | bool | True if garrison was placed by marshal detachment — player or AI (no regen, no 5k collapse). Default false. Backward compat: `from_dict` also reads old `garrison_player_placed` key. |
| `stability` | int | 0-100, affects income via tiered modifier. Default 100 for backward compat. (Phase 6.2.C) |
| `war_damage` | float | 0.0-0.5, reduces income. Default 0.0 for backward compat. (Phase 6.2.C) |
| `plundered` | bool | True if region was plundered on capture. Clears when stability > 50. Default false. (Phase 6.2.E) |
| `buildings` | list | Built buildings: `[{"type": str, "damaged": bool}]`. Default []. (Phase 6.2.E) |
| `building_under_construction` | dict\|null | Active construction: `{"type": str, "turns_remaining": int}`. Default null. (Phase 6.2.E) |

### Computed Properties (not serialized)

| Property | Derived From | Description |
|----------|-------------|-------------|
| `defense_bonus` | terrain | Defender bonus (0.0-0.25) |
| `movement_cost` | terrain | Attrition multiplier (1.0-2.0) |
| `supply_modifier` | terrain | Supply capacity modifier (0.5-1.2) |
| `cavalry_effectiveness` | terrain | Cavalry combat multiplier (0.3-1.2) |
| `get_effective_income()` | stability, war_damage, buildings | Actual income: `int(int((income_value + depot_bonus) * market_mult) * stability_mod * (1 - war_damage))`. Market mult = 1.25 if functional market, else 1.0. |
| `get_stability_label()` | stability | "Hostile" / "Unrest" / "Settling" / "Stable" |
| `max_building_slots()` | region_type | Capital: 2, major_city/city: 1, town/rural: 0 |
| `has_building(type)` | buildings | True if functional (undamaged) building of that type exists |

---

## Trust Format

```json
{
  "value": 75
}
```

### Trust Fields

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `value` | int | 0-100 | Trust level (81+ Loyal, 61-80 Reliable, 41-60 Questioning, 21-40 Strained, 0-20 Broken) |

---

## AuthorityTracker Format

```json
{
  "authority": 100,
  "recent_responses": ["trust", "insist", "compromise"],
  "_crossed_thresholds": [70]
}
```

### AuthorityTracker Fields

| Field | Type | Description |
|-------|------|-------------|
| `authority` | int | 0-100, Napoleon's authority |
| `recent_responses` | list | Last 10 responses ("trust", "insist", "compromise") |
| `_crossed_thresholds` | list | Threshold events already triggered (70, 50, 30) |

---

## VindicationTracker Format

```json
{
  "pending": {
    "Ney": {
      "choice": "insist",
      "original_order": {"action": "attack", "target": "Wellington"},
      "alternative": {"action": "defend"},
      "turn_recorded": null
    }
  },
  "history": [
    {
      "marshal": "Ney",
      "choice": "trust",
      "result": "victory",
      "vindication_change": 1,
      "trust_change": 3,
      "authority_change": 0,
      "message": "...",
      "new_vindication": 1,
      "new_trust": 78
    }
  ],
  "pending_defensive_vindication": {
    "Davout": {
      "order": {"action": "defend", "target": "Belgium"},
      "timestamp": 5
    }
  }
}
```

### VindicationTracker Fields

| Field | Type | Description |
|-------|------|-------------|
| `pending` | dict | marshal_name -> pending vindication data |
| `history` | list | List of resolved vindication events |
| `pending_defensive_vindication` | dict | marshal_name -> pending defensive vindication (V2a) |

---

## RegionIntel Format (Fog of War)

```json
{
  "region_name": "Belgium",
  "visibility": "partial",
  "known_marshals": [
    {"name": "Wellington", "nation": "Britain", "band": "large force"}
  ],
  "strength_band": "large force",
  "exact_strength": null,
  "morale": null,
  "stance": null,
  "last_scouted_turn": 0,
  "last_updated_turn": 1,
  "intel_source": "adjacent"
}
```

### RegionIntel Fields

| Field | Type | Description |
|-------|------|-------------|
| `region_name` | string | Region this intel applies to |
| `visibility` | string | Current visibility level: "full", "partial", "stale", "last_known", "unknown" |
| `known_marshals` | list | Snapshot of marshals last seen: `[{name, nation, strength?, band?}]`. Frozen during decay. |
| `strength_band` | string | Aggregate strength band: "no forces", "screening force", "small force", "substantial force", "large force", "massive force" |
| `exact_strength` | int\|null | Exact total troop count. Only set at FULL visibility. |
| `morale` | int\|null | Morale value. Only set at FULL visibility. |
| `stance` | string\|null | Stance value. Only set at FULL visibility. |
| `last_scouted_turn` | int | Turn when last scouted via scout action. Default 0. |
| `last_updated_turn` | int | Turn when intel was last refreshed by any source. Default 0. |
| `intel_source` | string | Best source: "own_territory", "marshal_present", "scout", "battle", "watchtower", "adjacent", "transit" |

### Visibility Levels (priority order)

| Level | Priority | Data Available |
|-------|----------|----------------|
| `full` | 4 | Exact strength, morale, stance, marshal names |
| `partial` | 3 | Marshal names + strength band, no morale/stance |
| `stale` | 2 | Frozen snapshot from last refresh, aging |
| `last_known` | 1 | Old snapshot, "last seen X turns ago" |
| `unknown` | 0 | Never scouted, no intel |

### Strength Bands

| Threshold | Band |
|-----------|------|
| 0 | "no forces" |
| 1 - 4,999 | "screening force" |
| 5,000 - 14,999 | "small force" |
| 15,000 - 39,999 | "substantial force" |
| 40,000 - 69,999 | "large force" |
| 70,000+ | "massive force" |

### Decay Timeline

| Turns since update | Effect |
|--------------------|--------|
| 0-2 | Stays at current level (fresh) |
| 3-4 | Degrades to STALE (exact data cleared, snapshot frozen) |
| 5+ | Degrades to LAST_KNOWN (persists indefinitely) |

---

## Validation Checklist

When implementing save/load, verify:

- [ ] All fields listed here are saved
- [ ] All fields listed here are restored
- [ ] Nested objects are proper instances, not plain dicts
  - `marshal.trust` is `Trust`, not `dict`
  - `marshal.strategic_order` is `StrategicOrder`, not `dict`
  - `marshal.strategic_order.condition` is `StrategicCondition`, not `dict`
  - `world.authority_tracker` is `AuthorityTracker`, not `dict`
  - `world.vindication_tracker` is `VindicationTracker`, not `dict`
  - All regions are `Region`, not `dict`
  - All intel entries are `RegionIntel`, not `dict`
- [ ] None values are handled correctly (field present with null value)
- [ ] Enum values are stored as strings, restored as enums (e.g., Stance)
- [ ] Unknown fields in save file are ignored (forward compatibility)
- [ ] All integer fields use `int()` wrapper (Godot compatibility)
- [ ] All float fields (defense_bonus) preserve precision

## Test Coverage

Serialization is validated by `tests/test_serialization.py`:

| Test Class | Tests | Coverage |
|------------|-------|----------|
| TestStrategicConditionSerialization | 3 | All condition fields |
| TestStrategicOrderSerialization | 5 | All order types |
| TestMarshalSerialization | 6 | All 50+ marshal fields |
| TestTrustSerialization | 3 | Value roundtrip |
| TestRegionSerialization | 3 | All region fields |
| TestAuthorityTrackerSerialization | 3 | Authority and thresholds |
| TestVindicationTrackerSerialization | 3 | Pending and history |
| TestWorldStateSerialization | 4 | Complete game state |
| TestParseResultSerialization | 2 | Command parsing |

**Total: 33 roundtrip tests, all passing**

---

## Future Considerations

### Version Migration

When format changes:
1. Increment `format_version`
2. Add migration function for old -> new format
3. Support reading old versions

### Save File Structure (Pre-EA)

Suggested file structure for actual save/load:

```json
{
  "metadata": {
    "format_version": "1.0",
    "game_version": "0.5.2",
    "saved_at": "2026-01-28T12:34:56Z",
    "save_name": "Campaign Turn 15",
    "playtime_seconds": 3600
  },
  "world_state": { ... }
}
```

### Compression

For large save files (200+ regions), consider:
- JSON with gzip compression
- Binary format (msgpack)

### Checksums

For corruption detection:
```json
{
  "checksum": "sha256:abc123...",
  "world_state": { ... }
}
```
