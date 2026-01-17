# Objection & Compromise System

This document explains how marshals object to orders and what compromise options are available.

---

## Marshal Personalities

| Marshal | Personality | Description |
|---------|-------------|-------------|
| **Ney** | Aggressive | "The Bravest of the Brave" - Prefers attacking, hates defensive orders |
| **Davout** | Cautious | "The Iron Marshal" - Methodical, questions risky attacks |
| **Grouchy** | Literal | "The Unlucky" - Follows orders exactly, rarely objects |
| **Wellington** | Cautious | (Enemy) Defensive genius, avoids unnecessary risk |
| **Blucher** | Aggressive | (Enemy) "Marshal Forward" - Always wants to attack |

---

## Objection Triggers by Personality

### AGGRESSIVE (Ney, Blucher, Murat)

| Trigger | Severity | When It Fires |
|---------|----------|---------------|
| `defend` | 0.60 (Major) | Ordered to defend |
| `hold_position` | 0.60 (Major) | Ordered to hold position (alias for defend) |
| `wait` | 0.50 (Major) | Ordered to wait/pass turn |
| `wait_with_enemy_nearby` | 0.65 (Major) | Ordered to wait when enemy is adjacent |
| `retreat` | 0.70 (Major) | Ordered to retreat |
| `fortify` | 0.55 (Major) | Ordered to dig trenches |
| `drill_enemy_nearby` | 0.45 (Mild) | Ordered to drill when enemy is close |
| `defensive_stance` | 0.55 (Major) | Ordered to adopt defensive stance |
| `neutral_stance_from_aggressive` | 0.35 (Mild) | Ordered to stand down from aggressive |

**What Ney Says:**
- *Defend:* "Defend? While the enemy sits idle? Give me the order to attack, Sire!"
- *Fortify:* "Dig trenches? You want me to dig trenches like a coward?!"
- *Defensive Stance:* "A defensive posture? You want me to adopt the stance of a coward?!"

---

### CAUTIOUS (Davout, Wellington)

| Trigger | Severity | When It Fires |
|---------|----------|---------------|
| `certain_death` | 0.80 (Major) | Attack at 5:1+ odds |
| `attack_outnumbered_3to1` | 0.70 (Major) | Attack when outnumbered 3:1 |
| `attack_outnumbered_2to1` | 0.60 (Major) | Attack when outnumbered 2:1 |
| `attack_outnumbered_1_5to1` | 0.50 (Major) | Attack when outnumbered 1.5:1 |
| `attack_without_intel` | 0.55 (Major) | Attack unknown enemy (TODO: Phase 3) |
| `attack_fortified` | 0.60 (Major) | Attack a fortified position |
| `forced_march` | 0.45 (Mild) | Ordered to force march |
| `aggressive_stance` | 0.40 (Mild) | Ordered to adopt aggressive stance |
| `aggressive_stance_outnumbered` | 0.60 (Major) | Ordered aggressive when outnumbered |

**What Davout Says:**
- *Attack Outnumbered:* "The odds are not in our favor. A direct assault would be costly."
- *Attack Fortified:* "Those walls have withstood sieges before. We need artillery first."
- *Aggressive Stance:* "Aggressive posture? That exposes us unnecessarily, Sire."

---

### LITERAL (Grouchy)

| Trigger | Severity | When It Fires |
|---------|----------|---------------|
| `ambiguous_order` | 0.50 (Major) | Order is unclear (TODO: LLM detection) |
| `contradictory_orders` | 0.60 (Major) | Order contradicts previous (TODO) |
| `change_of_plans` | 0.35 (Mild) | Frequent order changes (TODO) |

**What Grouchy Says:**
- *Ambiguous:* "Sire, I must ask for clarification. What exactly do you require?"

*Note: Grouchy rarely objects - he follows orders literally, which can be a strength or weakness.*

---

### BALANCED (Soult, future marshals)

| Trigger | Severity | When It Fires |
|---------|----------|---------------|
| `certain_death` | 0.70 (Major) | Attack at 5:1+ odds |
| `expose_capital` | 0.55 (Major) | Moving away from Paris with no other defender |
| `suicidal_order` | 0.65 (Major) | Certain death order (TODO: expand) |
| `attack_outnumbered_3to1` | 0.60 (Major) | Very bad odds |
| `abandon_allies` | 0.50 (Major) | Leaving ally exposed (TODO: Phase 3) |

---

### LOYAL (Lannes, future marshals)

| Trigger | Severity | When It Fires |
|---------|----------|---------------|
| `suicidal_order` | 0.40 (Mild) | Even suicidal orders only mild objection |
| `certain_death` | 0.55 (Major) | Even loyal marshals object to 5:1+ odds |
| `betray_emperor` | 0.95 (Major) | Orders harming Napoleon (TODO: Phase 3) |
| `expose_capital` | 0.35 (Mild) | Trusts Emperor's judgment |

*Loyal marshals almost never refuse orders - they trust the Emperor implicitly.*

---

## Severity Levels

| Range | Type | Result |
|-------|------|--------|
| 0.00 - 0.19 | None | Marshal obeys without comment |
| 0.20 - 0.49 | Mild | Marshal grumbles but obeys |
| 0.50 - 0.95 | Major | Marshal refuses - player must choose |

---

## Player Choices on Major Objection

When a marshal has a **major objection**, you have three choices:

### 1. TRUST
- Accept marshal's alternative suggestion
- Marshal executes their preferred action instead
- Trust +12, Authority -3
- If marshal is proven right later: Vindication +1

### 2. INSIST
- Override marshal, force original order
- Trust -10 (if obeys), Trust -15 (if disobeys), Authority +2
- If you were right: Vindication -1 for marshal
- If marshal was right: They may become autonomous

### 3. COMPROMISE
- Execute a middle-ground action
- Trust +3, Authority -1
- Both sides give a little

---

## Compromise Rules

When you choose COMPROMISE, the system finds a middle-ground action:

### Basic Action Compromises

| Player Order | Marshal Wants | Compromise |
|--------------|---------------|------------|
| Attack | Defend | **Move** (approach but don't engage) |
| Defend | Attack | **Move** (advance cautiously) |
| Attack | Move | **Move** |
| Move | Attack | **Move** |
| Move | Defend | **Defend** |
| Defend | Move | **Move** |

### Tactical Action Compromises

| Player Order | Marshal Wants | Compromise |
|--------------|---------------|------------|
| Fortify | Attack | **Defend** (hold but stay mobile) |
| Fortify | Move | **Defend** |
| Fortify | Drill | **Drill** (active preparation) |
| Attack | Fortify | **Defend** |
| Drill | Attack | **Defend** |
| Drill | Move | **Defend** |
| Drill | Defend | **Defend** |
| Attack | Drill | **Defend** |

### Retreat Compromises

| Player Order | Marshal Wants | Compromise |
|--------------|---------------|------------|
| Retreat | Defend | **Defend** (hold, don't flee) |
| Retreat | Attack | **Defend** (neither attack nor flee) |
| Defend | Retreat | **Defend** |
| Attack | Retreat | **Defend** |

### Stance Compromises

| Player Order | Marshal Wants | Compromise |
|--------------|---------------|------------|
| Defensive Stance | Aggressive Stance | **Neutral Stance** |
| Aggressive Stance | Defensive Stance | **Neutral Stance** |

---

## CAUTIOUS Alternative Suggestions

When a CAUTIOUS marshal (Davout, Wellington) objects to an attack order, their suggested alternative depends on how badly outnumbered they are:

| Odds Against | Suggested Alternative | Rationale |
|--------------|----------------------|-----------|
| 3:1+ outnumbered | **RETREAT** | Too dangerous to hold - survival first |
| 2:1 outnumbered | **FORTIFY** | Dig in for maximum defense |
| 1.5:1 outnumbered | **DEFENSIVE STANCE** | Careful posture, not full fortification |

**Examples:**
- Davout (48k) vs Wellington (144k+) = 3:1+ → Suggests **Retreat**
- Davout (48k) vs Wellington (96k) = 2:1 → Suggests **Fortify**
- Davout (48k) vs Wellington (72k) = 1.5:1 → Suggests **Defensive Stance**

*Note: If the suggested action is unavailable (already fortified, already retreating, at Paris), falls back to Defend.*

---

## Example Scenarios

### Scenario 1: Ney Ordered to Fortify

```
You: "Ney, fortify your position"

Ney (Aggressive, Trust 75):
"Dig trenches? You want me to dig trenches like a coward?!"
[MAJOR OBJECTION - Severity 0.55]

Suggested Alternative: Attack Wellington

Your Choices:
1. TRUST - Let Ney attack instead
2. INSIST - Force Ney to fortify (Trust -10)
3. COMPROMISE - Ney defends (holds position but stays mobile)
```

### Scenario 2: Davout Ordered to Attack Superior Force (2:1 odds)

```
You: "Davout, attack Wellington" (Wellington has 96k, Davout has 48k)

Davout (Cautious, Trust 85):
"The odds are not in our favor. May I suggest we dig in and fortify?"
[MAJOR OBJECTION - Severity 0.60]

Suggested Alternative: Fortify current position

Your Choices:
1. TRUST - Let Davout fortify instead
2. INSIST - Force Davout to attack (Trust -10)
3. COMPROMISE - Davout defends (holds position but stays mobile)
```

### Scenario 3: Ney Ordered to Defensive Stance

```
You: "Ney, adopt defensive stance"

Ney (Aggressive, Trust 75):
"A defensive posture? You want me to adopt the stance of a coward?!"
[MAJOR OBJECTION - Severity 0.55]

Suggested Alternative: Aggressive stance

Your Choices:
1. TRUST - Let Ney stay aggressive
2. INSIST - Force defensive stance (Trust -10)
3. COMPROMISE - Ney adopts neutral stance (middle ground)
```

### Scenario 4: Grouchy Given Clear Orders

```
You: "Grouchy, move to Belgium"

Grouchy (Literal, Trust 65):
[NO OBJECTION - Grouchy follows orders exactly]

Result: Grouchy moves to Belgium without question.
```

---

## Trust & Authority Modifiers

These factors affect objection severity:

### Trust Modifier (4-Tier Steep Curve)

| Factor | Effect on Severity |
|--------|-------------------|
| Trust 80+ | 0.7x (much less likely to object) |
| Trust 40-79 | 1.0x (baseline) |
| Trust 20-39 | 1.3x (more likely to object) |
| Trust <20 | 1.6x (very likely to object) |

### Vindication Modifier (3-Tier System)

| Factor | Effect on Severity |
|--------|-------------------|
| Vindication ≥+3 | 1.15x (proven right, bolder) |
| Vindication -1 to +2 | 1.0x (neutral) |
| Vindication ≤-2 | 0.85x (proven wrong, quieter) |

### Other Modifiers

| Factor | Effect on Severity |
|--------|-------------------|
| Low Authority (<50) | 1.25x (higher severity) |
| Moderate Authority (50-79) | 1.1x |
| High Authority (80+) | 1.0x |
| Winning Streak | 0.85x (confident, less objection) |
| Losing Streak | 1.15x (questioning orders) |
| Frequently Overridden | 1.3x (resentful) |

---

## Quick Reference: Who Objects to What

| Order | Ney (Aggressive) | Davout (Cautious) | Grouchy (Literal) |
|-------|------------------|-------------------|-------------------|
| Attack | Happy | Objects if outnumbered (0.50-0.80) | Obeys |
| Defend | **Objects** (0.60) | Happy | Obeys |
| Hold | **Objects** (0.60) | Happy | Obeys |
| Wait | **Objects** (0.50-0.65) | Happy | Obeys |
| Fortify | **Objects** (0.55) | Happy | Obeys |
| Drill | Mild if enemy nearby (0.45) | Happy | Obeys |
| Retreat | **Strongly objects** (0.70) | Happy if losing | Obeys |
| Aggressive Stance | Happy | Mild objection (0.40-0.60) | Obeys |
| Defensive Stance | **Objects** (0.55) | Happy | Obeys |
| Move | Usually fine | Usually fine | Obeys |

---

## Hold vs Wait vs Defend

Three similar-sounding orders with different effects:

| Order | Action Cost | Effect | When to Use |
|-------|-------------|--------|-------------|
| **Defend** | 1 | Shifts to defensive stance, may fortify | Maximum defense |
| **Hold** | 1 | Same as defend | Prefer "hold the line" wording |
| **Wait** | **FREE (0)** | No effect, pass turn | Conserve actions |

**Examples:**
- "Ney, defend" → Ney shifts to defensive stance (1 action)
- "Ney, hold the line" → Same as defend (1 action)
- "Ney, wait" → Ney does nothing, no stance change (FREE)

**Key Insight:** Use `wait` when you want a marshal to skip their turn without changing their current state. Use `defend` or `hold` when you want them to actively adopt a defensive posture.

---

## Future Expansions (TODO)

- **Ambiguous Order Detection**: LLM detects unclear commands for Literal personality
- **Contradictory Orders**: Track order history, detect conflicts
- **Abandon Allies**: Detect when orders leave allied marshal exposed
- **Betray Emperor**: Political intrigue system for Loyal personality
- **Fog of War**: "Attack without intel" trigger for Cautious personality
