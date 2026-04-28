# Imperial Settlement: War Settlement + Ally Participation Spec

> **Status:** v1.0 DESIGN-APPROVED — NO-GO for coding until implementation plan is written
> **Last Updated:** April 27, 2026
> **Companion docs:** `DIPLOMACY_SPEC.md`, `COALITION_SPEC.md`, `RELIABILITY_COMMITMENTS_SPEC.md`, `PEACE_DEALS_UMBRELLA_SPEC.md`, `WAR_BARGAIN_SPEC.md`, `WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md`, `STATUS.md`
> **Depends on (all landed):** Memory and Pressure v2.4.3, Bilateral Peace Hardening (BPH-A through BPH-D), War Purpose + Score Semantics (WPS-A through WPS-D), War Bargains (WB-A through WB-D)

---

## 1. Problem Statement

The current diplomacy game supports allies entering wars and making war bargains, but peace is still negotiated as a pairwise deal. That creates four gaps:

1. France can fight a multi-nation war, but peace resolves as separate bilateral treaties.
2. War Bargains create named-enemy promises (WB-A through WB-D) but the peace machinery cannot fulfill them by awarding territory to allies.
3. Great-power politics exist through hegemony pressure and Balance of Europe, but not at the settlement table.
4. An ally can contribute 35% of the war effort and be mechanically invisible when Saxony is being distributed.

This spec defines the settlement layer that makes allies visible at the peace table without building a conference minigame.

---

## 2. Design Philosophy: Imperial Settlement

France can dictate the settlement when military authority is high. Allies do not get a universal veto, but every ally has a level of **political standing**. If France ignores that standing, the cost is political: grievance, betrayal, downgrade pressure, hard-reject posture, coalition drift, or named-diplomat backlash.

The settlement stack — each layer already exists or is well-defined:

| Layer | Question | Source |
|-------|----------|--------|
| `war_score` | Can we impose terms on the enemy? | Existing pairwise system |
| `war_contribution_score` | Who has earned standing on our side? | **New — this spec** |
| `war_purpose` / `settlement_tier` | What kind of terms are politically plausible? | WPS-A through WPS-D (landed) |
| `war_bargain` | What specific promise did France make? | WB-A through WB-D (landed) |
| `hegemony` / `betrayal` / `grievance` | How much patience does Europe have left? | Memory and Pressure v2.4.3 (landed) |
| Named diplomats | How the deterministic result is voiced to the player | Diplomat Voice Bible (landed) |

The Napoleonic frame: Napoleon dictated terms after Austerlitz, Jena, Wagram. The interesting tension is not "who gets a turn at the peace table." It is **"how long can you dictate before your allies stop tolerating it?"** — and that arc runs directly through the hegemony pressure system.

Contribution score is not spoils accounting. It is the mechanical basis for **why** an ally has standing. Without it, "Prussia is angry" is arbitrary. With it, "Prussia contributed 31% and you gave them nothing" is legible and deterministic. Personalities voice that result; they do not generate it.

---

## 3. Current Baseline (April 27, 2026)

### 3.1 What already works

**War entry and cascade:**
- `_process_war_cascade()` handles defensive/offensive cascade and vassal auto-join
- DG-4 call-to-arms is direct-only (root attacker/defender allies + direct vassals, no transitive cascade)
- `war_entry_ledger` records honored/refused/vassal entry paths

**War purpose and score:**
- War declarations require choosing an objective (conquest/subjugation/forced_alliance) via War Purpose dialogue (WPS-A)
- Ticking score accumulates per-turn by objective type, capped at 25, paused during armistice
- Settlement tiers (white_peace through total_victory) computed from war score
- Vassalage power cap gates future vassalage proposals (WPS-B)
- Forced alliance and liberation clause types landed (WPS-C)
- AI ticking pressure and settlement tier mismatch warnings landed (WPS-D)

**War Bargains:**
- Data model + creation + validation (WB-A)
- Lifecycle: fulfillment, breach, void (WB-B)
- War-entry integration: `war_entry_score`, hard blocks, `join_opportunity`, counter-bargains, `repudiate_bargain` (WB-C)
- Presentation: commitments routing, notifications, witness scope, voiced templates, ledger badges (WB-D)

**Bilateral peace:**
- Term annotation with `display_label` and ownership (BPH-A)
- Peace preview with frozen war-context snapshot (BPH-B)
- Fallout preview + commitment conflict warnings (BPH-C)
- Ratification summary with territory/gold/casualty snapshots (BPH-D)

**Memory and Pressure:**
- Hegemony detection: bloc geometry, `33/50/60` bands, `balance_of_europe_shifted` beats
- Betrayal memory: strikes, grievance flags, reliability scores
- Make Amends: standard and grievance variants
- DG-4 call-to-arms: refusal → termination → grievance → anti-renewal cooldown
- Commitment paradox popup for alliance-vs-alliance conflicts

### 3.2 What does not exist yet

- **War grouping:** No `war_instance` container. Wars are still only pairwise `diplo_key` entries.
- **Contribution tracking:** No per-nation contribution within a war.
- **Common peace:** Peace proposals are always proposer ↔ target bilateral.
- **Ally beneficiary terms:** `territory_cede` always goes to the proposer. Cannot award territory to an ally.
- **Settlement standing:** No model for who has earned political say on the winning side.
- **Settlement reaction pass:** No post-ratification evaluation of how allies were treated.

### 3.3 What changed since April 13 draft

The original draft was written before Peace Deals shipped. Key reconciliation points:

- **War Bargains now exist.** §15 (Promise Integration) in the old draft described vague "settlement-guarantee promises." War Bargains (WB-A through WB-D) are the concrete implementation. This spec must wire bargain fulfillment/breach into the settlement reaction pass, not reinvent promises.
- **War Purpose now exists.** The old draft's §6 "settlement numbers" did not account for war objectives or ticking score. War purpose and settlement tier legitimacy are now real constraints on what terms are plausible.
- **Hegemony pressure is live.** The old draft's §14 ally fallout was disconnected from hegemony. Settlement terms that look imperial now compound through Balance of Europe, not just bilateral relations.
- **`threat_coalition` is retired.** All coalition/hegemony data flows through `balance_of_europe` exclusively.

---

## 4. Non-Goals

- This spec does not replace the existing pairwise acceptance formula for bilateral peace.
- This spec does not require an HOI4/EU4-style turn-based bidding conference.
- This spec does not require every war to become a multilateral congress.
- This spec does not block separate peace with a universal war-leader lock.
- This spec does not introduce new promise types — War Bargains are the promise system.

---

## 5. Design References

Brief notes on what we take from each game and what we do not.

**Hearts of Iron IV:** Take the concept that participation earns settlement standing distinct from war score. Do not copy the click-contest peace budget minigame.

**Victoria 3:** Take the concept that allies are explicit political participants, not invisible side effects. Do not require every ally to hard-consent to every treaty.

**Europa Universalis IV:** Take the concept that ignoring an ally at settlement creates durable political consequences, stronger when an explicit promise was made. Do not copy province-occupation-transfer micromanagement.

---

## 6. Core Model

### 6.1 Three Settlement Numbers

The system tracks three distinct wartime numbers:

1. **`pairwise_war_score`** — Existing value. Used for bilateral diplomacy, AI peace appetite, harsh terms, armistice logic, and pairwise military pressure. Unchanged.

2. **`side_pressure_score`** — A new war-level summary aggregating the winning side's combined military advantage. Used as the baseline for common peace acceptance by the opposing war leader. Derived from component pairwise war scores, not stored independently.

3. **`war_contribution_score`** — A new participant-level score determining political standing on a side. Used for settlement standing classification, consultation weight, and ally expectations. This is not a spoils budget. It is the mechanical basis for "who earned the right to be heard."

### 6.2 Why this split matters

France may have `+40` war score against Austria. Prussia may have contributed 31% of the winning side's effort. Austria negotiates with France, but Prussia's contribution gives Prussia political standing when Saxony is being distributed.

If we reuse pairwise `war_score` for everything, the ally disappears from the peace table.

---

## 7. War Identity

### 7.1 `war_instance`

A war-level container grouping related bilateral wars into one political conflict.

```python
world.war_instances[war_id] = {
    "war_id": str,
    "created_turn": int,
    "originator": "France",
    "origin_target": "Austria",
    "war_purpose": "conquest",           # from WPS-A
    "attackers": ["France", "Saxony"],
    "defenders": ["Austria", "Prussia"],
    "active_participants": ["France", "Saxony", "Austria", "Prussia"],
    "separate_peaced": [],               # nations that exited via separate peace
    "war_bargains": [],                  # war_bargain IDs attached to this war
}
```

### 7.2 Relationship to current diplomacy state

`war_instance` does not replace pairwise war state.

- `diplomatic_states` remains the source of truth for whether two nations are at war.
- `war_instances` group those pairs into one political conflict for reporting and settlement.
- Cascade entrants attach to the existing `war_id` of the declaration that pulled them in.
- War Bargains created at war entry (WB-C `join_opportunity`) attach to the same `war_id`.

### 7.3 End condition

A `war_instance` ends when no hostile pairs remain between the two sides, or when one side has no active participants remaining.

Separate peace removes a nation from the active participant list without ending the whole war.

---

## 8. Political Standing

### 8.1 Standing levels

Every active participant on a side has one of four standing levels at settlement time:

| Level | Meaning |
|-------|---------|
| `seat` | Full participant. Expectations visible. Ignoring them is a major political event. |
| `consult` | Meaningful contributor. Talleyrand warns about their interests. Ignoring them costs relations and reputation. |
| `beneficiary_only` | Receiving or losing a direct outcome, but without broad leverage. |
| `no_standing` | Low contribution, no direct stake, no promise, no affected territory. Not surfaced in the advisory. |

### 8.2 Standing classification rules

Standing is rule-based with numeric thresholds, not a fuzzy formula. Personalities color the reaction, not the bucket.

**`seat`** — any of:
- Active `major` power on the same side
- Explicit war bargain or promise directly involving a term being decided
- Own capital, survival, or core territory being decided
- Contribution share >= 25%

**`consult`** — any of:
- Contribution share >= 10%
- `secondary` power with meaningful contribution
- Region claim or territorial interest directly affected by a term
- Treaty ally (ALLIANCE / DEFENSIVE_ALLIANCE) materially involved in the war

**`beneficiary_only`** — any of:
- `minor` / vassal / liberated state receiving or losing a direct outcome
- Low contribution but a specific term names them as beneficiary or target

**`no_standing`** — none of the above apply.

### 8.3 Standing inputs

Standing is computed from:

1. **Contribution share** — from `war_contribution_score` (§9)
2. **Power tier** — `major / secondary / minor` (authored scenario data)
3. **Direct territorial interest** — regions being transferred that the nation borders, previously owned, or covets
4. **Active war bargain** — any WB-A bargain with `named_enemy` or `claim_region` involved in the settlement
5. **Treaty depth** — current diplomatic state with France (ALLIANCE > DEFENSIVE_ALLIANCE > lesser)
6. **Survival stakes** — own capital threatened, elimination risk, or core territory being ceded

---

## 9. War Contribution Score

### 9.1 Field

```python
world.war_contribution_scores[war_id][nation] = int
```

Side-local score. Normalized into percentage share at settlement time:

```python
standing_share[nation] = war_contribution_scores[war_id][nation] / total_side_contribution
```

### 9.2 Contribution buckets

Four buckets with suggested weighting:

| Bucket | Weight | What counts |
|--------|--------|-------------|
| `battle_contribution` | 40% | Casualties inflicted, casualties suffered (reduced weight), decisive battle participation |
| `occupation_contribution` | 35% | Enemy regions captured, enemy capital captured, allied/liberated regions restored |
| `staying_power` | 15% | Turns as active war participant (capped to prevent time-farming) |
| `support_contribution` | 10% | Hook for gold/subsidy/AP support; can be zero-weighted in v0.1 if support transfers are not yet wired |

### 9.3 Battle record extension

Current `battle_records` are pairwise and record one attacker/defender nation. That is not enough for allied contribution.

Extend battle records for coordinated battles:

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
    "war_id": "war_12",
}
```

Without this extension, any contribution system will mis-credit coalition battles.

---

## 10. Peace Types

### 10.1 Separate peace

The current bilateral model. Unchanged for:

- Armistice
- Simple peace
- Gold / manpower / AP exchanges
- Bilateral concession with no third-party beneficiary
- Coalition splitting

**New requirement:** Separate peace now fires a **settlement reaction pass** (§14) for France's remaining co-belligerents in the same `war_instance`. It checks:

- Did France abandon an ally still fighting?
- Did the separate peace make a war bargain impossible to fulfill?
- Did it shut out a high-standing contributor?
- Did it normalize with a bargain target (the named enemy)?
- Did it remove the enemy or region that an ally cared about?

This is where "you can do it, but allies remember" lives.

### 10.2 Common peace

A new war-scoped settlement mode. One package keyed to `war_instance`, not a sequence of bilateral deals.

Internally, terms are grouped by payer / target enemy:

- Terms imposed on Austria
- Terms imposed on Prussia
- Beneficiaries on France's side
- Side-wide political aftermath

If France wants to resolve only Austria while the larger war continues, that is separate peace, not common peace.

### 10.3 Wizard routing

Keep the existing bilateral wizard for separate peace, armistice, and bilateral deals.

When allied participation matters, route into a dedicated settlement flow:

- Entry choice: **Separate peace** vs **Open settlement**
- Separate peace stays in the existing bilateral wizard, but now shows ally-fallout and bargain-breach warnings before send
- Open settlement launches a war-scoped flow keyed to `war_id`

---

## 11. Mechanical Flow

No peace-conference turns. No EU4/HOI4 bidding. Peace is a decisive French action with visible consequences.

### Step 1: Player opens peace

- From the diplomacy wizard or war status panel, the player chooses **Separate peace** or **Open settlement**.
- Separate peace routes to the existing bilateral wizard (with new ally-fallout warnings).
- Open settlement enters the war-scoped settlement flow.

### Step 2: Talleyrand advisory preview

The system computes each participant's standing (§8) and generates structured warnings:

- Standing level per ally (seat / consult / beneficiary_only / no_standing)
- Active war bargains and their status (fulfillable / at risk / impossible)
- Contribution shares and what each ally expects
- Territory legitimacy warnings (§12) for each demand
- Hegemony impact preview

Example warnings:
- *"Prussia contributed 31% and expects Saxony under an active war bargain."*
- *"Austria will view exclusion from Bohemia as deliberate humiliation."*
- *"Demanding unoccupied Rhineland without meaningful pressure against Prussia carries severe acceptance cost."*

### Step 3: Player finalizes terms

- One package. Terms grouped by target enemy.
- Player can include ally beneficiary terms (§13).
- No ally turns. France decides.
- Severe cases (active war bargain breach, shutting out a `seat`-level ally) trigger a second Talleyrand confirm. This confirm is a warning, not a veto.

### Step 4: Enemy acceptance

**Separate peace:** Use the existing pairwise acceptance formula. Unchanged.

**Common peace:** The opposing war leader accepts or rejects the whole package. No majority vote, no per-enemy veto.

Common peace acceptance is a new war-scoped calculation:

```
common_peace_acceptance =
    base_side_pressure
    + settlement_tier_legitimacy
    + term_harshness_penalty
    + burdened_participant_penalty      # terms that hit non-leader enemies hard
    + leader_own_losses
    + war_purpose_alignment
    + hegemony_pressure                 # where relevant
    + war_exhaustion                    # from existing coalition system
```

If accepted, all covered active hostile pairs resolve. If rejected, the whole package fails. France can then try separate peace with individual enemies or revise terms.

### Step 5: Settlement reaction pass

After peace succeeds, every relevant party evaluates the outcome. Run for **both sides**, but keep enemy-side consequences lighter in the first pass.

**France-side reactions** (main player-facing loop):

| Outcome | Consequence |
|---------|-------------|
| War bargain honored | Positive relation, `they_chose_us`, fulfillment spotlight, bargain → `fulfilled` |
| High-standing ally rewarded | Relation bonus, acceptance bonus on future proposals |
| High-standing ally shut out | `shut_out_in_settlement` grievance, relation hit, future acceptance penalty |
| Explicit war bargain breached | Route through betrayal/reliability machinery (existing WB-B breach pipeline) |
| Major power humiliated | Downgrade pressure, hard-reject posture risk, coalition drift |
| Minor harmed | Narrower reaction — only when survival, capital, promise, or territory involved |

**Enemy-side reactions** (lighter first pass):

| Outcome | Consequence |
|---------|-------------|
| Enemy ally sacrificed by their leader | Resentment toward their own war leader, political drift |
| Disproportionate terms on a secondary enemy | Relation damage toward France, future resistance |

**Europe at large:**

| Outcome | Consequence |
|---------|-------------|
| Imperial-looking settlement | Hegemony / Balance of Europe reaction through existing `balance_of_europe_shifted` beats |
| Forced alliance imposed | Coalition threat increase (WPS-C, already wired: +15 per forced alliance) |

### Step 6: Next-turn presentation

- Notification rail, dispatch, ledger, named diplomat voice.
- Do not spam one popup per ally. Aggregate reactions, then spotlight only major breaches or bargain fulfillment/breach.
- Use the existing commitments routing table (§8.1 from `COMMITMENTS_PRESENTATION_SPEC.md`) for settlement event families.

---

## 12. Territory Demand Legitimacy

Territorial demands require a **pressure basis**. Occupation is not mandatory — Napoleon often dictated unoccupied concessions after decisive victories — but every region transfer must be justified. Demands without a pressure basis are legal only as extreme terms and carry severe acceptance and hegemony consequences.

### 12.1 Pressure bases

For every territorial term, evaluate:

| Basis | Strength | Description |
|-------|----------|-------------|
| `occupied_by_france_side` | Strong | Region is currently controlled by France or a French-side ally |
| `war_objective_or_bargain` | Strong | Region is tied to declared war purpose, liberation objective, or active war bargain |
| `high_pairwise_pressure` | Medium | France has strong pairwise war score against `from_nation` |
| `general_side_victory` | Weak | France's side is winning the overall war, but France has little direct pressure on `from_nation` |

### 12.2 Penalty rules

```
territory_demand_cost =
    base_territory_demand
    + unoccupied_region_penalty          # if not held by France's side
    + weak_pressure_penalty              # if low pairwise war score against from_nation
    + excessive_land_burden_penalty      # if too many regions demanded from one enemy
    - occupied_discount                  # if held by France's side
    - war_purpose_discount               # if tied to declared objective
    - bargain_promise_discount           # if tied to active war bargain or commitment
    - liberation_claim_discount          # if restoring a liberated nation
```

### 12.3 Edge cases

- **Region belongs to a non-participant:** Hard stop. Cannot demand territory from a nation not in the war.
- **`from_nation` is only an enemy ally that France barely fought:** Very high acceptance penalty. The enemy war leader will resist giving away an ally's land when that ally is not the one who lost.
- **Region tied to a war bargain but unoccupied:** Bargain discount reduces but does not eliminate the unoccupied penalty. Promise legitimacy helps, but the enemy still knows France doesn't hold it.

### 12.4 Talleyrand warnings

Territory legitimacy feeds into the Step 2 advisory preview:

- *"We hold Saxony. Austria has little ground to refuse."*
- *"We demand Bohemia, but no French marshal has set foot there. Austria will resist fiercely."*
- *"Prussia is barely a party to this war. Taking Silesia from them is an act of imperial overreach."*

---

## 13. Term Ownership

### 13.1 Beneficiary fields on existing terms

France can award territory to an ally. Use ownership fields on existing `territory_cede`, not a new term type:

```python
{
    "type": "territory_cede",
    "from_nation": "Austria",
    "to_nation": "Prussia",
    "beneficiary": "Prussia",
    "regions": ["Saxony"],
    "war_id": "war_12",
    "settlement_reason": "promise",  # promise | contribution | buffer | liberation
}
```

New term types are reserved for genuinely different political actions (forced_alliance, liberation — already landed in WPS-C).

### 13.2 Allowed beneficiaries

In common peace, the beneficiary can be:

- France
- An active ally on France's side
- A liberated nation
- A former owner restored by treaty

### 13.3 First-pass restrictions

Do not support:

- Ally gives region to another ally through three-step chains
- Hidden off-screen transfer to non-participants
- Nested protectorate / vassal / subject distribution logic

Keep the first pass to direct, legible outcomes.

---

## 14. Settlement Reaction Pass

### 14.1 `shut_out_in_settlement`

If an ally contributed meaningfully and France concludes peace that excludes them from meaningful gain, apply a settlement grievance. This is a **new grievance type**, not automatically a betrayal strike.

### 14.2 Severity bands

**Minor shut-out:**
- Ally contributed but had no promise and no high-interest claim
- Effect: moderate relation hit only (`-5` to `-10` relation)

**Major shut-out:**
- Ally had strong claim interest or high contribution (>= 20%)
- Effect: larger relation hit (`-15` to `-25`), acceptance penalty on future proposals, possible treaty downgrade pressure

**Promise breach (war bargain):**
- France could have honored an active war bargain and chose not to
- Effect: route through existing WB-B breach pipeline → `bargain_breached` → betrayal strike + reliability hit + grievance flag + potential anti-renewal cooldown

**Major power humiliation:**
- `major` power with `seat` standing, excluded or visibly subordinated
- Effect: hard-reject posture risk, coalition drift via hegemony pressure, possible `balance_of_europe_shifted` beat

### 14.3 Power tier reaction scaling

| Tier | Reaction scope |
|------|---------------|
| `major` | Bigger anger when excluded. More likely to downgrade alignment or shift against France politically. Coalition drift. |
| `secondary` | Moderate reaction. Primarily care about direct territorial interests and promises. |
| `minor` | Narrow reaction. Only care when survival, capital, or explicit promised reward is involved. |

### 14.4 Separate peace fallout

Separate peace fires a smaller settlement reaction pass for France's remaining co-belligerents in the `war_instance`:

- Abandoned ally still fighting → relation hit + possible `shut_out_in_settlement`
- Separate peace made a war bargain impossible → route through WB-B breach
- Separate peace removed the enemy or region an ally cared about → consultation-level grievance
- Separate peace normalized with a bargain target → bargain void check

---

## 15. War Bargain Integration

War Bargains (WB-A through WB-D) are the promise system. This spec does not invent new promise types. It wires bargains into the settlement machinery.

### 15.1 Bargain fulfillment at settlement

A war bargain with `named_enemy` and/or `claim_region` is considered **fulfilled** when:

- The beneficiary was on France's side in the war
- The final peace terms award or secure the promised outcome (e.g., region transferred to beneficiary)
- The beneficiary is legally eligible for the region

Settlement ratification triggers `bargain_fulfilled` through the existing WB-B lifecycle.

### 15.2 Bargain breach at settlement

A war bargain is **breached** when:

- France could have honored the bargain (the outcome was feasible given war score and occupation) and chose not to
- France cuts separate peace that makes the bargain impossible
- France awards the promised region to itself or a different ally

Settlement-triggered breach routes through the existing WB-B breach pipeline: `bargain_breached` → betrayal strike + reliability hit + grievance flag.

### 15.3 Bargain visibility in advisory

Step 2 (Talleyrand advisory) surfaces every active war bargain tied to the `war_instance`:

- Bargain status: fulfillable / at risk / impossible given current terms
- Beneficiary standing level
- Cost of breach (reliability hit, relation damage, named-diplomat reaction)

### 15.4 Dormant bargains

War Bargains that are dormant (neither fulfillable nor breachable due to war state) remain dormant through settlement. They do not block peace. The existing WB-B dormant-reminder dispatch continues to surface them.

---

## 16. Talleyrand Advisory and UI Surface

### 16.1 Talleyrand as settlement counsel

In common peace, Talleyrand surfaces:

- Current participants and their standing levels
- Contribution shares
- Active war bargains and their fulfillment status
- Territory legitimacy for each demand
- Likely reactions if an ally is cut out
- Whether a region is "theirs by contribution," "theirs by bargain," or "ours if we insist"

### 16.2 UI surfaces

Use existing surfaces where possible:

| Surface | Settlement use |
|---------|---------------|
| Proposal preview / advisory | Standing, bargain status, territory legitimacy, ally-fallout warnings |
| War status panel | Participant list, contribution shares, war bargain status |
| Diplomatic ledger | Post-settlement: grievance records, bargain outcomes |
| Dispatch | Post-ratification: settlement reaction summaries |
| Notification rail | Major events: bargain fulfilled, major shut-out, promise breach |

### 16.3 Warning presentation

Settlement warnings use the same structured `warnings[]` approach as bilateral diplomacy:

- Max 2 inline warnings in default preview, severity-sorted
- Overflow behind "View all concerns"
- Settlement-specific warnings (promise breach, major ally fallout) outrank generic rivalry flavor

### 16.4 Hard stops vs soft warnings

**Hard stop only for:**
- Impossible / invalid settlement shapes (e.g., demanding territory from a non-participant)
- Term packages that would create contradictory state

**Everything else is political cost, not veto:**
- Ally consultation skipped
- Great-power humiliation risk
- Shut-out risk
- Separate-peace fallout
- Promise breach warning (player can still choose to proceed)

---

## 17. Data Model Additions

### 17.1 New fields

```python
world.war_instances: Dict[str, Dict] = {}
world.war_contribution_scores: Dict[str, Dict[str, int]] = {}
world.shut_out_in_settlement: Dict[str, List[Dict]] = {}
```

### 17.2 Extended fields

```python
# Battle records gain optional multi-participant detail
battle_record["attacker_participants"] = ["France", "Saxony"]
battle_record["defender_participants"] = ["Austria", "Prussia"]
battle_record["nation_casualty_map"] = {"France": 4000, "Saxony": 1200, ...}
battle_record["war_id"] = "war_12"

# Territory terms gain beneficiary ownership
term["beneficiary"] = "Prussia"
term["settlement_reason"] = "promise"  # promise | contribution | buffer | liberation
term["war_id"] = "war_12"
```

### 17.3 Derived at settlement time (not stored)

```python
standing_share[nation] = war_contribution_scores[war_id][nation] / total_side_contribution
standing_level[nation] = classify_standing(nation, war_instance, standing_share, ...)
side_pressure_score = aggregate_pairwise_war_scores(war_instance)
```

### 17.4 Compatibility

- Keep `war_scores`, `battle_records`, `decisive_battles`, `war_start_turns`, `war_purposes`
- Do not migrate or delete existing pairwise structures
- Build the new layer on top of them

---

## 18. Implementation Sequence

This sequence is post-Peace-Deals. All Peace Deals dependencies (BPH, WPS, WB) are landed.

### Slice A: War identity + read-only grouping

- Add `war_instance` container
- Create `war_instance` on war declaration; attach cascade entrants to same `war_id`
- Wire War Bargain `war_id` attachment at join_opportunity
- Expose participant lists in war status panel and debug endpoints
- Serialization: `to_dict` / `from_dict` round-trip for `war_instances`
- ~20 tests

### Slice B: Contribution tracker

- Add `war_contribution_scores` field
- Extend battle records with multi-participant attribution and `war_id`
- Wire contribution accrual: battle (casualties inflicted/suffered), occupation (region captures), staying power (active turns)
- Derive contribution shares at query time
- Standing classification: `classify_standing()` with rule-based bucket assignment
- ~25 tests

### Slice C: Common peace plumbing + territory legitimacy

- Add `Open settlement` entry point (separate from bilateral wizard)
- One-package term builder grouped by target enemy
- Ally beneficiary fields on `territory_cede`
- Territory demand legitimacy evaluation
- Common peace acceptance formula (opposing war leader)
- Talleyrand advisory preview: standing, bargains, territory legitimacy, ally-fallout warnings
- ~30 tests

### Slice D: Settlement reaction pass + bargain integration

- Post-ratification reaction pass for both sides
- `shut_out_in_settlement` grievance type with severity bands
- Wire war bargain fulfillment/breach at settlement through existing WB-B pipeline
- Separate peace fallout: smaller reaction pass for remaining co-belligerents
- `they_chose_us` upside for rewarded allies
- Hegemony reaction for imperial-looking settlements
- ~25 tests

### Slice E: Presentation + polish

- Settlement warnings in proposal preview
- War status panel: contribution shares, standing levels
- Dispatch: settlement reaction summaries
- Notification rail: major settlement events (bargain fulfilled, major shut-out, promise breach)
- Named diplomat voice for settlement reactions (per Voice Bible)
- Ledger: post-settlement records
- ~15 tests

**Estimated total: ~115 tests across 5 slices.**

---

## 19. Testing Focus

Highest-priority tests:

1. Cascade-created ally enters same `war_instance` as original declaration.
2. War Bargain created at war entry attaches to the correct `war_id`.
3. Separate peace removes only that participant from the active list; does not end the war.
4. Separate peace fires settlement reaction pass for remaining co-belligerents.
5. Common peace sends one package; opposing war leader accepts/rejects whole.
6. Common peace can award territory to ally beneficiary via `territory_cede` with `beneficiary` field.
7. High-contribution ally excluded from common peace gains `shut_out_in_settlement` grievance.
8. Active war bargain denied when feasible triggers breach through WB-B pipeline.
9. Active war bargain honored at settlement triggers fulfillment through WB-B pipeline.
10. Territory demand for unoccupied region carries acceptance penalty; occupied region does not.
11. Territory demand against barely-fought enemy ally carries severe acceptance penalty.
12. `major` power with `seat` standing gets consultation warning even with lower contribution.
13. `minor` ally only surfaces when its direct interests (survival, capital, promise, territory) are involved.
14. Battle attribution in coordinated allied battles feeds the correct contribution score.
15. Existing bilateral peace proposals still work unchanged in wars without allied settlement needs.
16. Side pressure score aggregation does not break existing pairwise peace acceptance logic.
17. Standing classification respects all six inputs (contribution, power tier, territorial interest, bargain, treaty depth, survival).
18. Settlement reaction pass fires for both France-side and enemy-side participants.
19. Imperial-looking settlement compounds through `balance_of_europe_shifted` hegemony beats.
20. Dormant war bargains remain dormant through settlement; do not block peace.

---

## 20. Design Calls

### 20.1 Contribution is political standing, not spoils accounting

`war_contribution_score` determines who has earned the right to be heard. It is the mechanical basis for ally expectations. It is not an HOI4-style peace budget.

### 20.2 Keep separate peace

The interesting tension is not "peace is impossible unless the war leader says yes." The interesting tension is "you can cut a separate deal, but doing so may cost you allies."

### 20.3 No ally turns at the peace table

France dictates. Allies react. The drama is in the pre-visible advisory (knowing the cost) and the post-ratification memory (paying the cost). No conference minigame.

### 20.4 War Bargains are the promise system

Do not reinvent promises. War Bargains (WB-A through WB-D) handle creation, lifecycle, fulfillment, breach, and presentation. This spec wires them into settlement. If a new promise type is needed, extend War Bargains — do not add a parallel system.

### 20.5 Territory demands require a pressure basis

Occupation is the cleanest legitimacy basis. Unoccupied demands are legal but expensive. Demands against barely-fought enemies are brutal. This constraint prevents the player from making sweeping imperial demands without military backing, while still allowing decisive-victory dictation.

### 20.6 Power tiers are authored, not dynamic

`power_tier` is scenario data (`major / secondary / minor`). It affects consultation rights, not free settlement score. Dynamic power tiers remain a later enhancement.

### 20.7 Allies matter without universal veto

Standing, consultation, entitlement, and fallout — not hard blocking. Political cost, not absolute lockout. This follows the core design philosophy: the player always gets to choose, but the consequences are real and compound through existing systems.
