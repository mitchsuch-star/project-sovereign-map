# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Project Sovereign is a strategic turn-based military conquest game set in Napoleonic Western Europe. Players control France and manage marshals (Ney, Davout, Grouchy) to conquer 13 regions while managing an action economy system. Features natural language command parsing via Claude API (with mock fallback) and a Godot 4 frontend with FastAPI backend.

**Core Innovation:** Players don't click armies—they type commands like "Marshal Ney, attack Wellington" and AI marshals respond, question, or even disobey based on their personality.

## Commands

### Running the Backend
```bash
python backend/main.py
# FastAPI runs on http://127.0.0.1:8005 (NOT 8000!)
```

### Running Tests
```bash
pytest test_conquest_comprehensive.py -v
```

### Testing Individual Modules
```bash
python backend/models/world_state.py
python backend/game_logic/combat.py
python backend/commands/parser.py
```

### Running the Frontend
Open `godot-client/project-sovereign/` in Godot 4 editor.

## Architecture

### Command Processing Pipeline
```
User Input → LLMClient → CommandParser → CommandExecutor → WorldState
```

1. **LLMClient** (`backend/ai/llm_client.py`): Parses natural language using mock keyword matching (default) or Claude API
2. **CommandParser** (`backend/commands/parser.py`): Converts NL to structured commands, validates marshals and actions
3. **CommandExecutor** (`backend/commands/executor.py`): Routes commands to action handlers, manages action economy
4. **WorldState** (`backend/models/world_state.py`): Central game state container

### Core Models (`backend/models/`)
- **WorldState**: Game state container, action economy, income calculation, BFS pathfinding
- **Region**: Territory model with 13 hardcoded regions, adjacency, income values
- **Marshal**: Commander with army strength, personality traits (aggressive/cautious/literal), morale

### Game Logic (`backend/game_logic/`)
- **CombatResolver** (`combat.py`): Deterministic battle system with morale multipliers, terrain modifiers, defender bonus (+20%)
- **TurnManager** (`turn_manager.py`): Turn progression, victory conditions (≥8 regions by turn 40 or all 13)

### API Endpoints
- `GET /test` - Connection test
- `POST /command` - Execute player commands
- `GET /status` - Current game state
- `GET /docs` - Interactive API docs

---

## Critical Code Patterns

### Type Safety (CRITICAL!)
All numeric returns MUST be wrapped with `int()` - Godot expects int, not float:
```python
# CORRECT:
return {"turn": int(self.current_turn), "gold": int(self.gold)}

# WRONG - will cause Godot errors:
return {"turn": self.current_turn}
```

### Marshal Storage (Unified)
All marshals (player + enemy) in single dict. Do NOT create separate dicts:
```python
# CORRECT:
world.marshals  # Contains Ney, Davout, Grouchy, Wellington, Blucher

# WRONG - causes persistence bugs:
self.player_marshals = {}
self.enemy_marshals = {}
```

### Early Returns Pattern
```python
# CORRECT:
if not world:
    return {"success": False, "message": "No world state"}
if not marshal:
    return {"success": False, "message": "Marshal not found"}
# ... main logic

# WRONG - deep nesting:
if world:
    if marshal:
        if enemy:
            # ... deeply nested
```

---

## Action Economy

### Current Implementation (MVP)
- 4 actions per turn
- Auto-advance when actions exhausted
- Free actions: `status`, `help`, `end_turn`
- Paid actions: `attack`, `move`, `scout`, `recruit`, `defend` (cost 1 each)

### Future Expansion (Early Access) - CONCEPTUAL/TBD

```python
# Variable action costs
ACTION_COSTS = {
    "attack": 2,           # Major commitment
    "probe_attack": 1,     # Light engagement  
    "move": 1,
    "forced_march": 2,     # Move 2 regions, take casualties
    "scout": 1,
    "deep_reconnaissance": 2,
    "recruit": 1,
    "mass_conscription": 3,    # Double troops, morale penalty
    "defend": 1,
    "fortify": 2,
    "diplomatic_mission": 1,
    "negotiate_treaty": 2,
}
```

### Nation-Specific Action Counts (CONCEPTUAL)
Different nations have different administrative capacity:
```python
BASE_NATION_ACTIONS = {
    "France": 5,      # Corps system, centralized command
    "Prussia": 4,     # Efficient but smaller
    "Britain": 4,     # Parliamentary delays but competent
    "Austria": 3,     # Bureaucratic, multi-ethnic complexity
    "Russia": 3,      # Vast but slow
    "Spain": 2,       # Guerrilla focus, weak central command
    "Ottoman": 2,     # Declining administration
}
```

### Action Modifiers (CONCEPTUAL)
Actions can be gained or lost based on game state:

**Gaining Actions:**
```python
ACTION_BONUSES = {
    "tech_administration": +1,      # Administrative reforms
    "tech_military_theory": +1,     # Staff college system
    "leader_trait_organizer": +1,   # Napoleon's personal skill
    "stable_government": +1,        # No revolts, high legitimacy
}
```

**Losing Actions:**
```python
ACTION_PENALTIES = {
    "overextension": -1,           # Controlling too many non-core regions
    "instability": -1,             # Low stability score
    "war_exhaustion": -1,          # Long wars drain administration
    "revolt_ongoing": -1,          # Must divert attention to rebels
    "regency_council": -2,         # No strong leader
    "coalition_against": -1,       # Diplomatic pressure
}

# Example: France at peak vs struggling
# Peak Napoleon: 5 base + 2 bonuses = 7 actions/turn
# 1813 Napoleon: 5 base - 3 penalties = 2 actions/turn
```

### Overextension System (CONCEPTUAL)
```python
def calculate_overextension(nation):
    """
    Overextension = (non-core regions) / (core regions) * 100
    
    Effects at thresholds:
    - 0-25%:   No penalty
    - 25-50%:  -1 action, +10% revolt risk
    - 50-100%: -2 actions, +25% revolt risk, -20% income
    - 100%+:   -3 actions, +50% revolt risk, -50% income
    
    Reduced by:
    - Time (regions become cores after ~10 turns)
    - Cultural acceptance events
    - Puppet states (don't count as direct control)
    """
    pass
```

### Stability System (CONCEPTUAL)
```python
STABILITY_LEVELS = {
    3: {"name": "Triumphant", "action_bonus": +1, "revolt_risk": -50%},
    2: {"name": "Stable", "action_bonus": 0, "revolt_risk": -25%},
    1: {"name": "Uncertain", "action_bonus": 0, "revolt_risk": 0},
    0: {"name": "Unstable", "action_bonus": -1, "revolt_risk": +25%},
    -1: {"name": "Chaotic", "action_bonus": -1, "revolt_risk": +50%},
    -2: {"name": "Collapsing", "action_bonus": -2, "revolt_risk": +100%},
    -3: {"name": "Civil War", "action_bonus": -3, "revolt_risk": "automatic"},
}

# Stability changes from:
# + Major battle victories
# + Successful treaties
# + Leader events
# - Defeats
# - Breaking treaties
# - Overextension
# - War exhaustion
# - Leader death
```

---

## Building Blocks Philosophy

The game uses a "building blocks" approach where all actions (player AND AI) go through the same executor. This is intentional:

### Existing Blocks (Complete)
| Block | Location | Notes |
|-------|----------|-------|
| attack | executor.py | With region conquest |
| defend | executor.py | +30% bonus next battle |
| move | executor.py | Adjacency validated |
| scout | executor.py | Range-limited intel |
| recruit | executor.py | 200 gold → 10,000 troops |
| reinforce | executor.py | Move to ally marshal |

### Planned Blocks (Future)
| Block | Priority | Notes |
|-------|----------|-------|
| propose_peace | High | Win condition beyond conquest |
| declare_war | High | Coalition dynamics |
| propose_alliance | High | Alliance tracking |
| siege | Medium | Fortified regions take time |
| forced_march | Medium | Move 2, morale penalty |
| blockade | Medium | Reduce enemy income (naval abstraction) |
| emergency_taxation | Low | Gold now, morale cost |
| intercept_messages | Low | Intelligence gathering |

### Adding New Blocks
1. Add handler method in `executor.py`: `_execute_[action_name]()`
2. Add action to `parser.py` valid_actions list
3. Add cost to `world_state.py` `_action_costs` dict
4. Update mock parser keywords in `llm_client.py`

---

## Input Handling Architecture

**CRITICAL: Every user input MUST receive a response.** No input should ever be ignored or cause a crash.

### Input Classification System

```
User Input → Input Router → Classifier → Appropriate Handler → Response
```

### Input Categories

| Category | Examples | Handler | Action Cost |
|----------|----------|---------|-------------|
| **COMMAND** | "Ney, attack Wellington" | executor.execute() | Varies |
| **QUERY** | "Where is Davout?", "How much gold?" | query_handler | 0 (free) |
| **ADVICE** | "What should I do?", "Recommend strategy" | advisor_handler | 0 (free) |
| **LORE** | "Tell me about Wellington", "What happened at Austerlitz?" | lore_handler | 0 (free) |
| **ROLEPLAY** | "Ney, how are you feeling?" | roleplay_handler | 0 (free) |
| **META** | "help", "save", "settings", "quit" | meta_handler | 0 (free) |
| **CLARIFICATION** | "attack" (attack what?), "move him" (who?) | clarification_handler | 0 (free) |
| **INVALID** | "asdfghjkl", gibberish | invalid_handler | 0 (free) |
| **INAPPROPRIATE** | Off-topic, out of scope | redirect_handler | 0 (free) |

### Implementation: InputRouter Class

```python
# backend/commands/input_router.py

class InputRouter:
    """Routes ALL user input to appropriate handler. Never crashes."""
    
    def route(self, user_input: str, game_state: dict) -> dict:
        """Main entry point. ALWAYS returns a response."""
        text = user_input.strip().lower()
        
        # 1. META commands (help, save, quit)
        if self._is_meta(text):
            return self._handle_meta(text)
        
        # 2. QUERY patterns (where, how much, what is)
        if self._is_query(text):
            return self._handle_query(text, game_state)
        
        # 3. ADVICE requests (what should I, recommend)
        if self._is_advice(text):
            return self._handle_advice(game_state)
        
        # 4. Try to parse as COMMAND
        parsed = self.parser.parse(user_input)
        if parsed.get("success"):
            return self.executor.execute(parsed, game_state)
        
        # 5. CLARIFICATION needed (ambiguous input)
        if self._needs_clarification(text, parsed):
            return self._handle_clarification(text, game_state)
        
        # 6. LORE/ROLEPLAY (requires LLM, mock for MVP)
        if self._is_lore_or_roleplay(text):
            return self._handle_lore_roleplay(text, game_state)
        
        # 7. Default: INVALID (graceful response)
        return self._handle_invalid(text)
```

### Detection Patterns

```python
# Query detection
QUERY_STARTERS = ["where is", "how much", "how many", "what is", 
                  "what are", "who is", "what turn", "what regions",
                  "show me", "list", "status"]

# Advice detection  
ADVICE_PATTERNS = ["what should", "should i", "recommend", "suggest",
                   "best strategy", "what now", "advise", "help me decide"]

# Meta commands
META_COMMANDS = ["help", "save", "load", "quit", "settings", 
                 "commands", "tutorial", "?"]

# Needs clarification (single word commands without target)
AMBIGUOUS_COMMANDS = ["attack", "move", "reinforce", "scout"]
```

### Response Examples

```python
# QUERY: "Where is Ney?"
{"type": "query", "message": "Ney is at Belgium with 72,000 troops."}

# ADVICE: "What should I do?"  
{"type": "advice", "message": "Strategic Assessment:\n• You have numerical superiority. Consider attacking.\n• Treasury is healthy. You could recruit more troops."}

# CLARIFICATION: "attack"
{"type": "clarification", "message": "Attack whom, Sire? Available targets: Wellington at Waterloo, Blucher at Netherlands."}

# INVALID: "asdfghjkl"
{"type": "invalid", "message": "I don't understand that command, Sire. Try 'help' for examples, or give orders like 'Ney, attack Wellington'."}

# INAPPROPRIATE: "Write me a poem"
{"type": "redirect", "message": "Sire, we are at war! Perhaps focus on the campaign?"}
```

### MVP vs LLM-Enhanced Responses

| Category | MVP Response | LLM-Enhanced (EA) |
|----------|-------------|-------------------|
| QUERY | Direct factual answer | Same |
| ADVICE | Rule-based suggestions | LLM strategic analysis |
| LORE | "Coming in Early Access" | LLM historical context |
| ROLEPLAY | "Personality responses coming soon" | LLM in-character dialogue |
| CLARIFICATION | List options | LLM interprets context |

---

## LLM Integration Architecture

### Current State
- Mock LLM (keyword matching) for MVP
- Real LLM deferred to Phase 2

### Architecture Layers (Future)
```
Layer 1: Command Parser (Haiku - cheap, fast)
    ↓
Layer 2: Marshal Response Generator (Sonnet - personality)
    ↓
Layer 3: Executor (NO LLM - deterministic rules)
    ↓
Layer 4: Outcome Narrator (Sonnet - flavor text)
    ↓
Layer 5: AI Nation Decision Maker (Sonnet - strategy)
    ↓
Layer 6: Turn Summary Generator (Sonnet - narrative)
```

### Key Insight
**Executor stays rule-based.** LLM adds flavor and decisions, but game mechanics are deterministic. AI nations use SAME executor as player.

### Nation Tiers for LLM
```python
NATION_TIERS = {
    "great_power": {
        "llm_model": "claude-sonnet-4-20250514",
        "actions_per_turn": 4,
        "full_personality": True,
        "examples": ["France", "Britain", "Prussia", "Austria", "Russia"]
    },
    "secondary_power": {
        "llm_model": "claude-haiku-4-20250514",
        "actions_per_turn": 2,
        "examples": ["Spain", "Bavaria", "Netherlands"]
    },
    "minor_power": {
        "llm_model": None,  # Rule-based only
        "actions_per_turn": 1,
        "examples": ["Saxony", "Naples", "Denmark"]
    }
}
```

---

## Diplomacy System (Future)

### Design Philosophy
- Natural language negotiation with AI leaders
- Each nation has persistent conversation thread
- LLM remembers broken promises, past deals
- Treaties are game-mechanical (not just flavor)

### Planned State per Nation
```python
diplomatic_state = {
    "conversation_history": [],
    "relationship_level": int,     # -100 to +100
    "active_proposals": [],
    "broken_promises": [],
    "trust_score": int,
    "war_weariness": int,          # Long wars make peace attractive
}
```

### Diplomatic Actions
```python
DIPLOMATIC_BLOCKS = {
    "propose_peace": {"action_cost": 1, "params": ["nation", "terms"]},
    "propose_alliance": {"action_cost": 1, "requires": "relationship >= 0"},
    "declare_war": {"action_cost": 0},  # War is free!
    "send_envoy": {"action_cost": 1, "params": ["nation", "message"]},
    "break_treaty": {"action_cost": 0, "reputation_cost": -20},
}
```

---

## Naval Power Abstraction

### Design Decision
**No ship-to-ship combat.** Britain's naval supremacy is abstracted as economic/strategic effects.

### How It Works
```python
# Britain has "naval_power" attribute
# This enables certain actions and effects:

NAVAL_EFFECTS = {
    "blockade": {
        "requires": "naval_power",
        "effect": "Target nation income -30%",
        "action_cost": 2
    },
    "expeditionary_support": {
        "requires": "naval_power", 
        "effect": "Can reinforce any coastal region",
    },
    "trade_dominance": {
        "passive": True,
        "effect": "+100 gold/turn from trade"
    }
}

# France can counter with:
# - Continental System (reduce Britain trade income)
# - Coastal fortifications (block expeditions)
# - Alliance with naval powers (unlikely but possible)
```

### Why This Design
- Naval combat is complex to simulate
- Napoleonic Wars were decided on land
- Britain's power was economic/strategic, not tactical
- Keeps focus on land command gameplay

---

## Colonial Power Abstraction

### Design Decision
**Colonies are abstracted as a "Colonial Power" score**, not individually simulated. This explains Britain's wealth without simulating the entire colonial system.

### Colonial Power Mechanics (CONCEPTUAL)

```python
# Colonial Power is a nation attribute (0-100 scale)
COLONIAL_POWER = {
    "Britain": 100,      # Dominant colonial empire
    "France": 40,        # Caribbean, some Africa/India (pre-Napoleon losses)
    "Spain": 60,         # Americas (declining)
    "Portugal": 35,      # Brazil, Africa
    "Netherlands": 30,   # East Indies
    "Austria": 0,        # Landlocked, no colonies
    "Prussia": 0,        # No significant colonies
    "Russia": 5,         # Alaska, mostly land expansion
}

# Effects of Colonial Power:
def calculate_colonial_income(nation, colonial_power):
    """
    Colonial Power directly affects income.
    Britain's wealth comes from colonies, not European land.
    """
    base_colonial_income = colonial_power * 5  # Up to +500 gold/turn for Britain
    return base_colonial_income
```

### What Reduces Colonial Power

```python
COLONIAL_POWER_PENALTIES = {
    "european_instability": -10,    # Per stability level below 0
    "war_exhaustion_high": -15,     # Over 50% war exhaustion
    "blockaded_by_enemy": -20,      # If France blockades Britain (rare)
    "lost_naval_battle": -10,       # If fleet destroyed (event-based)
    "colonial_revolt": -25,         # Random event, more likely when unstable
    "overextension": -5,            # Per 25% overextension
}

# Example: Britain at war for 10 years
# Colonial Power: 100 - 15 (war exhaustion) - 10 (instability) = 75
# Income: 75 * 5 = +375 gold/turn (down from +500)
```

### What Increases Colonial Power

```python
COLONIAL_POWER_BONUSES = {
    "naval_victory": +5,            # Defeating enemy fleet
    "trade_treaty": +10,            # Commercial agreement
    "colonial_conquest": +15,       # Taking enemy colonies (event)
    "stability_high": +5,           # Per stability level above 0
    "continental_system_broken": +10,  # If France's system fails
}
```

### Strategic Implications

```python
# Why this matters for gameplay:

# 1. Britain can fund coalitions indefinitely... unless weakened
#    Napoleon's best strategy: Continental System + exhaust Britain economically

# 2. France capturing colonies is abstracted
#    "Colonial expedition" action: 
#    - Costs 2 actions, 500 gold
#    - Success chance based on naval power difference
#    - Reduces target colonial power by 10-20

# 3. AI behavior driven by colonial power
#    - Low colonial power = more willing to negotiate
#    - High colonial power = can afford long wars

# 4. Victory condition modifier
#    - Controlling all Europe means nothing if Britain funds resistance
#    - Must either: conquer Britain OR reduce their colonial power below 30
```

### Integration with Other Systems

```python
# Colonial Power affects:
colonial_effects = {
    "income": "colonial_power * 5 gold/turn",
    "war_capacity": "High = can fund longer wars",
    "coalition_strength": "Britain funds allies based on colonial power",
    "peace_willingness": "Low colonial power = more willing to negotiate",
    "stability": "Colonial revolts can destabilize home nation",
}

# Player (France) goals regarding colonial power:
# - Continental System reduces British trade (colonial power -2/turn while active)
# - Naval raids (expensive, risky, but can reduce colonial power)
# - Force Britain to overextend in Europe (drains colonial focus)
# - Wait them out (war exhaustion eventually hurts colonial power)
```

---

## Early Access Expansion Plans

### Timeline Change (EA 1.0)
- Current: 40 turns (100 days)
- EA: Year-based (1805-1815), monthly turns
- Each year = 12 turns
- Full campaign = ~120 turns

### Character Death System
```python
# Marshals can die from:
DEATH_CAUSES = {
    "battle": 0.05,      # 5% chance per major defeat
    "illness": 0.02,     # 2% per year, increases with age
    "old_age": 0.10,     # 10% per year over 60
    "assassination": 0.01,  # Rare, plot-driven
}

# When marshal dies:
# 1. LLM generates death narrative
# 2. LLM generates replacement marshal with new personality
# 3. Replacement has lower initial trust/effectiveness
```

### Vassal System
```python
# Conquered nations become vassals with autonomy levels:
AUTONOMY_LEVELS = {
    "puppet": 0,      # Full control, 1 action/turn
    "satellite": 25,  # Some autonomy, may refuse orders
    "ally": 50,       # Equal partner, negotiated actions
    "independent": 100,  # No control
}

# Vassal loyalty affected by:
# - War weariness
# - French defeats
# - Distance from Paris
# - Local nationalism
```

---

## Missing Design Elements (EA Priority)

### CRITICAL: Must Have for Early Access

#### 1. Supply & Logistics System
```python
# Napoleon lost 400,000 men to attrition in Russia, not combat
# Armies NEED supply lines to function

SUPPLY_SYSTEM = {
    "supply_range": 3,  # Regions from friendly territory
    "effects_when_unsupplied": {
        "attrition": "5% strength loss per turn",
        "morale_loss": "-10 per turn",
        "combat_penalty": "-30% effectiveness",
        "forced_retreat": "After 3 turns unsupplied",
    },
    
    # Supply sources:
    "supply_sources": [
        "Friendly controlled regions",
        "Depot buildings (can be built)",
        "Foraging (hostile territory, damages relations)",
    ],
    
    # Strategic implications:
    # - Can't just march to Moscow without supply chain
    # - Cutting enemy supply = winning without fighting
    # - Depots are high-value targets
}
```

#### 2. Manpower Pool System
```python
# France had ~30M people, not infinite soldiers
# Recruitment depletes national manpower

MANPOWER_SYSTEM = {
    "national_pools": {
        "France": 300_000,      # Available for recruitment
        "Prussia": 150_000,
        "Austria": 250_000,
        "Russia": 500_000,      # Vast but slow to mobilize
        "Britain": 100_000,     # Small but professional
    },
    
    "recovery_rate": "2% of max per turn (peacetime)",
    "wartime_recovery": "0.5% per turn",
    
    "recruitment_cost": {
        "gold": 200,
        "manpower": 10_000,     # Deducted from pool
    },
    
    # When manpower exhausted:
    # - Cannot recruit normally
    # - Emergency conscription: -stability, -morale
    # - Scraping the barrel: Low quality troops
}
```

#### 3. Coalition Trigger System
```python
# Why did everyone gang up on Napoleon?
# Coalitions form based on threat + diplomacy

COALITION_TRIGGERS = {
    "threat_level": {
        "calculation": "regions_controlled + recent_conquests + army_size",
        "thresholds": {
            50: "Minor powers nervous",
            75: "Great powers consider coalition",
            100: "Coalition likely forms",
            125: "Coalition certain",
        },
    },
    
    "trigger_events": [
        "Player conquers 3+ regions in one year",
        "Player breaks major treaty",
        "Player defeats great power decisively",
        "Player crowns themselves Emperor",
    ],
    
    "coalition_formation": {
        "lead_time": "2-4 turns warning",
        "can_prevent": "Diplomacy, releasing conquests, tribute",
        "members": "Based on who feels threatened",
    },
}
```

#### 4. Fog of War System
```python
# What does the player actually KNOW vs guess?

FOG_OF_WAR = {
    "visibility_levels": {
        "full": "Own regions, adjacent to own armies",
        "partial": "Scouted regions (decays over time)",
        "rumor": "2+ regions away, vague info",
        "unknown": "No information",
    },
    
    "information_types": {
        "full": ["Army location", "Army size", "Commander", "Morale"],
        "partial": ["Army location", "Approximate size (±20%)"],
        "rumor": ["Army reported in area", "Size unknown"],
        "unknown": ["???"],
    },
    
    "intel_gathering": [
        "Scout action (1 action, reveals 1 region fully)",
        "Spy network (passive, slow intel on enemy)",
        "Captured dispatches (random event)",
        "Allied reports (shared intel)",
    ],
}
```

#### 5. Terrain System
```python
# Mountains, rivers, fortresses matter enormously

TERRAIN_TYPES = {
    "plains": {
        "movement_cost": 1,
        "defender_bonus": 0,
        "attrition": 0,
    },
    "hills": {
        "movement_cost": 1.5,
        "defender_bonus": +20,
        "attrition": 0,
    },
    "mountains": {
        "movement_cost": 2,
        "defender_bonus": +40,
        "attrition": 2,  # % per turn
    },
    "forest": {
        "movement_cost": 1.5,
        "defender_bonus": +15,
        "cavalry_penalty": -30,
    },
    "marsh": {
        "movement_cost": 2,
        "defender_bonus": +10,
        "attrition": 3,
    },
    "river_crossing": {
        "attacker_penalty": -25,
        "requires": "Bridge or ford",
    },
    "fortress": {
        "defender_bonus": +50,
        "requires_siege": True,
        "siege_duration": "3-6 turns",
    },
}
```

#### 6. Attrition System
```python
# Armies lose men just by existing, especially in bad conditions

ATTRITION_FACTORS = {
    "base_attrition": 0.5,  # % per turn just existing
    
    "modifiers": {
        "winter": +3.0,           # % additional
        "hostile_territory": +1.0,
        "unsupplied": +5.0,
        "forced_march": +2.0,
        "mountain_terrain": +2.0,
        "disease_outbreak": +5.0,  # Event
        "over_supply_limit": +2.0, # Too many troops in region
    },
    
    "mitigation": {
        "high_morale": -0.5,
        "experienced_troops": -0.5,
        "supply_depot": -1.0,
        "winter_quarters": -2.0,  # Defensive stance in winter
    },
    
    # Historical example:
    # Napoleon enters Russia: 600,000 troops
    # Reaches Moscow: 100,000 troops
    # Most losses = attrition, not combat
}
```

### IMPORTANT: Should Have for EA

#### 7. Weather & Seasons
```python
SEASONS = {
    "spring": {"months": [3,4,5], "modifier": "normal"},
    "summer": {"months": [6,7,8], "modifier": "optimal_campaigning"},
    "autumn": {"months": [9,10,11], "modifier": "mud_season", "movement": -1},
    "winter": {"months": [12,1,2], "modifier": "harsh", "attrition": +3},
}

# Winter in Russia = death sentence
# Mud season = armies stuck
# Summer = optimal for offense
```

#### 8. Siege Mechanics
```python
SIEGE_SYSTEM = {
    "fortress_levels": {
        1: {"garrison": 5000, "duration": 2},
        2: {"garrison": 10000, "duration": 4},
        3: {"garrison": 20000, "duration": 6},  # Major fortress
    },
    
    "siege_options": {
        "starve_out": "Slow but safe, requires blockade",
        "assault": "Fast but costly, 50% casualties",
        "bombardment": "Moderate speed, requires artillery",
        "negotiate": "Offer terms, may succeed if morale low",
    },
    
    "relief_force": "Breaks siege if arrives",
}
```

#### 9. War Goals & Peace Terms
```python
# What can you demand in peace?

WAR_GOALS = {
    "annex_territory": {
        "warscore_cost": "10-50 per region",
        "aggressive_expansion": "+10 per region",
    },
    "puppet_state": {
        "warscore_cost": "50-100 for whole nation",
        "creates_vassal": True,
    },
    "war_reparations": {
        "warscore_cost": "20-40",
        "gold_received": "500-2000",
    },
    "trade_rights": {
        "warscore_cost": "10-20",
        "income_bonus": "+50 gold/turn",
    },
    "release_nation": {
        "warscore_cost": "30-60",
        "creates_new_nation": True,
    },
}

# Warscore earned from:
# - Battles won
# - Regions occupied
# - Enemy capital held
# - Time at war (ticking warscore if winning)
```

### NICE TO HAVE: Post-EA

- Espionage network system
- Trade route mechanics  
- Legitimacy/government stability
- Religion mechanics (minor for this era)
- Detailed economic simulation
- Leader personality traits affecting army
- Naval battle events (not simulation)

---

## LLM Philosophy: The Golden Rule

> **LLMs explain, react, and color events — they don't cause them.**

### What This Means

```
RULES do:           LLM does:
─────────────       ──────────────────────
Combat math         Battle aftermath narrative
Movement validation Movement flavor text
Economy calculation Treasury warnings in-character
State changes       Explaining state changes
AI action EXECUTION AI action SELECTION (constrained)
```

### Why AI Action Selection IS Safe (Our Approach)

```python
# ChatGPT says: "🚫 AI action selection" - TOO CONSERVATIVE

# Their fear:
llm_output = "destroy_france()"  # LLM invents invalid action
game.execute(llm_output)          # Game breaks

# Our reality:
llm_output = ai_engine.decide(game_state)  # LLM picks from menu
validated = executor.validate(llm_output)   # Executor checks validity
if not validated:
    llm_output = fallback_rules(game_state) # Rule-based backup
result = executor.execute(llm_output)       # Rules handle execution

# LLM can't break anything because:
# 1. Can only choose from VALID building blocks
# 2. Executor validates before executing
# 3. Fallback to rules if LLM fails
# 4. Worst case = suboptimal AI play, not crashes
```

### The Spectrum of LLM Safety

```
SAFE ──────────────────────────────────────────────────► DANGEROUS

Flavor text    Diplomatic    AI action    Combat      State
only           letters       selection    resolution  mutation
                             (constrained)

     ◄── We use these ──►    ◄── Our     ◄── NEVER
                                 limit
```

---

## LLM Flavor Systems (Immersion Layer)

### 1. Dynamic Diplomatic Writing

**Instead of:** "France refuses peace."

**You get:**
> "The French court rejects your proposal with barely concealed contempt. 
> Marshal Berthier hints that Vienna will soon beg on far worse terms."

```python
DIPLOMATIC_LETTER_PROMPT = """
Write a diplomatic letter from {sender} to {recipient}.

Context:
- Relations: {relation_score} (-100 to +100)
- War score: {war_score} (who's winning)
- Recent events: {events}
- Sender personality: {personality}

The letter should:
- Match the sender's national character
- Reflect the power balance
- Be 2-4 sentences
- Sound period-appropriate (1800s formal)

Letter:
"""
```

### 2. Newspapers & Gazettes (Same Event, Different Spin)

**One battle, four perspectives:**

```python
NEWSPAPER_PROMPT = """
Write a brief newspaper excerpt about this event:
{event_description}

Write from the perspective of: {nation}
National bias: {bias_description}
Tone: {winning/losing/neutral}

Keep it to 2-3 sentences. Sound like 1800s journalism.
"""

# Example outputs for "France wins Battle of Austerlitz":

# FRENCH MONITEUR:
# "The Emperor's genius shines again! The armies of the Tsar 
# and Emperor Francis flee in disorder. Europe trembles before France!"

# BRITISH TIMES:
# "Reports from the continent suggest French forces prevailed 
# at Austerlitz. Our coalition allies regroup. The struggle continues."

# AUSTRIAN GAZETTE:
# "Our brave soldiers fought valiantly against overwhelming odds. 
# A tactical withdrawal preserves the army for future operations."

# RUSSIAN BULLETIN:
# "Fog and Austrian incompetence led to temporary setback. 
# The Tsar's armies remain unbroken in spirit."
```

### 3. AI Introspection (Illusion of Intelligence)

**After rule-based AI acts, LLM explains "why":**

```python
# RULES decided: Prussia moves army to Saxony
# LLM explains the "reasoning":

AI_INTROSPECTION_PROMPT = """
You are {nation}'s war council. Explain why you took these actions:
{actions_taken}

Context:
- Your goals: {strategic_goals}
- Current threats: {threats}
- Your personality: {personality}

Speak as if YOU decided this (even though rules did).
2-3 sentences, in-character.
"""

# Output:
# "The Prussian General Staff recognizes the threat to our 
# southern flank. By securing Saxony, we deny the French 
# a staging ground and protect Berlin. Discipline and 
# preparation shall carry the day."
```

**This creates the illusion of strategic thinking while rules do everything.**

### 4. Advisor Commentary (Biased, Not Optimal)

```python
ADVISOR_PERSONALITIES = {
    "marshal": {
        "bias": "aggressive",
        "concerns": ["glory", "victory", "honor"],
        "blind_spots": ["logistics", "politics", "cost"],
    },
    "treasurer": {
        "bias": "conservative", 
        "concerns": ["gold", "debt", "economy"],
        "blind_spots": ["military necessity", "honor"],
    },
    "diplomat": {
        "bias": "cautious",
        "concerns": ["reputation", "alliances", "treaties"],
        "blind_spots": ["military advantage", "decisive action"],
    },
    "spymaster": {
        "bias": "paranoid",
        "concerns": ["threats", "conspiracies", "information"],
        "blind_spots": ["opportunities", "trust"],
    },
}

# KEY RULE: Advisors give BIASED advice, not OPTIMAL advice
# They disagree with each other
# Player must weigh perspectives

ADVISOR_PROMPT = """
You are the {role} advising {ruler}.

Situation: {situation}
Your personality: {personality}
Your concerns: {concerns}

Give your perspective in 1-2 sentences.
Be biased toward your concerns. You may be wrong.
"""

# Example - "Should we attack Austria?"

# MARSHAL: "Strike now while they're divided! 
#           Glory awaits those who seize the moment!"

# TREASURER: "Another war? The treasury barely survived the last. 
#             Perhaps negotiation serves us better."

# DIPLOMAT: "An attack now would alarm Prussia and Russia. 
#            Consider the coalition this might provoke."
```

### 5. Pattern-Based Player Reputation

```python
# Track player behavior patterns
PLAYER_PATTERNS = {
    "treaties_broken": 0,
    "wars_started": 0,
    "allies_betrayed": 0,
    "mercy_shown": 0,
    "ruthless_actions": 0,
}

# Flavor text shifts based on patterns
REPUTATION_FLAVOR = {
    "betrayer": "Other nations eye your ambassadors with suspicion...",
    "warmonger": "Europe whispers of the 'Corsican Ogre'...",
    "merciful": "Even enemies speak grudgingly of your honor...",
    "cautious": "Some call it wisdom. Others, timidity...",
}

# AI nations reference this in diplomatic text
# Creates consequences without mechanical changes
```

### 6. Turn-End Narrative Summary

```python
TURN_SUMMARY_PROMPT = """
Summarize this turn's events as a historical narrator.

Events: {all_turn_events}
Current situation: {situation}
Dramatic tension: {what's at stake}

Write 3-4 sentences. Be dramatic but accurate.
End with a hook about what might happen next.
Sound like a history documentary narrator.
"""

# Output:
# "The summer of 1805 drew to a close with French eagles 
# advancing across Bavaria. Vienna trembled as Napoleon's 
# Grande Armée swept aside all opposition. Yet in the north, 
# Prussian drums began to beat. The Tsar's armies marched west. 
# The decisive hour approached..."
```

### 7. Battle Aftermath Reports

```python
BATTLE_AFTERMATH_PROMPT = """
Write a brief battle aftermath report.

Battle: {battle_name}
Victor: {winner}
Casualties: {attacker_casualties}, {defender_casualties}
Outcome: {outcome_type}

Write as a field report to the commanding general.
Include: the human cost, morale impact, strategic meaning.
2-3 sentences. Period-appropriate tone.
"""

# Output:
# "The fields outside Ulm are littered with the wreckage of 
# victory. We hold the ground, but the ranks are thin and 
# the men exhausted. The Austrians flee south. Shall we pursue?"
```

### LLM Call Budget (Realistic)

```python
LLM_CALL_BUDGET = {
    "per_turn_max": 3,          # Keep costs manageable
    "cache_duration": "1_turn",  # Reuse expensive calls
    
    # Priority order (if budget limited):
    "priority": [
        "turn_summary",          # 1 call, high impact
        "marshal_response",      # Player-facing
        "ai_introspection",      # Makes AI feel smart
        "newspaper",             # Can skip if tight
    ],
}

# One prompt can generate multiple outputs:
# "Write newspaper excerpts for France, Britain, Austria, Prussia"
# = 1 LLM call → 4 different texts
```

---

## Nation AI: Decision Trees + Dynamic Relevance

### The Hybrid Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NATION AI SYSTEM                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Every nation has: DECISION TREE (always runs)             │
│   Some nations get: LLM ENHANCEMENT (based on relevance)    │
│                                                              │
│   Relevance is DYNAMIC, not static tiers!                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### The Problem with Static Tiers

```python
# WRONG - Static tiers miss the chaos of history:

STATIC_TIERS = {
    "great_power": ["France", "Britain", "Prussia", "Austria", "Russia"],
    "secondary": ["Spain", "Bavaria", "Netherlands"],
    "minor": ["Saxony", "Naples", "Portugal"],  # ← WRONG! Portugal was CRITICAL
}

# In reality:
# - Portugal 1807: Minor backwater
# - Portugal 1808: CRITICAL (Peninsular War begins, Wellington lands)
# - Saxony 1813: Minor German state
# - Saxony 1813 (Leipzig): PIVOTAL (defection changes battle outcome)
# - Bavaria 1805: French ally
# - Bavaria 1813: Switches sides, opens southern Germany
```

### Dynamic Relevance System

```python
# backend/ai/relevance_engine.py

class RelevanceEngine:
    """
    Calculates which nations deserve LLM attention THIS TURN.
    Relevance is contextual, not permanent.
    """
    
    def calculate_relevance(self, nation: str, game_state: dict) -> float:
        """
        Returns 0.0-1.0 relevance score.
        High relevance = gets LLM call.
        """
        score = 0.0
        
        # Base relevance (great powers start higher)
        score += BASE_RELEVANCE.get(nation, 0.1)
        
        # ESCALATION TRIGGERS (can make anyone important)
        score += self._war_involvement(nation, game_state)
        score += self._border_tension(nation, game_state)
        score += self._player_interaction(nation, game_state)
        score += self._strategic_position(nation, game_state)
        score += self._recent_events(nation, game_state)
        score += self._diplomatic_crisis(nation, game_state)
        score += self._betrayal_potential(nation, game_state)
        
        return min(1.0, score)  # Cap at 1.0


BASE_RELEVANCE = {
    # Great powers always somewhat relevant
    "France": 0.4, "Britain": 0.4, "Prussia": 0.4, 
    "Austria": 0.4, "Russia": 0.4,
    
    # Secondary powers - moderate base
    "Spain": 0.2, "Bavaria": 0.2, "Netherlands": 0.2,
    
    # Minor powers - low base, but CAN escalate
    "Saxony": 0.1, "Naples": 0.1, "Portugal": 0.1,
    "Württemberg": 0.1, "Baden": 0.1, "Denmark": 0.1,
}
```

### Escalation Triggers (What Makes Nations Important)

```python
ESCALATION_TRIGGERS = {
    
    # ════════════════════════════════════════════════════════
    # MILITARY ESCALATION
    # ════════════════════════════════════════════════════════
    
    "at_war_with_player": +0.5,        # Actively fighting player
    "at_war_with_great_power": +0.3,   # In a major war
    "army_in_combat_zone": +0.2,       # Troops near fighting
    "just_won_battle": +0.2,           # Recent victory (momentum)
    "just_lost_battle": +0.2,          # Recent defeat (desperate)
    "being_invaded": +0.4,             # Existential threat
    
    # ════════════════════════════════════════════════════════
    # GEOGRAPHIC ESCALATION  
    # ════════════════════════════════════════════════════════
    
    "borders_active_war": +0.3,        # War on their doorstep
    "strategic_chokepoint": +0.2,      # Controls key territory
    "player_army_adjacent": +0.3,      # Player threatening them
    "between_two_powers": +0.2,        # Caught in the middle
    
    # ════════════════════════════════════════════════════════
    # DIPLOMATIC ESCALATION
    # ════════════════════════════════════════════════════════
    
    "alliance_offer_pending": +0.3,    # Someone wants them
    "betrayal_imminent": +0.4,         # About to switch sides
    "war_declaration_considering": +0.3,  # Might join war
    "peace_negotiation_key": +0.3,     # Critical to peace deal
    "player_demanded_something": +0.4, # Player interacted directly
    
    # ════════════════════════════════════════════════════════
    # CHAOS ESCALATION (Random History Moments)
    # ════════════════════════════════════════════════════════
    
    "succession_crisis": +0.3,         # Leadership unstable
    "revolution_brewing": +0.4,        # Internal chaos
    "foreign_intervention": +0.3,      # Outside power meddling
    "unexpected_alliance": +0.3,       # Diplomatic surprise
    "key_figure_died": +0.2,           # Leadership change
}

def _war_involvement(self, nation: str, game_state: dict) -> float:
    """How involved is this nation in current wars?"""
    score = 0.0
    
    if game_state.is_at_war(nation, game_state.player_nation):
        score += 0.5  # Fighting the player = very relevant
    
    if game_state.is_at_war_with_any_great_power(nation):
        score += 0.3
    
    if game_state.has_army_in_combat_zone(nation):
        score += 0.2
    
    return score

def _player_interaction(self, nation: str, game_state: dict) -> float:
    """Has the player been interacting with this nation?"""
    score = 0.0
    
    recent_turns = game_state.get_recent_interactions(nation, turns=3)
    
    if "diplomatic_message" in recent_turns:
        score += 0.3  # Player sent them something
    
    if "demand" in recent_turns:
        score += 0.4  # Player demanded something
    
    if "war_declared" in recent_turns:
        score += 0.5  # Player declared war
    
    if "army_moved_adjacent" in recent_turns:
        score += 0.2  # Player moved army nearby
    
    return score

def _betrayal_potential(self, nation: str, game_state: dict) -> float:
    """Is this nation likely to switch sides?"""
    score = 0.0
    
    # Check for historical "betrayal moments"
    loyalty = game_state.get_alliance_loyalty(nation)
    war_weariness = game_state.get_war_weariness(nation)
    losing_side = game_state.is_on_losing_side(nation)
    
    if loyalty < 30 and war_weariness > 50:
        score += 0.3
    
    if losing_side and loyalty < 50:
        score += 0.2  # Might defect like Saxony at Leipzig
    
    if game_state.has_been_bribed(nation):
        score += 0.2
    
    return score
```

### The Relevance Threshold

```python
class NationController:
    """Decides which nations get LLM calls each turn."""
    
    # How relevant must a nation be to get LLM call?
    LLM_THRESHOLD = 0.5
    
    # Maximum LLM calls per turn (budget control)
    MAX_LLM_CALLS = 5
    
    def process_all_nations(self, game_state: dict) -> dict:
        """Process all nations, allocate LLM calls by relevance."""
        
        # Calculate relevance for everyone
        relevance_scores = {}
        for nation in game_state.all_nations:
            relevance_scores[nation] = self.relevance_engine.calculate_relevance(
                nation, game_state
            )
        
        # Sort by relevance
        sorted_nations = sorted(
            relevance_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Allocate LLM calls to most relevant
        llm_budget = self.MAX_LLM_CALLS
        results = {}
        
        for nation, relevance in sorted_nations:
            if relevance >= self.LLM_THRESHOLD and llm_budget > 0:
                # HIGH RELEVANCE: LLM decides + explains
                results[nation] = self._process_with_llm(nation, game_state)
                llm_budget -= 1
            else:
                # LOW RELEVANCE: Rules only
                results[nation] = self._process_with_rules(nation, game_state)
        
        return results
```

### Example: Portugal Escalation

```python
# Turn 1: Portugal is irrelevant
# relevance("Portugal") = 0.1 (base) = 0.1
# Result: Decision tree only, template text

# Turn 5: France invades Spain, threatens Portugal
# relevance("Portugal") = 0.1 (base) 
#                       + 0.3 (borders active war)
#                       + 0.3 (player army adjacent)
#                       = 0.7
# Result: LLM call! Portugal gets personality, makes decisions

# Portugal's LLM response:
# "The court in Lisbon watches French armies cross the Pyrenees 
#  with growing alarm. Prince Regent João weighs impossible choices:
#  submit to Napoleon's demands, or flee to Brazil and resist.
#  Britain promises naval support... but can they truly protect us?"

# Turn 8: Britain lands troops, Portugal joins coalition
# relevance("Portugal") = 0.1 (base)
#                       + 0.5 (at war with player)
#                       + 0.3 (alliance offer accepted)
#                       + 0.2 (strategic chokepoint)
#                       = 1.0+ (capped at 1.0)
# Result: Full LLM treatment, major player in the war
```

### Example: Saxony at Leipzig (Betrayal)

```python
# Turn 20: Saxony is French ally (minor)
# relevance("Saxony") = 0.1 (base)
#                     + 0.2 (army in combat zone)
#                     = 0.3
# Result: Decision tree, follows France

# Turn 22: Battle of Leipzig begins, France losing
# relevance("Saxony") = 0.1 (base)
#                     + 0.2 (army in combat zone)
#                     + 0.4 (betrayal imminent - losing side, low loyalty)
#                     + 0.3 (between two powers)
#                     = 1.0
# Result: LLM call for CRITICAL decision moment

# LLM prompt includes:
# - Saxony's war weariness (high)
# - Alliance loyalty to France (crumbling)
# - Coalition offers (Prussia promising territory)
# - Battle situation (France surrounded)

# LLM might decide: DEFECT
# "In the chaos of battle, Saxon regiments wheel about. 
#  Their guns, once aimed at Prussians, now fire into 
#  French ranks. King Frederick Augustus watches in silence
#  as his kingdom changes sides. Necessity, he tells himself.
#  Not betrayal. Necessity."
```

### Decision Tree Structure (Always Runs)

```python
class NationDecisionTree:
    """
    Rule-based decisions for ALL nations.
    LLM enhances but never replaces this.
    """
    
    def decide(self, nation: str, game_state: dict) -> list[Action]:
        """Priority-based decision tree."""
        
        personality = NATION_PERSONALITIES[nation]
        situation = self._analyze_situation(nation, game_state)
        
        # ══════════════════════════════════════════════════
        # PRIORITY 1: SURVIVAL (always checked first)
        # ══════════════════════════════════════════════════
        if situation.capital_threatened:
            return self._survival_mode(nation, game_state)
        
        if situation.army_destroyed:
            return self._desperate_measures(nation, game_state)
        
        # ══════════════════════════════════════════════════
        # PRIORITY 2: ACTIVE WAR DECISIONS
        # ══════════════════════════════════════════════════
        if situation.at_war:
            # Should we seek peace?
            if self._should_seek_peace(nation, situation, personality):
                return [Action("propose_peace", target=situation.strongest_enemy)]
            
            # Should we betray our allies?
            if self._should_switch_sides(nation, situation, personality):
                return [Action("defect", target=situation.current_alliance)]
            
            # Fight or defend?
            if personality["aggression"] > 0.5 and situation.military_advantage:
                return self._offensive_operations(nation, game_state)
            else:
                return self._defensive_operations(nation, game_state)
        
        # ══════════════════════════════════════════════════
        # PRIORITY 3: PEACE BUT THREATENED
        # ══════════════════════════════════════════════════
        if situation.neighbor_at_war:
            # Prepare for war spreading
            return self._mobilization(nation, game_state)
        
        if situation.player_threatening:
            # Player army nearby, diplomacy needed
            if personality["courage"] < 0.4:
                return [Action("appease", target="player")]
            else:
                return [Action("prepare_defense")]
        
        # ══════════════════════════════════════════════════
        # PRIORITY 4: OPPORTUNISM
        # ══════════════════════════════════════════════════
        opportunity = self._find_opportunity(nation, game_state)
        if opportunity and personality["opportunism"] > 0.5:
            return [Action("exploit_opportunity", target=opportunity)]
        
        # ══════════════════════════════════════════════════
        # PRIORITY 5: PEACETIME DEVELOPMENT
        # ══════════════════════════════════════════════════
        return self._peacetime_actions(nation, game_state)
    
    def _should_switch_sides(self, nation, situation, personality) -> bool:
        """
        The Saxony-at-Leipzig calculation.
        When do nations betray their allies?
        """
        # Factors that increase betrayal chance:
        betrayal_score = 0
        
        # Losing the war badly
        if situation.alliance_war_score < -30:
            betrayal_score += 30
        
        # Low loyalty to current alliance
        betrayal_score += (100 - situation.alliance_loyalty) * 0.3
        
        # High war weariness
        betrayal_score += situation.war_weariness * 0.3
        
        # Been offered good terms by enemy
        if situation.enemy_offering_terms:
            betrayal_score += 20
        
        # Personality factors
        betrayal_score *= personality["pragmatism"]
        betrayal_score *= (1 - personality["honor"])
        
        # Random factor (history is chaotic)
        betrayal_score += random.randint(-10, 10)
        
        return betrayal_score > 60  # Threshold for defection


NATION_PERSONALITIES = {
    # Great Powers
    "France": {
        "aggression": 0.8, "courage": 0.9, "pragmatism": 0.6,
        "honor": 0.4, "opportunism": 0.7,
    },
    "Britain": {
        "aggression": 0.4, "courage": 0.7, "pragmatism": 0.8,
        "honor": 0.6, "opportunism": 0.5,
    },
    "Prussia": {
        "aggression": 0.6, "courage": 0.8, "pragmatism": 0.5,
        "honor": 0.7, "opportunism": 0.4,
    },
    "Austria": {
        "aggression": 0.3, "courage": 0.5, "pragmatism": 0.8,
        "honor": 0.6, "opportunism": 0.6,
    },
    "Russia": {
        "aggression": 0.5, "courage": 0.7, "pragmatism": 0.4,
        "honor": 0.5, "opportunism": 0.3,
    },
    
    # Secondary/Minor - more likely to bend
    "Bavaria": {
        "aggression": 0.3, "courage": 0.4, "pragmatism": 0.9,  # Very pragmatic
        "honor": 0.3, "opportunism": 0.8,  # Switched sides twice historically
    },
    "Saxony": {
        "aggression": 0.2, "courage": 0.3, "pragmatism": 0.8,
        "honor": 0.4, "opportunism": 0.7,  # Leipzig defection
    },
    "Portugal": {
        "aggression": 0.3, "courage": 0.6, "pragmatism": 0.5,
        "honor": 0.7, "opportunism": 0.3,  # Loyal to Britain historically
    },
    "Spain": {
        "aggression": 0.5, "courage": 0.8, "pragmatism": 0.2,
        "honor": 0.9, "opportunism": 0.2,  # Proud, resisted to the end
    },
}
```

### Random Historical Events (Chaos Generator)

```python
class ChaosEngine:
    """
    Generates random events that make minor nations suddenly important.
    Simulates the unpredictability of history.
    """
    
    CHAOS_EVENTS = [
        {
            "name": "Succession Crisis",
            "description": "The {nation} throne is disputed",
            "relevance_boost": +0.4,
            "effects": ["instability", "foreign_intervention_possible"],
            "weight": 0.02,  # 2% chance per nation per turn
        },
        {
            "name": "Popular Uprising",
            "description": "The people of {nation} rise against their rulers",
            "relevance_boost": +0.5,
            "effects": ["instability", "potential_revolution"],
            "weight": 0.01,
        },
        {
            "name": "Secret Alliance Revealed",
            "description": "{nation} has been negotiating with {enemy}",
            "relevance_boost": +0.3,
            "effects": ["diplomatic_crisis", "trust_broken"],
            "weight": 0.02,
        },
        {
            "name": "Key General Dies",
            "description": "{nation}'s best commander has died",
            "relevance_boost": +0.2,
            "effects": ["military_weakness", "mourning"],
            "weight": 0.03,
        },
        {
            "name": "Economic Collapse",
            "description": "{nation}'s treasury is empty",
            "relevance_boost": +0.3,
            "effects": ["desperate", "seeking_peace_or_plunder"],
            "weight": 0.02,
        },
        {
            "name": "Foreign Gold Arrives",
            "description": "{nation} receives substantial subsidies",
            "relevance_boost": +0.2,
            "effects": ["emboldened", "might_enter_war"],
            "weight": 0.03,
        },
        {
            "name": "Nationalist Awakening",  
            "description": "Patriotic fervor sweeps {nation}",
            "relevance_boost": +0.3,
            "effects": ["resistance_to_occupation", "won't_surrender"],
            "weight": 0.02,
        },
    ]
    
    def roll_for_chaos(self, game_state: dict) -> list[Event]:
        """Check each nation for random events."""
        events = []
        
        for nation in game_state.all_nations:
            for event_template in self.CHAOS_EVENTS:
                if random.random() < event_template["weight"]:
                    # Chaos strikes!
                    event = self._create_event(nation, event_template, game_state)
                    events.append(event)
                    
                    # Boost nation's relevance
                    game_state.add_relevance_modifier(
                        nation, 
                        event_template["relevance_boost"],
                        duration=3  # Lasts 3 turns
                    )
        
        return events
```

### Summary: The Complete Flow

```
TURN START
    │
    ▼
┌─────────────────────────────────────────┐
│  CHAOS ENGINE                           │
│  Roll for random events                 │
│  (Succession crisis, uprising, etc.)    │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  RELEVANCE ENGINE                       │
│  Calculate relevance for ALL nations    │
│  (Base + Escalation triggers + Chaos)   │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  SORT BY RELEVANCE                      │
│  Top 5 get LLM calls                    │
│  Rest use decision trees only           │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  FOR EACH NATION:                       │
│                                         │
│  if relevance >= 0.5 AND budget > 0:    │
│      LLM suggests actions               │
│      LLM explains "reasoning"           │
│  else:                                  │
│      Decision tree chooses actions      │
│      Template text for explanation      │
│                                         │
│  Executor validates all actions         │
│  Rules execute all actions              │
└─────────────────────────────────────────┘
    │
    ▼
TURN END
```

### What LLM Should NEVER Do

```python
LLM_FORBIDDEN = [
    "Calculate combat results",      # Rules only
    "Determine movement validity",   # Rules only  
    "Compute economy/income",        # Rules only
    "Mutate game state directly",    # Rules only
    "Generate random numbers",       # Use seeded RNG
    "Make final decisions",          # Can suggest, rules decide
]

# If it changes numbers → RULES ONLY
# If it generates text → LLM OK
```

### Token Monetization & LLM Options (EA)

**Three ways users can access LLM features:**

```python
LLM_ACCESS_MODES = {
    # ============================================================
    # 1. FREE TIER (Always Available)
    # ============================================================
    "free_tier": {
        "mock_parsing": True,           # Keyword matching always works
        "llm_responses": False,         # No personality dialogue
        "ai_nations": "rule_based",     # Simple AI, no LLM
        "turn_summaries": False,        # No narrative generation
        "diplomatic_chat": False,       # No LLM negotiation
        "cost": "Free forever",
    },
    
    # ============================================================
    # 2. IN-HOUSE TOKEN PACKAGES (Buy in UI)
    # ============================================================
    "token_packages": {
        "description": "Purchase tokens through game UI",
        "payment": "Stripe/PayPal integration",
        "tokens_stored": "Server-side per user account",
        
        "packages": {
            "starter": {
                "price": "$2.99",
                "tokens": 50_000,        # ~50 full games
                "per_game": "~$0.06",
            },
            "standard": {
                "price": "$9.99",
                "tokens": 200_000,       # ~200 games
                "per_game": "~$0.05",
            },
            "enthusiast": {
                "price": "$24.99",
                "tokens": 600_000,       # ~600 games
                "per_game": "~$0.04",
            },
        },
        
        "ui_features": [
            "Token balance shown in settings",
            "Low balance warning (< 5000 tokens)",
            "Purchase button in-game",
            "Usage tracking per feature",
        ],
    },
    
    # ============================================================
    # 3. BRING YOUR OWN KEY (BYOK)
    # ============================================================
    "byok": {
        "description": "Use your own Anthropic API key",
        "cost_to_us": "$0",
        "cost_to_user": "Their API costs (~$0.50-1.00/game)",
        
        "setup": [
            "User enters API key in settings",
            "Key stored locally (never sent to our servers)",
            "All LLM calls go direct to Anthropic",
            "No token limits",
        ],
        
        "advantages": [
            "Power users who want unlimited access",
            "Developers testing/modding",
            "Users with existing Anthropic accounts",
            "No ongoing cost to us",
        ],
        
        "ui_features": [
            "API key input field (masked)",
            "Key validation on entry",
            "Clear 'using your key' indicator",
            "Easy switch back to token mode",
        ],
    },
}
```

### Backend Architecture for Token System

```python
# backend/ai/token_manager.py

class TokenManager:
    """Manages LLM access modes and token consumption."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.mode = self._determine_mode()
    
    def _determine_mode(self) -> str:
        """Determine which LLM mode to use."""
        if self._has_byok_key():
            return "byok"
        elif self._has_tokens():
            return "in_house"
        else:
            return "free"
    
    def can_use_llm(self, feature: str) -> bool:
        """Check if user can use LLM for a feature."""
        if self.mode == "free":
            return False
        if self.mode == "byok":
            return True  # No limits
        if self.mode == "in_house":
            estimated_cost = self._estimate_tokens(feature)
            return self.get_balance() >= estimated_cost
        return False
    
    def consume_tokens(self, actual_usage: int) -> bool:
        """Deduct tokens after LLM call."""
        if self.mode != "in_house":
            return True  # BYOK doesn't track
        
        current = self.get_balance()
        if current < actual_usage:
            return False
        
        self._update_balance(current - actual_usage)
        return True
    
    def get_llm_client(self):
        """Return appropriate LLM client based on mode."""
        if self.mode == "byok":
            return LLMClient(api_key=self._get_byok_key())
        elif self.mode == "in_house":
            return LLMClient(api_key=MASTER_API_KEY)  # Our key
        else:
            return MockLLMClient()  # Free tier fallback

# Token costs by feature (estimated)
TOKEN_COSTS = {
    "command_parse": 200,        # Haiku, cheap
    "marshal_response": 800,     # Sonnet, personality
    "ai_nation_turn": 1500,      # Sonnet, strategy
    "turn_summary": 1000,        # Sonnet, narrative
    "diplomatic_chat": 1200,     # Sonnet, negotiation
    "lore_query": 600,           # Sonnet, historical
}
```

### UI Requirements for Token System

```gdscript
# Settings screen needs:
# 1. Current mode indicator ("Free" / "Tokens: 45,230" / "Using Your Key")
# 2. Token purchase button (opens payment modal)
# 3. BYOK key input field
# 4. Usage history/stats
# 5. Mode switch controls

# In-game indicators:
# - Subtle token balance in corner (if using tokens)
# - "LLM Enhanced" badge on features using real LLM
# - Warning when balance low
```

---

## Configuration

### Environment Variables (`.env`)
```
ANTHROPIC_API_KEY=sk-...  # Required only for real LLM mode
```

### Server Configuration
- Port: 8005 (NOT 8000!)
- Host: 127.0.0.1
- CORS enabled for Godot client
- Change port in BOTH `backend/main.py` AND `godot-client/.../api_client.gd`

---

## Map System

### Current State (MVP/Testing)
- 13 hardcoded regions in `region.py`
- Programmatic circles + lines in `map.gd`
- Simplified Western Europe
- **Purpose:** Test gameplay mechanics, not final map

### Future Vision (Early Access)
**EU4-style 2D map of 1805 Europe**

```python
# Target scope:
MAP_VISION = {
    "style": "EU4 political map",      # 2D, colored provinces
    "time_period": "1805",              # Pre-Austerlitz Europe
    "region_count": "200-400",          # Full Europe granularity
    "visual_approach": "Polygon2D",     # Real borders, not circles
    
    # Geographic coverage:
    "regions": {
        "western_europe": ["France", "Spain", "Portugal", "Britain"],
        "central_europe": ["Prussia", "Austria", "Bavaria", "Saxony", "Poland"],
        "eastern_europe": ["Russia", "Ottoman"],
        "italian_states": ["Piedmont", "Milan", "Venice", "Naples", "Papal States"],
        "minor_states": ["Switzerland", "Netherlands", "Denmark", "Sweden"],
    }
}
```

### Map Implementation Phases

**Phase 1 (Current):** Testing map
- 13 regions, circles
- Validate gameplay loop
- No art investment yet

**Phase 2 (Post-MVP):** Enhanced testing map
- Same 13 regions
- Polygon2D real shapes
- Dynamic colors on conquest
- Flash animations

**Phase 3 (Early Access):** Full Europe
- Historical 1805 borders
- Province-level granularity
- EU4-style aesthetic
- Zoomable/pannable
- Region tooltips with info

---

## Map Transition Strategy

### When to Commission Real Map Art

**DO NOT commission art until:**
1. ✅ Core gameplay loop is FUN and validated
2. ✅ Action economy feels right
3. ✅ Combat/conquest mechanics finalized
4. ✅ Region count decided (200? 300? 400?)
5. ✅ EA feature scope locked
6. ⏳ You have players saying "this is fun but the map is ugly"

**Recommended timing:**
- **Now:** Keep testing with circles/programmatic
- **After MVP ships:** Get player feedback
- **Pre-EA (2-4 weeks before):** Commission map art
- **EA Launch:** Ship with real map

### How to Source the Map

**Option 1: Commission Artist (Recommended)**
```
Cost: $300-800 for EU4-style political map
Where: Fiverr, ArtStation, DeviantArt commissions
Deliverable: SVG or layered PSD with individual provinces
Time: 2-4 weeks typically

Requirements to specify:
- EU4/Victoria aesthetic
- 1805 historical borders
- Each province as separate path/layer
- Consistent art style
- Color-neutral (you'll recolor in code)
```

**Option 2: Historical Map + Trace**
```
Cost: $0-100 (your time or cheap trace)
Source: Public domain 1805 maps
Process: Trace provinces in Inkscape/Illustrator
Deliverable: SVG with path IDs matching region names
Time: 10-20 hours of work

Pros: Historically accurate
Cons: Time consuming, may look amateur
```

**Option 3: Procedural Generation**
```
Cost: Development time only
Process: Generate Voronoi regions, fit to coastlines
Tools: Godot + algorithms
Deliverable: Runtime-generated map

Pros: Infinitely scalable, moddable
Cons: Doesn't look historical, more dev work
```

**Recommendation:** Option 1 for EA. Commission when you know exact region count.

### Graceful Code Transition

**Key Principle:** Map data is SEPARATE from map rendering.

```python
# backend/models/region.py - Data layer (doesn't care about visuals)

# Current (MVP):
REGIONS_DATA = {
    "Paris": {"adjacent": ["Belgium", "Lyon"], "income": 100},
    # ... 13 regions
}

# Future (EA): Just add more regions, same structure
REGIONS_DATA = {
    "Ile-de-France": {"adjacent": ["Champagne", "Normandy"], "income": 150},
    "Champagne": {"adjacent": ["Ile-de-France", "Lorraine"], "income": 80},
    # ... 200+ regions
}

# The executor, combat, pathfinding don't care how many regions exist
# They just query the data structure
```

```gdscript
# godot-client/scenes/map.gd - Visual layer

# Step 1: Abstract region rendering (do this NOW)
class_name MapRenderer

# Instead of hardcoded positions:
var region_visuals = {}  # region_name -> visual_node

func load_map_data(data_source: String):
    """Load map from external file, not hardcoded."""
    var data = load_region_data(data_source)
    for region_name in data:
        var visual = create_region_visual(data[region_name])
        region_visuals[region_name] = visual

func create_region_visual(region_data: Dictionary) -> Node2D:
    """Create visual for a region. Override for different map styles."""
    # MVP: Circle at position
    # Future: Polygon2D from vertex data
    pass

func update_region_color(region_name: String, color: Color):
    """Update any region regardless of visual style."""
    if region_visuals.has(region_name):
        region_visuals[region_name].set_color(color)
```

### Data File Structure for Real Map

```json
// assets/maps/europe_1805.json
{
    "map_id": "europe_1805",
    "version": "1.0",
    "regions": {
        "Ile-de-France": {
            "display_name": "Île-de-France",
            "polygon_points": [[100,200], [150,180], [180,220], ...],
            "center": [140, 200],
            "label_position": [140, 195],
            "adjacent": ["Champagne", "Normandy", "Orleans", "Burgundy"],
            "income": 150,
            "is_capital": true,
            "culture": "French",
            "terrain": "plains"
        },
        // ... 200+ more regions
    },
    "sea_zones": {
        "English_Channel": {
            "polygon_points": [...],
            "adjacent_land": ["Normandy", "Picardy", "Kent", "Sussex"]
        }
    },
    "visual_settings": {
        "default_scale": 1.0,
        "min_zoom": 0.5,
        "max_zoom": 3.0
    }
}
```

### Migration Checklist

```markdown
## Pre-Migration (Now)
- [ ] Abstract region rendering in map.gd
- [ ] Move region data to external JSON file
- [ ] Create MapRenderer class with override points
- [ ] Test that gameplay works with any region count

## Migration Day (When art ready)
- [ ] Import new map JSON with 200+ regions
- [ ] Update backend REGIONS_DATA to match
- [ ] Test pathfinding with larger graph
- [ ] Verify all region names match between frontend/backend
- [ ] Performance test with full region count
- [ ] Add zoom/pan controls for larger map

## Post-Migration
- [ ] Adjust balance for more granular regions
- [ ] Update AI pathfinding weights
- [ ] Add region tooltips
- [ ] Add minimap for navigation
```

### Why EU4 Style?
- Proven readable at strategic scale
- Works with many regions
- Players understand the visual language
- Supports mod-friendly data files
- 2D is much simpler than 3D

---

## Don't Do

- ❌ Don't use separate dicts for player/enemy marshals
- ❌ Don't return floats to Godot (always wrap with `int()`)
- ❌ Don't add features outside current phase scope
- ❌ Don't change port without updating api_client.gd
- ❌ Don't add naval ship combat (abstracted instead)
- ❌ Don't make executor LLM-dependent (keep deterministic)
- ❌ Don't store API keys in code (use .env)

---

## Project Phases

### Phase 1: MVP (Current - 85% complete)
- ✅ Core gameplay loop
- ✅ Action economy
- ✅ Combat resolution
- ⏳ Victory/defeat screens
- ⏳ Full playthrough test

### Phase 2: LLM Integration (Next)
- Real Claude API for marshal responses
- Personality-driven dialogue
- Response caching

### Phase 3: AI Nations
- AI turn phase
- LLM decision engine for enemies
- Coalition coordination

### Phase 4: Diplomacy
- Natural language negotiation
- Treaty system
- Reputation tracking

### Phase 5: Early Access
- Year-based timeline
- Character death/replacement
- Vassal system
- Token monetization

---

## Reference Documents

For detailed design decisions and architecture:
- `PM_REVIEW_AND_ROADMAP.md` - Full assessment and phase plans
- `LLM_INTEGRATION_ARCHITECTURE.md` - Technical LLM specs
- `MVP_CREATION_LOG.md` - Development history and bug fixes
- `command-based-design.md` - Core gameplay vision

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Godot float→int error | Wrap all numeric returns with `int()` |
| Enemy not persisting | Check using unified `world.marshals` dict |
| Port connection failed | Verify port 8005 in both backend and frontend |
| Command not recognized | Add to `valid_actions` in parser.py |
| Marshal selection wrong | Check `find_nearest_marshal_to_region()` filtering |