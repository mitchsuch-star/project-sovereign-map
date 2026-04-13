# Reliability + Commitments Spec — Creative Review Prompt

> **Purpose:** Paste this into a fresh Claude session with no prior project context. Attach the spec file and supporting docs as described below.

---

## Attachments to include

1. `docs/RELIABILITY_COMMITMENTS_SPEC.md` (the spec under review)
2. `docs/RELIABILITY_IMPLEMENTATION_PLAN.md` (the implementation breakdown)
3. `docs/DIPLOMACY_SPEC.md` (the existing diplomacy system it builds on)
4. `docs/COALITION_SPEC.md` (coalition system it must coexist with)

---

## Prompt

You are a game designer reviewing a diplomacy spec for a Napoleonic strategy game called **Ink & Iron**. You have NO prior involvement with this project. You owe nothing to the spec's author. Your job is to find what's wrong, what's missing, and what could be better — not to validate existing decisions.

### The game in 60 seconds

The player is Napoleon. They type natural-language commands to marshals ("Ney, attack Wellington") and to their foreign minister Talleyrand ("propose alliance with Prussia"). Marshals have personalities and can disobey. The diplomacy system uses a deterministic acceptance formula — the AI decides mechanically, LLM adds flavor text only. There are 5 nations (France, Britain, Prussia, Austria, Saxony) on a 19-region map. The game targets EU4/Paradox fans who want character-driven strategy.

The diplomacy system already has: treaty states (WAR through ALLIANCE), a proposal/counter-offer flow via Talleyrand, a coalition system (anti-France), vassalization, a diplomatic points currency, nation relations (-100 to +100), and a war score system. What it currently lacks is **political memory and strategic consequence** — France can befriend everyone simultaneously, betrayal fades too fast, and promises are just flavor.

### What you're reviewing

The **Reliability + Commitments Spec** (v0.4) tries to fix this with three interlocking systems:

1. **Rivalries** — nations care who you align with (France allying Prussia angers Austria)
2. **Betrayal memory** — nations remember broken treaties with escalating consequences
3. **Territorial promises** — tracked obligations with deadlines ("help Prussia take Saxony within 10 turns")

There is also an **Implementation Plan** that breaks this into 8 sessions.

### Your review mandate

Play devil's advocate. Assume the spec has blind spots. Specifically:

**1. Play it in your head (3 full scenarios)**

Mentally simulate three complete diplomatic arcs on this 5-nation, 19-region map:

- **Scenario A — The Faithful Ally:** France picks Prussia as its primary partner, honors every commitment, and tries to win through reliable alliance-building. Does the spec reward this path enough? Is it *fun*? Or does it just feel like avoiding penalties?

- **Scenario B — The Betrayer:** France promises Saxony to Prussia, then vassalizes Saxony instead. Then tries to rebuild trust. Walk through every penalty, every redemption tick, every AI reaction. Is the punishment curve right? Too harsh? Too forgiving? Does redemption feel earned or just mechanical?

- **Scenario C — The Juggler:** France tries to maintain good relations with everyone simultaneously — the exact behavior the spec claims to prevent. Can a clever player still game the system? Where are the exploits? Does the rivalry pressure actually force hard choices, or can you work around it?

**2. Challenge the core assumptions**

For each, argue why it might be wrong:

- "Rivalries should be mostly static in v0.1" — Does this make the system feel authored/scripted rather than emergent? Will players figure out the 3 fixed rival pairs in 2 games and then the system becomes furniture?
- "Territorial promises are AI-initiated only" — Does this cripple the player's agency? Can the player ever feel like a diplomatic mastermind if they can't author promises?
- "Passive allied control counts as fulfillment" — Does this make promises feel hollow? ("I promised to help you take Saxony, then did nothing, but you took it yourself — promise fulfilled!")
- "Two paradox options only (reject / downgrade)" — Is the missing "proceed at cost" option actually needed for the system to feel like a real political choice rather than a binary gate?
- "Betrayal strikes decay after 8 honorable turns" — Is 8 turns too short on a game that runs 30-50 turns? Does this mean betrayal has no real long game?

**3. Find the missing interactions**

The spec exists alongside a coalition system, a vassal system, and a war score system. Look for:

- **Contradictions:** Where could rivalry rules and coalition rules give the player conflicting signals? (e.g., "Austria is angry you allied Prussia" vs "Austria joined the coalition because of threat, not rivalry — does anger stack or conflict?")
- **Dead combinations:** Are there rivalry + commitment states that create no-win scenarios the player can't escape? Or conversely, states where the system has no opinion and diplomacy goes back to being a one-way friendship ramp?
- **Missing feedback loops:** The spec adds penalties for bad behavior. Where are the *rewards* for good behavior beyond "absence of penalty"? Does the faithful ally get anything the betrayer can't eventually earn back?

**4. Judge the implementation plan**

- Is the session ordering correct? Would you reorder anything?
- Are there sessions that are too large or too small?
- Is Slice D (AI integration) safe to defer, or does the system feel dead without AI actively using rivalries in proposals?
- Are ~107 tests enough? Where would you want more coverage?

**5. Kill your darlings**

If you had to cut ONE of the three systems (rivalries, betrayal memory, territorial promises) because scope is too large, which one would you cut and why? What's the minimum viable version of this spec that still solves the core "universal friendship" problem?

### Output format

Structure your review as:

1. **Scenario walkthroughs** (A, B, C) — what happened, what felt right, what felt wrong
2. **Assumption challenges** — your strongest argument against each assumption listed above
3. **Interaction gaps** — contradictions, dead states, missing rewards
4. **Implementation feedback** — ordering, sizing, risk
5. **The cut** — which system you'd drop if forced, and the minimum viable spec
6. **Top 5 changes** — ranked list of specific spec changes you'd make, with reasoning

Be specific. Reference section numbers. If you think something should change, say exactly what it should change TO, not just that it's wrong. If the spec is actually solid on a point, say so — but fight for your criticism first.
