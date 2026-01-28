# Modding Guide for Project Sovereign

This document describes how to create custom scenarios, marshals, and regions for Project Sovereign using JSON files.

## Quick Start

The simplest mod is a scenario file with just one line:

```json
{
    "player_nation": "France"
}
```

This creates a game with default map and marshals, playing as France.

## Validation Tool

Before loading your mod, validate it:

```bash
python -m backend.modding.validator path/to/your/scenario.json
```

This will report any errors or warnings in your JSON file.

## Loading Scenarios

In Python code:

```python
from backend.models.world_state import WorldState

world = WorldState.from_scenario("mods/examples/battle_of_waterloo.json")
```

---

## Scenario Format

A scenario file is a JSON object with the following structure:

```json
{
    "scenario_name": "Battle of Waterloo",
    "scenario_description": "June 18, 1815",
    "player_nation": "France",
    "current_turn": 1,
    "max_turns": 40,
    "gold": 1200,
    "regions": { ... },
    "marshals": { ... }
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| None | - | All fields are optional! Defaults are applied. |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `scenario_name` | string | - | Display name (metadata only) |
| `scenario_description` | string | - | Description (metadata only) |
| `player_nation` | string | "France" | Nation the player controls |
| `current_turn` | integer | 1 | Starting turn number |
| `max_turns` | integer | 40 | Game length in turns |
| `gold` | integer | 1200 | Starting gold |
| `regions` | object | (default map) | Custom map regions |
| `marshals` | object | (default marshals) | Custom marshals |
| `enemy_nations` | array | ["Britain", "Prussia"] | AI-controlled nations |

---

## Marshal Format

Marshals represent commanders on the map.

### Minimal Marshal (Required Fields Only)

```json
{
    "name": "Murat",
    "location": "Lyon",
    "strength": 45000
}
```

### Full Marshal (All Fields)

```json
{
    "name": "Murat",
    "location": "Lyon",
    "strength": 45000,
    "personality": "aggressive",
    "nation": "France",
    "cavalry": true,
    "movement_range": 2,
    "tactical_skill": 7,
    "morale": 80,
    "stance": "neutral",
    "skills": {
        "tactical": 6,
        "shock": 9,
        "defense": 3,
        "logistics": 4,
        "administration": 3,
        "command": 7
    },
    "ability": {
        "name": "King of Naples",
        "description": "Charismatic cavalry leader"
    }
}
```

### Marshal Field Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | **REQUIRED** | Marshal's name |
| `location` | string | **REQUIRED** | Region name where marshal starts |
| `strength` | integer | **REQUIRED** | Number of troops (e.g., 50000) |
| `personality` | string | "balanced" | One of: `aggressive`, `cautious`, `literal`, `balanced`, `loyal` |
| `nation` | string | "France" | Nation this marshal belongs to |
| `cavalry` | boolean | false | If true, has cavalry movement/abilities |
| `movement_range` | integer | 1 | Regions can move per turn (cavalry often 2) |
| `tactical_skill` | integer | 5 | Overall tactical rating (1-10) |
| `morale` | integer | 70 | Starting morale (0-100) |
| `stance` | string | "neutral" | One of: `neutral`, `defensive`, `aggressive` |
| `skills` | object | null | Individual skill ratings |
| `ability` | object | null | Special ability |

### Personality Types

| Personality | Behavior |
|-------------|----------|
| `aggressive` | Prefers attacking, objects to defensive orders |
| `cautious` | Prefers defense, objects to risky attacks |
| `literal` | Follows orders exactly, needs clear instructions |
| `balanced` | No strong preferences |
| `loyal` | Rarely objects to any order |

### Skills Object

```json
{
    "tactical": 7,       // General tactics
    "shock": 9,          // Offensive power
    "defense": 4,        // Defensive ability
    "logistics": 5,      // Supply management
    "administration": 4, // Administrative skill
    "command": 8         // Leadership
}
```

All skills range from 1-10. If not specified, defaults are applied.

### Ability Object

```json
{
    "name": "Cavalry Charge",
    "description": "Can attack 2 regions away"
}
```

Abilities are currently informational. Future versions may add mechanical effects.

---

## Region Format

Regions represent territories on the map.

### Minimal Region (Required Fields Only)

```json
{
    "name": "Tuscany",
    "adjacent_regions": ["Milan", "Rome", "Venice"]
}
```

### Full Region (All Fields)

```json
{
    "name": "Paris",
    "adjacent_regions": ["Belgium", "Lyon", "Brittany"],
    "income_value": 200,
    "is_capital": true,
    "controller": "France",
    "garrison_strength": 5000
}
```

### Region Field Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | **REQUIRED** | Region's name |
| `adjacent_regions` | array | **REQUIRED** | List of connected region names |
| `income_value` | integer | 100 | Gold per turn when controlled |
| `is_capital` | boolean | false | If true, losing this loses the game |
| `controller` | string | null | Nation that controls this region |
| `garrison_strength` | integer | 0 | Troops defending (not marshal) |

### Adjacency Rules

**Important:** Adjacency should be bidirectional. If Paris lists Belgium as adjacent, Belgium should list Paris as adjacent.

```json
{
    "regions": {
        "Paris": {
            "name": "Paris",
            "adjacent_regions": ["Belgium"]
        },
        "Belgium": {
            "name": "Belgium",
            "adjacent_regions": ["Paris"]
        }
    }
}
```

The validator will warn if adjacency is not bidirectional.

---

## Complete Example: Custom Scenario

```json
{
    "scenario_name": "Battle of Waterloo",
    "player_nation": "France",
    "current_turn": 1,
    "max_turns": 10,
    "gold": 500,

    "regions": {
        "Waterloo": {
            "name": "Waterloo",
            "adjacent_regions": ["Brussels", "Charleroi"],
            "controller": "Britain"
        },
        "Brussels": {
            "name": "Brussels",
            "adjacent_regions": ["Waterloo"],
            "income_value": 150,
            "is_capital": true,
            "controller": "Britain"
        },
        "Charleroi": {
            "name": "Charleroi",
            "adjacent_regions": ["Waterloo", "Paris"],
            "controller": "France"
        },
        "Paris": {
            "name": "Paris",
            "adjacent_regions": ["Charleroi"],
            "income_value": 200,
            "is_capital": true,
            "controller": "France"
        }
    },

    "marshals": {
        "Napoleon": {
            "name": "Napoleon",
            "location": "Charleroi",
            "strength": 73000,
            "personality": "aggressive",
            "nation": "France"
        },
        "Wellington": {
            "name": "Wellington",
            "location": "Waterloo",
            "strength": 68000,
            "personality": "cautious",
            "nation": "Britain"
        }
    }
}
```

---

## Tips for Modders

### 1. Start Minimal

Begin with the smallest possible scenario and add complexity gradually:

```json
{
    "player_nation": "France",
    "gold": 5000
}
```

### 2. Use the Validator

Always validate your JSON before testing in-game:

```bash
python -m backend.modding.validator your_scenario.json
```

### 3. Marshal Locations Must Match Regions

If you define custom regions, ensure all marshal locations exist:

```json
{
    "regions": {
        "CustomCity": { ... }
    },
    "marshals": {
        "MyMarshal": {
            "location": "CustomCity",  // Must exist in regions!
            ...
        }
    }
}
```

### 4. Bidirectional Adjacency

Always make adjacency go both ways:

```json
{
    "regions": {
        "A": { "adjacent_regions": ["B"] },
        "B": { "adjacent_regions": ["A"] }  // Don't forget!
    }
}
```

### 5. Default Map + Custom Marshals

You can use the default map but with custom marshals:

```json
{
    "player_nation": "France",
    "marshals": {
        "Napoleon": {
            "name": "Napoleon",
            "location": "Paris",
            "strength": 100000
        }
    }
}
```

The default regions will be loaded automatically.

### 6. Custom Nations

You can use any nation names - they don't have to be historical:

```json
{
    "player_nation": "Gondor",
    "enemy_nations": ["Mordor"],
    "marshals": {
        "Aragorn": {
            "nation": "Gondor",
            ...
        },
        "Sauron": {
            "nation": "Mordor",
            ...
        }
    }
}
```

---

## Example Files

See the `mods/examples/` directory for complete examples:

- `minimal_scenario.json` - Simplest possible scenario
- `custom_marshal.json` - How to define a marshal
- `custom_region.json` - How to define a region
- `battle_of_waterloo.json` - Full historical scenario
- `custom_nations_scenario.json` - Custom nations example

---

## Troubleshooting

### "Required field is missing"

Check that your marshals have `name`, `location`, and `strength`.
Check that your regions have `name` and `adjacent_regions`.

### "Marshal location X is not a defined region"

Either:
1. Add the region to your `regions` object
2. Remove your custom `regions` to use the default map
3. Change the marshal's location to an existing region

### "References non-existent region"

A region's `adjacent_regions` lists a region that doesn't exist. Add the missing region or fix the typo.

### "non-bidirectional adjacency"

Region A says it's adjacent to B, but B doesn't say it's adjacent to A. Add the missing adjacency to region B.

---

## Version Compatibility

Scenario files are forward-compatible. Fields added in future versions will be ignored by older game versions. However, older scenarios may not have access to newer features.

Current format version: **1.0**
