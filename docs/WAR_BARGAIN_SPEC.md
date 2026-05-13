# War Bargain Spec

> **Status:** Historical landed implementation reference v1.1
> **Date:** April 16, 2026
> **Phase placement:** Landed Peace Deals slice, after `Memory and Pressure`, `Bilateral Peace Hardening`, and `War Purpose + Score Semantics`. Settlement ally participation/common peace now owns later settlement work.
> **Origin:** Extracted from `docs/RELIABILITY_COMMITMENTS_SPEC.md` v1.0 §6.4 / §9 / §10.4 / §10.5 / §12.3 / §12.4 / §13 during the v2.0 rescope on April 16, 2026. The Memory and Pressure substrate (rivalries, betrayal memory, episode_id, witness scope, hard-reject posture) shipped without bargains; this spec defines the promise mechanic that was deferred out of v0.1.
> **Companion docs:** `RELIABILITY_COMMITMENTS_SPEC.md` (substrate), `BILATERAL_PEACE_HARDENING_SPEC.md` (landed), `WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md` (landed), `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` (active follow-up)

---

## 1. Purpose

This spec defines the **war bargain** mechanic — the v0.1-shaped political promise layer that was cut from the Memory and Pressure phase in the April 16 rescope.

A war bargain is a named-enemy bilateral commitment, used to secure deeper alignment or war entry from an existing or prospective ally, in exchange for explicit recognition of France's priority claim to a single enemy-held region.

The mechanic gives the player a real political verb that:

- chooses an ally
- chooses a named enemy
- chooses a single French claim region
- decides whether to honor or reverse that promise as the war evolves

It deliberately avoids the failure mode of the older "promise an ally they will receive Region X by turn N" draft: it asks the player to honor outcomes they can directly shape (their own claim, their own war entry, their own alliance state), not outcomes only an ally AI can produce.

---

## 2. Phase placement and dependencies

This spec is **not** part of the `Memory and Pressure` v0.1 ship.

It depends on:

- **Memory and Pressure substrate** (`betrayal_history`, `episode_id`, `scope_reason`, hard-reject posture, structured `warnings[]`) — shipped.
- **Bilateral Peace Hardening** — explicit term ownership, peace preview clarity, promise-breach warnings at the peace table. Required so bargain breach via "France makes peace with the named enemy" can preview consequences before the player commits.
- **War Purpose + Score Semantics** — the war-objective contract gives bargains a clean settlement-side hook.

It feeds into:

- **Ally Participation + Common Peace** — fulfilled bargain `fulfillment_snapshot` becomes input to ally-aware settlement allocation.

Historically, implementation did not begin until both Bilateral Peace Hardening and War Purpose + Score Semantics had written, gated specs. The bargain mechanic is the political-promise layer that those two systems give meaning to.

---

## 3. Problems To Solve

### P1. The current diplomacy lacks a real promise verb

After Memory and Pressure ships, France has hegemony / bloc pressure, betrayal memory, and reliability — but no way to make a **specific** political commitment to a specific ally about a specific objective. Diplomacy still runs on generic alliance ratification.

### P2. Offensive war entry is silent

The current build cascades alliance partners into offensive wars automatically with no player-visible decision surface. This means France cannot *ask* an ally to join a war — they either join free or don't, and there is no negotiation moment.

### P3. The old promise draft asked the player to guarantee outcomes they could not produce

The older "France promises Prussia they will receive Saxony by turn 12" model failed because:

- France cannot run ally-aware settlement allocation
- France cannot force the ally AI to pursue the promised region
- deadline pressure created timer anxiety, not political drama

War bargains avoid this by being **France-claim-scoped**: France promises *its own* alignment and *its own* claim priority. France can directly shape both.

---

## 4. Goals

- Add a first-pass promise mechanic that improves war-entry politics without requiring common peace.
- Replace silent offensive cascade with a player-visible ally-entry decision.
- Give Memory and Pressure's betrayal substrate something to remember beyond raw treaty breach.
- Keep rules machine-readable enough for AI and tests.

## 5. Non-Goals

- Does **not** ship ally-beneficiary land promises ("Prussia gets Saxony"). Those belong to `Ally Participation + Common Peace`.
- Does **not** ship deadline-based promises, suspension-based promises, or passive-failure mechanics.
- Does **not** ship multi-region or multi-enemy bargains.
- Does **not** introduce per-turn bargain reminders or warning ladders.
- Does **not** generalize coalition target tracking (defer to `Coalition Generalization` follow-up).

---

## 6. Design Principle

War bargains are political-promise mechanics with one strict rule:

- **only punish the player for outcomes France could actually shape**

That means:

- France only as claimant in v0.1
- France only as bargain promiser in v0.1
- AI-to-AI bargains are **excluded** in v0.1 (AI nations may propose bargains to the player, but two AI nations may not create bargains between themselves)
- single named enemy
- single claim region
- breach is triggered only by explicit, surfaced French actions
- void without French penalty whenever the basis disappears for reasons France did not directly choose

---

## 7. System Overview

### 7.1 Data concepts

- `diplomatic_commitments: Dict[str, Dict]` — keyed by stringified commitment id; stores active and terminal `war_bargain` records.
- `next_commitment_id: int` — monotonic id allocator.
- `pending_declaration` — primitive payload (keyed by `declaration_transaction_id`) carrying staged offensive war state during ally-entry resolution; lives in dialogue context, not in a parallel store.
- `join_opportunity` — explicit surfaced ally-entry record (id, beneficiary, named_enemy, request_type, surfaced_turn, hard_blocks, origin_episode_id, reroll_key).
- `fulfillment_snapshot` — terminal bargain payload preserved on the bargain record after `fulfilled` close.
- `commitment_event_metadata` — primitive payload attached to bargain dispatch / log events; carries `episode_id`, `end_reason_family`, `fault_nation`, `decision_reason`, `trigger_context`, deterministic deltas, and witness set at rupture.

### 7.2 Reused substrate (Memory and Pressure)

**Implementation note:** the substrate fields below (`episode_id`, `betrayal_history`, `scope_reason`, `warnings[]`, `hard_reject_posture`) are shipped. The live acceptance layer is `hegemony_target_mod` + `bilateral_betrayal_mod` + `grievance_modifier`, clamped by the `-60` composite floor. This spec adds `bargain_value_mod` and `bargain_conflict_penalty` to that live political subtotal; see §9 and `PEACE_DEALS_UMBRELLA_SPEC.md` §4.2.

- `episode_id` allocator for root-cause grouping
- `betrayal_history` strike memory with severity-scaled decay and per-episode strike cap of 2
- per-witness `scope_reason` resolution (ally / rival / shared_enemy / region_observer); region_observer scope is **only valid once the bargain store exists**, so it lights up here for the first time
- structured `warnings[]` payload contract in proposal previews
- `commitment_paradox` HARD_STOP machinery (paradox surface evolves under this spec to read from commitment conflict + bargain conflict, not just the legacy alliance-cross-war trigger). The canonical WorldState field is `commitment_paradox_popup`; legacy `alliance_paradox_popup` is load-side compatibility only.
- `hard_reject_posture` blocking deep-treaty acceptance after 3 active strikes

### 7.3 Coalition / opposition seams (v0.1 minimal)

Authored content in v0.1 still centers France as the only `war_bargain.promiser`. Code should keep `(ratifier, new_treaty)` and `(promiser, beneficiary, target_enemy, claim_region)` parameterized so the future `Coalition Generalization` follow-up can plug in non-France actors without rewriting the validators. **Do not** create a parallel `war_bloc` / `opposition_graph` store in v0.1.

Define one helper boundary for bargain eligibility:

```python
get_bargain_opposition_pairs(world, actor, beneficiary) -> set[tuple[str, str]]
```

In v0.1, this helper derives opposition only from current `WAR` states, live `active_coalition.target_nation` / current coalition members, and live `war_bargain` records whose named enemy, beneficiary, or claim-holder creates an explicit conflict. It must not read or create `nation_rivalries`, `nation_concerns`, authored rivalry seed data, or any cached static rivalry table. Future coalition generalization can expand this helper without changing the bargain record shape.

---

## 8. War Bargain Mechanic

### 8.1 Clause type

Add a new clause type:

- `war_bargain`

User-facing wording emphasizes: alliance orientation, named enemy, French claim priority. Backend key remains `war_bargain`.

Internal structure:

- `entry_term` — the ally aligns against the named enemy
- `claim_term` — France's priority over exactly one region held by that enemy

These stay on one record in v0.1, but later systems may consume them separately.

### 8.2 Origin modes

`origin_mode` enum:

- `treaty_clause` — authored as part of a ratified `DEFENSIVE_ALLIANCE` / `ALLIANCE` treaty package
- `counter_bargain` — issued as a `war_entry_counter_bargain` on an offensive ally-entry decision and ratified in `triggered` state

Later authoring paths append; do not overload existing values.

### 8.3 Authoring model

Bargains may be:

- AI-proposed and player-confirmed
- player-authored through a constrained structured picker
- raised as a war-entry counter-bargain when France asks an existing ally to join a specific war and that ally wants terms before entering

### 8.4 Valid bargain targets

A war bargain is valid only if **all** are true:

1. The source treaty is `DEFENSIVE_ALLIANCE` or `ALLIANCE`, or France is invoking the same-turn ally-entry decision for an existing military ally.
2. The named enemy is a current war enemy of France or the beneficiary, or appears as an opposed nation for France or the beneficiary in `get_bargain_opposition_pairs()`.
3. The claim region is currently controlled by the named enemy or that enemy's subject.
4. The claim region is strategically plausible for France: in `covets_regions`, previously French, adjacent to French territory, or otherwise flagged as high-interest by existing desire data.
5. The target nation has plausible participation access against the named enemy: direct border, allied-theater adjacency, or a 2-hop friendly/uncontrolled route implemented as `_has_bargain_participation_access()` in `diplomacy.py`.

Invalid uses:

- bargaining over ally territory
- bargaining over territory held by an unrelated third party
- bargaining over a region France has no plausible political interest in
- bargaining with a partner that cannot plausibly participate in the named war

### 8.5 Caps and contradiction guards

Caps:

- max 1 live bargain per beneficiary + named enemy pair
- max 1 live bargain claiming a given region
- max 1 bargain generated from a single treaty package or ally-entry decision

Hard contradictions (validation failures or hard-stop choices, not soft warnings):

- France may not create a bargain for Region X if France already has a live bargain on Region X.
- France may not create a bargain for Region X while holding `DEFENSIVE_ALLIANCE` or `ALLIANCE` with the current holder of X unless the player first downgrades that alignment through an explicit hard-stop flow.
- France may not create a bargain with Nation A against Nation B if France already holds a live bargain with Nation B against Nation A.
- France may not stack multiple bargain clauses into one treaty.
- One ally-entry decision may produce at most one counter-bargain from that ally on that turn.

### 8.6 Lifecycle

On ratification, create a tracked commitment:

```json
{
  "id": 17,
  "type": "war_bargain",
  "promiser": "France",
  "beneficiary": "Prussia",
  "origin_mode": "treaty_clause",
  "target_enemy": "Britain",
  "entry_term": {"named_enemy": "Britain"},
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
  "end_reason_family": null,
  "fault_nation": null,
  "trigger_context": null,
  "fulfillment_snapshot": null,
  "zombie_clock_turns_elapsed": 0,
  "dormant_notice_fired": false
}
```

Allowed statuses:

- `active` — bargain exists, target war not yet jointly fought
- `triggered` — France and beneficiary are co-belligerents against the named enemy while the bargain is live
- `fulfilled` — France gains the claimed region while the bargain is still valid
- `void` — basis disappeared without French bad faith
- `breached` — France explicitly reversed the bargain

Field notes:

- `triggered_turn` stores the most recent turn on which the bargain entered `triggered`.
- `trigger_context` stores `{request_type, resolution_path, was_bargain_decisive, origin_episode_id}` when triggered.
- Imperial Settlement may add optional war-context snapshot metadata when a bargain attaches to a `war_instance`: `war_id`, `side_at_creation`, and `side_leader_at_creation`. These fields are snapshots for settlement advisory/fulfillment classification. Merges may rewrite `war_id`, but leader replacement must not rewrite `side_leader_at_creation`; current leaders determine settlement authority, not the original bargain promise context.

Live-bargain rule:

- `live` means `active` or `triggered`. Caps, contradiction checks, AI anti-spam, and "active bargain" UI references should read `live` unless a rule explicitly names a narrower status.

v0.1 simplification (preserved):

- **no** `deadline_turn`
- **no** `suspended_turns`
- **no** periodic urgency-warning ladder

### 8.7 War-entry decision contract

Every player-visible ally-entry decision materializes as a `join_opportunity`:

```json
{
  "id": 3,
  "beneficiary": "Prussia",
  "named_enemy": "Britain",
  "request_type": "offensive_ally_request",
  "surfaced_turn": 10,
  "hard_blocks": [],
  "origin_episode_id": 5,
  "reroll_key": "Prussia|Britain|offensive_ally_request|10"
}
```

Rules:

- only explicit accept / reject / back out actions on a surfaced `join_opportunity` change bargain state through ally-entry resolution
- failure to surface a `join_opportunity` never creates breach by itself
- v0.1 must ship both the declaration-preview intercept **and** the later explicit in-war ally-entry request surface (so a temporarily blocked bargain does not strand)
- pending dialogue context for `join_opportunity` / `counter_bargain` serializes `context.origin_episode_id`, `context.reroll_key`, `context.join_opportunity`, `context.counter_bargain_context`, `context.declaration_transaction_id`, and `context.pending_declaration` when applicable

`pending_declaration` minimum fields:

```text
{declaration_transaction_id, aggressor_nation, target_nation,
 pending_ally_invites, staged_war_state_snapshot, turn_created}
```

Three France-facing ally-entry cases:

- `defensive_honor_call` — France is attacked / enters as defender. `DEFENSIVE_ALLIANCE` and `ALLIANCE` may answer.
- `offensive_ally_request` — France starts or widens a war against the named enemy. `ALLIANCE` may answer by default; `DEFENSIVE_ALLIANCE` may answer only when a live bargain explicitly targets that named enemy.
- `coalition_entry` — separate from alliance logic. Coalition membership is not an ally call and cannot be sweetened by `war_bargain`.

Hard blocks (preview shows the exact reason):

- armistice / cooldown or treaty lock with named enemy
- already on the enemy side of that war or a direct enemy of France
- active anti-France `war_bloc` membership in the current coalition model
- `hard_reject_posture` active (3+ bilateral betrayal strikes from France toward this nation) — applies to offensive ally requests only; defensive honor calls bypass this block because the treaty obligation itself overrides bilateral distrust
- no plausible participation path (direct border, allied-theater adjacency, or adjacency reachable within 2 hops through allied/neutral territory)
- any other backend contradiction creating invalid war state

### 8.7.1 Defensive honor calls

- Defensive honor never generates counter-bargains.
- After hard-block checks, eligible `DEFENSIVE_ALLIANCE` and `ALLIANCE` partners join automatically.
- No soft-refusal path for non-blocked defensive honor in v0.1.
- Hard-blocked defensive honor does **not** auto-break source treaty or bargain.
- Co-belligerence under a live bargain marks it `triggered` and stamps `triggered_turn`.

### 8.7.2 Offensive ally requests

- `+25` war-entry modifier when a valid live bargain targets the named enemy.
- Bargain surfaced in declaration preview.
- Two-phase transaction: resolve surfaced ally-entry / counter-bargain decisions first, then commit war-state mutation.
- `Back Out` on offensive `join_opportunity` keeps bargain `active` unless France takes another contradictory action.
- Entering war against the named enemy through another player-controlled route still triggers the same preview / `join_opportunity`.
- Using the alliance against some other enemy keeps the bargain `active`; no automatic breach.

### 8.7.3 War-entry counter-bargains and rerolls

An ally that did **not** negotiate at alliance time may still demand terms when France reaches an offensive ally-entry decision.

- Trigger only on offensive ally-entry decisions (declaration preview or later explicit request).
- If ally is not willing to join free but is within the bargain-salvage range, ally may issue one counter-demand.
- Counter-demand may create a new `war_bargain` tied to that named enemy and one French claim region.
- Player options: Accept (bargain created in `triggered`), Reject (declaration may proceed without ally), Back Out (declaration cancelled, no bargain).
- Reroll determinism: same ally + same enemy + same request type + same turn must reuse the same score band and demanded region unless a material state change occurs.
- `reroll_key = f"{beneficiary}|{named_enemy}|{request_type}|{turn_created}"`.
- Material state changes for reroll: treaty depth between France and beneficiary; France-beneficiary relation; beneficiary war load; coalition / bloc status involving beneficiary or named enemy; route-feasibility changes from beneficiary / named-enemy territorial / treaty / war-state changes; bargain-region availability changes from beneficiary / named-enemy war resolution.
- Enemy-phase actions within the same turn count as material changes if they alter any of the above inputs. Implementation should snapshot the `war_entry_score` inputs at first evaluation and compare on re-entry; reroll only if any input changed.
- Unrelated third-party treaty signings or unrelated route openings do **not** qualify as rerolls.
- Counter-bargains use the existing `proposal_confirm` shell with `counter_bargain_context` payload in **blocking** mode — do not create a second dialogue family.
- Counter-bargain mode **must suppress** envoy-leak affordances: `renegotiate`, envoy-in-transit status, DP cost display / DP spend, mailbox deferral, `dismiss` / "never mind." Only `Accept`, `Reject`, `Back Out` remain terminal.

Valid wartime asks: claim-recognition for one region held by named enemy; deepen alignment via the bargain itself.

Invalid wartime asks: ally-beneficiary land in final peace; multi-ally conference terms; break / downgrade demands against an ally's rival as part of the same counter-bargain; any allocation request among multiple participants.

### 8.7.4 Coalition overlap

- Alliances are bilateral and may be sweetened by `war_bargain`.
- Coalitions are bloc commitments with separate loyalty / separate-peace logic; they are **not** bargainable through claim-recognition terms.
- Coalition overlap should read from `active_coalition.target_nation` and the shared opposition-pair list (the generic war-bloc contract, once generalized, must expose the same target field).
- An active coalition whose `target_nation` equals the ally-entry initiator is a hard block on accepting that initiator's request (in v0.1 the only instantiated `active_coalition.target_nation` is France; the rule is written target-aware so the future `Coalition Generalization` follow-up does not require a rewrite).
- If the beneficiary joins a coalition whose `target_nation` equals the bargain's `promiser` first, any live bargain from that promiser to that beneficiary voids for contrary alignment.

### 8.8 Fulfillment

A bargain is `fulfilled` when **all** are true at the final post-processing state of the turn:

1. Bargain is `triggered`.
2. France controls the claimed region.
3. Region changed from named enemy or its subject to France while bargain remained valid.
4. France still holds `DEFENSIVE_ALLIANCE` or `ALLIANCE` with beneficiary.
5. Beneficiary is still a co-belligerent on France's side against the named enemy in that final state, or the named war ended that turn with both having been co-belligerents immediately before resolution.

Turn-order rule:

1. Resolve treaty ratifications, breaks, and downgrades.
2. Resolve war-state changes and region ownership (including vassal processing, which can change region control).
3. Resolve bargain status changes caused by those results.
4. Evaluate fulfillment / breach / void using the final state after all region-control mutations.

Exploit guard:

- Voluntary downgrade of source treaty on the same turn a bargain would otherwise fulfill counts as **explicit breach**, not cheap passive failure.
- `fulfilled` is terminal; later loss / trade / renunciation does not retroactively reopen.

On fulfillment, write `fulfillment_snapshot`:

```text
{claim_region, beneficiary, target_enemy, fulfilled_turn,
 reliability_delta, relation_delta, reward_reduced: str,
 intended_reliability_delta: int, witness_nations_at_fulfillment,
 trigger_context}
```

- `reward_reduced` field: `"none"` (full reward applied), `"partial"` (10-turn cap reduced but did not zero the delta), or `"full"` (10-turn cap zeroed the applied delta). `intended_reliability_delta` preserves the pre-cap value in all cases.
- `trigger_context.resolution_path` resolves to one of `defensive_auto_honor`, `offensive_free_join`, `offensive_bargain_helped`, `offensive_counter_bargain_accept`. `was_bargain_decisive = True` only when the bargain changed the ally from non-join / counter-bargain territory into a join outcome.

Reward (per Memory and Pressure §8.5):

- `+4` to `diplomatic_reliability[bargain.promiser]`, capped once per (promiser, beneficiary) per 10 turns
- `+6` relation with beneficiary

If named war ends without fulfillment:

- `triggered` bargain with valid source treaty + claim basis returns to `active`
- if war ending also destroyed claim basis or created contrary alignment, resolve through `void` rules instead

### 8.9 Breach and void

#### A. France-caused breach

A bargain is `breached` if France does any of the following while it is `active` or `triggered`:

- breaks source treaty voluntarily
- voluntarily downgrades source treaty below `DEFENSIVE_ALLIANCE`
- causes source treaty to auto-decay below `DEFENSIVE_ALLIANCE` through a constructive-breach action: (a) France ratifies `NON_AGGRESSION` or deeper with a nation opposed to the beneficiary under `get_bargain_opposition_pairs()` (including current war enemies and coalition-target conflicts), (b) France attacks an ally of the beneficiary, or (c) France ratifies a contradictory bargain whose named enemy is the beneficiary or the beneficiary's ally. Only these explicit French diplomatic choices count as constructive breach — passive relation drift from third-party events does not
- enters `NON_AGGRESSION` or deeper alignment with named enemy or current claim holder
- ratifies a contradictory bargain
- ratifies `PEACE`, `ARMISTICE`, or equivalent de-escalation with named enemy after a surfaced `peace_conflict` warning when normalization would terminate or cheapen the bargain before its political purpose is resolved
- explicitly renounces the French claim in a later peace flow once bilateral peace hardening adds term-level claim warnings

Effects:

- relation penalty with beneficiary: `-10`
- betrayal strike: `+1` unless the same episode already spent the 2-strike cap through a source alliance break
- global reliability loss: `-6`
- 6-turn cooldown on new bargains for that same pair + named enemy
- dispatch / campaign log freezes `end_reason_family = "french_breach"`, `fault_nation = France`, witness set at rupture, deterministic deltas

#### B. Void without French penalty

A bargain is `void` if its basis disappears without French bad faith. Two sub-families:

`counterparty_reversal`:

- beneficiary breaks source treaty first
- source treaty auto-decays below `DEFENSIVE_ALLIANCE` through beneficiary-caused changes France did not directly choose
- beneficiary enters `NON_AGGRESSION` or deeper alignment with named enemy first
- beneficiary joins a coalition directed against France first
- beneficiary refuses a bargain-backed ally-entry request

`obsolescence_or_external`:

- target enemy stops holding claimed region through outside events not chosen by France
- named enemy or claim region basis disappears
- France pulled into contrary war against beneficiary through third-party cascade France did not directly declare (this includes cascades that arise from France's existing alliance network — the test is whether France explicitly chose **this specific war entry**, not whether France's prior alliances made it foreseeable)
- France and beneficiary become direct enemies through beneficiary-caused or external scripted state France did not directly choose
- "zombie bargain" lapse: `zombie_clock_turns_elapsed` increments each turn where France is at `ARMISTICE` or higher with the named enemy AND beneficiary is at `ARMISTICE` or higher with the named enemy. When the counter reaches **5**, the bargain voids. The counter resets to 0 only if either France or the beneficiary re-enters `WAR` with the named enemy. A brief re-declaration followed by immediate armistice does **not** reset the counter — only actual `WAR` state does. `ARMISTICE` qualifies because it represents a de facto end of hostilities; without this, a bargain could strand indefinitely if both sides sit in `ARMISTICE` without progressing to `PEACE`

Void effects:

- no French reliability loss
- no French betrayal strike
- 4-turn cooldown on same pair + named enemy
- dispatch / campaign log states why, including `end_reason_family`, `fault_nation` when applicable, `decision_reason` when counterparty made an explicit surfaced choice
- explicit counterparty reversals do **not** silently collapse into generic obsolescence; they remain penalty-free for France but stay mechanically distinct so downstream presentation can stage abandonment vs opportunism

#### C. Explicit `repudiate_bargain` action

- v0.1 ships one explicit `repudiate_bargain` action on live bargains.
- Blocking confirmation; resolves immediately as French breach using the penalties / cooldown above.
- Does **not** refund prior value, preserve goodwill, or bypass source-treaty fallout.

---

## 9. Acceptance formula additions

**Canonical source:** `PEACE_DEALS_UMBRELLA_SPEC.md` §4.2. War Bargains extends the live `calculate_acceptance()` political subtotal; it does not resurrect the superseded rivalry-composite model.

### 9.1 `bargain_value_mod`

- `+10` when sweetening `DEFENSIVE_ALLIANCE`
- `+15` when sweetening `ALLIANCE`

The `+25` live-bargain bonus is not part of ordinary `calculate_acceptance()`. It belongs only to the dedicated war-entry / ally-entry evaluation in §9.4.

Integration:

- when a tracked `war_bargain` clause is present, `bargain_value_mod` replaces any old static sweetener that covers the same claim-support concept
- when no tracked bargain clause is present, the old static bonus may remain
- never double-count static sweetener + tracked bargain for the same idea

### 9.2 `bargain_conflict_penalty` (live-bargain term)

When France holds a live bargain against a target, or a live bargain over territory currently held by that target, add `bargain_conflict_penalty = -8` to the live political subtotal before the composite floor clamp.

Rules:

- Apply at most one bargain-conflict penalty per proposal target.
- Do not double-count multiple bargains that create the same target conflict.
- The `-60` composite floor in §9.3 remains authoritative after adding this term.

### 9.3 Composite re-cap

The live political subtotal in `calculate_acceptance()` becomes:

```python
political_subtotal_raw = (
    hegemony_target_mod
    + bilateral_betrayal_mod
    + grievance_modifier
    + bargain_conflict_penalty
    + bargain_value_mod
)
political_subtotal_clamped = max(-60, political_subtotal_raw)
```

`bargain_value_mod` is positive and can counteract hegemony / betrayal / grievance pressure. `bargain_conflict_penalty` is negative and makes normalizing with a bargain target harder. Both surface as independent component rows for preview / debug legibility.

**Relationship to existing `reliability_modifier`:** the existing `calculate_acceptance()` in `diplomacy.py` includes `reliability_modifier = max(-6, min(6, reliability // 10))`. The political subtotal above is a separate, parallel group that captures pair-specific political pressure. It does not replace `reliability_modifier`, which stays as the global reputation input. Both contribute independently to the final acceptance score.

### 9.4 Dedicated `war_entry_score`

War entry should not piggyback on the generic treaty acceptance score. Use a dedicated `war_entry_score`. Evaluate hard blocks before the score; if any hard block is present, ally does not join and no counter-bargain is offered.

Inputs:

- `base = 20`
- treaty depth: `DEFENSIVE_ALLIANCE +10`, `ALLIANCE +18`
- defensive honor bonus when France is defender: `+18`
- hostility toward named enemy: `clamp((-relation_to_enemy) // 5, -10, +10)`
- if the named enemy is opposed to the beneficiary under `get_bargain_opposition_pairs()`: additional `+6`
- France-beneficiary relation: `clamp(relation_to_france // 5, -12, +12)`
- bilateral betrayal strikes: `-8` each, cap `-24`
- promiser global reliability: `clamp(diplomatic_reliability[promiser] // 10, -6, +6)`
- matching live bargain: `+25`
- other-war load: `-8` for one other active war, `-18` for 2+ or war exhaustion `>= 60`

Global reliability is a light input only; bilateral betrayal and treaty depth dominate. The `// 10` divisor and `±6` clamp match the live acceptance formula; if acceptance-formula reliability scaling changes later, revisit `war_entry_score` deliberately rather than copying changes by accident.

Thresholds:

- `50+` — join without terms
- `25-49` — may issue one counter-bargain on offensive requests only
- `< 25` — refuse
- defensive honor calls auto-resolve as join after hard-block checks; score still computed for preview / debug, not used as a second defensive gate

---

## 10. Player-facing surfaces

### 10.1 Bargain Review (mandatory)

Every offer containing a `war_bargain` clause passes through a Bargain Review stage before send / accept.

The review card is the core new v0.1 promise surface and inserts as the final stage inside the existing `proposal_confirm` flow. It inherits the existing `proposal_confirm` CanvasLayer and dialog-manager registration; it is not a separate popup family.

Review must show:

- beneficiary, named enemy, claim region, current holder, source treaty
- contradiction warnings
- main likely offended third party
- exact current war-entry forecast band: `join`, `counter-bargain likely`, `refuse`
- whether the bargain is currently decisive or merely supportive
- whether this action would create a third strike and trigger `hard_reject`
- practical effect in plain language: "This shifts Prussia from counter-bargain to join against Britain"
- any deterministic direct fallout if the bargain requires a prior downgrade or breaches an attached commitment

Layout:

- bargain summary + top 1-2 warnings above action buttons
- forecast band + decisive readout before action buttons
- reused for war-entry counter-bargains via `counter_bargain_context` in **blocking** mode, with envoy-leak affordances suppressed (per §8.7.3)

### 10.2 Required warning moments

- bargain ratification
- war declaration on the named enemy
- peace / armistice / normalization with named enemy or current holder while bargain is live
- source treaty downgrade / break while bargain is live
- deep treaty ratification with named enemy or current holder
- any action that would create the third active strike against a nation
- bargain void / breach / fulfillment

**No periodic per-turn bargain reminders.** Warnings are event-driven. **Exception:** if a bargain has been `active` for 8+ consecutive turns without entering `triggered`, a single one-time dispatch notice surfaces as a low-priority reminder (not a warning). This fires once per bargain (`dormant_notice_fired` flag on commitment record), not per turn, to prevent fatigue while catching dormant commitments players may have forgotten. If the bargain transitions to `triggered` and later reverts to `active` (inconclusive war), the `dormant_notice_fired` flag resets and the 8-turn clock restarts from the reversion turn.

### 10.3 Diplomatic Ledger additions

- live bargains owed to or from each nation
- bargain cooldown notice when relevant
- named-enemy bargains in the active treaties tab
- claim region, current holder, status (`active`, `triggered`, `fulfilled`, `void`, `breached`)

### 10.4 Dispatch and campaign log events

This spec adds eight new event types:

- `bargain_ratified`
- `bargain_triggered`
- `bargain_fulfilled`
- `bargain_breached`
- `bargain_voided`
- `hard_block_surfaced` (ally-entry hard block — notice tier only unless downstream consequence)
- `ally_refused_free_join` (notice tier)
- `declaration_backed_out` (notice tier; counter-bargain Back Out terminal — no "Ally refused" notice fires; only this campaign-log entry)

Campaign-log metadata payload:

- bargain id, beneficiary, target enemy, claim region
- previous status, new status
- end reason, end reason family, fault nation, decision reason
- witness nations with `scope_reason`
- trigger context
- relation delta, reliability delta
- for paradox events: chosen nation and spurned nation

Compact one-line campaign-log rendering. Full metadata stays on the event record for tooltip / expand affordances.

Per-event one-liner and fog contract:

| Event | One-liner template | Fog rule |
|-------|--------------------|----------|
| `bargain_ratified` | "{promiser} and {beneficiary} ratified a bargain against {target_enemy}: French priority claim on {claim_region}." | Public to all known courts. |
| `bargain_triggered` | "{beneficiary} joins against {target_enemy}; the bargain over {claim_region} is now active." | Public to all known courts. |
| `bargain_fulfilled` | "{promiser} honored the bargain: {claim_region} secured under France's claim." | Public to all known courts. |
| `bargain_breached` | "{fault_nation} broke the bargain with {beneficiary} over {claim_region}." | Public to all known courts; scoped witness payloads drive relation fallout. |
| `bargain_voided` | "Bargain with {beneficiary} over {claim_region} lapsed ({end_reason})." | Public to France and directly involved nations; scoped witnesses see it only when listed in `witnesses`. |
| `hard_block_surfaced` | "{beneficiary} cannot join against {target_enemy}: {hard_block_reason}." | Player only unless a downstream state change occurs. |
| `ally_refused_free_join` | "{beneficiary} declined to join against {target_enemy} without terms." | Public to France and the refusing ally; scoped witnesses only if refusal creates a commitment event. |
| `declaration_backed_out` | "{promiser} withdrew the declaration against {target_enemy}." | Player only; no diplomatic fallout by itself. |

### 10.5 Presentation pass (landed in WB-D)

The full bargain presentation pass — split-voice spotlight for `bargain_fulfilled` / `bargain_breached`, `dominant_witness_scope`-branched copy, named-diplomat envoy resolution at bargain ratification and breach — landed in WB-D as the bargain-era continuation of `COMMITMENTS_PRESENTATION_SPEC.md`.

WB-D extends the presentation pass with:

- `bargain_fulfilled` spotlight + Talleyrand vindication line + N+1 callback
- `bargain_breached` split-voice spotlight (lead = injured-party named diplomat per Voice Bible, witness = scoped court reaction, aside = Talleyrand) + N+1 aftermath
- `dominant_witness_scope`-branched copy for breach
- `Propose redress to {injured_party}` response route on breach (opens existing `proposal_options`)
- `Deepen the bond with {primary_nation}` response route on fulfillment
- `Attempt to reopen the chancery` route on hard-reject (low-acceptance preview)

Those specifics live with this spec, not back-ported into Memory and Pressure presentation.

---

## 11. AI Behavior

### 11.1 Proposal generation

AI may generate a bargain only if **all** are true:

- valid bargain under pair + enemy and same-region constraints
- no live same-region contradiction
- named enemy is a current war enemy or a current opposition-pair target under `get_bargain_opposition_pairs()`
- claim region held by that enemy or its subject
- target nation has plausible participation access
- target nation has at least one active marshal AND either direct / front-access relevance to named enemy OR total active field strength >= 25% of France's
- no obvious contradiction with France's current deep ally network
- same pair + target enemy is not on bargain cooldown
- timing belongs on military treaty creation / upgrade or at war-entry time when ally is close enough to salvage with terms

Every AI-authored offer, refusal, counter-bargain, hard block, or counterparty reversal emits one deterministic `decision_reason`. This spec extends the Memory and Pressure enum with bargain-specific reasons:

- `claim_trade` — accepting because the bargain offers a desired claim recognition
- `counterparty_reversal` — refusing / voiding because France's prior alignment removed credibility
- `claim_obsolete` — refusing / voiding because the named region basis has disappeared

### 11.2 Anti-spam

AI must not:

- propose a bargain when France already has a live bargain with that nation
- chain multiple bargain requests in consecutive turns after void or breach
- offer bargains the target cannot plausibly help fight over
- issue a war-entry counter-bargain that asks for ally-beneficiary land or any other multi-party settlement outcome

### 11.3 Refusal behavior

AI should refuse or resist:

- new bargains from a promiser with severe betrayal memory
- deep treaties at 3 active victim-side strikes (already shipped via hard-reject posture)
- bargains whose claim basis is currently held by an ally of the AI

### 11.4 War-entry behavior

If a valid bargain exists against the named enemy:

- AI values joining that war more highly (`+25` on `war_entry_score`)
- AI surfaces the reason in advisory / preview text
- if AI refuses anyway, bargain ends with `end_reason_family = counterparty_reversal`, no French penalty, and explicit `decision_reason`

### 11.5 Performance / architecture guard

- no new hot-path per-region scans
- scoped `get_bargain_opposition_pairs()` reads cached only for the current validation call; no static rivalry store or authored rivalry lookup is introduced
- direct commitment-id and pair-key reads
- targeted validation on bargain creation and key event hooks

---

## 12. Data model additions

Scale-hardening amendment: terminal bargain records move from `diplomatic_commitments` to `archived_diplomatic_commitments` after a 10-turn grace period, keeping live lifecycle and breach scans bounded while preserving history.

### 12.1 New WorldState fields

- `diplomatic_commitments: Dict[str, Dict]` — bargain records keyed by commitment id (string)
- `archived_diplomatic_commitments: List[Dict]` — terminal bargain records moved out of live scans after the 10-turn grace period; default `[]`; serialized through `WorldState.to_dict()` / `from_dict()`
- `next_commitment_id: int` — monotonic id

### 12.2 Cooldown contract

- cooldown lookups key off `cooldown_key = source_pair + "::" + target_enemy`, not the commitment id, so breach / void anti-spam persists across bargain replacement and save/load
- `source_pair` uses canonical `promiser|beneficiary` ordering; storage stays promiser-aware even though authored v1.0 content centers France

### 12.3 Save/load and pending dialogue

- `pending_declaration` persists as primitive payload inside dialogue context per §8.7
- counter-bargain `proposal_confirm` instances in blocking mode reference `pending_declaration` via `declaration_transaction_id`
- zombie-bargain void clock (§8.9.B) requires a serialized `zombie_clock_turns_elapsed` per commitment so save/load mid-clock preserves continuity (this field is not in the original spec §13 — adding it here so v1.0 implementation does not miss the seam)
- **Mid-transaction save/load recovery:** if save/load occurs while a `join_opportunity` or `counter_bargain` dialogue is active, the serialized dialogue context must restore the blocking popup on reload. The player sees the same Accept/Reject/Back Out choice with the same `reroll_key` and score band. No implicit resolution on load — the transaction resumes exactly where it left off

### 12.4 Region-observer witness scope (re-activated)

The Memory and Pressure substrate stubs `region_observer` scope but never returns it (no bargain store). With this spec live, witness classification reactivates the stub:

- `region_observer` — witness has a live bargain over the same claim region as the broken obligation
- precedence stays `ally > rival > shared_enemy > region_observer`

### 12.5 Multi-bargain witness scoping

When France breaches bargain #1 (e.g., with Prussia against Britain), witness classification for the breach event uses the standard scope precedence against the **injured party** (Prussia), not against France. A nation holding an unrelated bargain #2 with France (e.g., Austria against Russia) witnesses the breach only through its normal scope relationship with Prussia — `ally`, `rival`, `shared_enemy`, or `region_observer` of the same claim region. Holding an unrelated bargain with France does **not** create a new witness scope category. This prevents cross-contamination: a bargain breach in one theater should not poison an unrelated bargain's beneficiary through artificial witness amplification.

---

## 13. Implementation Sequence

### Slice WB-A. Data model + creation + validation

- Add `diplomatic_commitments` + `next_commitment_id` to WorldState
- `to_dict` / `from_dict` with `.get()` defaults
- Update `SAVE_FORMAT_REFERENCE.md`
- Add `war_bargain` clause type to acceptance / display
- Add `bargain_value_mod` and `bargain_conflict_penalty` to `FEEDBACK_STRINGS` in `display_names.py` and the `_generate_feedback` trackable set in `diplomacy.py`
- Implement `get_bargain_opposition_pairs()` from current WAR states, `active_coalition.target_nation` / members, and live bargain conflicts only; do not read `nation_rivalries` or authored rivalry seed data
- Validation: named enemy, claim region holder, French strategic interest, beneficiary participation feasibility, caps, cooldowns, contradiction guards
- Hard-stop preview for bargain creation when France must first downgrade an existing deep treaty
- Activate `region_observer` witness scope branch
- ~22 tests

### Slice WB-B. Lifecycle: fulfillment + breach + void

- Status transitions `active` → `triggered` → `fulfilled` / `void` / `breached`
- Zombie-bargain void clock: serialized `zombie_clock_turns_elapsed` increments on each qualifying turn where France and the beneficiary are both ARMISTICE-or-higher with the named enemy; it voids at 5 and resets only if either side re-enters WAR with the named enemy
- Fulfillment check in `advance_turn()` per §8.8 turn-order rule
- `fulfillment_snapshot` write on fulfillment
- Inconclusive war reactivation: `triggered` → `active` when source treaty + claim basis still valid
- Breach detection: source treaty break, voluntary downgrade below `DEFENSIVE_ALLIANCE`, constructive breach via French-engineered auto-decay, normalization with named enemy / holder, peace / armistice resolution after surfaced `peace_conflict`, contradictory bargain, explicit French claim renunciation in later peace flow, explicit `repudiate_bargain`
- Void detection: `counterparty_reversal` vs `obsolescence_or_external` classification per §8.9.B
- `fulfilled` terminal — no retroactive reopen
- 6-turn cooldown on breach, 4-turn cooldown on void (keyed by `cooldown_key`)
- Dispatch + campaign log events with required metadata
- Same-turn downgrade exploit guard (§8.8)
- ~32 tests

### Slice WB-C. War-entry integration + Bargain Review + AI rules

- Visible structured bargain picker in diplomacy wizard for eligible military treaties
- Mandatory Bargain Review stage in `proposal_confirm` flow per §10.1
- Pre-war warning when France declares on named enemy with live bargain
- Peace / armistice warning when France normalizes with named enemy with live bargain
- Replace offensive silent cascade with surfaced `join_opportunity` / `AllyEntryPipeline` in declaration preview
- Transactional offensive declaration preview (§8.7.2)
- Later explicit in-war ally-entry request surface for temporarily blocked bargains
- Split war-entry handling: defensive honor calls, offensive ally requests, coalition-overlap hard blocks
- `war_entry_counter_bargain` flow with `counter_bargain_context`, blocking mode, suppressed envoy affordances
- `pending_declaration` primitive payload serialized in dialogue context
- Counter-bargain `Back Out` cancels pending declaration, refunds DP / AP, not re-entrant within same turn; emits `declaration_backed_out` campaign-log entry only (no "Ally refused" notice)
- Structural bargain caps + deterministic same-turn reroll memory per §8.7.3
- Hard-block reason surfacing
- Dedicated `war_entry_score` per §9.4 with `50+` join / `25-49` counter-bargain / `<25` refuse thresholds; defensive honor auto-join after block checks
- `+25` war-entry score bonus when valid bargain targets named enemy
- `trigger_context` capture on bargain trigger
- Anti-France coalition overlap hooks (§8.7.4) without coalition generalization
- Extend paradox popup to surface attached bargain-breach / reliability fallout
- Ledger: live bargains with named enemy, claim region, holder, status, cooldown
- `repudiate_bargain` confirm surface routed into WB-B breach rules
- Wire `repudiate_bargain` per CLAUDE.md "Adding a New Action": `VALID_ACTIONS` in `validation.py`, parser valid-actions, `_action_costs` in `world_state.py` (1 AP), mock parser keywords (`repudiate bargain`, `break bargain`, `renounce bargain`), `ACTION_DISPLAY` in `display_names.py`, campaign-log type `bargain_breached` in `campaign_log.py`, and defiance / objection display mappings for any surfaced fallout
- AI bargain generation with feasibility gates and full v1.0 `decision_reason` enum (§11.1)
- AI anti-spam (§11.2)
- AI counter-bargain timing and refusal (§11.3-§11.4)
- ~52 tests (increased from 44 to account for reroll determinism, counter-bargain suppression, and multi-bargain witness scoping)

**Sub-division guidance if the session ceiling is reached:**

- **WB-C1: War-entry integration + declaration preview + hard blocks** (~20 tests)
- **WB-C2: Bargain Review + counter-bargain flow + reroll determinism** (~16 tests)
- **WB-C3: AI rules + anti-spam + ledger + repudiate surface** (~16 tests)

### Slice WB-D. Bargain-era presentation extension

Extend `COMMITMENTS_PRESENTATION_SPEC.md` (currently `C3-lite`) with bargain spotlights:

- `bargain_fulfilled` spotlight + Talleyrand vindication line + N+1 callback
- `bargain_breached` split-voice spotlight + N+1 aftermath
- `dominant_witness_scope`-branched breach copy
- `Propose redress` / `Deepen the bond` / `Attempt to reopen the chancery` response routes (open existing `proposal_options` / `proposal_confirm` surfaces)
- `bargain_ratified` / `bargain_triggered` / `bargain_voided` notices with period labels per Voice Bible
- ~18 tests

---

## 14. Risks

### R1. Bargain scope creep

If war bargains quietly turn back into ally-land promises, the old agency problem returns. **Mitigation:** France only as claimant, single region only, named enemy required, no deadline system.

### R2. Contradiction opacity

If the system allows hidden mutually impossible bargains, AI and players will both break it. **Mitigation:** one live bargain per region, one live bargain per beneficiary + named enemy pair, hard-stop contradictory-alignment checks.

### R3. Warning overload

If warnings fire every turn, players stop reading them. **Mitigation:** event-driven warning model only, no timer ladder, preview capped to 2 inline warnings.

### R4. Peace-hardening dependency

Bilateral peace hardening must land first so peace with the named enemy can preview bargain breach before the player commits. **Mitigation:** this spec is explicitly gated on `Bilateral Peace Hardening`.

### R5. France-centric coalition assumptions

If bargain validation hard-codes coalition overlap as "anti-France only," later coalition generalization becomes much harder. **Mitigation:** keep helpers parameterized; do not create parallel `war_bloc` / `opposition_graph` stores until the generalization spec asks for them.

### R6. Armistice duration dependency resolved

`DIPLOMACY_SPEC.md` previously had stale 3-turn armistice references. `PEACE_DEALS_UMBRELLA_SPEC.md` §4.1 canonizes **5 turns**, matching live code, and the active DIPLOMACY_SPEC references have been corrected. The zombie-bargain void clock is agnostic to the minimum duration — it counts any turn at ARMISTICE or higher — but implementation should assume the canonical 5-turn armistice window.

### R7. Dual acceptance formula maintenance

`war_entry_score` (§9.4) runs parallel to `calculate_acceptance()` with intentionally different reliability scaling. Two score systems with different constants for similar concepts will confuse future contributors. **Mitigation:** document the intentional divergence in both the spec (done in §9.4) and in code comments on `war_entry_score()` at implementation time. Consider consolidating into a shared base with mode-specific overrides in a future refactor if maintenance cost proves real.

---

## 15. Resolved design calls (carried from RELIABILITY_COMMITMENTS_SPEC.md v1.0)

- **Gate 3 — Timed territorial promises vs narrower war bargains:** war bargains chosen.
- **Gate 4 — Promise deadlines / suspension model:** cut entirely. No `deadline_turn`, no `suspended_turns`, no urgency ladder.
- **Gate 5 — AI-authored only, or limited player-authored bargaining too:** allow limited player-authored bargaining via constrained structured picker.
- **Gate 6 — Hard-reject threshold:** keep 3 strikes, cap strike gain to 2 per episode (already shipped in Memory and Pressure substrate).
- **Gate 7 — Ally-beneficiary land promises in v0.1:** defer to `Ally Participation + Common Peace`.
- **Gate 8 — Global bargain cap or structural caps:** structural caps only.
- **Gate 9 — Coalition obligation or alliance obligation:** distinct textures with explicit overlap rules.

---

## 16. Changelog

- **April 16, 2026** — v1.0 extracted from `RELIABILITY_COMMITMENTS_SPEC.md` v1.0 §6.4 / §9 / §10.4 / §10.5 / §12.3 / §12.4 / §13 during the v2.0 rescope. Bargain mechanic deferred from Memory and Pressure ship; this spec carries the full bargain layer as a Peace Deals phase precursor. Added `zombie_clock_turns_elapsed` save-load seam (§12.3) and explicit composite-floor-supersedes-cap note (§9.3) — both flagged in the original audit. Region-observer witness scope (§12.4) reactivated here since the original substrate stubbed it pending bargain store.
- **April 16, 2026** — v1.1 edge-case audit (two rounds). Round 1 (13 findings): (CD-1) fixed shipped modifier count from "two" to "three" and corrected §10→§9 section reference; (CD-2) added commitment_paradox rename dependency note in §7.2; (CD-3) aligned commitment-pressure wording with the live hegemony/betrayal/grievance subtotal rather than a legacy modifier name; (E-1) fixed zombie clock to start at ARMISTICE, not PEACE, preventing indefinite stranding; (E-2) replaced vague "directly angered" constructive breach with bright-line trigger list; (E-3) added hard_reject_posture to hard-block list for offensive ally requests, defensive honor bypasses; (E-4) clarified enemy-phase material changes qualify for reroll; (E-5) added §12.5 multi-bargain witness scoping to prevent cross-contamination; (E-7) clarified cascade void applies even when France's alliances made it foreseeable; (E-8) replaced boolean reward_capped with three-value reward_reduced enum; (A-1) explicitly excluded AI-to-AI bargains in v0.1; (A-2) added mid-transaction save/load recovery rule in §12.3; (A-3) defined participation-access heuristic in hard-block list; (F-1) noted intentional war_entry_score reliability divergence; (PX-1) added 8-turn dormant-bargain one-time dispatch notice. Round 2 (8 findings from 3-agent design/code/cross-doc review): added §7.2 implementation note that acceptance modifiers are designed but not yet in code (Memory and Pressure v2.1 prerequisite); added `zombie_clock_turns_elapsed` and `dormant_notice_fired` to §8.6 JSON example; changed zombie clock from continuous to cumulative counting (prevents re-declare-to-reset exploit); added vassal processing to §8.8 turn-order rule; specified dormant-notice flag reset on triggered→active reversion; added `join_opportunity` typed JSON example in §8.7; added R6 (DIPLOMACY_SPEC armistice contradiction) and R7 (dual formula maintenance) to Risks; bumped WB-C test count from 44 to 52.
