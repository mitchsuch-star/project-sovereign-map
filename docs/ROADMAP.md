# Ink & Iron: Master Roadmap

> **THE source of truth for all phases and timeline.**  
> **Other docs reference this — phase numbers only exist here.**  
> **Last Updated:** January 30, 2026

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
| EA | 1805 Campaign Launch | 🎯 November 2025 |

---

## Completed Phases ✅

| Phase | Name | Tests | Key Features |
|-------|------|-------|--------------|
| 1 | Foundation | ~80 | Core loop, actions, regions, marshals |
| 2 | Combat & AI | ~90 | Dice combat, enemy AI, stances, drill/fortify |
| 3 | Relationships | ~30 | Marshal relationships, historical values |
| 4 | LLM Integration | ~60 | Parsing, personality responses, BYOK |
| 5.1 | Tactical Feedback | 64 | Word-based scoring, strategic feedback |
| 5.2 | Strategic Commands | ~350 | MOVE_TO, PURSUE, HOLD, SUPPORT, interrupts, modding |
| 5.3 | Enemy AI Fixes | ~15 | Stagnation counter, oscillation fixes, consolidation |

**Total Tests:** 950+ (verify in STATUS.md)

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
| **AI Diplomatic Personality** | Metternich vs Tsar Alexander feel different | Medium | 📋 |
| **AI Proposals** | AI offers peace, makes demands | Medium | 📋 |

**Dependencies:** Phase 6 (economy for peace terms)  
**Exit Criteria:** Can negotiate peace, coalitions form, AI diplomacy feels alive

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

**Dependencies:** Phase 8 (diplomacy for event outcomes)  
**Exit Criteria:** Each campaign tells a story, nations play differently

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
| **Music & Sound** | Period orchestral, battle sounds, atmosphere | Medium | 📋 HIGH |
| Difficulty Settings | AI bonuses, player handicaps | Low | 📋 |

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
7. 📋 Phase 8: Diplomacy, **Coalitions** ← CRITICAL
8. 📋 Phase 8.5: **Events, National Goals, Flavor** ← Makes it a GAME
9. 📋 Phase 9: Advisors
10. 📋 Phase 10: Marshal death/recruitment
11. 📋 Phase 11: Vassals, Naval
12. 📋 Phase 12: Communication cutoff
13. 📋 Pre-EA: Save/Load, Tutorial, Voice, **LLM Monetization**, **Music**
14. 📋 **1805 Map UI** ← LARGEST SINGLE TASK
15. 📋 Steam Integration
16. 🎯 **November 2025: Early Access**

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
| **Early Access** | **November 2025** | |

---

## Document References

- **STATUS.md** — Current test count, active work, blockers
- **COMPLETED.md** — Reference for done systems
- **TECHNICAL.md** — Code patterns, workflow, ports
- **AI_REFERENCE.md** — Enemy AI decision tree
- **VISION.md** — Core concept, north star

**Rule:** Phase numbers and timeline ONLY exist in this document. Other docs say "see ROADMAP.md".
