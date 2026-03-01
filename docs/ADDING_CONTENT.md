# Adding Content Guide

Step-by-step guides for adding new marshals, personalities, and strategic commands.

---

## Table of Contents

1. [Adding a New Marshal](#1-adding-a-new-marshal)
   - [Pre-Flight Checklist](#pre-flight-checklist)
   - [Auto-Inherited Mechanics](#auto-inherited-mechanics)
   - [Marshal Data Questionnaire](#marshal-data-questionnaire)
   - [Complete File Reference](#complete-file-reference)
   - [Step-by-Step Implementation](#step-by-step-implementation)
   - [Code Templates](#code-templates)
   - [Validation Checklist](#validation-checklist)
   - [Common Pitfalls (Marshals)](#common-pitfalls-marshals)
   - [Troubleshooting (Marshals)](#troubleshooting-marshals)
   - [Quick Reference Tables](#quick-reference-tables)
   - [Adding New Nations](#adding-new-nations)
   - [Adding New Personalities](#adding-new-personalities)
   - [Worked Example: Adding Marshal Murat](#worked-example-adding-marshal-murat)
   - [Wiring a Special Ability (Full Checklist)](#wiring-a-special-ability-full-checklist)
   - [1805 Roster Planning Notes](#1805-roster-planning-notes)
2. [Adding a New Strategic Command Type](#2-adding-a-new-strategic-command-type)
   - [Checklist](#checklist)
   - [Worked Example: PATROL Command](#worked-example-patrol-command)
   - [Common Pitfalls (Strategic Commands)](#common-pitfalls-strategic-commands)
3. [Expanding the Map](#3-expanding-the-map)
   - [Region Data Questionnaire](#region-data-questionnaire)
   - [Complete File Reference (Regions)](#complete-file-reference-regions)
   - [Step-by-Step: Adding a New Region](#step-by-step-adding-a-new-region)
   - [Step-by-Step: Renaming a Region](#step-by-step-renaming-a-region)
   - [Grep Verification Commands](#grep-verification-commands)
   - [Adjacency Validation Script](#adjacency-validation-script)
   - [Test Fix Guide](#test-fix-guide)
   - [Victory Threshold Scaling](#victory-threshold-scaling)
   - [Common Pitfalls (Map Expansion)](#common-pitfalls-map-expansion)
   - [Quick Reference: Current 13-Region Map](#quick-reference-current-13-region-map)

---

## 1. Adding a New Marshal

Complete guide for adding new marshals to Ink & Iron: Napoleonic Wars. Covers EVERY file that must be modified, with copy-paste templates and validation checklists.

---

### Pre-Flight Checklist

Answer these questions BEFORE writing any code:

#### Basic Questions
- [ ] **Name:** What is the marshal's full name? (e.g., "Murat", "Lannes")
- [ ] **Nation:** What nation does this marshal belong to?
  - [ ] France (player)
  - [ ] Britain (enemy)
  - [ ] Prussia (enemy)
  - [ ] Austria (enemy - not yet in game)
  - [ ] Russia (enemy - not yet in game)
  - [ ] Other: ____________
- [ ] **Is this a new nation?** If yes, you'll need extra steps (see [Adding New Nations](#adding-new-nations))

#### Marshal Type
- [ ] **Player or Enemy?**
  - [ ] Player marshal (French) → Add to `create_starting_marshals()`
  - [ ] Enemy marshal → Add to `create_enemy_marshals()`

#### Personality Type
- [ ] **Which personality?**
  - [ ] `aggressive` - Attacks readily, objects to defensive orders
  - [ ] `cautious` - Defensive-minded, objects to risky attacks
  - [ ] `literal` - Follows orders exactly, never improvises
  - [ ] `balanced` - Mix of traits (placeholder, not fully implemented)
  - [ ] `loyal` - Extreme obedience (placeholder, not fully implemented)
  - [ ] **NEW personality type?** See [Adding New Personalities](#adding-new-personalities)

> **IMPORTANT: Personality = Auto-Inherited Mechanics!**
> - `aggressive` → +15% base attack, 10% max fortify, cavalry limits apply
> - `cautious` → **Counter-Punch** (free attack after defense!), +20% defense stance, 20% max fortify
> - `literal` → **Immovable** (+15% def when holding position)
>
> See [Auto-Inherited Mechanics](#auto-inherited-mechanics) for full details.

#### Unit Type
- [ ] **Infantry or Cavalry?**
  - [ ] Infantry (`cavalry=False`, `movement_range=1`)
  - [ ] Cavalry (`cavalry=True`, `movement_range=2`)

> **IMPORTANT: Cavalry = Special Mechanics!**
> - 2-region attack range
> - Cannot hold defensive positions >3 turns (-3 trust auto-switch)
> - **Aggressive + Cavalry** → Full **Recklessness System** (Ney-style gameplay!)
>
> See [Auto-Inherited Mechanics](#auto-inherited-mechanics) for full details.

#### Special Abilities
- [ ] Does this marshal have unique abilities?
  - [ ] Yes → Define ability and triggers
  - [ ] No → Use default ability structure

---

### Auto-Inherited Mechanics

**CRITICAL:** Many mechanics are automatically inherited based on personality and unit type. You don't implement these - they just work. Your marshal's signature ability should be something UNIQUE beyond these inherited mechanics.

#### Mechanics by Personality

| Personality | Auto-Inherited Mechanics | Source |
|-------------|--------------------------|--------|
| **aggressive** | +15% base attack bonus | `personality_modifiers.py` |
| | +5% additional attack in aggressive stance (total +20%) | |
| | -5% defense penalty in aggressive stance | |
| | Max 10% fortify (impatient) | |
| **cautious** | **Counter-Punch:** Free attack after successful defense | `combat.py` |
| | +5% additional defense in defensive stance (total +20%) | `personality_modifiers.py` |
| | +10% defense when outnumbered | |
| | -5% attack in aggressive stance (hesitant) | |
| | -10% attack at bad odds (ratio < 1:1) | |
| | +3%/turn fortify rate (not +2%), max 20% | |
| | +5% instant fortify bonus on first turn | |
| **literal** | **Immovable:** +15% defense when holding position | `personality_modifiers.py` |
| | Use `hold` command to activate `holding_position=True` | `marshal.py` |
| **balanced** | No special bonuses (baseline modifiers only) | - |

#### Mechanics by Unit Type

| Unit Type | Auto-Inherited Mechanics | Source |
|-----------|--------------------------|--------|
| **Cavalry** (`cavalry=True`) | 2-region attack range | `marshal.py` |
| | Defensive stance limit: 3 turns max, then auto-switch to aggressive (-3 trust) | `world_state.py` |
| | Fortify limit: 3 turns max, then auto-unfortify (-3 trust) | `world_state.py` |
| **Infantry** (`cavalry=False`) | Standard 1-region attack range | `marshal.py` |
| | No defensive limits (can hold positions indefinitely) | - |

#### COMBO: Aggressive + Cavalry = Recklessness System

When a marshal has BOTH `personality="aggressive"` AND `cavalry=True`, they automatically inherit the **full Recklessness System**. This is a major gameplay mechanic.

**Current marshals with Recklessness:** Ney
**Future marshals that would inherit:** Murat, Lasalle, any aggressive cavalry

| Recklessness Level | Attack Bonus | Defense Penalty | Restrictions |
|--------------------|--------------|-----------------|--------------|
| 0 | - | - | None |
| 1 | +5% | - | Can use `charge` command |
| 2 | +10% | -5% | Cannot use defensive stance |
| 3 | +15% | -10% | Cannot use defensive/neutral, popup before attack |
| 4+ | +20% | -15% | Auto-charge at turn start |

**Recklessness changes:**
- **+1:** Win battle AS ATTACKER
- **Reset to 0:** Lose any battle OR execute Glorious Charge
- **Glorious Charge (level 3+):** 2x casualties both sides, -20 enemy morale

#### Quick Inheritance Matrix

| Personality | Unit Type | Counter-Punch? | Recklessness? | Immovable? | Max Fortify |
|-------------|-----------|----------------|---------------|------------|-------------|
| aggressive | infantry | No | No | No | 10% |
| aggressive | cavalry | No | **YES** | No | 10%* |
| cautious | infantry | **YES** | No | No | 20% |
| cautious | cavalry | **YES** | No | No | 20%* |
| literal | infantry | No | No | **YES** | 15% |
| literal | cavalry | No | No | **YES** | 15%* |
| balanced | infantry | No | No | No | 15% |
| balanced | cavalry | No | No | No | 15%* |

*Cavalry: fortification auto-removed after 3 turns anyway

#### Signature Abilities: What They Should Be

Since so much is auto-inherited, signature abilities should be **UNIQUE**:

**Good examples:**
- Davout's "Free Unfortify" (0 action cost) - unique mechanic
- A coordination bonus when supporting allies - unique trigger
- Special morale effects under specific conditions - unique effect

**Bad examples (already inherited):**
- "Gets +10% attack bonus" - already from aggressive personality
- "Free attack after defense" - already Counter-Punch from cautious
- "Builds recklessness from victories" - already from aggressive+cavalry

For detailed mechanics reference, see [MARSHAL_MECHANICS_REFERENCE.md](MARSHAL_MECHANICS_REFERENCE.md).

---

### Marshal Data Questionnaire

Fill out this sheet completely before implementing:

```
+-------------------------------------------------------------+
| MARSHAL DATA SHEET                                          |
+-------------------------------------------------------------+
|                                                             |
| IDENTITY                                                    |
| ----------------------------------------------------------- |
| Name: _______________________________________________       |
| Nation: _____________________________________________       |
| Historical Title: ___________________________________       |
|   (e.g., "King of Naples", "Iron Marshal")                 |
|                                                             |
| PERSONALITY & UNIT TYPE                                     |
| ----------------------------------------------------------- |
| Personality: [ ] aggressive  [ ] cautious  [ ] literal      |
|              [ ] balanced    [ ] loyal                      |
|                                                             |
| Unit Type:   [ ] Infantry (movement_range=1)                |
|              [ ] Cavalry  (movement_range=2, cavalry=True)  |
|                                                             |
| STARTING STATE                                              |
| ----------------------------------------------------------- |
| Starting Region: ____________________________________       |
|   (Must exist in region.py - see Quick Reference)          |
|                                                             |
| Strength: ______________ (typical: 30,000 - 80,000)         |
| Starting Trust: ________ (typical: 60-85, French only)     |
|                                                             |
| Spawn Location: _________________ (capital for respawn)     |
|   (French = "Paris", Britain = "Waterloo", etc.)           |
|                                                             |
| SKILLS (1-10 scale, 5 = average)                            |
| ----------------------------------------------------------- |
| Tactical:       ____ (combat rolls, flanking bonuses)       |
| Shock:          ____ (attack damage, pursuit effectiveness) |
| Defense:        ____ (defender bonus, retreat casualties)   |
| Logistics:      ____ (supply range - Phase 5)               |
| Administration: ____ (recruitment speed, desertion)         |
| Command:        ____ (morale, discipline)                   |
|                                                             |
| Legacy tactical_skill: ____ (0-12, used for dice rolls)     |
|                                                             |
| SIGNATURE ABILITY                                           |
| ----------------------------------------------------------- |
| Ability Name: ________________________________________      |
| Description: _________________________________________      |
| Trigger: _____________________________________________      |
|   (when_attacking, morale_drops_below_50, etc.)            |
| Effect: ______________________________________________      |
|                                                             |
| RELATIONSHIPS (with existing marshals)                      |
| ----------------------------------------------------------- |
| Format: Marshal Name -> Value (-2 to +2)                    |
|   -2=Hostile, -1=Rival, 0=Professional, +1=Friendly, +2=Devoted |
|                                                             |
| _________________ -> ____                                   |
| _________________ -> ____                                   |
| _________________ -> ____                                   |
| _________________ -> ____                                   |
|                                                             |
| REMEMBER: Relationships must be set BIDIRECTIONALLY!        |
| If Murat likes Ney (+1), you must also set Ney's opinion    |
| of Murat (could be different value).                        |
|                                                             |
+-------------------------------------------------------------+
```

---

### Complete File Reference

#### Every File That Might Need Modification

**Backend Files (Required)**

| File | Purpose | When to Modify |
|------|---------|---------------|
| `backend/models/marshal.py` | Marshal creation | **ALWAYS** - Add marshal definition |
| `backend/commands/parser.py` | Name fuzzy matching | **ALWAYS** - Add to valid_marshals |

**Backend Files (Conditional)**

| File | Purpose | When to Modify |
|------|---------|---------------|
| `backend/models/personality_modifiers.py` | Combat bonuses | If NEW personality type |
| `backend/models/personality.py` | Objection triggers | If NEW personality type |
| `backend/commands/executor.py` | Special abilities | If unique combat mechanics |
| `backend/game_logic/combat.py` | Combat resolution | If unique combat triggers |
| `backend/ai/enemy_ai.py` | AI behavior | If enemy marshal with special AI |
| `backend/models/world_state.py` | Nation management | If NEW nation |
| `backend/ai/llm_client.py` | LLM keyword matching | If special command keywords |

**Frontend/Godot Files (Conditional)**

| File | Purpose | When to Modify |
|------|---------|---------------|
| `godot-client/.../scenes/map.gd` | Nation colors | If NEW nation |
| `godot-client/.../scripts/main.gd` | Marshal display | Rarely (auto-handles) |

**Test Files (Required)**

| File | Purpose | When to Modify |
|------|---------|---------------|
| `tests/test_marshal_abilities.py` | Ability tests | **ALWAYS** - Add ability tests |
| `tests/test_marshal_skills.py` | Skill tests | If special skill values |
| `tests/test_enemy_ai.py` | AI behavior | If enemy marshal |

**Documentation (Required)**

| File | Purpose | When to Modify |
|------|---------|---------------|
| `CLAUDE.md` | Master reference | **ALWAYS** - Update marshal list |
| `CHANGELOG.md` | Version history | **ALWAYS** - Document addition |

---

### Step-by-Step Implementation

#### Step 1: Add Marshal Definition

**File:** `backend/models/marshal.py`

**Location:**
- French marshals: Add to `create_starting_marshals()` (line ~717)
- Enemy marshals: Add to `create_enemy_marshals()` (line ~817)

**Action:** Add marshal to the appropriate function.

#### Step 2: Update Parser Valid Marshals

**File:** `backend/commands/parser.py`

**Location:** Line ~30

```python
# Before
self.valid_marshals = ["Ney", "Davout", "Grouchy", "Murat"]

# After (add your marshal)
self.valid_marshals = ["Ney", "Davout", "Grouchy", "Murat", "NewMarshal"]
```

#### Step 3: Update Known Enemies (if enemy marshal)

**File:** `backend/commands/parser.py`

**Location:** Line ~68

```python
# Before
self.known_enemies = ["Wellington", "Blucher"]

# After (add enemy marshal)
self.known_enemies = ["Wellington", "Blucher", "NewEnemy"]
```

#### Step 4: Set Up Bidirectional Relationships

**File:** `backend/models/marshal.py`

**Location:** After all marshals are created in the function

**CRITICAL:** Every relationship must be set in BOTH directions!

```python
# Example: Murat and Ney are friends
marshals["Murat"].set_relationship("Ney", 1)     # Murat likes Ney
marshals["Ney"].set_relationship("Murat", 1)     # Ney likes Murat

# Example: Asymmetric relationship
marshals["Murat"].set_relationship("Davout", 0)  # Murat is neutral
marshals["Davout"].set_relationship("Murat", -1) # Davout dislikes Murat
```

#### Step 5: Add Personality Modifiers (if new personality)

**File:** `backend/models/personality_modifiers.py`

See [Adding New Personalities](#adding-new-personalities) section.

#### Step 6: Add to Enemy AI (if enemy marshal)

**File:** `backend/ai/enemy_ai.py`

Enemy marshals automatically use the AI system. Verify:
- Marshal's personality threshold in `_get_attack_threshold()` (~line 500)
- Nation is in `world.enemy_nations` list

#### Step 7: Update Godot Nation Colors (if new nation)

**File:** `godot-client/project-sovereign/scenes/map.gd`

**Location:** Line ~38 (COLORS constant)

```gdscript
const COLORS = {
    "France": Color(0.255, 0.412, 0.882),   # Royal Blue
    "Britain": Color(0.863, 0.078, 0.235),  # Crimson
    "Prussia": Color(0.2, 0.2, 0.2),        # Dark Gray
    "Austria": Color(1.0, 0.843, 0.0),      # Gold
    "NewNation": Color(R, G, B),            # Add new nation color
    "Neutral": Color(0.565, 0.933, 0.565),  # Light Green
    "connection": Color(0.6, 0.6, 0.6)      # Gray
}
```

#### Step 8: Add Tests

**File:** `tests/test_marshal_abilities.py`

Create a test class for the new marshal's ability:

```python
class TestNewMarshalAbility:
    """Test NewMarshal's ability."""

    def test_new_marshal_has_ability(self):
        """Verify NewMarshal has ability defined."""
        # Test code here
        pass

    def test_new_marshal_ability_triggers(self):
        """Verify ability triggers correctly."""
        # Test code here
        pass
```

#### Step 9: Run All Tests

```bash
# Run all tests
pytest tests/ -v

# Run comprehensive test
pytest test_conquest_comprehensive.py -v

# Run specific marshal tests
pytest tests/test_marshal_abilities.py -v
```

#### Step 10: Manual Testing

Start the game and verify:
- [ ] Marshal appears on map in correct location
- [ ] Marshal shows correct nation color
- [ ] Hovering shows correct stats in tooltip
- [ ] Marshal responds to commands (if player)
- [ ] Enemy AI controls marshal correctly (if enemy)
- [ ] No console errors or warnings

#### Step 11: Update Documentation

**File:** `CLAUDE.md`

Update the marshal list in the quick reference section.

**File:** `CHANGELOG.md`

Add entry for the new marshal.

---

### Code Templates

#### Template A: French Player Marshal

Copy this template and fill in the values:

```python
# Add to create_starting_marshals() in backend/models/marshal.py

"NewMarshal": Marshal(
    name="NewMarshal",
    location="Paris",                    # Starting region
    strength=50000,                      # Army size
    personality="aggressive",            # aggressive/cautious/literal
    nation="France",
    movement_range=1,                    # 1=infantry, 2=cavalry
    tactical_skill=7,                    # 0-12 for dice rolls
    skills={
        "tactical": 7,                   # 1-10 scale
        "shock": 7,
        "defense": 5,
        "logistics": 5,
        "administration": 5,
        "command": 7
    },
    ability={
        "name": "Ability Name",
        "description": "What the ability does",
        "trigger": "when_attacking",     # or other trigger
        "effect": "Effect description"
    },
    starting_trust=70,                   # 50-85 typical
    cavalry=False,                       # True for cavalry commanders
    spawn_location="Paris"               # Respawn location
),
```

#### Template B: Enemy Marshal

Copy this template and fill in the values:

```python
# Add to create_enemy_marshals() in backend/models/marshal.py

"NewEnemy": Marshal(
    name="NewEnemy",
    location="Vienna",                   # Starting region
    strength=45000,                      # Army size
    personality="cautious",              # aggressive/cautious/literal
    nation="Austria",                    # Enemy nation
    movement_range=1,                    # 1=infantry, 2=cavalry
    tactical_skill=6,                    # 0-12 for dice rolls
    skills={
        "tactical": 6,                   # 1-10 scale
        "shock": 5,
        "defense": 7,
        "logistics": 6,
        "administration": 6,
        "command": 6
    },
    ability={
        "name": "Ability Name",
        "description": "What the ability does",
        "trigger": "trigger_condition",
        "effect": "TODO: Implement in Phase X"
    },
    starting_trust=70,                   # Enemies also have trust (for future)
    spawn_location="Vienna"              # Respawn location
),
```

#### Template C: Relationship Setup

Add after all marshals are created in the function:

```python
# ================================================================
# SCENARIO NAME: Historical Relationships
# ================================================================

# NewMarshal's relationships
marshals["NewMarshal"].set_relationship("Ney", 1)      # Friendly
marshals["NewMarshal"].set_relationship("Davout", 0)   # Professional
marshals["NewMarshal"].set_relationship("Grouchy", -1) # Rival

# Reciprocal relationships (REQUIRED!)
marshals["Ney"].set_relationship("NewMarshal", 1)      # Mutual friendship
marshals["Davout"].set_relationship("NewMarshal", 0)   # Mutual professionalism
marshals["Grouchy"].set_relationship("NewMarshal", -1) # Mutual rivalry
```

#### Template D: Test Class

```python
# Add to tests/test_marshal_abilities.py

class TestNewMarshalAbilityName:
    """Test NewMarshal's 'Ability Name' ability."""

    def test_new_marshal_has_ability(self):
        """Verify NewMarshal has the ability defined."""
        marshals = create_starting_marshals()  # or create_enemy_marshals()
        new_marshal = marshals["NewMarshal"]

        assert new_marshal.ability["name"] == "Ability Name"
        assert new_marshal.ability["trigger"] == "trigger_condition"

    def test_new_marshal_starting_stats(self):
        """Verify NewMarshal has correct starting stats."""
        marshals = create_starting_marshals()
        new_marshal = marshals["NewMarshal"]

        assert new_marshal.strength == 50000
        assert new_marshal.location == "Paris"
        assert new_marshal.personality == "aggressive"
        assert new_marshal.skills["shock"] == 7

    def test_new_marshal_relationships(self):
        """Verify NewMarshal relationships are bidirectional."""
        marshals = create_starting_marshals()

        # Check NewMarshal's view
        assert marshals["NewMarshal"].get_relationship("Ney") == 1

        # Check reciprocal (CRITICAL!)
        assert marshals["Ney"].get_relationship("NewMarshal") == 1
```

---

### Validation Checklist

Before committing, verify ALL items:

#### Marshal Definition
- [ ] Name is unique (not already in `self.marshals`)
- [ ] Nation exists in game (or you've added it)
- [ ] Personality is valid: `aggressive`, `cautious`, `literal`, `balanced`, `loyal`
- [ ] Starting region exists in `backend/models/region.py`
- [ ] Skills are all in range 1-10
- [ ] Tactical skill is in range 0-12
- [ ] Strength is reasonable (15,000 - 100,000 typical)
- [ ] Movement range is 1 (infantry) or 2 (cavalry)
- [ ] If cavalry: `cavalry=True` is set
- [ ] Spawn location exists and makes sense for nation
- [ ] Ability has all 4 fields: name, description, trigger, effect

#### Relationships
- [ ] All relationships are set BIDIRECTIONALLY
- [ ] Relationship values are in range -2 to +2
- [ ] Historical accuracy (if applicable)

#### Parser
- [ ] Marshal name added to `valid_marshals` list
- [ ] If enemy: name added to `known_enemies` list
- [ ] Name doesn't conflict with existing names (case-insensitive)
- [ ] Fuzzy matching works (test with typos)

#### Tests
- [ ] Test class created for new marshal
- [ ] Tests verify ability definition
- [ ] Tests verify starting stats
- [ ] Tests verify bidirectional relationships
- [ ] All tests pass: `pytest tests/ -v`

#### Frontend (if new nation)
- [ ] Nation color added to `map.gd` COLORS constant
- [ ] Color is visually distinct from existing nations

#### Documentation
- [ ] CLAUDE.md updated with new marshal
- [ ] CHANGELOG.md has entry for addition

#### Manual Testing
- [ ] Game starts without errors
- [ ] Marshal appears on map
- [ ] Tooltip shows correct info
- [ ] Commands work (if player marshal)
- [ ] AI controls correctly (if enemy marshal)

---

### Common Pitfalls (Marshals)

#### Pitfall 1: One-Sided Relationships

**WRONG:**
```python
marshals["Murat"].set_relationship("Ney", 1)
# Murat likes Ney, but what does Ney think of Murat?
```

**RIGHT:**
```python
marshals["Murat"].set_relationship("Ney", 1)
marshals["Ney"].set_relationship("Murat", 1)  # Must set both!
```

#### Pitfall 2: Wrong Movement Range for Cavalry

**WRONG:**
```python
Marshal(
    name="Murat",
    cavalry=True,
    movement_range=1,  # WRONG! Cavalry should have range 2
    ...
)
```

**RIGHT:**
```python
Marshal(
    name="Murat",
    cavalry=True,
    movement_range=2,  # Cavalry gets 2-tile attack range
    ...
)
```

#### Pitfall 3: Nonexistent Starting Region

**WRONG:**
```python
Marshal(
    name="SomeGeneral",
    location="London",  # London doesn't exist in the 13-region test map!
    ...
)
```

**RIGHT:**
```python
# Check backend/models/region.py for valid regions:
# Paris, Belgium, Netherlands, Waterloo, Rhine, Bavaria, Vienna,
# Lyon, Marseille, Geneva, Milan, Brittany, Bordeaux
Marshal(
    name="SomeGeneral",
    location="Vienna",  # Valid region
    ...
)
```

#### Pitfall 4: Skills Outside Valid Range

**WRONG:**
```python
skills={
    "tactical": 15,  # WRONG! Max is 10
    "shock": 0,      # WRONG! Min is 1
    ...
}
```

**RIGHT:**
```python
skills={
    "tactical": 10,  # Max valid value
    "shock": 1,      # Min valid value
    ...
}
```

#### Pitfall 5: Forgetting to Update Parser

Marshal is added but commands don't work:

```python
# parser.py - MUST ADD TO THIS LIST:
self.valid_marshals = ["Ney", "Davout", "Grouchy", "NewMarshal"]  # Added!

# For enemies:
self.known_enemies = ["Wellington", "Blucher", "NewEnemy"]  # Added!
```

#### Pitfall 6: Missing Nation Color in Godot

New nation's marshals appear as magenta on map (debug color).

Check `godot-client/.../scenes/map.gd`:
```gdscript
const COLORS = {
    # ...existing colors...
    "NewNation": Color(R, G, B),  # Must add this!
}
```

#### Pitfall 7: Not Adding Tests

Marshal seems to work but breaks in edge cases. Always add:
- Ability definition test
- Starting stats test
- Relationship bidirectionality test

#### Pitfall 8: Cavalry Without cavalry=True

Marshal has `movement_range=2` but `cavalry=False`:
- Won't get cavalry limits (restlessness system)
- Won't get cavalry-specific abilities

```python
# If movement_range=2, cavalry should be True:
Marshal(
    movement_range=2,
    cavalry=True,  # Must match!
    ...
)
```

---

### Troubleshooting (Marshals)

| Problem | Likely Cause | Solution |
|---------|--------------|----------|
| Marshal doesn't appear on map | Not added to create_*_marshals() | Add to correct function in marshal.py |
| Marshal not at expected location | Region name typo | Check region exists in region.py |
| Commands don't recognize marshal | Not in parser valid_marshals | Add to parser.py line ~30 |
| Enemy AI doesn't control marshal | Nation not in enemy_nations | Check world_state.py line ~114 |
| Nation color is magenta | Missing from COLORS dict | Add to map.gd line ~38 |
| Fuzzy matching fails | Name conflicts with existing | Use more unique name |
| Tests failing | Missing test updates | Add tests in test_marshal_abilities.py |
| Relationship only one-way | Forgot reciprocal | Set both directions |
| Attack range wrong | movement_range mismatch | Set 1 for infantry, 2 for cavalry |
| Cavalry limits not working | cavalry=False | Set cavalry=True for cavalry units |
| Skill modifiers not applying | New personality, no modifiers | Add to personality_modifiers.py |
| Marshal respawns wrong place | Wrong spawn_location | Set to nation capital |
| Tooltip shows wrong info | Skill values out of range | Keep skills 1-10 |

---

### Quick Reference Tables

#### Valid Regions (Current 13-Region Map)

| Region | Default Controller | Notes |
|--------|-------------------|-------|
| Paris | France | French capital |
| Belgium | France | Ney's start |
| Lyon | France | Interior France |
| Brittany | France | Western France |
| Bordeaux | France | Southwestern France |
| Marseille | France | Mediterranean |
| Netherlands | Britain | Blucher's start |
| Waterloo | Britain | Wellington's start |
| Rhine | Prussia | German territories |
| Bavaria | Austria | German territories |
| Vienna | Austria | Austrian capital |
| Milan | Neutral | Northern Italy |
| Geneva | Neutral | Swiss region |

#### Personality Types

| Personality | Attack Behavior | Defense Behavior | Use For |
|-------------|-----------------|------------------|---------|
| `aggressive` | +15% base attack | -5% in aggressive stance | Cavalry leaders, glory-seekers |
| `cautious` | -5% in aggressive stance | +5% in defensive stance | Defensive generals, staff officers |
| `literal` | Normal | +15% when holding | By-the-book officers (Grouchy) |
| `balanced` | Normal | Normal | Well-rounded generals |
| `loyal` | Normal | Normal | Absolutely obedient (placeholder) |

#### Skill Value Guidelines

| Value | Description | Example |
|-------|-------------|---------|
| 1-3 | Poor | Weak in this area |
| 4-5 | Average | Competent soldier |
| 6-7 | Good | Reliable professional |
| 8-9 | Excellent | Elite performer |
| 10 | Legendary | Best in Europe |

#### Typical Strength Values

| Force Type | Strength Range | Examples |
|------------|----------------|----------|
| Small corps | 15,000 - 25,000 | Light cavalry, reconnaissance |
| Medium corps | 30,000 - 50,000 | Standard army corps |
| Large corps | 50,000 - 80,000 | Main field army |
| Grande Armee | 100,000+ | Combined force |

#### Relationship Values

| Value | Label | Meaning |
|-------|-------|---------|
| -2 | Hostile | Active animosity, will undermine |
| -1 | Rival | Professional tension, competitive |
| 0 | Professional | Neutral working relationship |
| +1 | Friendly | Positive regard, cooperative |
| +2 | Devoted | Deep loyalty, will sacrifice for |

#### Historical French Marshals (For Future Addition)

| Marshal | Suggested Personality | Notes |
|---------|----------------------|-------|
| Murat | aggressive | Cavalry genius, King of Naples |
| Lannes | loyal | "Roland of the Army" |
| Soult | balanced | "Hand of Iron" |
| Massena | cautious | Defensive expert |
| Bernadotte | cautious | Future Swedish king |
| Bessieres | loyal | Imperial Guard commander |
| Mortier | balanced | Artillery expert |
| Oudinot | aggressive | "Bayard of the Army" |
| Marmont | cautious | Artillery, later traitor |
| Poniatowski | aggressive | Polish prince |

#### Historical Enemy Commanders (For Future Addition)

| Commander | Nation | Suggested Personality |
|-----------|--------|----------------------|
| Schwarzenberg | Austria | cautious |
| Archduke Charles | Austria | cautious |
| Kutuzov | Russia | cautious |
| Bagration | Russia | aggressive |
| Moore | Britain | balanced |

---

### Adding New Nations

If adding a marshal for a nation not yet in the game:

#### 1. Add Nation Color (Godot)

```gdscript
# map.gd line ~38
const COLORS = {
    # ...existing...
    "NewNation": Color(R, G, B),
}
```

#### 2. Add to Enemy Nations List

```python
# world_state.py line ~114
self.enemy_nations: List[str] = ["Britain", "Prussia", "NewNation"]

# Also add actions per nation
self.nation_actions: Dict[str, int] = {
    "Britain": 4,
    "Prussia": 4,
    "NewNation": 3,  # Adjust as appropriate
}
```

#### 3. Set Up Initial Region Control

```python
# world_state.py in _setup_initial_control()
control_map = {
    # ...existing...
    "RegionName": "NewNation",
}
```

---

### Adding New Personalities

If creating a new personality type:

#### 1. Add Modifiers

```python
# personality_modifiers.py

NEW_PERSONALITY_MODIFIERS = {
    "base_attack_bonus": 0.0,
    "base_defense_bonus": 0.0,
    # ... other modifiers
}
```

#### 2. Update Modifier Functions

```python
# personality_modifiers.py in get_personality_modifiers()
modifiers = {
    "aggressive": NEY_MODIFIERS,
    "cautious": DAVOUT_MODIFIERS,
    "literal": GROUCHY_MODIFIERS,
    "new_personality": NEW_PERSONALITY_MODIFIERS,  # Add this
}
```

#### 3. Add Objection Triggers

```python
# personality.py in PERSONALITY_TRIGGERS
Personality.NEW_TYPE: {
    'attack_weakness': 0.40,
    'defend_strong': 0.50,
    # ... objection trigger rates
}
```

---

### Worked Example: Adding Marshal Murat

Complete walkthrough of adding a new French cavalry marshal.

#### Step 1: Fill Out Data Sheet

```
Name: Murat
Nation: France
Personality: aggressive
Unit Type: Cavalry (movement_range=2, cavalry=True)
Starting Region: Lyon
Strength: 45,000
Starting Trust: 70
Spawn Location: Paris

Skills:
  Tactical: 6
  Shock: 9     (legendary cavalry charge)
  Defense: 4   (reckless, poor at defense)
  Logistics: 5
  Administration: 4
  Command: 8   (inspiring leader)

Ability: "King's Charge"
  Trigger: when_attacking_with_cavalry
  Effect: +3 Shock when leading cavalry charge

Relationships:
  Ney: +1 (fellow cavalry enthusiast)
  Davout: -1 (rivalry, Davout disapproves of Murat's style)
  Grouchy: 0 (professional)
```

#### Step 2: Add to marshal.py

```python
# In create_starting_marshals(), after Grouchy:

"Murat": Marshal(
    name="Murat",
    location="Lyon",
    strength=45000,
    personality="aggressive",
    nation="France",
    movement_range=2,
    tactical_skill=6,
    skills={
        "tactical": 6,
        "shock": 9,
        "defense": 4,
        "logistics": 5,
        "administration": 4,
        "command": 8
    },
    ability={
        "name": "King's Charge",
        "description": "Murat's legendary cavalry charges break enemy lines",
        "trigger": "when_attacking_with_cavalry",
        "effect": "+3 Shock when leading cavalry charge (TODO: Phase 2.4)"
    },
    starting_trust=70,
    cavalry=True,
    spawn_location="Paris"
),
```

#### Step 3: Add Relationships

```python
# After all marshals are created in create_starting_marshals():

# Murat's relationships
marshals["Murat"].set_relationship("Ney", 1)
marshals["Murat"].set_relationship("Davout", -1)
marshals["Murat"].set_relationship("Grouchy", 0)

# Reciprocal relationships
marshals["Ney"].set_relationship("Murat", 1)
marshals["Davout"].set_relationship("Murat", -1)
marshals["Grouchy"].set_relationship("Murat", 0)
```

#### Step 4: Update Parser

```python
# parser.py line ~30
self.valid_marshals = ["Ney", "Davout", "Grouchy", "Murat"]
```

#### Step 5: Add Tests

```python
# tests/test_marshal_abilities.py

class TestMuratKingsCharge:
    """Test Murat's 'King's Charge' ability."""

    def test_murat_has_ability(self):
        """Verify Murat has the King's Charge ability defined."""
        marshals = create_starting_marshals()
        murat = marshals["Murat"]

        assert murat.ability["name"] == "King's Charge"
        assert murat.ability["trigger"] == "when_attacking_with_cavalry"
        assert "+3 Shock" in murat.ability["effect"]

    def test_murat_is_cavalry(self):
        """Verify Murat is properly configured as cavalry."""
        marshals = create_starting_marshals()
        murat = marshals["Murat"]

        assert murat.cavalry is True
        assert murat.movement_range == 2

    def test_murat_relationships_bidirectional(self):
        """Verify Murat's relationships are set both ways."""
        marshals = create_starting_marshals()

        # Murat -> Ney
        assert marshals["Murat"].get_relationship("Ney") == 1
        # Ney -> Murat (must be set!)
        assert marshals["Ney"].get_relationship("Murat") == 1

        # Murat -> Davout
        assert marshals["Murat"].get_relationship("Davout") == -1
        # Davout -> Murat
        assert marshals["Davout"].get_relationship("Murat") == -1
```

#### Step 6: Run Tests

```bash
pytest tests/test_marshal_abilities.py -v
pytest tests/ -v
```

#### Step 7: Manual Test

1. Start backend: `python backend/main.py`
2. Open Godot client
3. Verify Murat appears at Lyon
4. Hover to check tooltip stats
5. Send command: "Murat, attack Bavaria"
6. Verify 2-tile attack range works

#### Step 8: Update Documentation

Add to CLAUDE.md and CHANGELOG.md.

#### Summary

Adding a marshal requires modifying **at minimum**:
1. `backend/models/marshal.py` - Marshal definition
2. `backend/commands/parser.py` - Valid marshals list
3. `tests/test_marshal_abilities.py` - Tests
4. `CLAUDE.md` and `CHANGELOG.md` - Documentation

Time estimate: **20-30 minutes** for a standard marshal with no new mechanics.

If adding new nation or personality: Add **30-60 minutes** for additional files.

If adding a wired special ability: See [Wiring a Special Ability](#wiring-a-special-ability-full-checklist) below.

---

### Wiring a Special Ability (Full Checklist)

Most generals are personality-driven only (aggressive/cautious/literal gives them a complete gameplay identity). Only historically distinguished commanders with a unique tactical identity should get a wired special ability. See `docs/SPECIAL_ABILITIES_EVALUATION.md` for design principles and roster planning.

**If your general has a unique ability that needs to DO something mechanically (not just display text), follow this checklist.**

#### Step 1: Define the Ability on the Marshal

**File:** `backend/models/marshal.py`

Every marshal already has an `ability` dict with 4 string fields. For an unwired ability, these are just display text. For a wired ability, the `trigger` and `effect` fields describe what happens mechanically.

```python
ability={
    "name": "Iron Resolve",
    "description": "Davout builds resolve while fortified, unleashing devastating counterattacks",
    "trigger": "while_fortified",
    "effect": "+8% attack per turn fortified (max 3 stacks, consumed on attack)"
}
```

#### Step 2: Add State Fields (if ability has state)

**File:** `backend/models/marshal.py`

If the ability tracks state (stacks, cooldowns, flags), add fields to `__init__`:

```python
# DAVOUT (Cautious) - Iron Resolve tracking
self.iron_resolve_stacks: int = 0  # Built while fortified, max 3
```

**MANDATORY:** Add to `to_dict()` AND `from_dict()` with `.get()` default:
```python
# to_dict:
"iron_resolve_stacks": self.iron_resolve_stacks,

# from_dict:
m.iron_resolve_stacks = data.get("iron_resolve_stacks", 0)
```

Run: `pytest tests/test_serialization_enforcement.py -v`

#### Step 3: Wire the Mechanical Effect

**File:** `backend/models/marshal.py` (for modifier-based abilities) or `backend/game_logic/combat.py` (for combat-time effects)

**Golden Rule #1:** Combat modifiers live in `marshal.py get_attack_modifier()` / `get_defense_modifier()` ONLY. `combat.py` reads them, never recalculates.

For attack modifier abilities (add to `get_attack_modifier()`):
```python
# Iron Resolve: +8% per stack when attacking
if (hasattr(self, 'ability')
        and self.ability.get("name") == "Iron Resolve"):
    stacks = getattr(self, 'iron_resolve_stacks', 0)
    if stacks > 0:
        modifier *= (1.0 + stacks * 0.08)
```

For combat-time abilities (shock bonus, pursuit, fort degradation), add to `combat.py resolve_battle()` following existing patterns (Ney shock at line ~175, pursuit at line ~567, fort degradation at line ~644).

#### Step 4: Add State Processing (if ability has per-turn state)

**File:** `backend/models/world_state.py` in `_process_tactical_states()`

If the ability builds stacks, expires, or changes each turn:
```python
# Iron Resolve: increment while fortified (Davout only)
if (getattr(marshal, 'ability', {}).get("name") == "Iron Resolve"
        and marshal.is_fortified and getattr(marshal, 'iron_resolve_stacks', 0) < 3):
    marshal.iron_resolve_stacks += 1
```

#### Step 5: Add State Consumption/Clearing

**File:** `backend/game_logic/combat.py` or `backend/commands/executor.py`

If stacks are consumed on use:
```python
# After get_attack_modifier() reads the value, clear stacks
if getattr(attacker, 'iron_resolve_stacks', 0) > 0:
    attacker.iron_resolve_stacks = 0
```

If state clears on movement, add to `marshal.py move_to()`:
```python
# Clear resolve on move
self.iron_resolve_stacks = 0
```

#### Step 6: Register as Wired Ability (UI)

**File:** `backend/game_logic/marshal_overview.py`

Add the marshal's name to `_WIRED_ABILITY_MARSHALS`:
```python
# NOTE: When adding a new wired ability, update this set AND follow the full
# checklist in docs/ADDING_CONTENT.md "Wiring a Special Ability" section.
_WIRED_ABILITY_MARSHALS = {"Ney", "Drouot", "Wellington", "Blucher", "Uxbridge", "Davout"}
```

This controls the `ability_active` flag sent to Godot's Marshal Management screen.

#### Step 7: Add Battle Report Observation (optional but recommended)

**File:** `backend/game_logic/battle_report.py`

Add Berthier observation templates for when the ability triggers:
```python
"iron_resolve_strike": [
    "The Iron Marshal's patience bore fruit — {marshal}'s deliberate counter-strike hit with devastating force.",
    "{marshal}'s troops, coiled like a spring after days of fortification, struck with terrible precision.",
]
```

Add selection logic in `_pick_observation()` following the existing priority tier pattern.

#### Step 8: Add Modifier Snapshot Label

**File:** `backend/game_logic/battle_report.py` in `snapshot_attacker_modifiers()` or `snapshot_defender_modifiers()`

So the player sees the ability bonus in the battle report modifier breakdown:
```python
# Iron Resolve stacks
resolve_stacks = getattr(attacker, 'iron_resolve_stacks', 0)
if resolve_stacks > 0:
    modifiers.append(("Iron Resolve", f"+{resolve_stacks * 8}%"))
```

#### Step 9: Add to game_state_summary Serialization

**File:** `backend/models/world_state.py` in `get_game_state_summary()`

If the state field needs to be visible to Godot:
```python
"iron_resolve_stacks": getattr(m, 'iron_resolve_stacks', 0),
```

#### Step 10: Write Tests

```python
class TestIronResolve:
    def test_resolve_builds_while_fortified(self):
        """Stacks increment each turn while fortified."""
        ...

    def test_resolve_caps_at_3(self):
        """Stacks don't exceed 3."""
        ...

    def test_resolve_consumed_on_attack(self):
        """Stacks reset to 0 after attacking."""
        ...

    def test_resolve_clears_on_move(self):
        """Stacks reset when marshal moves."""
        ...

    def test_resolve_boosts_attack_modifier(self):
        """Each stack adds 8% to attack modifier."""
        ...

    def test_resolve_serialization(self):
        """Stacks survive save/load roundtrip."""
        ...
```

Run full suite: `".venv\Scripts\python.exe" -m pytest tests/ -v`

#### Step 11: Update Documentation

- `CLAUDE.md` — Add ability to current phase notes
- `docs/SYSTEMS_REFERENCE.md` — Update Marshal Signature Abilities table
- `docs/SAVE_FORMAT_REFERENCE.md` — Document new serialized fields

#### Complete File Checklist (Copy-Paste)

```
WIRING A NEW SPECIAL ABILITY — MANDATORY FILES:

□ marshal.py        — Ability dict in create_*_marshals()
□ marshal.py        — State fields in __init__ (if stateful)
□ marshal.py        — to_dict() / from_dict() for state fields
□ marshal.py        — get_attack_modifier() or get_defense_modifier() (if modifier-based)
□ marshal.py        — move_to() state clearing (if state clears on move)
□ combat.py         — resolve_battle() effect (if combat-time trigger)
□ marshal_overview.py — Add name to _WIRED_ABILITY_MARSHALS set
□ world_state.py    — _process_tactical_states() (if per-turn state)
□ world_state.py    — get_game_state_summary() (if Godot needs the state)
□ executor.py       — State consumption/blocking (if applicable)
□ battle_report.py  — Modifier snapshot label (recommended)
□ battle_report.py  — Berthier observation templates (recommended)
□ tests/            — Ability tests (required)
□ CLAUDE.md         — Update phase notes
□ SYSTEMS_REFERENCE.md — Update ability table
□ SAVE_FORMAT_REFERENCE.md — Document new fields

AUTOMATICALLY HANDLED (no changes needed):
○ dispatch.py       — No ability display
○ map.gd            — No ability display in tooltips
○ marshal_management.gd — Reads whatever backend sends
○ ledger.py         — No ability display
○ campaign_log.py   — Events flow through normal channels
○ parser.py         — Already handled by marshal creation step
```

#### Common Mistakes When Wiring Abilities

| Mistake | Consequence | Prevention |
|---------|-------------|------------|
| Forgot `_WIRED_ABILITY_MARSHALS` | Marshal Management shows ability as "inactive" | Always update `marshal_overview.py` |
| Modifier in combat.py instead of marshal.py | Violates Golden Rule #1, modifier applied twice or inconsistently | All modifiers in `get_attack_modifier()` / `get_defense_modifier()` ONLY |
| Forgot to_dict/from_dict | Ability state lost on save/load | Run `test_serialization_enforcement.py` |
| State cleared before reading | Modifier returns 0 because state was already consumed | Golden Rule #4: get value, use it, THEN clear |
| Hardcoded personality check instead of ability name | All cautious/aggressive/literal marshals get the ability, not just the intended one | Check `ability.get("name")` not `personality` |
| No snapshot label in battle_report.py | Player doesn't see ability bonus in battle report | Add to `snapshot_*_modifiers()` |
| Returned float to Godot | Godot crashes | Golden Rule #2: wrap all numbers with `int()` |

---

### 1805 Roster Planning Notes

For the 1805 full Europe map, every nation needs a roster of generals. Design principles:

1. **Only great generals get unique abilities.** Most are personality-driven only (like Grouchy). Out of ~30-40 total generals, only ~10-12 should have wired abilities.
2. **Personality IS identity for most generals.** An aggressive cavalry commander already has a complete gameplay identity from personality + unit type mechanics alone.
3. **One ability per general, maximum.** Keep it simple.
4. **Abilities should create tactical decisions, not passive bonuses.** The player should have to think about when/how to use the ability.

See `docs/SPECIAL_ABILITIES_EVALUATION.md` for detailed roster estimates, ability candidates per nation, and design principles.

---

## 2. Adding a New Strategic Command Type

Step-by-step guide for adding new strategic commands (e.g., PATROL, ESCORT, FLANK).

**Difficulty:** 6/10 -- Requires touching 6+ files but the pattern is well-established.

---

### Checklist

#### Step 1: Define the Command Type

Add to the valid types set:

| File | Location | Change |
|------|----------|--------|
| `backend/ai/validation.py:117` | `VALID_STRATEGIC_TYPES` | Add `"PATROL"` to set |
| `backend/ai/strategic_parser.py:32` | `STRATEGIC_KEYWORDS` | Add keyword-to-type mapping |

#### Step 2: Parser Detection

**File:** `backend/ai/strategic_parser.py`

Add detection in `_detect_strategic_type()` (line 189):
```python
# Add keywords that trigger this command type
STRATEGIC_KEYWORDS = {
    ...
    "PATROL": ["patrol", "sweep", "patrol between", "guard route"],
}
```

If the command has a unique target classification (e.g., PATROL needs TWO regions), extend `_classify_target()` (line 264) or add a new classifier.

#### Step 3: Fast Parser Keywords

**File:** `backend/ai/llm_client.py`

Add keyword detection in `_parse_with_mock()` (~line 408):
```python
elif "patrol" in command_lower or "sweep" in command_lower:
    action = "move"  # Strategic parser will upgrade to PATROL
```

#### Step 4: Command Handler

**File:** `backend/commands/strategic.py`

Add a new handler method following the established pattern:

```python
def _execute_patrol(self, marshal, order, world, game_state):
    """PATROL: Move between waypoints in a loop."""
    # 1. Get current waypoint from order
    # 2. Move one step toward it
    # 3. On arrival, switch to next waypoint
    # 4. Check for enemies encountered en route
    # 5. Return result dict

    result = self.executor.execute(
        {"command": {
            "marshal": marshal.name,
            "action": "move",
            "target": next_waypoint,
            "_strategic_execution": True,  # REQUIRED: skips action cost
        }},
        game_state
    )
    return {
        "marshal": marshal.name,
        "command": "PATROL",
        "action_taken": "move",
        "moved_to": next_waypoint,
        "order_status": "active",  # or "completed"
    }
```

Wire it into `_execute_strategic_turn()` (line 74):
```python
elif order.command_type == "PATROL":
    return self._execute_patrol(marshal, order, world, game_state)
```

#### Step 5: Executor Initial Setup

**File:** `backend/commands/executor.py`

In `_execute_strategic_command()` (line 1984), add any command-specific setup when creating the StrategicOrder:

```python
if strategic_type == "PATROL":
    # PATROL may need multiple waypoints stored
    order = StrategicOrder(
        command_type="PATROL",
        target=waypoints[0],  # First waypoint
        target_type="region",
        path=initial_path,
        conditions=condition,
        # Store full waypoint list in a custom field if needed
    )
```

#### Step 6: Condition Support (if needed)

If the command has unique completion conditions, add them to:
- `backend/models/marshal.py` -- `StrategicCondition` dataclass (line 37)
- `backend/commands/strategic.py` -- `_check_condition()` (line 792)

#### Step 7: Serialization

If you added new fields to `StrategicOrder` or `StrategicCondition`:
- Update `to_dict()` and `from_dict()` in `backend/models/marshal.py`
- Test roundtrip: `order == StrategicOrder.from_dict(order.to_dict())`

#### Step 8: Tests

Add tests in `tests/` covering:
- Parser detects new command keywords
- Executor creates correct StrategicOrder
- Handler moves between waypoints / executes behavior
- Personality affects behavior (aggressive version vs. cautious version vs. literal version)
- Condition completion
- Serialization roundtrip

---

### Worked Example: PATROL Command

**Player says:** "Ney, patrol between Belgium and Netherlands"

#### What happens:

1. **llm_client.py** -- Fast parser sees "patrol" -> `action="move"`
2. **strategic_parser.py** -- `_detect_strategic_type()` sees "patrol" -> `PATROL`
3. **strategic_parser.py** -- `_classify_target()` needs to handle TWO region targets (new logic)
4. **parser.py** -- Injects `is_strategic=True`, `strategic_type="PATROL"`
5. **validation.py** -- `"PATROL" in VALID_STRATEGIC_TYPES` -> passes
6. **executor.py** -- Intercepts, creates StrategicOrder with waypoints, executes first move
7. **strategic.py** -- Each turn, moves to next waypoint; on arrival, reverses direction
8. **Personality:**
   - Aggressive: Auto-attacks enemies encountered on patrol route
   - Cautious: Avoids enemy regions, reports contact, asks player
   - Literal: Follows exact route, ignores nearby battles

#### Difficulty Breakdown

| Step | Effort | Notes |
|------|--------|-------|
| Keywords & validation | Easy | 2 lines each |
| Parser detection | Easy | Add to existing keyword dict |
| Target classification | Medium | PATROL needs multi-target support (new) |
| Handler | Medium | Movement loop exists, add waypoint cycling |
| Personality behavior | Medium | Reuse `_get_personality_aware_path()` and `_handle_blocked_path()` |
| Serialization | Easy | Add waypoints field to StrategicOrder |
| Tests | Medium | ~15-20 tests for full coverage |

**Total estimated difficulty: 6/10** -- Most infrastructure exists. The main new work is multi-waypoint targeting and the cycling behavior.

---

### Common Pitfalls (Strategic Commands)

1. **Always use `_strategic_execution=True`** in executor calls from handlers -- otherwise it deducts player actions
2. **Always use `_get_personality_aware_path()`** for pathfinding -- don't call `world.find_path()` directly
3. **Return `order_status`** in result dict -- `"active"`, `"completed"`, or `"paused"`
4. **Handle retreat recovery** -- check at top of handler, not just in `_execute_strategic_turn()`
5. **Test serialization** -- if you add fields to StrategicOrder, they MUST survive to_dict/from_dict roundtrip

---

## 3. Expanding the Map

Step-by-step guide for adding new regions, renaming existing regions, or expanding from the 13-region Western Europe map to a full European map.

**Difficulty:** 4/10 -- Backend region data auto-derives from `REGIONS_DATA` in `region.py` (single source of truth). Only `map.gd` (Godot) requires manual sync. Test files (~80+) still reference region names by string and need batch updates.

> **Key insight:** After rationalization, adding a region requires updating `region.py` REGIONS_DATA (with `starting_controller` + `grid_position`) and `map.gd`. Parser, strategic_parser, world_state initial control, enemy_ai capitals, and victory thresholds all auto-derive. `tests/test_map_consistency.py` catches backend/Godot drift.

---

### Region Data Questionnaire

Fill out this sheet for EACH new region before modifying any code:

```
+-------------------------------------------------------------+
| REGION DATA SHEET                                           |
+-------------------------------------------------------------+
|                                                             |
| IDENTITY                                                    |
| ----------------------------------------------------------- |
| Name: _______________________________________________       |
|   (Must be unique, Title Case, no spaces in key)           |
|                                                             |
| TERRAIN                                                     |
| ----------------------------------------------------------- |
| Terrain: [ ] plains    [ ] forest    [ ] hills              |
|          [ ] mountains [ ] urban     [ ] river_crossing     |
|                                                             |
|   (See VALID_TERRAINS in region.py for full set)           |
|   (Terrain affects: defense bonus, movement cost,          |
|    supply modifier, cavalry effectiveness, charge           |
|    blocking, bombardment modifier)                          |
|                                                             |
| ECONOMY                                                     |
| ----------------------------------------------------------- |
| Region Type: [ ] capital      (income: 300, 2 build slots) |
|              [ ] major_city   (income: 200, 1 build slot)  |
|              [ ] city         (income: 150, 1 build slot)  |
|              [ ] town         (income: 100, 0 build slots) |
|              [ ] rural        (income:  50, 0 build slots) |
|                                                             |
| Income Override: _____ (leave blank to use type default)    |
|                                                             |
| GEOGRAPHY                                                   |
| ----------------------------------------------------------- |
| Adjacent Regions: _____________________________________     |
|   (Comma-separated list. MUST be bidirectional —           |
|    if A lists B, then B must list A)                        |
|                                                             |
| Is Capital: [ ] Yes  [ ] No                                 |
|   (Capitals get 15,000 starting garrison)                  |
|                                                             |
| CONTROL                                                     |
| ----------------------------------------------------------- |
| Starting Controller: [ ] France    [ ] Britain              |
|                      [ ] Prussia   [ ] Austria              |
|                      [ ] Neutral   [ ] New Nation: ____     |
|                                                             |
| DISPLAY (Godot)                                             |
| ----------------------------------------------------------- |
| Map Position (pixels): X=_____ Y=_____                      |
|   (Relative to existing map — check map.gd REGION_POSITIONS)|
|                                                             |
| Grid Position (row, col): row=_____ col=_____               |
|   (For LLM strategic parser — check strategic_parser.py)   |
|                                                             |
+-------------------------------------------------------------+
```

---

### Complete File Reference (Regions)

Every file that contains hardcoded region names or region structure data, in dependency order.

#### Backend Files (MUST modify for any region change)

| # | File | What to Update | Notes |
|---|------|----------------|-------|
| 1 | `backend/models/region.py` | `REGIONS_DATA` dict — add/rename region entry with adjacency, income, terrain, region_type, is_capital, `starting_controller`, `grid_position`. Update `NATION_CAPITALS` if adding a new nation capital. | **Single source of truth.** parser.py, strategic_parser.py, world_state.py, and enemy_ai.py all derive from here automatically. |

#### Backend Files (Update IF applicable)

| # | File | What to Update | When |
|---|------|----------------|------|
| 2 | `backend/ai/llm_client.py` | Mock parser target keywords (~line 682) — add region name keywords for test parser | If new region names need mock parser recognition |
| 3 | `backend/ai/prompt_builder.py` | Few-shot examples reference region names (~44 references) — update examples for LLM context | If renaming regions or adding many new ones |

#### Auto-derived files (NO manual update needed)

These files now derive their region data from `region.py` automatically:

| File | What's Derived |
|------|---------------|
| `backend/commands/parser.py` | `known_regions` list — from `REGIONS_DATA.keys()` |
| `backend/ai/strategic_parser.py` | `REGION_POSITIONS` grid coordinates — from `grid_position` field |
| `backend/models/world_state.py` | `_setup_initial_control()` — from `starting_controller` field |
| `backend/ai/enemy_ai.py` | Capital lookups — from `WorldState.get_nation_capital()` → `NATION_CAPITALS` |
| `backend/game_logic/turn_manager.py` | Victory thresholds — derived from `len(world.regions)` |
| `backend/commands/executor.py` | Recruitment location — from `world.player_capital` |
| `backend/commands/disobedience.py` | Capital checks — from `world.player_capital` |

#### Frontend Files (MUST modify)

| # | File | What to Update | Notes |
|---|------|----------------|-------|
| 11 | `godot-client/.../scenes/map.gd` | `REGION_POSITIONS` dict (~line 4) — pixel coordinates for rendering | Must match backend region.py exactly |
| 12 | `godot-client/.../scenes/map.gd` | `REGION_CONNECTIONS` dict (~line 21) — adjacency for drawing edges | Must match backend region.py adjacency |

#### Test Files (Fix after backend/frontend)

| Category | Approximate Count | Nature of References |
|----------|-------------------|---------------------|
| Region name strings in test setup | 80+ files | Marshals placed at "Paris", "Belgium", etc. |
| Adjacency assertions | ~15 files | Tests that check specific neighbors |
| Region count assertions | ~10 files | `len(regions) == 13`, victory threshold checks |
| Economy/income tests | ~8 files | Tests that check specific region income values |

#### Documentation Files (Update last)

| File | What to Update |
|------|----------------|
| `CLAUDE.md` | Valid Regions table in Quick Reference |
| `docs/ADDING_CONTENT.md` | Quick Reference table at end of this section |
| `docs/SAVE_FORMAT_REFERENCE.md` | Region field documentation if new fields added |
| `docs/SYSTEMS_REFERENCE.md` | Map description, region count references |
| `docs/MANUAL_TEST_PLAN.md` | Test scenarios referencing specific regions |

---

### Step-by-Step: Adding a New Region

#### Step 1: Add to REGIONS_DATA (Source of Truth)

**File:** `backend/models/region.py` (~line 326)

```python
# Add to REGIONS_DATA dict:
"Hamburg": {
    "adjacent": ["Netherlands", "Rhine"],  # Must be bidirectional!
    "income": 150,
    "is_capital": False,
    "terrain": "plains",
    "region_type": "city",
    "starting_controller": "Prussia",       # Which nation controls at game start
    "grid_position": (0, 2),                # (row, col) for LLM direction context
},
```

**CRITICAL:** Update the adjacency lists of ALL neighboring regions too:

```python
# Netherlands BEFORE:
"Netherlands": {
    "adjacent": ["Belgium"],
    ...
}
# Netherlands AFTER:
"Netherlands": {
    "adjacent": ["Belgium", "Hamburg"],  # Added Hamburg
    ...
}
```

#### Step 2: Update Godot Map (only manual sync required)

**Steps 2-6 of the old guide are now auto-derived from REGIONS_DATA.** Parser, strategic_parser, world_state initial control, enemy_ai capitals, and victory thresholds all derive automatically.

If adding a new nation capital, update `NATION_CAPITALS` in `region.py`.

If the region name conflicts with mock parser action keywords, update `backend/ai/llm_client.py` (~line 682).

#### Step 3: Update Godot Map

**File:** `godot-client/.../scenes/map.gd`

Add to BOTH dicts:

```gdscript
# REGION_POSITIONS (~line 4):
const REGION_POSITIONS = {
    # ...existing...
    "Hamburg": Vector2(520, 130),   # Pixel position on map
}

# REGION_CONNECTIONS (~line 21):
const REGION_CONNECTIONS = {
    # ...existing...
    "Hamburg": ["Netherlands", "Rhine"],
    # Also update Netherlands and Rhine entries:
    "Netherlands": ["Belgium", "Hamburg"],
    "Rhine": ["Belgium", "Bavaria", "Lyon", "Hamburg"],
}
```

#### Step 4: Run Adjacency Validation

See [Adjacency Validation Script](#adjacency-validation-script) below. Also run `tests/test_map_consistency.py` to verify Godot matches backend.

#### Step 5: Fix Tests (Batched)

See [Test Fix Guide](#test-fix-guide) below.

#### Step 6: Update Documentation

Update the region tables in:
- `CLAUDE.md` (Valid Regions quick reference)
- This file (Quick Reference at bottom of section 3)
- `docs/SYSTEMS_REFERENCE.md` (if it references region count)

---

### Step-by-Step: Renaming a Region

Renaming is harder than adding because every string reference must change.

#### Step 1: Global Search First

Before changing anything, find ALL references:

```bash
# Find every file mentioning the old name
rg "OldName" --type py --type gdscript -l
rg "OldName" tests/ -l
rg "OldName" docs/ -l
```

#### Step 2: Update Source of Truth

**File:** `backend/models/region.py` — Change the key in `REGIONS_DATA` AND every adjacency list that references the old name.

#### Step 3: Update Backend + Godot

Update `REGIONS_DATA` in `region.py` (auto-derived files will pick it up). Update `map.gd` REGION_POSITIONS and REGION_CONNECTIONS. Check `llm_client.py` and `prompt_builder.py` for old name references.

#### Step 4: Update All Test Files

Use the batch approach in [Test Fix Guide](#test-fix-guide).

#### Step 5: Verify with Grep

```bash
# Should return ZERO results after renaming:
rg "OldName" --type py -l
rg "OldName" --type gdscript -l
```

---

### Grep Verification Commands

Run these AFTER making changes to verify nothing was missed.

```bash
# 1. List all files referencing a specific region name
rg "RegionName" --type py -l
rg "RegionName" --type gdscript -l

# 2. Find all hardcoded region name strings in backend (not comments)
rg '"(Paris|Belgium|Netherlands|Waterloo|Rhine|Bavaria|Vienna|Lyon|Milan|Marseille|Geneva|Brittany|Bordeaux)"' backend/ --type py

# 3. Find all files importing from region.py
rg "from backend.models.region import" --type py

# 4. Find adjacency references (to check bidirectionality)
rg "adjacent" backend/models/region.py

# 5. Find victory threshold references
rg "victory|regions.*>=|player_regions" backend/game_logic/turn_manager.py

# 6. Find "Paris" as capital/fallback (must update if capital changes)
rg '"Paris"' backend/ --type py -n

# 7. Count test files referencing regions (to estimate fix scope)
rg '"(Paris|Belgium|Netherlands|Waterloo|Rhine|Bavaria|Vienna|Lyon|Milan|Marseille|Geneva|Brittany|Bordeaux)"' tests/ -l | wc -l

# 8. Verify Godot map matches backend
# (manual: compare REGION_POSITIONS keys in map.gd with REGIONS_DATA keys in region.py)
```

---

### Adjacency Validation Script

Run this after any adjacency change to verify bidirectional consistency:

```python
"""Verify all region adjacencies are bidirectional."""
from backend.models.region import REGIONS_DATA

errors = []
for name, data in REGIONS_DATA.items():
    for adj in data["adjacent"]:
        if adj not in REGIONS_DATA:
            errors.append(f"  {name} lists '{adj}' but '{adj}' doesn't exist")
        elif name not in REGIONS_DATA[adj]["adjacent"]:
            errors.append(f"  {name} -> {adj} but {adj} does NOT -> {name}")

if errors:
    print("ADJACENCY ERRORS:")
    for e in errors:
        print(e)
else:
    print(f"OK: All {len(REGIONS_DATA)} regions have bidirectional adjacency.")
```

Save as `scripts/validate_adjacency.py` and run:

```bash
".venv\Scripts\python.exe" scripts/validate_adjacency.py
```

Or run inline:

```bash
".venv\Scripts\python.exe" -c "
from backend.models.region import REGIONS_DATA
errors = []
for name, data in REGIONS_DATA.items():
    for adj in data['adjacent']:
        if adj not in REGIONS_DATA:
            errors.append(f'{name} -> {adj} (missing)')
        elif name not in REGIONS_DATA[adj]['adjacent']:
            errors.append(f'{name} -> {adj} (one-way)')
print('ERRORS:' if errors else f'OK: {len(REGIONS_DATA)} regions valid')
for e in errors: print(f'  {e}')
"
```

---

### Test Fix Guide

After expanding the map, expect 20-80 test failures depending on the scope of changes. Fix them in this order (each category unlocks the next):

#### Category 1: String Renames (if renaming regions)

**Pattern:** Tests that reference old region names as string literals.

```python
# BEFORE:
marshal.location = "OldName"
# AFTER:
marshal.location = "NewName"
```

**Batch approach:**
```bash
# Find all test files with old name
rg "OldName" tests/ -l

# Preview replacements (don't auto-replace — some may be in comments or expected output)
rg "OldName" tests/ -n
```

Fix manually — automated find/replace can break test logic if the region name appears in message assertions.

#### Category 2: Adjacency Fixes

**Pattern:** Tests that assert specific neighbors or test movement between specific regions.

```python
# Test assumes Belgium is adjacent to Rhine — verify this is still true
assert world.regions["Belgium"].is_adjacent_to("Rhine")
```

Fix: Update adjacency assertions to match new map layout.

#### Category 3: Region Count Fixes

**Pattern:** Tests that assert `len(regions) == 13` or check player region counts.

```python
# BEFORE (13-region map):
assert len(world.regions) == 13
# AFTER (19-region map):
assert len(world.regions) == 19
```

**Key files:**
- `tests/test_cautious_advance_cooldown.py` — victory threshold test (10 regions)
- Any test checking `len(world.get_player_regions())`

#### Category 4: Economy Fixes

**Pattern:** Tests that assert total income, gold calculations, or economic balance based on specific region counts.

```python
# Total income changes when you add new regions
assert world.calculate_total_income("France") == expected_new_total
```

#### Category 5: Control Map Fixes

**Pattern:** Tests that set up specific world states with hardcoded controllers.

```python
# If a test sets up "all regions French" it needs to include new regions
for region in world.regions.values():
    region.controller = "France"
# This pattern is safe — it adapts automatically
```

Tests that set specific regions by name need manual updates.

---

### Victory Threshold Scaling

Current thresholds (13-region map):

| Condition | Current Value | Formula |
|-----------|--------------|---------|
| Total victory | 12 regions | `total_regions - 1` (allow 1 holdout) |
| Time victory | 10 regions | `ceil(total_regions * 0.77)` (~77% control) |
| Defeat | Lose "Paris" | Capital loss (unchanged by map size) |

**When expanding to N regions:**

```python
# In turn_manager.py _check_victory_conditions():
total = len(self.world.regions)
total_victory_threshold = total - 1           # Near-total conquest
time_victory_threshold = math.ceil(total * 0.77)  # ~77% control at time limit
```

**Examples:**

| Map Size | Total Victory | Time Victory |
|----------|---------------|--------------|
| 13 regions | 12 | 10 |
| 19 regions | 18 | 15 |
| 25 regions | 24 | 20 |
| 30 regions | 29 | 24 |

> **Note:** The current thresholds are hardcoded integers, not formulas. When expanding the map, either replace with dynamic formulas or update the hardcoded values.

---

### Common Pitfalls (Map Expansion)

#### Pitfall 1: One-Way Adjacency

**WRONG:**
```python
"Hamburg": {
    "adjacent": ["Netherlands", "Rhine"],
    ...
}
# But Netherlands still has: "adjacent": ["Belgium"]
# Hamburg can reach Netherlands, but Netherlands can't reach Hamburg!
```

**RIGHT:** Always update BOTH sides. Run the adjacency validation script.

#### Pitfall 2: Backend + Godot Duplication

Region data exists in TWO places that must stay synchronized:
1. `region.py` — `REGIONS_DATA` (source of truth — parser.py, strategic_parser.py, world_state.py, enemy_ai.py all auto-derive)
2. `map.gd` — `REGION_POSITIONS` + `REGION_CONNECTIONS` (rendering — GDScript can't import Python)

`tests/test_map_consistency.py` catches drift between them. Missing from region.py: Region doesn't exist in game. Missing from map.gd: Region exists but invisible on map.

#### Pitfall 3: Forgetting grid_position in REGIONS_DATA

Each region in `REGIONS_DATA` needs a `grid_position: (row, col)` field. `strategic_parser.py` derives `REGION_POSITIONS` from this automatically. Forgetting it causes a `KeyError` at import time. The grid uses (row=0 north, col=0 west) — it's separate from map.gd pixel positions.

#### Pitfall 4: Victory Thresholds (Auto-Scaled)

Victory thresholds in `turn_manager.py` are now derived from `len(world.regions)`: total victory = `total - 1`, time victory = `ceil(total * 0.77)`. No manual update needed.

#### Pitfall 5: Mock Parser Keyword Conflicts

The mock parser in `llm_client.py` matches region names by substring. If a new region name contains an action keyword (e.g., "Charge-ville", "Retreat-burg"), the mock parser may misparse commands. Check keyword ordering — more specific matches must come BEFORE generic ones.

#### Pitfall 6: Nation Capitals (Auto-Derived)

Capital lookups now use `NATION_CAPITALS` in `region.py` (single source of truth). If adding a new nation's capital, update `NATION_CAPITALS`. All backend files (executor, turn_manager, disobedience, enemy_ai) derive from `world.player_capital` / `world.get_nation_capital()`.

#### Pitfall 7: starting_controller in REGIONS_DATA

`_setup_initial_control()` in `world_state.py` derives controllers from the `starting_controller` field in each `REGIONS_DATA` entry. New regions MUST have this field set. Missing it causes a `KeyError` at game start.

#### Pitfall 8: Godot Connections Not Matching Backend Adjacency

`REGION_CONNECTIONS` in `map.gd` is used for drawing connection lines on the map. If it doesn't match `REGIONS_DATA` adjacency in `region.py`, the map shows incorrect connections. Always update both simultaneously.

---

### Quick Reference: Current 13-Region Map

| Region | Terrain | Type | Income | Capital | Controller | Adjacent To |
|--------|---------|------|--------|---------|------------|-------------|
| Paris | urban | capital | 300 | Yes | France | Belgium, Waterloo, Brittany, Lyon |
| Belgium | plains | town | 100 | No | France | Paris, Netherlands, Waterloo, Rhine |
| Netherlands | plains | rural | 50 | No | Britain | Belgium |
| Waterloo | hills | rural | 50 | No | Britain | Belgium, Paris |
| Rhine | river_crossing | town | 100 | No | Prussia | Belgium, Bavaria, Lyon |
| Bavaria | hills | town | 100 | No | Prussia | Rhine, Vienna, Lyon |
| Vienna | urban | major_city | 200 | No | Prussia | Bavaria, Milan |
| Lyon | hills | major_city | 200 | No | France | Paris, Rhine, Bavaria, Marseille, Milan |
| Milan | urban | city | 150 | No | Britain | Lyon, Vienna, Geneva |
| Marseille | plains | city | 150 | No | France | Lyon, Geneva |
| Geneva | mountains | town | 100 | No | Britain | Marseille, Milan, Bordeaux |
| Brittany | forest | rural | 50 | No | France | Paris, Bordeaux |
| Bordeaux | plains | rural | 50 | No | France | Brittany, Geneva |

**Update this table whenever the map changes.**
