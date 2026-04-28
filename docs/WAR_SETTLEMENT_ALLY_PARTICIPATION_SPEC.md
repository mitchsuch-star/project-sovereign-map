# Imperial Settlement: War Settlement + Ally Participation Spec

> **Status:** v1.3 FULL-EUROPE SCALE HARDENING - implementation plan written; coding may start from `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md`
> **Last Updated:** April 28, 2026
> **Companion docs:** `DIPLOMACY_SPEC.md`, `COALITION_SPEC.md`, `RELIABILITY_COMMITMENTS_SPEC.md`, `PEACE_DEALS_UMBRELLA_SPEC.md`, `WAR_BARGAIN_SPEC.md`, `WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md`, `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md`, `STATUS.md`
> **Depends on (all landed):** Memory and Pressure v2.4.3, Bilateral Peace Hardening (BPH-A through BPH-D), War Purpose + Score Semantics (WPS-A through WPS-D), War Bargains (WB-A through WB-D)

---

## 0. Scale and Ownership Contract

This spec is authored for the full 1805 Europe scale, not only the five-nation prototype. Implementation must assume:

- DG-1 roster scale: 13-20 active nations.
- 100+ regions and 78+ bilateral pair keys.
- Multiple simultaneous `war_instance` records.
- Coalition wars with 6-8 participants per side.
- Cross-theater fighting in Germany, Italy, Iberia, the Baltic, and the eastern frontier.

Design rule for this document: no unowned deferrals. A feature is either specified here, marked out of scope as not part of this settlement system, or tracked in `STATUS.md` / `ROADMAP.md` as a separate phase. This spec owns every item needed to make ally-aware settlement playable at full-Europe scale.

Scale guardrails:

- Settlement computation only scans active war participants, direct term targets/beneficiaries, active bargain parties, affected territorial-interest nations, and active major powers. Do not broad-scan every nation for every term.
- Player-facing advisory rows use deterministic salience filtering: top 5 default rows, grouped overflow behind "View all participants."
- Dispatch and notification output is aggregated. No settlement may emit one popup or rail notice per participant.
- `war_instance` grouping is additive over pairwise diplomacy. Pairwise `diplomatic_states`, `war_scores`, and WPS `war_objectives` remain the mechanical source of truth.

---

## 1. Problem Statement

The current diplomacy game supports allies entering wars and making war bargains, but peace is still negotiated as a pairwise deal. That creates four gaps:

1. France can fight a multi-nation war, but peace resolves as separate bilateral treaties.
2. War Bargains create named-enemy, France-claim promises (WB-A through WB-D), but the peace machinery cannot evaluate those promises beside ally rewards and settlement standing.
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
| `war_objectives` / `settlement_tier` | What kind of terms are politically plausible? | WPS-A through WPS-D (landed) |
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
- Vassalage power cap gates vassalage proposals (WPS-B)
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
- This spec does not redefine War Bargain fulfillment as ally-land transfer. Shipped War Bargains are France-claim-scoped; ally-beneficiary settlement terms are rewards/standing outcomes, not current WB fulfillment.

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

2. **`side_pressure_score`** — A new war-level summary aggregating the winning side's combined military advantage. Used as the baseline for common peace acceptance by the opposing war leader. Derived from component pairwise war scores using §6.3, not stored independently.

3. **`war_contribution_score`** — A new participant-level score determining political standing on a side. Used for settlement standing classification, consultation weight, and ally expectations. This is not a spoils budget. It is the mechanical basis for "who earned the right to be heard."

### 6.2 Why this split matters

France may have `+40` war score against Austria. Prussia may have contributed 31% of the winning side's effort. Austria negotiates with France, but Prussia's contribution gives Prussia political standing when Saxony is being distributed.

If we reuse pairwise `war_score` for everything, the ally disappears from the peace table. If we use only a war-level average, lopsided full-Europe coalitions become misleading: France can crush two minors while barely touching two majors. The settlement needs both numbers.

### 6.3 `side_pressure_score` formula

`side_pressure_score` is a power-weighted average, not a sum. Summing pairwise scores would let France farm pressure by dragging minors into a war; using only the maximum pair would erase broad coalition pressure.

For a proposed common peace, compute pressure from France's side against each covered enemy participant:

```python
pressure_terms = []
for enemy in covered_enemy_participants:
    direct_score = max(
        get_war_score_for(world, side_member, enemy)
        for side_member in active_france_side_participants
        if world.is_at_war(side_member, enemy)
    )
    weight = {"major": 3, "secondary": 2, "minor": 1}.get(
        world.get_power_tier(enemy) or "secondary",
        2,
    )
    pressure_terms.append((direct_score, weight))

side_pressure_score = (
    sum(score * weight for score, weight in pressure_terms)
    // sum(weight for _, weight in pressure_terms)
)
```

Rules:

- Empty `pressure_terms` is a hard stop: common peace has no valid covered enemy.
- Implementation must build `direct_scores` before calling `max()`. A covered enemy with no active direct pair against France's side is a hard stop for that enemy: `no_direct_war_score_for_covered_enemy`.
- Scores are clamped to the existing `[-100, 100]` war-score range after aggregation.
- `side_pressure_score` is a headline/base component. It is not blanket authorization for target-specific demands.
- Terms against a non-leader enemy with `direct_score < 20` are legal only as extreme terms and add the Step 4 burdened-participant penalty.

Per-target direct-score gates:

| Direct score against payer | Non-trivial terms allowed |
|----------------------------|---------------------------|
| `< 0` | Only occupied, objective-linked, or bargain-linked territorial terms; severe burden penalty |
| `0-19` | Extreme terms only; severe warning and burden penalty |
| `20-39` | Limited territory, gold, manpower, open-borders / non-aggression terms |
| `40-59` | Multiple regions, liberation, strong reparations, forced Continental System |
| `60-79` | Forced alliance if capital / objective basis exists, AP/turn, harsh territorial package |
| `80+` | Total-victory terms, subject to WPS power cap and material-state validity |

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
    "origin_diplo_key": "Austria|France",
    "objective_keys": ["Austria|France"],  # WPS-A war_objectives keys, not a new objective store
    "attacker_leader": "France",
    "defender_leader": "Austria",
    "leader_source": "originator",       # originator | coalition_leader | scripted
    "attackers": ["France", "Saxony"],
    "defenders": ["Austria", "Prussia"],
    "side_by_nation": {
        "France": "attackers",
        "Saxony": "attackers",
        "Austria": "defenders",
        "Prussia": "defenders",
    },
    "active_participants": ["France", "Saxony", "Austria", "Prussia"],
    "participant_meta": {
        "France": {"side": "attackers", "joined_turn": 12, "exited_turn": None, "entry_path": "originator"},
        "Saxony": {"side": "attackers", "joined_turn": 12, "exited_turn": None, "entry_path": "ally_cascade"},
    },
    "separate_peaced": [],               # nations that exited via separate peace
    "war_bargains": [],                  # war_bargain IDs attached to this war
}
```

### 7.2 Relationship to current diplomacy state

`war_instance` does not replace pairwise war state.

- `diplomatic_states` remains the source of truth for whether two nations are at war.
- `war_instances` group those pairs into one political conflict for reporting and settlement.
- Create `war_instance` before `_process_war_cascade()` runs, then pass `war_id` through the cascade path so honored/refused/vassal entries can append to the instance as they resolve.
- Cascade entrants attach to the existing `war_id` of the declaration that pulled them in.
- War Bargains created at war entry (WB-C `join_opportunity`) attach to the same `war_id`.

### 7.3 End condition

A `war_instance` ends when no hostile pairs remain between the two sides, or when one side has no active participants remaining.

Separate peace removes a nation from the active participant list without ending the whole war.

### 7.4 War leaders

Common peace uses side leaders, not majority votes:

- The originator is the attacker leader unless a coalition declaration supplies `active_coalition.leader`.
- The origin target is the defender leader unless a coalition declaration supplies `active_coalition.leader`.
- If a leader exits by separate peace, leadership passes to the active same-side participant with the highest `coalition_leadership_score()` when available; otherwise use power tier (`major > secondary > minor`), then active army strength, then alphabetical name.
- If no replacement exists, that side has no active participants and the `war_instance` ends.

The opposing leader can accept a package that burdens non-leader allies. This is intentional Napoleonic drama, not a veto gap. The sold-out participant receives a primary enemy-side reaction in §14.6, and severe non-leader burdens feed the Step 4 acceptance penalty.

---

### 7.5 Mid-war joiners and re-entry

At full-Europe scale, `war_instance` participants change over time. Nations can join through coalition mechanics, defensive calls, opportunistic entry, subsidy pressure, or a treaty signed after the war begins. Standing and contribution must use the nation episode inside the war, not only the war start.

Rules:

- `participant_meta[nation]["joined_turn"]` is the source of truth for when that nation's current active episode began.
- `staying_power` counts from `joined_turn`, not from `war_instance["created_turn"]`.
- Late joiners receive full battle, occupation, and support credit for events after `joined_turn`; do not apply a blanket contribution penalty to decisive late military action.
- No retroactive contribution credit is awarded for turns, battles, occupations, or support before the join episode.
- If a nation exits and then re-enters the same `war_instance`, append an episode record:

```python
participant_meta[nation]["episodes"] = [
    {"joined_turn": 12, "exited_turn": 18, "entry_path": "ally_cascade"},
    {"joined_turn": 22, "exited_turn": None, "entry_path": "coalition_reentry"},
]
```

Current standing uses the active episode. Historical totals in the war status panel may show prior episodes, but settlement contribution uses only active-episode contribution unless a term directly references the earlier exit settlement.

Late-joiner examples:

- Sweden joins on turn 15, fights decisively at turn 16, and earns `consult` or `seat` through battle/occupation contribution even though its `staying_power` is low.
- A minor joins on turn 18, never fights, and receives only the small `staying_power` earned since entry.

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

Definitions used by the buckets:

- `material_contribution_points = battle + occupation + support`
- `staying_power` alone can create a low visible participation note, but cannot by itself trigger `seat`, 15% / 25% contribution dispatches, or a major shut-out grievance.
- A `secondary` co-belligerent with any material contribution has at least `consult` standing. This prevents Spain, Sweden, Naples, Denmark, or the Ottoman Empire from vanishing in an 8-participant coalition where contribution shares are naturally diluted.

**`seat`** — any of:
- Active `major` power on the same side
- Active war bargain whose named enemy or claim region is directly involved in a term being decided
- Own capital, survival, or core territory being decided
- Contribution share >= 25% and `material_contribution_points > 0`

**`consult`** — any of:
- Contribution share >= 10% and `material_contribution_points > 0`
- `secondary` power with any material contribution
- Region claim or territorial interest directly affected by a term
- Treaty ally (ALLIANCE / DEFENSIVE_ALLIANCE) materially involved in the war
- `rival_strengthened` applies: a settlement transfers territory or alignment control to a rival / opposing-bloc nation adjacent to this nation or inside its local sphere

**`beneficiary_only`** — any of:
- `minor` / vassal / liberated state receiving or losing a direct outcome
- Low contribution but a specific term names them as beneficiary or target

**`no_standing`** — none of the above apply.

### 8.3 Standing inputs

Standing is computed from:

1. **Contribution share** — from `war_contribution_score` (§9)
2. **Power tier** — `major / secondary / minor` (authored scenario data)
3. **Direct territorial interest** — regions being transferred that the nation borders, previously owned, or covets
4. **Active war bargain** — any WB-A bargain with `target_enemy` or `claim_term.claim_region` involved in the settlement; this grants standing and breach visibility, not automatic ally-land entitlement
5. **Treaty depth** — current diplomatic state with France (ALLIANCE > DEFENSIVE_ALLIANCE > lesser)
6. **Survival stakes** — own capital threatened, elimination risk, or core territory being ceded

Additional standing input:

7. **Rival strengthened / local balance threat** — settlement strengthens a negative-relation rival, opposing-bloc member, or sphere competitor on the nation's border.

`rival_strengthened` is the local balance-of-power input. Austria may not covet Silesia, but Austria cares if France hands Silesia to Prussia and creates a stronger Prussian border. Sweden cares if Finnish territory goes to Russia. Austria, Russia, and Britain all care when Ottoman territory is redistributed into a rival sphere. The advisory should surface this as a political warning, for example: "Austria views handing Silesia to Prussia as a provocation: it strengthens their rival on their border."

Canonical data source: do not restore a static `nation_rivalries` store. `compute_local_balance_warning(nation, settlement_terms)` derives `rival_strengthened` from live state only:

- `world.get_diplomatic_state(nation, beneficiary)` is `WAR` or relation is `<= -40`.
- The beneficiary is in an opposing bloc from `get_bloc_members()` / Balance of Europe geometry.
- The transferred or forced-aligned region is adjacent to a region controlled by `nation`, appears in `nation_starting_regions[nation]`, or appears in the existing desire-profile `covets_regions` data.
- The beneficiary gains territory, vassalage, forced alliance, or liberation control from the settlement term.

The helper scans only settlement beneficiaries, affected regions, adjacent controllers, and active major powers. It must not broad-scan every nation for every term.

---

## 9. War Contribution Score

### 9.1 Field

```python
world.war_contribution_scores[war_id][nation] = {
    "battle": int,
    "occupation": int,
    "staying_power": int,
    "support": int,
    "total": int,
}
```

Side-local score. Normalized into percentage share at settlement time:

```python
standing_share[nation] = contribution_total(nation) / total_side_contribution
```

If `total_side_contribution <= 0`, the leader receives `seat`, direct beneficiaries receive `beneficiary_only`, and all other participants resolve to `no_standing`.

### 9.2 Contribution buckets

Four buckets with fixed weighting:

| Bucket | Weight | What counts |
|--------|--------|-------------|
| `battle_contribution` | 40% | Casualties inflicted, casualties suffered (reduced weight), decisive battle participation |
| `occupation_contribution` | 35% | Enemy regions captured, enemy capital captured, allied/liberated regions restored |
| `staying_power` | 15% | Turns as active war participant (capped to prevent time-farming) |
| `support_contribution` | 10% | Gold, subsidy, AP, manpower, access, or supply support delivered to active same-side participants during the war |

Contribution scoring:

```python
battle_side_raw =
    side_casualties_inflicted // 100
    + side_casualties_suffered // 250
    + decisive_battle_win * 25

battle_raw[nation] =
    round(battle_side_raw * nation_theater_strength[nation] / side_theater_strength)

occupation_raw =
    enemy_regions_captured * 20
    + enemy_capitals_captured * 40
    + allied_or_liberated_regions_restored * 15

staying_power_raw =
    min(active_turns, 10) * 5

support_raw =
    wartime_gold_or_subsidy_value // 100
    + ap_support_value * 5
    + manpower_support_value // 500
```

If `side_theater_strength <= 0`, the battle awards no contribution points and emits a debug warning; do not divide by zero or fall back to all participants.

Normalize each bucket against the side total for that bucket, multiply by the bucket weight, and store integer points:

```python
bucket_points[nation] = round((nation_bucket_raw / side_bucket_raw) * bucket_weight)
```

If a side bucket has zero raw contribution, it awards zero points and its unused weight is not redistributed. Support counts only when an actual support event exists; Britain or another paymaster receives support contribution for real gold / subsidy / AP / manpower support, while `major` auto-seat prevents a major war funder from disappearing when a war has no recorded support events.

Support contribution event schema:

```python
{
    "type": "war_support_delivered",
    "war_id": "war_12",
    "supporter": "Britain",
    "recipient": "Prussia",
    "support_kind": "gold",  # gold | subsidy | ap | manpower | access | supply
    "value": 500,
    "turn": 18,
    "source": "treaty_clause",  # treaty_clause | command | scripted_ai | settlement_followup
    "episode_id": "support-18-3",
}
```

Emission hooks are event-driven only: treaty-clause ratification, explicit support commands, scripted AI support, and any future settlement follow-up that transfers support. Contribution readers dedupe by `episode_id` and ignore support where either side is not an active same-side participant in `war_id` on that turn. Access/supply support uses `value = 1` per qualifying turn and is capped at `5` raw support points per war to prevent open-borders farming.

### 9.3 Player-facing contribution signals

Contribution should not ambush the player at settlement. Exact shares stay in the Talleyrand advisory, but the war should foreshadow standing:

- When an ally first crosses `15%` contribution share with `material_contribution_points > 0`, add a low-priority dispatch line: "{ally}'s forces are carrying real weight in the {war_name}."
- When an ally first crosses `25%` contribution share with `material_contribution_points > 0`, add a higher-priority dispatch line: "{ally} has earned a seat in any settlement."
- Staying-power-only shares never fire contribution threshold dispatches.
- Do not emit popups for contribution thresholds.
- Store fired thresholds in `participant_meta[nation]["contribution_signals_fired"]` to avoid repeat dispatch spam.

### 9.4 Theater-level battle attribution

The contribution layer uses theater participation, not per-nation casualty attribution. The existing combat executor resolves battles between marshals; forcing cross-nation casualty accounting into combat resolution would make this settlement slice depend on a combat rewrite. Theater attribution is sufficient for settlement politics and scales across Germany, Italy, Iberia, the Baltic, and the eastern frontier.

At battle resolution time, record:

```python
{
    "attacker": "France",
    "defender": "Austria",
    "battle_region": "Saxony",
    "attacker_participants": ["France", "Saxony"],
    "defender_participants": ["Austria", "Prussia"],
    "nation_theater_strength": {
        "France": 36000,
        "Saxony": 9000,
        "Austria": 28000,
        "Prussia": 12000,
    },
    "war_id": "war_12",
}
```

Participant detection:

- A nation participates if it has an active marshal in the battle region or in any one-hop adjacent region during the turn of the battle.
- Only active participants in the same `war_instance` side can be credited.
- Credit is divided by `nation_theater_strength` among detected participants on that side.
- Casualties still matter to the existing pairwise war-score record, but settlement contribution reads theater strength and battle result, not a new per-nation casualty map.
- This deliberately captures the Blucher-at-Waterloo pattern: an adjacent allied army can matter politically even when combat resolution treated the battle as one attacker and one defender.

Without this theater record, any contribution system will mis-credit coalition battles at full-Europe scale.

### 9.5 Contribution accrual performance contract

Contribution must comply with the project hot-path rule:

- Battle contribution accrues event-driven at battle resolution time.
- Occupation contribution accrues event-driven at region-controller change / treaty-transfer time.
- Staying power is the only per-turn accrual; it iterates active participants in `war_instances`, not all regions.
- Region ownership lookups use existing cached helpers such as `get_nation_regions()` where needed. Do not add per-region scans to `advance_turn()`.

### 9.6 Battle record compatibility

Old save records and old tests may only have `attacker`, `defender`, `attacker_casualties`, and `defender_casualties`. Any contribution reader must adapt old records to the theater shape:

```python
attacker_participants = record.get("attacker_participants") or [record["attacker"]]
defender_participants = record.get("defender_participants") or [record["defender"]]
nation_theater_strength = record.get("nation_theater_strength") or {
    record["attacker"]: 1,
    record["defender"]: 1,
}
battle_region = record.get("battle_region") or record.get("location") or record.get("region")
```

No retroactive multi-participant attribution is attempted for old saves; old records count as single-nation participation.

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

The BPH-C separate-peace relation penalty remains the base relation hit. The settlement reaction pass may add grievance flags, bargain breach/void outcomes, and standing records, but it must not re-apply the same base relation penalty a second time.

Separate peace is also a diplomatic weapon. When an enemy participant exits a `war_instance` by separate peace, remaining enemies on that side receive a bounded `abandoned_by_ally` pressure modifier in their next peace acceptance preview:

```python
abandoned_by_ally_acceptance_mod = min(
    4 * recently_exited_same_side_enemies,
    4 * max(3, original_enemy_side_size // 2),
)
```

This is a positive acceptance modifier for France's next peace preview against remaining enemies on that side. It lasts 5 turns, is shown in acceptance components, and represents coalition confidence collapsing after a partner defects. It supplements, but does not replace, recalculated military war score.

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

- Standing level per ally (seat / consult / beneficiary_only; `no_standing` is computed internally and omitted from the default advisory)
- Active war bargains and their status (fulfillable / at risk / impossible)
- Contribution shares and what each ally expects
- Territory legitimacy warnings (§12) for each demand
- Rival-strengthened / local balance warnings where a term strengthens a rival on another nation's border
- Hegemony impact preview

The advisory uses the same deterministic salience filtering pattern as DG-2 ledger scale work: show the top 3-5 allies by standing, contribution, bargain stake, territorial stake, and warning severity; group overflow behind "View all participants." The full list remains available, but the default preview must never become an 8-card wall in large coalition wars.

Example warnings:
- *"Prussia contributed 31% and expects consideration over Saxony."*
- *"The bargain with Prussia over Hanover is fulfillable only if France secures the French claim."*
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
    + war_objective_alignment
    + hegemony_pressure                 # where relevant
    + war_exhaustion                    # from existing coalition system
    + abandoned_by_ally_acceptance_mod   # if recent same-side enemies defected
```

Constants and clamps:

| Component | Range / clamp | Formula |
|-----------|---------------|---------|
| `base_side_pressure` | `[-50, 50]` | `round(side_pressure_score * 0.5)` using Â§6.3 |
| `settlement_tier_legitimacy` | `[-20, 15]` | `+15 total_victory`, `+10 harsh_peace`, `+5 dictated_terms`, `0 favorable_terms`, `-10 white_peace`, then subtract `10` if package harshness exceeds the tier's maximum |
| `term_harshness_penalty` | `[-45, 0]` | `-min(45, round(total_harshness_points * 0.6))`; harshness points reuse BPH/WPS term harshness values |
| `burdened_participant_penalty` | `[-30, 0]` | Sum the per-burdened-enemy penalties below, capped at `-30` |
| `leader_own_losses` | `[-25, 5]` | `-5` per leader-controlled region ceded, `-15` if leader capital is ceded/forced-aligned, `+5` if leader keeps all owned territory |
| `war_objective_alignment` | `[-20, 15]` | `+15` if the package satisfies France-side primary objective, `+5` if it partially satisfies it, `-15` if unrelated harsh terms dominate, `-20` if it contradicts the declared objective |
| `hegemony_pressure` | `[-20, 10]` | Existing Balance of Europe / hegemony pressure: `-20` if package crosses or deepens a `60%` bloc-share band, `-10` at `50%`, `-5` at `33%`, `+10` for meaningful de-escalation |
| `war_exhaustion` | `[0, 20]` | `min(20, enemy_leader_war_exhaustion // 3)` |
| `abandoned_by_ally_acceptance_mod` | `[0, 15]` | `+5` per same-side enemy participant that made separate peace in the last 3 turns, capped at `+15` |

Acceptance thresholds:

- `score >= 50`: accept.
- `35 <= score < 50`: reject, but feedback marks the package "near acceptable" and names the top two fixable components.
- `score < 35`: hard reject.

All component calculations are integerized with `round()` at the component boundary. The final score is clamped to `[-100, 100]`. Empty covered-enemy sets are invalid before scoring.

`base_side_pressure` is the war-level headline component. Every term that burdens a specific enemy must also pass the section 6.3 direct-score gate for that payer; a high side average cannot authorize harsh terms against a barely-defeated major.

If accepted, all covered active hostile pairs resolve. If rejected, the whole package fails. France can then try separate peace with individual enemies or revise terms. Rejection feedback must identify the top 1-2 objectionable terms or acceptance components by absolute penalty so the player knows whether the problem was Silesia, forced alliance, insufficient direct pressure, a bargain conflict, or accumulated harshness.

Burdened non-leader rule:

- If a non-leader enemy pays territory, vassalage, forced alliance, or liberation costs, compute `direct_score = max(get_war_score_for(side_member, burdened_enemy))` across France-side participants.
- `direct_score >= 20`: normal non-leader burden.
- `0 <= direct_score < 20`: add `burdened_participant_penalty = -15` and surface a severe warning.
- `direct_score < 0`: add `burdened_participant_penalty = -30`; only occupied, objective-linked, or bargain-linked territorial terms are legal.
- If the burdened non-leader is a `major`, add an additional `-10` unless their capital is occupied or the term directly matches the war objective.

These penalties are not vetoes. They model the enemy leader's reluctance to sell out an ally and set up the post-ratification resentment in §14.6.

### Step 5: Settlement reaction pass

After peace succeeds, every relevant party evaluates the outcome. Run for **both sides**. France-side ally reactions are the main player-facing loop, but enemy-side "sold out by leader" reactions are primary political events, not background flavor.

The reaction pass also checks active cross-war consequences. If a settlement changes region ownership, strengthens a rival on a border, changes forced alignment, affects a bargain target, or alters survival/capital stakes, scan active `war_instances` for participants in the affected nation set and evaluate their reaction. This is bounded by the affected terms and active participants; do not broad-scan every nation in Europe.

**France-side reactions** (main player-facing loop):

| Outcome | Consequence |
|---------|-------------|
| War bargain fulfilled | France secures the WB claim region; positive relation, fulfillment spotlight, bargain → `fulfilled` |
| High-standing ally rewarded | Relation bonus, `they_chose_us`, `settlement_gratitude` acceptance bonus on subsequent proposals |
| High-standing ally shut out | `settlement_shut_out` grievance flag, relation hit, subsequent acceptance penalty through existing `grievance_modifier` |
| Explicit war bargain breached | Route through betrayal/reliability machinery (existing WB-B breach pipeline) |
| Major power humiliated | Downgrade pressure, hard-reject posture risk, coalition drift |
| Minor harmed | Narrower reaction — only when survival, capital, promise, or territory involved |

**Enemy-side reactions:**

| Outcome | Consequence |
|---------|-------------|
| Enemy ally sacrificed by their leader | Major resentment toward their own war leader, relation hit, subsequent alignment drift |
| Disproportionate terms on a secondary enemy | Relation damage toward France, subsequent resistance |

**Europe at large:**

| Outcome | Consequence |
|---------|-------------|
| Annexation / vassalage / forced alignment | Existing `add_threat()` / `reduce_threat()` hooks plus bloc-cache invalidation |
| Bloc share crosses `33 / 50 / 60` or hegemon swaps | Existing `balance_of_europe_shifted` beat fires under the Memory and Pressure contract |
| Forced alliance imposed | Coalition threat increase (WPS-C, already wired: +15 per forced alliance) |

### Step 6: Next-turn presentation

- Notification rail, dispatch, ledger, named diplomat voice.
- Do not spam one popup per ally. Aggregate reactions, then spotlight only major breaches or bargain fulfillment/breach.
- Mechanical grievance / gratitude / sold-out records all apply, but presentation dispatches are capped at 3 primary settlement beats per ratification. Remaining reactions are grouped into one settlement digest line using the DG-7 categorized-dispatch pattern.
- Campaign log emits exactly one `settlement_summary` entry per ratified common peace. Participant-level reactions are stored in `settlement_summary["participant_reactions"]` as structured data and the one-liner shows at most three named participants plus `+N more`.
- Settlement reaction events use their own settlement route metadata. Existing `bargain_*` events continue to use commitments routing, and `balance_of_europe_shifted` remains owned by Memory and Pressure.

---

## 12. Territory Demand Legitimacy

Territorial demands require a **pressure basis**. Occupation is not mandatory — Napoleon often dictated unoccupied concessions after decisive victories — but every region transfer must be justified. Demands without a pressure basis are legal only as extreme terms and carry severe acceptance and hegemony consequences.

### 12.1 Pressure bases

For every territorial term, evaluate:

| Basis | Strength | Description |
|-------|----------|-------------|
| `occupied_by_france_side` | Strong | Region is currently controlled by France or a French-side ally |
| `war_objective_or_bargain` | Strong | Region is tied to declared war objective, liberation objective, or active war bargain |
| `high_pairwise_pressure` | Medium | France has strong pairwise war score against the `from` nation |
| `general_side_victory` | Weak | France's side is winning the overall war, but France has little direct pressure on the `from` nation |

### 12.2 Penalty rules

```
territory_demand_cost =
    base_territory_demand
    + unoccupied_region_penalty          # if not held by France's side
    + weak_pressure_penalty              # if low pairwise war score against `from`
    + excessive_land_burden_penalty      # if too many regions demanded from one enemy
    - occupied_discount                  # if held by France's side
- war_objective_discount             # if tied to declared objective
    - bargain_claim_discount             # if tied to active WB claim for France
    - liberation_claim_discount          # if restoring a liberated nation
```

First-pass constants:

| Term | Value |
|------|-------|
| `base_territory_demand` | `8` per region |
| `unoccupied_region_penalty` | `+12` when not controlled by France's side |
| `weak_pressure_penalty` | `+10` when `direct_score < 20`, `+20` when `direct_score < 0` |
| `excessive_land_burden_penalty` | `+6` for the second region from same enemy, `+10` for each additional region |
| `occupied_discount` | `-6` |
| `war_objective_discount` | `-6` |
| `bargain_claim_discount` | `-4` for France's WB `claim_region`; does not apply to ally-beneficiary land because current WB claims are France-claim-scoped |
| `liberation_claim_discount` | `-8` |

### 12.3 Edge cases

- **Region belongs to a non-participant:** Hard stop. Cannot demand territory from a nation not in the war.
- **`from` is only an enemy ally that France barely fought:** Very high acceptance penalty. The enemy war leader will resist giving away an ally's land when that ally is not the one who lost.
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
    "from": "Austria",
    "to": "Prussia",
    "beneficiary": "Prussia",
    "regions": ["Saxony"],
    "war_id": "war_12",
    "settlement_reason": "promise",  # promise | contribution | buffer | liberation
}
```

Canonical treaty-term ownership fields are `from` and `to`, matching live `_ratify_treaty()` handling. Importers may accept legacy draft aliases `from_nation` / `to_nation` only as input-normalization compatibility and must convert them before validation, preview, ratification, save, campaign log, or dispatch emission.

New term types are reserved for genuinely different political actions (forced_alliance, liberation — already landed in WPS-C).

### 13.2 Allowed beneficiaries

In common peace, the beneficiary can be:

- France
- An active ally on France's side
- A liberated nation
- A former owner restored by treaty

### 13.3 Invalid settlement shapes

Do not support:

- Ally gives region to another ally through three-step chains
- Hidden off-screen transfer to non-participants
- Nested protectorate / vassal / subject distribution logic

Keep settlement packages direct and legible.

---

## 14. Settlement Reaction Pass

### 14.1 `settlement_shut_out` grievance

If an ally contributed meaningfully and France concludes peace that excludes them from meaningful gain, apply a settlement grievance. This is a **new grievance flag type** on the existing `betrayal_history` pair record, not a separate acceptance system and not automatically a betrayal strike.

Storage:

```python
_add_grievance_flag(
    world,
    breaker="France",
    victim=ally,
    grievance_type="settlement_shut_out",
    episode_id=episode_id,
    source_episode_type="settlement_reaction",
)
_add_settlement_memory(
    world,
    actor="France",
    subject=ally,
    memory_type="settlement_context",
    episode_id=episode_id,
    payload={
        "war_id": war_id,
        "standing_level": standing_level,
        "contribution_share": standing_share,
        "severity": severity,
        "settlement_terms": summarized_terms,
    },
)
```

`grievance_modifier()` then supplies the subsequent acceptance penalty through the existing Memory and Pressure formula and the existing `-60` composite floor.

### 14.2 Severity bands

**Minor shut-out:**
- Ally contributed but had no promise and no high-interest claim
- Effect: moderate relation hit only (`-5` to `-10` relation)

**Major shut-out:**
- Ally had strong claim interest or high contribution (>= 20%)
- Effect: larger relation hit (`-15` to `-25`), `settlement_shut_out` grievance flag, possible treaty downgrade pressure

**Promise breach (war bargain):**
- France could have secured the active WB claim for France and chose not to
- Effect: route through existing WB-B breach pipeline → `bargain_breached` → betrayal strike + reliability hit + existing bargain breach presentation

**Major power humiliation:**
- `major` power with `seat` standing, excluded or visibly subordinated
- Effect: hard-reject posture risk, coalition drift through threat/bloc systems, possible `balance_of_europe_shifted` beat only if the existing threshold/swap contract is met

### 14.3 Rewarded ally memory

`they_chose_us` is a positive settlement memory, not just a one-time relation delta.

When a `seat` or `consult` ally receives a meaningful direct reward:

- Relation with France: `+5` for consult, `+10` for seat.
- Add a transient `settlement_gratitude` memory on the pair for 10 turns.
- Subsequent deep-treaty and war-entry proposals from France to that ally receive `+5` acceptance while the memory is active.
- The bonus is capped at one active gratitude memory per pair; a subsequent rewarded settlement refreshes the expiry, not the value.

### 14.4 Power tier reaction scaling

| Tier | Reaction scope |
|------|---------------|
| `major` | Bigger anger when excluded. More likely to downgrade alignment or shift against France politically. Coalition drift. |
| `secondary` | Moderate reaction. Primarily care about direct territorial interests and promises. |
| `minor` | Narrow reaction. Only care when survival, capital, or explicit promised reward is involved. |

### 14.5 Separate peace fallout

Separate peace fires a smaller settlement reaction pass for France's remaining co-belligerents in the `war_instance`:

- Abandoned ally still fighting → BPH-C base relation hit + possible `settlement_shut_out` grievance flag if standing warrants it
- Separate peace made a war bargain impossible → route through WB-B breach
- Separate peace removed the enemy or region an ally cared about → consultation-level grievance
- Separate peace normalized with a bargain target → bargain void check

### 14.6 Enemy ally sold out by leader

When the opposing leader accepts common peace terms that heavily burden a non-leader participant, the burdened participant reacts toward both France and its own leader.

Tilsit threshold: `sold_out_by_war_leader` fires only for material losses:

- Territory loss
- Independence loss, vassalage, or liberation of a subject
- Forced alliance / forced Continental System / forced alignment
- Capital loss, survival loss, or elimination

Minor gold, manpower, AP, access, or face-saving terms do not create `sold_out_by_war_leader`; they remain ordinary acceptance costs and relation deltas.

Primary reaction:

- Relation toward France: `-10` to `-25` depending on term severity.
- Relation toward own war leader: `-15` to `-30`.
- Add `sold_out_by_war_leader` memory for 10 turns against the leader.
- If the burdened participant is `major`, also add alignment drift away from the leader's bloc and toward anti-leader diplomacy.

This is the Tilsit pattern: the leader can sell out an ally, but the sold-out ally remembers who signed the paper.

---

## 15. War Bargain Integration

War Bargains (WB-A through WB-D) are the promise system. This spec does not invent new promise types. It wires bargains into the settlement machinery.

### 15.1 Bargain fulfillment at settlement

Shipped War Bargains are France-claim-scoped. A settlement can fulfill an existing WB only by satisfying the existing WB-B fulfillment contract:

- Bargain is `triggered`.
- France gains or secures `claim_term.claim_region`.
- The region changed from the named enemy or its subject to France while the bargain remained valid.
- France still holds `DEFENSIVE_ALLIANCE` or `ALLIANCE` with the beneficiary.
- The beneficiary was a co-belligerent on France's side against the named enemy immediately before settlement.

Settlement ratification triggers `bargain_fulfilled` through the existing WB-B lifecycle.

Ally-beneficiary land awards are separate settlement rewards. They may create `they_chose_us` / `settlement_gratitude` and may satisfy standing expectations, but they do **not** fulfill the current WB claim because shipped War Bargains are France-claim-scoped.

### 15.2 Bargain breach at settlement

A war bargain is **breached** when:

- France could have secured the WB `claim_term.claim_region` for itself under the package and chose not to
- France cuts separate peace that makes the bargain impossible
- France awards the WB `claim_term.claim_region` to an ally, to a different third party, or back to the named enemy while fulfillment was feasible

Settlement-triggered breach routes through the existing WB-B breach pipeline: `bargain_breached` → betrayal strike + reliability hit + WB-D presentation.

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
- Rival-strengthened / local balance warnings
- Likely reactions if an ally is cut out
- Whether a region is "theirs by contribution," "ours by bargain," "theirs by restoration," or "ours if we insist"

Default advisory rows are capped at 5 by `rank_diplomatic_salience()`: `seat` over `consult`, material contribution over staying power, active bargain stake, direct territorial stake, rival-strengthened warning, and severity. Overflow is grouped behind "View all participants."

### 16.2 UI surfaces

Use existing surfaces where possible:

| Surface | Settlement use |
|---------|---------------|
| Proposal preview / advisory | Standing, bargain status, territory legitimacy, ally-fallout warnings |
| War status panel | Participant list, contribution shares, war bargain status |
| Diplomatic ledger | Post-settlement: grievance records, bargain outcomes |
| Dispatch | Post-ratification: settlement reaction summaries |
| Notification rail | Major events: bargain fulfilled, major shut-out, promise breach |

Settlement event families own their own route metadata. Do not add generic settlement fallout to `COMMITMENTS_ROUTES`; that router remains for commitment families. Existing `bargain_fulfilled`, `bargain_breached`, `bargain_voided`, `bargain_ratified`, and `bargain_triggered` continue to use WB-D commitments routing.

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
world.war_contribution_scores: Dict[str, Dict[str, Dict[str, int]]] = {}
world.settlement_memories: Dict[str, List[Dict]] = {}
```

`settlement_memories` stores positive/transient settlement records such as `settlement_gratitude` and enemy-side `sold_out_by_war_leader`. Keys use the canonical ordered pair string `actor|subject`. Negative France-side grievances use existing `betrayal_history[pair]["grievance_flags"]` with `grievance_type="settlement_shut_out"`; do not add a parallel grievance store.

Canonical memory shape:

```python
{
    "memory_type": "settlement_gratitude",  # settlement_gratitude | sold_out_by_war_leader | settlement_context
    "actor": "France",
    "subject": "Prussia",
    "counterparty": "Austria",
    "war_id": "war_12",
    "episode_id": "settlement_war_12_turn_24",
    "created_turn": 24,
    "expires_on_turn": 34,
    "standing_level": "consult",
    "contribution_share": 0.18,
    "severity": "moderate",
    "terms_summary": ["territory_cede:Saxony->Prussia"],
    "acceptance_modifier": 5,
    "active": True,
}
```

Serialization ownership:

- `world.war_instances`, `world.war_contribution_scores`, and `world.settlement_memories` are saved and loaded through `WorldState.to_dict()` / `WorldState.from_dict()` with `{}` defaults for older saves.
- `docs/SAVE_FORMAT_REFERENCE.md` must document all three fields in Slice A / B / D as each field lands.
- `settlement_memories` stores detail payloads that do not fit the existing grievance flag shape. Existing `grievance_flags` remain `{grievance_type, episode_id, turn, source_episode_type}` only.

### 17.2 Extended fields

```python
# Battle records gain optional multi-participant detail
battle_record["attacker_participants"] = ["France", "Saxony"]
battle_record["defender_participants"] = ["Austria", "Prussia"]
battle_record["battle_region"] = "Saxony"
battle_record["nation_theater_strength"] = {"France": 36000, "Saxony": 9000, ...}
battle_record["war_id"] = "war_12"

# Territory terms gain beneficiary ownership
term["beneficiary"] = "Prussia"
term["settlement_reason"] = "promise"  # promise | contribution | buffer | liberation
term["war_id"] = "war_12"
```

### 17.3 Derived at settlement time (not stored)

```python
standing_share[nation] = contribution_total(nation) / total_side_contribution
standing_level[nation] = classify_standing(nation, war_instance, standing_share, ...)
side_pressure_score = compute_side_pressure_score(war_instance)
direct_scores[payer] = compute_direct_scores_by_enemy(war_instance)
rival_strengthened[nation] = compute_local_balance_warning(nation, settlement_terms)
```

### 17.4 Compatibility

- Keep `war_scores`, `battle_records`, `decisive_battles`, `war_start_turns`, `war_objectives`
- Do not migrate or delete existing pairwise structures
- Build the new layer on top of them
- Battle-record readers must adapt old single-attacker/single-defender records using §9.6.

---

## 18. Implementation Sequence

This sequence is post-Peace-Deals. All Peace Deals dependencies (BPH, WPS, WB) are landed.

The executable slice plan lives in `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md`. If this overview and the plan disagree, the implementation plan owns file-level order, test allocation, and gate criteria; this spec owns mechanic intent and formulas.

### Slice A: War identity + read-only grouping

- Add `war_instance` container
- Create `war_instance` before `_process_war_cascade()`; pass `war_id` through cascade / vassal-entry / ally-entry paths
- Add side leaders, leader replacement, `participant_meta`, active episodes, re-entry episodes, and WPS `war_objectives` key references
- Wire War Bargain `war_id` attachment at join_opportunity
- Expose participant lists in war status panel and debug endpoints
- Serialization: `to_dict` / `from_dict` round-trip for `war_instances`; update `SAVE_FORMAT_REFERENCE.md`
- ~34 tests

### Slice B: Contribution tracker

- Add `war_contribution_scores` field
- Add theater-level battle attribution (`battle_region`, `attacker_participants`, `defender_participants`, `nation_theater_strength`, `war_id`); add old-record adapter
- Wire contribution accrual: battle and occupation event-driven, support event-driven, staying power per active participant episode turn
- Add support contribution from recorded gold / subsidy / AP / manpower support
- Add material-contribution gate so staying power alone cannot trigger `seat`, threshold dispatches, or major shut-out grievances
- Add contribution threshold dispatch signals at 15% and 25% with material contribution required
- Derive contribution shares at query time
- Standing classification: `classify_standing()` with rule-based bucket assignment, secondary co-belligerent floor, and late-joiner rules
- Serialization: `to_dict` / `from_dict` round-trip for `war_contribution_scores`; update `SAVE_FORMAT_REFERENCE.md`
- ~44 tests

### Slice C: Common peace plumbing + territory legitimacy

- Add `Open settlement` entry point (separate from bilateral wizard)
- One-package term builder grouped by target enemy
- Ally beneficiary fields on `territory_cede`
- Territory demand legitimacy evaluation
- Common peace acceptance formula (opposing war leader)
- `side_pressure_score` weighted average as headline/base component only
- Per-target direct-score gates and burdened non-leader penalties
- Rejection feedback identifying the top 1-2 objectionable terms or acceptance components
- Rival-strengthened / local balance warning input
- Positive, coalition-size-scaled `abandoned_by_ally_acceptance_mod`
- Talleyrand advisory preview: standing, bargains, territory legitimacy, rival-strengthened warnings, ally-fallout warnings, salience-filtered default rows
- ~48 tests

### Slice D: Settlement reaction pass + bargain integration

- Post-ratification reaction pass for both sides
- `settlement_shut_out` grievance flag on existing `betrayal_history` using the live `_add_grievance_flag(..., source_episode_type="settlement_reaction")` signature
- `settlement_gratitude`, `sold_out_by_war_leader`, and `settlement_context` records in `settlement_memories`
- Wire war bargain fulfillment/breach at settlement through existing WB-B pipeline
- Separate peace fallout: smaller reaction pass for remaining co-belligerents
- Cross-war affected-participant reaction check bounded by active `war_instances`
- Sold-out-by-leader Tilsit threshold for material losses only
- `they_chose_us` upside for rewarded allies with subsequent acceptance bonus
- Hegemony/threat reaction through existing add_threat/reduce_threat/bloc invalidation seams
- Serialization: `to_dict` / `from_dict` round-trip for `settlement_memories`; update `SAVE_FORMAT_REFERENCE.md`
- ~42 tests

### Slice E: Presentation + ledger

- Settlement warnings in proposal preview
- War status panel: contribution shares, standing levels
- Separate settlement route metadata for settlement event families
- Dispatch: top 3 settlement beats plus digest overflow
- Notification rail: major settlement events (bargain fulfilled, major shut-out, promise breach)
- Named diplomat voice for settlement reactions (per Voice Bible)
- Ledger: post-settlement records
- Common-peace rejection preview shows top objectionable terms
- "View all participants" advisory overflow
- ~32 tests

**Estimated total: ~200 tests across 5 slices.** Slice boundaries are implementation gates: each slice owns its data fields, serialization/defaults, save-format documentation, focused backend tests, and any UI payload tests listed above.

---

## 19. Testing Focus

Highest-priority tests:

1. Cascade-created ally enters same `war_instance` as original declaration.
2. War Bargain created at war entry attaches to the correct `war_id`.
3. Separate peace removes only that participant from the active list; does not end the war.
4. Separate peace fires settlement reaction pass for remaining co-belligerents.
5. Common peace sends one package; opposing war leader accepts/rejects whole.
6. Common peace can award territory to ally beneficiary via `territory_cede` with `beneficiary` field.
7. High-contribution ally excluded from common peace gains `settlement_shut_out` grievance flag on `betrayal_history`.
8. Active war bargain denied when France could secure the WB claim triggers breach through WB-B pipeline.
9. Active war bargain honored by France securing the WB claim triggers fulfillment through WB-B pipeline.
10. Territory demand for unoccupied region carries acceptance penalty; occupied region does not.
11. Territory demand against barely-fought enemy ally carries severe acceptance penalty.
12. `major` power with `seat` standing gets consultation warning even with lower contribution.
13. `minor` ally only surfaces when its direct interests (survival, capital, promise, territory) are involved.
14. Battle attribution in coordinated allied battles feeds the correct contribution score.
15. Existing bilateral peace proposals still work unchanged in wars without allied settlement needs.
16. Side pressure score weighted-average aggregation does not break existing pairwise peace acceptance logic.
17. Standing classification respects all six inputs (contribution, power tier, territorial interest, bargain, treaty depth, survival).
18. Settlement reaction pass fires for both France-side and enemy-side participants.
19. Imperial-looking settlement uses existing threat/bloc seams and emits `balance_of_europe_shifted` only on threshold crossing or hegemon swap.
20. Dormant war bargains remain dormant through settlement; do not block peace.
21. Contribution threshold signals fire once at 15% and 25%, and do not create popups.
22. Old-format battle records adapt to single-participant contribution records.
23. Enemy ally sold out by its own leader receives relation damage toward both France and that leader.
24. Rewarded high-standing ally receives `settlement_gratitude` subsequent acceptance bonus and cap/refresh behavior.
25. Staying-power-only contribution never triggers `seat`, threshold dispatches, or major shut-out grievance.
26. Secondary co-belligerent with material contribution receives at least `consult` even in an 8-participant coalition.
27. `rival_strengthened` warning fires when a settlement strengthens a rival on an affected nation's border.
28. Theater-level battle attribution credits nations with marshals in or adjacent to the battle region by theater strength.
29. Late joiner contribution counts from `joined_turn`; decisive post-join battle credit is not reduced.
30. Common-peace rejection identifies the top 1-2 objectionable terms or acceptance components.
31. Cross-war settlement consequence check evaluates active participants in other `war_instances` when terms affect their interests.
32. Settlement presentation emits at most 3 primary dispatch beats plus one digest overflow line.
33. `sold_out_by_war_leader` fires only for material losses, not minor gold/manpower/AP costs.
34. `abandoned_by_ally_acceptance_mod` is positive, 5-turn, and capped by original side size.
35. `war_instances`, `war_contribution_scores`, and `settlement_memories` save/load with old-save defaults.
36. `settlement_shut_out` uses existing grievance flag shape and stores rich context in `settlement_memories`.

---

## 20. Design Calls

### 20.1 Contribution is political standing, not spoils accounting

`war_contribution_score` determines who has earned the right to be heard. It is the mechanical basis for ally expectations. It is not an HOI4-style peace budget.

Contribution must be foreshadowed during the war through quiet dispatch / war-status signals. The exact settlement share can wait for Talleyrand's advisory, but the player should not first learn at peace time that an ally carried the campaign.

### 20.2 Keep separate peace

The interesting tension is not "peace is impossible unless the war leader says yes." The interesting tension is "you can cut a separate deal, but doing so may cost you allies."

Separate peace is also a weapon. Peeling one enemy out of a war should pressure the remaining enemies for a short window, while still creating the appropriate ally/commitment fallout.

### 20.3 No ally turns at the peace table

France dictates. Allies react. The drama is in the pre-visible advisory (knowing the cost) and the post-ratification memory (paying the cost). No conference minigame.

### 20.4 War Bargains are the promise system

Do not reinvent promises. War Bargains (WB-A through WB-D) handle creation, lifecycle, fulfillment, breach, and presentation. This spec wires them into settlement.

Important constraint: current War Bargains are France-claim-scoped. France fulfills by securing the WB claim region for France while the beneficiary fought alongside France. Awarding land to an ally is a settlement reward and standing outcome, not current WB fulfillment.

### 20.5 Territory demands require a pressure basis

Occupation is the cleanest legitimacy basis. Unoccupied demands are legal but expensive. Demands against barely-fought enemies are brutal. This constraint prevents the player from making sweeping imperial demands without military backing, while still allowing decisive-victory dictation.

### 20.6 Power tiers are authored, not dynamic

`power_tier` is scenario data (`major / secondary / minor`). It affects consultation rights, not free settlement score. This spec reads authored power tiers only; runtime `power_score` belongs to Balance of Europe and is not a settlement power-tier input.

### 20.7 Allies matter without universal veto

Standing, consultation, entitlement, and fallout — not hard blocking. Political cost, not absolute lockout. This follows the core design philosophy: the player always gets to choose, but the consequences are real and compound through existing systems.

---

## 21. Changelog

- **April 28, 2026 - v1.3 full-Europe scale hardening.** Added the implementation-plan handoff, exact common-peace acceptance constants and thresholds, canonical `from` / `to` territory-term ownership, live `location` battle-record compatibility, support-contribution event schema, live-state `rival_strengthened` data source, and one-entry campaign-log aggregation contract for common settlements.

- **April 28, 2026 — v1.2 full-Europe scale synthesis.** Added the explicit 13-20 nation / 50+ region scale contract; added no-unowned-deferrals ownership rule; added mid-war joiner and re-entry rules; changed battle contribution to theater-level attribution; added material-contribution gates, secondary co-belligerent standing floor, support contribution, rival-strengthened local-balance warnings, per-target direct-score gates, common-peace rejection diagnostics, cross-war reaction checks, dispatch/digest caps, Tilsit material threshold, live grievance-flag signature, canonical settlement-memory shape, serialization/save-format ownership, expanded implementation slices to ~200 tests, and expanded testing focus for full-Europe coalition play.

- **April 28, 2026 — v1.1 audit synthesis.** Reconciled the design/system audit findings: protected the "France dictates, allies react" design call; corrected War Bargain settlement fulfillment to the shipped France-claim-scoped WB-B lifecycle; moved settlement shut-out into existing `betrayal_history` grievance flags; added side leaders, sold-out enemy ally reactions, weighted `side_pressure_score`, contribution threshold foreshadowing, battle-record compatibility, performance constraints, separate-peace pressure on remaining enemies, settlement gratitude, separate settlement routing, and expanded the implementation/test budget to ~152 tests.
