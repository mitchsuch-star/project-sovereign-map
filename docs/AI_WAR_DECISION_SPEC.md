# AI War Decision — "What It Leaves Undefended" (row **AI-3r**)

> **v0.1 — PROPOSED July 25, 2026. Not blessed. §6 holds the gate questions.**
>
> **This spec AMENDS a blessed gate decision** — `AI_INTENT_SPEC.md` §6 **D1**
> ("at most 2 simultaneous AI-initiated wars"). It does not reopen D2–D7.
>
> **Origin:** the pin-20 live in-game pass (July 25, 2026 — `docs/STATUS.md` top
> entry) measured **zero AI-initiated wars in 38 turns** with `war_intents`
> empty throughout, then a code read showed the top rung of the price ladder is
> **arithmetically unreachable** on the shipped seed. The user's design steer, in
> their words: *"doesn't just 2 at war seem overly gamey… there should be
> relationships and opportunities"* and *"they don't want to leave themselves
> exposed to a strong enemy — take inspiration from Hearts of Iron."*
>
> **Reading order:** §0 the evidence · §1 the design shift · §2 the mechanics ·
> §3 the numbers · §4 the slices · §5 acceptance · §6 the gate · §7 deferrals.

---

## 0. Why — the measured case

### 0.1 The observed behaviour

A 38-turn live 1805 campaign (client + backend, `LLM_MODE=anthropic`) produced:

- `war_intents == {}` at every inspection — **no crisis ever opened**;
- therefore beats 2 (Brewing Crisis), 3 (Ultimatum) and 7 (The Crisis Passes)
  never fired on screen;
- Prussia, holding the marquee acquire design `The Hanoverian Prize` beside an
  undefended Hanover, sat at price **`align`, weight 59** for the entire run.

Third-party wars the scenario *boots* with were fought and — thanks to Stage D —
ended without France (`THE CONGRESS` fired twice). Nothing was broken about war
*conduct*. Nothing ever *started*.

### 0.2 The arithmetic — why it is structural, not unlucky

A crisis opens only for a court whose intent has reached price **`fight`**
(`weight ≥ 85`, `intent.PRICE_THRESHOLDS`) against a target it is **not already
at war with** (`war_council.process_war_council` step 3 + `_restraints_hold`).
Every term that can move that weight (`intent._derive_weight`):

| Term | Value | Reachable in the qualifying case? |
|---|---:|---|
| base `acquire_regions` | 55 | always |
| `statecraft_weight_mod` | **0** for every authored 1805 court | 0 |
| `WEIGHT_AT_WAR_WITH_HOLDER` | +10 | **never** — that state disqualifies the crisis |
| relation ≤ −40 (`WEIGHT_RELATION_COLD`) | +8 | yes |
| holder in ≥2 wars (`WEIGHT_OPPORTUNISM_TWO_WARS`) | +10 | yes |
| holder bankrupt | +3 | yes |
| live guarantee on the holder | −8 | penalty only |
| `WEIGHT_RENEGED_BARGAIN` | +15 | only after a bought-off design is broken |
| `INTENT_WEIGHT_JITTER` | ±8, **0 on the historical/default seed** | seeded runs only |

**Ceiling on the default seed, absent a renege: 55 + 8 + 10 + 3 = 76.**
The floor is **85**. Maximum positive jitter on a seeded run reaches **84** —
still short. The only route to an AI-initiated war in the shipped game is a
**reneged bargain** (+15) *combined with* a cold relation *and* a distracted
holder. One extremely narrow corridor.

Two structural companions to the same defect:

- **`WEIGHT_AT_WAR_WITH_HOLDER` is a dead term** for war-opening — it can only
  apply in the exact case the opener excludes.
- **The opener filters `want_type == "acquire_regions"` only**
  (`war_council.py` step 3), so `deny_regions` (base 60) and
  `contain_hegemon` (base 65) — the highest-base, most historically warlike
  designs — can never open a crisis at all. Britain fighting to keep France out
  of the Scheldt is unreachable by construction.

**Consequence: D1's own acceptance band (1–4 AI-initiated wars per 40 turns,
`AI_INTENT_SPEC.md` §7) cannot be met.** Making the rung reachable is therefore
a **defect repair against the phase's own Definition of Done**, not a design
change. Only the cap deletion and the design widening are gate matters.

### 0.3 The cap misattributes its own effect on screen

When `MAX_SIMULTANEOUS_AI_WARS` binds, a fully fore-warned crisis accumulates
`soft_stall_turns` and, after `CRISIS_SOFT_STALL_TURNS`, fires **beat 7** with
cause `"starved"`, whose authored copy is:

> *"the moment passed — opportunism decayed"*

That is false. Opportunism did not decay; the engine refused because two
*unrelated* nations elsewhere were already at war. Beat 7 exists specifically to
teach cause and effect (§12.1, "the deterrence receipt"), so this is the same
defect class as the coalition-dissolution rule deleted on July 25, 2026: **a
surface stating a reason the code does not have.**

A quota is also the only restraint in the system with **no diegetic
explanation**. Every other gate can be rendered in the world's own terms —
Prussia cannot afford it, Prussia is already at war, Hanover has a guarantor,
the army is not strong enough. *"Prussia may not move because Spain and Bavaria
are busy"* can never be rendered honestly, because it is not a fact about
Prussia.

---

## 1. The design shift — from a quota to an exposure calculus

**The governing idea (HOI4 inspiration, user-directed):** a great power does not
commit its field army to a war of choice if that leaves its own soil open to a
neighbour who might take it. The ceiling on simultaneous wars is not a counter —
it is **what each court can afford to leave behind.**

What Hearts of Iron actually does, and what this borrows:

| HOI4 mechanic | What it does there | The borrow here |
|---|---|---|
| No global war cap | war count is an emergent output | **delete `MAX_SIMULTANEOUS_AI_WARS`** (§2.4) |
| AI holds divisions back on threatened borders | an army is not "free" just because it exists | **the rear-security reserve** (§2.1) — the centrepiece |
| Per-country AI strategy weights (`prepare_for_war`, `contain`, `ignore`) | authored national posture toward *specific* others | **authored `wary_of` pairs** on the existing `NATION_STATECRAFT` (§2.6) |
| Justify war goal — public, timed, raises tension | the target can see it coming and prepare | **already built** — the Stage D crisis fore-warning (beats 2/3) |
| World tension gates who may act | aggression has a political price | **already built** — AI-4a step 5 accrues threat to the *aggressor's own* slot, feeding coalitions against them (§2.4) |

Three properties this buys that a quota cannot:

1. **It is diegetic.** Every refusal renders as a fact about that court: *"Berlin
   will not strip the Silesian frontier while Vienna stands armed."*
2. **It is playable.** France can *create* the conditions for someone else's war
   (or prevent one) by moving armies, by guaranteeing, by making a neighbour
   look dangerous. A quota is unreachable by play.
3. **It self-limits without a number.** A tense, armed Europe produces few wars;
   a Europe where the great powers are committed elsewhere produces many. That
   is the historical shape, and it comes free.

---

## 2. Mechanics

### 2.1 The rear-security reserve — the centrepiece

**New single source** in `war_council.py` (decision layer, not a combat
modifier — Golden Rule 1 untouched):

```
get_rear_reserve(world, nation)        -> int   # strength that CANNOT march
get_free_strength(world, nation)       -> int   # standing − reserve, floored at 0
get_exposure_view(world, nation)       -> dict  # {reserve, free, threats:[…]} for render
```

**Derivation** (all terms already exist in the world; no new serialized field):

1. Assemble the court's **land neighbours**: powers controlling at least one
   region adjacent to one of its own. (New per-turn-cached helper —
   `world.get_neighbouring_nations(nation)`; see §2.7 for the Golden-Rule-8
   contract. The region-intersection idiom already exists at
   `diplomatic_templates.py:3596`.)
2. Drop neighbours that are: the same nation, its vassals, its lord, anyone it
   is in a defensive alliance with, and anyone eliminated.
3. For each remaining neighbour `P`, compute a **menace**:
   `menace(P) = standing_strength(P) × band(relation(N,P)) × posture(N,P)`
   where `band` comes from the existing relation bands and `posture` is the
   authored `wary_of` multiplier from §2.6 (default 1.0).
4. **`reserve = max over P of menace(P)`, clamped to `RESERVE_CAP_FRACTION` of
   the court's own standing strength.** *Max, not sum* — a state garrisons
   against its worst credible single opponent, not against a simultaneous
   invasion by everyone (recommendation; see gate **Q2**).
5. `free = max(0, standing − reserve)`.

**Where it binds.** `_restraints_hold` compares **free** strength, not standing,
against the target and its guarantors:

```
free_strength(coveter) >= AI_WAR_FORCE_RATIO × (standing(target) + Σ guarantors)
```

This single change is the diegetic replacement for the cap. Prussia with Austria
armed and cold on its flank cannot campaign in Hanover; Prussia after Austria is
beaten, bankrupt or friendly can.

**Symmetry (Golden Rule 5).** The same function computes France's exposure and
is *rendered* to the player (§2.5). It does not gate the player's own orders —
the player is never blocked from a foolish war; they are *told* what it leaves
open. Asymmetry here is deliberate and pinned: the AI's decision layer consumes
it, the player's legibility layer displays it.

### 2.2 The moment — opportunity terms that can actually climb

`_derive_weight` gains terms so that a genuine opening reaches the top rung
*without* requiring a reneged bargain:

| New term | Reads | Rationale |
|---|---|---|
| `WEIGHT_HOLDER_ALLIES_COMMITTED` | the holder's guarantors/allies are themselves at war | HOI4's "their faction is busy" — today only the *holder's* own wars count |
| `WEIGHT_HOLDER_RECENTLY_BEATEN` | the holder lost a settlement or a capital within N turns | the wolves gather after Austerlitz |
| `WEIGHT_HOLDER_EXHAUSTED` | holder war-exhaustion above a band | the existing AI-4c signal, finally consumed by a decision |
| `WEIGHT_OWN_REAR_QUIET` | the coveter's own §2.1 reserve is small relative to its army | the mirror of the exposure gate — a safe rear *invites* adventure |

**The window decays.** Each of these is a per-turn reading, never a latch
(§3.1a's descent rule holds). An opening not taken closes when the holder's
allies make peace, its exhaustion falls, or the coveter's own rear becomes
threatened — and beat 7 then reports **`starved`** *truthfully*.

`WEIGHT_AT_WAR_WITH_HOLDER` is **retired from the acquire path** (dead term,
§0.2); the `_derive_price` early return for "already at war" is unaffected.

### 2.3 Widen the eligible designs

The crisis opener accepts `deny_regions` and `contain_hegemon` in addition to
`acquire_regions`. Their targets resolve through the same
`get_agenda_military_targets` seam that already excludes self-conquest and
deny-target soil (NA-3 §3.1). This alone may restore reachability without moving
a single constant — the bases are 60 and 65 against 55.

**Guard (pin):** a `contain_hegemon` war must still respect **D3** — the
machinery generalises, but a non-player coalition forms only when that hegemon's
share exceeds France's. Containment wars against France remain the coalition's
business, never the war council's (**§16.2 v1 rule: AI-vs-AI only** stands).

### 2.4 Delete the cap; keep the costs

- `MAX_SIMULTANEOUS_AI_WARS` and `count_ai_initiated_wars`'s cap role are
  **deleted**. (`count_ai_initiated_wars` survives as a metric for the sweep.)
- **One design war per court at a time stays** — the existing
  `if world.get_nations_at_war_with(coveter): return False`. That limit *is*
  diegetic and is the real per-actor governor.
- The political cost stays and finally does work: **AI-4a step 5 already accrues
  threat to the aggressor's own slot**, so a conquering AI builds a coalition
  against itself exactly as France does. This is EU4's aggressive-expansion loop,
  already wired, currently idle because no AI ever expands.
- **The runaway guard moves from the engine to the suite** (§5): a seeded
  40-turn sweep that produces more than `SWEEP_WAR_ALARM` wars fails the sweep
  and sends a human to look at the costs. A test may be gamey; the world may not.

### 2.5 Honesty surfaces

1. **Beat 7's cause taxonomy gains the causes the engine can actually produce.**
   `_CRISIS_CAUSE_COPY` today carries `satisfied / bought_off / deterred /
   starved`. Add **`exposed`** ("the frontier could not be stripped — {threat}
   stands armed at their back") and **`outmatched`** ("the odds never came").
   **Pin:** every cause reachable in code has its own copy, and no cause is ever
   rendered under another's string — the defect §0.3 records.
2. **The ledger renders exposure** for every court whose forces are visible
   (fog rules as AI-4c's weariness row): *"Free field army: 48,000 of 91,000 —
   Vienna holds the rest against Prussia."* This is the row that makes the
   whole system playable rather than mysterious.
3. **France's own row** shows France its exposure (§2.1 symmetry) and is the
   first place the player learns the rule exists.
4. **Talleyrand's war-room counsel** gains one rung: *"Berlin is not free to
   move, Sire — while Vienna stands armed, the Hanoverian design stays a
   grievance."* Consumes the same view; no new evaluation.

### 2.6 Authored posture — the HOI4 AI-strategy borrow

`NATION_STATECRAFT` already carries a `weight_mod` authored **0** for every 1805
court. Extend the authored block (scenario data, `europe_1805.json`) with a
bounded per-pair posture:

```json
"statecraft": {
  "Prussia": { "wary_of": { "Austria": 1.25, "Russia": 1.4 } }
}
```

`posture(N,P)` multiplies the menace in §2.1-3; **absent → 1.0**. This follows
**D7's governing principle**: *the bounds are authored content, not a formula* —
fidelity stays reviewable by reading the scenario file, validator-enforced, and
free for modders. Ahistorical paranoia becomes structurally impossible rather
than merely unlikely.

Validator: `wary_of` values in `[0.5, 2.0]`, targets must be known nations
(hard error), self-reference a hard error.

### 2.7 Scale contract (Golden Rule 8)

`get_neighbouring_nations` scans regions once and is **per-turn cached with the
existing invalidation chain** (`invalidate_active_nations_cache` clears it —
region capture already routes there). `get_rear_reserve` is likewise per-turn
memoised per nation. **No helper added by this spec may scan
`world.regions.values()` inside a per-nation loop.** A tripwire test asserts the
region scan count per turn is O(1) in the number of courts.

---

## 3. The numbers — ALL escalate to the gate

Nothing below is blessed. **§4's slice 0 measures before any of these is set.**

| # | Constant | Proposed | Note |
|---|---|---|---|
| N1 | `RESERVE_CAP_FRACTION` | 0.60 | a court never garrisons more than 60% of its army |
| N2 | relation `band()` for menace | ≤−40 → 1.0 · ≤0 → 0.6 · ≤30 → 0.3 · >30 → 0.1 | an ally-ish neighbour still costs something |
| N3 | `WEIGHT_HOLDER_ALLIES_COMMITTED` | +6 | |
| N4 | `WEIGHT_HOLDER_RECENTLY_BEATEN` | +8, window 6 turns | |
| N5 | `WEIGHT_HOLDER_EXHAUSTED` | +5 above WE 100 | consumes AI-4c |
| N6 | `WEIGHT_OWN_REAR_QUIET` | +6 when reserve < 20% of standing | |
| N7 | `PRICE_THRESHOLDS["fight"]` | **85 → measure** | prefer the terms climbing to the bar over the bar dropping |
| N8 | `SWEEP_WAR_ALARM` | 6 per 40 turns | suite-level runaway guard, not an engine rule |

**Standing rule:** the blessed numbers stay in-band tunable; a change of
*shape* (a new term, a new gate) escalates.

---

## 4. Build slices

| Slice | Scope | Gate? |
|---|---|---|
| **AI-3r.0 — The Probe** | Harness only, **no production change**: an 8-seed × 40-turn scripted-France run logging per court per turn the weight, every contributing term, the price rung, and why a crisis did not open. Output = a memo in `docs/audits/`. Proves or refutes §0.2's ceiling empirically. | none |
| **AI-3r.1 — Exposure** | §2.1 reserve/free-strength + §2.7 caching + the `_restraints_hold` switch to free strength + §2.5-2 ledger row + France's own row | none (defect-side) |
| **AI-3r.2 — The Moment** | §2.2 opportunity terms + window decay + dead-term retirement + §2.3 design widening; re-run the probe and set N7 from data | **Q3** |
| **AI-3r.3 — The Cap** | §2.4 deletion + §2.5-1 cause taxonomy + the suite runaway guard + §2.6 authored posture + validator | **Q1, Q4** |
| **AI-3r.V — Re-measure** | The §5 acceptance sweep; folds into AI-V's arm (a) | none |

Slice order is load-bearing: **the probe runs first**, because every number in
§3 is otherwise guesswork, and .1 lands before .2 so the exposure brake exists
*before* the accelerator.

---

## 5. Acceptance (Definition of Done)

1. **8-seed × 40-turn scripted-France sweep**: every seed yields **1–4
   AI-initiated wars** (D1's own band, now met by costs rather than a counter),
   each carrying a rendered stated reason.
2. **The exposure gate demonstrably bites**: at least one seed shows a crisis
   cooling with cause `exposed`, and **no** AI-initiated war occurs whose
   aggressor loses a home province to a *third* party within 5 turns of
   declaring. (If the AI strips its frontier and is punished for it, the gate
   failed.)
3. **Beat 7 causes**: every cause the engine can emit is reachable in the sweep
   and correctly attributed; `starved` never renders for a gate refusal.
4. **Widened designs**: at least one `deny_regions` or `contain_hegemon` war
   occurs across the seed union, or a written blocking predicate.
5. **Boot integrity**: the `historical` seed boots **byte-identical**; M1–M7
   byte-identical; the suite green; `ruff` clean; parse harness EXIT=0.
6. **Scale**: the §2.7 tripwire green.
7. **In-game (pin 20)**: the exposure row and the new beat-7 causes seen on
   screen, not just in tests.

---

## 6. THE GATE — decisions I cannot make

| # | Question | Recommendation |
|---|---|---|
| **Q1** | Delete `MAX_SIMULTANEOUS_AI_WARS` outright, or raise it to 4 as a backstop? | **Delete.** It has never bound (§0.2), it cannot be rendered honestly (§0.3), and the costs that should govern are already built. Keep the runaway guard in the suite. |
| **Q2** | Rear reserve = **max** single menace, or **sum** of all menaces? | **Max.** Sum makes any centrally-placed power permanently immobile — Austria borders five states — and produces a Europe where only islands fight. |
| **Q3** | May `deny_regions` and `contain_hegemon` designs open wars? | **Yes**, with the D3 guard in §2.3. They are the historically warlike designs and their exclusion is why the highest-base decks are inert. |
| **Q4** | Authored `wary_of` posture, or purely derived from relations? | **Authored**, per D7 — reviewable in the scenario file, validator-enforced, moddable, and it cannot invent an ahistorical fear. |
| **Q5** | Does the exposure calculus gate the **player's** orders too? | **No — display only.** Napoleon may strip the Rhine if he wishes; the game must *tell* him what he is leaving open. Pinned as a deliberate asymmetry with a falsifiable negative test. |
| **Q6** | Does this run before or after the Battle Diorama (row BD)? | **After BD.** BD is queued, scoped and small; this is a multi-slice systems change and AI-V wants it settled, not rushed. |

---

## 7. Deferrals homed (Golden Rule 9)

| Item | Owner row | Landing | Completion | Test |
|---|---|---|---|---|
| Naval exposure (a coastal power's fear of Britain) | **DEF-5 naval spec** | with the naval rider | menace includes a sea-borne threat term | `test_naval_exposure.py` |
| Player-facing "your rear is exposed" *warning* at order time (beyond the ledger row) | **AI-3r.1 follow-on, this spec §2.5-3** | AI-3r.1 | the France row renders; an order-time nudge is explicitly OUT of v1 | pinned negative in the AI-3r.1 suite |
| Authored `wary_of` for scenarios other than 1805 | `MODDING_FORMAT.md` row added in AI-3r.3 | AI-3r.3 | validator accepts/rejects; absent → 1.0 | validator test |
| Multi-front conduct once a court holds two wars | **AI-V assertions** (already owned, `AI_INTENT_SPEC.md` §13) | AI-V | the existing §13 question | AI-V sweep |

Nothing in this spec is left as "future polish."
