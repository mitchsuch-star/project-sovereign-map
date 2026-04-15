# Reliability + Commitments Spec

> **Status:** Draft v0.9
> **Date:** April 14, 2026
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
- only explicit, player-surfaced obligations may create breach or betrayal

That means:

- no timer-based ally-land promises
- no suspension mini-system
- no invisible contradictory obligations
- no breach states triggered by AI inactivity alone

---

## 6. System Overview

The commitment system has four player-facing data concepts plus a small set of shared engine concepts that future systems can reuse.

### 6.1 Global reliability

This is the existing high-level reputation layer: "Does France generally honor agreements?"

- Keep `world.diplomatic_reliability` as a nation-keyed shared global reputation scalar.
- Clarify it as shared nation reputation, not pair memory.
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

### 6.5 Shared engine concepts

These are implementation-facing seams, not new player-facing mechanics:

- `episode_id`
  - root-cause identifier attached to all diplomatic consequences created by one explicit trigger
  - used to enforce strike caps by cause, not by whole turn
- `war_bloc`
  - generic bloc record with `target_nation`
  - in v0.1 this is backed by the serialized `active_coalition` record rather than a second parallel store
  - current coalition gameplay still instantiates only anti-France blocs, but the record shape must already be target-aware
- `opposition_graph`
  - derived view over active rivalries plus active `war_bloc` target pairs
  - used by paradox checks and future coalition overlap without hard-coding France
- `join_opportunity`
  - explicit surfaced ally-entry opportunity record used by declaration preview and later in-war requests
  - only explicit accept / reject / back out actions on a surfaced `join_opportunity` may change bargain state
- `fulfillment_snapshot`
  - terminal bargain payload used later by settlement / peace systems

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
- France/Austria is intentionally **not** a starting rivalry in v0.1; Austria remains the main swing partner on the 5-nation map.
- Playtest tripwire: if France can still reliably hold `ALLIANCE` with Britain, Prussia, and Austria by early midgame, the first follow-up should be France<->Austria `secondary + cold`, not a new bloc system.

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
| `VASSAL` | -25 relation + severe advisory warning |

Rules:

- if the offended nation is only a `cold` rival of A, apply half values rounded toward zero
- if France vassalizes a nation that is the offended rival's marked rival, apply the immediate `VASSAL` anger hit first, then process any authored escalation rule such as Prussia-Saxony
- the rival-reaction relation hit applies immediately on ratification and is the default pressure path
- if that relation loss pushes an existing French treaty with the offended rival below its stability threshold, normal downgrade and auto-downgrade rules should handle the fallout; do **not** force an instant treaty break as the default outcome
- do **not** add a separate `they_chose_us` token in v0.1; the reward loop should come from treaty depth, bargain leverage, fulfilled bargains, and visible preview / ledger surfacing

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

- the ratifying nation may not hold `DEFENSIVE_ALLIANCE` or `ALLIANCE` with both sides of the same `active` opposition pair
- in v0.1, the ratifying nation is always France and opposition pairs are authored rivalries; the rule is written generically so D2 coalition-driven opposition pairs plug in without rewriting it

Implementation seam:

- the paradox evaluator should read `opposition_pairs` from the shared `opposition_graph`
- in v0.1, authored rivalries populate that graph
- later coalition generalization may add `war_bloc.member <-> war_bloc.target_nation` opposition pairs without rewriting the paradox rule
- `commitment_paradox` preempts the older conflicting-alliance flow on same-ratification conflicts across active opposition pairs
- the older conflicting-alliance flow remains only for conflicts introduced later by war declaration or by non-opposition treaty states that were not intercepted at ratification

Rule body generalization:

- the rule subject is **the ratifying nation**, not a France-literal check
- in v0.1, the ratifying nation is always France, but the evaluator must already accept `(ratifier, new_treaty)` and reject when `ratifier` would span both sides of any active opposition pair

Multi-conflict ratification contract:

- a single ratification may surface more than one conflict (opposition-pair conflicts and legacy war-cross-alliance conflicts together)
- a single `ConflictResolutionPass` evaluator must collect **all** conflicts introduced by that ratification, classify each as `opposition` or `legacy`, and drive one consolidated resolution dialogue that lists every conflict and every downgrade option
- do not queue two sequential popups for one ratification; the player sees one decision surface covering the whole conflict set
- if resolving one conflict makes another moot, the pass must re-evaluate and drop the resolved conflict from the remaining set before committing the ratification
- if any unresolved conflict remains after the pass, the ratification is rejected

The paradox check runs on ratification, regardless of who proposed the treaty.

Player options in v0.1:

1. Reject the new treaty
2. Auto-downgrade the old military alignment

Rules:

- no silent rejection
- no silent coexistence
- no "proceed at cost" exception in v0.1
- the hard-stop must preview any deterministic downstream fallout from the chosen downgrade
- in the base rivalry slice this means the downgraded treaty outcome and the main offended-rival relation hit when knowable
- once war bargains ship, the same popup must also preview attached bargain breach, reliability loss, and strike gain when those values are knowable

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

Removed from v0.1:

- timer-based failure for ally-land promises
- suspension-based promise expiry
- passive failure caused only by AI inactivity
- explicit exclusivity-demand offenses
- bargain-only cancellation actions

### 8.3 Penalty model

Use both direct victim penalties and tightly scoped witness penalties.

| Event | Global reliability | Victim strikes | Witness effect |
|------|--------------------|----------------|----------------|
| Break `OPEN_BORDERS` / `PEACE`-level commitment | -4 | +1 | `-2` to each scoped witness |
| Break `NON_AGGRESSION` | -6 | +1 | `-2` to each scoped witness |
| Break `DEFENSIVE_ALLIANCE` / `ALLIANCE` | -10 | +2 | `-4` to each scoped witness |
| Explicitly reverse an active war bargain without also breaking the source military treaty | -6 | +1 | `-3` to each scoped witness that shares the same named enemy or claim region; `0` otherwise |

Critical episode-cap rule:

- one diplomatic episode may add at most **2 victim-side strikes to any one victim**

Definition:

- one diplomatic episode = all diplomatic penalties and strike applications that share the same root-cause `episode_id`
- a player-confirmed diplomatic action creates a fresh root `episode_id`
- `advance_turn()` may process multiple `episode_id`s; the turn itself is **not** one episode
- downstream treaty downgrades, bargain endings, witness fallout, and reliability changes caused by that same root trigger must reuse the same `episode_id`
- any pending dialogue, decay tracker, or delayed diplomatic consequence that may resolve after save/load must serialize its originating `episode_id` lineage until resolution

That means:

- if France breaks an alliance and an attached war bargain collapses in the same resolution step, relation and reliability penalties may stack
- Austria and Prussia may each gain strikes from the same episode if both were wronged
- no single victim's strike gain may exceed +2 from that single episode

Global reliability rule:

- all global reliability deltas in this spec apply to the acting nation's shared `diplomatic_reliability[actor]` value; the v0.1 actor is always France
- witness scoping changes relation fallout only; it does not create witness-specific reliability variants

This keeps the 3-strike hard-resistance threshold from becoming a one-click diplomatic death sentence on a 5-nation map.

### 8.4 Witness scoping

Witness penalties apply only to directly interested observers:

- nations with `DEFENSIVE_ALLIANCE` or `ALLIANCE` with the victim
- nations with an active rivalry against the betrayer
- nations with a live bargain that shares the same named enemy or the same claim region as the broken obligation

Everyone else gets zero witness effect.

Witnesses do **not** receive victim-grade strikes in v0.1.

Exclusivity-demand rule:

- do **not** add exclusivity-demand betrayal logic in v0.1
- if explicit exclusivity diplomacy ships later, it must create an explicit tracked commitment before it can create a betrayal offense

### 8.5 Faithful-play rewards

The system must reward sustained committed play, not only punish betrayal.

For v0.1:

- visible side-taking should feel legible through previews, warnings, and treaty outcomes rather than a bespoke hidden relation token
- fulfilled bargain: `+4` to `diplomatic_reliability[bargain.promiser]` and `+6` relation with the beneficiary
- reliability gain from fulfilled bargains is capped at once per (promiser, beneficiary) per 10 turns; additional fulfillments in that window still grant the beneficiary relation reward but no extra global reliability
- clear preview / ledger surfacing so loyalty feels intentional rather than invisible

Do **not** add a dedicated `trusted_partner` state in v0.1.

### 8.6 Redemption

Redemption remains possible, but stays simple.

Suggested rules:

- every 5 honored treaty turns: `+3` to `diplomatic_reliability[actor]` (v0.1 actor = France)
- each fulfilled bargain: `+4` to `diplomatic_reliability[bargain.promiser]` subject to the (promiser, beneficiary) cap above
- after honorable turns with a nation and no new offense, remove 1 bilateral strike using severity-scaled decay:
  - 6 turns: `OPEN_BORDERS` / `PEACE`-level break
  - 8 turns: `NON_AGGRESSION` break
  - 10 turns: `DEFENSIVE_ALLIANCE` / `ALLIANCE` break
  - 10 turns: explicit bargain reversal

Guardrails:

- passive decay clears at most 1 strike per nation per turn
- each strike decays on its own clock using its recorded `turn` + severity-scaled interval; the per-pair dict does **not** store a single shared decay clock
- strike age continues to mature during `WAR` and `ARMISTICE`
- actual strike removal requires an active non-`WAR` treaty (`PEACE` or above) with that nation
- once a non-war treaty is restored, any matured strikes may decay at the normal per-turn limit until caught up
- no special co-belligerence redemption hook in v0.1

### 8.7 Hard-reject behavior

Repeated betrayal must eventually change AI posture.

Rule:

- 3 active bilateral strikes from France toward Nation X causes AI hard resistance to deep treaties with X

Rules:

- witness suspicion alone never triggers this threshold
- survival exceptions are narrow: the 3-strike block may downgrade from absolute reject to heavy soft-resistance only when France and Nation X share a current enemy, France is not at war with X, the proposal is immediate military cooperation against that same enemy, and France did not betray X in the same episode
- when that narrow exception opens, AI still applies a major posture tax (treat as at least `-20` before normal formula evaluation); the exception removes only the absolute lock, not the political cost
- one episode cannot add more than 2 strikes to the same victim, per 8.3

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
- "priority claim" is political language only in v0.1; it does **not** create a general `nation_claims` mechanic or settlement entitlement outside this tracked bargain

Internal structure:

- `entry_term`
  - join / align against the named enemy
- `claim_term`
  - France's priority over exactly one region held by that enemy

These stay on one record in v0.1, but later systems may consume them separately.

`origin_mode` enum (v0.1):

- `treaty_clause` — authored as part of a ratified `DEFENSIVE_ALLIANCE` / `ALLIANCE` treaty package
- `counter_bargain` — issued as a `war_entry_counter_bargain` on an offensive ally-entry decision and ratified in `triggered` state
- later authoring paths append to this enum; do not overload existing values

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
- raised later as a **war-entry counter-bargain** when France asks an existing ally to join a specific war and that ally wants terms before entering

Why this is acceptable in v0.1:

- one named enemy
- one region
- France only as claimant
- no ally-beneficiary settlement allocation

This is a much smaller UI problem than open-ended territorial promises.

### 9.4 Valid bargain targets

A war bargain is valid only if all are true:

1. The source treaty being proposed or modified is `DEFENSIVE_ALLIANCE` or `ALLIANCE`, or France is invoking the v0.1 same-turn ally-entry decision for an existing military ally.
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

Current-build note / implementation correction:

- the current codebase has automatic defensive and offensive war cascade on declaration; it does **not** yet have a standalone `Call Ally` command
- this spec changes that contract for offensive ally entry: named-enemy ally participation must go through a player-visible ally-entry evaluation rather than silent automatic cascade
- in this spec, `ask`, `call`, and `war-entry request` mean the v0.1 ally-entry system, exposed at minimum through declaration preview and preferably through both preview intercept and a later explicit in-war request surface
- validation and scoring should read `promiser` and claimant fields from the record / payload rather than hard-coding string checks, even though current authored content still sets the claimant to France in v0.1

Invalid uses:

- bargaining over ally territory
- bargaining over territory held by an unrelated third party
- bargaining over a region France has no plausible political interest in
- bargaining with a partner that cannot plausibly participate in the named war

### 9.5 Scope caps and contradiction guards

War bargains need hard limits in v0.1, but the limits should target contradiction and spam rather than an arbitrary global ceiling.

Caps:

- maximum 1 live war bargain per beneficiary + named enemy pair
- maximum 1 live bargain claiming a given region
- maximum 1 bargain generated from a single treaty package or a single ally-entry decision

Hard contradiction checks:

- France may not create a bargain for Region X if France already has a live bargain on Region X
- France may not create a bargain for Region X while holding `DEFENSIVE_ALLIANCE` or `ALLIANCE` with the current holder of X unless the player first downgrades that alignment through an explicit hard-stop flow
- France may not create a bargain with Nation A against Nation B if France already holds a live bargain with Nation B against Nation A
- France may not stack multiple bargain clauses into one treaty; one treaty package gets at most one bargain
- one ally-entry decision may produce at most one counter-bargain from that ally on that turn

These are validation failures or hard-stop choices, not soft warnings.

### 9.6 Lifecycle

On ratification, create a tracked commitment:

```json
{
  "id": 17,
  "type": "war_bargain",
  "promiser": "France",
  "beneficiary": "Prussia",
  "origin_mode": "treaty_clause",
  "target_enemy": "Britain",
  "entry_term": {
    "named_enemy": "Britain"
  },
  "claim_term": {
    "claimant": "France",
    "claim_region": "Hanover",
    "claim_holder": "Britain"
  },
  "created_turn": 8,
  "triggered_turn": null,
  "ended_turn": null,
  "status": "active",
  "source_treaty": "alliance",
  "source_pair": "France|Prussia",
  "cooldown_key": "France|Prussia::Britain",
  "cooldown_until_turn": 0,
  "end_reason": null,
  "fulfillment_snapshot": null
}
```

Allowed statuses:

- `active`: bargain exists, target war not yet jointly fought
- `triggered`: France and beneficiary are co-belligerents against the named enemy while the bargain is live
- `fulfilled`: France gains the claimed region while the bargain is still valid
- `void`: basis disappeared without French bad faith
- `breached`: France explicitly reversed the bargain

Field note:

- `triggered_turn` stores the most recent turn on which the bargain entered `triggered`

Live-bargain rule:

- `live` means `active` or `triggered`
- caps, contradiction checks, AI anti-spam, and UI "active bargain" references in this spec should read `live` unless a rule explicitly names a narrower status
- only `fulfilled`, `void`, and `breached` stop counting against bargain caps

Important v0.1 simplification:

- there is **no** `deadline_turn`
- there is **no** `suspended_turns`
- there is **no** periodic urgency-warning ladder

This removes the entire class of uncontrollable timer bugs from the old promise design.

### 9.7 War-entry decision contract

The commitments slice needs a real ally-entry contract, not just terminology changes over today's automatic cascade.

Every player-visible ally-entry decision should materialize as a `join_opportunity`:

- `id`
- `beneficiary`
- `named_enemy`
- `request_type`
- `surfaced_turn`
- `hard_blocks[]`
- `origin_episode_id`
- `reroll_key`

Rules:

- only explicit accept / reject / back out actions on a surfaced `join_opportunity` may change bargain state
- failure to surface a `join_opportunity`, or inability to surface one because the request path does not yet exist, never creates breach by itself
- if a `join_opportunity` or pending counter-bargain may survive save/load, serialize `context.origin_episode_id`, `context.reroll_key`, and `context.join_opportunity` on the pending dialogue state; counter-bargain payloads should also store `context.counter_bargain_context`, `context.declaration_transaction_id`, and `context.pending_declaration`
- `context.pending_declaration` is the canonical staged offensive war-action snapshot for that transaction and must be sufficient to either commit or discard the declaration after the ally-entry decision resumes; at minimum keep `{transaction_id, actor, action_type, target_enemy, created_turn}` as primitive data

France-facing ally entry in v0.1 has three distinct cases:

- `defensive_honor_call`: France is attacked by the named enemy, or France enters that war as defender. `DEFENSIVE_ALLIANCE` and `ALLIANCE` partners may answer.
- `offensive_ally_request`: France starts or widens a war against the named enemy. `ALLIANCE` partners may answer by default; `DEFENSIVE_ALLIANCE` partners may answer only when a live bargain explicitly targets that named enemy.
- `coalition_entry`: coalition join logic is separate from alliance logic. Coalition membership is not an ally call and cannot be sweetened by `war_bargain`.

Hard blocks:

- armistice / cooldown or other treaty lock with the named enemy
- already on the enemy side of that war or already a direct enemy of France
- active `war_bloc` / coalition commitment against France in the current coalition model
- no plausible participation path under the game's access / route heuristic
- any other explicit backend contradiction that would create invalid war state

Rules:

- if a hard block exists, the preview must show the exact reason
- France does not incur bargain breach or reliability loss for failing to force an impossible join
- if a temporary hard block prevents entry and the bargain stays live, the UI must tell the player whether a later explicit ally-entry request will be available after the block clears

### 9.7.1 Defensive honor calls

When France is defender against the named enemy:

- defensive honor calls never generate counter-bargains
- after hard-block checks, eligible `DEFENSIVE_ALLIANCE` and `ALLIANCE` partners join automatically in v0.1
- there is no soft refusal path for a non-blocked defensive honor call in v0.1
- if a hard block prevents entry, do **not** auto-break the source treaty or the bargain from that blocked call alone
- if a live bargain exists against that same named enemy and both sides become co-belligerents, mark the bargain `triggered` and set `triggered_turn`

### 9.7.2 Offensive ally requests

When France uses an alliance offensively against the named enemy:

- apply a major positive war-entry modifier (`+25`) when a valid live bargain targets that named enemy
- surface the bargain in the ally-entry / declaration preview
- if France declares on the named enemy while a live bargain exists and the beneficiary is eligible for that ally-entry decision, the preview must surface either a `join_opportunity` or an explicit blocked reason
- offensive declaration preview is a two-phase transaction: resolve surfaced ally-entry / counter-bargain decisions first, then commit the war-state mutation
- if the player backs out from a surfaced offensive `join_opportunity`, the bargain remains `active` unless France also takes an explicit contradictory action elsewhere in this spec
- if France enters war against the named enemy through another direct player-controlled route while a live bargain exists, the same preview and surfaced `join_opportunity` rules apply
- if France uses the alliance against some other enemy, the bargain remains `active` and no automatic breach occurs

This keeps bargains oriented around the named enemy without turning them into universal leash mechanics.

### 9.7.3 War-entry counter-bargains and rerolls

An ally that did **not** negotiate a bargain at alliance time may still demand terms when France reaches an offensive ally-entry decision for a specific war.

This is the v0.1 wartime bargaining extension that fits current scope.

Rules:

- trigger point: France invokes an offensive ally-entry decision against a named enemy, whether through a declaration-preview intercept or a later explicit request flow
- defensive honor calls do **not** produce counter-bargains
- if the ally is not willing to join for free but is within the bargain-salvage range, the ally may issue one counter-demand
- the counter-demand may create a new `war_bargain` tied to that named enemy and one French claim region
- France may accept, reject, or back out of the request
- if France accepts, the ally joins and the bargain is created immediately in `triggered` state
- if France rejects, the ally does not join on that request, no bargain is created, and the declaration / war action may still proceed without that ally if otherwise legal
- if France backs out from declaration preview, the pending war-state mutation is cancelled and no bargain is created
- if no legal bargain can be generated because all valid claims are blocked by contradiction or scope rules, the ally either joins for free if already at the join threshold or refuses with that reason surfaced
- same-turn rerolls are deterministic: same ally + same enemy + same request type on the same turn must reuse the same score band and the same demanded region unless a material state change occurs
- `reroll_key = f"{beneficiary}|{named_enemy}|{request_type}|{turn_created}"`; the evaluator caches the last resolved (score_band, demanded_region) against this key and must return the cached pair unless a material state change invalidates it
- material state changes for reroll purposes are limited to:
  - treaty depth between France and the beneficiary
  - France-beneficiary relation
  - the beneficiary's war load
  - coalition / bloc status involving the beneficiary or the named enemy
  - route-feasibility changes caused by beneficiary / named-enemy territorial, treaty, or war-state changes
  - bargain-region availability changes caused by beneficiary / named-enemy war resolution
- France signing unrelated third-party treaties or opening unrelated third-party routes does **not** qualify as a reroll trigger
- counter-bargains should use the existing proposal-confirm shell with a `counter_bargain_context` payload in **blocking** mode; do **not** create a second dialogue family or mailbox flow for same-turn war entry
- a blocking counter-bargain confirm must not auto-dismiss on end turn and must offer terminal `Accept`, `Reject`, and `Back Out` actions against the staged `pending_declaration`

Valid wartime asks in v0.1:

- recognize France's claim to one region held by the named enemy
- deepen French alignment against that named enemy through the tracked `war_bargain` itself

Invalid wartime asks in v0.1:

- guaranteed ally land in the final peace
- multi-ally conference terms
- break or downgrade demands against an ally's rival as part of the same counter-bargain
- any request that requires settlement allocation among multiple participants

This keeps wartime bargaining bilateral and legible while deferring multi-party settlement politics to the later common-peace track.

### 9.7.4 Coalition overlap

Coalitions and alliances need different texture in this system.

- alliances are bilateral commitments and may be sweetened by a `war_bargain`
- coalitions are bloc commitments with separate loyalty and separate-peace logic; they are not bargainable through French claim-recognition terms
- coalition overlap rules and paradox evaluators should read from `war_bloc.target_nation` and the shared `opposition_graph`, not from literal "France" checks
- current gameplay still instantiates only anti-France `war_bloc`s, but the data and evaluator seams should already be target-aware
- an active `war_bloc` whose `target_nation` equals the ally-entry initiator is a hard block on accepting that initiator's ally-entry request; in the current build the only instantiated `war_bloc.target_nation` is France, but the rule is written target-aware so D2 does not require a rewrite
- if the beneficiary joins a `war_bloc` whose `target_nation` equals the bargain's `promiser` first, any live bargain from that promiser with that beneficiary voids for contrary alignment
- current coalition implementation is anti-France-specific; the later coalition follow-up should generalize this overlap logic so coalitions can form against powers other than France too

### 9.8 Fulfillment

A bargain is fulfilled when all are true:

1. The bargain is `triggered`.
2. France controls the claimed region in the final post-processing state of the turn.
3. The region changed from the named enemy or that enemy's subject to France while the bargain remained valid.
4. France still holds `DEFENSIVE_ALLIANCE` or `ALLIANCE` with the beneficiary in that final state.
5. The beneficiary is still a co-belligerent on France's side against the named enemy in that final state, or the named war ended that turn with both having been co-belligerents immediately before war resolution.

Turn-order rule:

1. Resolve treaty ratifications, breaks, and downgrades.
2. Resolve war-state changes and region ownership.
3. Resolve bargain status changes caused by those results.
4. Evaluate fulfillment / breach / void using the final state.

Exploit guard:

- if France voluntarily downgrades the source military treaty on the same turn a bargain would otherwise fulfill, that counts as explicit breach, not cheap passive failure
- `fulfilled` is terminal; later loss, trade, or renunciation of the region does not retroactively reopen the bargain, though later peace flows may still warn about political fallout

On fulfillment:

- write `fulfillment_snapshot = {claim_region, beneficiary, target_enemy, fulfilled_turn, reliability_delta, relation_delta, reward_capped: bool, intended_reliability_delta: int}`
- `reward_capped` is `True` when the `(promiser, beneficiary)` 10-turn cap zeroed the applied reliability delta; `intended_reliability_delta` preserves the pre-cap value so later peace / settlement systems can distinguish "first fulfillment" from "capped repeat fulfillment"
- keep the snapshot on the bargain record after terminal close so later peace / settlement systems can reason about prior fulfillment without walking the campaign log

If the named war ends without fulfillment:

- a `triggered` bargain that still has a valid source treaty and valid claim basis returns to `active`
- if the war ending also destroyed the claim basis or created contrary alignment, resolve through normal `void` rules instead

### 9.9 Breach and void

#### A. France-caused breach

A bargain is `breached` if France does any of the following while it is active or triggered:

- breaks the source treaty voluntarily
- voluntarily downgrades the source treaty below `DEFENSIVE_ALLIANCE`
- causes the source treaty to auto-decay through a French diplomatic action that directly angered the beneficiary or aligned France with the beneficiary's rival; this is constructive breach, not void
- deepens military alignment with the named enemy or current claim holder
- ratifies a contradictory bargain
- explicitly renounces the French claim in a later peace flow once bilateral peace hardening adds term-level claim warnings

Effects:

- relation penalty with beneficiary: `-10`
- betrayal strike: +1 unless the same episode already spent the 2-strike cap through a source alliance break
- global reliability loss: -6
- apply a 6-turn cooldown on new bargains for that same pair and named enemy

#### B. Void without French penalty

A bargain is `void` if:

- the beneficiary breaks the source treaty first
- the source treaty auto-decays below `DEFENSIVE_ALLIANCE` through beneficiary-caused or external changes that France did not directly choose
- the beneficiary enters `NON_AGGRESSION` or deeper alignment with the named enemy first
- the beneficiary joins a coalition directed against France first
- the beneficiary refuses a bargain-backed ally-entry request
- the target enemy stops holding the claimed region through outside events not chosen by France
- the named enemy or claim region basis disappears from the world
- France is pulled into a contrary war against the beneficiary through third-party cascade that France did not directly declare
- France and the beneficiary become direct enemies through beneficiary-caused or external scripted state not directly chosen by France
- the named war has been resolved (France at `PEACE` or higher with the named enemy) **and** the beneficiary is also at `PEACE` or higher with the named enemy, continuously for **5 turns**, with no re-declaration of war against the named enemy by either side in that window; this "zombie bargain" void is the legal exit when the bargain's political purpose has lapsed without French bad faith

Void effects:

- no French reliability loss
- no French betrayal strike
- apply a 4-turn cooldown on new bargains for that same pair and named enemy
- dispatch / campaign log must state why the bargain ended

#### C. No bargain-only cancellation action in v0.1

Rules:

- v0.1 does **not** ship a standalone "cancel bargain" action
- if France wants out, it must use ordinary treaty downgrade / break / contradictory-alignment actions, which then resolve through normal breach or void rules
- this avoids a parallel cancellation mini-system that would duplicate logic and create easy reward-then-unwind exploits

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
- any deterministic direct fallout if this bargain requires a prior downgrade or would breach an attached commitment: estimated reliability hit, strike risk, and direct relation hit where known

Required warning moments:

- bargain ratification
- war declaration on the named enemy
- source treaty downgrade / break while bargain is live
- deep treaty ratification with the named enemy or current holder
- bargain void / breach / fulfillment

Important v0.1 rule:

- there are **no** periodic per-turn bargain reminders
- warnings are event-driven, not timer-driven

That keeps the UX focused on moments of agency instead of warning spam.

---

## 10. Acceptance Formula Hooks

This spec needs four treaty-acceptance inputs in v0.1, plus a dedicated war-entry score.

### 10.1 Direct rivalry modifier

- use the exact treaty-depth values from 7.3:
  - `secondary + cold`: `OPEN_BORDERS -4`, `NON_AGGRESSION -6`, deep treaties / `VASSAL -12`
  - `secondary + active`: `OPEN_BORDERS -5`, `NON_AGGRESSION -10`, deep treaties / `VASSAL -20`
  - `primary + active`: `OPEN_BORDERS -6`, `NON_AGGRESSION -12`, deep treaties / `VASSAL -30`
- primary active rivals must be able to swing deep-treaty outcomes on their own

### 10.2 Rival-commitment conflict modifier

- negative when the target knows France is already aligned with its rival
- use explicit v0.1 values:
  - France holds `OPEN_BORDERS` with the target's active rival: `-2`
  - France holds `NON_AGGRESSION` with the target's active rival: `-4`
  - France holds `DEFENSIVE_ALLIANCE` with the target's active rival: `-10`
  - France holds `ALLIANCE` or `VASSAL` with the target's active rival: `-16`
  - France holds a live bargain against the target or for territory held by the target: `-8`
- do not double-count the same rival twice; use the strongest treaty-alignment value plus at most one bargain-conflict add-on
- cap `rival_conflict_mod` at `-20` before the composite floor
- France holding a live bargain against the target or for territory held by the target counts as rival-facing political alignment

### 10.3 Bilateral betrayal modifier

- negative based on active victim-side strikes at `-8` per strike
- cap `bilateral_betrayal_mod` at `-24`
- stronger than global reliability
- three active strikes should not be cleanly erased by a single bargain sweetener

### 10.4 Bargain-value modifier

- positive when the offer includes a valid `war_bargain`
- use explicit v0.1 values:
  - `+10` when sweetening `DEFENSIVE_ALLIANCE`
  - `+15` when sweetening `ALLIANCE`
  - `+25` on an immediate war-entry / ally-entry evaluation against the named enemy
- should be large enough to matter for military alignment and war-entry politics
- should not overcome hard-resistance at 3 strikes by itself

Integration rule:

- if a tracked `war_bargain` clause is present, use `bargain_value_mod` instead of any old static sweetener that covers the same claim-support concept
- if no tracked bargain clause is present, the old static bonus may remain
- never double-count static sweetener + tracked bargain for the same idea

### 10.5 Dedicated war-entry score

War entry should not piggyback on the generic treaty acceptance score. Use a dedicated `war_entry_score`.

Evaluate hard blocks before the score. If any hard block is present, the ally does not join and no counter-bargain is offered.

Use explicit v0.1 values:

- `base = 20`
- treaty depth: `DEFENSIVE_ALLIANCE +10`, `ALLIANCE +18`
- defensive honor bonus when France is defender: `+18`
- hostility toward the named enemy: `clamp((-relation_to_enemy) // 5, -10, +10)`
- if the named enemy is an active rival of the beneficiary: additional `+6`
- France-beneficiary relation: `clamp(relation_to_france // 5, -12, +12)`
- bilateral betrayal strikes: `-8` each, cap `-24`
- matching live bargain: `+25`
- other-war load: `-8` for one other active war, `-18` for 2+ other active wars or war exhaustion `>= 60`

Intentional omission:

- global reliability is **not** a direct `war_entry_score` input in v0.1
- war entry already reads bilateral betrayal memory, treaty depth, war load, and explicit bargain context; adding global reliability here mostly duplicates weaker information

Thresholds:

- `50+`: join without terms
- `25-49`: may issue one counter-bargain on offensive requests only
- below `25`: refuse
- defensive honor calls apply the `50` floor from 9.7.1 after hard-block checks

### 10.6 Composite grouping

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
- offer or request a war bargain tied to a named enemy and French claim

AI may generate a bargain only if all are true:

- there is room for a valid bargain under the pair + enemy and same-region constraints
- there is no live same-region contradiction
- named enemy is a current rival or current war enemy
- claim region is held by that enemy or their subject
- the target nation has plausible participation access
- the target nation has enough military weight or strategic willingness to matter:
  - at least one active marshal, and
  - either direct/front-access relevance to the named enemy or total active field strength >= 25% of France's current active field strength
- no obvious contradiction with France's current deep ally network
- the same pair + target enemy is not on bargain cooldown
- AI timing in v0.1 is narrow: bargain offers belong on military treaty creation / upgrade, or at war-entry time when the ally is close enough to salvage with terms

### 11.2 Anti-spam rules

AI must not:

- propose a bargain when France already has a live bargain with that nation
- chain multiple bargain requests in consecutive turns after void or breach
- offer bargains the target cannot plausibly help fight over
- issue a war-entry counter-bargain that asks for ally-beneficiary land or any other multi-party settlement outcome

### 11.3 Refusal behavior

AI should refuse or resist:

- deep alliance while France is already militarily aligned with the AI's rival
- new bargains from a promiser with severe betrayal memory
- deep treaties at 3 active victim-side strikes except under explicit survival exceptions

### 11.4 War-entry behavior

If a valid bargain exists against the named enemy:

- AI should value joining that war more highly (`+25` on the war-entry acceptance check)
- AI should surface the reason in Talleyrand-facing warnings / previews
- if AI refuses anyway, the bargain should void cleanly with no French penalty

Use the dedicated `war_entry_score` from 10.5 plus hard-block checks.

Defensive honor behavior:

- eligible `DEFENSIVE_ALLIANCE` and `ALLIANCE` partners do not counter-bargain
- absent a hard block, defensive honor should resolve as join
- if a hard block exists, the AI does not join and the block reason should be surfaced directly

Offensive ask behavior:

- if the pre-bargain war-entry score is `50+`, join without terms
- if the pre-bargain war-entry score is `25-49`, AI may issue a `war_entry_counter_bargain`
- if the pre-bargain war-entry score is below `25`, refuse outright
- the counter-demand must still obey the same named-enemy, single-region, France-claim, and feasibility constraints as a normal bargain
- if no legal bargain can be generated, the AI either joins for free if already over the threshold or refuses with an explicit reason
- same-turn repeat asks reuse the same result and same demanded region unless a material state change occurs

### 11.5 Strategic focus / advisory layer

Deferred. Static rivalries plus bargains are enough for v0.1.

Intentional v0.1 simplification:

- bargain timing and counter-bargain logic use shared heuristics, not personality-specific bargaining agendas

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
- live bargains owed to or from that nation
- bargain cooldown notice when relevant

Presentation rule:

- render this as one compact commitment block per nation, not as multiple new dense subsections repeated across tabs

### 12.2 Proposal preview / Talleyrand advisory

Add a dedicated **Political context** panel to proposal preview / ratification surfaces.

It should surface:

- active rivals relevant to the target
- any bilateral betrayal memory affecting the offer
- any live bargain with that nation
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

Severity contract:

- severity ordinals: `critical = 3`, `high = 2`, `medium = 1`, `low = 0`
- stable category tie-break order: `paradox`, `bargain`, `betrayal`, `rivalry`, `peace_conflict`
- later categories should append after this order, not silently reshuffle it

Preview legibility rules:

- show at most 2 warnings inline
- sort by severity first, then immediate player relevance
- collapse overflow behind `View all concerns`

### 12.3 Bargain Review

Any offer containing `war_bargain` gets a mandatory review card before send / accept.

The review card is the core new v0.1 promise surface.

Layout rule:

- insert the review card as the final stage inside the existing proposal-confirm popup / wizard flow
- show the bargain summary and top 1-2 warnings above the action buttons
- reuse the same card for war-entry counter-bargains with immediate Accept / Refuse / Back Out actions via `counter_bargain_context` on the existing proposal-confirm flow
- when used for counter-bargains, that reused proposal-confirm instance is `blocking=True` and resolves against the serialized `pending_declaration` snapshot rather than a normal envoy-in-transit proposal
- counter-bargain mode **must suppress** the following standard `proposal_confirm` affordances so envoy-semantics do not leak into same-turn war-entry resolution:
  - `renegotiate` action / counter-offer chain
  - envoy-in-transit status and turn-of-delivery language
  - DP cost display and DP spend on submit (the ally is not charging France DP for a demand)
  - mailbox deferral / "carry to them later" phrasing
  - dismiss / "never mind" action (blocking mode has no non-terminal exit; only `Accept`, `Reject`, `Back Out`)

### 12.4 Treaty display

Active treaties tab should surface:

- named-enemy bargains
- claim region
- current holder
- status (`active`, `triggered`, `fulfilled`, `void`, `breached`)

### 12.5 Dispatch and campaign log

High-signal events only:

- rivalry escalation
- betrayal recorded
- bargain ratified
- bargain triggered
- bargain fulfilled
- bargain breached
- bargain voided
- major reliability improvement or drop

Campaign log metadata must include:

- bargain id
- beneficiary
- target enemy
- claim region
- previous status
- new status
- end reason
- relation delta
- reliability delta

Rendering rule:

- store the full metadata payload on the event record
- render a compact one-line summary in the Campaign Log ("Prussia voided the Hanover bargain") rather than dumping all metadata inline
- deeper detail can be shown later through tooltip / expand affordances without changing the stored payload

---

## 13. Data Model Draft

### 13.1 Keep and clarify

- `diplomatic_reliability: Dict[str, int]`
  - nation-keyed shared global reputation scalar

### 13.2 Add

- `betrayal_history: Dict[str, Dict]`
  - key: `from|to`
  - value: `{strikes: List[StrikeRecord], categories: Set[str], last_turn: int}`
  - each `StrikeRecord` is `{severity: str, turn: int, episode_id: str, decays_on_turn: int}`
  - episode cap queries filter by `episode_id`; severity-scaled decay reads each strike's own `decays_on_turn`
  - the pair-level `last_turn` is retained only as a cached "most recent offense" summary for ledger display; it is **not** authoritative for decay or cap enforcement

- `nation_rivalries: Dict[str, Dict]`
  - key: `diplo_key`
  - value: `{intensity, source, weight, started_turn, last_changed_turn}`

- `diplomatic_commitments: Dict[str, Dict]`
  - value for `war_bargain`:
    - `id`
    - `type`
    - `promiser`
    - `beneficiary`
    - `origin_mode` — enum: `treaty_clause` | `counter_bargain`
    - `target_enemy`
    - `entry_term`
    - `claim_term`
    - `created_turn`
    - `triggered_turn`
    - `ended_turn`
    - `status`
    - `source_treaty`
    - `source_pair`
    - `cooldown_key`
    - `cooldown_until_turn`
    - `end_reason`
    - `fulfillment_snapshot` — `{claim_region, beneficiary, target_enemy, fulfilled_turn, reliability_delta, relation_delta, reward_capped, intended_reliability_delta}` or `null`

Cooldown note:

- cooldown lookups should key off `cooldown_key = source_pair + "::" + target_enemy`, not the commitment id, so breach / void anti-spam persists across bargain replacement and save/load
- `source_pair` should use canonical `promiser|beneficiary` ordering; in the v0.1 France-authored bargain slice this is always `France|beneficiary`

- `next_commitment_id: int`

### 13.3 Optional later

- `trusted_partners`
- `nation_strategic_focus`
- `nation_power_scores`
- `nation_power_tiers`

Do **not** add ally-beneficiary settlement entitlement fields in this spec.
Do **not** add a separate `nation_claims` store in this spec; until a later settlement system defines a canonical claim model, claim-like state should remain inside `diplomatic_commitments`.

---

## 14. Implementation Sequence

### Slice A. Foundations

- clarify `diplomatic_reliability` as nation-level reputation
- add bilateral betrayal memory store
- add rivalry store including `weight`
- seed `episode_id`, `join_opportunity`, `war_bloc.target_nation`, and `opposition_graph` seams in the engine contracts even where current authored content still targets France only
- surface both in ledger / debug output

### Slice B. Rivalry pressure

- direct rivalry acceptance modifier
- third-party anger on treaty deepening
- hard-reject behavior at 3 victim-side strikes
- commitment paradox flow for `DEFENSIVE_ALLIANCE` / `ALLIANCE`
- defer bloc pressure, power tiers, and strategic focus

### Slice C. War bargains

- new `war_bargain` clause type
- represent each `war_bargain` as one record with linked `entry_term` + `claim_term`
- limited structured bargain picker for player-authored offers
- AI bargain generation with feasibility gates
- tracked bargain creation
- contradiction validation and hard-stop checks
- no deadline / no suspension / no passive expiry
- no bargain-only cancellation action
- trigger on named-enemy war entry
- explicit fulfillment / breach / void processing plus `fulfillment_snapshot` on terminal close
- event-driven warnings only

### Slice D. Coalition overlap + war-entry hardening

- wire current coalition membership into bargain void / hard-block rules
- replace offensive silent cascade with a surfaced `join_opportunity` / ally-entry pipeline
- add or reserve later explicit in-war ally-entry requests so temporarily blocked bargains do not strand
- keep coalition loyalty / separate-peace logic distinct from alliance / bargain logic
- do **not** add breach on mere absence of a surfaced ally-entry opportunity

### Slice E. AI integration

Deferred follow-up only:

- strategic focus
- power tiers
- richer rival-aware agendas
- broader bargain reasoning beyond the v0.1 feasibility gates

### Slice F. Coalition buildout

Deferred next-phase work:

- generalize coalition logic so coalitions can form against powers other than France
- define coalition identity, leader, loyalty, and overlap hooks independently from France-specific threat rules
- extend coalition / alliance overlap rules beyond the current anti-France implementation
- revisit war-entry scoring once generalized coalition targets exist

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

- one live bargain per region
- one live bargain per beneficiary + named enemy pair
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
- current build must still warn whenever peace with the named enemy risks contradicting a live bargain

### R6. France-centric coalition assumptions

If commitments hard-code coalition overlap as "anti-France only," later coalition generalization becomes much harder.

Mitigation:

- keep coalition-overlap rules explicit and narrow in v0.1
- treat current anti-France coalition behavior as an implementation reality, not a permanent world rule
- document generic coalition follow-up in the implementation sequence now

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

Implementation clarification:

- the cap keys off root-cause `episode_id`, not whole-turn batching

### Gate 7: Ally-beneficiary land promises in v0.1?

**Resolved: defer.**

Those belong to the later settlement track, not this first commitments pass.

### Gate 8: Global bargain cap or structural caps?

**Resolved: use structural caps only.**

Why:

- pair + enemy and same-region limits stop contradiction and spam cleanly
- a hard global ceiling would arbitrarily block legitimate ally-by-ally bargaining

### Gate 9: Coalition obligation or alliance obligation?

**Resolved: treat them as distinct textures with explicit overlap rules.**

Why:

- alliances are bilateral and may be sweetened by bargains
- coalitions use separate loyalty and separate-peace pressure
- the current anti-France coalition model should be treated as a temporary implementation scope, not the final design limit

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
- add contradiction guards, structural anti-spam caps, and explicit breach / void rules
- make offensive ally entry player-mediated, with explicit hard-block reasons and deterministic same-turn asks
- keep warnings event-driven instead of timer-driven
- document coalition-overlap rules now and defer generalized non-France coalition buildout to the next phase

That is enough to make diplomacy feel political, create real war-entry bargaining, and remove the largest failure modes from the old promise draft without bundling in the full settlement overhaul too early.
