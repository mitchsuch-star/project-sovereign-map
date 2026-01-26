# Marshal Addition Guide

**Complete guide for adding new marshals to Ink & Iron: Napoleonic Wars**

This guide covers EVERY file that must be modified when adding a marshal, with copy-paste templates and validation checklists.

---

## Table of Contents

1. [Pre-Flight Checklist](#1-pre-flight-checklist)
2. [Marshal Data Questionnaire](#2-marshal-data-questionnaire)
3. [Complete File Reference](#3-complete-file-reference)
4. [Step-by-Step Implementation](#4-step-by-step-implementation)
5. [Code Templates](#5-code-templates)
6. [Validation Checklist](#6-validation-checklist)
7. [Common Pitfalls](#7-common-pitfalls)
8. [Troubleshooting](#8-troubleshooting)
9. [Quick Reference Tables](#9-quick-reference-tables)

---

## 1. Pre-Flight Checklist

Answer these questions BEFORE writing any code:

### Basic Questions
- [ ] **Name:** What is the marshal's full name? (e.g., "Murat", "Lannes")
- [ ] **Nation:** What nation does this marshal belong to?
  - [ ] France (player)
  - [ ] Britain (enemy)
  - [ ] Prussia (enemy)
  - [ ] Austria (enemy - not yet in game)
  - [ ] Russia (enemy - not yet in game)
  - [ ] Other: ____________
- [ ] **Is this a new nation?** If yes, you'll need extra steps (see [Adding New Nations](#adding-new-nations))

### Marshal Type
- [ ] **Player or Enemy?**
  - [ ] Player marshal (French) → Add to `create_starting_marshals()`
  - [ ] Enemy marshal → Add to `create_enemy_marshals()`

### Personality Type
- [ ] **Which personality?**
  - [ ] `aggressive` - Attacks readily, objects to defensive orders
  - [ ] `cautious` - Defensive-minded, objects to risky attacks
  - [ ] `literal` - Follows orders exactly, never improvises
  - [ ] `balanced` - Mix of traits (placeholder, not fully implemented)
  - [ ] `loyal` - Extreme obedience (placeholder, not fully implemented)
  - [ ] **NEW personality type?** See [Adding New Personalities](#adding-new-personalities)

### Unit Type
- [ ] **Infantry or Cavalry?**
  - [ ] Infantry (`cavalry=False`, `movement_range=1`)
  - [ ] Cavalry (`cavalry=True`, `movement_range=2`)

### Special Abilities
- [ ] Does this marshal have unique abilities?
  - [ ] Yes → Define ability and triggers
  - [ ] No → Use default ability structure

---

## 2. Marshal Data Questionnaire

Fill out this sheet completely before implementing:

```
┌─────────────────────────────────────────────────────────────┐
│ MARSHAL DATA SHEET                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ IDENTITY                                                    │
│ ─────────────────────────────────────────────────────────── │
│ Name: _______________________________________________       │
│ Nation: _____________________________________________       │
│ Historical Title: ___________________________________       │
│   (e.g., "King of Naples", "Iron Marshal")                 │
│                                                             │
│ PERSONALITY & UNIT TYPE                                     │
│ ─────────────────────────────────────────────────────────── │
│ Personality: [ ] aggressive  [ ] cautious  [ ] literal      │
│              [ ] balanced    [ ] loyal                      │
│                                                             │
│ Unit Type:   [ ] Infantry (movement_range=1)                │
│              [ ] Cavalry  (movement_range=2, cavalry=True)  │
│                                                             │
│ STARTING STATE                                              │
│ ─────────────────────────────────────────────────────────── │
│ Starting Region: ____________________________________       │
│   (Must exist in region.py - see Quick Reference)          │
│                                                             │
│ Strength: ______________ (typical: 30,000 - 80,000)         │
│ Starting Trust: ________ (typical: 60-85, French only)     │
│                                                             │
│ Spawn Location: _________________ (capital for respawn)     │
│   (French = "Paris", Britain = "Waterloo", etc.)           │
│                                                             │
│ SKILLS (1-10 scale, 5 = average)                            │
│ ─────────────────────────────────────────────────────────── │
│ Tactical:       ____ (combat rolls, flanking bonuses)       │
│ Shock:          ____ (attack damage, pursuit effectiveness) │
│ Defense:        ____ (defender bonus, retreat casualties)   │
│ Logistics:      ____ (supply range - Phase 5)               │
│ Administration: ____ (recruitment speed, desertion)         │
│ Command:        ____ (morale, discipline)                   │
│                                                             │
│ Legacy tactical_skill: ____ (0-12, used for dice rolls)     │
│                                                             │
│ SIGNATURE ABILITY                                           │
│ ─────────────────────────────────────────────────────────── │
│ Ability Name: ________________________________________      │
│ Description: _________________________________________      │
│ Trigger: _____________________________________________      │
│   (when_attacking, morale_drops_below_50, etc.)            │
│ Effect: ______________________________________________      │
│                                                             │
│ RELATIONSHIPS (with existing marshals)                      │
│ ─────────────────────────────────────────────────────────── │
│ Format: Marshal Name → Value (-2 to +2)                     │
│   -2=Hostile, -1=Rival, 0=Professional, +1=Friendly, +2=Devoted│
│                                                             │
│ _________________ → ____                                    │
│ _________________ → ____                                    │
│ _________________ → ____                                    │
│ _________________ → ____                                    │
│                                                             │
│ REMEMBER: Relationships must be set BIDIRECTIONALLY!        │
│ If Murat likes Ney (+1), you must also set Ney's opinion    │
│ of Murat (could be different value).                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Complete File Reference

### Every File That Might Need Modification

#### Backend Files (Required)

| File | Purpose | When to Modify |
|------|---------|---------------|
| `backend/models/marshal.py` | Marshal creation | **ALWAYS** - Add marshal definition |
| `backend/commands/parser.py` | Name fuzzy matching | **ALWAYS** - Add to valid_marshals |

#### Backend Files (Conditional)

| File | Purpose | When to Modify |
|------|---------|---------------|
| `backend/models/personality_modifiers.py` | Combat bonuses | If NEW personality type |
| `backend/models/personality.py` | Objection triggers | If NEW personality type |
| `backend/commands/executor.py` | Special abilities | If unique combat mechanics |
| `backend/game_logic/combat.py` | Combat resolution | If unique combat triggers |
| `backend/ai/enemy_ai.py` | AI behavior | If enemy marshal with special AI |
| `backend/models/world_state.py` | Nation management | If NEW nation |
| `backend/ai/llm_client.py` | LLM keyword matching | If special command keywords |

#### Frontend/Godot Files (Conditional)

| File | Purpose | When to Modify |
|------|---------|---------------|
| `godot-client/.../scenes/map.gd` | Nation colors | If NEW nation |
| `godot-client/.../scripts/main.gd` | Marshal display | Rarely (auto-handles) |

#### Test Files (Required)

| File | Purpose | When to Modify |
|------|---------|---------------|
| `tests/test_marshal_abilities.py` | Ability tests | **ALWAYS** - Add ability tests |
| `tests/test_marshal_skills.py` | Skill tests | If special skill values |
| `tests/test_enemy_ai.py` | AI behavior | If enemy marshal |

#### Documentation (Required)

| File | Purpose | When to Modify |
|------|---------|---------------|
| `CLAUDE.md` | Master reference | **ALWAYS** - Update marshal list |
| `CHANGELOG.md` | Version history | **ALWAYS** - Document addition |

---

## 4. Step-by-Step Implementation

### Step 1: Add Marshal Definition

**File:** `backend/models/marshal.py`

**Location:**
- French marshals: Add to `create_starting_marshals()` (line ~717)
- Enemy marshals: Add to `create_enemy_marshals()` (line ~817)

**Action:** Add marshal to the appropriate function.

### Step 2: Update Parser Valid Marshals

**File:** `backend/commands/parser.py`

**Location:** Line ~30

```python
# Before
self.valid_marshals = ["Ney", "Davout", "Grouchy", "Murat"]

# After (add your marshal)
self.valid_marshals = ["Ney", "Davout", "Grouchy", "Murat", "NewMarshal"]
```

### Step 3: Update Known Enemies (if enemy marshal)

**File:** `backend/commands/parser.py`

**Location:** Line ~68

```python
# Before
self.known_enemies = ["Wellington", "Blucher"]

# After (add enemy marshal)
self.known_enemies = ["Wellington", "Blucher", "NewEnemy"]
```

### Step 4: Set Up Bidirectional Relationships

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

### Step 5: Add Personality Modifiers (if new personality)

**File:** `backend/models/personality_modifiers.py`

See [Adding New Personalities](#adding-new-personalities) section.

### Step 6: Add to Enemy AI (if enemy marshal)

**File:** `backend/ai/enemy_ai.py`

Enemy marshals automatically use the AI system. Verify:
- Marshal's personality threshold in `_get_attack_threshold()` (~line 500)
- Nation is in `world.enemy_nations` list

### Step 7: Update Godot Nation Colors (if new nation)

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

### Step 8: Add Tests

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

### Step 9: Run All Tests

```bash
# Run all tests
pytest tests/ -v

# Run comprehensive test
pytest test_conquest_comprehensive.py -v

# Run specific marshal tests
pytest tests/test_marshal_abilities.py -v
```

### Step 10: Manual Testing

Start the game and verify:
- [ ] Marshal appears on map in correct location
- [ ] Marshal shows correct nation color
- [ ] Hovering shows correct stats in tooltip
- [ ] Marshal responds to commands (if player)
- [ ] Enemy AI controls marshal correctly (if enemy)
- [ ] No console errors or warnings

### Step 11: Update Documentation

**File:** `CLAUDE.md`

Update the marshal list in the quick reference section.

**File:** `CHANGELOG.md`

Add entry for the new marshal.

---

## 5. Code Templates

### Template A: French Player Marshal

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

### Template B: Enemy Marshal

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

### Template C: Relationship Setup

Add after all marshals are created in the function:

```python
# ════════════════════════════════════════════════════════════
# SCENARIO NAME: Historical Relationships
# ════════════════════════════════════════════════════════════

# NewMarshal's relationships
marshals["NewMarshal"].set_relationship("Ney", 1)      # Friendly
marshals["NewMarshal"].set_relationship("Davout", 0)   # Professional
marshals["NewMarshal"].set_relationship("Grouchy", -1) # Rival

# Reciprocal relationships (REQUIRED!)
marshals["Ney"].set_relationship("NewMarshal", 1)      # Mutual friendship
marshals["Davout"].set_relationship("NewMarshal", 0)   # Mutual professionalism
marshals["Grouchy"].set_relationship("NewMarshal", -1) # Mutual rivalry
```

### Template D: Test Class

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

## 6. Validation Checklist

Before committing, verify ALL items:

### Marshal Definition
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

### Relationships
- [ ] All relationships are set BIDIRECTIONALLY
- [ ] Relationship values are in range -2 to +2
- [ ] Historical accuracy (if applicable)

### Parser
- [ ] Marshal name added to `valid_marshals` list
- [ ] If enemy: name added to `known_enemies` list
- [ ] Name doesn't conflict with existing names (case-insensitive)
- [ ] Fuzzy matching works (test with typos)

### Tests
- [ ] Test class created for new marshal
- [ ] Tests verify ability definition
- [ ] Tests verify starting stats
- [ ] Tests verify bidirectional relationships
- [ ] All tests pass: `pytest tests/ -v`

### Frontend (if new nation)
- [ ] Nation color added to `map.gd` COLORS constant
- [ ] Color is visually distinct from existing nations

### Documentation
- [ ] CLAUDE.md updated with new marshal
- [ ] CHANGELOG.md has entry for addition

### Manual Testing
- [ ] Game starts without errors
- [ ] Marshal appears on map
- [ ] Tooltip shows correct info
- [ ] Commands work (if player marshal)
- [ ] AI controls correctly (if enemy marshal)

---

## 7. Common Pitfalls

### Pitfall 1: One-Sided Relationships

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

### Pitfall 2: Wrong Movement Range for Cavalry

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

### Pitfall 3: Nonexistent Starting Region

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

### Pitfall 4: Skills Outside Valid Range

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

### Pitfall 5: Forgetting to Update Parser

Marshal is added but commands don't work:

```python
# parser.py - MUST ADD TO THIS LIST:
self.valid_marshals = ["Ney", "Davout", "Grouchy", "NewMarshal"]  # Added!

# For enemies:
self.known_enemies = ["Wellington", "Blucher", "NewEnemy"]  # Added!
```

### Pitfall 6: Missing Nation Color in Godot

New nation's marshals appear as magenta on map (debug color).

Check `godot-client/.../scenes/map.gd`:
```gdscript
const COLORS = {
    # ...existing colors...
    "NewNation": Color(R, G, B),  # Must add this!
}
```

### Pitfall 7: Not Adding Tests

Marshal seems to work but breaks in edge cases. Always add:
- Ability definition test
- Starting stats test
- Relationship bidirectionality test

### Pitfall 8: Cavalry Without cavalry=True

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

## 8. Troubleshooting

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

## 9. Quick Reference Tables

### Valid Regions (Current 13-Region Map)

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

### Personality Types

| Personality | Attack Behavior | Defense Behavior | Use For |
|-------------|-----------------|------------------|---------|
| `aggressive` | +15% base attack | -5% in aggressive stance | Cavalry leaders, glory-seekers |
| `cautious` | -5% in aggressive stance | +5% in defensive stance | Defensive generals, staff officers |
| `literal` | Normal | +15% when holding | By-the-book officers (Grouchy) |
| `balanced` | Normal | Normal | Well-rounded generals |
| `loyal` | Normal | Normal | Absolutely obedient (placeholder) |

### Skill Value Guidelines

| Value | Description | Example |
|-------|-------------|---------|
| 1-3 | Poor | Weak in this area |
| 4-5 | Average | Competent soldier |
| 6-7 | Good | Reliable professional |
| 8-9 | Excellent | Elite performer |
| 10 | Legendary | Best in Europe |

### Typical Strength Values

| Force Type | Strength Range | Examples |
|------------|----------------|----------|
| Small corps | 15,000 - 25,000 | Light cavalry, reconnaissance |
| Medium corps | 30,000 - 50,000 | Standard army corps |
| Large corps | 50,000 - 80,000 | Main field army |
| Grande Armée | 100,000+ | Combined force |

### Relationship Values

| Value | Label | Meaning |
|-------|-------|---------|
| -2 | Hostile | Active animosity, will undermine |
| -1 | Rival | Professional tension, competitive |
| 0 | Professional | Neutral working relationship |
| +1 | Friendly | Positive regard, cooperative |
| +2 | Devoted | Deep loyalty, will sacrifice for |

### Historical French Marshals (For Future Addition)

| Marshal | Suggested Personality | Notes |
|---------|----------------------|-------|
| Murat | aggressive | Cavalry genius, King of Naples |
| Lannes | loyal | "Roland of the Army" |
| Soult | balanced | "Hand of Iron" |
| Masséna | cautious | Defensive expert |
| Bernadotte | cautious | Future Swedish king |
| Bessières | loyal | Imperial Guard commander |
| Mortier | balanced | Artillery expert |
| Oudinot | aggressive | "Bayard of the Army" |
| Marmont | cautious | Artillery, later traitor |
| Poniatowski | aggressive | Polish prince |

### Historical Enemy Commanders (For Future Addition)

| Commander | Nation | Suggested Personality |
|-----------|--------|----------------------|
| Schwarzenberg | Austria | cautious |
| Archduke Charles | Austria | cautious |
| Kutuzov | Russia | cautious |
| Bagration | Russia | aggressive |
| Moore | Britain | balanced |

---

## Adding New Nations

If adding a marshal for a nation not yet in the game:

### 1. Add Nation Color (Godot)

```gdscript
# map.gd line ~38
const COLORS = {
    # ...existing...
    "NewNation": Color(R, G, B),
}
```

### 2. Add to Enemy Nations List

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

### 3. Set Up Initial Region Control

```python
# world_state.py in _setup_initial_control()
control_map = {
    # ...existing...
    "RegionName": "NewNation",
}
```

---

## Adding New Personalities

If creating a new personality type:

### 1. Add Modifiers

```python
# personality_modifiers.py

NEW_PERSONALITY_MODIFIERS = {
    "base_attack_bonus": 0.0,
    "base_defense_bonus": 0.0,
    # ... other modifiers
}
```

### 2. Update Modifier Functions

```python
# personality_modifiers.py in get_personality_modifiers()
modifiers = {
    "aggressive": NEY_MODIFIERS,
    "cautious": DAVOUT_MODIFIERS,
    "literal": GROUCHY_MODIFIERS,
    "new_personality": NEW_PERSONALITY_MODIFIERS,  # Add this
}
```

### 3. Add Objection Triggers

```python
# personality.py in PERSONALITY_TRIGGERS
Personality.NEW_TYPE: {
    'attack_weakness': 0.40,
    'defend_strong': 0.50,
    # ... objection trigger rates
}
```

---

## Example: Adding Marshal Murat

Complete walkthrough of adding a new French cavalry marshal:

### Step 1: Fill Out Data Sheet

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

### Step 2: Add to marshal.py

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

### Step 3: Add Relationships

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

### Step 4: Update Parser

```python
# parser.py line ~30
self.valid_marshals = ["Ney", "Davout", "Grouchy", "Murat"]
```

### Step 5: Add Tests

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

### Step 6: Run Tests

```bash
pytest tests/test_marshal_abilities.py -v
pytest tests/ -v
```

### Step 7: Manual Test

1. Start backend: `python backend/main.py`
2. Open Godot client
3. Verify Murat appears at Lyon
4. Hover to check tooltip stats
5. Send command: "Murat, attack Bavaria"
6. Verify 2-tile attack range works

### Step 8: Update Documentation

Add to CLAUDE.md and CHANGELOG.md.

---

## Summary

Adding a marshal requires modifying **at minimum**:
1. `backend/models/marshal.py` - Marshal definition
2. `backend/commands/parser.py` - Valid marshals list
3. `tests/test_marshal_abilities.py` - Tests
4. `CLAUDE.md` and `CHANGELOG.md` - Documentation

Time estimate: **20-30 minutes** for a standard marshal with no new mechanics.

If adding new nation or personality: Add **30-60 minutes** for additional files.

---

*Last updated: January 2026*
*Compatible with: Phase 2.5 (Autonomy Foundation)*
