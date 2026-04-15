# Commitments Presentation Pass Spec

> **Status:** Draft v0.1
> **Date:** April 15, 2026
> **Queue Position:** Proposed post-`C2` follow-up inside `Reliability + Commitments`
> **Recommended Placement:** `C3` immediately after `C2`, before `Bilateral Peace Hardening`
> **Depends On:** `docs/RELIABILITY_COMMITMENTS_SPEC.md`, `docs/RELIABILITY_IMPLEMENTATION_PLAN.md`, `docs/DIPLOMACY_SPEC.md`, `docs/CONVERSATIONAL_DIPLOMACY_DESIGN.md`, `docs/INFORMATIONAL_UI_PLAN.md`

---

## 1. Purpose

The commitments engine now creates real political moments:

- rival anger
- betrayal memory
- bargain ratification / triggering / fulfillment / breach / void
- ally-entry refusal and hard blocks
- hard-reject diplomatic shutdown
- paradox hard stops

What it does **not** yet fully do is make those moments feel important in play.

Right now too many commitments consequences are likely to land as:

- a warning row
- a relation delta
- a strike counter
- a compact campaign-log line

This spec adds a narrow presentation pass over the commitments layer so the player feels the political consequences the engine already computes.

The pass must remain **mechanically inert**. It owns framing, pacing, and surfacing. It does not own any diplomatic outcome.

---

## 2. Phase Placement

This is **not** a new major diplomacy phase.

This is a narrow post-`C2` follow-up that should sit **inside** the `Reliability + Commitments` track:

1. `A1-A2` foundations and preview scaffolding
2. `B1-B3` rivalry / betrayal / paradox logic
3. `C1a-C1b` war bargain creation + lifecycle
4. `C2` ally-entry integration and commitments surfaces
5. **`C3` commitments presentation pass** <- this spec
6. `Bilateral Peace Hardening`
7. later `War Purpose + Score Semantics`
8. later `Ally Participation + Common Peace`

Why it belongs here:

- `C2` creates the meaningful commitments events.
- `C3` makes those events legible and dramatic while the player still remembers the new systems.
- waiting until the broader `Talleyrand Desk + Explanation Layer` track would bury a commitments-specific need inside a much larger advisory/UI pass.

What this is **not**:

- not `D1` strategic-focus AI work
- not common peace
- not coalition generalization
- not generic diplomacy polish
- not a new screen-family project

---

## 3. Problems To Solve

### P1. Big political moments currently risk landing as accounting

Fulfilling or betraying a bargain should feel like a diplomatic event, not just a number change.

### P2. The commitments system has multiple valid surfaces but no priority rule for dramatic emphasis

The project already has:

- blocking popups
- Morning Dispatch
- persistent notices
- ledger
- campaign log

What is missing is a commitments-specific rule for which moments deserve which surface.

### P3. Existing conversation / dispatch systems are broad, not commitments-aware

The current Talleyrand and dispatch systems can carry this work, but they do not yet define:

- which commitments moments get spotlight treatment
- how to suppress spam
- how to turn structured commitment payloads into memorable commentary

### P4. The player needs to feel political closure without adding mechanics

The commitments layer should feel more alive **without** reopening engine rules, timing, or AI outcomes.

---

## 4. Goals

- Make the largest commitments consequences feel memorable.
- Keep all mechanics deterministic and unchanged.
- Reuse existing surfaces rather than inventing a new diplomacy UI family.
- Create consistent priority rules for spotlight vs notice vs ledger-only moments.
- Ensure mock mode stays fully valid without LLM prose.
- Keep this pass narrow enough to ship as one focused follow-up session.

---

## 5. Non-Goals

- This spec does **not** change betrayal numbers, bargain logic, war-entry thresholds, or paradox rules.
- This spec does **not** redesign Morning Dispatch globally.
- This spec does **not** redesign the broader Talleyrand desk / trend / explanation surface.
- This spec does **not** add common peace, settlement allocation, or beneficiary spoils theatrics.
- This spec does **not** add new screen families, cinematic cutscenes, or map animations.
- This spec does **not** make LLM prose mandatory. Mock templates remain authoritative.
- This spec does **not** own coalition UI generally; it may only add commitments-aware commentary where an existing coalition event is already being surfaced.

---

## 6. Design Principle

The voice layer is a **render layer over deterministic engine output**.

For commitments events:

- the engine decides what happened
- the presentation router decides how prominently it should be surfaced
- templates or LLM prose decide how it sounds

Golden rules:

- no presentation layer may change score, state, cooldown, or outcome
- every dramatic line must be traceable to an existing deterministic payload
- one political moment should feel like one moment, not five duplicated notifications

---

## 7. Presentation Model

The commitments presentation pass uses four existing surface tiers.

### 7.1 Blocking hard-stop

Use only when the player must decide **now**.

This tier already exists and remains mechanically owned by prior slices:

- `commitment_paradox`
- war-entry counter-bargain
- any future commitments hard-stop already defined elsewhere

`C3` does not create new hard-stop mechanics. It only improves copy, emphasis, and fallout framing on these existing surfaces.

### 7.2 Dispatch spotlight

Use for the largest completed or triggered political moments.

This is the core new dramatic tier for commitments.

The dispatch spotlight should feel like:

- "something politically important just happened"
- "here is why it matters"
- "here is where to inspect it further"

### 7.3 Persistent notice

Use for medium-weight events that matter but should not dominate the whole turn.

These remain visible and reviewable, but they do not stop play.

### 7.4 Ledger / campaign log reference

Every commitments event should still appear in the durable reference layer.

The ledger and log remain the source of truth.
They are not the only emotional surface.

---

## 8. Event Routing

### 8.1 Core event table

| Event | Primary surface | Supporting surfaces | Notes |
|------|------------------|---------------------|-------|
| `bargain_ratified` | persistent notice | ledger, campaign log | Important, but usually not turn-defining |
| `bargain_triggered` | persistent notice | ledger, campaign log | "The deal is now live in war" should be visible but not overblown |
| `bargain_fulfilled` | dispatch spotlight | notice, ledger, campaign log | One of the best positive payoffs in the system |
| `bargain_breached` | dispatch spotlight | notice, ledger, campaign log | One of the sharpest negative payoffs in the system |
| `bargain_voided` | persistent notice | ledger, campaign log | Visible closure without overdrama |
| `witness_strike_recorded` | persistent notice | ledger, campaign log | Default route for ordinary witness fallout |
| `hard_reject_posture_triggered` | dispatch spotlight | ledger, campaign log | Should feel like a door closing |
| `hard_block_surfaced` on ally entry | persistent notice or inline preview only | ledger if commitment-related | No dispatch spotlight unless it creates a larger downstream consequence |
| `ally_refused_free_join` | persistent notice | ledger, campaign log | Keep visible; do not steal the turn |
| `commitment_paradox` | blocking hard-stop | ledger, campaign log | Existing hard-stop; `C3` enriches framing only |
| counter-bargain accepted / rejected / backed out | existing blocking confirm | campaign log, ledger when a bargain is created | No duplicate notice on the same turn |

### 8.2 Spotlight threshold rules

Dispatch spotlight is reserved for:

- `bargain_fulfilled`
- `bargain_breached`
- first-time `hard_reject_posture_triggered`
- the highest-severity commitments event of the turn if it materially closes or opens diplomatic space

Do **not** spotlight:

- every witness strike
- every void
- every hard block
- every trigger transition

### 8.3 One-turn emphasis rule

Maximum:

- 1 commitments dispatch spotlight per turn
- 2 commitments notices promoted above the fold in the same turn

If multiple high-value commitments events occur together:

1. `bargain_breached`
2. `hard_reject_posture_triggered`
3. `bargain_fulfilled`
4. `commitment_paradox` resolution fallout
5. `bargain_voided`
6. `witness_strike_recorded`

The rest still enter ledger and campaign log.

### 8.4 No duplicate-surface rule

If an event already occupied a blocking surface this turn:

- do not also raise it as a separate persistent notice
- do not spawn a redundant dispatch line repeating the same information

Instead:

- fold the aftermath into the blocking result text
- write the durable record to ledger / campaign log

---

## 9. Surface Contracts

### 9.1 Dispatch spotlight card

Use the existing Morning Dispatch delivery path.

Each commitments spotlight should include:

- a short headline
- 2-4 lines of Talleyrand commentary or diplomatic narration
- 1 compact consequence line naming the main political effect
- one obvious review action such as `Open Ledger` or `Review Bargains`

Do **not** overload it with:

- full formula breakdowns
- five witness names
- exhaustive tooltip content

That belongs in the ledger and log.

### 9.2 Persistent notice card

Each commitments notice should show:

- event headline
- the main nation affected
- one-line consequence summary
- optional review action if the player can inspect a relevant surface quickly

Notice cards should be concise enough that three of them do not feel like a second dispatch.

### 9.3 Ledger emphasis

This pass should add emphasis, not a new ledger family.

Recommended emphasis rules:

- fulfilled bargains get a recent-success badge for a short window
- breached bargains get a recent-breach badge for a short window
- nations in hard-reject posture display a clear closed-door marker
- the latest commitments event should be easy to spot in the related ledger section

### 9.4 Campaign log

Campaign log entries remain compact.

This pass may improve:

- wording quality
- event naming consistency
- metadata-driven summaries

It should **not** turn the campaign log into a second dispatch essay surface.

---

## 10. Voice Contract

### 10.1 Template-first

Mock mode must remain fully authoritative.

Every commitments event that receives spotlight or notice treatment should have:

- a deterministic headline template
- a deterministic body template
- slot values pulled from structured payloads

### 10.2 LLM mode

LLM mode may vary prose only.

It may:

- enrich tone
- vary wording
- sharpen diplomatic flavor

It may **not**:

- invent new facts
- imply uncomputed motives
- contradict the structured payload

### 10.3 Speaker rules

Default speaker by surface:

- blocking hard-stop: Talleyrand or direct diplomatic relay
- dispatch spotlight: Talleyrand commentary by default
- persistent notice: neutral system headline, optional short Talleyrand line
- campaign log: neutral declarative summary

### 10.4 Refusal and hard-block explanations

If the engine provides:

- hard-block reason
- war-entry score breakdown
- strongest negative factor

then the presentation layer should use it.

If the engine does **not** provide enough structured explanation:

- prefer a short, honest explanation
- do not let the voice layer invent causal detail

---

## 11. Payload Contract

Do **not** create a second long-lived commitments presentation store.

This pass should build on:

- existing dispatch metadata
- campaign-log metadata
- response payloads already produced by commitments systems

Where one normalized surface payload is needed, use a transient structure like:

```python
commitment_surface_event = {
    "event_type": "bargain_breached",
    "severity": "high",
    "primary_surface": "dispatch_spotlight",
    "primary_nation": "Prussia",
    "secondary_nation": "France",
    "target_enemy": "Britain",
    "claim_region": "Hanover",
    "source_commitment_id": "commitment_12",
    "relation_delta": -12,
    "reliability_delta": -4,
    "witness_nations": ["Austria"],
    "hard_block_reason": None,
    "top_reason_text": "France aligned with the named enemy instead.",
    "review_target": "ledger_commitments",
}
```

Required rules:

- all fields primitive-only
- no live object references
- no duplicate authority over commitment state

If a field is not known deterministically, omit it rather than improvising it in presentation.

---

## 12. Example Player Experience

### 12.1 Bargain fulfilled

Engine outcome:

- bargain moves to `fulfilled`
- relation and reliability rewards apply
- `fulfillment_snapshot` written

Player experience:

- Morning Dispatch spotlight frames it as France having kept its word
- ledger marks the bargain as newly fulfilled
- campaign log records the durable event

Desired feeling:

- "This alliance meant something."

### 12.2 Bargain breached

Engine outcome:

- bargain moves to `breached`
- betrayal fallout applies

Player experience:

- Morning Dispatch spotlight frames the diplomatic cost
- if witnesses were relevant, one summarized consequence line mentions that the courts are watching
- ledger and log preserve the exact fallout

Desired feeling:

- "I traded future trust for this move."

### 12.3 Hard-reject posture triggered

Engine outcome:

- a nation reaches the strike threshold and will now hard-resist deep treaties

Player experience:

- one featured dispatch spotlight tells the player that this channel is effectively closing
- the next relevant preview / refusal reinforces that state
- the ledger makes it obvious that the posture is active

Desired feeling:

- "That nation is not just numerically colder. They are diplomatically shut."

### 12.4 Ally-entry hard block

Engine outcome:

- ally cannot legally or plausibly join

Player experience:

- keep the main explanation inline at the ally-entry surface
- optionally raise a compact notice if a live bargain was implicated
- do not promote this into a dramatic dispatch unless it caused a larger downstream state change

Desired feeling:

- "I understand why this failed."

---

## 13. Anti-Spam Rules

- No more than 1 commitments dispatch spotlight per turn.
- No more than 2 above-the-fold commitments notices per turn.
- Blocking hard-stops suppress duplicate notice-generation for the same root event.
- Multiple witness strikes from one root event should collapse into one summarized presentation event when surfaced outside the ledger.
- A `bargain_triggered` notice should be suppressed if the same bargain is fulfilled or breached in the same turn and that higher-severity event is already surfaced.
- If a commitments event is unrelated to the current blocking popup, queue it into the normal notice/dispatch path instead of interrupting the player mid-resolution.

---

## 14. Proposed Implementation Slice

### C3. Commitments presentation pass

**Files:** `backend/game_logic/dispatch.py`, `backend/game_logic/diplomatic_templates.py`, `backend/game_logic/diplomatic_dialogue.py`, `backend/game_logic/diplomatic_ledger.py`, `backend/campaign_log.py`, `backend/main.py`, `godot-client/project-sovereign/scripts/main.gd`, `godot-client/project-sovereign/scripts/diplomatic_ledger.gd`, `godot-client/project-sovereign/scripts/campaign_log.gd`, notice / dispatch surfaces already used by diplomacy

Core tasks:

- define commitments event routing rules across blocking / dispatch / notice / ledger
- add commitments-specific spotlight and notice templates
- enrich existing hard-stop copy for paradox and counter-bargain outcomes
- add ledger emphasis rules for recent fulfillment / breach and active hard-reject posture
- wire duplicate suppression so one event does not surface three times
- keep campaign-log summaries compact but more specific

Suggested tests:

- spotlight priority ordering across multiple same-turn commitments events
- no duplicate notice after blocking counter-bargain resolution
- `bargain_triggered` suppression when same-turn `fulfilled`
- hard-reject posture gets one featured moment, not a repeated every-turn notice
- witness-strike collapse into one medium surface event
- save/load safety for any new transient surface payload
- mock-mode template coverage for all spotlight-worthy commitments events

Estimated budget:

- one focused session
- approximately 16-22 tests

---

## 15. Future Handoff

This pass should hand off cleanly to later systems:

- `Bilateral Peace Hardening`
  - can reuse spotlight / notice routing for promise-adjacent peace fallout
- `Talleyrand Desk + Explanation Layer`
  - can absorb the same commitments payloads into richer advisory surfaces later
- generalized coalition work
  - may later reuse the same spotlight principles for bloc pressure and split events

This spec should **not** pre-own those future systems.

Its job is narrower:

- make the current commitments layer feel alive
- without dragging later systems forward prematurely

---

## 16. Acceptance Criteria

This pass is successful if:

- a player can tell the difference between routine diplomacy bookkeeping and a major commitments moment
- bargain fulfillment and breach feel materially different in presentation weight
- hard-reject posture feels like a diplomatic state change, not just an invisible threshold
- witness fallout is legible without becoming spam
- all of the above work identically in mock mode without LLM dependency
- no commitments presentation surface changes any underlying outcome
