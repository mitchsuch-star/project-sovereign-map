# Ink & Iron: Future Design Concepts

> **CONCEPTUAL DESIGNS** — not yet implemented. Phase scheduling lives in ROADMAP.md.
> **Entries here are CONCEPTS, not promises.** Nothing in this file ships without an owner row/spec per CLAUDE.md Golden Rule 9; implemented systems are removed from this file as they land.
> **Last Updated:** July 2, 2026 (Landed systems removed: Phase 8 diplomacy, vassals, coalition triggers, war goals & peace terms)

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

**LANDED** — Phase 8 diplomacy is live in `diplomacy.py` and companion modules (treaties, relations, proposals, dialogue). See `docs/DIPLOMACY_SPEC.md` + `docs/SYSTEMS_REFERENCE.md`.

---

## Naval & Colonial Power Abstraction

> Live owner: the DEF-5 naval spec row in `docs/MAP_IMPLEMENTATION_PLAN.md`.

**No ship-to-ship combat.** Britain's naval supremacy = economic/strategic effects (blockade -30% income, expeditionary support to coastal regions, trade dominance +100 gold/turn). France counters via Continental System, coastal forts, alliances.

**Colonies = "Colonial Power" score (0-100).** Britain 100, Spain 60, France 40, etc. Affects income (score * 5 gold/turn), war capacity, coalition funding, peace willingness. Reduced by instability, war exhaustion, revolts. Increased by naval victories, trade treaties.

---

## Early Access Expansion Plans

- **Timeline:** Year-based (1805-1815), monthly turns, ~120 turn campaign
- **Character Death:** Battle (5%), illness (2%/year), old age (10%/year over 60). LLM generates death narrative + replacement marshal.
- **Vassal System:** LANDED — live in `vassal.py` (autonomy levels, loyalty, rebellion, tribute, investment). See `docs/SYSTEMS_REFERENCE.md`.

---

## Missing Design Elements (EA Priority)

> Implemented systems: Supply/Logistics (Phase 6.2), Manpower Pools (Session 41), Fog of War (Sessions 33-36), Terrain (Phase 6.1), Attrition (Phase 6.2.F), Coalition Triggers (LANDED — `coalition.py`, Phase 8), War Goals & Peace Terms (LANDED — WPS + Imperial Settlement + war bargains, April 2026). See SYSTEMS_REFERENCE.md.

### Still Needed

| System | Priority | Notes |
|--------|----------|-------|
| Weather & Seasons | EA | Spring/summer/autumn/winter cycle, movement -1 in mud, +3 attrition in winter. Concept only — no owner row; becomes a promise only when a phase adopts it |
| Siege Mechanics | EA | 3 fortress levels, starve/assault/bombardment/negotiate options. Concept only — no owner row; becomes a promise only when a phase adopts it |
| Supply Lines (distance-based) | Post-EA | Armies can be unsupplied, foraging, combat penalty |
| Winter Attrition | Post-EA | Disease events, base idle attrition. Concept only — no owner row; becomes a promise only when a phase adopts it |

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

### AI-AI Strategic Intent (Building Blocks Prep)

> **Status (July 2026):** Infrastructure is 95% nation-agnostic (Mar 2026 audit). `ai_diplomacy.py` now carries the Trigger 2 "Opportunistic Downgrade" (AI-AI relations slide toward war opportunistically), but the three named capabilities below remain unimplemented: opportunistic war declaration, AI vassalization of beaten opponents (`create_vassal_conquest()` still has no AI caller), and cross-AI peacetime threat assessment. **Owner: the ROADMAP critical-path 8c row.**

**What already works generically:**
- Combat, territory conquest, war declaration (via downgrade), treaty upgrades, nation elimination, vassal creation mechanics, enemy AI targeting (`get_enemies_of_nation()`)

**What's missing — 3 capabilities needed:**

1. **Opportunistic War Declaration** — AI nations never proactively decide "Saxony is weak, let's attack." Wars only happen through the passive rivalry downgrade spiral (adjacency friction → relation decay → state downgrades to WAR). Need: threat/opportunity scoring that evaluates troop ratios, undefended regions, and diplomatic isolation, then triggers `declare_war()` when conditions favor aggression. Gate by personality (opportunism score from Decision Tree above).

2. **AI Vassalization of Beaten Opponents** — When an AI nation conquers all regions of a smaller nation, that nation is simply eliminated. No AI code calls `create_vassal_conquest()`. Need: after conquest, AI evaluates whether to vassalize (keeps tribute flowing, buffer state) vs eliminate (cleaner, no rebellion risk). Decision factors: lord troop strength, distance to vassal, personality (pragmatic lords vassalize, aggressive lords annex).

3. **Cross-AI Threat Assessment** — AI nations assess threats only when already at war. Need: peacetime threat scoring between AI pairs. Factors: troop ratio, border adjacency, alliance networks, historical grievances (relation < -20), target isolation (no allies). Feed into Decision Tree Priority 4 (Opportunism) to generate war declaration proposals or preemptive alliance-seeking.

**Architecture note:** All three capabilities should use the same executor path as the player (Building Blocks). The enemy AI decision tree (`enemy_ai.py` P1-P8) already supports multi-nation targeting — these additions go in `ai_diplomacy.py` as new triggers in `_evaluate_ai_ai_proposal()` and `process_ai_ai_diplomatic_phase()`.

### Chaos Engine
Random events (2-3% per nation per turn): succession crisis, popular uprising, secret alliance, key general dies, economic collapse, foreign gold, nationalist awakening. Each boosts relevance for 3 turns, making minor nations suddenly important.

---

## Core Territories (Post-EA)

Replace `historical_ownership` with `core_territories`. Core territories always give 60 stability on recapture. Non-core always 25. Cores expand after 50+ turns of stable control. Adds strategic depth ("invest in integrating Milan?").

---

## Army Cohesion (Deferred)

New Marshal field `cohesion: int` (0-100). Rabble/Green/Trained/Veterans with combat modifiers. Raised by drilling, winning battles, time together. Lowered by mass recruitment (dilution). **Evaluate at the Marshal Content Pass design gate (`docs/MARSHAL_CONTENT_PASS_SPEC.md`) — else delete.**

---

## Imperial Governance — Marshals as Military Governors (Phase 8.5/11)

> **NEEDS SPEC.** Raw concept — critical design risks identified below.
> **Owner:** the ROADMAP Phase 8.5 Imperial Governance Events row + the Phase 11 Imperial Governance → Vassals row; the full system needs its own spec + design gate before any code.

**Core idea:** Territory management through marshals, not spreadsheets. Marshal who conquers a region becomes military governor. Personality shapes outcomes (Davout stabilizes, Ney suppresses but damages long-term). **Best general = best governor** creates command dilemma.

**Anti-snowball requirements (spec must solve):**
- Governance must drain military strength (15-20k troops tied down per region)
- Bad governance must snowball (Ney in Madrid → partisans → supply cuts → second marshal needed)
- Player can't govern everything well (finite marshals, 80+ provinces)
- Conquest must create problems, not just rewards

**Garrison as anchor:** Existing garrison mechanic layers governance on top. Garrisoned = managed, ungarrisoned = rebel spawns, supply cuts, territory flips. No new command verb needed.

**Integration:** Phase 8 (Diplomacy) for peace transitions, Phase 8.5 (Events) for governance events, Phase 11 (Vassals) for endgame.

---

*Last updated July 2, 2026. Verbose code examples archived — see git history for full designs.*
