# Reliability + Commitments Spec

> **Status:** Draft v0.5
> **Date:** April 13, 2026
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

- This spec does **not** redesign war goals, ticking war score, or peace settlement logic. That belongs to `War Purpose + Settlement` (see `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` for the ally-settlement draft).
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

Political commitments should also reward committed play:

- choosing a side should create trust with the side you backed, not only anger with the side you excluded
- faithful alliance-building should unlock diplomatic upside, not merely avoid penalties

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

Prussia-Saxony hardcoded escalation (v0.1 special case, not the full dynamic system):

- If Prussia and Saxony enter direct war → escalate to `active`
- If France vassalizes Saxony → escalate to `active`

These are two concrete triggers checked at turn-end, not a general dynamic-formation system. They keep Prussia-Saxony from feeling inert without opening the full edge-case space.

### 7.2 Dynamic rivalry formation

Dynamic rivalry formation is a valid future extension, but it is **not part of the first implementation pass**.

v0.1 ships with the static starting rivalries plus the two Prussia-Saxony escalation triggers above. General dynamic formation moves to Slice D or later after the static system is playtested.

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
| `cold` | Political friction | direct treaty malus (`OPEN_BORDERS` -3, `NON_AGGRESSION` -5, deep treaties -10), third-party anger at half of §7.4B rounded toward zero, never triggers paradox by itself |
| `active` | Live geopolitical conflict | direct treaty malus (`OPEN_BORDERS` -5, `NON_AGGRESSION` -10, deep treaties -20), full third-party reactions, paradox checks on deep military alignment |

For v0.1:

- rivalry levels are authored, not dynamically escalated (exception: Prussia-Saxony hardcoded triggers in §7.1)
- secondary or dynamic rivalries may decay if conditions soften; primary authored rivalries are sticky per §7.6
- dynamic escalation can be added later with the broader AI-agenda work

### 7.4 Rivalry effects on diplomacy

Rivalry should create pressure in two ways.

#### A. Direct rivalry friction

Trying to deepen treaties with a direct rival applies acceptance penalties:

- `PEACE`: no extra block beyond normal relation / war logic
- `OPEN_BORDERS`: `cold` -3, `active` -5
- `NON_AGGRESSION`: `cold` -5, `active` -10
- `DEFENSIVE_ALLIANCE` / `ALLIANCE`: `cold` -10, `active` -20 before any target-specific betrayal / commitment modifiers

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

Notes:

- The table above is the baseline for `active` rivalries.
- If the offended third party is only a `cold` rival of Nation A, apply half the above values rounded toward zero.
- When France takes a rivalry-angering action in favor of Nation A, Nation A gains +5 relation with France (`they_chose_us`) once per ratified treaty-deepening event. Choosing a side should create a small upside with the chosen side, not only a penalty with the excluded one.

#### C. Great-power bloc pressure

Do **not** solve great-power politics with a flat numeric cap like "France may only ally one great power."

Instead:

- multiple great-power alliances remain legally possible
- but they should become politically unstable when they span opposing great-power camps
- great powers should especially dislike France binding itself to the allies of their main peer rival

Practical rule:

- if Nation B is the active great-power rival or preferred counterweight target of Nation C, then France deepening ties with B should also worsen how C reads France's wider alignment
- this applies even when France is not directly allied to C's rival yet; bloc-shaping behavior should matter before the final paradox state
- the penalty scales by treaty depth and should be smaller than direct-rival penalties, but large enough that stacking multiple deep great-power alignments becomes self-limiting

Suggested first-pass bloc pressure by new French treaty with Nation B:

| New state with B | Great-power concern reaction from C |
|------------------|-------------------------------------|
| `OPEN_BORDERS` | suspicion only, usually no more than -2 relation / small acceptance malus |
| `NON_AGGRESSION` | visible concern, roughly -5 relation / small-to-moderate acceptance malus |
| `DEFENSIVE_ALLIANCE` | major bloc warning, roughly -10 relation / major acceptance malus |
| `ALLIANCE` | severe camp-alignment warning, roughly -15 relation / very large acceptance malus |

Design guardrail:

- this is still a **soft-pressure system**, not a universal lock
- the hard stop remains reserved for `DEFENSIVE_ALLIANCE` / `ALLIANCE` across an active rival pair per §7.5
- lower treaty levels should remain possible, but they should visibly push France into one camp and away from another

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

Draft default for v0.1:

- `DEFENSIVE_ALLIANCE` / `ALLIANCE` across active rivals should force a choice rather than coexist.
- Lower treaty levels may coexist, but they still anger the excluded rival.
- The paradox offers **two options only** in v0.1: reject, or downgrade the existing conflicting alignment.
- There is no `proceed at cost` exception in the first implementation pass. If later playtests show the forced choice is too rigid, that can be designed as an advanced follow-up rather than baked into the initial paradox flow.

Implementation note — relationship to existing `alliance_paradox`:

The codebase already has a fully wired `alliance_paradox` HARD_STOP dialogue (`dialogue_manager.py`, `diplomatic_executor.py:2620-2677`, `alliance_paradox_popup.gd`). That flow fires when a **war declaration** would violate an existing alliance. The commitment paradox fires at **ratification** when deep military alignment would span both sides of a rivalry.

These are different triggers with different option sets. Implement as a **sibling dialogue type** (`commitment_paradox`) rather than overloading the existing `alliance_paradox`. This means:

- new dialogue type in `HARD_STOP_TYPES`
- new priority slot (1, between `alliance_paradox` at 0 and `vassal_rebellion_imminent` at current 1 — bump others down)
- new Godot popup (`commitment_paradox_popup.gd`)
- new handler methods in `diplomatic_executor.py`

### 7.6 Rivalry decay and resolution

Rivalry should not be permanent if political conditions change.

Decay rules:

- shared war against a common enemy reduces intensity slowly
- long peaceful coexistence with no border friction reduces intensity slowly
- fulfilled territorial promises to one rival against another can harden rivalry instead of softening it

Minimum decay model:

- in v0.1, authored primary rivalries (`France-Britain`, `Prussia-Austria`) are sticky and do not passively clear
- every 5 quiet turns, `active` secondary or dynamic rivalries may soften to `cold` if relation is positive and no recent betrayal exists
- after a longer stable period, `cold` secondary or dynamic rivalries may clear entirely

### 7.7 Strategic focus and Talleyrand recommendations

Static rivalries are the structural layer, but they should not be the only political signal in play.

For v0.1-plus design direction, add a lighter **strategic focus** layer:

- a major power may track one current geopolitical concern and one preferred counterweight
- great powers should care most about the continental balance and counterweights
- secondary powers should care about regional opportunity, protector choice, and local rivals
- Saxony / minor powers should use a simpler "feared rival / preferred protector" framing rather than symmetric rival slots
- strategic focus is **not** a new rivalry and does not trigger paradox checks by itself
- strategic focus exists to drive AI phrasing, proposal weighting, and Talleyrand recommendations

Player-facing goal:

- Talleyrand should be able to recommend 1-2 nations France ought to back right now
- the recommendation should explain both the upside ("Prussia will trust us more if we choose them") and the cost ("Austria will be lost if we do this")
- the recommendation should also reflect the live balance of power ("Austria is no longer a peer to Prussia" / "Bavaria is rising into secondary-power status")

Great-power alignment rule:

- if 3 or more `great_power` states are active, each great power should usually have at least one peer rival or preferred counterweight
- this is a **usual pressure**, not an always-on hard requirement; unipolar or collapsed-map situations may temporarily leave a great power without a meaningful peer concern
- the gameplay goal is not "every great power must hate one other great power forever"
- the gameplay goal is "great powers should usually read French diplomacy in camp terms, not as infinite friendship slots"

This is intentionally lighter than full dynamic rivalry formation. It adds guidance and political texture without requiring every nation pair to become a full rivalry system in v0.1.

### 7.8 Dynamic power tiers

Power status should be derived from numbers, not permanently authored by country name.

Design direction:

- use a derived `power_score` rather than a fixed "Austria is always a great power" rule
- countries may rise or fall in status as they gain regions, lose armies, acquire vassals, or collapse militarily
- rivalry remains the historical / political layer; power tier is the current-capability layer

Suggested inputs once the full map is live:

- controlled regions, weighted by region income / strategic value
- current fielded army strength
- manpower reserve / replacement depth
- vassal / client contribution
- current war position as a smaller modifier, not the main driver

Suggested tiers:

- `great_power`: top continental actors that shape coalition and settlement expectations
- `secondary_power`: credible regional actors with leverage, but not quadrangle-defining
- `minor_power`: states that usually seek protectors rather than define the balance

Guardrails:

- use hysteresis or a multi-turn average so nations do not bounce between tiers every turn
- on the current 5-nation map, `secondary_power` may be sparse or empty; that is acceptable
- once the larger map lands, the "great quadrangle" feel should emerge from the top power scores rather than being hardcoded forever

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
| Let a territorial promise fail by deadline / inaction | -6 | +1 strike | conditional |
| Actively reverse a territorial promise (ally, vassalize, cede to, or otherwise back the rival holder) | -10 | +2 strikes | strong for involved rivals |

Witness penalties apply only to directly interested observers:

- nations with `DEFENSIVE_ALLIANCE` or `ALLIANCE` with the victim
- nations with an active rivalry against the betrayer

Everyone else gets zero witness effect. The system should not apply broad "half penalty for uninvolved observers" noise.

Important v0.1 simplification:

- witnesses do **not** receive victim-grade bilateral strikes in v0.1
- witness reaction should be a scoped relation / acceptance penalty or lighter suspicion state only
- the 3-strike hard-resistance threshold is for the betrayed victim, not second-hand observers

### 8.4 Faithful-play rewards

The system should reward sustained good behavior, not only punish betrayal.

Trusted partner rule:

- after 10 consecutive honorable turns at `DEFENSIVE_ALLIANCE` or `ALLIANCE` with Nation X, and with no active betrayal from France toward X, grant `trusted_partner`
- `trusted_partner` gives:
  - +5 relation with that nation
  - +5 acceptance on future deep-treaty proposals with that nation
  - Talleyrand-facing surfacing ("Prussia now regards us as a trusted partner")
- betraying that nation immediately removes `trusted_partner`
- re-earning it requires another 10 clean honorable turns; passive strike decay alone is not enough

This is the minimum carrot that makes faithful alliance-building feel chosen rather than merely safe.

### 8.5 Redemption

Redemption should be possible, but it cannot be so slow that one mid-game betrayal effectively poisons the whole campaign.

Suggested rules:

- every 5 honored treaty turns: +3 to global reliability
- each fulfilled tracked promise: +4 to global reliability
- after honorable turns with a nation and no new offense, remove 1 bilateral strike against that nation using severity-scaled decay:
  - 6 turns: `OPEN_BORDERS` / `PEACE`-level break
  - 10 turns: `NON_AGGRESSION` break
  - 12 turns: passive territorial-promise failure
  - 14 turns: `DEFENSIVE_ALLIANCE` / `ALLIANCE` break
  - 16 turns: active territorial-promise sabotage / rival realignment
- fulfilling a commitment owed to a victim clears 1 bilateral strike immediately
- joining a victim's defensive war and remaining co-belligerent for 3 turns clears 1 bilateral strike

Caps / guardrails:

- active redemption effects can clear at most 1 strike per source event
- no nation may lose more than 1 bilateral strike per turn from passive decay
- global reliability still caps at the existing maximum

This keeps betrayal meaningful without making it structurally irrecoverable in a short campaign.

### 8.6 Hard-reject behavior

Repeated betrayal should eventually change AI posture, not just shave numbers.

Draft rule:

- 3 active bilateral strikes from France toward Nation X causes AI hard resistance to deep treaties with X
- exceptions allowed only for existential survival, coalition emergency, or very favorable war position
- witness suspicion alone does not trigger this threshold
- this is a core first-pass betrayal behavior, not optional later AI polish

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

Follow-up priority:

- once the obligation loop is proven fun, the first expansion should be limited **player-authored** promise construction ("offer support for Saxony to Prussia"), not a giant favors system

### 9.2 New clause

Add a new clause type:

- `territorial_promise`

Meaning:

- backend clause name remains `territorial_promise` for v0.1
- player-facing phrasing should emphasize **claim support / settlement guarantee**, e.g. "France will support Prussia's claim to Saxony"
- France promises to help the target obtain control of a specified region or claim package later
- this is an obligation about future settlement and alignment, not magical immediate cession of land France does not yet own

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

### 9.4.1 Wizard fit

To keep the diplomacy wizard legible:

- outbound player-authored promise construction stays deferred for v0.1
- when a treaty package contains `territorial_promise`, the wizard should insert a mandatory **Promise review** stage before send / accept
- Promise review should show the exact regions, beneficiary, deadline, source treaty, and the main likely political loser
- this remains a bilateral treaty review flow, not a hidden substitute for multilateral settlement allocation

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
  "suspended_turns": 0,
  "status": "active",
  "source_treaty": "alliance",
  "source_pair": "France|Prussia"
}
```

Deadline storage model:

- Store `deadline_turn` (absolute) plus `suspended_turns` (integer counter).
- Effective deadline = `deadline_turn + suspended_turns`.
- Do **not** store `remaining_turns` as a decrementing counter — that requires per-turn writes and is error-prone with suspension/resume.
- This matches the existing codebase pattern: `war_start_turns`, `turn_signed`, `armistice_turns` are all absolute turn numbers or simple counters, never decremented-per-tick values.

Deadline source for v0.1:

- the AI sets the deadline when proposing the promise
- the deadline must be visible before the player accepts
- the deadline uses a bounded urgency window:
  - floor: 8 turns
  - ceiling: 15 turns
- deadline length is not separately negotiable in v0.1

Coalition / war interaction:

- coalition membership does **not** void an active promise
- if promiser and beneficiary enter direct war, the deadline clock suspends: increment `suspended_turns` by 1 each turn while direct war persists
- when peace resumes, the promise clock continues (effective deadline has shifted forward by the suspension count)
- suspension is not a free erase: if the promiser ratifies terms favoring the rival claimant against the beneficiary during suspension, treat that as bad-faith breach
- if promiser and beneficiary remain direct enemies for 5 consecutive turns, auto-void the promise with no penalty to France; long enemy status should not leave a pre-war commitment suspended indefinitely

Source treaty interaction:

- if the source treaty is **broken by France**, the promise immediately fails with full betrayal penalties (§9.7) — this stacks with the treaty-break penalties from §8.3
- if the source treaty is **broken by the beneficiary**, the promise is voided with no penalty to France
- if the source treaty **naturally downgrades** (e.g. via turns-below-threshold), the promise remains active — it is an independent obligation that survives treaty drift

### 9.6 Fulfillment

A territorial promise is fulfilled when the effective deadline is reached (`current_turn >= deadline_turn + suspended_turns`) and the beneficiary controls the promised region.

v0.1 fulfillment check (three prongs, all must be true):

1. The beneficiary controls the promised region by the effective deadline.
2. At the time the fulfillment check resolves, France currently holds `DEFENSIVE_ALLIANCE` or `ALLIANCE` with the beneficiary.
3. France did not actively obstruct the promise during the window by vassalizing, ceding, or aligning with the rival holder.

Passive allied control is still sufficient. France does not need to have fought in the specific war or ceded the region directly - maintaining the alliance that gave the beneficiary strategic freedom counts as honoring the commitment. Tracking whether France contributed a defined military action would require new event-tracking infrastructure not worth the complexity for v0.1.

The degenerate case where the beneficiary conquers the region entirely on its own while France does nothing is still politically acceptable if France is **still** standing with that ally when the promise comes due. A momentary alliance followed by downgrade does not count.

### 9.7 Failure

A promise fails if:

- effective deadline expires with no fulfillment, or
- France breaks the source treaty (immediate failure, stacks with treaty-break betrayal from §8.3), or
- France signs a settlement that blocks fulfillment (e.g. ceding the promised region to a third party), or
- France aligns with the rival holder instead (e.g. allying the nation that controls the promised region), or
- France vassalizes the promised region / rival holder or otherwise brings the promised target under French control for itself

Failure effects:

- relation penalty with beneficiary: -15
- betrayal strike against France -> beneficiary: +1
- global reliability loss: -6
- possible rivalry escalation between beneficiary and the favored rival
- if failure was caused by source-treaty break, these stack on top of the treaty-break penalties from §8.3

Active-sabotage override:

- if France actively reverses the promise by allying, vassalizing, ceding to, or otherwise backing the rival holder, apply the stronger active-sabotage penalties from §8.3 instead of the default passive-failure values above
- for avoidance of doubt, French vassal control of the promised rival / region counts as backing that rival for both promise-failure and rivalry-conflict purposes

### 9.8 Renegotiation

Before failure resolves, the promise owner should be able to renegotiate.

Entry point: **typed command**. The player types a command like "renegotiate promise to Prussia" in the terminal. Talleyrand opens a `HARD_STOP` dialogue flow. The ledger shows commitment status and deadline as read-only context, but the action is initiated through the command interface. This avoids adding clickable action buttons to ledger tabs, which would be a new UI interaction pattern.

Allowed v0.1 flow:

- renegotiation is player-initiated via typed command
- it uses a standard `HARD_STOP` dialogue flow
- it offers two concrete branches:
  - downgrade the promise scope (e.g. reduce from 2 regions to 1)
  - cancel the promise with light penalty
- AI may refuse a downgrade request
- if the AI refuses, the original promise remains active and the clock continues
- successful renegotiation must be cheaper than outright failure
- renegotiation is available at any point while the promise is active, not only after urgency warnings fire — early renegotiation should be cheapest

Renegotiation cost model:

- if the beneficiary accepts renegotiation, apply a light trust cost instead of full betrayal:
  - relation hit: -5 (vs -15 for hard failure)
  - global reliability hit: -3 (vs -6 for hard failure)
  - no bilateral betrayal strike
- full betrayal applies only on hard failure or bad-faith reversal
- compensation currencies beyond territory remain deferred

### 9.9 Promise urgency warnings

Tracked promises must warn the player before failure becomes unavoidable.

Required warning points (measured against effective deadline = `deadline_turn + suspended_turns`):

- when 50% of the deadline window has elapsed — include renegotiation hint
- when 75% of the deadline window has elapsed — stronger tone, explicit renegotiation call-to-action
- final urgent warning when 3 turns or fewer remain

These warnings should surface through Morning Dispatch and the Talleyrand / commitments ledger summary. Each warning should remind the player that renegotiation is available and gets more expensive as the deadline approaches.

---

## 10. Acceptance Formula Hooks

This spec needs five acceptance inputs.

### 10.1 Direct rivalry modifier

- negative when proposing deeper treaties to a direct rival
- should be in the same order of magnitude as the relation modifier
- should be capable of swinging a deep-treaty outcome on its own for `active` rivalries

### 10.2 Rival-commitment conflict modifier

- negative when the target knows France is already aligned with its rival
- should be a major penalty on military treaties, not a cosmetic nudge
- should stack with direct rivalry pressure but not make lower-tier treaties impossible by default
- France controlling the target's rival as a vassal or client counts as rival alignment for this purpose

### 10.3 Bilateral betrayal modifier

- negative based on active strikes from proposer toward target
- stronger than global reliability
- should be at least roughly 2x the practical weight of global reliability at equivalent severity
- three active strikes should not be cleanly overcome by a single promise-value bump

### 10.4 Promise-value modifier

- positive when the offer includes a territorial promise matching the target's strategic interest
- should be meaningful enough to change AI behavior and make offers feel politically real
- should **not** be strong enough to erase deep bilateral distrust by itself

Integration note: `SPECIAL_BONUSES` in `diplomatic_templates.py` already gives Prussia +10 for `territory_saxony` and Saxony +10 for `protection_promised`. The promise-value modifier should **replace** these static bonuses for deals that include a tracked `territorial_promise` clause, not stack independently. When a promise clause is present, use the promise-value modifier; when the old-style sweetener is present without a tracked promise, keep the static bonus. This prevents double-counting.

### 10.5 Trusted-partner modifier

- positive when the target currently regards France as a `trusted_partner`
- should be strong enough to make faithful play feel distinct, but not strong enough to erase active bilateral betrayal
- this modifier is the durable upside of long-horizon alliance play

### 10.6 Formula grouping

The acceptance formula already has 15+ components. Adding 5 more risks opacity in debug output and balance tuning.

Group the four new modifiers under a single **"political commitment"** composite in the formula breakdown:

```
political_commitment_mod = (
    direct_rivalry_mod
    + rival_conflict_mod
    + bilateral_betrayal_mod
    + promise_value_mod
    + trusted_partner_mod
)
```

Report this composite as one line in debug/ledger output, with a drill-down available in verbose debug mode. This keeps the formula readable while preserving tuning granularity.

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
- react to `they_chose_us` and `trusted_partner` states by preferring deeper follow-up proposals with the side France has clearly backed

### 11.2 Refusal behavior

AI should refuse or resist:

- deep alliance while France is already militarily aligned with the AI's rival
- new promises from a promiser with severe betrayal memory
- deep treaties at 3 active victim-side bilateral strikes except under explicit survival exceptions

### 11.3 Escalation behavior

If France repeatedly angers a rival through opposite-camp alignment:

- AI may downgrade
- AI may issue warning-style proposals
- AI may pivot from diplomatic courtship toward hostility
- AI should eventually stop expressing anger as a silent relation number and start expressing it as explicit diplomatic behavior

### 11.4 Strategic focus / advisory layer

To keep static rivalries from feeling like pure furniture, the first AI expansion after the core rivalry pass should be advisory-first strategic focus:

- major powers surface a current concern and a preferred counterweight
- great-power logic should read the top power tiers and balance against peers
- secondary-power logic should favor regional ambition, opportunism, and protector choice
- Saxony / minor powers surface a feared rival and preferred protector
- Talleyrand uses this to recommend 1-2 nations France should back and to explain which courts that choice likely sacrifices
- this is lighter than full dynamic rivalry formation and should land before any attempt at a broad emergent-rivalry system

### 11.5 Performance / architecture guard

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
- `trusted_partner` status where applicable
- active commitments owed to or from that nation

### 12.2 Proposal preview / Talleyrand advisory

Add a dedicated **Political context** panel to the proposal preview / ratification surface.

It should surface:

- active rivals relevant to the target nation
- France's current strategic focus recommendation
- `trusted_partner` upside where applicable
- any active promise skepticism or betrayal memory affecting the offer
- the nation most likely to be angered if France proceeds

Preview payload rule:

- expose a structured `warnings[]` list for proposal preview / ratification surfaces
- each warning entry should contain at least:
  - `severity`: `info` / `warning` / `critical`
  - `category`: e.g. `rivalry`, `promise`, `betrayal`, `strategic_focus`, `settlement`
  - `text`: player-facing summary
- Talleyrand flavor text may elaborate, but the warning list is the canonical scannable layer

Before ratification, Talleyrand should warn:

- "This will anger Austria."
- "Prussia will not trust another territorial promise lightly."
- "We cannot bind both rivals without choosing."
- "If we choose Prussia here, Austria is likely lost to us for some time."
- "Our best current diplomatic line is Prussia and Saxony, not Austria and Prussia together."

Warning severity:

- hard stop: `commitment_paradox`, or a treaty state that would silently create an invalid military alignment
- soft warning / strong confirm: rivalry anger, strategic-focus tradeoff, trusted-partner upside, promise skepticism, and likely third-party fallout

Preview legibility rule:

- show at most **2 warnings inline** in the default proposal preview
- always sort by severity first, then by immediate player relevance
- if more warnings exist, collapse the remainder behind a `View all concerns` expansion
- `critical` warning takes the first slot whenever present
- if a hard-stop condition is already known before execution, the preview should still show its warning text, but the actual forced choice remains the HARD_STOP flow

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

- `trusted_partners: Dict[str, Dict]`
  - key: `diplo_key`
  - value: `{status, earned_turn, clean_turns}`

### 13.3 Optional later

- `claim_map` or `nation_claims`
- `nation_strategic_focus: Dict[str, Dict]`
  - key: nation
  - value: `{primary_concern, preferred_counterweight}` or minor-power equivalent
- `nation_power_scores: Dict[str, int]`
  - key: nation
  - value: derived current-power score
- `nation_power_tiers: Dict[str, str]`
  - key: nation
  - value: `great_power` | `secondary_power` | `minor_power`

Do **not** add full claims in v0.1 unless implementation proves they are required. Existing nation desire profiles may be enough for the first pass.

---

## 14. Implementation Sequence

### Slice A. Foundations

- clarify `diplomatic_reliability` as nation-level reputation
- add bilateral betrayal memory store
- add rivalry store
- add trusted-partner state
- surface both in ledger / debug output

### Slice B. Rivalry pressure

- direct rivalry acceptance modifier
- third-party anger on treaty deepening
- `they_chose_us` relation reward on side-taking
- hard-reject behavior at 3 victim-side strikes
- commitment paradox flow for `DEFENSIVE_ALLIANCE` / `ALLIANCE`
- implement paradox as a standard `HARD_STOP` dialogue through the existing `dialogue_manager` taxonomy, not as a new parallel flow

### Slice C. Territorial promises

- clause type
- tracked commitment creation
- fulfillment / failure processing
- user-facing claim-support / settlement-guarantee phrasing
- require alliance still active at fulfillment time
- treat active sabotage (allying, vassalizing, ceding to rival) as the stronger failure class
- urgency warnings and renegotiation flow (typed command entry point)
- advisory + ledger surfacing
- **minimal AI promise stub**: add `territorial_promise` generation to the `generate_suggested_terms` pipeline in `diplomatic_templates.py`, gated to nations whose `covets_regions` matches a region currently controlled by France or by that nation's rival - this is required because promises are AI-initiated only in v0.1, so without the stub no promises can exist at all

### Slice D. AI integration

- advisory-first strategic focus layer for AI phrasing and Talleyrand recommendations
- derive `nation_power_scores` / `nation_power_tiers` from map + military state with hysteresis
- full rival-aware proposal logic (extends the Slice C stub into strategic decision-making)
- betrayal-aware refusals
- promise-aware alliance offers
- optional dynamic rivalry formation later (general system, beyond the Prussia-Saxony hardcoded triggers in §7.1)

---

## 15. Risks

### R1. Over-hard locking

If rivalry becomes a pure binary ban too early, diplomacy may feel scripted instead of political.

Mitigation:

- keep lower treaty levels flexible
- force choices only on deep military commitments
- reward committed play (`they_chose_us`, `trusted_partner`) so the system is not all stick

### R2. Promise ambiguity

If promise fulfillment is vague, players will feel cheated.

Mitigation:

- exact regions
- exact deadline
- exact status text
- alliance must still be active at fulfillment time
- active sabotage cases must be explicit, not inferred

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
- long enemy status should auto-void suspended pre-war commitments instead of preserving them forever

---

## 16. Resolved Design Gates (v0.4)

### Gate 1: Hard forced-choice vs soft penalty for rival military alignment?

**Resolved: forced choice for deep military alignment, soft penalty below that, with two paradox options only.**

`DEFENSIVE_ALLIANCE` / `ALLIANCE` across active rivals triggers a commitment paradox dialogue (§7.5). Lower treaty levels coexist but anger the excluded rival (§7.4B). The paradox does not allow `proceed at cost` in v0.1: the player must reject the new treaty or downgrade the existing conflicting alignment. This keeps diplomacy feeling political without scripting outcomes at lower engagement levels.

### Gate 2: Global reliability + bilateral betrayal, or all pair-specific?

**Resolved: keep the split.**

Global reliability = "does France keep its word" (nation-keyed, drives broad acceptance modifiers). Bilateral betrayal = "what did France do to us specifically" (directional, drives hard-reject behavior at 3 strikes). These are different questions with different audiences. Collapsing them loses the distinction between "untrustworthy in general" and "specifically betrayed us."

### Gate 3: Renegotiation cost — relation, reliability, or both?

**Resolved: both, at reduced rates.**

Accepted renegotiation costs -5 relation and -3 global reliability, with no bilateral betrayal strike. Hard failure costs -15 relation, -6 reliability, and +1 strike. This makes early renegotiation clearly cheaper while keeping it non-free. See §9.8.

### Gate 4: Deadline storage model?

**Resolved: `deadline_turn` + `suspended_turns`.**

Absolute turn number plus suspension counter. Effective deadline = `deadline_turn + suspended_turns`. No decrementing counters. See §9.5.

### Gate 5: Renegotiation entry point?

**Resolved: typed command.**

Player types a renegotiation command in the terminal. Talleyrand opens a HARD_STOP dialogue. Ledger shows read-only status. No new clickable action buttons on ledger tabs. See §9.8.

### Gate 6: Slice C AI stub needed?

**Resolved: yes.**

Promises are AI-initiated only in v0.1. Without a minimal stub in `generate_suggested_terms`, no promises can be created and Slice C is untestable. The stub is scoped to `covets_regions` matching, not full rival-aware AI logic. See §14 Slice C.

### Gate 7: Passive allied control sufficient for fulfillment?

**Resolved: yes, but only if the alliance still stands when the promise comes due.**

Beneficiary controls the region + France still holds DEFENSIVE_ALLIANCE or ALLIANCE at fulfillment time = fulfilled. No active-contribution tracking. See §9.6.

### Gate 8: Prussia-Saxony cold → active escalation?

**Resolved: two hardcoded triggers.**

Prussia-Saxony war or France vassalizes Saxony → escalate to `active`. Not the full dynamic system. See §7.1.

### Gate 9: Full dynamic rivalries now, or a lighter strategic-focus layer first?

**Resolved: strategic focus first.**

Static rivalries remain the structural layer in v0.1. A lighter strategic-focus / Talleyrand-recommendation layer should come before any broad emergent-rivalry system. This adds guidance, court behavior, and side-choice texture without exploding edge-case scope. See §7.7 and §11.4.

### Gate 10: Power tiers authored by nation, or derived from numbers?

**Resolved: derived from numbers.**

Great / secondary / minor power status should come from current map and military strength, not fixed nation labels. Rivalry may be historical; power is situational. See §7.8.

### Gate 11: Hard limit on great-power allies, or bloc pressure?

**Resolved: bloc pressure, not numeric cap.**

France may still align with multiple great powers, but deep alignment with one great power should anger the allies, clients, and preferred counterweights of another. The system should make multi-great-power diplomacy possible but self-limiting through rivalry, strategic focus, and paradox pressure rather than through an arbitrary slot count. See §7.4C and §7.7.

### Remaining open question

- After the obligation loop is proven, should player-authored territorial-claim offers be added as the first expansion to the diplomacy wizard, or should promises remain AI-authored until the settlement layer in `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` is implemented?

---

## 17. Draft Recommendation

For the first implementation pass:

- keep global reliability
- add bilateral betrayal memory
- add explicit rivalries with intensity
- add `trusted_partner` as the minimum faithful-play reward
- force a choice only for deep military alignment across active rivals
- implement territorial promises as tracked obligations with exact deadlines
- phrase territorial promises as claim-support / settlement-guarantee commitments, not magical cessions
- include minimal AI promise generation stub in Slice C
- prefer a light strategic-focus / Talleyrand-recommendation layer over full dynamic rivalry formation

That is enough to make diplomacy feel political without bundling in the full war-settlement overhaul too early.
