# Commitments Presentation Playtest Script

> **Status:** v1 — Apr 15, 2026
> **Purpose:** 20-minute structured playtest to measure the baseline felt experience of commitments events as they currently render — *before* the C3 presentation pass ships. Results calibrate the prediction that current surfacing lands as accounting. After C3 ships, re-run the same script and compare.
> **Who runs it:** facilitator is the designer or engineering lead. Player is a fresh-eyes participant with strategy-game experience but **no exposure** to `COMMITMENTS_PRESENTATION_SPEC.md`, `RELIABILITY_COMMITMENTS_SPEC.md`, or this document.
> **Time:** 20 minutes total. 5 setup / 10 play / 5 debrief.

---

## Why run this

The four-lens design review is confident criticism. "The player will feel nothing at the betrayal" is a *prediction*, not a *measurement*. Without a baseline playtest, we cannot:

- Tell whether C3 actually improved anything when it ships.
- Distinguish severity 5 findings from severity 3 findings.
- Catch problems the review missed (novice-confusion failures, for example).

This script is deliberately simple. It is not a usability study. It is a 20-minute signal-check: does the current commitments layer land, or does it flatten, and what specifically does the player struggle to feel?

---

## Prerequisites

- A running build of the game on the current branch (`master`, commit `cc7d83d` or later).
- A save file (or debug setup) where France is mid-war, has at least one active bargain, and can have additional commitments events triggered on demand.
- Facilitator familiar with the cheat/debug commands in `backend/commands/meta_executor.py` required to force-trigger each event (see §14 of `COMMITMENTS_PRESENTATION_SPEC.md` event list).
- A quiet room. A recording is ideal; a note-taker is acceptable.
- Printed copy of the Debrief Question Sheet (below) for the facilitator.

**If debug triggers for all five events are not available**, a pre-baked save file must be prepared that sequences the five events across 4-5 turns. This takes longer to prepare but is the more reliable path.

---

## Recruitment

**Target profile:**
- Has played at least one Paradox grand strategy game (EU4, CK3, Victoria, HOI4) to a competent level.
- Enjoys or tolerates heavy text UIs.
- Has NOT previously playtested this game.
- Has NOT read any internal specs.
- Comfortable thinking aloud while playing.

**Avoid:**
- Team members who have read the specs.
- First-time strategy players (they will struggle with baseline game concepts, which is not what this tests).
- Close friends of the design lead (politeness bias).

**Sample size:** 1 is enough for a baseline signal. 2 is better. 3 is overkill for this purpose.

---

## Pre-session prep (facilitator, before the player arrives)

1. Load the save file. Verify that the scheduled event sequence triggers correctly by running through it once alone.
2. Prepare a note-taking template with five rows — one per event — and columns: *player first reaction (verbatim quote)*, *player action (what they clicked / typed)*, *observed emotional register (1-5)*, *debrief Q&A*.
3. Close all internal docs. If Cursor / Claude Code / IDE is visible on screen, close them.
4. Have the Debrief Question Sheet printed and to hand.

---

## Session structure

### Part 1 — Setup (5 min)

**Do not reveal:**
- That this is a "commitments presentation" review.
- That we expect betrayals / paradoxes to land a particular way.
- The names "spotlight," "Talleyrand," "episode," "bargain" unless the player uses them first.

**Do reveal:**
- "This is a Napoleonic grand strategy game. You play France in 1805. You type commands to your marshals and diplomats, and they respond."
- "I want you to play for about 10 minutes. Think aloud. Tell me what you notice, what confuses you, what surprises you."
- "I may ask you some questions after. There are no wrong answers."

Show the player the HUD for 60 seconds, point out only: the terminal, the notification rail, the Diplomatic Ledger (D key), the Morning Dispatch re-read, and the campaign log.

Do NOT explain the notification rail tiers, the ledger's commitments filter, or any surface contract. The player discovers the surfaces on their own.

### Part 2 — Play (10 min)

Facilitator triggers events in this order. Between events, let the player take at least one normal turn so their context is ordinary-diplomacy, not "here comes another scripted moment."

| # | Event | Rough turn | Facilitator trigger | What to watch for |
|---|---|---|---|---|
| 1 | `bargain_ratified` | T+1 | France and Austria ratify a bargain on Hanover | Does the player notice? Do they understand what just happened? |
| 2 | `bargain_triggered` | T+2 | The Hanover bargain becomes live in an active war | Does the player register the state transition? |
| 3 | `bargain_fulfilled` | T+3 | France keeps its word to Austria | Does the player feel anything? Can they describe the moment in one sentence? |
| 4 | `bargain_breached` | T+4 | France is forced to break a separate bargain with Prussia (ally-witness: Austria) | **CRITICAL BEAT.** Observe silence/speech, body language, decision to click through or linger, any verbalization of feeling. |
| 5 | `commitment_paradox` | T+5 | Ratifying a new Prussian treaty would break faith with Austria (blocking hard-stop) | **CRITICAL BEAT.** Does the player understand this is unresolvable without a choice? Do they feel the weight? Do they search for a third option? |

Optional extension (if time permits and player is engaged):
- `hard_reject_posture_triggered` — Britain enters closed-door posture after enough strikes accumulate. Particularly useful for testing whether "the foreign-office voice" reads as anyone at all.
- `declaration_backed_out` — ally refuses and the player backs out of a war declaration. Tests the silent-suppression decision in §12.4.

**Facilitator behavior during play:**
- Do not explain anything unless the player is stuck on a basic UI mechanic (how to type a command, how to open the ledger).
- Do not hint that an event was "big." Let the player discover prominence.
- Do not fill silence. Silence is data.
- If the player verbalizes an interpretation, write it down verbatim and DO NOT correct it. Misinterpretations are the most valuable data.

### Part 3 — Debrief (5 min)

Ask exactly these questions, in this order, without editorializing between them.

---

## Debrief Question Sheet

*(Hand-printable single page.)*

**Q1. If you had to describe the last ten minutes to a friend in three sentences, what happened?**
> *What to listen for:* Does the player describe political events (betrayal, broken word, dilemma) or mechanical events (relation dropped, notification appeared, popup blocked me)? If it's all mechanical, the spec's prediction is confirmed.

**Q2. Which moment in the last ten minutes felt biggest? Why?**
> *What to listen for:* Does the player name the betrayal or the paradox (the two "critical beats"), or do they name something else entirely? If something else, we missed where the weight was landing.

**Q3. When France broke its word to Prussia — who told you that? Can you describe them?**
> *What to listen for:* Does the player name Hardenberg or Prussia or "an envoy"? If the answer is "the game" or "a notification," the anonymous-envoy finding is confirmed. If the player cannot recall any speaker, it's worse than confirmed.

**Q4. Rate each of these on a 1-5 scale, where 1 = "a status change" and 5 = "a political moment you will remember":**
> - The moment France kept its word to Austria: _ / 5
> - The moment France broke its word to Prussia: _ / 5
> - The moment you were told you must choose which promise to keep: _ / 5

> *What to listen for:* Expect 2s and 3s on the first two, possibly a 4 on the paradox because blocking is inherently weighty. Any 5 is unexpected and worth probing. Any 1 is a severity confirmation.

**Q5. When Prussia was wronged, did you want to do anything in response? What?**
> *What to listen for:* Whether the player articulated a specific verb ("send them money," "apologize," "propose a new treaty to patch it over," "retaliate against whoever caused this"). Then ask: *did the game let you do that?* If the answer is "no" or "I didn't look" — the reactive-affordance finding is confirmed.

**Q6. When you had to choose between honoring Austria or Prussia, how did you decide?**
> *What to listen for:* Did the player reason about historical relationships, about future AI consequences, or mostly about "which click I felt like"? If the latter, the paradox is not staged heavily enough to carry the weight of the choice.

**Q7. Was there any moment where you felt the game was "talking" to you, versus "informing" you?**
> *What to listen for:* The player's own phrasing. This is the VISION.md signal directly. An honest "no" here is a severe finding.

**Q8. If you had to change one thing about how these events were presented, what would it be?**
> *What to listen for:* Don't design the change; just capture. Player change-requests surface gaps the reviewers missed.

---

## Scoring and interpretation

### Primary metric: Q4 weighted sum

| Q4 score sum (of three items) | Interpretation |
|---|---|
| 3-6 | Prediction confirmed. Current surfacing lands as accounting. C3b is high-value. |
| 7-10 | Mixed. Parts land, parts flatten. Ship C3a; let C3b findings drive prioritization. |
| 11-15 | Prediction challenged. Baseline is better than the review assumed. Question whether the C3b investment is necessary. |

### Secondary signals

- **Q1 vocabulary:** If zero political words appear in the three-sentence recap, the spec's "feels like a changelog" prediction is the strongest interpretation.
- **Q3 speaker recall:** Inability to name any speaker confirms the named-diplomat routing priority.
- **Q5 action-desire:** Player who articulates a specific desired verb but finds no route validates the §12.6 widening.
- **Q7 "talking vs informing":** The most important qualitative signal. A cold "informing" answer is a VISION.md failure.

### What the playtest cannot tell us

- Whether C3 will actually fix the problem. (That's the post-C3 re-test.)
- Whether the commitments engine's mechanical rules are correct. (Separate audit.)
- Whether LLM mode would recover the drama. (Mock mode is authoritative per design.)
- Whether long-play retention issues exist. (Not in scope for a 20-minute session.)

---

## Post-session processing

1. Within 24 hours of the session, the facilitator writes a 300-word summary including: Q4 scores, verbatim Q1 recap, verbatim Q3 speaker-recall, and one paragraph of qualitative observation.
2. The summary is appended to `docs/COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md` as a "Playtest Findings" section, dated.
3. If Q4 sum is 6 or below: the summary is labeled "baseline confirmed flat" and C3b is treated as high-priority.
4. If Q4 sum is 11 or above: convene a design review to question the scope of C3b.
5. Raw notes and any recording are archived; they are not published.

---

## Re-test contract (after C3 ships)

After both C3a and C3b land, re-run this exact script with a new fresh-eyes player. Compare Q4 sums and Q1 vocabulary.

Success criteria for C3:
- Q4 sum improves by at least 3 points.
- Q3 answers name at least one diplomat (Hardenberg, Metternich, etc.) unprompted.
- Q7 produces at least one "yes, at this moment" answer.

Failure modes to watch for:
- Q4 scores go up but Q1 vocabulary stays mechanical → we achieved weight without achieving *political* weight. The spec prose needs another pass.
- Q3 improvement but Q5 unchanged → drama landed, agency didn't. §12.6 response routes may not have been wired correctly.
- Both Q3 and Q5 improve, Q7 stays cold → we added named actors and verbs but the staging still feels menu-like. Reveal cadence, typographic contract, and surface-tier work (§9.1, §14 C3a-pre) were skipped.

---

## Changelog

- **Apr 15, 2026** — v1. Five-event play sequence, eight-question debrief, Q4-weighted interpretation frame, post-C3 re-test contract. To be validated by running the first baseline session.
