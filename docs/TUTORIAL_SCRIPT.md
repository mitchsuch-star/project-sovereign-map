# Ink & Iron: Tutorial Script

> **Living document. Updated every phase. Feeds the Pre-EA tutorial.**
> **Format: What the player needs to learn, and how to teach it.**
> **Last Updated:** February 10, 2026 (Session 26)

---

## How This Document Works

Every time a feature is added, add an entry here. When Pre-EA tutorial content is built, this document IS the script. Each entry has:
- **Concept:** What the player needs to understand
- **Teach by:** How to introduce it (scripted event, tooltip, first encounter)
- **Phase added:** When this was built
- **Priority:** Must-know (blocks play), Should-know (improves play), Nice-to-know (depth)

---

## Core Concepts (Phase 1-2)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Commands are typed, not clicked | First prompt: "Type an order for Ney, e.g. 'Ney, attack Wellington'" | Must-know |
| Marshals have names | Label marshals on map, first prompt names them | Must-know |
| Two AP pools: 4 combat + 2 admin per turn | AP counters visible: "4 military actions, 2 admin actions remaining" | Must-know |
| Combat AP: attack, move, scout, defend, drill, fortify, stance | Tooltip on first action: "Military orders cost combat AP" | Must-know |
| Admin AP: recruit, build, repair | Tooltip on first admin action: "Administration costs admin AP" | Must-know |
| Unused admin AP earns 75 gold each | End-of-turn summary shows admin bonus: "Saved 1 admin action: +75 gold" | Should-know |
| Move to adjacent regions | "Ney, move to Belgium" as first order suggestion | Must-know |
| Attack requires enemy in range | Error message if no valid target, suggest alternatives | Must-know |
| Combat uses strength + modifiers | Post-battle analysis shows breakdown | Should-know |
| Stances affect combat (aggressive/defensive/neutral) | Tooltip after first battle: "Try changing stance with 'Ney, aggressive stance'" | Should-know |
| Drill gives one-time shock attack bonus | Tooltip after 3 turns: "Drilling troops gives a one-time attack bonus" | Nice-to-know |
| Fortify gives defense bonus (stacks per turn) | Suggest when enemy approaches: "Consider 'Davout, fortify'" | Should-know |
| Unfortify to abandon defensive position | Mention when player needs to move a fortified marshal | Nice-to-know |
| End turn advances game | "Type 'end turn' when done" | Must-know |
| Free commands: economy, help | "Type 'economy' to check your treasury (costs no AP)" | Should-know |

## Starting Forces

| Concept | Teach by | Priority |
|---------|----------|----------|
| You command 3 French marshals | Campaign briefing: "Your marshals: Ney (72,000, Belgium), Davout (48,000, Paris), Grouchy (33,000, Waterloo)" | Must-know |
| Enemy has 4 marshals across 2 nations | Scout reveals: "Wellington (68k) and Uxbridge (18k) at Waterloo. Blucher (55k) and Gneisenau (45k) in Netherlands." | Must-know |
| France controls 6 regions, Coalition controls 7 | Map shows controlled regions by color at start | Should-know |
| Ney is cavalry (2-tile range, can charge) | Tooltip on Ney: "Cavalry commander — can attack enemies 2 regions away" | Should-know |
| Davout is the best tactician (skill 10) | Tooltip on Davout: "Master tactician — strongest defensive modifiers" | Nice-to-know |

## Personality & Objections (Phase 2-3, V2a)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Marshals have personalities | Brief intro: "Ney is aggressive. Davout is cautious. Grouchy follows orders exactly." | Must-know |
| Personality affects combat modifiers | Tooltip: "Ney gets +15% attack. Davout gets +20% defense when outnumbered." | Should-know |
| Personality-specific fortify caps | Tooltip: "Davout fortifies faster (max 20%). Ney's cap is lower (max 10%)." | Nice-to-know |
| Marshals can object to orders | Scripted: Ney objects to first defensive order on turn 2 | Must-know |
| Objections have severity levels (MILD to CRITICAL) | MILD concerns appear as "Field Dispatches" in turn log; MAJOR+ trigger popup | Should-know |
| Trust/Insist/Compromise choices | Objection popup explains each option with consequences | Must-know |
| Trust affects tone, not triggers | Tooltip: "High trust = respectful advice. Low trust = defiant refusal." | Should-know |
| Insist always works but costs trust | Popup shows: "Insist: -10 trust, marshal obeys" | Should-know |
| Compromise builds trust with partial resolution | Popup shows: "Compromise: +5 trust, modified order" | Should-know |
| Grouchy needs clear orders | First vague order to Grouchy triggers clarification popup | Should-know |
| 5 personality types exist | Help text: "Aggressive, Cautious, Literal, Balanced, Loyal — each has different triggers" | Nice-to-know |

## Cavalry & Charges (Phase 4)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Cavalry marshals can attack 2 regions away | Tooltip on Ney: "Cavalry range: 2 tiles instead of 1" | Should-know |
| Aggressive attacks build recklessness | After Ney attacks: "Recklessness: 1/3. At 3, a glorious charge triggers!" | Should-know |
| Glorious charge at recklessness 3 (player choice) | Popup: "Ney's cavalry is surging! Order a glorious charge?" | Must-know |
| Auto-charge at recklessness 4+ (no choice) | Warning: "Recklessness too high — Ney charges without orders!" | Should-know |
| Terrain blocks charges (forest, mountains, urban) | If charge blocked: "Terrain prevents cavalry charge. Normal attack instead." | Should-know |
| Charge redirect to alternative target | If primary target on bad terrain but alternative exists, popup offers redirect | Nice-to-know |
| Restrain resets recklessness | Tooltip: "'Ney, restrain' resets recklessness to 0" | Should-know |

## Strategic Commands (Phase 5.2)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Multi-turn standing orders exist | After 3 tactical moves: "Try 'Ney, march to Belgium' for a standing order" | Should-know |
| Strategic costs 2 AP (vs 1 AP tactical) | AP counter shows: "Strategic order: 2 AP" | Should-know |
| MOVE_TO: march to distant region over turns | "Ney, march to Vienna" — auto-moves each turn along best path | Should-know |
| PURSUE: chase a specific enemy marshal | "Ney, pursue Blucher" — follows target until caught | Should-know |
| HOLD: defend a position for N turns | "Davout, hold Paris for 5 turns" — auto-fortifies (Davout bonus) | Should-know |
| SUPPORT: follow and assist another marshal | "Grouchy, support Ney" — follows ally, joins their battles | Should-know |
| Cannon fire/enemy contact interrupts orders | First time it triggers, explain what happened | Nice-to-know |
| Cancel strategic orders | "Say 'Ney, halt' to cancel a standing order" (costs 1 AP) | Should-know |
| Weighted pathfinding avoids bad terrain | MOVE_TO/HOLD routes avoid mountains when possible | Nice-to-know |

## Terrain (Phase 6.1)

| Concept | Teach by | Priority |
|---------|----------|----------|
| 6 terrain types affect combat and movement | Region tooltip shows terrain type on hover | Must-know |
| Plains: no bonus, cavalry thrives | Default terrain, best for cavalry charges | Should-know |
| Forest: +10% defense, blocks cavalry charges | Tooltip: "Forest slows movement and blocks charges" | Should-know |
| Hills: +15% defense, reduced cavalry power | Tooltip: "Hills favor defenders" | Should-know |
| Mountains: +25% defense, 2x move cost, blocks charges | Tooltip: "Mountains are deadly to attack into" | Should-know |
| Urban: +20% defense, good supply | Tooltip: "Cities are hard to assault but well-supplied" | Should-know |
| River crossing: +15% defense, 1.5x move cost | Tooltip: "River crossings slow armies and favor defenders" | Should-know |
| Scout shows terrain and defense bonus | Scout result: "Waterloo: Hills (+15% defense)" | Should-know |

## Economy (Phase 6.2)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Regions produce income based on type | Economy panel: "Capital: 300g, Major City: 200g, City: 150g, Town: 100g, Rural: 50g" | Must-know |
| France starts with 600 gold | Starting treasury shown in economy panel | Must-know |
| Troops cost upkeep each turn | Turn summary: "Upkeep: 765 gold (5 gold per 1,000 troops per marshal)" | Must-know |
| Type 'economy' to see financial summary | Tooltip: "Free action — check treasury, income, upkeep anytime" | Should-know |
| Turn summary shows financial report | End-of-turn: "Income: 850g, Upkeep: 765g, Net: +85g, Treasury: 685g" | Should-know |
| Bankruptcy triggers after gold goes negative | Warning: "Treasury depleted! Turn 1: upkeep halved. Turn 3+: troops desert (5%/turn)" | Must-know |

### Stability & War Damage

| Concept | Teach by | Priority |
|---------|----------|----------|
| Regions have stability (0-100) affecting income | Region tooltip: "Stability: Settling (60) — 75% income" | Should-know |
| 4 stability tiers: Hostile/Unrest/Settling/Stable | Tooltip: "Hostile (0-25): 0% income. Stable (76+): full income" | Should-know |
| Stability grows +5/turn, +5 more with garrison | Tooltip: "Station a marshal to speed up pacification" | Should-know |
| Battles cause war damage (reduces income) | Post-battle: "War damage: +10% (major battle: +20%). Recovers 2%/turn" | Should-know |
| Recruiting blocked in low-stability regions | Error: "Cannot recruit — stability 45 (need 51+)" | Must-know |

### Recruitment

| Concept | Teach by | Priority |
|---------|----------|----------|
| Recruit adds 10,000 troops to nearest marshal | "Recruit for Ney" — costs 1 admin AP + gold | Must-know |
| Recruit cost varies: capital 150g, stable 200g, settling 300g | Tooltip: "Recruit in Paris for a 25% discount" | Should-know |
| Green recruits have 40% morale (dilutes army) | Post-recruit: "Morale: 80% -> 66% (raw conscripts lower average)" | Should-know |
| Must control the region to recruit there | Error if recruiting in enemy territory | Must-know |

### Buildings

| Concept | Teach by | Priority |
|---------|----------|----------|
| Build structures in regions you control | "'Build market in Paris' — costs admin AP + gold" | Should-know |
| 4 building types with different effects | Help text lists building types | Should-know |
| Supply Depot (300g, 2 turns): +10k supply, halves movement attrition nearby | Tooltip: "Depots project logistics to adjacent regions" | Should-know |
| Fortification (400g, 3 turns): defense bonus + contested capture holdout | Tooltip: "Fortified regions hold out even after army retreats" | Should-know |
| Training Ground (250g, 2 turns): recruits start at 70% morale | Tooltip: "Trained recruits barely dilute veteran armies" | Nice-to-know |
| Market (350g, 2 turns): +25% region income | Tooltip: "Paris market: 300g -> 375g/turn" | Should-know |
| Building slots: capital 2, city/major_city 1, town/rural 0 | Error: "Rural regions cannot support buildings" | Should-know |
| Repair damaged buildings (1 admin AP + 150g) | "'Repair building in Paris' — restores damaged structure" | Should-know |
| Repair war damage (1 admin AP + 150g, -15% damage) | "'Repair Paris' — reduces war damage" | Should-know |

### Capture & Plunder

| Concept | Teach by | Priority |
|---------|----------|----------|
| Capturing enemy regions triggers choice: Plunder or Secure | Popup on first capture: "Plunder for gold or secure for stability?" | Must-know |
| Plunder: immediate gold (1.75x income), stability 10, heavy damage | "Plunder: 525 gold now, but region devastated (buildings destroyed)" | Should-know |
| Secure: stability 25, buildings damaged not destroyed | "Secure: no gold bonus, but region recovers faster" | Should-know |
| Fortified regions require occupation (hold for turns) | "Region fortified — must hold position to capture" | Should-know |

### Supply & Attrition

| Concept | Teach by | Priority |
|---------|----------|----------|
| Regions have supply capacity based on type | Region tooltip: "Supply: 32,000 / 50,000" | Should-know |
| Excess troops cause supply attrition (1%/3%/5% tiers) | Warning: "Army exceeds supply! 3% attrition this turn" | Must-know |
| Movement causes attrition (base 1%, terrain multiplied) | Post-move: "March losses: 720 troops (mountains 2x)" | Should-know |
| Moving through enemy fortification: +4% harassment | "Enemy fortification inflicts 4% harassment losses" | Should-know |
| Supply depots halve movement attrition nearby | "Forward supply lines reduce march losses" | Nice-to-know |
| Friendly stable regions: no supply attrition | "Home territory with stability 76+ has no supply drain" | Nice-to-know |

## UI & Information (Phase 6.5+)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Map hover shows region info | First mouse hover triggers tooltip: terrain, income, stability, buildings | Must-know |
| Campaign briefing shows status | Appears at turn start, explains what it shows | Should-know |
| Marshal report summarizes turn | End-of-turn summary, point out key events | Should-know |
| Enemy phase shows AI actions | Dialog after your turn: "Wellington fortifies. Blucher moves to Belgium." | Should-know |
| Save/Load exists | Menu accessible, autosave every turn | Must-know |

---

## Future Phases (NOT YET IMPLEMENTED)

> The following sections describe planned features. They are included for tutorial planning purposes but **no code exists yet**.

### Coalitions & Multi-Marshal (Phase 7 — Planned)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Coalition threat rises with conquest | Threat indicator visible, tooltip explains | Must-know |
| Multiple marshals can fight together | First time two marshals in same region, explain | Should-know |
| Relationships affect coordination | Tooltip after multi-marshal battle | Nice-to-know |

### Diplomacy (Phase 8 — Planned)

| Concept | Teach by | Priority |
|---------|----------|----------|
| You can talk to nation leaders | First diplomatic contact triggered by event | Must-know |
| Type proposals naturally | Example: "I offer Austria peace if they cede Tyrol" | Must-know |
| Leaders have personalities | Brief intro when first meeting each leader | Should-know |
| War score affects negotiation | Tooltip on diplomatic screen | Should-know |

### Events & Narrative (Phase 8.5 — Planned)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Gazette summarizes events | First gazette appears, explain what it is | Nice-to-know |
| Creative commands earn bonuses | After 5 turns, tooltip: "Try creative phrasing for bonuses" | Nice-to-know |
| Marshals remember past events | First time it triggers, let it speak for itself | Nice-to-know |

---

## Short Waterloo Scenario (Pre-EA)

10-15 turn guided scenario using current 13-region map. 40-turn max game. Teaches:
1. Turn 1: Issue first order (move). Introduce 2 AP pools (4 combat, 2 admin). Type 'economy' to see treasury.
2. Turn 2: Ney objects (scripted) — learn Trust/Insist/Compromise. See MILD "Field Dispatches" in log.
3. Turn 3: Attack enemy — learn combat, terrain bonuses, post-battle damage.
4. Turn 4: Strategic command — learn multi-turn orders (MOVE_TO). See AP cost difference (2 vs 1).
5. Turn 5: Capture a region — learn Plunder/Secure choice. Check economy impact.
6. Turn 6: Recruit troops, build a market — learn admin AP. See morale dilution from recruits.
7. Turn 7-10: Play freely with gentle tooltips (cavalry charges, supply, fortification).
8. Win/lose condition: take Waterloo or lose all marshals.

### Starting Map Reference

**French (Player):** Paris (capital, urban, 300g), Belgium (town, plains, 100g), Lyon (major_city, hills, 200g), Brittany (rural, forest, 50g), Bordeaux (rural, plains, 50g), Marseille (city, plains, 150g). Starting gold: 600.

**British:** Netherlands (rural, plains, 50g), Waterloo (rural, hills, 50g), Milan (city, urban, 150g), Geneva (town, mountains, 100g). Starting gold: 1,500.

**Prussian:** Rhine (town, river_crossing, 100g), Bavaria (town, hills, 100g), Vienna (major_city, urban, 200g). Starting gold: 800.

---

## Update Instructions

When adding a feature, add one line to the appropriate section:
```
| [What player needs to know] | [How to teach it] | [Must/Should/Nice] |
```
