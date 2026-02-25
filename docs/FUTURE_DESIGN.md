# Ink & Iron: Future Design Concepts

> **CONCEPTUAL DESIGNS** — not yet implemented. Phase scheduling lives in ROADMAP.md.
> **Last Updated:** February 25, 2026 (Trimmed: removed implemented sections, archived verbose examples)

---

## Future Expansion (Early Access) - CONCEPTUAL/TBD

### Variable Action Costs
```python
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

### Nation-Specific Action Counts
Different nations have different administrative capacity (France 5, Prussia/Britain 4, Austria/Russia 3, Spain/Ottoman 2). Modifiable by tech, leader traits, stability. Penalties from overextension, instability, war exhaustion.

### Overextension System
`(non-core regions) / (core regions) * 100`. Thresholds at 25/50/100% cause escalating penalties (-actions, +revolt risk, -income). Reduced by time (regions become cores ~10 turns), cultural events, puppet states.

### Stability System
Scale -3 (Civil War) to +3 (Triumphant). Affects action count, revolt risk. Changed by victories, defeats, treaties, overextension, leader events.

---

## Diplomacy System (Phase 8)

- Natural language negotiation with AI leaders via persistent conversation threads
- LLM remembers broken promises, past deals
- Treaties are mechanical (peace, alliance, war declaration, envoy, treaty-breaking)
- Relationship level (-100 to +100), war weariness, active proposals

---

## Naval & Colonial Power Abstraction

**No ship-to-ship combat.** Britain's naval supremacy = economic/strategic effects (blockade -30% income, expeditionary support to coastal regions, trade dominance +100 gold/turn). France counters via Continental System, coastal forts, alliances.

**Colonies = "Colonial Power" score (0-100).** Britain 100, Spain 60, France 40, etc. Affects income (score * 5 gold/turn), war capacity, coalition funding, peace willingness. Reduced by instability, war exhaustion, revolts. Increased by naval victories, trade treaties.

---

## Early Access Expansion Plans

- **Timeline:** Year-based (1805-1815), monthly turns, ~120 turn campaign
- **Character Death:** Battle (5%), illness (2%/year), old age (10%/year over 60). LLM generates death narrative + replacement marshal.
- **Vassal System:** Conquered nations get autonomy levels (puppet/satellite/ally/independent). Loyalty affected by war weariness, French defeats, distance, nationalism.

---

## Missing Design Elements (EA Priority)

> Implemented systems: Supply/Logistics (Phase 6.2), Manpower Pools (Session 41), Fog of War (Sessions 33-36), Terrain (Phase 6.1), Attrition (Phase 6.2.F). See SYSTEMS_REFERENCE.md.

### Still Needed

| System | Priority | Notes |
|--------|----------|-------|
| Coalition Triggers | Phase 8 | Threat calculation, 2-4 turn warning, preventable via diplomacy |
| Weather & Seasons | EA | Spring/summer/autumn/winter cycle, movement -1 in mud, +3 attrition in winter |
| Siege Mechanics | EA | 3 fortress levels, starve/assault/bombardment/negotiate options |
| War Goals & Peace Terms | EA | Warscore from battles/occupation/capital → annex/puppet/reparations/trade |
| Supply Lines (distance-based) | Post-EA | Armies can be unsupplied, foraging, combat penalty |
| Winter Attrition | Post-EA | Disease events, base idle attrition |

### Nice to Have (Post-EA)
Espionage, trade routes, legitimacy/government, religion (minor), detailed economics, leader traits, naval battle events.

---

## LLM Philosophy: The Golden Rule

> **LLMs explain, react, and color events — they don't cause them.**

| RULES do | LLM does |
|----------|----------|
| Combat math | Battle aftermath narrative |
| Movement validation | Movement flavor text |
| Economy calculation | Treasury warnings in-character |
| State changes | Explaining state changes |
| AI action EXECUTION | AI action SELECTION (constrained) |

AI action selection is safe because: LLM picks from valid building blocks, executor validates, fallback to rules on failure. Worst case = suboptimal AI play, not crashes. LLM **never** calculates combat, validates movement, computes economy, or mutates state.

---

## LLM Flavor Systems (Phase 8.5)

See ROADMAP.md Phase 8.5 for concrete implementation plan. Key systems:

- **Marshal Voice (3 tiers):** Templates → LLM Drama → Full Flavor
- **Gazette ("Le Moniteur"):** Every 3-5 turns, LLM-generated newspaper (same event, 4 perspectives)
- **AI Introspection:** After rule-based AI acts, LLM explains "why" (illusion of intelligence)
- **Advisor Commentary:** Biased, not optimal — marshal (aggressive), treasurer (conservative), diplomat (cautious), spymaster (paranoid). Player weighs perspectives.
- **Player Reputation:** Track behavior patterns (treaties broken, mercy shown) → flavor text shifts
- **Turn-End Narrative:** 3-4 sentence dramatic summary with hook
- **Battle Aftermath:** Field report style (human cost, morale impact, strategic meaning)

LLM call budget: max 3/turn, priority order: turn summary > marshal response > AI introspection > newspaper.

---

## Nation AI: Decision Trees + Dynamic Relevance (1805 Scope)

### The Hybrid Architecture

Every nation has a **decision tree** (always runs). High-relevance nations also get **LLM enhancement** (based on dynamic relevance score 0.0-1.0).

### Dynamic Relevance Engine

Relevance is contextual, not static. Base relevance (great powers 0.4, secondary 0.2, minor 0.1) + escalation triggers:

| Category | Triggers | Boost |
|----------|----------|-------|
| Military | At war with player, being invaded, army in combat zone | +0.2 to +0.5 |
| Geographic | Borders active war, strategic chokepoint, player army adjacent | +0.2 to +0.3 |
| Diplomatic | Alliance offer, betrayal imminent, peace negotiation | +0.3 to +0.4 |
| Chaos | Succession crisis, uprising, secret alliance revealed | +0.2 to +0.5 |

Nations above threshold (0.5) get LLM calls (max 5/turn). Below = decision tree + template text only.

**Key example:** Portugal starts at 0.1, escalates to 1.0 when France invades Spain + Britain lands troops. Saxony at Leipzig: low loyalty + losing side + enemy offers → betrayal_potential triggers LLM call for the critical defection decision.

### Decision Tree Priority Order
1. **Survival** — capital threatened, army destroyed
2. **Active War** — seek peace? betray allies? attack/defend?
3. **Peace but Threatened** — mobilize, appease, prepare
4. **Opportunism** — exploit weakness (personality-gated)
5. **Peacetime** — develop, trade, recruit

Nation personalities define aggression, courage, pragmatism, honor, opportunism (0.0-1.0). Betrayal calculation weighs war score, loyalty, weariness, enemy terms, personality.

### Chaos Engine
Random events (2-3% per nation per turn): succession crisis, popular uprising, secret alliance, key general dies, economic collapse, foreign gold, nationalist awakening. Each boosts relevance for 3 turns, making minor nations suddenly important.

---

## Core Territories (Post-EA)

Replace `historical_ownership` with `core_territories`. Core territories always give 60 stability on recapture. Non-core always 25. Cores expand after 50+ turns of stable control. Adds strategic depth ("invest in integrating Milan?").

---

## Army Cohesion (Deferred)

New Marshal field `cohesion: int` (0-100). Rabble/Green/Trained/Veterans with combat modifiers. Raised by drilling, winning battles, time together. Lowered by mass recruitment (dilution). **Deferred until playtesting shows morale dilution alone is insufficient.**

---

## Imperial Governance — Marshals as Military Governors (Phase 8.5/11)

> **NEEDS SPEC.** Raw concept — critical design risks identified below.

**Core idea:** Territory management through marshals, not spreadsheets. Marshal who conquers a region becomes military governor. Personality shapes outcomes (Davout stabilizes, Ney suppresses but damages long-term). **Best general = best governor** creates command dilemma.

**Anti-snowball requirements (spec must solve):**
- Governance must drain military strength (15-20k troops tied down per region)
- Bad governance must snowball (Ney in Madrid → partisans → supply cuts → second marshal needed)
- Player can't govern everything well (finite marshals, 80+ provinces)
- Conquest must create problems, not just rewards

**Garrison as anchor:** Existing garrison mechanic layers governance on top. Garrisoned = managed, ungarrisoned = rebel spawns, supply cuts, territory flips. No new command verb needed.

**Integration:** Phase 8 (Diplomacy) for peace transitions, Phase 8.5 (Events) for governance events, Phase 11 (Vassals) for endgame.

---

*Last updated February 25, 2026. Verbose code examples archived — see git history for full designs.*
