# Ink & Iron: Tutorial Script

> **Living document. Updated every phase. Feeds the Pre-EA tutorial.**
> **Format: What the player needs to learn, and how to teach it.**
> **Last Updated:** February 5, 2026 (Session 4)

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
| Actions cost AP (4/turn) | AP counter visible, "You have 4 actions remaining" | Must-know |
| Move to adjacent regions | "Ney, move to Belgium" as first order suggestion | Must-know |
| Attack requires enemy in range | Error message if no valid target, suggest alternatives | Must-know |
| Combat uses strength + modifiers | Post-battle analysis shows breakdown (Phase 6) | Should-know |
| Stances affect combat | Tooltip after first battle: "Try changing stance with 'Ney, aggressive stance'" | Should-know |
| Drill gives shock bonus | Tooltip after 3 turns: "Drilling troops gives a one-time attack bonus" | Nice-to-know |
| Fortify gives defense bonus | Suggest when enemy approaches: "Consider 'Davout, fortify'" | Should-know |
| End turn advances game | "Type 'end turn' when done" | Must-know |

## Personality & Objections (Phase 2-3, V2a)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Marshals have personalities | Brief intro: "Ney is aggressive. Davout is cautious. Grouchy follows orders exactly." | Must-know |
| Marshals can object to orders | Scripted: Ney objects to first defensive order on turn 2 | Must-know |
| Trust/Insist/Compromise choices | Objection popup explains each option with consequences | Must-know |
| Trust affects tone, not triggers | Tooltip: "High trust = respectful advice. Low trust = defiant refusal." | Should-know |
| Grouchy needs clear orders | First vague order to Grouchy triggers clarification popup | Should-know |

## Strategic Commands (Phase 5.2)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Multi-turn orders exist | After 3 tactical moves: "Try 'Ney, march to Belgium' for a standing order" | Should-know |
| MOVE_TO, PURSUE, HOLD, SUPPORT | Help text lists strategic commands with examples | Should-know |
| Cannon fire interrupts | First time it triggers, explain what happened | Nice-to-know |
| Cancel strategic orders | "Say 'Ney, halt' to cancel a standing order" | Should-know |

## Economy & Campaign (Phase 6)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Regions produce income | Economy panel visible from turn 1 | Should-know |
| Troops have upkeep | Warning when treasury low | Must-know |
| Recruiting costs gold + manpower | Tooltip on recruit action | Should-know |
| Terrain affects combat | Region tooltip shows terrain type and modifier | Should-know |
| Fog of war hides enemies | "Scout to reveal enemy positions" | Should-know |
| Save/Load exists | Menu accessible, autosave every turn | Must-know |

## UI & Information (Phase 6.5)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Campaign briefing shows status | Appears at turn start, explains what it shows | Should-know |
| Marshal report summarizes turn | End-of-turn summary, point out key events | Should-know |
| Strategic ledger shows everything | Tooltip: "Press L to see all marshals and armies" | Should-know |
| Map hover shows province info | First mouse hover triggers tooltip explanation | Must-know |

## Coalitions & Multi-Marshal (Phase 7)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Coalition threat rises with conquest | Threat indicator visible, tooltip explains | Must-know |
| Multiple marshals can fight together | First time two marshals in same region, explain | Should-know |
| Relationships affect coordination | Tooltip after multi-marshal battle | Nice-to-know |

## Diplomacy (Phase 8)

| Concept | Teach by | Priority |
|---------|----------|----------|
| You can talk to nation leaders | First diplomatic contact triggered by event | Must-know |
| Type proposals naturally | Example: "I offer Austria peace if they cede Tyrol" | Must-know |
| Leaders have personalities | Brief intro when first meeting each leader | Should-know |
| War score affects negotiation | Tooltip on diplomatic screen | Should-know |

## Events & Narrative (Phase 8.5)

| Concept | Teach by | Priority |
|---------|----------|----------|
| Gazette summarizes events | First gazette appears, explain what it is | Nice-to-know |
| Creative commands earn bonuses | After 5 turns, tooltip: "Try creative phrasing for bonuses" | Nice-to-know |
| Marshals remember past events | First time it triggers, let it speak for itself | Nice-to-know |

---

## Short Waterloo Scenario (Pre-EA)

10-15 turn guided scenario using current 13-region map data. Teaches:
1. Turn 1: Issue first order (move)
2. Turn 2: Ney objects (scripted) — learn Trust/Insist/Compromise
3. Turn 3: Attack enemy — learn combat
4. Turn 4: Strategic command — learn multi-turn orders
5. Turn 5-10: Play freely with gentle tooltips
6. Win/lose condition: take Waterloo or lose all marshals

---

## Update Instructions

When adding a feature, add one line to the appropriate section:
```
| [What player needs to know] | [How to teach it] | [Must/Should/Nice] |
```
