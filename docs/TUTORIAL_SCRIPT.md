# Ink & Iron: Tutorial Script

> **Living document. Updated every phase. Feeds the tutorial.**
> **Format: What the player needs to learn, and how to teach it.**
> **Last Updated:** September 23, 2026 (THE SCHOOL OF WAR REFRESH — three new
> cards: VII the Cabinet (diplomacy, through the REAL F1 wizard), IX the
> Marshalate (trust, glory, relationships, envy, reward) and XVI the Wooden
> Wall (the naval rule, taught honestly on a lesson with no fleet); the
> pushback/defiance explanation on cards IV/V; first-contact copy on I and
> XVII; and the lesson made UNBREAKABLE — a per-step Skip chip, a refused
> suggested order releases its step at once, the catch-up floor kept. Eighteen
> cards. Built Aug 8, 2026 at POSITION 7 on the authored Danube Lesson; see
> §The Danube Lesson below. The concept tables remain the teaching INVENTORY;
> the live script is `tutorial_overlay.gd` STEPS, mirrored by
> `backend/game_logic/tutorial_state.py` and driven headless by
> `tools/tutorial_overlay_harness.gd`.)
>
> **⚠ Staleness note (Aug 8 refresh):** the pre-cutover tables below were
> written against the legacy 19-region world (Feb 2026). Numbers corrected in
> place where they had drifted: admin-AP bonus 25g (was written 75g), plunder
> ×4 income (was 1.75×), fortify caps aggressive 8% / cautious 12%, THREE
> implemented personality types (balanced/loyal retired by MC-4). The legacy
> world survives only as the `SOVEREIGN_MAP=legacy` rollback fixture — the
> shipped tutorial runs on the real 1805 map.

---

## How This Document Works

Every time a feature is added, add an entry here. When Pre-EA tutorial content is built, this document IS the script. Each entry has:
- **Concept:** What the player needs to understand
- **Teach by:** How to introduce it (scripted event, tooltip, first encounter)
- **Phase added:** When this was built
- **Priority:** Must-know (blocks play), Should-know (improves play), Nice-to-know (depth)

### Update Policy

**Update this doc every phase, not in one big Pre-EA pass.** Adding 3-5 table rows when a feature ships takes 5 minutes. Deferring means reverse-engineering tutorial implications from code months later — entries get missed and nuances are forgotten. The developer who built the feature writes the best tutorial entry.

- Phase 7: Add coordination, adjacent support, reinforcement (Grouchy Rule) entries
- Phase 8: Add diplomacy chat, peace treaty, leader personality entries
- ~~Pre-EA: build `TutorialManager` + Short Waterloo Scenario~~ ✅ **DONE at
  Road-to-EA position 7 (Aug 8, 2026)** as "The School of War" on the Danube
  Lesson scenario — see that section below. New-feature rows still land here
  first; promoting one into the built tutorial means editing
  `tutorial_overlay.gd` STEPS + its two test files.

---

## Core Concepts (Phase 1-2)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Commands are typed, not clicked | First prompt: "Type an order for Ney, e.g. 'Ney, attack Wellington'" | Must-know |
| Marshals have names | Label marshals on map, first prompt names them | Must-know |
| Two AP pools: 4 combat + 2 admin per turn | AP counters visible: "4 military actions, 2 admin actions remaining" | Must-know |
| Combat AP: attack, move, scout, defend, drill, fortify, stance, garrison (2 AP) | Tooltip on first action: "Military orders cost combat AP" | Must-know |
| Admin AP: recruit, build, repair | Tooltip on first admin action: "Administration costs admin AP" | Must-know |
| Unused admin AP earns 25 gold each | End-of-turn summary shows admin bonus: "Saved 1 admin action: +25 gold" | Should-know |
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
| You command 4 French marshals | Campaign briefing: "Your marshals: Ney (72k, Belgium), Davout (48k, Paris), Grouchy (28k, Lyon), Drouot (25k, Paris)" | Must-know |
| Enemy has 4 marshals across 2 nations at war, plus neutral Austria (2) and Saxony (1) | Scout reveals: "Wellington (52k) at Waterloo. Uxbridge (24k) at Hanover. Blucher (40k) at Berlin. Gneisenau (32k) at Rhineland." | Must-know |
| 3 unit types: infantry, cavalry, artillery | Tooltip on each marshal shows unit type badge | Must-know |
| France controls 8 regions, Coalition controls 5, neutral 6 | Map shows controlled regions by color at start | Should-know |
| Ney is cavalry (2-tile range, can charge) | Tooltip on Ney: "CAVALRY — can attack enemies 2 regions away" | Should-know |
| Drouot is artillery (ranged bombardment) | Tooltip on Drouot: "ARTILLERY — cannot attack after moving" | Should-know |
| Davout is the best tactician (skill 10) | Tooltip on Davout: "Master tactician — strongest defensive modifiers" | Nice-to-know |

## Personality & Objections (Phase 2-3, V2a)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Marshals have personalities | Brief intro: "Ney is aggressive. Davout is cautious. Drouot is cautious. Grouchy follows orders exactly." | Must-know |
| Personality affects combat modifiers | Tooltip: "Ney gets +15% attack. Davout gets +20% defense when outnumbered." | Should-know |
| Personality-specific fortify caps | Tooltip: "Davout fortifies faster (max 12%). Ney's cap is lower (max 8%)." | Nice-to-know |
| Marshals can object to orders | Scripted: Ney objects to first defensive order on turn 2 | Must-know |
| Objections have severity levels (MILD to CRITICAL) | MILD concerns appear as "Field Dispatches" in turn log; MAJOR+ trigger popup | Should-know |
| Trust/Insist/Compromise choices | Objection popup explains each option with consequences | Must-know |
| Trust affects tone, not triggers | Tooltip: "High trust = respectful advice. Low trust = defiant refusal." | Should-know |
| Insist always works but costs trust | Popup shows: "Insist: -10 trust, marshal obeys" | Should-know |
| Compromise builds trust with partial resolution | Popup shows: "Compromise: +5 trust, modified order" | Should-know |
| Grouchy needs clear orders | First vague order to Grouchy triggers clarification popup | Should-know |
| 3 personality types exist | Help text: "Aggressive, Cautious, Literal — each has different triggers" (balanced/loyal retired by MC-4) | Nice-to-know |

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

## Artillery & Bombardment (Phase 6)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Artillery is the third unit type | Tooltip on Drouot: "ARTILLERY — ranged bombardment specialist" | Must-know |
| Artillery cannot attack after moving | Error: "Drouot's guns need time to set up — cannot attack this turn" | Must-know |
| Bombardment hits from adjacent region | "Drouot, bombard Wellington" — fires from one region away | Must-know |
| 2 bombardments per turn limit | Counter: "Bombardments: 1/2 remaining" (color-coded green/yellow/red) | Should-know |
| Bombardment does not capture regions | Tooltip: "Artillery doesn't advance — send infantry to take the ground" | Should-know |
| Terrain affects bombardment damage | Post-bombardment: "Plains +10%, Mountains -40%" | Should-know |
| Artillery degrades forts 2x faster | Post-bombardment: "Fortifications crumbling — 10% degraded" (vs 5% for infantry) | Should-know |
| Cavalry counters artillery (+30%) | Warning when cavalry attacks Drouot: "Cavalry overruns the guns!" | Should-know |
| Artillery gets -25% defense if it moved this turn | Tooltip: "Guns still unlimbering — defense reduced" | Nice-to-know |
| Artillery is exempt from exhaustion | Tooltip: "Sustained bombardment is artillery's function" | Nice-to-know |
| Bombardment streak tracks consecutive hits | After 2nd hit on same target: "Bombardment streak: 2 — zeroed in" | Nice-to-know |
| Berthier advises when forts crumble | Advisory: "Fortifications are crumbling. An infantry assault would have favorable odds." | Should-know |
| Collateral damage hits other forces in target region | Post-bombardment: "Collateral: Uxbridge took 480 casualties" | Should-know |
| Friendly fire possible with collateral | Warning (red): "FRIENDLY FIRE — allied marshal caught in bombardment!" Trust penalty. | Should-know |
| HOLD order auto-bombards for artillery | "Drouot, hold Belgium" — automatically bombards adjacent enemies each turn | Nice-to-know |
| PURSUE blocked for artillery | Error: "Artillery cannot pursue — use 'march to' instead" | Should-know |

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

### Manpower Pools (Phase 6)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Nation-level manpower reserves gate recruitment | HUD bar: "Inf: 80,000  Cav: 15,000  Art: 10,000" — depletes on recruit | Must-know |
| 3 pool types match unit types | Infantry pool for Davout/Grouchy, cavalry for Ney, artillery for Drouot | Must-know |
| Pools regenerate each turn | Economy report: "Infantry +5k/turn, Cavalry +500 base, Artillery +300 base" | Should-know |
| Cavalry regen boosted by plains regions | Each controlled plains region: +500 cavalry/turn | Should-know |
| Artillery regen boosted by urban regions | Each controlled urban region: +200 artillery/turn | Should-know |
| Stables building boosts cavalry regen | "Build stables in Paris" — +750 cavalry regen/turn | Should-know |
| Pool caps prevent hoarding | Caps: infantry 100k, cavalry 30k, artillery 20k | Nice-to-know |
| HUD color warns on low pools | Green → orange → red as pools deplete | Should-know |
| Recruit batch size varies by type | Infantry 10k, cavalry 5k, artillery 3k per recruit action | Should-know |
| Recruit cost varies by type | Infantry 200g, cavalry 300g, artillery 400g (before region discount) | Should-know |

### Recruitment

| Concept | Teach by | Priority |
|---------|----------|----------|
| Recruit adds troops based on marshal type | "Recruit for Ney" — 5k cavalry, costs 1 admin AP + 300g | Must-know |
| Recruit cost varies by region: capital 75%, stable 100%, settling 150% | Tooltip: "Recruit in Paris for a 25% discount" | Should-know |
| Green recruits have 40% morale (dilutes army) | Post-recruit: "Morale: 80% -> 66% (raw conscripts lower average)" | Should-know |
| Must control the region to recruit there | Error if recruiting in enemy territory | Must-know |
| Pool must have enough reserves | Error: "Insufficient cavalry reserves (need 5,000, have 2,000)" | Must-know |

### Buildings

| Concept | Teach by | Priority |
|---------|----------|----------|
| Build structures in regions you control | "'Build market in Paris' — costs admin AP + gold" | Should-know |
| 5 building types with different effects | Help text lists building types | Should-know |
| Supply Depot (300g, 2 turns): +10k BASE supply (delivered figure is terrain-scaled and ×1.5 fed — the build chip quotes the province's real delta, e.g. Paris +15,000), halves movement attrition nearby | Tooltip: "Depots project logistics to adjacent regions" | Should-know |
| Fortification (400g, 3 turns): defense bonus + contested capture holdout | Tooltip: "Fortified regions hold out even after army retreats" | Should-know |
| Training Ground (250g, 2 turns): recruits start at 70% morale | Tooltip: "Trained recruits barely dilute veteran armies" | Nice-to-know |
| Market (350g, 2 turns): +25% region income | Tooltip: "Paris market: 300g -> 375g/turn" | Should-know |
| Stables (300g, 2 turns): +750 cavalry regen/turn | Tooltip: "Stables breed warhorses for cavalry reinforcements" | Should-know |
| Building slots: capital 2, city/major_city 1, town/rural 0 | Error: "Rural regions cannot support buildings" | Should-know |
| Repair damaged buildings (1 admin AP + 150g) | "'Repair building in Paris' — restores damaged structure" | Should-know |
| Repair war damage (1 admin AP + 150g, -15% damage) | "'Repair Paris' — reduces war damage" | Should-know |

### Capture & Plunder

| Concept | Teach by | Priority |
|---------|----------|----------|
| Capturing enemy regions triggers choice: Plunder or Secure | Popup on first capture: "Plunder for gold or secure for stability?" | Must-know |
| Plunder: immediate gold (4x income, quoted live in the prompt), stability 10, heavy damage | "Plunder for +400 gold" — the modal quotes the real figure (IGR-E: shown = paid; a re-sack pays 0) | Should-know |
| Secure: stability 25, buildings damaged not destroyed | "Secure: no gold bonus, but region recovers faster" | Should-know |
| Fortified regions require occupation (hold for turns) | "Region fortified — must hold position to capture" | Should-know |

### Supply & Attrition

| Concept | Teach by | Priority |
|---------|----------|----------|
| Regions have supply capacity based on type; every screen shows the EFFECTIVE cap (×1.5 on own/allied soil — WO slice 8) | Region panel / tooltip: "Supply: 60,000" | Should-know |
| Excess troops cause supply attrition (continuous, up to 3% + 1%/extra corps stacking, 6% ceiling) | The muster preview quotes the real cost before you commit; the dispatch names it after | Must-know |
| Movement causes attrition (base 1%, terrain multiplied) | Post-move: "March losses: 720 troops (mountains 2x)" | Should-know |
| Moving through enemy fortification: +4% harassment | "Enemy fortification inflicts 4% harassment losses" | Should-know |
| Supply depots halve movement attrition nearby | "Forward supply lines reduce march losses" | Nice-to-know |
| Friendly stable regions: no supply attrition | "Home territory with stability 76+ has no supply drain" | Nice-to-know |

## Garrisons (Phase 6)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Capitals have built-in garrisons (15,000) | Map shows garrison shield below capital circle with strength | Must-know |
| Capital garrisons must be reduced below 5,000 before capture | Error: "Cannot capture — garrison still holds at 12,000" | Must-know |
| Capital garrisons regenerate +2,000/turn | Turn summary: "Paris garrison: 13,000 → 15,000 (max)" | Should-know |
| Capital garrison gets terrain + fort defense bonuses | Tooltip: "Garrison effective defense boosted by urban terrain and fortification" | Nice-to-know |
| Player can place garrison detachments | "'Davout, garrison' — detaches 3,000 troops to defend this region" (2 AP) | Should-know |
| Garrison command costs 2 AP | AP counter: "Garrison costs 2 military AP" | Should-know |
| Marshal needs 8,000+ troops to garrison | Error: "Insufficient strength to garrison (need 8,000)" | Should-know |
| Nation cap of 3 garrisons (includes capital) | Warning: "France already has 3 garrisons (cap reached)" | Should-know |
| Player garrisons fight to destruction | Tooltip: "Detachment garrisons don't collapse at 5,000 — they hold to the last man" | Nice-to-know |
| Player garrisons don't regenerate | Unlike capital garrisons, detachments don't heal over time | Nice-to-know |
| Map shows garrison shields | Colored shield below region with strength ("3k", "15k", dimmed under fog) | Should-know |

## Fog of War (Phase 6 — Fog)

| Concept | Teach by | Priority |
|---------|----------|----------|
| You don't see all enemies anymore | First turn: status shows "NO INTELLIGENCE" for distant regions | Must-know |
| 5 visibility levels: Full/Partial/Stale/Last Known/Unknown | Tooltip on first "no intelligence" region | Should-know |
| Scout reveals enemy positions and strength | "Scout Waterloo" gives FULL intel for 2 turns | Must-know |
| Adjacent regions show partial intel (name + band) | Map shows nearby enemies as "a substantial army" | Should-know |
| Intel decays over turns (exact -> band -> "last seen") | After 3 turns, status shows "[3 turns ago]" | Should-know |
| Attacking into fog is allowed (you learn the hard way) | First fog attack reveals enemy on contact | Should-know |
| PURSUE needs known/stale target location | Error if PURSUE target is UNKNOWN: "No intelligence on target" | Must-know |
| PURSUE into stale intel may find empty region | "Ney arrives at Waterloo but finds no sign of Wellington" | Should-know |
| Watchtower building provides permanent adjacent visibility | "Build watchtower in Belgium" — see nearby enemies without scouts | Should-know |
| Watchtower + scout synergy: 3 turns FULL instead of 2 | Tooltip: "Watchtower observation post keeps intel fresher" | Nice-to-know |
| Controllers (political) always visible, military intel varies | Region ownership shown regardless of fog | Should-know |

## UI & Information (Phase 6.5+)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Map hover shows region info | First mouse hover triggers tooltip: terrain, income, stability, buildings | Must-know |
| Campaign briefing shows status | Appears at turn start, explains what it shows | Should-know |
| Marshal report summarizes turn | End-of-turn summary, point out key events | Should-know |
| Enemy phase shows AI actions | Dialog after your turn: "Wellington fortifies. Blucher moves to Belgium." | Should-know |
| Save/Load exists | Menu accessible, autosave every turn | Must-know |

---

## Shipped Since February (teaching inventory — partly in the built tutorial since Sept 23, 2026)

> These systems SHIPPED (coalitions/multi-marshal July 2025-era phases;
> diplomacy Phase 8; jealousy/estates/naval/agendas 2026). The Danube Lesson
> taught the CORE LOOP only until the September 23, 2026 refresh, which
> promoted three rows into cards: **diplomacy** (VII — a real Cabinet mission,
> the DP cost stated, the D ledger and the mailbox named), **relationships /
> envy / reward expectation** (IX — the muster's WILL JOIN line, the G card,
> "two marshals at odds bring half their weight", envy dormant in the lesson
> and said so), and **naval** (XVI — the crossing rule, the crimson SHUT link,
> THE ADMIRALTY, blockade, expeditions — on a lesson that authors no fleet,
> and says so). The remaining rows stay the inventory for R159 screen lines
> and first-encounter hints. The Gazette row is CUT to post-EA (Aug-3
> re-plan) and kept only as provenance.

### Coalitions & Multi-Marshal (SHIPPED)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Coalition threat rises with conquest | Threat indicator visible, tooltip explains | Must-know |
| Multiple marshals can fight together | Coordination happens by standing together; the muster preview names the committed figure | Should-know |
| Relationships affect coordination | Battle report + Berthier observations after multi-marshal battle | Nice-to-know |

### Diplomacy (SHIPPED)

| Concept | Teach by | Priority |
|---------|----------|----------|
| You can treat with every court | F1 wizard + D ledger (R159 lines name both) | Must-know |
| Type proposals naturally | Example: "offer Austria peace" — or use the wizard's guided terms | Must-know |
| Courts have designs (agendas) | Ledger Design rows + war-room per-belligerent lines | Should-know |
| War score affects negotiation | War detail popup (R159 line: "its score, its fronts, and the price of peace") | Should-know |

### Marshals Deepened (SHIPPED — jealousy, estates, recruitment)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Glory breeds jealousy; the ladder ranks it | Generals screen LAURELS ladder + petition popups speak for themselves | Should-know |
| Success raises reward expectation (estates/rentes) | The Reward chip on every Generals card states its gate reason | Should-know |
| New marshals can be commissioned | Commission bench on the Generals screen (honest availability) | Nice-to-know |

### The Emperor (SHIPPED — row NP, August 15, 2026; FA-81 inventory)

> NOT in the built tutorial by design: the Danube Lesson is sovereign-free
> (`NAPOLEON_SPEC.md` §14.1 — the School teaches the marshal loop first).
> These rows are the inventory for the campaign's first-encounter hints and
> the README's YOUR MARSHALS block, which names him.

| Concept | Teach by | Priority |
|---------|----------|----------|
| Napoleon is a piece you command like a marshal ("Napoleon, march to Swabia") and he never objects | README YOUR MARSHALS "THE EMPEROR" entry; the Generals screen card | Must-know |
| The Presence: every corps fighting beside him fights harder, and the bonus dims as imperial grip slips | Battle report names the aura figure ("+9% — his star dims") | Must-know |
| The Peril is CAPTURE, not death: beaten with a road open, the Guard buys his escape every time (30% of his corps); with no road out you choose — fight to the last, or a breakout at even odds; taken, he is the captor's bargaining chip (authority collapses; every peace is priced with him in it) | The encirclement question + the Eagle-in-Chains outcome copy | Must-know |
| The Seat: seated at Paris he adds +1 diplomatic point a turn | Ledger DP line names the Seat | Should-know |
| His Guard (10,000) was carved from Soult's corps — the national total is unchanged | Generals screen strengths | Nice-to-know |

### Naval (SHIPPED — DEF-5 "The Wooden Wall")

| Concept | Teach by | Priority |
|---------|----------|----------|
| A hostile fleet shuts a crossing | Crimson SHUT link + the march refusal states the remedy | Must-know |
| Expeditions land small corps (≤15,000) | THE ADMIRALTY ledger tab: gate terms + landing chips quote the odds (NV-12) | Should-know |
| Blockade strangles trade + war-weariness | Blockade Board rows + signed ledger components | Should-know |

---

## The Danube Lesson (BUILT — POSITION 7, August 8, 2026)

**The shipped tutorial.** "The School of War" — Berthier's non-modal tutor
card (`tutorial_overlay.gd`, CanvasLayer 90) on the authored scenario
`tutorial_1805.json` (the real 126-province 1805 map; France + Bavaria
ALLIANCE vs Austria only; naval/agendas/commissioning dormant by authoring;
Austria PEACE-walled so the front is one-way). Launched from the main menu
("The School of War — a guided campaign", confirm-guarded) via
`POST /new_game {"scenario": "tutorial"}`. The client arms on
`game_state.scenario_name == "tutorial"`; steps resume by turn on reload;
skip/completion latches per-machine (`UiSettings.tutorial done`).

**The live script IS the `STEPS` table in `tutorial_overlay.gd`** — this
section mirrors it for design review. Every precondition below is pinned as
arithmetic in `tests/test_tutorial_scenario.py`; every suggested command is
mock-parse-verified against the tutorial roster in
`tests/test_tutorial_position7.py` (T-B1).

| Turn | Beat | Suggested command | The real system that answers |
|------|------|-------------------|------------------------------|
| 1 | The situation + free actions | `economy` | Free treasury report; boot charges 0 (treasury 900 under the EB-1 floor) |
| 1 | First march + AP pools | `Senarmont, move to Munich` | Allied ALLIANCE transit; artillery `moved_this_turn` foreshadows T4 |
| 1 | Close the day | `end turn` | Enemy phase + morning dispatch |
| 2 | The marshal's temper | `Ney, defend` | REAL aggressive objection at STRONG (24k vs PARTIAL-midpoint 10k = 2.4; popup survives mood variance). Never `hold` (strategic, evaluates NONE) or `fortify` (2 AP + immobilizes) |
| 2 | Trust/Insist/Compromise | *(the modal's own buttons)* | ⚠ The command line is DISABLED while the objection modal is up, so this is NOT a typed answer on the shipped client — the buttons read Trust… / Proceed as Ordered / Compromise… (built at runtime with the marshal's name and the trust figures). The W6-0 typed router still exists and is what a headless driver uses. **Trust branch = Ney attacks on T2 and card VII pivots to what the board actually shows** (FA-42: four arms — stands / running / lost / taken) |
| 2 | The guns speak | `Senarmont, bombard Jellacic` | Munich→Tyrol adjacent; moved-T1 so the moved-this-turn refusal cannot fire; then clear Swabia. (PC15-9 moved this gate 3→2, which is why it precedes First Blood) |
| 3 | **The Cabinet** (Sept 23, 2026) | *(chip: `Open the Cabinet on Austria ▸` → the REAL F1 wizard via `open_cabinet`; no typed chip — ruling G1 redirects typed diplomatic verbs)* | Gather intelligence on Austria: the wizard's own `gather intel on Austria` stages the `mission` confirm dialogue; "Begin mission" makes it live and the base response's `talleyrand_mission_summary` turns from the sentinel `"None"` to `Gather Intelligence → Austria` — that is the card's predicate (`_pred_mission_started`). 1 DP/turn of the lesson's 5. The driver scripts issue the same sentence on loop 3 under the new `missions: begin` dial |
| 4 | First blood | `Ney, attack Kienmayer` | Battle on allied Bavarian soil (PT-F1: no capture modal) — pure combat lesson. ⚠ "Kienmayer has no friendly exit (breaks in place or dies)" is FALSE and was measured so: forced retreat does not consult `can_enter_territory`, and he breaks onto French soil and survives in roughly half of trust runs. That is why card VIII branches |
| 5 | **The Marshalate** (Sept 23, 2026; gate 5 — FA-42 forbids a second gate-4 card, so it shows as "waiting" from the moment VIII completes) | *(none — a self-releasing card, `_pred_turn_gte_5`)* | The muster's WILL JOIN / WILL NOT line; the G card (trust, glory, skills, relationships); "Ney and Soult are at odds — two marshals at odds bring half their weight" (the authored −1 pair, `_pair_contribution_scale`); the glory ladder and envy — DORMANT in the lesson (`jealousy_dormant`) and the card says so; the Reward chip and reward expectation. A turn-gated card by design: it reads no event, so it can never wedge |
| 5 | Standing orders | `Davout, march to Franconia` | 2-hop auto-upgrade to strategic MOVE_TO at 2 AP (literal Soult pays 1 — the card contrasts) |
| 6 | Conquest | `Davout, move to Bohemia` | Battle-win capture → Plunder/Secure modal (typed answers work; no estate stage — no enemy `dotation_regions`); fallback `Ney, move to Tyrol` = PF-3 move-capture, same modal. Capitals lesson: Munich 10,000 / Vienna 25,000 on screen |
| 6 | The conqueror's choice | *(the modal's own buttons)* | Same as beat V: the capture modal disables the command line, so the shipped answer is the PLUNDER / SECURE button, not a typed token. `plunder` (×4 income, quoted live) vs `secure` — the card counsels SECURE on an allied front |
| 7 | The depots | `Soult, recruit troops` | 450g at Paris (200 × 0.75 capital × 3 war; admin-7 neutral Intendance — pinned); second admin action: `build watchtower in Lorraine` |
| 8+ | The fog | `Davout, scout Bohemia` | Austria's main body is ALREADY on you — see the FA-63 note below; the fog lesson is where it has gone, not whether it is coming |
| 9+ | The counter-blow | `Ney, fortify` | Mountains + earthworks + garrison vs the Vienna pair (~50k, cautious) — by this turn they have been in contact for six turns. Now also names supply: a province feeds only so many, and the region panel states the limit |
| 10+ | **The Wooden Wall** (Sept 23, 2026) | *(none — self-releasing, `_pred_turn_gte_11`)* | The naval rule taught, not staged: the lesson authors no `navies` (an Admiralty bill would bankrupt the 900-gold treasury), and the card SAYS there is no fleet in this lesson. Names the Royal Navy's Channel, the crimson SHUT link, THE ADMIRALTY (T, then 7), `build ships`, blockade + the Continental System, expeditions, the Grand Diversion, and where Britain lands (Normandy, Lisbon) |

> **FA-63 (Sept 11, 2026) — the reserve's timing, measured.** The scenario
> file's original `_comment` and this table's rows XII/XIII claimed that
> starting Archduke Charles at Hungary "delays the combined-strength attack
> into the designed turn-8+ free-play window". **It does not, and never did.**
> Driven through the real `/command` surface with the lesson's own T1 order
> (Senarmont to Munich): Charles marches Hungary → Tyrol in the turn-1 enemy
> phase and **attacks Senarmont at Munich in the turn-2 enemy phase**; the
> combined Charles + Schwarzenberg + Kienmayer assault lands **on turn 3**,
> before "First blood" (beat IV, turn 4) has been taught. Both filed
> mechanical remedies were measured and rejected: starting Charles one
> province further east buys at most ONE turn (he covers Hungary → Tyrol in
> one phase), and an authored `fortified: true` on the pair is stripped by
> the enemy AI inside turn 1 (three unfortify rungs) — measured inert. So the
> copy was corrected to what the engine does (card XIII no longer says the
> pair "will come west"), and `tests/test_fa_slice17_0_the_remnant_holds_no_ground_2026_09_11.py`
> pins the turn-2 first contact so the claim can never drift back.
| 10+ | The instruments | *(hotkeys)* | T / G / D / R — the R159 lines name each screen's mechanic. **HC-5:** step XIV also names THE ADMIRALTY (ledger book 7), the F1 wizard + its Formable Nations button, the Generals card's Reward chip, and the ledger's Design rows — honest pointers, no new lessons (the R159 self-teaching screens carry the depth) |
| 10+ | The instruments — the Cabinet (**IQ-4**, "The Cabinet Is Visible") | *(none)* | Step XIV now counts **Five** instruments: the fifth is Talleyrand's missions, sent from **F1** (warm a court, reassure an ally, spy, or pry two allies apart) — they cost diplomatic points every turn they run and stand in the Strategic Ledger's Orders book (the THE CABINET block, with a free Recall link) and on the notice rail until done. The card quotes **no figures** (a `.gd` constant cannot quote an applied number; the help text's missions block carries the live ones) and there is **no chip**: typed mission verbs are caught by the Cabinet redirect (`main.gd` `_redirect_diplomatic_command`), so a chip would teach a dead route |
| 12 | The lesson ends | *(Conclude chip)* | Hand-off card → main menu BEGIN; Europe worlds never hard-end (sandbox), so the school closes itself |

> **Card numbering after the refresh (18):** I Situation · II Marches · III
> Day Closes · IV Temper (pushback) · V Trust/Insist/Compromise (trust,
> defiance) · VI Guns · **VII Cabinet** · VIII First Blood · **IX Marshalate**
> · X Standing Orders · XI Conquest · XII Conqueror's Choice · XIII Depots ·
> XIV Fog · XV Counter-Blow · **XVI Wooden Wall** · XVII Instruments (now
> also L, N, Alt+key, the notice rail, Esc) · XVIII Lesson Ends. Card I now
> teaches Tab completion, province-click chips and the three first-contact
> doors (`what can I do` / `status` / `help`).

**Design rules (pinned):** the tutorial steers the player into REAL system
responses — nothing is faked; the overlay is observe-only (never routes,
never sends — main.gd tells it what was SENT via `note_sent`, and the
Cabinet chip asks main.gd to open the real wizard via `open_cabinet`); every
beat tolerates its fallback branch; **the lesson is unbreakable** — a
refusal of the card's OWN suggested order releases the step at once with
the reason on the next card, every card but the last carries a `Skip this
lesson` chip, and the turn-gate catch-up (gate + 2) stays as the floor
(`tests/test_tutorial_unbreakable_2026_09_23.py` drives the real overlay
over real responses: the idle Emperor, the refused order, the chips, the
Cabinet lesson, and the committed lesson script end to end); GR6 absolute
(zero mechanics changes; `scenario_name` is display-only).

---

## Update Instructions

When adding a feature, add one line to the appropriate section:
```
| [What player needs to know] | [How to teach it] | [Must/Should/Nice] |
```
