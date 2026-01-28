# Save Format Reference

## Overview

This document defines the serialization format for all game objects in Project Sovereign.
A future save/load system should use this as the specification.

**Serialization validation:** All roundtrip tests pass (33 tests in `tests/test_serialization.py`).

## Version

- **Format version:** 1.0
- **Last updated:** 2026-01-28
- **Compatible with:** Phase 5.2 Strategic Commands (commit after serialization audit)

## Top-Level Structure (WorldState)

```json
{
  "format_version": "1.0",

  "player_nation": "France",
  "current_turn": 1,
  "max_turns": 40,
  "gold": 1200,
  "game_over": false,
  "victory": null,

  "max_actions_per_turn": 4,
  "actions_remaining": 4,
  "bonus_actions": 0,

  "regions": { ... },
  "marshals": { ... },

  "authority_tracker": { ... },
  "vindication_tracker": { ... },
  "pending_objection": null,
  "pending_redemption": null,

  "enemy_nations": ["Britain", "Prussia"],
  "nation_actions": {"Britain": 4, "Prussia": 4},
  "active_battles": {},
  "battle_history": [],

  "battles_this_turn": [],
  "command_history": []
}
```

### WorldState Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `format_version` | string | "1.0" | Save format version for compatibility |
| `player_nation` | string | "France" | Nation controlled by player |
| `current_turn` | int | 1 | Current turn number |
| `max_turns` | int | 40 | Maximum turns before game ends |
| `gold` | int | 1200 | Player's treasury |
| `game_over` | bool | false | Whether game has ended |
| `victory` | string\|null | null | "victory", "defeat", or null |
| `max_actions_per_turn` | int | 4 | Base actions per turn |
| `actions_remaining` | int | 4 | Actions left this turn |
| `bonus_actions` | int | 0 | Extra actions from admin role |
| `regions` | dict | {} | Map of region_name -> Region |
| `marshals` | dict | {} | Map of marshal_name -> Marshal |
| `authority_tracker` | dict | {} | AuthorityTracker state |
| `vindication_tracker` | dict | {} | VindicationTracker state |
| `pending_objection` | dict\|null | null | Objection awaiting response |
| `pending_redemption` | dict\|null | null | Redemption event awaiting response |
| `enemy_nations` | list | ["Britain", "Prussia"] | AI-controlled nations |
| `nation_actions` | dict | {} | Actions per nation |
| `active_battles` | dict | {} | Currently ongoing battles |
| `battle_history` | list | [] | Completed battle records |
| `battles_this_turn` | list | [] | Battles this turn (Phase 5.2) |
| `command_history` | list | [] | LLM command context |

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
  "just_retreated": false,

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
  "fortify_expires_turn": -1,
  "defense_bonus": 0.0,

  "retreating": false,
  "retreat_recovery": 0,
  "retreated_this_turn": false,

  "broken": false,
  "broken_recovery": 0,

  "stance": "neutral",

  "cavalry": true,
  "turns_in_defensive_stance": 0,
  "turns_fortified": 0,
  "turns_defensive": 0,

  "counter_punch_available": false,
  "counter_punch_turns": 0,

  "holding_position": false,
  "hold_region": "",

  "recklessness": 0,
  "pending_glorious_charge": false,
  "pending_charge_target": "",

  "attacks_this_turn": 0
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
| `just_retreated` | bool | Vulnerable after retreat (legacy) |

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
| `fortify_expires_turn` | int | Turn when fortification expires |
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
| `turns_defensive` | int | Legacy counter |

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
  "income_value": 100,
  "is_capital": true,
  "controller": "France",
  "garrison_strength": 0
}
```

### Region Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Region name |
| `adjacent_regions` | list | Names of bordering regions |
| `income_value` | int | Gold per turn when controlled |
| `is_capital` | bool | Whether this is a capital |
| `controller` | string\|null | Nation controlling region |
| `garrison_strength` | int | Garrison troops (future use) |

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
  ]
}
```

### VindicationTracker Fields

| Field | Type | Description |
|-------|------|-------------|
| `pending` | dict | marshal_name -> pending vindication data |
| `history` | list | List of resolved vindication events |

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
