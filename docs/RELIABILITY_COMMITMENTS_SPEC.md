# Memory and Pressure Spec

> **Status:** v2.0 (rescope)
> **Date:** April 16, 2026 (rescope); v1.0 April 14, 2026
> **Phase placement:** Design Refinement queue item 1 (formerly "Reliability + Commitments"; renamed in v2.0).
> **Companion docs:** `RELIABILITY_IMPLEMENTATION_PLAN.md`, `COMMITMENTS_PRESENTATION_SPEC.md` (the `C3-lite` presentation pass), `WAR_BARGAIN_SPEC.md` (bargain mechanic, deferred to Peace Deals phase).

---

## v2.0 rescope note (April 16, 2026)

The April 16 audit established:

- The substrate (betrayal memory, episode_id threading, witness `scope_reason`, hard-reject posture, structured `warnings[]`, paradox episode continuity) is **shipped and tested** (~220 targeted tests passing).
- The promise mechanic (`war_bargain` / `diplomatic_commitments` / `join_opportunity` / `counter_bargain` / `war_entry_score`) was **never implemented** and is not buildable in a single phase together with the substrate.
- The acceptance-formula integration of the substrate (graduated `bilateral_betrayal_mod`, `direct_rivalry_mod`, `rival_conflict_mod`, third-party rival anger on ratification, rivalry seed data) was **partially missing**.
- The presentation spec was specced two audit rounds deep (`C3a` + `C3b`) for events that the engine cannot produce.

The rescope:

1. **War bargains move out** to `WAR_BARGAIN_SPEC.md`, scheduled in the Peace Deals phase after `Bilateral Peace Hardening` and `War Purpose + Score Semantics`.
2. **Phase rename:** `Reliability + Commitments` → `Memory and Pressure`. The new name reflects the actual scope: betrayal memory + rivalry / formula pressure + the legacy paradox renamed.
3. **Scope what remains to ship:** seed `nation_rivalries`, fill the acceptance formula with the spec values for the modifiers we have data for, wire third-party anger on treaty deepening, rename `alliance_paradox` to `commitment_paradox`, and ship the narrow `C3-lite` presentation pass.
4. **Presentation rescope:** `COMMITMENTS_PRESENTATION_SPEC.md` collapses `C3a` + `C3b` into one `C3-lite` slice that delivers the named-diplomat / spotlight-tier / split-voice flavor for the events that *do* fire today.

This spec covers the engine half of the rescope. Bargain content is preserved in `WAR_BARGAIN_SPEC.md` so nothing is lost; section numbers below intentionally skip slots that moved (e.g. former §9 is now in `WAR_BARGAIN_SPEC.md` §8).

---

## 1. Purpose

Memory and Pressure defines the political-memory and political-pressure layer for v0.1 diplomacy:

1. Nations remember betrayal in a way that changes both numbers and posture.
2. Nations care who France aligns with — rivalry creates real friction and forced choices.
3. The acceptance formula expresses graded political pressure, not only a binary hard-reject gate.

It deliberately does **not** ship a promise mechanic. Promises (war bargains) need bilateral peace hardening and war-purpose semantics underneath them; they live in `WAR_BARGAIN_SPEC.md`.

---

## 2. Problems To Solve

### P1. Universal friendship is too easy

France can drift toward broad friendship unless rivals punish opposite-camp alignment hard enough to force tradeoffs.

### P2. Betrayal memory is too shallow

Breaking a treaty hurts in the moment, but the game still lacks enough durable bilateral memory to make repeated bad faith structurally costly.

### P3. The acceptance formula doesn't yet use the memory

Even after the substrate ships, the live formula treats betrayal as a 0-or-100 gate (under 3 strikes nothing changes; at 3 strikes the door closes). No graded pressure.

### P4. Big political moments still land as log lines

`hard_reject_posture_triggered`, `commitment_paradox_resolved`, and `diplomatic_treaty_broken` (french_breach) all emit rich payloads and render as one-liner notifications. The `C3-lite` pass closes that gap.

---

## 3. Goals

- Make alliances politically costly rather than purely additive.
- Separate "France is generally reliable" from "this nation thinks France betrayed it."
- Express both as graded numeric pressure on acceptance, not only as a brute-force gate.
- Make the moments that matter (door-closing, paradox, betrayal) feel like political events.
- Keep rules machine-readable for AI and tests.
- Keep the first implementation legible on the current 5-nation / 19-region map.

---

## 4. Non-Goals

- No war bargains, ally-entry pipeline, counter-bargains, `join_opportunity`, `pending_declaration`, or `war_entry_score` (all in `WAR_BARGAIN_SPEC.md`).
- No common peace, ally beneficiaries, conference-style spoils allocation.
- No new diplomacy screen family — extends existing wizard / popup / ledger / dispatch surfaces.
- No dynamic power tiers, bloc pressure, or strategic focus.
- No periodic per-turn bargain reminders or warning ladders (event-driven only).
- No coalition generalization (defer to D2 follow-up); evaluators stay parameterized but data stores stay anti-France-only in v0.1.

---

## 5. Design Principle

Political pressure in v0.1 has three layers:

1. **Rivalry pressure** — nations care who France aligns with.
2. **Reliability memory** — nations care whether France generally keeps its word.
3. **Bilateral betrayal memory** — nations care what France did to them specifically.

The rule that governs the spec:

- only punish the player for outcomes France could actually shape
- only explicit, player-surfaced obligations may create breach or betrayal

That means:

- no breach states triggered by AI inactivity alone
- no invisible contradictory obligations
- breach is recorded only on the player's explicit confirmed action

---

## 6. System Overview

The pressure layer has four player-facing data concepts plus shared engine seams.

### 6.1 Global reliability (already shipped)

- `world.diplomatic_reliability: Dict[str, int]` — nation-keyed shared global reputation scalar.
- Storage and emit paths stay actor-aware (no France-literal hardcodes).
- Used for broad acceptance modifiers and ledger summaries.

### 6.2 Bilateral betrayal memory (already shipped)

- `world.betrayal_history: Dict[str, Dict]` — directional key `from_nation|to_nation`.
- Value: `{strikes: List[StrikeRecord], categories: Set[str], last_turn: int}`.
- Each `StrikeRecord` is `{severity, turn, episode_id, decays_on_turn}`.
- Episode-cap queries filter by `episode_id`; severity-scaled decay reads each strike's own `decays_on_turn`.
- Pair-level `last_turn` is cached "most recent offense" for ledger only — not authoritative for decay or cap enforcement.

### 6.3 Rivalries (data missing — this phase ships it)

- `world.nation_rivalries: Dict[str, Dict]` — pair key `diplo_key`.
- Value: `{intensity, source, weight, started_turn, last_changed_turn}`.
- v0.1 ships **3 authored seeded pairs only**; no dynamic formation.

### 6.4 War bargains

**Moved to `WAR_BARGAIN_SPEC.md`.** Memory and Pressure does not implement `diplomatic_commitments` or `next_commitment_id`. The substrate code stubs `region_observer` witness scope pending the bargain store; that branch reactivates when `WAR_BARGAIN_SPEC` lands.

### 6.5 Shared engine seams (already shipped)

- `episode_id` — root-cause identifier on all diplomatic consequences from one explicit trigger; enforces strike caps by cause, not by whole turn. Allocator is `_allocate_episode_id(world)`; counter is `world.next_episode_id` (serialized).
- `commitment_event_metadata` — primitive payload on dispatch / campaign-log events: `episode_id`, `end_reason_family`, `end_reason_action`, `fault_nation`, `decision_reason`, `trigger_context`, deterministic deltas, `witnesses[].scope_reason`, `dominant_witness_scope`.

`opposition_graph` and `war_bloc.target_nation` seams are intentionally **not** stood up in v0.1 (cut in the rescope). When `WAR_BARGAIN_SPEC` and the later `Coalition Generalization` follow-up land, helpers parameterized on `(ratifier, new_treaty)` and `(actor, victim)` accept opposition pairs from a future `get_opposition_pairs()` helper without needing rewrites.

---

## 7. Rivalry System

### 7.1 Starting rivalries (this phase ships seeding)

Initial set:

| Pair | Weight | Intensity | Why |
|------|--------|-----------|-----|
| France ↔ Britain | `primary` | `active` | Core geopolitical enemy pair |
| Prussia ↔ Austria | `primary` | `active` | German hegemony conflict |
| Prussia ↔ Saxony | `secondary` | `cold` | Expansion pressure / annexation fear |

Notes:

- France/Britain is structurally rare at deep alliance, not literally impossible.
- Prussia/Austria is the key anti-universal-friendship fork on the current map.
- Prussia/Saxony starts visible but weaker.
- France/Austria is intentionally **not** a starting rivalry; Austria remains the main swing partner on the 5-nation map.
- Playtest tripwire: if France can still reliably hold `ALLIANCE` with Britain, Prussia, and Austria by early midgame, the first follow-up is France↔Austria `secondary + cold`, not a new bloc system.

Authored escalation rules for Prussia/Saxony:

- if Prussia and Saxony enter direct war → escalate to `active`
- if France vassalizes Saxony → escalate to `active`

These are explicit authored checks, not a general dynamic-rivalry system.

### 7.2 Dynamic rivalry formation

Deferred. v0.1 ships only the static starting rivalries plus the two Prussia-Saxony escalation triggers above. General emergent rivalry formation moves to later AI-agenda work.

### 7.3 Rivalry intensity (acceptance values)

Two-step model — exact values used by `direct_rivalry_mod` (§9.1):

| Weight / Intensity | Meaning | Direct treaty effects |
|--------------------|---------|-----------------------|
| `secondary + cold` | low but visible friction | `OPEN_BORDERS -4`, `NON_AGGRESSION -6`, deep treaties / `VASSAL -12` |
| `secondary + active` | live regional rivalry | `OPEN_BORDERS -5`, `NON_AGGRESSION -10`, deep treaties / `VASSAL -20` |
| `primary + active` | major geopolitical rivalry | `OPEN_BORDERS -6`, `NON_AGGRESSION -12`, deep treaties / `VASSAL -30` |

Rules:

- `cold` rivalries never trigger paradox by themselves (paradox stays on legacy alliance-cross-war trigger; see §7.5).
- `active` rivalries can swing deep-treaty acceptance on their own.
- Primary rivalry is what makes France-Britain alliance "extraordinary but possible" rather than merely uncommon.

### 7.4 Rivalry effects on diplomacy

Two pressure paths.

#### A. Direct rivalry friction

Trying to deepen treaties with a direct rival applies acceptance penalties using §7.3. Lower treaty levels stay flexible; deep military friendship across major rival lines becomes structurally rare.

#### B. Third-party commitment pressure (this phase ships wiring)

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

- if the offended nation is only a `cold` rival of A, apply **half values rounded toward zero**
- if France vassalizes a nation that is the offended rival's marked rival, apply the immediate `VASSAL` anger hit first, then process any authored escalation rule such as Prussia-Saxony
- the rival-reaction relation hit applies immediately on ratification and is the default pressure path
- if that relation loss pushes an existing French treaty with the offended rival below its stability threshold, normal downgrade and auto-downgrade rules handle the fallout — do **not** force an instant treaty break as the default outcome
- do **not** add a separate `they_chose_us` token; the reward loop comes from treaty depth, fulfilled commitments, and visible preview / ledger surfacing

This is intentionally stronger than the old `+5` because the punishment side was drowning out the reward loop.

#### C. Great-power bloc pressure

Deferred. Do not add a separate bloc-pressure layer in v0.1.

The v0.1 side-picking package is:

- direct rivalry penalties
- third-party anger
- bilateral betrayal memory
- legacy commitment paradox (renamed; see §7.5)

War bargains, when `WAR_BARGAIN_SPEC` ships, will add the explicit named-enemy promise layer on top.

### 7.5 Commitment paradox

**v0.1 behavior:** rename the existing `alliance_paradox` dialogue type to `commitment_paradox`. Keep the same trigger (war declaration that would force the player into both sides of an alliance), the same fallout-preview, the same episode_id continuity. The HARD_STOP type registration of `commitment_paradox` (already in `dialogue_manager.py`) starts being used; the legacy type name becomes the historical alias for save-load back-compat.

**Deferred:** the rivalry-driven ratification paradox (the original §7.5 design — opposition-graph evaluator running at every deep-treaty ratification, multi-conflict `ConflictResolutionPass`) is **not** v0.1 scope. It depends on bargain conflicts to feel important; without bargains, it would only fire on the legacy alliance-cross-war condition the existing flow already handles. Defer to `WAR_BARGAIN_SPEC` slice WB-C, which extends the paradox to read live bargains and rivalry data.

What this phase keeps from the original §7.5:

- one-conflict resolution (the legacy flow is one conflict per push by definition)
- deterministic downgrade fallout preview before the choice (already shipped)
- durable `commitment_paradox_resolved` log + dispatch event (already shipped)

What this phase **does not** ship:

- multi-conflict ratification consolidation
- `opposition_graph` reads
- bargain-attached fallout preview (no bargains to attach)

### 7.6 Rivalry decay and resolution

Deferred except for the two Prussia-Saxony escalation triggers. Primary rivalries stay sticky in v0.1. Broader thaw / decay rules can return later.

---

## 8. Reliability And Betrayal

### 8.1 Split the memory cleanly

Two memories, kept separate:

- **Global reliability:** "France is known to keep or break agreements."
- **Bilateral betrayal memory:** "Austria specifically remembers France betrayed Austria."

### 8.2 Offense categories (already shipped)

Tracked betrayal categories in v0.1:

- breaking treaty voluntarily
- breaking non-aggression with rapid war follow-up
- breaking alliance / defensive alliance

Removed from v0.1 (in `WAR_BARGAIN_SPEC` until that ships):

- explicit reversal of an active war bargain
- timer-based failure for ally-land promises
- suspension-based promise expiry
- passive failure caused only by AI inactivity
- explicit exclusivity-demand offenses
- costless bargain-only cancellation actions

### 8.3 Penalty model (substrate shipped; bargain row deferred)

| Event | Global reliability | Victim strikes | Witness effect |
|------|--------------------|----------------|----------------|
| Break `OPEN_BORDERS` / `PEACE`-level commitment | -4 | +1 | `-2` to each scoped witness |
| Break `NON_AGGRESSION` | -6 | +1 | `-2` to each scoped witness |
| Break `DEFENSIVE_ALLIANCE` / `ALLIANCE` | -10 | +2 | `-4` to each scoped witness |
| Explicitly reverse an active war bargain | (`WAR_BARGAIN_SPEC`) | (`WAR_BARGAIN_SPEC`) | (`WAR_BARGAIN_SPEC`) |

Critical episode-cap rule (already shipped):

- one diplomatic episode may add at most **2 victim-side strikes to any one victim**

Episode definition:

- one diplomatic episode = all diplomatic penalties and strike applications that share the same root-cause `episode_id`
- a player-confirmed diplomatic action creates a fresh root `episode_id`
- `advance_turn()` may process multiple `episode_id`s; the turn itself is **not** one episode
- downstream treaty downgrades, witness fallout, and reliability changes caused by that same root trigger reuse the same `episode_id`
- pending dialogue, decay tracker, or delayed diplomatic consequence that may resolve after save/load serializes its originating `episode_id` lineage until resolution

Implications already wired:

- if France breaks an alliance and the cascade collapses other treaties in the same resolution step, relation and reliability penalties may stack
- multiple injured parties in the same episode may each gain strikes
- no single victim's strike gain may exceed +2 from that single episode

Global reliability rule:

- all global reliability deltas apply to the acting nation's shared `diplomatic_reliability[actor]` value
- witness scoping changes relation fallout only; it does not create witness-specific reliability variants

### 8.4 Witness scoping (substrate shipped; region_observer deferred)

Witness penalties apply only to directly interested observers:

- nations with `DEFENSIVE_ALLIANCE` or `ALLIANCE` with the victim
- nations with an active rivalry against the betrayer (currently uses war-state proxy; switches to `nation_rivalries` data once seeded — see §7.1)
- nations with a live bargain that shares the same named enemy or claim region (deferred until `WAR_BARGAIN_SPEC` lands)

Everyone else gets zero witness effect. Witnesses do **not** receive victim-grade strikes in v0.1.

Witness scope tagging (shipped):

- emitted witness payloads carry one deterministic `scope_reason`
- precedence: `ally` > `rival` > `shared_enemy` > `region_observer`
- a breach may have multiple witness nations, but each witness gets exactly one resolved `scope_reason`
- witness payloads carry relation fallout only; surfaced `reliability_delta` on witness events is always `0`

Exclusivity-demand rule:

- do **not** add exclusivity-demand betrayal logic in v0.1
- if explicit exclusivity diplomacy ships later, it must create an explicit tracked commitment before it can create a betrayal offense

### 8.5 Faithful-play rewards

The system must reward sustained committed play, not only punish betrayal.

For v0.1:

- visible side-taking should feel legible through previews, warnings, and treaty outcomes rather than a bespoke hidden relation token
- bargain fulfillment reward (`+4` reliability per (promiser, beneficiary) per 10 turns + `+6` relation) lives in `WAR_BARGAIN_SPEC.md`
- clear preview / ledger surfacing so loyalty feels intentional rather than invisible

Do **not** add a dedicated `trusted_partner` state in v0.1.

### 8.6 Redemption (substrate shipped; reliability tick this phase)

Suggested rules:

- every 5 honored treaty turns: `+3` to `diplomatic_reliability[actor]`, counted once per actor on a single global clock; a turn counts only if that actor ends the turn with at least one qualifying non-`WAR` treaty honored and no new betrayal offense created that turn — **wire this in this phase** (currently absent)
- after honorable turns with a nation and no new offense, remove 1 bilateral strike using severity-scaled decay:
  - 6 turns: `OPEN_BORDERS` / `PEACE`-level break
  - 8 turns: `NON_AGGRESSION` break
  - 10 turns: `DEFENSIVE_ALLIANCE` / `ALLIANCE` break

Guardrails (shipped):

- passive decay clears at most 1 strike per nation per turn
- each strike decays on its own clock using its recorded `turn` + severity-scaled interval; the per-pair dict does **not** store a single shared decay clock
- strike age continues to mature during `WAR` and `ARMISTICE`
- actual strike removal requires an active non-`WAR` treaty (`PEACE` or above) with that nation
- once a non-war treaty is restored, any matured strikes may decay at the normal per-turn limit until caught up
- vassal note: `_NON_WAR_TREATY_STATES` includes `VASSAL`, so a vassal's strikes can decay while vassalized; if the vassal is released or assimilated, strikes follow the nation, not the vassal relationship

### 8.7 Hard-reject behavior (already shipped)

Repeated betrayal must eventually change AI posture.

Rule:

- 3 active bilateral strikes from France toward Nation X causes AI hard resistance to deep treaties with X.

Rules:

- witness suspicion alone never triggers this threshold
- survival exception is narrow: the 3-strike block may downgrade from absolute reject to heavy soft-resistance only when France and Nation X share a current enemy, France is not at war with X, the proposal is immediate military cooperation against that same enemy, and France did not betray X in the same episode
- when that exception opens, AI applies a major posture tax (treat as at least `-20` before normal formula evaluation); the exception removes only the absolute lock, not the political cost
- one episode cannot add more than 2 strikes to the same victim (per §8.3)
- proposal preview must warn when the contemplated action would create the third active strike against a nation (`hard_reject` category warning — already wired)
- emit `hard_reject_posture_triggered` on first crossing from 2 to 3 active strikes and `hard_reject_posture_cleared` on first return from 3+ to 2 or fewer (already wired); both events persist in dispatch and campaign-log metadata for that posture span

---

## 9. Acceptance Formula Hooks

This phase needs three treaty-acceptance inputs in v0.1. The fourth (`bargain_value_mod`) and the dedicated `war_entry_score` live in `WAR_BARGAIN_SPEC.md`.

### 9.1 Direct rivalry modifier (this phase ships)

Use the exact treaty-depth values from §7.3:

- `secondary + cold`: `OPEN_BORDERS -4`, `NON_AGGRESSION -6`, deep treaties / `VASSAL -12`
- `secondary + active`: `OPEN_BORDERS -5`, `NON_AGGRESSION -10`, deep treaties / `VASSAL -20`
- `primary + active`: `OPEN_BORDERS -6`, `NON_AGGRESSION -12`, deep treaties / `VASSAL -30`

Primary active rivals must be able to swing deep-treaty outcomes on their own.

### 9.2 Rival-commitment conflict modifier (this phase ships, partial)

Negative when the target knows France is already aligned with its rival:

- France holds `OPEN_BORDERS` with the target's active rival: `-2`
- France holds `NON_AGGRESSION` with the target's active rival: `-4`
- France holds `DEFENSIVE_ALLIANCE` with the target's active rival: `-10`
- France holds `ALLIANCE` or `VASSAL` with the target's active rival: `-16`
- (bargain-conflict add-on lives in `WAR_BARGAIN_SPEC.md` §9.2)

Do not double-count the same rival twice; use the strongest treaty-alignment value.

Cap `rival_conflict_mod` at `-20` before the composite floor.

### 9.3 Bilateral betrayal modifier (this phase ships — currently missing from formula)

- `-8` per active victim-side strike
- cap `bilateral_betrayal_mod` at `-24`
- stronger than global reliability
- three active strikes should not be cleanly erased by a single sweetener

This is the single highest-value formula change in this phase. The substrate already counts strikes; the formula must read them.

### 9.4 Composite grouping

Group the new modifiers under one composite:

```python
raw_political_commitment_mod = (
    direct_rivalry_mod
    + rival_conflict_mod
    + bilateral_betrayal_mod
)

political_commitment_mod = max(-40, raw_political_commitment_mod)
```

Rules:

- the cap prevents formula-level total lockout
- hard-reject posture at 3 strikes still exists outside the formula
- the per-modifier caps (`bilateral_betrayal_mod -24`, `rival_conflict_mod -20`) are **superseded** by the composite floor when `raw < -40`. The floor is authoritative; per-modifier caps document intent but do not stack as combined limits.
- the per-episode strike cap in §8.3 is what keeps the hard-reject posture from becoming too punishing

When `WAR_BARGAIN_SPEC` ships, `bargain_value_mod` joins this composite (positive contribution).

---

## 10. AI Behavior

### 10.1 Proposal generation

AI uses rivalries to create branches:

- court France against their rival
- (bargain offers move to `WAR_BARGAIN_SPEC.md`)

Minimal v1.0 AI decision-reason contract (already shipped in subset; this phase tightens):

- every AI-authored offer, refusal, hard block, or counterparty reversal emits one deterministic `decision_reason`
- v0.1 enum: `rival_pressure`, `shared_enemy_survival`, `distrust_promiser`, `war_overload`, `route_blocked`, `coalition_conflict`, `counterparty_reversal`, **`unknown_baseline`** (added in this phase to replace the current `rival_pressure` catch-all when no actual rivalry pressure is computed)
- bargain-specific reasons (`claim_trade`, `claim_obsolete`) live in `WAR_BARGAIN_SPEC.md`
- `decision_reason` is mechanical motive metadata the presentation layer, advisory logic, and campaign log can read directly — it is not freeform narrative text

### 10.2 Anti-spam rules

AI must not:

- offer redundant proposals to a target with whom France currently has an unresolved hard-reject posture
- escalate ratification with rivals when a recent hard-stop was rejected

(Bargain-specific anti-spam moves to `WAR_BARGAIN_SPEC.md`.)

### 10.3 Refusal behavior

AI should refuse or resist:

- deep alliance while France is already militarily aligned with the AI's rival (uses §9.2)
- deep treaties at 3 active victim-side strikes except under explicit survival exceptions (already wired)

### 10.4 Strategic focus / advisory layer

Deferred. Personality-specific bargaining agendas and richer court personas move later.

### 10.5 Performance / architecture guard

No new hot-path per-region scans.

Use:

- cached rivalry lookups (per-turn cache when the rivalry seed lands)
- direct pair-key reads on `betrayal_history`
- targeted validation checks on key event hooks

`_classify_witness_scope`'s shared-enemy loop is currently O(active_nations) per witness — fine at 5 nations, monitor at 19+.

---

## 11. Player-Facing Surfaces

### 11.1 Diplomatic Ledger

Add to Nations / Talleyrand tabs:

- each nation's active rivals
- France's global reliability descriptor (already present)
- bilateral betrayal warning when that nation distrusts France specifically (already present)
- bargain section deferred to `WAR_BARGAIN_SPEC.md`

Presentation rule: render as one compact commitment block per nation, not as multiple new dense subsections repeated across tabs.

### 11.2 Proposal preview / Talleyrand advisory (already shipped)

Dedicated **Political context** panel on proposal preview / ratification surfaces.

Surfaces:

- active rivals relevant to the target
- any bilateral betrayal memory affecting the offer
- main nation likely to be angered if France proceeds

Canonical preview contract (shipped):

- expose a structured `warnings[]` list
- each warning contains `severity`, `category`, `text`

Warning categories used in this phase:

- `rivalry`
- `betrayal`
- `hard_reject`
- `paradox`
- `peace_conflict`

(`bargain` category reserved for `WAR_BARGAIN_SPEC.md`.)

Severity contract (shipped):

- ordinals: `critical = 3`, `high = 2`, `medium = 1`, `low = 0`
- stable category tie-break order: `paradox`, `hard_reject`, `bargain`, `betrayal`, `rivalry`, `peace_conflict`
- later categories should append after this order, not silently reshuffle it
- tie-break beyond severity + category currently uses text sort; a stable emit-sequence index would be more robust at scale (low priority; flagged for future)

Preview legibility rules (shipped):

- show at most 2 warnings inline
- sort by severity first, then immediate player relevance
- collapse overflow behind `View all concerns`

### 11.3 Treaty display

Active treaties tab — no new content in this phase. (Bargain rows live in `WAR_BARGAIN_SPEC.md`.)

### 11.4 Dispatch and campaign log

High-signal events for this phase:

- rivalry escalation (Prussia-Saxony triggers)
- betrayal recorded
- commitment paradox resolved (already shipped via legacy alliance_paradox flow)
- hard-reject posture triggered (already shipped)
- hard-reject posture cleared (already shipped)
- major reliability improvement or drop

Bargain events (`bargain_ratified`, `bargain_triggered`, `bargain_fulfilled`, `bargain_breached`, `bargain_voided`) live in `WAR_BARGAIN_SPEC.md`.

Campaign log metadata payload (shipped):

- `episode_id`, `end_reason_family`, `end_reason_action`, `fault_nation`, `decision_reason`, witnesses with `scope_reason`, deterministic deltas

Rendering rule: store the full metadata payload on the event record; render a compact one-line summary in the Campaign Log; deeper detail can be shown later through tooltip / expand affordances without changing the stored payload.

The full felt-experience presentation (spotlight tier, split-voice, named diplomats, N+1 callbacks) lives in `COMMITMENTS_PRESENTATION_SPEC.md` (`C3-lite`).

---

## 12. Data Model

### 12.1 Already shipped

- `diplomatic_reliability: Dict[str, int]` — nation-keyed shared global reputation scalar
- `betrayal_history: Dict[str, Dict]` per §6.2
- `next_episode_id: int` per §6.5
- `alliance_paradox_popup: Optional[Dict]` (renamed `commitment_paradox_popup` in this phase; legacy field name kept for save-load back-compat)

### 12.2 To add this phase

- `nation_rivalries: Dict[str, Dict]` per §6.3
  - key: `diplo_key`
  - value: `{intensity, source, weight, started_turn, last_changed_turn}`
- `actor_honored_turns: Dict[str, int]` — single global honored-turn clock per actor for §8.6 reliability tick

### 12.3 Deferred

- `diplomatic_commitments`, `next_commitment_id` → `WAR_BARGAIN_SPEC.md`
- `trusted_partners`, `nation_strategic_focus`, `nation_power_scores`, `nation_power_tiers` → later phases

Do **not** add ally-beneficiary settlement entitlement fields in this spec. Do **not** add a separate `nation_claims` store — until a settlement system defines a canonical claim model, claim-like state stays inside bargain records (in `WAR_BARGAIN_SPEC.md`).

---

## 13. Implementation Sequence

### Slice A. Foundations

**Already shipped:**

- `betrayal_history`, `next_episode_id`, witness-scope classifier, `commitment_event_metadata`, structured `warnings[]`, breach preview with reliability/applied-vs-intended deltas
- substrate ledger surfacing for reliability and bilateral betrayal
- `commitment_paradox` HARD_STOP type registration (placeholder)

### Slice B. Rivalry pressure

**Already shipped (B2a/B2b):**

- third-party anger metadata produced for breach events
- witness scoping with `scope_reason` precedence
- per-episode strike cap of 2
- redemption decay (severity-scaled) — strike-removal half
- hard-reject posture trigger / clear emits
- preview plumbing for `hard_reject` warnings
- Prussia↔Saxony escalation triggers (data-driven; activated by §7.1 seed)

**This phase ships:**

- **B-A1-fill: rivalry seed.** Add `nation_rivalries` to WorldState init with the 3 authored pairs from §7.1. `to_dict` / `from_dict` round-trip. ~8 tests.
- **B-B1: acceptance formula additions.** Add `direct_rivalry_mod`, `rival_conflict_mod`, graduated `bilateral_betrayal_mod` with composite `political_commitment_mod` floored at `-40`. Wire debug breakdown output and acceptance feedback strings. Preserve old static sweeteners only when no graded rivalry / betrayal data applies. Add regression tests comparing representative pre-change proposal scores against expected tolerance bands. ~14 tests.
- **B-B2a-fill: third-party anger on ratification.** Apply rival-reaction relation hits per §7.4.B at treaty ratification, scaled half for `cold`. Special handling for vassalize-rival-of-rival. Use existing downgrade / auto-downgrade behavior as the normal fallout path; do **not** add forced instant-break logic. ~10 tests.
- **B-B6: redemption tick.** Add `actor_honored_turns` global clock per §8.6 with the +3 reliability award once per actor per 5 honored turns. ~5 tests.
- **B-B3: paradox rename.** Rename push-side `dialogue_manager.push({"type": "alliance_paradox", ...})` to `commitment_paradox`; keep `alliance_paradox` as accepted alias on read for save-load. Rename the popup type passthrough on the Godot side (`alliance_paradox_popup.gd` field reads). The dedicated `commitment_paradox_popup.{tscn,gd}` surface ships in the `C3-lite` slice (Slice C below). ~3 tests.

### Slice C. C3-lite presentation pass

See `COMMITMENTS_PRESENTATION_SPEC.md` v0.3. Ships with this phase:

- Spotlight tier on the notification rail (elevated card, 2-turn persist, action buttons)
- Split-voice render (`attributed_lines[]`) on popup scene
- Named-diplomat resolution: `speaker="envoy"` resolves to nation's named diplomat per Voice Bible; `speaker="foreign_office"` renders as "The Chancery of {nation}"
- Committed mock prose for the three events that fire: `hard_reject_posture_triggered`, `diplomatic_treaty_broken` (french_breach), `commitment_paradox_resolved`
- One N+1 Talleyrand aside keyed by `episode_id`
- Dedicated `commitment_paradox_popup.{tscn,gd}` surface (one of the four Slice C Godot prerequisites; see `COMMITMENTS_PRESENTATION_SPEC.md` §14)
- ~16-22 tests

### Slice D. Deferred follow-up

Same as before:

- D1 (advisory-first strategic focus, deeper AI integration)
- D2 (coalition buildout / generalization)

Both stay deferred unless playtesting proves the v0.1 pressure layer still lacks political texture.

### Slice WB-* (deferred to Peace Deals phase)

War bargain implementation moved to `WAR_BARGAIN_SPEC.md` slices WB-A through WB-D. Not part of Memory and Pressure ship.

---

## 14. Risks

### R1. Over-hard locking

If rivalry becomes pure binary prohibition, diplomacy feels scripted.

**Mitigation:** keep lower treaty levels flexible; force choices only on deep military commitments; keep France-Britain extraordinary but technically possible.

### R2. Pressure-without-promise feels punitive

Without bargains, the player has more friction and less new agency. Risk: "diplomacy got harder but I can't do anything new."

**Mitigation:** the C3-lite presentation pass is the agency restoration path — events that already fire should land as memorable political moments rather than log lines. Playtest after this phase ships; if friction-without-agency reads as flat, accelerate `Bilateral Peace Hardening` so `WAR_BARGAIN_SPEC` can land sooner.

### R3. Contradiction opacity

If acceptance formula floor (-40) hides real underlying pressure, players can't reason about why proposals fail.

**Mitigation:** preview UI (`warnings[]`) exposes the contributing factors; debug breakdown output shows individual modifier values for tuning.

### R4. Warning overload

If warnings fire every turn, players stop reading them.

**Mitigation:** event-driven warning model only; preview capped to 2 inline warnings; rivalry seed is small (3 pairs) so anger events are rare.

### R5. France-centric coalition assumptions

If commitments hard-code coalition overlap as "anti-France only," later coalition generalization becomes much harder.

**Mitigation:** keep helpers parameterized on actor / victim / promiser. Do not create parallel `war_bloc` / `opposition_graph` stores in v0.1 (the rescope cut these forward-compat stubs). The commitments helpers (`_classify_witness_scope`, `_betrayal_key`, `_get_breach_witness_scope`) are already actor-parameterized and need no rewrite for non-France actors; however, surrounding `diplomacy.py` wiring still uses `world.player_nation` as shorthand for France in ~14 sites (e.g. `get_active_nations` callers, player-relation updaters, Talleyrand-dispatch attribution), so `Coalition Generalization` is a one-helper refactor for the scope / rivalry evaluators **plus** a broader audit of those surrounding paths.

---

## 15. Resolved Design Calls

### Gate 1 — Hard forced-choice vs soft penalty for rival military alignment?

**Resolved:** forced choice for deep military alignment, soft pressure below that. (Implemented via composite `political_commitment_mod` + hard-reject posture for deep treaties.)

### Gate 2 — Global reliability + bilateral betrayal, or all pair-specific?

**Resolved:** keep the split.

### Gate 3 — Timed territorial promises or narrower war bargains?

**Resolved:** war bargains chosen — and **moved to `WAR_BARGAIN_SPEC.md`** in the v2.0 rescope.

### Gate 4 — Promise deadlines / suspension model?

**Resolved:** cut entirely. (Inherited by `WAR_BARGAIN_SPEC.md` when bargains land.)

### Gate 5 — AI-authored only, or limited player-authored bargaining too?

**Resolved:** allow limited player-authored bargaining. (Lives in `WAR_BARGAIN_SPEC.md`.)

### Gate 6 — Hard-reject threshold?

**Resolved:** keep 3 strikes, but cap strike gain to 2 per episode. **Already shipped.**

### Gate 7 — Ally-beneficiary land promises in v0.1?

**Resolved:** defer to `Ally Participation + Common Peace`.

### Gate 8 — Global bargain cap or structural caps?

**Resolved:** structural caps only. (Inherited by `WAR_BARGAIN_SPEC.md`.)

### Gate 9 — Coalition obligation or alliance obligation?

**Resolved:** distinct textures with explicit overlap rules. v0.1 stays anti-France-only; helpers stay parameterized so later `Coalition Generalization` is a clean refactor.

### Gate 10 (new in v2.0 rescope) — Ship bargains alongside substrate, or rescope?

**Resolved:** rescope. The April 16 audit established the substrate had shipped without the bargain layer or formula integration; trying to land all of `Reliability + Commitments` as one phase would have either delayed every part or shipped a half-bargain. Splitting into Memory and Pressure (now) + Peace Deals containing `WAR_BARGAIN_SPEC.md` (later) lets the engine grow with each peace-related layer underneath it.

---

## 16. Draft Recommendation

For Memory and Pressure v2.0:

- keep global reliability and bilateral betrayal substrate (already shipped)
- seed `nation_rivalries` with the 3 authored pairs (this phase)
- fill the acceptance formula with `direct_rivalry_mod`, `rival_conflict_mod`, graduated `bilateral_betrayal_mod` under a `-40` composite floor (this phase)
- wire third-party anger on treaty ratification (this phase)
- rename `alliance_paradox` → `commitment_paradox` (this phase)
- ship the `C3-lite` presentation pass — spotlight tier, split-voice render, named-diplomat resolution, committed mock prose for the three live events, one N+1 callback (this phase)
- defer war bargains to `WAR_BARGAIN_SPEC.md`

That is enough to make diplomacy feel political, create real rivalry pressure, and remove the largest "events land as log lines" failure mode without bundling in the full settlement overhaul too early.

---

## 17. Changelog

- **April 16, 2026 — v2.0 rescope.** Renamed phase to "Memory and Pressure". War bargains moved to dedicated `WAR_BARGAIN_SPEC.md` (Peace Deals phase). Acceptance formula trimmed to three modifiers (no `bargain_value_mod`, no `war_entry_score`). §7.5 rivalry-driven paradox cut; legacy alliance-cross-war paradox renamed to `commitment_paradox`. §6.4 commitment store and §13 commitment data fields moved to `WAR_BARGAIN_SPEC.md`. Coalition forward-compat seams (`opposition_graph`, `war_bloc.target_nation` stores) cut from v0.1 — helpers stay parameterized. New Gate 10 added. New §6.5 note that `region_observer` witness scope reactivates when `WAR_BARGAIN_SPEC` ships. New §10.1 enum entry `unknown_baseline` to retire the current AI catch-all. Honored-turn reliability tick (§8.6) added explicitly as this-phase work. Vassal-decay edge case noted (§8.6). Composite-floor-supersedes-per-modifier-cap clarification added (§9.4). Stable-tie-break-index flagged as future improvement (§11.2).
- **April 14, 2026 — v1.0 draft** (`Reliability + Commitments`). Original spec covered rivalries, betrayal memory, and war bargains together. Rescoped April 16 after audit established the bargain layer was unimplementable in the same phase as the substrate. Original v1.0 content now split between this spec (substrate + rivalry pressure + paradox rename + presentation hand-off) and `WAR_BARGAIN_SPEC.md` (war bargains).
