# Commitments Presentation Pass Spec

> **Status:** Draft v0.2
> **Date:** April 15, 2026
> **Queue Position:** Proposed post-`C2` follow-up inside `Reliability + Commitments`, split into `C3a` routing and `C3b` drama
> **Recommended Placement:** `C3a` immediately after `C2`; `C3b` immediately after `C3a`, before `Bilateral Peace Hardening`
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

This document therefore splits the work in two:

- `C3a` makes commitments presentation structurally correct: routing, suppression, payload ownership, and ledger emphasis.
- `C3b` makes it dramatically alive: committed prose, cast discipline, aftermath beats, and reactive conversational follow-ups.

`C3a` may land first if schedule requires it. Full narrative sign-off does not happen until `C3b` lands.

---

## 2. Phase Placement

This is **not** a new major diplomacy phase.

This is a narrow post-`C2` follow-up that should sit **inside** the `Reliability + Commitments` track:

1. `A1-A2` foundations and preview scaffolding
2. `B1-B3` rivalry / betrayal / paradox logic
3. `C1a-C1b` war bargain creation + lifecycle
4. `C2` ally-entry integration and commitments surfaces
5. `C3a` commitments presentation routing
6. `C3b` commitments drama pass
7. `Bilateral Peace Hardening`
8. later `War Purpose + Score Semantics`
9. later `Ally Participation + Common Peace`

Why it belongs here:

- `C2` creates the meaningful commitments events.
- `C3a` makes those events legible and correctly routed while the player still remembers the new systems.
- `C3b` makes those same events sound and linger like political drama rather than release-note copy.
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
- Commit at least one canonical mock-mode prose template for every spotlight-worthy commitments family.
- Stage breach and paradox across more than one beat so they feel remembered, not merely emitted.
- Restore limited no-cost player response options through existing conversation surfaces.
- Keep this pass narrow enough to ship as two focused follow-up sessions.

---

## 5. Non-Goals

- This spec does **not** change betrayal numbers, bargain logic, war-entry thresholds, or paradox rules.
- This spec does **not** redesign Morning Dispatch globally.
- This spec does **not** redesign the broader Talleyrand desk / trend / explanation surface.
- This spec does **not** add common peace, settlement allocation, or beneficiary spoils theatrics.
- This spec does **not** add new screen families, cinematic cutscenes, or map animations.
- This spec does **not** make LLM prose mandatory. Mock templates remain authoritative.
- This spec does **not** own coalition UI generally; it may only add commitments-aware commentary where an existing coalition event is already being surfaced.
- `C3` does **not** set rail-wide notice caps. Rail-wide budget ownership stays with `INFORMATIONAL_UI_PLAN.md`; `C3` only defines commitments-local usage within that existing budget.
- This spec does **not** add new commitment outcomes, negotiation branches, or action costs; any new follow-up actions are no-cost advisory or inspection routes only.

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

**Spotlight surface:** the spotlight tier is rendered on the **persistent notice rail** using an elevated "spotlight" style — a larger card, top-stacked above ordinary notices, persisting for 2 turns before decaying to a normal notice. The rail is the immediate in-turn surface for a spotlight event.

**Relationship to Morning Dispatch:** the Morning Dispatch owns a highlighted "Spotlight Carryover" section that replays any spotlight events raised during the previous turn as NEXT-TURN dispatch cards. In-turn spotlight display is the rail; next-turn reinforcement is the dispatch. Mid-turn commitments events never inject directly into `build_morning_dispatch()` — the rail is the mid-turn delivery path.

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
| `bargain_fulfilled` | dispatch spotlight | notice, ledger, campaign log, optional aftermath callback | One of the best positive payoffs in the system. Spotlight uses Talleyrand voice and `C3b` commits a full mock template. |
| `bargain_breached` | dispatch spotlight | notice, ledger, campaign log, required aftermath callback | One of the sharpest negative payoffs in the system. `C3b` treats it as a three-beat sequence: injured-party accusation, one scoped witness reaction, next-turn Talleyrand aside. |
| `bargain_voided` | persistent notice | ledger, campaign log | Visible closure without overdrama |
| `witness_strike_recorded` | persistent notice | ledger, campaign log | Default route for ordinary witness fallout. Emission contract filed in `RELIABILITY_IMPLEMENTATION_PLAN.md` B2a. |
| `hard_reject_posture_triggered` | dispatch spotlight | ledger, campaign log, optional aftermath callback | Should feel like a door closing. Uses foreign-court or chancery voice rather than default Talleyrand narration. First-time-threshold-crossing emit contract filed against B2b in `RELIABILITY_IMPLEMENTATION_PLAN.md`; `C3` is blocked on that emit landing. |
| `hard_block_surfaced` on ally entry | persistent notice or inline preview only | ledger if commitment-related | No dispatch spotlight unless it creates a larger downstream consequence |
| `ally_refused_free_join` | persistent notice | ledger, campaign log | Keep visible; do not steal the turn |
| `commitment_paradox` | blocking hard-stop | ledger, campaign log, required aftermath callback | Existing hard-stop; `C3b` adds grave framing, after-choice aside, and next-turn callback while reusing the existing `commitment_paradox` body text from `CONVERSATIONAL_DIPLOMACY_DESIGN.md`. |
| counter-bargain `Accept` | existing blocking confirm | persistent notice ("Ally joined"), campaign log, ledger bargain record | One follow-up notice; do not spawn a second spotlight. |
| counter-bargain `Reject` | existing blocking confirm | persistent notice ("Ally refused, war continues"), campaign log | Declaration continues without the ally; notice informs the player the ally stayed out. |
| counter-bargain `Back Out` | existing blocking confirm | ledger entry ("Declaration withdrawn"), campaign log (`declaration_backed_out`) | `pending_declaration` transaction cancelled per C2; DP/AP refunded; no "Ally refused" notice. See §12.4 and §14 test list. |

### 8.2 Spotlight threshold rules

Dispatch spotlight is reserved for:

- `bargain_fulfilled`
- `bargain_breached`
- first-time `hard_reject_posture_triggered` — **blocked on B2b emit contract** (see `RELIABILITY_IMPLEMENTATION_PLAN.md` B2b add for first-time threshold crossing)
- the highest-severity commitments event of the turn if it materially closes or opens diplomatic space

Do **not** spotlight:

- every witness strike
- every void
- every hard block
- every trigger transition

### 8.3 One-turn emphasis rule

Commitments items consume at most 1 spotlight slot and 2 non-spotlight notice slots **within the rail's existing budget**. Rail-wide budget is owned by `INFORMATIONAL_UI_PLAN.md`; `C3` only bounds commitments' local consumption.

If multiple high-value commitments events occur together:

1. `bargain_breached`
2. `hard_reject_posture_triggered`
3. `bargain_fulfilled`
4. `commitment_paradox` resolution fallout
5. `bargain_voided`
6. `witness_strike_recorded`

Hard-reject ranks above fulfillment because it represents a diplomatic door-closing — fulfillment reinforces an existing relationship, but hard-reject ends one. Closure beats reinforcement for emphasis.

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

Spotlight delivery uses the rail-elevated "spotlight" style described in §7.2 as the in-turn surface, and the Morning Dispatch "Spotlight Carryover" section as the next-turn reinforcement. Spotlights are not injected mid-turn into `build_morning_dispatch()`.

Each commitments spotlight is "Scene 1" of a political moment, not a headline-only notice. The card contract is:

- a short player-facing period headline
- 2-4 lines of committed prose
- 1 compact consequence line naming the main political effect
- one obvious review action such as `Open Ledger` or `Review Bargains`
- zero or one no-cost conversational follow-up button when the event family allows it
- an optional lower-weight secondary aside line with its own speaker attribution

Do **not** overload it with:

- full formula breakdowns
- five witness names
- exhaustive tooltip content

That belongs in the ledger and log.

`bargain_breached` uses a split-voice spotlight:

- lead line: injured party or envoy accusation
- optional witness line: one scoped reaction based on the dominant witness scope
- lower strip: private Talleyrand aside

`hard_reject_posture_triggered` does **not** default to Talleyrand. It should read like a chancery or foreign-court closure notice. `commitment_paradox` remains blocking, but its post-choice fallout uses the same 2-4 line discipline for the callback beat.

#### Dominant witness scope branching

When `witness_nations` is non-empty, spotlight copy selects one dominant witness scope. This is not cosmetic; it changes the dramatic meaning of the same breach.

Deterministic precedence when multiple scopes are present:

1. `ally`
2. `rival`
3. `shared_enemy`
4. `region_observer`

If presentation receives `dominant_witness_scope`, use it. Otherwise derive it using the order above.

| Dominant scope | Breach tone | Example direction |
|-----------|---------|---------------|
| `ally` | disappointment / trust collapse | "Vienna notes that Berlin's word was given publicly..." |
| `rival` | satisfaction / opportunism | "Prussia finds advantage in France's embarrassment..." |
| `shared_enemy` | recalculation / strategic opportunity | "London reads the breach as weakness in the anti-British front..." |
| `region_observer` | gossip / reputational chill | "The Italian courts repeat the story as proof that French assurances travel lightly..." |

Only one witness court is named in the spotlight. Full witness enumeration stays in ledger and campaign log.

### 9.2 Persistent notice card

Each commitments notice should show:

- event headline
- the main nation affected
- one-line consequence summary
- optional review action if the player can inspect a relevant surface quickly

Notice cards should be concise enough that three of them do not feel like a second dispatch.

#### Icon and label contract

`notification_bar.gd` `TYPE_ICONS` must be extended with commitments types. Icon keys are proposed names; actual art is commissioned later.

Player-facing labels use period vocabulary. Internal `event_type` values remain unchanged.

| Event type | Icon key | Player-facing label |
|-----------|---------|---------------|
| `bargain_breached` | `icon_bargain_breach` | Word Broken |
| `bargain_fulfilled` | `icon_bargain_fulfill` | Word Kept |
| `bargain_ratified` | `icon_bargain_ratify` | Articles Agreed |
| `bargain_triggered` | `icon_bargain_triggered` | The Pledge Comes Due |
| `bargain_voided` | `icon_bargain_voided` | Articles Lapsed |
| `hard_reject_posture_triggered` | `icon_hard_reject` | The Chancery Shut |
| `commitment_paradox` | `icon_paradox` | Conflicting Oaths |
| `witness_strike_recorded` | `icon_witness_strike` | The Courts Noticed |
| `declaration_backed_out` | `icon_declaration_backed_out` | Ultimatum Recalled |

#### Priority tier contract

Each commitments event maps to a `backend/notifications.py` priority tier. Tiers survive `NOTIFICATION_CAP` trimming behavior (CRITICAL retained, NORMAL trimmed first).

| Event type | Priority tier |
|-----------|---------------|
| `bargain_breached` | CRITICAL |
| `bargain_fulfilled` | NORMAL |
| `hard_reject_posture_triggered` | CRITICAL |
| `commitment_paradox` | CRITICAL |
| `witness_strike_recorded` | NORMAL |
| `declaration_backed_out` | NORMAL |
| `bargain_ratified` | NORMAL |
| `bargain_triggered` | NORMAL |
| `bargain_voided` | NORMAL |

### 9.3 Ledger emphasis

This pass should add emphasis, not a new ledger family.

Recommended emphasis rules:

- fulfilled bargains get a recent-success badge for a short window
- breached bargains get a recent-breach badge for a short window
- nations in hard-reject posture display a clear closed-door marker
- the latest commitments event should be easy to spot in the related ledger section

**Badge data source:** recent-success / recent-breach badges derive from `backend/campaign_log.py` entries where `turn >= current_turn - 3` and `event_type in {"bargain_fulfilled", "bargain_breached"}`. The closed-door marker reads from the commitment record's active `hard_reject_posture` flag set by B2b, not from log scanning.

**Review target routing:** the `review_target: "ledger_commitments"` action routes to the existing **Treaties** tab of the Diplomatic Ledger with a commitments section filter applied. A dedicated commitments sub-tab is **out of scope** for `C3`.

### 9.4 Scene 2: Aftermath

`episode_id` is not only a dedupe key. For spotlight-worthy or blocking commitments events, it is the memory hook for one required or optional follow-up beat.

Minimum contract by family:

| Event family | N+1 aftermath | Later callback window |
|-----------|---------|---------------|
| `bargain_breached` | required private Talleyrand aside in the next Morning Dispatch | one callback allowed on the injured party's next `incoming_proposal` or advisory appearance within 10 turns |
| `bargain_fulfilled` | optional private aside if the bargain materially changed trust | one positive callback allowed on the next relevant proposal or advisory appearance within 10 turns |
| `hard_reject_posture_triggered` | optional dispatch aside | the next treaty refusal or preview from that nation should carry one closure line while posture remains active |
| `commitment_paradox` | required after-choice aside plus next-turn dispatch callback | no later callback until the first callback has fired |

Callbacks are short: 1-2 lines, not a second essay.

Callbacks may be stored as metadata on the originating surface payload or campaign-log entry keyed by `episode_id`; do **not** create a second authoritative commitments state store. If a callback has not fired by turn `N+10`, expire it quietly.

### 9.5 Campaign log

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

Every commitments event family that can occupy spotlight or blocking prominence must ship with at least one canonical mock template committed in this spec and mirrored in `diplomatic_templates.py`.

For `C3b`, these are mandatory:

- `bargain_fulfilled`
- `bargain_breached`
- `hard_reject_posture_triggered`
- `commitment_paradox` framing and after-choice callback

The worked examples in §12 are not decorative. They are the acceptance fixtures for tone, slot usage, and surface length.

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

Talleyrand is **not** the default speaker for every important commitments moment.

| Event family | Lead speaker | Supporting speaker | Register |
|-----------|---------|---------------|---------------|
| `bargain_fulfilled` | `talleyrand` | none or neutral consequence line | urbane vindication; a little bite is welcome |
| `bargain_breached` | `envoy` | `talleyrand` private aside | accusation first, private counsel second |
| `hard_reject_posture_triggered` | `foreign_office` or `system` | optional Talleyrand aftermath only | formal closure, no quips |
| `commitment_paradox` | `talleyrand` | none | grave, tragic, explicitly not quippy |
| `witness_strike_recorded` | `system` or `foreign_office` | none | terse third-party observation |
| campaign log | `system` | none | neutral declarative summary |

**Render contract:** the notice detail panel must expose a speaker-attribution slot (valid values: `system`, `talleyrand`, `envoy`, `foreign_office`) as a field separate from body text. `notification_bar.gd` render contract is extended in `C3` scope to honor this slot.

Spotlight cards and expanded notice detail must support `speaker_attribution` values `system`, `talleyrand`, `envoy`, and `foreign_office` as structured attribution, not fake quoted text.

### 10.4 Witness scope as dramatic input

`scope_reason` is not ledger garnish. It is the narrative selector for witness reactions.

- `ally` witnesses sound disappointed, wary, or reconsidering.
- `rival` witnesses sound pleased, amused, or opportunistic.
- `shared_enemy` witnesses sound calculating; they smell a strategic opening.
- `region_observer` witnesses sound gossipy or reputational; the story is spreading.

This branching applies first to `bargain_breached` spotlight copy, and later to any callback line that references the same `episode_id`.

### 10.5 Refusal and hard-block explanations

If the engine provides:

- hard-block reason (promised by C2)
- war-entry score breakdown (promised by C2)
- severity-sorted `warnings[]` (per `RELIABILITY_COMMITMENTS_SPEC.md` §12.2)

then the presentation layer should use it. Explanation is composed from `warnings[]` sorted by severity, with the first entry used as the lead line. There is no engine-side "strongest negative factor" or `top_reason_text` synthesizer; the presentation layer does not request one.

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
    "episode_id": "ep_1805_austerlitz_betrayal_001",
    "severity": "high",
    "primary_surface": "dispatch_spotlight",
    "primary_nation": "Prussia",
    "secondary_nation": "France",
    "injured_party": "Prussia",
    "target_enemy": "Britain",
    "claim_region": "Hanover",
    "source_commitment_id": "commitment_12",
    "speaker_attribution": "envoy",
    "dominant_witness_scope": "ally",
    "aftermath_mode": "private_aside_required",
    "callback_window_end_turn": 25,
    "follow_up_actions": ["talk_talleyrand", "summon_envoy", "open_ledger"],
    "relation_delta": -12,
    "reliability_delta": -4,
    "witness_nations": [
        {"nation": "Austria", "scope_reason": "ally"},
    ],
    "hard_block_reason": None,
    "review_target": "ledger_commitments",
}
```

Required rules:

- all fields primitive-only
- no live object references
- no duplicate authority over commitment state
- `episode_id` is the episode-boundary key (see `RELIABILITY_COMMITMENTS_SPEC.md` §8.3); `C3` collapse, dedupe, and aftermath callback logic key off it (see §9.4 and §13)
- `witness_nations` entries carry `scope_reason in {"ally", "rival", "shared_enemy", "region_observer"}` per `RELIABILITY_COMMITMENTS_SPEC.md` §8.4
- `speaker_attribution in {"system", "talleyrand", "envoy", "foreign_office"}`
- `dominant_witness_scope` is optional; if omitted, presentation derives it deterministically from `witness_nations` using the precedence in §9.1
- `aftermath_mode in {"none", "private_aside_optional", "private_aside_required", "proposal_callback_required"}`
- `callback_window_end_turn` is presentation-only expiration data, never mechanic authority
- `follow_up_actions` entries are UI routing hints only; they may reference only existing no-cost advisory or inspection surfaces
- `relation_delta` / `reliability_delta` are sourced from strike record delta fields (produced by `C1a`) for breach / witness flows, or computed at emit time from `fulfillment_snapshot` (produced by `C1b`) for fulfillment flows
- for fulfillment flows, the payload additionally carries narrative-ready fields from the extended `fulfillment_snapshot` contract (`witness_nations_at_fulfillment`, `relation_delta`, `reliability_delta`) per `RELIABILITY_IMPLEMENTATION_PLAN.md` `C1b`
- `review_target: "ledger_commitments"` routes to the Treaties tab of the Diplomatic Ledger with a commitments section filter (see §9.3)

If a field is not known deterministically, omit it rather than improvising it in presentation.

---

## 12. Example Player Experience

### 12.1 Bargain fulfilled

Engine outcome:

- bargain moves to `fulfilled`
- relation and reliability rewards apply
- `fulfillment_snapshot` written (extended with `witness_nations_at_fulfillment`, `relation_delta`, `reliability_delta` per `RELIABILITY_IMPLEMENTATION_PLAN.md` `C1b`; these feed the spotlight template directly)

Player experience:

- turn-N spotlight frames it as France having kept its word
- optional N+1 callback or proposal echo keyed by `episode_id` reinforces that the remembered promise changed trust
- ledger marks the bargain as newly fulfilled
- campaign log records the durable event

Canonical mock spotlight template:

- Headline: `Word Kept in {primary_nation}`
- Speaker: `talleyrand`
- Body:

  "Sire, {primary_nation} has received exactly what we named, and Europe is now
  obliged to admit that France can still distinguish victory from oath.
  A promise honored after success purchases a rarer coin than gratitude:
  belief. They may not love us for it. They will calculate with us."

- Consequence line: `{primary_nation} relation {relation_delta:+}; reliability {reliability_delta:+}.`

Desired feeling:

- "This alliance meant something."

### 12.2 Bargain breached

Engine outcome:

- bargain moves to `breached`
- betrayal fallout applies
- witness strikes and injured-party deltas are available to presentation

Player experience:

- turn-N spotlight lands as a three-beat card:
  1. injured-party accusation
  2. one witness reaction based on `dominant_witness_scope`
  3. short private Talleyrand aside
- next-morning dispatch carries a private callback keyed by `episode_id`
- the injured party's next `incoming_proposal` or advisory scene may carry one barbed callback line inside the normal surface
- ledger and log preserve the exact fallout

Canonical mock spotlight template (ally-witness example):

- Headline: `Word Broken Before {injured_party}`
- Lead speaker: `envoy`
- Lead line:

  "{secondary_nation} gave its word on {claim_region}; today that word is spent
  elsewhere. {injured_party} will remember the price of trusting it."

- Witness line (`dominant_witness_scope = ally`):

  "Vienna notes that the pledge was given publicly and asks what, then, French
  assurances are worth."

- Private aside:

  "They are wounded, Sire. Worse, they are entitled to be. Force is often
  forgiven; ridicule is remembered."

- Next-morning callback:

  "Hardenberg has not forgotten {claim_region}, Sire. He need not mention it
  each morning for it to sit at table."

Desired feeling:

- "I traded future trust for this move."

### 12.3 Hard-reject posture triggered

Blocked on B2b emit contract (see §8.2 and `RELIABILITY_IMPLEMENTATION_PLAN.md` B2b add). Spotlight fires on the first threshold crossing per victim nation only.

Engine outcome:

- a nation reaches the strike threshold and will now hard-resist deep treaties

Player experience:

- one featured spotlight tells the player that this channel is effectively closing
- the next relevant preview / refusal reinforces that state
- the ledger makes it obvious that the posture is active

Canonical mock spotlight template:

- Headline: `The Chancery Shut`
- Speaker: `foreign_office`
- Body:

  "The {primary_nation} chancery no longer receives French dispatches on matters
  of alliance, guarantee, or common cause.
  Courtesies may continue. Trust will not."

- Consequence line: `{primary_nation} will hard-refuse deep treaty asks until posture cools.`
- Optional N+1 aside:

  "Doors in Europe rarely slam, Sire. They close with a servant's politeness
  and a statesman's memory."

Desired feeling:

- "That nation is not just numerically colder. They are diplomatically shut."

### 12.4 Ally-entry hard block

Engine outcome:

- ally cannot legally or plausibly join

Player experience:

- keep the main explanation inline at the ally-entry surface
- optionally raise a compact notice if a live bargain was implicated
- if the surface is already conversational, offer a no-cost `Ask Talleyrand why not` follow-up rather than a second dramatic card
- do not promote this into a dramatic dispatch unless it caused a larger downstream state change

Desired feeling:

- "I understand why this failed."

**Rendering contract:** ally-entry hard-block rendering consumes the `pending_declaration` payload per the C2 contract (see `RELIABILITY_IMPLEMENTATION_PLAN.md` C2). No duplicate authority is held here.

**Back Out semantics:** counter-bargain `Back Out` cancels the `pending_declaration` transaction; DP and AP spent to stage the declaration are refunded; the action is not re-entrant within the same turn. These semantics are owned by C2; `C3` only renders.

### 12.5 Commitment paradox

Engine outcome:

- ratification would span an active opposition pair
- the existing blocking hard-stop pauses resolution until the player chooses which promise survives

Player experience:

- a grave Talleyrand framing line lands before the choice
- the blocking body and options remain owned by the existing `commitment_paradox` dialogue contract in `CONVERSATIONAL_DIPLOMACY_DESIGN.md`
- after the player chooses, one short Talleyrand aside names the wound
- the next morning dispatch may carry one callback if a live court was spurned

Canonical framing template:

- Speaker: `talleyrand`
- Before-choice line:

  "Sire, we have arranged our promises so artfully that Europe now insists on
  arithmetic. If we ratify {primary_nation}, we break faith with
  {secondary_nation}. There is no language in which both vows remain true."

- After-choice aside:

  "We have preserved one promise by choosing which wound to open. Europe
  forgives necessity sooner than contradiction, but it will call this necessity
  ours."

- Next-turn callback:

  "{spurned_nation} has received the news with the composure of a court
  counting knives."

Desired feeling:

- "I had to choose which promise to betray, and the choice hurt."

### 12.6 Reactive affordances

Commitments surfaces may not leave the player as a reader only. `C3b` adds no-cost follow-ups that route into existing conversational or inspection surfaces.

Minimum quick actions:

| Action | Availability | Route | Mechanical effect |
|-----------|---------|---------------|---------------|
| `Speak to Talleyrand about this` | breach, fulfillment, hard-reject, paradox aftermath | opens scoped `advisory` dialogue with `context.origin_episode_id = episode_id` | none |
| `Summon the envoy` | breach spotlight only | opens a short court-response or advisory scene seeded by `episode_id` | none |
| `Review the pledge` | any commitments spotlight or paradox resolution | routes to the filtered Treaties tab / commitments section | none |

Rules:

- no DP or AP cost
- no relation, reliability, or commitment-state change
- dismissal creates no extra notice
- if a route is unavailable, hide the button rather than substituting invented prose

---

## 13. Anti-Spam Rules

- No more than 1 commitments dispatch spotlight per turn.
- No more than 2 above-the-fold commitments notices per turn.
- Blocking hard-stops suppress duplicate notice-generation for the same root event.
- Multiple witness strikes from one root event should collapse into one summarized presentation event when surfaced outside the ledger. Witness-collapse keys off `episode_id`, not event-type heuristics.
- A `bargain_triggered` notice should be suppressed if the same bargain is fulfilled or breached in the same turn and that higher-severity event is already surfaced.
- If a commitments event is unrelated to the current blocking popup, queue it into the normal notice/dispatch path instead of interrupting the player mid-resolution.
- No more than 1 aftermath callback may fire per `episode_id`, and no later callback may survive past turn `N+10`.
- Quick-action follow-ups do not generate their own notices if opened and dismissed without state change.

---

## 14. Proposed Implementation Slice

### C3a. Commitments presentation routing

**Files:** `backend/game_logic/dispatch.py`, `backend/game_logic/diplomatic_templates.py`, `backend/game_logic/diplomatic_dialogue.py`, `backend/game_logic/diplomatic_ledger.py`, `backend/campaign_log.py`, `backend/main.py`, `godot-client/project-sovereign/scripts/main.gd`, `godot-client/project-sovereign/scripts/diplomatic_ledger.gd`, `godot-client/project-sovereign/scripts/campaign_log.gd`, notice / dispatch surfaces already used by diplomacy

Core tasks:

- define commitments event routing rules across blocking / dispatch / notice / ledger
- add commitments-specific spotlight and notice templates under the `commitments_spotlight_*` / `commitments_notice_*` template family in `diplomatic_templates.py`
- enrich existing hard-stop copy for paradox and counter-bargain outcomes
- add ledger emphasis rules for recent fulfillment / breach and active hard-reject posture
- wire duplicate suppression so one event does not surface three times
- keep campaign-log summaries compact but more specific
- register new event types in `backend/campaign_log.py` `CAMPAIGN_LOG_TYPES`: `bargain_ratified`, `bargain_triggered`, `bargain_fulfilled`, `bargain_breached`, `bargain_voided`, `witness_strike_recorded`, `hard_reject_posture_triggered`, `declaration_backed_out` (8 types total, including the `declaration_backed_out` entry added for H-1 Back Out)

Suggested tests:

- spotlight priority ordering across multiple same-turn commitments events
- no duplicate notice after blocking counter-bargain resolution
- `bargain_triggered` suppression when same-turn `fulfilled`
- hard-reject posture gets one featured moment, not a repeated every-turn notice
- witness-strike collapse into one medium surface event
- save/load safety for any new transient surface payload
- mock-mode template coverage for all spotlight-worthy commitments events
- Back Out terminal: no "Ally refused" notice is generated; only a `declaration_backed_out` campaign log entry is emitted

Estimated budget:

- one focused session
- approximately 16-22 tests

### C3b. Commitments drama pass

**Files:** same surface/render files as `C3a`, plus any existing dialogue or dispatch renderer that already exposes speaker attribution or quick actions

Core tasks:

- commit canonical mock templates for `bargain_fulfilled`, `bargain_breached`, `hard_reject_posture_triggered`, and `commitment_paradox` framing / aftermath
- add player-facing period labels and voice-by-event-family mapping
- support split-voice breach spotlight and one lower-weight private aside line
- branch breach copy on `dominant_witness_scope`
- turn `episode_id` into a minimal memory hook for N+1 aftermath and one later callback
- add no-cost reactive affordances that route into existing advisory or ledger surfaces
- inject callback lines into the next relevant `incoming_proposal` or advisory surface without changing mechanics

Suggested tests:

- committed mock template renders for every spotlight family with required slots
- breach spotlight uses `envoy` lead, scope-branched witness line, and Talleyrand aside
- paradox shows grave framing before choice and after-choice callback after resolution
- `episode_id` schedules exactly one N+1 aside and no more than one later callback before expiry
- `hard_reject_posture_triggered` uses `foreign_office` or `system` voice and infects the next relevant refusal line
- quick actions open the correct no-cost surfaces and never alter DP/AP or relation state

Estimated budget:

- one focused narrative session plus verification
- approximately 12-18 tests

---

## 15. Future Handoff

This pass should hand off cleanly to later systems:

- `Bilateral Peace Hardening`
  - owns its own spotlight events for peace settlement theatrics; the `C3` router is commitments-specific and does not extend to peace fallout. Bilateral Peace Hardening may copy patterns from `C3`, but it does not reuse the `C3` router.
- `Talleyrand Desk + Explanation Layer`
  - can absorb the same commitments payloads into richer advisory surfaces later, but it does **not** own inventing the first breach/paradox aftermath beats from scratch. `C3b` already commits the minimum callback and follow-up architecture.
- generalized coalition work
  - may later reuse the same spotlight principles for bloc pressure and split events

This spec should **not** pre-own those future systems.

Its job is narrower:

- make the current commitments layer feel alive
- without dragging later systems forward prematurely

What is no longer deferred:

- committed spotlight prose for the four core families
- breach accusation / witness / private-aside sequencing
- period labels and voice mapping
- minimal aftermath memory keyed by `episode_id`
- no-cost reactive affordances

---

## 16. Acceptance Criteria

`C3a` is successful if:

- a player can tell the difference between routine diplomacy bookkeeping and a major commitments moment
- bargain fulfillment and breach feel materially different in presentation weight
- hard-reject posture feels like a diplomatic state change, not just an invisible threshold
- witness fallout is legible without becoming spam
- all of the above work identically in mock mode without LLM dependency
- no commitments presentation surface changes any underlying outcome

`C3b` is successful if:

- each spotlight-worthy commitments family ships with a committed mock template
- `bargain_breached` lands as accusation + scoped witness reaction + next-turn private aside
- `commitment_paradox` has a before / during / after arc with grave Talleyrand framing
- player-facing labels read as political drama rather than engineering nouns
- `episode_id` supports one aftermath callback, so major moments linger beyond the origin turn
- at least one no-cost conversational follow-up exists on breach spotlights
- no commitments presentation surface changes any underlying outcome

Full `C3` sign-off requires both slices.

---

## 17. Changelog

- **Apr 15, 2026** - folded audit findings C-1..C-2, H-1..H-4, M-1..M-5, NEW-S1..S4, NEW-E1..E5, NEW-V1..V4 per `COMMITMENTS_PRESENTATION_AUDIT_FINDINGS.md`.
- **Apr 15, 2026** - split `C3` into `C3a` routing and `C3b` drama, and folded designer-eye audit findings F1-F8 per `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md`.
