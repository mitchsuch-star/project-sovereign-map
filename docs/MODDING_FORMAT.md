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
    "scenario_schema_version": 1,
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
| `scenario_schema_version` | integer | 1 | Scenario schema version. `1` is the current scale-readiness era shape. |
| `player_nation` | string | "France" | Nation the player controls |
| `current_turn` | integer | 1 | Starting turn number |
| `max_turns` | integer | 40 | Game length in turns |
| `gold` | integer | 1200 | Starting gold |
| `regions` | object | (default map) | Custom map regions |
| `marshals` | object | (default marshals) | Custom marshals |
| `enemy_nations` | array | ["Britain", "Prussia"] | AI-controlled nations |
| `nations` | object | {} | Optional authored nation records. In schema v1, this is where static nation metadata like `power_tier` belongs. Runtime `political_status` is not authored here. |
| `sovereign_map` | string | "legacy" | Which world the scenario targets: `"legacy"` (19-region fixture) or `"europe"` (the 126-province Europe world). Selects the default map/roster injected for omitted fields AND which nation roster the runtime-support validator checks against (1805 Loader pre-slice). |
| `starting_wars` | array | [] | ORDERED list of `{"attacker": str, "defender": str}` pairs. Seeded through the live `ensure_war_instance_for_pair` machinery after load — the first entry naming a side fixes the war instance's leaders, and later entries sharing a participant attach to the same instance (so France-first ordering yields ONE shared coalition war). Also sets the pair's diplomatic state to WAR and seeds `war_start_turns`. Do NOT hand-author raw `war_instance` JSON. |
| `region_overrides` | object | {} | Per-province shallow field overrides applied AFTER the default-map injection (Map Slice 8 / DEF-6): `{"Flanders": {"garrison_strength": 12000}}` stamps fields onto the named region dict without inlining the whole map. Keys must name existing provinces — an unknown name fails the load loudly. Works with authored `regions` too (merge wins). The shipped 1805 scenario uses it for the Flanders Channel-coast depot. |
| `marshal_pool` | object | {} | **Marshal Recruitment (Jealousy v3.2 — `MARSHAL_RECRUITMENT_SPEC.md`):** `{nation: [candidates]}` commissionable bench. Candidates are marshal entries WITHOUT `location`/`strength` (spawn-derived: capital, or the richest held homeland province; 5,000-man corps drawn from the infantry pool) plus a REQUIRED positive-int `cost` (gold). Personality must be an implemented type (the MC-4 boot guard extends here — retired types hard-fail validation). `relationships` seeds apply symmetrically to marshals in service; seeds may reference roster OR pool names (author pool-to-pool pairs on BOTH entries — arrival order must not matter). A candidate name colliding with the starting roster is a validation ERROR. Nations without a pool simply cannot recruit. |
| `agendas` | object | {} | **Nation Agendas (NA-0 — `NATION_AGENDAS_SPEC.md`):** `{nation: [agenda]}` authored historical decks. **Deck order = priority** — the first agenda whose predicate holds is ACTIVE (exactly one per nation). Each entry: REQUIRED `id` (unique per deck), `type` (one of `acquire_regions`/`deny_regions`/`contain_hegemon`/`paymaster`/`guard_neutrality`), `title` (player-facing); the three region-typed kinds REQUIRE a non-empty `regions` list (names cross-checked against the region set when present); `contain_hegemon` takes optional `share_floor` (number in (0,1], default 0.33), `paymaster` optional `treasury_floor` (non-negative int); optional `blurb`. Unknown nation keys WARN (deck never activates). Vassals never activate agendas while vassalized — a satellite MAY carry a dormant deck that wakes on independence. Nations without decks get the built-in survival override only. **NA-6 formables:** an entry may carry an optional `forms` object — REQUIRED non-empty `display_name` (the new name on every player surface), optional `flag` (heraldry asset tag; defaults to `display_name` with spaces stripped), optional `blurb` (the Proclamation's engraved line), optional `aggrieved` list of nations that take a one-time −30 relation blow with both the formed nation and its sponsor, then feed a standing threat contributor; optional `grudge_label` (NA-6d — the threat panel's name for that standing wound, e.g. "The Polish Question"; string; only meaningful beside `aggrieved`, and absent it falls back to the generic "Nations raised from their lands" row). When that entry's SATISFACTION condition holds while the nation is free (never vassalized), it forms once and permanently: +2,000 gold, +2 stability in every owned region (capped), and deck priority natively activates the NEXT authored entry as the post-formation goal — so author that entry too. `forms` is only valid on `acquire_regions`/`deny_regions`/`contain_hegemon`; the postures (`paymaster`/`guard_neutrality`) never reach a satisfied state, so a `forms` block on one is a validation ERROR rather than a formable that can never fire. Unknown `aggrieved` nations WARN. **Authoring note:** the "N of M provinces held" progress marker is only meaningful for `acquire_regions` — `deny_regions` and `contain_hegemon` satisfy on hegemon-bloc share rather than on self-control, so their marker will read 0-of-M while the design is genuinely advancing. Prefer `acquire_regions` for anything a player is meant to watch approach. A nation whose forming entry is ALREADY satisfied when the scenario boots would proclaim on turn 1; author conditions the starting world does not meet. **AI-0c deck-order band:** entries sharing a positive-int `order_group` value (a CONTIGUOUS run — a split group is a validation ERROR, a single-member group a no-op WARNING) are equally-live designs the campaign seed may reorder; the `historical` seed keeps authored order, and the key is stripped at load so the serialized deck is shaped exactly as before. Author it only where deck order was genuinely contested (the shipped file bands Austria's Italy-first/Germany-first pair; Russia's deck is deliberately unbanded — pin 22). |
| `nation_relations` | object | {} | `{"NationA\|NationB": value}` — pair keys MUST be alphabetically sorted (an unsorted key is unreachable at runtime and is a validation ERROR). A value is a bare int in [-100, 100] (fixed), or — **AI-0c variance bands (`AI_INTENT_SPEC.md` §3.8.1, D7)** — a band-carrying object `{"value": int, "band": [lo, hi]}` (the trust `{"value": N}` authoring idiom): the campaign seed resolves the relation inside `band`; the `historical` seed (or unset `SOVEREIGN_SEED`) ALWAYS resolves to `value`, byte-identical to a bare int. **No band = no variance** — the engine cannot invent a range it was not given. Clamps (validation ERRORs): the band must contain `value`; a band on a pair appearing in `starting_wars` must sit entirely below the −60 armistice-first line (`ARMISTICE_AUTO_PEACE_RELATION`) so no seed can flip a boot war's truce-expiry behaviour. Bands are resolved at `from_scenario` — the save file and `from_dict` only ever see plain ints. |
| `threat_level_band` | array | - | **AI-0c:** sibling `[lo, hi]` band for the top-level `threat_level` (0 ≤ lo ≤ hi ≤ 100, must contain the authored value). The seed resolves the campaign's central pressure inside it; `historical` keeps the authored value. Narrow by design — widening the envelope escalates (D7). |
| `statecraft` | object | {} | **AI War Decision AI-3r (`AI_WAR_DECISION_SPEC.md` §2.6, gate ruling R1):** `{nation: {"wary_of": {neighbour: multiplier}}}` — authored rear-security posture. `wary_of` multiplies that neighbour's MENACE in the war council's reserve calculus (`get_rear_reserve`): a fear the relations number alone would understate (the shipped file authors the German dualism both ways, Prussia's dread of Russia, the Russo-Turkish menace, Sweden's fear for Finland). **v1 authors `wary_of` ONLY** — any other sub-key is a validation ERROR; the statecraft PROFILE table (style/reaches_first/coercion/weight_mod/haggles) stays code-authored in `nation_config.NATION_STATECRAFT`. Clamps: values must be numbers in **[0.5, 2.0]** (ERROR), a self-reference is an ERROR, an unknown target nation is an ERROR, an unknown top-level nation WARNs (the posture is never read). Absent pair → 1.0; absent block → every posture 1.0. D7's principle: the bounds are authored content, reviewable in the scenario file — ahistorical paranoia is structurally impossible. |
| `navies` | object | {} | **DEF-5 naval (`NAVAL_SPEC.md` §3.2/§8):** the authored Wooden Wall — `{nation: row}`. A FLEET row: `ships` int 1–150 + REQUIRED `readiness` 40–100, optional `admiral` (display string, never an object), `ports` (non-negative int — the Continental System closure weight; island rows are excluded from the denominator), `dockyards` (non-empty list of provinces the nation CONTROLS at boot — the build sites; conquest grants yards at runtime, §3.4a), `island` (bool — the blockade war-weariness clause + the blockade-at-war AI doctrine), `trade_dominance` (non-negative int — absorbs the old Britain coastal naval_income; scaled ×(1−closure), floor ×0.4, suspended under blockade), `overseas_income` (int 0–1200, validator-clamped — **EB-2, the Econ Balance gate Aug 7 2026, `ECON_BALANCE_GATE_2026_08_07.md` §3:** the authored colonial/overseas pool, colonies as a MODIFIER never map objects; the trade-dominance HOLDER scales it ×(1−closure) floor ×0.4 and loses it under blockade; a NON-holder colonial power loses it while blockaded, keeps ×0.25 while at war with the dominance holder, full otherwise; renders as its own positive "Overseas Trade" ledger component; on the 1805 boot Britain 500 / Spain 250 / Holland 150 / Portugal 150 and France deliberately authors NONE — its overseas arm is continental Requisitions), `camp_provinces` (the §5.3 Descent staging shores). A `ships: 0` row is PORTS-ONLY — it authors the closure denominator and may NOT carry `readiness` or `dockyards` (both are validation errors). Omitting the whole block keeps the naval layer dormant (no crossing gate, no blockade, no Admiralty). The over-true registry `is_coastal` flag is never read for coverage/closure/building (§3.4 — DEF-8 untriggered); coverage keys off the registry's hand-authored `sea_links`, closure off `ports`, building off `dockyards`. |
| `formable_nations` | object | {} | **Nation Agendas NA-6c (`NATION_AGENDAS_SPEC.md` §11.4):** the CATALOGUE of client states a conquering side may carve out of a defeated party's soil at the settlement table via the `create_client` clause. `{tag: template}` — the KEY is the new nation tag and must NOT collide with a live nation (that is an ERROR: erecting a state that already exists is incoherent and would silently re-home a live court's regions). Each template: REQUIRED non-empty `display_name` (the tag is never shown to the player) and a REQUIRED non-empty `provinces` list (the whole carve eligibility predicate — every province must be held by the carver's bloc AND have belonged to the court being carved, per its registry `starting_controller`); optional `flag` (heraldry asset tag, defaults to `display_name` with spaces stripped), `blurb` (the Proclamation's engraved line), `aggrieved` (nations taking the §11.9 one-time −30 relation blow with both the new state and its sponsor — roster misses WARN), `grudge_label` (NA-6d — the threat panel's name for the standing wound; string), `seeds` (`gold` non-negative int, default 500; optional `manpower`, `actions`, `authority`, and a `diplomat` record in the `{name, personality, skill, biography}` shape), and `deck` (the client's own agenda deck, held to the IDENTICAL schema as an authored `agendas` deck — it lies dormant while the client answers to a lord, and a deck entry carrying a `forms` block makes the client itself formable later, the C-to-T chain). **Nothing in this block exists at boot** — it is a catalogue of what MAY be erected, not a roster. Any side may carve (GR5): the shipped Duchy of Normandy is the coalition-side mirror, carved from French home soil. A new tag also needs its companion rows — `NATION_DESIRE_PROFILES` + `TALLEYRAND_COMMENTARY` (both degrade SILENTLY), `NATION_POWER_TIERS` (unauthored = `secondary`, a middle power), `Utils.NATION_COLORS` (unauthored = bug-magenta) and a heraldry SVG with its `.import` sibling. |

### Europe-map scenarios (1805 Loader pre-slice)

With `"sovereign_map": "europe"`:

- Omitting `regions` injects the validated 126-province Europe world (`create_europe_regions()`) — you do not inline 126 region dicts.
- Omitting `marshals` yields an **army-less** start (the legacy marshal roster is never injected — its locations don't exist on the Europe map).
- Omitted roster surfaces (`nation_gold`, `nation_actions`, `nation_authority`, `diplomats`, `manpower_pools`, `enemy_nations`, `vassals`) keep the Europe world's own construction-time values, including the 3 seeded French satellite vassals.
- `max_turns` defaults to **60** on the Europe world (legacy stays 40).
- Nation references validate against the 20-nation Europe roster (`EUROPE_NATION_CAPITALS` + the Europe diplomat cast).
- To boot the backend directly into a scenario, set the `SOVEREIGN_SCENARIO` environment variable to the file path — the import-time bootstrap and `/new_game` both load it via `WorldState.from_scenario` (missing/invalid files fail loudly).

### Nations in schema v1

When a scenario defines nation records, keep authored static taxonomy separate from runtime diplomatic state:

- `power_tier` is authored scenario data: `major`, `secondary`, or `minor`
- `political_status` is runtime state (`independent`, `vassal`, `protectorate`, etc.) and should not be hardcoded into the scenario taxonomy as a substitute for `power_tier`

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
| `personality` | string | "balanced" | One of: `aggressive`, `cautious`, `literal` — the ONLY valid authoring values (MC-4, July 10, 2026: `balanced`/`loyal` are retired reserved values, a hard validation ERROR — a scenario authoring one cannot boot). Omitting the field falls back to the inert save-compat default `"balanced"` (no objection triggers ever fire) and logs a boot warning — author the field explicitly. |
| `nation` | string | "France" | Nation this marshal belongs to |
| `cavalry` | boolean | false | If true, has cavalry movement/abilities |
| `artillery` | boolean | false | If true, an artillery marshal — bombardment, +damage, fort degradation; cannot melee-attack. Mutually exclusive with `cavalry`. A commissioned artillery candidate raises its corps (`RECRUIT_ARTILLERY_CORPS`, 3,000) from the nation's `artillery` manpower pool, not infantry. See `docs/ARTILLERY_GAP_SPEC.md`. |
| `movement_range` | integer | 1 | Regions can move per turn (cavalry often 2) |
| `tactical_skill` | integer | 5 | Overall tactical rating (1-10) |
| `morale` | integer | 70 | Starting morale (0-100) |
| `stance` | string | "neutral" | One of: `neutral`, `defensive`, `aggressive` |
| `skills` | object | null | Individual skill ratings |
| `ability` | object | null | Special ability |
| `trust` | object | `{"value": 70}` | Starting trust in the player, `{"value": 0-100}` (MC-2: the shipped 1805 roster authors this per marshal) |
| `relationships` | object | `{}` | Starting relationships with other marshals by name, `{"Name": -2..2}`. −2 Hostile (coordination ×0.0, refuses unordered reinforcement) · −1 Rival (×0.5) · +1 Friendly (×1.25) · +2 Devoted (×1.5); also ±10/step on the reinforcement arrival score. Values outside −2..+2 are a validation ERROR (loaded raw, never clamped); a target not in the roster is a validation warning (the edge is never read). Author both directions if you want a symmetric pair — marshals load independently (MC-3: the shipped 1805 roster authors 13 symmetric pairs) |

### Personality Types

| Personality | Behavior |
|-------------|----------|
| `aggressive` | Prefers attacking, objects to defensive orders |
| `cautious` | Prefers defense, objects to risky attacks |
| `literal` | Follows orders exactly, never objects (the Literal Doctrine) |

`balanced` and `loyal` are RETIRED reserved values (MC-4, July 10, 2026) — no shipped marshal uses them, they carry no objection triggers or combat modifiers, and the validator rejects them. They survive only as save-load fallbacks.

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

Wired seams (what a point buys): `tactical` — combat dice (+1 per 3 pts);
`shock` — attack damage (+5%/pt); `defense` — damage resistance (−5%/pt);
`logistics` — reinforcement muster score (+5/pt); `command` — The Rally
(recovery 2 stages/turn at 8+, retreat penalties 10pp deeper at 3−).
`administration` is accepted and serialized but currently UNWIRED (reserved
for the MC-2b slice) — the marshal card hides it until its mechanic lands.

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
    "income_value": 300,
    "is_capital": true,
    "terrain": "urban",
    "region_type": "capital",
    "controller": "France",
    "garrison_strength": 5000,
    "stability": 100,
    "war_damage": 0.0
}
```

### Region Field Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | **REQUIRED** | Region's name |
| `adjacent_regions` | array | **REQUIRED** | List of connected region names |
| `income_value` | integer | 100 | Gold per turn when controlled |
| `is_capital` | boolean | false | If true, losing this loses the game |
| `terrain` | string | "plains" | Terrain type (see below). Affects defense, movement cost, cavalry, supply |
| `region_type` | string | "town" | Region type (see below). Determines income. Valid: capital, major_city, city, town, rural |
| `controller` | string | null | Nation that controls this region |
| `garrison_strength` | integer | 0 | Troops defending (not marshal) |
| `stability` | integer | 100 | Region stability (0-100). Affects income via tiers: 0-25=Hostile (0%), 26-50=Unrest (25%), 51-75=Settling (75%), 76-100=Stable (100%). Set to 25 on capture. |
| `war_damage` | float | 0.0 | War damage (0.0-0.5). Reduces income multiplicatively. Applied by battles, recovers -0.02/turn. |
| `plundered` | boolean | false | True if region was plundered on capture. Clears when stability > 50. |
| `buildings` | array | [] | Built buildings: `[{"type": "supply_depot", "damaged": false}]`. Types: supply_depot, fortification, training_ground. |
| `building_under_construction` | object\|null | null | Active construction project: `{"type": "supply_depot", "turns_remaining": 2}`. |

### Terrain Types

The `terrain` field controls combat bonuses, pathfinding costs, and cavalry effectiveness. Valid values:

| Terrain | Defense Bonus | Movement Cost | Cavalry Eff. | Charge Blocked |
|---------|-------------|---------------|-------------|----------------|
| `plains` | +0% | 1.0x | 1.2x | No |
| `forest` | +10% | 1.3x | 0.5x | Yes |
| `hills` | +15% | 1.2x | 0.8x | No |
| `mountains` | +25% | 2.0x | 0.3x | Yes |
| `urban` | +20% | 1.0x | 0.5x | Yes |
| `river_crossing` | +15% | 1.5x | 0.6x | No |

- **Defense Bonus**: Defender gets this bonus in combat
- **Movement Cost**: Dijkstra weight for MOVE_TO pathfinding (higher = costlier to enter)
- **Cavalry Eff.**: Multiplier on cavalry combat bonuses (lower = weaker cavalry)
- **Charge Blocked**: If yes, Glorious Charge (recklessness 3+) downgrades to normal attack

The `terrain` field is separate from `region_type`. Terrain affects combat/movement; region type affects income. Both default if omitted (`terrain` → "plains", `region_type` → "town").

### Region Types

The `region_type` field determines base income:

| Region Type | Income | Description |
|-------------|--------|-------------|
| `capital` | 300 | National capital |
| `major_city` | 200 | Large strategic city |
| `city` | 150 | Medium city |
| `town` | 100 | Small settlement (default) |
| `rural` | 50 | Countryside/village |

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

Current format version: **1.1**
