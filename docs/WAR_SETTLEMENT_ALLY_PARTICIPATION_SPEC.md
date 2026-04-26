# War Settlement + Ally Participation Spec

> **Status:** DEFERRED FOLLOW-UP DRAFT
> **Last Updated:** April 13, 2026
> **Companion docs:** `DIPLOMACY_SPEC.md`, `COALITION_SPEC.md`, `RELIABILITY_COMMITMENTS_SPEC.md`, `STATUS.md`
> **Scope note:** This is the ally-participation / peace-settlement slice of the broader `War Purpose + Settlement` track. It is explicitly **not** part of the `Reliability + Commitments` v0.1 ship scope.

---

## 1. Problem Statement

The current diplomacy game already supports allies entering wars, but it does not yet support allies participating in settlements in a first-class way.

That creates four gaps:

1. France can fight a multi-nation war, but peace is still negotiated as a pairwise deal.
2. Territorial claim-support / settlement-guarantee promises do not yet have a proper postwar fulfillment surface.
3. Great-power politics exist in spirit, but not yet in settlement procedure.
4. An ally can help win a war and still feel mechanically invisible at the peace table.

This spec defines the later settlement-side solution without replacing the current pairwise diplomacy foundation. The current commitments release should stop before this layer.

---

## 2. Current Verified Baseline

### 2.1 What already works

Allies already participate in wars at the declaration stage.

- `backend/game_logic/diplomacy.py` already processes defensive and offensive cascade in `_process_war_cascade()`.
- Defensive cascade: nations with `DEFENSIVE_ALLIANCE` or `ALLIANCE` with the target join against the aggressor.
- Offensive cascade: nations with `ALLIANCE` with the aggressor join against the target.
- Vassals also auto-join through the same war-entry pipeline.

### 2.2 Verification run on April 13, 2026

The following targeted tests passed locally in the repo virtualenv:

- `.\.venv\Scripts\python.exe -m pytest tests/test_session_2_diplomacy.py -k defensive_alliance_cascade`
- `.\.venv\Scripts\python.exe -m pytest tests/test_da3_offensive_cascade_friction.py`

Results:

- defensive cascade test: `1 passed`
- offensive cascade suite: `20 passed`

### 2.3 What does not exist yet

Peace and war score are still primarily pair-keyed.

- `world.war_scores` is pairwise by `diplo_key`
- `battle_records` are pairwise by `diplo_key`
- peace proposals are currently built as proposer <-> target deals with `sweeteners`, `demands`, and `clauses`

That is good enough for bilateral diplomacy and separate peace, but not for allied distribution of spoils.

---

## 3. Design Goals

- Keep current pairwise war state and pairwise war score intact for bilateral diplomacy.
- Add a separate settlement-side model for allies instead of overloading `war_scores`.
- Let allies who materially help in a war appear in settlement math and diplomatic fallout.
- Support both `separate peace` and `common peace`.
- Make territorial claim-support / settlement-guarantee promises resolvable in actual peace outcomes.
- Allow a first settlement pass to use authored / hardcoded power roles if needed; dynamic numeric power tiers remain a later enhancement.
- When this later feature begins, keep it compatible with the existing conversational diplomacy flow.

---

## 4. Non-Goals

- This spec does not replace the existing pairwise acceptance formula.
- This spec does not require a full HOI4-style turn-based bidding conference in v0.1.
- This spec does not require every war to become a giant multilateral congress.
- This spec does not block separate peace with a universal war-leader lock.
- This spec does not finalize the full `War Purpose + Settlement` overhaul by itself; it defines the ally-participation layer that the broader track needs.
- This spec is not part of the narrowed `Reliability + Commitments` v0.1 implementation target.

---

## 5. External Reference Patterns

These are design references, not direct implementation targets.

### 5.1 Hearts of Iron IV

Useful pattern:

- winning participants receive peace budget from participation rather than from a single bilateral score
- occupation, combat contribution, and broader war effort matter for postwar reward
- leaders can allocate gains to beneficiaries other than themselves

Useful takeaway for Sovereign Map:

- we need a settlement entitlement metric per ally
- this should be distinct from pairwise `war_score`

Not copied:

- no full click-contest peace minigame in v0.1
- no global total-war annexation buffet

Reference links:

- https://hoi4.paradoxwikis.com/Defines
- https://gamepretty.com/hearts-of-iron-iv-peace-conference-guide-bba-avalanche-1-12-3/

### 5.2 Victoria 3

Useful pattern:

- wars begin from explicit political sides and named participants
- backers and war goals are visible before or during escalation
- peace is not just a hidden bilateral number; allies have political standing

Useful takeaway for Sovereign Map:

- allies should become explicit participants in a war context, not invisible side effects
- peace terms that affect allies should pass through consultation, not just raw leader fiat

Not copied:

- no requirement that every ally must hard-consent to every peace treaty
- no need to recreate full diplomatic-play staging before this system lands

Reference links:

- https://www.vicky3.guide/diplomacy/first-war
- https://progameguides.com/victoria-3/how-to-declare-war-in-victoria-3/
- https://exputer.com/guides/victoria-3-war-system-explained/

### 5.3 Europa Universalis IV

Useful pattern:

- allies can be promised land and later judge whether the settlement honored that expectation
- peace can award provinces to participants other than the war leader
- contribution and reward affect long-term trust / favors

Useful takeaway for Sovereign Map:

- ignoring an ally at settlement should create a durable political consequence
- this consequence should be stronger when France explicitly promised a settlement outcome

Not copied:

- no province-occupation-transfer micromanagement requirement
- no hidden DLC-style edge case where a promise becomes effectively impossible to fulfill

Reference links:

- https://gaming.stackexchange.com/questions/337043/promising-land-to-allies
- https://gaming.stackexchange.com/questions/131539/how-to-demand-provinces-for-allies
- https://www.fandomspot.com/eu4-how-to-gain-favors/

---

## 6. Core Model

The central rule:

`war_score` answers "who is winning this bilateral war right now?"

`war_contribution_score` answers "who earned how much say in the settlement on this side?"

They are related, but they are not the same value and should not be merged.

### 6.1 Three Settlement Numbers

The system should track three distinct wartime numbers:

1. `pairwise_war_score`
   Existing value. Used for bilateral diplomacy, AI peace appetite, harsh terms, armistice logic, and pairwise military pressure.

2. `side_pressure_score`
   A new war-level or side-level summary used when negotiating common peace with a whole opposing bloc.

3. `war_contribution_score`
   A new participant-level score used only for settlement entitlement, consultation weight, and ally expectations.

### 6.2 Why this split matters

Example:

- France may have `+40` war score against Austria.
- Prussia may have contributed 35 percent of the winning side's effort.
- Austria may still negotiate primarily with France, but Prussia should not be invisible when Saxony or Bohemia are being distributed.

If we reuse pairwise `war_score` for everything, the ally disappears from the peace table.

---

## 7. War Identity

### 7.1 New concept: `war_instance`

Add a war-level container that groups related bilateral wars.

Suggested structure:

```python
world.war_instances[war_id] = {
    "created_turn": int,
    "originator": "France",
    "origin_target": "Austria",
    "attackers": ["France", "Saxony"],
    "defenders": ["Austria", "Prussia"],
    "active_participants": ["France", "Saxony", "Austria", "Prussia"],
    "separate_peaced": [],
    "declared_purposes": {},
    "common_settlement_open": False,
}
```

### 7.2 Relationship to current diplomacy state

`war_instance` does not replace pairwise war state.

- `diplomatic_states` remains the source of truth for whether two nations are at war
- `war_instances` group those pairs into one political conflict for reporting and settlement
- cascade entrants attach to the existing `war_id` of the declaration that pulled them in

### 7.3 End condition

A `war_instance` ends when there are no hostile pairs left between the two sides, or when one side has no active participants remaining.

Separate peace removes a nation from the active participant list without instantly ending the whole war.

---

## 8. Participant Roles

Each active participant on a side gets a role.

### 8.1 Roles

- `war_leader`
- `senior_ally`
- `junior_ally`
- `beneficiary_minor`
- `vassal_participant`

### 8.2 Leadership

For the player side:

- if France is an active participant, France chairs settlement on its side

For AI-only sides:

- side leader is the participant with the highest `war_lead_score`

Suggested `war_lead_score`:

```python
war_lead_score =
    (power_score_component * 0.5)
    + (war_contribution_share_component * 0.35)
    + (authority_component * 0.15)
```

This keeps great powers relevant without making contribution meaningless.

### 8.3 Power tiers

**SUPERSEDED — April 17, 2026.** This section's original text described dynamic numeric tiers (`great_power / secondary_power / minor_power`) recomputed from nation strength. That model is superseded by the canonical Phase 0 definition in `docs/SCALE_READINESS_PLAN.md` §"Phase 0 Cross-Cutting Taxonomy". Under the canonical rule:

- Tier names are `major / secondary / minor` (not `great_power / secondary_power / minor_power`)
- `power_tier` is **authored scenario data**, stable for the campaign. It is never recomputed at runtime.
- Any runtime numeric strength signal lives in a separate `power_score` field and does not overwrite `power_tier`.

The settlement-rights structure in §11 ("Seat rules") carries over under the new names: replace `great_power` with `major`, `secondary_power` with `secondary`, `minor_power` with `minor`. The seat / consult / beneficiary-only expectation levels are unchanged.

Power tier affects consultation rights, not free settlement score — this design intent is preserved.

*(Original superseded text: "Use the tier model already drafted in `RELIABILITY_COMMITMENTS_SPEC.md`: `great_power`, `secondary_power`, `minor_power`. These tiers come from numbers, not authored nation labels. The map can create a new quadrangle if power shifts.")*

---

## 9. War Contribution Score

### 9.1 New field

Add:

```python
world.war_contribution_scores[war_id][nation] = int
```

This is a side-local entitlement score. At settlement time, it is normalized into a percentage share on that participant's side.

### 9.2 v0.1 contribution buckets

Use four buckets:

1. `battle_contribution`
2. `occupation_contribution`
3. `staying_power`
4. `support_contribution`

Suggested weighting:

- battle: 40 percent
- occupation / liberation: 35 percent
- staying power: 15 percent
- support: 10 percent

### 9.3 What counts

`battle_contribution`

- casualties inflicted
- casualties suffered at reduced weight
- decisive battle participation

`occupation_contribution`

- enemy regions captured
- enemy capital captured
- allied/liberated regions restored

`staying_power`

- turns as an active war participant after joining
- capped so late wars do not become pure time-farming

`support_contribution`

- later hook for gold, manpower, AP, subsidy, or clause-driven support
- can be zero-weighted in the first implementation if support transfers are not yet wired

### 9.4 Important implementation note

Current `battle_records` are pairwise and only record one attacker nation and one defender nation.

That is not enough for fair allied contribution.

The first implementation pass should extend battle records for coordinated / allied battles with optional participant detail:

```python
{
    "attacker": "France",
    "defender": "Austria",
    "attacker_participants": ["France", "Saxony"],
    "defender_participants": ["Austria", "Prussia"],
    "nation_casualty_map": {
        "France": 4000,
        "Saxony": 1200,
        "Austria": 5000,
        "Prussia": 900,
    },
}
```

Without that extension, any ally-contribution system will mis-credit coalition battles.

---

## 10. Peace Types

Keep two peace modes.

### 10.1 Pairwise peace

This is the current model and should remain valid.

Use it for:

- armistice
- simple peace
- gold/manpower/AP exchanges
- bilateral concession with no third-party beneficiary
- coalition splitting and separate peace

### 10.2 Common peace

This is a new settlement mode for wars where allied participation matters.

Use it when:

- France wants to award territory to an ally
- a promise / settlement-guarantee is being fulfilled or broken
- a major term affects the whole opposing side politically
- a multi-party war ends with a coordinated postwar carve-up

### 10.3 Separate peace stays legal

Do not copy EU4's hard war-leader monopoly.

`COALITION_SPEC.md` already leans on separate-peace logic, so this spec keeps it:

- separate peace remains possible
- but it can trigger ally fallout if France cuts a deal that shuts out major contributors or breaks promises

### 10.4 Wizard routing

Use a **hybrid approach**.

Keep the existing nation -> proposal -> terms wizard for:

- armistice
- simple peace
- separate peace
- bilateral gold / manpower / AP deals

Do **not** try to stretch that wizard into a conference simulator.

When allied participation matters, route into a dedicated wartime settlement flow:

- entry choice from wartime diplomacy should be explicit: `Separate peace` vs `Open settlement`
- `Separate peace` stays in the existing bilateral wizard, but must show ally-fallout / promise-breach warnings before send
- `Open settlement` launches a war-scoped settlement flow keyed to the `war_id`, not to a single target nation

This keeps normal diplomacy legible while still letting allies matter in the wars where they actually should matter.

---

## 11. Settlement Rights and Expectations

### 11.1 Every participant does not need an equal veto

The first implementation should avoid a universal hard-consent rule.

Instead, give participants one of three expectation levels:

- `seat`
- `consult`
- `beneficiary_only`

### 11.2 Seat rules

*(Tier names updated April 17, 2026 to match canonical `power_tier` enum in `docs/SCALE_READINESS_PLAN.md` §"Phase 0 Cross-Cutting Taxonomy".)*

`major`

- always gets a settlement seat if it is an active participant

`secondary`

- gets a seat if contribution share is meaningful, or if its claim / promise is directly involved

`minor`

- gets a seat only when its own territory, survival, capital, or promised reward is being decided

### 11.3 Consultation rules

An ally must be consulted if:

- it has an active promise / settlement-guarantee connected to the target region
- it contributed materially above threshold
- the term changes control of a region it covets, borders, or previously owned
- the term would force or block its own strategic objective

### 11.4 No free universal veto

Consultation means:

- Talleyrand warns the player
- the UI surfaces likely reaction
- proceeding without accommodation creates diplomatic fallout

This is intentionally political cost, not absolute lockout.

---

## 12. Settlement Entitlement

### 12.1 New concept: `settlement_share`

At common peace time:

```python
settlement_share[nation] =
    war_contribution_score[nation] / total_side_contribution
```

This becomes the side's internal entitlement ledger.

### 12.2 What settlement share does

Settlement share affects:

- who expects reward
- who can plausibly receive territory or liberation outcomes
- how severe ally anger is if they are shut out
- AI willingness to accept being passed over

### 12.3 What settlement share does not do

It does not directly replace:

- pairwise war-score pressure
- acceptance formula math
- treaty legality

This is the internal "who earned spoils" number, not the "did we beat them" number.

### 12.4 Leader reallocation

The side leader may spend political capital to allocate settlement value to an ally even if the leader could have taken it themselves.

That is the intended route for:

- honoring promises
- rewarding a high-contribution ally
- creating loyal buffer states

This should improve relation with the beneficiary and strengthen `they_chose_us` plus any later faithful-play upside the diplomacy layer adds.

---

## 13. Term Ownership

Peace terms should become explicitly owned.

### 13.1 New term fields

For settlement-sensitive terms, add:

- `target`
- `payer`
- `beneficiary`
- `war_id`

For territory terms:

- `from_nation`
- `to_nation`
- `regions`

### 13.2 Allowed beneficiaries

In common peace, the beneficiary can be:

- France
- an active ally on France's side
- a liberated nation
- a former owner restored by treaty

### 13.3 First-pass restriction

Do not support arbitrary beneficiary chains in v0.1.

No:

- ally gives region to another ally through three-step chains
- hidden off-screen transfer to non-participants
- nested protectorate / vassal / subject distribution logic

Keep the first pass to direct, legible outcomes.

---

## 14. Ally Fallout

### 14.1 New memory: `shut_out_in_settlement`

If an ally contributed meaningfully and France concludes peace that excludes them from any meaningful gain, apply a diplomatic memory.

This is not automatically a betrayal strike.

It is a new settlement grievance.

### 14.2 Suggested severity bands

Minor shut-out:

- ally contributed but had no promise and no high-interest claim
- effect: moderate relation hit only

Major shut-out:

- ally had strong claim interest or high contribution
- effect: larger relation hit, acceptance penalty, possible treaty downgrade pressure

Promise breach:

- France could have honored an explicit settlement-guarantee and chose not to
- effect: route through the stronger reliability / betrayal pipeline from `RELIABILITY_COMMITMENTS_SPEC.md`

### 14.3 Major power vs minor reaction

Major powers:

- bigger anger when excluded
- more likely to downgrade alignment or shift against France politically

Minors:

- narrower grievance
- mostly care when their survival, capital, or explicit promised reward is involved

This is where the numeric power-tier model matters.

---

## 15. Promise Integration

This spec is the missing settlement half of the commitments design.

### 15.1 Promise fulfillment rule

A territorial claim-support / settlement-guarantee should be considered fulfilled only if:

- the beneficiary was on France's side in the war or settlement path
- the beneficiary is legally eligible for the region
- the final peace result actually awards or secures the promised political outcome

### 15.2 Promise breach via settlement

Examples:

- France promised Saxony to Prussia, then keeps Saxony
- France promised Prussian settlement priority, then cuts separate peace and excludes Prussia
- France promised liberation or restoration, then signs peace that blocks it while the outcome was still feasible

These are not vague disappointments. They are explicit settlement breaches.

### 15.3 Why this matters

Without settlement participation, territorial promises remain half-defined. The promise lives in diplomacy, but not in the actual war-ending machinery that is supposed to satisfy it.

---

## 16. Talleyrand and UI Surface

### 16.1 Talleyrand should become settlement counsel

In common peace, Talleyrand should surface:

- current participants
- contribution shares
- active promises
- likely reactions if an ally is cut out
- whether a region is "theirs by contribution", "theirs by promise", or "ours if we insist"

### 16.2 First-pass UI requirements

This does require a dedicated wartime settlement flow.

Do **not** build a full second diplomacy stack, but do not pretend the normal bilateral wizard is enough either.

Use existing surfaces where possible:

- proposal preview
- ledger
- war status panel
- dispatch
- mailbox / response popups

### 16.3 Required warnings

Examples:

- "Prussia expects Saxony under active settlement guarantee."
- "Austria contributed 28% and will view exclusion as deliberate humiliation."
- "Saxony is minor, but its survival is now a conference issue."
- "Proceeding will honor France's promise to Prussia and likely cost us Austria."

Settlement-warning presentation rule:

- common peace should use the same structured `warnings[]` approach as bilateral diplomacy
- keep the default preview scannable: max 2 inline warnings, severity-sorted, with overflow behind `View all concerns`
- settlement-specific warnings should usually outrank generic rivalry flavor when they imply immediate promise breach or major ally fallout

### 16.4 Recommended flow

**Separate peace:**

- choose nation from the existing wartime diplomacy wizard
- choose `Separate peace`
- review bilateral terms
- show an **Ally fallout** panel with contribution / promise / consultation warnings
- send or back out

**Common peace:**

- choose war / side context, not just one nation
- review participants, seats, and consultation expectations
- build settlement terms through structured pickers
- review the whole package in a conference-style summary
- send the common peace package

Structured pickers should own:

- beneficiary choice
- region allocation
- term ownership (`from_nation`, `to_nation`, `beneficiary`)
- any term tied to a promise or allied entitlement

Conversation should still own:

- Talleyrand's recommendation
- "who should we back?" framing
- the political cost explanation

### 16.5 Hard stops vs soft warnings

Hard stop only for:

- impossible / invalid settlement shapes
- any future contradiction that would silently create an illegal term package

Everything else should be political cost, not universal veto:

- ally consultation skipped
- great-power humiliation risk
- shut-out risk
- separate-peace fallout
- promise breach warning where the player can still choose to proceed

This follows the spec's core call: allies should matter without all receiving a veto.

---

## 17. Data Model Additions

Suggested additions:

```python
world.war_instances: Dict[str, Dict] = {}
world.war_contribution_scores: Dict[str, Dict[str, int]] = {}
world.war_settlement_expectations: Dict[str, Dict[str, Dict]] = {}
world.shut_out_in_settlement: Dict[str, List[Dict]] = {}
```

Possible derived or optional fields:

```python
world.side_pressure_scores: Dict[str, Dict[str, int]] = {}
world.war_leaders: Dict[str, Dict[str, str]] = {}
```

Important compatibility note:

- keep `war_scores`, `battle_records`, `decisive_battles`, and `war_start_turns`
- do not migrate or delete existing pairwise structures
- build the new layer on top of them

---

## 18. Implementation Sequence

This sequence is explicitly **post-commitments**. Do not start it until the narrowed `Reliability + Commitments` v0.1 pass is stable and legible in playtests.

### Slice A: War identity + read-only grouping

- add `war_instance`
- attach cascade entrants to the same `war_id`
- expose participant lists in read-only debug / ledger surfaces

### Slice B: Contribution tracker

- add `war_contribution_scores`
- extend battle records for multi-participant attribution
- derive contribution shares

### Slice C: Common peace plumbing

- add `common peace` as a settlement mode
- allow ally beneficiaries on territory terms
- add settlement entitlement and consultation checks

### Slice D: Fallout + commitments integration

- add `shut_out_in_settlement`
- route explicit promise failures through reliability / betrayal rules
- add `they_chose_us` upside for allies who are rewarded

### Slice E: Talleyrand and UI

- warnings in proposal preview
- settlement expectations in ledger / war view
- dispatch commentary on side reactions

---

## 19. Testing Focus

Highest-priority tests:

1. Cascade-created ally enters same `war_id` as original declaration.
2. Separate peace removes only that participant from the common war.
3. Common peace can award territory to ally beneficiary.
4. High-contribution ally excluded from common peace gains settlement grievance.
5. Explicit promised settlement denied when feasible triggers promise breach.
6. Great-power ally gets consultation warning even with lower contribution.
7. Minor ally only appears when its direct interests are involved.
8. Battle attribution in coordinated allied battles feeds the correct contribution score.
9. Side pressure score does not break existing pairwise peace acceptance logic.
10. Existing bilateral peace proposals still work unchanged in wars without allied settlement needs.

---

## 20. Design Calls

### 20.1 Strong call

Add `war_contribution_score` as a new per-ally settlement number.

Do not try to overload pairwise `war_score` into this job.

### 20.2 Strong call

Keep `separate peace`.

The interesting tension is not "peace is impossible unless the war leader says yes."
The interesting tension is "you can cut a separate deal, but doing so may cost you allies."

### 20.3 Strong call

Power tiers do not need to be dynamic on day one of settlement.

No country is eternally a great power, but this layer should not block the first settlement pass. Hardcoded / authored roles are acceptable until dynamic scoring is worth the added complexity.

### 20.4 Strong call

Allies should not all receive a veto, but they should all be able to matter.

That means seats, consultation, entitlement, and fallout, not universal hard blocking.

---

## 21. Draft Recommendation

For the first implementation pass **after commitments v0.1 is stable**:

- keep pairwise war score exactly where it is
- add `war_instance`
- add `war_contribution_score`
- keep separate peace
- keep separate peace in the existing bilateral diplomacy wizard
- add common peace only when ally beneficiaries or promises matter, and route it through a dedicated wartime settlement flow rather than the normal nation proposal loop
- add settlement grievance for shut-out allies
- use major / secondary / minor power weighting as consultation weight, not free score; hardcoded tiers are acceptable at first

This is enough to make allies visibly present in the political outcome of a war without turning the game into a full conference simulator. It is intentionally a later release, not part of the current commitments cut line.
