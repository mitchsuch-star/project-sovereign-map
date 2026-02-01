# Ink & Iron: Master Roadmap

> **THE source of truth for all phases and timeline.**
> **Other docs reference this — phase numbers only exist here.**
> **Last Updated:** February 1, 2026

---

## Quick Status

| Phase | Name | Status |
|-------|------|--------|
| 1-5.3 | Foundation through AI Fixes | ✅ COMPLETE |
| **6** | **Core Campaign Systems** | **📋 NEXT** |
| 6.5 | Information & UI Systems | 📋 Planned |
| 7 | Multi-Marshal & Relationships | 📋 Planned |
| 8 | Diplomacy & Coalitions | 📋 Planned |
| 8.5 | Events, Goals & National Identity | 📋 Planned |
| 9 | Advisors | 📋 Planned |
| 10 | Character & People | 📋 Planned |
| 11 | Vassals & Naval | 📋 Planned |
| 12 | Communication & Strategic Polish | 📋 Planned |
| Pre-EA | Polish & Infrastructure | 📋 Planned |
| EA | 1805 Campaign Launch | 🎯 TBD 2026 |

---

## Completed Phases ✅

| Phase | Name | Tests | Key Features |
|-------|------|-------|--------------|
| 1 | Foundation | ~80 | Core loop, actions, regions, marshals |
| 2 | Combat & AI | ~90 | Dice combat, enemy AI, stances, drill/fortify |
| 3 | Relationships | ~30 | Marshal relationships, historical values |
| 4 | LLM Integration | ~60 | Parsing, personality responses, BYOK |
| 5.1 | Tactical Feedback | 64 | Word-based scoring, strategic feedback |
| 5.2 | Strategic Commands | ~350 | MOVE_TO, PURSUE, HOLD, SUPPORT, interrupts, modding. Phase M (Strategic Objections) designed, not yet implemented |
| 5.3 | Enemy AI Fixes | ~15 | Stagnation counter, oscillation fixes, consolidation |

**Total Tests:** 1022 (verified Jan 31, 2026)

---

## Phase 6: Core Campaign Systems

**Goal:** Complete playable campaign loop with resources and win conditions.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Economy | Income per region, treasury, upkeep | Medium | 📋 |
| Reinforcements (Enemy) | AI can recruit troops | Low | 📋 |
| Manpower Pools | Separate: Infantry, Cavalry, Artillery | Medium | 📋 |
| Attrition | Movement/supply decay | Low | 📋 |
| Fog of War | Hidden enemies, scouting required | Medium | 📋 |
| Terrain | Region terrain affects combat/movement | Medium | 📋 |
| Sieges | Fortified cities require siege mechanics | Medium | 📋 |
| City Fortification | "Fortify this city" building action | Low | 📋 |
| Artillery Unit Type | Combat buffs like cavalry | Medium | 📋 |
| **War Score** | Visual progress toward victory/defeat | Low | 📋 |
| **Threat Indicator** | Coalition threat level, visible buildup | Low | 📋 |
| Turn Events Log | Track battles/captures/retreats per turn (feeds gazette system) | Low | 📋 |

**Dependencies:** None
**Exit Criteria:** Player manages economy, enemies reinforce, terrain matters, can see war progress

---

## Phase 6.5: Information & UI Systems

**Goal:** Player can track 200 regions, 30 marshals, 8 nations without drowning.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Notification System | Alerts for key events (invasions, deaths, diplomacy) | Medium | 📋 |
| Strategic Ledger | Overview screen: all marshals, armies, nations | Medium | 📋 |
| Marshal Management UI | View/manage all marshals, relationships, recruit | Medium | 📋 |
| Campaign Log | Scrollable history of major events | Low | 📋 |
| Tooltips | Hover info on regions, marshals, nations | Low | 📋 |

**Dependencies:** Phase 6 (needs data to display)  
**Exit Criteria:** Player has clear visibility into game state

---

## Phase 7: Multi-Marshal & Relationships

**Goal:** Multiple marshals fight together, relationships have gameplay impact.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Multi-marshal battles | Combined strength in single fight | High | 📋 |
| Command structure | Senior marshal leads combined force | Medium | 📋 |
| Coordination bonus/penalty | Relationships affect combined combat | Medium | 📋 |
| Strategic + Relationships | "Support Ney" → reaction based on feelings | Medium | 📋 |
| Jealousy system | Marshal getting all glory → others resent | Medium | 📋 |

### AI Enhancement: Combined Strength Evaluation ✅ IMPLEMENTED

**What:** AI evaluates attack decisions using combined strength of all friendly marshals in the same region, not just the individual marshal's strength.

**Why:** Prevents AI from being timid when it has overwhelming local superiority (e.g., two marshals trapped in dead-end should recognize they can fight their way out together).

**Note:** This affects DECISION-MAKING only. Actual coordinated attacks (combined damage) planned for Phase 7 multi-marshal commands.

### AI Enhancement: P0 Survival Instinct (Future)

**Current behavior:**
- AI only retreats via P0 when enemy is in same region AND ratio is below threshold
- A marshal at 10% strength might still counter-attack a full-strength enemy if personality is aggressive

**Proposed enhancement:**
- Add "critical survival" override to P0
- If marshal strength < 20% of starting_strength AND enemy in same region → ALWAYS retreat regardless of personality
- Rationale: Even Blucher wouldn't charge at 10% strength against a fresh army
- This is "survival instinct" not cowardice

**Implementation notes:**
- Add to P0 in enemy_ai.py, before personality threshold check
- Use starting_strength field (already tracked on marshal)
- Threshold could be personality-adjusted: Cautious 30%, Normal 20%, Aggressive 15%

**Status:** Planned for Phase 7

**Dependencies:** Phase 6.5 (Marshal Management UI)
**Exit Criteria:** Multi-marshal commands work, relationships affect outcomes

---

## Phase 8: Diplomacy & Coalitions

**Goal:** Wars start and end through negotiation. Coalitions form dynamically. Diplomacy feels like talking to PEOPLE.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Peace Treaties | LLM-powered negotiation | High | 📋 |
| Alliances | Form defensive/offensive pacts | Medium | 📋 |
| War Declarations | Formal with casus belli | Low | 📋 |
| Nation Relations | Values affect diplomacy options | Medium | 📋 |
| **Coalition System** | Threat level → coalition forms | High | 📋 CRITICAL |
| Tiered Nation AI | France smarter than minor nations | Medium | 📋 |
| **Diplomacy Chat** | LLM-powered conversations with nation leaders | High | 📋 |
| **Leader Personalities** | Distinct voices: Metternich (scheming), Alexander (idealistic), Frederick William (cautious), Castlereagh (pragmatic) | Medium | 📋 |
| Diplomatic Rules Engine | War score + relations → accept/reject (deterministic, LLM voices outcome) | Medium | 📋 |
| **AI Proposals** | AI offers peace, makes demands — LLM voices the proposal | Medium | 📋 |

### Diplomacy Chat Architecture

Player types natural language proposals. LLM generates leader response in-character. Rules engine resolves outcome deterministically. LLM narrates the result.

```
Player: "I offer Austria peace if they cede Tyrol"
  → LLM generates Metternich's response (in-character)
  → Rules engine: war score + relations + territory value → accept/reject/counter
  → LLM voices outcome: "Metternich smiles thinly..."
```

**Cost control:**
- 2 LLM calls per exchange (response + outcome narration)
- Last 3-4 exchanges as context only (prevents token creep)
- Max 3 diplomatic exchanges per turn (prevents cost abuse)
- Template fallback if LLM unavailable
- ~$0.0004-0.0008 per exchange (Haiku)

**Leader Personalities (per leader, not per nation):**

| Leader | Nation | Personality | Voice |
|--------|--------|-------------|-------|
| Metternich | Austria | Scheming | Calculating, poison-pill deals, never says what he means |
| Tsar Alexander | Russia | Idealistic | Grand gestures, emotional, unpredictable pivots |
| Frederick William | Prussia | Cautious | Deferential, follows strongest ally, hedges |
| Castlereagh | Britain | Pragmatic | Naval-focused, subsidy offers, cold cost-benefit |

**Dependencies:** Phase 6 (economy for peace terms)
**Exit Criteria:** Can negotiate peace, coalitions form, AI diplomacy feels alive, leaders have distinct voices

---

## Phase 8.5: Events, Goals & National Identity

**Goal:** Campaigns have narrative, nations feel distinct, player has objectives beyond "conquer."

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| **Events System** | Random + historical events with choices | High | 📋 |
| **National Goals** | "Unite Germany", "Defend the Isles", "Continental System" | Medium | 📋 |
| **National Flavor** | France FEELS different from Austria (unique mechanics) | Medium | 📋 |
| **Light Tech/Reforms** | Simple upgrades: conscription, tactics, administration | Medium | 📋 |
| **Campaign Objectives** | Victory conditions beyond territory (prestige, survival) | Medium | 📋 |
| Historical Moments | Coronation, Tilsit, Retreat from Moscow | Medium | 📋 |
| **Gazette System** | Period newspaper every 3-5 turns, LLM-generated recaps | Medium | 📋 |
| **Marshal Voice (Tier 1)** | Template personality responses for all command events | Low | 📋 |
| **Marshal Voice (Tier 2)** | LLM personality for high-drama moments (objections, combat, interrupts) | Medium | 📋 |
| **Music & Sound (Core)** | Battle drums on combat, march on movement, tension on objection, map ambient. Menus get theme. Sells the narrative systems above. | Medium | 📋 |

### Gazette System ("Le Moniteur")

Every 3-5 turns, generate a period newspaper summarizing recent events via single LLM call.

**Content:** Battles, territory changes, marshal heroics, tension/foreshadowing.
**Bias:** Written from French perspective. Post-EA: multiple nation perspectives.
**Trigger:** Every 5 turns by default. Force on: major battle, territory loss, marshal death.
**Skip:** If nothing meaningful happened (no battles, no territory change).

**Implementation:**
- `backend/ai/gazette.py` — prompt builder, trigger logic
- WorldState fields: `turns_since_last_gazette`, `gazette_history`, `turn_events_log`
- `turn_events_log` fed by `world.record_turn_event()` calls from executor/combat/turn_manager
- Event types: `battle`, `capture`, `retreat`, `objection`, `redemption`, `strategic_order`, `marshal_eliminated`
- Cost: ~$0.0005 per gazette (~$0.005 per 40-turn game)

### Marshal Voice System (Tiered)

Three tiers of personality expression, layered for cost control:

**Tier 1 — Templates (free, always-on):**
- 3-5 personality-specific variants per event type (move, attack, fortify, drill, stance, recruit)
- Selected by marshal personality. Example: Ney move → "Ney spurs forward!" vs Davout → "Davout advances in good order."
- File: `backend/ai/marshal_voice.py` — `TEMPLATES[personality][event_type] -> List[str]`

**Tier 2 — LLM Drama (default for high-stakes moments):**
- Triggers: objections, combat results, strategic interrupts, redemption, cannon fire, forced retreat
- 200-token prompt budget: marshal name, personality, trust, morale, event context
- Output: 1-2 sentences in-character
- Cache by (marshal, event_type, outcome) within session
- Fallback to Tier 1 template if LLM fails or mode=mock
- Cost: ~$0.001-0.003/turn (2-5 drama events max)

**Tier 3 — Full Flavor (opt-in player toggle, see Pre-EA):**
- ALL command responses get 1-sentence LLM personality color
- Same prompt as Tier 2 but for routine events
- ~$0.0004/command extra, warned in UI

**Integration:** `main.py` wraps executor result messages through `marshal_voice.get_response()`

**Dependencies:** Phase 8 (diplomacy for event outcomes)
**Exit Criteria:** Each campaign tells a story, nations play differently, marshals have personality voice, gazette provides narrative rhythm

---

## Phase 9: Advisors (Layer 1)

**Goal:** Implement VISION's "Three Layers of Agency" — advisors gate actions.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Advisor Characters | Talleyrand (diplomacy), Berthier (military) | Medium | 📋 |
| Action Gating | Advisors modify/delay/refuse orders | High | 📋 |
| Advisor Trust | Relationship affects options | Medium | 📋 |
| Advisor Dismissal | Fire advisor, lose capabilities | Low | 📋 |
| Diplomacy Integration | Advisors + peace treaties + LLM | High | 📋 |

**Dependencies:** Phase 8 (diplomacy system exists)  
**Exit Criteria:** Orders pass through advisors, advisors have agendas

---

## Phase 10: Character & People

**Goal:** Marshals feel like people who live, die, and can be replaced.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Marshal Death | Casualties in battle, old age | Medium | 📋 |
| Marshal Pool | Historical marshals waiting activation | Low | 📋 |
| LLM Replacements | Generate new marshals when pool empty | Medium | 📋 |
| Recruit Marshals | Activate from pool (costs resources) | Low | 📋 |
| Traits System | Acquired traits from events | Medium | 📋 |

**Dependencies:** Phase 6 (economy for recruitment costs)  
**Exit Criteria:** Marshals can die, player can recruit replacements

---

## Phase 11: Vassals & Naval

**Goal:** Puppet states and Britain's unique naval mechanics.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Create Vassals | Puppet states from conquests | Medium | 📋 |
| Autonomy Levels | Low/Medium/High affects tribute | Medium | 📋 |
| Vassal Troops | Vassal armies fight for overlord | Medium | 📋 |
| Naval Abstraction | British blockades, expeditions | Medium | 📋 |
| No Ship Combat | Naval is strategic, not tactical | — | Design |

**Dependencies:** Phase 8 (diplomacy for vassal creation)  
**Exit Criteria:** Can create vassals, Britain has coastal mechanics

---

## Phase 12: Communication & Strategic Polish

**Goal:** Communication matters, orders can be cut off.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Communication Cutoff | No capital connection → autonomous | Medium | 📋 |
| Moving HQ | Napoleon's command center moves | Low | 📋 |
| Courier Delay | Distance affects order timing | Low | 📋 |

**Dependencies:** Phase 6 (map/region connectivity)  
**Exit Criteria:** Cut-off marshals act autonomously or follow last order

---

## Pre-EA Polish

**Goal:** Game is shippable, onboardable, monetizable, and IMMERSIVE.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Save/Load | Full game state persistence | Low | 📋 |
| Autosave | Per-turn automatic saves | Low | 📋 |
| Tutorial | 5-stage onboarding | Medium | 📋 |
| Voice-to-Text | Speak orders naturally | Medium | 📋 |
| **LLM Monetization** | BYOK + token tiers + payment | High | 📋 CRITICAL |
| At-will Autonomy | Grant autonomy anytime | Low | 📋 |
| At-will Administrator | Sideline marshal anytime | Low | 📋 |
| Increase Salary | Gold → Trust conversion | Low | 📋 |
| Modding Polish | Finish tools, docs, examples | Low | 🔄 Nearly done |
| LLM Efficiency | Caching, optimization | Medium | 📋 |
| Settings Menu | Audio, display, controls | Low | 📋 |
| Steam Integration | Achievements, cloud saves | Medium | 📋 |
| **Music & Sound (Polish)** | Full period orchestral, per-nation themes, dynamic intensity | Medium | 📋 |
| Difficulty Settings | AI bonuses, player handicaps | Low | 📋 |
| **Full Flavor Toggle** | Player setting for LLM voice on ALL commands (Marshal Voice Tier 3) | Low | 📋 |
| **LLM Cost Display** | Show token usage in settings, warn on full flavor mode | Low | 📋 |

**Dependencies:** All phases complete
**Exit Criteria:** Can save/load, new players learn, payments work, game feels alive

---

## 1805 Campaign Launch (Early Access)

**Goal:** The real game — full Europe, 8 nations, 10-year campaign.

| Feature | Description | Complexity | Notes |
|---------|-------------|------------|-------|
| **200+ Region Map** | Full Europe | HIGH | ⚠️ MAJOR UI WORK |
| **EU4-Style Rendering** | Polygons, borders, colors | HIGH | ⚠️ MAJOR UI WORK |
| Map Interaction | Click provinces, zoom, pan | HIGH | ⚠️ MAJOR UI WORK |
| 8+ Nations | France, Austria, Russia, Prussia, Britain, Spain, Bavaria, Ottoman | HIGH | Data + balance |
| 30+ Marshals | Historical personalities | Medium | Data entry |
| Year-Based Turns | Monthly 1805-1815 | Low | |
| 1805 Win Conditions | Per-nation victory conditions | Medium | Blocked by map |

**⚠️ UI CALLOUT:** The 1805 map is the single largest task. Estimate 4-6 weeks dedicated UI work:
- Province polygon rendering (not circles)
- Click detection on complex shapes
- Zoom/pan controls
- Region tooltips
- Dynamic coloring on conquest
- Possibly commissioned art ($300-800)
- **Cardinal direction system:** `REGION_POSITIONS` in `strategic_parser.py` must be expanded from 13 to 200+ entries with approximate grid coordinates for all new regions

**Dependencies:** All phases + Pre-EA complete  
**Exit Criteria:** Full 1805 campaign playable

---

## Post-EA Expansion

| Feature | Priority | Notes |
|---------|----------|-------|
| Multi-Nation Play | HIGH | Play as Austria, Russia, etc. |
| Coalition Player | HIGH | Lead coalition against France |
| Additional Start Dates | HIGH | 1809, 1812, 1815 scenarios |
| Weather System | MEDIUM | Russian winter, mud season |
| Advanced AI | MEDIUM | Flanking, capital defense |
| Campaign Editor | MEDIUM | Player-made scenarios |
| Steam Workshop | MEDIUM | Mod sharing |
| Accessibility | MEDIUM | Colorblind, fonts, keybinding |
| Mobile Port | LOW | Touch UI |
| Multiplayer | LOW | Co-op? Competitive? |

---

## Critical Path to EA

Must be done, in rough order:

1. ✅ Strategic Commands (done)
2. ✅ Enemy AI (done)
3. ✅ Serialization/Modding foundation (done)
4. 📋 Phase 6: Economy, Manpower, Terrain, Fog, War Score
5. 📋 Phase 6.5: Notifications, Ledger, Marshal UI
6. 📋 Phase 7: Multi-marshal, Relationships gameplay
7. 📋 Phase 8: Diplomacy, **Coalitions**, **Diplomacy Chat** (LLM leader conversations) ← CRITICAL
8. 📋 Phase 8.5: **Events, National Goals, Flavor**, **Gazette**, **Marshal Voice** ← Makes it a GAME
9. 📋 Phase 9: Advisors
10. 📋 Phase 10: Marshal death/recruitment
11. 📋 Phase 11: Vassals, Naval
12. 📋 Phase 12: Communication cutoff
13. 📋 Pre-EA: Save/Load, Tutorial, Voice, **LLM Monetization**, **Music**
14. 📋 **1805 Map UI** ← LARGEST SINGLE TASK
15. 📋 Steam Integration
16. 🎯 **TBD 2026: Early Access**

---

## Phase Dependencies Graph

```
Phase 6 (Economy/Terrain) ──┬──► Phase 6.5 (UI/Info) ──► Phase 7 (Multi-marshal)
                           │
                           ├──► Phase 8 (Diplomacy) ──► Phase 8.5 (Events/Goals)
                           │                                    │
                           │                                    ▼
                           │                            Phase 9 (Advisors)
                           │
                           ├──► Phase 10 (Characters)
                           │
                           └──► Phase 12 (Communication)

Phase 8 (Diplomacy) ──► Phase 11 (Vassals)

All Phases ──► Pre-EA Polish (Save, Tutorial, Music) ──► 1805 Map UI ──► EA Launch
```

---

## Timeline Estimate

| Milestone | Target | Notes |
|-----------|--------|-------|
| Phase 6 | +3-4 weeks | Economy, terrain, fog, manpower, war score |
| Phase 6.5 | +2 weeks | Notifications, ledger, marshal UI |
| Phase 7 | +2-3 weeks | Multi-marshal |
| Phase 8 | +3-4 weeks | Diplomacy, coalitions |
| Phase 8.5 | +3 weeks | Events, national goals, flavor |
| Phase 9 | +2-3 weeks | Advisors |
| Phase 10 | +2 weeks | Characters |
| Phase 11 | +2 weeks | Vassals, naval |
| Phase 12 | +1 week | Communication |
| Pre-EA | +4 weeks | Polish, monetization, music |
| 1805 Map | +4-6 weeks | **Major UI work** |
| Buffer | +2 weeks | Bug fixes, testing |
| **Early Access** | **TBD 2026** | |

---

## LLM Cost Budget (Per 40-Turn Game)

| System | Phase | Calls | Cost |
|--------|-------|-------|------|
| Command parsing (existing) | 4 | ~40 LLM + ~360 free | ~$0.016 |
| Marshal Voice Tier 2 | 8.5 | ~30-50 drama events | ~$0.012-0.020 |
| Gazette | 8.5 | ~8 gazettes | ~$0.004 |
| Diplomacy Chat | 8 | ~40-60 exchanges | ~$0.016-0.024 |
| **Total per game** | | | **~$0.05-0.06** |
| Full Flavor Tier 3 (opt-in) | Pre-EA | +160 routine calls | +$0.064 |

At 1000 games/month = ~$50-60. BYOK covers heavy users. All systems degrade gracefully to templates when LLM unavailable.

---

## Document References

- **STATUS.md** — Current test count, active work, blockers
- **COMPLETED.md** — Reference for done systems
- **TECHNICAL.md** — Code patterns, workflow, ports
- **AI_REFERENCE.md** — Enemy AI decision tree
- **VISION.md** — Core concept, north star

**Rule:** Phase numbers and timeline ONLY exist in this document. Other docs say "see ROADMAP.md".
