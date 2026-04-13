# Reliability + Commitments Spec

> **Status:** Draft v0.3
> **Date:** April 12, 2026
> **Queue Position:** Design Refinement item 1
> **Collapses:** `R160` + `R119` + `R151`
> **Companion:** `docs/DESIGN_REFINEMENT.md`

---

## 1. Purpose

This spec turns three loosely related diplomacy ideas into one political-commitment system:

1. Rivalries should force strategic choice instead of allowing universal friendship.
2. Nations should remember betrayal in a way that matters mechanically and politically.
3. Territorial promises should create real obligations, not just flavor or a one-off acceptance bonus.

The current diplomacy foundation is stable enough to support this now:

- Envoys inbox / same-turn lapse / typed response flows are live.
- Backend-owned proposal labels are live.
- The current diplomacy engine already has treaty history, diplomatic history, and a thin reliability mechanic.

What is still missing is political memory. Nations can currently react to the present offer, but they do not yet react strongly enough to what France has promised, broken, or implicitly chosen.

---

## 2. Problems To Solve

### P1. Universal friendship is too easy

France can drift toward broad friendship without being forced to choose camps. That makes diplomacy feel additive instead of political.

### P2. Betrayal memory is too shallow

Breaking a treaty hurts in the moment, but there is not enough long-tail memory at either the bilateral or world-reputation level.

### P3. Promises have no durable weight

The game can talk about protection or strategic interests, but it cannot yet say:

- "Help us gain Saxony and we will align with you."
- "You promised us Bavaria and then kept it."

Without that, diplomacy lacks obligation and therefore lacks legitimacy.

---

## 3. Goals

- Make alliances politically costly rather than purely additive.
- Separate "the world thinks France keeps its word" from "this nation thinks France betrayed it."
- Let promises shape AI target choice, treaty interest, and post-war fallout.
- Reuse existing diplomacy surfaces: ledger, dispatch, mailbox, proposal preview, treaty ratification.
- Keep the first implementation legible on the 19-region map.

## 4. Non-Goals

- This spec does **not** redesign war goals, ticking war score, or peace settlement logic. That belongs to `War Purpose + Settlement`.
- This spec does **not** add a new diplomacy screen family. It extends existing ledger / popup / dispatch surfaces.
- This spec does **not** create a full EU4-style claims/favors system with dozens of currencies.

---

## 5. Design Principle

Political commitments should have three layers:

1. **Rivalry pressure**
   Nations care who you align with.
2. **Reliability memory**
   Nations care whether you keep your word.
3. **Tracked obligations**
   Nations care whether a specific promise was fulfilled.

These are connected but not identical:

- Rivalry creates the reason a promise matters.
- Reliability determines whether the target believes the promise.
- Fulfilled or broken obligations feed betrayal memory and world reputation.

---

## 6. System Overview

The commitment system has four data concepts.

### 6.1 Global reliability

This is the existing high-level reputation layer: "Does France generally honor agreements?"

- Current code already behaves as if this is nation-keyed, while older save-format text still describes it as pair-keyed.
- This spec resolves that mismatch in favor of **nation-keyed global reputation**.
- Keep `world.diplomatic_reliability` as the global, nation-keyed reputation score.
- Clarify it as **nation reputation**, not pair memory.
- Use it for broad acceptance modifiers and Talleyrand-facing reputation summaries.

### 6.2 Bilateral betrayal memory

This is target-specific memory: "What did France do to us?"

- Add `world.betrayal_history`.
- Directional key: `from_nation|to_nation`.
- Tracks repeated offenses, last offense turn, offense categories, and witness impact.

### 6.3 Rivalries

This is the political-pressure layer: "Who does this nation define itself against?"

- Add `world.nation_rivalries`.
- Pair key: `diplo_key`.
- Tracks source (`historical` or `dynamic`), intensity, and start turn.

### 6.4 Active commitments

This is the obligation layer: "What has been promised and what is still owed?"

- Add `world.diplomatic_commitments`.
- Each entry is a tracked obligation with identity, owner, beneficiary, subject, deadline, and status.

---

## 7. Rivalry System

### 7.1 Starting rivalries

The initial set should be small and legible.

| Pair | Type | Why |
|------|------|-----|
| France <-> Britain | Primary | Core geopolitical enemy pair |
| Prussia <-> Austria | Primary | German hegemony conflict |
| Prussia <-> Saxony | Secondary | Expansion pressure / annexation fear |

Notes:

- France/Britain rivalry should make alliance possible only under unusually favorable circumstances, not literally impossible.
- Prussia/Austria is the key anti-universal-friendship rivalry on the current map.
- Suggested starting levels for v0.1:
  - France <-> Britain: `active`
  - Prussia <-> Austria: `active`
  - Prussia <-> Saxony: `cold`

### 7.2 Dynamic rivalry formation

Dynamic rivalry formation is a valid future extension, but it is **not part of the first implementation pass**.

v0.1 ships with the static starting rivalries only. Dynamic formation moves to Slice D or later after the static system is playtested.

A dynamic rivalry may form when all are true:

- relation <= -40
- not already direct allies or vassal-linked
- either border friction exists or one nation repeatedly aligns with the other's rival

Suggested triggers:

- repeated wars between the pair
- treaty break followed by rearmament
- France allies one member of an active rival pair, angering the other repeatedly

Design note:

- deferring this avoids edge-case-heavy emergent politics before the base rivalry pressures are proven fun on the 19-region map

### 7.3 Rivalry intensity

Use a simple 2-step intensity model for v0.1.

| Intensity | Meaning | Default effects |
|-----------|---------|-----------------|
| `cold` | Political friction | proposal friction, mild anger, background alignment pressure |
| `active` | Live geopolitical conflict | large acceptance malus for deep treaties, strong third-party reactions, paradox checks on deep military alignment |

For v0.1:

- rivalry levels are authored, not dynamically escalated
- static rivalries may decay if conditions soften
- dynamic escalation can be added later with the broader AI-agenda work

### 7.4 Rivalry effects on diplomacy

Rivalry should create pressure in two ways.

#### A. Direct rivalry friction

Trying to deepen treaties with a direct rival applies acceptance penalties:

- `PEACE`: no extra block beyond normal relation / war logic
- `OPEN_BORDERS`: mild malus
- `NON_AGGRESSION`: moderate malus
- `DEFENSIVE_ALLIANCE` / `ALLIANCE`: strong malus, especially for `active` rivalries

This keeps "peace with Britain" viable while making "Britain becomes your best friend" structurally rare.

Primary-rival rule:

- France-Britain is a **soft cap**, not a hard prohibition.
- A France-Britain alliance should remain theoretically possible through extraordinary stacked circumstances.
- In practice, primary rivalry should impose an extremely large alliance malus rather than a literal hard block.

#### B. Third-party commitment pressure

When France deepens ties with Nation A, each active rival of A reacts.

Suggested base anger by new treaty level:

| New state with A | Rival reaction |
|------------------|----------------|
| `OPEN_BORDERS` | -5 relation |
| `NON_AGGRESSION` | -10 relation |
| `DEFENSIVE_ALLIANCE` | -15 relation + advisory warning |
| `ALLIANCE` | -20 relation + possible forced-choice flow |

### 7.5 Military alignment paradox

Deep military commitments should not silently coexist across the same active rival pair.

Rule:

- France may not silently hold `DEFENSIVE_ALLIANCE` or `ALLIANCE` with both sides of the same active rivalry pair.

The paradox check runs on **ratification**, regardless of who proposed the treaty:

- outbound: player proposal accepted and about to ratify
- inbound: AI proposal accepted by the player and about to ratify

When ratification would create that state:

- do **not** silently reject
- do **not** silently allow
- instead open a typed "commitment paradox" decision

Player options:

1. Reject the new treaty
2. Auto-downgrade the old military alignment
3. Proceed at severe political cost if the design review decides this should be allowed

Draft default for v0.1:

- `DEFENSIVE_ALLIANCE` / `ALLIANCE` across active rivals should force a choice rather than coexist.
- Lower treaty levels may coexist, but they still anger the excluded rival.

### 7.6 Rivalry decay and resolution

Rivalry should not be permanent if political conditions change.

Decay rules:

- shared war against a common enemy reduces intensity slowly
- long peaceful coexistence with no border friction reduces intensity slowly
- fulfilled territorial promises to one rival against another can harden rivalry instead of softening it

Minimum decay model:

- every 5 quiet turns, `active` may soften to `cold` if relation is positive and no recent betrayal exists
- after a longer stable period, `cold` may clear entirely

---

## 8. Reliability And Betrayal

### 8.1 Split the memory cleanly

The spec should distinguish:

- **Global reliability**: "France is known to keep or break agreements."
- **Bilateral betrayal memory**: "Austria specifically remembers France betrayed Austria."

This avoids overloading one score with two different jobs.

### 8.2 Offense categories

Tracked betrayal categories:

- breaking treaty voluntarily
- breaking non-aggression with rapid war follow-up
- breaking alliance / defensive alliance
- failing territorial promise
- aligning militarily with a rival after prior exclusivity pressure

### 8.3 Penalty model

Use both a direct victim penalty and a tightly scoped witness penalty.

| Event | Global reliability | Victim memory | Witness memory |
|------|--------------------|---------------|----------------|
| Break `OPEN_BORDERS` / `PEACE`-level commitment | -4 | +1 strike | minor |
| Break `NON_AGGRESSION` | -6 | +1 strike | minor |
| Break `DEFENSIVE_ALLIANCE` / `ALLIANCE` | -10 | +2 strikes | moderate |
| Break territorial promise | -6 | +1 strike | conditional |
| Break promise to aid against rival, then align with rival | -10 | +2 strikes | strong for involved rivals |

Witness penalties apply only to directly interested observers:

- nations with `DEFENSIVE_ALLIANCE` or `ALLIANCE` with the victim
- nations with an active rivalry against the betrayer

Everyone else gets zero witness effect. The system should not apply broad "half penalty for uninvolved observers" noise.

### 8.4 Redemption

Redemption should be possible, but it cannot be so slow that one mid-game betrayal effectively poisons the whole campaign.

Suggested rules:

- every 5 honored treaty turns: +3 to global reliability
- each fulfilled tracked promise: +4 to global reliability
- after 8 honorable turns with a nation and no new offense: remove 1 bilateral strike against that nation
- fulfilling a commitment owed to a victim clears 1 bilateral strike immediately
- joining a victim's defensive war and remaining co-belligerent for 3 turns clears 1 bilateral strike

Caps / guardrails:

- active redemption effects can clear at most 1 strike per source event
- no nation may lose more than 1 bilateral strike per turn from passive decay
- global reliability still caps at the existing maximum

This keeps betrayal meaningful without making it structurally irrecoverable in a short campaign.

### 8.5 Hard-reject behavior

Repeated betrayal should eventually change AI posture, not just shave numbers.

Draft rule:

- 3 active bilateral strikes from France toward Nation X causes AI hard resistance to deep treaties with X
- exceptions allowed only for existential survival, coalition emergency, or very favorable war position

That means:

- peace may still be possible
- alliance should become structurally difficult

---

## 9. Territorial Promise System

### 9.1 Promise initiation model

For v0.1, territorial promises are **AI-requested and player-confirmed**, not player-authored from scratch.

That means:

- AI may include `territorial_promise` in an incoming treaty package
- the player may accept or reject that package
- the player may later renegotiate an accepted promise
- the player does **not** get a new outbound region-picker flow in the diplomacy wizard yet

This keeps the core obligation loop while deferring new promise-authoring UI work.

### 9.2 New clause

Add a new clause type:

- `territorial_promise`

Meaning:

- France promises to help the target obtain control of a specified region or claim package later.
- This is an obligation, not immediate cession.

### 9.3 Valid promise targets

To keep the first version legible, a territorial promise must be tied to an existing strategic interest.

A promise is valid only if one of these is true:

- the target nation explicitly covets the region
- the region belongs to the target's active rival
- the region is adjacent to the target's current territory

Invalid use cases:

- random inland gifting with no strategic logic
- promising territory France can neither contest nor influence

### 9.4 Promise scope

Default v0.1 scope:

- one promise package per treaty
- one claim package may contain 1-2 regions at most
- the UI should name the exact regions

This keeps Saxony / Dresden type cases possible without opening the door to giant map-spanning barter.

### 9.5 Promise lifecycle

On treaty ratification, create a tracked commitment:

```json
{
  "id": 17,
  "type": "territorial_promise",
  "promiser": "France",
  "beneficiary": "Prussia",
  "regions": ["Saxony"],
  "rival_nation": "Saxony",
  "created_turn": 8,
  "deadline_turn": 18,
  "status": "active",
  "source_treaty": "alliance",
  "source_pair": "France|Prussia"
}
```

Deadline source for v0.1:

- the AI sets the deadline when proposing the promise
- the deadline must be visible before the player accepts
- the deadline uses a bounded urgency window:
  - floor: 8 turns
  - ceiling: 15 turns
- deadline length is not separately negotiable in v0.1

Coalition / war interaction:

- coalition membership does **not** void an active promise
- if promiser and beneficiary enter direct war, the deadline clock suspends while that war lasts
- when peace resumes, the promise clock continues from where it stopped
- suspension is not a free erase: if the promiser ratifies terms favoring the rival claimant against the beneficiary during suspension, treat that as bad-faith breach

### 9.6 Fulfillment

A territorial promise is fulfilled if, by the deadline:

- the beneficiary controls the promised region, and
- that control was achieved through conquest, treaty cession, vassal release, or allied war settlement in which France materially participated

Minimum v0.1 simplification:

- if beneficiary controls the promised region by deadline and France was allied / aligned through the relevant war window, count as fulfilled

### 9.7 Failure

A promise fails if:

- deadline expires with no fulfillment, or
- France signs a settlement that blocks fulfillment, or
- France aligns with the rival holder instead

Failure effects:

- relation penalty with beneficiary
- betrayal strike against France -> beneficiary
- global reliability loss
- possible rivalry escalation between beneficiary and the favored rival

### 9.8 Renegotiation

Before failure resolves, the promise owner should be able to renegotiate.

Allowed v0.1 flow:

- renegotiation is player-initiated
- it uses a standard `HARD_STOP` dialogue flow
- it offers two concrete branches:
  - downgrade the promise scope
  - cancel the promise with light penalty
- AI may refuse a downgrade request
- if the AI refuses, the original promise remains active and the clock continues
- successful renegotiation must be cheaper than outright failure

Draft v0.3 default:

- renegotiation exists
- compensation currencies beyond territory remain deferred
- if the beneficiary accepts renegotiation, apply a light trust cost instead of full betrayal:
  - small relation hit
  - small global reliability hit
  - no bilateral betrayal strike
- full betrayal applies only on hard failure or bad-faith reversal

### 9.9 Promise urgency warnings

Tracked promises must warn the player before failure becomes unavoidable.

Required warning points:

- when 50% of the deadline window has elapsed
- when 75% of the deadline window has elapsed
- final urgent warning when 3 turns or fewer remain

These warnings should surface through Morning Dispatch and, if needed, the Talleyrand / commitments ledger summary.

---

## 10. Acceptance Formula Hooks

This spec needs four acceptance inputs.

### 10.1 Direct rivalry modifier

- negative when proposing deeper treaties to a direct rival
- should be in the same order of magnitude as the relation modifier
- should be capable of swinging a deep-treaty outcome on its own for `active` rivalries

### 10.2 Rival-commitment conflict modifier

- negative when the target knows France is already aligned with its rival
- should be a major penalty on military treaties, not a cosmetic nudge
- should stack with direct rivalry pressure but not make lower-tier treaties impossible by default

### 10.3 Bilateral betrayal modifier

- negative based on active strikes from proposer toward target
- stronger than global reliability
- should be at least roughly 2x the practical weight of global reliability at equivalent severity
- three active strikes should not be cleanly overcome by a single promise-value bump

### 10.4 Promise-value modifier

- positive when the offer includes a territorial promise matching the target's strategic interest
- should be meaningful enough to change AI behavior and make offers feel politically real
- should **not** be strong enough to erase deep bilateral distrust by itself

Priority note:

- bilateral betrayal should outweigh generic reputation
- a good promise from an unreliable promiser should still be discounted

---

## 11. AI Behavior

### 11.1 Proposal generation

AI should use rivalries to create branches:

- court France against their rival
- ask for exclusivity against rival before deep alliance
- offer or request territorial promises tied to active claims

### 11.2 Refusal behavior

AI should refuse or resist:

- deep alliance while France is already militarily aligned with the AI's rival
- new promises from a promiser with severe betrayal memory

### 11.3 Escalation behavior

If France repeatedly angers a rival through opposite-camp alignment:

- AI may downgrade
- AI may issue warning-style proposals
- AI may pivot from diplomatic courtship toward hostility

### 11.4 Performance / architecture guard

No new hot-path per-region scans.

Use:

- cached nation-region helpers
- cached rivalry lookups per turn
- direct pair-key access for betrayal and commitment reads

This follows the current scale rule in `CLAUDE.md`.

---

## 12. Player-Facing Surfaces

### 12.1 Diplomatic Ledger

Add to Nations / Talleyrand tabs:

- each nation's active rivals
- France's global reliability descriptor
- bilateral betrayal warning if that nation distrusts France specifically
- active commitments owed to or from that nation

### 12.2 Proposal preview / Talleyrand advisory

Before ratification, Talleyrand should warn:

- "This will anger Austria."
- "Prussia will not trust another territorial promise lightly."
- "We cannot bind both rivals without choosing."

### 12.3 Treaty display

Active treaties tab should surface:

- tracked territorial promises
- deadline turns remaining
- current fulfillment status

### 12.4 Dispatch and campaign log

High-signal events only:

- rivalry escalates
- promise fulfilled
- promise broken
- promise deadline warning at 50% / 75% / final 3 turns
- France's reliability improved or worsened meaningfully

No per-turn spam.

---

## 13. Data Model Draft

### 13.1 Keep and clarify

- `diplomatic_reliability: Dict[str, int]`
  - nation-keyed global reputation

### 13.2 Add

- `betrayal_history: Dict[str, Dict]`
  - key: `from|to`
  - value: `{strikes, categories, last_turn, decays_on_turn}`
  - serialization note: keep this as a plain directional string key store; do not overload or auto-normalize it into the bilateral `diplo_key` format used by treaties and state lookups

- `nation_rivalries: Dict[str, Dict]`
  - key: `diplo_key`
  - value: `{intensity, source, started_turn, last_changed_turn}`

- `diplomatic_commitments: Dict[str, Dict]`
  - key: commitment id or string id
  - value: tracked promise / exclusivity record

- `next_commitment_id: int`

### 13.3 Optional later

- `claim_map` or `nation_claims`

Do **not** add full claims in v0.1 unless implementation proves they are required. Existing nation desire profiles may be enough for the first pass.

---

## 14. Implementation Sequence

### Slice A. Foundations

- clarify `diplomatic_reliability` as nation-level reputation
- add bilateral betrayal memory store
- add rivalry store
- surface both in ledger / debug output

### Slice B. Rivalry pressure

- direct rivalry acceptance modifier
- third-party anger on treaty deepening
- commitment paradox flow for `DEFENSIVE_ALLIANCE` / `ALLIANCE`
- implement paradox as a standard `HARD_STOP` dialogue through the existing `dialogue_manager` taxonomy, not as a new parallel flow

### Slice C. Territorial promises

- clause type
- tracked commitment creation
- fulfillment / failure processing
- urgency warnings and renegotiation penalties
- advisory + ledger surfacing

### Slice D. AI integration

- optional dynamic rivalry formation
- rival-aware proposals
- betrayal-aware refusals
- promise-aware alliance offers

---

## 15. Risks

### R1. Over-hard locking

If rivalry becomes a pure binary ban too early, diplomacy may feel scripted instead of political.

Mitigation:

- keep lower treaty levels flexible
- force choices only on deep military commitments

### R2. Promise ambiguity

If promise fulfillment is vague, players will feel cheated.

Mitigation:

- exact regions
- exact deadline
- exact status text

### R3. Memory overload

If too many invisible counters accumulate, the system becomes opaque.

Mitigation:

- expose rivalry, reliability, and owed commitments in the ledger
- keep betrayal categories small

### R4. Coalition interaction ambiguity

The core diplomatic drama on the 19-region map already runs through coalition formation and anti-France alignment. If commitment rules and coalition rules disagree, implementation will drift.

Mitigation:

- coalition membership does not erase promises
- direct war with the beneficiary suspends the promise deadline clock
- suspension semantics belong in the promise lifecycle, not as an ad hoc runtime exception
- bad-faith settlement in favor of the rival claimant during suspension still counts as breach

---

## 16. Open Gates For Design Review

These are the main questions worth pressure-testing with Claude.

1. Should rival military alignments be a hard forced-choice system, or a soft but severe penalty system?
2. Is the split of global reliability + bilateral betrayal memory the right structure, or should both be pair-specific?
3. What exact light-cost package should accepted renegotiation apply: relation only, reliability only, or both?

---

## 17. Draft Recommendation

For the first implementation pass:

- keep global reliability
- add bilateral betrayal memory
- add explicit rivalries with intensity
- force a choice only for deep military alignment across active rivals
- implement territorial promises as tracked obligations with exact deadlines

That is enough to make diplomacy feel political without bundling in the full war-settlement overhaul too early.
