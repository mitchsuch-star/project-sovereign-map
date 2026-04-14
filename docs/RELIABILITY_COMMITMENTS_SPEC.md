# Reliability + Commitments Spec

> **Status:** Draft v0.7
> **Date:** April 13, 2026
> **Queue Position:** Design Refinement item 1
> **Collapses:** `R160` + `R119` + `R151`
> **Companion:** `docs/DESIGN_REFINEMENT.md`

---

## 1. Purpose

This spec defines the narrowed v0.1 political-commitment layer:

1. Rivalries should force side-picking instead of allowing universal friendship.
2. Nations should remember betrayal in a way that changes both numbers and posture.
3. Promises should create real political leverage without demanding settlement machinery the game does not yet have.

The key scope correction from earlier drafts:

- v0.1 does **not** ship timed territorial-delivery promises to allies.
- v0.1 does ship **war bargains**: explicit named-enemy commitments used to secure alliance depth or war entry in exchange for French claim priority.
- Ally-beneficiary land promises, common peace, conference settlement, and contribution-weighted spoils remain deferred.

This keeps the part that creates agency and cuts the part that produced obligation without control.

---

## 2. Problems To Solve

### P1. Universal friendship is too easy

France can still drift toward broad friendship unless rivals punish opposite-camp alignment hard enough to force tradeoffs.

### P2. Betrayal memory is too shallow

Breaking a treaty hurts in the moment, but the game still lacks enough durable bilateral memory to make repeated bad faith structurally costly.

### P3. The previous promise model asked the player to guarantee outcomes they could not directly produce

The old "promise an ally they will get Region X by turn N" structure was not acceptable for v0.1 because:

- France cannot yet run ally-aware settlement.
- France cannot force the ally AI to pursue the promised region.
- deadline pressure created timer anxiety rather than political drama.

### P4. Promise logic must create agency, not homework

If promises exist in v0.1, they need to be about things France can actually do:

- choose a side
- orient an alliance against a named enemy
- bring an ally into war
- hold or renounce France's own territorial claim

---

## 3. Goals

- Make alliances politically costly rather than purely additive.
- Separate "France is generally reliable" from "this nation thinks France betrayed it."
- Add a first-pass promise mechanic that improves war-entry politics without requiring common peace.
- Keep rules machine-readable enough for AI and tests.
- Keep the first implementation legible on the current 5-nation / 19-region map.

---

## 4. Non-Goals

- This spec does **not** redesign war goals, ticking war score, or peace settlement logic.
- This spec does **not** add common peace, ally beneficiaries, or conference-style spoils allocation.
- This spec does **not** promise allies they will receive territory France cannot directly allocate yet.
- This spec does **not** add dynamic power tiers, bloc pressure, or strategic focus in v0.1.
- This spec does **not** add a new diplomacy screen family; it extends existing wizard / popup / ledger / dispatch surfaces.

---

## 5. Design Principle

Political commitments in v0.1 should have four layers:

1. **Rivalry pressure**
   Nations care who France aligns with.
2. **Reliability memory**
   Nations care whether France generally keeps its word.
3. **Bilateral betrayal memory**
   Nations care what France did to them specifically.
4. **War bargains**
   Nations can trade deeper alignment and future war support for a clear French political line.

The rule that governs this whole spec:

- only punish the player for outcomes France could actually shape

That means:

- no timer-based ally-land promises
- no suspension mini-system
- no invisible contradictory obligations
- no breach states triggered by AI inactivity alone

---

## 6. System Overview

The commitment system has four data concepts.

### 6.1 Global reliability

This is the existing high-level reputation layer: "Does France generally honor agreements?"

- Keep `world.diplomatic_reliability` as nation-keyed global reputation.
- Clarify it as nation reputation, not pair memory.
- Use it for broad acceptance modifiers and ledger summaries.

### 6.2 Bilateral betrayal memory

This is target-specific memory: "What did France do to us?"

- Add `world.betrayal_history`.
- Directional key: `from_nation|to_nation`.
- Track repeated offenses, offense categories, last offense turn, and decay schedule.

### 6.3 Rivalries

This is the camp-pressure layer: "Who does this nation define itself against?"

- Add `world.nation_rivalries`.
- Pair key: `diplo_key`.
- Track `intensity`, `source`, `weight`, and start / change turns.

### 6.4 War bargains

This is the v0.1 promise layer: "France and Nation A align against Nation B, and Nation A recognizes France's priority claim to Region X."

- Add `world.diplomatic_commitments`.
- v0.1 bargain commitments are always:
  - nation-scoped
  - named-enemy scoped
  - single-region scoped
  - France-claim scoped
- Ally-beneficiary territorial guarantees remain deferred to the later settlement spec.

---

## 7. Rivalry System

### 7.1 Starting rivalries

The initial set stays small and legible.

| Pair | Weight | Intensity | Why |
|------|--------|-----------|-----|
| France <-> Britain | `primary` | `active` | Core geopolitical enemy pair |
| Prussia <-> Austria | `primary` | `active` | German hegemony conflict |
| Prussia <-> Saxony | `secondary` | `cold` | Expansion pressure / annexation fear |

Notes:

- France/Britain should be structurally rare at deep alliance, not literally impossible.
- Prussia/Austria remains the key anti-universal-friendship fork on the current map.
- Prussia/Saxony starts visible but weaker.

Prussia-Saxony special-case escalation for v0.1:

- if Prussia and Saxony enter direct war -> escalate to `active`
- if France vassalizes Saxony -> escalate to `active`

These are still explicit authored checks, not a general dynamic-rivalry system.

### 7.2 Dynamic rivalry formation

Dynamic rivalry formation remains deferred.

v0.1 ships with:

- the static starting rivalries
- the two Prussia-Saxony escalation triggers above

General emergent rivalry formation moves to later AI-agenda work.

### 7.3 Rivalry intensity

Use a simple 2-step model.

| Weight / Intensity | Meaning | Direct treaty effects |
|--------------------|---------|-----------------------|
| `secondary + cold` | low but visible friction | `OPEN_BORDERS` -4, `NON_AGGRESSION` -6, deep treaties -12 |
| `secondary + active` | live regional rivalry | `OPEN_BORDERS` -5, `NON_AGGRESSION` -10, deep treaties -20 |
| `primary + active` | major geopolitical rivalry | `OPEN_BORDERS` -6, `NON_AGGRESSION` -12, deep treaties -30 |

Rules:

- `cold` rivalries never trigger paradox by themselves.
- `active` rivalries trigger paradox checks on deep military alignment.
- primary rivalry is what makes France-Britain alliance "extraordinary but possible" rather than merely uncommon.

### 7.4 Rivalry effects on diplomacy

Rivalry creates pressure in two ways.

#### A. Direct rivalry friction

Trying to deepen treaties with a direct rival applies acceptance penalties using the table above.

This keeps:

- peace with rivals possible
- lower-friction diplomacy possible
- deep military friendship across major rival lines structurally rare

#### B. Third-party commitment pressure

When France deepens ties with Nation A, each rival of A reacts.

Suggested base anger for `active` rivalries:

| New state with A | Rival reaction |
|------------------|----------------|
| `OPEN_BORDERS` | -5 relation |
| `NON_AGGRESSION` | -10 relation |
| `DEFENSIVE_ALLIANCE` | -15 relation + advisory warning |
| `ALLIANCE` | -20 relation + possible forced-choice flow |

Rules:

- if the offended nation is only a `cold` rival of A, apply half values rounded toward zero
- on a ratified side-taking action, Nation A gains `they_chose_us = +8` relation with France once per event
- `they_chose_us` may trigger from:
  - deep treaty ratification with a rival-marked nation
  - ratification of a war bargain against a named rival

This is intentionally stronger than the old `+5` because the punishment side was drowning out the reward loop.

#### C. Great-power bloc pressure

Deferred. Do not add a separate bloc-pressure layer in v0.1.

The v0.1 side-picking package is:

- direct rivalry penalties
- third-party anger
- bilateral betrayal memory
- commitment paradox
- war bargains

### 7.5 Commitment paradox

Deep military commitments may not silently span both sides of the same `active` rivalry pair.

Rule:

- France may not hold `DEFENSIVE_ALLIANCE` or `ALLIANCE` with both sides of the same `active` rivalry pair.

The paradox check runs on ratification, regardless of who proposed the treaty.

Player options in v0.1:

1. Reject the new treaty
2. Auto-downgrade the old military alignment

Rules:

- no silent rejection
- no silent coexistence
- no "proceed at cost" exception in v0.1

Implementation note:

- this is a new sibling flow to the existing `alliance_paradox`
- do not overload the current war-declaration paradox

### 7.6 Rivalry decay and resolution

Deferred except for the two Prussia-Saxony escalation triggers.

Primary rivalries stay sticky in v0.1. Broader thaw / decay rules can return later.

---

## 8. Reliability And Betrayal

### 8.1 Split the memory cleanly

The spec distinguishes:

- global reliability: "France is known to keep or break agreements"
- bilateral betrayal memory: "Austria specifically remembers France betrayed Austria"

These are different jobs and should stay separate.

### 8.2 Offense categories

Tracked betrayal categories in v0.1:

- breaking treaty voluntarily
- breaking non-aggression with rapid war follow-up
- breaking alliance / defensive alliance
- explicit reversal of an active war bargain
- ratifying contradictory deep alignment after prior exclusivity pressure

Removed from v0.1:

- timer-based failure for ally-land promises
- suspension-based promise expiry
- passive failure caused only by AI inactivity

### 8.3 Penalty model

Use both direct victim penalties and tightly scoped witness penalties.

| Event | Global reliability | Victim strikes | Witness effect |
|------|--------------------|----------------|----------------|
| Break `OPEN_BORDERS` / `PEACE`-level commitment | -4 | +1 | minor |
| Break `NON_AGGRESSION` | -6 | +1 | minor |
| Break `DEFENSIVE_ALLIANCE` / `ALLIANCE` | -10 | +2 | moderate |
| Explicitly reverse an active war bargain without also breaking the source military treaty | -6 | +1 | conditional |
| Accepted bargain cancellation | -3 | +0 | none |

Critical episode-cap rule:

- one diplomatic episode may add at most **2 victim-side strikes total**

That means:

- if France breaks an alliance and an attached war bargain collapses in the same resolution step, relation and reliability penalties may stack
- victim-side strike gain may **not** exceed +2 from that single episode

This keeps the 3-strike hard-resistance threshold from becoming a one-click diplomatic death sentence on a 5-nation map.

### 8.4 Witness scoping

Witness penalties apply only to directly interested observers:

- nations with `DEFENSIVE_ALLIANCE` or `ALLIANCE` with the victim
- nations with an active rivalry against the betrayer
- nations with an active bargain or claim-recognition state directly implicated by the same target enemy or same region

Everyone else gets zero witness effect.

Witnesses do **not** receive victim-grade strikes in v0.1.

### 8.5 Faithful-play rewards

The system must reward sustained committed play, not only punish betrayal.

For v0.1:

- `they_chose_us = +8` on visible side-taking or bargain ratification
- fulfilled bargain: +4 global reliability and +6 relation with the beneficiary
- clear preview / ledger surfacing so loyalty feels intentional rather than invisible

Do **not** add a dedicated `trusted_partner` state in v0.1.

### 8.6 Redemption

Redemption remains possible, but stays simple.

Suggested rules:

- every 5 honored treaty turns: +3 global reliability
- each fulfilled bargain: +4 global reliability
- after honorable turns with a nation and no new offense, remove 1 bilateral strike using severity-scaled decay:
  - 6 turns: `OPEN_BORDERS` / `PEACE`-level break
  - 8 turns: `NON_AGGRESSION` break
  - 10 turns: `DEFENSIVE_ALLIANCE` / `ALLIANCE` break
  - 10 turns: explicit bargain reversal

Guardrails:

- passive decay clears at most 1 strike per nation per turn
- no special co-belligerence redemption hook in v0.1

### 8.7 Hard-reject behavior

Repeated betrayal must eventually change AI posture.

Rule:

- 3 active bilateral strikes from France toward Nation X causes AI hard resistance to deep treaties with X

Rules:

- witness suspicion alone never triggers this threshold
- survival / coalition-emergency exceptions must still exist
- one episode cannot add more than 2 strikes, per 8.3

This keeps the threshold meaningful without letting one compound event instantly create 4 strikes.

---

## 9. War Bargain System

### 9.1 Role in v0.1

The v0.1 promise mechanic is **not** "France guarantees an ally will receive territory by a deadline."

The v0.1 promise mechanic **is**:

- a named-enemy political bargain
- used to secure deeper alignment or war entry
- tied to a single French territorial objective

Example:

- "Prussia will align with France against Britain, and Prussia recognizes France's priority claim to Hanover."

This creates agency because France can actually:

- choose the ally
- choose the enemy
- choose whether to go to war
- choose whether to maintain the alliance
- choose whether to renounce or reverse the claim

Ally-beneficiary land promises remain deferred until the later settlement track exists.

### 9.2 Clause type

Add a new clause type:

- `war_bargain`

Meaning in v0.1:

- France and the target nation align against a named enemy
- the target nation recognizes France's priority claim to exactly one region held by that enemy
- if war against that enemy happens while the bargain is live, the bargain should materially improve French ability to bring that ally in

Player-facing phrasing should emphasize:

- alliance orientation
- named enemy
- French claim priority

Example:

- "Alliance against Britain; Prussia recognizes France's priority claim to Hanover."

### 9.3 Authoring model

Unlike the older territorial-promise draft, v0.1 war bargains may be:

- AI-proposed and player-confirmed
- player-authored through a constrained structured picker

Why this is acceptable in v0.1:

- one named enemy
- one region
- France only as claimant
- no ally-beneficiary settlement allocation

This is a much smaller UI problem than open-ended territorial promises.

### 9.4 Valid bargain targets

A war bargain is valid only if all are true:

1. The source treaty being proposed or modified is `DEFENSIVE_ALLIANCE` or `ALLIANCE`, or France is issuing a war-entry request to an existing military ally.
2. The named enemy is:
   - an active rival of France, or
   - an active rival of the target nation, or
   - a current war enemy.
3. The claim region is currently controlled by the named enemy or that enemy's subject.
4. The claim region is strategically plausible for France:
   - in `covets_regions`, or
   - previously French, or
   - adjacent to French territory, or
   - otherwise explicitly flagged as high-interest by existing desire data.
5. The target nation has a plausible participation path against the named enemy:
   - direct border, or
   - allied theater adjacency, or
   - existing route / access heuristic that the AI already recognizes as feasible.

Invalid uses:

- bargaining over ally territory
- bargaining over territory held by an unrelated third party
- bargaining over a region France has no plausible political interest in
- bargaining with a partner that cannot plausibly participate in the named war

### 9.5 Scope caps and contradiction guards

War bargains need hard limits in v0.1.

Caps:

- maximum 1 active war bargain per beneficiary nation
- maximum 2 active French war bargains total
- maximum 1 active bargain claiming a given region

Hard contradiction checks:

- France may not create a bargain for Region X if France already has an active bargain on Region X
- France may not create a bargain for Region X while holding `DEFENSIVE_ALLIANCE` or `ALLIANCE` with the current holder of X unless the player first downgrades that alignment through an explicit hard-stop flow
- France may not create a bargain with Nation A against Nation B if France already holds an active bargain with Nation B against Nation A
- France may not stack multiple bargain clauses into one treaty; one treaty package gets at most one bargain

These are validation failures or hard-stop choices, not soft warnings.

### 9.6 Lifecycle

On ratification, create a tracked commitment:

```json
{
  "id": 17,
  "type": "war_bargain",
  "promiser": "France",
  "beneficiary": "Prussia",
  "target_enemy": "Britain",
  "claim_region": "Hanover",
  "claim_holder": "Britain",
  "created_turn": 8,
  "triggered_turn": null,
  "status": "active",
  "source_treaty": "alliance",
  "source_pair": "France|Prussia",
  "cooldown_until_turn": 0,
  "last_notice_turn": null
}
```

Allowed statuses:

- `active`: bargain exists, target war not yet jointly fought
- `triggered`: France and beneficiary are co-belligerents against the named enemy while the bargain is live
- `fulfilled`: France gains the claimed region while the bargain is still valid
- `cancelled`: both sides accepted bargain cancellation
- `void`: basis disappeared without French bad faith
- `breached`: France explicitly reversed the bargain

Important v0.1 simplification:

- there is **no** `deadline_turn`
- there is **no** `suspended_turns`
- there is **no** periodic urgency-warning ladder

This removes the entire class of uncontrollable timer bugs from the old promise design.

### 9.7 Triggering and war-entry effects

When a live bargain exists and France asks the beneficiary to join war against the named enemy:

- apply a major positive war-entry modifier
- surface the bargain in the call-to-arms / declaration preview
- mark the bargain `triggered` once both are on the same side in that war

If France declares on the named enemy while a live bargain exists and the beneficiary is eligible to be called:

- the preview must show the beneficiary and the bargain
- if France chooses not to call the beneficiary, that is an explicit bargain reversal and counts as breach

If France uses the alliance against some other enemy:

- the bargain remains `active`
- no automatic breach occurs

This keeps bargains oriented around the named enemy without turning them into universal leash mechanics.

### 9.8 Fulfillment

A bargain is fulfilled when all are true:

1. The bargain is `active` or `triggered`.
2. France controls the claimed region in the final post-processing state of the turn.
3. The region changed from the named enemy or that enemy's subject to France while the bargain remained valid.
4. France still holds `DEFENSIVE_ALLIANCE` or `ALLIANCE` with the beneficiary in that final state.

Turn-order rule:

1. Resolve treaty ratifications, breaks, and downgrades.
2. Resolve war-state changes and region ownership.
3. Resolve bargain status changes caused by those results.
4. Evaluate fulfillment / breach / void using the final state.

Exploit guard:

- if France voluntarily downgrades the source military treaty on the same turn a bargain would otherwise fulfill, that counts as explicit breach, not cheap passive failure

### 9.9 Breach, void, and cancellation

#### A. France-caused breach

A bargain is `breached` if France does any of the following while it is active or triggered:

- breaks the source treaty voluntarily
- voluntarily downgrades the source treaty below `DEFENSIVE_ALLIANCE`
- deepens military alignment with the named enemy or current claim holder
- ratifies a contradictory bargain or contradictory claim-recognition state
- declares war on the named enemy but intentionally does not call an eligible beneficiary
- explicitly renounces the French claim in a later peace flow once bilateral peace hardening adds term-level claim warnings

Effects:

- relation penalty with beneficiary: around -10
- betrayal strike: +1 unless the same episode already spent the 2-strike cap through a source alliance break
- global reliability loss: -6

#### B. Void without French penalty

A bargain is `void` if:

- the beneficiary breaks the source treaty first
- the source treaty auto-decays below `DEFENSIVE_ALLIANCE` without an explicit French downgrade command
- the beneficiary allies the named enemy first
- the beneficiary refuses a bargain-backed call to arms
- the target enemy stops holding the claimed region through outside events not chosen by France
- the named enemy or claim region basis disappears from the world
- France is pulled into a contrary war against the beneficiary through third-party cascade that France did not directly declare
- France and the beneficiary become direct enemies through beneficiary-caused or external scripted state not directly chosen by France

Void effects:

- no French reliability loss
- no French betrayal strike
- dispatch / campaign log must state why the bargain ended

#### C. Cancellation by consent

The player may attempt to cancel an active bargain through visible diplomacy.

Rules:

- cancellation is not unilateral
- the beneficiary may accept or refuse
- if accepted:
  - relation hit: -5
  - global reliability hit: -3
  - no betrayal strike
  - apply a 6-turn cooldown on new bargains for that same pair and same named enemy
- if refused:
  - bargain remains active

This is intentionally costlier and less spammable than the old "accept bonus, cancel immediately" exploit path.

### 9.10 Review and warning surfaces

Every bargain clause must pass through a mandatory **Bargain Review** stage before send / accept.

Review must show:

- beneficiary
- named enemy
- claim region
- current holder
- source treaty
- contradiction warnings
- the main likely offended third party
- the practical effect: "This will make Prussia more willing to join France against Britain"

Required warning moments:

- bargain ratification
- war declaration on the named enemy
- source treaty downgrade / break while bargain is active
- deep treaty ratification with the named enemy or current holder
- bargain void / breach / fulfillment / cancellation

Important v0.1 rule:

- there are **no** periodic per-turn bargain reminders
- warnings are event-driven, not timer-driven

That keeps the UX focused on moments of agency instead of warning spam.

---

## 10. Acceptance Formula Hooks

This spec needs four acceptance inputs in v0.1.

### 10.1 Direct rivalry modifier

- negative when proposing deeper treaties to a direct rival
- primary active rivals must be able to swing deep-treaty outcomes on their own

### 10.2 Rival-commitment conflict modifier

- negative when the target knows France is already aligned with its rival
- stronger on military treaties than on lower-tier treaties
- France holding a live bargain against the target or for territory held by the target counts as rival-facing political alignment

### 10.3 Bilateral betrayal modifier

- negative based on active victim-side strikes
- stronger than global reliability
- three active strikes should not be cleanly erased by a single bargain sweetener

### 10.4 Bargain-value modifier

- positive when the offer includes a valid `war_bargain`
- should be large enough to matter for military alignment and war-entry politics
- should not overcome hard-resistance at 3 strikes by itself

Integration rule:

- if a tracked `war_bargain` clause is present, use `bargain_value_mod` instead of any old static sweetener that covers the same claim-support concept
- if no tracked bargain clause is present, the old static bonus may remain
- never double-count static sweetener + tracked bargain for the same idea

### 10.5 Composite grouping

Group the new modifiers under one composite:

```python
raw_political_commitment_mod = (
    direct_rivalry_mod
    + rival_conflict_mod
    + bilateral_betrayal_mod
    + bargain_value_mod
)

political_commitment_mod = max(-40, raw_political_commitment_mod)
```

Rules:

- the cap prevents formula-level total lockout
- hard-reject posture at 3 strikes still exists outside the formula
- the per-episode strike cap in 8.3 is what keeps that posture from becoming too punishing

---

## 11. AI Behavior

### 11.1 Proposal generation

AI should use rivalries to create branches:

- court France against their rival
- ask for exclusivity against rival before deep alliance
- offer or request a war bargain tied to a named enemy and French claim

AI may generate a bargain only if all are true:

- France is below the global active-bargain cap
- there is no active same-region contradiction
- named enemy is a current rival or current war enemy
- claim region is held by that enemy or their subject
- the target nation has plausible participation access
- the target nation has enough military weight or strategic willingness to matter
- no obvious contradiction with France's current deep ally network
- the same pair + target enemy is not on bargain cooldown

### 11.2 Anti-spam rules

AI must not:

- propose a bargain when France already has an active bargain with that nation
- chain multiple bargain requests in consecutive turns after cancellation or breach
- offer bargains the target cannot plausibly help fight over

### 11.3 Refusal behavior

AI should refuse or resist:

- deep alliance while France is already militarily aligned with the AI's rival
- new bargains from a promiser with severe betrayal memory
- deep treaties at 3 active victim-side strikes except under explicit survival exceptions

### 11.4 War-entry behavior

If a valid bargain exists against the named enemy:

- AI should value joining that war more highly
- AI should surface the reason in Talleyrand-facing warnings / previews
- if AI refuses anyway, the bargain should void cleanly with no French penalty

### 11.5 Strategic focus / advisory layer

Deferred. Static rivalries plus bargains are enough for v0.1.

### 11.6 Performance / architecture guard

No new hot-path per-region scans.

Use:

- cached rivalry lookups
- direct commitment-id and pair-key reads
- targeted validation checks on bargain creation and key event hooks

---

## 12. Player-Facing Surfaces

### 12.1 Diplomatic Ledger

Add to Nations / Talleyrand tabs:

- each nation's active rivals
- France's global reliability descriptor
- bilateral betrayal warning if that nation distrusts France specifically
- active bargains owed to or from that nation
- bargain cooldown notice when relevant

### 12.2 Proposal preview / Talleyrand advisory

Add a dedicated **Political context** panel to proposal preview / ratification surfaces.

It should surface:

- active rivals relevant to the target
- any bilateral betrayal memory affecting the offer
- any active bargain with that nation
- the main nation likely to be angered if France proceeds

Canonical preview contract:

- expose a structured `warnings[]` list
- each warning contains:
  - `severity`
  - `category`
  - `text`

Warning categories in this spec:

- `rivalry`
- `betrayal`
- `bargain`
- `paradox`
- `peace_conflict`

Preview legibility rules:

- show at most 2 warnings inline
- sort by severity first, then immediate player relevance
- collapse overflow behind `View all concerns`

### 12.3 Bargain Review

Any offer containing `war_bargain` gets a mandatory review card before send / accept.

The review card is the core new v0.1 promise surface.

### 12.4 Treaty display

Active treaties tab should surface:

- named-enemy bargains
- claim region
- current holder
- status (`active`, `triggered`, `fulfilled`, `cancelled`, `void`, `breached`)

### 12.5 Dispatch and campaign log

High-signal events only:

- rivalry escalation
- betrayal recorded
- bargain ratified
- bargain triggered
- bargain fulfilled
- bargain breached
- bargain voided
- bargain cancelled
- major reliability improvement or drop

Campaign log metadata must include:

- bargain id
- beneficiary
- target enemy
- claim region
- previous status
- new status
- relation delta
- reliability delta

No generic one-line event without those fields.

---

## 13. Data Model Draft

### 13.1 Keep and clarify

- `diplomatic_reliability: Dict[str, int]`
  - nation-keyed global reputation

### 13.2 Add

- `betrayal_history: Dict[str, Dict]`
  - key: `from|to`
  - value: `{strikes, categories, last_turn, decays_on_turn}`

- `nation_rivalries: Dict[str, Dict]`
  - key: `diplo_key`
  - value: `{intensity, source, weight, started_turn, last_changed_turn}`

- `diplomatic_commitments: Dict[str, Dict]`
  - value for `war_bargain`:
    - `id`
    - `type`
    - `promiser`
    - `beneficiary`
    - `target_enemy`
    - `claim_region`
    - `claim_holder`
    - `created_turn`
    - `triggered_turn`
    - `status`
    - `source_treaty`
    - `source_pair`
    - `cooldown_until_turn`
    - `last_notice_turn`

- `next_commitment_id: int`

### 13.3 Optional later

- `nation_claims`
- `trusted_partners`
- `nation_strategic_focus`
- `nation_power_scores`
- `nation_power_tiers`

Do **not** add ally-beneficiary settlement entitlement fields in this spec.

---

## 14. Implementation Sequence

### Slice A. Foundations

- clarify `diplomatic_reliability` as nation-level reputation
- add bilateral betrayal memory store
- add rivalry store including `weight`
- surface both in ledger / debug output

### Slice B. Rivalry pressure

- direct rivalry acceptance modifier
- third-party anger on treaty deepening
- `they_chose_us = +8`
- hard-reject behavior at 3 victim-side strikes
- commitment paradox flow for `DEFENSIVE_ALLIANCE` / `ALLIANCE`
- defer bloc pressure, power tiers, and strategic focus

### Slice C. War bargains

- new `war_bargain` clause type
- limited structured bargain picker for player-authored offers
- AI bargain generation with feasibility gates
- tracked bargain creation
- contradiction validation and hard-stop checks
- no deadline / no suspension / no passive expiry
- trigger on named-enemy war entry
- explicit fulfillment / breach / void / cancellation processing
- event-driven warnings only

### Slice D. AI integration

Deferred follow-up only:

- strategic focus
- power tiers
- richer rival-aware agendas
- broader bargain reasoning beyond the v0.1 feasibility gates

---

## 15. Risks

### R1. Over-hard locking

If rivalry becomes pure binary prohibition, diplomacy feels scripted.

Mitigation:

- keep lower treaty levels flexible
- force choices only on deep military commitments
- keep France-Britain extraordinary but technically possible

### R2. Bargain scope creep

If war bargains quietly turn back into ally-land promises, the old agency problem returns.

Mitigation:

- France only as claimant in v0.1
- single region only
- named enemy required
- no deadline system

### R3. Contradiction opacity

If the system allows hidden mutually impossible bargains, AI and players will both break it.

Mitigation:

- one active bargain per region
- one active bargain per beneficiary
- hard-stop contradictory-alignment checks

### R4. Warning overload

If warnings fire every turn, players stop reading them.

Mitigation:

- event-driven warning model only
- no timer ladder
- preview still capped to 2 inline warnings

### R5. Peace-hardening dependency

Later bilateral peace hardening will add stronger term-level claim conflict warnings.

Mitigation:

- v0.1 is explicit that bargains create political orientation now, not full ally-aware settlement rights
- current build must still warn whenever peace with the named enemy risks contradicting an active bargain

---

## 16. Resolved Design Calls

### Gate 1: Hard forced-choice vs soft penalty for rival military alignment?

**Resolved: forced choice for deep military alignment, soft pressure below that.**

### Gate 2: Global reliability + bilateral betrayal, or all pair-specific?

**Resolved: keep the split.**

### Gate 3: Timed territorial promises or narrower war bargains?

**Resolved: war bargains replace timed territorial-delivery promises in v0.1.**

Why:

- they create agency
- they remove uncontrollable deadline failure
- they fit the current bilateral diplomacy and peace model

### Gate 4: Promise deadlines / suspension model?

**Resolved: cut them entirely from v0.1.**

No `deadline_turn`. No `suspended_turns`. No urgency ladder.

### Gate 5: AI-authored only, or limited player-authored bargaining too?

**Resolved: allow limited player-authored bargaining.**

Why:

- the v0.1 bargain is simple enough to author cleanly
- promise mechanics without player agency would be a weaker design

### Gate 6: Hard-reject threshold?

**Resolved: keep 3 strikes, but cap strike gain to 2 per episode.**

### Gate 7: Ally-beneficiary land promises in v0.1?

**Resolved: defer.**

Those belong to the later settlement track, not this first commitments pass.

---

## 17. Draft Recommendation

For the first implementation pass:

- keep global reliability
- add bilateral betrayal memory
- add explicit rivalries with intensity and weight
- force a choice only for deep military alignment across active rivals
- replace timed territorial promises with named-enemy war bargains
- allow limited player-authored bargain construction
- keep bargains France-claim only in v0.1
- add contradiction guards, anti-spam caps, and explicit breach / void rules
- keep warnings event-driven instead of timer-driven
- defer ally-beneficiary settlement, common peace, bloc pressure, strategic focus, and power tiers

That is enough to make diplomacy feel political, create real war-entry bargaining, and remove the largest failure modes from the old promise draft without bundling in the full settlement overhaul too early.
